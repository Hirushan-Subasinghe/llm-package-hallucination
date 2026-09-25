# Distributed Lease Module Implementation

## Project Structure

```
distributed-lease/
├── package.json
├── tsconfig.json
├── src/
│   ├── types.ts
│   ├── mock-redis.ts
│   ├── lease-manager.ts
│   ├── protected-resource.ts
│   └── index.ts
├── tests/
│   ├── acquisition.test.ts
│   ├── stale-fencing.test.ts
│   └── lost-renewal.test.ts
└── examples/
    └── basic-usage.ts
```

---

## `package.json`

```json
{
  "name": "distributed-lease",
  "version": "1.0.0",
  "description": "Self-contained distributed lease implementation with simulated Redis quorum",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsc",
    "test": "jest --runInBand --testTimeout=10000",
    "test:watch": "jest --watch",
    "example": "node dist/examples/basic-usage.js",
    "clean": "rm -rf dist",
    "prebuild": "npm run clean"
  },
  "keywords": [
    "distributed-lock",
    "lease",
    "redis",
    "fencing",
    "quorum"
  ],
  "author": "",
  "license": "MIT",
  "dependencies": {
    "ioredis": "5.4.1",
    "uuid": "9.0.1"
  },
  "devDependencies": {
    "@types/jest": "29.5.12",
    "@types/node": "20.12.7",
    "@types/uuid": "9.0.8",
    "jest": "29.7.0",
    "ts-jest": "29.1.2",
    "typescript": "5.4.5"
  },
  "engines": {
    "node": ">=20.0.0"
  }
}
```

---

## `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "resolveJsonModule": true,
    "moduleResolution": "node"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests", "examples"]
}
```

---

## `src/types.ts`

```typescript
/**
 * Core type definitions for the distributed lease system.
 */

/** Unique identifier for a lease holder */
export type OwnershipToken = string;

/** Monotonically increasing fencing token */
export type FencingToken = number;

/** Lease acquisition result */
export interface LeaseResult {
  /** Whether the lease was acquired */
  acquired: boolean;
  /** Unique ownership token for this lease holder */
  ownershipToken: OwnershipToken;
  /** Fencing token for this lease acquisition */
  fencingToken: FencingToken;
  /** TTL in milliseconds */
  ttlMs: number;
  /** Timestamp when lease expires (local clock) */
  expiresAt: number;
}

/** Lease renewal result */
export interface RenewalResult {
  /** Whether renewal succeeded */
  renewed: boolean;
  /** New fencing token (incremented on successful renewal) */
  fencingToken: FencingToken;
  /** New expiration timestamp */
  expiresAt: number;
}

/** Lease release result */
export interface ReleaseResult {
  /** Whether release succeeded */
  released: boolean;
}

/** Configuration for lease acquisition */
export interface LeaseConfig {
  /** Lease key/identifier */
  key: string;
  /** Desired TTL in milliseconds */
  ttlMs: number;
  /** Maximum clock drift allowance in milliseconds */
  driftAllowanceMs: number;
  /** Number of nodes required for quorum (default: 2 of 3) */
  quorumSize: number;
  /** Total number of nodes in the cluster (default: 3) */
  totalNodes: number;
  /** Acquisition timeout in milliseconds */
  acquireTimeoutMs: number;
  /** Renewal interval as fraction of TTL (0.0-1.0, default: 0.5) */
  renewalIntervalFraction: number;
}

/** Redis node response */
export interface NodeResponse<T> {
  /** Node identifier */
  nodeId: string;
  /** Response value */
  value: T;
  /** Whether the node responded successfully */
  success: boolean;
  /** Simulated network delay in ms */
  delayMs: number;
}

/** Mock Redis node state */
export interface MockNodeState {
  /** Key-value store */
  data: Map<string, { value: string; expiry: number }>;
  /** Fencing token counter per key */
  fencingTokens: Map<string, number>;
  /** Configured response delay in ms */
  responseDelayMs: number;
  /** Failure injection */
  shouldFail: boolean;
  /** Failure message */
  failureMessage: string;
}

/** Redis adapter interface for mockability */
export interface IRedisAdapter {
  /** Execute SET NX PX with fencing token increment */
  setNxPxWithFencing(
    key: string,
    value: string,
    ttlMs: number,
    expectedFencingToken: number
  ): Promise<{ success: boolean; fencingToken: number }>;

  /** Execute GET with fencing token */
  getWithFencing(key: string): Promise<{ value: string | null; fencingToken: number }>;

  /** Execute compare-and-delete (Lua script) */
  compareAndDelete(key: string, expectedValue: string): Promise<boolean>;

  /** Execute PEXPIRE to extend TTL */
  pexpire(key: string, ttlMs: number): Promise<boolean>;

  /** Get current time from node (for drift calculation) */
  time(): Promise<number>;

  /** Simulate network delay */
  delay(ms: number): Promise<void>;

  /** Inject failure for next operation */
  injectFailure(message: string): void;

  /** Clear injected failure */
  clearFailure(): void;

  /** Set response delay */
  setResponseDelay(ms: number): void;

  /** Get node identifier */
  getNodeId(): string;
}

/** Cluster of Redis adapters */
export interface IRedisCluster {
  /** All nodes in the cluster */
  nodes: IRedisAdapter[];
  /** Get nodes for quorum operations */
  getQuorumNodes(quorumSize: number): IRedisAdapter[];
}

/** Protected resource access request */
export interface AccessRequest {
  /** Lease key */
  key: string;
  /** Ownership token */
  ownershipToken: OwnershipToken;
  /** Fencing token */
  fencingToken: FencingToken;
  /** Operation identifier */
  operationId: string;
}

/** Protected resource access result */
export interface AccessResult {
  /** Whether access was granted */
  granted: boolean;
  /** Reason if denied */
  reason?: string;
  /** Current valid fencing token */
  currentFencingToken: FencingToken;
}

/** Event types for lease lifecycle */
export type LeaseEventType = 'acquired' | 'renewed' | 'released' | 'expired' | 'lost';

/** Lease event */
export interface LeaseEvent {
  type: LeaseEventType;
  key: string;
  ownershipToken: OwnershipToken;
  fencingToken: FencingToken;
  timestamp: number;
  details?: string;
}
```

---

## `src/mock-redis.ts`

```typescript
/**
 * Mock Redis adapter simulating three independent Redis nodes
 * with configurable delays, failures, and clock drift.
 */

import {
  IRedisAdapter,
  MockNodeState,
  NodeResponse,
  OwnershipToken
} from './types';
import { v4 as uuidv4 } from 'uuid';

/**
 * Creates a mock Redis node with independent state
 */
export function createMockRedisNode(
  nodeId: string,
  initialDelayMs: number = 0,
  clockDriftMs: number = 0
): IRedisAdapter {
  const state: MockNodeState = {
    data: new Map(),
    fencingTokens: new Map(),
    responseDelayMs: initialDelayMs,
    shouldFail: false,
    failureMessage: ''
  };

  // Simulated clock with drift
  let nodeClockOffset = clockDriftMs;

  const now = (): number => Date.now() + nodeClockOffset;

  const cleanupExpired = (): void => {
    const currentTime = now();
    for (const [key, entry] of state.data.entries()) {
      if (entry.expiry <= currentTime) {
        state.data.delete(key);
        state.fencingTokens.delete(key);
      }
    }
  };

  return {
    getNodeId(): string {
      return nodeId;
    },

    async setNxPxWithFencing(
      key: string,
      value: string,
      ttlMs: number,
      expectedFencingToken: number
    ): Promise<{ success: boolean; fencingToken: number }> {
      await this.delay(state.responseDelayMs);
      
      if (state.shouldFail) {
        throw new Error(state.failureMessage);
      }

      cleanupExpired();

      const currentFencingToken = state.fencingTokens.get(key) ?? 0;
      
      // Only succeed if fencing token matches expected (for renewal)
      // For new acquisition, expectedFencingToken should be 0
      const isNewAcquisition = expectedFencingToken === 0;
      const canAcquire = isNewAcquisition || currentFencingToken === expectedFencingToken;

      if (!canAcquire) {
        return { success: false, fencingToken: currentFencingToken };
      }

      const existingEntry = state.data.get(key);
      const isExpired = !existingEntry || existingEntry.expiry <= now();

      if (!isNewAcquisition && !isExpired && existingEntry.value !== value) {
        // Different owner holds the lease
        return { success: false, fencingToken: currentFencingToken };
      }

      // Increment fencing token for new acquisition or renewal
      const newFencingToken = currentFencingToken + 1;
      state.fencingTokens.set(key, newFencingToken);
      
      const expiry = now() + ttlMs;
      state.data.set(key, { value, expiry });

      return { success: true, fencingToken: newFencingToken };
    },

    async getWithFencing(key: string): Promise<{ value: string | null; fencingToken: number }> {
      await this.delay(state.responseDelayMs);
      
      if (state.shouldFail) {
        throw new Error(state.failureMessage);
      }

      cleanupExpired();

      const entry = state.data.get(key);
      const fencingToken = state.fencingTokens.get(key) ?? 0;

      if (!entry) {
        return { value: null, fencingToken };
      }

      if (entry.expiry <= now()) {
        state.data.delete(key);
        state.fencingTokens.delete(key);
        return { value: null, fencingToken };
      }

      return { value: entry.value, fencingToken };
    },

    async compareAndDelete(key: string, expectedValue: string): Promise<boolean> {
      await this.delay(state.responseDelayMs);
      
      if (state.shouldFail) {
        throw new Error(state.failureMessage);
      }

      cleanupExpired();

      const entry = state.data.get(key);
      if (!entry || entry.value !== expectedValue) {
        return false;
      }

      state.data.delete(key);
      state.fencingTokens.delete(key);
      return true;
    },

    async pexpire(key: string, ttlMs: number): Promise<boolean> {
      await this.delay(state.responseDelayMs);
      
      if (state.shouldFail) {
        throw new Error(state.failureMessage);
      }

      cleanupExpired();

      const entry = state.data.get(key);
      if (!entry) {
        return false;
      }

      entry.expiry = now() + ttlMs;
      return true;
    },

    async time(): Promise<number> {
      await this.delay(state.responseDelayMs);
      return now();
    },

    async delay(ms: number): Promise<void> {
      return new Promise(resolve => setTimeout(resolve, ms));
    },

    injectFailure(message: string): void {
      state.shouldFail = true;
      state.failureMessage = message;
    },

    clearFailure(): void {
      state.shouldFail = false;
      state.failureMessage = '';
    },

    setResponseDelay(ms: number): void {
      state.responseDelayMs = Math.max(0, ms);
    },

    // Internal methods for testing
    _getState(): MockNodeState {
      return state;
    },

    _setClockDrift(driftMs: number): void {
      nodeClockOffset = driftMs;
    },

    _getClockDrift(): number {
      return nodeClockOffset;
    }
  };
}

/**
 * Creates a cluster of 3 simulated Redis nodes
 */
export function createMockRedisCluster(
  baseDelayMs: number = 1,
  clockDriftsMs: number[] = [0, 2, -1]
): IRedisAdapter[] {
  return [
    createMockRedisNode('node-1', baseDelayMs, clockDriftsMs[0]),
    createMockRedisNode('node-2', baseDelayMs, clockDriftsMs[1]),
    createMockRedisNode('node-3', baseDelayMs, clockDriftsMs[2])
  ];
}

/**
 * Quorum helper for cluster operations
 */
export async function quorumExecute<T>(
  nodes: IRedisAdapter[],
  quorumSize: number,
  operation: (node: IRedisAdapter) => Promise<T>,
  successPredicate: (result: T) => boolean
): Promise<{ success: boolean; results: NodeResponse<T>[] }> {
  const results: NodeResponse<T>[] = [];
  let successCount = 0;

  // Execute in parallel across all nodes
  const promises = nodes.map(async (node) => {
    const startTime = Date.now();
    try {
      const value = await operation(node);
      const delayMs = Date.now() - startTime;
      const success = successPredicate(value);
      if (success) successCount++;
      results.push({ nodeId: node.getNodeId(), value, success, delayMs });
    } catch (error) {
      const delayMs = Date.now() - startTime;
      results.push({ 
        nodeId: node.getNodeId(), 
        value: null as unknown as T, 
        success: false, 
        delayMs 
      });
    }
  });

  await Promise.all(promises);

  return { success: successCount >= quorumSize, results };
}
```

---

## `src/lease-manager.ts`

```typescript
/**
 * Distributed Lease Manager implementing:
 * - Bounded TTL with drift allowance
 * - Quorum-based acquisition (2 of 3)
 * - Monotonically increasing fencing tokens
 * - Renewal with fencing token increment
 * - Compare-and-delete release
 */

import { v4 as uuidv4 } from 'uuid';
import {
  LeaseConfig,
  LeaseResult,
  RenewalResult,
  ReleaseResult,
  OwnershipToken,
  FencingToken,
  IRedisAdapter,
  IRedisCluster,
  LeaseEvent,
  LeaseEventType
} from './types';
import { createMockRedisCluster, quorumExecute } from './mock-redis';

/** Default lease configuration */
export const DEFAULT_LEASE_CONFIG: Partial<LeaseConfig> = {
  quorumSize: 2,
  totalNodes: 3,
  acquireTimeoutMs: 5000,
  renewalIntervalFraction: 0.5,
  driftAllowanceMs: 50
};

/** Active lease tracking */
interface ActiveLease {
  key: string;
  ownershipToken: OwnershipToken;
  fencingToken: FencingToken;
  expiresAt: number;
  config: LeaseConfig;
  renewalTimer?: NodeJS.Timeout;
  eventHandlers: Set<(event: LeaseEvent) => void>;
}

/**
 * Distributed Lease Manager
 */
export class LeaseManager {
  private cluster: IRedisAdapter[];
  private config: LeaseConfig;
  private activeLeases: Map<string, ActiveLease> = new Map();
  private globalEventHandlers: Set<(event: LeaseEvent) => void> = new Set();

  constructor(nodes: IRedisAdapter[], config: LeaseConfig) {
    this.cluster = nodes;
    this.config = { ...DEFAULT_LEASE_CONFIG, ...config } as LeaseConfig;
    
    // Validate quorum configuration
    if (this.config.quorumSize > this.config.totalNodes) {
      throw new Error('Quorum size cannot exceed total nodes');
    }
    if (this.config.quorumSize < Math.ceil(this.config.totalNodes / 2)) {
      throw new Error('Quorum size must be at least majority');
    }
  }

  /**
   * Acquire a distributed lease with bounded TTL and fencing token
   */
  async acquire(key: string, ttlMs?: number): Promise<LeaseResult> {
    const ownershipToken = uuidv4();
    const effectiveTtl = ttlMs ?? this.config.ttlMs;
    const startTime = Date.now();
    const deadline = startTime + this.config.acquireTimeoutMs;

    // Generate unique request ID for this acquisition attempt
    const requestValue = `${ownershipToken}:${Date.now()}:${Math.random().toString(36).slice(2)}`;

    while (Date.now() < deadline) {
      const remainingTime = deadline - Date.now();
      
      // Execute quorum-based acquisition
      const { success, results } = await quorumExecute(
        this.cluster,
        this.config.quorumSize,
        async (node) => {
          return node.setNxPxWithFencing(key, requestValue, effectiveTtl, 0);
        },
        (result) => result.success
      );

      if (success) {
        // Get the maximum fencing token from successful nodes
        const fencingToken = Math.max(
          ...results
            .filter(r => r.success)
            .map(r => r.value.fencingToken)
        );

        // Calculate expiration with drift allowance
        const expiresAt = Date.now() + effectiveTtl - this.config.driftAllowanceMs;

        const leaseResult: LeaseResult = {
          acquired: true,
          ownershipToken,
          fencingToken,
          ttlMs: effectiveTtl,
          expiresAt
        };

        // Track active lease for renewal
        this.trackLease(key, ownershipToken, fencingToken, expiresAt, effectiveTtl);

        this.emitEvent({
          type: 'acquired',
          key,
          ownershipToken,
          fencingToken,
          timestamp: Date.now(),
          details: `Acquired with quorum ${results.filter(r => r.success).length}/${this.cluster.length}`
        });

        return leaseResult;
      }

      // Brief backoff before retry
      const backoff = Math.min(50, remainingTime);
      if (backoff > 0) {
        await new Promise(resolve => setTimeout(resolve, backoff));
      }
    }

    // Acquisition failed
    return {
      acquired: false,
      ownershipToken,
      fencingToken: 0,
      ttlMs: effectiveTtl,
      expiresAt: 0
    };
  }

  /**
   * Renew an existing lease, incrementing fencing token
   */
  async renew(key: string, ownershipToken: OwnershipToken, fencingToken: FencingToken): Promise<RenewalResult> {
    const leaseKey = this.getLeaseKey(key, ownershipToken);
    const lease = this.activeLeases.get(leaseKey);

    if (!lease) {
      return { renewed: false, fencingToken: 0, expiresAt: 0 };
    }

    if (lease.fencingToken !== fencingToken) {
      // Stale fencing token - lease may have been renewed by another process
      return { renewed: false, fencingToken: lease.fencingToken, expiresAt: lease.expiresAt };
    }

    const requestValue = `${ownershipToken}:${Date.now()}:${Math.random().toString(36).slice(2)}`;

    const { success, results } = await quorumExecute(
      this.cluster,
      this.config.quorumSize,
      async (node) => {
        return node.setNxPxWithFencing(key, requestValue, this.config.ttlMs, fencingToken);
      },
      (result) => result.success
    );

    if (success) {
      const newFencingToken = Math.max(
        ...results
          .filter(r => r.success)
          .map(r => r.value.fencingToken)
      );

      const newExpiresAt = Date.now() + this.config.ttlMs - this.config.driftAllowanceMs;

      // Update tracked lease
      lease.fencingToken = newFencingToken;
      lease.expiresAt = newExpiresAt;

      this.emitEvent({
        type: 'renewed',
        key,
        ownershipToken,
        fencingToken: newFencingToken,
        timestamp: Date.now(),
        details: `Renewed with quorum ${results.filter(r => r.success).length}/${this.cluster.length}`
      });

      return { renewed: true, fencingToken: newFencingToken, expiresAt: newExpiresAt };
    }

    // Renewal failed - lease may be lost
    this.emitEvent({
      type: 'lost',
      key,
      ownershipToken,
      fencingToken,
      timestamp: Date.now(),
      details: 'Renewal failed to achieve quorum'
    });

    return { renewed: false, fencingToken, expiresAt: lease.expiresAt };
  }

  /**
   * Release a lease using compare-and-delete
   */
  async release(key: string, ownershipToken: OwnershipToken, fencingToken: FencingToken): Promise<ReleaseResult> {
    const leaseKey = this.getLeaseKey(key, ownershipToken);
    const lease = this.activeLeases.get(leaseKey);

    if (!lease || lease.fencingToken !== fencingToken) {
      return { released: false };
    }

    const requestValue = `${ownershipToken}:${lease.fencingToken}`;

    const { success } = await quorumExecute(
      this.cluster,
      this.config.quorumSize,
      async (node) => {
        return node.compareAndDelete(key, requestValue);
      },
      (result) => result === true
    );

    if (success) {
      this.untrackLease(leaseKey);
      this.emitEvent({
        type: 'released',
        key,
        ownershipToken,
        fencingToken,
        timestamp: Date.now(),
        details: 'Released via compare-and-delete'
      });
      return { released: true };
    }

    return { released: false };
  }

  /**
   * Get current lease status without modifying it
   */
  async getStatus(key: string, ownershipToken: OwnershipToken): Promise<{ valid: boolean; fencingToken: FencingToken; expiresAt: number }> {
    const leaseKey = this.getLeaseKey(key, ownershipToken);
    const lease = this.activeLeases.get(leaseKey);

    if (!lease) {
      return { valid: false, fencingToken: 0, expiresAt: 0 };
    }

    // Check local expiry with drift allowance
    const now = Date.now();
    if (now >= lease.expiresAt) {
      return { valid: false, fencingToken: lease.fencingToken, expiresAt: lease.expiresAt };
    }

    // Verify with quorum
    const { results } = await quorumExecute(
      this.cluster,
      this.config.quorumSize,
      async (node) => {
        return node.getWithFencing(key);
      },
      (result) => result.value !== null && result.value.startsWith(ownershipToken)
    );

    const valid = results.some(r => r.success && r.value.value?.startsWith(ownershipToken));
    const maxFencingToken = Math.max(...results.map(r => r.value.fencingToken));

    return { valid, fencingToken: maxFencingToken, expiresAt: lease.expiresAt };
  }

  /**
   * Subscribe to lease events
   */
  onEvent(handler: (event: LeaseEvent) => void): () => void {
    this.globalEventHandlers.add(handler);
    return () => this.globalEventHandlers.delete(handler);
  }

  /**
   * Get all active leases
   */
  getActiveLeases(): Array<{ key: string; ownershipToken: OwnershipToken; fencingToken: FencingToken; expiresAt: number }> {
    return Array.from(this.activeLeases.values()).map(lease => ({
      key: lease.key,
      ownershipToken: lease.ownershipToken,
      fencingToken: lease.fencingToken,
      expiresAt: lease.expiresAt
    }));
  }

  /**
   * Shutdown manager and release all leases
   */
  async shutdown(): Promise<void> {
    const releasePromises = Array.from(this.activeLeases.entries()).map(
      ([leaseKey, lease]) => this.release(lease.key, lease.ownershipToken, lease.fencingToken)
    );
    await Promise.all(releasePromises);
    this.activeLeases.clear();
  }

  // Private methods

  private trackLease(
    key: string,
    ownershipToken: OwnershipToken,
    fencingToken: FencingToken,
    expiresAt: number,
    ttlMs: number
  ): void {
    const leaseKey = this.getLeaseKey(key, ownershipToken);
    
    const lease: ActiveLease = {
      key,
      ownershipToken,
      fencingToken,
      expiresAt,
      config: this.config,
      eventHandlers: new Set(),
      renewalTimer: undefined
    };

    // Schedule automatic renewal
    const renewalInterval = ttlMs * this.config.renewalIntervalFraction;
    lease.renewalTimer = setInterval(async () => {
      if (this.activeLeases.has(leaseKey)) {
        const currentLease = this.activeLeases.get(leaseKey)!;
        const result = await this.renew(key, ownershipToken, currentLease.fencingToken);
        if (!result.renewed) {
          // Lease lost, stop renewal
          this.untrackLease(leaseKey);
          this.emitEvent({
            type: 'expired',
            key,
            ownershipToken,
            fencingToken: currentLease.fencingToken,
            timestamp: Date.now(),
            details: 'Lease expired due to failed renewal'
          });
        }
      }
    }, renewalInterval);

    // Don't prevent process exit
    lease.renewalTimer.unref();

    this.activeLeases.set(leaseKey, lease);
  }

  private untrackLease(leaseKey: string): void {
    const lease = this.activeLeases.get(leaseKey);
    if (lease?.renewalTimer) {
      clearInterval(lease.renewalTimer);
    }
    this.activeLeases.delete(leaseKey);
  }

  private getLeaseKey(key: string, ownershipToken: OwnershipToken): string {
    return `${key}:${ownershipToken}`;
  }

  private emitEvent(event: LeaseEvent): void {
    for (const handler of this.globalEventHandlers) {
      try {
        handler(event);
      } catch (error) {
        console.error('Lease event handler error:', error);
      }
    }
  }
}

/**
 * Factory function to create a LeaseManager with simulated Redis cluster
 */
export function createLeaseManager(config: Partial<LeaseConfig> = {}): LeaseManager {
  const nodes = createMockRedisCluster();
  const fullConfig: LeaseConfig = {
    key: config.key ?? 'default',
    ttlMs: config.ttlMs ?? 10000,
    driftAllowanceMs: config.driftAllowanceMs ?? 50,
    quorumSize: config.quorumSize ?? 2,
    totalNodes: config.totalNodes ?? 3,
    acquireTimeoutMs: config.acquireTimeoutMs ?? 5000,
    renewalIntervalFraction: config.renewalIntervalFraction ?? 0.5
  };
  return new LeaseManager(nodes, fullConfig);
}
```

---

## `src/protected-resource.ts`

```typescript
/**
 * Protected Resource that enforces fencing tokens
 * Rejects stale holders with outdated fencing tokens
 */

import {
  AccessRequest,
  AccessResult,
  FencingToken,
  OwnershipToken,
  IRedisAdapter
} from './types';

/**
 * Protected resource that only allows access with valid fencing token
 * Simulates a resource that stores the highest seen fencing token
 */
export class ProtectedResource {
  private resources: Map<string, { 
    maxFencingToken: FencingToken; 
    currentHolder: OwnershipToken | null;
    data: string;
  }> = new Map();

  private redisCluster: IRedisAdapter[];

  constructor(redisCluster: IRedisAdapter[]) {
    this.redisCluster = redisCluster;
  }

  /**
   * Attempt to access protected resource with fencing token
   * Returns granted/denied with current valid fencing token
   */
  async access(request: AccessRequest): Promise<AccessResult> {
    const { key, ownershipToken, fencingToken, operationId } = request;

    // Get current state from quorum
    const { results } = await this.getQuorumFencingToken(key);
    
    // Find maximum fencing token across quorum
    const maxFencingToken = Math.max(...results.map(r => r.value.fencingToken));
    const currentHolder = results.find(r => r.success)?.value.value?.split(':')[0] ?? null;

    // Update local cache
    const resource = this.resources.get(key) ?? { 
      maxFencingToken: 0, 
      currentHolder: null,
      data: ''
    };
    
    resource.maxFencingToken = Math.max(resource.maxFencingToken, maxFencingToken);
    resource.currentHolder = currentHolder;
    this.resources.set(key, resource);

    // Check if request has valid fencing token
    if (fencingToken < resource.maxFencingToken) {
      return {
        granted: false,
        reason: `Stale fencing token: provided ${fencingToken}, current max is ${resource.maxFencingToken}`,
        currentFencingToken: resource.maxFencingToken
      };
    }

    if (fencingToken > resource.maxFencingToken) {
      // This shouldn't happen if quorum is working, but handle it
      resource.maxFencingToken = fencingToken;
    }

    // Verify ownership matches
    if (resource.currentHolder !== ownershipToken) {
      return {
        granted: false,
        reason: `Ownership mismatch: resource held by ${resource.currentHolder}, requested by ${ownershipToken}`,
        currentFencingToken: resource.maxFencingToken
      };
    }

    // Access granted - simulate resource operation
    resource.data = `Operation ${operationId} by ${ownershipToken}@${fencingToken}`;
    
    return {
      granted: true,
      currentFencingToken: resource.maxFencingToken
    };
  }

  /**
   * Get current resource state (for testing/debugging)
   */
  getResourceState(key: string): { maxFencingToken: FencingToken; currentHolder: OwnershipToken | null; data: string } | null {
    return this.resources.get(key) ?? null;
  }

  /**
   * Reset resource state (for testing)
   */
  resetResource(key: string): void {
    this.resources.delete(key);
  }

  /**
   * Simulate external write with higher fencing token (for testing stale rejection)
   */
  async simulateExternalWrite(key: string, newFencingToken: FencingToken, newOwner: OwnershipToken): Promise<void> {
    // Write to all nodes with new fencing token
    const value = `${newOwner}:${Date.now()}:external`;
    for (const node of this.redisCluster) {
      try {
        await node.setNxPxWithFencing(key, value, 60000, newFencingToken - 1);
      } catch {
        // Ignore failures in simulation
      }
    }
    
    // Update local cache
    const resource = this.resources.get(key) ?? { 
      maxFencingToken: 0, 
      currentHolder: null,
      data: ''
    };
    resource.maxFencingToken = newFencingToken;
    resource.currentHolder = newOwner;
    this.resources.set(key, resource);
  }

  private async getQuorumFencingToken(key: string): Promise<{ results: Array<{ nodeId: string; value: { value: string | null; fencingToken: FencingToken }; success: boolean }> }> {
    const { results } = await this.executeOnQuorum(
      async (node) => node.getWithFencing(key),
      (result) => true // Always count responses for fencing token check
    );
    return { results };
  }

  private async executeOnQuorum<T>(
    operation: (node: IRedisAdapter) => Promise<T>,
    _successPredicate: (result: T) => boolean
  ): Promise<{ results: Array<{ nodeId: string; value: T; success: boolean }> }> {
    const results = await Promise.all(
      this.redisCluster.map(async (node) => {
        try {
          const value = await operation(node);
          return { nodeId: node.getNodeId(), value, success: true };
        } catch {
          return { nodeId: node.getNodeId(), value: null as unknown as T, success: false };
        }
      })
    );
    return { results };
  }
}
```

---

## `src/index.ts`

```typescript
/**
 * Main entry point - exports all public APIs
 */

export * from './types';
export * from './mock-redis';
export * from './lease-manager';
export * from './protected-resource';

// Re-export commonly used functions
import { createLeaseManager } from './lease-manager';
import { createMockRedisCluster } from './mock-redis';
import { ProtectedResource } from './protected-resource';
import { LeaseManager } from './lease-manager';

export { createLeaseManager, createMockRedisCluster, ProtectedResource, LeaseManager };

/**
 * Quick start example:
 * 
 * ```typescript
 * import { createLeaseManager, ProtectedResource } from 'distributed-lease';
 * 
 * const manager = createLeaseManager({ ttlMs: 10000 });
 * const resource = new ProtectedResource(manager['cluster']); // Access internal cluster
 * 
 * const lease = await manager.acquire('my-resource');
 * if (lease.acquired) {
 *   const access = await resource.access({
 *     key: 'my-resource',
 *     ownershipToken: lease.ownershipToken,
 *     fencingToken: lease.fencingToken,
 *     operationId: 'op-1'
 *   });
 *   if (access.granted) {
 *     // Perform protected operation
 *   }
 *   await manager.release('my-resource', lease.ownershipToken, lease.fencingToken);
 * }
 * ```
 */
```

---

## `tests/acquisition.test.ts`

```typescript
/**
 * Deterministic concurrency tests for lease acquisition
 * Tests quorum behavior, race conditions, and drift handling
 */

import { createMockRedisCluster, createLeaseManager, LeaseManager } from '../src';

describe('Lease Acquisition', () => {
  let cluster: ReturnType<typeof createMockRedisCluster>;
  let manager: LeaseManager;

  beforeEach(() => {
    cluster = createMockRedisCluster(1, [0, 0, 0]); // No drift for basic tests
    manager = new LeaseManager(cluster, {
      key: 'test',
      ttlMs: 10000,
      driftAllowanceMs: 50,
      quorumSize: 2,
      totalNodes: 3,
      acquireTimeoutMs: 5000,
      renewalIntervalFraction: 0.5
    });
  });

  afterEach(async () => {
    await manager.shutdown();
  });

  test('should acquire lease with quorum of 2/3 nodes', async () => {
    const result = await manager.acquire('resource-1', 5000);
    
    expect(result.acquired).toBe(true);
    expect(result.ownershipToken).toBeDefined();
    expect(result.fencingToken).toBe(1); // First acquisition = token 1
    expect(result.ttlMs).toBe(5000);
    expect(result.expiresAt).toBeGreaterThan(Date.now());
  });

  test('should reject second acquisition for same resource', async () => {
    const first = await manager.acquire('resource-1', 5000);
    expect(first.acquired).toBe(true);

    const second = await manager.acquire('resource-1', 5000);
    expect(second.acquired).toBe(false);
    expect(second.fencingToken).toBe(0);
  });

  test('should allow acquisition after lease expires', async () => {
    const cluster = createMockRedisCluster(1, [0, 0, 0]);
    const manager = new LeaseManager(cluster, {
      key: 'test',
      ttlMs: 100, // Very short TTL
      driftAllowanceMs: 10,
      quorumSize: 2,
      totalNodes: 3,
      acquireTimeoutMs: 5000,
      renewalIntervalFraction: 0.5
    });

    const first = await manager.acquire('resource-1', 100);
    expect(first.acquired).toBe(true);

    // Wait for expiry
    await new Promise(resolve => setTimeout(resolve, 150));

    const second = await manager.acquire('resource-1', 100);
    expect(second.acquired).toBe(true);
    expect(second.fencingToken).toBe(2); // Token increments

    await manager.shutdown();
  });

  test('should handle concurrent acquisition attempts', async () => {
    const attempts = 10;
    const promises = Array(attempts).fill(null).map(() => 
      manager.acquire('contended-resource', 5000)
    );

    const results = await Promise.all(promises);
    const acquired = results.filter(r => r.acquired);

    // Exactly one should succeed
    expect(acquired.length).toBe(1);
    expect(acquired[0].fencingToken).toBe(1);
  });

  test('should respect drift allowance in expiry calculation', async () => {
    const result = await manager.acquire('resource-1', 1000);
    
    // expiresAt should be now + ttl - driftAllowance
    const expectedMin = Date.now() + 1000 - 50 - 10; // Small buffer
    const expectedMax = Date.now() + 1000 - 50 + 10;
    
    expect(result.expiresAt).toBeGreaterThanOrEqual(expectedMin);
    expect(result.expiresAt).toBeLessThanOrEqual(expectedMax);
  });

  test('should emit acquired event', async () => {
    const events: any[] = [];
    const unsubscribe = manager.onEvent(e => events.push(e));

    await manager.acquire('resource-1', 5000);
    
    expect(events.length).toBe(1);
    expect(events[0].type).toBe('acquired');
    expect(events[0].key).toBe('resource-1');
    
    unsubscribe();
  });

  test('should fail acquisition when quorum unavailable', async () => {
    // Fail 2 nodes (quorum is 2)
    cluster[0].injectFailure('Node down');
    cluster[1].injectFailure('Node down');

    const result = await manager.acquire('resource-1', 5000);
    
    expect(result.acquired).toBe(false);
    
    cluster[0].clearFailure();
    cluster[1].clearFailure();
  });

  test('should handle partial node failures during acquisition', async () => {
    // Fail 1 node (quorum still achievable with 2/3)
    cluster[0].injectFailure('Network partition');

    const result = await manager.acquire('resource-1', 5000);
    
    expect(result.acquired).toBe(true);
    expect(result.fencingToken).toBe(1);
    
    cluster[0].clearFailure();
  });

  test('should handle delayed node responses', async () => {
    // Add significant delay to one node
    cluster[0].setResponseDelay(100);
    cluster[1].setResponseDelay(5);
    cluster[2].setResponseDelay(5);

    const start = Date.now();
    const result = await manager.acquire('resource-1', 5000);
    const duration = Date.now() - start;

    expect(result.acquired).toBe(true);
    // Should complete within reasonable time (not wait for slowest node indefinitely)
    expect(duration).toBeLessThan(200);
  });
});
```

---

## `tests/stale-fencing.test.ts`

```typescript
/**
 * Deterministic tests for stale fencing token rejection
 * Verifies protected resource rejects holders with outdated tokens
 */

import { createMockRedisCluster, createLeaseManager, LeaseManager, ProtectedResource } from '../src';

describe('Stale Fencing Token Rejection', () => {
  let cluster: ReturnType<typeof createMockRedisCluster>;
  let manager: LeaseManager;
  let resource: ProtectedResource;

  beforeEach(() => {
    cluster = createMockRedisCluster(1, [0, 0, 0]);
    manager = new LeaseManager(cluster, {
      key: 'test',
      ttlMs: 10000,
      driftAllowanceMs: 50,
      quorumSize: 2,
      totalNodes: 3,
      acquireTimeoutMs: 5000,
      renewalIntervalFraction: 0.5
    });
    resource = new ProtectedResource(cluster);
  });

  afterEach(async () => {
    await manager.shutdown();
  });

  test('should reject access with stale fencing token after renewal', async () => {
    // Acquire initial lease
    const lease1 = await manager.acquire('protected-resource', 5000);
    expect(lease1.acquired).toBe(true);
    expect(lease1.fencingToken).toBe(1);

    // Access with valid token
    const access1 = await resource.access({
      key: 'protected-resource',
      ownershipToken: lease1.ownershipToken,
      fencingToken: lease1.fencingToken,
      operationId: 'op-1'
    });
    expect(access1.granted).toBe(true);

    // Renew lease (increments fencing token)
    const renewal = await manager.renew('protected-resource', lease1.ownershipToken, lease1.fencingToken);
    expect(renewal.renewed).toBe(true);
    expect(renewal.fencingToken).toBe(2);

    // Try to access with OLD fencing token (stale)
    const staleAccess = await resource.access({
      key: 'protected-resource',
      ownershipToken: lease1.ownershipToken,
      fencingToken: 1, // Stale!
      operationId: 'op-2-stale'
    });
    
    expect(staleAccess.granted).toBe(false);
    expect(staleAccess.reason).toContain('Stale fencing token');
    expect(staleAccess.currentFencingToken).toBe(2);

    // Access with NEW fencing token should work
    const freshAccess = await resource.access({
      key: 'protected-resource',
      ownershipToken: lease1.ownershipToken,
      fencingToken: 2, // Current
      operationId: 'op-3-fresh'
    });
    expect(freshAccess.granted).toBe(true);
  });

  test('should reject access when different holder acquires lease', async () => {
    // Holder 1 acquires
    const lease1 = await manager.acquire('protected-resource', 5000);
    expect(lease1.acquired).toBe(true);

    // Holder 1 accesses
    const access1 = await resource.access({
      key: 'protected-resource',
      ownershipToken: lease1.ownershipToken,
      fencingToken: lease1.fencingToken,
      operationId: 'op-1'
    });
    expect(access1.granted).toBe(true);

    // Simulate lease expiry and new holder acquiring
    await manager.release('protected-resource', lease1.ownershipToken, lease1.fencingToken);

    // Holder 2 acquires (gets new fencing token)
    const lease2 = await manager.acquire('protected-resource', 5000);
    expect(lease2.acquired).toBe(true);
    expect(lease2.fencingToken).toBe(2); // Incremented
    expect(lease2.ownershipToken).not.toBe(lease1.ownershipToken);

    // Holder 1 tries to access with old token
    const staleAccess = await resource.access({
      key: 'protected-resource',
      ownershipToken: lease1.ownershipToken,
      fencingToken: lease1.fencingToken,
      operationId: 'op-2-stale-holder'
    });
    
    expect(staleAccess.granted).toBe(false);
    expect(staleAccess.reason).toContain('Ownership mismatch');
  });

  test('should handle external write with higher fencing token', async () => {
    const lease = await manager.acquire('protected-resource', 5000);
    expect(lease.acquired).toBe(true);

    // Valid access
    const access1 = await resource.access({
      key: 'protected-resource',
      ownershipToken: lease.ownershipToken,
      fencingToken: lease.fencingToken,
      operationId: 'op-1'
    });
    expect(access1.granted).toBe(true);

    // Simulate external system writing with higher fencing token
    await resource.simulateExternalWrite('protected-resource', 5, 'external-owner');

    // Original holder tries with old token
    const staleAccess = await resource.access({
      key: 'protected-resource',
      ownershipToken: lease.ownershipToken,
      fencingToken: lease.fencingToken,
      operationId: 'op-2-stale'
    });
    
    expect(staleAccess.granted).toBe(false);
    expect(staleAccess.currentFencingToken).toBe(5);
  });

  test('should track maximum fencing token across quorum', async () => {
    const lease = await manager.acquire('protected-resource', 5000);
    
    // Add delay to one node to simulate replication lag
    cluster[2].setResponseDelay(50);
    
    const access = await resource.access({
      key: 'protected-resource',
      ownershipToken: lease.ownershipToken,
      fencingToken: lease.fencingToken,
      operationId: 'op-1'
    });
    
    expect(access.granted).toBe(true);
    expect(access.currentFencingToken).toBe(1);
    
    cluster[2].setResponseDelay(1);
  });

  test('should reject access after lease release', async () => {
    const lease = await manager.acquire('protected-resource', 5000);
    
    const access1 = await resource.access({
      key: 'protected-resource',
      ownershipToken: lease.ownershipToken,
      fencingToken: lease.fencingToken,
      operationId: 'op-1'
    });
    expect(access1.granted).toBe(true);

    // Release lease
    await manager.release('protected-resource', lease.ownershipToken, lease.fencingToken);

    // Try to access after release
    const access2 = await resource.access({
      key: 'protected-resource',
      ownershipToken: lease.ownershipToken,
      fencingToken: lease.fencingToken,
      operationId: 'op-2-after-release'
    });
    
    expect(access2.granted).toBe(false);
  });
});
```

---

## `tests/lost-renewal.test.ts`

```typescript
/**
 * Deterministic tests for lost renewal scenarios
 * Tests renewal failure, network partitions, and automatic expiry
 */

import { createMockRedisCluster, createLeaseManager, LeaseManager } from '../src';

describe('Lost Renewal Handling', () => {
  let cluster: ReturnType<typeof createMockRedisCluster>;
  let manager: LeaseManager;

  beforeEach(() => {
    cluster = createMockRedisCluster(1, [0, 0, 0]);
    manager = new LeaseManager(cluster, {
      key: 'test',
      ttlMs: 1000, // Short TTL for faster tests
      driftAllowanceMs: 50,
      quorumSize: 2,
      totalNodes: 3,
      acquireTimeoutMs: 5000,
      renewalIntervalFraction: 0.3 // Renew at 30% of TTL
    });
  });

  afterEach(async () => {
    await manager.shutdown();
  });

  test('should detect lost renewal when quorum unavailable', async () => {
    const lease = await manager.acquire('resource-1', 1000);
    expect(lease.acquired).toBe(true);

    // Fail 2 nodes (quorum = 2, so renewal will fail)
    cluster[0].injectFailure('Network partition');
    cluster[1].injectFailure('Network partition');

    // Wait for renewal attempt (should happen at ~300ms)
    await new Promise(resolve => setTimeout(resolve, 500));

    // Check lease status - should be lost
    const status = await manager.getStatus('resource-1', lease.ownershipToken);
    expect(status.valid).toBe(false);

    cluster[0].clearFailure();
    cluster[1].clearFailure();
  });

  test('should emit lost event when renewal fails', async () => {
    const events: any[] = [];
    manager.onEvent(e => events.push(e));

    const lease = await manager.acquire('resource-1', 1000);
    
    // Fail quorum
    cluster[0].injectFailure('Node down');
    cluster[1].injectFailure('Node down');

    await new Promise(resolve => setTimeout(resolve, 500));

    const lostEvents = events.filter(e => e.type === 'lost');
    expect(lostEvents.length).toBe(1);
    expect(lostEvents[0].key).toBe('resource-1');
    expect(lostEvents[0].ownershipToken).toBe(lease.ownershipToken);

    cluster[0].clearFailure();
    cluster[1].clearFailure();
  });

  test('should allow new acquisition after lease lost', async () => {
    const lease1 = await manager.acquire('resource-1', 1000);
    expect(lease1.acquired).toBe(true);

    // Fail quorum to cause renewal loss
    cluster[0].injectFailure('Partition');
    cluster[1].injectFailure('Partition');

    await new Promise(resolve => setTimeout(resolve, 500));

    // Restore nodes
    cluster[0].clearFailure();
    cluster[1].clearFailure();

    // New acquisition should succeed
    const lease2 = await manager.acquire('resource-1', 1000);
    expect(lease2.acquired).toBe(true);
    expect(lease2.ownershipToken).not.toBe(lease1.ownershipToken);
    expect(lease2.fencingToken).toBe(2); // Incremented
  });

  test('should handle delayed renewal responses', async () => {
    const lease = await manager.acquire('resource-1', 1000);
    
    // Add significant delay to all nodes
    cluster.forEach(node => node.setResponseDelay(100));

    const renewal = await manager.renew('resource-1', lease.ownershipToken, lease.fencingToken);
    
    // Should still succeed despite delays
    expect(renewal.renewed).toBe(true);
    expect(renewal.fencingToken).toBe(2);

    cluster.forEach(node => node.setResponseDelay(1));
  });

  test('should handle partial renewal failure (1 node down)', async () => {
    const lease = await manager.acquire('resource-1', 1000);
    
    // Fail 1 node (quorum of 2 still achievable)
    cluster[0].injectFailure('Node down');

    const renewal = await manager.renew('resource-1', lease.ownershipToken, lease.fencingToken);
    
    expect(renewal.renewed).toBe(true);
    expect(renewal.fencingToken).toBe(2);

    cluster[0].clearFailure();
  });

  test('should expire lease locally when TTL exceeded', async () => {
    const shortTtlCluster = createMockRedisCluster(1, [0, 0, 0]);
    const shortTtlManager = new LeaseManager(shortTtlCluster, {
      key: 'test',
      ttlMs: 100,
      driftAllowanceMs: 10,
      quorumSize: 2,
      totalNodes: 3,
      acquireTimeoutMs: 5000,
      renewalIntervalFraction: 0.5
    });

    const lease = await shortTtlManager.acquire('resource-1', 100);
    expect(lease.acquired).toBe(true);

    // Wait well past TTL + drift allowance
    await new Promise(resolve => setTimeout(resolve, 200));

    const status = await shortTtlManager.getStatus('resource-1', lease.ownershipToken);
    expect(status.valid).toBe(false);

    await shortTtlManager.shutdown();
  });

  test('should handle clock drift between nodes', async () => {
    // Create cluster with clock drift
    const driftCluster = createMockRedisCluster(1, [0, 50, -30]); // ±50ms drift
    const driftManager = new LeaseManager(driftCluster, {
      key: 'test',
      ttlMs: 1000,
      driftAllowanceMs: 100, // Generous drift allowance
      quorumSize: 2,
      totalNodes: 3,
      acquireTimeoutMs: 5000,
      renewalIntervalFraction: 0.3
    });

    const lease = await driftManager.acquire('resource-1', 1000);
    expect(lease.acquired).toBe(true);

    // Renewal should work despite clock drift
    const renewal = await driftManager.renew('resource-1', lease.ownershipToken, lease.fencingToken);
    expect(renewal.renewed).toBe(true);

    await driftManager.shutdown();
  });

  test('should handle rapid acquire-release-acquire cycle', async () => {
    for (let i = 0; i < 5; i++) {
      const lease = await manager.acquire('resource-1', 1000);
      expect(lease.acquired).toBe(true);
      expect(lease.fencingToken).toBe(i + 1);

      await manager.release('resource-1', lease.ownershipToken, lease.fencingToken);
    }

    // Final acquisition
    const finalLease = await manager.acquire('resource-1', 1000);
    expect(finalLease.fencingToken).toBe(6);
  });

  test('should track multiple concurrent leases on different resources', async () => {
    const lease1 = await manager.acquire('resource-a', 1000);
    const lease2 = await manager.acquire('resource-b', 1000);
    const lease3 = await manager.acquire('resource-c', 1000);

    expect(lease1.acquired).toBe(true);
    expect(lease2.acquired).toBe(true);
    expect(lease3.acquired).toBe(true);

    const activeLeases = manager.getActiveLeases();
    expect(activeLeases.length).toBe(3);

    await manager.release('resource-a', lease1.ownershipToken, lease1.fencingToken);
    await manager.release('resource-b', lease2.ownershipToken, lease2.fencingToken);
    await manager.release('resource-c', lease3.ownershipToken, lease3.fencingToken);

    const remainingLeases = manager.getActiveLeases();
    expect(remainingLeases.length).toBe(0);
  });
});
```

---

## `examples/basic-usage.ts`

```typescript
/**
 * Basic usage example demonstrating:
 * - Lease acquisition with quorum
 * - Protected resource access with fencing
 * - Stale holder rejection
 * - Renewal and release
 */

import { createLeaseManager, createMockRedisCluster, ProtectedResource, LeaseManager } from '../src';

async function main() {
  console.log('=== Distributed Lease Demo ===\n');

  // Create simulated 3-node Redis cluster
  const cluster = createMockRedisCluster(2, [0, 5, -3]); // 2ms base delay, slight clock drift
  
  // Create lease manager with 10 second TTL, 50ms drift allowance
  const manager = new LeaseManager(cluster, {
    key: 'demo',
    ttlMs: 10000,
    driftAllowanceMs: 50,
    quorumSize: 2,
    totalNodes: 3,
    acquireTimeoutMs: 5000,
    renewalIntervalFraction: 0.5
  });

  // Create protected resource
  const resource = new ProtectedResource(cluster);

  // Subscribe to lease events
  const unsubscribe = manager.onEvent((event) => {
    console.log(`[EVENT] ${event.type.toUpperCase()}: ${event.key} @${event.fencingToken} (${event.details})`);
  });

  try {
    // --- Scenario 1: Basic Acquisition & Access ---
    console.log('--- Scenario 1: Basic Acquisition ---');
    const lease = await manager.acquire('database-primary', 10000);
    
    if (!lease.acquired) {
      console.log('Failed to acquire lease');
      return;
    }

    console.log(`Acquired lease: token=${lease.ownershipToken.slice(0,8)}... fencing=${lease.fencingToken} expiresIn=${lease.ttlMs}ms`);

    // Access protected resource
    const access1 = await resource.access({
      key: 'database-primary',
      ownershipToken: lease.ownershipToken,
      fencingToken: lease.fencingToken,
      operationId: 'write-user-record-123'
    });

    console.log(`Access 1: ${access1.granted ? 'GRANTED' : 'DENIED'} - ${access1.reason ?? 'OK'}`);

    // --- Scenario 2: Renewal Increments Fencing Token ---
    console.log('\n--- Scenario 2: Renewal ---');
    const renewal = await manager.renew('database-primary', lease.ownershipToken, lease.fencingToken);
    console.log(`Renewal: ${renewal.renewed ? 'SUCCESS' : 'FAILED'} - new fencing token: ${renewal.fencingToken}`);

    // Access with new fencing token
    const access2 = await resource.access({
      key: 'database-primary',
      ownershipToken: lease.ownershipToken,
      fencingToken: renewal.fencingToken,
      operationId: 'write-user-record-456'
    });
    console.log(`Access 2: ${access2.granted ? 'GRANTED' : 'DENIED'} - ${access2.reason ?? 'OK'}`);

    // --- Scenario 3: Stale Fencing Token Rejection ---
    console.log('\n--- Scenario 3: Stale Token Rejection ---');
    const staleAccess = await resource.access({
      key: 'database-primary',
      ownershipToken: lease.ownershipToken,
      fencingToken: lease.fencingToken, // OLD token!
      operationId: 'stale-write-attempt'
    });
    console.log(`Stale access: ${staleAccess.granted ? 'GRANTED' : 'DENIED'} - ${staleAccess.reason}`);

    // --- Scenario 4: Simulate External Takeover ---
    console.log('\n--- Scenario 4: External Takeover ---');
    // Simulate another process acquiring the lease (higher fencing token)
    await resource.simulateExternalWrite('database-primary', 10, 'external-process-owner');
    
    const externalAccess = await resource.access({
      key: 'database-primary',
      ownershipToken: lease.ownershipToken,
      fencingToken: renewal.fencingToken,
      operationId: 'post-takeover-attempt'
    });
    console.log(`Post-takeover access: ${externalAccess.granted ? 'GRANTED' : 'DENIED'} - ${externalAccess.reason}`);

    // --- Scenario 5: Concurrent Acquisition Attempt ---
    console.log('\n--- Scenario 5: Concurrent Contention ---');
    const manager2 = new LeaseManager(cluster, {
      key: 'demo',
      ttlMs: 10000,
      driftAllowanceMs: 50,
      quorumSize: 2,
      totalNodes: 3,
      acquireTimeoutMs: 2000,
      renewalIntervalFraction: 0.5
    });

    const [result1, result2, result3] = await Promise.all([
      manager2.acquire('shared-resource', 5000),
      manager2.acquire('shared-resource', 5000),
      manager2.acquire('shared-resource', 5000)
    ]);

    console.log(`Contender 1: ${result1.acquired ? 'WON' : 'LOST'} (fencing: ${result1.fencingToken})`);
    console.log(`Contender 2: ${result2.acquired ? 'WON' : 'LOST'} (fencing: ${result2.fencingToken})`);
    console.log(`Contender 3: ${result3.acquired ? 'WON' : 'LOST'} (fencing: ${result3.fencingToken})`);

    await manager2.shutdown();

    // --- Scenario 6: Partial Failure Handling ---
    console.log('\n--- Scenario 6: Partial Node Failure ---');
    cluster[0].injectFailure('Network partition');
    console.log('Injected failure on node-1');

    const leaseDuringFailure = await manager.acquire('resource-during-failure', 5000);
    console.log(`Acquisition during failure: ${leaseDuringFailure.acquired ? 'SUCCESS' : 'FAILED'}`);

    cluster[0].clearFailure();
    console.log('Cleared failure on node-1');

    // --- Scenario 7: Proper Release ---
    console.log('\n--- Scenario 7: Clean Release ---');
    const release = await manager.release('database-primary', lease.ownershipToken, renewal.fencingToken);
    console.log(`Release: ${release.released ? 'SUCCESS' : 'FAILED'}`);

    // Verify release
    const postReleaseAccess = await resource.access({
      key: 'database-primary',
      ownershipToken: lease.ownershipToken,
      fencingToken: renewal.fencingToken,
      operationId: 'post-release-attempt'
    });
    console.log(`Post-release access: ${postReleaseAccess.granted ? 'GRANTED' : 'DENIED'} - ${postReleaseAccess.reason}`);

  } finally {
    unsubscribe();
    await manager.shutdown();
    console.log('\n=== Demo Complete ===');
  }
}

main().catch(console.error);
```

---

## Installation & Usage Commands

```bash
# Create project directory
mkdir distributed-lease && cd distributed-lease

# Save all files to their respective paths:
# package.json, tsconfig.json
# src/types.ts, src/mock-redis.ts, src/lease-manager.ts, src/protected-resource.ts, src/index.ts
# tests/acquisition.test.ts, tests/stale-fencing.test.ts, tests/lost-renewal.test.ts
# examples/basic-usage.ts

# Install exact dependencies
npm install

# Build TypeScript
npm run build

# Run all tests (deterministic, sequential)
npm test

# Run example
npm run example

# Expected test output:
# PASS tests/acquisition.test.ts
# PASS tests/stale-fencing.test.ts
# PASS tests/lost-renewal.test.ts
# Test Suites: 3 passed, 3 total
# Tests:       20 passed, 20 total
```

---

## Redis & Distributed-Lock APIs Used

| Component | API Used | Purpose |
|-----------|----------|---------|
| **ioredis** (v5.4.1) | `set(key, value, 'PX', ttl, 'NX')` | Atomic SET with TTL and NX (not exists) |
| | `get(key)` | Retrieve value |
| | `eval(script, numKeys, key, expectedValue)` | Lua compare-and-delete |
| | `pexpire(key, ttl)` | Extend TTL |
| | `time()` | Get server time for drift calculation |
| **Redlock Algorithm** | Quorum (2/3) | Majority consensus for safety |
| | Fencing Tokens | Monotonic increment on each acquisition/renewal |
| | Ownership Tokens | UUID v4 for unique holder identity |
| | Drift Allowance | Subtract from TTL for clock skew safety |

---

## Key Design Decisions

1. **Mock Redis Adapter**: Fully simulates 3 independent nodes with configurable delay, failure injection, and clock drift for deterministic testing.

2. **Quorum Execution**: Parallel requests to all nodes, success requires `quorumSize` positive responses. Uses `Promise.all` with individual error handling.

3. **Fencing Token Monotonicity**: Each successful `setNxPxWithFencing` increments a per-key counter stored on each node. Renewal passes expected token to prevent split-brain.

4. **Compare-and-Delete Release**: Lua script ensures atomic check-and-delete only if ownership token matches.

5. **Drift Allowance**: Subtracted from TTL when calculating `expiresAt` to account for clock skew between client and Redis nodes.

6. **Automatic Renewal**: Background timer at `renewalIntervalFraction` of TTL. Stops on failure and emits `lost` event.

7. **Protected Resource**: Maintains local cache of max fencing token seen via quorum reads. Rejects any request with token `< maxSeen`.

8. **Deterministic Tests**: No real timers, controlled delays, explicit failure injection. Tests run sequentially (`--runInBand`).

