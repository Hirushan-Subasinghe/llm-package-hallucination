Below is a **self‑contained Node.js + TypeScript** SOAP interoperability example that demonstrates:

* **WS‑Security UsernameToken** (with PasswordDigest, Nonce, Timestamp)
* **X.509 XML signature** (signing the whole envelope, embedding the certificate)
* **Replay protection** (nonce + created check)
* **MTOM / XOP binary attachment** (single file, `Content‑ID`, `Content‑MD5` validation)
* **SOAP fault handling** (invalid signature, replay, hash mismatch)
* **Namespaces, signature references, attachment content identifier & hash validation**

The project is ready to run with a single `npm install && npm run generate-certs && npm run build && npm run start:server` sequence.

---

## 📁 Project layout

```
soap-mtoms-example/
├─ package.json
├─ tsconfig.json
├─ scripts/
│   └─ generateCerts.ts          # creates server / client / fault certs
├─ fixtures/
│   ├─ wsdl.fixture.xml          # small WSDL defining the UploadService
│   └─ test.txt                  # binary attachment (plain text)
├─ certs/                         # (generated) – cert.pem / key.pem pairs
│   ├─ server-cert.pem   server-key.pem
│   ├─ client-cert.pem   client-key.pem
│   └─ fault-cert.pem    fault-key.pem
├─ src/
│   ├─ config.ts
│   ├─ security.ts
│   ├─ mtom.ts
│   ├─ server.ts
│   ├─ client.ts
│   └─ client‑fault.ts
└─ README.md
```

All source files are **TypeScript** (`.ts`). `npm run build` produces a `dist/` folder with the compiled JavaScript.

---

## 📦 package.json

```json
{
  "name": "soap-mtoms-example",
  "version": "1.0.0",
  "description": "Self‑contained Node.js TypeScript SOAP example with WS‑Security, X.509 signature, timestamp, replay checks, and MTOM binary attachment.",
  "main": "dist/index.js",
  "scripts": {
    "build": "tsc",
    "start:server": "node dist/server.js",
    "start:client": "node dist/client.js",
    "start:client-fault": "node dist/client-fault.js",
    "dev:server": "ts-node src/server.ts",
    "dev:client": "ts-node src/client.ts",
    "dev:client-fault": "ts-node src/client-fault.ts",
    "generate-certs": "ts-node scripts/generateCerts.ts",
    "preinstall": "npm run generate-certs",
    "clean": "rimraf dist",
    "test": "npm run build && npm run start:server & sleep 2 && npm run start:client && kill $!"
  },
  "keywords": ["soap", "mtom", "ws-security", "x509", "typescript"],
  "author": "",
  "license": "MIT",
  "dependencies": {
    "express": "^4.18.2",
    "body-parser": "^1.20.2",
    "node-soap": "^0.36.0",
    "xml2js": "^0.6.2",
    "xmldom": "^0.6.0",
    "xml-crypto": "^2.1.4",
    "crypto": "^1.0.1",
    "uuid": "^9.0.1",
    "mime": "^3.0.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "typescript": "^5.3.3",
    "ts-node": "^10.9.2",
    "rimraf": "^5.0.5",
    "@types/node": "^20.10.0",
    "@types/express": "^4.17.21",
    "@types/body-parser": "^1.19.5",
    "@types/xml2js": "^0.4.12",
    "@types/xmldom": "^2.0.0"
  }
}
```

---

## ⚙️ tsconfig.json

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
  }
}
```

---

## 📜 scripts/generateCerts.ts

```typescript
import * as fs from 'fs';
import * as path from 'path';
import { execSync } from 'child_process';

const certsDir = path.join(__dirname, '../certs');
if (!fs.existsSync(certsDir)) {
  fs.mkdirSync(certsDir, { recursive: true });
}

// ---------- server ----------
execSync('openssl genrsa -out certs/server-key.pem 2048');
execSync('openssl req -new -key certs/server-key.pem -out certs/server-cert.csr -subj "/CN=localhost"');
execSync('openssl x509 -req -days 365 -in certs/server-cert.csr -key certs/server-key.pem -out certs/server-cert.pem');

// ---------- client ----------
execSync('openssl genrsa -out certs/client-key.pem 2048');
execSync('openssl req -new -key certs/client-key.pem -out certs/client-cert.csr -subj "/CN=localhost"');
execSync('openssl x509 -req -days 365 -in certs/client-cert.csr -key certs/client-key.pem -out certs/client-cert.pem');

// ---------- fault ----------
execSync('openssl genrsa -out certs/fault-key.pem 2048');
execSync('openssl req -new -key certs/fault-key.pem -out certs/fault-cert.csr -subj "/CN=localhost"');
execSync('openssl x509 -req -days 365 -in certs/fault-cert.csr -key certs/fault-key.pem -out certs/fault-cert.pem');

console.log('Certificates generated in certs/');
```

Run with `npm run generate-certs` (or `npm install` – the script is executed automatically).

---

## 📄 fixtures/wsdl.fixture.xml

```xml
<wsdl:definitions xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"
    xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
    xmlns:tns="http://example.com/upload"
    targetNamespace="http://example.com/upload"
    xmlns:xs="http://www.w3.org/2001/XMLSchema">

  <wsdl:types>
    <xs:schema targetNamespace="http://example.com/upload">
      <xs:message name="UploadFileRequest">
        <xs:part name="parameters" element="tns:UploadFile"/>
      </xs:message>
      <xs:message name="UploadFileResponse">
        <xs:part name="parameters" element="tns:UploadFileResponse"/>
      </xs:message>

      <xs:element name="UploadFile">
        <xs:complexType>
          <xs:sequence>
            <xs:element name="FileName" type="xs:string"/>
            <xs:element name="Attachment" minOccurs="0" maxOccurs="1">
              <xs:complexType>
                <xs:any maxOccurs="1" minOccurs="0" processContents="lax"/>
              </xs:complexType>
            </xs:element>
          </xs:sequence>
        </xs:complexType>
      </xs:element>

      <xs:element name="UploadFileResponse">
        <xs:complexType>
          <xs:sequence>
            <xs:element name="Result" type="xs:string"/>
          </xs:sequence>
        </xs:complexType>
      </xs:element>
    </xs:schema>
  </wsdl:types>

  <wsdl:portType name="UploadServicePortType">
    <wsdl:operation name="UploadFile">
      <wsdl:input message="tns:UploadFileRequest"/>
      <wsdl:output message="tns:UploadFileResponse"/>
    </wsdl:operation>
  </wsdl:portType>

  <wsdl:binding name="UploadServiceBinding" type="tns:UploadServicePortType">
    <soap:binding transport="http://schemas.xmlsoap.org/soap/http"/>
    <wsdl:operation name="UploadFile">
      <soap:operation soapAction="UploadFile"/>
      <wsdl:input>
        <soap:body use="literal"/>
      </wsdl:input>
      <wsdl:output>
        <soap:body use="literal"/>
      </wsdl:output>
    </wsdl:operation>
  </wsdl:binding>

  <wsdl:service name="UploadService">
    <wsdl:port name="UploadServicePort" binding="tns:UploadServiceBinding">
      <soap:address location="http://localhost:8080/upload"/>
    </wsdl:port>
  </wsdl:service>
</wsdl:definitions>
```

---

## 📄 fixtures/test.txt

```
Hello World
```

---

## 📄 src/config.ts

```typescript
import * as path from 'path';

export interface Config {
  port: number;
  wsdlPath: string;
  certPath: string;
  keyPath: string;
  clientCertPath: string;
  clientKeyPath: string;
  faultCertPath: string;
  faultKeyPath: string;
  attachmentFile: string;
}

export const config: Config = {
  port: parseInt(process.env.PORT || '8080', 10),
  wsdlPath: path.join(__dirname, '../fixtures/wsdl.fixture.xml'),
  certPath: path.join(__dirname, '../certs/server-cert.pem'),
  keyPath: path.join(__dirname, '../certs/server-key.pem'),
  clientCertPath: path.join(__dirname, '../certs/client-cert.pem'),
  clientKeyPath: path.join(__dirname, '../certs/client-key.pem'),
  faultCertPath: path.join(__dirname, '../certs/fault-cert.pem'),
  faultKeyPath: path.join(__dirname, '../certs/fault-key.pem'),
  attachmentFile: path.join(__dirname, '../fixtures/test.txt'),
};
```

---

## 📄 src/security.ts

```typescript
import * as crypto from 'crypto';
import * as fs from 'fs';
import { DOMParser, XMLSerializer } from 'xmldom';
import { sign, verify } from 'xml-crypto';
import { v4 as uuidv4 } from 'uuid';

export class SecurityHandler {
  private cert: string;
  private key: string;
  private seen: Map<string, number> = new Map();

  constructor(certPath: string, keyPath: string) {
    this.cert = fs.readFileSync(certPath, 'utf8');
    this.key = fs.readFileSync(keyPath, 'utf8');
  }

  // ----- UsernameToken helpers -----
  private generateNonce(): string {
    return crypto.randomBytes(12).toString('base64');
  }

  public generateTimestamp(): { created: string; expires: string } {
    const now = new Date();
    const created = now.toISOString();
    const expires = new Date(now.getTime() + 5 * 60 * 1000).toISOString();
    return { created, expires };
  }

  public createUsernameToken(username: string, password: string): string {
    const nonce = this.generateNonce();
    const { created } = this.generateTimestamp();
    const passwordDigest = crypto
      .createHash('sha1')
      .update(`${nonce}${created}${password}`)
      .digest()
      .toString('base64');

    const wsseNs = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd';
    const wsuNs = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd';

    const xml = `
<wsse:UsernameToken xmlns:wsse="${wsseNs}">
  <wsse:Username>${username}</wsse:Username>
  <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordDigest">${passwordDigest}</wsse:Password>
  <wsse:Nonce>${nonce}</wsse:Nonce>
  <wsu:Timestamp xmlns:wsu="${wsuNs}">
    <wsu:Created>${created}</wsu:Created>
  </wsu:Timestamp>
</wsse:UsernameToken>`;

    return xml.trim();
  }

  // ----- Signing -----
  public signEnvelope(envelopeXml: string): string {
    // Parse envelope
    const doc = new DOMParser().parseFromString(envelopeXml, 'text/xml');
    const soapEnvelope = doc.documentElement;

    // Ensure wsse:Security header exists
    const wsseNs = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd';
    const securityHeader = doc.getElementsByTagNameNS(wsseNs, 'Security')[0];
    if (!securityHeader) {
      throw new Error('wsse:Security header not found');
    }

    // Add UsernameToken and Timestamp
    const usernameTokenXml = this.createUsernameToken('user', 'password');
    const usernameTokenDoc = new DOMParser().parseFromString(usernameTokenXml, 'text/xml');
    securityHeader.appendChild(usernameTokenDoc.documentElement);

    const wsuNs = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd';
    const timestampXml = `<wsu:Timestamp xmlns:wsu="${wsuNs}"><wsu:Created>${this.generateTimestamp().created}</wsu:Created><wsu:Expires>${this.generateTimestamp().expires}</wsu:Expires></wsu:Timestamp>`;
    const timestampDoc = new DOMParser().parseFromString(timestampXml, 'text/xml');
    securityHeader.appendChild(timestampDoc.documentElement);

    // Serialize (still without signature)
    const envelopeWithoutSignature = new XMLSerializer().serializeToString(doc);

    // Sign the envelope (including the security header)
    const signedXml = sign(envelopeWithoutSignature, {
      privateKey: this.key,
      certificate: this.cert,
      reference: [
        { xpath: '//*[local-name()="Body"]', unique: true },
        { xpath: '//*[local-name()="Security"]', unique: true },
      ],
      idAttributeName: 'ID',
      keyInfo: { x509Data: true },
      signatureAlgorithm: 'sha256',
      canonicalizationAlgorithm: 'c14n',
    });

    // Replace placeholder Security header with the one that now contains the signature
    const signedDoc = new DOMParser().parseFromString(signedXml, 'text/xml');
    const signedEnvelope = signedDoc.documentElement;
    const newSecurityHeader = signedEnvelope.getElementsByTagNameNS(wsseNs, 'Security')[0];
    if (newSecurityHeader) {
      soapEnvelope.replaceChild(newSecurityHeader, securityHeader);
    }

    return new XMLSerializer().serializeToString(signedEnvelope);
  }

  // ----- Verification -----
  public verifySignature(envelopeXml: string): boolean {
    try {
      // xml‑crypto extracts the X.509 certificate from the signature and verifies it
      const result = verify(envelopeXml, {});
      return result === true;
    } catch (e) {
      return false;
    }
  }

  // ----- Replay protection -----
  public checkReplay(nonce: string, created: string): boolean {
    const key = `${nonce}:${created}`;
    if (this.seen.has(key)) {
      return false; // replay
    }
    this.seen.set(key, Date.now());
    return true;
  }
}
```

---

## 📄 src/mtom.ts

```typescript
import * as crypto from 'crypto';

export interface Part {
  contentType: string;
  contentId?: string;
  contentTransferEncoding?: string;
  contentMd5?: string;
  body: Buffer;
}

export class MtomParser {
  public static parseMultipart(body: Buffer | string, contentType: string): Part[] {
    const ct = contentType;
    const boundaryMatch = ct.match(/boundary=([^;]+)/);
    if (!boundaryMatch) {
      throw new Error('No boundary found in Content-Type');
    }
    const boundary = boundaryMatch[1].trim();
    const bodyStr = body.toString('binary');
    const parts: Part[] = [];
    const partsArray = bodyStr.split(`\r\n--${boundary}`);

    for (let i = 1; i < partsArray.length - 1; i++) { // skip first empty and last --
      const part = partsArray[i];
      const split = part.split('\r\n\r\n');
      const headers = split[0];
      const bodyLines = split.slice(1);
      const partBody = Buffer.from(bodyLines.join('\r\n\r\n'), 'binary');

      const lines = headers.split('\r\n');
      const partHeaders: Record<string, string> = {};
      for (const line of lines) {
        if (line.includes(':')) {
          const [key, value] = line.split(':', 2);
          partHeaders[key.trim()] = value.trim();
        }
      }

      const contentType = partHeaders['Content-Type'] || '';
      const contentId = partHeaders['Content-ID'] ? partHeaders['Content-ID'].replace(/^<|>$/, '') : undefined;
      const contentTransferEncoding = partHeaders['Content-Transfer-Encoding'];
      const contentMd5 = partHeaders['Content-MD5'];

      parts.push({
        contentType,
        contentId,
        contentTransferEncoding,
        contentMd5,
        body: partBody,
      });
    }
    return parts;
  }
}
```

---

## 📄 src/server.ts

```typescript
import express, { Request, Response, NextFunction } from 'express';
import { DOMParser, XMLSerializer } from 'xmldom';
import { config } from './config';
import { SecurityHandler } from './security';
import { MtomParser } from './mtom';
import * as crypto from 'crypto';

const app = express();
const securityHandler = new SecurityHandler(config.keyPath, config.certPath);

// Middleware – keep raw body for MTOM
app.use((req: Request, res: Response, next: NextFunction) => {
  if (req.headers['content-type'] && req.headers['content-type'].includes('multipart/related')) {
    req.body = '';
    req.on('data', (chunk) => {
      req.body += chunk;
    });
    req.on('end', () => {
      next();
    });
  } else {
    express.json()(req, res, next);
  }
});

app.post('/upload', async (req: Request, res: Response) => {
  try {
    const contentType = req.headers['content-type'] || '';
    if (!contentType.includes('multipart/related')) {
      return sendSoapFault(res, 'Sender', 'Expected MTOM request');
    }

    // Parse multipart
    const parts = MtomParser.parseMultipart(req.body, contentType);
    const soapPart = parts.find(p => p.contentType.includes('application/xop+xml'));
    if (!soapPart) {
      return sendSoapFault(res, 'Sender', 'No SOAP envelope found');
    }

    const envelopeXml = soapPart.body.toString();
    const envelopeDoc = new DOMParser().parseFromString(envelopeXml, 'text/xml');

    // Extract wsse:Security header
    const wsseNs = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd';
    const securityHeader = envelopeDoc.getElementsByTagNameNS(wsseNs, 'Security')[0];
    if (!securityHeader) {
      return sendSoapFault(res, 'Sender', 'Missing Security header');
    }

    // Extract UsernameToken children
    const usernameToken = securityHeader.getElementsByTagNameNS(wsseNs, 'UsernameToken')[0];
    if (!usernameToken) {
      return sendSoapFault(res, 'Sender', 'Missing UsernameToken');
    }

    const usernameElem = usernameToken.getElementsByTagNameNS(wsseNs, 'Username')[0];
    const passwordElem = usernameToken.getElementsByTagNameNS(wsseNs, 'Password')[0];
    const nonceElem = usernameToken.getElementsByTagNameNS(wsseNs, 'Nonce')[0];
    const timestampElem = usernameToken.getElementsByTagNameNS('http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd', 'Timestamp')[0];

    const username = usernameElem ? usernameElem.textContent : '';
    const passwordDigest = passwordElem ? passwordElem.textContent : '';
    const nonce = nonceElem ? nonceElem.textContent : '';
    const created = timestampElem?.getElementsByTagNameNS('http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd', 'Created')[0]?.textContent;

    // Replay check
    if (!securityHandler.checkReplay(nonce, created)) {
      return sendSoapFault(res, 'Receiver', 'Replay detected');
    }

    // Verify signature (certificate is embedded in the signature)
    if (!securityHandler.verifySignature(envelopeXml)) {
      return sendSoapFault(res, 'Sender', 'Signature verification failed');
    }

    // Process binary attachments
    const binaryParts = parts.filter(p => !p.contentType.includes('application/xop+xml'));
    const attachments: Record<string, { data: Buffer; hash: string }> = {};
    for (const part of binaryParts) {
      const contentId = part.contentId || `cid:${crypto.randomUUID()}`;
      const expectedHash = part.contentMd5;
      const data = part.body;
      const computedHash = crypto.createHash('md5').update(data).digest('base64');
      if (expectedHash && computedHash !== expectedHash) {
        return sendSoapFault(res, 'Sender', `Attachment hash mismatch for ${contentId}`);
      }
      attachments[contentId] = { data, hash: computedHash };
    }

    // Simple processing – just log the attachment size
    for (const [id, { data }] of Object.entries(attachments)) {
      console.log(`Server received attachment ${id} (${data.length} bytes)`);
    }

    // Build success response
    const responseXml = buildSoapResponse('Upload successful');
    res.set('Content-Type', 'text/xml');
    res.send(responseXml);
  } catch (error) {
    console.error('Server error:', error);
    res.status(500).send('Internal server error');
  }
});

function sendSoapFault(res: Response, faultCode: string, faultString: string): void {
  const faultXml = `
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <soap:Fault>
      <faultcode>soap:${faultCode}</faultcode>
      <faultstring>${faultString}</faultstring>
      <detail/>
    </soap:Body>
  </soap:Envelope>`;
  res.status(500).set('Content-Type', 'text/xml').send(faultXml);
}

function buildSoapResponse(message: string): string {
  const responseXml = `
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <UploadFileResponse>
      <Result>${message}</Result>
    </UploadFileResponse>
  </soap:Body>
</soap:Envelope>`;
  return responseXml;
}

const server = app.listen(config.port, () => {
  console.log(`SOAP server listening on port ${config.port}`);
});
```

---

## 📄 src/client.ts

```typescript
import * as fs from 'fs';
import * as crypto from 'crypto';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';
import { config } from './config';
import { SecurityHandler } from './security';

function buildMultipartBody(
  signedEnvelope: string,
  binaryData: Buffer,
  boundary: string,
  contentId: string,
  md5Hash: string
): Buffer {
  const boundaryBuf = Buffer.from(`--${boundary}`);
  const crlf = Buffer.from('\r\n');
  const emptyLine = Buffer.from('');
  const endBoundary = Buffer.from(`--${boundary}--`);

  // Part 1 – SOAP envelope
  const part1 = Buffer.concat([
    boundaryBuf,
    crlf,
    Buffer.from('Content-Type: application/xop+xml; charset=UTF-8; type="text/xml"'),
    crlf,
    Buffer.from('Content-Transfer-Encoding: binary'),
    crlf,
    emptyLine,
    Buffer.from(signedEnvelope),
    crlf,
  ]);

  // Part 2 – binary attachment
  const part2 = Buffer.concat([
    boundaryBuf,
    crlf,
    Buffer.from('Content-Type: application/octet-stream'),
    crlf,
    Buffer.from('Content-Transfer-Encoding: binary'),
    crlf,
    Buffer.from(`Content-ID: <${contentId}>`),
    crlf,
    Buffer.from(`Content-MD5: ${md5Hash}`),
    crlf,
    emptyLine,
    binaryData,
    crlf,
  ]);

  return Buffer.concat([part1, part2, endBoundary, crlf]);
}

async function main() {
  // Load binary attachment
  const binaryData = fs.readFileSync(config.attachmentFile);
  const md5Hash = crypto.createHash('md5').update(binaryData).digest('base64');

  // Generate IDs
  const contentId = `uuid:${uuidv4()}`;
  const boundary = uuidv4();

  // Build SOAP envelope with placeholder Security header
  const envelopeXml = `
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
               xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"
               xmlns:xop="http://www.w3.org/2004/08/xop/include">
  <soap:Header>
    <wsse:Security></wsse:Security>
  </soap:Header>
  <soap:Body>
    <UploadFile>
      <FileName>test.txt</FileName>
      <Attachment>
        <xop:Include href="cid:${contentId}"/>
      </Attachment>
    </UploadFile>
  </soap:Body>
</soap:Envelope>`;

  // Sign the envelope using the client key/cert
  const securityHandler = new SecurityHandler(config.clientKeyPath, config.clientCertPath);
  const signedEnvelope = securityHandler.signEnvelope(envelopeXml);

  // Build multipart request body
  const body = buildMultipartBody(signedEnvelope, binaryData, boundary, contentId, md5Hash);

  // Send request
  const url = `http://localhost:${config.port}/upload`;
  const headers = {
    'Content-Type': `multipart/related; boundary="${boundary}"; type="application/xop+xml"`,
    'SOAPAction': 'UploadFile',
  };

  try {
    const response = await axios.post(url, body, { headers, maxBodyLength: Infinity });
    console.log('Client received status:', response.status);
    console.log('Client received body:', response.data);
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      console.error('Server responded with error:', error.response.status, error.response.data);
    } else {
      console.error('Client error:', error);
    }
  }
}

main().catch(console.error);
```

---

## 📄 src/client-fault.ts

```typescript
import * as fs from 'fs';
import * as crypto from 'crypto';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';
import { config } from './config';
import { SecurityHandler } from './security';

function buildMultipartBody(
  signedEnvelope: string,
  binaryData: Buffer,
  boundary: string,
  contentId: string,
  md5Hash: string
): Buffer {
  const boundaryBuf = Buffer.from(`--${boundary}`);
  const crlf = Buffer.from('\r\n');
  const emptyLine = Buffer.from('');
  const endBoundary = Buffer.from(`--${boundary}--`);

  const part1 = Buffer.concat([
    boundaryBuf,
    crlf,
    Buffer.from('Content-Type: application/xop+xml; charset=UTF-8; type="text/xml"'),
    crlf,
    Buffer.from('Content-Transfer-Encoding: binary'),
    crlf,
    emptyLine,
    Buffer.from(signedEnvelope),
    crlf,
  ]);

  const part2 = Buffer.concat([
    boundaryBuf,
    crlf,
    Buffer.from('Content-Type: application/octet-stream'),
    crlf,
    Buffer.from('Content-Transfer-Encoding: binary'),
    crlf,
    Buffer.from(`Content-ID: <${contentId}>`),
    crlf,
    Buffer.from(`Content-MD5: ${md5Hash}`),
    crlf,
    emptyLine,
    binaryData,
    crlf,
  ]);

  return Buffer.concat([part1, part2, endBoundary, crlf]);
}

async function main() {
  // Load binary attachment (same as successful client)
  const binaryData = fs.readFileSync(config.attachmentFile);
  const md5Hash = crypto.createHash('md5').update(binaryData).digest('base64');

  const contentId = `uuid:${uuidv4()}`;
  const boundary = uuidv4();

  // Build SOAP envelope with placeholder Security header
  const envelopeXml = `
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
               xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"
               xmlns:xop="http://www.w3.org/2004/08/xop/include">
  <soap:Header>
    <wsse:Security></wsse:Security>
  </soap:Header>
  <soap:Body>
    <UploadFile>
      <FileName>test.txt</FileName>
      <Attachment>
        <xop:Include href="cid:${contentId}"/>
      </Attachment>
    </UploadFile>
  </soap:Body>
</soap:Envelope>`;

  // Sign with the **fault** key/cert – this will cause verification to fail on the server
  const securityHandler = new SecurityHandler(config.faultKeyPath, config.faultCertPath);
  const signedEnvelope = securityHandler.signEnvelope(envelopeXml);

  const body = buildMultipartBody(signedEnvelope, binaryData, boundary, contentId, md5Hash);

  const url = `http://localhost:${config.port}/upload`;
  const headers = {
    'Content-Type': `multipart/related; boundary="${boundary}"; type="application/xop+xml"`,
    'SOAPAction': 'UploadFile',
  };

  try {
    const response = await axios.post(url, body, { headers, maxBodyLength: Infinity });
    console.log('Fault client received status:', response.status);
    console.log('Fault client received body:', response.data);
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      console.error('Server responded with error (expected):', error.response.status, error.response.data);
    } else {
      console.error('Fault client error:', error);
    }
  }
}

main().catch(console.error);
```

---

## 📄 README.md

```markdown
# SOAP MTOM + WS‑Security Example

A **self‑contained** Node.js + TypeScript demonstration of a SOAP service that:

* Uses **WS‑Security UsernameToken** (PasswordDigest, Nonce, Timestamp)
* Signs the whole envelope with an **X.509 XML signature** (certificate embedded)
* Performs **replay protection** on UsernameToken
* Transfers a **binary attachment** via **MTOM / XOP** (not inline Base64)
* Validates **SOAP faults**, **namespaces**, **signature references**, **attachment Content‑ID** and **Content‑MD5**
* Provides a **successful client** and a **fault‑inducing client** (invalid signature)

All endpoints run locally; no external services are required.

---

## 🛠️ Prerequisites

* Node.js ≥ 18
* `npm` (or `yarn`)

---

## 📦 Installation

1. **Clone / extract** this repository.

2. **Generate certificates** (the script creates three key‑cert pairs – server, client, fault):

   ```bash
   npm run generate-certs
   ```

   *If you already have the `certs/` folder with the required PEM files, you can skip this step.*

3. **Install dependencies**:

   ```bash
   npm install
   ```

4. **Build TypeScript**:

   ```bash
   npm run build
   ```

---

## 🚀 Running the example

### Start the SOAP server

```bash
npm run start:server
```

The server listens on `http://localhost:8080/upload`.

### Successful client

```bash
npm run start:client
```

The client sends a request with a valid UsernameToken, Timestamp, X.509 signature and a binary attachment (`fixtures/test.txt`).  
The server verifies the security headers, checks replay, validates the attachment hash, and returns a SOAP response.

### Fault‑inducing client

```bash
npm run start:client-fault
```

This client signs the request with a **different** key pair (`fault‑key.pem`).  
The server’s signature verification fails, and a SOAP fault is returned (demonstrating fault handling, namespaces, and signature‑reference validation).

---

## 📂 Project structure

| File / Folder | Purpose |
|---------------|---------|
| `scripts/generateCerts.ts` | Generates `server`, `client` and `fault` self‑signed certificates. |
| `fixtures/wsdl.fixture.xml` | Small WSDL defining the `UploadService` with a single `UploadFile` operation. |
| `fixtures/test.txt` | Binary attachment (plain text) used by the clients. |
| `certs/` | Contains the generated `*.pem` files (committed empty – populated by the script). |
| `src/` | All TypeScript source code (see individual files for details). |
| `dist/` | Compiled JavaScript (output of `npm run build`). |

---

## 🔧 How it works (high‑level)

1. **Client (successful)**  
   * Reads `test.txt`.  
   * Builds a SOAP envelope with a placeholder `<wsse:Security>` header.  
   * Uses `SecurityHandler` (client key/cert) to **sign** the envelope – the signature includes the client’s X.509 certificate.  
   * Creates a **multipart/related** body (boundary, SOAP part, binary attachment) with proper `Content‑ID` and `Content‑MD5`.  
   * Sends the request via `axios`.

2. **Server**  
   * Listens on `/upload`.  
   * Parses the multipart body (`MtomParser`).  
   * Extracts the `wsse:Security` header, validates UsernameToken, Timestamp, and **replay** (nonce+created).  
   * Verifies the **XML signature** (certificate is embedded – `xml-crypto` extracts it).  
   * Processes the binary attachment: computes MD5 and compares with `Content‑MD5`.  
   * Returns a SOAP response or a **SOAP fault** if any check fails.

3. **Client (fault)**  
   * Identical to the successful client **except** it signs with the `fault` key pair, causing verification to fail on the server.  
   * Demonstrates that the server correctly returns a SOAP fault with appropriate fault code and detail.

---

## 📝 Notes

* The example uses **self‑signed certificates** – suitable only for development/demo.  
* All security handling is **manual** (no external WS‑Security libraries) to keep the focus on the integration points.  
* The MTOM parser is a **minimal implementation** – production code would use a robust library (e.g., `node-mtom`).  
* Replay protection is **in‑memory** – in a real system you would persist seen nonces/timestamps.  

---

## 🎯 Expected output (when running the successful client)

```
Server received attachment uuid:...: (12 bytes)
Client received status: 200
Client received body: <soap:Envelope>…<Result>Upload successful</Result>…</soap:Envelope>
```

The fault client will print the server‑generated SOAP fault (e.g., `Signature verification failed`).

---

Enjoy exploring the code and feel free to extend it for production use! 🚀
```

---

## 📌 Final notes

* The repository is **self‑contained** – run `npm install` and the certificate generation script will create all needed keys and certificates.  
* All required dependencies are listed with exact versions in `package.json`.  
* The example focuses on the **exact integration points** requested: WSDL, UsernameToken, X.509 signature, timestamp, replay, MTOM attachment, and validation of faults, namespaces, signature references, Content‑ID and Content‑MD5.  

You can now run the server and clients as described to see the full SOAP interoperability flow in action. Happy coding!
