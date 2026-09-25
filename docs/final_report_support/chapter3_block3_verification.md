# Chapter 3 Block 3 Verification

## 1. Verification Scope

`CHAPTER-3-BLOCK3-VERIFICATION-01` reviewed Sections 3.10 to 3.16 of `docs/report_drafts/chapter3_sections_3_10_to_3_16.md`. The review used the controlling project instructions, report-generation protocol, current status, progress log, final-paper notes, decisions D032, D033, D036, and D037, the analysis specification, the Chapter 3 reconciliation, and the verified Blocks 1 and 2. It also inspected PIPE-06 through PIPE-10 implementations, their available schemas and synthetic-fixture tests, the risk protocol, and the validation record. Frozen implementation and finalised decisions governed where an earlier prose source differed.

The review checked definitions, eligibility and denominator rules, secondary-state resolution, statistical selection, risk scoring, validation wording, integrity and safety claims, limitations, cross-block table and figure numbering, style, and final-result leakage. No frozen input, raw observation, collection state, derived result, or collection code was changed.

## 2. Overall Verdict

**PASS_WITH_CORRECTIONS.** The draft accurately represented the implemented primary and secondary metric constructs, PIPE-09 comparison paths, `risk-model-1.0.0`, and the documented synthetic-fixture validation boundary. Two minor evidence-backed corrections were applied: explicit all-zero and all-one statistical-path behaviour was added, and the Chapter 4 transition was made expressly conditional on completion of final collection and analysis. No empirical result, current collection count, ranking, or obsolete methodology was found in the draft.

## 3. Primary Metrics Verification

The PHR definition was verified against D033, D037, PIPE-07, and PIPE-08. Its unit is one metric-eligible unique `(run_id, normalized_package)` row. PIPE-08 counts every such eligible row in the denominator and counts only rows whose PIPE-07 `primary_confirmed_hallucination` field is true in the numerator. PIPE-07 admits confirmation exactly once through either a supported PIPE-05 reviewed confirmation or a guarded PIPE-05B confirmation from a review-required, ambiguous source row. Duplicate, unmatched, malformed, inconsistent, or dual-route evidence fails closed.

The draft correctly explained that repeated occurrences in one response do not inflate PHR, whereas the same package in different responses forms separate units. It also correctly retained unadjudicated `REVIEW_REQUIRED` rows, PIPE-05B `UNRESOLVED` rows, registry-unresolved rows, and self or local rows in the primary PHR denominator while excluding them from its numerator. `external_dependency_eligible` affects D036 resolution only and does not alter the D033 primary denominator. Completed zero-package responses create no PHR package row; truncated and failed responses are metric-ineligible and do not contribute eligible package rows.

The SHR definition was likewise verified. PIPE-08 aggregates the same controlled confirmation field by response and counts an eligible response once when at least one package row is primary-confirmed. Its denominator is every metric-eligible completed response, including completed zero-package responses. Truncated and failed responses are excluded. PIPE-08 produces rates as `null` rather than zero when a primary denominator is zero. It does not calculate confidence intervals for PHR or SHR; the draft does not claim that it does.

## 4. Secondary Metrics Verification

The DFR and RDFR account matched D036 and PIPE-10. DFR is explicitly described as an exact-name npm dependency-resolution measure, not as a hallucination rate or a complete measure of dependency reliability. The draft correctly states the fixed package states: `F` for `EXTERNAL_FAILURE`, `N` for `EXTERNAL_NON_FAILURE`, and `U` for `UNDETERMINED`. `NOT_EXTERNAL` rows are excluded from the DFR point-estimate numerator and denominator. The point estimate is `F / (F + N)` and is `null` where that denominator is zero. When `U` is present, PIPE-10 reports lower `F / (F + N + U)` and upper `(F + U) / (F + N + U)` bounds; Wilson 95% intervals accompany estimable point estimates.

The draft correctly reflects the D036 resolution order. Auto-valid rows are external non-failures. Review-required rows with an appropriate PIPE-05B record become external failures, external non-failures, non-external rows, or undetermined according to the adjudicated eligibility and dependency-failure fields. Missing adjudication, registry unresolved evidence, reviewed ambiguity, and PIPE-05B unresolved evidence are undetermined rather than assumed failures or non-failures. Unsupported combinations fail closed.

RDFR response-state precedence was accurate: a response with any external failure is `POSITIVE`; otherwise a response with any undetermined state is `INDETERMINATE`; otherwise it is `NEGATIVE`. This correctly handles mixed failure and undetermined rows, zero-package responses, and self/local-only responses. The point estimate is `P / (R - I)`, equivalently positive responses divided by positive plus negative responses, and is `null` at a zero denominator. Bounds use `P / R` and `(P + I) / R` when indeterminate responses exist. The draft also correctly states that the final-label completeness gate requires zero `UNADJUDICATED` and zero `REGISTRY_UNRESOLVED` counts; PIPE-05B unresolved cases can remain terminal undetermined states while bounds disclose their uncertainty.

## 5. Statistical Analysis Verification

PIPE-09 was verified as producing grouped descriptive PHR and SHR summaries, and comparisons of their two binary outcomes only: package-level confirmed versus not confirmed and response-level contains-confirmed versus not. It does not calculate grouped DFR or RDFR. The permitted grouping dimensions are model condition, task category, repetition, and model condition by category. The draft accurately presents descriptive summaries before conditional inference and does not imply rankings.

For exactly two usable groups, PIPE-09 uses two-sided Fisher's exact test and reports an odds ratio with a 95% Wald log-odds confidence interval and a risk difference with a 95% Newcombe/Wilson-score confidence interval. The Haldane-Anscombe correction is applied only when a zero cell would otherwise make the odds ratio or its variance undefined.

For more than two usable groups, PIPE-09 applies a Pearson chi-square test only when every expected cell count is at least five. Otherwise it uses the deterministic fixed-margin two-by-C permutation procedure. The default procedure uses 20,000 iterations and seed `1234567891`; its statistic is the chi-square-style statistic recomputed under the fixed-margin permutations. All pairwise comparisons among usable groups use Fisher's exact test, and the Holm adjustment family is the complete set of those pairwise raw p-values within that omnibus comparison. The applied correction preserves the input ordering after step-down adjustment.

Groups with zero denominators are recorded as excluded. Fewer than two groups with non-zero denominators yields `not_testable`; a direct two-group comparison with a zero total also yields `not_testable`. All-zero or all-one outcome patterns in otherwise usable groups are not automatically non-testable: Fisher remains available for two groups, while zero expected cells send a multi-group table to the Monte Carlo path. When the fixed margins permit only one table, that procedure returns statistic zero and p-value one. The amended draft now states these rules without describing non-testable cases as non-significant.

## 6. Risk Framework Verification

Section 3.13 matches PIPE-06 and `risk-model-1.0.0`: Impact ranges from 1 to 5, Detectability from 1 to 4, and the deterministic score is their product. The bands are `LOW` for 1 to 4, `MODERATE` for 5 to 8, `HIGH` for 9 to 14, and `CRITICAL` for 15 to 20. The displayed matrix conforms to these component ranges and the band boundaries.

The draft correctly places scoring after classification and limits it to eligible confirmed hallucination findings with resolved evidence. PIPE-06 rejects scores and component rationales for ineligible or evidence-unresolved findings, emitting `null` fields rather than zero. It requires source evidence, expected consequence, impact and detectability rationales, assessor identifier, UTC assessment time, and provenance. `security_sensitive_context` is a required Boolean with a rationale, remains separate from the formula, and does not alter the score. Detectability is described as the earliest likely detection control, not as a probability.

The draft correctly identifies the framework as an ordinal prioritisation aid. It does not describe it as predictive, nor as an estimate of exploitation, installation, malicious registration, financial loss, or real-world incident probability. The old risk scheme is not used. Figure 3-5 correctly describes the score pathway and separate context field.

## 7. Validation and QA Verification

The validation claims match `FINAL-ANALYSIS-VALIDATION-01` in the progress log and are accurately limited to synthetic-only fixtures. The focused adjudication plus PIPE-07, PIPE-08, PIPE-09, and PIPE-10 suites recorded 126 passing tests. The PIPE-07 and PIPE-10-focused subset recorded 44 passing tests. The full suite result was 327 passing tests with two known historical freeze-test failures, rather than a 327-test run with no failures. The missing fixtures were four expected v2.1 `API-v2.1-*` raw directories and eight expected v2.3 `API-v2.3-*` raw directories. The recorded verdict was `PASS WITH DOCUMENTED LIMITATIONS`.

The draft accurately describes the scope as pipeline implementation, decision logic, derived-analysis reconciliation, provenance checks, and fail-closed safeguards. It does not imply validation of final empirical findings, adjudicative expertise, inter-rater agreement, Cohen's Kappa, predictive accuracy, temporal validity, or wider-population model performance. Test counts are not presented as a quality score.

## 8. Integrity / Safety / Limitations Verification

The integrity and safety wording was supported by the freeze, collection, inventory, analysis, registry, and risk-scoring controls. The draft correctly describes frozen and hash-controlled inputs, preserved raw evidence, derived overlays rather than raw rewrites, provenance-bearing derived transformations, fixed denominators, no outcome-dependent substitution, and separation of interim from final analysis. Its description of raw immutability is appropriately framed as a preservation and append-only principle rather than a claim of an unqualified filesystem enforcement mechanism.

The safety boundary accurately states that generated dependencies were neither installed nor executed; registry queries were read-only; no names were claimed, registered, reserved, or published; and no active exploitation was conducted. The stated rationale is consistent with the defined package-reference validation construct.

The limitations are implementation-specific and suitable for Chapter 3: Node.js/npm scope, the bounded 30-task/four-condition/three-planned-repetition design, uncalibrated medium difficulty, direct supported explicit forms, excluded narrative and transitive analysis, unsupported extraction forms, absence of execution, functional, API/capability, and version-level evaluation, time-bounded registry evidence, uncontrolled provider-side serving/versioning, hybrid-interface considerations, possible unresolved adjudications, the rule-based risk framework, and limited generalisability. They do not make discussion-style empirical claims reserved for Chapter 5.

## 9. Figure and Table Numbering

Figure numbering is consistent across all three Chapter 3 blocks: Figure 3-1 is the frozen task-condition-repetition design; Figure 3-2 the final v2.6 workflow and preservation boundary; Figure 3-3 the extraction, registry-evidence, and adjudication pipeline; Figure 3-4 the derivation of primary and secondary metrics; and Figure 3-5 the `risk-model-1.0.0` framework.

Table numbering is consecutive without duplication: Tables 3-1 to 3-4 appear in Block 1, Tables 3-5 to 3-10 in Block 2, and Tables 3-11 to 3-14 in Block 3. No cross-block renumbering is required.

## 10. Final-Result Leakage Check

No final empirical PHR, SHR, DFR, RDFR, package total, response total, group result, p-value, odds ratio, risk distribution, ranking, or current collection count appears in the reviewed draft. The only numerical material consists of methodological constants, score ranges, confidence levels, Monte Carlo settings, and documented validation-test counts. The final Chapter 4 transition is conditional on completion of final collection and analysis.

## 11. Issues Found

1. The original statistical prose did not state the implemented treatment of all-zero and all-one outcomes in otherwise non-empty groups. Without this, readers could incorrectly infer that such cases were necessarily `not_testable`.
2. The Chapter 4 transition used a future-oriented phrase that was acceptable but less explicit than the repository status requires about completion of final collection and analysis.

## 12. Corrections Applied

1. Added evidence-backed PIPE-09 wording to Section 3.12: all-zero and all-one outcomes retain the applicable Fisher or Monte Carlo path; only specified denominator and usable-group conditions return `not_testable`.
2. Revised the Section 3.16 transition to: “Chapter 4 reports the verified empirical results after completion of the final collection and analysis process.”

## 13. Remaining Restrictions

Final v2.6 collection and provenance-consistent final analysis remain incomplete. No final rate, outcome total, grouped comparison, p-value, ranking, risk distribution, or final empirical conclusion may be added until final data, adjudication, and analysis evidence exist. DFR and RDFR must remain labelled secondary/exploratory and must not be used as hallucination rates. Any future report amendment must preserve the frozen inputs, raw evidence, eligibility rules, and controlled D037 routing.

Progress-log update needed: **NO**. Final-paper note needed: **NO**. Draft reconciliation needed: **YES**; this verification report is the required block-level reconciliation record.

## 14. Evidence Index

| Evidence | Verified use |
| --- | --- |
| `docs/decision_log.md` D032, D033, D036, D037 | Controlling risk, primary metrics, secondary states, denominator rules, and confirmation routing |
| `scripts/build_analysis_dataset.py`; `scripts/calculate_primary_metrics.py`; PIPE-07/08 schemas and tests | Primary eligibility, uniqueness, D037 fields, cross-validation, PHR and SHR aggregation, zero-denominator behaviour |
| `scripts/calculate_dependency_reliability_metrics.py`; PIPE-10 tests | DFR/RDFR state resolution, precedence, bounds, intervals, completeness gate, and fail-closed handling |
| `scripts/analyze_group_comparisons.py`; `tests/test_analyze_group_comparisons.py` | Allowed groups, descriptive PHR/SHR output, comparison selection, Cochran threshold, Monte Carlo procedure, pairwise Fisher tests, Holm adjustment, confidence intervals, and testability behaviour |
| `docs/risk_assessment_protocol.md`; `scripts/score_risk_findings.py`; `schemas/risk_finding_pipe06_v1.schema.json`; PIPE-06 tests | Risk eligibility, component ranges, bands, null treatment, rationales, assessor and provenance fields, and security-context semantics |
| `docs/research_progress_log.md` `FINAL-ANALYSIS-VALIDATION-01`; `docs/current_research_status.md` | Synthetic-fixture validation counts, historical-fixture limitation, readiness verdict, and final-results-pending boundary |
| `docs/report_generation_protocol.md`; methodology reconciliation; Blocks 1 and 2; all Chapter 3 draft blocks | Report constraints, cross-block consistency, figure and table sequence, and prohibition of result leakage |
