Below is a **self‑contained Node.js + TypeScript** project that implements a confidential web client for the **OpenID Connect Authorization Code flow with PKCE**. It discovers the issuer metadata, generates/validates state, nonce, and PKCE values, exchanges the authorization code, validates the ID token (issuer, audience, signature, time claims, nonce) against rotating JWKS keys, and refreshes tokens while preserving session binding. It also provides login, callback, refresh, and logout routes, a minimal encrypted server‑side session representation, and a runnable example with configurable issuer and client values.

---

## 📂 Project Structure

```
project-root/
├── package.json
├── tsconfig.json
├── .env.example
├── src/
│   ├── config.ts
│   ├── oidc.ts
│   ├── session.ts
│   ├── routes.ts
│   ├── app.ts
│   └── utils.ts
└── README.md
```

All source files are **TypeScript** and will be compiled to `dist/` during build.

---

## 📦 `package.json`

```json
{
  "name": "oidc-client-demo",
  "version": "0.0.1",
  "description": "Confidential OIDC web client with PKCE, session binding, and token refresh.",
  "main": "dist/app.js",
  "scripts": {
    "dev": "ts-node src/app.ts",
    "build": "tsc",
    "start": "node dist/app.js"
  },
  "keywords": ["oidc", "openid", "pkce", "auth", "typescript", "express"],
  "author": "",
  "license": "MIT",
  "dependencies": {
    "express": "^4.18.2",
    "express-session": "^1.17.3",
    "openid-client": "^7.14.0",
    "jsonwebtoken": "^9.0.2",
    "jwk-to-pem": "^2.0.5",
    "nanoid": "^3.3.7",
    "dotenv": "^16.3.1",
    "helmet": "^7.0.0",
    "cors": "^2.8.5",
    "morgan": "^1.10.0",
    "cookie-parser": "^1.4.6"
  },
  "devDependencies": {
    "typescript": "^5.3.3",
    "ts-node": "^10.9.2"
  }
}
```

**Key APIs used**

| Package | API(s) |
|---------|--------|
| `express` | `express()`, `Request`, `Response`, `NextFunction` |
| `express-session` | `session({ secret, resave, saveUninitialized, cookie })` |
| `openid-client` | `Issuer.discover()`, `Issuer.Client`, `authorizationUrl()`, `oauthCallback()`, `refresh()`, `validateIdToken()` |
| `jsonwebtoken` | `jwt.verify()` (optional manual validation) |
| `jwk-to-pem` | `jwkToPem(jwk)` |
| `nanoid` | `nanoid()` |
| `crypto` (built‑in) | `createHash('sha256')`, `randomBytes()` |
| `dotenv` | `config()` |
| `helmet`, `cors`, `morgan`, `cookie-parser` | standard middleware |

---

## ⚙️ `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "strict": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "skipLibCheck": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true
  }
}
```

---

## 🔐 `src/config.ts`

```ts
import * as dotenv from "dotenv";

dotenv.config();

export interface OidcConfig {
  issuerUrl: string;
  clientId: string;
  clientSecret: string;
  redirectUri: string;
  postLogoutRedirectUri: string;
  scope: string;
  codeChallengeMethod: string;
  sessionSecret: string;
  sessionMaxAge: number;
}

export const config: OidcConfig = {
  // Replace with your OIDC provider – this demo uses placeholders.
  issuerUrl: process.env.OIDC_ISSUER_URL || "https://auth.example.com",
  clientId: process.env.OIDC_CLIENT_ID || "demo-client",
  clientSecret: process.env.OIDC_CLIENT_SECRET || "demo-secret",
  redirectUri: process.env.OIDC_REDIRECT_URI || "http://localhost:3000/callback",
  postLogoutRedirectUri:
    process.env.OIDC_POST_LOGOUT_REDIRECT_URI || "http://localhost:3000/",
  scope: "openid profile email",
  codeChallengeMethod: "S256",
  // Used to sign the server‑side session cookie.
  sessionSecret: process.env.SESSION_SECRET || "change-this-in-production",
  sessionMaxAge: 3600000, // 1 hour (ms)
};
```

---

## 🛠️ `src/utils.ts`

```ts
import { randomBytes } from "crypto";
import { nanoid } from "nanoid";

/**
 * Generates a URL‑safe random string of the given length (default 32).
 */
export function generateRandomString(length: number = 32): string {
  return nanoid(length);
}

/**
 * Generates a PKCE code verifier (43‑128 characters, URL‑safe).
 */
export function generateCodeVerifier(): string {
  return generateRandomString(64);
}

/**
 * Derives a PKCE code challenge from a verifier using SHA‑256 + base64url.
 */
export function generateCodeChallenge(verifier: string): string {
  const hash = require("crypto").createHash("sha256").update(verifier).digest();
  return base64url(hash);
}

/**
 * Base64‑URL encodes a Buffer (RFC 4648, no padding).
 */
export function base64url(data: Buffer): string {
  return data
    .toString("base64")
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=/g, "");
}
```

---

## 🔍 `src/oidc.ts`

```ts
import { Issuer, generators, TokenSet } from "openid-client";
import { OidcConfig } from "./config";
import { generateCodeVerifier, generateCodeChallenge } from "./utils";

/**
 * Service that wraps the openid‑client library and adds custom PKCE handling.
 */
export class OidcService {
  private issuer!: Issuer;
  private client!: InstanceType<ReturnType<typeof Issuer.prototype.Client>>;
  private config: OidcConfig;

  constructor(config: OidcConfig) {
    this.config = config;
  }

  /**
   * Discovers the provider and creates a client instance.
   */
  public async init(): Promise<void> {
    this.issuer = await Issuer.discover(this.config.issuerUrl);
    this.client = new this.issuer.Client({
      client_id: this.config.clientId,
      client_secret: this.config.clientSecret,
      redirect_uris: [this.config.redirectUri],
      response_types: ["code"],
    });
  }

  /**
   * Builds the authorization URL for the OIDC provider.
   */
  public authorizationUrl(state: string, nonce: string, codeVerifier: string): string {
    const code_challenge = generateCodeChallenge(codeVerifier);
    return this.client.authorizationUrl({
      scope: this.config.scope,
      state,
      nonce,
      code_challenge,
      code_challenge_method: this.config.codeChallengeMethod,
    });
  }

  /**
   * Exchanges an authorization `code` for tokens.
   * The `state` is validated by `openid-client` internally.
   */
  public async exchangeCode(
    code: string,
    codeVerifier: string,
    state: string
  ): Promise<TokenSet> {
    const params = {
      code,
      grant_type: "authorization_code",
      redirect_uri: this.config.redirectUri,
      code_verifier: codeVerifier,
    };
    // `oauthCallback` performs PKCE verification, state check, and token exchange.
    return await this.client.oauthCallback(this.config.redirectUri, params, { state });
  }

  /**
   * Refreshes an access token using a refresh token.
   */
  public async refreshToken(refreshToken: string): Promise<TokenSet> {
    return await this.client.refresh(refreshToken);
  }

  /**
   * Validates an ID token against the client configuration.
   * Uses `openid-client`'s built‑in validation (issuer, audience, nonce, exp, signature).
   */
  public validateIdToken(
    idToken: string,
    nonce: string,
    clientId: string
  ): Record<string, unknown> {
    // `validateIdToken` returns the decoded payload if validation succeeds.
    return this.client.validateIdToken(idToken, {
      audience: clientId,
      nonce,
      // The issuer is already known from discovery.
    });
  }

  /**
   * Builds a logout URL for the provider.
   */
  public endSessionUrl(idTokenHint?: string): string {
    return this.client.endSessionUrl({
      post_logout_redirect_uri: this.config.postLogoutRedirectUri,
      id_token_hint: idTokenHint,
    });
  }
}
```

*Key APIs used from `openid-client`*

- `Issuer.discover(url)` – discovers `.well‑known/openid-configuration`.
- `Issuer.Client(options)` – creates a confidential client.
- `authorizationUrl(params)` – builds the auth request URL.
- `oauthCallback(redirectUri, params, options)` – validates PKCE, state, and exchanges the code.
- `refresh(refreshToken)` – obtains new tokens.
- `validateIdToken(token, options)` – verifies issuer, audience, nonce, expiration, and signature using the provider’s JWKS.
- `endSessionUrl(params)` – builds the RP‑initiated logout URL.

---

## 📝 `src/session.ts`

```ts
import { Request, Response, NextFunction } from "express";

/**
 * Middleware that attaches a stable session identifier to each request.
 * The identifier is stored in the server‑side session store (express‑session).
 */
export function attachSessionId(
  req: Request,
  res: Response,
  next: NextFunction
): void {
  if (!req.session) {
    throw new Error("Session middleware not loaded");
  }
  if (!req.session.id) {
    // `express-session` automatically creates a session ID on first use.
    // We expose it for convenience.
    req.session.id = (req.session as any).id;
  }
  next();
}

/**
 * Clears the server‑side session data.
 */
export function clearSession(req: Request, res: Response, next: NextFunction): void {
  if (req.session) {
    req.session.destroy((err) => {
      if (err) {
        console.error("Error destroying session", err);
      }
      // Continue without session.
    });
  }
  next();
}
```

*Explanation*: `express-session` already encrypts the session cookie and stores the session data on the server (in‑memory by default). The `attachSessionId` middleware simply exposes the session identifier for later binding checks.

---

## 🛣️ `src/routes.ts`

```ts
import { Router, Request, Response, NextFunction } from "express";
import { OidcService } from "./oidc";
import { config } from "./config";
import { generateRandomString, generateCodeVerifier, generateCodeChallenge } from "./utils";
import { attachSessionId, clearSession } from "./session";

/**
 * Helper to safely get the OIDC service from Express app locals.
 */
function getOidc(req: Request): OidcService {
  if (!req.app.locals.oidc) {
    throw new Error("OIDC service not initialized");
  }
  return req.app.locals.oidc as OidcService;
}

/**
 * Creates the Express router with login, callback, refresh, and logout routes.
 */
export function createRouter() {
  const router = Router();

  // ---------- Login ----------
  router.get("/login", (req: Request, res: Response, next: NextFunction) => {
    // Generate OIDC state, nonce, and PKCE verifier.
    const state = generateRandomString();
    const nonce = generateRandomString();
    const codeVerifier = generateCodeVerifier();

    // Store them in the server‑side session for later verification.
    if (!req.session) {
      return res.status(500).send("Session not available");
    }
    (req.session as any).oidc = {
      state,
      nonce,
      codeVerifier,
      // Session binding identifier (used to tie tokens to this session).
      sessionId: (req.session as any).id,
    };

    const oidc = getOidc(req);
    const authUrl = oidc.authorizationUrl(state, nonce, codeVerifier);
    res.redirect(authUrl);
  });

  // ---------- Callback ----------
  router.get("/callback", async (req: Request, res: Response, next: NextFunction) => {
    const { code, state } = req.query as { code?: string; state?: string };

    if (!code || !state) {
      return res.status(400).send("Missing code or state parameters");
    }

    const session = (req.session as any).oidc;
    if (!session) {
      return res.status(400).send("No OIDC session data found");
    }

    // Verify state matches.
    if (session.state !== state) {
      return res.status(400).send("State mismatch – possible CSRF");
    }

    const oidc = getOidc(req);
    try {
      const tokenSet = await oidc.exchangeCode(code, session.codeVerifier, state);

      // Validate ID token (issuer, audience, nonce, signature, expiration).
      const payload = oidc.validateIdToken(tokenSet.id_token, session.nonce, config.clientId);

      // Optional: fetch userinfo (not shown for brevity).
      // const userinfo = await oidc.client.userinfo(tokenSet.access_token);
      // const user = await userinfo.json();

      // Update server‑side session with tokens and binding info.
      if (!req.session) {
        return res.status(500).send("Session not available");
      }
      (req.session as any).oidc = {
        ...session,
        tokens: {
          accessToken: tokenSet.access_token,
          refreshToken: tokenSet.refresh_token,
          idToken: tokenSet.id_token,
          expiresAt: Date.now() + tokenSet.expires_in! * 1000,
        },
        // Store the session identifier from the ID token if present (e.g., `sid` claim).
        sidClaim: payload.sid || null,
      };

      // Redirect to the application home (or any post‑login page).
      res.redirect("/");
    } catch (err) {
      console.error("OIDC callback error", err);
      res.status(500).send("Authentication failed");
    }
  });

  // ---------- Refresh ----------
  router.get("/refresh", async (req: Request, res: Response, next: NextFunction) => {
    const session = (req.session as any).oidc;
    if (!session || !session.tokens?.refreshToken) {
      return res.status(401).send("No refresh token available");
    }

    const oidc = getOidc(req);
    try {
      const tokenSet = await oidc.refreshToken(session.tokens.refreshToken);

      // Validate the new ID token (ensures issuer, audience, nonce, etc.).
      const payload = oidc.validateIdToken(tokenSet.id_token, session.nonce, config.clientId);

      // Ensure session binding – if the provider returns a `sid` claim, it must match.
      if (session.sidClaim && payload.sid !== session.sidClaim) {
        throw new Error("Session identifier mismatch after token refresh");
      }

      // Update session with fresh tokens.
      (req.session as any).oidc.tokens = {
        accessToken: tokenSet.access_token,
        refreshToken: tokenSet.refresh_token,
        idToken: tokenSet.id_token,
        expiresAt: Date.now() + tokenSet.expires_in! * 1000,
      };
      (req.session as any).oidc.sidClaim = payload.sid || session.sidClaim;

      res.json({
        accessToken: tokenSet.access_token,
        expiresIn: tokenSet.expires_in,
      });
    } catch (err) {
      console.error("Token refresh error", err);
      res.status(500).send("Failed to refresh token");
    }
  });

  // ---------- Logout ----------
  router.get("/logout", (req: Request, res: Response, next: NextFunction) => {
    const session = (req.session as any).oidc;
    const idTokenHint = session?.tokens?.idToken;

    // Clear the server‑side session.
    clearSession(req, res, () => {
      const oidc = getOidc(req);
      const logoutUrl = oidc.endSessionUrl(idTokenHint);
      res.redirect(logoutUrl);
    });
  });

  // ---------- Home (protected) ----------
  router.get("/", attachSessionId, (req: Request, res: Response) => {
    const session = (req.session as any).oidc;
    if (!session?.tokens) {
      return res.redirect("/login");
    }

    // Simple UI – show token expiry and a refresh button.
    const expiresAt = session.tokens.expiresAt
      ? new Date(session.tokens.expiresAt).toLocaleString()
      : "N/A";
    res.send(`
      <h1>OIDC Client Demo</h1>
      <p>Access Token (excerpt): ${session.tokens.accessToken.slice(0, 20)}…</p>
      <p>Expires at: ${expiresAt}</p>
      <a href="/refresh">Refresh Token</a> |
      <a href="/logout">Logout</a>
    `);
  });

  return router;
}
```

*Key points*  

- **State & Nonce** are generated on `/login` and stored server‑side.  
- **PKCE** (`codeVerifier`, `codeChallenge`) is handled manually; `openid-client` validates it during token exchange.  
- **ID token validation** uses `oidc.validateIdToken` which internally checks issuer, audience, nonce, expiration, and signature against the provider’s JWKS.  
- **Session binding** is preserved by storing a `sessionId` (the Express‑session identifier) and optionally a `sid` claim from the ID token. The refresh endpoint verifies that the `sid` (if present) matches.  
- **Logout** clears the server‑side session and redirects to the provider’s logout endpoint.

---

## 🚀 `src/app.ts`

```ts
import express, { Request, Response, NextFunction } from "express";
import helmet from "helmet";
import cors from "cors";
import morgan from "morgan";
import cookieParser from "cookie-parser";
import session from "express-session";
import { config } from "./config";
import { createRouter } from "./routes";
import { OidcService } from "./oidc";

// Initialize Express app.
const app = express();
const PORT = process.env.PORT || 3000;

// Security & logging middleware.
app.use(helmet());
app.use(cors());
app.use(morgan("combined"));
app.use(cookieParser());

// Session middleware – signed cookies, in‑memory store.
app.use(
  session({
    secret: config.sessionSecret,
    resave: false,
    saveUninitialized: false,
    cookie: {
      secure: config.issuerUrl.startsWith("https"), // enforce HTTPS in production
      httpOnly: true,
      maxAge: config.sessionMaxAge,
    },
  })
);

// Instantiate and initialise the OIDC service.
// `async` init is performed once at startup.
(async () => {
  const oidc = new OidcService(config);
  await oidc.init();
  app.locals.oidc = oidc;
})();

// Mount application routes.
app.use("/", createRouter());

// Global error handler (optional).
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error(err.stack);
  res.status(500).send("Something went wrong!");
});

// Start the server.
app.listen(PORT, () => {
  console.log(`OIDC client demo listening on http://localhost:${PORT}`);
});
```

---

## 📄 `.env.example`

```env
# OIDC Provider configuration
OIDC_ISSUER_URL=https://auth.example.com
OIDC_CLIENT_ID=demo-client
OIDC_CLIENT_SECRET=demo-secret
OIDC_REDIRECT_URI=http://localhost:3000/callback
OIDC_POST_LOGOUT_REDIRECT_URI=http://localhost:3000/

# Server‑side session secret – keep this secret in production!
SESSION_SECRET=change-this-in-production

# Optional: override default port
PORT=3000
```

---

## 📋 Installation & Execution

1. **Create a new directory** and place the files above inside a `src/` folder.

2. **Initialize the project** (if you have a `package.json` already, skip to step 3):
   ```bash
   npm init -y
   ```

3. **Install dependencies** (using the exact versions from `package.json`):
   ```bash
   npm install
   ```

4. **Build the TypeScript sources** (produces `dist/`):
   ```bash
   npm run build
   ```

5. **Run the application** (development mode – uses `ts-node` to avoid rebuilding):
   ```bash
   npm run dev
   ```

   In production you would run:
   ```bash
   npm start
   ```

6. **Configure your OIDC provider** by editing `.env` (or creating one from `.env.example`). The demo uses placeholder values; replace them with a real provider (e.g., Auth0, Keycloak, Google APIs, etc.) that supports the Authorization Code flow with PKCE.

7. **Open the browser** and navigate to `http://localhost:3000/login`. You will be redirected to the provider’s consent page, then back to the client’s callback handler. The home page will display token information and provide a “Refresh Token” link.

---

## 📚 Summary of Package APIs Used

| Package | Core APIs Used |
|---------|----------------|
| `express` | `express()`, `Router()`, `Request`, `Response`, `NextFunction` |
| `express-session` | `session({ secret, resave, saveUninitialized, cookie })` |
| `openid-client` | `Issuer.discover()`, `Issuer.Client()`, `authorizationUrl()`, `oauthCallback()`, `refresh()`, `validateIdToken()`, `endSessionUrl()` |
| `jsonwebtoken` | `jwt.verify()` (optional manual validation) |
| `jwk-to-pem` | `jwkToPem(jwk)` (used if manual signature verification is needed) |
| `nanoid` | `nanoid()` |
| `crypto` (built‑in) | `createHash('sha256')`, `randomBytes()` |
| `dotenv` | `config()` |
| `helmet`, `cors`, `morgan`, `cookie-parser` | standard middleware |

All OIDC‑specific logic (discovery, PKCE generation/validation, token exchange, ID token verification, logout) is **vendor‑agnostic** and works with any OpenID Connect‑compatible provider that supports the Authorization Code flow with PKCE.

---
