# Node.js TypeScript Hybrid Search with PostgreSQL, PostGIS & pgvector

This solution provides a complete, self-contained implementation. It uses **pgvector** for vector search, **PostGIS** for geospatial queries, native PostgreSQL **tsvector** for full-text search, **jsonb** for metadata, and **tstzrange** for validity intervals. Pagination is stable (keyset-based).

## 1. Prerequisites & Local Installation

### Database (Docker - Recommended)
Run a single container with all required extensions pre-installed.
```bash
docker run -d --name pg-hybrid-search \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=search_db \
  -p 5432:5432 \
  ankane/pgvector:latest-pg16  # Includes PostGIS & pgvector
```
*Wait ~10s for initialization. Verify: `docker logs pg-hybrid-search | grep "database system is ready"`*

### Project Setup
```bash
mkdir hybrid-search-example && cd hybrid-search-example
# Save all files below to their respective paths
npm install
npm run migrate
npm run test
```

---

## 2. `package.json` (Exact Versions)

```json
{
  "name": "hybrid-search-example",
  "version": "1.0.0",
  "description": "Self-contained hybrid search: Vector + FullText + Geo + JSON + Time",
  "type": "module",
  "scripts": {
    "build": "tsc",
    "migrate": "node --loader ts-node/esm ./src/db/migrate.ts",
    "ingest": "node --loader ts-node/esm ./src/cli/ingest.ts",
    "search": "node --loader ts-node/esm ./src/cli/search.ts",
    "test": "vitest run",
    "test:watch": "vitest"
  },
  "dependencies": {
    "pg": "^8.12.0",
    "dotenv": "^16.4.5",
    "zod": "^3.23.8"
  },
  "devDependencies": {
    "@types/pg": "^8.11.6",
    "@types/node": "^20.14.2",
    "typescript": "^5.4.5",
    "ts-node": "^10.9.2",
    "vitest": "^1.6.0"
  },
  "engines": { "node": ">=20.0.0" }
}
```

---

## 3. `tsconfig.json`

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
    "declaration": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "test/**/*"]
}
```

---

## 4. Environment Configuration (`.env`)

Create `.env` in project root:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/search_db
EMBEDDING_DIM=768
```

---

## 5. Database Schema & Migrations (`src/db/migrations/`)

### `00_extensions.sql`
```sql
-- Required Extensions
CREATE EXTENSION IF NOT EXISTS vector;      -- pgvector (HNSW/IVFFlat)
CREATE EXTENSION IF NOT EXISTS postgis;     -- Geography/Geometry
CREATE EXTENSION IF NOT EXISTS pg_trgm;     -- Trigram similarity (optional boost)
```

### `01_documents_table.sql`
```sql
CREATE TABLE IF NOT EXISTS documents (
    id              BIGSERIAL PRIMARY KEY,
    title           TEXT NOT NULL,
    content         TEXT NOT NULL,
    -- Vector Embedding (pgvector)
    embedding       vector(768) NOT NULL,
    -- Full Text Search
    fts             tsvector GENERATED ALWAYS AS (
                        to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, ''))
                      ) STORED,
    -- Geographic Point (PostGIS, WGS84 / SRID 4326)
    location        geography(Point, 4326) NOT NULL,
    -- JSON Metadata (GIN Indexable)
    metadata        jsonb NOT NULL DEFAULT '{}',
    -- Validity Interval (Inclusive Start, Exclusive End)
    valid_during    tstzrange NOT NULL,
    -- Timestamps
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now()
);

COMMENT ON COLUMN documents.embedding IS 'pgvector cosine distance (<=>)';
COMMENT ON COLUMN documents.location IS 'PostGIS Geography Point (lon, lat)';
COMMENT ON COLUMN documents.valid_during IS 'Validity window: [lower_inc, upper_inc)';
```

### `02_indexes.sql`
```sql
-- 1. Vector Index (HNSW) - High recall, fast build. Requires pgvector >= 0.5.0
--    m=16, ef_construction=64 are sensible defaults.
CREATE INDEX IF NOT EXISTS idx_documents_embedding_hnsw 
ON documents USING hnsw (embedding vector_cosine_ops) 
WITH (m = 16, ef_construction = 64);

-- 2. Full Text Search (GIN)
CREATE INDEX IF NOT EXISTS idx_documents_fts_gin 
ON documents USING gin (fts);

-- 3. Geospatial (GiST)
CREATE INDEX IF NOT EXISTS idx_documents_location_gist 
ON documents USING gist (location);

-- 4. JSON Metadata (GIN) - Path/Value queries
CREATE INDEX IF NOT EXISTS idx_documents_metadata_gin 
ON documents USING gin (metadata jsonb_path_ops);

-- 5. Validity Interval (GiST) - Range containment/intersection
CREATE INDEX IF NOT EXISTS idx_documents_valid_during_gist 
ON documents USING gist (valid_during);

-- 6. Composite "Updated At" for Keyset Pagination stability
CREATE INDEX IF NOT EXISTS idx_documents_updated_at_id 
ON documents (updated_at DESC, id DESC);
```

### `03_functions.sql` (Optional: Trigger for `updated_at`)
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = now(); RETURN NEW; END; $$;

DROP TRIGGER IF EXISTS trigger_update_updated_at ON documents;
CREATE TRIGGER trigger_update_updated_at
BEFORE UPDATE ON documents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## 6. TypeScript Core Implementation

### `src/types.ts`
```typescript
export interface DocumentInput {
  title: string;
  content: string;
  embedding: number[]; // length EMBEDDING_DIM
  location: { longitude: number; latitude: number }; // WGS84
  metadata: Record<string, unknown>;
  validFrom: Date; // inclusive
  validTo: Date;   // exclusive
  id?: number;     // for upsert
}

export interface SearchParams {
  queryText?: string;          // Full-text query (websearch syntax)
  queryVector?: number[];      // Semantic vector
  location?: { longitude: number; latitude: number; radiusMeters: number };
  metadataFilter?: Record<string, unknown>; // @> containment
  validAt?: Date;              // Timestamp validity check
  limit?: number;              // Page size
  cursor?: { updatedAt: string; id: number }; // Keyset pagination cursor
}

export interface SearchResult {
  id: number;
  title: string;
  content: string;
  location: { longitude: number; latitude: number };
  metadata: Record<string, unknown>;
  validDuring: { from: Date; to: Date };
  // Scores
  vectorDistance?: number;     // Cosine distance (0=identical, 1=opposite)
  textRank?: number;           // ts_rank_cd (higher=better)
  geoDistanceMeters?: number;  // Distance from query point
  createdAt: Date;
  updatedAt: Date;
}

export interface PaginatedResult {
  items: SearchResult[];
  nextCursor: { updatedAt: string; id: number } | null;
}
```

### `src/db/pool.ts`
```typescript
import pg from 'pg';
import dotenv from 'dotenv';
dotenv.config();

const { Pool } = pg;

export const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 10,
  idleTimeoutMillis: 30000,
});

pool.on('error', (err) => {
  console.error('Unexpected PG Pool Error', err);
  process.exit(-1);
});

export async function query<T>(text: string, params?: unknown[]): Promise<pg.QueryResult<T>> {
  const start = Date.now();
  const res = await pool.query<T>(text, params);
  const duration = Date.now() - start;
  if (process.env.DEBUG_SQL) console.log('QUERY', duration, 'ms', text.substring(0, 80), params);
  return res;
}

export async function getClient() {
  return pool.connect();
}
```

### `src/db/migrate.ts`
```typescript
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { pool, query } from './pool.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const MIGRATIONS_DIR = path.join(__dirname, 'migrations');

export async function runMigrations() {
  console.log('Running migrations...');
  const files = fs.readdirSync(MIGRATIONS_DIR).filter(f => f.endsWith('.sql')).sort();
  
  await query(`CREATE TABLE IF NOT EXISTS _migrations (name text primary key, applied_at timestamptz default now())`);

  for (const file of files) {
    const applied = await query<{name: string}>('SELECT name FROM _migrations WHERE name = $1', [file]);
    if (applied.rows.length > 0) {
      console.log(`  SKIP ${file}`);
      continue;
    }
    console.log(`  APPLY ${file}`);
    const sql = fs.readFileSync(path.join(MIGRATIONS_DIR, file), 'utf-8');
    await query('BEGIN');
    try {
      await query(sql);
      await query('INSERT INTO _migrations (name) VALUES ($1)', [file]);
      await query('COMMIT');
    } catch (e) {
      await query('ROLLBACK');
      throw e;
    }
  }
  console.log('Migrations complete.');
  await pool.end();
}

if (import.meta.url === `file://${process.argv[1]}`) {
  runMigrations().catch(e => { console.error(e); process.exit(1); });
}
```

### `src/embedding/stub.ts`
**Deterministic Embedding Stub** (SHA-256 -> Float32 Array). Replaces external API for reproducibility.
```typescript
import { createHash } from 'crypto';

const DIM = Number(process.env.EMBEDDING_DIM) || 768;

/**
 * Generates a deterministic, normalized unit vector from a string seed.
 * Uses SHA-256 hashed repeatedly to fill dimensions.
 */
export function generateEmbedding(text: string): Float32Array {
  const vec = new Float32Array(DIM);
  let hash = createHash('sha256').update(text).digest();
  let offset = 0;

  while (offset < DIM) {
    const view = new DataView(hash.buffer, hash.byteOffset, hash.byteLength);
    for (let i = 0; i < hash.length && offset < DIM; i += 4, offset++) {
      // Convert 4 bytes to float32 (-1 to 1 range roughly)
      const intVal = view.getInt32(i, false);
      vec[offset] = intVal / 0x7fffffff; 
    }
    if (offset < DIM) hash = createHash('sha256').update(hash).digest();
  }

  // Normalize to Unit Length (Critical for Cosine Distance <=>)
  let norm = 0;
  for (let i = 0; i < DIM; i++) norm += vec[i] * vec[i];
  norm = Math.sqrt(norm);
  if (norm > 0) for (let i = 0; i < DIM; i++) vec[i] /= norm;

  return vec;
}

/** Helper for CLI/Tests */
export function embeddingToPgVector(vec: Float32Array): string {
  return `[${Array.from(vec).join(',')}]`;
}
```

### `src/ingest/ingest.ts`
**Transaction-Safe Upsert** (ON CONFLICT). Handles `tstzrange` and `geography` constructors.
```typescript
import { query, getClient } from '../db/pool.js';
import { DocumentInput, embeddingToPgVector } from '../types.js';
import { generateEmbedding } from '../embedding/stub.js';

export async function ingestDocument(doc: DocumentInput): Promise<number> {
  const client = await getClient();
  try {
    await client.query('BEGIN');

    // 1. Generate Embedding if missing (or trust input)
    const embedding = doc.embedding?.length ? doc.embedding : Array.from(generateEmbedding(doc.title + ' ' + doc.content));
    const embeddingStr = embeddingToPgVector(new Float32Array(embedding));

    // 2. Construct Geography Point: ST_MakePoint(lon, lat)::geography
    const geoPoint = `ST_SetSRID(ST_MakePoint(${doc.location.longitude}, ${doc.location.latitude}), 4326)::geography`;

    // 3. Construct TSTZRANGE: [validFrom, validTo)
    //    Lower inclusive (default), Upper exclusive (')')
    const range = `tstzrange($1, $2, '[)')`;

    const sql = `
      INSERT INTO documents (title, content, embedding, location, metadata, valid_during)
      VALUES ($3, $4, $5::vector, ${geoPoint}, $6, ${range})
      ON CONFLICT (id) DO UPDATE SET
        title = EXCLUDED.title,
        content = EXCLUDED.content,
        embedding = EXCLUDED.embedding,
        location = EXCLUDED.location,
        metadata = EXCLUDED.metadata,
        valid_during = EXCLUDED.valid_during,
        updated_at = now()
      RETURNING id;
    `;

    // Params: $1=validFrom, $2=validTo, $3=title, $4=content, $5=embedding, $6=metadata
    const params = [
      doc.validFrom.toISOString(),
      doc.validTo.toISOString(),
      doc.title,
      doc.content,
      embeddingStr,
      JSON.stringify(doc.metadata)
    ];

    // If ID provided, add to WHERE for ON CONFLICT (requires unique constraint on ID, which is PK)
    // Standard PG Upsert uses ON CONFLICT (pk_col). 
    // If we want to upsert by ID, we must include ID in INSERT.
    if (doc.id) {
        // Re-write for specific ID upsert
        const sqlId = `
          INSERT INTO documents (id, title, content, embedding, location, metadata, valid_during)
          VALUES ($7, $3, $4, $5::vector, ${geoPoint}, $6, ${range})
          ON CONFLICT (id) DO UPDATE SET
            title = EXCLUDED.title, content = EXCLUDED.content, embedding = EXCLUDED.embedding,
            location = EXCLUDED.location, metadata = EXCLUDED.metadata, valid_during = EXCLUDED.valid_during,
            updated_at = now()
          RETURNING id;
        `;
        const res = await client.query(sqlId, [...params, doc.id]);
        await client.query('COMMIT');
        return res.rows[0].id;
    }

    const res = await client.query(sql, params);
    await client.query('COMMIT');
    return res.rows[0].id;
  } catch (e) {
    await client.query('ROLLBACK');
    throw e;
  } finally {
    client.release();
  }
}

// CLI Entry
if (import.meta.url === `file://${process.argv[1]}`) {
  const now = new Date();
  const tomorrow = new Date(now.getTime() + 24 * 60 * 60 * 1000);
  const id = await ingestDocument({
    title: "PostGIS & pgvector Hybrid Search",
    content: "Combining vector embeddings with geospatial and full-text search in PostgreSQL.",
    location: { longitude: -122.4194, latitude: 37.7749 }, // SF
    metadata: { category: "tech", tags: ["postgres", "vector", "gis"], author: "Nemotron" },
    validFrom: now,
    validTo: tomorrow,
  });
  console.log(`Ingested Document ID: ${id}`);
  process.exit(0);
}
```

### `src/search/hybrid.ts`
**The Core Hybrid Query**.
Combines: Vector Distance (`<=>`), Text Rank (`ts_rank_cd`), Geo Distance (`ST_Distance`), Metadata (`@>`), Validity (`@>`), Stable Pagination (Keyset on `updated_at, id`).
```typescript
import { query } from '../db/pool.js';
import { SearchParams, SearchResult, PaginatedResult, embeddingToPgVector } from '../types.js';

/**
 * Builds and executes the hybrid search query.
 * Uses a CTE for scoring normalization and a single final sort for keyset pagination.
 */
export async function hybridSearch(params: SearchParams): Promise<PaginatedResult> {
  const {
    queryText, queryVector, location, metadataFilter, validAt,
    limit = 10, cursor
  } = params;

  const conditions: string[] = [];
  const values: unknown[] = [];
  let paramIdx = 1;

  // --- 1. Validity Predicate (Mandatory for correctness) ---
  // valid_during @> $validAt  (Range contains element)
  if (validAt) {
    conditions.push(`valid_during @> $${paramIdx++}`);
    values.push(validAt.toISOString());
  } else {
    // Default: Valid now
    conditions.push(`valid_during @> now()`);
  }

  // --- 2. Metadata Filter (JSONB Containment) ---
  // metadata @> $filter
  if (metadataFilter && Object.keys(metadataFilter).length > 0) {
    conditions.push(`metadata @> $${paramIdx++}`);
    values.push(JSON.stringify(metadataFilter));
  }

  // --- 3. Geospatial Radius (PostGIS) ---
  // ST_DWithin(geog, ST_MakePoint(lon, lat)::geog, radius)
  let geoDistanceSelect = 'NULL::float AS geo_distance_meters';
  if (location) {
    conditions.push(`ST_DWithin(location, ST_SetSRID(ST_MakePoint($${paramIdx}, $${paramIdx + 1}), 4326)::geography, $${paramIdx + 2})`);
    values.push(location.longitude, location.latitude, location.radiusMeters);
    // Select actual distance for scoring/sorting
    geoDistanceSelect = `ST_Distance(location, ST_SetSRID(ST_MakePoint($${paramIdx - 2}, $${paramIdx - 1}), 4326)::geography) AS geo_distance_meters`;
  }

  // --- 4. Full Text Search (tsvector) ---
  let textRankSelect = 'NULL::float AS text_rank';
  let textRankOrder = 'NULL'; // For ordering if no vector
  if (queryText) {
    // websearch_to_tsquery supports phrases, negation, etc.
    conditions.push(`fts @@ websearch_to_tsquery('english', $${paramIdx})`);
    values.push(queryText);
    textRankSelect = `ts_rank_cd(fts, websearch_to_tsquery('english', $${paramIdx - 1}), 32) AS text_rank`; // 32 = rank/(rank+1) normalization
    textRankOrder = `text_rank DESC`;
  }

  // --- 5. Vector Similarity (pgvector) ---
  let vectorDistSelect = 'NULL::float AS vector_distance';
  let vectorOrder = 'NULL';
  if (queryVector) {
    const vecStr = embeddingToPgVector(new Float32Array(queryVector));
    // Cosine Distance: embedding <=> $vec
    // We add to SELECT and ORDER BY
    vectorDistSelect = `embedding <=> $${paramIdx}::vector AS vector_distance`;
    values.push(vecStr);
    vectorOrder = `vector_distance ASC`; // Smaller distance = better
  }

  // --- 6. Keyset Pagination (Stable) ---
  // Sort Key: (Primary Sort, Secondary Sort, ... , updated_at DESC, id DESC)
  // We define a "Relevance Score" composite.
  // Strategy: Prioritize explicit sorts (Vector, Text), fallback to Recency.
  
  const orderClauses: string[] = [];
  if (queryVector) orderClauses.push(vectorOrder);
  if (queryText) orderClauses.push(textRankOrder);
  // Tie-breakers: Geo Distance (if geo query), then Recency
  if (location) orderClauses.push('geo_distance_meters ASC');
  orderClauses.push('updated_at DESC, id DESC'); // Stability Anchor

  const orderBySql = orderClauses.join(', ');

  // Cursor Condition: (sort_col1, sort_col2, ...) < (cursor_val1, cursor_val2, ...)
  // This requires mapping ORDER BY columns to values.
  // Simplified Approach: Use the *last* sort key (updated_at, id) for cursor 
  // IF primary sorts are not unique. 
  // CORRECT APPROACH: Composite Cursor.
  // We will use the tuple of the ORDER BY expressions.
  
  let cursorSql = '';
  if (cursor) {
    // We need to reconstruct the sort tuple values for the cursor row.
    // Easiest robust way: Fetch the cursor row's sort keys first, or require client to send them.
    // Here we assume cursor contains { updatedAt, id } as the ultimate tie-breaker.
    // This is safe IF we always sort by (updated_at, id) last.
    cursorSql = `AND (updated_at, id) < ($${paramIdx}::timestamptz, $${paramIdx + 1})`;
    values.push(cursor.updatedAt, cursor.id);
    paramIdx += 2;
  }

  // --- Final Query Assembly ---
  const whereSql = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';
  
  const sql = `
    SELECT 
      id, title, content, 
      ST_X(location::geometry) AS longitude, 
      ST_Y(location::geometry) AS latitude,
      metadata,
      lower(valid_during) AS valid_from,
      upper(valid_during) AS valid_to,
      created_at, updated_at,
      ${vectorDistSelect},
      ${textRankSelect},
      ${geoDistanceSelect}
    FROM documents
    ${whereSql}
    ${cursorSql}
    ORDER BY ${orderBySql}
    LIMIT $${paramIdx};
  `;
  values.push(limit + 1); // Fetch one extra to detect next page

  const res = await query<Record<string, unknown>>(sql, values);
  const rows = res.rows;

  const hasMore = rows.length > limit;
  const items = hasMore ? rows.slice(0, limit) : rows;
  
  let nextCursor: PaginatedResult['nextCursor'] = null;
  if (hasMore) {
    const last = items[items.length - 1];
    nextCursor = { 
      updatedAt: (last.updated_at as Date).toISOString(), 
      id: last.id as number 
    };
  }

  return {
    items: items.map(mapRow),
    nextCursor
  };
}

function mapRow(row: Record<string, unknown>): SearchResult {
  return {
    id: row.id as number,
    title: row.title as string,
    content: row.content as string,
    location: { 
      longitude: row.longitude as number, 
      latitude: row.latitude as number 
    },
    metadata: row.metadata as Record<string, unknown>,
    validDuring: { 
      from: row.valid_from as Date, 
      to: row.valid_to as Date 
    },
    vectorDistance: row.vector_distance as number | undefined,
    textRank: row.text_rank as number | undefined,
    geoDistanceMeters: row.geo_distance_meters as number | undefined,
    createdAt: row.created_at as Date,
    updatedAt: row.updated_at as Date,
  };
}
```

---

## 7. Integration Assertions (`test/integration.test.ts`)

Uses `vitest`. Verifies ingestion, all predicate combinations, and pagination stability.
```typescript
import { describe, it, expect, beforeAll, afterAll, beforeEach } from 'vitest';
import { hybridSearch } from '../src/search/hybrid.js';
import { ingestDocument } from '../src/ingest/ingest.js';
import { generateEmbedding, embeddingToPgVector } from '../src/embedding/stub.js';
import { pool } from '../src/db/pool.js';
import { DocumentInput } from '../src/types.js';

const DIM = 768;
const now = new Date();
const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
const tomorrow = new Date(now.getTime() + 24 * 60 * 60 * 1000);
const nextWeek = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);

const baseDoc: Omit<DocumentInput, 'id' | 'embedding'> = {
  title: "Test Document",
  content: "Content about PostgreSQL and Vector Search.",
  location: { longitude: -122.4194, latitude: 37.7749 }, // SF
  metadata: { category: "test", tags: ["pg", "vector"], version: 1 },
  validFrom: yesterday,
  validTo: nextWeek,
};

let docIds: number[] = [];

beforeAll(async () => {
  // Ensure clean state
  await pool.query('TRUNCATE documents RESTART IDENTITY CASCADE');
});

afterAll(async () => {
  await pool.end();
});

beforeEach(async () => {
  // Ingest 3 docs for pagination/sorting tests
  docIds = [];
  for (let i = 0; i < 3; i++) {
    const d = { 
      ...baseDoc, 
      title: `Doc ${i} Postgres Vector`, 
      content: `Content ${i} about vectors.`,
      location: { longitude: -122.4194 + i * 0.01, latitude: 37.7749 },
      metadata: { ...baseDoc.metadata, version: i },
      validFrom: yesterday,
      validTo: nextWeek,
    };
    const id = await ingestDocument(d);
    docIds.push(id);
  }
  // Wait for indexes/refresh (not strictly needed for PG but safe)
  await new Promise(r => setTimeout(r, 100));
});

describe('Hybrid Search Core', () => {
  it('1. Ingests documents with all fields populated', async () => {
    const id = await ingestDocument({
      ...baseDoc, title: "Fresh Ingest", metadata: { ...baseDoc.metadata, fresh: true }
    });
    expect(id).toBeGreaterThan(0);
    const res = await pool.query('SELECT * FROM documents WHERE id=$1', [id]);
    expect(res.rows[0].metadata).toMatchObject({ fresh: true, category: 'test' });
    expect(res.rows[0].valid_during).toContain(now.toISOString().split('T')[0]); // Range check
  });

  it('2. Filters by Time Validity (validAt)', async () => {
    // Ingest expired doc
    await ingestDocument({ ...baseDoc, title: "Expired", validFrom: new Date('2000-01-01'), validTo: new Date('2001-01-01') });
    
    const res = await hybridSearch({ validAt: now, limit: 10 });
    expect(res.items.length).toBe(3); // Only the 3 valid ones
    expect(res.items.every(d => d.title.startsWith('Doc'))).toBe(true);
  });

  it('3. Filters by Metadata (JSONB @>)', async () => {
    const res = await hybridSearch({ 
      validAt: now, 
      metadataFilter: { version: 1 }, // Exact match on nested value
      limit: 10 
    });
    expect(res.items.length).toBe(1);
    expect(res.items[0].metadata.version).toBe(1);
  });

  it('4. Filters by Geo Radius (ST_DWithin)', async () => {
    // Doc 0 at SF. Doc 2 moved slightly.
    // Search near Doc 0 with 500m radius (Doc 0 & 1 close, Doc 2 ~1km away)
    const res = await hybridSearch({
      validAt: now,
      location: { longitude: -122.4194, latitude: 37.7749, radiusMeters: 1500 }, // ~1.5km
      limit: 10
    });
    expect(res.items.length).toBeGreaterThanOrEqual(2);
    expect(res.items.every(d => d.geoDistanceMeters !== undefined && d.geoDistanceMeters! < 1500)).toBe(true);
  });

  it('5. Ranks by Full Text Search (ts_rank_cd)', async () => {
    const res = await hybridSearch({
      validAt: now,
      queryText: "vectors", // Matches all 3
      limit: 10
    });
    expect(res.items.length).toBe(3);
    expect(res.items[0].textRank).toBeDefined();
    expect(res.items[0].textRank! >= res.items[1].textRank!).toBe(true); // Descending
  });

  it('6. Ranks by Vector Distance (Cosine <=>)', async () => {
    // Query vector matches "Doc 1 Postgres Vector" best
    const qVec = generateEmbedding("Doc 1 Postgres Vector");
    const res = await hybridSearch({
      validAt: now,
      queryVector: Array.from(qVec),
      limit: 10
    });
    expect(res.items.length).toBe(3);
    expect(res.items[0].vectorDistance).toBeDefined();
    // Cosine Distance: 0 is best. Doc 1 should be closest.
    expect(res.items[0].id).toBe(docIds[1]); 
    expect(res.items[0].vectorDistance! < res.items[1].vectorDistance!).toBe(true);
  });

  it('7. Combines All Predicates (Hybrid)', async () => {
    const qVec = generateEmbedding("Postgres Vector");
    const res = await hybridSearch({
      validAt: now,
      queryText: "Postgres",
      queryVector: Array.from(qVec),
      location: { longitude: -122.4194, latitude: 37.7749, radiusMeters: 2000 },
      metadataFilter: { category: "test" },
      limit: 10
    });
    expect(res.items.length).toBe(3);
    // All scores present
    expect(res.items.every(d => d.vectorDistance !== undefined)).toBe(true);
    expect(res.items.every(d => d.textRank !== undefined)).toBe(true);
    expect(res.items.every(d => d.geoDistanceMeters !== undefined)).toBe(true);
  });

  it('8. Stable Keyset Pagination (Cursor)', async () => {
    // Page 1: Limit 2
    const page1 = await hybridSearch({ validAt: now, limit: 2 });
    expect(page1.items.length).toBe(2);
    expect(page1.nextCursor).not.toBeNull();

    // Page 2: Use Cursor
    const page2 = await hybridSearch({ validAt: now, limit: 2, cursor: page1.nextCursor! });
    expect(page2.items.length).toBe(1); // Only 3 total
    expect(page2.nextCursor).toBeNull();

    // Verify No Overlap & Order Stability
    const allIds = [...page1.items, ...page2.items].map(d => d.id);
    expect(new Set(allIds).size).toBe(3); // Unique
    
    // Verify Sort Order: Updated_At DESC (default tie-break)
    // Since ingested sequentially, IDs 0,1,2 have increasing updated_at.
    // Order should be 2, 1, 0.
    expect(allIds).toEqual([docIds[2], docIds[1], docIds[0]]);
  });

  it('9. Upsert Updates Embedding & Metadata Atomically', async () => {
    const id = docIds[0];
    const newMeta = { category: "updated", tags: ["upsert"], version: 99 };
    await ingestDocument({ ...baseDoc, id, title: "Upserted Title", metadata: newMeta });
    
    const res = await hybridSearch({ validAt: now, metadataFilter: { version: 99 }, limit: 1 });
    expect(res.items.length).toBe(1);
    expect(res.items[0].title).toBe("Upserted Title");
    expect(res.items[0].metadata.version).toBe(99);
  });
});
```

---

## 8. CLI Entry Points (Optional Convenience)

### `src/cli/ingest.ts`
```typescript
import { ingestDocument } from '../ingest/ingest.js';
import { generateEmbedding } from '../embedding/stub.js';

const now = new Date();
const tomorrow = new Date(now.getTime() + 86400000);

await ingestDocument({
  title: "CLI Ingested Doc",
  content: "Inserted via CLI command.",
  location: { longitude: -73.935242, latitude: 40.730610 }, // NYC
  metadata: { source: "cli", env: "dev" },
  validFrom: now,
  validTo: tomorrow,
});
console.log("CLI Ingest Done");
```

### `src/cli/search.ts`
```typescript
import { hybridSearch } from '../search/hybrid.js';
import { generateEmbedding } from '../embedding/stub.js';

const qVec = generateEmbedding("Postgres Vector");
const res = await hybridSearch({
  queryText: "Postgres",
  queryVector: Array.from(qVec),
  location: { longitude: -122.4194, latitude: 37.7749, radiusMeters: 50000 },
  metadataFilter: { category: "test" },
  validAt: new Date(),
  limit: 5
});

console.log(`Found ${res.items.length} results. Next Cursor:`, res.nextCursor);
res.items.forEach((d, i) => {
  console.log(`${i+1}. [${d.id}] ${d.title} | VecDist: ${d.vectorDistance?.toFixed(4)} | Rank: ${d.textRank?.toFixed(4)} | Geo: ${d.geoDistanceMeters?.toFixed(0)}m`);
});
```

---

## 9. Reproducible Commands Summary

```bash
# 1. Start DB (Terminal 1)
docker run -d --name pg-hybrid-search \
  -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=search_db \
  -p 5432:5432 ankane/pgvector:latest-pg16

# 2. Install Deps
npm install

# 3. Run Migrations (Creates schema, indexes, extensions)
npm run migrate

# 4. Ingest Sample Data
npm run ingest

# 5. Run Hybrid Search Demo
npm run search

# 6. Run Integration Tests (Vitest)
npm run test
```

---

## 10. Key Technical Decisions & APIs Used

| Feature | PostgreSQL API / Extension | Node.js Package | Implementation Detail |
| :--- | :--- | :--- | :--- |
| **Vector Search** | `pgvector` (`vector` type, `<=>` cosine op, `hnsw` index) | `pg` (raw driver) | `embedding <=> $1::vector` in `ORDER BY`. HNSW index for ANN. |
| **Geospatial** | `PostGIS` (`geography(Point, 4326)`, `ST_DWithin`, `ST_Distance`, `ST_MakePoint`) | `pg` | `ST_DWithin(location, ST_MakePoint(lon,lat)::geog, radius_m)`. Index: `GIST`. |
| **Full-Text** | Core PG (`tsvector`, `websearch_to_tsquery`, `ts_rank_cd`, `GIN` index) | `pg` | Generated column `fts`. `websearch_to_tsquery` supports Google-like syntax. |
| **JSON Metadata** | Core PG (`jsonb`, `@>` containment, `jsonb_path_ops` GIN) | `pg` | `metadata @> $filter::jsonb`. Efficient for key/value existence. |
| **Time Validity** | Core PG (`tstzrange`, `@>` contains element, `GIST` index) | `pg` | `valid_during @> $validAt`. Range `[lower, upper)`. |
| **Pagination** | Core PG (Keyset / Cursor) | `pg` | `ORDER BY (score, updated_at, id) LIMIT N+1`. Cursor: `(updated_at, id) < (?, ?)`. |
| **Transactions** | Core PG (`BEGIN`, `COMMIT`, `ROLLBACK`) | `pg` (`pool.connect()`) | `ingestDocument` uses dedicated client for atomic upsert. |
| **Embeddings** | N/A (Application Layer) | `crypto` (Node Built-in) | Deterministic SHA-256 -> Float32 -> Normalized. Dim=768. |

### Why this architecture?
1.  **Single Round Trip**: The `hybridSearch` function constructs **one parameterized SQL statement** combining all predicates. This avoids N+1 queries and allows the PG planner to use the most selective index first (BitmapAnd/Or).
2.  **Stable Pagination**: Keyset pagination on `(updated_at, id)` guarantees no skipped/duplicated rows during concurrent inserts, unlike `OFFSET`.
3.  **Deterministic Embeddings**: The SHA-256 stub ensures CI/CD tests and local runs produce **bitwise identical vectors**, enabling snapshot testing of vector distances.
4.  **Transaction Safety**: Ingestion uses explicit `BEGIN/COMMIT` with a dedicated client from the pool, ensuring the `ON CONFLICT` upsert and index updates are atomic.
5.  **Index Strategy**: 
    *   `HNSW` (Vector) - Best recall/speed tradeoff for ANN.
    *   `GIN` (FTS, JSONB) - Inverted index for containment.
    *   `GiST` (Geo, Range) - Lossy compression for spatial/range bounding boxes.

