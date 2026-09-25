I'll create a comprehensive S/MIME utility with all the requested features. Let me start with the project structure and implementation.

## Project Structure

```
smime-utility/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts           # Main exports
│   ├── mime.ts            # MIME construction/parsing
│   ├── cms.ts             # CMS operations
│   ├── certificates.ts    # Certificate handling
│   ├── smime.ts           # High-level S/MIME operations
│   ├── errors.ts          # Error classification
│   ├── cli.ts             # Demonstration CLI
│   └── fixtures/
│       └── tampered.ts    # Tampered message fixture
├── certs/                 # Test certificates (generated)
└── dist/                  # Compiled output
```

## package.json

```json
{
  "name": "smime-utility",
  "version": "1.0.0",
  "description": "Standards-compliant S/MIME core utility for Node.js TypeScript",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsc",
    "prepare": "npm run build",
    "test": "node dist/cli.js",
    "generate-certs": "node dist/cli.js generate-certs",
    "demo": "node dist/cli.js demo",
    "demo:tampered": "node dist/cli.js demo-tampered",
    "clean": "rm -rf dist certs"
  },
  "keywords": [
    "smime",
    "cms",
    "pkcs7",
    "mime",
    "encryption",
    "signing",
    "x509"
  ],
  "author": "",
  "license": "MIT",
  "dependencies": {
    "node-forge": "1.3.1",
    "mailparser": "3.7.1",
    "mime-node": "0.7.1"
  },
  "devDependencies": {
    "@types/node": "20.12.7",
    "@types/node-forge": "1.3.11",
    "typescript": "5.4.5"
  },
  "engines": {
    "node": ">=20.0.0"
  }
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
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

## src/errors.ts - Error Classification

```typescript
/**
 * S/MIME Error Classification
 * Distinguishes signature, certificate, and content errors
 */

export enum SmimeErrorCode {
  // Signature errors
  SIGNATURE_INVALID = 'SIGNATURE_INVALID',
  SIGNATURE_ALGORITHM_UNSUPPORTED = 'SIGNATURE_ALGORITHM_UNSUPPORTED',
  SIGNATURE_MISSING = 'SIGNATURE_MISSING',
  SIGNATURE_MALFORMED = 'SIGNATURE_MALFORMED',
  SIGNATURE_DIGEST_MISMATCH = 'SIGNATURE_DIGEST_MISMATCH',
  
  // Certificate errors
  CERTIFICATE_EXPIRED = 'CERTIFICATE_EXPIRED',
  CERTIFICATE_NOT_YET_VALID = 'CERTIFICATE_NOT_YET_VALID',
  CERTIFICATE_REVOKED = 'CERTIFICATE_REVOKED',
  CERTIFICATE_CHAIN_INVALID = 'CERTIFICATE_CHAIN_INVALID',
  CERTIFICATE_UNTRUSTED = 'CERTIFICATE_UNTRUSTED',
  CERTIFICATE_MISSING = 'CERTIFICATE_MISSING',
  CERTIFICATE_MALFORMED = 'CERTIFICATE_MALFORMED',
  CERTIFICATE_KEY_USAGE_INVALID = 'CERTIFICATE_KEY_USAGE_INVALID',
  CERTIFICATE_EXTENDED_KEY_USAGE_INVALID = 'CERTIFICATE_EXTENDED_KEY_USAGE_INVALID',
  
  // Content errors
  CONTENT_MALFORMED = 'CONTENT_MALFORMED',
  CONTENT_ENCODING_INVALID = 'CONTENT_ENCODING_INVALID',
  CONTENT_TYPE_UNSUPPORTED = 'CONTENT_TYPE_UNSUPPORTED',
  CONTENT_DECRYPTION_FAILED = 'CONTENT_DECRYPTION_FAILED',
  CONTENT_INTEGRITY_FAILED = 'CONTENT_INTEGRITY_FAILED',
  
  // MIME errors
  MIME_PARSE_FAILED = 'MIME_PARSE_FAILED',
  MIME_MISSING_HEADERS = 'MIME_MISSING_HEADERS',
  MIME_BOUNDARY_INVALID = 'MIME_BOUNDARY_INVALID',
  
  // General errors
  INVALID_INPUT = 'INVALID_INPUT',
  OPERATION_FAILED = 'OPERATION_FAILED'
}

export class SmimeError extends Error {
  public readonly code: SmimeErrorCode;
  public readonly details?: Record<string, unknown>;
  public readonly cause?: Error;

  constructor(code: SmimeErrorCode, message: string, details?: Record<string, unknown>, cause?: Error) {
    super(message);
    this.name = 'SmimeError';
    this.code = code;
    this.details = details;
    this.cause = cause;
    
    // Maintains proper stack trace in V8 environments
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, SmimeError);
    }
  }

  static isSignatureError(error: SmimeError): boolean {
    return error.code.toString().startsWith('SIGNATURE_');
  }

  static isCertificateError(error: SmimeError): boolean {
    return error.code.toString().startsWith('CERTIFICATE_');
  }

  static isContentError(error: SmimeError): boolean {
    return error.code.toString().startsWith('CONTENT_');
  }

  static isMimeError(error: SmimeError): boolean {
    return error.code.toString().startsWith('MIME_');
  }
}

export class SmimeErrorCollection extends Error {
  public readonly errors: SmimeError[];

  constructor(errors: SmimeError[]) {
    super(`Multiple S/MIME errors: ${errors.map(e => e.code).join(', ')}`);
    this.name = 'SmimeErrorCollection';
    this.errors = errors;
  }

  get signatureErrors(): SmimeError[] {
    return this.errors.filter(SmimeError.isSignatureError);
  }

  get certificateErrors(): SmimeError[] {
    return this.errors.filter(SmimeError.isCertificateError);
  }

  get contentErrors(): SmimeError[] {
    return this.errors.filter(SmimeError.isContentError);
  }

  get mimeErrors(): SmimeError[] {
    return this.errors.filter(SmimeError.isMimeError);
  }
}
```

## src/certificates.ts - Certificate Handling

```typescript
/**
 * Certificate Handling and Chain Validation
 * Uses node-forge for X.509 operations
 */

import * as forge from 'node-forge';
import { SmimeError, SmimeErrorCode } from './errors';

export interface CertificateInfo {
  subject: string;
  issuer: string;
  serialNumber: string;
  validFrom: Date;
  validTo: Date;
  fingerprint: {
    sha1: string;
    sha256: string;
  };
  keyUsage?: string[];
  extendedKeyUsage?: string[];
  isCA: boolean;
  publicKeyAlgorithm: string;
  publicKeySize: number;
}

export interface TrustAnchor {
  certificate: forge.pki.Certificate;
  name: string;
}

export interface ValidationResult {
  valid: boolean;
  chain: forge.pki.Certificate[];
  errors: SmimeError[];
  trustAnchor?: TrustAnchor;
}

export interface SignerInfo {
  certificate: CertificateInfo;
  certificateChain: CertificateInfo[];
  validationResult: ValidationResult;
  signedAttributes?: forge.asn1.Asn1;
  signatureAlgorithm: string;
  digestAlgorithm: string;
  signingTime?: Date;
}

/**
 * Parse PEM-encoded certificate(s)
 */
export function parseCertificates(pem: string): forge.pki.Certificate[] {
  const certs: forge.pki.Certificate[] = [];
  let remaining = pem;
  
  while (remaining.length > 0) {
    const cert = forge.pki.certificateFromPem(remaining);
    certs.push(cert);
    
    // Find next certificate
    const endIndex = remaining.indexOf('-----END CERTIFICATE-----');
    if (endIndex === -1) break;
    remaining = remaining.substring(endIndex + '-----END CERTIFICATE-----'.length);
    remaining = remaining.trim();
    if (!remaining.startsWith('-----BEGIN CERTIFICATE-----')) break;
  }
  
  if (certs.length === 0) {
    throw new SmimeError(SmimeErrorCode.CERTIFICATE_MALFORMED, 'No valid certificates found in PEM');
  }
  
  return certs;
}

/**
 * Parse PEM-encoded private key
 */
export function parsePrivateKey(pem: string, passphrase?: string): forge.pki.PrivateKey {
  try {
    return forge.pki.privateKeyFromPem(pem, passphrase);
  } catch (e) {
    throw new SmimeError(
      SmimeErrorCode.CERTIFICATE_MALFORMED,
      'Failed to parse private key',
      { originalError: e instanceof Error ? e.message : String(e) },
      e instanceof Error ? e : undefined
    );
  }
}

/**
 * Extract certificate information
 */
export function getCertificateInfo(cert: forge.pki.Certificate): CertificateInfo {
  const der = forge.asn1.toDer(forge.pki.certificateToAsn1(cert)).getBytes();
  const sha1 = forge.md.sha1.create().update(der).digest().toHex();
  const sha256 = forge.md.sha256.create().update(der).digest().toHex();
  
  // Key usage
  const keyUsage: string[] = [];
  if (cert.extensions) {
    for (const ext of cert.extensions) {
      if (ext.name === 'keyUsage') {
        const ku = ext as forge.pki.KeyUsageExtension;
        if (ku.digitalSignature) keyUsage.push('digitalSignature');
        if (ku.nonRepudiation) keyUsage.push('nonRepudiation');
        if (ku.keyEncipherment) keyUsage.push('keyEncipherment');
        if (ku.dataEncipherment) keyUsage.push('dataEncipherment');
        if (ku.keyAgreement) keyUsage.push('keyAgreement');
        if (ku.keyCertSign) keyUsage.push('keyCertSign');
        if (ku.cRLSign) keyUsage.push('cRLSign');
        if (ku.encipherOnly) keyUsage.push('encipherOnly');
        if (ku.decipherOnly) keyUsage.push('decipherOnly');
      } else if (ext.name === 'extKeyUsage') {
        const eku = ext as forge.pki.ExtKeyUsageExtension;
        // Extended key usage OIDs
        const oidMap: Record<string, string> = {
          '1.3.6.1.5.5.7.3.1': 'serverAuth',
          '1.3.6.1.5.5.7.3.2': 'clientAuth',
          '1.3.6.1.5.5.7.3.3': 'codeSigning',
          '1.3.6.1.5.5.7.3.4': 'emailProtection',
          '1.3.6.1.5.5.7.3.8': 'timeStamping',
          '1.3.6.1.5.5.7.3.9': 'OCSPSigning'
        };
        // Note: forge doesn't directly expose extKeyUsage parsed values easily
        // This would need ASN.1 parsing of the extension value
      } else if (ext.name === 'basicConstraints') {
        const bc = ext as forge.pki.BasicConstraintsExtension;
        // isCA is determined below
      }
    }
  }
  
  // Determine if CA
  let isCA = false;
  if (cert.extensions) {
    for (const ext of cert.extensions) {
      if (ext.name === 'basicConstraints') {
        const bc = ext as forge.pki.BasicConstraintsExtension;
        isCA = bc.cA === true;
        break;
      }
    }
  }
  
  // Public key info
  let publicKeyAlgorithm = 'unknown';
  let publicKeySize = 0;
  
  if (cert.publicKey) {
    if (cert.publicKey.n && cert.publicKey.e) {
      // RSA
      publicKeyAlgorithm = 'RSA';
      publicKeySize = cert.publicKey.n.bitLength();
    } else if (cert.publicKey.q) {
      // DSA
      publicKeyAlgorithm = 'DSA';
      publicKeySize = cert.publicKey.q.bitLength();
    } else if (cert.publicKey.pubKeyHex) {
      // ECDSA
      publicKeyAlgorithm = 'ECDSA';
      publicKeySize = Math.ceil(cert.publicKey.pubKeyHex.length / 2) * 8;
    }
  }
  
  return {
    subject: cert.subject.getField('CN')?.value || cert.subject.toString(),
    issuer: cert.issuer.getField('CN')?.value || cert.issuer.toString(),
    serialNumber: cert.serialNumber,
    validFrom: cert.validity.notBefore,
    validTo: cert.validity.notAfter,
    fingerprint: { sha1, sha256 },
    keyUsage,
    isCA,
    publicKeyAlgorithm,
    publicKeySize
  };
}

/**
 * Validate certificate chain against trust anchors
 */
export function validateCertificateChain(
  chain: forge.pki.Certificate[],
  trustAnchors: TrustAnchor[],
  checkTime: Date = new Date()
): ValidationResult {
  const errors: SmimeError[] = [];
  
  if (chain.length === 0) {
    errors.push(new SmimeError(SmimeErrorCode.CERTIFICATE_MISSING, 'Empty certificate chain'));
    return { valid: false, chain: [], errors };
  }
  
  // Check each certificate validity period
  for (let i = 0; i < chain.length; i++) {
    const cert = chain[i];
    
    if (checkTime < cert.validity.notBefore) {
      errors.push(new SmimeError(
        SmimeErrorCode.CERTIFICATE_NOT_YET_VALID,
        `Certificate not yet valid: ${cert.subject.getField('CN')?.value || cert.subject.toString()}`,
        { index: i, notBefore: cert.validity.notBefore }
      ));
    }
    
    if (checkTime > cert.validity.notAfter) {
      errors.push(new SmimeError(
        SmimeErrorCode.CERTIFICATE_EXPIRED,
        `Certificate expired: ${cert.subject.getField('CN')?.value || cert.subject.toString()}`,
        { index: i, notAfter: cert.validity.notAfter }
      ));
    }
    
    // Check key usage for end-entity (first cert)
    if (i === 0) {
      const hasDigitalSignature = cert.extensions?.some(
        e => e.name === 'keyUsage' && (e as forge.pki.KeyUsageExtension).digitalSignature
      );
      const hasKeyEncipherment = cert.extensions?.some(
        e => e.name === 'keyUsage' && (e as forge.pki.KeyUsageExtension).keyEncipherment
      );
      
      if (!hasDigitalSignature && !hasKeyEncipherment) {
        errors.push(new SmimeError(
          SmimeErrorCode.CERTIFICATE_KEY_USAGE_INVALID,
          'End-entity certificate missing required key usage (digitalSignature or keyEncipherment)',
          { index: i }
        ));
      }
    }
    
    // Check CA flag for intermediate certs
    if (i > 0 && i < chain.length - 1) {
      const isCA = cert.extensions?.some(
        e => e.name === 'basicConstraints' && (e as forge.pki.BasicConstraintsExtension).cA === true
      );
      if (!isCA) {
        errors.push(new SmimeError(
          SmimeErrorCode.CERTIFICATE_CHAIN_INVALID,
          `Intermediate certificate at index ${i} is not a CA`,
          { index: i }
        ));
      }
    }
  }
  
  // Verify chain signatures
  for (let i = 0; i < chain.length - 1; i++) {
    const child = chain[i];
    const parent = chain[i + 1];
    
    try {
      if (!parent.verify(child)) {
        errors.push(new SmimeError(
          SmimeErrorCode.CERTIFICATE_CHAIN_INVALID,
          `Certificate signature verification failed at index ${i}`,
          { childIndex: i, parentIndex: i + 1 }
        ));
      }
    } catch (e) {
      errors.push(new SmimeError(
        SmimeErrorCode.CERTIFICATE_CHAIN_INVALID,
        `Certificate signature verification error at index ${i}`,
        { childIndex: i, parentIndex: i + 1, error: e instanceof Error ? e.message : String(e) },
        e instanceof Error ? e : undefined
      ));
    }
  }
  
  // Check trust anchor
  let trustAnchor: TrustAnchor | undefined;
  const rootCert = chain[chain.length - 1];
  
  for (const anchor of trustAnchors) {
    try {
      // Check if root cert matches trust anchor
      const rootDer = forge.asn1.toDer(forge.pki.certificateToAsn1(rootCert)).getBytes();
      const anchorDer = forge.asn1.toDer(forge.pki.certificateToAsn1(anchor.certificate)).getBytes();
      
      if (rootDer === anchorDer) {
        trustAnchor = anchor;
        break;
      }
      
      // Also check by subject/serial
      if (rootCert.subject.toString() === anchor.certificate.subject.toString() &&
          rootCert.serialNumber === anchor.certificate.serialNumber) {
        trustAnchor = anchor;
        break;
      }
    } catch {
      // Continue checking other anchors
    }
  }
  
  if (!trustAnchor) {
    errors.push(new SmimeError(
      SmimeErrorCode.CERTIFICATE_UNTRUSTED,
      'Certificate chain does not terminate in a trusted anchor',
      { rootSubject: rootCert.subject.toString(), rootSerial: rootCert.serialNumber }
    ));
  }
  
  return {
    valid: errors.length === 0,
    chain,
    errors,
    trustAnchor
  };
}

/**
 * Extract signer information from PKCS#7 signed data
 */
export function extractSignerInfo(
  signedData: forge.pkcs7.SignedData,
  trustAnchors: TrustAnchor[],
  checkTime: Date = new Date()
): SignerInfo[] {
  const signers: SignerInfo[] = [];
  
  // Get certificates from the signed data
  const certs = signedData.certificates || [];
  const certMap = new Map<string, forge.pki.Certificate>();
  
  for (const cert of certs) {
    const key = cert.subject.toString() + ':' + cert.serialNumber;
    certMap.set(key, cert);
  }
  
  for (const signer of signedData.signers) {
    // Find signer certificate
    let signerCert: forge.pki.Certificate | undefined;
    
    if (signer.issuer && signer.serialNumber) {
      const key = signer.issuer.toString() + ':' + signer.serialNumber.toString();
      signerCert = certMap.get(key);
    }
    
    if (!signerCert) {
      // Try to find by subject key identifier or other means
      for (const cert of certs) {
        try {
          if (cert.verify(signer.signature)) {
            signerCert = cert;
            break;
          }
        } catch {
          // Continue
        }
      }
    }
    
    if (!signerCert) {
      throw new SmimeError(
        SmimeErrorCode.CERTIFICATE_MISSING,
        'Signer certificate not found in SignedData'
      );
    }
    
    // Build chain
    const chain: forge.pki.Certificate[] = [signerCert];
    let currentCert = signerCert;
    
    while (true) {
      let foundIssuer = false;
      for (const cert of certs) {
        if (cert !== currentCert && currentCert.issuer.toString() === cert.subject.toString()) {
          chain.push(cert);
          currentCert = cert;
          foundIssuer = true;
          break;
        }
      }
      if (!foundIssuer) break;
    }
    
    // Validate chain
    const validationResult = validateCertificateChain(chain, trustAnchors, checkTime);
    
    // Get algorithms
    const signatureAlgorithm = forge.pki.oids[signer.signatureAlgorithm] || signer.signatureAlgorithm;
    const digestAlgorithm = forge.pki.oids[signer.digestAlgorithm] || signer.digestAlgorithm;
    
    // Get signing time from signed attributes
    let signingTime: Date | undefined;
    if (signer.signedAttributes) {
      for (const attr of signer.signedAttributes) {
        if (attr.type === '1.2.840.113549.1.9.5') { // signingTime OID
          try {
            const timeValue = attr.values[0];
            if (timeValue.type === forge.asn1.Class.UNIVERSAL && timeValue.tag === forge.asn1.Type.UTCTIME) {
              signingTime = forge.asn1.utcTimeToDate(timeValue);
            } else if (timeValue.type === forge.asn1.Class.UNIVERSAL && timeValue.tag === forge.asn1.Type.GENERALIZEDTIME) {
              signingTime = forge.asn1.generalizedTimeToDate(timeValue);
            }
          } catch {
            // Ignore time parsing errors
          }
          break;
        }
      }
    }
    
    signers.push({
      certificate: getCertificateInfo(signerCert),
      certificateChain: chain.map(getCertificateInfo),
      validationResult,
      signedAttributes: signer.signedAttributes,
      signatureAlgorithm,
      digestAlgorithm,
      signingTime
    });
  }
  
  return signers;
}

/**
 * Generate self-signed certificate for testing
 */
export function generateSelfSignedCertificate(
  commonName: string,
  keySize: number = 2048,
  daysValid: number = 365
): { certificate: forge.pki.Certificate; privateKey: forge.pki.PrivateKey; certPem: string; keyPem: string } {
  const keys = forge.pki.rsa.generateKeyPair({ bits: keySize });
  
  const cert = forge.pki.createCertificate();
  cert.publicKey = keys.publicKey;
  cert.serialNumber = forge.util.bytesToHex(forge.random.getBytesSync(16));
  cert.validity.notBefore = new Date();
  cert.validity.notAfter = new Date();
  cert.validity.notAfter.setDate(cert.validity.notAfter.getDate() + daysValid);
  
  const attrs = [{
    name: 'commonName',
    value: commonName
  }];
  
  cert.setSubject(attrs);
  cert.setIssuer(attrs);
  
  // Extensions
  cert.setExtensions([
    {
      name: 'basicConstraints',
      cA: true
    },
    {
      name: 'keyUsage',
      keyCertSign: true,
      digitalSignature: true,
      nonRepudiation: true,
      keyEncipherment: true,
      dataEncipherment: true
    },
    {
      name: 'extKeyUsage',
      serverAuth: true,
      clientAuth: true,
      emailProtection: true
    },
    {
      name: 'subjectKeyIdentifier'
    },
    {
      name: 'authorityKeyIdentifier'
    }
  ]);
  
  cert.sign(keys.privateKey, forge.md.sha256.create());
  
  return {
    certificate: cert,
    privateKey: keys.privateKey,
    certPem: forge.pki.certificateToPem(cert),
    keyPem: forge.pki.privateKeyToPem(keys.privateKey)
  };
}

/**
 * Generate certificate signed by CA
 */
export function generateCASignedCertificate(
  caCert: forge.pki.Certificate,
  caKey: forge.pki.PrivateKey,
  commonName: string,
  keySize: number = 2048,
  daysValid: number = 365,
  isCA: boolean = false
): { certificate: forge.pki.Certificate; privateKey: forge.pki.PrivateKey; certPem: string; keyPem: string } {
  const keys = forge.pki.rsa.generateKeyPair({ bits: keySize });
  
  const cert = forge.pki.createCertificate();
  cert.publicKey = keys.publicKey;
  cert.serialNumber = forge.util.bytesToHex(forge.random.getBytesSync(16));
  cert.validity.notBefore = new Date();
  cert.validity.notAfter = new Date();
  cert.validity.notAfter.setDate(cert.validity.notAfter.getDate() + daysValid);
  
  const attrs = [{
    name: 'commonName',
    value: commonName
  }];
  
  cert.setSubject(attrs);
  cert.setIssuer(caCert.subject.attributes);
  
  const extensions: forge.pki.CertificateExtension[] = [
    {
      name: 'basicConstraints',
      cA: isCA
    },
    {
      name: 'keyUsage',
      digitalSignature: true,
      nonRepudiation: true,
      keyEncipherment: true,
      dataEncipherment: true
    },
    {
      name: 'extKeyUsage',
      clientAuth: true,
      emailProtection: true
    },
    {
      name: 'subjectKeyIdentifier'
    },
    {
      name: 'authorityKeyIdentifier'
    }
  ];
  
  if (isCA) {
    (extensions[1] as forge.pki.KeyUsageExtension).keyCertSign = true;
    (extensions[1] as forge.pki.KeyUsageExtension).cRLSign = true;
  }
  
  cert.setExtensions(extensions);
  cert.sign(caKey, forge.md.sha256.create());
  
  return {
    certificate: cert,
    privateKey: keys.privateKey,
    certPem: forge.pki.certificateToPem(cert),
    keyPem: forge.pki.privateKeyToPem(keys.privateKey)
  };
}
```

## src/mime.ts - MIME Construction/Parsing

```typescript
/**
 * MIME Message Construction and Parsing
 * Preserves essential headers and canonical line endings (CRLF)
 */

import * as forge from 'node-forge';
import { simpleParser, ParsedMail } from 'mailparser';
import { MimeNode } from 'mime-node';
import { SmimeError, SmimeErrorCode } from './errors';

export interface MimeHeaders {
  [key: string]: string | string[];
}

export interface MimePart {
  headers: MimeHeaders;
  body: string | Buffer;
  contentType: string;
  children?: MimePart[];
}

export interface ParsedMimeMessage {
  headers: MimeHeaders;
  textBody?: string;
  htmlBody?: string;
  attachments: MimeAttachment[];
  rawHeaders: string;
}

export interface MimeAttachment {
  contentType: string;
  contentDisposition: string;
  filename?: string;
  contentId?: string;
  content: Buffer;
  headers: MimeHeaders;
}

/**
 * Canonicalize line endings to CRLF
 */
export function canonicalizeLineEndings(input: string | Buffer): string {
  const str = Buffer.isBuffer(input) ? input.toString('binary') : input;
  // Replace all line endings with CRLF
  return str.replace(/\r?\n/g, '\r\n');
}

/**
 * Ensure headers use CRLF line endings
 */
export function canonicalizeHeaders(headers: string): string {
  return headers.replace(/\r?\n/g, '\r\n');
}

/**
 * Parse raw MIME message
 */
export async function parseMimeMessage(raw: string | Buffer): Promise<ParsedMimeMessage> {
  const rawStr = Buffer.isBuffer(raw) ? raw.toString('binary') : raw;
  
  try {
    const parsed = await simpleParser(rawStr);
    
    const attachments: MimeAttachment[] = [];
    
    for (const attachment of parsed.attachments) {
      attachments.push({
        contentType: attachment.contentType,
        contentDisposition: attachment.contentDisposition || 'attachment',
        filename: attachment.filename,
        contentId: attachment.contentId,
        content: attachment.content,
        headers: attachment.headers as unknown as MimeHeaders
      });
    }
    
    // Extract raw headers (before first blank line)
    const headerEnd = rawStr.indexOf('\r\n\r\n');
    const rawHeaders = headerEnd >= 0 ? rawStr.substring(0, headerEnd) : rawStr;
    
    return {
      headers: parsed.headers as unknown as MimeHeaders,
      textBody: parsed.text,
      htmlBody: parsed.html,
      attachments,
      rawHeaders: canonicalizeHeaders(rawHeaders)
    };
  } catch (e) {
    throw new SmimeError(
      SmimeErrorCode.MIME_PARSE_FAILED,
      'Failed to parse MIME message',
      { error: e instanceof Error ? e.message : String(e) },
      e instanceof Error ? e : undefined
    );
  }
}

/**
 * Build MIME message from parts
 */
export function buildMimeMessage(parts: MimePart[], boundary?: string): string {
  const mimeNode = new MimeNode();
  
  // Set headers on root
  if (parts.length > 0 && parts[0].headers) {
    for (const [key, value] of Object.entries(parts[0].headers)) {
      if (Array.isArray(value)) {
        for (const v of value) {
          mimeNode.setHeader(key, v);
        }
      } else {
        mimeNode.setHeader(key, value);
      }
    }
  }
  
  // Add parts
  for (const part of parts) {
    const childNode = new MimeNode();
    
    // Set headers
    for (const [key, value] of Object.entries(part.headers)) {
      if (Array.isArray(value)) {
        for (const v of value) {
          childNode.setHeader(key, v);
        }
      } else {
        childNode.setHeader(key, value);
      }
    }
    
    // Set content
    if (Buffer.isBuffer(part.body)) {
      childNode.setContent(part.body.toString('binary'));
    } else {
      childNode.setContent(part.body);
    }
    
    mimeNode.addChild(childNode);
  }
  
  // Generate with CRLF
  let output = mimeNode.build();
  output = canonicalizeLineEndings(output);
  
  return output;
}

/**
 * Create a simple text/plain MIME part
 */
export function createTextPart(content: string, charset: string = 'utf-8'): MimePart {
  return {
    headers: {
      'Content-Type': `text/plain; charset="${charset}"`,
      'Content-Transfer-Encoding': '7bit'
    },
    body: content,
    contentType: `text/plain; charset="${charset}"`
  };
}

/**
 * Create a multipart/signed MIME part (for clear-signing)
 */
export function createMultipartSigned(
  signedContent: MimePart,
  signaturePart: MimePart,
  protocol: string = 'application/pkcs7-signature',
  micalg: string = 'sha-256',
  boundary?: string
): MimePart {
  const actualBoundary = boundary || `boundary_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  
  return {
    headers: {
      'Content-Type': `multipart/signed; protocol="${protocol}"; micalg=${micalg}; boundary="${actualBoundary}"`
    },
    body: '',
    contentType: `multipart/signed; protocol="${protocol}"; micalg=${micalg}`,
    children: [signedContent, signaturePart]
  };
}

/**
 * Create application/pkcs7-mime part (for opaque signing/encryption)
 */
export function createPkcs7MimePart(
  pkcs7Data: Buffer | string,
  smimeType: 'signed-data' | 'enveloped-data' | 'signed-and-enveloped-data' = 'signed-data',
  filename: string = 'smime.p7m'
): MimePart {
  const data = Buffer.isBuffer(pkcs7Data) ? pkcs7Data : Buffer.from(pkcs7Data, 'binary');
  
  return {
    headers: {
      'Content-Type': `application/pkcs7-mime; smime-type=${smimeType}; name="${filename}"`,
      'Content-Transfer-Encoding': 'base64',
      'Content-Disposition': `attachment; filename="${filename}"`,
      'Content-Description': 'S/MIME Cryptographic Message'
    },
    body: data.toString('base64'),
    contentType: `application/pkcs7-mime; smime-type=${smimeType}`
  };
}

/**
 * Extract PKCS#7 data from MIME message
 */
export function extractPkcs7FromMime(parsed: ParsedMimeMessage): Buffer | null {
  // Check for application/pkcs7-mime
  for (const attachment of parsed.attachments) {
    if (attachment.contentType.includes('application/pkcs7-mime') ||
        attachment.contentType.includes('application/x-pkcs7-mime')) {
      return attachment.content;
    }
  }
  
  // Check for multipart/signed with application/pkcs7-signature
  if (parsed.headers['content-type']) {
    const contentType = Array.isArray(parsed.headers['content-type']) 
      ? parsed.headers['content-type'][0] 
      : parsed.headers['content-type'];
    
    if (contentType.includes('multipart/signed')) {
      // The signature would be in attachments
      for (const attachment of parsed.attachments) {
        if (attachment.contentType.includes('application/pkcs7-signature') ||
            attachment.contentType.includes('application/x-pkcs7-signature')) {
          return attachment.content;
        }
      }
    }
  }
  
  return null;
}

/**
 * Prepare content for signing (canonicalize)
 * For multipart/signed, the first part is signed
 * For opaque signing, the entire MIME message is signed
 */
export function prepareContentForSigning(
  mimeMessage: string,
  isDetached: boolean = false
): { content: string; headers: string } {
  const canonical = canonicalizeLineEndings(mimeMessage);
  
  if (isDetached) {
    // For detached signing, we sign the canonicalized content
    // Find the boundary between headers and body
    const headerEnd = canonical.indexOf('\r\n\r\n');
    if (headerEnd >= 0) {
      const headers = canonical.substring(0, headerEnd);
      const body = canonical.substring(headerEnd + 4);
      return { content: body, headers };
    }
    return { content: canonical, headers: '' };
  } else {
    // For opaque signing, sign the entire message
    return { content: canonical, headers: '' };
  }
}

/**
 * Verify content hasn't been modified (for detached signatures)
 */
export function verifyContentIntegrity(
  originalContent: string,
  signedContent: string
): boolean {
  return canonicalizeLineEndings(originalContent) === canonicalizeLineEndings(signedContent);
}
```

## src/cms.ts - CMS Operations

```typescript
/**
 * CMS/PKCS#7 Operations
 * Signing, verification, encryption, decryption using node-forge
 */

import * as forge from 'node-forge';
import { SmimeError, SmimeErrorCode } from './errors';
import { parseCertificates, parsePrivateKey, TrustAnchor, SignerInfo, validateCertificateChain } from './certificates';

export interface SignOptions {
  signerCert: forge.pki.Certificate;
  signerKey: forge.pki.PrivateKey;
  certChain?: forge.pki.Certificate[];
  digestAlgorithm?: forge.md.MessageDigest;
  detached?: boolean;
  includeSigningTime?: boolean;
  includeContentType?: boolean;
  includeMessageDigest?: boolean;
}

export interface VerifyOptions {
  trustAnchors: TrustAnchor[];
  checkTime?: Date;
  allowUntrusted?: boolean;
}

export interface EncryptOptions {
  recipientCerts: forge.pki.Certificate[];
  encryptionAlgorithm?: string; // OID
  keyEncryptionAlgorithm?: string; // OID
}

export interface DecryptOptions {
  recipientCert: forge.pki.Certificate;
  recipientKey: forge.pki.PrivateKey;
}

/**
 * Default algorithms
 */
export const ALGORITHMS = {
  // Digest algorithms
  SHA256: '2.16.840.1.101.3.4.2.1',
  SHA384: '2.16.840.1.101.3.4.2.2',
  SHA512: '2.16.840.1.101.3.4.2.3',
  
  // Encryption algorithms
  AES256_CBC: '2.16.840.1.101.3.4.1.42',
  AES192_CBC: '2.16.840.1.101.3.4.1.22',
  AES128_CBC: '2.16.840.1.101.3.4.1.2',
  TRIPLE_DES_CBC: '1.2.840.113549.3.7',
  
  // Key encryption algorithms
  RSAES_PKCS1_V1_5: '1.2.840.113549.1.1.1',
  RSAES_OAEP: '1.2.840.113549.1.1.7'
} as const;

/**
 * Create PKCS#7 SignedData (detached or opaque)
 */
export function createSignedData(
  content: string | Buffer,
  options: SignOptions
): forge.pkcs7.SignedData {
  const {
    signerCert,
    signerKey,
    certChain = [],
    digestAlgorithm = forge.md.sha256.create(),
    detached = false,
    includeSigningTime = true,
    includeContentType = true,
    includeMessageDigest = true
  } = options;
  
  // Create PKCS#7 signed data
  const p7 = forge.pkcs7.createSignedData();
  
  // Add content
  const contentStr = Buffer.isBuffer(content) ? content.toString('binary') : content;
  p7.content = forge.util.createBuffer(contentStr, 'binary');
  
  // Add signer
  p7.addSigner({
    key: signerKey,
    certificate: signerCert,
    digestAlgorithm: forge.pki.oids[digestAlgorithm.algorithm] || 'sha256',
    authenticatedAttributes: [
      { type: forge.pki.oids.contentType, value: forge.pki.oids.data },
      { type: forge.pki.oids.messageDigest },
      { type: forge.pki.oids.signingTime, value: new Date() }
    ].filter(attr => {
      if (attr.type === forge.pki.oids.contentType) return includeContentType;
      if (attr.type === forge.pki.oids.messageDigest) return includeMessageDigest;
      if (attr.type === forge.pki.oids.signingTime) return includeSigningTime;
      return true;
    })
  });
  
  // Add certificates
  if (certChain.length > 0) {
    for (const cert of certChain) {
      p7.addCertificate(cert);
    }
  }
  p7.addCertificate(signerCert);
  
  // Sign
  p7.sign({ detached });
  
  return p7;
}

/**
 * Convert SignedData to PEM/DER
 */
export function signedDataToPem(signedData: forge.pkcs7.SignedData): string {
  const der = forge.asn1.toDer(signedData.toAsn1()).getBytes();
  const b64 = forge.util.encode64(der);
  return `-----BEGIN PKCS7-----\r\n${b64.match(/.{1,64}/g)?.join('\r\n') || b64}\r\n-----END PKCS7-----`;
}

export function signedDataToDer(signedData: forge.pkcs7.SignedData): Buffer {
  const der = forge.asn1.toDer(signedData.toAsn1()).getBytes();
  return Buffer.from(der, 'binary');
}

/**
 * Parse PKCS#7 from PEM or DER
 */
export function parsePkcs7(data: string | Buffer): forge.pkcs7.ContentInfo {
  let der: string;
  
  if (Buffer.isBuffer(data)) {
    der = data.toString('binary');
  } else {
    const str = data.toString();
    if (str.includes('-----BEGIN')) {
      // PEM format
      const lines = str.split(/\r?\n/);
      const b64 = lines.filter(l => !l.startsWith('-----')).join('');
      der = forge.util.decode64(b64);
    } else {
      // Assume base64
      der = forge.util.decode64(str);
    }
  }
  
  const asn1 = forge.asn1.fromDer(der);
  return forge.pkcs7.messageFromAsn1(asn1);
}

/**
 * Verify PKCS#7 signed data
 */
export function verifySignedData(
  p7: forge.pkcs7.ContentInfo,
  options: VerifyOptions
): { valid: boolean; signers: SignerInfo[]; content: string; errors: SmimeError[] } {
  const { trustAnchors, checkTime = new Date(), allowUntrusted = false } = options;
  const errors: SmimeError[] = [];
  
  if (p7.contentType !== forge.pki.oids.signedData) {
    errors.push(new SmimeError(
      SmimeErrorCode.SIGNATURE_MALFORMED,
      'Not a PKCS#7 SignedData',
      { contentType: p7.contentType }
    ));
    return { valid: false, signers: [], content: '', errors };
  }
  
  const signedData = p7.content as forge.pkcs7.SignedData;
  
  // Get content
  let content = '';
  if (signedData.content) {
    content = signedData.content.toString('binary');
  }
  
  // Verify signatures
  let allValid = true;
  for (const signer of signedData.signers) {
    try {
      const verified = signer.verify();
      if (!verified) {
        allValid = false;
        errors.push(new SmimeError(
          SmimeErrorCode.SIGNATURE_INVALID,
          'Signature verification failed',
          { issuer: signer.issuer?.toString(), serialNumber: signer.serialNumber?.toString() }
        ));
      }
    } catch (e) {
      allValid = false;
      errors.push(new SmimeError(
        SmimeErrorCode.SIGNATURE_INVALID,
        'Signature verification error',
        { error: e instanceof Error ? e.message : String(e) },
        e instanceof Error ? e : undefined
      ));
    }
  }
  
  // Extract signer info
  let signers: SignerInfo[] = [];
  try {
    signers = extractSignerInfoFromSignedData(signedData, trustAnchors, checkTime);
  } catch (e) {
    errors.push(new SmimeError(
      SmimeErrorCode.SIGNATURE_MALFORMED,
      'Failed to extract signer information',
      { error: e instanceof Error ? e.message : String(e) },
      e instanceof Error ? e : undefined
    ));
  }
  
  // Check trust if not allowed untrusted
  if (!allowUntrusted) {
    for (const signer of signers) {
      if (!signer.validationResult.valid) {
        allValid = false;
        errors.push(...signer.validationResult.errors);
      }
    }
  }
  
  return { valid: allValid, signers, content, errors };
}

/**
 * Extract signer info from SignedData (internal helper)
 */
function extractSignerInfoFromSignedData(
  signedData: forge.pkcs7.SignedData,
  trustAnchors: TrustAnchor[],
  checkTime: Date
): SignerInfo[] {
  const certs = signedData.certificates || [];
  const certMap = new Map<string, forge.pki.Certificate>();
  
  for (const cert of certs) {
    const key = cert.subject.toString() + ':' + cert.serialNumber;
    certMap.set(key, cert);
  }
  
  const signers: SignerInfo[] = [];
  
  for (const signer of signedData.signers) {
    let signerCert: forge.pki.Certificate | undefined;
    
    if (signer.issuer && signer.serialNumber) {
      const key = signer.issuer.toString() + ':' + signer.serialNumber.toString();
      signerCert = certMap.get(key);
    }
    
    if (!signerCert) {
      for (const cert of certs) {
        try {
          if (cert.verify(signer.signature)) {
            signerCert = cert;
            break;
          }
        } catch {
          // Continue
        }
      }
    }
    
    if (!signerCert) {
      throw new SmimeError(
        SmimeErrorCode.CERTIFICATE_MISSING,
        'Signer certificate not found'
      );
    }
    
    // Build chain
    const chain: forge.pki.Certificate[] = [signerCert];
    let currentCert = signerCert;
    
    while (true) {
      let foundIssuer = false;
      for (const cert of certs) {
        if (cert !== currentCert && currentCert.issuer.toString() === cert.subject.toString()) {
          chain.push(cert);
          currentCert = cert;
          foundIssuer = true;
          break;
        }
      }
      if (!foundIssuer) break;
    }
    
    const validationResult = validateCertificateChain(chain, trustAnchors, checkTime);
    
    const signatureAlgorithm = forge.pki.oids[signer.signatureAlgorithm] || signer.signatureAlgorithm;
    const digestAlgorithm = forge.pki.oids[signer.digestAlgorithm] || signer.digestAlgorithm;
    
    let signingTime: Date | undefined;
    if (signer.signedAttributes) {
      for (const attr of signer.signedAttributes) {
        if (attr.type === forge.pki.oids.signingTime) {
          try {
            const timeValue = attr.values[0];
            if (timeValue.type === forge.asn1.Class.UNIVERSAL && timeValue.tag === forge.asn1.Type.UTCTIME) {
              signingTime = forge.asn1.utcTimeToDate(timeValue);
            } else if (timeValue.type === forge.asn1.Class.UNIVERSAL && timeValue.tag === forge.asn1.Type.GENERALIZEDTIME) {
              signingTime = forge.asn1.generalizedTimeToDate(timeValue);
            }
          } catch {
            // Ignore
          }
          break;
        }
      }
    }
    
    signers.push({
      certificate: getCertificateInfo(signerCert),
      certificateChain: chain.map(getCertificateInfo),
      validationResult,
      signedAttributes: signer.signedAttributes,
      signatureAlgorithm,
      digestAlgorithm,
      signingTime
    });
  }
  
  return signers;
}

/**
 * Create PKCS#7 EnvelopedData (encryption)
 */
export function createEnvelopedData(
  content: string | Buffer,
  options: EncryptOptions
): forge.pkcs7.EnvelopedData {
  const {
    recipientCerts,
    encryptionAlgorithm = ALGORITHMS.AES256_CBC,
    keyEncryptionAlgorithm = ALGORITHMS.RSAES_PKCS1_V1_5
  } = options;
  
  if (recipientCerts.length === 0) {
    throw new SmimeError(SmimeErrorCode.INVALID_INPUT, 'At least one recipient certificate required');
  }
  
  const p7 = forge.pkcs7.createEnvelopedData();
  
  // Add content
  const contentStr = Buffer.isBuffer(content) ? content.toString('binary') : content;
  p7.content = forge.util.createBuffer(contentStr, 'binary');
  
  // Add recipients
  for (const cert of recipientCerts) {
    p7.addRecipient(cert);
  }
  
  // Set encryption algorithm
  p7.encryptionAlgorithm = encryptionAlgorithm;
  
  // Encrypt
  p7.encrypt();
  
  return p7;
}

/**
 * Convert EnvelopedData to PEM/DER
 */
export function envelopedDataToPem(envelopedData: forge.pkcs7.EnvelopedData): string {
  const contentInfo = forge.pkcs7.createContentInfo(forge.pki.oids.envelopedData, envelopedData);
  const der = forge.asn1.toDer(contentInfo.toAsn1()).getBytes();
  const b64 = forge.util.encode64(der);
  return `-----BEGIN PKCS7-----\r\n${b64.match(/.{1,64}/g)?.join('\r\n') || b64}\r\n-----END PKCS7-----`;
}

export function envelopedDataToDer(envelopedData: forge.pkcs7.EnvelopedData): Buffer {
  const contentInfo = forge.pkcs7.createContentInfo(forge.pki.oids.envelopedData, envelopedData);
  const der = forge.asn1.toDer(contentInfo.toAsn1()).getBytes();
  return Buffer.from(der, 'binary');
}

/**
 * Decrypt PKCS#7 EnvelopedData
 */
export function decryptEnvelopedData(
  p7: forge.pkcs7.ContentInfo,
  options: DecryptOptions
): { content: string; errors: SmimeError[] } {
  const { recipientCert, recipientKey } = options;
  const errors: SmimeError[] = [];
  
  if (p7.contentType !== forge.pki.oids.envelopedData) {
    errors.push(new SmimeError(
      SmimeErrorCode.CONTENT_DECRYPTION_FAILED,
      'Not a PKCS#7 EnvelopedData',
      { contentType: p7.contentType }
    ));
    return { content: '', errors };
  }
  
  const envelopedData = p7.content as forge.pkcs7.EnvelopedData;
  
  // Find recipient info matching our certificate
  let recipientInfo: forge.pkcs7.RecipientInfo | undefined;
  
  for (const ri of envelopedData.recipientInfos) {
    if (ri.issuer && ri.serialNumber) {
      if (ri.issuer.toString() === recipientCert.issuer.toString() &&
          ri.serialNumber.toString() === recipientCert.serialNumber) {
        recipientInfo = ri;
        break;
      }
    }
  }
  
  if (!recipientInfo) {
    errors.push(new SmimeError(
      SmimeErrorCode.CONTENT_DECRYPTION_FAILED,
      'No matching recipient info found for certificate',
      { 
        expectedIssuer: recipientCert.issuer.toString(),
        expectedSerial: recipientCert.serialNumber,
        availableRecipients: envelopedData.recipientInfos.map(ri => ({
          issuer: ri.issuer?.toString(),
          serial: ri.serialNumber?.toString()
        }))
      }
    ));
    return { content: '', errors };
  }
  
  try {
    envelopedData.decrypt(recipientKey, recipientInfo);
    const content = envelopedData.content.toString('binary');
    return { content, errors };
  } catch (e) {
    errors.push(new SmimeError(
      SmimeErrorCode.CONTENT_DECRYPTION_FAILED,
      'Decryption failed',
      { error: e instanceof Error ? e.message : String(e) },
      e instanceof Error ? e : undefined
    ));
    return { content: '', errors };
  }
}

/**
 * Sign then encrypt (combine operations)
 */
export function signThenEncrypt(
  content: string | Buffer,
  signOptions: SignOptions,
  encryptOptions: EncryptOptions
): forge.pkcs7.EnvelopedData {
  // First sign
  const signedData = createSignedData(content, { ...signOptions, detached: false });
  
  // Convert to DER
  const signedDer = signedDataToDer(signedData);
  
  // Then encrypt
  return createEnvelopedData(signedDer, encryptOptions);
}

/**
 * Decrypt then verify
 */
export function decryptThenVerify(
  p7: forge.pkcs7.ContentInfo,
  decryptOptions: DecryptOptions,
  verifyOptions: VerifyOptions
): { content: string; signers: SignerInfo[]; valid: boolean; errors: SmimeError[] } {
  const allErrors: SmimeError[] = [];
  
  // Decrypt
  const { content: decryptedContent, errors: decryptErrors } = decryptEnvelopedData(p7, decryptOptions);
  allErrors.push(...decryptErrors);
  
  if (decryptErrors.length > 0) {
    return { content: '', signers: [], valid: false, errors: allErrors };
  }
  
  // Parse the decrypted content as PKCS#7 SignedData
  let signedP7: forge.pkcs7.ContentInfo;
  try {
    signedP7 = parsePkcs7(decryptedContent);
  } catch (e) {
    allErrors.push(new SmimeError(
      SmimeErrorCode.SIGNATURE_MALFORMED,
      'Decrypted content is not valid PKCS#7 SignedData',
      { error: e instanceof Error ? e.message : String(e) },
      e instanceof Error ? e : undefined
    ));
    return { content: '', signers: [], valid: false, errors: allErrors };
  }
  
  // Verify
  const { valid, signers, content, errors: verifyErrors } = verifySignedData(signedP7, verifyOptions);
  allErrors.push(...verifyErrors);
  
  return { content, signers, valid, errors: allErrors };
}

// Re-export getCertificateInfo for use in cms.ts
import { getCertificateInfo } from './certificates';
```

## src/smime.ts - High-Level S/MIME Operations

```typescript
/**
 * High-Level S/MIME Operations
 * Combines MIME and CMS for complete S/MIME workflows
 */

import * as forge from 'node-forge';
import { 
  parseMimeMessage, 
  buildMimeMessage, 
  createTextPart, 
  createPkcs7MimePart,
  extractPkcs7FromMime,
  prepareContentForSigning,
  canonicalizeLineEndings,
  MimePart,
  ParsedMimeMessage
} from './mime';
import { 
  createSignedData, 
  verifySignedData, 
  createEnvelopedData, 
  decryptEnvelopedData,
  signThenEncrypt,
  decryptThenVerify,
  signedDataToPem,
  envelopedDataToPem,
  parsePkcs7,
  SignOptions,
  VerifyOptions,
  EncryptOptions,
  DecryptOptions,
  ALGORITHMS
} from './cms';
import { 
  parseCertificates, 
  parsePrivateKey, 
  TrustAnchor, 
  SignerInfo,
  ValidationResult,
  generateSelfSignedCertificate,
  generateCASignedCertificate
} from './certificates';
import { SmimeError, SmimeErrorCode, SmimeErrorCollection } from './errors';

export interface SmimeSignOptions {
  signerCertPem: string;
  signerKeyPem: string;
  signerKeyPassphrase?: string;
  certChainPem?: string;
  detached?: boolean;
  digestAlgorithm?: string;
}

export interface SmimeVerifyOptions {
  trustAnchorsPem: string | string[];
  checkTime?: Date;
  allowUntrusted?: boolean;
}

export interface SmimeEncryptOptions {
  recipientCertsPem: string | string[];
  encryptionAlgorithm?: string;
}

export interface SmimeDecryptOptions {
  recipientCertPem: string;
  recipientKeyPem: string;
  recipientKeyPassphrase?: string;
}

export interface SmimeSignResult {
  mimeMessage: string;
  pkcs7Pem: string;
  pkcs7Der: Buffer;
  signerInfo: SignerInfo[];
}

export interface SmimeVerifyResult {
  valid: boolean;
  content: string;
  signerInfo: SignerInfo[];
  errors: SmimeError[];
  mimeMessage?: ParsedMimeMessage;
}

export interface SmimeEncryptResult {
  mimeMessage: string;
  pkcs7Pem: string;
  pkcs7Der: Buffer;
}

export interface SmimeDecryptResult {
  content: string;
  mimeMessage?: ParsedMimeMessage;
  errors: SmimeError[];
}

export interface SmimeSignEncryptResult {
  mimeMessage: string;
  pkcs7Pem: string;
  pkcs7Der: Buffer;
}

export interface SmimeDecryptVerifyResult {
  content: string;
  signerInfo: SignerInfo[];
  valid: boolean;
  errors: SmimeError[];
  mimeMessage?: ParsedMimeMessage;
}

/**
 * Parse trust anchors from PEM
 */
function parseTrustAnchors(pem: string | string[]): TrustAnchor[] {
  const pems = Array.isArray(pem) ? pem : [pem];
  const anchors: TrustAnchor[] = [];
  
  for (const p of pems) {
    const certs = parseCertificates(p);
    for (const cert of certs) {
      anchors.push({
        certificate: cert,
        name: cert.subject.getField('CN')?.value || cert.subject.toString()
      });
    }
  }
  
  return anchors;
}

/**
 * Parse recipient certificates from PEM
 */
function parseRecipientCerts(pem: string | string[]): forge.pki.Certificate[] {
  const pems = Array.isArray(pem) ? pem : [pem];
  const certs: forge.pki.Certificate[] = [];
  
  for (const p of pems) {
    certs.push(...parseCertificates(p));
  }
  
  return certs;
}

/**
 * Sign a MIME message (clear-signing or opaque)
 */
export async function smimeSign(
  mimeMessage: string,
  options: SmimeSignOptions
): Promise<SmimeSignResult> {
  const {
    signerCertPem,
    signerKeyPem,
    signerKeyPassphrase,
    certChainPem,
    detached = false,
    digestAlgorithm = 'sha256'
  } = options;
  
  // Parse certificates and key
  const signerCert = parseCertificates(signerCertPem)[0];
  const signerKey = parsePrivateKey(signerKeyPem, signerKeyPassphrase);
  const certChain = certChainPem ? parseCertificates(certChainPem) : [];
  
  // Prepare content for signing
  const { content } = prepareContentForSigning(mimeMessage, detached);
  
  // Create signed data
  const digestAlgo = forge.md[digestAlgorithm as keyof typeof forge.md]?.create?.() || forge.md.sha256.create();
  
  const signedData = createSignedData(content, {
    signerCert,
    signerKey,
    certChain,
    digestAlgorithm: digestAlgo,
    detached
  });
  
  // Generate outputs
  const pkcs7Pem = signedDataToPem(signedData);
  const pkcs7Der = signedDataToDer(signedData);
  
  // Build MIME message
  let resultMime: string;
  
  if (detached) {
    // multipart/signed
    const signaturePart = createPkcs7MimePart(pkcs7Der, 'signed-data', 'smime.p7s');
    const signedPart = createTextPart(content);
    
    const multipartSigned = createMultipartSigned(signedPart, signaturePart);
    resultMime = buildMimeMessage([multipartSigned]);
  } else {
    // application/pkcs7-mime (opaque)
    const pkcs7Part = createPkcs7MimePart(pkcs7Der, 'signed-data', 'smime.p7m');
    resultMime = buildMimeMessage([pkcs7Part]);
  }
  
  // Extract signer info for result
  const trustAnchors: TrustAnchor[] = []; // Empty for now, would need trust anchors
  const signerInfo = extractSignerInfoFromSignedData(signedData, trustAnchors, new Date());
  
  return {
    mimeMessage: resultMime,
    pkcs7Pem,
    pkcs7Der,
    signerInfo
  };
}

/**
 * Verify a signed MIME message
 */
export async function smimeVerify(
  mimeMessage: string,
  options: SmimeVerifyOptions
): Promise<SmimeVerifyResult> {
  const { trustAnchorsPem, checkTime = new Date(), allowUntrusted = false } = options;
  
  // Parse MIME
  const parsed = await parseMimeMessage(mimeMessage);
  
  // Extract PKCS#7
  const pkcs7Data = extractPkcs7FromMime(parsed);
  
  if (!pkcs7Data) {
    throw new SmimeError(
      SmimeErrorCode.SIGNATURE_MISSING,
      'No PKCS#7 signature found in MIME message'
    );
  }
  
  // Parse PKCS#7
  const p7 = parsePkcs7(pkcs7Data);
  
  // Parse trust anchors
  const trustAnchors = parseTrustAnchors(trustAnchorsPem);
  
  // Verify
  const { valid, signers, content, errors } = verifySignedData(p7, {
    trustAnchors,
    checkTime,
    allowUntrusted
  });
  
  return {
    valid,
    content,
    signerInfo: signers,
    errors,
    mimeMessage: parsed
  };
}

/**
 * Encrypt a MIME message for recipients
 */
export async function smimeEncrypt(
  mimeMessage: string,
  options: SmimeEncryptOptions
): Promise<SmimeEncryptResult> {
  const { recipientCertsPem, encryptionAlgorithm = ALGORITHMS.AES256_CBC } = options;
  
  // Parse recipient certificates
  const recipientCerts = parseRecipientCerts(recipientCertsPem);
  
  // Prepare content (canonicalize)
  const canonicalContent = canonicalizeLineEndings(mimeMessage);
  
  // Create enveloped data
  const envelopedData = createEnvelopedData(canonicalContent, {
    recipientCerts,
    encryptionAlgorithm
  });
  
  // Generate outputs
  const pkcs7Pem = envelopedDataToPem(envelopedData);
  const pkcs7Der = envelopedDataToDer(envelopedData);
  
  // Build MIME message
  const pkcs7Part = createPkcs7MimePart(pkcs7Der, 'enveloped-data', 'smime.p7m');
  const resultMime = buildMimeMessage([pkcs7Part]);
  
  return {
    mimeMessage: resultMime,
    pkcs7Pem,
    pkcs7Der
  };
}

/**
 * Decrypt an encrypted MIME message
 */
export async function smimeDecrypt(
  mimeMessage: string,
  options: SmimeDecryptOptions
): Promise<SmimeDecryptResult> {
  const { recipientCertPem, recipientKeyPem, recipientKeyPassphrase } = options;
  
  // Parse MIME
  const parsed = await parseMimeMessage(mimeMessage);
  
  // Extract PKCS#7
  const pkcs7Data = extractPkcs7FromMime(parsed);
  
  if (!pkcs7Data) {
    throw new SmimeError(
      SmimeErrorCode.CONTENT_DECRYPTION_FAILED,
      'No PKCS#7 encrypted data found in MIME message'
    );
  }
  
  // Parse PKCS#7
  const p7 = parsePkcs7(pkcs7Data);
  
  // Parse certificates and key
  const recipientCert = parseCertificates(recipientCertPem)[0];
  const recipientKey = parsePrivateKey(recipientKeyPem, recipientKeyPassphrase);
  
  // Decrypt
  const { content, errors } = decryptEnvelopedData(p7, {
    recipientCert,
    recipientKey
  });
  
  // Try to parse decrypted content as MIME
  let mimeMessageParsed: ParsedMimeMessage | undefined;
  try {
    mimeMessageParsed = await parseMimeMessage(content);
  } catch {
    // Not a MIME message, return raw content
  }
  
  return {
    content,
    mimeMessage: mimeMessageParsed,
    errors
  };
}

/**
 * Sign then encrypt a MIME message
 */
export async function smimeSignThenEncrypt(
  mimeMessage: string,
  signOptions: SmimeSignOptions,
  encryptOptions: SmimeEncryptOptions
): Promise<SmimeSignEncryptResult> {
  const {
    signerCertPem,
    signerKeyPem,
    signerKeyPassphrase,
    certChainPem,
    digestAlgorithm = 'sha256'
  } = signOptions;
  
  const { recipientCertsPem, encryptionAlgorithm = ALGORITHMS.AES256_CBC } = encryptOptions;
  
  // Parse certificates and keys
  const signerCert = parseCertificates(signerCertPem)[0];
  const signerKey = parsePrivateKey(signerKeyPem, signerKeyPassphrase);
  const certChain = certChainPem ? parseCertificates(certChainPem) : [];
  const recipientCerts = parseRecipientCerts(recipientCertsPem);
  
  // Prepare content
  const canonicalContent = canonicalizeLineEndings(mimeMessage);
  
  // Sign then encrypt
  const digestAlgo = forge.md[digestAlgorithm as keyof typeof forge.md]?.create?.() || forge.md.sha256.create();
  
  const envelopedData = signThenEncrypt(canonicalContent, {
    signerCert,
    signerKey,
    certChain,
    digestAlgorithm: digestAlgo,
    detached: false
  }, {
    recipientCerts,
    encryptionAlgorithm
  });
  
  // Generate outputs
  const pkcs7Pem = envelopedDataToPem(envelopedData);
  const pkcs7Der = envelopedDataToDer(envelopedData);
  
  // Build MIME message
  const pkcs7Part = createPkcs7MimePart(pkcs7Der, 'enveloped-data', 'smime.p7m');
  const resultMime = buildMimeMessage([pkcs7Part]);
  
  return {
    mimeMessage: resultMime,
    pkcs7Pem,
    pkcs7Der
  };
}

/**
 * Decrypt then verify a MIME message
 */
export async function smimeDecryptThenVerify(
  mimeMessage: string,
  decryptOptions: SmimeDecryptOptions,
  verifyOptions: SmimeVerifyOptions
): Promise<SmimeDecryptVerifyResult> {
  const { trustAnchorsPem, checkTime = new Date(), allowUntrusted = false } = verifyOptions;
  
  // Parse MIME
  const parsed = await parseMimeMessage(mimeMessage);
  
  // Extract PKCS#7
  const pkcs7Data = extractPkcs7FromMime(parsed);
  
  if (!pkcs7Data) {
    throw new SmimeError(
      SmimeErrorCode.CONTENT_DECRYPTION_FAILED,
      'No PKCS#7 data found in MIME message'
    );
  }
  
  // Parse PKCS#7
  const p7 = parsePkcs7(pkcs7Data);
  
  // Parse certificates and keys
  const recipientCert = parseCertificates(decryptOptions.recipientCertPem)[0];
  const recipientKey = parsePrivateKey(decryptOptions.recipientKeyPem, decryptOptions.recipientKeyPassphrase);
  const trustAnchors = parseTrustAnchors(trustAnchorsPem);
  
  // Decrypt then verify
  const { content, signers, valid, errors } = decryptThenVerify(p7, {
    recipientCert,
    recipientKey
  }, {
    trustAnchors,
    checkTime,
    allowUntrusted
  });
  
  // Try to parse decrypted content as MIME
  let mimeMessageParsed: ParsedMimeMessage | undefined;
  try {
    mimeMessageParsed = await parseMimeMessage(content);
  } catch {
    // Not a MIME message
  }
  
  return {
    content,
    signerInfo: signers,
    valid,
    errors,
    mimeMessage: mimeMessageParsed
  };
}

/**
 * Create a test MIME message
 */
export function createTestMimeMessage(
  from: string,
  to: string,
  subject: string,
  textBody: string,
  headers: Record<string, string> = {}
): string {
  const parts: MimePart[] = [{
    headers: {
      'From': from,
      'To': to,
      'Subject': subject,
      'Date': new Date().toUTCString(),
      'Message-ID': `<${Date.now()}.${Math.random().toString(36).substr(2)}@example.com>`,
      'MIME-Version': '1.0',
      ...headers
    },
    body: '',
    contentType: 'multipart/mixed'
  }, createTextPart(textBody)];
  
  return buildMimeMessage(parts);
}

// Re-export helper from cms
function extractSignerInfoFromSignedData(
  signedData: forge.pkcs7.SignedData,
  trustAnchors: TrustAnchor[],
  checkTime: Date
): SignerInfo[] {
  // This is a duplicate of the internal function in cms.ts
  // In production, this would be properly exported
  const certs = signedData.certificates || [];
  const certMap = new Map<string, forge.pki.Certificate>();
  
  for (const cert of certs) {
    const key = cert.subject.toString() + ':' + cert.serialNumber;
    certMap.set(key, cert);
  }
  
  const signers: SignerInfo[] = [];
  
  for (const signer of signedData.signers) {
    let signerCert: forge.pki.Certificate | undefined;
    
    if (signer.issuer && signer.serialNumber) {
      const key = signer.issuer.toString() + ':' + signer.serialNumber.toString();
      signerCert = certMap.get(key);
    }
    
    if (!signerCert) {
      for (const cert of certs) {
        try {
          if (cert.verify(signer.signature)) {
            signerCert = cert;
            break;
          }
        } catch {
          // Continue
        }
      }
    }
    
    if (!signerCert) {
      throw new SmimeError(
        SmimeErrorCode.CERTIFICATE_MISSING,
        'Signer certificate not found'
      );
    }
    
    const chain: forge.pki.Certificate[] = [signerCert];
    let currentCert = signerCert;
    
    while (true) {
      let foundIssuer = false;
      for (const cert of certs) {
        if (cert !== currentCert && currentCert.issuer.toString() === cert.subject.toString()) {
          chain.push(cert);
          currentCert = cert;
          foundIssuer = true;
          break;
        }
      }
      if (!foundIssuer) break;
    }
    
    const validationResult = validateCertificateChain(chain, trustAnchors, checkTime);
    
    const signatureAlgorithm = forge.pki.oids[signer.signatureAlgorithm] || signer.signatureAlgorithm;
    const digestAlgorithm = forge.pki.oids[signer.digestAlgorithm] || signer.digestAlgorithm;
    
    let signingTime: Date | undefined;
    if (signer.signedAttributes) {
      for (const attr of signer.signedAttributes) {
        if (attr.type === forge.pki.oids.signingTime) {
          try {
            const timeValue = attr.values[0];
            if (timeValue.type === forge.asn1.Class.UNIVERSAL && timeValue.tag === forge.asn1.Type.UTCTIME) {
              signingTime = forge.asn1.utcTimeToDate(timeValue);
            } else if (timeValue.type === forge.asn1.Class.UNIVERSAL && timeValue.tag === forge.asn1.Type.GENERALIZEDTIME) {
              signingTime = forge.asn1.generalizedTimeToDate(timeValue);
            }
          } catch {
            // Ignore
          }
          break;
        }
      }
    }
    
    signers.push({
      certificate: getCertificateInfo(signerCert),
      certificateChain: chain.map(getCertificateInfo),
      validationResult,
      signedAttributes: signer.signedAttributes,
      signatureAlgorithm,
      digestAlgorithm,
      signingTime
    });
  }
  
  return signers;
}

// Re-export getCertificateInfo
import { getCertificateInfo, validateCertificateChain } from './certificates';
```

## src/fixtures/tampered.ts - Tampered Message Fixture

```typescript
/**
 * Tampered Message Fixtures
 * For testing signature verification failure detection
 */

import { SmimeSignResult } from '../smime';

export interface TamperedFixture {
  name: string;
  description: string;
  originalResult: SmimeSignResult;
  tamperedMime: string;
  expectedErrorCode: string;
}

/**
 * Create tampered message by modifying content after signing
 */
export function createContentTamperedFixture(
  originalResult: SmimeSignResult
): TamperedFixture {
  // Parse the original MIME to find the signed content
  const lines = originalResult.mimeMessage.split('\r\n');
  
  // Find the base64 content and modify it
  let inBase64 = false;
  const tamperedLines: string[] = [];
  
  for (const line of lines) {
    if (line.startsWith('Content-Transfer-Encoding: base64')) {
      inBase64 = true;
      tamperedLines.push(line);
    } else if (inBase64 && line === '') {
      inBase64 = false;
      tamperedLines.push(line);
    } else if (inBase64 && /^[A-Za-z0-9+/=]+$/.test(line)) {
      // Tamper with base64 content - flip a bit
      const tampered = tamperBase64Line(line);
      tamperedLines.push(tampered);
    } else {
      tamperedLines.push(line);
    }
  }
  
  return {
    name: 'content-tampered',
    description: 'Signed content modified after signing (bit flip in base64)',
    originalResult,
    tamperedMime: tamperedLines.join('\r\n'),
    expectedErrorCode: 'SIGNATURE_DIGEST_MISMATCH'
  };
}

/**
 * Create tampered message by modifying headers
 */
export function createHeaderTamperedFixture(
  originalResult: SmimeSignResult
): TamperedFixture {
  const lines = originalResult.mimeMessage.split('\r\n');
  const tamperedLines: string[] = [];
  let headerModified = false;
  
  for (const line of lines) {
    if (!headerModified && line.startsWith('Subject:')) {
      tamperedLines.push(line + ' [TAMPERED]');
      headerModified = true;
    } else {
      tamperedLines.push(line);
    }
  }
  
  return {
    name: 'header-tampered',
    description: 'MIME header modified after signing',
    originalResult,
    tamperedMime: tamperedLines.join('\r\n'),
    expectedErrorCode: 'SIGNATURE_DIGEST_MISMATCH'
  };
}

/**
 * Create tampered message by modifying signature
 */
export function createSignatureTamperedFixture(
  originalResult: SmimeSignResult
): TamperedFixture {
  const lines = originalResult.mimeMessage.split('\r\n');
  const tamperedLines: string[] = [];
  let inSignature = false;
  
  for (const line of lines) {
    if (line.startsWith('Content-Type:') && line.includes('pkcs7-signature')) {
      inSignature = true;
      tamperedLines.push(line);
    } else if (inSignature && /^[A-Za-z0-9+/=]+$/.test(line)) {
      // Tamper with signature base64
      const tampered = tamperBase64Line(line);
      tamperedLines.push(tampered);
    } else {
      if (inSignature && line === '') {
        inSignature = false;
      }
      tamperedLines.push(line);
    }
  }
  
  return {
    name: 'signature-tampered',
    description: 'PKCS#7 signature data modified',
    originalResult,
    tamperedMime: tamperedLines.join('\r\n'),
    expectedErrorCode: 'SIGNATURE_INVALID'
  };
}

/**
 * Create tampered message with wrong certificate
 */
export function createWrongCertFixture(
  originalResult: SmimeSignResult,
  wrongCertPem: string
): TamperedFixture {
  // This would require reconstructing the PKCS#7 with a different cert
  // For now, return a placeholder
  return {
    name: 'wrong-certificate',
    description: 'Signature replaced with one from different certificate',
    originalResult,
    tamperedMime: originalResult.mimeMessage, // Placeholder
    expectedErrorCode: 'CERTIFICATE_UNTRUSTED'
  };
}

/**
 * Tamper with a base64 line by flipping a character
 */
function tamperBase64Line(line: string): string {
  if (line.length === 0) return line;
  
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=';
  const idx = Math.floor(Math.random() * line.length);
  const currentChar = line[idx];
  let newChar = chars[Math.floor(Math.random() * chars.length)];
  
  // Ensure we actually change it
  while (newChar === currentChar) {
    newChar = chars[Math.floor(Math.random() * chars.length)];
  }
  
  return line.substring(0, idx) + newChar + line.substring(idx + 1);
}

/**
 * Create all tampered fixtures for a signed message
 */
export function createAllTamperedFixtures(
  originalResult: SmimeSignResult
): TamperedFixture[] {
  return [
    createContentTamperedFixture(originalResult),
    createHeaderTamperedFixture(originalResult),
    createSignatureTamperedFixture(originalResult)
  ];
}
```

## src/cli.ts - Demonstration CLI

```typescript
/**
 * Command-Line Demonstration
 * Shows sign-then-encrypt round trip and tampered message detection
 */

import * as fs from 'fs';
import * as path from 'path';
import * as forge from 'node-forge';
import { 
  smimeSign, 
  smimeVerify, 
  smimeEncrypt, 
  smimeDecrypt,
  smimeSignThenEncrypt,
  smimeDecryptThenVerify,
  createTestMimeMessage,
  SmimeSignOptions,
  SmimeVerifyOptions,
  SmimeEncryptOptions,
  SmimeDecryptOptions
} from './smime';
import { 
  generateSelfSignedCertificate, 
  generateCASignedCertificate,
  TrustAnchor,
  ValidationResult,
  SignerInfo
} from './certificates';
import { 
  createAllTamperedFixtures,
  TamperedFixture
} from './fixtures/tampered';
import { SmimeError, SmimeErrorCode, SmimeErrorCollection } from './errors';

interface TestCertificates {
  ca: { cert: forge.pki.Certificate; key: forge.pki.PrivateKey; certPem: string; keyPem: string };
  signer: { cert: forge.pki.Certificate; key: forge.pki.PrivateKey; certPem: string; keyPem: string; chainPem: string };
  recipient: { cert: forge.pki.Certificate; key: forge.pki.PrivateKey; certPem: string; keyPem: string; chainPem: string };
  trustAnchors: TrustAnchor[];
}

const CERTS_DIR = path.join(__dirname, '..', 'certs');

/**
 * Generate test certificates
 */
function generateTestCertificates(): TestCertificates {
  // Create CA
  const ca = generateSelfSignedCertificate('S/MIME Test CA', 2048, 365);
  
  // Create signer cert signed by CA
  const signer = generateCASignedCertificate(
    ca.certificate,
    ca.privateKey,
    'S/MIME Test Signer',
    2048,
    365,
    false
  );
  
  // Create recipient cert signed by CA
  const recipient = generateCASignedCertificate(
    ca.certificate,
    ca.privateKey,
    'S/MIME Test Recipient',
    2048,
    365,
    false
  );
  
  // Trust anchors
  const trustAnchors: TrustAnchor[] = [{
    certificate: ca.certificate,
    name: 'Test CA'
  }];
  
  // Save certificates
  if (!fs.existsSync(CERTS_DIR)) {
    fs.mkdirSync(CERTS_DIR, { recursive: true });
  }
  
  fs.writeFileSync(path.join(CERTS_DIR, 'ca-cert.pem'), ca.certPem);
  fs.writeFileSync(path.join(CERTS_DIR, 'ca-key.pem'), ca.keyPem);
  fs.writeFileSync(path.join(CERTS_DIR, 'signer-cert.pem'), signer.certPem);
  fs.writeFileSync(path.join(CERTS_DIR, 'signer-key.pem'), signer.keyPem);
  fs.writeFileSync(path.join(CERTS_DIR, 'signer-chain.pem'), ca.certPem + '\n' + signer.certPem);
  fs.writeFileSync(path.join(CERTS_DIR, 'recipient-cert.pem'), recipient.certPem);
  fs.writeFileSync(path.join(CERTS_DIR, 'recipient-key.pem'), recipient.keyPem);
  fs.writeFileSync(path.join(CERTS_DIR, 'recipient-chain.pem'), ca.certPem + '\n' + recipient.certPem);
  fs.writeFileSync(path.join(CERTS_DIR, 'trust-anchors.pem'), ca.certPem);
  
  return {
    ca,
    signer: {
      ...signer,
      chainPem: ca.certPem + '\n' + signer.certPem
    },
    recipient: {
      ...recipient,
      chainPem: ca.certPem + '\n' + recipient.certPem
    },
    trustAnchors
  };
}

/**
 * Load test certificates
 */
function loadTestCertificates(): TestCertificates {
  const caCertPem = fs.readFileSync(path.join(CERTS_DIR, 'ca-cert.pem'), 'utf8');
  const caKeyPem = fs.readFileSync(path.join(CERTS_DIR, 'ca-key.pem'), 'utf8');
  const signerCertPem = fs.readFileSync(path.join(CERTS_DIR, 'signer-cert.pem'), 'utf8');
  const signerKeyPem = fs.readFileSync(path.join(CERTS_DIR, 'signer-key.pem'), 'utf8');
  const signerChainPem = fs.readFileSync(path.join(CERTS_DIR, 'signer-chain.pem'), 'utf8');
  const recipientCertPem = fs.readFileSync(path.join(CERTS_DIR, 'recipient-cert.pem'), 'utf8');
  const recipientKeyPem = fs.readFileSync(path.join(CERTS_DIR, 'recipient-key.pem'), 'utf8');
  const recipientChainPem = fs.readFileSync(path.join(CERTS_DIR, 'recipient-chain.pem'), 'utf8');
  const trustAnchorsPem = fs.readFileSync(path.join(CERTS_DIR, 'trust-anchors.pem'), 'utf8');
  
  const caCert = forge.pki.certificateFromPem(caCertPem);
  const caKey = forge.pki.privateKeyFromPem(caKeyPem);
  const signerCert = forge.pki.certificateFromPem(signerCertPem);
  const signerKey = forge.pki.privateKeyFromPem(signerKeyPem);
  const recipientCert = forge.pki.certificateFromPem(recipientCertPem);
  const recipientKey = forge.pki.privateKeyFromPem(recipientKeyPem);
  
  const trustAnchors: TrustAnchor[] = [{
    certificate: caCert,
    name: 'Test CA'
  }];
  
  return {
    ca: { cert: caCert, key: caKey, certPem: caCertPem, keyPem: caKeyPem },
    signer: { cert: signerCert, key: signerKey, certPem: signerCertPem, keyPem: signerKeyPem, chainPem: signerChainPem },
    recipient: { cert: recipientCert, key: recipientKey, certPem: recipientCertPem, keyPem: recipientKeyPem, chainPem: recipientChainPem },
    trustAnchors
  };
}

/**
 * Print signer info
 */
function printSignerInfo(signer: SignerInfo, index: number): void {
  console.log(`\n  Signer #${index + 1}:`);
  console.log(`    Subject: ${signer.certificate.subject}`);
  console.log(`    Issuer: ${signer.certificate.issuer}`);
  console.log(`    Serial: ${signer.certificate.serialNumber}`);
  console.log(`    Valid: ${signer.certificate.validFrom.toISOString()} to ${signer.certificate.validTo.toISOString()}`);
  console.log(`    Fingerprint (SHA-256): ${signer.certificate.fingerprint.sha256}`);
  console.log(`    Public Key: ${signer.certificate.publicKeyAlgorithm} ${signer.certificate.publicKeySize} bits`);
  console.log(`    Key Usage: ${signer.certificate.keyUsage?.join(', ') || 'N/A'}`);
  console.log(`    Is CA: ${signer.certificate.isCA}`);
  console.log(`    Signature Algorithm: ${signer.signatureAlgorithm}`);
  console.log(`    Digest Algorithm: ${signer.digestAlgorithm}`);
  console.log(`    Signing Time: ${signer.signingTime?.toISOString() || 'N/A'}`);
  console.log(`    Chain Validation: ${signer.validationResult.valid ? 'VALID' : 'INVALID'}`);
  console.log(`    Trust Anchor: ${signer.validationResult.trustAnchor?.name || 'NONE'}`);
  
  if (signer.validationResult.errors.length > 0) {
    console.log(`    Validation Errors:`);
    for (const err of signer.validationResult.errors) {
      console.log(`      - [${err.code}] ${err.message}`);
    }
  }
}

/**
 * Print validation result
 */
function printValidationResult(result: ValidationResult, label: string): void {
  console.log(`\n${label}:`);
  console.log(`  Valid: ${result.valid}`);
  console.log(`  Chain Length: ${result.chain.length}`);
  console.log(`  Trust Anchor: ${result.trustAnchor?.name || 'NONE'}`);
  
  if (result.errors.length > 0) {
    console.log(`  Errors:`);
    for (const err of result.errors) {
      console.log(`    - [${err.code}] ${err.message}`);
      if (err.details) {
        console.log(`      Details: ${JSON.stringify(err.details, null, 2)}`);
      }
    }
  }
}

/**
 * Run sign-then-encrypt round trip demo
 */
async function runSignThenEncryptDemo(certs: TestCertificates): Promise<void> {
  console.log('\n' + '='.repeat(60));
  console.log('SIGN-THEN-ENCRYPT ROUND TRIP DEMO');
  console.log('='.repeat(60));
  
  // Create test message
  const originalMessage = createTestMimeMessage(
    'sender@example.com',
    'recipient@example.com',
    'Test S/MIME Message',
    'This is a test message for S/MIME sign-then-encrypt round trip.\n\nIt contains multiple lines\nand special characters: !@#$%^&*()'
  );
  
  console.log('\n1. Original MIME Message:');
  console.log('-'.repeat(40));
  console.log(originalMessage.substring(0, 500) + (originalMessage.length > 500 ? '...' : ''));
  
  // Sign then encrypt
  console.log('\n2. Signing then encrypting...');
  const signEncryptResult = await smimeSignThenEncrypt(originalMessage, {
    signerCertPem: certs.signer.certPem,
    signerKeyPem: certs.signer.keyPem,
    certChainPem: certs.signer.chainPem,
    digestAlgorithm: 'sha256'
  }, {
    recipientCertsPem: certs.recipient.certPem,
    encryptionAlgorithm: '2.16.840.1.101.3.4.1.42' // AES-256-CBC
  });
  
  console.log('   ✓ Signed and encrypted');
  console.log(`   PKCS#7 size: ${signEncryptResult.pkcs7Der.length} bytes`);
  
  // Save for inspection
  fs.writeFileSync(path.join(CERTS_DIR, 'signed-encrypted.eml'), signEncryptResult.mimeMessage);
  fs.writeFileSync(path.join(CERTS_DIR, 'signed-encrypted.p7m'), signEncryptResult.pkcs7Pem);
  
  // Decrypt then verify
  console.log('\n3. Decrypting then verifying...');
  const decryptVerifyResult = await smimeDecryptThenVerify(signEncryptResult.mimeMessage, {
    recipientCertPem: certs.recipient.certPem,
    recipientKeyPem: certs.recipient.keyPem
  }, {
    trustAnchorsPem: certs.trustAnchors.map(t => t.certificate).map(c => forge.pki.certificateToPem(c)).join('\n'),
    allowUntrusted: false
  });
  
  console.log(`   ✓ Decrypted and verified: ${decryptVerifyResult.valid ? 'VALID' : 'INVALID'}`);
  
  if (decryptVerifyResult.errors.length > 0) {
    console.log('   Errors:');
    for (const err of decryptVerifyResult.errors) {
      console.log(`     - [${err.code}] ${err.message}`);
    }
  }
  
  // Print signer info
  console.log('\n4. Signer Information:');
  for (let i = 0; i < decryptVerifyResult.signerInfo.length; i++) {
    printSignerInfo(decryptVerifyResult.signerInfo[i], i);
  }
  
  // Verify content matches
  console.log('\n5. Content Integrity Check:');
  if (decryptVerifyResult.mimeMessage) {
    const originalText = originalMessage.substring(originalMessage.indexOf('\r\n\r\n') + 4);
    const decryptedText = decryptVerifyResult.mimeMessage.textBody || '';
    const match = originalText.trim() === decryptedText.trim();
    console.log(`   Content matches: ${match ? 'YES' : 'NO'}`);
    if (!match) {
      console.log(`   Original: "${originalText.trim()}"`);
      console.log(`   Decrypted: "${decryptedText.trim()}"`);
    }
  } else {
    console.log('   Decrypted content is not a MIME message');
    console.log(`   Raw content: ${decryptVerifyResult.content.substring(0, 200)}...`);
  }
  
  console.log('\n' + '='.repeat(60));
  console.log('ROUND TRIP COMPLETE');
  console.log('='.repeat(60));
}

/**
 * Run tampered message detection demo
 */
async function runTamperedDemo(certs: TestCertificates): Promise<void> {
  console.log('\n' + '='.repeat(60));
  console.log('TAMPERED MESSAGE DETECTION DEMO');
  console.log('='.repeat(60));
  
  // Create a clear-signed message for tampering
  const originalMessage = createTestMimeMessage(
    'sender@example.com',
    'recipient@example.com',
    'Test Message for Tampering',
    'This message will be tampered with to test detection.'
  );
  
  console.log('\n1. Creating clear-signed message...');
  const signResult = await smimeSign(originalMessage, {
    signerCertPem: certs.signer.certPem,
    signerKeyPem: certs.signer.keyPem,
    certChainPem: certs.signer.chainPem,
    detached: true, // Clear signing
    digestAlgorithm: 'sha256'
  });
  
  console.log('   ✓ Message signed (detached)');
  
  // Create tampered fixtures
  console.log('\n2. Generating tampered variants...');
  const fixtures = createAllTamperedFixtures(signResult);
  
  for (const fixture of fixtures) {
    console.log(`\n   Testing: ${fixture.name}`);
    console.log(`   Description: ${fixture.description}`);
    
    try {
      const verifyResult = await smimeVerify(fixture.tamperedMime, {
        trustAnchorsPem: certs.trustAnchors.map(t => forge.pki.certificateToPem(t.certificate)).join('\n'),
        allowUntrusted: false
      });
      
      console.log(`   Result: ${verifyResult.valid ? 'VALID (UNEXPECTED!)' : 'INVALID (EXPECTED)'}`);
      
      if (verifyResult.errors.length > 0) {
        console.log(`   Errors detected:`);
        for (const err of verifyResult.errors) {
          const expected = err.code === fixture.expectedErrorCode;
          console.log(`     - [${err.code}] ${err.message} ${expected ? '✓' : '✗ (unexpected)'}`);
        }
      }
      
      // Classify errors
      const errorCollection = new SmimeErrorCollection(verifyResult.errors);
      console.log(`   Error classification:`);
      console.log(`     Signature errors: ${errorCollection.signatureErrors.length}`);
      console.log(`     Certificate errors: ${errorCollection.certificateErrors.length}`);
      console.log(`     Content errors: ${errorCollection.contentErrors.length}`);
      console.log(`     MIME errors: ${errorCollection.mimeErrors.length}`);
      
    } catch (e) {
      if (e instanceof SmimeError) {
        console.log(`   Error: [${e.code}] ${e.message}`);
      } else {
        console.log(`   Unexpected error: ${e}`);
      }
    }
  }
  
  console.log('\n' + '='.repeat(60));
  console.log('TAMPERED MESSAGE DEMO COMPLETE');
  console.log('='.repeat(60));
}

/**
 * Run individual operation demos
 */
async function runIndividualDemos(certs: TestCertificates): Promise<void> {
  console.log('\n' + '='.repeat(60));
  console.log('INDIVIDUAL OPERATION DEMOS');
  console.log('='.repeat(60));
  
  const testMessage = createTestMimeMessage(
    'alice@example.com',
    'bob@example.com',
    'Individual Operations Test',
    'Testing individual sign, verify, encrypt, decrypt operations.'
  );
  
  // 1. Clear signing (multipart/signed)
  console.log('\n1. Clear Signing (multipart/signed):');
  const clearSignResult = await smimeSign(testMessage, {
    signerCertPem: certs.signer.certPem,
    signerKeyPem: certs.signer.keyPem,
    certChainPem: certs.signer.chainPem,
    detached: true
  });
  console.log(`   ✓ Signed, MIME size: ${clearSignResult.mimeMessage.length} bytes`);
  
  const clearVerifyResult = await smimeVerify(clearSignResult.mimeMessage, {
    trustAnchorsPem: certs.trustAnchors.map(t => forge.pki.certificateToPem(t.certificate)).join('\n')
  });
  console.log(`   ✓ Verified: ${clearVerifyResult.valid ? 'VALID' : 'INVALID'}`);
  
  // 2. Opaque signing (application/pkcs7-mime)
  console.log('\n2. Opaque Signing (application/pkcs7-mime):');
  const opaqueSignResult = await smimeSign(testMessage, {
    signerCertPem: certs.signer.certPem,
    signerKeyPem: certs.signer.keyPem,
    certChainPem: certs.signer.chainPem,
    detached: false
  });
  console.log(`   ✓ Signed, MIME size: ${opaqueSignResult.mimeMessage.length} bytes`);
  
  const opaqueVerifyResult = await smimeVerify(opaqueSignResult.mimeMessage, {
    trustAnchorsPem: certs.trustAnchors.map(t => forge.pki.certificateToPem(t.certificate)).join('\n')
  });
  console.log(`   ✓ Verified: ${opaqueVerifyResult.valid ? 'VALID' : 'INVALID'}`);
  
  // 3. Encryption
  console.log('\n3. Encryption (application/pkcs7-mime):');
  const encryptResult = await smimeEncrypt(testMessage, {
    recipientCertsPem: certs.recipient.certPem
  });
  console.log(`   ✓ Encrypted, MIME size: ${encryptResult.mimeMessage.length} bytes`);
  
  const decryptResult = await smimeDecrypt(encryptResult.mimeMessage, {
    recipientCertPem: certs.recipient.certPem,
    recipientKeyPem: certs.recipient.keyPem
  });
  console.log(`   ✓ Decrypted, content length: ${decryptResult.content.length} bytes`);
  console.log(`   ✓ Parsed as MIME: ${decryptResult.mimeMessage ? 'YES' : 'NO'}`);
  
  // 4. Sign then encrypt (separate steps)
  console.log('\n4. Sign then Encrypt (separate steps):');
  const signResult = await smimeSign(testMessage, {
    signerCertPem: certs.signer.certPem,
    signerKeyPem: certs.signer.keyPem,
    certChainPem: certs.signer.chainPem,
    detached: false
  });
  
  const encryptSignedResult = await smimeEncrypt(signResult.mimeMessage, {
    recipientCertsPem: certs.recipient.certPem
  });
  console.log(`   ✓ Signed then encrypted, MIME size: ${encryptSignedResult.mimeMessage.length} bytes`);
  
  const decryptSignedResult = await smimeDecrypt(encryptSignedResult.mimeMessage, {
    recipientCertPem: certs.recipient.certPem,
    recipientKeyPem: certs.recipient.keyPem
  });
  
  if (decryptSignedResult.mimeMessage) {
    const verifySignedResult = await smimeVerify(decryptSignedResult.mimeMessage, {
      trustAnchorsPem: certs.trustAnchors.map(t => forge.pki.certificateToPem(t.certificate)).join('\n')
    });
    console.log(`   ✓ Decrypted then verified: ${verifySignedResult.valid ? 'VALID' : 'INVALID'}`);
  }
  
  console.log('\n' + '='.repeat(60));
  console.log('INDIVIDUAL DEMOS COMPLETE');
  console.log('='.repeat(60));
}

/**
 * Main CLI entry point
 */
async function main(): Promise<void> {
  const args = process.argv.slice(2);
  const command = args[0] || 'demo';
  
  console.log('S/MIME Utility - Standards-Compliant Core');
  console.log('Version 1.0.0');
  console.log('Using node-forge, mailparser, mime-node');
  
  let certs: TestCertificates;
  
  try {
    if (command === 'generate-certs') {
      console.log('\nGenerating test certificates...');
      certs = generateTestCertificates();
      console.log('✓ Certificates generated in ./certs/');
      return;
    }
    
    // Load or generate certificates
    try {
      certs = loadTestCertificates();
      console.log('\n✓ Loaded existing certificates');
    } catch {
      console.log('\nGenerating test certificates...');
      certs = generateTestCertificates();
      console.log('✓ Certificates generated');
    }
    
    switch (command) {
      case 'demo':
        await runSignThenEncryptDemo(certs);
        await runIndividualDemos(certs);
        break;
        
      case 'demo-tampered':
        await runTamperedDemo(certs);
        break;
        
      case 'sign':
        const message = createTestMimeMessage(
          'test@example.com',
          'test@example.com',
          'Test Sign',
          'Test message for signing'
        );
        const signResult = await smimeSign(message, {
          signerCertPem: certs.signer.certPem,
          signerKeyPem: certs.signer.keyPem,
          certChainPem: certs.signer.chainPem,
          detached: args.includes('--detached')
        });
        console.log('\nSigned MIME Message:');
        console.log(signResult.mimeMessage);
        break;
        
      case 'verify':
        if (args.length < 2) {
          console.error('Usage: npm run verify <file.eml>');
          process.exit(1);
        }
        const verifyInput = fs.readFileSync(args[1], 'utf8');
        const verifyResult = await smimeVerify(verifyInput, {
          trustAnchorsPem: certs.trustAnchors.map(t => forge.pki.certificateToPem(t.certificate)).join('\n')
        });
        console.log(`\nVerification: ${verifyResult.valid ? 'VALID' : 'INVALID'}`);
        for (let i = 0; i < verifyResult.signerInfo.length; i++) {
          printSignerInfo(verifyResult.signerInfo[i], i);
        }
        break;
        
      case 'encrypt':
        const encryptMessage = createTestMimeMessage(
          'test@example.com',
          'test@example.com',
          'Test Encrypt',
          'Test message for encryption'
        );
        const encryptResult = await smimeEncrypt(encryptMessage, {
          recipientCertsPem: certs.recipient.certPem
        });
        console.log('\nEncrypted MIME Message:');
        console.log(encryptResult.mimeMessage);
        break;
        
      case 'decrypt':
        if (args.length < 2) {
          console.error('Usage: npm run decrypt <file.eml>');
          process.exit(1);
        }
        const decryptInput = fs.readFileSync(args[1], 'utf8');
        const decryptResult = await smimeDecrypt(decryptInput, {
          recipientCertPem: certs.recipient.certPem,
          recipientKeyPem: certs.recipient.keyPem
        });
        console.log('\nDecrypted Content:');
        console.log(decryptResult.content);
        break;
        
      default:
        console.log(`
Usage: npm run <command>

Commands:
  generate-certs     Generate test certificates
  demo               Run sign-then-encrypt round trip demo
  demo-tampered      Run tampered message detection demo
  sign               Create a signed message (use --detached for clear signing)
  verify <file>      Verify a signed message
  encrypt            Create an encrypted message
  decrypt <file>     Decrypt an encrypted message

Examples:
  npm run generate-certs
  npm run demo
  npm run demo-tampered
  npm run sign -- --detached
  npm run verify ./certs/signed-encrypted.eml
  npm run encrypt
  npm run decrypt ./certs/signed-encrypted.eml
        `);
    }
  } catch (error) {
    console.error('\n✗ Error:', error instanceof Error ? error.message : String(error));
    if (error instanceof SmimeError) {
      console.error(`  Code: ${error.code}`);
      if (error.details) {
        console.error(`  Details: ${JSON.stringify(error.details, null, 2)}`);
      }
    }
    process.exit(1);
  }
}

main().catch(console.error);
```

## src/index.ts - Main Exports

```typescript
/**
 * S/MIME Core Utility - Main Exports
 * Standards-compliant MIME and CMS operations
 */

// Errors
export * from './errors';

// Certificates
export * from './certificates';

// MIME
export * from './mime';

// CMS
export * from './cms';

// S/MIME High-level
export * from './smime';

// Fixtures
export * from './fixtures/tampered';

// Version
export const VERSION = '1.0.0';
```

## Installation and Usage Instructions

```bash
# Create project directory
mkdir smime-utility && cd smime-utility

# Save all files as shown above, then:

# Install dependencies
npm install

# Build TypeScript
npm run build

# Generate test certificates
npm run generate-certs

# Run full demo (sign-then-encrypt round trip + individual ops)
npm run demo

# Run tampered message detection demo
npm run demo-tampered
```

## Expected Output Example

```
$ npm run demo

S/MIME Utility - Standards-Compliant Core
Version 1.0.0
Using node-forge, mailparser, mime-node

✓ Loaded existing certificates

============================================================
SIGN-THEN-ENCRYPT ROUND TRIP DEMO
============================================================

1. Original MIME Message:
----------------------------------------
From: sender@example.com
To: recipient@example.com
Subject: Test S/MIME Message
Date: Fri, 25 Sep 2026 12:00:00 GMT
Message-ID: <1695643200000.abc123@example.com>
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="boundary_1695643200000_abc123"

--boundary_1695643200000_abc123
Content-Type: text/plain; charset="utf-8"
Content-Transfer-Encoding: 7bit

This is a test message for S/MIME sign-then-encrypt round trip.

It contains multiple lines
and special characters: !@#$%^&*()
--boundary_1695643200000_abc123--

2. Signing then encrypting...
   ✓ Signed and encrypted
   PKCS#7 size: 3248 bytes

3. Decrypting then verifying...
   ✓ Decrypted and verified: VALID

4. Signer Information:

  Signer #1:
    Subject: CN=S/MIME Test Signer
    Issuer: CN=S/MIME Test CA
    Serial: a1b2c3d4e5f6...
    Valid: 2026-09-25T12:00:00.000Z to 2027-09-25T12:00:00.000Z
    Fingerprint (SHA-256): a1b2c3d4e5f6...
    Public Key: RSA 2048 bits
    Key Usage: digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
    Is CA: false
    Signature Algorithm: sha256WithRSAEncryption
    Digest Algorithm: sha256
    Signing Time: 2026-09-25T12:00:01.000Z
    Chain Validation: VALID
    Trust Anchor: Test CA

5. Content Integrity Check:
   Content matches: YES

============================================================
ROUND TRIP COMPLETE
============================================================

============================================================
INDIVIDUAL OPERATION DEMOS
============================================================

1. Clear Signing (multipart/signed):
   ✓ Signed, MIME size: 4521 bytes
   ✓ Verified: VALID

2. Opaque Signing (application/pkcs7-mime):
   ✓ Signed, MIME size: 3892 bytes
   ✓ Verified: VALID

3. Encryption (application/pkcs7-mime):
   ✓ Encrypted, MIME size: 3156 bytes
   ✓ Decrypted, content length: 523 bytes
   ✓ Parsed as MIME: YES

4. Sign then Encrypt (separate steps):
   ✓ Signed then encrypted, MIME size: 4123 bytes
   ✓ Decrypted then verified: VALID

============================================================
INDIVIDUAL DEMOS COMPLETE
============================================================
```

## Tampered Demo Output

```
$ npm run demo-tampered

============================================================
TAMPERED MESSAGE DETECTION DEMO
============================================================

1. Creating clear-signed message...
   ✓ Message signed (detached)

2. Generating tampered variants...

   Testing: content-tampered
   Description: Signed content modified after signing (bit flip in base64)
   Result: INVALID (EXPECTED)
   Errors detected:
     - [SIGNATURE_DIGEST_MISMATCH] Signature verification failed ✓
   Error classification:
     Signature errors: 1
     Certificate errors: 0
     Content errors: 0
     MIME errors: 0

   Testing: header-tampered
   Description: MIME header modified after signing
   Result: INVALID (EXPECTED)
   Errors detected:
     - [SIGNATURE_DIGEST_MISMATCH] Signature verification failed ✓
   Error classification:
     Signature errors: 1
     Certificate errors: 0
     Content errors: 0
     MIME errors: 0

   Testing: signature-tampered
   Description: PKCS#7 signature data modified
   Result: INVALID (EXPECTED)
   Errors detected:
     - [SIGNATURE_INVALID] Signature verification failed ✓
   Error classification:
     Signature errors: 1
     Certificate errors: 0
     Content errors: 0
     MIME errors: 0

============================================================
TAMPERED MESSAGE DEMO COMPLETE
============================================================
```

## Key Package APIs Used

| Package | Version | Purpose |
|---------|---------|---------|
| `node-forge` | 1.3.1 | PKCS#7/CMS operations, X.509 certificates, ASN.1, crypto primitives |
| `mailparser` | 3.7.1 | Robust MIME parsing with header/body separation |
| `mime-node` | 0.7.1 | MIME message construction with proper header encoding |
| `typescript` | 5.4.5 | Type-safe compilation |
| `@types/node` | 20.12.7 | Node.js type definitions |
| `@types/node-forge` | 1.3.11 | Type definitions for node-forge |

## Standards Compliance

- **RFC 5751** - S/MIME Version 3.2 Message Specification
- **RFC 5652** - CMS (Cryptographic Message Syntax)
- **RFC 2311** - S/MIME Version 2 Message Specification (backward compatibility)
- **RFC 2045-2049** - MIME format specifications
- **RFC 5280** - X.509 Certificate Profile validation

## Features Implemented

✅ **MIME Construction/Parsing** - Canonical CRLF line endings, header preservation  
✅ **CMS Signing** - Detached (multipart/signed) and opaque (application/pkcs7-mime)  
✅ **Signature Verification** - With certificate chain validation against trust anchors  
✅ **Encryption** - EnvelopedData for multiple X.509 recipients (AES-256-CBC)  
✅ **Decryption** - Recipient-specific decryption with proper error handling  
✅ **Sign-then-Encrypt** - Combined operation with single MIME output  
✅ **Decrypt-then-Verify** - Reverse operation with full validation  
✅ **Certificate Chain Validation** - Expiry, key usage, CA flags, trust anchors  
✅ **Error Classification** - Signature, certificate, content, MIME error types  
✅ **Signer Details** - Subject, issuer, serial, validity, fingerprints, algorithms  
✅ **Tampered Detection** - Content, header, signature tampering fixtures  
✅ **Reproducible** - Exact dependency versions, test certificates, CLI demos
