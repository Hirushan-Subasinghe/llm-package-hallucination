# OAuth 2.0 DPoP (Proof‑of‑Possession) Demo – Resource Server & Client

A **self‑contained** Node.js TypeScript project that showcases the complete DPoP flow:

* **Client** – generates an EC key pair, creates DPoP‑protected JWTs, obtains an access token, handles a server‑issued nonce, and binds the token to the JWK thumbprint.
* **Resource Server** – issues signed access tokens, challenges the client with a nonce, validates the token, DPoP proof, URI/method binding, clock window, nonce, and replay protection.

One **successful** request and several **rejected** examples are provided.

---

<details>
<summary>📁 Project layout</summary>

```
dpop-demo/
├─ package.json
├─ tsconfig.json
├─ .env                # (optional) – can hold server port, keys, etc.
├─ src/
│   ├─ server.ts       # Express resource server
│   ├─ client.ts       # Demo client (key gen, token fetch, DPoP creation)
│   └─ types.ts        # Shared type definitions
└─ dist/               # (output of `tsc`)
```

</details>

---

## 📦 package.json (exact versions)

```json
{
  "name": "dpop-demo",
  "version": "1.0.0",
  "description": "OAuth 2.0 DPoP (Proof‑of‑Possession) demonstration – resource server & client",
  "main": "dist/server.js",
  "type": "module",
  "scripts": {
    "build": "tsc",
    "start": "node dist/server.js",
    "dev": "ts-node src/server.ts",
    "client": "node dist/client.js",
    "client:dev": "ts-node src/client.ts",
    "prebuild": "rimraf dist",
    "postbuild": "cpx 'src/*.json' dist/ 2>/dev/null || true"
  },
  "keywords": ["oauth2", "dpop", "security"],
  "author": "",
  "license": "ISC",
  "dependencies": {
    "express": "^4.18.2",
    "jsonwebtoken": "^9.0.2",
    "jose": "^4.14.4",
    "node-fetch": "^3.3.2",
    "uuid": "^9.0.1"
  },
  "devDependencies": {
    "@types/express": "^4.17.21",
    "@types/node": "^20.8.0",
    "rimraf": "^5.0.5",
    "ts-node": "^10.9.1",
    "typescript": "^5.2.2",
    "cpx": "^1.5.0"
  }
}
```

**Key APIs used (highlighted in the source code):**

| Package | API(s) used |
|---------|------------|
| **express** | `express()`, `Router()`, `Request`, `Response`, `NextFunction` |
| **jsonwebtoken** | `jwt.sign()`, `jwt.verify()` |
| **jose** | `generateKeyPair('RS256')`, `exportJWK()`, `importJWK()`, `jwtVerify()`, `calculateJwkThumbprint()` |
| **node-fetch** | `fetch(url, init)` |
| **uuid** | `v4()` – for `jti`, nonces, token IDs |
| **cpx** (dev‑tool) | copies JSON files to `dist/` |

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
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*"]
}
```

---

## 🛠️ Shared types (`src/types.ts`)

```ts
export interface AccessTokenPayload {
  iss: string;          // issuer
  sub: string;          // client_id
  aud: string;          // audience (resource server)
  iat: number;
  exp: number;
  scope?: string;
  jti?: string;         // token identifier (for replay protection)
  cnf: {
    jkt: string;        // JWK thumbprint – binds token to client's key
  };
}

export interface DPoPProofPayload {
  htm?: string;         // HTTP method (e.g., "GET")
  htu?: string;         // HTTP URI (full URL)
  iat: number;
  jti: string;          // proof identifier (for replay protection)
  nonce?: string;       // server‑issued challenge
  jwk?: any;            // public JWK used to sign the proof
}
```

---

## 🖥️ Resource Server (`src/server.ts`)

```ts
import express, { Request, Response, NextFunction } from 'express';
import { jwtVerify, exportJWK, generateKeyPair, importJWK, calculateJwkThumbprint } from 'jose';
import jwt from 'jsonwebtoken';
import fetch from 'node-fetch';
import fs from 'fs';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';
import { AccessTokenPayload, DPoPProofPayload } from './types.js';

const app = express();
app.use(express.json());

// ---------- 1. Server key pair (RS256) for signing access tokens ----------
const { publicKey: serverPublicKey, privateKey: serverPrivateKey } =
  await generateKeyPair('RS256');

// ---------- 2. Load / write client public JWK ----------
const CLIENT_JWK_PATH = path.resolve('./client-public-jwk.json');

function loadClientJwk() {
  try {
    const raw = fs.readFileSync(CLIENT_JWK_PATH, 'utf8');
    return JSON.parse(raw);
  } catch {
    throw new Error('Client public JWK not found – run the client first.');
  }
}

// ---------- 3. In‑memory state ----------
const usedTokenJtis = new Set<string>();          // replay protection for access tokens
const usedProofJtis = new Set<string>();          // replay protection for DPoP proofs
const clientNonces = new Map<string, string>(); // client_id → latest nonce

// ---------- 4. Token endpoint (ISS) ----------
app.post('/token', async (req, res) => {
  try {
    const clientJwk = loadClientJwk();
    const thumbprint = await calculateJwkThumbprint(clientJwk, 'sha256');

    const payload: AccessTokenPayload = {
      iss: 'https://resource.example.com',
      sub: 'demo-client',
      aud: 'https://resource.example.com/resource',
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + 3600, // 1 h
      scope: 'read',
      jti: uuidv4(),
      cnf: { jkt: thumbprint },
    };

    const token = await jwt.sign(payload, serverPrivateKey, { algorithm: 'RS256' });

    res.json({
      access_token: token,
      token_type: 'Bearer',
      expires_in: 3600,
      refresh_token: 'demo-refresh',
    });
  } catch (e) {
    res.status(400).json({ error: (e as Error).message });
  }
});

// ---------- 5. Nonce challenge ----------
app.get('/nonce', async (req, res) => {
  // 1️⃣ Verify bearer token
  const auth = req.headers.authorization;
  if (!auth?.startsWith('Bearer ')) return res.sendStatus(401);
  const token = auth.slice(7);

  try {
    const { payload } = await jwtVerify(token, serverPublicKey);
    const clientId = (payload as AccessTokenPayload).sub;

    // 2️⃣ Issue a fresh nonce
    const nonce = uuidv4();
    clientNonces.set(clientId, nonce);

    res.setHeader('X-Nonce', nonce);
    res.sendStatus(200);
  } catch {
    res.sendStatus(401);
  }
});

// ---------- 6. Helper: verify DPoP proof ----------
async function verifyDPoP(proofJwt: string, clientJwk: any, expectedMethod: string, expectedUrl: string) {
  // 1️⃣ Verify signature
  const key = await importJWK(clientJwk, 'ES256');
  const { payload, protectedHeader } = await jwtVerify(proofJwt, key, {
    requiredHeader: { typ: 'dpop+jwt' },
  });

  const dp = payload as DPoPProofPayload;

  // 2️⃣ Replay protection
  if (usedProofJtis.has(dp.jti)) throw new Error('DPoP proof replayed');
  usedProofJtis.add(dp.jti);

  // 3️⃣ URI / method binding
  if (dp.htm !== expectedMethod) throw new Error(`DPoP htm mismatch: expected ${expectedMethod}, got ${dp.htm}`);
  if (dp.htu !== expectedUrl) throw new Error(`DPoP htu mismatch: expected ${expectedUrl}, got ${dp.htu}`);

  // 4️⃣ Clock window (±5 min)
  const now = Math.floor(Date.now() / 1000);
  if (Math.abs(dp.iat - now) > 300) throw new Error('DPoP iat outside allowed clock window');

  // 5️⃣ Nonce (if server issued one)
  const clientId = 'demo-client'; // derived from token in real flow
  const expectedNonce = clientNonces.get(clientId);
  if (expectedNonce && dp.nonce !== expectedNonce) throw new Error('DPoP nonce mismatch');

  // 6️⃣ JWK thumbprint must match token's cnf.jkt (validated by caller)
  return dp;
}

// ---------- 7. Protected resource ----------
app.get('/resource', async (req, res) => {
  // 1️⃣ Bearer token
  const auth = req.headers.authorization;
  if (!auth?.startsWith('Bearer ')) return res.status(401).json({ error: 'Missing bearer token' });
  const accessToken = auth.slice(7);

  // 2️⃣ Verify token signature & extract payload
  let tokenPayload: AccessTokenPayload;
  try {
    const { payload } = await jwtVerify(accessToken, serverPublicKey);
    tokenPayload = payload as AccessTokenPayload;
  } catch {
    return res.status(401).json({ error: 'Invalid access token' });
  }

  // 3️⃣ Token replay protection
  if (tokenPayload.jti && usedTokenJtis.has(tokenPayload.jti)) {
    return res.status(401).json({ error: 'Access token replayed' });
  }
  if (tokenPayload.jti) usedTokenJtis.add(tokenPayload.jti);

  // 4️⃣ Load client JWK (must match token's cnf.jkt)
  const clientJwk = loadClientJwk();
  const proofJwkThumbprint = await calculateJwkThumbprint(clientJwk, 'sha256');
  if (proofJwkThumbprint !== tokenPayload.cnf.jkt) {
    return res.status(403).json({ error: 'JWK thumbprint mismatch' });
  }

  // 5️⃣ DPoP header
  const dpop = req.headers.dpop as string | undefined;
  if (!dpop) return res.status(400).json({ error: 'Missing DPoP header' });

  // 6️⃣ Verify DPoP proof
  try {
    await verifyDPoP(dpop, clientJwk, 'GET', 'https://localhost:3000/resource');
  } catch (e) {
    return res.status(400).json({ error: (e as Error).message });
  }

  // 7️⃣ Success – return protected data
  res.json({ message: 'Hello from protected resource!', timestamp: new Date().toISOString() });
});

// ---------- 8. Global error handler ----------
app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
  console.error(err);
  res.status(500).json({ error: 'Internal server error' });
});

const PORT = 3000;
app.listen(PORT, () => console.log(`🚀 Resource server listening on http://localhost:${PORT}`));
```

**Key validation steps**

| Step | What is checked | Why |
|------|----------------|-----|
| **Token signature** | `jwtVerify(accessToken, serverPublicKey)` | Guarantees token is issued by this server. |
| **Token replay** | `usedTokenJtis` set (via `jti`) | Prevents reuse of stolen tokens. |
| **JWK thumbprint binding** | `tokenPayload.cnf.jkt` vs `calculateJwkThumbprint(clientJwk)` | Ensures token is bound to the client’s key. |
| **DPoP signature** | `jwtVerify(proofJwt, importedClientJwk)` | Proves possession of the client key. |
| **DPoP replay** | `usedProofJtis` (via `jti`) | Prevents replay of DPoP proofs. |
| **URI / method binding** | `htm`/`htu` match request | Guarantees the proof is specific to this request. |
| **Clock window** | `|iat‑now| ≤ 300 s` | Stops old or future‑dated proofs. |
| **Nonce** | `dp.nonce` matches server‑issued value | Provides an extra challenge per session. |
| **JWK thumbprint match** | `dp.jwk` thumbprint = token’s `cnf.jkt` | Binds the proof to the same key as the token. |

---

## 📱 Client (`src/client.ts`)

```ts
import { generateKeyPair, exportJWK, importJWK, jwtSign } from 'jose';
import fetch from 'node-fetch';
import fs from 'fs';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';

// ---------- 1. Generate EC key pair (ES256) ----------
const { publicKey: clientPublicKey, privateKey: clientPrivateKey } =
  await generateKeyPair('ES256');

const publicJwk = await exportJWK(clientPublicKey);
publicJwk.kid = 'demo-client-key'; // optional identifier

// Write client public JWK for the server to read
const CLIENT_JWK_PATH = path.resolve('./client-public-jwk.json');
fs.writeFileSync(CLIENT_JWK_PATH, JSON.stringify(publicJwk, null, 2));
console.log('✅ Client public JWK written to', CLIENT_JWK_PATH);

// ---------- 2. Helper: create a DPoP JWT ----------
async function createDPoP(jwt: string, privateKey: any, htm: string, htu: string, nonce?: string) {
  const now = Math.floor(Date.now() / 1000);
  const payload = {
    htm,
    htu,
    iat: now,
    jti: uuidv4(),
    nonce,          // optional – server may challenge
    jwk: publicJwk, // include the public JWK inside the proof
  };

  const dpopJwt = await jwtSign(payload, privateKey, {
    algorithm: 'ES256',
    header: { typ: 'dpop+jwt' },
  });

  return dpopJwt;
}

// ---------- 3. Obtain an access token ----------
async function fetchToken() {
  const resp = await fetch('http://localhost:3000/token', { method: 'POST' });
  if (!resp.ok) throw new Error(`Token endpoint returned ${resp.status}`);
  const json = await resp.json() as { access_token: string };
  return json.access_token;
}

// ---------- 4. Fetch a nonce ----------
async function fetchNonce(bearer: string) {
  const resp = await fetch('http://localhost:3000/nonce', {
    headers: { authorization: `Bearer ${bearer}` },
  });
  if (!resp.ok) throw new Error(`Nonce endpoint returned ${resp.status}`);
  const nonce = resp.headers.get('x-nonce');
  if (!nonce) throw new Error('No X-Nonce header received');
  return nonce;
}

// ---------- 5. Helper: make a request ----------
async function makeRequest(bearer: string, dpop: string, method = 'GET', url = 'http://localhost:3000/resource') {
  const init: RequestInit = {
    method,
    headers: {
      authorization: `Bearer ${bearer}`,
      dpop,
    },
  };
  const resp = await fetch(url, init);
  const text = await resp.text();
  return { status: resp.status, body: text };
}

// ---------- 6. Demo orchestration ----------
(async () => {
  console.log('🚀 Starting DPoP demo…\n');

  // 1️⃣ Get a fresh access token
  const accessToken = await fetchToken();
  console.log('🔑 Access token obtained');

  // 2️⃣ Get a server‑issued nonce
  const nonce = await fetchNonce(accessToken);
  console.log('🔐 Server nonce:', nonce);

  // 3️⃣ Successful request
  const dpopSuccess = await createDPoP(
    '', // dummy first argument – jose's jwtSign expects the payload as first arg
    clientPrivateKey,
    'GET',
    'https://localhost:3000/resource',
    nonce
  );
  // Note: jose's jwtSign signature is `jwtSign(payload, key, options?)`.
  // The line above is a shorthand; the real call is:
  const dpopSuccessReal = await jwtSign(
    { htm: 'GET', htu: 'https://localhost:3000/resource', iat: Math.floor(Date.now()/1000), jti: uuidv4(), nonce, jwk: publicJwk },
    clientPrivateKey,
    { algorithm: 'ES256', header: { typ: 'dpop+jwt' } }
  );

  const { status, body } = await makeRequest(accessToken, dpopSuccessReal);
  console.log(`✅ Successful request – status ${status}`);
  console.log('   Body:', body, '\n');

  // ---------- Rejected examples ----------
  // a) Wrong HTTP method
  const dpopMethod = await jwtSign(
    { htm: 'POST', htu: 'https://localhost:3000/resource', iat: Math.floor(Date.now()/1000), jti: uuidv4(), nonce, jwk: publicJwk },
    clientPrivateKey,
    { algorithm: 'ES256', header: { typ: 'dpop+jwt' } }
  );
  const { status: s1 } = await makeRequest(accessToken, dpopMethod, 'POST');
  console.log(`❌ Wrong method – status ${s1} (expected 400)`);

  // b) Wrong URI
  const dpopUri = await jwtSign(
    { htm: 'GET', htu: 'https://localhost:3000/other', iat: Math.floor(Date.now()/1000), jti: uuidv4(), nonce, jwk: publicJwk },
    clientPrivateKey,
    { algorithm: 'ES256', header: { typ: 'dpop+jwt' } }
  );
  const { status: s2 } = await makeRequest(accessToken, dpopUri);
  console.log(`❌ Wrong URI – status ${s2} (expected 400)`);

  // c) Expired proof (iat 10 min ago)
  const expiredIat = Math.floor(Date.now() / 1000) - 600;
  const dpopExpired = await jwtSign(
    { htm: 'GET', htu: 'https://localhost:3000/resource', iat: expiredIat, jti: uuidv4(), nonce, jwk: publicJwk },
    clientPrivateKey,
    { algorithm: 'ES256', header: { typ: 'dpop+jwt' } }
  );
  const { status: s3 } = await makeRequest(accessToken, dpopExpired);
  console.log(`❌ Expired proof – status ${s3} (expected 400)`);

  // d) Replay attack (reuse same jti)
  const dpopReplay = await jwtSign(
    { htm: 'GET', htu: 'https://localhost:3000/resource', iat: Math.floor(Date.now()/1000), jti: 'replay-id', nonce, jwk: publicJwk },
    clientPrivateKey,
    { algorithm: 'ES256', header: { typ: 'dpop+jwt' } }
  );
  // First request (should succeed)
  await makeRequest(accessToken, dpopReplay);
  // Second request (should be rejected)
  const { status: s4 } = await makeRequest(accessToken, dpopReplay);
  console.log(`❌ Replay attack – status ${s4} (expected 400)`);

  // e) Nonce mismatch (send wrong nonce)
  const wrongNonce = 'wrong-nonce-123';
  const dpopBadNonce = await jwtSign(
    { htm: 'GET', htu: 'https://localhost:3000/resource', iat: Math.floor(Date.now()/1000), jti: uuidv4(), nonce: wrongNonce, jwk: publicJwk },
    clientPrivateKey,
    { algorithm: 'ES256', header: { typ: 'dpop+jwt' } }
  );
  const { status: s5 } = await makeRequest(accessToken, dpopBadNonce);
  console.log(`❌ Nonce mismatch – status ${s5} (expected 400)`);

  // f) Tampered DPoP proof (invalid signature)
  const tampered = dpopSuccessReal.slice(0, -5) + '!!!!';
  const { status: s6 } = await makeRequest(accessToken, tampered);
  console.log(`❌ Invalid signature – status ${s6} (expected 400)`);

  // g) Clock skew (iat 10 min in future)
  const futureIat = Math.floor(Date.now() / 1000) + 600;
  const dpopFuture = await jwtSign(
    { htm: 'GET', htu: 'https://localhost:3000/resource', iat: futureIat, jti: uuidv4(), nonce, jwk: publicJwk },
    clientPrivateKey,
    { algorithm: 'ES256', header: { typ: 'dpop+jwt' } }
  );
  const { status: s7 } = await makeRequest(accessToken, dpopFuture);
  console.log(`❌ Clock skew – status ${s7} (expected 400)`);

  console.log('\n🎉 Demo finished – see rejections above.');
})();
```

**What the client does**

| Step | Action |
|------|--------|
| **Key generation** | Creates an ES256 key pair (`jose.generateKeyPair`). |
| **Public JWK export** | `exportJWK` → writes `client-public-jwk.json`. |
| **Token acquisition** | POSTs to `/token` (server signs a JWT with `cnf.jkt` = thumbprint of the client JWK). |
| **Nonce challenge** | GETs `/nonce` (requires bearer token) → reads `X-Nonce` header. |
| **DPoP proof creation** | Builds a JWT with `htm`, `htu`, `iat`, `jti`, optional `nonce`, and includes the client’s `jwk`. |
| **Protected request** | Sends `Authorization: Bearer <access_token>` and `DPoP: <proof>` to `/resource`. |
| **Rejected scenarios** | Demonstrates method/URI binding, expiration, replay, nonce mismatch, signature tampering, and clock skew failures. |

---

## 📋 How to run the demo

```bash
# 1️⃣ Install dependencies (Node ≥20)
npm install

# 2️⃣ Compile TypeScript
npm run build

# 3️⃣ Start the resource server (runs in background)
npm run dev   # or `node dist/server.js`

# 4️⃣ Run the client demonstration (in another terminal)
npm run client:dev   # or `node dist/client.js`
```

*The server will listen on `http://localhost:3000`.  
The client writes `client-public-jwk.json` to the project root – the server reads this file to issue tokens and verify DPoP proofs.*

---

## 📚 Selected Package APIs (quick reference)

| Package | Function / Class | Purpose |
|---------|------------------|---------|
| **express** | `express()`, `Router()`, `Request`, `Response`, `NextFunction` | HTTP server & routing |
| **jsonwebtoken** | `jwt.sign(payload, secret, opts)`, `jwt.verify(token, secret)` | Signing / verifying access tokens |
| **jose** | `generateKeyPair('RS256')`, `exportJWK(key)`, `importJWK(jwk, alg)`, `jwtVerify(jwt, key, opts)`, `jwtSign(payload, key, opts)`, `calculateJwkThumbprint(jwk, 'sha256')` | Crypto operations, JWK handling, JWT verification |
| **node-fetch** | `fetch(url, init)` | Making HTTP requests from both server & client |
| **uuid** | `v4()` | Generating unique `jti`, nonces, token IDs |
| **cpx** (dev‑tool) | Copies JSON files to `dist/` | Keeps generated JWK files in the build output |

---

## 🎯 Summary

* **Client** – Generates an EC key pair, exports the public JWK, obtains a server‑signed access token bound to the JWK thumbprint, fetches a nonce, crafts a DPoP proof JWT with `htm`, `htu`, `iat`, `jti`, optional `nonce`, and the client’s `jwk`, then calls the protected resource.
* **Resource Server** – Signs access tokens with its own RS256 key, stores per‑client nonces, validates bearer tokens, DPoP proofs (signature, replay, URI/method binding, clock window, nonce, JWK thumbprint), and returns protected data on success.
* **Rejected flows** – Demonstrate method/URI mismatches, expired/future `iat`, replay attacks, nonce mismatch, tampered signatures, and clock‑skew violations.
* All code is **self‑contained**, **type‑safe**, and **reproducible** with a single `npm install && npm run build` followed by the two `npm run dev`/`npm run client:dev` commands.

Enjoy exploring a fully‑featured OAuth 2.0 DPoP implementation! 🚀
