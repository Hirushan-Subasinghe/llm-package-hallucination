# Chapter 2 Reference-Coverage Plan

## 1. Coverage policy

All 34 references in `docs/references/approved_references.md` require at least one planned in-text use in the final Chapter 2. Coverage does not change the approved-reference boundary and does not make a metadata-only record evidence for a detailed finding. The final prose must give each source a safe, topic-appropriate location, while reserving substantive definitions, empirical findings, comparisons, and security arguments for sources whose full text has been verified.

**Reference coverage is required, but citation frequency follows evidentiary relevance, not equal distribution.** The plan therefore assigns repeated meaningful uses to the 11 full-text-verified sources and one conservative contextual use to each metadata-only source. Gandhi (2026) is conditional on bibliographic reconciliation.

## 2. Source-strength hierarchy

1. **Direct analytical evidence — FULL_TEXT_VERIFIED:** Spracklen; Al-Zofi; Gao; Ladisa; Duan; Williams; Zhao; Tian; Liu et al. (2026); Woesle; Twist. These may support the verified claim wording in `chapter2_source_verification.md` and may be reused where the same evidence genuinely bears on more than one argument.
2. **Contextual metadata-only references:** the remaining approved sources other than Gandhi. Use once, only for a broad role indicated by the approved bibliographic metadata (for example, “related work has examined API-hallucination mitigation”). They must not be the sole evidence for a detailed finding, number, comparison, or causal conclusion.
3. **Conditional reference:** Gandhi (2026). The baseline uses Gandhi (2025), whereas the approved list records Gandhi (2026). It has a planned contextual location but is not citable in final prose until the approved citation year/identity is reconciled.

## 3. 34-reference citation coverage matrix

| Reference | Verification Level | Primary Chapter 2 Section | Secondary Section | Intended Claim/Role | Minimum Uses | Maximum Confidence | Restrictions |
|---|---|---|---|---|---:|---|---|
| Agarwal et al. (2024) | METADATA_ONLY | 2.2 | — | RELATED_WORK_CONTEXT: broad code-hallucination research | 1 | METADATA_CONTEXT_ONLY | One neutral related-work sentence; no results, taxonomy, or prevalence. |
| Al-Zofi (2025) | FULL_TEXT_VERIFIED | 2.4 | 2.5 | DEFINITION and SECURITY_CONTEXT: distinguish typosquatting, dependency confusion, and slopsquatting | 3 | FULL_TEXT_DIRECT | Slopsquatting is conditional downstream context; no attack occurrence in this study. |
| Daoud (2026) | METADATA_ONLY | 2.2 | — | RELATED_WORK_CONTEXT: security-related code hallucinations | 1 | METADATA_CONTEXT_ONLY | Do not report SLR findings or security rates. |
| Duan et al. (2020) | FULL_TEXT_VERIFIED | 2.3 | 2.6 | SECURITY_CONTEXT and VALIDATION_CONTEXT: package-manager supply-chain attacks and analysis approaches | 2 | FULL_TEXT_DIRECT | Its malicious-package result is not package hallucination and no number is used without its exact context. |
| Dubey and Madisetti (2026) | METADATA_ONLY | 2.7 | — | RELATED_WORK_CONTEXT: reliable/trustworthy LLM coding | 1 | METADATA_CONTEXT_ONLY | Do not state effectiveness of debugging or explainability techniques. |
| Gandhi (2026) | METADATA_ONLY | 2.7 | — | RELATED_WORK_CONTEXT: autonomous-development security-risk context | 1 after reconciliation | BIBLIOGRAPHIC_RECONCILIATION_REQUIRED | Baseline says 2025, approved list says 2026; do not insert an in-text citation until resolved; autonomy is not an experimental variable. |
| Gao et al. (2025) | FULL_TEXT_VERIFIED | 2.2 | 2.6 | CORE_EVIDENCE: code-hallucination reliability and validation framing | 2 | FULL_TEXT_DIRECT | No universal definition, causal account, or rate. |
| Jain et al. (2025) | METADATA_ONLY | 2.7 | — | RELATED_WORK_CONTEXT: API-documentation mitigation | 1 | METADATA_CONTEXT_ONLY | State only that related work has considered documentation-based mitigation; no effectiveness claim. |
| Zhao et al. (2025) | FULL_TEXT_VERIFIED | 2.5 | 2.6 | EMPIRICAL_PRIOR_WORK and VALIDATION_CONTEXT: package hallucination and testing | 2 | FULL_TEXT_DIRECT | Preserve its study-specific operational setting; do not conflate testing with this study’s adjudication. |
| AlSobeh et al. (2025) | METADATA_ONLY | 2.7 | — | RELATED_WORK_CONTEXT: defences concerning dependency hallucination | 1 | METADATA_CONTEXT_ONLY | Do not claim the defence works or was evaluated here. |
| Ladisa et al. (2023) | FULL_TEXT_VERIFIED | 2.3 | 2.4 | CORE_EVIDENCE and SECURITY_CONTEXT: OSS supply-chain attack taxonomy | 2 | FULL_TEXT_DIRECT | Broad context only; registry absence is not evidence of compromise. |
| Le-Anh et al. (2026) | METADATA_ONLY | 2.2 | — | RELATED_WORK_CONTEXT: repository-level code-generation context | 1 | METADATA_CONTEXT_ONLY | Do not derive repository-level findings for this study. |
| Li et al. (2026) | METADATA_ONLY | 2.7 | — | RELATED_WORK_CONTEXT: knowledge-graph API-hallucination mitigation | 1 | METADATA_CONTEXT_ONLY | No mitigation performance or causal claim. |
| Lian et al. (2024) | METADATA_ONLY | 2.6 | — | RELATED_WORK_CONTEXT: weaknesses/evaluation of automatic code generation | 1 | METADATA_CONTEXT_ONLY | Do not assert particular metrics or comparative outcomes. |
| Liu (2026) | METADATA_ONLY | 2.7 | — | RELATED_WORK_CONTEXT: pseudocode-oriented hallucination mitigation | 1 | METADATA_CONTEXT_ONLY | Mention only as complementary mitigation work. |
| Liu et al. (2025a) | METADATA_ONLY | 2.8 | — | COMPARATIVE_CONTEXT: detection-metric research in a different generation direction | 1 | METADATA_CONTEXT_ONLY | Do not transfer its prevalence/metric results to generated dependencies. |
| Liu et al. (2025b) | METADATA_ONLY | 2.7 | — | RELATED_WORK_CONTEXT: knowledge-injection API mitigation | 1 | METADATA_CONTEXT_ONLY | No effectiveness percentage or claim. |
| Liu et al. (2026) | FULL_TEXT_VERIFIED | 2.2 | 2.8 | CORE_EVIDENCE: code-hallucination categories and reliability context | 2 | FULL_TEXT_DIRECT | Do not use as a universal definition or model ranking. |
| Ohm and Stuke (2023) | METADATA_ONLY | 2.6 | — | VALIDATION_CONTEXT: practical supply-chain-attack detection | 1 | METADATA_CONTEXT_ONLY | Full text remains needed for any detailed detection-method claim. |
| Pashchenko et al. (2022) | METADATA_ONLY | 2.7 | — | RISK_CONTEXT: dependency-risk assessment as related context | 1 | METADATA_CONTEXT_ONLY | Do not equate vulnerability assessment with package hallucination. |
| Qu et al. (2026) | METADATA_ONLY | 2.7 | — | RELATED_WORK_CONTEXT: LLM coding-agent supply-chain risks | 1 | METADATA_CONTEXT_ONLY | One broad contextual mention only; no agentic finding or performed-agent implication. |
| Spracklen et al. (2025) | FULL_TEXT_VERIFIED | 2.5 | 2.8 | CORE_EVIDENCE and EMPIRICAL_PRIOR_WORK: package hallucination, repetition, model/ecosystem comparison | 4 | FULL_TEXT_DIRECT | Rates require exact study context; a hallucinated name is not confirmed exploitation. |
| Tian et al. (2025) | FULL_TEXT_VERIFIED | 2.6 | 2.2 | VALIDATION_CONTEXT: execution-based verification and limits of syntactic plausibility | 2 | FULL_TEXT_DIRECT | Clearly state that this dissertation did not execute generated code/dependencies. |
| Tileria et al. (2026) | METADATA_ONLY | 2.6 | — | RELATED_WORK_CONTEXT: API fact-checking | 1 | METADATA_CONTEXT_ONLY | No judge accuracy or validation finding. |
| Tripathi et al. (2025) | METADATA_ONLY | 2.7 | — | RELATED_WORK_CONTEXT: agentic-coder hallucination/reliability | 1 | METADATA_CONTEXT_ONLY | Do not claim agentic-system evidence or study relevance beyond context. |
| Twist et al. (2026) | FULL_TEXT_VERIFIED | 2.5 | 2.8 | EMPIRICAL_PRIOR_WORK and COMPARATIVE_CONTEXT: library hallucinations across prompts/models | 2 | FULL_TEXT_DIRECT | Python-library setting; numbers only with exact prompt/model context. |
| Wang et al. (2025) | METADATA_ONLY | 2.3 | — | BACKGROUND_ONLY: LLM supply-chain research agenda | 1 | METADATA_CONTEXT_ONLY | Do not infer an empirical attack result. |
| Washio and Miyao (2022) | METADATA_ONLY | 2.7 | — | RELATED_WORK_CONTEXT: API-documentation grounding | 1 | METADATA_CONTEXT_ONLY | No performance or mitigation-effect claim. |
| Williams et al. (2025) | FULL_TEXT_VERIFIED | 2.3 | 2.7 | CORE_EVIDENCE and RISK_CONTEXT: software supply-chain security directions | 2 | FULL_TEXT_DIRECT | Use for broad attack-surface/risk context, not package-hallucination prevalence. |
| Woesle et al. (2025) | FULL_TEXT_VERIFIED | 2.2 | 2.7 | BACKGROUND_ONLY: general LLM-hallucination review context | 2 | FULL_TEXT_QUALIFIED | No baseline self-verification-recall number; do not let it define code/package hallucination alone. |
| Yadav et al. (2026) | METADATA_ONLY | 2.7 | — | RELATED_WORK_CONTEXT: AI-assisted development as a supply-chain context | 1 | METADATA_CONTEXT_ONLY | No attack-surface conclusion or empirical result. |
| Yang et al. (2026) | METADATA_ONLY | 2.6 | — | RELATED_WORK_CONTEXT: hybrid hallucination detection | 1 | METADATA_CONTEXT_ONLY | No accuracy, design, or superiority statement. |
| Zheng et al. (2026) | METADATA_ONLY | 2.8 | — | COMPARATIVE_CONTEXT: cross-ecosystem Rust-crate research | 1 | METADATA_CONTEXT_ONLY | Cross-ecosystem context only; no Rust result or mitigation claim. |
| Zhuo et al. (2025) | METADATA_ONLY | 2.2 | — | RELATED_WORK_CONTEXT: API misuse/hallucination | 1 | METADATA_CONTEXT_ONLY | Do not report identification or mitigation results. |

## 4. Section-by-section reference allocation

### 2.1 Chapter Introduction

- **Primary references:** none required; introduce the chapter’s bounded scope.
- **Supporting references:** none required.
- **One-time contextual references:** none.
- **Do not use:** numeric prevalence claims or claims about this dissertation’s results.

### 2.2 Large Language Models in Software Development

- **Primary references:** Gao et al. (2025); Liu et al. (2026).
- **Supporting references:** Tian et al. (2025); Woesle et al. (2025).
- **One-time contextual references:** Agarwal et al. (2024); Daoud (2026); Le-Anh et al. (2026); Zhuo et al. (2025).
- **Do not use:** package-manager attack results as evidence of ordinary code-generation reliability; agentic/security sources as experimental context.

### 2.3 Software Dependency Ecosystems and Package Registries

- **Primary references:** Ladisa et al. (2023); Duan et al. (2020); Williams et al. (2025).
- **Supporting references:** Spracklen et al. (2025).
- **One-time contextual references:** Wang et al. (2025).
- **Do not use:** metadata-only mitigation papers as registry-architecture evidence, or a time-sensitive npm package count.

### 2.4 Software Supply-Chain Threats Related to Package Naming

- **Primary references:** Al-Zofi (2025); Ladisa et al. (2023); Duan et al. (2020).
- **Supporting references:** Spracklen et al. (2025); Williams et al. (2025).
- **One-time contextual references:** none; substantive distinctions should remain with verified sources.
- **Do not use:** a claim that any observed absent name constitutes typosquatting, dependency confusion, malicious registration, or exploitation.

### 2.5 Package Hallucination in LLM-Generated Code

- **Primary references:** Spracklen et al. (2025); Zhao et al. (2025); Twist et al. (2026); Al-Zofi (2025).
- **Supporting references:** Gao et al. (2025).
- **One-time contextual references:** none; contextual coverage is better placed in the narrower areas above and below.
- **Do not use:** unqualified baseline rates, claims of no prior research, or a description of slopsquatting as an observed outcome.

### 2.6 Detection, Validation, and Classification Approaches

- **Primary references:** Tian et al. (2025); Zhao et al. (2025); Duan et al. (2020).
- **Supporting references:** Spracklen et al. (2025); Twist et al. (2026); Gao et al. (2025).
- **One-time contextual references:** Lian et al. (2024); Ohm and Stuke (2023); Tileria et al. (2026); Yang et al. (2026).
- **Do not use:** metadata-only work as direct evidence of detector accuracy; wording that registry absence itself confirms a hallucination; wording that this dissertation executed code.

### 2.7 Reliability, Security, and Risk Assessment

- **Primary references:** Williams et al. (2025); Ladisa et al. (2023); Al-Zofi (2025).
- **Supporting references:** Woesle et al. (2025); Spracklen et al. (2025).
- **One-time contextual references:** Dubey and Madisetti (2026); Gandhi (2026, pending reconciliation); Jain et al. (2025); AlSobeh et al. (2025); Li et al. (2026); Liu (2026); Liu et al. (2025b); Pashchenko et al. (2022); Qu et al. (2026); Tripathi et al. (2025); Washio and Miyao (2022); Yadav et al. (2026).
- **Do not use:** mitigation efficacy claims, predictive-risk claims, or agent autonomy as a performed study factor.

### 2.8 Comparative Dimensions in Prior Research

- **Primary references:** Spracklen et al. (2025); Twist et al. (2026); Liu et al. (2026).
- **Supporting references:** Zhao et al. (2025); Tian et al. (2025).
- **One-time contextual references:** Liu et al. (2025a); Zheng et al. (2026).
- **Do not use:** rates across studies as directly comparable, or cross-ecosystem context as evidence that the performed study covered Python, Java/Maven, or Rust.

### 2.9 Synthesis of Literature and Research Gap

- **Primary references:** Spracklen et al. (2025); Zhao et al. (2025); Tian et al. (2025); Twist et al. (2026).
- **Supporting references:** Al-Zofi (2025); Gao et al. (2025); Duan et al. (2020); Ladisa et al. (2023); Williams et al. (2025).
- **One-time contextual references:** none; synthesize verified literature rather than re-cite for coverage.
- **Do not use:** “first,” “no prior work,” “unexplored,” “no benchmarks,” or “no detection methods” claims.

### 2.10 Chapter Summary

- **Primary references:** none required beyond a concise synthesis.
- **Supporting references:** none required.
- **One-time contextual references:** none.
- **Do not use:** new evidence, new numeric claims, or empirical findings from the present study.

## 5. High-frequency/core references

The 11 full-text-verified references are planned for multiple meaningful uses: Spracklen et al. (2025) (4); Al-Zofi (2025) (3); and Gao et al. (2025), Duan et al. (2020), Zhao et al. (2025), Ladisa et al. (2023), Liu et al. (2026), Tian et al. (2025), Twist et al. (2026), Williams et al. (2025), and Woesle et al. (2025) (2 each). These counts are ceilings for planned meaningful roles, not a directive to cite a source mechanically.

## 6. Single-use contextual references

The 22 metadata-only sources with a safe one-time contextual role are Agarwal; Daoud; Dubey and Madisetti; Jain; AlSobeh; Le-Anh; Li; Lian; Liu (2026); Liu et al. (2025a); Liu et al. (2025b); Ohm and Stuke; Pashchenko; Qu; Tileria; Tripathi; Wang; Washio and Miyao; Yadav; Yang; Zheng; and Zhuo. Gandhi is separately conditional, rather than usable, pending citation reconciliation.

## 7. Numeric-claim restrictions

The source-verification review identifies **0 SAFE_TO_USE** numeric claims, **6 USE_ONLY_WITH_CONTEXT** claims, and **15 removed/unverified** numeric claims. Numbers are optional and should generally be omitted from Chapter 2.

If a contextual number is retained, it must reproduce the source population and setting. In particular, Spracklen et al.’s 19.7% figure is 440,445 of approximately 2.23 million recommended packages across 30 tests; 576,000 is the number of code samples, not its denominator. Its 5.2% and 21.7% values are commercial/open-source aggregates from that study, not universal rates. Twist’s 84.74% value and Duan’s 278/339 result likewise require their specified prompt/task and malicious-package-report contexts. No contextual number may be generalized to all LLM-generated code or the present experiment.

## 8. Gandhi bibliographic issue

`chapter2_literature_synthesis.md` records that the baseline Chapter 2 cites **Gandhi (2025)**, while the approved-reference list records **Gandhi (2026)**. The coverage status is **BIBLIOGRAPHIC_RECONCILIATION_REQUIRED**. Its planned location is Section 2.7 as one contextual sentence on broader autonomous-development security-risk literature; no final in-text citation should be inserted until the approved bibliography resolves the identity/year.

## 9. Citation-density rules

- Reference coverage is required, but citation frequency follows evidentiary relevance, not equal distribution.
- Reuse full-text-verified sources only where they directly support the paragraph’s distinct argument.
- Do not create citation-dense lists of five or six sources to satisfy coverage.
- Do not let metadata-only sources support strong claims, exact results, causal conclusions, superiority claims, or numbers.
- A conservative one-time pattern for metadata-only sources is: “Related work has also examined [broad topic indicated by the approved metadata] [Citation].”
- Cross-ecosystem work is literature context; it must never be represented as a Java/Maven, PyPI, Python, Rust, agentic, mitigation, or survey component of the performed Node.js/npm study.

## 10. Final drafting checklist

- [ ] Retain the approved 34-reference set without additions or removals.
- [ ] Ensure all 33 non-blocked references occur at least once and add Gandhi only after bibliographic reconciliation.
- [ ] Use the coverage matrix’s section and restriction for each citation.
- [ ] Keep detailed claims within the full-text-verified evidence summaries in `chapter2_source_verification.md`.
- [ ] Treat metadata-only sources as one-time contextual citations only.
- [ ] Exclude all unverified numeric claims; preserve full context for any of the six conditional numbers.
- [ ] State that cross-ecosystem material is context, while the implemented study is Node.js/npm-specific.
- [ ] Avoid broad novelty claims and do not portray validation, mitigation, autonomous agents, or security exploitation as performed elements of the study.
- [ ] Resolve Gandhi’s bibliographic year before inserting its final citation.

## Completion summary

- Total approved references: **34**.
- References with planned use: **34** (33 presently citable; Gandhi conditional on reconciliation).
- References planned for multiple use: **11**.
- References planned for single use: **22**.
- References blocked pending bibliographic reconciliation: **1** (Gandhi, 2026).
- References for which no academically safe use could be found: **0** (Gandhi has a conditional safe location only).
- Chapter 2 readiness: **READY_WITH_RESTRICTED_CLAIMS** for prose drafting, subject to the verification constraints and Gandhi reconciliation above.

## Pre-draft freeze addendum — CHAPTER-2-PRE-DRAFT-FREEZE-01

The Gandhi issue recorded in Section 8 is resolved. The baseline `IM2021101.pdf` reference list contains one Gandhi entry only, labelled `[Gandhi, 2026]` with year 2026 and the same TechRxiv DOI as approved entry 6; all 16 baseline in-text citations read `Gandhi, 2025`. This is an in-text citation-year mismatch only. Gandhi coverage status: **RESOLVED — USE Gandhi (2026)**. It moves from conditional coverage to one conservative metadata-only contextual use in Section 2.7 (23 single-use contextual references in total). LC19 remains `NOT_VERIFIABLE`, so no substantive agentic claim may rest on it. All 34 approved references are now citable within the restrictions above. Earlier sections are preserved as the pre-resolution record.
