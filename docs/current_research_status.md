# Current Research Status

**Last updated:** 2026-09-23 (D036 secondary dependency-reliability metrics and D037 primary confirmed-hallucination numerator routing finalized; status reconciliation: v2.6 collection started; analysis infrastructure PIPE-05B–PIPE-09)
**Project:** LLM Package Hallucination Study

## Current phase: v2.6 official collection in progress; final analysis not yet run

v2.5 was prospectively stopped after preserved observations showed repeated 16,000-token truncation. Its raw responses, state, manifest, freeze, and prompts remain separate historical evidence and are excluded from v2.6 primary SHR/PHR. The historical v2.5 freeze remains anchored to commit `87d3158` and tag `v2.5.0-freeze`; the live v2.5 state and observations have since advanced beyond that initial freeze.

v2.6.0 is a fresh independent 360-observation experiment beginning at observation 1. At its freeze (commit `5247c2bccb58ecd6c86b9b7e92d800ade0378282`, tag `v2.6.0-freeze`), its manifest contained 360 unique pending rows, its state had no collection events or provider pacing history, and there were zero v2.6 raw observations; no v2.6 API request was sent during implementation. Official v2.6 collection began on 2026-09-22 with `API-v2.6-AUTH-FED-01-M1-R01` and is continuing in the official study repository (`~/Dev/ai-hallucination-study/data/final/raw/`), with pending M2 rows temporarily deferred because of OpenRouter paid-credit access; see `docs/research_progress_log.md` for preserved completed, truncated, and failed observations. Accidental collection artifacts from this analysis repository are quarantined and excluded from all analysis. v2.6 is intended as the final protocol version. Any remaining output-ceiling hit will be preserved as a right-censored truncation, excluded from primary SHR/PHR, and will not trigger another restart.

## Frozen prospective v2.6 inputs

- Task set: `prompts/tasks/final_2.0.0.jsonl` (unchanged from v2.5).
- Model set: `config/api_model_set_1.4.0.json`.
- Prompt template: `prompts/prompt_template_v2.6.0.md`; all 30 rendered prompts are byte-identical to v2.5.
- Manifest: `manifests/api_final_v2.6.0_manifest.csv`.
- Initial state: `data/final/api_batch_state_v2.6.0.json`.
- Freeze record: `config/experiment_freeze_v2.6.0.json` and `docs/experiment_freeze_v2.6.0.md`.

The v2.5-to-v2.6 experimental changes are model-specific output ceilings (M1 64,000; M2 32,768; M3 and M4 65,536) and moving the unchanged M2 model ID `qwen/qwen3.8-27b` from Groq to OpenRouter, pinned exclusively to Darkbloom (`darkbloom`) with fallback disabled. All other generation and collection rules remain unchanged.

## Historical v2.5 freeze snapshot

v2.4 was prospectively stopped at the documented checkpoint of 30 finalized observations: 14 completed, 12 truncated, and 4 failed (40.0% preliminary truncation). Its frozen inputs and preserved observations remain methodological evidence only. No further v2.4 collection is planned.

At its prospective freeze, v2.5.0 began as a fresh, independent 360-observation experiment at observation 1. Its manifest had 360 pending rows, its initial state had no events or provider pacing history, and there were zero official v2.5 raw observations. No v2.5 API request was sent during implementation. The implementation and prospective freeze records were reviewed and frozen at commit `87d3158`, tagged `v2.5.0-freeze`. Official v2.5 collection subsequently produced preserved observations before the prospective stop.

## Frozen v2.5 inputs

- Task set: `prompts/tasks/final_2.0.0.jsonl` (SHA-256 `ef0aff59f8a3934f65379d34036848652b7b5593f595ffa4b449a15af021546b`)
- Model set: `config/api_model_set_1.3.0.json` (SHA-256 `554cd8d8d011639c46d9d2c0280f8b08c451ea475bc2b8e2ec4006c8ab75b1e4`)
- Prompt template: `prompts/prompt_template_v2.5.0.md` (SHA-256 `8d3971d6f9f86dfd98a4b5c49c0c13d734b7f650744da682225195f2ea49b528`)
- Manifest: `manifests/api_final_v2.5.0_manifest.csv` (SHA-256 `c7911420181f090a16df33ed041caa800d5859e8e9a30882655b4ca02e72c438`)
- Initial state: `data/final/api_batch_state_v2.5.0.json` (SHA-256 `9c2816a76618a9edbab32648e7b7529ffdd66e17587a786757a79f6cb9c3d825`)
- Freeze record: `config/experiment_freeze_v2.5.0.json` and `docs/experiment_freeze_v2.5.0.md`

## Protocol

The sole experimental change from v2.4 is `max_output_tokens: 12000 → 16000`. The 30 final-2.0.0 tasks, task wording, wrapper and rendered prompt bytes, four exact model IDs and API providers, provider pins, no-fallback and no-tools interface, single user message, no prior context, temperature 0.6, top_p 0.95, omitted seed, retry/backoff, failed-observation continuation, truncation handling, and zero artificial pacing remain unchanged. Failed and truncated observations are preserved and excluded from primary SHR/PHR denominators.

The 30 v2.5 rendered prompts are byte-identical to v2.4. The dry run selects `API-v2.5-AUTH-FED-01-M1-R01`, OpenRouter, collection order 1, with `wait_seconds: 0.0`.

## Historical versions

v2.0–v2.4 remain separate methodological evidence and are excluded from v2.5 primary analysis. v2.3 stopped on its frozen non-retryable failure rule; v2.4 retained the continuation amendment and stopped prospectively because of the observed truncation burden. Their frozen inputs, raw responses, and collection behavior have not been altered for v2.5.

## Analysis infrastructure status

- v2.6 remains the controlling live/final collection protocol; see the frozen v2.6 inputs and freeze record above.
- Derived analysis infrastructure is implemented and tested against synthetic fixtures only: PIPE-03 extraction, PIPE-04 registry validation, and PIPE-05 classification (pre-existing), plus the following, all added 2026-09-22: PIPE-06 risk scoring under the controlling `risk-model-1.0.0` (D032; `scripts/score_risk_findings.py`), PIPE-07 dataset construction (`scripts/build_analysis_dataset.py`), PIPE-08 primary PHR/SHR calculation (`scripts/calculate_primary_metrics.py`), and PIPE-05B/05B.1 review-required adjudication (`scripts/adjudicate_review_required_packages.py`). PIPE-09 grouped-descriptive and statistical-comparison infrastructure (`scripts/analyze_group_comparisons.py`) is also present in the working tree and passes its synthetic-fixture tests, but has no progress-log entry yet. See `docs/research_progress_log.md` for verified test results.
- Implementation status is not research-result status: no final-dataset PIPE-05B package adjudication (only four interim-checkpoint rows have been adjudicated; see `docs/research_progress_log.md`), no final risk scoring, no final PHR/SHR, and no final grouped or inferential comparison has been produced from the final v2.6 dataset.
- The existing `results/*_v2.2.0.json` derived snapshots are historical/interim artifacts from the earlier v2.2 experiment version only. Do not treat them as final study results or as a source of reportable PHR/SHR/prevalence figures.
- PIPE-05B.1 (2026-09-22) adds the `SELF_REFERENCE_OR_LOCAL_PACKAGE` adjudication outcome (adjudicator/schema `pipe-05b-adjudicator-1.1.0`), tested with synthetic fixtures at implementation; four interim v2.6 checkpoint rows have since been adjudicated (one `SELF_REFERENCE_OR_LOCAL_PACKAGE`, one `NAMESPACE_CONFUSION`, two `PACKAGE_NAME_CONFUSION`; none `CONFIRMED_HALLUCINATION`), which are interim observations, not final results. Under decision D034, D033 primary PHR and primary SHR are unchanged; adjudicated self/local references are excluded only from a separately labelled secondary/exploratory external-dependency sensitivity analysis, and unresolved external/local status (`external_dependency_eligible = null`) is reported separately.
- D037 (2026-09-23 UTC, FINALIZED; documentation only, not yet implemented): a metric-eligible row counts in the primary PHR numerator, and its response in the primary SHR numerator, when exactly one authorized path establishes `CONFIRMED_HALLUCINATION`: PIPE-05 `REVIEWED` review, or a guarded PIPE-05B `CONFIRMED_HALLUCINATION` on a PIPE-05 `REVIEW_REQUIRED` row. PIPE-07 is the single resolution point; the PIPE-05 classification is not rewritten; a key present on both paths fails closed. The PIPE-05B input must be supplied explicitly or explicitly declared absent. For `CONFIRMED_HALLUCINATION` only, this supersedes earlier statements that PIPE-05B never contributes to PHR/SHR. D033 PHR/SHR units and denominators, metric eligibility, D021, D034, and D035 are unchanged. The current PIPE-07/PIPE-08 code still counts only the PIPE-05 `REVIEWED` path, so final PHR/SHR must not be calculated until D037 is implemented and tested. D037 changes no interim numerator: none of the four interim PIPE-05B adjudications is `CONFIRMED_HALLUCINATION`, and the archived checkpoints contain no PIPE-05 `REVIEWED` rows.
- D036 (2026-09-23 UTC, FINALIZED; secondary/exploratory; documentation only, not yet implemented): defines the Dependency Failure Rate (DFR; unit = metric-eligible unique `(run_id, normalized_package)` row) and Response Dependency Failure Rate (RDFR; unit = metric-eligible completed response) for exact-name npm dependency-resolution failures. `AUTO_VALID` rows are external non-failures; self/local references are excluded; undetermined rows are excluded from point estimates and bounded; zero-package responses are RDFR negatives; truncated and failed responses are excluded. Outputs may be labelled FINAL only when no `REVIEW_REQUIRED` row is unadjudicated and no registry row is unresolved. DFR/RDFR are not hallucination rates and do not change D033 or D037. No DFR/RDFR calculator exists and no DFR/RDFR value has been calculated.
- D035 (2026-09-22 UTC): a provider `finish_reason` other than `stop`/`length` (including `error`) marks an observation failed/`FAILED` and metric-ineligible, even with partial content. `API-v2.6-AUTH-FED-04-M4-R01` is the only affected v2.6 observation. It is corrected by a derived inventory overlay (`status_correction = "D035"`); its raw artifacts are unchanged and it was not regenerated. The analysis-repository collector is hardened, but **the same collector patch has not yet been applied to the official collection repository** `~/Dev/ai-hallucination-study`. Interim screening counts before and after the correction are in `docs/research_progress_log.md` and are not final results.
- The PIPE-08 primary PHR/SHR calculator is implemented, follows the D033 units (PHR: unique `(run_id, normalized_package)` rows; SHR: completed, non-truncated responses), and has been validated with synthetic fixtures only. Real/final PHR/SHR has not yet been calculated from the final v2.6 dataset. Final reported PHR/SHR/prevalence figures must be computed only from provenance-consistent inputs — i.e., a response inventory, PIPE-03/04/05 derived outputs, and PIPE-07 datasets all built from the same collection snapshot — which for the final study means v2.6-derived inputs once v2.6 collection is sufficiently complete.
