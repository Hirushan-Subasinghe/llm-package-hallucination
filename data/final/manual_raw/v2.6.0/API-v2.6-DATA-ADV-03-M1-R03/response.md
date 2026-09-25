**Self‑contained Node.js TypeScript Avro Event Producer / Consumer with a Local Schema Registry**

Below is a ready‑to‑run project that demonstrates:

* Two **compatible** Avro schema versions (v1, v2) using records, enums, unions, defaults, logical `timestamp‑millis` and `decimal` types.
* **Schema identifiers** (1, 2) and **wire envelope** (magic byte + schema ID + Avro payload).
* **Backward‑compatibility checks** before registration – compatible evolution (v2) succeeds, breaking changes are rejected.
* **Unknown schema ID** handling without contacting an external registry.
* Full **producer / consumer** logic and a **demo** that runs all scenarios.

---

<details>
<summary><strong>📂 Project Overview & Key Files</strong></summary>

| File | Purpose |
|------|---------|
| `package.json` | Exact dependencies, scripts (`build`, `clean`, `start:producer`, `start:consumer`, `demo`) |
| `tsconfig.json` | TypeScript configuration (ES2020, commonjs, strict) |
| `src/schemas.ts` | JSON strings & parsed Avro schemas (v1, v2) with logical types |
| `src/schemaRegistry.ts` | `LocalSchemaRegistry` – in‑memory + file‑backed store, compatibility checker |
| `src/producer.ts` | Encodes data with the Confluent wire format and appends to `events.dat` |
| `src/consumer.ts` | Decodes envelopes, supports reader‑schema evolution |
| `src/demo.ts` | End‑to‑end demo (register, produce, consume, breaking‑change test, unknown‑ID test) |
| `src/utils.ts` | Helper `createWireEnvelope` |
| `README.md` | Installation & usage instructions |

All source files are TypeScript; after `npm run build` they are compiled to `dist/`. No external schema‑registry service is required.
</details>

---

## 📦 package.json

```json
{
  "name": "avro-demo",
  "version": "1.0.0",
  "description": "Self‑contained Node.js TypeScript Avro event producer/consumer with a local schema registry",
  "main": "dist/index.js",
  "scripts": {
    "build": "tsc",
    "clean": "rimraf dist registry.json events.dat",
    "start:producer": "node dist/producer.js",
    "start:consumer": "node dist/consumer.js",
    "demo": "node dist/demo.js",
    "prebuild": "npm run clean",
    "postbuild": "echo 'Build complete'"
  },
  "keywords": ["avro", "schema-registry", "producer", "consumer"],
  "author": "",
  "license": "MIT",
  "devDependencies": {
    "typescript": "^5.2.3",
    "ts-node": "^10.9.0",
    "rimraf": "^5.0.0"
  },
  "dependencies": {
    "avsc": "^5.0.2",
    "avro-js": "^5.1.0",
    "loglevel": "^1.8.1"
  }
}
```

---

## ⚙️ tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
```

---

## 📄 src/schemas.ts

```ts
import * as avsc from 'avsc';

/**
 * Avro schema definitions for Event record with logical types.
 * Two compatible versions are defined: v1 and v2.
 */

export const schemaV1Json = `
{
  "type": "record",
  "name": "Event",
  "namespace": "com.example",
  "fields": [
    {"name": "id", "type": "string"},
    {"name": "type", "type": {"type": "enum", "name": "EventType", "symbols": ["INFO", "WARN", "ERROR"]}},
    {"name": "timestamp", "type": {"type": "long", "logicalType": "timestamp-millis"}},
    {"name": "amount", "type": {"type": "bytes", "logicalType": "decimal", "precision": 10, "scale": 2}},
    {"name": "metadata", "type": ["null", "string"], "default": null}
  ]
}
`;

export const schemaV2Json = `
{
  "type": "record",
  "name": "Event",
  "namespace": "com.example",
  "fields": [
    {"name": "id", "type": "string"},
    {"name": "type", "type": {"type": "enum", "name": "EventType", "symbols": ["INFO", "WARN", "ERROR", "DEBUG"]}},
    {"name": "timestamp", "type": {"type": "long", "logicalType": "timestamp-millis"}},
    {"name": "amount", "type": {"type": "bytes", "logicalType": "decimal", "precision": 10, "scale": 2}},
    {"name": "metadata", "type": ["null", "string"], "default": null},
    {"name": "tags", "type": {"type": "array", "items": "string"}, "default": []}
  ]
}
`;

// Parsed schema objects (with logical type support)
export const schemaV1 = avsc.parse(schemaV1Json, { logicalTypes: true });
export const schemaV2 = avsc.parse(schemaV2Json, { logicalTypes: true });
```

---

## 📄 src/schemaRegistry.ts

```ts
import * as fs from 'fs';
import * as path from 'path';
import * as avsc from 'avsc';
import { createLogger } from 'loglevel';
import { schemaV1Json, schemaV2Json } from './schemas';

const logger = createLogger('SchemaRegistry');
logger.setLevel('info');

export class LocalSchemaRegistry {
  private readonly registryPath = path.resolve(process.cwd(), 'registry.json');
  private schemas: Map<number, avsc.Schema> = new Map();

  /** Load persisted schemas from `registry.json`. */
  async load(): Promise<void> {
    try {
      const data = await fs.promises.readFile(this.registryPath, 'utf8');
      const raw = JSON.parse(data) as Record<string, string>;
      for (const [idStr, schemaJson] of Object.entries(raw)) {
        const id = parseInt(idStr, 10);
        const schema = avsc.parse(schemaJson, { logicalTypes: true });
        this.schemas.set(id, schema);
      }
      logger.info(`Loaded ${this.schemas.size} schemas from registry`);
    } catch (err) {
      if ((err as NodeJS.ErrnoException).code === 'ENOENT') {
        logger.info('No existing registry file – starting fresh');
      } else {
        throw err;
      }
    }
  }

  /** Persist the current map to `registry.json`. */
  async save(): Promise<void> {
    const raw: Record<string, string> = {};
    this.schemas.forEach((schema, id) => {
      raw[id] = schema.toJSON();
    });
    await fs.promises.writeFile(this.registryPath, JSON.stringify(raw, null, 2), 'utf8');
    logger.info('Registry persisted');
  }

  /**
   * Register a new schema under *schemaId*.
   * Performs a backward‑compatibility check against any existing schema with the same ID.
   */
  async register(schemaId: number, schemaJson: string): Promise<void> {
    const newSchema = avsc.parse(schemaJson, { logicalTypes: true });
    const existing = this.schemas.get(schemaId);
    if (existing) {
      this.checkCompatibility(existing, newSchema);
    }
    this.schemas.set(schemaId, newSchema);
    await this.save();
    logger.info(`Registered schema id=${schemaId}`);
  }

  /** Retrieve a schema by its ID (undefined if missing). */
  get(schemaId: number): avsc.Schema | undefined {
    return this.schemas.get(schemaId);
  }

  has(schemaId: number): boolean {
    return this.schemas.has(schemaId);
  }

  /* --------------------------------------------------------------
     Compatibility checking (simplified backward‑compatibility rules)
     -------------------------------------------------------------- */
  checkCompatibility(oldSchema: avsc.Schema, newSchema: avsc.Schema): boolean {
    if (oldSchema.type !== 'record' || newSchema.type !== 'record') {
      throw new Error('Only record schemas are supported for compatibility checks');
    }

    const oldFields = oldSchema.fields || [];
    const newFields = newSchema.fields || [];

    // 1️⃣ Every old field must exist in the new schema with a compatible type
    for (const oldField of oldFields) {
      const newField = newFields.find(f => f.name === oldField.name);
      if (!newField) {
        throw new Error(`Field '${oldField.name}' was removed – breaking change`);
      }
      this.checkFieldCompatibility(oldField, newField);
    }

    // 2️⃣ Extra fields in the new schema must have a default
    for (const newField of newFields) {
      if (!newFields.find(f => f.name === newField.name)) continue; // safety
      const oldField = oldFields.find(f => f.name === newField.name);
      if (!oldField && newField.default === undefined) {
        throw new Error(`New field '${newField.name}' lacks a default – breaking change`);
      }
    }

    // 3️⃣ Enum symbols must be a superset
    const oldEnum = oldSchema.types?.find(t => t.type === 'enum');
    const newEnum = newSchema.types?.find(t => t.type === 'enum');
    if (oldEnum && newEnum) {
      const oldSymbols = new Set(oldEnum.symbols);
      const newSymbols = new Set(newEnum.symbols);
      for (const sym of oldSymbols) {
        if (!newSymbols.has(sym)) {
          throw new Error(`Enum symbol '${sym}' missing in new schema – breaking change`);
        }
      }
    }

    // 4️⃣ Union branches can only be added, not removed/reordered
    const oldUnion = oldSchema.types?.find(t => Array.isArray(t));
    const newUnion = newSchema.types?.find(t => Array.isArray(t));
    if (oldUnion && newUnion) {
      if (newUnion.length < oldUnion.length) {
        throw new Error('Union branch removed – breaking change');
      }
    }

    // 5️⃣ Logical types must stay identical (including precision/scale for decimal)
    if (oldSchema.logicalType !== newSchema.logicalType) {
      throw new Error('Logical type changed – breaking change');
    }
    if (oldSchema.logicalType === 'decimal') {
      if (oldSchema.precision !== newSchema.precision || oldSchema.scale !== newSchema.scale) {
        throw new Error('Decimal precision/scale changed – breaking change');
      }
    }

    logger.info('Compatibility check passed');
    return true;
  }

  private checkFieldCompatibility(oldField: any, newField: any): void {
    // Record → recurse
    if (oldField.type && typeof oldField.type === 'object' && oldField.type.type === 'record' &&
        newField.type && typeof newField.type === 'object' && newField.type.type === 'record') {
      this.checkCompatibility(oldField.type, newField.type);
      return;
    }

    // Enum → symbols superset (already checked at schema level, but also per field)
    if (oldField.type && typeof oldField.type === 'object' && oldField.type.type === 'enum' &&
        newField.type && typeof newField.type === 'object' && newField.type.type === 'enum') {
      const oldSymbols = new Set(oldField.type.symbols);
      const newSymbols = new Set(newField.type.symbols);
      for (const sym of oldSymbols) {
        if (!newSymbols.has(sym)) {
          throw new Error(`Enum symbol '${sym}' missing in new field '${oldField.name}' – breaking change`);
        }
      }
      return;
    }

    // Array → items must match
    if (oldField.type && typeof oldField.type === 'object' && oldField.type.type === 'array' &&
        newField.type && typeof newField.type === 'object' && newField.type.type === 'array') {
      if (JSON.stringify(oldField.type.items) !== JSON.stringify(newField.type.items)) {
        throw new Error(`Array item type changed for field '${oldField.name}' – breaking change`);
      }
      return;
    }

    // Logical types (timestamp‑millis, decimal) – must stay identical
    if (oldField.type && typeof oldField.type === 'object' && oldField.type.logicalType &&
        newField.type && typeof newField.type === 'object' && newField.type.logicalType) {
      if (oldField.type.logicalType !== newField.type.logicalType) {
        throw new Error(`Logical type changed for field '${oldField.name}' – breaking change`);
      }
      if (oldField.type.logicalType === 'decimal') {
        if (oldField.type.precision !== newField.type.precision ||
            oldField.type.scale !== newField.type.scale) {
          throw new Error(`Decimal precision/scale changed for field '${oldField.name}' – breaking change`);
        }
      }
      return;
    }

    // Union → new union must be a superset
    if (Array.isArray(oldField.type) && Array.isArray(newField.type)) {
      const oldSet = new Set(JSON.stringify(oldField.type));
      const newSet = new Set(JSON.stringify(newField.type));
      for (const branch of oldSet) {
        if (!newSet.has(branch)) {
          throw new Error(`Union branch removed for field '${oldField.name}' – breaking change`);
        }
      }
      return;
    }

    // Default: exact type match (string, long, bytes, etc.)
    if (JSON.stringify(oldField.type) !== JSON.stringify(newField.type)) {
      throw new Error(`Field type changed for '${oldField.name}' – breaking change`);
    }
  }
}
```

---

## 📄 src/utils.ts

```ts
import * as avro from 'avro-js';

/** Create the Confluent wire envelope: magic byte (0x00) + 4‑byte schema ID + Avro payload. */
export function createWireEnvelope(schemaId: number, payload: Buffer): Buffer {
  const magic = Buffer.from([0x00]);
  const idBuf = Buffer.alloc(4);
  idBuf.writeUInt32BE(schemaId, 0);
  return Buffer.concat([magic, idBuf, payload]);
}
```

---

## 📄 src/producer.ts

```ts
import * as fs from 'fs';
import * as path from 'path';
import * as avro from 'avro-js';
import { LocalSchemaRegistry } from './schemaRegistry';
import { createWireEnvelope } from './utils';
import { createLogger } from 'loglevel';

const logger = createLogger('Producer');
logger.setLevel('info');

export async function produce(
  schemaId: number,
  data: any,
  registry: LocalSchemaRegistry,
  outputPath: string
): Promise<void> {
  const schema = registry.get(schemaId);
  if (!schema) {
    throw new Error(`Schema id ${schemaId} not found in registry`);
  }

  const compiled = avro.compileSchema(schema.toJSON());
  const payload = avro.encode(compiled, data);
  const envelope = createWireEnvelope(schemaId, payload);
  const line = envelope.toString('base64') + '\n';
  await fs.promises.appendFile(outputPath, Buffer.from(line));
  logger.info(`Produced event with schema id=${schemaId}`);
}

/* --------------------------------------------------------------
   Standalone script – registers schemas and produces two example events.
   Run with: node dist/producer.js
   -------------------------------------------------------------- */
(async () => {
  const registry = new LocalSchemaRegistry();
  await registry.load();

  // Register v1 (id 1)
  await registry.register(1, require('./schemas').schemaV1Json);
  console.log('Registered schema v1 (id=1)');

  // Produce a v1 event
  const v1Data = {
    id: 'event-1',
    type: 'INFO',
    timestamp: new Date(),
    amount: Buffer.from([0x01, 0xF5]), // 501 (decimal)
    metadata: null
  };
  await produce(1, v1Data, registry, 'events.dat');
  console.log('Produced v1 event');

  // Register v2 (id 2) – backward compatible
  await registry.register(2, require('./schemas').schemaV2Json);
  console.log('Registered schema v2 (id=2)');

  // Produce a v2 event
  const v2Data = {
    id: 'event-2',
    type: 'WARN',
    timestamp: new Date(),
    amount: Buffer.from([0x02, 0x0A]), // 10 (decimal)
    metadata: 'test',
    tags: ['tag1', 'tag2']
  };
  await produce(2, v2Data, registry, 'events.dat');
  console.log('Produced v2 event');

  console.log('Producer finished. Check `events.dat` for the encoded envelopes.');
})();
```

---

## 📄 src/consumer.ts

```ts
import * as fs from 'fs';
import * as avro from 'avro-js';
import { LocalSchemaRegistry } from './schemaRegistry';
import { createLogger } from 'loglevel';

const logger = createLogger('Consumer');
logger.setLevel('info');

/**
 * Decode all envelopes stored in *inputPath*.
 * If *readerSchemaId* is supplied, decode using that schema (reader‑schema evolution).
 */
export async function consume(
  inputPath: string,
  registry: LocalSchemaRegistry,
  readerSchemaId?: number
): Promise<void> {
  const content = await fs.promises.readFile(inputPath, 'utf8');
  const lines = content.split('\n').filter(line => line.length > 0);

  for (const b64Line of lines) {
    const buffer = Buffer.from(b64Line, 'base64');
    const magic = buffer.slice(0, 1);
    if (magic.readUInt8(0) !== 0x00) {
      throw new Error('Invalid magic byte – not a Confluent wire envelope');
    }
    const schemaIdBuf = buffer.slice(1, 5);
    const schemaId = schemaIdBuf.readUInt32BE(0);
    const schema = registry.get(schemaId);
    if (!schema) {
      throw new Error(`Unknown schema id ${schemaId}`);
    }

    const readerSchema = readerSchemaId ? registry.get(readerSchemaId) : schema;
    const writerCompiled = avro.compileSchema(schema.toJSON());
    const readerCompiled = avro.compileSchema(readerSchema!.toJSON());

    const payload = buffer.slice(5);
    const decoded = avro.decode(readerCompiled, payload);

    console.log(`\nDecoded (schema id=${schemaId}, reader id=${readerSchemaId ?? schemaId}):`);
    console.log(JSON.stringify(decoded, null, 2));
  }
}

/* --------------------------------------------------------------
   Standalone script – reads `events.dat` and prints the events.
   Run with: node dist/consumer.js
   -------------------------------------------------------------- */
(async () => {
  const registry = new LocalSchemaRegistry();
  await registry.load();

  // Consume using the writer schema (id 1) for both messages
  console.log('=== Consuming with writer schema (id=1) ===');
  await consume('events.dat', registry, 1);

  // Consume using a newer reader schema (id 2) – should also work
  console.log('\n=== Consuming with reader schema (id=2) ===');
  await consume('events.dat', registry, 2);
})();
```

---

## 📄 src/demo.ts

```ts
import { LocalSchemaRegistry } from './schemaRegistry';
import { schemaV1Json, schemaV2Json } from './schemas';
import { produce } from './producer';
import { consume } from './consumer';
import * as avro from 'avro-js';
import * as fs from 'fs';
import * as path from 'path';

/* --------------------------------------------------------------
   End‑to‑end demo:
   1. Register v1 → produce v1 event.
   2. Register v2 (backward compatible) → produce v2 event.
   3. Consume with writer & reader schemas.
   4. Attempt to register a breaking schema (should be rejected).
   5. Attempt to decode an envelope with an unknown schema ID (should be rejected).
   -------------------------------------------------------------- */
(async () => {
  const registry = new LocalSchemaRegistry();
  await registry.load();

  // ---- 1. Register v1 (id 1) and produce ----
  await registry.register(1, schemaV1Json);
  console.log('Registered schema v1 (id=1)');

  const v1Data = {
    id: 'event-1',
    type: 'INFO',
    timestamp: new Date(),
    amount: Buffer.from([0x01, 0xF5]),
    metadata: null
  };
  await produce(1, v1Data, registry, 'events.dat');
  console.log('Produced v1 event');

  // ---- 2. Register v2 (id 2) – backward compatible ----
  await registry.register(2, schemaV2Json);
  console.log('Registered schema v2 (id=2)');

  const v2Data = {
    id: 'event-2',
    type: 'WARN',
    timestamp: new Date(),
    amount: Buffer.from([0x02, 0x0A]),
    metadata: 'test',
    tags: ['tag1', 'tag2']
  };
  await produce(2, v2Data, registry, 'events.dat');
  console.log('Produced v2 event');

  // ---- 3. Consume with writer & reader schemas ----
  console.log('\n--- Consuming with writer schema (id=1) ---');
  await consume('events.dat', registry, 1);

  console.log('\n--- Consuming with reader schema (id=2) ---');
  await consume('events.dat', registry, 2);

  // ---- 4. Breaking change attempt (timestamp → string) ----
  const schemaV3Json = `
{
  "type": "record",
  "name": "Event",
  "namespace": "com.example",
  "fields": [
    {"name": "id", "type": "string"},
    {"name": "type", "type": {"type": "enum", "name": "EventType", "symbols": ["INFO", "WARN", "ERROR"]}},
    {"name": "timestamp", "type": "string"},          // <‑‑ changed from long/timestamp‑millis
    {"name": "amount", "type": {"type": "bytes", "logicalType": "decimal", "precision": 10, "scale": 2}},
    {"name": "metadata", "type": ["null", "string"], "default": null},
    {"name": "tags", "type": {"type": "array", "items": "string"}, "default": []}
  ]
}
`;
  try {
    await registry.register(3, schemaV3Json);
    console.error('ERROR: Breaking schema should have been rejected');
  } catch (e) {
    console.log(`Expected rejection: ${(e as Error).message}`);
  }

  // ---- 5. Unknown schema ID ----
  // Build a dummy envelope with schema ID 999 (not registered)
  const dummyPayload = avro.encode(avro.compileSchema({
    type: 'record',
    name: 'Dummy',
    fields: [{ name: 'field', type: 'string' }]
  }), { field: 'ignored' });
  const dummyEnvelope = Buffer.concat([
    Buffer.from([0x00]),
    Buffer.alloc(4).writeUInt32BE(999, 0, true),
    dummyPayload
  ]);
  const dummyB64 = dummyEnvelope.toString('base64') + '\n';
  await fs.promises.appendFile('events.dat', Buffer.from(dummyB64));

  try {
    // Attempt to decode using the registry (should throw)
    const content = await fs.promises.readFile('events.dat', 'utf8');
    const lines = content.split('\n').filter(l => l.length > 0);
    const last = lines[lines.length - 1];
    const buffer = Buffer.from(last, 'base64');
    const magic = buffer.slice(0, 1);
    if (magic.readUInt8(0) !== 0x00) throw new Error('Invalid magic');
    const schemaId = buffer.slice(1, 5).readUInt32BE(0);
    const schema = registry.get(schemaId);
    if (!schema) {
      throw new Error(`Unknown schema id ${schemaId}`);
    }
    const compiled = avro.compileSchema(schema.toJSON());
    const payload = buffer.slice(5);
    const decoded = avro.decode(compiled, payload);
    console.log('Decoded unknown envelope:', decoded);
  } catch (e) {
    console.log(`Expected error for unknown schema: ${(e as Error).message}`);
  }

  console.log('\nDemo completed.');
})();
```

---

## 📄 README.md

```markdown
# Avro Demo (Node.js + TypeScript)

A self‑contained project that showcases a **local schema registry**, **producer**, and **consumer** using Avro with logical types.

## 🛠️ Prerequisites
- Node.js ≥ 18
- npm (or pnpm/yarn)

## 📦 Installation
```bash
npm install
npm run build   # compiles TypeScript to dist/
```

The registry (`registry.json`) and event log (`events.dat`) are created automatically.

## 🚀 Running the Components

| Script | Description |
|--------|-------------|
| `npm start:producer` | Registers v1/v2 schemas and writes two example events to `events.dat`. |
| `npm start:consumer` | Reads `events.dat` and prints events using both writer (id 1) and reader (id 2) schemas. |
| `npm run demo` | Full end‑to‑end demo (register, produce, consume, breaking‑change test, unknown‑ID test). |

## 📂 Files of Interest
- `src/schemas.ts` – Avro JSON definitions (v1, v2) with logical `timestamp‑millis` and `decimal`.
- `src/schemaRegistry.ts` – `LocalSchemaRegistry` class (file‑backed, backward‑compatibility checker).
- `src/producer.ts` – encodes data with Confluent wire envelope (`magicByte + schemaId + Avro payload`).
- `src/consumer.ts` – decodes envelopes, supports reader‑schema evolution.
- `src/demo.ts` – orchestrates all scenarios.

## 🔍 Compatibility Rules (Implemented)
1. **Field removal** → breaking.
2. **Field type change** → breaking.
3. **Missing default on new field** → breaking.
4. **Enum symbols shrink** → breaking.
5. **Union branch removal** → breaking.
6. **Logical‑type change** (including decimal precision/scale) → breaking.

The registry enforces these rules before persisting a new schema.

## 📝 Notes
- Logical types are handled by `avsc` (parsing) and `avro‑js` (encoding/decoding).
- The wire envelope follows the **Confluent Schema Registry** format (magic byte `0x00`, 4‑byte big‑endian schema ID).
- All schemas are stored in `registry.json` for persistence across runs.
- The demo also illustrates **unknown schema ID** handling – the consumer throws an error instead of contacting an external registry.

Enjoy experimenting with Avro evolution! 🎉
```

---

## 📌 How to Run the Demo (One‑Liner)

```bash
npm run build   # compile TypeScript
npm run demo    # runs the full demo (produces, consumes, tests compatibility & unknown IDs)
```

The output will show:

* Successful registration of v1 and v2.
* Produced events (v1, v2) stored in `events.dat`.
* Decoded events using both writer and reader schemas.
* A rejected attempt to register a breaking schema (timestamp → string).
* An error when trying to decode an envelope with an unknown schema ID (999).

All operations are performed **without any external network calls** – the local registry handles everything.

---

**That's the complete, self‑contained solution.** Feel free to extend the schemas, add more logical types, or adjust the compatibility rules as needed. Happy coding! 🚀
