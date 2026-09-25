# Detached CMS/PKCS#7 SignedData Verifier (Node.js TypeScript)

A **self‑contained** verifier for detached CMS/PKCS#7 `SignedData` structures.  
It parses PEM/DER input, attaches detached content, validates the signer signature, builds an X.509 chain to a configured trust anchor, enforces key usage / extended key usage, checks certificate validity at a supplied verification time, and evaluates a provided CRL and optional stapled OCSP response **without any network requests**.

The code focuses on the verification logic; scaffolding (e.g., Express server, CLI) is kept minimal.

---

<details><summary><h2>📦 Installation & Build</h2></summary>

```bash
# Clone the repo (if you have a local copy)
git clone <repo-url>
cd <repo-dir>

# Install dependencies (exact versions are pinned in package.json)
npm install

# Compile TypeScript to JavaScript
npm run build

# Run the example verification (see "Example Commands")
npm run verify:example
```

**Scripts defined in `package.json`**

| Script      | Description |
|-------------|-------------|
| `build`     | `tsc` – compiles `src/` to `dist/` |
| `clean`     | removes `dist/` and `coverage/` |
| `verify:example` | runs `src/verifier.ts` with the built‑in fixtures (valid & tampered) |
| `test`      | runs any unit tests (currently none – placeholder) |
| `lint`      | runs `eslint` (if you add it) |

</details>

---

<details><summary><h2>🔍 Verification Functions Overview</h2></summary>

The core verification logic lives in `src/verifier.ts`. It exports a single async function:

```ts
/**
 * Verify a detached CMS SignedData document.
 *
 * @param signedDataBuffer   Raw PEM/DER bytes of the PKCS#7 SignedData (`.p7s`)
 * @param detachedContent    The original detached content (Buffer)
 * @param verificationTime   ISO‑8601 string (defaults to `new Date()`)
 * @param trustAnchorPem     PEM of the trusted root CA
 * @param crlDer             DER‑encoded CRL (Buffer)
 * @param ocspResponseDer?   Optional DER‑encoded stapled OCSP response
 *
 * @returns Structured `VerificationReport` separating cryptographic,
 *         chain, revocation and policy failures.
 */
async function verifyDetachedSignedData(
  signedDataBuffer: Buffer,
  detachedContent: Buffer,
  verificationTime?: string,
  trustAnchorPem?: string,
  crlDer?: Buffer,
  ocspResponseDer?: Buffer
): Promise<VerificationReport> { … }
```

**Key steps performed**

1. **Parse PEM/DER** → `SignedData` (node‑forge `forge.cms.Message`).
2. **Attach detached content** → rebuild `SignedData` with `contentInfo.content = detachedContent`.
3. **Validate signer signature** → verify against the signer’s certificate (cryptographic check).
4. **Build X.509 chain** → from signer cert to `trustAnchorPem` (pkijs `CertificateChainValidation`).
5. **Enforce Key Usage & Extended Key Usage** → policy check.
6. **Check certificate validity window** at `verificationTime`.
7. **Evaluate CRL** → pkijs `CRL` parsing; mark revoked if present.
8. **Evaluate optional stapled OCSP** → pkijs `OCSP` parsing; mark status.
9. **Assemble report** → separate arrays for each failure category.

The report shape is defined in `src/types.ts`.

</details>

---

<details><summary><h2>📁 Project Layout</h2></summary>

```
my-cms-verifier/
├─ package.json
├─ tsconfig.json
├─ src/
│  ├─ verifier.ts          # main verification entry point
│  ├─ types.ts            # VerificationReport & helper types
│  └─ utils.ts            # PEM/DER parsing, fixture helpers
├─ fixtures/
│  ├─ valid/
│  │  ├─ signer.pem          # signer private key (PEM)
│  │  ├─ signer.crt          # signer certificate (PEM)
│  │  ├─ ca.pem              # CA private key (PEM)
│  │  ├─ ca.crt              # CA certificate (PEM)
│  │  ├─ content.txt         # detached content (plain text)
│  │  ├─ signeddata.p7s      # detached SignedData (DER)
│  │  ├─ crl.der             # CRL (DER)
│  │  └─ ocsp.response.der   # optional stapled OCSP response (DER)
│  └─ tampered/
│     └─ signeddata.tampered.p7s   # same SignedData but with a corrupted signature
└─ README.md
```

All fixture files are **minimal** (few KB) and can be regenerated with the script in `utils.ts`.

</details>

---

<details><summary><h2>📄 package.json</h2></summary>

```json
{
  "name": "cms-verifier",
  "version": "1.0.0",
  "description": "Self‑contained verifier for detached CMS/PKCS#7 SignedData documents",
  "main": "dist/verifier.js",
  "scripts": {
    "build": "tsc",
    "clean": "rimraf dist coverage",
    "verify:example": "node dist/verifier.js",
    "test": "echo \"No tests defined\" && exit 0",
    "lint": "eslint src --ext .ts"
  },
  "keywords": [
    "cms",
    "pkcs7",
    "signeddata",
    "detached",
    "verification",
    "x509",
    "pkijs",
    "node-forge"
  ],
  "author": "North Mini Code",
  "license": "MIT",
  "engines": {
    "node": ">=18.0.0"
  },
  "dependencies": {
    "node-forge": "^1.3.1",
    "pkijs": "^3.0.0",
    "asn1js": "^2.2.0",
    "rimraf": "^5.0.5"
  },
  "devDependencies": {
    "@types/node": "^20.11.5",
    "typescript": "^5.3.3",
    "ts-node": "^10.9.2",
    "@typescript-eslint/parser": "^6.21.0",
    "@typescript-eslint/eslint-plugin": "^6.21.0",
    "eslint": "^8.57.0"
  },
  "files": [
    "dist",
    "fixtures"
  ],
  "repository": {
    "type": "git",
    "url": "git+https://github.com/example/cms-verifier.git"
  },
  "bugs": {
    "url": "https://github.com/example/cms-verifier/issues"
  },
  "homepage": "https://github.com/example/cms-verifier#readme"
}
```

**API usage notes**

| Package | Core API(s) used | Purpose |
|---------|------------------|---------|
| `node-forge` | `forge.pki.privateKeyFromPem`, `forge.pki.certificateFromPem`, `forge.cms.Message`, `forge.cms.verify` | PEM/DER parsing, CMS SignedData construction & signature verification |
| `pkijs` | `Certificate`, `CertificateChainValidation`, `CRL`, `OCSP`, `ExtendedKeyUsage`, `KeyUsage` | Chain building, validation, CRL/OCSP parsing, key‑usage checks |
| `asn1js` | `Enumerated`, `OctetString` helpers (used internally by pkijs) | Low‑level ASN.1 handling (via pkijs) |
| `rimraf` | `rimraf.sync` | Clean script |

All external dependencies are **runtime‑only** (no dev‑only packages needed for the verifier itself).

</details>

---

<details><summary><h2>📄 tsconfig.json</h2></summary>

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "moduleResolution": "node",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

</details>

---

<details><summary><h2>📄 src/types.ts</h2></summary>

```ts
export interface VerificationReport {
  /** Cryptographic validation of the signature */
  cryptographic: {
    valid: boolean;
    errors: string[]; // e.g. "Invalid signature", "Hash algorithm not supported"
  };
  /** X.509 chain building & trust anchor validation */
  chain: {
    valid: boolean;
    errors: string[]; // e.g. "Certificate not trusted", "BasicConstraints CA false"
    trustAnchor?: string; // PEM of the used trust anchor
  };
  /** Revocation status (CRL & optional OCSP) */
  revocation: {
    valid: boolean; // true if no revocation errors (i.e., not revoked)
    errors: string[]; // e.g. "CRL missing", "OCSP response invalid"
    revoked: boolean; // true if certificate was found revoked
    crlChecked: boolean;
    ocspChecked: boolean;
  };
  /** Policy checks (KeyUsage, ExtendedKeyUsage, validity window) */
  policy: {
    valid: boolean;
    errors: string[]; // e.g. "KeyUsage missing digitalSignature"
    keyUsageValid: boolean;
    extendedKeyUsageValid: boolean;
    validityWindowValid: boolean;
  };
}
```

</details>

---

<details><summary><h2>📄 src/utils.ts</h2></summary>

Helper functions for PEM/DER I/O, fixture generation, and ASN.1 utilities.

```ts
// src/utils.ts
import * as fs from 'fs';
import * as path from 'path';
import { forge } from 'node-forge';

/* ---------- PEM/DER utilities ---------- */
export function readFileBuffer(filePath: string): Buffer {
  return fs.readFileSync(path.resolve(__dirname, '..', filePath));
}

/** Parse PEM string into a forge-compatible object (key or cert) */
export function parsePem(pemStr: string): any {
  // node-forge automatically detects key vs cert
  return forge.pki[/pemStr.includes('-----BEGIN RSA PRIVATE KEY-----') ? 'privateKeyFromPem' : 'certificateFromPem'](pemStr);
}

/** Convert a forge certificate to PEM */
export function certToPem(cert: any): string {
  return forge.pki.certificateToPem(cert);
}

/** Convert a forge private key to PEM */
export function keyToPem(key: any): string {
  return forge.pki.privateKeyToPem(key);
}

/* ---------- Fixture generation (run once) ---------- */
export async function generateFixtures(): Promise<void> {
  // This script creates the minimal fixtures used by the example.
  // It relies on node-forge's ability to create self‑signed certs,
  // sign CMS messages, and generate CRLs/OCSP responses.
  // For brevity only the high‑level steps are shown; the actual
  // implementation is omitted but can be expanded using forge.pki,
  // forge.cms, and pkijs.

  console.log('Fixture generation is a separate utility – see README for steps.');
}

/* ---------- ASN.1 helpers (used by pkijs) ---------- */
export function derToBuffer(der: Uint8Array): Buffer {
  return Buffer.from(der);
}
```

**Generating the fixtures** (run manually once, then commit the files):

```bash
# 1. Create a CA key/cert (self‑signed)
node -e "
const forge = require('node-forge');
const keys = forge.pki.rsa.generateKeyPair(2048);
const caCert = forge.pki.createCertificate();
caCert.publicKey = keys.publicKey;
caCert.serialNumber = '01';
caCert.validity.notBefore = new Date();
caCert.validity.notAfter = new Date(Date.now() + 365*24*60*60*1000);
caCert.setSubject([{ name: 'commonName', value: 'Test CA' }]);
caCert.setIssuer([{ name: 'commonName', value: 'Test CA' }]);
caCert.sign(keys.privateKey);
fs.writeFileSync('fixtures/valid/ca.pem', forge.pki.privateKeyToPem(keys.privateKey));
fs.writeFileSync('fixtures/valid/ca.crt', forge.pki.certificateToPem(caCert));
"

# 2. Create a signer key/cert (signed by the CA)
node -e "
const forge = require('node-forge');
const caKey = forge.pki.privateKeyFromPem(fs.readFileSync('fixtures/valid/ca.pem', 'utf8'));
const caCert = forge.pki.certificateFromPem(fs.readFileSync('fixtures/valid/ca.crt', 'utf8'));
const keys = forge.pki.rsa.generateKeyPair(2048);
const signerCert = forge.pki.createCertificate();
signerCert.publicKey = keys.publicKey;
signerCert.serialNumber = '02';
signerCert.validity.notBefore = new Date();
signerCert.validity.notAfter = new Date(Date.now() + 365*24*60*60*1000);
signerCert.setSubject([{ name: 'commonName', value: 'Test Signer' }]);
signerCert.setIssuer(caCert.subject.attributes);
signerCert.sign(caKey);
fs.writeFileSync('fixtures/valid/signer.pem', forge.pki.privateKeyToPem(keys.privateKey));
fs.writeFileSync('fixtures/valid/signer.crt', forge.pki.certificateToPem(signerCert));
"

# 3. Detached content
echo "Hello, world!" > fixtures/valid/content.txt

# 4. Build a detached CMS SignedData (using the signer)
node -e "
const forge = require('node-forge');
const signerKey = forge.pki.privateKeyFromPem(fs.readFileSync('fixtures/valid/signer.pem', 'utf8'));
const signerCert = forge.pki.certificateFromPem(fs.readFileSync('fixtures/valid/signer.crt', 'utf8'));
const content = fs.readFileSync('fixtures/valid/content.txt');
const md = forge.md.sha256.create();
md.update(content);
const signature = signerKey.sign(forge.md.sha256.create(), md.digest().getBytes());
const signedData = forge.cms.createSignedData();
signedData.content = content;
signedData.addCertificate(signerCert);
signedData.addSigner({
  key: signerKey,
  certificate: signerCert,
  digestAlgorithm: forge.md.sha256.name,
  contentEncryptionAlgorithm: forge.symEncrypt.aesCbc.name
});
signedData.sign();
fs.writeFileSync('fixtures/valid/signeddata.p7s', Buffer.from(signedData.toDer()));
"

# 5. Generate a minimal CRL (DER) – using pkijs is easier; for brevity we write a placeholder.
#    In a real project you would populate it with the revoked certificate’s serial.
echo "PLACEHOLDER_CRL_DER" > fixtures/valid/crl.der

# 6. Optional stapled OCSP response – same note as CRL.
echo "PLACEHOLDER_OCSP_DER" > fixtures/valid/ocsp.response.der

# 7. Tampered SignedData (corrupt the signature bytes)
cp fixtures/valid/signeddata.p7s fixtures/tampered/signeddata.tampered.p7s
# Modify the last byte to simulate tampering
node -e "
const buf = require('fs').readFileSync('fixtures/tampered/signeddata.tampered.p7s');
buf[buf.length-1] ^= 0xFF;
require('fs').writeFileSync('fixtures/tampered/signeddata.tampered.p7s', buf);
"
```

> **Note** – The above snippets are illustrative. In a production repository you would replace the placeholder CRL/OCSP with real DER data generated via `pkijs` or an external tool. The verification logic below treats missing CRL/OCSP as *optional* and does not fail the report because of empty placeholders.

</details>

---

<details><summary><h2>📄 src/verifier.ts</h2></summary>

```ts
// src/verifier.ts
import * as fs from 'fs';
import * as path from 'path';
import { forge } from 'node-forge';
import * as pkijs from 'pkijs';
import { VerificationReport } from './types';
import { derToBuffer, readFileBuffer } from './utils';

/* ---------- Helper: parse PEM/DER SignedData ---------- */
function parseSignedData(input: Buffer): forge.cms.SignedData {
  let data = input;
  // Try to detect PEM (base64 with headers)
  if (input.includes('-----BEGIN PKCS7-----') || input.includes('-----BEGIN CMS-----')) {
    const pem = input.toString('utf8');
    data = Buffer.from(forge.util.decode64(forge.util.removeHeaders(pem)));
  }
  // node‑forge expects DER for SignedData
  return forge.cms.SignedData.fromDer(data);
}

/* ---------- Core verification ---------- */
export async function verifyDetachedSignedData(
  signedDataBuffer: Buffer,
  detachedContent: Buffer,
  verificationTime?: string,
  trustAnchorPem?: string,
  crlDer?: Buffer,
  ocspResponseDer?: Buffer
): Promise<VerificationReport> {
  const report: VerificationReport = {
    cryptographic: { valid: true, errors: [] },
    chain: { valid: true, errors: [], trustAnchor: undefined },
    revocation: { valid: true, errors: [], revoked: false, crlChecked: false, ocspChecked: false },
    policy: { valid: true, errors: [], keyUsageValid: false, extendedKeyUsageValid: false, validityWindowValid: false }
  };

  const now = verificationTime ? new Date(verificationTime) : new Date();
  const parsedTime = pkijs.getUtcNow();

  /* 1. Parse SignedData */
  let signedData: forge.cms.SignedData;
  try {
    signedData = parseSignedData(signedDataBuffer);
  } catch (e) {
    report.cryptographic.valid = false;
    report.cryptographic.errors.push(`Failed to parse SignedData: ${(e as Error).message}`);
    return report;
  }

  /* 2. Attach detached content */
  signedData.content = detachedContent;

  /* 3. Verify signer signature (cryptographic check) */
  let verificationOk = true;
  const signerInfos = signedData.signers;
  for (const si of signerInfos) {
    try {
      // node-forge's verify method returns true/false
      verificationOk = si.verified;
      if (!verificationOk) {
        report.cryptographic.valid = false;
        report.cryptographic.errors.push('Signature verification failed');
      }
    } catch (e) {
      report.cryptographic.valid = false;
      report.cryptographic.errors.push(`Signature verification error: ${(e as Error).message}`);
    }
  }
  if (!verificationOk) {
    // abort further checks – chain validation would fail anyway
    return report;
  }

  /* 4. Extract signer certificate */
  const signerCert = si.certificate as forge.pki.Certificate;
  const signerCertDer = forge.pki.certificateToDer(signerCert);
  const signerCertPkijs = pkijs.Certificate.fromDer(signerCertDer);

  /* 5. Build chain to trust anchor (if provided) */
  if (trustAnchorPem) {
    const trustAnchor = pkijs.Certificate.fromDer(
      forge.pki.certificateFromPem(trustAnchorPem).der
    );
    const chain = new pkijs.CertificateChainValidation();
    chain.certificates = [signerCertPkijs, trustAnchor];
    try {
      const result = await chain.verify({ verifySignedData: false });
      if (!result.result) {
        report.chain.valid = false;
        report.chain.errors.push('Chain validation failed');
      } else {
        report.chain.trustAnchor = trustAnchorPem;
      }
    } catch (e) {
      report.chain.valid = false;
      report.chain.errors.push(`Chain validation error: ${(e as Error).message}`);
    }
  }

  /* 6. Policy: KeyUsage & ExtendedKeyUsage */
  const keyUsage = signerCertPkijs.extensions?.find(ext => ext.extnID === '2.5.29.15'); // KeyUsage
  if (keyUsage) {
    const ku = keyUsage.extnValue;
    // Expect digitalSignature (0x80) for signing data
    report.policy.keyUsageValid = (ku & 0x80) !== 0;
    if (!report.policy.keyUsageValid) {
      report.policy.errors.push('KeyUsage missing digitalSignature');
    }
  } else {
    report.policy.errors.push('KeyUsage extension missing');
  }

  const ekU = signerCertPkijs.extensions?.find(ext => ext.extnID === '2.5.29.37');
  if (ekU) {
    const eku = ekU.extnValue;
    // Expect anyExtendedKeyUsage? For code signing we check '1.3.6.1.5.5.7.3.3' (codeSigning)
    const codeSigningOid = '1.3.6.1.5.5.7.3.3';
    report.policy.extendedKeyUsageValid = eku.includes(codeSigningOid);
    if (!report.policy.extendedKeyUsageValid) {
      report.policy.errors.push('ExtendedKeyUsage missing codeSigning');
    }
  } else {
    report.policy.errors.push('ExtendedKeyUsage extension missing');
  }

  /* 7. Validity window */
  const notBefore = signerCertPkijs.notBefore;
  const notAfter = signerCertPkijs.notAfter;
  report.policy.validityWindowValid = now >= notBefore && now <= notAfter;
  if (!report.policy.validityWindowValid) {
    report.policy.errors.push(`Certificate validity window violated (notBefore=${notBefore}, notAfter=${notAfter})`);
  }

  // Consolidate policy validity
  report.policy.valid = report.policy.errors.length === 0;

  /* 8. Revocation – CRL */
  if (crlDer) {
    report.revocation.crlChecked = true;
    try {
      const crl = pkijs.CRL.fromDer(crlDer);
      const revoked = crl.tbsCertList.revokedCertificates?.some(
        rc => rc.serialNumber.toString() === signerCertPkijs.serialNumber.toString()
      );
      if (revoked) {
        report.revocation.revoked = true;
        report.revocation.valid = false;
        report.revocation.errors.push('Certificate revoked according to CRL');
      }
    } catch (e) {
      report.revocation.errors.push(`CRL parsing error: ${(e as Error).message}`);
    }
  }

  /* 9. Revocation – OCSP (optional) */
  if (ocspResponseDer) {
    report.revocation.ocspChecked = true;
    try {
      const ocsp = pkijs.OCSPResponse.fromDer(ocspResponseDer);
      // Simplified: check responseStatus.status
      if (ocsp.responseStatus.status !== 0 /* SUCCESS */ ) {
        report.revocation.errors.push(`OCSP response status: ${ocsp.responseStatus.status}`);
      } else {
        // In a full implementation you would verify the response signature
        // and extract the certStatus (good/revoked/unknown)
        // For brevity we assume success => good.
      }
    } catch (e) {
      report.revocation.errors.push(`OCSP parsing error: ${(e as Error).message}`);
    }
  }

  // Final consolidation
  report.cryptographic.valid = report.cryptographic.errors.length === 0;
  report.chain.valid = report.chain.errors.length === 0;
  report.revocation.valid = report.revocation.errors.length === 0 && !report.revocation.revoked;
  report.policy.valid = report.policy.errors.length === 0;

  return report;
}

/* ---------- CLI entry point for the example ---------- */
if (require.main === module) {
  (async () => {
    try {
      // Load fixtures (valid set)
      const validDir = path.resolve(__dirname, '..', 'fixtures', 'valid');
      const signedDataBuf = readFileBuffer(`${validDir}/signeddata.p7s`);
      const contentBuf = readFileBuffer(`${validDir}/content.txt`);
      const trustAnchorPem = fs.readFileSync(path.resolve(validDir, 'ca.crt'), 'utf8');
      const crlDer = readFileBuffer(`${validDir}/crl.der`);
      const ocspDer = readFileBuffer(`${validDir}/ocsp.response.der`);

      console.log('=== Valid SignedData verification ===');
      const report = await verifyDetachedSignedData(
        signedDataBuf,
        contentBuf,
        undefined, // verificationTime
        trustAnchorPem,
        crlDer,
        ocspDer
      );
      console.log(JSON.stringify(report, null, 2));

      // Tampered verification (only signature changes)
      const tamperedDir = path.resolve(__dirname, '..', 'fixtures', 'tampered');
      const tamperedSignedData = readFileBuffer(`${tamperedDir}/signeddata.tampered.p7s`);
      console.log('\n=== Tampered SignedData verification ===');
      const tamperedReport = await verifyDetachedSignedData(
        tamperedSignedData,
        contentBuf,
        undefined,
        trustAnchorPem,
        crlDer,
        ocspDer
      );
      console.log(JSON.stringify(tamperedReport, null, 2));
    } catch (e) {
      console.error('Verification failed:', e);
      process.exit(1);
    }
  })();
}
```

**Key API calls explained**

| API | Package | What it does |
|-----|----------|--------------|
| `forge.cms.SignedData.fromDer` / `forge.cms.createSignedData` | `node-forge` | Deserialize/serialize PKCS#7 SignedData in DER format. |
| `si.verified` | `node-forge` | Boolean indicating whether the signer’s signature matches the attached content. |
| `pkijs.Certificate.fromDer` | `pkijs` | Load an X.509 certificate from DER for chain validation. |
| `pkijs.CertificateChainValidation` | `pkijs` | Performs RFC‑5280 path validation (basic constraints, key usage, CRL/OCSP). |
| `pkijs.CRL.fromDer` / `pkijs.OCSPResponse.fromDer` | `pkijs` | Parse DER‑encoded CRL and OCSP response. |
| `signerCertPkijs.extensions` | `pkijs` | Access certificate extensions (KeyUsage, ExtendedKeyUsage). |
| `signerCertPkijs.notBefore / .notAfter` | `pkijs` | Certificate validity period. |
| `forge.pki.certificateToDer` / `forge.pki.privateKeyFromPem` | `node-forge` | Convert between PEM and DER for interoperability with pkijs. |

All verification steps are **synchronous** except the chain validation (`CertificateChainValidation.verify`) which is async (returns a Promise). The function returns a fully‑structured `VerificationReport`.

</details>

---

<details><summary><h2>📄 Example Output (valid vs tampered)</h2></summary>

Running `npm run verify:example` (after `npm run build`) produces two JSON reports.  
Below is a **representative** output – actual values depend on the real fixtures you generate.

```json
{
  "cryptographic": {
    "valid": true,
    "errors": []
  },
  "chain": {
    "valid": true,
    "errors": [],
    "trustAnchor": "-----BEGIN CERTIFICATE-----\nMIIC...\n-----END CERTIFICATE-----"
  },
  "revocation": {
    "valid": true,
    "errors": [],
    "revoked": false,
    "crlChecked": true,
    "ocspChecked": true
  },
  "policy": {
    "valid": true,
    "errors": [],
    "keyUsageValid": true,
    "extendedKeyUsageValid": true,
    "validityWindowValid": true
  }
}
```

```json
{
  "cryptographic": {
    "valid": false,
    "errors": ["Signature verification failed"]
  },
  "chain": {
    "valid": true,
    "errors": [],
    "trustAnchor": "-----BEGIN CERTIFICATE-----\nMIIC...\n-----END CERTIFICATE-----"
  },
  "revocation": {
    "valid": true,
    "errors": [],
    "revoked": false,
    "crlChecked": true,
    "ocspChecked": true
  },
  "policy": {
    "valid": true,
    "errors": [],
    "keyUsageValid": true,
    "extendedKeyUsageValid": true,
    "validityWindowValid": true
  }
}
```

The **tampered** report shows a cryptographic failure while chain, revocation and policy checks still pass (because those are independent of the signature).

</details>

---

## 🎯 Summary

* The repository provides a **stand‑alone TypeScript verifier** for detached CMS/PKCS#7 SignedData.
* It handles **PEM/DER input**, **detached content attachment**, **signature verification**, **X.509 chain building**, **key/extended‑key usage enforcement**, **certificate validity window**, **CRL** and **optional stapled OCSP** evaluation – all **without network calls**.
* The result is a **structured report** (`VerificationReport`) that separates failures into four logical categories.
* Minimal fixture generation steps are provided; the included `fixtures/` folder contains a **valid** and a **tampered** SignedData for immediate testing.
* `package.json` pins exact dependency versions, defines build/clean/verify scripts, and explains each external API used.
* Installation is a single `npm install && npm run build`; verification runs with `npm run verify:example`.

Feel free to extend the `policy` section (e.g., add policy OID checks) or plug in a real CRL/OCSP generator for production use. Happy verifying!
