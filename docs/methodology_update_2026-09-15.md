# Methodology Update — 2026-09-15

> **Superseded before official final collection (2026-09-16):** The controlling API redesign and exact historical-v1 provenance record are now in [methodology_update_2026-09-16.md](methodology_update_2026-09-16.md). The material below is retained as the 2026-09-15 record. No official final data had been generated when the redesign decision was made.

## Controlling API Redesign — 2026-09-16

The official main study compares four fixed open-weight model/API conditions under one controlled request protocol. The model set is `api-model-set-1.0.0`, the candidate task set is `final-2.0.0`, and the balanced sample remains 30 tasks × 4 conditions × 3 independent runs = 360 generations. Pilot and exploratory data remain excluded.

The superseded conditions were ChatGPT Web, Gemini Web, Codex CLI, and Antigravity CLI. They are not represented by, mapped onto, or treated as equivalent to the API models. Their prompts, manifests, collection code, and pilot artifacts remain historical provenance. The new unit of comparison is the frozen model/API condition.

The exact candidate conditions are:

- M1: OpenRouter, `qwen/qwen3-coder:free`, Qwen3-Coder-480B-A35B-Instruct.
- M2: OpenRouter, `deepseek/deepseek-r1-0528:free`, DeepSeek-R1-0528.
- M3: Groq, `openai/gpt-oss-120b`, GPT-OSS-120B.
- M4: OpenRouter, `nvidia/nemotron-3-ultra-550b-a55b:free`, NVIDIA Nemotron 3 Ultra 550B A55B.

Generic router identifiers and silent model substitution are prohibited. OpenRouter underlying providers must be inspected and, where technically possible for the free endpoint, pinned prospectively with fallbacks disabled. A resolved provider is recorded on every generation. Model unavailability stops collection for that condition and requires documentation before any methodological decision.

Every generation uses one fresh API request containing exactly one user message with the exact common rendered prompt. There is no prior context, system message, model-specific hint, browsing, web search, retrieval augmentation, exposed tool or function, code execution, or external file not embedded in the prompt. The candidate common parameters are temperature `0.6`, top-p `0.95`, and maximum output tokens `6000`, subject to preflight confirmation of consistent support. Seed is `not_controlled`; no deterministic seed is forced.

Only HTTP 429, network/transport failure, or HTTP 5xx without a valid model response permits an infrastructure retry. Content quality, absence of external packages, absence of hallucination, or another condition's performance never permits retry. Every infrastructure attempt is logged, and every valid returned model response is preserved as the observation.

The candidate v2 task set replaces the v1 general functional set for official collection. It contains 30 dependency-intensive Node.js/npm tasks across `AUTH-FED`, `PKI-CRYPTO`, `DOC-BINARY`, `ENT-INT`, `DATA-ADV`, and `DIST-OBS`, with five tasks per category. The v1 prompt assets remain unchanged. The v2 task file is a review candidate only: no v2 prompts or manifest are rendered or frozen in this step.

### Updated Research Questions

**RQ1:** What is the prevalence of npm package-name hallucinations produced by contemporary open-weight LLMs when solving dependency-intensive Node.js/npm tasks?

**RQ2:** When valid npm packages are selected, to what extent do generated solutions contain package-version, package-API, or package-capability hallucinations?

**RQ3:** How do package-related hallucination frequency, type, and risk differ across the evaluated open-weight models and specialized task domains?

**RQ4:** What practical software-development risks are associated with confirmed package-related hallucinations observed in dependency-intensive AI-generated Node.js solutions?

### Updated Objectives

1. Produce a reproducible 360-generation dataset from the four frozen model/API conditions and the reviewed dependency-intensive task set.
2. Extract direct external npm dependency recommendations and quantify confirmed package-name hallucinations using SHR and PHR.
3. Identify package-version, package-API, and package-capability hallucinations separately under the existing evidence rules.
4. Compare confirmed finding frequency, type, and deterministic risk across model conditions and specialized domains.
5. Assess concrete practical consequences with `risk-model-1.0.0` and report evidence-bounded software-development implications.

### Preserved Outcome and Risk Boundaries

The primary classifications remain `VALID`, `CONFIRMED_HALLUCINATION`, `LEGACY_OR_REMOVED`, `AMBIGUOUS`, and `BUILTIN_OR_LOCAL`. SHR and PHR continue to count confirmed package-name hallucinations only. `PACKAGE_VERSION_HALLUCINATION`, `PACKAGE_API_HALLUCINATION`, and `PACKAGE_CAPABILITY_HALLUCINATION` remain separate secondary findings. Ordinary API misuse, bugs, syntax errors, omissions, and general implementation errors remain outside these metrics.

The deterministic `risk-model-1.0.0` remains unchanged: eligible confirmed findings are scored as Impact × Detectability. It is not replaced with an ML model. The v1 persistence experiment and cross-workflow recurrence design are not part of the new official 360-generation API protocol; adding another generation phase would require a prospective decision and is not implied by the retained risk model.

The detailed current generation protocol is [api_model_protocol.md](api_model_protocol.md), and task rationale is [task_set_v2_design.md](task_set_v2_design.md).

## Historical 2026-09-15 Record

## Purpose and Authority

This document records methodological decisions made before the main 360-generation analysis. It updates the research questions, adds a bounded secondary package-knowledge analysis, and replaces the earlier four-dimension risk rubric with `risk-model-1.0.0`.

Where this document conflicts with earlier research-question wording or the earlier namespace-claimability/persistence/functional-criticality/cross-tool risk rubric in [experiment_protocol.md](experiment_protocol.md), this dated update controls. The frozen collection design, primary package-name outcome, package-level classifications, and SHR/PHR definitions remain unchanged.

This update does not report or imply experimental findings.

## Current Working Research Questions

### RQ1

What is the prevalence of npm package-name hallucinations in Node.js code generated by the selected contemporary AI coding workflows?

### RQ2

When valid npm packages are recommended, to what extent do generated responses contain package-version, package-API, or package-capability hallucinations?

### RQ3

How do primary and secondary package-related hallucination patterns differ across the selected AI coding workflows and functional task categories?

### RQ4

What practical software-development risks are associated with confirmed package-related hallucinations, and how can those risks be assessed reproducibly?

## Current Research Objectives

1. Generate a reproducible dataset of Node.js/npm coding responses from the four selected workflows using the frozen task set.
2. Extract and validate npm dependency recommendations and quantify package-name hallucinations.
3. Identify and classify package-version, package-API, and package-capability hallucinations separately.
4. Compare hallucination patterns across workflows and task categories.
5. Assess the risk of confirmed package-related hallucinations using a transparent rule-based framework.
6. Produce practical recommendations based on the empirical findings.

## Primary Outcome and Metrics

The original primary outcome remains npm package-name hallucination. The authoritative package-level classifications remain:

- `VALID`
- `CONFIRMED_HALLUCINATION`
- `LEGACY_OR_REMOVED`
- `AMBIGUOUS`
- `BUILTIN_OR_LOCAL`

For primary analysis, `CONFIRMED_HALLUCINATION` means confirmed package-name hallucination.

The primary metrics remain:

$$
\mathrm{SHR} = \frac{\text{completed generations containing at least one CONFIRMED_HALLUCINATION}}{\text{completed generations analysed}}
$$

$$
\mathrm{PHR} = \frac{\text{confirmed hallucinated external npm package recommendation occurrences}}{\text{all eligible external npm package recommendation occurrences}}
$$

A generation with no external package references remains in the SHR denominator and contributes zero occurrences to the PHR denominator. Secondary hallucinations are never added to SHR or PHR.

## Secondary Package-Related Analysis

The study may separately identify confirmed:

- `PACKAGE_VERSION_HALLUCINATION`
- `PACKAGE_API_HALLUCINATION`
- `PACKAGE_CAPABILITY_HALLUCINATION`

These categories capture false package knowledge that the package-name outcome alone cannot represent. Their definitions and evidence requirements are specified in [package_hallucination_taxonomy.md](package_hallucination_taxonomy.md).

The addition is analytical, not an intervention in data generation. It does not change prompts, tasks, workflows, repetition counts, or primary denominators. General coding mistakes, wrong arguments to real APIs, syntax errors, security bugs, incomplete implementations, dependency omissions, and configuration errors remain outside hallucination metrics unless authoritative evidence establishes the required false package-specific claim.

No secondary rate is defined by this update. Any later rate requires a prospectively documented unit of analysis and denominator; confirmed secondary findings may otherwise be reported as counts and clearly labeled comparisons.

## Risk Assessment Update

The earlier additive rubric based on Namespace Claimability, Within-Tool Persistence, Functional Criticality, and Cross-Tool Consistency is superseded for official package-related hallucination risk scoring.

The authoritative model is now `risk-model-1.0.0`, defined in [risk_assessment_protocol.md](risk_assessment_protocol.md):

- Impact: 1–5
- Detectability: 1–4
- Risk score: Impact × Detectability
- `LOW`: 1–4
- `MODERATE`: 5–8
- `HIGH`: 9–14
- `CRITICAL`: 15–20
- non-scored `security_sensitive_context`: `true` or `false`

Only confirmed package-name, package-version, package-API, and package-capability hallucinations are eligible. Impact is assigned from the concrete consequence, never automatically from hallucination type or functional category. The model is deterministic and rule-based; it is not a machine-learning model.

For generation-level comparison, the maximum confirmed finding score in a generation may be used to avoid response-length inflation.

## Frozen Experimental Design

This update does not alter any collection condition:

- The main v1.0.0 30-task prompt set remains frozen.
- The four workflows remain ChatGPT Web, Gemini Web, Codex CLI, and Antigravity CLI.
- Three independent runs per task/workflow remain fixed.
- The main experiment remains 30 × 4 × 3 = 360 generations.
- Pilot generations remain separate and excluded from the 360.
- Task definitions and frozen workflow/model settings remain unchanged.
- Raw responses remain immutable and downstream annotations remain separate derivatives.
- No retry is allowed merely because a generation contains no hallucination.
- A zero or near-zero primary package-name hallucination rate is a valid result.
- Challenge or exploratory prompts remain separate from the primary experiment.

Changing prompts, tasks, retries, or selection rules after observing pilot outcomes would introduce outcome-driven bias. Secondary categories exist to represent false package knowledge accurately, not to increase hallucination counts.

## Methodological Integrity and Safety

- Detection, validation, classification, and risk assessment remain separate stages.
- Uncertain cases are not classified as confirmed hallucinations.
- General package existence does not prove package safety or legitimacy.
- Registry validation remains read-only.
- Generated code and recommended packages are never installed or executed.
- Package names are never published, registered, reserved, or claimed.
- Pilot, fixture, exploratory, persistence, and final baseline data remain distinguishable.
- Tool/model/version information is preserved exactly as observed; unexposed values remain `not_exposed`.

## Relationship to Existing Recommendations

This update retains the scope-control recommendations in [research_recommendations_usenix_2025.md](research_recommendations_usenix_2025.md): Node.js/npm only, 30 frozen tasks, four workflows, three repetitions, immutable raw outputs, automated extraction, conservative read-only validation, explicit ambiguity handling, simple statistics, and no unnecessary expansion into new ecosystems, tools, mitigation experiments, developer studies, or machine-learning classifiers.

The secondary analysis is intentionally narrow. It examines only version, API, and material capability claims directly connected to recommended npm packages. It does not create a general-purpose code-correctness benchmark.

## Reporting Implications

The final report should distinguish:

1. primary package-name results using SHR, PHR, occurrence counts, and unique normalized package names;
2. secondary confirmed version/API/capability findings reported separately;
3. non-hallucinatory implementation-quality observations, if reported;
4. workflow and functional-category comparisons without attributing causality to unobserved model internals; and
5. risk scores under `risk-model-1.0.0`, including component rationales and limitations.

No unobserved finding may be inserted into the report skeleton or methodology as if it were an experimental result.

## Change Control

Any later change to the taxonomy, primary metric definitions, secondary unit of analysis, scoring scales, risk thresholds, prompt set, task set, workflows, or generation count requires a dated methodology decision before it is applied to official analysis. Such changes must not be selected in response to desired or observed results.
