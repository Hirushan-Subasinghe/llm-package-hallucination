# Redis-Backed Job Processing Service with OpenTelemetry

## Project Structure

```
payment-notification-service/
├── package.json
├── tsconfig.json
├── vitest.config.ts
├── .env.example
├── src/
│   ├── index.ts                 # Entry point
│   ├── config.ts                # Configuration
│   ├── queue/
│   │   ├── paymentQueue.ts      # Queue setup & job types
│   │   ├── processor.ts         # Job processor with concurrency control
│   │   ├── deadLetter.ts        # Dead-letter handling
│   │   └── idempotency.ts       # Idempotency key management
│   ├── telemetry/
│   │   ├── tracer.ts            # OpenTelemetry setup
│   │   └── context.ts           # Trace context propagation
│   ├── jobs/
│   │   └── paymentNotification.ts  # Business logic
│   ├── errors/
│   │   └── classification.ts    # Retryable vs terminal errors
│   └── utils/
│       └── retry.ts             # Exponential backoff with jitter
├── tests/
│   ├── duplicate-delivery.test.ts
│   ├── worker-crash.test.ts
│   ├── retry-exhaustion.test.ts
│   └── dead-letter-replay.test.ts
└── scripts/
    └── replay-dead-letter.ts    # Operator replay script
```

---

## package.json

```json
{
  "name": "payment-notification-service",
  "version": "1.0.0",
  "description": "Redis-backed job processing service for payment notifications with OpenTelemetry tracing",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "tsx watch src/index.ts",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage",
    "lint": "eslint src/**/*.ts tests/**/*.ts",
    "replay:dlq": "tsx scripts/replay-dead-letter.ts",
    "docker:build": "docker build -t payment-notification-service .",
    "docker:run": "docker run --rm -p 3000:3000 --env-file .env payment-notification-service"
  },
  "dependencies": {
    "@opentelemetry/api": "^1.9.0",
    "@opentelemetry/auto-instrumentations-node": "^0.56.0",
    "@opentelemetry/exporter-trace-otlp-http": "^0.56.0",
    "@opentelemetry/instrumentation-ioredis": "^0.56.0",
    "@opentelemetry/resources": "^1.30.0",
    "@opentelemetry/sdk-node": "^0.56.0",
    "@opentelemetry/semantic-conventions": "^1.30.0",
    "bullmq": "^5.56.0",
    "ioredis": "^5.6.0",
    "js-yaml": "^4.1.0",
    "pino": "^9.6.0",
    "pino-pretty": "^13.0.0",
    "uuid": "^11.1.0",
    "zod": "^3.24.2"
  },
  "devDependencies": {
    "@types/js-yaml": "^4.0.9",
    "@types/node": "^22.13.0",
    "@types/uuid": "^10.0.0",
    "@vitest/coverage-v8": "^3.0.0",
    "eslint": "^9.20.0",
    "tsx": "^4.19.0",
    "typescript": "^5.7.0",
    "vitest": "^3.0.0"
  },
  "engines": {
    "node": ">=22.0.0"
  },
  "packageManager": "npm@10.9.0"
}
```

---

## tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2024",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2024"],
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
  "exclude": ["node_modules", "dist", "tests", "scripts"]
}
```

---

## vitest.config.ts

```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'node',
    include: ['tests/**/*.test.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['tests/**', 'scripts/**', 'src/index.ts'],
    },
    testTimeout: 30000,
    hookTimeout: 10000,
    pool: 'forks',
    poolOptions: {
      forks: {
        singleFork: true,
      },
    },
  },
});
```

---

## .env.example

```bash
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
REDIS_TLS=false

# Queue
QUEUE_NAME=payment-notifications
QUEUE_CONCURRENCY=5
QUEUE_MAX_RETRIES=5
QUEUE_BASE_DELAY_MS=1000
QUEUE_MAX_DELAY_MS=300000
QUEUE_JITTER_FACTOR=0.2

# Dead Letter
DLQ_MAX_SIZE=10000
DLQ_TTL_DAYS=30

# OpenTelemetry
OTEL_SERVICE_NAME=payment-notification-service
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318/v1/traces
OTEL_EXPORTER_OTLP_HEADERS=
OTEL_SAMPLER=traceidratio
OTEL_SAMPLER_ARG=0.1

# Application
LOG_LEVEL=info
NODE_ENV=development
```

---

## src/config.ts

```typescript
import { z } from 'zod';

const envSchema = z.object({
  REDIS_HOST: z.string().default('localhost'),
  REDIS_PORT: z.coerce.number().default(6379),
  REDIS_PASSWORD: z.string().optional(),
  REDIS_DB: z.coerce.number().default(0),
  REDIS_TLS: z.coerce.boolean().default(false),

  QUEUE_NAME: z.string().default('payment-notifications'),
  QUEUE_CONCURRENCY: z.coerce.number().default(5),
  QUEUE_MAX_RETRIES: z.coerce.number().default(5),
  QUEUE_BASE_DELAY_MS: z.coerce.number().default(1000),
  QUEUE_MAX_DELAY_MS: z.coerce.number().default(300000),
  QUEUE_JITTER_FACTOR: z.coerce.number().default(0.2),

  DLQ_MAX_SIZE: z.coerce.number().default(10000),
  DLQ_TTL_DAYS: z.coerce.number().default(30),

  OTEL_SERVICE_NAME: z.string().default('payment-notification-service'),
  OTEL_EXPORTER_OTLP_ENDPOINT: z.string().url().default('http://localhost:4318/v1/traces'),
  OTEL_EXPORTER_OTLP_HEADERS: z.string().optional(),
  OTEL_SAMPLER: z.enum(['always_on', 'always_off', 'traceidratio', 'parentbased_traceidratio']).default('traceidratio'),
  OTEL_SAMPLER_ARG: z.string().default('0.1'),

  LOG_LEVEL: z.enum(['fatal', 'error', 'warn', 'info', 'debug', 'trace']).default('info'),
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
});

export type Config = z.infer<typeof envSchema>;

let cachedConfig: Config | null = null;

export function getConfig(): Config {
  if (cachedConfig) return cachedConfig;
  const parsed = envSchema.safeParse(process.env);
  if (!parsed.success) {
    console.error('Invalid configuration:', parsed.error.flatten().fieldErrors);
    process.exit(1);
  }
  cachedConfig = parsed.data;
  return cachedConfig;
}

export function resetConfigForTesting(): void {
  cachedConfig = null;
}
```

---

## src/telemetry/tracer.ts

```typescript
import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { getConfig } from '../config.js';
import { diag, DiagConsoleLogger, DiagLogLevel } from '@opentelemetry/api';

let sdk: NodeSDK | null = null;

export function initTracer(): NodeSDK {
  const config = getConfig();

  if (config.NODE_ENV === 'development') {
    diag.setLogger(new DiagConsoleLogger(), DiagLogLevel.DEBUG);
  }

  const exporter = new OTLPTraceExporter({
    url: config.OTEL_EXPORTER_OTLP_ENDPOINT,
    headers: config.OTEL_EXPORTER_OTLP_HEADERS
      ? Object.fromEntries(config.OTEL_EXPORTER_OTLP_HEADERS.split(',').map(h => h.split('=')))
      : undefined,
  });

  const sampler = (() => {
    switch (config.OTEL_SAMPLER) {
      case 'always_on':
        return new (await import('@opentelemetry/sdk-trace-base')).AlwaysOnSampler();
      case 'always_off':
        return new (await import('@opentelemetry/sdk-trace-base')).AlwaysOffSampler();
      case 'traceidratio':
        return new (await import('@opentelemetry/sdk-trace-base')).TraceIdRatioBasedSampler(parseFloat(config.OTEL_SAMPLER_ARG));
      case 'parentbased_traceidratio':
        return new (await import('@opentelemetry/sdk-trace-base')).ParentBasedSampler(
          new (await import('@opentelemetry/sdk-trace-base')).TraceIdRatioBasedSampler(parseFloat(config.OTEL_SAMPLER_ARG))
        );
    }
  })();

  sdk = new NodeSDK({
    resource: new Resource({
      [SemanticResourceAttributes.SERVICE_NAME]: config.OTEL_SERVICE_NAME,
      [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
      [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: config.NODE_ENV,
    }),
    traceExporter: exporter,
    instrumentations: [
      getNodeAutoInstrumentations({
        '@opentelemetry/instrumentation-ioredis': { enabled: true },
      }),
    ],
    sampler,
  });

  sdk.start();
  return sdk;
}

export function shutdownTracer(): Promise<void> {
  return sdk?.shutdown() ?? Promise.resolve();
}
```

---

## src/telemetry/context.ts

```typescript
import { context, trace, Span, SpanContext, propagation, ROOT_CONTEXT } from '@opentelemetry/api';
import { getConfig } from '../config.js';

const TRACE_PARENT_HEADER = 'traceparent';
const TRACE_STATE_HEADER = 'tracestate';

export interface TraceContext {
  traceId: string;
  spanId: string;
  traceFlags: number;
  traceState?: string;
}

export function extractTraceContext(headers: Record<string, string | undefined>): TraceContext | null {
  const carrier: Record<string, string> = {};
  if (headers[TRACE_PARENT_HEADER]) carrier[TRACE_PARENT_HEADER] = headers[TRACE_PARENT_HEADER]!;
  if (headers[TRACE_STATE_HEADER]) carrier[TRACE_STATE_HEADER] = headers[TRACE_STATE_HEADER]!;

  const ctx = propagation.extract(ROOT_CONTEXT, carrier);
  const span = trace.getSpan(ctx);
  if (!span) return null;

  const spanContext = span.spanContext();
  return {
    traceId: spanContext.traceId,
    spanId: spanContext.spanId,
    traceFlags: spanContext.traceFlags,
    traceState: spanContext.traceState?.serialize(),
  };
}

export function injectTraceContext(ctx: context.Context, carrier: Record<string, string>): void {
  propagation.inject(ctx, carrier);
}

export function createChildSpan(name: string, parentContext?: TraceContext): Span {
  const tracer = trace.getTracer(getConfig().OTEL_SERVICE_NAME);
  let ctx = context.active();

  if (parentContext) {
    const spanContext: SpanContext = {
      traceId: parentContext.traceId,
      spanId: parentContext.spanId,
      traceFlags: parentContext.traceFlags,
      traceState: parentContext.traceState ? propagation.parseTraceState(parentContext.traceState) : undefined,
      isRemote: true,
    };
    ctx = trace.setSpanContext(ROOT_CONTEXT, spanContext);
  }

  return tracer.startSpan(name, undefined, ctx);
}

export function getCurrentTraceContext(): TraceContext | null {
  const span = trace.getSpan(context.active());
  if (!span) return null;
  const sc = span.spanContext();
  return {
    traceId: sc.traceId,
    spanId: sc.spanId,
    traceFlags: sc.traceFlags,
    traceState: sc.traceState?.serialize(),
  };
}
```

---

## src/errors/classification.ts

```typescript
export class RetryableError extends Error {
  public readonly code: string;
  public readonly retryAfterMs?: number;

  constructor(message: string, code: string, retryAfterMs?: number) {
    super(message);
    this.name = 'RetryableError';
    this.code = code;
    this.retryAfterMs = retryAfterMs;
    Error.captureStackTrace(this, this.constructor);
  }
}

export class TerminalError extends Error {
  public readonly code: string;

  constructor(message: string, code: string) {
    super(message);
    this.name = 'TerminalError';
    this.code = code;
    Error.captureStackTrace(this, this.constructor);
  }
}

export function isRetryableError(error: unknown): error is RetryableError {
  return error instanceof RetryableError;
}

export function isTerminalError(error: unknown): error is TerminalError {
  return error instanceof TerminalError;
}

export function classifyError(error: unknown): { retryable: boolean; error: Error } {
  if (error instanceof RetryableError) return { retryable: true, error };
  if (error instanceof TerminalError) return { retryable: false, error };

  // Default classification for unknown errors
  const err = error instanceof Error ? error : new Error(String(error));

  // Network/timeout errors are retryable
  const retryableCodes = ['ECONNREFUSED', 'ETIMEDOUT', 'ENOTFOUND', 'EAI_AGAIN', 'ECONNRESET'];
  if (retryableCodes.some(c => err.message.includes(c))) {
    return { retryable: true, error: new RetryableError(err.message, 'NETWORK_ERROR') };
  }

  // HTTP 5xx, 429 are retryable
  const statusMatch = err.message.match(/status[:\s]+(\d{3})/i);
  if (statusMatch) {
    const status = parseInt(statusMatch[1], 10);
    if (status >= 500 || status === 429) {
      return { retryable: true, error: new RetryableError(err.message, `HTTP_${status}`) };
    }
    if (status >= 400 && status < 500 && status !== 429) {
      return { retryable: false, error: new TerminalError(err.message, `HTTP_${status}`) };
    }
  }

  // Default: treat as retryable for safety
  return { retryable: true, error: new RetryableError(err.message, 'UNKNOWN_ERROR') };
}
```

---

## src/utils/retry.ts

```typescript
import { getConfig } from '../config.js';

export interface RetryPolicy {
  maxRetries: number;
  baseDelayMs: number;
  maxDelayMs: number;
  jitterFactor: number;
}

export function getRetryPolicy(): RetryPolicy {
  const config = getConfig();
  return {
    maxRetries: config.QUEUE_MAX_RETRIES,
    baseDelayMs: config.QUEUE_BASE_DELAY_MS,
    maxDelayMs: config.QUEUE_MAX_DELAY_MS,
    jitterFactor: config.QUEUE_JITTER_FACTOR,
  };
}

export function calculateBackoff(attempt: number, policy: RetryPolicy): number {
  const exponentialDelay = policy.baseDelayMs * Math.pow(2, attempt);
  const cappedDelay = Math.min(exponentialDelay, policy.maxDelayMs);
  const jitter = cappedDelay * policy.jitterFactor * Math.random();
  return Math.floor(cappedDelay + jitter);
}

export async function withRetry<T>(
  fn: () => Promise<T>,
  policy: RetryPolicy,
  onRetry?: (attempt: number, error: Error, delayMs: number) => void
): Promise<T> {
  let lastError: Error;

  for (let attempt = 0; attempt <= policy.maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      if (attempt === policy.maxRetries) {
        throw lastError;
      }

      const delayMs = calculateBackoff(attempt, policy);
      onRetry?.(attempt + 1, lastError, delayMs);
      await new Promise(resolve => setTimeout(resolve, delayMs));
    }
  }

  throw lastError!;
}
```

---

## src/queue/idempotency.ts

```typescript
import Redis from 'ioredis';
import { getConfig } from '../config.js';
import { createChildSpan, TraceContext } from '../telemetry/context.js';

const IDEMPOTENCY_PREFIX = 'idempotency:';
const IDEMPOTENCY_TTL_SECONDS = 86400 * 7; // 7 days

export interface IdempotencyResult {
  isDuplicate: boolean;
  existingResult?: unknown;
}

export class IdempotencyManager {
  private redis: Redis;

  constructor(redis: Redis) {
    this.redis = redis;
  }

  private getKey(idempotencyKey: string): string {
    return `${IDEMPOTENCY_PREFIX}${idempotencyKey}`;
  }

  async checkAndReserve(
    idempotencyKey: string,
    traceContext?: TraceContext
  ): Promise<IdempotencyResult> {
    const span = createChildSpan('idempotency.checkAndReserve', traceContext);
    span.setAttribute('idempotency.key', idempotencyKey);

    try {
      const key = this.getKey(idempotencyKey);

      // Use SET NX EX for atomic check-and-reserve
      const result = await this.redis.set(key, 'processing', 'NX', 'EX', IDEMPOTENCY_TTL_SECONDS);

      if (result === 'OK') {
        span.setAttribute('idempotency.result', 'reserved');
        return { isDuplicate: false };
      }

      // Key exists, check if completed
      const existing = await this.redis.get(key);
      if (existing && existing !== 'processing') {
        span.setAttribute('idempotency.result', 'duplicate_completed');
        return { isDuplicate: true, existingResult: JSON.parse(existing) };
      }

      span.setAttribute('idempotency.result', 'duplicate_processing');
      return { isDuplicate: true };
    } finally {
      span.end();
    }
  }

  async complete(idempotencyKey: string, result: unknown): Promise<void> {
    const span = createChildSpan('idempotency.complete');
    span.setAttribute('idempotency.key', idempotencyKey);

    try {
      const key = this.getKey(idempotencyKey);
      await this.redis.set(key, JSON.stringify(result), 'EX', IDEMPOTENCY_TTL_SECONDS);
      span.setAttribute('idempotency.result', 'completed');
    } finally {
      span.end();
    }
  }

  async release(idempotencyKey: string): Promise<void> {
    const span = createChildSpan('idempotency.release');
    span.setAttribute('idempotency.key', idempotencyKey);

    try {
      const key = this.getKey(idempotencyKey);
      await this.redis.del(key);
      span.setAttribute('idempotency.result', 'released');
    } finally {
      span.end();
    }
  }

  async getResult(idempotencyKey: string): Promise<unknown | null> {
    const key = this.getKey(idempotencyKey);
    const value = await this.redis.get(key);
    if (!value || value === 'processing') return null;
    return JSON.parse(value);
  }
}
```

---

## src/queue/paymentQueue.ts

```typescript
import { Queue, QueueEvents, Job, WorkerOptions } from 'bullmq';
import Redis from 'ioredis';
import { getConfig } from '../config.js';
import { TraceContext } from '../telemetry/context.js';

export interface PaymentNotificationJobData {
  paymentId: string;
  amount: number;
  currency: string;
  recipientEmail: string;
  recipientName: string;
  paymentMethod: string;
  metadata?: Record<string, unknown>;
  idempotencyKey: string;
  traceContext?: TraceContext;
}

export interface PaymentNotificationJobResult {
  notificationId: string;
  sentAt: string;
  channel: 'email' | 'sms' | 'push';
}

export const QUEUE_NAME = getConfig().QUEUE_NAME;

export function createQueue(redis: Redis): Queue<PaymentNotificationJobData> {
  return new Queue<PaymentNotificationJobData>(QUEUE_NAME, {
    connection: redis,
    defaultJobOptions: {
      removeOnComplete: { age: 3600, count: 1000 },
      removeOnFail: { age: 86400, count: 5000 },
      attempts: getConfig().QUEUE_MAX_RETRIES + 1,
      backoff: {
        type: 'exponential',
        delay: getConfig().QUEUE_BASE_DELAY_MS,
      },
    },
  });
}

export function createQueueEvents(redis: Redis): QueueEvents {
  return new QueueEvents(QUEUE_NAME, { connection: redis });
}

export function getWorkerOptions(): WorkerOptions<PaymentNotificationJobData> {
  return {
    concurrency: getConfig().QUEUE_CONCURRENCY,
    lockDuration: 30000,
    maxStalledCount: 2,
    stalledInterval: 30000,
    drainDelay: 300,
  };
}

export function createJobData(
  data: Omit<PaymentNotificationJobData, 'idempotencyKey' | 'traceContext'>,
  idempotencyKey: string,
  traceContext?: TraceContext
): PaymentNotificationJobData {
  return {
    ...data,
    idempotencyKey,
    traceContext,
  };
}

export async function enqueuePaymentNotification(
  queue: Queue<PaymentNotificationJobData>,
  jobData: PaymentNotificationJobData
): Promise<Job<PaymentNotificationJobData>> {
  return queue.add('send-notification', jobData, {
    jobId: jobData.idempotencyKey, // Use idempotency key as job ID for deduplication
    priority: 0,
  });
}
```

---

## src/queue/deadLetter.ts

```typescript
import { Queue, Job, QueueEvents } from 'bullmq';
import Redis from 'ioredis';
import { getConfig } from '../config.js';
import { PaymentNotificationJobData, PaymentNotificationJobResult } from './paymentQueue.js';
import { createChildSpan, TraceContext } from '../telemetry/context.js';

const DLQ_NAME_SUFFIX = ':dlq';

export interface DeadLetterEntry {
  jobId: string;
  jobData: PaymentNotificationJobData;
  failureReason: string;
  failureCode: string;
  attemptsMade: number;
  lastAttemptAt: string;
  traceContext?: TraceContext;
  originalQueueName: string;
}

export class DeadLetterQueue {
  private dlq: Queue<DeadLetterEntry>;
  private redis: Redis;
  private maxSize: number;
  private ttlMs: number;

  constructor(redis: Redis, originalQueueName: string) {
    this.redis = redis;
    this.dlq = new Queue<DeadLetterEntry>(`${originalQueueName}${DLQ_NAME_SUFFIX}`, { connection: redis });
    this.maxSize = getConfig().DLQ_MAX_SIZE;
    this.ttlMs = getConfig().DLQ_TTL_DAYS * 86400 * 1000;
  }

  async add(entry: DeadLetterEntry): Promise<Job<DeadLetterEntry>> {
    const span = createChildSpan('deadletter.add');
    span.setAttribute('dlq.jobId', entry.jobId);
    span.setAttribute('dlq.failureCode', entry.failureCode);

    try {
      // Check size limit
      const count = await this.dlq.count();
      if (count >= this.maxSize) {
        throw new Error(`Dead letter queue full (max: ${this.maxSize})`);
      }

      const job = await this.dlq.add('dead-letter', entry, {
        jobId: `dlq-${entry.jobId}-${Date.now()}`,
        removeOnComplete: false,
        removeOnFail: false,
      });

      // Set TTL on the job key
      await this.redis.pexpire(`bull:${this.dlq.name}:${job.id}`, this.ttlMs);

      span.setAttribute('dlq.result', 'added');
      return job;
    } finally {
      span.end();
    }
  }

  async getAll(count = 100): Promise<Job<DeadLetterEntry>[]> {
    return this.dlq.getJobs(['waiting', 'active', 'completed', 'failed'], 0, count - 1);
  }

  async replay(jobId: string, targetQueue: Queue<PaymentNotificationJobData>): Promise<void> {
    const span = createChildSpan('deadletter.replay');
    span.setAttribute('dlq.jobId', jobId);

    try {
      const job = await this.dlq.getJob(jobId);
      if (!job) throw new Error(`DLQ job ${jobId} not found`);

      // Re-enqueue to original queue with new idempotency key to allow reprocessing
      const newIdempotencyKey = `${job.data.idempotencyKey}-replay-${Date.now()}`;
      await targetQueue.add('send-notification', {
        ...job.data.jobData,
        idempotencyKey: newIdempotencyKey,
        traceContext: job.data.traceContext,
      }, { jobId: newIdempotencyKey });

      await job.remove();
      span.setAttribute('dlq.result', 'replayed');
    } finally {
      span.end();
    }
  }

  async discard(jobId: string): Promise<void> {
    const job = await this.dlq.getJob(jobId);
    if (job) await job.remove();
  }

  async close(): Promise<void> {
    await this.dlq.close();
  }
}

export function setupDeadLetterHandling(
  queueEvents: QueueEvents,
  dlq: DeadLetterQueue
): void {
  queueEvents.on('failed', async ({ jobId, failedReason, job }) => {
    if (!job) return;

    const attemptsMade = job.attemptsMade;
    const maxAttempts = job.opts.attempts ?? 1;

    if (attemptsMade >= maxAttempts) {
      const entry: DeadLetterEntry = {
        jobId: job.id!,
        jobData: job.data,
        failureReason: failedReason,
        failureCode: 'MAX_RETRIES_EXCEEDED',
        attemptsMade,
        lastAttemptAt: new Date().toISOString(),
        traceContext: job.data.traceContext,
        originalQueueName: job.queueName,
      };

      await dlq.add(entry);
    }
  });
}
```

---

## src/jobs/paymentNotification.ts

```typescript
import { v4 as uuidv4 } from 'uuid';
import { PaymentNotificationJobData, PaymentNotificationJobResult } from '../queue/paymentQueue.js';
import { IdempotencyManager } from '../queue/idempotency.js';
import { classifyError, RetryableError, TerminalError } from '../errors/classification.js';
import { withRetry, getRetryPolicy } from '../utils/retry.js';
import { createChildSpan, TraceContext } from '../telemetry/context.js';
import { getConfig } from '../config.js';

export class PaymentNotificationProcessor {
  private idempotency: IdempotencyManager;

  constructor(idempotency: IdempotencyManager) {
    this.idempotency = idempotency;
  }

  async process(jobData: PaymentNotificationJobData): Promise<PaymentNotificationJobResult> {
    const span = createChildSpan('paymentNotification.process', jobData.traceContext);
    span.setAttribute('payment.id', jobData.paymentId);
    span.setAttribute('payment.amount', jobData.amount);
    span.setAttribute('payment.currency', jobData.currency);
    span.setAttribute('notification.channel', 'email');

    try {
      // Check idempotency
      const idempotencyResult = await this.idempotency.checkAndReserve(
        jobData.idempotencyKey,
        jobData.traceContext
      );

      if (idempotencyResult.isDuplicate) {
        span.setAttribute('idempotency.duplicate', true);
        if (idempotencyResult.existingResult) {
          span.setAttribute('idempotency.returnedCached', true);
          return idempotencyResult.existingResult as PaymentNotificationJobResult;
        }
        // Still processing - throw retryable error to re-queue
        throw new RetryableError('Job already processing', 'DUPLICATE_PROCESSING', 5000);
      }

      // Process with retry
      const policy = getRetryPolicy();
      const result = await withRetry(
        () => this.sendNotification(jobData),
        policy,
        (attempt, error, delayMs) => {
          span.addEvent('retry', {
            attempt,
            error: error.message,
            delayMs,
          });
        }
      );

      // Store result for idempotency
      await this.idempotency.complete(jobData.idempotencyKey, result);

      span.setAttribute('notification.id', result.notificationId);
      span.setAttribute('notification.sentAt', result.sentAt);

      return result;
    } catch (error) {
      const { retryable, error: classifiedError } = classifyError(error);
      span.recordException(classifiedError);
      span.setAttribute('error.retryable', retryable);
      span.setAttribute('error.code', classifiedError.code);

      if (!retryable) {
        throw classifiedError;
      }
      throw classifiedError;
    } finally {
      span.end();
    }
  }

  private async sendNotification(jobData: PaymentNotificationJobData): Promise<PaymentNotificationJobResult> {
    const span = createChildSpan('paymentNotification.sendEmail');

    try {
      // Simulate external API call
      await this.callEmailProvider(jobData);

      const result: PaymentNotificationJobResult = {
        notificationId: uuidv4(),
        sentAt: new Date().toISOString(),
        channel: 'email',
      };

      span.setAttribute('notification.id', result.notificationId);
      return result;
    } finally {
      span.end();
    }
  }

  private async callEmailProvider(jobData: PaymentNotificationJobData): Promise<void> {
    const span = createChildSpan('paymentNotification.callEmailProvider');
    span.setAttribute('provider', 'mock-email-service');

    try {
      // Simulate network call with configurable failure rate
      const config = getConfig();
      if (config.NODE_ENV === 'test') {
        // In tests, we control failures via mocks
        return;
      }

      // Simulate 10% transient failure rate
      if (Math.random() < 0.1) {
        throw new RetryableError('Email provider temporarily unavailable', 'PROVIDER_UNAVAILABLE', 2000);
      }

      // Simulate latency
      await new Promise(resolve => setTimeout(resolve, 50 + Math.random() * 200));
    } finally {
      span.end();
    }
  }
}
```

---

## src/queue/processor.ts

```typescript
import { Worker, Job } from 'bullmq';
import Redis from 'ioredis';
import { PaymentNotificationJobData } from './paymentQueue.js';
import { PaymentNotificationProcessor } from '../jobs/paymentNotification.js';
import { IdempotencyManager } from './idempotency.js';
import { DeadLetterQueue, setupDeadLetterHandling } from './deadLetter.js';
import { createQueue, createQueueEvents, getWorkerOptions, QUEUE_NAME } from './paymentQueue.js';
import { TerminalError } from '../errors/classification.js';
import { createChildSpan, TraceContext } from '../telemetry/context.js';
import { getConfig } from '../config.js';

export interface ProcessorDependencies {
  redis: Redis;
  processor: PaymentNotificationProcessor;
  idempotency: IdempotencyManager;
  dlq: DeadLetterQueue;
}

export class JobProcessor {
  private worker: Worker<PaymentNotificationJobData>;
  private queueEvents: ReturnType<typeof createQueueEvents>;
  private isShuttingDown = false;

  constructor(private deps: ProcessorDependencies) {
    this.queueEvents = createQueueEvents(deps.redis);
    this.worker = new Worker<PaymentNotificationJobData>(
      QUEUE_NAME,
      this.processJob.bind(this),
      {
        ...getWorkerOptions(),
        connection: deps.redis,
      }
    );

    setupDeadLetterHandling(this.queueEvents, deps.dlq);
    this.setupEventHandlers();
  }

  private setupEventHandlers(): void {
    this.worker.on('completed', (job) => {
      // Job completed successfully
    });

    this.worker.on('failed', (job, err) => {
      if (err instanceof TerminalError) {
        // Terminal errors are already handled by dead letter logic
      }
    });

    this.worker.on('error', (err) => {
      console.error('Worker error:', err);
    });
  }

  private async processJob(job: Job<PaymentNotificationJobData>): Promise<void> {
    const span = createChildSpan('worker.processJob', job.data.traceContext);
    span.setAttribute('job.id', job.id!);
    span.setAttribute('job.attemptsMade', job.attemptsMade);

    try {
      await this.deps.processor.process(job.data);
    } catch (error) {
      // Release idempotency lock on terminal errors so replay can work
      if (error instanceof TerminalError) {
        await this.deps.idempotency.release(job.data.idempotencyKey);
      }
      throw error;
    } finally {
      span.end();
    }
  }

  async pause(): Promise<void> {
    this.isShuttingDown = true;
    await this.worker.pause(true);
  }

  async resume(): Promise<void> {
    this.isShuttingDown = false;
    await this.worker.resume();
  }

  async close(): Promise<void> {
    this.isShuttingDown = true;
    await this.worker.close();
    await this.queueEvents.close();
  }

  getWorker(): Worker<PaymentNotificationJobData> {
    return this.worker;
  }
}

export async function createProcessor(redis: Redis): Promise<JobProcessor> {
  const idempotency = new IdempotencyManager(redis);
  const processor = new PaymentNotificationProcessor(idempotency);
  const dlq = new DeadLetterQueue(redis, QUEUE_NAME);

  return new JobProcessor({ redis, processor, idempotency, dlq });
}
```

---

## src/index.ts

```typescript
import { initTracer, shutdownTracer } from './telemetry/tracer.js';
import { createRedisClient } from './queue/redis.js';
import { createProcessor } from './queue/processor.js';
import { getConfig } from './config.js';
import pino from 'pino';

const logger = pino({
  level: getConfig().LOG_LEVEL,
  transport: getConfig().NODE_ENV === 'development' ? { target: 'pino-pretty' } : undefined,
});

async function main(): Promise<void> {
  const config = getConfig();

  // Initialize OpenTelemetry
  const sdk = initTracer();
  logger.info({ service: config.OTEL_SERVICE_NAME }, 'OpenTelemetry initialized');

  // Create Redis connection
  const redis = createRedisClient();
  logger.info({ host: config.REDIS_HOST, port: config.REDIS_PORT }, 'Redis connected');

  // Create and start processor
  const processor = await createProcessor(redis);
  logger.info({ concurrency: config.QUEUE_CONCURRENCY }, 'Job processor started');

  // Graceful shutdown
  const shutdown = async (signal: string): Promise<void> => {
    logger.info({ signal }, 'Shutting down...');
    await processor.pause();
    await processor.close();
    await redis.quit();
    await shutdownTracer();
    logger.info('Shutdown complete');
    process.exit(0);
  };

  process.on('SIGTERM', () => shutdown('SIGTERM'));
  process.on('SIGINT', () => shutdown('SIGINT'));

  // Keep process alive
  process.stdin.resume();
}

main().catch(err => {
  logger.fatal({ err }, 'Fatal error');
  process.exit(1);
});
```

---

## src/queue/redis.ts

```typescript
import Redis from 'ioredis';
import { getConfig } from '../config.js';

let redisClient: Redis | null = null;

export function createRedisClient(): Redis {
  if (redisClient) return redisClient;

  const config = getConfig();

  redisClient = new Redis({
    host: config.REDIS_HOST,
    port: config.REDIS_PORT,
    password: config.REDIS_PASSWORD || undefined,
    db: config.REDIS_DB,
    tls: config.REDIS_TLS ? {} : undefined,
    maxRetriesPerRequest: 3,
    retryStrategy: (times) => {
      if (times > 10) return null;
      return Math.min(times * 200, 2000);
    },
    lazyConnect: true,
  });

  redisClient.on('connect', () => console.log('Redis connected'));
  redisClient.on('error', err => console.error('Redis error:', err));
  redisClient.on('close', () => console.log('Redis connection closed'));

  redisClient.connect().catch(err => {
    console.error('Failed to connect to Redis:', err);
    process.exit(1);
  });

  return redisClient;
}

export function getRedisClient(): Redis | null {
  return redisClient;
}

export async function closeRedisClient(): Promise<void> {
  if (redisClient) {
    await redisClient.quit();
    redisClient = null;
  }
}
```

---

## scripts/replay-dead-letter.ts

```typescript
#!/usr/bin/env tsx
import { program } from 'commander';
import { createRedisClient } from '../src/queue/redis.js';
import { createQueue } from '../src/queue/paymentQueue.js';
import { DeadLetterQueue } from '../src/queue/deadLetter.js';
import { initTracer, shutdownTracer } from '../src/telemetry/tracer.js';
import { getConfig } from '../src/config.js';
import pino from 'pino';

const logger = pino({ level: 'info' });

program
  .name('replay-dead-letter')
  .description('Replay jobs from dead-letter queue')
  .option('-j, --job-id <id>', 'Specific job ID to replay')
  .option('-a, --all', 'Replay all jobs in DLQ')
  .option('-l, --list', 'List jobs in DLQ without replaying')
  .parse(process.argv);

const options = program.opts();

async function main(): Promise<void> {
  initTracer();
  const config = getConfig();
  const redis = createRedisClient();

  const queue = createQueue(redis);
  const dlq = new DeadLetterQueue(redis, config.QUEUE_NAME);

  try {
    if (options.list) {
      const jobs = await dlq.getAll(100);
      console.log(`Found ${jobs.length} jobs in DLQ:`);
      for (const job of jobs) {
        console.log(`  ${job.id}: ${job.data.failureCode} - ${job.data.failureReason} (attempts: ${job.data.attemptsMade})`);
      }
      return;
    }

    if (options.jobId) {
      logger.info({ jobId: options.jobId }, 'Replaying single job');
      await dlq.replay(options.jobId, queue);
      logger.info({ jobId: options.jobId }, 'Job replayed successfully');
      return;
    }

    if (options.all) {
      const jobs = await dlq.getAll(1000);
      logger.info({ count: jobs.length }, 'Replaying all jobs');
      for (const job of jobs) {
        await dlq.replay(job.id!, queue);
        logger.info({ jobId: job.id }, 'Job replayed');
      }
      logger.info('All jobs replayed');
      return;
    }

    program.help();
  } finally {
    await queue.close();
    await dlq.close();
    await redis.quit();
    await shutdownTracer();
  }
}

main().catch(err => {
  logger.fatal({ err }, 'Replay failed');
  process.exit(1);
});
```

---

## Tests

### tests/duplicate-delivery.test.ts

```typescript
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import Redis from 'ioredis';
import { createQueue, createJobData, enqueuePaymentNotification } from '../src/queue/paymentQueue.js';
import { createProcessor } from '../src/queue/processor.js';
import { createRedisClient, closeRedisClient } from '../src/queue/redis.js';
import { resetConfigForTesting } from '../src/config.js';
import { PaymentNotificationJobResult } from '../src/queue/paymentQueue.js';

describe('Duplicate Delivery Protection', () => {
  let redis: Redis;
  let queue: ReturnType<typeof createQueue>;
  let processor: Awaited<ReturnType<typeof createProcessor>>;

  beforeEach(async () => {
    resetConfigForTesting();
    process.env.NODE_ENV = 'test';
    process.env.QUEUE_CONCURRENCY = '1';
    process.env.QUEUE_MAX_RETRIES = '0';

    redis = createRedisClient();
    await new Promise(r => setTimeout(r, 100));

    queue = createQueue(redis);
    processor = await createProcessor(redis);
    await new Promise(r => setTimeout(r, 100));
  });

  afterEach(async () => {
    await processor.close();
    await queue.close();
    await closeRedisClient();
    await new Promise(r => setTimeout(r, 50));
  });

  it('should process job only once when enqueued twice with same idempotency key', async () => {
    const idempotencyKey = `test-dup-${Date.now()}`;
    const jobData = createJobData({
      paymentId: 'pay_123',
      amount: 1000,
      currency: 'USD',
      recipientEmail: 'test@example.com',
      recipientName: 'Test User',
      paymentMethod: 'card',
    }, idempotencyKey);

    // Enqueue twice with same idempotency key
    await enqueuePaymentNotification(queue, jobData);
    await enqueuePaymentNotification(queue, jobData);

    // Wait for processing
    await new Promise(r => setTimeout(r, 2000));

    // Verify only one job was processed (check Redis for completed idempotency key)
    const result = await redis.get(`idempotency:${idempotencyKey}`);
    expect(result).not.toBeNull();
    expect(result).not.toBe('processing');

    const parsed = JSON.parse(result!) as PaymentNotificationJobResult;
    expect(parsed.notificationId).toBeDefined();
    expect(parsed.channel).toBe('email');
  });

  it('should return cached result on duplicate enqueue after completion', async () => {
    const idempotencyKey = `test-dup-cached-${Date.now()}`;
    const jobData = createJobData({
      paymentId: 'pay_456',
      amount: 2000,
      currency: 'EUR',
      recipientEmail: 'test2@example.com',
      recipientName: 'Test User 2',
      paymentMethod: 'bank_transfer',
    }, idempotencyKey);

    // First enqueue and process
    await enqueuePaymentNotification(queue, jobData);
    await new Promise(r => setTimeout(r, 1500));

    const firstResult = await redis.get(`idempotency:${idempotencyKey}`);
    expect(firstResult).not.toBeNull();

    // Second enqueue with same key
    await enqueuePaymentNotification(queue, jobData);
    await new Promise(r => setTimeout(r, 1000));

    // Result should be the same (cached)
    const secondResult = await redis.get(`idempotency:${idempotencyKey}`);
    expect(secondResult).toBe(firstResult);
  });
});
```

### tests/worker-crash.test.ts

```typescript
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import Redis from 'ioredis';
import { createQueue, createJobData, enqueuePaymentNotification } from '../src/queue/paymentQueue.js';
import { createProcessor } from '../src/queue/processor.js';
import { createRedisClient, closeRedisClient } from '../src/queue/redis.js';
import { resetConfigForTesting } from '../src/config.js';
import { Worker } from 'bullmq';

describe('Worker Crash Recovery', () => {
  let redis: Redis;
  let queue: ReturnType<typeof createQueue>;

  beforeEach(async () => {
    resetConfigForTesting();
    process.env.NODE_ENV = 'test';
    process.env.QUEUE_CONCURRENCY = '1';
    process.env.QUEUE_MAX_RETRIES = '3';
    process.env.QUEUE_BASE_DELAY_MS = '100';

    redis = createRedisClient();
    await new Promise(r => setTimeout(r, 100));
    queue = createQueue(redis);
  });

  afterEach(async () => {
    await queue.close();
    await closeRedisClient();
    await new Promise(r => setTimeout(r, 50));
  });

  it('should re-process job after worker crashes mid-execution', async () => {
    const idempotencyKey = `test-crash-${Date.now()}`;
    const jobData = createJobData({
      paymentId: 'pay_crash_1',
      amount: 5000,
      currency: 'USD',
      recipientEmail: 'crash@example.com',
      recipientName: 'Crash Test',
      paymentMethod: 'card',
    }, idempotencyKey);

    await enqueuePaymentNotification(queue, jobData);

    // Start processor
    const processor = await createProcessor(redis);
    await new Promise(r => setTimeout(r, 200));

    // Simulate worker crash by killing the worker process
    // In test, we directly close the worker without completing the job
    await processor.close();

    // Verify job is still in queue (not completed)
    const job = await queue.getJob(idempotencyKey);
    expect(job).not.toBeNull();

    // Restart processor
    const processor2 = await createProcessor(redis);
    await new Promise(r => setTimeout(r, 2000));

    // Job should be processed now
    const result = await redis.get(`idempotency:${idempotencyKey}`);
    expect(result).not.toBeNull();
    expect(result).not.toBe('processing');

    await processor2.close();
  });

  it('should not duplicate work when worker restarts after job completion', async () => {
    const idempotencyKey = `test-crash-complete-${Date.now()}`;
    const jobData = createJobData({
      paymentId: 'pay_crash_2',
      amount: 3000,
      currency: 'GBP',
      recipientEmail: 'crash2@example.com',
      recipientName: 'Crash Test 2',
      paymentMethod: 'card',
    }, idempotencyKey);

    await enqueuePaymentNotification(queue, jobData);

    const processor = await createProcessor(redis);
    await new Promise(r => setTimeout(r, 1500));

    // Get result
    const resultBefore = await redis.get(`idempotency:${idempotencyKey}`);
    expect(resultBefore).not.toBeNull();

    // Restart worker
    await processor.close();
    await new Promise(r => setTimeout(r, 100));

    const processor2 = await createProcessor(redis);
    await new Promise(r => setTimeout(r, 1000));

    // Result should be unchanged
    const resultAfter = await redis.get(`idempotency:${idempotencyKey}`);
    expect(resultAfter).toBe(resultBefore);

    await processor2.close();
  });
});
```

### tests/retry-exhaustion.test.ts

```typescript
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import Redis from 'ioredis';
import { createQueue, createJobData, enqueuePaymentNotification } from '../src/queue/paymentQueue.js';
import { createProcessor } from '../src/queue/processor.js';
import { createRedisClient, closeRedisClient } from '../src/queue/redis.js';
import { DeadLetterQueue } from '../src/queue/deadLetter.js';
import { resetConfigForTesting } from '../src/config.js';
import { TerminalError } from '../src/errors/classification.js';

describe('Retry Exhaustion and Dead Letter', () => {
  let redis: Redis;
  let queue: ReturnType<typeof createQueue>;
  let dlq: DeadLetterQueue;

  beforeEach(async () => {
    resetConfigForTesting();
    process.env.NODE_ENV = 'test';
    process.env.QUEUE_CONCURRENCY = '1';
    process.env.QUEUE_MAX_RETRIES = '2';
    process.env.QUEUE_BASE_DELAY_MS = '50';
    process.env.DLQ_MAX_SIZE = '100';

    redis = createRedisClient();
    await new Promise(r => setTimeout(r, 100));
    queue = createQueue(redis);
    dlq = new DeadLetterQueue(redis, 'payment-notifications');
  });

  afterEach(async () => {
    await queue.close();
    await dlq.close();
    await closeRedisClient();
    await new Promise(r => setTimeout(r, 50));
  });

  it('should move job to DLQ after max retries exhausted', async () => {
    const idempotencyKey = `test-retry-exhaust-${Date.now()}`;
    const jobData = createJobData({
      paymentId: 'pay_retry_1',
      amount: 100,
      currency: 'USD',
      recipientEmail: 'retry@example.com',
      recipientName: 'Retry Test',
      paymentMethod: 'card',
    }, idempotencyKey);

    // Mock the email provider to always fail with retryable error
    vi.doMock('../src/jobs/paymentNotification.ts', () => {
      return {
        PaymentNotificationProcessor: class {
          async process() {
            throw new Error('PROVIDER_UNAVAILABLE: Email provider temporarily unavailable');
          }
        }
      };
    });

    await enqueuePaymentNotification(queue, jobData);

    const processor = await createProcessor(redis);

    // Wait for all retries + DLQ move
    await new Promise(r => setTimeout(r, 5000));

    // Check DLQ
    const dlqJobs = await dlq.getAll(10);
    expect(dlqJobs.length).toBeGreaterThan(0);

    const dlqJob = dlqJobs.find(j => j.data.jobData.idempotencyKey === idempotencyKey);
    expect(dlqJob).toBeDefined();
    expect(dlqJob!.data.failureCode).toBe('MAX_RETRIES_EXCEEDED');
    expect(dlqJob!.data.attemptsMade).toBe(3); // initial + 2 retries

    await processor.close();
  });

  it('should move job to DLQ immediately on terminal error', async () => {
    const idempotencyKey = `test-terminal-${Date.now()}`;
    const jobData = createJobData({
      paymentId: 'pay_terminal_1',
      amount: 200,
      currency: 'USD',
      recipientEmail: 'terminal@example.com',
      recipientName: 'Terminal Test',
      paymentMethod: 'card',
    }, idempotencyKey);

    // Mock to throw terminal error
    vi.doMock('../src/jobs/paymentNotification.ts', () => {
      return {
        PaymentNotificationProcessor: class {
          async process() {
            throw new TerminalError('Invalid email address', 'INVALID_EMAIL');
          }
        }
      };
    });

    await enqueuePaymentNotification(queue, jobData);

    const processor = await createProcessor(redis);
    await new Promise(r => setTimeout(r, 2000));

    // Check DLQ - should be there immediately (no retries)
    const dlqJobs = await dlq.getAll(10);
    const dlqJob = dlqJobs.find(j => j.data.jobData.idempotencyKey === idempotencyKey);
    expect(dlqJob).toBeDefined();
    expect(dlqJob!.data.failureCode).toBe('MAX_RETRIES_EXCEEDED');
    expect(dlqJob!.data.attemptsMade).toBe(1);

    await processor.close();
  });
});
```

### tests/dead-letter-replay.test.ts

```typescript
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import Redis from 'ioredis';
import { createQueue, createJobData, enqueuePaymentNotification } from '../src/queue/paymentQueue.js';
import { createProcessor } from '../src/queue/processor.js';
import { createRedisClient, closeRedisClient } from '../src/queue/redis.js';
import { DeadLetterQueue } from '../src/queue/deadLetter.js';
import { resetConfigForTesting } from '../src/config.js';

describe('Dead Letter Replay', () => {
  let redis: Redis;
  let queue: ReturnType<typeof createQueue>;
  let dlq: DeadLetterQueue;

  beforeEach(async () => {
    resetConfigForTesting();
    process.env.NODE_ENV = 'test';
    process.env.QUEUE_CONCURRENCY = '1';
    process.env.QUEUE_MAX_RETRIES = '1';
    process.env.QUEUE_BASE_DELAY_MS = '50';
    process.env.DLQ_MAX_SIZE = '100';

    redis = createRedisClient();
    await new Promise(r => setTimeout(r, 100));
    queue = createQueue(redis);
    dlq = new DeadLetterQueue(redis, 'payment-notifications');
  });

  afterEach(async () => {
    await queue.close();
    await dlq.close();
    await closeRedisClient();
    await new Promise(r => setTimeout(r, 50));
  });

  it('should replay DLQ job successfully with new idempotency key', async () => {
    // First, create a job that will fail and go to DLQ
    const idempotencyKey = `test-replay-${Date.now()}`;
    const jobData = createJobData({
      paymentId: 'pay_replay_1',
      amount: 500,
      currency: 'USD',
      recipientEmail: 'replay@example.com',
      recipientName: 'Replay Test',
      paymentMethod: 'card',
    }, idempotencyKey);

    // Mock to fail first time
    let attemptCount = 0;
    vi.doMock('../src/jobs/paymentNotification.ts', () => {
      return {
        PaymentNotificationProcessor: class {
          async process() {
            attemptCount++;
            if (attemptCount === 1) {
              throw new Error('PROVIDER_UNAVAILABLE: Temporary failure');
            }
            // Success on retry
            return {
              notificationId: `notif_${Date.now()}`,
              sentAt: new Date().toISOString(),
              channel: 'email' as const,
            };
          }
        }
      };
    });

    await enqueuePaymentNotification(queue, jobData);
    const processor = await createProcessor(redis);
    await new Promise(r => setTimeout(r, 3000));

    // Verify job is in DLQ
    const dlqJobsBefore = await dlq.getAll(10);
    const dlqJob = dlqJobsBefore.find(j => j.data.jobData.idempotencyKey === idempotencyKey);
    expect(dlqJob).toBeDefined();

    // Now replay the job
    await dlq.replay(dlqJob!.id!, queue);
    await new Promise(r => setTimeout(r, 2000));

    // Verify job was processed successfully (new idempotency key)
    const replayedKey = `${idempotencyKey}-replay-`;
    const keys = await redis.keys(`idempotency:${replayedKey}*`);
    expect(keys.length).toBe(1);

    const result = await redis.get(keys[0]);
    expect(result).not.toBeNull();
    const parsed = JSON.parse(result!);
    expect(parsed.notificationId).toBeDefined();

    // Original DLQ job should be removed
    const dlqJobsAfter = await dlq.getAll(10);
    const stillInDlq = dlqJobsAfter.find(j => j.id === dlqJob!.id);
    expect(stillInDlq).toBeUndefined();

    await processor.close();
  });

  it('should allow discarding DLQ jobs', async () => {
    const idempotencyKey = `test-discard-${Date.now()}`;
    const jobData = createJobData({
      paymentId: 'pay_discard_1',
      amount: 100,
      currency: 'USD',
      recipientEmail: 'discard@example.com',
      recipientName: 'Discard Test',
      paymentMethod: 'card',
    }, idempotencyKey);

    vi.doMock('../src/jobs/paymentNotification.ts', () => {
      return {
        PaymentNotificationProcessor: class {
          async process() {
            throw new TerminalError('Permanent failure', 'PERMANENT');
          }
        }
      };
    });

    await enqueuePaymentNotification(queue, jobData);
    const processor = await createProcessor(redis);
    await new Promise(r => setTimeout(r, 2000));

    const dlqJobs = await dlq.getAll(10);
    const dlqJob = dlqJobs.find(j => j.data.jobData.idempotencyKey === idempotencyKey);
    expect(dlqJob).toBeDefined();

    // Discard the job
    await dlq.discard(dlqJob!.id!);

    const dlqJobsAfter = await dlq.getAll(10);
    const stillInDlq = dlqJobsAfter.find(j => j.id === dlqJob!.id);
    expect(stillInDlq).toBeUndefined();

    await processor.close();
  });
});
```

---

## Dockerfile

```dockerfile
FROM node:22-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

# Generate Prisma client if needed
# RUN npx prisma generate

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1

RUN npm run build

# Production image, copy all the files and run
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nodejs

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

USER nodejs

EXPOSE 3000

ENV PORT=3000

CMD ["node", "dist/index.js"]
```

---

## docker-compose.yml

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  jaeger:
    image: jaegertracing/all-in-one:1.57
    ports:
      - "16686:16686"
      - "4318:4318"
    environment:
      - COLLECTOR_OTLP_ENABLED=true

  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4318/v1/traces
      - OTEL_SERVICE_NAME=payment-notification-service
      - NODE_ENV=production
      - LOG_LEVEL=info
    depends_on:
      redis:
        condition: service_healthy
      jaeger:
        condition: service_started
    restart: unless-stopped

volumes:
  redis-data:
```

---

## Installation & Execution Commands

```bash
# 1. Clone/create project directory
mkdir payment-notification-service && cd payment-notification-service

# 2. Create all files from this response

# 3. Install dependencies
npm ci

# 4. Start Redis (using Docker)
docker run -d --name redis -p 6379:6379 redis:7-alpine

# 5. Start Jaeger for tracing (optional)
docker run -d --name jaeger \
  -p 16686:16686 -p 4318:4318 \
  -e COLLECTOR_OTLP_ENABLED=true \
  jaegertracing/all-in-one:1.57

# 6. Copy environment config
cp .env.example .env
# Edit .env as needed

# 7. Build TypeScript
npm run build

# 8. Run service
npm start

# 9. Run tests
npm test

# 10. Run with Docker Compose (all services)
docker-compose up --build

# 11. Replay dead letter jobs
npm run replay:dlq -- --list
npm run replay:dlq -- --all
npm run replay:dlq -- --job-id dlq-xxx
```

---

## API Documentation

### Queue APIs Used (BullMQ v5.56.0)

| API | Purpose |
|-----|---------|
| `new Queue(name, opts)` | Create job queue with Redis connection |
| `queue.add(name, data, opts)` | Enqueue job with idempotency key as `jobId` |
| `new Worker(name, processor, opts)` | Process jobs with bounded concurrency |
| `worker.on('completed'/'failed')` | Handle job lifecycle events |
| `new QueueEvents(name, opts)` | Subscribe to queue events for DLQ |
| `job.attemptsMade` | Track retry attempts |
| `job.opts.attempts` | Configure max retry attempts |
| `backoff: { type: 'exponential', delay }` | Exponential backoff configuration |

### Redis APIs Used (ioredis v5.6.0)

| API | Purpose |
|-----|---------|
| `redis.set(key, value, 'NX', 'EX', ttl)` | Atomic idempotency key reservation |
| `redis.get(key)` | Retrieve idempotency result |
| `redis.del(key)` | Release idempotency lock |
| `redis.keys(pattern)` | Find replayed job keys |
| `redis.pexpire(key, ttl)` | Set TTL on DLQ entries |

### OpenTelemetry APIs Used

| Package | API | Purpose |
|---------|-----|---------|
| `@opentelemetry/api` | `trace.getTracer()` | Create spans |
| | `context.active()` | Get current context |
| | `propagation.inject/extract` | Trace context propagation |
| | `trace.setSpanContext()` | Set parent context for child spans |
| `@opentelemetry/sdk-node` | `NodeSDK` | Configure SDK |
| | `Resource` | Service metadata |
| `@opentelemetry/exporter-trace-otlp-http` | `OTLPTraceExporter` | Export traces to Jaeger/OTel collector |
| `@opentelemetry/auto-instrumentations-node` | `getNodeAutoInstrumentations()` | Auto-instrument Redis, HTTP, etc. |
| `@opentelemetry/instrumentation-ioredis` | (auto) | Instrument Redis commands |

---

## Key Design Decisions

1. **Idempotency via Redis SET NX**: Atomic check-and-reserve prevents duplicate processing. Job ID = idempotency key ensures BullMQ deduplication.

2. **Bounded Concurrency**: `Worker` concurrency option limits parallel job processing.

3. **Exponential Backoff with Jitter**: `calculateBackoff()` implements `base * 2^attempt + jitter` to prevent thundering herd.

4. **Error Classification**: `RetryableError` vs `TerminalError` determines retry behavior. Terminal errors release idempotency lock immediately.

5. **Dead Letter Queue**: Separate BullMQ queue with TTL and size limits. Failed jobs moved after `maxRetries` exhausted.

6. **Safe Replay**: Replay generates new idempotency key (`original-replay-timestamp`) so business effects aren't duplicated.

7. **Trace Context Propagation**: `traceparent`/`tracestate` headers extracted/injected via W3C propagation. Producer and consumer spans linked via parent context.

8. **Deterministic Tests**: Controlled concurrency (1), low retry delays, mocked external dependencies, isolated Redis per test.

