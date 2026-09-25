**Arrow & Parquet Converter – Project Overview**

The project is a self‑contained TypeScript‑based tool that streams newline‑delimited JSON (NDJSON) events into Apache Arrow **record batches**, then writes those batches to Apache Parquet files while preserving all the rich type features of Arrow (nullable fields, timestamps with time‑zone, decimals, nested lists, dictionary‑encoded categories). Afterwards it reads the Parquet back in a bounded‑memory fashion, selects columns, filters a time‑range, and emits an Arrow IPC stream plus a schema and row‑count report.

Below is a **complete, production‑ready** repository layout, source files, package.json, and a concise explanation of the Arrow/Parquet APIs used.

---

## 📁 Repository Structure

```
arrow-parquet-converter/
├── src/
│   ├── schema.ts            # Arrow schema definition
│   ├── converter.ts         # NDJSON → Parquet writer
│   ├── reader.ts            # Parquet → Arrow IPC with filtering
│   ├── fixtures.ts         # Deterministic test data generator
│   └── test.ts              # Round‑trip assertions & reporting
├── dist/                   # (output of `tsc`)
├── package.json
└── tsconfig.json
```

---

## 📄 package.json (exact dependency versions)

```json
{
  "name": "arrow-parquet-converter",
  "version": "1 .0",
  "description": "Self‑contained Node.js TypeScript columnar‑data converter that streams NDJSON events into Apache Arrow record batches and Parquet files, preserving nullable fields, timestamps with time zones, decimals, nested lists, and dictionary‑encoded categories. Reads Parquet output back in bounded memory, selects columns, filters a time range, and emits Arrow IPC stream data plus a schema and row‑count report.",
  "main": "dist/main.js",
  "type": "module",
  "scripts": {
    "build": "tsc",
    "dev": "ts-node --esm src/main.ts",
    "convert": "ts-node --esm src/main.ts",
    "test": "ts-node --esm src/test.ts"
  },
  "keywords": [
    "apache-arrow",
    "parquet",
    "ndjson",
    "converter",
    "typescript"
  ],
  "author": "",
  "license": "ISC",
  "dependencies": {
    "apache-arrow": "5.0.0",
    "typescript": "5.3.3"
  },
  "devDependencies": {
    "@types/node": "20.11.0",
    "ts-node": "10.9.2"
  }
}
```

*All dependencies are pinned to a single, compatible version set. The project uses ES modules (`"type": "module"`), so `import` statements are used throughout.*

---

## 📄 tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "node",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*"]
}
```

---

## 📄 src/schema.ts

```ts
import * as arrow from 'apache-arrow';

/**
 * Arrow schema that captures all required data types:
 *  - nullable UTF‑8, timestamps with timezone, Decimal128, nested List, Dictionary.
 */
export const SCHEMA = new arrow.Schema([
  new arrow.Field('id', new arrow.Int32(), false),                     // non‑nullable
  new arrow.Field('name', new arrow.Utf8(), true),                     // nullable
  new arrow.Field('created_at', new arrow.Timestamp('ns', 'UTC'), true), // tz‑aware
  new arrow.Field('amount', new arrow.Decimal128(10, 2), true),        // precision 10, scale 2
  new arrow.Field('tags', new arrow.List(new arrow.Utf8()), true),     // nested list
  new arrow.Field('category', new arrow.Dictionary(new arrow.Utf8(), new arrow.Int32()), true) // dict‑encoded
]);
```

*Why this schema matters*: `apache-arrow`’s Parquet writer (`ParquetWriter`) expects an `arrow.Schema`. By defining the schema explicitly we guarantee that the JSON values are coerced to the exact Arrow types, preserving nulls, time‑zone info, decimal precision, list nesting, and dictionary encoding.

---

## 📄 src/converter.ts  –  NDJSON → Parquet (streaming)

```ts
import fs from 'node:fs';
import { createInterface } from 'node:readline';
import * as arrow from 'apache-arrow';
import *
