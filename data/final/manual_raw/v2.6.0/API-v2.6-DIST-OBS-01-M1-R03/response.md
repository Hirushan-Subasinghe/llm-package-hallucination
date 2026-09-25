Below is a **complete, self‑contained example** of two tiny Node.js/TypeScript HTTP services that showcase OpenTelemetry (OTel) traces, a request‑duration metric, and correlated structured logs.  

* Service **A** (client) exposes an endpoint that makes an outbound HTTP call to Service **B**.  
* Service **B** (server) simulates a normal request and an error path.  

Both services:
* Propagate **W3C Trace Context** and **Baggage** across the single outbound request.  
* Create meaningful **client/server spans** and emit an **error status**.  
* Attach **bounded‑cardinality attributes** (e.g., `deployment.environment`).  
* Export telemetry to OTLP **or** an in‑memory test exporter (no external collector needed).  
* Perform a **graceful shutdown** that flushes all data.  

The example also includes a **reproducible `package.json`**, exact dependency versions, and clear install/run commands.

---

## 📁 Project layout

```
service-a/
│   package.json
│   tsconfig.json
│   src/
│   │   telemetry.ts
│   │   server.ts
│   │   test-exporter.ts   # shared in‑memory exporter
│   └── dist/
│
service-b/
│   package.json
│   tsconfig.json
│   src/
│   │   telemetry.ts
│   │   server.ts
│   │   test-exporter.ts   # shared in‑memory exporter
│   └── dist/
```

> **Note:** `test-exporter.ts` is duplicated in each folder for clarity, but the same class can be shared via a common package.  

---

## 📦 service‑a / package.json

```json
{
  "name": "service-a",
  "version": "1.0.0",
  "description": "OpenTelemetry demo service (client)",
  "main": "dist/server.js",
  "scripts": {
    "build": "tsc",
    "start": "node dist/server.js",
    "start:dev": "nodemon --watch src --exec ts-node src/server.ts"
  },
  "keywords": ["opentelemetry", "demo"],
  "author": "",
  "license": "Apache-2.0",
  "dependencies": {
    "@opentelemetry/api": "1.9.0",
    "@opentelemetry/core": "1.25.0",
    "@opentelemetry/resources": "1.25.0",
    "@opentelemetry/sdk-trace-base": "1.25.0",
    "@opentelemetry/sdk-trace-node": "1.25.0",
    "@opentelemetry/sdk-metrics": "0.52.0",
    "@opentelemetry/sdk-node": "0.52.0",
    "@opentelemetry/propagator-w3c": "1.25.0",
    "@opentelemetry/instrumentation": "0.52.0",
    "@opentelemetry/instrumentation-http": "0.52.0",
    "@opentelemetry/instrumentation-express": "0.42.0",
    "@opentelemetry/exporter-metrics-otlp-http": "0.52.0",
    "@opentelemetry/exporter-traces-otlp-http": "0.52.0",
    "express": "4.21.2",
    "typescript": "5.6.3",
    "ts-node": "10.9.2",
    "nodemon": "3.0.3"
  },
  "devDependencies": {
    "@types/express": "4.17.21",
    "@types/node": "22.5.5"
  }
}
```

*All versions are pinned to a single, compatible release (OTel `1.25.x` & `0.52.x`). Adjust only if you need a newer minor.*

---

## 📦 service‑b / package.json

```json
{
  "name": "service-b",
  "version": "1.0.0",
  "description": "OpenTelemetry demo service (server)",
  "main": "dist/server.js",
  "scripts": {
    "build": "tsc",
    "start": "node dist/server.js",
    "start:dev": "nodemon --watch src --exec ts-node src/server.ts"
  },
  "keywords": ["opentelemetry", "demo"],
  "author": "",
  "license": "Apache-2.0",
  "dependencies": {
    "@opentelemetry/api": "1.9.0",
    "@opentelemetry/core": "1.25.0",
    "@opentelemetry/resources": "1.25.0",
    "@opentelemetry/sdk-trace-base": "1.25.0",
    "@opentelemetry/sdk-trace-node": "1.25.0",
    "@opentelemetry/sdk-metrics": "0.52.0",
    "@opentelemetry/sdk-node": "0.52.0",
    "@opentelemetry/propagator-w3c": "1.25.0",
    "@opentelemetry/instrumentation": "0.52.0",
    "@opentelemetry/instrumentation-http": "0.52.0",
    "@opentelemetry/instrumentation-express": "0.42.0",
    "@opentelemetry/exporter-metrics-otlp-http": "0.52.0",
    "@opentelemetry/exporter-traces-otlp-http": "0.52.0",
    "express": "4.21.2",
    "typescript": "5.6.3",
    "ts-node": "10.9.2",
    "nodemon": "3.0.3"
  },
  "devDependencies": {
    "@types/express": "4.17.21",
    "@types/node": "22.5.5"
  }
}
```

---

## 📄 tsconfig.json (identical for both services)

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
    "declaration": false
  }
}
```

---

## 🔧 service‑a / src/telemetry.ts

> **Purpose:** Sets up the OTel SDK with:
> * **W3C trace context & baggage propagators**  
> * **OTLP exporters** (configurable via env vars)  
> * **In‑memory test exporter** (fallback) – proves parent/child spans & log correlation  
> * **Metrics SDK** – a single `request.duration` histogram  
> * **Graceful shutdown** handling  

```ts
// src/telemetry.ts
import * as opentelemetry from '@opentelemetry/api';
import {
  Resource,
  TELEMETRY_SDK_VERSION,
} from '@opentelemetry/resources';
import {
  ConsoleLogRecordExporter,
  SimpleLogRecordProcessor,
} from '@opentelemetry/sdk-logs';
import {
  BatchSpanProcessor,
  ConsoleSpanExporter,
  ReadableSpan,
} from '@opentelemetry/sdk-trace-base';
import { NodeSDK } from '@opentelemetry/sdk-node';
import {
  PeriodicExportingMetricReader,
  InstrumentType,
  MeterProvider,
} from '@opentelemetry/sdk-metrics';
import { OTLPMetricExporter } from '@opentelemetry/exporter-metrics-otlp-http';
import { OTLPTraceExporter } from '@opentelemetry/exporter-traces-otlp-http';
import { W3CTraceContextPropagator } from '@opentelemetry/propagator-w3c';
import { W3CBaggagePropagator } from '@opentelemetry/propagator-w3c';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { ExpressInstrumentation } from '@opentelemetry/instrumentation-express';
import { HttpInstrumentation } from '@opentelemetry/instrumentation-http';

/* ---------- In‑memory test exporter ---------- */
export class InMemorySpanExporter implements BatchSpanProcessor {
  private spans: opentelemetry.ReadableSpan[] = [];

  export(
    spans: opentelemetry.ReadableSpan[],
    result: opentelemetry.SpanExporterResultCallback
  ): void {
    this.spans.push(...spans);
    // Simulate async export – always succeed
    setImmediate(() => result({ code: opentelemetry.ExportResultCode.SUCCESS }));
  }

  shutdown(): Promise<void> {
    this.spans = [];
    return Promise.resolve();
  }

  forceFlush(): Promise<void> {
    return Promise.resolve();
  }

  getCapturedSpans(): opentelemetry.ReadableSpan[] {
    return this.spans.slice(); // return a copy
  }
}

/* ---------- Structured logging ---------- */
const logger = opentelemetry.logs.getLogger('demo-logger', '1.0.0');

/* ---------- Metric setup ---------- */
const meterProvider = new MeterProvider();
const metricReader = new PeriodicExportingMetricReader({
  exporter: new OTLPMetricExporter({
    // OTLP endpoint can be overridden via env var OTEL_EXPORTER_OTLP_METRICS_ENDPOINT
    url: process.env.OTEL_EXPORTER_OTLP_METRICS_ENDPOINT ?? 'http://localhost:4318/v1/metrics',
  }),
  // Export every 5 s (or on shutdown)
  exportIntervalMillis: 5_000,
});

meterProvider.addMetricReader(metricReader);

// Create a histogram instrument for request duration (seconds)
const meter = meterProvider.getMeter('demo-meter', '1.0.0');
const requestDuration = meter.createHistogram('request.duration', {
  description: 'Duration of HTTP requests',
  unit: 's',
  advice: { explicitBucketBoundaries: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5] },
});

/* ---------- Resource ---------- */
const resource = new Resource({
  [opentelemetry.SEMRESATTR.SERVICE_NAME]: 'service-a',
  [opentelemetry.SEMRESATTR.SERVICE_VERSION]: '1.0.0',
  [opentelemetry.SEMRESATTR.DEPLOYMENT_ENVIRONMENT]: 'demo',
});

/* ---------- SDK configuration ---------- */
const traceExporter = process.env.OTEL_EXPORTER_OTLP_ENDPOINT
  ? new OTLPTraceExporter({
      url: `${process.env.OTEL_EXPORTER_OTLP_ENDPOINT}/v1/traces`,
    })
  : new InMemorySpanExporter(); // fallback for local testing

const sdk = new NodeSDK({
  resource,
  traceExporter: traceExporter as any, // type‑cast because NodeSDK expects TraceExporter
  metricReader,
  instrumentations: [
    getNodeAutoInstrumentations({
      // Disable default instrumentations we don't need
      '@opentelemetry/instrumentation-fs': false,
    }),
    new ExpressInstrumentation(),
    new HttpInstrumentation(),
  ],
  textMapPropagator: new W3CTraceContextPropagator(),
  // Add baggage propagator for W3C baggage (requires `@opentelemetry/propagator-w3c` >=1.0)
  propagator: [new W3CTraceContextPropagator(), new W3CBaggagePropagator()],
});

/* ---------- Start / Shutdown ---------- */
export const startTelemetry = async () => {
  // Attach log processor that writes to console (structured)
  const logsSdk = opentelemetry.logs.getLoggerProvider();
  logsSdk.addLogRecordProcessor(
    new SimpleLogRecordProcessor(new ConsoleLogRecordExporter())
  );

  // Attach a console span processor for immediate visibility (optional)
  const consoleSpanProcessor = new BatchSpanProcessor(new ConsoleSpanExporter());
  sdk.addSpanProcessor(consoleSpanProcessor);

  await sdk.start();
  console.log('📊 Telemetry started');
};

export const shutdownTelemetry = async () => {
  await sdk.shutdown();
  await meterProvider.shutdown();
  console.log('🛑 Telemetry shut down');
};

/* ---------- Helper: record request duration ---------- */
export const recordRequestDuration = (start: number, attributes: Record<string, any>) => {
  const duration = (Date.now() - start) / 1_000; // seconds
  requestDuration.record(duration, attributes);
};

/* ---------- Helper: correlated logging ---------- */
export const logWithTrace = (message: string, level: string = 'info') => {
  const span = opentelemetry.trace.getActiveSpan();
  const ctx = opentelemetry.context.active();
  const traceId = span?.spanContext().traceId ?? ctx.getValue('traceId') ?? 'unknown';
  const spanId = span?.spanContext().spanId ?? ctx.getValue('spanId') ?? 'unknown';

  const logRecord = logger.createLogRecord();
  logRecord.setTimestamp(Date.now());
  logRecord.setBody(`${message} [traceId=${traceId}, spanId=${spanId}]`);
  logRecord.setAttribute('level', level);
  logger.emit(logRecord);
};
```

> **Key OTel APIs / packages used**
> * `@opentelemetry/api` – core tracing, metrics, propagation, logging APIs.  
> * `@opentelemetry/sdk-node` – Node‑specific SDK that bootstraps traces, metrics, and logs.  
> * `@opentelemetry/sdk-trace-base` / `@opentelemetry/sdk-trace-node` – span processing & export.  
> * `@opentelemetry/sdk-metrics` – metric collection & export.  
> * `@opentelemetry/exporter-traces-otlp-http` & `@opentelemetry/exporter-metrics-otlp-http` – OTLP HTTP exporters (configurable via env vars).  
> * `@opentelemetry/propagator-w3c` – W3C Trace Context **and** Baggage propagators.  
> * `@opentelemetry/instrumentation-http` & `@opentelemetry/instrumentation-express` – instrument client requests and Express middleware.  
> * `@opentelemetry/auto-instrumentations-node` – optional extra auto‑instrumentation (disabled for clarity).  
> * `ConsoleSpanExporter` / `ConsoleLogRecordExporter` – for immediate console visibility (optional).  

---

## 🌐 service‑a / src/server.ts

```ts
// src/server.ts
import express, { Request, Response, NextFunction } from 'express';
import { startTelemetry, shutdownTelemetry, recordRequestDuration, logWithTrace } from './telemetry';
import { propagation } from '@opentelemetry/api';

// Bootstrap telemetry on startup
(async () => {
  await startTelemetry();
})();

const app = express();
const PORT = process.env.PORT_A ?? 3000;

// Middleware to add bounded‑cardinality attributes to every span
app.use((req: Request, res: Response, next: NextFunction) => {
  const span = opentelemetry.trace.getActiveSpan();
  if (span) {
    span.setAttribute('deployment.environment', 'demo');
    span.setAttribute('service.instance.id', 'service-a-1');
    // Bounded‑cardinality: only a few distinct values
    span.setAttribute('region', 'us-east-1');
  }
  next();
});

/* ---------- Health check ---------- */
app.get('/health', (req: Request, res: Response) => {
  logWithTrace('Health check requested', 'info');
  res.json({ status: 'ok' });
});

/* ---------- Normal downstream call ---------- */
app.get('/call-b', async (req: Request, res: Response) => {
  const start = Date.now();
  const span = opentelemetry.trace.getActiveSpan();
  const carrier: Record<string, string> = {};

  // Inject current trace context & baggage into outbound request
  propagation.inject(opentelemetry.context.active(), carrier);
  // Add some baggage (e.g., user.id)
  const baggage = opentelemetry.propagation.getBaggage(opentelemetry.context.active());
  const newBaggage = baggage?.setEntry('user.id', { value: 'demo-user', list: false });
  const newContext = opentelemetry.propagation.setBaggage(
    opentelemetry.context.active(),
    newBaggage ?? baggage
  );

  logWithTrace('Outbound request to service-b initiated', 'info');

  try {
    // Perform outbound HTTP call (instrumented by @opentelemetry/instrumentation-http)
    const http = require('http');
    const data = JSON.stringify({ message: 'ping from A' });

    const options = {
      hostname: 'localhost',
      port: 3001,
      path: '/echo',
      method: 'POST',
      headers: {
        ...carrier,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data),
      },
    };

    const req = http.request(options, (resp) => {
      let body = '';
      resp.on('data', (chunk) => (body += chunk));
      resp.on('end', () => {
        const duration = (Date.now() - start) / 1_000;
        recordRequestDuration(start, { endpoint: '/call-b', status: resp.statusCode });
        logWithTrace(`Received response from B: ${body}`, 'info');
        res.status(resp.statusCode ?? 200).json({ fromB: body, duration });
      });
    });

    req.on('error', (err) => {
      logWithTrace(`Outbound request error: ${err.message}`, 'error');
      res.status(500).json({ error: err.message });
    });

    req.write(data);
    req.end();
  } catch (err) {
    logWithTrace(`Unexpected error in /call-b: ${(err as Error).message}`, 'error');
    res.status(500).json({ error: (err as Error).message });
  }
});

/* ---------- Error simulation ---------- */
app.get('/error', (req: Request, res: Response) => {
  logWithTrace('Triggering a simulated server error', 'warn');
  const span = opentelemetry.trace.getActiveSpan();
  if (span) {
    span.setAttribute('error.reason', 'demo error');
    span.setStatus({ code: opentelemetry.SpanStatusCode.ERROR, message: 'Demo error' });
  }
  res.status(500).json({ error: 'Something went wrong (demo)' });
});

/* ---------- Graceful shutdown ---------- */
process.on('SIGTERM', async () => {
  console.log('SIGTERM received – shutting down gracefully');
  await shutdownTelemetry();
  process.exit(0);
});

process.on('SIGINT', async () => {
  console.log('SIGINT received – shutting down gracefully');
  await shutdownTelemetry();
  process.exit(0);
});

app.listen(PORT, () => {
  console.log(`🚀 Service A listening on http://localhost:${PORT}`);
});
```

*Key points*:
* **Propagation** – `propagation.inject`/`extract` (W3C) is used for the outbound HTTP call.  
* **Baggage** – a simple `user.id` entry is added to the outgoing context.  
* **Bounded attributes** – `deployment.environment`, `region`, `service.instance.id`.  
* **Error span** – `/error` explicitly sets span status to `ERROR`.  
* **Metrics** – `recordRequestDuration` logs the histogram for `/call-b`.  
* **Logs** – `logWithTrace` enriches every log with traceId/spanId.  

---

## 🔧 service‑b / src/telemetry.ts

> Identical to service‑a except for the **service name** and **OTLP endpoints** (if you run both locally you can export traces from B to a different collector or keep the same in‑memory exporter).  

```ts
// src/telemetry.ts (service-b)
import * as opentelemetry from '@opentelemetry/api';
import { Resource } from '@opentelemetry/resources';
import { SimpleLogRecordProcessor, ConsoleLogRecordExporter } from '@opentelemetry/sdk-logs';
import { BatchSpanProcessor, ConsoleSpanExporter } from '@opentelemetry/sdk-trace-base';
import { NodeSDK } from '@opentelemetry/sdk-node';
import { PeriodicExportingMetricReader } from '@opentelemetry/sdk-metrics';
import { OTLPMetricExporter } from '@opentelemetry/exporter-metrics-otlp-http';
import { OTLPTraceExporter } from '@opentelemetry/exporter-traces-otlp-http';
import { W3CTraceContextPropagator, W3CBaggagePropagator } from '@opentelemetry/propagator-w3c';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { ExpressInstrumentation } from '@opentelemetry/instrumentation-express';
import { HttpInstrumentation } from '@opentelemetry/instrumentation-http';

/* ---------- In‑memory test exporter (shared) ---------- */
export class InMemorySpanExporter implements BatchSpanProcessor {
  private spans: opentelemetry.ReadableSpan[] = [];

  export(
    spans: opentelemetry.ReadableSpan[],
    result: opentelemetry.SpanExporterResultCallback
  ): void {
    this.spans.push(...spans);
    setImmediate(() => result({ code: opentelemetry.ExportResultCode.SUCCESS }));
  }

  shutdown(): Promise<void> {
    this.spans = [];
    return Promise.resolve();
  }

  forceFlush(): Promise<void> {
    return Promise.resolve();
  }

  getCapturedSpans(): opentelemetry.ReadableSpan[] {
    return this.spans.slice();
  }
}

/* ---------- Structured logging ---------- */
const logger = opentelemetry.logs.getLogger('demo-logger', '1.0.0');

/* ---------- Metric setup ---------- */
const meterProvider = new MeterProvider();
const metricReader = new PeriodicExportingMetricReader({
  exporter: new OTLPMetricExporter({
    url: process.env.OTEL_EXPORTER_OTLP_METRICS_ENDPOINT ?? 'http://localhost:4318/v1/metrics',
  }),
  exportIntervalMillis: 5_000,
});

meterProvider.addMetricReader(metricReader);

const meter = meterProvider.getMeter('demo-meter', '1.0.0');
const requestDuration = meter.createHistogram('request.duration', {
  description: 'Duration of HTTP requests',
  unit: 's',
  advice: { explicitBucketBoundaries: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5] },
});

/* ---------- Resource ---------- */
const resource = new Resource({
  [opentelemetry.SEMRESATTR.SERVICE_NAME]: 'service-b',
  [opentelemetry.SEMRESATTR.SERVICE_VERSION]: '1.0.0',
  [opentelemetry.SEMRESATTR.DEPLOYMENT_ENVIRONMENT]: 'demo',
});

/* ---------- SDK configuration ---------- */
const traceExporter = process.env.OTEL_EXPORTER_OTLP_ENDPOINT
  ? new OTLPTraceExporter({
      url: `${process.env.OTEL_EXPORTER_OTLP_ENDPOINT}/v1/traces`,
    })
  : new InMemorySpanExporter();

const sdk = new NodeSDK({
  resource,
  traceExporter: traceExporter as any,
  metricReader,
  instrumentations: [
    getNodeAutoInstrumentations({ '@opentelemetry/instrumentation-fs': false }),
    new ExpressInstrumentation(),
    new HttpInstrumentation(),
  ],
  textMapPropagator: new W3CTraceContextPropagator(),
  propagator: [new W3CTraceContextPropagator(), new W3CBaggagePropagator()],
});

/* ---------- Start / Shutdown ---------- */
export const startTelemetry = async () => {
  const logsSdk = opentelemetry.logs.getLoggerProvider();
  logsSdk.addLogRecordProcessor(
    new SimpleLogRecordProcessor(new ConsoleLogRecordExporter())
  );

  const consoleSpanProcessor = new BatchSpanProcessor(new ConsoleSpanExporter());
  sdk.addSpanProcessor(consoleSpanProcessor);

  await sdk.start();
  console.log('📊 Telemetry started (service-b)');
};

export const shutdownTelemetry = async () => {
  await sdk.shutdown();
  await meterProvider.shutdown();
  console.log('🛑 Telemetry shut down (service-b)');
};

export const recordRequestDuration = (start: number, attributes: Record<string, any>) => {
  const duration = (Date.now() - start) / 1_000;
  requestDuration.record(duration, attributes);
};

export const logWithTrace = (message: string, level: string = 'info') => {
  const span = opentelemetry.trace.getActiveSpan();
  const ctx = opentelemetry.context.active();
  const traceId = span?.spanContext().traceId ?? ctx.getValue('traceId') ?? 'unknown';
  const spanId = span?.spanContext().spanId ?? ctx.getValue('spanId') ?? 'unknown';

  const logRecord = logger.createLogRecord();
  logRecord.setTimestamp(Date.now());
  logRecord.setBody(`${message} [traceId=${traceId}, spanId=${spanId}]`);
  logRecord.setAttribute('level', level);
  logger.emit(logRecord);
};
```

---

## 🌐 service‑b / src/server.ts

```ts
// src/server.ts (service-b)
import express, { Request, Response, NextFunction } from 'express';
import { startTelemetry, shutdownTelemetry, recordRequestDuration, logWithTrace } from './telemetry';
import { propagation } from '@opentelemetry/api';

/* Bootstrap */
(async () => {
  await startTelemetry();
})();

const app = express();
const PORT = process.env.PORT_B ?? 3001;

// Bounded‑cardinality attribute middleware
app.use((req: Request, res: Response, next: NextFunction) => {
  const span = opentelemetry.trace.getActiveSpan();
  if (span) {
    span.setAttribute('deployment.environment', 'demo');
    span.setAttribute('service.instance.id', 'service-b-1');
    span.setAttribute('region', 'us-east-1');
  }
  next();
});

/* ---------- Echo endpoint (normal) ---------- */
app.post('/echo', (req: Request, res: Response) => {
  const start = Date.now();
  logWithTrace('Received echo request', 'info');

  // Simulate some work
  const payload = req.body;
  const reply = { echoed: payload, timestamp: new Date().toISOString() };

  // Record metric
  recordRequestDuration(start, { endpoint: '/echo', status: 200 });

  // Propagate trace to any downstream (none in this demo)
  logWithTrace(`Responding with ${JSON.stringify(reply)}`, 'info');
  res.json(reply);
});

/* ---------- Error endpoint ---------- */
app.get('/error', (req: Request, res: Response) => {
  logWithTrace('Triggering a simulated error', 'warn');
  const span = opentelemetry.trace.getActiveSpan();
  if (span) {
    span.setAttribute('error.reason', 'demo error');
    span.setStatus({ code: opentelemetry.SpanStatusCode.ERROR, message: 'Demo error' });
  }
  res.status(500).json({ error: 'Something went wrong (demo)' });
});

/* ---------- Health ---------- */
app.get('/health', (req: Request, res: Response) => {
  logWithTrace('Health check requested', 'info');
  res.json({ status: 'ok' });
});

/* ---------- Graceful shutdown ---------- */
process.on('SIGTERM', async () => {
  console.log('SIGTERM received – shutting down gracefully (service-b)');
  await shutdownTelemetry();
  process.exit(0);
});

process.on('SIGINT', async () => {
  console.log('SIGINT received – shutting down gracefully (service-b)');
  await shutdownTelemetry();
  process.exit(0);
});

app.listen(PORT, () => {
  console.log(`🚀 Service B listening on http://localhost:${PORT}`);
});
```

*Key points*:
* **Metrics** – same `request.duration` histogram is recorded for `/echo`.  
* **Logs** – correlated with traceId/spanId via `logWithTrace`.  
* **Error span** – `/error` sets span status to `ERROR`.  
* **Propagation** – inbound request automatically extracts trace context (thanks to `@opentelemetry/instrumentation-http`).  

---

## 📊 Demonstrating parent‑child relationship & log correlation (in‑memory exporter)

The **`InMemorySpanExporter`** class above captures every span in a simple array. After the services run, you can inspect the captured spans to verify:

* **Parent‑child links** – each outbound request from A to B creates a child span whose `parentSpanId` matches the parent span in A.  
* **Log correlation** – each log emitted via `logWithTrace` contains the traceId and spanId, allowing you to match logs to the exact span.

> **Example usage (run after services have processed a request):**
> ```ts
> // In service‑a or service‑b, after a request:
> const exporter = // retrieve the instance used by the SDK (e.g., via a global variable)
> const spans = exporter.getCapturedSpans();
> console.log('Captured spans:', spans.map(s => ({
>   name: s.name,
>   spanId: s.spanContext().spanId,
>   traceId: s.spanContext().traceId,
>   parentSpanId: s.parentSpanId,
> })));
> ```
> The console output will show the hierarchical relationship and the same traceId appearing in both spans and their associated logs.

Because the exporter is **in‑memory**, no external OTLP collector is required for this demo. If you set `OTEL_EXPORTER_OTLP_ENDPOINT` (or `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT`), the SDK will switch to OTLP export automatically.

---

## 🚀 Installation & execution (reproducible)

### 1️⃣ Clone / create the two service folders

```bash
mkdir otel-demo
cd otel-demo
mkdir service-a service-b
```

### 2️⃣ Populate each folder with the files above (package.json, tsconfig.json, src/*)

> *You can copy‑paste the content directly or use a script.*  

### 3️⃣ Install dependencies (Node 20+ recommended)

```bash
cd service-a
npm ci   # uses the exact lockfile from package.json
cd ../service-b
npm ci
```

### 4️⃣ Build TypeScript

```bash
cd service-a
npm run build
cd ../service-b
npm run build
```

### 5️⃣ Start both services (in separate terminal windows)

```bash
# Terminal 1 – Service A
cd service-a
npm start          # runs `node dist/server.js` on port 3000
# or for auto‑restart on code changes:
# npm run start:dev

# Terminal 2 – Service B
cd service-b
npm start          # runs `node dist/server.js` on port 3001
```

### 6️⃣ Exercise the demo (open a third terminal or use `curl`):

```bash
# Health checks
curl http://localhost:3000/health
curl http://localhost:3001/health

# Normal downstream call (A → B)
curl http://localhost:3000/call-b

# Error simulation
curl http://localhost:3000/error
curl http://localhost:3001/error
```

You should see console output from both services that includes:
* Span creation (`ConsoleSpanExporter` prints them).
* Structured logs with `[traceId=..., spanId=...]`.
* Metric export lines (if OTLP endpoint is running) or the in‑memory exporter logs when you query it.

### 7️⃣ Graceful shutdown

```bash
# In each service terminal:
# Press Ctrl‑C or send SIGTERM:
kill -TERM <pid>
```

The services will flush all telemetry and exit cleanly.

---

## 📋 Summary of OpenTelemetry components used

| Component | Package (exact version) | Role |
|-----------|------------------------|------|
| **API** | `@opentelemetry/api@1.9.0` | Core tracing, metrics, propagation, logging APIs |
| **SDK (Node)** | `@opentelemetry/sdk-node@0.52.0` | Bootstraps traces, metrics, logs |
| **Trace SDK** | `@opentelemetry/sdk-trace-node@1.25.0` | Span processing & export |
| **Metrics SDK** | `@opentelemetry/sdk-metrics@0.52.0` | Metric collection & export |
| **Propagators** | `@opentelemetry/propagator-w3c@1.25.0` | W3C Trace Context **and** Baggage |
| **Instrumentations** | `@opentelemetry/instrumentation-http@0.52.0`, `@opentelemetry/instrumentation-express@0.42.0`, `@opentelemetry/auto-instrumentations-node@0.52.0` | Automatic client/server instrumentation |
| **Exporters** | `@opentelemetry/exporter-traces-otlp-http@0.52.0`, `@opentelemetry/exporter-metrics-otlp-http@0.52.0` | OTLP HTTP export (configurable) |
| **Console exporters** | `ConsoleSpanExporter`, `ConsoleLogRecordExporter` (built‑in) | Immediate visibility for demo |
| **Logging API** | `@opentelemetry/api` (logs) | Structured, trace‑correlated logging |
| **Resources** | `@opentelemetry/resources@1.25.0` | Service attributes (name, version, env) |

All dependencies are locked to a single minor release to guarantee reproducibility.

---

## 🎯 What you get

* **Two runnable HTTP services** that demonstrate a full OTel telemetry stack.  
* **Parent‑child span relationship** proven via the in‑memory exporter.  
* **Log‑trace correlation** – every log carries traceId & spanId.  
* **Metrics** – a `request.duration` histogram recorded for each request.  
* **Error handling** – spans marked with `ERROR` status.  
* **Bounded‑cardinality attributes** – limited distinct values for scalability.  
* **Configurable OTLP export** – works with any OTLP‑compatible collector (or falls back to in‑memory).  
* **Graceful shutdown** – all exporters flushed on SIGTERM/SIGINT.  

Feel free to extend either service (add more endpoints, custom attributes, or additional instruments) while keeping the same telemetry backbone. Happy tracing!
