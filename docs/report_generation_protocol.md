# Final Dissertation Report-Generation Protocol

## 1. Purpose

This protocol governs production of the final University of Kelaniya dissertation for the study actually performed. Repository evidence overrides outdated proposal and draft content. The dissertation must describe the implemented study, not planned-but-unperformed work.

## 2. Source-of-Truth Order

Resolve conflicts in this order:

1. Actual frozen experiment inputs, outputs, manifests, code, configuration, and verified results.
2. `docs/current_research_status.md`.
3. `docs/research_progress_log.md`.
4. `docs/final_paper_notes.md`.
5. Verified implementation/results produced in the current workflow.
6. `IM2021101.pdf` and earlier dissertation drafts.
7. Older plans, proposals, or chat discussions.

## 3. University Writing and Format Requirements

Apply the University of Kelaniya study-guide requirements: A4 pages; 38 mm left margin; 25 mm top, right, and bottom margins; Times New Roman or Times Roman; 12 pt body text; 1.5 line spacing; fully justified body text; 24 pt bold chapter headings; and approximately 18/16/14 pt bold headings at levels 1/2/3. Use Roman page numbers in preliminary pages, begin Arabic numbering at Chapter 1 page 1, and begin every chapter on a new page. Every main chapter must include an introduction and end with a summary.

Use completed methodology in past tense and formal scientific/academic prose. The narrative should be approximately 60–80 pages and normally no more than 120 pages, excluding front matter, references, and appendices. The University study guide remains authoritative if any formatting detail conflicts with this protocol.

## 4. Baseline Dissertation Policy

`IM2021101.pdf` is a useful baseline for topic and motivation, terminology, background, literature-review structure, theoretical context, research-problem framing, references, existing academic prose, and methodology text that still matches the implemented study. It is not authoritative where it conflicts with actual implementation.

Do not automatically retain outdated planned elements, including Spring Boot/Maven as a final ecosystem; unperformed multiple ecosystems, human surveys, developer-expertise variables, workflow-autonomy experiments, verification mediators, Java/Maven AST extraction, model/tool sets, 200–300 prompt assumptions, 500–1000 dependency assumptions, risk models, train/test predictive modelling, Cohen's Kappa, expert review, temporal holdouts, or mitigation experiments.

## 5. Draft Reconciliation Workflow

Before rewriting an existing dissertation section, prepare a reconciliation matrix:

| Old draft claim | Actual implementation | Evidence | Action: KEEP / REVISE / REMOVE / FUTURE WORK |
|---|---|---|---|

Do not directly rewrite outdated methodology before identifying each mismatch.

When present, review `recomendations.txt` as advisory research recommendations during planning, reporting, and reconciliation. It does not override frozen experiment evidence, verified implementation, current research status, decisions, or verified results. Do not describe unimplemented recommendations as performed methodology; they may inform interpretation, reporting emphasis, limitations, or future-work planning only where consistent with verified evidence.

## 6. Reference Control

Once it exists, use only `docs/references/approved_references.md` for academic citations. That file must be derived from the reference list in `IM2021101.pdf` and must not silently expand the bibliography. If another academic source seems necessary, record:

```text
NEW SOURCE PROPOSED:
<reason>
```

Do not cite it unless the researcher explicitly approves it. Repository files may support methodology or results claims, but are not academic literature citations. Do not invent bibliographic metadata.

For every literature claim, confirm that its citation supports the claim, verify exact numerical claims, and flag unsupported claims for removal or verification rather than fabricating a replacement citation. Use the University of Kelaniya author-year citation style.

## 7. Chapter 1 Workflow

Do not begin with final prose. First conduct a repository-grounded evidence audit to resolve the final research title, problem, gap, aim, objectives, questions, scope and delimitations, and contributions/significance. Check every item against the implemented study. Assemble Chapter 1 prose only after researcher review.

## 8. Chapter 2 Workflow

Use the existing dissertation literature review and approved references as the baseline. Do not use repository experiment results as literature evidence. Synthesize rather than list papers; compare agreements, disagreements, methodological differences, and gaps; retain only gaps relevant to the implemented study; and distinguish prior literature from this study's findings. Do not add web citations without explicit approval. Flag unsupported claims for removal or verification.

## 9. Chapter 3 Workflow

Reconstruct Chapter 3 from repository evidence. Before drafting, inspect the current research status, latest progress log, final paper notes, recommendations, decision log, frozen task files, prompt/template files, rendered prompts, manifests, model configuration, generation settings, collection scripts, raw-response storage design, response inventories, dependency extraction, normalization logic, registry validation, adjudication/classification, analysis scripts, risk analysis, schemas, tests, and verified outputs. Use the reconciliation matrix before drafting, describe only methodology actually performed, and write completed methodology in past tense.

## 10. Package Classification and Adjudication

Preserve the distinction between registry evidence and final research classification: an npm `404` or `not_found` alone is not a confirmed hallucination. Follow the exact implemented PIPE-05 / PIPE-05B semantics and controlling decisions. Do not invent or collapse classifications, including where implemented: `VALID`, `AUTO_VALID`, `REVIEW_REQUIRED`, `AMBIGUOUS`, `VALIDATION_UNRESOLVED`, `CONFIRMED_HALLUCINATION`, `LEGACY_OR_REMOVED`, `NAMESPACE_CONFUSION`, `PACKAGE_NAME_CONFUSION`, `INVALID_OR_REDUNDANT_TYPES_PACKAGE`, `ECOSYSTEM_CONFUSION`, `OTHER_DEPENDENCY_ERROR`, `SELF_REFERENCE_OR_LOCAL_PACKAGE`, `BUILTIN_OR_LOCAL` where historically applicable, and `UNRESOLVED`.

## 11. Primary Metrics Control

Follow D033 for primary PHR/SHR units and denominators, D034 for the primary/secondary external-dependency boundary, D035 for abnormal provider termination handling, and D037 for confirmed-hallucination routing. Do not redefine primary denominators after observing outcomes.

## 12. Secondary Metrics Control

Follow D036 for DFR/RDFR. Label DFR/RDFR as **secondary/exploratory**, never as a hallucination rate, and preserve uncertainty and incompleteness handling.

## 13. Chapter 4 Results Rule

Chapter 4 may contain only verified experimental results. Never convert an interim snapshot into a final finding. When collection or analysis is incomplete, use `[FINAL RESULT PENDING]`, replacing it only when final verified v2.6 analysis exists. Map every important result claim to exact evidence such as a result or analysis file, table or figure, manifest/version, run ID, and relevant script/version. Do not infer missing percentages or sample counts.

## 14. Chapter 5 Discussion

Interpret verified results primarily through the final research questions. Separate this study's empirical findings, comparison with approved literature, practical implications, security implications, and limitations. Do not introduce new empirical results.

## 15. Chapter 6 Conclusion

Answer research objectives and research questions only with verified final evidence. Treat planned-but-unperformed work only as an appropriate limitation, future work item, or removed outdated scope. Do not introduce new findings.

## 16. Claims-Evidence Control

Use `docs/final_report_support/claims_evidence_matrix.md`. For each important claim, record its claim ID, dissertation section, proposed claim, repository evidence, result file, literature citation where applicable, status, and notes. Permitted statuses are `VERIFIED`, `PENDING`, and `REJECTED`. Do not admit strong empirical or methodology claims into final text without exact evidence.

## 17. Front Matter

The Title Page, Declaration, Acknowledgements, Table of Contents structure, List of Figures, List of Tables, and Acronym List can be prepared early. Do not finalize the Abstract until Results, Discussion, and Conclusion are stable.

## 18. Final Dissertation Structure

The planned structure is as follows. Exact chapter and section titles may be adjusted where the University guide requires a different structure.

### Preliminary Pages

Title Page; Declaration; Abstract; Acknowledgements; Table of Contents; List of Figures; List of Tables; List of Acronyms.

### Chapter 1 — Introduction (approximately 6–9 pages)

1.1 Chapter Introduction; 1.2 Background of the Study; 1.3 Research Problem; 1.4 Research Gap; 1.5 Research Aim; 1.6 Research Objectives; 1.7 Research Questions; 1.8 Scope and Delimitations; 1.9 Research Contributions; 1.10 Dissertation Structure; 1.11 Chapter Summary.

### Chapter 2 — Literature Review (approximately 22–30 pages)

2.1 Chapter Introduction / Review Approach; 2.2 AI-Assisted Software Development; 2.3 Code Hallucination; 2.4 Package Hallucination; 2.5 Software Supply-Chain Security; 2.5.1 Typosquatting; 2.5.2 Dependency Confusion; 2.5.3 Slopsquatting; 2.6 Package Registry Architecture; 2.7 Empirical Package-Hallucination Research; 2.8 Detection and Validation Approaches; 2.9 Mitigation Strategies; 2.10 Research Gaps; 2.11 Chapter Summary.

### Chapter 3 — Research Methodology (approximately 18–25 pages)

The exact structure follows repository evidence, but may include: 3.1 Chapter Introduction; 3.2 Research Design and Approach; 3.3 Study Scope and Experimental Environment; 3.4 Experimental Task Dataset; 3.5 Prompt Design and Experimental Controls; 3.6 Evaluated Model Configurations; 3.7 Experimental Manifest and Run Design; 3.8 Response Collection Protocol; 3.9 Dependency Extraction; 3.10 Package Normalization; 3.11 Registry Evidence Collection; 3.12 Classification / Adjudication Framework; 3.13 Manual Review where actually performed; 3.14 Data Transformation and Analysis; 3.15 Statistical Analysis Method; 3.16 Risk Assessment Method; 3.17 Reproducibility and Integrity Controls; 3.18 Ethical Considerations; 3.19 Threats to Validity / Methodological Limitations; 3.20 Chapter Summary.

### Chapter 4 — Results and Analysis (approximately 14–20 pages)

Possible sections: 4.1 Chapter Introduction; 4.2 Experimental Dataset / Collection Completion; 4.3 Response Inventory; 4.4 Dependency Extraction Results; 4.5 Registry Evidence Results; 4.6 Package Classification Results; 4.7 Hallucination Prevalence; 4.8 Model / Configuration Comparisons; 4.9 Functional Category Comparisons; 4.10 Recurrence / Repeated Hallucinations; 4.11 Cross-Model Overlap where supported; 4.12 Risk Assessment Results; 4.13 Statistical Results; 4.14 Chapter Summary.

### Chapter 5 — Discussion (approximately 10–15 pages)

Organize primarily around final research questions.

### Chapter 6 — Conclusions and Future Work (approximately 5–8 pages)

Possible sections: 6.1 Chapter Introduction; 6.2 Research Summary; 6.3 Achievement of Objectives; 6.4 Answers to Research Questions; 6.5 Research Contributions; 6.6 Practical Recommendations; 6.7 Limitations; 6.8 Future Work; 6.9 Final Conclusion.

### References and Appendices

Use only cited, approved references. Possible appendices include the final task set, prompt template, experimental configuration, manifest description, classification/adjudication schema, additional result tables, and reproducibility material.

## 19. Writing Quality

Use formal academic English with cohesive paragraphs, precise terminology, cautious evidence-based language, clear transitions, and appropriate tables and figures. Avoid conversational writing, AI-style filler, excessive headings, repetitive summaries, exaggerated cybersecurity language, unsupported claims, and absolute wording such as “proves”, “completely”, or “guarantees” unless literally justified. Prefer wording such as “the findings indicate…”, “the analysis identified…”, “within the evaluated experimental conditions…”, “at the time of registry validation…”, and “the results suggest…”.

## 20. AI Responsibility Split

Use Codex CLI primarily for repository-wide inspection, methodology reconciliation, exact experiment descriptions, extraction of configurations and versions, results and analysis, tables, claims/evidence verification, and reproducibility material. Use Claude primarily for academic prose refinement, chapter coherence and restructuring, repetition detection, argument-strength critique, checking whether interpretations exceed evidence, and final language refinement. For repository-sensitive work, use Codex first and Claude review second. Neither may invent results or citations.

## 21. Standard Chapter Workflow

For every chapter, follow:

`repository audit → evidence summary → old-draft reconciliation → approved outline → subsection drafting → factual verification → academic-language review → chapter assembly → final consistency check`

Do not jump directly to writing a whole chapter.

## 22. Final Results Safety and End-of-Task Reporting

Final v2.6 collection is still ongoing. Do not infer final counts or rates, or present interim PHR, SHR, DFR, RDFR, risk distributions, or statistical comparisons as final dissertation findings.

For every significant task, determine and report:

- Progress-log update needed: YES/NO
- Final-paper note needed: YES/NO
- Draft reconciliation needed: YES/NO

If an update is needed, provide exact appendable Markdown or update it only when explicitly instructed. Never rewrite historical progress-log entries unless correcting an explicitly documented mistake.
