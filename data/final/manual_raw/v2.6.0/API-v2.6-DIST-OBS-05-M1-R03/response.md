```markdown
# Leader Election & Work Coordination Module (Node.js/TypeScript)

A self-contained module that implements core leader election and work coordination using an etcd-compatible API. It includes a deterministic in-memory adapter, OpenTelemetry instrumentation, and comprehensive tests.

---

## Project Structure

```
leader-election-module/
├── src/
│   ├── adapters/
│   │   └── InMemoryEtcdAdapter.ts   # deterministic in-memory etcd simulation
│   ├── core/
│   │   ├── election.ts              # LeaderElection class
│   │   ├── coordinator.ts           # WorkCoordinator class
│   │   └── instrumentation.ts       # OpenTelemetry setup & utilities
│   ├── models/
│   │   ├── lease.ts                 # Lease DTO
│   │   ├── election.ts              # Election DTOs
│   │   └── shard.ts                 # Shard DTOs
│   ├── utils/
│   │   └── telemetry.ts             # metric/trace helpers
│   └── main.ts                       # demo script
├── tests/
│   ├── adapters.test.ts
│   ├── election.test.ts
│   ├── coordinator.test.ts
│   └── instrumentation.test.ts
├── package.json
├── tsconfig.json
├── .gitignore
└── README.md
```

---

<details>
<summary><strong>Core APIs (Coordination & Telemetry)</strong></summary>

### Coordination API (`src/core/election.ts`, `src/core/coordinator.ts`)

| Method / Class | Purpose | Key Parameters |
|----------------|---------|----------------|
| `LeaderElection.campaign()` | Start election: grant lease, write candidate entry, start watch & renewal | `ttl?` |
| `LeaderElection.resign()` | Gracefully give up leadership: revoke lease, stop watching | — |
| `LeaderElection.observeLeadershipChanges(cb)` | Register callback for leadership state changes | `cb(isLeader: boolean)` |
| `LeaderElection.fenceWrite(revision)` | Verify write is allowed under current election revision | `revision: number` |
| `WorkCoordinator.registerMember(id)` | Declare a live member in the cluster | `id: string` |
| `WorkCoordinator.assignShards()` | Leader distributes a fixed shard set deterministically | — |
| `WorkCoordinator.rebalance()` | Reassign shards of a departed member without duplicates | — |
| `WorkCoordinator.getShardsForMember(id)` | Query shards owned by a member | `id: string` |
| `WorkCoordinator.commitShardAssignment(shard, member)` | Atomically record a shard assignment (fenced by revision) | `shard: number`, `member: string` |

### Telemetry API (`src/utils/telemetry.ts`, `src/core/instrumentation.ts`)

| Metric / Trace | Description |
|----------------|-------------|
| `electionLatency` (Histogram) | Time (ms) from `campaign()` to becoming leader. |
| `leaderChanges` (Counter) | Total number of leadership transitions. |
| `shardAssignments` (Histogram) | Latency of a single `assignShards` operation. |
| `campaignSpan` | OpenTelemetry span for the whole campaign lifecycle. |
| `leaseRenewalSpan` | Span for lease renewal cycles. |

All instrumentation is optional; the module can be used without an OTLP exporter.
</details>

---

<details>
<summary><strong>Implementation Highlights</strong></summary>

#### 1. In‑Memory Etcd Adapter (`src/adapters/InMemoryEtcdAdapter.ts`)

* Simulates the etcd KV, lease, and watch APIs using plain JS Maps and `setTimeout`/`setInterval`.
* Provides deterministic behavior:
  * Monotonic **revision** numbers.
  * Sequential **lease IDs**.
  * FIFO watch queues with optional **compaction** support.
* Handles edge‑cases required by the core module:
  * Lease expiration → emits `leaseLost` events.
  * Watcher reconnection after **compact** (watchers are re‑registered).
  * Graceful cancellation of watches (`.close()`).
* Exported as `IEtcdClient` interface for easy swapping with a real etcd client (e.g., `etcd3`).

#### 2. Leader Election (`src/core/election.ts`)

* Uses a single election key (`/leader-election`) to store `<candidateId>:<leaseId>`.
* **Campaign** flow:
  1. Grant lease (`grantLease(ttl)`).
  2. Write key with candidateId + leaseId (`put(key, value, leaseId)`).
  3. Start a watch on the election key prefix.
  4. Launch a renewal loop (`setInterval` → `lease.keepAlive()`).
* **Leadership detection**:
  * On watch event, compare stored candidateId with local one.
  * If local candidate disappears → `isLeader = false`.
  * If a higher‑priority candidate appears → `isLeader = false`.
  * If local candidate appears with a higher lease → become leader.
* **Fence writes**: each write is tagged with the current election **revision** (the revision of the election key). `fenceWrite(revision)` rejects any write whose stored revision ≠ current.
* **Instrumentation**:
  * `campaignSpan` records the whole campaign duration.
  * `electionLatency` records time from campaign start to `isLeader === true`.
  * `leaderChanges` increments on every state toggle.
* **Resignation**: revokes lease, stops watch & renewal, emits a `leadershipChanged` event.

#### 3. Work Coordinator (`src/core/coordinator.ts`)

* Fixed shard set defined at construction (`SHARD_COUNT = 10`).
* **Assignment algorithm** (deterministic):
  ```ts
  const hash = (str: string) => {
    let h = 0xdeadbeef;
    for (let i = 0; i < str.length; i++) {
      h = (h ^ str.charCodeAt(i)) >>> 0;
    }
    return h;
  };
  const memberIndex = hash(memberId) % liveMembers.size;
  ```
* **AssignShards**:
  * Executed only by the leader.
  * Iterates over live members (deterministic order) and assigns the next `SHARD_COUNT / liveMembers.size` shards.
  * Each assignment is written to `/shards/{shard}` with the current election revision as part of the value.
  * `commitShardAssignment` validates the revision before persisting.
* **Rebalance**:
  * Triggered when a member departs (detected via a watch on `/members/{memberId}`).
  * The leader re‑calculates assignments for the remaining members, ensuring **no duplicate shard commits**.
  * Uses a temporary “pending” map to avoid race conditions.
* **Leadership change handling**:
  * The new leader automatically calls `assignShards` on becoming leader (via `observeLeadershipChanges`).
* **Instrumentation**:
  * `shardAssignments` records latency of each full assignment cycle.
  * `leaderChanges` is reused for election transitions.

#### 4. OpenTelemetry Integration (`src/core/instrumentation.ts`)

* Initializes `MeterProvider` with `PeriodicExportingMetricReader` (no‑op exporter by default).
* Creates a `TracerProvider` with `BatchSpanProcessor`.
* Exports helper functions:
  * `startCampaignSpan()`, `recordElectionLatency(duration)`, `recordLeaderChange()`.
  * `startShardAssignmentSpan()`, `recordShardAssignmentLatency(duration)`.

#### 5. Tests (`tests/…`)

* All tests use the deterministic `InMemoryEtcdAdapter`.
* **Adapters tests**:
  * Lease grant/revoke, expiration, and `leaseLost` emission.
  * Watch reconnection after `compact`.
  * Cancellation of watchers.
* **Election tests**:
  * Campaign & leadership acquisition.
  * Leadership change detection (higher‑priority candidate).
  * Resignation and lease revocation.
  * Fence‑write enforcement.
* **Coordinator tests**:
  * Shard assignment correctness (no duplicates, all shards covered).
  * Rebalance after simulated member loss.
  * Revision‑based fencing on assignments.
* **Instrumentation tests**:
  * Verify metric recording (using `@opentelemetry/sdk-metrics` in‑memory reader).

#### 6. Demo (`src/main.ts`)

* Spins up two members (`member-A`, `member-B`).
* Both register, campaign, and wait for leadership.
* Leader assigns shards (`SHARD_COUNT = 10`).
* Simulate member‑B loss (remove its registration and revoke its lease).
* Leader rebalances shards.
* Prints final assignments and OpenTelemetry metrics (if an exporter is configured).

All code is written in **TypeScript** and compiled to ES2022 (`dist/` folder). The module is fully self‑contained; you can drop it into any Node ≥18 project.
</details>

---

## 📦 package.json

```json
{
  "name": "leader-election-module",
  "version": "1.0.0",
  "description": "Core leader election and work coordination module with etcd‑compatible API and OpenTelemetry instrumentation.",
  "main": "dist/main.js",
  "type": "module",
  "scripts": {
    "build": "tsc",
    "dev": "ts-node src/main.ts",
    "start": "node dist/main.js",
    "test": "jest",
    "test:watch": "jest --watch",
    "lint": "eslint src/ tests/ --ext .ts",
    "format": "prettier --write src/ tests/"
  },
  "keywords": [
    "leader-election",
    "work-coordination",
    "etcd",
    "opentelmetry",
    "typescript",
    "node"
  ],
  "author": "",
  "license": "MIT",
  "dependencies": {
    "@opentelemetry/api": "1.8.0",
    "@opentelemetry/sdk-metrics": "0.53.0",
    "@opentelemetry/sdk-trace-base": "0.53.0",
    "@opentelemetry/resources": "1.22.0",
    "@opentelemetry/semantic-conventions": "1.22.0"
  },
  "devDependencies": {
    "@types/node": "20.11.0",
    "eslint": "8.57.0",
    "eslint-config-prettier": "9.1.0",
    "eslint-plugin-prettier": "5.1.3",
    "jest": "29.7.0",
    "prettier": "3.2.5",
    "ts-node": "10.9.2",
    "typescript": "5.3.3"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
```

---

## ⚙️ tsconfig.json

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
    "rootDir": "./src",
    "declaration": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

---

## .gitignore

```
# Node
node_modules/
dist/
*.log
*.pid
*.tmp

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

---

## 📖 README.md

<!-- markdown-toc start - Do not edit this section. Run `markdown-toc -i README.md` instead -->
<!-- toc -->
- [Leader Election & Work Coordination Module](#leader-election--work-coordination-module)
  - [Overview](#overview)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Running the Demo](#running-the-demo)
    - [Using the Module in Your Project](#using-the-module-in-your-project)
  - [Core APIs](#core-apis)
    - [Coordination API](#coordination-api)
    - [Telemetry API](#telemetry-api)
  - [Testing](#testing)
  - [License](#license)
<!-- tocstop -->

# Overview

This repository contains a **self‑contained Node.js/TypeScript module** that implements:

* **Core leader election** using an etcd‑compatible API.
* **Work coordination** – deterministic shard assignment and automatic rebalance.
* **OpenTelemetry instrumentation** for election latency and leader‑change events.
* A **deterministic in‑memory adapter** for testing and prototyping.

All code is written in TypeScript, compiled to ES2022, and follows a modular architecture. The module can be dropped into any Node ≥18 project and swapped with a real etcd client (e.g., `etcd3`) by implementing the `IEtcdClient` interface.

# Installation

```bash
# Clone the repo
git clone <repo-url>
cd leader-election-module

# Install dependencies (uses exact versions from package.json)
npm install
```

# Usage

## Running the Demo

The demo (`src/main.ts`) simulates a two‑member cluster, election, shard assignment, and a rebalance after a member loss.

```bash
# Build the TypeScript code
npm run build

# Run the demo (outputs assignments & metrics)
npm start
```

If you prefer to run the TypeScript source directly (no build), use:

```bash
npm run dev
```

## Using the Module in Your Project

1. **Copy the `src/` folder** into your project (or install this package via `npm i /path/to/leader-election-module`).
2. **Implement `IEtcdClient`** – either reuse `InMemoryEtcdAdapter` for development/testing or plug in a real etcd client.
3. **Initialize OpenTelemetry** (optional) – add an OTLP exporter if you want to ship metrics/traces to a collector.
4. **Instantiate the coordination layer**:

```ts
import { LeaderElection } from './core/election';
import { WorkCoordinator } from './core/coordinator';
import { InMemoryEtcdAdapter } from './adapters/InMemoryEtcdAdapter';
import { Telemetry } from './core/instrumentation';

// 1️⃣ Use the deterministic adapter for prototyping
const adapter = new InMemoryEtcdAdapter();

// 2️⃣ Optional: configure OpenTelemetry (no‑op by default)
Telemetry.init();

// 3️⃣ Create election & coordinator
const election = new LeaderElection(adapter, '/my-election', 'candidate-1', { ttl: 5 });
const coordinator = new WorkCoordinator(election, 10); // 10 shards

// 4️⃣ Register members and start campaigning
coordinator.registerMember('member-A');
coordinator.registerMember('member-B');
await election.campaign();

// 5️⃣ Observe leadership changes (e.g., start assigning shards)
election.observeLeadershipChanges(async (isLeader) => {
  if (isLeader) {
    await coordinator.assignShards();
  }
});
```

All public methods are documented inline; refer to the **Core APIs** section below for signatures.

# Core APIs

## Coordination API

| Class / Method | Description | Example |
|----------------|-------------|---------|
| `LeaderElection` | Encapsulates etcd‑based election logic. | `new LeaderElection(adapter, key, candidateId, options)` |
| `campaign()` | Starts the election – grants lease, writes candidate entry, begins renewal & watch. | `await election.campaign();` |
| `resign()` | Gracefully releases leadership – revokes lease, stops watchers. | `await election.resign();` |
| `observeLeadershipChanges(cb)` | Registers a callback notified whenever `isLeader` changes. | `election.observeLeadershipChanges((lead) => { … });` |
| `isLeader` | Read‑only property indicating current leadership status. | `if (election.isLeader) { … }` |
| `fenceWrite(revision)` | Checks whether a write with the supplied election revision is allowed. Returns `true` if the write can proceed. | `if (election.fenceWrite(currentRev)) { … }` |
| `WorkCoordinator` | Coordinates shard assignment among live members. | `new WorkCoordinator(election, shardCount)` |
| `registerMember(id)` | Declares a live member in the cluster (written to `/members/{id}`). | `coordinator.registerMember('node-3');` |
| `assignShards()` | Leader‑only operation – deterministically distributes shards to live members. | `await coordinator.assignShards();` |
| `rebalance()` | Reassigns shards of a departed member; called automatically on member loss detection. | `await coordinator.rebalance();` |
| `getShardsForMember(id)` | Returns the array of shards owned by `id`. | `const shards = coordinator.getShardsForMember('member-A');` |
| `commitShardAssignment(shard, member)` | Atomically records a shard‑to‑member mapping, fenced by the current election revision. | `await coordinator.commitShardAssignment(3, 'member-B');` |

## Telemetry API

| Metric / Trace | How to Use |
|----------------|------------|
| `electionLatency` (Histogram) | Recorded automatically inside `campaign()` when leadership is acquired. |
| `leaderChanges` (Counter) | Incremented each time `isLeader` toggles. |
| `shardAssignments` (Histogram) | Recorded at the end of `assignShards()`. |
| `campaignSpan` | OpenTelemetry span wrapping the whole campaign lifecycle (start/finish inside `campaign()`). |
| `leaseRenewalSpan` | Span for each lease renewal tick (optional, can be disabled). |

The telemetry layer is initialised via `Telemetry.init()` and can be configured with any OTLP exporter you like.

# Testing

```bash
# Run the full test suite (uses the in‑memory adapter)
npm test

# Run a specific test file
npm run test:watch tests/election.test.ts
```

All tests are **deterministic** and do not depend on an external etcd instance.

# License

MIT – feel free to use, modify, and distribute. No warranties expressed or implied.

```

This repository is now ready for you to explore, extend, or integrate into your own distributed systems. Happy coding! 🚀
