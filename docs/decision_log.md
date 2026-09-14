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
