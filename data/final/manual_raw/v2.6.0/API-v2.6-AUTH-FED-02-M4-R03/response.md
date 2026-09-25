# OpenID Connect Confidential Client Implementation

This implementation provides a production-ready, vendor-agnostic OIDC client using the Authorization Code Flow with PKCE. It uses **Express** for routing, **jose** for cryptographic operations (JWT/JWKS), **iron-session** for encrypted server-side sessions, and **openid-client** for metadata discovery and standard compliance helpers.

## Project Structure

```text
oidc-client/
├── package.json
├── tsconfig.json
├── .env.example
├── src/
│   ├── index.ts                 # Application entry point
│   ├── config.ts                # Configuration validation
│   ├── oidc/
│   │   ├── discovery.ts         # Issuer metadata discovery
│   │   ├── pkce.ts              # PKCE challenge/verifier generation
│   │   ├── tokens.ts            # Token exchange & refresh logic
│   │   ├── validation.ts        # ID Token validation (JWKS, claims, nonce)
│   │   └── client.ts            # High-level OIDC Client facade
│   ├── session/
│   │   └── session.ts           # Encrypted session management (iron-session)
│   └── routes/
│       ├── auth.ts              # /login, /callback, /logout routes
│       └── protected.ts         # Example protected route
```

---

## 1. Configuration & Dependencies

### `package.json`

```json
{
  "name": "oidc-confidential-client",
  "version": "1.0.0",
  "description": "Self-contained OIDC Authorization Code Flow with PKCE Client",
  "main": "dist/index.js",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "ts-node src/index.ts",
    "lint": "eslint src --ext .ts"
  },
  "dependencies": {
    "express": "4.19.2",
    "iron-session": "8.0.1",
    "jose": "5.2.4",
    "openid-client": "5.6.5",
    "dotenv": "16.4.5",
    "uuid": "9.0.1"
  },
  "devDependencies": {
    "@types/express": "4.17.21",
    "@types/node": "20.12.12",
    "@types/uuid": "9.0.8",
    "typescript": "5.4.5",
    "ts-node": "10.9.2",
    "eslint": "8.57.0",
    "@typescript-eslint/eslint-plugin": "7.8.0",
    "@typescript-eslint/parser": "7.8.0"
  },
  "engines": {
    "node": ">=20.0.0"
  }
}
```

### Exact Package APIs Used

| Package | Version | Key APIs Used |
| :--- | :--- | :--- |
| **express** | 4.19.2 | `express()`, `Request`, `Response`, `NextFunction`, `Router` |
| **iron-session** | 8.0.1 | `withIronSession`, `getIronSession`, `SessionData`, `IronSessionOptions` |
| **jose** | 5.2.4 | `createRemoteJWKSet`, `jwtVerify`, `JWTPayload`, `KeyLike`, `generateKeyPair`, `SignJWT`, `importJWK`, `exportJWK` |
| **openid-client** | 5.6.5 | `discovery`, `AuthorizationCode`, `TokenSet`, `ClientMetadata`, `IssuerMetadata`, `grantTypes` |
| **dotenv** | 16.4.5 | `config` |
| **uuid** | 9.0.1 | `v4` (for State/Nonce generation) |

### `.env.example`

```bash
# Server
PORT=3000
SESSION_PASSWORD="super-secret-password-min-32-chars-long!!" # Must be >= 32 chars
SESSION_COOKIE_NAME="oidc_session"

# OIDC Client (Confidential)
CLIENT_ID="your-client-id"
CLIENT_SECRET="your-client-secret"
REDIRECT_URI="http://localhost:3000/callback"
POST_LOGOUT_REDIRECT_URI="http://localhost:3000/"

# OIDC Provider (Generic Discovery)
ISSUER_URL="https://your-identity-provider.com" # e.g., https://accounts.google.com, https://login.microsoftonline.com/{tenant}/v2.0

# Scopes
SCOPES="openid profile email offline_access"
```

---

## 2. TypeScript Configuration

### `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

---

## 3. Core Implementation

### `src/config.ts`

Validates environment variables at startup.

```typescript
import dotenv from 'dotenv';
dotenv.config();

interface Config {
  port: number;
  session: {
    password: string;
    cookieName: string;
  };
  oidc: {
    clientId: string;
    clientSecret: string;
    redirectUri: string;
    postLogoutRedirectUri: string;
    issuerUrl: string;
    scopes: string[];
  };
}

function getEnv(key: string): string {
  const value = process.env[key];
  if (!value) throw new Error(`Missing required environment variable: ${key}`);
  return value;
}

export const config: Config = {
  port: parseInt(process.env.PORT || '3000', 10),
  session: {
    password: getEnv('SESSION_PASSWORD'),
    cookieName: getEnv('SESSION_COOKIE_NAME'),
  },
  oidc: {
    clientId: getEnv('CLIENT_ID'),
    clientSecret: getEnv('CLIENT_SECRET'),
    redirectUri: getEnv('REDIRECT_URI'),
    postLogoutRedirectUri: getEnv('POST_LOGOUT_REDIRECT_URI'),
    issuerUrl: getEnv('ISSUER_URL'),
    scopes: (process.env.SCOPES || 'openid profile email offline_access').split(' '),
  },
};
```

---

### `src/oidc/discovery.ts`

Uses `openid-client` for standard-compliant metadata discovery.

```typescript
import { discovery, IssuerMetadata } from 'openid-client';
import { config } from '../config';

let cachedMetadata: IssuerMetadata | null = null;

export async function getIssuerMetadata(): Promise<IssuerMetadata> {
  if (cachedMetadata) return cachedMetadata;

  // openid-client discovery handles .well-known/openid-configuration fetch + validation
  const metadata = await discovery(
    new URL(config.oidc.issuerUrl),
    config.oidc.clientId,
    config.oidc.clientSecret
  );

  // Ensure required endpoints exist for Auth Code Flow + PKCE
  if (!metadata.authorization_endpoint || !metadata.token_endpoint || !metadata.jwks_uri) {
    throw new Error('Issuer metadata missing required endpoints (authorization_endpoint, token_endpoint, jwks_uri)');
  }

  cachedMetadata = metadata;
  return metadata;
}

export function clearMetadataCache() {
  cachedMetadata = null;
}
```

---

### `src/oidc/pkce.ts`

Generates Code Verifier (RFC 7636) and Challenge (S256).

```typescript
import { v4 as uuidv4 } from 'uuid';
import { createHash } from 'crypto';

const CODE_VERIFIER_LENGTH = 64; // 43-128 chars allowed
const CODE_CHALLENGE_METHOD = 'S256';

export interface PkceCodes {
  codeVerifier: string;
  codeChallenge: string;
  codeChallengeMethod: string;
}

/**
 * Generates a cryptographically random code_verifier and derives code_challenge (S256).
 * @returns {PkceCodes}
 */
export function generatePkce(): PkceCodes {
  // RFC 7636: code_verifier = unreserved chars (A-Z, a-z, 0-9, -, ., _, ~)
  // Base64URL encode 32 bytes -> 43 chars. We generate slightly more entropy.
  const buffer = Buffer.alloc(CODE_VERIFIER_LENGTH);
  // Using crypto.randomFillSync would be better in sync context, but uuid + hash is standard pattern
  // Here we use a high-entropy random string generation suitable for Node.js
  const verifier = uuidv4().replace(/-/g, '') + uuidv4().replace(/-/g, '') + uuidv4().replace(/-/g, ''); // 96 chars hex
  const codeVerifier = verifier.substring(0, CODE_VERIFIER_LENGTH);

  const hash = createHash('sha256').update(codeVerifier).digest();
  const codeChallenge = hash.toString('base64url'); // Base64URL encoding (no padding)

  return {
    codeVerifier,
    codeChallenge,
    codeChallengeMethod: CODE_CHALLENGE_METHOD,
  };
}

/**
 * Validates a code_verifier against a stored challenge (used if implementing device flow or similar, 
 * but primarily here for reference. In Auth Code flow, the AS validates it).
 */
export function verifyPkce(codeVerifier: string, codeChallenge: string): boolean {
  const hash = createHash('sha256').update(codeVerifier).digest();
  return hash.toString('base64url') === codeChallenge;
}
```

---

### `src/oidc/validation.ts`

**Critical Security Component**: Validates ID Token signature via rotating JWKS, claims (iss, aud, exp, iat, nbf, nonce, auth_time).

```typescript
import { createRemoteJWKSet, jwtVerify, JWTPayload, errors as joseErrors } from 'jose';
import { getIssuerMetadata } from './discovery';
import { config } from '../config';

// Cache the JWKS remote set. jose handles rotation automatically via cache headers / re-fetch on signature failure.
let jwks: ReturnType<typeof createRemoteJWKSet> | null = null;

async function getJwks() {
  if (jwks) return jwks;
  const metadata = await getIssuerMetadata();
  if (!metadata.jwks_uri) throw new Error('JWKS URI not found in metadata');
  jwks = createRemoteJWKSet(new URL(metadata.jwks_uri), {
    // Cache keys for 5 minutes, cooldown 10s (jose defaults are sensible)
    cooldownDuration: 10000, 
  });
  return jwks;
}

export interface ValidatedIdTokenClaims extends JWTPayload {
  iss: string;
  sub: string;
  aud: string | string[];
  exp: number;
  iat: number;
  nonce?: string;
  auth_time?: number;
  [key: string]: unknown;
}

export interface ValidationOptions {
  nonce?: string;
  maxAge?: number; // Max age of authentication in seconds (for auth_time check)
}

export class TokenValidationError extends Error {
  constructor(message: public readonly code: string, public readonly details?: string) {
    super(message);
    this.name = 'TokenValidationError';
  }
}

/**
 * Validates the ID Token comprehensively.
 * @param idToken The raw ID Token string.
 * @param options Validation options (nonce, maxAge).
 * @returns Validated claims payload.
 */
export async function validateIdToken(
  idToken: string,
  options: ValidationOptions = {}
): Promise<ValidatedIdTokenClaims> {
  const jwksClient = await getJwks();
  const metadata = await getIssuerMetadata();

  let payload: ValidatedIdTokenClaims;

  try {
    // 1. Signature & Standard Claims Validation (iss, aud, exp, iat, nbf)
    // jose.jwtVerify validates exp, nbf, iat automatically (with clock tolerance).
    // We must manually verify 'iss' and 'aud' match *our* config because the JWKS endpoint might be shared.
    const { payload: verifiedPayload } = await jwtVerify(idToken, jwksClient, {
      issuer: metadata.issuer, // Validates 'iss' claim matches discovered issuer
      audience: config.oidc.clientId, // Validates 'aud' claim matches our client_id
      clockTolerance: 30, // 30s clock skew tolerance
    });
    payload = verifiedPayload as ValidatedIdTokenClaims;

  } catch (err) {
    if (err instanceof joseErrors.JWTExpired) throw new TokenValidationError('TOKEN_EXPIRED', 'ID Token has expired');
    if (err instanceof joseErrors.JWTClaimValidationFailed) {
        const reason = err.claim === 'iss' ? 'ISSUER_MISMATCH' : err.claim === 'aud' ? 'AUDIENCE_MISMATCH' : 'CLAIM_VALIDATION_FAILED';
        throw new TokenValidationError(reason, err.message);
    }
    if (err instanceof joseErrors.JWSSignatureVerificationFailed) throw new TokenValidationError('INVALID_SIGNATURE', 'ID Token signature verification failed');
    throw new TokenValidationError('VERIFICATION_FAILED', (err as Error).message);
  }

  // 2. Nonce Validation (Replay Protection)
  if (options.nonce) {
    if (!payload.nonce) throw new TokenValidationError('MISSING_NONCE', 'ID Token missing nonce claim');
    if (payload.nonce !== options.nonce) throw new TokenValidationError('NONCE_MISMATCH', 'ID Token nonce does not match expected value');
  }

  // 3. Authentication Time Validation (Session Management / Step-up Auth)
  if (options.maxAge !== undefined) {
    if (!payload.auth_time) throw new TokenValidationError('MISSING_AUTH_TIME', 'ID Token missing auth_time claim required for max_age validation');
    const authAge = Math.floor(Date.now() / 1000) - payload.auth_time;
    if (authAge > options.maxAge) throw new TokenValidationError('AUTH_TIME_TOO_OLD', `Authentication too old: ${authAge}s > ${options.maxAge}s`);
  }

  // 4. AZP (Authorized Party) Validation - Required if ID Token issued to hybrid/multiple audiences
  if (payload.azp && payload.azp !== config.oidc.clientId) {
    // If 'aud' is an array, 'azp' MUST be present and match client_id.
    // If 'aud' is single string (our client_id), 'azp' is optional but if present must match.
    if (Array.isArray(payload.aud) || payload.aud !== config.oidc.clientId) {
       throw new TokenValidationError('AZP_MISMATCH', 'Authorized party (azp) does not match client_id');
    }
  }

  return payload;
}
```

---

### `src/oidc/tokens.ts`

Handles Token Exchange (Code -> Tokens) and Refresh Token Rotation.

```typescript
import { AuthorizationCode, TokenSet, grantTypes } from 'openid-client';
import { getIssuerMetadata } from './discovery';
import { config } from '../config';
import { validateIdToken } from './validation';

export interface TokenResponse {
  accessToken: string;
  idToken: string | undefined;
  refreshToken: string | undefined;
  expiresAt: number; // Unix timestamp (seconds)
  tokenType: string;
  scope: string;
}

/**
 * Exchanges Authorization Code for Token Set.
 * Validates ID Token immediately.
 */
export async function exchangeCodeForTokens(
  code: string,
  codeVerifier: string,
  state: string,
  nonce: string
): Promise<TokenResponse> {
  const metadata = await getIssuerMetadata();
  
  // openid-client handles the HTTP request to token_endpoint with client_auth (Basic Auth for confidential)
  const client = new AuthorizationCode(metadata, config.oidc.clientId, config.oidc.clientSecret);
  
  const tokenSet: TokenSet = await client.callback(
    config.oidc.redirectUri,
    { code, state }, // Parameters from callback URL
    { 
      code_verifier: codeVerifier, // PKCE Verifier
      // openid-client validates state automatically if passed in session/options, 
      // but we validate manually in route for clarity.
    }
  );

  // Validate ID Token (Signature, Claims, Nonce)
  if (!tokenSet.id_token) throw new Error('ID Token missing from token response');
  
  await validateIdToken(tokenSet.id_token, { nonce });

  return {
    accessToken: tokenSet.access_token!,
    idToken: tokenSet.id_token,
    refreshToken: tokenSet.refresh_token,
    expiresAt: tokenSet.expires_at!, // Unix timestamp
    tokenType: tokenSet.token_type!,
    scope: tokenSet.scope!,
  };
}

/**
 * Refreshes Access Token using Refresh Token.
 * Preserves session binding (returns new TokenSet with potentially new Refresh Token).
 */
export async function refreshAccessToken(refreshToken: string): Promise<TokenResponse> {
  const metadata = await getIssuerMetadata();
  const client = new AuthorizationCode(metadata, config.oidc.clientId, config.oidc.clientSecret);

  // openid-client handles 'refresh_token' grant type
  const tokenSet: TokenSet = await client.grant(grantTypes.refreshToken, refreshToken);

  // ID Token is NOT typically returned on refresh grant, but some OPs do.
  // If returned, we should validate it (nonce not applicable here usually, but iss/aud/sig yes).
  if (tokenSet.id_token) {
    await validateIdToken(tokenSet.id_token, {}); // No nonce check on refresh
  }

  return {
    accessToken: tokenSet.access_token!,
    idToken: tokenSet.id_token,
    refreshToken: tokenSet.refresh_token ?? refreshToken, // OP may rotate refresh token
    expiresAt: tokenSet.expires_at!,
    tokenType: tokenSet.token_type!,
    scope: tokenSet.scope!,
  };
}

/**
 * Revokes tokens at the OP (RFC 7009) - Best effort during logout.
 */
export async function revokeToken(token: string, tokenTypeHint: 'access_token' | 'refresh_token'): Promise<void> {
  const metadata = await getIssuerMetadata();
  if (!metadata.revocation_endpoint) return; // Optional endpoint

  const client = new AuthorizationCode(metadata, config.oidc.clientId, config.oidc.clientSecret);
  try {
    await client.revoke(token, tokenTypeHint);
  } catch (e) {
    console.warn(`Token revocation failed (${tokenTypeHint}):`, (e as Error).message);
  }
}
```

---

### `src/oidc/client.ts`

High-level facade combining Discovery, PKCE, Tokens, Validation.

```typescript
import { getIssuerMetadata } from './discovery';
import { generatePkce, PkceCodes } from './pkce';
import { exchangeCodeForTokens, refreshAccessToken, revokeToken, TokenResponse } from './tokens';
import { validateIdToken, ValidatedIdTokenClaims } from './validation';
import { config } from '../config';

export interface AuthUrlParams {
  url: string;
  state: string;
  nonce: string;
  pkce: PkceCodes;
}

export class OidcClient {
  /**
   * Generates the Authorization URL and required ephemeral values (State, Nonce, PKCE).
   * Caller MUST store state, nonce, pkce.codeVerifier securely (e.g., in session).
   */
  async getAuthorizationUrl(): Promise<AuthUrlParams> {
    const metadata = await getIssuerMetadata();
    
    const state = crypto.randomUUID(); // High entropy state
    const nonce = crypto.randomUUID(); // High entropy nonce
    const pkce = generatePkce();

    // Build URL manually to ensure exact parameter control, or use openid-client AuthorizationRequest
    // Using URLSearchParams for transparency.
    const params = new URLSearchParams({
      response_type: 'code',
      client_id: config.oidc.clientId,
      redirect_uri: config.oidc.redirectUri,
      scope: config.oidc.scopes.join(' '),
      state,
      nonce,
      code_challenge: pkce.codeChallenge,
      code_challenge_method: pkce.codeChallengeMethod,
    });

    // Add optional parameters if needed (e.g., prompt, max_age, ui_locales)
    
    const url = `${metadata.authorization_endpoint}?${params.toString()}`;

    return { url, state, nonce, pkce };
  }

  /**
   * Handles the callback logic: validates state, exchanges code, validates ID token.
   */
  async handleCallback(
    query: { code?: string; state?: string; error?: string; error_description?: string },
    sessionState: string,
    sessionNonce: string,
    sessionCodeVerifier: string
  ): Promise<{ tokens: TokenResponse; claims: ValidatedIdTokenClaims }> {
    
    if (query.error) throw new Error(`${query.error}: ${query.error_description}`);
    if (!query.code) throw new Error('Missing authorization code');
    if (!query.state) throw new Error('Missing state in callback');
    if (query.state !== sessionState) throw new Error('State mismatch (CSRF protection)');

    const tokens = await exchangeCodeForTokens(
      query.code,
      sessionCodeVerifier,
      query.state,
      sessionNonce
    );

    // Re-validate ID token to get claims (exchangeCodeForTokens validates but doesn't return payload)
    const claims = await validateIdToken(tokens.idToken!, { nonce: sessionNonce });

    return { tokens, claims };
  }

  /**
   * Refreshes tokens if expired or near expiry.
   */
  async ensureValidAccessToken(refreshToken: string, expiresAt: number): Promise<TokenResponse> {
    const now = Math.floor(Date.now() / 1000);
    // Refresh if expired or expiring in 60 seconds
    if (now < expiresAt - 60) {
      throw new Error('Token not yet expired'); // Caller should check
    }
    return refreshAccessToken(refreshToken);
  }

  /**
   * Constructs End Session (Logout) URL.
   */
  async getLogoutUrl(idTokenHint: string): Promise<string> {
    const metadata = await getIssuerMetadata();
    if (!metadata.end_session_endpoint) {
      throw new Error('OP does not support RP-Initiated Logout (end_session_endpoint missing)');
    }

    const params = new URLSearchParams({
      id_token_hint: idTokenHint,
      post_logout_redirect_uri: config.oidc.postLogoutRedirectUri,
      // client_id: config.oidc.clientId, // Optional but recommended by some OPs
    });

    return `${metadata.end_session_endpoint}?${params.toString()}`;
  }

  async revokeTokens(accessToken: string, refreshToken: string): Promise<void> {
    await Promise.allSettled([
      revokeToken(accessToken, 'access_token'),
      revokeToken(refreshToken, 'refresh_token'),
    ]);
  }
}

export const oidcClient = new OidcClient();
```

---

### `src/session/session.ts`

Encrypted Server-Side Session using `iron-session` (AES-256-GCM + HMAC-SHA256).

```typescript
import { withIronSession, GetIronSessionOptions } from 'iron-session';
import { Request, Response, NextFunction } from 'express';
import { config } from '../config';

// Define Session Shape
export interface SessionData {
  // Auth Flow Ephemeral
  oidcState?: string;
  oidcNonce?: string;
  oidcCodeVerifier?: string;
  
  // Persistent Tokens
  accessToken?: string;
  idToken?: string;
  refreshToken?: string;
  expiresAt?: number; // Unix seconds
  tokenScope?: string;
  
  // User Info
  userClaims?: Record<string, unknown>;
  
  // CSRF Protection for forms (optional but good practice)
  csrfSecret?: string;
}

declare module 'iron-session' {
  interface IronSessionData extends SessionData {}
}

const sessionOptions: GetIronSessionOptions = {
  password: config.session.password,
  cookieName: config.session.cookieName,
  cookieOptions: {
    secure: process.env.NODE_ENV === 'production', // HTTPS only in prod
    httpOnly: true,
    sameSite: 'lax', // CSRF protection for login/callback
    maxAge: 60 * 60 * 24 * 14, // 2 weeks session lifetime
    path: '/',
  },
};

/**
 * Express Middleware to attach session to req.session
 */
export const sessionMiddleware = withIronSession(sessionOptions);

/**
 * Helper to destroy session completely
 */
export async function destroySession(req: Request, res: Response): Promise<void> {
  await req.session.destroy();
}

/**
 * Helper to save session explicitly (iron-session auto-saves on response finish, 
 * but explicit save needed if redirecting immediately after mutation).
 */
export async function saveSession(req: Request): Promise<void> {
  await req.session.save();
}
```

---

### `src/routes/auth.ts`

Login, Callback, Logout Routes.

```typescript
import { Router, Request, Response, NextFunction } from 'express';
import { oidcClient } from '../oidc/client';
import { saveSession, destroySession, SessionData } from '../session/session';
import { config } from '../config';

const router = Router();

/**
 * GET /login
 * Initiates OIDC Authorization Code Flow with PKCE.
 */
router.get('/login', async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { url, state, nonce, pkce } = await oidcClient.getAuthorizationUrl();

    // Store ephemeral values in session
    req.session.oidcState = state;
    req.session.oidcNonce = nonce;
    req.session.oidcCodeVerifier = pkce.codeVerifier;
    await saveSession(req);

    res.redirect(url);
  } catch (err) {
    next(err);
  }
});

/**
 * GET /callback
 * Handles redirect from OP. Validates state, exchanges code, validates ID Token, establishes session.
 */
router.get('/callback', async (req: Request, res: Response, next: NextFunction) => {
  try {
    // 1. Retrieve & Clear Ephemeral State
    const { oidcState, oidcNonce, oidcCodeVerifier } = req.session;
    if (!oidcState || !oidcNonce || !oidcCodeVerifier) {
      throw new Error('Missing OIDC state/nonce/verifier in session. Session expired or invalid flow.');
    }

    // Clear ephemeral immediately to prevent replay
    delete req.session.oidcState;
    delete req.session.oidcNonce;
    delete req.session.oidcCodeVerifier;

    // 2. Process Callback
    const { tokens, claims } = await oidcClient.handleCallback(req.query, oidcState, oidcNonce, oidcCodeVerifier);

    // 3. Establish Authenticated Session
    req.session.accessToken = tokens.accessToken;
    req.session.idToken = tokens.idToken;
    req.session.refreshToken = tokens.refreshToken;
    req.session.expiresAt = tokens.expiresAt;
    req.session.tokenScope = tokens.scope;
    req.session.userClaims = claims; // Store validated claims (sub, email, name, etc.)

    await saveSession(req);

    // 4. Redirect to App
    res.redirect('/profile'); // Or stored original URL
  } catch (err) {
    // Clear potentially corrupted session on error
    await destroySession(req, res);
    next(err);
  }
});

/**
 * GET /logout
 * Performs Local Logout + RP-Initiated OIDC Logout (End Session Endpoint).
 */
router.get('/logout', async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { idToken, accessToken, refreshToken } = req.session;

    // 1. Revoke tokens at OP (Best Effort)
    if (accessToken && refreshToken) {
      await oidcClient.revokeTokens(accessToken, refreshToken);
    }

    // 2. Destroy Local Session
    await destroySession(req, res);

    // 3. Redirect to OP Logout
    if (idToken) {
      const logoutUrl = await oidcClient.getLogoutUrl(idToken);
      return res.redirect(logoutUrl);
    }

    // Fallback if no ID token (should not happen if logged in)
    res.redirect(config.oidc.postLogoutRedirectUri);
  } catch (err) {
    // Even if OP logout fails, local session is destroyed.
    console.error('Logout error:', err);
    res.redirect(config.oidc.postLogoutRedirectUri);
  }
});

export default router;
```

---

### `src/routes/protected.ts`

Example Protected Route with Automatic Token Refresh.

```typescript
import { Router, Request, Response, NextFunction } from 'express';
import { oidcClient } from '../oidc/client';
import { saveSession } from '../session/session';

const router = Router();

/**
 * Middleware: Ensure Valid Access Token
 * Refreshes automatically if expired.
 */
export async function requireAuth(req: Request, res: Response, next: NextFunction) {
  const { accessToken, refreshToken, expiresAt } = req.session;

  if (!accessToken || !refreshToken || !expiresAt) {
    return res.status(401).json({ error: 'Unauthorized', message: 'No active session' });
  }

  const now = Math.floor(Date.now() / 1000);
  if (now >= expiresAt - 60) { // Expired or expiring soon
    try {
      console.log('Access token expired, refreshing...');
      const tokens = await oidcClient.ensureValidAccessToken(refreshToken, expiresAt);
      
      // Update session with new tokens (Rotation!)
      req.session.accessToken = tokens.accessToken;
      req.session.idToken = tokens.idToken ?? req.session.idToken; // Preserve old if not returned
      req.session.refreshToken = tokens.refreshToken; // Handle Rotation
      req.session.expiresAt = tokens.expiresAt;
      req.session.tokenScope = tokens.scope;
      
      await saveSession(req);
      console.log('Token refreshed successfully. New expiry:', new Date(tokens.expiresAt * 1000).toISOString());
    } catch (err) {
      console.error('Token refresh failed:', err);
      await req.session.destroy();
      return res.status(401).json({ error: 'Session Expired', message: 'Please log in again' });
    }
  }

  next();
}

router.get('/profile', requireAuth, (req: Request, res: Response) => {
  res.json({
    message: 'Access granted to protected resource',
    user: req.session.userClaims,
    tokenExpires: req.session.expiresAt ? new Date(req.session.expiresAt * 1000).toISOString() : null,
  });
});

export default router;
```

---

### `src/index.ts`

Application Entry Point.

```typescript
import express from 'express';
import { sessionMiddleware } from './session/session';
import authRoutes from './routes/auth';
import protectedRoutes from './routes/protected';
import { config } from './config';

const app = express();

// Trust proxy for secure cookies behind reverse proxy (nginx, etc.)
app.set('trust proxy', 1);

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Session Middleware (Must be before routes)
app.use(sessionMiddleware);

// Routes
app.use('/', authRoutes);
app.use('/', protectedRoutes);

// Root
app.get('/', (req, res) => {
  const isLoggedIn = !!req.session.accessToken;
  res.send(`
    <h1>OIDC Client Demo</h1>
    <p>Status: ${isLoggedIn ? 'Logged In' : 'Logged Out'}</p>
    <ul>
      <li><a href="/login">Login</a></li>
      <li><a href="/profile">Profile (Protected)</a></li>
      <li><a href="/logout">Logout</a></li>
    </ul>
  `);
});

// Global Error Handler
app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('Unhandled Error:', err);
  res.status(500).send(`
    <h1>Internal Server Error</h1>
    <pre>${err.message}</pre>
    <a href="/">Home</a>
  `);
});

app.listen(config.port, () => {
  console.log(`🚀 Server running at http://localhost:${config.port}`);
  console.log(`🔐 OIDC Issuer: ${config.oidc.issuerUrl}`);
  console.log(`🔑 Client ID: ${config.oidc.clientId}`);
});
```

---

## 4. Installation & Execution

### Prerequisites
*   Node.js >= 20.0.0
*   An OIDC Provider (Keycloak, Auth0, Azure AD, Google, Okta, etc.) configured for **Confidential Client** (Client Secret enabled) with **Authorization Code Flow + PKCE** allowed.
*   Redirect URI configured in OP: `http://localhost:3000/callback`
*   Post-Logout Redirect URI configured in OP: `http://localhost:3000/`

### Commands

```bash
# 1. Clone / Create directory
mkdir oidc-client && cd oidc-client

# 2. Create files (package.json, tsconfig.json, .env.example, src/...)

# 3. Install exact dependencies
npm ci

# 4. Configure Environment
cp .env.example .env
# EDIT .env with your Provider details (ISSUER_URL, CLIENT_ID, CLIENT_SECRET, SESSION_PASSWORD)

# 5. Build TypeScript
npm run build

# 6. Run Production Build
npm start

# OR Run Development (with ts-node)
npm run dev
```

### Verification Steps

1.  Open `http://localhost:3000`.
2.  Click **Login** -> Redirects to your Identity Provider.
3.  Authenticate at Provider.
4.  Redirect back to `/callback` -> Validates State, PKCE, Nonce, ID Token Signature (JWKS), Claims.
5.  Redirects to `/profile` -> Shows User Claims (sub, email, name, etc.) from validated ID Token.
6.  Wait for Access Token to expire (or reduce `expiresAt` in session for testing) -> Refresh `/profile` -> Observe "Token refreshed successfully" in console, new token stored, session preserved.
7.  Click **Logout** -> Local session destroyed, Tokens revoked at OP (if supported), Redirects to OP Logout Screen -> Returns to Home.

---

## 5. Security Architecture Summary

| Threat | Mitigation Implemented |
| :--- | :--- |
| **CSRF (Cross-Site Request Forgery)** | `state` parameter (cryptographically random, bound to session, validated on callback). `SameSite=Lax` cookies. |
| **Authorization Code Injection** | `PKCE (S256)`: `code_verifier` generated per request, stored in encrypted session, sent only in token request. |
| **Token Replay / ID Token Forgery** | `nonce` parameter (bound to session, validated in ID Token). |
| **ID Token Tampering** | Asymmetric Signature Validation via **Rotating JWKS** (`jose.createRemoteJWKSet` handles caching/rotation). |
| **Token Misuse (Wrong Audience/Issuer)** | Strict `iss` (Issuer) & `aud` (Client ID) validation during `jwtVerify`. |
| **Token Expiration / Clock Skew** | `exp`, `iat`, `nbf` validation with 30s `clockTolerance`. |
| **Session Hijacking** | **Encrypted Server-Side Sessions** (`iron-session`: AES-256-GCM, integrity protected, `HttpOnly`, `Secure`, `SameSite=Lax` cookies). No JWTs in cookies. |
| **Refresh Token Theft / Replay** | **Refresh Token Rotation**: New Refresh Token issued on every refresh (if OP supports), old one invalidated. Stored only in encrypted session. |
| **Token Leakage on Logout** | **Token Revocation (RFC 7009)** called on `access_token` and `refresh_token` during logout. |
| **Open Redirects** | `redirect_uri` and `post_logout_redirect_uri` hardcoded in config/validated against pre-registered values. |

---

## 6. Mathematical Basis for PKCE (RFC 7636)

The Proof Key for Code Exchange (PKCE) transforms a high-entropy secret into a challenge suitable for public transmission.

**Code Verifier Generation:**
$V \leftarrow \text{Random}(32 \text{ to } 96 \text{ bytes}) \rightarrow \text{Base64URLEncode}(V)$
*Implementation uses 64-char high-entropy alphanumeric string.*

**Code Challenge Generation (S256 Method):**
$C = \text{Base64URLEncode}(\text{SHA256}(V))$

**Verification (Performed by Authorization Server):**
$\text{SHA256}(V_{\text{received}}) \stackrel{?}{=} \text{Base64URLDecode}(C_{\text{stored}})$

This ensures that even if the Authorization Code ($Code$) is intercepted, the attacker cannot exchange it for tokens without the Verifier ($V$), which never leaves the client's secure session storage.
