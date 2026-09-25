## 3.5 Model Conditions and Data Collection

### 3.5.1 Frozen model conditions

The rendered prompts described in Section 3.4 were submitted to four frozen model conditions, designated M1 to M4. Each condition was defined in the frozen model configuration (`api-model-set-1.4.0`) as a combination of an exact model identifier, an API provider, an underlying-provider routing constraint where applicable, and a model-specific output-token ceiling (Table 3-5). The identifiers are reported exactly as frozen, regardless of any later changes in the names under which providers present these models.

**Table 3-5. Frozen model conditions in the v2.6 experiment**

| Condition | Frozen model identifier                  | API provider | Underlying-provider constraint            | Output-token ceiling |
| --------- | ---------------------------------------- | ------------ | ----------------------------------------- | -------------------: |
| M1        | `cohere/north-mini-code:free`            | OpenRouter   | Pinned to `cohere`; fallback disabled     | 64,000               |
| M2        | `qwen/qwen3.8-27b`                       | OpenRouter   | Restricted to Darkbloom only; no fallback | 32,768               |
| M3        | `openai/gpt-oss-120b`                    | Groq         | Not applicable                            | 65,536               |
| M4        | `nvidia/nemotron-3-ultra-550b-a55b:free` | OpenRouter   | Pinned to `nvidia`; fallback disabled     | 65,536               |

*Note.* Source: frozen model configuration `config/api_model_set_1.4.0.json`. Shared settings for all conditions: temperature 0.6; top-p 0.95; seed not controlled.

For the three OpenRouter conditions, each request named the frozen underlying provider, disabled fallback routing, and required the serving provider to support all requested parameters; for M2, the route was additionally restricted to Darkbloom alone. M3 was requested directly from Groq, so no underlying-provider constraint applied. No fallback model was defined for any condition.

All conditions shared a temperature of 0.6 and a top-p of 0.95; the seed was not controlled and is recorded as `not_controlled`. Each request consisted of a single user message containing the frozen rendered prompt, with no previous conversational context. No tools were exposed, each request explicitly declared that no tool use was permitted, and browsing, retrieval augmentation, and code execution were unavailable. The output-token ceilings were set per condition with reference to documented model and provider limits, following the ceiling problems observed in earlier protocol versions (Section 3.2). The ceiling is therefore part of each condition's definition, and conditions were not compared under an identical output budget.

The model conditions were treated as experimental conditions. The design held prompts, sampling settings, and interaction format constant, but it neither controlled nor observed the training data, architecture, alignment procedures, serving infrastructure, or provider-side versioning of the underlying models. Differences between conditions therefore describe differences between frozen model/API configurations under the evaluated experimental conditions. They cannot be attributed, on the basis of this design, to architecture, training-data composition, or any other hidden provider-side property.

### 3.5.2 Collection routes and the separation of assignment from eligibility

The planned hybrid assignment allocated 180 manifest rows to automated collection through the provider APIs and 180 rows to manual collection. Every row, whichever its route, was defined in advance by the frozen manifest, which fixed its task, category, model condition, repetition, rendered prompt, and expected prompt digest (Section 3.4.5). The study does not claim that route assignment was randomised; the route of each row was recorded so that it remains available when outcomes are interpreted. Operational details of the manual route are reported only to the extent supported by the authoritative collection records (Appendix `[APPENDIX REFERENCE PENDING]`).

Interface assignment was an accounting attribute of a manifest row, not a statement about its analytical value. A row retained its assignment irrespective of outcome: an API-assigned row that failed remained API-assigned and was not moved to the manual route to obtain a usable response. Whether a response entered the analysis was determined separately, by the rules in Section 3.6.

### 3.5.3 Collection procedure

API collection proceeded sequentially in the frozen manifest order, one request at a time, without researcher-imposed pacing. Before each request, the collection software confirmed that the manifest row matched the frozen model configuration and that the prompt file's SHA-256 digest matched the manifest. It refused to proceed if a record already existed for the run identifier, so no preserved observation could be overwritten. When one condition's rows could not be collected for a period for operational reasons, they were left pending without altering the manifest, renumbering the collection order, or changing any other observation.

For every API observation, the exact prompt, the exact request body, the complete raw provider response, the extracted assistant content, and a metadata record were preserved. The metadata recorded the requested and returned model identifiers, the provider and, for routed conditions, the underlying provider that served the request, the sampling parameters and ceiling, UTC timestamps, exposed token usage, the declared finish reason, and SHA-256 digests of the prompt, request, response, and raw provider response. For HTTP attempts, the response body and selected safe response headers were retained; transport failures were recorded in the retry history. Credentials were excluded from all records. A returned model identifier or serving provider that differed from the frozen condition was recorded as a protocol deviation; for M2, whose route was restricted to one provider, such a mismatch made the observation a failure.

Retries were permitted only for infrastructure faults: transport failures, rate-limit responses (HTTP 429), and server errors (HTTP 5xx). The initial request could be followed by at most three retries, for at most four attempts in total; the configured waits before retries were 2, 5, and 10 seconds. For HTTP 429, a valid `Retry-After` value could extend the applicable wait. Each attempt was logged. No request was repeated because of the content of its response, and no response was replaced with output from a different model, provider, or route. When the retry allowance was exhausted or a non-retryable fault occurred, the observation was finalised as a failure, preserved, and collection continued with the next row.

Two decisions adopted during collection governed abnormal outcomes. Under D035, a provider response declaring an abnormal termination was treated as a failure even when it contained partial content (Section 3.6). Under D038, a request that had already been sent but was interrupted by the researcher while its response was being received was finalised once as a failure and was not regenerated. This finalisation was performed offline by a utility that verified the manifest identity, prompt and request digests, start time, and in-progress status, wrote an immutable pre-recovery audit record, made no network request, and refused to act on any record that was already finalised or contained a response.

Figure 3-2 summarises the workflow and the boundary between preserved evidence and derived analysis.

> **[Figure 3-2 placeholder] Final v2.6 experimental workflow and preservation boundary.**
> Frozen inputs (task set, template, rendered prompts, model configuration, manifest) → sequential collection through the assigned route (API or manual) → preserved raw evidence (prompt, request, raw provider response, assistant content, metadata, attempt history) → **preservation boundary** → derived stages (response inventory and status derivation, extraction, registry validation, classification, adjudication, analysis datasets). Arrows cross the boundary in one direction only. The figure must not imply collection completion, package installation or execution, or any result.

---

## 3.6 Response Preservation, Status, and Analytical Eligibility

### 3.6.1 Preservation principle

Raw collection records were treated as append-only evidence. Once finalised, an observation's prompt, request, provider response, assistant content, and metadata were not edited, regenerated, or replaced. All later processing read these records and wrote to separate, versioned derived files. The first derived stage was a response inventory with one row per planned manifest row. Where a later rule changed the analytical status of an observation, the change was applied in this inventory, never in the raw record.

### 3.6.2 Response states

Each finalised observation was assigned one of three states according to how its generation ended.

A response was **COMPLETED** when the provider returned a valid response with assistant content and declared the finish reason `stop`.

A response was **TRUNCATED** when the provider declared the finish reason `length`, meaning that generation was incomplete because it reached the configured output-token ceiling. Truncated responses were preserved under their original run identifiers, including empty visible content where applicable, and package references could be extracted from them with a truncation marker. Because the ungenerated remainder might have added, removed, or corrected package references, truncated responses were excluded from both numerator and denominator of the primary metrics. They may be described separately, but never combined with the primary estimates.

A response was **FAILED** when no valid, normally terminated or length-limited response was obtained. This covered exhaustion of the retry allowance, non-retryable HTTP statuses, malformed responses, empty content without a length termination, the M2 provider-identity rule, abnormal provider terminations, and the interrupted request finalised under D038. Failed observations were preserved once as evidence of the collection process, excluded from analysis, and not regenerated or substituted.

The original protocol had defined only the `stop` and `length` cases, so abnormal terminations required an explicit rule. Under D035, any other finish reason, including a provider-declared `error`, a content-filter or tool-call termination, or a missing value, made the observation FAILED. Partial content did not override the declared termination, and such responses were not treated as truncated, because truncation in this study denotes reaching the frozen ceiling specifically. The rule depends only on the declared termination status, not on response content. For observations whose raw metadata recorded a different status, it was applied as a deterministic overlay in the response inventory, which retained the original raw status and finish reason alongside the derived status while leaving the raw records unchanged.

Rows that had not been finalised, such as pending rows, had no final state and did not enter the analysis.

### 3.6.3 Response-level and package-level eligibility

Four attributes were kept distinct. The **collection route** recorded API or manual assignment. The **collection status** recorded how generation ended. **Response-level eligibility** determined entry into the response-level metrics, and **package-level eligibility** determined entry of extracted package references into the package-level metrics.

Eligibility followed a single rule: a response, and every package row derived from it, was eligible only when its derived collection status was completed. Package-level eligibility was inherited from the response and never assessed independently. Truncated and failed responses kept a response-level row marked ineligible, so that they remained visible in completeness reporting. Failed responses were not passed to extraction, and the analysis-dataset builder rejected, rather than silently discarded, any package record attributed to a failed response. This prevented outputs built from an uncorrected inventory from being combined with a corrected one.

A completed response with no extractable external npm reference remained eligible. It contributed nothing to the package-level denominator but remained in the denominator of the Sample Hallucination Rate (SHR) as a response without a confirmed hallucination. Excluding such responses would have limited the denominator to responses that happened to name packages and overstated the proportion containing a confirmed hallucination. The metrics are defined in Sections 3.10 and 3.11. Table 3-6 summarises the rules.

**Table 3-6. Response states and analytical eligibility**

| State     | Operational definition                                                                                                   | Raw evidence                                   | Package extraction          | Primary metrics (PHR, SHR)                          | Secondary metrics (DFR, RDFR) |
| --------- | ------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------- | --------------------------- | --------------------------------------------------- | ----------------------------- |
| COMPLETED | Valid response with finish reason `stop`                                                                                 | Preserved unchanged                            | Yes                         | Eligible, including zero-package responses          | Eligible                      |
| TRUNCATED | Finish reason `length` (output ceiling reached)                                                                          | Preserved unchanged                            | Yes, with truncation marker | Excluded from numerator and denominator             | Excluded                      |
| FAILED    | No valid normally terminated or length-limited response, including other finish reasons (D035) and the interrupted request (D038) | Preserved once; not regenerated or substituted | No                          | Excluded from numerator and denominator             | Excluded                      |

*Note.* Collection-route assignment (API or manual) is recorded separately and does not affect eligibility. Pending or unfinalised rows have no final state and do not enter the analysis.

---

## 3.7 Package Reference Extraction and Normalisation

### 3.7.1 Supported reference forms

Package references were extracted by a deterministic, rule-based stage, PIPE-03 (extractor version `pipe-03-package-reference-extractor-1.0.2`), which read the preserved content of every completed and truncated response. It made no registry query, installed no package, and executed no code. Extraction was restricted to explicit syntactic forms through which a Node.js response names an npm dependency. These were recognised wherever they appeared in the response text, but a package mentioned only in narrative description was not extracted, and the dependencies of named packages were not examined.

Five families of reference were supported:

1. static ECMAScript module imports with a literal specifier, including type-only, side-effect, and multi-line declarations;
2. CommonJS `require(...)` calls with a single string-literal argument;
3. dynamic `import(...)` expressions with a single string-literal argument;
4. package operands of `npm install` and `npm i` commands written on their own line, ignoring command-line options and stopping at shell control operators so that a chained command could not contribute words from the next command; and
5. string-valued entries in `dependencies`, `devDependencies`, `peerDependencies`, and `optionalDependencies` objects that could be parsed as valid JSON.

Other forms were not extracted, including non-literal specifiers, `export ... from` re-exports, `require.resolve` calls, and installation commands for other package managers.

### 3.7.2 Normalisation and exclusions

Each reference was normalised to the root npm package name that a registry lookup requires. Unscoped subpaths were reduced to their first segment (`lodash/fp` became `lodash`), and scoped references retained both scope and package segment (`@scope/package/subpath` became `@scope/package`). Explicit versions in installation operands and `package.json` version strings were retained as version specifiers but not analysed further (Section 3.3.2). For every occurrence, the stage retained the original reference, the normalised name, the source form, the complete source line, its character offset, any version specifier, and its position in the response, so that each analysed package can be traced to the exact text that produced it.

References that do not denote an external npm package were excluded: Node.js built-in modules and their subpaths, identified from a fixed list; `node:` references; relative references; absolute and home-directory filesystem paths; `file:` references; and HTTP(S) URLs. References using npm alias syntax (`npm:`) were also excluded, because no policy for resolving aliases to their targets had been defined, and references that could not be reduced to a well-formed package root were discarded as malformed. None of these exclusions depended on registry outcomes. Table 3-7 summarises the rules.

**Table 3-7. Package-reference extraction, normalisation, and exclusion rules (PIPE-03)**

| Aspect          | Rule                                                                                                                                                               |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Input           | Preserved assistant content of completed and truncated responses; failed responses not processed                                                                   |
| Supported forms | Static ESM `import` (literal specifier); `require('...')`; literal dynamic `import('...')`; `npm install` / `npm i` operands; `dependencies`, `devDependencies`, `peerDependencies`, `optionalDependencies` in valid `package.json` content |
| Not extracted   | Narrative-only mentions; non-literal specifiers; `export ... from`; `require.resolve`; other package managers' commands; transitive dependencies                   |
| Normalisation   | Root package name; scoped names retain `@scope/package`; subpaths reduced to the root; explicit version specifiers retained                                        |
| Exclusions      | Node.js built-ins and their subpaths; `node:` references; relative, absolute, and home-directory paths; `file:`; HTTP(S) URLs; `npm:` aliases; malformed references |
| Provenance      | Original reference, normalised name, source form, source line, offset, version specifier, occurrence position, extractor version                                    |
| Analytical unit | Unique `(run_id, normalized_package)`, with occurrence count and source forms retained                                                                             |

### 3.7.3 Unit of package analysis

PIPE-03 produced an occurrence view retaining every extracted reference and a unique view grouping occurrences by `(run_id, normalized_package)`, with the occurrence count, source forms, and first position of each pair. The unique pair was the analytical unit for all package-level metrics. A response that imports a package in several files, lists it in `package.json`, and names it in an installation command makes one dependency recommendation, not several; counting occurrences would have let verbosity or code organisation inflate the denominator and, for a confirmed hallucination, the numerator. Under the unique unit, repeated mentions within one response count once, while the full occurrence record remains available for audit and qualitative description. The same package named in two responses produces two package rows.

---

## 3.8 npm Registry Validation

### 3.8.1 Read-only validation procedure

The registry-validation stage, PIPE-04 (validator version `pipe-04-npm-validator-1.0.0`), recorded whether each normalised name was present in the official npm registry at `https://registry.npmjs.org`. The procedure was strictly read-only. It issued HTTP GET requests for package metadata, did not follow redirects, and made network requests only when live validation was explicitly authorised. No package was installed or executed, and no package name was registered, claimed, reserved, or published. Installation was unnecessary for the construct under study, which concerns whether a named package exists, and would have introduced the very security risk under assessment.

Because registry evidence concerns a name rather than a response, each distinct normalised name was queried once and the evidence was joined to every `(run_id, normalized_package)` row containing it. Scoped names were fully percent-encoded so that scope and package segment were queried together.

### 3.8.2 Evidence states

Each query produced one of three evidence states (Table 3-8). The `not_found` state was reserved for the structurally recognisable response through which the registry reports an absent package: HTTP 404 with the expected not-found JSON body. An error, an unexpected response, or an uncertain outcome is not evidence of absence, so every such outcome remained `unresolved`, as did HTTP 200 metadata whose name did not exactly match the query. Rate-limit responses, server errors, and transport failures could be retried twice, for at most three attempts in total, with 0.5- and 1.0-second waits. A registry `Retry-After` value was used only when valid and no greater than five seconds; otherwise the query ended unresolved. A fixed 0.25-second interval separated successive queries.

**Table 3-8. npm registry evidence states (PIPE-04)**

| Evidence state | Condition                                                                                                                       | Interpretation                                            |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| `exists`       | HTTP 200; metadata `name` exactly equals the normalised name                                                                    | Name present in the registry at the recorded time         |
| `not_found`    | HTTP 404 with the expected package-not-found JSON body                                                                          | Registry evidence of absence only; requires classification |
| `unresolved`   | Any other outcome, including mismatched or malformed metadata, unexpected 404 body, rate limiting, server or transport error     | No registry conclusion; never treated as absence          |

### 3.8.3 Recorded provenance

Each record stored the registry address, exact request URL, HTTP status (absent after a transport failure), UTC retrieval time, validator version, an evidence summary, the error type for unresolved outcomes, the retry count, and the SHA-256 digests of the extraction outputs from which the query list was derived. These digests bind registry evidence to a specific extraction snapshot, so that it cannot be combined with a different set of extracted references without detection.

Validation could resume from an earlier evidence file only if its format version, source digests, package set, and validator version all matched; otherwise the stage refused to proceed. On resumption, names already resolved as `exists` or `not_found` were not queried again. An unresolved name was re-queried only on explicit request, and its earlier record was then retained in the name's evidence history rather than overwritten. Outputs were written atomically, so an interrupted run could not leave a partial evidence file.

### 3.8.4 Interpretation of registry evidence

Registry evidence describes the registry at the time of the query. A package that existed when a response was generated may have been removed before validation, and an absent name may have existed earlier, so registry outcomes are reported as evidence at the time of registry validation, not as permanent properties of names.

Critically, an npm 404 response or `not_found` state was treated as registry evidence only and was not, by itself, a confirmed hallucination. A name can be absent because the model invented it, but also because the package was removed or renamed, placed under the wrong scope, confused with a module inside another package, taken from another ecosystem, or used as the name of the project the response was itself generating. Distinguishing these explanations was the task of the procedure described in Section 3.9.

---

## 3.9 Classification and Adjudication

### 3.9.1 Classification structure

Counting every `not_found` result as a hallucination would have merged the explanations listed in Section 3.8.4 and overstated the construct under study. The classification procedure therefore separated three questions for each package reference: whether it denoted an external npm dependency at all, whether the dependency as named would fail to resolve from the registry, and whether the name was a confirmed package-name hallucination. These were answered by a deterministic classification stage (PIPE-05) and a separate, evidence-based adjudication stage for cases the first could not decide (PIPE-05B). The analysis-dataset builder (PIPE-07) then combined their outputs under a single controlled rule. Figure 3-3 shows the sequence.

> **[Figure 3-3 placeholder] Direct npm extraction, registry evidence, and conservative adjudication pipeline.**
> Preserved response → PIPE-03 extraction and normalisation (unique `(run_id, normalized_package)` rows) → PIPE-04 read-only registry evidence (`exists` / `not_found` / `unresolved`) → PIPE-05 deterministic classification (`AUTO_VALID`; `VALIDATION_UNRESOLVED`; `REVIEW_REQUIRED`; `REVIEWED`) → PIPE-05B guarded adjudication of `REVIEW_REQUIRED` rows (separate output) → PIPE-07 single confirmation-resolution point → analysis datasets. The figure must show that `not_found` leads to review, not directly to a hallucination outcome, and must not depict package installation or execution.

### 3.9.2 Deterministic classification (PIPE-05)

PIPE-05 (classifier version `pipe-05-classifier-1.0.0`) classified each distinct package name from its registry evidence without network access. It first verified input consistency: registry evidence had to carry the digests of the extraction outputs it was built from, each extracted pair had to have exactly one registry record, each evidence state had to agree structurally with its recorded HTTP status and summary, and timestamps had to be in UTC. Any inconsistency stopped the stage.

The rules were deterministic (Table 3-9). A name with registry state `exists` was classified `VALID` (`AUTO_VALID`). A name with state `unresolved` received no classification (`VALIDATION_UNRESOLVED`), so that an operational failure could never become a finding. A name with state `not_found` was classified `AMBIGUOUS` (`REVIEW_REQUIRED`), recording that a clean 404 was insufficient without further checks.

PIPE-05 also accepted researcher-supplied review records for `not_found` names, producing the status `REVIEWED`. Each record had to identify the reviewer, give a UTC review time and written rationale, cite at least one dated evidence source, and record three checks: a historical check for prior existence, a normalisation check of whether the name was an external npm reference rather than a built-in or local one, and an ambiguity check. `CONFIRMED_HALLUCINATION` was accepted only when no prior existence was found, the name was established as an external npm reference, and ambiguity was cleared. `LEGACY_OR_REMOVED` required evidence of prior existence and `BUILTIN_OR_LOCAL` required a corresponding normalisation finding; a review could also leave the name `AMBIGUOUS`.

**Table 3-9. Deterministic classification routes (PIPE-05)**

| Registry evidence | Review record supplied                     | Classification                                                                      | Adjudication status     | Further handling                                  |
| ----------------- | ------------------------------------------ | ----------------------------------------------------------------------------------- | ----------------------- | ------------------------------------------------- |
| `exists`          | Not applicable                             | `VALID`                                                                             | `AUTO_VALID`            | None                                              |
| `unresolved`      | Not applicable                             | None assigned                                                                       | `VALIDATION_UNRESOLVED` | Never treated as a finding                        |
| `not_found`       | No                                         | `AMBIGUOUS`                                                                         | `REVIEW_REQUIRED`       | Eligible for PIPE-05B adjudication                |
| `not_found`       | Yes, with dated evidence and three checks  | `CONFIRMED_HALLUCINATION`, `LEGACY_OR_REMOVED`, `BUILTIN_OR_LOCAL`, or `AMBIGUOUS` | `REVIEWED`              | Confirmation requires all three checks satisfied  |

### 3.9.3 Evidence-based adjudication (PIPE-05B)

Some explanations of registry absence can only be judged within a specific response; a name may be the response's own project name in one response and an external recommendation in another. PIPE-05B (adjudicator version `pipe-05b-adjudicator-1.1.0`) therefore operated on individual `(run_id, normalized_package)` rows and accepted only rows that PIPE-05 had marked `REVIEW_REQUIRED` and `AMBIGUOUS`. It read the PIPE-05 output without modifying it, made no network requests, and wrote its adjudications to a separate, versioned output; the PIPE-05 classification was never rewritten.

Each adjudication record identified the reviewer and UTC review time, gave a rationale, and recorded six checks: the three PIPE-05 checks and three further checks for namespace confusion, ecosystem confusion, and invalid or redundant TypeScript type-definition packages. It also recorded whether the evidence was resolved or insufficient, the dated sources consulted, any historical registry evidence, and, where relevant, the nearest legitimate package or reference. Adjudication was carried out by the researcher; no expert panel or multiple independent reviewers were used, and no inter-rater agreement is claimed.

Each row received one of nine outcomes (Table 3-10). Every outcome except `UNRESOLVED` required resolved evidence and at least one dated evidence source, and each specific category required the check results that support it. Records whose checks did not support their stated outcome were rejected.

**Table 3-10. PIPE-05B adjudication outcomes and derived fields**

| Outcome                              | Evidentiary requirement (summary)                                                                                                              | `confirmed_package_hallucination` | `dependency_failure` | `external_dependency_eligible` |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------: | :------------------: | :----------------------------: |
| `CONFIRMED_HALLUCINATION`            | All six checks satisfied: no prior existence; external npm reference; ambiguity, namespace, ecosystem, and types-package explanations cleared | true                              | true                 | true                           |
| `LEGACY_OR_REMOVED`                  | Evidence of prior existence, removal, or relevant renaming; external npm reference                                                             | false                             | stated explicitly    | true                           |
| `NAMESPACE_CONFUSION`                | Confirmed scope or namespace mismatch; nearest legitimate reference identified                                                                 | false                             | stated explicitly    | true                           |
| `PACKAGE_NAME_CONFUSION`             | External npm reference; nearest legitimate reference identified                                                                                | false                             | stated explicitly    | true                           |
| `INVALID_OR_REDUNDANT_TYPES_PACKAGE` | Type-definition package confirmed invalid or redundant                                                                                         | false                             | stated explicitly    | true                           |
| `ECOSYSTEM_CONFUSION`                | Name confirmed to belong to another package ecosystem                                                                                          | false                             | stated explicitly    | true                           |
| `OTHER_DEPENDENCY_ERROR`             | Resolved evidence of a dependency error not covered by the specific categories                                                                 | false                             | stated explicitly    | true                           |
| `SELF_REFERENCE_OR_LOCAL_PACKAGE`    | Response-internal evidence that the name is the generated project's own package or a local/workspace package declared in the response         | false                             | false                | false                          |
| `UNRESOLVED`                         | Evidence insufficient to support any specific outcome                                                                                          | false                             | not asserted (null)  | undetermined (null)            |

*Note.* "Stated explicitly" means the adjudicator had to record, as true or false, whether the dependency as named would fail to resolve; the value was not implied by the outcome.

The three derived fields represent separate judgements. `confirmed_package_hallucination` was true only for `CONFIRMED_HALLUCINATION`. `dependency_failure` recorded whether the dependency as named would fail to resolve from the registry, which could hold for outcomes that are not hallucinations, such as a removed package or a scope error. `external_dependency_eligible` recorded whether the reference was an external dependency claim at all. This separation allowed exact-name resolution failures to be reported (Section 3.11) without being presented as hallucinations.

`SELF_REFERENCE_OR_LOCAL_PACKAGE` was defined narrowly. It could not be inferred from a 404, from the form of a name, or from its plausibility. It required response-internal evidence that the name was the package name the response declared for its own project, or a local or workspace package the response itself defined. The record had to give the declared name, which had to equal the adjudicated name exactly, the declaration location, the locations and contexts in which the name was referenced, and whether the referenced symbols were defined in the response. Because such a reference is not an external dependency claim, it was classified neither as a hallucination nor as a dependency failure.

Where the evidence did not support a specific outcome, the row was adjudicated `UNRESOLVED`, which required the evidence to be recorded as insufficient and could not assert a dependency-failure value. This prevented uncertain cases from being forced into hallucination or non-hallucination categories. `OTHER_DEPENDENCY_ERROR` served a comparable purpose for resolved cases that did not meet the stricter requirements of the specific categories.

### 3.9.4 Controlled routing of confirmed hallucinations (PIPE-07)

A confirmed hallucination could be recorded through a PIPE-05 `REVIEWED` classification or through PIPE-05B adjudication of a `REVIEW_REQUIRED` row. Without an explicit rule, entry into the primary metrics could have depended on the tool used rather than on the evidence. Decision D037 therefore made PIPE-07 the single point at which primary confirmation was resolved; the metric calculators consumed this resolved result and did not re-derive it.

An eligible package row was primary-confirmed if, and only if, exactly one authorised route established a confirmed hallucination. The first route was a PIPE-05 `REVIEWED` row classified `CONFIRMED_HALLUCINATION`. The second was a PIPE-05B record for a `REVIEW_REQUIRED`/`AMBIGUOUS` row with outcome `CONFIRMED_HALLUCINATION`, all three derived fields true, resolved evidence, all six checks at their confirmation values, non-empty dated evidence sources, a UTC review time, and supported format and adjudicator versions. Because the PIPE-05B checks include those of PIPE-05 and add three more, the second route admitted no weaker evidence than the first. All other PIPE-05B outcomes, including the confusion categories, `LEGACY_OR_REMOVED`, `OTHER_DEPENDENCY_ERROR`, `SELF_REFERENCE_OR_LOCAL_PACKAGE`, and `UNRESOLVED`, remained outside the primary numerators. A row confirmed through PIPE-05B kept its PIPE-05 classification of `AMBIGUOUS` and received a separate derived field recording the confirmation route, the confirming tool or adjudication version, and the SHA-256 digest of the confirming output.

PIPE-07 was designed to fail closed: it produced no dataset from which primary metrics could be calculated unless the adjudication evidence matched the analysis rows unambiguously. It stopped if a PIPE-05B record could not be matched to an analysis row or its source row was not `REVIEW_REQUIRED`/`AMBIGUOUS`; if the record had been built from a different PIPE-05 output, as detected by digest comparison; if a row appeared twice in the PIPE-05B output, or on both routes even with agreeing outcomes; if a record claimed confirmation without meeting the requirements; if a version was unsupported; or if the record's truncation marker disagreed with the analysis dataset. The PIPE-05B input was never discovered automatically: it had to be supplied, or its absence declared, explicitly, and the choice was recorded. When PIPE-05 was rebuilt, PIPE-05B had to be rerun from the preserved adjudication evidence rather than an earlier file being reattached by hand.

These rules changed neither the unit nor the denominators of the primary metrics. Rows left `REVIEW_REQUIRED` without adjudication, and rows adjudicated `UNRESOLVED`, remained in the package-level denominator and outside its numerator, and are reported as separate counts. The confirmation status resolved here is the input to the primary metrics defined in Section 3.10.
