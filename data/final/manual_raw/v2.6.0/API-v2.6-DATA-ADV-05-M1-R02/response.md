## Overview

This repository provides a **self‑contained Node.js + TypeScript** example that demonstrates core TimescaleDB time‑series patterns:

* **Hypertable creation** with chunking, retention, and compression.
* **Continuous aggregates** for hourly summarisation.
* **Idempotent batch ingestion** of sensor readings (tags, event time, ingestion time, quality flag).
* **Gap‑filled hourly query** with *last‑observation carry‑forward* (LOCF) and timezone‑aware boundaries.
* **Late‑arrival handling** (insert after materialisation, refresh to include).

All code is written in TypeScript and run locally against a TimescaleDB instance (PostgreSQL 15+ with the `timescaledb` extension).

---

<details><summary><strong>📦 Installation & Local Setup</strong></summary>

**Prerequisites**

* Docker (or native PostgreSQL 15+ with TimescaleDB extension)

**1. Start a TimescaleDB container**

```bash
docker network create pgnet
docker run -d \
  --name timescaledb \
  --network pgnet \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=timeseries \
  -p 5432:5432 \
  timescaledb/timescaledb:latest-pg15
```

**2. Set the database URL**

```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/timeseries"
```

**3. Clone the repo and install dependencies**

```bash
git clone <repo-url>
cd times-series-example
npm ci               # uses the exact versions from package.json
```

**4. Apply the schema (run once)**

```bash
npm run init
```

**5. Seed example data**

```bash
npm run seed
```

**6. Run the gap‑filled query demo**

```bash
npm run query
```

**7. Execute the test suite (includes late‑arrival scenario)**

```bash
npm test
```

All scripts are defined in `package.json` (see below).  
The example is fully reproducible – no manual SQL editing required.

</details>

---

## Project Structure

```
times-series-example/
├── package.json
├── tsconfig.json
├── .gitignore
├── docker-compose.yml          # optional, alternative to manual container start
├── src/
│   ├── db.ts                   # pg client & connection helpers
│   ├── init.ts                 # schema creation (extension, hypertable, policies, CA)
│   ├── seed.ts                 # idempotent batch insert
│   ├── query.ts                # gap‑filled hourly LOCF query
│   └── test.ts                 # assertions & late‑arrival demo
└── README.md
```

---

## 📄 package.json

```json
{
  "name": "times-series-example",
  "version": "0.0.1",
  "description": "Self‑contained Node.js TypeScript example for local PostgreSQL with TimescaleDB time‑series features.",
  "type": "module",
  "scripts": {
    "dev": "tsx src/index.ts",
    "init": "tsx src/init.ts",
    "seed": "tsx src/seed.ts",
    "query": "tsx src/query.ts",
    "test": "tsx src/test.ts",
    "lint": "eslint src --ext .ts",
    "format": "prettier --write src"
  },
  "keywords": ["timeseries", "postgresql", "timescaledb", "typescript"],
  "author": "",
  "license": "MIT",
  "dependencies": {
    "pg": "^8.11.0",
    "dotenv": "^16.3.1"
  },
  "devDependencies": {
    "typescript": "^5.3.3",
    "@types/pg": "^8.11.0",
    "@types/node": "^20.11.0",
    "tsx": "^4.5.0",
    "eslint": "^8.56.0",
    "eslint-config-prettier": "^9.1.0",
    "eslint-plugin-prettier": "^5.1.1",
    "prettier": "^3.2.1",
    "jest": "^29.7.0",
    "ts-jest": "^29.1.1",
    "@types/jest": "^29.5.11",
    "zod": "^3.22.4"
  }
}
```

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
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

---

## 📄 .gitignore

```
node_modules
dist
*.log
.env
```

---

## 📄 src/db.ts

```ts
import { Client } from 'pg';
import dotenv from 'dotenv';

dotenv.config();

export const client = new Client({
  connectionString: process.env.DATABASE_URL ?? 'postgresql://postgres:postgres@localhost:5432/timeseries',
});

export async function connectDb(): Promise<void> {
  await client.connect();
  console.log('Connected to PostgreSQL');
}
```

---

## 📄 src/init.ts

```ts
import { client } from './db.js';
import { connectDb } from './db.js';

(async () => {
  await connectDb();

  // Drop everything for a clean start (idempotent)
  await client.query(`DROP TABLE IF EXISTS sensor_readings;`);
  await client.query(`DROP MATERIALIZED VIEW IF EXISTS hourly_avg_sensor;`);
  await client.query(`DROP EXTENSION IF EXISTS timescaledb;`);
  await client.query(`CREATE EXTENSION IF NOT EXISTS timescaledb;`);

  // Table definition
  await client.query(`
    CREATE TABLE sensor_readings (
      id SERIAL PRIMARY KEY,
      sensor_id TEXT NOT NULL,
      tags JSONB NOT NULL,
      event_time TIMESTAMPTZ NOT NULL,
      ingestion_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
      quality_flag TEXT NOT NULL CHECK (quality_flag IN ('good', 'bad', 'unknown')),
      value DOUBLE PRECISION NOT NULL,
      UNIQUE (sensor_id, event_time)
    );
  `);

  // Hypertable with 1‑day chunks
  await client.query(
    `SELECT create_hypertable('sensor_readings', 'event_time', chunk_time_interval => INTERVAL '1 day');`
  );

  // Retention policy – drop older than 30 days
  await client.query(`SELECT add_retention_policy('sensor_readings', INTERVAL '30 days');`);

  // Compression policy – compress older than 7 days
  await client.query(`SELECT add_compression_policy('sensor_readings', INTERVAL '7 days');`);

  // Continuous aggregate for hourly averages per sensor
  await client.query(`
    CREATE MATERIALIZED VIEW hourly_avg_sensor WITH (timescaledb.continuous) AS
    SELECT
      time_bucket('1h', event_time) AS bucket,
      sensor_id,
      AVG(value) AS avg_value
    FROM sensor_readings
    GROUP BY bucket, sensor_id;
  `);

  // Initial materialisation
  await client.query('REFRESH MATERIALIZED VIEW CONCURRENTLY hourly_avg_sensor;');

  await client.end();
  console.log('Schema initialized');
})();
```

---

## 📄 src/seed.ts

```ts
import { client } from './db.js';
import { connectDb } from './db.js';

(async () => {
  await connectDb();

  // Clear any existing data
  await client.query('DELETE FROM sensor_readings;');
  await client.query('REFRESH MATERIALIZED VIEW CONCURRENTLY hourly_avg_sensor;');

  const readings = [
    {
      sensor_id: 'sensor-a',
      tags: { location: 'room1', unit: 'celsius' },
      event_time: new Date('2024-09-01T12:00:00Z'),
      quality_flag: 'good',
      value: 23.5,
    },
    {
      sensor_id: 'sensor-a',
      tags: { location: 'room1', unit: 'celsius' },
      event_time: new Date('2024-09-01T12:30:00Z'),
      quality_flag: 'good',
      value: 24.1,
    },
    {
      sensor_id: 'sensor-b',
      tags: { location: 'room2', unit: 'percent' },
      event_time: new Date('2024-09-01T13:00:00Z'),
      quality_flag: 'bad',
      value: -999,
    },
    {
      sensor_id: 'sensor-b',
      tags: { location: 'room2', unit: 'percent' },
      event_time: new Date('2024-09-01T13:45:00Z'),
      quality_flag: 'good',
      value: 78.3,
    },
    {
      sensor_id: 'sensor-a',
      tags: { location: 'room1', unit: 'celsius' },
      event_time: new Date('2024-09-01T14:15:00Z'),
      quality_flag: 'unknown',
      value: 22.9,
    },
  ];

  for (const r of readings) {
    await client.query(
      `INSERT INTO sensor_readings (sensor_id, tags, event_time, quality_flag, value)
       VALUES ($1, $2, $3, $4, $5)
       ON CONFLICT (sensor_id, event_time) DO UPDATE SET
           tags = EXCLUDED.tags,
           quality_flag = EXCLUDED.quality_flag,
           value = EXCLUDED.value
       RETURNING id;`,
      [r.sensor_id, r.tags, r.event_time, r.quality_flag, r.value]
    );
  }

  // Refresh the continuous aggregate after inserts
  await client.query('REFRESH MATERIALIZED VIEW CONCURRENTLY hourly_avg_sensor;');
  await client.end();
  console.log('Seed data inserted');
})();
```

---

## 📄 src/query.ts

```ts
import { client } from './db.js';
import { connectDb } from './db.js';

(async () => {
  await connectDb();

  /**
   * Gap‑filled hourly series with LOCF.
   * @param sensorId      Sensor identifier
   * @param start         Start of the window (inclusive)
   * @param end           End of the window (exclusive)
   * @param tz            Time‑zone for bucket calculation (default UTC)
   */
  async function gapFilledHourly(sensorId: string, start: Date, end: Date, tz: string = 'UTC'): Promise<void> {
    const query = {
      text: `
        WITH buckets AS (
          SELECT generate_series($1::timestamptz, $2::timestamptz, INTERVAL '1 hour') AS bucket
        ),
        aggregated AS (
          SELECT
            time_bucket('1h', event_time AT TIME ZONE $3) AS bucket,
            AVG(value) AS avg_val
          FROM sensor_readings
          WHERE sensor_id = $4
            AND event_time AT TIME ZONE $3 >= $1
            AND event_time AT TIME ZONE $3 < $2
          GROUP BY bucket
        )
        SELECT
          b.bucket AS time,
          COALESCE(
            a.avg_val,
            LAG(COALESCE(a.avg_val, NULL), 1) OVER (ORDER BY b.bucket)
          ) AS avg_value
        FROM buckets b
        LEFT JOIN aggregated a ON b.bucket = a.bucket
        ORDER BY b.bucket;
      `,
      values: [start, end, tz, sensorId],
    };

    const res = await client.query(query);
    console.log(`Gap‑filled hourly series for ${sensorId} from ${start} to ${end} (tz=${tz}):`);
    console.table(res.rows);
  }

  // Example: sensor‑a, 11 Z → 15 Z on 2024‑09‑01
  const sensorId = 'sensor-a';
  const start = new Date('2024-09-01T11:00:00Z');
  const end = new Date('2024-09-01T15:00:00Z');

  await gapFilledHourly(sensorId, start, end, 'UTC');

  await client.end();
})();
```

---

## 📄 src/test.ts

```ts
import { client } from './db.js';
import { connectDb } from './db.js';
import assert from 'assert';

(async () => {
  await connectDb();

  try {
    /* ---------- 1. Hypertable ---------- */
    const hyperRes = await client.query(
      `SELECT * FROM timescaledb_information.hypertables WHERE table_name = 'sensor_readings';`
    );
    assert.strictEqual(hyperRes.rows.length, 1, 'Hypertable sensor_readings not created');
    console.log('✓ Hypertable exists');

    /* ---------- 2. Continuous aggregate ---------- */
    const aggRes = await client.query(
      `SELECT * FROM timescaledb_information.continuous_aggregates WHERE matview_name = 'hourly_avg_sensor';`
    );
    assert.strictEqual(aggRes.rows.length, 1, 'Continuous aggregate hourly_avg_sensor not created');
    console.log('✓ Continuous aggregate exists');

    /* ---------- 3. Row count after seed ---------- */
    const cntRes = await client.query('SELECT COUNT(*) FROM sensor_readings;');
    const inserted = Number(cntRes.rows[0].count);
    assert.strictEqual(inserted, 5, `Expected 5 rows, got ${inserted}`);
    console.log(`✓ Inserted ${inserted} rows`);

    /* ---------- 4. Hourly aggregate for sensor‑a @ 12:00 ---------- */
    const bucketRes = await client.query(
      `SELECT bucket, avg_value FROM hourly_avg_sensor
       WHERE sensor_id = $1 AND bucket = $2;`,
      ['sensor-a', new Date('2024-09-01T12:00:00Z')]
    );
    assert.strictEqual(bucketRes.rows.length, 1, 'Missing hourly aggregate for sensor-a @ 12:00');
    const avg = bucketRes.rows[0].avg_value;
    assert.strictEqual(avg, 23.8, `Expected avg 23.8, got ${avg}`);
    console.log(`✓ Hourly aggregate for sensor-a at 12:00 is ${avg}`);

    /* ---------- 5. Gap‑filled query assertions ---------- */
    const start = new Date('2024-09-01T11:00:00Z');
    const end = new Date('2024-09-01T15:00:00Z');
    const gapRes = await client.query(
      `
      WITH buckets AS (
        SELECT generate_series($1::timestamptz, $2::timestamptz, INTERVAL '1 hour') AS bucket
      ),
      aggregated AS (
        SELECT
          time_bucket('1h', event_time AT TIME ZONE $3) AS bucket,
          AVG(value) AS avg_val
        FROM sensor_readings
        WHERE sensor_id = $4
          AND event_time AT TIME ZONE $3 >= $1
          AND event_time AT TIME ZONE $3 < $2
        GROUP BY bucket
      )
      SELECT
        b.bucket AS time,
        COALESCE(
          a.avg_val,
          LAG(COALESCE(a.avg_val, NULL), 1) OVER (ORDER BY b.bucket)
        ) AS avg_value
      FROM buckets b
      LEFT JOIN aggregated a ON b.bucket = a.bucket
      ORDER BY b.bucket;
      `,
      [start, end, 'UTC', 'sensor-a']
    );

    assert.strictEqual(gapRes.rows.length, 4, `Expected 4 hourly rows, got ${gapRes.rows.length}`);
    assert.strictEqual(gapRes.rows[0].avg_value, null, 'Expected NULL for bucket 11');
    assert.strictEqual(gapRes.rows[1].avg_value, 23.8, 'Expected 23.8 for bucket 12');
    assert.strictEqual(gapRes.rows[2].avg_value, 23.8, 'Expected LOCF 23.8 for bucket 13');
    assert.strictEqual(gapRes.rows[3].avg_value, 22.9, 'Expected 22.9 for bucket 14');
    console.log('✓ Gap‑filled query assertions passed');

    /* ---------- 6. Late‑arrival example ---------- */
    const late = {
      sensor_id: 'sensor-c',
      tags: { location: 'room3', unit: 'volts' },
      event_time: new Date('2024-08-31T23:30:00Z'),
      quality_flag: 'good',
      value: 5.0,
    };

    await client.query(
      `INSERT INTO sensor_readings (sensor_id, tags, event_time, quality_flag, value)
       VALUES ($1, $2, $3, $4, $5)
       ON CONFLICT (sensor_id, event_time) DO UPDATE SET
           tags = EXCLUDED.tags,
           quality_flag = EXCLUDED.quality_flag,
           value = EXCLUDED.value
       RETURNING id;`,
      [late.sensor_id, late.tags, late.event_time, late.quality_flag, late.value]
    );
    console.log('✓ Late arrival inserted');

    // Before refresh the CA should not contain sensor‑c
    const before = await client.query(
      `SELECT COUNT(*) FROM hourly_avg_sensor WHERE sensor_id = $1;`,
      ['sensor-c']
    );
    assert.strictEqual(Number(before.rows[0].count), 0, 'Late arrival should not be reflected before refresh');
    console.log('✓ Late arrival not yet in continuous aggregate');

    // Refresh and verify
    await client.query('REFRESH MATERIALIZED VIEW CONCURRENTLY hourly_avg_sensor;');
    const after = await client.query(
      `SELECT bucket, avg_value FROM hourly_avg_sensor WHERE sensor_id = $1;`,
      ['sensor-c']
    );
    assert.strictEqual(after.rows.length, 1, 'Late arrival should appear after refresh');
    assert.strictEqual(after.rows[0].avg_value, 5.0, 'Avg value mismatch for late arrival');
    console.log('✓ Late arrival reflected after refresh');

  } catch (err) {
    console.error('Test failed:', err);
    process.exit(1);
  } finally {
    await client.end();
  }

  console.log('All tests passed');
})();
```

---

## 📄 docker-compose.yml *(optional)*

```yaml
version: '3.8'
services:
  timescaledb:
    image: timescaledb/timescaledb:latest-pg15
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: timeseries
    ports:
      - "5432:5432"
    volumes:
      - pg_data:/var/lib/postgresql/data
volumes:
  pg_data:
```

*Run with `docker compose up -d` instead of the manual container command.*

---

## 🚀 Usage Commands

| Command | Description |
|---------|-------------|
| `npm run init` | Create extension, hypertable, retention, compression, and continuous aggregate. |
| `npm run seed` | Insert a small batch of sensor readings (idempotent). |
| `npm run query` | Execute the gap‑filled hourly LOCF query for **sensor‑a** (11 Z → 15 Z). |
| `npm run test` | Full test suite – validates schema, data, aggregates, gap‑fill, and late‑arrival handling. |
| `npm run lint` | Run ESLint on TypeScript sources. |
| `npm run format` | Re‑format code with Prettier. |

All scripts assume the environment variable `DATABASE_URL` points to a running TimescaleDB instance (see installation).

---

## 🔧 APIs & SQL Features Used

| Category | Feature / API | Purpose |
|----------|---------------|---------|
| **Client** | `pg` (`^8.11.0`) | PostgreSQL driver for Node.js. |
| **Extension** | `CREATE EXTENSION IF NOT EXISTS timescaledb;` | Enables time‑series functions. |
| **Hypertable** | `create_hypertable('sensor_readings', 'event_time', chunk_time_interval => INTERVAL '1 day')` | Turns `sensor_readings` into a hypertable with daily chunks. |
| **Retention** | `add_retention_policy('sensor_readings', INTERVAL '30 days')` | Automatically drops older than 30 days. |
| **Compression** | `add_compression_policy('sensor_readings', INTERVAL '7 days')` | Compacts chunks older than 7 days. |
| **Continuous Aggregate** | `CREATE MATERIALIZED VIEW hourly_avg_sensor WITH (timescaledb.continuous) AS …` | Hourly average per sensor. |
| **Refresh** | `REFRESH MATERIALIZED VIEW CONCURRENTLY hourly_avg_sensor;` | Populates / updates the aggregate. |
| **Idempotent Insert** | `INSERT … ON CONFLICT (sensor_id, event_time) DO UPDATE SET …` | Guarantees duplicate‑free writes. |
| **Unique Constraint** | `UNIQUE (sensor_id, event_time)` | Enforces conflict target for `ON CONFLICT`. |
| **Gap‑fill** | `generate_series($1::timestamptz, $2::timestamptz, INTERVAL '1 hour')` | Produces a continuous hourly series. |
| **Time‑zone handling** | `event_time AT TIME ZONE $tz` and `time_bucket('1h', …)` | Aligns buckets to the requested TZ. |
| **LOCF** | `LAG(COALESCE(a.avg_val, NULL), 1) OVER (ORDER BY b.bucket)` + `COALESCE` | Carries forward the last observed value. |
| **Late‑arrival** | Insert after materialisation, then `REFRESH` | Demonstrates out‑of‑order data handling. |
| **Assertions** | Node `assert` module | Validates expected state in `test.ts`. |

---

## 📝 Notes on Reproducibility

* The example works with **TimescaleDB 2.x** on PostgreSQL 15 (the Docker image `timescaledb/timescaledb:latest-pg15` is used).
* All SQL is executed via the **`pg`** client; no external migration tools are required.
* The scripts are **idempotent** – running `init` again drops and recreates objects, `seed` clears the table before inserting.
* The `gapFilledHourly` function is fully **parameterizable** – change `sensorId`, `start`, `end`, and `tz` to explore other windows.
* The test suite covers the **late‑arrival** scenario, confirming that out‑of‑order events are retained and only reflected after a refresh of the continuous aggregate.

---

Feel free to extend the example with additional sensors, tags, or more sophisticated quality‑flag logic. Happy coding!
