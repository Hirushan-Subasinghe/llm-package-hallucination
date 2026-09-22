```json
{
  "name": "ts-iso-validator",
  "version": "1.0.0",
  "description": "Validates ISO-8601 timestamp and prints normalized UTC version.",
  "main": "dist/index.js",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "ts-node src/index.ts"
  },
  "keywords": [],
  "author": "",
  "license": "ISC",
  "dependencies": {
    "date-fns": "^2.29.7"
  },
  "devDependencies": {
    "typescript": "^5.0.3",
    "ts-node": "^10.9.1"
  }
}
```

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  }
}
```

```typescript
#!/usr/bin/env node
import { parseISO, isValid } from 'date-fns';

const input = process.argv[2];

if (!input) {
  console.error('Error: No timestamp provided.');
  console.log('Usage: npm start <iso-timestamp>');
  process.exit(1);
}

const date = parseISO(input);

if (!isValid(date)) {
  console.error(`Invalid ISO-8601 timestamp: ${input}`);
  process.exit(1);
}

const normalized = date.toISOString();
console.log(normalized);
```