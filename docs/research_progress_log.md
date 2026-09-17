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
