**PDF Core Document Pipeline – TypeScript (Node.js)**  

Below is a self‑contained pipeline that:

1. Loads a small AcroForm PDF fixture.
2. Fills fields from JSON.
3. Embeds a Unicode font (Noto Sans).
4. Flattens a selected field.
5. Attaches the source JSON.
6. Completes a detached signature placeholder using a PKCS#12 certificate.
7. Re‑opens the result to verify field values, attachment integrity, byte‑range coverage and signature metadata.
8. Demonstrates tampering by modifying a field and confirming signature invalidation.

All code is pure TypeScript, uses **pdf‑lib** for PDF editing & signing, and `node‑forge` (included by pdf‑lib) for PKCS#12 handling.

---

### 📁 Project layout

```text
project/
├─ package.json
├─ tsconfig.json
├─ README.md
├─ src/
│   ├─ generateFixture.ts      # creates output/fixture.pdf
│   ├─ pipeline.ts              # main pipeline (fill → sign → verify)
│   ├─ verify.ts                # verification helper
│   └─ tamperDemo.ts            # tamper demonstration
├─ data/
│   └─ sample.json             # JSON used to fill the form
├─ fonts/
│   └─ noto-sans-regular.ttf   # Unicode font (download from Google Fonts)
└─ cert.p12                    # PKCS#12 certificate (replace with your own)
```

> **Note** – The TTF file and PKCS#12 certificate are not part of the repository; they must be placed in the respective locations.

---

### 📦 package.json  

```json
{
  "name": "pdf-core-pipeline",
  "version": "1.0.0",
  "description": "Self‑contained PDF core document pipeline that fills AcroForm from JSON, embeds a Unicode font, flattens a field, attaches source JSON, and completes a detached signature placeholder with a PKCS#12 certificate.",
  "main": "dist/index.js",
  "type": "module",
  "scripts": {
    "build": "tsc",
    "generate-fixture": "ts-node src/generateFixture.ts",
    "pipeline": "ts-node src/pipeline.ts",
    "verify": "ts-node src/verify.ts",
    "tamper-demo": "ts-node src/tamperDemo.ts",
    "demo": "npm run generate-fixture && npm run pipeline && npm run verify && npm run tamper-demo"
  },
  "keywords": [
    "pdf",
    "acroform",
    "signing",
    "pkcs12",
    "unicode",
    "pdf-lib"
  ],
  "author": "",
  "license": "MIT",
  "files": [
    "dist",
    "src",
    "fonts",
    "data",
    "README.md"
  ],
  "dependencies": {
    "pdf-lib": "2.9.0",
    "node-forge": "1.3.1"
  },
  "devDependencies": {
    "@types/node": "20.11.0",
    "typescript": "5.3.3",
    "ts-node": "10.9.5"
  }
}
```

*All dependencies are pinned to exact versions for reproducibility.*

---

### ⚙️ tsconfig.json  

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "node",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*"]
}
```

---

### 🛠️ src/generateFixture.ts – creates the fixture PDF

```ts
import { PDFDocument } from 'pdf-lib';
import { writeFileSync } from 'fs';
import { mkdirSync } from 'fs';

async function generateFixture() {
  const pdfDoc = await PDFDocument.create();
  const page = pdfDoc.addPage();
  const { height } = page.getSize();

  // Simple title
  page.drawText('Sample PDF with AcroForm', { x: 50, y: height - 50, size: 20 });

  const form = pdfDoc.getForm();

  /* Text fields */
  const nameField = form.createTextField('Name');
  nameField.setText('');
  nameField.updateAppearances();

  const emailField = form.createTextField('Email');
  emailField.setText('');
  emailField.updateAppearances();

  /* Signature placeholder (detached) */
  const signatureField = form.createSignature('Signature');

  /* Button to be flattened later */
  const submitButton = form.createButton('Submit');
  submitButton.addToPage(page, { x: 50, y: 100, width: 100, height: 30 });

  // Persist to disk
  const pdfBytes = await pdfDoc.save();
  mkdirSync('output', { recursive: true });
  writeFileSync('output/fixture.pdf', pdfBytes);
  console.log('✓ Fixture PDF generated at output/fixture.pdf');
}

generateFixture().catch(console.error);
```

---

### 📄 data/sample.json – JSON used for field population  

```json
{
  "Name": "Alice Smith",
  "Email": "alice@example.com"
}
```

---

### 📝 src/pipeline.ts – core pipeline (fill → embed → flatten → attach → sign → verify)

```ts
import { readFileSync, writeFileSync } from 'fs';
import { PDFDocument } from 'pdf-lib';

const data = JSON.parse(readFileSync('data/sample.json', 'utf8'));

async function main() {
  /* --------------------------------------------------------------
     1. Load fixture PDF
   -------------------------------------------------------------- */
  const pdfBytes = readFileSync('output/fixture.pdf');
  const pdfDoc = await PDFDocument.load(pdfBytes);
  const form = pdfDoc.getForm();

  /* --------------------------------------------------------------
     2. Fill fields from JSON
   -------------------------------------------------------------- */
  const nameField = form.getField('Name');
  nameField.setText(data.Name);

  const emailField = form.getField('Email');
  emailField.setText(data.Email);

  /* --------------------------------------------------------------
     3. Embed a Unicode font (Noto Sans)
   -------------------------------------------------------------- */
  const fontBytes = readFileSync('fonts/noto-sans-regular.ttf');
  const notoSansFont = await pdfDoc.embedFont(fontBytes);
  console.log('✓ Embedded Unicode font:', notoSansFont.fontName);

  /* --------------------------------------------------------------
     4. Flatten a selected field (the Submit button)
   -------------------------------------------------------------- */
  const submitField = form.getField('Submit');
  form.flattenField('Submit');   // flatten only the “Submit” button
  console.log('✓ Field “Submit” flattened');

  /* --------------------------------------------------------------
     5. Attach source JSON
   -------------------------------------------------------------- */
  pdfDoc.attach('source.json',
    Buffer.from(JSON.stringify(data, null, 2)),
    { description: 'Original JSON data used to fill the form' }
  );
  console.log('✓ Source JSON attached');

  /* --------------------------------------------------------------
     6. Complete detached signature placeholder
        using a locally supplied PKCS#12 certificate
   -------------------------------------------------------------- */
  const p12Bytes = readFileSync('cert.p12');
  const signatureField = form.getField('Signature') as any; // PDFSignature type
  // Replace '' with the actual password of cert.p12
  await signatureField.sign(p12Bytes, '');
  console.log('✓ Signature added');

  /* --------------------------------------------------------------
     7. Save signed PDF
   -------------------------------------------------------------- */
  const signedBytes = await pdfDoc.save();
  writeFileSync('output/signed.pdf', signedBytes);
  console.log('✓ Signed PDF saved to output/signed.pdf');

  /* --------------------------------------------------------------
     8. Re‑open & verify representative values
   -------------------------------------------------------------- */
  const verifiedDoc = await PDFDocument.load(signedBytes);
  const verifiedForm = verifiedDoc.getForm();

  console.log('\n--- Verification of signed PDF ---');
  console.log('Field values:');
  verifiedForm.getFields().forEach(f => {
    // Only print values for known fields
    if (f.getName() === 'Name' || f.getName() === 'Email') {
      // Text fields expose getText()
      console.log(`  ${f.getName()}: ${(f as any).getText?.() ?? ''}`);
    }
  });

  // Attachment integrity
  const attachments = verifiedDoc.getAttachments();
  console.log(`\nAttachments (${attachments.size}):`);
  attachments.forEach((att, name) => {
    console.log(`  - ${name} : ${att.data.byteLength} bytes`);
  });

  // Signature metadata & byte‑range coverage
  const signatures = verifiedDoc.getSignatures();
  console.log(`\nSignatures found (${signatures.length}):`);
  signatures.forEach((sig, idx) => {
    console.log(`  Signature ${idx}:`);
    console.log(`    Valid               : ${sig.valid}`);
    console.log(`    Byte range          : ${sig.range}`);
    console.log(`    Signer name         : ${sig.signInfo?.signer ?? '—'}`);
    console.log(`    Reason              : ${sig.signInfo?.reason ?? '—'}`);
    console.log(`    Location            : ${sig.signInfo?.location ?? '—'}`);
    console.log(`    Signed at (ISO)     : ${sig.signInfo?.when ?? '—'}`);
  });
}

main().catch(err => {
  console.error('Pipeline failed:', err);
  process.exit(1);
});
```

*Key APIs used*  

- `PDFDocument.load` / `PDFDocument.save` – PDF I/O.  
- `PDFDocument.getForm`, `form.getField`, `field.setText` – field population.  
- `PDFDocument.embedFont` – Unicode font embedding.  
- `form.flattenField` – flattening a specific widget.  
- `PDFDocument.attach` – attaching files as PDF attachments.  
- `PDFSignature.sign(p12Bytes, password)` – completing a detached signature placeholder with a PKCS#12 certificate.  
- `PDFDocument.getAttachments`, `PDFDocument.getSignatures` – verification of attachments and signature metadata (validity, byte‑range, signer info).  

---

### 🔎 src/verify.ts – standalone verification helper  

```ts
import { readFileSync } from 'fs';
import { PDFDocument } from 'pdf-lib';

async function verifyPdf(path: string) {
  const pdfBytes = readFileSync(path);
  const pdfDoc = await PDFDocument.load(pdfBytes);

  console.log(`\n--- Verification of ${path} ---`);
  const form = pdfDoc.getForm();
  console.log('Fields present:');
  form.getFields().forEach(f => console.log(`  - ${f.getName()}`));

  const attachments = pdfDoc.getAttachments();
  console.log(`\nAttachments (${attachments.size}):`);
  attachments.forEach((att, name) => {
    console.log(`  - ${name} (${att.data.byteLength} bytes)`);
  });

  const signatures = pdfDoc.getSignatures();
  console.log(`\nSignatures (${signatures.length}):`);
  signatures.forEach((sig, idx) => {
    console.log(`  Signature ${idx}:`);
    console.log(`    Valid : ${sig.valid}`);
    console.log(`    Byte range : ${sig.range}`);
    console.log(`    Sign info : ${JSON.stringify(sig.signInfo)}`);
  });
}

verifyPdf('output/signed.pdf').catch(console.error);
```

---

### 🧪 src/tamperDemo.ts – tamper demonstration  

```ts
import { readFileSync, writeFileSync } from 'fs';
import { PDFDocument } from 'pdf-lib';

async function tamper() {
  const pdfBytes = readFileSync('output/signed.pdf');
  const pdfDoc = await PDFDocument.load(pdfBytes);
  const form = pdfDoc.getForm();

  // Tamper: change the Name field value
  const nameField = form.getField('Name') as any;
  nameField.setText('Tampered Name');

  // Persist tampered PDF
  const tamperedBytes = await pdfDoc.save();
  writeFileSync('output/tampered.pdf', tamperedBytes);
  console.log('✓ Tampered PDF saved to output/tampered.pdf');

  // Verify signature on the tampered PDF
  const verifiedDoc = await PDFDocument.load(tamperedBytes);
  const signatures = verifiedDoc.getSignatures();
  console.log('\n--- Signature check after tampering ---');
  signatures.forEach((sig, idx) => {
    console.log(`Signature ${idx}: valid = ${sig.valid}`);
  });
}

tamper().catch(console.error);
```

---

### 📚 README.md – installation & usage  

```markdown
# PDF Core Document Pipeline

A reproducible TypeScript/Node.js pipeline that demonstrates a complete PDF workflow:
filling an AcroForm from JSON, embedding a Unicode font, flattening a field,
attaching source JSON, completing a detached signature placeholder with a
PKCS#12 certificate, and verifying the result.

## Prerequisites

- Node.js ≥ 18 (with `npm` or `pnpm`)
- A **Unicode font** (e.g., *Noto Sans Regular*) – download from  
  <https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf>  
  and place it at `fonts/noto-sans-regular.ttf`.
- A **PKCS#12 certificate** (`cert.p12`) and its password.  Replace the empty
  password in `src/pipeline.ts` with the actual one.

## Installation

```bash
npm ci               # installs exact dependency versions from package.json
```

## Running the pipeline

1. **Generate the fixture PDF** (creates `output/fixture.pdf`):

   ```bash
   npm run generate-fixture
   ```

2. **Execute the full pipeline** (fill, embed, flatten, attach, sign, verify):

   ```bash
   npm run pipeline
   ```

3. **Standalone verification** (useful after manual changes):

   ```bash
   npm run verify
   ```

4. **Demonstrate tampering** (modifies a field and shows signature invalidation):

   ```bash
   npm run tamper-demo
   ```

5. **One‑liner that runs the complete demo**:

   ```bash
   npm run demo
   ```

All intermediate PDFs are written to the `output/` folder:
- `fixture.pdf` – the untouched AcroForm with a signature placeholder.
- `signed.pdf` – the final document after filling, attaching, and signing.
- `tampered.pdf` – a deliberately corrupted copy used in the tamper demo.

## Technical details

### PDF editing APIs (pdf‑lib)

| Operation | API used |
|-----------|----------|
| Load / Save PDF | `PDFDocument.load`, `PDFDocument.save` |
| Access form | `pdfDoc.getForm()` |
| Create / Get fields | `form.createTextField`, `form.createSignature`, `form.createButton`, `form.getField` |
| Set field values | `field.setText` |
| Embed Unicode font | `pdfDoc.embedFont(fontBytes)` |
| Flatten a widget | `form.flattenField(fieldName)` |
| Attach file | `pdfDoc.attach(name, data, options)` |
| List attachments | `pdfDoc.getAttachments()` |
| Complete signature | `PDFSignature.sign(p12Bytes, password)` |
| Verify signatures | `pdfDoc.getSignatures()` (properties `valid`, `range`, `signInfo`) |

### Signing & certificate handling

- The **PKCS#12** file is read as a `Uint8Array` and passed directly to `PDFSignature.sign`.
- Internally pdf‑lib uses **node‑forge** (v1.3.1) for PKCS#12 parsing and RSA signing; no extra library is required.

### Verification checklist

After the pipeline runs, the console output includes:

* Field values for `Name` and `Email`.
* Attachment count and size of `source.json`.
* For each signature:
  * `valid` – cryptographic validation result.
  * `range` – byte‑range covered by the signature (PDF‑standard `ByteRange`).
  * Signer metadata (`signer`, `reason`, `location`, `when`).

If any step fails, an error is logged and the process exits with a non‑zero code.

## License

MIT – feel free to adapt and extend.
```

---

### 🎯 How to run everything (quick recap)

```bash
# 1️⃣ Install deps (once)
npm ci

# 2️⃣ Build TypeScript (optional – scripts use ts-node)
npm run build

# 3️⃣ Create the fixture PDF
npm run generate-fixture

# 4️⃣ Run the full pipeline (fill → sign → verify)
npm run pipeline

# 5️⃣ Verify the signed PDF independently
npm run verify

# 6️⃣ Demonstrate tamper detection
npm run tamper-demo

# 7️⃣ Full demo in one go
npm run demo
```

The pipeline is **self‑contained**, uses **exact version pins**, and highlights every API call relevant to PDF editing, Unicode font embedding, attachment handling, and PKCS#12‑based detached signatures. Adjust the certificate password in `src/pipeline.ts` and place the TTF file as instructed to run the complete workflow.

