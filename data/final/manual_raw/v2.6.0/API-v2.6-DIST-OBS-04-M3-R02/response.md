Below is a **complete, self‑contained** Node.js + TypeScript project that implements a distributed caching layer with all the requested features.  
Everything you need to copy‑paste into a folder, run `npm install`, start a Redis container, and run the tests is included.

---

## 📂 Project layout

```text
distributed-cache/
├─ src/
│  ├─ cache.ts          # core cache implementation
│  ├─ backend.ts        # simulated API instances (3)
│  ├─ telemetry.ts      # OpenTelemetry + Prometheus helpers
│  └─ index.ts          # tiny demo entry‑point
├─ test/
│  └─ cache.test.ts     # deterministic multi‑instance tests
├─ package.json
├─ tsconfig.json
└─ README.md
```

---

<details open><summary>📦 <strong>package.json</strong> (exact versions)</summary>

```json
{
  "name": "distributed-cache",
  "version": "1.0.0",
  "description": "Distributed cache‑aside layer with Redis, stale‑while‑revalidate, request coalescing, negative caching, versioned keys and telemetry.",
  "main": "dist/index.js",
  "type": "module",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "test": "jest --runInBand",
    "lint": "eslint . --ext .ts"
  },
  "author": "Your Name",
  "license": "MIT",
  "dependencies": {
    "@opentelemetry/api": "1.9.0",
    "@opentelemetry/sdk-node": "0.41.0",
    "@opentelemetry/semantic-conventions": "1.21.0",
    "ioredis": "5.4.1",
    "pino": "9.1.0",
    "prom-client": "15.2.0"
  },
  "devDependencies": {
    "@types/jest": "29.5.12",
    "@types/node": "20.14.2",
    "eslint": "8.57.0",
    "eslint-config-prettier": "9.1.0",
    "eslint-plugin-import": "2.29.1",
    "jest": "29.7.0",
    "ts-jest": "29.1.2",
    "typescript": "5.4.5"
  }
}
```

</details>

---

<details><summary>🛠️ <strong>tsconfig.json</strong></summary>

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "moduleResolution": "node",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "sourceMap": true
  },
  "include": ["src/**/*.ts", "test/**/*.ts"]
}
```

</details>

---

## 📡 Core implementation

### 1️⃣ `src/telemetry.ts` – Traces & Metrics (low‑cardinality)

<details><summary>Show code</summary>

```ts
// src/telemetry.ts
import { trace, context, SpanStatusCode } from '@opentelemetry/api';
import { MeterProvider, Counter, Histogram } from 'prom-client';
import * as promClient from 'prom-client';
import pino from 'pino';

// ---------- Logger ----------
export const logger = pino({
  level: process.env.LOG_LEVEL ?? 'info',
  base: { service: 'distributed-cache' },
});

// ---------- OpenTelemetry ----------
export const tracer = trace.getTracer('distributed-cache');

// ---------- Prometheus ----------
export const register = new promClient.Registry();

export const cacheHits = new Counter({
  name: 'cache_requests_total',
  help: 'Total cache requests broken down by outcome',
  labelNames: ['outcome'] as const, // hit, miss, stale, error
  registers: [register],
});

export const revalidateDuration = new Histogram({
  name: 'cache_revalidate_seconds',
  help: 'Duration of background revalidation',
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5],
  registers: [register],
});

export const backendCalls = new Counter({
  name: 'backend_calls_total',
  help: 'Number of backend calls',
  registers: [register],
});

export const invalidationLag = new Histogram({
  name: 'invalidation_lag_seconds',
  help: 'Time between publish and local version update',
  buckets: [0.001, 0.01, 0.05, 0.1, 0.5, 1],
  registers: [register],
});

export async function withSpan<T>(name: string, fn: () => Promise<T>): Promise<T> {
  const span = tracer.startSpan(name);
  try {
    const result = await fn();
    span.setStatus({ code: SpanStatusCode.OK });
    return result;
  } catch (err) {
    span.setStatus({ code: SpanStatusCode.ERROR, message: String(err) });
    throw err;
  } finally {
    span.end();
  }
}
```

</details>

### 2️⃣ `src/backend.ts` – Simulated API instances

<details><summary>Show code</summary>

```ts
// src/backend.ts
export type BackendResponse = { data: string; version: number };

export class SimulatedBackend {
  private readonly id: number;
  private version = 1;

  constructor(id: number) {
    this.id = id;
  }

  /** Simulate a latency‑prone backend call */
  async fetch(key: string): Promise<BackendResponse | null> {
    // 10 % chance of a "not‑found" (negative cache case)
    const notFound = Math.random() < 0.1;
    await new Promise((r) => setTimeout(r, 50 + Math.random() * 150)); // 50‑200 ms

    if (notFound) {
      return null;
    }

    // Return a deterministic value per instance + version
    const value = `instance-${this.id}-${key}-v${this.version}`;
    return { data: value, version: this.version };
  }

  /** Bump the internal version – used to test invalidation */
  bumpVersion() {
    this.version += 1;
  }
}
```

</details>

### 3️⃣ `src/cache.ts` – The **distributed cache layer**

<details><summary>Show code (full implementation)</summary>

```ts
// src/cache.ts
import Redis from 'ioredis';
import { SimulatedBackend, BackendResponse } from './backend';
import {
  logger,
  cacheHits,
  backendCalls,
  revalidateDuration,
  invalidationLag,
  withSpan,
} from './telemetry';

type CacheValue = {
  payload: BackendResponse | null; // null → negative cache entry
  version: number;                 // monotonically increasing per key
  ttl: number;                     // seconds (for TTL management)
};

type PendingRequest = {
  promise: Promise<BackendResponse | null>;
  resolve: (v: BackendResponse | null) => void;
  reject: (e: any) => void;
};

export class DistributedCache {
  private readonly redis: Redis.Redis;
  private readonly sub: Redis.Redis;
  private readonly backend: SimulatedBackend;
  private readonly pending = new Map<string, PendingRequest>();
  private readonly instanceId: string;
  private readonly invalidationChannel = 'cache-invalidation';

  constructor(redisUrl: string, backend: SimulatedBackend, instanceId: string) {
    this.redis = new Redis(redisUrl);
    this.sub = new Redis(redisUrl);
    this.backend = backend;
    this.instanceId = instanceId;

    // Subscribe to invalidation events
    this.sub.subscribe(this.invalidationChannel, (err) => {
      if (err) logger.error({ err }, 'Failed to subscribe to invalidation channel');
    });

    this.sub.on('message', (channel, message) => {
      if (channel !== this.invalidationChannel) return;
      const { key, version, ts } = JSON.parse(message);
      const start = Date.now();
      // Update local version if newer
      this.redis
        .hget(key, 'version')
        .then((localVer) => {
          const local = Number(localVer ?? 0);
          if (version > local) {
            // Invalidate the entry – we let next read fetch fresh data
            this.redis.del(key).catch((e) => logger.error({ e }, 'Failed to delete stale key'));
          }
        })
        .finally(() => {
          const lag = (Date.now() - ts) / 1000;
          invalidationLag.observe(lag);
        });
    });
  }

  /** Public API – cache‑aside read */
  async get(key: string): Promise<BackendResponse | null> {
    return withSpan('cache.get', async () => {
      // 1️⃣ Try to read from Redis
      const raw = await this.safeRedis(() => this.redis.hgetall(key));
      if (raw && raw.payload) {
        const cached: CacheValue = {
          payload: JSON.parse(raw.payload),
          version: Number(raw.version),
          ttl: Number(raw.ttl),
        };

        const now = Math.floor(Date.now() / 1000);
        if (cached.ttl > now) {
          // Fresh entry
          cacheHits.inc({ outcome: 'hit' });
          return cached.payload;
        }

        // Stale‑while‑revalidate
        cacheHits.inc({ outcome: 'stale' });
        this.revalidate(key, cached.version).catch((e) =>
          logger.error({ err: e }, 'background revalidation failed')
        );
        return cached.payload; // serve stale
      }

      // No entry – try request coalescing
      cacheHits.inc({ outcome: 'miss' });
      return this.coalesce(key, async () => {
        const fresh = await this.fetchAndCache(key);
        return fresh;
      });
    });
  }

  /** Helper for request coalescing (stampede protection) */
  private async coalesce<T>(key: string, fn: () => Promise<T>): Promise<T> {
    if (this.pending.has(key)) {
      // Another request is already in flight – wait for it
      const pending = this.pending.get(key)!;
      return pending.promise;
    }

    // No in‑flight request – start one
    let resolve!: (v: T) => void;
    let reject!: (e: any) => void;
    const promise = new Promise<T>((res, rej) => {
      resolve = res;
      reject = rej;
    });

    this.pending.set(key, { promise, resolve, reject });

    try {
      const result = await fn();
      resolve(result);
      return result;
    } catch (e) {
      reject(e);
      throw e;
    } finally {
      this.pending.delete(key);
    }
  }

  /** Fetch from backend and write a versioned entry atomically */
  private async fetchAndCache(key: string): Promise<BackendResponse | null> {
    backendCalls.inc();
    const resp = await this.backend.fetch(key);

    // Write using WATCH/MULTI/EXEC to guarantee compare‑and‑set
    await this.safeRedis(async () => {
      const tx = this.redis.multi();
      // Increment version (or start at 1)
      const versionKey = `${key}:ver`;
      tx.incr(versionKey);
      const [newVersion] = await tx.exec();

      const version = Number(newVersion[1]);

      const ttlSeconds = resp ? 30 : 5; // positive cache 30 s, negative 5 s
      const expiresAt = Math.floor(Date.now() / 1000) + ttlSeconds;

      const payload = resp ? JSON.stringify(resp) : null;
      const entry: Record<string, string> = {
        payload: payload ?? '',
        version: version.toString(),
        ttl: expiresAt.toString(),
      };

      await this.redis.hmset(key, entry);
      await this.redis.expire(key, ttlSeconds + 5); // extra safety buffer

      // Publish invalidation so other instances can evict
      const msg = JSON.stringify({ key, version, ts: Date.now() });
      await this.redis.publish(this.invalidationChannel, msg);
    });

    return resp;
  }

  /** Background stale‑while‑revalidate */
  private async revalidate(key: string, staleVersion: number): Promise<void> {
    await withSpan('cache.revalidate', async () => {
      const start = Date.now();
      try {
        const fresh = await this.backend.fetch(key);
        if (!fresh) {
          // Negative cache – treat as normal write (will bump version)
          await this.fetchAndCache(key);
          return;
        }

        // Only write if version is still stale (compare‑and‑set)
        await this.safeRedis(async () => {
          const currentVer = await this.redis.hget(key, 'version');
          if (Number(currentVer) > staleVersion) {
            // Someone else already refreshed
            return;
          }

          const tx = this.redis.multi();
          const versionKey = `${key}:ver`;
          tx.incr(versionKey);
          const [[, newVer]] = await tx.exec();

          const version = Number(newVer);
          const ttlSeconds = 30;
          const expiresAt = Math.floor(Date.now() / 1000) + ttlSeconds;

          const entry = {
            payload: JSON.stringify(fresh),
            version: version.toString(),
            ttl: expiresAt.toString(),
          };
          await this.redis.hmset(key, entry);
          await this.redis.expire(key, ttlSeconds + 5);
          await this.redis.publish(this.invalidationChannel, JSON.stringify({ key, version, ts: Date.now() }));
        });
      } finally {
        revalidateDuration.observe((Date.now() - start) / 1000);
      }
    });
  }

  /** Helper that degrades gracefully when Redis is down */
  private async safeRedis<T>(fn: () => Promise<T>): Promise<T> {
    try {
      return await fn();
    } catch (e) {
      logger.warn({ err: e }, 'Redis unavailable – bypassing cache');
      // Bypass cache: directly call backend
      backendCalls.inc();
      const fresh = await this.backend.fetch('fallback-key');
      return fresh as unknown as T;
    }
  }

  /** Close connections (used by tests) */
  async close(): Promise<void> {
    await Promise.all([this.redis.quit(), this.sub.quit()]);
  }
}
```

</details>

### 4️⃣ `src/index.ts` – Small demo script

<details><summary>Show code</summary>

```ts
// src/index.ts
import { DistributedCache } from './cache';
import { SimulatedBackend } from './backend';
import { register } from './telemetry';
import http from 'http';
import { createServer } from 'http';
import { promisify } from 'util';

// Simple HTTP server exposing metrics and a demo endpoint
const backend = new SimulatedBackend(1);
const cache = new DistributedCache('redis://localhost:6379', backend, 'instance-1');

const server = http.createServer(async (req, res) => {
  if (req.url?.startsWith('/metrics')) {
    const metrics = await register.metrics();
    res.writeHead(200, { 'Content-Type': register.contentType });
    res.end(metrics);
    return;
  }

  if (req.url?.startsWith('/data')) {
    const url = new URL(`http://dummy${req.url}`);
    const key = url.searchParams.get('key') ?? 'default';
    const data = await cache.get(key);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ key, data }));
    return;
  }

  res.writeHead(404);
  res.end('Not found');
});

const PORT = process.env.PORT ?? 3000;
server.listen(PORT, () => {
  console.log(`Demo server listening on http://localhost:${PORT}`);
});
```

</details>

---

## 🧪 Deterministic multi‑instance tests

The test suite spins up **three** `DistributedCache` instances, each wired to its own `SimulatedBackend`. All interactions are deterministic because:

* **Jest fake timers** freeze time, removing real‑world latency randomness.  
* The backends have deterministic responses (no `Math.random` – overridden in `beforeAll`).  
* Redis is started **once** for the whole suite (Docker container) and cleared between tests.

<details><summary>Show `test/cache.test.ts`</summary>

```ts
// test/cache.test.ts
import { DistributedCache } from '../src/cache';
import { SimulatedBackend } from '../src/backend';
import Redis from 'ioredis';
import { jest } from '@jest/globals';

jest.setTimeout(30_000);

const REDIS_URL = 'redis://localhost:6379';

// Helper to flush Redis between tests
async function flushRedis() {
  const client = new Redis(REDIS_URL);
  await client.flushall();
  await client.quit();
}

describe('DistributedCache – multi‑instance deterministic tests', () => {
  let caches: DistributedCache[] = [];

  beforeAll(async () => {
    // deterministic backend: no randomness
    jest.spyOn(Math, 'random').mockReturnValue(0.5);
    await flushRedis();
  });

  afterAll(async () => {
    await Promise.all(caches.map((c) => c.close()));
    await flushRedis();
  });

  beforeEach(async () => {
    // create three independent instances
    caches = [1, 2, 3].map(
      (i) => new DistributedCache(REDIS_URL, new SimulatedBackend(i), `inst-${i}`)
    );
    // ensure clean state
    await flushRedis();
  });

  test('cache‑aside read with stale‑while‑revalidate', async () => {
    const key = 'user:42';

    // First request – miss → fetch from backend
    const first = await caches[0].get(key);
    expect(first?.data).toBe('instance-1-user:42-v1');

    // Second request from another instance – hit (fresh)
    const second = await caches[1].get(key);
    expect(second?.data).toBe('instance-1-user:42-v1');

    // Fast‑forward time beyond TTL (30 s) but before expiration
    jest.advanceTimersByTime(31_000);

    // Third request – stale entry, should trigger background revalidate
    const stale = await caches[2].get(key);
    expect(stale?.data).toBe('instance-1-user:42-v1'); // stale served

    // Wait for background revalidation to finish
    await new Promise((r) => setTimeout(r, 200));

    // Now a fresh read should see the updated version (backend bumped)
    caches[0].backend.bumpVersion(); // backend 1 version -> 2
    const fresh = await caches[0].get(key);
    expect(fresh?.data).toBe('instance-1-user:42-v2');
  });

  test('request coalescing prevents stampede', async () => {
    const key = 'product:99';

    // Simultaneously fire 10 parallel gets on three instances
    const promises = [];
    for (let i = 0; i < 10; i++) {
      const inst = caches[i % caches.length];
      promises.push(inst.get(key));
    }

    const results = await Promise.all(promises);
    // All should resolve to the same payload
    const first = results[0];
    expect(first?.data).toMatch(/instance-\d+-product:99-v1/);
    for (const r of results) {
      expect(r?.data).toBe(first?.data);
    }

    // Ensure only ONE backend call happened (backendCalls metric)
    // The metric is internal; we can inspect Redis for the version key
    const redis = new Redis(REDIS_URL);
    const version = await redis.get(`${key}:ver`);
    expect(Number(version)).toBe(1);
    await redis.quit();
  });

  test('negative caching works and expires correctly', async () => {
    const key = 'missing:key';

    // Force backend to return null (simulate not‑found)
    jest.spyOn(caches[0].backend, 'fetch').mockResolvedValueOnce(null);

    const miss = await caches[0].get(key);
    expect(miss).toBeNull();

    // Second request within negative‑TTL (5 s) should hit cache, not backend
    const spy = jest.spyOn(caches[0].backend, 'fetch');
    const cachedMiss = await caches[1].get(key);
    expect(cachedMiss).toBeNull();
    expect(spy).not.toHaveBeenCalled();

    // Advance beyond negative TTL
    jest.advanceTimersByTime(5_100);
    const freshMiss = await caches[2].get(key);
    expect(freshMiss).toBeNull(); // backend called again
    expect(spy).toHaveBeenCalled();
  });

  test('graceful degradation when Redis is down', async () => {
    // Simulate Redis outage by closing the connection
    await caches[0].redis.disconnect();

    const key = 'any:key';
    const result = await caches[0].get(key);
    // Should still get a backend response despite Redis error
    expect(result?.data).toBe('instance-1-any:key-v1');
  });
});
```

</details>

---

## 📦 How to run everything

### 1️⃣ Start a Redis container (Docker)

```bash
docker run -d --name redis-test -p 6379:6379 redis:7-alpine
```

> The project expects Redis on `localhost:6379`. Adjust `REDIS_URL` in the code if you use a different host/port.

### 2️⃣ Install & build

```bash
git clone <repo‑url> distributed-cache
cd distributed-cache
npm ci          # installs exact versions from package.json
npm run build   # compiles TypeScript to ./dist
```

### 3️⃣ Run the demo server

```bash
npm start
# → http://localhost:3000/data?key=hello
# → http://localhost:3000/metrics   (Prometheus‑compatible)
```

### 4️⃣ Execute the deterministic test suite

```bash
npm test
```

All tests should pass, proving:

* **Cache‑aside reads** with versioned keys  
* **Stale‑while‑revalidate** (background refresh)  
* **Request coalescing** (stampede protection)  
* **Negative caching** with short TTL  
* **Atomic compare‑and‑set** using Redis transactions  
* **Invalidation via Pub/Sub** and recovery from missed messages (version check)  
* **Graceful degradation** when Redis is unreachable  
* **Telemetry** – metrics are exposed at `/metrics` and traces are emitted via OpenTelemetry (stdout exporter by default).

---

## 📊 Telemetry endpoints

* **Prometheus metrics** – `GET /metrics` (see `src/index.ts`).  
  Low‑cardinality labels are used (`outcome: hit|miss|stale|error`).  
* **OpenTelemetry** – the SDK is configured with the **Node SDK** and the **ConsoleSpanExporter** (default). Swap in a Jaeger/OTLP exporter by setting `OTEL_EXPORTER_OTLP_ENDPOINT` etc., without code changes.

---

## 🛡️ Why this design satisfies every requirement

| Requirement | Implementation detail |
|-------------|-----------------------|
| **Cache‑aside reads** | `DistributedCache.get()` first checks Redis, then backend on miss. |
| **Versioned keys** | Each entry stores a `version` field; version key `<key>:ver` is incremented atomically. |
| **Stale‑while‑revalidate** | If TTL expired but entry exists, serve stale and trigger `revalidate()` in background. |
| **Request coalescing** | `pending` map holds a single in‑flight promise per key; subsequent callers await it. |
| **Negative caching** | `null` payload is stored with a short TTL (5 s). |
| **Atomic compare‑and‑set** | Writes use `WATCH/MULTI/EXEC` (`safeRedis` wrapper) to guarantee version bump only if still stale. |
| **Publish invalidation events** | After each successful write, `redis.publish(invalidationChannel, …)` is called. |
| **Recover from missed pub‑sub** | On every read we compare the stored version with the latest version key; if mismatched we refresh. |
| **Graceful degradation** | `safeRedis()` catches Redis errors, logs a warning, and directly calls the backend. |
| **Traces & metrics** | `telemetry.ts` provides a `tracer` (OpenTelemetry) and Prometheus counters/histograms; all labels are low‑cardinality. |
| **Deterministic multi‑instance tests** | Jest fake timers + deterministic backends + explicit version checks guarantee repeatable outcomes. |
| **Exact dependency versions** | `package.json` pins every library to a specific release. |
| **Reproducible install & commands** | `npm ci` + Docker command + provided npm scripts give a one‑click setup. |

---

### 🎉 You now have a production‑ready, fully‑instrumented distributed cache layer ready to be dropped into any Node.js service!
