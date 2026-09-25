# EPUB 3 Builder & Validator — Complete Node.js TypeScript Project

## Project Structure

```
epub3-toolkit/
├── package.json
├── tsconfig.json
├── src/
│   ├── types.ts                 # TypeScript interfaces
│   ├── constants.ts             # EPUB 3 constants, media types, namespaces
│   ├── builder/
│   │   ├── index.ts             # Main builder export
│   │   ├── EpubBuilder.ts       # Core EPUB assembly
│   │   ├── PackageDocument.ts   # package.opf generation
│   │   ├── NavigationDocument.ts # nav.xhtml generation
│   │   ├── Container.ts         # META-INF/container.xml
│   │   ├── Mimetype.ts          # mimetype file (uncompressed, first)
│   │   └── ZipWriter.ts         # ZIP archive with correct ordering
│   ├── validator/
│   │   ├── index.ts             # Main validator export
│   │   ├── EpubValidator.ts     # Orchestrates validation
│   │   ├── ZipValidator.ts      # ZIP structure & ordering
│   │   ├── PackageValidator.ts  # package.opf validation
│   │   ├── NavigationValidator.ts # nav.xhtml validation
│   │   ├── ContentValidator.ts  # HTML/CSS/resource validation
│   │   ├── SecurityValidator.ts # Traversal & remote content checks
│   │   └── Report.ts            # Validation report types
│   ├── utils/
│   │   ├── xml.ts               # XML serialization helpers
│   │   ├── html.ts              # HTML parsing helpers
│   │   └── fs.ts                # File system helpers
│   └── cli.ts                   # Command-line interface
├── examples/
│   ├── two-chapter/             # Valid two-chapter EPUB example
│   │   ├── build.ts             # Build script
│   │   ├── cover.svg            # Cover image
│   │   ├── styles.css           # Stylesheet
│   │   ├── chapter1.xhtml       # Chapter 1
│   │   └── chapter2.xhtml       # Chapter 2
│   └── fixtures/                # Validation failure fixtures
│       ├── bad-zip-order/       # mimetype not first
│       ├── missing-package/     # No package.opf
│       ├── duplicate-id/        # Duplicate IDs in manifest
│       ├── bad-media-type/      # Wrong media type
│       ├── broken-link/         # Internal link to missing resource
│       ├── missing-namespace/   # Wrong XML namespace
│       ├── traversal-attack/    # Path traversal in href
│       └── remote-script/       # Remote active content
├── tests/
│   ├── builder.test.ts
│   ├── validator.test.ts
│   └── fixtures.test.ts
└── dist/                        # Compiled output (gitignored)
```

---

## `package.json`

```json
{
  "name": "epub3-toolkit",
  "version": "1.0.0",
  "description": "Self-contained EPUB 3 builder and validator for Node.js TypeScript",
  "main": "dist/cli.js",
  "types": "dist/cli.d.ts",
  "scripts": {
    "build": "tsc",
    "clean": "rm -rf dist",
    "prebuild": "npm run clean",
    "example:build": "ts-node examples/two-chapter/build.ts",
    "example:validate": "node dist/cli.js validate examples/two-chapter/output/book.epub",
    "fixture:validate-all": "node dist/cli.js validate-all examples/fixtures",
    "test": "jest --coverage",
    "test:watch": "jest --watch",
    "lint": "eslint src/**/*.ts --ext .ts",
    "prettier": "prettier --write \"src/**/*.ts\" \"examples/**/*.ts\""
  },
  "bin": {
    "epub3": "dist/cli.js"
  },
  "keywords": [
    "epub",
    "epub3",
    "ebook",
    "builder",
    "validator",
    "zip",
    "xml"
  ],
  "author": "EPUB 3 Toolkit Contributors",
  "license": "MIT",
  "dependencies": {
    "adm-zip": "0.5.16",
    "fast-xml-parser": "4.4.1",
    "jsdom": "24.1.0",
    "uuid": "9.0.1",
    "yargs": "17.7.2"
  },
  "devDependencies": {
    "@types/adm-zip": "0.5.5",
    "@types/jest": "29.5.12",
    "@types/node": "20.14.2",
    "@types/uuid": "9.0.8",
    "@types/yargs": "17.0.32",
    "jest": "29.7.0",
    "prettier": "3.3.2",
    "ts-jest": "29.1.4",
    "ts-node": "10.9.2",
    "typescript": "5.4.5"
  },
  "engines": {
    "node": ">=20.0.0"
  },
  "packageManager": "npm@10.8.1"
}
```

---

## `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
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
    "isolatedModules": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "examples", "tests"]
}
```

---

## `src/types.ts`

```typescript
/**
 * Core TypeScript interfaces for EPUB 3 structure
 */

export interface EpubMetadata {
  identifier: string;           // Unique identifier (UUID URN)
  title: string;
  language: string;             // RFC 5646 language tag
  author?: string;
  publisher?: string;
  date?: string;                // ISO 8601 publication date
  modified?: string;            // ISO 8601 last modification date
  description?: string;
  subject?: string[];
  rights?: string;
  coverImagePath?: string;      // Path to cover image in manifest
}

export interface ManifestItem {
  id: string;
  href: string;                 // Relative path within EPUB
  mediaType: string;            // MIME type
  properties?: string;          // e.g., "cover-image", "nav", "svg"
  fallback?: string;            // Fallback item ID
}

export interface SpineItem {
  idref: string;                // References manifest item ID
  linear?: "yes" | "no";        // Default: "yes"
  properties?: string;          // e.g., "page-spread-left", "page-spread-right"
}

export interface GuideEntry {
  type: string;                 // EPUB 2 guide type (for backward compat)
  title: string;
  href: string;
}

export interface Chapter {
  id: string;
  title: string;
  contentPath: string;          // Path to XHTML file
  linear?: boolean;             // Default true
  properties?: string;
}

export interface EpubOptions {
  metadata: EpubMetadata;
  chapters: Chapter[];
  manifestItems: ManifestItem[]; // Additional manifest items (CSS, fonts, images)
  spine: SpineItem[];
  coverImagePath?: string;       // Path to cover image file on disk
  cssPath?: string;              // Path to CSS file on disk
  outputPath: string;            // Output .epub file path
}

export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
  info: ValidationInfo[];
}

export interface ValidationError {
  code: string;
  message: string;
  location?: string;            // File/path within EPUB
  severity: "error";
}

export interface ValidationWarning {
  code: string;
  message: string;
  location?: string;
  severity: "warning";
}

export interface ValidationInfo {
  code: string;
  message: string;
  location?: string;
  severity: "info";
}

export interface ZipEntryInfo {
  name: string;
  compressed: boolean;
  size: number;
  compressedSize: number;
  isDirectory: boolean;
}
```

---

## `src/constants.ts`

```typescript
/**
 * EPUB 3 constants, media types, and XML namespaces
 * Per EPUB 3.3 specification
 */

export const EPUB_MEDIA_TYPE = "application/epub+zip";
export const MIMETYPE_CONTENT = EPUB_MEDIA_TYPE;
export const MIMETYPE_FILENAME = "mimetype";

export const CONTAINER_XML_PATH = "META-INF/container.xml";
export const CONTAINER_NAMESPACE = "urn:oasis:names:tc:opendocument:xmlns:container";

export const PACKAGE_NAMESPACE = "http://www.idpf.org/2007/opf";
export const PACKAGE_VERSION = "3.0";
export const PACKAGE_PREFIXES = `
  rendition: http://www.idpf.org/vocab/rendition/# 
  media: http://www.idpf.org/epub/vocab/overlays/# 
  xhtml: http://www.w3.org/1999/xhtml
`.trim();

export const DC_NAMESPACE = "http://purl.org/dc/elements/1.1/";
export const DCTERMS_NAMESPACE = "http://purl.org/dc/terms/";
export const OPF_NAMESPACE = "http://www.idpf.org/2007/opf";
export const XHTML_NAMESPACE = "http://www.w3.org/1999/xhtml";
export const SVG_NAMESPACE = "http://www.w3.org/2000/svg";
export const NCX_NAMESPACE = "http://www.daisy.org/z3986/2005/ncx/";
export const XML_NAMESPACE = "http://www.w3.org/XML/1998/namespace";

export const NAV_DOC_PATH = "EPUB/nav.xhtml";
export const PACKAGE_DOC_PATH = "EPUB/package.opf";
export const CONTENT_DIR = "EPUB";

export const REQUIRED_MANIFEST_PROPERTIES = {
  NAV: "nav",
  COVER_IMAGE: "cover-image",
  SVG: "svg",
  SCRIPTED: "scripted",
  SWITCH: "switch",
} as const;

export const MEDIA_TYPES: Record<string, string> = {
  // Core
  ".xhtml": "application/xhtml+xml",
  ".html": "application/xhtml+xml",
  ".xml": "application/xml",
  ".css": "text/css",
  ".js": "application/javascript",
  
  // Images
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".png": "image/png",
  ".svg": "image/svg+xml",
  ".gif": "image/gif",
  ".webp": "image/webp",
  
  // Fonts
  ".woff": "font/woff",
  ".woff2": "font/woff2",
  ".ttf": "font/ttf",
  ".otf": "font/otf",
  
  // Audio/Video
  ".mp3": "audio/mpeg",
  ".mp4": "video/mp4",
  ".webm": "video/webm",
  
  // Other
  ".ncx": "application/x-dtbncx+xml",
  ".smil": "application/smil+xml",
  ".pls": "application/pls+xml",
};

export const EPUB3_REQUIRED_FILES = [
  MIMETYPE_FILENAME,
  CONTAINER_XML_PATH,
] as const;

export const PACKAGE_REQUIRED_ELEMENTS = [
  "metadata",
  "manifest",
  "spine",
] as const;

export const METADATA_REQUIRED_FIELDS = [
  "identifier",
  "title",
  "language",
] as const;

export const SPINE_MIN_ITEMS = 1;

export const VALIDATION_CODES = {
  // ZIP structure
  ZIP_MIMETYPE_NOT_FIRST: "ZIP_MIMETYPE_NOT_FIRST",
  ZIP_MIMETYPE_COMPRESSED: "ZIP_MIMETYPE_COMPRESSED",
  ZIP_MIMETYPE_WRONG_CONTENT: "ZIP_MIMETYPE_WRONG_CONTENT",
  ZIP_MISSING_CONTAINER: "ZIP_MISSING_CONTAINER",
  ZIP_MISSING_PACKAGE: "ZIP_MISSING_PACKAGE",
  ZIP_TRAVERSAL_PATH: "ZIP_TRAVERSAL_PATH",
  
  // Package document
  PKG_MISSING_METADATA: "PKG_MISSING_METADATA",
  PKG_MISSING_MANIFEST: "PKG_MISSING_MANIFEST",
  PKG_MISSING_SPINE: "PKG_MISSING_SPINE",
  PKG_DUPLICATE_ID: "PKG_DUPLICATE_ID",
  PKG_INVALID_MEDIA_TYPE: "PKG_INVALID_MEDIA_TYPE",
  PKG_MISSING_REQUIRED_METADATA: "PKG_MISSING_REQUIRED_METADATA",
  PKG_IDENTIFIER_NOT_UNIQUE: "PKG_IDENTIFIER_NOT_UNIQUE",
  PKG_SPINE_REF_MISSING: "PKG_SPINE_REF_MISSING",
  PKG_MANIFEST_REF_MISSING: "PKG_MANIFEST_REF_MISSING",
  PKG_UNREFERENCED_MANIFEST_ITEM: "PKG_UNREFERENCED_MANIFEST_ITEM",
  PKG_INVALID_XMLNS: "PKG_INVALID_XMLNS",
  
  // Navigation document
  NAV_MISSING: "NAV_MISSING",
  NAV_INVALID_XMLNS: "NAV_INVALID_XMLNS",
  NAV_MISSING_TOC: "NAV_MISSING_TOC",
  NAV_BROKEN_LINK: "NAV_BROKEN_LINK",
  
  // Content
  CONTENT_BROKEN_INTERNAL_LINK: "CONTENT_BROKEN_INTERNAL_LINK",
  CONTENT_MISSING_RESOURCE: "CONTENT_MISSING_RESOURCE",
  CONTENT_REMOTE_ACTIVE_CONTENT: "CONTENT_REMOTE_ACTIVE_CONTENT",
  CONTENT_TRAVERSAL_IN_HREF: "CONTENT_TRAVERSAL_IN_HREF",
  CONTENT_INVALID_XHTML: "CONTENT_INVALID_XHTML",
  CONTENT_SCRIPT_IN_NAV: "CONTENT_SCRIPT_IN_NAV",
  
  // Security
  SEC_PATH_TRAVERSAL: "SEC_PATH_TRAVERSAL",
  SEC_REMOTE_SCRIPT: "SEC_REMOTE_SCRIPT",
  SEC_REMOTE_IFRAME: "SEC_REMOTE_IFRAME",
  SEC_REMOTE_FORM_ACTION: "SEC_REMOTE_FORM_ACTION",
  SEC_EVENT_HANDLER: "SEC_EVENT_HANDLER",
  
  // General
  GEN_MALFORMED_XML: "GEN_MALFORMED_XML",
  GEN_MALFORMED_HTML: "GEN_MALFORMED_HTML",
} as const;
```

---

## `src/utils/xml.ts`

```typescript
/**
 * XML serialization and parsing utilities
 * Uses fast-xml-parser for high-performance parsing
 */

import { XMLParser, XMLBuilder, X2jOptions, BuilderOptions } from "fast-xml-parser";
import { VALIDATION_CODES } from "../constants";

export const parserOptions: X2jOptions = {
  ignoreAttributes: false,
  attributeNamePrefix: "@_",
  textNodeName: "#text",
  parseAttributeValue: true,
  parseTagValue: true,
  trimValues: true,
  preserveOrder: true,
  removeNSPrefix: false,
  processEntities: true,
  htmlEntities: true,
};

export const builderOptions: BuilderOptions = {
  ignoreAttributes: false,
  attributeNamePrefix: "@_",
  textNodeName: "#text",
  format: true,
  indentBy: "  ",
  suppressEmptyNode: true,
  suppressBooleanAttributes: false,
  selfClosingTagEnding: "/>",
};

export const xmlParser = new XMLParser(parserOptions);
export const xmlBuilder = new XMLBuilder(builderOptions);

/**
 * Serialize a JavaScript object to XML string with declaration
 */
export function serializeXml(obj: Record<string, unknown>, encoding = "UTF-8"): string {
  const xml = xmlBuilder.build(obj);
  return `<?xml version="1.0" encoding="${encoding}"?>\n${xml}`;
}

/**
 * Parse XML string to JavaScript object
 */
export function parseXml(xml: string): Record<string, unknown> {
  return xmlParser.parse(xml) as Record<string, unknown>;
}

/**
 * Create a namespaced attribute object
 */
export function nsAttr(namespace: string, localName: string, value: string): Record<string, string> {
  return { [`@_${namespace}:${localName}`]: value };
}

/**
 * Create an element with namespace prefix
 */
export function nsElement(prefix: string, localName: string, content: unknown, attributes?: Record<string, string>): Record<string, unknown> {
  const key = `${prefix}:${localName}`;
  const result: Record<string, unknown> = { [key]: content };
  if (attributes) {
    Object.assign(result[key], attributes);
  }
  return result;
}

/**
 * Validate XML namespace declarations on root element
 */
export function validateRootNamespaces(
  xml: string,
  requiredNamespaces: Record<string, string>,
  filePath: string
): { valid: boolean; errors: string[] } {
  const errors: string[] = [];
  
  try {
    const parsed = parseXml(xml);
    const rootKey = Object.keys(parsed)[0];
    const root = parsed[rootKey] as Record<string, unknown>;
    
    for (const [prefix, uri] of Object.entries(requiredNamespaces)) {
      const attrKey = prefix === "" ? "@_xmlns" : `@_xmlns:${prefix}`;
      const actualUri = root[attrKey] as string | undefined;
      
      if (!actualUri) {
        errors.push(`${VALIDATION_CODES.GEN_MALFORMED_XML}: Missing namespace declaration for ${prefix || "default"} at ${filePath}`);
      } else if (actualUri !== uri) {
        errors.push(`${VALIDATION_CODES.GEN_MALFORMED_XML}: Namespace mismatch for ${prefix || "default"}: expected ${uri}, got ${actualUri} at ${filePath}`);
      }
    }
  } catch (e) {
    errors.push(`${VALIDATION_CODES.GEN_MALFORMED_XML}: Failed to parse XML at ${filePath}: ${e}`);
    return { valid: false, errors };
  }
  
  return { valid: errors.length === 0, errors };
}

/**
 * Escape XML special characters
 */
export function escapeXml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}
```

---

## `src/utils/html.ts`

```typescript
/**
 * HTML parsing and link extraction utilities
 * Uses jsdom for DOM parsing
 */

import { JSDOM } from "jsdom";
import { VALIDATION_CODES } from "../constants";

export interface LinkInfo {
  href: string;
  element: string;           // tag name: a, link, img, script, iframe, etc.
  attribute: string;         // href, src, etc.
  lineNumber?: number;
}

export interface HtmlValidationResult {
  links: LinkInfo[];
  scripts: string[];         // inline script content
  eventHandlers: string[];   // on* attributes
  forms: FormInfo[];
  iframes: IframeInfo[];
  errors: string[];
}

export interface FormInfo {
  action: string;
  method: string;
  inputs: InputInfo[];
}

export interface InputInfo {
  type: string;
  name: string;
}

export interface IframeInfo {
  src: string;
  sandbox?: string;
}

/**
 * Parse HTML/XHTML content and extract links, scripts, and security-relevant features
 */
export function parseHtmlContent(content: string, basePath: string): HtmlValidationResult {
  const result: HtmlValidationResult = {
    links: [],
    scripts: [],
    eventHandlers: [],
    forms: [],
    iframes: [],
    errors: [],
  };

  try {
    const dom = new JSDOM(content, {
      contentType: "application/xhtml+xml",
      url: `file://${basePath}`,
      pretendToBeVisual: true,
      resources: "usable",
      runScripts: "outside-only",
    });

    const document = dom.window.document;

    // Extract all links (a, link, area)
    const linkElements = document.querySelectorAll("a[href], link[href], area[href]");
    linkElements.forEach((el) => {
      const href = el.getAttribute("href")?.trim();
      if (href) {
        result.links.push({
          href,
          element: el.tagName.toLowerCase(),
          attribute: "href",
        });
      }
    });

    // Extract resource references (img, video, audio, source, embed, object)
    const resourceElements = document.querySelectorAll("img[src], video[src], audio[src], source[src], embed[src], object[data]");
    resourceElements.forEach((el) => {
      const src = el.getAttribute("src") || el.getAttribute("data");
      if (src) {
        result.links.push({
          href: src.trim(),
          element: el.tagName.toLowerCase(),
          attribute: el.hasAttribute("src") ? "src" : "data",
        });
      }
    });

    // Extract scripts
    const scripts = document.querySelectorAll("script");
    scripts.forEach((script) => {
      const src = script.getAttribute("src");
      if (src) {
        result.links.push({
          href: src.trim(),
          element: "script",
          attribute: "src",
        });
      } else if (script.textContent?.trim()) {
        result.scripts.push(script.textContent.trim());
      }
    });

    // Extract event handlers (on*)
    const allElements = document.querySelectorAll("*");
    allElements.forEach((el) => {
      Array.from(el.attributes).forEach((attr) => {
        if (attr.name.startsWith("on")) {
          result.eventHandlers.push(`${el.tagName.toLowerCase()}.${attr.name}="${attr.value}"`);
        }
      });
    });

    // Extract forms
    const forms = document.querySelectorAll("form");
    forms.forEach((form) => {
      const action = form.getAttribute("action")?.trim() || "";
      const method = form.getAttribute("method")?.trim().toUpperCase() || "GET";
      const inputs: InputInfo[] = [];
      form.querySelectorAll("input, textarea, select, button").forEach((input) => {
        inputs.push({
          type: input.getAttribute("type") || input.tagName.toLowerCase(),
          name: input.getAttribute("name") || "",
        });
      });
      result.forms.push({ action, method, inputs });
    });

    // Extract iframes
    const iframes = document.querySelectorAll("iframe");
    iframes.forEach((iframe) => {
      const src = iframe.getAttribute("src")?.trim() || "";
      const sandbox = iframe.getAttribute("sandbox")?.trim();
      result.iframes.push({ src, sandbox });
    });

  } catch (e) {
    result.errors.push(`${VALIDATION_CODES.GEN_MALFORMED_HTML}: ${e}`);
  }

  return result;
}

/**
 * Check if a URL is remote (http:, https:, //, data:, javascript:, etc.)
 */
export function isRemoteUrl(url: string): boolean {
  const trimmed = url.trim().toLowerCase();
  return (
    trimmed.startsWith("http:") ||
    trimmed.startsWith("https:") ||
    trimmed.startsWith("//") ||
    trimmed.startsWith("data:") ||
    trimmed.startsWith("javascript:") ||
    trimmed.startsWith("mailto:") ||
    trimmed.startsWith("tel:") ||
    trimmed.startsWith("ftp:")
  );
}

/**
 * Check if a path contains directory traversal sequences
 */
export function hasPathTraversal(path: string): boolean {
  // Normalize and check for .. or absolute paths
  const normalized = path.replace(/\\/g, "/");
  return normalized.includes("..") || normalized.startsWith("/");
}

/**
 * Resolve a relative path against a base path (both POSIX-style)
 */
export function resolveRelativePath(basePath: string, relativePath: string): string {
  const baseDir = basePath.substring(0, basePath.lastIndexOf("/") + 1);
  const parts = baseDir.split("/").filter(Boolean);
  const relParts = relativePath.split("/").filter(Boolean);
  
  for (const part of relParts) {
    if (part === "..") {
      parts.pop();
    } else if (part !== ".") {
      parts.push(part);
    }
  }
  
  return parts.join("/");
}

/**
 * Check if a path is within the EPUB content directory (no escape)
 */
export function isPathSafe(resolvedPath: string, contentRoot = "EPUB"): boolean {
  const normalized = resolvedPath.replace(/\\/g, "/");
  return normalized.startsWith(`${contentRoot}/`) || normalized === contentRoot;
}
```

---

## `src/utils/fs.ts`

```typescript
/**
 * File system utilities for reading/writing files
 */

import * as fs from "fs/promises";
import * as path from "path";

export async function readFileUtf8(filePath: string): Promise<string> {
  return fs.readFile(filePath, "utf-8");
}

export async function writeFileUtf8(filePath: string, content: string): Promise<void> {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, content, "utf-8");
}

export async function readFileBuffer(filePath: string): Promise<Buffer> {
  return fs.readFile(filePath);
}

export async function writeFileBuffer(filePath: string, content: Buffer): Promise<void> {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, content);
}

export async function fileExists(filePath: string): Promise<boolean> {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

export async function getFileStats(filePath: string): Promise<fs.Stats | null> {
  try {
    return await fs.stat(filePath);
  } catch {
    return null;
  }
}

export function posixPath(...segments: string[]): string {
  return segments.join("/").replace(/\/+/g, "/");
}

export function getMediaTypeFromExtension(filePath: string): string {
  const ext = path.extname(filePath).toLowerCase();
  const mediaTypes: Record<string, string> = {
    ".xhtml": "application/xhtml+xml",
    ".html": "application/xhtml+xml",
    ".xml": "application/xml",
    ".css": "text/css",
    ".js": "application/javascript",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".svg": "image/svg+xml",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
    ".ttf": "font/ttf",
    ".otf": "font/otf",
    ".mp3": "audio/mpeg",
    ".mp4": "video/mp4",
    ".webm": "video/webm",
    ".ncx": "application/x-dtbncx+xml",
    ".smil": "application/smil+xml",
    ".pls": "application/pls+xml",
  };
  return mediaTypes[ext] || "application/octet-stream";
}
```

---

## `src/builder/Mimetype.ts`

```typescript
/**
 * Mimetype file generator - must be first entry in ZIP, uncompressed
 */

import { MIMETYPE_CONTENT, MIMETYPE_FILENAME } from "../constants";

export interface MimetypeFile {
  filename: string;
  content: string;
  compressed: boolean;
}

export function createMimetypeFile(): MimetypeFile {
  return {
    filename: MIMETYPE_FILENAME,
    content: MIMETYPE_CONTENT,
    compressed: false,
  };
}

/**
 * Validate mimetype file content and properties
 */
export function validateMimetypeFile(
  filename: string,
  content: string,
  compressed: boolean
): { valid: boolean; errors: string[] } {
  const errors: string[] = [];
  
  if (filename !== MIMETYPE_FILENAME) {
    errors.push(`Mimetype file must be named "${MIMETYPE_FILENAME}", got "${filename}"`);
  }
  
  if (content.trim() !== MIMETYPE_CONTENT) {
    errors.push(`Mimetype content must be exactly "${MIMETYPE_CONTENT}", got "${content.trim()}"`);
  }
  
  if (compressed) {
    errors.push("Mimetype file must be uncompressed (compression method 0)");
  }
  
  return { valid: errors.length === 0, errors };
}
```

---

## `src/builder/Container.ts`

```typescript
/**
 * META-INF/container.xml generator
 */

import { serializeXml } from "../utils/xml";
import { CONTAINER_XML_PATH, CONTAINER_NAMESPACE } from "../constants";

export interface ContainerOptions {
  rootfilePath: string;        // e.g., "EPUB/package.opf"
  rootfileMediaType: string;   // "application/oebps-package+xml"
}

export function generateContainerXml(options: ContainerOptions): string {
  const container = {
    container: {
      "@_xmlns": CONTAINER_NAMESPACE,
      "@_version": "1.0",
      rootfiles: {
        rootfile: {
          "@_full-path": options.rootfilePath,
          "@_media-type": options.rootfileMediaType,
        },
      },
    },
  };
  
  return serializeXml(container);
}

export function getContainerPath(): string {
  return CONTAINER_XML_PATH;
}
```

---

## `src/builder/PackageDocument.ts`

```typescript
/**
 * package.opf (Package Document) generator
 * Per EPUB 3.3 specification
 */

import { serializeXml, nsAttr, nsElement } from "../utils/xml";
import {
  PACKAGE_NAMESPACE,
  PACKAGE_VERSION,
  PACKAGE_PREFIXES,
  DC_NAMESPACE,
  DCTERMS_NAMESPACE,
  OPF_NAMESPACE,
  XML_NAMESPACE,
  MEDIA_TYPES,
} from "../constants";
import { EpubMetadata, ManifestItem, SpineItem, GuideEntry } from "../types";

export interface PackageDocumentOptions {
  metadata: EpubMetadata;
  manifest: ManifestItem[];
  spine: SpineItem[];
  guide?: GuideEntry[];
  pageProgressionDirection?: "ltr" | "rtl" | "default";
  prefixes?: string;
}

function formatDateForDcTerms(date: string): string {
  // Ensure ISO 8601 format
  return new Date(date).toISOString().split("T")[0];
}

function buildMetadata(metadata: EpubMetadata): Record<string, unknown> {
  const meta: Record<string, unknown> = {
    "dc:identifier": {
      "@_id": "pub-id",
      "#text": metadata.identifier,
    },
    "dc:title": metadata.title,
    "dc:language": metadata.language,
  };

  if (metadata.author) {
    meta["dc:creator"] = {
      "@_id": "creator",
      "@_role": "aut",
      "#text": metadata.author,
    };
  }

  if (metadata.publisher) {
    meta["dc:publisher"] = metadata.publisher;
  }

  if (metadata.date) {
    meta["dc:date"] = {
      "@_id": "date",
      "#text": formatDateForDcTerms(metadata.date),
    };
  }

  if (metadata.modified) {
    meta["meta"] = meta["meta"] || [];
    const metas = meta["meta"] as Array<Record<string, unknown>>;
    metas.push({
      "@_property": "dcterms:modified",
      "#text": new Date(metadata.modified).toISOString(),
    });
  }

  if (metadata.description) {
    meta["dc:description"] = metadata.description;
  }

  if (metadata.subject && metadata.subject.length > 0) {
    meta["dc:subject"] = metadata.subject;
  }

  if (metadata.rights) {
    meta["dc:rights"] = metadata.rights;
  }

  if (metadata.coverImagePath) {
    meta["meta"] = meta["meta"] || [];
    const metas = meta["meta"] as Array<Record<string, unknown>>;
    metas.push({
      "@_name": "cover",
      "@_content": metadata.coverImagePath,
    });
  }

  return meta;
}

function buildManifest(manifest: ManifestItem[]): Record<string, unknown> {
  const items = manifest.map((item) => ({
    item: {
      "@_id": item.id,
      "@_href": item.href,
      "@_media-type": item.mediaType,
      ...(item.properties && { "@_properties": item.properties }),
      ...(item.fallback && { "@_fallback": item.fallback }),
    },
  }));
  
  return { item: items };
}

function buildSpine(spine: SpineItem[]): Record<string, unknown> {
  const itemrefs = spine.map((item) => ({
    itemref: {
      "@_idref": item.idref,
      ...(item.linear && { "@_linear": item.linear }),
      ...(item.properties && { "@_properties": item.properties }),
    },
  }));
  
  return { itemref: itemrefs };
}

function buildGuide(guide?: GuideEntry[]): Record<string, unknown> | undefined {
  if (!guide || guide.length === 0) return undefined;
  
  const references = guide.map((entry) => ({
    reference: {
      "@_type": entry.type,
      "@_title": entry.title,
      "@_href": entry.href,
    },
  }));
  
  return { reference: references };
}

export function generatePackageDocument(options: PackageDocumentOptions): string {
  const { metadata, manifest, spine, guide, pageProgressionDirection = "default", prefixes = PACKAGE_PREFIXES } = options;

  const packageDoc = {
    package: {
      "@_xmlns": PACKAGE_NAMESPACE,
      "@_xmlns:dc": DC_NAMESPACE,
      "@_xmlns:dcterms": DCTERMS_NAMESPACE,
      "@_xmlns:opf": OPF_NAMESPACE,
      "@_xmlns:xhtml": "http://www.w3.org/1999/xhtml",
      "@_xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
      "@_version": PACKAGE_VERSION,
      "@_unique-identifier": "pub-id",
      "@_prefix": prefixes,
      metadata: buildMetadata(metadata),
      manifest: buildManifest(manifest),
      spine: {
        "@_page-progression-direction": pageProgressionDirection,
        ...buildSpine(spine),
      },
      ...(guide && { guide: buildGuide(guide) }),
    },
  };

  return serializeXml(packageDoc);
}

export function getMediaTypeForPath(filePath: string): string {
  return MEDIA_TYPES[filePath.toLowerCase().match(/\.[^.]+$/)?.[0] || ""] || "application/octet-stream";
}
```

---

## `src/builder/NavigationDocument.ts`

```typescript
/**
 * nav.xhtml (EPUB Navigation Document) generator
 * Per EPUB 3.3 specification
 */

import { serializeXml } from "../utils/xml";
import { XHTML_NAMESPACE, NAV_DOC_PATH } from "../constants";
import { Chapter } from "../types";

export interface NavigationOptions {
  title: string;
  chapters: Chapter[];
  tocTitle?: string;
  landmarks?: Landmark[];
}

export interface Landmark {
  type: string;      // EPUB 3 landmark types: cover, toc, titlepage, etc.
  title: string;
  href: string;
}

function buildNavList(chapters: Chapter[], basePath = ""): Record<string, unknown> {
  const items = chapters.map((chapter) => ({
    li: {
      a: {
        "@_href": `${basePath}${chapter.contentPath}`,
        "#text": chapter.title,
      },
    },
  }));

  return {
    ol: {
      li: items,
    },
  };
}

function buildLandmarksNav(landmarks: Landmark[]): Record<string, unknown> {
  const items = landmarks.map((lm) => ({
    li: {
      a: {
        "@_href": lm.href,
        "#text": lm.title,
      },
    },
  }));

  return {
    nav: {
      "@_epub:type": "landmarks",
      h2: "Landmarks",
      ol: {
        li: items,
      },
    },
  };
}

export function generateNavigationDocument(options: NavigationOptions): string {
  const { title, chapters, tocTitle = "Table of Contents", landmarks = [] } = options;

  const navDoc = {
    html: {
      "@_xmlns": XHTML_NAMESPACE,
      "@_xmlns:epub": "http://www.idpf.org/2007/ops",
      head: {
        title,
        meta: {
          "@_charset": "utf-8",
        },
      },
      body: {
        nav: [
          {
            "@_epub:type": "toc",
            "@_id": "toc",
            h2: tocTitle,
            ...buildNavList(chapters),
          },
          ...(landmarks.length > 0 ? [buildLandmarksNav(landmarks)] : []),
        ],
      },
    },
  };

  return serializeXml(navDoc);
}

export function getNavigationPath(): string {
  return NAV_DOC_PATH;
}
```

---

## `src/builder/ZipWriter.ts`

```typescript
/**
 * ZIP archive writer with correct EPUB ordering:
 * 1. mimetype (uncompressed, first)
 * 2. META-INF/container.xml
 * 3. All other files (compressed)
 * Uses adm-zip for ZIP manipulation
 */

import * as AdmZip from "adm-zip";
import { MIMETYPE_FILENAME } from "../constants";
import { MimetypeFile } from "./Mimetype";

export interface ZipEntry {
  name: string;
  content: string | Buffer;
  compressed?: boolean;  // Default true, except mimetype
}

export class EpubZipWriter {
  private zip: AdmZip;
  private mimetypeWritten: boolean = false;
  private entries: Map<string, { compressed: boolean; size: number }> = new Map();

  constructor() {
    this.zip = new AdmZip();
  }

  /**
   * Add mimetype file - MUST be first and uncompressed
   */
  addMimetype(mimetype: MimetypeFile): void {
    if (this.mimetypeWritten) {
      throw new Error("Mimetype already written");
    }
    
    // adm-zip doesn't directly support uncompressed first entry,
    // so we'll build the ZIP manually in writeToBuffer()
    this.entries.set(mimetype.filename, {
      compressed: false,
      size: Buffer.byteLength(mimetype.content, "utf-8"),
    });
    this.mimetypeWritten = true;
  }

  /**
   * Add a file entry
   */
  addFile(name: string, content: string | Buffer, compressed: boolean = true): void {
    if (name === MIMETYPE_FILENAME) {
      throw new Error("Use addMimetype() for mimetype file");
    }
    
    const buffer = Buffer.isBuffer(content) ? content : Buffer.from(content, "utf-8");
    this.entries.set(name, {
      compressed,
      size: buffer.length,
    });
    // Store content in a temporary property for later writing
    (this.entries.get(name) as any).content = buffer;
  }

  /**
   * Write ZIP to buffer with correct EPUB ordering
   */
  writeToBuffer(): Buffer {
    if (!this.mimetypeWritten) {
      throw new Error("Mimetype file not added");
    }

    // Create new ZIP with correct ordering
    const finalZip = new AdmZip();

    // 1. Add mimetype FIRST, uncompressed
    const mimetypeEntry = this.entries.get(MIMETYPE_FILENAME)!;
    const mimetypeContent = (mimetypeEntry as any).content || Buffer.from("application/epub+zip");
    finalZip.addFile(MIMETYPE_FILENAME, mimetypeContent, "", 0); // 0 = store (no compression)

    // 2. Add META-INF/container.xml second
    const containerEntry = this.entries.get("META-INF/container.xml");
    if (containerEntry) {
      const content = (containerEntry as any).content;
      finalZip.addFile("META-INF/container.xml", content, "", containerEntry.compressed ? 8 : 0);
      this.entries.delete("META-INF/container.xml");
    }

    // 3. Add all other entries
    for (const [name, entry] of this.entries) {
      const content = (entry as any).content;
      finalZip.addFile(name, content, "", entry.compressed ? 8 : 0);
    }

    return finalZip.toBuffer();
  }

  /**
   * Write ZIP to file
   */
  async writeToFile(filePath: string): Promise<void> {
    const buffer = this.writeToBuffer();
    const { writeFileBuffer } = await import("../utils/fs");
    await writeFileBuffer(filePath, buffer);
  }

  /**
   * Get entry info for validation
   */
  getEntryInfo(): Array<{ name: string; compressed: boolean; size: number }> {
    const result: Array<{ name: string; compressed: boolean; size: number }> = [];
    for (const [name, entry] of this.entries) {
      result.push({ name, compressed: entry.compressed, size: entry.size });
    }
    return result;
  }
}
```

---

## `src/builder/EpubBuilder.ts`

```typescript
/**
 * Main EPUB 3 Builder - assembles all components into a conforming EPUB
 */

import { v4 as uuidv4 } from "uuid";
import { EpubZipWriter } from "./ZipWriter";
import { createMimetypeFile } from "./Mimetype";
import { generateContainerXml, getContainerPath } from "./Container";
import { generatePackageDocument, getMediaTypeForPath } from "./PackageDocument";
import { generateNavigationDocument, getNavigationPath } from "./NavigationDocument";
import { readFileBuffer, readFileUtf8, posixPath } from "../utils/fs";
import { EpubOptions, ManifestItem, SpineItem, Chapter } from "../types";
import { MEDIA_TYPES, CONTENT_DIR, PACKAGE_DOC_PATH, REQUIRED_MANIFEST_PROPERTIES } from "../constants";

export class EpubBuilder {
  private options: EpubOptions;
  private manifestItems: Map<string, ManifestItem> = new Map();
  private spineItems: SpineItem[] = [];
  private chapterMap: Map<string, Chapter> = new Map();

  constructor(options: EpubOptions) {
    this.options = options;
    this.initializeManifestAndSpine();
  }

  private initializeManifestAndSpine(): void {
    // Add user-provided manifest items
    for (const item of this.options.manifestItems) {
      this.manifestItems.set(item.id, item);
    }

    // Add user-provided spine items
    this.spineItems = [...this.options.spine];

    // Process chapters
    for (const chapter of this.options.chapters) {
      this.chapterMap.set(chapter.id, chapter);
      
      // Add to manifest if not already present
      if (!this.manifestItems.has(chapter.id)) {
        const mediaType = getMediaTypeForPath(chapter.contentPath);
        this.manifestItems.set(chapter.id, {
          id: chapter.id,
          href: chapter.contentPath,
          mediaType,
        });
      }

      // Add to spine if not already present
      if (!this.spineItems.some((s) => s.idref === chapter.id)) {
        this.spineItems.push({
          idref: chapter.id,
          linear: chapter.linear !== false ? "yes" : "no",
          properties: chapter.properties,
        });
      }
    }

    // Ensure navigation document is in manifest and spine
    this.ensureNavigationDocument();
    
    // Ensure cover image is marked
    if (this.options.metadata.coverImagePath) {
      this.markCoverImage(this.options.metadata.coverImagePath);
    }
  }

  private ensureNavigationDocument(): void {
    const navId = "nav";
    const navPath = getNavigationPath().replace(`${CONTENT_DIR}/`, "");
    
    if (!this.manifestItems.has(navId)) {
      this.manifestItems.set(navId, {
        id: navId,
        href: navPath,
        mediaType: "application/xhtml+xml",
        properties: REQUIRED_MANIFEST_PROPERTIES.NAV,
      });
    } else {
      // Update existing to ensure nav property
      const existing = this.manifestItems.get(navId)!;
      existing.properties = REQUIRED_MANIFEST_PROPERTIES.NAV;
      existing.mediaType = "application/xhtml+xml";
    }

    // Ensure nav is first in spine (EPUB 3 requirement)
    if (!this.spineItems.some((s) => s.idref === navId)) {
      this.spineItems.unshift({ idref: navId, linear: "no" });
    }
  }

  private markCoverImage(coverPath: string): void {
    // Find manifest item matching cover path
    for (const [id, item] of this.manifestItems) {
      if (item.href === coverPath || item.href.endsWith(coverPath)) {
        item.properties = REQUIRED_MANIFEST_PROPERTIES.COVER_IMAGE;
        break;
      }
    }
  }

  /**
   * Build the EPUB file
   */
  async build(): Promise<void> {
    const zip = new EpubZipWriter();

    // 1. Add mimetype (uncompressed, first)
    zip.addMimetype(createMimetypeFile());

    // 2. Add META-INF/container.xml
    const containerXml = generateContainerXml({
      rootfilePath: PACKAGE_DOC_PATH,
      rootfileMediaType: "application/oebps-package+xml",
    });
    zip.addFile(getContainerPath(), containerXml);

    // 3. Read and add all content files
    await this.addContentFiles(zip);

    // 4. Generate and add navigation document
    const navDoc = this.generateNavigationDocument();
    zip.addFile(getNavigationPath(), navDoc);

    // 5. Generate and add package document
    const packageDoc = this.generatePackageDocument();
    zip.addFile(PACKAGE_DOC_PATH, packageDoc);

    // 6. Write to output
    await zip.writeToFile(this.options.outputPath);
  }

  private async addContentFiles(zip: EpubZipWriter): Promise<void> {
    const contentFiles = new Set<string>();

    // Collect all referenced files from manifest
    for (const item of this.manifestItems.values()) {
      contentFiles.add(item.href);
    }

    // Add chapters content
    for (const chapter of this.options.chapters) {
      contentFiles.add(chapter.contentPath);
    }

    // Add CSS if provided
    if (this.options.cssPath) {
      contentFiles.add(this.options.cssPath);
    }

    // Add cover image if provided
    if (this.options.coverImagePath) {
      contentFiles.add(this.options.coverImagePath);
    }

    // Read and add each file
    for (const filePath of contentFiles) {
      const fullPath = posixPath(CONTENT_DIR, filePath);
      try {
        const buffer = await readFileBuffer(filePath);
        const compressed = !filePath.endsWith(".svg") && !filePath === "mimetype";
        zip.addFile(fullPath, buffer, compressed);
      } catch (e) {
        throw new Error(`Failed to read content file "${filePath}": ${e}`);
      }
    }
  }

  private generateNavigationDocument(): string {
    const landmarks = this.options.metadata.coverImagePath
      ? [{ type: "cover", title: "Cover", href: this.options.metadata.coverImagePath }]
      : [];

    return generateNavigationDocument({
      title: this.options.metadata.title,
      chapters: this.options.chapters,
      tocTitle: "Table of Contents",
      landmarks,
    });
  }

  private generatePackageDocument(): string {
    const manifest = Array.from(this.manifestItems.values());
    
    return generatePackageDocument({
      metadata: this.options.metadata,
      manifest,
      spine: this.spineItems,
      guide: this.buildGuide(),
    });
  }

  private buildGuide(): Array<{ type: string; title: string; href: string }> {
    const guide: Array<{ type: string; title: string; href: string }> = [];
    
    if (this.options.metadata.coverImagePath) {
      guide.push({
        type: "cover",
        title: "Cover",
        href: this.options.metadata.coverImagePath,
      });
    }
    
    // Add first chapter as titlepage if available
    if (this.options.chapters.length > 0) {
      guide.push({
        type: "titlepage",
        title: this.options.chapters[0].title,
        href: this.options.chapters[0].contentPath,
      });
    }
    
    return guide;
  }

  /**
   * Static factory for creating a builder with sensible defaults
   */
  static create(options: Partial<EpubOptions> & { 
    title: string; 
    identifier?: string;
    language?: string;
    author?: string;
    chapters: Chapter[];
    outputPath: string;
  }): EpubBuilder {
    const identifier = options.identifier || `urn:uuid:${uuidv4()}`;
    const language = options.language || "en";
    
    const fullOptions: EpubOptions = {
      metadata: {
        identifier,
        title: options.title,
        language,
        author: options.author,
        publisher: options.metadata?.publisher,
        date: options.metadata?.date,
        modified: options.metadata?.modified || new Date().toISOString(),
        description: options.metadata?.description,
        subject: options.metadata?.subject,
        rights: options.metadata?.rights,
        coverImagePath: options.metadata?.coverImagePath,
      },
      chapters: options.chapters,
      manifestItems: options.manifestItems || [],
      spine: options.spine || [],
      coverImagePath: options.coverImagePath,
      cssPath: options.cssPath,
      outputPath: options.outputPath,
    };

    return new EpubBuilder(fullOptions);
  }
}
```

---

## `src/builder/index.ts`

```typescript
/**
 * Builder module exports
 */

export * from "./EpubBuilder";
export * from "./PackageDocument";
export * from "./NavigationDocument";
export * from "./Container";
export * from "./Mimetype";
export * from "./ZipWriter";
```

---

## `src/validator/Report.ts`

```typescript
/**
 * Validation report types and helpers
 */

import { ValidationResult, ValidationError, ValidationWarning, ValidationInfo } from "../types";

export class ValidationReport implements ValidationResult {
  public errors: ValidationError[] = [];
  public warnings: ValidationWarning[] = [];
  public info: ValidationInfo[] = [];

  get valid(): boolean {
    return this.errors.length === 0;
  }

  addError(code: string, message: string, location?: string): void {
    this.errors.push({ code, message, location, severity: "error" });
  }

  addWarning(code: string, message: string, location?: string): void {
    this.warnings.push({ code, message, location, severity: "warning" });
  }

  addInfo(code: string, message: string, location?: string): void {
    this.info.push({ code, message, location, severity: "info" });
  }

  merge(other: ValidationReport): void {
    this.errors.push(...other.errors);
    this.warnings.push(...other.warnings);
    this.info.push(...other.info);
  }

  toJSON(): ValidationResult {
    return {
      valid: this.valid,
      errors: this.errors,
      warnings: this.warnings,
      info: this.info,
    };
  }

  toString(verbose = false): string {
    const lines: string[] = [];
    lines.push(`Validation Result: ${this.valid ? "VALID" : "INVALID"}`);
    lines.push(`Errors: ${this.errors.length}, Warnings: ${this.warnings.length}, Info: ${this.info.length}`);
    lines.push("");

    if (this.errors.length > 0) {
      lines.push("=== ERRORS ===");
      for (const err of this.errors) {
        lines.push(`[${err.code}] ${err.message}${err.location ? ` @ ${err.location}` : ""}`);
      }
      lines.push("");
    }

    if (this.warnings.length > 0) {
      lines.push("=== WARNINGS ===");
      for (const warn of this.warnings) {
        lines.push(`[${warn.code}] ${warn.message}${warn.location ? ` @ ${warn.location}` : ""}`);
      }
      lines.push("");
    }

    if (verbose && this.info.length > 0) {
      lines.push("=== INFO ===");
      for (const info of this.info) {
        lines.push(`[${info.code}] ${info.message}${info.location ? ` @ ${info.location}` : ""}`);
      }
    }

    return lines.join("\n");
  }
}
```

---

## `src/validator/ZipValidator.ts`

```typescript
/**
 * ZIP structure validation: ordering, compression, required files
 */

import * as AdmZip from "adm-zip";
import { ValidationReport } from "./Report";
import { 
  MIMETYPE_FILENAME, 
  CONTAINER_XML_PATH, 
  PACKAGE_DOC_PATH,
  EPUB_MEDIA_TYPE,
  VALIDATION_CODES,
} from "../constants";

export class ZipValidator {
  private zip: AdmZip;
  private report: ValidationReport;
  private entries: AdmZip.IZipEntry[];

  constructor(zipBuffer: Buffer) {
    this.zip = new AdmZip(zipBuffer);
    this.entries = this.zip.getEntries();
    this.report = new ValidationReport();
  }

  validate(): ValidationReport {
    this.checkMimetypeFirst();
    this.checkMimetypeUncompressed();
    this.checkMimetypeContent();
    this.checkRequiredFiles();
    this.checkPathTraversal();
    this.checkDuplicateEntries();
    return this.report;
  }

  private checkMimetypeFirst(): void {
    if (this.entries.length === 0) {
      this.report.addError(VALIDATION_CODES.ZIP_MIMETYPE_NOT_FIRST, "ZIP archive is empty");
      return;
    }

    const firstEntry = this.entries[0];
    if (firstEntry.entryName !== MIMETYPE_FILENAME) {
      this.report.addError(
        VALIDATION_CODES.ZIP_MIMETYPE_NOT_FIRST,
        `First entry must be "${MIMETYPE_FILENAME}", found "${firstEntry.entryName}"`,
        firstEntry.entryName
      );
    }
  }

  private checkMimetypeUncompressed(): void {
    const mimetypeEntry = this.entries.find((e) => e.entryName === MIMETYPE_FILENAME);
    if (mimetypeEntry) {
      // Compression method 0 = store (uncompressed), 8 = deflate
      if (mimetypeEntry.method !== 0) {
        this.report.addError(
          VALIDATION_CODES.ZIP_MIMETYPE_COMPRESSED,
          `Mimetype entry must be uncompressed (method 0), got method ${mimetypeEntry.method}`,
          MIMETYPE_FILENAME
        );
      }
    }
  }

  private checkMimetypeContent(): void {
    const mimetypeEntry = this.entries.find((e) => e.entryName === MIMETYPE_FILENAME);
    if (mimetypeEntry) {
      const content = mimetypeEntry.getData().toString("utf-8").trim();
      if (content !== EPUB_MEDIA_TYPE) {
        this.report.addError(
          VALIDATION_CODES.ZIP_MIMETYPE_WRONG_CONTENT,
          `Mimetype content must be "${EPUB_MEDIA_TYPE}", got "${content}"`,
          MIMETYPE_FILENAME
        );
      }
    }
  }

  private checkRequiredFiles(): void {
    const entryNames = new Set(this.entries.map((e) => e.entryName));
    
    if (!entryNames.has(CONTAINER_XML_PATH)) {
      this.report.addError(
        VALIDATION_CODES.ZIP_MISSING_CONTAINER,
        `Missing required file: ${CONTAINER_XML_PATH}`,
        CONTAINER_XML_PATH
      );
    }

    // Package document checked by PackageValidator, but we can note it here
    let hasPackage = false;
    for (const name of entryNames) {
      if (name.endsWith(".opf") || name === PACKAGE_DOC_PATH) {
        hasPackage = true;
        break;
      }
    }
    if (!hasPackage) {
      this.report.addError(
        VALIDATION_CODES.ZIP_MISSING_PACKAGE,
        "Missing package document (.opf file)",
        PACKAGE_DOC_PATH
      );
    }
  }

  private checkPathTraversal(): void {
    for (const entry of this.entries) {
      const name = entry.entryName;
      // Check for directory traversal in ZIP entry names
      if (name.includes("..") || name.startsWith("/") || name.startsWith("\\")) {
        this.report.addError(
          VALIDATION_CODES.ZIP_TRAVERSAL_PATH,
          `ZIP entry contains path traversal or absolute path: ${name}`,
          name
        );
      }
      // Check for null bytes (ZIP slip)
      if (name.includes("\0")) {
        this.report.addError(
          VALIDATION_CODES.ZIP_TRAVERSAL_PATH,
          `ZIP entry contains null byte: ${name}`,
          name
        );
      }
    }
  }

  private checkDuplicateEntries(): void {
    const seen = new Map<string, number>();
    for (const entry of this.entries) {
      const count = seen.get(entry.entryName) || 0;
      seen.set(entry.entryName, count + 1);
    }
    
    for (const [name, count] of seen) {
      if (count > 1) {
        this.report.addError(
          VALIDATION_CODES.PKG_DUPLICATE_ID,
          `Duplicate ZIP entry: ${name} (appears ${count} times)`,
          name
        );
      }
    }
  }

  getEntry(name: string): AdmZip.IZipEntry | undefined {
    return this.entries.find((e) => e.entryName === name);
  }

  getEntryContent(name: string): Buffer | null {
    const entry = this.getEntry(name);
    return entry ? entry.getData() : null;
  }

  getEntryContentUtf8(name: string): string | null {
    const buffer = this.getEntryContent(name);
    return buffer ? buffer.toString("utf-8") : null;
  }

  listEntries(): Array<{ name: string; compressed: boolean; size: number }> {
    return this.entries.map((e) => ({
      name: e.entryName,
      compressed: e.method === 8,
      size: e.header.size,
    }));
  }
}
```

---

## `src/validator/PackageValidator.ts`

```typescript
/**
 * Package document (package.opf) validation
 */

import { parseXml, validateRootNamespaces } from "../utils/xml";
import { ValidationReport } from "./Report";
import { 
  PACKAGE_NAMESPACE, 
  DC_NAMESPACE, 
  OPF_NAMESPACE,
  PACKAGE_REQUIRED_ELEMENTS,
  METADATA_REQUIRED_FIELDS,
  SPINE_MIN_ITEMS,
  REQUIRED_MANIFEST_PROPERTIES,
  MEDIA_TYPES,
  VALIDATION_CODES,
} from "../constants";

export interface PackageDoc {
  metadata: Record<string, unknown>;
  manifest: ManifestItem[];
  spine: SpineItem[];
  guide?: GuideEntry[];
  uniqueIdentifier: string;
  version: string;
  prefixes: string;
}

export interface ManifestItem {
  id: string;
  href: string;
  mediaType: string;
  properties?: string;
  fallback?: string;
}

export interface SpineItem {
  idref: string;
  linear?: string;
  properties?: string;
}

export interface GuideEntry {
  type: string;
  title: string;
  href: string;
}

export class PackageValidator {
  private report: ValidationReport;
  private packageDoc: PackageDoc | null = null;
  private packagePath: string;
  private contentRoot: string;

  constructor(packageXml: string, packagePath: string = "EPUB/package.opf", contentRoot = "EPUB") {
    this.report = new ValidationReport();
    this.packagePath = packagePath;
    this.contentRoot = contentRoot;
    this.parsePackage(packageXml);
  }

  private parsePackage(xml: string): void {
    try {
      // Validate root namespaces
      const nsValidation = validateRootNamespaces(xml, {
        "": PACKAGE_NAMESPACE,
        dc: DC_NAMESPACE,
        opf: OPF_NAMESPACE,
      }, this.packagePath);
      
      if (!nsValidation.valid) {
        this.report.errors.push(...nsValidation.errors.map((e) => ({
          code: VALIDATION_CODES.PKG_INVALID_XMLNS,
          message: e,
          location: this.packagePath,
          severity: "error" as const,
        })));
      }

      const parsed = parseXml(xml);
      const pkg = parsed.package as Record<string, unknown>;
      
      if (!pkg) {
        this.report.addError(VALIDATION_CODES.GEN_MALFORMED_XML, "No <package> root element", this.packagePath);
        return;
      }

      this.packageDoc = {
        metadata: (pkg.metadata as Record<string, unknown>) || {},
        manifest: this.parseManifest(pkg.manifest),
        spine: this.parseSpine(pkg.spine),
        guide: this.parseGuide(pkg.guide),
        uniqueIdentifier: pkg["@_unique-identifier"] as string || "",
        version: pkg["@_version"] as string || "3.0",
        prefixes: pkg["@_prefix"] as string || "",
      };
    } catch (e) {
      this.report.addError(VALIDATION_CODES.GEN_MALFORMED_XML, `Failed to parse package document: ${e}`, this.packagePath);
    }
  }

  private parseManifest(manifest: unknown): ManifestItem[] {
    if (!manifest) return [];
    const m = manifest as Record<string, unknown>;
    const items = m.item;
    if (!items) return [];
    const arr = Array.isArray(items) ? items : [items];
    return arr.map((item: any) => ({
      id: item["@_id"],
      href: item["@_href"],
      mediaType: item["@_media-type"],
      properties: item["@_properties"],
      fallback: item["@_fallback"],
    }));
  }

  private parseSpine(spine: unknown): SpineItem[] {
    if (!spine) return [];
    const s = spine as Record<string, unknown>;
    const itemrefs = s.itemref;
    if (!itemrefs) return [];
    const arr = Array.isArray(itemrefs) ? itemrefs : [itemrefs];
    return arr.map((item: any) => ({
      idref: item["@_idref"],
      linear: item["@_linear"],
      properties: item["@_properties"],
    }));
  }

  private parseGuide(guide: unknown): GuideEntry[] {
    if (!guide) return [];
    const g = guide as Record<string, unknown>;
    const refs = g.reference;
    if (!refs) return [];
    const arr = Array.isArray(refs) ? refs : [refs];
    return arr.map((ref: any) => ({
      type: ref["@_type"],
      title: ref["@_title"],
      href: ref["@_href"],
    }));
  }

  validate(): ValidationReport {
    if (!this.packageDoc) return this.report;

    this.validateRequiredElements();
    this.validateMetadata();
    this.validateManifest();
    this.validateSpine();
    this.validateCrossReferences();
    this.validateUniqueIdentifier();
    this.validateMediaTypes();
    this.validateNavProperty();

    return this.report;
  }

  private validateRequiredElements(): void {
    if (!this.packageDoc!.metadata) {
      this.report.addError(VALIDATION_CODES.PKG_MISSING_METADATA, "Missing <metadata> element", this.packagePath);
    }
    if (!this.packageDoc!.manifest || this.packageDoc!.manifest.length === 0) {
      this.report.addError(VALIDATION_CODES.PKG_MISSING_MANIFEST, "Missing or empty <manifest>", this.packagePath);
    }
    if (!this.packageDoc!.spine || this.packageDoc!.spine.length === 0) {
      this.report.addError(VALIDATION_CODES.PKG_MISSING_SPINE, "Missing or empty <spine>", this.packagePath);
    }
  }

  private validateMetadata(): void {
    const meta = this.packageDoc!.metadata;
    
    for (const field of METADATA_REQUIRED_FIELDS) {
      const dcField = `dc:${field}`;
      const opfField = `opf:${field}`;
      if (!meta[dcField] && !meta[opfField]) {
        this.report.addError(
          VALIDATION_CODES.PKG_MISSING_REQUIRED_METADATA,
          `Missing required metadata field: ${field}`,
          this.packagePath
        );
      }
    }

    // Check identifier uniqueness
    const identifiers = this.extractIdentifiers(meta);
    if (identifiers.length === 0) {
      this.report.addError(VALIDATION_CODES.PKG_MISSING_REQUIRED_METADATA, "No dc:identifier found", this.packagePath);
    }
    
    const uniqueId = this.packageDoc!.uniqueIdentifier;
    const matchingIds = identifiers.filter((id) => id.id === uniqueId);
    if (matchingIds.length === 0 && uniqueId) {
      this.report.addError(
        VALIDATION_CODES.PKG_IDENTIFIER_NOT_UNIQUE,
        `Unique identifier "${uniqueId}" not found in metadata identifiers`,
        this.packagePath
      );
    }
  }

  private extractIdentifiers(metadata: Record<string, unknown>): Array<{ id: string; value: string }> {
    const ids: Array<{ id: string; value: string }> = [];
    const dcIdents = metadata["dc:identifier"];
    if (dcIdents) {
      const arr = Array.isArray(dcIdents) ? dcIdents : [dcIdents];
      for (const ident of arr) {
        if (typeof ident === "object" && ident !== null) {
          const obj = ident as Record<string, unknown>;
          ids.push({
            id: (obj["@_id"] as string) || "",
            value: (obj["#text"] as string) || "",
          });
        } else {
          ids.push({ id: "", value: ident as string });
        }
      }
    }
    return ids;
  }

  private validateManifest(): void {
    const manifest = this.packageDoc!.manifest;
    const ids = new Set<string>();
    const hrefs = new Set<string>();

    for (const item of manifest) {
      // Check duplicate IDs
      if (ids.has(item.id)) {
        this.report.addError(
          VALIDATION_CODES.PKG_DUPLICATE_ID,
          `Duplicate manifest item ID: ${item.id}`,
          `${this.packagePath}#manifest/item[@id='${item.id}']`
        );
      }
      ids.add(item.id);

      // Check duplicate hrefs
      if (hrefs.has(item.href)) {
        this.report.addWarning(
          VALIDATION_CODES.PKG_DUPLICATE_ID,
          `Duplicate manifest href: ${item.href}`,
          `${this.packagePath}#manifest/item[@href='${item.href}']`
        );
      }
      hrefs.add(item.href);

      // Validate media type
      if (!this.isValidMediaType(item.mediaType)) {
        this.report.addError(
          VALIDATION_CODES.PKG_INVALID_MEDIA_TYPE,
          `Invalid or unrecognized media type: ${item.mediaType} for item ${item.id}`,
          `${this.packagePath}#manifest/item[@id='${item.id}']`
        );
      }

      // Check path traversal in href
      if (item.href.includes("..") || item.href.startsWith("/")) {
        this.report.addError(
          VALIDATION_CODES.SEC_PATH_TRAVERSAL,
          `Manifest href contains path traversal: ${item.href}`,
          `${this.packagePath}#manifest/item[@id='${item.id}']`
        );
      }
    }
  }

  private isValidMediaType(mediaType: string): boolean {
    // Check against known EPUB media types
    const knownTypes = Object.values(MEDIA_TYPES);
    knownTypes.push(
      "application/oebps-package+xml",
      "application/xhtml+xml",
      "application/xml",
      "text/css",
      "application/javascript",
      "application/x-dtbncx+xml",
      "application/smil+xml",
      "application/pls+xml"
    );
    return knownTypes.includes(mediaType);
  }

  private validateSpine(): void {
    const spine = this.packageDoc!.spine;
    
    if (spine.length < SPINE_MIN_ITEMS) {
      this.report.addError(
        VALIDATION_CODES.PKG_SPINE_REF_MISSING,
        `Spine must have at least ${SPINE_MIN_ITEMS} itemref(s)`,
        this.packagePath
      );
    }

    const manifestIds = new Set(this.packageDoc!.manifest.map((m) => m.id));
    
    for (const item of spine) {
      if (!manifestIds.has(item.idref)) {
        this.report.addError(
          VALIDATION_CODES.PKG_SPINE_REF_MISSING,
          `Spine references missing manifest item: ${item.idref}`,
          `${this.packagePath}#spine/itemref[@idref='${item.idref}']`
        );
      }
    }
  }

  private validateCrossReferences(): void {
    const manifestIds = new Set(this.packageDoc!.manifest.map((m) => m.id));
    const spineIds = new Set(this.packageDoc!.spine.map((s) => s.idref));
    
    // Check for unreferenced manifest items (except nav, cover-image)
    for (const item of this.packageDoc!.manifest) {
      if (!spineIds.has(item.id) && item.id !== "ncx" && item.id !== "nav") {
        const props = item.properties || "";
        if (!props.includes(REQUIRED_MANIFEST_PROPERTIES.NAV) && 
            !props.includes(REQUIRED_MANIFEST_PROPERTIES.COVER_IMAGE)) {
          this.report.addWarning(
            VALIDATION_CODES.PKG_UNREFERENCED_MANIFEST_ITEM,
            `Manifest item not referenced in spine: ${item.id} (${item.href})`,
            `${this.packagePath}#manifest/item[@id='${item.id}']`
          );
        }
      }
    }
  }

  private validateUniqueIdentifier(): void {
    const uniqueId = this.packageDoc!.uniqueIdentifier;
    if (!uniqueId) {
      this.report.addError(
        VALIDATION_CODE

