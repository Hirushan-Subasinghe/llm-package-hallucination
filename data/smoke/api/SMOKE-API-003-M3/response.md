**Folder layout**

```
iso-timestamp-cli/
├─ src/
│  └─ index.ts
├─ package.json
├─ tsconfig.json
```

---

### `package.json` (exact versions)

```json
{
  "name": "iso-timestamp-cli",
  "version": "1.0.0",
  "description": "Validate an ISO‑8601 timestamp and print a normalized UTC ISO string",
  "type": "module",
  "main": "dist/index.js",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "ts-node src/index.ts"
  },
  "dependencies": {
    "validator": "13.9.0"
  },
  "devDependencies": {
    "typescript": "5.3.3",
    "ts-node": "10.9.2"
  }
}
```

---

### `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "node",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  }
}
```

---

### `src/index.ts`

```ts
import validator from "validator";

/**
 * CLI usage:
 *   npx ts-node src/index.ts <ISO-8601 timestamp>
 *   or after build:  npm start -- <ISO-8601 timestamp>
 */

const raw = process.argv[2];

if (!raw) {
  console.error("Usage: <script> <ISO-8601 timestamp>");
  process.exit(1);
}

// validator.isISO8601 with `strict:true` rejects loose forms (e.g. "2023-01")
if (!validator.isISO8601(raw, { strict: true })) {
  console.error("❌ Invalid ISO‑8601 timestamp");
  process.exit(1);
}

// `new Date` can still produce an invalid date for some edge cases
const date = new Date(raw);
if (Number.isNaN(date.getTime())) {
  console.error("❌ Unable to parse the timestamp");
  process.exit(1);
}

// `toISOString` returns a UTC‑normalized ISO‑8601 string
console.log(date.toISOString());
```

---

**How to run**

```bash
# install exact deps
npm ci

# quick test without building
npm run dev -- "2023-08-15T13:45:30+02:00"
# → 2023-08-15T11:45:30.000Z

# or build + run
npm run build
npm start -- "2023-08-15T13:45:30+02:00"
```

The script validates the input with **validator** and prints a normalized UTC ISO‑8601 timestamp.