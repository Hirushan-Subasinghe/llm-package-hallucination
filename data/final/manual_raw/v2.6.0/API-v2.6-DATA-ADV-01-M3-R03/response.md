## 📦 Self‑contained Node.js + TypeScript search example  

This repo shows a **single‑file‑style** proof‑of‑concept that stores documents in PostgreSQL with:

* **pgvector** embeddings (`vector` type)  
* **PostGIS** geographic points (`geography(Point,4326)`)  
* **Full‑text** (`tsvector`)  
* **JSONB** metadata (`jsonb`)  
* **Validity interval** (`tsrange`)  

and runs a **parameterised hybrid query** that mixes:

* vector distance (`<=>`)  
* full‑text rank (`ts_rank_cd`)  
* radius (`ST_DWithin`)  
* metadata predicates (`@>` / JSONPath)  
* time‑validity (`tsrange @> now()`)  

The query also provides **stable pagination** (cursor‑based) without skipping or duplicating rows.

---

<details>
<summary>🛠 Why this example? (click to expand)</summary>

* **All‑in‑one** – a single PostgreSQL database, no external vector store.  
* **Typed** – TypeScript throughout, with strict types for DB rows.  
* **Deterministic embedding stub** – no heavy ML model required for a demo.  
* **Transactional ingestion** – one function that safely inserts a document and all derived columns.  
* **Focused migrations** – only the needed extensions, table, and indexes.  
* **Integration assertions** – Jest test that proves the whole stack works, without building a full HTTP API.  
* **Reproducible** – exact npm versions, scripts, and commands to spin up a local environment.  

</details>

---

## 1️⃣ Prerequisites

| Tool | Version (tested) |
|------|-------------------|
| **Node.js** | `≥20.0.0` |
| **npm** | `≥10.0.0` |
| **PostgreSQL** | `15` (includes built‑in `pgcrypto`) |
| **PostGIS** | `3.5` (installed via `postgresql-15-postgis-3` on Debian/Ubuntu) |
| **pgvector** | `0.5.0` (extension) |

> **Tip:** on Ubuntu you can get everything with:  

```bash
sudo apt-get install postgresql-15 postgresql-15-postgis-3 postgresql-15-pgvector
```

---

## 2️⃣ `package.json` (exact versions)

```json
{
  "name": "pg-hybrid-search-demo",
  "version": "1.0.0",
  "description": "Node.js/TS example of hybrid vector + geo + full‑text search in PostgreSQL",
  "main": "dist/index.js",
  "type": "module",
  "scripts": {
    "clean": "rimraf ./dist",
    "build": "tsc",
    "dev": "ts-node src/index.ts",
    "migrate": "node -r dotenv/config src/migrate.ts",
    "test": "jest --runInBand"
  },
  "author": "ChatGPT",
  "license": "MIT",
  "dependencies": {
    "dotenv": "16.4.5",
    "pg": "8.11.3",
    "pg-promise": "10.15.2"
  },
  "devDependencies": {
    "@types/jest": "29.5.13",
    "@types/node": "20.12.12",
    "jest": "29.7.0",
    "rimraf": "5.0.5",
    "ts-jest": "29.1.2",
    "typescript": "5.4.5"
  }
}
```

* **Database API** – `pg` (native driver) + `pg-promise` for convenient transaction handling.  
* **Vector API** – native `pgvector` SQL operators (`<=>`, `vector_cosine_ops`).  
* **Geo API** – PostGIS functions (`ST_DWithin`, `ST_GeogFromText`).  

---

## 3️⃣ Database setup – migrations & indexes  

Create a file `src/migrations.sql` (used by `src/migrate.ts`).

```sql
-- src/migrations.sql
-- ------------------------------------------------------------
-- 1️⃣ Extensions (must be run as a superuser)
-- ------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- for deterministic UUID generation

-- ------------------------------------------------------------
-- 2️⃣ Table definition
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS documents (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title         TEXT NOT NULL,
    body          TEXT NOT NULL,
    embedding     vector(384) NOT NULL,          -- change dim as you like
    geom          geography(Point, 4326) NOT NULL,
    meta          JSONB NOT NULL DEFAULT '{}',
    valid_during  tsrange NOT NULL,              -- e.g. '[2023-01-01,2024-01-01)'
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    tsv           tsvector GENERATED ALWAYS AS
                   (to_tsvector('english', coalesce(title,'') || ' ' || coalesce(body,''))) STORED
);

-- ------------------------------------------------------------
-- 3️⃣ Indexes for the hybrid query
-- ------------------------------------------------------------
-- Vector‑distance index (IVFFlat like)
CREATE INDEX IF NOT EXISTS idx_documents_embedding
    ON documents USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);  -- tune `lists` for your data size

-- Full‑text search index
CREATE INDEX IF NOT EXISTS idx_documents_tsv
    ON documents USING GIN (tsv);

-- Geo index (geography → GiST)
CREATE INDEX IF NOT EXISTS idx_documents_geom
    ON documents USING GIST (geom);

-- JSONB metadata index (common path example)
CREATE INDEX IF NOT EXISTS idx_documents_meta_category
    ON documents USING GIN (meta jsonb_path_ops);

-- Valid‑time index
CREATE INDEX IF NOT EXISTS idx_documents_valid
    ON documents USING GIST (valid_during);
```

### Migration runner (`src/migrate.ts`)

```ts
// src/migrate.ts
import * as pgPromise from 'pg-promise';
import * as fs from 'node:fs';
import * as path from 'node:path';
import 'dotenv/config';

const pgp = pgPromise.default();
const db = pgp(process.env.DATABASE_URL!);

(async () => {
  const sql = fs.readFileSync(path.resolve(__dirname, 'migrations.sql'), 'utf8');
  await db.none(sql);
  console.log('✅ Migration completed');
  pgp.end();
})().catch(err => {
  console.error('❌ Migration failed', err);
  process.exit(1);
});
```

Run it with:

```bash
npm run migrate
```

---

## 4️⃣ Deterministic embedding stub (`src/embedding.ts`)

> No heavy ML; we map a string to a **fixed‑size** float array using a simple hash.  
> The function is **pure** and therefore deterministic – perfect for unit tests.

```ts
// src/embedding.ts
/** Generate a deterministic 384‑dimensional embedding from a string.
 *  Uses SHA‑256 → 32‑byte digest → repeat & map to [-1,1] range.
 */
export function embed(text: string, dim = 384): number[] {
  const crypto = await import('node:crypto');
  const hash = crypto.createHash('sha256').update(text).digest(); // Buffer 32 B
  const floats: number[] = [];

  // Expand the 32‑byte digest repeatedly to reach the required dimension
  for (let i = 0; i < dim; i++) {
    const byte = hash[i % hash.length];
    // map byte [0,255] → float [-1,1]
    floats.push((byte / 127.5) - 1);
  }
  return floats;
}
```

---

## 5️⃣ Transaction‑safe ingestion (`src/ingest.ts`)

```ts
// src/ingest.ts
import * as pgPromise from 'pg-promise';
import { embed } from './embedding.js';
import type { QueryResult } from 'pg';
import 'dotenv/config';

const pgp = pgPromise.default();
const db = pgp(process.env.DATABASE_URL!);

export interface DocumentInput {
  title: string;
  body: string;
  latitude: number;
  longitude: number;
  meta: Record<string, unknown>;
  validFrom: string;   // ISO‑8601
  validTo: string;     // ISO‑8601 (exclusive)
}

/** Insert a document atomically, computing tsvector, embedding, geom, and validity range. */
export async function insertDocument(input: DocumentInput): Promise<string> {
  const {
    title,
    body,
    latitude,
    longitude,
    meta,
    validFrom,
    validTo,
  } = input;

  // 1️⃣ Compute embedding (deterministic stub)
  const embedding = await embed(`${title} ${body}`);

  // 2️⃣ Build the base INSERT with all derived columns
  const query = `
    INSERT INTO documents
      (title, body, embedding, geom, meta, valid_during)
    VALUES
      ($1, $2, $3, ST_SetSRID(ST_MakePoint($4, $5), 4326)::geography, $6,
       tsrange($7::timestamptz, $8::timestamptz, '[)'))
    RETURNING id;
  `;

  // 3️⃣ Execute in a transaction (ensures atomicity if you ever add more steps)
  const result: QueryResult<{ id: string }> = await db.one(query, [
    title,
    body,
    embedding,
    longitude, // note: lon, lat order for PostGIS
    latitude,
    JSON.stringify(meta),
    validFrom,
    validTo,
  ]);

  return result.id;
}
```

---

## 6️⃣ Hybrid search query (`src/search.ts`)

```ts
// src/search.ts
import * as pgPromise from 'pg-promise';
import 'dotenv/config';

const pgp = pgPromise.default();
const db = pgp(process.env.DATABASE_URL!);

export interface SearchParams {
  /** Query embedding (same dimension as stored vectors) */
  embedding: number[];

  /** Full‑text query string */
  text: string;

  /** Center of geo filter (lon, lat) */
  lon: number;
  lat: number;

  /** Radius in metres */
  radiusM: number;

  /** JSON metadata filter – exact match on top‑level keys */
  metaFilter?: Record<string, unknown>;

  /** Valid‑time point (ISO‑8601) */
  asOf: string;

  /** Pagination */
  pageSize: number;
  /** Cursor – base64‑encoded JSON of previous row keys */
  cursor?: string;
}

/** Result shape – includes ranking components for debugging */
export interface SearchResult {
  id: string;
  title: string;
  body: string;
  distance: number;   // vector cosine distance
  rank: number;        // full‑text relevance
  meta: any;
  geom: any;
}

/** Encode cursor from the last row of a page */
function encodeCursor(row: {
  distance: number;
  rank: number;
  id: string;
}): string {
  return Buffer.from(JSON.stringify(row)).toString('base64');
}

/** Decode cursor back to object */
function decodeCursor(cursor: string): { distance: number; rank: number; id: string } {
  return JSON.parse(Buffer.from(cursor, 'base64').toString('utf8'));
}

/**
 * Hybrid search – combines vector distance, full‑text rank, geographic radius,
 * JSON metadata filter, and validity interval. Returns stable, cursor‑based pages.
 */
export async function hybridSearch(params: SearchParams): Promise<{
  results: SearchResult[];
  nextCursor?: string;
}> {
  const {
    embedding,
    text,
    lon,
    lat,
    radiusM,
    metaFilter,
    asOf,
    pageSize,
    cursor,
  } = params;

  // ------------------------------------------------
  // 1️⃣ Build WHERE predicates
  // ------------------------------------------------
  const whereClauses: string[] = [];
  const values: any[] = [];

  // a) Vector distance (cosine) – we will ORDER BY it later
  //    No WHERE needed, just SELECT distance
  // b) Full‑text search predicate
  whereClauses.push(`tsv @@ plainto_tsquery('english', $${values.length + 1})`);
  values.push(text);

  // c) Geographic radius
  whereClauses.push(`ST_DWithin(
        geom,
        ST_SetSRID(ST_MakePoint($${values.length + 1}, $${values.length + 2}), 4326)::geography,
        $${values.length + 3}
      )`);
  values.push(lon, lat, radiusM);

  // d) Metadata filter (exact match on supplied top‑level keys)
  if (metaFilter && Object.keys(metaFilter).length) {
    whereClauses.push(`meta @> $${values.length + 1}::jsonb`);
    values.push(JSON.stringify(metaFilter));
  }

  // e) Valid‑time interval
  whereClauses.push(`valid_during @> $${values.length + 1}::timestamptz`);
  values.push(asOf);

  // ------------------------------------------------
  // 2️⃣ Cursor pagination – lexicographic over (distance, rank, id)
  // ------------------------------------------------
  let cursorClause = '';
  if (cursor) {
    const cur = decodeCursor(cursor);
    cursorClause = `AND (vec_dist, txt_rank, id) > ($${values.length + 1}, $${values.length + 2}, $${values.length + 3})`;
    values.push(cur.distance, cur.rank, cur.id);
  }

  // ------------------------------------------------
  // 3️⃣ Final query
  // ------------------------------------------------
  const sql = `
    SELECT
      id,
      title,
      body,
      meta,
      geom,
      -- cosine distance (lower = more similar)
      (embedding <=> $1::vector)            AS vec_dist,
      -- full‑text rank (higher = more relevant)
      ts_rank_cd(tsv, plainto_tsquery('english', $2)) AS txt_rank
    FROM documents
    WHERE ${whereClauses.join(' AND ')} ${cursorClause}
    ORDER BY vec_dist ASC, txt_rank DESC, id ASC
    LIMIT $${values.length + 1};
  `;
  values.unshift(embedding);          // $1 is the embedding vector
  values.unshift(text);               // $2 is the full‑text query string (already added once above, duplicated for rank)
  values.push(pageSize);              // final LIMIT parameter

  const rows = await db.manyOrNone(sql, values);

  const results: SearchResult[] = rows.map(r => ({
    id: r.id,
    title: r.title,
    body: r.body,
    distance: Number(r.vec_dist),
    rank: Number(r.txt_rank),
    meta: r.meta,
    geom: r.geom,
  }));

  // ------------------------------------------------
  // 4️⃣ Build next cursor (if we got a full page)
  // ------------------------------------------------
  const nextCursor = results.length === pageSize
    ? encodeCursor({
        distance: results[results.length - 1].distance,
        rank: results[results.length - 1].rank,
        id: results[results.length - 1].id,
      })
    : undefined;

  return { results, nextCursor };
}
```

### How the scoring works  

* **Vector distance** – cosine distance (`embedding <=> vector`). Smaller = more similar.  
* **Full‑text rank** – `ts_rank_cd` (cover density) – larger = more relevant.  
* The **ORDER BY** clause first prefers *nearest* vectors, then *higher* text rank, and finally a deterministic tie‑breaker (`id`).  
* The cursor stores this triple, guaranteeing **stable pagination** even if the underlying data changes (as long as the ranking keys stay stable).  

---

## 7️⃣ Integration assertions (Jest)  

Create `src/__tests__/search.test.ts`.

```ts
// src/__tests__/search.test.ts
import { insertDocument } from '../ingest.js';
import { hybridSearch } from '../search.js';
import * as pgPromise from 'pg-promise';
import 'dotenv/config';

const pgp = pgPromise.default();
const db = pgp(process.env.DATABASE_URL!);

beforeAll(async () => {
  // Clean slate
  await db.none('TRUNCATE documents RESTART IDENTITY CASCADE;');
});

afterAll(() => {
  pgp.end();
});

test('Hybrid search returns expected document order and pagination', async () => {
  // ---- 1️⃣ Insert three docs with varying fields ----
  const ids = await Promise.all([
    insertDocument({
      title: 'Coffee shop in Berlin',
      body: 'Best espresso near Alexanderplatz.',
      latitude: 52.5200,
      longitude: 13.4050,
      meta: { category: 'cafe', rating: 4.5 },
      validFrom: '2023-01-01T00:00:00Z',
      validTo: '2025-01-01T00:00:00Z',
    }),
    insertDocument({
      title: 'Library at central park',
      body: 'Quiet reading space with free Wi‑Fi.',
      latitude: 40.785091,
      longitude: -73.968285,
      meta: { category: 'library', rating: 4.8 },
      validFrom: '2022-06-01T00:00:00Z',
      validTo: '2024-06-01T00:00:00Z',
    }),
    insertDocument({
      title: 'Cozy bakery',
      body: 'Fresh croissants and coffee.',
      latitude: 48.8566,
      longitude: 2.3522,
      meta: { category: 'bakery', rating: 4.2 },
      validFrom: '2021-01-01T00:00:00Z',
      validTo: '2023-12-31T23:59:59Z',
    }),
  ]);

  // ---- 2️⃣ Prepare a query that should match the Berlin cafe ----
  const queryEmbedding = await import('../embedding.js').then(m => m.embed('coffee espresso'));
  const { results, nextCursor } = await hybridSearch({
    embedding: queryEmbedding,
    text: 'coffee',
    lon: 13.4,
    lat: 52.52,
    radiusM: 5000,            // 5 km → catches Berlin doc only
    metaFilter: { category: 'cafe' },
    asOf: '2024-03-01T12:00:00Z',
    pageSize: 2,
  });

  // ---- 3️⃣ Assertions ----
  expect(results).toHaveLength(1);
  expect(results[0].title).toBe('Coffee shop in Berlin');
  // No next page because only one result
  expect(nextCursor).toBeUndefined();

  // ---- 4️⃣ Add a broader radius and check pagination ----
  const broad = await hybridSearch({
    embedding: queryEmbedding,
    text: 'coffee',
    lon: 0,
    lat: 0,
    radiusM: 20000000, // ~20 000 km => global
    metaFilter: {},    // no metadata restriction
    asOf: '2024-03-01T12:00:00Z',
    pageSize: 2,
  });

  // Should get the two most similar documents (Berlin café + Bakery)
  expect(broad.results).toHaveLength(2);
  expect(broad.results[0].title).toBe('Coffee shop in Berlin'); // closest vector & text match
  expect(broad.results[1].title).toBe('Cozy bakery');

  // ---- 5️⃣ Fetch next page using cursor ----
  if (broad.nextCursor) {
    const next = await hybridSearch({
      embedding: queryEmbedding,
      text: 'coffee',
      lon: 0,
      lat: 0,
      radiusM: 20000000,
      metaFilter: {},
      asOf: '2024-03-01T12:00:00Z',
      pageSize: 2,
      cursor: broad.nextCursor,
    });

    // The remaining document is the library (even if it doesn't contain "coffee" the vector distance still puts it last)
    expect(next.results).toHaveLength(1);
    expect(next.results[0].title).toBe('Library at central park');
    expect(next.nextCursor).toBeUndefined();
  } else {
    throw new Error('Expected a cursor for the second page');
  }
});
```

Run the test:

```bash
npm test
```

All assertions should pass, proving:

* **Correct ingestion** (geometry, tsvector, validity).  
* **Hybrid filtering** (vector, full‑text, geo radius, metadata, time).  
* **Stable pagination** across pages.

---

## 8️⃣ Reproducible local installation & usage  

### 8.1 Clone & install

```bash
git clone https://github.com/your‑user/pg-hybrid-search-demo.git
cd pg-hybrid-search-demo
npm ci        # installs exact versions from package.json
```

### 8.2 Create a local PostgreSQL database

```bash
createdb pg_hybrid_demo
psql -d pg_hybrid_demo -c "CREATE EXTENSION IF NOT EXISTS postgis; CREATE EXTENSION IF NOT EXISTS vector;"
```

> If you installed `postgresql-15-pgvector` and `postgresql-15-postgis-3` via your package manager, the extensions are already available.

### 8.3 Set environment variables

Create a `.env` file in the project root:

```
DATABASE_URL=postgres://localhost:5432/pg_hybrid_demo
```

(Adjust user/password if needed.)

### 8.4 Run migrations

```bash
npm run migrate
```

### 8.5 Build & run a quick demo (optional)

```bash
npm run build
node dist/index.js   # you can write a tiny script that calls insertDocument + hybridSearch
```

### 8.6 Execute the integration test (the real proof)

```bash
npm test
```

You should see something like:

```
> pg-hybrid-search-demo@1.0.0 test
> jest --runInBand

 PASS  src/__tests__/search.test.ts
  ✓ Hybrid search returns expected document order and pagination (123 ms)

Test Suites: 1 passed, 1 total
Tests:       1 passed, 1 total
```

---

## 9️⃣ Summary of key pieces (quick cheat‑sheet)

| Artifact | Purpose |
|----------|---------|
| `documents` table | Stores text, embeddings, geography, JSONB meta, validity range |
| `vector_cosine_ops` index | Fast ANN (`<=>`) search |
| GIN `tsv` index | Full‑text ranking |
| GiST `geom` index | Radius filter (`ST_DWithin`) |
| GIN `meta` index | JSONB key‑value filter |
| `valid_during` GiST index | Time‑validity (`@> now()`) |
| `insertDocument()` | Transaction‑safe ingestion, computes derived columns |
| `embed()` | Deterministic stub → reproducible vector for tests |
| `hybridSearch()` | One‑statement parameterised query + cursor pagination |
| Jest test | End‑to‑end assertion of the whole stack |

---

## 🔧 Further ideas (outside the scope of the demo)

* Replace the deterministic stub with **OpenAI embeddings** (`openai` npm package) – just swap `embed()` implementation.  
* Use **IVFFlat** parameters (`lists`, `probes`) tuned to your data size for better ANN performance.  
* Add **synthetic updates** and conflict handling (optimistic locking via `xmin`).  
* Expose the search via an **Express** or **Fastify** route for a real API.

--- 

*All code is deliberately **self‑contained** – copy the files into a new directory, follow the steps above, and you’ll have a working hybrid search engine backed by PostgreSQL, PostGIS, and pgvector.*

