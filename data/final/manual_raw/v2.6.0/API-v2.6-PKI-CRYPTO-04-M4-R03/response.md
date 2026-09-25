I'll create a comprehensive, production-ready PKCS#11 signing service with all the requirements. Let me build this step by step.

## Project Structure

```
pkcs11-signing-service/
├── package.json
├── tsconfig.json
├── jest.config.js
├── .env.example
├── src/
│   ├── index.ts                 # Main entry point
│   ├── types.ts                 # TypeScript interfaces
│   ├── errors.ts                # Custom error classes
│   ├── adapters/
│   │   ├── index.ts             # Adapter exports
│   │   ├── Pkcs11Adapter.ts     # Interface definition
│   │   ├── RealPkcs11Adapter.ts # Real PKCS#11 implementation
│   │   └── MockPkcs11Adapter.ts # Mock for testing
│   ├── services/
│   │   ├── SigningService.ts    # Core signing logic
│   │   ├── SessionManager.ts    # Session lifecycle
│   │   ├── TokenManager.ts      # Token/slot enumeration
│   │   └── CsrGenerator.ts      # PKCS#10 CSR creation
│   └── utils/
│       ├── pin.ts               # PIN handling
│       └── mechanism.ts         # Mechanism utilities
├── tests/
│   ├── mock/
│   │   └── mockSetup.ts         # Mock configuration
│   ├── unit/
│   │   ├── SigningService.test.ts
│   │   ├── SessionManager.test.ts
│   │   ├── TokenManager.test.ts
│   │   └── CsrGenerator.test.ts
│   └── integration/
│       └── realDevice.test.ts   # Requires actual HSM
└── examples/
    ├── basic-sign.ts
    ├── create-csr.ts
    └── enumerate-tokens.ts
```

## package.json

```json
{
  "name": "pkcs11-signing-service",
  "version": "1.0.0",
  "description": "Production-ready PKCS#11 signing service for Node.js with TypeScript",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "ts-node src/index.ts",
    "test": "jest --coverage",
    "test:unit": "jest --testPathPattern=tests/unit",
    "test:integration": "jest --testPathPattern=tests/integration",
    "test:watch": "jest --watch",
    "lint": "eslint src/**/*.ts",
    "prepublishOnly": "npm run build && npm run test",
    "example:sign": "ts-node examples/basic-sign.ts",
    "example:csr": "ts-node examples/create-csr.ts",
    "example:enumerate": "ts-node examples/enumerate-tokens.ts"
  },
  "keywords": [
    "pkcs11",
    "hsm",
    "signing",
    "certificate",
    "csr",
    "crypto",
    "security"
  ],
  "author": "Security Engineering Team",
  "license": "MIT",
  "dependencies": {
    "pkcs11js": "^1.3.0",
    "node-forge": "^1.3.1",
    "dotenv": "^16.3.1",
    "pino": "^8.16.2",
    "pino-pretty": "^10.2.3"
  },
  "devDependencies": {
    "@types/node": "^20.10.0",
    "@types/jest": "^29.5.11",
    "@types/node-forge": "^1.3.10",
    "typescript": "^5.3.2",
    "ts-node": "^10.9.2",
    "jest": "^29.7.0",
    "ts-jest": "^29.1.1",
    "eslint": "^8.55.0",
    "@typescript-eslint/eslint-plugin": "^6.13.1",
    "@typescript-eslint/parser": "^6.13.1"
  },
  "engines": {
    "node": ">=18.0.0"
  },
  "packageManager": "npm@10.2.3"
}
```

## tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "moduleResolution": "node",
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests", "examples"]
}
```

## jest.config.js

```javascript
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/tests'],
  testMatch: ['**/*.test.ts'],
  moduleFileExtensions: ['ts', 'js', 'json'],
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/index.ts',
    '!src/adapters/MockPkcs11Adapter.ts'
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  setupFilesAfterEnv: ['<rootDir>/tests/mock/mockSetup.ts'],
  testTimeout: 30000,
  verbose: true
};
```

## .env.example

```bash
# PKCS#11 Library Path (required)
# Examples:
#   SoftHSM2: /usr/local/lib/softhsm/libsofthsm2.so
#   OpenSC:   /usr/lib/x86_64-linux-gnu/opensc-pkcs11.so
#   AWS CloudHSM: /opt/cloudhsm/lib/libcloudhsm_pkcs11.so
#   Nitro Enclaves: /usr/lib/nitro_enclaves/pkcs11.so
PKCS11_LIB_PATH=/usr/local/lib/softhsm/libsofthsm2.so

# Token Authentication
# PIN can be provided via env var or interactive prompt
PKCS11_PIN=1234
PKCS11_SO_PIN=5678

# Slot/Token Selection (optional - will use first available if not specified)
PKCS11_SLOT_INDEX=0
PKCS11_TOKEN_LABEL=signing-token

# Key Identification (at least one required)
PKCS11_KEY_LABEL=signing-key
PKCS11_KEY_ID=01020304

# Default Signing Mechanism (optional)
# Supported: CKM_RSA_PKCS, CKM_SHA256_RSA_PKCS, CKM_ECDSA, CKM_SHA384_RSA_PKCS, CKM_SHA512_RSA_PKCS
PKCS11_DEFAULT_MECHANISM=CKM_SHA256_RSA_PKCS

# Session Configuration
PKCS11_SESSION_POOL_SIZE=5
PKCS11_READ_ONLY_SESSION=true

# Logging
LOG_LEVEL=info
```

## Source Files

### src/types.ts

```typescript
/**
 * Core type definitions for the PKCS#11 Signing Service
 */

// PKCS#11 Constants (subset from PKCS#11 v2.40)
export enum CKK {
  RSA = 0x00000000,
  EC = 0x00000003,
  EC_EDWARDS = 0x00000040,
}

export enum CKM {
  RSA_PKCS = 0x00000001,
  RSA_PKCS_OAEP = 0x00000009,
  SHA256_RSA_PKCS = 0x00000040,
  SHA384_RSA_PKCS = 0x00000041,
  SHA512_RSA_PKCS = 0x00000042,
  SHA256_RSA_PKCS_PSS = 0x00000043,
  SHA384_RSA_PKCS_PSS = 0x00000044,
  SHA512_RSA_PKCS_PSS = 0x00000045,
  ECDSA = 0x00001041,
  ECDSA_SHA256 = 0x00001042,
  ECDSA_SHA384 = 0x00001043,
  ECDSA_SHA512 = 0x00001044,
  SHA256 = 0x00000250,
  SHA384 = 0x00000251,
  SHA512 = 0x00000252,
}

export enum CKO {
  DATA = 0x00000000,
  CERTIFICATE = 0x00000001,
  PUBLIC_KEY = 0x00000002,
  PRIVATE_KEY = 0x00000003,
  SECRET_KEY = 0x00000004,
}

export enum CKF {
  RWF = 0x00000001,
  SERIAL_SESSION = 0x00000004,
  RW_SESSION = 0x00000002,
}

export enum CKU {
  SO = 0,
  USER = 1,
  CONTEXT_SPECIFIC = 2,
}

export enum CKR {
  OK = 0x00000000,
  CANCEL = 0x00000001,
  HOST_MEMORY = 0x00000002,
  SLOT_ID_INVALID = 0x00000003,
  GENERAL_ERROR = 0x00000005,
  FUNCTION_FAILED = 0x00000006,
  ARGUMENTS_BAD = 0x00000007,
  NO_EVENT = 0x00000008,
  NEED_TO_CREATE_THREADS = 0x00000009,
  CANT_LOCK = 0x0000000A,
  ATTRIBUTE_READ_ONLY = 0x00000010,
  ATTRIBUTE_SENSITIVE = 0x00000011,
  ATTRIBUTE_TYPE_INVALID = 0x00000012,
  ATTRIBUTE_VALUE_INVALID = 0x00000013,
  ACTION_PROHIBITED = 0x00000014,
  DATA_INVALID = 0x00000020,
  DATA_LEN_RANGE = 0x00000021,
  DEVICE_ERROR = 0x00000030,
  DEVICE_MEMORY = 0x00000031,
  DEVICE_REMOVED = 0x00000032,
  ENCRYPTED_DATA_INVALID = 0x00000040,
  ENCRYPTED_DATA_LEN_RANGE = 0x00000041,
  FUNCTION_CANCELED = 0x00000050,
  FUNCTION_NOT_PARALLEL = 0x00000051,
  FUNCTION_NOT_SUPPORTED = 0x00000054,
  KEY_HANDLE_INVALID = 0x00000060,
  KEY_SIZE_RANGE = 0x00000062,
  KEY_TYPE_INCONSISTENT = 0x00000063,
  KEY_NOT_NEEDED = 0x00000064,
  KEY_CHANGED = 0x00000065,
  KEY_NEEDED = 0x00000066,
  KEY_INDIGESTIBLE = 0x00000067,
  KEY_FUNCTION_NOT_PERMITTED = 0x00000068,
  KEY_NOT_WRAPPABLE = 0x00000069,
  KEY_UNEXTRACTABLE = 0x0000006A,
  MECHANISM_INVALID = 0x00000070,
  MECHANISM_PARAM_INVALID = 0x00000071,
  OBJECT_HANDLE_INVALID = 0x00000082,
  OPERATION_ACTIVE = 0x00000090,
  OPERATION_NOT_INITIALIZED = 0x00000091,
  PIN_INCORRECT = 0x000000A0,
  PIN_INVALID = 0x000000A1,
  PIN_LEN_RANGE = 0x000000A2,
  PIN_EXPIRED = 0x000000A3,
  PIN_LOCKED = 0x000000A4,
  SESSION_CLOSED = 0x000000B0,
  SESSION_COUNT = 0x000000B1,
  SESSION_HANDLE_INVALID = 0x000000B3,
  SESSION_PARALLEL_NOT_SUPPORTED = 0x000000B4,
  SESSION_READ_ONLY = 0x000000B5,
  SESSION_EXISTS = 0x000000B6,
  SESSION_READ_ONLY_EXISTS = 0x000000B7,
  SESSION_READ_WRITE_SO_EXISTS = 0x000000B8,
  SIGNATURE_INVALID = 0x000000C0,
  SIGNATURE_LEN_RANGE = 0x000000C1,
  TEMPLATE_INCOMPLETE = 0x000000D0,
  TEMPLATE_INCONSISTENT = 0x000000D1,
  TOKEN_NOT_PRESENT = 0x000000E0,
  TOKEN_NOT_RECOGNIZED = 0x000000E1,
  TOKEN_WRITE_PROTECTED = 0x000000E2,
  UNWRAPPING_KEY_HANDLE_INVALID = 0x000000F0,
  UNWRAPPING_KEY_SIZE_RANGE = 0x000000F1,
  UNWRAPPING_KEY_TYPE_INCONSISTENT = 0x000000F2,
  USER_ALREADY_LOGGED_IN = 0x00000100,
  USER_NOT_LOGGED_IN = 0x00000101,
  USER_PIN_NOT_INITIALIZED = 0x00000102,
  USER_TYPE_INVALID = 0x00000103,
  USER_ANOTHER_ALREADY_LOGGED_IN = 0x00000104,
  USER_TOO_MANY_TYPES = 0x00000105,
  WRAPPED_KEY_INVALID = 0x00000110,
  WRAPPED_KEY_LEN_RANGE = 0x00000111,
  WRAPPING_KEY_HANDLE_INVALID = 0x00000112,
  WRAPPING_KEY_SIZE_RANGE = 0x00000113,
  WRAPPING_KEY_TYPE_INCONSISTENT = 0x00000114,
  RANDOM_SEED_NOT_SUPPORTED = 0x00000120,
  RANDOM_NO_RNG = 0x00000121,
  DOMAIN_PARAMS_INVALID = 0x00000130,
  BUFFER_TOO_SMALL = 0x00000150,
  SAVED_STATE_INVALID = 0x00000160,
  INFORMATION_SENSITIVE = 0x00000170,
  STATE_UNSAVEABLE = 0x00000180,
  CRYPTOKI_NOT_INITIALIZED = 0x00000190,
  CRYPTOKI_ALREADY_INITIALIZED = 0x00000191,
  MUTEX_BAD = 0x000001A0,
  MUTEX_NOT_LOCKED = 0x000001A1,
  NEW_PIN_MODE = 0x000001B0,
  NEXT_OTP = 0x000001B1,
  EXCEEDED_MAX_ITERATIONS = 0x000001B5,
  FIPS_SELF_TEST_FAILED = 0x000001B6,
  LIBRARY_LOAD_FAILED = 0x000001B7,
  PIN_TOO_WEAK = 0x000001B8,
  PUBLIC_KEY_INVALID = 0x000001B9,
  FUNCTION_REJECTED = 0x000001BA,
  VENDOR_DEFINED = 0x80000000,
}

// Type-safe mechanism mapping
export type MechanismType = 
  | CKM.RSA_PKCS
  | CKM.SHA256_RSA_PKCS
  | CKM.SHA384_RSA_PKCS
  | CKM.SHA512_RSA_PKCS
  | CKM.SHA256_RSA_PKCS_PSS
  | CKM.SHA384_RSA_PKCS_PSS
  | CKM.SHA512_RSA_PKCS_PSS
  | CKM.ECDSA
  | CKM.ECDSA_SHA256
  | CKM.ECDSA_SHA384
  | CKM.ECDSA_SHA512;

export interface Mechanism {
  mechanism: MechanismType;
  parameter?: Buffer;
}

export interface SlotInfo {
  slotIndex: number;
  slotDescription: string;
  manufacturerId: string;
  hardwareVersion: { major: number; minor: number };
  firmwareVersion: { major: number; minor: number };
  tokenPresent: boolean;
}

export interface TokenInfo {
  label: string;
  manufacturerId: string;
  model: string;
  serialNumber: string;
  flags: number;
  maxSessionCount: number;
  sessionCount: number;
  maxRwSessionCount: number;
  rwSessionCount: number;
  maxPinLen: number;
  minPinLen: number;
  totalPublicMemory: number;
  freePublicMemory: number;
  totalPrivateMemory: number;
  freePrivateMemory: number;
  hardwareVersion: { major: number; minor: number };
  firmwareVersion: { major: number; minor: number };
  utcTime: string;
}

export interface KeyInfo {
  handle: any; // PKCS#11 object handle
  label: string;
  id: Buffer;
  keyType: CKK;
  keySize: number;
  extractable: boolean;
  sign: boolean;
  verify: boolean;
  decrypt: boolean;
  wrap: boolean;
  unwrap: boolean;
  derive: boolean;
  publicKeyHandle?: any;
}

export interface SessionConfig {
  readOnly: boolean;
  serialSession: boolean;
}

export interface SignRequest {
  data: Buffer;
  mechanism?: MechanismType;
  keyLabel?: string;
  keyId?: Buffer;
}

export interface SignResponse {
  signature: Buffer;
  mechanism: MechanismType;
  keyLabel: string;
  keyId: Buffer;
}

export interface CsrRequest {
  subject: CsrSubject;
  keyLabel: string;
  keyId?: Buffer;
  mechanism?: MechanismType;
  extensions?: CsrExtension[];
}

export interface CsrSubject {
  commonName: string;
  organization?: string;
  organizationalUnit?: string;
  country?: string;
  state?: string;
  locality?: string;
  emailAddress?: string;
}

export interface CsrExtension {
  oid: string;
  critical: boolean;
  value: any;
}

export interface CsrResponse {
  csrPem: string;
  csrDer: Buffer;
  publicKeyPem: string;
  keyLabel: string;
  keyId: Buffer;
}

export interface ServiceConfig {
  libPath: string;
  pin: string;
  soPin?: string;
  slotIndex?: number;
  tokenLabel?: string;
  keyLabel: string;
  keyId?: Buffer;
  defaultMechanism: MechanismType;
  sessionPoolSize: number;
  readOnlySession: boolean;
  logLevel: string;
}
```

### src/errors.ts

```typescript
/**
 * Custom error classes for the PKCS#11 Signing Service
 */

export class Pkcs11Error extends Error {
  public readonly code: number;
  public readonly pkcs11Code: number;
  public readonly retryable: boolean;

  constructor(message: string, pkcs11Code: number, retryable = false) {
    super(message);
    this.name = 'Pkcs11Error';
    this.pkcs11Code = pkcs11Code;
    this.code = pkcs11Code;
    this.retryable = retryable;
    
    // Maintains proper stack trace in V8 environments
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, Pkcs11Error);
    }
  }

  static fromReturnCode(code: number, context: string): Pkcs11Error {
    const messages: Record<number, string> = {
      0x00000001: 'Operation canceled',
      0x00000002: 'Host memory allocation failed',
      0x00000003: 'Invalid slot ID',
      0x00000005: 'General error',
      0x00000006: 'Function failed',
      0x00000007: 'Invalid arguments',
      0x00000008: 'No event',
      0x00000009: 'Cannot create threads',
      0x0000000A: 'Cannot lock mutex',
      0x00000010: 'Attribute read-only',
      0x00000011: 'Attribute sensitive',
      0x00000012: 'Invalid attribute type',
      0x00000013: 'Invalid attribute value',
      0x00000014: 'Action prohibited',
      0x00000020: 'Invalid data',
      0x00000021: 'Data length out of range',
      0x00000030: 'Device error',
      0x00000031: 'Device memory error',
      0x00000032: 'Device removed',
      0x00000040: 'Invalid encrypted data',
      0x00000041: 'Encrypted data length out of range',
      0x00000050: 'Function canceled',
      0x00000051: 'Function not parallel',
      0x00000054: 'Function not supported',
      0x00000060: 'Invalid key handle',
      0x00000062: 'Key size out of range',
      0x00000063: 'Key type inconsistent',
      0x00000064: 'Key not needed',
      0x00000065: 'Key changed',
      0x00000066: 'Key needed',
      0x00000067: 'Key indigestible',
      0x00000068: 'Key function not permitted',
      0x00000069: 'Key not wrappable',
      0x0000006A: 'Key unextractable',
      0x00000070: 'Invalid mechanism',
      0x00000071: 'Invalid mechanism parameter',
      0x00000082: 'Invalid object handle',
      0x00000090: 'Operation active',
      0x00000091: 'Operation not initialized',
      0x000000A0: 'Incorrect PIN',
      0x000000A1: 'Invalid PIN',
      0x000000A2: 'PIN length out of range',
      0x000000A3: 'PIN expired',
      0x000000A4: 'PIN locked',
      0x000000B0: 'Session closed',
      0x000000B1: 'Session count exceeded',
      0x000000B3: 'Invalid session handle',
      0x000000B4: 'Parallel sessions not supported',
      0x000000B5: 'Read-only session',
      0x000000B6: 'Session exists',
      0x000000B7: 'Read-only session exists',
      0x000000B8: 'Read-write SO session exists',
      0x000000C0: 'Invalid signature',
      0x000000C1: 'Signature length out of range',
      0x000000D0: 'Template incomplete',
      0x000000D1: 'Template inconsistent',
      0x000000E0: 'Token not present',
      0x000000E1: 'Token not recognized',
      0x000000E2: 'Token write protected',
      0x00000100: 'User already logged in',
      0x00000101: 'User not logged in',
      0x00000102: 'User PIN not initialized',
      0x00000103: 'Invalid user type',
      0x00000104: 'Another user already logged in',
      0x00000105: 'Too many user types',
      0x00000150: 'Buffer too small',
      0x00000160: 'Saved state invalid',
      0x00000170: 'Information sensitive',
      0x00000180: 'State unsaveable',
      0x00000190: 'Cryptoki not initialized',
      0x00000191: 'Cryptoki already initialized',
      0x000001A0: 'Bad mutex',
      0x000001A1: 'Mutex not locked',
      0x000001B0: 'New PIN mode',
      0x000001B1: 'Next OTP',
      0x000001B5: 'Exceeded max iterations',
      0x000001B6: 'FIPS self-test failed',
      0x000001B7: 'Library load failed',
      0x000001B8: 'PIN too weak',
      0x000001B9: 'Public key invalid',
      0x000001BA: 'Function rejected',
    };

    const message = messages[code] || `Unknown PKCS#11 error: 0x${code.toString(16).toUpperCase().padStart(8, '0')}`;
    const retryable = [0x00000030, 0x00000032, 0x00000090, 0x000000B1].includes(code);
    
    return new Pkcs11Error(`${context}: ${message}`, code, retryable);
  }
}

export class TokenNotFoundError extends Error {
  public readonly tokenLabel?: string;
  public readonly slotIndex?: number;

  constructor(message: string, tokenLabel?: string, slotIndex?: number) {
    super(message);
    this.name = 'TokenNotFoundError';
    this.tokenLabel = tokenLabel;
    this.slotIndex = slotIndex;
  }
}

export class KeyNotFoundError extends Error {
  public readonly keyLabel?: string;
  public readonly keyId?: Buffer;

  constructor(message: string, keyLabel?: string, keyId?: Buffer) {
    super(message);
    this.name = 'KeyNotFoundError';
    this.keyLabel = keyLabel;
    this.keyId = keyId;
  }
}

export class MechanismMismatchError extends Error {
  public readonly requestedMechanism: number;
  public readonly supportedMechanisms: number[];
  public readonly keyType: number;

  constructor(
    message: string,
    requestedMechanism: number,
    supportedMechanisms: number[],
    keyType: number
  ) {
    super(message);
    this.name = 'MechanismMismatchError';
    this.requestedMechanism = requestedMechanism;
    this.supportedMechanisms = supportedMechanisms;
    this.keyType = keyType;
  }
}

export class SessionError extends Error {
  public readonly sessionHandle?: any;
  public readonly operation: string;

  constructor(message: string, operation: string, sessionHandle?: any) {
    super(message);
    this.name = 'SessionError';
    this.operation = operation;
    this.sessionHandle = sessionHandle;
  }
}

export class ConfigurationError extends Error {
  public readonly configKey: string;

  constructor(message: string, configKey: string) {
    super(message);
    this.name = 'ConfigurationError';
    this.configKey = configKey;
  }
}

export class CsrGenerationError extends Error {
  public readonly reason: string;

  constructor(message: string, reason: string) {
    super(message);
    this.name = 'CsrGenerationError';
    this.reason = reason;
  }
}
```

### src/adapters/Pkcs11Adapter.ts

```typescript
/**
 * PKCS#11 Adapter Interface - Mockable abstraction for PKCS#11 operations
 */

import {
  SlotInfo,
  TokenInfo,
  KeyInfo,
  Mechanism,
  MechanismType,
  SessionConfig,
  CKK,
  CKO,
  CKF,
  CKR,
} from '../types';

export interface Pkcs11LibraryInfo {
  manufacturerId: string;
  libraryDescription: string;
  libraryVersion: { major: number; minor: number };
  cryptokiVersion: { major: number; minor: number };
}

export interface SessionHandle {
  handle: any;
  slotIndex: number;
  readOnly: boolean;
  createdAt: number;
  inUse: boolean;
}

export interface FindObjectsTemplate {
  class?: CKO;
  keyType?: CKK;
  label?: string;
  id?: Buffer;
  token?: boolean;
  private?: boolean;
  sign?: boolean;
  verify?: boolean;
}

export interface AttributeMap {
  [key: number]: any;
}

export interface Pkcs11Adapter {
  // Library lifecycle
  initialize(libraryPath: string): Promise<void>;
  finalize(): Promise<void>;
  getLibraryInfo(): Promise<Pkcs11LibraryInfo>;
  isInitialized(): boolean;

  // Slot/Token enumeration
  getSlotList(tokenPresent?: boolean): Promise<number[]>;
  getSlotInfo(slotIndex: number): Promise<SlotInfo>;
  getTokenInfo(slotIndex: number): Promise<TokenInfo>;
  waitForSlotEvent(timeout?: number): Promise<number | null>;

  // Session management
  openSession(slotIndex: number, config: SessionConfig): Promise<SessionHandle>;
  closeSession(sessionHandle: SessionHandle): Promise<void>;
  closeAllSessions(slotIndex: number): Promise<void>;
  login(sessionHandle: SessionHandle, userType: number, pin: string): Promise<void>;
  logout(sessionHandle: SessionHandle): Promise<void>;
  getSessionInfo(sessionHandle: SessionHandle): Promise<{ state: number; flags: number; deviceError: number }>;

  // Object management
  findObjects(
    sessionHandle: SessionHandle,
    template: FindObjectsTemplate,
    maxCount?: number
  ): Promise<any[]>;
  findObjectsInit(
    sessionHandle: SessionHandle,
    template: FindObjectsTemplate
  ): Promise<void>;
  findObjectsNext(sessionHandle: SessionHandle, maxCount: number): Promise<any[]>;
  findObjectsFinal(sessionHandle: SessionHandle): Promise<void>;
  getAttributeValue(sessionHandle: SessionHandle, objectHandle: any, attributes: number[]): Promise<AttributeMap>;
  getAttributeValueSingle(sessionHandle: SessionHandle, objectHandle: any, attribute: number): Promise<any>;

  // Key operations
  generateKeyPair(
    sessionHandle: SessionHandle,
    mechanism: Mechanism,
    publicKeyTemplate: AttributeMap,
    privateKeyTemplate: AttributeMap
  ): Promise<{ publicKey: any; privateKey: any }>;

  // Signing operations
  signInit(sessionHandle: SessionHandle, mechanism: Mechanism, keyHandle: any): Promise<void>;
  sign(sessionHandle: SessionHandle, data: Buffer): Promise<Buffer>;
  signUpdate(sessionHandle: SessionHandle, data: Buffer): Promise<void>;
  signFinal(sessionHandle: SessionHandle): Promise<Buffer>;
  signRecoverInit(sessionHandle: SessionHandle, mechanism: Mechanism, keyHandle: any): Promise<void>;
  signRecover(sessionHandle: SessionHandle, data: Buffer): Promise<Buffer>;

  // Verification operations
  verifyInit(sessionHandle: SessionHandle, mechanism: Mechanism, keyHandle: any): Promise<void>;
  verify(sessionHandle: SessionHandle, data: Buffer, signature: Buffer): Promise<boolean>;
  verifyUpdate(sessionHandle: SessionHandle, data: Buffer): Promise<void>;
  verifyFinal(sessionHandle: SessionHandle, signature: Buffer): Promise<boolean>;
  verifyRecoverInit(sessionHandle: SessionHandle, mechanism: Mechanism, keyHandle: any): Promise<void>;
  verifyRecover(sessionHandle: SessionHandle, signature: Buffer): Promise<Buffer>;

  // Digest operations
  digestInit(sessionHandle: SessionHandle, mechanism: Mechanism): Promise<void>;
  digest(sessionHandle: SessionHandle, data: Buffer): Promise<Buffer>;
  digestUpdate(sessionHandle: SessionHandle, data: Buffer): Promise<void>;
  digestKey(sessionHandle: SessionHandle, keyHandle: any): Promise<void>;
  digestFinal(sessionHandle: SessionHandle): Promise<Buffer>;

  // Mechanism support
  getMechanismList(slotIndex: number): Promise<number[]>;
  getMechanismInfo(slotIndex: number, mechanism: number): Promise<{
    minKeySize: number;
    maxKeySize: number;
    flags: number;
  }>;

  // Random generation
  seedRandom(sessionHandle: SessionHandle, seed: Buffer): Promise<void>;
  generateRandom(sessionHandle: SessionHandle, length: number): Promise<Buffer>;

  // Utility
  getFunctionList(): any;
}

export type AdapterFactory = (logger?: any) => Pkcs11Adapter;
```

### src/adapters/RealPkcs11Adapter.ts

```typescript
/**
 * Real PKCS#11 Adapter Implementation using pkcs11js
 */

import * as pkcs11js from 'pkcs11js';
import { Pkcs11Adapter, SessionHandle, FindObjectsTemplate, AttributeMap, Pkcs11LibraryInfo, Mechanism } from './Pkcs11Adapter';
import { CKK, CKO, CKF, CKR, CKU, MechanismType } from '../types';
import { Pkcs11Error, SessionError } from '../errors';
import pino from 'pino';

const logger = pino({ name: 'RealPkcs11Adapter' });

// PKCS#11 Attribute Constants
const CKA = {
  CLASS: 0x00000000,
  TOKEN: 0x00000001,
  PRIVATE: 0x00000002,
  LABEL: 0x00000003,
  APPLICATION: 0x00000010,
  VALUE: 0x00000011,
  OBJECT_ID: 0x00000012,
  CERTIFICATE_TYPE: 0x00000080,
  ISSUER: 0x00000081,
  SERIAL_NUMBER: 0x00000082,
  KEY_TYPE: 0x00000100,
  SUBJECT: 0x00000101,
  ID: 0x00000102,
  SENSITIVE: 0x00000103,
  ENCRYPT: 0x00000104,
  DECRYPT: 0x00000105,
  WRAP: 0x00000106,
  UNWRAP: 0x00000107,
  SIGN: 0x00000108,
  VERIFY: 0x00000109,
  DERIVE: 0x0000010A,
  START_DATE: 0x00000110,
  END_DATE: 0x00000111,
  MODULUS: 0x00000120,
  MODULUS_BITS: 0x00000121,
  PUBLIC_EXPONENT: 0x00000122,
  PRIVATE_EXPONENT: 0x00000123,
  PRIME_1: 0x00000124,
  PRIME_2: 0x00000125,
  EXPONENT_1: 0x00000126,
  EXPONENT_2: 0x00000127,
  COEFFICIENT: 0x00000128,
  PRIME: 0x00000130,
  SUBPRIME: 0x00000131,
  BASE: 0x00000132,
  PRIME_BITS: 0x00000133,
  SUBPRIME_BITS: 0x00000134,
  VALUE_BITS: 0x00000160,
  VALUE_LEN: 0x00000161,
  EXTRACTABLE: 0x00000162,
  LOCAL: 0x00000163,
  NEVER_EXTRACTABLE: 0x00000164,
  ALWAYS_SENSITIVE: 0x00000165,
  KEY_GEN_MECHANISM: 0x00000166,
  MODIFIABLE: 0x00000170,
  ECDSA_PARAMS: 0x00000180,
  EC_PARAMS: 0x00000180,
  EC_POINT: 0x00000181,
  ALWAYS_AUTHENTICATE: 0x00000202,
  WRAP_WITH_TRUSTED: 0x00000210,
  UNWRAP_TEMPLATE: 0x00000211,
  DERIVE_TEMPLATE: 0x00000212,
  OTP_FORMAT: 0x00000220,
  OTP_LENGTH: 0x00000221,
  OTP_TIME_INTERVAL: 0x00000222,
  OTP_USER_FRIENDLY_MODE: 0x00000223,
  OTP_CHALLENGE_REQUIREMENT: 0x00000224,
  OTP_TIME_REQUIREMENT: 0x00000225,
  OTP_COUNTER_REQUIREMENT: 0x00000226,
  OTP_PIN_REQUIREMENT: 0x00000227,
  OTP_COUNTER: 0x0000022E,
  OTP_TIME: 0x0000022F,
  USER_TYPE: 0x00000230,
  HW_FEATURE_TYPE: 0x00000231,
  RESET_ON_INIT: 0x00000232,
  HAS_RESET: 0x00000233,
  PIXEL_X: 0x00000240,
  PIXEL_Y: 0x00000241,
  RESOLUTION: 0x00000242,
  CHAR_ROWS: 0x00000243,
  CHAR_COLUMNS: 0x00000244,
  COLOR: 0x00000245,
  BITS_PER_PIXEL: 0x00000246,
  CHAR_SETS: 0x00000247,
  ENCODING_METHODS: 0x00000248,
  MIME_TYPES: 0x00000249,
  MECHANISM_TYPE: 0x00000250,
  REQUIRED_CMS_ATTRIBUTES: 0x00000251,
  DEFAULT_CMS_ATTRIBUTES: 0x00000252,
  SUPPORTED_CMS_ATTRIBUTES: 0x00000253,
  ALLOWED_MECHANISMS: 0x00000600,
};

export class RealPkcs11Adapter implements Pkcs11Adapter {
  private pkcs11: pkcs11js.PKCS11;
  private initialized = false;
  private libPath: string = '';

  constructor(private readonly log = logger) {}

  async initialize(libraryPath: string): Promise<void> {
    if (this.initialized) {
      this.log.warn('PKCS#11 library already initialized');
      return;
    }

    this.libPath = libraryPath;
    this.pkcs11 = new pkcs11js.PKCS11();

    try {
      this.pkcs11.load(libraryPath);
      this.pkcs11.C_Initialize();
      this.initialized = true;
      this.log.info({ libraryPath }, 'PKCS#11 library initialized');
    } catch (error) {
      this.log.error({ err: error, libraryPath }, 'Failed to initialize PKCS#11 library');
      throw new Pkcs11Error(
        `Failed to load PKCS#11 library: ${error instanceof Error ? error.message : String(error)}`,
        CKR.LIBRARY_LOAD_FAILED
      );
    }
  }

  async finalize(): Promise<void> {
    if (!this.initialized) return;

    try {
      this.pkcs11.C_Finalize();
      this.initialized = false;
      this.log.info('PKCS#11 library finalized');
    } catch (error) {
      this.log.error({ err: error }, 'Error finalizing PKCS#11 library');
      throw new Pkcs11Error(
        `Failed to finalize PKCS#11 library: ${error instanceof Error ? error.message : String(error)}`,
        CKR.GENERAL_ERROR
      );
    }
  }

  isInitialized(): boolean {
    return this.initialized;
  }

  async getLibraryInfo(): Promise<Pkcs11LibraryInfo> {
    this.ensureInitialized();
    try {
      const info = this.pkcs11.C_GetInfo();
      return {
        manufacturerId: info.manufacturerID.trim(),
        libraryDescription: info.libraryDescription.trim(),
        libraryVersion: { major: info.libraryVersion.major, minor: info.libraryVersion.minor },
        cryptokiVersion: { major: info.cryptokiVersion.major, minor: info.cryptokiVersion.minor },
      };
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        'C_GetInfo'
      );
    }
  }

  async getSlotList(tokenPresent = false): Promise<number[]> {
    this.ensureInitialized();
    try {
      return this.pkcs11.C_GetSlotList(tokenPresent);
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        'C_GetSlotList'
      );
    }
  }

  async getSlotInfo(slotIndex: number): Promise<SlotInfo> {
    this.ensureInitialized();
    try {
      const info = this.pkcs11.C_GetSlotInfo(slotIndex);
      return {
        slotIndex,
        slotDescription: info.slotDescription.trim(),
        manufacturerId: info.manufacturerID.trim(),
        hardwareVersion: { major: info.hardwareVersion.major, minor: info.hardwareVersion.minor },
        firmwareVersion: { major: info.firmwareVersion.major, minor: info.firmwareVersion.minor },
        tokenPresent: info.flags & 0x00000001,
      };
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        `C_GetSlotInfo(slot=${slotIndex})`
      );
    }
  }

  async getTokenInfo(slotIndex: number): Promise<TokenInfo> {
    this.ensureInitialized();
    try {
      const info = this.pkcs11.C_GetTokenInfo(slotIndex);
      return {
        label: info.label.trim(),
        manufacturerId: info.manufacturerID.trim(),
        model: info.model.trim(),
        serialNumber: info.serialNumber.trim(),
        flags: info.flags,
        maxSessionCount: info.maxSessionCount,
        sessionCount: info.sessionCount,
        maxRwSessionCount: info.maxRwSessionCount,
        rwSessionCount: info.rwSessionCount,
        maxPinLen: info.maxPinLen,
        minPinLen: info.minPinLen,
        totalPublicMemory: info.totalPublicMemory,
        freePublicMemory: info.freePublicMemory,
        totalPrivateMemory: info.totalPrivateMemory,
        freePrivateMemory: info.freePrivateMemory,
        hardwareVersion: { major: info.hardwareVersion.major, minor: info.hardwareVersion.minor },
        firmwareVersion: { major: info.firmwareVersion.major, minor: info.firmwareVersion.minor },
        utcTime: info.utcTime?.trim() || '',
      };
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        `C_GetTokenInfo(slot=${slotIndex})`
      );
    }
  }

  async waitForSlotEvent(timeout = 0): Promise<number | null> {
    this.ensureInitialized();
    try {
      const slot = this.pkcs11.C_WaitForSlotEvent(timeout > 0 ? pkcs11js.CKF_DONT_BLOCK : 0, null, timeout);
      return slot ?? null;
    } catch (error) {
      const code = (error as any).code || CKR.GENERAL_ERROR;
      if (code === CKR.NO_EVENT) return null;
      throw Pkcs11Error.fromReturnCode(code, 'C_WaitForSlotEvent');
    }
  }

  async openSession(slotIndex: number, config: SessionConfig): Promise<SessionHandle> {
    this.ensureInitialized();
    try {
      const flags = (config.readOnly ? 0 : CKF.RW_SESSION) | (config.serialSession ? CKF.SERIAL_SESSION : 0);
      const handle = this.pkcs11.C_OpenSession(slotIndex, flags);
      return {
        handle,
        slotIndex,
        readOnly: config.readOnly,
        createdAt: Date.now(),
        inUse: false,
      };
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        `C_OpenSession(slot=${slotIndex})`
      );
    }
  }

  async closeSession(sessionHandle: SessionHandle): Promise<void> {
    this.ensureInitialized();
    try {
      this.pkcs11.C_CloseSession(sessionHandle.handle);
      sessionHandle.inUse = false;
    } catch (error) {
      throw new SessionError(
        `Failed to close session: ${error instanceof Error ? error.message : String(error)}`,
        'C_CloseSession',
        sessionHandle.handle
      );
    }
  }

  async closeAllSessions(slotIndex: number): Promise<void> {
    this.ensureInitialized();
    try {
      this.pkcs11.C_CloseAllSessions(slotIndex);
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        `C_CloseAllSessions(slot=${slotIndex})`
      );
    }
  }

  async login(sessionHandle: SessionHandle, userType: number, pin: string): Promise<void> {
    this.ensureInitialized();
    try {
      this.pkcs11.C_Login(sessionHandle.handle, userType, pin);
      this.log.debug({ slotIndex: sessionHandle.slotIndex, userType }, 'Login successful');
    } catch (error) {
      const code = (error as any).code || CKR.GENERAL_ERROR;
      if (code === CKR.USER_ALREADY_LOGGED_IN) {
        this.log.debug('User already logged in');
        return;
      }
      throw Pkcs11Error.fromReturnCode(code, `C_Login(userType=${userType})`);
    }
  }

  async logout(sessionHandle: SessionHandle): Promise<void> {
    this.ensureInitialized();
    try {
      this.pkcs11.C_Logout(sessionHandle.handle);
      this.log.debug({ slotIndex: sessionHandle.slotIndex }, 'Logout successful');
    } catch (error) {
      const code = (error as any).code || CKR.GENERAL_ERROR;
      if (code === CKR.USER_NOT_LOGGED_IN) {
        this.log.debug('User not logged in');
        return;
      }
      throw Pkcs11Error.fromReturnCode(code, 'C_Logout');
    }
  }

  async getSessionInfo(sessionHandle: SessionHandle): Promise<{ state: number; flags: number; deviceError: number }> {
    this.ensureInitialized();
    try {
      const info = this.pkcs11.C_GetSessionInfo(sessionHandle.handle);
      return {
        state: info.state,
        flags: info.flags,
        deviceError: info.deviceError,
      };
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        `C_GetSessionInfo(handle=${sessionHandle.handle})`
      );
    }
  }

  async findObjects(
    sessionHandle: SessionHandle,
    template: FindObjectsTemplate,
    maxCount = 10
  ): Promise<any[]> {
    this.ensureInitialized();
    try {
      const pkcs11Template = this.buildFindTemplate(template);
      this.pkcs11.C_FindObjectsInit(sessionHandle.handle, pkcs11Template);
      const objects = this.pkcs11.C_FindObjects(sessionHandle.handle, maxCount);
      this.pkcs11.C_FindObjectsFinal(sessionHandle.handle);
      return objects;
    } catch (error) {
      try {
        this.pkcs11.C_FindObjectsFinal(sessionHandle.handle);
      } catch {}
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        'C_FindObjects'
      );
    }
  }

  async findObjectsInit(sessionHandle: SessionHandle, template: FindObjectsTemplate): Promise<void> {
    this.ensureInitialized();
    try {
      const pkcs11Template = this.buildFindTemplate(template);
      this.pkcs11.C_FindObjectsInit(sessionHandle.handle, pkcs11Template);
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        'C_FindObjectsInit'
      );
    }
  }

  async findObjectsNext(sessionHandle: SessionHandle, maxCount: number): Promise<any[]> {
    this.ensureInitialized();
    try {
      return this.pkcs11.C_FindObjects(sessionHandle.handle, maxCount);
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        'C_FindObjectsNext'
      );
    }
  }

  async findObjectsFinal(sessionHandle: SessionHandle): Promise<void> {
    this.ensureInitialized();
    try {
      this.pkcs11.C_FindObjectsFinal(sessionHandle.handle);
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        'C_FindObjectsFinal'
      );
    }
  }

  async getAttributeValue(
    sessionHandle: SessionHandle,
    objectHandle: any,
    attributes: number[]
  ): Promise<AttributeMap> {
    this.ensureInitialized();
    try {
      const attrTemplate = attributes.map(attr => ({ type: attr }));
      const result = this.pkcs11.C_GetAttributeValue(sessionHandle.handle, objectHandle, attrTemplate);
      const map: AttributeMap = {};
      for (const attr of result) {
        map[attr.type] = attr.value;
      }
      return map;
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        'C_GetAttributeValue'
      );
    }
  }

  async getAttributeValueSingle(
    sessionHandle: SessionHandle,
    objectHandle: any,
    attribute: number
  ): Promise<any> {
    const result = await this.getAttributeValue(sessionHandle, objectHandle, [attribute]);
    return result[attribute];
  }

  async generateKeyPair(
    sessionHandle: SessionHandle,
    mechanism: Mechanism,
    publicKeyTemplate: AttributeMap,
    privateKeyTemplate: AttributeMap
  ): Promise<{ publicKey: any; privateKey: any }> {
    this.ensureInitialized();
    try {
      const mech = this.buildMechanism(mechanism);
      const pubTemplate = this.buildAttributeTemplate(publicKeyTemplate);
      const privTemplate = this.buildAttributeTemplate(privateKeyTemplate);
      const keys = this.pkcs11.C_GenerateKeyPair(sessionHandle.handle, mech, pubTemplate, privTemplate);
      return { publicKey: keys.publicKey, privateKey: keys.privateKey };
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        'C_GenerateKeyPair'
      );
    }
  }

  async signInit(sessionHandle: SessionHandle, mechanism: Mechanism, keyHandle: any): Promise<void> {
    this.ensureInitialized();
    try {
      const mech = this.buildMechanism(mechanism);
      this.pkcs11.C_SignInit(sessionHandle.handle, mech, keyHandle);
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        'C_SignInit'
      );
    }
  }

  async sign(sessionHandle: SessionHandle, data: Buffer): Promise<Buffer> {
    this.ensureInitialized();
    try {
      const signature = this.pkcs11.C_Sign(sessionHandle.handle, data);
      return Buffer.from(signature);
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        'C_Sign'
      );
    }
  }

  async signUpdate(sessionHandle: SessionHandle, data: Buffer): Promise<void> {
    this.ensureInitialized();
    try {
      this.pkcs11.C_SignUpdate(sessionHandle.handle, data);
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        'C_SignUpdate'
      );
    }
  }

  async signFinal(sessionHandle: SessionHandle): Promise<Buffer> {
    this.ensureInitialized();
    try {
      const signature = this.pkcs11.C_SignFinal(sessionHandle.handle);
      return Buffer.from(signature);
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        'C_SignFinal'
      );
    }
  }

  async signRecoverInit(sessionHandle: SessionHandle, mechanism: Mechanism, keyHandle: any): Promise<void> {
    this.ensureInitialized();
    try {
      const mech = this.buildMechanism(mechanism);
      this.pkcs11.C_SignRecoverInit(sessionHandle.handle, mech, keyHandle);
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        'C_SignRecoverInit'
      );
    }
  }

  async signRecover(sessionHandle: SessionHandle, data: Buffer): Promise<Buffer> {
    this.ensureInitialized();
    try {
      const result = this.pkcs11.C_SignRecover(sessionHandle.handle, data);
      return Buffer.from(result);
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        'C_SignRecover'
      );
    }
  }

  async verifyInit(sessionHandle: SessionHandle, mechanism: Mechanism, keyHandle: any): Promise<void> {
    this.ensureInitialized();
    try {
      const mech = this.buildMechanism(mechanism);
      this.pkcs11.C_VerifyInit(sessionHandle.handle, mech, keyHandle);
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        'C_VerifyInit'
      );
    }
  }

  async verify(sessionHandle: SessionHandle, data: Buffer, signature: Buffer): Promise<boolean> {
    this.ensureInitialized();
    try {
      return this.pkcs11.C_Verify(sessionHandle.handle, data, signature);
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        'C_Verify'
      );
    }
  }

  async verifyUpdate(sessionHandle: SessionHandle, data: Buffer): Promise<void> {
    this.ensureInitialized();
    try {
      this.pkcs11.C_VerifyUpdate(sessionHandle.handle, data);
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        'C_VerifyUpdate'
      );
    }
  }

  async verifyFinal(sessionHandle: SessionHandle, signature: Buffer): Promise<boolean> {
    this.ensureInitialized();
    try {
      return this.pkcs11.C_VerifyFinal(sessionHandle.handle, signature);
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        'C_VerifyFinal'
      );
    }
  }

  async verifyRecoverInit(sessionHandle: SessionHandle, mechanism: Mechanism, keyHandle: any): Promise<void> {
    this.ensureInitialized();
    try {
      const mech = this.buildMechanism(mechanism);
      this.pkcs11.C_VerifyRecoverInit(sessionHandle.handle, mech, keyHandle);
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        'C_VerifyRecoverInit'
      );
    }
  }

  async verifyRecover(sessionHandle: SessionHandle, signature: Buffer): Promise<Buffer> {
    this.ensureInitialized();
    try {
      const result = this.pkcs11.C_VerifyRecover(sessionHandle.handle, signature);
      return Buffer.from(result);
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        'C_VerifyRecover'
      );
    }
  }

  async digestInit(sessionHandle: SessionHandle, mechanism: Mechanism): Promise<void> {
    this.ensureInitialized();
    try {
      const mech = this.buildMechanism(mechanism);
      this.pkcs11.C_DigestInit(sessionHandle.handle, mech);
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        'C_DigestInit'
      );
    }
  }

  async digest(sessionHandle: SessionHandle, data: Buffer): Promise<Buffer> {
    this.ensureInitialized();
    try {
      const result = this.pkcs11.C_Digest(sessionHandle.handle, data);
      return Buffer.from(result);
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        'C_Digest'
      );
    }
  }

  async digestUpdate(sessionHandle: SessionHandle, data: Buffer): Promise<void> {
    this.ensureInitialized();
    try {
      this.pkcs11.C_DigestUpdate(sessionHandle.handle, data);
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        'C_DigestUpdate'
      );
    }
  }

  async digestKey(sessionHandle: SessionHandle, keyHandle: any): Promise<void> {
    this.ensureInitialized();
    try {
      this.pkcs11.C_DigestKey(sessionHandle.handle, keyHandle);
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        'C_DigestKey'
      );
    }
  }

  async digestFinal(sessionHandle: SessionHandle): Promise<Buffer> {
    this.ensureInitialized();
    try {
      const result = this.pkcs11.C_DigestFinal(sessionHandle.handle);
      return Buffer.from(result);
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        'C_DigestFinal'
      );
    }
  }

  async getMechanismList(slotIndex: number): Promise<number[]> {
    this.ensureInitialized();
    try {
      return this.pkcs11.C_GetMechanismList(slotIndex);
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        `C_GetMechanismList(slot=${slotIndex})`
      );
    }
  }

  async getMechanismInfo(slotIndex: number, mechanism: number): Promise<{
    minKeySize: number;
    maxKeySize: number;
    flags: number;
  }> {
    this.ensureInitialized();
    try {
      const info = this.pkcs11.C_GetMechanismInfo(slotIndex, mechanism);
      return {
        minKeySize: info.minKeySize,
        maxKeySize: info.maxKeySize,
        flags: info.flags,
      };
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        `C_GetMechanismInfo(slot=${slotIndex}, mech=0x${mechanism.toString(16)})`
      );
    }
  }

  async seedRandom(sessionHandle: SessionHandle, seed: Buffer): Promise<void> {
    this.ensureInitialized();
    try {
      this.pkcs11.C_SeedRandom(sessionHandle.handle, seed);
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        'C_SeedRandom'
      );
    }
  }

  async generateRandom(sessionHandle: SessionHandle, length: number): Promise<Buffer> {
    this.ensureInitialized();
    try {
      const result = this.pkcs11.C_GenerateRandom(sessionHandle.handle, length);
      return Buffer.from(result);
    } catch (error) {
      throw Pkcs11Error.fromReturnCode(
        (error as any).code || CKR.GENERAL_ERROR,
        'C_GenerateRandom'
      );
    }
  }

  getFunctionList(): any {
    this.ensureInitialized();
    return this.pkcs11;
  }

  private ensureInitialized(): void {
    if (!this.initialized || !this.pkcs11) {
      throw new Pkcs11Error('PKCS#11 library not initialized', CKR.CRYPTOKI_NOT_INITIALIZED);
    }
  }

  private buildFindTemplate(template: FindObjectsTemplate): any[] {
    const result: any[] = [];
    
    if (template.class !== undefined) {
      result.push({ type: CKA.CLASS, value: template.class });
    }
    if (template.keyType !== undefined) {
      result.push({ type: CKA.KEY_TYPE, value: template.keyType });
    }
    if (template.label !== undefined) {
      result.push({ type: CKA.LABEL, value: template.label });
    }
    if (template.id !== undefined) {
      result.push({ type: CKA.ID, value: template.id });
    }
    if (template.token !== undefined) {
      result.push({ type: CKA.TOKEN, value: template.token });
    }
    if (template.private !== undefined) {
      result.push({ type: CKA.PRIVATE, value: template.private });
    }
    if (template.sign !== undefined) {
      result.push({ type: CKA.SIGN, value: template.sign });
    }
    if (template.verify !== undefined) {
      result.push({ type: CKA.VERIFY, value: template.verify });
    }
    
    return result;
  }

  private buildAttributeTemplate(template: AttributeMap): any[] {
    return Object.entries(template).map(([key, value]) => ({
      type: parseInt(key, 10),
      value,
    }));
  }

  private buildMechanism(mechanism: Mechanism): any {
    const mech: any = { mechanism: mechanism.mechanism };
    if (mechanism.parameter) {
      mech.parameter = mechanism.parameter;
    }
    return mech;
  }
}
```

### src/adapters/MockPkcs11Adapter.ts

```typescript
/**
 * Mock PKCS#11 Adapter for Testing Without Hardware
 */

import {
  Pkcs11Adapter,
  SessionHandle,
  FindObjectsTemplate,
  AttributeMap,
  Pkcs11LibraryInfo,
  Mechanism,
} from './Pkcs11Adapter';
import { CKK, CKO, CKF, CKR, CKU, MechanismType } from '../types';
import { Pkcs11Error, KeyNotFoundError, MechanismMismatchError } from '../errors';
import pino from 'pino';

const logger = pino({ name: 'MockPkcs11Adapter' });

// Mock data store
interface MockObject {
  handle: string;
  attributes: AttributeMap;
}

interface MockSlot {
  index: number;
  tokenPresent: boolean;
  tokenInfo?: TokenInfo;
  objects: Map<string, MockObject>;
  sessions: Map<string, MockSession>;
}

interface MockSession {
  handle: string;
  slotIndex: number;
  readOnly: boolean;
  loggedIn: boolean;
  userType: number;
  signInit?: { mechanism: Mechanism; keyHandle: string };
  verifyInit?: { mechanism: Mechanism; keyHandle: string };
  digestInit?: Mechanism;
  findObjectsInit?: FindObjectsTemplate;
}

interface TokenInfo {
  label: string;
  manufacturerId: string;
  model: string;
  serialNumber: string;
  flags: number;
  maxSessionCount: number;
  sessionCount: number;
  maxRwSessionCount: number;
  rwSessionCount: number;
  maxPinLen: number;
  minPinLen: number;
  totalPublicMemory: number;
  freePublicMemory: number;
  totalPrivateMemory: number;
  freePrivateMemory: number;
  hardwareVersion: { major: number; minor: number };
  firmwareVersion: { major: number; minor: number };
  utcTime: string;
}

export class MockPkcs11Adapter implements Pkcs11Adapter {
  private initialized = false;
  private slots: Map<number, MockSlot> = new Map();
  private sessionCounter = 0;
  private objectCounter = 0;
  private defaultPin = '1234';
  private defaultSoPin = '5678';

  constructor(private readonly log = logger) {
    this.setupDefaultSlot();
  }

  private setupDefaultSlot(): void {
    const slot: MockSlot = {
      index: 0,
      tokenPresent: true,
      tokenInfo: {
        label: 'mock-token',
        manufacturerId: 'Mock HSM',
        model: 'Mock HSM v1.0',
        serialNumber: 'MOCK123456',
        flags: 0x0000000F, // RNG, LOGIN_REQUIRED, USER_PIN_INITIALIZED, TOKEN_INITIALIZED
        maxSessionCount: 10,
        sessionCount: 0,
        maxRwSessionCount: 10,
        rwSessionCount: 0,
        maxPinLen: 255,
        minPinLen: 4,
        totalPublicMemory: 1024 * 1024,
        freePublicMemory: 512 * 1024,
        totalPrivateMemory: 1024 * 1024,
        freePrivateMemory: 512 * 1024,
        hardwareVersion: { major: 1, minor: 0 },
        firmwareVersion: { major: 1, minor: 0 },
        utcTime: new Date().toISOString().replace(/[-:]/g, '').split('.')[0] + '00',
      },
      objects: new Map(),
      sessions: new Map(),
    };

    // Add a default RSA key pair
    this.addMockKeyPair(slot, 'signing-key', Buffer.from('01020304'), CKK.RSA, 2048);
    // Add a default EC key pair
    this.addMockKeyPair(slot, 'ec-signing-key', Buffer.from('05060708'), CKK.EC, 256);

    this.slots.set(0, slot);
  }

  private addMockKeyPair(
    slot: MockSlot,
    label: string,
    id: Buffer,
    keyType: CKK,
    keySize: number
  ): void {
    const privHandle = `priv_${++this.objectCounter}`;
    const pubHandle = `pub_${++this.objectCounter}`;

    const pubKeyAttrs: AttributeMap = {
      0x00000000: CKO.PUBLIC_KEY, // CKA_CLASS
      0x00000100: keyType, // CKA_KEY_TYPE
      0x00000003: label, // CKA_LABEL
      0x00000102: id, // CKA_ID
      0x00000001: true, // CKA_TOKEN
      0x00000108: false, // CKA_SIGN
      0x00000109: true, // CKA_VERIFY
      0x00000104: true, // CKA_ENCRYPT
      0x00000105: false, // CKA_DECRYPT
      0x00000106: true, // CKA_WRAP
      0x00000107: false, // CKA_UNWRAP
      0x0000010A: false, // CKA_DERIVE
      0x00000162: true, // CKA_EXTRACTABLE
      0x00000121: keySize, // CKA_MODULUS_BITS (RSA) or CKA_PRIME_BITS (EC)
    };

    const privKeyAttrs: AttributeMap = {
      0x00000000: CKO.PRIVATE_KEY, // CKA_CLASS
      0x00000100: keyType, // CKA_KEY_TYPE
      0x00000003: label, // CKA_LABEL
      0x00000102: id, // CKA_ID
      0x00000001: true, // CKA_TOKEN
      0x00000002: true, // CKA_PRIVATE
      0x00000103: true, // CKA_SENSITIVE
      0x00000108: true, // CKA_SIGN
      0x00000109: false, // CKA_VERIFY
      0x00000104: false, // CKA_ENCRYPT
      0x00000105: true, // CKA_DECRYPT
      0x00000106: false, // CKA_WRAP
      0x00000107: true, // CKA_UNWRAP
      0x0000010A: false, // CKA_DERIVE
      0x00000162: false, // CKA_EXTRACTABLE
      0x00000164: true, // CKA_NEVER_EXTRACTABLE
      0x00000165: true, // CKA_ALWAYS_SENSITIVE
      0x00000121: keySize, // CKA_MODULUS_BITS / CKA_PRIME_BITS
    };

    // Add mock key material
    if (keyType === CKK.RSA) {
      pubKeyAttrs[0x00000120] = Buffer.from('mock-modulus'); // CKA_MODULUS
      pubKeyAttrs[0x00000122] = Buffer.from([0x01, 0x00, 0x01]); // CKA_PUBLIC_EXPONENT (65537)
      privKeyAttrs[0x00000123] = Buffer.from('mock-private-exponent'); // CKA_PRIVATE_EXPONENT
    } else {
      pubKeyAttrs[0x00000181] = Buffer.from('mock-ec-point'); // CKA_EC_POINT
      pubKeyAttrs[0x00000180] = Buffer.from('mock-ec-params'); // CKA_EC_PARAMS
      privKeyAttrs[0x00000181] = Buffer.from('mock-ec-private'); // CKA_VALUE for EC private
    }

    slot.objects.set(privHandle, { handle: privHandle, attributes: privKeyAttrs });
    slot.objects.set(pubHandle, { handle: pubHandle, attributes: pubKeyAttrs });
  }

  // Library lifecycle
  async initialize(libraryPath: string): Promise<void> {
    if (this.initialized) return;
    this.initialized = true;
    this.log.info({ libraryPath }, 'Mock PKCS#11 library initialized');
  }

  async finalize(): Promise<void> {
    if (!this.initialized) return;
    // Close all sessions
    for (const slot of this.slots.values()) {
      for (const session of slot.sessions.values()) {
        session.loggedIn = false;
      }
      slot.sessions.clear();
    }
    this.initialized = false;
    this.log.info('Mock PKCS#11 library finalized');
  }

  isInitialized(): boolean {
    return this.initialized;
  }

  async getLibraryInfo(): Promise<Pkcs11LibraryInfo> {
    this.ensureInitialized();
    return {
      manufacturerId: 'Mock HSM Vendor',
      libraryDescription: 'Mock PKCS#11 Library for Testing',
      libraryVersion: { major: 1, minor: 0 },
      cryptokiVersion: { major: 2, minor: 40 },
    };
  }

  // Slot/Token enumeration
  async getSlotList(tokenPresent = false): Promise<number[]> {
    this.ensureInitialized();
    const slots: number[] = [];
    for (const [index, slot] of this.slots) {
      if (!tokenPresent || slot.tokenPresent) {
        slots.push(index);
      }
    }
    return slots;
  }

  async getSlotInfo(slotIndex: number): Promise<any> {
    this.ensureInitialized();
    const slot = this.slots.get(slotIndex);
    if (!slot) {
      throw new Pkcs11Error('Slot not found', CKR.SLOT_ID_INVALID);
    }
    return {
      slotIndex,
      slotDescription: `Mock Slot ${slotIndex}`,
      manufacturerId: 'Mock HSM Vendor',
      hardwareVersion: { major: 1, minor: 0 },
      firmwareVersion: { major: 1, minor: 0 },
      tokenPresent: slot.tokenPresent,
    };
  }

  async getTokenInfo(slotIndex: number): Promise<TokenInfo> {
    this.ensureInitialized();
    const slot = this.slots.get(slotIndex);
    if (!slot || !slot.tokenInfo) {
      throw new Pkcs11Error('Token not present', CKR.TOKEN_NOT_PRESENT);
    }
    return slot.tokenInfo;
  }

  async waitForSlotEvent(timeout = 0): Promise<number | null> {
    this.ensureInitialized();
    // Mock: return null immediately (no events)
    return null;
  }

  // Session management
  async openSession(slotIndex: number, config: { readOnly: boolean; serialSession: boolean }): Promise<SessionHandle> {
    this.ensureInitialized();
    const slot = this.slots.get(slotIndex);
    if (!slot) {
      throw new Pkcs11Error('Slot not found', CKR.SLOT_ID_INVALID);
    }
    if (!slot.tokenPresent) {
      throw new Pkcs11Error('Token not present', CKR.TOKEN_NOT_PRESENT);
    }

    const handle = `session_${++this.sessionCounter}`;
    const session: MockSession = {
      handle,
      slotIndex,
      readOnly: config.readOnly,
      loggedIn: false,
      userType: CKU.USER,
    };
    slot.sessions.set(handle, session);
    slot.tokenInfo!.sessionCount++;

    return {
      handle,
      slotIndex,
      readOnly: config.readOnly,
      createdAt: Date.now(),
      inUse: false,
    };
  }

  async closeSession(sessionHandle: SessionHandle): Promise<void> {
    this.ensureInitialized();
    const slot = this.slots.get(sessionHandle.slotIndex);
    if (slot) {
      slot.sessions.delete(sessionHandle.handle);
      if (slot.tokenInfo) slot.tokenInfo.sessionCount--;
    }
  }

  async closeAllSessions(slotIndex: number): Promise<void> {
    this.ensureInitialized();
    const slot = this.slots.get(slotIndex);
    if (slot) {
      slot.sessions.clear();
      if (slot.tokenInfo) slot.tokenInfo.sessionCount = 0;
    }
  }

  async login(sessionHandle: SessionHandle, userType: number, pin: string): Promise<void> {
    this.ensureInitialized();
    const slot = this.slots.get(sessionHandle.slotIndex);
    if (!slot) throw new Pkcs11Error('Slot not found', CKR.SLOT_ID_INVALID);
    
    const session = slot.sessions.get(sessionHandle.handle);
    if (!session) throw new Pkcs11Error('Session not found', CKR.SESSION_HANDLE_INVALID);

    const expectedPin = userType === CKU.SO ? this.defaultSoPin : this.defaultPin;
    if (pin !== expectedPin) {
      throw new Pkcs11Error('Incorrect PIN', CKR.PIN_INCORRECT);
    }

    session.loggedIn = true;
    session.userType = userType;
  }

  async logout(sessionHandle: SessionHandle): Promise<void> {
    this.ensureInitialized();
    const slot = this.slots.get(sessionHandle.slotIndex);
    if (!slot) throw new Pkcs11Error('Slot not found', CKR.SLOT_ID_INVALID);
    
    const session = slot.sessions.get(sessionHandle.handle);
    if (!session) throw new Pkcs11Error('Session not found', CKR.SESSION_HANDLE_INVALID);

    session.loggedIn = false;
  }

  async getSessionInfo(sessionHandle: SessionHandle): Promise<{ state: number; flags: number; deviceError: number }> {
    this.ensureInitialized();
    const slot = this.slots.get(sessionHandle.slotIndex);
    if (!slot) throw new Pkcs11Error('Slot not found', CKR.SLOT_ID_INVALID);
    
    const session = slot.sessions.get(sessionHandle.handle);
    if (!session) throw new Pkcs11Error('Session not found', CKR.SESSION_HANDLE_INVALID);

    return {
      state: session.loggedIn ? 1 : 0, // CKS_RO_USER_FUNCTIONS : CKS_RO_PUBLIC_SESSION
      flags: session.readOnly ? 0 : CKF.RW_SESSION,
      deviceError: 0,
    };
  }

  // Object management
  async findObjects(
    sessionHandle: SessionHandle,
    template: FindObjectsTemplate,
    maxCount = 10
  ): Promise<any[]> {
    this.ensureInitialized();
    const slot = this.slots.get(sessionHandle.slotIndex);
    if (!slot) throw new Pkcs11Error('Slot not found', CKR.SLOT_ID_INVALID);
    
    const session = slot.sessions.get(sessionHandle.handle);
    if (!session) throw new Pkcs11Error('Session not found', CKR.SESSION_HANDLE_INVALID);

    const results: any[] = [];
    for (const obj of slot.objects.values()) {
      if (this.matchesTemplate(obj.attributes, template)) {
        results.push(obj.handle);
        if (results.length >= maxCount) break;
      }
    }
    return results;
  }

  async findObjectsInit(sessionHandle: SessionHandle, template: FindObjectsTemplate): Promise<void> {
    this.ensureInitialized();
    const slot = this.slots.get(sessionHandle.slotIndex);
    if (!slot) throw new Pkcs11Error('Slot not found', CKR.SLOT_ID_INVALID);
    
    const session = slot.sessions.get(sessionHandle.handle);
    if (!session) throw new Pkcs11Error('Session not found', CKR.SESSION_HANDLE_INVALID);

    session.findObjectsInit = template;
  }

  async findObjectsNext(sessionHandle: SessionHandle, maxCount: number): Promise<any[]> {
    this.ensureInitialized();
    const slot = this.slots.get(sessionHandle.slotIndex);
    if (!slot) throw new Pkcs11Error('Slot not found', CKR.SLOT_ID_INVALID);
    
    const session = slot.sessions.get(sessionHandle.handle);
    if (!session || !session.findObjectsInit) {
      throw new Pkcs11Error('Find objects not initialized', CKR.OPERATION_NOT_INITIALIZED);
    }

    const results: any[] = [];
    for (const obj of slot.objects.values()) {
      if (this.matchesTemplate(obj.attributes, session.findObjectsInit)) {
        results.push(obj.handle);
        if (results.length >= maxCount) break;
      }
    }
    return results;
  }

  async findObjectsFinal(sessionHandle: SessionHandle): Promise<void> {
    this.ensureInitialized();
    const slot = this.slots.get(sessionHandle.slotIndex);
    if (!slot) throw new Pkcs11Error('Slot not found', CKR.SLOT_ID_INVALID);
    
    const session = slot.sessions.get(sessionHandle.handle);
    if (session) {
      session.findObjectsInit = undefined;
    }
  }

  async getAttributeValue(
    sessionHandle: SessionHandle,
    objectHandle: any,
    attributes: number[]
  ): Promise<AttributeMap> {
    this.ensureInitialized();
    const slot = this.slots.get(sessionHandle.slotIndex);
    if (!slot) throw new Pkcs11Error('Slot not found', CKR.SLOT_ID_INVALID);
    
    const obj = slot.objects.get(objectHandle);
    if (!obj) throw new Pkcs11Error('Object not found', CKR.OBJECT_HANDLE_INVALID);

    const result: AttributeMap = {};
    for (const attr of attributes) {
      if (obj.attributes[attr] !== undefined) {
        result[attr] = obj.attributes[attr];
      }
    }
    return result;
  }

  async getAttributeValueSingle(
    sessionHandle: SessionHandle,
    objectHandle: any,
    attribute: number
  ): Promise<any> {
    const result = await this.getAttributeValue(sessionHandle, objectHandle, [attribute]);
    return result[attribute];
  }

  async generateKeyPair(
    sessionHandle: SessionHandle,
    mechanism: Mechanism,
    publicKeyTemplate: AttributeMap,
    privateKeyTemplate: AttributeMap
  ): Promise<{ publicKey: any; privateKey: any }> {
    this.ensureInitialized();
    const slot = this.slots.get(sessionHandle.slotIndex);
    if (!slot) throw new Pkcs11Error('Slot not found', CKR.SLOT_ID_INVALID);

    const label = publicKeyTemplate[0x00000003] || `key-${Date.now()}`;
    const id = publicKeyTemplate[0x00000102] || Buffer.from([++this.objectCounter]);
    const keyType = publicKeyTemplate[0x00000100] || CKK.RSA;
    const keySize = publicKeyTemplate[0x00000121] || 2048;

    this.addMockKeyPair(slot, label, id, keyType, keySize);

    // Return the newly created key handles
    const newKeys = Array.from(slot.objects.entries()).slice(-2);
    return { publicKey: newKeys[1][0], privateKey: newKeys[0][0] };
  }

  // Signing operations
  async signInit(sessionHandle: SessionHandle, mechanism: Mechanism, keyHandle: any): Promise<void> {
    this.ensureInitialized();
    const slot = this.slots.get(sessionHandle.slotIndex);
    if (!slot) throw new Pkcs11Error('Slot not found', CKR.SLOT_ID_INVALID);
    
    const session = slot.sessions.get(sessionHandle.handle);
    if (!session) throw new Pkcs11Error('Session not found', CKR.SESSION_HANDLE_INVALID);
    if (!session.loggedIn) throw new Pkcs11Error('User not logged in', CKR.USER_NOT_LOGGED_IN);

    const obj = slot.objects.get(keyHandle);
    if (!obj) throw new Pkcs11Error('Key not found', CKR.KEY_HANDLE_INVALID);
    if (obj.attributes[0x00000000] !== CKO.PRIVATE_KEY) {
      throw new Pkcs11Error('Key is not a private key', CKR.KEY_TYPE_INCONSISTENT);
    }
    if (!obj.attributes[0x00000108]) {
      throw new Pkcs11Error('Key cannot sign', CKR.KEY_FUNCTION_NOT_PERMITTED);
    }

    // Validate mechanism matches key type
    this.validateMechanismForKey(mechanism.mechanism, obj.attributes[0x00000100]);

    session.signInit = { mechanism, keyHandle };
  }

  async sign(sessionHandle: SessionHandle, data: Buffer): Promise<Buffer> {
    this.ensureInitialized();
    const slot = this.slots.get(sessionHandle.slotIndex);
    if (!slot) throw new Pkcs11Error('Slot not found', CKR.SLOT_ID_INVALID);
    
    const session = slot.sessions.get(sessionHandle.handle);
    if (!session || !session.signInit) {
      throw new Pkcs11Error('Sign not initialized', CKR.OPERATION_NOT_INITIALIZED);
    }

    // Mock signature: return a deterministic "signature" based on data
    const signature = Buffer.concat([
      Buffer.from('MOCK-SIG-'),
      Buffer.from(session.signInit.keyHandle),
      Buffer.from('-'),
      data.length > 32 ? data.subarray(0, 32) : data,
    ]);

    return signature;
  }

  async signUpdate(sessionHandle: SessionHandle, data: Buffer): Promise<void> {
    this.ensureInitialized();
    // Mock: just validate session
    const slot = this.slots.get(sessionHandle.slotIndex);
    if (!slot) throw new Pkcs11Error('Slot not found', CKR.SLOT_ID_INVALID);
    
    const session = slot.sessions.get(sessionHandle.handle);
    if (!session || !session.signInit) {
      throw new Pkcs11Error('Sign not initialized', CKR.OPERATION_NOT_INITIALIZED);
    }
  }

  async signFinal(sessionHandle: SessionHandle): Promise<Buffer> {
    this.ensureInitialized();
    const slot = this.slots.get(sessionHandle.slotIndex);
    if (!slot) throw new Pkcs11Error('Slot not found', CKR.SLOT_ID_INVALID);
    
    const session = slot.sessions.get(sessionHandle.handle);
    if (!session || !session.signInit) {
      throw new Pkcs11Error('Sign not initialized', CKR.OPERATION_NOT_INITIALIZED);
    }

    const signature = Buffer.from(`MOCK-SIG-FINAL-${session.signInit.keyHandle}`);
    session.signInit = undefined;
    return signature;
  }

  async signRecoverInit(sessionHandle: SessionHandle, mechanism: Mechanism, keyHandle: any): Promise<void> {
    return this.signInit(sessionHandle, mechanism, keyHandle);
  }

  async signRecover(sessionHandle: SessionHandle, data: Buffer): Promise<Buffer> {
    return this.sign(sessionHandle, data);
  }

  // Verification operations
  async verifyInit(sessionHandle: SessionHandle, mechanism: Mechanism, keyHandle: any): Promise<void> {
    this.ensureInitialized();
    const slot = this.slots.get(sessionHandle.slotIndex);
    if (!slot) throw new Pkcs11Error('Slot not found', CKR.SLOT_ID_INVALID);
    
    const session = slot.sessions.get(sessionHandle.handle);
    if (!session) throw new Pkcs11Error('Session not found', CKR.SESSION_HANDLE_INVALID);

    const obj = slot.objects.get(keyHandle);
    if (!obj) throw new Pkcs11Error('Key not found', CKR.KEY_HANDLE_INVALID);
    if (obj.attributes[0x00000000] !== CKO.PUBLIC_KEY) {
      throw new Pkcs11Error('Key is not a public key', CKR.KEY_TYPE_INCONSISTENT);
    }
    if (!obj.attributes[0x00000109]) {
      throw new Pkcs11Error('Key cannot verify', CKR.KEY_FUNCTION_NOT_PERMITTED);
    }

    this.validateMechanismForKey(mechanism.mechanism, obj.attributes[0x00000100]);
    session.verifyInit = { mechanism, keyHandle };
  }

  async verify(sessionHandle: SessionHandle, data: Buffer, signature: Buffer): Promise<boolean> {
    this.ensureInitialized();
    // Mock: always return true for valid mock signatures
    return signature.toString().startsWith('MOCK-SIG-');
  }

  async verifyUpdate(sessionHandle: SessionHandle, data: Buffer): Promise<void> {
    // Mock: no-op
  }

  async verifyFinal(sessionHandle: SessionHandle, signature: Buffer): Promise<boolean> {
    return this.verify(sessionHandle, Buffer.alloc(0), signature);
  }

  async verifyRecoverInit(sessionHandle: SessionHandle, mechanism: Mechanism, keyHandle: any): Promise<void> {
    return this.verifyInit(sessionHandle, mechanism, keyHandle);
  }

  async verifyRecover(sessionHandle: SessionHandle, signature: Buffer): Promise<Buffer> {
    // Mock: return original data
    return Buffer.from('mock-recovered-data');
  }

  // Digest operations
  async digestInit(sessionHandle: SessionHandle, mechanism: Mechanism): Promise<void> {
    this.ensureInitialized();
    const slot = this.slots.get(sessionHandle.slotIndex);
    if (!slot) throw new Pkcs11Error('Slot not found', CKR.SLOT_ID_INVALID);
    
    const session = slot.sessions.get(sessionHandle.handle);
    if (!session) throw new Pkcs11Error('Session not found', CKR.SESSION_HANDLE_INVALID);

    session.digestInit = mechanism;
  }

  async digest(sessionHandle: SessionHandle, data: Buffer): Promise<Buffer> {
    this.ensureInitialized();
    // Mock: return a fake hash
    return Buffer.from(`MOCK-HASH-${data.toString('hex').substring(0, 32)}`);
  }

  async digestUpdate(sessionHandle: SessionHandle, data: Buffer): Promise<void> {
    // Mock: no-op
  }

  async digestKey(sessionHandle: SessionHandle, keyHandle: any): Promise<void> {
    // Mock: no-op
  }

  async digestFinal(sessionHandle: SessionHandle): Promise<Buffer> {
    return Buffer.from('MOCK-HASH-FINAL');
  }

  // Mechanism support
  async getMechanismList(slotIndex: number): Promise<number[]> {
    this.ensureInitialized();
    return [
      CKM.RSA_PKCS,
      CKM.SHA256_RSA_PKCS,
      CKM.SHA384_RSA_PKCS,
      CKM.SHA512_RSA_PKCS,
      CKM.SHA256_RSA_PKCS_PSS,
      CKM.ECDSA,
      CKM.ECDSA_SHA256,
      CKM.SHA256,
      CKM.SHA384,
      CKM.SHA512,
    ];
  }

  async getMechanismInfo(slotIndex: number, mechanism: number): Promise<{
    minKeySize: number;
    maxKeySize: number;
    flags: number;
  }> {
    this.ensureInitialized();
    const infoMap: Record<number, { minKeySize: number; maxKeySize: number; flags: number }> = {
      [CKM.RSA_PKCS]: { minKeySize: 1024, maxKeySize: 4096, flags: 0x0000000F },
      [CKM.SHA256_RSA_PKCS]: { minKeySize: 1024, maxKeySize: 4096, flags: 0x0000000F },
      [CKM.ECDSA]: { minKeySize: 192, maxKeySize: 521, flags: 0x0000000F },
      [CKM.ECDSA_SHA256]: { minKeySize: 256, maxKeySize: 521, flags: 0x0000000F },
      [CKM.SHA256]: { minKeySize: 0, maxKeySize: 0, flags: 0x0000000F },
    };
    return infoMap[mechanism] || { minKeySize: 0, maxKeySize: 0, flags: 0 };
  }

  // Random generation
  async seedRandom(sessionHandle: SessionHandle, seed: Buffer): Promise<void> {
    // Mock: no-op
  }

  async generateRandom(sessionHandle: SessionHandle, length: number): Promise<Buffer> {
    return Buffer.alloc(length).fill(0x42); // Mock random data
  }

  getFunctionList(): any {
    return {};
  }

  // Test helper methods
  setPin(pin: string): void {
    this.defaultPin = pin;
  }

  setSoPin(pin: string): void {
    this.defaultSoPin = pin;
  }

  addSlot(slotIndex: number, tokenInfo?: Partial<TokenInfo>): void {
    const slot: MockSlot = {
      index: slotIndex,
      tokenPresent: true,
      tokenInfo: {
        label: `mock-token-${slotIndex}`,
        manufacturerId: 'Mock HSM',
        model: 'Mock HSM v1.0',
        serialNumber: `MOCK${slotIndex}`,
        flags: 0x0000000F,
        maxSessionCount: 10,
        sessionCount: 0,
        maxRwSessionCount: 10,
        rwSessionCount: 0,
        maxPinLen: 255,
        minPinLen: 4,
        totalPublicMemory: 1024 * 1024,
        freePublicMemory: 512 * 1024,
        totalPrivateMemory: 1024 * 1024,
        freePrivateMemory: 512 * 1024,
        hardwareVersion: { major: 1, minor: 0 },
        firmwareVersion: { major: 1, minor: 0 },
        utcTime: new Date().toISOString().replace(/[-:]/g, '').split('.')[0] + '00',
        ...tokenInfo,
      },
      objects: new Map(),
      sessions: new Map(),
    };
    this.slots.set(slotIndex, slot);
  }

  removeSlot(slotIndex: number): void {
    this.slots.delete(slotIndex);
  }

  setTokenPresent(slotIndex: number, present: boolean): void {
    const slot = this.slots.get(slotIndex);
    if (slot) {
      slot.tokenPresent = present;
    }
  }

  private ensureInitialized(): void {
    if (!this.initialized) {
      throw new Pkcs11Error('PKCS#11 library not initialized', CKR.CRYPTOKI_NOT_INITIALIZED);
    }
  }

  private matchesTemplate(attributes: AttributeMap, template: FindObjectsTemplate): boolean {
    if (template.class !== undefined && attributes[0x00000000] !== template.class) return false;
    if (template.keyType !== undefined && attributes[0x00000100] !== template.keyType) return false;
    if (template.label !== undefined && attributes[0x00000003] !== template.label) return false;
    if (template.id !== undefined) {
      const attrId = attributes[0x00000102];
      if (!attrId || !attrId.equals(template.id)) return false;
    }
    if (template.token !== undefined && attributes[0x00000001] !== template.token) return false;
    if (template.private !== undefined && attributes[0x00000002] !== template.private) return false;
    if (template.sign !== undefined && attributes[0x00000108] !== template.sign) return false;
    if (template.verify !== undefined && attributes[0x00000109] !== template.verify) return false;
    return true;
  }

  private validateMechanismForKey(mechanism: MechanismType, keyType: CKK): void {
    const rsaMechanisms = [
      CKM.RSA_PKCS,
      CKM.SHA256_RSA_PKCS,
      CKM.SHA384_RSA_PKCS,
      CKM.SHA512_RSA_PKCS,
      CKM.SHA256_RSA_PKCS_PSS,
      CKM.SHA384_RSA_PKCS_PSS,
      CKM.SHA512_RSA_PKCS_PSS,
    ];
    const ecMechanisms = [
      CKM.ECDSA,
      CKM.ECDSA_SHA256,
      CKM.ECDSA_SHA384,
      CKM.ECDSA_SHA512,
    ];

    let supported: number[] = [];
    if (keyType === CKK.RSA) supported = rsaMechanisms;
    else if (keyType === CKK.EC || keyType === CKK.EC_EDWARDS) supported = ecMechanisms;

    if (!supported.includes(mechanism)) {
      throw new MechanismMismatchError(
        `Mechanism 0x${mechanism.toString(16)} not supported for key type ${keyType}`,
        mechanism,
        supported,
        keyType
      );
    }
  }
}
```

### src/adapters/index.ts

```typescript
/**
 * Adapter exports
 */

export { Pkcs11Adapter, SessionHandle, FindObjectsTemplate, AttributeMap, Pkcs11LibraryInfo, Mechanism, AdapterFactory } from './Pkcs11Adapter';
export { RealPkcs11Adapter } from './RealPkcs11Adapter';
export { MockPkcs11Adapter } from './MockPkcs11Adapter';
```

### src/utils/pin.ts

```typescript
/**
 * PIN handling utilities
 */

import { ConfigurationError } from '../errors';

export interface PinConfig {
  pin?: string;
  soPin?: string;
  pinSource?: 'env' | 'prompt' | 'file' | 'callback';
  pinCallback?: () => Promise<string>;
}

export async function resolvePin(config: PinConfig): Promise<string> {
  // Priority: explicit pin > env var > callback > prompt
  if (config.pin) {
    return config.pin;
  }

  if (process.env.PKCS11_PIN) {
    return process.env.PKCS11_PIN;
  }

  if (config.pinCallback) {
    return config.pinCallback();
  }

  if (config.pinSource === 'prompt') {
    return promptForPin('Enter PKCS#11 PIN: ');
  }

  throw new ConfigurationError(
    'PIN not provided. Set PKCS11_PIN environment variable or provide pin in config.',
    'pin'
  );
}

export async function resolveSoPin(config: PinConfig): Promise<string> {
  if (config.soPin) {
    return config.soPin;
  }

  if (process.env.PKCS11_SO_PIN) {
    return process.env.PKCS11_SO_PIN;
  }

  if (config.pinSource === 'prompt') {
    return promptForPin('Enter PKCS#11 SO PIN: ');
  }

  throw new ConfigurationError(
    'SO PIN not provided. Set PKCS11_SO_PIN environment variable or provide soPin in config.',
    'soPin'
  );
}

function promptForPin(prompt: string): Promise<string> {
  return new Promise((resolve, reject) => {
    process.stdin.setRawMode(true);
    process.stdout.write(prompt);
    
    let pin = '';
    const onData = (char: Buffer) => {
      const c = char.toString();
      if (c === '\n' || c === '\r' || c === '\u0004') {
        process.stdin.setRawMode(false);
        process.stdin.removeListener('data', onData);
        process.stdout.write('\n');
        resolve(pin);
      } else if (c === '\u0003') {
        process.stdin.setRawMode(false);
        process.stdin.removeListener('data', onData);
        process.stdout.write('\n');
        reject(new Error('Cancelled'));
      } else if (c === '\b' || c === '\u007f') {
        if (pin.length > 0) {
          pin = pin.slice(0, -1);
          process.stdout.write('\b \b');
        }
      } else {
        pin += c;
        process.stdout.write('*');
      }
    };

    process.stdin.on('data', onData);
  });
}

export function maskPin(pin: string): string {
  return '*'.repeat(pin.length);
}
```

### src/utils/mechanism.ts

```typescript
/**
 * Mechanism utilities and validation
 */

import { Mechanism, MechanismType, CKK, CKM } from '../types';
import { MechanismMismatchError } from '../errors';

export interface MechanismInfo {
  mechanism: MechanismType;
  name: string;
  description: string;
  keyTypes: CKK[];
  requiresHash: boolean;
  hashAlgorithm?: string;
}

export const SUPPORTED_MECHANISMS: MechanismInfo[] = [
  {
    mechanism: CKM.RSA_PKCS,
    name: 'CKM_RSA_PKCS',
    description: 'RSA PKCS#1 v1.5 signature (raw RSA, no hashing)',
    keyTypes: [CKK.RSA],
    requiresHash: false,
  },
  {
    mechanism: CKM.SHA256_RSA_PKCS,
    name: 'CKM_SHA256_RSA_PKCS',
    description: 'RSA PKCS#1 v1.5 with SHA-256',
    keyTypes: [CKK.RSA],
    requiresHash: true,
    hashAlgorithm: 'sha256',
  },
  {
    mechanism: CKM.SHA384_RSA_PKCS,
    name: 'CKM_SHA384_RSA_PKCS',
    description: 'RSA PKCS#1 v1.5 with SHA-384',
    keyTypes: [CKK.RSA],
    requiresHash: true,
    hashAlgorithm: 'sha384',
  },
  {
    mechanism: CKM.SHA512_RSA_PKCS,
    name: 'CKM_SHA512_RSA_PKCS',
    description: 'RSA PKCS#1 v1.5 with SHA-512',
    keyTypes: [CKK.RSA],
    requiresHash: true,
    hashAlgorithm: 'sha512',
  },
  {
    mechanism: CKM.SHA256_RSA_PKCS_PSS,
    name: 'CKM_SHA256_RSA_PKCS_PSS',
    description: 'RSA PKCS#1 PSS with SHA-256',
    keyTypes: [CKK.RSA],
    requiresHash: true,
    hashAlgorithm: 'sha256',
  },
  {
    mechanism: CKM.SHA384_RSA_PKCS_PSS,
    name: 'CKM_SHA384_RSA_PKCS_PSS',
    description: 'RSA PKCS#1 PSS with SHA-384',
    keyTypes: [CKK.RSA],
    requiresHash: true,
    hashAlgorithm: 'sha384',
  },
  {
    mechanism: CKM.SHA512_RSA_PKCS_PSS,
    name: 'CKM_SHA512_RSA_PKCS_PSS',
    description: 'RSA PKCS#1 PSS with SHA-512',
    keyTypes: [CKK.RSA],
    requiresHash: true,
    hashAlgorithm: 'sha512',
  },
  {
    mechanism: CKM.ECDSA,
    name: 'CKM_ECDSA',
    description: 'ECDSA signature (raw, no hashing)',
    keyTypes: [CKK.EC, CKK.EC_EDWARDS],
    requiresHash: false,
  },
  {
    mechanism: CKM.ECDSA_SHA256,
    name: 'CKM_ECDSA_SHA256',
    description: 'ECDSA with SHA-256',
    keyTypes: [CKK.EC, CKK.EC_EDWARDS],
    requiresHash: true,
    hashAlgorithm: 'sha256',
  },
  {
    mechanism: CKM.ECDSA_SHA384,
    name: 'CKM_ECDSA_SHA384',
    description: 'ECDSA with SHA-384',
    keyTypes: [CKK.EC, CKK.EC_EDWARDS],
    requiresHash: true,
    hashAlgorithm: 'sha384',
  },
  {
    mechanism: CKM.ECDSA_SHA512,
    name: 'CKM_ECDSA_SHA512',
    description: 'ECDSA with SHA-512',
    keyTypes: [CKK.EC, CKK.EC_EDWARDS],
    requiresHash: true,
    hashAlgorithm: 'sha512',
  },
];

export function getMechanismInfo(mechanism: MechanismType): MechanismInfo | undefined {
  return SUPPORTED_MECHANISMS.find(m => m.mechanism === mechanism);
}

export function getMechanismsForKeyType(keyType: CKK): MechanismInfo[] {
  return SUPPORTED_MECHANISMS.filter(m => m.keyTypes.includes(keyType));
}

export function validateMechanismForKey(mechanism: MechanismType, keyType: CKK): void {
  const info = getMechanismInfo(mechanism);
  if (!info) {
    throw new MechanismMismatchError(
      `Unknown mechanism: 0x${mechanism.toString(16)}`,
      mechanism,
      [],
      keyType
    );
  }
  if (!info.keyTypes.includes(keyType)) {
    throw new MechanismMismatchError(
      `Mechanism ${info.name} not supported for key type ${CKK[keyType]}`,
      mechanism,
      info.keyTypes.map(k => k as unknown as number),
      keyType
    );
  }
}

export function mechanismToString(mechanism: MechanismType): string {
  const info = getMechanismInfo(mechanism);
  return info ? info.name : `0x${mechanism.toString(16).toUpperCase().padStart(8, '0')}`;
}

export function parseMechanism(name: string): MechanismType {
  const upper = name.toUpperCase();
  for (const m of SUPPORTED_MECHANISMS) {
    if (m.name === upper || m.name.replace('CKM_', '') === upper) {
      return m.mechanism;
    }
  }
  // Try parsing as hex
  if (upper.startsWith('0X')) {
    return parseInt(upper, 16) as MechanismType;
  }
  throw new Error(`Unknown mechanism: ${name}`);
}

export function createMechanism(mechanism: MechanismType, parameter?: Buffer): Mechanism {
  return { mechanism, parameter };
}

export function getDefaultMechanismForKeyType(keyType: CKK): MechanismType {
  switch (keyType) {
    case CKK.RSA:
      return CKM.SHA256_RSA_PKCS;
    case CKK.EC:
    case CKK.EC_EDWARDS:
      return CKM.ECDSA_SHA256;
    default:
      throw new Error(`No default mechanism for key type ${keyType}`);
  }
}
```

### src/services/TokenManager.ts

```typescript
/**
 * Token and Slot Management Service
 */

import { Pkcs11Adapter, SlotInfo, TokenInfo } from '../adapters';
import { TokenNotFoundError, Pkcs11Error } from '../errors';
import { CKF } from '../types';
import pino from 'pino';

const logger = pino({ name: 'TokenManager' });

export interface TokenSelectionCriteria {
  slotIndex?: number;
  tokenLabel?: string;
  requireTokenPresent?: boolean;
  requireUserPin?: boolean;
  requireRwSession?: boolean;
}

export class TokenManager {
  constructor(private readonly adapter: Pkcs11Adapter) {}

  async enumerateSlots(tokenPresent = true): Promise<SlotInfo[]> {
    const slotIndices = await this.adapter.getSlotList(tokenPresent);
    const slots: SlotInfo[] = [];
    
    for (const index of slotIndices) {
      try {
        const info = await this.adapter.getSlotInfo(index);
        slots.push(info);
      } catch (error) {
        logger.warn({ slotIndex: index, err: error }, 'Failed to get slot info');
      }
    }
    
    return slots;
  }

  async enumerateTokens(slotIndex?: number): Promise<Array<{ slotIndex: number; tokenInfo: TokenInfo }>> {
    const slots = await this.enumerateSlots(true);
    const tokens: Array<{ slotIndex: number; tokenInfo: TokenInfo }> = [];
    
    for (const slot of slots) {
      if (slotIndex !== undefined && slot.slotIndex !== slotIndex) continue;
      
      try {
        const tokenInfo = await this.adapter.getTokenInfo(slot.slotIndex);
        tokens.push({ slotIndex: slot.slotIndex, tokenInfo });
      } catch (error) {
        logger.warn({ slotIndex: slot.slotIndex, err: error }, 'Failed to get token info');
      }
    }
    
    return tokens;
  }

  async selectToken(criteria: TokenSelectionCriteria = {}): Promise<{ slotIndex: number; tokenInfo: TokenInfo }> {
    const tokens = await this.enumerateTokens(criteria.slotIndex);
    
    if (tokens.length === 0) {
      throw new TokenNotFoundError(
        'No tokens found matching criteria',
        criteria.tokenLabel,
        criteria.slotIndex
      );
    }

    // Filter by label if provided
    let filtered = tokens;
    if (criteria.tokenLabel) {
      filtered = tokens.filter(t => t.tokenInfo.label === criteria.tokenLabel);
      if (filtered.length === 0) {
        throw new TokenNotFoundError(
          `Token with label "${criteria.tokenLabel}" not found`,
          criteria.tokenLabel,
          criteria.slotIndex
        );
      }
    }

    // Filter by requirements
    filtered = filtered.filter(t => {
      if (criteria.requireTokenPresent && !(t.tokenInfo.flags & 0x00000001)) return false;
      if (criteria.requireUserPin && !(t.tokenInfo.flags & 0x00000100)) return false; // USER_PIN_INITIALIZED
      if (criteria.requireRwSession && t.tokenInfo.maxRwSessionCount === 0) return false;
      return true;
    });

    if (filtered.length === 0) {
      throw new TokenNotFoundError(
        'No tokens match the specified requirements',
        criteria.tokenLabel,
        criteria.slotIndex
      );
    }

    // Return first matching token
    const selected = filtered[0];
    logger.info({ slotIndex: selected.slotIndex, tokenLabel: selected.tokenInfo.label }, 'Selected token');
    return selected;
  }

  async getTokenInfo(slotIndex: number): Promise<TokenInfo> {
    return this.adapter.getTokenInfo(slotIndex);
  }

  async waitForToken(slotIndex: number, timeout = 30000): Promise<TokenInfo> {
    const startTime = Date.now();
    
    while (Date.now() - startTime < timeout) {
      try {
        const slotInfo = await this.adapter.getSlotInfo(slotIndex);
        if (slotInfo.tokenPresent) {
          return await this.adapter.getTokenInfo(slotIndex);
        }
      } catch (error) {
        // Token not ready yet
      }
      
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    throw new TokenNotFoundError(
      `Token not present in slot ${slotIndex} after ${timeout}ms timeout`,
      undefined,
      slotIndex
    );
  }

  async getMechanismList(slotIndex: number): Promise<number[]> {
    return this.adapter.getMechanismList(slotIndex);
  }

  async getMechanismInfo(slotIndex: number, mechanism: number): Promise<{
    minKeySize: number;
    maxKeySize: number;
    flags: number;
  }> {
    return this.adapter.getMechanismInfo(slotIndex, mechanism);
  }

  async checkTokenHealth(slotIndex: number): Promise<{ healthy: boolean; issues: string[] }> {
    const issues: string[] = [];
    
    try {
      const slotInfo = await this.adapter.getSlotInfo(slotIndex);
      if (!slotInfo.tokenPresent) {
        issues.push('Token not present in slot');
      }
    } catch (error) {
      issues.push(`Slot error: ${error instanceof Error ? error.message : String(error)}`);
      return { healthy: false, issues };
    }

    try {
      const tokenInfo = await this.adapter.getTokenInfo(slotIndex);
      if (tokenInfo.flags & 0x00000004) { // CKF_WRITE_PROTECTED
        issues.push('Token is write-protected');
      }
      if (tokenInfo.freePrivateMemory < 1024) {
        issues.push('Low private memory on token');
      }
    } catch (error) {
      issues.push(`Token error: ${error instanceof Error ? error.message : String(error)}`);
    }

    return { healthy: issues.length === 0, issues };
  }
}
```

### src/services/SessionManager.ts

```typescript
/**
 * Session Management with Pooling and Concurrency Control
 */

import { Pkcs11Adapter, SessionHandle, SessionConfig } from '../adapters';
import { SessionError, Pkcs11Error } from '../errors';
import { CKU, CKF, CKR } from '../types';
import pino from 'pino';

const logger = pino({ name: 'SessionManager' });

export interface SessionPoolConfig {
  maxSize: number;
  readOnly: boolean;
  serialSession: boolean;
  idleTimeout: number; // ms
  maxAge: number; // ms
}

export interface PooledSession extends SessionHandle {
  lastUsed: number;
  useCount: number;
  healthy: boolean;
}

export class SessionManager {
  private pools: Map<number, PooledSession[]> = new Map();
  private readonly config: SessionPoolConfig;
  private cleanupInterval?: NodeJS.Timeout;

  constructor(
    private readonly adapter: Pkcs11Adapter,
    config: Partial<SessionPoolConfig> = {}
  ) {
    this.config = {
      maxSize: config.maxSize ?? 5,
      readOnly: config.readOnly ?? true,
      serialSession: config.serialSession ?? true,
      idleTimeout: config.idleTimeout ?? 300000, // 5 minutes
      maxAge: config.maxAge ?? 3600000, // 1 hour
    };

    // Start cleanup interval
    this.cleanupInterval = setInterval(() => this.cleanup(), 60000);
    this.cleanupInterval.unref();
  }

  async acquireSession(slotIndex: number, userPin?: string): Promise<PooledSession> {
    let pool = this.pools.get(slotIndex);
    if (!pool) {
      pool = [];
      this.pools.set(slotIndex, pool);
    }

    // Try to find an available healthy session
    for (const session of pool) {
      if (!session.inUse && session.healthy) {
        try {
          // Validate session is still alive
          await this.adapter.getSessionInfo(session);
          session.inUse = true;
          session.lastUsed = Date.now();
          session.useCount++;
          logger.debug({ slotIndex, handle: session.handle }, 'Reused session from pool');
          return session;
        } catch (error) {
          // Session is dead, mark unhealthy
          session.healthy = false;
          logger.debug({ slotIndex, handle: session.handle, err: error }, 'Session unhealthy, will recreate');
        }
      }
    }

    // Create new session if pool not full
    if (pool.length < this.config.maxSize) {
      return this.createSession(slotIndex, userPin);
    }

    // Pool full, wait for a session to become available
    return this.waitForSession(slotIndex, userPin);
  }

  async releaseSession(session: PooledSession): Promise<void> {
    session.inUse = false;
    session.lastUsed = Date.now();
    logger.debug({ slotIndex: session.slotIndex, handle: session.handle }, 'Session released to pool');
  }

  async destroySession(session: PooledSession): Promise<void> {
    const pool = this.pools.get(session.slotIndex);
    if (pool) {
      const index = pool.indexOf(session);
      if (index !== -1) {
        pool.splice(index, 1);
      }
    }
    
    try {
      await this.adapter.closeSession(session);
      logger.debug({ slotIndex: session.slotIndex, handle: session.handle }, 'Session destroyed');
    } catch (error) {
      logger.warn({ slotIndex: session.slotIndex, handle: session.handle, err: error }, 'Error destroying session');
    }
  }

  async loginSession(session: PooledSession, pin: string, userType = CKU.USER): Promise<void> {
    try {
      await this.adapter.login(session, userType, pin);
      logger.debug({ slotIndex: session.slotIndex }, 'Session logged in');
    } catch (error) {
      throw new SessionError(
        `Login failed: ${error instanceof Error ? error.message : String(error)}`,
        'login',
        session.handle
      );
    }
  }

  async logoutSession(session: PooledSession): Promise<void> {
    try {
      await this.adapter.logout(session);
      logger.debug({ slotIndex: session.slotIndex }, 'Session logged out');
    } catch (error) {
      logger.warn({ slotIndex: session.slotIndex, err: error }, 'Logout error');
    }
  }

  async closeAllSessions(slotIndex: number): Promise<void> {
    const pool = this.pools.get(slotIndex);
    if (pool) {
      for (const session of pool) {
        try {
          await this.adapter.closeSession(session);
        } catch (error) {
          logger.warn({ handle: session.handle, err: error }, 'Error closing session');
        }
      }
      pool.length = 0;
    }
    
    try {
      await this.adapter.closeAllSessions(slotIndex);
    } catch (error) {
      logger.warn({ slotIndex, err: error }, 'Error closing all sessions');
    }
  }

  async shutdown(): Promise<void> {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
    
    for (const [slotIndex] of this.pools) {
      await this.closeAllSessions(slotIndex);
    }
    this.pools.clear();
    logger.info('Session manager shut down');
  }

  getPoolStats(slotIndex: number): { total: number; inUse: number; available: number; healthy: number } {
    const pool = this.pools.get(slotIndex) || [];
    return {
      total: pool.length,
      inUse: pool.filter(s => s.inUse).length,
      available: pool.filter(s => !s.inUse && s.healthy).length,
      healthy: pool.filter(s => s.healthy).length,
    };
  }

  private async createSession(slotIndex: number, userPin?: string): Promise<PooledSession> {
    const sessionConfig: SessionConfig = {
      readOnly: this.config.readOnly,
      serialSession: this.config.serialSession,
    };

    const handle = await this.adapter.openSession(slotIndex, sessionConfig);
    const pooledSession: PooledSession = {
      ...handle,
      lastUsed: Date.now(),
      useCount: 1,
      healthy: true,
      inUse: true,
    };

    const pool = this.pools.get(slotIndex)!;
    pool.push(pooledSession);

    // Login if PIN provided
    if (userPin) {
      await this.loginSession(pooledSession, userPin);
    }

    logger.debug({ slotIndex, handle: pooledSession.handle }, 'Created new session');
    return pooledSession;
  }

  private async waitForSession(slotIndex: number, userPin?: string): Promise<PooledSession> {
    const maxWait = 30000; // 30 seconds
    const startTime = Date.now();
    
    while (Date.now() - startTime < maxWait) {
      const pool = this.pools.get(slotIndex) || [];
      for (const session of pool) {
        if (!session.inUse && session.healthy) {
          try {
            await this.adapter.getSessionInfo(session);
            session.inUse = true;
            session.lastUsed = Date.now();
            session.useCount++;
            return session;
          } catch {
            session.healthy = false;
          }
        }
      }
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    throw new SessionError('Timeout waiting for available session', 'acquire', undefined);
  }

  private cleanup(): void {
    const now = Date.now();
    
    for (const [slotIndex, pool] of this.pools) {
      const toRemove: PooledSession[] = [];
      
      for (const session of pool) {
        if (session.inUse) continue;
        
        const idleTime = now - session.lastUsed;
        const age = now - session.createdAt;
        
        if (idleTime > this.config.idleTimeout || age > this.config.maxAge) {
          toRemove.push(session);
        }
      }
      
      for (const session of toRemove) {
        const index = pool.indexOf(session);
        if (index !== -1) {
          pool.splice(index, 1);
          this.destroySession(session).catch(err => 
            logger.warn({ handle: session.handle, err }, 'Error destroying idle session')
          );
        }
      }
    }
  }
}
```

### src/services/CsrGenerator.ts

```typescript
/**
 * PKCS#10 Certificate Signing Request Generator
 */

import * as forge from 'node-forge';
import { Pkcs11Adapter, SessionHandle, Mechanism } from '../adapters';
import { KeyInfo, CsrRequest, CsrResponse, CsrSubject, CsrExtension, CKK, CKM, MechanismType } from '../types';
import { KeyNotFoundError, CsrGenerationError, MechanismMismatchError } from '../errors';
import { validateMechanismForKey, getMechanismInfo } from '../utils/mechanism';
import pino from 'pino';

const logger = pino({ name: 'CsrGenerator' });

// OID mappings
const OIDS: Record<string, string> = {
  commonName: '2.5.4.3',
  organizationName: '2.5.4.10',
  organizationalUnitName: '2.5.4.11',
  countryName: '2.5.4.6',
  stateOrProvinceName: '2.5.4.8',
  localityName: '2.5.4.7',
  emailAddress: '1.2.840.113549.1.9.1',
  subjectAltName: '2.5.29.17',
  keyUsage: '2.5.29.15',
  extendedKeyUsage: '2.5.29.37',
  basicConstraints: '2.5.29.19',
};

export class CsrGenerator {
  constructor(private readonly adapter: Pkcs11Adapter) {}

  async generateCsr(session: SessionHandle, request: CsrRequest): Promise<CsrResponse> {
    // Find the private key
    const keyInfo = await this.findPrivateKey(session, request.keyLabel, request.keyId);
    
    // Validate mechanism
    const mechanism = request.mechanism || this.getDefaultMechanism(keyInfo.keyType);
    validateMechanismForKey(mechanism, keyInfo.keyType);
    
    // Get public key
    const publicKeyPem = await this.exportPublicKey(session, keyInfo);
    
    // Build CSR using forge
    const csr = await this.buildCsr(request, publicKeyPem, keyInfo);
    
    // Sign CSR using HSM
    const signature = await this.signCsr(session, keyInfo, mechanism, csr);
    
    // Create final CSR with signature
    const finalCsr = this.finalizeCsr(csr, signature, mechanism, keyInfo.keyType);
    
    const csrDer = forge.asn1.toDer(finalCsr).getBytes();
    const csrPem = forge.pki.certificationRequestToPem(finalCsr);
    
    return {
      csrPem,
      csrDer: Buffer.from(csrDer, 'binary'),
      publicKeyPem,
      keyLabel: keyInfo.label,
      keyId: keyInfo.id,
    };
  }

  private async findPrivateKey(
    session: SessionHandle,
    keyLabel: string,
    keyId?: Buffer
  ): Promise<KeyInfo> {
    const template: any = {
      class: CKO.PRIVATE_KEY,
      label: keyLabel,
      token: true,
      sign: true,
    };
    
    if (keyId) {
      template.id = keyId;
    }

    const objects = await this.adapter.findObjects(session, template, 10);
    
    if (objects.length === 0) {
      throw new KeyNotFoundError(
        `Private key not found with label "${keyLabel}"${keyId ? ` and ID ${keyId.toString('hex')}` : ''}`,
        keyLabel,
        keyId
      );
    }

    if (objects.length > 1) {
      logger.warn({ keyLabel, count: objects.length }, 'Multiple keys found, using first');
    }

    const keyHandle = objects[0];
    const attributes = await this.adapter.getAttributeValue(session, keyHandle, [
      0x00000000, // CKA_CLASS
      0x00000100, // CKA_KEY_TYPE
      0x00000003, // CKA_LABEL
      0x00000102, // CKA_ID
      0x00000121, // CKA_MODULUS_BITS / CKA_PRIME_BITS
      0x00000162, // CKA_EXTRACTABLE
      0x00000108, // CKA_SIGN
      0x00000109, // CKA_VERIFY
      0x00000104, // CKA_ENCRYPT
      0x00000105, // CKA_DECRYPT
      0x00000106, // CKA_WRAP
      0x00000107, // CKA_UNWRAP
      0x0000010A, // CKA_DERIVE
    ]);

    const keyType = attributes[0x00000100] as CKK;
    const keySize = attributes[0x00000121] as number;

    return {
      handle: keyHandle,
      label: attributes[0x00000003] as string,
      id: attributes[0x00000102] as Buffer,
      keyType,
      keySize,
      extractable: attributes[0x00000162] as boolean,
      sign: attributes[0x00000108] as boolean,
      verify: attributes[0x00000109] as boolean,
      decrypt: attributes[0x00000105] as boolean,
      wrap: attributes[0x00000106] as boolean,
      unwrap: attributes[0x00000107] as boolean,
      derive: attributes[0x0000010A] as boolean,
    };
  }

  private async exportPublicKey(session: SessionHandle, keyInfo: KeyInfo): Promise<string> {
    // Find corresponding public key
    const template: any = {
      class: CKO.PUBLIC_KEY,
      label: keyInfo.label,
      token: true,
    };
    
    if (keyInfo.id.length > 0) {
      template.id = keyInfo.id;
    }

    const objects = await this.adapter.findObjects(session, template, 1);
    if (objects.length === 0) {
      throw new CsrGenerationError('Corresponding public key not found', 'PUBLIC_KEY_NOT_FOUND');
    }

    const pubHandle = objects[0];
    const attributes = await this.adapter.getAttributeValue(session, pubHandle, [
      0x00000100, // CKA_KEY_TYPE
      0x00000120, // CKA_MODULUS (RSA)
      0x00000122, // CKA_PUBLIC_EXPONENT (RSA)
      0x00000180, // CKA_EC_PARAMS (EC)
      0x00000181, // CKA_EC_POINT (EC)
    ]);

    const keyType = attributes[0x00000100] as CKK;
    
    if (keyType === CKK.RSA) {
      const modulus = attributes[0x00000120] as Buffer;
      const exponent = attributes[0x00000122] as Buffer;
      return this.createRsaPublicKeyPem(modulus, exponent);
    } else if (keyType === CKK.EC || keyType === CKK.EC_EDWARDS) {
      const ecParams = attributes[0x00000180] as Buffer;
      const ecPoint = attributes[0x00000181] as Buffer;
      return this.createEcPublicKeyPem(ecParams, ecPoint);
    }
    
    throw new CsrGenerationError(`Unsupported key type: ${keyType}`, 'UNSUPPORTED_KEY_TYPE');
  }

  private createRsaPublicKeyPem(modulus: Buffer, exponent: Buffer): string {
    const n = forge.util.bytesToHex(modulus);
    const e = forge.util.bytesToHex(exponent);
    
    const rsaPublicKey = forge.pki.setRsaPublicKey(
      new forge.jsbn.BigInteger(n, 16),
      new forge.jsbn.BigInteger(e, 16)
    );
    
    return forge.pki.publicKeyToPem(rsaPublicKey);
  }

  private createEcPublicKeyPem(ecParams: Buffer, ecPoint: Buffer): string {
    // Parse EC parameters (OID) and point
    // This is simplified - real implementation would parse the OID to get curve name
    const curveOid = forge.util.bytesToHex(ecParams);
    const pointHex = forge.util.bytesToHex(ecPoint);
    
    // Common curve OIDs
    const curveMap: Record<string, string> = {
      '06082a8648ce3d030107': 'secp256r1', // prime256v1
      '06052b81040022': 'secp384r1',
      '06052b81040023': 'secp521r1',
      '06072a8648ce3d0201': 'secp256k1',
    };
    
    const curveName = curveMap[curveOid] || 'secp256r1';
    
    // Create EC public key from point
    const ecPublicKey = forge.pki.setEcPublicKey(
      curveName,
      new forge.jsbn.BigInteger(pointHex.substring(2), 16) // Remove 0x04 prefix
    );
    
    return forge.pki.publicKeyToPem(ecPublicKey);
  }

  private async buildCsr(
    request: CsrRequest,
    publicKeyPem: string,
    keyInfo: KeyInfo
  ): Promise<any> {
    const csr = forge.pki.createCertificationRequest();
    csr.publicKey = forge.pki.publicKeyFromPem(publicKeyPem);
    
    // Set subject
    const subjectAttrs: any[] = [];
    if (request.subject.commonName) subjectAttrs.push({ name: 'commonName', value: request.subject.commonName });
    if (request.subject.organization) subjectAttrs.push({ name: 'organizationName', value: request.subject.organization });
    if (request.subject.organizationalUnit) subjectAttrs.push({ name: 'organizationalUnitName', value: request.subject.organizationalUnit });
    if (request.subject.country) subjectAttrs.push({ name: 'countryName', value: request.subject.country });
    if (request.subject.state) subjectAttrs.push({ name: 'stateOrProvinceName', value: request.subject.state });
    if (request.subject.locality) subjectAttrs.push({ name: 'localityName', value: request.subject.locality });
    if (request.subject.emailAddress) subjectAttrs.push({ name: 'emailAddress', value: request.subject.emailAddress });
    
    csr.setSubject(subjectAttrs);
    
    // Add extensions
    if (request.extensions && request.extensions.length > 0) {
      const extAttrs: any[] = [];
      for (const ext of request.extensions) {
        extAttrs.push({
          id: ext.oid,
          critical: ext.critical,
          value: ext.value,
        });
      }
      csr.setAttributes([{ name: 'extensionRequest', extensions: extAttrs }]);
    }
    
    return csr;
  }

  private async signCsr(
    session: SessionHandle,
    keyInfo: KeyInfo,
    mechanism: MechanismType,
    csr: any
  ): Promise<Buffer> {
    // Get the TBS (to-be-signed) portion of the CSR
    const tbs = forge.asn1.toDer(csr.certificationRequestInfo).getBytes();
    const tbsBuffer = Buffer.from(tbs, 'binary');
    
    // Initialize signing
    const mechInfo = getMechanismInfo(mechanism);
    let mechanismObj: Mechanism = { mechanism };
    
    // For mechanisms that require hashing, the HSM does the hashing internally
    // For raw mechanisms (CKM_RSA_PKCS, CKM_ECDSA), we need to hash first
    if (!mechInfo?.requiresHash) {
      // Hash the data externally
      const hashAlg = keyInfo.keyType === CKK.RSA ? 'sha256' : 'sha256';
      const md = forge.md[hashAlg].create();
      md.update(tbs);
      const digest = Buffer.from(md.digest().bytes(), 'binary');
      
      await this.adapter.signInit(session, mechanismObj, keyInfo.handle);
      return this.adapter.sign(session, digest);
    } else {
      // HSM will hash internally
      await this.adapter.signInit(session, mechanismObj, keyInfo.handle);
      return this.adapter.sign(session, tbsBuffer);
    }
  }

  private finalizeCsr(csr: any, signature: Buffer, mechanism: MechanismType, keyType: CKK): any {
    // Determine signature algorithm OID
    let sigOid: string;
    const mechInfo = getMechanismInfo(mechanism);
    
    if (keyType === CKK.RSA) {
      if (mechanism === CKM.RSA_PKCS) {
        sigOid = '1.2.840.113549.1.1.1'; // sha256WithRSAEncryption (approximate)
      } else if (mechanism === CKM.SHA256_RSA_PKCS || mechanism === CKM.SHA256_RSA_PKCS_PSS) {
        sigOid = '1.2.840.113549.1.1.11'; // sha256WithRSAEncryption
      } else if (mechanism === CKM.SHA384_RSA_PKCS || mechanism === CKM.SHA384_RSA_PKCS_PSS) {
        sigOid = '1.2.840.113549.1.1.12'; // sha384WithRSAEncryption
      } else if (mechanism === CKM.SHA512_RSA_PKCS || mechanism === CKM.SHA512_RSA_PKCS_PSS) {
        sigOid = '1.2.840.113549.1.1.13'; // sha512WithRSAEncryption
      } else {
        sigOid = '1.2.840.113549.1.1.11'; // default to SHA256
      }
    } else {
      // EC
      if (mechanism === CKM.ECDSA) {
        sigOid = '1.2.840.10045.4.3.2'; // ecdsa-with-SHA256 (approximate)
      } else if (mechanism === CKM.ECDSA_SHA256) {
        sigOid = '1.2.840.10045.4.3.2';
      } else if (mechanism === CKM.ECDSA_SHA384) {
        sigOid = '1.2.840.10045.4.3.3';
      } else if (mechanism === CKM.ECDSA_SHA512) {
        sigOid = '1.2.840.10045.4.3.4';
      } else {
        sigOid = '1.2.840.10045.4.3.2';
      }
    }
    
    // Set signature algorithm and value
    csr.signatureAlgorithm = sigOid;
    csr.signature = forge.util.createBuffer(signature.toString('binary'));
    csr.signatureOid = sigOid;
    
    return csr;
  }

  private getDefaultMechanism(keyType: CKK): MechanismType {
    switch (keyType) {
      case CKK.RSA:
        return CKM.SHA256_RSA_PKCS;
      case CKK.EC:
      case CKK.EC_EDWARDS:
        return CKM.ECDSA_SHA256;
      default:
        throw new CsrGenerationError(`No default mechanism for key type ${keyType}`, 'NO_DEFAULT_MECHANISM');
    }
  }
}
```

### src/services/SigningService.ts

```typescript
/**
 * Core Signing Service - High-level API for signing operations
 */

import { Pkcs11Adapter, SessionHandle, Mechanism, MechanismType } from '../adapters';
import { TokenManager } from './TokenManager';
import { SessionManager, PooledSession } from './SessionManager';
import { CsrGenerator } from './CsrGenerator';
import { KeyInfo, SignRequest, SignResponse, CsrRequest, CsrResponse, ServiceConfig, CKK, CKM, CKU } from '../types';
import { KeyNotFoundError, MechanismMismatchError, SessionError, Pkcs11Error } from '../errors';
import { validateMechanismForKey, getDefaultMechanismForKeyType, parseMechanism } from '../utils/mechanism';
import { resolvePin } from '../utils/pin';
import pino from 'pino';

const logger = pino({ name: 'SigningService' });

export class SigningService {
  private tokenManager: TokenManager;
  private sessionManager: SessionManager;
  private csrGenerator: CsrGenerator;
  private config: ServiceConfig;
  private initialized = false;
  private currentSlotIndex: number = 0;
  private currentKeyInfo?: KeyInfo;

  constructor(
    private readonly adapter: Pkcs11Adapter,
    config: Partial<ServiceConfig> = {}
  ) {
    this.config = {
      libPath: config.libPath || process.env.PKCS11_LIB_PATH || '',
      pin: config.pin || process.env.PKCS11_PIN || '',
      soPin: config.soPin || process.env.PKCS11_SO_PIN,
      slotIndex: config.slotIndex ?? (process.env.PKCS11_SLOT_INDEX ? parseInt(process.env.PKCS11_SLOT_INDEX) : undefined),
      tokenLabel: config.tokenLabel || process.env.PKCS11_TOKEN_LABEL,
      keyLabel: config.keyLabel || process.env.PKCS11_KEY_LABEL || '',
      keyId: config.keyId || (process.env.PKCS11_KEY_ID ? Buffer.from(process.env.PKCS11_KEY_ID, 'hex') : undefined),
      defaultMechanism: config.defaultMechanism || parseMechanism(process.env.PKCS11_DEFAULT_MECHANISM || 'CKM_SHA256_RSA_PKCS'),
      sessionPoolSize: config.sessionPoolSize ?? 5,
      readOnlySession: config.readOnlySession ?? true,
      logLevel: config.logLevel || process.env.LOG_LEVEL || 'info',
    };

    this.tokenManager = new TokenManager(adapter);
    this.sessionManager = new SessionManager(adapter, {
      maxSize: this.config.sessionPoolSize,
      readOnly: this.config.readOnlySession,
      serialSession: true,
      idleTimeout: 300000,
      maxAge: 3600000,
    });
    this.csrGenerator = new CsrGenerator(adapter);
  }

  async initialize(): Promise<void> {
    if (this.initialized) {
      logger.warn('Signing service already initialized');
      return;
    }

    // Validate configuration
    if (!this.config.libPath) {
      throw new Error('PKCS#11 library path not configured (PKCS11_LIB_PATH)');
    }
    if (!this.config.keyLabel) {
      throw new Error('Key label not configured (PKCS11_KEY_LABEL)');
    }

    // Initialize PKCS#11 library
    await this.adapter.initialize(this.config.libPath);
    
    // Select token
    const token = await this.tokenManager.selectToken({
      slotIndex: this.config.slotIndex,
      tokenLabel: this.config.tokenLabel,
      requireTokenPresent: true,
      requireUserPin: true,
      requireRwSession: !this.config.readOnlySession,
    });
    
    this.currentSlotIndex = token.slotIndex;
    
    // Get PIN
    const pin = await resolvePin({ pin: this.config.pin });
    
    // Acquire a session to verify key exists and login
    const session = await this.sessionManager.acquireSession(this.currentSlotIndex, pin);
    try {
      this.currentKeyInfo = await this.findAndValidateKey(session);
      logger.info({ 
        keyLabel: this.currentKeyInfo.label, 
        keyId: this.currentKeyInfo.id.toString('hex'),
        keyType: CKK[this.currentKeyInfo.keyType],
        keySize: this.currentKeyInfo.keySize 
      }, 'Key validated successfully');
    } finally {
      await this.sessionManager.releaseSession(session);
    }

    this.initialized = true;
    logger.info({ slotIndex: this.currentSlotIndex }, 'Signing service initialized');
  }

  async sign(request: SignRequest): Promise<SignResponse> {
    this.ensureInitialized();
    
    const mechanism = request.mechanism || this.config.defaultMechanism;
    const keyLabel = request.keyLabel || this.config.keyLabel;
    const keyId = request.keyId || this.config.keyId;
    
    // Acquire session
    const pin = await resolvePin({ pin: this.config.pin });
    const session = await this.sessionManager.acquireSession(this.currentSlotIndex, pin);
    
    try {
      // Find key if different from default
      let keyInfo = this.currentKeyInfo;
      if (keyLabel !== this.config.keyLabel || (keyId && !keyId.equals(this.config.keyId || Buffer.alloc(0)))) {
        keyInfo = await this.findKey(session, keyLabel, keyId);
      }
      
      if (!keyInfo) {
        throw new KeyNotFoundError('Key not found', keyLabel, keyId);
      }
      
      // Validate mechanism
      validateMechanismForKey(mechanism, keyInfo.keyType);
      
      // Perform signing
      const mechObj: Mechanism = { mechanism };
      await this.adapter.signInit(session, mechObj, keyInfo.handle);
      const signature = await this.adapter.sign(session, request.data);
      
      return {
        signature,
        mechanism,
        keyLabel: keyInfo.label,
        keyId: keyInfo.id,
      };
    } catch (error) {
      if (error instanceof Pkcs11Error && error.pkcs11Code === CKR.DEVICE_REMOVED) {
        // Token removed, invalidate sessions
        await this.sessionManager.closeAllSessions(this.currentSlotIndex);
        this.currentKeyInfo = undefined;
      }
      throw error;
    } finally {
      await this.sessionManager.releaseSession(session);
    }
  }

  async signMulti(requests: SignRequest[]): Promise<SignResponse[]> {
    // Process concurrently with limited concurrency
    const concurrency = this.config.sessionPoolSize;
    const results: SignResponse[] = [];
    
    for (let i = 0; i < requests.length; i += concurrency) {
      const batch = requests.slice(i, i + concurrency);
      const batchResults = await Promise.all(batch.map(req => this.sign(req)));
      results.push(...batchResults);
    }
    
    return results;
  }

  async createCsr(request: CsrRequest): Promise<CsrResponse> {
    this.ensureInitialized();
    
    const pin = await resolvePin({ pin: this.config.pin });
    const session = await this.sessionManager.acquireSession(this.currentSlotIndex, pin);
    
    try {
      return await this.csrGenerator.generateCsr(session, request);
    } finally {
      await this.sessionManager.releaseSession(session);
    }
  }

  async getKeyInfo(keyLabel?: string, keyId?: Buffer): Promise<KeyInfo> {
    this.ensureInitialized();
    
    const pin = await resolvePin({ pin: this.config.pin });
    const session = await this.sessionManager.acquireSession(this.currentSlotIndex, pin);
    
    try {
      const label = keyLabel || this.config.keyLabel;
      const id = keyId || this.config.keyId;
      const keyInfo = await this.findKey(session, label, id);
      
      if (!keyInfo) {
        throw new KeyNotFoundError('Key not found', label, id);
      }
      
      return keyInfo;
    } finally {
      await this.sessionManager.releaseSession(session);
    }
  }

  async listKeys(keyType?: CKK): Promise<KeyInfo[]> {
    this.ensureInitialized();
    
    const pin = await resolvePin({ pin: this.config.pin });
    const session = await this.sessionManager.acquireSession(this.currentSlotIndex, pin);
    
    try {
      const template: any = {
        class: CKO.PRIVATE_KEY,
        token: true,
        sign: true,
      };
      
      if (keyType) {
        template.keyType = keyType;
      }
      
      const objects = await this.adapter.findObjects(session, template, 100);
      const keys: KeyInfo[] = [];
      
      for (const handle of objects) {
        const attrs = await this.adapter.getAttributeValue(session, handle, [
          0x00000000, 0x00000100, 0x00000003, 0x00000102, 0x00000121,
          0x00000162, 0x00000108, 0x00000109, 0x00000104, 0x00000105,
          0x00000106, 0x00000107, 0x0000010A,
        ]);
        
        keys.push({
          handle,
          label: attrs[0x00000003] as string,
          id: attrs[0x00000102] as Buffer,
          keyType: attrs[0x00000100] as CKK,
          keySize: attrs[0x00000121] as number,
          extractable: attrs[0x00000162] as boolean,
          sign: attrs[0x00000108] as boolean,
          verify: attrs[0x00000109] as boolean,
          decrypt: attrs[0x00000105] as boolean,
          wrap: attrs[0x00000106] as boolean,
          unwrap: attrs[0x00000107] as boolean,
          derive: attrs[0x0000010A] as boolean,
        });
      }
      
      return keys;
    } finally {
      await this.sessionManager.releaseSession(session);
    }
  }

  async getTokenInfo(): Promise<any> {
    this.ensureInitialized();
    return this.tokenManager.getTokenInfo(this.currentSlotIndex);
  }

  async getSlotInfo(): Promise<any> {
    this.ensureInitialized();
    return this.tokenManager.getSlotInfo(this.currentSlotIndex);
  }

  async getMechanismList(): Promise<number[]> {
    this.ensureInitialized();
    return this.tokenManager.getMechanismList(this.currentSlotIndex);
  }

  async healthCheck(): Promise<{ healthy: boolean; details: any }> {
    try {
      if (!this.initialized) {
        return { healthy: false, details: { reason: 'Not initialized' } };
      }
      
      const tokenHealth = await this.tokenManager.checkTokenHealth(this.currentSlotIndex);
      const poolStats = this.sessionManager.getPoolStats(this.currentSlotIndex);
      
      return {
        healthy: tokenHealth.healthy,
        details: {
          token: tokenHealth,
          sessionPool: poolStats,
          key: this.currentKeyInfo ? {
            label: this.currentKeyInfo.label,
            id: this.currentKeyInfo.id.toString('hex'),
            type: CKK[this.currentKeyInfo.keyType],
            size: this.currentKeyInfo.keySize,
          } : null,
        },
      };
    } catch (error) {
      return {
        healthy: false,
        details: { error: error instanceof Error ? error.message : String(error) },
      };
    }
  }

  async shutdown(): Promise<void> {
    await this.sessionManager.shutdown();
    await this.adapter.finalize();
    this.initialized = false;
    logger.info('Signing service shut down');
  }

  private async findAndValidateKey(session: SessionHandle): Promise<KeyInfo> {
    const keyInfo = await this.findKey(session, this.config.keyLabel, this.config.keyId);
    
    if (!keyInfo) {
      throw new KeyNotFoundError(
        `Default key not found: label="${this.config.keyLabel}"${this.config.keyId ? `, id=${this.config.keyId.toString('hex')}` : ''}`,
        this.config.keyLabel,
        this.config.keyId
      );
    }
    
    // Validate key can sign
    if (!keyInfo.sign) {
      throw new Error(`Key "${keyInfo.label}" does not have CKA_SIGN attribute set`);
    }
    
    // Validate mechanism compatibility
    try {
      validateMechanismForKey(this.config.defaultMechanism, keyInfo.keyType);
    } catch (error) {
      if (error instanceof MechanismMismatchError) {
        throw new Error(
          `Default mechanism ${error.requestedMechanism} not compatible with key type ${CKK[keyInfo.keyType]}. ` +
          `Supported: ${error.supportedMechanisms.map(m => `0x${m.toString(16)}`).join(', ')}`
        );
      }
      throw error;
    }
    
    return keyInfo;
  }

  private async findKey(session: SessionHandle, label: string, id?: Buffer): Promise<KeyInfo | null> {
    const template: any = {
      class: CKO.PRIVATE_KEY,
      label,
      token: true,
      sign: true,
    };
    
    if (id) {
      template.id = id;
    }
    
    const objects = await this.adapter.findObjects(session, template, 1);
    
    if (objects.length === 0) {
      return null;
    }
    
    const keyHandle = objects[0];
    const attributes = await this.adapter.getAttributeValue(session, keyHandle, [
      0x00000000, 0x00000100, 0x00000003, 0x00000102, 0x00000121,
      0x00000162, 0x00000108, 0x00000109, 0x00000104, 0x00000105,
      0x00000106, 0x00000107, 0x0000010A,
    ]);
    
    return {
      handle: keyHandle,
      label: attributes[0x00000003] as string,
      id: attributes[0x00000102] as Buffer,
      keyType: attributes[0x00000100] as CKK,
      keySize: attributes[0x00000121] as number,
      extractable: attributes[0x00000162] as boolean,
      sign: attributes[0x00000108] as boolean,
      verify: attributes[0x00000109] as boolean,
      decrypt: attributes[0x00000105] as boolean,
      wrap: attributes[0x00000106] as boolean,
      unwrap: attributes[0x00000107] as boolean,
      derive: attributes[0x0000010A] as boolean,
    };
  }

  private ensureInitialized(): void {
    if (!this.initialized) {
      throw new Error('Signing service not initialized. Call initialize() first.');
    }
  }

  getConfig(): Readonly<ServiceConfig> {
    return { ...this.config };
  }

  isInitialized(): boolean {
    return this.initialized;
  }
}
```

### src/index.ts

```typescript
/**
 * PKCS#11 Signing Service - Main Entry Point
 * 
 * A production-ready signing service that uses PKCS#11 to interface with
 * Hardware Security Modules (HSMs) or software tokens without exporting private keys.
 */

import { SigningService } from './services/SigningService';
import { RealPkcs11Adapter } from './adapters/RealPkcs11Adapter';
import { MockPkcs11Adapter } from './adapters/MockPkcs11Adapter';
import { ServiceConfig, MechanismType, CKM } from './types';
import { Pkcs11Adapter } from './adapters/Pkcs11Adapter';
import pino from 'pino';

export { SigningService } from './services/SigningService';
export { TokenManager } from './services/TokenManager';
export { SessionManager } from './services/SessionManager';
export { CsrGenerator } from './services/CsrGenerator';
export { RealPkcs11Adapter } from './adapters/RealPkcs11Adapter';
export { MockPkcs11Adapter } from './adapters/MockPkcs11Adapter';
export { Pkcs11Adapter } from './adapters/Pkcs11Adapter';
export * from './types';
export * from './errors';
export * from './utils/mechanism';
export * from './utils/pin';

// Default logger
export const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  transport: process.env.NODE_ENV !== 'production' ? {
    target: 'pino-pretty',
    options: { colorize: true }
  } : undefined
});

/**
 * Create a signing service with real PKCS#11 backend
 */
export function createSigningService(config?: Partial<ServiceConfig>): SigningService {
  const adapter = new RealPkcs11Adapter(logger.child({ component: 'pkcs11' }));
  return new SigningService(adapter, config);
}

/**
 * Create a signing service with mock PKCS#11 backend (for testing)
 */
export function createMockSigningService(config?: Partial<ServiceConfig>): SigningService {
  const adapter = new MockPkcs11Adapter(logger.child({ component: 'mock-pkcs11' }));
  return new SigningService(adapter, config);
}

/**
 * Create a signing service with custom adapter (for advanced use cases)
 */
export function createCustomSigningService(adapter: Pkcs11Adapter, config?: Partial<ServiceConfig>): SigningService {
  return new SigningService(adapter, config);
}

/**
 * Parse mechanism string to MechanismType
 */
export function parseMechanism(name: string): MechanismType {
  const upper = name.toUpperCase();
  const mechanismMap: Record<string, MechanismType> = {
    'CKM_RSA_PKCS': CKM.RSA_PKCS,
    'CKM_SHA256_RSA_PKCS': CKM.SHA256_RSA_PKCS,
    'CKM_SHA384_RSA_PKCS': CKM.SHA384_RSA_PKCS,
    'CKM_SHA512_RSA_PKCS': CKM.SHA512_RSA_PKCS,
    'CKM_SHA256_RSA_PKCS_PSS': CKM.SHA256_RSA_PKCS_PSS,
    'CKM_SHA384_RSA_PKCS_PSS': CKM.SHA384_RSA_PKCS_PSS,
    'CKM_SHA512_RSA_PKCS_PSS': CKM.SHA512_RSA_PKCS_PSS,
    'CKM_ECDSA': CKM.ECDSA,
    'CKM_ECDSA_SHA256': CKM.ECDSA_SHA256,
    'CKM_ECDSA_SHA384': CKM.ECDSA_SHA384,
    'CKM_ECDSA_SHA512': CKM.ECDSA_SHA512,
  };
  
  if (mechanismMap[upper]) return mechanismMap[upper];
  if (upper.startsWith('0X')) return parseInt(upper, 16) as MechanismType;
  
  throw new Error(`Unknown mechanism: ${name}`);
}

// Re-export constants for convenience
export { CKK, CKM, CKO, CKF, CKU, CKR } from './types';

// CLI support
if (require.main === module) {
  (async () => {
    try {
      const service = createSigningService();
      await service.initialize();
      
      const health = await service.healthCheck();
      console.log('Health check:', JSON.stringify(health, null, 2));
      
      const keys = await service.listKeys();
      console.log('Available keys:', keys.map(k => ({
        label: k.label,
        id: k.id.toString('hex'),
        type: CKK[k.keyType],
        size: k.keySize,
      })));
      
      // Example sign
      const data = Buffer.from('Hello, PKCS#11!');
      const result = await service.sign({ data });
      console.log('Signature:', result.signature.toString('base64'));
      
      await service.shutdown();
    } catch (error) {
      console.error('Error:', error);
      process.exit(1);
    }
  })();
}
```

## Tests

### tests/mock/mockSetup.ts

```typescript
/**
 * Mock setup for unit tests
 */

import { MockPkcs11Adapter } from '../../src/adapters/MockPkcs11Adapter';
import { Pkcs11Adapter } from '../../src/adapters/Pkcs11Adapter';

// Global mock adapter instance for tests
let globalMockAdapter: MockPkcs11Adapter | null = null;

export function getMockAdapter(): MockPkcs11Adapter {
  if (!globalMockAdapter) {
    globalMockAdapter = new MockPkcs11Adapter();
  }
  return globalMockAdapter;
}

export function resetMockAdapter(): void {
  if (globalMockAdapter) {
    // Clean up
    globalMockAdapter.finalize().catch(() => {});
  }
  globalMockAdapter = new MockPkcs11Adapter();
}

export function setMockPin(pin: string): void {
  const adapter = getMockAdapter();
  adapter.setPin(pin);
}

export function setMockSoPin(pin: string): void {
  const adapter = getMockAdapter();
  adapter.setSoPin(pin);
}

// Mock the RealPkcs11Adapter for testing
jest.mock('../../src/adapters/RealPkcs11Adapter', () => {
  return {
    RealPkcs11Adapter: jest.fn().mockImplementation(() => getMockAdapter()),
  };
});
```

### tests/unit/SigningService.test.ts

```typescript
/**
 * Unit tests for SigningService using MockPkcs11Adapter
 */

import { createMockSigningService } from '../../src';
import { SignRequest, CsrRequest, CKM, CKK } from '../../src/types';
import { KeyNotFoundError, MechanismMismatchError } from '../../src/errors';
import { getMockAdapter, resetMockAdapter, setMockPin } from '../mock/mockSetup';

describe('SigningService', () => {
  let service: ReturnType<typeof createMockSigningService>;
  let mockAdapter: ReturnType<typeof getMockAdapter>;

  beforeEach(() => {
    resetMockAdapter();
    mockAdapter = getMockAdapter();
    setMockPin('1234');
    
    service = createMockSigningService({
      keyLabel: 'signing-key',
      keyId: Buffer.from('01020304', 'hex'),
      defaultMechanism: CKM.SHA256_RSA_PKCS,
    });
  });

  afterEach(async () => {
    if (service.isInitialized()) {
      await service.shutdown();
    }
  });

  describe('initialize', () => {
    it('should initialize successfully with valid config', async () => {
      await service.initialize();
      expect(service.isInitialized()).toBe(true);
    });

    it('should fail without library path', async () => {
      const svc = createMockSigningService({
        libPath: '',
        keyLabel: 'test-key',
      });
      await expect(svc.initialize()).rejects.toThrow('PKCS#11 library path not configured');
    });

    it('should fail without key label', async () => {
      const svc = createMockSigningService({
        libPath: '/mock/path',
        keyLabel: '',
      });
      await expect(svc.initialize()).rejects.toThrow('Key label not configured');
    });
  });

  describe('sign', () => {
    beforeEach(async () => {
      await service.initialize();
    });

    it('should sign data with default key and mechanism', async () => {
      const data = Buffer.from('test data to sign');
      const result = await service.sign({ data });
      
      expect(result.signature).toBeInstanceOf(Buffer);
      expect(result.signature.length).toBeGreaterThan(0);
      expect(result.mechanism).toBe(CKM.SHA256_RSA_PKCS);
      expect(result.keyLabel).toBe('signing-key');
      expect(result.keyId).toEqual(Buffer.from('01020304', 'hex'));
    });

    it('should sign with explicit mechanism', async () => {
      const data = Buffer.from('test data');
      const result = await service.sign({ 
        data, 
        mechanism: CKM.RSA_PKCS 
      });
      
      expect(result.mechanism).toBe(CKM.RSA_PKCS);
    });

    it('should sign with different key', async () => {
      // Add another key to mock
      mockAdapter.addMockKeyPair(
        mockAdapter['slots'].get(0)!,
        'other-key',
        Buffer.from('11111111', 'hex'),
        CKK.RSA,
        2048
      );
      
      const data = Buffer.from('test data');
      const result = await service.sign({ 
        data, 
        keyLabel: 'other-key',
        keyId: Buffer.from('11111111', 'hex'),
      });
      
      expect(result.keyLabel).toBe('other-key');
    });

    it('should throw KeyNotFoundError for non-existent key', async () => {
      const data = Buffer.from('test data');
      await expect(service.sign({ 
        data, 
        keyLabel: 'non-existent',
      })).rejects.toThrow(KeyNotFoundError);
    });

    it('should throw MechanismMismatchError for incompatible mechanism', async () => {
      const data = Buffer.from('test data');
      await expect(service.sign({ 
        data, 
        mechanism: CKM.ECDSA, // EC mechanism for RSA key
      })).rejects.toThrow(MechanismMismatchError);
    });
  });

  describe('signMulti', () => {
    beforeEach(async () => {
      await service.initialize();
    });

    it('should sign multiple requests concurrently', async () => {
      const requests: SignRequest[] = [
        { data: Buffer.from('data 1') },
        { data: Buffer.from('data 2') },
        { data: Buffer.from('data 3') },
      ];
      
      const results = await service.signMulti(requests);
      
      expect(results).toHaveLength(3);
      results.forEach((result, i) => {
        expect(result.signature).toBeInstanceOf(Buffer);
        expect(result.keyLabel).toBe('signing-key');
      });
    });
  });

  describe('createCsr', () => {
    beforeEach(async () => {
      await service.initialize();
    });

    it('should generate a valid CSR', async () => {
      const request: CsrRequest = {
        subject: {
          commonName: 'test.example.com',
          organization: 'Test Org',
          country: 'US',
        },
        keyLabel: 'signing-key',
        keyId: Buffer.from('01020304', 'hex'),
      };
      
      const result = await service.createCsr(request);
      
      expect(result.csrPem).toContain('-----BEGIN CERTIFICATE REQUEST-----');
      expect(result.csrDer).toBeInstanceOf(Buffer);
      expect(result.publicKeyPem).toContain('-----BEGIN PUBLIC KEY-----');
      expect(result.keyLabel).toBe('signing-key');
    });

    it('should generate CSR with extensions', async () => {
      const request: CsrRequest = {
        subject: {
          commonName: 'test.example.com',
        },
        keyLabel: 'signing-key',
        extensions: [
          {
            oid: '2.5.29.17', // subjectAltName
            critical: false,
            value: [{ type: 2, value: 'test.example.com' }, { type: 2, value: 'www.test.example.com' }],
          },
          {
            oid: '2.5.29.15', // keyUsage
            critical: true,
            value: { digitalSignature: true, keyEncipherment: true },
          },
        ],
      };
      
      const result = await service.createCsr(request);
      expect(result.csrPem).toContain('-----BEGIN CERTIFICATE REQUEST-----');
    });
  });

  describe('getKeyInfo', () => {
    beforeEach(async () => {
      await service.initialize();
    });

    it('should return key info for default key', async () => {
      const info = await service.getKeyInfo();
      
      expect(info.label).toBe('signing-key');
      expect(info.id).toEqual(Buffer.from('01020304', 'hex'));
      expect(info.keyType).toBe(CKK.RSA);
      expect(info.keySize).toBe(2048);
      expect(info.sign).toBe(true);
    });

    it('should return key info for EC key', async () => {
      const info = await service.getKeyInfo('ec-signing-key', Buffer.from('05060708', 'hex'));
      
      expect(info.label).toBe('ec-signing-key');
      expect(info.keyType).toBe(CKK.EC);
      expect(info.keySize).toBe(256);
    });

    it('should throw for non-existent key', async () => {
      await expect(service.getKeyInfo('non-existent')).rejects.toThrow(KeyNotFoundError);
    });
  });

  describe('listKeys', () => {
    beforeEach(async () => {
      await service.initialize();
    });

    it('should list all signing keys', async () => {
      const keys = await service.listKeys();
      
      expect(keys.length).toBeGreaterThanOrEqual(2);
      const labels = keys.map(k => k.label).sort();
      expect(labels).toContain('signing-key');
      expect(labels).toContain('ec-signing-key');
    });

    it('should filter by key type', async () => {
      const rsaKeys = await service.listKeys(CKK.RSA);
      const ecKeys = await service.listKeys(CKK.EC);
      
      expect(rsaKeys.every(k => k.keyType === CKK.RSA)).toBe(true);
      expect(ecKeys.every(k => k.keyType === CKK.EC)).toBe(true);
    });
  });

  describe('healthCheck', () => {
    beforeEach(async () => {
      await service.initialize();
    });

    it('should return healthy status', async () => {
      const health = await service.healthCheck();
      
      expect(health.healthy).toBe(true);
      expect(health.details.token).toBeDefined();
      expect(health.details.sessionPool).toBeDefined();
      expect(health.details.key).toBeDefined();
    });
  });

  describe('shutdown', () => {
    it('should shutdown cleanly', async () => {
      await service.initialize();
      await service.shutdown();
      expect(service.isInitialized()).toBe(false);
    });
  });
});
```

### tests/unit/SessionManager.test.ts

```typescript
/**
 * Unit tests for SessionManager
 */

import { MockPkcs11Adapter } from '../../src/adapters/MockPkcs11Adapter';
import { SessionManager } from '../../src/services/SessionManager';
import { getMockAdapter, resetMockAdapter, setMockPin } from '../mock/mockSetup';
import { CKU } from '../../src/types';

describe('SessionManager', () => {
  let adapter: MockPkcs11Adapter;
  let sessionManager: SessionManager;

  beforeEach(() => {
    resetMockAdapter();
    adapter = getMockAdapter();
    setMockPin('1234');
    sessionManager = new SessionManager(adapter, { maxSize: 3 });
  });

  afterEach(async () => {
    await sessionManager.shutdown();
  });

  it('should create and reuse sessions', async () => {
    const session1 = await sessionManager.acquireSession(0, '1234');
    expect(sessionManager.getPoolStats(0).total).toBe(1);
    
    await sessionManager.releaseSession(session1);
    expect(sessionManager.getPoolStats(0).available).toBe(1);
    
    const session2 = await sessionManager.acquireSession(0, '1234');
    expect(session2.handle).toBe(session1.handle); // Same session reused
    expect(sessionManager.getPoolStats(0).total).toBe(1);
  });

  it('should create multiple sessions up to pool size', async () => {
    const sessions = [];
    for (let i = 0; i < 3; i++) {
      sessions.push(await sessionManager.acquireSession(0, '1234'));
    }
    expect(sessionManager.getPoolStats(0).total).toBe(3);
    expect(sessionManager.getPoolStats(0).inUse).toBe(3);
    
    // Release all
    for (const s of sessions) {
      await sessionManager.releaseSession(s);
    }
    expect(sessionManager.getPoolStats(0).available).toBe(3);
  });

  it('should wait for session when pool exhausted', async () => {
    const sessions = [];
    for (let i = 0; i < 3; i++) {
      sessions.push(await sessionManager.acquireSession(0, '1234'));
    }
    
    // This should wait and eventually timeout
    const promise = sessionManager.acquireSession(0, '1234');
    
    // Release one session
    setTimeout(() => sessionManager.releaseSession(sessions[0]), 100);
    
    const session = await promise;
    expect(session).toBeDefined();
  });

  it('should login and logout sessions', async () => {
    const session = await sessionManager.acquireSession(0);
    expect((await adapter.getSessionInfo(session)).state).toBe(0); // Not logged in
    
    await sessionManager.loginSession(session, '1234');
    expect((await adapter.getSessionInfo(session)).state).toBe(1); // Logged in
    
    await sessionManager.logoutSession(session);
    expect((await adapter.getSessionInfo(session)).state).toBe(0); // Logged out
    
    await sessionManager.releaseSession(session);
  });

  it('should destroy sessions', async () => {
    const session = await sessionManager.acquireSession(0, '1234');
    expect(sessionManager.getPoolStats(0).total).toBe(1);
    
    await sessionManager.destroySession(session);
    expect(sessionManager.getPoolStats(0).total).toBe(0);
  });

  it('should close all sessions for a slot', async () => {
    await sessionManager.acquireSession(0, '1234');
    await sessionManager.acquireSession(0, '1234');
    expect(sessionManager.getPoolStats(0).total).toBe(2);
    
    await sessionManager.closeAllSessions(0);
    expect(sessionManager.getPoolStats(0).total).toBe(0);
  });
});
```

### tests/unit/TokenManager.test.ts

```typescript
/**
 * Unit tests for TokenManager
 */

import { MockPkcs11Adapter } from '../../src/adapters/MockPkcs11Adapter';
import { TokenManager } from '../../src/services/TokenManager';
import { getMockAdapter, resetMockAdapter } from '../mock/mockSetup';
import { TokenNotFoundError } from '../../src/errors';

describe('TokenManager', () => {
  let adapter: MockPkcs11Adapter;
  let tokenManager: TokenManager;

  beforeEach(() => {
    resetMockAdapter();
    adapter = getMockAdapter();
    tokenManager = new TokenManager(adapter);
  });

  it('should enumerate slots', async () => {
    const slots = await tokenManager.enumerateSlots(true);
    expect(slots.length).toBeGreaterThan(0);
    expect(slots[0].tokenPresent).toBe(true);
  });

  it('should enumerate tokens', async () => {
    const tokens = await tokenManager.enumerateTokens();
    expect(tokens.length).toBeGreaterThan(0);
    expect(tokens[0].tokenInfo.label).toBe('mock-token');
  });

  it('should select token by default criteria', async () => {
    const token = await tokenManager.selectToken({});
    expect(token.slotIndex).toBe(0);
    expect(token.tokenInfo.label).toBe('mock-token');
  });

  it('should select token by label', async () => {
    adapter.addSlot(1, { label: 'token-1' });
    adapter.addSlot(2, { label: 'token-2' });
    
    const token = await tokenManager.selectToken({ tokenLabel: 'token-2' });
    expect(token.slotIndex).toBe(2);
    expect(token.tokenInfo.label).toBe('token-2');
  });

  it('should throw TokenNotFoundError for non-existent label', async () => {
    await expect(tokenManager.selectToken({ tokenLabel: 'non-existent' }))
      .rejects.toThrow(TokenNotFoundError);
  });

  it('should filter by requirements', async () => {
    // Add a token without user PIN initialized
    adapter.addSlot(1, { 
      label: 'no-pin-token',
      flags: 0x00000007, // No USER_PIN_INITIALIZED flag
    });
    
    const token = await tokenManager.selectToken({ 
      requireUserPin: true 
    });
    expect(token.tokenInfo.label).toBe('mock-token'); // Should skip the one without PIN
  });

  it('should get mechanism list', async () => {
    const mechanisms = await tokenManager.getMechanismList(0);
    expect(mechanisms).toContain(0x00000001); // CKM_RSA_PKCS
    expect(mechanisms).toContain(0x00000040); // CKM_SHA256_RSA_PKCS
  });

  it('should check token health', async () => {
    const health = await tokenManager.checkTokenHealth(0);
    expect(health.healthy).toBe(true);
    expect(health.issues).toHaveLength(0);
  });
});
```

### tests/unit/CsrGenerator.test.ts

```typescript
/**
 * Unit tests for CsrGenerator
 */

import { MockPkcs11Adapter } from '../../src/adapters/MockPkcs11Adapter';
import { CsrGenerator } from '../../src/services/CsrGenerator';
import { SessionManager } from '../../src/services/SessionManager';
import { getMockAdapter, resetMockAdapter, setMockPin } from '../mock/mockSetup';
import { CsrRequest, CKM, CKK } from '../../src/types';
import * as forge from 'node-forge';

describe('CsrGenerator', () => {
  let adapter: MockPkcs11Adapter;
  let sessionManager: SessionManager;
  let csrGenerator: CsrGenerator;

  beforeEach(async () => {
    resetMockAdapter();
    adapter = getMockAdapter();
    setMockPin('1234');
    sessionManager = new SessionManager(adapter);
    csrGenerator = new CsrGenerator(adapter);
  });

  afterEach(async () => {
    await sessionManager.shutdown();
  });

  it('should generate CSR for RSA key', async () => {
    const session = await sessionManager.acquireSession(0, '1234');
    
    try {
      const request: CsrRequest = {
        subject: {
          commonName: 'test.example.com',
          organization: 'Test Org',
          country: 'US',
        },
        keyLabel: 'signing-key',
        keyId: Buffer.from('01020304', 'hex'),
        mechanism: CKM.SHA256_RSA_PKCS,
      };
      
      const result = await csrGenerator.generateCsr(session, request);
      
      expect(result.csrPem).toContain('-----BEGIN CERTIFICATE REQUEST-----');
      expect(result.csrDer).toBeInstanceOf(Buffer);
      expect(result.publicKeyPem).toContain('-----BEGIN PUBLIC KEY-----');
      expect(result.keyLabel).toBe('signing-key');
      
      // Verify CSR can be parsed
      const csr = forge.pki.certificationRequestFromPem(result.csrPem);
      expect(csr.subject.getField('CN').value).toBe('test.example.com');
      expect(csr.subject.getField('O').value).toBe('Test Org');
      expect(csr.subject.getField('C').value).toBe('US');
    } finally {
      await sessionManager.releaseSession(session);
    }
  });

  it('should generate CSR for EC key', async () => {
    const session = await sessionManager.acquireSession(0, '1234');
    
    try {
      const request: CsrRequest = {
        subject: {
          commonName: 'ec-test.example.com',
        },
        keyLabel: 'ec-signing-key',
        keyId: Buffer.from('05060708', 'hex'),
        mechanism: CKM.ECDSA_SHA256,
      };
      
      const result = await csrGenerator.generateCsr(session, request);
      
      expect(result.csrPem).toContain('-----BEGIN CERTIFICATE REQUEST-----');
      expect(result.keyLabel).toBe('ec-signing-key');
    } finally {
      await sessionManager.releaseSession(session);
    }
  });

  it('should include extensions in CSR', async () => {
    const session = await sessionManager.acquireSession(0, '1234');
    
    try {
      const request: CsrRequest = {
        subject: {
          commonName: 'test.example.com',
        },
        keyLabel: 'signing-key',
        extensions: [
          {
            oid: '2.5.29.17', // subjectAltName
            critical: false,
            value: [{ type: 2, value: 'test.example.com' }],
          },
        ],
      };
      
      const result = await csrGenerator.generateCsr(session, request);
      
      const csr = forge.pki.certificationRequestFromPem(result.csrPem);
      const extReq = csr.getAttribute('extensionRequest');
      expect(extReq).toBeDefined();
    } finally {
      await sessionManager.releaseSession(session);
    }
  });
});
```

## Examples

### examples/basic-sign.ts

```typescript
/**
 * Example: Basic signing operation
 * 
 * Run with: npm run example:sign
 * Requires: PKCS11_LIB_PATH, PKCS11_PIN, PKCS11_KEY_LABEL environment variables
 */

import { createSigningService, parseMechanism } from '../src';

async function main() {
  // Configuration from environment variables
  const service = createSigningService({
    libPath: process.env.PKCS11_LIB_PATH,
    pin: process.env.PKCS11_PIN,
    slotIndex: process.env.PKCS11_SLOT_INDEX ? parseInt(process.env.PKCS11_SLOT_INDEX) : undefined,
    tokenLabel: process.env.PKCS11_TOKEN_LABEL,
    keyLabel: process.env.PKCS11_KEY_LABEL,
    keyId: process.env.PKCS11_KEY_ID ? Buffer.from(process.env.PKCS11_KEY_ID, 'hex') : undefined,
    defaultMechanism: process.env.PKCS11_DEFAULT_MECHANISM 
      ? parseMechanism(process.env.PKCS11_DEFAULT_MECHANISM)
      : undefined,
  });

  try {
    console.log('Initializing signing service...');
    await service.initialize();
    console.log('Service initialized successfully');

    // Health check
    const health = await service.healthCheck();
    console.log('Health check:', JSON.stringify(health, null, 2));

    // List available keys
    const keys = await service.listKeys();
    console.log('\nAvailable signing keys:');
    keys.forEach(key => {
      console.log(`  - ${key.label} (ID: ${key.id.toString('hex')}, Type: ${key.keyType === 0 ? 'RSA' : 'EC'}, Size: ${key.keySize} bits)`);
    });

    // Sign some data
    const data = Buffer.from('Hello, PKCS#11 Signing Service!');
    console.log('\nSigning data:', data.toString());
    
    const result = await service.sign({ data });
    console.log('Signature (base64):', result.signature.toString('base64'));
    console.log('Mechanism:', result.mechanism.toString(16));
    console.log('Key:', result.keyLabel);

    // Sign with explicit mechanism
    const result2 = await service.sign({ 
      data, 
      mechanism: parseMechanism('CKM_RSA_PKCS') 
    });
    console.log('\nSignature with CKM_RSA_PKCS (base64):', result2.signature.toString('base64'));

  } catch (error) {
    console.error('Error:', error);
    process.exit(1);
  } finally {
    await service.shutdown();
    console.log('\nService shut down');
  }
}

main();
```

### examples/create-csr.ts

```typescript
/**
 * Example: Create a PKCS#10 Certificate Signing Request
 * 
 * Run with: npm run example:csr
 * Requires: PKCS11_LIB_PATH, PKCS11_PIN, PKCS11_KEY_LABEL environment variables
 */

import { createSigningService, parseMechanism } from '../src';

async function main() {
  const service = createSigningService({
    libPath: process.env.PKCS11_LIB_PATH,
    pin: process.env.PKCS11_PIN,
    slotIndex: process.env.PKCS11_SLOT_INDEX ? parseInt(process.env.PKCS11_SLOT_INDEX) : undefined,
    tokenLabel: process.env.PKCS11_TOKEN_LABEL,
    keyLabel: process.env.PKCS11_KEY_LABEL,
    keyId: process.env.PKCS11_KEY_ID ? Buffer.from(process.env.PKCS11_KEY_ID, 'hex') : undefined,
  });

  try {
    console.log('Initializing signing service...');
    await service.initialize();
    console.log('Service initialized successfully');

    // Create CSR
    const csr = await service.createCsr({
      subject: {
        commonName: 'api.example.com',
        organization: 'Example Corp',
        organizationalUnit: 'Engineering',
        country: 'US',
        state: 'California',
        locality: 'San Francisco',
        emailAddress: 'admin@example.com',
      },
      keyLabel: process.env.PKCS11_KEY_LABEL || 'signing-key',
      keyId: process.env.PKCS11_KEY_ID ? Buffer.from(process.env.PKCS11_KEY_ID, 'hex') : undefined,
      mechanism: parseMechanism('CKM_SHA256_RSA_PKCS'),
      extensions: [
        {
          oid: '2.5.29.17', // subjectAltName
          critical: false,
          value: [
            { type: 2, value: 'api.example.com' },
            { type: 2, value: 'www.example.com' },
            { type: 7, value: '192.168.1.100' }, // IP address
          ],
        },
        {
          oid: '2.5.29.15', // keyUsage
          critical: true,
          value: {
            digitalSignature: true,
            keyEncipherment: true,
            keyCertSign: false,
            cRLSign: false,
          },
        },
        {
          oid: '2.5.29.37', // extendedKeyUsage
          critical: false,
          value: [
            { type: '1.3.6.1.5.5.7.3.1' }, // serverAuth
            { type: '1.3.6.1.5.5.7.3.2' }, // clientAuth
          ],
        },
      ],
    });

    console.log('\n--- CSR (PEM) ---');
    console.log(csr.csrPem);
    
    console.log('\n--- Public Key (PEM) ---');
    console.log(csr.publicKeyPem);
    
    console.log('\n--- CSR Details ---');
    console.log('Key Label:', csr.keyLabel);
    console.log('Key ID:', csr.keyId.toString('hex'));
    console.log('CSR DER Length:', csr.csrDer.length, 'bytes');

    // Save to files
    const fs = await import('fs/promises');
    await fs.writeFile('csr.pem', csr.csrPem);
    await fs.writeFile('public-key.pem', csr.publicKeyPem);
    console.log('\nFiles saved: csr.pem, public-key.pem');

  } catch (error) {
    console.error('Error:', error);
    process.exit(1);
  } finally {
    await service.shutdown();
  }
}

main();
```

### examples/enumerate-tokens.ts

```typescript
/**
 * Example: Enumerate slots and tokens
 * 
 * Run with: npm run example:enumerate
 * Requires: PKCS11_LIB_PATH environment variable
 */

import { createSigningService, RealPkcs11Adapter, TokenManager } from '../src';

async function main() {
  const libPath = process.env.PKCS11_LIB_PATH;
  if (!libPath) {
    console.error('PKCS11_LIB_PATH environment variable required');
    process.exit(1);
  }

  const adapter = new RealPkcs11Adapter();
  const tokenManager = new TokenManager(adapter);

  try {
    console.log('Initializing PKCS#11 library...');
    await adapter.initialize(libPath);
    
    const libInfo = await adapter.getLibraryInfo();
    console.log('\nLibrary Info:');
    console.log(`  Manufacturer: ${libInfo.manufacturerId}`);
    console.log(`  Description: ${libInfo.libraryDescription}`);
    console.log(`  Version: ${libInfo.libraryVersion.major}.${libInfo.libraryVersion.minor}`);
    console.log(`  Cryptoki Version: ${libInfo.cryptokiVersion.major}.${libInfo.cryptokiVersion.minor}`);

    // Enumerate slots
    console.log('\nEnumerating slots...');
    const slots = await tokenManager.enumerateSlots(false);
    
    for (const slot of slots) {
      console.log(`\nSlot ${slot.slotIndex}:`);
      console.log(`  Description: ${slot.slotDescription}`);
      console.log(`  Manufacturer: ${slot.manufacturerId}`);
      console.log(`  Token Present: ${slot.tokenPresent ? 'Yes' : 'No'}`);
      
      if (slot.tokenPresent) {
        try {
          const tokenInfo = await tokenManager.getTokenInfo(slot.slotIndex);
          console.log(`  Token Label: ${tokenInfo.label}`);
          console.log(`  Token Model: ${tokenInfo.model}`);
          console.log(`  Serial Number: ${tokenInfo.serialNumber}`);
          console.log(`  Max Sessions: ${tokenInfo.maxSessionCount}`);
          console.log(`  Active Sessions: ${tokenInfo.sessionCount}`);
          console.log(`  Max RW Sessions: ${tokenInfo.maxRwSessionCount}`);
          console.log(`  Active RW Sessions: ${tokenInfo.rwSessionCount}`);
          console.log(`  PIN Length: ${tokenInfo.minPinLen}-${tokenInfo.maxPinLen}`);
          console.log(`  Free Public Memory: ${tokenInfo.freePublicMemory} bytes`);
          console.log(`  Free Private Memory: ${tokenInfo.freePrivateMemory} bytes`);
          
          // Get mechanism list
          const mechanisms = await tokenManager.getMechanismList(slot.slotIndex);
          console.log(`  Supported Mechanisms (${mechanisms.length}):`);
          mechanisms.forEach(m => {
            console.log(`    - 0x${m.toString(16).toUpperCase().padStart(8, '0')}`);
          });
        } catch (error) {
          console.log(`  Error reading token: ${error}`);
        }
      }
    }

    // Wait for token event (demo)
    console.log('\nWaiting for slot event (5 seconds)...');
    const event = await tokenManager.waitForToken(0, 5000);
    if (event) {
      console.log('Token event detected!');
    } else {
      console.log('No token events (timeout)');
    }

  } catch (error) {
    console.error('Error:', error);
    process.exit(1);
  } finally {
    await adapter.finalize();
    console.log('\nLibrary finalized');
  }
}

main();
```

## Documentation

### PKCS#11 MECHANISMS USED

| Mechanism Constant | Value | Description | Key Types | Hash Algorithm |
|---|---|---|---|---|
| `CKM_RSA_PKCS` | 0x00000001 | RSA PKCS#1 v1.5 (raw) | RSA | None (external) |
| `CKM_SHA256_RSA_PKCS` | 0x00000040 | RSA PKCS#1 v1.5 with SHA-256 | RSA | SHA-256 (internal) |
| `CKM_SHA384_RSA_PKCS` | 0x00000041 | RSA PKCS#1 v1.5 with SHA-384 | RSA | SHA-384 (internal) |
| `CKM_SHA512_RSA_PKCS` | 0x00000042 | RSA PKCS#1 v1.5 with SHA-512 | RSA | SHA-512 (internal) |
| `CKM_SHA256_RSA_PKCS_PSS` | 0x00000043 | RSA PSS with SHA-256 | RSA | SHA-256 (internal) |
| `CKM_SHA384_RSA_PKCS_PSS` | 0x00000044 | RSA PSS with SHA-384 | RSA | SHA-384 (internal) |
| `CKM_SHA512_RSA_PKCS_PSS` | 0x00000045 | RSA PSS with SHA-512 | RSA | SHA-512 (internal) |
| `CKM_ECDSA` | 0x00001041 | ECDSA (raw) | EC | None (external) |
| `CKM_ECDSA_SHA256` | 0x00001042 | ECDSA with SHA-256 | EC | SHA-256 (internal) |
| `CKM_ECDSA_SHA384` | 0x00001043 | ECDSA with SHA-384 | EC | SHA-384 (internal) |
| `CKM_ECDSA_SHA512` | 0x00001044 | ECDSA with SHA-512 | EC | SHA-512 (internal) |

### PKCS#11 ATTRIBUTES USED

| Attribute | Constant | Purpose |
|---|---|---|
| `CKA_CLASS` | 0x00000000 | Object class (key, cert, data) |
| `CKA_KEY_TYPE` | 0x00000100 | Key type (RSA, EC, etc.) |
| `CKA_LABEL` | 0x00000003 | Human-readable label |
| `CKA_ID` | 0x00000102 | Key identifier (bytes) |
| `CKA_TOKEN` | 0x00000001 | Token object (persistent) |
| `CKA_PRIVATE` | 0x00000002 | Requires login |
| `CKA_SENSITIVE` | 0x00000103 | Cannot be revealed in plaintext |
| `CKA_SIGN` | 0x00000108 | Key can sign |
| `CKA_VERIFY` | 0x00000109 | Key can verify |
| `CKA_ENCRYPT` | 0x00000104 | Key can encrypt |
| `CKA_DECRYPT` | 0x00000105 | Key can decrypt |
| `CKA_WRAP` | 0x00000106 | Key can wrap |
| `CKA_UNWRAP` | 0x00000107 | Key can unwrap |
| `CKA_DERIVE` | 0x0000010A | Key can derive |
| `CKA_EXTRACTABLE` | 0x00000162 | Key can be extracted |
| `CKA_NEVER_EXTRACTABLE` | 0x00000164 | Key never extractable |
| `CKA_ALWAYS_SENSITIVE` | 0x00000165 | Key always sensitive |
| `CKA_MODULUS_BITS` | 0x00000121 | RSA key size |
| `CKA_PRIME_BITS` | 0x00000133 | EC prime size |
| `CKA_MODULUS` | 0x00000120 | RSA modulus |
| `CKA_PUBLIC_EXPONENT` | 0x00000122 | RSA public exponent |
| `CKA_EC_PARAMS` | 0x00000180 | EC domain parameters (OID) |
| `CKA_EC_POINT` | 0x00000181 | EC public point |

### NPM PACKAGES USED

| Package | Version | Purpose |
|---|---|---|
| `pkcs11js` | ^1.3.0 | Native Node.js bindings for PKCS#11 |
| `node-forge` | ^1.3.1 | Pure JS crypto for CSR generation, ASN.1, PEM |
| `dotenv` | ^16.3.1 | Environment variable loading |
| `pino` | ^8.16.2 | Structured logging |
| `pino-pretty` | ^10.2.3 | Pretty logging for development |

## Setup Instructions

### 1. Install Dependencies

```bash
# System dependencies (Ubuntu/Debian)
sudo apt-get update && sudo apt-get install -y \
  build-essential \
  pkg-config \
  libssl-dev \
  softhsm2 \
  opensc \
  pcscd \
  libpcsclite-dev

# For macOS
brew install softhsm opensc pcsc-lite

# For AWS CloudHSM
# Follow AWS CloudHSM client installation guide

# Project dependencies
npm install
```

### 2. Configure SoftHSM2 (Software HSM for Testing)

```bash
# Initialize SoftHSM token
softhsm2-util --init-token --slot 0 --label "signing-token" --pin 1234 --so-pin 5678

# Generate RSA key pair
softhsm2-util --generate-key-pair --slot 0 --label "signing-key" --id 01020304 --bits 2048 --pin 1234

# Generate EC key pair
softhsm2-util --generate-key-pair --slot 0 --label "ec-signing-key" --id 05060708 --bits 256 --pin 1234

# Verify
softhsm2-util --show-slots
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your values
```

Example `.env` for SoftHSM2:
```bash
PKCS11_LIB_PATH=/usr/local/lib/softhsm/libsofthsm2.so
PKCS11_PIN=1234
PKCS11_SO_PIN=5678
PKCS11_SLOT_INDEX=0
PKCS11_TOKEN_LABEL=signing-token
PKCS11_KEY_LABEL=signing-key
PKCS11_KEY_ID=01020304
PKCS11_DEFAULT_MECHANISM=CKM_SHA256_RSA_PKCS
PKCS11_SESSION_POOL_SIZE=5
PKCS11_READ_ONLY_SESSION=true
LOG_LEVEL=info
```

### 4. Build and Test

```bash
# Build TypeScript
npm run build

# Run unit tests (no hardware required)
npm run test:unit

# Run all tests
npm run test

# Run examples
npm run example:enumerate
npm run example:sign
npm run example:csr
```

## Production Deployment

### Docker Example

```dockerfile
FROM node:20-alpine

# Install PKCS#11 libraries
RUN apk add --no-cache \
    softhsm \
    opensc \
    pcsc-lite \
    libpcsclite \
    make \
    g++ \
    python3

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY dist ./dist
COPY .env.example .env

# Initialize SoftHSM token at runtime
RUN softhsm2-util --init-token --slot 0 --label "signing-token" --pin 1234 --so-pin 5678 && \
    softhsm2-util --generate-key-pair --slot 0 --label "signing-key" --id 01020304 --bits 2048 --pin 1234

ENV PKCS11_LIB_PATH=/usr/lib/softhsm/libsofthsm2.so
ENV PKCS11_PIN=1234
ENV PKCS11_KEY_LABEL=signing-key
ENV PKCS11_KEY_ID=01020304

CMD ["node", "dist/index.js"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pkcs11-signing-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pkcs11-signing-service
  template:
    metadata:
      labels:
        app: pkcs11-signing-service
    spec:
      containers:
      - name: signing-service
        image: your-registry/pkcs11-signing-service:latest
        env:
        - name: PKCS11_LIB_PATH
          value: "/opt/cloudhsm/lib/libcloudhsm_pkcs11.so"
        - name: PKCS11_PIN
          valueFrom:
            secretKeyRef:
              name: hsm-credentials
              key: pin
        - name: PKCS11_KEY_LABEL
          value: "signing-key"
        - name: PKCS11_KEY_ID
          value: "01020304"
        volumeMounts:
        - name: cloudhsm
          mountPath: /opt/cloudhsm
        - name: pkcs11-config
          mountPath: /etc/cloudhsm
      volumes:
      - name: cloudhsm
        hostPath:
          path: /opt/cloudhsm
      - name: pkcs11-config
        configMap:
          name: cloudhsm-config
```

## Usage Examples

### Basic Signing

```typescript
import { createSigningService } from 'pkcs11-signing-service';

const service = createSigningService({
  libPath: '/usr/local/lib/softhsm/libsofthsm2.so',
  pin: '1234',
  keyLabel: 'signing-key',
  keyId: Buffer.from('01020304', 'hex'),
});

await service.initialize();

const result = await service.sign({
  data: Buffer.from('Document to sign'),
  mechanism: 0x00000040, // CKM_SHA256_RSA_PKCS
});

console.log('Signature:', result.signature.toString('base64'));

await service.shutdown();
```

### CSR Generation

```typescript
const csr = await service.createCsr({
  subject: {
    commonName: 'api.example.com',
    organization: 'Example Inc',
    country: 'US',
  },
  keyLabel: 'signing-key',
  mechanism: 0x00000040, // CKM_SHA256_RSA_PKCS
  extensions: [
    {
      oid: '2.5.29.17',
      critical: false,
      value: [{ type: 2, value: 'api.example.com' }],
    },
  ],
});

console.log(csr.csrPem);
```

### Concurrent Signing

```typescript
const requests = Array.from({ length: 100 }, (_, i) => ({
  data: Buffer.from(`Document ${i}`),
}));

const results = await service.signMulti(requests);
// Results processed with controlled concurrency (pool size)
```

## Error Handling

The service provides typed errors for different failure modes:

- `Pkcs11Error` - Base PKCS#11 error with error code and retryable flag
- `TokenNotFoundError` - Token/slot not found
- `KeyNotFoundError` - Key not found by label/ID
- `MechanismMismatchError` - Mechanism incompatible with key type
- `SessionError` - Session operation failed
- `ConfigurationError` - Invalid configuration
- `CsrGenerationError` - CSR creation failed

All PKCS#11 errors include the original PKCS#11 return code for precise debugging.
