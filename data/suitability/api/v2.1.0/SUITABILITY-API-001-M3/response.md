Below is a **complete, self‑contained Node.js + TypeScript** project that provides  

* **GET /health** – returns `{ "status": "ok" }`  
* **POST /greet** – expects JSON `{ "name": "YourName" }` and returns `{ "greeting": "Hello, YourName!" }`

Everything you need (source, configuration, exact dependency versions, and the commands to install and run) is included in this single response.

---

## 1️⃣ Project layout (what you will create)

```
health-greet-app/
├─ package.json
├─ tsconfig.json
└─ src/
   └─ index.ts
```

---

## 2️⃣ `package.json` – exact versions

```json
{
  "name": "health-greet-app",
  "version": "1.0.0",
  "description": "A minimal TypeScript Express app with health and greet endpoints.",
  "main": "dist/index.js",
  "scripts": {
    "dev": "ts-node-dev --respawn --transpile-only src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js"
  },
  "author": "",
  "license": "MIT",
  "dependencies": {
    "express": "4.18.2"
  },
  "devDependencies": {
    "@types/express": "4.18.2",
    "@types/node": "20.11.0",
    "ts-node-dev": "2.0.0",
    "typescript": "5.4.5"
  }
}
```

*All versions are pinned, so `npm install` will always give the same exact set of packages.*

---

## 3️⃣ `tsconfig.json` – TypeScript compiler options

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "skipLibCheck": true
  },
  "include": ["src"]
}
```

---

## 4️⃣ Source code – `src/index.ts`

```ts
import express, { Request, Response } from 'express';

const app = express();
const port = process.env.PORT || 3000;

// Built‑in JSON body parser (no extra dependency needed)
app.use(express.json());

/**
 * GET /health
 * Returns a simple JSON object indicating the service is alive.
 */
app.get('/health', (req: Request, res: Response) => {
  res.json({ status: 'ok' });
});

/**
 * POST /greet
 * Expects: { "name": "YourName" }
 * Returns: { "greeting": "Hello, YourName!" }
 */
app.post('/greet', (req: Request, res: Response) => {
  const name = req.body?.name;

  if (typeof name !== 'string' || !name.trim()) {
    return res
      .status(400)
      .json({ error: 'Name is required and must be a non‑empty string.' });
  }

  res.json({ greeting: `Hello, ${name}!` });
});

app.listen(port, () => {
  console.log(`🚀 Server listening at http://localhost:${port}`);
});
```

---

## 5️⃣ How to get it running

> **Prerequisite** – Node.js ≥ 18 (any recent LTS version) must be installed and available on the command line.

### Step‑by‑step

```bash
# 1️⃣ Clone / copy the files into a folder (e.g. health-greet-app)
#    (If you are reading this in a terminal, just create the folder and paste the files.)

# 2️⃣ Install the exact dependencies
npm install

# 3️⃣ Development mode (auto‑restarts on changes)
npm run dev
#    → Server starts on http://localhost:3000
#    → You’ll see a console line: "🚀 Server listening at http://localhost:3000"

# 4️⃣ Production build + start
npm run build   # compiles TypeScript to ./dist
npm start       # runs the compiled JavaScript
```

---

## 6️⃣ Quick test with `curl`

```bash
# Health check
curl -i http://localhost:3000/health
#> HTTP/1.1 200 OK
#> Content-Type: application/json; charset=utf-8
#> ...
#> {"status":"ok"}

# Greet (valid)
curl -i -X POST http://localhost:3000/greet \
     -H "Content-Type: application/json" \
     -d '{"name":"Alice"}'
#> HTTP/1.1 200 OK
#> Content-Type: application/json; charset=utf-8
#> ...
#> {"greeting":"Hello, Alice!"}

# Greet (missing name)
curl -i -X POST http://localhost:3000/greet \
     -H "Content-Type: application/json" \
     -d '{}'
#> HTTP/1.1 400 Bad Request
#> {"error":"Name is required and must be a non‑empty string."}
```

---

## 7️⃣ What you have now

* A **single source file** (`src/index.ts`) that defines the two endpoints.
* **TypeScript** compilation set up with strict checking.
* **npm scripts** for fast development (`npm run dev`) and for building/starting a production‑ready version (`npm run build && npm start`).
* All **dependency versions are fixed**, guaranteeing reproducible installs.

You can now extend the app, add more routes, or integrate it into a larger system – all while having a clean, typed, and minimal starting point. Happy coding!