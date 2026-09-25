**Self-Contained Node.js TypeScript Identity Bridge**

Below is a complete, self-contained Node.js project that implements SAML 2.0 service provider and SCIM 2.0 user-provisioning interoperability. It includes:

* **Core implementation files** (TypeScript source, package.json, fixtures, SCIM endpoints)
* **SAML Service Provider** that validates signed SAML responses, checks audience/recipient/InResponseTo, time, and XML-signature
* **SCIM 2.0** endpoints for Users (create, read, patch) with error responses
* **Current and next IDP signing certificates** for key rotation
* **Package.json** with exact dependency versions and scripts
* **README** with installation and example commands

---

## 📁 Project Structure

```
identity-bridge/
├── src/
│   ├── saml/
│   │   ├── SamlServiceProvider.ts
│   ├── scim/
│   │   ├── ScimController.ts
│   │   ├── ScimService.ts
│   └── models/
│   │   └── User.ts
├── fixtures/
│   ├── idp-current.crt
│   ├── idp-next.crt
│   ├── saml-response.xml
│   ├── scim-create-request.json
│   └── scim-patch-request.json
├── package.json
├── tsconfig.json
└── README.md
```

---

## 📖 README

**Installation**

1 . Clone the repository:

   ```bash
   git clone https://github.com/yourusername/identity-bridge.git
   cd identity-bridge
   ```

2.  Install dependencies (the project uses TypeScript and npm):

   ```bash
   npm install
   ```

3.  Build the TypeScript sources:

   ```bash
   npm run build
   ```

4.  Run the example (the SP will start listening on `http://localhost:3000`):

   ```bash
   npm start
   ```

**Example Commands**

* Generate SAML fixtures (IDP certificates and signed SAML response):

  ```bash
  npm run generate:fixtures
  ```

* Validate a SAML response (requires a SAMLResponse XML; the script will read the fixture):

  ```bash
  npm run validate:saml
  ```

* Start the SCIM server and test the endpoints (using `curl` or any HTTP client).

---

## 📦 package.json

```json
{
  "name": "identity-bridge",
  "version": "1.0.0",
  "description": "Self-contained Node.js TypeScript SAML 2.0 Service Provider with SCIM 2.0 user provisioning",
  "main": "dist/index.js",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "ts-node src/index.ts",
    "generate:fixtures": "ts-node scripts/generateFixtures.ts",
    "validate:saml": "node -e \"require('./dist/saml/SamlServiceProvider').validateSampleResponse()\""
  },
  "keywords": [
    "saml",
    "scim",
    "bridge",
    "identity"
  ],
  "author": "",
  "license": "MIT",
  "devDependencies": {
    "@types/express": "^4.18.2",
    "@types/node": "^20.5.0",
    "typescript": "^5.1.6",
    "ts-node": "^10.9.1"
  },
  "dependencies": {
    "express": "^4.18.2",
    "body-parser": "^1.20.2",
    "onelogin-saml": "^4.2.0",
    "xml-crypto": "^2.1.3",
    "xmldom": "^0.6.0",
    "xpath": "^0.0.32",
    "uuid": "^9.0.0"
  }
}
```

---

## 📁 tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*"]
}
```

---

## 📁 src/config.ts

```typescript
import { readFileSync } from 'fs';
import { join } from 'path';

export interface IdpConfig {
  entityId: string;
  ssoUrl: string;
  certificates: string[]; // PEM strings, current then next
}
export interface SpConfig {
  entityId: string;
  acsUrl
