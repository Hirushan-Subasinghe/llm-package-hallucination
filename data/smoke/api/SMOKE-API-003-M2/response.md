```json
{
  "name": "ts-timestamp",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "start": "tsx src/index.ts"
  },
  "dependencies": {
    "date-fns": "3.6.0"
  },
  "devDependencies": {
    "typescript": "5.5.4",
    "tsx": "4.19.0"
  }
}
```

```typescript
// src/index.ts
import { parseISO, formatISO } from "date-fns";

const input = process.argv[2];
if (!input) {
  console.error("Usage: tsx src/index.ts <ISO-8601 timestamp>");
  process.exit(1);
}

try {
  const date = parseISO(input);
  if (isNaN(date.getTime())) {
    throw new Error("Invalid date");
  }
  console.log(formatISO(date, { representation: "extended" }));
} catch (e) {
  console.error("Invalid ISO-8601 timestamp:", (e as Error).message);
  process.exit(1);
}
```