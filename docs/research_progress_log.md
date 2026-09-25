## 2026-09-17

### Experimental collection status

- v2.2 API collection is active.
- Current manifest: `manifests/api_final_v2.2.0_manifest.csv`.
- Current state file: `data/final/api_batch_state_v2.2.0.json`.
- M2 was sent successfully to Groq.
- M3 is waiting because the frozen 45-minute Groq pacing interval is being enforced.
- No pacing bypass, state reset, or manual collection-order modification was performed.

### Analysis preparation

- Created the pre-analysis specification:
  `docs/analysis_specification_v1.0.md`
- Initial SHA-256 recorded:
  `9616c72ae24557b8fffec13b88ec112e76061ce308dd1ef7736cac09bb7c67b4`
- Primary package-level analysis is being designed around npm package hallucination.
- Truncation is being treated separately from hallucination.
- Raw responses are to remain immutable; validation and classifications will be stored as derived data.

### Project coordination

- Adopted `docs/research_progress_log.md` as the chronological record of completed research work.
- Cross-chat work must record completed milestones rather than relying only on ChatGPT conversation history.

### Next

- Build the read-only response inventory pipeline.
- Continue analysis/report preparation while Groq pacing is active.
- Recheck M3 only with the approved v2.2 `--dry-run --limit 1` command.

### Response inventory pipeline

- Implemented the read-only v2.2 response inventory builder:
  `scripts/build_response_inventory.py`.
- Added automated tests:
  `tests/test_response_inventory.py`.
- Added inventory item schema:
  `schemas/response_inventory_item.schema.json`.
- The inventory preserves one row per planned manifest run and supports
  uncollected/pending runs.
- Manifest ordering and provenance are preserved.
- Fields unavailable from experimental evidence remain null rather than being inferred.
- Hardened failed-attempt handling:
  - explicit `failed_attempts/attempt-*` evidence may mark a metadata-less run failed;
  - explicit `temporarily_blocked_or_failed` state evidence may mark a run failed;
  - missing metadata alone does not imply failure;
  - ordinary `attempts/attempt-*` alone does not imply failure.
- Updated the live v2.2 verification test so it checks stable structural invariants
  rather than exact collection counts that change during active collection.
- Test result:
  `python3 -m unittest tests/test_response_inventory.py`
  → 3 tests passed.
- No frozen manifest, active v2.2 state file, raw response, prompt, model/generation
  configuration, or pacing rule was modified by this analysis task.
- The pre-existing modified active state file was not changed by this task.

### Next

- Generate the first derived response inventory snapshot for v2.2.
- Verify row count, status mapping, hashes, and sampled records.
- Continue to package extraction only after the inventory snapshot is validated.

### First v2.2 response inventory snapshot

- Generated the first derived response inventory for the active v2.2 experiment.
- Command:
  `python3 scripts/build_response_inventory.py --manifest manifests/api_final_v2.2.0_manifest.csv --raw-root data/final/raw --output-json results/response_inventory_v2.2.0.json --output-csv results/response_inventory_v2.2.0.csv`
- Inventory contains 360 planned runs in manifest order.
- CSV contains 361 lines including the header.
- Current collection status at snapshot time:
  - completed: 1
  - truncated: 1
  - pending: 358
- Current completion status:
  - COMPLETED: 1
  - TRUNCATED: 1
  - pending/blank: 358
- Verified first collected rows:
  - `API-v2.2-AUTH-FED-01-M1-R01` → completed, 11347 completion tokens.
  - `API-v2.2-AUTH-FED-01-M2-R01` → truncated, 12000 completion tokens.
- Derived output hashes:
  - `results/response_inventory_v2.2.0.json`
    `b6f44b72c2d7bfc66ec264ae67f368e0b589a33ad5bcf7ac2caa30cc8f34b697`
  - `results/response_inventory_v2.2.0.csv`
    `34bad9dc91a9126d9fb5830ed03f8017d673022c8491a13a2ca9044747081311`
- No frozen experiment input or raw response was modified during inventory generation.

### Next

- Begin package extraction implementation using the validated response inventory and raw response artifacts.
- Keep collection and analysis paths separate.
- Continue v2.2 collection only according to frozen pacing.

### Response inventory snapshot provenance correction

- Audited the preservation of the v2.2 derived response inventory after the rolling
  outputs changed after the first documented snapshot.
- The first snapshot's terminal-recorded summary and hashes remain historical
  provenance evidence: 360 planned runs; 1 completed; 1 truncated; 358 pending;
  JSON SHA-256
  `b6f44b72c2d7bfc66ec264ae67f368e0b589a33ad5bcf7ac2caa30cc8f34b697`;
  CSV SHA-256
  `34bad9dc91a9126d9fb5830ed03f8017d673022c8491a13a2ca9044747081311`.
- The original byte-for-byte files were not preserved before rolling regeneration;
  their historical timestamp and hashes are not assigned to regenerated content.
- A later rolling inventory was preserved at
  `results/snapshots/response_inventory_v2.2.0_preserved_at_20260917T082919Z.json`
  and `.csv`. It contains 360 planned runs: 2 completed, 2 truncated, and 356
  pending. Its SHA-256 hashes are respectively
  `ec4f95f3fc96c3ef305ca59801341b37ef9b1967a02ef79ec7695a77c89722fe` and
  `a0e05acce5a677b8d50469f6bdb0dacb8e9405482b79ce8b1f13fe8cc22bec04`.
- The four non-pending records in that preserved later inventory are collection
  orders 1--4: M1 completed (11,347 tokens), M2 truncated (12,000), M3 completed
  (8,893), and M4 truncated (12,000), all for `API-v2.2-AUTH-FED-01` replicate
  `R01`.
- `results/response_inventory_v2.2.0.*` are rolling derived outputs. A documented
  milestone must use a timestamped preserved copy with hashes recorded immediately;
  the preserved later inventory is historical and may be stale relative to active
  collection.
- No frozen manifest, raw observation, collection state, prompt, model
  configuration, or pacing rule was modified during this correction.

### Preserved rolling v2.2 response-inventory snapshot (20260917T095610Z)

- After regeneration, the rolling inventory contains 360 planned runs: 6 completed,
  4 truncated, and 350 pending.
- Preserved copies were created immediately at
  `results/snapshots/response_inventory_v2.2.0_preserved_at_20260917T095610Z.json`
  and `.csv`.
- SHA-256:
  - JSON: `de51a6d9713c00579a624576feb3f66b94aeb02e957d04e50fddd05776dd0e3e`
  - CSV: `d209294f3e4b0fa69c90077c8fbb810c2840bd6b5d964f3b4f065862325f63bb`
- Each preserved file was verified byte-identical to its corresponding rolling
  output at preservation time. This is historical derived metadata and may become
  stale as active collection proceeds.

## 2026-09-17 — v2.2 initial four-model collection gate completed

- Completed the first four official observations of the frozen v2.2 experiment for task `AUTH-FED-01`, one observation per model condition.
- Verified observations:
  - `API-v2.2-AUTH-FED-01-M1-R01` — COMPLETED, `finish_reason=stop`, 11,347 completion tokens.
  - `API-v2.2-AUTH-FED-01-M2-R01` — TRUNCATED, `finish_reason=length`, 12,000 completion tokens.
  - `API-v2.2-AUTH-FED-01-M3-R01` — COMPLETED, `finish_reason=stop`, 8,893 completion tokens.
  - `API-v2.2-AUTH-FED-01-M4-R01` — TRUNCATED, `finish_reason=length`, 12,000 completion tokens.
- All four observations used the intended frozen model/provider conditions from `api-model-set-1.1.0`.
- All four recorded `tools_exposed=false` and no protocol deviations.
- Grep validation across all four response files found no simulated tool-call markup (`<tool_call>`, `<function=`, or `</tool_call>`).
- The 12,000-token ceiling resolved truncation for M1 and M3 but M2 and M4 still reached the output ceiling.
- Per the frozen protocol, truncated observations are preserved unchanged and will not be regenerated merely because of truncation.
- Next: refresh the derived v2.2 response inventory, verify counts/statuses, then continue official collection under the frozen pacing rules.

### Final-paper synchronization audit

- Created and audited `docs/final_paper_notes.md`.
- Reconciled the old university-draft methodology against the current v2.2 study.
- Verified that the frozen v2.2 truncation rule supersedes earlier analysis-spec wording: primary PHR/SHR exclude `TRUNCATED` observations, with separately labeled secondary/sensitivity treatment.
- Verified `risk-model-1.0.0` from `docs/risk_assessment_protocol.md` as the current frozen risk methodology: Impact (1–5) × Detectability (1–4); no risk results have yet been produced.
- Flagged the package-counting/PHR wording for explicit reconciliation before final metric generation.
- Identified that the previous current-status document was stale because preserved M1–M4 raw artifacts now exist; actual run status must be determined from metadata/state, not directory existence.
- No frozen experimental input was changed by the paper-note audit.

## 2026-09-17 — v2.3 prospective freeze for fast final collection

- Prospectively stopped v2.2 after 10 collected observations: 6 completed, 4 truncated, and 350 pending of 360 planned. The 10 observations remain unchanged as methodological evidence and are excluded from v2.3 primary metrics.
- Created fresh v2.3 artifacts: `api-model-set-1.2.0`, 30 rendered prompts, a 360-row all-pending `API-v2.3-` manifest, empty v2.3 batch state, and v2.3 freeze record.
- v2.3 retains the v2.2 task set, prompt content, four exact model/provider conditions and pins, no-fallback/no-tools interface, sampling parameters, retry philosophy, and truncation policy.
- The sole planned change is sequential zero artificial provider spacing to remove the conservative researcher-imposed delay under the final collection window. HTTP 429 Retry-After and infrastructure retry/backoff remain binding; non-retryable quota/credit/account failures stop the batch without skipping or substitution.
- No API request was sent while creating or validating v2.3.


### 2026-09-18 — v2.3 initial four-model collection gate completed

- Completed the initial protocol/infrastructure gate for the frozen v2.3 API experiment.
- Frozen experiment commit/tag:
  - commit: `0ec24d4`
  - tag: `v2.3.0-freeze`
- Verified v2.3 dry-run began at `API-v2.3-AUTH-FED-01-M1-R01` with `wait_seconds: 0.0`.
- Collected the first four official v2.3 observations for task `AUTH-FED-01`, one for each model condition:
  - `API-v2.3-AUTH-FED-01-M1-R01`
  - `API-v2.3-AUTH-FED-01-M2-R01`
  - `API-v2.3-AUTH-FED-01-M3-R01`
  - `API-v2.3-AUTH-FED-01-M4-R01`
- All four observations used the expected model/provider routing, exposed no tools, and recorded no protocol deviations.
- All four observations ended with `finish_reason=length` and were preserved once as `TRUNCATED` according to the frozen protocol; none will be regenerated merely because of truncation.
- M1/OpenRouter raw provider metadata reported `completion_tokens=11998` and `reasoning_tokens=12087`; inspection of `provider_response.json` confirmed the collector preserved these upstream values unchanged. Treat this as a provider token-accounting anomaly rather than a collection/protocol failure.
- The initial gate therefore confirms the v2.3 collection path and zero-artificial-pacing behavior, while also identifying a high early truncation rate that must be monitored and reported separately from primary SHR/PHR analysis.
- Next: continue the remaining v2.3 manifest sequentially under the frozen zero-artificial-pacing protocol and stop only on the defined provider/quota/non-retryable failure conditions.

### 2026-09-18 — v2.3 stopped on non-retryable empty-content provider response

- During frozen v2.3 sequential collection, the batch advanced through collection order 7 and then attempted `API-v2.3-AUTH-FED-02-M1-R01` at collection order 8.
- OpenRouter returned HTTP 200, but the response contained no non-empty assistant content.
- The collector preserved `prompt.txt`, `request.json`, and `metadata.json`; no usable `response.md` or `provider_response.json` was retained.
- The run was recorded with `collection_status: failed` and failure reason `HTTP 200 response contains no non-empty assistant content`.
- Inspection of `scripts/collect_api_run.py` confirmed automatic retries are limited to HTTP 429 and configured HTTP 5xx failures. HTTP 200 with empty assistant content is therefore non-retryable.
- Inspection of `scripts/collect_api_batch.py` confirmed existing `failed` runs block later collection rather than being skipped.
- The frozen v2.3 record explicitly states that non-retryable provider failures stop the batch without skipping or substitution.
- Therefore collection was stopped without retrying, deleting, skipping, substituting models/providers, or modifying frozen v2.3 inputs.
- Next: create a prospectively versioned operational amendment/new collection version that preserves non-retryable failed observations once but permits subsequent manifest rows to continue, while leaving generation semantics unchanged.

### 2026-09-18 — v2.4 prospective continuation version frozen

- Recommended and implemented **option A: a fresh separate 360-observation v2.4.0 experiment**, rather than reusing v2.3 observations under an amended denominator. This avoids mixing v2.3's frozen stop rule with v2.4's continuation rule.
- v2.3 remains stopped prospectively at `API-v2.3-AUTH-FED-02-M1-R01` because its frozen rule required a non-retryable provider failure to stop the batch.
- v2.4 was created prospectively before further collection. Its only methodological change is failure continuation: a non-retryable provider failure is preserved exactly once with explicit evidence, excluded from primary SHR/PHR denominators, and skipped on future invocations so later manifest rows continue sequentially.
- v2.4 does not retry, regenerate, or substitute a model/provider after failure. The 30 tasks, wording, prompt bytes, four conditions, provider pins, no-fallback/no-tools rules, sampling/request structure, truncation semantics, infrastructure retry/backoff, and zero artificial pacing are unchanged.
- New immutable inputs are the v2.4 manifest, freeze record, fresh state, versioned prompt copies, and prompt template copy. Their prompt hashes match v2.3 byte-for-byte.
- No API request was sent while creating or validating v2.4.

## 2026-09-21

### PIPE-03 — npm package-reference extraction completed

- Implemented the deterministic read-only package-reference extractor:
  `scripts/extract_package_references.py`.
- Added occurrence schema:
  `schemas/package_reference_occurrence.schema.json`.
- Added unique-package schema:
  `schemas/package_reference_unique.schema.json`.
- Added automated tests:
  `tests/test_extract_package_references.py`.
- Added decision-log entry D029 defining the extraction contract.
- Extraction supports explicit ES module imports, CommonJS `require()` references,
  dynamic `import()`, `npm install` / `npm i` operands, and package.json dependency
  objects.
- Normalization preserves scoped npm package roots, removes import subpaths, and
  separates explicit version specifiers.
- Node.js built-ins, `node:` references, relative/local/absolute paths, `file:`
  references, and HTTP(S) URLs are excluded.
- Occurrence-level references are preserved for provenance. A separate deterministic
  unique view is deduplicated only by `(run_id, normalized_package)`.
- PIPE-03 deliberately does not calculate PHR, SHR, hallucination classifications,
  registry status, or risk scores.
- Current extraction over the 10 collected v2.2 observations produced 167
  package-reference occurrences and 97 unique normalized package-per-response
  records. Source types were 104 `package_json`, 58 `es_import`, and 5
  `dynamic_import`. These are intermediate extraction counts, not hallucination
  results.
- Test result: `python3 -m unittest tests/test_extract_package_references.py` and
  the verified broader test suite: 70 tests passed.
- No npm/registry/network/model request or generated-code execution occurred. No
  frozen manifest, state, raw observation, prompt, generation configuration, pacing
  rule, or historical snapshot was modified.

### Next

- Implement PIPE-04 read-only npm registry validation.
- Preserve validation evidence and timestamps.
- Distinguish `exists`, `not_found`, and `unresolved`.
- Do not calculate PHR/SHR until validation and research classification are complete.

### PIPE-03A/03B/03C — extraction audit, repair, and closure

- PIPE-03A manually audited all 10 collected v2.2 raw responses against the derived
  extraction output. Its initial result was **FAIL / FIX REQUIRED**: a line-bound
  import regex missed 8 multiline literal ESM imports. It found 0 false positives
  and 0 referential-integrity mismatches.
- The missed references included `@peculiar/asn1-schema`, `fido2-lib`,
  `@simplewebauthn/types`, `@simplewebauthn/server`, and `jose`.
- PIPE-03B repaired the extractor as
  `pipe-03-package-reference-extractor-1.0.1` with bounded multiline static-import
  scanning. Regression tests cover scoped/unscoped packages, `import type`,
  aliasing, comments, subpaths, built-ins, default-plus-named imports, and ordering.
- Regeneration added exactly 8 occurrence records, yielding **175 occurrences**;
  the **97 unique `(run_id, normalized_package)` keys** were unchanged. These are
  intermediate processing counts, not hallucination findings.
- The post-fix audit concluded **PASS WITH DOCUMENTED LIMITATIONS** after reviewing
  all 10 responses, 175 occurrences, and 97 unique records: 0 false positives and
  0 false negatives under D029, 3 documented contract-boundary cases, 0
  referential-integrity mismatches, and byte-deterministic outputs.
- Final authoritative SHA-256 hashes:
  - occurrence JSON: `fb650d06bfab6ab29cf8a162e8452d612e58f716cd99be53b4db4212dad7fee6`
  - occurrence CSV: `e74f6de2e5c1f66beb3636b38a24df49860c157e79ce8baa88ba104751deb55e`
  - unique JSON: `a6dbca67c6f8e34665535ffc95ac6bb46e6846f61d806441edecdc7a9a0fd7b5`
  - unique CSV: `9bca2b66d3b496bbfc648a78debcbb2298cfeb0244e3f89ffb0c89f969a42d17`
- The focused extractor suite passed 14/14 tests and the response-inventory suite
  passed 3/3. The broader suite had one unrelated v2.4 freeze-test failure because
  its empty-initial-state assertion no longer matches the active collection state.
- PIPE-03C's read-only coexistence check found no evidence that PIPE-03 created
  unrelated repository-root artifacts; possible parallel-agent artifacts were left
  untouched. No frozen input, raw response, collection state, or response inventory
  was modified by PIPE-03A/03B/03C.

### PIPE-04/04A — npm registry validator implemented and first validation snapshot completed

- Implemented the read-only official npm metadata validator
  `scripts/validate_npm_packages.py`, its registry-evidence-only schema
  `schemas/npm_package_validation_pipe04_v1.schema.json`, and offline tests
  `tests/test_validate_npm_packages.py`. Its operational states are `exists`,
  `not_found`, and `unresolved`, not research hallucination classifications.
- The 97 v2.2 response-package rows contained 44 distinct normalized package names.
  PIPE-04A checked all 44: 43 `exists`, 1 `not_found` (`webauthn2`), and 0
  `unresolved`. The validator attempted 45 HTTP requests because `ts-node`
  required one retry; the deterministic joined output covers all 97 rows.
- The `webauthn2` 404 is registry evidence only: it remains a candidate for
  conservative PIPE-05 classification/adjudication, not a confirmed hallucination.
  No PHR, SHR, model comparison, hallucination prevalence, or risk score was
  calculated.
- Authoritative PIPE-04A SHA-256 hashes:
  - package JSON: `b478ca330b659e27e001e11e49889fcf1b8d3f68c48004924ff5790d9a9cff21`
  - package CSV: `4113bd81a2de12c381308337a0a7ea085018e214d0b0fe32cc2289ffcb348a87`
  - joined JSON: `6b8f7c0b45488630b26a4d4c3a39c1c64cbda3e5ef736943b0eee6d165cc9f59`
  - joined CSV: `b541e0375ceceadcf9e575ee9336e534103b89422449a51a78c0f7e021f4c42a`
- Byte-identical copies of all four outputs were preserved under
  `results/snapshots/` with timestamp `20260921T060711Z`; each snapshot has
  the corresponding live-file hash above.

### v2.4 prospectively stopped; 16,000-token v2.5 amendment selected

- Reviewed preliminary official v2.4 collection outcomes under the frozen 12,000-token maximum output ceiling.
- At the decision point, v2.4 had reached 30 finalized observations: 14 completed, 12 truncated, and 4 failed.
- The observed truncation rate was therefore 40.0% overall at this preliminary checkpoint.
- Model-level evidence showed repeated ceiling hits particularly for M2 and M4, while completed-response token counts alone could not estimate the natural lengths of truncated outputs because those observations are right-censored at 12,000 tokens.
- Because primary SHR/PHR analysis excludes truncated observations, continuing with the observed truncation burden risked materially reducing the usable primary-analysis sample.
- Decision: prospectively stop v2.4 without altering, deleting, retrying, or regenerating any existing v2.4 observation.
- A new fresh experiment version, v2.5, will be created from observation 1 with a 16,000-token maximum output ceiling.
- The planned v2.5 amendment changes only the maximum output ceiling from 12,000 to 16,000 tokens. Tasks, prompt content, model conditions, provider routing, sampling parameters other than the ceiling, failure-continuation semantics, retry rules, no-tools constraints, and zero researcher-imposed pacing remain unchanged.
- Existing v2.4 observations remain methodological evidence and will not be mixed into v2.5 primary SHR/PHR results.
- No v2.5 API observations may be collected until the new version is implemented, validated, frozen, committed, and tagged.

### v2.5 fresh experiment implemented and validated

- Implemented a new independent `API-v2.5-` 360-row, all-pending manifest, fresh empty batch state, byte-identical prompt template and 30 rendered prompts, and `api-model-set-1.3.0`.
- The sole experimental change from v2.4 is `max_output_tokens` from 12,000 to 16,000. Model identities, provider pins, remaining generation settings, retry/backoff, v2.4 failure continuation, truncation handling, and zero artificial pacing remain the same.
- Created prospective freeze records and a versioned v2.5 batch wrapper. Freeze checks passed for v2.3, v2.4, and v2.5. Targeted API tests passed 37/37; the full repository suite passed 113/113.
- SHA-256: task set `ef0aff59f8a3934f65379d34036848652b7b5593f595ffa4b449a15af021546b`; model set `554cd8d8d011639c46d9d2c0280f8b08c451ea475bc2b8e2ec4006c8ab75b1e4`; template `8d3971d6f9f86dfd98a4b5c49c0c13d734b7f650744da682225195f2ea49b528`; manifest `c7911420181f090a16df33ed041caa800d5859e8e9a30882655b4ca02e72c438`; initial state `9c2816a76618a9edbab32648e7b7529ffdd66e17587a786757a79f6cb9c3d825`; freeze JSON `0e5ce36bf94cecc137c94056e762a19c301c2ee0db8bc0791118d2894cedb197`; freeze Markdown `ba13bdf74a1d8ef399fe39a7a7d336c819493645d457e49fb408071795128f29`.
- Dry run: `API-v2.5-AUTH-FED-01-M1-R01`, order 1, OpenRouter, `wait_seconds: 0.0`. Zero real v2.5 API requests were sent. No commit or tag was created; researcher review is next.

### v2.5 freeze committed and tagged

- The reviewed v2.5 prospective experiment freeze was committed on branch `feature/data-collection`.
- Freeze commit: `87d3158` (`freeze: add v2.5 experiment with 16000-token output ceiling`).
- Freeze tag: `v2.5.0-freeze`, verified to point to commit `87d3158`.
- Immediately before the freeze commit, `git diff --cached --check` passed, the complete repository test suite passed 113/113 tests, and `python3 scripts/create_experiment_freeze_v2_5.py --check` passed.
- No official v2.5 API request had been sent at the time of commit/tag creation.
- The next experimental step is the first official v2.5 observation, which will also serve as the live compatibility check for the 16,000-token ceiling.

### First official v2.5 observation completed successfully

- Collected and verified the first official v2.5 observation: `API-v2.5-AUTH-FED-01-M1-R01`.
- Collection status: `completed`; response completion status: `COMPLETED`; finish reason: `stop`.
- The OpenRouter M1 request used the frozen v2.5 `max_output_tokens: 16000` setting and was accepted successfully.
- Token usage: 228 prompt tokens, 7,058 completion tokens, and 7,286 total tokens; completion-token details reported 294 reasoning tokens.
- The request succeeded on attempt 1 with HTTP 200 and no retry.
- Generation started at `2026-09-21T08:37:31.701588Z` and ended at `2026-09-21T08:43:04.812012Z`.
- This confirms live compatibility of the 16,000-token ceiling for the M1/OpenRouter condition only; it does not yet establish compatibility for M2-M4 or demonstrate that v2.5 eliminates truncation.
- No SHR, PHR, hallucination-prevalence, or risk result is inferred from this observation.

### v2.5 four-model initial live gate completed

- Completed the first official v2.5 observation for each frozen model condition using `AUTH-FED-01`, repetition `R01`.
- All four conditions accepted the frozen `max_output_tokens: 16000` request and returned HTTP 200 on attempt 1 with no retry.
- Verified outcomes from each run's authoritative `metadata.json`:
  - M1 `API-v2.5-AUTH-FED-01-M1-R01`: `COMPLETED`, finish reason `stop`, 7,058 completion tokens.
  - M2 `API-v2.5-AUTH-FED-01-M2-R01`: `COMPLETED`, finish reason `stop`, 13,998 completion tokens.
  - M3 `API-v2.5-AUTH-FED-01-M3-R01`: `COMPLETED`, finish reason `stop`, 8,210 completion tokens.
  - M4 `API-v2.5-AUTH-FED-01-M4-R01`: `TRUNCATED`, finish reason `length`, exactly 16,000 completion tokens.
- M2 demonstrates that the 16,000-token ceiling provides useful headroom beyond v2.4's 12,000-token ceiling for at least one observed generation; this must not be generalized to all responses.
- M4 demonstrates that the 16,000-token ceiling does not eliminate truncation.
- The batch-state event label `completed` is a generic successful-row-processing event: `run_batch()` appends it after the underlying collector returns successfully for either a completed or truncated response. The authoritative response-completion classification remains `collection_status` / `response_completion_status` in each run's metadata. Existing-run handling separately recognizes and preserves both `completed` and `truncated` observations.
- No collector code or frozen v2.5 experimental setting was changed after collection began.
- Initial gate outcome: 3 completed and 1 truncated observation. No SHR, PHR, hallucination-prevalence, or risk result is inferred from this gate.

### v2.5 preserved provider-format failure during continued collection

- During continued official v2.5 collection, `API-v2.5-AUTH-FED-02-M4-R01` received HTTP 200 on its first attempt, but the response body did not satisfy the collector's valid chat-completion structure.
- The run was preserved with `collection_status: failed` and failure reason `HTTP 200 response is not a valid chat completion`.
- No `response_completion_status` or `finish_reason` exists because no valid assistant completion was parsed.
- The failed run was not retried, regenerated, or substituted.
- The immediately preceding run, `API-v2.5-AUTH-FED-02-M3-R01`, had completed successfully before the batch stopped.
- Under the frozen v2.5 continuation rule, a subsequent invocation should preserve and skip this failed observation and continue to later manifest rows without retry or model/provider substitution.
- This observation is infrastructure/provider-format evidence and must be excluded from primary SHR/PHR denominators.

### v2.5 repeated provider-response failures during continued collection

- Continued official v2.5 collection preserved additional provider-response failures without retry, regeneration, or substitution.
- `API-v2.5-AUTH-FED-03-M4-R01` became the second M4/OpenRouter observation to fail with HTTP 200 and failure reason `HTTP 200 response is not a valid chat completion`, following the earlier `API-v2.5-AUTH-FED-02-M4-R01` failure of the same class.
- `API-v2.5-AUTH-FED-03-M1-R01` failed on its first HTTP 200 response with the distinct failure reason `HTTP 200 response contains no non-empty assistant content`.
- For the M1 empty-content failure, no valid assistant completion was available, so `response_completion_status` and `finish_reason` are absent.
- The collector correctly skipped previously preserved completed and failed observations on subsequent invocation and continued to the next pending manifest row without retry or model/provider substitution.
- These are infrastructure/provider-response failures, not hallucination outcomes or truncations, and they must be excluded from primary SHR/PHR denominators.
- No frozen v2.5 collection setting or collector code was changed in response to these failures.

### v2.5 continued collection confirms repeated M4 truncation

- Continued official v2.5 collection successfully processed `API-v2.5-AUTH-FED-03-M2-R01` and `API-v2.5-AUTH-FED-04-M4-R01`.
- `API-v2.5-AUTH-FED-03-M2-R01` completed normally with finish reason `stop` and 9,210 completion tokens under the frozen 16,000-token ceiling.
- `API-v2.5-AUTH-FED-04-M4-R01` was preserved as `TRUNCATED` with finish reason `length` and exactly 16,000 completion tokens.
- This is a second verified v2.5 M4 observation to hit the 16,000-token ceiling, following `API-v2.5-AUTH-FED-01-M4-R01`.
- The observation confirms that the higher v2.5 ceiling provides additional headroom but does not eliminate truncation for all responses.
- No truncated observation will be regenerated or included in primary SHR/PHR denominators.

### v2.5 AUTH-FED-04/05 outcomes verified

- Verified authoritative per-run metadata for the remaining `AUTH-FED-04` observations and the first two `AUTH-FED-05` observations.
- `API-v2.5-AUTH-FED-04-M1-R01` was preserved as `failed` after HTTP 200 returned no non-empty assistant content; no response-completion status or finish reason exists.
- `API-v2.5-AUTH-FED-04-M2-R01` was preserved as `TRUNCATED` with finish reason `length` at exactly 16,000 completion tokens.
- `API-v2.5-AUTH-FED-04-M3-R01` completed normally with finish reason `stop` and 10,387 completion tokens.
- `API-v2.5-AUTH-FED-04-M4-R01` was preserved as `TRUNCATED` with finish reason `length` at exactly 16,000 completion tokens.
- `API-v2.5-AUTH-FED-05-M1-R01` completed normally with finish reason `stop` and 6,219 completion tokens.
- `API-v2.5-AUTH-FED-05-M2-R01` completed normally with finish reason `stop` and 13,024 completion tokens.
- All six requests used the frozen 16,000-token ceiling and all recorded attempts were first-attempt HTTP 200 responses.
- These observations further confirm that v2.5 still contains three distinct collection outcomes: completed responses, right-censored truncated responses, and preserved provider-response failures.
- Truncated and failed observations remain excluded from primary SHR/PHR denominators and are not regenerated or substituted.

### v2.5 AUTH-FED-05 completed across all four model conditions

- Verified the remaining `AUTH-FED-05` observations from authoritative per-run metadata.
- `API-v2.5-AUTH-FED-05-M3-R01` completed normally with finish reason `stop` and 9,215 completion tokens.
- `API-v2.5-AUTH-FED-05-M4-R01` completed normally with finish reason `stop` and 13,154 completion tokens.
- Together with the previously verified M1 and M2 observations, all four `AUTH-FED-05` model-condition runs completed normally under the frozen 16,000-token ceiling.
- This confirms that M4 does not always truncate under v2.5; earlier M4 ceiling hits remain valid observations but are not universal for that condition.
- No SHR, PHR, hallucination-prevalence, or risk conclusion is inferred from this task-level completion pattern.

### v2.5 PKI-CRYPTO collection begins with mixed completion outcomes

- Verified the first two collected `PKI-CRYPTO-01` observations from authoritative per-run metadata.
- `API-v2.5-PKI-CRYPTO-01-M2-R01` was preserved as `TRUNCATED` with finish reason `length` at exactly 16,000 completion tokens.
- `API-v2.5-PKI-CRYPTO-01-M3-R01` completed normally with finish reason `stop` and 6,429 completion tokens.
- Both observations used the frozen v2.5 16,000-token ceiling and completed on the first HTTP attempt.
- This provides another verified example that truncation under v2.5 is not limited to M4; M2 can also reach the 16,000-token ceiling.
- Truncated observations remain preserved once and excluded from primary SHR/PHR denominators.

### v2.5 prospectively stopped; final high-output v2.6 amendment selected

- Reviewed verified v2.5 collection evidence showing repeated right-censoring at the 16,000-token output ceiling across multiple model conditions, including M2 and M4.
- v2.5 also demonstrated that some responses complete normally above the earlier 12,000-token ceiling, while others still reach 16,000 tokens with finish reason `length`.
- Decision: prospectively stop v2.5 without deleting, retrying, regenerating, or altering any existing v2.5 observation.
- A fresh v2.6 experiment will begin from observation 1 with model-specific output ceilings chosen near the supported maximums of the selected model/provider conditions:
  - M1: 64,000 output tokens.
  - M2: 32,768 output tokens, with the same `qwen/qwen3.8-27b` model moved from Groq to OpenRouter because the Groq condition cannot provide substantially more than the current v2.5 ceiling.
  - M3: 65,536 output tokens.
  - M4: 65,536 output tokens.
- The M2 provider change and the model-specific output ceilings make v2.6 a new experimental version; v2.5 observations must not be pooled into v2.6 primary SHR/PHR results.
- All other experimental dimensions are intended to remain unchanged unless required by provider-specific request compatibility: task set, prompt bytes, repetitions, temperature, top-p, no-tools policy, retry semantics, failure preservation, truncation preservation, and zero researcher-imposed pacing.
- v2.6 is intended as the final prospective collection protocol. Any remaining responses that hit their supported output ceiling will be preserved as right-censored truncated observations rather than triggering another protocol restart.
- No v2.6 API request may be sent until the implementation is reviewed, tested, frozen, committed, and tagged.

### 2026-09-22 — prospective v2.6 implementation and local validation

- Implemented a fresh independent v2.6.0 namespace with `api-model-set-1.4.0`, 360 unique all-pending `API-v2.6-` manifest rows, a zero-event/zero-pacing-history initial state, byte-identical copies of the v2.5 template and all 30 rendered prompts, and no v2.6 raw observations.
- M1–M4 output ceilings are 64,000, 32,768, 65,536, and 65,536 respectively. The shared collector selects the ceiling from the model condition for v2.6 while retaining the frozen v2.5 shared 16,000-token behavior.
- M2 retains model ID `qwen/qwen3.8-27b` and moves to OpenRouter with a Darkbloom-only provider pin: `order` and `only` are both `darkbloom`, provider fallback is disabled, and all request parameters are required. The other three model/provider conditions retain their v2.5 identities and routing.
- OpenRouter's Qwen3.8 model and Darkbloom provider pages establish the model/provider pairing. The OpenRouter routing documentation and model pages, plus Groq's GPT-OSS-120B model page, support the documented request routing and ceilings; their URLs are preserved in the v2.6 freeze record.
- v2.5 was prospectively stopped and remains separate historical evidence outside v2.6 primary SHR/PHR. v2.6 is intended as the final protocol version; further ceiling hits are preserved once as right-censored truncations, without a restart. No v2.6 result or live API request exists at this implementation point.

### 2026-09-22 — v2.6 prospective experiment frozen and tagged

- Completed final validation of the prospective v2.6 experiment before live collection.
- v2.6 implementation and freeze artifacts were committed as:
  - commit: `5247c2bccb58ecd6c86b9b7e92d800ade0378282`
  - commit message: `Freeze prospective v2.6 API experiment with model-specific ceilings and Darkbloom-pinned M2`
- Created and verified annotated tag:
  - `v2.6.0-freeze`
  - tag points to commit `5247c2bccb58ecd6c86b9b7e92d800ade0378282`.
- Frozen v2.6 model conditions:
  - M1 `cohere/north-mini-code:free` via OpenRouter, provider pin `cohere`, max output 64,000.
  - M2 `qwen/qwen3.8-27b` via OpenRouter, provider pin `darkbloom`, max output 32,768, provider fallback disabled.
  - M3 `openai/gpt-oss-120b` via Groq, max output 65,536.
  - M4 `nvidia/nemotron-3-ultra-550b-a55b:free` via OpenRouter, provider pin `nvidia`, max output 65,536.
- v2.6 contains 360 unique all-pending planned observations, with 90 per model, 120 per repetition, and 60 per category.
- The v2.6 prompt template and all 30 rendered prompts are byte-identical to v2.5.
- Validation before freeze:
  - v2.5 tests: 4/4 passed.
  - v2.6 targeted tests: 5/5 passed.
  - shared API/freeze tests: 33/33 passed.
  - full repository suite: 118/118 passed.
  - v2.5 freeze verification: PASS.
  - v2.6 freeze verification: PASS.
  - `git diff --check`: PASS.
- SHA-256 comparison of 195 protected v2.5 artifacts showed 0 added, 0 removed, and 0 changed during v2.6 implementation/test repair.
- No live v2.6 provider API request had been sent at the time of freeze/tag creation.
- v2.5 remains preserved as methodological evidence and is excluded from v2.6 primary SHR/PHR.
- v2.6 is the final prospective collection protocol. Any remaining ceiling hit will be preserved as right-censored truncation rather than causing another protocol restart.
- Next step: record final-paper freeze provenance, then begin live v2.6 collection from observation 1 without altering frozen inputs.

### 2026-09-22 — first official v2.6 observation successfully collected

- Began official collection under frozen commit `5247c2bccb58ecd6c86b9b7e92d800ade0378282` / tag `v2.6.0-freeze`.
- First observation: `API-v2.6-AUTH-FED-01-M1-R01`.
- Model condition: M1, `cohere/north-mini-code:free` via OpenRouter with resolved underlying provider `Cohere`.
- Collection result: `completed`; response completion status `COMPLETED`; finish reason `stop`.
- Request used the frozen 64,000-token M1 output ceiling, temperature 0.6, top_p 0.95, uncontrolled seed, one user message, and no tools.
- Provider returned the requested model identity with no recorded protocol deviation.
- Token usage: 228 prompt tokens, 16,832 completion tokens, 17,060 total tokens; 9,600 reasoning tokens reported.
- Provider-reported cost was 0.
- Request completed with HTTP 200 on attempt 1.
- The 16,832-token completed response exceeds the former v2.5 16,000-token ceiling, providing direct operational evidence that the increased v2.6 ceiling can prevent ceiling-induced truncation for at least some responses.
- No regeneration, retry beyond the frozen infrastructure policy, or protocol amendment was performed.
- Next step: continue v2.6 collection using larger batches while preserving failed or truncated observations exactly once.

### 2026-09-22 — temporary v2.6 collection scheduling decision due M2 billing-access failure

- Three official v2.6 M2 observations have been preserved as failed pre-generation observations with OpenRouter HTTP 402 because paid-credit authorization was unavailable for the frozen 32,768-token M2 request.
- The frozen M2 model, provider pin, token ceiling, prompt, retry/failure policy, and all other experimental parameters remain unchanged.
- To avoid blocking collection of unaffected model conditions, remaining M1, M3, and M4 observations will be collected first while still-pending M2 observations remain pending and unmodified.
- No existing failed M2 observation will be retried, regenerated, deleted, or substituted.
- After OpenRouter paid access is available, the remaining pending M2 observations will be collected under the same frozen v2.6 M2 configuration.
- The frozen manifest must not be edited or reordered. Original run IDs and manifest collection-order values remain authoritative.
- This is an operational scheduling change caused by temporary provider billing access, not a change to the experimental model conditions or analysis definitions.

### 2026-09-22 — post-freeze v2.6 M2-deferral scheduling support committed

- Added an operational-only model-exclusion option to the v2.6 batch driver so unaffected M1, M3, and M4 observations can be collected while pending M2 observations are temporarily deferred because of OpenRouter paid-credit access.
- Operational scheduling implementation commit: `4bf0240`.
- Commit message: `Add v2.6 model exclusion scheduling for deferred M2 collection`.
- Exactly three files were committed: `scripts/collect_api_batch_v2_6.py`, `tests/test_api_v2_6.py`, and `tests/test_api_v2_6_exclude_model.py`.
- The frozen v2.6 experiment remains anchored at commit `5247c2bccb58ecd6c86b9b7e92d800ade0378282` and tag `v2.6.0-freeze`; no frozen manifest, prompt, model configuration, output ceiling, retry rule, failure rule, or analysis definition was changed.
- Filtering is applied only in memory. The frozen manifest remains byte-identical and original `collection_order` values are preserved.
- Existing failed M2 observations are not retried, regenerated, deleted, or substituted. Still-pending M2 rows remain pending until paid access is restored.
- Validation after the scheduling change: v2.6 tests 5/5 PASS, exclusion-filter tests 12/12 PASS, v2.5 tests 4/4 PASS, shared freeze tests 9/9 PASS, full repository suite 130/130 PASS, and both v2.5 and v2.6 freeze verification PASS.
- Existing v2.6 raw observations and the v2.6 manifest were verified unchanged during implementation/testing.
- No live API request was sent while implementing or validating the scheduling option.

### 2026-09-22 — v2.6 non-M2 verification batch: first 64k truncation and Nvidia overload failure

- Continued official v2.6 collection with M2 temporarily excluded using the post-freeze operational scheduling filter.
- The M2 exclusion behaved correctly: pending M2 rows were not attempted and the three previously preserved M2 HTTP 402 failures remained unchanged.
- `API-v2.6-AUTH-FED-04-M1-R01` was preserved as truncated with finish reason `length` under the frozen M1 64,000-token output ceiling.
- This confirms that increasing the v2.6 output ceiling substantially reduces avoidable censoring but cannot guarantee elimination of truncation.
- `API-v2.6-AUTH-FED-05-M4-R01` was preserved as failed after OpenRouter returned HTTP 200 containing an upstream Nvidia error payload: code 503, `provider_overloaded`, message `Service temporarily overloaded`.
- The M4 failure was therefore an upstream provider/infrastructure failure rather than a generated-response or prompt-format failure.
- Neither the truncated M1 observation nor the failed M4 observation was retried, regenerated, deleted, or substituted.
- No frozen experimental input or model condition was changed.

### 2026-09-22 — recurring v2.6 M4 Nvidia provider-overload failures confirmed

- A second official M4 observation, `API-v2.6-PKI-CRYPTO-01-M4-R01`, was preserved as failed because OpenRouter returned an upstream Nvidia error payload with code 503, error type `provider_overloaded`, and message `Service temporarily overloaded`.
- This matches the previously preserved M4 failure `API-v2.6-AUTH-FED-05-M4-R01`.
- These failures are therefore treated as recurring provider/infrastructure availability failures rather than model-output, prompt-format, hallucination, or truncation events.
- Failed M4 observations are preserved once and are not retried, regenerated, deleted, or substituted.
- Pending M2 observations remain temporarily excluded from collection; no new M2 observation was attempted during this non-M2 batch.

### SCREEN-01 — interim review-required dependency screening completed

- A fresh v2.6 checkpoint was processed through the current PIPE-03/04/05/07 pipeline using extractor version 1.0.2.
- Screening population contained 350 metric-eligible unique `(run_id, normalized_package)` package-response rows across 35 eligible completed responses.
- 5/350 eligible package-response rows (1.43%) were classified `AMBIGUOUS` / `REVIEW_REQUIRED`.
- These 5 rows occurred in 5 distinct eligible responses, giving an interim review-required response screening rate of 5/35 (14.29%).
- Each affected eligible response contained one review-required package.
- Eligible review-required package names at this checkpoint:
  `@types/xpath`, `@xmldom/xpath`, `pkcs12`, `mtls-pfx-loader`, `mime-node`.
- Two additional review-required rows were excluded from the primary screening rates because their responses were truncated:
  `@peculiar/asn1-rs` and `@types/pdf-lib`.
- These values are INTERIM DESCRIPTIVE SCREENING ONLY and are not final study results.
- `REVIEW_REQUIRED` is not equivalent to confirmed hallucination or confirmed dependency failure; evidence-based PIPE-05B adjudication is required before stronger conclusions are made.

### PIPE-05B — REVIEW_REQUIRED adjudication infrastructure implemented

- Implemented `scripts/adjudicate_review_required_packages.py`, a conservative, evidence-based secondary adjudication tool for PIPE-05 rows already marked `AMBIGUOUS`/`REVIEW_REQUIRED`.
- Taxonomy: `CONFIRMED_HALLUCINATION`, `LEGACY_OR_REMOVED`, `NAMESPACE_CONFUSION`, `PACKAGE_NAME_CONFUSION`, `INVALID_OR_REDUNDANT_TYPES_PACKAGE`, `ECOSYSTEM_CONFUSION`, `OTHER_DEPENDENCY_ERROR`, `UNRESOLVED`; `dependency_failure` is tracked independently of `confirmed_package_hallucination`.
- Reads an existing PIPE-05 joined classification envelope read-only; writes a separate PIPE-05B adjudication output. It does not modify PIPE-05 outputs, PHR, or SHR.
- Created `scripts/adjudicate_review_required_packages.py`, `schemas/package_adjudication_pipe05b_v1.schema.json`, and `tests/test_adjudicate_review_required_packages.py`.
- 22/22 new PIPE-05B tests passed using synthetic fixtures only; full suite 287 run, 285 passed, with 2 pre-existing unrelated `test_api_freeze.py` failures.
- No real `REVIEW_REQUIRED` package was adjudicated; this milestone covers infrastructure only.

### 2026-09-22 — M3/M4-first scheduling checkpoint

- Continued v2.6 collection using the operational scheduling filter with M1 and M2 excluded, leaving only pending M3 and M4 observations eligible.
- This scheduling change did not modify the frozen manifest, collection order, prompts, model configuration, token ceilings, or any finalized observation.
- The checkpoint successfully finalized:
  - order 64 `API-v2.6-ENT-INT-01-M3-R01`: completed;
  - order 67 `API-v2.6-ENT-INT-02-M3-R01`: completed;
  - order 68 `API-v2.6-ENT-INT-02-M4-R01`: completed;
  - order 70 `API-v2.6-ENT-INT-03-M3-R01`: completed;
  - order 71 `API-v2.6-ENT-INT-03-M4-R01`: completed;
  - order 73 `API-v2.6-ENT-INT-04-M3-R01`: completed.
- Order 74 `API-v2.6-ENT-INT-04-M4-R01` was finalized as failed with collector reason `HTTP 200 response is not a valid chat completion`.
- Preserved response evidence for order 74 shows the underlying Nvidia error was HTTP 503 with `error_type: provider_overloaded` and message `Service temporarily overloaded`.
- Order 74 therefore matches the previously observed recurring M4 infrastructure/provider-overload failure pattern.
- No retry, regeneration, protocol change, or new experiment version was introduced.

### 2026-09-22 — M3 Groq TPM rejection identified at order 83

- Observation `API-v2.6-DATA-ADV-01-M3-R01` (collection order 83) was finalized as failed with `http_status_413`.
- Preserved Groq response evidence identified the underlying error as `rate_limit_exceeded` for tokens per minute (TPM).
- Groq reported service tier `on_demand`, TPM limit `8000`, and requested tokens `65830` for model `openai/gpt-oss-120b`.
- The requested amount is consistent with the frozen M3 high output ceiling plus prompt tokens and indicates a provider/account rate-limit constraint rather than a generated-response failure.
- Order 83 remains preserved once as failed and must not be retried or regenerated.
- The frozen M3 token ceiling must not be reduced mid-experiment merely to fit the current provider TPM limit.
- Pending M3 collection is deferred while Groq account/tier capability is investigated; this does not modify the frozen manifest or finalized observations.

### 2026-09-23 — M3 collection temporarily paused after another Groq HTTP 413

- Restarted the original v2.6 M3 condition for the remaining pending observations.
- The collector exited immediately on another finalized HTTP 413 response.
- No M3 observation remained stranded in `requesting` state, so interruption recovery was not required.
- This follows multiple previously verified Groq TPM/rate-limit failures interspersed with successful M3 completions.
- Decision: temporarily pause M3 collection rather than repeatedly consume pending M3 slots during the current provider/account rate-limit condition.
- Existing completed and failed M3 observations remain preserved unchanged and will not be retried.
- Next step: test one still-pending M2 observation now that OpenRouter paid access is active.

### 2026-09-23 — M2 paid-access gate reached Darkbloom but exhausted output budget in reasoning

- After OpenRouter paid access was activated, the next pending M2 observation `API-v2.6-AUTH-FED-04-M2-R01` (order 15) no longer failed with the previous HTTP 402 affordability error.
- The request was routed to the frozen M2 model/provider condition:
  - model: `qwen/qwen3.8-27b`
  - provider: Darkbloom
- OpenRouter usage evidence reported:
  - prompt tokens: 305
  - completion tokens: 32,768
  - reasoning tokens: 32,767
- The frozen M2 maximum output is 32,768 tokens.
- The model therefore consumed essentially the entire available output budget in reasoning and produced no non-empty assistant content.
- The collector finalized the observation as failed with `HTTP 200 response contains no non-empty assistant content`.
- This failure is not attributable to OpenRouter billing/credit exhaustion.
- Order 15 remains preserved and will not be regenerated.
- No frozen M2 model, provider pin, prompt, or generation setting was changed.
- Next step: test another still-unstarted M2 observation under the unchanged frozen condition before determining whether this is an isolated or recurrent M2 behavior.

### 2026-09-23 — M1 order 62 empty-content failure verified as provider/model error

- Inspected preserved response evidence for `API-v2.6-ENT-INT-01-M1-R01` (order 62).
- OpenRouter routed the request to the frozen M1 condition:
  - model: `cohere/north-mini-code:free`
  - provider: Cohere
- The HTTP response was successful at the transport level but the model response reported:
  - `finish_reason: error`
  - `native_finish_reason: error`
  - assistant `content: null`
  - completion tokens: 3,603
  - reasoning tokens: 3,603
  - generation time: approximately 27.9 seconds
- Because the frozen M1 output ceiling is 64,000 tokens, this failure was not caused by reaching the output-token ceiling.
- The observation remains finalized as failed and will not be retried.
- This establishes a second M1 failure mode distinct from M1 output-ceiling truncation.

### 2026-09-23 — HYBRID interface assignment formalized and verified

- Created the deterministic derived allocation artifact `manifests/hybrid_assignment_v1.0.0.csv`, with one assignment for each of the 360 frozen v2.6 manifest rows. It is an allocation layer and does not replace or modify `manifests/api_final_v2.6.0_manifest.csv`.
- The preserved raw metadata baseline was verified as 119 API-attempted rows: M1 16, M2 6, M3 38, M4 59. This includes failed and truncated observations; interface assignment is not based on successful responses.
- The verified final allocation is M1 40 API / 50 manual, M2 40 / 50, M3 41 / 49, and M4 59 / 31, for totals of 180 API and 180 manual rows.
- All 119 preserved raw observations remain API-assigned. The remaining API assignments are 61 never-attempted rows selected per model in ascending frozen manifest `collection_order`: M1 24, M2 34, M3 3, and M4 0.
- Added `scripts/create_hybrid_assignment_v1_0.py` and `tests/test_hybrid_assignment.py`. The utility verifies unique IDs, unchanged order, target counts, raw-observation preservation, earliest eligible selection, no M4 addition, and the frozen-manifest hash. `python3 scripts/create_hybrid_assignment_v1_0.py --verify` passed; `python3 -m unittest tests/test_hybrid_assignment.py` passed (2 tests).
- The frozen manifest SHA-256 was `b2b2750b3ae4ce96a867df14117b05c12f214760ef7036d6bbf2f78e44939b7f` before derivation and after verification. The derived assignment SHA-256 is `e4b9295b2efc0fe639092161561e915c1d0c47f9a545df2699f7fe12595dd54f`.
- No API request and no manual collection was started by this allocation task. M3 remains paused; the allocation does not alter the frozen M3 configuration or retry policy.

### 2026-09-23 — M1 hybrid automatic collection advanced through seven API-assigned rows

- Continued v2.6 collection through `scripts/collect_hybrid_api_batch.py`, which restricts automatic collection to rows assigned to the API side of the hybrid allocation.
- Seven additional M1 API-assigned observations were finalized:
  - order 72: completed
  - order 75: completed
  - order 78: completed
  - order 81: completed
  - order 88: completed
  - order 91: truncated
  - order 94: failed with `provider_finish_reason_error`
- Outcome for these seven observations:
  - completed: 5
  - truncated: 1
  - failed: 1
- Order 94 remains preserved as failed and will not be retried.
- The M1 hybrid API queue now contains 16 unstarted API-assigned observations, beginning at order 97.
- Decision: continue M1 automatic collection in smaller batches of three because provider/model failures can terminate a larger batch early.

### 2026-09-23 — M3 hybrid automatic allocation fully finalized

- Completed the remaining three M3 API-assigned observations through `scripts/collect_hybrid_api_batch.py`.
- Final outcomes:
  - order 154 `API-v2.6-PKI-CRYPTO-04-M3-R02`: completed
  - order 157 `API-v2.6-PKI-CRYPTO-05-M3-R02`: completed
  - order 164 `API-v2.6-DOC-BINARY-01-M3-R02`: failed with HTTP 413
- The M3 hybrid API queue is now empty.
- M3 has therefore reached its hybrid automatic target of 41 finalized API-assigned positions.
- Order 164 remains preserved as failed and will not be retried.
- Next automatic collection priority: finish the remaining M1 API-assigned observations, followed by M2.

### 2026-09-24 — M1 hybrid automatic allocation fully finalized

- Completed all M1 positions assigned to automatic API collection under the hybrid v2.6 workflow.
- Final M1 API outcomes:
  - completed: 27
  - truncated: 10
  - failed: 3
  - finalized total: 40
- The M1 hybrid API queue is empty.
- All truncated and failed observations remain preserved and were not regenerated.
- M1 has therefore reached its hybrid automatic target of 40 finalized API-assigned observations.
- Next automatic collection target: M2.

### 2026-09-25 — M2 removed; v2.7.0 three-model final study frozen and verified

- Supersedes the "Next automatic collection target: M2" note in the 2026-09-24 entry. No further M2 collection is planned for the final study.
- Completed the M2 removal impact audit (`docs/m2_removal_final_study_impact_audit.md`) and recorded decision D036 in `docs/decision_log.md`.
- Created v2.7.0 (freeze timestamp `2026-09-24T23:22:58.369305Z`; commit `bba890d`; `v2.7.0-freeze` tag pending researcher review). v2.7.0 is now the active final study.
- Final design: the v2.6 manifest minus every M2 row, giving 30 tasks × 3 model conditions (M1, M3, M4) × 3 repetitions = 270 planned observations, 90 per retained model. M2 rows in the v2.7 manifest: 0. Condition IDs are not renumbered.
- Interface assignment is inherited unchanged from `hybrid_assignment_v1.0.0.csv`: 140 API / 130 manual (M1 40/50, M3 41/49, M4 59/31). No row was reassigned or rebalanced.
- Exclusion rationale is operational: the M2 automatic API route (`qwen/qwen3.8-27b` via Darkbloom-only OpenRouter) could not complete the intended protocol consistently. The exclusion occurred after partial M2 collection (11 of 90 rows attempted) and before final analysis. No extraction/classification output existed that could have motivated it.
- Provenance reuse: the 140 retained M1/M3/M4 API observations are mapped in place to their existing v2.6 raw evidence by run ID and SHA-256 in `data/final/collection_state_v2.7.0.json`. Nothing was copied, renamed, or regenerated.
- Preservation: all v2.6 inputs, the v2.6 state, the HYBRID assignment, and all 11 M2 raw directories remain unchanged as historical evidence. The 11 M2 directories are hash-listed in the v2.7 freeze.
- Initial v2.7 collection-state snapshot (collection state only, not results):
  - M1: 27 completed / 10 truncated / 3 failed; 50 manual pending
  - M3: 36 completed / 0 truncated / 5 failed; 49 manual pending
  - M4: 42 completed / 6 truncated / 11 failed; 31 manual pending
  - 130 manual rows pending in total
- Validation: full suite `python3 -m unittest discover -s tests` passed 164 tests, 0 failed. The v2.7 and v2.6 freeze `--check` runs and the HYBRID `--verify` run passed. Details are in `docs/final_study_v2.7_migration_verification.md`.
- Remaining blockers:
  - manual interface configuration approval (D035) before any of the 130 manual rows can be collected;
  - an approved mechanism to update/advance the v2.7 collection state once manual capture begins;
  - collection scripts (`collect_hybrid_manual.py`, `collect_hybrid_api_batch.py`) are still v2.6-oriented and pin the v2.6 manifest and assignment.

### 2026-09-25 — v2.7.0 final-study freeze established

- Created annotated Git tag `v2.7.0-freeze`.
- Freeze tag points to commit:
  `bba890d9aa5838f06bee4b1bd0e85d9e61b444f8`
  (`experiment: establish final v2.7 three-model study`).
- The frozen final study contains model conditions M1, M3, and M4 only.
- Final planned design:
  - 30 frozen tasks
  - 6 functional categories
  - 3 retained model conditions
  - 3 planned repetitions
  - 270 planned observations
  - 140 API-assigned observations
  - 130 manual-assigned observations
- M2 has zero rows in the v2.7 final-study manifest. Historical M2 evidence remains preserved under the superseded v2.6 study.
- Verified freeze hashes:
  - task set: `ef0aff59f8a3934f65379d34036848652b7b5593f595ffa4b449a15af021546b`
  - prompt template: `8d3971d6f9f86dfd98a4b5c49c0c13d734b7f650744da682225195f2ea49b528`
  - model set: `247eec71556f2908630ec8e4d34fc5ac54a29fcf5c47cb7406dafcd67991235c`
  - v2.7 manifest: `2edf2638f08a1079aadd02c174951a912aa2797b56df36997878096b29a4ed20`
  - freeze JSON: `f6fbb15192dee3d5744bc15890c0df81615e3c70ea76a41d9dbfbe7cb27bcfc5`
- Freeze validation passed:
  - v2.7 tests: 12/12
  - existing v2.6/hybrid tests: 32/32
  - full suite: 164/164
- Freeze verification documented in `docs/v2.7_freeze_tag_verification.md` and committed as `1c8fd9b`.
- No v2.6 frozen experiment input was modified by establishing the v2.7 freeze.
- Outstanding collection-state issue: `data/final/api_batch_state_v2.6.0.json` remains an uncommitted working-tree modification and requires a separate provenance/checkpoint decision before it is staged or changed.
- Next report task: reconcile Chapters 1–3 with the frozen v2.7 three-model methodology before final report assembly.

### 2026-09-25 — Final v2.7 data collection complete; provenance checkpoint

- Final v2.7 data collection is complete. All 270 assigned observations have terminal evidence. These are collection-state counts only, not results.
  - API (140): 105 completed, 16 truncated, 19 failed, 0 pending. By model: M1 27/10/3, M3 36/0/5, M4 42/6/11. Failed and truncated rows are final under the freeze policy: no retry and no regeneration.
  - Manual (130): M1 50, M3 49, M4 31, all `response_status=completed`. They are tracked on `origin/collection/m1-manual-v2.6` @ `1e06280`, `origin/collection/m3-manual-v2.6` @ `ee952dc` and `origin/collection/m4-manual-v2.6` @ `fb0d56a`, which are not yet merged. All 130 rows had already been verified against the frozen v2.7 manifest (`docs/final_v2.7_consolidation_preflight.md` §2).
  - M2 rows among the final-study observations: 0.
- Checkpointed `data/final/api_batch_state_v2.6.0.json` unchanged at SHA-256 `1a3af56d138d3da1c3e67c1f04f55b27e4ab5d0ec786ab31d7c2cd17cb6b695c`. This exactly matches `source_v2_6_state_snapshot.sha256` in the frozen `collection_state_v2.7.0.json`. The difference from the previous commit is append-only: 1,008 → 1,073 events, plus the collector's `updated_at_utc`/pacing fields. This resolves the outstanding collection-state issue noted in the previous entry.
- Recorded D043: raw API evidence stays gitignored and is protected by `reports/final_v2.7_raw_evidence_inventory.sha256`, which covers 1,552 files in 229 run directories, 46,240,449 bytes, and has inventory SHA-256 `1f79cdecbd573b57f5121dc04fcd5e3aadcca8d46d005cebf4628a8fa75634e7`. The evidence is to be copied byte-for-byte into the canonical final worktree and reverified there. Breakdown: `reports/final_v2.7_raw_evidence_summary.md`.
- Timing provenance: 85 manual captures (M1 36, M3 49) predate the v2.7 freeze timestamp `2026-09-24T23:22:58.369305Z`, and 45 (M1 14, M4 31) postdate it. The 85 were reused as compatible retained v2.6 evidence without regeneration, not produced by a new v2.7 collection event. Details: `reports/final_v2.7_manual_timing_provenance.md`.
- Verification: `v2.7.0-freeze` → `bba890d9aa5838f06bee4b1bd0e85d9e61b444f8`. All 39 frozen v2.7 input hashes match, and `create_experiment_freeze_v2_7.py --check` passes. All 140 API evidence directories hash-match the frozen state. Raw evidence verifies against the inventory, and no raw evidence is Git-tracked.
- Next: consolidation into the canonical final worktree (`docs/final_v2.7_consolidation_preflight.md`), an append-only derived record of manual completion, and a v2.7-aware analysis pipeline.

### 2026-09-25 — fake-auth provenance audit completed; accidental npm dependency removed

- Completed the provenance audit of `fake-auth@0.1.7` (`docs/fake_auth_dependency_provenance_audit.md`, re-verified in its §9). It confirms an accidental development-time install, first made on 2026-09-21T04:31:02Z and tracked in `5333f9e`. The package did not come from any AI-generated experimental response.
- The package was not used for registry validation or any other experimental purpose, and its code was never executed by the research pipeline or the tests.
- Recorded D044. The tracked accidental manifests `package.json` and `package-lock.json` were removed with `git rm`. The history is preserved as evidence. The local, gitignored `node_modules/` in this worktree was deleted as environment cleanup only. The analysis worktree is untouched.
- The PIPE-03 test string that contains `fake-auth` is unchanged.
- Experiment evidence and frozen inputs are unchanged. This resolves the `RESEARCHER_DECISION_REQUIRED` item in preflight §8 for the study worktree.

### 2026-09-25 — M3 manual collection completed

- Completed the manual-assigned portion of the frozen v2.6 M3 condition: 49/49 manual observations are now captured under `data/final/manual_raw/v2.6.0/`.
- The recorded model is `openai/gpt-oss-120b`, and all 49 M3 manual metadata files record the actual interface as `Groq Playground web UI`.
- Verified that all 49 M3 manual `response.md` files are non-empty.
- `scripts/collect_hybrid_manual.py --model M3 --show-next --dry-run` reports `FAIL: no unobserved manual-assigned rows remain`, confirming that the M3 manual allocation is exhausted.
- The completed M3 manual collection is recorded on branch `collection/m3-manual-v2.6`; completion commit: `4ae8344` (`data: complete M3 manual collection`).
- Frozen experiment inputs and the HYBRID assignment were not modified during manual capture. Raw responses remain preserved as captured without whitespace normalization or response-content editing.
- Next step: validate and integrate the completed M3 collection with the broader v2.6 experiment state without modifying frozen prompts, manifests, assignments, or raw observations.

### 2026-09-25 — M1 manual collection completed

- Completed the manual-assigned portion of the frozen v2.6 M1 condition: 50/50 manual observations are now captured under `data/final/manual_raw/v2.6.0/`.
- The recorded M1 model is `cohere/north-mini-code:free`, and all 50 M1 manual metadata files record the actual interface as `OpenRouter Chatroom web UI`.
- Verification confirmed:
  - 50 M1 observation directories;
  - 0 missing `response.md` files;
  - 0 empty `response.md` files;
  - 0 missing `metadata.json` files;
  - 0 incorrect `actual_model` values;
  - 0 incorrect `actual_interface` values.
- `scripts/collect_hybrid_manual.py --model M1 --show-next --dry-run` reports `FAIL: no unobserved manual-assigned rows remain`, confirming that the M1 manual allocation is exhausted.
- The completed M1 manual collection is recorded on branch `collection/m1-manual-v2.6`.
- Completion commit: `d68460e6b1ea9c4737b5a519c11113990768446a` (`data: complete M1 manual collection`).
- Exactly 150 files were committed for the 50 observations, corresponding to the preserved `metadata.json`, `prompt.txt`, and `response.md` artifacts.
- Frozen experiment inputs and the HYBRID assignment were not modified during M1 manual capture. Raw responses remain preserved as captured without response-content editing or whitespace normalization.
- Next step: integrate and validate M1 alongside the other completed/finalizing v2.6 model conditions before downstream response inventory, scoring, and statistical analysis.

### 2026-09-25 — M4 manual collection completed

- Completed the manual-assigned portion of the frozen v2.6 M4 condition: 31/31 manual observations are now captured under `data/final/manual_raw/v2.6.0/`.
- The recorded M4 model is `nvidia/nemotron-3-ultra-550b-a55b:free`, and all 31 M4 manual metadata files record the actual interface as `OpenRouter Chatroom web UI`.
- Verification confirmed:
  - 31 M4 observation directories;
  - 0 missing `response.md` files;
  - 0 empty `response.md` files;
  - 0 missing `metadata.json` files;
  - 0 incorrect `actual_model` values;
  - 0 incorrect `actual_interface` values.
- `scripts/collect_hybrid_manual.py --model M4 --show-next --dry-run` reports `FAIL: no unobserved manual-assigned rows remain`, confirming that the M4 manual allocation is exhausted.
- The completed M4 manual collection is recorded on branch `collection/m4-manual-v2.6`.
- Completion commit: `44d3e24b4f19b34cd68d8389dd85375ad5c1700e` (`data: complete M4 manual collection`).
- Exactly 93 files were committed for the 31 observations, corresponding to the preserved `metadata.json`, `prompt.txt`, and `response.md` artifacts.
- Frozen experiment inputs and the HYBRID assignment were not modified during M4 manual capture. Raw responses remain preserved as captured without response-content editing or whitespace normalization.
- Next step: integrate and validate M4 alongside the other completed v2.6 model conditions before downstream response inventory, scoring, and statistical analysis.

### 2026-09-22 — accidental collection in analysis workspace quarantined and blocked

- An API collection command was accidentally run from the analysis repository instead of the official study repository.
- The accidental analysis-repo run created:
  - `API-v2.6-AUTH-FED-01-M1-R01` as `failed` with `transport_failure`;
  - `API-v2.6-AUTH-FED-01-M3-R01` as a completed duplicate generation.
- The M3 accidental run used the same request hash as the official study-repo observation but produced a different provider response ID and different response hash, confirming that it was a second live generation for the same planned observation.
- The official dataset remains exclusively under `~/Dev/ai-hallucination-study/data/final/raw/`.
- The accidental analysis-repo artifacts were removed from the active `data/final/raw/` location and preserved under `data/quarantine/accidental_v2.6_collection_2026-09-22/`.
- The tracked `data/final/api_batch_state_v2.6.0.json` was restored to its pre-accident Git version.
- Active analysis-repo `data/final/raw/` contains no `API-v2.6-*` directories.
- Quarantined evidence is excluded from SHR, PHR, package validation, classification, risk-model inputs, and all final analysis.
- Quarantine hashes were preserved; the `SHA256SUMS.txt` file contains a self-referential checksum entry and should not be treated as validating itself, while the individual evidence-file hashes were verified.
- A hard sentinel-based repository guard was added so all 10 collection CLI entry points refuse to run in this analysis repository.
- The guard aborts before network/provider calls, raw-directory creation, and collection-state mutation.
- Guard implementation committed as `fa01ad4` (`Block live collection in analysis repository`).
- Repository-guard tests passed 25/25 before the final init-guard extension; after extension the full suite ran 179 tests with no new failures. Two historical freeze tests remain failing because gitignored historical raw artifacts are absent from this worktree; these failures pre-existed the guard work and are unrelated.
- Two legacy initializer tests currently pass because the new CLI guard intercepts before the logic named by those tests; this is a testing-quality caveat for later cleanup, not a collection-safety failure.

### PIPE-06 — risk-scoring infrastructure implemented

- Implemented deterministic risk-scoring infrastructure for the frozen `risk-model-1.0.0` protocol in `docs/risk_assessment_protocol.md`.
- Model uses:
  - Impact 1-5;
  - Detectability 1-4;
  - risk score = Impact x Detectability;
  - LOW 1-4;
  - MODERATE 5-8;
  - HIGH 9-14;
  - CRITICAL 15-20.
- `security_sensitive_context` is recorded separately and does not change the numeric score.
- Only eligible, resolved hallucination findings are scoreable; ineligible or evidence-unresolved findings retain null score/band, never zero.
- Created:
  - `scripts/score_risk_findings.py`
  - `schemas/risk_finding_pipe06_v1.schema.json`
  - `tests/test_score_risk_findings.py`
- 24/24 new risk-model tests passed using synthetic fixtures only.
- No real finding was scored.
- No PHR, SHR, prevalence, comparison, or real risk result was calculated.
- No collection/raw/state file was modified by this implementation.
- The broader suite (179 tests) still contains the same two pre-existing, unrelated `test_api_freeze.py` failures noted above; do not attribute those to PIPE-06.

### PIPE-07 — derived analysis-dataset builder implemented

- Implemented a version-agnostic derived analysis-dataset builder (`scripts/build_analysis_dataset.py`) that joins the response inventory, PIPE-03 unique package-per-response records, PIPE-04 joined registry evidence, and PIPE-05 joined research classification into two reusable datasets: package/response-level (one row per `(run_id, normalized_package)`) and response-level (one row per planned manifest run, including pending/failed/truncated rows with zero counts).
- The primary package-level unit is one unique normalized package per response, `(run_id, normalized_package)`, per decision D033. Occurrence-level provenance (`occurrence_count`, `source_types`) is preserved on each row but never inflates a count on its own.
- Primary metric eligibility uses `collection_status == "completed"` (completed, non-truncated responses only), per decision D033 and the frozen truncation-exclusion rule.
- Created: `scripts/build_analysis_dataset.py`, `schemas/package_response_analysis_pipe07_v1.schema.json`, `schemas/response_level_analysis_pipe07_v1.schema.json`, `tests/test_build_analysis_dataset.py`.
- 21/21 new PIPE-07 tests passed using synthetic fixtures only.
- Verified exact broader-suite result after adding PIPE-07: 200 tests run, 198 passed, 2 failed, 0 errors. The 2 failures are the same pre-existing, unrelated `test_api_freeze.py` cases (`test_freeze_record_v2_1_historical_context_and_preserved_observations`, `test_freeze_record_v2_3_hashes_and_zero_observations`), both `AssertionError` from historical v2.1/v2.3 raw artifact directories being absent (gitignored) from this worktree; neither failure is caused by or related to PIPE-06 or PIPE-07.
- An attempted v2.2 dry validation failed safely: this analysis worktree lacks the physical v2.2 raw response files that the existing `results/*_v2.2.0.json` derived snapshots were built from, so a freshly regenerated v2.2 response inventory (360/360 pending) disagreed with those 97-row snapshots. The builder's fail-safe cross-validation caught this and refused to write output rather than generating an inconsistent dataset; no PHR/SHR/result metric was calculated.
- Final use of this builder will be against provenance-consistent v2.6-derived inputs (a response inventory and PIPE-03/04/05 outputs all built from the same v2.6 collection snapshot) once v2.6 collection is sufficiently complete.

### DESIGN/SIGNAL-01 — v2.6 prompt-to-analysis alignment audit completed

- The frozen v2.6 design was audited read-only against the implemented extraction and classification pipeline.
- All 30/30 tasks are dependency-intensive and require complete package.json output with exact dependencies and documented API usage.
- Package selection is model-selected rather than pre-specified; no task names a specific npm package for the model to reuse.
- No prompt-level anti-dependency or anti-hallucination wording was found that would structurally suppress package-name hallucination opportunities.
- Current v2.6 signal snapshot at audit time:
  - 25 completed non-truncated responses;
  - 3 truncated responses;
  - 6 failed;
  - 1 requesting;
  - 325 pending;
  - all 28 completed/truncated responses contained at least one explicit external package reference;
  - 576 occurrence records;
  - 292 unique `(run_id, normalized_package)` rows;
  - 87 distinct normalized package names.
- Current source-type mix: package_json 339, es_import 216, require 18, dynamic_import 3, npm_install 0.
- Extractor coverage was adequate for all package-reference forms observed in the current v2.6 sample.
- Theoretical gaps noted: `export ... from` re-export syntax, yarn/pnpm install syntax, and `require.resolve`; none were observed in the current sample.
- Narrative-only package claims remain intentionally out of scope under the existing taxonomy.
- Current model/category coverage is incomplete because collection is still in progress.
- Audit conclusion: ADEQUATE WITH DOCUMENTED LIMITATIONS.
- A future zero confirmed package-hallucination count would remain interpretable if package-opportunity density and extraction coverage remain comparable through the completed experiment.
- No frozen prompt, manifest, raw response, state, or analysis file was modified.

### PIPE-08 — primary PHR/SHR metric calculator implemented

- Implemented version-agnostic `scripts/calculate_primary_metrics.py`.
- Created `schemas/primary_metrics_pipe08_v1.schema.json`.
- Added `tests/test_calculate_primary_metrics.py`.
- PHR follows D033: confirmed package-name hallucination rows / all metric-eligible unique `(run_id, normalized_package)` rows.
- Repeated occurrences of the same package in one response cannot inflate PHR.
- SHR follows D033: eligible responses containing >=1 confirmed package-name hallucination / all metric-eligible responses.
- Completed zero-package responses remain in the SHR denominator.
- Truncated responses are excluded through the PIPE-07 `metric_eligible` field, not a recomputed rule.
- Zero denominator produces null rate, never zero.
- Ambiguous/unresolved/non-hallucination classifications do not enter the numerator.
- The calculator independently cross-checks the package and response datasets and fails on inconsistent provenance/counts rather than repairing them.
- 27/27 PIPE-08 tests passed using synthetic fixtures only.
- Full suite: 227 run, 225 passed, 2 failed — the same pre-existing, unrelated `test_api_freeze.py` failures documented above; not caused by PIPE-08.
- No real PHR, SHR, model comparison, or v2.6 result was calculated.
- First real run must use provenance-consistent v2.6 PIPE-07 outputs.

### Secondary dependency-reliability analysis planned

- Decided to retain the frozen primary package-hallucination methodology unchanged:
  confirmed package-name hallucinations remain the basis for primary PHR/SHR.
- A secondary dependency-reliability analysis will be added to examine
  `REVIEW_REQUIRED` package recommendations without reclassifying them automatically
  as hallucinations or failures.
- Planned workflow:
  1. calculate review-required package/response screening counts;
  2. implement PIPE-05B manual evidence-based adjudication;
  3. freeze a secondary dependency-error taxonomy only after reviewing real cases;
  4. implement secondary package-level and response-level reliability metrics;
  5. use selected adjudicated cases for qualitative analysis.
- The secondary analysis must remain separate from the frozen primary hallucination
  outcome and must not alter v2.6 prompts, manifest, collection state, PHR, or SHR.
- No secondary failure metric has yet been finalized or calculated.

### PIPE-05B — REVIEW_REQUIRED adjudication infrastructure implemented

- Implemented `scripts/adjudicate_review_required_packages.py`, a conservative, evidence-based secondary adjudication tool for PIPE-05 rows already marked `AMBIGUOUS`/`REVIEW_REQUIRED`.
- Taxonomy: `CONFIRMED_HALLUCINATION`, `LEGACY_OR_REMOVED`, `NAMESPACE_CONFUSION`, `PACKAGE_NAME_CONFUSION`, `INVALID_OR_REDUNDANT_TYPES_PACKAGE`, `ECOSYSTEM_CONFUSION`, `OTHER_DEPENDENCY_ERROR`, `UNRESOLVED`; `dependency_failure` is tracked independently of `confirmed_package_hallucination`.
- Reads an existing PIPE-05 joined classification envelope read-only; writes a separate PIPE-05B adjudication output. It does not modify PIPE-05 outputs, PHR, or SHR.
- Created `scripts/adjudicate_review_required_packages.py`, `schemas/package_adjudication_pipe05b_v1.schema.json`, and `tests/test_adjudicate_review_required_packages.py`.
- 22/22 new PIPE-05B tests passed using synthetic fixtures only; full suite 287 run, 285 passed, with 2 pre-existing unrelated `test_api_freeze.py` failures.
- No real `REVIEW_REQUIRED` package was adjudicated; this milestone covers infrastructure only.

### 2026-09-22 — PIPE-05B.1 — self-reference/local package adjudication outcome added

- Added `SELF_REFERENCE_OR_LOCAL_PACKAGE` to `scripts/adjudicate_review_required_packages.py` and `schemas/package_adjudication_pipe05b_v1.schema.json`; adjudicator/schema version is now `pipe-05b-adjudicator-1.1.0`.
- The outcome requires response-internal evidence (`self_reference_evidence`: the generated project's own package name or a generated local/workspace package, with declaration and reference locations).
- It always records `dependency_failure=false`, `confirmed_package_hallucination=false`, and `external_dependency_eligible=false`.
- 29/29 PIPE-05B tests passed using synthetic fixtures only; full suite 294 run, 292 passed, with the same 2 pre-existing unrelated `test_api_freeze.py` failures.
- No real package was adjudicated.
- Decision D034 resolves primary-vs-secondary denominator handling: D033 primary PHR and primary SHR are unchanged; adjudicated self/local references are excluded only from a separately labelled secondary/exploratory external-dependency sensitivity analysis, and `external_dependency_eligible=null` rows are reported separately.

### PIPE-09 — grouped descriptive and statistical-comparison infrastructure implemented

- Implemented `scripts/analyze_group_comparisons.py`, reusing the validated PIPE-07/08 package-response and response-level analysis units.
- Grouped descriptive summaries support `model_condition_id`, `category`, `repetition`, and `model_condition_id × category`.
- Statistical comparison support includes Fisher's exact test for 2×2 comparisons, assumption-gated Pearson chi-square or deterministic seeded Monte Carlo handling for sparse 2×C tables, and Holm-Bonferroni-corrected pairwise Fisher comparisons.
- Two-group comparisons report odds ratio and risk/rate difference with 95% confidence intervals.
- Sparse, zero-event, zero-total, and single-group cases are handled with explicit boundary or `not_testable` outputs rather than fabricated significance.
- No ranking, best/worst, or winner output is produced.
- 26/26 PIPE-09 tests passed using synthetic fixtures only.
- No final v2.6 inferential comparison or model ranking has been produced; final use requires a provenance-consistent final v2.6 analysis dataset.

### 2026-09-22 — STATUS-AUDIT-01 and D035: provider error finish reason reclassified as failed

- STATUS-AUDIT-01 found `API-v2.6-AUTH-FED-04-M4-R01` recorded as completed/`COMPLETED`/metric-eligible although the provider returned HTTP 200 with `finish_reason: "error"`. It used 7,599 of 65,536 permitted completion tokens (no output-ceiling truncation), and `response.md` ends mid-identifier. Cause: the collector's `length`-else-`completed` mapping.
- Decision D035 (`docs/decision_log.md`): `stop` → completed; `length` → truncated; any other provider finish reason, including `error`, → failed/`FAILED`, even with partial content. Failed observations are preserved once, not regenerated, and not primary-metric eligible.
- Correction implemented as a derived inventory overlay (`scripts/build_response_inventory.py`; new inventory fields `raw_collection_status`, `provider_finish_reason`, `status_correction = "D035"`; schema updated). Raw `metadata.json`/`response.md` were not modified, and the run was not regenerated.
- Collector hardened in this repository (`scripts/collect_api_run.py`): abnormal finish reasons are preserved as failed with `failure_reason: provider_finish_reason_<value>`. The same patch is **not yet applied** to the official collection repository `~/Dev/ai-hallucination-study`.
- PIPE-03/PIPE-07 handling (approach A): failed responses are not extracted; PIPE-07 keeps an ineligible response-level row and rejects stale package rows for failed runs.
- Tests: 14 new tests (collector 3, inventory 9, PIPE-07 2); full suite 308 run, 306 passed, with the same 2 pre-existing unrelated `test_api_freeze.py` failures.
- Read-only live scan of all 60 v2.6 run directories on 2026-09-22 UTC: `API-v2.6-AUTH-FED-04-M4-R01` is the only observation recorded completed/truncated with a finish reason other than `stop`/`length`. The other 11 non-`stop`/`length` directories carry no finish reason: 10 are already `failed` before a response was parsed, and 1 (`API-v2.6-DATA-ADV-01-M4-R01`) is `requesting`.
- Screening recompute on the same checkpoint `/tmp/v2.6_screening_checkpoint_20260922T161227Z` (outputs in `/tmp/v2.6_screening_d035_20260922T190815Z`, not in the repository). Inventory, PIPE-03, and PIPE-07 were rerun. PIPE-04/05 joined evidence is the preserved pre-D035 screening evidence with only this run's rows removed; no registry request was made. The rebuilt PIPE-03 output equals the earlier output minus this run's 18 unique rows / 26 occurrences, and every other row is unchanged.

**INTERIM DESCRIPTIVE SCREENING — NOT FINAL RESEARCH RESULT** (49 of 360 v2.6 observations at the checkpoint; no real adjudication performed)

| Count | Pre-D035 | D035-corrected |
|---|---:|---:|
| Completed responses | 35 | 34 |
| Truncated responses | 6 | 6 |
| Failed responses | 8 | 9 |
| Eligible package-response rows | 350 | 332 |
| Eligible `REVIEW_REQUIRED` package rows | 5 | 4 |
| Eligible responses | 35 | 34 |
| Eligible responses with ≥1 `REVIEW_REQUIRED` package | 5 | 4 |

### POST-D035-LIVE-AUDIT-01 — live collector deployment verified

- The D035 collector patch is present in `~/Dev/ai-hallucination-study`: `stop` → completed/`COMPLETED`, `length` → truncated/`TRUNCATED`, and every other finish reason → failed/`FAILED`.
- The live collector's focused test suite passed 27/27.
- A read-only scan covered 79 current v2.6 raw metadata records: 58 completed, 9 truncated, 11 failed, and 1 requesting; 281 of 360 manifest rows had no raw metadata yet.
- Exactly one present abnormal finish reason was found: `API-v2.6-AUTH-FED-04-M4-R01`, raw completed/`COMPLETED` with `finish_reason="error"`. D035 analytically reclassifies it as failed/`FAILED`/metric-ineligible; it was not regenerated and its stored artifacts matched their recorded hashes.
- Among observations collected after `2026-09-22T16:10:32Z`, no additional completed observation had an abnormal present finish reason; therefore no additional D035 analytical corrections were identified at this audit snapshot.
- The audit modified no raw observation, collection state, manifest, prompt, configuration, or pacing rule.

### 2026-09-23 — PIPE-05C-PROV-01 — reproducible provenance archived for first real adjudication

- Archived a permanent non-frozen derived evidence snapshot at `data/derived_checkpoints/interim_val_01b_20260922T112234Z/` for `API-v2.6-PKI-CRYPTO-02-M4-R01` / `mtls-pfx-loader`.
- Verified the original PIPE-05 joined source SHA-256 `2f5796d4d0ea06ee868a3602fb79eda87e0c39b3ea0d6ae6f2ce10c6a28256eb` and target response SHA-256 `6d2fbae0d09dd7463cacf9c386c48b829453729bf103638d011a82450f6764be`.
- The snapshot contains the minimum provenance required to reproduce the adjudication, including the PIPE-05 source envelope, relevant PIPE-03/04/inventory evidence, the target response, a SHA-256 manifest, and provenance documentation.
- Reproduced the PIPE-05B adjudication from the permanent snapshot. The outcome remained `SELF_REFERENCE_OR_LOCAL_PACKAGE`, with `dependency_failure=false`, `confirmed_package_hallucination=false`, `external_dependency_eligible=false`, and `installation_impact=not_applicable_local_reference`.
- PIPE-05B focused tests passed 29/29 and the reproduced output satisfied the PIPE-05B schema contract.
- No raw/frozen experiment data, manifests, prompts, quarantine data, collection state, or `/tmp` source files were modified.
- Historical checkpoint-b PHR `0/309` and SHR `0/31` predate D035 and must not be used as current or final metrics.

### 2026-09-23 — PIPE-05C-FINAL-01 — remaining three interim REVIEW_REQUIRED rows adjudicated

- Adjudicated, from permanent derived snapshot `data/derived_checkpoints/interim_val_01b_20260922T112234Z_pipe05c-final-01/`:
  - `API-v2.6-DOC-BINARY-02-M4-R01` / `@xmldom/xpath` → `NAMESPACE_CONFUSION`
  - `API-v2.6-PKI-CRYPTO-02-M1-R01` / `pkcs12` → `PACKAGE_NAME_CONFUSION`
  - `API-v2.6-PKI-CRYPTO-03-M4-R01` / `mime-node` → `PACKAGE_NAME_CONFUSION`
- All three have `dependency_failure=true`, `confirmed_package_hallucination=false`, `external_dependency_eligible=true`, `installation_impact=would_fail_install`, and `checks.historical=inconclusive`.
- No evidence of historical existence was found with the sources checked; this is not treated as proof that the exact package names never existed. Classification rests on positive evidence of the legitimate package/module relationship.
- PIPE-05 source SHA-256: `2f5796d4d0ea06ee868a3602fb79eda87e0c39b3ea0d6ae6f2ce10c6a28256eb`.
- Output: `results/pipe05b_adjudication_interim-v2.6-checkpoint-b_pipe05c-final-01_20260923T034600Z/`; JSON SHA-256 `33e5e28c381b910e4fa6f946158d77ecac40c6502d87aafe9eeffaa01fd2749a`.
- Reproduction from the permanent snapshot was byte-identical; PIPE-05B focused tests passed 29/29.
- All four metric-eligible interim REVIEW_REQUIRED rows are now adjudicated: 3 eligible external dependency failures, 1 excluded self-reference, 0 unresolved, and 0 confirmed package hallucinations.
- D033 primary PHR/SHR definitions remain unchanged.
- No raw/frozen data, manifests, prompts, quarantine data, or collection state were modified.
- INTERIM — NOT FINAL RESEARCH RESULT.

### 2026-09-23 — D037 primary confirmed-hallucination routing defined (no metrics calculated)

- Accepted decision D037 (`docs/decision_log.md`): a metric-eligible unique `(run_id, normalized_package)` row counts in the primary PHR numerator, and its response in the primary SHR numerator, when confirmed as `CONFIRMED_HALLUCINATION` through exactly one authorized path: PIPE-05 `REVIEWED`, or a guarded PIPE-05B `CONFIRMED_HALLUCINATION` on a PIPE-05 `REVIEW_REQUIRED` row. PIPE-07 is the single resolution point.
- A key present on both paths (even if they agree), unmatched PIPE-05B records, provenance-hash disagreement, guard failures, unsupported versions, or `source_truncated` mismatches fail closed. The PIPE-05B input must be supplied explicitly or explicitly declared absent.
- PIPE-05 `research_classification` is not rewritten. D033 PHR/SHR units and denominators, zero-package handling, metric eligibility, D021, D035, and D034 are unchanged. D036 remains PROPOSED and is not affected.
- Supersedes prospectively, for `CONFIRMED_HALLUCINATION` only, earlier statements that PIPE-05B never contributes to PHR/SHR. Earlier entries are preserved.
- Interim effect: none. The four real PIPE-05B adjudications include no `CONFIRMED_HALLUCINATION`, and no PIPE-05 `REVIEWED` rows exist in the archived checkpoints. Earlier interim figures are not rewritten.
- Definition only: no code changed, no PHR/SHR calculated. No raw/frozen data, manifests, prompts, quarantine data, results, or collection state were modified.

### 2026-09-23 — D036 secondary dependency-reliability metrics defined (no rates calculated)

- Accepted decision D036 (`docs/decision_log.md`), secondary/exploratory: Dependency Failure Rate (DFR; unit = metric-eligible unique `(run_id, normalized_package)` row) and Response Dependency Failure Rate (RDFR; unit = metric-eligible completed response, same eligibility as D033 SHR).
- Construct: exact-name npm dependency-resolution failure under the defined adjudication rules. It excludes wrong-but-existing packages, version-resolution errors, API errors, capability mismatches, and functional-unsuitability errors.
- `AUTO_VALID` rows enter the DFR denominator as non-failures. Adjudicated external failures enter the numerator and denominator. Self/local references are excluded. Undetermined rows (PIPE-05B `UNRESOLVED`, unadjudicated `REVIEW_REQUIRED`, registry-unresolved, PIPE-05 reviewed `AMBIGUOUS`) are excluded from point estimates, counted by reason, and bounded.
- Zero-package and self/local-only responses remain in the RDFR denominator as NEGATIVE. INDETERMINATE responses are excluded from the point estimate and bounded. A response with any external failure is POSITIVE.
- FINAL labelling requires zero unadjudicated `REVIEW_REQUIRED` rows and zero registry-unresolved rows.
- Truncated (D021) and failed (D035) responses remain excluded. D033 primary PHR/SHR and the finalized D037 confirmation routing are unchanged. D034 is clarified: `AUTO_VALID` rows are deterministic external non-failures; its treatment of adjudicated rows is unchanged.
- Definition only: no DFR, RDFR, PHR, or SHR has been calculated, and no calculator exists. The four interim PIPE-05B adjudications are not a denominator.
- No code, schemas, tests, results, raw/frozen data, manifests, prompts, quarantine data, or collection state were modified.

### 2026-09-23 — D037 implemented and D036/PIPE-10 secondary metric infrastructure completed

- Implemented finalized D037 primary-confirmation routing in PIPE-07. PIPE-07 is now the single resolution point for `primary_confirmed_hallucination`, with explicit PIPE-05B or explicit no-PIPE-05B input modes, conservative confirmation guards, per-row provenance, and fail-closed integrity checks.
- PIPE-08 and PIPE-09 now consume the D037-resolved confirmation fields rather than relying only on raw PIPE-05 classification.
- D033 primary PHR/SHR units, denominators, metric eligibility, zero-package response handling, D021 truncation handling, and D035 failed-response handling remain unchanged.
- Added PIPE-10 (`scripts/calculate_dependency_reliability_metrics.py`) implementing finalized D036 secondary/exploratory Dependency Failure Rate (DFR) and Response Dependency Failure Rate (RDFR), including external/non-external/undetermined resolution, uncertainty bounds, descriptive Wilson intervals, completeness gating, required counts, and denominator invariants.
- Version updates: PIPE-07 `1.1.0`, PIPE-08 `1.1.0`, PIPE-09 `1.1.0`, and new PIPE-10 `1.0.0`.
- D037-focused PIPE-07/08/09 tests passed 78/78. PIPE-10 focused tests passed 6/6.
- Full suite: 316 tests run, 314 passed; the 2 failures are the previously known historical freeze tests caused by missing v2.1/v2.3 raw fixtures in this worktree.
- No real v2.6 PHR, SHR, DFR, or RDFR was calculated. No raw/frozen data, manifests, prompts, collection state, quarantine data, or existing result outputs were modified.
- Remaining validation item before real metrics: expand negative/fail-closed test coverage for malformed PIPE-05B provenance and guard combinations.

### 2026-09-23 — FINAL-ANALYSIS-VALIDATION-01 completed; analysis pipeline passes with documented historical-fixture limitation

- Completed FINAL-ANALYSIS-VALIDATION-01 using synthetic-only fixtures.
- Expanded D037 malformed PIPE-05B fail-closed coverage and D036/PIPE-10 state, boundary, denominator, uncertainty-bound, determinism, and regression coverage.
- Synthetic cross-pipeline reconciliation passed:
  - PIPE-07 resolved confirmation counts reconcile with PIPE-08 primary numerators.
  - PIPE-09 grouped totals reconcile with the primary analysis outputs.
  - PIPE-10 package-state totals equal the D033 package denominator.
  - PIPE-10 eligible-response totals equal the D033 SHR denominator.
  - D037 confirmation-path counts sum to the primary numerator.
  - historical PIPE-07/08/09 output overwrite protection was verified.
- Focused adjudication + PIPE-07/08/09/10 suites: 126 passed.
- PIPE-07/PIPE-10-focused subset: 44 passed.
- Full suite: 327 passed with 2 known historical freeze-test failures caused by absent historical raw fixtures:
  - v2.1 expected 4 `API-v2.1-*` raw directories, found 0.
  - v2.3 expected 8 `API-v2.3-*` raw directories, found 0.
- Readiness verdict: PASS WITH DOCUMENTED LIMITATIONS. No new D036/D037 implementation defect was identified.
- No real v2.6 PHR, SHR, DFR, RDFR, interim adjudication metric, or final research result was calculated.
- No raw data, frozen inputs, manifests, prompts, model configuration, pacing, collection state, quarantine data, or existing result outputs were modified.

### 2026-09-23 — Final report integration worktree created and analysis pipeline consolidated

- Created dedicated integration/report worktree `/home/hirushan/Dev/ai-hallucination-integration` on branch `integration/final-report`, based on the committed live-collection branch snapshot.
- Merged committed `analysis/pipeline` state (`102320f`) into the integration branch without modifying the active live collection worktree.
- Integration merge committed as `2607907` (`integration: combine collection history with verified analysis pipeline`).
- Preserved the verified D033-D037 methodology and PIPE-05B/06/07/08/09/10 implementation while retaining the live collection/recovery history.
- Resolved a branch-local decision-ID collision: the analysis risk-model decision retains canonical ID `D032`; the live interrupted-request recovery decision, originally branch-local `D032`, is preserved unchanged in substance as integrated decision `D038`, with its original ID explicitly recorded for provenance.
- The integration/report repository retains the analysis collection-prevention guard and must not be used for live collection.
- Repository-guard validation in the integration worktree passed 24/25 tests. The sole failure was `test_quarantine_evidence_is_untouched` because `data/quarantine/` is intentionally absent from the integration worktree; the live-collection refusal and side-effect-prevention guard tests passed.
- Active v2.6 raw observations, batch state, recovery-audit state, analysis quarantine evidence, and derived checkpoint material were not merged into the integration worktree.
- Live v2.6 collection remains authoritative in `/home/hirushan/Dev/ai-hallucination-study` and can continue independently.

### 2026-09-23 — Final dissertation reporting control layer established

- Established the permanent final-dissertation/reporting control layer in the integration worktree.
- Commit: `17b1ae6` (`docs: establish final dissertation reporting controls`).
- Updated `AGENTS.md` to define the final-report worktree purpose, source-of-truth priority, frozen-experiment integrity rules, experiment/repository security safeguards, classification and metric controls, dissertation writing rules, citation controls, reporting workflow, and worktree safety boundaries.
- Added `docs/report_generation_protocol.md` defining the detailed dissertation-generation workflow, including university formatting requirements, baseline-draft reconciliation, citation policy, chapter-specific workflows, results safety, claims-evidence requirements, AI-tool responsibilities, and the standard audit → reconciliation → drafting → verification process.
- Added `docs/final_report_support/claims_evidence_matrix.md` as the control surface for `VERIFIED`, `PENDING`, and `REJECTED` dissertation claims.
- Added `docs/references/approved_references.md` as a controlled reference-list skeleton. Reference extraction has not yet been performed.
- Confirmed that no experimental/frozen files, raw data, manifests, prompts, model configuration, collection state, results, code, schemas, or tests were modified by this documentation milestone.
- Confirmed that `recomendations.txt` was not present under `~/Dev` within the checked search scope; repository instructions therefore treat it as advisory only when present and do not reconstruct it from memory.
- Next step: extract and verify the approved academic reference list from the baseline dissertation `IM2021101.pdf`, then begin the Chapter 1 evidence/reconciliation audit.

### 2026-09-23 — Approved dissertation reference set extracted

- Populated `docs/references/approved_references.md` from the baseline dissertation `IM2021101.pdf`.
- Extracted and preserved 34 baseline-approved citation entries.
- No external academic sources were added.
- Citation keys were checked for duplicates; none were found.
- Bibliographic metadata was preserved as supplied by the baseline dissertation rather than silently corrected.
- One baseline ambiguity was retained for later verification: the Yadav et al. DOI is recorded without an `http(s)` scheme.
- External DOI/bibliographic verification was not performed at this stage.
- The approved reference set now acts as the citation gate for final dissertation drafting.
- No experimental or frozen research artifacts were modified.
- Next step: conduct the Chapter 1 evidence/reconciliation audit before drafting final prose.

### 2026-09-23 — v2.6 hybrid API allocation corrected from 62 to 61 remaining rows

- Re-audited current v2.6 raw API observations before continuing hybrid allocation.
- Verified 119 existing API-assigned raw observations: M1=16, M2=6, M3=38, M4=59.
- The additional M1 observation is `API-v2.6-ENT-INT-01-M1-R01` (collection order 62), preserved with `collection_status: failed`.
- Because every existing raw API observation must retain its original interface assignment, the failed M1 observation remains API-assigned and must not be reclassified as manual.
- Correct remaining API allocation is therefore M1=24, M2=34, M3=3, M4=0, for 61 additional API rows.
- This preserves the intended final hybrid assignment of exactly 180 API rows and 180 Manual rows across the 360-row v2.6 manifest.
- Failed observations remain preserved and metric-ineligible; no failed observation is regenerated, substituted, or reassigned.
- The earlier estimate of 62 additional API rows was based on the previous M1 started count of 15 and is superseded by this raw-state audit.

### 2026-09-23 — Chapter 1 support-document milestone completed

- Completed `CHAPTER-1-EVIDENCE-AUDIT-01`, `CHAPTER-1-DRAFT-RECONCILIATION-01`, and `CHAPTER-1-LITERATURE-RECONCILIATION-01`.
- Created `docs/final_report_support/chapter1_evidence_audit.md`, `docs/final_report_support/chapter1_draft_reconciliation.md`, and `docs/final_report_support/chapter1_literature_reconciliation.md`.
- Preserved the existing research title unchanged. Aligned the working aim, O1–O4, and RQ1–RQ4 to the implemented Node.js/npm study; identified the baseline SLR-oriented framing for replacement.
- The literature reconciliation reviewed 22 claims: `SUPPORTED` 8; `PARTIALLY_SUPPORTED` 5; `UNVERIFIED` 8; `CONTRADICTED` 1.
- The strongest approved Chapter 1 sources identified were Spracklen et al. (2025), Al-Zofi (2025), Gao et al. (2025), Ladisa et al. (2023), Wang et al. (2025), Williams et al. (2025), Duan et al. (2020), and Ohm and Stuke (2023).
- Unsupported percentages and broad novelty claims must not be reused. Final empirical results remain pending.
- No frozen or experimental files were modified.

### 2026-09-23 — Chapter 1 final verification completed

- Completed `FINAL-CHAPTER-1-VERIFICATION-01` against repository evidence, approved references, the baseline dissertation, and the reconciled Chapter 1 support documents.
- Created `docs/final_report_support/chapter1_final_verification.md`.
- Verified 24 study-specific factual claims and 22 citation uses.
- Verification verdict: `PASS WITH MINOR CORRECTIONS`.
- One wording correction was required in Section 1.8 so the practical-risk statement matches the implemented framework boundary: assessment is limited to eligible confirmed package-hallucination findings.
- No final empirical result, prevalence value, model/category ranking, statistical conclusion, or risk distribution was introduced.
- No superseded SLR, autonomy-comparison, Java/Maven experimental, survey, predictive-modelling, or mitigation-study methodology remains in Chapter 1.
- After the verified wording correction, Chapter 1 Sections 1.1–1.11 are ready for transfer into the dissertation Word document.
- No frozen experimental artifacts were modified and no final v2.6 metrics were calculated.

### 2026-09-23 — Chapter 2 literature synthesis and baseline reconciliation completed

- Created `docs/final_report_support/chapter2_literature_synthesis.md`.
- Reconciled the baseline Chapter 2 against the implemented Node.js/npm study.
- Assessed all 34 approved references in a reference-theme matrix.
- Assessed 20 candidate literature claims.
- Audited 21 numeric/prevalence claims from the baseline literature review.
- Established the proposed final Chapter 2 structure and section-by-section writing plan.
- Distinguished literature context from the actual experimental scope so Java/Maven, PyPI, autonomy, slopsquatting, mitigation, and related cross-ecosystem topics are not misrepresented as performed experimental variables.
- Established a bounded literature-gap synthesis rather than a broad novelty claim.
- Identified source-level verification as a prerequisite before final Chapter 2 prose is drafted.
- No approved reference was added or removed.
- No frozen/experimental artifact was modified.
- No empirical result was calculated.
- `git diff --check` passed for the synthesis task.

### 2026-09-23 — Chapter 2 source verification, reference-coverage plan, and pre-draft freeze completed

- Completed `CHAPTER-2-SOURCE-VERIFICATION-01`, `CHAPTER-2-REFERENCE-COVERAGE-PLAN-01`, and `CHAPTER-2-PRE-DRAFT-FREEZE-01`.
- Created `docs/final_report_support/chapter2_source_verification.md` and `docs/final_report_support/chapter2_reference_coverage_plan.md`.
- Updated `docs/final_report_support/chapter2_literature_synthesis.md` with a source-verification addendum and the final Chapter 2 reference-coverage requirement; the original reconciliation assessment was preserved.
- Source-checked all 34 approved references: `FULL_TEXT_VERIFIED` 11; `METADATA_ONLY` 23; `ABSTRACT_ONLY` 0; `UNAVAILABLE` 0.
- Claim verification (20 claims): `DIRECTLY_SUPPORTED` 14; `SUPPORTED_WITH_QUALIFICATION` 5; `NOT_SUPPORTED` 0; `NOT_VERIFIABLE` 1 (LC19, agentic-systems context).
- Numeric-claim audit (21 baseline claims): `SAFE_TO_USE` 0; `USE_ONLY_WITH_CONTEXT` 6; removed/unverified 15.
- All 34 approved references have a planned Chapter 2 use: 11 full-text-verified references are planned for multiple substantive use; 22 metadata-only references are planned for single conservative contextual use; Gandhi (2026) was held as conditional pending bibliographic reconciliation.
- Gandhi bibliographic reconciliation: the baseline `IM2021101.pdf` reference list contains exactly one Gandhi entry, labelled `[Gandhi, 2026]` with year field 2026 and DOI `10.36227/techrxiv.176800890.09196406/v1`, identical to approved entry 6 in `docs/references/approved_references.md`. All 16 baseline in-text Gandhi citations use `Gandhi, 2025`; none uses 2026, and no other Gandhi entry exists. The discrepancy is therefore an in-text citation-year mismatch only, not a source-identity conflict. Status: `RESOLVED — USE Gandhi (2026)`. `approved_references.md` was not changed because its entry matches the baseline reference list. External bibliographic verification remains not performed, consistent with the approved-reference status.
- Gandhi (2026) remains `METADATA_ONLY`; resolution of the year makes it citable for one conservative contextual use only (Section 2.7, autonomous-development security-risk context). LC19 remains `NOT_VERIFIABLE`, and autonomy remains outside the performed study.
- Froze the Chapter 2 reference policy: all 34 approved references must appear at least once; argumentative weight follows source strength; no citation dumping; no unsupported percentages; no broad novelty claim.
- Chapter 2 drafting verdict remains `READY_WITH_RESTRICTED_CLAIMS`.
- No approved reference was added or removed. No frozen/experimental file was modified. No empirical result was calculated.

### 2026-09-23 — Chapter 2 first drafting block (Sections 2.1–2.4)

- Created `docs/report_drafts/chapter2_sections_2_1_to_2_4.md` (approximately 4,640 words; Sections 2.5–2.10 not yet drafted).
- Cited 18 of 34 approved references in this first block: 11 full-text-verified sources and 7 metadata-only sources used conservatively for contextual claims.
- The seven metadata-only sources used once are Agarwal et al. (2024), Daoud (2026), Le-Anh et al. (2026), Zhuo et al. (2025), Dubey and Madisetti (2026), Ohm and Stuke (2023), and Wang et al. (2025).
- Sixteen approved references remain to be incorporated in later Chapter 2 sections under the established reference-coverage plan.
- Dubey and Madisetti (2026) and Ohm and Stuke (2023) used their planned single contextual citation earlier than originally allocated; they should not later be reused as independent support for stronger claims unless source-level evidence is available.
- Spracklen et al. (2025) was additionally used in Section 2.2.1 for the verified non-determinism/repetition claim.
- No numeric claims were used.
- No `Gandhi, 2025`, `Spracklen, 2024`, or `Ohm et al., 2020` citation was used.
- No dissertation empirical result was stated or inferred.
- The draft remains uncommitted pending factual, citation, and synthesis review.

### 2026-09-23 — Chapter 2 Block 1 correction

- Applied CHAPTER-2-BLOCK-1-CORRECTION-01 to `docs/report_drafts/chapter2_sections_2_1_to_2_4.md`.
- Completed C01–C16 and applied optional clarity revisions R1–R4.
- Re-verified Table 2.1, citation constraints, metadata-only contextual uses, and absence of dissertation results and numeric claims.
- Verdict: PASS; readiness: READY_TO_DRAFT_2_5_TO_2_10.

### 2026-09-24 — Chapter 2 Block 2 drafted (Sections 2.5–2.7)

- Created `docs/report_drafts/chapter2_sections_2_5_to_2_7.md` (working draft; ~5,325 words).
- 23 approved references cited (9 full-text-verified; 14 metadata-only, each once at title/topic level only). Chapter 2 coverage now 32/34; Liu et al. (2025a) and Zheng et al. (2026) reserved for Section 2.8.
- No numeric claims; no dissertation results; Gandhi cited once as Gandhi (2026); no Spracklen 2024 / Ohm et al. 2020 forms.
- Package hallucination presented as a reliability defect; slopsquatting as a conditional downstream scenario; the Impact × Detectability framework stated as study-defined (Chapter 3), not literature-derived.
- Block 2 source-level verification recommended before drafting Sections 2.8–2.10.

### 2026-09-24 — Chapter 2 Block 3 drafted (Sections 2.8–2.10)

- Drafted `docs/report_drafts/chapter2_sections_2_8_to_2_10.md` (comparative dimensions, bounded synthesis/research gap, chapter summary); Sections 2.1–2.7 unchanged.
- Cumulative Chapter 2 approved-reference coverage: 34/34; Liu et al. (2025a) and Zheng et al. (2026) used once each at metadata/title level in Section 2.8.
- No numeric literature claims; no dissertation results; no novelty/absence claims. Block 3 verification and chapter assembly pending.

### 2026-09-24 — Chapter 2 assembled and final verification passed

- Assembled the verified Chapter 2 drafting blocks into `docs/report_drafts/chapter2_complete_draft.md`.
- Created `docs/final_report_support/chapter2_final_verification.md`.
- Final Chapter 2 verification verdict: `PASS`.
- Final Chapter 2 word count: approximately 13,192 words, estimated at approximately 32–36 pages under the dissertation formatting before final Word-layout verification.
- Verified all 34 approved references appear at least once in Chapter 2, with no unapproved references.
- Gandhi is cited only as `Gandhi (2026)`; the superseded forms `Gandhi (2025)`, `Spracklen (2024)`, and `Ohm et al. (2020)` do not appear.
- Table 2.1 passed final verification and preserves the distinctions among typosquatting, dependency confusion, accidental dependency error, package hallucination, and slopsquatting.
- Table 2.2 passed final verification as a literature-design synthesis; evidence-limited fields remain `—` rather than being inferred.
- One duplicated topic-context sentence in Section 2.7 was removed during final assembly; no broader prose rewrite was performed.
- No unverified numeric literature claim, dissertation empirical result, model/category ranking, statistical-significance result, risk distribution, or unsupported novelty/absence claim appears in the final Chapter 2 draft.
- Final Word-readiness status: `READY_FOR_WORD`.
- No frozen or experimental artifact was modified and no final study metric was calculated.

### 2026-09-24 — Chapter 2 figure plan reconciled with final study

- Updated `docs/report_drafts/chapter2_complete_draft.md` with two final-study-aligned figure placeholders.
- Added Figure 2-1 after Table 2.1 and before Section 2.5: conceptual relationship between LLM package-name hallucination, dependency resolution, and downstream software supply-chain risk.
- Added Figure 2-2 at the start of Section 2.9: literature synthesis linking LLM code generation, package hallucination, dependency reliability, and software supply-chain risk.
- Baseline Chapter 2 figures representing PRISMA, autonomous-agent/slopsquatting execution flow, defensive architecture, hybrid mitigation architecture, and sandboxed execution were designated for removal/replacement because they reflect superseded methodology or unperformed work.
- Table 2.1 and Table 2.2 were not modified.
- Chapter 2 citation coverage remains 34/34 approved references.
- No verified Chapter 2 claim, citation, experimental artifact, or result was changed.

### 2026-09-24 — Chapter 3 methodology reconciliation completed

- Completed evidence-grounded reconciliation of the baseline dissertation methodology against the implemented frozen v2.6 study.
- Created `docs/final_report_support/chapter3_methodology_reconciliation.md`.
- Reviewed 36 baseline methodology items:
  - KEEP: 1
  - KEEP_WITH_REVISION: 8
  - REWRITE: 4
  - REMOVE: 17
  - MOVE_TO_LIMITATIONS: 3
  - MOVE_TO_FUTURE_WORK: 3
- Confirmed the final methodology as a Node.js/npm-only study with 30 frozen tasks, six categories, four frozen model conditions, three planned repetitions, and 360 planned observations.
- Reconciled the implemented analysis pipeline from PIPE-03 through PIPE-10, including conservative adjudication under D037, primary PHR/SHR metrics, secondary DFR/RDFR metrics, grouped statistical analysis, and `risk-model-1.0.0`.
- Removed or reclassified unsupported baseline methodology including Java/Maven/PyPI experimentation, surveys/human participants, autonomy comparisons, mitigation experiments, predictive ML, 70/30 train-test modelling, Cohen’s Kappa, expert validation, temporal holdout, package execution/installation, and the superseded 0–12 risk model.
- Final Chapter 3 structure, figure plan, table plan, methodological limitations, and prohibited/outdated statements were established.
- Chapter 3 drafting status: READY WITH RESTRICTIONS.
- Restrictions: final collection/results remain pending; detailed manual-interface operational prose must remain limited to verified collection records; no expert/inter-rater validation may be claimed.
- `git diff --check` passed.
- Frozen experiment inputs and raw evidence were not modified.

Next:
- draft Chapter 3 prose from the verified reconciliation;
- keep final achieved sample counts and empirical findings out of Chapter 3 until final collection/analysis is complete;
- verify the completed Chapter 3 draft against repository evidence before Word integration.

### 2026-09-24 — Chapter 3 final assembly verified

- Assembled Chapter 3: Research Methodology from three separately drafted and verified blocks.
- Saved the authoritative final draft at `docs/report_drafts/chapter3_complete_draft.md` and its final verification at `docs/final_report_support/chapter3_final_verification.md`.
- The chapter covers Sections 3.1–3.16 and contains 12,249 Markdown words.
- It retains five planned figures and 14 methodology tables numbered consecutively from Table 3-1 through Table 3-14.
- Three `[APPENDIX REFERENCE PENDING]` placeholders remain for later dissertation assembly.
- The final-result leakage check passed; the obsolete-methodology leakage check passed; and the em-dash count was zero.
- The final verification verdict is `READY_FOR_WORD`.
- Chapter 3 contains no empirical final results. Final collection and provenance-consistent final analysis remain pending.
- Finalized Chapter 3 assembly commit: `0bb0f1b` (`docs: finalize verified Chapter 3 methodology`).

Next:
- prepare Chapter 4 around verified final analytical outputs once they are available; do not imply that Chapter 4 results already exist.

### 2026-09-25 — Chapter 3 visual, table, and style refinement completed

- Completed the Chapter 3 visual, table, and style refinement; the authoritative chapter remains `docs/report_drafts/chapter3_complete_draft.md`.
- Reviewed six baseline Chapter 3 figures/tables from `IM2021101.pdf` as design references only, not as methodology authority.
- Retained five planned Chapter 3 figures; all five remain detailed production placeholders.
- Retained Tables 3-1 through 3-14; no table was removed or merged. Five tables were flagged/revised in the presentation audit, including the terminology correction in Table 3-1.
- Applied 13 targeted academic-style edits. Prose double-hyphen count = 0; em-dash count = 0; final-result leakage = NO; obsolete-methodology leakage = NO.
- Review evidence: `docs/final_report_support/chapter3_visual_table_style_review.md`.
- `git diff --check` passed.
- Refinement commit: `1fd19b1` (`docs: refine Chapter 3 visuals tables and style`).

Next:
- create publication-quality Chapter 3 figures from the five approved placeholders;
- preserve the implemented v2.6 methodology while drawing them.

### 2026-09-25 — Compact verified Chapter 3 promoted as authoritative

- Promoted the compact verified Chapter 3 as the authoritative methodology chapter at `docs/report_drafts/chapter3_complete_draft.md`.
- Compact-equivalence verification: `docs/final_report_support/chapter3_compact_equivalence_verification.md`.
- The final chapter contains 7,501 Markdown words, reduced from the approximately 12.3k-word previous verified version by approximately 39%.
- The final structure contains 9 tables, 5 approved figure placeholders, and 6 unresolved appendix-reference placeholders.
- The compact-equivalence review found no material methodology loss. PHR/SHR, DFR/RDFR, the PIPE-09 statistical procedure, the risk model, safety controls, and limitations remained equivalent.
- Final-result leakage: NO. Obsolete-methodology leakage: NO. Em-dash count: 0. Prose double-hyphen count: 0.
- Final status: `READY_FOR_WORD`.
- Compact-promotion commit: `0c82c82ef3207706529f9ea92da0351ebeba0925` (`docs: promote compact verified Chapter 3`).

Next:
- create the five approved Chapter 3 figures;
- transfer the verified compact Chapter 3 to Word;
- check actual pagination after the figures and university formatting are applied.

### 2026-09-25 — Chapter 2 v2.7 reconciliation

- Reviewed the complete Chapter 2 literature-review draft against the frozen v2.7.0 three-model final study.
- No Chapter 2 prose changes were required.
- Chapter 2 contains no current-study model count, planned observation total, API/manual split, M2 inclusion, or active-study version that conflicts with v2.7.
- Section 2.9.3 remains valid because it refers generically to frozen model conditions and leaves implementation detail to Chapter 3.
- Figures 2-1 and 2-2 are conceptual and independent of the number of retained model conditions.
- References were unchanged.
- Verification recorded in `docs/final_report_support/chapter2_v2.7_reconciliation_verification.md`.
- Outstanding supporting-document reconciliation: `claims_evidence_matrix.md` contains stale Chapter 1 claims CH1-004, CH1-006, and CH1-014, and this worktree's `docs/current_research_status.md` still reflects v2.6.

### 2026-09-25 — Chapter 1 reconciled to frozen v2.7 final study

- Updated `docs/report_drafts/chapter1_complete_draft.md` to align with the frozen v2.7.0 three-model design.
- Current Chapter 1 reports M1, M3, and M4 as the retained model conditions.
- Updated the planned design from the superseded four-condition/360-observation description to 270 planned observations.
- Updated assignment totals to 140 API-assigned and 130 manual-assigned observations.
- Added a concise disclosure that M2 was removed after partial collection and before final analysis because its intended collection protocol could not be completed consistently; historical M2 evidence remains preserved but excluded from final analysis.
- Research questions and objectives were unchanged.
- No empirical findings were introduced.
- Verification recorded in `docs/final_report_support/chapter1_v2.7_reconciliation_verification.md`.
- Chapter 1 reconciliation committed as `7442715`.

### 2026-09-25 — Decision-ID collision resolved for M2 removal

- Resolved the cross-worktree D036 decision-ID collision before Chapter 3 reconciliation.
- Integration/report D036 remains the existing DFR/RDFR secondary dependency-reliability decision unchanged.
- The M2-removal decision originally recorded as D036 in the data-collection worktree is represented in the integration worktree as D039.
- D039 preserves the source decision meaning and records provenance to `feature/data-collection`, freeze commit `bba890d9aa5838f06bee4b1bd0e85d9e61b444f8`, and tag `v2.7.0-freeze`.
- Updated `docs/current_research_status.md` and `docs/final_report_support/claims_evidence_matrix.md` to use the unambiguous D039 mapping.
- Added `docs/final_report_support/decision_id_collision_reconciliation.md`.
- No chapter draft, figure asset, frozen experimental input, or empirical result was modified.
- Remaining cross-worktree decision-ID collisions D033–D035 require reconciliation if they are referenced by the dissertation or current methodology documentation.

### 2026-09-25 — Remaining decision-ID collisions reconciled

- Resolved the remaining cross-worktree decision-ID collisions D033, D034, and D035 before Chapter 3 v2.7 reconciliation.
- Existing integration/report decisions remain unchanged:
  - D033: primary PHR/SHR analytical units and truncated-response exclusion.
  - D034: primary PHR/SHR retained; external-dependency eligibility handled separately in secondary sensitivity analysis.
  - D035: abnormal provider termination other than `stop` or `length` is FAILED and metric-ineligible.
- Added integration aliases for the corresponding data-collection decisions:
  - data-collection D033 → integration D040: deterministic HYBRID API/manual allocation.
  - data-collection D034 → integration D041: API collection restricted to eligible never-attempted API-assigned rows.
  - data-collection D035 → integration D042: offline manual observation capture and preservation workflow.
- Source decisions remain preserved unchanged in the data-collection repository.
- Updated `docs/current_research_status.md` and `docs/final_report_support/claims_evidence_matrix.md` to use the unambiguous aliases where relevant.
- Added `docs/final_report_support/remaining_decision_id_collision_reconciliation.md`.
- No chapter draft, figure asset, frozen experiment input, or empirical result was modified.
- Future Chapter 3 references to HYBRID allocation, API row selection, or manual capture must use D040, D041, and D042 respectively.

### 2026-09-25 — Chapter 3 reconciled to v2.7.0 three-condition final study

- Reconciled `docs/report_drafts/chapter3_complete_draft.md` from the superseded v2.6.0 design to frozen v2.7.0 (tag `v2.7.0-freeze`, commit `bba890d9aa5838f06bee4b1bd0e85d9e61b444f8`): M1, M3, M4; 270 planned observations; 45 per category; 140 API / 130 manual (deterministic, not balanced).
- Added M2 exclusion disclosure (Section 3.5.1; integrated D039) and retained-evidence reuse statement (Section 3.5.2).
- Tables 3-1, 3-2, 3-3 updated; Tables 3-4 to 3-9 unchanged. Word count 7,501 to 8,055.
- Figures 3-1 and 3-2 require regeneration; Figures 3-3 to 3-5 unaffected.
- Verification: `docs/final_report_support/chapter3_v2.7_reconciliation_verification.md`. No empirical results added.
