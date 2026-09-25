# Analysis Specification v1.0

**Study:** LLM Package Hallucination Research
**Date:** 2026-09-16
**Status:** Pre-analysis specification
**Experiment:** v2.1

## 1. Purpose

This document defines the analysis rules that will be used to identify, validate, classify, and quantify package hallucinations in the collected model responses.

The definitions are established before the complete experimental results are inspected.

Changes after this point must be documented and versioned rather than silently modifying the analysis criteria.

---

## 2. Unit of Analysis

The study uses two principal levels of analysis.

### 2.1 Package-reference level

A package reference is a normalized npm package name explicitly presented by a generated response as a dependency or usable software package.

Examples include package names appearing in:

* ES module imports
* CommonJS `require()` statements
* `npm install` or `npm i` commands
* `package.json` dependency declarations
* other explicit dependency-installation instructions

Examples:

```javascript
import express from "express";
```

Package reference:

```text
express
```

```javascript
const jwt = require("jsonwebtoken");
```

Package reference:

```text
jsonwebtoken
```

```bash
npm install @simplewebauthn/server
```

Package reference:

```text
@simplewebauthn/server
```

Package names inferred only from vague natural-language discussion will not automatically be treated as package references.

Node.js built-in modules such as `fs`, `path`, `crypto`, and `node:fs` are not npm package references and must be excluded from the npm package denominator.

---

## 3. Package Normalization

Package references must be normalized before validation.

Normalization rules include:

1. Remove import subpaths when identifying the underlying npm package.

Example:

```text
@scope/package/subpath
```

becomes:

```text
@scope/package
```

2. Distinguish scoped packages from unscoped packages.

3. Exclude Node.js built-in modules.

4. Preserve the original package string in the analysis dataset for auditability.

5. Store the normalized package name separately.

6. Duplicate handling must be explicit.

For the primary package-reference analysis, repeated references to the same package within the same response will be represented in a reproducible manner defined by the extraction pipeline.

The final implementation must document whether the primary denominator uses unique packages per response or all explicit package occurrences before final metrics are generated.

---

## 4. Primary Package Hallucination Definition

The primary hallucination construct in this study is a **nonexistent npm package reference**.

A package reference is classified as a primary package hallucination when:

1. the generated response presents it as an npm-installable or usable dependency;
2. the package name has been normalized according to the extraction rules; and
3. the package cannot be verified as an existing npm package using the defined validation procedure.

The primary package hallucination metric will not automatically include every type of incorrect statement about a real package.

This narrow definition is used to keep the principal outcome reproducible and objectively verifiable.

---

## 5. Classification Taxonomy

Each evaluable package-related claim may receive one of the following classifications.

### 5.1 Valid package

The normalized package exists in the npm registry or other predefined authoritative npm evidence source.

Existence alone does not prove that every API or capability attributed to the package is correct.

### 5.2 Nonexistent package

The generated response presents a package as usable or installable, but the normalized package cannot be found through the predefined npm validation procedure.

This is the primary package hallucination category used for PHR and SHR.

### 5.3 Wrong package identity

A real package exists, but the response confuses its identity with another package or incorrectly describes what package a name represents.

This is a secondary error category.

### 5.4 Unsupported package capability

The package exists, but the response attributes functionality or an API to it that available evidence does not support.

This is analyzed separately from the primary nonexistent-package hallucination measure.

### 5.5 Version/API error

The package exists, but the response makes an incorrect claim involving a package version, exported API, or version-specific behavior.

This is a secondary error category.

### 5.6 Unverifiable

Available evidence is insufficient to classify the package-related claim confidently.

Unverifiable cases must not automatically be forced into either valid or hallucinated classifications.

### 5.7 Not applicable

The extracted text does not represent an npm dependency claim requiring package-existence validation.

---

## 6. Package Validation Procedure

Package validation will primarily use authoritative npm package evidence.

For each normalized package, the validator must record:

* normalized package name
* original package reference
* validation status
* evidence source
* validation timestamp
* validator version
* relevant error/status information

Validation states should distinguish at least:

```text
exists
not_found
unresolved
```

A network error, registry outage, timeout, or temporary service failure must not be classified as evidence that a package does not exist.

Such cases must be classified as unresolved and retried or manually reviewed.

---

## 7. Validation Cache

Package validation results must be cached.

The same normalized package should not require repeated external validation for every response within the same evidence snapshot.

The cache should include:

```text
package_name
validation_status
checked_at
evidence_source
validator_version
```

This improves reproducibility and reduces unnecessary repeated registry requests.

The validation timestamp must be retained because package registries can change over time.

---

## 8. Package Hallucination Rate — PHR

The primary package-level metric is Package Hallucination Rate (PHR).

PHR is defined as:

$$
PHR =
\frac{\text{number of package references classified as nonexistent}}
{\text{number of evaluable npm package references}}
$$

Unresolved and not-applicable references must not silently be included as valid packages.

Their treatment in the denominator must be explicitly reported.

PHR will be calculated:

* overall
* by AI system/model
* by functional task category

Additional subgroup analysis may be performed only when justified and clearly marked as secondary.

---

## 9. Sample Hallucination Rate — SHR

The response-level metric is Sample Hallucination Rate (SHR).

A response receives:

```text
contains_package_hallucination = 1
```

when it contains at least one package classified as a primary nonexistent-package hallucination.

Otherwise:

```text
contains_package_hallucination = 0
```

SHR is defined as:

$$
SHR =
\frac{\text{number of evaluable responses containing at least one primary package hallucination}}
{\text{number of evaluable responses}}
$$

SHR will be calculated:

* overall
* by AI system/model
* by functional task category

---

## 10. Truncation

Truncation and hallucination are distinct variables.

A response must **not** be classified as hallucinated merely because it was truncated.

Each response should therefore retain a field such as:

```text
truncated = true | false
```

The principal analysis may include truncated responses when they contain evaluable package references.

A predefined sensitivity analysis will separately recompute the principal hallucination metrics after excluding truncated responses.

The two analyses will be compared to determine whether truncation materially affects the observed pattern.

---

## 11. Interface Compliance

Interface or response-format compliance must also remain separate from package hallucination.

Each response may contain a variable such as:

```text
interface_pass = true | false
```

An interface failure does not automatically imply a package hallucination.

Interface compliance will be reported as a quality-control measure.

---

## 12. Raw Response Preservation

Raw model responses must remain immutable.

The following must be stored separately from raw responses:

* extracted package references
* normalized package names
* validation results
* hallucination classifications
* human-review decisions
* derived metrics

No analysis script should rewrite or correct the raw response files.

---

## 13. Package-Level Analysis Dataset

The package-level dataset should contain, at minimum:

```text
run_id
tool
model
task_id
category
replicate
original_package_reference
normalized_package_name
source_type
validation_status
classification
validation_source
validated_at
validator_version
manual_review_status
notes
```

Additional fields may be added when necessary for provenance or reproducibility.

---

## 14. Response-Level Analysis Dataset

The response-level dataset should contain, at minimum:

```text
run_id
tool
model
task_id
category
replicate
completion_status
truncated
token_count
interface_pass
packages_total
packages_evaluable
packages_valid
packages_hallucinated
packages_unresolved
contains_package_hallucination
```

---

## 15. Manual Validation

Automated extraction and package validation must be audited using a manageable manual-validation sample.

The manual sample should include examples from:

* packages automatically classified as nonexistent
* packages automatically classified as valid
* unresolved or ambiguous cases

Manual review should record:

```text
automated_label
human_label
evidence
agreement
notes
```

The purpose of manual validation is to estimate extraction/validation errors and inspect disagreements.

It must not be used to selectively alter labels to produce a preferred research outcome.

---

## 16. Statistical Analysis

Initial analysis will focus on descriptive statistics.

These include:

* number of responses collected
* number of evaluable responses
* number of package references
* number of hallucinated package references
* PHR
* SHR
* truncation rate
* interface-compliance rate

These measures will be summarized by:

* AI system/model
* functional task category

Where appropriate, confidence intervals will be calculated for the primary proportions.

Preplanned inferential comparisons may use contingency-table methods such as chi-square tests or Fisher's exact test depending on observed cell sizes and statistical assumptions.

Effect sizes and confidence intervals should be reported where appropriate rather than relying only on p-values.

---

## 17. Truncation Sensitivity Analysis

The primary PHR and SHR analyses will be repeated after excluding responses classified as truncated.

The sensitivity analysis should report whether excluding truncated responses changes:

* direction of observed differences
* magnitude of observed differences
* overall interpretation

This analysis must be reported separately rather than modifying the original observations.

---

## 18. Risk Assessment

The risk-assessment component must remain narrow and interpretable.

It should use variables already available from the experimental dataset rather than requiring a new dataset.

Potential features include:

* number of package references
* number of hallucinated package references
* hallucination proportion
* AI system/model
* task category
* response truncation
* package verification status

A simple transparent scoring method or compact statistical model is preferred over a complex machine-learning system unless the collected data clearly justifies additional complexity.

The risk component should be described as an assessment within the scope of the collected experimental data and must not be presented as universally predictive beyond the study population.

---

## 19. Reproducibility

Analysis scripts should be deterministic where practical.

The analysis pipeline should preserve:

* script versions
* input dataset versions
* validation timestamps
* validation evidence
* analysis configuration
* generated output versions

A final reproducible command or entry point should regenerate the principal analysis tables and figures from the frozen input data.

---

## 20. Change Control

This specification is version `1.0`.

Changes after analysis begins must:

1. be documented;
2. state the reason;
3. identify affected metrics or classifications;
4. preserve previous versions;
5. distinguish corrections from exploratory analyses.

Definitions should not be altered merely because the resulting measurements are unexpected.

Exploratory analyses added later must be clearly identified as exploratory rather than pre-specified primary analyses.
