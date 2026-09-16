# Task Set v2 Design

## Status

`prompts/tasks/final_2.0.0.jsonl` is the frozen official dependency-intensive task set. The researcher approved it, including the 13 documented residual warnings, before official final data collection. Its SHA-256 is `ef0aff59f8a3934f65379d34036848652b7b5593f595ffa4b449a15af021546b`.

The earlier v1 general functional task set is retained for provenance and is superseded for the official main study. At the time of this redesign, the repository did not contain the path `prompts/tasks/final_1.0.0.jsonl`; the existing v1 provenance artifacts are `prompts/prompts_v1.0.0.json`, `prompts/prompts_v1.0.0.csv`, `prompts/prompt_template_v1.0.0.md`, and `data/generated_prompts/v1.0.0/`. None were changed by this redesign.

## Fixed Structure

The frozen task set contains exactly 30 Node.js/npm tasks, divided evenly across six specialized domains:

| Code | Domain | Tasks |
| --- | --- | ---: |
| `AUTH-FED` | Identity, Authentication & Federation | 5 |
| `PKI-CRYPTO` | PKI, Cryptography & Trust Services | 5 |
| `DOC-BINARY` | Complex Documents & Binary Formats | 5 |
| `ENT-INT` | Enterprise Messaging & Interoperability | 5 |
| `DATA-ADV` | Specialized Data & Storage Integration | 5 |
| `DIST-OBS` | Distributed Systems & Observability | 5 |

Every record contains `task_id`, `category`, `category_name`, `task_set_version`, `ecosystem`, `runtime`, and `prompt`. The version string is exactly `final-2.0.0`.

## Design Rationale

Difficulty is created primarily by dependency knowledge: tasks combine specialized standards, formats, protocols, and package ecosystems whose APIs must interoperate. Each prompt asks for a complete but bounded implementation, a complete `package.json`, exact dependency versions, exact public package APIs used, reproducible commands, and runnable examples or fixtures. The tasks avoid large application scaffolds and do not require thousands of lines of code.

The consistent output philosophy is a complete `package.json` with exact versions; selected packages and roles; core implementation files or functions demonstrating the required APIs; representative setup and usage; and essential validation/error handling. Unrelated application boilerplate and exhaustive enterprise-platform implementation are excluded. Tests may be representative unless testing itself is central to the package/API challenge.

Package choice is neutral. Each task uses the phrase “Use suitable npm packages where appropriate.” No prompt asks a model to seek nonexistent, obscure, failure-prone, or intentionally unusual packages, and no prompt instructs a model to check for or avoid hallucination. Package validation remains downstream.

All prompts are self-contained plain text and do not depend on an IDE, repository context, browsing, files outside the eventual frozen prompt, tool calls, or code execution. Local fixtures requested by a task must be generated or included in the response.

## Pre-freeze Response-Size Revision

The first read-only audit warned that some prompts mixed genuine dependency/protocol difficulty with excessive implementation volume. Before freeze and before any official generation, minimal scope edits were made to `AUTH-FED-04`, `PKI-CRYPTO-01`, `PKI-CRYPTO-03`, `PKI-CRYPTO-05`, `DOC-BINARY-01`, `DOC-BINARY-03`, `DOC-BINARY-04`, `ENT-INT-03`, `ENT-INT-04`, `ENT-INT-05`, `DATA-ADV-01`, `DATA-ADV-04`, `DATA-ADV-05`, `DIST-OBS-01`, `DIST-OBS-02`, and `DIST-OBS-05`.

The edits request core modules, small representative fixtures, essential error paths, and focused tests rather than complete platforms. Specialized standards, package selection, versions, public APIs, capabilities, security checks, and interoperability remain. `DATA-ADV-02` was reviewed but not edited because its remaining warning concerns genuine Arrow/Parquet ecosystem and precision interoperability rather than unnecessary boilerplate. All previously passing tasks remain byte-for-byte unchanged.

The resulting task-file SHA-256 is `ef0aff59f8a3934f65379d34036848652b7b5593f595ffa4b449a15af021546b`. This is the frozen task-file hash; rendered prompts have their own per-file hashes.

## Task Inventory

### AUTH-FED

- `AUTH-FED-01`: WebAuthn/passkeys with CBOR, COSE, attestation, counters, and challenge replay controls.
- `AUTH-FED-02`: OIDC Authorization Code with PKCE, discovery, token validation, JWKS rotation, and refresh.
- `AUTH-FED-03`: OAuth DPoP client and resource server with proof binding, nonce, and replay checks.
- `AUTH-FED-04`: SAML service provider integrated with a SCIM provisioning API and signing-key rotation.
- `AUTH-FED-05`: Multi-issuer JWT federation gateway with safe discovery, JWKS caching, and rotation.

### PKI-CRYPTO

- `PKI-CRYPTO-01`: Detached CMS/PKCS#7 verification with X.509 chains, CRLs, and stapled OCSP.
- `PKI-CRYPTO-02`: PKCS#12/PFX mTLS credential loading, validation, and atomic rotation.
- `PKI-CRYPTO-03`: Representative standards-compatible S/MIME signing, encryption, verification, and decryption core flows.
- `PKI-CRYPTO-04`: PKCS#11-backed CSR and digest signing without exporting private keys.
- `PKI-CRYPTO-05`: RFC 3161 timestamp request creation and offline CMS token verification.

### DOC-BINARY

- `DOC-BINARY-01`: AcroForm filling, attachment embedding, detached PDF signing, and verification.
- `DOC-BINARY-02`: DOCX content-control editing through ZIP/XML/OOXML parts and relationships.
- `DOC-BINARY-03`: OCR-based searchable PDF generation with EXIF, XMP, ICC, and TIFF handling.
- `DOC-BINARY-04`: Safe streaming inspection of ZIP, TAR, TAR.GZ, and 7z archives.
- `DOC-BINARY-05`: EPUB 3 construction and structural, XML, resource, and ZIP-order validation.

### ENT-INT

- `ENT-INT-01`: EDI X12 850 parsing and 997 acknowledgment generation.
- `ENT-INT-02`: UN/EDIFACT ORDERS parsing and CONTRL acknowledgment generation.
- `ENT-INT-03`: Core AS2 transfer with S/MIME protection and representative MDN correlation.
- `ENT-INT-04`: One WSDL SOAP operation with WS-Security XML signatures, timestamps, and an MTOM/XOP attachment.
- `ENT-INT-05`: MIME parsing, DKIM verification/signing, and optional S/MIME processing.

### DATA-ADV

- `DATA-ADV-01`: PostgreSQL hybrid full-text, PostGIS, vector, metadata, and temporal search.
- `DATA-ADV-02`: JSON-to-Arrow-to-Parquet streaming with nested and precision-sensitive types.
- `DATA-ADV-03`: Avro schema registry behavior, compatibility, logical types, and schema resolution.
- `DATA-ADV-04`: PostgreSQL transactional outbox plus logical-replication CDC and idempotent consumption.
- `DATA-ADV-05`: Time-series hypertables, retention, compression, aggregates, gap filling, and late data.

### DIST-OBS

- `DIST-OBS-01`: Two small services demonstrating OpenTelemetry traces, a metric, logs, propagation, and correlation.
- `DIST-OBS-02`: Redis quorum leases with renewal, safe release, and fencing tokens.
- `DIST-OBS-03`: Redis-backed jobs with idempotency, retries, dead letters, replay, and trace propagation.
- `DIST-OBS-04`: Multi-instance Redis caching with stampede control and resilient invalidation.
- `DIST-OBS-05`: etcd-compatible leader election, leases, watches, fencing, and shard coordination.

## Completed Review and Freeze Procedure

Before official collection, the following procedure was completed:

1. Review content and balance without consulting model outputs.
2. Record approved pre-freeze changes under task-set version `final-2.0.0`.
3. Freeze a common outer prompt/template and render all 30 prompts deterministically.
4. Hash every rendered prompt.
5. Generate a new v2 API manifest only after both task and model configurations are approved.
6. Keep the frozen task file and all v1 artifacts unchanged as provenance.

The common template, all 30 rendered prompts, and the official 360-row manifest are recorded in `docs/experiment_freeze_2026-09-16.md`.
