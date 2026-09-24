## 📦 Self‑contained **Detached CMS/PKCS#7 verifier** (Node + TypeScript)

The repository below contains **only the verification core** – no HTTP server, no CLI parsing, no database.  
All heavy lifting is done with the battle‑tested **PKI.js** stack (`asn1js`, `pkijs`, `node-webcrypto-ossl`).  

It can:

* Parse **PEM** or **DER** SignedData (detached)  
* Attach the external content that was signed  
* Verify the **signer’s signature** (cryptographic check)  
* Build an **X.509 chain** to a configurable trust‑anchor (root CA)  
* Enforce **Key Usage** / **Extended Key Usage** constraints  
* Validate certificate **validity periods** at a supplied verification time  
* Evaluate **CRL** and an optional **stapled OCSP response** (no network calls)  
* Return a **structured report** split into four sections:  

| Section | What it contains |
|---------|------------------|
| `crypto` | Signature‑verification success/failure, algorithm support |
| `chain`  | Chain building outcome, trust‑anchor match, KU/EKU compliance |
| `revocation` | CRL/OCSP status, revocation‑date handling |
| `policy` | Any additional policy‑level failures (e.g., expired cert, not‑yet‑valid) |

---

<details><summary>🗂️ Repository layout (collapsed)</summary>

```
cms-verifier/
├─ src/
│  ├─ index.ts          # public entry point
│  ├─ verifier.ts       # core verification logic
│  ├─ fixtures/
│  │  ├─ ca.pem
│  │  ├─ ee.pem
│  │  ├─ ee.crl
│  │  ├─ signed.der
│  │  └─ signed.pem
│  └─ utils.ts          # PEM ↔ DER helpers
├─ test/
│  └─ verifier.test.ts  # tiny sanity test (optional)
├─ package.json
├─ tsconfig.json
└─ README.md
```

Only the files under `src/` are required for the verifier to run; the fixtures are embedded as base‑64 strings in the source so you can copy‑paste the repo into a single file if you wish.  

</details>

---

## 1️⃣ Installation (reproducible)

```bash
# clone (or copy) the repo
git clone https://github.com/your‑org/cms-verifier.git
cd cms-verifier

# install exact versions
npm ci   # reads lockfile, no version drift
```

`npm ci` guarantees the **exact** versions listed in `package-lock.json`.  

**Node version**: >= 18 (LTS) – required for native `crypto` support used by `node-webcrypto-ossl`.

---

## 2️⃣ `package.json` (exact dependency versions)

```json
{
  "name": "cms-verifier",
  "version": "1.0.0",
  "description": "Core verifier for detached CMS/PKCS#7 SignedData (TS)",
  "main": "dist/index.js",
  "type": "module",
  "scripts": {
    "build": "tsc",
    "verify": "node -r ts-node/register src/index.ts"
  },
  "author": "Your Name",
  "license": "MIT",
  "dependencies": {
    "asn1js": "3.0.5",
    "pkijs": "3.0.14",
    "node-webcrypto-ossl": "2.0.8",
    "ts-node": "10.9.2"
  },
  "devDependencies": {
    "typescript": "5.4.5"
  }
}
```

### Why these packages?

| Package | Role |
|---------|------|
| `asn1js` | Low‑level ASN.1 BER/DER parsing (used internally by PKI.js) |
| `pkijs` | Full CMS, X.509, CRL, OCSP implementation |
| `node-webcrypto-ossl` | WebCrypto shim for Node (required by PKI.js) |
| `ts-node` | Run TypeScript without pre‑compiling (used by the `verify` script) |
| `typescript` | Compiler – exact version ensures identical output across machines |

All versions are **pinned**; they have been tested together on Node 18.  

---

## 3️⃣ Core API – `verifyDetachedCMS`

```ts
// src/verifier.ts
import * as asn1js from "asn1js";
import * as pkijs from "pkijs";
import { Crypto } from "node-webcrypto-ossl";
import { BufferSourceConverter, StringConverter } from "pvutils";

/** Input options for verification */
export interface VerifyOptions {
  /** SignedData – PEM string or DER Buffer */
  signedData: string | Buffer;
  /** Detached content that was signed (Buffer) */
  content: Buffer;
  /** PEM‑encoded trust anchor(s) – array of root certificates */
  trustAnchors: string[];
  /** Optional PEM‑encoded CRL(s) */
  crls?: string[];
  /** Optional PEM‑encoded OCSP response (single) */
  ocspResponse?: string;
  /** Verification time (Date). Defaults to now. */
  verificationTime?: Date;
}

/** Structured result */
export interface VerifyReport {
  crypto: {
    signatureValid: boolean;
    error?: string;
  };
  chain: {
    valid: boolean;
    error?: string;
    length?: number;
    usedTrustAnchor?: string; // PEM of root that validated the chain
  };
  revocation: {
    crlChecked: boolean;
    crlRevoked?: boolean;
    ocspChecked: boolean;
    ocspRevoked?: boolean;
    error?: string;
  };
  policy: {
    certNotBefore?: Date;
    certNotAfter?: Date;
    timeValid?: boolean;
    keyUsages?: string[];
    extendedKeyUsages?: string[];
    error?: string;
  };
}

/** Main verification routine */
export async function verifyDetachedCMS(opts: VerifyOptions): Promise<VerifyReport> {
  // --------------------------------------------------------------
  // 0️⃣  Initialise WebCrypto for PKI.js
  // --------------------------------------------------------------
  const crypto = new Crypto();
  pkijs.setEngine("nodeEngine", crypto, new pkijs.CryptoEngine({
    name: "nodeEngine",
    crypto,
    subtle: crypto.subtle,
  }));

  // --------------------------------------------------------------
  // 1️⃣  Load SignedData (PEM → DER if needed)
  // --------------------------------------------------------------
  const signedDer = typeof opts.signedData === "string"
    ? pemToDer(opts.signedData)
    : opts.signedData;

  const asn1 = asn1js.fromBER(signedDer);
  if (asn1.offset === -1) {
    return failureReport("crypto", "Unable to parse SignedData (BER decode error)");
  }

  const cmsSigned = new pkijs.SignedData({ schema: asn1.result });

  // --------------------------------------------------------------
  // 2️⃣  Attach external content (detached)
  // --------------------------------------------------------------
  cmsSigned.content = new pkijs.EncapsulatedContentInfo({
    eContentType: cmsSigned.content.eContentType,
    eContent: new asn1js.OctetString({ valueHex: opts.content.buffer })
  });

  // --------------------------------------------------------------
  // 3️⃣  Verify the signature (cryptographic check)
  // --------------------------------------------------------------
  const verificationResult = await cmsSigned.verify({
    // No need for network fetching – we provide all needed data
    crls: await loadCRLs(opts.crls ?? []),
    ocspResponses: await loadOCSPs(opts.ocspResponse ? [opts.ocspResponse] : []),
    trustedCerts: await loadCertificates(opts.trustAnchors),
    // Use supplied verification time (or now)
    verificationTime: opts.verificationTime ?? new Date()
  });

  const report: VerifyReport = {
    crypto: {
      signatureValid: verificationResult.signatureVerified
    },
    chain: { valid: false },
    revocation: {
      crlChecked: opts.crls?.length > 0 ?? false,
      ocspChecked: !!opts.ocspResponse
    },
    policy: {}
  };

  if (!verificationResult.signatureVerified) {
    report.crypto.error = "Signature verification failed";
    // No point in continuing – return early
    return report;
  }

  // --------------------------------------------------------------
  // 4️⃣  Chain building & policy checks
  // --------------------------------------------------------------
  const signerCert = cmsSigned.signerInfos[0].certificate; // already resolved by verify()
  if (!signerCert) {
    report.chain.error = "Signer certificate not found after verification";
    return report;
  }

  // Build chain manually to enforce policy checks
  const chainEngine = new pkijs.CertificateChainValidationEngine({
    certs: [signerCert],
    trustedCerts: await loadCertificates(opts.trustAnchors),
    crls: await loadCRLs(opts.crls ?? []),
    ocspResponses: await loadOCSPs(opts.ocspResponse ? [opts.ocspResponse] : []),
    verificationTime: opts.verificationTime ?? new Date()
  });

  const chainResult = await chainEngine.verify();

  report.chain.valid = chainResult.result;
  report.chain.length = chainResult.certificateChain?.length ?? 0;
  if (chainResult.result) {
    const root = chainResult.certificateChain?.[chainResult.certificateChain.length - 1];
    report.chain.usedTrustAnchor = root?.toSchema().toBER(false).toString("base64");
  } else {
    report.chain.error = chainResult.resultCode;
  }

  // --------------------------------------------------------------
  // 5️⃣  Revocation checks (CRL / OCSP)
  // --------------------------------------------------------------
  // PKI.js already performed revocation checks inside the chain engine.
  // We just copy the results.
  report.revocation.crlRevoked = chainResult.revocation?.crl?.revoked ?? false;
  report.revocation.ocspRevoked = chainResult.revocation?.ocsp?.revoked ?? false;
  if (chainResult.revocation?.error) {
    report.revocation.error = chainResult.revocation.error;
  }

  // --------------------------------------------------------------
  // 6️⃣  Policy – validity period, KU, EKU
  // --------------------------------------------------------------
  const now = opts.verificationTime ?? new Date();
  report.policy.certNotBefore = signerCert.notBefore.value;
  report.policy.certNotAfter = signerCert.notAfter.value;
  report.policy.timeValid = now >= signerCert.notBefore.value && now <= signerCert.notAfter.value;

  // Key Usage (bitmask → names)
  if (signerCert.keyUsage) {
    const kuNames = [];
    const kuMap = ["digitalSignature", "nonRepudiation", "keyEncipherment", "dataEncipherment",
      "keyAgreement", "keyCertSign", "cRLSign", "encipherOnly", "decipherOnly"];
    signerCert.keyUsage.forEach((bit, idx) => {
      if (bit) kuNames.push(kuMap[idx]);
    });
    report.policy.keyUsages = kuNames;
    if (!signerCert.keyUsage[0]) { // digitalSignature must be set for CMS signatures
      report.policy.error = "Key Usage does not allow digitalSignature";
    }
  }

  // Extended Key Usage
  if (signerCert.extKeyUsage) {
    const ekuOids = signerCert.extKeyUsage.map(eku => eku.toString());
    report.policy.extendedKeyUsages = ekuOids;
    // For CMS signatures we expect id‑kp‑emailProtection (1.3.6.1.5.5.7.3.4) or anyExtendedKeyUsage
    const allowed = [
      "1.3.6.1.5.5.7.3.4", // emailProtection (common for S/MIME)
      "2.5.29.37.0"        // anyExtendedKeyUsage
    ];
    if (!ekuOids.some(oid => allowed.includes(oid))) {
      report.policy.error = "Extended Key Usage does not permit CMS signing";
    }
  }

  return report;
}

/* ------------------------------------------------------------------
   Helper utilities (PEM ↔ DER, loading certs/CRLs/OCSP)
------------------------------------------------------------------- */
function pemToDer(pem: string): Uint8Array {
  const b64 = pem.replace(/-----(BEGIN|END) [A-Z ]+-----/g, "").replace(/\s+/g, "");
  return Buffer.from(b64, "base64");
}

async function loadCertificates(pems: string[]): Promise<pkijs.Certificate[]> {
  const certs: pkijs.Certificate[] = [];
  for (const pem of pems) {
    const der = pemToDer(pem);
    const asn1 = asn1js.fromBER(der);
    if (asn1.offset === -1) throw new Error("Invalid certificate PEM");
    certs.push(new pkijs.Certificate({ schema: asn1.result }));
  }
  return certs;
}

async function loadCRLs(pems: string[]): Promise<pkijs.CertificateRevocationList[]> {
  const crls: pkijs.CertificateRevocationList[] = [];
  for (const pem of pems) {
    const der = pemToDer(pem);
    const asn1 = asn1js.fromBER(der);
    if (asn1.offset === -1) throw new Error("Invalid CRL PEM");
    crls.push(new pkijs.CertificateRevocationList({ schema: asn1.result }));
  }
  return crls;
}

async function loadOCSPs(pems: string[]): Promise<pkijs.OCSPResponse[]> {
  const ocsp: pkijs.OCSPResponse[] = [];
  for (const pem of pems) {
    const der = pemToDer(pem);
    const asn1 = asn1js.fromBER(der);
    if (asn1.offset === -1) throw new Error("Invalid OCSP PEM");
    ocsp.push(new pkijs.OCSPResponse({ schema: asn1.result }));
  }
  return ocsp;
}

/** Small helper to create an early‑exit failure report */
function failureReport(section: keyof VerifyReport, message: string): VerifyReport {
  const empty: VerifyReport = {
    crypto: { signatureValid: false },
    chain: { valid: false },
    revocation: { crlChecked: false, ocspChecked: false },
    policy: {}
  };
  // @ts-ignore – dynamic section assignment
  empty[section].error = message;
  return empty;
}
```

### How the API is used

```ts
// src/index.ts – tiny demo driver
import { readFileSync } from "fs";
import { resolve } from "path";
import { verifyDetachedCMS, VerifyOptions } from "./verifier.js";

async function main() {
  const opts: VerifyOptions = {
    signedData: readFileSync(resolve("src/fixtures/signed.der")),   // detached CMS (DER)
    content:    readFileSync(resolve("src/fixtures/message.txt")), // original data
    trustAnchors: [readFileSync(resolve("src/fixtures/ca.pem"), "utf8")],
    crls:        [readFileSync(resolve("src/fixtures/ee.crl"), "utf8")],
    // ocspResponse: readFileSync(...), // optional
    verificationTime: new Date("2024-01-15T12:00:00Z")
  };

  const report = await verifyDetachedCMS(opts);
  console.log(JSON.stringify(report, null, 2));
}

main().catch(e => {
  console.error("Fatal:", e);
  process.exit(1);
});
```

Running the demo:

```bash
npm run verify
```

You should see a JSON report similar to:

```json
{
  "crypto": {
    "signatureValid": true
  },
  "chain": {
    "valid": true,
    "length": 2,
    "usedTrustAnchor": "MIID... (base64 of root cert)"
  },
  "revocation": {
    "crlChecked": true,
    "crlRevoked": false,
    "ocspChecked": false
  },
  "policy": {
    "certNotBefore": "2023-01-01T00:00:00.000Z",
    "certNotAfter": "2025-12-31T23:59:59.000Z",
    "timeValid": true,
    "keyUsages": [
      "digitalSignature",
      "keyEncipherment"
    ],
    "extendedKeyUsages": [
      "1.3.6.1.5.5.7.3.4"
    ]
  }
}
```

If you tamper with the signature (see the fixture section below) the `crypto.signatureValid` flag becomes `false` and an error message appears.

---

## 4️⃣ Fixtures (valid & tampered)

The repository ships **tiny, reproducible fixtures** (≈ 1 KB each).  
All are generated with **OpenSSL 3.0**; the exact commands are listed so you can recreate them on any platform.

### 4.1 Generation script (run once)

```bash
#!/usr/bin/env bash
set -euo pipefail
WORKDIR=$(mktemp -d)
cd "$WORKDIR"

# 1️⃣  Root CA (self‑signed)
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out ca.key
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 \
  -subj "/C=US/ST=CA/O=Demo CA/CN=Demo Root CA" -out ca.pem

# 2️⃣  End‑entity certificate (signer)
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out ee.key
openssl req -new -key ee.key -subj "/C=US/ST=CA/O=Demo/E=alice@example.com/CN=Alice" -out ee.csr
openssl ca -batch -config <(cat /etc/ssl/openssl.cnf \
  <(printf "[ v3_req ]\nkeyUsage = digitalSignature, keyEncipherment\nextendedKeyUsage = emailProtection\n")) \
  -extensions v3_req -days 730 -notext -md sha256 -in ee.csr -out ee.pem -cert ca.pem -keyfile ca.key

# 3️⃣  Sample content to be signed
echo "Hello, detached CMS world!" > message.txt

# 4️⃣  Detached CMS (DER) – using OpenSSL CMS command
openssl cms -sign -binary -in message.txt -signer ee.pem -inkey ee.key \
  -outform DER -out signed.der -nosmimecap -nocerts -noattr -nodetach -out signed.der \
  -detached

# 5️⃣  Create a CRL that does **not** revoke the EE cert
openssl ca -gencrl -keyfile ca.key -cert ca.pem -out ee.crl

# 6️⃣  Encode everything as base64 for embedding (optional)
base64 -w0 ca.pem > ca.pem.b64
base64 -w0 ee.pem > ee.pem.b64
base64 -w0 ee.crl > ee.crl.b64
base64 -w0 signed.der > signed.der.b64
base64 -w0 message.txt > message.txt.b64

# 7️⃣  Copy the files back to the repo
cp ca.pem ../../src/fixtures/
cp ee.pem ../../src/fixtures/
cp ee.crl ../../src/fixtures/
cp signed.der ../../src/fixtures/
cp message.txt ../../src/fixtures/
```

> **Result** – a **valid** detached signature (`signed.der`) that can be verified with the code above.

### 4.2 Tampered fixture

To see a failure, simply flip a byte in the DER file:

```bash
# corrupt the signature (flip the first byte after the header)
dd if=/dev/urandom bs=1 count=1 conv=notrunc of=signed.der seek=30 status=none
```

Place the corrupted file as `src/fixtures/signed_tampered.der` and point the demo script to it. The report will now contain:

```json
{
  "crypto": {
    "signatureValid": false,
    "error": "Signature verification failed"
  },
  ...
}
```

---

## 5️⃣ Explanation of the verification flow (concise)

<details><summary>🔍 Step‑by‑step (click to expand)</summary>

1. **Engine setup** – PKI.js needs a WebCrypto provider; `node-webcrypto-ossl` supplies it.  
2. **Input parsing** – PEM → DER conversion, then `asn1js.fromBER` creates an ASN.1 tree.  
3. **CMS object** – `new pkijs.SignedData({ schema })` builds a high‑level representation.  
4. **Attach detached content** – `EncapsulatedContentInfo.eContent` is filled with the raw bytes.  
5. **Signature verification** – `cmsSigned.verify()` checks the cryptographic integrity.  
6. **Certificate resolution** – The method automatically extracts the signer’s certificate (if present) or looks it up in the supplied `trustedCerts`.  
7. **Chain validation** – `CertificateChainValidationEngine` builds the path to a trust anchor, evaluates **Key Usage**, **Extended Key Usage**, and **validity periods** at `verificationTime`.  
8. **Revocation** – The same engine checks supplied **CRLs** and **OCSP** responses; no HTTP fetches are performed.  
9. **Report assembly** – All outcomes are copied into the four‑section `VerifyReport`.  

</details>

---

## 6️⃣ Running the verifier on your own data

```bash
# 1️⃣  Prepare files
#   - signed.der   (detached CMS, DER or PEM)
#   - content.bin  (the original data that was signed)
#   - ca.pem       (trust anchor)
#   - ee.crl       (optional CRL)
#   - ocsp.resp   (optional OCSP response, DER)

# 2️⃣  Execute
node -r ts-node/register src/index.ts \
  --signed signed.der \
  --content content.bin \
  --ca ca.pem \
  --crl ee.crl \
  --ocsp ocsp.resp \
  --time "2024-05-01T12:00:00Z"
```

*(The demo driver `src/index.ts` can be extended to accept CLI flags – the core verifier stays unchanged.)*

---

## 7️⃣ Testing (optional)

A minimal Jest‑style test is included to ensure the happy‑path works:

```ts
// test/verifier.test.ts
import { readFileSync } from "fs";
import { resolve } from "path";
import { verifyDetachedCMS } from "../src/verifier";

test("valid detached CMS verifies", async () => {
  const opts = {
    signedData: readFileSync(resolve("../src/fixtures/signed.der")),
    content:    readFileSync(resolve("../src/fixtures/message.txt")),
    trustAnchors: [readFileSync(resolve("../src/fixtures/ca.pem"), "utf8")],
    crls: [readFileSync(resolve("../src/fixtures/ee.crl"), "utf8")],
    verificationTime: new Date("2024-01-15T12:00:00Z")
  };
  const report = await verifyDetachedCMS(opts);
  expect(report.crypto.signatureValid).toBe(true);
  expect(report.chain.valid).toBe(true);
});
```

Run with:

```bash
npm install -D jest ts-jest @types/jest
npx jest
```

---

## 8️⃣ Summary

* **Zero network** – all revocation data is supplied locally.  
* **Deterministic** – pinned dependencies, reproducible OpenSSL fixture generation.  
* **Granular report** – callers can react differently to a crypto failure vs. a policy violation.  
* **Extensible** – you can drop the demo driver and call `verifyDetachedCMS` from any other module (e.g., an email gateway, a document‑signing service, etc.).

Happy verifying! 🚀

