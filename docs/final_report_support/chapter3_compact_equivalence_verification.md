# Chapter 3 Compact Equivalence Verification

## 1. Verification Scope

`CHAPTER-3-COMPACT-EQUIVALENCE-VERIFICATION-01` compared `docs/report_drafts/chapter3_compact_draft.md` with the verified full chapter at `docs/report_drafts/chapter3_complete_draft.md`. The review used the final assembly verification, visual/table/style review, methodology reconciliation, the three block verification records, current research status, and final-paper notes. The verified implemented v2.6 methodology governed wherever a wording choice required interpretation.

The review tested methodological equivalence rather than textual similarity. It assessed whether permissible compression retained the experimental design, scope, status and eligibility rules, direct-reference boundary, registry and adjudication semantics, primary and secondary metrics, PIPE-09 procedure, risk framework, validation boundary, safety restrictions, and material limitations. No frozen artefact, raw evidence, collection state, or full chapter text was modified.

## 2. Overall Verdict

**PASS AFTER MINOR EVIDENCE-BACKED CORRECTION.** The compact draft accurately retains the verified methodology in a shorter nine-table presentation. One clarification was required and applied: self/local package rows remain in the primary PHR denominator even though they are non-external for the secondary DFR boundary. One duplicate appendix placeholder was also removed. No material methodology was lost, and no final or interim result was introduced.

## 3. Section-by-Section Equivalence

| Section | Classification | Verification outcome |
| --- | --- | --- |
| 3.1 Chapter Introduction | EQUIVALENT_WITH_ACCEPTABLE_COMPRESSION | Retains the four-question context, frozen v2.6 boundary, evidence-to-interpretation separation, and no-results rule. |
| 3.2 Research Design | EQUIVALENT_WITH_ACCEPTABLE_COMPRESSION | Retains controlled repeated quantitative design, 30 × 4 × 3 planned structure, uncontrolled seed, non-independence caution, prospective rules, and derived-stage order. |
| 3.3 Experimental Scope and Study Variables | EQUIVALENT_WITH_ACCEPTABLE_COMPRESSION | Retains Node.js/npm scope, factors, controls, construct boundary, and prohibited non-scope methods. |
| 3.4 Task and Prompt Construction | EQUIVALENT_WITH_ACCEPTABLE_COMPRESSION | Retains balanced tasks/categories, qualitative medium-difficulty boundary, pre-freeze review, prompt freezing, manifest, and Figure 3-1. |
| 3.5 Model Conditions and Data Collection | EQUIVALENT_WITH_ACCEPTABLE_COMPRESSION | Retains frozen M1–M4 configuration, shared generation settings, hybrid assignment, non-substitution, preservation, and Figure 3-2. |
| 3.6 Response Preservation, Status, and Analytical Eligibility | EQUIVALENT | Retains COMPLETED, TRUNCATED, FAILED, derived status overlay, primary and secondary exclusion, and zero-package SHR treatment. |
| 3.7 Package Reference Extraction and Normalisation | EQUIVALENT_WITH_ACCEPTABLE_COMPRESSION | Retains direct explicit forms, normalisation, exclusions, occurrence provenance, and unique package unit. |
| 3.8 npm Registry Validation | EQUIVALENT_WITH_ACCEPTABLE_COMPRESSION | Retains read-only official npm validation, `exists`/`not_found`/`unresolved`, temporal evidence boundary, and non-confirmatory 404 semantics. |
| 3.9 Classification and Adjudication | EQUIVALENT_WITH_ACCEPTABLE_COMPRESSION | Retains conservative taxonomy, unresolved and self/local treatment, and controlled one-time confirmation routing. |
| 3.10 Primary Package-Hallucination Metrics | CORRECTION_REQUIRED, CORRECTED | PHR/SHR formulae and eligibility were retained. The compact draft was corrected to state explicitly that self/local rows remain in the primary PHR denominator. |
| 3.11 Secondary Dependency-Reliability Metrics | EQUIVALENT | Retains DFR/RDFR states, formulae, bounds, zero-package/self-local negative handling, and non-hallucination-rate limitation. |
| 3.12 Grouped and Statistical Analysis | EQUIVALENT | Retains all grouping dimensions and PIPE-09 selection, effect-size, confidence-interval, Monte Carlo, and Holm rules. |
| 3.13 Practical-Risk Assessment | EQUIVALENT | Retains `risk-model-1.0.0`, component ranges, multiplication, bands, separate security context, and non-probabilistic interpretation. |
| 3.14 Validation and Quality Assurance | EQUIVALENT_WITH_ACCEPTABLE_COMPRESSION | Retains synthetic-fixture scope, `PASS WITH DOCUMENTED LIMITATIONS`, correct test counts, and limitations of validation claims. |
| 3.15 Research Integrity, Safety, and Methodological Limitations | EQUIVALENT | Retains raw-evidence, safety, scope, construct, provider, registry, adjudication, risk, and generalisability limitations. |
| 3.16 Chapter Summary | EQUIVALENT_WITH_ACCEPTABLE_COMPRESSION | Accurately restates the boundaries without results and makes the Chapter 4 transition conditional on final provenance-consistent analysis. |

## 4. Design and Collection Equivalence

The compact chapter retains the Node.js/npm-only boundary, 30 frozen tasks, six five-task categories, four frozen conditions, three planned fresh generations, and the 360 planned-observation total. It retains the pre-freeze qualitative medium-difficulty designation and explicitly states that it was neither externally calibrated nor an analytical variable. The task and prompt account preserves deterministic rendering, frozen manifest controls, byte-identical task prompts across conditions, and the non-independence caution for repetitions.

The compact model table preserves all four frozen model identifiers, providers, routing constraints, and condition-specific token ceilings. It states temperature 0.6, top-p 0.95, uncontrolled seed, a fresh single-user-message interaction, and the absence of prior context, tools, browsing, retrieval, function calling, and execution. It correctly treats conditions as frozen model/API configurations rather than architecture comparisons.

The planned hybrid allocation remains 180 API and 180 manual rows. Assignment is explicitly distinct from analytical eligibility, including the prohibition on moving a failed API row to manual collection for a replacement. The compact draft retains sequential collection, evidence preservation, infrastructure-only retry, and the prohibition on content-driven regeneration, substitution, or fallback. It removes low-level retry and recovery implementation detail without changing those controls.

## 5. Eligibility Equivalence

The compact response-status table retains the verified three-state rule. `stop` defines COMPLETED, `length` defines TRUNCATED, and all other non-valid completion circumstances are FAILED. It preserves the abnormal-finish and interrupted-request treatment as failure, rather than treating partial text as a completed or truncated answer.

Only completed responses and their inherited package rows are eligible for primary and secondary point estimates. Truncated and failed responses remain preserved but are excluded from numerator and denominator. Completed zero-package responses create no PHR package row and remain negative SHR-denominator responses. The compact chapter therefore preserves the distinction among collection route, collection status, response eligibility, and package eligibility.

## 6. Extraction / Registry / Adjudication Equivalence

The direct-reference extraction boundary remains intact: literal ESM imports, CommonJS `require`, literal dynamic import, npm installation operands, and valid `package.json` dependency entries are supported. Narrative-only references and transitive dependencies are excluded, as are non-literal and other unsupported forms. The normalisation and exclusion rules retain built-ins, `node:`, relative/local/filesystem, `file:`, HTTP(S), aliases, and malformed-reference handling. The analytical package unit remains unique `(run_id, normalized_package)`, while occurrences remain provenance.

The registry stage remains read-only and limited to the official npm registry. It preserves `exists`, `not_found`, and `unresolved` as time-bounded evidence states. It correctly states that 404/`not_found` is not itself a hallucination classification.

The compact taxonomy retains VALID, confirmed hallucination, legacy/removed, namespace confusion, package-name confusion, invalid/redundant types package, ecosystem confusion, other dependency error, self/local package, and unresolved outcomes. It accurately requires response-internal evidence for `SELF_REFERENCE_OR_LOCAL_PACKAGE`; registry absence cannot establish that outcome. It also preserves a single controlled primary-confirmation resolution point, accepting an authorised reviewed confirmation or guarded adjudication confirmation once only. Unresolved, unadjudicated, duplicate, malformed, unmatched, or other non-confirming evidence remains outside primary numerators.

## 7. Primary Metric Equivalence

The compact PHR definition remains confirmed metric-eligible unique `(run_id, normalized_package)` rows divided by all metric-eligible unique package rows. SHR remains eligible completed responses containing at least one controlled confirmed hallucination divided by all eligible completed responses. The compact chapter retains the distinct package and response units, repeated-occurrence deduplication, zero-package SHR denominator, exclusion of truncated and failed responses, and controlled confirmation input.

The full chapter and Block 3 verification require self/local, unresolved, and other non-confirmed primary package rows to remain in the D033 PHR denominator, while the D034 external-dependency field affects only secondary analysis. The compact draft initially made the latter point but did not name self/local rows explicitly. It now does so. No denominator or numerator rule was changed.

## 8. Secondary Metric Equivalence

The compact draft retains DFR as `F / (F + N)`, with external failure F and external non-failure N. Undetermined U is excluded from the point estimate and is represented through lower and upper bounds. It retains Wilson 95% confidence intervals for estimable point estimates and the reason/outcome disclosure boundary.

It retains RDFR response precedence: any failure is POSITIVE; otherwise an unresolved package state makes a response INDETERMINATE; otherwise it is NEGATIVE. Completed zero-package and self/local-only responses are negative. Its point estimate remains `P / (R - I)`, with bounds for indeterminate responses. DFR/RDFR are clearly limited to exact-name dependency resolution and are labelled secondary/exploratory rather than hallucination rates. The compact chapter does not imply that they assess wrong-but-existing packages, version compatibility, APIs, capability, or functional suitability.

## 9. Statistical Method Equivalence

The compact draft retains descriptive primary-metric summaries by model condition, category, repetition, and model-condition-by-category combination. It retains the restriction of inference to binary primary outcomes and correctly says grouped DFR/RDFR comparison is not produced by PIPE-09.

It preserves the complete selection procedure: fewer than two usable groups is `not_testable`; two usable groups use two-sided Fisher's exact test; multi-group tables use Pearson chi-square only when every expected cell is at least five; otherwise they use the deterministic fixed-margin 2 × C Monte Carlo procedure with 20,000 iterations and seed `1234567891`. Pairwise Fisher tests use Holm adjustment. Odds ratios, risk differences, and 95% confidence intervals remain required reporting, including the Haldane-Anscombe and Newcombe/Wilson-score conditions. Zero-denominator and all-zero/all-one behaviour is accurately retained, and the compact chapter makes no best-model ranking claim.

## 10. Risk Framework Equivalence

The compact draft accurately retains `risk-model-1.0.0`. Impact is 1 to 5, Detectability is 1 to 4, and score equals Impact × Detectability. The bands remain LOW 1–4, MODERATE 5–8, HIGH 9–14, and CRITICAL 15–20. Scoring follows eligibility and confirmation, does not decide hallucination status, and records an unscored finding rather than a zero score where evidence is insufficient.

`security_sensitive_context` remains a separately rationalised, non-scored Boolean. The compact draft correctly rejects probability interpretations concerning exploitation, installation, package claiming, financial loss, and real-world incidents. It does not restore the superseded 0–12 model.

## 11. Validation / Safety / Limitation Equivalence

The compact draft accurately identifies `FINAL-ANALYSIS-VALIDATION-01` as `PASS WITH DOCUMENTED LIMITATIONS`, based on synthetic fixtures. It preserves the 126 focused passing tests, 44-test subset, and 327 passing tests with two known historical fixture failures. It correctly limits this evidence to implementation and rule validation, and does not claim expert, inter-rater, predictive, temporal, or final empirical validation.

The safety boundary remains equivalent: no generated dependency or code was installed or executed; registry requests were read-only; no package was claimed, registered, reserved, or published; and no active exploitation occurred. The compact limitations retain Node.js/npm scope; the bounded task-condition-repetition design; medium-difficulty qualification; direct-form, narrative, transitive, and unsupported-form boundaries; absence of version, functional, API, and capability testing; time-bounded registry evidence; uncontrolled provider-side behaviour/versioning; hybrid-collection consideration; possible unresolved adjudication; study-specific rule-based risk scoring; and limited generalisability.

## 12. Table Reduction Audit

The compact table sequence is consecutive from Table 3-1 to Table 3-9. The reduction is safe because the removed table slots were merged only where their substantive content remained directly available.

| Full table(s) | Compact treatment | Essential content retained |
| --- | --- | --- |
| 3-1 design summary and 3-2 RQ-method relationship | Merged into compact 3-1 | Design constants, primary/secondary outcomes, risk framework, and RQ coverage |
| 3-3 study variables | Removed as a standalone table | Factors, controls, outcomes, and scope appear in compact Section 3.3 prose and Tables 3-1 and 3-3 |
| 3-4 task categories | Retained as compact 3-2 | Six categories, five tasks each, and 360 planned total |
| 3-5 model conditions | Retained as compact 3-3 | Exact identifiers, providers, route constraints, and ceilings |
| 3-6 response status | Retained as compact 3-4 | Statuses, extraction, eligibility, and zero-package treatment |
| 3-7 extraction rules | Retained as compact 3-5 | Inputs, forms, normalisation, exclusions, and unique unit |
| 3-8 registry states, 3-9 classification routes, and 3-10 adjudication taxonomy | Merged into compact 3-6 | Evidence states, non-confirmatory `not_found`, final taxonomy, self/local, unresolved, and metric relevance |
| 3-11 primary metrics and 3-12 secondary states | Merged into compact 3-7 | PHR/SHR and DFR/RDFR definitions, units, eligibility, and state semantics |
| 3-13 PIPE-09 rules | Retained as compact 3-8 | Test selection, reporting, Monte Carlo, and Holm procedure |
| 3-14 risk matrix | Retained as compact 3-9 | Impact × Detectability matrix and score ranges |

No necessary methodological definition is dependent on a removed table alone.

## 13. Figure Placeholder Audit

All five approved detailed placeholders remain in their intended sections and are introduced by adequate surrounding prose:

1. Figure 3-1, frozen task-condition-repetition design, in Section 3.4.
2. Figure 3-2, final v2.6 workflow and preservation boundary, in Section 3.5.
3. Figure 3-3, direct npm extraction, registry evidence, and conservative adjudication pipeline, in Section 3.9.
4. Figure 3-4, derivation of primary and secondary metrics, in Section 3.10.
5. Figure 3-5, `risk-model-1.0.0` Impact × Detectability framework, in Section 3.13.

Their required content preserves the constraints against an independence claim, raw-evidence rewriting, direct 404-to-hallucination routing, conflating DFR/RDFR with hallucination rates, and probability-style risk interpretation.

## 14. Appendix Placeholder Audit

The compact candidate initially contained seven `[APPENDIX REFERENCE PENDING]` placeholders. The Section 3.2 freeze-metadata placeholder duplicated the more specific Section 3.4 digest/template reference and was removed. The revised compact chapter contains six placeholders, each justified by audit-level detail not required to define the main methodology.

| Compact location | Classification | Assessment |
| --- | --- | --- |
| Section 3.4 task list | Justified by removed audit-level detail | The main text retains category balance and task construction; the full list is supplementary. |
| Section 3.4 digests and template metadata | Justified by removed audit-level detail | The freezing and byte-identical prompt rules remain in the chapter. |
| Section 3.5 manual-route operational detail | Justified by removed audit-level detail | The 180/180 assignment and assignment-eligibility distinction remain in the chapter. |
| Section 3.5 request configuration and recovery mechanics | Justified by removed audit-level detail | Preservation, infrastructure-only retry, and no substitution remain in the chapter. |
| Section 3.8 registry retry and storage detail | Justified by removed audit-level detail | Official read-only validation and three evidence states remain in the chapter. |
| Section 3.9 detailed adjudication records and checks | Justified by removed audit-level detail | Taxonomy, evidence basis, self/local semantics, and controlled routing remain in the chapter. |

No core definition is deferred to an appendix and no appendix number was invented.

## 15. Style and Length Assessment

The revised compact draft is 7,501 Markdown words, within the requested approximate 7,500–8,500-word range. It uses formal, natural British-English academic prose, retains past-tense methodology, and is materially less software-documentation-oriented than the full draft. It has no em dash and no prose double hyphen. Direct whitespace checks found no adjacent blank lines, tabs, or trailing whitespace.

The compression remains readable: tables carry compact definitions, while prose supplies the distinctions necessary for interpretation. It does not rely on unexplained pipeline version strings or exhaustive file/schema mechanics.

## 16. Corrections Applied

1. In Section 3.10, added explicit wording that self/local package rows remain in the PHR denominator and outside its numerator. This aligns the compact chapter with D033/D034, the full chapter, and Block 3 verification.
2. Removed the duplicate Section 3.2 appendix placeholder for detailed freeze metadata. The specific Section 3.4 digest/template placeholder retains the supplementary reference without making core methodology appendix-dependent.

## 17. Remaining Restrictions

Final v2.6 collection, required adjudications, and provenance-consistent final analysis remain pending. Neither chapter version may receive final outcome counts, PHR/SHR/DFR/RDFR values, comparisons, p-values, rankings, risk distributions, or empirical conclusions until verified final evidence exists. The compact chapter must continue to preserve the Node.js/npm boundary, eligibility exclusions, conservative confirmation route, and no-installation/no-execution safety boundary.

Progress-log update needed: **NO**. Final-paper note needed: **NO**. Draft reconciliation needed: **NO**; this verification records the compact-equivalence review.

## 18. Evidence Index

| Evidence | Verified use |
| --- | --- |
| `docs/report_drafts/chapter3_complete_draft.md` | Full verified source for Sections 3.1–3.16 and Tables 3-1 to 3-14 |
| `docs/report_drafts/chapter3_compact_draft.md` | Compact candidate, corrected only as recorded in Section 16 |
| `docs/final_report_support/chapter3_final_verification.md` | Final chapter structure, terminology, figures, result boundary, and authorised methodology |
| `docs/final_report_support/chapter3_visual_table_style_review.md` | Approved figure content and full-table purpose audit |
| `docs/final_report_support/chapter3_methodology_reconciliation.md` | Scope, metric, eligibility, adjudication, risk, and limitation reconciliation |
| `docs/final_report_support/chapter3_block1_verification.md`, `chapter3_block2_verification.md`, and `chapter3_block3_verification.md` | Block-level factual verification of design, collection, metrics, statistics, risk, validation, and safety |
| `docs/current_research_status.md` and `docs/final_paper_notes.md` | Final-results-pending and report-boundary controls |
| `docs/decision_log.md` D033–D037 | Primary units and denominators, external-dependency boundary, failure handling, secondary metrics, and confirmation routing |

## 19. Authoritative-Replacement Recommendation

REPLACE_FULL_WITH_COMPACT
