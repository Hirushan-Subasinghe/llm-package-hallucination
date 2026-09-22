# Methodology Decision Log

Track implementation and methodology decisions with rationale, preserving design evolution between the originally proposed research design and the final executed empirical methodology.

## Purpose and Scope

This log records formal architectural, methodological, and experimental design decisions made throughout the project lifecycle. In particular, it documents how and why the research methodology evolved from the earlier dissertation/proposal design into the final executed experiment.

This decision history supports:
- Chapter 3 (Methodology) dissertation revision and defense
- Final research report and academic publication preparation
- Reproducibility and research auditability
- Explicit justification of study limitations and scope boundaries
- Explanations for academic supervisors and examination panels

All decisions adhere strictly to empirical research integrity rules: design refinements are recorded objectively without claiming experimental findings prematurely, inventing results, or asserting undocumented supervisor approvals.

## Entry Schema

Each decision record contains the following standardized fields:

- **decision_id:** Unique identifier (e.g., D001).
- **date:** Date of formalization (YYYY-MM-DD).
- **status:** Decision lifecycle status (e.g., FINALIZED).
- **approved_by:** Recording authority (`researcher`; formal supervisor approval marked as `not_recorded` unless formally documented).
- **original_design:** The earlier proposed scope or initial methodology design.
- **final_design:** The refined and frozen methodology for the executed experiment.
- **rationale:** Practical or operational drivers necessitating the change.
- **methodological_justification:** Scientific and academic justification preserving validity and rigour.
- **impact_on_data_collection:** Concrete effects on data generation, capture, and storage.
- **impact_on_analysis:** Effects on analytical pipelines, metrics, and statistical evaluation.
- **affected_research_questions:** Which research questions are governed or bounded by this decision.
- **scope_effect:** Summary of boundaries established or superseded work excluded.

---

## Decisions

### D001 — Ecosystem Scope Reduction

- **decision_id:** D001
- **date:** 2026-09-11
- **status:** FINALIZED
- **approved_by:** researcher (formal supervisor approval: not_recorded)
- **original_design:** Node.js/npm plus Spring Boot/Maven and broader cross-ecosystem comparative analysis across multiple programming languages.
- **final_design:** Restrict empirical scope strictly to Node.js and the npm package ecosystem.
- **rationale:** The earlier multi-ecosystem design was too broad for the available dissertation timeline and would multiply extraction pipelines, package registry validation architectures, and statistical analysis workflows.
- **methodological_justification:** Restricting the experiment to one ecosystem improves experimental consistency, eliminates package registry architecture as a confounding variable, and enables deeper, high-fidelity analysis of hallucinated npm dependencies. Spring Boot/Maven and other ecosystems represent superseded planning and are preserved as recommendations for future work.
- **impact_on_data_collection:** Data collection infrastructure only needs to support Node.js/JavaScript/TypeScript source code extraction and npm registry HTTP queries. Eliminates the requirement to build Maven Central API integration, `pom.xml`/Gradle build file parsers, and Java import extraction modules.
- **impact_on_analysis:** Analysis focuses strictly on npm package ecosystem dynamics, naming conventions, and registry availability without requiring cross-ecosystem normalization or comparative registry modeling.
- **affected_research_questions:** RQ1, RQ2, RQ3, RQ4 (bounds all empirical research questions strictly to the Node.js/npm ecosystem).
- **scope_effect:** Substantial reduction in experimental complexity; Spring Boot/Maven empirical evaluation deferred to future work.

---

### D002 — Final Task Set Standardization

- **decision_id:** D002
- **date:** 2026-09-11
- **status:** FINALIZED
- **approved_by:** researcher (formal supervisor approval: not_recorded)
- **original_design:** Broader, potentially larger prompt-sampling plan across arbitrary programming tasks without fixed category stratification.
- **final_design:** Exactly 30 standardized tasks stratified across 6 functional categories (Authentication and Authorization, Database Connectivity and Integration, File Handling and Processing, API Development and Endpoints, Security Features and Encryption, Logging and Caching), with exactly 5 tasks per category, all standardized at medium difficulty.
- **rationale:** Provides balanced category coverage across representative backend development domains without unnecessarily inflating experimental workload or introducing task-complexity variance.
- **methodological_justification:** Structured stratification across 6 representative functional categories ensures systematic comparison across functional domains while maintaining strict experimental control. This design provides structural coverage of backend tasks without implying that 30 tasks statistically represent the entire software engineering domain.
- **impact_on_data_collection:** Freezes the prompt suite to exactly 30 deterministic prompt templates, ensuring repeatable and uniform execution across all experimental workflows.
- **impact_on_analysis:** Enables balanced comparison across workflows and functional categories with equal baseline observations per category (5 tasks × 4 workflows × 3 runs = 60 observations per category).
- **affected_research_questions:** RQ1, RQ2.
- **scope_effect:** Fixes task set at 30 tasks across 6 categories; eliminates open-ended prompt expansion.

---

### D003 — Experimental Workflows Selection

- **decision_id:** D003
- **date:** 2026-09-11
- **status:** FINALIZED
- **approved_by:** researcher (formal supervisor approval: not_recorded)
- **original_design:** Earlier planning contemplated comparing disparate AI models or LLM architectures directly, potentially including GitHub Copilot, Claude, Cursor, Devin, OpenHands, or arbitrary open-source models, treating them as abstract foundation model comparisons.
- **final_design:** Compare exactly four accessible contemporary AI coding workflows/tool environments finalized by the researcher:
  1. ChatGPT Web
  2. Gemini Web
  3. Codex CLI
  4. Antigravity CLI
  Tool and model versions are recorded if visibly exposed in the interface or metadata; otherwise recorded as the literal value `not_exposed`.
- **rationale:** Selected by the researcher to represent accessible contemporary AI development workflows spanning both interactive conversational web interfaces and terminal-integrated developer CLI environments.
- **methodological_justification:** These environments are compared as operational AI coding workflows/tool environments rather than four equivalent or directly comparable underlying LLM architectures. Underlying model weights, system prompts, retrieval augmentations, or decoding configurations may vary and are often proprietary or unexposed. Treating them as developer workflows avoids ungrounded claims about underlying model architectures.
- **impact_on_data_collection:** Standardizes collection protocols across two web interfaces and two CLI tools. Enforces strict provenance logging: visible metadata is recorded, while unexposed parameters (temperature, seed, specific model checkpoint) are marked `not_exposed` rather than guessed.
- **impact_on_analysis:** Cross-tool comparisons evaluate practical developer workflow environments rather than foundation models. Excludes speculative attribution of differences to unverified internal model mechanisms.
- **affected_research_questions:** RQ1, RQ2, RQ3.
- **scope_effect:** Restricts tool scope strictly to four finalized workflows; excludes GitHub Copilot, Claude, Cursor, Devin, OpenHands, and other tools from the empirical matrix.

---

### D004 — Three Independent Generations Sample Design

- **decision_id:** D004
- **date:** 2026-09-11
- **status:** FINALIZED
- **approved_by:** researcher (formal supervisor approval: not_recorded)
- **original_design:** Possibility of larger repetition counts (e.g., 5 or 10 runs per prompt) or single-run observational sampling.
- **final_design:** Exactly 3 independent generations per task/workflow combination, yielding a complete baseline dataset of:
  30 tasks × 4 workflows × 3 independent generations = 360 baseline outputs.
- **rationale:** Provides repeated observations and permits baseline recurrence measurement while keeping data collection, raw artifact preservation, and registry validation feasible within dissertation constraints.
- **methodological_justification:** Three independent generations provide repeated observations, basic evidence of recurrence and variation across workflows, and a balanced and feasible baseline design (360 outputs total), while acknowledging that the repetition count remains limited compared to large-scale Monte Carlo sampling.
- **impact_on_data_collection:** Sets the baseline generation target strictly at 360 outputs. Prevents unbounded or uneven data collection across conditions.
- **impact_on_analysis:** Establishes a fixed baseline denominator (N = 360 completed runs) for the Sample-level Hallucination Rate (SHR) and consistent group sizes for within-tool and cross-tool recurrence analysis.
- **affected_research_questions:** RQ1, RQ2, RQ3.
- **scope_effect:** Freezes baseline dataset size to 360 outputs; establishes clear completion criteria.

---

### D005 — Standardized Dependency-Declaration Prompting

- **decision_id:** D005
- **date:** 2026-09-11
- **status:** FINALIZED
- **approved_by:** researcher (formal supervisor approval: not_recorded)
- **original_design:** Earlier prompt phrasing considered explicitly mandating external libraries/packages (e.g., "use a third-party library to solve this") or testing explicit prompt interventions.
- **final_design:** Standardized dependency-declaration prompting: every workflow receives the same functional task requirements and is asked for a complete implementation. External dependencies actually used must be explicitly declared, but the prompt does not name or recommend specific npm packages and does not require an external package when Node.js built-in functionality is sufficient. Package selection remains the AI workflow's decision.
- **rationale:** Forcing external dependencies would artificially increase the volume of package recommendations and could bias the baseline hallucination rate. Warning models against hallucination would alter baseline model behavior and confound measurement of natural hallucination risk.
- **methodological_justification:** Provides observable dependency recommendations without prescribing which dependency should be selected. The design reflects realistic implementation requests while avoiding package-specific recommendations and anti-hallucination warnings that could bias model behavior. Downstream analysis cleanly differentiates built-in APIs from external dependencies.
- **impact_on_data_collection:** Prompts use standardized functional requirements, request complete implementations, and require explicit declaration of external dependencies actually used, without naming packages or warning about hallucinations.
- **impact_on_analysis:** Enables analysis of dependency recommendations under a shared declaration requirement. Downstream extraction classifies built-in modules (`BUILTIN_OR_LOCAL`) separately from external packages so Package-level Hallucination Rate (PHR) accurately reflects external dependency choices.
- **affected_research_questions:** RQ1, RQ2.
- **scope_effect:** Eliminates prompt-intervention variables and anti-hallucination guardrail experiments from baseline data collection.

---

### D006 — Dependency Classification Refinement

- **decision_id:** D006
- **date:** 2026-09-11
- **status:** FINALIZED
- **approved_by:** researcher (formal supervisor approval: not_recorded)
- **original_design:** Simpler or coarser classification taxonomy such as VALID / HALLUCINATED / AMBIGUOUS / EXCLUDED / UNRESOLVED.
- **final_design:** Five authoritative final research classifications:
  1. VALID
  2. CONFIRMED_HALLUCINATION
  3. LEGACY_OR_REMOVED
  4. AMBIGUOUS
  5. BUILTIN_OR_LOCAL
  `UNRESOLVED` is designated strictly as an operational validation status descriptor (for transient network, DNS, or registry outages), not as a research classification.
- **rationale:** Avoid conflating network failures, historic/unpublished packages, built-in modules, local relative imports, and genuine hallucinations.
- **methodological_justification:** A clean HTTP 404 indicates an absent namespace at query time, but absent packages must undergo historical and ambiguity validation before being labeled hallucinations. Separating removed/unpublished packages (`LEGACY_OR_REMOVED`) from fabricated package names (`CONFIRMED_HALLUCINATION`) is vital for assessing true hallucination rates and slopsquatting risk without distortion.
- **impact_on_data_collection:** Registry validation script captures raw HTTP status codes, timestamped responses, and historical registry flags, separating operational status from classification.
- **impact_on_analysis:** Enables precise calculation of SHR and PHR using only strictly validated `CONFIRMED_HALLUCINATION` records, preventing inflated hallucination rates.
- **affected_research_questions:** RQ1, RQ2, RQ3, RQ4.
- **scope_effect:** Formalizes the dependency taxonomy and establishes explicit boundaries between operational retrieval outcomes and scientific classifications.

---

### D007 — Risk-Model Simplification

- **decision_id:** D007
- **date:** 2026-09-11
- **status:** FINALIZED
- **approved_by:** researcher (formal supervisor approval: not_recorded)
- **original_design:** A complex, broad risk framework incorporating multi-registry differences, typographical naming similarity distances, developer installation probability, workflow privilege levels, autonomous execution depth, and speculative vulnerability metrics.
- **final_design:** A lightweight, empirical risk model based on four observable dimensions:
  1. Namespace Claimability (0–3)
  2. Within-Tool Persistence (0–3)
  3. Functional Criticality (0–3)
  4. Cross-Tool Consistency (0–3)
  Scored on a discrete 0–3 integer scale per dimension, totaling 0–12 across four risk bands (Low [0–3], Moderate [4–6], High [7–9], Critical [10–12]).
- **rationale:** All four final dimensions can be derived directly from collected experimental data and verified registry state without unsupported assumptions, speculative scoring parameters, or unvalidated human surveys.
- **methodological_justification:** An empirical risk model grounded in observable data ensures high reproducibility, transparency, and internal validity. It directly captures the software supply-chain threat (slopsquatting exploitability) without introducing subjective or unmeasurable constructs.
- **impact_on_data_collection:** Data requirements are tightly bounded: registry namespace availability, run repetition recurrence, functional category assignment, and cross-tool generation overlap.
- **impact_on_analysis:** Replaces speculative multi-parameter equations with an objective, reproducible rubric that can be systematically applied to each confirmed hallucinated package.
- **affected_research_questions:** RQ4.
- **scope_effect:** Excludes predictive structural equation modeling, machine learning risk classifiers, and ungrounded scoring variables.

---

### D008 — Developer Study Removal

- **decision_id:** D008
- **date:** 2026-09-11
- **status:** FINALIZED
- **approved_by:** researcher (formal supervisor approval: not_recorded)
- **original_design:** Developer expertise survey, user study, and empirical modeling of developer installation probability based on participant responses.
- **final_design:** No developer survey, no recruited human participants, and no empirical developer installation-probability scoring. Developer trust and blind-installation behaviors are discussed qualitatively using established peer-reviewed literature.
- **rationale:** The executed study contains no recruited human participants. Fabricating or estimating quantitative developer-behavior assumptions would lack empirical justification and would excessively expand ethical review, participant recruitment, and statistical scope beyond the dissertation timeline.
- **methodological_justification:** Maintains a rigorous empirical boundary between observable AI artifact generation and human user behavior. Grounding human factors in existing peer-reviewed literature rather than a small, statistically underpowered survey strengthens academic integrity and avoids methodology overreach.
- **impact_on_data_collection:** Eliminates the requirement for survey instrument design, human subject recruitment, ethical board review for human subjects, and participant telemetry collection.
- **impact_on_analysis:** Removes subjective installation-probability variables from the quantitative risk formula; analysis focuses strictly on empirical artifact properties.
- **affected_research_questions:** RQ4.
- **scope_effect:** Eliminates human subject research from the empirical scope; confines investigation to AI artifact generation and registry validation.

---

### D009 — Mitigation Implementation Removal

- **decision_id:** D009
- **date:** 2026-09-11
- **status:** FINALIZED
- **approved_by:** researcher (formal supervisor approval: not_recorded)
- **original_design:** Potential design, implementation, and empirical testing of active mitigation mechanisms (e.g., building RAG pipelines, Knowledge Graph verification layers, model fine-tuning, or IDE linters).
- **final_design:** Mitigation strategies are presented as literature-informed recommendations and design guidance in the discussion, rather than implemented experimental artifacts.
- **rationale:** The core empirical contribution is measuring hallucination prevalence, recurrence, and supply-chain risk across workflows. Implementing and evaluating multiple prototype mitigation systems would dilute focus, divide engineering effort, and exceed dissertation time limits.
- **methodological_justification:** Separating problem characterization from solution implementation ensures the measurement methodology is rigorously established and executed. Comprehensive empirical baseline data provides a solid foundation from which evidence-based mitigation recommendations can be derived.
- **impact_on_data_collection:** Data collection pipeline focuses entirely on baseline output capture and registry validation; no secondary data collection for prototype defenses is required.
- **impact_on_analysis:** Analysis focuses on diagnostic baseline findings; discussion synthesizes actionable recommendations based on empirical observations and existing literature.
- **affected_research_questions:** RQ1, RQ2, RQ3, RQ4.
- **scope_effect:** Excludes software engineering of defensive tooling (RAG, KG, linters, fine-tuning) from the empirical experimental deliverables.

---

### D010 — Persistence Scope Refinement

- **decision_id:** D010
- **date:** 2026-09-11
- **status:** FINALIZED
- **approved_by:** researcher (formal supervisor approval: not_recorded)
- **original_design:** Potential large-scale repetition experiment repeating all prompt/workflow conditions over multiple iterations (e.g., repeating the full 360-run matrix).
- **final_design:** Targeted second-stage persistence testing conducted on a limited subset of confirmed hallucinations identified from the baseline (approximately 3 additional generations per selected case under the same task/workflow condition).
- **rationale:** Tests repeatability and persistence of specific hallucinated package names without unnecessarily duplicating the entire 360 baseline data collection effort.
- **methodological_justification:** Targeted probing isolates whether hallucinations are transient stochastic artifacts or systematic hallucinations tied to particular prompt-tool pairings, optimizing experimental effort while yielding high-value persistence data.
- **impact_on_data_collection:** Persistence testing is structured as a contingent, targeted second phase, initiated only after baseline analysis identifies candidate confirmed hallucinations.
- **impact_on_analysis:** Directly populates the Within-Tool Persistence dimension of the risk assessment framework for confirmed hallucinated packages without skewing baseline prevalence metrics.
- **affected_research_questions:** RQ3, RQ4.
- **scope_effect:** Prevents unfeasible expansion of the baseline generation matrix while still providing empirical persistence data.

---

### D011 — Research Question Refinement

- **decision_id:** D011
- **date:** 2026-09-11
- **status:** FINALIZED
- **approved_by:** researcher (formal supervisor approval: not_recorded)
- **original_design:** Original proposal questions were broad and open-ended, covering root causes across multiple architectures and ecosystems, empirical slopsquatting exploitation manifestations, developer installation behaviors, and comparative efficacy of mitigation techniques.
- **final_design:** Four tightly focused empirical research questions (RQ1: Prevalence, RQ2: Workflow & Functional Category Differences, RQ3: Persistence & Recurrence, RQ4: Security Risk), strictly aligned with observable data collected from the 360-run matrix and targeted persistence testing.
- **rationale:** The research questions were narrowed before full empirical generation so that conclusions will be based only on observable experimental evidence.
- **methodological_justification:** Aligning research questions strictly with observable, collectible data prevents overclaiming, ensures internal validity, and maintains direct traceability from prompt execution to statistical analysis.
- **impact_on_data_collection:** Data collection is purpose-built to populate metrics directly mapped to RQ1–RQ4 without extraneous data gathering.
- **impact_on_analysis:** Analysis directly addresses each RQ using defined quantitative metrics (SHR, PHR, contingency tables, recurrence rates, risk scoring rubric).
- **affected_research_questions:** RQ1, RQ2, RQ3, RQ4.
- **scope_effect:** Aligns dissertation scope directly with the achievable empirical evidence base.

---

### D012 — Risk Scoring Rubric Pre-Specification

- **decision_id:** D012
- **date:** 2026-09-11
- **status:** FINALIZED
- **approved_by:** researcher (formal supervisor approval: not_recorded)
- **original_design:** The lightweight model had four dimensions and a 0–3 scale, but exact score thresholds had not yet been formally defined.
- **final_design:** The exact 0–3 criteria for Namespace Claimability, Within-Tool Persistence, Functional Criticality, and Cross-Tool Consistency were specified before final empirical results were analysed, including an exhaustive and deterministic Within-Tool Persistence decision matrix that explicitly handles all combinations of baseline observations (1/3, 2/3, 3/3) and targeted persistence testing outcomes.
- **rationale:** Prevent post-hoc adjustment of scoring rules after observing results.
- **methodological_justification:** Pre-specifying the rubric improves transparency, reproducibility and reduces researcher degrees of freedom when assigning risk scores.
- **impact_on_data_collection:** Ensures the pipeline records the registry, recurrence, category and workflow evidence necessary to calculate each dimension.
- **impact_on_analysis:** Each confirmed hallucination can be scored using the same predefined rules. Risk bands remain descriptive rather than probabilistic.
- **affected_research_questions:** RQ4
- **scope_effect:** Freezes the lightweight model and prevents additional risk variables or post-hoc scoring criteria from being introduced without a new documented methodology decision.

### D013 — Task Difficulty Standardization

- **decision_id:** D013
- **date:** 2026-09-14
- **status:** FINALIZED
- **approved_by:** researcher (formal supervisor approval: not_recorded)
- **original_design:** Tasks were labelled medium difficulty without an explicit rubric.
- **final_design:** A qualitative medium-difficulty rubric was defined before final prompt freezing. Each task must represent a realistic Node.js backend development requirement, require multiple meaningful implementation steps beyond a trivial single-function solution, remain implementable within one self-contained AI response, avoid large-scale distributed architecture or advanced infrastructure design, and be understandable without follow-up clarification. Equal difficulty does not mean identical code length, dependency count, or implementation complexity; tasks remain reasonably comparable rather than artificially identical.
- **rationale:** Improve consistency and reproducibility in the final task set.
- **methodological_justification:** Defining the rubric before final prompt freezing avoids arbitrary post-hoc task difficulty claims and provides a consistent basis for review.
- **impact_on_data_collection:** All 30 final tasks were reviewed against the same qualitative criteria before collection.
- **impact_on_analysis:** Category comparisons are less likely to be dominated by obvious trivial or extreme task outliers.
- **affected_research_questions:** RQ1, RQ2
- **scope_effect:** No numerical difficulty model is introduced.

---

### D014 — Reproducible Codex CLI Pilot Automation

- **decision_id:** D014
- **date:** 2026-09-15
- **status:** FINALIZED
- **approved_by:** researcher (formal supervisor approval: not_recorded)
- **original_design:** Manual CLI operation using an initialized repository artifact directory as the possible agent workspace, with the transcript treated as the required raw CLI capture.
- **final_design:** Automate Codex pilot collection using one fresh `codex exec` process per manifest row, exact prompt bytes over stdin, a dedicated clean external `CODEX_HOME`, an external disposable read-only workspace, external output staging, explicit model/configuration pins, and verified feature disables. Preserve `response.md` as the canonical model response and JSONL `transcript.txt` plus `stderr.txt` as separate operational evidence.
- **rationale:** Automation reduces operator variation and prevents user configuration, repository context, conversation history, and output-copying differences from silently changing the Codex condition.
- **methodological_justification:** Fixed invocation arguments, prompt hashing, independent processes, append-only preservation, explicit failure states, and no automatic retry improve reproducibility without changing the frozen v1.0.0 prompts or selecting runs based on observed hallucinations.
- **impact_on_data_collection:** Codex CLI `0.154.0` is pinned to provider `OpenAI`, model `gpt-5.6-sol`, reasoning effort `medium`, service tier `default`, disabled web search, an ephemeral session, read-only sandboxing, ignored user config/rules, and verified disabled optional integrations and execution features. Only pilot Codex rows are enabled initially. Failed evidence is retained but never finalized as successful.
- **impact_on_analysis:** The canonical dependency-extraction input for Codex is `response.md`; transcripts and stderr remain audit evidence rather than being conflated with the model's final response. Pilot records remain excluded from all final baseline denominators.
- **affected_research_questions:** RQ1, RQ2, RQ3, RQ4 (collection provenance and validity only; no change to measurement definitions).
- **scope_effect:** Adds deterministic pilot collection mechanics while keeping manual Web collection, frozen prompts, immutable manifests, downstream npm-only analysis, and the 360-run baseline design unchanged.

---

### D015 — API Model and Dependency-Intensive Task-Set Redesign

- **decision_id:** D015
- **date:** 2026-09-16
- **status:** FINALIZED (provider pinning and artifact freeze remain preflight gates)
- **approved_by:** researcher (formal supervisor approval: not_recorded)
- **timing:** Decided before official final data generation; no official API dataset existed at the time of redesign.
- **superseded_design:** The official 360-generation comparison of ChatGPT Web, Gemini Web, Codex CLI, and Antigravity CLI using the v1 general functional task set and mixed manual/CLI collection mechanics.
- **candidate_design:** Compare M1 OpenRouter `qwen/qwen3-coder:free`, M2 OpenRouter `deepseek/deepseek-r1-0528:free`, M3 Groq `openai/gpt-oss-120b`, and M4 OpenRouter `nvidia/nemotron-3-ultra-550b-a55b:free` under a common stateless API protocol. Use candidate task set `final-2.0.0`, containing 30 dependency-intensive Node.js/npm tasks across six specialized domains with three independent repetitions, for 360 official generations.
- **rationale:** A common API protocol supports automated generation, reduces manual copy/paste error, preserves exact request and response bytes, improves reproducibility, fixes model identification, and captures consistent generation and routing metadata.
- **provider_routing_control:** Inspect OpenRouter endpoints before freeze, select and pin one underlying provider per model where the free API permits it, disable fallbacks, and capture the resolved provider for every response. If pinning is unavailable, document and approve the limitation prospectively; never invent provider names or silently conceal changes.
- **sampling_control:** Candidate temperature 0.6, top-p 0.95, and maximum output tokens 6000 are used only after consistent support is confirmed. Seed is not controlled. No tools, browsing, retrieval, execution, external files, prior context, or model-specific prompt changes are allowed.
- **retry_control:** Retry only HTTP 429, network/transport failures, or 5xx without a valid response. Preserve every valid response regardless of quality or observed package behavior, and log all infrastructure attempts.
- **preserved_methodology:** Node.js/npm-only scope; 30 × 4 × 3 sample size; pilot/final separation; immutable raw responses; direct-dependency unit; five primary package classifications; SHR and PHR; analytically separate package version/API/capability categories; and deterministic `risk-model-1.0.0` Impact × Detectability scoring.
- **historical_preservation:** The repository has no `prompts/tasks/final_1.0.0.jsonl`, and none will be reconstructed. Existing v1 provenance is `prompts/prompts_v1.0.0.json`, `prompts/prompts_v1.0.0.csv`, `prompts/prompt_template_v1.0.0.md`, the 30 files under `data/generated_prompts/v1.0.0/`, and their hashes recorded in the historical manifests. Those artifacts, manifests, pilot data, raw responses, and CLI collection code remain unchanged. Old identifiers are not reused. V2 rendering and manifest generation are deferred until review.
- **affected_research_questions:** Replaces RQ1–RQ4 with the open-weight model, secondary package-knowledge, specialized-domain comparison, and practical-risk questions stated in the controlling methodology update.
- **scope_effect:** Changes the comparison conditions and task domains without increasing the official 360-generation total or adding ecosystems, developer studies, mitigation experiments, transitive-dependency analysis, or ML risk scoring.

---

### D016 — API Preflight and Explicit No-Tools Gate

- **decision_id:** D016
- **date:** 2026-09-16
- **status:** RESOLVED_BY_D017_BEFORE_COLLECTION
- **decision:** Official requests expose no tools. Groq `openai/gpt-oss-120b` sends `tool_choice: "none"` and no `tools`. Each OpenRouter condition must prospectively record either supported `tool_choice: "none"` or a documented omit-only mode if its endpoint rejects that explicit parameter; unresolved behavior blocks collection. OpenRouter fallbacks remain disabled, provider pinning is not selected automatically, and retries must honor `Retry-After` without changing sampling parameters.
- **preflight_observation:** On 2026-09-16, M1 and M2 had no available OpenRouter endpoints, M3 was active on Groq, and M4 exposed one free NVIDIA endpoint. Therefore the four-condition set and common parameters cannot yet be frozen.
- **scope_effect:** Adds operational safeguards and records a pre-collection blocker; it creates no generation, result, manifest row, or model substitution.

---

### D017 — Availability-Only Model Replacement and Response-Size Revision

- **decision_id:** D017
- **date:** 2026-09-16
- **status:** CANDIDATE_PENDING_RESEARCHER_REVIEW
- **timing:** Decided before official final generation; no experimental task had been submitted to any candidate API condition.
- **model_replacement:** Replace unavailable candidate M1 OpenRouter `qwen/qwen3-coder:free` with M1 OpenRouter `cohere/north-mini-code:free`, and unavailable candidate M2 OpenRouter `deepseek/deepseek-r1-0528:free` with M2 Groq `qwen/qwen3.8-27b`. M3 Groq `openai/gpt-oss-120b` and M4 OpenRouter `nvidia/nemotron-3-ultra-550b-a55b:free` remain unchanged.
- **replacement_rationale:** The rejected M1/M2 records had zero runnable endpoints during metadata-only preflight. Replacement used endpoint availability and reproducibility only. No generated task output, package behavior, hallucination observation, or performance comparison existed or influenced selection.
- **replacement_preflight:** All four current conditions are active and support temperature `0.6`, top-p `0.95`, and a 6000-token output cap. No seed or model-specific reasoning parameter is sent. Groq and supported OpenRouter endpoints use `tool_choice: "none"` with no `tools`.
- **provider_proposals:** Under the predeclared rule of complete parameter support, zero cost, active status, provider-native/reproducible metadata, and lexical tie-break only if required, propose M1 `Cohere` / `cohere` and M4 `Nvidia` / `nvidia`. Each is the sole suitable zero-cost endpoint. Proposals are not frozen pins until researcher approval.
- **task_revision:** Minimally narrow 16 previously warned `final-2.0.0` prompts to core implementation files, representative fixtures, essential validation, and focused tests suitable for the 6000-token cap. Preserve all specialized standards, package/version/API/capability and interoperability requirements, all 30 task IDs, six balanced categories, task-set version, and neutral package selection. Review but do not alter `DATA-ADV-02`, whose residual warning reflects genuine ecosystem difficulty rather than response volume. The revised candidate SHA-256 is `ef0aff59f8a3934f65379d34036848652b7b5593f595ffa4b449a15af021546b`; it is not yet a frozen rendered-prompt hash.
- **preserved_methodology:** Primary package-name hallucination remains separate from secondary version/API/capability findings, and `risk-model-1.0.0` remains deterministic and rule-based.
- **scope_effect:** Resolves the availability blocker and reduces response-size confounding without producing data, selecting models from observed outcomes, freezing provider pins, rendering prompts, or creating a v2 manifest.

---

### D018 — Freeze API Model Set, Task Set, Prompt Rendering, and Official Manifest

- **decision_id:** D018
- **date:** 2026-09-16
- **status:** FROZEN_BEFORE_OFFICIAL_COLLECTION
- **researcher_approval:** Approves M1 OpenRouter `cohere/north-mini-code:free` pinned to `cohere`; M2 Groq preview `qwen/qwen3.8-27b`; M3 Groq `openai/gpt-oss-120b`; M4 OpenRouter `nvidia/nemotron-3-ultra-550b-a55b:free` pinned to `nvidia`; and the revised `final-2.0.0` task set including 13 intentional residual warnings.
- **final_availability_gate:** Metadata-only recheck at `2026-09-16T06:05:24.433082Z` found all four exact models active. M1 and M4 retained their sole approved zero-cost provider endpoints with the required parameter surface. No completion request was made by the gate.
- **frozen_protocol:** Temperature `0.6`, top-p `0.95`, maximum output `6000`, seed omitted, exactly one user message, no previous context, no tools, no browsing, no retrieval, no code execution, and no function calling. OpenRouter uses `max_tokens`; Groq uses `max_completion_tokens`; all conditions send `tool_choice: "none"` because the frozen endpoints support it. No reasoning-effort control is sent and model defaults remain intrinsic.
- **task_and_prompt_freeze:** Freeze the 30-record task file at SHA-256 `ef0aff59f8a3934f65379d34036848652b7b5593f595ffa4b449a15af021546b`, use the neutral v2 template, and deterministically render 30 identical-across-condition prompts under `data/generated_prompts/v2.0.0/`.
- **manifest_freeze:** Create `manifests/api_final_v2.0.0_manifest.csv` with 360 pending rows, unique API run IDs, exact prompt hashes, provider pins, and deterministic balanced collection order. No row is completed at freeze.
- **unavailability_policy:** Before a model's first official observation, unavailability stops the study and any prospectively approved replacement requires regenerated frozen configuration and manifest. After observations begin, stop only that condition, preserve completed observations, never mix a replacement under the same condition, and restart any approved replacement as a new condition. Hallucination outcomes never influence replacement.
- **smoke_boundary:** Write a versioned freeze record before four explicitly excluded smoke completions. Smoke outputs are infrastructure evidence only and never enter official metrics.
- **scope_effect:** Authorizes frozen artifacts and excluded smoke testing but does not authorize starting the official 360-generation collection.

---

### D019 — Excluded Smoke-Test Infrastructure Result

- **decision_id:** D019
- **date:** 2026-09-16
- **status:** OFFICIAL_COLLECTION_BLOCKED_PENDING_GROQ_TRANSPORT_RESOLUTION
- **boundary:** Exactly four logical `SMOKE-API-001` generations were attempted after the freeze record, one per frozen condition. The smoke task and outputs are excluded from the official manifest and all metrics; content quality and package claims were not assessed.
- **result:** M1 and M4 completed with exact requested model IDs, correct pinned providers, no tool calls, preserved metadata, and verified hashes. M2 and M3 each returned one HTTP 403 edge response with body `error code: 1010` before any model response.
- **retry_decision:** No Groq repeat was sent because HTTP 403 is outside the frozen retry set. The collector was hardened with a fixed User-Agent for future transport compatibility, but another completion smoke requires prospective approval.
- **impact:** The experimental configuration remains frozen, but official collection must not begin until Groq completion access is resolved and infrastructure readiness is re-approved. No model replacement is authorized or implied.

---

### D020 — Groq HTTP Transport Correction and Truncation Safeguard

- **decision_id:** D020
- **date:** 2026-09-16
- **status:** IMPLEMENTED_BEFORE_OFFICIAL_COLLECTION
- **evidence:** A manual conventional HTTP/1.1 Groq completion request returned HTTP 200 for exact model `openai/gpt-oss-120b`, including a Groq request ID and rate-limit headers, while the earlier Python `urllib.request` M2/M3 smokes returned Cloudflare HTTP 403 error 1010 before Groq. Account authorization, model access, and general network access therefore work; the strongest supported diagnosis is an incompatibility in the original collector HTTP transport/header profile.
- **transport_correction:** Replace only the completion POST implementation with the already-installed `requests` 2.33.1 / `urllib3` 2.7.0 HTTP/1.1 client. Send stable `User-Agent: ai-hallucination-study/1.0`, `Accept: application/json`, and `Content-Type: application/json` headers, retain Bearer authorization without serialization, preserve exact request-body bytes, disable redirects, and retain conventional environment-proxy behavior. No proxy variables were set during the correction. No browser impersonation, rotating header, Cloudflare bypass, proxy rotation, fingerprint spoofing, or dependency installation is used.
- **truncation_control:** A valid response with `finish_reason: "length"` is preserved once and marked operationally as `TRUNCATED`; it is never content-retried or regenerated. Preserve finish reason, full usage metadata, total completion tokens, exposed reasoning tokens, and exposed visible-response tokens. Report truncated observations separately in dataset-quality statistics.
- **denominator_review_at_time:** Existing SHR language did not explicitly decide whether a truncated yet potentially analyzable response entered the primary denominator. D021 prospectively resolves this issue before official collection by excluding `TRUNCATED` observations from primary SHR/PHR while retaining them in the preserved dataset and separate quality reporting.
- **frozen_semantics:** Model IDs, M1/M4 pins, task and prompt bytes/hashes, official manifest, temperature `0.6`, top-p `0.95`, 6000-token cap, seed policy, one-message/no-tools protocol, reasoning-effort policy, and collection order remain unchanged. Do not regenerate the freeze record.
- **re_smoke_result:** The first local execution series (`SMOKE-API-002`) was preserved after the network sandbox prevented any HTTP exchange and the frozen transport retry sequence was exhausted. The separately preserved, actually transmitted `SMOKE-API-003` observations each succeeded on their first HTTP attempt: M2 returned exact `qwen/qwen3.8-27b`, M3 returned exact `openai/gpt-oss-120b`, both returned zero tool calls and `finish_reason: "stop"`, and both preserved raw response, assistant content, usage, safe headers, and hashes. M2 exposed 274 completion tokens and no reasoning-token count; M3 exposed 1,293 completion tokens including 663 reasoning tokens. Neither exposed a visible-response-token count.
- **readiness:** Original M1/M4 successes remain unchanged, the replacement Groq re-smokes passed, and all four frozen conditions are infrastructure-ready. Official collection remains a separate deliberate action and has not begun.

---

### D021 — Freeze Primary-Metric Treatment of Truncated Responses

- **decision_id:** D021
- **date:** 2026-09-16
- **status:** FROZEN_BEFORE_FIRST_OFFICIAL_API_GENERATION
- **observation_rule:** A provider-valid response with `finish_reason: "length"` is an official experimental observation with operational status `TRUNCATED`. Preserve it under its original official run ID without regeneration, retaining the exact raw provider response, visible assistant content including empty content, exposed reasoning metadata, token usage, and finish reason.
- **primary_shr_rule:** A truncated observation is not a completed generation for primary analysis. The primary SHR denominator is completed, non-truncated generations eligible for analysis.
- **primary_phr_rule:** The primary PHR occurrence population is eligible external npm package recommendations extracted from completed, non-truncated generations. Truncated observations are excluded from both the primary PHR numerator and denominator.
- **separate_reporting:** Report scheduled runs, completed runs, truncated runs, infrastructure failures, overall truncation rate, truncation rate by model, and truncation rate by task category. Truncated outputs remain part of the preserved research dataset and may be described qualitatively or used in a separately labelled sensitivity analysis, but those results must never be mixed with primary SHR/PHR estimates.
- **timing:** This rule was frozen prospectively while all 360 official manifest rows remained pending and before the first official API generation.
- **supersession:** The earlier D009 planning assumption of a fixed primary SHR denominator of 360 completed runs is superseded only on this point. The schedule remains fixed at 360 runs; the primary denominator is the completed, non-truncated eligible subset.
- **scope_effect:** Resolves the denominator review raised in D020 without otherwise redesigning SHR, PHR, the hallucination taxonomy, the risk model, the frozen task/model sets, generation settings, provider pins, manifest, prompt bytes/hashes, or collection order.

---

### D022 — Stop v2.0 Collection and Freeze the v2.1 Interface-Suitability Gate

- **decision_id:** D022
- **date:** 2026-09-16
- **status:** CRITERIA_FROZEN_BEFORE_SUITABILITY_REQUESTS
- **timing:** Recorded after exactly two v2.0 official observations and before any v2.1 suitability request or official observation.
- **v2.0_stop:** Official v2.0 collection stopped after exactly `API-AUTH-FED-01-M1-R01` and `API-AUTH-FED-01-M2-R01`. The standardized no-tools API condition did not reliably elicit standalone text/code output: M1 returned structured `tool_calls` with `finish_reason: tool_calls` despite `tool_choice: "none"` and no exposed tools; M2 returned assistant content primarily comprising simulated `<tool_call>` markup and repository-inspection requests despite no repository or tools.
- **analysis_status:** v2.0 is stopped/aborted for final-analysis purposes. Its two observations remain immutable methodological evidence and must not enter the eventual v2.1 primary dataset. The historical freeze commit, v2.0 manifest, and existing raw run directories remain unchanged.
- **decision_basis:** Output-interface validity only. Package correctness and observed hallucination rate were not evaluated and did not influence this decision.
- **candidate_conditions_retained:** Retain M1 `cohere/north-mini-code:free`, M2 `qwen/qwen3.8-27b`, M3 `openai/gpt-oss-120b`, and M4 `nvidia/nemotron-3-ultra-550b-a55b:free`, including the existing M1/M4 provider pins. No model is replaced at this stage.
- **v2.1_wrapper:** Preserve each `final-2.0.0` task text byte-for-byte and append the same neutral text-only interface instruction from `prompts/prompt_template_v2.1.0.md`. The wrapper contains no package-verification, anti-hallucination, registry-lookup, or model-specific wording. No official v2.1 manifest is authorized yet.
- **excluded_suitability_task:** `SUITABILITY-API-001` is a small non-final Node.js/TypeScript task. Its prompt and all four responses are excluded from the official dataset and hallucination metrics.
- **frozen_pass_gate:** A condition passes only when the HTTP/model response is valid; structured provider `tool_calls` are absent; finish reason is not `tool_calls`; simulated tool-call markup is absent; the response does not stop merely for repository/file inspection; substantive requested implementation is inline; and no actual tools were exposed or executed.
- **explicit_non_evaluations:** Do not evaluate dependency validity, hallucination frequency, code correctness, security quality, or relative solution quality.
- **request_protocol:** Exactly one suitability generation per retained condition; temperature `0.6`; top-p `0.95`; 6000-token maximum; seed omitted; one user message; no `tools`; `tool_choice: "none"`; no browsing, retrieval, or execution; existing M1/M4 pins; infrastructure retries only under the existing policy; no content retry.
- **stop_rule:** If any model fails, stop and report without automatic replacement. If all pass, report suitability but do not freeze v2.1 or begin official collection.
- **scope_effect:** Prospectively repairs and tests only the output interface. It does not change the 30 research task records, generate a v2.1 official manifest, authorize official collection, or assess package outcomes.

---

### D023 — v2.1 Excluded Interface-Suitability Result

- **decision_id:** D023
- **date:** 2026-09-16
- **status:** ALL_FOUR_CONDITIONS_INTERFACE_SUITABLE; V2.1_NOT_YET_FROZEN
- **timing:** Recorded after the four requests governed by the prospectively frozen D022 gate.
- **request_count:** Exactly four logical suitability generations were sent, one each to M1, M2, M3, and M4. Every condition completed on its initial HTTP attempt; no infrastructure retry and no content retry occurred.
- **result:** All four conditions returned HTTP 200, the exact requested model ID, `finish_reason: stop`, zero structured provider tool calls, no simulated tool-call markup, and substantive inline requested implementation. Completion-token counts were M1 1,536; M2 3,211; M3 2,256; and M4 1,486.
- **tool_boundary:** Every request omitted `tools`, explicitly sent `tool_choice: "none"`, and exposed or executed no actual tool. There was no browsing, retrieval, repository access, code execution, or external execution environment.
- **provider_pins:** OpenRouter resolved M1 to the existing `Cohere` pin and M4 to the existing `Nvidia` pin. M2 and M3 used Groq.
- **evaluation_boundary:** The result assesses interface suitability only. Dependency validity, hallucination frequency, code correctness, security quality, and comparative solution quality were not evaluated.
- **data_boundary:** Task `SUITABILITY-API-001` and all responses under `data/suitability/api/v2.1.0/` are excluded from the official research dataset and hallucination metrics.
- **next_state:** All four retained models are suitable for the standardized text-only v2.1 condition. This result does not freeze v2.1, create an official v2.1 manifest, or authorize official collection.

---

### D024 — Freeze v2.1 Standardized Text-Only Experimental Condition

- **decision_id:** D024
- **date:** 2026-09-16
- **status:** FINALIZED
- **approved_by:** researcher (formal supervisor approval: not_recorded)
- **original_design:** v2.0 unadorned task prompt interface without explicit text-only wrapper, which resulted in tool-call invocation (M1) or simulated tool markup (M2) in the first two observations.
- **final_design:** v2.1 standardized stateless text-only interface appending `prompts/prompt_template_v2.1.0.md` to every task prompt. Four models retained unchanged (M1 `cohere/north-mini-code:free`, M2 `qwen/qwen3.8-27b`, M3 `openai/gpt-oss-120b`, M4 `nvidia/nemotron-3-ultra-550b-a55b:free`), existing M1/M4 provider pins preserved, sampling parameters unchanged (temperature `0.6`, top-p `0.95`, max completion tokens `6000`, seed omitted, 1 user message, no tools/retrieval/browsing/execution/reasoning-effort), 30 underlying tasks in `prompts/tasks/final_2.0.0.jsonl` unchanged, model set referenced as `api-model-set-1.0.0`, 360-row manifest `manifests/api_final_v2.1.0_manifest.csv` with unique versioned run IDs (`API-v2.1-...`), separate batch state `data/final/api_batch_state_v2.1.0.json`, and pre-generation freeze record `config/experiment_freeze_v2.1.0.json` / `docs/experiment_freeze_v2.1.0.md`.
- **rationale:** Standardizes the prompt wrapper to prevent models from attempting interactive tool calls or workspace inspection while preserving identical task content and objective evaluation across all four model conditions.
- **methodological_justification:** The neutral text-only wrapper contains no package-verification, anti-hallucination, registry-lookup, or model-specific hints. Agentic-capable models are evaluated under a standardized stateless text-only generation interface. The two aborted v2.0 observations remain immutable methodological evidence but are strictly excluded from the v2.1 final dataset.
- **impact_on_data_collection:** Complete physical and logical separation of v2.1 data (manifest, rendered prompts, run IDs, batch state) from v2.0 aborted observations, smoke tests, suitability tests, and historical pilot data.
- **impact_on_analysis:** 360 official planned observations (90/model, 120/rep, 60/cat); primary SHR/PHR evaluation applies strictly to completed non-truncated v2.1 generations.
- **affected_research_questions:** RQ1, RQ2, RQ3, RQ4.
- **scope_effect:** Freezes the v2.1 experimental condition with zero official observations generated; does not authorize starting collection.

---

### D025 — Increase Max Output Tokens to 12000 and Freeze v2.2 Experiment

- **decision_id:** D025
- **date:** 2026-09-16
- **status:** FINALIZED
- **approved_by:** researcher (formal supervisor approval: not_recorded)
- **original_design:** v2.1 standardized stateless text-only interface with 6000 max output token limit (`max_output_tokens: 6000`).
- **final_design:** v2.2 standardized stateless text-only interface with 12000 max output token limit (`max_output_tokens: 12000`) under versioned model-set `api-model-set-1.1.0` (`config/api_model_set_1.1.0.json`). All other experimental semantics unchanged: task set (30 tasks in `prompts/tasks/final_2.0.0.jsonl`), prompt wrapper text (`prompts/prompt_template_v2.2.0.md` byte-for-byte equivalent to v2.1), model set (M1 `cohere/north-mini-code:free`, M2 `qwen/qwen3.8-27b`, M3 `openai/gpt-oss-120b`, M4 `nvidia/nemotron-3-ultra-550b-a55b:free`), existing M1/M4 provider pins (`cohere`/`nvidia`), temperature `0.6`, top-p `0.95`, seed omitted (`not_controlled`), no tools exposed (`tool_choice: "none"`), 3 repetitions, Latin-square rotation, 360 manifest rows with `API-v2.2-` prefix in `manifests/api_final_v2.2.0_manifest.csv`, batch state `data/final/api_batch_state_v2.2.0.json`, freeze record `config/experiment_freeze_v2.2.0.json` / `docs/experiment_freeze_v2.2.0.md`. Historical `config/api_model_set_1.0.0.json` (6000 tokens) preserved byte-for-byte for v2.0/v2.1.
- **rationale:** Official collection of the first four v2.1 observations (`API-v2.1-AUTH-FED-01-M1-R01` through `M4-R01`) validated that the text-only wrapper solved the interface-validity issue (all four models provided substantive inline code with zero tool calls). However, 3 of 4 models (M2 Qwen, M3 GPT-OSS, M4 Nemotron) were truncated at the 6000-token ceiling (`finish_reason: length`), and the fourth (M1 Cohere) stopped at 5893/6000 (only 107 tokens below ceiling). To avoid widespread artificial truncation while keeping the prompt and task interfaces identical, the token ceiling was doubled from 6000 to 12000 across all four model conditions.
- **methodological_justification:** The four v2.1 observations are permanently preserved in `data/final/raw/` as methodological evidence and excluded from v2.2 analysis metrics. v2.1 collection was stopped before row 5.
- **infrastructure_fix:** Fixed phantom pacing reservation bug in `scripts/collect_api_batch.py` by ensuring all local pre-transmission validation (API key existence, config checks, prompt path/hash, request body construction, directory collision) completes before reserving provider pacing slots.
- **impact_on_data_collection:** Complete logical and physical isolation of v2.2 artifacts (run IDs `API-v2.2-...`, manifest, rendered prompts, batch state). Zero v2.2 observations collected prior to freeze.
- **impact_on_analysis:** 360 planned observations for v2.2 (90/model, 120/rep, 60/cat). Primary SHR/PHR evaluation applies strictly to completed non-truncated v2.2 generations.
- **affected_research_questions:** RQ1, RQ2, RQ3, RQ4.
- **scope_effect:** Freezes the v2.2 experimental condition with zero official observations generated; does not authorize starting collection.

---

### D026 — Correct Response-Inventory Snapshot Provenance

- **decision_id:** D026
- **date:** 2026-09-17
- **status:** PROVENANCE_CORRECTION_RECORDED
- **issue:** `results/response_inventory_v2.2.0.*` are rolling derived outputs. The first documented PIPE-02 inventory summary (360 planned; 1 completed; 1 truncated; 358 pending) and its JSON/CSV hashes (`b6f44b72c2d7bfc66ec264ae67f368e0b589a33ad5bcf7ac2caa30cc8f34b697` / `34bad9dc91a9126d9fb5830ed03f8017d673022c8491a13a2ca9044747081311`) were terminal-recorded, but the original byte-for-byte files were not preserved before later rolling regeneration.
- **correction:** Retain the first summary and hashes as historical provenance evidence only. Do not attribute them, or their older snapshot time, to regenerated rolling content.
- **preserved_later_snapshot:** The later inventory was preserved at `results/snapshots/response_inventory_v2.2.0_preserved_at_20260917T082919Z.json` and `.csv`. It contains 360 planned runs: 2 completed, 2 truncated, and 356 pending. The JSON/CSV SHA-256 values are `ec4f95f3fc96c3ef305ca59801341b37ef9b1967a02ef79ec7695a77c89722fe` / `a0e05acce5a677b8d50469f6bdb0dacb8e9405482b79ce8b1f13fe8cc22bec04`.
- **observations:** The preserved later inventory's non-pending records are collection orders 1--4: `API-v2.2-AUTH-FED-01-M1-R01` completed (11,347 completion tokens); `API-v2.2-AUTH-FED-01-M2-R01` truncated (12,000); `API-v2.2-AUTH-FED-01-M3-R01` completed (8,893); and `API-v2.2-AUTH-FED-01-M4-R01` truncated (12,000).
- **handling_rule:** When a rolling inventory is cited as a research milestone, preserve a timestamped copy and record its hashes immediately. A preserved inventory is historical derived metadata and may be stale relative to active collection.
- **data_boundary:** No frozen manifest, raw observation, collection state, prompt, model configuration, or pacing rule was modified.

---

### D027 — Prospectively Stop v2.2 and Freeze v2.3 Zero-Artificial-Pacing Collection

- **decision_id:** D027
- **date:** 2026-09-17
- **status:** FINALIZED
- **approved_by:** researcher (formal supervisor approval: not_recorded)
- **original_design:** v2.2 used fixed researcher-imposed minimum intervals of 1,800 seconds for OpenRouter and 2,700 seconds for Groq.
- **final_design:** v2.2 is prospectively stopped after 10 preserved observations (6 completed, 4 truncated, 350 pending of 360 planned). v2.3 is a new, separate 360-observation dataset with `api-model-set-1.2.0` and sequential requests with a zero-second artificial interval after successful requests. Provider-enforced 429/Retry-After and the frozen infrastructure retry/backoff policy remain mandatory.
- **rationale:** The v2.2 fixed spacing was unnecessarily conservative under a tight final collection window.
- **methodological_justification:** The task set, prompt wrapper, exact model IDs, provider pins, no-fallback rule, no-tools condition, sampling parameters, retry philosophy, and truncation handling remain unchanged. The version boundary isolates the operational pacing change and prevents mixing v2.2 observations into v2.3 metrics.
- **impact_on_data_collection:** v2.3 uses fresh `API-v2.3-` IDs, manifest, batch state, prompt directory, and raw-observation namespace. A non-retryable quota/credit/account/provider failure is recorded and stops the batch without skipping, model/provider substitution, or automatic `:free`-to-paid route changes.
- **impact_on_analysis:** The 10 v2.2 observations remain immutable methodological evidence and are excluded from v2.3 primary analysis. v2.3 primary metrics apply only to the fresh 360-observation v2.3 dataset.
- **affected_research_questions:** RQ1, RQ2, RQ3, RQ4.
- **scope_effect:** Payment/account tier is infrastructure availability only and is not an experimental condition when model ID, routing, prompt, and generation parameters remain identical. This decision does not authorize collection during freeze creation.
---

### D028 — Prospectively Stop v2.3 and Freeze v2.4 Fresh Dataset with Failure Continuation

- **decision_id:** D028
- **date:** 2026-09-18
- **status:** FINALIZED
- **approved_by:** researcher (formal supervisor approval: not_recorded)
- **original_design:** v2.3 collection protocol where any non-retryable provider failure (such as HTTP 200 with empty assistant content or HTTP 402) stops the batch without skipping or substitution, blocking subsequent manifest rows.
- **final_design:** v2.3 was prospectively stopped at observation 8 (`API-v2.3-AUTH-FED-02-M1-R01`) after preserving failure evidence. v2.4 is defined prospectively as a fresh, separate 360-observation experiment (`manifests/api_final_v2.4.0_manifest.csv`) where preserved non-retryable failed observations are recorded once with failure evidence, excluded from primary SHR/PHR denominators, and skipped on later invocations so subsequent manifest rows continue sequentially.
- **rationale:** Reusing v2.3 observations inside an amended sample would combine two distinct collection protocols and create denominator/provenance ambiguity. Creating a clean v2.4 dataset isolates the single operational change.
- **methodological_justification:** No generation parameters, models, provider routing pins, task wording, prompt template content, sampling settings (temp 0.6, top-p 0.95, 12000 max tokens), zero artificial pacing, or retry rules are altered. Failed observations are never retried, regenerated for success, or substituted with alternative models/providers.
- **impact_on_data_collection:** Clean `API-v2.4-` run ID prefix, independent batch state (`data/final/api_batch_state_v2.4.0.json`), and versioned prompt copies matching v2.3 byte-for-byte.
- **impact_on_analysis:** All historical observations (v2.0, v2.1, v2.2, v2.3) remain immutable methodological evidence and are excluded from v2.4 primary metrics. Failed observations are counted and reported separately in quality metrics.
- **affected_research_questions:** RQ1, RQ2, RQ3, RQ4.
- **scope_effect:** Zero API calls are executed during freeze and validation.

---

### D029 — PIPE-03 Explicit Package-Reference Extraction Contract

- **decision_id:** D029
- **date:** 2026-09-21
- **status:** IMPLEMENTED
- **decision:** PIPE-03 creates separate, deterministic occurrence-level and unique-normalized-package derived outputs from a response inventory and immutable response artifacts. The occurrence view retains every explicit reference; the unique view deduplicates only by `(run_id, normalized_package)` and retains occurrence count and source types.
- **supported_syntax:** Literal ESM imports, literal CommonJS `require`, literal dynamic `import`, explicit `npm install` / `npm i` operands, and string-valued entries in structurally valid `dependencies`, `devDependencies`, `peerDependencies`, and `optionalDependencies` objects.
- **normalization_and_exclusions:** Scoped package roots retain both scope and package segment; unscoped and scoped subpaths are reduced to their package roots; explicit install-specifier versions and dependency-object version strings are retained. Centralized Node built-ins, `node:` references, local/relative/absolute paths, `file:` references, and HTTP(S) URLs are excluded. No semantic inference is applied to prose.
- **metric_boundary:** This stage does not query a registry, classify package existence or hallucinations, calculate PHR or SHR, score risk, or modify raw observations. Truncated records can be extracted and retain their truncation marker for later, separately governed filtering.
- **data_boundary:** Inputs are read-only inventory and raw-response artifacts. Outputs are versioned derived files under `results/`; collection state, prompts, manifests, raw data, and historical inventory snapshots are not changed.

---

### D030 — Implement Fresh v2.5 Dataset with 16,000-Token Ceiling

- **decision_id:** D030
- **date:** 2026-09-21
- **status:** IMPLEMENTED; commit and tag pending researcher review
- **decision:** After the documented prospective v2.4 stop at 30 finalized observations (14 completed, 12 truncated, 4 failed), create an independent 360-observation v2.5 experiment beginning at observation 1.
- **sole_experimental_change:** Increase `max_output_tokens` from 12,000 to 16,000.
- **preserved_protocol:** Same 30 task IDs and wording, byte-identical prompt template and rendered prompts, four model/provider conditions and pins, no-fallback/no-tools stateless interface, temperature 0.6, top_p 0.95, omitted seed, retry/backoff, v2.4 failure continuation, truncation policy, and zero artificial pacing.
- **data_boundary:** New `API-v2.5-` run namespace, all-pending manifest, and empty state. No v2.4 observation is reused. No v2.5 API request was sent during implementation or validation.
- **analysis_effect:** v2.0–v2.4 remain methodological evidence outside v2.5 primary SHR/PHR denominators. Failed and truncated v2.5 observations, if later collected, remain excluded from those denominators under the preserved policy.

---

### D031 — Implement Fresh Final v2.6 Dataset with Model-Specific Ceilings and Darkbloom-Pinned M2

- **decision_id:** D031
- **date:** 2026-09-22
- **status:** IMPLEMENTED; collection not started; commit and tag pending researcher review
- **decision:** Prospectively stop v2.5 after preserved 16,000-token truncations and create a separate v2.6 360-observation dataset beginning at observation 1. v2.5 observations remain immutable methodological evidence and are excluded from v2.6 primary SHR/PHR.
- **experimental_changes:** Set max output tokens per model condition to M1 64,000, M2 32,768, M3 65,536, and M4 65,536. Move the unchanged M2 model ID `qwen/qwen3.8-27b` from Groq to OpenRouter, pinned to provider slug `darkbloom` with `provider.order` and `provider.only` both restricted to `darkbloom`, `allow_fallbacks: false`, and `require_parameters: true`. No model fallback is supplied.
- **provider_evidence:** OpenRouter's Qwen3.8 27B model and Darkbloom provider pages list the model/provider pairing. OpenRouter's provider-routing documentation defines `order`, `only`, `allow_fallbacks`, and `require_parameters`. OpenRouter model pages and Groq's GPT-OSS-120B model page document the selected output ceilings. The source URLs are recorded in the v2.6 freeze record.
- **preserved_protocol:** The final-2.0.0 task set, template and rendered prompt bytes, four model identities, M1/M4 pins, three repetitions, temperature 0.6, top_p 0.95, uncontrolled seed, stateless single-user-message/no-tools interface, no browsing/retrieval/execution/function calling, infrastructure retry/backoff, preserved-failure continuation, truncation preservation, and zero researcher-imposed pacing remain unchanged.
- **final_protocol_rule:** v2.6 is intended as the final version. Further ceiling hits are preserved as right-censored truncations and excluded from primary SHR/PHR without another protocol restart. Failed observations remain preserved once and excluded. No v2.6 result exists yet.
- **data_boundary:** New `API-v2.6-` run namespace, 360 unique all-pending manifest rows, empty state, byte-identical prompt copies, and zero raw observations. No live API request was sent during implementation.
