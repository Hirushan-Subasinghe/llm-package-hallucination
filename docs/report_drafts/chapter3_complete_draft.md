# Chapter 3: Research Methodology

## 3.1 Chapter Introduction

Chapter 1 identified four questions concerning confirmed npm package-name hallucinations, secondary exact-name dependency-resolution failures, variation across model conditions and task categories, and the practical risk of eligible confirmed findings. Chapter 2 established that such observations depend on the defined model, prompt, task, ecosystem, and measurement boundary, and that a registry lookup alone cannot establish hallucination. This chapter describes the implemented, frozen v2.6 methodology developed in response to those constraints.

The study separated collection from interpretation. Frozen tasks and prompts were submitted to predefined model conditions; raw responses and collection records were preserved; and extraction, registry validation, classification, adjudication, measurement, statistical analysis, and risk assessment were conducted as derived stages. The chapter describes the planned design and implemented analytical rules, not empirical outcomes. No achieved totals, rates, comparisons, or risk distributions are presented here.

The methodology follows the implemented final-study boundary where it differs from earlier proposals or protocol iterations. It is therefore a record of what was frozen and performed for the v2.6 study, rather than a description of superseded multi-ecosystem, survey, execution, or risk approaches. The sections proceed from design and inputs through collection, derived analysis, and interpretation safeguards.

## 3.2 Research Design

The study used a quantitative, controlled, repeated experimental design. A fixed set of Node.js coding tasks was submitted to fixed model conditions through separate fresh requests, after which explicit package references were processed through deterministic and evidence-based analytical stages. The design supports descriptive summaries and, where data permit, comparisons across model condition and functional task category. It was not designed to test directional hypotheses or to attribute outcomes to hidden properties such as architecture, training data, alignment, or provider infrastructure.

Control, repetition, and traceability guided the design. Task wording, outer template, rendered prompts, model configuration, and the observation manifest were frozen before official collection. Content digests bound the frozen inputs to the collection and analysis record. Each task-condition combination was planned for three separate fresh requests because the generation seed was uncontrolled. Repetition describes the request protocol and does not establish statistical independence. Raw evidence was preserved separately from all derived outputs, allowing an analytical claim to be traced from a reported classification to the source response without rewriting that response.

The frozen design contained 30 tasks, four model conditions, and three repetitions, giving 360 planned observations. An observation is one generation for a task, condition, and repetition, identified by a run identifier in the manifest. This is a planned design total rather than an achieved or eligible sample count. Earlier protocol versions are retained as methodological evidence but are not pooled with the v2.6 analysis.

The design was prospective in the sense that the inputs, outcome definitions, eligibility criteria, and comparison procedure were established before the final v2.6 analysis. It does not remove all sources of uncertainty: provider behaviour, unconstrained generation seeds, task heterogeneity, and later adjudication evidence remain relevant to interpretation. Rather, it specifies how those uncertainties are recorded or bounded, and prevents a response from being replaced or a denominator revised after the response content is known.

The sequence of derived stages also defines the order of methodological inference. A response first becomes a preserved collection record; its status then determines whether it can contribute to metrics; explicit references are subsequently extracted and normalised; registry evidence and contextual review inform classification; and only then can a controlled confirmation or dependency-resolution state be aggregated. Risk scoring follows confirmation rather than preceding it. This order limits circular reasoning, since an apparent practical consequence, a registry absence, or an expected group difference cannot independently determine the primary outcome.

**Table 3-1. Summary of the frozen v2.6 study design and analytical coverage**

| Element | Implemented specification |
| --- | --- |
| Design | Quantitative, controlled, repeated experiment; descriptive and, where estimable, comparative analysis |
| Ecosystem | Node.js runtime and npm registry only |
| Inputs | 30 frozen tasks in six categories; common prompt template and rendered prompts |
| Conditions | Four frozen model/API configurations; three planned fresh repetitions |
| Planned observations | 30 × 4 × 3 = 360 |
| Primary outcomes | Package Hallucination Rate (PHR) and Session Hallucination Rate (SHR) |
| Secondary outcomes | Dependency Failure Rate (DFR) and Response Dependency Failure Rate (RDFR) |
| RQ coverage | RQ1: extraction, validation, adjudication and PHR/SHR; RQ2: DFR/RDFR; RQ3: grouped analysis; RQ4: post-classification risk assessment |

## 3.3 Experimental Scope and Study Variables

The empirical scope was restricted to direct npm dependency references in Node.js responses. Restricting the study to one runtime and registry held registry conventions and validation procedures constant and permitted one tested extraction and classification boundary. The findings therefore do not estimate package-reference reliability in other programming languages, registries, or code-generation settings.

The study examined explicit syntactic references to packages, rather than dependencies inferred from narrative prose or transitive dependencies of a named package. Node.js built-ins, `node:` imports, and relative, local, filesystem, file, and web references were outside the external npm boundary. The study did not install, execute, or functionally test generated code or packages. It consequently did not test version compatibility, API suitability, functional correctness, or real-world effects. It involved no human participants, developer surveys, autonomous-workflow comparison, mitigation experiment, package registration, or attack simulation.

The structural factors were model condition, functional task category, and repetition. A model condition was a frozen combination of exact model identifier, provider, routing constraint where applicable, and output-token ceiling. Categories were balanced design groups rather than manipulated treatments. Repetitions were separate fresh requests under the same frozen inputs. The controlled interaction consisted of a single user message with no previous context; tools, browsing, retrieval, function calling, and code execution were unavailable. Temperature was 0.6 and top-p was 0.95. The seed was uncontrolled, and provider-side versions and serving behaviour were recorded only where exposed. Outcome definitions are specified in Sections 3.6 to 3.13.

These factors support comparisons between the frozen conditions, not claims about causal differences in model architectures or training data. The condition-specific output ceiling is part of the condition definition and means that conditions did not share an identical output budget.

At package level, each unique normalised package reference was associated with registry evidence, a classification, and, where review was required, an adjudicated outcome. These records supplied two distinct derived indicators: controlled confirmation of a package-name hallucination and exact-name dependency-resolution failure. At response level, the collection status determined eligibility and an eligible response could be positive or negative for confirmed hallucination. The later risk score applied only to eligible confirmed findings. Keeping these levels distinct prevents the number of mentions in a lengthy response from becoming a response-level outcome and prevents a registry result from being treated as a research classification.

The design did not use developer expertise, workflow autonomy, or verification assistance as explanatory variables. It therefore does not evaluate how a developer would detect, correct, install, or act on a generated recommendation. Similarly, functional category was retained as a transparent grouping dimension, not as a claim that the six categories exhaust technical work or that individual tasks within a category are interchangeable. These choices give the comparison a defined, reproducible boundary while narrowing the inferences that can be drawn from it.

## 3.4 Task and Prompt Construction

### 3.4.1 Frozen task set and category design

The frozen `final-2.0.0` task set comprised 30 self-contained TypeScript-for-Node.js coding tasks, distributed evenly across six functional categories. The tasks required bounded implementations, `package.json` content with exact dependency versions and scripts, package API explanation, and reproducible commands. They were designed to elicit explicit dependency recommendations in specialised domains, rather than to represent all routine Node.js work.

**Table 3-2. Functional task categories and planned design allocation**

| Code | Functional task category | Tasks | Planned observations |
| --- | --- | ---: | ---: |
| `AUTH-FED` | Identity, Authentication & Federation | 5 | 60 |
| `PKI-CRYPTO` | PKI, Cryptography & Trust Services | 5 | 60 |
| `DOC-BINARY` | Complex Documents & Binary Formats | 5 | 60 |
| `ENT-INT` | Enterprise Messaging & Interoperability | 5 | 60 |
| `DATA-ADV` | Specialized Data & Storage Integration | 5 | 60 |
| `DIST-OBS` | Distributed Systems & Observability | 5 | 60 |
| **Total** |  | **30** | **360** |

Package selection was left neutral. No task named a package, requested obscure packages, mentioned hallucination, or asked the model to validate availability. Pre-freeze review narrowed excessive implementation volume while retaining the specialised standards, formats, protocols, and package requirements that motivated the task. Sixteen tasks were minimally narrowed; one was reviewed but retained unchanged. All such decisions preceded official generation, so model outputs did not influence task wording. The full task list is retained in [APPENDIX REFERENCE PENDING].

The tasks were designated medium difficulty using a qualitative rubric: a realistic backend requirement involving several meaningful steps, achievable in one self-contained response, and understandable without clarification. The designation was neither externally calibrated nor an analytical variable. Tasks were not assumed to have equal complexity, code length, or dependency count, which limits generalisation.

### 3.4.2 Prompt freezing and manifest

Each prompt was deterministically rendered by inserting one task specification into a common outer template. The template required a direct, complete response and stated that no existing project, filesystem, terminal, browser, tools, external execution environment, or prior files were available. It required all requested code, package configuration, examples, explanations, and commands to appear in the response. Thus, the generated answer was a self-contained textual artefact and each condition was subject to the same interaction boundary.

The task file, template, rendered prompts, configuration, and manifest were frozen before collection. Rendering checks confirmed task/category structure and matched each output to its frozen prompt. For a given task, every model condition received byte-identical prompt text. Detailed digests and template metadata are retained in [APPENDIX REFERENCE PENDING].

The manifest enumerated 360 rows in advance, each with a run identifier, task, category, condition, repetition, rendered-prompt identity, and expected prompt digest. It fixed the collection order, rotating the within-task condition position to avoid a condition always being collected first. The manifest is a design record, not evidence that every row became an eligible response.

The task set was intentionally dependency-intensive. Its domains included identity and federation, public-key and trust services, complex document formats, enterprise interoperability, specialised data and storage, and distributed-system observability. Such requirements ordinarily require a code generator to make explicit library recommendations rather than relying solely on the Node.js standard library. That choice improves the opportunity to observe the study construct, but also means that the results cannot be interpreted as a prevalence estimate for simple programming questions or for all software-development prompts. A task was not selected because a particular package was expected to fail or exist; package evidence was obtained only after generation.

Prompt rendering also separated task content from model treatment. The outer instructions told a model to produce the requested implementation directly, but did not prescribe a programming strategy or package choice. They did not contain a warning to check package availability, since such a warning would alter the generation context whose recommendations were being measured. The same constraint against tools and external context applied to every condition. The frozen rendered prompt was therefore the operational input, rather than an informal interpretation of the task wording at collection time.

[FIGURE 3-1 TO BE DRAWN]

Title:
Figure 3-1. Frozen task-condition-repetition design.

Purpose:
Show the fixed design structure and planned, rather than achieved, observation total. The layout must not imply formal statistical independence.

Required content:
- Six functional task categories, each containing five frozen tasks, leading to 30 frozen tasks.
- A factorial sequence: 30 frozen tasks × four model conditions (M1 to M4) × three planned repetitions (R01 to R03) = 360 planned observations.
- A note that repetitions are separate fresh requests and do not establish statistical independence.
- A note that 360 is a planned design total, not an achieved or analytically eligible count.

## 3.5 Model Conditions and Data Collection

### 3.5.1 Frozen model conditions

Four frozen model conditions, M1 to M4, received the rendered prompts. Their identifiers, providers, routing constraints, and output-token ceilings are reported as frozen, rather than updated to later provider naming. Shared sampling settings were temperature 0.6 and top-p 0.95; seed was not controlled. No condition had a fallback model. The settings and interaction format were held constant, but hidden model and provider characteristics were not observed or controlled.

**Table 3-3. Frozen model conditions in the v2.6 experiment**

| Condition | Frozen model identifier | API provider | Underlying-provider constraint | Output-token ceiling |
| --- | --- | --- | --- | ---: |
| M1 | `cohere/north-mini-code:free` | OpenRouter | Pinned to `cohere`; fallback disabled | 64,000 |
| M2 | `qwen/qwen3.8-27b` | OpenRouter | Restricted to Darkbloom only; no fallback | 32,768 |
| M3 | `openai/gpt-oss-120b` | Groq | Not applicable | 65,536 |
| M4 | `nvidia/nemotron-3-ultra-550b-a55b:free` | OpenRouter | Pinned to `nvidia`; fallback disabled | 65,536 |

For routed conditions, the frozen provider constraint was requested and fallback was disabled. A provider identity mismatch was retained as a protocol deviation and, for M2, constituted failure. These configurations are experimental conditions, not model-architecture treatments.

### 3.5.2 Hybrid collection and preservation boundary

The manifest assigned 180 rows to automated API collection and 180 to manual collection. Assignment was planned and recorded, not randomised. It is distinct from analytical eligibility: an API-assigned row that failed remained API-assigned and was not moved to the manual route to obtain a replacement. Manual-route operational detail is retained in [APPENDIX REFERENCE PENDING].

API requests followed the manifest sequentially. The collector verified the frozen prompt and applicable condition before submission, retained the prompt, request, raw provider response, assistant content, safe metadata, and attempt history, and prevented an existing run record being overwritten. Retries were permitted only for infrastructure faults; content never triggered a retry, substitution, or fallback. A final failure was preserved once and collection continued. Credentials were excluded from preserved records. Detailed request configuration and recovery mechanics are retained in [APPENDIX REFERENCE PENDING].

The preservation record included the requested and, where exposed, returned model identity, provider route, sampling parameters, output ceiling, timestamps, token-use information, and declared finish reason. These fields allow collection fidelity and status to be inspected without implying that unavailable provider-side details were known. A route mismatch was recorded as a deviation rather than silently accepted. The workflow also distinguished a transport or provider fault from answer content: retries addressed only the former, while an answer was never regenerated because it was short, inconvenient, incomplete in substance, or apparently unreliable. This rule prevented selection of a preferred response after observing its content.

The API and manual routes were operational means of collecting preassigned manifest rows. They were not intended as a comparison between interfaces, and no conclusion about interface effects is planned. Recording assignment nevertheless preserves a factual account of the collection process and prevents a failed assigned row from disappearing through reassignment. The one-way preservation boundary in Figure 3-2 is consequently both a data-integrity principle and a methodological separation: analysis may derive an inventory or classification from raw evidence, but cannot change the response that created it.

[FIGURE 3-2 TO BE DRAWN]

Title:
Figure 3-2. Final v2.6 experimental workflow and preservation boundary.

Purpose:
Show how frozen inputs become preserved response evidence and how later analysis reads, but never rewrites, that evidence.

Required content:
- Frozen inputs: task set, template, rendered prompts, model configuration, and manifest.
- Assigned collection route: API or manual, followed by preserved response evidence: prompt, request, raw provider response, assistant content, metadata, and attempt history.
- A clearly labelled preservation boundary after the preserved evidence; arrows must cross it in one direction only.
- Derived response inventory and status, extraction, registry evidence, classification/adjudication, analytical dataset, metrics/statistics, and risk assessment after the boundary.
- A note that raw evidence is not rewritten by later stages; do not depict installation, execution, collection completion, or results.

## 3.6 Response Preservation, Status, and Analytical Eligibility

Raw records were append-only evidence. Later stages read them and produced separate derived outputs; a status correction was a provenance-bearing overlay rather than a raw-record alteration. Every finalised observation was classified as COMPLETED, TRUNCATED, or FAILED. Only completed responses were analytically eligible, at both response and package levels.

**Table 3-4. Response status and analytical eligibility**

| Status | Definition | Extraction | Primary and secondary metric treatment |
| --- | --- | --- | --- |
| COMPLETED | Valid response with finish reason `stop` | Yes | Eligible; completed zero-package responses remain in the SHR denominator |
| TRUNCATED | Finish reason `length`, indicating output ceiling reached | Yes, marked as truncated | Preserved but excluded from numerator and denominator |
| FAILED | No valid `stop` or `length` response, including other provider finish reasons | No | Preserved once and excluded from analysis |

An abnormal finish reason, including `error`, was treated as FAILED even if partial content existed. This rule distinguishes a provider failure from truncation, which specifically denotes the frozen output ceiling. An interrupted sent request was likewise finalised once as failed, not regenerated. Pending or unfinalised rows had no final status and were not analysed.

Collection route and status remained separate. Package eligibility was inherited from response eligibility, so package rows from a failed response could not enter a metric. Truncated text could be extracted for preservation and quality reporting but was excluded because the ungenerated remainder could have changed its references. A completed response with no external package reference generated no PHR package unit, but remained an SHR-denominator response with no confirmed hallucination.

The exclusion policy is a rule about estimands, not a deletion policy. A truncated or failed observation remains material to any account of collection completeness and data quality, but it does not contribute partial evidence to a rate intended to describe completed responses. Similarly, a completed response may be eligible even if it supplies no external package unit. Package-level and response-level denominators therefore answer different questions: PHR concerns eligible direct package recommendations, whereas SHR concerns eligible responses. Neither status nor eligibility was inferred from later registry evidence or adjudication.

Status was assigned from the preserved collection record and then carried forward through the derived inventory. This procedure avoids interpreting partial provider content as a completed answer merely because it contains extractable text. It also avoids treating a failed attempt as a zero-package negative response. Where a provider exposed a reason other than normal completion or the length ceiling, the failure rule applied consistently irrespective of the text's apparent usefulness. The retained inventory makes these distinctions available for later completeness reporting without mixing them into the primary rates.

## 3.7 Package Reference Extraction and Normalisation

The deterministic extraction stage read preserved content from completed and truncated responses without querying a registry, installing a package, or executing code. It extracted only direct, explicit npm-reference forms: literal static ESM imports, literal CommonJS `require` calls, literal dynamic imports, `npm install` or `npm i` operands, and valid JSON dependency entries in `dependencies`, `devDependencies`, `peerDependencies`, or `optionalDependencies`. Narrative mentions, transitive dependencies, non-literal specifiers, re-exports, `require.resolve`, and other package-manager commands were not extracted.

**Table 3-5. Extraction, normalisation, and exclusion boundary**

| Aspect | Rule |
| --- | --- |
| Input | Preserved assistant content from completed and truncated responses |
| Supported forms | Literal imports and `require`; literal dynamic imports; npm install operands; valid `package.json` dependency objects |
| Normalisation | Reduce subpaths to root package; retain scoped `@scope/package`; retain stated version metadata without version-level analysis |
| Excluded references | Node.js built-ins and `node:`; relative, absolute, home-directory, `file:`, and HTTP(S) references; npm aliases and malformed names |
| Not extracted | Narrative-only references, transitive dependencies, unsupported syntax, and other package-manager commands |
| Package unit | Unique `(run_id, normalized_package)`; source occurrences retained as provenance |

For example, an unscoped subpath was normalised to its first package segment, whereas a scoped subpath retained scope and package. Normalisation was determined before registry evidence, so exclusion did not depend on whether a name existed. The occurrence record retained source form and text location; the analytical package unit deduplicated repeated mentions of the same normalised package within one response. The same normalised name in another response remained a separate package unit.

The extraction boundary was deliberately narrower than every possible way a dependency can appear in generated software. It provides a stable unit that can be reproduced from preserved text, rather than relying on a reviewer to infer intent from prose. An import, install command, or dependency declaration makes an explicit external package claim that can be normalised and checked. By contrast, a narrative assertion that a package might be useful is not transformed into an analytical observation, and neither is a dependency that might be reached only through another named package. The choice restricts the construct but avoids conflating direct package recommendation with broader semantic interpretation.

Version syntax was preserved for provenance but did not create a version-resolution analysis. The registry lookup asked whether the normalised package name had evidence in npm, not whether a version range was available, compatible, secure, or appropriate for the stated code. Similarly, an existing exact-name package was not functionally inspected. A valid registry result therefore answers a limited availability question and is not evidence that a generated implementation would work. These boundaries are relevant when interpreting both valid references and dependency-reliability outcomes.

## 3.8 npm Registry Validation

Normalised external npm package names were validated through read-only requests to the official npm registry. The validation stage recorded the request and response evidence needed to interpret a lookup at its validation time, but neither installed nor claimed a package. Infrastructure retries and caching supported collection of registry evidence without changing the meaning of a request; detailed timing and storage behaviour are retained in [APPENDIX REFERENCE PENDING].

The resulting evidence state was `exists`, `not_found`, or `unresolved`. `exists` indicated successful registry evidence for the exact normalised name. `not_found` indicated an official absence response at the recorded time. `unresolved` indicated that a usable registry conclusion could not be obtained. These are evidence states, not research classifications. In particular, a 404 or `not_found` is not automatically a package-name hallucination: the name may be a local project reference, a legacy name, a namespace error, an ecosystem confusion, or an unresolved ambiguity.

Registry evidence was time-bounded and retained with provenance. The study did not infer a package's historical state from a contemporary lookup without supporting evidence in adjudication.

The registry stage followed the normalised name rather than the surface text alone, allowing import subpaths and installation operands to be assessed against the package root that npm resolves. It was intentionally read-only: no name was reserved, registered, published, or otherwise acted upon in response to a lookup. An absence response can be meaningful evidence, but its research interpretation requires the later contextual checks. For example, an apparent absence may reflect a renamed or removed package, the wrong scope, a name from another ecosystem, an invalid type-definition convention, or a reference that the response itself declares as local. The three evidence states preserve uncertainty instead of converting failed validation into a negative fact.

## 3.9 Classification and Adjudication

### 3.9.1 Conservative classification

Classification combined normalisation, registry evidence, and review evidence. An `exists` result was classified as valid for the exact-name boundary. An `unresolved` result did not become a finding. A `not_found` result was routed to review rather than directly to confirmation. Review assessed whether the name had prior existence, was an external npm reference, and remained ambiguous after considering the response and dated evidence.

**Table 3-6. Registry-to-adjudication routes and final taxonomy**

| Evidence or outcome | Interpretation and metric relevance |
| --- | --- |
| `exists` / VALID | Exact normalised name resolved; external non-failure for DFR where eligible |
| `unresolved` | No registry conclusion; not a hallucination and undetermined for secondary analysis |
| `not_found` / review required | Requires classification and, where needed, adjudication; never confirms hallucination alone |
| CONFIRMED_HALLUCINATION | External reference with required confirmation evidence; eligible for controlled primary routing |
| LEGACY_OR_REMOVED, NAMESPACE_CONFUSION, PACKAGE_NAME_CONFUSION, INVALID_OR_REDUNDANT_TYPES_PACKAGE, ECOSYSTEM_CONFUSION, OTHER_DEPENDENCY_ERROR | Resolved alternatives to confirmed hallucination; dependency-failure status recorded separately |
| SELF_REFERENCE_OR_LOCAL_PACKAGE | Response-supported non-external reference; neither primary confirmation nor external secondary unit |
| UNRESOLVED | Insufficient evidence for a specific outcome; not a primary confirmation and undetermined for secondary analysis |

Adjudication considered review-required cases at the unique response-package level, because context can establish that the same name is an external recommendation in one response but a project's own package name in another. It used dated, recorded evidence and a written rationale. A self/local outcome required response-internal evidence of a matching declared project, local, or workspace name; it could not be inferred from registry absence. The researcher performed adjudication, so no independent reviewer or inter-rater agreement is claimed. Detailed adjudication records and checks are retained in [APPENDIX REFERENCE PENDING].

The taxonomy separates confirmed package hallucination from exact-name dependency failure. Several resolved non-hallucination outcomes can still denote that a named dependency would fail to resolve, whereas self/local references are not external claims. Unresolved evidence is not forced into either category. This separation prevents namespace, package-name, or ecosystem confusion from being relabelled as confirmed hallucination.

### 3.9.2 Controlled confirmation route

Primary confirmation was resolved once during analytical dataset construction. A package row could be confirmed through either a reviewed classification that established `CONFIRMED_HALLUCINATION`, or a guarded adjudication of a previously ambiguous, review-required row that established the same outcome. The confirming route and provenance were recorded, and a row could be counted only once. All other taxonomy outcomes, unadjudicated review-required rows, and unresolved cases remained outside primary numerators. They were not silently removed from the primary package denominator.

This controlled route ensured that a registry-absent name was not counted merely because it followed one operational path rather than another. Inconsistent, duplicate, unmatched, or unsupported provenance did not produce a primary confirmation. Figure 3-3 depicts the separation of extraction, registry evidence, adjudication, and metric routing.

The deterministic classification and the later adjudication were additive rather than competing attempts to rewrite a case. A reviewed classification could already contain sufficient evidence for a confirmation or alternative outcome. The dedicated adjudication process addressed cases initially retained as ambiguous and review-required, applying the same external-reference and historical-existence concerns together with context-specific checks. The analysis builder then resolved whether the evidence entered the primary metric, retaining the route rather than collapsing all intermediate records into a single unsupported label. This arrangement ensures that primary outcomes are not revised merely because a separate analytic output uses a more detailed taxonomy.

For secondary analysis, the adjudication record separately states whether the dependency as named would fail to resolve and whether it is an external dependency claim. These are not inferred simply from the taxonomy label where a context-specific judgement is required. Consequently, an outcome such as namespace confusion can be an exact-name failure without becoming a confirmed package-name hallucination. Conversely, an unresolved case remains uncertain rather than being treated as a valid dependency. The taxonomy makes that distinction visible to later metrics and avoids a false equivalence between non-existence, error, and hallucination.

[FIGURE 3-3 TO BE DRAWN]

Title:
Figure 3-3. Direct npm extraction, registry evidence, and conservative adjudication pipeline.

Purpose:
Show the direct npm-only reference boundary and make clear that registry absence is evidence requiring review, not a hallucination outcome.

Required content:
- Preserved completed and truncated response content → direct reference extraction and normalisation → excluded non-external references separated before lookup.
- Official npm registry evidence: `exists`, `not_found`, or `unresolved`.
- `exists` → valid; `unresolved` → unresolved, not a finding; `not_found` → review-required and adjudication.
- Adjudication outcomes including confirmed hallucination, legacy/removed, confusion, self/local, other dependency error, and unresolved.
- A controlled confirmation route to primary metrics that accepts confirmation once and keeps `not_found` distinct from confirmation.
- No installation, execution, package claiming, or automatic 404-to-hallucination arrow.

## 3.10 Primary Package-Hallucination Metrics

The primary analysis used PHR at package level and SHR at response level. Both used only eligible completed evidence after extraction, registry validation, classification, adjudication where required, and controlled confirmation resolution.

$$
\mathrm{PHR}=\frac{\text{confirmed metric-eligible unique }(run\_id,\ normalized\_package)\text{ rows}}{\text{all metric-eligible unique package rows}}
$$

$$
\mathrm{SHR}=\frac{\text{eligible completed responses containing at least one confirmed hallucination}}{\text{all eligible completed responses}}
$$

PHR counts each normalised package once within a response, avoiding inflation from repeated imports or installation commands. SHR counts a response once if it contains one or more confirmed package hallucinations. Completed responses with no extracted package remain SHR-denominator members but create no PHR package row. Truncated and failed responses are excluded from both primary numerators and denominators. Registry-unresolved, review-required, adjudication-unresolved, and self/local package rows remain in the PHR denominator but not its numerator; the secondary external-dependency field does not alter this primary denominator.

The two measures answer complementary questions. A response with several distinct confirmed references adds one positive session to SHR but can add several package rows to PHR. A completed response that recommends no package is relevant to the response-level probability of a confirmed recommendation but has no package-level item to count. Repeated occurrences of the same package are traceable in the occurrence records but do not inflate PHR. These definitions were fixed before final analysis so that neither denominator could be adjusted in response to observed package frequency or review uncertainty.

Primary confirmation is deliberately stricter than registry absence. A name entered the numerator only after the defined confirmation route established a confirmed hallucination. Resolved alternatives such as legacy or removed names, namespace and package-name confusion, ecosystem confusion, self/local reference, and other dependency errors did not enter the numerator. This does not assert that those alternatives are harmless or correct; it recognises that they represent different research classifications. Their treatment in the secondary measures is specified independently below.

**Table 3-7. Primary and secondary metric definitions**

| Metric | Unit and point estimate | Eligibility and interpretation |
| --- | --- | --- |
| PHR | Confirmed unique package rows / all eligible unique package rows | Primary package-hallucination rate |
| SHR | Eligible completed responses with ≥1 confirmed hallucination / all eligible completed responses | Primary response-level hallucination rate; includes zero-package completions |
| DFR | F / (F + N), where F is external exact-name failure and N external non-failure | Secondary/exploratory dependency-resolution measure; U is excluded from point estimate and informs bounds |
| RDFR | P / (R - I), where P is positive response, R eligible completed responses, and I indeterminate responses | Secondary/exploratory response measure; zero-package and self/local-only responses are negative |

[FIGURE 3-4 TO BE DRAWN]

Title:
Figure 3-4. Derivation of primary and secondary metrics.

Purpose:
Distinguish the controlled primary hallucination measures from the secondary dependency-reliability measures.

Required content:
- Primary branch: eligible completed responses and metric-eligible package rows → controlled confirmed-hallucination resolution → PHR and SHR.
- Secondary branch: eligible exact-name external dependency evidence → `dependency_failure` true, false, or undetermined → DFR; eligible completed responses → `POSITIVE`, `NEGATIVE`, or `INDETERMINATE` → RDFR.
- A clear visual label that DFR and RDFR are secondary dependency-reliability metrics, not hallucination rates.
- Eligibility and controlled resolution must be shown before the respective metric outputs.

## 3.11 Secondary Dependency-Reliability Metrics

DFR and RDFR were secondary, exploratory measures of exact-name npm dependency resolution. They do not replace PHR or SHR and are not hallucination rates. DFR does not capture all dependency unreliability: wrong-but-existing packages, version-resolution errors, API errors, capability mismatch, and functional unsuitability remain outside its construct.

At package level, an eligible row was classified as external failure (F), external non-failure (N), undetermined (U), or non-external. An exact-name valid registry result was an external non-failure. Resolved adjudication could establish a failure or non-failure; self/local references were non-external. Registry-unresolved, unadjudicated review-required, reviewed ambiguous, and adjudication-unresolved rows were U rather than assumed failures or non-failures. DFR excluded U from its point-estimate denominator and reported lower and upper bounds by treating U respectively as non-failure and failure. Estimable point estimates were accompanied by Wilson 95% confidence intervals and counts by failure outcome and undetermined reason.

At response level, any external failure made an eligible response POSITIVE. If no failure was present but one or more package states were undetermined, it was INDETERMINATE. Otherwise it was NEGATIVE. Thus, completed zero-package responses and responses containing only self/local references were negative. RDFR excluded indeterminate responses from its point-estimate denominator, with bounds treating them respectively as negative and positive; estimable values received Wilson 95% confidence intervals. A completeness label distinguished final outputs from incomplete evidence chains without altering states or point estimates.

The bounds disclose the effect that unresolved evidence could have on the secondary estimate without declaring a single unsupported status for it. At package level the lower bound treats every U as non-failure and the upper bound treats every U as failure. At response level the lower bound treats every indeterminate response as negative and the upper bound treats it as positive. The point estimate remains restricted to resolved states. This approach does not turn the secondary analysis into a lower or upper bound on all possible dependency unreliability; it is limited to exact-name resolution under the stated extraction, registry, and adjudication rules.

The secondary metrics use the same completed-response eligibility boundary as the primary measures so that a partial or failed collection record does not become a dependency-resolution observation. Their denominators differ from PHR and SHR because they exclude non-external references and, for point estimates, unresolved states. For this reason a DFR or RDFR value cannot be interpreted as a package-hallucination rate, compared mechanically with PHR or SHR, or substituted for the primary measures in answering RQ1.

## 3.12 Grouped and Statistical Analysis

The grouped analysis first produced descriptive primary-metric summaries by model condition, functional task category, repetition, and model-condition-by-category combination. It retained denominators and the status counts needed to interpret eligibility exclusions. The inferential procedure then considered the binary primary outcomes only: package-level confirmed versus not confirmed, and response-level presence versus absence of a confirmed hallucination. It did not calculate grouped DFR or RDFR comparisons, impose rankings, or turn unavailable comparisons into conclusions.

**Table 3-8. Prespecified inferential selection procedure**

| Comparison condition | Procedure and reporting |
| --- | --- |
| Fewer than two groups with non-zero denominators | `not_testable`; report reason and excluded groups |
| Exactly two usable groups | Two-sided Fisher's exact test; odds ratio and risk difference with 95% confidence intervals |
| More than two usable groups with every expected cell ≥ 5 | Omnibus Pearson chi-square; pairwise Fisher tests with Holm adjustment |
| More than two usable groups with sparse expected cells | Deterministic fixed-margin 2 × C Monte Carlo procedure, 20,000 iterations, seed `1234567891`; pairwise Fisher tests with Holm adjustment |

The odds ratio used a Haldane-Anscombe correction only if a zero cell otherwise made it undefined; risk-difference intervals used the Newcombe/Wilson-score method. Zero-denominator groups were excluded rather than treated as zero-risk groups. All-zero and all-one outcomes in otherwise usable groups did not automatically make a comparison untestable: Fisher remained available for two groups, while zero expected cells selected the Monte Carlo path for a multi-group table. Effect estimates, confidence intervals, denominators, and eligibility exclusions accompany statistical output. Findings are interpreted as comparisons within the frozen conditions, not causal estimates of model architecture or task-domain effects.

The procedure was chosen before final inference to make test selection depend on table structure rather than a preferred result. For a two-group comparison, Fisher's exact test is used because it remains applicable with sparse observed outcomes. For a multi-group comparison, the chi-square route requires every expected cell to meet the stated threshold; otherwise the fixed-margin Monte Carlo procedure is used. Pairwise testing follows an applicable omnibus comparison and uses Holm adjustment across the complete set of usable pairwise p-values in that comparison. A `not_testable` output records an unavailable comparison rather than evidence of equality, non-significance, or absence of risk.

Grouped outputs report the counts that form each denominator, not only a rate. This is necessary because differing numbers of completed observations or package units can affect the precision and interpretability of a comparison. The model-condition-by-category grouping permits inspection of the frozen factorial layout but should not be mistaken for an unrestricted higher-dimensional inferential model. Repetitions are reported as planned grouping levels and descriptive sources of variation; their use does not remedy dependence arising from shared tasks, shared prompts, or common service environments.

## 3.13 Practical-Risk Assessment

Practical-risk assessment used `risk-model-1.0.0` after a finding had been confirmed and was eligible for scoring. It did not determine classification. Impact was scored from 1 to 5 according to the consequence supported by the generated recommendation and task context. Detectability was scored from 1 to 4 according to the earliest ordinary development control likely to identify the issue. Each score required a documented rationale and supporting evidence.

$$
\text{Risk score}=\text{Impact}\times\text{Detectability}
$$

**Table 3-9. `risk-model-1.0.0` Impact × Detectability matrix**

| Impact \ Detectability | 1 | 2 | 3 | 4 |
| --- | ---: | ---: | ---: | ---: |
| 1 | 1 | 2 | 3 | 4 |
| 2 | 2 | 4 | 6 | 8 |
| 3 | 3 | 6 | 9 | 12 |
| 4 | 4 | 8 | 12 | 16 |
| 5 | 5 | 10 | 15 | 20 |

Scores of 1 to 4 were LOW, 5 to 8 MODERATE, 9 to 14 HIGH, and 15 to 20 CRITICAL. Insufficient evidence produced an unscored record rather than a score of zero. `security_sensitive_context` was a separate non-scored Boolean with a written rationale; it identified security-relevant contexts without changing the formula. The framework is an ordinal prioritisation aid, not a probability model for exploitation, installation, package claiming, financial loss, or real-world incidents.

Impact concerns the practical consequence supported by the generated recommendation and the documented task context, ranging from negligible effect to a supported potential consequence for security, integrity, or software-supply-chain concerns. Detectability concerns the earliest ordinary development control likely to identify the particular issue, ranging from immediately apparent dependency resolution to detection requiring relevant package or domain knowledge. Neither dimension represents likelihood. The score was applied after classification, so a high-scoring hypothetical concern could not establish a hallucination where evidence remained unresolved.

The required written rationales, evidence links, assessor identity, assessment time, and source provenance allow a score to be audited as a rule-based judgement. `security_sensitive_context` covers contexts such as authentication, authorisation, cryptography, secret handling, integrity enforcement, access control, and supply-chain trust, but it does not automatically raise or lower the numeric band. The framework is therefore a transparent prioritisation convention for eligible confirmed findings, not an assessment of whether a developer would install the recommendation or whether an attack would occur.

[FIGURE 3-5 TO BE DRAWN]

Title:
Figure 3-5. `risk-model-1.0.0` Impact × Detectability framework.

Purpose:
Show the rule-based prioritisation framework applied after confirmation, without representing risk as a probability.

Required content:
- Eligible confirmed package-hallucination finding → Impact (1 to 5) and Detectability (1 to 4) with documented rationales.
- Risk score = Impact × Detectability.
- Bands: LOW 1 to 4; MODERATE 5 to 8; HIGH 9 to 14; CRITICAL 15 to 20.
- `security_sensitive_context` as a separate non-scored attribute with a rationale.
- Do not depict exploit probability, installation probability, attack probability, or financial-loss probability.

## 3.14 Validation and Quality Assurance

Validation addressed the derived-analysis infrastructure using synthetic fixtures only. The final validation record reported 126 passing focused tests for adjudication and the analysis stages, including a 44-test focused subset. The full suite recorded 327 passing tests and two known historical fixture failures caused by raw directories absent from this worktree. Its verdict was `PASS WITH DOCUMENTED LIMITATIONS`.

The validation tested response eligibility, zero-package treatment, controlled confirmation routing, provenance consistency, package and response reconciliation, secondary states and bounds, deterministic statistical selection, and rejection of inconsistent evidence. These checks support correct implementation of the specified rules, not the accuracy of final empirical findings or individual researcher judgements. They do not establish inter-rater reliability, predictive performance, temporal validity, or generalisability. Final empirical analysis still requires a provenance-consistent collection and adjudication snapshot.

Synthetic fixtures were used so that validation could exercise the decision rules without creating or altering experimental observations. The checks included malformed or mismatched provenance, duplicate or dual confirmation routes, status inheritance, zero denominators, and sparse statistical tables. They also reconciled package-level and response-level totals with the corresponding primary metric definitions. A passing validation result therefore supports the internal operation of the software and schemas under controlled test cases; it is not a claim that all future registry judgments, provider responses, or human adjudications will be correct.

Quality assurance also relied on separation of stages. Extraction did not alter collection data, registry validation did not supply a classification by itself, and risk scoring could not feed back into confirmation. This makes it possible to inspect a later-stage inconsistency against the preserved response and preceding derived outputs. The approach is intended to support reproducibility and auditability of the defined method; it does not make a prospective study immune to incomplete collection, registry change, or uncertainty that the method explicitly retains.

## 3.15 Research Integrity, Safety, and Methodological Limitations

Frozen inputs, append-only raw evidence, and derived-only analysis protected the distinction between observation and interpretation. Frozen task, prompt, configuration, and manifest controls were checked against their identities; raw response content and provider records were not overwritten to obtain preferred outcomes. Derived outputs retained source relationships and timestamps. Denominators and confirmation rules were fixed before final results, and failed or truncated observations were not regenerated, substituted, or pooled from earlier protocol versions.

Generated dependencies and code were neither installed nor executed. npm validation was read-only, and no package name was claimed, registered, reserved, published, or actively exploited. This safety boundary restricted the research to generated references and their documentary classification, avoiding exposure to untrusted artefacts and preserving the stated construct.

The study is limited to direct, supported forms of Node.js/npm references in a bounded design of 30 tasks, four conditions, and three planned repetitions. The medium-difficulty label was not independently calibrated. Extraction excludes narrative implications, transitive dependencies, non-literal and several unsupported forms. The method does not assess execution, functional correctness, package capability, version compatibility, or wrong-but-existing packages. Registry evidence is time-bounded; provider serving and exposed versions were not fully controlled; and the hybrid collection route was operational rather than randomised. Adjudications may remain unresolved, and the rule-based risk framework is not a calibrated forecast. These boundaries limit generalisation beyond the evaluated conditions.

The study's controlled prompt format also differs from ordinary multi-turn development. Each model received one fresh user message and could not inspect a repository, ask follow-up questions, browse documentation, call tools, or test code. This makes the evidence comparable across conditions, but it means that the findings do not show how package references would change after iterative debugging, retrieval, human review, or execution feedback. Likewise, the selected tasks emphasise specialised dependency use, so observed rates should not be generalised to all code-completion settings or used to make a claim about the prevalence of hallucination in all programming activity.

Finally, the status exclusions and conservative adjudication rules prioritise a clearly defined completed-response estimate over broad inclusion of partial and uncertain evidence. They may leave some cases outside a point estimate rather than assigning them a convenient outcome. That is an intended limitation of the measurement design, not evidence that omitted cases were correct, incorrect, or harmless. Chapter 4 must report the relevant eligibility, uncertainty, and completeness information alongside any empirical result.

## 3.16 Chapter Summary

This chapter specified the frozen v2.6 methodology for a Node.js/npm experiment with 30 tasks across six functional categories, four frozen model conditions, and three planned fresh repetitions. It defined prompt freezing, a hybrid collection assignment, response preservation, and the distinction between collection status and analytical eligibility. Only completed responses were eligible for the primary and secondary analyses; truncated and failed responses were retained as evidence but excluded from metric denominators. The package-level analysis used direct explicit reference extraction, normalisation, and read-only official npm registry evidence, followed by conservative classification and adjudication. Registry absence alone did not establish hallucination.

PHR and SHR were defined as the primary measures of confirmed package-name hallucination, with unique `(run_id, normalized_package)` package units and completed zero-package responses retained in the SHR denominator. DFR and RDFR were defined separately as secondary, exploratory measures of exact-name dependency resolution. The chapter also specified prescreened grouped comparisons, effect-size reporting, the post-confirmation Impact × Detectability risk framework, synthetic-fixture validation, and the integrity, safety, and limitation boundaries. Chapter 4 reports empirical results only after final collection and provenance-consistent analysis are complete.

Together, these procedures preserve the distinction between availability evidence, research classification, rate construction, and practical prioritisation. They also ensure that incomplete generation and unresolved evidence remain visible rather than being converted into completed observations or confirmed findings.

All reported empirical interpretation consequently remains bounded by these predefined methodological conditions.
