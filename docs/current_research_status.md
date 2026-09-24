# Current Research Status

**Last updated:** 2026-09-25 (v2.7.0 three-model final study frozen and migration verified)
**Project:** LLM Package Hallucination Study

## Current phase: v2.7.0 is the active final study; API collection complete for retained models; manual collection pending

v2.7.0 is the active, current final study. It is the frozen v2.6.0 design with the entire M2 condition removed (decision D036). It was frozen at `2026-09-24T23:22:58.369305Z` and committed in `bba890d` ("experiment: establish final v2.7 three-model study"). The `v2.7.0-freeze` tag has not been created yet and is pending researcher review.

### Current v2.7.0 three-model design

- Retained model conditions: M1 `cohere/north-mini-code:free`, M3 `openai/gpt-oss-120b`, M4 `nvidia/nemotron-3-ultra-550b-a55b:free`. Condition IDs keep their historical identifiers and are **not** renumbered.
- Planned observations: 30 tasks × 3 model conditions × 3 repetitions = **270** (90 per retained model, 90 per repetition, 45 per category).
- Interface assignment, inherited unchanged from the v2.6 HYBRID allocation and not rebalanced: **140 API / 130 manual** (M1 40/50, M3 41/49, M4 59/31). Interface is unevenly associated with model condition, so analyses must not claim interface balance.
- M2 rows in the v2.7 manifest: **0**.
- Model set: `config/api_model_set_1.5.0.json` (`api-model-set-1.4.0` with M2 removed; the retained condition definitions are identical).
- Manifest: `manifests/api_final_v2.7.0_manifest.csv` (270 unique rows; SHA-256 `2edf2638f08a1079aadd02c174951a912aa2797b56df36997878096b29a4ed20`). Retained rows keep their original `API-v2.6-…` run IDs, task/category/repetition identities, prompt bytes, and `source_collection_order`. `cohort_order` numbers them 1–270.
- Initial collection state: `data/final/collection_state_v2.7.0.json`.
- Freeze record: `config/experiment_freeze_v2.7.0.json` and `docs/experiment_freeze_v2.7.0.md`.
- Migration verification: `docs/final_study_v2.7_migration_verification.md`. Source audit: `docs/m2_removal_final_study_impact_audit.md`.
- Task set, prompt template, rendered prompt bytes, model IDs, providers, pins, output ceilings, sampling parameters, retry, pacing, failure, and truncation policies are unchanged from v2.6.

**All final analysis must use the v2.7 manifest (or `final_study_rows()`) only and must assert zero M2 rows.** The downstream inventory, extraction, validation, and classification stages have not yet been wired to the v2.7 cohort.

### M2 exclusion

- M2 (`qwen/qwen3.8-27b`, OpenRouter pinned to Darkbloom) is excluded from the final study and from every v2.7 metric and denominator, including its 2 completed outputs.
- Rationale is operational: the intended automatic API route could not complete the required collection protocol consistently. At the decision snapshot, 11 of 90 M2 rows had been attempted (3 `http_status_402` failures, 6 HTTP-200 responses without non-empty assistant content, 2 completed) and 79 were pending.
- The exclusion occurred after partial M2 collection and before final analysis; it is not wholly prospective and must be disclosed as such. No package-extraction, registry-validation, classification, metric, or risk output existed for any v2.6 condition, so no empirical outcome could have motivated the removal.
- All M2 evidence is preserved unchanged as historical v2.6 evidence: the 90 M2 manifest rows, the M2 HYBRID assignment rows, M2 events in the v2.6 state, M2 in model set 1.4.0 and the v2.6 freeze, and all 11 `data/final/raw/API-v2.6-*-M2-R01/` directories (hash-listed in the v2.7 freeze).

### Evidence reuse

The 140 retained API observations (M1/M3/M4) are mapped in place to their preserved v2.6 raw evidence by run ID and SHA-256. Nothing was copied, renamed, rewritten, or regenerated, and no `API-v2.7-*` raw directory exists. Mapped observations were generated under `api-model-set-1.4.0`; that provenance is not rewritten.

### Current collection-state snapshot (v2.7 initial state)

These are collection-state counts only, not research results.

| Condition | API completed | API truncated | API failed | Manual pending | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| M1 | 27 | 10 | 3 | 50 | 90 |
| M3 | 36 | 0 | 5 | 49 | 90 |
| M4 | 42 | 6 | 11 | 31 | 90 |
| **Total** | **105** | **16** | **19** | **130** | **270** |

All 140 API-assigned rows are finalized. Failed and truncated observations are preserved and are not retried or replaced. No v2.7 API collection remains.

### Open blockers

- **Manual interface approval:** the 130 manual rows cannot be validly collected until a manual interface configuration is approved (D035).
- **v2.7 collection-state update mechanism:** `collection_state_v2.7.0.json` is an initial frozen snapshot; a separately approved procedure to refresh/advance it is needed before manual collection begins (`--check` fails by design if evidence changes).
- **Collection scripts are still v2.6-oriented:** `collect_hybrid_manual.py` and `collect_hybrid_api_batch.py` still pin the v2.6 manifest and assignment; the v2.6 HYBRID API selector can still select M2 rows (stopping M2 collection is an operational instruction, not code-enforced).

Validation at migration: full test suite 164 passed, 0 failed; `create_experiment_freeze_v2_7.py --check`, `create_experiment_freeze_v2_6.py --check`, and `create_hybrid_assignment_v1_0.py --verify` all passed.

## Superseded v2.6.0 four-model design (historical)

> **Historical / superseded by v2.7.0.** The text in this section describes the v2.6 state as of 2026-09-23 and is retained for provenance only. v2.6 is not the active final study; its four-condition, 360-observation, 180 API / 180 manual design must not be cited as the current design. All v2.6 inputs and records remain preserved unchanged.

v2.5 was prospectively stopped after preserved observations showed repeated 16,000-token truncation. Its raw responses, state, manifest, freeze, and prompts remain separate historical evidence and are excluded from v2.6 primary SHR/PHR. The historical v2.5 freeze remains anchored to commit `87d3158` and tag `v2.5.0-freeze`; the live v2.5 state and observations have since advanced beyond that initial freeze.

v2.6.0 was a fresh independent 360-observation experiment (four conditions M1–M4) beginning at observation 1, frozen under tag `v2.6.0-freeze`. Its frozen manifest remains 360 unique pending rows. As of 2026-09-23 (pre-HYBRID snapshot, now stale), the preserved raw state contained 119 API-attempted observations: M1 16, M2 6, M3 38, and M4 59. M3 API collection was then paused because the frozen Groq configuration has a documented TPM/HTTP 413 incompatibility.

The derived `manifests/hybrid_assignment_v1.0.0.csv` assigned every v2.6 frozen manifest row to an interface without modifying frozen inputs: 180 API and 180 manual (M1 40/50, M2 40/50, M3 41/49, M4 59/31 API/manual). It preserved all 119 existing API attempts and filled the remaining model API quotas using earliest never-attempted rows in frozen `collection_order`. The original frozen manifest SHA-256 remained `b2b2750b3ae4ce96a867df14117b05c12f214760ef7036d6bbf2f78e44939b7f` before and after derivation. v2.7.0 inherits the M1/M3/M4 portion of this assignment unchanged.

## Frozen v2.6 inputs (historical)

- Task set: `prompts/tasks/final_2.0.0.jsonl` (unchanged from v2.5).
- Model set: `config/api_model_set_1.4.0.json`.
- Prompt template: `prompts/prompt_template_v2.6.0.md`; all 30 rendered prompts are byte-identical to v2.5.
- Manifest: `manifests/api_final_v2.6.0_manifest.csv`.
- Derived HYBRID allocation: `manifests/hybrid_assignment_v1.0.0.csv` (not a frozen input and not a manifest replacement).
- Derived verification report: `reports/hybrid_assignment_v1.0.0_report.md`.
- Initial state: `data/final/api_batch_state_v2.6.0.json`.
- Freeze record: `config/experiment_freeze_v2.6.0.json` and `docs/experiment_freeze_v2.6.0.md`.

The v2.5-to-v2.6 experimental changes are model-specific output ceilings (M1 64,000; M2 32,768; M3 and M4 65,536) and moving the unchanged M2 model ID `qwen/qwen3.8-27b` from Groq to OpenRouter, pinned exclusively to Darkbloom (`darkbloom`) with fallback disabled. All other generation and collection rules remain unchanged.

## Historical v2.5 freeze snapshot

v2.4 was prospectively stopped at the documented checkpoint of 30 finalized observations: 14 completed, 12 truncated, and 4 failed (40.0% preliminary truncation). Its frozen inputs and preserved observations remain methodological evidence only. No further v2.4 collection is planned.

At its prospective freeze, v2.5.0 began as a fresh, independent 360-observation experiment at observation 1. Its manifest had 360 pending rows, its initial state had no events or provider pacing history, and there were zero official v2.5 raw observations. No v2.5 API request was sent during implementation. The implementation and prospective freeze records were reviewed and frozen at commit `87d3158`, tagged `v2.5.0-freeze`. Official v2.5 collection subsequently produced preserved observations before the prospective stop.

## Frozen v2.5 inputs (historical)

- Task set: `prompts/tasks/final_2.0.0.jsonl` (SHA-256 `ef0aff59f8a3934f65379d34036848652b7b5593f595ffa4b449a15af021546b`)
- Model set: `config/api_model_set_1.3.0.json` (SHA-256 `554cd8d8d011639c46d9d2c0280f8b08c451ea475bc2b8e2ec4006c8ab75b1e4`)
- Prompt template: `prompts/prompt_template_v2.5.0.md` (SHA-256 `8d3971d6f9f86dfd98a4b5c49c0c13d734b7f650744da682225195f2ea49b528`)
- Manifest: `manifests/api_final_v2.5.0_manifest.csv` (SHA-256 `c7911420181f090a16df33ed041caa800d5859e8e9a30882655b4ca02e72c438`)
- Initial state: `data/final/api_batch_state_v2.5.0.json` (SHA-256 `9c2816a76618a9edbab32648e7b7529ffdd66e17587a786757a79f6cb9c3d825`)
- Freeze record: `config/experiment_freeze_v2.5.0.json` and `docs/experiment_freeze_v2.5.0.md`

## v2.5 protocol (historical)

The sole experimental change from v2.4 is `max_output_tokens: 12000 → 16000`. The 30 final-2.0.0 tasks, task wording, wrapper and rendered prompt bytes, four exact model IDs and API providers, provider pins, no-fallback and no-tools interface, single user message, no prior context, temperature 0.6, top_p 0.95, omitted seed, retry/backoff, failed-observation continuation, truncation handling, and zero artificial pacing remain unchanged. Failed and truncated observations are preserved and excluded from primary SHR/PHR denominators.

The 30 v2.5 rendered prompts are byte-identical to v2.4. The dry run selects `API-v2.5-AUTH-FED-01-M1-R01`, OpenRouter, collection order 1, with `wait_seconds: 0.0`.

## Historical versions

v2.0–v2.4 remain separate methodological evidence and are excluded from v2.5 primary analysis. v2.3 stopped on its frozen non-retryable failure rule; v2.4 retained the continuation amendment and stopped prospectively because of the observed truncation burden. Their frozen inputs, raw responses, and collection behavior have not been altered for v2.5.
