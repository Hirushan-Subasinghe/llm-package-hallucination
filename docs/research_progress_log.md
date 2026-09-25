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
