# Experiment Freeze Record — v2.7.0

Created at `2026-09-24T23:22:58.369305Z` before any final-study analysis.

v2.7.0 is the frozen v2.6.0 design with the whole M2 condition removed. Membership is the exact set difference of the v2.6 manifest minus every M2 row; no outcome field participates. Retained M1/M3/M4 rows keep their v2.6 run IDs, task/category/repetition identities, prompt bytes, and HYBRID interface assignment. Model-condition IDs are not renumbered.

## Design change

| | v2.6.0 | v2.7.0 |
| --- | ---: | ---: |
| Model conditions | 4 (M1, M2, M3, M4) | 3 (M1, M3, M4) |
| Planned observations | 360 | 270 |
| API / manual assignment | 180 / 180 | 140 / 130 |

No other protocol element changes. The retained split is inherited, not rebalanced; interface is unevenly associated with model condition.

## Frozen inputs

- Source freeze: `53736d8a38fb4f497fc525cff7453693cd2ed0154b0c55a14172ea39164d5719` (`config/experiment_freeze_v2.6.0.json`, tag `v2.6.0-freeze`)
- Task set: `ef0aff59f8a3934f65379d34036848652b7b5593f595ffa4b449a15af021546b` (`prompts/tasks/final_2.0.0.jsonl`)
- Model set: `247eec71556f2908630ec8e4d34fc5ac54a29fcf5c47cb7406dafcd67991235c` (`config/api_model_set_1.5.0.json`)
- Prompt template (reused, not copied): `8d3971d6f9f86dfd98a4b5c49c0c13d734b7f650744da682225195f2ea49b528` (`prompts/prompt_template_v2.6.0.md`)
- Manifest: `2edf2638f08a1079aadd02c174951a912aa2797b56df36997878096b29a4ed20` (`manifests/api_final_v2.7.0_manifest.csv`), 270 unique rows
- Initial collection state: `55a32c0d4a7c6ae493ca701be2dea11995792a09bdb4a9fb8f3024ca073709a6` (`data/final/collection_state_v2.7.0.json`)

## Model conditions

| Condition | Model | API provider | Provider pin | Max output tokens | API rows | Manual rows |
| --- | --- | --- | --- | ---: | ---: | ---: |
| M1 | `cohere/north-mini-code:free` | OpenRouter | `cohere` | 64000 | 40 | 50 |
| M3 | `openai/gpt-oss-120b` | Groq | `not_applicable` | 65536 | 41 | 49 |
| M4 | `nvidia/nemotron-3-ultra-550b-a55b:free` | OpenRouter | `nvidia` | 65536 | 59 | 31 |

## M2 exclusion

M2 (`qwen/qwen3.8-27b`, OpenRouter pinned to `darkbloom`) is excluded in full: 90 planned rows. Operational: the intended automatic API collection route for M2 (qwen/qwen3.8-27b via Darkbloom-only OpenRouter) could not complete the required collection protocol consistently.

At freeze, M2 had 11 preserved artifact directories (2 completed, 0 truncated, 9 failed) and 79 planned rows without an artifact. The exclusion applies to the whole condition, including completed M2 outputs. The recorded rationale uses collection outcomes only. No v2.6 package-extraction, registry-validation, classification, metric or risk output exists in the repository for M2 or any condition. The exclusion occurred after partial M2 collection and before final analysis. All M2 evidence remains preserved unchanged as historical v2.6 evidence and is excluded from every v2.7 metric and denominator.

| Preserved M2 directory | Status | Metadata SHA-256 |
| --- | --- | --- |
| `data/final/raw/API-v2.6-AUTH-FED-01-M2-R01` | failed | `cc686b6f9e6fe4df2c2d10aa300ede1adaae4182ac2fd0b5a5b6edfb6e0bf2e7` |
| `data/final/raw/API-v2.6-AUTH-FED-02-M2-R01` | failed | `dde90033f11447a730c8f3a8ab57e2aaf8bde9dfe60f0c2b0f81f1b2fe7b16b2` |
| `data/final/raw/API-v2.6-AUTH-FED-03-M2-R01` | failed | `5438ef6d9e1f48523f362bda8ceec7e83c9c70ce3b5f91d91c6aa9517afe518c` |
| `data/final/raw/API-v2.6-AUTH-FED-04-M2-R01` | failed | `aa3cdaa5e28a6846c132b5de2434005779fda6471e5daeafdb6216eda6881b32` |
| `data/final/raw/API-v2.6-AUTH-FED-05-M2-R01` | completed | `af1e2632387ce53967f73e4feff66c871d5878bcbbaf4c6e639adebb8a7a16b7` |
| `data/final/raw/API-v2.6-DOC-BINARY-01-M2-R01` | failed | `8410895f9da0b60ec0d7d270bd63e501559d932c3a589fda9c5317385771789c` |
| `data/final/raw/API-v2.6-PKI-CRYPTO-01-M2-R01` | failed | `eb5eedb09fe7f2c9ec4a7fb45abe3c3913073f5209a2b3e0671165537807e11d` |
| `data/final/raw/API-v2.6-PKI-CRYPTO-02-M2-R01` | failed | `28f35a5a90e4499d243ed6a0953fd91a1c80e8c42895e9bd69310e20ff5b3abd` |
| `data/final/raw/API-v2.6-PKI-CRYPTO-03-M2-R01` | failed | `9859655c8b80b0ae861def4d3774ce6268c9d85ef1541b6a8eaaa99b91c791ca` |
| `data/final/raw/API-v2.6-PKI-CRYPTO-04-M2-R01` | failed | `e4c697c26c0ecaf4a9ab926c14feab719d56010cadf14eeba34052c003592c2a` |
| `data/final/raw/API-v2.6-PKI-CRYPTO-05-M2-R01` | completed | `c382103ce8d5f2c9b4fff9625a22aa557de64b6f916d9305a4c2748658f85954` |

## Evidence reuse

140 retained observations map in place to preserved v2.6 evidence by run ID and SHA-256; nothing is copied, renamed, rewritten, or regenerated. Mapped API observations were generated under api-model-set-1.4.0; their M1/M3/M4 definitions are identical in api-model-set-1.5.0.

Initial status counts: completed 105, failed 19, pending 130, truncated 16.
