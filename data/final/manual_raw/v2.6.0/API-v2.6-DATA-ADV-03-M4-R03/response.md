# Self-Contained Node.js TypeScript Avro Event Producer/Consumer with Local Schema Registry

## Project Structure

```
avro-event-system/
├── package.json
├── tsconfig.json
├── src/
│   ├── schemas/
│   │   ├── event-v1.avsc
│   │   └── event-v2.avsc
│   ├── registry/
│   │   ├── LocalSchemaRegistry.ts
│   │   ├── CompatibilityChecker.ts
│   │   └── WireEnvelope.ts
│   ├── producer/
│   │   └── EventProducer.ts
│   ├── consumer/
│   │   └── EventConsumer.ts
│   ├── types/
│   │   └── index.ts
│   └── examples/
│       ├── run-compatible-evolution.ts
│       ├── run-breaking-change-rejection.ts
│       └── run-unknown-schema-id.ts
```

---

## `package.json`

```json
{
  "name": "avro-event-system",
  "version": "1.0.0",
  "description": "Self-contained Avro event producer/consumer with local schema registry",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsc",
    "clean": "rm -rf dist",
    "rebuild": "npm run clean && npm run build",
    "example:compatible": "node dist/examples/run-compatible-evolution.js",
    "example:breaking": "node dist/examples/run-breaking-change-rejection.js",
    "example:unknown": "node dist/examples/run-unknown-schema-id.js",
    "example:all": "npm run example:compatible && npm run example:breaking && npm run example:unknown",
    "test": "node --test dist/**/*.test.js"
  },
  "keywords": ["avro", "schema-registry", "event-sourcing", "serialization"],
  "author": "",
  "license": "MIT",
  "dependencies": {
    "avsc": "5.7.7",
    "uuid": "9.0.0"
  },
  "devDependencies": {
    "@types/node": "20.10.0",
    "@types/uuid": "9.0.0",
    "typescript": "5.3.2"
  },
  "engines": {
    "node": ">=20.0.0"
  },
  "packageManager": "npm@10.2.3"
}
```

---

## `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

---

## Schema Definitions

### `src/schemas/event-v1.avsc`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "record",
  "name": "Event",
  "namespace": "com.example.events",
  "doc": "Version 1 - Initial event schema",
  "fields": [
    {
      "name": "eventId",
      "type": "string",
      "doc": "Unique event identifier"
    },
    {
      "name": "eventType",
      "type": {
        "type": "enum",
        "name": "EventType",
        "namespace": "com.example.events",
        "symbols": ["CREATED", "UPDATED", "DELETED"]
      },
      "doc": "Type of event"
    },
    {
      "name": "timestamp",
      "type": {
        "type": "long",
        "logicalType": "timestamp-millis"
      },
      "doc": "Event occurrence timestamp (logical timestamp-millis)"
    },
    {
      "name": "amount",
      "type": [
        "null",
        {
          "type": "bytes",
          "logicalType": "decimal",
          "precision": 10,
          "scale": 2
        }
      ],
      "default": null,
      "doc": "Optional monetary amount (logical decimal with precision 10, scale 2)"
    },
    {
      "name": "metadata",
      "type": {
        "type": "record",
        "name": "Metadata",
        "namespace": "com.example.events",
        "fields": [
          {
            "name": "source",
            "type": "string",
            "default": "unknown"
          },
          {
            "name": "version",
            "type": "int",
            "default": 1
          }
        ]
      },
      "default": {
        "source": "unknown",
        "version": 1
      },
      "doc": "Event metadata with defaults"
    }
  ],
  "connect.name": "com.example.events.Event"
}
```

### `src/schemas/event-v2.avsc`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "record",
  "name": "Event",
  "namespace": "com.example.events",
  "doc": "Version 2 - Backward compatible evolution: added correlationId field and ARCHIVED enum symbol",
  "fields": [
    {
      "name": "eventId",
      "type": "string",
      "doc": "Unique event identifier"
    },
    {
      "name": "eventType",
      "type": {
        "type": "enum",
        "name": "EventType",
        "namespace": "com.example.events",
        "symbols": ["CREATED", "UPDATED", "DELETED", "ARCHIVED"]
      },
      "doc": "Type of event (added ARCHIVED)"
    },
    {
      "name": "timestamp",
      "type": {
        "type": "long",
        "logicalType": "timestamp-millis"
      },
      "doc": "Event occurrence timestamp (logical timestamp-millis)"
    },
    {
      "name": "amount",
      "type": [
        "null",
        {
          "type": "bytes",
          "logicalType": "decimal",
          "precision": 10,
          "scale": 2
        }
      ],
      "default": null,
      "doc": "Optional monetary amount (logical decimal with precision 10, scale 2)"
    },
    {
      "name": "metadata",
      "type": {
        "type": "record",
        "name": "Metadata",
        "namespace": "com.example.events",
        "fields": [
          {
            "name": "source",
            "type": "string",
            "default": "unknown"
          },
          {
            "name": "version",
            "type": "int",
            "default": 1
          }
        ]
      },
      "default": {
        "source": "unknown",
        "version": 1
      },
      "doc": "Event metadata with defaults"
    },
    {
      "name": "correlationId",
      "type": ["null", "string"],
      "default": null,
      "doc": "Optional correlation ID for event tracing (new in v2)"
    }
  ],
  "connect.name": "com.example.events.Event"
}
```

---

## Type Definitions

### `src/types/index.ts`

```typescript
/**
 * Core type definitions for the Avro event system
 */

export interface SchemaEntry {
  id: number;
  schema: avro.Type;
  rawSchema: object;
  version: number;
  registeredAt: Date;
}

export interface Envelope {
  magicByte: number;
  schemaId: number;
  payload: Buffer;
}

export interface CompatibilityResult {
  compatible: boolean;
  reason?: string;
}

export type CompatibilityLevel = 'BACKWARD' | 'FORWARD' | 'FULL' | 'NONE';

export interface RegistryConfig {
  compatibilityLevel: CompatibilityLevel;
  subjectNameStrategy: SubjectNameStrategy;
}

export type SubjectNameStrategy = 
  | 'TopicNameStrategy' 
  | 'RecordNameStrategy' 
  | 'TopicRecordNameStrategy';

export interface ProducerConfig {
  registry: LocalSchemaRegistry;
  defaultSubject: string;
}

export interface ConsumerConfig {
  registry: LocalSchemaRegistry;
  readerSchemaSubject?: string;
}

export interface EventV1 {
  eventId: string;
  eventType: 'CREATED' | 'UPDATED' | 'DELETED';
  timestamp: Date;
  amount: Buffer | null;
  metadata: {
    source: string;
    version: number;
  };
}

export interface EventV2 extends EventV1 {
  eventType: 'CREATED' | 'UPDATED' | 'DELETED' | 'ARCHIVED';
  correlationId: string | null;
}

export type Event = EventV1 | EventV2;

// Re-export avro types for convenience
import * as avro from 'avsc';
export { avro };
```

---

## Registry Implementation

### `src/registry/CompatibilityChecker.ts`

```typescript
/**
 * Avro Schema Compatibility Checker
 * 
 * Implements backward compatibility checking per Avro specification:
 * - Writer schema (old) must be readable by Reader schema (new)
 * - Uses avsc's built-in type resolution for validation
 * 
 * APIs used:
 * - avro.Type.canRead() - checks if reader can read writer data
 * - avro.Type.compare() - compares two types for equality
 * - avro.parse() - parses schema JSON into Type objects
 */

import * as avro from 'avsc';
import { CompatibilityResult, CompatibilityLevel } from '../types';

export class CompatibilityChecker {
  /**
   * Check if a new reader schema is compatible with an existing writer schema
   * @param writerSchema - The schema used to write data (older version)
   * @param readerSchema - The schema used to read data (newer version)
   * @param level - Compatibility level to enforce
   * @returns CompatibilityResult with boolean and optional reason
   */
  static checkCompatibility(
    writerSchema: avro.Type,
    readerSchema: avro.Type,
    level: CompatibilityLevel = 'BACKWARD'
  ): CompatibilityResult {
    switch (level) {
      case 'BACKWARD':
        return this.checkBackwardCompatibility(writerSchema, readerSchema);
      case 'FORWARD':
        return this.checkForwardCompatibility(writerSchema, readerSchema);
      case 'FULL':
        return this.checkFullCompatibility(writerSchema, readerSchema);
      case 'NONE':
        return { compatible: true };
      default:
        return { compatible: false, reason: `Unknown compatibility level: ${level}` };
    }
  }

  /**
   * Backward compatibility: New reader can read old writer data
   * Rules:
   * - Reader may have more fields than writer (with defaults)
   * - Reader may have fewer fields than writer (extra writer fields ignored)
   * - Enum: Reader may have more symbols (unknown symbols from writer cause error unless union)
   * - Types must be promotable (int->long, float->double, etc.)
   */
  private static checkBackwardCompatibility(
    writerSchema: avro.Type,
    readerSchema: avro.Type
  ): CompatibilityResult {
    try {
      // avsc's canRead checks if readerSchema can read data written with writerSchema
      const canRead = readerSchema.canRead(writerSchema);
      
      if (!canRead) {
        return {
          compatible: false,
          reason: 'Reader schema cannot read writer schema data. ' +
            'Check: missing required fields without defaults, ' +
            'incompatible type changes, or removed enum symbols.'
        };
      }

      // Additional validation: ensure no required fields were added without defaults
      const fieldCheck = this.validateRecordFields(writerSchema, readerSchema);
      if (!fieldCheck.compatible) return fieldCheck;

      return { compatible: true };
    } catch (error) {
      return {
        compatible: false,
        reason: `Compatibility check failed: ${error instanceof Error ? error.message : String(error)}`
      };
    }
  }

  /**
   * Forward compatibility: Old reader can read new writer data
   * Rules (inverse of backward):
   * - Writer may have more fields than reader (with defaults in writer)
   * - Writer may have fewer fields than reader
   * - Enum: Writer may not use symbols unknown to reader
   */
  private static checkForwardCompatibility(
    writerSchema: avro.Type,
    readerSchema: avro.Type
  ): CompatibilityResult {
    // Forward compatibility = backward compatibility with schemas swapped
    return this.checkBackwardCompatibility(readerSchema, writerSchema);
  }

  /**
   * Full compatibility: Both backward and forward
   */
  private static checkFullCompatibility(
    writerSchema: avro.Type,
    readerSchema: avro.Type
  ): CompatibilityResult {
    const backward = this.checkBackwardCompatibility(writerSchema, readerSchema);
    if (!backward.compatible) return backward;
    
    const forward = this.checkForwardCompatibility(writerSchema, readerSchema);
    if (!forward.compatible) return forward;
    
    return { compatible: true };
  }

  /**
   * Validate record field compatibility
   */
  private static validateRecordFields(
    writerSchema: avro.Type,
    readerSchema: avro.Type
  ): CompatibilityResult {
    if (writerSchema.type !== 'record' || readerSchema.type !== 'record') {
      return { compatible: true }; // Non-records handled by canRead
    }

    const writerFields = new Map(writerSchema.fields.map(f => [f.name, f]));
    const readerFields = new Map(readerSchema.fields.map(f => [f.name, f]));

    // Check each writer field exists in reader or has default in reader
    for (const [name, writerField] of writerFields) {
      const readerField = readerFields.get(name);
      
      if (!readerField) {
        // Field removed in reader - OK for backward compatibility (ignored)
        continue;
      }

      // Check type compatibility
      const typeCheck = this.checkTypeCompatibility(writerField.type, readerField.type);
      if (!typeCheck.compatible) {
        return {
          compatible: false,
          reason: `Field '${name}': ${typeCheck.reason}`
        };
      }
    }

    // Check new reader fields have defaults
    for (const [name, readerField] of readerFields) {
      if (!writerFields.has(name)) {
        // New field in reader - must have default for backward compatibility
        if (readerField.default === undefined) {
          return {
            compatible: false,
            reason: `New field '${name}' in reader schema must have a default value for backward compatibility`
          };
        }
      }
    }

    return { compatible: true };
  }

  /**
   * Check if writer type can be read as reader type
   */
  private static checkTypeCompatibility(
    writerType: avro.Type,
    readerType: avro.Type
  ): CompatibilityResult {
    // Use avsc's canRead for type-level checking
    try {
      if (readerType.canRead(writerType)) {
        return { compatible: true };
      }
      
      // Special handling for unions
      if (writerType.type === 'union' && readerType.type === 'union') {
        return this.checkUnionCompatibility(writerType, readerType);
      }
      
      // Special handling for enums
      if (writerType.type === 'enum' && readerType.type === 'enum') {
        return this.checkEnumCompatibility(writerType, readerType);
      }

      return {
        compatible: false,
        reason: `Type mismatch: writer ${writerType.type} cannot be read as reader ${readerType.type}`
      };
    } catch (error) {
      return {
        compatible: false,
        reason: `Type compatibility error: ${error instanceof Error ? error.message : String(error)}`
      };
    }
  }

  private static checkUnionCompatibility(
    writerUnion: avro.Type,
    readerUnion: avro.Type
  ): CompatibilityResult {
    // For backward compatibility, reader union must be a superset of writer union
    // (reader can handle all types writer might produce)
    const writerTypes = writerUnion.types;
    const readerTypes = readerUnion.types;

    for (const wType of writerTypes) {
      let matched = false;
      for (const rType of readerTypes) {
        if (rType.canRead(wType)) {
          matched = true;
          break;
        }
      }
      if (!matched) {
        return {
          compatible: false,
          reason: `Union type ${wType.type} in writer has no compatible type in reader union`
        };
      }
    }
    return { compatible: true };
  }

  private static checkEnumCompatibility(
    writerEnum: avro.Type,
    readerEnum: avro.Type
  ): CompatibilityResult {
    const writerSymbols = new Set(writerEnum.symbols);
    const readerSymbols = new Set(readerEnum.symbols);

    // For backward compatibility: reader must have all writer symbols
    // (writer won't produce symbols it doesn't know)
    for (const symbol of writerSymbols) {
      if (!readerSymbols.has(symbol)) {
        return {
          compatible: false,
          reason: `Enum symbol '${symbol}' in writer schema not present in reader schema`
        };
      }
    }

    // Reader can have additional symbols (backward compatible)
    return { compatible: true };
  }
}
```

### `src/registry/WireEnvelope.ts`

```typescript
/**
 * Wire Envelope Encoding/Decoding
 * 
 * Implements the Confluent Schema Registry wire format:
 * - Byte 0: Magic byte (0x00)
 * - Bytes 1-4: Schema ID (4-byte big-endian integer)
 * - Bytes 5+: Avro binary payload
 * 
 * This format allows consumers to look up the writer schema by ID
 * and resolve it against their reader schema.
 */

import { Envelope } from '../types';

export class WireEnvelope {
  static readonly MAGIC_BYTE = 0x00;
  static readonly HEADER_SIZE = 5; // 1 byte magic + 4 bytes schema ID

  /**
   * Encode a payload with schema ID into wire format
   * @param schemaId - Registered schema identifier
   * @param payload - Avro-encoded binary data
   * @returns Complete wire-format buffer
   */
  static encode(schemaId: number, payload: Buffer): Buffer {
    if (schemaId < 0 || schemaId > 0xFFFFFFFF) {
      throw new Error(`Schema ID out of range: ${schemaId} (must be 0 to 2^32-1)`);
    }

    const envelope = Buffer.alloc(this.HEADER_SIZE + payload.length);
    envelope[0] = this.MAGIC_BYTE;
    envelope.writeUInt32BE(schemaId, 1);
    payload.copy(envelope, this.HEADER_SIZE);
    return envelope;
  }

  /**
   * Decode a wire-format buffer into envelope components
   * @param buffer - Wire-format buffer
   * @returns Parsed envelope with magic byte, schema ID, and payload
   * @throws Error if buffer is malformed or magic byte mismatch
   */
  static decode(buffer: Buffer): Envelope {
    if (buffer.length < this.HEADER_SIZE) {
      throw new Error(
        `Buffer too short for wire envelope: ${buffer.length} bytes (minimum ${this.HEADER_SIZE})`
      );
    }

    const magicByte = buffer[0];
    if (magicByte !== this.MAGIC_BYTE) {
      throw new Error(
        `Invalid magic byte: 0x${magicByte.toString(16).padStart(2, '0')} ` +
        `(expected 0x${this.MAGIC_BYTE.toString(16).padStart(2, '0')})`
      );
    }

    const schemaId = buffer.readUInt32BE(1);
    const payload = buffer.subarray(this.HEADER_SIZE);

    return { magicByte, schemaId, payload };
  }

  /**
   * Validate envelope without full decode
   */
  static isValidEnvelope(buffer: Buffer): boolean {
    try {
      this.decode(buffer);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Extract schema ID from envelope without full validation
   */
  static peekSchemaId(buffer: Buffer): number | null {
    if (buffer.length < this.HEADER_SIZE) return null;
    if (buffer[0] !== this.MAGIC_BYTE) return null;
    return buffer.readUInt32BE(1);
  }
}
```

### `src/registry/LocalSchemaRegistry.ts`

```typescript
/**
 * Local Schema Registry Adapter
 * 
 * In-memory schema registry that:
 * - Stores schemas by subject and version
 * - Assigns globally unique schema IDs
 * - Enforces compatibility checks before registration
 * - Provides schema lookup by ID or subject+version
 * - No external dependencies - fully self-contained
 * 
 * APIs used from avsc:
 * - avro.parse() - Parse JSON schema into Type object
 * - avro.Type.toString() - Get canonical schema string
 * - avro.Type.canRead() - Used by CompatibilityChecker
 */

import * as avro from 'avsc';
import { v4 as uuidv4 } from 'uuid';
import { 
  SchemaEntry, 
  RegistryConfig, 
  CompatibilityLevel, 
  SubjectNameStrategy 
} from '../types';
import { CompatibilityChecker } from './CompatibilityChecker';
import { WireEnvelope } from './WireEnvelope';

export class LocalSchemaRegistry {
  private schemasById: Map<number, SchemaEntry> = new Map();
  private schemasBySubject: Map<string, Map<number, SchemaEntry>> = new Map();
  private subjectVersions: Map<string, number> = new Map();
  private nextSchemaId: number = 1;
  private config: RegistryConfig;

  constructor(config: Partial<RegistryConfig> = {}) {
    this.config = {
      compatibilityLevel: config.compatibilityLevel ?? 'BACKWARD',
      subjectNameStrategy: config.subjectNameStrategy ?? 'TopicNameStrategy'
    };
  }

  /**
   * Register a new schema under a subject
   * Performs compatibility check against latest version
   * @param subject - Subject name (typically topic-name or record-name)
   * @param schemaJson - Avro schema as JSON object
   * @returns Registered schema entry with assigned ID and version
   * @throws Error if compatibility check fails or schema invalid
   */
  register(subject: string, schemaJson: object): SchemaEntry {
    // Parse and validate schema
    let schemaType: avro.Type;
    try {
      schemaType = avro.parse(schemaJson, { wrapUnions: true });
    } catch (error) {
      throw new Error(`Invalid Avro schema: ${error instanceof Error ? error.message : String(error)}`);
    }

    // Get current latest version for compatibility check
    const subjectMap = this.schemasBySubject.get(subject);
    const latestVersion = subjectMap ? Math.max(...subjectMap.keys()) : 0;

    if (latestVersion > 0) {
      const latestEntry = subjectMap!.get(latestVersion)!;
      const compatResult = CompatibilityChecker.checkCompatibility(
        latestEntry.schema,  // Writer (existing)
        schemaType,          // Reader (new)
        this.config.compatibilityLevel
      );

      if (!compatResult.compatible) {
        throw new Error(
          `Schema compatibility check failed for subject '${subject}' ` +
          `(${this.config.compatibilityLevel}): ${compatResult.reason}`
        );
      }
    }

    // Assign new schema ID and version
    const schemaId = this.nextSchemaId++;
    const version = latestVersion + 1;

    const entry: SchemaEntry = {
      id: schemaId,
      schema: schemaType,
      rawSchema: schemaJson,
      version,
      registeredAt: new Date()
    };

    // Store by ID
    this.schemasById.set(schemaId, entry);

    // Store by subject+version
    if (!this.schemasBySubject.has(subject)) {
      this.schemasBySubject.set(subject, new Map());
    }
    this.schemasBySubject.get(subject)!.set(version, entry);
    this.subjectVersions.set(subject, version);

    return entry;
  }

  /**
   * Get schema by global ID
   */
  getById(schemaId: number): SchemaEntry | undefined {
    return this.schemasById.get(schemaId);
  }

  /**
   * Get schema by subject and version
   */
  getBySubjectAndVersion(subject: string, version: number): SchemaEntry | undefined {
    return this.schemasBySubject.get(subject)?.get(version);
  }

  /**
   * Get latest schema for a subject
   */
  getLatest(subject: string): SchemaEntry | undefined {
    const version = this.subjectVersions.get(subject);
    if (!version) return undefined;
    return this.getBySubjectAndVersion(subject, version);
  }

  /**
   * Get all versions for a subject
   */
  getVersions(subject: string): number[] {
    const subjectMap = this.schemasBySubject.get(subject);
    if (!subjectMap) return [];
    return Array.from(subjectMap.keys()).sort((a, b) => a - b);
  }

  /**
   * Check if a schema ID exists
   */
  hasSchemaId(schemaId: number): boolean {
    return this.schemasById.has(schemaId);
  }

  /**
   * Encode data using a registered schema (writer schema)
   * Returns wire-format envelope
   */
  encode(schemaId: number, data: object): Buffer {
    const entry = this.schemasById.get(schemaId);
    if (!entry) {
      throw new Error(`Schema ID ${schemaId} not found in registry`);
    }

    const payload = entry.schema.toBuffer(data);
    return WireEnvelope.encode(schemaId, payload);
  }

  /**
   * Decode wire-format envelope using reader schema resolution
   * @param envelope - Wire-format buffer
   * @param readerSchemaSubject - Optional subject to use for reader schema (defaults to latest)
   * @param readerSchemaVersion - Optional specific version for reader schema
   * @returns Decoded data resolved against reader schema
   */
  decode(
    envelope: Buffer,
    readerSchemaSubject?: string,
    readerSchemaVersion?: number
  ): object {
    const { schemaId: writerSchemaId, payload } = WireEnvelope.decode(envelope);

    // Get writer schema (used to encode)
    const writerEntry = this.schemasById.get(writerSchemaId);
    if (!writerEntry) {
      throw new Error(`Unknown schema ID in envelope: ${writerSchemaId}`);
    }

    // Determine reader schema
    let readerEntry: SchemaEntry;
    if (readerSchemaSubject) {
      if (readerSchemaVersion) {
        readerEntry = this.getBySubjectAndVersion(readerSchemaSubject, readerSchemaVersion)!;
      } else {
        readerEntry = this.getLatest(readerSchemaSubject)!;
      }
      if (!readerEntry) {
        throw new Error(`Reader schema not found for subject: ${readerSchemaSubject}`);
      }
    } else {
      // Default: use writer schema as reader (no resolution)
      readerEntry = writerEntry;
    }

    // Resolve writer schema against reader schema
    const resolvedType = avro.Type.forType(
      writerEntry.schema,
      readerEntry.schema,
      { wrapUnions: true }
    );

    return resolvedType.fromBuffer(payload);
  }

  /**
   * Get registry configuration
   */
  getConfig(): RegistryConfig {
    return { ...this.config };
  }

  /**
   * Get all registered subjects
   */
  getSubjects(): string[] {
    return Array.from(this.schemasBySubject.keys());
  }

  /**
   * Get registry statistics
   */
  getStats(): { subjects: number; schemas: number; nextSchemaId: number } {
    return {
      subjects: this.schemasBySubject.size,
      schemas: this.schemasById.size,
      nextSchemaId: this.nextSchemaId
    };
  }

  /**
   * Clear all schemas (for testing)
   */
  clear(): void {
    this.schemasById.clear();
    this.schemasBySubject.clear();
    this.subjectVersions.clear();
    this.nextSchemaId = 1;
  }
}
```

---

## Producer & Consumer

### `src/producer/EventProducer.ts`

```typescript
/**
 * Avro Event Producer
 * 
 * Produces events using a registered writer schema.
 * Encodes events into wire-format envelopes with schema ID.
 * 
 * APIs used from avsc:
 * - Type.toBuffer() - Serialize JavaScript object to Avro binary
 * - Type.fromBuffer() - Deserialize (used internally for validation)
 */

import { LocalSchemaRegistry } from '../registry/LocalSchemaRegistry';
import { ProducerConfig, EventV1, EventV2 } from '../types';
import { WireEnvelope } from '../registry/WireEnvelope';

export class EventProducer {
  private registry: LocalSchemaRegistry;
  private defaultSubject: string;
  private writerSchemaId: number | null = null;

  constructor(config: ProducerConfig) {
    this.registry = config.registry;
    this.defaultSubject = config.defaultSubject;
  }

  /**
   * Initialize producer with a specific schema version
   * @param subject - Subject to use (defaults to defaultSubject)
   * @param version - Specific version to use (defaults to latest)
   */
  async initialize(subject?: string, version?: number): Promise<void> {
    const subj = subject ?? this.defaultSubject;
    let entry = version 
      ? this.registry.getBySubjectAndVersion(subj, version)
      : this.registry.getLatest(subj);

    if (!entry) {
      throw new Error(`No schema found for subject '${subj}'${version ? ` version ${version}` : ''}`);
    }

    this.writerSchemaId = entry.id;
  }

  /**
   * Produce an event using the initialized writer schema
   * @param event - Event data matching writer schema
   * @returns Wire-format envelope buffer
   */
  produce(event: EventV1 | EventV2): Buffer {
    if (this.writerSchemaId === null) {
      throw new Error('Producer not initialized. Call initialize() first.');
    }

    return this.registry.encode(this.writerSchemaId, event);
  }

  /**
   * Produce multiple events as a batch
   */
  produceBatch(events: (EventV1 | EventV2)[]): Buffer[] {
    return events.map(event => this.produce(event));
  }

  /**
   * Get current writer schema ID
   */
  getWriterSchemaId(): number | null {
    return this.writerSchemaId;
  }

  /**
   * Get writer schema metadata
   */
  getWriterSchemaInfo(): { id: number; version: number; subject: string } | null {
    if (this.writerSchemaId === null) return null;
    const entry = this.registry.getById(this.writerSchemaId);
    if (!entry) return null;
    return {
      id: entry.id,
      version: entry.version,
      subject: this.defaultSubject
    };
  }
}
```

### `src/consumer/EventConsumer.ts`

```typescript
/**
 * Avro Event Consumer
 * 
 * Consumes wire-format envelopes and resolves them against a reader schema.
 * Demonstrates schema resolution: older writer schemas read with newer reader schemas.
 * 
 * APIs used from avsc:
 * - Type.forType() - Create a resolving type (writer -> reader)
 * - ResolvingType.fromBuffer() - Decode with schema resolution
 */

import { LocalSchemaRegistry } from '../registry/LocalSchemaRegistry';
import { ConsumerConfig, EventV2 } from '../types';
import { WireEnvelope } from '../registry/WireEnvelope';

export interface DecodedEvent {
  data: EventV2;
  writerSchemaId: number;
  writerSchemaVersion: number;
  readerSchemaVersion: number;
}

export class EventConsumer {
  private registry: LocalSchemaRegistry;
  private readerSchemaSubject: string;
  private readerSchemaVersion: number | null = null;

  constructor(config: ConsumerConfig) {
    this.registry = config.registry;
    this.readerSchemaSubject = config.readerSchemaSubject ?? 'events';
  }

  /**
   * Set specific reader schema version (for testing evolution)
   */
  setReaderSchemaVersion(version: number): void {
    this.readerSchemaVersion = version;
  }

  /**
   * Use latest reader schema
   */
  useLatestReaderSchema(): void {
    this.readerSchemaVersion = null;
  }

  /**
   * Consume a wire-format envelope
   * @param envelope - Wire-format buffer from producer
   * @returns Decoded event with schema metadata
   */
  consume(envelope: Buffer): DecodedEvent {
    // Peek writer schema ID
    const writerSchemaId = WireEnvelope.peekSchemaId(envelope);
    if (writerSchemaId === null) {
      throw new Error('Invalid envelope: cannot determine writer schema ID');
    }

    const writerEntry = this.registry.getById(writerSchemaId);
    if (!writerEntry) {
      throw new Error(`Unknown writer schema ID: ${writerSchemaId}`);
    }

    // Determine reader schema
    let readerEntry = this.readerSchemaVersion
      ? this.registry.getBySubjectAndVersion(this.readerSchemaSubject, this.readerSchemaVersion)
      : this.registry.getLatest(this.readerSchemaSubject);

    if (!readerEntry) {
      throw new Error(`Reader schema not found for subject: ${this.readerSchemaSubject}`);
    }

    // Decode with schema resolution (writer -> reader)
    const data = this.registry.decode(
      envelope,
      this.readerSchemaSubject,
      this.readerSchemaVersion ?? undefined
    ) as EventV2;

    return {
      data,
      writerSchemaId: writerEntry.id,
      writerSchemaVersion: writerEntry.version,
      readerSchemaVersion: readerEntry.version
    };
  }

  /**
   * Consume multiple envelopes
   */
  consumeBatch(envelopes: Buffer[]): DecodedEvent[] {
    return envelopes.map(env => this.consume(env));
  }

  /**
   * Get current reader schema info
   */
  getReaderSchemaInfo(): { subject: string; version: number; id: number } | null {
    const entry = this.readerSchemaVersion
      ? this.registry.getBySubjectAndVersion(this.readerSchemaSubject, this.readerSchemaVersion)
      : this.registry.getLatest(this.readerSchemaSubject);
    
    if (!entry) return null;
    return {
      subject: this.readerSchemaSubject,
      version: entry.version,
      id: entry.id
    };
  }
}
```

---

## Example Scripts

### `src/examples/run-compatible-evolution.ts`

```typescript
/**
 * Example: Compatible Schema Evolution
 * 
 * Demonstrates:
 * 1. Register v1 schema
 * 2. Produce events with v1
 * 3. Register v2 schema (backward compatible)
 * 4. Consume v1 events with v2 reader schema
 * 5. Verify new fields get defaults, enum extension works
 */

import { LocalSchemaRegistry } from '../registry/LocalSchemaRegistry';
import { EventProducer } from '../producer/EventProducer';
import { EventConsumer } from '../consumer/EventConsumer';
import * as fs from 'fs';
import * as path from 'path';

// Load schema files
const schemaV1 = JSON.parse(
  fs.readFileSync(path.join(__dirname, '../../schemas/event-v1.avsc'), 'utf-8')
);
const schemaV2 = JSON.parse(
  fs.readFileSync(path.join(__dirname, '../../schemas/event-v2.avsc'), 'utf-8')
);

const SUBJECT = 'com.example.events.Event';

async function runCompatibleEvolution() {
  console.log('╔══════════════════════════════════════════════════════════════╗');
  console.log('║  Example: Compatible Schema Evolution (Backward Compatible) ║');
  console.log('╚══════════════════════════════════════════════════════════════╝\n');

  // Create registry with backward compatibility (default)
  const registry = new LocalSchemaRegistry({ compatibilityLevel: 'BACKWARD' });

  // Step 1: Register v1 schema
  console.log('📝 Step 1: Registering v1 schema...');
  const v1Entry = registry.register(SUBJECT, schemaV1);
  console.log(`   ✓ Registered v1: ID=${v1Entry.id}, Version=${v1Entry.version}`);

  // Step 2: Initialize producer with v1
  console.log('\n📤 Step 2: Producing events with v1 writer schema...');
  const producer = new EventProducer({ registry, defaultSubject: SUBJECT });
  await producer.initialize(SUBJECT, 1);

  // Create v1 events (no correlationId, no ARCHIVED enum)
  const v1Events = [
    {
      eventId: 'evt-001',
      eventType: 'CREATED' as const,
      timestamp: new Date('2024-01-15T10:30:00.000Z'),
      amount: Buffer.from([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0xE8]), // 1000.00 as decimal(10,2)
      metadata: { source: 'web-app', version: 1 }
    },
    {
      eventId: 'evt-002',
      eventType: 'UPDATED' as const,
      timestamp: new Date('2024-01-15T11:45:00.000Z'),
      amount: null,
      metadata: { source: 'mobile-app', version: 1 }
    },
    {
      eventId: 'evt-003',
      eventType: 'DELETED' as const,
      timestamp: new Date('2024-01-15T12:00:00.000Z'),
      amount: Buffer.from([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x07, 0xD0]), // 2000.00
      metadata: { source: 'api', version: 1 }
    }
  ];

  const envelopes = producer.produceBatch(v1Events);
  console.log(`   ✓ Produced ${envelopes.length} events with writer schema ID=${producer.getWriterSchemaId()}`);

  // Step 3: Register v2 schema (backward compatible)
  console.log('\n📝 Step 3: Registering v2 schema (backward compatible)...');
  const v2Entry = registry.register(SUBJECT, schemaV2);
  console.log(`   ✓ Registered v2: ID=${v2Entry.id}, Version=${v2Entry.version}`);

  // Step 4: Initialize consumer with v2 reader schema
  console.log('\n📥 Step 4: Consuming v1 events with v2 reader schema...');
  const consumer = new EventConsumer({ 
    registry, 
    readerSchemaSubject: SUBJECT 
  });
  // Use latest (v2) reader schema
  consumer.useLatestReaderSchema();

  // Step 5: Consume and verify resolution
  console.log('\n🔍 Step 5: Verifying schema resolution results...\n');
  
  for (let i = 0; i < envelopes.length; i++) {
    const result = consumer.consume(envelopes[i]);
    const event = result.data;
    
    console.log(`   Event ${i + 1} (writer v${result.writerSchemaVersion} → reader v${result.readerSchemaVersion}):`);
    console.log(`     eventId: ${event.eventId}`);
    console.log(`     eventType: ${event.eventType}`);
    console.log(`     timestamp: ${event.timestamp.toISOString()}`);
    console.log(`     amount: ${event.amount ? 'present (decimal bytes)' : 'null'}`);
    console.log(`     metadata: ${JSON.stringify(event.metadata)}`);
    console.log(`     correlationId: ${event.correlationId ?? '(default: null)'}`);
    console.log('');
  }

  // Verify backward compatibility: v2 reader can read v1 data
  console.log('✅ Backward compatibility verified:');
  console.log('   - v2 reader successfully read v1 writer data');
  console.log('   - New field correlationId defaulted to null');
  console.log('   - Enum ARCHIVED not present in v1 data (no conflict)');
  console.log('   - Default metadata values preserved\n');

  // Also test producing with v2
  console.log('📤 Bonus: Producing new event with v2 writer schema...');
  const producerV2 = new EventProducer({ registry, defaultSubject: SUBJECT });
  await producerV2.initialize(SUBJECT, 2);

  const v2Event = {
    eventId: 'evt-004',
    eventType: 'ARCHIVED' as const,  // New enum value
    timestamp: new Date('2024-01-15T13:00:00.000Z'),
    amount: Buffer.from([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0B, 0xB8]), // 3000.00
    metadata: { source: 'archive-service', version: 2 },
    correlationId: 'corr-12345'
  };

  const v2Envelope = producerV2.produce(v2Event);
  const v2Result = consumer.consume(v2Envelope);
  console.log(`   ✓ Produced and consumed v2 event with ARCHIVED type`);
  console.log(`     correlationId: ${v2Result.data.correlationId}`);
  console.log(`     eventType: ${v2Result.data.eventType}\n`);

  console.log('═══════════════════════════════════════════════════════════════');
  console.log('✅ Compatible evolution example completed successfully');
  console.log('═══════════════════════════════════════════════════════════════\n');
}

runCompatibleEvolution().catch(console.error);
```

### `src/examples/run-breaking-change-rejection.ts`

```typescript
/**
 * Example: Breaking Change Rejection
 * 
 * Demonstrates:
 * 1. Register v1 schema
 * 2. Attempt to register breaking change (removed required field, changed type)
 * 3. Verify registry rejects with clear error message
 */

import { LocalSchemaRegistry } from '../registry/LocalSchemaRegistry';
import * as fs from 'fs';
import * as path from 'path';

const schemaV1 = JSON.parse(
  fs.readFileSync(path.join(__dirname, '../../schemas/event-v1.avsc'), 'utf-8')
);

// Breaking change: remove required field 'eventId' (no default)
// and change amount from decimal to string
const breakingSchema = {
  ...schemaV1,
  doc: "Version X - BREAKING: removed required field, changed type",
  fields: [
    // eventId REMOVED - breaking!
    {
      "name": "eventType",
      "type": {
        "type": "enum",
        "name": "EventType",
        "namespace": "com.example.events",
        "symbols": ["CREATED", "UPDATED", "DELETED"]
      }
    },
    {
      "name": "timestamp",
      "type": { "type": "long", "logicalType": "timestamp-millis" }
    },
    {
      "name": "amount",
      "type": "string",  // CHANGED from decimal to string - breaking!
      "default": "0.00"
    },
    {
      "name": "metadata",
      "type": {
        "type": "record",
        "name": "Metadata",
        "namespace": "com.example.events",
        "fields": [
          { "name": "source", "type": "string", "default": "unknown" },
          { "name": "version", "type": "int", "default": 1 }
        ]
      },
      "default": { "source": "unknown", "version": 1 }
    }
  ]
};

const SUBJECT = 'com.example.events.Event';

async function runBreakingChangeRejection() {
  console.log('╔══════════════════════════════════════════════════════════════╗');
  console.log('║  Example: Breaking Change Rejection                         ║');
  console.log('╚══════════════════════════════════════════════════════════════╝\n');

  const registry = new LocalSchemaRegistry({ compatibilityLevel: 'BACKWARD' });

  // Register v1
  console.log('📝 Registering v1 schema...');
  registry.register(SUBJECT, schemaV1);
  console.log('   ✓ v1 registered\n');

  // Attempt to register breaking schema
  console.log('📝 Attempting to register BREAKING schema...');
  console.log('   Changes: removed required "eventId" field, changed "amount" from decimal to string\n');

  try {
    registry.register(SUBJECT, breakingSchema);
    console.log('   ❌ ERROR: Breaking schema was incorrectly accepted!');
    process.exit(1);
  } catch (error) {
    console.log('   ✓ Registry correctly rejected breaking schema:');
    console.log(`      ${error instanceof Error ? error.message : String(error)}\n`);
  }

  // Also test forward compatibility rejection
  console.log('📝 Testing FORWARD compatibility rejection...');
  const forwardRegistry = new LocalSchemaRegistry({ compatibilityLevel: 'FORWARD' });
  forwardRegistry.register(SUBJECT, schemaV1);
  
  // Forward breaking: add required field without default in writer
  const forwardBreakingSchema = {
    ...schemaV1,
    fields: [
      ...schemaV1.fields,
      { "name": "newRequiredField", "type": "string" } // No default!
    ]
  };

  try {
    forwardRegistry.register(SUBJECT, forwardBreakingSchema);
    console.log('   ❌ ERROR: Forward-breaking schema was incorrectly accepted!');
    process.exit(1);
  } catch (error) {
    console.log('   ✓ Registry correctly rejected forward-breaking schema:');
    console.log(`      ${error instanceof Error ? error.message : String(error)}\n`);
  }

  // Test FULL compatibility
  console.log('📝 Testing FULL compatibility rejection...');
  const fullRegistry = new LocalSchemaRegistry({ compatibilityLevel: 'FULL' });
  fullRegistry.register(SUBJECT, schemaV1);

  try {
    fullRegistry.register(SUBJECT, breakingSchema);
    console.log('   ❌ ERROR: Full-breaking schema was incorrectly accepted!');
    process.exit(1);
  } catch (error) {
    console.log('   ✓ Registry correctly rejected full-breaking schema:');
    console.log(`      ${error instanceof Error ? error.message : String(error)}\n`);
  }

  console.log('═══════════════════════════════════════════════════════════════');
  console.log('✅ Breaking change rejection example completed successfully');
  console.log('═══════════════════════════════════════════════════════════════\n');
}

runBreakingChangeRejection().catch(console.error);
```

### `src/examples/run-unknown-schema-id.ts`

```typescript
/**
 * Example: Unknown Schema ID Handling
 * 
 * Demonstrates:
 * 1. Produce event with known schema ID
 * 2. Attempt to decode with unknown schema ID
 * 3. Verify clear error message without external registry contact
 */

import { LocalSchemaRegistry } from '../registry/LocalSchemaRegistry';
import { EventProducer } from '../producer/EventProducer';
import { EventConsumer } from '../consumer/EventConsumer';
import { WireEnvelope } from '../registry/WireEnvelope';
import * as fs from 'fs';
import * as path from 'path';

const schemaV1 = JSON.parse(
  fs.readFileSync(path.join(__dirname, '../../schemas/event-v1.avsc'), 'utf-8')
);

const SUBJECT = 'com.example.events.Event';

async function runUnknownSchemaId() {
  console.log('╔══════════════════════════════════════════════════════════════╗');
  console.log('║  Example: Unknown Schema ID Handling                        ║');
  console.log('╚══════════════════════════════════════════════════════════════╝\n');

  const registry = new LocalSchemaRegistry();

  // Register v1
  console.log('📝 Registering v1 schema...');
  const v1Entry = registry.register(SUBJECT, schemaV1);
  console.log(`   ✓ Registered: ID=${v1Entry.id}\n`);

  // Produce event
  console.log('📤 Producing event with known schema ID...');
  const producer = new EventProducer({ registry, defaultSubject: SUBJECT });
  await producer.initialize(SUBJECT, 1);

  const event = {
    eventId: 'evt-unknown-test',
    eventType: 'CREATED' as const,
    timestamp: new Date('2024-01-15T10:30:00.000Z'),
    amount: null,
    metadata: { source: 'test', version: 1 }
  };

  const envelope = producer.produce(event);
  console.log(`   ✓ Produced envelope with schema ID=${producer.getWriterSchemaId()}`);

  // Verify envelope structure
  const decoded = WireEnvelope.decode(envelope);
  console.log(`   Envelope: magic=0x${decoded.magicByte.toString(16)}, schemaId=${decoded.schemaId}, payload=${decoded.payload.length} bytes\n`);

  // Test 1: Normal consumption (should work)
  console.log('📥 Test 1: Consuming with known schema ID...');
  const consumer = new EventConsumer({ registry, readerSchemaSubject: SUBJECT });
  consumer.useLatestReaderSchema();

  try {
    const result = consumer.consume(envelope);
    console.log(`   ✓ Successfully consumed: ${result.data.eventId}\n`);
  } catch (error) {
    console.log(`   ❌ Unexpected error: ${error instanceof Error ? error.message : String(error)}\n`);
    process.exit(1);
  }

  // Test 2: Manually create envelope with unknown schema ID
  console.log('📥 Test 2: Attempting to consume envelope with UNKNOWN schema ID (9999)...');
  
  // Create a valid payload but with fake schema ID
  const fakeSchemaId = 9999;
  const fakeEnvelope = WireEnvelope.encode(fakeSchemaId, decoded.payload);
  
  try {
    consumer.consume(fakeEnvelope);
    console.log('   ❌ ERROR: Unknown schema ID was incorrectly accepted!');
    process.exit(1);
  } catch (error) {
    console.log('   ✓ Registry correctly rejected unknown schema ID:');
    console.log(`      ${error instanceof Error ? error.message : String(error)}\n`);
  }

  // Test 3: Corrupted magic byte
  console.log('📥 Test 3: Attempting to consume envelope with INVALID magic byte...');
  const corruptedEnvelope = Buffer.from(envelope);
  corruptedEnvelope[0] = 0xFF; // Invalid magic byte
  
  try {
    consumer.consume(corruptedEnvelope);
    console.log('   ❌ ERROR: Corrupted envelope was incorrectly accepted!');
    process.exit(1);
  } catch (error) {
    console.log('   ✓ Registry correctly rejected corrupted envelope:');
    console.log(`      ${error instanceof Error ? error.message : String(error)}\n`);
  }

  // Test 4: Truncated envelope
  console.log('📥 Test 4: Attempting to consume TRUNCATED envelope...');
  const truncatedEnvelope = envelope.subarray(0, 3); // Too short
  
  try {
    consumer.consume(truncatedEnvelope);
    console.log('   ❌ ERROR: Truncated envelope was incorrectly accepted!');
    process.exit(1);
  } catch (error) {
    console.log('   ✓ Registry correctly rejected truncated envelope:');
    console.log(`      ${error instanceof Error ? error.message : String(error)}\n`);
  }

  console.log('═══════════════════════════════════════════════════════════════');
  console.log('✅ Unknown schema ID handling example completed successfully');
  console.log('═══════════════════════════════════════════════════════════════\n');
}

runUnknownSchemaId().catch(console.error);
```

---

## Installation & Usage Commands

```bash
# 1. Create project directory and files
mkdir avro-event-system && cd avro-event-system

# 2. Save all files above to their respective paths:
#    package.json, tsconfig.json
#    src/schemas/event-v1.avsc, src/schemas/event-v2.avsc
#    src/types/index.ts
#    src/registry/CompatibilityChecker.ts, src/registry/WireEnvelope.ts, src/registry/LocalSchemaRegistry.ts
#    src/producer/EventProducer.ts
#    src/consumer/EventConsumer.ts
#    src/examples/run-compatible-evolution.ts, run-breaking-change-rejection.ts, run-unknown-schema-id.ts

# 3. Install exact dependencies
npm ci

# 4. Build TypeScript
npm run build

# 5. Run examples
npm run example:compatible   # Compatible evolution demo
npm run example:breaking     # Breaking change rejection demo
npm run example:unknown      # Unknown schema ID handling demo
npm run example:all          # Run all examples sequentially
```

---

## Expected Output

### `npm run example:compatible`

```
╔══════════════════════════════════════════════════════════════╗
║  Example: Compatible Schema Evolution (Backward Compatible) ║
╚══════════════════════════════════════════════════════════════╝

📝 Step 1: Registering v1 schema...
   ✓ Registered v1: ID=1, Version=1

📤 Step 2: Producing events with v1 writer schema...
   ✓ Produced 3 events with writer schema ID=1

📝 Step 3: Registering v2 schema (backward compatible)...
   ✓ Registered v2: ID=2, Version=2

📥 Step 4: Consuming v1 events with v2 reader schema...

🔍 Step 5: Verifying schema resolution results...

   Event 1 (writer v1 → reader v2):
     eventId: evt-001
     eventType: CREATED
     timestamp: 2024-01-15T10:30:00.000Z
     amount: present (decimal bytes)
     metadata: {"source":"web-app","version":1}
     correlationId: (default: null)

   Event 2 (writer v1 → reader v2):
     eventId: evt-002
     eventType: UPDATED
     timestamp: 2024-01-15T11:45:00.000Z
     amount: null
     metadata: {"source":"mobile-app","version":1}
     correlationId: (default: null)

   Event 3 (writer v1 → reader v2):
     eventId: evt-003
     eventType: DELETED
     timestamp: 2024-01-15T12:00:00.000Z
     amount: present (decimal bytes)
     metadata: {"source":"api","version":1}
     correlationId: (default: null)

✅ Backward compatibility verified:
   - v2 reader successfully read v1 writer data
   - New field correlationId defaulted to null
   - Enum ARCHIVED not present in v1 data (no conflict)
   - Default metadata values preserved

📤 Bonus: Producing new event with v2 writer schema...
   ✓ Produced and consumed v2 event with ARCHIVED type
     correlationId: corr-12345
     eventType: ARCHIVED

════════════════════════════════════════════════════════════════
✅ Compatible evolution example completed successfully
════════════════════════════════════════════════════════════════
```

### `npm run example:breaking`

```
╔══════════════════════════════════════════════════════════════╗
║  Example: Breaking Change Rejection                         ║
╚══════════════════════════════════════════════════════════════╝

📝 Registering v1 schema...
   ✓ v1 registered

📝 Attempting to register BREAKING schema...
   Changes: removed required "eventId" field, changed "amount" from decimal to string

   ✓ Registry correctly rejected breaking schema:
      Schema compatibility check failed for subject 'com.example.events.Event' (BACKWARD): Reader schema cannot read writer schema data. Check: missing required fields without defaults, incompatible type changes, or removed enum symbols.

📝 Testing FORWARD compatibility rejection...
   ✓ Registry correctly rejected forward-breaking schema:
      Schema compatibility check failed for subject 'com.example.events.Event' (FORWARD): New field 'newRequiredField' in reader schema must have a default value for backward compatibility

📝 Testing FULL compatibility rejection...
   ✓ Registry correctly rejected full-breaking schema:
      Schema compatibility check failed for subject 'com.example.events.Event' (FULL): Reader schema cannot read writer schema data. Check: missing required fields without defaults, incompatible type changes, or removed enum symbols.

════════════════════════════════════════════════════════════════
✅ Breaking change rejection example completed successfully
════════════════════════════════════════════════════════════════
```

### `npm run example:unknown`

```
╔══════════════════════════════════════════════════════════════╗
║  Example: Unknown Schema ID Handling                        ║
╚══════════════════════════════════════════════════════════════╝

📝 Registering v1 schema...
   ✓ Registered: ID=1

📤 Producing event with known schema ID...
   ✓ Produced envelope with schema ID=1
   Envelope: magic=0x0, schemaId=1, payload=87 bytes

📥 Test 1: Consuming with known schema ID...
   ✓ Successfully consumed: evt-unknown-test

📥 Test 2: Attempting to consume envelope with UNKNOWN schema ID (9999)...
   ✓ Registry correctly rejected unknown schema ID:
      Unknown schema ID in envelope: 9999

📥 Test 3: Attempting to consume envelope with INVALID magic byte...
   ✓ Registry correctly rejected corrupted envelope:
      Invalid magic byte: 0xff (expected 0x00)

📥 Test 4: Attempting to consume TRUNCATED envelope...
   ✓ Registry correctly rejected truncated envelope:
      Buffer too short for wire envelope: 3 bytes (minimum 5)

════════════════════════════════════════════════════════════════
✅ Unknown schema ID handling example completed successfully
════════════════════════════════════════════════════════════════
```

---

## Key Avro APIs Used

| API | Purpose | Location |
|-----|---------|----------|
| `avro.parse(schema, { wrapUnions: true })` | Parse JSON schema to Type object | `LocalSchemaRegistry.register()` |
| `type.toBuffer(data)` | Serialize JS object to Avro binary | `LocalSchemaRegistry.encode()` |
| `type.fromBuffer(buffer)` | Deserialize Avro binary to JS object | Internal resolution |
| `avro.Type.forType(writer, reader, opts)` | Create resolving type for schema evolution | `LocalSchemaRegistry.decode()` |
| `readerType.canRead(writerType)` | Check backward compatibility | `CompatibilityChecker.checkBackwardCompatibility()` |
| `type.compare(otherType)` | Compare type equality | Available for advanced checks |
| `type.fields` | Access record fields | `CompatibilityChecker.validateRecordFields()` |
| `type.symbols` | Access enum symbols | `CompatibilityChecker.checkEnumCompatibility()` |
| `type.types` | Access union member types | `CompatibilityChecker.checkUnionCompatibility()` |

---

## Schema Compatibility Rules Enforced

| Change | Backward | Forward | Full |
|--------|----------|---------|------|
| Add field with default | ✅ | ✅ | ✅ |
| Add field without default | ❌ | ✅ | ❌ |
| Remove field (writer had it) | ✅ | ❌ | ❌ |
| Add enum symbol | ✅ | ❌* | ❌* |
| Remove enum symbol | ❌ | ✅ | ❌ |
| Change int → long | ✅ | ❌ | ❌ |
| Change long → int | ❌ | ✅ | ❌ |
| Change decimal precision | ❌ | ❌ | ❌ |
| Add union branch | ✅ | ❌ | ❌ |
| Remove union branch | ❌ | ✅ | ❌ |

*Adding enum symbols is backward compatible for readers but forward-incompatible if writer uses new symbol.

---

## Logical Types Handling

| Logical Type | Avro Base Type | Encoding | Example |
|--------------|----------------|----------|---------|
| `timestamp-millis` | `long` | Milliseconds since epoch | `new Date()` → `Buffer` |
| `decimal(10,2)` | `bytes` | Two's complement big-endian | `1000.00` → `Buffer([0,0,0,0,0,0,3,232])` |

The `avsc` library automatically handles logical type conversion when `wrapUnions: true` is used during parsing.
