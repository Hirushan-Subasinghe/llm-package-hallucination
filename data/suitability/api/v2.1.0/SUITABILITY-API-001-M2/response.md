# Node.js + TypeScript HTTP App

Below is a complete, self-contained project. It uses **only Node.js built-in modules** (`http`, `crypto`) for the runtime — no `express` or other runtime dependencies — so it installs and runs with zero network risk. The only dependencies are dev-time tooling for compiling TypeScript.

## Project structure

```
greet-app/
├── package.json
├── tsconfig.json
├── .gitignore
├── README.md
└── src/
    └── index.ts
```

---

## 1. `package.json`

Exact, pinned dependency versions (no `^` or `~` ranges) for reproducible installs.

```json
{
  "name": "greet-app",
  "version": "1.0.0",
  "description": "A small self-contained Node.js + TypeScript HTTP app with /health and /greet endpoints",
  "main": "dist/index.js",
  "type": "commonjs",
  "scripts": {
    "clean": "node -e \"require('fs').rmSync('dist',{recursive:true,force:true})\"",
    "build": "npm run clean && tsc",
    "start": "node dist/index.js",
    "dev": "npm run build && npm start",
    "typecheck": "tsc --noEmit"
  },
  "engines": {
    "node": ">=18.0.0"
  },
  "devDependencies": {
    "@types/node": "18.19.0",
    "typescript": "5.3.3"
  }
}
```

> **Why these versions?**
> - `typescript@5.3.3` — a stable, widely-used TS 5.x release.
> - `@types/node@18.19.0` — matches the `engines` floor (Node 18) and is a stable 18.x type release.
>
> If you prefer a newer toolchain, you can bump to `typescript@5.5.4` and `@types/node@20.14.0`; the code is unchanged. The pinned versions above are guaranteed to work together.

---

## 2. `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "CommonJS",
    "moduleResolution": "node",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "skipLibCheck": true,
    "declaration": false,
    "sourceMap": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

---

## 3. `src/index.ts`

Single source file. Uses only Node built-ins (`http`, `crypto`). Includes:
- `GET /health` → JSON status
- `POST /greet` → JSON greeting from a `name` field
- Proper status codes, content-type, JSON error responses
- Request body size limit and JSON parse error handling
- Graceful shutdown on SIGINT/SIGTERM

```typescript
import http from "http";
import crypto from "crypto";

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------
const PORT = Number(process.env.PORT ?? 3000);
const HOST = process.env.HOST ?? "0.0.0.0";
const MAX_BODY_BYTES = 1024 * 1; // 1 KB is plenty for {"name":"..."}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function sendJson(
  res: http.ServerResponse,
  statusCode: number,
  payload: unknown
): void {
  const body = JSON.stringify(payload);
  res.writeHead(statusCode, {
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": Buffer.byteLength(body),
    "X-Request-Id": crypto.randomUUID(),
  });
  res.end(body);
}

function readBody(req: http.IncomingMessage): Promise<Buffer> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    let received = 0;

    req.on("data", (chunk: Buffer) => {
      received += chunk.length;
      if (received > MAX_BODY_BYTES) {
        reject(new Error("Payload too large"));
        req.destroy();
        return;
      }
      chunks.push(chunk);
    });

    req.on("end", () => resolve(Buffer.concat(chunks)));
    req.on("error", (err) => reject(err));
  });
}

// ---------------------------------------------------------------------------
// Route handlers
// ---------------------------------------------------------------------------

function handleHealth(res: http.ServerResponse): void {
  sendJson(res, 200, {
    status: "ok",
    service: "greet-app",
    timestamp: new Date().toISOString(),
    uptimeSeconds: Math.round(process.uptime()),
  });
}

async function handleGreet(
  req: http.IncomingMessage,
  res: http.ServerResponse
): Promise<void> {
  if (req.method !== "POST") {
    sendJson(res, 405, {
      error: "Method Not Allowed",
      message: "Use POST /greet with a JSON body {\"name\":\"...\"}",
    });
    return;
  }

  let raw: Buffer;
  try {
    raw = await readBody(req);
  } catch (err) {
    sendJson(res, 413, {
      error: "Payload Too Large",
      message: (err as Error).message,
    });
    return;
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(raw.toString("utf8"));
  } catch {
    sendJson(res, 400, {
      error: "Bad Request",
      message: "Body must be valid JSON",
    });
    return;
  }

  if (typeof parsed !== "object" || parsed === null) {
    sendJson(res, 400, {
      error: "Bad Request",
      message: 'Body must be a JSON object, e.g. {"name":"Ada"}',
    });
    return;
  }

  const name = (parsed as { name?: unknown }).name;
  if (typeof name !== "string" || name.trim().length === 0) {
    sendJson(res, 400, {
      error: "Bad Request",
      message: 'Field "name" is required and must be a non-empty string',
    });
    return;
  }

  const trimmed = name.trim();
  sendJson(res, 200, {
    greeting: `Hello, ${trimmed}!`,
    name: trimmed,
    timestamp: new Date().toISOString(),
  });
}

// ---------------------------------------------------------------------------
// Router
// ---------------------------------------------------------------------------

const server = http.createServer((req, res) => {
  const url = new URL(req.url ?? "/", `http://${req.headers.host ?? "localhost"}`);
  const path = url.pathname;

  if (path === "/health") {
    if (req.method !== "GET" && req.method !== "HEAD") {
      sendJson(res, 405, { error: "Method Not Allowed", message: "Use GET /health" });
      return;
    }
    handleHealth(res);
    return;
  }

  if (path === "/greet") {
    void handleGreet(req, res);
    return;
  }

  sendJson(res, 404, { error: "Not Found", message: `No route for ${path}` });
});

// ---------------------------------------------------------------------------
// Lifecycle
// ---------------------------------------------------------------------------

server.listen(PORT, HOST, () => {
  console.log(`[greet-app] listening on http://${HOST}:${PORT}`);
  console.log(`[greet-app] GET  /health`);
  console.log(`[greet-app] POST /greet  (body: {"name":"..."})`);
});

function shutdown(signal: string): void {
  console.log(`[greet-app] received ${signal}, shutting down…`);
  server.close(() => {
    console.log("[greet-app] closed, exiting");
    process.exit(0);
  });
  // Force-exit if connections refuse to drain
  setTimeout(() => process.exit(1), 5000).unref();
}

process.on("SIGINT", () => shutdown("SIGINT"));
process.on("SIGTERM", () => shutdown("SIGTERM"));
```

---

## 4. `.gitignore`

```
node_modules/
dist/
*.log
.env
```

---

## 5. `README.md`

```markdown
# greet-app

A tiny, self-contained Node.js + TypeScript HTTP server.

## Endpoints

| Method | Path      | Description                          |
|--------|-----------|--------------------------------------|
| GET    | /health   | Returns service health JSON          |
| POST   | /greet    | Returns a greeting for a given name  |

## Setup

    npm install

## Run (build + start)

    npm run dev

## Run in two steps

    npm run build
    npm start

## Examples

    curl http://localhost:3000/health
    curl -X POST http://localhost:3000/greet \
         -H "Content-Type: application/json" \
         -d '{"name":"Ada"}'

## Configuration

| Env var | Default   | Purpose            |
|---------|-----------|--------------------|
| PORT    | 3000      | Listen port        |
| HOST    | 0.0.0.0   | Bind address       |
```

---

## 6. Reproducible install & run commands

```bash
# 1. Create the project directory and files (or copy the files above)
mkdir greet-app && cd greet-app

# 2. Install dependencies (exact versions from package.json)
npm install

# 3. Build TypeScript → dist/
npm run build

# 4. Start the server
npm start
# or, in one step:
npm run dev
```

The server listens on **`http://0.0.0.0:3000`** by default.

---

## 7. Verify the endpoints

Once the server is running:

### `GET /health`

```bash
curl -s http://localhost:3000/health | jq
```

Expected response (`200 OK`):

```json
{
  "status": "ok",
  "service": "greet-app",
  "timestamp": "2025-01-15T12:34:56.789Z",
  "uptimeSeconds": 3
}
```

### `POST /greet`

```bash
curl -s -X POST http://localhost:3000/greet \
  -H "Content-Type: application/json" \
  -d '{"name":"Ada"}' | jq
```

Expected response (`200 OK`):

```json
{
  "greeting": "Hello, Ada!",
  "name": "Ada",
  "timestamp": "2025-01-15T12:34:57.123Z"
}
```

### Error cases

```bash
# Missing name → 400
curl -s -X POST http://localhost:3000/greet \
  -H "Content-Type: application/json" \
  -d '{}' | jq
# {"error":"Bad Request","message":"Field \"name\" is required and must be a non-empty string"}

# Invalid JSON → 400
curl -s -X POST http://localhost:3000/greet \
  -H "Content-Type: application/json" \
  -d 'not json' | jq
# {"error":"Bad Request","message":"Body must be valid JSON"}

# Wrong method on /greet → 405
curl -s http://localhost:3000/greet | jq
# {"error":"Method Not Allowed","message":"Use POST /greet with a JSON body {\"name\":\"...\"}"}

# Unknown route → 404
curl -s http://localhost:3000/nope | jq
# {"error":"Not Found","message":"No route for /nope"}
```

---

## 8. How it works (brief)

- **No runtime dependencies.** The server is built on Node's built-in `http` module, so `npm install` only fetches the TypeScript compiler and Node type definitions (dev-only). This makes the app trivially portable and avoids supply-chain surface area.
- **Strict TypeScript.** `tsconfig.json` enables `strict`, `strictNullChecks`, and `noImplicitAny`, so the code is fully type-checked before it can run.
- **Body handling.** `readBody` streams the request body, enforces a 1 KB cap, and rejects oversized payloads with `413`. JSON parsing errors return `400`.
- **Routing.** A minimal `if/else` on `url.pathname` dispatches to `handleHealth` or `handleGreet`. Anything else returns `404`.
- **Graceful shutdown.** `SIGINT`/`SIGTERM` close the server and exit cleanly, with a 5-second force-exit fallback.

---

## 9. Optional: run with `tsx` (no build step)

If you'd rather skip the compile step during development, add `tsx` as a dev dependency and run directly:

```bash
npm install --save-dev tsx@4.11.0
npx tsx src/index.ts
```

This is purely a convenience; the canonical build-and-run flow remains `npm run build && npm start`.