# Distributed Redis Caching Layer for Node.js TypeScript

## Project Structure

```
distributed-cache/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts                 # Public exports
│   ├── cache/
│   │   ├── CacheLayer.ts        # Main cache implementation
│   │   ├── CacheEntry.ts        # Versioned cache entry types
│   │   ├── CoalescingMap.ts     # Request coalescing utility
│   │   ├── InvalidationBus.ts   # Pub/sub invalidation with recovery
│   │   ├── NegativeCache.ts     # Negative caching
│   │   └── DegradedCache.ts     # Fallback when Redis unavailable
│   ├── redis/
│   │   ├── RedisClient.ts       # Redis connection management
│   │   └── LuaScripts.ts        # Atomic operations
│   ├── telemetry/
│   │   ├── Metrics.ts           # Prometheus metrics
│   │   └── Tracing.ts           # OpenTelemetry traces
│   ├── config/
│   │   └── CacheConfig.ts       # Configuration types
│   └── utils/
│       ├── version.ts           # Version utilities
│       └── errors.ts            # Custom errors
├── tests/
│   ├── cache.test.ts            # Unit tests
│   ├── integration.test.ts      # Multi-instance deterministic tests
│   └── fixtures/
│       └── test-helpers.ts
├── examples/
│   ├── basic-usage.ts
│   ├── multi-instance.ts
│   └── benchmark.ts
└── README.md
```

---

## package.json

```json
{
  "name": "distributed-cache-layer",
  "version": "1.0.0",
  "description": "Self-contained distributed caching layer with Redis for Node.js TypeScript",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsc",
    "test": "vitest run --reporter=verbose",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage",
    "example:basic": "tsx examples/basic-usage.ts",
    "example:multi": "tsx examples/multi-instance.ts",
    "example:benchmark": "tsx examples/benchmark.ts",
    "lint": "eslint src --ext .ts",
    "prepublishOnly": "npm run build && npm run test"
  },
  "keywords": [
    "cache",
    "redis",
    "distributed",
    "stale-while-revalidate",
    "request-coalescing",
    "negative-caching"
  ],
  "author": "",
  "license": "MIT",
  "dependencies": {
    "ioredis": "5.4.1",
    "pino": "9.0.0",
    "prom-client": "15.1.0",
    "@opentelemetry/api": "1.8.0",
    "@opentelemetry/sdk-trace-base": "1.23.0",
    "@opentelemetry/sdk-trace-node": "1.23.0",
    "@opentelemetry/resources": "1.23.0",
    "@opentelemetry/semantic-conventions": "1.23.0",
    "@opentelemetry/exporter-prometheus": "0.54.0",
    "uuid": "9.0.0",
    "js-yaml": "4.1.0"
  },
  "devDependencies": {
    "typescript": "5.4.2",
    "vitest": "1.3.1",
    "@types/node": "20.11.24",
    "@types/uuid": "9.0.8",
    "@types/js-yaml": "4.0.9",
    "tsx": "4.7.1",
    "ioredis-mock": "8.9.0",
    "@vitest/coverage-v8": "1.3.1",
    "eslint": "8.57.0",
    "@typescript-eslint/eslint-plugin": "7.1.0",
    "@typescript-eslint/parser": "7.1.0"
  },
  "engines": {
    "node": ">=20.0.0"
  },
  "packageManager": "npm@10.5.0"
}
```

---

## tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests", "examples"]
}
```

---

## Source Code

### src/config/CacheConfig.ts

```typescript
export interface CacheConfig {
  redis: RedisConfig;
  cache: CacheBehaviorConfig;
  telemetry: TelemetryConfig;
  degradation: DegradationConfig;
}

export interface RedisConfig {
  host: string;
  port: number;
  password?: string;
  db: number;
  connectionName: string;
  maxRetriesPerRequest: number;
  retryStrategy: RetryStrategy;
  enableReadyCheck: boolean;
  lazyConnect: boolean;
  connectTimeout: number;
  commandTimeout: number;
  family: number;
  tls?: Record<string, unknown>;
}

export interface RetryStrategy {
  enabled: boolean;
  maxRetries: number;
  retryDelay: number;
  maxRetryDelay: number;
}

export interface CacheBehaviorConfig {
  defaultTtlMs: number;
  staleWhileRevalidateTtlMs: number;
  negativeCacheTtlMs: number;
  maxCoalescingWaitMs: number;
  coalescingMaxConcurrent: number;
  versionKeyPrefix: string;
  dataKeyPrefix: string;
  negativeKeyPrefix: string;
  lockTtlMs: number;
  lockRetryDelayMs: number;
  lockMaxRetries: number;
}

export interface TelemetryConfig {
  serviceName: string;
  instanceId: string;
  enableMetrics: boolean;
  enableTracing: boolean;
  metricsPort: number;
  traceSampleRate: number;
}

export interface DegradationConfig {
  enabled: boolean;
  maxLocalCacheSize: number;
  localCacheTtlMs: number;
  healthCheckIntervalMs: number;
  circuitBreakerThreshold: number;
  circuitBreakerTimeoutMs: number;
}

export const DEFAULT_CONFIG: CacheConfig = {
  redis: {
    host: 'localhost',
    port: 6379,
    db: 0,
    connectionName: 'distributed-cache',
    maxRetriesPerRequest: 3,
    retryStrategy: {
      enabled: true,
      maxRetries: 3,
      retryDelay: 100,
      maxRetryDelay: 2000,
    },
    enableReadyCheck: true,
    lazyConnect: true,
    connectTimeout: 10000,
    commandTimeout: 5000,
    family: 4,
  },
  cache: {
    defaultTtlMs: 300000,
    staleWhileRevalidateTtlMs: 60000,
    negativeCacheTtlMs: 30000,
    maxCoalescingWaitMs: 500,
    coalescingMaxConcurrent: 100,
    versionKeyPrefix: 'cache:ver:',
    dataKeyPrefix: 'cache:data:',
    negativeKeyPrefix: 'cache:neg:',
    lockTtlMs: 5000,
    lockRetryDelayMs: 50,
    lockMaxRetries: 10,
  },
  telemetry: {
    serviceName: 'distributed-cache',
    instanceId: `instance-${process.pid}-${Math.random().toString(36).slice(2, 8)}`,
    enableMetrics: true,
    enableTracing: true,
    metricsPort: 9090,
    traceSampleRate: 0.1,
  },
  degradation: {
    enabled: true,
    maxLocalCacheSize: 10000,
    localCacheTtlMs: 60000,
    healthCheckIntervalMs: 10000,
    circuitBreakerThreshold: 5,
    circuitBreakerTimeoutMs: 30000,
  },
};
```

### src/utils/errors.ts

```typescript
export class CacheError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly cause?: Error
  ) {
    super(message);
    this.name = 'CacheError';
    Error.captureStackTrace(this, CacheError);
  }
}

export class RedisUnavailableError extends CacheError {
  constructor(cause?: Error) {
    super('Redis unavailable', 'REDIS_UNAVAILABLE', cause);
    this.name = 'RedisUnavailableError';
  }
}

export class VersionConflictError extends CacheError {
  constructor(key: string, expectedVersion: number, actualVersion: number) {
    super(
      `Version conflict for key ${key}: expected ${expectedVersion}, got ${actualVersion}`,
      'VERSION_CONFLICT'
    );
    this.name = 'VersionConflictError';
  }
}

export class CoalescingTimeoutError extends CacheError {
  constructor(key: string) {
    super(`Coalescing wait timeout for key ${key}`, 'COALESCING_TIMEOUT');
    this.name = 'CoalescingTimeoutError';
  }
}

export class InvalidationLagError extends CacheError {
  constructor(key: string, lagMs: number) {
    super(`Invalidation lag detected for key ${key}: ${lagMs}ms`, 'INVALIDATION_LAG');
    this.name = 'InvalidationLagError';
  }
}
```

### src/utils/version.ts

```typescript
export interface VersionedKey {
  key: string;
  version: number;
  timestamp: number;
}

export function generateVersion(): number {
  return Date.now() * 1000 + Math.floor(Math.random() * 1000);
}

export function parseVersionedKey(compositeKey: string): VersionedKey | null {
  const parts = compositeKey.split(':');
  if (parts.length < 3) return null;
  const version = parseInt(parts[parts.length - 2], 10);
  const timestamp = parseInt(parts[parts.length - 1], 10);
  if (isNaN(version) || isNaN(timestamp)) return null;
  const key = parts.slice(0, -2).join(':');
  return { key, version, timestamp };
}

export function buildVersionedKey(baseKey: string, version: number, timestamp?: number): string {
  return `${baseKey}:${version}:${timestamp ?? Date.now()}`;
}

export function extractBaseKey(versionedKey: string, prefix: string): string {
  if (!versionedKey.startsWith(prefix)) return versionedKey;
  const withoutPrefix = versionedKey.slice(prefix.length);
  const parts = withoutPrefix.split(':');
  if (parts.length < 3) return withoutPrefix;
  return parts.slice(0, -2).join(':');
}

export function isStale(entryTimestamp: number, ttlMs: number): boolean {
  return Date.now() - entryTimestamp > ttlMs;
}

export function isExpired(entryTimestamp: number, ttlMs: number): boolean {
  return Date.now() - entryTimestamp > ttlMs * 2;
}
```

### src/cache/CacheEntry.ts

```typescript
import { VersionedKey } from '../utils/version';

export interface CacheEntry<T> {
  value: T;
  version: number;
  timestamp: number;
  ttlMs: number;
  stale: boolean;
  negative?: boolean;
  negativeReason?: string;
}

export interface StoredCacheEntry<T> {
  v: number;
  t: number;
  d: T;
  ttl: number;
  neg?: boolean;
  nr?: string;
}

export function serializeEntry<T>(entry: CacheEntry<T>): StoredCacheEntry<T> {
  return {
    v: entry.version,
    t: entry.timestamp,
    d: entry.value,
    ttl: entry.ttlMs,
    neg: entry.negative,
    nr: entry.negativeReason,
  };
}

export function deserializeEntry<T>(stored: StoredCacheEntry<T>): CacheEntry<T> {
  const now = Date.now();
  const age = now - stored.t;
  return {
    value: stored.d,
    version: stored.v,
    timestamp: stored.t,
    ttlMs: stored.ttl,
    stale: age > stored.ttl,
    negative: stored.neg,
    negativeReason: stored.nr,
  };
}

export function createCacheEntry<T>(
  value: T,
  version: number,
  ttlMs: number,
  negative = false,
  negativeReason?: string
): CacheEntry<T> {
  const timestamp = Date.now();
  return {
    value,
    version,
    timestamp,
    ttlMs,
    stale: false,
    negative,
    negativeReason,
  };
}

export function createNegativeEntry(reason: string, ttlMs: number, version: number): CacheEntry<null> {
  return createCacheEntry(null, version, ttlMs, true, reason);
}

export function isNegativeEntry<T>(entry: CacheEntry<T>): entry is CacheEntry<null> & { negative: true } {
  return entry.negative === true;
}
```

### src/cache/CoalescingMap.ts

```typescript
import { EventEmitter } from 'events';

export interface CoalescedRequest<T> {
  promise: Promise<T>;
  resolve: (value: T) => void;
  reject: (error: Error) => void;
  timestamp: number;
  subscribers: number;
}

export class CoalescingMap<K, T> extends EventEmitter {
  private readonly map = new Map<K, CoalescedRequest<T>>();
  private readonly maxConcurrent: number;
  private readonly maxWaitMs: number;
  private readonly cleanupInterval: ReturnType<typeof setInterval>;

  constructor(maxConcurrent = 100, maxWaitMs = 500) {
    super();
    this.maxConcurrent = maxConcurrent;
    this.maxWaitMs = maxWaitMs;
    this.cleanupInterval = setInterval(() => this.cleanup(), 10000);
    this.cleanupInterval.unref();
  }

  async execute(key: K, factory: () => Promise<T>): Promise<T> {
    const existing = this.map.get(key);
    if (existing) {
      existing.subscribers++;
      this.emit('coalesced', key, existing.subscribers);
      return this.waitForResult(key, existing);
    }

    if (this.map.size >= this.maxConcurrent) {
      this.emit('rejected', key, 'max_concurrent');
      return factory();
    }

    let resolve!: (value: T) => void;
    let reject!: (error: Error) => void;
    const promise = new Promise<T>((res, rej) => {
      resolve = res;
      reject = rej;
    });

    const request: CoalescedRequest<T> = {
      promise,
      resolve: resolve!,
      reject: reject!,
      timestamp: Date.now(),
      subscribers: 1,
    };

    this.map.set(key, request);
    this.emit('started', key);

    try {
      const result = await factory();
      request.resolve(result);
      this.emit('completed', key, true);
      return result;
    } catch (error) {
      request.reject(error as Error);
      this.emit('completed', key, false);
      throw error;
    } finally {
      this.cleanupKey(key);
    }
  }

  private async waitForResult(key: K, request: CoalescedRequest<T>): Promise<T> {
    const timeoutPromise = new Promise<never>((_, reject) => {
      setTimeout(() => {
        reject(new Error(`Coalescing timeout for key ${String(key)}`));
      }, this.maxWaitMs);
    });

    try {
      return await Promise.race([request.promise, timeoutPromise]);
    } catch (error) {
      this.emit('timeout', key);
      throw error;
    }
  }

  private cleanupKey(key: K): void {
    this.map.delete(key);
  }

  private cleanup(): void {
    const now = Date.now();
    for (const [key, request] of this.map.entries()) {
      if (now - request.timestamp > this.maxWaitMs * 2) {
        request.reject(new Error(`Coalescing stale request for key ${String(key)}`));
        this.map.delete(key);
        this.emit('cleanup', key);
      }
    }
  }

  getStats(): { size: number; keys: K[] } {
    return {
      size: this.map.size,
      keys: Array.from(this.map.keys()),
    };
  }

  destroy(): void {
    clearInterval(this.cleanupInterval);
    for (const request of this.map.values()) {
      request.reject(new Error('CoalescingMap destroyed'));
    }
    this.map.clear();
    this.removeAllListeners();
  }
}
```

### src/cache/NegativeCache.ts

```typescript
export interface NegativeCacheEntry {
  reason: string;
  timestamp: number;
  ttlMs: number;
}

export class NegativeCache {
  private readonly cache = new Map<string, NegativeCacheEntry>();
  private readonly defaultTtlMs: number;
  private readonly cleanupInterval: ReturnType<typeof setInterval>;

  constructor(defaultTtlMs = 30000) {
    this.defaultTtlMs = defaultTtlMs;
    this.cleanupInterval = setInterval(() => this.cleanup(), 60000);
    this.cleanupInterval.unref();
  }

  set(key: string, reason: string, ttlMs?: number): void {
    this.cache.set(key, {
      reason,
      timestamp: Date.now(),
      ttlMs: ttlMs ?? this.defaultTtlMs,
    });
  }

  get(key: string): NegativeCacheEntry | null {
    const entry = this.cache.get(key);
    if (!entry) return null;

    if (Date.now() - entry.timestamp > entry.ttlMs) {
      this.cache.delete(key);
      return null;
    }

    return entry;
  }

  has(key: string): boolean {
    return this.get(key) !== null;
  }

  delete(key: string): boolean {
    return this.cache.delete(key);
  }

  clear(): void {
    this.cache.clear();
  }

  private cleanup(): void {
    const now = Date.now();
    for (const [key, entry] of this.cache.entries()) {
      if (now - entry.timestamp > entry.ttlMs) {
        this.cache.delete(key);
      }
    }
  }

  getStats(): { size: number; hitRate: number } {
    return {
      size: this.cache.size,
      hitRate: 0,
    };
  }

  destroy(): void {
    clearInterval(this.cleanupInterval);
    this.cache.clear();
  }
}
```

### src/redis/LuaScripts.ts

```typescript
export const LUA_SCRIPTS = {
  getWithVersion: {
    numberOfKeys: 2,
    lua: `
      local versionKey = KEYS[1]
      local dataKey = KEYS[2]
      local version = redis.call('GET', versionKey)
      if not version then
        return {nil, nil, nil}
      end
      local data = redis.call('GET', dataKey)
      if not data then
        return {version, nil, nil}
      end
      return {version, data, redis.call('TTL', dataKey)}
    `,
  },

  setWithVersion: {
    numberOfKeys: 3,
    lua: `
      local versionKey = KEYS[1]
      local dataKey = KEYS[2]
      local lockKey = KEYS[3]
      local newVersion = ARGV[1]
      local newData = ARGV[2]
      local ttlMs = tonumber(ARGV[3])
      local expectedVersion = ARGV[4]
      local timestamp = ARGV[5]

      local lock = redis.call('SET', lockKey, '1', 'PX', 5000, 'NX')
      if not lock then
        return {0, 'LOCK_FAILED'}
      end

      local currentVersion = redis.call('GET', versionKey)
      if expectedVersion ~= '-1' and currentVersion and tonumber(currentVersion) ~= tonumber(expectedVersion) then
        redis.call('DEL', lockKey)
        return {0, 'VERSION_CONFLICT', currentVersion}
      end

      redis.call('SET', versionKey, newVersion)
      redis.call('SET', dataKey, newData, 'PX', ttlMs)
      redis.call('DEL', lockKey)
      return {1, newVersion}
    `,
  },

  compareAndSet: {
    numberOfKeys: 3,
    lua: `
      local versionKey = KEYS[1]
      local dataKey = KEYS[2]
      local lockKey = KEYS[3]
      local expectedVersion = ARGV[1]
      local newVersion = ARGV[2]
      local newData = ARGV[3]
      local ttlMs = tonumber(ARGV[4])

      local lock = redis.call('SET', lockKey, '1', 'PX', 5000, 'NX')
      if not lock then
        return {0, 'LOCK_FAILED'}
      end

      local currentVersion = redis.call('GET', versionKey)
      if not currentVersion or tonumber(currentVersion) ~= tonumber(expectedVersion) then
        redis.call('DEL', lockKey)
        return {0, 'VERSION_MISMATCH', currentVersion or 'nil'}
      end

      redis.call('SET', versionKey, newVersion)
      redis.call('SET', dataKey, newData, 'PX', ttlMs)
      redis.call('DEL', lockKey)
      return {1, newVersion}
    `,
  },

  deleteWithVersion: {
    numberOfKeys: 3,
    lua: `
      local versionKey = KEYS[1]
      local dataKey = KEYS[2]
      local lockKey = KEYS[3]
      local expectedVersion = ARGV[1]

      local lock = redis.call('SET', lockKey, '1', 'PX', 5000, 'NX')
      if not lock then
        return {0, 'LOCK_FAILED'}
      end

      local currentVersion = redis.call('GET', versionKey)
      if currentVersion and tonumber(currentVersion) ~= tonumber(expectedVersion) then
        redis.call('DEL', lockKey)
        return {0, 'VERSION_MISMATCH', currentVersion}
      end

      redis.call('DEL', versionKey, dataKey)
      redis.call('DEL', lockKey)
      return {1}
    `,
  },

  invalidateVersion: {
    numberOfKeys: 1,
    lua: `
      local versionKey = KEYS[1]
      local newVersion = ARGV[1]
      redis.call('SET', versionKey, newVersion)
      return {newVersion}
    `,
  },

  acquireLock: {
    numberOfKeys: 1,
    lua: `
      local lockKey = KEYS[1]
      local ttlMs = tonumber(ARGV[1])
      local lock = redis.call('SET', lockKey, '1', 'PX', ttlMs, 'NX')
      return lock and 1 or 0
    `,
  },

  releaseLock: {
    numberOfKeys: 1,
    lua: `
      local lockKey = KEYS[1]
      redis.call('DEL', lockKey)
      return 1
    `,
  },
} as const;

export type LuaScriptName = keyof typeof LUA_SCRIPTS;
```

### src/redis/RedisClient.ts

```typescript
import Redis from 'ioredis';
import { EventEmitter } from 'events';
import { LUA_SCRIPTS, LuaScriptName } from './LuaScripts';
import { CacheConfig, RedisConfig } from '../config/CacheConfig';
import { RedisUnavailableError } from '../utils/errors';
import pino from 'pino';

export interface RedisClientEvents {
  connect: []; 
  disconnect: [Error | null];
  error: [Error];
  ready: [];
  close: [];
}

export class RedisClient extends EventEmitter<RedisClientEvents> {
  private client: Redis | null = null;
  private readonly config: RedisConfig;
  private readonly logger: pino.Logger;
  private connected = false;
  private connecting = false;
  private scriptsLoaded = false;

  constructor(config: RedisConfig, logger: pino.Logger) {
    super();
    this.config = config;
    this.logger = logger.child({ component: 'RedisClient' });
  }

  async connect(): Promise<void> {
    if (this.connected || this.connecting) return;

    this.connecting = true;
    this.client = new Redis({
      host: this.config.host,
      port: this.config.port,
      password: this.config.password,
      db: this.config.db,
      connectionName: this.config.connectionName,
      maxRetriesPerRequest: this.config.maxRetriesPerRequest,
      retryStrategy: this.config.retryStrategy.enabled
        ? (times) => {
            if (times > this.config.retryStrategy.maxRetries) {
              return null;
            }
            const delay = Math.min(
              this.config.retryStrategy.retryDelay * Math.pow(2, times - 1),
              this.config.retryStrategy.maxRetryDelay
            );
            return delay;
          }
        : undefined,
      enableReadyCheck: this.config.enableReadyCheck,
      lazyConnect: this.config.lazyConnect,
      connectTimeout: this.config.connectTimeout,
      commandTimeout: this.config.commandTimeout,
      family: this.config.family,
      tls: this.config.tls,
    });

    this.client.on('connect', () => {
      this.logger.info('Redis connected');
      this.emit('connect');
    });

    this.client.on('ready', () => {
      this.connected = true;
      this.connecting = false;
      this.logger.info('Redis ready');
      this.loadScripts();
      this.emit('ready');
    });

    this.client.on('error', (error) => {
      this.logger.error({ err: error }, 'Redis error');
      this.emit('error', error);
    });

    this.client.on('close', () => {
      this.connected = false;
      this.logger.warn('Redis connection closed');
      this.emit('close');
    });

    this.client.on('reconnecting', () => {
      this.logger.info('Redis reconnecting');
    });

    try {
      await this.client.connect();
    } catch (error) {
      this.connecting = false;
      throw new RedisUnavailableError(error as Error);
    }
  }

  private async loadScripts(): Promise<void> {
    if (!this.client || this.scriptsLoaded) return;

    for (const [name, script] of Object.entries(LUA_SCRIPTS)) {
      try {
        this.client.defineCommand(name, {
          numberOfKeys: script.numberOfKeys,
          lua: script.lua,
        });
      } catch (error) {
        this.logger.error({ err: error, script: name }, 'Failed to define Lua script');
      }
    }
    this.scriptsLoaded = true;
  }

  async executeScript<T>(
    scriptName: LuaScriptName,
    keys: string[],
    args: (string | number)[]
  ): Promise<T> {
    if (!this.client) throw new RedisUnavailableError();
    if (!this.connected) throw new RedisUnavailableError();

    const command = this.client[scriptName] as (...args: unknown[]) => Promise<T>;
    if (!command) {
      throw new Error(`Lua script ${scriptName} not loaded`);
    }

    return command.call(this.client, ...keys, ...args);
  }

  async get(key: string): Promise<string | null> {
    if (!this.client) throw new RedisUnavailableError();
    return this.client.get(key);
  }

  async set(key: string, value: string, pxMs?: number): Promise<'OK' | null> {
    if (!this.client) throw new RedisUnavailableError();
    if (pxMs) return this.client.set(key, value, 'PX', pxMs);
    return this.client.set(key, value);
  }

  async del(...keys: string[]): Promise<number> {
    if (!this.client) throw new RedisUnavailableError();
    return this.client.del(...keys);
  }

  async exists(...keys: string[]): Promise<number> {
    if (!this.client) throw new RedisUnavailableError();
    return this.client.exists(...keys);
  }

  async pttl(key: string): Promise<number> {
    if (!this.client) throw new RedisUnavailableError();
    return this.client.pttl(key);
  }

  async publish(channel: string, message: string): Promise<number> {
    if (!this.client) throw new RedisUnavailableError();
    return this.client.publish(channel, message);
  }

  async subscribe(channel: string, callback: (message: string) => void): Promise<void> {
    if (!this.client) throw new RedisUnavailableError();
    const subscriber = this.client.duplicate();
    await subscriber.subscribe(channel);
    subscriber.on('message', (ch, msg) => {
      if (ch === channel) callback(msg);
    });
  }

  async ping(): Promise<boolean> {
    if (!this.client || !this.connected) return false;
    try {
      const result = await this.client.ping();
      return result === 'PONG';
    } catch {
      return false;
    }
  }

  isConnected(): boolean {
    return this.connected;
  }

  getClient(): Redis | null {
    return this.client;
  }

  async disconnect(): Promise<void> {
    if (this.client) {
      await this.client.quit();
      this.client = null;
      this.connected = false;
      this.connecting = false;
    }
  }
}
```

### src/cache/InvalidationBus.ts

```typescript
import { EventEmitter } from 'events';
import { RedisClient } from '../redis/RedisClient';
import { CacheConfig } from '../config/CacheConfig';
import { generateVersion, parseVersionedKey, buildVersionedKey } from '../utils/version';
import pino from 'pino';

export interface InvalidationMessage {
  key: string;
  version: number;
  timestamp: number;
  sourceInstanceId: string;
  type: 'invalidate' | 'update' | 'delete';
}

export interface InvalidationBusEvents {
  invalidation: [InvalidationMessage];
  connected: [];
  disconnected: [Error | null];
  error: [Error];
  lagDetected: [string, number];
}

export class InvalidationBus extends EventEmitter<InvalidationBusEvents> {
  private readonly redis: RedisClient;
  private readonly config: CacheConfig;
  private readonly logger: pino.Logger;
  private readonly channel: string;
  private readonly instanceId: string;
  private subscriber: RedisClient | null = null;
  private connected = false;
  private lastProcessedVersion = new Map<string, number>();
  private messageBuffer: InvalidationMessage[] = [];
  private readonly maxBufferSize = 1000;
  private processing = false;

  constructor(redis: RedisClient, config: CacheConfig, logger: pino.Logger) {
    super();
    this.redis = redis;
    this.config = config;
    this.logger = logger.child({ component: 'InvalidationBus' });
    this.channel = `cache:invalidation:${config.redis.db}`;
    this.instanceId = config.telemetry.instanceId;
  }

  async start(): Promise<void> {
    this.subscriber = new RedisClient(this.config.redis, this.logger);
    this.subscriber.on('connect', () => {
      this.connected = true;
      this.logger.info('Invalidation bus connected');
      this.emit('connected');
      this.processBuffer();
    });

    this.subscriber.on('disconnect', (error) => {
      this.connected = false;
      this.logger.warn({ err: error }, 'Invalidation bus disconnected');
      this.emit('disconnected', error);
    });

    this.subscriber.on('error', (error) => {
      this.logger.error({ err: error }, 'Invalidation bus error');
      this.emit('error', error);
    });

    await this.subscriber.connect();
    await this.subscriber.subscribe(this.channel, this.handleMessage.bind(this));
  }

  private handleMessage(message: string): void {
    try {
      const parsed: InvalidationMessage = JSON.parse(message);
      if (parsed.sourceInstanceId === this.instanceId) {
        return;
      }
      this.messageBuffer.push(parsed);
      if (this.messageBuffer.length > this.maxBufferSize) {
        this.messageBuffer.shift();
      }
      this.processBuffer();
    } catch (error) {
      this.logger.error({ err: error, message }, 'Failed to parse invalidation message');
    }
  }

  private async processBuffer(): Promise<void> {
    if (this.processing || this.messageBuffer.length === 0) return;
    this.processing = true;

    while (this.messageBuffer.length > 0) {
      const message = this.messageBuffer.shift()!;
      await this.processMessage(message);
    }

    this.processing = false;
  }

  private async processMessage(message: InvalidationMessage): Promise<void> {
    const lastVersion = this.lastProcessedVersion.get(message.key) ?? 0;
    if (message.version <= lastVersion) {
      this.logger.debug({ key: message.key, version: message.version, lastVersion }, 'Stale invalidation message ignored');
      return;
    }

    const lagMs = Date.now() - message.timestamp;
    if (lagMs > 5000) {
      this.emit('lagDetected', message.key, lagMs);
    }

    this.lastProcessedVersion.set(message.key, message.version);
    this.emit('invalidation', message);
  }

  async publishInvalidation(key: string, version: number, type: InvalidationMessage['type'] = 'invalidate'): Promise<void> {
    const message: InvalidationMessage = {
      key,
      version,
      timestamp: Date.now(),
      sourceInstanceId: this.instanceId,
      type,
    };

    await this.redis.publish(this.channel, JSON.stringify(message));
    this.lastProcessedVersion.set(key, version);
  }

  async recoverVersion(key: string): Promise<number> {
    const versionKey = `${this.config.cache.versionKeyPrefix}${key}`;
    const versionStr = await this.redis.get(versionKey);
    return versionStr ? parseInt(versionStr, 10) : 0;
  }

  async syncVersion(key: string): Promise<number> {
    const remoteVersion = await this.recoverVersion(key);
    const localVersion = this.lastProcessedVersion.get(key) ?? 0;
    const maxVersion = Math.max(remoteVersion, localVersion);
    this.lastProcessedVersion.set(key, maxVersion);
    return maxVersion;
  }

  isConnected(): boolean {
    return this.connected;
  }

  getStats(): { bufferSize: number; trackedKeys: number; connected: boolean } {
    return {
      bufferSize: this.messageBuffer.length,
      trackedKeys: this.lastProcessedVersion.size,
      connected: this.connected,
    };
  }

  async stop(): Promise<void> {
    if (this.subscriber) {
      await this.subscriber.disconnect();
      this.subscriber = null;
    }
    this.connected = false;
    this.messageBuffer = [];
    this.lastProcessedVersion.clear();
  }
}
```

### src/cache/DegradedCache.ts

```typescript
import { CacheEntry, createCacheEntry, serializeEntry, deserializeEntry } from './CacheEntry';
import { CacheConfig } from '../config/CacheConfig';
import { generateVersion } from '../utils/version';
import pino from 'pino';

interface LocalCacheEntry<T> {
  entry: CacheEntry<T>;
  expiresAt: number;
}

export class DegradedCache<T> {
  private readonly cache = new Map<string, LocalCacheEntry<T>>();
  private readonly config: CacheConfig;
  private readonly logger: pino.Logger;
  private readonly cleanupInterval: ReturnType<typeof setInterval>;
  private hits = 0;
  private misses = 0;

  constructor(config: CacheConfig, logger: pino.Logger) {
    this.config = config;
    this.logger = logger.child({ component: 'DegradedCache' });
    this.cleanupInterval = setInterval(() => this.cleanup(), 30000);
    this.cleanupInterval.unref();
  }

  get(key: string): CacheEntry<T> | null {
    const stored = this.cache.get(key);
    if (!stored) {
      this.misses++;
      return null;
    }

    if (Date.now() > stored.expiresAt) {
      this.cache.delete(key);
      this.misses++;
      return null;
    }

    this.hits++;
    return stored.entry;
  }

  set(key: string, entry: CacheEntry<T>): void {
    if (this.cache.size >= this.config.degradation.maxLocalCacheSize) {
      this.evictOldest();
    }

    this.cache.set(key, {
      entry,
      expiresAt: Date.now() + this.config.degradation.localCacheTtlMs,
    });
  }

  delete(key: string): boolean {
    return this.cache.delete(key);
  }

  has(key: string): boolean {
    return this.get(key) !== null;
  }

  clear(): void {
    this.cache.clear();
    this.hits = 0;
    this.misses = 0;
  }

  private evictOldest(): void {
    let oldestKey: string | null = null;
    let oldestTime = Infinity;

    for (const [key, value] of this.cache.entries()) {
      if (value.expiresAt < oldestTime) {
        oldestTime = value.expiresAt;
        oldestKey = key;
      }
    }

    if (oldestKey) {
      this.cache.delete(oldestKey);
    }
  }

  private cleanup(): void {
    const now = Date.now();
    for (const [key, value] of this.cache.entries()) {
      if (now > value.expiresAt) {
        this.cache.delete(key);
      }
    }
  }

  getStats(): { size: number; hits: number; misses: number; hitRate: number } {
    const total = this.hits + this.misses;
    return {
      size: this.cache.size,
      hits: this.hits,
      misses: this.misses,
      hitRate: total > 0 ? this.hits / total : 0,
    };
  }

  destroy(): void {
    clearInterval(this.cleanupInterval);
    this.cache.clear();
  }
}
```

### src/telemetry/Metrics.ts

```typescript
import { Registry, Counter, Gauge, Histogram, collectDefaultMetrics } from 'prom-client';
import { CacheConfig } from '../config/CacheConfig';

export interface CacheMetrics {
  hitsTotal: Counter<string>;
  missesTotal: Counter<string>;
  staleHitsTotal: Counter<string>;
  negativeHitsTotal: Counter<string>;
  coalescedRequestsTotal: Counter<string>;
  backendCallsTotal: Counter<string>;
  invalidationLagMs: Histogram<string>;
  invalidationReceivedTotal: Counter<string>;
  invalidationPublishedTotal: Counter<string>;
  redisErrorsTotal: Counter<string>;
  degradedModeGauge: Gauge<string>;
  localCacheSize: Gauge<string>;
  operationDurationMs: Histogram<string>;
}

export function createMetrics(config: CacheConfig, registry?: Registry): CacheMetrics {
  const register = registry ?? new Registry();
  
  if (config.telemetry.enableMetrics) {
    collectDefaultMetrics({ register, prefix: 'cache_' });
  }

  const prefix = 'cache_';

  const hitsTotal = new Counter({
    name: `${prefix}hits_total`,
    help: 'Total number of cache hits',
    labelNames: ['state'],
    registers: [register],
  });

  const missesTotal = new Counter({
    name: `${prefix}misses_total`,
    help: 'Total number of cache misses',
    labelNames: ['reason'],
    registers: [register],
  });

  const staleHitsTotal = new Counter({
    name: `${prefix}stale_hits_total`,
    help: 'Total number of stale-while-revalidate hits',
    labelNames: [],
    registers: [register],
  });

  const negativeHitsTotal = new Counter({
    name: `${prefix}negative_hits_total`,
    help: 'Total number of negative cache hits',
    labelNames: ['reason'],
    registers: [register],
  });

  const coalescedRequestsTotal = new Counter({
    name: `${prefix}coalesced_requests_total`,
    help: 'Total number of requests coalesced',
    labelNames: [],
    registers: [register],
  });

  const backendCallsTotal = new Counter({
    name: `${prefix}backend_calls_total`,
    help: 'Total number of backend calls',
    labelNames: ['result'],
    registers: [register],
  });

  const invalidationLagMs = new Histogram({
    name: `${prefix}invalidation_lag_ms`,
    help: 'Invalidation message lag in milliseconds',
    labelNames: [],
    buckets: [1, 5, 10, 50, 100, 500, 1000, 5000, 10000],
    registers: [register],
  });

  const invalidationReceivedTotal = new Counter({
    name: `${prefix}invalidation_received_total`,
    help: 'Total number of invalidation messages received',
    labelNames: ['type'],
    registers: [register],
  });

  const invalidationPublishedTotal = new Counter({
    name: `${prefix}invalidation_published_total`,
    help: 'Total number of invalidation messages published',
    labelNames: ['type'],
    registers: [register],
  });

  const redisErrorsTotal = new Counter({
    name: `${prefix}redis_errors_total`,
    help: 'Total number of Redis errors',
    labelNames: ['operation', 'error_type'],
    registers: [register],
  });

  const degradedModeGauge = new Gauge({
    name: `${prefix}degraded_mode`,
    help: 'Whether cache is in degraded mode (1) or normal (0)',
    labelNames: [],
    registers: [register],
  });

  const localCacheSize = new Gauge({
    name: `${prefix}local_cache_size`,
    help: 'Number of entries in local degraded cache',
    labelNames: [],
    registers: [register],
  });

  const operationDurationMs = new Histogram({
    name: `${prefix}operation_duration_ms`,
    help: 'Cache operation duration in milliseconds',
    labelNames: ['operation'],
    buckets: [1, 5, 10, 25, 50, 100, 250, 500, 1000],
    registers: [register],
  });

  return {
    hitsTotal,
    missesTotal,
    staleHitsTotal,
    negativeHitsTotal,
    coalescedRequestsTotal,
    backendCallsTotal,
    invalidationLagMs,
    invalidationReceivedTotal,
    invalidationPublishedTotal,
    redisErrorsTotal,
    degradedModeGauge,
    localCacheSize,
    operationDurationMs,
  };
}

export function getMetricsRegistry(metrics: CacheMetrics): Registry {
  return metrics.hitsTotal.registries[0] as Registry;
}
```

### src/telemetry/Tracing.ts

```typescript
import { trace, Span, SpanStatusCode, Tracer, context, propagation, SpanKind } from '@opentelemetry/api';
import { NodeTracerProvider } from '@opentelemetry/sdk-trace-node';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { BatchSpanProcessor } from '@opentelemetry/sdk-trace-base';
import { PrometheusExporter } from '@opentelemetry/exporter-prometheus';
import { CacheConfig } from '../config/CacheConfig';

export interface TracingContext {
  tracer: Tracer;
  provider: NodeTracerProvider | null;
  exporter: PrometheusExporter | null;
}

export function initializeTracing(config: CacheConfig): TracingContext {
  if (!config.telemetry.enableTracing) {
    return {
      tracer: trace.getTracer(config.telemetry.serviceName),
      provider: null,
      exporter: null,
    };
  }

  const provider = new NodeTracerProvider({
    resource: new Resource({
      [SemanticResourceAttributes.SERVICE_NAME]: config.telemetry.serviceName,
      [SemanticResourceAttributes.SERVICE_INSTANCE_ID]: config.telemetry.instanceId,
    }),
  });

  const exporter = new PrometheusExporter({
    port: config.telemetry.metricsPort,
    endpoint: '/metrics',
  }, () => {});

  provider.addSpanProcessor(new BatchSpanProcessor(exporter));
  provider.register();

  const tracer = trace.getTracer(config.telemetry.serviceName);

  return { tracer, provider, exporter };
}

export function createSpan(
  tracer: Tracer,
  name: string,
  attributes: Record<string, string | number | boolean> = {},
  kind: SpanKind = SpanKind.INTERNAL
): Span {
  return tracer.startActiveSpan(name, { kind, attributes }, (span) => {
    return span;
  });
}

export function endSpan(span: Span, error?: Error): void {
  if (error) {
    span.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
    span.recordException(error);
  } else {
    span.setStatus({ code: SpanStatusCode.OK });
  }
  span.end();
}

export function injectContext(carrier: Record<string, string>): void {
  propagation.inject(context.active(), carrier);
}

export function extractContext(carrier: Record<string, string>): context.Context {
  return propagation.extract(context.active(), carrier);
}

export const CACHE_SPAN_ATTRIBUTES = {
  KEY: 'cache.key',
  OPERATION: 'cache.operation',
  HIT_STATE: 'cache.hit_state',
  VERSION: 'cache.version',
  STALE: 'cache.stale',
  NEGATIVE: 'cache.negative',
  COALESCED: 'cache.coalesced',
  BACKEND_LATENCY_MS: 'cache.backend_latency_ms',
  INVALIDATION_LAG_MS: 'cache.invalidation_lag_ms',
  DEGRADED_MODE: 'cache.degraded_mode',
} as const;

export type HitState = 'hit' | 'miss' | 'stale' | 'negative' | 'error';
```

### src/cache/CacheLayer.ts

```typescript
import { EventEmitter } from 'events';
import { CacheConfig, DEFAULT_CONFIG } from '../config/CacheConfig';
import { RedisClient } from '../redis/RedisClient';
import { InvalidationBus, InvalidationMessage } from './InvalidationBus';
import { CoalescingMap } from './CoalescingMap';
import { NegativeCache } from './NegativeCache';
import { DegradedCache } from './DegradedCache';
import { CacheEntry, StoredCacheEntry, createCacheEntry, createNegativeEntry, serializeEntry, deserializeEntry, isNegativeEntry } from './CacheEntry';
import { generateVersion, buildVersionedKey, extractBaseKey, isStale } from '../utils/version';
import { CacheMetrics, createMetrics } from '../telemetry/Metrics';
import { TracingContext, initializeTracing, createSpan, endSpan, CACHE_SPAN_ATTRIBUTES, HitState } from '../telemetry/Tracing';
import { RedisUnavailableError, VersionConflictError } from '../utils/errors';
import pino from 'pino';

export interface CacheLayerOptions {
  config?: Partial<CacheConfig>;
  logger?: pino.Logger;
  backendFetcher: (key: string) => Promise<unknown>;
  backendUpdater?: (key: string, value: unknown, version: number) => Promise<number>;
  backendDeleter?: (key: string, version: number) => Promise<void>;
}

export interface GetResult<T> {
  value: T | null;
  hitState: HitState;
  version: number;
  stale: boolean;
  fromDegraded: boolean;
}

export interface SetResult {
  version: number;
  success: boolean;
}

export interface CacheLayerEvents {
  hit: [string, HitState];
  miss: [string, string];
  invalidation: [InvalidationMessage];
  degradedModeChange: [boolean];
  error: [Error];
}

export class CacheLayer<T = unknown> extends EventEmitter<CacheLayerEvents> {
  private readonly config: CacheConfig;
  private readonly logger: pino.Logger;
  private readonly redis: RedisClient;
  private readonly invalidationBus: InvalidationBus;
  private readonly coalescingMap: CoalescingMap<string, CacheEntry<T>>;
  private readonly negativeCache: NegativeCache;
  private readonly degradedCache: DegradedCache<T>;
  private readonly metrics: CacheMetrics;
  private readonly tracing: TracingContext;
  private readonly backendFetcher: (key: string) => Promise<T>;
  private readonly backendUpdater?: (key: string, value: T, version: number) => Promise<number>;
  private readonly backendDeleter?: (key: string, version: number) => Promise<void>;
  private degradedMode = false;
  private circuitBreakerFailures = 0;
  private circuitBreakerOpen = false;
  private circuitBreakerTimer: ReturnType<typeof setTimeout> | null = null;
  private healthCheckInterval: ReturnType<typeof setInterval> | null = null;

  constructor(options: CacheLayerOptions) {
    super();
    this.config = { ...DEFAULT_CONFIG, ...options.config } as CacheConfig;
    this.logger = options.logger?.child({ component: 'CacheLayer' }) ?? pino({ level: 'info' }).child({ component: 'CacheLayer' });
    this.backendFetcher = options.backendFetcher as (key: string) => Promise<T>;
    this.backendUpdater = options.backendUpdater as (key: string, value: T, version: number) => Promise<number> | undefined;
    this.backendDeleter = options.backendDeleter;

    this.redis = new RedisClient(this.config.redis, this.logger);
    this.invalidationBus = new InvalidationBus(this.redis, this.config, this.logger);
    this.coalescingMap = new CoalescingMap<string, CacheEntry<T>>(
      this.config.cache.coalescingMaxConcurrent,
      this.config.cache.maxCoalescingWaitMs
    );
    this.negativeCache = new NegativeCache(this.config.cache.negativeCacheTtlMs);
    this.degradedCache = new DegradedCache<T>(this.config, this.logger);
    this.metrics = createMetrics(this.config);
    this.tracing = initializeTracing(this.config);

    this.setupEventHandlers();
  }

  private setupEventHandlers(): void {
    this.redis.on('error', (error) => {
      this.metrics.redisErrorsTotal.inc({ operation: 'connection', error_type: error.name });
      this.handleRedisError(error);
    });

    this.invalidationBus.on('invalidation', (message) => {
      this.metrics.invalidationReceivedTotal.inc({ type: message.type });
      this.handleInvalidation(message);
    });

    this.invalidationBus.on('lagDetected', (key, lagMs) => {
      this.metrics.invalidationLagMs.observe(lagMs);
      this.logger.warn({ key, lagMs }, 'Invalidation lag detected');
    });

    this.coalescingMap.on('coalesced', (key, count) => {
      this.metrics.coalescedRequestsTotal.inc();
      this.logger.debug({ key, count }, 'Request coalesced');
    });

    if (this.config.degradation.enabled) {
      this.startHealthChecks();
    }
  }

  async start(): Promise<void> {
    await this.redis.connect();
    await this.invalidationBus.start();
    this.logger.info('Cache layer started');
  }

  async stop(): Promise<void> {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
    }
    if (this.circuitBreakerTimer) {
      clearTimeout(this.circuitBreakerTimer);
    }
    await this.invalidationBus.stop();
    await this.redis.disconnect();
    this.coalescingMap.destroy();
    this.negativeCache.destroy();
    this.degradedCache.destroy();
    if (this.tracing.provider) {
      await this.tracing.provider.shutdown();
    }
    this.logger.info('Cache layer stopped');
  }

  async get(key: string): Promise<GetResult<T>> {
    const span = createSpan(this.tracing.tracer, 'cache.get', {
      [CACHE_SPAN_ATTRIBUTES.KEY]: key,
      [CACHE_SPAN_ATTRIBUTES.OPERATION]: 'get',
    });

    const startTime = Date.now();
    let hitState: HitState = 'miss';
    let fromDegraded = false;

    try {
      const negativeEntry = this.negativeCache.get(key);
      if (negativeEntry) {
        hitState = 'negative';
        this.metrics.negativeHitsTotal.inc({ reason: negativeEntry.reason });
        this.metrics.hitsTotal.inc({ state: 'negative' });
        endSpan(span);
        this.emit('hit', key, 'negative');
        return {
          value: null,
          hitState: 'negative',
          version: 0,
          stale: false,
          fromDegraded: false,
        };
      }

      if (this.degradedMode) {
        const degradedEntry = this.degradedCache.get(key);
        if (degradedEntry) {
          hitState = degradedEntry.stale ? 'stale' : 'hit';
          fromDegraded = true;
          this.metrics.hitsTotal.inc({ state: hitState });
          if (hitState === 'stale') this.metrics.staleHitsTotal.inc();
          endSpan(span, undefined, { [CACHE_SPAN_ATTRIBUTES.HIT_STATE]: hitState, [CACHE_SPAN_ATTRIBUTES.DEGRADED_MODE]: true });
          this.emit('hit', key, hitState);
          return {
            value: degradedEntry.value as T,
            hitState,
            version: degradedEntry.version,
            stale: degradedEntry.stale,
            fromDegraded: true,
          };
        }
        this.metrics.missesTotal.inc({ reason: 'degraded_cache_miss' });
        endSpan(span, undefined, { [CACHE_SPAN_ATTRIBUTES.HIT_STATE]: 'miss', [CACHE_SPAN_ATTRIBUTES.DEGRADED_MODE]: true });
        this.emit('miss', key, 'degraded_cache_miss');
        return { value: null, hitState: 'miss', version: 0, stale: false, fromDegraded: true };
      }

      const versionKey = `${this.config.cache.versionKeyPrefix}${key}`;
      const dataKey = `${this.config.cache.dataKeyPrefix}${key}`;

      const result = await this.redis.executeScript<[string | null, string | null, number | null]>(
        'getWithVersion',
        [versionKey, dataKey],
        []
      );

      const [versionStr, dataStr, ttl] = result;

      if (!versionStr || !dataStr) {
        this.metrics.missesTotal.inc({ reason: 'not_found' });
        hitState = 'miss';
        endSpan(span, undefined, { [CACHE_SPAN_ATTRIBUTES.HIT_STATE]: 'miss' });
        this.emit('miss', key, 'not_found');
        return { value: null, hitState: 'miss', version: 0, stale: false, fromDegraded: false };
      }

      const version = parseInt(versionStr, 10);
      const stored: StoredCacheEntry<T> = JSON.parse(dataStr);
      const entry = deserializeEntry(stored);

      if (isNegativeEntry(entry)) {
        this.negativeCache.set(key, entry.negativeReason!, entry.ttlMs);
        hitState = 'negative';
        this.metrics.negativeHitsTotal.inc({ reason: entry.negativeReason! });
        this.metrics.hitsTotal.inc({ state: 'negative' });
        endSpan(span, undefined, { [CACHE_SPAN_ATTRIBUTES.HIT_STATE]: 'negative', [CACHE_SPAN_ATTRIBUTES.VERSION]: version });
        this.emit('hit', key, 'negative');
        return { value: null, hitState: 'negative', version, stale: false, fromDegraded: false };
      }

      if (entry.stale) {
        hitState = 'stale';
        this.metrics.staleHitsTotal.inc();
        this.metrics.hitsTotal.inc({ state: 'stale' });
        this.triggerBackgroundRefresh(key, version);
      } else {
        hitState = 'hit';
        this.metrics.hitsTotal.inc({ state: 'hit' });
      }

      this.degradedCache.set(key, entry);

      endSpan(span, undefined, {
        [CACHE_SPAN_ATTRIBUTES.HIT_STATE]: hitState,
        [CACHE_SPAN_ATTRIBUTES.VERSION]: version,
        [CACHE_SPAN_ATTRIBUTES.STALE]: entry.stale,
      });
      this.emit('hit', key, hitState);

      return {
        value: entry.value,
        hitState,
        version,
        stale: entry.stale,
        fromDegraded: false,
      };
    } catch (error) {
      if (error instanceof RedisUnavailableError) {
        return this.getDegraded(key);
      }
      this.metrics.redisErrorsTotal.inc({ operation: 'get', error_type: (error as Error).name });
      hitState = 'error';
      this.metrics.missesTotal.inc({ reason: 'error' });
      endSpan(span, error as Error, { [CACHE_SPAN_ATTRIBUTES.HIT_STATE]: 'error' });
      this.emit('error', error as Error);
      throw error;
    } finally {
      this.metrics.operationDurationMs.observe({ operation: 'get' }, Date.now() - startTime);
    }
  }

  private async getDegraded(key: string): Promise<GetResult<T>> {
    const entry = this.degradedCache.get(key);
    if (entry) {
      const hitState = entry.stale ? 'stale' : 'hit';
      this.metrics.hitsTotal.inc({ state: hitState });
      if (hitState === 'stale') this.metrics.staleHitsTotal.inc();
      this.metrics.degradedModeGauge.set(1);
      return {
        value: entry.value as T,
        hitState,
        version: entry.version,
        stale: entry.stale,
        fromDegraded: true,
      };
    }
    this.metrics.missesTotal.inc({ reason: 'degraded_cache_miss' });
    return { value: null, hitState: 'miss', version: 0, stale: false, fromDegraded: true };
  }

  private async triggerBackgroundRefresh(key: string, currentVersion: number): Promise<void> {
    setImmediate(async () => {
      try {
        await this.refresh(key, currentVersion);
      } catch (error) {
        this.logger.error({ err: error, key }, 'Background refresh failed');
      }
    });
  }

  async refresh(key: string, expectedVersion?: number): Promise<GetResult<T>> {
    const span = createSpan(this.tracing.tracer, 'cache.refresh', {
      [CACHE_SPAN_ATTRIBUTES.KEY]: key,
      [CACHE_SPAN_ATTRIBUTES.OPERATION]: 'refresh',
    });

    const startTime = Date.now();

    try {
      return await this.coalescingMap.execute(key, async () => {
        const backendStart = Date.now();
        let value: T;
        try {
          value = await this.backendFetcher(key);
          this.metrics.backendCallsTotal.inc({ result: 'success' });
        } catch (error) {
          this.metrics.backendCallsTotal.inc({ result: 'error' });
          const negativeEntry = createNegativeEntry(
            (error as Error).message,
            this.config.cache.negativeCacheTtlMs,
            expectedVersion ?? generateVersion()
          );
          await this.setInternal(key, negativeEntry, expectedVersion);
          endSpan(span, error as Error);
          throw error;
        }

        const backendLatency = Date.now() - backendStart;
        const newVersion = generateVersion();
        const entry = createCacheEntry(value, newVersion, this.config.cache.defaultTtlMs);
        await this.setInternal(key, entry, expectedVersion);

        const result: GetResult<T> = {
          value,
          hitState: 'miss',
          version: newVersion,
          stale: false,
          fromDegraded: false,
        };

        endSpan(span, undefined, {
          [CACHE_SPAN_ATTRIBUTES.HIT_STATE]: 'miss',
          [CACHE_SPAN_ATTRIBUTES.VERSION]: newVersion,
          [CACHE_SPAN_ATTRIBUTES.BACKEND_LATENCY_MS]: backendLatency,
        });
        return result;
      });
    } catch (error) {
      if (error instanceof RedisUnavailableError) {
        this.handleRedisError(error);
      }
      endSpan(span, error as Error);
      throw error;
    } finally {
      this.metrics.operationDurationMs.observe({ operation: 'refresh' }, Date.now() - startTime);
    }
  }

  async set(key: string, value: T, ttlMs?: number): Promise<SetResult> {
    const span = createSpan(this.tracing.tracer, 'cache.set', {
      [CACHE_SPAN_ATTRIBUTES.KEY]: key,
      [CACHE_SPAN_ATTRIBUTES.OPERATION]: 'set',
    });

    const startTime = Date.now();

    try {
      const version = generateVersion();
      const entry = createCacheEntry(value, version, ttlMs ?? this.config.cache.defaultTtlMs);
      await this.setInternal(key, entry);
      endSpan(span, undefined, { [CACHE_SPAN_ATTRIBUTES.VERSION]: version });
      return { version, success: true };
    } catch (error) {
      endSpan(span, error as Error);
      throw error;
    } finally {
      this.metrics.operationDurationMs.observe({ operation: 'set' }, Date.now() - startTime);
    }
  }

  private async setInternal(key: string, entry: CacheEntry<T>, expectedVersion = -1): Promise<void> {
    if (this.degradedMode) {
      this.degradedCache.set(key, entry);
      return;
    }

    const versionKey = `${this.config.cache.versionKeyPrefix}${key}`;
    const dataKey = `${this.config.cache.dataKeyPrefix}${key}`;
    const lockKey = `${this.config.cache.versionKeyPrefix}lock:${key}`;

    const serialized = JSON.stringify(serializeEntry(entry));

    await this.redis.executeScript<[number, string]>(
      'setWithVersion',
      [versionKey, dataKey, lockKey],
      [entry.version, serialized, entry.ttlMs, expectedVersion, entry.timestamp]
    );

    this.degradedCache.set(key, entry);

    await this.invalidationBus.publishInvalidation(key, entry.version, 'update');
    this.metrics.invalidationPublishedTotal.inc({ type: 'update' });
  }

  async compareAndSet(key: string, expectedVersion: number, newValue: T, ttlMs?: number): Promise<SetResult> {
    const span = createSpan(this.tracing.tracer, 'cache.compareAndSet', {
      [CACHE_SPAN_ATTRIBUTES.KEY]: key,
      [CACHE_SPAN_ATTRIBUTES.OPERATION]: 'compareAndSet',
      [CACHE_SPAN_ATTRIBUTES.VERSION]: expectedVersion,
    });

    const startTime = Date.now();

    try {
      if (this.degradedMode) {
        const current = this.degradedCache.get(key);
        if (!current || current.version !== expectedVersion) {
          throw new VersionConflictError(key, expectedVersion, current?.version ?? 0);
        }
        const newVersion = generateVersion();
        const entry = createCacheEntry(newValue, newVersion, ttlMs ?? this.config.cache.defaultTtlMs);
        this.degradedCache.set(key, entry);
        endSpan(span);
        return { version: newVersion, success: true };
      }

      const versionKey = `${this.config.cache.versionKeyPrefix}${key}`;
      const dataKey = `${this.config.cache.dataKeyPrefix}${key}`;
      const lockKey = `${this.config.cache.versionKeyPrefix}lock:${key}`;

      const newVersion = generateVersion();
      const entry = createCacheEntry(newValue, newVersion, ttlMs ?? this.config.cache.defaultTtlMs);
      const serialized = JSON.stringify(serializeEntry(entry));

      const result = await this.redis.executeScript<[number, string]>(
        'compareAndSet',
        [versionKey, dataKey, lockKey],
        [expectedVersion, newVersion, serialized, entry.ttlMs]
      );

      const [success, response] = result;

      if (!success) {
        if (response === 'VERSION_MISMATCH') {
          const actualVersion = parseInt(response, 10);
          throw new VersionConflictError(key, expectedVersion, actualVersion);
        }
        throw new Error(`CAS failed: ${response}`);
      }

      this.degradedCache.set(key, entry);
      await this.invalidationBus.publishInvalidation(key, newVersion, 'update');
      this.metrics.invalidationPublishedTotal.inc({ type: 'update' });

      endSpan(span, undefined, { [CACHE_SPAN_ATTRIBUTES.VERSION]: newVersion });
      return { version: newVersion, success: true };
    } catch (error) {
      if (error instanceof RedisUnavailableError) {
        this.handleRedisError(error);
      }
      endSpan(span, error as Error);
      throw error;
    } finally {
      this.metrics.operationDurationMs.observe({ operation: 'compareAndSet' }, Date.now() - startTime);
    }
  }

  async delete(key: string, expectedVersion?: number): Promise<boolean> {
    const span = createSpan(this.tracing.tracer, 'cache.delete', {
      [CACHE_SPAN_ATTRIBUTES.KEY]: key,
      [CACHE_SPAN_ATTRIBUTES.OPERATION]: 'delete',
    });

    const startTime = Date.now();

    try {
      this.negativeCache.delete(key);
      this.degradedCache.delete(key);

      if (this.degradedMode) {
        endSpan(span);
        return true;
      }

      const versionKey = `${this.config.cache.versionKeyPrefix}${key}`;
      const dataKey = `${this.config.cache.dataKeyPrefix}${key}`;
      const lockKey = `${this.config.cache.versionKeyPrefix}lock:${key}`;

      const version = expectedVersion ?? -1;

      await this.redis.executeScript<[number]>(
        'deleteWithVersion',
        [versionKey, dataKey, lockKey],
        [version]
      );

      await this.invalidationBus.publishInvalidation(key, generateVersion(), 'delete');
      this.metrics.invalidationPublishedTotal.inc({ type: 'delete' });

      if (this.backendDeleter && expectedVersion !== undefined) {
        await this.backendDeleter(key, expectedVersion);
      }

      endSpan(span);
      return true;
    } catch (error) {
      if (error instanceof RedisUnavailableError) {
        this.handleRedisError(error);
      }
      endSpan(span, error as Error);
      throw error;
    } finally {
      this.metrics.operationDurationMs.observe({ operation: 'delete' }, Date.now() - startTime);
    }
  }

  private handleInvalidation(message: InvalidationMessage): void {
    const baseKey = extractBaseKey(message.key, this.config.cache.versionKeyPrefix);
    if (message.type === 'delete' || message.type === 'invalidate') {
      this.negativeCache.delete(baseKey);
      this.degradedCache.delete(baseKey);
    }
    this.emit('invalidation', message);
  }

  private handleRedisError(error: Error): void {
    this.circuitBreakerFailures++;
    this.logger.warn({ err: error, failures: this.circuitBreakerFailures }, 'Redis error recorded');

    if (this.circuitBreakerFailures >= this.config.degradation.circuitBreakerThreshold && !this.circuitBreakerOpen) {
      this.openCircuitBreaker();
    }
  }

  private openCircuitBreaker(): void {
    this.circuitBreakerOpen = true;
    this.degradedMode = true;
    this.metrics.degradedModeGauge.set(1);
    this.logger.warn('Circuit breaker opened, entering degraded mode');
    this.emit('degradedModeChange', true);

    this.circuitBreakerTimer = setTimeout(() => {
      this.circuitBreakerOpen = false;
      this.circuitBreakerFailures = 0;
      this.attemptRecovery();
    }, this.config.degradation.circuitBreakerTimeoutMs);
  }

  private async attemptRecovery(): Promise<void> {
    this.logger.info('Attempting Redis recovery');
    try {
      await this.redis.connect();
      const healthy = await this.redis.ping();
      if (healthy) {
        this.degradedMode = false;
        this.metrics.degradedModeGauge.set(0);
        this.logger.info('Redis recovery successful, exiting degraded mode');
        this.emit('degradedModeChange', false);
      } else {
        this.openCircuitBreaker();
      }
    } catch (error) {
      this.logger.warn({ err: error }, 'Redis recovery failed');
      this.openCircuitBreaker();
    }
  }

  private startHealthChecks(): void {
    this.healthCheckInterval = setInterval(async () => {
      if (this.degradedMode && !this.circuitBreakerOpen) {
        await this.attemptRecovery();
      } else if (!this.degradedMode) {
        try {
          const healthy = await this.redis.ping();
          if (!healthy) {
            this.handleRedisError(new Error('Health check ping failed'));
          } else {
            this.circuitBreakerFailures = 0;
          }
        } catch (error) {
          this.handleRedisError(error as Error);
        }
      }
    }, this.config.degradation.healthCheckIntervalMs);
    this.healthCheckInterval.unref();
  }

  isDegraded(): boolean {
    return this.degradedMode;
  }

  getMetrics(): CacheMetrics {
    return this.metrics;
  }

  getStats(): {
    degradedMode: boolean;
    circuitBreakerOpen: boolean;
    circuitBreakerFailures: number;
    coalescing: ReturnType<CoalescingMap<string, CacheEntry<T>>['getStats']>;
    negativeCache: ReturnType<NegativeCache['getStats']>;
    degradedCache: ReturnType<DegradedCache<T>['getStats']>;
    invalidationBus: ReturnType<InvalidationBus['getStats']>;
  } {
    return {
      degradedMode: this.degradedMode,
      circuitBreakerOpen: this.circuitBreakerOpen,
      circuitBreakerFailures: this.circuitBreakerFailures,
      coalescing: this.coalescingMap.getStats(),
      negativeCache: this.negativeCache.getStats(),
      degradedCache: this.degradedCache.getStats(),
      invalidationBus: this.invalidationBus.getStats(),
    };
  }
}
```

### src/index.ts

```typescript
export { CacheLayer, CacheLayerOptions, GetResult, SetResult } from './cache/CacheLayer';
export { CacheConfig, DEFAULT_CONFIG } from './config/CacheConfig';
export { CacheEntry, StoredCacheEntry, createCacheEntry, createNegativeEntry } from './cache/CacheEntry';
export { InvalidationBus, InvalidationMessage } from './cache/InvalidationBus';
export { CoalescingMap } from './cache/CoalescingMap';
export { NegativeCache } from './cache/NegativeCache';
export { DegradedCache } from './cache/DegradedCache';
export { RedisClient } from './redis/RedisClient';
export { CacheMetrics, createMetrics } from './telemetry/Metrics';
export { initializeTracing, TracingContext, CACHE_SPAN_ATTRIBUTES, HitState } from './telemetry/Tracing';
export { CacheError, RedisUnavailableError, VersionConflictError, CoalescingTimeoutError, InvalidationLagError } from './utils/errors';
export { generateVersion, parseVersionedKey, buildVersionedKey, isStale } from './utils/version';
```

---

## Tests

### tests/fixtures/test-helpers.ts

```typescript
import { CacheLayer, CacheConfig, DEFAULT_CONFIG } from '../src';
import { RedisClient } from '../src/redis/RedisClient';
import pino from 'pino';
import { vi } from 'vitest';

export function createTestConfig(overrides: Partial<CacheConfig> = {}): CacheConfig {
  return {
    ...DEFAULT_CONFIG,
    redis: {
      ...DEFAULT_CONFIG.redis,
      host: process.env.REDIS_HOST ?? 'localhost',
      port: parseInt(process.env.REDIS_PORT ?? '6379', 10),
      db: 15,
      connectionName: 'test-cache',
      lazyConnect: false,
    },
    cache: {
      ...DEFAULT_CONFIG.cache,
      defaultTtlMs: 5000,
      staleWhileRevalidateTtlMs: 1000,
      negativeCacheTtlMs: 1000,
    },
    tele

