# Transactional Outbox & CDC Consumer Implementation

## Project Structure

```
.
├── package.json
├── tsconfig.json
├── src/
│   ├── config.ts
│   ├── db/
│   │   ├── pool.ts
│   │   ├── migrations/
│   │   │   ├── 001_create_schema.sql
│   │   │   ├── 002_create_outbox.sql
│   │   │   └── 003_create_consumer_offsets.sql
│   │   └── migration-runner.ts
│   ├── outbox/
│   │   ├── outbox-writer.ts
│   │   └── types.ts
│   ├── cdc/
│   │   ├── replication-client.ts
│   │   ├── logical-decoder.ts
│   │   ├── consumer.ts
│   │   └── types.ts
│   ├── broker/
│   │   ├── local-broker.ts
│   │   └── types.ts
│   ├── aggregates/
│   │   └── order-aggregate.ts
│   ├── poison/
│   │   └── poison-handler.ts
│   └── index.ts
├── tests/
│   ├── crash-restart.test.ts
│   └── setup.ts
└── jest.config.js
```

## package.json

```json
{
  "name": "pg-transactional-outbox-cdc",
  "version": "1.0.0",
  "description": "Self-contained PostgreSQL transactional outbox with CDC consumer",
  "main": "dist/index.js",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "ts-node src/index.ts",
    "test": "jest --runInBand --forceExit",
    "test:watch": "jest --watch",
    "migrate": "ts-node src/db/migration-runner.ts",
    "migrate:down": "ts-node src/db/migration-runner.ts down"
  },
  "dependencies": {
    "pg": "^8.11.5",
    "pg-protocol": "^1.6.0",
    "uuid": "^9.0.0",
    "pino": "^8.19.0",
    "pino-pretty": "^10.3.1"
  },
  "devDependencies": {
    "@types/jest": "^29.5.12",
    "@types/node": "^20.11.24",
    "@types/pg": "^8.11.2",
    "@types/uuid": "^9.0.8",
    "jest": "^29.7.0",
    "ts-jest": "^29.1.2",
    "ts-node": "^10.9.2",
    "typescript": "^5.3.3"
  },
  "engines": {
    "node": ">=20.0.0"
  }
}
```

## tsconfig.json

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
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "moduleResolution": "node"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests"]
}
```

## jest.config.js

```javascript
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/tests'],
  testMatch: ['**/*.test.ts'],
  moduleFileExtensions: ['ts', 'js', 'json'],
  collectCoverageFrom: ['src/**/*.ts', '!src/index.ts'],
  coverageDirectory: 'coverage',
  verbose: true,
  testTimeout: 30000,
  setupFilesAfterEnv: ['<rootDir>/tests/setup.ts']
};
```

## src/config.ts

```typescript
export interface DatabaseConfig {
  host: string;
  port: number;
  database: string;
  user: string;
  password: string;
  maxConnections: number;
  replicationDatabase?: string;
}

export interface AppConfig {
  database: DatabaseConfig;
  replicationSlot: string;
  publicationName: string;
  consumerGroupId: string;
  pollIntervalMs: number;
  batchSize: number;
  maxRetries: number;
  retryDelayMs: number;
  poisonQueueMaxSize: number;
}

export const config: AppConfig = {
  database: {
    host: process.env.PGHOST || 'localhost',
    port: parseInt(process.env.PGPORT || '5432', 10),
    database: process.env.PGDATABASE || 'outbox_demo',
    user: process.env.PGUSER || 'postgres',
    password: process.env.PGPASSWORD || 'postgres',
    maxConnections: 10,
    replicationDatabase: process.env.PGREPLICATION_DATABASE || 'outbox_demo'
  },
  replicationSlot: 'outbox_cdc_slot',
  publicationName: 'outbox_publication',
  consumerGroupId: 'order-processor-v1',
  pollIntervalMs: 100,
  batchSize: 100,
  maxRetries: 3,
  retryDelayMs: 1000,
  poisonQueueMaxSize: 1000
};
```

## src/db/pool.ts

```typescript
import { Pool, PoolClient, QueryResult } from 'pg';
import { config } from '../config';
import pino from 'pino';

const logger = pino({ name: 'db-pool' });

export class DatabasePool {
  private pool: Pool;
  private replicationPool: Pool;

  constructor() {
    this.pool = new Pool({
      host: config.database.host,
      port: config.database.port,
      database: config.database.database,
      user: config.database.user,
      password: config.database.password,
      max: config.database.maxConnections,
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 5000
    });

    this.replicationPool = new Pool({
      host: config.database.host,
      port: config.database.port,
      database: config.database.replicationDatabase,
      user: config.database.user,
      password: config.database.password,
      max: 2,
      idleTimeoutMillis: 0,
      connectionTimeoutMillis: 5000
    });

    this.pool.on('error', (err) => logger.error({ err }, 'Unexpected pool error'));
    this.replicationPool.on('error', (err) => logger.error({ err }, 'Replication pool error'));
  }

  async query(text: string, params?: unknown[]): Promise<QueryResult> {
    const start = Date.now();
    const result = await this.pool.query(text, params);
    const duration = Date.now() - start;
    logger.debug({ query: text.substring(0, 100), duration, rows: result.rowCount });
    return result;
  }

  async getClient(): Promise<PoolClient> {
    return this.pool.connect();
  }

  async getReplicationClient(): Promise<PoolClient> {
    return this.replicationPool.connect();
  }

  async transaction<T>(callback: (client: PoolClient) => Promise<T>): Promise<T> {
    const client = await this.getClient();
    try {
      await client.query('BEGIN');
      const result = await callback(client);
      await client.query('COMMIT');
      return result;
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }

  async end(): Promise<void> {
    await this.pool.end();
    await this.replicationPool.end();
  }

  getPool(): Pool {
    return this.pool;
  }
}

export const dbPool = new DatabasePool();
```

## src/db/migrations/001_create_schema.sql

```sql
-- Core schema for orders aggregate
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY,
    customer_id UUID NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    total_amount_cents BIGINT NOT NULL DEFAULT 0,
    version BIGINT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

-- Order items for completeness
CREATE TABLE IF NOT EXISTS order_items (
    id UUID PRIMARY KEY,
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price_cents BIGINT NOT NULL CHECK (unit_price_cents >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
```

## src/db/migrations/002_create_outbox.sql

```sql
-- Transactional outbox table
CREATE TABLE IF NOT EXISTS outbox_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    aggregate_id UUID NOT NULL,
    aggregate_type VARCHAR(100) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    version BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    published_at TIMESTAMPTZ
);

-- Critical indexes for CDC ordering and performance
CREATE INDEX IF NOT EXISTS idx_outbox_aggregate_version 
    ON outbox_events(aggregate_id, version);

CREATE INDEX IF NOT EXISTS idx_outbox_published_at 
    ON outbox_events(published_at) 
    WHERE published_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_outbox_created_at 
    ON outbox_events(created_at);

-- Publication for logical replication
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_publication WHERE pubname = 'outbox_publication') THEN
        CREATE PUBLICATION outbox_publication FOR TABLE outbox_events;
    END IF;
END $$;
```

## src/db/migrations/003_create_consumer_offsets.sql

```sql
-- Consumer offset tracking for idempotent processing
CREATE TABLE IF NOT EXISTS consumer_offsets (
    consumer_group_id VARCHAR(200) NOT NULL,
    replication_slot_name VARCHAR(200) NOT NULL,
    lsn pg_lsn NOT NULL,
    last_processed_event_id UUID,
    last_processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (consumer_group_id, replication_slot_name)
);

-- Poison event dead letter queue
CREATE TABLE IF NOT EXISTS poison_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_event_id UUID NOT NULL,
    aggregate_id UUID NOT NULL,
    aggregate_type VARCHAR(100) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    metadata JSONB NOT NULL,
    version BIGINT NOT NULL,
    error_message TEXT NOT NULL,
    error_stack TEXT,
    retry_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_retry_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_poison_events_created_at ON poison_events(created_at);
CREATE INDEX IF NOT EXISTS idx_poison_events_retry_count ON poison_events(retry_count);
```

## src/db/migration-runner.ts

```typescript
import { dbPool } from './pool';
import * as fs from 'fs';
import * as path from 'path';
import pino from 'pino';

const logger = pino({ name: 'migration-runner' });

const MIGRATIONS_DIR = path.join(__dirname, 'migrations');
const MIGRATION_TABLE = 'schema_migrations';

async function ensureMigrationTable(): Promise<void> {
  await dbPool.query(`
    CREATE TABLE IF NOT EXISTS ${MIGRATION_TABLE} (
        version VARCHAR(50) PRIMARY KEY,
        applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
  `);
}

async function getAppliedMigrations(): Promise<Set<string>> {
  const result = await dbPool.query(`SELECT version FROM ${MIGRATION_TABLE} ORDER BY version`);
  return new Set(result.rows.map(r => r.version));
}

async function runMigrations(direction: 'up' | 'down' = 'up'): Promise<void> {
  await ensureMigrationTable();
  const applied = await getAppliedMigrations();
  
  const files = fs.readdirSync(MIGRATIONS_DIR)
    .filter(f => f.endsWith('.sql'))
    .sort((a, b) => a.localeCompare(b));

  if (direction === 'down') {
    files.reverse();
  }

  for (const file of files) {
    const version = file.split('_')[0];
    
    if (direction === 'up' && applied.has(version)) {
      logger.info({ version, file }, 'Migration already applied, skipping');
      continue;
    }
    
    if (direction === 'down' && !applied.has(version)) {
      logger.info({ version, file }, 'Migration not applied, skipping rollback');
      continue;
    }

    const filePath = path.join(MIGRATIONS_DIR, file);
    const sql = fs.readFileSync(filePath, 'utf-8');
    
    logger.info({ version, file, direction }, 'Running migration');
    
    try {
      await dbPool.transaction(async (client) => {
        await client.query(sql);
        if (direction === 'up') {
          await client.query(
            `INSERT INTO ${MIGRATION_TABLE} (version) VALUES ($1)`,
            [version]
          );
        } else {
          await client.query(
            `DELETE FROM ${MIGRATION_TABLE} WHERE version = $1`,
            [version]
          );
        }
      });
      logger.info({ version, file }, 'Migration completed');
    } catch (error) {
      logger.error({ err: error, version, file }, 'Migration failed');
      throw error;
    }
  }
}

const direction = process.argv[2] === 'down' ? 'down' : 'up';
runMigrations(direction)
  .then(() => {
    logger.info('All migrations completed');
    process.exit(0);
  })
  .catch((err) => {
    logger.error({ err }, 'Migration failed');
    process.exit(1);
  });
```

## src/outbox/types.ts

```typescript
export interface OutboxEvent {
  id: string;
  aggregateId: string;
  aggregateType: string;
  eventType: string;
  payload: Record<string, unknown>;
  metadata: Record<string, unknown>;
  version: number;
  createdAt: Date;
  publishedAt: Date | null;
}

export interface OutboxEventInput {
  aggregateId: string;
  aggregateType: string;
  eventType: string;
  payload: Record<string, unknown>;
  metadata?: Record<string, unknown>;
  version: number;
}

export type EventHandler = (event: OutboxEvent) => Promise<void>;
```

## src/outbox/outbox-writer.ts

```typescript
import { PoolClient } from 'pg';
import { v4 as uuidv4 } from 'uuid';
import { OutboxEventInput, OutboxEvent } from './types';
import pino from 'pino';

const logger = pino({ name: 'outbox-writer' });

export class OutboxWriter {
  /**
   * Atomically updates an aggregate and appends an outbox event in a single transaction.
   * This is the core of the transactional outbox pattern.
   */
  static async writeEvent(
    client: PoolClient,
    input: OutboxEventInput
  ): Promise<OutboxEvent> {
    const eventId = uuidv4();
    const now = new Date();

    const result = await client.query<OutboxEvent>(
      `INSERT INTO outbox_events (id, aggregate_id, aggregate_type, event_type, payload, metadata, version, created_at)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
       RETURNING id, aggregate_id as "aggregateId", aggregate_type as "aggregateType",
                 event_type as "eventType", payload, metadata, version, created_at as "createdAt", published_at as "publishedAt"`,
      [
        eventId,
        input.aggregateId,
        input.aggregateType,
        input.eventType,
        JSON.stringify(input.payload),
        JSON.stringify(input.metadata || {}),
        input.version,
        now
      ]
    );

    const event = result.rows[0];
    logger.debug({ eventId, aggregateId: input.aggregateId, eventType: input.eventType }, 'Outbox event written');
    return event;
  }

  /**
   * Writes multiple outbox events atomically with aggregate updates.
   * All events share the same transaction.
   */
  static async writeEvents(
    client: PoolClient,
    inputs: OutboxEventInput[]
  ): Promise<OutboxEvent[]> {
    const events: OutboxEvent[] = [];
    for (const input of inputs) {
      const event = await this.writeEvent(client, input);
      events.push(event);
    }
    return events;
  }
}
```

## src/aggregates/order-aggregate.ts

```typescript
import { PoolClient } from 'pg';
import { v4 as uuidv4 } from 'uuid';
import { OutboxWriter } from '../outbox/outbox-writer';
import pino from 'pino';

const logger = pino({ name: 'order-aggregate' });

export interface Order {
  id: string;
  customerId: string;
  status: OrderStatus;
  totalAmountCents: number;
  version: number;
  createdAt: Date;
  updatedAt: Date;
}

export type OrderStatus = 'pending' | 'confirmed' | 'shipped' | 'delivered' | 'cancelled';

export interface OrderItem {
  id: string;
  orderId: string;
  productId: string;
  quantity: number;
  unitPriceCents: number;
}

export interface CreateOrderInput {
  customerId: string;
  items: Array<{ productId: string; quantity: number; unitPriceCents: number }>;
}

export class OrderAggregate {
  /**
   * Creates a new order with order items and emits OrderCreated event atomically.
   */
  static async create(
    client: PoolClient,
    input: CreateOrderInput
  ): Promise<Order> {
    const orderId = uuidv4();
    const now = new Date();
    const totalAmountCents = input.items.reduce(
      (sum, item) => sum + item.quantity * item.unitPriceCents,
      0
    );

    // Insert order
    await client.query(
      `INSERT INTO orders (id, customer_id, status, total_amount_cents, version, created_at, updated_at)
       VALUES ($1, $2, $3, $4, $5, $6, $7)`,
      [orderId, input.customerId, 'pending', totalAmountCents, 1, now, now]
    );

    // Insert order items
    for (const item of input.items) {
      await client.query(
        `INSERT INTO order_items (id, order_id, product_id, quantity, unit_price_cents, created_at)
         VALUES ($1, $2, $3, $4, $5, $6)`,
        [uuidv4(), orderId, item.productId, item.quantity, item.unitPriceCents, now]
      );
    }

    // Write outbox event atomically
    await OutboxWriter.writeEvent(client, {
      aggregateId: orderId,
      aggregateType: 'Order',
      eventType: 'OrderCreated',
      payload: {
        orderId,
        customerId: input.customerId,
        totalAmountCents,
        items: input.items
      },
      metadata: { source: 'order-aggregate' },
      version: 1
    });

    logger.info({ orderId, customerId: input.customerId, totalAmountCents }, 'Order created');
    return {
      id: orderId,
      customerId: input.customerId,
      status: 'pending',
      totalAmountCents,
      version: 1,
      createdAt: now,
      updatedAt: now
    };
  }

  /**
   * Confirms an order with optimistic locking and emits OrderConfirmed event.
   */
  static async confirm(
    client: PoolClient,
    orderId: string,
    expectedVersion: number
  ): Promise<Order> {
    const now = new Date();

    // Optimistic lock update
    const result = await client.query<Order>(
      `UPDATE orders 
       SET status = 'confirmed', version = version + 1, updated_at = $1
       WHERE id = $2 AND version = $3
       RETURNING id, customer_id as "customerId", status, total_amount_cents as "totalAmountCents",
                 version, created_at as "createdAt", updated_at as "updatedAt"`,
      [now, orderId, expectedVersion]
    );

    if (result.rowCount === 0) {
      throw new Error(`Order ${orderId} not found or version mismatch (expected ${expectedVersion})`);
    }

    const order = result.rows[0];

    // Write outbox event with new version
    await OutboxWriter.writeEvent(client, {
      aggregateId: orderId,
      aggregateType: 'Order',
      eventType: 'OrderConfirmed',
      payload: { orderId, customerId: order.customerId, totalAmountCents: order.totalAmountCents },
      metadata: { source: 'order-aggregate', previousStatus: 'pending' },
      version: order.version
    });

    logger.info({ orderId, version: order.version }, 'Order confirmed');
    return order;
  }

  /**
   * Ships an order with optimistic locking.
   */
  static async ship(
    client: PoolClient,
    orderId: string,
    expectedVersion: number,
    trackingNumber: string
  ): Promise<Order> {
    const now = new Date();

    const result = await client.query<Order>(
      `UPDATE orders 
       SET status = 'shipped', version = version + 1, updated_at = $1
       WHERE id = $2 AND version = $3
       RETURNING id, customer_id as "customerId", status, total_amount_cents as "totalAmountCents",
                 version, created_at as "createdAt", updated_at as "updatedAt"`,
      [now, orderId, expectedVersion]
    );

    if (result.rowCount === 0) {
      throw new Error(`Order ${orderId} not found or version mismatch`);
    }

    const order = result.rows[0];

    await OutboxWriter.writeEvent(client, {
      aggregateId: orderId,
      aggregateType: 'Order',
      eventType: 'OrderShipped',
      payload: { orderId, customerId: order.customerId, trackingNumber },
      metadata: { source: 'order-aggregate', previousStatus: 'confirmed' },
      version: order.version
    });

    logger.info({ orderId, version: order.version, trackingNumber }, 'Order shipped');
    return order;
  }

  /**
   * Gets order by ID for version checking.
   */
  static async getById(client: PoolClient, orderId: string): Promise<Order | null> {
    const result = await client.query<Order>(
      `SELECT id, customer_id as "customerId", status, total_amount_cents as "totalAmountCents",
              version, created_at as "createdAt", updated_at as "updatedAt"
       FROM orders WHERE id = $1`,
      [orderId]
    );
    return result.rows[0] || null;
  }
}
```

## src/broker/types.ts

```typescript
export interface Message<T = unknown> {
  id: string;
  type: string;
  payload: T;
  metadata: Record<string, unknown>;
  timestamp: Date;
  headers: Record<string, string>;
}

export interface Subscription {
  unsubscribe(): void;
}

export interface Broker {
  publish<T>(topic: string, message: Message<T>): Promise<void>;
  subscribe<T>(topic: string, handler: (message: Message<T>) => Promise<void>): Subscription;
  publishBatch<T>(topic: string, messages: Message<T>[]): Promise<void>;
}
```

## src/broker/local-broker.ts

```typescript
import { Broker, Message, Subscription } from './types';
import pino from 'pino';

const logger = pino({ name: 'local-broker' });

interface HandlerEntry<T> {
  handler: (message: Message<T>) => Promise<void>;
  id: string;
}

export class LocalBroker implements Broker {
  private handlers: Map<string, Map<string, HandlerEntry<unknown>>> = new Map();
  private messageLog: Message[] = [];
  private maxLogSize = 10000;

  publish<T>(topic: string, message: Message<T>): Promise<void> {
    this.messageLog.push(message as Message);
    if (this.messageLog.length > this.maxLogSize) {
      this.messageLog.shift();
    }

    const topicHandlers = this.handlers.get(topic);
    if (!topicHandlers || topicHandlers.size === 0) {
      logger.debug({ topic, messageId: message.id }, 'No subscribers for topic');
      return Promise.resolve();
    }

    const promises: Promise<void>[] = [];
    for (const entry of topicHandlers.values()) {
      promises.push(
        entry.handler(message as Message<T>).catch((err) => {
          logger.error({ err, topic, messageId: message.id, handlerId: entry.id }, 'Handler error');
        })
      );
    }

    return Promise.all(promises).then(() => {});
  }

  async publishBatch<T>(topic: string, messages: Message<T>[]): Promise<void> {
    for (const message of messages) {
      await this.publish(topic, message);
    }
  }

  subscribe<T>(topic: string, handler: (message: Message<T>) => Promise<void>): Subscription {
    if (!this.handlers.has(topic)) {
      this.handlers.set(topic, new Map());
    }

    const handlerId = `${topic}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const entry: HandlerEntry<T> = { handler: handler as (message: Message<unknown>) => Promise<void>, id: handlerId };
    
    this.handlers.get(topic)!.set(handlerId, entry);
    logger.debug({ topic, handlerId }, 'Subscribed to topic');

    return {
      unsubscribe: () => {
        this.handlers.get(topic)?.delete(handlerId);
        logger.debug({ topic, handlerId }, 'Unsubscribed from topic');
      }
    };
  }

  getMessageLog(): Message[] {
    return [...this.messageLog];
  }

  clearLog(): void {
    this.messageLog = [];
  }
}

export const localBroker = new LocalBroker();
```

## src/cdc/types.ts

```typescript
export interface ReplicationMessage {
  lsn: string;
  type: 'insert' | 'update' | 'delete' | 'begin' | 'commit' | 'origin' | 'relation' | 'type';
  data?: {
    relationId: number;
    newTuple?: Record<string, unknown>;
    oldTuple?: Record<string, unknown>;
    keys?: string[];
  };
  timestamp: Date;
}

export interface DecodedOutboxEvent {
  id: string;
  aggregateId: string;
  aggregateType: string;
  eventType: string;
  payload: Record<string, unknown>;
  metadata: Record<string, unknown>;
  version: number;
  createdAt: Date;
  lsn: string;
}

export interface ConsumerOffset {
  consumerGroupId: string;
  replicationSlotName: string;
  lsn: string;
  lastProcessedEventId: string | null;
  lastProcessedAt: Date;
}

export interface ProcessingResult {
  success: boolean;
  processedCount: number;
  failedCount: number;
  lastLsn: string | null;
}
```

## src/cdc/logical-decoder.ts

```typescript
import { ReplicationMessage, DecodedOutboxEvent } from './types';
import pino from 'pino';

const logger = pino({ name: 'logical-decoder' });

// pgoutput message type constants
const MESSAGE_TYPES = {
  BEGIN: 'B',
  COMMIT: 'C',
  ORIGIN: 'O',
  RELATION: 'R',
  TYPE: 'Y',
  INSERT: 'I',
  UPDATE: 'U',
  DELETE: 'D',
  TRUNCATE: 'T'
} as const;

// Column type OIDs for decoding
const TYPE_OIDS = {
  INT2: 21,
  INT4: 23,
  INT8: 20,
  FLOAT4: 700,
  FLOAT8: 701,
  NUMERIC: 1700,
  BOOL: 16,
  VARCHAR: 1043,
  TEXT: 25,
  BYTEA: 17,
  TIMESTAMP: 1114,
  TIMESTAMPTZ: 1184,
  DATE: 1082,
  UUID: 2950,
  JSONB: 3802
} as const;

interface ColumnInfo {
  name: string;
  typeOid: number;
  typeModifier: number;
}

interface RelationInfo {
  relationId: number;
  namespace: string;
  name: string;
  columns: ColumnInfo[];
}

export class LogicalDecoder {
  private relations: Map<number, RelationInfo> = new Map();
  private typeMap: Map<number, string> = new Map();

  constructor() {
    this.initializeTypeMap();
  }

  private initializeTypeMap(): void {
    for (const [name, oid] of Object.entries(TYPE_OIDS)) {
      this.typeMap.set(oid, name);
    }
  }

  /**
   * Decodes a raw pgoutput message buffer into structured ReplicationMessage.
   */
  decode(buffer: Buffer): ReplicationMessage[] {
    const messages: ReplicationMessage[] = [];
    let offset = 0;

    while (offset < buffer.length) {
      const messageType = String.fromCharCode(buffer[offset]);
      offset++;

      try {
        switch (messageType) {
          case MESSAGE_TYPES.BEGIN: {
            const lsn = this.readLSN(buffer, offset);
            offset += 8;
            const timestamp = this.readTimestamp(buffer, offset);
            offset += 8;
            const xid = buffer.readUInt32BE(offset);
            offset += 4;
            messages.push({
              lsn: this.formatLSN(lsn),
              type: 'begin',
              timestamp: new Date(timestamp)
            });
            break;
          }
          case MESSAGE_TYPES.COMMIT: {
            const lsn = this.readLSN(buffer, offset);
            offset += 8;
            const commitLsn = this.readLSN(buffer, offset);
            offset += 8;
            const timestamp = this.readTimestamp(buffer, offset);
            offset += 8;
            messages.push({
              lsn: this.formatLSN(lsn),
              type: 'commit',
              timestamp: new Date(timestamp)
            });
            break;
          }
          case MESSAGE_TYPES.ORIGIN: {
            const lsn = this.readLSN(buffer, offset);
            offset += 8;
            const originLsn = this.readLSN(buffer, offset);
            offset += 8;
            const originName = this.readString(buffer, offset);
            offset += originName.length + 1;
            messages.push({
              lsn: this.formatLSN(lsn),
              type: 'origin',
              timestamp: new Date()
            });
            break;
          }
          case MESSAGE_TYPES.RELATION: {
            const relationId = buffer.readUInt32BE(offset);
            offset += 4;
            const namespace = this.readString(buffer, offset);
            offset += namespace.length + 1;
            const name = this.readString(buffer, offset);
            offset += name.length + 1;
            const replicaIdentity = String.fromCharCode(buffer[offset]);
            offset += 1;
            const columnCount = buffer.readUInt16BE(offset);
            offset += 2;

            const columns: ColumnInfo[] = [];
            for (let i = 0; i < columnCount; i++) {
              const columnName = this.readString(buffer, offset);
              offset += columnName.length + 1;
              const typeOid = buffer.readUInt32BE(offset);
              offset += 4;
              const typeModifier = buffer.readInt32BE(offset);
              offset += 4;
              columns.push({ name: columnName, typeOid, typeModifier });
            }

            this.relations.set(relationId, { relationId, namespace, name, columns });
            messages.push({
              lsn: '',
              type: 'relation',
              data: { relationId, newTuple: { namespace, name, columns } },
              timestamp: new Date()
            });
            break;
          }
          case MESSAGE_TYPES.INSERT:
          case MESSAGE_TYPES.UPDATE:
          case MESSAGE_TYPES.DELETE: {
            const lsn = this.readLSN(buffer, offset);
            offset += 8;
            const relationId = buffer.readUInt32BE(offset);
            offset += 4;

            const relation = this.relations.get(relationId);
            if (!relation) {
              logger.warn({ relationId, lsn: this.formatLSN(lsn) }, 'Unknown relation, skipping');
              // Skip tuple data - we can't decode without relation info
              if (messageType === MESSAGE_TYPES.INSERT || messageType === MESSAGE_TYPES.UPDATE) {
                offset = this.skipTuple(buffer, offset, relation?.columns || []);
              } else if (messageType === MESSAGE_TYPES.UPDATE) {
                offset = this.skipTuple(buffer, offset, relation?.columns || []);
                offset = this.skipTuple(buffer, offset, relation?.columns || []);
              }
              break;
            }

            let newTuple: Record<string, unknown> | undefined;
            let oldTuple: Record<string, unknown> | undefined;

            if (messageType === MESSAGE_TYPES.INSERT) {
              newTuple = this.decodeTuple(buffer, offset, relation.columns);
              offset = this.skipTuple(buffer, offset, relation.columns);
            } else if (messageType === MESSAGE_TYPES.UPDATE) {
              const hasOldTuple = buffer[offset] === 0x4b; // 'K' for key
              if (hasOldTuple) {
                offset++;
                oldTuple = this.decodeTuple(buffer, offset, relation.columns);
                offset = this.skipTuple(buffer, offset, relation.columns);
              } else {
                offset++;
                oldTuple = this.decodeTuple(buffer, offset, relation.columns);
                offset = this.skipTuple(buffer, offset, relation.columns);
              }
              newTuple = this.decodeTuple(buffer, offset, relation.columns);
              offset = this.skipTuple(buffer, offset, relation.columns);
            } else if (messageType === MESSAGE_TYPES.DELETE) {
              const hasOldTuple = buffer[offset] === 0x4b; // 'K' for key
              if (hasOldTuple) {
                offset++;
                oldTuple = this.decodeTuple(buffer, offset, relation.columns);
                offset = this.skipTuple(buffer, offset, relation.columns);
              } else {
                offset++;
                oldTuple = this.decodeTuple(buffer, offset, relation.columns);
                offset = this.skipTuple(buffer, offset, relation.columns);
              }
            }

            messages.push({
              lsn: this.formatLSN(lsn),
              type: messageType === MESSAGE_TYPES.INSERT ? 'insert' : 
                    messageType === MESSAGE_TYPES.UPDATE ? 'update' : 'delete',
              data: { relationId, newTuple, oldTuple, keys: [] },
              timestamp: new Date()
            });
            break;
          }
          case MESSAGE_TYPES.TRUNCATE: {
            const lsn = this.readLSN(buffer, offset);
            offset += 8;
            const relationCount = buffer.readUInt32BE(offset);
            offset += 4;
            for (let i = 0; i < relationCount; i++) {
              const relationId = buffer.readUInt32BE(offset);
              offset += 4;
            }
            messages.push({
              lsn: this.formatLSN(lsn),
              type: 'delete',
              timestamp: new Date()
            });
            break;
          }
          case MESSAGE_TYPES.TYPE: {
            // Skip type message for now
            const typeOid = buffer.readUInt32BE(offset);
            offset += 4;
            const namespace = this.readString(buffer, offset);
            offset += namespace.length + 1;
            const name = this.readString(buffer, offset);
            offset += name.length + 1;
            break;
          }
          default:
            logger.warn({ messageType, offset }, 'Unknown message type, stopping decode');
            return messages;
        }
      } catch (error) {
        logger.error({ err: error, offset, bufferLength: buffer.length }, 'Decode error');
        throw error;
      }
    }

    return messages;
  }

  /**
   * Extracts outbox events from INSERT messages on outbox_events table.
   */
  extractOutboxEvents(messages: ReplicationMessage[]): DecodedOutboxEvent[] {
    const events: DecodedOutboxEvent[] = [];

    for (const msg of messages) {
      if (msg.type === 'insert' && msg.data?.newTuple) {
        const tuple = msg.data.newTuple;
        // Check if this is an outbox_events insert
        if (tuple.table_name === 'outbox_events' || 
            (this.relations.get(msg.data.relationId)?.name === 'outbox_events')) {
          events.push({
            id: tuple.id as string,
            aggregateId: tuple.aggregate_id as string,
            aggregateType: tuple.aggregate_type as string,
            eventType: tuple.event_type as string,
            payload: tuple.payload as Record<string, unknown>,
            metadata: tuple.metadata as Record<string, unknown>,
            version: Number(tuple.version),
            createdAt: new Date(tuple.created_at as string),
            lsn: msg.lsn
          });
        }
      }
    }

    return events;
  }

  private readLSN(buffer: Buffer, offset: number): bigint {
    const high = buffer.readUInt32BE(offset);
    const low = buffer.readUInt32BE(offset + 4);
    return (BigInt(high) << 32n) | BigInt(low);
  }

  private formatLSN(lsn: bigint): string {
    const high = Number(lsn >> 32n);
    const low = Number(lsn & 0xffffffffn);
    return `${high.toString(16).toUpperCase().padStart(8, '0')}/${low.toString(16).toUpperCase().padStart(8, '0')}`;
  }

  private readTimestamp(buffer: Buffer, offset: number): number {
    // PostgreSQL timestamp is microseconds since 2000-01-01
    const high = buffer.readUInt32BE(offset);
    const low = buffer.readUInt32BE(offset + 4);
    const microseconds = (BigInt(high) << 32n) | BigInt(low);
    const pgEpoch = Date.UTC(2000, 0, 1);
    return pgEpoch + Number(microseconds / 1000n);
  }

  private readString(buffer: Buffer, offset: number): string {
    let end = offset;
    while (end < buffer.length && buffer[end] !== 0) {
      end++;
    }
    return buffer.toString('utf-8', offset, end);
  }

  private decodeTuple(buffer: Buffer, offset: number, columns: ColumnInfo[]): Record<string, unknown> {
    const tuple: Record<string, unknown> = {};
    
    // Read number of columns in tuple
    const columnCount = buffer.readUInt16BE(offset);
    offset += 2;

    for (let i = 0; i < columnCount; i++) {
      const column = columns[i];
      const length = buffer.readInt32BE(offset);
      offset += 4;

      if (length === -1) {
        tuple[column.name] = null;
        continue;
      }

      const valueBuffer = buffer.slice(offset, offset + length);
      offset += length;

      tuple[column.name] = this.decodeValue(valueBuffer, column.typeOid);
    }

    return tuple;
  }

  private skipTuple(buffer: Buffer, offset: number, columns: ColumnInfo[]): number {
    const columnCount = buffer.readUInt16BE(offset);
    offset += 2;

    for (let i = 0; i < columnCount; i++) {
      const length = buffer.readInt32BE(offset);
      offset += 4;
      if (length !== -1) {
        offset += length;
      }
    }

    return offset;
  }

  private decodeValue(buffer: Buffer, typeOid: number): unknown {
    switch (typeOid) {
      case TYPE_OIDS.INT2:
        return buffer.readInt16BE(0);
      case TYPE_OIDS.INT4:
        return buffer.readInt32BE(0);
      case TYPE_OIDS.INT8:
        return buffer.readBigInt64BE(0).toString();
      case TYPE_OIDS.FLOAT4:
        return buffer.readFloatBE(0);
      case TYPE_OIDS.FLOAT8:
        return buffer.readDoubleBE(0);
      case TYPE_OIDS.BOOL:
        return buffer[0] === 1;
      case TYPE_OIDS.VARCHAR:
      case TYPE_OIDS.TEXT:
        return buffer.toString('utf-8');
      case TYPE_OIDS.UUID:
        return this.formatUUID(buffer);
      case TYPE_OIDS.JSONB:
        // JSONB has a version byte (0x01) prefix
        return JSON.parse(buffer.slice(1).toString('utf-8'));
      case TYPE_OIDS.TIMESTAMPTZ:
        return this.decodeTimestamptz(buffer);
      default:
        return buffer.toString('utf-8');
    }
  }

  private formatUUID(buffer: Buffer): string {
    const hex = buffer.toString('hex');
    return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
  }

  private decodeTimestamptz(buffer: Buffer): string {
    const microseconds = buffer.readBigInt64BE(0);
    const pgEpoch = Date.UTC(2000, 0, 1);
    const date = new Date(pgEpoch + Number(microseconds / 1000n));
    return date.toISOString();
  }
}
```

## src/cdc/replication-client.ts

```typescript
import { PoolClient } from 'pg';
import { dbPool } from '../db/pool';
import { config } from '../config';
import pino from 'pino';

const logger = pino({ name: 'replication-client' });

export interface ReplicationSlotInfo {
  slotName: string;
  plugin: string;
  database: string;
  active: boolean;
  confirmedFlushLsn: string | null;
}

export class ReplicationClient {
  private client: PoolClient | null = null;
  private isStreaming = false;

  async connect(): Promise<PoolClient> {
    this.client = await dbPool.getReplicationClient();
    return this.client;
  }

  async createReplicationSlot(slotName: string, plugin: string = 'pgoutput'): Promise<void> {
    if (!this.client) throw new Error('Not connected');
    
    await this.client.query(
      `SELECT pg_create_logical_replication_slot($1, $2)`,
      [slotName, plugin]
    );
    logger.info({ slotName, plugin }, 'Replication slot created');
  }

  async dropReplicationSlot(slotName: string): Promise<void> {
    if (!this.client) throw new Error('Not connected');
    
    await this.client.query(
      `SELECT pg_drop_replication_slot($1)`,
      [slotName]
    );
    logger.info({ slotName }, 'Replication slot dropped');
  }

  async getReplicationSlots(): Promise<ReplicationSlotInfo[]> {
    if (!this.client) throw new Error('Not connected');
    
    const result = await this.client.query<ReplicationSlotInfo>(
      `SELECT slot_name as "slotName", plugin, database, active, confirmed_flush_lsn as "confirmedFlushLsn"
       FROM pg_replication_slots`
    );
    return result.rows;
  }

  async startReplication(
    slotName: string,
    startLsn: string | null = null,
    options: Record<string, string> = {}
  ): Promise<void> {
    if (!this.client) throw new Error('Not connected');

    const publicationNames = options['publication_names'] || config.publicationName;
    
    let command = `START_REPLICATION SLOT ${slotName} LOGICAL`;
    if (startLsn) {
      command += ` ${startLsn}`;
    }
    command += ` (FORMAT pgoutput, PUBLICATION_NAMES '${publicationNames}'`;

    if (options['proto_version']) {
      command += `, PROTO_VERSION ${options['proto_version']}`;
    }
    command += ')';

    await this.client.query(command);
    this.isStreaming = true;
    logger.info({ slotName, startLsn, publicationNames }, 'Logical replication started');
  }

  async getReplicationMessages(): Promise<Buffer[]> {
    if (!this.client || !this.isStreaming) {
      throw new Error('Replication not started');
    }

    // Use pg_logical_slot_get_changes for polling mode
    const result = await this.client.query(
      `SELECT data FROM pg_logical_slot_get_changes($1, NULL, NULL, 'format', 'pgoutput', 'include-xids', '0', 'skip-empty-xacts', '1')`,
      [config.replicationSlot]
    );

    return result.rows.map(row => row.data as Buffer);
  }

  async advanceReplicationSlot(lsn: string): Promise<void> {
    if (!this.client) throw new Error('Not connected');
    
    await this.client.query(
      `SELECT pg_replication_slot_advance($1, $2)`,
      [config.replicationSlot, lsn]
    );
  }

  async stopReplication(): Promise<void> {
    if (!this.client) return;
    
    try {
      await this.client.query('IDENTIFY_SYSTEM');
    } catch {
      // Ignore errors during stop
    }
    this.isStreaming = false;
    logger.info('Logical replication stopped');
  }

  async close(): Promise<void> {
    await this.stopReplication();
    if (this.client) {
      this.client.release();
      this.client = null;
    }
  }

  isConnected(): boolean {
    return this.client !== null;
  }

  isStreamingActive(): boolean {
    return this.isStreaming;
  }
}
```

## src/cdc/consumer.ts

```typescript
import { dbPool } from '../db/pool';
import { ReplicationClient } from './replication-client';
import { LogicalDecoder } from './logical-decoder';
import { LocalBroker, Message } from '../broker/local-broker';
import { config } from '../config';
import { DecodedOutboxEvent, ConsumerOffset, ProcessingResult } from './types';
import { PoisonHandler } from '../poison/poison-handler';
import pino from 'pino';

const logger = pino({ name: 'cdc-consumer' });

export class CDCconsumer {
  private replicationClient: ReplicationClient;
  private decoder: LogicalDecoder;
  private broker: LocalBroker;
  private poisonHandler: PoisonHandler;
  private running = false;
  private currentLsn: string | null = null;
  private processedCount = 0;
  private failedCount = 0;

  constructor(broker: LocalBroker, poisonHandler: PoisonHandler) {
    this.replicationClient = new ReplicationClient();
    this.decoder = new LogicalDecoder();
    this.broker = broker;
    this.poisonHandler = poisonHandler;
  }

  async initialize(): Promise<void> {
    await this.replicationClient.connect();
    
    // Ensure replication slot exists
    const slots = await this.replicationClient.getReplicationSlots();
    const slotExists = slots.some(s => s.slotName === config.replicationSlot);
    
    if (!slotExists) {
      await this.replicationClient.createReplicationSlot(config.replicationSlot, 'pgoutput');
      logger.info({ slotName: config.replicationSlot }, 'Created replication slot');
    }

    // Load last processed LSN
    const offset = await this.loadOffset();
    if (offset) {
      this.currentLsn = offset.lsn;
      logger.info({ lsn: this.currentLsn }, 'Resumed from saved offset');
    }

    // Start replication
    await this.replicationClient.startReplication(config.replicationSlot, this.currentLsn || undefined);
  }

  async processBatch(): Promise<ProcessingResult> {
    if (!this.running) {
      return { success: false, processedCount: 0, failedCount: 0, lastLsn: this.currentLsn };
    }

    const messages = await this.replicationClient.getReplicationMessages();
    if (messages.length === 0) {
      return { success: true, processedCount: 0, failedCount: 0, lastLsn: this.currentLsn };
    }

    let batchProcessed = 0;
    let batchFailed = 0;
    let lastLsn: string | null = null;

    for (const msgBuffer of messages) {
      try {
        const decodedMessages = this.decoder.decode(msgBuffer);
        const outboxEvents = this.decoder.extractOutboxEvents(decodedMessages);

        for (const event of outboxEvents) {
          lastLsn = event.lsn;
          const success = await this.processEvent(event);
          if (success) {
            batchProcessed++;
            this.processedCount++;
          } else {
            batchFailed++;
            this.failedCount++;
          }
        }

        // Advance LSN after successful batch processing
        if (lastLsn) {
          await this.replicationClient.advanceReplicationSlot(lastLsn);
          this.currentLsn = lastLsn;
          await this.saveOffset(lastLsn, outboxEvents[outboxEvents.length - 1]?.id || null);
        }
      } catch (error) {
        logger.error({ err: error }, 'Batch processing error');
        batchFailed++;
        this.failedCount++;
      }
    }

    return {
      success: batchFailed === 0,
      processedCount: batchProcessed,
      failedCount: batchFailed,
      lastLsn
    };
  }

  private async processEvent(event: DecodedOutboxEvent): Promise<boolean> {
    try {
      // Check if already processed (idempotency)
      const alreadyProcessed = await this.isEventProcessed(event.id);
      if (alreadyProcessed) {
        logger.debug({ eventId: event.id }, 'Event already processed, skipping');
        return true;
      }

      // Publish to local broker
      const message: Message = {
        id: event.id,
        type: event.eventType,
        payload: event.payload,
        metadata: {
          ...event.metadata,
          aggregateId: event.aggregateId,
          aggregateType: event.aggregateType,
          version: event.version,
          lsn: event.lsn
        },
        timestamp: event.createdAt,
        headers: {
          'x-aggregate-id': event.aggregateId,
          'x-aggregate-type': event.aggregateType,
          'x-event-type': event.eventType,
          'x-version': event.version.toString(),
          'x-lsn': event.lsn
        }
      };

      await this.broker.publish(`outbox.${event.aggregateType.toLowerCase()}`, message);
      
      // Mark as processed
      await this.markEventProcessed(event.id, event.lsn);
      
      logger.debug({ eventId: event.id, aggregateId: event.aggregateId, eventType: event.eventType }, 'Event published');
      return true;
    } catch (error) {
      logger.error({ err: error, eventId: event.id }, 'Event processing failed');
      
      // Handle poison event
      await this.poisonHandler.handlePoisonEvent(event, error as Error);
      return false;
    }
  }

  private async isEventProcessed(eventId: string): Promise<boolean> {
    const result = await dbPool.query(
      `SELECT 1 FROM consumer_offsets WHERE last_processed_event_id = $1`,
      [eventId]
    );
    return result.rowCount > 0;
  }

  private async markEventProcessed(eventId: string, lsn: string): Promise<void> {
    await dbPool.query(
      `UPDATE consumer_offsets 
       SET last_processed_event_id = $1, lsn = $2, last_processed_at = NOW()
       WHERE consumer_group_id = $3 AND replication_slot_name = $4`,
      [eventId, lsn, config.consumerGroupId, config.replicationSlot]
    );
  }

  private async loadOffset(): Promise<ConsumerOffset | null> {
    const result = await dbPool.query<ConsumerOffset>(
      `SELECT consumer_group_id as "consumerGroupId", replication_slot_name as "replicationSlotName",
              lsn, last_processed_event_id as "lastProcessedEventId", last_processed_at as "lastProcessedAt"
       FROM consumer_offsets
       WHERE consumer_group_id = $1 AND replication_slot_name = $2`,
      [config.consumerGroupId, config.replicationSlot]
    );
    return result.rows[0] || null;
  }

  private async saveOffset(lsn: string, lastEventId: string | null): Promise<void> {
    await dbPool.query(
      `INSERT INTO consumer_offsets (consumer_group_id, replication_slot_name, lsn, last_processed_event_id, last_processed_at)
       VALUES ($1, $2, $3, $4, NOW())
       ON CONFLICT (consumer_group_id, replication_slot_name) DO UPDATE SET
         lsn = EXCLUDED.lsn,
         last_processed_event_id = EXCLUDED.last_processed_event_id,
         last_processed_at = NOW()`,
      [config.consumerGroupId, config.replicationSlot, lsn, lastEventId]
    );
  }

  async start(): Promise<void> {
    this.running = true;
    logger.info('CDC consumer started');
    
    while (this.running) {
      try {
        await this.processBatch();
      } catch (error) {
        logger.error({ err: error }, 'Processing loop error');
      }
      
      // Small delay to prevent busy loop
      await new Promise(resolve => setTimeout(resolve, config.pollIntervalMs));
    }
  }

  async stop(): Promise<void> {
    this.running = false;
    await this.replicationClient.close();
    logger.info('CDC consumer stopped');
  }

  getStats() {
    return {
      running: this.running,
      currentLsn: this.currentLsn,
      processedCount: this.processedCount,
      failedCount: this.failedCount
    };
  }
}
```

## src/poison/poison-handler.ts

```typescript
import { dbPool } from '../db/pool';
import { DecodedOutboxEvent } from '../cdc/types';
import { config } from '../config';
import pino from 'pino';

const logger = pino({ name: 'poison-handler' });

export class PoisonHandler {
  private retryCounts: Map<string, number> = new Map();

  async handlePoisonEvent(event: DecodedOutboxEvent, error: Error): Promise<void> {
    const eventKey = `${event.id}:${event.version}`;
    const retryCount = (this.retryCounts.get(eventKey) || 0) + 1;
    this.retryCounts.set(eventKey, retryCount);

    logger.warn({ 
      eventId: event.id, 
      aggregateId: event.aggregateId, 
      eventType: event.eventType,
      retryCount,
      error: error.message 
    }, 'Event processing failed');

    if (retryCount >= config.maxRetries) {
      await this.moveToDeadLetterQueue(event, error, retryCount);
      this.retryCounts.delete(eventKey);
    } else {
      // Schedule retry with exponential backoff
      setTimeout(() => {
        this.retryCounts.delete(eventKey);
      }, config.retryDelayMs * retryCount);
    }
  }

  private async moveToDeadLetterQueue(
    event: DecodedOutboxEvent, 
    error: Error, 
    retryCount: number
  ): Promise<void> {
    try {
      await dbPool.query(
        `INSERT INTO poison_events 
         (original_event_id, aggregate_id, aggregate_type, event_type, payload, metadata, version, error_message, error_stack, retry_count)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)`,
        [
          event.id,
          event.aggregateId,
          event.aggregateType,
          event.eventType,
          JSON.stringify(event.payload),
          JSON.stringify(event.metadata),
          event.version,
          error.message,
          error.stack || '',
          retryCount
        ]
      );

      logger.error({ 
        eventId: event.id, 
        aggregateId: event.aggregateId,
        retryCount 
      }, 'Event moved to poison queue after max retries');
    } catch (dlqError) {
      logger.error({ err: dlqError, originalEventId: event.id }, 'Failed to write to poison queue');
    }
  }

  async getPoisonEvents(limit: number = 100): Promise<Array<{ id: string; event: DecodedOutboxEvent; error: string; retryCount: number }>> {
    const result = await dbPool.query(
      `SELECT id, original_event_id as "originalEventId", aggregate_id as "aggregateId",
              aggregate_type as "aggregateType", event_type as "eventType", payload, metadata, version,
              error_message as "errorMessage", error_stack as "errorStack", retry_count as "retryCount"
       FROM poison_events
       ORDER BY created_at DESC
       LIMIT $1`,
      [limit]
    );

    return result.rows.map(row => ({
      id: row.id,
      event: {
        id: row.originalEventId,
        aggregateId: row.aggregateId,
        aggregateType: row.aggregateType,
        eventType: row.eventType,
        payload: row.payload,
        metadata: row.metadata,
        version: row.version,
        createdAt: new Date(),
        lsn: ''
      },
      error: row.errorMessage,
      retryCount: row.retryCount
    }));
  }

  async retryPoisonEvent(poisonId: string): Promise<boolean> {
    const result = await dbPool.query(
      `DELETE FROM poison_events WHERE id = $1 RETURNING *`,
      [poisonId]
    );
    return result.rowCount > 0;
  }

  async clearPoisonQueue(): Promise<number> {
    const result = await dbPool.query('DELETE FROM poison_events');
    return result.rowCount || 0;
  }
}
```

## src/index.ts

```typescript
import { dbPool } from './db/pool';
import { LocalBroker, localBroker } from './broker/local-broker';
import { CDCconsumer } from './cdc/consumer';
import { PoisonHandler } from './poison/poison-handler';
import { OrderAggregate, CreateOrderInput } from './aggregates/order-aggregate';
import { config } from './config';
import pino from 'pino';

const logger = pino({ name: 'app' });

// Initialize components
const broker = localBroker;
const poisonHandler = new PoisonHandler();
const cdcConsumer = new CDCconsumer(broker, poisonHandler);

// Message handlers for demonstration
const messageHandlers: Map<string, (message: any) => Promise<void>> = new Map();

function registerHandler(eventType: string, handler: (message: any) => Promise<void>): void {
  messageHandlers.set(eventType, handler);
  broker.subscribe(`outbox.order`, async (message) => {
    const handler = messageHandlers.get(message.type);
    if (handler) {
      await handler(message);
    } else {
      logger.warn({ eventType: message.type }, 'No handler for event type');
    }
  });
}

// Example handlers
registerHandler('OrderCreated', async (message) => {
  logger.info({ orderId: message.payload.orderId, customerId: message.payload.customerId }, 'Processing OrderCreated');
  // Simulate business logic: send welcome email, initialize inventory reservation, etc.
});

registerHandler('OrderConfirmed', async (message) => {
  logger.info({ orderId: message.payload.orderId }, 'Processing OrderConfirmed');
  // Simulate business logic: charge payment, notify warehouse, etc.
});

registerHandler('OrderShipped', async (message) => {
  logger.info({ orderId: message.payload.orderId, trackingNumber: message.payload.trackingNumber }, 'Processing OrderShipped');
  // Simulate business logic: send tracking email, update analytics, etc.
});

// Poison event handler for demonstration
registerHandler('PoisonEvent', async (message) => {
  logger.error({ eventId: message.payload.originalEventId, error: message.payload.error }, 'Poison event received');
});

async function runDemo(): Promise<void> {
  try {
    logger.info('Starting transactional outbox CDC demo');

    // Initialize CDC consumer
    await cdcConsumer.initialize();

    // Start consumer in background
    const consumerPromise = cdcConsumer.start();

    // Demo: Create orders and trigger events
    await demoOrderFlow();

    // Give consumer time to process
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Show stats
    const stats = cdcConsumer.getStats();
    logger.info({ stats }, 'Consumer stats');

    // Show poison queue
    const poisonEvents = await poisonHandler.getPoisonEvents();
    logger.info({ poisonCount: poisonEvents.length }, 'Poison queue status');

    // Stop consumer
    await cdcConsumer.stop();
    await consumerPromise;

    logger.info('Demo completed successfully');
  } catch (error) {
    logger.error({ err: error }, 'Demo failed');
    throw error;
  } finally {
    await dbPool.end();
  }
}

async function demoOrderFlow(): Promise<void> {
  logger.info('Starting order flow demo');

  // Create order
  const createInput: CreateOrderInput = {
    customerId: '550e8400-e29b-41d4-a716-446655440000',
    items: [
      { productId: 'prod-1', quantity: 2, unitPriceCents: 2999 },
      { productId: 'prod-2', quantity: 1, unitPriceCents: 4999 }
    ]
  };

  const order = await dbPool.transaction(async (client) => {
    return OrderAggregate.create(client, createInput);
  });

  logger.info({ orderId: order.id, total: order.totalAmountCents }, 'Order created');

  // Confirm order
  const confirmedOrder = await dbPool.transaction(async (client) => {
    return OrderAggregate.confirm(client, order.id, order.version);
  });

  logger.info({ orderId: confirmedOrder.id, version: confirmedOrder.version }, 'Order confirmed');

  // Ship order
  const shippedOrder = await dbPool.transaction(async (client) => {
    return OrderAggregate.ship(client, confirmedOrder.id, confirmedOrder.version, 'TRACK-12345');
  });

  logger.info({ orderId: shippedOrder.id, version: shippedOrder.version }, 'Order shipped');

  // Demonstrate poison event by creating an order with invalid data that will fail in handler
  // (In real scenario, this would be a handler that throws)
  await dbPool.transaction(async (client) => {
    await OrderAggregate.create(client, {
      customerId: '550e8400-e29b-41d4-a716-446655440001',
      items: [{ productId: 'poison-product', quantity: 1, unitPriceCents: 1000 }]
    });
  });

  logger.info('Poison event trigger order created');
}

// Handle graceful shutdown
process.on('SIGINT', async () => {
  logger.info('Shutting down...');
  await cdcConsumer.stop();
  await dbPool.end();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  logger.info('Shutting down...');
  await cdcConsumer.stop();
  await dbPool.end();
  process.exit(0);
});

// Run if executed directly
if (require.main === module) {
  runDemo().catch((err) => {
    logger.error({ err }, 'Application failed');
    process.exit(1);
  });
}

export { broker, cdcConsumer, poisonHandler, runDemo, registerHandler };
```

## tests/setup.ts

```typescript
import { dbPool } from '../src/db/pool';
import { config } from '../src/config';

beforeAll(async () => {
  // Wait for database to be ready
  let retries = 30;
  while (retries > 0) {
    try {
      await dbPool.query('SELECT 1');
      break;
    } catch {
      retries--;
      await new Promise(r => setTimeout(r, 1000));
    }
  }
  
  if (retries === 0) {
    throw new Error('Database not available');
  }
});

afterAll(async () => {
  await dbPool.end();
});
```

## tests/crash-restart.test.ts

```typescript
import { dbPool } from '../src/db/pool';
import { LocalBroker } from '../src/broker/local-broker';
import { CDCconsumer } from '../src/cdc/consumer';
import { PoisonHandler } from '../src/poison/poison-handler';
import { OrderAggregate, CreateOrderInput } from '../src/aggregates/order-aggregate';
import { config } from '../src/config';
import pino from 'pino';

const logger = pino({ name: 'crash-restart-test' });

describe('Crash and Restart Idempotency Test', () => {
  let broker: LocalBroker;
  let poisonHandler: PoisonHandler;
  let processedEvents: Array<{ id: string; type: string; aggregateId: string }> = [];
  let consumer: CDCconsumer;

  beforeAll(async () => {
    // Clean up any existing test data
    await dbPool.query('DELETE FROM orders WHERE customer_id LIKE $1', ['test-crash-%']);
    await dbPool.query('DELETE FROM outbox_events WHERE aggregate_id IN (SELECT id FROM orders WHERE customer_id LIKE $1)', ['test-crash-%']);
    await dbPool.query('DELETE FROM consumer_offsets WHERE consumer_group_id = $1', [config.consumerGroupId]);
    await dbPool.query('DELETE FROM poison_events');
  });

  beforeEach(async () => {
    processedEvents = [];
    broker = new LocalBroker();
    poisonHandler = new PoisonHandler();
    consumer = new CDCconsumer(broker, poisonHandler);

    // Register test handler that records processed events
    broker.subscribe('outbox.order', async (message) => {
      processedEvents.push({
        id: message.id,
        type: message.type,
        aggregateId: message.headers['x-aggregate-id'] || ''
      });
      logger.debug({ eventId: message.id, type: message.type }, 'Test handler processed event');
    });

    await consumer.initialize();
  });

  afterEach(async () => {
    await consumer.stop();
  });

  it('should process events exactly once across crash and restart', async () => {
    // Phase 1: Create orders and generate outbox events
    const orderIds: string[] = [];
    
    for (let i = 0; i < 5; i++) {
      const order = await dbPool.transaction(async (client) => {
        return OrderAggregate.create(client, {
          customerId: `test-crash-${Date.now()}-${i}`,
          items: [{ productId: `prod-${i}`, quantity: 1, unitPriceCents: 1000 * (i + 1) }]
        });
      });
      orderIds.push(order.id);
    }

    // Confirm orders to generate more events
    for (const orderId of orderIds) {
      const order = await OrderAggregate.getById(dbPool.getPool().connect() as any, orderId);
      if (order) {
        await dbPool.transaction(async (client) => {
          return OrderAggregate.confirm(client, orderId, order.version);
        });
      }
    }

    // Phase 2: Start consumer and process first batch
    await consumer.start();
    
    // Wait for initial processing
    await waitForEvents(10, 5000); // 5 orders * 2 events each = 10 events
    
    const eventsAfterFirstRun = [...processedEvents];
    const initialCount = processedEvents.length;
    logger.info({ initialCount }, 'Events processed in first run');

    // Phase 3: Simulate crash - stop consumer without cleaning up
    await consumer.stop();
    
    // Phase 4: Create new consumer instance (simulating restart)
    const newBroker = new LocalBroker();
    const newPoisonHandler = new PoisonHandler();
    const newConsumer = new CDCconsumer(newBroker, newPoisonHandler);
    
    newBroker.subscribe('outbox.order', async (message) => {
      processedEvents.push({
        id: message.id,
        type: message.type,
        aggregateId: message.headers['x-aggregate-id'] || ''
      });
    });

    await newConsumer.initialize();
    await newConsumer.start();

    // Wait for processing after restart
    await waitForEvents(initialCount, 5000); // Should not process more events
    
    const eventsAfterRestart = [...processedEvents];
    
    // Phase 5: Verify idempotency - no duplicate events
    const uniqueEvents = new Set(eventsAfterRestart.map(e => e.id));
    expect(uniqueEvents.size).toBe(eventsAfterRestart.length);
    
    // Should have same number of events (no duplicates)
    expect(eventsAfterRestart.length).toBe(initialCount);
    
    // Verify all original events are present
    for (const event of eventsAfterFirstRun) {
      const found = eventsAfterRestart.find(e => e.id === event.id);
      expect(found).toBeDefined();
      expect(found?.type).toBe(event.type);
    }

    await newConsumer.stop();
  }, 30000);

  it('should handle poison events and not block processing', async () => {
    // Create a failing handler for OrderCreated
    const failingBroker = new LocalBroker();
    const failingPoisonHandler = new PoisonHandler();
    const failingConsumer = new CDCconsumer(failingBroker, failingPoisonHandler);
    
    let failCount = 0;
    failingBroker.subscribe('outbox.order', async (message) => {
      if (message.type === 'OrderCreated') {
        failCount++;
        if (failCount <= 2) {
          throw new Error(`Simulated failure for ${message.id}`);
        }
      }
      processedEvents.push({ id: message.id, type: message.type, aggregateId: message.headers['x-aggregate-id'] || '' });
    });

    await failingConsumer.initialize();
    await failingConsumer.start();

    // Create orders that will trigger poison handling
    for (let i = 0; i < 3; i++) {
      await dbPool.transaction(async (client) => {
        return OrderAggregate.create(client, {
          customerId: `test-poison-${Date.now()}-${i}`,
          items: [{ productId: `poison-prod-${i}`, quantity: 1, unitPriceCents: 1000 }]
        });
      });
    }

    // Wait for processing and retries
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    await failingConsumer.stop();

    // Check poison queue
    const poisonEvents = await failingPoisonHandler.getPoisonEvents();
    expect(poisonEvents.length).toBeGreaterThan(0);
    
    // Verify poison events have correct structure
    for (const pe of poisonEvents) {
      expect(pe.event.eventType).toBe('OrderCreated');
      expect(pe.retryCount).toBeGreaterThanOrEqual(config.maxRetries);
    }

    logger.info({ poisonCount: poisonEvents.length }, 'Poison events captured');
  }, 30000);

  it('should maintain per-aggregate ordering', async () => {
    const orderingBroker = new LocalBroker();
    const orderingPoisonHandler = new PoisonHandler();
    const orderingConsumer = new CDCconsumer(orderingBroker, orderingPoisonHandler);
    
    const aggregate

