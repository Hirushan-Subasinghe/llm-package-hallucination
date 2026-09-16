**project structure**

```
my-app/
├─ package.json
├─ tsconfig.json
├─ src/
│   └─ index.ts
└─ README.md   (optional – just for reference)
```

---

### package.json
```json
{
  "name": "typescript-http-app",
  "version": "1.0.0",
  "description": "A tiny self‑contained Node.js/TypeScript HTTP server with /health and /greet endpoints.",
  "main": "dist/index.js",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "ts-node src/index.ts"
  },
  "keywords": [
    "typescript",
    "node",
    "http",
    "express"
  ],
  "author": "",
  "license": "MIT",
  "dependencies": {
    "express": "^4.18.2"
  },
  "devDependencies": {
    "@types/express": "^4.17.21",
    "@types/node": "^20.1.0",
    "ts-node": "^10.9.1",
    "typescript": "^5.0.3"
  }
}
```

---

### tsconfig.json
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
    "noEmitOnError": true
  },
  "include": ["src/**/*"]
}
```

---

### src/index.ts
```typescript
import express, { Request, Response } from 'express';

/**
 * Health‑check endpoint.
 * GET /health
 */
const healthHandler = (_req: Request, res: Response) => {
  res.json({ status: 'ok' });
};

/**
 * Greeting endpoint.
 * POST /greet – expects JSON body: { "name": "Alice" }
 */
const greetHandler = (req: Request, res: Response) => {
  const { name } = req.body as { name?: string };

  if (!name) {
    res.status(400).json({ error: 'Missing "name" field in request body.' });
    return;
  }

  res.json({ message: `Hello, ${name}!` });
};

const app = express();
const PORT = process.env.PORT ?? 3000;

// Middleware to parse JSON bodies
app.use(express.json());

// Routes
app.get('/health', healthHandler);
app.post('/greet', greetHandler);

// Start server
app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
```

---

### How to install and run

```bash
# 1️⃣ Create the project folder (if you haven’t already)
mkdir my-app && cd my-app

# 2️⃣ Paste the three files above into the appropriate locations
#    (package.json, tsconfig.json, src/index.ts)

# 3️⃣ Install dependencies (exact versions are locked by package.json)
npm install

# 4️⃣ Build the TypeScript code into JavaScript
npm run build   # creates dist/index.js

# 5️⃣ Run the HTTP server
npm start       # listens on port 3000

# For development with auto‑restart (if ts-node is installed):
npm run dev     # runs the same code without a separate build step
```

**Testing the endpoints**

```bash
# Health check
curl http://localhost:3000/health
# Expected output: {"status":"ok"}

# Greeting
curl -X POST -H "Content-Type: application/json" -d '{"name":"World"}' http://localhost:3000/greet
# Expected output: {"message":"Hello, World!"}
```

That’s the complete, self‑contained solution. No extra tooling or external services are required – just Node.js + TypeScript. Enjoy!