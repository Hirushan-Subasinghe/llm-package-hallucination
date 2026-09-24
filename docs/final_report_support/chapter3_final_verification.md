# Chapter 3 Final Assembly Verification

## 1. Assembly Scope

`CHAPTER-3-FINAL-ASSEMBLY-01` assembled the three verified Chapter 3 methodology blocks into one authoritative draft. The assembly preserved verified substantive methodology and made only boundary-level edits required for cross-block consistency.

## 2. Source Blocks

- `docs/report_drafts/chapter3_sections_3_1_to_3_4.md`
- `docs/report_drafts/chapter3_sections_3_5_to_3_9.md`
- `docs/report_drafts/chapter3_sections_3_10_to_3_16.md`

The supporting verification records reviewed were `chapter3_block1_verification.md`, `chapter3_block2_verification.md`, `chapter3_block3_verification.md`, and `chapter3_methodology_reconciliation.md`.

## 3. Overall Verdict

**PASS.** The assembled chapter contains one Chapter 3 heading and complete Sections 3.1 through 3.16 in sequence. It preserves the verified Node.js/npm methodology and contains no final empirical result values.

## 4. Section Coverage

Sections 3.1 through 3.16 are all present once and in numerical order. The source-block boundary before Section 3.5 and the boundary before Section 3.10 were normalised without duplicated chapter headings or omitted substantive text.

## 5. Figure Numbering

Five figure placeholders occur in first-appearance order:

1. Figure 3-1: Frozen task-condition-repetition design.
2. Figure 3-2: Final v2.6 experimental workflow and preservation boundary.
3. Figure 3-3: Direct npm extraction, registry evidence, and conservative adjudication pipeline.
4. Figure 3-4: Derivation of primary and secondary metrics.
5. Figure 3-5: `risk-model-1.0.0` Impact × Detectability framework.

All in-text references and placeholders use this sequence. No images were generated.

## 6. Table Numbering

The final table sequence is consecutive: Tables 3-1, 3-2, 3-3, 3-4, 3-5, 3-6, 3-7, 3-8, 3-9, 3-10, 3-11, 3-12, 3-13, and 3-14. Captions align with their respective sections. The tables contain methodology definitions, planned design constants, procedural settings, and risk thresholds only; they contain no final result values.

## 7. Terminology Consistency

The chapter uses the verified terms consistently: model condition; repetition; planned observation; collection route; collection status; analytical eligibility; unique `(run_id, normalized_package)`; confirmed package-name hallucination; PHR; SHR; DFR; RDFR; dependency failure; external dependency eligibility; registry evidence; adjudication; `risk-model-1.0.0`; Impact; Detectability; and `security_sensitive_context`.

The primary and secondary constructs remain distinct. In particular, registry `not_found` evidence is not itself a confirmed hallucination, and DFR/RDFR remain secondary dependency-reliability measures rather than hallucination rates.

## 8. Cross-Chapter Consistency

Repetition language uses separate fresh requests or repeated generations under frozen conditions and does not claim formal statistical independence. The residual description of v2.6 as a fresh independent experiment was changed to a fresh 360-observation experiment.

The difficulty statement now matches the corrected Chapter 1 boundary: tasks were designated medium difficulty during pre-freeze design using a qualitative study rubric; the designation was not externally calibrated and was not used as an analytical variable. It does not claim that difficulty was a field in the frozen task records.

## 9. Result-Leakage Check

**NO final-result leakage found.** The chapter contains no achieved-completion, failure, or truncation totals; package or hallucination totals; final PHR, SHR, DFR, or RDFR values; final p-values or odds ratios; outcome comparisons; or final risk distributions. Permitted methodological constants and documented synthetic-validation test counts remain.

## 10. Outdated-Methodology Check

**NO obsolete-methodology leakage found.** Java, Maven, PyPI, surveys, human participants, developer expertise, autonomous-agent comparisons, mitigation experiments, installation/execution, and related excluded methods appear only as explicit non-scope statements where mentioned. The chapter does not present them as performed methodology. It does not use the superseded 0–12 risk model, treat 404 as a hallucination, or label DFR/RDFR as hallucination rates.

## 11. Appendix Placeholders

Three occurrences of `[APPENDIX REFERENCE PENDING]` remain, at the task-list reference, frozen-digest reference, and manual-route operational-detail reference. No appendix number was invented.

## 12. Style Check

The chapter uses formal British-English dissertation prose and past tense for performed methodology. No em dashes were found. Direct whitespace checks found no trailing whitespace or tab characters. The assembly did not introduce duplicate chapter headings or excessive boundary repetition.

## 13. Corrections Applied During Assembly

1. Removed duplicate source-block chapter-heading risk by retaining one authoritative Chapter 3 title.
2. Restored and normalised the Section 3.5 and Section 3.10 boundaries in the assembled file.
3. Replaced the residual wording “fresh, independent 360-observation experiment” with “fresh 360-observation experiment”.
4. Aligned the task-difficulty wording with the pre-freeze qualitative-rubric, non-calibration, and non-analytical-variable boundary.
5. Retained the verified Figure 3-1 to Figure 3-5 and Table 3-1 to Table 3-14 sequences.

## 14. Remaining Restrictions

Final v2.6 collection, adjudication completion, and provenance-consistent final analysis remain outside Chapter 3 assembly. No final empirical count, rate, comparison, ranking, risk distribution, or outcome conclusion may be added to this chapter until verified final evidence exists. Appendix placeholders require resolution during final dissertation assembly.

Milestone assessment: progress-log update needed: **NO**. Final-paper note needed: **NO**. Draft reconciliation needed: **NO**; the assembly and this verification record complete the required final Chapter 3 reconciliation.

## 15. Evidence Index

| Evidence | Verified use |
| --- | --- |
| Three Chapter 3 source blocks | Authoritative verified methodology prose for Sections 3.1–3.16 |
| Block 1, Block 2, and Block 3 verification records | Block-level factual, terminology, figure/table, and result-boundary checks |
| `docs/final_report_support/chapter3_methodology_reconciliation.md` | Controlling scope, measurement, terminology, and obsolete-methodology reconciliation |
| `docs/decision_log.md` D032–D038 | Risk, primary/secondary metrics, eligibility, confirmation, and recovery decisions |
| `docs/current_research_status.md` and `docs/research_progress_log.md` | Final-results-pending and synthetic-validation boundaries |
| `docs/final_report_support/claims_evidence_matrix.md` | Chapter 3 claim traceability context |

## 16. Word Count

The assembled Markdown word count is **12,249**. The approximate prose word count, excluding headings, tables, display mathematics, and block-quoted figure placeholders, is **9,913**.

## 17. Word-Readiness Decision

READY_FOR_WORD

## Compact authoritative revision

The originally assembled Chapter 3 contained approximately 12.3k Markdown words and 14 tables. A subsequent presentation-focused condensation produced a compact draft, which was independently checked against the verified full methodology in `docs/final_report_support/chapter3_compact_equivalence_verification.md`.

The equivalence verification found no material methodology loss. All core methodology, including eligibility, metric denominators, classification and adjudication semantics, PIPE-09 selection, risk scoring, safety boundaries, and limitations, remained equivalent. One evidence-backed PHR-denominator clarification and one duplicate appendix-placeholder removal were completed before promotion.

The compact draft was promoted as the authoritative Chapter 3 under `CHAPTER-3-COMPACT-PROMOTION-01`. The authoritative chapter now contains 7,501 Markdown words, nine consecutively numbered tables, and all five approved detailed figure placeholders. Final-result leakage remains **NO**; obsolete-methodology leakage remains **NO**; and the em-dash count remains zero. The promotion recommendation was `REPLACE_FULL_WITH_COMPACT`.

Six `[APPENDIX REFERENCE PENDING]` placeholders remain, covering the full task list, frozen digests/template metadata, manual-route operational detail, request/recovery mechanics, registry timing/storage detail, and detailed adjudication records/checks. These retain audit-level material only; no core methodological definition is deferred to an appendix.

The current Word-readiness state remains:

READY_FOR_WORD

The existing restriction remains unchanged: final empirical results belong in Chapter 4 only after verified final analysis.
