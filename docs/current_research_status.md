# Current Research Status

**Last updated:** 2026-09-21 (v2.5 prospective implementation and validation)
**Project:** LLM Package Hallucination Study

## Current phase: v2.5 prepared for researcher review

v2.4 was prospectively stopped at the documented checkpoint of 30 finalized observations: 14 completed, 12 truncated, and 4 failed (40.0% preliminary truncation). Its frozen inputs and preserved observations remain methodological evidence only. No further v2.4 collection is planned.

v2.5.0 is a fresh, independent 360-observation experiment beginning at observation 1. Its manifest has 360 pending rows, its state has no events or provider pacing history, and there are zero official v2.5 raw observations. No v2.5 API request was sent during implementation. The implementation and prospective freeze records are ready for review; no commit or tag has been created.

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
