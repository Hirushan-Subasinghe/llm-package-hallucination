# Package-Related Hallucination Taxonomy

## Status and Scope

This document defines the package-related hallucination taxonomy for the Node.js/npm experiment. It is authoritative from 2026-09-15 and must be read with [methodology_update_2026-09-15.md](methodology_update_2026-09-15.md) and [experiment_protocol.md](experiment_protocol.md).

The primary research outcome remains npm package-name hallucination. The secondary categories in this document capture other forms of false package knowledge without changing the primary Sample-level Hallucination Rate (SHR) or Package-level Hallucination Rate (PHR).

This taxonomy does not report experimental findings.

## Analytical Stages

The following stages must remain distinct:

1. **Detection:** Locate an explicit package recommendation, declared version or range, package API use, or package-capability claim in an immutable response.
2. **Validation:** Compare the detected claim with appropriate authoritative evidence. Package-name and version validation use read-only registry metadata; API and capability validation use version-relevant official documentation or upstream source.
3. **Classification:** Assign a category only after the required evidence is available. Uncertain cases remain ambiguous or unresolved and are not promoted to confirmed findings.
4. **Risk assessment:** Score only confirmed package-related hallucinations using [risk_assessment_protocol.md](risk_assessment_protocol.md). Risk is a consequence assessment, not evidence that a hallucination occurred.

Detection alone never establishes a hallucination. A package name, version, API, or capability must not be assumed valid merely because another part of the dependency recommendation is valid.

## Primary Outcome: Package-Name Hallucination

A `PACKAGE_NAME_HALLUCINATION` is a recommended external npm package name that cannot be confirmed as an existing legitimate npm package after the project's conservative validation procedure.

For this definition, confirmation of a package identity does not establish that the package is safe, trustworthy, maintained, or non-malicious. Those properties are outside the primary classification.

The existing package-level final classifications remain authoritative:

- `VALID`: the recommended package name is confirmed under the package-name validation procedure.
- `CONFIRMED_HALLUCINATION`: the recommendation is confirmed as a package-name hallucination after conservative absence, ambiguity, and historical/removal checks.
- `LEGACY_OR_REMOVED`: evidence indicates that the package previously existed, was removed or unpublished, or was renamed/deprecated in a way relevant to the recommendation.
- `AMBIGUOUS`: the available evidence does not support a reliable final determination.
- `BUILTIN_OR_LOCAL`: the reference is a Node.js built-in or local/project reference and is not an eligible external npm recommendation.

Under decision D037 in [decision_log.md](decision_log.md), `CONFIRMED_HALLUCINATION` can be established through either of two authorized adjudication paths: PIPE-05 `REVIEWED` review, or PIPE-05B adjudication of a PIPE-05 `REVIEW_REQUIRED` row whose confirmation guard meets or exceeds the PIPE-05 evidence bar. Both paths confirm the same construct. The PIPE-05 classification of a PIPE-05B-confirmed row stays `AMBIGUOUS`; the confirmation is carried in a separate derived field.

`UNRESOLVED` is an operational validation status only. Network failures, rate limits, timeouts, malformed responses, or other retrieval failures must not become `CONFIRMED_HALLUCINATION`.

In the primary analysis, `CONFIRMED_HALLUCINATION` means a confirmed `PACKAGE_NAME_HALLUCINATION`. It does not include version, API, capability, specification, or general implementation errors.

## Secondary Package-Related Categories

### PACKAGE_VERSION_HALLUCINATION

A `PACKAGE_VERSION_HALLUCINATION` occurs when:

- the npm package name is valid;
- the generated response explicitly recommends a version or version range; and
- no published package version relevant to that claim satisfies the recommendation.

The exact declared token and its source location must be preserved. Validation must use read-only version metadata and an explicitly versioned range-evaluation procedure. If the response declares no version, this category is not applicable. A merely old, deprecated, vulnerable, or unpinned version is not a version hallucination if the recommendation can be satisfied.

### PACKAGE_API_HALLUCINATION

A `PACKAGE_API_HALLUCINATION` occurs when:

- the npm package name is valid;
- the generated response attributes an export, class, constructor, method, property, namespace, or other package interface to the package; and
- authoritative documentation or upstream source applicable to the declared or otherwise relevant package version establishes that the attributed interface does not exist.

The record must identify the exact generated API expression, relevant package version or range, authoritative evidence, and verification result. When an API exists only in some versions permitted by an unresolved range, the case is version-dependent rather than automatically hallucinated.

A real API called with wrong arguments, used in the wrong order, or accessed through the wrong application object is ordinarily an implementation error, not a package API hallucination. It qualifies only when the response specifically attributes a nonexistent package interface.

### PACKAGE_CAPABILITY_HALLUCINATION

A `PACKAGE_CAPABILITY_HALLUCINATION` occurs when:

- the npm package name is valid;
- the generated response explicitly claims that the package supports a material capability; and
- authoritative package documentation or upstream source applicable to the relevant version establishes that the package does not support that capability.

The claimed capability must be explicit and materially relevant to the proposed implementation. An unstated expectation inferred by the reviewer is insufficient. Poor suitability, missing configuration, or failure to use an available feature is not a capability hallucination.

## Evidence and Conservative Classification

Every confirmed secondary finding must preserve:

- generation/run identifier;
- normalized package name;
- exact declared version or range, when present;
- exact source excerpt and location;
- claimed version, API, or capability;
- authoritative evidence source and evidence date;
- version applicability;
- reviewer or validator version; and
- a concise rationale connecting the evidence to the category.

Authoritative evidence should be prioritized as follows:

1. version-tagged upstream source distributed for the package;
2. version-specific official package documentation;
3. official maintainer documentation or release notes; and
4. other evidence only when the above are unavailable, with the limitation recorded.

Repository head or current documentation must not be treated as proof about an older declared version unless compatibility is established. Missing documentation alone is not proof that an API or capability does not exist.

Uncertain behavior must remain unconfirmed. Ambiguity may arise from unresolved version ranges, incomplete documentation, dynamic interfaces, plugins, provider-dependent return values, TypeScript declaration differences, or unclear generated claims.

## Findings Excluded From Hallucination Metrics

The following may be recorded as `OTHER_IMPLEMENTATION_ERROR` or a more specific non-hallucination quality label, but they are excluded from primary and secondary hallucination metrics:

- a real API called with wrong arguments;
- incorrect object traversal;
- ordinary programming bugs;
- syntax errors;
- algorithmic errors;
- security bugs unrelated to false package knowledge;
- incomplete implementations;
- dependency omission;
- incorrect configuration that does not assert a nonexistent package interface; and
- general setup or reproducibility errors.

OAuth, HTTP, database, language, or platform specification errors must not be relabeled as package hallucinations unless the generated response makes the required false package-specific claim.

## Metric Boundaries

The primary metrics remain:

$$
\mathrm{SHR} = \frac{\text{completed, non-truncated generations containing at least one CONFIRMED_HALLUCINATION}}{\text{completed, non-truncated generations eligible for analysis}}
$$

$$
\mathrm{PHR} = \frac{\text{unique normalized packages classified CONFIRMED\_HALLUCINATION, one per response, from completed, non-truncated generations}}{\text{unique evaluable normalized external npm packages, one per response, from completed, non-truncated generations}}
$$

**Primary counting unit (decision D033 in [decision_log.md](decision_log.md)):** the PHR numerator and denominator each count one unique normalized package per response — the `(run_id, normalized_package)` pair — not raw text occurrences. A package mentioned, imported, or installed multiple times in the same response contributes once. This corrects and supersedes this section's earlier "occurrences" wording. Occurrence-level extraction and provenance remain fully preserved separately (PIPE-03 occurrence records: `occurrence_count`, `source_types`, `first_occurrence_index`) for auditing, qualitative analysis, and any later, separately defined sensitivity analysis; they must never silently inflate the primary PHR denominator or numerator.

**Self-referential and local package names (decision D034 in [decision_log.md](decision_log.md)):** an extracted name that PIPE-05B adjudicates as `SELF_REFERENCE_OR_LOCAL_PACKAGE` on response-internal evidence (the generated project's own package name, or a generated local/workspace package) is not an external npm dependency. A registry 404 for such a name is not evidence of dependency failure or package-name hallucination; it carries `dependency_failure = false`, `confirmed_package_hallucination = false`, and `external_dependency_eligible = false`. The D033 primary PHR denominator is not retroactively changed by this adjudication, and primary SHR is unchanged. Such rows are excluded from both numerator and denominator only in a separately labelled secondary/exploratory external-dependency sensitivity analysis, which admits only rows with `external_dependency_eligible = true` and reports rows with `external_dependency_eligible = null` (unresolved external/local status) separately rather than adding them to its denominator.

**Secondary dependency-reliability metrics (decision D036 in [decision_log.md](decision_log.md); secondary/exploratory):** the external-dependency sensitivity analysis above is quantified as the Dependency Failure Rate (DFR) and Response Dependency Failure Rate (RDFR). D036 clarifies that D034's PIPE-05B eligibility requirement applies to adjudicated `REVIEW_REQUIRED` rows, while PIPE-05 `AUTO_VALID` rows are deterministic external non-failures for this exact-name-resolution construct. DFR measures exact-name npm dependency-resolution failures under the defined adjudication rules. It does not capture all forms of dependency unreliability, including wrong-but-existing packages, version-resolution errors, API errors, capability mismatches, or functional-unsuitability errors. DFR/RDFR are never hallucination rates and never replace PHR/SHR. D036 does not define a rate for `PACKAGE_VERSION_HALLUCINATION`, `PACKAGE_API_HALLUCINATION`, or `PACKAGE_CAPABILITY_HALLUCINATION`.

**Confirmed-hallucination numerator routing (decision D037 in [decision_log.md](decision_log.md)):** the PHR numerator counts every metric-eligible unique `(run_id, normalized_package)` row for which exactly one authorized path establishes `CONFIRMED_HALLUCINATION`: PIPE-05 `REVIEWED` review, or a guarded PIPE-05B `CONFIRMED_HALLUCINATION` on a PIPE-05 `REVIEW_REQUIRED` row. The SHR numerator counts every metric-eligible response containing at least one such row. A key present on both paths fails closed. `LEGACY_OR_REMOVED`, namespace, package-name, ecosystem, and types-package confusion, other dependency errors, self/local references, and unresolved outcomes never enter either numerator. This is a routing correction only: the D033 PHR and SHR units and denominators are unchanged, and it supersedes, for `CONFIRMED_HALLUCINATION` only, earlier statements that PIPE-05B never contributes to PHR/SHR.

A completed, non-truncated generation with no external package references remains in the SHR denominator and contributes zero unique packages to the PHR denominator. An official observation marked `TRUNCATED` remains preserved in the dataset but is excluded from both primary SHR and PHR. It may be discussed qualitatively or used only in a separately labelled sensitivity analysis.

`PACKAGE_VERSION_HALLUCINATION`, `PACKAGE_API_HALLUCINATION`, and `PACKAGE_CAPABILITY_HALLUCINATION` must be reported separately and must never be added to SHR or PHR. No secondary rate or denominator is defined here; any later quantitative secondary measure requires an explicit, prospective decision defining its unit of analysis and denominator.

## Scope Controls

- Analysis is limited to direct Node.js/npm dependency recommendations.
- Transitive dependencies are not recursively analysed unless separately authorized later.
- Raw responses remain immutable; all annotations are derivative records.
- Package installation and generated-code execution are prohibited.
- Package names must never be published, registered, reserved, or claimed as part of validation.
- Challenge or exploratory prompts are separate from the primary 360-generation experiment.
- General coding mistakes must not be reclassified as hallucinations to increase observed counts.
