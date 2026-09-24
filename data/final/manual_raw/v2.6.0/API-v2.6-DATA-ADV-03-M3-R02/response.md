## 📦 Self‑contained Node.js + TypeScript Avro producer / consumer  
**All you need is a single folder, `npm install`, and two npm scripts.**  
The project contains a **local in‑memory schema‑registry adapter** that:

* assigns numeric schema IDs,  
* stores versions,  
* runs **backward‑compatibility checks** before registration (using `avro‑compatibility`),  
* encodes messages with the **Confluent wire envelope** (`0x00` + 4‑byte id),  
* resolves older writer schemas against the **current reader schema** (using `avsc`).

---

<details open>
<summary>🗂️ Directory layout</summary>

```
avro-demo/
├─ src/
│  ├─ registry.ts          # local schema‑registry implementation
│  ├─ schemas.ts           # schema definitions & IDs
│  ├─ producer.ts          # Avro producer (writes to stdout)
│  └─ consumer.ts          # Avro consumer (reads from stdin)
├─ tsconfig.json
├─ package.json
└─ README.md
```
</details>

--- 

## 1️⃣ `package.json` – exact versions & scripts  

```json
{
  "name": "avro-demo",
  "version": "1.0.0",
  "description": "Self‑contained Avro producer/consumer with a local schema‑registry adapter (TS)",
  "main": "dist/index.js",
  "type": "module",
  "scripts": {
    "build": "tsc",
    "producer": "ts-node src/producer.ts",
    "consumer": "ts-node src/consumer.ts",
    "start": "npm-run-all --parallel producer consumer"
  },
  "author": "Your Name",
  "license": "MIT",
  "dependencies": {
    "avsc": "5.7.9",
    "avro-compatibility": "1.2.0"
  },
  "devDependencies": {
    "ts-node": "10.9.2",
    "typescript": "5.4.5",
    "npm-run-all": "4.1.5"
  }
}
```

* **`avsc`** – core Avro (serialization, logical types, resolver).  
* **`avro-compatibility`** – compatibility‑checking API (`CompatibilityChecker`, `CompatibilityMode`).  
* **`ts-node` / `typescript`** – run TS directly.  
* **`npm-run-all`** – optional convenience to run producer & consumer together.

--- 

## 2️⃣ TypeScript configuration (`tsconfig.json`)

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "moduleResolution": "node",
    "esModuleInterop": true,
    "strict": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "outDir": "dist"
  },
  "include": ["src/**/*.ts"]
}
```

--- 

## 3️⃣ Schema definitions (`src/schemas.ts`)

```ts
// src/schemas.ts
import type { Schema } from 'avsc';

// ---------- Version 1 ----------
export const USER_EVENT_V1: Schema = {
  type: 'record',
  name: 'UserEvent',
  namespace: 'com.example',
  fields: [
    { name: 'id', type: 'string' },
    {
      name: 'eventTime',
      type: {
        type: 'long',
        logicalType: 'timestamp-millis'
      }
    },
    {
      name: 'amount',
      type: {
        type: 'bytes',
        logicalType: 'decimal',
        precision: 10,
        scale: 2
      }
    },
    {
      name: 'status',
      type: {
        type: 'enum',
        name: 'Status',
        symbols: ['ACTIVE', 'INACTIVE']
      }
    },
    {
      name: 'details',
      type: ['null', 'string'],
      default: null
    }
  ]
} as const;

// ---------- Version 2 (compatible evolution) ----------
export const USER_EVENT_V2: Schema = {
  type: 'record',
  name: 'UserEvent',
  namespace: 'com.example',
  fields: [
    { name: 'id', type: 'string' },
    {
      name: 'eventTime',
      type: {
        type: 'long',
        logicalType: 'timestamp-millis'
      }
    },
    {
      name: 'amount',
      type: {
        type: 'bytes',
        logicalType: 'decimal',
        precision: 10,
        scale: 2
      }
    },
    {
      name: 'status',
      type: {
        type: 'enum',
        name: 'Status',
        // added a new symbol – still backward compatible
        symbols: ['ACTIVE', 'INACTIVE', 'SUSPENDED']
      }
    },
    {
      name: 'details',
      type: ['null', 'string'],
      default: null
    },
    {
      // NEW optional field with a default value – backward compatible
      name: 'metadata',
      type: {
        type: 'map',
        values: 'string'
      },
      default: {}
    }
  ]
} as const;

// ---------- Schema IDs (simulated registry IDs) ----------
export const SCHEMA_IDS = {
  USER_EVENT_V1: 1,
  USER_EVENT_V2: 2
} as const;
```

*Both versions use**:

* **Enums** (`Status`) – V2 adds a symbol.  
* **Unions** (`null` | `string`).  
* **Logical types** – `timestamp-millis` and `decimal`.  
* **Defaults** – `details` defaults to `null`, `metadata` defaults to `{}` in V2.

--- 

## 4️⃣ Local schema‑registry adapter (`src/registry.ts`)

```ts
// src/registry.ts
import { CompatibilityChecker, CompatibilityMode } from 'avro-compatibility';
import type { Schema } from 'avsc';
import { USER_EVENT_V1, USER_EVENT_V2, SCHEMA_IDS } from './schemas';

/**
 * In‑memory registry that mimics Confluent's Schema Registry.
 * - schemaId → { schema, version }
 * - subject (here we have a single subject) → ordered list of schemas
 */
export class LocalRegistry {
  private idCounter = 3; // start after our pre‑registered IDs
  private schemasById = new Map<number, Schema>();
  private versions: Schema[] = [];

  constructor() {
    // pre‑register the two example schemas
    this.registerPredefined(USER_EVENT_V1, SCHEMA_IDS.USER_EVENT_V1);
    this.registerPredefined(USER_EVENT_V2, SCHEMA_IDS.USER_EVENT_V2);
  }

  /** Register a schema that is already known (used for the demo bootstrap). */
  private registerPredefined(schema: Schema, id: number) {
    this.schemasById.set(id, schema);
    this.versions.push(schema);
  }

  /** Register a new schema version after compatibility check. */
  public register(schema: Schema, mode: CompatibilityMode = CompatibilityMode.BACKWARD): number {
    // 1️⃣ Compatibility check against *all* previous versions (transitive)
    const compatible = CompatibilityChecker
      .check(schema)
      .against(this.versions.slice().reverse()) // newest first
      .withCompatibility(mode)
      .check();

    if (!compatible) {
      throw new Error(`Schema is not ${CompatibilityMode[mode]} compatible with existing versions`);
    }

    // 2️⃣ Assign a new ID and store
    const newId = this.idCounter++;
    this.schemasById.set(newId, schema);
    this.versions.push(schema);
    return newId;
  }

  /** Retrieve a schema by its numeric ID – throws if unknown. */
  public getSchema(id: number): Schema {
    const schema = this.schemasById.get(id);
    if (!schema) {
      throw new Error(`Unknown schema ID ${id}`);
    }
    return schema;
  }

  /** Get the *latest* registered schema (reader schema). */
  public getLatestSchema(): Schema {
    return this.versions[this.versions.length - 1];
  }
}

/** Singleton instance used by producer & consumer */
export const registry = new LocalRegistry();
```

### How compatibility is enforced  

* **`CompatibilityChecker.check(schema).against(previousVersions).withCompatibility(CompatibilityMode.BACKWARD).check()`**  
  * Returns `true` only if **all** older versions can be read by the new schema (standard “backward” rule).  
* The demo registers the two initial schemas directly (they are known to be compatible).  
* You can try to register a breaking schema later – the call will throw.

--- 

## 5️⃣ Producer (`src/producer.ts`)

```ts
// src/producer.ts
import { registry } from './registry';
import { SCHEMA_IDS, USER_EVENT_V1 } from './schemas';
import avro from 'avsc';
import { Buffer } from 'node:buffer';

// Helper: encode a value with the Confluent wire format
function encodeMessage(schemaId: number, value: unknown, writerSchema: object): Buffer {
  const type = avro.Type.forSchema(writerSchema);
  const payload = type.toBuffer(value); // Avro binary payload

  // Confluent envelope: magic byte (0) + 4‑byte big‑endian schema ID
  const header = Buffer.alloc(5);
  header.writeUInt8(0, 0);               // magic byte
  header.writeUInt32BE(schemaId, 1);     // schema id

  return Buffer.concat([header, payload]);
}

// Example event using **schema version 1**
const eventV1 = {
  id: 'user-123',
  eventTime: Date.now(),
  amount: Buffer.from([0x00, 0x00, 0x27, 0x10]), // 1000 → 10.00 with precision 10, scale 2
  status: 'ACTIVE',
  details: 'first login'
};

const message = encodeMessage(
  SCHEMA_IDS.USER_EVENT_V1,
  eventV1,
  USER_EVENT_V1
);

// For demo purposes we just write the base64 string to stdout
console.log(message.toString('base64'));
```

**Run:**  

```bash
npm run producer
# → prints a base64 string representing the Avro envelope
```

--- 

## 6️⃣ Consumer (`src/consumer.ts`)

```ts
// src/consumer.ts
import { registry } from './registry';
import avro from 'avsc';
import { Buffer } from 'node:buffer';
import * as readline from 'node:readline';

// Decode a Confluent envelope and resolve writer→reader schemas
function decodeMessage(buf: Buffer) {
  if (buf.length < 5) throw new Error('Message too short');
  const magic = buf.readUInt8(0);
  if (magic !== 0) throw new Error(`Unsupported magic byte ${magic}`);

  const schemaId = buf.readUInt32BE(1);
  const writerSchema = registry.getSchema(schemaId);
  const readerSchema = registry.getLatestSchema(); // current version

  // Create resolver that can read writer data with the newer reader schema
  const writerType = avro.Type.forSchema(writerSchema);
  const readerType = avro.Type.forSchema(readerSchema);
  const resolver = readerType.createResolver(writerType);

  const payload = buf.slice(5);
  return readerType.fromBuffer(payload, resolver);
}

// Read a base64 line from stdin, decode, and pretty‑print
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

rl.on('line', line => {
  try {
    const buf = Buffer.from(line.trim(), 'base64');
    const value = decodeMessage(buf);
    console.log('✅ Decoded event (reader = latest schema):');
    console.dir(value, { depth: null });
  } catch (e) {
    console.error('❌ Failed to decode:', (e as Error).message);
  }
});
```

**Run:**  

```bash
npm run consumer   # waits for a line on stdin
# In another terminal:
npm run producer | npm run consumer
```

The consumer automatically **resolves** the V1 writer schema (ID 1) against the **latest reader schema** (V2).  
Fields that exist only in V2 (`metadata`) appear with their default value (`{}`).

--- 

## 7️⃣ Demonstrating evolution & breaking changes  

### 7.1 ✅ Compatible evolution (already shown)

* Added enum symbol `SUSPENDED`.  
* Added optional field `metadata` with a default.  
Both pass the **backward** compatibility check, so registration succeeds.

### 7.2 ❌ Rejected breaking change  

Create a new incompatible schema (remove `details` without a default, change `amount` type).

```ts
// src/badSchema.ts (demo only)
import type { Schema } from 'avsc';
export const USER_EVENT_BAD: Schema = {
  type: 'record',
  name: 'UserEvent',
  namespace: 'com.example',
  fields: [
    { name: 'id', type: 'string' },
    // removed `details` field entirely – no default
    { name: 'eventTime', type: { type: 'long', logicalType: 'timestamp-millis' } },
    // changed amount from decimal bytes to double – incompatible
    { name: 'amount', type: 'double' },
    {
      name: 'status',
      type: { type: 'enum', name: 'Status', symbols: ['ACTIVE', 'INACTIVE'] }
    }
  ]
} as const;
```

Attempting to register:

```ts
import { registry } from './registry';
import { USER_EVENT_BAD } from './badSchema';
import { CompatibilityMode } from 'avro-compatibility';

try {
  registry.register(USER_EVENT_BAD, CompatibilityMode.BACKWARD);
} catch (e) {
  console.error('🚨 Registration failed (as expected):', (e as Error).message);
}
```

**Result:**  

```
🚨 Registration failed (as expected): Schema is not BACKWARD compatible with existing versions
```

### 7.3 ❓ Unknown schema identifier  

If a consumer receives a message whose schema ID was never registered:

```ts
const unknownId = 9999;
const fakeHeader = Buffer.alloc(5);
fakeHeader.writeUInt8(0, 0);
fakeHeader.writeUInt32BE(unknownId, 1);
const fakePayload = Buffer.concat([fakeHeader, Buffer.from([0x00])]);

try {
  // will throw inside decodeMessage()
  decodeMessage(fakePayload);
} catch (e) {
  console.error('❓ Unknown ID handling:', (e as Error).message);
}
```

Output:

```
❓ Unknown ID handling: Unknown schema ID 9999
```

No external registry is contacted – everything lives in the in‑memory `LocalRegistry`.

--- 

## 8️⃣ Full source listing (copy‑paste ready)

<details>
<summary>📂 src/registry.ts</summary>

```ts
// src/registry.ts
import { CompatibilityChecker, CompatibilityMode } from 'avro-compatibility';
import type { Schema } from 'avsc';
import { USER_EVENT_V1, USER_EVENT_V2, SCHEMA_IDS } from './schemas';

export class LocalRegistry {
  private idCounter = 3;
  private schemasById = new Map<number, Schema>();
  private versions: Schema[] = [];

  constructor() {
    this.registerPredefined(USER_EVENT_V1, SCHEMA_IDS.USER_EVENT_V1);
    this.registerPredefined(USER_EVENT_V2, SCHEMA_IDS.USER_EVENT_V2);
  }

  private registerPredefined(schema: Schema, id: number) {
    this.schemasById.set(id, schema);
    this.versions.push(schema);
  }

  public register(schema: Schema, mode: CompatibilityMode = CompatibilityMode.BACKWARD): number {
    const compatible = CompatibilityChecker
      .check(schema)
      .against(this.versions.slice().reverse())
      .withCompatibility(mode)
      .check();

    if (!compatible) {
      throw new Error(`Schema is not ${CompatibilityMode[mode]} compatible with existing versions`);
    }

    const newId = this.idCounter++;
    this.schemasById.set(newId, schema);
    this.versions.push(schema);
    return newId;
  }

  public getSchema(id: number): Schema {
    const schema = this.schemasById.get(id);
    if (!schema) {
      throw new Error(`Unknown schema ID ${id}`);
    }
    return schema;
  }

  public getLatestSchema(): Schema {
    return this.versions[this.versions.length - 1];
  }
}

export const registry = new LocalRegistry();
```

</details>

<details>
<summary>📂 src/schemas.ts</summary>

```ts
// src/schemas.ts
import type { Schema } from 'avsc';

export const USER_EVENT_V1: Schema = {
  type: 'record',
  name: 'UserEvent',
  namespace: 'com.example',
  fields: [
    { name: 'id', type: 'string' },
    {
      name: 'eventTime',
      type: { type: 'long', logicalType: 'timestamp-millis' }
    },
    {
      name: 'amount',
      type: {
        type: 'bytes',
        logicalType: 'decimal',
        precision: 10,
        scale: 2
      }
    },
    {
      name: 'status',
      type: { type: 'enum', name: 'Status', symbols: ['ACTIVE', 'INACTIVE'] }
    },
    { name: 'details', type: ['null', 'string'], default: null }
  ]
} as const;

export const USER_EVENT_V2: Schema = {
  type: 'record',
  name: 'UserEvent',
  namespace: 'com.example',
  fields: [
    { name: 'id', type: 'string' },
    {
      name: 'eventTime',
      type: { type: 'long', logicalType: 'timestamp-millis' }
    },
    {
      name: 'amount',
      type: {
        type: 'bytes',
        logicalType: 'decimal',
        precision: 10,
        scale: 2
      }
    },
    {
      name: 'status',
      type: { type: 'enum', name: 'Status', symbols: ['ACTIVE', 'INACTIVE', 'SUSPENDED'] }
    },
    { name: 'details', type: ['null', 'string'], default: null },
    {
      name: 'metadata',
      type: { type: 'map', values: 'string' },
      default: {}
    }
  ]
} as const;

export const SCHEMA_IDS = {
  USER_EVENT_V1: 1,
  USER_EVENT_V2: 2
} as const;
```

</details>

<details>
<summary>📂 src/producer.ts</summary>

```ts
// src/producer.ts
import { registry } from './registry';
import { SCHEMA_IDS, USER_EVENT_V1 } from './schemas';
import avro from 'avsc';
import { Buffer } from 'node:buffer';

function encodeMessage(schemaId: number, value: unknown, writerSchema: object): Buffer {
  const type = avro.Type.forSchema(writerSchema);
  const payload = type.toBuffer(value);
  const header = Buffer.alloc(5);
  header.writeUInt8(0, 0);
  header.writeUInt32BE(schemaId, 1);
  return Buffer.concat([header, payload]);
}

const eventV1 = {
  id: 'user-123',
  eventTime: Date.now(),
  amount: Buffer.from([0x00, 0x00, 0x27, 0x10]), // 1000 → 10.00
  status: 'ACTIVE',
  details: 'first login'
};

const message = encodeMessage(SCHEMA_IDS.USER_EVENT_V1, eventV1, USER_EVENT_V1);
console.log(message.toString('base64'));
```

</details>

<details>
<summary>📂 src/consumer.ts</summary>

```ts
// src/consumer.ts
import { registry } from './registry';
import avro from 'avsc';
import { Buffer } from 'node:buffer';
import * as readline from 'node:readline';

function decodeMessage(buf: Buffer) {
  if (buf.length < 5) throw new Error('Message too short');
  const magic = buf.readUInt8(0);
  if (magic !== 0) throw new Error(`Unsupported magic byte ${magic}`);

  const schemaId = buf.readUInt32BE(1);
  const writerSchema = registry.getSchema(schemaId);
  const readerSchema = registry.getLatestSchema();

  const writerType = avro.Type.forSchema(writerSchema);
  const readerType = avro.Type.forSchema(readerSchema);
  const resolver = readerType.createResolver(writerType);

  const payload = buf.slice(5);
  return readerType.fromBuffer(payload, resolver);
}

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

rl.on('line', line => {
  try {
    const buf = Buffer.from(line.trim(), 'base64');
    const value = decodeMessage(buf);
    console.log('✅ Decoded event (reader = latest schema):');
    console.dir(value, { depth: null });
  } catch (e) {
    console.error('❌ Failed to decode:', (e as Error).message);
  }
});
```

</details>

--- 

## 9️⃣ Reproducible installation & execution  

```bash
# 1️⃣ Clone / copy the folder
git clone https://github.com/your‑org/avro-demo.git
cd avro-demo

# 2️⃣ Install exact dependencies
npm ci   # uses the lockfile (generated by npm install once)

# 3️⃣ Build (optional – ts-node runs directly)
npm run build

# 4️⃣ Run the demo (producer → consumer)
npm run producer | npm run consumer
```

You should see something like:

```
✅ Decoded event (reader = latest schema):
{
  id: 'user-123',
  eventTime: 1727189323456,
  amount: <Buffer 00 00 27 10>,
  status: 'ACTIVE',
  details: 'first login',
  metadata: {}        // default from V2
}
```

--- 

## 10️⃣ Summary of key APIs used  

| Feature | NPM package | API / Method |
|---------|-------------|--------------|
| **Avro serialization / logical types** | `avsc@5.7.9` | `avro.Type.forSchema()`, `type.toBuffer()`, `type.fromBuffer()`, `readerType.createResolver(writerType)` |
| **Compatibility checking** | `avro-compatibility@1.2.0` | `CompatibilityChecker.check(schema).against(prevSchemas).withCompatibility(mode).check()` |
| **Enum, Union, Default, Logical timestamp, Decimal** | `avsc` schema definitions (see `schemas.ts`) |
| **Wire envelope (magic byte + schema id)** | Hand‑rolled in `producer.ts` / `consumer.ts` (no external lib) |
| **Schema‑registry‑like storage** | Custom `LocalRegistry` (in‑memory map) |
| **TypeScript execution** | `ts-node@10.9.2` | `npm run producer` / `npm run consumer` |

--- 

## 🎉 What you have now  

* **Two Avro schema versions** that illustrate compatible evolution (enum addition, optional map field).  
* **Local registry** that mimics Confluent’s ID assignment, stores schemas, and enforces **backward compatibility** before accepting a new version.  
* **Producer** that writes messages with the Confluent wire format.  
* **Consumer** that resolves older writer schemas against the latest reader schema, handling unknown IDs gracefully.  
* **Demo scripts** – one‑liner to see the whole flow, plus code showing a rejected breaking change.

Feel free to extend the registry (persist to disk, expose HTTP, add subjects) or plug in other compatibility modes (`FORWARD`, `FULL`, …) by changing the argument to `registry.register`. Happy Avro coding!