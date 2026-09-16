# API Model and Collection Protocol

## Status and Scope

This document defines the frozen API protocol for the official main study before data generation. Model set `api-model-set-1.0.0` and task set `final-2.0.0` were frozen on 2026-09-16. No official API response had been generated at freeze time.

The previous comparison of ChatGPT Web, Gemini Web, Codex CLI, and Antigravity CLI is superseded before official final collection. Historical pilot artifacts remain pilot data and are excluded from the 360-generation main experiment. The API models are not proxies for those products. The comparison unit is one frozen model/API condition.

## Frozen Conditions

| Condition | API provider | Exact model ID | Model family |
| --- | --- | --- | --- |
| M1 | OpenRouter | `cohere/north-mini-code:free` | Cohere North Mini Code |
| M2 | Groq | `qwen/qwen3.8-27b` | Qwen 3.8 27B |
| M3 | Groq | `openai/gpt-oss-120b` | GPT-OSS-120B |
| M4 | OpenRouter | `nvidia/nemotron-3-ultra-550b-a55b:free` | NVIDIA Nemotron 3 Ultra 550B A55B |

Generic routers such as `openrouter/free` are prohibited. No model or endpoint may be silently substituted. If a frozen model becomes unavailable during official collection, stop that condition, preserve the failure evidence, record the event in the decision log, and make no methodological substitution until a prospective decision is approved.

## Experimental Size

The main study is exactly:

```text
30 tasks × 4 fixed model/API conditions × 3 independent runs = 360 generations
```

Pilot, exploratory, and smoke outputs are separate and excluded. The frozen official manifest is `manifests/api_final_v2.0.0_manifest.csv`; it contains 360 pending rows with `task_set_version`, `model_set_version`, exact `model_id`, `api_provider`, model condition, provider pin, repetition, prompt hash, and collection order. Existing v1 manifests and identifiers are not reused. The row contract is `schemas/api_manifest_row.schema.json`.

## Common Interaction Protocol

Each observation is a fresh, independent HTTP request with exactly one user message containing the exact rendered prompt. There is no system message, earlier conversation, follow-up, model-specific hint, browsing, web search, retrieval augmentation, function or tool definition, function or tool call, code execution, or external file not embedded in the frozen prompt.

No request contains a `tools` member. Both Groq models explicitly send `tool_choice: "none"`; this prevents local function calls and Groq-hosted browser-search or code-interpreter use. Groq Compound is not used. Both current OpenRouter endpoints expose `tool_choice` support and therefore also use explicit `tool_choice: "none"` with no tools. If a future selected OpenRouter endpoint rejects that explicit setting, the reviewed configuration must use omit-only mode (no `tools` and no `tool_choice`) and document the evidence; it must never enable a tool as a workaround.

The frozen common sampling values are:

- temperature: `0.6`
- top-p: `0.95`
- maximum output tokens: `6000`
- seed: `not_controlled`

The metadata preflight confirms that all four current conditions expose temperature, top-p, and an output limit of at least 6000 tokens. OpenRouter uses `max_tokens`; Groq uses `max_completion_tokens`. If a provider or selected underlying endpoint later cannot support these values consistently, record the incompatibility and suspend freezing rather than emulating or silently dropping the parameter. No fixed seed is used because consistent seed semantics have not been established across all four endpoints; the three runs are intended to retain stochastic variation.

## OpenRouter Provider Preflight and Pinning

The freeze procedure was:

1. Run the read-only preflight against each exact model ID.
2. Preserve the timestamped endpoint response summary, including endpoint provider name, routing slug/tag, status, maximum completion length, quantization when exposed, and supported parameters.
3. Choose one available underlying provider for each OpenRouter model using prospectively documented criteria. Do not invent names or slugs.
4. Write the exact selected provider display name and routing slug into the model-set configuration, set `pinning_status` to `pinned`, keep `allow_fallbacks` false, and keep `require_parameters` true.
5. Confirm Groq model availability and the common parameter surface.
6. Confirm and record each condition's no-tools request mode.
7. Change the configuration status to `frozen_for_collection` and parameter compatibility to `confirmed` only after researcher approval.

The generation request pins an OpenRouter condition with `provider.order` containing the one reviewed slug, `provider.allow_fallbacks: false`, and `provider.require_parameters: true`. Routing metadata is requested and the selected provider returned by OpenRouter is recorded for every generation.

`require_parameters: true` means OpenRouter may route only to an endpoint that supports every parameter actually sent, including `tool_choice` when explicit no-tool mode is selected. It cannot establish compatibility for a model with no available endpoint.

If a free endpoint cannot be pinned, document the technical evidence and methodological decision, set `pinning_status` to `unavailable`, and explicitly approve `allow_unpinned_after_documented_decision`. Even then fallbacks remain disabled where supported, and the resolved provider must be captured per generation. Provider changes are protocol deviations and must never be hidden.

## Retry and Failure Policy

Infrastructure retries are permitted only after:

- HTTP 429;
- network or transport failure; or
- HTTP 5xx when no valid model response was obtained.

The frozen schedule permits at most three retries after the initial attempt, with minimum delays of 2, 5, and 10 seconds. For HTTP 429, the collector uses the greater of the configured delay and a valid provider `Retry-After` value. Every attempt is timestamped and its status or transport failure is preserved. Official requests are sequential; no concurrent official requests are permitted, and sampling parameters are never changed to work around a limit.

No content retry is permitted. A valid model response is the observation even when it is poor, incomplete, uses no external package, contains no package-name hallucination, or differs from another condition. A successful HTTP response that is malformed is preserved and marked failed without a content-motivated retry.

`finish_reason: "length"` is a provider-valid, terminal official experimental observation and is never a retry trigger. The collector preserves it under its original official run ID, preserves the exact raw provider response and exact visible assistant content (including an empty string), records `response_completion_status: "TRUNCATED"`, and retains exposed reasoning metadata, token usage, and finish reason. It must never be regenerated merely because it is truncated.

For primary SHR/PHR analysis, a `TRUNCATED` observation is not a completed generation. The primary SHR denominator is completed, non-truncated generations eligible for analysis. The primary PHR occurrence population is eligible external npm package recommendations extracted from completed, non-truncated generations. Truncated observations must never be mixed into primary SHR or PHR estimates.

Truncated outputs remain preserved research-dataset observations. Dataset-quality reporting must separately state scheduled runs, completed runs, truncated runs, infrastructure failures, overall truncation rate, truncation rate by model, and truncation rate by task category. Truncated outputs may later be described qualitatively or included in an explicitly labelled sensitivity analysis, but those results must remain separate from primary SHR/PHR results. This rule was frozen prospectively before the first official API generation.

## Preservation and Metadata

For every logical generation, the collector reserves a new run directory before transmission and refuses any existing directory. It preserves:

- `prompt.txt`: exact rendered prompt bytes;
- `request.json`: exact request body without credentials;
- `attempts/attempt-NN/http_response.bin`: exact body for every HTTP response, including retryable errors;
- safe response headers for each HTTP attempt;
- `provider_response.json`: exact successful provider response bytes;
- `response.md`: exact assistant content encoded as UTF-8;
- `metadata.json`: run identity, timestamps, hashes, request model, returned model, API provider, resolved underlying provider, sampling values, token usage, finish reason, provider response identifier, safe request/HTTP metadata, retry history, and protocol deviations.

Prompt, request, provider-response, and assistant-response SHA-256 values are recorded. Authorization headers and API keys are never written. Only `OPENROUTER_API_KEY` and `GROQ_API_KEY` are read from the environment.

Response content is preserved before any dependency extraction, validation, classification, or risk analysis. Generated code remains inert research data and must never be executed or used to install dependencies.

## Collector Controls

`scripts/preflight_api_models.py` performs read-only model and endpoint inspection and sends zero generation requests. It distinguishes presence in the active OpenRouter model catalog from a historical per-model record and records an empty endpoint list as unavailable. `scripts/collect_api_run.py` handles one selected manifest row and one logical generation. It refuses to operate while the model set is a candidate, parameter compatibility is unconfirmed, no-tools behavior is unresolved, or an OpenRouter condition is not pinned. It never includes `tools` and never sends a seed. `scripts/collect_api_batch.py` preserves manifest order, reserves durable provider pacing state, and invokes the one-row collector sequentially.

The completion POST transport uses `requests` 2.33.1 over its conventional HTTP/1.1 stack (`urllib3` 2.7.0). It sends `User-Agent: ai-hallucination-study/1.0`, `Accept: application/json`, `Content-Type: application/json`, and `Authorization: Bearer <environment credential>`. Redirect following is disabled, the exact UTF-8 JSON bytes from `request.json` are sent as the body, and the normal `requests` environment-proxy behavior is retained; no proxy variables were present during the 2026-09-16 correction and re-smoke. Credentials are never serialized. This is a normal API client with no browser impersonation, header rotation, proxy rotation, Cloudflare bypass, or fingerprint spoofing.

## Initial Rejected-Candidate Preflight — 2026-09-16

No completion endpoint was called. The first metadata preflight found OpenRouter `qwen/qwen3-coder:free` and `deepseek/deepseek-r1-0528:free` absent from the active model catalog with zero runnable endpoints. They generated no experimental data and were replaced before official collection solely because endpoint availability and reproducible access failed. No task output or hallucination result influenced replacement.

## Replacement-Condition Preflight — 2026-09-16

The second GET-only preflight completed at `2026-09-16T05:44:20.937157Z` and recorded `generation_requests_sent: 0`.

- M1 OpenRouter `cohere/north-mini-code:free`: active; context 256,000; maximum completion 64,000. Its only endpoint is provider `Cohere`, slug `cohere`, endpoint `cohere/north-mini-code-20260617:free`, status value `0`, and zero prompt/completion price. It supports `temperature`, `top_p`, `max_tokens`, `tools`, `tool_choice`, `seed`, `reasoning`, and `include_reasoning`. Quantization is exposed exactly as `unknown`.
- M2 Groq `qwen/qwen3.8-27b`: active preview model; context 131,042; maximum completion 16,384. Metadata exposes temperature, top-p, seed, max-token sampling, tools, and reasoning. Groq documents `max_completion_tokens`, `tool_choice: "none"`, TruePoint Numerics, and reasoning controls `none`, `default`, `low`, `medium`, and `high`. No reasoning parameter is sent; Groq documents this model's default as `none`.
- M3 Groq `openai/gpt-oss-120b`: active; context 131,072; maximum completion 65,536. Metadata exposes temperature, top-p, seed, max-token sampling, tools, and reasoning. Groq documents `max_completion_tokens`, `tool_choice: "none"`, TruePoint Numerics, and reasoning efforts `low`, `medium`, and `high`. No reasoning parameter is sent, leaving the documented default behavior intrinsic to the condition.
- M4 OpenRouter `nvidia/nemotron-3-ultra-550b-a55b:free`: active; context 1,000,000; maximum completion 65,536. Its only endpoint is provider `Nvidia`, slug `nvidia`, endpoint `nvidia/nemotron-3-ultra-550b-a55b-20260604:free`, status value `0`, and zero prompt/completion price. It supports `temperature`, `top_p`, `max_tokens`, `tools`, `tool_choice`, `seed`, `reasoning`, `include_reasoning`, and `reasoning_effort`. Quantization is exposed exactly as `unknown`.

All four conditions support temperature `0.6`, top-p `0.95`, and a 6000-token output cap. Seed remains uncontrolled and omitted. No reasoning-effort or reasoning-format parameter is sent. The exact provider response is preserved so any returned reasoning field or usage metadata remains available.

### Deterministic OpenRouter pinning decision

The prospective rule is: support every frozen request parameter; require zero cost; require an active endpoint; prefer provider-native or strongest reproducibility metadata; then use a lexical provider-slug tie-break only if still tied. Each OpenRouter model currently exposes exactly one suitable endpoint, so no performance or output comparison is involved:

- M1 selected `Cohere` / `cohere`.
- M4 selected `Nvidia` / `nvidia`.

Researcher approval was recorded and both selections are frozen with one-item `provider.order`, `allow_fallbacks: false`, and `require_parameters: true`.

## Frozen-Model Unavailability Policy

If a frozen model becomes unavailable before its first official observation, stop, document the event, and make no automatic replacement. Any replacement requires prospective researcher approval, regeneration of the affected frozen configuration, and regeneration of the official manifest before collection.

If a frozen model becomes unavailable after official observations for that model have begun, do not silently substitute another model. Stop collection for that condition, preserve all completed observations, and document the interruption. A replacement model must not be mixed under the same experimental condition. If replacement is approved, it constitutes a new condition and must be restarted consistently.

No availability or replacement decision may depend on hallucination outcomes.

## Deterministic Collection Order

Rows are grouped by repetition and task. For task position `t` and repetition `r`, the starting model is rotated by `(t + r - 1) mod 4` from `M1, M2, M3, M4`; all four conditions are then collected for that task in cyclic order. Thus the first four task blocks of R01 start M1, M2, M3, and M4 respectively, and R02/R03 receive one- and two-position offsets. The manifest's `collection_order` field freezes this sequence from 1 through 360.

OpenRouter identifies the inspected key as free-tier but exposes no numeric key limit in read-only key metadata. Its documentation states a shared free-model allowance of 50 requests/day without at least 10 purchased credits and 1,000/day with at least 10 credits. Groq's published table currently lists both M2 and M3 at 30 requests/minute, 1,000 requests/day, 8,000 tokens/minute, and 200,000 tokens/day. Account-specific limits may differ. Groq exposes rate-limit counters in response headers and `Retry-After` on 429, and those safe headers are preserved.

The completion collector uses the already-installed `requests` package; no package was installed for the transport correction. Running unit tests uses mocked transports and sends no external requests.

## Environment Variables

```text
OPENROUTER_API_KEY
GROQ_API_KEY
```

Secrets belong only in the local environment or a gitignored `.env` file. They must not appear in configuration, manifests, logs, metadata, commands committed to the repository, or test fixtures.
