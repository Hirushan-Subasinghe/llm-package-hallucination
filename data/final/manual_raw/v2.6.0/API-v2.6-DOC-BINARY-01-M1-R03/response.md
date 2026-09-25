**PDF Core Document Pipeline (TypeScript) – Overview**

The pipeline consists of two main parts:

1️⃣ **Fixtures Generation** – creates a PDF with an embedded Unicode font, a JSON data file, a PKCS#12 certificate, and the necessary TTF file.

2️⃣ **Core Document Processing** – loads the fixtures, fills the AcroForm fields, flattens a selected field, attaches the JSON, signs the PDF, and verifies the result. A tamper demonstration is also included.

---

### 📦 **package.json** (exact versions)

```json
{
  "name": "pdf-core-pipeline",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "build": "tsc",
    "clean": "rimraf dist",
    "demo": "node dist/demo",
    "start": "npm run build && npm run demo"
  },
  "keywords": ["pdf", "acroform", "signing", "pdf-lib", "pdf-sign"],
  "author": "",
  "license": "MIT",
  "devDependencies": {
    "@types/node": "20.11.20",
    "rimraf": "5.0.1",
    "typescript": "5.3.3"
  },
  "dependencies": {
    "pdf-lib": "1.4.0",
    "@pdf-lib/fontkit": "0.1.0",
    "pdf-sign": "0.2.0",
    "node-forge": "1.3.1",
    "pkcs12-pfx": "0.6.0",
    "fs-extra": "11.1.0",
    "node-fetch": "3.3.2"
  }
}
```

---

### 📄 **tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": false
  }
}
```

---

### 📁 **src/index.ts** – The Core Pipeline

```typescript
import * as fs from 'fs-extra';
import * as path from 'path';
import { PDFDocument, PDFPage, PDFTextField } from 'pdf-lib';
import fontkit from '@pdf-lib/fontkit';
import { signPdf, verifyPdf } from 'pdf-sign';
import * as forge from 'node-forge';
import fetch from 'node-fetch';

// Register fontkit with PDF‑lib
PDFDocument.registerFontkit(fontkit);

const FIXTURES_DIR = path.resolve(__dirname, '../fixtures');
const SIGNED_OUT   = path.resolve(__dirname, '../dist/signed.pdf');
const TAMPERED_OUT = path.resolve(__dirname, '../dist/tampered.pdf');

export class PdfPipeline {
  /* --------------------------------------------------------------
   | 1. Fixtures generation
   -------------------------------------------------------------- */
  static async generateFixtures(): Promise<void> {
    await fs.ensureDir(FIXTURES_DIR);

    // ---- 1a. Download a Unicode‑capable TTF (NotoSans) ----
    const fontUrl = 'https://cdn.jsdelivr.net/npm/@fontsource/noto-sans@5.0.13/files/noto-sans-all-500-normal.ttf';
    const fontResp = await fetch(fontUrl);
    const fontBytes = await fontResp.arrayBuffer();
    const fontPath = path.join(FIXTURES_DIR, 'NotoSans-Regular.ttf');
    await fs.writeFile(fontPath, Buffer.from(fontBytes));
    console.log('✓ Downloaded Unicode font →', fontPath);

    // ---- 1b. Create a PDF with AcroForm fields & a signature placeholder ----
    const doc = await PDFDocument.create();
    const customFont = await doc.embedFont(fontBytes);

    const page = doc.addPage([600, 400]);
    const form = doc.getForm();

    // Name field (Unicode capable)
    const nameField = form.createTextField('Name');
    nameField.setFont(customFont);
    nameField.setFontSize(12);
    nameField.setTextboxSize({ x: 100, y: 350, width: 200, height: 20 });
    nameField.setDefaultValue('');
    form.addFieldToPage(nameField, page);

    // Email field
    const emailField = form.createTextField('Email');
    emailField.setFont(customFont);
    emailField.setFontSize(12);
    emailField.setTextboxSize({ x: 100, y: 300, width: 200, height: 20 });
    emailField.setDefaultValue('');
    form.add
