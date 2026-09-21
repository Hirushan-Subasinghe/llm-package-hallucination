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
- Extraction is separate from registry validation and hallucination classification.
  It excludes Node.js built-ins, `node:` references, local/relative/absolute paths,
  `file:` references, and HTTP(S) URLs; unsupported or ambiguous syntax is not guessed.
- Truncated observations can be extracted, but retain their truncation marker for later
  exclusion from primary PHR/SHR under the frozen v2.2 rule.
- The current 167 occurrence records and 97 unique records are intermediate processing
  counts, not hallucination findings. Do not report them as hallucination prevalence.

**Draft reconciliation:** Old university-draft Section 3.5.1.2 describes Node.js
extraction using package.json parsing, AST parsing, and require/import scanning while
also including Spring Boot/Maven extraction elsewhere. The final dissertation must
remove Spring Boot/Maven extraction from performed methodology unless supported by
final experiment evidence; describe only the grammar actually implemented; not claim
AST parsing; document occurrence provenance and deterministic normalization; and
describe the unique-package view separately from occurrence extraction.

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
| Dependency extraction | Maven/Spring parsing and finalized AST/extraction mechanisms | Node.js/npm direct-dependency extraction is the only scope. PIPE-03 implements deterministic explicit-syntax extraction, occurrence provenance, normalization, and a separate unique-per-response view; it does not perform AST parsing. | UPDATE / IMPLEMENTED |
| Registry validation | Absence inferred broadly from registry lookup | Read-only, timestamped npm validation must separate `exists`, `not_found`, and `unresolved`; 404 requires conservative classification checks. | UPDATE |
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
