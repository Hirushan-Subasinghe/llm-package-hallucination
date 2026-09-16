# Complete Node.js TypeScript HTTP Application

## Project Structure
```
.
├── package.json
├── tsconfig.json
└── src
    └── index.ts
```

---

## package.json

```json
{
  "name": "health-greet-api",
  "version": "1.0.0",
  "description": "Minimal HTTP API with /health and /greet endpoints",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "ts-node src/index.ts"
  },
  "keywords": [],
  "author": "",
  "license": "MIT",
  "dependencies": {
    "express": "4.19.2"
  },
  "devDependencies": {
    "@types/express": "4.17.21",
    "@types/node": "20.14.2",
    "ts-node": "10.9.2",
    "typescript": "5.4.5"
  },
  "engines": {
    "node": ">=20.0.0"
  }
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
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

---

## src/index.ts

```typescript
import express, { Request, Response, NextFunction } from 'express';

const app = express();
const PORT = process.env.PORT ? Number(process.env.PORT) : 3000;

app.use(express.json());

// GET /health - returns service health status
app.get('/health', (_req: Request, res: Response) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

// POST /greet - accepts { "name": "string" } and returns greeting
app.post('/greet', (req: Request, res: Response, next: NextFunction) => {
  const { name } = req.body as { name?: unknown };

  if (typeof name !== 'string' || name.trim() === '') {
    return res.status(400).json({
      error: 'Invalid request: "name" must be a non-empty string'
    });
  }

  res.json({
    message: `Hello, ${name.trim()}!`,
    receivedAt: new Date().toISOString()
  });
});

// 404 handler
app.use((_req: Request, res: Response) => {
  res.status(404).json({ error: 'Not found' });
});

// Error handler
app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
  console.error('Unhandled error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

app.listen(PORT, () => {
  console.log(`Server listening on http://localhost:${PORT}`);
});

export { app };
```

---

## Installation & Run Commands

### 1. Install dependencies (reproducible, exact versions)
```bash
npm ci
```
> **Note:** `npm ci` requires a `package-lock.json`. On first run, generate it with:
> ```bash
> npm install --package-lock-only
> npm ci
> ```

### 2. Build TypeScript to JavaScript
```bash
npm run build
```
Output: `dist/index.js` + `dist/index.d.ts` + source maps

### 3. Run production build
```bash
npm start
```
Server starts on `http://localhost:3000`

### 4. Run in development (with hot reload via ts-node)
```bash
npm run dev
```

---

## API Examples

### Health Check
```bash
curl http://localhost:3000/health
```
**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-06-15T12:34:56.789Z",
  "uptime": 12.345
}
```

### Greet (valid)
```bash
curl -X POST http://localhost:3000/greet \
  -H "Content-Type: application/json" \
  -d '{"name": "Ada"}'
```
**Response:**
```json
{
  "message": "Hello, Ada!",
  "receivedAt": "2025-06-15T12:35:01.234Z"
}
```

### Greet (invalid - missing/empty name)
```bash
curl -X POST http://localhost:3000/greet \
  -H "Content-Type: application/json" \
  -d '{"name": ""}'
```
**Response (400):**
```json
{
  "error": "Invalid request: \"name\" must be a non-empty string"
}
```

---

## Verification Checklist

| Step | Command | Expected |
|------|---------|----------|
| Install | `npm ci` | `node_modules/` created, no vulnerabilities |
| Build | `npm run build` | `dist/index.js` exists |
| Start | `npm start` | Logs `Server listening on http://localhost:3000` |
| Health | `curl localhost:3000/health` | JSON with `status: "ok"` |
| Greet | `curl -X POST ... -d '{"name":"Test"}'` | JSON with `message: "Hello, Test!"` |