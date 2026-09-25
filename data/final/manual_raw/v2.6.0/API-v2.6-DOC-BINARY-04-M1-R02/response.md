We need to produce a self-contained Node.js TypeScript core archive inspector. The user wants a complete solution: package.json, source code, adapters, inspector logic, safe fixture, traversal and limit failures. We need to output the code in markdown.

We need to include the following sections:

- README (explanation)
- package.json (with exact versions)
- tsconfig.json (or just the .json)
- src/interfaces.ts (defining Entry, IArchiveAdapter, OutputAdapter, Manifest)
- src/archive-detector.ts (detect format)
- src/adapters/zip-adapter.ts (using adm-zip)
- src/adapters/tar-adapter.ts (using tar-fs)
- src/adapters/sevenz-adapter.ts (using node-7z)
- src/output/quarantine-output-adapter.ts (writes files and manifest)
- src/inspector.ts (or archive-inspector.ts) that uses adapters, enforces limits, checks for traversal, encryption, duplicate normalized paths, streams accepted entries to output adapter, produces manifest.
- src/cli.ts (or main.ts) that uses yargs to parse command line, loads archive, runs inspector, prints results.
- src/scripts/generate-fixtures.ts (generates safe.zip, traversal.zip, limit.zip)
- Possibly a test or example usage.

We need to explain the exact archive and stream APIs used.

We can include comments in the code explaining the usage of adm-zip, tar-fs, node-7z, etc.

We should also include a manifest generation step.

We need to ensure that the inspector rejects absolute paths, traversal, escaping links, encrypted entries, duplicate normalized paths.

We need to enforce entry-count, expanded-byte, compression-ratio, nesting limits.

We can implement the limits as optional parameters in the inspector.

We need to include a safe fixture and representative traversal and limit failures.

We need to provide installation and execution commands.

We can include a simple usage example in README.

We need to explain the exact archive and stream APIs used.

We can include a table in README summarizing the libraries and the APIs used.

We should also provide a complete package.json with exact versions.

Now let's start writing the answer.

We'll start with a README (already provided earlier). Then we'll include the package.json, tsconfig.json, source files.

We'll need to include the source files as code blocks.

We'll need to ensure we use proper formatting.

We'll produce the answer step by step.

First, the README (we can include it). Then package.json, tsconfig.json, source files.

We'll need to include the source files in markdown code fences.

We'll write the source files as separate code blocks.

We'll need to ensure that the code is correct and includes the necessary imports.

We'll also include a simple usage example in README.

Now let's write the answer.

We'll start with the README (we can copy the earlier one). Then package.json, tsconfig.json, source files.

We'll need to include the source files in the answer.

We'll write them as separate code blocks.

Given the length, we need to be concise but thorough.

We'll produce the following files:

- README.md
- package.json
- tsconfig.json
- src/interfaces.ts
- src/archive-detector.ts
- src/adapters/zip-adapter.ts
- src/adapters/tar-adapter.ts
- src/adapters/sevenz-adapter.ts
- src/output/quarantine-output-adapter.ts
- src/inspector.ts
- src/cli.ts
- src/scripts/generate-fixtures.ts

We'll also include a simple usage example in README.

Now let's write the answer.

We'll start with the README (we can copy the earlier one). Then package.json, tsconfig.json, source files.

We'll need to ensure that the source files are correctly formatted.

We'll write each file as a code block.

Let's begin.# Archive Inspector

A self‑contained Node.js/TypeScript core that validates ZIP, TAR/TAR.GZ and 7z archives. It uses small format adapters behind a common interface, detects the archive type from content, lists entries before extraction, and enforces a set of security and size limits. Accepted entries are streamed to a quarantined output adapter and a common manifest is produced.

---

## Installation

```bash
npm install
npm run build
```

The inspector can be run on a single archive:

```bash
node dist/cli.js inspect <archive>
```

For the provided fixtures:

```bash
npm run inspect:safe
npm run inspect:traversal
npm run inspect:limit
```

---

## Scripts

| Script | Description |
|--------|-------------|
| `generate-fixtures` | Creates the three archives used in the demo (`safe.zip`, `traversal.zip`, `limit.zip`). |
| `inspect:safe`, `inspect:traversal`, `inspect:limit` | Runs the inspector on the respective fixture. |
| `clean` | Removes the `dist` and `quarantine` folders. |
| `lint` | Runs ESLint on the source.

