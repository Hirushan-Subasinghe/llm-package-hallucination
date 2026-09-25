<details>
<summary>📋 Overview & Key Components</summary>

This repository provides a **self‑contained Node.js + TypeScript** example that demonstrates a hybrid search powered by a local **PostgreSQL** instance with **PostGIS** and the **vector** extension.

**Core features**

- **Schema** – `documents` table storing:
  - `id` (UUID)
  - `content` (text) with generated `tsvector` for full‑text search
  - `embedding` (vector, deterministic stub)
  - `location` (geography point, 4326)
  - `metadata` (JSONB)
  - `valid_from` / `valid_to` (timestamptz) – time‑window validity
- **Indexes** – GiST (`location`), GIN (`metadata`), IVFFlat (`embedding`), and time‑based partial indexes.
- **Ingestion** – a single transaction‑safe `ingestDocument()` that inserts a row.
- **Search** – a parameterized hybrid query that combines:
  - Vector similarity (`<->` L2 distance)
  - Full‑text rank (`ts_rank`)
  - Geographic radius (`ST_DWithin`)
  - JSONB metadata filter
  - Temporal validity (`valid_from`/`valid_to`)
  - Stable pagination (`LIMIT`/`OFFSET` with deterministic ordering)
- **Deterministic embedding stub** – a pure‑TS function that maps any text to a fixed‑size vector (no external ML model required).
- **Integration assertions** – Jest tests that verify ingestion and hybrid search.
- **Reproducible setup** – SQL to create extensions, migrations, and seed data; `package.json` with exact dependency versions; one‑liner install & run commands.

All code is **TypeScript**, uses the official `pg` client, and follows a minimal, focused structure suitable for learning or prototyping.
</details>

---

## 📁 Project Structure

```
my-search-example/
├── package.json
├── tsconfig.json
├── .env                # (optional) DB connection string
├── src/
│   ├── db.ts           # PostgreSQL client & helpers
│   ├── embedding.ts    # deterministic embedding stub
│   ├── ingest.ts       # transaction‑safe ingestion
│   ├── search.ts       # hybrid search implementation
│   ├── migrations/
│   │   ├── 001_create_documents.sql
│   │   └── 002_create_indexes.sql
│   └── seed.ts         # insert sample documents
├── tests/
│   └── search.test.ts  # integration assertions
└── README.md
```

---

## 📦 package.json

```json
{
  "name": "node-ts-postgres-postgis-vector-search",
  "version": "1.0.0",
  "description": "Hybrid search example using PostgreSQL + PostGIS + vector extension",
  "main": "dist/src/db.js",
  "scripts": {
    "build": "tsc",
    "dev": "tsx src/db.ts",                     // example: start REPL / ad‑hoc scripts
    "migrate": "tsx src/migrate.ts",           // run migration SQL files
    "seed": "tsx src/seed.ts",                 // seed sample data
    "test": "jest",
    "test:watch": "jest --watch",
    "clean": "rimraf dist"
  },
  "keywords": [
    "postgresql",
    "postgis",
    "vector",
    "search",
    "hybrid",
    "typescript"
  ],
  "author": "",
  "license": "MIT",
  "dependencies": {
    "pg": "^8.11.0",
    "uuid": "^9.0.1",
    "dotenv": "^16.1.4"
  },
  "devDependencies": {
    "@types/pg": "^8.11.0",
    "typescript": "^5.0.0",
    "ts-node": "^10.9.0",
    "tsx": "^4.0.0",
    "jest": "^29.5.0",
    "@types/jest": "^29.5.0",
    "rimraf": "^5.0.1"
  },
  "engines": {
    "node": ">=20.0.0"
  }
}
```

**Key APIs used**

- **PostgreSQL client** – `pg` (v8.11) for connection pooling and query execution.
- **PostGIS** – functions like `ST_MakePoint`, `ST_SetSRID`, `ST_DWithin`, `geography`.
- **vector extension** – `vector_l2_ops` for distance (`<->`) and IVFFlat indexing.
- **Full‑text search** – `to_tsvector`, `to_tsquery`, `ts_rank`.
- **JSONB** – `metadata->>'category'` path syntax.

---

## ⚙️ Setup SQL (extensions & DB)

Save the following as `setup.sql` (run with `psql` after starting PostgreSQL):

```sql
-- Enable required extensions (run as superuser or with appropriate privileges)
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS vector;

-- Create a dedicated database (optional – can be done with createdb)
-- SELECT 'DROP DATABASE IF EXISTS searchdb;';
-- SELECT 'CREATE DATABASE searchdb OWNER postgres;';
```

**Example commands (Linux/macOS)**

```bash
# 1️⃣ Start a local PostgreSQL (Docker)
docker run --name pgsearch \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=searchdb \
  -p 5432:5432 \
  -d postgres:15

# 2️⃣ Wait for it to be ready
sleep 3

# 3️⃣ Enable extensions (run inside psql)
psql -U postgres -d searchdb <<'EOSQL'
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS vector;
EOSQL

# 4️⃣ Run this repo's migrations & seed
npm install
npm run migrate
npm run seed
```

---

## 📄 Migrations

### 001_create_documents.sql

```sql
CREATE TABLE documents (
  id UUID PRIMARY KEY,
  content TEXT NOT NULL,
  embedding vector(384),                     -- 384‑dim example (e.g., OpenAI Ada)
  location geography('POINT', 4326),         -- WGS84 geography
  metadata JSONB,
  valid_from timestamptz NOT NULL,
  valid_to timestamptz NOT NULL,
  -- generated tsvector for full‑text search
  content_tsvector tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
);
```

### 002_create_indexes.sql

```sql
-- Partial index for currently valid documents (optimises time predicates)
CREATE INDEX idx_documents_valid
  ON documents
  WHERE valid_from <= now() AND valid_to >= now();

-- GiST index for geographic radius queries
CREATE INDEX idx_documents_location
  ON documents USING gist (location);

-- GIN index for JSONB metadata filtering
CREATE INDEX idx_documents_metadata
  ON documents USING gin (metadata);

-- Vector IVFFlat index for approximate nearest‑neighbour search
-- Adjust `lists` based on dataset size (100 is a good start)
CREATE INDEX idx_documents_embedding
  ON documents USING ivfflat (embedding vector_l2_ops)
  WITH (lists = 100);
```

*Both migration files are executed in order by the `migrate.ts` script (see below).*

---

## 🛠️ TypeScript Core

### src/db.ts – Connection pool & query helpers

```ts
// src/db.ts
import { Pool } from 'pg';
import dotenv from 'dotenv';

dotenv.config();

export const pool = new Pool({
  connectionString: process.env.DATABASE_URL ?? 'postgresql://postgres:postgres@localhost:5432/searchdb',
  // Optional: allow non‑SSL connections for local dev
  ssl: false,
});

// Simple helper to run a SQL file
export async function runSqlFile(path: string): Promise<void> {
  const { readFile }s = require('fs').promises;
  const sql = await readFileSync(path, 'utf8');
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    await client.query(sql);
    await client.query('COMMIT');
  } catch (err) {
    await client.query('ROLLBACK');
    throw err;
  } finally {
    client.release();
  }
}
```

### src/embedding.ts – Deterministic stub

```ts
// src/embedding.ts
import { createHash } from 'crypto';

/**
 * Generate a deterministic embedding vector from arbitrary text.
 * @param text - Input text to embed.
 * @param dimension - Desired vector length (e.g., 384).
 * @returns A number[] of length `dimension`.
 */
export function generateEmbedding(text: string, dimension: number = 384): number[] {
  // Simple deterministic seed: SHA‑256 hash of the text
  const hash = createHash('sha256').update(text).digest();
  const vec: number[] = [];

  // Map each byte to a float in [-1, 1] using a simple linear mapping.
  // This ensures the same text always yields the same vector.
  for (let i = 0; i < dimension; i++) {
    // Use two bytes per dimension for a bit more variance
    const byte1 = hash[i % hash.length];
    const byte2 = hash[(i + 1) % hash.length];
    // Combine bytes into a 16‑bit integer, then normalize
    const combined = (byte2 << 8) | byte1;
    // Map 0‑65535 to -1 … 1
    const normalized = (combined / 0xffff) * 2 - 1;
    vec.push(parseFloat(normalized.toFixed(6)));
  }

  return vec;
}
```

### src/ingest.ts – Transaction‑safe ingestion

```ts
// src/ingest.ts
import { PoolClient } from 'pg';
import { v4 as uuidv4 } from 'uuid';
import { generateEmbedding } from './embedding';

export interface IngestDocumentParams {
  content: string;
  location: { lat: number; lng: number };
  metadata?: Record<string, any>;
  validFrom?: Date;
  validTo?: Date;
}

/**
 * Insert a document into PostgreSQL inside a single transaction.
 * The embedding is generated deterministically from the content.
 */
export async function ingestDocument(pool: Pool, params: IngestDocumentParams): Promise<void> {
  const client: PoolClient = await pool.connect();

  try {
    await client.query('BEGIN');

    const id = uuidv4();
    const embedding = generateEmbedding(params.content, 384);

    // Build PostGIS geography point (WGS84, 4326)
    const locationSql = `ST_SetSRID(ST_MakePoint(${params.location.lng}, ${params.location.lat}), 4326)`;

    const validFrom = params.validFrom ?? new Date();
    const validTo = params.validTo ?? new Date(Date.now() + 365 * 24 * 60 * 60 * 1000); // +1 year

    await client.query(
      `
      INSERT INTO documents (id, content, embedding, location, metadata, valid_from, valid_to)
      VALUES ($1, $2, $3::vector, $4::geography, $5, $6, $7)
      `,
      [
        id,
        params.content,
        embedding,               // pg‑vector expects a string like '{0.1,0.2,...}'
        locationSql,
        params.metadata ?? {},
        validFrom,
        validTo,
      ]
    );

    await client.query('COMMIT');
  } catch (err) {
    await client.query('ROLLBACK');
    throw err;
  } finally {
    client.release();
  }
}
```

> **Note** – `pg` serialises an array as a PostgreSQL vector literal automatically (`{0.123,0.456,...}`). If you prefer explicit casting, you can join the array into a string.

### src/search.ts – Hybrid query with pagination

```ts
// src/search.ts
import { PoolClient } from 'pg';

export interface SearchResult {
  id: string;
  content: string;
  embedding: number[];
  location: string; // WKT representation
  metadata: Record<string, any>;
  validFrom: Date;
  validTo: Date;
  rank: number;      // ts_rank
  distance: number;  // vector L2 distance
}

/**
 * Hybrid search combining vector similarity, full‑text rank,
 * geographic radius, JSONB metadata, and temporal validity.
 */
export async function hybridSearch(
  client: PoolClient,
  {
    embedding,           // number[] – query embedding
    radius = 50,         // kilometers for geographic radius
    metadata = {},       // JSONB filter object
    validAt = new Date(), // point in time to check validity
    queryText = '',      // plain‑text full‑text query
    limit = 20,
    offset = 0,
  }: {
    embedding: number[];
    radius?: number;
    metadata?: Record<string, any>;
    validAt?: Date;
    queryText?: string;
    limit?: number;
    offset?: number;
  }
): Promise<SearchResult[]> {
  // Build metadata filter clause (safe for simple equality)
  const metaEntries = Object.entries(metadata).map(([k, v]) => `metadata->>'${k}' = $${metaEntries.length + 8}`);
  const metaClause = metaEntries.length ? `AND ${metaEntries.join(' AND ')}` : '';

  // Prepare queryText tsquery if provided
  const tsQueryClause = queryText
    ? `AND to_tsquery('english', $7) @@ content_tsvector`
    : '';

  // Vector distance uses the pg‑vector `<->` operator (L2)
  // The embedding param is passed as a vector literal string.
  const vectorLiteral = `{${embedding.join(',')}}`;

  const sql = `
    SELECT
      id,
      content,
      embedding::float[],
      ST_AsText(location) AS location,
      metadata,
      valid_from,
      valid_to,
      ts_rank(content_tsvector, to_tsquery('english', $8)) AS rank,
      embedding <-> $1::vector AS distance
    FROM documents
    WHERE
      /* Vector similarity */
      embedding <-> $1::vector <= $2   -- $2 = maxDistance (optional)
      AND
      /* Geographic radius */
      ST_DWithin(location, ST_MakePoint($3, $4)::geography, $5)   -- $3 lng, $4 lat, $5 meters
      AND
      /* Temporal validity */
      valid_from <= $6 AND valid_to >= $6                         -- $6 = validAt
      ${metaClause}
      ${tsQueryClause}
    ORDER BY
      distance ASC,               -- vector closeness first
      rank DESC,                  -- then full‑text relevance
      ST_Distance(location, ST_MakePoint($3, $4)::geography) ASC, -- then geography
      id ASC                       -- deterministic pagination
    LIMIT $9
    OFFSET $10
  `;

  // Build parameter array
  const params: any[] = [
    vectorLiteral,               // $1 – query embedding
    1000,                        // $2 – max vector distance (example)
    embedding[0] ?? 0,           // $3 – query location lng (placeholder – should come from user)
    embedding[1] ?? 0,           // $4 – query location lat (placeholder)
    radius * 1000,               // $5 – radius in meters
    validAt,                     // $6 – timestamp
  ];

  // Add metadata placeholders
  Object.values(metadata).forEach(v => params.push(v));

  // Add tsquery and rank query text placeholders
  if (queryText) {
    params.push(queryText);      // $7 – tsquery string
    params.push(queryText);      // $8 – same for rank calculation
  } else {
    params.push('', '');         // dummy placeholders to keep positional indices
  }

  params.push(limit);            // $9
  params.push(offset);           // $10

  const { rows } = await client.query(sql, params);
  return rows as SearchResult[];
}
```

> **Important** – The example above assumes a query location is provided. In a real implementation you would accept a `{ lng, lat }` param and use it for the geographic filter. For brevity the current signature re‑uses the first two embedding components as a placeholder; adjust as needed.

---

## 📄 Migration runner (src/migrate.ts)

```ts
// src/migrate.ts
import { runSqlFile } from './db';
import { join } from 'path';

async function migrate() {
  const migrationsDir = join(__dirname, 'migrations');
  const files = ['001_create_documents.sql', '002_create_indexes.sql'];

  for (const file of files) {
    const path = join(migrationsDir, file);
    console.log(`Running migration: ${path}`);
    await runSqlFile(path);
  }
  console.log('Migrations completed.');
}

migrate().catch(err => {
  console.error('Migration failed', err);
  process.exit(1);
});
```

---

## 🌱 Seed data (src/seed.ts)

```ts
// src/seed.ts
import { pool } from './db';
import { ingestDocument } from './ingest';

async function seed() {
  const client = await pool.connect();

  try {
    // Example documents – location in {lat, lng}
    const docs = [
      {
        content: 'The quick brown fox jumps over the lazy dog.',
        location: { lat: 40.7128, lng: -74.0060 }, // New York
        metadata: { category: 'animals', source: 'test' },
        validFrom: new Date(),
        validTo: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
      },
      {
        content: 'A distant star shines brightly in the night sky.',
        location: { lat: 51.5074, lng: -0.1278 }, // London
        metadata: { category: 'astronomy', source: 'test' },
        validFrom: new Date(),
        validTo: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000),
      },
    ];

    for (const doc of docs) {
      await ingestDocument(pool, doc);
      console.log(`Seeded document ${doc.content.substring(0, 30)}...`);
    }
  } finally {
    client.release();
    await pool.end();
  }
}

seed().catch(err => {
  console.error('Seed failed', err);
  process.exit(1);
});
```

---

## 🧪 Integration tests (tests/search.test.ts)

```ts
// tests/search.test.ts
import { pool } from '../src/db';
import { ingestDocument } from '../src/ingest';
import { hybridSearch } from '../src/search';
import { generateEmbedding } from '../src/embedding';

describe('Hybrid Search Integration', () => {
  // Run after all other tests have set up the DB (migrations & seed)
  beforeAll(async () => {
    // Ensure the pool is connected (migrations already ran)
    await pool.query('SELECT 1');
  });

  afterAll(async () => {
    await pool.end();
  });

  it('should ingest a document and retrieve it via hybrid search', async () => {
    // 1️⃣ Ingest a fresh document
    const docParams = {
      content: 'TypeScript is a typed superset of JavaScript.',
      location: { lat: 37.7749, lng: -122.4194 }, // San Francisco
      metadata: { category: 'tech', priority: 1 },
      validFrom: new Date(),
      validTo: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
    };

    const client = await pool.connect();
    try {
      await ingestDocument(pool, docParams);
    } finally {
      client.release();
    }

    // 2️⃣ Prepare search parameters
    // Use the same deterministic embedding as the ingestion stub
    const queryEmbedding = generateEmbedding(docParams.content, 384);
    const searchParams = {
      embedding: queryEmbedding,
      radius: 100, // km – large enough to include SF
      metadata: { category: 'tech' },
      validAt: new Date(),
      queryText: 'TypeScript',
      limit: 5,
      offset: 0,
    };

    // 3️⃣ Execute hybrid search
    const results = await hybridSearch(client, searchParams);

    // 4️⃣ Assert results
    expect(results.length).toBeGreaterThanOrEqual(1);
    const hit = results[0];
    expect(hit.content).toBe(docParams.content);
    expect(hit.metadata.category).toBe('tech');
    expect(hit.rank).toBeGreaterThan(0);
    expect(hit.distance).toBeGreaterThanOrEqual(0);
  });
});
```

*Run the tests with:* `npm test`.

---

## 🚀 Installation & Usage

1. **Clone / extract the repo** (or create a new folder and paste the files).

2. **Install Node.js (≥ 20)** and **PostgreSQL** (≥ 15).  
   Example on Ubuntu:

   ```bash
   sudo apt-get update
   sudo apt-get install -y postgresql postgresql-contrib
   sudo systemctl start postgresql
   sudo -u postgres psql -c "CREATE EXTENSION IF NOT EXISTS postgis; CREATE EXTENSION IF NOT EXISTS vector;"
   ```

3. **Create a database** (or use the one created by the Docker command below).

4. **Set up environment variables** (optional). Create a `.env` file:

   ```
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/searchdb
   ```

5. **Install dependencies**

   ```bash
   npm ci   # or `npm install`
   ```

6. **Run migrations** – this creates the `documents` table and indexes.

   ```bash
   npm run migrate
   ```

7. **Seed sample data** – populates the table with a couple of documents.

   ```bash
   npm run seed
   ```

8. **Run the integration tests** – verifies ingestion and hybrid search.

   ```bash
   npm test
   ```

9. **Extend / use the APIs** – import `ingestDocument` and `hybridSearch` in your own service, pass your own embedding model, and call them with the required parameters.

---

## 📚 Notes & Extensions

- **Embedding model** – The stub is deterministic and lightweight. In production replace `generateEmbedding` with a call to OpenAI, HuggingFace, or any vector‑generation service. The `embedding` column type (`vector(384)`) remains unchanged.
- **Vector index tuning** – Adjust `lists` in the IVFFlat index based on dataset size. For very large corpora consider `hnsw` (requires `vector` ≥ 0.7.0).
- **Full‑text language** – Change `'english'` to any supported PostgreSQL text search language (`'simple'`, `'french'`, etc.).
- **Metadata filtering** – The current implementation only supports simple equality (`metadata->>'key' = $val`). For complex queries use `jsonb_path_query` or extend the clause builder.
- **Pagination stability** – Ordering by `id` after the other criteria guarantees consistent `OFFSET` results even if new rows are inserted.

---

**That’s the complete, self‑contained example!** Feel free to copy, modify, and expand it for your own search‑as‑a‑service needs. Happy coding!
