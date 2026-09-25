# Archive Inspector — Self-Contained Node.js TypeScript Solution

## Project Structure

```
archive-inspector/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts                    # CLI entry point
│   ├── types.ts                    # Shared types & interfaces
│   ├── adapters/
│   │   ├── interface.ts            # FormatAdapter interface
│   │   ├── zip-adapter.ts          # ZIP implementation (yauzl)
│   │   ├── tar-adapter.ts          # TAR/TAR.GZ implementation (tar-stream)
│   │   └── seven-zip-adapter.ts    # 7z implementation (7zz)
│   ├── core/
│   │   ├── detector.ts             # Magic-byte format detection
│   │   ├── inspector.ts            # Main inspection logic
│   │   ├── security.ts             # Path validation & limits
│   │   ├── quarantine.ts           # Quarantined output adapter
│   │   └── manifest.ts             # Manifest generation
│   └── fixtures/
│       └── generate-fixtures.ts    # Safe + malicious test archives
└── fixtures/                       # Generated test archives (gitignored)
    ├── safe.zip
    ├── traversal.tar.gz
    ├── entry-limit.7z
    └── ratio.zip
```

---

## `package.json`

```json
{
  "name": "archive-inspector",
  "version": "1.0.0",
  "description": "Secure archive inspector with format adapters, security limits, and quarantine extraction",
  "type": "module",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "tsx src/index.ts",
    "fixtures": "tsx src/fixtures/generate-fixtures.ts",
    "test": "vitest run",
    "test:watch": "vitest",
    "lint": "eslint src --ext .ts",
    "clean": "rm -rf dist fixtures"
  },
  "dependencies": {
    "yauzl": "^3.2.0",
    "tar-stream": "^3.1.7",
    "7zip-bin": "^5.2.0",
    "streamx": "^2.18.0",
    "uint8array-extras": "^1.4.0"
  },
  "devDependencies": {
    "@types/node": "^22.5.0",
    "@types/yauzl": "^3.2.31",
    "typescript": "^5.6.2",
    "tsx": "^4.19.0",
    "vitest": "^2.1.0",
    "eslint": "^9.10.0",
    "@typescript-eslint/eslint-plugin": "^8.5.0",
    "@typescript-eslint/parser": "^8.5.0"
  },
  "engines": {
    "node": ">=20.0.0"
  },
  "packageManager": "npm@10.8.2"
}
```

---

## `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2024",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2024"],
    "outDir": "./dist",
    "rootDir": "./src",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "forceConsistentCasingInFileNames": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": false
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "fixtures"]
}
```

---

## `src/types.ts`

```typescript
/**
 * Core type definitions for the archive inspector.
 */

/** Archive format identifiers */
export type ArchiveFormat = 'zip' | 'tar' | 'tar.gz' | 'tgz' | '7z';

/** Entry metadata from archive listing */
export interface ArchiveEntry {
  /** Normalized path (POSIX, no leading slash, no .. segments) */
  path: string;
  /** Uncompressed size in bytes */
  size: number;
  /** Compressed size in bytes (if available) */
  compressedSize?: number;
  /** Last modification time (UTC) */
  mtime?: Date;
  /** Entry type */
  type: 'file' | 'directory' | 'symlink' | 'hardlink' | 'other';
  /** Link target for symlinks/hardlinks */
  linkTarget?: string;
  /** Unix permissions mode (e.g., 0o644) */
  mode?: number;
  /** Whether entry is encrypted */
  encrypted: boolean;
  /** Raw format-specific metadata */
  raw?: Record<string, unknown>;
}

/** Security limits configuration */
export interface SecurityLimits {
  /** Maximum number of entries allowed */
  maxEntries: number;
  /** Maximum total uncompressed bytes allowed */
  maxTotalSize: number;
  /** Maximum compression ratio (uncompressed/compressed) */
  maxCompressionRatio: number;
  /** Maximum nesting depth (path segments) */
  maxNestingDepth: number;
  /** Maximum individual entry size */
  maxEntrySize: number;
}

/** Result of security validation */
export interface ValidationResult {
  allowed: boolean;
  reason?: string;
  normalizedPath?: string;
}

/** Quarantined output entry */
export interface QuarantineEntry {
  path: string;
  stream: ReadableStream<Uint8Array> | AsyncIterable<Uint8Array>;
  size: number;
  mtime?: Date;
  mode?: number;
}

/** Common manifest for all formats */
export interface InspectionManifest {
  /** Archive format detected */
  format: ArchiveFormat;
  /** Original archive filename */
  archiveName: string;
  /** Archive size in bytes */
  archiveSize: number;
  /** Timestamp of inspection */
  inspectedAt: string;
  /** Security limits applied */
  limits: SecurityLimits;
  /** All entries found (before filtering) */
  allEntries: ArchiveEntry[];
  /** Entries that passed validation */
  acceptedEntries: ArchiveEntry[];
  /** Entries rejected with reasons */
  rejectedEntries: Array<{ entry: ArchiveEntry; reason: string }>;
  /** Summary statistics */
  summary: {
    totalEntries: number;
    acceptedCount: number;
    rejectedCount: number;
    totalUncompressedSize: number;
    maxCompressionRatio: number;
  };
  /** Errors during processing */
  errors: string[];
}

/** Format adapter interface */
export interface FormatAdapter {
  /** Unique format identifier */
  readonly format: ArchiveFormat;
  /** List all entries without extracting */
  listEntries(source: AsyncIterable<Uint8Array> | NodeJS.ReadableStream): Promise<ArchiveEntry[]>;
  /** Extract a single entry as a stream */
  extractEntry(source: AsyncIterable<Uint8Array> | NodeJS.ReadableStream, entryPath: string): Promise<AsyncIterable<Uint8Array> | null>;
  /** Check if format supports streaming extraction */
  readonly supportsStreaming: boolean;
}

/** Quarantine output adapter interface */
export interface QuarantineAdapter {
  /** Write an accepted entry to quarantine */
  writeEntry(entry: QuarantineEntry): Promise<void>;
  /** Finalize and return manifest */
  finalize(manifest: InspectionManifest): Promise<void>;
  /** Get quarantine root path */
  readonly rootPath: string;
}
```

---

## `src/adapters/interface.ts`

```typescript
/**
 * Format Adapter Interface
 * 
 * Each adapter implements this interface for a specific archive format.
 * Adapters must support streaming (no full extraction to disk/memory).
 */

import type { ArchiveEntry, ArchiveFormat, FormatAdapter } from '../types.js';

/**
 * Base adapter class with common utilities.
 * Concrete adapters extend this and implement abstract methods.
 */
export abstract class BaseAdapter implements FormatAdapter {
  public abstract readonly format: ArchiveFormat;
  public abstract readonly supportsStreaming: boolean;

  /**
   * Normalize a path to POSIX format, resolve . and .. segments,
   * and remove leading slash.
   */
  protected normalizePath(rawPath: string): string {
    // Convert backslashes to forward slashes
    let path = rawPath.replace(/\\/g, '/');
    
    // Remove leading slash
    if (path.startsWith('/')) {
      path = path.slice(1);
    }
    
    // Resolve . and .. segments
    const segments = path.split('/').filter(seg => seg !== '' && seg !== '.');
    const resolved: string[] = [];
    
    for (const seg of segments) {
      if (seg === '..') {
        if (resolved.length > 0) {
          resolved.pop();
        }
      } else {
        resolved.push(seg);
      }
    }
    
    return resolved.join('/');
  }

  /**
   * Calculate nesting depth of a normalized path.
   */
  protected getNestingDepth(normalizedPath: string): number {
    if (normalizedPath === '') return 0;
    return normalizedPath.split('/').length;
  }

  /**
   * Validate entry path against security rules.
   * Returns normalized path if valid, throws if invalid.
   */
  protected validatePath(rawPath: string, entryType: ArchiveEntry['type'], linkTarget?: string): string {
    const normalized = this.normalizePath(rawPath);
    
    // Empty path after normalization
    if (normalized === '') {
      throw new Error('Empty path after normalization');
    }
    
    // Absolute path check (should be caught by normalization, but defense in depth)
    if (rawPath.startsWith('/') || /^[A-Za-z]:[\\/]/.test(rawPath)) {
      throw new Error('Absolute path detected');
    }
    
    // Traversal attempt in original path
    if (rawPath.includes('..') || rawPath.includes('~')) {
      throw new Error('Path traversal sequence detected');
    }
    
    // Symlink/hardlink target validation
    if ((entryType === 'symlink' || entryType === 'hardlink') && linkTarget) {
      const normalizedTarget = this.normalizePath(linkTarget);
      if (linkTarget.startsWith('/') || /^[A-Za-z]:[\\/]/.test(linkTarget) || linkTarget.includes('..')) {
        throw new Error('Link target escapes archive root');
      }
      // Ensure target stays within archive (no absolute, no traversal)
      if (normalizedTarget.startsWith('/') || normalizedTarget.includes('..')) {
        throw new Error('Link target escapes archive root');
      }
    }
    
    return normalized;
  }

  public abstract listEntries(source: AsyncIterable<Uint8Array> | NodeJS.ReadableStream): Promise<ArchiveEntry[]>;
  public abstract extractEntry(source: AsyncIterable<Uint8Array> | NodeJS.ReadableStream, entryPath: string): Promise<AsyncIterable<Uint8Array> | null>;
}
```

---

## `src/adapters/zip-adapter.ts`

```typescript
/**
 * ZIP Format Adapter using yauzl
 * 
 * yauzl API:
 * - yauzl.fromBuffer(buffer, options, callback) -> ZipFile
 * - ZipFile.on('entry', callback) -> Entry
 * - ZipFile.openReadStream(entry, callback) -> ReadableStream
 * - Entry: { fileName, compressedSize, uncompressedSize, getLastModDate(), 
 *            isDirectory(), mode, encrypted }
 * 
 * Streaming: yauzl reads central directory first, then streams individual entries
 * on demand. No full extraction required.
 */

import yauzl from 'yauzl';
import { Readable } from 'node:stream';
import { BaseAdapter } from './interface.js';
import type { ArchiveEntry, ArchiveFormat, FormatAdapter } from '../types.js';
import { toAsyncIterable } from '../utils/stream-utils.js';

export class ZipAdapter extends BaseAdapter implements FormatAdapter {
  public readonly format: ArchiveFormat = 'zip';
  public readonly supportsStreaming = true;

  async listEntries(source: AsyncIterable<Uint8Array> | NodeJS.ReadableStream): Promise<ArchiveEntry[]> {
    const buffer = await this.consumeSource(source);
    return new Promise((resolve, reject) => {
      yauzl.fromBuffer(buffer, { lazyEntries: true }, (err, zipfile) => {
        if (err) return reject(err);
        if (!zipfile) return reject(new Error('Failed to open ZIP'));

        const entries: ArchiveEntry[] = [];
        
        zipfile.on('entry', (entry) => {
          try {
            const normalizedPath = this.validatePath(
              entry.fileName,
              entry.isDirectory() ? 'directory' : 'file',
              undefined
            );
            
            entries.push({
              path: normalizedPath,
              size: entry.uncompressedSize,
              compressedSize: entry.compressedSize,
              mtime: entry.getLastModDate(),
              type: entry.isDirectory() ? 'directory' : 'file',
              mode: entry.externalFileAttributes >> 16 & 0o777,
              encrypted: (entry.bitFlag & 0x1) !== 0,
              raw: {
                compressionMethod: entry.compressionMethod,
                crc32: entry.crc32,
                extraFields: entry.extraFields,
              },
            });
          } catch (e) {
            // Invalid entry - we'll catch it in security validation later
            entries.push({
              path: entry.fileName,
              size: entry.uncompressedSize,
              compressedSize: entry.compressedSize,
              mtime: entry.getLastModDate(),
              type: entry.isDirectory() ? 'directory' : 'file',
              encrypted: (entry.bitFlag & 0x1) !== 0,
              raw: { validationError: (e as Error).message },
            });
          }
          zipfile.readEntry();
        });

        zipfile.on('end', () => resolve(entries));
        zipfile.on('error', reject);
        zipfile.readEntry();
      });
    });
  }

  async extractEntry(
    source: AsyncIterable<Uint8Array> | NodeJS.ReadableStream,
    entryPath: string
  ): Promise<AsyncIterable<Uint8Array> | null> {
    const buffer = await this.consumeSource(source);
    
    return new Promise((resolve, reject) => {
      yauzl.fromBuffer(buffer, { lazyEntries: true }, (err, zipfile) => {
        if (err) return reject(err);
        if (!zipfile) return reject(new Error('Failed to open ZIP'));

        let found = false;
        
        zipfile.on('entry', (entry) => {
          if (found) {
            zipfile.readEntry();
            return;
          }
          
          if (entry.fileName === entryPath) {
            found = true;
            zipfile.openReadStream(entry, (err, stream) => {
              if (err) return reject(err);
              if (!stream) return resolve(null);
              resolve(toAsyncIterable(stream));
            });
          } else {
            zipfile.readEntry();
          }
        });

        zipfile.on('end', () => {
          if (!found) resolve(null);
        });
        zipfile.on('error', reject);
        zipfile.readEntry();
      });
    });
  }

  private async consumeSource(source: AsyncIterable<Uint8Array> | NodeJS.ReadableStream): Promise<Buffer> {
    if (Symbol.asyncIterator in source) {
      const chunks: Uint8Array[] = [];
      for await (const chunk of source) {
        chunks.push(chunk);
      }
      return Buffer.concat(chunks);
    }
    // Node.js ReadableStream
    return new Promise((resolve, reject) => {
      const chunks: Buffer[] = [];
      source.on('data', (chunk: Buffer) => chunks.push(chunk));
      source.on('end', () => resolve(Buffer.concat(chunks)));
      source.on('error', reject);
    });
  }
}
```

---

## `src/adapters/tar-adapter.ts`

```typescript
/**
 * TAR/TAR.GZ Format Adapter using tar-stream
 * 
 * tar-stream API:
 * - tar.extract() -> Extract stream
 * - extract.on('entry', (header, stream, next) => { ... })
 * - header: { name, size, mode, mtime, type, linkname }
 * - Types: 'file', 'directory', 'symlink', 'link', 'block-device', 
 *          'character-device', 'fifo', 'contiguous-file'
 * - stream: Readable stream of entry data
 * - next(): call to continue to next entry
 * 
 * For gzipped: use zlib.createGunzip() pipe before tar.extract()
 * 
 * Streaming: tar-stream parses headers sequentially, yields entry streams
 * on demand. No full extraction.
 */

import tar from 'tar-stream';
import zlib from 'node:zlib';
import { Readable } from 'node:stream';
import { BaseAdapter } from './interface.js';
import type { ArchiveEntry, ArchiveFormat, FormatAdapter } from '../types.js';
import { toAsyncIterable } from '../utils/stream-utils.js';

export class TarAdapter extends BaseAdapter implements FormatAdapter {
  public readonly format: ArchiveFormat = 'tar';
  public readonly supportsStreaming = true;

  private isGzipped = false;

  setGzipped(gzipped: boolean): this {
    this.isGzipped = gzipped;
    return this;
  }

  async listEntries(source: AsyncIterable<Uint8Array> | NodeJS.ReadableStream): Promise<ArchiveEntry[]> {
    const entries: ArchiveEntry[] = [];
    
    await this.processEntries(source, async (header, stream, next) => {
      try {
        const type = this.mapType(header.type);
        const normalizedPath = this.validatePath(header.name, type, header.linkname);
        
        // Consume stream to advance parser (but don't store data)
        for await (const _chunk of toAsyncIterable(stream)) {
          // Drain
        }
        
        entries.push({
          path: normalizedPath,
          size: header.size,
          compressedSize: undefined, // TAR doesn't store per-entry compression
          mtime: header.mtime ? new Date(header.mtime) : undefined,
          type,
          linkTarget: header.linkname,
          mode: header.mode,
          encrypted: false, // TAR doesn't support encryption
          raw: { 
            type: header.type,
            uid: header.uid,
            gid: header.gid,
            uname: header.uname,
            gname: header.gname,
          },
        });
      } catch (e) {
        // Still consume stream
        for await (const _chunk of toAsyncIterable(stream)) {}
        entries.push({
          path: header.name,
          size: header.size,
          mtime: header.mtime ? new Date(header.mtime) : undefined,
          type: this.mapType(header.type),
          linkTarget: header.linkname,
          mode: header.mode,
          encrypted: false,
          raw: { validationError: (e as Error).message },
        });
      }
      next();
    });
    
    return entries;
  }

  async extractEntry(
    source: AsyncIterable<Uint8Array> | NodeJS.ReadableStream,
    entryPath: string
  ): Promise<AsyncIterable<Uint8Array> | null> {
    let found = false;
    let result: AsyncIterable<Uint8Array> | null = null;
    
    await this.processEntries(source, async (header, stream, next) => {
      if (found) {
        for await (const _ of toAsyncIterable(stream)) {}
        next();
        return;
      }
      
      if (header.name === entryPath) {
        found = true;
        result = toAsyncIterable(stream);
        // Don't call next() - we're taking ownership of the stream
        // The parser will be abandoned, which is fine for single extraction
      } else {
        for await (const _ of toAsyncIterable(stream)) {}
        next();
      }
    });
    
    return result;
  }

  private async processEntries(
    source: AsyncIterable<Uint8Array> | NodeJS.ReadableStream,
    onEntry: (header: tar.Headers, stream: NodeJS.ReadableStream, next: () => void) => Promise<void>
  ): Promise<void> {
    const nodeStream = this.toNodeStream(source);
    const extract = this.isGzipped ? tar.extract() : tar.extract();
    
    if (this.isGzipped) {
      const gunzip = zlib.createGunzip();
      nodeStream.pipe(gunzip).pipe(extract);
    } else {
      nodeStream.pipe(extract);
    }

    return new Promise((resolve, reject) => {
      extract.on('entry', (header, stream, next) => {
        Promise.resolve(onEntry(header, stream, next)).catch(reject);
      });
      extract.on('finish', resolve);
      extract.on('error', reject);
    });
  }

  private toNodeStream(source: AsyncIterable<Uint8Array> | NodeJS.ReadableStream): NodeJS.ReadableStream {
    if (typeof source.pipe === 'function') {
      return source;
    }
    // Convert async iterable to readable stream
    return Readable.from(toAsyncIterable(source));
  }

  private mapType(tarType: string): ArchiveEntry['type'] {
    switch (tarType) {
      case 'directory': return 'directory';
      case 'symlink': return 'symlink';
      case 'link': return 'hardlink';
      case 'file':
      case 'contiguous-file':
      default: return 'file';
    }
  }
}
```

---

## `src/adapters/seven-zip-adapter.ts`

```typescript
/**
 * 7z Format Adapter using 7zz (7-Zip extra binary)
 * 
 * 7zz API (command line):
 * - 7zz l -slt -ba <archive> -> detailed listing (stdout)
 * - 7zz e -so <archive> <entry> -> extract to stdout
 * 
 * We use 7zip-bin package which provides the 7zz binary path.
 * 
 * Streaming: 7zz can extract individual entries to stdout (-so flag).
 * Listing requires parsing text output.
 */

import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { BaseAdapter } from './interface.js';
import type { ArchiveEntry, ArchiveFormat, FormatAdapter } from '../types.js';
import { toAsyncIterable } from '../utils/stream-utils.js';
import { get7zzPath } from '../utils/7zz-path.js';

export class SevenZipAdapter extends BaseAdapter implements FormatAdapter {
  public readonly format: ArchiveFormat = '7z';
  public readonly supportsStreaming = true;

  private sevenzzPath: string;

  constructor() {
    super();
    this.sevenzzPath = get7zzPath();
  }

  async listEntries(source: AsyncIterable<Uint8Array> | NodeJS.ReadableStream): Promise<ArchiveEntry[]> {
    // 7zz needs a file, so we must write to temp file
    const tmpFile = await this.writeToTempFile(source);
    
    try {
      const output = await this.run7zz(['l', '-slt', '-ba', tmpFile]);
      return this.parseListing(output);
    } finally {
      // Cleanup temp file
      await this.cleanupTempFile(tmpFile);
    }
  }

  async extractEntry(
    source: AsyncIterable<Uint8Array> | NodeJS.ReadableStream,
    entryPath: string
  ): Promise<AsyncIterable<Uint8Array> | null> {
    const tmpFile = await this.writeToTempFile(source);
    
    try {
      // 7zz extracts to stdout with -so
      const proc = spawn(this.sevenzzPath, ['e', '-so', tmpFile, entryPath], {
        stdio: ['ignore', 'pipe', 'pipe'],
      });
      
      let found = false;
      proc.stdout.on('data', () => { found = true; });
      
      await new Promise<void>((resolve, reject) => {
        proc.on('close', (code) => {
          if (code === 0 || (code === 1 && found)) resolve();
          else if (code === 1 && !found) resolve(); // Entry not found
          else reject(new Error(`7zz exited with code ${code}`));
        });
        proc.on('error', reject);
      });
      
      if (!found) return null;
      
      return toAsyncIterable(proc.stdout);
    } finally {
      await this.cleanupTempFile(tmpFile);
    }
  }

  private parseListing(output: string): ArchiveEntry[] {
    const entries: ArchiveEntry[] = [];
    const blocks = output.split('\n\n').filter(b => b.trim());
    
    for (const block of blocks) {
      const lines = block.split('\n').map(l => l.trim()).filter(l => l);
      const entry: Partial<ArchiveEntry> = {
        encrypted: false,
        raw: {},
      };
      
      for (const line of lines) {
        const [key, ...valParts] = line.split('=');
        const value = valParts.join('=').trim();
        
        switch (key) {
          case 'Path':
            try {
              entry.path = this.validatePath(value, 'file');
            } catch (e) {
              entry.path = value;
              entry.raw = { ...entry.raw, validationError: (e as Error).message };
            }
            break;
          case 'Size':
            entry.size = parseInt(value, 10);
            break;
          case 'Packed Size':
            entry.compressedSize = parseInt(value, 10);
            break;
          case 'Modified':
            entry.mtime = new Date(value);
            break;
          case 'Attributes':
            if (value.startsWith('D')) entry.type = 'directory';
            else entry.type = 'file';
            break;
          case 'Encrypted':
            entry.encrypted = value === '+';
            break;
          case 'Method':
            entry.raw = { ...entry.raw, method: value };
            break;
        }
      }
      
      if (entry.path !== undefined && entry.size !== undefined) {
        entries.push(entry as ArchiveEntry);
      }
    }
    
    return entries;
  }

  private run7zz(args: string[]): Promise<string> {
    return new Promise((resolve, reject) => {
      const proc = spawn(this.sevenzzPath, args, { stdio: ['ignore', 'pipe', 'pipe'] });
      let stdout = '';
      let stderr = '';
      
      proc.stdout.on('data', (data) => { stdout += data.toString(); });
      proc.stderr.on('data', (data) => { stderr += data.toString(); });
      
      proc.on('close', (code) => {
        if (code === 0) resolve(stdout);
        else reject(new Error(`7zz failed (${code}): ${stderr}`));
      });
      proc.on('error', reject);
    });
  }

  private async writeToTempFile(source: AsyncIterable<Uint8Array> | NodeJS.ReadableStream): Promise<string> {
    const fs = await import('node:fs/promises');
    const os = await import('node:os');
    const tmpName = path.join(os.tmpdir(), `archive-inspector-${Date.now()}-${Math.random().toString(36).slice(2)}.7z`);
    
    const fileHandle = await fs.open(tmpName, 'w');
    try {
      if (typeof source.pipe === 'function') {
        for await (const chunk of source) {
          await fileHandle.write(chunk);
        }
      } else {
        for await (const chunk of source) {
          await fileHandle.write(chunk);
        }
      }
    } finally {
      await fileHandle.close();
    }
    return tmpName;
  }

  private async cleanupTempFile(tmpFile: string): Promise<void> {
    try {
      await import('node:fs/promises').then(fs => fs.unlink(tmpFile));
    } catch {
      // Ignore cleanup errors
    }
  }
}
```

---

## `src/utils/7zz-path.ts`

```typescript
/**
 * Resolve 7zz binary path from 7zip-bin package.
 */

import { fileURLToPath } from 'node:url';
import path from 'node:path';

let cachedPath: string | null = null;

export function get7zzPath(): string {
  if (cachedPath) return cachedPath;
  
  // 7zip-bin exports path via require('7zip-bin').path7zz
  // Since we're ESM, we need to resolve it differently
  try {
    const modulePath = require.resolve('7zip-bin');
    const binDir = path.dirname(modulePath);
    const sevenzz = path.join(binDir, '..', '7zz');
    
    // Verify it exists
    const fs = require('node:fs');
    if (fs.existsSync(sevenzz)) {
      cachedPath = sevenzz;
      return cachedPath;
    }
  } catch {
    // Fall through to fallback
  }
  
  // Fallback: assume 7zz is in PATH
  cachedPath = '7zz';
  return cachedPath;
}
```

---

## `src/utils/stream-utils.ts`

```typescript
/**
 * Stream utility functions for converting between Node.js streams
 * and web-standard AsyncIterable<Uint8Array>.
 */

import { Readable } from 'node:stream';

/**
 * Convert a Node.js ReadableStream to AsyncIterable<Uint8Array>.
 */
export async function* toAsyncIterable(stream: NodeJS.ReadableStream): AsyncIterable<Uint8Array> {
  for await (const chunk of stream) {
    yield chunk instanceof Buffer ? chunk : Buffer.from(chunk);
  }
}

/**
 * Convert an AsyncIterable<Uint8Array> to a Node.js Readable stream.
 */
export function toNodeReadable(iterable: AsyncIterable<Uint8Array>): NodeJS.ReadableStream {
  return Readable.from(iterable);
}

/**
 * Pipe an async iterable to a writable stream.
 */
export async function pipeToWritable(
  source: AsyncIterable<Uint8Array>,
  writable: NodeJS.WritableStream
): Promise<void> {
  for await (const chunk of source) {
    await new Promise<void>((resolve, reject) => {
      writable.write(chunk, (err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  }
  await new Promise<void>((resolve, reject) => {
    writable.end((err) => {
      if (err) reject(err);
      else resolve();
    });
  });
}
```

---

## `src/core/detector.ts`

```typescript
/**
 * Magic-byte format detection.
 * 
 * Signatures:
 * - ZIP: PK\x03\x04 (local file header) or PK\x05\x06 (EOCD) or PK\x07\x08 (archive extra)
 * - GZIP: \x1f\x8b
 * - TAR: ustar\0 at offset 257 (POSIX) or ustar\040\0 at offset 257 (GNU)
 * - 7z: 7z\xbc\xaf\x27\x1c
 */

import type { ArchiveFormat } from '../types.js';

const MAGIC_BYTES: Record<ArchiveFormat, number[][]> = {
  zip: [
    [0x50, 0x4b, 0x03, 0x04], // Local file header
    [0x50, 0x4b, 0x05, 0x06], // End of central directory
    [0x50, 0x4b, 0x07, 0x08], // Archive extra data record
  ],
  'tar.gz': [[0x1f, 0x8b]], // GZIP magic
  tgz: [[0x1f, 0x8b]],
  tar: [
    [0x75, 0x73, 0x74, 0x61, 0x72, 0x00],     // ustar\0 (POSIX)
    [0x75, 0x73, 0x74, 0x61, 0x72, 0x20, 0x00], // ustar\040\0 (GNU)
  ],
  '7z': [[0x37, 0x7a, 0xbc, 0xaf, 0x27, 0x1c]], // 7z signature
};

const TAR_OFFSET = 257;

/**
 * Detect archive format from the first bytes of the file.
 * Returns the most specific format match.
 */
export function detectFormat(buffer: Uint8Array): ArchiveFormat | null {
  // Check 7z first (longest signature)
  if (matches(buffer, MAGIC_BYTES['7z'][0])) return '7z';
  
  // Check ZIP signatures
  for (const sig of MAGIC_BYTES.zip) {
    if (matches(buffer, sig)) return 'zip';
  }
  
  // Check GZIP (could be tar.gz)
  if (matches(buffer, MAGIC_BYTES['tar.gz'][0])) {
    // Peek at decompressed content for TAR signature
    // For detection purposes, we'll assume .tar.gz or .tgz extension
    // or detect after gunzip. Here we return 'tar.gz' as format.
    return 'tar.gz';
  }
  
  // Check TAR signatures at offset 257
  if (buffer.length >= TAR_OFFSET + 6) {
    const tarSlice = buffer.subarray(TAR_OFFSET, TAR_OFFSET + 6);
    for (const sig of MAGIC_BYTES.tar) {
      if (matches(tarSlice, sig.slice(0, 6))) return 'tar';
    }
    // Also check for 7-byte GNU signature
    if (buffer.length >= TAR_OFFSET + 7) {
      const tarSlice7 = buffer.subarray(TAR_OFFSET, TAR_OFFSET + 7);
      if (matches(tarSlice7, MAGIC_BYTES.tar[1])) return 'tar';
    }
  }
  
  return null;
}

function matches(buffer: Uint8Array, signature: number[]): boolean {
  if (buffer.length < signature.length) return false;
  for (let i = 0; i < signature.length; i++) {
    if (buffer[i] !== signature[i]) return false;
  }
  return true;
}

/**
 * Get format from filename extension as fallback.
 */
export function formatFromExtension(filename: string): ArchiveFormat | null {
  const ext = filename.toLowerCase().split('.').pop();
  switch (ext) {
    case 'zip': return 'zip';
    case 'tar': return 'tar';
    case 'gz':
    case 'tgz': return 'tar.gz';
    case '7z': return '7z';
    default: return null;
  }
}
```

---

## `src/core/security.ts`

```typescript
/**
 * Security validation: path normalization, traversal detection,
 * duplicate detection, and limit enforcement.
 */

import type { ArchiveEntry, SecurityLimits, ValidationResult } from '../types.js';

export const DEFAULT_LIMITS: SecurityLimits = {
  maxEntries: 1000,
  maxTotalSize: 100 * 1024 * 1024, // 100 MB
  maxCompressionRatio: 100,
  maxNestingDepth: 20,
  maxEntrySize: 50 * 1024 * 1024, // 50 MB
};

/**
 * Validate a single entry against security limits.
 * Returns ValidationResult with normalized path if allowed.
 */
export function validateEntry(
  entry: ArchiveEntry,
  limits: SecurityLimits,
  seenPaths: Set<string>
): ValidationResult {
  // 1. Encrypted entries rejected
  if (entry.encrypted) {
    return { allowed: false, reason: 'Encrypted entry not allowed' };
  }

  // 2. Normalize path (already done by adapter, but re-validate)
  let normalizedPath: string;
  try {
    normalizedPath = normalizePath(entry.path);
  } catch (e) {
    return { allowed: false, reason: (e as Error).message };
  }

  // 3. Absolute path check
  if (entry.path.startsWith('/') || /^[A-Za-z]:[\\/]/.test(entry.path)) {
    return { allowed: false, reason: 'Absolute path detected', normalizedPath };
  }

  // 4. Traversal in original path
  if (entry.path.includes('..') || entry.path.includes('~')) {
    return { allowed: false, reason: 'Path traversal sequence detected', normalizedPath };
  }

  // 5. Link target validation
  if ((entry.type === 'symlink' || entry.type === 'hardlink') && entry.linkTarget) {
    const target = normalizePath(entry.linkTarget);
    if (entry.linkTarget.startsWith('/') || /^[A-Za-z]:[\\/]/.test(entry.linkTarget) || entry.linkTarget.includes('..')) {
      return { allowed: false, reason: 'Link target escapes archive root', normalizedPath };
    }
    // Ensure resolved target stays within archive
    if (target.startsWith('..') || target.includes('..')) {
      return { allowed: false, reason: 'Link target escapes archive root', normalizedPath };
    }
  }

  // 6. Duplicate normalized path
  if (seenPaths.has(normalizedPath)) {
    return { allowed: false, reason: 'Duplicate normalized path', normalizedPath };
  }

  // 7. Nesting depth
  const depth = getNestingDepth(normalizedPath);
  if (depth > limits.maxNestingDepth) {
    return { allowed: false, reason: `Nesting depth ${depth} exceeds limit ${limits.maxNestingDepth}`, normalizedPath };
  }

  // 8. Individual entry size
  if (entry.size > limits.maxEntrySize) {
    return { allowed: false, reason: `Entry size ${entry.size} exceeds limit ${limits.maxEntrySize}`, normalizedPath };
  }

  return { allowed: true, normalizedPath };
}

/**
 * Validate aggregate limits across all entries.
 */
export function validateAggregateLimits(
  entries: ArchiveEntry[],
  limits: SecurityLimits
): { allowed: boolean; reason?: string } {
  // Entry count
  if (entries.length > limits.maxEntries) {
    return { allowed: false, reason: `Entry count ${entries.length} exceeds limit ${limits.maxEntries}` };
  }

  // Total uncompressed size
  const totalSize = entries.reduce((sum, e) => sum + e.size, 0);
  if (totalSize > limits.maxTotalSize) {
    return { allowed: false, reason: `Total uncompressed size ${totalSize} exceeds limit ${limits.maxTotalSize}` };
  }

  // Compression ratio (if compressed sizes available)
  const entriesWithCompressed = entries.filter(e => e.compressedSize && e.compressedSize > 0);
  if (entriesWithCompressed.length > 0) {
    const totalCompressed = entriesWithCompressed.reduce((sum, e) => sum + (e.compressedSize || 0), 0);
    const totalUncompressed = entriesWithCompressed.reduce((sum, e) => sum + e.size, 0);
    const ratio = totalCompressed > 0 ? totalUncompressed / totalCompressed : 0;
    if (ratio > limits.maxCompressionRatio) {
      return { allowed: false, reason: `Compression ratio ${ratio.toFixed(2)} exceeds limit ${limits.maxCompressionRatio}` };
    }
  }

  return { allowed: true };
}

/**
 * Normalize path to POSIX, resolve . and .., remove leading slash.
 */
export function normalizePath(rawPath: string): string {
  let path = rawPath.replace(/\\/g, '/');
  if (path.startsWith('/')) path = path.slice(1);
  
  const segments = path.split('/').filter(seg => seg !== '' && seg !== '.');
  const resolved: string[] = [];
  
  for (const seg of segments) {
    if (seg === '..') {
      if (resolved.length > 0) resolved.pop();
    } else {
      resolved.push(seg);
    }
  }
  
  return resolved.join('/');
}

/**
 * Calculate nesting depth of normalized path.
 */
export function getNestingDepth(normalizedPath: string): number {
  if (normalizedPath === '') return 0;
  return normalizedPath.split('/').length;
}

/**
 * Check for duplicate normalized paths in entry list.
 */
export function findDuplicatePaths(entries: ArchiveEntry[]): Map<string, ArchiveEntry[]> {
  const pathMap = new Map<string, ArchiveEntry[]>();
  for (const entry of entries) {
    const norm = normalizePath(entry.path);
    const existing = pathMap.get(norm) || [];
    existing.push(entry);
    pathMap.set(norm, existing);
  }
  // Return only duplicates
  const duplicates = new Map<string, ArchiveEntry[]>();
  for (const [path, entries] of pathMap) {
    if (entries.length > 1) duplicates.set(path, entries);
  }
  return duplicates;
}
```

---

## `src/core/quarantine.ts`

```typescript
/**
 * Quarantine Output Adapter
 * 
 * Streams accepted entries to a secure output directory with:
 * - Sanitized paths (already normalized)
 * - No symlink/hardlink following
 * - Atomic writes (temp file + rename)
 * - Manifest generation
 */

import { mkdir, writeFile, open, constants } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import type { QuarantineAdapter, QuarantineEntry, InspectionManifest } from '../types.js';
import { toNodeReadable } from '../utils/stream-utils.js';

export class FilesystemQuarantine implements QuarantineAdapter {
  public readonly rootPath: string;
  private manifest: InspectionManifest;
  private writtenPaths: Set<string> = new Set();

  constructor(rootPath: string, manifest: InspectionManifest) {
    this.rootPath = rootPath;
    this.manifest = manifest;
  }

  async writeEntry(entry: QuarantineEntry): Promise<void> {
    // Sanitize path again (defense in depth)
    const safePath = this.sanitizePath(entry.path);
    const fullPath = path.join(this.rootPath, safePath);
    
    // Ensure parent directory exists
    await mkdir(path.dirname(fullPath), { recursive: true });
    
    // Atomic write: write to temp, then rename
    const tmpPath = fullPath + `.tmp.${Date.now()}.${Math.random().toString(36).slice(2)}`;
    
    try {
      const fileHandle = await open(tmpPath, 'w');
      try {
        await pipeToWritable(entry.stream, fileHandle.createWriteStream());
      } finally {
        await fileHandle.close();
      }
      
      // Set mtime if provided
      if (entry.mtime) {
        const fs = await import('node:fs/promises');
        await fs.utimes(tmpPath, new Date(), entry.mtime);
      }
      
      // Set mode if provided
      if (entry.mode !== undefined) {
        const fs = await import('node:fs/promises');
        await fs.chmod(tmpPath, entry.mode);
      }
      
      // Atomic rename
      await import('node:fs/promises').then(fs => fs.rename(tmpPath, fullPath));
      this.writtenPaths.add(safePath);
    } catch (e) {
      // Cleanup temp file on error
      try { await import('node:fs/promises').then(fs => fs.unlink(tmpPath)); } catch {}
      throw e;
    }
  }

  async finalize(manifest: InspectionManifest): Promise<void> {
    this.manifest = manifest;
    const manifestPath = path.join(this.rootPath, 'MANIFEST.json');
    await writeFile(manifestPath, JSON.stringify(manifest, null, 2), 'utf-8');
  }

  private sanitizePath(rawPath: string): string {
    // Already normalized, but ensure no funny business
    let p = rawPath.replace(/\\/g, '/');
    if (p.startsWith('/')) p = p.slice(1);
    // Remove any remaining .. segments (shouldn't exist)
    const segments = p.split('/').filter(s => s !== '' && s !== '.' && s !== '..');
    return segments.join('/');
  }
}

/**
 * In-memory quarantine adapter for testing.
 */
export class MemoryQuarantine implements QuarantineAdapter {
  public readonly rootPath = ':memory:';
  private files: Map<string, Uint8Array> = new Map();
  private manifest?: InspectionManifest;

  async writeEntry(entry: QuarantineEntry): Promise<void> {
    const chunks: Uint8Array[] = [];
    for await (const chunk of entry.stream) {
      chunks.push(chunk);
    }
    this.files.set(entry.path, Buffer.concat(chunks));
  }

  async finalize(manifest: InspectionManifest): Promise<void> {
    this.manifest = manifest;
  }

  getFiles(): Map<string, Uint8Array> {
    return this.files;
  }

  getManifest(): InspectionManifest | undefined {
    return this.manifest;
  }
}

/**
 * Helper to pipe async iterable to writable stream.
 */
async function pipeToWritable(
  source: AsyncIterable<Uint8Array>,
  writable: NodeJS.WritableStream
): Promise<void> {
  for await (const chunk of source) {
    await new Promise<void>((resolve, reject) => {
      writable.write(chunk, (err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  }
  await new Promise<void>((resolve, reject) => {
    writable.end((err) => {
      if (err) reject(err);
      else resolve();
    });
  });
}
```

---

## `src/core/manifest.ts`

```typescript
/**
 * Manifest generation and serialization.
 */

import type { InspectionManifest, ArchiveEntry, SecurityLimits, ArchiveFormat } from '../types.js';

export function createManifest(
  format: ArchiveFormat,
  archiveName: string,
  archiveSize: number,
  allEntries: ArchiveEntry[],
  acceptedEntries: ArchiveEntry[],
  rejectedEntries: Array<{ entry: ArchiveEntry; reason: string }>,
  limits: SecurityLimits,
  errors: string[] = []
): InspectionManifest {
  const totalUncompressedSize = acceptedEntries.reduce((sum, e) => sum + e.size, 0);
  
  // Calculate max compression ratio among accepted entries
  let maxCompressionRatio = 0;
  for (const entry of acceptedEntries) {
    if (entry.compressedSize && entry.compressedSize > 0) {
      const ratio = entry.size / entry.compressedSize;
      if (ratio > maxCompressionRatio) maxCompressionRatio = ratio;
    }
  }

  return {
    format,
    archiveName,
    archiveSize,
    inspectedAt: new Date().toISOString(),
    limits,
    allEntries,
    acceptedEntries,
    rejectedEntries,
    summary: {
      totalEntries: allEntries.length,
      acceptedCount: acceptedEntries.length,
      rejectedCount: rejectedEntries.length,
      totalUncompressedSize,
      maxCompressionRatio: Math.round(maxCompressionRatio * 100) / 100,
    },
    errors,
  };
}

export function formatManifestSummary(manifest: InspectionManifest): string {
  const lines = [
    `Archive: ${manifest.archiveName} (${manifest.format})`,
    `Size: ${formatBytes(manifest.archiveSize)}`,
    `Inspected: ${manifest.inspectedAt}`,
    ``,
    `Limits:`,
    `  Max entries: ${manifest.limits.maxEntries}`,
    `  Max total size: ${formatBytes(manifest.limits.maxTotalSize)}`,
    `  Max compression ratio: ${manifest.limits.maxCompressionRatio}`,
    `  Max nesting depth: ${manifest.limits.maxNestingDepth}`,
    `  Max entry size: ${formatBytes(manifest.limits.maxEntrySize)}`,
    ``,
    `Summary:`,
    `  Total entries: ${manifest.summary.totalEntries}`,
    `  Accepted: ${manifest.summary.acceptedCount}`,
    `  Rejected: ${manifest.summary.rejectedCount}`,
    `  Total uncompressed: ${formatBytes(manifest.summary.totalUncompressedSize)}`,
    `  Max compression ratio: ${manifest.summary.maxCompressionRatio}`,
  ];
  
  if (manifest.rejectedEntries.length > 0) {
    lines.push(``);
    lines.push(`Rejected entries:`);
    for (const { entry, reason } of manifest.rejectedEntries) {
      lines.push(`  ${entry.path}: ${reason}`);
    }
  }
  
  if (manifest.errors.length > 0) {
    lines.push(``);
    lines.push(`Errors:`);
    for (const err of manifest.errors) {
      lines.push(`  ${err}`);
    }
  }
  
  return lines.join('\n');
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
  return `${(bytes / 1024 / 1024 / 1024).toFixed(1)} GB`;
}
```

---

## `src/core/inspector.ts`

```typescript
/**
 * Main Archive Inspector
 * 
 * Orchestrates format detection, entry listing, security validation,
 * quarantine extraction, and manifest generation.
 */

import { detectFormat, formatFromExtension } from './detector.js';
import { validateEntry, validateAggregateLimits, DEFAULT_LIMITS, findDuplicatePaths } from './security.js';
import { FilesystemQuarantine, MemoryQuarantine } from './quarantine.js';
import { createManifest, formatManifestSummary } from './manifest.js';
import { ZipAdapter } from '../adapters/zip-adapter.js';
import { TarAdapter } from '../adapters/tar-adapter.js';
import { SevenZipAdapter } from '../adapters/seven-zip-adapter.js';
import type {
  ArchiveFormat,
  ArchiveEntry,
  SecurityLimits,
  InspectionManifest,
  QuarantineAdapter,
  FormatAdapter,
} from '../types.js';
import { toAsyncIterable } from '../utils/stream-utils.js';

export interface InspectorOptions {
  limits?: Partial<SecurityLimits>;
  quarantineRoot?: string;
  useMemoryQuarantine?: boolean;
}

export class ArchiveInspector {
  private adapters: Map<ArchiveFormat, FormatAdapter> = new Map();
  private limits: SecurityLimits;

  constructor(options: InspectorOptions = {}) {
    this.limits = { ...DEFAULT_LIMITS, ...options.limits };
    
    // Register adapters
    this.adapters.set('zip', new ZipAdapter());
    this.adapters.set('tar', new TarAdapter());
    this.adapters.set('tar.gz', new TarAdapter().setGzipped(true));
    this.adapters.set('tgz', new TarAdapter().setGzipped(true));
    this.adapters.set('7z', new SevenZipAdapter());
  }

  /**
   * Inspect an archive from a stream source.
   */
  async inspect(
    source: AsyncIterable<Uint8Array> | NodeJS.ReadableStream,
    archiveName: string,
    archiveSize: number,
    options: InspectorOptions = {}
  ): Promise<InspectionManifest> {
    // We need to buffer the source for multiple passes (detect + list + extract)
    // For large archives, this could be optimized with a tee, but for security
    // inspection we accept the memory cost of buffering the archive once.
    const buffer = await this.bufferSource(source);
    
    // Detect format
    const format = detectFormat(new Uint8Array(buffer)) || formatFromExtension(archiveName);
    if (!format) {
      throw new Error(`Unable to detect archive format for ${archiveName}`);
    }
    
    const adapter = this.adapters.get(format);
    if (!adapter) {
      throw new Error(`No adapter for format: ${format}`);
    }
    
    // List entries
    const allEntries = await adapter.listEntries(toAsyncIterable(buffer));
    
    // Validate aggregate limits first
    const aggregateCheck = validateAggregateLimits(allEntries, this.limits);
    if (!aggregateCheck.allowed) {
      const manifest = createManifest(
        format, archiveName, archiveSize,
        allEntries, [], allEntries.map(e => ({ entry: e, reason: aggregateCheck.reason! })),
        this.limits, [aggregateCheck.reason!]
      );
      return manifest;
    }
    
    // Validate individual entries
    const seenPaths = new Set<string>();
    const acceptedEntries: ArchiveEntry[] = [];
    const rejectedEntries: Array<{ entry: ArchiveEntry; reason: string }> = [];
    const errors: string[] = [];
    
    // Check for duplicates first
    const duplicates = findDuplicatePaths(allEntries);
    for (const [normPath, dupEntries] of duplicates) {
      for (const entry of dupEntries) {
        rejectedEntries.push({ entry, reason: 'Duplicate normalized path' });
      }
    }
    
    for (const entry of allEntries) {
      const normPath = entry.path; // Already normalized by adapter
      if (duplicates.has(normPath)) continue; // Already rejected
      
      const validation = validateEntry(entry, this.limits, seenPaths);
      if (validation.allowed) {
        seenPaths.add(validation.normalizedPath!);
        acceptedEntries.push({ ...entry, path: validation.normalizedPath! });
      } else {
        rejectedEntries.push({ entry, reason: validation.reason! });
      }
    }
    
    // Create quarantine adapter
    const quarantine = options.useMemoryQuarantine
      ? new MemoryQuarantine()
      : new FilesystemQuarantine(options.quarantineRoot || './quarantine', {} as InspectionManifest);
    
    // Extract accepted entries
    const extractionErrors: string[] = [];
    for (const entry of acceptedEntries) {
      try {
        const stream = await adapter.extractEntry(toAsyncIterable(buffer), entry.path);
        if (stream) {
          await quarantine.writeEntry({
            path: entry.path,
            stream,
            size: entry.size,
            mtime: entry.mtime,
            mode: entry.mode,
          });
        } else {
          extractionErrors.push(`Failed to extract ${entry.path}: entry not found`);
        }
      } catch (e) {
        extractionErrors.push(`Failed to extract ${entry.path}: ${(e as Error).message}`);
      }
    }
    
    // Create and finalize manifest
    const manifest = createManifest(
      format, archiveName, archiveSize,
      allEntries, acceptedEntries, rejectedEntries,
      this.limits, extractionErrors
    );
    
    await quarantine.finalize(manifest);
    
    return manifest;
  }

  /**
   * Inspect from a file path.
   */
  async inspectFile(filePath: string, options: InspectorOptions = {}): Promise<InspectionManifest> {
    const fs = await import('node:fs/promises');
    const stats = await fs.stat(filePath);
    const fileHandle = await fs.open(filePath, 'r');
    
    try {
      const stream = fileHandle.createReadStream();
      return await this.inspect(stream, path.basename(filePath), stats.size, options);
    } finally {
      await fileHandle.close();
    }
  }

  private async bufferSource(source: AsyncIterable<Uint8Array> | NodeJS.ReadableStream): Promise<Buffer> {
    const chunks: Buffer[] = [];
    if (typeof source.pipe === 'function') {
      // Node.js stream
      await new Promise<void>((resolve, reject) => {
        source.on('data', (chunk: Buffer) => chunks.push(chunk));
        source.on('end', resolve);
        source.on('error', reject);
      });
    } else {
      // Async iterable
      for await (const chunk of source) {
        chunks.push(chunk instanceof Buffer ? chunk : Buffer.from(chunk));
      }
    }
    return Buffer.concat(chunks);
  }
}

/**
 * Convenience function for CLI usage.
 */
export async function inspectArchive(
  filePath: string,
  options: InspectorOptions = {}
): Promise<InspectionManifest> {
  const inspector = new ArchiveInspector(options);
  return inspector.inspectFile(filePath, options);
}

export { formatManifestSummary };
```

---

## `src/index.ts`

```typescript
/**
 * Archive Inspector CLI
 * 
 * Usage:
 *   npm run build && node dist/index.js <archive-file> [options]
 *   npx tsx src/index.ts <archive-file> [options]
 * 
 * Options:
 *   --quarantine <dir>    Quarantine output directory (default: ./quarantine)
 *   --memory              Use in-memory quarantine (for testing)
 *   --limits <json>       JSON string of security limits
 *   --json                Output manifest as JSON
 *   --help                Show help
 */

import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { ArchiveInspector, formatManifestSummary } from './core/inspector.js';
import type { InspectorOptions, SecurityLimits } from './core/inspector.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  
  if (args.includes('--help') || args.includes('-h') || args.length === 0) {
    printHelp();
    process.exit(0);
  }
  
  const filePath = args[0];
  const options: InspectorOptions = {};
  
  // Parse options
  for (let i = 1; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--quarantine' && i + 1 < args.length) {
      options.quarantineRoot = args[++i];
    } else if (arg === '--memory') {
      options.useMemoryQuarantine = true;
    } else if (arg === '--limits' && i + 1 < args.length) {
      try {
        options.limits = JSON.parse(args[++i]);
      } catch {
        console.error('Error: --limits requires valid JSON');
        process.exit(1);
      }
    } else if (arg === '--json') {
      options.jsonOutput = true;
    }
  }
  
  try {
    const inspector = new ArchiveInspector(options);
    const manifest = await inspector.inspectFile(filePath, options);
    
    if (options.jsonOutput) {
      console.log(JSON.stringify(manifest, null, 2));
    } else {
      console.log(formatManifestSummary(manifest));
    }
    
    // Exit with error code if any entries rejected
    if (manifest.rejectedEntries.length > 0 || manifest.errors.length > 0) {
      process.exit(1);
    }
  } catch (error) {
    console.error('Inspection failed:', (error as Error).message);
    process.exit(1);
  }
}

function printHelp(): void {
  console.log(`
Archive Inspector - Secure archive inspection and quarantine extraction

Usage:
  archive-inspector <archive-file> [options]

Options:
  --quarantine <dir>    Quarantine output directory (default: ./quarantine)
  --memory              Use in-memory quarantine (no filesystem writes)
  --limits <json>       Security limits as JSON (see below)
  --json                Output manifest as JSON
  --help, -h            Show this help

Default Limits:
  ${JSON.stringify({
    maxEntries: 1000,
    maxTotalSize: 104857600,
    maxCompressionRatio: 100,
    maxNestingDepth: 20,
    maxEntrySize: 52428800,
  }, null, 2)}

Example Limits JSON:
  {"maxEntries":500,"maxTotalSize":52428800,"maxCompressionRatio":50,"maxNestingDepth":10,"maxEntrySize":10485760}

Supported Formats:
  ZIP (.zip), TAR (.tar), TAR.GZ (.tar.gz, .tgz), 7z (.7z)

Exit Codes:
  0 - Success, all entries accepted
  1 - Rejected entries or errors occurred
  2 - Fatal error (format detection, I/O, etc.)
`);
}

// Add jsonOutput to options type
interface InspectorOptions {
  limits?: Partial<SecurityLimits>;
  quarantineRoot?: string;
  useMemoryQuarantine?: boolean;
  jsonOutput?: boolean;
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(2);
});
```

---

## `src/fixtures/generate-fixtures.ts`

```typescript
/**
 * Generate test fixtures for the archive inspector.
 * Creates:
 * - safe.zip: Clean archive with various file types
 * - traversal.tar.gz: Archive with path traversal attempts
 * - entry-limit.7z: Archive exceeding entry count limit
 * - ratio.zip: Archive with high compression ratio (zip bomb)
 */

import { createWriteStream } from 'node:fs';
import { pipeline } from 'node:stream/promises';
import { Readable } from 'node:stream';
import yauzl from 'yauzl';
import tar from 'tar-stream';
import zlib from 'node:zlib';
import { spawn } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { get7zzPath } from '../utils/7zz-path.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const FIXTURES_DIR = path.join(__dirname, '..', '..', 'fixtures');

async function ensureDir(dir: string): Promise<void> {
  const fs = await import('node:fs/promises');
  await fs.mkdir(dir, { recursive: true });
}

async function generateSafeZip(): Promise<void> {
  const fs = await import('node:fs/promises');
  const outputPath = path.join(FIXTURES_DIR, 'safe.zip');
  
  // Use yauzl for reading, but we need to create - use a simple approach
  // We'll use the `zip` command if available, or create manually
  const { createWriteStream } = await import('node:fs');
  const archiver = await import('archiver');
  
  const archive = archiver.default('zip', { zlib: { level: 6 } });
  const output = createWriteStream(outputPath);
  
  await pipeline(archive, output);
  
  // Add files
  archive.append('Hello, World!', { name: 'readme.txt' });
  archive.append('console.log("hello");', { name: 'src/main.js' });
  archive.append('export const x = 1;', { name: 'src/lib/utils.ts' });
  archive.append('{"name":"test"}', { name: 'package.json' });
  archive.append('', { name: 'empty/' }); // directory
  archive.append('symlink target', { name: 'src/link-target.txt' });
  // Note: archiver doesn't easily support symlinks in zip
  
  archive.finalize();
  await new Promise<void>((resolve, reject) => {
    output.on('close', resolve);
    output.on('error', reject);
  });
  
  console.log(`Created ${outputPath}`);
}

async function generateTraversalTarGz(): Promise<void> {
  const outputPath = path.join(FIXTURES_DIR, 'traversal.tar.gz');
  const pack = tar.pack();
  const gzip = zlib.createGzip();
  const output = createWriteStream(outputPath);
  
  await pipeline(pack, gzip, output);
  
  // Normal file
  pack.entry({ name: 'normal.txt', size: 12 }, 'Normal file');
  
  // Traversal attempts
  pack.entry({ name: '../etc/passwd', size: 10 }, 'traversal');
  pack.entry({ name: 'subdir/../../escape.txt', size: 10 }, 'escape');
  pack.entry({ name: 'absolute/path.txt', size: 10 }, 'absolute');
  pack.entry({ name: 'C:\\Windows\\system32\\cmd.exe', size: 10 }, 'windows');
  
  // Symlink escaping
  pack.entry({ name: 'link-to-root', type: 'symlink', linkname: '/' }, '');
  pack.entry({ name: 'link-to-parent', type: 'symlink', linkname: '../..' }, '');
  
  pack.finalize();
  await new Promise<void>((resolve, reject) => {
    output.on('close', resolve);
    output.on('error', reject);
  });
  
  console.log(`Created ${outputPath}`);
}

async function generateEntryLimit7z(): Promise<void> {
  const outputPath = path.join(FIXTURES_DIR, 'entry-limit.7z');
  const sevenzz = get7zzPath();
  
  // Create a temp directory with many files
  const fs = await import('node:fs/promises');
  const os = await import('node:os');
  const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), 'fixture-entries-'));
  
  try {
    // Create 1500 small files (default limit is 1000)
    for (let i = 0; i < 1500; i++) {
      await fs.writeFile(path.join(tmpDir, `file${i}.txt`), `content ${i}`);
    }
    
    // Pack with 7zz
    await new Promise<void>((resolve, reject) => {
      const proc = spawn(sevenzz, ['a', '-t7z', outputPath, `${tmpDir}/*`], {
        stdio: ['ignore', 'pipe', 'pipe'],
      });
      proc.on('close', code => code === 0 ? resolve() : reject(new Error(`7zz exited ${code}`)));
      proc.on('error', reject);
    });
  } finally {
    await fs.rm(tmpDir, { recursive: true, force: true });
  }
  
  console.log(`Created ${outputPath}`);
}

async function generateRatioZip(): Promise<void> {
  const fs = await import('node:fs/promises');
  const outputPath = path.join(FIXTURES_DIR, 'ratio.zip');
  
  // Create a zip bomb: highly compressed repetitive data
  // 10MB of zeros compresses to ~100KB (ratio ~100)
  // We'll create a smaller one that exceeds ratio 100
  
  const archiver = (await import('archiver')).default('zip', { zlib: { level: 9 } });
  const output = createWriteStream(outputPath);
  
  await pipeline(archiver, output);
  
  // Add a 1MB file of zeros (compresses extremely well)
  const zeros = Buffer.alloc(1024 * 1024, 0);
  archiver.append(zeros, { name: 'zeros.bin' });
  
  // Add a few more to push ratio
  for (let i = 0; i < 5; i++) {
    archiver.append(zeros, { name: `zeros${i}.bin` });
  }
  
  archiver.finalize();
  await new Promise<void>((resolve, reject) => {
    output.on('close', resolve);
    output.on('error', reject);
  });
  
  console.log(`Created ${outputPath}`);
}

async function main(): Promise<void> {
  await ensureDir(FIXTURES_DIR);
  
  console.log('Generating test fixtures...');
  
  await generateSafeZip();
  await generateTraversalTarGz();
  await generateEntryLimit7z();
  await generateRatioZip();
  
  console.log('All fixtures generated!');
}

main().catch(err => {
  console.error('Fixture generation failed:', err);
  process.exit(1);
});
```

---

## Installation & Execution Commands

```bash
# 1. Create project directory and files
mkdir archive-inspector && cd archive-inspector

# 2. Save all the above files to their respective paths:
#    package.json, tsconfig.json, src/**/*.ts

# 3. Install dependencies (exact versions from package.json)
npm install

# 4. Generate test fixtures
npm run fixtures

# 5. Build TypeScript
npm run build

# 6. Run inspector on safe fixture (should pass)
node dist/index.js fixtures/safe.zip --quarantine ./quarantine-safe

# 7. Run inspector on traversal fixture (should reject entries)
node dist/index.js fixtures/traversal.tar.gz --quarantine ./quarantine-traversal

# 8. Run inspector on entry-limit fixture (should reject aggregate)
node dist/index.js fixtures/entry-limit.7z --quarantine ./quarantine-entries

# 9. Run inspector on ratio fixture (should reject compression ratio)
node dist/index.js fixtures/ratio.zip --quarantine ./quarantine-ratio

# 10. Test with custom limits (JSON)
node dist/index.js fixtures/safe.zip --limits '{"maxEntries":10,"maxTotalSize":1000}'

# 11. Test JSON output
node dist/index.js fixtures/safe.zip --json

# 12. Test in-memory quarantine (no filesystem writes)
node dist/index.js fixtures/safe.zip --memory --json

# 13. Run tests
npm test
```

---

## API Explanation

### Archive APIs Used

| Format | Package | Key API | Streaming Behavior |
|--------|---------|---------|-------------------|
| **ZIP** | `yauzl` | `yauzl.fromBuffer(buf, {lazyEntries:true}, cb)` → `ZipFile` | Reads central directory first, then `openReadStream(entry, cb)` yields readable stream per entry on demand. No full extraction. |
| **TAR** | `tar-stream` | `tar.extract()` → `Extract` stream | Event-based: `on('entry', (header, stream, next))`. Header parsed, then entry stream flows. Call `next()` for next entry. |
| **TAR.GZ** | `tar-stream` + `zlib` | `zlib.createGunzip()` pipe to `tar.extract()` | Same as TAR, with gunzip decompression layer. |
| **7z** | `7zip-bin` + `child_process` | `7zz l -slt -ba` (list), `7zz e -so <archive> <file>` (extract to stdout) | Requires temp file (7zz doesn't support stdin for listing). Extraction streams to stdout. |

### Stream APIs Used

| Conversion | Method |
|------------|--------|
| Node.js `ReadableStream` → `AsyncIterable<Uint8Array>` | `Readable.from(stream)` + `for await (const chunk of stream)` |
| `AsyncIterable<Uint8Array>` → Node.js `Readable` | `Readable.from(iterable)` |
| Piping async iterable to writable | Manual `write()` + `end()` with promises |

### Security Validation Pipeline

1. **Format Detection** → Magic bytes (first 262 bytes) + extension fallback
2. **Entry Listing** → Adapter-specific streaming list (no extraction)
3. **Aggregate Limits** → Entry count, total size, compression ratio
4. **Per

