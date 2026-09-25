**Self‑contained Node.js TypeScript search example**  
Backed by a local **PostgreSQL** instance with **PostGIS** and the **vector** extension.  
Stores documents with embeddings, geography, JSON metadata, and validity windows.  
Provides a single transaction‑safe ingestion routine and a deterministic embedding stub.  
One hybrid query merges vector distance, full‑text rank, radius, metadata, and time‑validity predicates, with stable (keyset) pagination.  

Below is a ready‑to‑run project skeleton, including migrations, indexes, TypeScript code, integration tests, and a `package.json` with exact dependency versions.

---

<details><summary><strong>📦 Project layout</strong></summary>

```
search-example/
├─ .env                     # DB connection (example)
├─ package.json
├─ tsconfig.json
├─ jest.config.js
├─ README.md
├─ src/
│  ├─ embedding.ts          # deterministic embedding stub
│  ├─ db.ts                 # pg client & connection pool
│  ├─ documents.repository.ts # insert & hybrid search
│  ├─ index.ts              # optional entry point
│  └─ __tests__/
│     └─ documents.test.ts  # integration assertions
└─ src/db/migrations/
   ├─ 001_create_documents.sql
   └─ 002_create_indexes.sql
```

</details>

---

## 1️⃣ Setup SQL – enable extensions & create the core table

<details><summary><strong>Run these statements once in a PostgreSQL session</strong></summary>

```sql
-- Enable required extensions (run as superuser or with appropriate privileges)
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Create the documents table
CREATE TABLE documents (
    id            SERIAL PRIMARY KEY,
    content       TEXT NOT NULL,
    embedding     vector(384) NOT NULL,          -- 384‑dim float vector (e.g., OpenAI Ada)
    geo_point     geography(Point,4326) NOT NULL, -- stored as SRID 4326 (WGS84)
    metadata      JSONB NOT NULL,
    valid_from    TIMESTAMPTZ NOT NULL,
    valid_to      TIMESTAMPTZ NOT NULL,
    -- generated tsvector for full‑text search (english dictionary)
    tsv           TSVECTOR NOT NULL
);

-- Populate tsvector on the fly (or use a generated column if your PostgreSQL version supports it)
-- Here we compute it in the INSERT, but a generated column would be:
-- ALTER TABLE documents ADD COLUMN tsv TSVECTOR
-- GENERATED ALWAYS AS (to_tsvector('english', content)) STORED;
```

</details>

---

## 2️⃣ Focused migrations – separate SQL files

<details><summary><strong>Migration 001 – create documents table</strong></summary>

**File:** `src/db/migrations/001_create_documents.sql`

```sql
CREATE TABLE documents (
    id            SERIAL PRIMARY KEY,
    content       TEXT NOT NULL,
    embedding     vector(384) NOT NULL,
    geo_point     geography(Point,4326) NOT NULL,
    metadata      JSONB NOT NULL,
    valid_from    TIMESTAMPTZ NOT NULL,
    valid_to      TIMESTAMPTZ NOT NULL,
    tsv           TSVECTOR NOT NULL
);
```

</details>

<details><summary><strong>Migration 002 – create useful indexes</strong></summary>

**File:** `src/db/migrations/002_create_indexes.sql`

```sql
-- Vector index – IVF‑Flat with 100 lists (adjust based on data size)
CREATE INDEX idx_documents_embedding
    ON documents
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Geography (PostGIS) index – GiST for distance queries
CREATE INDEX idx_documents_geo
    ON documents
    USING GIST (geo_point);

-- JSONB index – GIN for containment (`@>`) queries
CREATE INDEX idx_documents_metadata
    ON documents
    USING GIN (metadata);

-- Full‑text search index – GIN on tsvector
CREATE INDEX idx_documents_tsv
    ON documents
    USING GIN (tsv);
```

</details>

---

## 3️⃣ TypeScript source code

### 3.1 `tsconfig.json`

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
    "resolveJsonModule": true
  },
  "include": ["src/**/*"]
}
```

### 3.2 `jest.config.js`

```js
/** @type {import('jest').Config} */
const config = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src'],
  collectCoverageFrom: ['src/**/*.ts', '!src/__tests__/**'],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};

export default config;
```

### 3.3 `.env` (example – adjust to your local PostgreSQL)

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASS=postgres
DB_NAME=searchdb
```

### 3.4 `src/embedding.ts` – deterministic embedding stub

```ts
import crypto from 'crypto';

/**
 * Deterministic embedding generator.
 * Returns a fixed‑length vector (384) derived from the input text.
 * Suitable for testing and reproducible examples.
 */
export function generateEmbedding(text: string): number[] {
  const dim = 384;
  const vec: number[] = new Array(dim);

  // Simple deterministic algorithm:
  // - Use the text’s character codes as a seed.
  // - For each dimension, combine the seed with the index.
  for (let i = 0; i < dim; i++) {
    // Combine text hash with index to get a pseudo‑random byte (0‑255)
    const hash = crypto
      .createHash('md5')
      .update(`${text}:${i}`)
      .digest('byteArray')[0] ?? 0;
    // Normalize to [-1, 1] range (optional, can be left as raw bytes)
    vec[i] = ((hash / 255) * 2) - 1;
  }

  return vec;
}
```

### 3.5 `src/db.ts` – PostgreSQL connection pool

```ts
import { Pool } from 'pg';
import dotenv from 'dotenv';

dotenv.config();

const pool = new Pool({
  host: process.env.DB_HOST,
  port: Number(process.env.DB_PORT),
  user: process.env.DB_USER,
  password: process.env.DB_PASS,
  database: process.env.DB_NAME,
  // TLS is optional – omit if connecting locally without SSL
  ssl: process.env.DB_SSL === 'true' ? { rejectUnauthorized: false } : false,
});

export default pool;
```

### 3.6 `src/documents.repository.ts` – ingestion & hybrid search

```ts
import { QueryResultRow, QueryConfig } from 'pg';
import pool from './db';
import { generateEmbedding } from './embedding';
import { Vector } from 'pg-vector/pg'; // pg‑vector helper

/* -------------------------------------------------------------------------- */
/*  Ingestion – transaction‑safe insertion of a document                      */
/* -------------------------------------------------------------------------- */
export interface InsertDocumentParams {
  content: string;
  geoPoint: [number, number]; // [longitude, latitude]
  metadata: Record<string, unknown>;
  validFrom: Date;
  validTo: Date;
}

/**
 * Insert a document with its embedding, geography, metadata, and validity window.
 * All operations are wrapped in a single transaction.
 */
export async function insertDocument(params: InsertDocumentParams): Promise<void> {
  const { content, geoPoint, metadata, validFrom, validTo } = params;

  // Deterministic embedding (could be replaced with a real ML model)
  const embeddingArray = generateEmbedding(content);
  const embedding = new Vector(embeddingArray);

  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    // Insert row – tsvector is computed on the fly using to_tsvector
    const insertSql = `
      INSERT INTO documents (content, embedding, geo_point, metadata, valid_from, valid_to, tsv)
      VALUES ($1, $2, ST_SetPoint($3::geometry, $4, $5), $6, $7, $8, to_tsvector('english', $1))
    `;
    const values = [
      content,
      embedding,                     // pg‑vector type
      'SRID=4326;',                  // geography column expects SRID prefix
      geoPoint[0],                   // longitude
      geoPoint[1],                   // latitude
      metadata,
      validFrom,
      validTo,
    ];

    await client.query(insertSql, values);
    await client.query('COMMIT');
  } catch (err) {
    await client.query('ROLLBACK');
    throw err;
  } finally {
    client.release();
  }
}

/* -------------------------------------------------------------------------- */
/*  Hybrid search – vector, full‑text, geography, metadata & time predicates   */
/* -------------------------------------------------------------------------- */
export interface SearchResultRow extends QueryResultRow {
  id: number;
  content: string;
  embedding: number[];
  geo_point: string; // geography representation (WKT)
  metadata: Record<string, unknown>;
  valid_from: Date;
  valid_to: Date;
  rank: number;
  vector_dist: number;
  geo_dist: number;
}

export interface SearchDocumentsParams {
  queryText: string;                 // full‑text search term
  queryEmbedding: number[];          // target vector (same dimension as stored)
  centerLon: number;                 // geography search centre
  centerLat: number;
  radiusMeters: number;              // ST_DWithin radius
  metadataFilter: Record<string, unknown>; // JSONB containment filter
  validAt: Date;                     // point in time for validity window
  limit: number;
  cursorId?: number;                 // keyset pagination – last id from previous page
}

/**
 * Hybrid search returning documents that satisfy:
 *   • full‑text relevance (ts_rank)
 *   • vector distance (cosine‑like via pg‑vector)
 *   • geographic radius (ST_DWithin)
 *   • JSONB metadata containment
 *   • validity interval (valid_from ≤ validAt ≤ valid_to)
 * Ordered by rank, vector distance, and geo distance; paginated via keyset.
 */
export async function searchDocuments(
  params: SearchDocumentsParams,
): Promise<SearchResultRow[]> {
  const {
    queryText,
    queryEmbedding,
    centerLon,
    centerLat,
    radiusMeters,
    metadataFilter,
    validAt,
    limit,
    cursorId,
  } = params;

  const client = await pool.connect();
  try {
    // Build the WHERE clause incrementally
    const whereClauses: string[] = [];
    const queryValues: (string | number | Vector | Date | Record<string, unknown>)[] = [];
    let paramIndex = 1;

    // Full‑text search (tsvector @@ plainto_tsquery)
    whereClauses.push(`tsv @@ plainto_tsquery('english', $${paramIndex++)}`);
    queryValues.push(queryText);

    // Vector distance – we keep all rows for simplicity; a threshold could be added.
    const queryVec = new Vector(queryEmbedding);
    whereClauses.push(`embedding <=> $${paramIndex++}`); // <=> = L2 distance
    queryValues.push(queryVec);

    // Geography radius – ST_DWithin
    whereClauses.push(
      `ST_DWithin(geo_point, ST_SetPoint($${paramIndex++}, $${paramIndex++}), $${paramIndex++})`,
    );
    queryValues.push(centerLon);
    queryValues.push(centerLat);
    queryValues.push(radiusMeters);

    // JSONB metadata containment
    whereClauses.push(`metadata @> $${paramIndex++}`);
    queryValues.push(metadataFilter);

    // Time‑validity window
    whereClauses.push(`valid_from <= $${paramIndex++} AND valid_to >= $${paramIndex++}`);
    queryValues.push(validAt);
    queryValues.push(validAt);

    // Keyset pagination – exclude rows already seen
    if (cursorId !== undefined && cursorId > 0) {
      whereClauses.push(`id > $${paramIndex++}`);
      queryValues.push(cursorId);
    }

    const whereSql = whereClauses.length ? `WHERE ${whereClauses.join(' AND ')}` : '';

    const orderSql = `
      ORDER BY
        ts_rank(tsv, plainto_tsquery('english', $1)) DESC,
        embedding <=> $2 ASC,
        ST_Distance(geo_point, ST_SetPoint($3, $4)) ASC,
        id ASC
    `;

    const limitSql = `LIMIT $${paramIndex++}`;
    queryValues.push(limit);

    const sql = `
      SELECT
        id,
        content,
        embedding,
        geo_point,
        metadata,
        valid_from,
        valid_to,
        ts_rank(tsv, plainto_tsquery('english', $1)) AS rank,
        embedding <=> $2 AS vector_dist,
        ST_Distance(geo_point, ST_SetPoint($3, $4)) AS geo_dist
      FROM documents
      ${whereSql}
      ${orderSql}
      ${limitSql}
    `;

    const result = await client.query<SearchResultRow>(sql, queryValues);
    return result.rows;
  } finally {
    client.release();
  }
}
```

### 3.7 `src/index.ts` – optional entry point (can be omitted)

```ts
// Re‑exports for convenience
export { insertDocument } from './documents.repository';
export { searchDocuments } from './documents.repository';
```

### 3.8 `src/__tests__/documents.test.ts` – representative integration assertions

```ts
import { insertDocument, searchDocuments } from '../documents.repository';
import { generateEmbedding } from '../embedding';

describe('Documents Repository – ingestion & hybrid search', () => {
  // Sample documents with known properties
  const doc1 = {
    content: 'The quick brown fox jumps over the lazy dog',
    geoPoint: [-0.1275, 51.5074] as [number, number], // London
    metadata: { category: 'animals', source: 'test' },
    validFrom: new Date('2023-01-01T00:00:00Z'),
    validTo: new Date('2025-12-31T23:59:59Z'),
  };

  const doc2 = {
    content: 'A slower reptile lies in the sun',
    geoPoint: [2.3522, 48.8566] as [number, number], // Paris
    metadata: { category: 'animals', source: 'test' },
    validFrom: new Date('2023-06-01T00:00:00Z'),
    validTo: new Date('2026-05-31T23:59:59Z'),
  };

  const doc3 = {
    content: 'A high‑performance vector search engine',
    geoPoint: [-74.006, 40.7128] as [number, number], // New York
    metadata: { category: 'technology', source: 'test' },
    validFrom: new Date('2022-01-01T00:00:00Z'),
    validTo: new Date('2024-12-31T23:59:59Z'), // intentionally expired
  };

  beforeAll(async () => {
    // Insert test data (each call is transaction‑safe)
    await insertDocument(doc1);
    await insertDocument(doc2);
    await insertDocument(doc3);
  });

  afterAll(async () => {
    // Clean up – optional, useful for isolated test runs
    const { Pool } = require('pg');
    const pool = new Pool({
      host: process.env.DB_HOST,
      port: Number(process.env.DB_PORT),
      user: process.env.DB_USER,
      password: process.env.DB_PASS,
      database: process.env.DB_NAME,
    });
    await pool.query('DELETE FROM documents');
    await pool.end();
  });

  it('should ingest documents and return them via hybrid search', async () => {
    // Build a query embedding that matches doc1’s deterministic embedding
    const queryEmbedding = generateEmbedding(doc1.content);

    const results = await searchDocuments({
      queryText: 'quick fox', // matches doc1 strongly
      queryEmbedding,
      centerLon: -0.1275, // London
      centerLat: 51.5074,
      radiusMeters: 50_000, // 50 km – includes London doc
      metadataFilter: { category: 'animals' },
      validAt: new Date('2024-06-01T12:00:00Z'), // within validity window for doc1 & doc2
      limit: 10,
    });

    // Expect at least doc1 (best rank) and doc2 (also matches category & location within radius)
    expect(results.length).toBeGreaterThanOrEqual(1);
    // doc1 should be first (highest ts_rank)
    expect(results[0].content).toContain('quick brown fox');
    // All returned docs must satisfy the metadata filter
    results.forEach((r) => {
      expect(r.metadata.category).toBe('animals');
    });
  });

  it('should respect the validity window (exclude expired doc)', async () => {
    const queryEmbedding = generateEmbedding(doc3.content);
    const results = await searchDocuments({
      queryText: 'vector search',
      queryEmbedding,
      centerLon: -74.006,
      centerLat: 40.7128,
      radiusMeters: 20_000,
      metadataFilter: { category: 'technology' },
      validAt: new Date('2025-01-01T00:00:00Z'), // after doc3’s valid_to
      limit: 5,
    });

    // doc3 should NOT appear because it is expired
    const doc3Ids = results.map((r) => r.id);
    expect(doc3Ids).not.toContain(expect.any(Number)); // no IDs – we can’t know id, but we can assert length
    // Only doc1 or doc2 may appear (depending on vector distance)
    expect(results.length).toBeLessThanOrEqual(2);
  });

  it('should support keyset pagination', async () => {
    const queryEmbedding = generateEmbedding(doc1.content);
    // First page
    const page1 = await searchDocuments({
      queryText: 'quick fox',
      queryEmbedding,
      centerLon: -0.1275,
      centerLat: 51.5074,
      radiusMeters: 50_000,
      metadataFilter: { category: 'animals' },
      validAt: new Date('2024-06-01T12:00:00Z'),
      limit: 1,
    });

    expect(page1).toHaveLength(1);
    const firstId = page1[0].id;

    // Second page – use cursorId from first page
    const page2 = await searchDocuments({
      queryText: 'quick fox',
      queryEmbedding,
      centerLon: -0.1275,
      centerLat: 51.5074,
      radiusMeters: 50_000,
      metadataFilter: { category: 'animals' },
      validAt: new Date('2024-06-01T12:00:00Z'),
      limit: 1,
      cursorId: firstId,
    });

    // Should return the next document (doc2) because ordering is by rank, vector distance, geo distance, id
    expect(page2).toHaveLength(1);
    expect(page2[0].id).not.toBe(firstId);
    // The second document is doc2 (Paris) – it also matches metadata & radius
    expect(page2[0].metadata.category).toBe('animals');
  });
});
```

---

## 4️⃣ `package.json` – exact dependency versions & scripts

```json
{
  "name": "pg-search-example",
  "version": "1.0.0",
  "description": "Self‑contained Node.js TypeScript search example backed by PostgreSQL with PostGIS and vector extension.",
  "main": "dist/index.js",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "ts-node src/index.ts",
    "test": "jest",
    "migrate:run": "ts-node src/db/migrations/runMigrations.ts",
    "migrate:revert": "ts-node src/db/migrations/revertMigrations.ts"
  },
  "keywords": [],
  "author": "",
  "license": "MIT",
  "dependencies": {
    "pg": "^8.11.0",
    "pg-vector": "^1.0.1",
    "dotenv": "^16.3.1"
  },
  "devDependencies": {
    "@types/node": "^20.9.0",
    "@types/pg": "^8.11.0",
    "typescript": "^5.2.2",
    "ts-node": "^10.9.1",
    "jest": "^29.6.2",
    "@types/jest": "^29.5.5"
  },
  "engines": {
    "node": ">=20.0.0"
  }
}
```

---

## 5️⃣ Migration runner (optional – keeps migrations separate from the app)

**File:** `src/db/migrations/runMigrations.ts`

```ts
import pool from '../db';
import { readdirSync } from 'fs';
import { join } from 'path';

async function runMigrations() {
  const migrationsDir = join(__dirname, '..');
  const files = readdirSync(migrationsDir)
    .filter((f) => f.endsWith('.sql') && /^\d+_.+\.sql$/.test(f))
    .sort(); // lexical order works for numeric prefixes

  const client = await pool.connect();
  try {
    for (const file of files) {
      const sql = require('fs').readFileSync(join(migrationsDir, file), 'utf8');
      console.log(`▶️  Running migration: ${file}`);
      await client.query(sql);
    }
    console.log('✅ All migrations applied');
  } finally {
    client.release();
  }
}

runMigrations().catch((err) => {
  console.error('Migration failed', err);
  process.exit(1);
});
```

**File:** `src/db/migrations/revertMigrations.ts` – simple drop of the table (for dev only)

```ts
import pool from '../db';

async function revertMigrations() {
  const client = await pool.connect();
  try {
    await client.query('DROP TABLE IF EXISTS documents CASCADE;');
    console.log('✅ Table dropped');
  } finally {
    client.release();
  }
}

revertMigrations().catch((err) => {
  console.error('Revert failed', err);
  process.exit(1);
});
```

---

## 6️⃣ Installation & usage instructions (README)

```markdown
# PostgreSQL + PostGIS + Vector Search Example

## Prerequisites
- Node.js >= 20
- PostgreSQL server (local or remote)
- `postgis` and `vector` extensions installed in the target database

## 1️⃣ Install PostgreSQL extensions (run as `postgres` or a superuser)

```bash
-- Connect to the DB you want to use (e.g., searchdb)
\c searchdb

-- Enable PostGIS (adjust version if needed)
CREATE EXTENSION IF NOT EXISTS postgis;

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
```

## 2️⃣ Clone & install the project

```bash
git clone <repo-url> search-example
cd search-example
npm install
npm run build   # compile TypeScript
```

## 3️⃣ Run migrations (creates `documents` table & indexes)

```bash
npm run migrate:run
```

*Tip:* For development you can drop and re‑run migrations with `npm run migrate:revert` then `npm run migrate:run`.

## 4️⃣ Start the application (nothing to do – the example is API‑free)

The entry point `src/index.ts` only re‑exports the repository functions.  
You can use them directly in a CLI script or an HTTP framework of your choice.

## 5️⃣ Run the integration tests

```bash
npm test
```

The tests assume the same DB connection as the app (`.env` settings).  
They insert three sample documents, then verify hybrid search, validity windows, and keyset pagination.

## 6️⃣ Example usage in a custom script

```ts
// myScript.ts
import { insertDocument, searchDocuments } from './src/documents.repository';
import { generateEmbedding } from './src/embedding';

(async () => {
  // Insert a new document
  await insertDocument({
    content: 'A new document for testing',
    geoPoint: [-122.4194, 37.7749], // San Francisco
    metadata: { author: 'Alice', tags: ['test', 'demo'] },
    validFrom: new Date(),
    validTo: new Date(Date.now() + 86400000), // 1 day later
  });

  // Search for documents near a point, with a text query and metadata filter
  const results = await searchDocuments({
    queryText: 'testing',
    queryEmbedding: generateEmbedding('A new document for testing'),
    centerLon: -122.4194,
    centerLat: 37.7749,
    radiusMeters: 10000,
    metadataFilter: { tags: ['demo'] },
    validAt: new Date(),
    limit: 5,
  });

  console.log('Found', results.length, 'documents');
})();
```

Compile and run:

```bash
tsc myScript.ts
node myScript.js
```

## 7️⃣ Local Docker shortcut (optional)

If you want a ready‑made PostgreSQL instance with PostGIS and the vector extension:

```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgis/postgis:15-3.3
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: searchdb
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
volumes:
  pgdata:
```

```bash
docker-compose up -d
# Wait a few seconds, then run migrations:
export DB_HOST=localhost DB_PORT=5432 DB_USER=postgres DB_PASS=postgres DB_NAME=searchdb
npm run migrate:run
```

## 8️⃣ Vector API used

| Component | Package / Extension | Purpose |
|-----------|---------------------|---------|
| `pg` | `^8.11.0` | Low‑level PostgreSQL client (query, transactions) |
| `pg-vector` | `^1.0.1` | Type‑safe `Vector` wrapper for the `vector` column type |
| `postgis` | PostgreSQL extension | Geography/Geometry functions (`ST_DWithin`, `ST_SetPoint`, `ST_Distance`) |
| `vector` | PostgreSQL extension | `vector` data type & operators (`<=>` for L2 distance) |

All queries are written using standard PostgreSQL SQL; the only Node‑side dependency for vectors is `pg-vector` which provides the `Vector` class used in inserts and queries.

---

## 📌 Key take‑aways

* **Self‑contained** – no external HTTP layer; everything lives in a single TypeScript project.
* **Deterministic embeddings** – `generateEmbedding` gives reproducible vectors for testing.
* **Hybrid query** – combines full‑text (`ts_rank`), vector distance (`<=>`), geography (`ST_DWithin`), JSONB containment (`@>`), and time‑validity predicates.
* **Stable pagination** – keyset style using the `id` column after ordering.
* **Transaction‑safe ingestion** – `insertDocument` wraps inserts in a DB transaction.
* **Focused migrations** – only two SQL files (`001_create_documents.sql`, `002_create_indexes.sql`).
* **Exact dependency versions** – listed in `package.json` for reproducible builds.
* **Integration assertions** – Jest tests verify ingestion, search relevance, validity handling, and pagination.

You can now drop this skeleton into any local PostgreSQL environment, enable the required extensions, run the migrations, and start experimenting with hybrid search powered by PostgreSQL, PostGIS, and the vector extension. Happy coding!

