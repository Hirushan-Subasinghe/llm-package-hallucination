**Implementation Overview**

We’ll implement a self‑contained Node.js/TypeScript service that provides the full WebAuthn protocol flow:

| Layer | Purpose | Key APIs / Packages |
|------|---------|---------------|
| **Package dependencies** | - `@simplewebauthn/server` (v9.0.0) – core WebAuthn library |
| | - `@simplewebauthn/browser` (v9.0.0) – client‑side utilities (used for fixtures) |
| | - `express` (4.18.2) – HTTP framework |
| | - `cors` (2.8.5) – middleware |
| | - `dotenv` (16.3.1 .env support) |
| | - `typescript` (5.3.3) – type safety |
| | - `@types/node` (20.10.0) – Node typings |
| | - `ts-node` (10.9.2) – TypeScript runner |
| | - `nodemon` (3.0.1) – dev auto‑restart |
| **Core modules** | |
| **Tenant config** | `src/config/tenants.ts` – `Map<string, TenantConfig>` (RP ID, RP name, origin) |
| **In‑memory credential store** | `src/adapters/InMemoryWebAuthnProvider.ts` – implements `WebAuthnProvider` (get/create/update/delete) |
| **Challenge lifecycle** | `src/utils/challengeStore.ts` – TTL‑based store, auto‑cleanup |
| **Registration flow** | `src/controllers/registrationController.ts` – `registrationStart` / `registrationFinish` |
| **Authentication flow** | `src/controllers/authenticationController.ts` – `authenticationStart` / `authenticationFinish` |
| **Express router** | `src/routes.ts` – 4 HTTP endpoints |
| **Server entry** | `src/server.ts` – Express app, CORS, JSON body parser |
| **Types** | `src/types.ts` – request/response DTOs, `TenantConfig` |
| **Fixtures** | `src/fixtures/registration-start.json`, `registration-finish.json`, `authentication-start.json`, `authentication-finish.json` |

---

### 📦 Package Dependencies & APIs Used

| Package | Version | Public APIs Used |
|---------|---------|-----------------|
| `@simplewebauthn/server` | 9.0.0 | `generateRegistrationOptions`, `verifyRegistrationResponse`, `generateAuthenticationOptions`, `verifyAuthenticationResponse`, `WebAuthnProvider` (interface), `Credential` (type), `RegistrationCredentialJSON`, `AuthenticationCredentialJSON`, `base64url`, `parseClientData` |
| `@simplewebauthn/browser` | 9.0.0 | Used only for fixture generation (client‑side utilities) |
| `express` | 4.18.2 | `express()`, `Router`, `json()`, `urlencoded()` |
| `cors` | 2.8.5 | `cors()` middleware |
| `dotenv` | 16.3.1 | `config()` |
| `typescript` | 5.3.3 | `tsc` compiler |
| `@types/node` | 20.10.0 | Type definitions |
| `ts-node` | 10.9.2 | `ts-node` CLI |
| `nodemon` | 3.0.1 | `nodemon` dev tool |

---

### 📁 File Structure

```
src/
├─ config/
│  └─ tenants.ts
├─ adapters/
│  └─ InMemoryWebAuthnProvider.ts
├─ utils/
│  ├─ challengeStore.ts
│  └─ (optional) logger.ts
├─ controllers/
│  ├─ registrationController.ts
│  └─ authenticationController.ts
├─ routes.ts
├─ server.ts
└─ types.ts
fixtures/
├─ registration-start.json
├─ registration-finish.json
├─ authentication-start.json
└─ authentication-finish.json
```

---

### 🛠️ Installation & Execution

```bash
# 1️⃣ Clone the repo (if applicable) and navigate
git clone <repo-url>
cd passkey-service

# 2️⃣ Install dependencies (exact versions from package.json)
npm install

# 3️⃣ Build the TypeScript project
npm run build   # produces dist/ with compiled JS

# 4️⃣ Run the service (dev mode with auto‑restart)
npm run dev    # uses ts-node-dev, watches src/, runs on http://localhost:3000

# 5️⃣ Test the endpoints (see examples below)
```

**Production start**

```bash
npm start   # runs the compiled dist/server.js
```

---

### 📝 Core Implementation Details

#### 1. Tenant Configuration (`src/config/tenants.ts`)

```
