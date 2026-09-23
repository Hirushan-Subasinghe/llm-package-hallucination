# Chapter 1 Evidence Audit — CHAPTER-1-EVIDENCE-AUDIT-01

**Audit date:** 2026-09-23
**Purpose:** Establish a defensible Chapter 1 framing from the implemented final-study design without drafting Chapter 1 prose, calculating metrics, or changing frozen experimental evidence.

## 1. Audit scope

This audit reviewed the controlling project instructions and reporting protocol; current status, progress, paper notes, decisions, analysis, taxonomy, and risk documentation; the approved-reference list and claims–evidence matrix; the frozen v2.6 task, prompt, model, manifest, and freeze artifacts; and the relevant analysis scripts and schemas.

The controlling final study is the fresh v2.6 Node.js/npm experiment. Collection is in progress and final analysis has not run. Therefore all claims about observed prevalence, group differences, recurrence, or risk distributions remain **PENDING**. Historical v2.2–v2.5 material, pilot/smoke/suitability material, and interim checkpoints are not final results.

Milestone documentation decision: progress-log update needed **NO**; final-paper note needed **NO**; draft reconciliation needed **YES** before reusing any Chapter 1 material from the baseline dissertation.

## 2. Verified implemented-study facts

| Item | Verified fact | Exact evidence |
|---|---|---|
| Final experimental ecosystem | Direct **Node.js/npm** dependency recommendations only. The task records specify `runtime: Node.js` and `ecosystem: npm`. | `docs/decision_log.md` D001; `docs/package_hallucination_taxonomy.md` (Scope Controls); `prompts/tasks/final_2.0.0.jsonl`; `docs/current_research_status.md` |
| Final task count | **30** frozen official tasks, task-set version `final-2.0.0`. | `prompts/tasks/final_2.0.0.jsonl` (30 records); `docs/task_set_v2_design.md` (Fixed Structure); `config/experiment_freeze_v2.6.0.json` (`official_manifest`) |
| Task difficulty | **Medium difficulty**, governed by a qualitative rubric; it is not a numeric covariate or a claim of identical complexity. The v2 task redesign preserved bounded, dependency-intensive tasks. | `docs/decision_log.md` D013; `docs/task_set_v2_design.md` (Design Rationale and Pre-freeze Response-Size Revision) |
| Functional-category count and names | **Six** categories, five tasks each: `AUTH-FED` — Identity, Authentication & Federation; `PKI-CRYPTO` — PKI, Cryptography & Trust Services; `DOC-BINARY` — Complex Documents & Binary Formats; `ENT-INT` — Enterprise Messaging & Interoperability; `DATA-ADV` — Specialized Data & Storage Integration; `DIST-OBS` — Distributed Systems & Observability. | `docs/task_set_v2_design.md` (Fixed Structure); `prompts/tasks/final_2.0.0.jsonl`; `config/experiment_freeze_v2.6.0.json` (`rows_per_category`) |
| Model conditions | **Four** frozen model/API conditions. The comparison unit is `frozen_model_api_condition`, not an abstract architecture or a workflow-autonomy condition. | `config/api_model_set_1.4.0.json` (`comparison_unit`, `models`); `config/experiment_freeze_v2.6.0.json` (`model_set`) |
| M1 | `cohere/north-mini-code:free`; API provider **OpenRouter**; underlying provider pin `cohere`; ceiling 64,000 output tokens. | `config/api_model_set_1.4.0.json`; `config/experiment_freeze_v2.6.0.json`; `docs/experiment_freeze_v2.6.0.md` (Model conditions) |
| M2 | `qwen/qwen3.8-27b`; API provider **OpenRouter**; underlying provider pin `darkbloom`, with fallback disabled; ceiling 32,768 output tokens. | `config/api_model_set_1.4.0.json`; `config/experiment_freeze_v2.6.0.json`; `docs/experiment_freeze_v2.6.0.md` (Model conditions) |
| M3 | `openai/gpt-oss-120b`; API provider **Groq**; provider pin `not_applicable`; ceiling 65,536 completion tokens. | `config/api_model_set_1.4.0.json`; `config/experiment_freeze_v2.6.0.json`; `docs/experiment_freeze_v2.6.0.md` (Model conditions) |
| M4 | `nvidia/nemotron-3-ultra-550b-a55b:free`; API provider **OpenRouter**; underlying provider pin `nvidia`; ceiling 65,536 output tokens. | `config/api_model_set_1.4.0.json`; `config/experiment_freeze_v2.6.0.json`; `docs/experiment_freeze_v2.6.0.md` (Model conditions) |
| Repetitions | **Three independent generations** (`R01`, `R02`, `R03`) per task × condition combination. | `config/experiment_freeze_v2.6.0.json` (`rows_per_repetition`); `manifests/api_final_v2.6.0_manifest.csv`; `docs/decision_log.md` D004 and D031 |
| Planned v2.6 observations | **360 planned observations** = 30 tasks × 4 conditions × 3 repetitions; at freeze the manifest had 360 unique pending rows. This is a planned count, not a final eligible-analysis denominator. | `config/experiment_freeze_v2.6.0.json` (`dataset_strategy`, `official_manifest`); `manifests/api_final_v2.6.0_manifest.csv`; `docs/experiment_freeze_v2.6.0.md` |
| Primary outcomes | **PHR** and **SHR**, for conservatively confirmed npm package-name hallucinations. PHR counts one unique `(run_id, normalized_package)` per eligible response; SHR counts completed, non-truncated responses containing at least one primary-confirmed finding. Failed and truncated observations are excluded. | `docs/decision_log.md` D033, D035, D037; `docs/package_hallucination_taxonomy.md` (Primary Outcome; Metric Boundaries); `scripts/build_analysis_dataset.py`; `scripts/calculate_primary_metrics.py` |
| Secondary/exploratory outcomes | **DFR** and **RDFR**, which measure exact-name npm dependency-resolution failure under D036 adjudication rules. They are explicitly secondary/exploratory, are not hallucination rates, and do not capture all forms of dependency unreliability. Secondary package version/API/capability categories are analytically separate from PHR/SHR. | `docs/decision_log.md` D036; `docs/package_hallucination_taxonomy.md` (Secondary Package-Related Categories; Metric Boundaries); `scripts/calculate_dependency_reliability_metrics.py` |
| Risk assessment | `risk-model-1.0.0`: transparent deterministic rule-based assessment after confirmation, **Impact (1–5) × Detectability (1–4)**, yielding 1–20 bands, with a non-scored `security_sensitive_context` flag. It is not an ML model, exploitation probability, or loss forecast. | `docs/risk_assessment_protocol.md`; `docs/decision_log.md` D032; `scripts/score_risk_findings.py`; `schemas/risk_finding_pipe06_v1.schema.json` |
| Grouped/statistical dimensions | Grouped descriptions and comparison infrastructure support **model condition**, **functional category**, **repetition**, and **model condition × category**. Methods are Fisher exact for 2×2; assumption-gated chi-square or deterministic Monte Carlo for sparse multi-group tables; Holm correction; odds ratio/risk difference with 95% CIs. No final inference or ranking exists. | `scripts/analyze_group_comparisons.py`; `docs/research_progress_log.md` (PIPE-09); `docs/final_paper_notes.md` (PIPE-09) |
| Performed / not performed | **Not performed:** human-participant/developer survey; developer-expertise study; Java/Maven or Spring Boot experiment; workflow-autonomy comparison; verification-mediator experiment; package installation or generated-code execution; transitive-dependency analysis; predictive-model training; dynamic mitigation experiment. The frozen design instead used stateless, no-tools API conditions and downstream read-only evidence. | `docs/decision_log.md` D001, D008, D009, D015; `docs/final_paper_notes.md` (Draft reconciliation backlog); `docs/risk_assessment_protocol.md` (Safety and Scope); `docs/package_hallucination_taxonomy.md` (Scope Controls); `config/api_model_set_1.4.0.json` (`interaction_protocol`) |

**Interpretive boundary:** an npm `not_found`/404 is registry evidence, not itself a confirmed hallucination. `UNRESOLVED`, namespace confusion, package-name confusion, ecosystem confusion, legacy/removed, self/local, and other excluded outcomes must not be promoted to the primary numerator without the D037-authorized evidence route.

## 3. Candidate final titles

The following are options, not a title selection.

1. **Package-Name Hallucinations in LLM-Generated Node.js Code: An Empirical Study of npm Dependency Reliability and Practical Risk**
   Scope note: accurately foregrounds primary package-name hallucination, while “dependency reliability” must be described as secondary/exploratory DFR/RDFR analysis.

2. **LLM-Generated Node.js Code and npm Dependency Reliability: Package-Name Hallucination, Grouped Comparisons, and Practical Risk Assessment**
   Scope note: makes the comparative and rule-based risk components visible without asserting final results.

3. **Assessing npm Package-Name Hallucinations in LLM-Generated Node.js Solutions: Implications for Software Supply-Chain Risk**
   Scope note: the most conservative supply-chain wording; the dissertation must state that the risk rubric is an ordinal, evidence-bounded prioritization aid rather than a security-compromise estimate.

## 4. Research problem

LLM-generated Node.js solutions can contain explicit npm dependency references that a developer may use when constructing or executing the proposed solution. Two related but distinct problems require measurement. First, a reference may be a **confirmed package-name hallucination**: an external npm package name that cannot be confirmed as an existing legitimate package under the study's conservative validation and adjudication procedure. Second, a recommendation may exhibit a broader **exact-name dependency-reference reliability failure**—for example, a namespace or package-name confusion—that would fail to resolve as declared but is not evidence of an invented package name. Registry `not_found` evidence alone cannot distinguish these states. A controlled, evidence-preserving Node.js/npm study is therefore needed to measure confirmed package-name hallucination separately from secondary/exploratory exact-name dependency-resolution failures, compare the defined outcomes across the frozen conditions and task categories, and assess the practical consequence of eligible confirmed findings using the implemented rule-based framework.

## 5. Research-gap evidence

### Supported implementation-facing gap

The project has implemented a bounded contemporary study that can address a gap at the following level: a reproducible, condition-specific Node.js/npm evaluation that separates conservative confirmed package-name hallucination from other exact-name dependency-resolution failures; preserves a direct-dependency evidence chain from immutable response to registry/adjudication evidence; supports comparisons by model condition and specialized task category; and applies a transparent, post-classification practical-risk rubric. The project does **not** establish that no prior study has done these things.

Supporting study-design evidence: `docs/methodology_update_2026-09-16.md`; `docs/task_set_v2_design.md`; `config/api_model_set_1.4.0.json`; `docs/package_hallucination_taxonomy.md`; `docs/decision_log.md` D032–D037; `docs/risk_assessment_protocol.md`.

### Literature-framing boundary

The approved reference list contains an approved package-hallucination study (Spracklen et al., 2025) and relevant software-supply-chain references, but the present audit did not reconcile each baseline-dissertation literature claim against the cited source text. Chapter 1 may therefore frame the study as a bounded empirical contribution and state its implemented distinctions, but must not assert novelty, comparative absence, or a literature-wide quantitative gap until the baseline dissertation's claims and approved citations have been checked.

**[DRAFT-LITERATURE-RECONCILIATION REQUIRED]** Verify the baseline Chapter 1/2 claims about prior package-hallucination evidence, ecosystem coverage, validation methods, risk assessment, and mitigation before converting this gap into literature-backed dissertation prose. Use only `docs/references/approved_references.md`; propose any additional source using the required `NEW SOURCE PROPOSED` process.

## 6. Proposed aim

**To empirically assess confirmed npm package-name hallucinations and secondary exact-name dependency-reference reliability failures in LLM-generated Node.js solutions across the frozen model/API conditions and functional task categories, and to assess the practical risk of eligible confirmed findings using the implemented rule-based framework.**

## 7. Proposed objectives

| Objective text | Supporting implementation/evidence | Status |
|---|---|---|
| O1. Measure the prevalence of conservatively confirmed npm package-name hallucinations in the eligible v2.6 Node.js responses using PHR and SHR. | `docs/decision_log.md` D033, D035, D037; `docs/package_hallucination_taxonomy.md`; `scripts/build_analysis_dataset.py`; `scripts/calculate_primary_metrics.py`; v2.6 frozen manifest. | **SUPPORTED** |
| O2. Characterize adjudicated exact-name npm dependency-reference reliability outcomes separately from confirmed package-name hallucination, using the secondary/exploratory DFR/RDFR framework and outcome breakdowns. | `docs/decision_log.md` D036; `scripts/adjudicate_review_required_packages.py`; `scripts/calculate_dependency_reliability_metrics.py`; `docs/package_hallucination_taxonomy.md`. | **SUPPORTED** |
| O3. Describe and, where data support it, compare primary and secondary outcome patterns across model conditions and functional task categories. | `scripts/analyze_group_comparisons.py`; `docs/research_progress_log.md` (PIPE-09); frozen stratified manifest and task set. Repetition is an implemented grouping dimension but does not require a separate objective. | **SUPPORTED** |
| O4. Assess the practical risk level of eligible confirmed package-related findings under `risk-model-1.0.0`. | `docs/risk_assessment_protocol.md`; `docs/decision_log.md` D032; `scripts/score_risk_findings.py`; `schemas/risk_finding_pipe06_v1.schema.json`. | **SUPPORTED** |

The objectives are supported by the final design and implemented pipeline, not by final findings. Final attainment remains pending v2.6 completion and provenance-consistent analysis.

## 8. Proposed research questions

| RQ | Assessment | Exact evidence | Wording correction required | Implemented answer path |
|---|---|---|---|---|
| RQ1. What is the prevalence of confirmed npm package-name hallucinations in LLM-generated Node.js coding responses? | **SUPPORTED** | D033, D035, D037 in `docs/decision_log.md`; `docs/package_hallucination_taxonomy.md`; `scripts/calculate_primary_metrics.py`; v2.6 manifest/freeze. | Replace “coding responses” with “eligible completed, non-truncated Node.js responses” in methods; retain the concise RQ wording if eligibility is defined immediately below it. | PIPE-03/04/05 and 05B → PIPE-07 D037 resolution → PIPE-08 PHR/SHR. |
| RQ2. What types of npm dependency-reference reliability failures occur in the generated responses? | **SUPPORTED** | `docs/decision_log.md` D036; PIPE-05B and PIPE-10 scripts; taxonomy. | Add “under the study's secondary/exploratory exact-name resolution and adjudication rules.” Do not imply all dependency reliability, APIs, versions, capability, or functional suitability. | PIPE-04/05 → PIPE-05B → PIPE-10 DFR/RDFR and required outcome breakdowns. |
| RQ3. How do package-hallucination and dependency-reliability outcomes vary across the studied model conditions and functional task categories? | **PARTIALLY SUPPORTED** | v2.6 stratified manifest; `scripts/analyze_group_comparisons.py`; D036 grouped descriptive provision; PIPE-09 notes. | Say “How are ... outcomes **descriptively distributed and, where estimable, compared** ...?” This avoids promising inferential conclusions when cells are sparse/zero-event and keeps DFR/RDFR secondary/exploratory. | PIPE-09 by `model_condition_id` and `category`; PIPE-10 grouped descriptive output where appropriate. |
| RQ4. What practical risk levels are associated with the identified dependency-related findings under the implemented risk-assessment framework? | **PARTIALLY SUPPORTED** | `docs/risk_assessment_protocol.md`; D032; PIPE-06 script/schema. | Replace “identified dependency-related findings” with “eligible **confirmed package-related hallucination findings**.” The rubric deliberately excludes unresolved, valid, self/local, ordinary errors, and unconfirmed confusion outcomes. | PIPE-06 applies Impact × Detectability to eligible confirmed findings; generation-level maximum is permitted by protocol. |

RQ1–RQ4 are justified by the frozen design and final reporting plan, not merely by the existence of scripts. RQ3 and RQ4 remain conditional on sufficient eligible findings and completed risk assessments, respectively.

## 9. Scope and delimitations

| Topic | Classification | Verified boundary | Evidence |
|---|---|---|---|
| Node.js/npm | IN SCOPE | Direct Node.js/npm dependency recommendations. | D001; task JSONL; taxonomy Scope Controls |
| 30 final tasks | IN SCOPE | Exactly 30 `final-2.0.0` tasks. | task JSONL; task-set design; v2.6 freeze |
| Six functional categories | IN SCOPE | `AUTH-FED`, `PKI-CRYPTO`, `DOC-BINARY`, `ENT-INT`, `DATA-ADV`, `DIST-OBS`; five tasks each. | task-set design; v2.6 freeze |
| Medium difficulty | IN SCOPE | Qualitative medium-difficulty standard, not a score or equality claim. | D013; task-set design |
| Four model/API conditions | IN SCOPE | M1–M4 exactly as frozen in api-model-set-1.4.0. | model configuration; v2.6 freeze |
| Three repetitions | IN SCOPE | R01–R03 per task-condition combination. | manifest; v2.6 freeze |
| 360 planned observations | IN SCOPE | Planned fresh v2.6 manifest size; eligible final denominator may be lower because failures/truncations are preserved but excluded. | v2.6 freeze; D031, D035 |
| Package/dependency references | IN SCOPE | Explicit direct references in supported syntax; vague prose is not automatically included. | D029; analysis specification §2; taxonomy |
| Exact-name registry resolution | IN SCOPE | Read-only npm registry evidence plus adjudication; 404 alone is insufficient for confirmed hallucination. | taxonomy; D036–D037; PIPE-04/05/05B scripts |
| Primary PHR/SHR | IN SCOPE | Strict confirmed package-name hallucination outcomes using D033/D037 units and eligibility. | D033, D035, D037; PIPE-08 |
| Secondary DFR/RDFR | IN SCOPE, SECONDARY/EXPLORATORY | Exact-name dependency-resolution failures; not hallucination rates or a full reliability measure. | D036; PIPE-10 |
| Risk assessment | IN SCOPE | Eligible confirmed package-related findings only, using Impact × Detectability. | risk protocol; D032; PIPE-06 |
| Grouped comparisons | IN SCOPE, CONDITIONAL | Descriptive / assumption-gated comparisons by condition, category, repetition, and condition × category; no guaranteed inference. | PIPE-09; progress log PIPE-09 |
| Spring Boot/Maven | OUT OF SCOPE | Superseded multi-ecosystem planning. | D001; final-paper notes reconciliation backlog |
| Java analysis / Maven AST extraction | OUT OF SCOPE | Only Node.js/npm direct-reference extraction is implemented; no Java/Maven parser/AST work. | D001; D029; final-paper notes |
| Developer surveys / expertise / human subjects | OUT OF SCOPE | No recruited participants, survey, or installation-probability evidence. | D008; final-paper notes |
| Autonomous workflow comparison | OUT OF SCOPE | Conditions are fixed stateless model/API conditions; no autonomy variable was evaluated. | `config/api_model_set_1.4.0.json` interaction protocol; D015 |
| Verification mediator | OUT OF SCOPE | No mediator/verification-intervention condition was introduced; validation is downstream measurement. | D015; report-generation protocol §4 |
| Package installation/execution | OUT OF SCOPE | Read-only validation only; generated code and packages are not executed. | taxonomy Scope Controls; risk protocol Safety and Scope |
| Transitive dependency analysis | OUT OF SCOPE | Direct recommendations only; no recursive analysis. | taxonomy Scope Controls; risk protocol Safety and Scope |
| Predictive ML-model training | OUT OF SCOPE | Risk model is deterministic rule based; no fitted weights, probabilities, or train/test split. | risk protocol; D032 |
| Dynamic mitigation experiments | OUT OF SCOPE | Mitigation is discussion/future-work material, not an evaluated intervention. | D009; final-paper notes |

## 10. Potential contributions

| Contribution type | Defensible contribution statement | Status |
|---|---|---|
| Methodological | A versioned Node.js/npm evidence chain that separates extraction, normalization, registry evidence, conservative classification/adjudication, primary confirmed-hallucination routing, and secondary exact-name dependency-resolution analysis. | VERIFIED as implemented methodology; final application is PENDING. |
| Dataset/experimental | A frozen, balanced v2.6 design of 30 dependency-intensive Node.js/npm tasks across six specialized categories, four fixed model/API conditions, and three repetitions (360 planned observations), with hashed tasks/prompts and a frozen manifest. | VERIFIED as design; final collected dataset completeness is PENDING. |
| Empirical | Final estimates of confirmed package-name hallucination, dependency-resolution failure patterns, group patterns, recurrence, and risk distributions. | **PENDING** — no final values, rankings, or distributions may be claimed. |
| Practical/software-supply-chain | An evidence-bounded way to distinguish confirmed invented package names from other exact-name failure modes and to prioritize eligible confirmed findings using an ordinal practical-risk rubric. It does not establish package safety, exploitation likelihood, or real-world compromise. | VERIFIED as methodology; practical empirical implications are **PENDING**. |

## 11. Old-draft reconciliation flags

| Do not retain this old-draft claim | Implemented alternative / required action | Evidence |
|---|---|---|
| Final Spring Boot/Maven experiment or multi-ecosystem comparison | Replace with Node.js/npm-only direct-dependency study; Spring/Maven is future work only. | D001; task JSONL; taxonomy |
| Developer-expertise survey, developer installation probabilities, or human-subject study | Remove/move to future work; no participants or survey occurred. | D008; final-paper notes reconciliation table |
| Workflow-autonomy variable or comparison | Replace with frozen model/API-condition comparison under one stateless, no-tools protocol. | D015; `config/api_model_set_1.4.0.json` |
| Verification mediator/intervention | Remove as performed methodology; downstream registry validation/adjudication measures outputs, not an experimental mediator. | D015; report-generation protocol §4 |
| 200–300 prompt assumption | Replace with exactly 30 final tasks. | task JSONL; task-set design; report-generation protocol §4 |
| 500–1000 dependency assumption | Remove; no final reference count is pre-assumed or reportable before final analysis. | report-generation protocol §4; current status |
| Java/Maven AST extraction | Replace with deterministic Node.js/npm explicit-syntax extraction; no AST parser. | D001; D029; final-paper notes |
| Old web/CLI tool set (ChatGPT Web, Gemini Web, Codex CLI, Antigravity CLI) | Replace with M1–M4 exact frozen model/API identities and providers in v2.6. | methodology update; D015/D031; `config/api_model_set_1.4.0.json` |
| Old 0–12 four-dimension risk model | Replace with `risk-model-1.0.0`: Impact × Detectability, range 1–20. | D032; risk protocol |
| Predictive 70/30 train-test design | Remove; no ML/predictive model or train/test split. | risk protocol; final-paper notes reconciliation table |
| Expert validation or Cohen's Kappa | Remove unless separate evidence is later produced; no evidence that such validation occurred. The protocol only calls for a documented subset double-check if risk scoring occurs. | final-paper notes reconciliation table; risk protocol Reproducibility and Review |
| Temporal holdout | Remove; no performed temporal holdout exists. | report-generation protocol §4; final-paper notes reconciliation table |
| Mitigation experiment | Remove as performed work; retain only literature-informed recommendations/future work if justified. | D009; final-paper notes |
| Final prevalence, model ranking, risk distribution, or final v2.6 conclusion | Do not retain any interim value; write `[FINAL RESULT PENDING]` until provenance-consistent final analysis exists. | current status; report-generation protocol §§13, 16; progress log final-analysis validation |

## 12. Claims-evidence candidates

These are proposals only; do **not** insert them into `claims_evidence_matrix.md` until researcher review.

| Suggested Claim ID | Section | Proposed claim | Exact evidence | Status |
|---|---|---|---|---|
| C1-01 | 1.2 Background / scope | The empirical study is limited to direct Node.js/npm dependency recommendations. | D001; `prompts/tasks/final_2.0.0.jsonl`; taxonomy Scope Controls. | VERIFIED |
| C1-02 | 1.8 Scope | The frozen v2.6 design comprises 30 tasks, six specialized categories, four fixed model/API conditions, and three repetitions, giving 360 planned observations. | v2.6 freeze JSON; manifest; task-set design; model config. | VERIFIED |
| C1-03 | 1.3 Research problem | Registry non-existence alone is insufficient to classify a reference as a confirmed package-name hallucination. | taxonomy §§Primary Outcome/Evidence; D037; PIPE-05B progress notes. | VERIFIED |
| C1-04 | 1.5 Aim / 1.6 Objectives | Primary outcomes are PHR and SHR for conservative confirmed package-name hallucinations; DFR/RDFR are secondary/exploratory exact-name dependency-resolution metrics. | D033, D036, D037; taxonomy Metric Boundaries; PIPE-08/10. | VERIFIED |
| C1-05 | 1.8 Scope | The study does not include Java/Maven, surveys/human participants, package execution, transitive dependency analysis, predictive ML training, or mitigation experiments. | D001, D008, D009, D015; taxonomy; risk protocol. | VERIFIED |
| C1-06 | 1.9 Contributions | The study applies a deterministic Impact × Detectability risk rubric only after eligible package-related hallucination confirmation. | risk protocol; D032; PIPE-06 schema/script. | VERIFIED |
| C1-07 | 1.4 Research gap | Existing approved literature leaves a need for the precise bounded Node.js/npm evidence-chain and risk framing used here. | Approved-reference list plus baseline dissertation citation reconciliation. | PENDING — **[DRAFT-LITERATURE-RECONCILIATION REQUIRED]** |
| C1-08 | 1.9 Contributions | The final study found a particular prevalence, model/category difference, or risk distribution. | Future provenance-consistent final v2.6 result artifacts only. | PENDING |

## 13. Open issues requiring researcher decision

1. Select a final title from the candidates (or approve a revised conservative title).
2. Approve whether RQ3 should retain the phrase “vary” or use the more cautious “descriptively distributed and, where estimable, compared.”
3. Approve the RQ4 boundary: risk applies to eligible **confirmed package-related hallucination findings**, not every dependency reliability failure.
4. Complete **[DRAFT-LITERATURE-RECONCILIATION REQUIRED]** against the baseline dissertation and approved references before making any literature novelty/gap statement in Chapter 1.
5. Decide whether “medium difficulty” should remain a Chapter 1 scope descriptor. It is supported by D013, but should be presented as a qualitative task-design standard rather than an empirically validated difficulty measurement.
6. Before final Chapter 1 claims are converted to prose, await v2.6 collection completion and final provenance-consistent analysis. Empirical claims must remain `[FINAL RESULT PENDING]` until then.

## 14. Evidence-file index

| Evidence file | Audit use |
|---|---|
| `AGENTS.md` | Integrity, scope, reporting, and worktree controls. |
| `docs/report_generation_protocol.md` | Chapter 1 workflow, old-draft reconciliation, claims-evidence control. |
| `docs/current_research_status.md` | Current v2.6 collection/final-analysis status. |
| `docs/research_progress_log.md` | Implemented pipeline and synthetic-validation milestones; no-final-results controls. |
| `docs/final_paper_notes.md` | Draft-reconciliation and reporting boundaries, subordinated to frozen evidence. |
| `docs/decision_log.md` | Controlling D001, D008, D009, D013, D015, D031–D037 decisions. |
| `docs/analysis_specification_v1.0.md` | Analysis units and historical/superseded wording markers. |
| `docs/package_hallucination_taxonomy.md` | Primary/secondary classification and metric boundaries. |
| `docs/risk_assessment_protocol.md` | Controlling `risk-model-1.0.0`. |
| `docs/references/approved_references.md` | Approved-citation boundary, including Spracklen et al. (2025). |
| `docs/final_report_support/claims_evidence_matrix.md` | Existing matrix structure and permitted statuses; not modified. |
| `docs/methodology_update_2026-09-16.md` | API redesign and task-set transition context. |
| `docs/task_set_v2_design.md` | Final task categories, structure, and bounded task design. |
| `prompts/tasks/final_2.0.0.jsonl` | Frozen 30 task records and Node.js/npm fields. |
| `prompts/prompt_template_v2.6.0.md` and `data/generated_prompts/v2.6.0/` | Frozen common template and rendered-prompt provenance. |
| `config/api_model_set_1.4.0.json` | Exact v2.6 model/API conditions and interaction protocol. |
| `config/experiment_freeze_v2.6.0.json` and `docs/experiment_freeze_v2.6.0.md` | v2.6 fresh-design, hashes, counts, model pins, and protocol. |
| `manifests/api_final_v2.6.0_manifest.csv` | 360 planned row matrix and per-run identities. |
| `scripts/build_analysis_dataset.py`, `scripts/calculate_primary_metrics.py`, `scripts/adjudicate_review_required_packages.py`, `scripts/calculate_dependency_reliability_metrics.py`, `scripts/analyze_group_comparisons.py`, `scripts/score_risk_findings.py` | Implemented analysis/risk pathways only; no final metrics run for this audit. |
| `schemas/risk_finding_pipe06_v1.schema.json`, `schemas/package_response_analysis_pipe07_v1.schema.json`, `schemas/response_level_analysis_pipe07_v1.schema.json` | Implemented analysis-record and risk schema boundaries. |
