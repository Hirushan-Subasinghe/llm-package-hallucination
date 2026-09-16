# Methodology Update — 2026-09-16

## Status and Timing

This pre-collection decision replaces the planned mixed web/CLI official workflow with four fixed model/API conditions. No official final API response had been generated when these decisions were made. Pilot material remains separate from the future official dataset and is not evidence for official results.

## API Redesign

The superseded comparison used ChatGPT Web, Gemini Web, Codex CLI, and Antigravity CLI with a mixture of manual web interaction and CLI automation. The frozen comparison uses the four exact conditions in `config/api_model_set_1.0.0.json`: M1 OpenRouter `cohere/north-mini-code:free`, M2 Groq preview `qwen/qwen3.8-27b`, M3 Groq `openai/gpt-oss-120b`, and M4 OpenRouter `nvidia/nemotron-3-ultra-550b-a55b:free`.

The motivation is to automate collection, apply one consistent stateless interaction protocol, improve reproducibility, preserve exact request and response bytes, and capture model, provider, routing, sampling, timing, token-usage, and exposed reasoning metadata more precisely. Each condition remains the combination of the exact model ID, API provider, and reviewed underlying provider routing where applicable; the models are not proxies for the superseded products.

All official requests must contain one user message and no prior context, browsing, retrieval, function tools, code execution, external files, or model-specific prompt additions. No model-specific reasoning-effort parameter is set. Intrinsic/default reasoning behavior remains part of each frozen model/API condition, while the exact provider response is preserved so exposed reasoning metadata is not discarded.

### Pre-collection model replacement

The first candidate configuration assigned M1 to OpenRouter `qwen/qwen3-coder:free` and M2 to OpenRouter `deepseek/deepseek-r1-0528:free`. The read-only preflight on 2026-09-16 found both absent from the active model catalog with zero runnable endpoints. They were rejected as candidate conditions and replaced prospectively by M1 OpenRouter `cohere/north-mini-code:free` and M2 Groq `qwen/qwen3.8-27b`.

This replacement occurred before any official final generation. Neither rejected model generated experimental data, and no result, package recommendation, or observed hallucination rate influenced the change. Endpoint availability and reproducible provider access were the only selection criteria. The rejected IDs remain solely as provenance of the pre-collection decision.

## Dependency-Intensive Task Set and Sample Size

Frozen task set `prompts/tasks/final_2.0.0.jsonl` contains 30 dependency-intensive Node.js/npm tasks: five tasks in each of six specialized categories (`AUTH-FED`, `PKI-CRYPTO`, `DOC-BINARY`, `ENT-INT`, `DATA-ADV`, and `DIST-OBS`). It replaces the v1 general functional set for official collection.

Following a read-only methodological audit, 16 previously warned prompts received minimal pre-freeze scope edits to reduce response-volume confounding. The specialized standards, package selection, exact versions and APIs, capability claims, and interoperability requirements remain. Revised prompts request core implementation files, representative fixtures and setup, essential validation, and focused tests while excluding unrelated platform boilerplate. Task IDs, categories, count, version, and neutral package-selection wording are unchanged.

The frozen `prompts/tasks/final_2.0.0.jsonl` SHA-256 is `ef0aff59f8a3934f65379d34036848652b7b5593f595ffa4b449a15af021546b`. The template and per-prompt hashes are recorded separately in `docs/experiment_freeze_2026-09-16.md`.

The official design remains:

```text
30 tasks × 4 fixed model/API conditions × 3 independent generations = 360 official generations
```

The primary outcome remains package-name hallucination under the existing package classification rules and SHR/PHR definitions. Package-version, package-API, and package-capability hallucinations are secondary findings and must not be merged into the primary numerator or denominator. General code defects remain outside those hallucination categories unless the evidence requirements for a package-specific claim are met.

### Prospective treatment of truncated API observations

Before the first official API generation, the study freezes the following clarification. A provider-valid response with `finish_reason: "length"` is an official experimental observation with operational status `TRUNCATED`. Preserve it under its original official run ID without regeneration, including the exact raw provider response, exact visible assistant content even when empty, exposed reasoning metadata, token usage, and finish reason.

For primary SHR/PHR analysis, `TRUNCATED` is not a completed generation. The primary SHR denominator consists only of completed, non-truncated generations eligible for analysis. The primary PHR occurrence population consists only of eligible external npm package recommendations extracted from completed, non-truncated generations. Truncated observations must not enter either primary estimate.

Truncated outputs remain part of the preserved research dataset. Report scheduled runs, completed runs, truncated runs, infrastructure failures, overall truncation rate, truncation rate by model, and truncation rate by task category separately. A later qualitative description or separately labelled sensitivity analysis may use truncated outputs, but its findings must never be mixed with primary SHR/PHR results. This clarification does not otherwise redesign SHR, PHR, the hallucination taxonomy, or the risk model.

`risk-model-1.0.0` remains the deterministic, rule-based Impact × Detectability model. It is not a machine-learning model.

## Historical v1 Provenance Present in This Repository

The repository does **not** contain `prompts/tasks/final_1.0.0.jsonl`. That path must not be cited as an existing artifact, created, or reconstructed retroactively.

The historical v1 prompt provenance actually present is:

| Artifact | Exact path | SHA-256 / hash location |
| --- | --- | --- |
| JSON prompt definitions | `prompts/prompts_v1.0.0.json` | `736daea2796cfcbb4c67621b8eddf1098c8680a590d27da94392a6685f3425a0` |
| CSV prompt definitions | `prompts/prompts_v1.0.0.csv` | `4d2a72de51e8731b154ed6328d570b88a13e8efc4ba50434bd88da4be346a07d` |
| Frozen outer template | `prompts/prompt_template_v1.0.0.md` | `0e2cb9cce6f953d24bb8810b9d1bbaf09fd5821bacd76830d99ebfcc40f52aef` |
| Thirty rendered prompts | `data/generated_prompts/v1.0.0/AUTH-01.txt` through `AUTH-05.txt`, `DB-01.txt` through `DB-05.txt`, `FILE-01.txt` through `FILE-05.txt`, `API-01.txt` through `API-05.txt`, `SEC-01.txt` through `SEC-05.txt`, and `LOG-01.txt` through `LOG-05.txt` | Each exact rendered-prompt SHA-256 is already recorded beside its path in `manifests/baseline_manifest.csv`; the pilot subset is also recorded in `manifests/pilot_manifest.csv`. |

The historical manifests are provenance for the earlier design, not a v2 manifest. Their current file hashes are `263478494a720e67a7094bf6de1e38f9571cae9ed59b3b9c606aed02f8ac1862` for `manifests/baseline_manifest.csv` and `c0df7ab54752895bab7c1a4c1f187afee187d13e05d83c916bf84e6bcce4e94a` for `manifests/pilot_manifest.csv`.

None of these historical v1 artifacts is changed by this redesign. The unversioned v0.1 files are separate earlier records and are not substitutes for a nonexistent v1 JSONL task file.

## Freeze Gates

All four replacement/current models passed the final metadata availability gate. The researcher approved the model conditions, M1/M4 provider pins, common parameters, and revised task set including 13 intentional warnings. Model set `api-model-set-1.0.0`, task set `final-2.0.0`, the neutral v2 template, 30 rendered prompts, and the 360-row official manifest were frozen before excluded smoke requests. Official collection still requires an explicit later start; a missing model or endpoint follows the predeclared no-silent-substitution policy.
