**Self-Contained Node.js/TypeScript Image-to-Searchable PDF Pipeline**

---

### Overview

This pipeline processes **oriented JPEG** and **small multipage TIFF** inputs, honors EXIF orientation, reports ICC and XMP metadata with a documented preserve-or-normalize policy, performs selectable-language OCR, creates an invisible text layer while preserving page geometry, and emits both extracted text and a metadata report. It includes bounded worker concurrency and representative orientation/OCR-coordinate assertions.

---

### 📋 Package.json (Exact Versions)

```json
{
  "name": "image-to-pdf-pipeline",
  "version": "1 .0.0",
  "private": true,
  "description": "Self‑contained Node.js/TypeScript core image‑to‑searchable‑PDF pipeline.",
  "main": "dist/pipeline.js",
  "scripts": {
    "build": "tsc && copyfiles -f \"src/**/*.json\" dist",
    "dev": "ts-node src/pipeline.ts",
    "process": "node dist/pipeline.js --input ./sample.jpg --input ./sample.tif",
    "verify": "node dist/verify.js",
    "clean": "rimraf dist *.pdf *.json",
    "lint": "eslint src/**/*.ts",
    "format": "prettier --write src/**/*.ts",
    "type-check": "tsc --noEmit",
    "test": "jest",
    "precommit": "npm run lint && npm run format && npm run type-check && npm run test && npm run build"
  },
  "keywords": [
    "sharp",
    "pdf-lib",
    "tesseract.js",
    "p-limit",
    "searchable-pdf",
    "ocr",
    "exif",
    "metadata"
  ],
  "author": "Your Name",
  "license": "MIT",
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=9.0.0"
  },
  "dependencies": {
    "sharp": "^0.33.2",
    "pdf-lib": "^2.10.1",
    "tesseract.js": "^5.0.0",
    "p-limit": "^3.0.1",
    "yargs": "^17.7.2",
    "fs-extra": "^11.2.0",
    "chalk": "^4.1.2"
  },
  "devDependencies": {
    "typescript": "^5.2.3",
    "ts-node": "^10.9.1",
    "eslint": "^8.57.0",
    "@typescript-eslint/parser": "^7.0.1",
    "@typescript-eslint/eslint-plugin": "^7.0.1",
    "prettier": "^3.2.5",
    "eslint-config-prettier": "^9.0.0",
    "eslint-plugin-prettier": "^5.0.0",
    "jest": "^29.7.0",
    "@types/jest": "^29.5.12",
    "@types/node": "^20.11.0",
    "c8": "^9.1.0",
    "rimraf": "^5.0.5",
    "copyfiles": "^2.4.1"
  }
}
```

---

### 📁 Project Structure

```
src/
├─ types.ts               # Type definitions
├─ config.ts              # Runtime configuration
├─ concurrency.ts         # Bounded worker utility
├─ metadataReporter.ts    # ICC/XMP reporting with policy
├─ ocrProcessor.ts        # Tesseract wrapper
├─ pdfCreator.ts          # PDF generation with invisible text layer
├─ pipeline.ts            # Main orchestration
└─ verify.ts              # Orientation & OCR coordinate assertions
```

---

### 📄 src/types.ts

```ts
export interface ExtractedWord {
  text: string;
  bbox: { x0: number; y0: number; x1: number; y1: number };
}
export interface ExtractedPage {
  page: number;
  text: string;
  words: ExtractedWord[];
}
export interface ExtractedFile {
  file: string;
  pages: ExtractedPage[];
}
export interface MetadataReport {
  file: string;
  format: string;
  size: { width: number; height: number };
  orientation: number;
  iccProfile?: string;   // base64
  xmpMetadata?: string; // base64
  policy: 'preserve' | 'normalize';
  pages?: number;
}
```

---

### 📄 src/config.ts

```ts
export interface PipelineConfig {
  concurrency: number;
  metadataPolicy: 'preserve' | 'normalize';
  ocrLanguage: string;
}
export const config: PipelineConfig = {
  concurrency: parseInt(process.env.CONCURRENCY ?? '4', 10),
  metadataPolicy
