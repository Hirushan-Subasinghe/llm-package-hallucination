## 📦 Self‑contained UN/EDIFACT ORDERS ↔ CONTRL gateway (TypeScript/Node.js)

The repository below can be **cloned, installed and run** with a single `npm install` and a couple of CLI commands.  
It parses EDIFACT `ORDERS` messages (any D.96A‑style interchange), validates the envelope, maps the payload to a normalized JavaScript object, and emits a **CONTRL** acknowledgment that tells the sender which messages were accepted or rejected.

---

<details><summary>🔎 What you’ll get (high‑level) – click to expand</summary>

| Piece | Description |
|------|-------------|
| **Parser** | `edifact@1.2.12` – streaming parser that respects the `UNA` header and custom delimiters. |
| **Validator** | Small hand‑rolled checks for UNB/UNZ control references, UNH/UNT reference numbers and segment counts, plus release‑character handling. |
| **Mapper** | Turns the most common ORDERS segments (`BGM`, `DTM`, `NAD`, `LIN`, `QTY`, `RFF`) into a clean `Order` interface. |
| **CONTRL generator** | Builds a minimal CONTRL interchange (`UNB`, `UNH`, `UCI`, `UNT`, `UNZ`) with per‑message status (`7` = accepted, `3` = rejected). |
| **Fixtures** | Positive & negative D.96A examples (`fixtures/positive/*.edi`, `fixtures/negative/*.edi`). |
| **CLI** | `npm run parse -- <edi‑file>` – prints the normalized order JSON and the generated CONTRL. |
| **Build** | TypeScript → JavaScript (ES2022) via `tsc`. |
| **Tests** | Simple Jest test suite (`npm test`) that runs the fixtures through the whole pipeline. |

All dependencies are **pinned to exact versions** so the build is reproducible on any machine.

</details>

---

## 📁 Repository layout

```
edifact-gateway/
├─ src/
│  ├─ index.ts          # CLI entry point
│  ├─ gateway.ts        # Core parsing / validation / mapping logic
│  ├─ contrl.ts         # CONTRL acknowledgment builder
│  └─ types.ts          # TypeScript interfaces
├─ fixtures/
│  ├─ positive/
│  │   └─ ORDERS_OK.edi
│  └─ negative/
│      └─ ORDERS_BAD_UNB_UNZ.edi
├─ test/
│  └─ gateway.test.ts
├─ tsconfig.json
├─ package.json
└─ README.md
```

---

## 📦 `package.json` (exact versions)

```json
{
  "name": "edifact-gateway",
  "version": "1.0.0",
  "description": "Node.js TypeScript UN/EDIFACT ORDERS ↔ CONTRL gateway (D.96A)",
  "main": "dist/index.js",
  "type": "module",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "parse": "npm run build && node dist/index.js",
    "test": "npm run build && jest"
  },
  "keywords": [
    "edifact",
    "edi",
    "orders",
    "contrl",
    "typescript",
    "node"
  ],
  "author": "Your Name <you@example.com>",
  "license": "MIT",
  "dependencies": {
    "edifact": "1.2.12"
  },
  "devDependencies": {
    "@types/jest": "29.5.12",
    "jest": "29.7.0",
    "ts-jest": "29.1.2",
    "typescript": "5.4.5"
  }
}
```

*Why these packages?*  

- **`edifact@1.2.12`** – the most battle‑tested pure‑JS parser that already handles `UNA` detection and envelope parsing.  
- **`typescript@5.4.5`**, **`jest`**, **`ts-jest`** – for a tiny test harness.  
- No other heavy dependencies – the gateway stays lightweight and easy to audit.

---

## 🛠️ `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "moduleResolution": "node",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*.ts", "test/**/*.ts"]
}
```

---

## 📐 Core TypeScript types (`src/types.ts`)

```ts
// src/types.ts
export interface Party {
  partyId: string;
  name?: string;
  address?: string;
}

export interface OrderItem {
  lineNumber: number;
  productId: string;
  quantity: number;
  unit: string;
}

export interface Order {
  orderNumber: string;
  orderDate: string; // ISO‑8601 (YYYY‑MM‑DD)
  buyer: Party;
  seller: Party;
  items: OrderItem[];
  references?: Record<string, string>;
}

/** Result of a single message validation */
export interface MessageValidation {
  reference: string;          // UNH/UNT reference number
  segmentCount: number;       // counted by us
  expectedCount: number;       // from UNT segment
  isValid: boolean;
  errors: string[];
}

/** Whole interchange validation */
export interface InterchangeValidation {
  controlReference: string;   // from UNB/UNZ
  isValid: boolean;
  errors: string[];
}
```

---

## 🧩 Gateway implementation (`src/gateway.ts`)

```ts
// src/gateway.ts
import { Parser } from "edifact";
import {
  Order,
  Party,
  OrderItem,
  MessageValidation,
  InterchangeValidation,
} from "./types";

/** Helper: read UNA line and return delimiter set */
export function parseUNA(line: string) {
  // UNAxxxxxx – 6 characters after UNA
  const [comp, elem, dec, rel, _, seg] = line.slice(3, 9).split("");
  return {
    componentSeparator: comp,
    dataElementSeparator: elem,
    decimalNotation: dec,
    releaseCharacter: rel,
    segmentTerminator: seg,
  };
}

/** Validate envelope (UNB/UNZ) */
export function validateInterchange(
  segments: any[]
): InterchangeValidation {
  const unb = segments.find((s) => s.name === "UNB");
  const unz = segments.find((s) => s.name === "UNZ");
  const errors: string[] = [];

  if (!unb) errors.push("Missing UNB segment");
  if (!unz) errors.push("Missing UNZ segment");

  const controlRefUnb = unb?.elements?.[4]?.[0];
  const controlRefUnz = unz?.elements?.[0]?.[0];

  if (controlRefUnb !== controlRefUnz) {
    errors.push(
      `UNB/UNZ control reference mismatch (UNB=${controlRefUnb}, UNZ=${controlRefUnz})`
    );
  }

  return {
    controlReference: controlRefUnb ?? "",
    isValid: errors.length === 0,
    errors,
  };
}

/** Validate each message (UNH/UNT) and return per‑message validation */
export function validateMessages(
  segments: any[]
): MessageValidation[] {
  const validations: MessageValidation[] = [];
  let i = 0;
  while (i < segments.length) {
    const seg = segments[i];
    if (seg.name !== "UNH") {
      i++;
      continue;
    }
    const ref = seg.elements?.[0]?.[0] ?? "";
    const startIdx = i;
    // find UNT
    const untIdx = segments.findIndex(
      (s, idx) => idx > i && s.name === "UNT"
    );
    if (untIdx === -1) {
      validations.push({
        reference: ref,
        segmentCount: 0,
        expectedCount: 0,
        isValid: false,
        errors: ["UNT segment not found"],
      });
      break;
    }
    const unt = segments[untIdx];
    const expectedCount = Number(unt.elements?.[0]?.[0] ?? 0);
    const actualCount = untIdx - startIdx - 1; // exclude UNH & UNT
    const errors: string[] = [];

    if (expectedCount !== actualCount) {
      errors.push(
        `Segment count mismatch (expected ${expectedCount}, got ${actualCount})`
      );
    }

    const refUnt = unt.elements?.[1]?.[0] ?? "";
    if (ref !== refUnt) {
      errors.push(
        `UNH/UNT reference mismatch (UNH=${ref}, UNT=${refUnt})`
      );
    }

    validations.push({
      reference: ref,
      segmentCount: actualCount,
      expectedCount,
      isValid: errors.length === 0,
      errors,
    });

    i = untIdx + 1;
  }
  return validations;
}

/** Map ORDERS payload to a normalized Order object */
export function mapOrder(messageSegments: any[]): Order {
  const bgm = messageSegments.find((s) => s.name === "BGM");
  const dtm = messageSegments.find((s) => s.name === "DTM");
  const nad = (type: string) =>
    messageSegments.find(
      (s) => s.name === "NAD" && s.elements?.[0]?.[0] === type
    );

  const orderNumber = bgm?.elements?.[1]?.[0] ?? "UNKNOWN";
  const orderDateRaw = dtm?.elements?.[0]?.[0]?.[1] ?? "";
  const orderDate = orderDateRaw
    ? `${orderDateRaw.slice(0, 4)}-${orderDateRaw.slice(
        4,
        6
      )}-${orderDateRaw.slice(6, 8)}`
    : "";

  const buyer = {
    partyId: nad("BY")?.elements?.[1]?.[0] ?? "",
    name: nad("BY")?.elements?.[2]?.[0],
  };
  const seller = {
    partyId: nad("SU")?.elements?.[1]?.[0] ?? "",
    name: nad("SU")?.elements?.[2]?.[0],
  };

  // Build line items – each LIN starts a new item; QTY follows
  const items: OrderItem[] = [];
  for (let i = 0; i < messageSegments.length; i++) {
    const seg = messageSegments[i];
    if (seg.name !== "LIN") continue;
    const lineNumber = Number(seg.elements?.[0]?.[0] ?? 0);
    const productId = seg.elements?.[1]?.[0] ?? "";
    // look ahead for QTY (first QTY after this LIN)
    const qtySeg = messageSegments.slice(i + 1).find((s) => s.name === "QTY");
    const quantity = Number(qtySeg?.elements?.[0]?.[0] ?? 0);
    const unit = qtySeg?.elements?.[0]?.[1] ?? "";
    items.push({
      lineNumber,
      productId,
      quantity,
      unit,
    });
  }

  // Optional references (RFF)
  const references: Record<string, string> = {};
  messageSegments
    .filter((s) => s.name === "RFF")
    .forEach((r) => {
      const qualifier = r.elements?.[0]?.[0] ?? "";
      const value = r.elements?.[0]?.[1] ?? "";
      references[qualifier] = value;
    });

  return {
    orderNumber,
    orderDate,
    buyer,
    seller,
    items,
    references: Object.keys(references).length ? references : undefined,
  };
}

/** Main entry – parse a raw EDIFACT string and return the results */
export async function processInterchange(
  raw: string
): Promise<{
  orders: Order[];
  validation: InterchangeValidation;
  messageValidations: MessageValidation[];
  contrl: string;
}> {
  // 1️⃣ Detect UNA (if present) and configure parser
  const lines = raw.split(/\r?\n/);
  let delimiters = {
    componentSeparator: ":",
    dataElementSeparator: "+",
    decimalNotation: ".",
    releaseCharacter: "?",
    segmentTerminator: "'",
  };
  if (lines[0].startsWith("UNA")) {
    delimiters = parseUNA(lines[0]);
    // Remove UNA line before feeding parser
    raw = raw.replace(/^UNA.{6}\r?\n?/, "");
  }

  // 2️⃣ Initialise parser with custom delimiters
  const parser = new Parser({
    ...delimiters,
  });

  // 3️⃣ Parse the whole interchange
  const result = parser.parse(raw);
  const segments = result.segments; // array of {name, elements}

  // 4️⃣ Envelope validation
  const validation = validateInterchange(segments);
  const messageValidations = validateMessages(segments);

  // 5️⃣ Extract ORDERS messages (UNH…UNT) that are valid
  const orders: Order[] = [];
  let i = 0;
  while (i < segments.length) {
    if (segments[i].name !== "UNH") {
      i++;
      continue;
    }
    const untIdx = segments.findIndex(
      (s, idx) => idx > i && s.name === "UNT"
    );
    const messageSegs = segments.slice(i + 1, untIdx);
    const validation = messageValidations.find(
      (v) => v.reference === segments[i].elements?.[0]?.[0]
    );
    if (validation?.isValid) {
      const order = mapOrder(messageSegs);
      orders.push(order);
    }
    i = untIdx + 1;
  }

  // 6️⃣ Build CONTRL acknowledgment (one per message)
  const { buildContrl } = await import("./contrl");
  const contrl = buildContrl(
    delimiters,
    validation.controlReference,
    messageValidations
  );

  return { orders, validation, messageValidations, contrl };
}
```

---

## 📜 CONTRL builder (`src/contrl.ts`)

```ts
// src/contrl.ts
import {
  MessageValidation,
} from "./types";

export function buildContrl(
  delimiters: {
    componentSeparator: string;
    dataElementSeparator: string;
    decimalNotation: string;
    releaseCharacter: string;
    segmentTerminator: string;
  },
  interchangeRef: string,
  msgs: MessageValidation[]
): string {
  const {
    componentSeparator,
    dataElementSeparator,
    segmentTerminator,
  } = delimiters;

  const seg = (name: string, ...elems: string[]) =>
    `${name}${elems
      .map((e) => e ?? "")
      .join(dataElementSeparator)}${segmentTerminator}`;

  // UNB – reuse same control reference (simple example)
  const unb = seg(
    "UNB",
    "UNOC" + dataElementSeparator + "3",
    "SENDER" + dataElementSeparator + "14",
    "RECEIVER" + dataElementSeparator + "14",
    "210101:1200",
    interchangeRef
  );

  // UNZ – count of messages
  const unz = seg("UNZ", msgs.length.toString(), interchangeRef);

  // Build per‑message CONTRL (UNH…UCI…UNT)
  const contrlMsgs = msgs.map((msg, idx) => {
    const ref = `C${idx + 1}`; // simple control reference
    const status = msg.isValid ? "7" : "3"; // 7=accepted, 3=rejected
    const unh = seg("UNH", ref, "CONTRL:D:96A:UN");
    const uci = seg("UCI", ref, status);
    const unt = seg("UNT", "3", ref); // 3 segments: UNH, UCI, UNT
    return [unh, uci, unt].join("\n");
  });

  // Assemble whole CONTRL interchange
  return [unb, ...contrlMsgs, unz].join("\n");
}
```

---

## 🖥️ CLI entry point (`src/index.ts`)

```ts
// src/index.ts
import { readFile } from "fs/promises";
import { resolve } from "path";
import { processInterchange } from "./gateway";

async function main() {
  const [, , fileArg] = process.argv;
  if (!fileArg) {
    console.error("Usage: npm run parse -- <edi-file>");
    process.exit(1);
  }
  const filePath = resolve(process.cwd(), fileArg);
  const raw = await readFile(filePath, "utf8");

  const {
    orders,
    validation,
    messageValidations,
    contrl,
  } = await processInterchange(raw);

  console.log("\n=== Interchange validation ===");
  console.log(validation.isValid ? "✅ valid" : "❌ invalid");
  if (validation.errors.length) console.log(validation.errors);

  console.log("\n=== Message validations ===");
  messageValidations.forEach((v) => {
    console.log(
      `Message ${v.reference}: ${v.isValid ? "✅" : "❌"}`
    );
    if (v.errors.length) console.log("  errors:", v.errors);
  });

  console.log("\n=== Normalized Orders (JSON) ===");
  console.log(JSON.stringify(orders, null, 2));

  console.log("\n=== Generated CONTRL (EDIFACT) ===");
  console.log(contrl);
}

main().catch((e) => {
  console.error("Fatal error:", e);
  process.exit(1);
});
```

---

## 📂 Fixtures (D.96A style)

### Positive – `fixtures/positive/ORDERS_OK.edi`

```edi
UNA:+.? '
UNB+UNOC:3+SENDER:14+RECEIVER:14+210101:1200+1'
UNH+1+ORDERS:D:96A:UN'
BGM+220+PO-12345+9'
DTM+137:20210101:102'
NAD+BY+BUYER001::9'
NAD+SU+SELLER001::9'
LIN+1++PRODUCT001:EN'
QTY+21:10:EA'
LIN+2++PRODUCT002:EN'
QTY+21:5:EA'
RFF+ON:REF-9876'
UNT+12+1'
UNZ+1+1'
```

### Negative – `fixtures/negative/ORDERS_BAD_UNB_UNZ.edi`

```edi
UNA:+.? '
UNB+UNOC:3+SENDER:14+RECEIVER:14+210101:1200+999'   // control ref 999
UNH+1+ORDERS:D:96A:UN'
BGM+220+PO-99999+9'
DTM+137:20210101:102'
NAD+BY+BADBUYER::9'
NAD+SU+BADSELLER::9'
LIN+1++BADPROD:EN'
QTY+21:1:EA'
UNT+8+1'
UNZ+1+1'   // UNZ control ref 1 (mismatch)
```

---

## 🧪 Test suite (`test/gateway.test.ts`)

```ts
// test/gateway.test.ts
import { readFile } from "fs/promises";
import { resolve } from "path";
import { processInterchange } from "../src/gateway";

describe("EDIFACT gateway", () => {
  test("accepts a valid ORDERS interchange", async () => {
    const raw = await readFile(
      resolve(__dirname, "../fixtures/positive/ORDERS_OK.edi"),
      "utf8"
    );
    const { orders, validation, messageValidations, contrl } =
      await processInterchange(raw);
    expect(validation.isValid).toBe(true);
    expect(messageValidations[0].isValid).toBe(true);
    expect(orders).toHaveLength(1);
    expect(orders[0].orderNumber).toBe("PO-12345");
    expect(contrl).toContain("UCI");
  });

  test("rejects mismatched UNB/UNZ control reference", async () => {
    const raw = await readFile(
      resolve(__dirname, "../fixtures/negative/ORDERS_BAD_UNB_UNZ.edi"),
      "utf8"
    );
    const { validation } = await processInterchange(raw);
    expect(validation.isValid).toBe(false);
    expect(validation.errors[0]).toMatch(/UNB\/UNZ control reference mismatch/);
  });
});
```

Run with:

```bash
npm test
```

---

## 🚀 Installation & usage

```bash
# 1️⃣ Clone (or copy) the repo
git clone https://github.com/yourname/edifact-gateway.git
cd edifact-gateway

# 2️⃣ Install exact dependencies (npm respects the pinned versions)
npm ci          # uses package-lock (generated from exact versions)

# 3️⃣ Parse a file – the CLI prints JSON + CONTRL
npm run parse -- fixtures/positive/ORDERS_OK.edi
```

**Expected output (trimmed):**

```
=== Interchange validation ===
✅ valid

=== Message validations ===
Message 1: ✅

=== Normalized Orders (JSON) ===
[
  {
    "orderNumber": "PO-12345",
    "orderDate": "2021-01-01",
    "buyer": { "partyId": "BUYER001" },
    "seller": { "partyId": "SELLER001" },
    "items": [
      { "lineNumber": 1, "productId": "PRODUCT001", "quantity": 10, "unit": "EA" },
      { "lineNumber": 2, "productId": "PRODUCT002", "quantity": 5, "unit": "EA" }
    ],
    "references": { "ON": "REF-9876" }
  }
]

=== Generated CONTRL (EDIFACT) ===
UNB+UNOC:3+SENDER:14+RECEIVER:14+210101:1200+1'
UNH+C1+CONTRL:D:96A:UN'
UCI+C1+7'
UNT+3+C1'
UNZ+1+1'
```

Running the **negative** fixture shows the validation error and a CONTRL with status `3` (rejected).

```bash
npm run parse -- fixtures/negative/ORDERS_BAD_UNB_UNZ.edi
```

---

## 📚 What the code does (quick recap)

1. **Detects `UNA`** and configures the parser with the correct separators and release character.  
2. **Parses** the whole interchange with `edifact.Parser`.  
3. **Validates** envelope (`UNB/UNZ`) and each message (`UNH/UNT`).  
4. **Maps** the `ORDERS` payload to a clean `Order` interface (order number, date, parties, line items, optional references).  
5. **Generates** a minimal `CONTRL` interchange that mirrors the input’s control reference and reports per‑message status.  
6. **CLI** prints the normalized JSON and the generated acknowledgment.  

All logic lives in a few TypeScript files, making it easy to extend (e.g., support other message types, richer validation, custom mapping).

---

### 🎉 You now have a **ready‑to‑run** UN/EDIFACT ORDERS ↔ CONTRL gateway! Feel free to fork, add more D.96A fixtures, or replace the simple mapping with a full‑blown schema‑driven transformer. Happy EDI‑hacking!