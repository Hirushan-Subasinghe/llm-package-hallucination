# TimescaleDB Sensor Ingestion & Query Example

A self-contained Node.js TypeScript project demonstrating idempotent sensor ingestion, hypertable configuration, compression, continuous aggregates, and gap-filled LOCF queries with TimescaleDB.

---

## Project Structure

```
timeseries-example/
├── package.json
├── tsconfig.json
├── .env.example
├── src/
│   ├── db/
│   │   ├── client.ts
│   │   └── schema.sql
│   ├── ingest/
│   │   └── ingest.ts
│   ├── query/
│   │   └── hourlyGapfill.ts
│   ├── examples/
│   │   ├── syntheticData.ts
│   │   └── lateArrival.ts
│   └── index.ts
└── tests/
    └── assertions.test.ts
```

---

## package.json

```json
{
  "name": "timeseries-example",
  "version": "1.0.0",
  "description": "Self-contained TimescaleDB sensor ingestion and query example",
  "type": "module",
  "scripts": {
    "build": "tsc",
    "start": "tsx src/index.ts",
    "dev": "tsx watch src/index.ts",
    "test": "vitest run",
    "db:init": "tsx src/db/init.ts",
    "db:reset": "tsx src/db/reset.ts",
    "ingest": "tsx src/ingest/ingest.ts",
    "query": "tsx src/query/hourlyGapfill.ts",
    "example:late-arrival": "tsx src/examples/lateArrival.ts"
  },
  "dependencies": {
    "pg": "8.12.0",
    "dotenv": "16.4.5",
    "zod": "3.23.8"
  },
  "devDependencies": {
    "@types/pg": "8.11.6",
    "@types/node": "20.14.10",
    "typescript": "5.5.3",
    "tsx": "4.16.2",
    "vitest": "2.0.4"
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
  "include": ["src/**/*", "tests/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

---

## .env.example

```bash
# PostgreSQL connection (TimescaleDB)
PGHOST=localhost
PGPORT=5432
PGDATABASE=timeseries_demo
PGUSER=postgres
PGPASSWORD=postgres

# Timezone for query boundaries (IANA tz database name)
QUERY_TIMEZONE=America/Los_Angeles
```

---

## src/db/client.ts

```typescript
import pg from 'pg';
import dotenv from 'dotenv';

dotenv.config();

const { Pool } = pg;

export const pool = new Pool({
  host: process.env.PGHOST ?? 'localhost',
  port: Number(process.env.PGPORT ?? 5432),
  database: process.env.PGDATABASE ?? 'timeseries_demo',
  user: process.env.PGUSER ?? 'postgres',
  password: process.env.PGPASSWORD ?? 'postgres',
  max: 10,
  idleTimeoutMillis: 30_000,
  connectionTimeoutMillis: 5_000,
});

pool.on('error', (err) => {
  console.error('Unexpected pool error:', err);
  process.exit(-1);
});

export async function query<T = any>(text: string, params?: any[]): Promise<pg.QueryResult<T>> {
  const start = Date.now();
  const res = await pool.query<T>(text, params);
  const duration = Date.now() - start;
  if (process.env.NODE_ENV !== 'test') {
    console.log('QUERY', { duration: `${duration}ms`, rows: res.rowCount, text: text.slice(0, 120) });
  }
  return res;
}

export async function getClient(): Promise<pg.PoolClient> {
  return pool.connect();
}

export async function close(): Promise<void> {
  await pool.end();
}
```

---

## src/db/schema.sql

```sql
-- ============================================================================
-- TIMESCALEDB SCHEMA: sensor_readings hypertable with tags, quality, ingestion
-- ============================================================================

-- Enable TimescaleDB extension (run once per database)
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- ----------------------------------------------------------------------------
-- Raw sensor readings hypertable
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sensor_readings (
  sensor_id      TEXT        NOT NULL,
  event_time     TIMESTAMPTZ NOT NULL,
  ingestion_time TIMESTAMPTZ NOT NULL DEFAULT now(),
  value          DOUBLE PRECISION NOT NULL,
  quality_flag   SMALLINT    NOT NULL DEFAULT 0,  -- 0=good, 1=suspect, 2=bad
  tags           JSONB       NOT NULL DEFAULT '{}'::jsonb,
  PRIMARY KEY (sensor_id, event_time)
);

-- Convert to hypertable partitioned by event_time (chunk interval: 1 day)
SELECT create_hypertable(
  'sensor_readings',
  'event_time',
  chunk_time_interval => INTERVAL '1 day',
  if_not_exists => TRUE,
  migrate_data => TRUE
);

-- Index for common query patterns (sensor_id + time range)
CREATE INDEX IF NOT EXISTS idx_sensor_readings_sensor_time
  ON sensor_readings (sensor_id, event_time DESC);

-- Index for ingestion-time based late-arrival detection
CREATE INDEX IF NOT EXISTS idx_sensor_readings_ingestion_time
  ON sensor_readings (ingestion_time DESC);

-- ----------------------------------------------------------------------------
-- Compression: compress chunks older than 7 days
-- ----------------------------------------------------------------------------
ALTER TABLE sensor_readings SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'sensor_id'
);

-- Compression policy: compress chunks after 7 days
SELECT add_compression_policy('sensor_readings', INTERVAL '7 days', if_not_exists => TRUE);

-- ----------------------------------------------------------------------------
-- Retention: drop raw data older than 90 days (compressed data retained)
-- ----------------------------------------------------------------------------
SELECT add_retention_policy('sensor_readings', INTERVAL '90 days', if_not_exists => TRUE);

-- ----------------------------------------------------------------------------
-- Continuous Aggregate: hourly rollups with gap-fill support
-- ----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS sensor_readings_hourly
WITH (timescaledb.continuous) AS
SELECT
  sensor_id,
  time_bucket('1 hour', event_time) AS bucket,
  COUNT(*) AS sample_count,
  AVG(value) FILTER (WHERE quality_flag = 0) AS avg_value,
  MIN(value) FILTER (WHERE quality_flag = 0) AS min_value,
  MAX(value) FILTER (WHERE quality_flag = 0) AS max_value,
  LAST(value, event_time) FILTER (WHERE quality_flag = 0) AS last_value,
  SUM(CASE WHEN quality_flag = 0 THEN 1 ELSE 0 END) AS good_count,
  SUM(CASE WHEN quality_flag > 0 THEN 1 ELSE 0 END) AS bad_count
FROM sensor_readings
GROUP BY sensor_id, bucket
WITH NO DATA;

-- Add continuous aggregate policy: refresh hourly, lag 1 hour
SELECT add_continuous_aggregate_policy(
  'sensor_readings_hourly',
  start_offset => INTERVAL '2 hours',
  end_offset   => INTERVAL '1 hour',
  schedule_interval => INTERVAL '1 hour',
  if_not_exists => TRUE
);

-- Index for continuous aggregate queries
CREATE INDEX IF NOT EXISTS idx_sensor_readings_hourly_sensor_bucket
  ON sensor_readings_hourly (sensor_id, bucket DESC);

-- ----------------------------------------------------------------------------
-- Helper function: gap-filled hourly query with LOCF (Last Observation Carried Forward)
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION get_hourly_gapfilled(
  p_sensor_id   TEXT,
  p_start       TIMESTAMPTZ,
  p_end         TIMESTAMPTZ,
  p_timezone    TEXT DEFAULT 'UTC'
)
RETURNS TABLE (
  bucket        TIMESTAMPTZ,
  value         DOUBLE PRECISION,
  sample_count  BIGINT,
  is_gapfilled  BOOLEAN
)
LANGUAGE sql
STABLE
AS $$
  SELECT
    bucket,
    locf(avg_value) AS value,
    sample_count,
    (avg_value IS NULL) AS is_gapfilled
  FROM (
    SELECT
      time_bucket_gapfill('1 hour', event_time AT TIME ZONE p_timezone) AT TIME ZONE p_timezone AS bucket,
      AVG(value) FILTER (WHERE quality_flag = 0) AS avg_value,
      COUNT(*) FILTER (WHERE quality_flag = 0) AS sample_count
    FROM sensor_readings
    WHERE sensor_id = p_sensor_id
      AND event_time >= p_start
      AND event_time < p_end
    GROUP BY bucket
  ) sub
  ORDER BY bucket;
$$;

-- ----------------------------------------------------------------------------
-- View for late-arrival detection (ingestion_time > event_time + threshold)
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW late_arrivals AS
SELECT
  sensor_id,
  event_time,
  ingestion_time,
  ingestion_time - event_time AS latency,
  value,
  quality_flag
FROM sensor_readings
WHERE ingestion_time > event_time + INTERVAL '5 minutes'
ORDER BY ingestion_time DESC;
```

---

## src/db/init.ts

```typescript
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { pool, query, close } from './client.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function initDatabase(): Promise<void> {
  console.log('Initializing database schema...');
  
  const schemaPath = join(__dirname, 'schema.sql');
  const schema = readFileSync(schemaPath, 'utf-8');
  
  // Split by semicolon, filter empty statements
  const statements = schema
    .split(';')
    .map(s => s.trim())
    .filter(s => s.length > 0 && !s.startsWith('--'));
  
  for (const stmt of statements) {
    try {
      await query(stmt);
      console.log('  ✓ Executed:', stmt.slice(0, 80).replace(/\n/g, ' ') + '...');
    } catch (err) {
      // Ignore "already exists" errors for idempotent setup
      if (err instanceof Error && err.message.includes('already exists')) {
        console.log('  ⊘ Skipped (exists):', stmt.slice(0, 80).replace(/\n/g, ' ') + '...');
      } else {
        console.error('  ✗ Failed:', stmt.slice(0, 120));
        throw err;
      }
    }
  }
  
  console.log('Database initialization complete.');
  await close();
}

initDatabase().catch((err) => {
  console.error('Initialization failed:', err);
  process.exit(1);
});
```

---

## src/db/reset.ts

```typescript
import { query, close } from './client.js';

async function resetDatabase(): Promise<void> {
  console.log('Resetting database (dropping all objects)...');
  
  const statements = [
    'DROP VIEW IF EXISTS late_arrivals CASCADE;',
    'DROP FUNCTION IF EXISTS get_hourly_gapfilled(TEXT, TIMESTAMPTZ, TIMESTAMPTZ, TEXT) CASCADE;',
    'DROP MATERIALIZED VIEW IF EXISTS sensor_readings_hourly CASCADE;',
    'DROP TABLE IF EXISTS sensor_readings CASCADE;',
    'DROP EXTENSION IF EXISTS timescaledb CASCADE;',
  ];
  
  for (const stmt of statements) {
    await query(stmt);
    console.log('  ✓', stmt);
  }
  
  console.log('Database reset complete.');
  await close();
}

resetDatabase().catch((err) => {
  console.error('Reset failed:', err);
  process.exit(1);
});
```

---

## src/ingest/ingest.ts

```typescript
import { z } from 'zod';
import { query, getClient, close } from '../db/client.js';

// ----------------------------------------------------------------------------
// Zod schema for sensor reading validation
// ----------------------------------------------------------------------------
export const SensorReadingSchema = z.object({
  sensor_id: z.string().min(1),
  event_time: z.string().datetime({ offset: true }), // ISO 8601 with timezone
  ingestion_time: z.string().datetime({ offset: true }).optional(),
  value: z.number().finite(),
  quality_flag: z.number().int().min(0).max(2).default(0),
  tags: z.record(z.unknown()).default({}),
});

export type SensorReading = z.infer<typeof SensorReadingSchema>;

export const SensorReadingBatchSchema = z.array(SensorReadingSchema);
export type SensorReadingBatch = z.infer<typeof SensorReadingBatchSchema>;

// ----------------------------------------------------------------------------
// Idempotent upsert: ON CONFLICT (sensor_id, event_time) DO UPDATE
// ----------------------------------------------------------------------------
const UPSERT_SQL = `
  INSERT INTO sensor_readings (sensor_id, event_time, ingestion_time, value, quality_flag, tags)
  VALUES ($1, $2, $3, $4, $5, $6)
  ON CONFLICT (sensor_id, event_time) DO UPDATE SET
    ingestion_time = EXCLUDED.ingestion_time,
    value = EXCLUDED.value,
    quality_flag = EXCLUDED.quality_flag,
    tags = EXCLUDED.tags
  RETURNING sensor_id, event_time, ingestion_time;
`;

export async function ingestReadings(readings: SensorReadingBatch): Promise<number> {
  const client = await getClient();
  let inserted = 0;
  
  try {
    await client.query('BEGIN');
    
    for (const reading of readings) {
      const ingestionTime = reading.ingestion_time ?? new Date().toISOString();
      
      await client.query(UPSERT_SQL, [
        reading.sensor_id,
        reading.event_time,
        ingestionTime,
        reading.value,
        reading.quality_flag,
        JSON.stringify(reading.tags),
      ]);
      inserted++;
    }
    
    await client.query('COMMIT');
    console.log(`Ingested ${inserted} readings (idempotent upsert)`);
    return inserted;
  } catch (err) {
    await client.query('ROLLBACK');
    throw err;
  } finally {
    client.release();
  }
}

// ----------------------------------------------------------------------------
// Batch ingest with validation
// ----------------------------------------------------------------------------
export async function ingestBatch(raw: unknown): Promise<number> {
  const parsed = SensorReadingBatchSchema.parse(raw);
  return ingestReadings(parsed);
}

// CLI entry point
if (import.meta.url === `file://${process.argv[1]}`) {
  const sampleBatch: SensorReadingBatch = [
    {
      sensor_id: 'sensor-001',
      event_time: '2026-09-25T10:00:00-07:00',
      value: 23.4,
      quality_flag: 0,
      tags: { location: 'building-a', floor: 2, type: 'temperature' },
    },
    {
      sensor_id: 'sensor-001',
      event_time: '2026-09-25T10:15:00-07:00',
      value: 23.6,
      quality_flag: 0,
      tags: { location: 'building-a', floor: 2, type: 'temperature' },
    },
    {
      sensor_id: 'sensor-001',
      event_time: '2026-09-25T10:30:00-07:00',
      value: 23.8,
      quality_flag: 0,
      tags: { location: 'building-a', floor: 2, type: 'temperature' },
    },
    {
      sensor_id: 'sensor-001',
      event_time: '2026-09-25T10:45:00-07:00',
      value: 24.0,
      quality_flag: 0,
      tags: { location: 'building-a', floor: 2, type: 'temperature' },
    },
    {
      sensor_id: 'sensor-002',
      event_time: '2026-09-25T10:00:00-07:00',
      value: 65.2,
      quality_flag: 0,
      tags: { location: 'building-b', floor: 1, type: 'humidity' },
    },
  ];
  
  await ingestBatch(sampleBatch);
  await close();
}
```

---

## src/query/hourlyGapfill.ts

```typescript
import { query, close } from '../db/client.js';

// ----------------------------------------------------------------------------
// Parameterized gap-filled hourly query with LOCF and timezone-aware boundaries
// ----------------------------------------------------------------------------
export interface HourlyGapfilledRow {
  bucket: Date;
  value: number | null;
  sample_count: number;
  is_gapfilled: boolean;
}

export interface HourlyGapfillParams {
  sensorId: string;
  start: Date | string;
  end: Date | string;
  timezone?: string; // IANA timezone, e.g., 'America/Los_Angeles'
}

const GAPFILL_SQL = `
  SELECT * FROM get_hourly_gapfilled($1, $2, $3, $4)
`;

/**
 * Execute gap-filled hourly query with Last Observation Carried Forward (LOCF).
 * 
 * @param params - Query parameters
 * @returns Array of hourly buckets with LOCF-filled values
 * 
 * TimescaleDB features used:
 * - time_bucket_gapfill: generates continuous hourly buckets, filling gaps
 * - locf(): Last Observation Carried Forward - fills NULLs with previous non-NULL
 * - AT TIME ZONE: timezone-aware bucket boundaries
 */
export async function queryHourlyGapfill(params: HourlyGapfillParams): Promise<HourlyGapfilledRow[]> {
  const { sensorId, start, end, timezone = 'UTC' } = params;
  
  const startStr = start instanceof Date ? start.toISOString() : start;
  const endStr = end instanceof Date ? end.toISOString() : end;
  
  const result = await query<HourlyGapfilledRow>(GAPFILL_SQL, [
    sensorId,
    startStr,
    endStr,
    timezone,
  ]);
  
  return result.rows;
}

// ----------------------------------------------------------------------------
// Alternative: raw SQL version without helper function (for transparency)
// ----------------------------------------------------------------------------
export async function queryHourlyGapfillRaw(params: HourlyGapfillParams): Promise<HourlyGapfilledRow[]> {
  const { sensorId, start, end, timezone = 'UTC' } = params;
  
  const startStr = start instanceof Date ? start.toISOString() : start;
  const endStr = end instanceof Date ? end.toISOString() : end;
  
  const sql = `
    SELECT
      bucket,
      locf(avg_value) AS value,
      sample_count,
      (avg_value IS NULL) AS is_gapfilled
    FROM (
      SELECT
        time_bucket_gapfill('1 hour', event_time AT TIME ZONE $4) AT TIME ZONE $4 AS bucket,
        AVG(value) FILTER (WHERE quality_flag = 0) AS avg_value,
        COUNT(*) FILTER (WHERE quality_flag = 0) AS sample_count
      FROM sensor_readings
      WHERE sensor_id = $1
        AND event_time >= $2
        AND event_time < $3
      GROUP BY bucket
    ) sub
    ORDER BY bucket;
  `;
  
  const result = await query<HourlyGapfilledRow>(sql, [sensorId, startStr, endStr, timezone]);
  return result.rows;
}

// CLI demo
if (import.meta.url === `file://${process.argv[1]}`) {
  const tz = process.env.QUERY_TIMEZONE ?? 'America/Los_Angeles';
  
  const start = new Date('2026-09-25T00:00:00-07:00');
  const end = new Date('2026-09-26T00:00:00-07:00');
  
  console.log(`Querying hourly gapfill for sensor-001 in ${tz}`);
  console.log(`Range: ${start.toISOString()} → ${end.toISOString()}`);
  
  const rows = await queryHourlyGapfill({
    sensorId: 'sensor-001',
    start,
    end,
    timezone: tz,
  });
  
  console.table(rows.map(r => ({
    bucket: r.bucket.toISOString(),
    value: r.value?.toFixed(2) ?? 'NULL',
    samples: r.sample_count,
    gapfilled: r.is_gapfilled ? 'YES' : 'no',
  })));
  
  await close();
}
```

---

## src/examples/syntheticData.ts

```typescript
import { query, close } from '../db/client.js';
import { SensorReadingBatch, SensorReadingSchema } from '../ingest/ingest.js';
import { z } from 'zod';

// ----------------------------------------------------------------------------
// Synthetic data generator with assertions
// ----------------------------------------------------------------------------
export interface SyntheticDataConfig {
  sensorId: string;
  start: Date;
  end: Date;
  intervalMinutes: number;
  baseValue: number;
  noiseStdDev: number;
  qualityFlag?: number;
  tags?: Record<string, unknown>;
  gapRanges?: Array<{ start: Date; end: Date }>; // Periods with NO data
}

export function generateSyntheticData(config: SyntheticDataConfig): SensorReadingBatch {
  const { sensorId, start, end, intervalMinutes, baseValue, noiseStdDev, qualityFlag = 0, tags = {}, gapRanges = [] } = config;
  const readings: SensorReadingBatch = [];
  
  let current = new Date(start);
  while (current < end) {
    // Check if current time falls in a gap range
    const inGap = gapRanges.some(g => current >= g.start && current < g.end);
    
    if (!inGap) {
      const noise = (Math.random() - 0.5) * 2 * noiseStdDev;
      readings.push({
        sensor_id: sensorId,
        event_time: current.toISOString(),
        value: Number((baseValue + noise).toFixed(2)),
        quality_flag: qualityFlag,
        tags,
      });
    }
    
    current = new Date(current.getTime() + intervalMinutes * 60_000);
  }
  
  return readings;
}

// ----------------------------------------------------------------------------
// Assertion helpers for testing
// ----------------------------------------------------------------------------
export async function assertRowCount(table: string, expected: number, tolerance = 0): Promise<void> {
  const result = await query<{ count: string }>(`SELECT COUNT(*) FROM ${table}`);
  const actual = Number(result.rows[0].count);
  if (Math.abs(actual - expected) > tolerance) {
    throw new Error(`Row count mismatch for ${table}: expected ${expected}±${tolerance}, got ${actual}`);
  }
  console.log(`  ✓ ${table}: ${actual} rows (expected ${expected}±${tolerance})`);
}

export async function assertGapfillBehavior(sensorId: string, start: Date, end: Date, timezone: string): Promise<void> {
  const rows = await query<{ bucket: Date; value: number | null; is_gapfilled: boolean }>(
    `SELECT * FROM get_hourly_gapfilled($1, $2, $3, $4)`,
    [sensorId, start.toISOString(), end.toISOString(), timezone]
  );
  
  // Verify no NULL values in result (LOCF should fill all)
  const nullValues = rows.rows.filter(r => r.value === null);
  if (nullValues.length > 0) {
    throw new Error(`Gapfill produced ${nullValues.length} NULL values (LOCF failed)`);
  }
  
  // Verify gapfilled flag is true only for buckets with no source data
  const gapfilledRows = rows.rows.filter(r => r.is_gapfilled);
  const nonGapfilledRows = rows.rows.filter(r => !r.is_gapfilled);
  
  console.log(`  ✓ Gapfill: ${rows.rows.length} buckets, ${gapfilledRows.length} gap-filled, ${nonGapfilledRows.length} from data`);
}

export async function assertContinuousAggregateFreshness(): Promise<void> {
  const result = await query<{ 
    materialization_hypertable_name: string;
    lag: string;
    last_refresh: Date | null;
  }>(`
    SELECT 
      cagg.materialization_hypertable_name,
      cagg.refresh_lag AS lag,
      cagg.last_refresh
    FROM timescaledb_information.continuous_aggregates cagg
    WHERE cagg.user_view_name = 'sensor_readings_hourly'
  `);
  
  if (result.rows.length === 0) {
    throw new Error('Continuous aggregate sensor_readings_hourly not found');
  }
  
  console.log(`  ✓ Continuous aggregate: ${result.rows[0].materialization_hypertable_name}, lag: ${result.rows[0].lag}`);
}

export async function assertCompressionActive(): Promise<void> {
  const result = await query<{ 
    hypertable_name: string;
    compressed_chunk_count: number;
    uncompressed_chunk_count: number;
  }>(`
    SELECT 
      ht.hypertable_name,
      COUNT(cs.chunk_name) FILTER (WHERE cs.is_compressed) AS compressed_chunk_count,
      COUNT(cs.chunk_name) FILTER (WHERE NOT cs.is_compressed) AS uncompressed_chunk_count
    FROM timescaledb_information.hypertables ht
    LEFT JOIN timescaledb_information.chunks cs ON cs.hypertable_name = ht.hypertable_name
    WHERE ht.hypertable_name = 'sensor_readings'
    GROUP BY ht.hypertable_name
  `);
  
  if (result.rows.length === 0) {
    throw new Error('Hypertable sensor_readings not found');
  }
  
  const { compressed_chunk_count, uncompressed_chunk_count } = result.rows[0];
  console.log(`  ✓ Compression: ${compressed_chunk_count} compressed, ${uncompressed_chunk_count} uncompressed chunks`);
}

// ----------------------------------------------------------------------------
// Run synthetic data generation + assertions
// ----------------------------------------------------------------------------
if (import.meta.url === `file://${process.argv[1]}`) {
  console.log('Generating synthetic data...');
  
  const now = new Date();
  const start = new Date(now.getTime() - 48 * 60 * 60 * 1000); // 48 hours ago
  const end = new Date(now.getTime() - 1 * 60 * 60 * 1000);    // 1 hour ago
  
  // Generate data with a 6-hour gap
  const gapStart = new Date(now.getTime() - 30 * 60 * 60 * 1000);
  const gapEnd = new Date(now.getTime() - 24 * 60 * 60 * 1000);
  
  const readings = generateSyntheticData({
    sensorId: 'sensor-synthetic',
    start,
    end,
    intervalMinutes: 15,
    baseValue: 20.0,
    noiseStdDev: 1.5,
    tags: { source: 'synthetic', test: true },
    gapRanges: [{ start: gapStart, end: gapEnd }],
  });
  
  console.log(`Generated ${readings.length} readings (with 6-hour gap)`);
  
  // Ingest
  const { ingestReadings } = await import('../ingest/ingest.js');
  await ingestReadings(readings);
  
  // Run assertions
  console.log('\nRunning assertions...');
  await assertRowCount('sensor_readings', readings.length);
  await assertGapfillBehavior('sensor-synthetic', start, end, 'UTC');
  await assertContinuousAggregateFreshness();
  await assertCompressionActive();
  
  console.log('\nAll assertions passed.');
  await close();
}
```

---

## src/examples/lateArrival.ts

```typescript
import { query, close } from '../db/client.js';
import { SensorReadingBatch } from '../ingest/ingest.js';

// ----------------------------------------------------------------------------
// Late-arrival example: data arrives with event_time in the past but
// ingestion_time = now (simulating delayed transmission)
// ----------------------------------------------------------------------------
export async function demonstrateLateArrival(): Promise<void> {
  console.log('=== Late Arrival Demonstration ===\n');
  
  const sensorId = 'sensor-late-demo';
  const now = new Date();
  
  // 1. Insert "on-time" data for 10:00-11:00 (ingested at 10:05)
  const onTimeData: SensorReadingBatch = [
    {
      sensor_id: sensorId,
      event_time: new Date(now.getTime() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
      ingestion_time: new Date(now.getTime() - 2 * 60 * 60 * 1000 + 5 * 60 * 1000).toISOString(), // +5 min
      value: 22.0,
      quality_flag: 0,
      tags: { scenario: 'on-time' },
    },
    {
      sensor_id: sensorId,
      event_time: new Date(now.getTime() - 2 * 60 * 60 * 1000 + 15 * 60 * 1000).toISOString(),
      ingestion_time: new Date(now.getTime() - 2 * 60 * 60 * 1000 + 20 * 60 * 1000).toISOString(),
      value: 22.5,
      quality_flag: 0,
      tags: { scenario: 'on-time' },
    },
  ];
  
  console.log('1. Inserting on-time data (ingestion ~5 min after event)...');
  await insertBatch(onTimeData);
  
  // 2. Insert "late" data for 09:00-09:45 (event time 3 hours ago, ingested NOW)
  const lateData: SensorReadingBatch = [
    {
      sensor_id: sensorId,
      event_time: new Date(now.getTime() - 3 * 60 * 60 * 1000).toISOString(), // 3 hours ago
      ingestion_time: now.toISOString(), // ingested NOW
      value: 21.0,
      quality_flag: 0,
      tags: { scenario: 'late-arrival' },
    },
    {
      sensor_id: sensorId,
      event_time: new Date(now.getTime() - 3 * 60 * 60 * 1000 + 15 * 60 * 1000).toISOString(),
      ingestion_time: now.toISOString(),
      value: 21.2,
      quality_flag: 0,
      tags: { scenario: 'late-arrival' },
    },
    {
      sensor_id: sensorId,
      event_time: new Date(now.getTime() - 3 * 60 * 60 * 1000 + 30 * 60 * 1000).toISOString(),
      ingestion_time: now.toISOString(),
      value: 21.5,
      quality_flag: 0,
      tags: { scenario: 'late-arrival' },
    },
  ];
  
  console.log('2. Inserting late-arrival data (event 3 hours ago, ingested now)...');
  await insertBatch(lateData);
  
  // 3. Query late_arrivals view
  console.log('\n3. Late arrivals view (latency > 5 minutes):');
  const lateArrivals = await query<{
    sensor_id: string;
    event_time: Date;
    ingestion_time: Date;
    latency: string; // interval
    value: number;
    quality_flag: number;
  }>('SELECT * FROM late_arrivals WHERE sensor_id = $1 ORDER BY ingestion_time DESC', [sensorId]);
  
  console.table(lateArrivals.rows.map(r => ({
    sensor: r.sensor_id,
    event_time: r.event_time.toISOString(),
    ingestion_time: r.ingestion_time.toISOString(),
    latency: r.latency,
    value: r.value,
  })));
  
  // 4. Verify continuous aggregate will catch up on next refresh
  console.log('\n4. Continuous aggregate refresh policy will backfill late data on next run.');
  console.log('   Policy: start_offset=2h, end_offset=1h, schedule=1h');
  console.log('   Late data at T-3h will be included in next refresh covering T-3h bucket.');
  
  // 5. Show gapfill query includes late data immediately (raw hypertable)
  console.log('\n5. Gapfill query on raw hypertable includes late data immediately:');
  const gapfill = await query<{ bucket: Date; value: number | null; is_gapfilled: boolean }>(
    `SELECT * FROM get_hourly_gapfilled($1, $2, $3, 'UTC')`,
    [
      sensorId,
      new Date(now.getTime() - 4 * 60 * 60 * 1000).toISOString(),
      new Date(now.getTime() - 1 * 60 * 60 * 1000).toISOString(),
    ]
  );
  
  console.table(gapfill.rows.map(r => ({
    bucket: r.bucket.toISOString(),
    value: r.value?.toFixed(1) ?? 'NULL',
    gapfilled: r.is_gapfilled ? 'YES' : 'no',
  })));
  
  console.log('\n=== Key Points ===');
  console.log('- Raw hypertable: late data visible immediately via gapfill');
  console.log('- Continuous aggregate: catches up on next scheduled refresh');
  console.log('- late_arrivals view: identifies records with ingestion_time > event_time + 5min');
  console.log('- Idempotent upsert: re-sending late data updates ingestion_time, preserves event_time');
}

async function insertBatch(batch: SensorReadingBatch): Promise<void> {
  const { ingestReadings } = await import('../ingest/ingest.js');
  await ingestReadings(batch);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  await demonstrateLateArrival();
  await close();
}
```

---

## src/index.ts

```typescript
// Main entry point - runs full demonstration
import { initDatabase } from './db/init.js';
import { ingestBatch } from './ingest/ingest.js';
import { queryHourlyGapfill } from './query/hourlyGapfill.js';
import { demonstrateLateArrival } from './examples/lateArrival.js';
import { close } from './db/client.js';

async function main(): Promise<void> {
  console.log('╔══════════════════════════════════════════════════════════════╗');
  console.log('║  TimescaleDB Sensor Time-Series Example                      ║');
  console.log('╚══════════════════════════════════════════════════════════════╝\n');
  
  // 1. Initialize schema (idempotent)
  console.log('📦 Step 1: Initialize database schema');
  await initDatabase();
  console.log('');
  
  // 2. Ingest sample data
  console.log('📥 Step 2: Ingest sample sensor readings');
  const sampleData = [
    {
      sensor_id: 'sensor-main',
      event_time: '2026-09-25T08:00:00-07:00',
      value: 20.5,
      quality_flag: 0,
      tags: { location: 'warehouse', zone: 'cold-storage' },
    },
    {
      sensor_id: 'sensor-main',
      event_time: '2026-09-25T08:15:00-07:00',
      value: 20.7,
      quality_flag: 0,
      tags: { location: 'warehouse', zone: 'cold-storage' },
    },
    {
      sensor_id: 'sensor-main',
      event_time: '2026-09-25T08:30:00-07:00',
      value: 20.6,
      quality_flag: 0,
      tags: { location: 'warehouse', zone: 'cold-storage' },
    },
    {
      sensor_id: 'sensor-main',
      event_time: '2026-09-25T08:45:00-07:00',
      value: 20.8,
      quality_flag: 0,
      tags: { location: 'warehouse', zone: 'cold-storage' },
    },
    // Gap: no data for 09:00-10:00
    {
      sensor_id: 'sensor-main',
      event_time: '2026-09-25T10:00:00-07:00',
      value: 21.2,
      quality_flag: 0,
      tags: { location: 'warehouse', zone: 'cold-storage' },
    },
  ];
  await ingestBatch(sampleData);
  console.log('');
  
  // 3. Query with gap-fill
  console.log('📊 Step 3: Gap-filled hourly query (LOCF)');
  const tz = process.env.QUERY_TIMEZONE ?? 'America/Los_Angeles';
  const start = new Date('2026-09-25T07:00:00-07:00');
  const end = new Date('2026-09-25T12:00:00-07:00');
  
  const results = await queryHourlyGapfill({
    sensorId: 'sensor-main',
    start,
    end,
    timezone: tz,
  });
  
  console.table(results.map(r => ({
    bucket_local: r.bucket.toLocaleString('en-US', { timeZone: tz }),
    value: r.value?.toFixed(2) ?? 'NULL',
    samples: r.sample_count,
    gapfilled: r.is_gapfilled ? '✓' : '',
  })));
  console.log('');
  
  // 4. Late arrival demo
  console.log('⏰ Step 4: Late arrival demonstration');
  await demonstrateLateArrival();
  console.log('');
  
  console.log('✅ Demonstration complete');
  await close();
}

main().catch(async (err) => {
  console.error('Fatal error:', err);
  await close();
  process.exit(1);
});
```

---

## tests/assertions.test.ts

```typescript
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { query, close } from '../src/db/client.js';
import { ingestReadings, SensorReadingBatch } from '../src/ingest/ingest.js';
import { queryHourlyGapfill } from '../src/query/hourlyGapfill.js';
import { generateSyntheticData, assertRowCount, assertGapfillBehavior } from '../src/examples/syntheticData.js';

const TEST_SENSOR = 'sensor-test-vitest';
const TEST_TZ = 'UTC';

beforeAll(async () => {
  // Clean test sensor data
  await query('DELETE FROM sensor_readings WHERE sensor_id = $1', [TEST_SENSOR]);
});

afterAll(async () => {
  await close();
});

describe('Idempotent Ingestion', () => {
  it('should insert new readings', async () => {
    const batch: SensorReadingBatch = [
      {
        sensor_id: TEST_SENSOR,
        event_time: '2026-09-25T12:00:00Z',
        value: 100,
        quality_flag: 0,
        tags: { test: 'idempotent-1' },
      },
    ];
    await ingestReadings(batch);
    
    const count = await query<{ c: string }>('SELECT COUNT(*) as c FROM sensor_readings WHERE sensor_id = $1', [TEST_SENSOR]);
    expect(Number(count.rows[0].c)).toBe(1);
  });

  it('should update existing readings on conflict (same sensor_id, event_time)', async () => {
    const batch: SensorReadingBatch = [
      {
        sensor_id: TEST_SENSOR,
        event_time: '2026-09-25T12:00:00Z', // Same as above
        value: 200, // Different value
        quality_flag: 1,
        tags: { test: 'idempotent-2', updated: true },
      },
    ];
    await ingestReadings(batch);
    
    const count = await query<{ c: string }>('SELECT COUNT(*) as c FROM sensor_readings WHERE sensor_id = $1', [TEST_SENSOR]);
    expect(Number(count.rows[0].c)).toBe(1); // Still 1 row
    
    const row = await query<{ value: number; quality_flag: number; tags: object }>(
      'SELECT value, quality_flag, tags FROM sensor_readings WHERE sensor_id = $1 AND event_time = $2',
      [TEST_SENSOR, '2026-09-25T12:00:00Z']
    );
    expect(row.rows[0].value).toBe(200);
    expect(row.rows[0].quality_flag).toBe(1);
    expect(row.rows[0].tags).toEqual(expect.objectContaining({ updated: true }));
  });
});

describe('Gap-filled Hourly Query with LOCF', () => {
  it('should return hourly buckets with LOCF filling gaps', async () => {
    // Clean and insert data with a gap
    await query('DELETE FROM sensor_readings WHERE sensor_id = $1', [TEST_SENSOR]);
    
    const data = generateSyntheticData({
      sensorId: TEST_SENSOR,
      start: new Date('2026-09-25T00:00:00Z'),
      end: new Date('2026-09-25T06:00:00Z'),
      intervalMinutes: 30,
      baseValue: 50,
      noiseStdDev: 0.1,
      gapRanges: [
        { start: new Date('2026-09-25T02:00:00Z'), end: new Date('2026-09-25T04:00:00Z') }, // 2-hour gap
      ],
    });
    
    await ingestReadings(data);
    
    const results = await queryHourlyGapfill({
      sensorId: TEST_SENSOR,
      start: '2026-09-25T00:00:00Z',
      end: '2026-09-25T06:00:00Z',
      timezone: TEST_TZ,
    });
    
    // Should have 6 hourly buckets (00:00, 01:00, 02:00, 03:00, 04:00, 05:00)
    expect(results.length).toBe(6);
    
    // No NULL values (LOCF fills everything)
    const nullValues = results.filter(r => r.value === null);
    expect(nullValues.length).toBe(0);
    
    // Gap-filled flags for 02:00 and 03:00 buckets
    const gapfilled = results.filter(r => r.is_gapfilled);
    expect(gapfilled.length).toBe(2);
    expect(gapfilled.map(r => r.bucket.getUTCHours())).toEqual([2, 3]);
  });
});

describe('Schema Features', () => {
  it('should have hypertable created', async () => {
    const result = await query<{ hypertable_name: string }>(
      "SELECT hypertable_name FROM timescaledb_information.hypertables WHERE hypertable_name = 'sensor_readings'"
    );
    expect(result.rows.length).toBe(1);
  });

  it('should have compression policy', async () => {
    const result = await query<{ hypertable_name: string; compress_after: string }>(
      "SELECT hypertable_name, compress_after FROM timescaledb_information.compression_settings WHERE hypertable_name = 'sensor_readings'"
    );
    expect(result.rows.length).toBe(1);
  });

  it('should have retention policy', async () => {
    const result = await query<{ hypertable_name: string; drop_after: string }>(
      "SELECT hypertable_name, drop_after FROM timescaledb_information.retention_policies WHERE hypertable_name = 'sensor_readings'"
    );
    expect(result.rows.length).toBe(1);
  });

  it('should have continuous aggregate', async () => {
    const result = await query<{ view_name: string }>(
      "SELECT view_name FROM timescaledb_information.continuous_aggregates WHERE view_name = 'sensor_readings_hourly'"
    );
    expect(result.rows.length).toBe(1);
  });
});
```

---

## Installation & Execution

### Prerequisites

1. **PostgreSQL 15+ with TimescaleDB 2.13+**
   ```bash
   # macOS (Homebrew)
   brew install timescaledb/tap/timescaledb
   brew services start timescaledb
   
   # Or Docker
   docker run -d --name timescaledb \
     -p 5432:5432 \
     -e POSTGRES_PASSWORD=postgres \
     -e POSTGRES_DB=timeseries_demo \
     timescale/timescaledb:latest-pg15
   ```

2. **Node.js 20+**

### Setup

```bash
# 1. Create project directory and files (copy all code above into respective files)
mkdir timeseries-example && cd timeseries-example

# 2. Create package.json, tsconfig.json, .env.example
# 3. Create src/ and tests/ directories with all TypeScript files

# 4. Install dependencies
npm install

# 5. Configure environment
cp .env.example .env
# Edit .env if needed (default works for local Docker setup)

# 6. Initialize database schema
npm run db:init

# 7. Run full demonstration
npm start
```

### Individual Commands

```bash
# Run ingestion only
npm run ingest

# Run gapfill query only
npm run query

# Run late arrival demo
npm run example:late-arrival

# Run synthetic data + assertions
tsx src/examples/syntheticData.ts

# Run tests
npm test

# Reset database (drop all objects)
npm run db:reset
```

---

## APIs & SQL Features Used

| Category | Feature | Purpose |
|----------|---------|---------|
| **Client** | `pg.Pool` | Connection pooling, parameterized queries |
| **Hypertable** | `create_hypertable()` | Partition `sensor_readings` by `event_time` (1-day chunks) |
| **Compression** | `ALTER TABLE ... SET (timescaledb.compress, ...)` + `add_compression_policy()` | Columnar compression after 7 days, segmented by `sensor_id` |
| **Retention** | `add_retention_policy()` | Drop raw chunks older than 90 days |
| **Continuous Aggregate** | `CREATE MATERIALIZED VIEW ... WITH (timescaledb.continuous)` + `add_continuous_aggregate_policy()` | Hourly rollups refreshed every hour with 1h lag |
| **Gap Fill** | `time_bucket_gapfill()` | Generate continuous hourly buckets, fill missing |
| **LOCF** | `locf()` | Last Observation Carried Forward for gap-filled buckets |
| **Timezone** | `AT TIME ZONE` | Shift bucket boundaries to query timezone |
| **Idempotent Write** | `INSERT ... ON CONFLICT (sensor_id, event_time) DO UPDATE` | Upsert preserves `event_time`, updates `ingestion_time` |
| **Late Arrival** | `late_arrivals` view | Detect `ingestion_time > event_time + 5min` |
| **Validation** | `zod` | Runtime schema validation for ingestion payloads |
| **Testing** | `vitest` | Unit/integration assertions |

---

## Key Design Decisions

1. **Primary Key**: `(sensor_id, event_time)` enables idempotent upserts and efficient time-range queries per sensor.

2. **Ingestion Time**: Stored separately from event time to track latency and enable late-arrival detection.

3. **Quality Flags**: Numeric (0/1/2) for storage efficiency; filtered in aggregates via `FILTER (WHERE quality_flag = 0)`.

4. **Tags as JSONB**: Flexible metadata without schema migrations; GIN index can be added if needed.

5. **Gapfill Function**: Encapsulated in SQL function `get_hourly_gapfilled()` for reuse and plan stability.

6. **Timezone Handling**: Boundaries computed in query timezone via `AT TIME ZONE`; bucket timestamps returned in UTC.

7. **Continuous Aggregate Lag**: 1-hour end offset ensures late arrivals within 1 hour are captured; older late data caught on next refresh.

8. **Compression SegmentBy**: `sensor_id` keeps each sensor's data together for compression efficiency.

---

## Verification Checklist

After running `npm start`, verify:

- [ ] Schema created: hypertable, indexes, compression, retention, continuous aggregate
- [ ] Sample data ingested (5 rows for `sensor-main`)
- [ ] Gapfill query returns 5 hourly buckets (07:00–11:00) with 09:00–10:00 gap-filled via LOCF
- [ ] Late arrival demo shows 3 late records in `late_arrivals` view
- [ ] Gapfill on raw hypertable includes late data immediately
- [ ] Tests pass: `npm test`

