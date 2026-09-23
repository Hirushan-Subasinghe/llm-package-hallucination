# Chapter 1 Draft Reconciliation — CHAPTER-1-DRAFT-RECONCILIATION-01

**Audit date:** 2026-09-23
**Purpose:** Reconcile the baseline dissertation's existing Chapter 1 with the implemented final v2.6 study, without drafting final Chapter 1 prose, modifying frozen evidence, calculating results, or changing the dissertation title.

## 1. Reconciliation basis

The source-of-truth order applied in this reconciliation is: (1) frozen v2.6 inputs, manifests, configuration, implementation, and verified outputs; (2) `docs/current_research_status.md`; (3) `docs/research_progress_log.md`; (4) `docs/final_paper_notes.md`; (5) verified current implementation; (6) `docs/source_documents/IM2021101.pdf`; then (7) older plans.

The baseline PDF was directly inspected. Its present Chapter 1 occupies printed pages 1–3 (PDF pages 10–12) and contains: **1.1 Background**, **1.2 Problem Statement**, **1.3 Research Objectives and Questions**, and **1.4 Document Structure**. It frames the work as a systematic literature review (SLR), with root-cause, slopsquatting/agentic-autonomy, and mitigation questions. It does not describe the implemented final empirical Node.js/npm study.

`docs/final_report_support/chapter1_evidence_audit.md` remains the immediate factual foundation for this document. The final v2.6 collection is in progress and final analysis has not run; all final empirical answers, prevalence values, comparisons, and risk distributions remain `[FINAL RESULT PENDING]`.

Milestone documentation decision: progress-log update needed **NO**; final-paper note needed **NO**; draft reconciliation needed **YES** (completed by this document before any Chapter 1 rewrite).

## 2. Research title preservation

The research title is preserved exactly, without editorial assessment or alteration:

> **AI Hallucination Attack Surface: A Risk Assessment of Fake APIs and Libraries in AI-Generated Code**

Source: `docs/source_documents/IM2021101.pdf`, title page (PDF page 1).

The fixed title is broader than the final empirical method. That mismatch must be managed through scope, delimitations, limitations, and reconciliation notes—not by changing the title. Chapter 1 must make clear that the implemented evidence concerns direct Node.js/npm dependency references, conservative confirmed package-name hallucination, secondary exact-name dependency-resolution failures, and the implemented rule-based practical-risk assessment. It must not imply that every kind of fake API/library, every ecosystem, autonomous agent behaviour, package compromise, or mitigation technique was evaluated.

## 3. Verified Chapter 1 factual foundation

| Foundation item | Verified implemented fact | Exact evidence |
|---|---|---|
| Ecosystem | Direct **Node.js/npm** dependency recommendations only. | `docs/decision_log.md` D001; `prompts/tasks/final_2.0.0.jsonl`; `docs/package_hallucination_taxonomy.md` (Scope Controls) |
| Tasks and task metadata | **30** frozen `final-2.0.0` tasks; task-set metadata/designation is **medium difficulty** under a qualitative rubric only. It is not externally validated difficulty measurement. | `prompts/tasks/final_2.0.0.jsonl`; `docs/task_set_v2_design.md`; `docs/decision_log.md` D013 |
| Categories | **Six** specialized categories: `AUTH-FED`, `PKI-CRYPTO`, `DOC-BINARY`, `ENT-INT`, `DATA-ADV`, and `DIST-OBS`; five tasks per category. | `docs/task_set_v2_design.md`; `config/experiment_freeze_v2.6.0.json` |
| Conditions | **Four frozen model/API conditions**: M1 `cohere/north-mini-code:free` via OpenRouter/cohere; M2 `qwen/qwen3.8-27b` via OpenRouter/darkbloom; M3 `openai/gpt-oss-120b` via Groq; M4 `nvidia/nemotron-3-ultra-550b-a55b:free` via OpenRouter/nvidia. | `config/api_model_set_1.4.0.json`; `config/experiment_freeze_v2.6.0.json`; `docs/experiment_freeze_v2.6.0.md` |
| Repetitions and planned observations | **Three** independent repetitions per task-condition combination; **360 planned v2.6 observations**. This is a planned manifest count, not a guaranteed final metric denominator. | `manifests/api_final_v2.6.0_manifest.csv`; `config/experiment_freeze_v2.6.0.json`; `docs/decision_log.md` D031 |
| Measurement focus | Explicit generated direct package/dependency references, normalized before npm registry evidence and conservative classification/adjudication. A registry `not_found` is not by itself a confirmed hallucination. | `docs/decision_log.md` D029, D033–D037; `docs/package_hallucination_taxonomy.md`; `scripts/adjudicate_review_required_packages.py` |
| Primary outcomes | PHR and SHR for **confirmed npm package-name hallucination**. PHR uses one unique `(run_id, normalized_package)` per eligible response; SHR uses eligible completed, non-truncated responses. | `docs/decision_log.md` D033, D035, D037; `scripts/build_analysis_dataset.py`; `scripts/calculate_primary_metrics.py` |
| Secondary/exploratory outcomes | DFR and RDFR for exact-name npm dependency-resolution failures under D036; they are not hallucination rates and do not measure all dependency unreliability. | `docs/decision_log.md` D036; `scripts/calculate_dependency_reliability_metrics.py`; taxonomy Metric Boundaries |
| Grouped analysis | Grouping by model condition, functional category, repetition, and model-condition × category; descriptive analysis and assumption-gated statistical comparison only where estimable. | `scripts/analyze_group_comparisons.py`; `docs/research_progress_log.md` (PIPE-09) |
| Practical risk | Post-classification `risk-model-1.0.0`: Impact (1–5) × Detectability (1–4), with non-scored security-sensitive context. It is rule based, ordinal, and not predictive. | `docs/risk_assessment_protocol.md`; `docs/decision_log.md` D032; `scripts/score_risk_findings.py` |
| Unperformed components | No human participants/developer survey or expertise variable; no Java/Maven/Spring Boot experiment; no workflow-autonomy or verification-mediator experiment; no package installation/execution; no transitive analysis; no predictive ML, 70/30 train/test model, mitigation experiment, Cohen's Kappa, expert validation, or temporal holdout evidenced as performed. | `docs/decision_log.md` D001, D008, D009, D015, D032; `docs/final_paper_notes.md` (Draft reconciliation backlog); taxonomy Scope Controls; risk protocol Safety and Scope |

## 4. Final proposed research aim

**Recommended wording:**

> **To assess confirmed npm package-name hallucinations and secondary exact-name dependency-reference reliability failures in LLM-generated Node.js coding responses across the frozen experimental conditions and functional task categories, and to assess eligible confirmed findings using the implemented practical-risk framework.**

This wording is grammatically sound and preserves the requested substantive boundary. “Eligible confirmed findings” deliberately does not expand risk scoring to every dependency anomaly. It does not claim that final assessment results already exist.

Supporting evidence: `docs/final_report_support/chapter1_evidence_audit.md`; `docs/decision_log.md` D033, D036, D037; `docs/risk_assessment_protocol.md`; `config/experiment_freeze_v2.6.0.json`.

## 5. Final proposed objectives

| ID | Final recommended wording | Supporting implementation/evidence | Status | Final achievement |
|---|---|---|---|---|
| O1 | **Measure the prevalence of confirmed npm package-name hallucinations in eligible LLM-generated Node.js coding responses using the primary PHR and SHR measures.** | D033, D035, D037; taxonomy Metric Boundaries; PIPE-07 and `scripts/calculate_primary_metrics.py`. | SUPPORTED | **PENDING** final v2.6 collection and provenance-consistent analysis. |
| O2 | **Characterize secondary/exploratory exact-name npm dependency-resolution failures using the implemented DFR/RDFR framework and adjudication taxonomy.** | D036; PIPE-05B; `scripts/calculate_dependency_reliability_metrics.py`; taxonomy. | SUPPORTED | **PENDING** final v2.6 adjudication and analysis. |
| O3 | **Examine how primary confirmed package-name hallucination outcomes and secondary/exploratory dependency-reliability outcomes are descriptively distributed and, where estimable, compared across the evaluated model conditions and functional task categories.** | Frozen stratified manifest; PIPE-09; D036 grouped-descriptive provision. | PARTIALLY SUPPORTED | **PENDING**; comparison is conditional on eligible group sizes/events and does not promise significance. |
| O4 | **Assess the practical risk of eligible confirmed package-hallucination findings using the implemented Impact × Detectability risk model.** | `docs/risk_assessment_protocol.md`; D032; PIPE-06 script/schema. | SUPPORTED | **PENDING** final eligible findings and completed risk assessments. |

O2 must always retain “secondary/exploratory”; DFR/RDFR must never be called primary hallucination measures. O3 avoids a guarantee of inferential results. O4 does not score unconfirmed, unresolved, valid, local/self-reference, or ordinary implementation-error outcomes.

## 6. Final proposed research questions

| RQ | Recommended formulation | Status | Exact evidence | Implemented metric/pipeline | Current final answer | Wording correction required |
|---|---|---|---|---|---|---|
| RQ1 | **What is the prevalence of confirmed npm package-name hallucinations in LLM-generated Node.js coding responses under the evaluated experimental conditions?** | SUPPORTED | D033, D035, D037; taxonomy; v2.6 freeze/manifest. | PIPE-03/04/05/05B → PIPE-07 → PIPE-08 PHR/SHR. | **PENDING** | None in the RQ. Methods must define “confirmed,” eligible, completed, and non-truncated; registry 404 is not itself confirmation. |
| RQ2 | **What secondary exact-name npm dependency-resolution failure patterns are observed in the generated responses under the implemented adjudication framework?** | SUPPORTED | D036; taxonomy; PIPE-05B and PIPE-10. | PIPE-04/05 → PIPE-05B → PIPE-10 DFR/RDFR and outcome breakdowns. | **PENDING** | Retain “secondary” and “exact-name”; do not call DFR/RDFR hallucination rates or imply all reliability failures are captured. |
| RQ3 | **How are confirmed package-name hallucination and secondary dependency-reliability outcomes descriptively distributed and, where estimable, compared across the evaluated model conditions and functional task categories?** | PARTIALLY SUPPORTED | v2.6 stratified manifest; PIPE-09; D036. | PIPE-09 by `model_condition_id` and `category`; secondary grouped output as appropriate. | **PENDING** | Replace unqualified “vary” with the recommended wording to avoid promising significant/inferential differences. |
| RQ4 | **What practical risk levels are assigned to eligible confirmed package-hallucination findings under the implemented risk-assessment framework?** | PARTIALLY SUPPORTED | risk protocol; D032; PIPE-06. | PIPE-06, applying Impact × Detectability after confirmation. | **PENDING** | None beyond retaining “eligible confirmed package-hallucination findings”; do not imply every dependency anomaly receives a score. |

## 7. Old Chapter 1 reconciliation matrix

The baseline's Chapter 1 material is identified by printed page and PDF page where directly inspected. Items that appear principally in its Chapter 2/3 are included because they shape what must not migrate into the final Chapter 1 as performed research.

| Existing section / claim | Old draft meaning | Implemented study | Action | Final-Chapter treatment | Evidence |
|---|---|---|---|---|---|
| A. 1.1 general LLM-assisted software-development background | LLMs/coding assistants and autonomous agents are changing development; includes an uncited “citation needed” adoption claim. | The study concerns LLM-generated Node.js coding responses, but does not measure adoption, vibe coding, or autonomy. | KEEP WITH REVISION | Retain a short, cited introduction to AI-assisted code generation; remove the uncited adoption statistic/claim and do not make autonomy a study variable. | Baseline Ch.1 p.1/PDF p.10; approved refs include Gao et al. (2025), Woesle et al. (2025), Wang et al. (2025). **[LITERATURE CLAIM VERIFICATION REQUIRED]** |
| B. 1.2 general code-hallucination background | Defines hallucination broadly as fluent but factually incorrect output. | The implementation only measures package-specific constructs, chiefly confirmed package-name hallucination. | KEEP WITH REVISION | Use broad code hallucination only as background; transition immediately to the operational npm package-name definition. Do not claim general code-error prevalence. | Baseline Ch.1 pp.1–2/PDF pp.10–11; taxonomy Primary Outcome; approved refs Agarwal et al. (2024), Gao et al. (2025). **[LITERATURE CLAIM VERIFICATION REQUIRED]** |
| C. 1.2 package-hallucination definition/background | Treats nonexistent libraries, modules, and API endpoints together as “package hallucination.” | Primary construct excludes API/capability/version errors; secondary DFR/RDFR is a distinct exact-name-resolution construct. | REWRITE | Define a confirmed package-name hallucination conservatively; separately describe secondary reliability failures. Explicitly say npm 404 is not sufficient. | taxonomy §§Primary Outcome/Metric Boundaries; D033, D036, D037 |
| D. Registry discussion (baseline 1.1 and Chapter 2) | npm, PyPI, and Maven Central discussed as common registries and possible comparative settings. | Empirical ecosystem is Node.js/npm only. | KEEP WITH REVISION | npm is experimental context. PyPI/Maven may appear only as literature/background examples, with explicit statement that they are outside the final experiment. | Baseline Ch.1 p.1/PDF p.10; D001; task JSONL. **[LITERATURE CLAIM VERIFICATION REQUIRED]** for registry-characterization claims. |
| E. Typosquatting background | Traditional human naming-error attack context. | Not measured, simulated, or used as a classification shortcut. | KEEP WITH REVISION | Retain as brief security context, carefully distinguished from confirmed hallucination and from this study's non-registration approach. | Baseline Ch.1 p.1/PDF p.10; approved refs Ladisa et al. (2023), Ohm and Stuke (2023), Al-Zofi (2025). **[LITERATURE CLAIM VERIFICATION REQUIRED]** |
| F. Dependency-confusion background | Private/public namespace-resolution threat presented alongside package hallucination. | Not experimentally evaluated; namespace confusion may be an adjudication outcome but is never primary confirmation. | KEEP WITH REVISION | Keep only literature context. Explain that a detected namespace-confusion outcome is not automatically a confirmed package-name hallucination. | Baseline Ch.1 p.1/PDF p.10; D036–D037; taxonomy. **[LITERATURE CLAIM VERIFICATION REQUIRED]** |
| G. Slopsquatting background | Presents adversarial pre-registration/weaponization as the central threat. | No name registration, package claiming, payload creation, installation, execution, or attack demonstration occurred. | MOVE TO CHAPTER 2 | Treat as literature/security context and a possible practical implication only; never present slopsquatting exploitation as performed research or a demonstrated outcome. | Baseline Ch.1 pp.2/PDF p.11; taxonomy Scope Controls; risk protocol Safety and Scope. **[LITERATURE CLAIM VERIFICATION REQUIRED]** |
| H. Software supply-chain risk framing | Links hallucinated dependencies to broad compromise claims and historical incidents. | Rule-based practical-risk assessment is evidence bounded; it does not estimate compromise, loss, malware, or package trust. | KEEP WITH REVISION | Retain cautious supply-chain relevance; state the measured practical-risk boundary and avoid claims of actual compromise. Historical incident claims belong in Chapter 2 unless directly needed and verified. | Baseline Ch.1 p.1/PDF p.10; risk protocol; D032. **[LITERATURE CLAIM VERIFICATION REQUIRED]** |
| I. Autonomous-agent / confused-deputy discussion | Treats agent execution privileges as amplifying the risk. | The conditions are stateless, one-user-message, no tools/browsing/retrieval/execution; no autonomy comparison. | MOVE TO CHAPTER 2 | Retain only literature context if supported; explicitly exclude autonomous execution depth from empirical scope/risk model. | Baseline Ch.1 p.2/PDF p.11; model config `interaction_protocol`; risk protocol Safety and Scope. **[LITERATURE CLAIM VERIFICATION REQUIRED]** |
| J. Existing 1.2 problem statement | Frames a general, highly exploitable supply-chain vulnerability and assumes adversarial monitoring/registration. | Study measures conservative package-name hallucination and secondary exact-name failure, not attacker activity. | REWRITE | Use the verified research problem from the evidence audit: distinguish confirmation from broader exact-name failures and do not assert observed exploitation. | Baseline Ch.1 pp.1–2/PDF pp.10–11; chapter1 evidence audit §§4–5; D036–D037 |
| K. Existing research-gap statement | Implied gap is broad SLR coverage of hallucination, exploitability, agentic autonomy, and mitigations. | No literature-wide novelty conclusion has been verified; implemented contribution is a bounded Node.js/npm empirical evidence chain. | REWRITE | State only the implementation-facing gap. Mark any claim that prior research has not done this **[LITERATURE CLAIM VERIFICATION REQUIRED]**. | chapter1 evidence audit §5; approved references list; baseline Ch.2 research-gap content |
| L. Existing aim/objective framing | Aim is to systematically investigate mechanisms, exploitability, and defensive strategies. | Final aim/objectives concern prevalence, secondary reliability failures, grouped comparisons, and practical risk. | REWRITE | Replace with the four verified objectives in §5 of this document. | Baseline Ch.1 p.2/PDF p.11; D033, D036, D032; PIPE-08/09/10/06 |
| M. Existing research questions | RQ1 root causes/prevalence across ecosystems; RQ2 slopsquatting/autonomy; RQ3 mitigation strategies. | Four empirical RQs are package-name prevalence, secondary failure patterns, conditional grouped comparisons, and practical risk. | REWRITE | Replace entirely with the RQs in §6. | Baseline Ch.1 pp.2–3/PDF pp.11–12; chapter1 evidence audit §8 |
| N. Existing SLR framing | Baseline says the study is a systematic literature review and Chapter 2 describes search/inclusion/thematic synthesis. | Final dissertation is an empirical Node.js/npm experiment; literature review remains contextual but is not the final empirical design. | REMOVE | Remove SLR as the Chapter 1 research design and remove PRISMA/search-method claims unless independently retained as a separate, verifiable literature-review component. Chapter 2 may review approved literature. | Baseline Ch.1 pp.2–3/PDF pp.11–12 and Ch.2; report-generation protocol §§7–9; D015 |
| O. Existing 1.4 document structure | Five-section SLR paper: review methodology, thematic synthesis, SLR findings, conclusion. | Final dissertation has six empirical-report chapters with the specified Chapter 1 subsections. | REWRITE | Replace with a concise six-chapter dissertation map consistent with the report-generation protocol. | Baseline Ch.1 p.3/PDF p.12; report-generation protocol §18 |

## 8. Final Chapter 1 structure

| Subsection | Purpose | Existing material that can be reused | Material requiring revision | Material requiring new writing | Repository evidence needed | Approved literature likely relevant | Result-dependent wording |
|---|---|---|---|---|---|---|---|
| 1.1 Chapter Introduction | Orient the reader to the empirical dissertation and chapter. | Short opening about LLM-generated code and package-reference concern. | Remove SLR identity and autonomy/mitigation claims as study activities. | State chapter purpose and empirical focus without results. | report protocol §18; chapter1 evidence audit. | Gao et al. (2025); Woesle et al. (2025). **[LITERATURE CLAIM VERIFICATION REQUIRED]** | No findings; do not forecast prevalence. |
| 1.2 Background of the Study | Establish relevant LLM, package-hallucination, and supply-chain context. | General LLM/code-generation, package-registry, typosquatting/dependency-confusion background. | Constrain language from cross-ecosystem/agentic compromise to Node.js/npm relevance; distinguish slopsquatting from the study. | Explain direct package-reference scope and conservative classification boundary. | taxonomy; D001; D029; risk protocol. | Spracklen et al. (2025); Ladisa et al. (2023); Ohm and Stuke (2023); Wang et al. (2025); Al-Zofi (2025). **[LITERATURE CLAIM VERIFICATION REQUIRED]** | Do not say a vulnerability was exploited or an attack observed. |
| 1.3 Research Problem | Specify the measurable problem. | Broad problem transition from package recommendation to supply-chain relevance. | Replace broad fake APIs/libraries and adversarial exploitation claims. | State distinction: confirmed package-name hallucination versus secondary exact-name dependency-resolution failure; 404 is not confirmation. | taxonomy; D033, D036, D037. | Spracklen et al. (2025) likely relevant. **[LITERATURE CLAIM VERIFICATION REQUIRED]** | No prevalence, number of findings, or model differences. |
| 1.4 Research Gap | Motivate bounded empirical study without unsupported novelty. | General motivation that package hallucination/security needs study. | Remove unverified “absence of research” and SLR-gap claims. | State implementation-facing gap and marked literature reconciliation condition. | chapter1 evidence audit §5; approved-reference list. | Spracklen et al. (2025); Wang et al. (2025); Williams et al. (2025). **[LITERATURE CLAIM VERIFICATION REQUIRED]** | Do not claim this is the first study or that prior methods are absent. |
| 1.5 Research Aim | State one bounded purpose. | None suitable verbatim. | Replace SLR aim. | Use §4 aim exactly after researcher approval. | D032–D037; risk protocol; v2.6 freeze. | None required for a study aim. | None. |
| 1.6 Research Objectives | Operationalize the aim. | None suitable verbatim. | Replace root-cause/exploitability/mitigation objectives. | Use O1–O4 from §5. | D033, D036; PIPE-06/08/09/10. | None required for objectives. | Objective attainment is `[FINAL RESULT PENDING]`. |
| 1.7 Research Questions | Define answerable final questions. | None suitable verbatim. | Replace baseline RQ1–RQ3. | Use RQ1–RQ4 from §6. | D032–D037; taxonomy; analysis scripts. | None required for RQ wording. | Answers are `[FINAL RESULT PENDING]`. |
| 1.8 Scope and Delimitations | Bound empirical claims, inputs, analysis, and exclusions. | Brief registry/supply-chain context only. | Remove multi-ecosystem, autonomous, human, and mitigation scope implications. | Use verified in/out-of-scope statement in §9. | D001, D008, D009, D013, D015, D032–D037; v2.6 freeze. | None required for method scope. | Note 360 is planned; no completion/value claims. |
| 1.9 Research Contributions | State verified design/pipeline contributions and reserve empirical contribution. | General practical significance. | Remove claims that an attack model, mitigation system, or cross-ecosystem assessment was delivered. | Use four-part contribution statement in §10. | frozen design; taxonomy; risk protocol; pipeline scripts. | Literature comparison only after verification. | Empirical contribution is `[FINAL RESULT PENDING]`. |
| 1.10 Dissertation Structure | Map the final dissertation. | The idea of a reader map. | Replace the five-part SLR-paper map. | Describe Chapters 1–6 according to report protocol. | report protocol §18. | None. | No results. |
| 1.11 Chapter Summary | Close without repeating claims. | None. | Not present in baseline. | New concise summary of framing, aim, objectives, RQs, and scope. | Approved Chapter 1 plan. | None. | No findings. |

## 9. Scope and delimitations

**Verified final scope statement:** The empirical dissertation evaluates direct package/dependency references in LLM-generated Node.js coding responses. It uses 30 frozen `final-2.0.0` tasks across six functional categories, designated medium difficulty by a qualitative task-set rubric, four frozen model/API conditions, and three independent repetitions, producing a 360-observation v2.6 planned manifest. It normalizes explicit package references, collects read-only npm registry evidence, applies conservative adjudication, reports primary PHR/SHR and secondary/exploratory DFR/RDFR, supports grouped model-condition/category comparisons where estimable, and applies the versioned practical-risk framework to eligible confirmed package-hallucination findings. “Medium difficulty” is task-set metadata/designation only; no external difficulty validation is claimed.

| IN SCOPE | OUT OF SCOPE | Evidence |
|---|---|---|
| Node.js/npm direct references; normalization; read-only npm registry evidence; conservative adjudication | Spring Boot/Maven final experiment; Java analysis; PyPI as experimental ecosystem | D001; D029; taxonomy; task JSONL |
| 30 tasks; six categories; qualitative medium-difficulty designation; four frozen model/API conditions; three repetitions; 360 planned observations | 200–300 prompts; pre-assumed 500–1000 dependencies; other/future model sets | D013; task-set design; v2.6 freeze; model configuration; manifest |
| PHR/SHR primary confirmed package-name outcomes | A rule that npm 404 automatically means confirmed hallucination | D033, D037; taxonomy |
| DFR/RDFR exact-name failure analysis, explicitly secondary/exploratory | DFR/RDFR as hallucination rates or complete dependency reliability | D036; PIPE-10; taxonomy |
| Descriptive and, where estimable, statistical group comparisons | Guaranteed statistical significance, rankings, or model “best/worst” claims | PIPE-09; progress log |
| Post-classification practical risk assessment | Predictive ML; fitted weights; 70/30 train/test modelling; old 0–12 risk model | D032; risk protocol |
| Immutable response evidence and downstream annotations | Package installation/execution; dynamic execution of generated dependencies; active package claiming/registration; transitive dependency analysis | taxonomy Scope Controls; risk protocol Safety and Scope |
| Generated-artifact study | Developer surveys; developer-expertise variable; human-participant study; workflow-autonomy comparison; verification mediator | D008; D015; model configuration interaction protocol |
| Literature-informed discussion/recommendations where supported | Mitigation experiment; expert validation, Cohen's Kappa, or temporal holdout unless new repository evidence proves performance | D009; final-paper notes reconciliation backlog; report protocol §4 |

## 10. Potential contributions

| Contribution type | Defensible Chapter 1 framing | Status |
|---|---|---|
| 1. Methodological | A reproducible Node.js/npm pipeline that separates immutable response preservation, explicit-reference extraction/normalization, registry evidence, conservative classification/adjudication, D037 primary routing, and D036 secondary exact-name failure analysis. | VERIFIED as implemented methodology; final application to completed v2.6 data is PENDING. |
| 2. Dataset/experimental | A frozen, balanced v2.6 design: 30 dependency-intensive Node.js/npm tasks in six specialized categories, four exact model/API conditions, three repetitions, hashed prompts, and 360 planned observations. | VERIFIED as design; final completed dataset is PENDING. |
| 3. Empirical | Evidence about final prevalence, outcome patterns, grouped differences, recurrence, and risk distributions. | **PENDING**. Do not state rates, differences, model ranking, significance, or risk distributions. |
| 4. Practical/software-supply-chain | An evidence-bounded distinction between confirmed package-name hallucination and other exact-name resolution failures, plus ordinal prioritization of eligible confirmed findings. It does not claim package safety, maliciousness, compromise probability, installation probability, or real-world exploitation. | VERIFIED as methodological framing; evidence-based practical implications are PENDING. |

## 11. Literature-claim verification requirements

No web search was used. Only the approved-reference list was consulted. Its entries were extracted from the baseline bibliography, while external bibliographic verification remains unperformed. An entry may be named below only because its title/topic appears relevant; this is not proof that it supports a proposed sentence.

| Proposed Chapter 1 literature claim area | Existing material / approved references that appear relevant | Reconciliation rule |
|---|---|---|
| Prior package-hallucination prevalence or definitions | Baseline Ch.2 discussion; Spracklen et al. (2025); Agarwal et al. (2024); Zhao et al. (2025). | **[LITERATURE CLAIM VERIFICATION REQUIRED]** Confirm each definition, sample, ecosystem, and value from the cited source before use. Never import a baseline percentage unverified. |
| Slopsquatting | Baseline Ch.1 pp.1–2 and Ch.2; Al-Zofi (2025). | **[LITERATURE CLAIM VERIFICATION REQUIRED]** Keep as security context only; do not describe attack registration/weaponization as performed. |
| Dependency confusion and typosquatting | Baseline Ch.1 p.1; Ladisa et al. (2023); Ohm and Stuke (2023); Duan et al. (2020). | **[LITERATURE CLAIM VERIFICATION REQUIRED]** Verify technical definitions and ensure the text distinguishes them from this study's primary classification. |
| Software supply-chain attacks/risk | Baseline Ch.1 p.1; Ladisa et al. (2023); Wang et al. (2025); Williams et al. (2025). | **[LITERATURE CLAIM VERIFICATION REQUIRED]** Use cautious contextual claims; do not infer actual compromise from an experiment finding. |
| Autonomous-agent / confused-deputy risks | Baseline Ch.1 p.2; Gandhi (2026); Qu et al. (2026); Tripathi et al. (2025). | **[LITERATURE CLAIM VERIFICATION REQUIRED]** Literature context only; the final empirical study has no tool exposure or autonomous-execution variable. |
| Mitigation limitations or approaches | Baseline Ch.1 p.3 and Ch.2; Jain et al. (2025); AlSobeh et al. (2025); Zhuo et al. (2025); Yang et al. (2026). | **[LITERATURE CLAIM VERIFICATION REQUIRED]** Literature/future-work context only; no intervention effectiveness claim from this study. |
| Research novelty/gap | Baseline Ch.2 gap material; approved references above. | **[LITERATURE CLAIM VERIFICATION REQUIRED]** Do not use “first,” “unexplored,” “lacks,” or comparative novelty claims until baseline text and source support are reconciled. |

## 12. Claims-evidence candidates

These are candidates only. `docs/final_report_support/claims_evidence_matrix.md` was not edited.

| Suggested Claim ID | Dissertation section | Claim | Exact repository evidence | Literature citation if applicable | Status |
|---|---|---|---|---|---|
| C1R-01 | 1.8 Scope | The empirical study is limited to direct Node.js/npm dependency recommendations. | D001; task JSONL; taxonomy Scope Controls. | None required for methodology scope. | VERIFIED |
| C1R-02 | 1.8 Scope | The frozen v2.6 task design contains 30 tasks in six functional categories. | task JSONL; task-set design; v2.6 freeze. | None. | VERIFIED |
| C1R-03 | 1.8 Scope | The task set is designated medium difficulty using a qualitative rubric, not an externally validated difficulty measure. | D013; task-set design. | None. | VERIFIED |
| C1R-04 | 1.8 Scope | Four frozen model/API conditions and three repetitions produce 360 planned v2.6 observations. | model config; v2.6 freeze; manifest. | None. | VERIFIED |
| C1R-05 | 1.5–1.7 | PHR/SHR are primary outcomes for confirmed package-name hallucination; DFR/RDFR are secondary/exploratory exact-name failure metrics. | D033, D036, D037; taxonomy; PIPE-08/10. | None. | VERIFIED |
| C1R-06 | 1.9 Contributions / 1.8 Scope | The risk framework scores eligible confirmed findings after classification using Impact × Detectability; it is not predictive. | risk protocol; D032; PIPE-06. | None. | VERIFIED |
| C1R-07 | 1.8 Delimitations | The final experiment contains no human-subject/developer survey component and no Java/Maven final experiment. | D001; D008; final-paper notes. | None. | VERIFIED |
| C1R-08 | 1.9 Contributions | The final study observed a particular prevalence, risk distribution, group difference, or model ranking. | Future provenance-consistent final v2.6 results only. | Any literature comparison only after verified final result. | PENDING |

## 13. Statements prohibited from final Chapter 1

The following must not appear as descriptions of performed final research:

- The final study evaluated Node.js **and** Java/Maven, Spring Boot/Maven, PyPI, or multiple ecosystems.
- A developer survey, developer-expertise measurement, human-participant study, or installation-probability study was conducted.
- Autonomous versus autocomplete workflows, agent autonomy, or a verification mediator were experimentally compared.
- The final sample comprised 200–300 prompts or a pre-assumed 500–1000 dependency sample.
- Java/Maven AST extraction, Maven Central validation, or Java code analysis was performed.
- The final model configuration was an old GPT-4/GPT-3.5/Copilot/Gemini/Claude/tool set rather than frozen v2.6 M1–M4 identities/providers.
- The old 0–12 four-factor risk model was the performed final method.
- A 70/30 predictive ML train/test design, Cohen's Kappa calculation, expert validation, or temporal holdout analysis was performed without new exact evidence.
- A mitigation experiment, RAG system, knowledge graph, fine-tuning, registry reservation, malicious package registration, or attack demonstration was performed.
- An npm 404/not-found result automatically means a confirmed package-name hallucination.
- DFR or RDFR is a hallucination rate, or a complete measure of dependency reliability.
- A package finding shows package safety, maliciousness, exploitability, installation, compromise, or loss without evidence beyond the implemented scope.
- Interim v2.6 values, checkpoint observations, synthetic-fixture tests, or infrastructure readiness are final research findings.

## 14. Open issues

1. Approve the final aim, O1–O4, and RQ1–RQ4 wording—especially the conditional/descriptive wording in O3/RQ3 and the confirmation eligibility boundary in O4/RQ4.
2. Reconcile and verify the baseline literature claims against approved sources before retaining any claim about prevalence, slopsquatting, registry characteristics, autonomy, mitigation effectiveness, or research novelty.
3. Decide which background material on typosquatting, dependency confusion, slopsquatting, and autonomous-agent risk should remain briefly in Chapter 1 versus move to Chapter 2 after citation verification.
4. Approve contribution wording after final v2.6 results exist; empirical contributions cannot yet be stated.
5. Decide the exact final dissertation chapter map wording once the full final report structure is confirmed. The title is not an open issue and must remain unchanged.

## 15. Evidence index

| Evidence file | Reconciliation use |
|---|---|
| `AGENTS.md` | Study integrity, source priority, frozen-data and report-writing controls. |
| `docs/report_generation_protocol.md` | Chapter 1 workflow, baseline policy, reconciliation requirement, final chapter structure. |
| `docs/final_report_support/chapter1_evidence_audit.md` | Prior verified foundation, scope, objectives, RQs, contributions, and reconciliation flags. |
| `docs/source_documents/IM2021101.pdf` | Directly inspected baseline title page and Chapter 1 (PDF pp. 1, 10–12; printed pp. 1–3). |
| `docs/references/approved_references.md` | Approved-reference boundary; baseline-reference extraction status. |
| `docs/current_research_status.md` | v2.6 collection in progress and no final analysis/result status. |
| `docs/research_progress_log.md` | PIPE-06 through PIPE-10 implementation/validation status and no-final-results restriction. |
| `docs/final_paper_notes.md` | Reconciliation backlog and reporting constraints, subordinate to frozen/controlling evidence. |
| `docs/decision_log.md` | D001, D008, D009, D013, D015, D032–D037 controlling scope and metric decisions. |
| `docs/analysis_specification_v1.0.md` | Analysis-unit and historical-supersession context. |
| `docs/package_hallucination_taxonomy.md` | Conservative classification, primary/secondary outcomes, and scope controls. |
| `docs/risk_assessment_protocol.md` | `risk-model-1.0.0` eligibility and boundaries. |
| `docs/task_set_v2_design.md`; `prompts/tasks/final_2.0.0.jsonl` | Task count, categories, Node.js/npm records, and task-design context. |
| `config/api_model_set_1.4.0.json`; `config/experiment_freeze_v2.6.0.json`; `docs/experiment_freeze_v2.6.0.md`; `manifests/api_final_v2.6.0_manifest.csv` | Frozen v2.6 conditions, model/provider identities, repetitions, and 360 planned observations. |
| `scripts/build_analysis_dataset.py`; `scripts/calculate_primary_metrics.py`; `scripts/adjudicate_review_required_packages.py`; `scripts/calculate_dependency_reliability_metrics.py`; `scripts/analyze_group_comparisons.py`; `scripts/score_risk_findings.py` | Implemented pipeline boundaries only; no final metric computation was run. |
