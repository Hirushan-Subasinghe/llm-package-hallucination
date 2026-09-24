# Chapter 3 Visual, Table, and Style Review

## Scope and evidence basis

This review completed `CHAPTER-3-VISUAL-TABLE-AND-STYLE-PASS-01` against the authoritative Chapter 3 draft, its final and block verification records, the methodology reconciliation, the current research status, final-paper notes, and the report-generation protocol. The baseline dissertation was inspected visually for its Chapter 3 presentation devices only. It was not used as methodology authority.

The revised chapter retains five detailed, draw.io-ready figure placeholders. No publication-quality figures were created in Markdown. The placeholders specify the content, boundaries, and prohibited implications needed for final figure production.

## Baseline dissertation visual reconciliation

| Baseline item | Old purpose | Current relevance | Action | Reason |
| --- | --- | --- | --- | --- |
| Figure 3-0-1, Conceptual Framework Diagram | Map LLM architecture, workflow type, programming environment, functional category, and prompt characteristics to hallucination frequency, exploitability, and severity. | The box-and-arrow hierarchy is a useful presentation convention only. | REPLACE | The constructs include workflow autonomy, multiple environments, architectural causal implications, exploitability, and the old severity model. Figure 3-1 now presents the frozen task-condition-repetition design without those constructs. |
| Table 3-1, Operationalization of Research Variables | Define independent, moderating, and dependent variables, including workflow type, developer expertise, surveys, and exploitability. | No substantive reuse. | REMOVE | Its variables and survey content are superseded. Current Tables 3-1 and 3-3 instead define the frozen design and implemented study factors and outcomes. |
| Figure 3-2, Dependency Classification Workflow Pipeline | Illustrate extraction, registry lookup, classification, and a final hallucination count. | The staged-flow layout is a useful visual-design inspiration. | ADAPT | Figure 3-3 replaces the substantive flow with the npm-only PIPE-03 to PIPE-07 process. `not_found` routes to review, not directly to confirmation, and the final figure excludes installation and execution. |
| Classification outcome boxes and linear registry decision path | Categorise dependencies as valid, hallucinated, or ambiguous from registry responses. | The need to distinguish evidence states from outcomes remains relevant. | REPLACE | The final taxonomy separates `exists`, `not_found`, and `unresolved` registry evidence from PIPE-05 classification, PIPE-05B adjudication, and PIPE-07 confirmation resolution. |
| Severity scoring and high/medium/low representations | Relate severity to namespace availability, workflow autonomy, and execution privileges. | No substantive reuse. | REPLACE | Figure 3-5 and Table 3-14 use the implemented `risk-model-1.0.0` Impact × Detectability framework, including its stated bands and separate `security_sensitive_context` attribute. |
| Exploitability assessment and proposed risk-model architecture figure | Represent attack feasibility, developer installation probability, and weighted risk output. | No reuse. | REMOVE | The final study did not assess exploit probability, installation probability, attack probability, financial loss, registration, package claiming, execution, or the earlier four-factor 0 to 12 model. |

No baseline visual is reused unchanged. The old classification flow supplies only a general layout idea; it is not evidence of the implemented final pipeline.

## Final figure plan

| Figure | Placement | Status | Presentation decision |
| --- | --- | --- | --- |
| Figure 3-1. Frozen task-condition-repetition design. | Section 3.4 | Detailed placeholder | Show 30 frozen tasks across six categories, four conditions, three planned repetitions, and 360 planned observations; explicitly avoid an independence claim. |
| Figure 3-2. Final v2.6 experimental workflow and preservation boundary. | Section 3.5 | Detailed placeholder | Separate frozen inputs, assigned collection route, and preserved raw evidence from one-way derived analysis; state that later stages do not rewrite raw evidence. |
| Figure 3-3. Direct npm extraction, registry evidence, and conservative adjudication pipeline. | Section 3.9 | Detailed placeholder | Use a staged flowchart, but show `not_found` as review-required rather than a direct hallucination outcome. |
| Figure 3-4. Derivation of primary and secondary metrics. | Section 3.10 | Detailed placeholder | Use two branches to distinguish PHR/SHR from secondary DFR/RDFR dependency-reliability metrics. |
| Figure 3-5. `risk-model-1.0.0` Impact × Detectability framework. | Section 3.13 | Detailed placeholder | Show the multiplication, bands, and separate non-scored security-context field; do not depict probability. |

## Table audit

| Table | Decision | Review outcome |
| --- | --- | --- |
| Table 3-1. Summary of the frozen v2.6 study design. | REVISE | Retained as the concise design anchor. Corrected the expansion of SHR to Session Hallucination Rate for consistency with the chapter. |
| Table 3-2. Relationship between research questions and methodological components. | KEEP | Connects each question to the relevant implemented procedure without reporting results. |
| Table 3-3. Study variables in the frozen v2.6 design. | REVISE | Retained because it replaces the superseded operationalisation table with current factors, controls, and outcomes. Its three-column structure remains suitable for portrait presentation. |
| Table 3-4. Functional task categories in task set `final-2.0.0`. | KEEP | Compactly records the balanced frozen category structure and planned totals. |
| Table 3-5. Frozen model conditions in the v2.6 experiment. | KEEP | Required to record condition identity and condition-specific ceiling without speculation about internal architectures. |
| Table 3-6. Response states and analytical eligibility. | REVISE | Retained as the single eligibility reference; its matrix format prevents repeated prose explanations of state treatment. |
| Table 3-7. Package-reference extraction, normalisation, and exclusion rules. | REVISE | Retained because it fixes the direct npm boundary. The concise aspect-and-rule format is preferable to a procedural software listing. |
| Table 3-8. npm registry evidence states. | KEEP | Separates time-bounded evidence from research classification. |
| Table 3-9. Deterministic classification routes. | KEEP | Gives the essential PIPE-05 route logic, including the non-confirmatory treatment of `not_found`. |
| Table 3-10. PIPE-05B adjudication outcomes and derived fields. | REVISE | Retained because the outcome-to-field distinction is methodologically necessary; its evidentiary requirements are summary statements, with detail retained in surrounding prose. |
| Table 3-11. Definitions and eligibility rules for the primary metrics. | KEEP | Concisely fixes PHR and SHR units, numerators, denominators, and exclusions. |
| Table 3-12. Secondary dependency-reliability states and their metric treatment. | KEEP | Distinguishes DFR/RDFR states without calling them hallucination rates. |
| Table 3-13. PIPE-09 inferential selection rules. | KEEP | Avoids duplicating implementation code while making the prespecified selection path auditable. |
| Table 3-14. `risk-model-1.0.0` Impact × Detectability matrix. | KEEP | The compact matrix is the clearest representation of the score calculation. |

No table was merged or removed because each retained table records non-duplicative, verified methodology. Five tables were reviewed for concise portrait-oriented presentation and retained with their substantive boundaries intact.

## Style and caption pass

All figure captions were converted to short academic titles within the placeholders. Explanatory material now appears in the placeholder purpose and required-content fields, rather than as caption-length prose. The duplicate primary-metric introduction preceding Section 3.10 was removed. The remaining wording was preserved where it was already precise and natural.

The pass made limited edits: it removed one mechanical transition word, corrected the inconsistent SHR expansion, replaced narrative en-dash ranges with ordinary wording, and replaced all five abbreviated figure placeholders with reproducible specifications. No result statement, empirical count, rate, comparison, or outcome conclusion was added.

## Dash review

All narrative uses of en dashes were replaced with ordinary wording. No em dash occurs in the revised chapter. Remaining `--` matches in the requested grep check are Markdown table-divider or horizontal-rule syntax, not prose punctuation, command-line flags, identifiers, quoted material, or executable code. The chapter contains no legitimate technical double-hyphen token.

## Milestone assessment

- Progress-log update needed: NO.
- Final-paper note needed: NO.
- Draft reconciliation needed: NO. This review record provides the requested visual, table, and style reconciliation.
