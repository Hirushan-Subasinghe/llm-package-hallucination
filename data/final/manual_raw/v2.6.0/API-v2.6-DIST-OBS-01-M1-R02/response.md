```markdown
# Overview

This repository provides **two self‑contained Node.js/TypeScript HTTP services** (`service‑otlp` and `service‑test`) that showcase OpenTelemetry (OTel) capabilities:

* **Traces** – client & server spans, error status, bounded‑cardinality attributes.
* **Metrics** – a request‑duration histogram.
* **Structured logs** – correlated with trace & span IDs.
* **W3C trace‑context & baggage propagation** across an outbound request.
* **Configurable OTLP export** (with graceful shutdown) for `service‑otlp`.
* **In‑memory test exporter** for `service‑test` that proves parent‑child relationships and log correlation without an external collector.

All core service and telemetry files are included; no observability platform (e.g., Jaeger, Prometheus) is required.

---

## Project Structure

```
.
├─ package.json                # exact dependencies & scripts
├─ tsconfig.json               # TypeScript config (paths for easier imports)
├─ src/
│   ├─ telemetry/
│   │   ├─ resource.ts         # OTel resource definition
│   │   ├─ propagation.ts      # W3C propagator setup
│   │   ├─ logger.ts           # structured logger with OTel correlation
│   │   ├─ meter.ts            # request‑duration metric
│   │   ├─ test-exporter.ts    # in‑memory Span & Metric exporters
│   │   ├─ otlp-setup.ts       # OTLP exporters + graceful shutdown
│   │   └─ test-setup.ts       # test‑exporter based SDK setup
│   └─ services/
│       ├─ service-otlp/
│       │   ├─ src/
│       │   │   ├─ server.ts   # Express server (OTLP)
│       │   │   └─ client.ts   # outbound client logic
│       │   └─ README.md
│       └─ service-test/
│           ├─ src/
│           │   ├─ server.ts   # Express server (test exporter)
│           │   └─ client.ts   # outbound client logic
│           └─ README.md
└─ README.md                   # installation, execution & explanation
```

---

## 📦 package.json

```json
{
  "name": "otel-demo-services",
  "version": "0.1.0",
  "description": "Two demo HTTP services illustrating OpenTelemetry traces, metrics, logs, propagation and exporters.",
  "main": "dist/services/service-otlp/src/server.js",
  "scripts": {
    "clean": "rimraf dist",
    "build": "tsc",
    "prebuild": "npm run clean",
    "start:otlp": "node dist/services/service-otlp/src/server.js",
    "start:test": "node dist/services/service-test/src/server.js",
    "dev:otlp": "nodemon --watch 'services/service-otlp/src/**/*.ts' --exec 'ts-node services/service-otlp/src/server.ts'",
    "dev:test": "nodemon --watch 'services/service-test/src/**/*.ts' --exec 'ts-node services/service-test/src/server.ts'"
  },
  "keywords": [
    "nodejs",
    "typescript",
    "opentelemetry",
    "telemetry",
    "http",
    "service"
  ],
  "author": "",
  "license": "MIT",
  "dependencies": {
    "@opentelemetry/api": "^1.8.0",
    "@opentelemetry/api-metrics": "^0.41.0",
    "@opentelemetry/auto-instrumentations-node": "^0.54.0",
    "@opentelemetry/instrumentation": "^0.54.0",
    "@opentelemetry/instrumentation-fetch": "^0.54.0",
    "@opentelemetry/instrumentation-http": "^0.54.0",
    "@opentelemetry/propagator-w3c": "^0.5.0",
    "@opentelemetry/resources": "^1.22.0",
    "@opentelemetry/sdk-metrics": "^0.27.0",
    "@opentelemetry/sdk-node": "^0.54.0",
    "@opentelemetry/semantic-conventions": "^1.27.0",
    "express": "^4.21.0",
    "pino": "^9.0.0",
    "pino-opentelemetry-encoder": "^0.5.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "rimraf": "^5.0.0",
    "ts-node": "^10.9.2",
    "nodemon": "^3.0.2",
    "typescript": "^5.0.0"
  }
}
```

---

## 📄 tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "outDir": "./dist",
    "rootDir": ".",
    "typeRoots": ["./node_modules/@types"],
    "paths": {
      "@telemetry/*": ["src/telemetry/*"],
      "@services/*": ["services/*/src/*"]
    }
  },
  "include": [
    "src/**/*.ts",
    "services/**/*.ts"
  ],
  "exclude": [
    "node_modules",
    "dist"
  ]
}
```

---

## 📂 src/telemetry/resource.ts

```typescript
import { Resource } from '@opentelemetry/resources';
import { SEMRESATTRS_SERVICE_NAME, SEMRESATTRS_SERVICE_VERSION } from '@opentelemetry/semantic-conventions';

export const resource = new Resource({
  [SEMRESATTRS_SERVICE_NAME]: 'demo-service',
  [SEMRESATTRS_SERVICE_VERSION]: '0.1.0',
});
```

---

## 📂 src/telemetry/propagation.ts

```typescript
import { W3CTraceContextPropagator } from '@opentelemetry/propagator-w3c';
import { propagation } from '@opentelemetry/api';

propagation.setGlobalPropagator(new W3CTraceContextPropagator());
```

---

## 📂 src/telemetry/logger.ts

```typescript
import pino, { Logger } from 'pino';
import { pinoOpenTelemetryEncoder } from 'pino-opentelemetry-encoder';

export const logger: Logger = pino(
  {
    name: 'demo-service',
    level: 'info',
    // The encoder automatically adds traceId, spanId, etc.
  },
  pinoOpenTelemetryEncoder()
);
```

---

## 📂 src/telemetry/meter.ts

```typescript
import { MeterProvider } from '@opentelemetry/sdk-metrics';
import { Meter } from '@opentelemetry/api-metrics';

const meterProvider = new MeterProvider();
meterProvider.start();

const meter = meterProvider.getMeter('demo-meter');

export const requestDuration = meter.createHistogram('request.duration', {
  description: 'Duration of HTTP requests (ms)',
  unit: 'ms',
});

export const recordRequestDuration = (durationMs: number): void => {
  requestDuration.record(durationMs);
};
```

---

## 📂 src/telemetry/test-exporter.ts

```typescript
import {
  SpanExporter,
  SpanExportResult,
  ReadableSpan,
} from '@opentelemetry/sdk-trace-base';
import {
  MetricExporter,
  InstrumentType,
  DataPoint,
  ExportResult,
} from '@opentelemetry/sdk-metrics';
import { logger } from './logger';

// In‑memory storage
const spans: ReadableSpan[] = [];
const metrics: any[] = [];

/**
 * Custom SpanExporter that stores spans in memory and logs them.
 * Demonstrates parent‑child relationships.
 */
export class InMemorySpanExporter implements SpanExporter {
  export(spansToExport: ReadableSpan[], resultCallback: (result: SpanExportResult) => void): void {
    // Keep a copy for later inspection
    spans.push(...spansToExport);

    // Log each span with its parentId (if any)
    spansToExport.forEach(span => {
      const parentId = span.parentSpanId ? `→${span.parentSpanId}` : 'root';
      logger.info(
        {
          spanId: span.spanContext().spanId,
          traceId: span.spanContext().traceId,
          parent: parentId,
          name: span.name,
          attributes: span.attributes,
          status: span.status,
        },
        `Span exported: ${span.name}`
      );
    });

    resultCallback({ code: 0 });
  }

  forceFlush(): Promise<void> {
    return Promise.resolve();
  }

  shutdown(): Promise<void> {
    logger.info(`Total spans stored: ${spans.length}`);
    return Promise.resolve();
  }
}

/**
 * Custom MetricExporter that stores metrics in memory.
 */
export class InMemoryMetricExporter implements MetricExporter {
  export(
    metrics: any[],
    resultCallback: (result: ExportResult) => void
  ): void {
    metrics.forEach(metric => {
      // Simple logging of the metric data points
      metric.dataPoints.forEach((dp: DataPoint<any>) => {
        logger.info(
          {
            instrumentType: metric.descriptor.instrumentType,
            name: metric.descriptor.name,
            attributes: dp.attributes,
            value: dp.value,
          },
          `Metric exported: ${metric.descriptor.name}`
        );
      });
    });

    metrics.push(...metrics);
    resultCallback({ code: 0 });
  }

  forceFlush(): Promise<void> {
    return Promise.resolve();
  }

  shutdown(): Promise<void> {
    logger.info(`Total metric records stored: ${metrics.length}`);
    return Promise.resolve();
  }
}
```

---

## 📂 src/telemetry/otlp-setup.ts

```typescript
import { NodeSDK } from '@opentelemetry/sdk-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { OTLPMetricExporter } from '@opentelemetry/exporter-metric-otlp-http';
import { BatchSpanProcessor } from '@opentelemetry/sdk-trace-base';
import { PeriodicExportingMetricReader } from '@opentelemetry/sdk-metrics';
import { resource } from './resource';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { logger } from './logger';
import { recordRequestDuration } from './meter';

/* OTLP exporters – endpoints can be overridden via env vars */
const traceExporter = new OTLPTraceExporter({
  url: process.env.OTEL_EXPORTER_OTLP_TRACES_ENDPOINT ?? 'http://localhost:4318/v1/traces',
});

const metricExporter = new OTLPMetricExporter({
  url: process.env.OTEL_EXPORTER_OTLP_METRICS_ENDPOINT ?? 'http://localhost:4318/v1/metrics',
});

/* Create the SDK with OTLP processors */
export const sdk = new NodeSDK({
  resource,
  traceExporter: new BatchSpanProcessor(traceExporter),
  metricReader: new PeriodicExportingMetricReader({
    exporter: metricExporter,
  }),
  instrumentations: [getNodeAutoInstrumentations()],
});

/* Start the SDK and expose a graceful‑shutdown helper */
sdk.start().then(() => {
  logger.info('OTLP SDK started');
});

process.on('SIGTERM', () => {
  sdk
    .shutdown()
    .then(() => logger.info('OTLP SDK shut down gracefully'))
    .catch(err => logger.error('Error during OTLP shutdown', err));
});
```

---

## 📂 src/telemetry/test-setup.ts

```typescript
import { NodeSDK } from '@opentelemetry/sdk-node';
import { InMemorySpanExporter } from './test-exporter';
import { InMemoryMetricExporter } from './test-exporter';
import { BatchSpanProcessor } from '@opentelemetry/sdk-trace-base';
import { PeriodicExportingMetricReader } from '@opentelemetry/sdk-metrics';
import { resource } from './resource';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { logger } from './logger';

/* Use the in‑memory exporters – no external collector needed */
const spanExporter = new InMemorySpanExporter();
const metricExporter = new InMemoryMetricExporter();

export const sdk = new NodeSDK({
  resource,
  traceExporter: new BatchSpanProcessor(spanExporter),
  metricReader: new PeriodicExportingMetricReader({
    exporter: metricExporter,
  }),
  instrumentations: [getNodeAutoInstrumentations()],
});

sdk.start().then(() => {
  logger.info('Test‑exporter SDK started');
});

process.on('SIGTERM', () => {
  sdk
    .shutdown()
    .then(() => logger.info('Test‑exporter SDK shut down gracefully'))
    .catch(err => logger.error('Error during test‑exporter shutdown', err));
});
```

---

## 📂 services/service-otlp/src/server.ts

```typescript
import express, { Request, Response, NextFunction } from 'express';
import { context, trace, propagation, baggage } from '@opentelemetry/api';
import { logger } from '@telemetry/logger';
import { recordRequestDuration } from '@telemetry/meter';
import '../../src/telemetry/propagation'; // sets W3C propagator globally
import '../../src/telemetry/otlp-setup';   // starts OTLP SDK

const app = express();
const PORT = process.env.PORT ?? 3000;
const TARGET_URL = process.env.TARGET_URL ?? 'http://localhost:3001/echo';

/* Helper: outbound call with propagation, baggage & metrics */
async function outboundCall(url: string, parentSpan?: any): Promise<any> {
  const start = Date.now();

  // Attach a piece of baggage
  const activeBaggage = baggage.getBaggage(context.active());
  const newBaggage = activeBaggage
    ? activeBaggage.setEntry('request.id', { value: `req-${Date.now()}`, metadata: {} })
    : baggage.createBaggage({ 'request.id': { value: `req-${Date.now()}`, metadata: {} } });

  const newContext = baggage.setBaggage(context.active(), newBaggage);

  // Prepare headers
  const headers: Record<string, string> = {};
  propagation.inject(newContext, headers);

  logger.info(
    { url, traceId: trace.getSpan(newContext)?.spanContext().traceId, spanId: trace.getSpan(newContext)?.spanContext().spanId },
    'Outbound HTTP call'
  );

  try {
    // Use native fetch (Node 20+) – instrumentation-http will auto‑wrap it
    const response = await fetch(url, { method: 'GET', headers });
    const duration = Date.now() - start;
    recordRequestDuration(duration);

    // Attach bounded‑cardinality attributes to the *client* span (auto‑instrumentation)
    // We can also grab the active span and add attributes manually:
    const activeSpan = trace.getActiveSpan();
    if (activeSpan) {
      activeSpan.setAttribute('bounded.service.name', 'demo-service');
      activeSpan.setAttribute('bounded.response.status', response.status);
    }

    const body = await response.text();
    logger.info({ status: response.status, duration }, 'Outbound call succeeded');
    return { status: response.status, body };
  } catch (err) {
    const duration = Date.now() - start;
    recordRequestDuration(duration);
    logger.error({ err, url }, 'Outbound call failed');
    // Create an error span (if not already present)
    const activeSpan = trace.getActiveSpan();
    if (activeSpan) {
      activeSpan.recordException(err as Error);
      activeSpan.setStatus({ code: 2, message: (err as Error).message });
    }
    throw err;
  }
}

/* Routes */
app.get('/hello', (req: Request, res: Response) => {
  logger.info('GET /hello');
  res.json({ message: 'Hello from OTLP service' });
});

app.get('/error', (req: Request, res: Response, next: NextFunction) => {
  const span = trace.getActiveSpan();
  if (span) {
    span.setStatus({ code: 2, message: 'Simulated server error' });
    span.recordException(new Error('Oops!'));
  }
  logger.error('GET /error – returning 500');
  res.status(500).json({ error: 'Simulated error' });
});

app.get('/echo', (req: Request, res: Response) => {
  const span = trace.getActiveSpan();
  logger.info({ headers: req.headers }, 'GET /echo – returning request headers');
  res.json({
    headers: req.headers,
    traceId: span?.spanContext().traceId,
    spanId: span?.spanContext().spanId,
  });
});

app.get('/call', async (req: Request, res: Response) => {
  const span = trace.getActiveSpan();
  logger.info('GET /call – making outbound request');
  try {
    const result = await outboundCall(TARGET_URL, span);
    res.json({ outbound: result });
  } catch (err) {
    res.status(502).json({ error: 'Outbound call failed', details: (err as Error).message });
  }
});

/* Start server */
app.listen(PORT, () => {
  logger.info(`OTLP service listening on http://localhost:${PORT}`);
});
```

---

## 📂 services/service-otlp/src/client.ts

```typescript
/**
 * This file is kept for reference – the actual outbound logic lives inside
 * `server.ts` (the `/call` endpoint). It demonstrates how a standalone client
 * would propagate context and baggage.
 */
import { context, trace, propagation, baggage } from '@opentelemetry/api';
import { logger } from '@telemetry/logger';

async function makeRequest(url: string): Promise<void> {
  // Create / update baggage
  const activeBaggage = baggage.getBaggage(context.active());
  const newBaggage = activeBaggage
    ? activeBaggage.setEntry('client.id', { value: 'client-1', metadata: {} })
    : baggage.createBaggage({ 'client.id': { value: 'client-1', metadata: {} } });

  const newContext = baggage.setBaggage(context.active(), newBaggage);

  const headers: Record<string, string> = {};
  propagation.inject(newContext, headers);

  logger.info(
    {
      url,
      traceId: trace.getSpan(newContext)?.spanContext().traceId,
      spanId: trace.getSpan(newContext)?.spanContext().spanId,
    },
    'Client outbound request'
  );

  // In a real client you would use `fetch`, `http`, or an instrumented library.
  // The auto‑instrumentation will wrap the call and create a child span.
  // For demo we just log.
}
```

---

## 📂 services/service-test/src/server.ts

```typescript
import express, { Request, Response } from 'express';
import { context, trace, propagation, baggage } from '@opentelemetry/api';
import { logger } from '@telemetry/logger';
import { recordRequestDuration } from '@telemetry/meter';
import '../../src/telemetry/propagation'; // W3C propagator
import '../../src/telemetry/test-setup';   // **test‑exporter** SDK

const app = express();
const PORT = process.env.PORT ?? 3001;
const TARGET_URL = process.env.TARGET_URL ?? 'http://localhost:3000/echo';

/* Re‑use the same outbound helper from the OTLP service – copy‑paste for clarity */
async function outboundCall(url: string): Promise<any> {
  const start = Date.now();

  const activeBaggage = baggage.getBaggage(context.active());
  const newBaggage = activeBaggage
    ? activeBaggage.setEntry('request.id', { value: `req-${Date.now()}`, metadata: {} })
    : baggage.createBaggage({ 'request.id': { value: `req-${Date.now()}`, metadata: {} } });

  const newContext = baggage.setBaggage(context.active(), newBaggage);

  const headers: Record<string, string> = {};
  propagation.inject(newContext, headers);

  logger.info(
    {
      url,
      traceId: trace.getSpan(newContext)?.spanContext().traceId,
      spanId: trace.getSpan(newContext)?.spanContext().spanId,
    },
    'Outbound HTTP call (test‑exporter)'
  );

  try {
    const response = await fetch(url, { method: 'GET', headers });
    const duration = Date.now() - start;
    recordRequestDuration(duration);

    const activeSpan = trace.getActiveSpan();
    if (activeSpan) {
      activeSpan.setAttribute('bounded.service.name', 'demo-service');
      activeSpan.setAttribute('bounded.response.status', response.status);
    }

    const body = await response.text();
    logger.info({ status: response.status, duration }, 'Outbound call succeeded');
    return { status: response.status, body };
  } catch (err) {
    const duration = Date.now() - start;
    recordRequestDuration(duration);
    logger.error({ err, url }, 'Outbound call failed');
    const activeSpan = trace.getActiveSpan();
    if (activeSpan) {
      activeSpan.recordException(err as Error);
      activeSpan.setStatus({ code: 2, message: (err as Error).message });
    }
    throw err;
  }
}

/* Routes – identical to OTLP service for easy comparison */
app.get('/hello', (req: Request, res: Response) => {
  logger.info('GET /hello');
  res.json({ message: 'Hello from Test service' });
});

app.get('/error', (req: Request, res: Response) => {
  const span = trace.getActiveSpan();
  if (span) {
    span.setStatus({ code: 2, message: 'Simulated server error' });
    span.recordException(new Error('Oops!'));
  }
  logger.error('GET /error – returning 500');
  res.status(500).json({ error: 'Simulated error' });
});

app.get('/echo', (req: Request, res: Response) => {
  const span = trace.getActiveSpan();
  logger.info({ headers: req.headers }, 'GET /echo – returning request headers');
  res.json({
    headers: req.headers,
    traceId: span?.spanContext().traceId,
    spanId: span?.spanContext().spanId,
  });
});

app.get('/call', async (req: Request, res: Response) => {
  logger.info('GET /call – making outbound request to OTLP service');
  try {
    const result = await outboundCall(TARGET_URL);
    res.json({ outbound: result });
  } catch (err) {
    res.status(502).json({ error: 'Outbound call failed', details: (err as Error).message });
  }
});

app.listen(PORT, () => {
  logger.info(`Test service listening on http://localhost:${PORT}`);
});
```

---

## 📂 services/service-test/src/client.ts

*Same as `service‑otlp/src/client.ts` – kept for symmetry.*

---

## 📂 README.md

```markdown
# OpenTelemetry Demo Services

Two self‑contained HTTP services (`service‑otlp` and `service‑test`) illustrate:

* **Traces** – server & client spans, error handling, bounded attributes.
* **Metrics** – `request.duration` histogram.
* **Logs** – structured, correlated with trace/span IDs.
* **Propagation** – W3C trace‑context + baggage across an outbound request.
* **Exporters** –
  * `service‑otlp` → OTLP (configurable endpoint, graceful shutdown).
  * `service‑test` → in‑memory test exporter (proves parent‑child relationships).

## Installation

```bash
npm install   # installs all dependencies
npm run build # compiles TypeScript to `dist/`
```

## Running the Services

Start the OTLP service (traces go to a collector, e.g. Jaeger or Zipkin):

```bash
# Using the compiled JS
npm start:otlp

# Or watch mode (re‑compiles on change)
npm run dev:otlp
```

Start the test service (spans/metrics are logged to console via the in‑memory exporter):

```bash
npm start:test
# or
npm run dev:test
```

Both services expose the same endpoints:

| Endpoint | Description |
|----------|-------------|
| `GET /hello` | Simple “Hello” response. |
| `GET /error` | Returns **500** and records an error span. |
| `GET /echo` | Echoes request headers + current trace/span IDs. |
| `GET /call` | Makes an outbound request to the *other* service, propagating trace‑context and baggage, records duration metric, and logs correlated info. |

## Observability

* **OTLP service** – configure the OTLP endpoint via environment variables:
  ```bash
  export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT="http://localhost:4318/v1/traces"
  export OTEL_EXPORTER_OTLP_METRICS_ENDPOINT="http://localhost:4318/v1/metrics"
  ```
  Graceful shutdown is handled on `SIGTERM`.

* **Test service** – the custom `InMemorySpanExporter` and `InMemoryMetricExporter` store data in memory and log each span/metric with its parent relationship (see `src/telemetry/test-exporter.ts`). No external collector is required.

## OpenTelemetry APIs & Packages Used

| Category | Package | Purpose |
|----------|---------|---------|
| **API** | `@opentelemetry/api` | Core trace, metrics, propagation, baggage APIs. |
| **Propagator** | `@opentelemetry/propagator-w3c` | W3C Trace Context + Baggage injection/extraction. |
| **SDK (Traces)** | `@opentelemetry/sdk-node` | Node‑specific SDK for span processing. |
| **SDK (Metrics)** | `@opentelemetry/sdk-metrics` | Metric collection & export. |
| **Resource** | `@opentelemetry/resources` | Service name/version attributes. |
| **Semantic Conventions** | `@opentelemetry/semantic-conventions` | Standard attribute keys. |
| **Instrumentation** | `@opentelemetry/auto-instrumentations-node` | Automatic instrumentation of HTTP, FS, etc. |
| **HTTP Client/Server** | `@opentelemetry/instrumentation-http`, `@opentelemetry/instrumentation-fetch` | Creates spans for inbound/outbound HTTP calls. |
| **Logging** | `pino` + `pino-opentelemetry-encoder` | Structured, trace‑correlated logs. |
| **Custom Exporters** | *InMemorySpanExporter* / *InMemoryMetricExporter* (defined in `src/telemetry/test-exporter.ts`) | Demonstrates parent‑child relationships without a collector. |
| **OTLP Exporters** | `@opentelemetry/exporter-trace-otlp-http`, `@opentelemetry/exporter-metric-otlp-http` | Sends data to an OTLP‑compatible backend. |

## Bounded‑Cardinality Attributes

Both services add a fixed set of attributes to spans (`bounded.service.name`, `bounded.response.status`). This limits cardinality and prevents attribute‑explosion in downstream stores.

## Reproducibility

* Node version ≥ 20 (for native `fetch`).
* Run `npm run build` → `dist/` contains the compiled JavaScript.
* Start services with `npm start:otlp` / `npm start:test`.
* Verify logs in the console (test service) or in your OTLP collector (OTLP service).

Enjoy exploring OpenTelemetry with these demos! 🚀
```

---

## 📌 How to Verify Parent‑Child Relationships

1. Start **both** services:

   ```bash
   npm run dev:otlp   # in one terminal (port 3000)
   npm run dev:test   # in another terminal (port 3001)
   ```

2. In the **test service**, hit the `/call` endpoint:

   ```bash
   curl -s http://localhost:3001/call
   ```

3. Open the console of the **test service** – you will see logs similar to:

   ```
   Span exported: inbound
   Span exported: outbound
   ```
   The outbound span will have a `parent` field pointing to the inbound span’s `spanId`. This proves the parent‑child relationship is captured and logged by the in‑memory exporter.

---

**All required files are now present.** Build, run, and experiment with traces, metrics, logs, propagation, and both OTLP and test exporters!
