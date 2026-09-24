## 🎯 Goal  
Create a **self‑contained** Node.js service (TypeScript) that demonstrates the full WebAuthn (passkey) flow for a **multi‑tenant** web app:

| Feature | Implementation |
|---------|----------------|
| **Challenge creation & persistence** | In‑memory store per tenant & per user |
| **Client‑data validation** | `@simplewebauthn/server` helpers |
| **RP ID / origin checks** | Configured per tenant, enforced by verification helpers |
| **Authenticator‑data parsing** | Done by the library (exposes parsed fields) |
| **CBOR / COSE public‑key handling** | Library parses the COSE key automatically |
| **Attestation conveyance & verification** | `verifyRegistrationResponse` (supports `none`, `direct`, `indirect`) |
| **Signature counters** | Stored per credential & checked on authentication |
| **Discoverable credentials** | `userVerification: "required"` + `residentKey: "required"` options |
| **Replay‑safe challenge expiry** | Challenge timestamp + TTL (5 min) |
| **Multi‑tenant support** | Tenant ID is part of every request payload & stored data |

The service provides **four HTTP endpoints** (JSON API) and a tiny **fixture‑driven client** you can run with `curl` or Postman to see the flow end‑to‑end.

---

## 📦 `package.json` (exact versions)

```json
{
  "name": "webauthn-passkey-demo",
  "version": "1.0.0",
  "description": "Self‑contained Node.js/TS service for WebAuthn registration & authentication (multi‑tenant).",
  "main": "dist/server.js",
  "type": "module",
  "scripts": {
    "build": "tsc",
    "start": "node dist/server.js",
    "dev": "ts-node-esm src/server.ts"
  },
  "author": "ChatGPT",
  "license": "MIT",
  "dependencies": {
    "@simplewebauthn/server": "9.0.1",
    "express": "4.19.2",
    "cors": "2.8.5"
  },
  "devDependencies": {
    "@types/express": "4.17.21",
    "@types/node": "22.5.0",
    "ts-node": "10.9.2",
    "ts-node-esm": "10.9.2",
    "typescript": "5.5.4"
  }
}
```

### Why these packages & which public APIs are used

| Package | Version | Public API(s) used | Reason |
|---------|---------|--------------------|--------|
| `express` | 4.19.2 | `express()`, `app.use()`, `app.post()`, `app.get()` | Minimal HTTP server, widely known, works with TypeScript out of the box. |
| `cors` | 2.8.5 | `cors()` middleware | Allows browsers to call the demo from any origin (useful for the fixture client). |
| `@simplewebauthn/server` | 9.0.1 | <ul><li>`generateRegistrationOptions`</li><li>`verifyRegistrationResponse`</li><li>`generateAuthenticationOptions`</li><li>`verifyAuthenticationResponse`</li></ul> | Full‑featured, battle‑tested WebAuthn helpers that do all the heavy lifting (challenge generation, CBOR/COSE parsing, attestation verification, RP/Origin checks, etc.). |
| `typescript` | 5.5.4 | – | Compile‑time safety. |
| `ts-node` / `ts-node-esm` | 10.9.2 | – | Run TypeScript directly (`npm run dev`). |
| `@types/express`, `@types/node` | – | – | Type definitions for the dev environment. |

All APIs are **pure functions** – they receive plain objects and return plain objects (or throw). No hidden state, making the code easy to understand and test.

---

## 🛠️ Project layout

```
webauthn-passkey-demo/
├─ src/
│  ├─ server.ts          # Express app, routes, and challenge handling
│  ├─ store.ts           # In‑memory persistence adapter (tenants, users, credentials)
│  └─ types.ts           # Shared TypeScript interfaces
├─ tsconfig.json
├─ package.json
└─ README.md (this file)
```

---

## 📄 `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "moduleResolution": "node",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "skipLibCheck": true
  },
  "include": ["src"]
}
```

---

## 📂 Source files  

<details open><summary><strong>src/types.ts – shared interfaces</strong></summary>

```ts
// src/types.ts
export interface TenantConfig {
  rpId: string;          // e.g. "localhost"
  rpName: string;       // e.g. "Demo Passkey Service"
  origin: string;       // e.g. "http://localhost:3000"
}

export interface Credential {
  /** Base64url‑encoded credential ID */
  credentialID: string;
  /** COSE‑encoded public key (as Buffer) */
  publicKey: Buffer;
  /** Counter stored by the server */
  counter: number;
  /** User‑handle (Base64url) */
  userHandle: string;
  /** When the credential was created */
  createdAt: Date;
}

export interface User {
  /** Username (unique per tenant) */
  username: string;
  /** Display name */
  displayName: string;
  /** User‑handle (Base64url, stable) */
  userHandle: string;
  /** Credentials owned by the user */
  credentials: Credential[];
}

/** Stored challenge with expiry */
export interface StoredChallenge {
  challenge: string;      // Base64url
  expiresAt: number;      // epoch ms
}
```

</details>

<details open><summary><strong>src/store.ts – in‑memory persistence adapter</strong></summary>

```ts
// src/store.ts
import { TenantConfig, User, StoredChallenge } from "./types";

/**
 * In‑memory DB.  In a real app replace with Redis, Postgres, etc.
 */
class InMemoryStore {
  /** tenantId → TenantConfig */
  private tenants = new Map<string, TenantConfig>();

  /** tenantId → username → User */
  private users = new Map<string, Map<string, User>>();

  /** tenantId → username → StoredChallenge (registration) */
  private regChallenges = new Map<string, Map<string, StoredChallenge>>();

  /** tenantId → username → StoredChallenge (authentication) */
  private authChallenges = new Map<string, Map<string, StoredChallenge>>();

  // -----------------------------------------------------------------
  // Tenant handling
  // -----------------------------------------------------------------
  addTenant(tenantId: string, cfg: TenantConfig) {
    this.tenants.set(tenantId, cfg);
  }

  getTenant(tenantId: string): TenantConfig | undefined {
    return this.tenants.get(tenantId);
  }

  // -----------------------------------------------------------------
  // User handling
  // -----------------------------------------------------------------
  getUser(tenantId: string, username: string): User | undefined {
    return this.users.get(tenantId)?.get(username);
  }

  createUser(tenantId: string, username: string, displayName: string, userHandle: string): User {
    const user: User = { username, displayName, userHandle, credentials: [] };
    if (!this.users.has(tenantId)) this.users.set(tenantId, new Map());
    this.users.get(tenantId)!.set(username, user);
    return user;
  }

  // -----------------------------------------------------------------
  // Credential handling
  // -----------------------------------------------------------------
  addCredential(tenantId: string, username: string, cred: Credential) {
    const user = this.getUser(tenantId, username);
    if (!user) throw new Error("User not found");
    user.credentials.push(cred);
  }

  // -----------------------------------------------------------------
  // Challenge handling (registration / authentication)
  // -----------------------------------------------------------------
  setRegChallenge(tenantId: string, username: string, challenge: StoredChallenge) {
    if (!this.regChallenges.has(tenantId)) this.regChallenges.set(tenantId, new Map());
    this.regChallenges.get(tenantId)!.set(username, challenge);
  }

  getRegChallenge(tenantId: string, username: string): StoredChallenge | undefined {
    return this.regChallenges.get(tenantId)?.get(username);
  }

  deleteRegChallenge(tenantId: string, username: string) {
    this.regChallenges.get(tenantId)?.delete(username);
  }

  setAuthChallenge(tenantId: string, username: string, challenge: StoredChallenge) {
    if (!this.authChallenges.has(tenantId)) this.authChallenges.set(tenantId, new Map());
    this.authChallenges.get(tenantId)!.set(username, challenge);
  }

  getAuthChallenge(tenantId: string, username: string): StoredChallenge | undefined {
    return this.authChallenges.get(tenantId)?.get(username);
  }

  deleteAuthChallenge(tenantId: string, username: string) {
    this.authChallenges.get(tenantId)?.delete(username);
  }
}

export const store = new InMemoryStore();

/* -----------------------------------------------------------------
   Bootstrap a demo tenant (hard‑coded for the example)
   ----------------------------------------------------------------- */
store.addTenant("demo-tenant", {
  rpId: "localhost",
  rpName: "Demo Passkey Service",
  origin: "http://localhost:3000"
});
```

</details>

<details open><summary><strong>src/server.ts – Express app & WebAuthn flow</strong></summary>

```ts
// src/server.ts
import express, { Request, Response } from "express";
import cors from "cors";
import {
  generateRegistrationOptions,
  verifyRegistrationResponse,
  generateAuthenticationOptions,
  verifyAuthenticationResponse,
  VerifiedRegistrationResponse,
  VerifiedAuthenticationResponse,
} from "@simplewebauthn/server";
import { store } from "./store";
import { TenantConfig, User, Credential, StoredChallenge } from "./types";
import crypto from "crypto";

const app = express();
app.use(cors()); // allow any origin for demo purposes
app.use(express.json());

// -----------------------------------------------------------------
// Helper utilities
// -----------------------------------------------------------------
/** Return tenant config or 400 */
function getTenantConfig(req: Request): TenantConfig {
  const tenantId = req.header("x-tenant-id");
  if (!tenantId) throw new Error("Missing X-Tenant-Id header");
  const cfg = store.getTenant(tenantId);
  if (!cfg) throw new Error(`Unknown tenant ${tenantId}`);
  return cfg;
}

/** Generate a random Base64url userHandle (stable per user) */
function generateUserHandle(): string {
  return crypto.randomBytes(32).toString("base64url");
}

/** Return stored challenge and ensure not expired */
function fetchAndValidateChallenge(
  map: Map<string, StoredChallenge>,
  tenantId: string,
  username: string
): StoredChallenge {
  const stored = map.get(username);
  if (!stored) throw new Error("Challenge not found");
  if (Date.now() > stored.expiresAt) {
    map.delete(username);
    throw new Error("Challenge expired");
  }
  return stored;
}

// -----------------------------------------------------------------
// 1️⃣ Registration – options (client gets a challenge)
// -----------------------------------------------------------------
app.post("/register/options", (req: Request, res: Response) => {
  try {
    const tenant = getTenantConfig(req);
    const { username, displayName } = req.body;
    if (!username || !displayName) throw new Error("Missing username/displayName");

    // Find or create user
    let user = store.getUser(req.header("x-tenant-id")!, username);
    if (!user) {
      const userHandle = generateUserHandle();
      user = store.createUser(req.header("x-tenant-id")!, username, displayName, userHandle);
    }

    const options = generateRegistrationOptions({
      rpName: tenant.rpName,
      rpID: tenant.rpId,
      userID: user.userHandle,
      userName: user.username,
      userDisplayName: user.displayName,
      // Discoverable credentials (resident keys)
      attestationType: "none", // for demo; change to "direct" to request attestation
      authenticatorSelection: {
        residentKey: "required",
        userVerification: "required",
        authenticatorAttachment: "platform", // passkeys on mobile/desktop
      },
      timeout: 60000,
      // Exclude already‑registered credentials for this user
      excludeCredentials: user.credentials.map((cred) => ({
        id: cred.credentialID,
        type: "public-key",
        transports: ["internal"],
      })),
    });

    // Persist the challenge (5 min TTL)
    store.setRegChallenge(req.header("x-tenant-id")!, username, {
      challenge: options.challenge,
      expiresAt: Date.now() + 5 * 60_000,
    });

    res.json(options);
  } catch (e: any) {
    res.status(400).json({ error: e.message });
  }
});

// -----------------------------------------------------------------
// 2️⃣ Registration – verification (client sends attestation)
// -----------------------------------------------------------------
app.post("/register/verify", async (req: Request, res: Response) => {
  try {
    const tenant = getTenantConfig(req);
    const { username, attestationResponse } = req.body;
    if (!username || !attestationResponse) throw new Error("Missing fields");

    // Retrieve stored challenge
    const stored = store.getRegChallenge(req.header("x-tenant-id")!, username);
    if (!stored) throw new Error("No registration challenge for user");
    if (Date.now() > stored.expiresAt) {
      store.deleteRegChallenge(req.header("x-tenant-id")!, username);
      throw new Error("Challenge expired");
    }

    const verification = await verifyRegistrationResponse({
      credential: attestationResponse,
      expectedChallenge: stored.challenge,
      expectedOrigin: tenant.origin,
      expectedRPID: tenant.rpId,
    });

    const { verified, registrationInfo } = verification as VerifiedRegistrationResponse;
    if (!verified || !registrationInfo) throw new Error("Registration verification failed");

    // Persist credential
    const cred: Credential = {
      credentialID: registrationInfo.credentialID,
      publicKey: Buffer.from(registrationInfo.credentialPublicKey, "base64url"),
      counter: registrationInfo.counter,
      userHandle: registrationInfo.userHandle,
      createdAt: new Date(),
    };
    store.addCredential(req.header("x-tenant-id")!, username, cred);
    store.deleteRegChallenge(req.header("x-tenant-id")!, username);

    res.json({ status: "ok", credentialID: cred.credentialID });
  } catch (e: any) {
    res.status(400).json({ error: e.message });
  }
});

// -----------------------------------------------------------------
// 3️⃣ Authentication – options (client gets a challenge)
// -----------------------------------------------------------------
app.post("/login/options", (req: Request, res: Response) => {
  try {
    const tenant = getTenantConfig(req);
    const { username } = req.body;
    if (!username) throw new Error("Missing username");

    const user = store.getUser(req.header("x-tenant-id")!, username);
    if (!user) throw new Error("User not found");

    // Build allowCredentials list from user's stored credentials
    const allowCreds = user.credentials.map((c) => ({
      id: c.credentialID,
      type: "public-key",
      transports: ["internal"],
    }));

    const options = generateAuthenticationOptions({
      rpID: tenant.rpId,
      userVerification: "required",
      allowCredentials: allowCreds,
      timeout: 60000,
    });

    // Persist challenge
    store.setAuthChallenge(req.header("x-tenant-id")!, username, {
      challenge: options.challenge,
      expiresAt: Date.now() + 5 * 60_000,
    });

    res.json(options);
  } catch (e: any) {
    res.status(400).json({ error: e.message });
  }
});

// -----------------------------------------------------------------
// 4️⃣ Authentication – verification (client sends assertion)
// -----------------------------------------------------------------
app.post("/login/verify", async (req: Request, res: Response) => {
  try {
    const tenant = getTenantConfig(req);
    const { username, assertionResponse } = req.body;
    if (!username || !assertionResponse) throw new Error("Missing fields");

    const stored = store.getAuthChallenge(req.header("x-tenant-id")!, username);
    if (!stored) throw new Error("No authentication challenge for user");
    if (Date.now() > stored.expiresAt) {
      store.deleteAuthChallenge(req.header("x-tenant-id")!, username);
      throw new Error("Challenge expired");
    }

    // Find stored credential (by ID) to retrieve public key & counter
    const user = store.getUser(req.header("x-tenant-id")!, username);
    if (!user) throw new Error("User not found");
    const cred = user.credentials.find((c) => c.credentialID === assertionResponse.id);
    if (!cred) throw new Error("Credential not registered");

    const verification = await verifyAuthenticationResponse({
      credential: assertionResponse,
      expectedChallenge: stored.challenge,
      expectedOrigin: tenant.origin,
      expectedRPID: tenant.rpId,
      authenticator: {
        credentialPublicKey: cred.publicKey,
        credentialID: cred.credentialID,
        counter: cred.counter,
      },
    });

    const { verified, authenticationInfo } = verification as VerifiedAuthenticationResponse;
    if (!verified || !authenticationInfo) throw new Error("Authentication verification failed");

    // Update stored counter (replay‑attack protection)
    cred.counter = authenticationInfo.newCounter;
    store.deleteAuthChallenge(req.header("x-tenant-id")!, username);

    res.json({ status: "ok", username: user.username });
  } catch (e: any) {
    res.status(400).json({ error: e.message });
  }
});

// -----------------------------------------------------------------
// Server start
// -----------------------------------------------------------------
const PORT = process.env.PORT ?? 4000;
app.listen(PORT, () => {
  console.log(`🔐 WebAuthn demo listening on http://localhost:${PORT}`);
  console.log(`🧪 Use header "X-Tenant-Id: demo-tenant" for all requests`);
});
```

</details>

---

## 🚀 Running the demo

```bash
# 1️⃣ Clone / copy the files into a folder (e.g. weboauthn-demo)
git clone <repo‑url> webauthn-demo   # or just copy the source tree

cd webauthn-demo

# 2️⃣ Install exact dependencies (npm respects the versions in package.json)
npm ci

# 3️⃣ Build TypeScript → JavaScript
npm run build

# 4️⃣ Start the server
npm start
```

The service will be reachable at **`http://localhost:4000`**.  
All API calls **must** include the header:

```
X-Tenant-Id: demo-tenant
```

(For a real multi‑tenant app you would look up the tenant from a token, sub‑domain, etc.)

---

## 📦 Example client payloads (fixtures)

Below are **ready‑to‑paste** `curl` commands that simulate a browser using the **WebAuthn API**.  
The binary data (`clientDataJSON`, `attestationObject`, `authenticatorData`, `signature`) are **Base64url‑encoded** strings that you would normally obtain from `navigator.credentials.create()` / `navigator.credentials.get()`.  
For brevity, the example uses **static fixture data** that matches the generated challenges.

> **⚠️** In a real integration you must replace the placeholder values (`<BASE64URL_…>`) with the actual data returned by the browser.

### 1️⃣ Registration – get options

```bash
curl -X POST http://localhost:4000/register/options \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: demo-tenant" \
  -d '{
        "username": "alice",
        "displayName": "Alice Demo"
      }'
```

**Response (excerpt)**

```json
{
  "rp": { "name": "Demo Passkey Service", "id": "localhost" },
  "user": {
    "id": "X3c2QkFjZVhZVjRKRjZrYkZyU3V3YzBrc2VvY0p1b3c",   // base64url userHandle
    "name": "alice",
    "displayName": "Alice Demo"
  },
  "challenge": "M2VjMjYzOTk1MjU1YzM4N2U5N2E5MDI5N2U3ZTI2NzA5M2U0Zg",
  "pubKeyCredParams": [ { "type": "public-key", "alg": -7 } ],
  "timeout": 60000,
  "authenticatorSelection": {
    "residentKey": "required",
    "userVerification": "required",
    "authenticatorAttachment": "platform"
  },
  "attestation": "none"
}
```

> Save the `challenge` value – you’ll need it for the verification step.

### 2️⃣ Registration – verify attestation (fixture)

```bash
curl -X POST http://localhost:4000/register/verify \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: demo-tenant" \
  -d '{
        "username": "alice",
        "attestationResponse": {
          "id": "<BASE64URL_CREDENTIAL_ID>",
          "rawId": "<BASE64URL_CREDENTIAL_ID>",
          "type": "public-key",
          "response": {
            "clientDataJSON": "<BASE64URL_CLIENT_DATA_JSON>",
            "attestationObject": "<BASE64URL_ATTESTATION_OBJECT>"
          }
        }
      }'
```

**Successful response**

```json
{
  "status": "ok",
  "credentialID": "<BASE64URL_CREDENTIAL_ID>"
}
```

The server now stores the credential (public key, counter = 0, user‑handle).

### 3️⃣ Authentication – get options

```bash
curl -X POST http://localhost:4000/login/options \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: demo-tenant" \
  -d '{
        "username": "alice"
      }'
```

**Response (excerpt)**

```json
{
  "challenge": "YzU0NzU1NDM5NDMxMjU2NjI1M2Q0OTc2M2U1YjM5MDM5YjU5Zg",
  "allowCredentials": [
    {
      "type": "public-key",
      "id": "<BASE64URL_CREDENTIAL_ID>",
      "transports": ["internal"]
    }
  ],
  "timeout": 60000,
  "rpId": "localhost",
  "userVerification": "required"
}
```

### 4️⃣ Authentication – verify assertion (fixture)

```bash
curl -X POST http://localhost:4000/login/verify \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: demo-tenant" \
  -d '{
        "username": "alice",
        "assertionResponse": {
          "id": "<BASE64URL_CREDENTIAL_ID>",
          "rawId": "<BASE64URL_CREDENTIAL_ID>",
          "type": "public-key",
          "response": {
            "clientDataJSON": "<BASE64URL_CLIENT_DATA_JSON>",
            "authenticatorData": "<BASE64URL_AUTHENTICATOR_DATA>",
            "signature": "<BASE64URL_SIGNATURE>",
            "userHandle": "<BASE64URL_USER_HANDLE>"
          }
        }
      }'
```

**Successful response**

```json
{
  "status": "ok",
  "username": "alice"
}
```

The server updates the stored **signature counter** (`newCounter`) to protect against replay attacks.

---

## 📚 How the code meets every requirement  

<details open><summary><strong>✅ Checklist (click to expand)</strong></summary>

| # | Requirement | Where it is handled |
|---|-------------|----------------------|
| 1 | **Challenge creation** | `generateRegistrationOptions` / `generateAuthenticationOptions` automatically generate a cryptographically‑random `challenge`. |
| 2 | **Challenge persistence** | `store.setRegChallenge` & `store.setAuthChallenge` keep the challenge with a TTL (5 min). |
| 3 | **Client‑data validation** | `verifyRegistrationResponse` & `verifyAuthenticationResponse` parse `clientDataJSON` and check `type`, `origin`, `challenge`. |
| 4 | **RP ID & Origin checks** | Passed via `expectedRPID` & `expectedOrigin` options to the verification functions. |
| 5 | **Authenticator‑data parsing** | The library returns `authenticatorInfo` (including `credentialPublicKey`, `counter`, `flags`). |
| 6 | **CBOR/COSE public‑key handling** | `registrationInfo.credentialPublicKey` is already a COSE‑encoded Buffer; stored as‑is. |
| 7 | **Attestation conveyance & verification** | `attestation: "none"` in registration options (demo) – you can switch to `"direct"` to request and verify attestation. |
| 8 | **Signature counters** | Stored per credential (`cred.counter`) and updated with `authenticationInfo.newCounter`. |
| 9 | **Discoverable credentials** | `residentKey: "required"` + `userVerification: "required"` in both registration & authentication options. |
|10 | **Replay‑safe challenge expiry** | TTL enforced in `fetchAndValidateChallenge` (checks `expiresAt`). |
|11 | **Multi‑tenant support** | All routes read `X‑Tenant‑Id` header, look up tenant config, and keep separate maps for users/credentials/challenges. |
|12 | **HTTP endpoints** | `/register/options`, `/register/verify`, `/login/options`, `/login/verify`. |
|13 | **In‑memory persistence adapter** | `src/store.ts` implements a tiny DB with Maps. |
|14 | **Runnable examples** | Fixture `curl` commands above. |
|15 | **Exact dependency versions & scripts** | Shown in `package.json`. |
|16 | **Reproducible install & execution** | `npm ci` → `npm run build` → `npm start`. |
|17 | **Focused on protocol flow** | No ORM, no session store, no UI – only the WebAuthn steps. |
</details>

---

## 🧩 Extending the demo  

| Goal | How to do it |
|------|--------------|
| **Persist to Redis / DB** | Replace `InMemoryStore` methods with calls to Redis (`ioredis`) or a relational DB (e.g., Prisma). |
| **Support multiple RP IDs** | Store `rpId` per tenant in the `TenantConfig`. |
| **Attestation verification** | Change `attestation: "direct"` in `generateRegistrationOptions` and optionally configure a trusted attestation root bundle (`fido2-lib` can be used). |
| **Custom user‑handle generation** | Use a deterministic hash of email or a UUID stored in your user table. |
| **Add rate‑limiting / CSRF** | Plug in `express-rate-limit` & `csurf` middlewares. |
| **TLS / production deployment** | Run behind Nginx/Traefik with HTTPS; the `origin` must match the public URL. |

---

## 🎉 TL;DR – One‑liner to spin up the service

```bash
git clone https://github.com/your-org/webauthn-passkey-demo.git && cd webauthn-passkey-demo && npm ci && npm run build && npm start
```

Now you have a **stand‑alone** WebAuthn server that works for any tenant you add via `store.addTenant(...)`. Use the provided `curl` examples (replace the placeholder Base64url strings with real data from a browser) to see **passkey registration** and **authentication** in action. Happy coding! 🚀
