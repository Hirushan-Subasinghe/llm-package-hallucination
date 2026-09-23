# Chapter 1 Literature Reconciliation - CHAPTER-1-LITERATURE-RECONCILIATION-01

**Audit date:** 2026-09-23  
**Purpose:** Determine which literature-context claims from the baseline dissertation can be retained in the final Chapter 1 without drafting Chapter 1 prose, adding references, calculating metrics, or changing frozen evidence.

## 1. Scope and source constraints

This reconciliation used only the 34 entries in `docs/references/approved_references.md`, which were extracted from the baseline dissertation's reference list. No web search, new reference, result calculation, or experimental-file modification was performed.

The baseline source inspected was `docs/source_documents/IM2021101.pdf`. Its Chapter 1 appears at printed pp. 1-3 (PDF pp. 10-12); relevant literature treatment appears principally in Chapter 2, especially printed pp. 12-15, 17-31, and 46-47. The baseline Chapter 1 itself contains an explicit "citation needed" adoption statement and otherwise presents many literature-facing assertions without an adjacent citation. A citation was treated as usable only where the baseline Chapter 2 directly links it to the claim, not merely because the reference appears in the bibliography or nearby discussion.

**Meaning of support status:** it records whether the baseline supplies a direct, approved-reference linkage adequate for cautious retention. It is not external full-text verification of the cited paper. Exact numerical claims are deliberately more restrictive: a number is `UNVERIFIED` unless the baseline identifies its source, population, and scope without an internal inconsistency. Repository material is used only for final-study design, scope, and delimitation claims; it is not academic literature evidence.

The final study remains a Node.js/npm-only empirical study. Package hallucination, typosquatting, dependency confusion, slopsquatting, and autonomous agents must not be conflated with one another or represented as experimental variables, attacks, or results where the frozen design did not assess them.

## 2. Chapter 1 literature-claim matrix

| Claim ID | Proposed Chapter 1 Claim | Baseline Wording/Location | Approved Citation(s) | Support Status | Action | Notes |
|---|---|---|---|---|---|---|
| L01 | LLM-generated code can contain code-specific hallucinations relevant to software reliability. | Ch. 2.3.2, printed p. 17: code hallucinations are described as affecting correctness, maintainability, and security. | Gao et al. (2025) | SUPPORTED | KEEP | Retain as concise background; do not state a prevalence or causal mechanism. |
| L02 | AI-assisted programming changes the context in which code is generated and reviewed. | Ch. 2.2.2, printed pp. 13-14: contrasts traditional verification with non-deterministic generated code. | Liu et al. (2026); Tian et al. (2025); Dubey and Madisetti (2026) | SUPPORTED | KEEP | Context only; final study did not compare human review or development productivity. |
| L03 | LLMs may recommend non-existent package names; this is a package-hallucination concern. | Ch. 2.3.3, printed p. 19: ties non-deterministic recommendations and public registries to package hallucination. | Spracklen et al. (2025); Al-Zofi (2025) | SUPPORTED | KEEP | Final operational definition must instead come from the study's conservative classification rules. |
| L04 | Public package ecosystems are relevant to dependency-related software supply-chain security. | Ch. 1.1, printed p. 1 names npm, PyPI, and Maven Central without citation; Ch. 2.4 supplies supply-chain context. | Ladisa et al. (2023); Wang et al. (2025); Williams et al. (2025) | PARTIALLY_SUPPORTED | KEEP_WITH_CAUTION | Use a general supply-chain context statement. Do not make unverified registry-architecture or ecosystem-comparison claims in Chapter 1. |
| L05 | Typosquatting is distinct from package hallucination. | Ch. 2.4.2, printed p. 22: baseline describes typosquatting as exploiting a misspelled package identifier. | Al-Zofi (2025); Ladisa et al. (2023); Duan et al. (2020) | SUPPORTED | KEEP | State the distinction, not that the final experiment tested typosquatting. |
| L06 | Dependency confusion is distinct from package hallucination. | Ch. 2.4.2, printed p. 22: baseline describes private/public namespace-resolution manipulation. | Al-Zofi (2025); Ladisa et al. (2023); Duan et al. (2020) | SUPPORTED | KEEP | Do not treat an npm absence, name resemblance, or hallucination as dependency confusion. |
| L07 | Slopsquatting is literature/security context concerning malicious registration of AI-hallucinated names. | Ch. 2.3.3, printed p. 19; Ch. 2.4.2, printed p. 22. | Al-Zofi (2025) | SUPPORTED | MOVE_TO_CHAPTER_2 | If retained briefly in Chapter 1, call it literature context only. The final study did not register names, install packages, execute code, or conduct an attack. |
| L08 | The final study's npm scope does not make PyPI or Maven Central experimental ecosystems. | Ch. 2.3.3, printed p. 19 contrasts Python, JavaScript, and Java ecosystems. | Al-Zofi (2025); Spracklen et al. (2025) | PARTIALLY_SUPPORTED | KEEP_WITH_CAUTION | Cross-ecosystem comparison is baseline context only; the final empirical scope is Node.js/npm only and requires repository evidence. |
| L09 | Autonomous coding systems can create broader security concerns in prior literature. | Ch. 2.2.3, printed pp. 14-15 discusses tool use, execution, and package registries. | Yadav et al. (2026); Qu et al. (2026); baseline also cites `Gandhi, 2025` | PARTIALLY_SUPPORTED | MOVE_TO_CHAPTER_2 | Use only a bounded literature-background statement. Final conditions are stateless and no-tools; autonomy is not a study variable. The Gandhi citation-year discrepancy prevents relying on it. |
| L10 | The baseline's exact adoption statement, "up to 97%" of developers and "approximately 30%" AI-generated code contributions, is suitable Chapter 1 evidence. | Ch. 2.2.1, printed p. 12. | Al-Zofi (2025) | UNVERIFIED | REMOVE | The baseline supplies the values but no inspectable primary evidence in this audit; Chapter 1 originally labels adoption as "citation needed." Do not use either number. |
| L11 | Package-hallucination prevalence is 15.8% for Python and 21.3% for JavaScript. | Ch. 2.3.3, printed p. 19. | Spracklen et al. (2025) | UNVERIFIED | REMOVE | Exact ecosystem-specific values must not migrate without source-level confirmation of denominator, model set, and task design. They are also outside the final study's Node.js-only scope. |
| L12 | Package-hallucination prevalence averages 19.7% across 576,000 samples. | Ch. 2.3.3, printed p. 20. | Spracklen et al. (2025) | UNVERIFIED | REMOVE | Do not use the number or its implied generality; it requires direct source verification and may describe a different population/estimand. |
| L13 | Commercial models have a 5.2% package-fabrication rate and open-source models a 21.7% rate. | Ch. 2.3.1, printed p. 16. | Al-Zofi (2025) | UNVERIFIED | REMOVE | Exact comparative rates, model grouping, task selection, and scope were not independently established; the final study does not compare commercial versus open-source categories as a variable. |
| L14 | High temperature or low-frequency APIs can yield package-fabrication rates up to 85%. | Ch. 2.2.3, printed p. 15 and Ch. 2.3.3, printed p. 20. | Twist et al. (2026); Jain et al. (2025) | UNVERIFIED | REMOVE | Keep no numerical rate. The frozen experiment sets one temperature and does not manipulate temporal prompts or API frequency. |
| L15 | Registry lookup and static dependency analysis are literature-described pre-installation validation approaches. | Ch. 2.5.1, printed p. 28. | Al-Zofi (2025); Duan et al. (2020); Ohm and Stuke (2023) | SUPPORTED | KEEP_WITH_CAUTION | Appropriate as literature context and to motivate read-only registry evidence. Do not describe the final study as a mitigation experiment or claim complete detection. |
| L16 | Static lookup filters flag up to 94.8% of package hallucinations. | Ch. 2.5.1, printed p. 28. | Al-Zofi (2025) | UNVERIFIED | REMOVE | Exact effectiveness must not be retained without direct source verification; no effectiveness was measured in the final study. |
| L17 | Documentation grounding and knowledge-graph approaches are literature-described mitigation directions for API/code hallucination. | Ch. 2.2.2, printed pp. 13-14; Ch. 2.6. | Jain et al. (2025); Li et al. (2026); Liu et al. (2025b) | SUPPORTED | MOVE_TO_CHAPTER_2 | Mention only in related-work/future-work context. No such intervention was evaluated. |
| L18 | Existing detection and mitigation approaches have implementation trade-offs or limits. | Ch. 2.5.1-2.5.3, printed pp. 28-31; Ch. 2.8, printed pp. 46-47. | Ohm and Stuke (2023); Tian et al. (2025); Yang et al. (2026); Tileria et al. (2026) | PARTIALLY_SUPPORTED | MOVE_TO_CHAPTER_2 | A narrow, attributed statement is possible; avoid universal claims such as "no approach provides complete protection." |
| L19 | Prior literature lacks standardized cross-ecosystem package-hallucination benchmarks. | Ch. 2.3.3, printed p. 20. | Yang et al. (2026) | PARTIALLY_SUPPORTED | REWRITE | Do not assert absence. Safer wording, if needed after source review: prior work reviewed in the baseline reports heterogeneous ecosystems and evaluation settings. |
| L20 | Prior literature lacks data on developers installing hallucinated dependencies or live slopsquatting campaigns. | Ch. 2.3.3, printed p. 20; Ch. 2.8, printed p. 46. | No direct approved source is linked to each absence assertion. | UNVERIFIED | REMOVE | These are broad literature-absence claims and cannot establish the final study's novelty. |
| L21 | The baseline's citation `Gandhi, 2025` supports its autonomous-agent statement. | Ch. 2.2.3, printed p. 14; Ch. 2.8, printed p. 46. | Approved list contains Gandhi (2026), not Gandhi (2025). | CONTRADICTED | REMOVE | Do not cite Gandhi for the baseline's 2025 claim until the citation identity/year is reconciled within the approved-reference process. |
| L22 | The final study fills a literature-wide gap by being the first, only, or absent-from-prior-work evaluation of its kind. | Baseline Ch. 2.8, printed pp. 46-47 presents broad gaps; neither Chapter 1 nor the approved list provides a direct exhaustive comparison to the final design. | Several potentially relevant sources, especially Spracklen et al. (2025), Wang et al. (2025), and Williams et al. (2025). | UNVERIFIED | REWRITE | Do not claim priority or exhaustive absence. Use a bounded implementation-facing rationale only. |

**Matrix totals (22 claims):** `SUPPORTED` 8; `PARTIALLY_SUPPORTED` 5; `UNVERIFIED` 8; `CONTRADICTED` 1.

## 3. Approved references most relevant to Chapter 1

This is a citation-selection guide, not a bibliography change. It identifies the smallest useful subset from the approved list.

| Group | Recommended approved references | Appropriate use |
|---|---|---|
| General code hallucination | Gao et al. (2025); Liu et al. (2026); Tian et al. (2025) | Brief reliability/hallucination context; distinguish code hallucination from the final package-name outcome. |
| Package hallucination | Spracklen et al. (2025); Al-Zofi (2025); Zhao et al. (2025) | Package-name context, empirical motivation, and package-hallucination testing. Do not import unverified numerical claims. |
| Software supply-chain security | Ladisa et al. (2023); Ohm and Stuke (2023); Wang et al. (2025); Williams et al. (2025); Duan et al. (2020) | Supply-chain context and distinction from established package-manager attacks. |
| Slopsquatting / package-hallucination risk | Al-Zofi (2025); Spracklen et al. (2025) | Literature-only security context. Never describe the final study as a slopsquatting attack, payload analysis, or registry-registration study. |
| Detection / validation | Al-Zofi (2025); Duan et al. (2020); Ohm and Stuke (2023); Jain et al. (2025); Li et al. (2026); Tian et al. (2025) | Related-work context for registry validation, documentation grounding, and execution-based approaches. The final study used downstream read-only npm validation only. |
| Broader reliability / agentic context | Woesle et al. (2025); Dubey and Madisetti (2026); Yadav et al. (2026); Qu et al. (2026) | Cautious background or Chapter 2 context. Do not cite Gandhi until the baseline's year discrepancy is resolved. |

## 4. Unsupported or risky claims

The following claims must not be retained as Chapter 1 literature claims without a separately approved source-verification step:

- Any adoption statistic, including the baseline's 97% developer-use and 30% code-composition assertions.
- Any package-hallucination prevalence percentage or sample-size claim: 15.8%, 21.3%, 19.7% across 576,000 samples, 5.2% versus 21.7%, or 85%.
- Any detection-performance percentage: 94.8%, 33.5%, or 2.5%.
- "No prior work," "complete lack," "undefined," "unmodeled," "first," or equivalent literature-wide absence/priority wording.
- Claims that package hallucination causes, demonstrates, or predicts installation, malicious registration, compromise, exploitability, or loss.
- Claims that npm, PyPI, or Maven architecture caused a particular prevalence difference, unless the exact cited study is directly verified.
- Claims that autonomous agents were evaluated, that their autonomy is an experimental variable, or that the final study tested confused-deputy execution.
- Claims that RAG, documentation grounding, knowledge graphs, static tooling, dynamic tooling, or hybrid defenses were evaluated by the final experiment.

## 5. Research-gap wording constraints

The research gap is **not ready for unqualified novelty drafting**. It is ready only for a bounded study-design rationale grounded in repository evidence.

Permitted direction for later drafting, subject to final researcher approval: describe the dissertation as providing a reproducible, bounded Node.js/npm evidence chain that preserves generated responses, extracts direct package references, obtains read-only registry evidence, applies conservative adjudication, and separates confirmed package-name hallucination from secondary exact-name dependency-resolution failures. This is a description of the implemented study, not a claim that no prior study has done so.

Do not state that the literature lacks this exact design, that the study is first, or that its results close a field-wide gap. A literature-comparison claim requires a source-by-source comparison against the approved references, including Spracklen et al. (2025), Zhao et al. (2025), and the supply-chain reviews, before it can be drafted.

## 6. Citation guidance by Chapter 1 subsection

| Subsection | Are academic citations needed? | Appropriate approved references | Use repository evidence for | Claims not to make |
|---|---|---|---|---|
| 1.1 Chapter Introduction | Yes, for the broad motivation only. | Gao et al. (2025); Woesle et al. (2025); Spracklen et al. (2025). | State that this dissertation is an empirical Node.js/npm study; no results. | Adoption statistics; forecast prevalence; agentic study framing. |
| 1.2 Background of the Study | Yes. | Spracklen et al. (2025); Al-Zofi (2025); Ladisa et al. (2023); Wang et al. (2025); Williams et al. (2025). | Node.js/npm scope and conservative outcome definitions. | Treating PyPI/Maven as evaluated ecosystems; saying this study performed a supply-chain attack. |
| 1.3 Research Problem | One or two contextual citations are appropriate. | Spracklen et al. (2025); Al-Zofi (2025), with cautious wording. | Exact distinction between confirmed package-name hallucination, 404 evidence, and secondary DFR/RDFR. | Observed exploitation, prevalence, maliciousness, or attacker behavior. |
| 1.4 Research Gap | Yes, but only after direct claim-to-source verification. | Potentially Spracklen et al. (2025); Zhao et al. (2025); Wang et al. (2025); Williams et al. (2025). | Bounded rationale and exact implemented evidence chain. | First/only/no-prior-work claims; broad absence claims. |
| 1.5 Research Aim | No, normally. | None required. | Final aim and its bounded empirical scope. | SLR aim, root-cause claims, or mitigation-evaluation aim. |
| 1.6 Research Objectives | No, normally. | None required. | Verified objectives and pending-status boundary. | Objectives concerning autonomous comparisons, developer surveys, package installation, or mitigation tests. |
| 1.7 Research Questions | No, normally. | None required. | Answerable Node.js/npm questions and outcome definitions. | Cross-ecosystem, agentic-autonomy, or mitigation-effectiveness questions. |
| 1.8 Scope and Delimitations | No, normally. | None required; citations may support brief background examples only. | Node.js/npm only; no human participants, execution, registration, transitive analysis, or mitigation intervention. | PyPI/Maven final scope; registry safety/exploitability claim; completed-result count. |
| 1.9 Research Contributions | Literature comparison needs citations; design description does not. | Use only after source-by-source comparison. | Implemented pipeline/design contributions and `[FINAL RESULT PENDING]` for empirical contributions. | Final rates, rankings, significance, risk distributions, or a delivered security control. |
| 1.10 Dissertation Structure | No. | None required. | Actual final report structure. | Baseline five-part SLR structure. |
| 1.11 Chapter Summary | No, unless restating a cited background claim. | Reuse only already-verified citations. | Summary of scope, aim, objectives, questions, and delimitations. | New literature claims or results. |

## 7. Claims safe to retain

The following are safe only as claims, not ready-made Chapter 1 prose:

- Code hallucination is a literature-recognized reliability concern in LLM-generated code (Gao et al., 2025).
- Package-hallucination research provides relevant context for studying LLM-generated dependency recommendations (Spracklen et al., 2025; Al-Zofi, 2025).
- Software supply-chain security literature provides relevant context for dependency-related risks (Ladisa et al., 2023; Wang et al., 2025; Williams et al., 2025).
- Typosquatting, dependency confusion, and slopsquatting are distinct concepts; none should be silently relabelled as package hallucination (Al-Zofi, 2025; Ladisa et al., 2023; Duan et al., 2020).
- Registry lookup and static dependency analysis are literature-described validation approaches (Al-Zofi, 2025; Duan et al., 2020; Ohm and Stuke, 2023).
- Documentation grounding and knowledge-oriented approaches are literature-described mitigation directions, not interventions performed in this dissertation (Jain et al., 2025; Li et al., 2026).
- The final dissertation's Node.js/npm scope, exact experimental conditions, conservative classification, and no-execution limitations are study-design facts supported by repository evidence, not by academic citations.

## 8. Claims requiring rewrite/removal

**Rewrite:**

- General registry background: keep npm as the experimental context; confine PyPI/Maven to attributed literature examples and state they are outside the final experiment.
- Autonomous-agent risk: if retained, move to Chapter 2 or make a short, cited background statement; expressly state it is not an empirical variable.
- Detection/mitigation limits: state only narrowly attributed trade-offs; do not claim universal failure or complete protection.
- Research gap: use the bounded implementation-facing rationale in Section 5 rather than a literature-wide absence claim.

**Remove:**

- The baseline Chapter 1's uncited adoption wording and any 97%/30% values.
- All unverified prevalence, detection, bypass, and model-comparison numbers listed in Section 4.
- The baseline `Gandhi, 2025` citation until its mismatch with the approved Gandhi (2026) entry is resolved.
- Any suggestion that this dissertation performed slopsquatting, name registration, malicious package analysis, package installation, code execution, autonomous-agent evaluation, or mitigation experimentation.
- Any claim that non-existence in npm alone establishes a confirmed package-name hallucination.

## 9. Open verification issues

1. The audit did not inspect the full text of the 34 cited works; approved-reference status permits their use but does not independently validate the baseline's paraphrases or numbers.
2. The approved entry is `Gandhi (2026)`, while relevant baseline passages cite `Gandhi, 2025`. Resolve this bibliographic mismatch before citation.
3. Spracklen et al. (2025) is central to baseline prevalence assertions, but all exact values and the claimed 576,000-sample population require source-level verification before use.
4. Al-Zofi (2025) is central to package-hallucination/slopsquatting context, but its baseline-reported adoption, ecosystem, model-rate, registry, and detection-performance numbers require source-level verification before use.
5. The gap wording needs a controlled source-by-source comparison to the small relevant approved subset before it is ready for final drafting. Until then, only the bounded implementation-facing rationale is permitted.
6. The final study has no final metrics or findings at this milestone; Chapter 1 must not convert literature context or repository implementation into results.

## Evidence index

- `AGENTS.md` and `docs/report_generation_protocol.md`: final-report integrity, source order, and Chapter 1 reconciliation rules.
- `docs/references/approved_references.md`: the exclusive 34-reference academic-citation boundary.
- `docs/source_documents/IM2021101.pdf`: baseline Chapter 1 and the directly inspected Chapter 2 passages identified above.
- `docs/final_report_support/chapter1_evidence_audit.md` and `docs/final_report_support/chapter1_draft_reconciliation.md`: final-study scope and prior reconciliation constraints; neither is academic literature evidence.
- `docs/current_research_status.md` and `docs/final_paper_notes.md`: current-study/reporting constraints; not academic literature evidence.
