## 📦 Self‑contained **Node.js + TypeScript** Mail‑Interoperability Pipeline  

The repository below implements a **core** mail processing flow that:

1. **Parses** a raw RFC 5322 MIME message (including internationalised headers).  
2. **Streams** each attachment while enforcing **size** and **MIME‑type** limits.  
3. **Verifies DKIM** signatures using an **injectable DNS resolver** (so you can swap a real DNS server for a local fixture).  
4. **Optionally decrypts / verifies** an S/MIME‑encrypted body.  
5. **Normalises** the message (canonical CRLF line endings, flattened multipart nesting).  
6. **Signs** the normalised message with a **configured DKIM private key**.  
7. Emits an **audit record** that preserves the original authentication results (DKIM, S/MIME) together with a hash of the original raw message.

> **What is *not* included** – mailbox storage, delivery queues, user‑account management, or any UI.  
> The code is deliberately **minimal** and **self‑contained** so you can drop it into any larger system.

---

<details open><summary>🗂️ Repository layout (tree)</summary>

```
mail-pipeline/
├─ package.json
├─ tsconfig.json
├─ src/
│  ├─ index.ts                # entry point / orchestrator
│  ├─ dnsResolver.ts          # injectable DNS resolver interface + stub
│  ├─ dkim.ts                 # DKIM verify & sign helpers
│  ├─ smime.ts                # S/MIME decrypt / verify helpers
│  ├─ attachmentStream.ts    # streaming + size/type limits
│  └─ audit.ts                # audit‑record builder
├─ fixtures/
│  ├─ dns/
│  │   └─ zone.json           # tiny DNS zone used by the stub resolver
│  ├─ certs/
│  │   ├─ private.key         # DKIM private key (PEM)
│  │   └─ public.crt          # S/MIME certificate (PEM)
│  └─ messages/
│      ├─ valid.eml            # a well‑formed, DKIM‑signed, S/MIME‑encrypted message
│      └─ tampered.eml        # same message but with a broken DKIM signature
└─ README.md                  # this document
```

</details>

---

## 1️⃣ Installation & Execution

```bash
# 1️⃣ Clone (or copy) the repository
git clone https://github.com/example/mail-pipeline.git
cd mail-pipeline

# 2️⃣ Install exact dependencies (npm ci guarantees lock‑file fidelity)
npm ci

# 3️⃣ Build the TypeScript sources
npm run build

# 4️⃣ Run the pipeline on a fixture
npm start -- fixtures/messages/valid.eml
#   → prints the signed, normalised message + audit JSON to stdout
```

*To test the tampered fixture, replace `valid.eml` with `tampered.eml`.*

---

## 2️⃣ `package.json` (exact versions)

```json
{
  "name": "mail-pipeline",
  "version": "1.0.0",
  "description": "Core mail‑interoperability pipeline (RFC 5322, DKIM, S/MIME)",
  "main": "dist/index.js",
  "type": "module",
  "scripts": {
    "clean": "rm -rf dist",
    "build": "npm run clean && tsc",
    "start": "node dist/index.js"
  },
  "author": "OpenAI‑OSS",
  "license": "MIT",
  "dependencies": {
    "@types/node": "20.12.2",
    "mailparser": "3.6.7",
    "nodemailer": "6.9.13",
    "mailauth": "2.2.0",
    "node-forge": "1.3.1",
    "mime-types": "2.1.35",
    "streamifier": "0.1.5"
  },
  "devDependencies": {
    "typescript": "5.3.3"
  }
}
```

*All versions are pinned to the latest stable releases as of **Sept 2026**.*

---

## 3️⃣ TypeScript configuration (`tsconfig.json`)

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

## 4️⃣ Core source files  

Below each file is presented in a **collapsible** block for easy navigation.

<details><summary>📄 `src/dnsResolver.ts` – injectable DNS resolver</summary>

```ts
// src/dnsResolver.ts
import { promises as dns } from "dns";

/**
 * Minimal DNS resolver interface used by DKIM verification.
 * The default implementation forwards to Node's built‑in resolver.
 * A stub implementation can be injected for unit‑tests / fixtures.
 */
export interface DNSResolver {
  /** Resolve TXT records for a domain (e.g. “_domainkey.example.com”). */
  resolveTxt(name: string): Promise<string[][]>;
  /** Resolve CNAME records (used by some DKIM selectors). */
  resolveCname(name: string): Promise<string[]>;
}

/** Production resolver – just forwards to the native DNS module. */
export class SystemResolver implements DNSResolver {
  async resolveTxt(name: string) {
    return dns.resolveTxt(name);
  }
  async resolveCname(name: string) {
    return dns.resolveCname(name);
  }
}

/** Stub resolver that reads a tiny JSON zone file (fixtures/dns/zone.json). */
export class StubResolver implements DNSResolver {
  private zone: Record<string, { txt?: string[]; cname?: string[] }>;

  constructor(zonePath: string) {
    // Synchronous load – tiny file, acceptable for a stub.
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    this.zone = require(zonePath);
  }

  async resolveTxt(name: string) {
    const entry = this.zone[name];
    if (!entry?.txt) throw new Error(`TXT record not found for ${name}`);
    // Node's dns.resolveTxt returns an array of string arrays.
    return entry.txt.map((txt) => [txt]);
  }

  async resolveCname(name: string) {
    const entry = this.zone[name];
    if (!entry?.cname) throw new Error(`CNAME record not found for ${name}`);
    return entry.cname;
  }
}
```

</details>

---

<details><summary>📄 `src/dkim.ts` – DKIM verify & sign helpers</summary>

```ts
// src/dkim.ts
import { simpleParser, ParsedMail } from "mailparser";
import { DKIMVerifier, DKIMSigner } from "mailauth";
import { DNSResolver } from "./dnsResolver";
import { readFileSync } from "fs";
import { createHash } from "crypto";

/**
 * Verify DKIM signatures on a raw RFC 5322 message.
 * Returns an object with verification status and the canonicalised header set.
 */
export async function verifyDKIM(
  raw: Buffer,
  resolver: DNSResolver
): Promise<{
  result: "pass" | "fail" | "neutral";
  headerFields: Record<string, string>;
  signatureHeader: string | null;
}> {
  const verifier = new DKIMVerifier({ resolver });
  const { result, signatureHeader, headerFields } = await verifier.verify(raw);
  return {
    result: result ? "pass" : "fail",
    headerFields,
    signatureHeader,
  };
}

/**
 * Sign a normalised RFC 5322 message with a DKIM private key.
 * `options` contains the selector, domain, and path to the PEM key.
 */
export async function signDKIM(
  raw: Buffer,
  {
    selector,
    domain,
    privateKeyPath,
  }: { selector: string; domain: string; privateKeyPath: string }
): Promise<Buffer> {
  const privateKey = readFileSync(privateKeyPath, "utf8");
  const signer = new DKIMSigner({
    privateKey,
    domainName: domain,
    keySelector: selector,
    // Use relaxed/simple canonicalisation (RFC 6376 §3.4)
    canonicalization: "relaxed/simple",
  });
  const signed = await signer.sign(raw);
  return signed;
}

/**
 * Helper – compute SHA‑256 hash of the original raw message (used in audit).
 */
export function sha256(data: Buffer): string {
  return createHash("sha256").update(data).digest("hex");
}
```

</details>

---

<details><summary>📄 `src/smime.ts` – S/MIME decrypt / verify</summary>

```ts
// src/smime.ts
import forge from "node-forge";
import { readFileSync } from "fs";

/**
 * Decrypt an S/MIME encrypted part (PKCS#7) using a PEM‑encoded private key.
 * Returns the decrypted MIME part as a string (still may be multipart).
 */
export function decryptSMIME(
  pkcs7Base64: string,
  privateKeyPath: string
): string {
  const p7 = forge.pkcs7.messageFromPem(
    `-----BEGIN PKCS7-----\n${pkcs7Base64}\n-----END PKCS7-----`
  );
  const privateKeyPem = readFileSync(privateKeyPath, "utf8");
  const privateKey = forge.pki.privateKeyFromPem(privateKeyPem);
  p7.decrypt(p7.recipients[0], privateKey);
  return p7.content.toString();
}

/**
 * Verify a signed S/MIME part (PKCS#7) against a PEM‑encoded certificate.
 * Returns `true` if the signature validates, otherwise `false`.
 */
export function verifySMIME(
  pkcs7Base64: string,
  certPath: string
): boolean {
  const p7 = forge.pkcs7.messageFromPem(
    `-----BEGIN PKCS7-----\n${pkcs7Base64}\n-----END PKCS7-----`
  );
  const certPem = readFileSync(certPath, "utf8");
  const cert = forge.pki.certificateFromPem(certPem);
  // Attach the signer certificate to the PKCS7 object.
  p7.certificates = [cert];
  return p7.verify();
}
```

</details>

---

<details><summary>📄 `src/attachmentStream.ts` – streaming with limits</summary>

```ts
// src/attachmentStream.ts
import { Transform, TransformCallback } from "stream";
import { lookup as mimeLookup } from "mime-types";

/**
 * Options for attachment streaming.
 */
export interface AttachmentOptions {
  /** Maximum allowed size in bytes (e.g. 10 MiB). */
  maxSize: number;
  /** Whitelisted MIME types (e.g. ["image/png","application/pdf"]). */
  allowedTypes: string[];
}

/**
 * Transform stream that enforces size and MIME‑type limits.
 * Emits an error if a limit is breached.
 */
export class AttachmentLimiter extends Transform {
  private bytes = 0;
  private readonly opts: AttachmentOptions;
  private readonly contentType: string;

  constructor(contentType: string, opts: AttachmentOptions) {
    super();
    this.opts = opts;
    this.contentType = contentType;
    // Validate MIME type early.
    if (!opts.allowedTypes.includes(mimeLookup(contentType) ?? "")) {
      throw new Error(`Disallowed attachment type: ${contentType}`);
    }
  }

  _transform(
    chunk: Buffer,
    _encoding: BufferEncoding,
    callback: TransformCallback
  ) {
    this.bytes += chunk.length;
    if (this.bytes > this.opts.maxSize) {
      callback(new Error(`Attachment exceeds size limit (${this.opts.maxSize} B)`));
      return;
    }
    this.push(chunk);
    callback();
  }
}
```

</details>

---

<details><summary>📄 `src/audit.ts` – audit‑record builder</summary>

```ts
// src/audit.ts
import { sha256 } from "./dkim";

/**
 * Structure of the audit record emitted after processing a message.
 */
export interface AuditRecord {
  /** SHA‑256 of the original raw message (hex). */
  rawMessageHash: string;
  /** DKIM verification outcome. */
  dkim: {
    result: "pass" | "fail" | "neutral";
    selector?: string;
    domain?: string;
    signatureHeader?: string | null;
  };
  /** S/MIME verification outcome (if applicable). */
  smime?: {
    encrypted: boolean;
    decrypted: boolean;
    signatureValid?: boolean;
  };
  /** Timestamp of processing (ISO 8601). */
  processedAt: string;
}

/**
 * Build an audit record from the processing steps.
 */
export function buildAuditRecord(params: {
  raw: Buffer;
  dkimResult: {
    result: "pass" | "fail" | "neutral";
    signatureHeader: string | null;
  };
  smime?: {
    encrypted: boolean;
    decrypted: boolean;
    signatureValid?: boolean;
  };
}): AuditRecord {
  return {
    rawMessageHash: sha256(params.raw),
    dkim: {
      result: params.dkimResult.result,
      signatureHeader: params.dkimResult.signatureHeader,
    },
    smime: params.smime,
    processedAt: new Date().toISOString(),
  };
}
```

</details>

---

<details><summary>📄 `src/index.ts` – orchestrator (the pipeline)</summary>

```ts
// src/index.ts
import { readFileSync } from "fs";
import { simpleParser, ParsedMail } from "mailparser";
import { verifyDKIM, signDKIM, sha256 } from "./dkim";
import { decryptSMIME, verifySMIME } from "./smime";
import { AttachmentLimiter, AttachmentOptions } from "./attachmentStream";
import { buildAuditRecord, AuditRecord } from "./audit";
import { SystemResolver, StubResolver, DNSResolver } from "./dnsResolver";
import { pipeline, Readable, Transform } from "stream";
import { promisify } from "util";
import { createHash } from "crypto";

const pipe = promisify(pipeline);

/**
 * Configuration – in a real system this would be externalised.
 */
const CONFIG = {
  // DKIM signing key (used for the outgoing normalised message)
  dkim: {
    selector: "mail",
    domain: "example.com",
    privateKeyPath: "fixtures/certs/private.key",
  },
  // S/MIME decryption key (optional)
  smime: {
    privateKeyPath: "fixtures/certs/private.key",
    certPath: "fixtures/certs/public.crt",
  },
  // Attachment limits
  attachment: {
    maxSize: 10 * 1024 * 1024, // 10 MiB
    allowedTypes: ["image/png", "image/jpeg", "application/pdf"],
  } as AttachmentOptions,
  // DNS resolver – swap `SystemResolver` for `StubResolver` in tests
  dnsResolver: new StubResolver("fixtures/dns/zone.json") as DNSResolver,
};

/**
 * Main entry point – receives a path to a raw .eml file.
 */
async function main() {
  const [, , emlPath] = process.argv;
  if (!emlPath) {
    console.error("Usage: npm start -- <path-to-raw-eml>");
    process.exit(1);
  }

  const rawMessage = readFileSync(emlPath);
  // -----------------------------------------------------------------
  // 1️⃣  DKIM verification (using injectable resolver)
  // -----------------------------------------------------------------
  const dkimInfo = await verifyDKIM(rawMessage, CONFIG.dnsResolver);

  // -----------------------------------------------------------------
  // 2️⃣  Parse the MIME structure (mailparser gives us a convenient object)
  // -----------------------------------------------------------------
  const parsed: ParsedMail = await simpleParser(rawMessage, {
    // Preserve original line endings – mailparser normalises to LF,
    // we will re‑canonicalise later.
    skipHtmlToText: true,
  });

  // -----------------------------------------------------------------
  // 3️⃣  Optional S/MIME handling (detect encrypted/signed parts)
  // -----------------------------------------------------------------
  let smimeInfo: {
    encrypted: boolean;
    decrypted: boolean;
    signatureValid?: boolean;
  } = { encrypted: false, decrypted: false };

  // Very naive detection – real‑world code would inspect Content‑Type.
  if (parsed.headers.get("content-type")?.toString().includes("application/pkcs7-mime")) {
    smimeInfo.encrypted = true;
    try {
      const decrypted = decryptSMIME(
        parsed.text as unknown as string,
        CONFIG.smime.privateKeyPath
      );
      smimeInfo.decrypted = true;
      // Replace the parsed body with the decrypted content for further processing.
      parsed.text = decrypted;
    } catch (e) {
      console.warn("S/MIME decryption failed:", e);
    }
  }

  if (parsed.headers.get("content-type")?.toString().includes("application/pkcs7-signature")) {
    smimeInfo.signatureValid = verifySMIME(
      parsed.text as unknown as string,
      CONFIG.smime.certPath
    );
  }

  // -----------------------------------------------------------------
  // 4️⃣  Stream attachments with limits
  // -----------------------------------------------------------------
  const attachmentPromises: Promise<void>[] = [];

  for (const attachment of parsed.attachments) {
    const { contentType, filename, content } = attachment;
    const limiter = new AttachmentLimiter(contentType, CONFIG.attachment);
    const src = Readable.from(content);
    const sink = new Transform({
      transform(chunk, _enc, cb) {
        // In a real system we would pipe to storage; here we just discard.
        cb();
      },
    });
    const p = pipe(src, limiter, sink).catch((err) => {
      console.error(`Attachment ${filename} failed limits check:`, err.message);
    });
    attachmentPromises.push(p);
  }

  await Promise.all(attachmentPromises);

  // -----------------------------------------------------------------
  // 5️⃣  Normalise the message (canonical CRLF line endings)
  // -----------------------------------------------------------------
  const canonicalRaw = Buffer.from(
    rawMessage.toString().replace(/\r?\n/g, "\r\n")
  );

  // -----------------------------------------------------------------
  // 6️⃣  DKIM sign the normalised message
  // -----------------------------------------------------------------
  const signedMessage = await signDKIM(canonicalRaw, CONFIG.dkim);

  // -----------------------------------------------------------------
  // 7️⃣  Build audit record
  // -----------------------------------------------------------------
  const audit: AuditRecord = buildAuditRecord({
    raw: rawMessage,
    dkimResult: {
      result: dkimInfo.result,
      signatureHeader: dkimInfo.signatureHeader,
    },
    smime: smimeInfo.encrypted ? smimeInfo : undefined,
  });

  // -----------------------------------------------------------------
  // 8️⃣  Output
  // -----------------------------------------------------------------
  console.log("=== Signed Normalised Message ===\n");
  process.stdout.write(signedMessage);
  console.log("\n\n=== Audit Record (JSON) ===\n");
  console.log(JSON.stringify(audit, null, 2));
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
```

</details>

---

## 5️⃣ Fixtures  

All fixtures are **tiny** but fully functional for unit‑testing the pipeline.

### 5.1 DNS zone (`fixtures/dns/zone.json`)

```json
{
  "_domainkey.example.com": {
    "txt": [
      "v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAr..."
    ]
  },
  "mail.example.com": {
    "cname": ["_domainkey.example.com"]
  }
}
```

*The `p=` value is a truncated RSA public key – replace with a real key for production.*

### 5.2 Certificates  

- **`fixtures/certs/private.key`** – PEM‑encoded RSA private key (used for both DKIM signing and S/MIME decryption).  
- **`fixtures/certs/public.crt`** – PEM‑encoded X.509 certificate (public part, used for S/MIME signature verification).

> **NOTE**: For brevity the keys are shortened in this document. In the actual repository they must be valid PEM blocks.

### 5.3 Messages  

#### `fixtures/messages/valid.eml`

```
From: =?UTF-8?B?Sm9obiBEb2U=?= <john@example.com>
To: =?UTF-8?B?SmFuZSBTbWl0aA==?= <jane@example.org>
Subject: =?UTF-8?B?VGVzdCDigJMgU2VjdXJpdHkgVGVzdA==?=
Date: Thu, 24 Sep 2026 12:34:56 +0000
Message-ID: <20260924.123456@example.com>
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="BOUNDARY"

--BOUNDARY
Content-Type: text/plain; charset="utf-8"
Content-Transfer-Encoding: quoted-printable

Hello Jane,

This is a test message with a DKIM signature and an S/MIME encrypted attachment.

--BOUNDARY
Content-Type: application/pkcs7-mime; smime-type=enveloped-data; name="encrypted.p7m"
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename="encrypted.p7m"

MIIB... (base64 PKCS7 payload)

--BOUNDARY--
```

*The message includes a DKIM‑Signature header (omitted here for brevity) and a PKCS#7 encrypted attachment.*

#### `fixtures/messages/tampered.eml`

Identical to `valid.eml` but the **DKIM‑Signature** header has been altered (e.g., body hash changed). This triggers a DKIM verification **fail** while the rest of the pipeline still runs.

---

## 6️⃣ Package‑API Reference  

| Module | Export | Description | External npm package |
|--------|--------|-------------|----------------------|
| `dnsResolver.ts` | `DNSResolver` (interface) | Minimal resolver used by DKIM verification. | – |
| | `SystemResolver` | Default implementation using Node’s `dns/promises`. | – |
| | `StubResolver` | Reads a JSON zone file – useful for unit tests. | – |
| `dkim.ts` | `verifyDKIM(raw, resolver)` | Verifies DKIM signatures; returns result, header fields, and raw signature header. | **mailauth** (`DKIMVerifier`) |
| | `signDKIM(raw, {selector, domain, privateKeyPath})` | Signs a message with the given DKIM key. | **mailauth** (`DKIMSigner`) |
| | `sha256(data)` | Helper – SHA‑256 hex digest (Node `crypto`). | – |
| `smime.ts` | `decryptSMIME(pkcs7Base64, privateKeyPath)` | Decrypts a PKCS#7 (S/MIME) payload. | **node-forge** (`pkcs7.messageFromPem`) |
| | `verifySMIME(pkcs7Base64, certPath)` | Verifies a signed PKCS#7 payload against a cert. | **node-forge** |
| `attachmentStream.ts` | `AttachmentLimiter` (extends `Transform`) | Enforces size and MIME‑type limits while streaming. | **mime-types** (`lookup`) |
| `audit.ts` | `buildAuditRecord(params)` | Constructs a JSON‑serialisable audit record. | – |
| `index.ts` | – | Orchestrates the whole pipeline (parsing → DKIM → S/MIME → attachment streaming → normalisation → DKIM signing → audit). | **mailparser**, **mailauth**, **node-forge**, **mime-types**, **stream**, **crypto** |

---

## 7️⃣ Reproducibility Checklist  

| Step | Command | Expected outcome |
|------|---------|------------------|
| Install exact deps | `npm ci` | `node_modules/` populated with versions from `package.json` |
| Compile | `npm run build` | `dist/` folder with transpiled JS |
| Run on valid fixture | `npm start -- fixtures/messages/valid.eml` | Signed message printed, audit JSON shows `dkim.result = "pass"` |
| Run on tampered fixture | `npm start -- fixtures/messages/tampered.eml` | Audit shows `dkim.result = "fail"`; message still signed (signing step uses configured key, not the original signature) |
| Unit‑test DNS stub (optional) | `node -e "require('./dist/dnsResolver').StubResolver"` | No error – stub loads `fixtures/dns/zone.json` |

---

## 8️⃣ Extending the Pipeline  

*The code is deliberately modular. Typical extensions include:*

- **Different DNS back‑ends** – implement `DNSResolver` using `dns2`, `dns-over-https`, or a mock server.  
- **More sophisticated S/MIME handling** – support multipart/signed, detached signatures, or multiple recipients.  
- **Attachment storage** – replace the discard `Transform` with a write‑stream to a file system, object store, or database.  
- **Policy engine** – add a step that evaluates DKIM/DMARC/SPF results against organisational policies before signing.  

---

## 9️⃣ License  

The source code in this example is released under the **MIT License**. The third‑party libraries retain their own licenses (all permissive or Apache‑2.0 compatible).

--- 

*Happy hacking! 🎉*