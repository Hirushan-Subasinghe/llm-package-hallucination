# Final Paper Notes

## How to use this file

Use these notes to draft the final dissertation from frozen artifacts and verified derived outputs. They are a writing aid, not a source of experimental evidence: manifests, immutable raw responses, collection metadata, versioned protocols, and regenerated analysis outputs control if any statement conflicts with this file. Do not present a planned analysis, a collection snapshot, pilot material, or a historical aborted version as a final result.

## Current methodology facts

### Experimental design

- v2.2 was prospectively stopped after 10 observations (6 completed, 4 truncated, 350 pending of 360 planned). Those observations are immutable methodological evidence and are excluded from v2.3 primary metrics.
- The active final experiment is v2.3, governed by `manifests/api_final_v2.3.0_manifest.csv`; it is a fresh 360-observation dataset with separate frozen configuration, state, raw observations, and derived analysis artifacts.
- Scope is direct Node.js/npm dependency recommendations only. Do not claim Spring Boot/Maven, other ecosystems, transitive-dependency analysis, generated-code execution, package installation, or package-name registration.
- The frozen matrix is 30 dependency-intensive tasks across six categories × four fixed model/API conditions × three independent repetitions = 360 planned runs (90 per condition, 60 per category, 120 per repetition). Collection order uses a balanced Latin-square rotation.
- The v2.3 generation interface is stateless and text-only: one user message, no prior context, tools, browsing, retrieval, code execution, or function calling. The frozen shared parameters are temperature 0.6, top-p 0.95, and a 12,000-token maximum; seed is not controlled. Exact model IDs, API providers, routing pins, and exposed metadata must be taken from the manifest/freeze record, never substituted from the old draft.
- Raw responses are immutable observations. Derived extraction, validation, classification, inventory, and risk records must remain separate and traceable. v2.3 uses sequential zero artificial pacing, while still respecting provider-enforced throttling and Retry-After.
- v2.0 and v2.1 observations, smoke/suitability material, and pilot data are preserved provenance but excluded from v2.2 research metrics.

### Analysis definitions

- A package reference is an explicit npm dependency or usable-package claim (for example, import/require, `npm install`/`npm i`, `package.json`, or equivalent explicit installation instruction). Vague prose alone is not automatically a package reference.
- Normalize before validation: remove import subpaths to identify the package root, distinguish scoped from unscoped names, retain the original string for audit, and exclude Node.js built-ins and local/relative references.
- The current primary package-level counting unit is a unique normalized npm package per response; repeated mentions of that normalized package in the same response count once for primary PHR. Retain occurrence-level source/provenance separately for audit and secondary analysis. The final extraction implementation and its version must document this deduplication reproducibly.
- **Open metric-wording check before final analysis:** `docs/current_research_status.md` specifies the unique-per-response primary unit, while older taxonomy/protocol wording describes PHR as occurrences. The current-status rule governs these notes, but PIPE-03 must document the implemented primary denominator and preserve occurrences separately so the final paper does not mix units.
- A primary package hallucination is a normalized package presented as an npm-installable/usable dependency that conservative validation confirms as nonexistent. Real-package identity, version, API, and capability errors are separate secondary categories and must not be added to primary PHR or SHR.
- Primary PHR is confirmed primary nonexistent-package references divided by evaluable npm package references; primary SHR is completed, non-truncated evaluable responses containing at least one primary package hallucination divided by completed, non-truncated evaluable responses. State the exact eligible denominator and treatment of unresolved records in the final analysis report.
- A completed non-truncated response with no external package reference remains eligible for SHR but contributes zero to PHR. `UNRESOLVED`/unverifiable records and not-applicable references must never be silently counted as valid or hallucinated.
- A provider-valid length-limited response is preserved as `TRUNCATED`, not labeled hallucinated or retried for truncation. The frozen v2.2 rule excludes truncated observations from the primary SHR and PHR estimates; report them and any separately labeled sensitivity/qualitative analysis apart from those estimates.
- Primary validation must distinguish `exists`, `not_found`, and `unresolved`; timeout, outage, rate limit, and other temporary retrieval failure are not absence evidence. Validation needs timestamped, versioned, read-only authoritative npm evidence and cache provenance. A clean 404 is a candidate absence, not by itself a final confirmed hallucination.
- The research-classification vocabulary requires conservative treatment: `VALID`, `CONFIRMED_HALLUCINATION`, `LEGACY_OR_REMOVED`, `AMBIGUOUS`, and `BUILTIN_OR_LOCAL`; `UNRESOLVED` is an operational validation state. Preserve manual-review decisions and evidence for audit.
- The verified risk protocol is the transparent, rule-based `risk-model-1.0.0` in `docs/risk_assessment_protocol.md`, identified in the v2.2 freeze record: eligible confirmed package-related findings may be scored as Impact (1–5) × Detectability (1–4), with a non-scored security-sensitive-context flag. It is an ordinal prioritization aid, not a predictive model or exploitation probability. Do not report score distributions until assessments have been performed and verified.

### Data-processing pipeline

- `scripts/build_response_inventory.py` is read-only: it combines manifest rows with preserved raw-run metadata and collector-designated failure evidence, without modifying the manifest, state, or raw responses.
- The derived inventory emits one row for every planned manifest run, sorted by manifest collection order. Pending/uncollected runs remain represented; unavailable fields are `null`, not inferred.
- A metadata-less run is not treated as failed merely because it has an ordinary attempt directory. Failed status requires explicit `failed_attempts/attempt-*` evidence or an explicit `temporarily_blocked_or_failed` state event; metadata remains authoritative when present.
- Inventory provenance includes run/order, provider/model/condition, task/category/repetition, prompt hash/path, raw response path, collection and completion status, truncation, token count, and interface-pass field. The schema and tests enforce the structural contract and live 360-row/order invariants.

### PIPE-03 dependency extraction and normalization (implemented)

**Affected final-paper sections:** Chapter 3 / Dependency Extraction and
Normalization; dataset construction and provenance.

- The implemented Node.js/npm extractor (`scripts/extract_package_references.py`)
  reads response-inventory records and immutable raw response text. It deterministically
  extracts explicit dependency syntax, retains occurrence-level provenance, normalizes
  package roots, and produces a separate unique normalized package-per-response view.
- Extractor v1.0.1 was manually audited against all 10 currently collected v2.2
  responses. The initial audit found 8 missed multiline literal imports; bounded
  multiline import scanning corrected them. The post-fix audit found 0 false
  positives and 0 false negatives under D029, with 3 documented contract-boundary
  cases. Describe this as validation on the audited observations, not as perfect
  extraction accuracy for future or unaudited responses.
- Extraction is separate from registry validation and hallucination classification.
  It excludes Node.js built-ins, `node:` references, local/relative/absolute paths,
  `file:` references, and HTTP(S) URLs; unsupported or ambiguous syntax is not guessed.
- Truncated observations can be extracted, but retain their truncation marker for later
  exclusion from primary PHR/SHR under the frozen v2.2 rule.
- The current 175 occurrence records and 97 unique `(run_id, normalized_package)`
  records are intermediate processing counts, not hallucination findings. Do not
  report them as hallucination prevalence.

**Draft reconciliation:** Old university-draft Section 3.5.1.2 describes Node.js
extraction using package.json parsing, AST parsing, and require/import scanning while
also including Spring Boot/Maven extraction elsewhere. The final dissertation must
remove Spring Boot/Maven extraction from performed methodology unless supported by
final experiment evidence; describe the implemented deterministic grammar and its
audit; not claim AST parsing; document occurrence provenance and deterministic
normalization; and describe the unique-package view separately from occurrence
extraction. Mention the multiline-import repair only if useful for reproducibility
or quality assurance, not as a headline research result.

### PIPE-04 registry validation (implemented; first v2.2 snapshot)

**Affected final-paper section:** Chapter 3 / Registry Validation.

- The implemented validator (`scripts/validate_npm_packages.py`) deduplicates
  normalized package names before read-only metadata GET requests to the official
  npm registry, then joins each package-level result back to response-package rows.
  A successful metadata response must match the exact normalized name to yield
  `exists`; a clean authoritative npm 404 yields `not_found`. Timeouts, network
  errors, HTTP 429/5xx, and malformed or unexpected responses remain `unresolved`.
- Operational failures receive bounded retries. Records retain UTC check times,
  validator version, request endpoint, status/evidence summary, and source-input
  hashes; the joined view preserves the response-package mapping. These are
  registry evidence states, separate from final research classifications.
- The first snapshot covers only the 10 collected v2.2 observations: 44 distinct
  names across 97 response-package rows yielded 43 `exists`, 1 `not_found`, and
  0 `unresolved`. These are interim validation counts, not final study results or
  hallucination prevalence. The `not_found` case requires later classification.

**Draft reconciliation:** Final Chapter 3 should describe this implemented npm
metadata lookup, bounded retry, provenance, and join mechanism rather than broader
planned validation mechanisms that were not performed.

## Draft reconciliation backlog

| Draft section/topic | Old draft assumption | Current evidence | Action |
|---|---|---|---|
| Title / empirical scope | “AI Hallucination Attack Surface: A Risk Assessment of Fake APIs and Libraries in AI-Generated Code” implies empirical coverage of both fake APIs and libraries | The v2.2 experiment is focused on Node.js/npm package-related claims. Whether fake APIs are empirically measured must be established from final analysis evidence. | PENDING FINAL SCOPE REVIEW |
| Abstract | SLR/literature-synthesis abstract | The study includes a frozen v2.2 empirical experiment. The final abstract must be rewritten after analysis to state the actual design, model/API conditions, sample size, package-validation method, verified results, limitations, and contribution. | REWRITE AFTER FINAL ANALYSIS |
| Research questions/objectives | Literature-review RQs on causes, slopsquatting distinction, and mitigation | `docs/methodology_update_2026-09-16.md` defines current working API-redesign RQs/objectives; `docs/experiment_protocol.md` explicitly says its earlier wording is superseded. Final RQs must remain answerable from implemented v2.2 evidence. | VERIFY AND RECONCILE BEFORE REPORT WRITING |
| Literature-review methodology / SLR claims | Database searches, Boolean strings, PRISMA selection, extraction matrix, quality assessment, and multi-reviewer arbitration were performed | Retain these only if search records, PRISMA counts, screening records, extraction sheets, quality-assessment data, and reviewer evidence exist. Otherwise describe only the review process actually performed. | VERIFY EVIDENCE |
| Conceptual framework, operationalization, and H1–H5 | Workflow/autonomy, developer expertise, ecosystem, mitigation variables, and fixed numerical thresholds | Retain only variables/hypotheses supported by the frozen v2.2 design and collected data. Do not retain numerical thresholds solely because they appeared in the old draft. | PENDING FINAL SCOPE REVIEW |
| Scope | Node.js/npm and Spring Boot/Maven experiments | Executed scope is Node.js/npm-only; Spring Boot/Maven is superseded planning. | REMOVE / MOVE TO FUTURE WORK |
| Comparison variables | Autocomplete/agentic workflow, programming environment, and developer expertise are experimental variables | v2.2 compares four fixed model/API conditions under one stateless text-only API protocol; no expertise variable or environment comparison. | UPDATE |
| Tools/models | GPT-3.5/GPT-4, Copilot, Gemini, Claude, or generic workflow claims | Use only the v2.2 manifest and freeze record's exact M1–M4 model/API conditions and pins. Do not map them to historical tools. | UPDATE |
| Sample size/power | Planned 200–300 prompts and projected dependency counts/power claims | Frozen design has 360 planned runs; collection is incomplete and no final outcome counts exist. | UPDATE; REMOVE unsupported power claims |
| Dependency extraction | Maven/Spring parsing and finalized AST/extraction mechanisms | Node.js/npm direct-dependency extraction is the only scope. PIPE-03 v1.0.1 implements deterministic explicit-syntax extraction, occurrence provenance, normalization, and a separate unique-per-response view; all 10 collected v2.2 responses were audited. It does not perform AST parsing. | UPDATE / IMPLEMENTED AND AUDITED |
| Registry validation | Absence inferred broadly from registry lookup | PIPE-04 uses read-only official npm metadata GET requests with exact-name checks, timestamped evidence, bounded retries, and a deterministic response-package join. Its 404 `not_found` state is not a final hallucination classification. | UPDATE / IMPLEMENTED; CLASSIFICATION PENDING |
| Hallucination measure | Absolute count of nonexistent dependencies | Primary PHR/SHR, normalized-package handling, occurrence provenance, unresolved handling, and separate truncation are required. | UPDATE |
| Risk assessment | Large composite model, naming distance, installation probability, workflow privilege, or predictive scoring | Only the specified rule-based Impact × Detectability protocol is in scope; no fitted/predictive model or risk result exists yet. | UPDATE; do not claim evaluation completed |
| Model validation | 70/30 split, predictive accuracy, Cohen's kappa, experts, temporal holdout, cross-tool validation, sensitivity-weight fitting | No evidence these validation studies were performed. The protocol calls only for documented subset double-checks if risk scoring occurs. | REMOVE / MOVE TO FUTURE WORK |
| Survey and mitigation | Developer survey, participant privacy procedure, or static/dynamic mitigation experiments | No human-participant study, installation-probability data, or mitigation experiment is in the executed design. | REMOVE / MOVE TO FUTURE WORK |
| Truncation rule | Earlier pre-analysis text allowed inclusion with a sensitivity exclusion | The frozen v2.2 protocol excludes truncated observations from primary PHR/SHR and permits only separately labeled secondary treatment. | UPDATE; frozen v2.2 protocol controls |

### Truncation precedence

`docs/analysis_specification_v1.0.md` §10/§17 contains earlier pre-analysis wording that primary analysis *may* include truncated responses and then recompute after exclusion. That wording is superseded for v2.2 by the prospective freeze rule in `docs/experiment_freeze_v2.2.0.md` (Truncation Policy) and `config/experiment_freeze_v2.2.0.json` (`truncation_rule`), as confirmed by `docs/methodology_update_2026-09-16.md` and decision D021 in `docs/decision_log.md`: `TRUNCATED` observations are preserved but excluded from primary SHR and PHR; only separately labelled qualitative or sensitivity treatment is permitted.

## Verified milestones relevant to paper

### 2026-09-16 — v2.2 experiment freeze

The v2.2 manifest and generation protocol were frozen before official v2.2 requests. The freeze record identifies 360 pending rows and records the manifest SHA-256 `0cec7f82a0b7d1c035b43410472bdb1565cf981a365595e9f2035d28cacd7ac6`. This supports a reproducibility/methodology statement, not a result claim.

### 2026-09-17 — first derived v2.2 response-inventory snapshot

The terminal-recorded first snapshot summary was 360 planned rows and 361 CSV lines including the header: 1 completed, 1 truncated, and 358 pending. It is collection-completeness metadata at that point in time, not an experimental finding. Its historical JSON and CSV SHA-256 values were `b6f44b72c2d7bfc66ec264ae67f368e0b589a33ad5bcf7ac2caa30cc8f34b697` and `34bad9dc91a9126d9fb5830ed03f8017d673022c8491a13a2ca9044747081311`, respectively. The original byte-for-byte rolling files were not preserved before regeneration, so these values must be treated as historical provenance evidence rather than hashes of the current rolling paths.

The later rolling inventory was preserved at `results/snapshots/response_inventory_v2.2.0_preserved_at_20260917T082919Z.json` and `.csv` without assigning it the first snapshot's timestamp. It records 360 planned runs: 2 completed, 2 truncated, and 356 pending; its JSON and CSV SHA-256 values are `ec4f95f3fc96c3ef305ca59801341b37ef9b1967a02ef79ec7695a77c89722fe` and `a0e05acce5a677b8d50469f6bdb0dacb8e9405482b79ce8b1f13fe8cc22bec04`. This preserved later inventory is also historical derived metadata and may be stale relative to active collection.

## Results notes

No final experimental results belong here yet. Add results only from verified, versioned extraction, validation, classification, and analysis outputs after v2.2 collection and the corresponding audit steps are complete. Never convert the inventory snapshot into a hallucination-rate finding.

## Tables/Figures to prepare

- Experimental-design table: task categories/counts, repetitions, fixed model/API conditions, provider routing, and frozen parameters.
- Collection-completeness table: scheduled, completed, truncated, failed/incomplete, and pending counts, dated and clearly separated from outcome results.
- Primary-results table (later): eligible responses, unique normalized evaluable packages, confirmed primary hallucinations, PHR, SHR, confidence intervals if calculated, by condition and category.
- Truncation/quality-control table (later): overall and condition/category truncation rates, separately from primary PHR/SHR.
- Secondary-findings and risk table (later): separately labeled version/API/capability findings and verified risk scores, with no merger into primary metrics.
- Analysis pipeline figure: frozen manifest and immutable raw responses → derived response inventory → extraction/normalization with occurrence provenance → read-only validation/classification → primary metrics and separately labeled risk assessment.

## Threats / limitations backlog

- Results are bounded by the frozen v2.2 task set, four fixed model/API conditions, direct Node.js/npm dependencies, three repetitions, and a stateless text-only interface; they do not generalize automatically to other ecosystems, tools, interfaces, or model versions.
- Model availability, provider routing, provider behavior, and npm registry state are temporal snapshots. Preserve exact observed metadata and validation timestamps; do not infer unexposed settings.
- Provider pacing/availability and incomplete collection can affect final completeness; disclose actual completed, truncated, failed, and pending counts at the analysis cutoff.
- Output truncation can affect observable dependency recommendations. It is preserved and reported separately, while exclusion from primary metrics limits the primary estimand to completed non-truncated responses.
- Extraction/normalization, registry validation, and manual adjudication can introduce error; report the extractor/validator versions, audit protocol, unresolved/ambiguous counts, and any documented reviewer agreement rather than assuming perfect classification.
- Registry existence does not establish package safety, legitimacy, maliciousness, exploitability, or user installation behavior. The risk rubric is evidence-bounded and ordinal, not a calibrated attack or loss forecast.

## Core evidence files for paper claims

- `manifests/api_final_v2.2.0_manifest.csv`; `config/experiment_freeze_v2.2.0.json`; `docs/experiment_freeze_v2.2.0.md`
- `docs/current_research_status.md`; `docs/research_progress_log.md`; `docs/decision_log.md`; `docs/methodology_update_2026-09-16.md`
- `docs/analysis_specification_v1.0.md`; `docs/package_hallucination_taxonomy.md`; `docs/risk_assessment_protocol.md`
- `scripts/build_response_inventory.py`; `schemas/response_inventory_item.schema.json`; `tests/test_response_inventory.py`


## 2026-09-17 — Initial v2.2 collection behavior

**Affected sections:** Methodology — AI Models, Code Generation Protocol, Response Handling, Sample Inclusion/Exclusion, Limitations.

- The implemented v2.2 study uses a common maximum output ceiling of 12,000 tokens.
- Initial official observations show that output truncation remains model-dependent even under the increased ceiling:
  - M1 completed at 11,347 tokens.
  - M2 reached 12,000 tokens and was truncated.
  - M3 completed at 8,893 tokens.
  - M4 reached 12,000 tokens and was truncated.
- Truncation is determined from provider `finish_reason=length` and is preserved as an observed generation outcome rather than retried.
- The first four official responses showed no tool exposure, protocol deviations, or simulated tool-call markup, supporting the validity of the stateless text-only generation interface.
- Final results must report truncation counts/rates separately from primary package-hallucination metrics.
- Evidence files: `data/final/raw/API-v2.2-AUTH-FED-01-M{1,2,3,4}-R01/metadata.json` and corresponding `response.md` files.

### 2026-09-18 — v2.3 initial collection gate

- **Affected sections:** Methodology / Data Collection, Results / Dataset Completion, Limitations.
- The final study uses the frozen v2.3 API protocol with zero researcher-imposed post-success delay; provider rate limits and retry behavior remain governed by the frozen collection rules.
- The first four official v2.3 observations, covering M1–M4 on `AUTH-FED-01`, were protocol-clean but all four reached the 12,000-token output ceiling and were recorded as truncated.
- Truncated observations are preserved exactly once and excluded from primary SHR/PHR denominators according to the frozen analysis protocol; truncation counts and rates must be reported separately.
- OpenRouter M1 returned internally inconsistent token-detail metadata (`completion_tokens=11998`, `reasoning_tokens=12087`). The raw provider response contains the same values, so provider token-detail subfields should not be treated as independently validated measurements.
- **Potential table/figure:** final completion-status/truncation counts by model condition.
- **Limitation to mention:** substantial truncation, if it persists across the completed dataset, reduces the number of analyzable non-truncated observations and may affect precision/comparability of model-level estimates.
- Evidence: `data/final/raw/API-v2.3-AUTH-FED-01-M1-R01/` through `API-v2.3-AUTH-FED-01-M4-R01/`.

### 2026-09-18 — non-retryable provider failure during v2.3 collection

- **Affected sections:** Methodology / Data Collection, Dataset Completion, Limitations / Threats to Validity.
- `API-v2.3-AUTH-FED-02-M1-R01` received HTTP 200 from OpenRouter but no non-empty assistant content and was recorded as a failed infrastructure observation.
- The frozen v2.3 retry policy permits retries for HTTP 429 and configured HTTP 5xx infrastructure failures only; this HTTP 200 empty-content case was therefore not retried.
- The frozen v2.3 batch rule stops on non-retryable provider failure without skipping or provider/model substitution, so collection stopped at this observation.
- The failed observation must not be interpreted as a package-hallucination result and must not enter SHR/PHR denominators.
- Any later continuation rule must be documented prospectively as a versioned operational amendment rather than silently modifying the frozen v2.3 protocol.
- Evidence: `data/final/raw/API-v2.3-AUTH-FED-02-M1-R01/`, `scripts/collect_api_run.py`, `scripts/collect_api_batch.py`, `docs/experiment_freeze_v2.3.0.md`, and `config/experiment_freeze_v2.3.0.json`.

### 2026-09-18 — v2.4 fresh prospective continuation version

- v2.4.0 is a fresh, separate 360-observation experiment, not a silent continuation or reuse of v2.3 observations.
- It was created prospectively before further collection. The only methodological change from v2.3 is that preserved non-retryable failed observations no longer block later manifest rows.
- Failed observations remain explicit infrastructure evidence, are never retried or regenerated for a successful answer, permit no model/provider substitution, and are excluded from primary SHR/PHR denominators.
- All v2.3 observations and artifacts remain immutable and are excluded from v2.4 metrics. v2.4 uses byte-identical copied task/prompt content and the same four model/provider conditions and generation protocol.

### 2026-09-21 — v2.4 initial collection gate

- **Affected sections:** Methodology / Data Collection, Dataset Completion, Limitations.
- Official v2.4 collection began only after the prospective freeze.
- The first four model-condition observations for `AUTH-FED-01` produced one completed response, two truncated responses, and one transport-failure observation.
- The M3 transport failure exhausted the frozen retry policy and was preserved as failed infrastructure evidence without manual regeneration or model/provider substitution.
- The v2.4 continuation rule then allowed later manifest rows to proceed, demonstrating the intended distinction from v2.3.
- Failed and truncated observations must be excluded from primary SHR/PHR denominators and reported separately in dataset-completion/data-quality tables.
- Evidence: `data/final/raw/API-v2.4-AUTH-FED-01-M1-R01/` through `API-v2.4-AUTH-FED-01-M4-R01/`.


### 2026-09-21 — output-token ceiling revision after v2.4

- **Affected sections:** Methodology / Experimental Protocol, Data Collection, Limitations.
- Frozen v2.4 used a 12,000-token maximum output ceiling.
- At the prospective decision checkpoint after 30 finalized v2.4 observations, 14 were completed, 12 were truncated, and 4 failed; the preliminary truncation rate was 40.0%.
- Truncated generations are right-censored at the configured ceiling, so their natural completion lengths cannot be inferred from completed-response token distributions.
- Because truncated observations are excluded from primary SHR/PHR denominators, the observed truncation burden motivated a prospective new experiment version rather than an in-place protocol change.
- v2.4 was therefore stopped without regenerating existing observations.
- The planned v2.5 experiment increases the maximum output ceiling from 12,000 to 16,000 tokens while retaining all other experimental conditions.
- v2.4 observations must remain separate methodological evidence and must not be pooled into v2.5 primary results.
- Avoid wording implying that 16,000 tokens is proven to eliminate truncation; it is a prospective protocol adjustment intended to provide additional response headroom.

### 2026-09-21 — v2.5 methodology implemented and prospectively frozen for review

- The previously documented v2.4 truncation checkpoint remains the reason for the prospective version change. The v2.5 implementation now exists as an independent 360-observation all-pending dataset with zero collected observations.
- Its sole experimental difference from v2.4 is a 16,000-token maximum output ceiling instead of 12,000. Task and prompt bytes, four model/provider conditions, other generation settings, retry/backoff, failure continuation, truncation semantics, and pacing are unchanged.
- The 30 rendered prompts and prompt template match v2.4 byte-for-byte. Freeze checks and tests passed, and the first-row dry run returned `API-v2.5-AUTH-FED-01-M1-R01`, OpenRouter, order 1, zero wait.
- No v2.5 API request was sent; there are no v2.5 outcomes, SHR/PHR estimates, or claims that the higher ceiling resolves truncation. The freeze has been prepared for researcher review, with commit and tag still pending.

### 2026-09-21 — v2.5 initial four-model live collection gate

- **Affected sections:** Methodology / Data Collection, Dataset Completion, Limitations.
- Official v2.5 collection began under the frozen 16,000-token output ceiling with one `AUTH-FED-01`, `R01` observation from each of the four frozen model conditions.
- All four model/provider conditions accepted the configured `max_output_tokens: 16000` request and returned HTTP 200 on the first attempt without retry.
- Verified response outcomes were:
  - M1: `COMPLETED`, finish reason `stop`, 7,058 completion tokens.
  - M2: `COMPLETED`, finish reason `stop`, 13,998 completion tokens.
  - M3: `COMPLETED`, finish reason `stop`, 8,210 completion tokens.
  - M4: `TRUNCATED`, finish reason `length`, exactly 16,000 completion tokens.
- The M2 observation provides direct evidence that the revised ceiling allowed at least one response to complete above the prior 12,000-token ceiling. This should be described as an observed case, not generalized to all generations.
- The M4 observation demonstrates that the 16,000-token ceiling did not eliminate truncation. Do not state or imply that v2.5 solved truncation completely.
- The batch-state event label `completed` denotes successful row processing and is not the authoritative response-completion classification. The authoritative status for analysis is the per-run `metadata.json` `collection_status` / `response_completion_status`.
- The initial gate outcome was therefore 3 completed and 1 truncated observation. These observations are collection-quality evidence only; no SHR, PHR, hallucination prevalence, or risk conclusion should be derived from this gate alone.
- Evidence: `data/final/raw/API-v2.5-AUTH-FED-01-M1-R01/` through `API-v2.5-AUTH-FED-01-M4-R01/`, plus the frozen v2.5 configuration and batch state.

### 2026-09-21 — v2.5 preserved provider-format failure

- **Affected sections:** Data Collection, Dataset Completion, Limitations.
- During official v2.5 collection, `API-v2.5-AUTH-FED-02-M4-R01` returned HTTP 200 on its first attempt, but the response body did not satisfy the collector's expected chat-completion structure.
- The observation was preserved with `collection_status: failed` and failure reason `HTTP 200 response is not a valid chat completion`.
- No valid assistant completion was parsed, so no `response_completion_status` or `finish_reason` exists for this run.
- The observation was not retried, regenerated, or replaced with another model/provider response.
- Under the frozen v2.5 continuation rule, preserved failed observations remain explicit infrastructure evidence and are excluded from primary SHR/PHR denominators while later manifest rows may continue.
- Do not describe this case as a package hallucination, truncation, or model-content failure; it is a provider/response-format collection failure.
- Evidence: `data/final/raw/API-v2.5-AUTH-FED-02-M4-R01/metadata.json` and `data/final/api_batch_state_v2.5.0.json`.

### 2026-09-21 — repeated v2.5 provider-response failures

- **Affected sections:** Data Collection, Dataset Completion, Limitations.
- Continued official v2.5 collection produced additional preserved provider-response failures.
- Two M4/OpenRouter observations, `API-v2.5-AUTH-FED-02-M4-R01` and `API-v2.5-AUTH-FED-03-M4-R01`, returned HTTP 200 but did not satisfy the collector's expected chat-completion structure.
- A separate M1/OpenRouter observation, `API-v2.5-AUTH-FED-03-M1-R01`, returned HTTP 200 but contained no non-empty assistant content.
- These observations were preserved as `failed`, were not retried, regenerated, or substituted, and have no valid response-completion classification.
- They must be reported as infrastructure/provider-response failures and excluded from primary SHR/PHR denominators.
- Do not describe these cases as package hallucinations, truncations, or model-content failures.
- Evidence: the corresponding per-run `metadata.json` files and `data/final/api_batch_state_v2.5.0.json`.

### 2026-09-21 — repeated M4 truncation under the v2.5 ceiling

- **Affected sections:** Data Collection, Dataset Completion, Limitations.
- Continued official v2.5 collection produced another M4 observation, `API-v2.5-AUTH-FED-04-M4-R01`, that reached exactly 16,000 completion tokens and ended with finish reason `length`.
- This is a second verified M4 v2.5 truncation at the 16,000-token ceiling, following `API-v2.5-AUTH-FED-01-M4-R01`.
- The repeated ceiling hits confirm that the v2.5 increase from 12,000 to 16,000 tokens provided additional output headroom but did not eliminate truncation for all responses.
- Truncated observations remain preserved once, are not regenerated, and are excluded from primary SHR/PHR denominators.
- Do not state or imply in the dissertation that the 16,000-token amendment solved the truncation problem.
- Evidence: `data/final/raw/API-v2.5-AUTH-FED-01-M4-R01/metadata.json`, `data/final/raw/API-v2.5-AUTH-FED-04-M4-R01/metadata.json`, and `data/final/api_batch_state_v2.5.0.json`.

### 2026-09-21 — verified AUTH-FED-04/05 collection outcomes

- **Affected sections:** Data Collection, Dataset Completion, Limitations.
- Verified per-run metadata for `AUTH-FED-04` and the first two `AUTH-FED-05` observations confirms a mixture of completed, truncated, and failed collection outcomes under the frozen v2.5 protocol.
- `API-v2.5-AUTH-FED-04-M1-R01` was preserved as a provider-response failure after an HTTP 200 response contained no non-empty assistant content.
- `API-v2.5-AUTH-FED-04-M2-R01` and `API-v2.5-AUTH-FED-04-M4-R01` were both truncated at exactly 16,000 completion tokens with finish reason `length`.
- `API-v2.5-AUTH-FED-04-M3-R01` completed normally at 10,387 completion tokens.
- `API-v2.5-AUTH-FED-05-M1-R01` and `API-v2.5-AUTH-FED-05-M2-R01` completed normally at 6,219 and 13,024 completion tokens respectively.
- These observations reinforce that the 16,000-token ceiling provides additional response headroom but does not remove right-censoring, and that preserved provider-response failures remain a separate dataset-completion category.
- Primary SHR/PHR analysis must exclude both truncated and failed observations according to the frozen protocol.
- Evidence: the corresponding per-run `metadata.json` files and `data/final/api_batch_state_v2.5.0.json`.

### 2026-09-22 — AUTH-FED-05 completed across all four v2.5 model conditions

- **Affected sections:** Data Collection, Dataset Completion, Limitations.
- All four `AUTH-FED-05` model-condition observations completed normally under the frozen 16,000-token ceiling.
- The verified completion-token counts were 6,219 for M1, 13,024 for M2, 9,215 for M3, and 13,154 for M4.
- This provides direct evidence that the previously observed M4 truncations are not universal across that model condition.
- The dissertation should therefore report M4 truncation as an observed recurring collection outcome, not as an inevitable property of every M4 response.
- No hallucination-rate or risk conclusion should be inferred from this task-level completion pattern.
- Evidence: `data/final/raw/API-v2.5-AUTH-FED-05-M1-R01/` through `API-v2.5-AUTH-FED-05-M4-R01/`.

### 2026-09-22 — PKI-CRYPTO begins with mixed v2.5 completion outcomes

- **Affected sections:** Data Collection, Dataset Completion, Limitations.
- The first two verified `PKI-CRYPTO-01` observations produced mixed completion outcomes under the frozen 16,000-token ceiling.
- `API-v2.5-PKI-CRYPTO-01-M2-R01` was truncated at exactly 16,000 completion tokens with finish reason `length`.
- `API-v2.5-PKI-CRYPTO-01-M3-R01` completed normally with finish reason `stop` and 6,429 completion tokens.
- This confirms that v2.5 truncation is not confined to the M4 condition; M2 can also reach the configured ceiling.
- Truncated observations remain preserved once and excluded from primary SHR/PHR denominators.
- Do not infer hallucination prevalence or model-quality differences from these collection-completion outcomes alone.
- Evidence: `data/final/raw/API-v2.5-PKI-CRYPTO-01-M2-R01/metadata.json`, `data/final/raw/API-v2.5-PKI-CRYPTO-01-M3-R01/metadata.json`, and `data/final/api_batch_state_v2.5.0.json`.

### 2026-09-22 — final high-output v2.6 protocol selected after v2.5 truncation evidence

- **Affected sections:** Methodology / Experimental Protocol, Data Collection, Dataset Completion, Limitations.
- Verified v2.5 observations showed that increasing the output ceiling from 12,000 to 16,000 tokens reduced some censoring pressure but did not eliminate truncation. Multiple M2 and M4 observations reached exactly 16,000 completion tokens with finish reason `length`.
- v2.5 was therefore prospectively stopped without deleting, retrying, regenerating, or modifying any preserved v2.5 observation.
- A fresh v2.6 experiment will start from observation 1 and will use model-specific output ceilings intended to minimize avoidable right-censoring:
  - M1: 64,000 output tokens.
  - M2: 32,768 output tokens with the same `qwen/qwen3.8-27b` model moved from Groq to OpenRouter.
  - M3: 65,536 output tokens.
  - M4: 65,536 output tokens.
- Because M2 changes provider and the output ceilings change, v2.6 is a distinct experimental version. v2.5 observations must remain methodological evidence and must not be pooled into v2.6 primary SHR/PHR results.
- The task set, prompt content, repetitions, temperature, top-p, no-tools policy, retry semantics, failure preservation, truncation preservation, and zero researcher-imposed pacing are intended to remain unchanged unless a provider-specific request-format difference is technically required.
- v2.6 is intended to be the final collection protocol. Any response that still reaches its supported output ceiling will be preserved as a right-censored truncated observation rather than triggering another experiment restart.
- No v2.6 result, hallucination rate, SHR, PHR, or risk result exists yet.

### 2026-09-22 — prospective v2.6 implementation provenance

- **Affected sections:** Methodology / Experimental Protocol, Data Collection, Dataset Completion, Limitations.
- The v2.6 implementation uses a fresh 360-row all-pending manifest and empty collection state, with no v2.6 raw observations. It does not reuse any v2.5 observation. v2.5 remains prospectively stopped and excluded from v2.6 primary SHR/PHR.
- The v2.6 template and all 30 rendered prompts are byte-identical to v2.5. The same task set, four model identities, repetitions, sampling parameters other than output ceilings, and collection/failure/truncation rules are retained.
- The experimental amendments are per-model output ceilings (M1 64,000; M2 32,768; M3 and M4 65,536) and moving M2 `qwen/qwen3.8-27b` from Groq to Darkbloom-pinned OpenRouter. The request restricts both provider order and allowlist to `darkbloom`, disables provider fallback, and supplies no model fallback.
- v2.6 is intended as the final prospective protocol. Remaining ceiling hits will be reported as preserved right-censored truncations and excluded from primary SHR/PHR, without restarting the experiment. No v2.6 hallucination, risk, SHR, or PHR result exists yet.
- The v2.6 freeze record contains the source URLs and hashes needed to audit these implementation facts. No live v2.6 API request was sent during implementation.

### 2026-09-22 — v2.6 final prospective protocol frozen

- **Affected sections:** Methodology / Experimental Setup, Data Collection, Model Configuration, Limitations, Reproducibility.
- The final prospective experiment version is v2.6.0, frozen at commit `5247c2bccb58ecd6c86b9b7e92d800ade0378282` and annotated tag `v2.6.0-freeze`.
- The primary v2.6 dataset contains 360 planned observations: 30 tasks × 4 model conditions × 3 repetitions.
- Frozen model conditions are:
  - M1: `cohere/north-mini-code:free` via OpenRouter, provider pin `cohere`, maximum output 64,000 tokens.
  - M2: `qwen/qwen3.8-27b` via OpenRouter, provider pin `darkbloom`, maximum output 32,768 tokens, provider fallback disabled.
  - M3: `openai/gpt-oss-120b` via Groq, maximum output 65,536 tokens.
  - M4: `nvidia/nemotron-3-ultra-550b-a55b:free` via OpenRouter, provider pin `nvidia`, maximum output 65,536 tokens.
- The v2.6 task set, prompt template, rendered prompt bytes, repetitions, temperature 0.6, top_p 0.95, uncontrolled seed, single-user-message interface, no-tools policy, retry semantics, failure preservation, truncation preservation, and zero researcher-imposed pacing are preserved from the prior protocol except for the explicitly documented provider/output-ceiling amendment.
- v2.5 is retained as methodological evidence and must not be pooled into v2.6 primary SHR or PHR estimates.
- Remaining v2.6 responses that hit their frozen output ceiling must be preserved as right-censored truncated observations and excluded from primary SHR/PHR under the predefined analysis policy; they must not trigger another experiment restart.
- Final pre-collection validation passed: v2.5 tests 4/4, v2.6 targeted tests 5/5, shared API/freeze tests 33/33, full repository suite 118/118, v2.5 freeze verification PASS, v2.6 freeze verification PASS, and `git diff --check` PASS.
- No live v2.6 API request had been sent when the freeze commit and tag were created.
- The final dissertation must describe v2.6 as the performed primary protocol if collection proceeds under this freeze. Earlier v2.0-v2.5 versions should be described only as protocol-development/methodological evidence where relevant.

### 2026-09-22 — official v2.6 collection began successfully

- **Affected sections:** Methodology / Data Collection, Results / Dataset Completion, Limitations.
- Official collection began under frozen v2.6 commit `5247c2bccb58ecd6c86b9b7e92d800ade0378282` and tag `v2.6.0-freeze`.
- The first official observation, `API-v2.6-AUTH-FED-01-M1-R01`, completed normally with finish reason `stop` under M1 (`cohere/north-mini-code:free` via OpenRouter/Cohere).
- The observation used 16,832 completion tokens under the frozen 64,000-token ceiling, with no protocol deviations.
- This single observation provides operational evidence that the higher v2.6 ceiling can avoid a 16,000-token ceiling hit for at least some responses; it must not be generalized into a truncation-rate result until sufficient v2.6 observations are collected.
- No v2.6 SHR, PHR, hallucination-rate, or comparative model result should be reported from this single observation.

### 2026-09-22 — temporary M2 collection deferral during frozen v2.6 execution

- **Affected sections:** Methodology / Data Collection Procedure, Dataset Completion, Limitations, Reproducibility.
- During official v2.6 collection, M2 generation was temporarily deferred after three preserved pre-generation HTTP 402 failures caused by unavailable OpenRouter paid-credit authorization.
- M1, M3, and M4 collection was allowed to continue while remaining M2 rows stayed pending.
- This changed only execution chronology; it did not change the frozen manifest, run IDs, original collection-order values, task prompts, model identities, provider pins, output ceilings, sampling parameters, retry/failure policy, truncation policy, or primary analysis definitions.
- The operational scheduling support was committed separately as `4bf0240` after the prospective experiment freeze. The experimental freeze remains `5247c2bccb58ecd6c86b9b7e92d800ade0378282` / `v2.6.0-freeze`.
- Actual execution timestamps should be used to describe collection chronology, while manifest `collection_order` remains the predefined planned ordering.
- The three already-failed M2 observations remain preserved failures and must not be regenerated. Remaining pending M2 observations will be collected later under the same frozen M2 configuration once paid access is available.

### 2026-09-22 — temporary M2 collection deferral during frozen v2.6 execution

- **Affected sections:** Methodology / Data Collection Procedure, Dataset Completion, Limitations, Reproducibility.
- During official v2.6 collection, M2 generation was temporarily deferred after three preserved pre-generation HTTP 402 failures caused by unavailable OpenRouter paid-credit authorization.
- M1, M3, and M4 collection was allowed to continue while remaining M2 rows stayed pending.
- This changed only execution chronology; it did not change the frozen manifest, run IDs, original collection-order values, task prompts, model identities, provider pins, output ceilings, sampling parameters, retry/failure policy, truncation policy, or primary analysis definitions.
- The operational scheduling support was committed separately as `4bf0240` after the prospective experiment freeze. The experimental freeze remains `5247c2bccb58ecd6c86b9b7e92d800ade0378282` / `v2.6.0-freeze`.
- Actual execution timestamps should be used to describe collection chronology, while manifest `collection_order` remains the predefined planned ordering.
- The three already-failed M2 observations remain preserved failures and must not be regenerated. Remaining pending M2 observations will be collected later under the same frozen M2 configuration once paid access is available.

### 2026-09-22 — residual truncation and provider-overload evidence in v2.6

- **Affected sections:** Data Collection, Results / Dataset Completion, Limitations.
- During official v2.6 collection, an M1 observation reached the frozen 64,000-token output ceiling with finish reason `length` and was preserved as truncated.
- Therefore, the larger model-specific v2.6 ceilings reduced ceiling-induced truncation but did not guarantee complete elimination of right-censoring.
- A separate M4 observation failed before a valid chat completion was produced because the upstream Nvidia provider reported temporary overload (`503 provider_overloaded`) inside the OpenRouter response.
- The M4 overload event should be reported as a provider/infrastructure failure, not as a hallucination, truncation, or malformed generated-code result.
- Both observations remain preserved once under the predefined collection policy and are excluded from primary SHR/PHR where required by that policy.

### 2026-09-22 — recurring M4 upstream availability failures

- **Affected sections:** Data Collection, Dataset Completion, Limitations.
- Multiple v2.6 M4 observations failed because the upstream Nvidia provider reported temporary overload (`503 provider_overloaded`) through OpenRouter.
- These events should be classified as provider/infrastructure failures and excluded from hallucination and truncation interpretations.
- The predefined preservation policy was maintained: each failed observation was retained once without regeneration or substitution.

### 2026-09-22 — Interim dependency-review screening produced a non-zero signal

**Affected sections:** Chapter 3 / Secondary Analysis Method; Results structure;
Discussion / Dependency Reliability.

- A current v2.6 checkpoint contained 350 metric-eligible package-response rows and 35 eligible completed responses.
- 5 eligible package recommendations required manual review (1.43%), occurring in 5 distinct eligible responses (14.29%).
- These are screening observations only and must not be presented as final research results.
- `REVIEW_REQUIRED` must remain distinct from confirmed hallucination and confirmed dependency failure.
- The next analysis stage is evidence-based PIPE-05B adjudication of the real review-required candidates.
- Two additional review-required cases occurred in truncated responses and are excluded from primary screening rates but may be retained for qualitative or sensitivity analysis.

### 2026-09-22 — PIPE-05B secondary dependency-reliability adjudication infrastructure implemented

**Affected sections:** Chapter 3 / Secondary Analysis Method; Results methodology; Discussion / Dependency Reliability.

- To characterize `AMBIGUOUS` / `REVIEW_REQUIRED` package references without weakening the primary conservative hallucination definition, a separate manual adjudication layer was implemented.
- PIPE-05B distinguishes confirmed package-name hallucination from other evidence-backed dependency-reliability outcomes: legacy/removed package, namespace confusion, package-name confusion, invalid/redundant types package, ecosystem confusion, other dependency error, and unresolved cases.
- `dependency_failure` is tracked independently from `confirmed_package_hallucination`.
- PIPE-05B is additive and does not feed back into the frozen primary PHR/SHR definitions.
- The implementation was validated with synthetic fixtures only; no real review-required package had been adjudicated at this milestone.

### 2026-09-22 — M3 provider TPM constraint

- **Affected sections:** Methodology / Provider Configuration, Data Collection Reliability, Limitations.
- A v2.6 M3 observation was rejected by Groq before generation because the current `on_demand` service tier exposed an 8,000 TPM limit while the frozen request reserved approximately 65.8k tokens.
- This event is a provider/account capacity constraint, not a hallucination, truncation, or generated model failure.
- The failed observation remains excluded from primary SHR/PHR.
- The frozen M3 generation ceiling was not reduced in response to this event.

### 2026-09-23 — M3 temporarily paused after recurrent Groq rate-limit failures

- Sections affected: Experimental Execution / Data Quality / Threats to Validity.
- The M3 condition continued to experience intermittent Groq HTTP 413 failures under the account's 8,000 TPM limit.
- A subsequent restart again produced a finalized HTTP 413 with no stranded request.
- Collection was temporarily paused to avoid repeatedly consuming pending observations during an unstable provider/account rate-limit period.
- Existing M3 completed and failed observations remain preserved, and finalized failures are not regenerated.
- The paper should distinguish these provider/account failures from model-output behavior.

### 2026-09-23 — M2 output budget consumed by reasoning without usable assistant content

- Sections affected: Experimental Execution / Data Quality / Threats to Validity.
- M2 order 15 reached the intended `qwen/qwen3.8-27b` Darkbloom condition after paid OpenRouter access was enabled, showing that the earlier HTTP 402 access problem was no longer the immediate blocker.
- Provider usage reported 32,768 completion tokens against the frozen 32,768-token output ceiling, of which 32,767 were reported as reasoning tokens.
- No non-empty assistant content was produced, so the observation was finalized as failed rather than treated as a usable generation.
- This observation provides evidence of output-budget exhaustion dominated by provider-reported reasoning tokens.
- The observation remains excluded from primary SHR/PHR eligibility under the frozen protocol.
- Avoid attributing this failure to billing or credit exhaustion.
- Evidence: preserved M2 order-15 response and metadata.

### 2026-09-23 — M1 exhibited both truncation and provider/model-error failure modes

- Sections affected: Experimental Execution / Data Quality / Threats to Validity.
- M1 order 62 returned HTTP 200 but no assistant content, with provider/model `finish_reason=error`.
- Provider usage reported only 3,603 completion/reasoning tokens, well below the frozen 64,000-token M1 ceiling.
- Therefore this observation should not be described as output-ceiling truncation.
- M1 missingness includes at least two distinct mechanisms:
  1. output-ceiling truncation;
  2. provider/model errors producing no usable assistant content.
- Failed rows remain excluded from primary SHR/PHR eligibility and are not regenerated.

### 2026-09-23 — HYBRID collection-interface allocation

- **Affected sections:** Methodology / Data Collection, Dataset Completion, Reproducibility, Limitations.
- A derived HYBRID allocation layer assigned the 360 frozen v2.6 manifest rows evenly by collection interface: 180 API and 180 manual. The frozen original manifest remains unchanged and is not replaced by the allocation artifact.
- The assignment preserves all 119 previously API-attempted observations (M1 16, M2 6, M3 38, M4 59), including completed, truncated, and failed observations. Interface allocation must not be interpreted as a successful-response count, and failed observations are not replaced to obtain successful outputs.
- Remaining API quotas were filled deterministically from never-attempted rows in each model condition's ascending frozen manifest order: 24 M1, 34 M2, 3 M3, and 0 M4 rows. Final model allocations are M1 40 API / 50 manual, M2 40 / 50, M3 41 / 49, and M4 59 / 31.
- The allocation is documented in `manifests/hybrid_assignment_v1.0.0.csv`; reproducibility checks and row lists are in `reports/hybrid_assignment_v1.0.0_report.md`. The verified original-manifest SHA-256 before and after is `b2b2750b3ae4ce96a867df14117b05c12f214760ef7036d6bbf2f78e44939b7f`.
- This formalization did not send API requests or start manual collection. M3 remains paused because of the documented Groq TPM/HTTP 413 incompatibility; no retry or frozen-configuration change is implied.

### 2026-09-25 — M1 manual data collection completed

- **Affected sections:** Methodology / Data Collection, Experimental Execution, Reproducibility.
- The implemented v2.6 HYBRID protocol assigned 50 M1 observations to manual collection, and all 50/50 have now been captured.
- The M1 condition used model `cohere/north-mini-code:free`; all 50 manual metadata files record the actual interface as `OpenRouter Chatroom web UI`.
- Manual M1 artifacts are stored under `data/final/manual_raw/v2.6.0/`; each observation preserves its exact rendered prompt, raw assistant response, and capture metadata.
- Verification confirmed all 50 M1 manual observation directories were present, all responses were non-empty, all metadata files were present, and the recorded model/interface values matched the intended M1 manual protocol.
- The manual collector reports no unobserved M1 manual-assigned rows remaining.
- Completion evidence is preserved on branch `collection/m1-manual-v2.6` at commit `d68460e6b1ea9c4737b5a519c11113990768446a`.
- No hallucination-rate, package-hallucination-rate, supply-chain-risk, or comparative model-result claim should be made from this collection milestone alone; those require downstream validated analysis.
- The final dissertation must describe the actual HYBRID API/manual collection procedure for M1 rather than any earlier assumption that all observations were collected through APIs.
