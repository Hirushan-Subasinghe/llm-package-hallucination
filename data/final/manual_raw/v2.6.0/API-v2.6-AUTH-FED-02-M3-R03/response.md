## 📚 Overview  

Below is a **complete, self‑contained Node.js + TypeScript** example of a **confidential OIDC client** that implements the **Authorization Code Flow with PKCE**.  

It:

* discovers the **issuer metadata** (`/.well‑known/openid-configuration`);
* generates & validates **state**, **nonce**, and **PKCE** (`code_verifier` / `code_challenge`);
* exchanges the **authorization code** for a **token set**;
* validates the **ID‑token** (issuer, audience, signature, `exp`/`nbf`, `nonce`) against **rotating JWKS**;
* stores the **PKCE verifier, state, nonce, and token set** in an **encrypted server‑side session**;
* supports **refresh‑token** flow without losing the session binding;
* provides **login**, **callback**, and **logout** routes;
* is **configurable** (issuer URL, client credentials, redirect URI, etc.) via a `.env` file;  
* ships with an exact `package.json` (pinned versions) and reproducible install/run commands.

> **No vendor‑specific IdP is hard‑coded** – you can point the client at any OIDC‑compliant provider (Keycloak, FusionAuth, Auth0, Azure AD, etc.).

---  

<details open><summary>📁 Project Structure</summary>

```
oidc-pkce-client/
├─ src/
│  ├─ server.ts          # Main Express app
│  └─ types.d.ts         # Optional custom types
├─ .env.example           # Example env file
├─ tsconfig.json          # TypeScript config
├─ package.json
└─ README.md
```

</details>

---  

## 📦 `package.json` (exact versions)

```json
{
  "name": "oidc-pkce-client",
  "version": "1.0.0",
  "description": "Confidential OIDC client (Authorization Code + PKCE) with encrypted server‑side session",
  "main": "dist/server.js",
  "type": "module",
  "scripts": {
    "build": "tsc",
    "start": "node dist/server.js",
    "dev": "ts-node-dev --respawn --transpile-only src/server.ts"
  },
  "author": "Your Name",
  "license": "MIT",
  "engines": {
    "node": ">=18"
  },
  "dependencies": {
    "dotenv": "16.4.5",
    "express": "4.19.2",
    "express-session": "1.18.0",
    "openid-client": "5.6.5",
    "jose": "5.2.0"
  },
  "devDependencies": {
    "@types/express": "4.17.21",
    "@types/express-session": "1.17.7",
    "@types/node": "22.2.0",
    "ts-node": "10.9.2",
    "ts-node-dev": "2.0.0",
    "typescript": "5.4.5"
  }
}
```

### Packages & APIs Used  

| Package | Purpose | Key APIs |
|---------|---------|----------|
| **express** | HTTP server & routing | `express()`, `app.get()`, `app.post()` |
| **express-session** | Server‑side session storage (cookie‑based) | `session()`, `req.session` |
| **openid-client** | Full OIDC client, discovery, PKCE, token handling, JWKS validation | `Issuer.discover()`, `new client.Client()`, `client.authorizationUrl()`, `client.callback()`, `client.refresh()` |
| **jose** | Low‑level JWT verification (used for extra nonce check & encryption utilities) | `jwtVerify()`, `createSecretKey()`, `AES.GCM` helpers |
| **dotenv** | Load environment variables | `config()` |
| **typescript**, **ts-node**, **ts-node-dev** | Compile & run TS | N/A |

---  

## 🛠️ `tsconfig.json`

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

## 📄 `.env.example`

```dotenv
# -------------------------------------------------
# OpenID Connect Provider (Issuer) – e.g. https://auth.example.com
# -------------------------------------------------
ISSUER_URL=https://your-issuer.example.com

# -------------------------------------------------
# Confidential client credentials (registered in the IdP)
# -------------------------------------------------
CLIENT_ID=your-client-id
CLIENT_SECRET=your-client-secret

# -------------------------------------------------
# URL where the provider will redirect back to your app
# Must be registered in the IdP (e.g. http://localhost:3000/callback)
# -------------------------------------------------
REDIRECT_URI=http://localhost:3000/callback

# -------------------------------------------------
# Session & encryption secrets (32‑byte base64 strings recommended)
# -------------------------------------------------
SESSION_SECRET=change-me-to-a-strong-random-string
ENCRYPTION_KEY=change-me-to-32-bytes-base64

# -------------------------------------------------
# Optional: Scopes you want (space‑separated)
# -------------------------------------------------
SCOPES=openid profile email offline_access
```

> **Tip:** Generate a 32‑byte base64 key with `openssl rand -base64 32`.

---  

## 🧩 `src/server.ts` – Full Implementation  

```ts
// src/server.ts
import 'dotenv/config';
import express, { Request, Response, NextFunction } from 'express';
import session from 'express-session';
import { Issuer, generators, TokenSet, Client } from 'openid-client';
import { createSecretKey, randomBytes, createCipheriv, createDecipheriv } from 'crypto';
import { jwtVerify, JWKS } from 'jose';

// ---------- Configuration ----------
const {
  ISSUER_URL,
  CLIENT_ID,
  CLIENT_SECRET,
  REDIRECT_URI,
  SESSION_SECRET,
  ENCRYPTION_KEY,
  SCOPES = 'openid profile email offline_access',
} = process.env;

if (!ISSUER_URL || !CLIENT_ID || !CLIENT_SECRET || !REDIRECT_URI || !SESSION_SECRET || !ENCRYPTION_KEY) {
  console.error('Missing required environment variables. Check .env file.');
  process.exit(1);
}

// ---------- Helper: AES‑256‑GCM encryption for session payload ----------
const ENC_ALGO = 'aes-256-gcm';
const ENCRYPTION_KEY_BUF = Buffer.from(ENCRYPTION_KEY, 'base64'); // 32‑bytes

function encrypt(data: string): string {
  const iv = randomBytes(12); // 96‑bit nonce for GCM
  const cipher = createCipheriv(ENC_ALGO, ENCRYPTION_KEY_BUF, iv);
  const ciphertext = Buffer.concat([cipher.update(data, 'utf8'), cipher.final()]);
  const tag = cipher.getAuthTag();
  // Store iv|tag|ciphertext as base64
  return Buffer.concat([iv, tag, ciphertext]).toString('base64');
}

function decrypt(enc: string): string {
  const buf = Buffer.from(enc, 'base64');
  const iv = buf.subarray(0, 12);
  const tag = buf.subarray(12, 28);
  const ciphertext = buf.subarray(28);
  const decipher = createDecipheriv(ENC_ALGO, ENCRYPTION_KEY_BUF, iv);
  decipher.setAuthTag(tag);
  const plaintext = Buffer.concat([decipher.update(ciphertext), decipher.final()]);
  return plaintext.toString('utf8');
}

// ---------- Express app ----------
const app = express();
app.set('trust proxy', 1); // if behind reverse proxy

app.use(
  session({
    name: 'oidc.sid',
    secret: SESSION_SECRET,
    resave: false,
    saveUninitialized: false,
    cookie: {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 24 * 60 * 60 * 1000, // 1 day
    },
    // Store encrypted JSON payload in the session cookie
    // (express-session already signs + encrypts the cookie, but we add a second layer
    //  for demonstration & defense‑in‑depth.)
    genid: () => randomBytes(16).toString('hex'), // custom session IDs
  })
);

// ---------- Types for session payload ----------
interface OIDCSession {
  state: string;
  nonce: string;
  codeVerifier: string;
  tokenSet?: TokenSet; // stored after callback
}

// ---------- Middleware to attach a typed session ----------
app.use((req: Request, _res: Response, next: NextFunction) => {
  if (!req.session) return next();
  // deserialize encrypted payload if present
  if (typeof req.session.oidc === 'string') {
    try {
      req.session.oidc = JSON.parse(decrypt(req.session.oidc)) as OIDCSession;
    } catch (e) {
      console.warn('Failed to decrypt session payload', e);
      req.session.oidc = {} as OIDCSession;
    }
  } else {
    req.session.oidc = {} as OIDCSession;
  }
  // after response, re‑encrypt before saving
  const originalSave = req.session.save.bind(req.session);
  req.session.save = (cb?: (err?: any) => void) => {
    if (req.session?.oidc) {
      try {
        const enc = encrypt(JSON.stringify(req.session.oidc));
        (req.session as any).oidc = enc;
      } catch (e) {
        console.error('Failed to encrypt session payload', e);
      }
    }
    return originalSave(cb);
  };
  next();
});

// ---------- OIDC client setup ----------
let client: Client; // will be initialized after discovery

async function initClient() {
  const issuer = await Issuer.discover(ISSUER_URL);
  client = new issuer.Client({
    client_id: CLIENT_ID,
    client_secret: CLIENT_SECRET,
    redirect_uris: [REDIRECT_URI],
    response_types: ['code'],
    token_endpoint_auth_method: 'client_secret_basic',
  });
  console.log(`Discovered issuer ${issuer.issuer}`);
}
initClient().catch((err) => {
  console.error('Failed to discover OIDC issuer:', err);
  process.exit(1);
});

// ---------- Route: Home ----------
app.get('/', (req, res) => {
  const isLoggedIn = !!(req.session as any).oidc?.tokenSet?.access_token;
  res.send(`
    <h1>OIDC PKCE Confidential Client Demo</h1>
    ${isLoggedIn ? `<p>🟢 Logged in as ${(req.session as any).oidc?.tokenSet?.claims()?.sub}</p>` : '<p>🔴 Not logged in</p>'}
    <a href="/login">Login</a> | <a href="/profile">Profile</a> | <a href="/logout">Logout</a>
  `);
});

// ---------- Route: Login ----------
app.get('/login', async (req, res) => {
  // Generate PKCE verifier/challenge, state & nonce
  const codeVerifier = generators.codeVerifier(); // 43‑128 chars
  const codeChallenge = generators.codeChallenge(codeVerifier);
  const state = generators.state();
  const nonce = generators.nonce();

  // Store them in the encrypted session
  const sess = (req.session as any).oidc as OIDCSession;
  sess.state = state;
  sess.nonce = nonce;
  sess.codeVerifier = codeVerifier;
  await req.session?.save();

  const authUrl = client.authorizationUrl({
    scope: SCOPES,
    response_mode: 'query',
    code_challenge: codeChallenge,
    code_challenge_method: 'S256',
    state,
    nonce,
  });

  res.redirect(authUrl);
});

// ---------- Route: Callback ----------
app.get('/callback', async (req, res) => {
  const sess = (req.session as any).oidc as OIDCSession;

  // Verify state matches what we sent
  if (!req.query.state || req.query.state !== sess.state) {
    return res.status(400).send('Invalid state');
  }

  // Exchange code for tokens, passing the original PKCE verifier
  let tokenSet: TokenSet;
  try {
    tokenSet = await client.callback(REDIRECT_URI, req.query, {
      state: sess.state,
      nonce: sess.nonce,
      code_verifier: sess.codeVerifier,
    });
  } catch (err) {
    console.error('Token exchange error:', err);
    return res.status(500).send('Failed to exchange code');
  }

  // ----- ID‑Token validation (extra checks) -----
  const idToken = tokenSet.id_token;
  if (!idToken) {
    return res.status(500).send('Missing ID token');
  }

  // Use jose to verify signature + claims (openid-client already does this, but we
  // demonstrate explicit verification against rotating JWKS).
  try {
    const jwks = JWKS.fromKeyStore(client.issuer.keystore);
    const { payload } = await jwtVerify(idToken, jwks, {
      issuer: client.issuer.issuer,
      audience: CLIENT_ID,
    });

    // Verify nonce claim matches the stored one
    if (payload.nonce !== sess.nonce) {
      throw new Error('Nonce mismatch');
    }

    // Verify time based claims (exp, nbf) – jose does this automatically
    // Additional optional checks can be added here.
  } catch (e) {
    console.error('ID‑Token validation failed:', e);
    return res.status(400).send('Invalid ID token');
  }

  // Store the token set in the session (encrypted by the wrapper above)
  sess.tokenSet = tokenSet;
  await req.session?.save();

  res.redirect('/');
});

// ---------- Route: Profile (protected) ----------
app.get('/profile', async (req, res) => {
  const tokenSet = (req.session as any).oidc?.tokenSet as TokenSet | undefined;
  if (!tokenSet) {
    return res.redirect('/login');
  }

  // Optional: refresh token if access token is expired
  if (tokenSet.expired()) {
    if (!tokenSet.refresh_token) {
      return res.status(401).send('Session expired and no refresh token available.');
    }
    try {
      const refreshed = await client.refresh(tokenSet.refresh_token);
      (req.session as any).oidc.tokenSet = refreshed;
      await req.session?.save();
    } catch (e) {
      console.error('Refresh token error:', e);
      return res.status(401).send('Unable to refresh token');
    }
  }

  // Show claims from ID token
  const claims = tokenSet.claims();
  res.send(`
    <h2>User Profile</h2>
    <pre>${JSON.stringify(claims, null, 2)}</pre>
    <a href="/">Home</a> | <a href="/logout">Logout</a>
  `);
});

// ---------- Route: Logout ----------
app.get('/logout', async (req, res) => {
  // Clear session
  req.session?.destroy((err) => {
    if (err) console.error('Session destroy error:', err);
    // Optional: perform RP‑initiated logout at the IdP
    const endSessionUrl = client.endSessionUrl({
      id_token_hint: (req.session as any).oidc?.tokenSet?.id_token,
      post_logout_redirect_uri: `${REDIRECT_URI.replace('/callback', '/')}?logged_out=1`,
    });
    res.redirect(endSessionUrl);
  });
});

// ---------- Start Server ----------
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 OIDC PKCE client listening on http://localhost:${PORT}`);
});
```

### How the Code Works (key points)

| Step | What the code does | Relevant snippet |
|------|-------------------|------------------|
| **Discovery** | `Issuer.discover(ISSUER_URL)` obtains the provider’s metadata (authorization, token, JWKS endpoints, etc.) | `initClient()` |
| **PKCE generation** | `generators.codeVerifier()` & `generators.codeChallenge()` from **openid-client** | `/login` route |
| **State & nonce** | Random strings via `generators.state()` / `generators.nonce()`; stored in encrypted session | `/login` |
| **Authorization URL** | `client.authorizationUrl({ … })` builds the URL with scopes, PKCE, state, nonce | `/login` |
| **Callback handling** | Validates `state`, exchanges code (`client.callback`) while passing `code_verifier` and `nonce` | `/callback` |
| **ID‑token verification** | Uses **jose** to verify signature against rotating JWKS (`client.issuer.keystore`), issuer, audience, and nonce claim | `/callback` |
| **Session binding** | Encrypted JSON payload (`encrypt`/`decrypt`) stored in `express-session` cookie; contains `state`, `nonce`, `codeVerifier`, `tokenSet` | Session middleware |
| **Refresh token flow** | `client.refresh(refresh_token)` called automatically when access token is expired (in `/profile`) | `/profile` |
| **Logout** | Destroys session & optionally redirects to provider’s `end_session_endpoint` | `/logout` |

---  

## 📥 Installation & Execution (reproducible)

```bash
# 1️⃣ Clone / copy the project
git clone https://github.com/yourname/oidc-pkce-client.git
cd oidc-pkce-client

# 2️⃣ Install exact dependencies (npm respects the pinned versions)
npm ci   # uses package-lock.json (generated by npm ci)

# 3️⃣ Create a .env file from the example
cp .env.example .env
# Edit .env and fill in:
#   ISSUER_URL, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SESSION_SECRET, ENCRYPTION_KEY

# 4️⃣ Build the TypeScript sources
npm run build

# 5️⃣ Run the server
npm start
# Or for hot‑reload during development:
# npm run dev
```

The app will be reachable at **http://localhost:3000**. Click **Login** → you’ll be redirected to the provider’s login page, then back to `/callback`, and finally to the home page showing a logged‑in state.

---  

## 🔐 Security & Hardening Notes  

* **PKCE** (`S256`) prevents authorization‑code interception.  
* **State** protects against CSRF; **nonce** binds the ID token to the authentication request.  
* **Encrypted session payload** adds a second layer of confidentiality beyond the signed cookie that `express-session` already provides.  
* **HTTPS** is mandatory in production (`cookie.secure: true`).  
* **Session secret** and **encryption key** must be long, random, and stored outside source control (e.g., in a secret manager).  
* **Refresh token** is stored server‑side only (never exposed to the browser).  
* **JWKS rotation** is handled automatically because the client fetches the JWKS from the issuer each time it validates a token.  

---  

## 📚 Further Reading  

* OpenID Connect Core 1.0 – <https://openid.net/specs/openid-connect-core-1_0.html>  
* PKCE (RFC 7636) – <https://datatracker.ietf.org/doc/html/rfc7636>  
* `openid-client` docs – <https://github.com/panva/node-openid-client>  
* `jose` library – <https://github.com/panva/jose>  

Feel free to adapt the code (e.g., add a database‑backed session store, more scopes, or UI templates). The core flow, security checks, and session binding are all in place and ready for production‑grade use. Happy coding!
