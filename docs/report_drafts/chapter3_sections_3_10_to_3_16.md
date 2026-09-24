## 3.10 Primary Package-Hallucination Metrics

The primary analysis measured confirmed package-name hallucination at two complementary levels. The Package Hallucination Rate (PHR) was a package-level measure, whereas the Session Hallucination Rate (SHR) was a response-level measure. Both measures were calculated only after extraction, registry validation, classification, adjudication where required, and the controlled confirmation-resolution stage described in Sections 3.7 to 3.9. This ordering ensured that registry absence alone could not determine a primary outcome.

PHR used the following definition:

$$
\mathrm{PHR}=\frac{\text{confirmed hallucinated metric-eligible unique }(run\_id,\ normalized\_package)\text{ rows}}{\text{all metric-eligible unique package rows}}
$$

The package-level unit was a unique `(run_id, normalized_package)` pair. Thus, repeated references to the same normalised package in one response were counted once, while the same package in two different responses contributed two rows. This choice prevented response length, repeated imports, or repeated installation instructions from increasing either the numerator or denominator merely through repetition. Occurrence-level provenance was retained separately, so that deduplication did not remove the evidential trail for individual mentions.

SHR measured the proportion of eligible completed responses containing at least one confirmed hallucination:

$$
\mathrm{SHR}=\frac{\text{eligible completed responses containing at least one confirmed hallucination}}{\text{all eligible completed responses}}
$$

PHR therefore represented the frequency of confirmed hallucinated package recommendations among eligible unique package recommendations. SHR represented the frequency with which an eligible response contained any such finding. The measures should not be interpreted interchangeably: a response containing several distinct confirmed package hallucinations contributes several package rows to PHR but only one positive response to SHR.

**Table 3-11. Definitions and eligibility rules for the primary metrics**

| Metric | Analytical unit | Numerator | Denominator | Principal exclusions |
| --- | --- | --- | --- | --- |
| PHR | Unique `(run_id, normalized_package)` row | Metric-eligible rows with controlled confirmation of a package hallucination | All metric-eligible unique package rows | Package rows from failed or truncated responses |
| SHR | Completed response | Eligible completed responses with one or more controlled confirmed hallucinations | All eligible completed responses, including zero-package responses | Failed and truncated responses |

Metric eligibility was determined from the preserved response inventory. Completed responses with `finish_reason` `stop` were eligible, provided that the completion was valid; responses ending because of the output-length limit were retained as truncated and excluded. Failed responses, including abnormal provider terminations classified as failures, were also excluded. Package extraction was not performed for failed responses, and stale package rows associated with such responses were rejected by the analysis builder. These rules preserved the distinction between an observed incomplete response and an eligible response for rate estimation.

An eligible completed response with no extracted package references remained in the SHR denominator and contributed a negative response-level outcome. It did not contribute a package row to the PHR denominator because no package-level unit existed. This distinction was important because removing zero-package completions from SHR would have changed a response-level denominator according to whether a model happened to mention a package.

All metric-eligible unique package rows remained in the PHR denominator, including rows awaiting adjudication and rows adjudicated as unresolved. Such rows were not added to the numerator. In particular, an unadjudicated `REVIEW_REQUIRED` row or a PIPE-05B `UNRESOLVED` row did not become a non-hallucination by default, nor was it removed after observing its uncertainty. Counts for these states were retained separately to make denominator composition auditable. The external-dependency field used in the secondary analysis did not alter the primary PHR denominator.

Primary confirmation was resolved once, in the analysis-dataset construction stage. A row entered the PHR numerator, and caused its response to enter the SHR numerator, only when exactly one authorised route established `CONFIRMED_HALLUCINATION`: a supported reviewed classification from PIPE-05 or a guarded PIPE-05B confirmation originating from an ambiguous, review-required PIPE-05 row. The latter route required the prescribed resolved evidence, all confirmation checks, dated sources, provenance agreement, and route exclusivity. Duplicate, malformed, unmatched, or dual-route records failed closed. Outcomes such as legacy or removed packages, namespace or package-name confusion, ecosystem confusion, self or local references, other dependency errors, and unresolved cases were not primary confirmations.

> **[Figure 3-4 placeholder] Derivation of primary and secondary metrics.**
> Preserved response inventory and PIPE-07 eligibility → unique metric-eligible package rows and eligible completed response rows → controlled confirmed-hallucination field → PHR and SHR; separately, external failure, non-failure, and undetermined states → DFR and RDFR. The figure must show that DFR and RDFR are secondary dependency-reliability measures rather than hallucination rates.

## 3.11 Secondary Dependency-Reliability Metrics

The study also specified the Dependency Failure Rate (DFR) and Response Dependency Failure Rate (RDFR) as secondary, exploratory measures of exact-name npm dependency reliability. They were intentionally distinct from the primary hallucination measures. DFR measures exact-name npm dependency-resolution failures under the defined adjudication rules. It does not capture all forms of dependency unreliability, including wrong-but-existing packages, version-resolution errors, API errors, capability mismatches, or functional-unsuitability errors.

At the package level, the secondary procedure classified each metric-eligible unique package row as an external failure (`F`), an external non-failure (`N`), an undetermined case (`U`), or a non-external reference. An automatically valid registry result was an external non-failure. Resolved adjudication could establish an external failure or non-failure. Self or local references were recorded as non-external and were not included in the DFR calculation. Registry-unresolved rows, unadjudicated ambiguous rows, reviewed ambiguous rows, and PIPE-05B unresolved rows were undetermined rather than silently assigned to either resolved state.

The DFR point estimate was:

$$
\mathrm{DFR}=\frac{F}{F+N}
$$

Undetermined rows were excluded from this point-estimate denominator. Where undetermined rows existed, the procedure also produced bounds that treated all such rows as non-failures for the lower bound and as failures for the upper bound. Wilson 95% confidence intervals accompanied estimable point estimates. The output retained counts by undetermined reason and failures by adjudication outcome, allowing dependency failures to be described without re-labelling every failure as a confirmed hallucination.

RDFR translated these package states to the response level. An eligible completed response was `POSITIVE` if it contained at least one external dependency failure. If it contained no failure but retained one or more undetermined dependency states, it was `INDETERMINATE`. It was `NEGATIVE` only when it contained neither a failure nor an undetermined state. Accordingly, completed responses with zero extracted packages, and completed responses containing only self or local references, were negative for RDFR. Truncated and failed responses were excluded, consistently with the primary eligibility rule.

The RDFR point estimate was calculated as the number of positive eligible responses divided by eligible completed responses excluding indeterminate responses:

$$
\mathrm{RDFR}=\frac{P}{R-I}
$$

where \(P\) is the number of positive responses, \(R\) the number of eligible completed responses, and \(I\) the number of indeterminate responses. Wilson 95% confidence intervals were produced for estimable RDFR values. If indeterminate responses were present, lower and upper bounds used all eligible completed responses: the lower bound treated indeterminate responses as negative and the upper bound treated them as positive. A completeness gate labelled an output `FINAL` only when no review-required row was unadjudicated and no registry row remained unresolved; otherwise it was labelled `INTERIM_OR_INCOMPLETE`. This gate did not alter the calculated states, but prevented an incomplete evidence chain from being presented as final.

**Table 3-12. Secondary dependency-reliability states and their metric treatment**

| Level | State | Meaning | Treatment in point estimate |
| --- | --- | --- | --- |
| Package | `F` | External exact-name dependency failure | DFR numerator and denominator |
| Package | `N` | External exact-name dependency non-failure | DFR denominator only |
| Package | `U` | Dependency status undetermined | Excluded from DFR point estimate; included in bounds |
| Response | `POSITIVE` | At least one dependency failure | RDFR numerator and denominator |
| Response | `INDETERMINATE` | No failure, but at least one undetermined dependency status | Excluded from RDFR point estimate; included in bounds |
| Response | `NEGATIVE` | No failure or undetermined status, including zero-package and self/local-only responses | RDFR denominator only |

DFR and RDFR were secondary/exploratory dependency-reliability measures. They were not hallucination rates and did not replace, redefine, or modify PHR and SHR. In particular, an exact-name dependency failure could arise from a resolved non-hallucination category, while a primary confirmed hallucination required the stricter controlled confirmation route described in Section 3.10.

## 3.12 Grouped and Statistical Analysis

PIPE-09 produced grouped descriptive summaries before any inferential comparison. The predefined grouping dimensions were model condition, task category, repetition, and the model-condition-by-category combination. For each group, the procedure summarised the primary package-level and response-level counts and their denominators, while retaining counts of truncated and failed responses for transparency. This sequence ensured that the distribution and available denominators were inspected before a comparison method was selected.

The inferential component concerned two binary primary outcomes: confirmed hallucination versus not confirmed at package level, and whether an eligible completed response contained a confirmed hallucination at response level. It was conditional on sufficient usable data. It did not impose a model ranking, identify a best model, or turn the absence of a testable comparison into an inferential conclusion.

For a comparison containing exactly two non-empty groups, PIPE-09 used Fisher's exact test. It also reported an odds ratio and a risk difference, each with a 95% confidence interval. The odds-ratio calculation applied a Haldane-Anscombe correction only if a zero cell would otherwise make the odds ratio or its variance undefined. Risk-difference intervals used the Newcombe/Wilson-score approach. A group with a zero denominator made a direct two-group comparison not testable rather than supplying a numerical inference.

For comparisons with more than two non-empty groups, the procedure first evaluated the expected-cell assumptions for a chi-square test. Where the assumptions were met, it reported an omnibus chi-square result. Where sparse expected counts caused those assumptions to fail, it used a deterministic permutation-based Monte Carlo procedure for the two-by-C table, with 20,000 iterations and seed `1234567891`. The fixed iteration count and seed made the sparse-table procedure reproducible. The general procedure did not attempt unsupported higher-dimensional exact tests; cases outside the implemented two-outcome comparison structure were returned as `not_testable`.

When an omnibus multi-group comparison was applicable, pairwise two-group Fisher tests were also generated for the usable groups. Their p-values were adjusted with the Holm procedure to control the family-wise error rate across those pairwise comparisons. Groups with zero denominators were reported as excluded from the comparison, not treated as zero-risk groups. Where fewer than two groups had non-zero denominators, no comparison was testable. Where a result was `not_testable`, it was reported as such rather than described as statistically significant or non-significant.

All-zero and all-one outcome patterns in otherwise non-empty groups did not, by themselves, make a comparison untestable. For two usable groups, the Fisher path remained available and the zero-cell continuity correction was applied only to the odds-ratio estimate where necessary. For multi-group comparisons, a zero expected cell failed the chi-square assumption gate and therefore selected the deterministic Monte Carlo path; when the fixed margins permitted only one table, that procedure returned a statistic of zero and a p-value of one. These behaviours were reported as properties of the selected procedure, not as evidence of an effect or of equivalence.

**Table 3-13. PIPE-09 inferential selection rules**

| Comparison condition | Method | Supplementary reporting |
| --- | --- | --- |
| Fewer than two groups with non-zero denominators | `not_testable` | Reason and excluded zero-total groups |
| Exactly two usable groups | Fisher's exact test | Odds ratio, risk difference, and 95% confidence intervals |
| More than two usable groups; chi-square assumptions met | Omnibus chi-square test | Pairwise Fisher tests with Holm adjustment, effect estimates for pairs |
| More than two usable groups; chi-square assumptions not met | Deterministic 2 × C Monte Carlo permutation test | 20,000 iterations, seed `1234567891`; pairwise Fisher tests with Holm adjustment |

The resulting analyses were descriptive and, where estimable, comparative within the frozen study conditions. They were not designed to establish causal effects of model architecture, provider infrastructure, or task-domain properties. Statistical output was therefore interpreted together with denominators, effect estimates, confidence intervals, eligibility exclusions, and the bounded design rather than through p-values alone.

## 3.13 Practical-Risk Assessment

Practical-risk assessment used the transparent, rule-based `risk-model-1.0.0` framework after classification had established an eligible confirmed package-hallucination finding. It was not used to decide whether a finding was a hallucination. Consequently, a high score could not supply confirmation for an uncertain reference, and unresolved, valid, self or local, and other unconfirmed findings were not scored.

Each eligible finding received an Impact score from 1 to 5 and a Detectability score from 1 to 4. Impact represented the concrete consequence supported by the generated recommendation and documented task context, from negligible effect to a supported potential security, integrity, or software-supply-chain consequence. Detectability represented the earliest ordinary development control likely to reveal the particular issue, from immediately apparent during dependency resolution to difficult to identify without relevant package or domain knowledge. The numeric score was calculated deterministically:

$$
\text{Risk score}=\text{Impact}\times\text{Detectability}
$$

**Table 3-14. `risk-model-1.0.0` Impact × Detectability matrix**

| Impact \ Detectability | 1 | 2 | 3 | 4 |
| --- | ---: | ---: | ---: | ---: |
| 1 | 1 | 2 | 3 | 4 |
| 2 | 2 | 4 | 6 | 8 |
| 3 | 3 | 6 | 9 | 12 |
| 4 | 4 | 8 | 12 | 16 |
| 5 | 5 | 10 | 15 | 20 |

Scores of 1 to 4 were classified `LOW`, 5 to 8 `MODERATE`, 9 to 14 `HIGH`, and 15 to 20 `CRITICAL`. The assessment retained the impact and detectability rationales, source evidence, consequence statement, assessor and UTC assessment time, model version, and links to the relevant validation and classification provenance. When evidence was insufficient for scoring, the score and associated fields were recorded as `null`, not as zero. This distinction prevented an unscored finding from being represented as a finding with no risk.

`security_sensitive_context` was retained as a separate, non-scored Boolean field with a written rationale. It identified whether the confirmed finding affected security-relevant behaviour, such as authentication, authorisation, cryptography, secret handling, integrity enforcement, access control, or software-supply-chain trust. It did not change the numerical score unless an implementation rule expressly required that change; the implemented framework contained no such adjustment.

> **[Figure 3-5 placeholder] `risk-model-1.0.0` Impact × Detectability framework.**
> Eligible confirmed package-hallucination finding → documented impact (1–5) and detectability (1–4) rationales → deterministic product → LOW, MODERATE, HIGH, or CRITICAL band. `security_sensitive_context` is recorded alongside, but outside, the calculation.

The framework was an ordinal prioritisation aid, not a probability model. It did not estimate exploitation probability, installation probability, malicious-registration probability, financial loss, or real-world incident probability. It likewise did not use the superseded four-factor, 0–12 scoring approach. The assessment was confined to the practical consequence supported by the preserved response and evidence available under the study's non-execution boundary.

## 3.14 Validation and Quality Assurance

Validation concentrated on the implemented derived-analysis infrastructure and used synthetic-only fixtures. The final validation exercise, `FINAL-ANALYSIS-VALIDATION-01`, recorded 126 passing focused tests covering adjudication and PIPE-07, PIPE-08, PIPE-09, and PIPE-10. A PIPE-07 and PIPE-10-focused subset recorded 44 passing tests. The full suite recorded 327 passing tests alongside two known historical freeze-fixture failures: the worktree lacked the expected historical raw directories for four v2.1 and eight v2.3 fixtures. The validation verdict was `PASS WITH DOCUMENTED LIMITATIONS`.

The checks covered pipeline implementation, decision logic, and derived-analysis behaviour. They included cross-pipeline reconciliation of the controlled confirmation count with primary numerators, grouped totals with primary outputs, package-state totals with the primary package denominator, and eligible response totals with the SHR denominator. They also exercised malformed-provenance rejection, route exclusivity, overwrite protection, response eligibility, zero-package response treatment, secondary-state classification, uncertainty bounds, and deterministic statistical behaviour. Such checks supported the fail-closed handling of inconsistent provenance and ensured that outputs were derived from coherent, explicitly supplied inputs rather than silently reconstructed from unrelated records.

These test counts were not a quality score and did not validate final empirical findings. They did not establish the correctness of any final rate, the accuracy of researcher judgement in individual adjudications, inter-rater reliability, predictive accuracy, temporal generalisation, or model performance beyond the bounded study. They also did not remove the need for a provenance-consistent final analysis snapshot once collection and required adjudications were complete. Their purpose was to demonstrate that the implemented rules and safeguards behaved as specified under controlled test cases.

## 3.15 Research Integrity, Safety, and Methodological Limitations

### 3.15.1 Research integrity and preservation controls

The study used frozen v2.6 prompts, configuration, task manifest, and rendered-input controls, with hash checks binding inputs and derived stages to their specified sources. Raw responses and collection metadata were preserved as observations. The append-only and raw-immutability principle meant that response content, provider records, and frozen inputs were not overwritten to obtain a preferred analytical outcome. Corrections to analytical status, where required by documented rules, were applied as derived overlays with provenance rather than by changing the preserved raw evidence.

Extraction, registry evidence, classification, adjudication, metric construction, grouping, and risk scoring were derived-only transformations. Their outputs retained versions, hashes, timestamps, and source relationships so that a derived result could be traced back through the evidence chain. Primary denominators were fixed by pre-specified eligibility and unit rules, and were not changed after outcomes were observed. The workflow prohibited regeneration, substitution, or fallback-based replacement of observations that were failed or truncated. Interim outputs and historical snapshots were retained separately from the final v2.6 analysis and were not represented as final results.

### 3.15.2 Safety and non-execution boundary

Generated or untrusted dependencies were not installed or executed because doing so was not required for the defined package-reference validation construct, would introduce unnecessary security risk, and would create a different experimental construct. Registry validation was restricted to read-only queries. The study did not claim, register, reserve, publish, or otherwise attempt to obtain package names, and it did not conduct active exploitation. This boundary both reduced exposure to untrusted artefacts and ensured that the observations concerned generated references and their evidence-based classification, rather than the behaviour of installed code or newly registered packages.

### 3.15.3 Methodological limitations

The empirical scope was limited to direct Node.js/npm package references. The frozen design comprised 30 tasks, four model conditions, and three planned repetitions, so it was a bounded comparison rather than a representation of all code-generation systems, software tasks, or package ecosystems. The medium-difficulty designation was study metadata and was not externally calibrated.

Extraction covered supported explicit forms only. It did not infer dependencies from narrative discussion, analyse transitive dependencies, or cover unsupported forms such as re-exports, `require.resolve`, non-literal references, aliases, and commands from other package managers. The study therefore did not measure every way in which generated code might imply a dependency.

The evidence chain did not test whether generated code executed correctly, whether a package's API or capabilities suited the intended use, whether a referenced version resolved or was compatible, or whether an existing package was functionally appropriate. Registry evidence was time-bounded to the recorded validation time and could not establish a package's historical state beyond the evidence used in adjudication. Provider-side serving, routing, and versioning were not controlled beyond the frozen exposed condition records; the hybrid collection-interface allocation was also an operational consideration when interpreting the bounded design.

Some adjudications could remain unresolved, and the risk framework was study-specific and rule-based rather than a calibrated forecast. These limitations, together with the preserved exclusions for truncated and failed responses, mean that the findings should not be generalised to all LLM-generated code or all forms of software dependency reliability.

## 3.16 Chapter Summary

This chapter specified the frozen v2.6 methodology for a Node.js/npm study comprising 30 tasks, four model conditions, and three planned repetitions. It described direct npm reference extraction, read-only registry validation, conservative classification and adjudication, and controlled confirmation routing. PHR and SHR were defined as the primary measures of confirmed package hallucination, while DFR and RDFR were retained as secondary, exploratory measures of exact-name dependency-resolution reliability. The chapter also defined grouped descriptive and conditional statistical analysis, a post-classification Impact × Detectability practical-risk framework, and the preservation, safety, validation, and limitation boundaries governing interpretation.

Chapter 4 reports the verified empirical results after completion of the final collection and analysis process.
