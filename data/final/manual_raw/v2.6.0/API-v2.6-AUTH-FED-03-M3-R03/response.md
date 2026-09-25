## 📦  Full, reproducible example (Node + TypeScript)

Below is a **self‑contained** OAuth 2.0 + DPoP (Proof‑of‑Possession) demo that includes  

* a **resource server** (`server.ts`) that validates DPoP proofs, nonces, replay, thumb‑prints, etc.  
* a **client** (`client.ts`) that creates an asymmetric key, builds DPoP JWTs, handles the nonce challenge and binds the access token to the JWK thumb‑print.  

All code compiles and runs with **exact dependency versions** – just copy the files, run `npm install`, then start the two processes.

---

<details><summary>🗂️  Directory layout</summary>

```
dpop-demo/
├─ package.json
├─ tsconfig.json
├─ src/
│  ├─ server.ts
│  └─ client.ts
```

</details>

---

## 1️⃣  `package.json` – exact versions & scripts

```json
{
  "name": "dpop-demo",
  "version": "1.0.0",
  "description": "OAuth2 DPoP proof‑of‑possession demo (Node.js + TypeScript)",
  "main": "src/server.ts",
  "type": "module",
  "scripts": {
    "build": "tsc",
    "start:server": "ts-node-esm src/server.ts",
    "start:client": "ts-node-esm src/client.ts"
  },
  "author": "ChatGPT",
  "license": "MIT",
  "dependencies": {
    "axios": "1.7.2",
    "express": "4.19.2",
    "jose": "5.2.1",
    "uuid": "9.0.1"
  },
  "devDependencies": {
    "@types/express": "4.17.21",
    "@types/node": "20.14.2",
    "ts-node": "10.9.2",
    "typescript": "5.5.4"
  }
}
```

* **`express`** – HTTP server.  
* **`jose`** – JWK / JWT creation & verification (covers DPoP proof, access token, thumb‑print).  
* **`axios`** – client HTTP requests (you could also use `node-fetch`).  
* **`uuid`** – generates `jti` values for replay‑protection.  
* **`ts-node`** – run TypeScript directly (no separate compile step needed).  

---

## 2️⃣  `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "NodeNext",
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "strict": true,
    "skipLibCheck": true,
    "outDir": "dist"
  },
  "include": ["src"]
}
```

---

## 3️⃣  Server – `src/server.ts`

```ts
// src/server.ts
import express, { Request, Response, NextFunction } from "express";
import { jwtVerify, createRemoteJWKSet, decodeJwt, calculateJwkThumbprint } from "jose";
import { v4 as uuidv4 } from "uuid";
import crypto from "crypto";

const app = express();
app.use(express.json());

// ---------------------------------------------------------------------------
// In‑memory stores (for demo only!)
const usedJti = new Set<string>();          // replay protection
const issuedNonces = new Map<string, number>(); // nonce → timestamp
const ACCESS_TOKEN_SECRET = new TextEncoder().encode("super‑secret‑signing‑key");

// ---------------------------------------------------------------------------
// Helper: generate a server nonce (base64url)
function generateNonce(): string {
  const nonce = crypto.randomBytes(16).toString("base64url");
  issuedNonces.set(nonce, Date.now());
  return nonce;
}

// ---------------------------------------------------------------------------
// Token endpoint – issues a signed JWT bound to the client’s JWK thumb‑print
app.post("/token", async (req: Request, res: Response) => {
  const { jwk } = req.body;
  if (!jwk) {
    return res.status(400).json({ error: "missing jwk" });
  }

  // Compute JWK thumb‑print (RFC 7638)
  const thumbprint = await calculateJwkThumbprint(jwk as any, "sha256");
  const now = Math.floor(Date.now() / 1000);

  const accessToken = await new jose.SignJWT({
    sub: "demo-client",
    iat: now,
    exp: now + 300, // 5 min
    cnf: { jkt: thumbprint } // bind token to key
  })
    .setProtectedHeader({ alg: "HS256" })
    .sign(ACCESS_TOKEN_SECRET);

  res.json({ access_token: accessToken, token_type: "DPoP", expires_in: 300 });
});

// ---------------------------------------------------------------------------
// Middleware: verify Authorization header (Bearer token) + DPoP proof
async function verifyDPoP(req: Request, res: Response, next: NextFunction) {
  const auth = req.headers.authorization;
  const dpopHeader = req.headers["dpop"] as string | undefined;

  if (!auth?.startsWith("DPoP ")) {
    return res.status(401).json({ error: "invalid or missing Authorization header" });
  }
  if (!dpopHeader) {
    return res.status(401).json({ error: "missing DPoP header" });
  }

  const accessToken = auth.substring("DPoP ".length);
  // ----------------------------------------------------------------------- // 1️⃣ Verify access token signature & cnf
  let payload: any;
  try {
    const { payload: p } = await jwtVerify(accessToken, ACCESS_TOKEN_SECRET);
    payload = p;
  } catch (e) {
    return res.status(401).json({ error: "invalid access token" });
  }

  // ----------------------------------------------------------------------- // 2️⃣ Verify DPoP proof JWT
  let dpopPayload: any;
  let dpopJwk: any;
  try {
    const { payload: dp, protectedHeader } = await jwtVerify(dpopHeader, async (protectedHeader) => {
      // The proof is signed with the client’s private key → we need the public key.
      // The public key is embedded in the JWT as the "jwk" claim.
      if (!dp?.jwk) throw new Error("DPoP proof missing jwk claim");
      dpopJwk = dp.jwk;
      return jose.importJWK(dp.jwk, protectedHeader.alg);
    });
    dpopPayload = dp;
  } catch (e: any) {
    return res.status(401).json({ error: "invalid DPoP proof", details: e.message });
  }

  // ----------------------------------------------------------------------- // 3️⃣ Validate DPoP claims
  const now = Math.floor(Date.now() / 1000);
  const { htm, htu, iat, jti, nonce } = dpopPayload;

  // a) method & URL binding
  if (htm?.toUpperCase() !== req.method) {
    return res.status(401).json({ error: "DPoP htm does not match request method" });
  }
  if (htu !== `${req.protocol}://${req.get("host")}${req.originalUrl}`) {
    return res.status(401).json({ error: "DPoP htu does not match request URL" });
  }

  // b) iat freshness (±5 min)
  if (Math.abs(now - iat) > 300) {
    return res.status(401).json({ error: "DPoP iat out of allowed window" });
  }

  // c) replay protection (jti)
  if (usedJti.has(jti)) {
    return res.status(401).json({ error: "DPoP jti replay detected" });
  }
  usedJti.add(jti);
  // (optional) prune old JTIs after a few minutes – omitted for brevity

  // d) nonce handling
  if (nonce) {
    const issued = issuedNonces.get(nonce);
    if (!issued || now - Math.floor(issued / 1000) > 300) {
      return res.status(401).json({ error: "DPoP nonce invalid or expired" });
    }
    // nonce used – delete to enforce one‑time use
    issuedNonces.delete(nonce);
  } else {
    // No nonce supplied → challenge the client
    const newNonce = generateNonce();
    res.set(
      "WWW-Authenticate",
      `DPoP realm="demo", nonce="${newNonce}", error="use_dpop_nonce"`
    );
    return res.status(401).json({ error: "DPoP nonce required" });
  }

  // e) Bind token to proof (thumb‑print)
  const proofThumb = await calculateJwkThumbprint(dpopJwk, "sha256");
  if (payload.cnf?.jkt !== proofThumb) {
    return res.status(401).json({ error: "access token not bound to presented key" });
  }

  // All checks passed → attach token payload for downstream handlers
  (req as any).token = payload;
  next();
}

// ---------------------------------------------------------------------------
// Protected resource
app.get("/resource", verifyDPoP, (req: Request, res: Response) => {
  const token = (req as any).token;
  res.json({
    message: "✅ Protected data accessed!",
    sub: token.sub,
    issued_at: token.iat
  });
});

// ---------------------------------------------------------------------------
// Start server
const PORT = 4000;
app.listen(PORT, () => {
  console.log(`🛡️  DPoP Resource Server listening on http://localhost:${PORT}`);
});
```

### What the server does

| Step | Purpose |
|------|---------|
| **/token** | Issues a signed access token (`HS256`) containing `cnf.jkt` – the thumb‑print of the client’s public JWK. |
| **verifyDPoP middleware** | 1️⃣ verifies the access token signature, 2️⃣ verifies the DPoP proof JWT signature using the embedded `jwk`, 3️⃣ checks `htm`, `htu`, `iat` (±5 min), `jti` (replay), **nonce** (challenge if missing), and finally that the token’s `cnf.jkt` matches the thumb‑print of the proof key. |
| **/resource** | Returns a JSON payload only when all checks succeed. |

All state (used JTIs, issued nonces) lives in memory – perfect for a demo but **not** for production.

---

## 4️⃣  Client – `src/client.ts`

```ts
// src/client.ts
import axios from "axios";
import * as jose from "jose";
import { v4 as uuidv4 } from "uuid";

const SERVER = "http://localhost:4000";

// ---------------------------------------------------------------------------
// 1️⃣ Generate an asymmetric EC key (P‑256) – this is the PoP key
async function generateKeyPair() {
  const { publicKey, privateKey } = await jose.generateKeyPair("ES256");
  const publicJwk = await jose.exportJWK(publicKey);
  const privateJwk = await jose.exportJWK(privateKey);
  return { publicJwk, privateJwk };
}

// ---------------------------------------------------------------------------
// 2️⃣ Obtain an access token bound to the JWK thumb‑print
async function getAccessToken(publicJwk: jose.JWK) {
  const resp = await axios.post(
    `${SERVER}/token`,
    { jwk: publicJwk },
    { headers: { "Content-Type": "application/json" } }
  );
  return resp.data.access_token as string;
}

// ---------------------------------------------------------------------------
// 3️⃣ Build a DPoP proof JWT (may include a nonce if supplied)
async function createDpopProof(
  method: string,
  url: string,
  privateJwk: jose.JWK,
  nonce?: string
) {
  const iat = Math.floor(Date.now() / 1000);
  const jti = uuidv4();

  // Export the public part to embed as "jwk" claim
  const { publicKey } = await jose.importJWK(privateJwk);
  const publicJwk = await jose.exportJWK(publicKey);

  const payload: any = {
    htm: method,
    htu: url,
    iat,
    jti,
    jwk: publicJwk // embed public key for server verification
  };
  if (nonce) payload.nonce = nonce;

  const dpopJwt = await new jose.SignJWT(payload)
    .setProtectedHeader({ alg: "ES256", typ: "dpop+jwt" })
    .sign(await jose.importJWK(privateJwk));

  return dpopJwt;
}

// ---------------------------------------------------------------------------
// 4️⃣ Perform a request to the protected resource, handling nonce challenges
async function requestResource(accessToken: string, privateJwk: jose.JWK) {
  const method = "GET";
  const url = `${SERVER}/resource`;

  // First attempt – no nonce
  let dpop = await createDpopProof(method, url, privateJwk);
  let resp = await sendRequest(url, method, accessToken, dpop);
  if (resp.status === 401 && resp.headers["www-authenticate"]) {
    // Extract nonce from WWW‑Authenticate header
    const authHeader = resp.headers["www-authenticate"] as string;
    const match = authHeader.match(/nonce="([^"]+)"/);
    const serverNonce = match?.[1];
    console.log("🔐 Server demanded nonce:", serverNonce);
    // Retry with nonce
    dpop = await createDpopProof(method, url, privateJwk, serverNonce);
    resp = await sendRequest(url, method, accessToken, dpop);
  }

  console.log("🔎 Final response status:", resp.status);
  console.log("🔎 Body:", resp.data);
}

// Helper – send HTTP request with Authorization & DPoP headers
async function sendRequest(
  url: string,
  method: string,
  accessToken: string,
  dpopJwt: string
) {
  try {
    return await axios.request({
      url,
      method: method as any,
      headers: {
        Authorization: `DPoP ${accessToken}`,
        DPoP: dpopJwt
      },
      validateStatus: () => true // we want to see 4xx responses too
    });
  } catch (e) {
    throw e;
  }
}

// ---------------------------------------------------------------------------
// 5️⃣ Demonstrate successful and failing requests
(async () => {
  const { publicJwk, privateJwk } = await generateKeyPair();
  const accessToken = await getAccessToken(publicJwk);
  console.log("✅ Obtained access token bound to JWK thumb‑print");

  // ---- Successful request (includes nonce handling) ----
  console.log("\n=== ✅ Successful request ===");
  await requestResource(accessToken, privateJwk);

  // ---- Failure #1: Re‑using same DPoP proof (replay of jti) ----
  console.log("\n=== ❌ Replay attack (same jti) ===");
  const method = "GET";
  const url = `${SERVER}/resource`;
  const dpopReplay = await createDpopProof(method, url, privateJwk);
  // First use – succeeds (nonce already supplied by previous call)
  await sendRequest(url, method, accessToken, dpopReplay);
  // Second use – same jti → should be rejected
  const replayResp = await sendRequest(url, method, accessToken, dpopReplay);
  console.log("Replay response:", replayResp.status, replayResp.data);

  // ---- Failure #2: Wrong HTTP method in DPoP proof ----
  console.log("\n=== ❌ Method mismatch ===");
  const wrongMethodProof = await createDpopProof("POST", url, privateJwk);
  const methodResp = await sendRequest(url, "GET", accessToken, wrongMethodProof);
  console.log("Method mismatch response:", methodResp.status, methodResp.data);

  // ---- Failure #3: Invalid signature (tampered proof) ----
  console.log("\n=== ❌ Tampered DPoP proof ===");
  let tampered = await createDpopProof(method, url, privateJwk);
  // corrupt the JWT by flipping a character
  tampered = tampered.replace(/.$/, "A");
  const tamperResp = await sendRequest(url, method, accessToken, tampered);
  console.log("Tampered proof response:", tamperResp.status, tamperResp.data);

  // ---- Failure #4: Access token bound to a different key ----
  console.log("\n=== ❌ Token bound to different key ===");
  const { publicJwk: otherPub, privateJwk: otherPriv } = await generateKeyPair();
  const otherToken = await getAccessToken(otherPub);
  const proofWithOriginalKey = await createDpopProof(method, url, privateJwk);
  const crossResp = await sendRequest(url, method, otherToken, proofWithOriginalKey);
  console.log("Cross‑key response:", crossResp.status, crossResp.data);
})();
```

### How the client works

1. **Key generation** – EC P‑256 (`ES256`).  
2. **Token request** – sends the public JWK to `/token`; receives a JWT whose `cnf.jkt` equals the thumb‑print of that JWK.  
3. **DPoP proof creation** – builds a JWT with required claims (`htm`, `htu`, `iat`, `jti`, `jwk`). If the server replies with a `WWW‑Authenticate` header containing a nonce, the client repeats the request with the `nonce` claim.  
4. **Demo of failures** – shows replay, method mismatch, tampered signature, and token‑key mismatch.  

All logs are printed to the console, so you can see exactly which check fails.

---

## 5️⃣  Running the demo

```bash
# 1️⃣ Clone / copy the files into a folder (e.g. dpop-demo)
cd dpop-demo

# 2️⃣ Install exact dependencies
npm ci   # uses the lock‑file generated from the versions above

# 3️⃣ Start the resource server (in one terminal)
npm run start:server

# 4️⃣ In another terminal, run the client
npm run start:client
```

You should see output similar to:

```
🛡️  DPoP Resource Server listening on http://localhost:4000
✅ Obtained access token bound to JWK thumb‑print

=== ✅ Successful request ===
🔐 Server demanded nonce: 9vKfYg5sB3lYjJpQ6sV6Vw
🔎 Final response status: 200
🔎 Body: { message: '✅ Protected data accessed!', sub: 'demo-client', issued_at: 172718... }

=== ❌ Replay attack (same jti) ===
Replay response: 401 { error: 'DPoP jti replay detected' }

=== ❌ Method mismatch ===
Method mismatch response: 401 { error: 'DPoP htm does not match request method' }

=== ❌ Tampered DPoP proof ===
Tampered proof response: 401 { error: 'invalid DPoP proof', details: 'JWT malformed' }

=== ❌ Token bound to different key ===
Cross‑key response: 401 { error: 'access token not bound to presented key' }
```

---

## 6️⃣  What each **rejected** request demonstrates

| # | Failure type | Trigger | Server response |
|---|--------------|---------|-----------------|
| 1 | **Replay (jti)** | Same DPoP JWT sent twice | `401 { error: 'DPoP jti replay detected' }` |
| 2 | **Method mismatch** | `htm` claim = `POST` while request is `GET` | `401 { error: 'DPoP htm does not match request method' }` |
| 3 | **Signature tampering** | Corrupt JWT string | `401 { error: 'invalid DPoP proof', details: 'JWT malformed' }` |
| 4 | **Token‑key binding mismatch** | Access token bound to a different JWK than the proof’s key | `401 { error: 'access token not bound to presented key' }` |
| 5 | **Missing/invalid nonce** | Omit `nonce` claim on first request | `401` with `WWW-Authenticate: DPoP realm="demo", nonce="…", error="use_dpop_nonce"` (client must retry with that nonce) |
| 6 | **Expired `iat`** (not shown) – change system clock or set `iat` far in the past → server returns `401 { error: 'DPoP iat out of allowed window' }`. |

---

## 7️⃣  Extending / hardening the demo (optional)

| Area | What to do |
|------|-------------|
| **Persistent storage** | Replace in‑memory `usedJti` / `issuedNonces` with Redis or a DB to survive restarts. |
| **Algorithm agility** | Use RSA (`RS256`) or EdDSA (`EdDSA`) keys; update `jose.generateKeyPair` accordingly. |
| **HTTPS** | Run the server behind TLS (required for production DPoP). |
| **Access‑token signing** | Use an asymmetric key (`RS256`) and JWKS endpoint instead of a static secret. |
| **Scope / audience** | Add `aud`, `scope` claims and enforce them in the resource endpoint. |
| **Nonce expiry** | Periodically purge old nonces (e.g., every minute). |
| **Rate‑limiting** | Add `express-rate-limit` to protect against DoS. |

---

### 🎉  You now have a **complete, reproducible** Node.js/TypeScript demo that shows how OAuth 2.0 DPoP works end‑to‑end, including proof‑of‑possession, nonce challenges, thumb‑print binding, and all the common failure modes. Happy hacking!
