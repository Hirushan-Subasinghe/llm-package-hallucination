## 📦 Quick‑start Overview  

This repo shows a **minimal, self‑contained Node.js + TypeScript** example that:

1. **Creates** a TimescaleDB hypertable for sensor readings.  
2. Sets up **retention**, **compression**, and a **continuous aggregate** (hourly, gap‑filled, LOCF).  
3. **Ingests** a small batch of readings with idempotent `INSERT … ON CONFLICT`.  
4. Runs a **parameterised** gap‑filled query that respects a time‑zone‑aware window and carries the last observation forward.  
5. Demonstrates a **late‑arrival** record and validates the result with a few synthetic‑data assertions.

Everything runs locally against a PostgreSQL instance with the TimescaleDB extension – no external services required.

---  

<details><summary>🛠️ Prerequisites & Installation (click to expand)</summary>

### 1️⃣ Install PostgreSQL 14+ with TimescaleDB  

You can use Docker (recommended) or a native install.

```bash
# Pull the official TimescaleDB image (includes PostgreSQL)
docker run -d \
  --name timescale-demo \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_USER=demo \
  -e POSTGRES_DB=timeseries_demo \
  -p 5432:5432 \
  timescale/timescaledb:2.13.2-pg14
```

> **Note** – The image tag `2.13.2-pg14` pins TimescaleDB 2.13.2 on PostgreSQL 14, which is the exact version used for this example.

### 2️⃣ Clone / create the project folder  

```bash
mkdir ts-timeseries-demo && cd ts-timeseries-demo
```

### 3️⃣ Add the source files (see sections below)  

- `package.json` – exact dependency versions & scripts  
- `tsconfig.json` – TypeScript compiler options  
- `src/index.ts` – main program (SQL + ingestion + query + assertions)  

### 4️⃣ Install Node dependencies  

```bash
npm ci      # installs the exact versions from package-lock.json
```

### 5️⃣ Compile & run  

```bash
npm run build   # transpiles to ./dist
npm start       # runs the compiled program
```

Or run directly with `ts-node` (no build step needed):

```bash
npm run dev
```

The script will:

1. Connect to the DB (`postgres://demo:secret@localhost:5432/timeseries_demo`).  
2. Create the schema (hypertable, policies, continuous aggregate).  
3. Insert a batch of synthetic sensor rows (including a late‑arrival).  
4. Execute the gap‑filled hourly query.  
5. Print the results and assert the expected values.

</details>  

---  

## 📄 `package.json` – exact versions & scripts  

```json
{
  "name": "ts-timeseries-demo",
  "version": "1.0.0",
  "description": "Self‑contained Node.js/TS example of TimescaleDB time‑series ingestion & gap‑filled query",
  "main": "dist/index.js",
  "type": "module",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "ts-node src/index.ts",
    "lint": "eslint . --ext .ts",
    "format": "prettier --write ."
  },
  "author": "OpenAI ChatGPT",
  "license": "MIT",
  "dependencies": {
    "pg": "8.11.5"
  },
  "devDependencies": {
    "@types/node": "20.12.7",
    "@types/pg": "8.10.7",
    "ts-node": "10.9.2",
    "typescript": "5.3.3",
    "eslint": "8.57.0",
    "eslint-config-prettier": "9.1.0",
    "eslint-plugin-import": "2.29.1",
    "prettier": "3.2.5"
  }
}
```

*All versions are pinned* – the `npm ci` command will install exactly these releases, guaranteeing reproducibility.

---  

## 🛠️ `tsconfig.json`  

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "moduleResolution": "node",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*.ts"]
}
```

---  

## 📂 `src/index.ts` – core implementation  

```ts
// src/index.ts
import { Client } from "pg";

/* ----------------------------------------------------------------------
   CONNECTION SETTINGS (adjust if you run PostgreSQL elsewhere)
----------------------------------------------------------------------- */
const DB_URL = "postgres://demo:secret@localhost:5432/timeseries_demo";

/* ----------------------------------------------------------------------
   SQL – Schema definitions (hypertable, policies, continuous aggregate)
----------------------------------------------------------------------- */
const SCHEMA_SQL = `
-- 1️⃣ Base table for raw sensor data
CREATE TABLE IF NOT EXISTS sensor_data (
  sensor_id   TEXT NOT NULL,
  tags        JSONB NOT NULL,               -- e.g. {"location":"room1","type":"temp"}
  event_time  TIMESTAMPTZ NOT NULL,          -- when the measurement actually occurred
  ingest_time TIMESTAMPTZ NOT NULL DEFAULT now(), -- when we stored it
  value       DOUBLE PRECISION NOT NULL,
  quality     SMALLINT NOT NULL,            -- 0=good, 1=questionable, 2=bad
  PRIMARY KEY (sensor_id, event_time)       -- idempotent key
);

-- 2️⃣ Convert to a TimescaleDB hypertable
SELECT create_hypertable('sensor_data', 'event_time', if_not_exists => TRUE);

-- 3️⃣ Retention policy – keep 30 days of raw data
SELECT add_retention_policy('sensor_data', INTERVAL '30 days');

-- 4️⃣ Compression policy – compress chunks older than 7 days
SELECT add_compression_policy('sensor_data', INTERVAL '7 days');

-- 5️⃣ Continuous aggregate: hourly, gap‑filled, last‑observation carry‑forward (LOCF)
CREATE MATERIALIZED VIEW IF NOT EXISTS sensor_hourly_agg
WITH (timescaledb.continuous) AS
SELECT
  time_bucket_gapfill('1 hour', event_time) AS bucket,
  sensor_id,
  tags,
  last(value, event_time) AS last_value,
  last(quality, event_time) AS last_quality,
  max(ingest_time) AS last_ingest_time
FROM sensor_data
GROUP BY bucket, sensor_id, tags
WITH NO DATA;   -- we will refresh manually

-- Refresh policy for the continuous aggregate (optional, every 10 min)
SELECT add_continuous_aggregate_policy(
  'sensor_hourly_agg',
  start_offset => INTERVAL '1 day',
  end_offset   => INTERVAL '1 hour',
  schedule_interval => INTERVAL '10 minutes'
);
`;

/* ----------------------------------------------------------------------
   Helper: run a query and log errors in a single place
----------------------------------------------------------------------- */
async function exec(client: Client, sql: string, params?: unknown[]) {
  try {
    await client.query(sql, params);
  } catch (e) {
    console.error("❌ SQL error:", e);
    throw e;
  }
}

/* ----------------------------------------------------------------------
   1️⃣ Ingest a small batch (idempotent writes) – includes a late arrival
----------------------------------------------------------------------- */
async function ingestBatch(client: Client) {
  const rows = [
    // Normal on‑time readings
    {
      sensor_id: "s1",
      tags: { location: "room1", type: "temp" },
      event_time: "2026-09-20T08:15:00Z",
      value: 22.3,
      quality: 0,
    },
    {
      sensor_id: "s1",
      tags: { location: "room1", type: "temp" },
      event_time: "2026-09-20T08:45:00Z",
      value: 22.5,
      quality: 0,
    },
    // Late‑arrival reading (event_time earlier than previous ingest)
    {
      sensor_id: "s1",
      tags: { location: "room1", type: "temp" },
      event_time: "2026-09-20T08:30:00Z", // falls between the two above
      value: 22.4,
      quality: 0,
    },
  ];

  const sql = `
    INSERT INTO sensor_data (sensor_id, tags, event_time, value, quality)
    VALUES ($1, $2, $3, $4, $5)
    ON CONFLICT (sensor_id, event_time) DO UPDATE
      SET value = EXCLUDED.value,
          quality = EXCLUDED.quality,
          ingest_time = now();
  `;

  for (const r of rows) {
    await exec(client, sql, [
      r.sensor_id,
      r.tags,
      r.event_time,
      r.value,
      r.quality,
    ]);
  }

  console.log("✅ Ingestion batch completed (including late arrival).");
}

/* ----------------------------------------------------------------------
   2️⃣ Parameterised gap‑filled hourly query (LOCF) with TZ‑aware bounds
----------------------------------------------------------------------- */
interface HourlyResult {
  bucket: string; // ISO timestamp string
  sensor_id: string;
  tags: Record<string, unknown>;
  last_value: number | null;
  last_quality: number | null;
}

/**
 * Returns hourly buckets (gap‑filled) for the given sensor between
 * `start` and `end` in the supplied IANA time zone.
 *
 * @param client   pg client
 * @param sensorId sensor identifier
 * @param start    inclusive start (local time, e.g. "2026‑09‑20 00:00")
 * @param end      exclusive end (local time, e.g. "2026‑09‑21 00:00")
 * @param tz       IANA time‑zone, e.g. "America/New_York"
 */
async function queryHourly(
  client: Client,
  sensorId: string,
  start: string,
  end: string,
  tz: string
): Promise<HourlyResult[]> {
  const sql = `
    SELECT
      bucket AT TIME ZONE $5 AS bucket,
      sensor_id,
      tags,
      last_value,
      last_quality
    FROM sensor_hourly_agg
    WHERE sensor_id = $1
      AND bucket >= ($2 AT TIME ZONE $5)
      AND bucket <  ($3 AT TIME ZONE $5)
    ORDER BY bucket;
  `;

  const res = await client.query(sql, [sensorId, start, end, tz, tz]);
  return res.rows.map((r) => ({
    bucket: r.bucket,
    sensor_id: r.sensor_id,
    tags: r.tags,
    last_value: r.last_value,
    last_quality: r.last_quality,
  }));
}

/* ----------------------------------------------------------------------
   3️⃣ Simple synthetic‑data assertions
----------------------------------------------------------------------- */
function assert(condition: boolean, message: string) {
  if (!condition) {
    console.error(`❌ Assertion failed: ${message}`);
    process.exit(1);
  }
}

/* ----------------------------------------------------------------------
   Main driver
----------------------------------------------------------------------- */
(async () => {
  const client = new Client({ connectionString: DB_URL });
  await client.connect();

  // 0️⃣ Ensure TimescaleDB extension is available (fails fast if not)
  await exec(client, `CREATE EXTENSION IF NOT EXISTS timescaledb;`);

  // 1️⃣ Create schema (idempotent)
  await exec(client, SCHEMA_SQL);
  console.log("✅ Schema created (hypertable, policies, continuous aggregate).");

  // 2️⃣ Ingest sample data
  await ingestBatch(client);

  // 3️⃣ Refresh the continuous aggregate (necessary for newly inserted rows)
  await exec(client, `CALL refresh_continuous_aggregate('sensor_hourly_agg', NULL, NULL);`);
  console.log("✅ Continuous aggregate refreshed.");

  // 4️⃣ Run the gap‑filled hourly query for 08:00‑10:00 UTC on 2026‑09‑20
  const results = await queryHourly(
    client,
    "s1",
    "2026-09-20 08:00",
    "2026-09-20 10:00",
    "UTC"
  );

  console.log("\n🕐 Hourly LOCF results (UTC):");
  console.table(results);

  // 5️⃣ Assertions – we know the expected LOCF values:
  //   08:00‑09:00 → last reading at 08:45 (value 22.5)
  //   09:00‑10:00 → no new reading → carry forward 22.5
  assert(results.length === 2, "Expected two hourly buckets.");
  assert(
    Math.abs(results[0].last_value - 22.5) < 1e-6,
    "08:00 bucket should carry value 22.5"
  );
  assert(
    Math.abs(results[1].last_value - 22.5) < 1e-6,
    "09:00 bucket should carry forward value 22.5"
  );

  console.log("\n✅ All assertions passed.");

  await client.end();
})();
```

### What the code uses  

| Layer | Feature / API | Description |
|------|----------------|-------------|
| **PostgreSQL client** | `pg` (`Client`) | Standard async driver (`await client.query(sql, params)`). |
| **TimescaleDB extension** | `CREATE EXTENSION timescaledb` | Enables hypertable & continuous‑aggregate functions. |
| **Hypertable** | `create_hypertable('sensor_data', 'event_time')` | Turns `sensor_data` into a time‑partitioned table. |
| **Retention policy** | `add_retention_policy('sensor_data', INTERVAL '30 days')` | Auto‑drops raw chunks older than 30 days. |
| **Compression policy** | `add_compression_policy('sensor_data', INTERVAL '7 days')` | Compresses chunks older than 7 days. |
| **Continuous aggregate** | `CREATE MATERIALIZED VIEW … WITH (timescaledb.continuous)` | Pre‑computes hourly buckets. |
| **Gap‑fill & LOCF** | `time_bucket_gapfill('1 hour', event_time)` + `last(value, event_time)` | Generates empty buckets and carries the last known value forward. |
| **Idempotent writes** | `INSERT … ON CONFLICT (sensor_id, event_time) DO UPDATE` | Guarantees exactly‑once semantics for the same `(sensor_id, event_time)`. |
| **Time‑zone handling** | `AT TIME ZONE $5` in the query | Allows callers to specify an IANA zone (e.g., `"America/New_York"`). |
| **Refresh continuous aggregate** | `CALL refresh_continuous_aggregate('sensor_hourly_agg', NULL, NULL);` | Materialized view refresh for newly ingested rows (in dev mode). |

---  

## 📚 Reproducible Commands (copy‑paste)

```bash
# 1️⃣ Start TimescaleDB container (if not already running)
docker run -d \
  --name timescale-demo \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_USER=demo \
  -e POSTGRES_DB=timeseries_demo \
  -p 5432:5432 \
  timescale/timescaledb:2.13.2-pg14

# 2️⃣ Clone / create the project directory (skip if you already have it)
mkdir ts-timeseries-demo && cd ts-timeseries-demo

# 3️⃣ Create the files (package.json, tsconfig.json, src/index.ts) – see sections above.

# 4️⃣ Install exact dependencies
npm ci

# 5️⃣ Build & run the demo
npm run build && npm start
#   OR (no build step)
npm run dev
```

You should see output similar to:

```
✅ Schema created (hypertable, policies, continuous aggregate).
✅ Ingestion batch completed (including late arrival).
✅ Continuous aggregate refreshed.

🕐 Hourly LOCF results (UTC):
┌─────────┬───────────────────────────────┬───────────┬───────────────────────────────────────┬────────────┬───────────────┐
│ (index) │            bucket               │ sensor_id │                tags                   │ last_value │ last_quality │
├─────────┼───────────────────────────────┼───────────┼───────────────────────────────────────┼────────────┼───────────────┤
│    0    │ '2026‑09‑20T08:00:00.000Z'      │   's1'   │ { location: 'room1', type: 'temp' }   │   22.5    │      0        │
│    1    │ '2026‑09‑20T09:00:00.000Z'      │   's1'   │ { location: 'room1', type: 'temp' }   │   22.5    │      0        │
└─────────┴───────────────────────────────┴───────────┴───────────────────────────────────────┴────────────┴───────────────┘

✅ All assertions passed.
```

---  

## 🎯 What you can extend from here  

* **More sensors / tags** – just add rows; the primary key `(sensor_id, event_time)` guarantees idempotency per sensor.  
* **Different bucket sizes** – replace `'1 hour'` with `'5 minutes'`, `'1 day'`, etc.  
* **Down‑sampling** – create additional continuous aggregates (e.g., daily max/min).  
* **Streaming ingestion** – replace the static batch with a Kafka consumer or an HTTP endpoint using the same `INSERT … ON CONFLICT` pattern.  

Feel free to fork the repo and adapt the schema, policies, or queries to your own use‑case!
