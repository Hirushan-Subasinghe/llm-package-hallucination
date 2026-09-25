```json
{
  "name": "distributed-lease-demo",
  "version": "0.1.0",
  "description": "Self‑contained TypeScript module that simulates a distributed lease using three independent Redis nodes, supporting bounded‑TTL acquisition, drift allowance, quorum decisions, renewal, compare‑and‑delete release, monotonic fencing tokens, and a protected resource that rejects stale holders. Includes focused deterministic concurrency tests.",
  "main": "dist/lease/lease.js",
  "scripts": {
    "clean": "rimraf dist",
    "build": "tsc",
    "prebuild": "npm run clean",
    "start": "node dist/lease/lease.js",
    "test": "jest",
    "test:watch": "jest --watch",
    "dev": "ts-node src/lease/lease.ts"
  },
  "keywords": [
    "distributed",
    "lease",
    "redis",
    "quorum",
    "fencing",
    "typescript"
  ],
  "author": "",
  "license": "MIT",
  "dependencies": {
    "redis": "^4.6.0",
    "distributed-lock": "^2.0.0",
    "uuid": "^9.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0",
    "jest": "^29.0.0",
    "ts-jest": "^29.0.0",
    "@types/jest": "^29.0.0",
    "sinon": "^18.0.0",
    "rimraf": "^5.0.0"
  }
}
```

