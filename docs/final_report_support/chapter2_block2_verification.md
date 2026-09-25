# Chapter 2 Block 2 Verification — CHAPTER-2-BLOCK-2-VERIFICATION-01

**Reviewed draft:** `docs/report_drafts/chapter2_sections_2_5_to_2_7.md`  
**Scope:** Sections 2.5–2.7 only. No experimental, frozen, or raw-response file was inspected as literature evidence or modified.

## 1. Verification verdict

**PASS WITH MINOR CORRECTIONS**

The block is a coherent, evidence-aware synthesis. It retains the distinction between a literature-level package-hallucination definition and the dissertation's conservative confirmed-hallucination rule; does not report dissertation results; contains no numerical literature claims; and does not treat a registry `not_found` result as a final classification. Twelve bounded corrections are required before the block is used as the basis for Sections 2.8–2.10. They chiefly remove over-broad inference, mark dissertation reasoning as such, and keep metadata-only and title-only material contextual.

## 2. Citation-accounting result

| Measure | Independent result | Check against drafting summary |
|---|---:|---|
| Unique approved references cited in Sections 2.5–2.7 | **23** | Matches |
| FULL_TEXT_VERIFIED references cited in Block 2 | **9** | Matches |
| METADATA_ONLY references cited in Block 2 | **14** | Matches |
| References newly covered by Block 2 relative to Sections 2.1–2.4 | **15** | Consistent |
| Unique approved references in Sections 2.1–2.4 | **17** | — |
| Shared references between Blocks 1 and 2 | **8** | — |
| Cumulative unique Chapter 2 coverage through Section 2.7 | **32/34** | Matches |
| Approved references still unused | **2** | Matches |

The nine full-text-verified Block 2 references are Al-Zofi (2025), Duan et al. (2020), Gao et al. (2025), Ladisa et al. (2023), Spracklen et al. (2025), Tian et al. (2025), Twist et al. (2026), Williams et al. (2025), and Zhao et al. (2025). The 14 metadata-only references are Yang et al. (2026), Tileria et al. (2026), Lian et al. (2024), Pashchenko et al. (2022), Washio and Miyao (2022), Jain et al. (2025), Li et al. (2026), Liu et al. (2025b), Liu (2026), AlSobeh et al. (2025), Yadav et al. (2026), Gandhi (2026), Qu et al. (2026), and Tripathi et al. (2025).

## 3. Claim-verification table

`Line` refers to the reviewed working draft. “Context only” means that the prose is acceptable only if it remains explicitly framed as dissertation reasoning or bibliographic-topic context, rather than as a result of the cited literature.

| Line | Literature-backed or substantive claim | Classification | Verification finding / action |
|---:|---|---|---|
| 15 | Package hallucination is a recommendation/reference to a non-existent package. | DIRECTLY_SUPPORTED | Spracklen and Zhao directly support the literature-level definition. |
| 15 | Package hallucination is a dependency-reference manifestation of code hallucination. | SUPPORTED_WITH_QUALIFICATION | Safe as a conceptual relation; it must not substitute for the study's confirmed-hallucination rule. |
| 15 | Existence “can be established only” by a registry or index. | OVERSTATED | External authoritative evidence is needed, but documentation or other authoritative evidence can also bear on an identity/status question. Apply C01. |
| 17 | Syntactic plausibility is not evidence that a dependency reference is valid. | SUPPORTED_WITH_QUALIFICATION | Tian supports the general syntax/plausibility versus execution/requirements distinction; the dependency-specific application is sound synthesis. |
| 19 | Package hallucination is narrower than broader dependency error. | DIRECTLY_SUPPORTED | Consistent with Spracklen/Zhao’s non-existence construct and the stated boundaries. |
| 19 | A hallucinated reference “by definition, has no such [legitimate] target.” | OVERSTATED | Non-existence of the referenced name does not prove anything about a model's possible intended real-package analogue. Apply C02. |
| 21 | Twist operationalised library hallucination at library and library-member/interface levels, using package-index and documentation evidence. | DIRECTLY_SUPPORTED | Full-text verification supports the library/member distinction and validation description. |
| 25 | Spracklen, Zhao, and Twist studied package/library hallucination with differing designs. | DIRECTLY_SUPPORTED | The summary is accurate and retains setting-specific boundaries. |
| 25 | Twist varied time-related prompt phrasing. | DIRECTLY_SUPPORTED | Full text supports inclusion of a specified time-related prompt condition. No rate or broader effect is claimed. |
| 27–29 | Outcomes/dimensions differ by model, task/prompt, ecosystem, unit, and validation rule; rates are not transferable. | DIRECTLY_SUPPORTED | Directly supported by the differing inspected study designs. |
| 31 | Spracklen examined repetition and temperature; probabilistic generation contributed to output diversity in that study. | DIRECTLY_SUPPORTED | Correctly tied to that study, not universalised. |
| 31 | Empirical estimation “depends on repeated independent generation.” | SUPPORTED_WITH_QUALIFICATION | A reasonable methodological inference, but it should be stated as this study's design rationale, not an established requirement of the cited study. Apply C03. |
| 31 | Recurring names may be analytically/security relevant. | CONTEXT_ONLY | Safe dissertation synthesis if explicitly conditional; it is not a prevalence or exploitation finding. |
| 33 | Work in multiple settings shows package/library hallucination is not a phenomenon of one ecosystem. | SUPPORTED_WITH_QUALIFICATION | The studies cover multiple settings, but cannot establish a universal ecosystem claim. Apply C04. |
| 37–43 | Slopsquatting is a downstream malicious-registration/use scenario, not a synonym for hallucination or proof of exploitation. | DIRECTLY_SUPPORTED | Al-Zofi and Spracklen support the conditional attack sequence. |
| 39 | An unregistered hallucinated name results in a failed installation. | SUPPORTED_WITH_QUALIFICATION | True only at the relevant time and if installation is attempted; apply C05. |
| 41 | A registry observation is time-bounded evidence and does not establish past/future exploitation. | SUPPORTED_WITH_QUALIFICATION | Consistent with Spracklen and with the stated conditional attack model; retain time qualification. |
| 55 | Registry/reference checks and Duan's metadata/static/dynamic malicious-package analysis are distinct validation contexts. | DIRECTLY_SUPPORTED | Correctly distinguishes malicious-package work from hallucination work. |
| 55 | A registry is the external “source of truth.” | OVERSTATED | It is time-bounded external evidence, not a complete final classification source. Apply C06. |
| 57–59 | Extraction/normalisation choices affect which references are compared; absence alone does not settle classification. | DIRECTLY_SUPPORTED | Twist supports normalisation/over-counting context; the conclusion accords with the verified source constraints and dissertation taxonomy. |
| 63 | Tian’s execution-based verification addresses plausible code that fails execution/requirements. | DIRECTLY_SUPPORTED | Accurate. |
| 63 | Execution reveals failures “that no textual check would detect.” | OVERSTATED | The absolute is not established. Apply C07. |
| 65 | Yang, Tileria, and Lian are examples of detection/evaluation topic areas. | CONTEXT_ONLY | Their use remains at title/topic level; no technique property or result is attributed. |
| 67 | Executing generated code/dependencies may create a safe-handling concern for untrusted references. | CONTEXT_ONLY | Sound dissertation reasoning, but methodology-specific rationale belongs in Chapter 3. Apply C08. |
| 69 | Registry/reference, execution, testing, and malicious-package analysis answer different questions. | SUPPORTED_WITH_QUALIFICATION | Accurate high-level synthesis; retain the explicit separation of Duan's malicious-package setting. |
| 73 | Duan illustrates a distinction between automated candidate detection and subsequent confirmation. | DIRECTLY_SUPPORTED | Full text supports confirmation after automated malicious-package reporting. It must remain explicitly malicious-package context only; apply C09 for maximal precision. |
| 75–77 | Classification rules and unresolved cases affect reported figures; unresolved evidence should not be silently forced into a binary category. | SUPPORTED_WITH_QUALIFICATION | Sound synthesis grounded in heterogeneous constructs; Chapter 3 alone defines the final categories. |
| 79 | Timestamped evidence, recorded rules, and preserved responses support traceability/re-examination. | CONTEXT_ONLY | Appropriate methodological reasoning, but better placed in Chapter 3 or retained briefly as a forward reference. |
| 91 | An invalid/unavailable dependency reference can cause reliability failure, without itself establishing compromise. | SUPPORTED_WITH_QUALIFICATION | The conditional reliability framing is sound; failure should be tied to the time of attempted resolution. |
| 91 | Twist’s title framing as a “risk analysis” demonstrates a particular practical-developer concern. | UNSUPPORTED | Detailed inference from the title/risk framing exceeds the available verification record. Apply C10. |
| 93–95 | Security consequence is conditional on registration and subsequent action; a package name is not evidence of compromise. | DIRECTLY_SUPPORTED | Well supported and properly bounded. |
| 97 | Practical consequence can vary with a package's role/context. | CONTEXT_ONLY | Safe analytical reasoning if marked as such; not a reported literature finding or measured study result. |
| 101 | Consequence and detectability motivate a study-defined prioritisation frame. | SUPPORTED_WITH_QUALIFICATION | Broad concepts are supported, but immediate/deferred detection examples are analytical possibilities, not empirical findings. Apply C11. |
| 103 | Pashchenko is context for methodology concerning actually vulnerable dependencies, not hallucinations. | CONTEXT_ONLY | Correct title-level use and explicit construct distinction. |
| 105 | Impact × Detectability is this study's ordinal framework, not a literature standard or probability/loss model. | DIRECTLY_SUPPORTED | Correctly constrained by the implemented-study description; no results are claimed. |
| 109 | Mitigation/grounding work exists; this study evaluated none and makes no effectiveness claim. | SUPPORTED_WITH_QUALIFICATION | Safe, subject to the metadata-only audit below. |
| 111 | Gandhi/agentic literature is broad development-context material, not an autonomy variable in this study. | CONTEXT_ONLY | Gandhi year is correct and the citation occurs once. The final human-review/autonomy inference is unsupported by metadata-only sources; apply C12. |
| 113 | Reliability/security are conditional; consequence/detectability motivate, but do not define, the study framework. | SUPPORTED_WITH_QUALIFICATION | Keep as synthesis after C11/C12; it does not prestate a result. |

## 4. Twist-specific findings

1. **Library-member level:** supported. The use in Section 2.5.1 correctly says that Twist et al. (2026) addresses libraries and their members/interfaces and uses package-index/documentation validation. It appropriately distinguishes this construct from package-name existence.
2. **Time-related phrasing:** supported. Section 2.5.2 accurately reports that time-related prompt phrasing was among the conditions varied. It does not infer a direction, size, or general effect, and it includes no rate.
3. **“Risk analysis” framing:** insufficient for the detailed inference presently made in line 91. The fact that the title calls the work a risk analysis and is grounded in developer queries does not, without a verified result, establish a particular practical consequence or developer finding. C10 removes that inference while retaining the work as related context.

## 5. Duan-specific findings

The draft generally handles Duan et al. (2020) correctly. It identifies the work as **malicious-package/supply-chain research**, not package-hallucination research, and uses it to distinguish automated candidate identification from later confirmation/classification. It does not claim that package-hallucination studies universally require maintainer confirmation.

One wording correction (C09) makes that scope unmistakable and avoids the potentially imprecise phrase “registry maintainers.” No Duan numeric result is present.

## 6. Mitigation-claim audit

| Reference | Draft use | Audit result |
|---|---|---|
| Spracklen et al. (2025) | Discusses mitigation directions. | Acceptable: full-text verified, but no efficacy/result is claimed. |
| Gao et al. (2025) | Discusses mitigation directions within a review. | Acceptable: full-text verified and non-comparative. |
| Jain et al. (2025) | Topic-level API-documentation mitigation. | Acceptable metadata-only use; no effectiveness claim. |
| Li et al. (2026) | Topic-level knowledge-graph reasoning for API hallucination. | Acceptable metadata-only use; no measured benefit claimed. |
| Liu et al. (2025b) | Topic-level knowledge injection. | Acceptable metadata-only use; no measured benefit claimed. |
| Liu (2026) | Topic-level pseudocode intermediation. | Acceptable metadata-only use; no measured benefit claimed. |
| AlSobeh et al. (2025) | Topic-level proposed defences involving dependency hallucination. | Acceptable metadata-only use; no defence effectiveness claimed. |
| Tripathi et al. (2025) | Topic-level agentic-coder mitigation context. | Acceptable metadata-only use; no mitigation result or comparison claimed. |

The phrase “body of work” is acceptable as a description of the cited set, not as a prevalence claim. Keep the final two sentences of line 109, which expressly prevent an effectiveness inference.

## 7. Gandhi and metadata-only audit

**Gandhi:** The draft uses **Gandhi (2026)** exactly once, at line 111. It attributes no empirical result and says autonomy/agentic operation was not a dissertation variable. C12 removes the residual unsupported statement about differences in human dependency review.

| Metadata-only reference | Use remains topic/title level? | Finding |
|---|---|---|
| Yang et al. (2026) | Yes | “Hybrid approach” only; no accuracy/design claim. |
| Tileria et al. (2026) | Yes | “Fact-checking judge” only; no performance claim. |
| Lian et al. (2024) | Yes | Work on weaknesses only; no finding/comparison. |
| Pashchenko et al. (2022) | Yes | Methodology/counting topic only; construct difference explicit. |
| Washio and Miyao (2022) | Yes | Documentation-related topic only. |
| Jain et al. (2025) | Yes | Documentation mitigation topic only. |
| Li et al. (2026) | Yes | Knowledge-graph mitigation topic only. |
| Liu et al. (2025b) | Yes | Knowledge-injection topic only. |
| Liu (2026) | Yes | Pseudocode-intermediation topic only. |
| AlSobeh et al. (2025) | Yes | Proposed-defence topic only. |
| Yadav et al. (2026) | Yes | Title-level framing only. |
| Gandhi (2026) | Yes, after C12 | Survey topic only; no empirical inference. |
| Qu et al. (2026) | Yes | Attack-topic context only; no attack result. |
| Tripathi et al. (2025) | Yes | Mitigation/overconfidence topic only; no result. |

No metadata-only reference is used for an effectiveness, frequency, prevalence, causal, comparison, or measured-security-outcome claim.

## 8. Uncited-synthesis audit

| Analytical point | Decision | Required handling |
|---|---|---|
| Recurring package names may be analytically relevant. | **SAFE_AS_SYNTHESIS** | Retain only as a conditional dissertation observation (“may be relevant”); do not state recurrence frequency or security outcome. C03 makes this boundary clearer. |
| Execution-based validation may conflict with safe handling of untrusted dependencies. | **MOVE_TO_CHAPTER_3** | It is a study-method rationale, not a literature result. C08 replaces the paragraph with a short scope boundary and moves the rationale to Chapter 3. |
| Practical consequence depends on package role/context. | **SAFE_AS_SYNTHESIS** | Retain with “may vary” language and without presenting examples as observed cases or literature results. |
| Detectability may vary or be delayed. | **SAFE_AS_SYNTHESIS** | Retain as conditional reasoning, not a measured prior-literature result. C11 changes deterministic/likely wording to analytical possibilities. |

## 9. Risk-framework consistency

The block is consistent with the implemented study-defined framework after the required corrections:

- Line 105 clearly identifies **Impact × Detectability** as this study's rule-based ordinal practical-risk framework.
- It explicitly says the framework is not a cited-literature standard and does not measure exploitation probability, package-install probability, or realised loss.
- Chapter 2 motivates practical consequence and detectability only at a conceptual level.
- Eligible confirmed findings are referred to prospectively; no final finding, score, distribution, or result is stated.

## 10. Length and redundancy findings

Section 2.5 is slightly over the approximate target because the empirical-study synthesis and the subsequent comparison paragraph cover some of the same material.

- **Easiest safe cut — 2.5.2 paragraph 2 (line 27):** the statement that the studies treat outcomes in relation to model/task/ecosystem largely repeats the more precise comparison in line 29. Remove the final two sentences beginning “The designs of Spracklen…” and “This shared orientation…”, or reduce them to one transition sentence.
- **Further small reduction:** line 33 repeats Section 2.3.2's npm-only boundary and anticipates Section 2.8's comparative-ecosystem discussion. Retain one sentence stating that cross-ecosystem material is context, then move the detailed transferability discussion to Section 2.8.
- **Do not cut:** the conceptual distinction in 2.5.1, the conditional slopsquatting account, or the construct/unit/validation comparison in line 29. They are substantive and not duplicative.

**Recommendation:** **shorten Section 2.5 modestly**, because the identified repetition is real, not merely to reach a page target.

## 11. Required corrections with exact replacement wording

**C01 — line 15, external-evidence wording**

Replace:

> Whether a loop is correct can, at least in principle, be examined by reasoning about or running the code; whether a named package exists can be established only by reference to an external registry or index.

With:

> Whether a loop is correct can, at least in principle, be examined by reasoning about or running the code; assessing the status of a named package requires external authoritative evidence, such as the relevant registry or index.

**C02 — line 19, intended-target inference**

Replace:

> A misspelled reference to a real package points towards an identifiable legitimate target, whereas a hallucinated reference, by definition, has no such target.

With:

> A misspelled reference to a real package may point towards an identifiable legitimate target, whereas the literature-level package-hallucination construct concerns the non-existence of the referenced name.

**C03 — line 31, repetition as study rationale**

Replace:

> Methodologically, it implies that an empirical estimate depends on repeated independent generation under fixed conditions rather than on a single sample.

With:

> Methodologically, it supports treating repeated independent generation under fixed conditions as a more informative basis for an empirical estimate than a single sample.

**C04 — line 33, cross-ecosystem scope**

Replace:

> This work shows that package and library hallucination is not treated as a phenomenon of a single ecosystem, but it does not show that outcomes observed in one ecosystem will hold in another.

With:

> These studies examine package or library hallucination in more than one ecosystem setting, but they do not show that outcomes observed in one ecosystem will hold in another.

**C05 — line 39, time-bounded installation outcome**

Replace:

> If the name is not registered, the hallucinated reference remains a reliability defect: an installation attempt fails because the name does not resolve, or the reference is corrected before it is used.

With:

> If the name remains unregistered when it is acted upon, the hallucinated reference remains a reliability defect: an installation attempt would fail to resolve it, or the reference may be corrected before use.

**C06 — line 55, registry as evidence rather than complete truth**

Replace:

> Across these uses, the registry functions as the external source of truth that the generated code itself cannot supply.

With:

> Across these uses, the registry provides time-bounded external evidence about a dependency reference that the generated code itself cannot supply.

**C07 — line 63, execution claim**

Replace:

> Execution can reveal behavioural failures that no textual check would detect, and for this reason it complements reference-level validation.

With:

> Execution can reveal behavioural failures that a reference-level or textual check may not establish, and for this reason it can complement reference-level validation.

**C08 — lines 67–68, move execution-safety rationale to Chapter 3**

Replace the full paragraph beginning “Execution-based approaches carry a particular constraint…” with:

> Execution-based validation addresses a different question from the read-only registry evidence used in the present study. The present study neither installed packages nor executed generated code; its methodology and the resulting behavioural limitation are described in Chapter 3.

Add the omitted safe-handling rationale to Chapter 3 only when that chapter is drafted, as a study-design rationale rather than a literature finding.

**C09 — line 73, Duan scope precision**

Replace the final three sentences of the paragraph, beginning “In the study of Duan…” with:

> In Duan et al. (2020), automated analysis identified candidate malicious packages and subsequent maintainer confirmation did not confirm every reported candidate as malicious. This was malicious-package research, not package-hallucination research; it illustrates only that an automated signal and a confirmed classification are different kinds of statement.

**C10 — line 91, Twist risk-title inference**

Replace:

> The framing of Twist et al. (2026), who present their study of library hallucinations as a risk analysis grounded in developer queries, likewise indicates that hallucinated references are treated in the literature as a practical concern for developers and not only as a measurement outcome.

With:

> Twist et al. (2026) provide related research on library hallucinations grounded in developer queries. This review does not infer a particular practical consequence from the “risk analysis” framing in that work's title.

**C11 — line 101, detectability as conditional synthesis**

Replace the final three sentences of the paragraph, beginning “A hallucinated reference…” with:

> As a matter of dissertation reasoning, detectability may differ across references and use contexts. A reference that fails immediately on installation may be noticed earlier than one whose status becomes relevant only later in use; likewise, a registered name may remove an immediate resolution-failure signal. These are analytical possibilities that motivate attention to detectability, not measured outcomes reported by the cited studies.

**C12 — line 111, agentic-context boundary**

Replace the final two sentences of the paragraph, beginning “Their relevance…” with:

> They provide topic-level context for broader discussions of AI-assisted and agentic development. Autonomous or agentic operation was not a variable in the present study, and no empirical finding about such settings is drawn from these sources.

## 12. References still unused after Sections 2.5–2.7

1. **Liu et al. (2025a)** — planned for contextual comparison/detection-metric use in Section 2.8.
2. **Zheng et al. (2026)** — planned for cross-ecosystem contextual comparison in Section 2.8.

No unapproved references appear. The reviewed block uses Gandhi (2026), never Gandhi (2025); contains no Spracklen (2024), no Ohm et al. (2020), and no numeric literature claims.

## 13. Synthesis quality and readiness

The narrative synthesises rather than catalogues sources: it moves coherently from package-hallucination concepts, through validation/classification, to conditional reliability/security and a study-defined risk frame. Citation density is proportionate, and metadata-only sources are grouped in an explicitly limited contextual paragraph rather than used as evidence for detailed claims. It does not prematurely state Section 2.9's research-gap conclusion.

**Readiness:** **READY_AFTER_CORRECTIONS**

After C01–C12 are applied, Sections 2.8–2.10 may be drafted under the existing source-verification and coverage-plan constraints. In particular, the two remaining approved references must remain topic-level contextual citations in Section 2.8, and Section 2.9 must avoid novelty/absence assertions.

## 14. Milestone documentation assessment

- Progress-log update needed: **NO** — this is a requested verification artifact, not a research or methodology milestone.
- Final-paper note needed: **NO** — no final-study fact changed.
- Draft reconciliation needed: **NO** — no existing dissertation draft was rewritten; this report supplies exact corrections for later drafting action.
