**Self-contained Node.js TypeScript UN/EDIFACT Gateway**

Below is a complete, self-contained project with:

- **package.json** (dependencies and scripts)
- **tsconfig.json** (compiler settings)
- **src/** (source code)
- **fixtures/** (positive and negative EDIFACT samples)
- **README.md** (installation and usage instructions)

---

### package.json

```json
{
  "name": "edifact-gateway",
  "version": "0.1 .1",
  "private": true,
  "description": "A Node.js TypeScript UN/EDIFACT gateway for ORDERS messages with syntax detection, validation, mapping, and CONTRL acknowledgment generation.",
  "main": "dist/index.js",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "process:positive": "node dist/index.js fixtures/orders_positive.edifact",
    "process:negative": "node dist/index.js fixtures/orders_negative.edifact",
    "clean": "rimraf dist",
    "prebuild": "npm run clean",
    "postbuild": "echo \"Build complete. Generated files in dist/\"",
    "prestart": "npm run build",
    "preprocess:positive": "npm run build",
    "preprocess:negative": "npm run build"
  },
  "repository": {
    "type": "git",
    "url": "git+https://github.com/yourusername/edifact-gateway.git"
  },
  "keywords": [
    "edifact",
    "UN/EDIFACT",
    "ORDERS",
    "gateway",
    "typescript",
    "parser"
  ],
  "author": "Your Name",
  "license": "MIT",
  "bugs": {
    "url": "https://github.com/yourusername/edifact-gateway/issues"
  },
  "homepage": "https://github.com/yourusername/edifact-gateway#readme",
  "devDependencies": {
    "@types/node": "^20.10.0",
    "nodemon": "^3.0.1",
    "ts-node": "^10.9.2",
    "typescript": "^5.3.2",
    "rimraf": "^5.0.1"
  },
  "dependencies": {
    "edifact-parser": "^2.2.0",
    "fs-extra": "^11.1.0",
    "chalk": "^5.3.0"
  }
}
```

---

### tsconfig.json

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
    "declaration": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

---

### src/interfaces.ts

```typescript
export interface Segment {
  tag: string;
  dataElements: string[][];
  compositeElements?: string[][];
  raw?: string;
}

export interface SyntaxInfo {
  releaseChar: string;
  dataSeparator: string;
  componentSeparator: string;
  decimalSeparator: string;
  segmentSeparator: string;
  reserved: string;
}

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  acceptedSegments: Segment[];
  rejectedSegments: Segment[];
}

export interface NormalizedOrder {
  interchangeHeader: InterchangeHeader;
  messages: Message[];
}

export interface InterchangeHeader {
  sender: string;
  receiver: string;
  dateTime: string;
  interchangeControlReference: string;
}

export interface Message {
  messageHeader: MessageHeader;
  lineItems: LineItem[];
  parties: Party[];
  references: Reference[];
  dates: DateInfo[];
  quantities: QuantityInfo[];
}

export interface MessageHeader {
  messageType: string;
  version: string;
  association: string;
  messageControlReference: string;
}

export interface LineItem {
  lineNumber: string;
  goodsDescription: string;
  quantity: QuantityInfo;
  unitOfMeasure: string;
  price: string;
  currency: string;
  dates: DateInfo[];
  parties: Party[];
  references: Reference[];
}

export interface Party {
  partyQualifier: string;
  partyId: string;
  name: string;
  address: string;
}

export interface Reference {
  qualifier: string;
  reference: string;
}

export interface DateInfo {
  qualifier: string;
  date: string;
  time?: string;
}

export interface QuantityInfo {
  qualifier: string;
  quantity: string;
  unit: string;
}
```

---

###
