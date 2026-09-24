# Chapter 3: Research Methodology

## 3.1 Chapter Introduction

Chapter 1 set out four research questions concerning the prevalence of confirmed npm package-name hallucinations (RQ1), the pattern of secondary exact-name npm dependency-resolution failures (RQ2), the variation of these outcomes across model conditions and functional task categories (RQ3), and the practical risk of eligible confirmed findings (RQ4). Chapter 2 showed that reported package-hallucination findings depend on the models, generation settings, tasks, prompts, ecosystems, and measurement rules of the studies that produced them. It also showed that registry evidence alone cannot determine whether a reference is a hallucination. The methodology described in this chapter was designed with both observations in mind. It fixed the experimental conditions before data collection. It also separated the collection of evidence from its interpretation, so that each reported outcome could be traced to preserved inputs and to explicitly defined classification and measurement rules.

This chapter describes the methodology that was implemented for the final study, designated the frozen v2.6 experiment. Where the methodology differs from earlier planning documents, including the baseline dissertation proposal, the implemented study is described and superseded elements are not presented as performed work. Final data collection was still in progress when this chapter was prepared. The chapter therefore reports the planned design, the frozen inputs, and the analytical procedures, but no achieved sample counts, rates, or comparative findings. These are reported in Chapter 4 once the final analysis has been completed and verified.

The chapter is organised in the order in which evidence moved through the study. Section 3.2 presents the overall research design and its relationship to the research questions. Section 3.3 defines the experimental scope and the study variables, and Section 3.4 describes how the coding tasks and prompts were constructed and frozen. Sections 3.5 and 3.6 describe the model conditions, data collection, response preservation, and analytical eligibility. Sections 3.7 to 3.9 describe package-reference extraction, read-only npm registry validation, and classification and adjudication. Sections 3.10 to 3.13 define the primary and secondary metrics, the grouped and statistical analysis, and the practical-risk assessment. Section 3.14 describes validation and quality assurance, Section 3.15 addresses research integrity, safety, and methodological limitations, and Section 3.16 summarises the chapter.

---

## 3.2 Research Design

The study adopted a quantitative, controlled, repeated experimental design. A fixed set of standardised Node.js coding tasks was submitted to a fixed set of model conditions, each task-condition combination was requested separately more than once, and the resulting responses were processed through a deterministic sequence of derived analysis stages. The design was comparative in that outcomes could be grouped and, where the data permitted, compared across model conditions and functional task categories. It was not organised around a set of pre-specified directional hypotheses. The study instead defined its constructs, units of analysis, denominators, and comparison procedures before the final data were analysed, and it describes the resulting outcomes within those predefined boundaries. This bounded empirical design reflects the purpose of the research questions, which ask what is observed under defined conditions rather than whether a particular theoretical expectation is confirmed.

Three design principles shaped the study. The first was control. The task wording, the outer prompt template, the rendered prompt text, the model conditions, the generation settings, and the planned sequence of observations were fixed in a versioned freeze record before official collection began. Each of these inputs was identified by a SHA-256 content digest, so that any later alteration would be detectable. The second principle was repetition. Because LLM outputs are non-deterministic, and because the generation seed was not controlled, a single response per task and condition would provide limited evidence about the stability of a model's dependency recommendations. Each task-condition combination was therefore planned for three separate fresh requests. This terminology describes the request protocol and does not assert statistical independence. The third principle was the separation of evidence from interpretation. Raw model responses and their collection metadata were preserved as the primary evidence, and every subsequent step (package extraction, registry validation, classification, adjudication, metric calculation, grouping, and risk scoring) was implemented as a separate derived stage that read, but did not modify, the preserved evidence. This separation allowed the reasoning from a response to a reported outcome to be inspected stage by stage.

The resulting planned design comprised 30 tasks, four model conditions, and three repetitions, giving 30 × 4 × 3 = 360 planned observations. An observation, in this chapter, denotes one generation for one task under one model condition in one repetition, identified by a unique run identifier in the frozen experimental manifest. The figure of 360 is a planned design total. It is not a count of achieved or analytically eligible responses, because some observations may end in truncation or failure and, under the eligibility rules described in Section 3.6, such observations are preserved but excluded from the primary metrics. The number of achieved and eligible observations is reported in Chapter 4.

The v2.6 experiment was the last in a sequence of versioned protocol iterations. Earlier versions were stopped prospectively when preserved observations revealed operational problems, including, in the versions immediately preceding v2.6, repeated responses reaching the configured output-token ceiling. The v2.6 experiment was not a continuation of an earlier dataset. It was frozen as a fresh 360-observation experiment beginning at its first observation, and it was designated as the final protocol version. Observations from earlier versions were retained as methodological evidence but were excluded from the v2.6 analysis. The changes introduced in v2.6 concerned model-specific output-token ceilings and the provider route for one model condition; the task set and the rendered prompt text were unchanged from the preceding version. These details are described further in Section 3.5.

Within the frozen design, observations were assigned to one of two collection routes: automated collection through provider application programming interfaces (APIs), and manual collection. The planned assignment allocated 180 manifest rows to each route. Interface assignment was recorded separately from analytical eligibility, so that, for example, a failed API observation remained an API-assigned observation while being excluded from metric calculation. The collection procedure is described in Section 3.5. Figure 3-2 in that section presents the overall workflow and the boundary between preserved evidence and derived analysis.

Table 3-1 summarises the design, and Table 3-2 relates each research question to the methodological components that address it.

**Table 3-1. Summary of the frozen v2.6 study design**

| Design element                     | Implemented specification                                                                                          |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Design type                        | Quantitative, controlled, repeated experimental design with descriptive and, where estimable, comparative analysis |
| Ecosystem                          | Node.js runtime and the npm package registry only                                                                  |
| Task set                           | 30 frozen tasks, task-set version `final-2.0.0`                                                                    |
| Functional task categories         | Six categories, five tasks each                                                                                    |
| Model conditions                   | Four frozen conditions, M1 to M4 (Section 3.5)                                                                     |
| Repetitions                        | Three planned separate fresh requests per task-condition combination (R01 to R03)                                  |
| Planned observations               | 30 × 4 × 3 = 360                                                                                                   |
| Unit of package analysis           | Unique normalised package reference per response                                                                   |
| Unit of response analysis          | Eligible completed response                                                                                        |
| Primary metrics                    | Package Hallucination Rate (PHR) and Session Hallucination Rate (SHR)                                              |
| Secondary, exploratory metrics     | Dependency Failure Rate (DFR) and Response Dependency Failure Rate (RDFR)                                          |
| Risk framework                     | `risk-model-1.0.0`, Impact × Detectability                                                                         |

**Table 3-2. Relationship between research questions and methodological components**

| Research question                                                     | Principal methodological components                                                                                    | Sections  |
| --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | --------- |
| RQ1: Prevalence of confirmed npm package-name hallucinations          | Extraction and normalisation; read-only registry validation; conservative classification and adjudication; PHR and SHR | 3.7 to 3.10 |
| RQ2: Secondary exact-name dependency-resolution failure patterns      | Adjudication taxonomy; DFR and RDFR                                                                                    | 3.9, 3.11 |
| RQ3: Variation across model conditions and functional task categories | Frozen factorial structure; grouped descriptive summaries; assumption-gated statistical comparisons where estimable    | 3.3, 3.12 |
| RQ4: Practical risk of eligible confirmed findings                    | Rule-based Impact × Detectability scoring after classification                                                         | 3.13      |

---

## 3.3 Experimental Scope and Study Variables

### 3.3.1 Ecosystem boundary

The empirical scope was restricted to the Node.js runtime and the npm package registry. Earlier planning had envisaged a comparison across more than one language ecosystem, but this was narrowed before the final experiment was designed. The restriction served three methodological purposes. First, it held the registry context constant. Package registries differ in their naming conventions, namespace mechanisms, and lookup interfaces, and Chapter 2 noted that these differences affect how resolution failures arise and can be observed. With one registry, differences in outcomes between model conditions or task categories could not be attributed to differences in registry architecture. Second, it permitted a single, explicitly specified extraction procedure and a single registry-validation procedure, each of which could be examined in detail and tested. A multi-ecosystem design would have required parallel extraction rules, registry integrations, and classification conventions, each of which would introduce its own sources of measurement error. Third, the narrower scope was feasible within the time available for the dissertation while preserving the depth of adjudication that the conservative classification approach required.

The consequence of this choice is that the findings describe npm dependency references in Node.js coding responses. They are not presented as estimates for other package ecosystems, for other programming languages, or for LLM-generated code in general. This boundary is revisited as a limitation in Section 3.15.

### 3.3.2 Construct boundary

Within the Node.js/npm setting, the substantive unit of interest was an explicit, direct reference to an npm package in a generated response. Direct references were those expressed through the syntactic forms supported by the extraction stage, such as import and `require` statements, npm installation commands, and dependency entries in `package.json` content (Section 3.7). References inferred only from narrative prose were not extracted, and the packages on which a named package itself depends (transitive dependencies) were not analysed. Node.js built-in modules, relative and local paths, and file or web references were excluded from the set of external npm references.

The study did not install, execute, or functionally test any generated code or named package. It therefore did not assess whether a generated solution was functionally correct, whether a named package offered the capabilities the response attributed to it, or whether stated version specifiers were appropriate. It also did not register, reserve, or publish any package name, and it did not simulate any attack. The study did not involve human participants, developer surveys, or measures of developer expertise, and it did not compare autonomous or agentic workflows or evaluate mitigation techniques. These boundaries follow from the research questions set out in Chapter 1 and from the security considerations discussed in Section 3.15.

### 3.3.3 Study variables

The design contained three structural factors. The first, *model condition*, had four levels (M1 to M4). Each model condition was defined as a frozen combination of an exact model identifier, an API provider, an underlying-provider routing constraint where applicable, and a model-specific output-token ceiling, applied under shared generation settings. Model conditions were compared as experimental conditions. Because differences in training data, architecture, alignment, and serving infrastructure were neither controlled nor observable, the design did not permit differences in outcomes to be attributed to specific internal model characteristics. The second factor, *functional task category*, had six levels, each containing five tasks (Section 3.4). Task category was a design factor used for grouping; it was not a manipulated treatment, and the design did not presuppose that any category would produce a particular outcome. The third factor, *repetition*, had three levels (R01 to R03). Repetitions were not intended as a substantive comparison; they provided separate fresh requests under otherwise identical frozen inputs and permitted the stability of outcomes to be examined. They did not establish statistical independence.

Several factors were held constant across all observations. These included the task wording, the outer prompt template, and the resulting rendered prompt text, which was byte-identical across model conditions for a given task. Every request consisted of a single user message with no previous conversational context. No tools, browsing, retrieval, code execution, or function calling were made available. The sampling temperature was fixed at 0.6 and nucleus sampling (top-p) at 0.95 for all conditions. Other factors were recorded rather than controlled. The generation seed was not controlled, and provider-side model versions and serving behaviour were outside the researcher's control. The output-token ceiling differed between model conditions and is therefore part of the definition of each condition rather than a shared setting.

The outcome variables were defined at two levels. At the package level, each unique normalised package reference in a response was associated with registry evidence and a research classification, and from these with an indicator of whether it was a confirmed package-name hallucination and whether it constituted an exact-name dependency-resolution failure. At the response level, each observation had a collection status (completed, truncated, or failed), which determined its analytical eligibility, and each eligible completed response had an indicator of whether it contained at least one confirmed hallucination. Eligible confirmed findings additionally received a practical-risk score and band. The precise definitions of these outcomes are given in Sections 3.6 to 3.13. Table 3-3 summarises the study variables.

**Table 3-3. Study variables in the frozen v2.6 design**

| Role                     | Variable                                                           | Levels or values                                                                                     |
| ------------------------ | ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------- |
| Structural factor        | Model condition                                                    | M1, M2, M3, M4                                                                                       |
| Structural factor        | Functional task category                                           | `AUTH-FED`, `PKI-CRYPTO`, `DOC-BINARY`, `ENT-INT`, `DATA-ADV`, `DIST-OBS`                            |
| Structural factor        | Repetition                                                         | R01, R02, R03                                                                                        |
| Held constant            | Task wording, template, rendered prompt text                       | Frozen, identified by SHA-256 digests                                                                |
| Held constant            | Interaction format                                                 | One user message; no previous context; no tools, browsing, retrieval, execution, or function calling |
| Held constant            | Sampling settings                                                  | Temperature 0.6; top-p 0.95                                                                          |
| Condition-specific       | Output-token ceiling                                               | Defined per model condition (Section 3.5)                                                            |
| Recorded, not controlled | Generation seed; provider-side model version and serving behaviour | `not_controlled` or as exposed in collection metadata                                                |
| Response-level outcome   | Collection status and analytical eligibility                       | Completed, truncated, failed (Section 3.6)                                                           |
| Response-level outcome   | Contains at least one confirmed hallucination                      | Yes or no, for eligible completed responses                                                          |
| Package-level outcome    | Research classification and confirmed-hallucination status         | Adjudication taxonomy (Section 3.9)                                                                  |
| Package-level outcome    | Exact-name dependency-resolution failure status                    | Failure, non-failure, excluded, or undetermined (Section 3.11)                                       |
| Finding-level outcome    | Practical-risk score and band                                      | `risk-model-1.0.0` (Section 3.13)                                                                    |

---

## 3.4 Task and Prompt Construction

### 3.4.1 Task set

The final study used the frozen task set `final-2.0.0`, comprising 30 Node.js coding tasks distributed evenly across six functional task categories. The categories represent specialised technical domains in which implementations typically rely on external packages to handle established standards, formats, or protocols. Table 3-4 shows the category distribution.

**Table 3-4. Functional task categories in task set `final-2.0.0`**

| Code         | Functional task category                | Tasks  | Planned observations (5 × 4 × 3) |
| ------------ | --------------------------------------- | -----: | -------------------------------: |
| `AUTH-FED`   | Identity, Authentication & Federation   | 5      | 60                               |
| `PKI-CRYPTO` | PKI, Cryptography & Trust Services      | 5      | 60                               |
| `DOC-BINARY` | Complex Documents & Binary Formats      | 5      | 60                               |
| `ENT-INT`    | Enterprise Messaging & Interoperability | 5      | 60                               |
| `DATA-ADV`   | Specialized Data & Storage Integration  | 5      | 60                               |
| `DIST-OBS`   | Distributed Systems & Observability     | 5      | 60                               |
| **Total**    |                                         | **30** | **360**                          |

*Note.* Category names are reproduced as recorded in the frozen task set. Planned observations are design totals, not achieved counts.

The tasks were designed to be dependency-intensive. Each combined specialised standards, formats, or protocols whose implementation in Node.js would ordinarily involve selecting and integrating external npm packages. Examples include passkey registration and authentication using WebAuthn, the verification of detached cryptographic signatures with certificate chains and revocation data, the construction and validation of EPUB 3 documents, the parsing of electronic data interchange messages, streaming conversion between columnar data formats, and distributed coordination using leases and fencing tokens. The complete task list is reproduced in Appendix `[APPENDIX REFERENCE PENDING]`. This design choice was intended to elicit a substantial number of explicit package references, since a study of package-reference reliability requires responses in which packages are named. It also means that the task set is not a representative sample of Node.js programming work in general, and outcomes observed under these tasks may differ from those under more routine tasks.

Each task was written as a self-contained plain-text specification in TypeScript for Node.js. Each task requested a complete but bounded implementation rather than a full application, together with a complete `package.json` file with exact dependency versions and scripts, an identification or explanation of the package APIs used, and reproducible installation or execution commands. Where fixtures were required, the task asked for them to be included in the response or generated by steps given in the response, so that no external files were needed.

Two features of the task wording were designed to avoid biasing package selection. First, package choice was left neutral. All tasks included the instruction to use suitable npm packages where appropriate, although the instruction was not uniformly the final sentence and `AUTH-FED-02` used a semicolon before an additional constraint. No task named a specific package, asked the model to prefer obscure or unusual packages, or asked it to seek packages that might not exist. Second, no task mentioned hallucination or instructed the model to verify that its packages existed. A warning of this kind could have altered the behaviour being measured, and validation of the named packages was instead performed entirely downstream of generation (Sections 3.7 to 3.9).

### 3.4.2 Task difficulty designation

Tasks were designated medium difficulty during pre-freeze design using a qualitative study rubric. Under this rubric, a task was expected to represent a realistic Node.js backend requirement, to require multiple meaningful implementation steps beyond a trivial single-function solution, to remain implementable within one self-contained response, and to be understandable without follow-up clarification. The rubric explicitly did not require equal code length, dependency count, or implementation complexity across tasks.

The designation was not externally calibrated, was not assigned through a numerical difficulty model, and was not used as an analytical variable. The study therefore makes no claim that the 30 tasks are of equal or independently verified difficulty. Some tasks inherently involve more packages or more complex integrations than others, and this variation is acknowledged as a limitation in Section 3.15.

### 3.4.3 Pre-freeze task review

Before any official generation took place, the task set was reviewed for content and category balance without reference to any model output. A review of response size found that some tasks combined genuine dependency and protocol requirements with implementation volume that could lead to excessively long responses. Sixteen tasks were minimally narrowed to request core modules, small representative fixtures, essential error handling, and focused tests rather than complete platforms, while retaining their specialised standards and their package, version, API, and interoperability requirements. One further task was reviewed but not edited, because its remaining complexity reflected the genuine difficulty of its ecosystem rather than unnecessary scope. The researcher approved the revised task set, including documented residual review warnings, before it was frozen. Because these revisions preceded all official generation, no observed model output or package outcome influenced the final task wording.

### 3.4.4 Prompt template and rendering

The prompt submitted for each observation was produced by inserting a task specification into a common outer template. The v2.6 template contained a single `[TASK_DESCRIPTION]` placeholder followed by fixed instructions that applied to all tasks and model conditions. These instructions asked the model to return the complete requested solution directly in a single response. They stated that no existing repository, project scaffold, filesystem, terminal, browser, tools, external execution environment, or prior files were available. They also asked the model not to request, invoke, or simulate tool calls, and to include all requested code, `package.json` content, configuration, examples, explanations, and commands in the response itself. These instructions were intended to ensure that each response was a complete, self-contained text artefact from which package references could be extracted, and that no model condition was implicitly invited to rely on capabilities that were not available to the others.

Rendering was deterministic. A rendering script verified the SHA-256 digest of the frozen task file before use, checked that the file contained exactly 30 tasks with unique identifiers and five tasks in each category, and substituted each task specification into the template. It then compared each rendered prompt with the frozen prompt file for that task. The resulting 30 rendered prompts were each identified by their own SHA-256 digest in the freeze record. Because the rendered text depended only on the task and not on the model condition, all four model conditions received byte-identical prompts for a given task. The v2.6 rendered prompts were also byte-identical to those of the preceding protocol version, so the change to v2.6 did not alter the prompt input. The digests of the task file, template, rendered prompts, and manifest are listed in Appendix `[APPENDIX REFERENCE PENDING]`.

### 3.4.5 Experimental manifest and observation structure

The 360 planned observations were enumerated in advance in a frozen experimental manifest. Each manifest row recorded a unique run identifier, the task and its category, the task-set and model-set versions, the model condition, the exact model identifier, the API provider and any underlying-provider pin, the repetition, the path of the rendered prompt, and the expected SHA-256 digest of that prompt. At the time of freezing, every row had a pending status, and no observation had been collected.

The manifest also fixed the collection order. Observations were ordered by repetition, so that all 120 observations of the first repetition preceded those of the second, and within each repetition by task. Within each task, the order of the four model conditions was rotated cyclically from one task to the next, and the starting position was also shifted between repetitions. As a result, no single model condition was always collected first within a task. Recording the expected prompt digest in each row allowed the collection process to confirm that the exact frozen prompt was submitted for every observation. Figure 3-1 illustrates the frozen task-condition-repetition structure.

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

The task and prompt construction described in this section fixed the inputs of the experiment. Section 3.5 describes the model conditions to which these inputs were submitted and the procedure through which the responses were collected.

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

A completed response with no extractable external npm reference remained eligible. It contributed nothing to the package-level denominator but remained in the denominator of the Session Hallucination Rate (SHR) as a response without a confirmed hallucination. Excluding such responses would have limited the denominator to responses that happened to name packages and overstated the proportion containing a confirmed hallucination. The metrics are defined in Sections 3.10 and 3.11. Table 3-6 summarises the rules.

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

An npm 404 response or `not_found` state was treated as registry evidence only and was not, by itself, a confirmed hallucination. A name can be absent because the model invented it, but also because the package was removed or renamed, placed under the wrong scope, confused with a module inside another package, taken from another ecosystem, or used as the name of the project the response was itself generating. The procedure in Section 3.9 distinguishes these explanations.

---

## 3.9 Classification and Adjudication

### 3.9.1 Classification structure

Counting every `not_found` result as a hallucination would have merged the explanations listed in Section 3.8.4 and overstated the construct under study. The classification procedure therefore separated three questions for each package reference: whether it denoted an external npm dependency at all, whether the dependency as named would fail to resolve from the registry, and whether the name was a confirmed package-name hallucination. These were answered by a deterministic classification stage (PIPE-05) and a separate, evidence-based adjudication stage for cases the first could not decide (PIPE-05B). The analysis-dataset builder (PIPE-07) then combined their outputs under a single controlled rule. Figure 3-3 shows the sequence.

[FIGURE 3-3 TO BE DRAWN]

Title:
Figure 3-3. Direct npm extraction, registry evidence, and conservative adjudication pipeline.

Purpose:
Show the evidence-based route from a preserved eligible response to analysis fields without treating registry absence as a final classification.

Required content:
- Preserved eligible response → PIPE-03 explicit package-reference extraction and normalisation → unique `(run_id, normalized_package)`.
- PIPE-04 official npm registry evidence with three branches: `exists`, `not_found`, and `unresolved`.
- PIPE-05 classification, with `not_found` routed to `AMBIGUOUS` and `REVIEW_REQUIRED`, never directly to `CONFIRMED_HALLUCINATION`.
- PIPE-05B adjudication where required → PIPE-07 controlled confirmation resolution → final analysis fields.
- No installation, execution, package claiming, attack execution, or exploit testing.

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

The framework was an ordinal prioritisation aid, not a probability model. It did not estimate exploitation probability, installation probability, malicious-registration probability, financial loss, or real-world incident probability. It likewise did not use the superseded four-factor, 0 to 12 scoring approach. The assessment was confined to the practical consequence supported by the preserved response and evidence available under the study's non-execution boundary.

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
