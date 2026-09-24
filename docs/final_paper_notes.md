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

### 2026-09-22 — accidental duplicate generation excluded from study data

- **Affected sections:** Methodology / Data Collection Integrity, Reproducibility, Limitations.
- One accidental duplicate live generation occurred outside the official collection workspace when the v2.6 collector was mistakenly run from the analysis repository.
- The accidental completed run used the same request bytes as the official observation but produced a different provider response ID and response content, confirming it was a second generation rather than a copy of the official observation.
- The accidental run and associated failed attempt were quarantined and excluded from all study datasets and downstream metrics.
- The official v2.6 dataset remains the copy collected under `~/Dev/ai-hallucination-study/data/final/raw/`.
- The analysis repository now contains a hard guard that blocks all collection CLI entry points before network access or data/state mutation.
- The guard is recorded in commit `fa01ad4`.
- This incident did not change the frozen v2.6 experimental inputs or the official observation set.
- Avoid wording that implies the accidental duplicate contributed to sample size, SHR, PHR, validation counts, or risk-model results.

### 2026-09-22 — PIPE-06 risk-scoring infrastructure implemented (no results yet)

**Affected sections:** Chapter 3 / Risk Assessment; Methodology / Reproducibility.

- The implemented risk model is `risk-model-1.0.0` from `docs/risk_assessment_protocol.md`: Impact (1-5) x Detectability (1-4), with bands LOW 1-4 / MODERATE 5-8 / HIGH 9-14 / CRITICAL 15-20.
- `security_sensitive_context` is recorded as a separate boolean flag with its own rationale and does not change the numeric score.
- The model is a deterministic, rule-based ordinal prioritization aid; it is not a probability or predictive model.
- Only a finding whose research classification is an eligible hallucination category and whose evidence is resolved can be scored. Every other finding remains unscored, encoded as `null` risk_score/risk_band, never zero.
- The implementation (`scripts/score_risk_findings.py`, `schemas/risk_finding_pipe06_v1.schema.json`) is currently validated only against synthetic fixtures (`tests/test_score_risk_findings.py`, 24/24 passing).
- No real finding has been scored and no real risk result exists yet. Do not report any risk score, band, or distribution until real eligible confirmed findings exist and are scored under this implementation.

### 2026-09-22 — PIPE-07 derived analysis-dataset infrastructure implemented; primary PHR/SHR unit formalized (no results yet)

**Affected sections:** Chapter 3 / Analysis Pipeline; Results-method definitions.

- A version-agnostic builder (`scripts/build_analysis_dataset.py`) now joins the response inventory with PIPE-03/04/05 derived evidence into two reusable datasets: package/response-level (one row per `(run_id, normalized_package)`) and response-level (one row per planned run, including pending/failed/truncated).
- **Primary package-level unit (decision D033):** one unique normalized package per response, `(run_id, normalized_package)`. A package mentioned, imported, or installed multiple times in one response counts once in the primary PHR numerator/denominator. This resolves the "Open metric-wording check" flagged above and corrects `docs/package_hallucination_taxonomy.md`'s earlier "occurrences" PHR wording; occurrence-level provenance remains fully preserved separately.
- **Primary response-level (SHR) unit (decision D033, confirming the existing taxonomy rule):** one completed, non-truncated evaluable response. Numerator: eligible responses with at least one confirmed package-name hallucination. Denominator: all eligible completed, non-truncated responses, including zero-package responses.
- **Truncation eligibility:** `TRUNCATED` observations are preserved in derived datasets but excluded from primary PHR/SHR, reaffirming that `docs/analysis_specification_v1.0.md` Sections 10 and 17's earlier "may include truncated responses" wording is superseded for primary metrics (both sections now carry an inline marker to this effect).
- The builder performs fail-safe cross-input validation (duplicate keys, metadata conflicts between the response inventory and PIPE-03/04/05 outputs, unsupported classification labels) and refuses to write output rather than silently produce an inconsistent dataset.
- This implementation is validated only against synthetic fixtures (21/21 tests passing; verified full-suite result after this change: 200 run, 198 passed, 2 failed — the same 2 pre-existing, unrelated `test_api_freeze.py` failures caused by historical raw artifacts absent from this worktree). No PHR, SHR, prevalence, or model comparison exists yet, and none was computed here.
- An attempted v2.2 dry-run failed cleanly and safely: this worktree no longer holds the physical v2.2 raw response files that the existing `results/*_v2.2.0.json` snapshots were built from, so a freshly built v2.2 response inventory (360/360 pending) disagreed with those snapshots. This is a worktree/provenance state issue, not a study finding, and no dataset was generated from it.
- Final reported analyses must use provenance-consistent v2.6-derived inputs — a response inventory and PIPE-03/04/05/07 outputs all built from the same v2.6 collection snapshot — not the historical, interim v2.2 snapshots.

### 2026-09-22 — DESIGN/SIGNAL-01: v2.6 prompt-to-analysis alignment audit (no final results yet)

**Affected sections:** Chapter 3 / Experimental Design; Chapter 3 / Measurement Validity; Chapter 5 / Threats to Validity / Interpretation.

- v2.6 prompts provide substantial external-package choice opportunity: all 30 tasks require a complete package.json with exact dependencies and documented API usage, across dependency-intensive specialized domains with no Node built-in equivalent.
- Package names are not pre-specified in any task; selection is left entirely to the model.
- Early v2.6 responses show dense actual package usage: all 28 completed/truncated responses audited so far contained at least one explicit external package reference (576 occurrences; 292 unique `(run_id, normalized_package)` rows; 87 distinct normalized package names).
- Therefore, a low or zero confirmed package-name hallucination result in the final v2.6 analysis should not automatically be interpreted as a failed measurement design; the opportunity and extraction-coverage evidence available at audit time supports treating such a result as potentially a legitimate null finding.
- Interpretation must still acknowledge documented limitations: narrative-only false package claims (never appearing in an actual import/require/install/package.json statement) are out of scope under the existing taxonomy; theoretical extractor gaps (`export ... from` re-exports, yarn/pnpm install syntax, `require.resolve`) exist but were not observed in the audited sample; and category/model coverage was incomplete at audit time (3 of 6 categories and 3 of 4 model conditions had zero eligible observations so far, reflecting collection progress rather than a design defect).
- Do not treat the audited 28-response snapshot as final results. This audit is a design/measurement-validity check, not a hallucination-prevalence finding.

### 2026-09-22 — PIPE-08 primary metric implementation completed (no results yet)

**Affected sections:** Chapter 3 / Analysis Pipeline; Chapter 3 / Metric Definitions; Results methodology.

- PHR unit is unique `(run_id, normalized_package)`.
- SHR unit is one completed, non-truncated response.
- Zero-package eligible responses remain in the SHR denominator.
- Occurrence repetition cannot inflate primary PHR.
- Zero denominator returns undefined/null rather than 0%.
- PIPE-08 performs cross-input consistency validation before calculation.
- Implementation was validated with synthetic fixtures only.
- No real PHR/SHR exists yet.
- Final execution must use a provenance-consistent v2.6 analysis snapshot.

### 2026-09-22 — Planned secondary dependency-reliability analysis

**Affected sections:** Research Questions/Objectives (pending evidence), Chapter 3 /
Analysis Methodology, Results structure, Discussion.

- The primary research outcome remains strict confirmed package-name hallucination
  measured through PHR/SHR.
- A secondary exploratory analysis is planned for package recommendations that require
  manual review after registry validation/classification.
- `REVIEW_REQUIRED` must not be treated as equivalent to hallucination or dependency
  failure.
- Real cases will first undergo evidence-based adjudication; only then may additional
  failure subtypes and secondary reliability metrics be frozen.
- Possible secondary outputs include package-level review/failure rates,
  response-level review/failure rates, error-type distributions, and qualitative case
  studies.
- No secondary reliability result should be written as a study finding until the
  adjudication taxonomy and metrics are formally defined and applied to real v2.6 data.

### 2026-09-22 — PIPE-05B secondary dependency-reliability adjudication infrastructure implemented

**Affected sections:** Chapter 3 / Secondary Analysis Method; Results methodology; Discussion / Dependency Reliability.

- To characterize `AMBIGUOUS` / `REVIEW_REQUIRED` package references without weakening the primary conservative hallucination definition, a separate manual adjudication layer was implemented.
- PIPE-05B distinguishes confirmed package-name hallucination from other evidence-backed dependency-reliability outcomes: legacy/removed package, namespace confusion, package-name confusion, invalid/redundant types package, ecosystem confusion, other dependency error, and unresolved cases.
- `dependency_failure` is tracked independently from `confirmed_package_hallucination`.
- PIPE-05B is additive and does not feed back into the frozen primary PHR/SHR definitions.
- The implementation was validated with synthetic fixtures only; no real review-required package had been adjudicated at this milestone.

### 2026-09-22 — Self-referential package names and external-dependency sensitivity eligibility (D034; no results yet)

**Affected sections:** Chapter 3 / Metric Definitions; Chapter 3 / Secondary Analysis Method; Results methodology; Threats to Validity.

- Self-referential generated-project names (the generated project's own package name, or a generated local/workspace package) are distinct from external npm dependencies. PIPE-05B.1 records them as `SELF_REFERENCE_OR_LOCAL_PACKAGE` only on response-internal evidence.
- A registry 404 for such a name is not evidence of dependency failure or package-name hallucination.
- Primary PHR remains frozen under D033 (unique `(run_id, normalized_package)` rows); it is not retroactively changed by adjudication, because doing so after self-reference cases were observed would risk outcome-dependent methodology. Primary SHR is also unchanged.
- Secondary external-dependency sensitivity metrics, labelled secondary/exploratory, exclude adjudicated local/self references (`external_dependency_eligible=false`) from both numerator and denominator.
- Unresolved external/local status (`external_dependency_eligible=null`) is reported separately and does not silently enter any denominator.
- No real result is claimed at this stage: no real package has been adjudicated and no primary or secondary rate has been calculated.

### 2026-09-22 — provider error finish reasons classified as failed (D035)

- **Affected sections:** Data Collection (outcome classification), Dataset Completion, Limitations.
- One v2.6 M4 observation received HTTP 200 with partial assistant content but a provider-declared `finish_reason: "error"`, far below its output ceiling. The collector originally recorded it as completed.
- Under D035, only `stop` is a completed generation and only `length` is a truncation. Any other provider finish reason, including `error`, is a failed observation even when partial text was returned.
- Report it as a provider/infrastructure failure, not as a truncation or a hallucination result. It is excluded from primary SHR/PHR, preserved once, and was not regenerated.
- Methods text should state that the correction was applied as a derived, documented status overlay without editing raw data, and that the rule depends only on the provider's termination status, not on response content.

### 2026-09-22 — PIPE-09 grouped comparison infrastructure implemented (no final inference yet)

**Affected sections:** Chapter 3 / Statistical Methods; Results methodology.

- Grouped descriptive analysis is implemented for model condition, task category, repetition, and model-condition × category views.
- Statistical infrastructure supports Fisher's exact testing for 2×2 comparisons, assumption-gated chi-square or deterministic Monte Carlo handling for sparse multi-group tables, Holm-Bonferroni correction for pairwise comparisons, and odds-ratio/risk-difference effect sizes with 95% confidence intervals.
- Sparse, zero-event, and insufficient-group situations are handled explicitly rather than forcing a significance result.
- No ranking or best/worst model label is produced.
- PIPE-09 has been validated with synthetic fixtures only; no final v2.6 inferential result exists yet.

### 2026-09-23 — First real PIPE-05B adjudication reproducibly archived

**Affected sections:** Chapter 3 / Dependency Adjudication; Results / Secondary Dependency Reliability; Threats to Validity.

- A real interim v2.6 `REVIEW_REQUIRED` case, `mtls-pfx-loader`, was adjudicated as `SELF_REFERENCE_OR_LOCAL_PACKAGE`.
- The generated response declared `mtls-pfx-loader` as its own project name and used that name in documentation examples referring to symbols implemented by the generated project itself.
- Therefore the npm registry 404 did not indicate an external dependency failure or confirmed package hallucination.
- The adjudication was reproduced from a permanent derived evidence snapshot with verified source and response hashes.
- This observation supports the methodological requirement that registry non-existence alone is insufficient to establish package hallucination.
- The row remains part of the frozen D033 primary metric definition but is excluded from the D034 secondary external-dependency sensitivity denominator.
- This is an interim adjudication and does not constitute a final research result or final PHR/SHR value.

### 2026-09-23 — Remaining interim PIPE-05B cases: confusion rather than confirmed package hallucination

**Affected sections:** Results / Secondary Dependency Reliability; Discussion; Threats to Validity.

- Three interim v2.6 package references returning npm 404 were traceable to legitimate package/module concepts:
  - `@xmldom/xpath` → namespace confusion involving the real `xpath` package and `@xmldom` scope.
  - `pkcs12` → package-name confusion; the generated implementation actually uses `node-forge` / `forge.pkcs12`.
  - `mime-node` → package-name confusion involving Nodemailer's `lib/mime-node` / `MimeNode` implementation.
- All three are adjudicated as dependency failures because the generated dependency declaration would fail installation, but none is classified as a confirmed package-name hallucination.
- No evidence of historical existence was found with the sources checked; the paper must not state that these packages definitively "never existed".
- Registry absence alone did not determine the classification. Positive evidence identifying the intended legitimate package/module was used.
- Together with the separately adjudicated `mtls-pfx-loader` self-reference, all four metric-eligible interim REVIEW_REQUIRED rows have now been resolved.
- These remain interim checkpoint observations and must not be reported as final rates or final v2.6 findings.
- An additional `node-forge` API-use anomaly (`forge.pkcs12.load`) was observed during review. It is outside the current dependency/package-reference adjudication scope and should not be promoted into a new measured category without a separately defined and validated method.

### 2026-09-23 — Confirmed hallucinations counted regardless of adjudication path (D037; no results yet)

**Affected sections:** Chapter 3 / Classification and Adjudication; Chapter 3 / Metric Definitions; Threats to Validity.

- Registry-404 package names can be confirmed as package-name hallucinations through either the original PIPE-05 review or the later, stricter PIPE-05B adjudication. Methods text should state that a confirmation from either path counts once in primary PHR and SHR, with the confirming path recorded for every counted row.
- PIPE-05B confirmation requires every PIPE-05 conservative check plus namespace, ecosystem, and types-package exclusion, so no weaker evidence enters the primary metrics.
- Confusion outcomes (namespace, package-name, ecosystem, types-package), legacy/removed, other dependency errors, self/local references, and unresolved cases never enter the primary numerators.
- Units, denominators, and eligibility are unchanged from D033. This is a routing correction adopted before any PIPE-05B confirmation existed, and it changed no interim figure.
- Report how many eligible review-required rows were left unadjudicated or unresolved, because they stay in the PHR denominator without being able to enter its numerator.
- No final PHR/SHR exists at this stage.

### 2026-09-23 — Secondary dependency-reliability metrics defined (D036; no results yet)

**Affected sections:** Chapter 3 / Secondary Analysis Method; Results / Secondary Dependency Reliability; Threats to Validity.

- DFR and RDFR are secondary/exploratory and must be labelled as such. They are not hallucination rates and never replace PHR/SHR.
- Methods text: "DFR measures exact-name npm dependency-resolution failures under the defined adjudication rules. It does not capture all forms of dependency unreliability, including wrong-but-existing packages, version-resolution errors, API errors, capability mismatches, or functional-unsuitability errors." Do not describe DFR as a lower bound on all dependency unreliability.
- VALID packages count as non-failures. Self/local references are excluded. Unresolved or unadjudicated rows are excluded from point estimates but reported with lower/upper bounds and counts by reason. Zero-package responses remain RDFR negatives.
- Report the DFR numerator by adjudication outcome, so that confusion cases (namespace, package-name) are never presented as confirmed hallucinations. Confirmed hallucinations inside the failure breakdown follow D037 routing.
- Threats to validity: semantic review is asymmetric (registry-404 names receive deeper adjudication than registry-valid names); wrong-but-existing packages, version failures, and API/capability errors are outside DFR; registry state is time-sensitive; adjudication relies on researcher review; grouped estimates may be sparse and clustered; the metrics were defined after four interim adjudications were seen, but before any rate was computed and before v2.6 collection completed.
- No DFR/RDFR result exists at this stage.

### 2026-09-23 — D037 routing and D036 secondary metric infrastructure implemented

**Affected sections:** Chapter 3 / Classification and Adjudication; Metric Definitions; Secondary Analysis Method; Threats to Validity.

- D037 is implemented at PIPE-07 as the single primary-confirmation resolution point. Guarded confirmations from either the PIPE-05 reviewed path or PIPE-05B can enter primary PHR/SHR exactly once, while D033 units and denominators remain unchanged.
- PIPE-08 and PIPE-09 consume the resolved confirmation fields produced by PIPE-07.
- D036 is implemented separately as PIPE-10 for secondary/exploratory DFR and RDFR. These metrics measure exact-name npm dependency-resolution failures under the defined adjudication rules and must not be described as hallucination rates.
- PIPE-10 explicitly represents external failures, external non-failures, self/local exclusions, and undetermined cases, and reports uncertainty bounds and completeness status.
- Synthetic validation passed for the new routing and secondary-metric infrastructure. No real v2.6 PHR, SHR, DFR, or RDFR result had been calculated at this milestone.

### 2026-09-23 — v2.6 hybrid interface-allocation clarification

- **Affected section:** Methodology / Experimental Design / Data Collection.
- The final v2.6 hybrid interface assignment is 180 API rows and 180 Manual rows across the 360-row manifest.
- Preserved failed API observations remain classified as API-assigned for interface-allocation accounting even though they are excluded from metric eligibility.
- `API-v2.6-ENT-INT-01-M1-R01` is one such preserved failed API observation and must not be reassigned or regenerated.
- Final reporting should distinguish interface assignment from analytical eligibility so failed API observations are not mistaken for completed metric-eligible runs.

### 2026-09-23 — Chapter 1 support-document synchronization

**Affected sections:** Chapter 1 Research Problem, Research Gap, Aim, Objectives, Research Questions, Scope/Delimitations, Contributions, and Dissertation Structure.

- The existing title remains unchanged.
- Chapter 1 must explicitly delimit the empirical study to direct Node.js/npm dependency references and replace SLR-as-final-study framing.
- Replace the old root-cause, slopsquatting, and mitigation research questions with the repository-grounded empirical RQ1–RQ4.
- PHR/SHR are primary; DFR/RDFR remain secondary/exploratory. Grouped comparisons are descriptive and, where estimable, compared.
- Risk statements apply only to eligible confirmed package-hallucination findings.
- Unsupported baseline percentages and literature-wide novelty claims must not appear.
- Slopsquatting, autonomy, and mitigation remain background/literature topics only unless discussing future work or implications.
- Final empirical contribution wording remains pending final v2.6 results.

### 2026-09-23 — Chapter 1 verified for dissertation use

- **Affected section:** Chapter 1 — Introduction.
- The complete Chapter 1 draft (Sections 1.1–1.11) has passed repository-grounded factual and citation verification, subject to one verified wording correction in Section 1.8.
- Final Chapter 1 preserves the existing dissertation title while explicitly delimiting the implemented empirical study to direct Node.js/npm dependency references.
- Primary outcomes are PHR and SHR; DFR and RDFR remain secondary/exploratory dependency-reliability measures.
- Group comparisons remain descriptive and where-estimable, and practical-risk assessment is limited to eligible confirmed package-hallucination findings.
- No final empirical findings are stated in Chapter 1; result-dependent contributions remain pending final v2.6 analysis.
- The verified Chapter 1 is suitable for transfer into the final Word dissertation after the Section 1.8 wording correction.

### 2026-09-23 — Chapter 2 literature review reconciliation

- **Affected section:** Chapter 2 — Literature Review.
- The final literature review should be organized around LLM-assisted software development, code hallucination, dependency/package ecosystems, software supply-chain threats, package hallucination, validation/classification approaches, reliability/risk, comparative dimensions, and a bounded synthesis/research gap.
- Cross-ecosystem literature on PyPI, Maven, Java, Python, autonomous systems, slopsquatting, mitigation, and other topics may remain as literature context where supported, but must not be described as part of the performed Node.js/npm experiment.
- Unsupported baseline prevalence/adoption/detection percentages must not be carried into the final dissertation until source-level verification supports them.
- Chapter 2 must not claim that no prior work exists or that this dissertation is the first study of package hallucination.
- Source-level verification of priority approved references is required before final Chapter 2 prose is written.
- Final literature claims must remain within the approved 34-reference citation set.

### 2026-09-23 — Chapter 2 reference policy frozen before drafting

- **Affected section:** Chapter 2 — Literature Review.
- All 34 approved references in `docs/references/approved_references.md` must appear at least once in final Chapter 2.
- Citation frequency and argumentative weight follow evidence strength, not equal distribution. Citation dumping to satisfy coverage is not permitted.
- The 11 full-text-verified sources should carry the central literature synthesis: Spracklen et al. (2025), Al-Zofi (2025), Gao et al. (2025), Ladisa et al. (2023), Duan et al. (2020), Williams et al. (2025), Zhao et al. (2025), Tian et al. (2025), Liu et al. (2026), Woesle et al. (2025), and Twist et al. (2026). Detailed claims must stay within the verified evidence summaries in `docs/final_report_support/chapter2_source_verification.md`.
- Metadata-only references should normally be used only once, for bounded contextual coverage, and must not be the sole support for a detailed finding, number, comparison, causal conclusion, or superiority claim.
- No unsupported numeric or prevalence claim from the baseline should be restored. The six `USE_ONLY_WITH_CONTEXT` numeric claims may be used only with their exact source-specific population, ecosystem, model, and task/prompt context, and only if analytically needed.
- Spracklen et al.'s 19.7% figure uses approximately 2.23 million recommended packages (440,445 hallucinated) as its denominator, not 576,000 code samples; 576,000 is that study's code-sample count.
- No broad "first study", "no prior work", "unexplored", or equivalent novelty claim may appear.
- Gandhi citation rule: cite as **Gandhi (2026)**, matching the baseline reference list and the approved entry. The baseline in-text `Gandhi, 2025` citations are a citation-year error and must not be reused. Gandhi (2026) remains metadata-only: one conservative contextual use in the autonomous-development security-risk context only, with no agentic finding and no implication that autonomy was a performed study variable.
- Chapter 2 prose may now be drafted with restricted claims (`READY_WITH_RESTRICTED_CLAIMS`).

### 2026-09-24 — Chapter 2 verified for dissertation use

- **Affected section:** Chapter 2 — Literature Review.
- The assembled Chapter 2 draft (`docs/report_drafts/chapter2_complete_draft.md`) has passed final structural, citation, factual, and consistency verification and is ready for transfer into the dissertation Word document.
- All 34 approved references are represented at least once; citation weight remains evidence-dependent, with full-text-verified sources carrying the substantive literature synthesis and metadata-only sources restricted to conservative contextual use.
- Table 2.1 may be retained as the conceptual distinction table for package-naming/dependency threats.
- Table 2.2 may be retained as a study-design synthesis table; evidence-limited cells must remain `—`.
- Unsupported baseline percentages and broad novelty claims must not be reintroduced during Word editing.
- The final literature synthesis distinguishes package hallucination from broader dependency failure and from downstream adversarial actions such as slopsquatting.
- Chapter 2 does not treat the study-defined PHR/SHR, DFR/RDFR, or Impact × Detectability framework as prior-literature standards.
- Detailed execution-safety and non-installation rationale removed from Chapter 2 should be documented in Chapter 3 Methodology.

### 2026-09-24 — Chapter 2 final figure plan

- **Affected section:** Chapter 2 — Literature Review / List of Figures.
- Do not retain the baseline PRISMA figure, autonomous-agent lifecycle/slopsquatting execution diagram, multi-stage defensive architecture, hybrid mitigation pipeline, or sandboxed-execution evaluation framework as figures representing the performed research.
- Final Figure 2-1 should depict the conceptual relationship between LLM package-name hallucination, dependency resolution, and possible downstream software supply-chain risk, while explicitly showing that package hallucination itself is not an attack.
- Final Figure 2-2 should summarize the literature progression from LLM-assisted software development and code hallucination through dependency reliability and supply-chain implications to the bounded Node.js/npm research rationale.
- Table 2.2 already covers comparative methodological dimensions, so no Figure 2-3 is currently required.
- Detailed experimental workflow, extraction/validation/adjudication pipeline, metric derivation, and practical-risk framework figures should be placed in Chapter 3 rather than Chapter 2.

### 2026-09-24 — Chapter 3 methodology reconciliation

**Affected section:** Chapter 3 — Methodology

The final dissertation methodology must describe the implemented frozen v2.6 Node.js/npm study rather than the methodology proposed in the original draft.

Verified methodology to report:
- Node.js/npm empirical scope only.
- 30 final coding tasks across six categories.
- Four frozen model conditions.
- Three planned repetitions.
- 360 planned observations.
- Frozen task/template/rendered-prompt and manifest provenance.
- Hybrid API/manual collection assignment where supported by authoritative records.
- Explicit response-status and analytical-eligibility rules.
- PIPE-03 package-reference extraction and normalisation.
- PIPE-04 read-only npm registry validation.
- PIPE-05/PIPE-05B classification and adjudication.
- D037 single hallucination-resolution path.
- PHR and SHR as primary hallucination measures.
- DFR and RDFR as secondary/exploratory dependency-resolution measures, not hallucination rates.
- PIPE-09 grouped/statistical analysis.
- `risk-model-1.0.0`: Impact 1–5 × Detectability 1–4, with LOW/MODERATE/HIGH/CRITICAL bands and separate `security_sensitive_context`.
- No generated dependency installation/execution or package claiming/registration.
- Validation evidence must be described as infrastructure/pipeline validation, not expert or inter-rater validation.

The final Chapter 3 must remove or avoid:
- Java/Maven or PyPI as performed experiments;
- multi-ecosystem empirical claims;
- surveys/human participants;
- autonomy/agentic comparison;
- mitigation experiments;
- predictive ML or 70/30 validation;
- Cohen’s Kappa or expert review;
- temporal holdout;
- static/dynamic execution comparison;
- package installation/execution;
- superseded 0–12 risk scoring;
- claims that npm 404/not_found automatically means hallucination;
- claims that DFR/RDFR are hallucination rates.

Methodological limitations to include:
- single ecosystem;
- bounded 30-task/four-condition/three-repetition design;
- medium difficulty is study metadata, not externally calibrated;
- direct explicit package references only;
- no transitive-dependency analysis;
- no functional execution/correctness testing;
- time-bounded registry/provider evidence;
- unresolved adjudications;
- rule-based study-specific risk model.

Evidence:
`docs/final_report_support/chapter3_methodology_reconciliation.md`

Drafting status:
READY WITH RESTRICTIONS — final collection/results remain pending, and manual-interface operational details must not exceed what is supported by authoritative collection records.

### 2026-09-24 — Chapter 3 final methodology and Word-transfer note

Chapter 3 is `READY_FOR_WORD`. The final dissertation methodology must describe the implemented study as Node.js/npm only: 30 frozen tasks across six categories, four frozen model conditions, three planned repeated generations per task/model condition, and 360 planned observations. It must describe the hybrid 180 API / 180 manual assignment, while keeping collection assignment distinct from analytical eligibility.

The methodology must state that deterministic package-reference extraction uses unique `(run_id, normalized_package)` package rows; official npm registry validation is read-only; and npm `404`/`not_found` alone does not establish a hallucination. It must preserve conservative classification and adjudication with one controlled confirmation path. PHR and SHR are the primary hallucination metrics. DFR and RDFR are secondary/exploratory exact-name dependency-reliability metrics and must not be described as hallucination rates. Grouped analysis must use the verified PIPE-09 statistical procedure.

Practical risk must use `risk-model-1.0.0`: Impact 1–5 × Detectability 1–4, with LOW 1–4, MODERATE 5–8, HIGH 9–14, and CRITICAL 15–20. `security_sensitive_context` remains a separate non-scored field. No generated package installation, execution, claiming, registration, reservation, or active exploitation occurred.

Validation status is `FINAL-ANALYSIS-VALIDATION-01 = PASS WITH DOCUMENTED LIMITATIONS`. The medium-difficulty designation came from pre-freeze qualitative task design; it was not externally calibrated and was not an analytical variable. Wording implying formal statistical independence of repetitions must be avoided.

Potential final-paper assets are:

- Figure 3-1: Frozen task-condition-repetition design.
- Figure 3-2: Experimental workflow and preservation boundary.
- Figure 3-3: Extraction, registry, and adjudication pipeline.
- Figure 3-4: Primary and secondary metric derivation.
- Figure 3-5: Impact × Detectability risk framework.

Final empirical results must be added only after verified final analysis. Do not add empirical values or findings to Chapter 3.
