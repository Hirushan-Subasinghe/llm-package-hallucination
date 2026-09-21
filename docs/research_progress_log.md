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
