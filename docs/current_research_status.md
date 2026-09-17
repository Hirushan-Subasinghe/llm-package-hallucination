# Current Research Status

**Last updated:** 2026-09-17 (repository-state audit)
**Project:** LLM Package Hallucination Study

## Current phase

v2.2 was prospectively stopped after 10 collected observations and remains immutable methodological evidence: 360 planned, 6 completed, 4 truncated, and 350 pending. Its observations are excluded from v2.3 primary metrics.

The frozen v2.3 experiment is ready for collection as a fresh 360-observation dataset. Its governing manifest is `manifests/api_final_v2.3.0_manifest.csv`; initial state is `data/final/api_batch_state_v2.3.0.json`; its frozen model set is `config/api_model_set_1.2.0.json`. Do not alter frozen inputs, collection state, raw observations, or configuration.

v2.3 retains all v2.2 scientific conditions but removes only researcher-imposed fixed provider spacing: requests remain sequential and the next row is attempted immediately after a successful request. Provider-enforced throttling and `Retry-After`, infrastructure retry/backoff, no-fallback routing, no tools, and the original truncation rule remain binding.

## Verified collection state

This is collection metadata, not final research results. Metadata and state evidence, rather than directory existence, determine run status.

| Run ID | Condition | Provider | Collection status | Completion status | Truncated | Completion tokens | `response.md` |
|---|---|---|---|---|---|---:|---|
| `API-v2.2-AUTH-FED-01-M1-R01` | M1 | OpenRouter | completed | COMPLETED | false | 11,347 | yes |
| `API-v2.2-AUTH-FED-01-M2-R01` | M2 | Groq | truncated | TRUNCATED | true | 12,000 | yes |
| `API-v2.2-AUTH-FED-01-M3-R01` | M3 | Groq | completed | COMPLETED | false | 8,893 | yes |
| `API-v2.2-AUTH-FED-01-M4-R01` | M4 | OpenRouter | truncated | TRUNCATED | true | 12,000 | yes |

The latest terminal event in the active state is completion of collection order 5, `API-v2.2-AUTH-FED-02-M2-R01`, at `2026-09-17T07:26:25.599723Z`. The state does not store a literal `next_run_id`; from that event and manifest order, the next pending candidate is collection order 6, `API-v2.2-AUTH-FED-02-M3-R01`.

The state records provider next-allowed times of `2026-09-17T08:11:13.891382Z` (Groq) and `2026-09-17T07:11:04.723260Z` (OpenRouter). At the audit read time (`2026-09-17T08:15:49Z`), neither recorded pacing deadline was active. No current `wait_seconds` value is stored, and none was determined by sending a request.

## Analysis handoff

- Primary package hallucination remains narrowly defined around nonexistent npm package references; truncation and interface compliance remain separate variables.
- The frozen v2.2 rule excludes `TRUNCATED` observations from primary SHR/PHR while preserving and reporting them separately. Do not retry merely because an observation is truncated.
- Raw model responses remain immutable; extraction, validation, classification, inventory, and risk records are derived artifacts.
- **Open analysis issue:** PIPE-03 must preserve occurrence-level extraction provenance and a deterministic unique normalized package-per-response view. No PHR calculation should occur until the controlling denominator wording is explicitly reconciled.

## Safe parallel work

Analysis/report preparation and synthetic-fixture tests may continue without modifying the frozen v2.2 experiment. Do not run the real collector, bypass pacing, reset state, manually advance collection order, install extracted packages, execute generated code, or register package names.
