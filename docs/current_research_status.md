# Current Research Status

**Last updated:** 2026-09-21 (v2.4 prospective freeze audit)
**Project:** LLM Package Hallucination Study

## Current Phase: v2.4 Prospective Freeze

The active experimental version is **v2.4.0**, governed by:
- Manifest: `manifests/api_final_v2.4.0_manifest.csv` (SHA-256: `19339dd0790405532b04fa0ed482ee80e3d9ea2860211e2984934c4f49f59abf`)
- Model configuration: `config/api_model_set_1.2.0.json` (SHA-256: `e931bf60f1b07a19e975ccd0c71f9f32ecbbd80da4001b006494555801351af4`)
- Prompt template: `prompts/prompt_template_v2.4.0.md` (SHA-256: `8d3971d6f9f86dfd98a4b5c49c0c13d734b7f650744da682225195f2ea49b528`)
- Freeze specification: `config/experiment_freeze_v2.4.0.json` and `docs/experiment_freeze_v2.4.0.md`
- Initial batch state: `data/final/api_batch_state_v2.4.0.json`

v2.4 is a fresh, separate 360-observation experiment. Zero official v2.4 API requests have been sent. All 360 manifest rows are pending.

## Dataset & Protocol Invariants

v2.4 preserves all scientific conditions from v2.3:
- **Tasks:** 30 tasks across 6 categories (5 tasks/category) in `prompts/tasks/final_2.0.0.jsonl`.
- **Rendered Prompts:** 30 rendered prompt files in `data/generated_prompts/v2.4.0/`, byte-identical to v2.3.
- **Model Conditions:** 4 conditions (M1: `cohere/north-mini-code:free` via OpenRouter pinned to `cohere`; M2: `qwen/qwen3.8-27b` via Groq; M3: `openai/gpt-oss-120b` via Groq; M4: `nvidia/nemotron-3-ultra-550b-a55b:free` via OpenRouter pinned to `nvidia`).
- **Generation Parameters:** Single user message, no prior context, stateless, no tools (`tool_choice: "none"`), temperature 0.6, top_p 0.95, max output tokens 12,000, seed omitted (`not_controlled`).
- **Infrastructure Policy:** Zero researcher-imposed artificial pacing; HTTP 429 obeys `Retry-After` / exponential backoff; configured HTTP 5xx retry up to 3 times.
- **Truncation Policy:** `finish_reason: length` is preserved exactly once as `TRUNCATED`, never retried, and excluded from primary SHR/PHR denominators.

## The v2.4 Continuation Amendment

The single operational difference between v2.3 and v2.4 is failure continuation:
- In v2.3, a non-retryable provider failure (such as HTTP 200 with empty assistant content) stopped the batch without skipping or substitution, blocking further collection.
- In v2.4, a non-retryable provider failure is preserved exactly once with full failure evidence, is never automatically retried or substituted with another model/provider, is excluded from primary SHR/PHR denominators, and is skipped on subsequent batch runs so later manifest rows continue sequentially.

## Historical Frozen Versions (Methodological Evidence Only)

All historical observations remain immutable and strictly excluded from v2.4 primary metrics:
- **v2.0:** Stopped after 2 observations due to tool calling / simulated tool markup.
- **v2.1:** Stopped after 4 observations (3 truncated at 6,000 tokens) to increase ceiling to 12,000 tokens.
- **v2.2:** Stopped after 10 observations (6 completed, 4 truncated) to remove unnecessarily conservative researcher-imposed artificial delays.
- **v2.3:** Stopped after 8 observations (3 completed, 4 truncated, 1 failed: `API-v2.3-AUTH-FED-02-M1-R01` due to OpenRouter HTTP 200 with empty assistant content) in strict accordance with the frozen v2.3 stopping rule.

## Dry-Run Verification

- Command: `python3 scripts/collect_api_batch_v2_4.py --dry-run`
- Result: `{"api_provider": "OpenRouter", "collection_order": 1, "next_run_id": "API-v2.4-AUTH-FED-01-M1-R01", "wait_seconds": 0.0}`
- No external network or LLM API calls were made.
