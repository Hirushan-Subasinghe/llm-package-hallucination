# Chapter 2 Literature Synthesis - CHAPTER-2-LITERATURE-SYNTHESIS-01

## 1. Reconciliation basis

This is an evidence-and-structure document, not Chapter 2 prose. It follows the controlling source order in `AGENTS.md` and `docs/report_generation_protocol.md`. The source review comprised the complete baseline Chapter 2 (printed pp. 4-47; PDF text extracted and inspected), the controlled set of 34 approved references, the current-status, progress, final-paper, decision, claims-control, and Chapter 1 reconciliation documents named in the task.

The final dissertation reports a Node.js/npm empirical study. Its literature review may retain cross-ecosystem, autonomous-system, attack, and mitigation literature as clearly attributed context. It must not imply that the performed experiment evaluated Java/Maven, PyPI, agent autonomy, package installation/execution, attacks, surveys, predictive models, or mitigation effectiveness. In particular, a registry `not_found` result is evidence to be adjudicated, not a self-explanatory confirmed hallucination (D033-D037).

`approved_references.md` establishes a citation boundary, not source-level verification: it records that all 34 entries were extracted from the baseline bibliography and that external bibliographic verification was not performed. No source PDFs/full texts were available in this worktree and no web search was used. Therefore, a high-level topic may be inferred only where the title and baseline use align; every substantive paraphrase, definition, comparison, and numeric claim still requires source-level verification before it enters final prose.

Milestone assessment: progress-log update needed **YES** (a significant Chapter 2 support-document milestone was completed); final-paper note needed **NO**; draft reconciliation needed **YES** (completed in this document). No historical log or note was edited because this task did not authorize those edits.

## 2. Baseline Chapter 2 inventory

| Baseline section | Principal themes and useful material | Citations used in baseline body | Principal reconciliation finding |
|---|---|---|---|
| 2.1 SLR methodology (2.1.1-2.1.7) | Search vocabulary, terminology map, selection and quality concerns, heterogeneous reporting/reproducibility as concepts. | None consistently tied to procedural claims. | The asserted database search, Boolean strings, PRISMA process, extraction matrix, quality assessment, and multi-reviewer process are not evidenced as performed final work. Remove as dissertation methodology; retain only a short non-methodological statement of the Chapter 2 scope if helpful. |
| 2.2 AI-assisted development landscape | LLM code-generation context; reliability, review, and code-hallucination terminology. | Le-Anh; Daoud; Liu et al. (2026); Gao; Zheng; Tian; Dubey and Madisetti; Zhuo; Jain; Li; Gandhi (2025); Yadav; Spracklen (2024); Ohm et al. (2020); Twist. | Retain concise code-generation/reliability context. Agentic/autonomous material is contextual only. `Gandhi, 2025`, `Spracklen et al., 2024`, and `Ohm et al., 2020` do not match approved entries and cannot be cited as written. |
| 2.3 LLMs for code generation | Model variation, code hallucination, package hallucination, evaluation differences, package-name terminology. | Liu et al. (2026); Zheng; Twist; Lian; Jain; Daoud; Gao; Tian; Tripathi; Li; Al-Zofi; Spracklen; Yang. | This is the strongest conceptual foundation, but exact rates, root-cause assertions, closed/open model rankings, and ecosystem architecture explanations require verification or removal. |
| 2.4 Software supply-chain security | Supply-chain context; distinctions among typosquatting, dependency confusion, slopsquatting; registries; AI/agentic risk. | Al-Zofi; Ohm and Stuke; Yadav; Gandhi (2025); Qu; Tileria; Woesle; Duan; Spracklen; Zheng. | Keep the conceptual distinctions and supply-chain context after verification. Remove claims that the experiment evaluated attack propagation, confused-deputy behaviour, registry architecture, active malicious registration, or agent execution. |
| 2.5 Detection approaches | Registry validation, static analysis, execution-based approaches, and the distinction between textual and behavioural checks. | Daoud; Al-Zofi; Duan; Dubey and Madisetti; Tileria; Ohm and Stuke; Jain; Tian; Yang; Qu; Yadav. | Retain as related-work context. Explain that the dissertation used read-only registry evidence and conservative classification, not a static/dynamic detector comparison or execution-based validation. Registry absence cannot be equated to hallucination. |
| 2.6 Mitigation strategies | RAG, knowledge graphs, API documentation, retrieval and maintenance trade-offs. | Twist; Spracklen; Le-Anh; Zheng; Jain; Li; Liu et al. (2025b); Dubey and Madisetti; Washio and Miyao; Qu; Tileria. | Merge into a short related-work subsection or background within detection/validation. Do not make it a large mitigation chapter: no intervention was implemented or evaluated. All effectiveness/latency/cost claims require source checks. |
| 2.7 Evaluation of mitigation | Metric and benchmark differences; static/execution evaluation; generalization concerns. | Lian; Jain; Li; Spracklen; Tian; Twist; Le-Anh; Qu; Liu et al. (2025b); Zheng; Daoud; Yang; Al-Zofi. | Merge with 2.6 and 2.8 as methodological-comparison context. Do not retain claims of mitigation evaluation by this study. |
| 2.8 Research gaps | Heterogeneity, benchmark/design limits, supply-chain context, agentic risk, validation trade-offs. | Le-Anh; Lian; Tian; Tripathi; Al-Zofi; Spracklen; Gandhi (2025); Qu; Yadav; Tileria; Yang; Jain; Li; Liu et al. (2025b); Zhao; Twist. | Replace broad absence/priority language with a bounded synthesis. The final rationale is the implemented, traceable Node.js/npm assessment; it is not proof that no comparable work exists. |

Useful retained terminology: *code hallucination* as an LLM code-reliability concern; *package hallucination* or *package-name hallucination* as a literature concept; *typosquatting*, *dependency confusion*, and *slopsquatting* as distinct security concepts; and *registry validation* as an evidence-gathering approach. Final operational terms such as **confirmed package-name hallucination**, PHR/SHR, DFR/RDFR, and classification outcomes must be defined from D033-D037 and the implemented taxonomy, not imported from the baseline.

Baseline body-citation inventory: Al-Zofi (2025); Daoud (2026); Duan et al. (2020); Dubey and Madisetti (2026); Gao et al. (2025); Jain et al. (2025); Le-Anh et al. (2026); Li et al. (2026); Lian et al. (2024); Liu et al. (2025b); Liu et al. (2026); Ohm and Stuke (2023); Qu et al. (2026); Spracklen et al. (2025); Tian et al. (2025); Tileria et al. (2026); Tripathi et al. (2025); Twist et al. (2026); Washio and Miyao (2022); Woesle et al. (2025); Yadav et al. (2026); Yang et al. (2026); Zheng et al. (2026); and Zhuo et al. (2025). The baseline also uses the unapproved/mismatched forms Gandhi (2025), Spracklen et al. (2024), and Ohm et al. (2020), plus one malformed `[2025; Zheng et al., 2026]` citation. Approved entries not cited in the baseline body remain assessed in Section 4 but are not falsely described as baseline uses.

## 3. Proposed final Chapter 2 structure

The proposed structure has 10 numbered sections and 18 substantive subsections. It is designed for approximately 22-30 university-formatted pages without padding.

1. **2.1 Chapter Introduction**
2. **2.2 Large Language Models in Software Development**
   - 2.2.1 Code generation and reliability limitations
   - 2.2.2 Code hallucination as a software-engineering concern
3. **2.3 Software Dependency Ecosystems and Package Registries**
   - 2.3.1 Dependencies and software supply-chain context
   - 2.3.2 Package managers and registries: npm as the empirical boundary
4. **2.4 Software Supply-Chain Threats Related to Package Naming**
   - 2.4.1 Typosquatting
   - 2.4.2 Dependency confusion
   - 2.4.3 Related package-manager attacks and the distinction from package hallucination
5. **2.5 Package Hallucination in LLM-Generated Code**
   - 2.5.1 Concept, terminology, and package-name hallucination
   - 2.5.2 Empirical package-hallucination research
   - 2.5.3 Slopsquatting as downstream security context
6. **2.6 Detection, Validation, and Classification Approaches**
   - 2.6.1 Registry validation and static/reference-level analysis
   - 2.6.2 Execution-based and other validation approaches
   - 2.6.3 Classification and adjudication limits
7. **2.7 Reliability, Security, and Risk Assessment**
   - 2.7.1 Practical consequences and supply-chain implications
   - 2.7.2 Risk-oriented and mitigation-related literature (context only)
8. **2.8 Comparative Dimensions in Prior Research**
   - 2.8.1 Model, task, and ecosystem variation
   - 2.8.2 Repetition, non-determinism, measurement, and reproducibility
9. **2.9 Synthesis of Literature and Research Gap**
10. **2.10 Chapter Summary**

Cross-ecosystem papers are retained where they advance conceptual comparison, but Chapter 2 must state that npm is the final experimental boundary. No final section is titled “Systematic Literature Review Methodology”; the baseline does not provide evidence that the claimed SLR procedure was performed, and it is not the final study method.

## 4. Approved-reference theme matrix

Support confidence concerns source-level support for a final paraphrase, not publication quality or thematic relevance. `LOW*` means only metadata and/or baseline attribution were available; **SOURCE-LEVEL VERIFICATION REQUIRED**.

| Reference | Main Theme | Relevant Chapter 2 Section(s) | Baseline Usage | Final Use Recommendation | Support Confidence | Notes |
|---|---|---|---|---|---|---|
| Agarwal et al. (2024) | code hallucination | 2.2, 2.5, 2.8 | Reference-list only | SUPPORTING | LOW* | Title directly concerns code hallucinations; source-level verification required. |
| Al-Zofi (2025) | package hallucination; slopsquatting | 2.3-2.7, 2.9 | Central, including definitions, registries, rates, detection | CORE | LOW* | Use conceptual context only until verified; all baseline numbers and registry/attack assertions require checking. |
| Daoud (2026) | security-related code hallucination | 2.2, 2.6, 2.7 | Code-hallucination/detection/mitigation context | SUPPORTING | LOW* | Systematic-review title fits broad synthesis; verify individual findings. |
| Duan et al. (2020) | package-manager attacks | 2.3, 2.4, 2.6, 2.7 | Supply-chain/detection discussion | CORE | LOW* | Strong contextual fit; do not carry package counts/removal claims without source review. |
| Dubey and Madisetti (2026) | debugging/reliability | 2.2, 2.6, 2.7 | Explainability/debugging and static context | POSSIBLE | LOW* | Not package-specific; use only for a narrow reliability statement after verification. |
| Gandhi (2026) | autonomous/agentic systems | 2.2, 2.7 | Baseline instead cites Gandhi (2025) | DO_NOT_USE_UNLESS_VERIFIED | LOW* | Citation-year identity mismatch must be resolved; no study-autonomy implication. |
| Gao et al. (2025) | code hallucination | 2.2, 2.6, 2.8 | General hallucination/reliability taxonomy | CORE | LOW* | Strong title fit; validate taxonomy/causal claims directly. |
| Jain et al. (2025) | detection/validation; API documentation | 2.6, 2.7 | Documentation-grounding effectiveness/trade-offs | SUPPORTING | LOW* | API, not package, focus; do not use unverified performance figures. |
| Zhao et al. (2025) | package hallucination; testing | 2.5, 2.6, 2.8, 2.9 | Gap/validation context | CORE | LOW* | Directly relevant title; verify method, definition, and scope before comparison. |
| AlSobeh et al. (2025) | dependency hallucination; defenses | 2.6, 2.7 | Reference-list only | POSSIBLE | LOW* | Title suggests relevance but source is unavailable; no role/prompt-injection claim without verification. |
| Ladisa et al. (2023) | software supply chain | 2.3, 2.4, 2.7, 2.9 | Reference-list only | CORE | LOW* | Use for broad attack-taxonomy context, not definitions unless source checked. |
| Le-Anh et al. (2026) | repository-level code generation | 2.2, 2.7, 2.8 | Code-as-not-natural-language and repository context | SUPPORTING | LOW* | Useful scope/limitations context; not evidence for the performed experiment. |
| Li et al. (2026) | API hallucination mitigation | 2.6, 2.7 | Knowledge-graph mitigation | BACKGROUND_ONLY | LOW* | Literature-only mitigation direction; no effectiveness claims without verification. |
| Lian et al. (2024) | code-generation evaluation | 2.2, 2.6, 2.8 | Match-based metric limitations | SUPPORTING | LOW* | Relevant to evaluation variation; all quantified error claims require source review. |
| Liu (2026) | code-hallucination mitigation | 2.7 | Reference-list only | BACKGROUND_ONLY | LOW* | Pseudocode intervention is outside final scope. |
| Liu et al. (2025a) | hallucination detection metrics | 2.6, 2.8 | Reference-list only | SUPPORTING | LOW* | Different generation direction; use only for careful metric-definition context. |
| Liu et al. (2025b) | API hallucination mitigation | 2.6, 2.7 | Knowledge injection | BACKGROUND_ONLY | LOW* | Intervention literature only; source-level verification required. |
| Liu et al. (2026) | code hallucination | 2.2, 2.6, 2.8 | Functional-correctness and code-hallucination context | SUPPORTING | LOW* | General conceptual source; no model-performance paraphrase until verified. |
| Ohm and Stuke (2023) | supply-chain attack detection | 2.3, 2.4, 2.6, 2.7 | Static/dynamic detection and dependency graphs | CORE | LOW* | Strong detection-context fit; do not import operational-effectiveness claims unverified. |
| Pashchenko et al. (2022) | dependency risk assessment | 2.3, 2.7 | Reference-list only | POSSIBLE | LOW* | Vulnerable dependencies are not package hallucinations; use only to distinguish constructs. |
| Qu et al. (2026) | agentic supply-chain poisoning | 2.4, 2.7 | Agentic attack/detection bypass claims | BACKGROUND_ONLY | LOW* | Context only; no autonomous systems were evaluated. All attack-rate claims require verification. |
| Spracklen et al. (2025) | package hallucination | 2.5, 2.6, 2.8, 2.9 | Central prevalence/model/ecosystem assertions | CORE | LOW* | Directly relevant title. Every baseline sample/rate/definition and `2024` mismatch requires source verification. |
| Tian et al. (2025) | execution-based validation | 2.2, 2.6, 2.8 | CodeHalu/execution-based discussion | SUPPORTING | LOW* | Relevant contrast to read-only registry evidence; no execution was performed here. |
| Tileria et al. (2026) | API fact-checking | 2.6, 2.7 | Hallucination-inspector and scaffolding claims | POSSIBLE | LOW* | API migration focus may limit relevance; verify before use. |
| Tripathi et al. (2025) | agentic coder reliability | 2.2, 2.7, 2.8 | Overconfidence/model-scale claims | BACKGROUND_ONLY | LOW* | Agentic focus is contextual only; do not import causal/model claims. |
| Twist et al. (2026) | library hallucinations; risk | 2.5, 2.7, 2.8 | Temporal prompts/library-rate claims | CORE | LOW* | Strong library-hallucination title fit; exact 85% claim needs source-level verification. |
| Wang et al. (2025) | LLM supply chain | 2.3, 2.7, 2.9 | Reference-list only | SUPPORTING | LOW* | Broad research-agenda context, not direct empirical evidence. |
| Washio and Miyao (2022) | API documentation | 2.6, 2.7 | Documentation grounding | BACKGROUND_ONLY | LOW* | Unknown-library generation is context only; source-level verification required. |
| Williams et al. (2025) | software supply chain | 2.3, 2.4, 2.7, 2.9 | Reference-list only | SUPPORTING | LOW* | Research-directions context; not a direct package-hallucination source. |
| Woesle et al. (2025) | LLM hallucination | 2.2, 2.7, 2.8 | Self-verification/recall claim | POSSIBLE | LOW* | General LLM review; do not use the baseline 0.02 figure without verification. |
| Yadav et al. (2026) | AI-assisted development attack surface | 2.4, 2.7 | Agentic supply-chain framing | BACKGROUND_ONLY | LOW* | Literature context only; the experiment is stateless/no-tools. |
| Yang et al. (2026) | code-hallucination detection | 2.6, 2.8 | Hybrid detection and benchmark-gap claims | SUPPORTING | LOW* | Detection context, not study methodology; verify evaluation scope. |
| Zheng et al. (2026) | package hallucination; Rust crates | 2.5, 2.8 | Cross-ecosystem/model comparisons | SUPPORTING | LOW* | Cross-ecosystem context only; do not make npm claims from Rust evidence. |
| Zhuo et al. (2025) | API misuse | 2.2, 2.6 | API misuse context | POSSIBLE | LOW* | API misuse differs from package-name hallucination. |

**Recommendation totals (34 references):** CORE **8**; SUPPORTING **12**; BACKGROUND_ONLY **7**; POSSIBLE **6**; DO_NOT_USE_UNLESS_VERIFIED **1**.

## 5. Literature-claim matrix

`SUPPORTED` means the approved title and baseline citation usage support a cautious, non-numeric planning statement, not that the source has been independently read in this worktree. Source-level verification remains required before prose.

| Claim ID | Proposed Literature Claim | Supporting Approved References | Support Status | Recommended Section | Notes |
|---|---|---|---|---|---|
| LC01 | LLM-generated code can contain hallucinated or unreliable elements. | Gao; Agarwal; Liu et al. (2026); Daoud | SUPPORTED | 2.2 | Use cautious reliability language; no prevalence assertion. |
| LC02 | Code hallucination may survive superficial or syntax-oriented checks, motivating richer validation approaches. | Tian; Lian; Yang | PARTIALLY_SUPPORTED | 2.2, 2.6 | Verify that each source makes the proposed static-versus-execution comparison. |
| LC03 | Software commonly incorporates third-party dependencies, making dependency references relevant to software engineering. | Ladisa; Williams; Pashchenko; Ohm and Stuke | PARTIALLY_SUPPORTED | 2.3 | Do not retain the baseline “180 dependencies” average. |
| LC04 | Package managers and registries create relevant software supply-chain exposure. | Ladisa; Duan; Ohm and Stuke; Williams | SUPPORTED | 2.3, 2.4 | General context only; not evidence of compromise in this study. |
| LC05 | Typosquatting is a package-naming attack distinct from package hallucination. | Ladisa; Duan; Al-Zofi | PARTIALLY_SUPPORTED | 2.4 | Confirm exact technical definitions before final prose. |
| LC06 | Dependency confusion is distinct from package hallucination. | Ladisa; Duan; Al-Zofi | PARTIALLY_SUPPORTED | 2.4 | Never call an npm absence or name similarity dependency confusion. |
| LC07 | Package-name hallucination is a relevant manifestation of code hallucination in generated dependency references. | Spracklen; Zhao; Al-Zofi; Twist | SUPPORTED | 2.5 | Final operational definition comes from implementation, not literature alone. |
| LC08 | Slopsquatting describes a downstream security concern involving malicious use of AI-hallucinated names. | Al-Zofi; Spracklen | PARTIALLY_SUPPORTED | 2.5, 2.7 | Verify terminology/source wording. It is not an observed attack in this study. |
| LC09 | Hallucinated package names are not equivalent to confirmed exploitation. | Al-Zofi; Ladisa; Duan; Ohm and Stuke | SUPPORTED | 2.5, 2.7 | Logical distinction supported by the distinct themes; do not assert empirical exploitation without a verified source. |
| LC10 | Package hallucination has been studied empirically. | Spracklen; Zhao; Twist; Zheng | SUPPORTED | 2.5, 2.8 | Direct titles establish active research; no “unexplored” claim. |
| LC11 | Different studies use different definitions, validation rules, settings, and outcomes, limiting direct comparison. | Gao; Zhao; Spracklen; Tian; Lian; Liu et al. (2025a) | PARTIALLY_SUPPORTED | 2.6, 2.8, 2.9 | Must be demonstrated source-by-source before firm prose. |
| LC12 | Registry absence alone may be insufficient to classify a package reference as a hallucination. | Al-Zofi; Zhao; Spracklen; Duan | PARTIALLY_SUPPORTED | 2.6 | Literature support needs verification; independently, this is a controlling study-method rule, not a literature finding. |
| LC13 | Repeated generations and non-determinism are relevant to interpreting generated-code outcomes. | Gao; Twist; Spracklen; Tian | PARTIALLY_SUPPORTED | 2.8 | Avoid causal/temperature statements unless verified. |
| LC14 | Model, task/domain, and ecosystem differences are relevant comparison dimensions. | Spracklen; Twist; Zheng; Lian; Zhao | PARTIALLY_SUPPORTED | 2.8 | Do not state the direction or magnitude of differences without source review. |
| LC15 | Validation/detection approaches include registry/reference checking, static analysis, and execution-based approaches. | Zhao; Duan; Ohm and Stuke; Tian; Yang | SUPPORTED | 2.6 | Clearly distinguish literature approaches from the performed read-only npm workflow. |
| LC16 | Practical and security consequences of unreliable dependency references vary by context. | Ladisa; Williams; Al-Zofi; Twist | PARTIALLY_SUPPORTED | 2.7 | Do not infer maliciousness, installation, exploitability, compromise, or loss from a finding. |
| LC17 | Broad novelty assertions such as “no prior research” are unsupported. | Spracklen; Zhao; Al-Zofi; Twist; Zheng | CONTRADICTED | 2.9 | Existing approved package/library-hallucination work directly defeats such wording. |
| LC18 | Mitigation/grounding approaches are available in prior work. | Jain; Li; Liu et al. (2025b); Washio and Miyao; AlSobeh | PARTIALLY_SUPPORTED | 2.7 | Mention only as related work/future context; no intervention evaluated here. |
| LC19 | Agentic systems can be discussed as a broader, distinct risk context. | Gandhi; Qu; Tripathi; Yadav | PARTIALLY_SUPPORTED | 2.7 | Gandhi identity must be reconciled; not a final study variable. |
| LC20 | Cross-ecosystem literature can provide context while an empirical study remains npm-specific. | Spracklen; Zheng; Al-Zofi; Duan | SUPPORTED | 2.3, 2.5, 2.8 | Explicitly mark PyPI/Maven/Rust as literature context, not study ecosystems. |

**Claim totals (20 claims):** SUPPORTED **7**; PARTIALLY_SUPPORTED **12**; UNVERIFIED **0**; CONTRADICTED **1**. LC17 is intentionally recorded as contradicted because existing approved package/library-hallucination work rules out the proposed novelty assertion.

## 6. Baseline Chapter 2 reconciliation matrix

| Baseline Section/Topic | Action | Reason | Final Destination |
|---|---|---|---|
| 2.1 SLR methodology, Boolean strings, inclusion/exclusion, PRISMA, multi-reviewer selection | REMOVE | No evidence that this dissertation performed the described review procedure; it is superseded as final-study framing. | At most a one-sentence Chapter 2 scope statement; not a method section. |
| Terminology evolution table | KEEP_WITH_REVISION | Useful conceptual bridge, but contains unsupported framing and no final-study method. | 2.1/2.4/2.5 narrative; no need to reproduce table. |
| AI code-generation evolution | KEEP_WITH_REVISION | Supports background but needs concise, verified statements. | 2.2.1 |
| Traditional versus AI-assisted programming | MERGE | Reliability/validation discussion overlaps later sections. | 2.2.2 and 2.6 |
| Agent autonomy / agentic coding | MOVE | Useful broader context, but final study was stateless/no-tools and did not evaluate autonomy. | Brief 2.7.2 context or future work; omit if source verification remains unresolved. |
| Commercial versus open-source model comparison | KEEP_WITH_REVISION | Model variation is relevant, but exact model rankings/rates are unverified and do not map to the final condition design. | 2.8.1 |
| General code hallucination | KEEP_WITH_REVISION | Core conceptual foundation; avoid causal/metric assertions. | 2.2.2 |
| Package hallucination | KEEP_WITH_REVISION | Core topic; literature concept must be distinguished from conservative implemented classification. | 2.5 |
| PyPI material | KEEP_WITH_REVISION | Useful cross-ecosystem literature context; not an experiment ecosystem. | 2.3/2.5/2.8, explicitly contextual |
| Java/Maven material | MOVE | Registry-design comparison may be contextual, but baseline causal superiority and zero-rate claims are unverified; no performed Java/Maven study. | Brief 2.3/2.8 only if verified |
| npm material | KEEP_WITH_REVISION | Relevant registry context and empirical boundary; remove unsupported registry-scale/architecture claims. | 2.3.2, 2.6, 2.9 |
| Typosquatting | KEEP_WITH_REVISION | Relevant distinction from package hallucination; source definition needs checking. | 2.4.1 |
| Dependency confusion | KEEP_WITH_REVISION | Relevant distinction; it was not measured/tested by this study. | 2.4.2 |
| Slopsquatting | KEEP_WITH_REVISION | Relevant downstream security context, not an observed attack or registry registration exercise. | 2.5.3 and 2.7.1 |
| “Confused deputy” framing | REMOVE | Baseline uses it for tool-enabled autonomous agents; no such interface or variable exists in final study. | Future work only, if verified and clearly separated |
| Registry architectures | KEEP_WITH_REVISION | Context can aid interpretation, but avoid deterministic claims about namespace design or ecosystem outcomes. | 2.3.2 |
| Static detection | KEEP_WITH_REVISION | Related-work context; final workflow gathered registry evidence but did not evaluate a static detector. | 2.6.1 |
| Runtime/execution detection | MOVE | Useful contrast to direct reference/registry validation; no generated code/dependency execution occurred. | 2.6.2 |
| RAG, knowledge graphs, documentation grounding | MERGE | Related mitigation literature only; not enough for multiple long sections. | 2.7.2 |
| Mitigation evaluation/table | REMOVE | Baseline figures, cost/latency/effectiveness comparisons are unverified and no mitigation evaluation was performed. | Mention verified approaches narratively only in 2.7.2 |
| Trust/verification systems | MOVE | Literature context; final evidence chain is a methodology claim, not a tested trust system. | 2.6/2.9, carefully bounded |
| Developer expertise/trust decay | REMOVE | No developer survey/expertise variable, and broad absence claims are unsupported. | Future work only if appropriate |
| Predictive/risk modelling | REMOVE | Final study uses a deterministic post-classification ordinal Impact x Detectability framework, not predictive modelling. | Chapter 3 methodology; 2.7 only broad risk context |
| Prevalence/model/attack/detection figures | VERIFY_BEFORE_USE | All values require direct source and denominator/context checks. | Only relevant verified values, otherwise no numerical carry-over |
| Research-gap claims | KEEP_WITH_REVISION | Broad “lack”, “absence”, and “first” claims are not supported. | 2.9 bounded synthesis |

## 7. Numeric/prevalence claim audit

Every numeric or quantitative claim located in baseline Chapter 2 is listed below. Repetitions of the same number across sections/tables are consolidated; none is approved for final prose without direct source review.

| Numeric Claim | Baseline Citation | Verification Status | Final Action |
|---|---|---|---|
| Up to 97% of developers incorporate generative AI | Al-Zofi (2025) | UNVERIFIED; source-level evidence unavailable | REMOVE |
| Approximately 30% of codebase compositions contain AI-generated contributions | Al-Zofi (2025) | UNVERIFIED | REMOVE |
| Dependency fabrication up to 85% under temporal/low-frequency prompts | Twist et al. (2026); Jain et al. (2025) | UNVERIFIED; baseline repeats it without stable method/denominator | REMOVE |
| 2.23 million code samples; 5.2% commercial versus 21.7% open-source fabrication | Al-Zofi (2025) | UNVERIFIED | REMOVE |
| 39.02% absolute correctness drop with sub-optimal retrieval | Jain et al. (2025) | UNVERIFIED | REMOVE |
| Up to 43.66% correct GPT-4 outputs misclassified by match-based measures | Lian et al. (2024) | UNVERIFIED | SOURCE_LEVEL_VERIFICATION_REQUIRED |
| 15.8% Python and 21.3% JavaScript package-hallucination frequencies | Spracklen et al. (2025) | UNVERIFIED; exact estimator/population unknown | REMOVE |
| 19.7% average across 576,000 samples | Spracklen et al. (2025) | UNVERIFIED | REMOVE |
| Average 180 direct and transitive third-party dependencies | Ohm and Stuke (2023) | UNVERIFIED | REMOVE |
| Up to 33.5% bypass combined/static defenses | Qu et al. (2026) | UNVERIFIED | REMOVE |
| Approximately 2.5% evade strict structural/localized static defenses | Qu et al. (2026) | UNVERIFIED | REMOVE |
| Self-verification recall of 0.02 | Woesle et al. (2025) | UNVERIFIED | REMOVE |
| Nearly 3.4 million active npm packages | Al-Zofi (2025) | UNVERIFIED and time-sensitive | REMOVE |
| Approximately 82% removal of flagged dependencies | Duan et al. (2020) | UNVERIFIED; baseline wording may conflate outcome measures | SOURCE_LEVEL_VERIFICATION_REQUIRED |
| 6,705 invalid dependency fabrications for npm and exactly 0 for Maven Central | Spracklen et al. (2025) | UNVERIFIED | REMOVE |
| Up to 90.7% of explicit code injections intercepted | Qu et al. (2026) | UNVERIFIED | REMOVE |
| Static lookup filters flag up to 94.8% of package hallucinations | Al-Zofi (2025) | UNVERIFIED | REMOVE |
| 82% confirmation/removal across 339 intercepted malicious packages | Duan et al. (2020) | UNVERIFIED; needs exact metric/context | SOURCE_LEVEL_VERIFICATION_REQUIRED |
| 8.1% relative repair and 4.0% test-pass improvement | Li et al. (2026) | UNVERIFIED | REMOVE |
| Error rate reduced from 61.18% to 16.64% | Liu et al. (2025b) | UNVERIFIED | REMOVE |
| Valid cloud invocation increased from 38.58% to 47.94% | Jain et al. (2025) | UNVERIFIED | REMOVE |

**Numeric-claim count:** 21 distinct claims (many repeated in baseline Sections 2.2-2.7 and Table 2.2). Baseline structural numbers such as subsection/table/figure numbering are not treated as empirical literature claims.

## 8. Section-by-section writing plan

| Final subsection | Purpose and major argument | Suitable references | References not to use there | Target length | Transition | Source-level verification required |
|---|---|---|---|---:|---|---|
| 2.1 Introduction | State the review’s conceptual scope and distinguish literature context from the npm empirical boundary. | Gao; Spracklen; Ladisa | Mitigation-only or agent-only sources | 1-1.5 pp. | From reliability problem to software dependencies. | Verify all opening definitions. |
| 2.2.1 Code generation and reliability | Establish LLM code generation as a software-engineering setting with reliability limitations. | Gao; Agarwal; Liu et al. (2026); Daoud | Al-Zofi for adoption figures; Qu/Yadav agentic attack claims | 2-2.5 pp. | Narrow general reliability to hallucination. | Definitions and scope of code hallucination. |
| 2.2.2 Code hallucination | Explain code hallucination and why syntax/functional correctness are not interchangeable. | Gao; Tian; Lian; Liu et al. (2026) | Package-attack rates; mitigation performance figures | 2-2.5 pp. | Move from general errors to dependency references. | Any taxonomy, cause, or evaluation claim. |
| 2.3.1 Dependencies and supply chain | Position third-party dependencies and package managers in supply-chain context. | Ladisa; Williams; Duan; Ohm and Stuke | Baseline dependency/package counts | 2-2.5 pp. | From dependency relevance to registries. | General dependency and attack-taxonomy wording. |
| 2.3.2 Registries and npm boundary | Explain registries as validation context and state npm-only study scope. | Duan; Ohm and Stuke; Al-Zofi; Spracklen | Claims that Maven architecture causes a rate; npm-scale statistics | 1.5-2 pp. | From registry context to naming threats. | Cross-ecosystem/registry assertions. |
| 2.4.1 Typosquatting | Define and distinguish typosquatting from generated-name errors. | Ladisa; Duan; Al-Zofi | Agentic/mitigation sources | 1-1.5 pp. | Contrast with dependency confusion. | Exact definition. |
| 2.4.2 Dependency confusion | Define dependency confusion and distinguish it from a nonexistent/incorrect package claim. | Duan; Ladisa; Al-Zofi | Package prevalence sources | 1-1.5 pp. | Broaden to related attacks but preserve distinctions. | Exact package-resolution mechanics. |
| 2.4.3 Related attacks | Briefly situate other package-manager attacks without turning Chapter 2 into an attack survey. | Ladisa; Ohm and Stuke; Williams | Qu quantitative bypass claims | 1-1.5 pp. | Introduce package hallucination as a different upstream error context. | Taxonomy linkage. |
| 2.5.1 Concept and terminology | Define package hallucination at literature level and reserve final operational classification for Chapter 3. | Spracklen; Zhao; Al-Zofi; Twist | Baseline rates, any final-study metric definition | 2-2.5 pp. | From concept to prior empirical work. | Definitions and scope. |
| 2.5.2 Empirical research | Synthesize what package/library-hallucination studies investigate; compare dimensions, not unverified figures. | Spracklen; Zhao; Twist; Zheng | Gandhi; generic API-only mitigation papers | 2.5-3 pp. | From studies to downstream security context. | Designs, ecosystems, sample sizes, validation rules, outcomes. |
| 2.5.3 Slopsquatting | Explain slopsquatting as potential downstream malicious registration/use of hallucinated names; do not conflate it with a hallucination. | Al-Zofi; Spracklen | DFR/RDFR or any claim of observed exploitation | 1-1.5 pp. | Shift from security context to validation. | Definition and any empirical incident/prevalence claim. |
| 2.6.1 Registry/static validation | Compare registry lookup and reference/static checks; establish why existence evidence is not a complete classification. | Zhao; Duan; Ohm and Stuke; Al-Zofi | “94.8%” effectiveness, final study as detector | 2-2.5 pp. | Explain methods beyond existence lookup. | Tool/method capability claims. |
| 2.6.2 Execution-based validation | Contrast execution/behavioural approaches with registry validation, and state no code/dependency execution was performed. | Tian; Yang; Lian | Supply-chain attack prevalence; mitigation performance | 1.5-2 pp. | Move to classification/adjudication limits. | Execution benchmarks and detection performance. |
| 2.6.3 Classification/adjudication | Synthesize definitional/validation heterogeneity and motivate cautious separation of nonexistence, confusion, local names, and unresolved cases. | Spracklen; Zhao; Al-Zofi; Duan | Any source not verified for classifications | 2-2.5 pp. | Connect classification to consequence/risk. | Direct evidence that sources use differing rules; Chapter 3 defines final taxonomy. |
| 2.7.1 Consequences and implications | Describe reliability and supply-chain implications as conditional/context-dependent. | Ladisa; Williams; Ohm and Stuke; Al-Zofi | Exploitation, installation, loss, or maliciousness claims unsupported by sources | 1.5-2 pp. | From consequence to approaches intended to reduce risk. | Any causal security-impact claim. |
| 2.7.2 Risk/mitigation context | Briefly identify documentation, knowledge, retrieval, and defensive research; clarify no mitigation evaluation in the dissertation. | Jain; Li; Liu et al. (2025b); Washio; AlSobeh | All baseline effectiveness/cost/latency figures | 1.5-2 pp. | Move to how prior work varies. | Individual approach results and limitations. |
| 2.8.1 Comparison dimensions | Synthesize model/task/ecosystem variation as reasons comparisons need explicit boundaries. | Spracklen; Zhao; Twist; Zheng; Lian | Closed/open ranking claims; Java/Maven causal claims | 1.5-2 pp. | Link variation to repeated generations/reproducibility. | Each reported comparison dimension. |
| 2.8.2 Non-determinism and reproducibility | Explain why repeated generation, fixed conditions, preserved inputs/outputs, and transparent validation matter. | Gao; Tian; Spracklen; Twist | Final-results claims or frozen-study details as literature evidence | 1.5-2 pp. | Summarise evidence limits into the gap. | Non-determinism/repetition claims. |
| 2.9 Synthesis and gap | State what the verified literature establishes, identify comparability/definition issues conservatively, then separate this study’s implementation rationale. | Core package-hallucination and supply-chain subset | Broad novelty/absence wording; unverified numeric sources | 2-2.5 pp. | Lead to Chapter 3 method. | Every comparative gap statement. |
| 2.10 Summary | Recap conceptual chain and scope. | Reuse verified citations only if needed | New claims/numbers | 0.5-1 pp. | Chapter 3’s implemented method. | None beyond reused claims. |

Estimated total: **25-29 pages**, allowing the final verified source synthesis to determine the natural final length.

## 9. Research-gap synthesis

### Literature-supported gap (conditional on source-level verification)

The approved set plainly contains work on code hallucination, package hallucination, package-hallucination testing, library/crate hallucination, supply-chain attacks, and detection/mitigation. Chapter 2 must therefore not portray the topic as unexplored, without benchmarks, or without detection approaches. The titles and baseline narrative support investigating whether prior studies differ in their constructs, target ecosystems, model/task settings, validation methods, and reported units. Those differences can make prevalence figures difficult to compare directly unless the exact definition of a package hallucination, the registry evidence rule, the unit of analysis, eligibility treatment, and sampling conditions are made explicit. This synthesis is provisional until the relevant source texts are checked.

The most defensible literature-facing statement is not an absence claim: it is that comparison should be bounded by the definition and validation rule used. In particular, a package name that does not resolve at a registry lookup may have multiple explanations. Literature discussion of naming attacks, registry validation, and package hallucination should not be used to collapse a registry result, name confusion, local reference, legacy state, or an unresolved case into one category.

### Implementation-based study rationale (not a claim about literature absence)

The final study provides a defined Node.js/npm assessment with frozen tasks and model conditions; repeated independent generations; preserved response and provenance evidence; deterministic direct-reference extraction and normalization; timestamped read-only npm registry evidence; conservative classification/adjudication; D033/D037 primary PHR/SHR routing; separately labelled D036 exploratory DFR/RDFR; and a post-classification ordinal risk framework for eligible confirmed findings. This is a description of the implemented design, not an assertion that no earlier paper integrated any of those elements.

The rationale for Chapter 2 Section 2.9 is consequently: a controlled npm-specific assessment benefits from explicit scope, traceability, and separation of confirmed package-name hallucination from broader exact-name dependency-resolution failure. That rationale directly supports Chapter 1 RQ1-RQ4 while avoiding claims of priority, comprehensive novelty, or exploitation.

## 10. High-confidence core references

These nine entries are the strongest **thematic** core for Chapter 2 because their approved titles and baseline placement directly align with the final chapter. “High-confidence” here means relevance to the planned synthesis, not source-level verification, which remains pending for all nine.

- Spracklen et al. (2025) - package hallucinations by code-generating LLMs.
- Zhao et al. (2025) - testing LLMs for package hallucinations.
- Al-Zofi (2025) - package hallucinations, slopsquatting, and supply-chain context.
- Twist et al. (2026) - library hallucinations and risk.
- Gao et al. (2025) - code-hallucination synthesis.
- Ladisa et al. (2023) - open-source supply-chain attack taxonomy.
- Duan et al. (2020) - package-manager supply-chain attacks.
- Ohm and Stuke (2023) - practical detection of supply-chain attacks.
- Zheng et al. (2026) - empirical package hallucination in a different ecosystem.

## 11. References requiring source-level verification

**All 34 approved references require source-level verification for substantive Chapter 2 use**, because the repository supplies only reference metadata and baseline paraphrases, not source text. Priority verification order: Spracklen; Zhao; Al-Zofi; Twist; Ladisa; Duan; Ohm and Stuke; Gao; Zheng; Tian; Lian; Jain; Williams; Wang; Yang.

Additional bibliographic/citation anomalies requiring resolution before use:

- Baseline Chapter 2 cites `Gandhi, 2025`; the approved entry is Gandhi (2026).
- Baseline Chapter 2 cites `Spracklen et al., 2024`; the approved entry is Spracklen et al. (2025).
- Baseline Chapter 2 cites `Ohm et al., 2020`; the approved relevant entry is Ohm and Stuke (2023), while Duan et al. (2020) is separate.
- A malformed baseline citation appears as `[2025; Zheng et al., 2026]` in Section 2.7.

No corrected bibliography must be silently substituted; resolution belongs to the approved-reference control process.

## 12. Claims that must not appear in final Chapter 2

- That the dissertation performed an SLR, PRISMA screening, database search, multi-reviewer arbitration, or quality assessment without exact records.
- That Java/Maven, PyPI, Rust, autonomous agents, developer expertise, developer surveys, package installation/execution, malicious package registration, or mitigation interventions were part of the final empirical study.
- That an npm `404`/`not_found` alone confirms a package-name hallucination.
- That name confusion, namespace confusion, legacy/removed packages, local/self references, or unresolved references are confirmed hallucinations.
- That DFR/RDFR are hallucination rates or comprehensive dependency-reliability measures.
- That the study observed slopsquatting, exploitation, maliciousness, installation, compromise, loss, or attack success.
- Any unverified baseline percentage, package/sample count, rate, model ranking, registry-size figure, detection rate, or mitigation-effectiveness value identified in Section 7.
- “No prior work,” “first study,” “unexplored,” “no benchmarks,” “no detection approaches,” “complete absence,” or equivalent novelty claims.
- That registry design deterministically explains ecosystem prevalence differences, absent direct verified source support.
- That RAG, knowledge graphs, documentation grounding, static/dynamic tools, or hybrid defenses were evaluated by this dissertation.
- Final empirical results, interim counts, rankings, statistical conclusions, or risk distributions while v2.6 collection and final analysis remain incomplete.

## 13. Open issues

1. Obtain or inspect source-level content for the priority references before drafting substantive prose; preserve the approved-reference boundary.
2. Resolve the three baseline-to-approved citation mismatches before reuse.
3. Decide, after verification, whether agentic/autonomous-system context merits a short 2.7.2 paragraph or is better left to future work.
4. Verify whether the literature explicitly supports the proposed assertion about heterogeneous definitions/validation rules; otherwise frame it only as an observed comparison criterion in this review.
5. Confirm which vetted baseline quantitative claims, if any, can survive source verification. The default is no numerical prevalence claim.
6. Before prose drafting, add verified literature claims to `claims_evidence_matrix.md` only if the controlling process authorizes that update; this task does not modify it.

Chapter 2 is **not ready for final prose drafting**: its structure and reconciliation are ready, but priority sources and all substantive citation claims still need source-level verification.

## 14. Evidence index

| Evidence | Use in this synthesis |
|---|---|
| `AGENTS.md` | Scope, integrity, citation, and reporting constraints. |
| `docs/report_generation_protocol.md` | Controlling workflow, Chapter 2 requirements, baseline policy, result-safety rules. |
| `docs/references/approved_references.md` | Exclusive 34-reference citation boundary and verification limitation. |
| `docs/source_documents/IM2021101.pdf` | Complete inspected baseline Chapter 2 (printed pp. 4-47) and its baseline citations, topics, figures, tables, and numbers. |
| `docs/current_research_status.md` | v2.6 still in progress; no final analysis/results. |
| `docs/research_progress_log.md` | Final-report controls, Chapter 1 milestone, and preserved methodology/result boundaries. |
| `docs/final_paper_notes.md` | Subordinate reporting/reconciliation constraints and current-design boundary. |
| `docs/decision_log.md` D033-D038 | Primary/secondary metric, classification, failure, and routing constraints used to prevent literature framing from misdescribing the study. |
| `docs/final_report_support/claims_evidence_matrix.md` | Claim-status control; not amended in this task. |
| `docs/final_report_support/chapter1_evidence_audit.md` | Verified Node.js/npm scope, RQs, and prior literature-reconciliation flags. |
| `docs/final_report_support/chapter1_draft_reconciliation.md` | Old-draft scope reconciliation and prohibited methodology claims. |
| `docs/final_report_support/chapter1_literature_reconciliation.md` | Earlier 22-claim literature audit, numerical-claim restrictions, and citation mismatch flags. |
| `docs/report_drafts/chapter1_complete_draft.md` | Chapter 1 RQ1-RQ4 and the hand-off to Chapter 2. |

## Completion summary

- Proposed Chapter 2 sections/subsections: **10 numbered sections; 18 substantive subsections**.
- References assessed: **34**.
- Recommendations: **CORE 8 / SUPPORTING 12 / BACKGROUND_ONLY 7 / POSSIBLE 6 / DO_NOT_USE_UNLESS_VERIFIED 1**.
- Literature claims assessed: **20**.
- Claim status: **SUPPORTED 7 / PARTIALLY_SUPPORTED 12 / UNVERIFIED 0 / CONTRADICTED 1**.
- Numeric/prevalence claims found: **21 distinct claims**.
- Strongest thematic references: Spracklen et al. (2025), Zhao et al. (2025), Al-Zofi (2025), Twist et al. (2026), Gao et al. (2025), Ladisa et al. (2023), Duan et al. (2020), Ohm and Stuke (2023), and Zheng et al. (2026).
- References needing source-level verification: **all 34**, with priority order stated in Section 11.
- Ready for prose drafting: **NO - source-level verification is required first**.
- `git diff --check`: **PASS** (run after creating this file).
- `git status --short`: `?? docs/final_report_support/chapter2_literature_synthesis.md` (the intended new support document only).

### Source-verification addendum - CHAPTER-2-SOURCE-VERIFICATION-01

Source-level verification subsequently inspected full text for Spracklen et al. (2025), Al-Zofi (2025), Gao et al. (2025), Ladisa et al. (2023), Duan et al. (2020), Williams et al. (2025), Zhao et al. (2025), Tian et al. (2025), Liu et al. (2026), Woesle et al. (2025), and Twist et al. (2026). It strengthens the synthesis for bounded claims about code/package hallucination, supply-chain context, naming-attack distinctions, validation approaches, and cross-study comparison dimensions. It also establishes that the baseline’s Spracklen 19.7% figure used 2.23 million recommended packages as its denominator, not 576,000 code samples; all unverified baseline numbers remain excluded. See `chapter2_source_verification.md` for source-specific evidence, constraints, and the **READY_WITH_RESTRICTED_CLAIMS** drafting verdict. This addendum preserves the original reconciliation assessment rather than silently rewriting it.

## Reference-Coverage Requirement for Final Chapter 2

The final Chapter 2 must cite all **34** references in `docs/references/approved_references.md` at least once. This is a coverage requirement, not a direction to assign equal argumentative weight. **Reference coverage is required, but citation frequency follows evidentiary relevance, not equal distribution.** The 11 full-text-verified sources carry the central analytical argument and may be used more than once where their evidence directly supports distinct arguments. The 22 non-Gandhi metadata-only sources receive one conservative, contextual use each; their approved metadata does not establish an empirical result, percentage, causal conclusion, or comparative superiority.

| Coverage group | References and planned use |
|---|---|
| Repeated direct evidence | Spracklen et al. (2025) (4); Al-Zofi (2025) (3); Gao et al. (2025), Duan et al. (2020), Zhao et al. (2025), Ladisa et al. (2023), Liu et al. (2026), Tian et al. (2025), Twist et al. (2026), Williams et al. (2025), and Woesle et al. (2025) (2 each). |
| One-time contextual coverage | Agarwal et al. (2024); Daoud (2026); Dubey and Madisetti (2026); Jain et al. (2025); AlSobeh et al. (2025); Le-Anh et al. (2026); Li et al. (2026); Lian et al. (2024); Liu (2026); Liu et al. (2025a); Liu et al. (2025b); Ohm and Stuke (2023); Pashchenko et al. (2022); Qu et al. (2026); Tileria et al. (2026); Tripathi et al. (2025); Wang et al. (2025); Washio and Miyao (2022); Yadav et al. (2026); Yang et al. (2026); Zheng et al. (2026); Zhuo et al. (2025). |
| Conditional coverage | Gandhi (2026): planned once in Section 2.7 for broader autonomous-development security-risk context, but its in-text citation is blocked pending bibliographic reconciliation. The baseline says Gandhi (2025), whereas the approved list says Gandhi (2026). |

The source-strength hierarchy and complete section allocation are recorded in `chapter2_reference_coverage_plan.md`. Cross-ecosystem and agentic/mitigation literature may remain as contextual literature where safely supported, but must not be described as performed Java/Maven, PyPI, Python, autonomous-agent, mitigation, or other non-Node.js/npm experimental variables. No final claim may be invented from metadata-only sources.
