**package.json**
```json
{
  "name": "iso-timestamp-normalizer",
  "version": "1.0.0",
  "description": "Validate an ISO‑8601 timestamp and print a normalized UTC timestamp",
  "main": "dist/index.js",
  "scripts": {
    "build": "tsc",
    "start": "ts-node index.ts"
  },
  "dependencies": {
    "date-fns": "3.6.0"
  },
  "devDependencies": {
    "typescript": "5.4.5",
    "ts-node": "10.9.2",
    "@types/node": "20.12.7"
  },
  "engines": { "node": ">=20" }
}
```

**index.ts**
```ts
import { parseISO, isValid, formatISO } from 'date-fns';

const input = process.argv[2];
if (!input) {
  console.error('Usage: npm start -- <ISO-8601 timestamp>');
  process.exit(1);
}

const date = parseISO(input);
if (!isValid(date)) {
  console.error(`Invalid ISO-8601 timestamp: ${input}`);
  process.exit(1);
}

// Normalized UTC timestamp (e.g. 2024-06-15T12:34:56.000Z)
console.log(formatISO(date));
```

**Run**

```bash
npm install          # installs exact versions
npm start -- "2024-06-15T12:34:56.789+02:00"
# → 2024-06-15T10:34:56.789Z
```