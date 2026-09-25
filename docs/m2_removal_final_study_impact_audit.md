# M2 Removal Final-Study Impact Audit

**Audit ID:** M2-REMOVAL-FINAL-STUDY-IMPACT-AUDIT-01

**Audit date:** 2026-09-25

**Scope:** Read-only audit of the current v2.6 frozen design, live collection evidence, HYBRID interface allocation, relevant code/tests, report notes, and freeze history.

**Change boundary:** This audit creates only this report. It does not amend v2.6 or authorize collection, regeneration, reassignment, deletion, analysis, or publication.

## 1. Executive Summary

The frozen v2.6 design contains **360 planned observations**: 30 tasks × 4 model conditions × 3 repetitions. Each of M1, M2, M3, and M4 has 90 planned rows. Removing M2 therefore removes exactly **90 rows** and leaves the mathematically correct three-model design of **270 planned observations**: 30 tasks × 3 retained models × 3 repetitions.

The verified v2.6 HYBRID assignment is 180 API / 180 manual overall. Directly filtering M2, without reassigning any retained row, produces **140 API / 130 manual** for M1/M3/M4: M1 40/50, M3 41/49, and M4 59/31. The retained split is therefore not 135/135 and must not be reported as such.

At the audit snapshot, M2 has 40 API-assigned and 50 manual-assigned rows. Eleven M2 API rows have authoritative metadata: **2 completed, 0 truncated, and 9 failed**. The other **79 planned M2 rows are pending**: 29 API-assigned and 50 manual-assigned. There are eleven M2 API raw directories, no M2 manual raw directory, and 42 M2-linked events in the live v2.6 batch-state file.

All **140 retained API-assigned rows already have preserved v2.6 raw metadata/artifacts**. The 130 retained manual rows have not been collected. The existing M1/M3/M4 evidence can be carried into the revised final study unchanged through an explicit, hash-verified provenance mapping. Regeneration is neither technically required nor methodologically desirable. Failed and truncated retained observations remain observations with their existing eligibility rules; they must not be replaced to obtain successful outputs.

The final-study amendment must be a **new frozen version, recommended `v2.7.0`**, rather than an edit to v2.6. This follows the repository's sequential experiment convention (`v2.3.0` through `v2.6.0`, each with a `vX.Y.0-freeze` tag) and is necessary because the model set, planned denominator, interface totals, comparison structure, and final-analysis population all change. A corresponding three-model set version of **`api-model-set-1.5.0`** is consistent with the existing `1.0.0` through `1.4.0` sequence.

M2 must remain preserved as superseded historical/frozen v2.6 evidence, be excluded in full from v2.7 primary and secondary final-study metrics, and be explicitly disclosed as a condition removed before final analysis because its intended automatic-generation route could not be completed consistently. The primary integrity risk is that a condition is being removed after some observations exist, which can appear outcome-dependent unless the operational reason, timing, all-condition exclusion rule, and absence of result-based motivation are documented before final analysis.

## 2. Current v2.6 Design

### 2.1 Frozen counts

The authoritative frozen manifest is `manifests/api_final_v2.6.0_manifest.csv`, SHA-256 `b2b2750b3ae4ce96a867df14117b05c12f214760ef7036d6bbf2f78e44939b7f`.

| Dimension | Frozen count |
| --- | ---: |
| Tasks | 30 |
| Model conditions | 4 |
| Repetitions | 3 |
| Planned observations | 360 |
| Rows per model | 90 |
| Rows per repetition | 120 |
| Rows per category | 60 |

| Condition | Frozen model ID | Planned rows |
| --- | --- | ---: |
| M1 | `cohere/north-mini-code:free` | 90 |
| M2 | `qwen/qwen3.8-27b` | 90 |
| M3 | `openai/gpt-oss-120b` | 90 |
| M4 | `nvidia/nemotron-3-ultra-550b-a55b:free` | 90 |
| **Total** |  | **360** |

The 30 tasks are the records in `prompts/tasks/final_2.0.0.jsonl`, SHA-256 `ef0aff59f8a3934f65379d34036848652b7b5593f595ffa4b449a15af021546b`. The task set contains five tasks in each of AUTH-FED, PKI-CRYPTO, DOC-BINARY, ENT-INT, DATA-ADV, and DIST-OBS.

The v2.6 prompt template is `prompts/prompt_template_v2.6.0.md`, SHA-256 `8d3971d6f9f86dfd98a4b5c49c0c13d734b7f650744da682225195f2ea49b528`. All 30 files under `data/generated_prompts/v2.6.0/` exist, match their manifest hashes, and are byte-identical to the corresponding v2.5 rendered prompts.

### 2.2 Frozen versus derived/live facts

The manifest's `collection_status=pending` values are prospective frozen fields and have not been mutated as collection progressed. Current outcomes must be read from raw `metadata.json` and, where needed, the batch-state event trail. Similarly, `manifests/hybrid_assignment_v1.0.0.csv` is a post-freeze derived assignment layer, not a replacement for the v2.6 manifest.

The v2.6 freeze is anchored at commit `5247c2bccb58ecd6c86b9b7e92d800ade0378282` and tag `v2.6.0-freeze`. Later commits added M2-deferral scheduling, the HYBRID assignment, HYBRID API selection, and an offline manual-capture scaffold without editing the frozen manifest.

## 3. Current Collection State

### 3.1 HYBRID assignment totals

The authoritative route assignment for this audit is `manifests/hybrid_assignment_v1.0.0.csv`, SHA-256 `e4b9295b2efc0fe639092161561e915c1d0c47f9a545df2699f7fe12595dd54f`.

| Condition | API assigned | Manual assigned | Total |
| --- | ---: | ---: | ---: |
| M1 | 40 | 50 | 90 |
| M2 | 40 | 50 | 90 |
| M3 | 41 | 49 | 90 |
| M4 | 59 | 31 | 90 |
| **v2.6 total** | **180** | **180** | **360** |

These are assignments, not success counts. The allocation preserved every API attempt that existed at its 119-row derivation baseline and filled remaining per-model API quotas using earliest eligible frozen manifest order.

### 3.2 Live finalized API metadata by model

At the audit snapshot, raw v2.6 metadata gives the following current state:

| Condition | Raw/API metadata directories | Completed | Truncated | Failed | Planned rows without raw metadata |
| --- | ---: | ---: | ---: | ---: | ---: |
| M1 | 40 | 27 | 10 | 3 | 50 |
| M2 | 11 | 2 | 0 | 9 | 79 |
| M3 | 41 | 36 | 0 | 5 | 49 |
| M4 | 59 | 42 | 6 | 11 | 31 |
| **Total** | **151** | **107** | **16** | **28** | **209** |

For the retained conditions, the raw directory counts exactly equal their API assignment counts: 40 M1 + 41 M3 + 59 M4 = 140. Thus all retained API positions have already been attempted and finalized. Their remaining 130 rows are exactly their manual assignments; no manual observation directory exists at the audited path.

The live state file is `data/final/api_batch_state_v2.6.0.json`, updated at `2026-09-24T03:17:10.643089Z` and currently SHA-256 `1a3af56d138d3da1c3e67c1f04f55b27e4ab5d0ec786ab31d7c2cd17cb6b695c`. This is a rolling operational file and is already modified relative to `HEAD`; its current hash is an audit-snapshot fact, not the prospective initial-state hash in the freeze record.

## 4. M2-Specific State

### 4.1 Counts

| M2 measure | Count |
| --- | ---: |
| Planned | 90 |
| API assigned | 40 |
| Manual assigned | 50 |
| API attempted/finalized | 11 |
| Completed | 2 |
| Truncated | 0 |
| Failed | 9 |
| Pending, API assigned | 29 |
| Pending, manual assigned | 50 |
| **Pending, total** | **79** |

The pending count is defined as planned M2 rows without a finalized API metadata directory and without a manual artifact. It is not inferred from the frozen manifest's unchanged `pending` column.

M2's nine failures comprise three `http_status_402` failures and six HTTP-200/no-non-empty-assistant-content failures. The repository documents that the first post-paid-access empty-content failure consumed 32,768 completion tokens, of which 32,767 were provider-reported reasoning tokens. Two later M2 rows completed normally. These are operational outcomes only; this audit does not inspect or compare the substantive research results in the completed M2 responses.

### 4.2 Every existing M2 API artifact directory

Every directory below is under `data/final/raw/`. `metadata` and `response` hashes are SHA-256; `—` means no `response.md` exists. No directory may be altered or removed.

| Order | Run directory | Status | Recorded reason | Files present | Metadata hash | Response hash |
| ---: | --- | --- | --- | --- | --- | --- |
| 2 | `API-v2.6-AUTH-FED-01-M2-R01/` | failed | `http_status_402` | `prompt.txt`, `request.json`, `metadata.json`, `attempts/attempt-01/{http_response.bin,response_headers.json}` | `cc686b6f9e6fe4df2c2d10aa300ede1adaae4182ac2fd0b5a5b6edfb6e0bf2e7` | — |
| 5 | `API-v2.6-AUTH-FED-02-M2-R01/` | failed | `http_status_402` | same five-file pattern, attempt 01 | `dde90033f11447a730c8f3a8ab57e2aaf8bde9dfe60f0c2b0f81f1b2fe7b16b2` | — |
| 12 | `API-v2.6-AUTH-FED-03-M2-R01/` | failed | `http_status_402` | same five-file pattern, attempt 01 | `5438ef6d9e1f48523f362bda8ceec7e83c9c70ce3b5f91d91c6aa9517afe518c` | — |
| 15 | `API-v2.6-AUTH-FED-04-M2-R01/` | failed | no non-empty assistant content | same five-file pattern, attempt 01 | `aa3cdaa5e28a6846c132b5de2434005779fda6471e5daeafdb6216eda6881b32` | — |
| 18 | `API-v2.6-AUTH-FED-05-M2-R01/` | completed | `finish_reason=stop` | failed-pattern files plus `provider_response.json`, `response.md` | `af1e2632387ce53967f73e4feff66c871d5878bcbbaf4c6e639adebb8a7a16b7` | `ca20837ce5ea8390868bb495018dc875d63b906fb1802e2dbbfeaf803ee7a11f` |
| 21 | `API-v2.6-PKI-CRYPTO-01-M2-R01/` | failed | no non-empty assistant content | five-file pattern, attempt 02 | `eb5eedb09fe7f2c9ec4a7fb45abe3c3913073f5209a2b3e0671165537807e11d` | — |
| 28 | `API-v2.6-PKI-CRYPTO-02-M2-R01/` | failed | no non-empty assistant content | five-file pattern, attempt 01 | `28f35a5a90e4499d243ed6a0953fd91a1c80e8c42895e9bd69310e20ff5b3abd` | — |
| 31 | `API-v2.6-PKI-CRYPTO-03-M2-R01/` | failed | no non-empty assistant content | five-file pattern, attempt 01 | `9859655c8b80b0ae861def4d3774ce6268c9d85ef1541b6a8eaaa99b91c791ca` | — |
| 34 | `API-v2.6-PKI-CRYPTO-04-M2-R01/` | failed | no non-empty assistant content | five-file pattern, attempt 02 | `e4c697c26c0ecaf4a9ab926c14feab719d56010cadf14eeba34052c003592c2a` | — |
| 37 | `API-v2.6-PKI-CRYPTO-05-M2-R01/` | completed | `finish_reason=stop` | failed-pattern files plus `provider_response.json`, `response.md` | `c382103ce8d5f2c9b4fff9625a22aa557de64b6f916d9305a4c2748658f85954` | `1c2aac1c72a5c185e4d26f08c56e6cd157158806060e908d825716ac9bc7866b` |
| 44 | `API-v2.6-DOC-BINARY-01-M2-R01/` | failed | no non-empty assistant content | five-file pattern, attempt 01 | `8410895f9da0b60ec0d7d270bd63e501559d932c3a589fda9c5317385771789c` | — |

For the failed rows, the exact `http_response.bin` and `response_headers.json` are preserved inside the stated attempt directory. The two completed rows additionally preserve provider response JSON and assistant response bytes. Each directory also contains a prompt whose hash equals the corresponding frozen manifest prompt hash.

### 4.3 M2 collection-state and assignment artifacts

M2 is also represented in these non-raw artifacts:

- `manifests/api_final_v2.6.0_manifest.csv`: all 90 frozen M2 planned rows.
- `manifests/hybrid_assignment_v1.0.0.csv`: 40 M2 API assignments and 50 M2 manual assignments.
- `data/final/api_batch_state_v2.6.0.json`: 42 events linked to M2 run IDs: 11 reservations, 9 terminal collector failures, 3 batch-stop events, 16 preserved-failure skips, 2 completions, and 1 preserved-completion skip.
- `config/api_model_set_1.4.0.json` and `config/experiment_freeze_v2.6.0.json`: the frozen M2 identity, Darkbloom route, and 32,768-token ceiling.
- `docs/experiment_freeze_v2.6.0.md`, `docs/research_progress_log.md`, `docs/final_paper_notes.md`, `docs/current_research_status.md`, and `docs/decision_log.md`: design and operational narrative.
- `reports/hybrid_assignment_v1.0.0_report.md`: the full M2 assignment listing and original allocation verification.

There is **no existing `data/final/manual_raw/v2.6.0/` observation tree**, and therefore no M2 manual response or manual metadata artifact to preserve at the audit snapshot. There is also no v2.6 response-inventory output under `results/`; current authoritative M2 outcome counts come from raw metadata plus the state trail.

## 5. Proposed Three-Model Design

The correct proposed design is:

> 30 tasks × 3 retained model conditions × 3 repetitions = **270 planned observations**.

| Condition | Planned rows | Rows per repetition | Rows per category |
| --- | ---: | ---: | ---: |
| M1 | 90 | 30 | 15 |
| M3 | 90 | 30 | 15 |
| M4 | 90 | 30 | 15 |
| **Total** | **270** | **90** | **45** |

Exactly 90 M2 rows are excluded. Each retained task still has one row for each of M1/M3/M4 in R01, R02, and R03. Thus task coverage, per-model replication, category coverage, and within-model balance remain intact.

Retaining the existing M1/M3/M4 route assignments produces a complete 270-row protocol **without reassigning any retained row**, subject to one explicit design disclosure: the inherited route totals are 140 API / 130 manual, not a 50/50 overall split. The design remains operationally valid if interface is treated as recorded provenance and the analysis does not claim equal interface balance. Because route and model are unevenly associated, any analysis of model differences must acknowledge possible interface confounding and should stratify or adjust by interface where supported. Reassigning already-frozen retained rows merely to force 135/135 is not recommended.

## 6. Retained API/Manual Assignment Counts

| Retained condition | API | Manual | Total |
| --- | ---: | ---: | ---: |
| M1 | 40 | 50 | 90 |
| M3 | 41 | 49 | 90 |
| M4 | 59 | 31 | 90 |
| **Retained total** | **140** | **130** | **270** |

The retained assignment is the exact result of filtering the verified v2.6 assignment on `model_condition_id != M2`. It preserves all 140 retained API attempts and all 130 not-yet-collected manual positions.

The removal changes only the final-study cohort membership. It does not turn an API row into a manual row, turn a manual row into an API row, replace a failure, or authorize a new attempt.

## 7. Provenance Preservation Strategy

### 7.1 What a pure M2 filter preserves

A deterministic filter of the v2.6 manifest and HYBRID assignment can preserve:

- all 30 task identities and the exact `final-2.0.0` task-set hash;
- all 30 rendered prompt byte hashes;
- R01/R02/R03 repetition identities;
- M1, M3, and M4 model identities, providers, pins, and generation settings;
- every retained API/manual assignment;
- every retained raw observation, including completed, truncated, and failed artifacts;
- the original v2.6 run ID and original collection-order provenance.

The filter must be mechanical and tested as an exact set difference: `v2.7 retained IDs = v2.6 IDs − all M2 IDs`. No outcome field may influence membership.

### 7.2 Identity and ordering rule

Raw evidence must not be renamed or copied into a misleading new raw namespace. The safest design is to keep the immutable v2.6 source run ID as the evidence identity and add a v2.7 cohort/provenance mapping that records, at minimum:

- v2.7 cohort order, if a contiguous 1–270 order is required by new tooling;
- source v2.6 `collection_order`;
- source v2.6 `run_id`;
- task, category, repetition, and model condition;
- retained collection interface;
- source manifest and assignment hashes;
- raw metadata/response paths and hashes where present;
- inclusion status `retained_from_v2.6` or pending status for uncollected manual rows.

If the new manifest introduces `API-v2.7-*` logical IDs, a one-to-one source-run mapping is mandatory and downstream tools must resolve source artifacts through it. It would be incorrect to alter the existing raw metadata's `run_id` or to present a copied response as newly generated under v2.7. An identity-preserving cohort manifest using the original source run IDs is preferable if the new schema and collectors can support it.

### 7.3 Reuse decision

**Retained M1/M3/M4 evidence is reusable without regeneration: YES.** The removal of M2 does not change the retained prompts, tasks, repetitions, conditions, parameters, or assignments. Provenance mapping, not regeneration, is the required mechanism. Regeneration would discard valid frozen observations, change stochastic draws and timestamps, and conflict with the preserve-once failure/truncation rules.

### 7.4 M2 treatment

All M2 evidence should be:

1. preserved unchanged as superseded historical/frozen v2.6 evidence;
2. excluded from all v2.7 final-study metrics and comparative figures, including both completed M2 outputs;
3. reported in methodology/data-quality provenance as an excluded condition;
4. described as removed before final analysis because the intended collection route could not be completed consistently; and
5. never deleted, rewritten, retried for inclusion, or selectively used in final metrics.

## 8. New-Version Requirements

### 8.1 Version decision

**A new experiment version is required: YES. Recommended identifier: `v2.7.0`.**

Editing v2.6 would break its frozen hash chain and obscure the fact that collection began under a four-condition, 360-row, 180/180 plan. The repository consistently uses a minor experiment increment with patch zero for a prospective design/protocol change and an annotated `vX.Y.0-freeze` tag. The next consistent experiment identifier is therefore `v2.7.0`, with a future `v2.7.0-freeze` tag only after implementation, audit, and approval. This audit does not create or authorize that tag.

The next model-set identifier should be `api-model-set-1.5.0`, containing only M1, M3, and M4 with retained condition definitions byte-for-byte equivalent to their `api-model-set-1.4.0` entries except for unavoidable enclosing-version/schema references. The new freeze must state that pre-existing raw observations were generated under source model set 1.4.0 and are admitted by verified condition equivalence; it must not falsely rewrite their provenance to 1.5.0.

### 8.2 Required freeze assertions

The new freeze must assert and verify:

- exactly 270 unique retained cohort rows, 90 each for M1/M3/M4;
- exactly 90 rows per repetition and 45 per category;
- zero M2 rows in the v2.7 final cohort;
- exact membership equality to the v2.6 manifest after removing M2;
- exact 140/130 retained route totals and per-model route counts;
- unchanged task-set and prompt-byte hashes;
- unchanged retained model/provider/generation definitions;
- hash-verified mapping to all 140 existing retained API artifacts;
- no existing raw artifact was copied, renamed, rewritten, or regenerated;
- M2 is excluded from metrics but remains preserved in v2.6;
- the 130 pending retained rows are the inherited manual assignments only; and
- final-analysis tooling reads only the v2.7 cohort and cannot accidentally include M2.

## 9. Files Requiring New Counterparts

The following are counterparts of artifacts that actually exist in the repository. Names shown for v2.7 are recommended implementation names; none exists at this audit snapshot.

| Existing artifact | Required v2.7 counterpart or action | Reason |
| --- | --- | --- |
| `config/experiment_freeze_v2.6.0.json` | `config/experiment_freeze_v2.7.0.json` | Freeze 270-row membership, hashes, exclusion reason, and inheritance. |
| `docs/experiment_freeze_v2.6.0.md` | `docs/experiment_freeze_v2.7.0.md` | Human-readable freeze and disclosure. |
| `config/api_model_set_1.4.0.json` | `config/api_model_set_1.5.0.json` | Three retained conditions only; exact retained-condition equivalence. |
| `schemas/api_model_set_v2_6.schema.json` | versioned three-model schema, conventionally `schemas/api_model_set_v2_7.schema.json` | Current schema requires exactly four items and const version 1.4.0. |
| `manifests/api_final_v2.6.0_manifest.csv` | new v2.7 270-row cohort/official manifest | M2-free authoritative denominator and membership. |
| `manifests/hybrid_assignment_v1.0.0.csv` | new, separately versioned 270-row assignment artifact; do not overwrite v1.0.0 | Preserve retained 140/130 assignments and source identities. A major assignment version such as `hybrid_assignment_v2.0.0.csv` is appropriate because cohort membership changes. |
| `reports/hybrid_assignment_v1.0.0_report.md` | matching new assignment verification report | Verify 270 rows, 140/130 totals, and no reassignment. |
| `data/final/api_batch_state_v2.6.0.json` | `data/final/api_batch_state_v2.7.0.json` or an explicitly named v2.7 collection-state counterpart | New manifest hash and future operational events must not be appended to v2.6 state. The freeze must separately anchor the inherited v2.6 state snapshot. |
| `prompts/prompt_template_v2.6.0.md` | `prompts/prompt_template_v2.7.0.md`, byte-identical | Matches repository versioned-freeze convention and proves no prompt change. |
| `data/generated_prompts/v2.6.0/*.txt` | `data/generated_prompts/v2.7.0/*.txt`, all 30 byte-identical, if the existing freeze convention is retained | Provides version-scoped prompt paths without changing bytes. Hash equality must be tested. |
| `scripts/create_experiment_freeze_v2_6.py` | `scripts/create_experiment_freeze_v2_7.py` | New counts, membership, inherited-evidence validation, and new hashes. |
| `scripts/collect_api_batch_v2_6.py` | v2.7-specific driver or a safely generalized collector | Current shared ordering validation is hard-coded to 360 rows; carried evidence must be skipped through verified provenance. |
| `scripts/create_hybrid_assignment_v1_0.py` | new versioned derivation/verifier | Current code requires 360 rows, includes M2, and targets 180/180. |
| `scripts/collect_hybrid_api_batch.py` | v2.7-specific counterpart or safely generalized version | Current constants pin the v2.6 manifest/assignment hashes, four conditions, and 360 rows. |
| `scripts/collect_hybrid_manual.py` | v2.7-specific counterpart or safely generalized version | Current constants pin v2.6 and write under `manual_raw/v2.6.0`. |
| `tests/test_api_v2_6.py` and HYBRID tests | new v2.7 tests; retain v2.6 tests unchanged | Protect both historical v2.6 and new v2.7 contracts. |

Additional required provenance is not currently represented by a v2.6 standalone file: the implementation needs a new, hash-verified source mapping between v2.7 cohort rows and v2.6 evidence. Its exact filename should be frozen with v2.7 rather than implied by this audit. This is a new provenance artifact, not a replacement for any raw file.

No new copy of `prompts/tasks/final_2.0.0.jsonl` is required: the existing frozen task file should be referenced by its unchanged hash. No v2.6 response inventory currently exists, so there is no inventory file to copy. After the new manifest and provenance mapping are frozen, generate new derived `response_inventory_v2.7.0.json` and `.csv` outputs using code that understands both retained API source artifacts and future manual artifacts. Do not label a filtered v2.6 inventory as v2.7 without recording its source mapping and generation timestamp.

The generic `schemas/api_manifest_row.schema.json` and `schemas/api_collection_metadata.schema.json` include M2 in their allowed enum for historical compatibility and need not have M2 removed globally. Any v2.7 cohort-level schema/validator must enforce absence of M2 at the dataset level.

## 10. Test/Validation Requirements

### 10.1 Existing tests that must remain valid

The historical v2.6 tests and hash checks must continue to pass unchanged. During this audit, the following 20 existing tests passed:

`python3 -m unittest tests/test_api_v2_6.py tests/test_hybrid_assignment.py tests/test_hybrid_api_collection.py tests/test_hybrid_manual_collection.py`

Result: **20 tests passed**. The v2.6 freeze verifier also reported PASS.

### 10.2 New or changed validation coverage

Add v2.7-specific tests for:

1. **Cohort cardinality:** 270 unique rows; M1/M3/M4 exactly 90 each; M2 exactly zero; repetitions 90 each; categories 45 each; every task/model/repetition cell occurs exactly once.
2. **Exact filter membership:** the v2.7 source-ID set equals the v2.6 manifest set minus exactly the 90 M2 IDs. No status/result criterion participates.
3. **Assignment preservation:** M1 40/50, M3 41/49, M4 59/31; totals 140/130; every retained row has the same route as v2.6.
4. **Prompt preservation:** task-set hash unchanged; template and all 30 rendered prompt files byte-identical to v2.6; every row's expected prompt hash matches.
5. **Model preservation:** all retained condition fields and generation settings match v2.6; only M2 and enclosing version/schema metadata are removed/updated.
6. **Provenance mapping:** one-to-one mapping for 270 rows; all 140 current API artifacts resolve to their original v2.6 path; metadata and response hashes match; no raw write/copy occurs.
7. **Outcome preservation:** retained metadata counts reconcile to M1 27/10/3, M3 36/0/5, M4 42/6/11 at this snapshot; tests should prefer invariant reconciliation over permanently hard-coding live counts if collection is still active.
8. **Pending/manual boundary:** exactly 130 retained manual assignments remain at snapshot; API selection cannot select them; manual selection cannot select API rows.
9. **No carried-row regeneration:** a v2.7 collector refuses or skips every mapped existing API observation, including failed and truncated rows.
10. **State isolation:** v2.7 writes only to its own state; v2.6 state hash is unchanged by all v2.7 dry runs/tests.
11. **M2 metric exclusion:** response inventory, extraction, registry validation, classification, aggregation, tables, and figures reject or exclude M2 from the v2.7 population while leaving v2.6 historical outputs untouched.
12. **Order semantics:** if v2.7 uses contiguous cohort order 1–270, verify the stored source v2.6 order for every row. Do not silently overwrite source order.
13. **Schema behavior:** three-model set accepted; two/four/duplicate conditions rejected for v2.7; historical four-model v2.6 still validates under its original schema.
14. **Freeze reproducibility:** new JSON and Markdown are deterministic apart from the prospectively fixed timestamp; all referenced paths/hashes and the source freeze/tag resolve.
15. **Report assertions:** no current-final-study text or generated table claims four conditions, 360 observations, or 180/180 after v2.7 becomes active.

Existing code with hard-coded four-model/360-row assumptions that requires a v2.7 counterpart or careful parameterization includes `scripts/create_api_manifest.py`, `scripts/collect_api_batch.py`, `scripts/create_experiment_freeze_v2_6.py`, `scripts/create_hybrid_assignment_v1_0.py`, `scripts/collect_hybrid_api_batch.py`, and `scripts/collect_hybrid_manual.py`. Existing v2.6 behavior must not be weakened while adding 270-row support.

## 11. Research-Integrity Assessment

### 11.1 Methodological threat

Removing M2 after 11 of its 90 planned rows were attempted creates a real **post-collection condition-selection threat**. A reader could suspect that the condition was removed because its observed hallucination results were favorable or unfavorable. It also changes the pre-specified four-condition comparison and removes 90 planned observations after data exist.

This threat is mitigable, but not by silence. It must be treated as a protocol amendment made before final analysis, with a new frozen version and complete preservation of the excluded condition.

### 11.2 A versus B

**A. Operational protocol infeasibility:** Repository evidence supports operational difficulty. It records three M2 HTTP 402 failures before paid access, then repeated Darkbloom responses with no non-empty assistant content. At the current snapshot, 9 of 11 attempted M2 rows failed; six failures occurred after HTTP 200 with no usable assistant content, while two rows completed. The progress log documents the paid-access gate and one 32,768-token reasoning-dominated empty-content failure.

**B. Undesirable research results:** No inspected repository decision record states that M2 is being removed because of observed package-hallucination prevalence, package identities, risk scores, or comparative performance. This audit found no documented result-based removal rationale. It also did not inspect the substantive response content for desirability.

The researcher's instruction for this audit states that the intended automatic-generation route is not operationally reliable enough to complete the collection protocol. That rationale is consistent with the operational evidence, but **the final M2-removal decision and its full recurrent evidence are not yet recorded in `docs/decision_log.md`**. The current decision log ends with HYBRID implementation decisions and must receive a new, prospectively timestamped decision during the later migration task. This audit itself must not be treated as a substitute for researcher approval or a silent methodology change.

### 11.3 Required dissertation disclosure

The dissertation should disclose:

- v2.6 was prospectively frozen for four conditions and 360 rows;
- M2 had 90 planned rows, with 11 attempted before removal: 2 completed, 0 truncated, 9 failed, and 79 pending at the decision snapshot;
- the operational failure modes, including the three initial access failures and recurrent no-usable-content outcomes;
- when the condition-removal decision was made relative to collection, package extraction/classification, and final statistical analysis;
- that the entire M2 condition, including its two completed outputs, was excluded uniformly rather than selecting individual M2 outcomes;
- that no M2 raw evidence was deleted, changed, retried for inclusion, or included in final metrics;
- that M1/M3/M4 assignments and observations were retained unchanged;
- that the new planned denominator is 270 and the inherited interface split is 140 API / 130 manual;
- that condition removal reduces external validity and prevents any final inference about M2/Qwen/Darkbloom; and
- that interface is unevenly distributed across retained models and may confound model comparisons.

The report should avoid claiming that the removal was wholly prospective in the sense of occurring before any M2 observation: it occurred after some M2 collection. It may accurately state that it occurred before final analysis if the decision is formally frozen before final metric generation. Historical interim screening must remain clearly labeled and must not be presented as the basis for removal.

## 12. Report Impact Map

| Report area | Classification | Required impact |
| --- | --- | --- |
| Chapter 1 | MINOR_UPDATE | Change scope from four to three conditions, planned N from 360 to 270, and contribution/limitation wording. Do not imply inference about M2. |
| Chapter 2 | MINOR_UPDATE | Core literature remains valid; update any passage presenting four selected conditions or Qwen/M2 as part of the final comparison. Historical discussion may remain labeled historical. |
| Chapter 3 | MAJOR_UPDATE | Replace final design, model table, denominator, route totals, manifest/freeze provenance, collection-flow description, exclusion rationale, carried-evidence mapping, and threats/limitations. |
| Chapter 4 | RESULT_DEPENDENT | Recompute all metrics, denominators, comparisons, confidence intervals/tests, quality counts, and narrative using M1/M3/M4 only. Do not merely hide an M2 series from a four-model calculation. |
| Chapter 5 | RESULT_DEPENDENT | Rework interpretation, cross-model comparison, implications, and limitations after three-model results are final. Add operational-exclusion and selection-bias discussion. |
| Chapter 6 | RESULT_DEPENDENT | Update conclusions, answers to research questions, contributions, generalizability, and future work based on the final three-model results. |
| Appendices | MAJOR_UPDATE | Add v2.7 freeze/manifest/model-set/assignment/provenance material and M2 exclusion disclosure. Preserve v2.6 and M2 evidence as historical appendices rather than deleting it. |
| Figures | RESULT_DEPENDENT | Regenerate every M1–M4/model-comparison or N=360 figure from the v2.7 cohort. Design-flow figures need a definite three-model/270/140–130 update. |
| Tables | MAJOR_UPDATE | Replace the final model/protocol/sample/assignment tables now; regenerate result tables later. Historical v2.6 tables must be labeled historical rather than rewritten. |

### 12.1 Statements that become outdated for the active final study

The following statement classes must be updated wherever they describe the active/final study:

- “four model conditions,” “four fixed model/API conditions,” “M1–M4,” and four-model comparison language;
- `30 × 4 × 3 = 360`, “360 planned observations,” “90 per condition” when used as a total-design claim, “120 per repetition,” and “60 per category”;
- “180 API / 180 manual” and “balanced evenly by collection interface”;
- the M2 row in the final model table, including `qwen/qwen3.8-27b`, Darkbloom, and 32,768 tokens;
- any diagram, legend, axis, color key, or caption showing M1, M2, M3, and M4 as final comparators;
- any denominator, comparison, recurrence description, or hypothesis framed across four models;
- statements that remaining M2 rows will be collected later under v2.6;
- any final-study claim that the current HYBRID allocation is 40/50, 40/50, 41/49, 59/31 across four conditions;
- any current-state statement using the pre-HYBRID 119-attempt snapshot (M1 16, M2 6, M3 38, M4 59) as if it were live; and
- any statement that v2.6 remains the active final experiment after v2.7 is frozen.

The most direct current locations are:

- `docs/current_research_status.md` lines 3–25: active v2.6 phase, 360 rows, four models, 180/180, M2 route, and stale 119-attempt snapshot;
- `docs/final_paper_notes.md` lines 9–18 and 342–351: final design and model table;
- `docs/final_paper_notes.md` line 38: a live 360-row inventory invariant;
- `docs/final_paper_notes.md` lines 97–113: reconciliation rows that still point to four v2.2 conditions and 360 runs;
- `docs/final_paper_notes.md` lines 134–160: the “after v2.2” results gate, tables/figures plan, four-condition limitation, and v2.2 core-evidence list;
- `docs/final_paper_notes.md` lines 465–472: 360-row and 180/180 HYBRID description;
- `docs/final_paper_notes.md` lines 368–386: duplicated “temporary” M2 deferral language that says M2 will later be collected;
- `docs/experiment_protocol.md` lines 9–11, 142, 341, and related persistence references: four-condition/360 design and an older M2/Groq description;
- `docs/api_model_protocol.md` and `docs/generation_guide.md`: old active-status/model tables, 360 totals, four-condition sequencing, and final-baseline wording must be labeled historical or superseded before being cited as the final protocol;
- `docs/methodology_update_2026-09-15.md`, `docs/methodology_update_2026-09-16.md`, and `docs/task_set_v2_design.md`: their four-condition/360 statements are valid historical decisions, but must not be quoted as the current final design without a v2.7 supersession note;
- `docs/decision_log.md` decisions describing 360/four conditions: these are historical records and should **not** be rewritten; add a new superseding decision;
- `docs/experiment_freeze_v2.6.0.md`, `config/experiment_freeze_v2.6.0.json`, and `reports/hybrid_assignment_v1.0.0_report.md`: preserve unchanged as historical v2.6 evidence and cite the new counterparts for the active final study.

Historical v2.0–v2.6 accounts can retain their original four-model/360 wording when clearly presented as historical protocol facts. The required correction is to active/final-study claims, not retroactive rewriting of evidence.

## 13. Recommended Migration Sequence

1. Stop further M2 collection and preserve the current v2.6 state/raw hashes; do not edit v2.6 artifacts.
2. Record a new researcher-approved decision in the decision log, before final analysis, stating the operational criterion, timing, counts, whole-condition exclusion, and absence of result-based selection.
3. Create the three-condition `api-model-set-1.5.0` and its versioned schema by copying M1/M3/M4 definitions exactly and removing M2 only.
4. Create a deterministic 270-row v2.7 cohort manifest as the exact v2.6-minus-M2 set. Preserve source run IDs and source order in explicit provenance even if a new contiguous cohort order is added.
5. Create a new versioned assignment artifact by filtering v2.6 assignments only; verify 140 API / 130 manual and exact per-model counts. Do not rebalance.
6. Create the source-provenance mapping and hash all existing retained metadata/responses. Reference raw evidence in place; do not copy or rename it.
7. Create isolated v2.7 state and collection helpers for the 130 inherited manual rows. Ensure no mapped API row can be regenerated.
8. Copy the prompt template/rendered prompts only if required by the established version convention; assert byte equality. Reuse the existing task file by hash.
9. Add the v2.7 freeze JSON/Markdown and all tests. Run historical v2.6 verification and new v2.7 verification together.
10. Update current-status/progress/final-paper notes after the new freeze exists. Preserve historical statements as historical records.
11. Build a v2.7 response inventory that resolves both v2.6 API source artifacts and v2.7 manual artifacts; preserve a timestamped snapshot and hashes.
12. Complete only the 130 retained manual rows under the separately approved manual-interface protocol. Preserve failures/truncations once.
13. Run extraction, validation, classification, and final metrics solely against the frozen v2.7 cohort. Add a hard assertion that M2 count is zero.
14. Regenerate final report tables/figures and disclose the amendment and its threats.
15. Commit and tag only after researcher review; this audit does not commit or tag anything.

## 14. Blocking Questions or Risks

1. **Formal rationale not yet frozen:** The repository contains operational evidence but no final decision-log entry removing M2. This must be resolved before v2.7 freeze or final analysis.
2. **Manual interface approval:** D035 explicitly states that the manual product/UI is not yet approved. The 130 retained manual rows cannot be validly collected until the interface configuration and exact model-label handling are prospectively approved and frozen.
3. **Interface/model confounding:** The retained 140/130 split is uneven by model, especially M4 59/31. The analysis plan must state how interface is handled and must not claim a balanced interface experiment.
4. **Run-ID semantics:** Creating new v2.7 IDs without explicit source mapping risks misrepresenting v2.6 responses as new observations. Keeping source identities or mapping them one-to-one is mandatory.
5. **Hard-coded 360 assumptions:** Current manifest creation, ordering, HYBRID, and several tests assume 360/four models. A superficial CSV filter will not be accepted by current collectors/verifiers.
6. **Rolling state and dirty worktree:** The audited state and two research documents have pre-existing uncommitted changes. A migration must snapshot/reconcile them without overwriting researcher work.
7. **Analysis contamination:** Any rolling v2.6-derived analysis or interim screening may contain M2. New v2.7 outputs must be regenerated from the frozen cohort, not manually edited to remove rows.
8. **Historical-versus-current prose:** Freeze records and decisions must remain historical. Updating them in place would destroy the audit trail; use superseding v2.7 records and current-status updates.
9. **Timing disclosure:** The exact approval timestamp relative to extraction/classification and review of completed M2 content should be recorded. Without it, selection-bias concerns remain harder to rebut.
10. **Scope of secondary analyses:** Decide prospectively whether excluded M2 may appear only in an operational appendix. It should not enter final scientific metrics, sensitivity estimates, or headline comparisons unless a separately labeled, justified historical analysis is approved in advance.

## 15. Evidence Index

### Frozen design and prompts

- `AGENTS.md` — repository integrity/security constraints.
- `config/experiment_freeze_v2.6.0.json` — frozen v2.6 record; current file SHA-256 `53736d8a38fb4f497fc525cff7453693cd2ed0154b0c55a14172ea39164d5719`.
- `docs/experiment_freeze_v2.6.0.md` — human-readable freeze.
- `config/api_model_set_1.4.0.json` — four frozen conditions; SHA-256 `cba4a4ec3c785132523beb860db944b5d3b0ecacc429f8d6674889f34b35ad8c`.
- `manifests/api_final_v2.6.0_manifest.csv` — 360-row frozen manifest; SHA-256 `b2b2750b3ae4ce96a867df14117b05c12f214760ef7036d6bbf2f78e44939b7f`.
- `prompts/tasks/final_2.0.0.jsonl` — 30 tasks; SHA-256 `ef0aff59f8a3934f65379d34036848652b7b5593f595ffa4b449a15af021546b`.
- `prompts/prompt_template_v2.6.0.md` — template; SHA-256 `8d3971d6f9f86dfd98a4b5c49c0c13d734b7f650744da682225195f2ea49b528`.
- `data/generated_prompts/v2.6.0/*.txt` — 30 rendered prompt artifacts.

### Assignment and collection

- `manifests/hybrid_assignment_v1.0.0.csv` — 180/180 derived route assignment; SHA-256 `e4b9295b2efc0fe639092161561e915c1d0c47f9a545df2699f7fe12595dd54f`.
- `reports/hybrid_assignment_v1.0.0_report.md` — verified per-model counts and row lists.
- `data/final/api_batch_state_v2.6.0.json` — rolling state and event trail; audit-snapshot SHA-256 `1a3af56d138d3da1c3e67c1f04f55b27e4ab5d0ec786ab31d7c2cd17cb6b695c`.
- `data/final/raw/API-v2.6-*/metadata.json` — current authoritative finalized outcomes.
- The eleven M2 directories enumerated in section 4.2 — all existing M2 raw/API artifacts.
- No `data/final/manual_raw/v2.6.0/` artifacts existed at inspection time.

### Scripts and schemas inspected

- `scripts/collect_api_batch.py`
- `scripts/collect_api_batch_v2_6.py`
- `scripts/collect_api_run.py`
- `scripts/create_api_manifest.py`
- `scripts/create_experiment_freeze_v2_6.py`
- `scripts/create_hybrid_assignment_v1_0.py`
- `scripts/collect_hybrid_api_batch.py`
- `scripts/collect_hybrid_manual.py`
- `scripts/build_response_inventory.py`
- `schemas/api_model_set_v2_6.schema.json`
- `schemas/api_manifest_row.schema.json`
- `schemas/api_collection_metadata.schema.json`
- `schemas/response_inventory_item.schema.json`

### Tests inspected/run

- `tests/test_api_v2_6.py`
- `tests/test_api_v2_6_exclude_model.py`
- `tests/test_hybrid_assignment.py`
- `tests/test_hybrid_api_collection.py`
- `tests/test_hybrid_manual_collection.py`
- `tests/test_response_inventory.py`
- `tests/test_api_freeze.py`

### Research records and report notes

- `docs/current_research_status.md`
- `docs/research_progress_log.md`
- `docs/final_paper_notes.md`
- `docs/decision_log.md`
- `docs/analysis_specification_v1.0.md`
- `docs/experiment_protocol.md`

### Git provenance inspected

- `5247c2b` / tag `v2.6.0-freeze` — prospective v2.6 freeze.
- `4bf0240` — post-freeze M2 exclusion scheduling support.
- `ce13048` — deterministic HYBRID assignment.
- `7b2a23f` — HYBRID API assignment enforcement.
- `8accdc5` — offline manual capture workflow.

### Audit conclusion

The evidence supports a new, explicitly inherited **v2.7.0** three-model final-study freeze. It does not support editing v2.6, deleting M2, reassigning retained rows, or regenerating retained evidence.
