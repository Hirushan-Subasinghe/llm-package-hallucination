# Chapter 3 Block 2 Verification

## 1. Verification Scope

This verification reviewed Sections 3.5--3.9 of `docs/report_drafts/chapter3_sections_3_5_to_3_9.md` against the frozen v2.6 model configuration, experiment freeze, manifest, collection and recovery scripts, response-inventory, extraction, validation, classification, adjudication, and analysis builders; their schemas and focused tests; D033--D038; the required status, progress, notes, analysis, reconciliation, and Block 1 records. It is a methodology verification only. No frozen input, raw observation, collection state, result, or final empirical claim was changed.

## 2. Overall Verdict

**PASS_WITH_CORRECTIONS.** The revised block is consistent with the implemented v2.6 methodology and the controlling decisions. Five evidence-backed wording corrections were required. No final-result or obsolete-methodology leakage was found.

## 3. Issues Found

| ID | Area | Finding |
| --- | --- | --- |
| B2-01 | API attempt preservation | The draft said every attempt retained an HTTP response and headers. Transport failures have retry-history records but no HTTP response artefact. |
| B2-02 | API retries | The draft did not distinguish three retries from four maximum attempts. |
| B2-03 | Truncation terminology | “Right-censored” asserted a statistical-censoring term not used by the primary methodology. |
| B2-04 | PIPE-03 JSON parsing | The extractor parses identified dependency objects, not necessarily an entire `package.json` document. |
| B2-05 | PIPE-04 retries | The draft omitted the implemented 0.5/1.0-second retry waits, three-attempt maximum, five-second `Retry-After` ceiling, and 0.25-second inter-query interval. |

## 4. Required Corrections

The target draft now states that HTTP bodies and selected safe headers are retained for HTTP attempts, while transport failures are retained in retry history; defines the initial request plus at most three retries; uses neutral truncation wording; narrows the JSON-parsing claim to dependency objects; and gives the exact PIPE-04 retry and interval behaviour.

The following reviewed claims were retained without correction: M1--M4 identifiers, providers, per-condition ceilings, OpenRouter `require_parameters`, no-fallback routing, M2 Darkbloom-only routing, temperature 0.6, top-p 0.95, `not_controlled` seed, one user message, no previous context, no tools, no browsing/retrieval/execution, the planned 180 API/180 Manual assignment without randomisation, manifest-order sequential API collection, zero artificial pacing, hash checks, overwrite prevention, M2 mismatch failure, D035, and D038.

## 5. Retry-Semantics Verification

API collection used an initial request plus at most three infrastructure retries, hence at most four attempts. Retryable events were transport failures, HTTP 429, and HTTP 5xx; the configured retry waits were 2, 5, and 10 seconds. A valid HTTP-429 `Retry-After` value could increase the applicable wait. Content did not cause a retry, and no model, provider, or route substitution occurred.

PIPE-04 is separate: it allowed at most two retries, hence at most three attempts, only for rate limiting, server error, or transport failure. Its configured waits were 0.5 and 1.0 seconds. A valid registry `Retry-After` was accepted only up to five seconds; invalid or longer values ended in `unresolved`. A 0.25-second interval separated distinct live registry requests.

## 6. Eligibility and Denominator Verification

`COMPLETED` requires a valid assistant response with `finish_reason == "stop"`; empty stop content fails validation. `TRUNCATED` is `finish_reason == "length"`, including an empty visible response, and is excluded from primary and secondary metric eligibility. Other API finish reasons, including `error`, `content_filter`, `tool_calls`, and a null finish reason, are failed under D035 even if content was preserved. The inventory overlay applies to completed/truncated API metadata that contain an abnormal `finish_reason`; records with no `finish_reason` field are outside that overlay.

PIPE-07 sets `metric_eligible` only when inventory `collection_status == "completed"`. This eligibility is inherited by package rows. Failed responses are not extracted, and PIPE-07 rejects stale package rows for failed runs. Completed zero-package responses remain in the primary SHR denominator and are non-hallucination responses.

**PHR denominator wording verified: YES.** D033 and D037 explicitly retain all metric-eligible unique `(run_id, normalized_package)` rows in the primary PHR denominator. Therefore unadjudicated `REVIEW_REQUIRED` rows and PIPE-05B `UNRESOLVED` rows remain outside the numerator but inside that denominator. `external_dependency_eligible` true/false/null changes only the D036 secondary DFR/RDFR resolution: false is `NOT_EXTERNAL`, null is `UNDETERMINED`, and neither changes primary PHR eligibility or denominator membership.

## 7. PIPE-03 Verification

PIPE-03 is `pipe-03-package-reference-extractor-1.0.2`. It supports literal static ESM imports, including type-only, side-effect, and multiline forms; literal `require(...)` and dynamic `import(...)`; own-line `npm install`/`npm i` commands; and string-valued entries in parsable dependency objects. It excludes narrative-only references, non-literal forms, re-exports, `require.resolve`, other package-manager commands, and transitive dependencies. Install parsing discards options and stops at `&&`, `||`, `;`, or `|`.

Normalisation reduces unscoped and scoped subpaths to npm roots, preserves an explicit version specifier as provenance, and excludes built-ins, `node:`, relative, absolute, home-directory, `file:`, HTTP(S), npm-alias, and malformed references. Occurrence records preserve original reference, normalised package, source type/text/offset, version specifier, occurrence index, and extractor version. The package-level unit is unique `(run_id, normalized_package)`; occurrence and unique views have the stated distinct roles.

## 8. PIPE-04 Verification

PIPE-04 is `pipe-04-npm-validator-1.0.0`. It makes read-only GET requests to the official npm registry, disables redirects, percent-encodes the full scoped name, queries each distinct normalised name, and joins the resulting evidence to every response-package row. `exists` requires HTTP 200 with an exact metadata-name match. `not_found` requires HTTP 404 and an expected JSON error value of `not found` or `not_found`. All other cases are `unresolved`.

The validator records URL, status, UTC check time, version, summary, error type, retry count, source hashes, and history. Resume requires matching format, both source hashes, package set, and validator version. Resolved names are reused; unresolved names are retried only with explicit `--retry-unresolved`, retaining prior history. Outputs are atomically written. A 404 remains evidence only and is not a confirmed hallucination.

## 9. PIPE-05 / PIPE-05B / PIPE-07 Verification

PIPE-05 is `pipe-05-classifier-1.0.0`. Its classification/status combinations are `VALID`/`AUTO_VALID` for `exists`, no classification/`VALIDATION_UNRESOLVED` for unresolved registry evidence, `AMBIGUOUS`/`REVIEW_REQUIRED` for unreviewed `not_found`, and a researcher-review outcome/`REVIEWED` for supported dated review evidence. PIPE-05 labels are not the PIPE-05B final taxonomy.

PIPE-05B is `pipe-05b-adjudicator-1.1.0`, with nine outcomes: `CONFIRMED_HALLUCINATION`, `LEGACY_OR_REMOVED`, `NAMESPACE_CONFUSION`, `PACKAGE_NAME_CONFUSION`, `INVALID_OR_REDUNDANT_TYPES_PACKAGE`, `ECOSYSTEM_CONFUSION`, `OTHER_DEPENDENCY_ERROR`, `SELF_REFERENCE_OR_LOCAL_PACKAGE`, and `UNRESOLVED`. It accepts only PIPE-05 `REVIEW_REQUIRED`/`AMBIGUOUS` rows, makes no network request, and writes a separate output. `confirmed_package_hallucination` is true only for `CONFIRMED_HALLUCINATION`; `external_dependency_eligible` is false for self/local, null for unresolved, and true otherwise; `dependency_failure` is null for unresolved, false for self/local, and an explicit Boolean for other outcomes.

Self/local adjudication requires the specified response-internal declaration, exact name match, declaration location, reference locations and contexts, and Boolean symbol-definition field. It cannot be inferred from a 404. `UNRESOLVED` requires insufficient evidence and cannot assert `dependency_failure`.

D037 is implemented in PIPE-07 `pipe-07-analysis-builder-1.1.0`. It accepts exactly one confirmation route: PIPE-05 `REVIEWED`/`CONFIRMED_HALLUCINATION`, or a guarded PIPE-05B confirmation from a PIPE-05 `REVIEW_REQUIRED`/`AMBIGUOUS` row. PIPE-07 verifies the source hash, versions, record key, source truncation, confirmation fields, all six checks, dated sources, UTC review time, and route exclusivity; malformed, duplicate, unmatched, or dual-route evidence fails closed. PIPE-07 records the confirmation route, version, and source hash without rewriting PIPE-05.

## 10. Figure and Table Assessment

Figure numbering matches Block 1: Figure 3-2 is the workflow figure and Figure 3-3 is the extraction-to-adjudication pipeline. Tables 3-5--3-10 contain methodology values only and no empirical counts. Table 3-10 correctly presents PIPE-05B outcomes rather than PIPE-05 statuses as final taxonomy; its non-fixed `dependency_failure` values remain correctly represented as explicitly recorded. No result leakage was found.

## 11. Corrections Applied

Applied only to `docs/report_drafts/chapter3_sections_3_5_to_3_9.md`:

- corrected HTTP-attempt versus transport-failure preservation wording;
- made API retry count and maximum attempts explicit;
- replaced “right-censored” with neutral ceiling-incompletion wording;
- narrowed the `package.json` parsing description to dependency objects; and
- made PIPE-04 retry, `Retry-After`, and fixed-interval behaviour exact.

## 12. Remaining Restrictions

Final v2.6 collection and a provenance-consistent final analysis remain pending. No achieved counts, final metrics, comparative results, risk findings, or inferential claims may be inserted into this block. Manual-route operational detail must remain limited to the verified planned 180/180 assignment. Appendix reference placeholders remain pending.

Progress-log update needed: **NO**. Final-paper note needed: **NO**. Draft reconciliation needed: **YES**; this report supplies the block-level reconciliation record.

## 13. Evidence Index

| Evidence | Verified use |
| --- | --- |
| `config/api_model_set_1.4.0.json`; `config/experiment_freeze_v2.6.0.json`; `manifests/api_final_v2.6.0_manifest.csv` | Frozen M1--M4 conditions, parameters, routing, ceilings, pacing, retry policy, and manifest ordering. |
| `scripts/collect_api_run.py`; `scripts/collect_api_batch_v2_6.py`; `scripts/finalize_interrupted_api_run.py`; collection tests | Request construction, preconditions, preservation, retries, mismatch handling, D035 source mapping, and D038 recovery. |
| `scripts/build_response_inventory.py`; `scripts/build_analysis_dataset.py`; `scripts/calculate_primary_metrics.py`; `scripts/calculate_dependency_reliability_metrics.py`; related schemas/tests | Status overlays, eligibility inheritance, zero-package SHR treatment, D037 routing, and D036 secondary treatment. |
| `scripts/extract_package_references.py`; PIPE-03 schemas/tests | Extracted forms, parsing, exclusions, provenance, and unique unit. |
| `scripts/validate_npm_packages.py`; PIPE-04 schema/tests | Registry protocol, evidence states, retry policy, cache/resume, provenance, and atomic outputs. |
| `scripts/classify_npm_packages.py`; `scripts/adjudicate_review_required_packages.py`; PIPE-05/05B schemas/tests | Classification labels/statuses, review constraints, taxonomy, derived fields, and self/local/unresolved semantics. |
| `docs/decision_log.md` D033--D038; `docs/analysis_specification_v1.0.md`; status, progress, notes, reconciliation, and Block 1 records | Controlling metric, eligibility, recovery, report-boundary, figure-numbering, and final-results-pending decisions. |
