# Final-Study v2.7 Migration Verification

**Task ID:** FINAL-STUDY-V2.7-MIGRATION-01

**Date:** 2026-09-25 (freeze timestamp `2026-09-24T23:22:58.369305Z`)

**Source audit:** `docs/m2_removal_final_study_impact_audit.md`

**Decision record:** `docs/decision_log.md` D036

**Commit/tag:** none. Commit and a `v2.7.0-freeze` tag are pending researcher review.

## 1. Reason for migration

The v2.6.0 final study was frozen for four model conditions. M2 (`qwen/qwen3.8-27b`, OpenRouter pinned to Darkbloom) could not complete the required collection protocol consistently through its intended automatic API route. Of its 90 planned rows, 11 were attempted: 3 failed with `http_status_402`, 6 failed with an HTTP 200 response that had no non-empty assistant content, and 2 completed. The other 79 rows were pending.

The rationale uses collection outcomes only. The repository contains no v2.6 package-extraction, registry-validation, classification, metric, or risk output for M2 or any other condition; `results/` holds only v2.2 derived outputs. No M2 result value was therefore available to justify the exclusion. The exclusion happened after partial M2 collection and before final analysis. Because some M2 observations already existed, it is not wholly prospective.

## 2. Preconditions verified before creation

Each value was recomputed from the source files. All of them matched the audit.

| Check | Expected | Observed |
| --- | ---: | ---: |
| v2.6 planned observations | 360 | 360 |
| M2 rows | 90 | 90 |
| Retained rows | 270 | 270 |
| Retained API-assigned | 140 | 140 |
| Retained manual-assigned | 130 | 130 |
| Retained models | M1, M3, M4 | M1, M3, M4 |
| Per-model API/manual | M1 40/50, M3 41/49, M4 59/31 | identical |
| Retained API rows with preserved raw metadata | 140 | 140 (none missing) |
| Raw identity/prompt/response hash mismatches | 0 | 0 |

The source hashes also matched the audit: the v2.6 manifest (`b2b2750b…`), the HYBRID assignment (`e4b9295b…`), the v2.6 freeze (`53736d8a…`), model set 1.4.0 (`cba4a4ec…`), and the rolling v2.6 state at snapshot (`1a3af56d…`).

## 3. Design change (v2.6.0 to v2.7.0)

| | v2.6.0 | v2.7.0 |
| --- | ---: | ---: |
| Model conditions | 4 (M1, M2, M3, M4) | 3 (M1, M3, M4) |
| Planned observations | 360 | 270 |
| Rows per model | 90 | 90 |
| Rows per repetition | 120 | 90 |
| Rows per category | 60 | 45 |
| API / manual | 180 / 180 | 140 / 130 |
| Model set | api-model-set-1.4.0 | api-model-set-1.5.0 |

Nothing else changes. The task set, prompt template, rendered prompt bytes, model IDs, providers, pins, output ceilings, sampling parameters, retry, pacing, failure, and truncation policies are all the same.

- **Membership rule:** the v2.6 manifest run IDs minus every M2 run ID. No status, outcome, or response field is used.
- **Condition IDs:** M1, M3, and M4 keep their IDs and are not renumbered.
- **Run IDs:** the original `API-v2.6-…` run IDs are kept, so v2.6 evidence is never presented as a new v2.7 generation. `cohort_order` numbers the rows 1–270 contiguously, and `source_collection_order` keeps the v2.6 order. Relative order is preserved.
- **Interface:** the assignment is inherited from `hybrid_assignment_v1.0.0.csv` by filtering. No retained row was reassigned, and the design does not force a 135/135 split. Interface is unevenly associated with model condition, most strongly for M4 (59/31), so analyses must not claim interface balance.
- **Model set 1.5.0:** it is `api-model-set-1.4.0` with the M2 entry removed. `$schema`, `model_set_version`, and `frozen_at_utc` are updated, and a `source_model_set` provenance block is added. The retained condition objects are identical to their 1.4.0 entries.

## 4. M2 removal and preservation

- All 90 M2 rows are absent from the v2.7 manifest, collection state, and final-study selection (`final_study_rows()`). That selection fails closed if an M2 row is present.
- All M2 evidence is kept as historical v2.6 evidence:
  - the 90 M2 rows in the v2.6 manifest;
  - the 40/50 M2 rows in the HYBRID assignment;
  - M2 events in the v2.6 state;
  - M2 in model set 1.4.0 and the v2.6 freeze;
  - all 11 raw directories under `data/final/raw/API-v2.6-*-M2-R01/`.

  Each of the 11 directories is listed in the v2.7 freeze with its metadata and response SHA-256. `--check` and the tests confirm that they are still present and unchanged.
- M2 is excluded from all v2.7 metrics and denominators. This includes both completed M2 outputs.

## 5. Reuse of existing evidence

`data/final/collection_state_v2.7.0.json` maps every v2.7 row to its existing evidence. The mapping is read-only and is based on provenance. For each of the 140 retained API rows, the derivation verifies:

- the raw metadata `run_id`, `task_id`, `category`, `model_condition_id`, `requested_model_id`, repetition, and `collection_order` against the v2.7 row;
- that the preserved `prompt.txt` bytes and the metadata `prompt_sha256` equal the frozen prompt digest;
- that the collection route is API and that no manual artifact exists for the row;
- that `response.md` bytes equal the recorded `response_sha256`, where a response exists;
- that the observation is finalized as completed, truncated, or failed.

All 140 rows mapped. Nothing was copied, renamed, rewritten, or regenerated, and no `API-v2.7-*` raw directory exists. The mapped observations were generated under `api-model-set-1.4.0`. Their provenance is not rewritten to 1.5.0, and the claim that they are equivalent rests on the retained condition definitions being identical.

Initial v2.7 collection state:

| Condition | API completed | API truncated | API failed | Manual pending | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| M1 | 27 | 10 | 3 | 50 | 90 |
| M3 | 36 | 0 | 5 | 49 | 90 |
| M4 | 42 | 6 | 11 | 31 | 90 |
| **Total** | **105** | **16** | **19** | **130** | **270** |

These counts describe the state of collection only. They are not final results. Failed and truncated observations keep their existing eligibility rules and are not replaced.

## 6. Tests and verification run

| Command | Result |
| --- | --- |
| `python3 -m unittest tests/test_final_study_v2_7.py` | 12 tests, OK |
| `python3 -m unittest tests/test_api_v2_6.py tests/test_hybrid_assignment.py tests/test_hybrid_api_collection.py tests/test_hybrid_manual_collection.py tests/test_api_v2_6_exclude_model.py` | 32 tests, OK |
| `python3 -m unittest discover -s tests` (full suite) | 164 tests, OK |
| `python3 scripts/create_experiment_freeze_v2_7.py --check` | PASS |
| `python3 scripts/create_experiment_freeze_v2_6.py --check` | PASS |
| `python3 scripts/create_hybrid_assignment_v1_0.py --verify` | PASS |
| SHA-256 snapshot of 1,066 v2.6/M2 files taken before creation and re-checked afterwards (freeze, model set 1.4.0, manifest, assignment, template, 30 prompts, v2.6 state, every `API-v2.6-*` raw file, v2.6 freeze Markdown, assignment report, v2.6 schema, progress log, paper notes) | all unchanged |

The new tests cover the following:

1. 270 rows.
2. 90 rows per retained model.
3. Zero M2 rows.
4. 30 tasks.
5. Six categories with 45 rows each.
6. Three repetitions with 90 rows each.
7. 140 API rows.
8. 130 manual rows. Items 7 and 8 also check the per-model split and route equality with v2.6.
9. Prompt digests equal v2.6 and the prompt file bytes.
10. Task, category, repetition, and all other v2.6 identity fields are unchanged, and the manifest is the deterministic filter.
11. In-place mapping of the 140 retained API rows, rejection of tampered evidence, and no v2.7 raw namespace.
12. Frozen v2.6 hashes are unchanged, and a build does not write v2.6 state or raw metadata.
13. All 11 M2 directories are present with frozen hashes.
14. Final-study selection excludes M2 and fails closed on an M2 row or a wrong row count.

The tests also check that model set 1.5.0 is 1.4.0 minus M2 (four, two, or reordered condition sets are rejected), that the schema requires exactly three items, and that the freeze JSON and Markdown are reproducible.

## 7. Files

**Created**

- `config/api_model_set_1.5.0.json`
- `config/experiment_freeze_v2.7.0.json`
- `docs/experiment_freeze_v2.7.0.md`
- `manifests/api_final_v2.7.0_manifest.csv`
- `data/final/collection_state_v2.7.0.json`
- `schemas/api_model_set_v2_7.schema.json`. It is needed because the v2.6 schema requires exactly four conditions and version 1.4.0.
- `scripts/create_experiment_freeze_v2_7.py`. It creates and verifies the files above and refuses to overwrite them.
- `tests/test_final_study_v2_7.py`
- `docs/final_study_v2.7_migration_verification.md` (this file)

**Modified**

- `docs/decision_log.md`: D036 appended. No earlier entry was edited.

**Intentionally untouched**

- All v2.6 inputs and records: freeze JSON/Markdown, model set 1.4.0, v2.6 schema, manifest, HYBRID assignment and report, prompt template, rendered prompts, `data/final/api_batch_state_v2.6.0.json`, and every raw directory.
- Collectors: `collect_api_run.py`, `collect_api_batch*.py`, `collect_hybrid_*.py`.
- `docs/research_progress_log.md` and `docs/final_paper_notes.md`, which are not to be updated yet. Their pre-existing uncommitted changes and the pre-existing modification to the v2.6 state file were left exactly as found.
- `docs/current_research_status.md`.

**Not created, by design**

- No v2.7 copies of the prompt template or rendered prompts. v2.7 references the v2.6 files by unchanged hash, so retained rows and their raw `prompt.txt` share a single prompt identity.
- No separate `hybrid_assignment_v2.0.0.csv`. The inherited interface is a frozen column of the v2.7 manifest.
- No v2.7 API state file, because no v2.7 API collection remains.

## 8. Limitations and open items

- **Timing:** the exclusion was decided after 11 M2 rows were collected. It is before final analysis but is not wholly prospective, and the dissertation must disclose this (audit section 11.3).
- **Manual interface not yet approved:** the 130 pending manual rows cannot be validly collected until a manual interface configuration is approved (D035).
- **Existing tools are still pinned to v2.6:** `collect_hybrid_manual.py` and `collect_hybrid_api_batch.py` still pin the v2.6 manifest and assignment. `collect_api_run.load_config` accepts only four-condition model sets, so it does not accept 1.5.0; this does not matter because no v2.7 API collection remains. The v2.7 state derivation already recognises manual artifacts for retained rows under the existing `data/final/manual_raw/v2.6.0/<run_id>/` root, because run IDs are unchanged. Whether future manual capture should use that root or a v2.7-specific tool is a separate decision.
- **Refreshing the state:** `collection_state_v2.7.0.json` is an initial snapshot anchored in the freeze. Once manual collection begins, a separately approved procedure for refreshing or advancing the state is needed. Until then, `--check` will fail on purpose if evidence changes.
- **M2 collection under v2.6:** the v2.6 HYBRID API selector can still select M2 rows. Stopping further M2 collection is an operational instruction; it is not enforced in code. Any later M2 artifact would stay outside v2.7 automatically.
- **Downstream pipeline:** the response inventory, extraction, validation, and classification stages have not yet been wired to the v2.7 cohort. They must use `final_study_rows()` or the v2.7 manifest and assert that there are zero M2 rows.
- **Current-status and paper documents:** `docs/current_research_status.md`, the progress log, and the final-paper notes still describe v2.6 as active. They should be updated after researcher review and freeze.
