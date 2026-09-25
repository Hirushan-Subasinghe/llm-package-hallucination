# Current Research Status

**Last updated:** 2026-09-25 (canonical worktree verification guards finalized: `scripts/verify_final_collection_v2_7.py` FINAL_COMPLETION_CHECK passes; raw evidence copied and verified in the canonical worktree. Earlier the same day: final v2.7 data collection complete; provenance checkpoint D043; tracked branches consolidated into `integration/v2.7-final`. Earlier integration-worktree update 2026-09-25: v2.7 synchronization and v2.6 relabelled historical; 2026-09-23: integrated D036 secondary dependency-reliability metrics and D037 primary confirmed-hallucination numerator routing finalized; analysis infrastructure PIPE-05B–PIPE-09)
**Project:** LLM Package Hallucination Study

## Current phase: v2.7.0 is the active final study; final data collection complete (270/270 assigned rows); evidence consolidated and verified in the canonical worktree; final analysis not yet run

### Canonical worktree

- Canonical worktree: `~/Dev/ai-hallucination-final`. Canonical branch: `integration/v2.7-final`. This worktree is the canonical location for the final v2.7 evidence, analysis, report drafting, and dissertation work. `~/Dev/ai-hallucination-study` is retained only as the historical collection origin.
- Final data collection is complete and frozen. The repository guard refuses any new collection in this worktree; read-only inspection and verification remain allowed.
- Raw API evidence has been copied byte-for-byte into this worktree and verified against the D043 inventory (1,552 files; inventory SHA-256 `1f79cdecbd573b57f5121dc04fcd5e3aadcca8d46d005cebf4628a8fa75634e7`). It remains gitignored.
- Final derived collection record: `reports/final_collection_completion_v2.7.0.json` and `reports/final_collection_completion_v2.7.0.md`.
- The original frozen collection state `data/final/collection_state_v2.7.0.json` is unchanged. It holds the pre-completion state, with the 130 manual rows `pending`.
- Two separate checks:
  - FROZEN_SNAPSHOT_CHECK, `python3 scripts/create_experiment_freeze_v2_7.py --check` (frozen script, unchanged). It fails by design after manual completion, because it compares the frozen snapshot with a live re-derivation.
  - FINAL_COMPLETION_CHECK, `python3 scripts/verify_final_collection_v2_7.py`. It passes, and is the check for the completed state (`docs/final_v2.7_canonical_worktree_validation.md`).

v2.7.0 is the active, current final study. It is the frozen v2.6.0 design with the entire M2 condition removed (integrated decision **D039**, originally recorded as D036 on `feature/data-collection`; integrated D036 is the DFR/RDFR secondary-metric decision). It was frozen at `2026-09-24T23:22:58.369305Z` and committed in `bba890d` ("experiment: establish final v2.7 three-model study"). The annotated tag `v2.7.0-freeze` points to `bba890d9aa5838f06bee4b1bd0e85d9e61b444f8`.

### Current v2.7.0 three-model design

- Retained model conditions: M1 `cohere/north-mini-code:free`, M3 `openai/gpt-oss-120b`, M4 `nvidia/nemotron-3-ultra-550b-a55b:free`. Condition IDs keep their historical identifiers and are **not** renumbered.
- Planned observations: 30 tasks × 3 model conditions × 3 repetitions = **270** (90 per retained model, 90 per repetition, 45 per category).
- Interface assignment, inherited unchanged from the v2.6 HYBRID allocation and not rebalanced: **140 API / 130 manual** (M1 40/50, M3 41/49, M4 59/31). Interface is unevenly associated with model condition, so analyses must not claim interface balance.
- M2 rows in the v2.7 manifest: **0**.
- Model set: `config/api_model_set_1.5.0.json` (`api-model-set-1.4.0` with M2 removed; the retained condition definitions are identical).
- Manifest: `manifests/api_final_v2.7.0_manifest.csv` (270 unique rows; SHA-256 `2edf2638f08a1079aadd02c174951a912aa2797b56df36997878096b29a4ed20`). Retained rows keep their original `API-v2.6-…` run IDs, task/category/repetition identities, prompt bytes, and `source_collection_order`. `cohort_order` numbers them 1–270.
- Initial collection state: `data/final/collection_state_v2.7.0.json`.
- Schema: `schemas/api_model_set_v2_7.schema.json`.
- Freeze record: `config/experiment_freeze_v2.7.0.json` and `docs/experiment_freeze_v2.7.0.md`.
- Migration verification: `docs/final_study_v2.7_migration_verification.md`. Source audit: `docs/m2_removal_final_study_impact_audit.md`.
- Freeze-tag verification: `docs/v2.7_freeze_tag_verification.md`.
- Interface allocation decision: integrated **D040** (originally D033 on `feature/data-collection`; not the integrated D033 PHR/SHR-unit decision). Manual capture scaffold: integrated **D042** (originally D035; not the integrated D035 abnormal-termination decision).
- Decision-ID collision records: `docs/final_report_support/decision_id_collision_reconciliation.md` (D036/D039) and `docs/final_report_support/remaining_decision_id_collision_reconciliation.md` (source D032–D035 → integrated D038, D040–D042; integrated D033–D035 unchanged).
- Task set, prompt template, rendered prompt bytes, model IDs, providers, pins, output ceilings, sampling parameters, retry, pacing, failure, and truncation policies are unchanged from v2.6.

**All final analysis must use the v2.7 manifest (or `final_study_rows()`) only and must assert zero M2 rows.** The downstream inventory, extraction, validation, and classification stages have not yet been wired to the v2.7 cohort.

### M2 exclusion

- M2 (`qwen/qwen3.8-27b`, OpenRouter pinned to Darkbloom) is excluded from the final study and from every v2.7 metric and denominator, including its 2 completed outputs.
- Rationale is operational: the intended automatic API route could not complete the required collection protocol consistently. At the decision snapshot, 11 of 90 M2 rows had been attempted (3 `http_status_402` failures, 6 HTTP-200 responses without non-empty assistant content, 2 completed) and 79 were pending.
- The exclusion occurred after partial M2 collection and before final analysis; it is not wholly prospective and must be disclosed as such. No package-extraction, registry-validation, classification, metric, or risk output existed for any v2.6 condition, so no empirical outcome could have motivated the removal.
- All M2 evidence is preserved unchanged as historical v2.6 evidence: the 90 M2 manifest rows, the M2 HYBRID assignment rows, M2 events in the v2.6 state, M2 in model set 1.4.0 and the v2.6 freeze, and all 11 `data/final/raw/API-v2.6-*-M2-R01/` directories (hash-listed in the v2.7 freeze).

### Evidence reuse

The 140 retained API observations (M1/M3/M4) are mapped in place to their preserved v2.6 raw evidence by run ID and SHA-256. Nothing was copied, renamed, rewritten, or regenerated, and no `API-v2.7-*` raw directory exists. Mapped observations were generated under `api-model-set-1.4.0`; that provenance is not rewritten.

### Final collection status (verified 2026-09-25)

These are collection-state counts only, not research results.

| Condition | API completed | API truncated | API failed | Manual captured | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| M1 | 27 | 10 | 3 | 50 | 90 |
| M3 | 36 | 0 | 5 | 49 | 90 |
| M4 | 42 | 6 | 11 | 31 | 90 |
| **Total** | **105** | **16** | **19** | **130** | **270** |

All 140 API-assigned rows are finalized (0 pending). Failed and truncated observations are preserved and are not retried or replaced. All 130 manual-assigned rows have completed evidence under `data/final/manual_raw/v2.6.0/` on `origin/collection/m1-manual-v2.6` (`1e06280`), `origin/collection/m3-manual-v2.6` (`ee952dc`) and `origin/collection/m4-manual-v2.6` (`fb0d56a`). These branches are verified against the frozen v2.7 manifest and are merged into `integration/v2.7-final` (see `docs/final_v2.7_tracked_branch_merge_verification.md`). No further data collection remains.

The frozen `data/final/collection_state_v2.7.0.json` still records the 130 manual rows as `pending`. It is not edited. Manual completion is recorded in the separate, non-frozen derived record `reports/final_collection_completion_v2.7.0.{json,md}`, whose agreement with the evidence is checked by `scripts/verify_final_collection_v2_7.py`.

No final PHR/SHR, DFR/RDFR, grouped comparison, or risk output exists for v2.7.0. All final findings remain `[FINAL RESULT PENDING]`.

**Timing disclosure:** 85 manual captures (M1 36, M3 49) predate the v2.7 freeze timestamp. They were reused as compatible retained v2.6 evidence, not regenerated (`reports/final_v2.7_manual_timing_provenance.md`).

**Raw evidence provenance (D043):** `data/final/raw/` remains gitignored. It is protected by `reports/final_v2.7_raw_evidence_inventory.sha256` (1,552 files, 229 run directories; inventory SHA-256 `1f79cdecbd573b57f5121dc04fcd5e3aadcca8d46d005cebf4628a8fa75634e7`) and has been copied byte-for-byte into the canonical final worktree and reverified there (1,552 files, no file outside the inventory; `docs/final_v2.7_evidence_consolidation_verification.md` §2). `data/final/api_batch_state_v2.6.0.json` is committed at SHA-256 `1a3af56d138d3da1c3e67c1f04f55b27e4ab5d0ec786ab31d7c2cd17cb6b695c`, the snapshot cited by the v2.7 collection state.

### Open items (post-collection)

- **Consolidation:** complete. The manual and analysis/report branches are merged into `integration/v2.7-final` (`docs/final_v2.7_tracked_branch_merge_verification.md`). Raw evidence is copied and verified, and the analysis-local `data/derived_checkpoints/` and `data/quarantine/` material is preserved (untracked; `docs/final_v2.7_evidence_consolidation_verification.md`). `AGENTS.md`, the repository guard, and the guard tests are reconciled with the data-bearing canonical branch (`docs/final_v2.7_canonical_worktree_validation.md`).
- **Derived final collection-state record:** done (`reports/final_collection_completion_v2.7.0.{json,md}`). `collection_state_v2.7.0.json` stays frozen.
- **Analysis pipeline:** not yet v2.7-aware. It must cover the 270-row cohort (140 API + 130 manual) and assert zero M2 rows.
- **Collection scripts are still v2.6-oriented:** `collect_hybrid_manual.py` and `collect_hybrid_api_batch.py` pin the v2.6 manifest and assignment. Collection is complete: both are now guarded, and only their read-only modes run in this worktree.

Validation at migration: full test suite 164 passed, 0 failed; `create_experiment_freeze_v2_7.py --check`, `create_experiment_freeze_v2_6.py --check`, and `create_hybrid_assignment_v1_0.py --verify` all passed.

## Superseded v2.6.0 four-model design (historical)

> **Historical / superseded by v2.7.0.** The text in this section describes the v2.6 state as of 2026-09-23 and is retained for provenance only. v2.6 is not the active final study; its four-condition, 360-observation, 180 API / 180 manual design must not be cited as the current design. All v2.6 inputs and records remain preserved unchanged.

v2.5 was prospectively stopped after preserved observations showed repeated 16,000-token truncation. Its raw responses, state, manifest, freeze, and prompts remain separate historical evidence and are excluded from v2.6 primary SHR/PHR. The historical v2.5 freeze remains anchored to commit `87d3158` and tag `v2.5.0-freeze`; the live v2.5 state and observations have since advanced beyond that initial freeze.

v2.6.0 was a fresh independent 360-observation experiment (four conditions M1–M4) beginning at observation 1, frozen under tag `v2.6.0-freeze`. Its frozen manifest remains 360 unique pending rows. As of 2026-09-23 (pre-HYBRID snapshot, now stale), the preserved raw state contained 119 API-attempted observations: M1 16, M2 6, M3 38, and M4 59. M3 API collection was then paused because the frozen Groq configuration has a documented TPM/HTTP 413 incompatibility.

The v2.6 freeze commit is `5247c2bccb58ecd6c86b9b7e92d800ade0378282`. Official v2.6 collection began on 2026-09-22 with `API-v2.6-AUTH-FED-01-M1-R01` in the official study repository. Pending M2 rows were then deferred because of OpenRouter paid-credit access, and M2 was subsequently removed before final analysis (see v2.7.0 above). Accidental collection artifacts from the analysis repository are quarantined and excluded from all analysis. The v2.6 truncation rule (right-censored, excluded from primary SHR/PHR, no restart) is inherited unchanged by v2.7.0.

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

v2.0–v2.4 remain separate methodological evidence and are excluded from v2.5 and later primary analysis. v2.3 stopped on its frozen non-retryable failure rule; v2.4 retained the continuation amendment and stopped prospectively because of the observed truncation burden. Their frozen inputs, raw responses, and collection behavior have not been altered for v2.5.

## Analysis infrastructure status

- v2.7.0 is the controlling final-study protocol (see above). The integration analysis pipeline was implemented while v2.6 was active; it has not yet been verified against the v2.7 cohort, and final analysis must use only the 270-row v2.7 manifest with zero M2 rows. Bullets below dated before 2026-09-25 describe interim v2.6-era state.
- Derived analysis infrastructure is implemented and tested against synthetic fixtures only: PIPE-03 extraction, PIPE-04 registry validation, and PIPE-05 classification (pre-existing), plus the following, all added 2026-09-22: PIPE-06 risk scoring under the controlling `risk-model-1.0.0` (D032; `scripts/score_risk_findings.py`), PIPE-07 dataset construction (`scripts/build_analysis_dataset.py`), PIPE-08 primary PHR/SHR calculation (`scripts/calculate_primary_metrics.py`), and PIPE-05B/05B.1 review-required adjudication (`scripts/adjudicate_review_required_packages.py`). PIPE-09 grouped-descriptive and statistical-comparison infrastructure (`scripts/analyze_group_comparisons.py`) is also present in the working tree and passes its synthetic-fixture tests, but has no progress-log entry yet. See `docs/research_progress_log.md` for verified test results.
- Implementation status is not research-result status: no final-dataset PIPE-05B package adjudication (only four interim-checkpoint rows have been adjudicated; see `docs/research_progress_log.md`), no final risk scoring, no final PHR/SHR, and no final grouped or inferential comparison has been produced from the final v2.7.0 dataset.
- The existing `results/*_v2.2.0.json` derived snapshots are historical/interim artifacts from the earlier v2.2 experiment version only. Do not treat them as final study results or as a source of reportable PHR/SHR/prevalence figures.
- PIPE-05B.1 (2026-09-22) adds the `SELF_REFERENCE_OR_LOCAL_PACKAGE` adjudication outcome (adjudicator/schema `pipe-05b-adjudicator-1.1.0`), tested with synthetic fixtures at implementation; four interim v2.6 checkpoint rows have since been adjudicated (one `SELF_REFERENCE_OR_LOCAL_PACKAGE`, one `NAMESPACE_CONFUSION`, two `PACKAGE_NAME_CONFUSION`; none `CONFIRMED_HALLUCINATION`), which are interim v2.6-era checkpoint observations, not final results. Under decision D034, D033 primary PHR and primary SHR are unchanged; adjudicated self/local references are excluded only from a separately labelled secondary/exploratory external-dependency sensitivity analysis, and unresolved external/local status (`external_dependency_eligible = null`) is reported separately.
- D037 (2026-09-23 UTC, FINALIZED; documentation only, not yet implemented): a metric-eligible row counts in the primary PHR numerator, and its response in the primary SHR numerator, when exactly one authorized path establishes `CONFIRMED_HALLUCINATION`: PIPE-05 `REVIEWED` review, or a guarded PIPE-05B `CONFIRMED_HALLUCINATION` on a PIPE-05 `REVIEW_REQUIRED` row. PIPE-07 is the single resolution point; the PIPE-05 classification is not rewritten; a key present on both paths fails closed. The PIPE-05B input must be supplied explicitly or explicitly declared absent. For `CONFIRMED_HALLUCINATION` only, this supersedes earlier statements that PIPE-05B never contributes to PHR/SHR. D033 PHR/SHR units and denominators, metric eligibility, D021, D034, and D035 are unchanged. The current PIPE-07/PIPE-08 code still counts only the PIPE-05 `REVIEWED` path, so final PHR/SHR must not be calculated until D037 is implemented and tested. D037 changes no interim numerator: none of the four interim PIPE-05B adjudications is `CONFIRMED_HALLUCINATION`, and the archived checkpoints contain no PIPE-05 `REVIEWED` rows.
- D036 (2026-09-23 UTC, FINALIZED; secondary/exploratory; documentation only, not yet implemented): defines the Dependency Failure Rate (DFR; unit = metric-eligible unique `(run_id, normalized_package)` row) and Response Dependency Failure Rate (RDFR; unit = metric-eligible completed response) for exact-name npm dependency-resolution failures. `AUTO_VALID` rows are external non-failures; self/local references are excluded; undetermined rows are excluded from point estimates and bounded; zero-package responses are RDFR negatives; truncated and failed responses are excluded. Outputs may be labelled FINAL only when no `REVIEW_REQUIRED` row is unadjudicated and no registry row is unresolved. DFR/RDFR are not hallucination rates and do not change D033 or D037. No DFR/RDFR calculator exists and no DFR/RDFR value has been calculated.
- D035 (2026-09-22 UTC): a provider `finish_reason` other than `stop`/`length` (including `error`) marks an observation failed/`FAILED` and metric-ineligible, even with partial content. `API-v2.6-AUTH-FED-04-M4-R01` is the only affected v2.6 observation. It is corrected by a derived inventory overlay (`status_correction = "D035"`); its raw artifacts are unchanged and it was not regenerated. The analysis-repository collector is hardened, but **the same collector patch has not yet been applied to the official collection repository** `~/Dev/ai-hallucination-study`. Interim screening counts before and after the correction are in `docs/research_progress_log.md` and are not final results.
- The PIPE-08 primary PHR/SHR calculator is implemented, follows the D033 units (PHR: unique `(run_id, normalized_package)` rows; SHR: completed, non-truncated responses), and has been validated with synthetic fixtures only. Real/final PHR/SHR has not yet been calculated from the final v2.7.0 dataset. Final reported PHR/SHR/prevalence figures must be computed only from provenance-consistent inputs — i.e., a response inventory, PIPE-03/04/05 derived outputs, and PIPE-07 datasets all built from the same collection snapshot — which for the final study means v2.7.0-derived inputs (retained M1/M3/M4 rows only) once v2.7 collection is sufficiently complete.
- Consolidation note (2026-09-25): the `feature/data-collection` collector also implements the abnormal-finish-reason rule (commit `57e51f7`, "fix(collection): preserve abnormal finish reasons as failed"). Both histories are merged in `integration/v2.7-final`, so the D035 bullet's statement that the patch had not reached the official collection repository describes the pre-consolidation state.
