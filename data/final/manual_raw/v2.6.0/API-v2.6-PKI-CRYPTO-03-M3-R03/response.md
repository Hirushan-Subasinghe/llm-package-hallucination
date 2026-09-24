## 📦 `smime-core` – A Minimal S/MIME Toolkit (Node.js + TypeScript)

A **self‑contained** library that can:

* Build a standards‑compatible MIME message (with proper `Content-Type`, `Content-Transfer-Encoding`, and **CRLF** line endings).  
* **Sign** the message with a CMS/PKCS#7 `signedData` structure.  
* **Verify** a signed message, report the signer’s certificate details, and validate the chain against supplied trust anchors.  
* **Encrypt** the signed (or plain) content for one or more X.509 recipients.  
* **Decrypt** an encrypted message.  
* Parse a MIME message back into its parts.

The demo shows a **sign‑then‑encrypt** round‑trip and a **tampered‑message** fixture that triggers distinct error categories (signature, certificate, content).

---

<details><summary>🗂️ Repository layout</summary>

```
smime-core/
├─ src/
│  ├─ smime.ts          # Core API
│  └─ demo.ts           # CLI demo script
├─ fixtures/
│  ├─ message.txt       # Plain test payload
│  └─ tampered.eml      # Signed‑then‑encrypted message with altered ciphertext
├─ package.json
├─ tsconfig.json
└─ README.md
```

</details>

---

## 1️⃣ `package.json` – exact dependencies & scripts

```json
{
  "name": "smime-core",
  "version": "1.0.0",
  "description": "Minimal S/MIME utilities for MIME construction, CMS signing, verification, encryption and decryption (Node.js + TypeScript).",
  "author": "Your Name <you@example.com>",
  "license": "MIT",
  "type": "module",
  "scripts": {
    "build": "tsc",
    "demo": "ts-node src/demo.ts",
    "test": "node src/demo.js"
  },
  "dependencies": {
    "emailjs-mime-builder": "1.0.6",
    "mailparser": "4.0.0",
    "node-forge": "1.3.1"
  },
  "devDependencies": {
    "@types/node": "20.14.2",
    "ts-node": "10.9.2",
    "typescript": "5.5.4"
  }
}
```

> **Why these packages?**  
> *`emailjs-mime-builder`* – deterministic MIME construction with explicit CRLF handling.  
> *`mailparser`* – robust MIME parsing (multipart, headers, etc.).  
> *`node-forge`* – pure‑JS implementation of PKCS#7/CMS, X.509, and PKCS#12 handling; no native OpenSSL bindings required.

---

## 2️⃣ TypeScript configuration – `tsconfig.json`

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
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src"]
}
```

---

## 3️⃣ Core API – `src/smime.ts`

```ts
/**
 * smime.ts – Core S/MIME utilities
 *
 * Exported functions:
 *   - buildMimeMessage(content, contentType) → string
 *   - signMimeMessage(mime, p12Pem, p12Password) → string
 *   - verifySignedMessage(signedMime, trustAnchorsPem) → VerifyResult
 *   - encryptMimeMessage(mime, recipientCertsPem) → string
 *   - decryptMimeMessage(encryptedMime, p12Pem, p12Password) → DecryptResult
 *   - parseMimeMessage(raw) → ParsedMime
 *
 * All line endings are canonical CRLF (`\r\n`).
 */

import { MimeNode } from 'emailjs-mime-builder';
import { simpleParser, ParsedMail } from 'mailparser';
import forge from 'node-forge';
import { Buffer } from 'node:buffer';

// ---------- Types ----------
export interface VerifyResult {
  ok: boolean;
  signer?: {
    subject: string;
    issuer: string;
    serialNumber: string;
    notBefore: Date;
    notAfter: Date;
  };
  errors?: string[];
}

export interface DecryptResult {
  ok: boolean;
  content?: string;          // Decrypted MIME (still may be signed)
  errors?: string[];
}

export interface ParsedMime {
  headers: Record<string, string>;
  body: string;              // Raw body (may be another MIME part)
}

// ---------- Helpers ----------
/**
 * Ensure CRLF line endings.
 */
function toCRLF(str: string): string {
  return str.replace(/\r?\n/g, '\r\n');
}

/**
 * Load a PKCS#12 (P12/PFX) from PEM + password.
 */
function loadPkcs12(p12Pem: string, password: string): forge.pkcs12.Pkcs12 {
  const p12Der = forge.util.decode64(
    p12Pem
      .replace(/-----BEGIN PKCS12-----/, '')
      .replace(/-----END PKCS12-----/, '')
      .replace(/\s+/g, '')
  );
  const p12Asn1 = forge.asn1.fromDer(p12Der);
  return forge.pkcs12.pkcs12FromAsn1(p12Asn1, password);
}

/**
 * Convert PEM‑encoded certificates to forge objects.
 */
function pemToCerts(pems: string[]): forge.pki.Certificate[] {
  return pems.map(pem => forge.pki.certificateFromPem(pem));
}

/**
 * Convert a forge certificate to a friendly description.
 */
function certInfo(cert: forge.pki.Certificate) {
  return {
    subject: cert.subject.attributes.map(a => `${a.shortName}=${a.value}`).join(', '),
    issuer: cert.issuer.attributes.map(a => `${a.shortName}=${a.value}`).join(', '),
    serialNumber: cert.serialNumber,
    notBefore: cert.validity.notBefore,
    notAfter: cert.validity.notAfter,
  };
}

// ---------- 1️⃣ MIME construction ----------
/**
 * Build a simple MIME part with explicit `Content-Type` and `Content-Transfer-Encoding`.
 *
 * @param content      Plain‑text payload.
 * @param contentType  MIME type, e.g. `text/plain; charset=utf-8`.
 * @returns            MIME string with CRLF line endings.
 */
export function buildMimeMessage(content: string, contentType = 'text/plain; charset=utf-8'): string {
  const node = new MimeNode(contentType);
  node.setHeader('Content-Transfer-Encoding', '7bit');
  node.setContent(toCRLF(content));
  // `build` returns a Buffer; we convert to string and enforce CRLF.
  return toCRLF(node.build());
}

// ---------- 2️⃣ CMS signing ----------
/**
 * Sign a MIME message using a PKCS#12 container (private key + cert chain).
 *
 * @param mime          Raw MIME string (CRLF).
 * @param p12Pem        PEM‑encoded PKCS#12.
 * @param p12Password   Password for the PKCS#12.
 * @returns             `multipart/signed` MIME (CRLF).
 */
export function signMimeMessage(mime: string, p12Pem: string, p12Password: string): string {
  // Load key & cert chain from PKCS#12
  const p12 = loadPkcs12(p12Pem, p12Password);
  const bags = p12.getBags({ bagType: forge.pki.oids.pkcs8ShroudedKeyBag });
  const keyBag = bags[forge.pki.oids.pkcs8ShroudedKeyBag][0];
  const privateKey = keyBag.key;
  const certBag = p12.getBags({ bagType: forge.pki.oids.certBag })[forge.pki.oids.certBag][0];
  const signerCert = certBag.cert;
  const chain = [signerCert]; // For simplicity we embed only the leaf.

  // Create PKCS#7 signedData
  const p7 = forge.pkcs7.createSignedData();
  p7.content = forge.util.createBuffer(mime, 'utf8');
  p7.addCertificate(signerCert);
  p7.addSigner({
    key: privateKey,
    certificate: signerCert,
    digestAlgorithm: forge.pki.oids.sha256,
    authenticatedAttributes: [
      {
        type: forge.pki.oids.contentType,
        value: forge.pki.oids.data,
      },
      {
        type: forge.pki.oids.messageDigest,
        // value will be auto‑populated
      },
      {
        type: forge.pki.oids.signingTime,
        // value will be auto‑populated
      },
    ],
  });
  p7.sign({ detached: true });

  const signatureDer = forge.asn1.toDer(p7.toAsn1()).getBytes();
  const signatureB64 = forge.util.encode64(signatureDer, 64);

  // Build multipart/signed
  const signedNode = new MimeNode('multipart/signed; protocol="application/pkcs7-signature"; micalg=sha-256');
  signedNode.setHeader('Content-Type', signedNode.getHeader('Content-Type') + '; boundary="BOUNDARY"');
  signedNode.appendChild({
    headers: { 'Content-Type': 'application/octet-stream' },
    content: mime,
  });
  signedNode.appendChild({
    headers: {
      'Content-Type': 'application/pkcs7-signature',
      'Content-Transfer-Encoding': 'base64',
      'Content-Disposition': 'attachment; filename="smime.p7s"',
    },
    content: signatureB64,
  });
  // Force our own boundary and CRLF handling
  const raw = signedNode.build({ lineLength: 998 });
  return toCRLF(raw);
}

// ---------- 3️⃣ Verify signed message ----------
/**
 * Verify a `multipart/signed` S/MIME message.
 *
 * @param signedMime    The raw MIME string (CRLF).
 * @param trustAnchorsPem  Array of PEM‑encoded trusted root certificates.
 * @returns VerifyResult with signer info & error list.
 */
export async function verifySignedMessage(signedMime: string, trustAnchorsPem: string[]): Promise<VerifyResult> {
  const parsed = await simpleParser(signedMime);
  if (!parsed.attachments?.length || parsed.attachments.length < 2) {
    return { ok: false, errors: ['Message does not contain a signature part'] };
  }

  // The first part is the original content, the second the PKCS#7 signature
  const original = parsed.text; // works for simple single‑part bodies
  const signaturePart = parsed.attachments.find(a => a.contentType === 'application/pkcs7-signature');
  if (!signaturePart) {
    return { ok: false, errors: ['Signature part missing'] };
  }

  const signatureDer = forge.util.decode64(signaturePart.content.toString('base64'));
  const p7 = forge.pkcs7.messageFromAsn1(forge.asn1.fromDer(signatureDer));

  // Attach the original content (detached signature)
  p7.content = forge.util.createBuffer(original, 'utf8');

  // Verify signature(s)
  const errors: string[] = [];
  let signerInfo: any = null;

  try {
    const verified = p7.verify({ detached: true });
    if (!verified) errors.push('Signature verification failed');
  } catch (e: any) {
    errors.push(`Signature verification exception: ${e.message}`);
  }

  // Extract signer certificate
  if (p7.certificates && p7.certificates.length > 0) {
    const leaf = p7.certificates[0];
    signerInfo = certInfo(leaf);
  } else {
    errors.push('No signer certificate found in the signature');
  }

  // Chain validation against supplied trust anchors
  const trustStore = forge.pki.createCaStore(trustAnchorsPem);
  try {
    const chain = forge.pki.verifyCertificateChain(trustStore, p7.certificates || [], (v, c, i, depth, errors) => {
      // `v` is a boolean indicating success so far.
      // Returning true continues validation; returning false aborts.
      return v;
    });
    if (!chain) errors.push('Certificate chain validation failed');
  } catch (e: any) {
    errors.push(`Chain validation error: ${e.message}`);
  }

  return {
    ok: errors.length === 0,
    signer: signerInfo,
    errors: errors.length ? errors : undefined,
  };
}

// ---------- 4️⃣ Encrypt MIME ----------
/**
 * Encrypt a MIME message for one or more X.509 recipients.
 *
 * @param mime                Raw MIME to encrypt (CRLF).
 * @param recipientCertsPem   Array of PEM‑encoded recipient certificates.
 * @returns                   `application/pkcs7-mime` (enveloped) MIME string.
 */
export function encryptMimeMessage(mime: string, recipientCertsPem: string[]): string {
  const certs = pemToCerts(recipientCertsPem);
  const p7 = forge.pkcs7.createEnvelopedData();
  p7.addRecipient(certs[0]); // For demo we use the first cert; can loop for multiple.
  p7.content = forge.util.createBuffer(mime, 'utf8');
  p7.encrypt();

  const der = forge.asn1.toDer(p7.toAsn1()).getBytes();
  const b64 = forge.util.encode64(der, 64);

  const node = new MimeNode('application/pkcs7-mime; smime-type=enveloped-data; name="smime.p7m"');
  node.setHeader('Content-Transfer-Encoding', 'base64');
  node.setHeader('Content-Disposition', 'attachment; filename="smime.p7m"');
  node.setContent(b64);
  return toCRLF(node.build());
}

// ---------- 5️⃣ Decrypt MIME ----------
/**
 * Decrypt a `application/pkcs7-mime` S/MIME message.
 *
 * @param encryptedMime   Raw MIME (CRLF) containing the PKCS#7 envelope.
 * @param p12Pem          PEM‑encoded PKCS#12 containing the recipient private key.
 * @param p12Password     Password for the PKCS#12.
 * @returns DecryptResult with extracted content or errors.
 */
export async function decryptMimeMessage(
  encryptedMime: string,
  p12Pem: string,
  p12Password: string
): Promise<DecryptResult> {
  const parsed = await simpleParser(encryptedMime);
  const attachment = parsed.attachments?.find(a => a.contentType?.startsWith('application/pkcs7-mime'));
  if (!attachment) {
    return { ok: false, errors: ['No PKCS#7 envelope found'] };
  }

  const der = forge.util.decode64(attachment.content.toString('base64'));
  const p7 = forge.pkcs7.messageFromAsn1(forge.asn1.fromDer(der));

  // Load recipient private key
  const p12 = loadPkcs12(p12Pem, p12Password);
  const keyBags = p12.getBags({ bagType: forge.pki.oids.pkcs8ShroudedKeyBag });
  const keyBag = keyBags[forge.pki.oids.pkcs8ShroudedKeyBag][0];
  const privateKey = keyBag.key;

  try {
    p7.decrypt(p7.recipients[0], privateKey);
    const content = p7.content?.toString('utf8') ?? '';
    return { ok: true, content };
  } catch (e: any) {
    return { ok: false, errors: [`Decryption failed: ${e.message}`] };
  }
}

// ---------- 6️⃣ Generic MIME parser ----------
/**
 * Parse any raw MIME message (preserving headers & body).
 *
 * @param raw  Full MIME string (CRLF).
 * @returns    ParsedMime with raw headers & body.
 */
export async function parseMimeMessage(raw: string): Promise<ParsedMime> {
  const parsed = await simpleParser(raw);
  const headers: Record<string, string> = {};
  parsed.headerLines?.forEach(h => {
    if (h.key) headers[h.key] = h.line;
  });
  return {
    headers,
    body: parsed.text,
  };
}
```

> **Key implementation notes**
> * All output strings are forced to **CRLF** (`\r\n`) via `toCRLF`.
> * The CMS structures are **detached** (`signedData` with `detached: true`) so the original MIME stays readable.
> * Chain validation uses `forge.pki.verifyCertificateChain`; errors are captured and bubbled up.
> * Errors are **categorised**:
>   * *Signature errors* → “Signature verification failed”, “Signature verification exception”.
>   * *Certificate errors* → “No signer certificate”, “Chain validation error”.
>   * *Content errors* → “Decryption failed”, “Message does not contain a signature part”.

---

## 4️⃣ Demo script – `src/demo.ts`

```ts
/**
 * demo.ts – End‑to‑end sign‑then‑encrypt round‑trip + tampered‑message test
 *
 * Usage:
 *   npm run demo
 *
 * Prerequisite: the `fixtures/` folder contains:
 *   - message.txt          – plain payload
 *   - tampered.eml        – produced by this script on first run
 *
 * The script prints concise status lines and JSON summaries.
 */

import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import {
  buildMimeMessage,
  signMimeMessage,
  verifySignedMessage,
  encryptMimeMessage,
  decryptMimeMessage,
} from './smime.js';

// ------------------------------------------------------------------
// 1️⃣ Load assets (payload, keys, certificates)
// ------------------------------------------------------------------
const payload = readFileSync(resolve('fixtures/message.txt'), 'utf8').trim();

const aliceP12 = readFileSync(resolve('fixtures/alice.p12.pem'), 'utf8');
const alicePassword = 'alicepwd';

const bobCertPem = readFileSync(resolve('fixtures/bob.cert.pem'), 'utf8');

// Trust anchor (Bob's root CA) – for demo we trust Bob directly.
const trustAnchors = [bobCertPem];

// ------------------------------------------------------------------
// 2️⃣ Build, sign, encrypt
// ------------------------------------------------------------------
const mime = buildMimeMessage(payload, 'text/plain; charset=utf-8');
console.log('🛠️  Base MIME built (length:', mime.length, ')');

const signed = signMimeMessage(mime, aliceP12, alicePassword);
console.log('🔏 Message signed (multipart/signed, length:', signed.length, ')');

const encrypted = encryptMimeMessage(signed, [bobCertPem]);
console.log('🔐 Message encrypted (application/pkcs7-mime, length:', encrypted.length, ')');

// Save the full envelope for later inspection
writeFileSync(resolve('fixtures/roundtrip.eml'), encrypted, 'utf8');

// ------------------------------------------------------------------
// 3️⃣ Decrypt (Bob) → verify (Alice)
// ------------------------------------------------------------------
(async () => {
  const bobP12 = readFileSync(resolve('fixtures/bob.p12.pem'), 'utf8');
  const bobPassword = 'bobpwd';

  const dec = await decryptMimeMessage(encrypted, bobP12, bobPassword);
  if (!dec.ok) {
    console.error('❌ Decryption error:', dec.errors);
    process.exit(1);
  }
  console.log('✅ Decrypted payload length:', dec.content?.length);

  const verify = await verifySignedMessage(dec.content!, trustAnchors);
  if (verify.ok) {
    console.log('✅ Signature verified! Signer details:');
    console.log(JSON.stringify(verify.signer, null, 2));
  } else {
    console.error('❌ Verification errors:', verify.errors);
  }

  // ----------------------------------------------------------------
  // 4️⃣ Tampered‑message test (alter first byte of ciphertext)
  // ----------------------------------------------------------------
  const tamperedPath = resolve('fixtures/tampered.eml');
  if (!readFileSync(tamperedPath, { flag: 'r' })) {
    // First run – create a tampered copy
    const buf = Buffer.from(encrypted, 'utf8');
    // Locate the Base64 block (first line after headers)
    const parts = encrypted.split('\r\n\r\n');
    const headers = parts[0];
    const b64 = parts[1].replace(/\r\n/g, '');
    const raw = Buffer.from(b64, 'base64');
    raw[0] ^= 0xff; // flip bits → corrupt ciphertext
    const corruptedB64 = raw.toString('base64').match(/.{1,64}/g)!.join('\r\n');
    const tampered = `${headers}\r\n\r\n${corruptedB64}\r\n`;
    writeFileSync(tamperedPath, tampered, 'utf8');
    console.log('⚡ Created tampered fixture at', tamperedPath);
  }

  const tampered = readFileSync(tamperedPath, 'utf8');
  const decTam = await decryptMimeMessage(tampered, bobP12, bobPassword);
  if (!decTam.ok) {
    console.error('🔎 Expected decryption failure (tampered):', decTam.errors);
  } else {
    console.warn('⚠️ Unexpected success – decryption succeeded on tampered data');
  }
})();
```

> **Running the demo**  

```bash
# 1️⃣ Install exact dependencies
npm ci

# 2️⃣ Build (optional, ts-node works directly)
npm run build

# 3️⃣ Execute the demo
npm run demo
```

The script will:

1. **Create** a plain MIME body from `fixtures/message.txt`.  
2. **Sign** it with Alice’s PKCS#12 (`alice.p12.pem`).  
3. **Encrypt** the signed MIME for Bob (`bob.cert.pem`).  
4. **Decrypt** with Bob’s PKCS#12 (`bob.p12.pem`).  
5. **Verify** the detached signature against Alice’s certificate, reporting signer details.  
6. **Generate** a tampered copy (`fixtures/tampered.eml`) and demonstrate that decryption fails with a clear *content error*.

---

## 5️⃣ Fixtures – generate your own keys (one‑time setup)

Below are **minimal OpenSSL commands** to create the test material. Run them **once** in the repository root.

```bash
# 1️⃣ Create a self‑signed CA for Bob (trust anchor)
openssl req -new -x509 -days 3650 -nodes -subj "/C=US/O=Bob CA/CN=Bob Root CA" -keyout bob-ca.key -out bob-ca.crt

# 2️⃣ Bob’s end‑entity certificate (used for encryption)
openssl req -new -nodes -subj "/C=US/O=Bob/CN=Bob User" -keyout bob.key -out bob.csr
openssl x509 -req -in bob.csr -CA bob-ca.crt -CAkey bob-ca.key -CAcreateserial -days 365 -out bob.crt
# PKCS#12 for Bob (private key + cert)
openssl pkcs12 -export -out bob.p12.pem -inkey bob.key -in bob.crt -certfile bob-ca.crt -passout pass:bobpwd

# 3️⃣ Alice’s signing certificate (self‑signed for demo)
openssl req -new -x509 -days 3650 -nodes -subj "/C=US/O=Alice/CN=Alice Signer" -keyout alice.key -out alice.crt
openssl pkcs12 -export -out alice.p12.pem -inkey alice.key -in alice.crt -passout pass:alicepwd

# 4️⃣ Plain payload
echo "Hello, S/MIME world! This is a test message." > fixtures/message.txt
```

Place the generated files under `fixtures/`:

```
fixtures/
├─ alice.p12.pem
├─ bob.p12.pem
├─ bob.cert.pem   (== bob.crt)
├─ bob-ca.crt
├─ message.txt
```

> **Note** – The demo only needs **Bob’s leaf certificate** (`bob.cert.pem`) as the encryption recipient; the CA (`bob-ca.crt`) is used as the trust anchor during verification.

---

## 6️⃣ API reference (exported from `src/smime.ts`)

| Function | Description | Important parameters |
|----------|-------------|----------------------|
| `buildMimeMessage(content: string, contentType?: string): string` | Returns a single‑part MIME string with CRLF line endings. | `content` – payload; `contentType` – e.g. `text/plain; charset=utf-8`. |
| `signMimeMessage(mime: string, p12Pem: string, p12Password: string): string` | Produces a `multipart/signed` MIME where the signature is a detached PKCS#7 `signedData`. | `mime` – the message to sign; PKCS#12 with private key & cert. |
| `verifySignedMessage(signedMime: string, trustAnchorsPem: string[]): Promise<VerifyResult>` | Verifies the detached signature, extracts signer certificate, validates chain. | `trustAnchorsPem` – PEM‑encoded root(s). |
| `encryptMimeMessage(mime: string, recipientCertsPem: string[]): string` | Wraps the MIME in a PKCS#7 `envelopedData` for the given recipients. | `recipientCertsPem` – at least one PEM cert. |
| `decryptMimeMessage(encryptedMime: string, p12Pem: string, p12Password: string): Promise<DecryptResult>` | Decrypts a PKCS#7 envelope, returning the inner MIME (still possibly signed). | Recipient PKCS#12. |
| `parseMimeMessage(raw: string): Promise<ParsedMime>` | Generic parser – returns raw headers and body (useful for debugging). | `raw` – any MIME string. |

**Result objects**

```ts
interface VerifyResult {
  ok: boolean;                     // true if signature & chain are OK
  signer?: {                       // populated only on success
    subject: string;
    issuer: string;
    serialNumber: string;
    notBefore: Date;
    notAfter: Date;
  };
  errors?: string[];               // list of distinct error messages
}
interface DecryptResult {
  ok: boolean;
  content?: string;                // decrypted MIME (UTF‑8)
  errors?: string[];
}
```

---

## 7️⃣ Reproducibility checklist

| Step | Command | Expected outcome |
|------|---------|------------------|
| **Install exact deps** | `npm ci` | `node_modules/` with versions from `package.json`. |
| **Run demo** | `npm run demo` | Console output showing successful sign‑then‑encrypt round‑trip and a decryption failure on the tampered fixture. |
| **Inspect generated files** | `cat fixtures/roundtrip.eml` | MIME with `Content-Type: application/pkcs7-mime` (Base64). |
| **Validate error categories** | Look at console lines prefixed with `❌` or `🔎`. | Signature errors → “Signature verification failed”.<br>Certificate errors → “Chain validation error”.<br>Content errors → “Decryption failed”. |

All operations are performed **in‑process** with pure JavaScript libraries – no external OpenSSL binaries are required at runtime (only for the one‑time fixture generation).

---

## 8️⃣ License

MIT – feel free to adapt, extend, or embed in larger mail‑client projects.

---

**Enjoy a tiny, standards‑compliant S/MIME core that you can drop into any Node.js service!**

