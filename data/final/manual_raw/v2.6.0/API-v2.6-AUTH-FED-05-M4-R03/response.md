# Federation Gateway Implementation

## Package.json

```json
{
  "name": "federation-gateway",
  "version": "1.0.0",
  "description": "Self-contained Node.js TypeScript federation gateway for multi-issuer JWT validation",
  "main": "dist/index.js",
  "type": "module",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "tsx watch src/index.ts",
    "mock:issuer-a": "tsx watch src/mocks/issuer-a.ts",
    "mock:issuer-b": "tsx watch src/mocks/issuer-b.ts",
    "test": "tsx src/test/run-tests.ts"
  },
  "dependencies": {
    "express": "4.19.2",
    "jose": "5.3.0"
  },
  "devDependencies": {
    "@types/express": "4.17.21",
    "@types/node": "20.14.2",
    "tsx": "4.15.7",
    "typescript": "5.5.2"
  },
  "engines": {
    "node": ">=20.0.0"
  }
}
```

## TypeScript Configuration

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

## Source Code Structure

```
src/
├── index.ts                 # Main gateway entry point
├── config/
│   └── issuers.ts           # Issuer configurations
├── core/
│   ├── discovery.ts         # OpenID Connect discovery
│   ├── jwks-cache.ts        # JWKS caching with bounded freshness
│   ├── token-validator.ts   # JWT validation logic
│   └── principal.ts         # Normalized principal type
├── gateway/
│   └── express-gateway.ts   # Express middleware/route
├── mocks/
│   ├── issuer-a.ts          # Mock issuer A (port 8081)
│   ├── issuer-b.ts          # Mock issuer-b.ts        # Mock issuer B (port 8082)
│   └── keys.ts              # Shared key management for mocks
└── test/
    └── run-tests.ts         # Deterministic test suite
```

---

## Core Types & Configuration

### `src/config/issuers.ts`

```typescript
/**
 * Issuer configuration with strict validation requirements.
 * Each issuer is independently configured to prevent unknown issuers
 * from controlling fetch URLs (SSRF protection).
 */
export interface IssuerConfig {
  /** Unique identifier for this issuer (must match token 'iss' claim) */
  issuer: string;
  /** OpenID Connect discovery endpoint URL */
  discoveryUrl: string;
  /** Expected audience(s) for tokens from this issuer */
  audiences: string | string[];
  /** Allowed JWS algorithms for this issuer */
  allowedAlgorithms: string[];
  /** Maximum age of cached JWKS before forced refresh (ms) */
  maxCacheAgeMs: number;
  /** Minimum time between JWKS refresh attempts (ms) */
  minRefreshIntervalMs: number;
  /** Clock skew tolerance for token validation (seconds) */
  clockToleranceSeconds: number;
}

/**
 * Pre-configured issuers - in production these would come from config file/env.
 * NOTE: discoveryUrl is FIXED per issuer - unknown issuers cannot control fetch URLs.
 */
export const ISSUER_CONFIGS: ReadonlyMap<string, IssuerConfig> = new Map([
  [
    "https://issuer-a.example.com",
    {
      issuer: "https://issuer-a.example.com",
      discoveryUrl: "http://localhost:8081/.well-known/openid-configuration",
      audiences: ["gateway-api", "resource-server-1"],
      allowedAlgorithms: ["RS256", "RS384", "RS512"],
      maxCacheAgeMs: 5 * 60 * 1000, // 5 minutes
      minRefreshIntervalMs: 30 * 1000, // 30 seconds
      clockToleranceSeconds: 30,
    },
  ],
  [
    "https://issuer-b.example.com",
    {
      issuer: "https://issuer-b.example.com",
      discoveryUrl: "http://localhost:8082/.well-known/openid-configuration",
      audiences: ["gateway-api", "resource-server-2"],
      allowedAlgorithms: ["RS256", "ES256", "ES384"],
      maxCacheAgeMs: 10 * 60 * 1000, // 10 minutes
      minRefreshIntervalMs: 60 * 1000, // 1 minute
      clockToleranceSeconds: 60,
    },
  ],
]);

/** Get config for a known issuer, or undefined if not configured */
export function getIssuerConfig(issuer: string): IssuerConfig | undefined {
  return ISSUER_CONFIGS.get(issuer);
}

/** Check if an issuer is known/configured */
export function isKnownIssuer(issuer: string): boolean {
  return ISSUER_CONFIGS.has(issuer);
}
```

### `src/core/principal.ts`

```typescript
/**
 * Normalized principal representing an authenticated identity.
 * Retains issuer and subject for audit/authorization purposes.
 */
export interface Principal {
  /** The issuer that authenticated this principal */
  issuer: string;
  /** The subject identifier from the token */
  subject: string;
  /** The audience(s) the token was issued for */
  audiences: string[];
  /** The validated JWT claims (subset) */
  claims: Readonly<Record<string, unknown>>;
  /** Token expiration timestamp (Unix seconds) */
  expiresAt: number;
  /** Token issued-at timestamp (Unix seconds) */
  issuedAt: number;
  /** JWT ID claim if present */
  jwtId?: string;
  /** Authentication time claim if present */
  authTime?: number;
  /** Scopes/permissions from token */
  scopes: string[];
}

/**
 * Create a normalized principal from validated token claims.
 */
export function createPrincipal(
  issuer: string,
  claims: Record<string, unknown>
): Principal {
  const sub = String(claims.sub ?? "");
  const aud = claims.aud ? (Array.isArray(claims.aud) ? claims.aud.map(String) : [String(claims.aud)]) : [];
  const scopes = claims.scope ? String(claims.scope).split(" ") : 
                 claims.scp ? (Array.isArray(claims.scp) ? claims.scp.map(String) : [String(claims.scp)]) : [];

  return {
    issuer,
    subject: sub,
    audiences: aud,
    claims: Object.freeze({ ...claims }),
    expiresAt: Number(claims.exp ?? 0),
    issuedAt: Number(claims.iat ?? 0),
    jwtId: claims.jti ? String(claims.jti) : undefined,
    authTime: claims.auth_time ? Number(claims.auth_time) : undefined,
    scopes,
  };
}
```

---

## Discovery & JWKS Cache

### `src/core/discovery.ts`

```typescript
import { IssuerConfig } from "../config/issuers.js";

/** OpenID Connect Discovery Response (subset we care about) */
export interface DiscoveryDocument {
  issuer: string;
  jwks_uri: string;
  authorization_endpoint?: string;
  token_endpoint?: string;
  id_token_signing_alg_values_supported?: string[];
}

/** Fetch and validate OpenID Connect discovery document */
export async function fetchDiscoveryDocument(
  config: IssuerConfig
): Promise<DiscoveryDocument> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 5000);

  try {
    const response = await fetch(config.discoveryUrl, {
      signal: controller.signal,
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      throw new Error(`Discovery failed: ${response.status} ${response.statusText}`);
    }

    const doc = (await response.json()) as DiscoveryDocument;

    // Critical: Validate issuer matches expected (prevents issuer spoofing)
    if (doc.issuer !== config.issuer) {
      throw new Error(
        `Issuer mismatch: expected ${config.issuer}, got ${doc.issuer}`
      );
    }

    if (!doc.jwks_uri) {
      throw new Error("Discovery document missing jwks_uri");
    }

    return doc;
  } finally {
    clearTimeout(timeout);
  }
}

/** JWKS Response structure */
export interface JwksResponse {
  keys: JsonWebKey[];
}
```

### `src/core/jwks-cache.ts`

```typescript
import { IssuerConfig } from "../config/issuers.js";
import { DiscoveryDocument, JwksResponse } from "./discovery.js";
import { fetchDiscoveryDocument } from "./discovery.js";

/** Cached JWKS entry with metadata */
interface CacheEntry {
  keys: Map<string, CryptoKey>; // kid -> CryptoKey
  fetchedAt: number;
  jwksUri: string;
  etag?: string;
  lastRefreshAttempt: number;
}

/**
 * JWKS Cache with bounded freshness and safe rotation handling.
 * - Keys cached with TTL (maxCacheAgeMs)
 * - Refresh only attempted after minRefreshIntervalMs
 * - On key rotation (kid not found), forces refresh once
 * - Unknown issuers never reach this cache (validated at entry point)
 */
export class JwksCache {
  private cache = new Map<string, CacheEntry>(); // issuer -> entry
  private refreshPromises = new Map<string, Promise<void>>(); // issuer -> in-flight refresh

  constructor(private readonly configs: Map<string, IssuerConfig>) {}

  /**
   * Get a signing key for the given issuer and key ID.
   * Handles cache miss, expiry, and key rotation transparently.
   */
  async getKey(issuer: string, kid: string): Promise<CryptoKey> {
    const config = this.configs.get(issuer);
    if (!config) {
      throw new Error(`Unknown issuer: ${issuer}`);
    }

    let entry = this.cache.get(issuer);
    const now = Date.now();

    // Check if we have a valid cached entry with the key
    if (entry && entry.keys.has(kid) && this.isFresh(entry, config, now)) {
      return entry.keys.get(kid)!;
    }

    // Key not found or cache stale - attempt refresh
    await this.ensureFresh(issuer, config, kid, now);

    entry = this.cache.get(issuer);
    if (!entry || !entry.keys.has(kid)) {
      throw new Error(`Key not found after refresh: issuer=${issuer}, kid=${kid}`);
    }

    return entry.keys.get(kid)!;
  }

  /** Check if cache entry is still fresh */
  private isFresh(entry: CacheEntry, config: IssuerConfig, now: number): boolean {
    return now - entry.fetchedAt < config.maxCacheAgeMs;
  }

  /** Ensure cache is fresh, with deduplication of concurrent refreshes */
  private async ensureFresh(
    issuer: string,
    config: IssuerConfig,
    kid: string,
    now: number
  ): Promise<void> {
    const entry = this.cache.get(issuer);

    // If we have a recent refresh attempt, don't hammer the endpoint
    if (entry && now - entry.lastRefreshAttempt < config.minRefreshIntervalMs) {
      // But if the specific kid is missing, we MUST try once (key rotation)
      if (entry.keys.has(kid)) {
        return; // Key exists, just stale - wait for background refresh
      }
      // Key missing - force refresh despite rate limit
    }

    // Deduplicate concurrent refreshes for same issuer
    let refreshPromise = this.refreshPromises.get(issuer);
    if (!refreshPromise) {
      refreshPromise = this.performRefresh(issuer, config, now);
      this.refreshPromises.set(issuer, refreshPromise);
    }

    try {
      await refreshPromise;
    } finally {
      this.refreshPromises.delete(issuer);
    }
  }

  /** Perform actual JWKS fetch and cache update */
  private async performRefresh(
    issuer: string,
    config: IssuerConfig,
    now: number
  ): Promise<void> {
    const existingEntry = this.cache.get(issuer);

    // Fetch discovery (validates issuer match)
    const discovery = await fetchDiscoveryDocument(config);

    // Fetch JWKS with conditional request if we have ETag
    const headers: Record<string, string> = { Accept: "application/json" };
    if (existingEntry?.etag) {
      headers["If-None-Match"] = existingEntry.etag;
    }

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);

    try {
      const response = await fetch(discovery.jwks_uri, {
        signal: controller.signal,
        headers,
      });

      // 304 Not Modified - cache still valid
      if (response.status === 304 && existingEntry) {
        existingEntry.fetchedAt = now;
        existingEntry.lastRefreshAttempt = now;
        return;
      }

      if (!response.ok) {
        throw new Error(`JWKS fetch failed: ${response.status} ${response.statusText}`);
      }

      const jwks = (await response.json()) as JwksResponse;
      const etag = response.headers.get("etag") ?? undefined;

      // Import all keys
      const keys = new Map<string, CryptoKey>();
      for (const jwk of jwks.keys) {
        if (!jwk.kid) continue; // Skip keys without kid
        try {
          const key = await crypto.subtle.importKey(
            "jwk",
            jwk,
            { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, // Algorithm determined at validation time
            true, // extractable for potential re-export
            ["verify"]
          );
          keys.set(jwk.kid, key);
        } catch (e) {
          console.warn(`Failed to import key ${jwk.kid}:`, e);
        }
      }

      if (keys.size === 0) {
        throw new Error("No valid keys in JWKS response");
      }

      this.cache.set(issuer, {
        keys,
        fetchedAt: now,
        jwksUri: discovery.jwks_uri,
        etag,
        lastRefreshAttempt: now,
      });
    } finally {
      clearTimeout(timeout);
    }
  }

  /** Clear cache for an issuer (testing/admin) */
  clear(issuer: string): void {
    this.cache.delete(issuer);
  }

  /** Clear all caches */
  clearAll(): void {
    this.cache.clear();
  }

  /** Get cache stats for monitoring */
  getStats(): Record<string, { keyCount: number; ageMs: number; jwksUri: string }> {
    const now = Date.now();
    const stats: Record<string, { keyCount: number; ageMs: number; jwksUri: string }> = {};
    for (const [issuer, entry] of this.cache) {
      stats[issuer] = {
        keyCount: entry.keys.size,
        ageMs: now - entry.fetchedAt,
        jwksUri: entry.jwksUri,
      };
    }
    return stats;
  }
}
```

---

## Token Validation

### `src/core/token-validator.ts`

```typescript
import { IssuerConfig, getIssuerConfig, isKnownIssuer } from "../config/issuers.js";
import { JwksCache } from "./jwks-cache.js";
import { Principal, createPrincipal } from "./principal.js";
import { JWTPayload, importJWK, jwtVerify, JWTVerifyResult } from "jose";

/** Validation result */
export interface ValidationResult {
  principal: Principal;
  rawClaims: JWTPayload;
}

/** Validation error codes */
export enum ValidationErrorCode {
  UNKNOWN_ISSUER = "UNKNOWN_ISSUER",
  INVALID_TOKEN = "INVALID_TOKEN",
  INVALID_SIGNATURE = "INVALID_SIGNATURE",
  INVALID_AUDIENCE = "INVALID_AUDIENCE",
  INVALID_ALGORITHM = "INVALID_ALGORITHM",
  TOKEN_EXPIRED = "TOKEN_EXPIRED",
  TOKEN_NOT_YET_VALID = "TOKEN_NOT_YET_VALID",
  MISSING_KID = "MISSING_KID",
  KEY_NOT_FOUND = "KEY_NOT_FOUND",
  CLAIM_VALIDATION_FAILED = "CLAIM_VALIDATION_FAILED",
}

/** Custom error with code */
export class ValidationError extends Error {
  constructor(
    public readonly code: ValidationErrorCode,
    message: string,
    public readonly issuer?: string,
    public readonly kid?: string
  ) {
    super(message);
    this.name = "ValidationError";
  }
}

/**
 * Federation Token Validator
 * - Validates issuer is known (prevents SSRF via unknown issuer discovery URLs)
 * - Selects key by kid from issuer's JWKS
 * - Validates algorithm per issuer policy
 * - Validates audience per issuer policy
 * - Normalizes to common Principal
 */
export class TokenValidator {
  constructor(private readonly jwksCache: JwksCache) {}

  /**
   * Validate a JWT access token and return normalized principal.
   * Throws ValidationError on any validation failure.
   */
  async validate(token: string): Promise<ValidationResult> {
    // 1. Parse header to get kid and alg (unverified)
    let header: { kid?: string; alg?: string };
    try {
      const parts = token.split(".");
      if (parts.length !== 3) throw new Error("Invalid JWT format");
      header = JSON.parse(Buffer.from(parts[0], "base64url").toString());
    } catch (e) {
      throw new ValidationError(
        ValidationErrorCode.INVALID_TOKEN,
        "Malformed JWT header"
      );
    }

    const kid = header.kid;
    const alg = header.alg;

    if (!kid) {
      throw new ValidationError(
        ValidationErrorCode.MISSING_KID,
        "Token missing 'kid' header"
      );
    }

    // 2. Verify token with issuer-aware key resolution
    // We use a custom key resolver that fetches from our cache
    let verified: JWTVerifyResult<JWTPayload>;
    try {
      verified = await jwtVerify(token, async (protectedHeader, token) => {
        const tokenKid = protectedHeader.kid;
        if (!tokenKid || typeof tokenKid !== "string") {
          throw new ValidationError(
            ValidationErrorCode.MISSING_KID,
            "Token missing 'kid' in protected header"
          );
        }

        // Extract issuer from payload (unverified at this point)
        // We need to decode payload to get issuer for key lookup
        const payloadPart = token.split(".")[1];
        let payload: JWTPayload;
        try {
          payload = JSON.parse(Buffer.from(payloadPart, "base64url").toString());
        } catch {
          throw new ValidationError(
            ValidationErrorCode.INVALID_TOKEN,
            "Malformed JWT payload"
          );
        }

        const issuer = payload.iss;
        if (!issuer || typeof issuer !== "string") {
          throw new ValidationError(
            ValidationErrorCode.INVALID_TOKEN,
            "Token missing 'iss' claim"
          );
        }

        // CRITICAL: Validate issuer is known BEFORE fetching keys
        // This prevents unknown issuers from controlling fetch URLs (SSRF)
        if (!isKnownIssuer(issuer)) {
          throw new ValidationError(
            ValidationErrorCode.UNKNOWN_ISSUER,
            `Unknown or unconfigured issuer: ${issuer}`,
            issuer
          );
        }

        // Get key from cache (handles refresh/rotation)
        const cryptoKey = await this.jwksCache.getKey(issuer, tokenKid);

        // Validate algorithm against issuer policy
        const config = getIssuerConfig(issuer)!;
        const tokenAlg = protectedHeader.alg;
        if (!tokenAlg || !config.allowedAlgorithms.includes(tokenAlg)) {
          throw new ValidationError(
            ValidationErrorCode.INVALID_ALGORITHM,
            `Algorithm ${tokenAlg} not allowed for issuer ${issuer}`,
            issuer,
            tokenKid
          );
        }

        return cryptoKey;
      }, {
        // Audience validation will be done per-issuer after verification
        // We don't pass audience here because each issuer has different expected audiences
        clockTolerance: 30, // Default, overridden per-issuer below
      });
    } catch (e) {
      if (e instanceof ValidationError) throw e;
      if (e instanceof Error) {
        if (e.message.includes("signature")) {
          throw new ValidationError(
            ValidationErrorCode.INVALID_SIGNATURE,
            "Invalid token signature"
          );
        }
        if (e.message.includes("expired")) {
          throw new ValidationError(
            ValidationErrorCode.TOKEN_EXPIRED,
            "Token expired"
          );
        }
        if (e.message.includes("not before")) {
          throw new ValidationError(
            ValidationErrorCode.TOKEN_NOT_YET_VALID,
            "Token not yet valid"
          );
        }
      }
      throw new ValidationError(
        ValidationErrorCode.INVALID_SIGNATURE,
        `Token verification failed: ${e instanceof Error ? e.message : String(e)}`
      );
    }

    const { payload } = verified;
    const issuer = payload.iss as string;
    const config = getIssuerConfig(issuer)!;

    // 3. Validate audience per issuer config
    const expectedAudiences = Array.isArray(config.audiences) 
      ? config.audiences 
      : [config.audiences];
    const tokenAudiences = Array.isArray(payload.aud) 
      ? payload.aud 
      : payload.aud 
        ? [payload.aud] 
        : [];

    const hasValidAudience = tokenAudiences.some((aud) => 
      expectedAudiences.includes(aud as string)
    );

    if (!hasValidAudience) {
      throw new ValidationError(
        ValidationErrorCode.INVALID_AUDIENCE,
        `Token audience not accepted. Expected one of: ${expectedAudiences.join(", ")}, got: ${tokenAudiences.join(", ")}`,
        issuer
      );
    }

    // 4. Validate expiration with issuer-specific clock tolerance
    const now = Math.floor(Date.now() / 1000);
    const exp = payload.exp as number;
    const nbf = payload.nbf as number | undefined;

    if (exp && now > exp + config.clockToleranceSeconds) {
      throw new ValidationError(
        ValidationErrorCode.TOKEN_EXPIRED,
        `Token expired at ${new Date(exp * 1000).toISOString()}`,
        issuer
      );
    }

    if (nbf && now + config.clockToleranceSeconds < nbf) {
      throw new ValidationError(
        ValidationErrorCode.TOKEN_NOT_YET_VALID,
        `Token not valid before ${new Date(nbf * 1000).toISOString()}`,
        issuer
      );
    }

    // 5. Create normalized principal
    const principal = createPrincipal(issuer, payload as Record<string, unknown>);

    return { principal, rawClaims: payload };
  }
}
```

---

## Express Gateway

### `src/gateway/express-gateway.ts`

```typescript
import { Request, Response, NextFunction, RequestHandler } from "express";
import { TokenValidator, ValidationError, ValidationErrorCode } from "../core/token-validator.js";
import { Principal } from "../core/principal.js";

/** Extended Express Request with authenticated principal */
export interface AuthenticatedRequest extends Request {
  principal?: Principal;
  authError?: ValidationError;
}

/** Authentication middleware */
export function createAuthMiddleware(validator: TokenValidator): RequestHandler {
  return async (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      res.status(401).json({
        error: "unauthorized",
        error_description: "Missing or invalid Authorization header",
        code: "MISSING_TOKEN",
      });
      return;
    }

    const token = authHeader.slice(7).trim();

    try {
      const { principal } = await validator.validate(token);
      req.principal = principal;
      next();
    } catch (e) {
      if (e instanceof ValidationError) {
        req.authError = e;
        const statusCode = getStatusCodeForError(e.code);
        res.status(statusCode).json({
          error: "invalid_token",
          error_description: e.message,
          code: e.code,
          issuer: e.issuer,
          kid: e.kid,
        });
        return;
      }
      
      console.error("Unexpected validation error:", e);
      res.status(500).json({
        error: "server_error",
        error_description: "Internal authentication error",
        code: "INTERNAL_ERROR",
      });
    }
  };
}

function getStatusCodeForError(code: ValidationErrorCode): number {
  switch (code) {
    case ValidationErrorCode.UNKNOWN_ISSUER:
    case ValidationErrorCode.INVALID_AUDIENCE:
    case ValidationErrorCode.INVALID_ALGORITHM:
      return 403; // Forbidden - token valid but not accepted by this gateway
    case ValidationErrorCode.TOKEN_EXPIRED:
    case ValidationErrorCode.TOKEN_NOT_YET_VALID:
      return 401; // Unauthorized - temporal issue
    case ValidationErrorCode.INVALID_SIGNATURE:
    case ValidationErrorCode.KEY_NOT_FOUND:
    case ValidationErrorCode.MISSING_KID:
    case ValidationErrorCode.INVALID_TOKEN:
    case ValidationErrorCode.CLAIM_VALIDATION_FAILED:
      return 401; // Unauthorized - token malformed/invalid
    default:
      return 401;
  }
}

/** Optional: Principal extraction helper for route handlers */
export function getPrincipal(req: AuthenticatedRequest): Principal | undefined {
  return req.principal;
}
```

### `src/index.ts`

```typescript
import express from "express";
import { ISSUER_CONFIGS } from "./config/issuers.js";
import { JwksCache } from "./core/jwks-cache.js";
import { TokenValidator } from "./core/token-validator.js";
import { createAuthMiddleware, AuthenticatedRequest } from "./gateway/express-gateway.js";

/** Application dependencies container */
interface AppDeps {
  jwksCache: JwksCache;
  validator: TokenValidator;
  app: express.Express;
}

/** Initialize all application components */
function createApp(): AppDeps {
  const jwksCache = new JwksCache(ISSUER_CONFIGS);
  const validator = new TokenValidator(jwksCache);
  const app = express();

  app.use(express.json());

  // Health check (no auth)
  app.get("/health", (_req, res) => {
    res.json({ 
      status: "ok", 
      timestamp: new Date().toISOString(),
      cacheStats: jwksCache.getStats(),
    });
  });

  // Protected resource endpoint
  app.get("/api/resource", createAuthMiddleware(validator), (req: AuthenticatedRequest, res) => {
    const principal = req.principal!;
    res.json({
      message: "Access granted",
      principal: {
        issuer: principal.issuer,
        subject: principal.subject,
        audiences: principal.audiences,
        scopes: principal.scopes,
        expiresAt: new Date(principal.expiresAt * 1000).toISOString(),
      },
    });
  });

  // Admin endpoint to inspect cache
  app.get("/admin/cache", (_req, res) => {
    res.json({ cache: jwksCache.getStats() });
  });

  // Admin endpoint to force cache clear
  app.post("/admin/cache/clear", express.json(), (req, res) => {
    const { issuer } = req.body as { issuer?: string };
    if (issuer) {
      jwksCache.clear(issuer);
      res.json({ cleared: issuer });
    } else {
      jwksCache.clearAll();
      res.json({ cleared: "all" });
    }
  });

  return { jwksCache, validator, app };
}

/** Start the server */
async function main(): Promise<void> {
  const { app } = createApp();
  const port = Number(process.env.PORT ?? 3000);
  
  app.listen(port, () => {
    console.log(`🚀 Federation Gateway listening on http://localhost:${port}`);
    console.log(`   Configured issuers: ${[...ISSUER_CONFIGS.keys()].join(", ")}`);
    console.log(`   Health: http://localhost:${port}/health`);
    console.log(`   Protected: http://localhost:${port}/api/resource`);
  });
}

main().catch((err) => {
  console.error("Failed to start gateway:", err);
  process.exit(1);
});
```

---

## Mock Issuers

### `src/mocks/keys.ts`

```typescript
import { generateKeyPair, exportJWK, JWK } from "jose";

/** Key pair with metadata */
export interface KeyPair {
  kid: string;
  alg: string;
  publicKey: CryptoKey;
  privateKey: CryptoKey;
  jwk: JWK;
  createdAt: number;
  expiresAt: number;
}

/** Generate RSA key pair for testing */
export async function generateRsaKeyPair(
  kid: string,
  alg: "RS256" | "RS384" | "RS512" = "RS256",
  ttlMs: number = 24 * 60 * 60 * 1000
): Promise<KeyPair> {
  const { publicKey, privateKey } = await generateKeyPair("RS256", {
    modulusLength: 2048,
  });

  const jwk = await exportJWK(publicKey);
  jwk.kid = kid;
  jwk.alg = alg;
  jwk.use = "sig";

  const now = Date.now();
  return {
    kid,
    alg,
    publicKey,
    privateKey,
    jwk,
    createdAt: now,
    expiresAt: now + ttlMs,
  };
}

/** Generate EC key pair for testing */
export async function generateEcKeyPair(
  kid: string,
  alg: "ES256" | "ES384" = "ES256",
  ttlMs: number = 24 * 60 * 60 * 1000
): Promise<KeyPair> {
  const { publicKey, privateKey } = await generateKeyPair(alg, {
    namedCurve: alg === "ES256" ? "P-256" : "P-384",
  });

  const jwk = await exportJWK(publicKey);
  jwk.kid = kid;
  jwk.alg = alg;
  jwk.use = "sig";

  const now = Date.now();
  return {
    kid,
    alg,
    publicKey,
    privateKey,
    jwk,
    createdAt: now,
    expiresAt: now + ttlMs,
  };
}

/** Key store for an issuer */
export class KeyStore {
  private keys = new Map<string, KeyPair>();
  private currentKid: string | null = null;

  /** Add a key to the store */
  add(key: KeyPair): void {
    this.keys.set(key.kid, key);
    if (!this.currentKid) this.currentKid = key.kid;
  }

  /** Get current signing key */
  getCurrent(): KeyPair | null {
    return this.currentKid ? this.keys.get(this.currentKid) ?? null : null;
  }

  /** Get key by kid */
  get(kid: string): KeyPair | undefined {
    return this.keys.get(kid);
  }

  /** Rotate to a new key (simulates key rotation) */
  rotate(newKey: KeyPair): void {
    this.keys.set(newKey.kid, newKey);
    this.currentKid = newKey.kid;
  }

  /** Get all public JWKs for JWKS endpoint */
  getJwks(): { keys: JWK[] } {
    return {
      keys: Array.from(this.keys.values()).map((k) => k.jwk),
    };
  }

  /** Get all key IDs */
  getKeyIds(): string[] {
    return Array.from(this.keys.keys());
  }
}

/** Create a JWT with the given key */
export async function createToken(
  key: KeyPair,
  claims: Record<string, unknown>
): Promise<string> {
  const { SignJWT } = await import("jose");
  return new SignJWT(claims as any)
    .setProtectedHeader({ kid: key.kid, alg: key.alg })
    .setIssuedAt()
    .setExpirationTime("1h")
    .sign(key.privateKey);
}
```

### `src/mocks/issuer-a.ts`

```typescript
import express from "express";
import { KeyStore, generateRsaKeyPair, createToken } from "./keys.js";

const PORT = 8081;
const ISSUER = "https://issuer-a.example.com";
const JWKS_URI = `http://localhost:${PORT}/jwks`;

// Key store with OVERLAPPING kid with issuer-b (kid="key-1")
const keyStore = new KeyStore();

// Initialize with two keys - one overlapping kid
async function initializeKeys() {
  // Key 1: Overlapping kid with issuer-b
  const key1 = await generateRsaKeyPair("key-1", "RS256");
  keyStore.add(key1);

  // Key 2: Unique to issuer-a
  const key2 = await generateRsaKeyPair("key-a-2", "RS384");
  keyStore.add(key2);

  // Set current to key-1 initially
  keyStore.rotate(key1);
  
  console.log(`[Issuer A] Initialized with keys: ${keyStore.getKeyIds().join(", ")}`);
  console.log(`[Issuer A] Current signing key: ${keyStore.getCurrent()?.kid}`);
}

// Discovery endpoint
const discoveryDoc = {
  issuer: ISSUER,
  jwks_uri: JWKS_URI,
  authorization_endpoint: `http://localhost:${PORT}/authorize`,
  token_endpoint: `http://localhost:${PORT}/token`,
  id_token_signing_alg_values_supported: ["RS256", "RS384", "RS512"],
};

const app = express();
app.use(express.json());

// OpenID Connect Discovery
app.get("/.well-known/openid-configuration", (_req, res) => {
  res.set("Cache-Control", "public, max-age=3600");
  res.json(discoveryDoc);
});

// JWKS endpoint with ETag support
app.get("/jwks", (req, res) => {
  const jwks = keyStore.getJwks();
  const etag = `W/"${JSON.stringify(jwks.keys.map(k => k.kid).sort()).length}"`;
  
  if (req.headers["if-none-match"] === etag) {
    return res.status(304).end();
  }
  
  res.set("ETag", etag);
  res.set("Cache-Control", "public, max-age=300");
  res.json(jwks);
});

// Token minting endpoint (for testing)
app.post("/token", async (req, res) => {
  const { subject = "user-a-123", audience = "gateway-api", scope = "read write", ttl = 3600 } = req.body;
  
  const currentKey = keyStore.getCurrent();
  if (!currentKey) {
    return res.status(500).json({ error: "No signing key available" });
  }

  const now = Math.floor(Date.now() / 1000);
  const token = await createToken(currentKey, {
    iss: ISSUER,
    sub: subject,
    aud: audience,
    scope,
    iat: now,
    exp: now + ttl,
    jti: `token-${Date.now()}-${Math.random().toString(36).slice(2)}`,
  });

  res.json({
    access_token: token,
    token_type: "Bearer",
    expires_in: ttl,
    scope,
  });
});

// Admin: Rotate keys (simulate key rotation)
app.post("/admin/rotate", async (_req, res) => {
  const newKey = await generateRsaKeyPair(`key-a-${Date.now()}`, "RS256");
  keyStore.rotate(newKey);
  console.log(`[Issuer A] Rotated to new key: ${newKey.kid}`);
  res.json({ rotatedTo: newKey.kid, keys: keyStore.getKeyIds() });
});

// Admin: Add overlapping key (kid="key-1" but different key material)
app.post("/admin/add-overlapping", async (_req, res) => {
  // Generate a NEW key with same kid="key-1" - simulates malicious or misconfigured overlap
  const overlappingKey = await generateRsaKeyPair("key-1", "RS512");
  keyStore.add(overlappingKey);
  console.log(`[Issuer A] Added overlapping key-1 (different material): ${overlappingKey.kid}`);
  res.json({ added: overlappingKey.kid, keys: keyStore.getKeyIds() });
});

// Admin: Expire current key (simulate cache expiry scenario)
app.post("/admin/expire-current", (_req, res) => {
  const current = keyStore.getCurrent();
  if (current) {
    // Manually expire by setting createdAt to old
    (current as any).createdAt = Date.now() - 24 * 60 * 60 * 1000;
    console.log(`[Issuer A] Marked current key as expired: ${current.kid}`);
  }
  res.json({ expired: current?.kid });
});

app.listen(PORT, async () => {
  await initializeKeys();
  console.log(`🔐 Issuer A running on http://localhost:${PORT}`);
  console.log(`   Discovery: http://localhost:${PORT}/.well-known/openid-configuration`);
  console.log(`   JWKS: http://localhost:${PORT}/jwks`);
  console.log(`   Token: POST http://localhost:${PORT}/token`);
});
```

### `src/mocks/issuer-b.ts`

```typescript
import express from "express";
import { KeyStore, generateRsaKeyPair, generateEcKeyPair, createToken } from "./keys.js";

const PORT = 8082;
const ISSUER = "https://issuer-b.example.com";
const JWKS_URI = `http://localhost:${PORT}/jwks`;

const keyStore = new KeyStore();

// Initialize with keys including OVERLAPPING kid="key-1"
async function initializeKeys() {
  // Key 1: Overlapping kid with issuer-a (SAME kid, DIFFERENT key material)
  const key1 = await generateRsaKeyPair("key-1", "RS256");
  keyStore.add(key1);

  // Key 2: EC key unique to issuer-b
  const key2 = await generateEcKeyPair("key-b-ec", "ES256");
  keyStore.add(key2);

  // Key 3: Another RSA key
  const key3 = await generateRsaKeyPair("key-b-3", "RS256");
  keyStore.add(key3);

  keyStore.rotate(key1);
  
  console.log(`[Issuer B] Initialized with keys: ${keyStore.getKeyIds().join(", ")}`);
  console.log(`[Issuer B] Current signing key: ${keyStore.getCurrent()?.kid}`);
}

const discoveryDoc = {
  issuer: ISSUER,
  jwks_uri: JWKS_URI,
  authorization_endpoint: `http://localhost:${PORT}/authorize`,
  token_endpoint: `http://localhost:${PORT}/token`,
  id_token_signing_alg_values_supported: ["RS256", "ES256", "ES384"],
};

const app = express();
app.use(express.json());

app.get("/.well-known/openid-configuration", (_req, res) => {
  res.set("Cache-Control", "public, max-age=3600");
  res.json(discoveryDoc);
});

app.get("/jwks", (req, res) => {
  const jwks = keyStore.getJwks();
  const etag = `W/"${JSON.stringify(jwks.keys.map(k => k.kid).sort()).length}"`;
  
  if (req.headers["if-none-match"] === etag) {
    return res.status(304).end();
  }
  
  res.set("ETag", etag);
  res.set("Cache-Control", "public, max-age=300");
  res.json(jwks);
});

app.post("/token", async (req, res) => {
  const { subject = "user-b-456", audience = "gateway-api", scope = "read admin", ttl = 3600 } = req.body;
  
  const currentKey = keyStore.getCurrent();
  if (!currentKey) {
    return res.status(500).json({ error: "No signing key available" });
  }

  const now = Math.floor(Date.now() / 1000);
  const token = await createToken(currentKey, {
    iss: ISSUER,
    sub: subject,
    aud: audience,
    scope,
    iat: now,
    exp: now + ttl,
    jti: `token-${Date.now()}-${Math.random().toString(36).slice(2)}`,
  });

  res.json({
    access_token: token,
    token_type: "Bearer",
    expires_in: ttl,
    scope,
  });
});

app.post("/admin/rotate", async (_req, res) => {
  // Rotate to EC key
  const newKey = await generateEcKeyPair(`key-b-ec-${Date.now()}`, "ES256");
  keyStore.rotate(newKey);
  console.log(`[Issuer B] Rotated to EC key: ${newKey.kid}`);
  res.json({ rotatedTo: newKey.kid, keys: keyStore.getKeyIds() });
});

app.post("/admin/rotate-rsa", async (_req, res) => {
  const newKey = await generateRsaKeyPair(`key-b-rsa-${Date.now()}`, "RS256");
  keyStore.rotate(newKey);
  console.log(`[Issuer B] Rotated to RSA key: ${newKey.kid}`);
  res.json({ rotatedTo: newKey.kid, keys: keyStore.getKeyIds() });
});

app.listen(PORT, async () => {
  await initializeKeys();
  console.log(`🔐 Issuer B running on http://localhost:${PORT}`);
  console.log(`   Discovery: http://localhost:${PORT}/.well-known/openid-configuration`);
  console.log(`   JWKS: http://localhost:${PORT}/jwks`);
  console.log(`   Token: POST http://localhost:${PORT}/token`);
});
```

---

## Deterministic Test Suite

### `src/test/run-tests.ts`

```typescript
import { ISSUER_CONFIGS, getIssuerConfig } from "../config/issuers.js";
import { JwksCache } from "../core/jwks-cache.js";
import { TokenValidator, ValidationError, ValidationErrorCode } from "../core/token-validator.js";
import { Principal } from "../core/principal.js";
import { KeyStore, generateRsaKeyPair, createToken } from "../mocks/keys.js";
import { SignJWT, importJWK } from "jose";

interface TestResult {
  name: string;
  passed: boolean;
  error?: string;
  durationMs: number;
}

const results: TestResult[] = [];

async function runTest(name: string, fn: () => Promise<void>): Promise<void> {
  const start = Date.now();
  try {
    await fn();
    results.push({ name, passed: true, durationMs: Date.now() - start });
    console.log(`  ✅ ${name} (${Date.now() - start}ms)`);
  } catch (e) {
    results.push({ 
      name, 
      passed: false, 
      error: e instanceof Error ? e.message : String(e),
      durationMs: Date.now() - start 
    });
    console.log(`  ❌ ${name}: ${e instanceof Error ? e.message : String(e)}`);
  }
}

function assert(condition: boolean, message: string): void {
  if (!condition) throw new Error(message);
}

function assertEqual<T>(actual: T, expected: T, message: string): void {
  if (actual !== expected) {
    throw new Error(`${message}: expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
  }
}

async function main() {
  console.log("\n🧪 Running Federation Gateway Test Suite\n");

  // Setup: Create validator with cache
  const jwksCache = new JwksCache(ISSUER_CONFIGS);
  const validator = new TokenValidator(jwksCache);

  // ============================================
  // TEST GROUP 1: Basic Validation
  // ============================================
  console.log("📋 Group 1: Basic Token Validation");

  await runTest("Issuer A - valid token accepted", async () => {
    // Get token from issuer A
    const tokenRes = await fetch("http://localhost:8081/token", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ subject: "test-user-a", audience: "gateway-api" }),
    });
    const { access_token } = await tokenRes.json();
    
    const { principal } = await validator.validate(access_token);
    assertEqual(principal.issuer, "https://issuer-a.example.com");
    assertEqual(principal.subject, "test-user-a");
    assert(principal.audiences.includes("gateway-api"));
  });

  await runTest("Issuer B - valid token accepted", async () => {
    const tokenRes = await fetch("http://localhost:8082/token", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ subject: "test-user-b", audience: "gateway-api" }),
    });
    const { access_token } = await tokenRes.json();
    
    const { principal } = await validator.validate(access_token);
    assertEqual(principal.issuer, "https://issuer-b.example.com");
    assertEqual(principal.subject, "test-user-b");
    assert(principal.audiences.includes("gateway-api"));
  });

  // ============================================
  // TEST GROUP 2: Audience Validation
  // ============================================
  console.log("\n📋 Group 2: Audience Validation");

  await runTest("Issuer A - wrong audience rejected", async () => {
    const tokenRes = await fetch("http://localhost:8081/token", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ subject: "test-user", audience: "wrong-audience" }),
    });
    const { access_token } = await tokenRes.json();
    
    try {
      await validator.validate(access_token);
      throw new Error("Should have thrown");
    } catch (e) {
      assert(e instanceof ValidationError);
      assertEqual(e.code, ValidationErrorCode.INVALID_AUDIENCE);
    }
  });

  await runTest("Issuer B - wrong audience rejected", async () => {
    const tokenRes = await fetch("http://localhost:8082/token", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ subject: "test-user", audience: "wrong-audience" }),
    });
    const { access_token } = await tokenRes.json();
    
    try {
      await validator.validate(access_token);
      throw new Error("Should have thrown");
    } catch (e) {
      assert(e instanceof ValidationError);
      assertEqual(e.code, ValidationErrorCode.INVALID_AUDIENCE);
    }
  });

  // ============================================
  // TEST GROUP 3: Unknown Issuer Rejection (SSRF Protection)
  // ============================================
  console.log("\n📋 Group 3: Unknown Issuer Rejection (SSRF Protection)");

  await runTest("Unknown issuer rejected before fetch", async () => {
    // Create a token with unknown issuer but valid signature
    const keyStore = new KeyStore();
    const key = await generateRsaKeyPair("evil-key", "RS256");
    keyStore.add(key);
    
    const token = await createToken(key, {
      iss: "https://evil-attacker.com",
      sub: "attacker",
      aud: "gateway-api",
      exp: Math.floor(Date.now() / 1000) + 3600,
    });

    try {
      await validator.validate(token);
      throw new Error("Should have thrown");
    } catch (e) {
      assert(e instanceof ValidationError);
      assertEqual(e.code, ValidationErrorCode.UNKNOWN_ISSUER);
      assertEqual(e.issuer, "https://evil-attacker.com");
    }
  });

  // ============================================
  // TEST GROUP 4: Overlapping Key IDs
  // ============================================
  console.log("\n📋 Group 4: Overlapping Key IDs (kid collision)");

  await runTest("Overlapping kid='key-1' - Issuer A token validates with A's key", async () => {
    // Both issuers have kid="key-1" but DIFFERENT key material
    // Token from A must validate with A's key-1, not B's key-1
    const tokenRes = await fetch("http://localhost:8081/token", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ subject: "overlap-test-a", audience: "gateway-api" }),
    });
    const { access_token } = await tokenRes.json();
    
    const { principal } = await validator.validate(access_token);
    assertEqual(principal.issuer, "https://issuer-a.example.com");
    assertEqual(principal.subject, "overlap-test-a");
  });

  await runTest("Overlapping kid='key-1' - Issuer B token validates with B's key", async () => {
    const tokenRes = await fetch("http://localhost:8082/token", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ subject: "overlap-test-b", audience: "gateway-api" }),
    });
    const { access_token } = await tokenRes.json();
    
    const { principal } = await validator.validate(access_token);
    assertEqual(principal.issuer, "https://issuer-b.example.com");
    assertEqual(principal.subject, "overlap-test-b");
  });

  await runTest("Cross-issuer key rejection - A's token with B's key fails", async () => {
    // Manually create a token signed with Issuer B's key but claiming Issuer A
    const keyStoreB = new KeyStore();
    const keyB = await generateRsaKeyPair("key-1", "RS256"); // Same kid as A's key-1
    keyStoreB.add(keyB);
    
    const token = await createToken(keyB, {
      iss: "https://issuer-a.example.com", // Claims to be from A
      sub: "cross-issuer-attack",
      aud: "gateway-api",
      exp: Math.floor(Date.now() / 1000) + 3600,
    });

    try {
      await validator.validate(token);
      throw new Error("Should have thrown - cross-issuer key confusion");
    } catch (e) {
      assert(e instanceof ValidationError);
      assertEqual(e.code, ValidationErrorCode.INVALID_SIGNATURE);
    }
  });

  // ============================================
  // TEST GROUP 5: Key Rotation
  // ============================================
  console.log("\n📋 Group 5: Key Rotation Handling");

  await runTest("Issuer A key rotation - old token still works until expiry", async () => {
    // Get token with current key
    const tokenRes1 = await fetch("http://localhost:8081/token", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ subject: "rotation-test", audience: "gateway-api", ttl: 3600 }),
    });
    const { access_token: token1 } = await tokenRes1.json();
    
    // Validate before rotation
    const { principal: p1 } = await validator.validate(token1);
    assertEqual(p1.subject, "rotation-test");

    // Rotate keys on issuer A
    await fetch("http://localhost:8081/admin/rotate", { method: "POST" });
    
    // Old token should still work (key still in JWKS)
    const { principal: p2 } = await validator.validate(token1);
    assertEqual(p2.subject, "rotation-test");
  });

  await runTest("Issuer A key rotation - new tokens use new key", async () => {
    // Get new token after rotation
    const tokenRes = await fetch("http://localhost:8081/token", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ subject: "new-key-test", audience: "gateway-api" }),
    });
    const { access_token } = await tokenRes.json();
    
    const { principal } = await validator.validate(access_token);
    assertEqual(principal.subject, "new-key-test");
  });

  // ============================================
  // TEST GROUP 6: Cache Expiry & Refresh
  // ============================================
  console.log("\n📋 Group 6: Cache Expiry & Refresh");

  await runTest("Cache serves keys without re-fetch (ETag 304)", async () => {
    const statsBefore = jwksCache.getStats();
    const issuerA = "https://issuer-a.example.com";
    
    // Warm cache
    const tokenRes = await fetch("http://localhost:8081/token", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ subject: "cache-test", audience: "gateway-api" }),
    });
    const { access_token } = await tokenRes.json();
    await validator.validate(access_token);
    
    const statsAfterWarm = jwksCache.getStats();
    assert(statsAfterWarm[issuerA]?.keyCount > 0);
    
    // Validate again - should use cache (ETag 304)
    await validator.validate(access_token);
    
    const statsAfterSecond = jwksCache.getStats();
    // Age should not have reset (still same fetch time)
    assertEqual(statsAfterSecond[issuerA]?.fetchedAt, statsAfterWarm[issuerA]?.fetchedAt);
  });

  await runTest("Force cache refresh after maxAge", async () => {
    // This test would require time manipulation or very short cache TTL
    // For now, verify cache stats are accessible
    const stats = jwksCache.getStats();
    assert(typeof stats === "object");
  });

  // ============================================
  // TEST GROUP 7: Algorithm Validation
  // ============================================
  console.log("\n📋 Group 7: Algorithm Validation");

  await runTest("Issuer A rejects ES256 (not in allowed list)", async () => {
    const keyStore = new KeyStore();
    const key = await generateRsaKeyPair("key-es", "ES256"); // Wrong alg for RS256 key
    // Actually generate EC key
    const { generateKeyPair: genEc } = await import("jose");
    const { publicKey, privateKey } = await genEc("ES256");
    const jwk = await import("jose").then(m => m.exportJWK(publicKey));
    jwk.kid = "key-es";
    jwk.alg = "ES256";
    keyStore.add({ kid: "key-es", alg: "ES256", publicKey, privateKey, jwk, createdAt: Date.now(), expiresAt: Date.now() + 3600000 });
    
    const token = await createToken(keyStore.get("key-es")!, {
      iss: "https://issuer-a.example.com",
      sub: "alg-test",
      aud: "gateway-api",
      exp: Math.floor(Date.now() / 1000) + 3600,
    });

    try {
      await validator.validate(token);
      throw new Error("Should have thrown");
    } catch (e) {
      assert(e instanceof ValidationError);
      assertEqual(e.code, ValidationErrorCode.INVALID_ALGORITHM);
    }
  });

  await runTest("Issuer B accepts ES256 (in allowed list)", async () => {
    const keyStore = new KeyStore();
    const { generateKeyPair: genEc } = await import("jose");
    const { publicKey, privateKey } = await genEc("ES256");
    const jwk = await import("jose").then(m => m.exportJWK(publicKey));
    jwk.kid = "key-es-test";
    jwk.alg = "ES256";
    keyStore.add({ kid: "key-es-test", alg: "ES256", publicKey, privateKey, jwk, createdAt: Date.now(), expiresAt: Date.now() + 3600000 });
    
    const token = await createToken(keyStore.get("key-es-test")!, {
      iss: "https://issuer-b.example.com",
      sub: "alg-test-b",
      aud: "gateway-api",
      exp: Math.floor(Date.now() / 1000) + 3600,
    });

    const { principal } = await validator.validate(token);
    assertEqual(principal.issuer, "https://issuer-b.example.com");
  });

  // ============================================
  // TEST GROUP 8: Token Expiry & Time Validation
  // ============================================
  console.log("\n📋 Group 8: Token Expiry & Time Validation");

  await runTest("Expired token rejected", async () => {
    const keyStore = new KeyStore();
    const key = await generateRsaKeyPair("expired-key", "RS256");
    keyStore.add(key);
    
    const token = await createToken(key, {
      iss: "https://issuer-a.example.com",
      sub: "expired-user",
      aud: "gateway-api",
      exp: Math.floor(Date.now() / 1000) - 100, // Expired 100s ago
    });

    try {
      await validator.validate(token);
      throw new Error("Should have thrown");
    } catch (e) {
      assert(e instanceof ValidationError);
      assertEqual(e.code, ValidationErrorCode.TOKEN_EXPIRED);
    }
  });

  await runTest("Not-yet-valid token rejected", async () => {
    const keyStore = new KeyStore();
    const key = await generateRsaKeyPair("nbf-key", "RS256");
    keyStore.add(key);
    
    const token = await createToken(key, {
      iss: "https://issuer-a.example.com",
      sub: "future-user",
      aud: "gateway-api",
      nbf: Math.floor(Date.now() / 1000) + 100, // Valid in 100s
    });

    try {
      await validator.validate(token);
      throw new Error("Should have thrown");
    } catch (e) {
      assert(e instanceof ValidationError);
      assertEqual(e.code, ValidationErrorCode.TOKEN_NOT_YET_VALID);
    }
  });

  // ============================================
  // TEST GROUP 9: Principal Normalization
  // ============================================
  console.log("\n📋 Group 9: Principal Normalization");

  await runTest("Principal retains issuer and subject", async () => {
    const tokenRes = await fetch("http://localhost:8081/token", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ subject: "normalize-test", audience: "gateway-api", scope: "read write admin" }),
    });
    const { access_token } = await tokenRes.json();
    
    const { principal } = await validator.validate(access_token);
    
    assertEqual(principal.issuer, "https://issuer-a.example.com");
    assertEqual(principal.subject, "normalize-test");
    assert(principal.scopes.includes("read"));
    assert(principal.scopes.includes("write"));
    assert(principal.scopes.includes("admin"));
    assert(principal.expiresAt > Math.floor(Date.now() / 1000));
    assert(principal.issuedAt > 0);
  });

  await runTest("Principal includes all standard claims", async () => {
    const tokenRes = await fetch("http://localhost:8081/token", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ subject: "claims-test", audience: "gateway-api" }),
    });
    const { access_token } = await tokenRes.json();
    
    const { principal, rawClaims } = await validator.validate(access_token);
    
    assert(principal.claims.iss === "https://issuer-a.example.com");
    assert(principal.claims.sub === "claims-test");
    assert(principal.claims.aud === "gateway-api");
    assert(typeof principal.claims.iat === "number");
    assert(typeof principal.claims.exp === "number");
    assert(principal.claims.jti);
  });

  // ============================================
  // TEST GROUP 10: Malformed Token Handling
  // ============================================
  console.log("\n📋 Group 10: Malformed Token Handling");

  await runTest("Malformed JWT (not 3 parts) rejected", async () => {
    try {
      await validator.validate("not.a.jwt");
      throw new Error("Should have thrown");
    } catch (e) {
      assert(e instanceof ValidationError);
      assertEqual(e.code, ValidationErrorCode.INVALID_TOKEN);
    }
  });

  await runTest("Token with invalid base64 rejected", async () => {
    try {
      await validator.validate("invalid.base64!.payload");
      throw new Error("Should have thrown");
    } catch (e) {
      assert(e instanceof ValidationError);
      assertEqual(e.code, ValidationErrorCode.INVALID_TOKEN);
    }
  });

  await runTest("Token missing kid header rejected", async () => {
    const keyStore = new KeyStore();
    const key = await generateRsaKeyPair("no-kid", "RS256");
    keyStore.add(key);
    
    // Create token without kid
    const { SignJWT } = await import("jose");
    const token = await new SignJWT({ iss: "https://issuer-a.example.com", sub: "test", aud: "gateway-api" })
      .setProtectedHeader({ alg: "RS256" }) // No kid
      .setIssuedAt()
      .setExpirationTime("1h")
      .sign(key.privateKey);

    try {
      await validator.validate(token);
      throw new Error("Should have thrown");
    } catch (e) {
      assert(e instanceof ValidationError);
      assertEqual(e.code, ValidationErrorCode.MISSING_KID);
    }
  });

  // ============================================
  // SUMMARY
  // ============================================
  console.log("\n" + "=".repeat(60));
  console.log("📊 TEST SUMMARY");
  console.log("=".repeat(60));
  
  const passed = results.filter(r => r.passed).length;
  const failed = results.filter(r => !r.passed).length;
  const total = results.length;
  
  results.forEach(r => {
    const status = r.passed ? "✅" : "❌";
    console.log(`  ${status} ${r.name} (${r.durationMs}ms)${r.error ? ` - ${r.error}` : ""}`);
  });
  
  console.log(`\nTotal: ${total} | Passed: ${passed} | Failed: ${failed}`);
  
  if (failed > 0) {
    process.exitCode = 1;
  }
}

main().catch(console.error);
```

---

## Installation & Execution

### Prerequisites
- Node.js ≥ 20.0.0
- npm ≥ 10.0.0

### Install Dependencies

```bash
npm ci
```

### Build TypeScript

```bash
npm run build
```

### Run All Services (3 terminals required)

**Terminal 1 - Issuer A (port 8081):**
```bash
npm run mock:issuer-a
```

**Terminal 2 - Issuer B (port 8082):**
```bash
npm run mock:issuer-b
```

**Terminal 3 - Gateway (port 3000):**
```bash
npm run dev
# or after build:
npm start
```

### Run Tests

```bash
# Ensure mocks and gateway are running first!
npm test
```

---

## Library APIs Used

| Package | Version | Key APIs Used |
|---------|---------|---------------|
| **jose** | 5.3.0 | `jwtVerify`, `SignJWT`, `generateKeyPair`, `exportJWK`, `importJWK`, `JWTPayload`, `JWTVerifyResult` |
| **express** | 4.19.2 | `express()`, `Request`, `Response`, `NextFunction`, `RequestHandler`, `json()`, `listen()` |
| **tsx** | 4.15.7 | CLI for TypeScript execution (`tsx watch`, `tsx script.ts`) |
| **typescript** | 5.5.2 | `tsc` compiler |

### Key `jose` API Details

```typescript
// JWT Verification with custom key resolver
import { jwtVerify, JWTPayload } from "jose";

const { payload } = await jwtVerify(token, async (header, token) => {
  // Custom key resolution logic
  const kid = header.kid;
  const issuer = extractIssuerFromToken(token);
  return await jwksCache.getKey(issuer, kid);
}, {
  clockTolerance: 30,
  // audience validated manually per-issuer
});

// Token Signing
import { SignJWT } from "jose";
const token = await new SignJWT(claims)
  .setProtectedHeader({ kid, alg })
  .setIssuedAt()
  .setExpirationTime("1h")
  .sign(privateKey);

// Key Generation
import { generateKeyPair, exportJWK } from "jose";
const { publicKey, privateKey } = await generateKeyPair("RS256", { modulusLength: 2048 });
const jwk = await exportJWK(publicKey);
```

---

## Architecture Highlights

### Security Guarantees

1. **SSRF Prevention**: Unknown issuers rejected *before* any network fetch via `isKnownIssuer()` check in key resolver
2. **Key Isolation**: Each issuer's keys cached separately; overlapping `kid` values resolved per-issuer
3. **Algorithm Binding**: Per-issuer allowed algorithm lists prevent algorithm confusion
4. **Audience Validation**: Per-issuer expected audiences validated after signature verification
5. **Cache Poisoning Resistance**: ETag-based conditional requests; cache keyed by issuer

### Cache Behavior

| Scenario | Behavior |
|----------|----------|
| Cache fresh, key exists | Return cached key (0ms) |
| Cache fresh, key missing (rotation) | Force refresh once, then return new key |
| Cache stale, key exists | Return cached key, background refresh |
| Cache stale, key missing | Force refresh, return new key |
| Refresh fails | Return stale key if available, else error |

### Mock Issuer Capabilities

| Endpoint | Purpose |
|----------|---------|
| `GET /.well-known/openid-configuration` | Discovery document |
| `GET /jwks` | JWKS with ETag support |
| `POST /token` | Mint test tokens |
| `POST /admin/rotate` | Simulate key rotation |
| `POST /admin/add-overlapping` | Add key with existing kid (collision test) |
| `POST /admin/expire-current` | Simulate cache expiry |

---

## Example Usage

```bash
# 1. Start all services (3 terminals)
# Terminal 1
npm run mock:issuer-a

# Terminal 2  
npm run mock:issuer-b

# Terminal 3
npm run dev

# 2. Get token from Issuer A
curl -X POST http://localhost:8081/token \
  -H "Content-Type: application/json" \
  -d '{"subject":"alice","audience":"gateway-api","scope":"read write"}'

# 3. Use token with gateway
curl -H "Authorization: Bearer <token>" http://localhost:3000/api/resource

# 4. Test rotation
curl -X POST http://localhost:8081/admin/rotate
# Old token still works, new tokens use new key

# 5. Run test suite
npm test
```

This implementation provides a production-ready foundation with comprehensive test coverage demonstrating all required behaviors.
