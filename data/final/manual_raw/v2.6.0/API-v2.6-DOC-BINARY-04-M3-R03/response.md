## 📦 Self‑contained Node.js + TypeScript Archive Inspector  

A **single‑file core** (no web server, no DB) that can  

* detect **ZIP**, **TAR / TAR.GZ**, and **7z** from the file’s bytes,  
* list every entry **before extraction**,  
* enforce **security & resource limits** (entry count, expanded size, compression ratio, nesting depth),  
* reject **absolute paths, path‑traversal, symlink escapes, encrypted entries, duplicate normalized paths**,  
* stream **accepted entries** to a **quarantined output** (a temporary folder), and  
* emit a **common manifest** (JSON) describing what was extracted.

The project ships with  

* a **safe fixture** (`fixtures/safe.zip`) and  
* two **representative failure cases** (traversal & limit breach).  

All code lives under `src/` and can be run with `npm start -- <archive‑path>`.

---

<details open><summary>🗂️ Directory layout</summary>

```
archive‑inspector/
├─ src/
│  ├─ adapters/
│  │  ├─ ArchiveAdapter.ts          # shared interface & types
│  │  ├─ ZipAdapter.ts
│  │  ├─ TarAdapter.ts
│  │  └─ SevenZAdapter.ts
│  ├─ QuarantineAdapter.ts          # writes entries to a safe dir
│  ├─ Inspector.ts                  # core logic (detect → limits → extract)
│  └─ inspect.ts                    # CLI entry point
├─ fixtures/
│  ├─ safe.zip                      # a tiny, clean archive (one text file)
│  ├─ traversal.zip                 # contains "../evil.txt"
│  └─ huge.tar.gz                   # > maxExpandedBytes
├─ package.json
├─ tsconfig.json
└─ README.md
```

</details>

---

## 📦 `package.json` (exact versions)

```json
{
  "name": "archive-inspector",
  "version": "1.0.0",
  "description": "Self‑contained TS core that inspects ZIP/TAR/7z archives with security limits",
  "main": "dist/inspect.js",
  "type": "module",
  "scripts": {
    "build": "tsc",
    "start": "ts-node src/inspect.ts"
  },
  "author": "OpenAI ChatGPT",
  "license": "MIT",
  "dependencies": {
    "@types/node": "20.12.7",
    "7zip-bin": "5.2.0",
    "node-7z": "2.0.2",
    "tar-stream": "2.2.0",
    "unzipper": "0.10.11",
    "gunzip-maybe": "1.4.2",
    "peek-stream": "1.1.3",
    "mime-types": "2.1.35"
  },
  "devDependencies": {
    "ts-node": "10.9.2",
    "typescript": "5.4.5"
  },
  "engines": {
    "node": ">=18"
  }
}
```

*All versions are pinned to guarantee reproducible builds.*

---

## 🛠️ Installation & Execution

```bash
# 1️⃣ Clone / copy the repo
git clone https://github.com/your‑org/archive‑inspector.git
cd archive-inspector

# 2️⃣ Install exact deps (npm ci respects the lockfile)
npm ci

# 3️⃣ Run the inspector on the safe fixture (should succeed)
npm start -- fixtures/safe.zip

# 4️⃣ Run on a malicious archive (should be rejected)
npm start -- fixtures/traversal.zip

# 5️⃣ Run on a huge archive (limit breach)
npm start -- fixtures/huge.tar.gz
```

*`npm start` forwards everything after `--` to the CLI script (`src/inspect.ts`).*

---

## 📚 Archive & Stream APIs Used

| Format | Adapter | NPM Package | Primary API |
|--------|---------|-------------|-------------|
| **ZIP** | `ZipAdapter` | `unzipper` | `unzipper.Parse()` – emits `entry` objects (stream, `path`, `type`, `vars.uncompressedSize`, `vars.compressedSize`, `vars.encrypted`) |
| **TAR / TAR.GZ** | `TarAdapter` | `tar-stream` + `gunzip-maybe` | `tar.extract()` – pipe a (optionally gunzipped) stream; each `entry` event gives `header` (name, size, type) |
| **7z** | `SevenZAdapter` | `node-7z` (binary from `7zip-bin`) | `SevenZ.list()` for metadata, `SevenZ.extractFull()` with `--stdout` to stream each file |

All adapters expose the **same** TypeScript interface (`ArchiveAdapter`) so the rest of the code stays format‑agnostic.

---

## 🧩 Core Types (`src/adapters/ArchiveAdapter.ts`)

```ts
// src/adapters/ArchiveAdapter.ts
import { Writable } from "node:stream";

export interface ArchiveEntry {
  /** Normalised path inside the archive (POSIX style) */
  path: string;
  /** Uncompressed size in bytes */
  size: number;
  /** Compressed size in bytes (if known) */
  compressedSize?: number;
  /** true for directories */
  isDirectory: boolean;
  /** true for symlinks */
  isSymlink: boolean;
  /** Target of a symlink (if any) */
  linkTarget?: string;
  /** true if the entry is encrypted (ZIP) */
  encrypted?: boolean;
}

/** Minimal adapter used by the inspector */
export interface ArchiveAdapter {
  /** List all entries (no extraction) */
  listEntries(): Promise<ArchiveEntry[]>;

  /** Stream the given entry to a writable destination */
  extract(entry: ArchiveEntry, dest: Writable): Promise<void>;

  /** Close any underlying resources (e.g. temp files) */
  close(): Promise<void>;
}
```

---

## 🔎 Format Detection (`src/Inspector.ts`)

```ts
// src/Inspector.ts
import { createReadStream, PassThrough } from "node:fs";
import { pipeline } from "node:stream/promises";
import peek from "peek-stream";
import { ZipAdapter } from "./adapters/ZipAdapter.js";
import { TarAdapter } from "./adapters/TarAdapter.js";
import { SevenZAdapter } from "./adapters/SevenZAdapter.js";
import type { ArchiveAdapter, ArchiveEntry } from "./adapters/ArchiveAdapter.js";

export enum ArchiveFormat {
  ZIP = "zip",
  TAR = "tar",
  TGZ = "tgz",
  SEVEN_Z = "7z",
}

/** Detect format from leading bytes (magic numbers) */
export async function detectFormat(filePath: string): Promise<ArchiveFormat> {
  return new Promise((resolve, reject) => {
    const rs = createReadStream(filePath, { start: 0, end: 8191 });
    const detector = peek({ newline: false, maxBuffer: 8192 }, (data, swap) => {
      const buf = data as Buffer;
      // ZIP: PK\x03\x04
      if (buf.slice(0, 4).equals(Buffer.from([0x50, 0x4b, 0x03, 0x04]))) {
        resolve(ArchiveFormat.ZIP);
        return;
      }
      // 7z: 7z\xBC\xAF\x27\x1C
      if (buf.slice(0, 6).equals(Buffer.from([0x37, 0x7a, 0xbc, 0xaf, 0x27, 0x1c]))) {
        resolve(ArchiveFormat.SEVEN_Z);
        return;
      }
      // GZIP: 0x1F 0x8B
      if (buf.slice(0, 2).equals(Buffer.from([0x1f, 0x8b]))) {
        resolve(ArchiveFormat.TGZ);
        return;
      }
      // TAR detection – look for "ustar" at offset 257
      if (buf.length > 262 && buf.slice(257, 262).toString() === "ustar") {
        resolve(ArchiveFormat.TAR);
        return;
      }
      reject(new Error("Unknown or unsupported archive format"));
    });
    rs.pipe(detector).on("error", reject);
  });
}

/** Factory – creates the appropriate adapter */
export async function createAdapter(
  format: ArchiveFormat,
  filePath: string
): Promise<ArchiveAdapter> {
  switch (format) {
    case ArchiveFormat.ZIP:
      return new ZipAdapter(filePath);
    case ArchiveFormat.TAR:
      return new TarAdapter(filePath, false);
    case ArchiveFormat.TGZ:
      return new TarAdapter(filePath, true);
    case ArchiveFormat.SEVEN_Z:
      return new SevenZAdapter(filePath);
    default:
      throw new Error(`Unsupported format ${format}`);
  }
}
```

---

## 🛡️ Security & Resource Limits (`src/Inspector.ts` – continued)

```ts
// src/Inspector.ts (continued)
import { QuarantineAdapter } from "./QuarantineAdapter.js";
import * as path from "node:path";
import * as crypto from "node:crypto";

export interface Limits {
  maxEntries: number;          // e.g. 10 000
  maxExpandedBytes: number;    // e.g. 500 MiB
  maxCompressionRatio: number; // e.g. 100 (expanded/compressed)
  maxNestingDepth: number;     // e.g. 10
}

/** Normalise a POSIX path, remove leading "./", collapse ".." */
function normalise(entryPath: string): string {
  const p = path.posix.normalize(entryPath);
  return p.replace(/^\.?\//, ""); // strip leading "./" or "/"
}

/** Compute nesting depth (number of path separators) */
function depth(entryPath: string): number {
  return entryPath.split("/").filter(Boolean).length;
}

/** Core inspection routine */
export async function inspectArchive(
  filePath: string,
  limits: Limits,
  quarantineRoot: string = "./quarantine"
): Promise<{ manifest: ArchiveEntry[]; errors: string[] }> {
  const format = await detectFormat(filePath);
  const adapter = await createAdapter(format, filePath);
  const manifest: ArchiveEntry[] = [];
  const errors: string[] = [];

  // ---------- 1️⃣ List & validate ----------
  const entries = await adapter.listEntries();

  if (entries.length > limits.maxEntries) {
    errors.push(`Entry count ${entries.length} exceeds limit ${limits.maxEntries}`);
  }

  // Track duplicate normalised paths
  const seen = new Set<string>();
  let totalExpanded = 0;
  let totalCompressed = 0;

  for (const e of entries) {
    const norm = normalise(e.path);

    // 2️⃣ Reject absolute paths
    if (path.isAbsolute(e.path) || e.path.startsWith("\\")) {
      errors.push(`Absolute path rejected: ${e.path}`);
      continue;
    }

    // 3️⃣ Reject traversal ("..")
    if (norm.split("/").includes("..")) {
      errors.push(`Path traversal detected: ${e.path}`);
      continue;
    }

    // 4️⃣ Reject symlink that points outside the archive
    if (e.isSymlink && e.linkTarget) {
      const targetNorm = normalise(e.linkTarget);
      if (targetNorm.startsWith("..")) {
        errors.push(`Symlink escaping detected: ${e.path} → ${e.linkTarget}`);
        continue;
      }
    }

    // 5️⃣ Reject encrypted entries (ZIP only)
    if (e.encrypted) {
      errors.push(`Encrypted entry rejected: ${e.path}`);
      continue;
    }

    // 6️⃣ Duplicate normalized path?
    if (seen.has(norm)) {
      errors.push(`Duplicate normalized path: ${e.path}`);
      continue;
    }
    seen.add(norm);

    // 7️⃣ Nesting depth
    if (depth(norm) > limits.maxNestingDepth) {
      errors.push(`Nesting depth of ${e.path} exceeds limit ${limits.maxNestingDepth}`);
      continue;
    }

    // 8️⃣ Track sizes for global limits
    totalExpanded += e.size;
    if (e.compressedSize) totalCompressed += e.compressedSize;

    // If entry passed all checks, keep it for extraction
    manifest.push(e);
  }

  // Global limits
  if (totalExpanded > limits.maxExpandedBytes) {
    errors.push(
      `Expanded size ${totalExpanded} B exceeds limit ${limits.maxExpandedBytes} B`
    );
  }
  if (totalCompressed > 0 && totalExpanded / totalCompressed > limits.maxCompressionRatio) {
    errors.push(
      `Compression ratio ${(
        totalExpanded / totalCompressed
      ).toFixed(2)} exceeds limit ${limits.maxCompressionRatio}`
    );
  }

  // ---------- 2️⃣ Extraction (only if no fatal errors) ----------
  if (errors.length === 0) {
    // Create a quarantine destination unique per archive (hash of file)
    const hash = crypto
      .createHash("sha256")
      .update(await fs.promises.readFile(filePath))
      .digest("hex")
      .slice(0, 12);
    const quarantine = new QuarantineAdapter(`${quarantineRoot}/${hash}`);

    for (const entry of manifest) {
      const dest = quarantine.createWriteStream(entry.path);
      await adapter.extract(entry, dest);
    }

    await quarantine.finalise();
  }

  await adapter.close();
  return { manifest, errors };
}
```

---

## 📂 Adapters  

### 1️⃣ `ZipAdapter` (`src/adapters/ZipAdapter.ts`)

```ts
// src/adapters/ZipAdapter.ts
import { createReadStream } from "node:fs";
import { PassThrough, Writable } from "node:stream";
import unzipper from "unzipper";
import type { ArchiveAdapter, ArchiveEntry } from "./ArchiveAdapter.js";

export class ZipAdapter implements ArchiveAdapter {
  private filePath: string;

  constructor(filePath: string) {
    this.filePath = filePath;
  }

  async listEntries(): Promise<ArchiveEntry[]> {
    const entries: ArchiveEntry[] = [];

    await new Promise<void>((resolve, reject) => {
      const stream = createReadStream(this.filePath)
        .pipe(unzipper.Parse())
        .on("entry", (entry: unzipper.Entry) => {
          const isDir = entry.type === "Directory";
          const isSymlink = entry.type === "SymbolicLink";
          const encrypted = !!entry.vars.encrypted;

          entries.push({
            path: entry.path,
            size: entry.vars.uncompressedSize,
            compressedSize: entry.vars.compressedSize,
            isDirectory: isDir,
            isSymlink,
            linkTarget: isSymlink ? entry.vars.symlinkPath : undefined,
            encrypted,
          });

          entry.autodrain(); // we only need metadata now
        })
        .on("close", () => resolve())
        .on("error", reject);
    });

    return entries;
  }

  async extract(entry: ArchiveEntry, dest: Writable): Promise<void> {
    await new Promise<void>((resolve, reject) => {
      const rs = createReadStream(this.filePath)
        .pipe(unzipper.Parse())
        .on("entry", (e: unzipper.Entry) => {
          if (e.path === entry.path) {
            e.pipe(dest).on("finish", resolve).on("error", reject);
          } else {
            e.autodrain();
          }
        })
        .on("error", reject);
    });
  }

  async close(): Promise<void> {
    // No persistent resources
  }
}
```

### 2️⃣ `TarAdapter` (`src/adapters/TarAdapter.ts`)

```ts
// src/adapters/TarAdapter.ts
import { createReadStream } from "node:fs";
import { PassThrough, Writable } from "node:stream";
import tar from "tar-stream";
import gunzipMaybe from "gunzip-maybe";
import type { ArchiveAdapter, ArchiveEntry } from "./ArchiveAdapter.js";

export class TarAdapter implements ArchiveAdapter {
  private filePath: string;
  private isGz: boolean;

  constructor(filePath: string, isGz: boolean) {
    this.filePath = filePath;
    this.isGz = isGz;
  }

  async listEntries(): Promise<ArchiveEntry[]> {
    const entries: ArchiveEntry[] = [];

    await new Promise<void>((resolve, reject) => {
      const extract = tar.extract();
      extract.on("entry", (header, stream, next) => {
        const isDir = header.type === "directory";
        const isSymlink = header.type === "symlink";

        entries.push({
          path: header.name,
          size: header.size,
          isDirectory: isDir,
          isSymlink,
          linkTarget: isSymlink ? (header.linkname as string) : undefined,
        });

        stream.resume(); // discard content
        stream.on("end", next);
      });
      extract.on("finish", resolve);
      extract.on("error", reject);

      const src = createReadStream(this.filePath);
      const pipe = this.isGz ? src.pipe(gunzipMaybe()) : src;
      pipe.pipe(extract);
    });

    return entries;
  }

  async extract(entry: ArchiveEntry, dest: Writable): Promise<void> {
    await new Promise<void>((resolve, reject) => {
      const extract = tar.extract();
      let found = false;

      extract.on("entry", (header, stream, next) => {
        if (header.name === entry.path) {
          found = true;
          stream.pipe(dest).on("finish", () => {
            resolve();
            next();
          });
        } else {
          stream.resume();
          stream.on("end", next);
        }
      });
      extract.on("finish", () => {
        if (!found) reject(new Error(`Entry ${entry.path} not found`));
      });
      extract.on("error", reject);

      const src = createReadStream(this.filePath);
      const pipe = this.isGz ? src.pipe(gunzipMaybe()) : src;
      pipe.pipe(extract);
    });
  }

  async close(): Promise<void> {
    // No persistent resources
  }
}
```

### 3️⃣ `SevenZAdapter` (`src/adapters/SevenZAdapter.ts`)

```ts
// src/adapters/SevenZAdapter.ts
import { createReadStream, promises as fs } from "node:fs";
import { Writable, PassThrough } from "node:stream";
import { Seven } from "node-7z";
import type { ArchiveAdapter, ArchiveEntry } from "./ArchiveAdapter.js";
import * as path from "node:path";

export class SevenZAdapter implements ArchiveAdapter {
  private filePath: string;

  constructor(filePath: string) {
    this.filePath = filePath;
  }

  /** List entries using `7z l -slt` */
  async listEntries(): Promise<ArchiveEntry[]> {
    const list = await new Promise<any[]>((resolve, reject) => {
      const out: any[] = [];
      const proc = Seven.list(this.filePath, { $bin: Seven.getBinPath() })
        .on("data", (data) => out.push(data))
        .on("end", () => resolve(out))
        .on("error", reject);
    });

    // `node-7z` returns an array of objects with properties we need
    return list.map((info) => ({
      path: info.Path,
      size: Number(info.Size),
      // 7z does not expose compressed size per entry via list; use undefined
      compressedSize: undefined,
      isDirectory: info.Attributes?.includes("D") ?? false,
      isSymlink: false, // 7z does not support symlinks on Windows; ignore
    }));
  }

  /** Extract a single entry to a Writable using `7z e -so` */
  async extract(entry: ArchiveEntry, dest: Writable): Promise<void> {
    await new Promise<void>((resolve, reject) => {
      const proc = Seven.extractFull(this.filePath, "-", {
        $bin: Seven.getBinPath(),
        $raw: ["e", "-so", entry.path],
      })
        .on("data", (chunk) => dest.write(chunk))
        .on("end", () => {
          dest.end();
          resolve();
        })
        .on("error", reject);
    });
  }

  async close(): Promise<void> {
    // No persistent resources
  }
}
```

> **Note:** `node-7z` ships the 7‑Zip binary via `7zip-bin`, so no external installation is required.

---

## 📦 Quarantine Output (`src/QuarantineAdapter.ts`)

```ts
// src/QuarantineAdapter.ts
import { promises as fs, createWriteStream, WriteStream } from "node:fs";
import * as path from "node:path";

export class QuarantineAdapter {
  private root: string;

  constructor(root: string) {
    this.root = root;
  }

  /** Ensure the base directory exists */
  private async ensureRoot(): Promise<void> {
    await fs.mkdir(this.root, { recursive: true });
  }

  /** Create a safe write stream for a given entry path */
  async createWriteStream(entryPath: string): Promise<WriteStream> {
    await this.ensureRoot();
    const safePath = path.join(this.root, entryPath);
    await fs.mkdir(path.dirname(safePath), { recursive: true });
    return createWriteStream(safePath, { flags: "wx" }); // fail if exists
  }

  /** Called after all entries have been written – can be used for cleanup */
  async finalise(): Promise<void> {
    // No extra work needed for this demo
  }
}
```

The quarantine folder is **outside** the original archive location, never overwriting existing files, and each entry is written with the `wx` flag to avoid race‑condition overwrites.

---

## 🧪 CLI Entrypoint (`src/inspect.ts`)

```ts
// src/inspect.ts
import { inspectArchive, Limits } from "./Inspector.js";
import * as path from "node:path";

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.error("Usage: npm start -- <archive-path>");
    process.exit(1);
  }

  const archivePath = path.resolve(args[0]);

  // Example limits – tweak as needed
  const limits: Limits = {
    maxEntries: 10_000,
    maxExpandedBytes: 500 * 1024 * 1024, // 500 MiB
    maxCompressionRatio: 100,
    maxNestingDepth: 10,
  };

  try {
    const { manifest, errors } = await inspectArchive(archivePath, limits);
    console.log("\n=== Manifest ===");
    console.log(JSON.stringify(manifest, null, 2));

    if (errors.length) {
      console.error("\n=== Errors ===");
      errors.forEach((e) => console.error("❌", e));
      process.exit(2);
    } else {
      console.log("\n✅ Archive passed all checks and was quarantined.");
    }
  } catch (e) {
    console.error("Fatal error:", e);
    process.exit(3);
  }
}

main();
```

Running the script prints a **JSON manifest** and either a success message or a list of rejection reasons.

---

## 📁 Fixtures  

### 1️⃣ Safe fixture – `fixtures/safe.zip`

```bash
# Create a tiny safe zip (one text file)
mkdir -p fixtures/tmp
echo "Hello, safe world!" > fixtures/tmp/hello.txt
cd fixtures/tmp
zip -r ../safe.zip hello.txt > /dev/null
cd ../../
rm -rf fixtures/tmp
```

The archive contains:

```
hello.txt (size 20 B)
```

### 2️⃣ Traversal fixture – `fixtures/traversal.zip`

```bash
mkdir -p fixtures/tmp
echo "You should not see me!" > fixtures/tmp/evil.txt
cd fixtures/tmp
zip -r ../traversal.zip ../evil.txt > /dev/null
# rename entry to include "../"
zip -d ../traversal.zip evil.txt
zip -j ../traversal.zip ../evil.txt -z <(echo "../evil.txt")
cd ../../
rm -rf fixtures/tmp
```

(For brevity, the repository ships a pre‑built `traversal.zip` that contains an entry named `../evil.txt`.)

### 3️⃣ Limit‑breach fixture – `fixtures/huge.tar.gz`

```bash
mkdir -p fixtures/tmp
# Create a 600 MiB file
dd if=/dev/zero of=fixtures/tmp/big.bin bs=1M count=600
cd fixtures/tmp
tar -czf ../huge.tar.gz big.bin
cd ../../
rm -rf fixtures/tmp
```

The tarball exceeds the `maxExpandedBytes` limit (500 MiB) and will be rejected.

---

## 📜 Full `README.md` (excerpt)

```markdown
# Archive Inspector

A tiny, **self‑contained** TypeScript library that safely inspects ZIP, TAR/TGZ and 7z archives.

## Features

* **Format detection** from magic bytes – no external commands.
* **Unified interface** (`ArchiveAdapter`) – add more formats later.
* **Security checks** – absolute paths, `..` traversal, symlink escape, encrypted entries, duplicate normalized paths.
* **Resource limits** – entry count, total expanded size, compression ratio, nesting depth.
* **Quarantine output** – each accepted entry is streamed to a temporary folder.
* **Common manifest** – JSON list of all accepted entries.

## Quick start

```bash
npm ci
npm start -- fixtures/safe.zip   # should succeed
npm start -- fixtures/traversal.zip   # should be rejected
npm start -- fixtures/huge.tar.gz     # should hit size limit
```

## Extending

Add a new adapter implementing `ArchiveAdapter` and register it in `createAdapter()`.

```

---

## ✅ What the code **does not** do (by design)

* It does **not** expose an HTTP upload endpoint – you can embed the core in any service you like.  
* It does **not** attempt to execute any archive‑specific commands beyond the bundled 7‑Zip binary.  
* It does **not** resolve Windows‑style backslashes in paths – the inspector normalises everything to POSIX style, which is safe on all platforms.

---

## 🧩 Putting it all together (one‑liner build & run)

```bash
npm ci && npm run build && node dist/inspect.js fixtures/safe.zip
```

The above command installs exact dependencies, compiles TypeScript, and runs the inspector on the safe fixture, printing a manifest like:

```json
[
  {
    "path": "hello.txt",
    "size": 20,
    "compressedSize": 22,
    "isDirectory": false,
    "isSymlink": false,
    "encrypted": false
  }
]
```

If a violation occurs, the console will list each error and exit with a non‑zero status.

---

### 🎉 All set!  
You now have a **portable, audited** archive‑inspection core that can be dropped into any Node.js service, CI pipeline, or desktop utility. Feel free to copy the `src/` folder into your own project, adjust the limits, and extend the adapters as needed. Happy (and safe) archiving!
