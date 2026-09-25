I'll continue the response with the necessary sections.## Overview

The service is a **self-contained Node.js TypeScript job‑processing system** that uses Redis as the backing store and BullMQ for advanced queuing features. It provides:

* Idempotent payment‑notification job processing
* Bounded concurrency control
* Exponential retry with jitter
* Clear error classification (retryable vs terminal)
* Exhausted jobs moved to a Dead‑Letter flow
* Safe operator replay without repeating completed business effects
* Full trace context propagation linking producer and consumer spans using OpenTelemetry
* Deterministic tests covering duplicate delivery, worker crash, retry exhaustion, and dead‑letter replay

---

<details><summary>Project Structure</summary>

```
.
├── package.json
├── tsconfig.json
├── .gitignore
├── .env.example
├── README.md
├── src/
│   ├── config/
│   │   ├── redis.ts
│   │   └── otel.ts
│   ├── queues/
│   │   └── payment-notification-queue.ts
│   ├── jobs/
│   │   └── payment-notification-job.ts
│   ├── workers/
│   │   └── payment-notification-worker.ts
│   ├── dead-letter/
│   │   └── dead-letter-queue.ts
│   ├── services/
│   │   ├── idempotent.ts
│   │   ├── trace-propagation.ts
│   │   └── payment-notification-service.ts
│   ├── producers/
│   │   └── payment-notification-producer.ts
│   ├── utils/
│   │   ├── errors.ts
│   │   └── retry-strategies.ts
│   └── index.ts
├── tests/
│   ├── duplicate-delivery.test.ts
│   ├── worker-crash.test.ts
│   ├── retry-exhaustion.test.ts
│   └── dead-letter-replay.test.ts
├── scripts/
│   └── enqueue-sample.ts
```

---

## Dependencies & Versions

| Package | Version | Purpose |
|---------|---------|---------|
| `typescript` | `5.3.3` | TypeScript language |
| `ts-node-dev` | `2.0.0` | Dev server with auto‑restart |
| `@types/node` | `20.10.5` | Node typings |
| `ioredis` | `5.3.2` | Redis client |
| `bullmq` | `5.8.1 | Advanced queue library (Redis‑backed) |
| `@opentelemetry/api` | `1.7.0` | OpenTelemetry API |
| `@opentelemetry/sdk-node` | `0.48.0` | OpenTelemetry Node SDK |
| `@opentelemetry/instrumentation` | `0.48.0` | Instrumentation plugins |
| `@opentelemetry/instrumentation-http` | `0.48.0` | HTTP instrumentation |
| `@opentelemetry/exporter-trace-otlp-proto` | `0.48.0` | OTLP trace exporter |
| `@opentelemetry/resources` | `1.22.0` | Resource detection |
| `@opentelemetry/semantic-conventions` | `1.22.0` | Semantic conventions |
| `jest` | `29.7.0` | Test runner |
| `@types/jest` | `29.5.11` | Jest typings |
| `ts-jest` | `29.1.1` | Jest for TypeScript |
| `sinon` | `17.0.1` | Test spies/mocks |
| `dotenv` | `16.3.1` | Environment variables |

*All packages are compatible with Node.js 20 and use ES modules (`"type": "module"`).*

---

## Configuration Files

### `package.json`

```json
{
  "name": "payment-notification-service",
  "version": "1.0.0",
  "description": "Idempotent payment‑notification job processor with Redis, BullMQ, OpenTelemetry.",
  "main": "dist/index.js",
  "type": "module",
  "scripts": {
    "dev": "ts-node-dev --respawn --transpile-only src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js",
    "test": "jest",
    "test:watch": "jest --watch",
    "lint": "eslint src/ tests/ --ext .ts",
    "format": "prettier --write src/ tests/"
  },
  "keywords": [
    "nodejs",
    "typescript",
    "redis",
    "bullmq",
    "queue",
    "otel",
    "payment"
  ],
  "author": "",
  "license": "ISC",
  "dependencies": {
    "ioredis": "5.3.2",
    "bullmq": "5.8.1",
    "@opentelemetry
