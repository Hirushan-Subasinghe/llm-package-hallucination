# Chapter 3 Methodology Reconciliation

## 1. Reconciliation Basis

This is an evidence-grounded reconciliation plan, not final Chapter 3 prose or a result report. Authority: frozen v2.6 artifacts, then `docs/current_research_status.md`, progress log, notes, decisions, implementation, and finally baseline `docs/source_documents/IM2021101.pdf` (Chapter 3, printed pp. 48--88). No `recomendations.txt` was present. Milestone updates: progress log **NO**; final-paper note **NO**; draft reconciliation **YES, this file**.

## 2. Source-of-Truth Review

Reviewed: `AGENTS.md`; report protocol; status/progress/notes; D001--D038; analysis specification; taxonomy; risk protocol; claims matrix; Chapters 1--2; approved references; frozen tasks/template/prompts/model config/manifest/freeze; PIPE-03--10 scripts, schemas and tests; baseline PDF. Frozen v2.6 is controlling; final results are pending.

## 3. Baseline Chapter 3 Reconciliation Matrix

36 items reviewed: **KEEP 1; KEEP_WITH_REVISION 8; REWRITE 4; REMOVE 17; MOVE_TO_LIMITATIONS 3; MOVE_TO_FUTURE_WORK 3.**

| Baseline Method / Claim | Implemented Study | Status | Evidence | Required Action |
|---|---|---|---|---|
| Quantitative reproducible experiment | Controlled repeated generation and deterministic derived analysis | KEEP | D002--D004; PIPE-03--10 | Retain neutral wording only. |
| Positivist/deductive hypotheses | No frozen hypothesis-testing framework | REWRITE | baseline pp.48--57; PIPE-09 | Describe bounded empirical comparative design. |
| Four-phase design | Collection → extraction → evidence → adjudication → analysis/risk | REWRITE | PIPE-03--10 | Replace. |
| Autonomy/workflow comparison | Four frozen model/API conditions, not autonomy | REMOVE | D003 | Remove. |
| Java/Maven, PyPI, multi-ecosystem | Node.js/npm only | REMOVE | D001 | Remove. |
| Survey, participants, expertise | Not performed | REMOVE | D008 | Remove. |
| Verification mediator/mitigation experiment | Not performed | REMOVE | D009 | Remove. |
| Slopsquatting registration/installation lifecycle | No claiming, installation, execution, or exploitation | MOVE_TO_FUTURE_WORK | taxonomy scope controls | Future work/literature only. |
| Six categories | Six frozen categories, five tasks each | KEEP_WITH_REVISION | task design | Use final IDs/names; no criticality manipulation. |
| Standard prompts | Frozen template and deterministic rendering | KEEP_WITH_REVISION | renderer; freeze | Use actual hashes/process. |
| GUI/IDE harnesses | Hybrid API/manual assignment | REWRITE | notes/progress hybrid entries | Do not claim Copilot IDE automation. |
| GPT/Copilot/Gemini/Claude; temp .7 | Exact M1--M4; temp .6/top_p .95/seed not controlled | REWRITE | model config | Use frozen IDs only. |
| 200--300 prompts/power/dependency estimates | 30×4×3 = 360 planned | REMOVE | D002,D004; manifest | Replace; no power claim. |
| Raw metadata/storage | Immutable raw and separate derived provenance | KEEP_WITH_REVISION | schemas; pipelines | Describe actual fields. |
| Node extraction | Explicit syntax extraction/normalisation | KEEP_WITH_REVISION | D029; PIPE-03 | No unimplemented AST claim. |
| Java/Maven extraction/lookup | Not implemented | REMOVE | D001 | Remove. |
| npm lookup | Read-only npm evidence | KEEP_WITH_REVISION | PIPE-04 | 404 is not classification. |
| 404 = hallucination/claimability | Conservative classification required | REWRITE | PIPE-04/05B; D037 | Replace. |
| Generic manual verification | Structured dated PIPE-05B evidence | KEEP_WITH_REVISION | PIPE-05B | Do not claim experts. |
| 0--12 four-factor risk | Superseded by Impact×Detectability | REMOVE | D032 | Remove. |
| Risk assessment | Rule-based post-classification scoring | KEEP_WITH_REVISION | risk protocol; PIPE-06 | Use 1--5×1--4. |
| ML/70:30/predictive validation | Not performed | REMOVE | risk protocol | Remove. |
| Cohen Kappa/expert review | Not performed | REMOVE | baseline pp.79--82 | Remove. |
| Temporal holdout | Not performed | MOVE_TO_FUTURE_WORK | status | Future replication only. |
| Alternative-tool validation | Not performed | REMOVE | D003 | Remove. |
| Transitive dependency exclusion | Direct references only | MOVE_TO_LIMITATIONS | taxonomy; PIPE-03 | State limitation. |
| Temporal snapshot | Registry evidence time-bounded | MOVE_TO_LIMITATIONS | PIPE-04 timestamps | State limitation. |
| Sample-generalisation claim | Bounded task/model design | MOVE_TO_LIMITATIONS | D002,D004 | State limitation. |

Remaining baseline subclaims (registry architecture moderator, exploitability scoring, static/dynamic validation, mitigation/cost-benefit, data privacy, Maven coordinates, sensitivity weights) are **REMOVE**; mitigation proposals are **MOVE_TO_FUTURE_WORK**. This accounts for the 36-item totals.

## 4. Verified Final Research Design

Frozen v2.6.0 is a Node.js/npm direct-package-reference study: 30 `final-2.0.0` tasks × 4 frozen model/API conditions × 3 planned independent repetitions = **360 planned observations**, never the interim completed count. Freeze commit `5247c2bccb58ecd6c86b9b7e92d800ade0378282`, tag `v2.6.0-freeze`. It compares conditions, not foundation architectures, autonomy, people, or exploitation.

## 5. Experimental Scope

Six five-task categories: `AUTH-FED`, `PKI-CRYPTO`, `DOC-BINARY`, `ENT-INT`, `DATA-ADV`, `DIST-OBS`. Tasks are Node.js/npm and marked `medium`; this is study metadata, not externally calibrated difficulty. Direct explicit dependencies only; no transitive analysis, human study, execution, installation, functional testing, or other ecosystem.

## 6. Task and Prompt Construction

`prompts/tasks/final_2.0.0.jsonl`: SHA-256 `ef0aff59f8a3934f65379d34036848652b7b5593f595ffa4b449a15af021546b`. Template `prompts/prompt_template_v2.6.0.md`: SHA-256 `8d3971d6f9f86dfd98a4b5c49c0c13d734b7f650744da682225195f2ea49b528`; one `[TASK_DESCRIPTION]`. Renderer validates task hash, uniqueness/distribution and frozen prompt bytes. Manifest rotates M1--M4 by task/repetition and records prompt hash/path; its hash is `b2b2750b3ae4ce96a867df14117b05c12f214760ef7036d6bbf2f78e44939b7f`.

## 7. Model Conditions

| ID | Model ID | Provider / pin | Ceiling |
|---|---|---|---:|
| M1 | `cohere/north-mini-code:free` | OpenRouter / `cohere` | 64000 |
| M2 | `qwen/qwen3.8-27b` | OpenRouter / Darkbloom-only, no fallback | 32768 |
| M3 | `openai/gpt-oss-120b` | Groq / `not_applicable` | 65536 |
| M4 | `nvidia/nemotron-3-ultra-550b-a55b:free` | OpenRouter / `nvidia` | 65536 |

Source: `config/api_model_set_1.4.0.json`. Shared settings: temperature .6, top_p .95, seed `not_controlled`; fresh one-user-message, no previous context/tools/browsing/retrieval/execution. Do not rename frozen conditions from current branding.

## 8. Data Collection

Sequential manifest order; retries only for infrastructure (2/5/10 seconds, maximum three), zero artificial pacing, no content retry/substitution/fallback. Planned hybrid assignment is 180 API and 180 Manual rows; **assignment is not eligibility** and a failed API row remains API. Raw response/metadata/provenance are preserved. `length` is preserved truncation; failures are preserved once, not regenerated. D035: non-`stop`/`length` finish reasons, including `error`, are derived `FAILED` without raw editing. D038 preserved an interrupted sent request as failure without replacement.

## 9. Response Status and Eligibility

| Status | Extraction | PHR/SHR and DFR/RDFR | Grouping |
|---|---|---|---|
| COMPLETED (`stop`) | Yes | Eligible | Eligible |
| TRUNCATED (`length`) | Yes, marked | Excluded | Ineligible/status retained |
| FAILED (including D035 abnormal finish) | No | Excluded | Ineligible/status retained |

PIPE-07 defines eligibility as inventory `collection_status == completed`; zero-package completed responses remain in SHR denominator. Stale failed package rows fail provenance checks. Earlier truncated-in-primary wording in the analysis specification is superseded.

## 10. Package Extraction and Normalisation

PIPE-03 (`pipe-03-package-reference-extractor-1.0.2`) supports literal ESM import, `require`, literal dynamic import, `npm install`/`npm i`, and package.json dependencies/devDependencies/peerDependencies/optionalDependencies. It roots scoped/unscoped subpaths, retains version specifiers, and excludes built-ins, `node:`, relative/local/absolute, `file:`, HTTP(S), and unsupported aliases. Unit: unique `(run_id, normalized_package)`; occurrence provenance (source text/offset/type/version/count/first index) is retained separately. No prose inference or transitive traversal.

## 11. npm Registry Validation

PIPE-04 read-only GETs the official npm registry and records `exists`, `not_found`, or `unresolved`, URL/status/time/version/retry/source hashes/history. Only structurally expected 404 payload is `not_found`; operational/malformed states are unresolved. Cache/resume preserves evidence. **404 is not confirmed hallucination.** No installation, execution, claim, registration, reservation, publication, or exploitation occurs.

## 12. Classification and Adjudication

PIPE-05/05B/07 distinguish `CONFIRMED_HALLUCINATION`, `LEGACY_OR_REMOVED`, `NAMESPACE_CONFUSION`, `PACKAGE_NAME_CONFUSION`, `INVALID_OR_REDUNDANT_TYPES_PACKAGE`, `ECOSYSTEM_CONFUSION`, `OTHER_DEPENDENCY_ERROR`, `UNRESOLVED`, and `SELF_REFERENCE_OR_LOCAL_PACKAGE`. Fields include independent `confirmed_package_hallucination`, `dependency_failure`, and `external_dependency_eligible` (true/false/null). Self/local requires response-internal evidence, has false dependency failure, and a 404 is not evidence.

D037 lets PIPE-07 count a row only once via PIPE-05 `REVIEWED` confirmation or a guarded PIPE-05B confirmation from PIPE-05 `REVIEW_REQUIRED`/`AMBIGUOUS`; duplicate/mismatched/weak provenance fails closed. Other outcomes never enter PHR/SHR numerators; PIPE-05 is never rewritten.

## 13. Primary Metrics

PHR = confirmed metric-eligible unique `(run_id, normalized_package)` rows / all metric-eligible unique package rows. SHR = eligible completed responses with ≥1 confirmed hallucination / all eligible completed responses. D033/D037 control. Completed zero-package responses remain SHR-denominator members; truncated/failed excluded; unresolved/non-hallucination outcomes do not enter numerators.

## 14. Secondary Metrics

D036/PIPE-10: DFR and RDFR are secondary/exploratory exact-name npm dependency-resolution measures, **not hallucination rates**. `DFR=F/(F+N)` for external failure/non-failure rows; undetermined U rows are excluded from point estimate and bounded. Responses are POSITIVE with a failure, otherwise INDETERMINATE if undetermined, otherwise NEGATIVE; zero-package/self-local-only responses are NEGATIVE and `RDFR=P/(eligible-I)`. Wilson intervals/bounds and completeness gate are reported. Quote controlling scope: DFR does not capture wrong-but-existing packages, version/API/capability or functional-unsuitability errors.

## 15. Grouped and Statistical Analysis

PIPE-09 groups by model condition, category, repetition, and model×category. Two groups use Fisher exact with odds ratio/risk difference and 95% CIs. Multi-group uses assumption-gated chi-square or deterministic 2×C Monte Carlo (20,000, seed 1234567891); pairwise p-values use Holm. Sparse/zero/insufficient cases are `not_testable`; no ranking/best model output.

## 16. Practical-Risk Framework

`risk-model-1.0.0`/PIPE-06 is rule-based post-classification scoring of eligible resolved findings: Impact 1--5 × Detectability 1--4; LOW 1--4, MODERATE 5--8, HIGH 9--14, CRITICAL 15--20. `security_sensitive_context` is non-scored. It preserves source, consequence, rationales, assessor/time and provenance; unscored is null, never zero. It is not predictive ML, probability, installation likelihood, financial loss, or old 0--12 model (superseded D032).

## 17. Pipeline Stage Mapping

| Stage | Purpose | Input → Output | Dissertation role |
|---|---|---|---|
| PIPE-03 | Extract/normalise | inventory/raw → occurrence/unique | Construct/unit |
| PIPE-04 | Registry evidence | unique → evidence/joined | Evidence, not classification |
| PIPE-05 | Classification routing | PIPE-03/04 → classifications | Review boundary |
| PIPE-05B | Conservative adjudication | review-required + dated evidence → separate records | Taxonomy |
| PIPE-06 | Risk scoring | confirmed findings → scores | Practical risk |
| PIPE-07 | Join/eligibility/D037 | derived inputs → package/response data | Metric gate |
| PIPE-08 | Primary metrics | PIPE-07 → PHR/SHR | Primary definitions |
| PIPE-09 | Grouping/comparisons | PIPE-07 → summaries/tests | Analysis method |
| PIPE-10 | Reliability metrics | PIPE-07/05B → DFR/RDFR | Secondary definitions |

## 18. Validation and Quality Assurance

`FINAL-ANALYSIS-VALIDATION-01` used synthetic-only fixtures: 126 focused tests passed; 44 PIPE-07/10 subset passed; full suite 327 passed with two known historical freeze-fixture failures (missing four v2.1 and eight v2.3 gitignored raw directories). Verdict: **PASS WITH DOCUMENTED LIMITATIONS**. This is infrastructure validation, not expert/Cohen-Kappa, temporal, predictive, or final-result validation.

## 19. Research Integrity and Safety

Frozen hashes, immutable raw evidence, derived-only transformations, pre-specified denominators, preserved failed/truncated records, read-only registry validation, and no outcome-dependent changes are controlling safeguards. Untrusted dependencies were not installed/executed because that was unnecessary for the package-reference validation construct, would add security risk, and would create a different experiment. Interim outputs are not final findings.

## 20. Methodological Limitations

One ecosystem; bounded 30-task/four-condition/three-repetition design; uncalibrated difficulty; direct explicit extraction only; no transitive/narrative-only/`export ... from`/yarn-pnpm/`require.resolve` coverage; no execution/function correctness/version analysis; time-bounded registry/provider evidence; hybrid assignment considerations; unresolved researcher adjudication; rule-based study-specific risk rubric.

## 21. Proposed Final Chapter 3 Structure

3.1 Introduction; 3.2 Research Design; 3.3 Experimental Scope and Study Variables; 3.4 Task and Prompt Construction; 3.5 Model Conditions and Data Collection; 3.6 Response Preservation, Status, and Analytical Eligibility; 3.7 Package Reference Extraction and Normalisation; 3.8 npm Registry Validation; 3.9 Classification and Adjudication; 3.10 Primary Metrics; 3.11 Secondary Metrics; 3.12 Grouped and Statistical Analysis; 3.13 Practical-Risk Assessment; 3.14 Validation and QA; 3.15 Integrity, Safety and Limitations; 3.16 Summary.

## 22. Figure Plan

| Caption | Placement | Nodes/arrows | Must not imply | Now? |
|---|---|---|---|---|
| Figure 3-1. Final v2.6 experimental workflow and preservation boundary | 3.5 | frozen inputs→prompts→manifest→API/manual→raw→derived | completion, execution, results | Yes |
| Figure 3-2. Direct npm extraction, registry evidence, and conservative adjudication pipeline | 3.7--3.9 | response→03→04→05/05B→07 | 404=hallu | Yes |
| Figure 3-3. Derivation of primary and secondary metrics | 3.10--3.11 | eligibility→PHR/SHR; failure states→DFR/RDFR | DFR=hallu | Yes |
| Figure 3-4. `risk-model-1.0.0` Impact × Detectability framework | 3.13 | eligible finding→components→band; separate flag | probability | Yes |
| Figure 3-5. Frozen task-condition-repetition design (optional) | 3.4 | 6×5×4×3=360 | achieved sample | Yes |

## 23. Table Plan

Study design (3.2); category distribution (3.4); model-condition summary (3.5); status/eligibility (3.6); extraction/exclusions (3.7); taxonomy (3.9); metrics (3.10--11); statistical selection (3.12); risk matrix (3.13). All can be filled now; none should contain interim/final results.

## 24. Claims-Evidence Candidates

| ID | Claim | Status | Evidence |
|---|---|---|---|
| CH3-001 | Node.js/npm direct scope | VERIFIED | D001; task JSONL; taxonomy |
| CH3-002 | 30×4×3 planned v2.6 design | VERIFIED | freeze; manifest; task design |
| CH3-003 | Frozen hash-controlled rendering | VERIFIED | freeze; renderer; manifest creator |
| CH3-004 | Exact M1--M4 conditions | VERIFIED | model config; freeze doc |
| CH3-005 | Status/D035 eligibility | VERIFIED | D021,D033,D035; inventory/PIPE-07 |
| CH3-006 | PIPE-03 unique unit/provenance | VERIFIED | D029,D033; extractor |
| CH3-007 | 404 not automatically hallucination | VERIFIED | PIPE-04; taxonomy; D037 |
| CH3-008 | D037 single confirmation routing | VERIFIED | D037; PIPE-07 |
| CH3-009 | PHR/SHR definitions | VERIFIED | D033; PIPE-08 |
| CH3-010 | DFR/RDFR secondary | VERIFIED | D036; PIPE-10 |
| CH3-011 | Rule-based risk | VERIFIED | D032; protocol; PIPE-06 |
| CH3-012 | Final v2.6 results pending | PENDING | status; progress log |

## 25. Prohibited/Outdated Methodology Statements

Do not write that the study tested Java/Maven/PyPI/multiple ecosystems; participants/surveys/expertise; autonomy/agents/filesystem/package execution; mitigations/static-dynamic/RAG/sandboxing; 404 equals hallucination/exploit; installation/execution/claiming/publication; 200--300 prompts/power/GPT-Copilot-Gemini-Claude/temp .7; Maven/Java extraction; 0--12/predictive/70:30 risk model; Kappa/experts/temporal/alternative-tool validation; occurrence/404-only PHR; truncated/failed primary eligibility; DFR/RDFR as hallucination rates; or interim results as final.

## 26. Open Issues

Collection and final provenance-consistent v2.6 analysis remain pending. Manual-interface operational details need an authoritative collection record before detailed prose beyond confirmed 180/180 assignment. Any review description must identify actual records and never claim experts/inter-rater agreement. Chapter drafting is ready only with these restrictions.

## 27. Evidence Index

`AGENTS.md`; report protocol; status/progress/notes; decisions D001--D038; analysis spec/taxonomy/risk protocol; frozen v2.6 config, freeze, task/template/rendered prompt/manifest; PIPE-03--10 scripts/schemas/tests; claims matrix; Chapters 1--2; approved references; baseline PDF.
