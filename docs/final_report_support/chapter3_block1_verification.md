# Chapter 3 Block 1 Verification

## 1. Verification scope

This verification reviewed Sections 3.1--3.4 of `docs/report_drafts/chapter3_sections_3_1_to_3_4.md` against the frozen v2.6 task set, template, rendered-prompt checks, model configuration, manifest, freeze record, manifest and renderer code, the controlling methodology reconciliation, and the required status, decision, analysis, progress, notes, and Chapter 1--2 documents. It is a methodology verification only; it does not report collection outcomes or final analysis results.

## 2. Overall verdict

**PASS_WITH_CORRECTIONS.** The block now accurately describes the planned v2.6 design and preserves its methodological boundaries. Four block-local issues were corrected. A later, matching Chapter 1 terminology correction is required, and the figure plan in the controlling reconciliation requires a later administrative update to reflect the requested first-appearance sequence.

## 3. Claim-by-claim issues

| ID | Claim or area | Verification finding | Disposition |
| --- | --- | --- | --- |
| B1-01 | Design total and categories | Verified: 30 tasks × 4 conditions × 3 repetitions = 360 planned observations; the six frozen categories each contain five tasks. | Retained. |
| B1-02 | Repetition terminology | “Independent generations” could be read as statistical independence. The records establish separate fresh requests under frozen inputs, but do not establish statistical independence. | Corrected in the block; Chapter 1 follow-up required. |
| B1-03 | Table 3-1 achieved-count row | An achieved/eligible-observations row is a Chapter 4 result, not a methodology-table element. | Removed. |
| B1-04 | Neutral package-selection instruction | All 30 tasks contain the neutral instruction, but it was not universally the identical final sentence: `AUTH-FED-01` continued after it and `AUTH-FED-02` used a semicolon before an added constraint. | Corrected. |
| B1-05 | Figure order | The task-condition-repetition figure first appears in Section 3.4 and must be Figure 3-1. The later workflow figure therefore becomes Figure 3-2. | Corrected in the target block; later figure references require renumbering. |

The following claims were specifically verified and required no edit: the 180 API/180 Manual planned assignment; a unique run identifier and the listed manifest fields; R01--R03 ordering; cyclic M1--M4 ordering with a repetition offset; all manifest rows pending at freeze; one `[TASK_DESCRIPTION]` placeholder; deterministic rendering and hashes; single-message, no-context, no-tool conditions; byte-identical v2.5 and v2.6 rendered prompts; the fresh v2.6 experiment and exclusion of earlier-version observations; output-ceiling and M2 provider-route changes; and the absence of final findings.

## 4. Required corrections

The following corrections were required in the target draft:

1. Use “separate fresh requests” rather than “independent generations” where the wording could assert statistical independence.
2. Remove “Achieved and eligible observations | `[FINAL RESULT PENDING]`” from Table 3-1.
3. State the task-level package instruction accurately rather than claiming every task ended with the identical quoted sentence.
4. Apply the requested first-appearance figure numbering in Sections 3.2 and 3.4.

## 5. Chapter 1 consistency issue

**Chapter 1 reconciliation required: YES.** Lines 46 and 58 of `docs/report_drafts/chapter1_complete_draft.md` describe “repeated independent generations” or “independent repetitions.” The protocol supports separate fresh requests, not a claim of statistical independence. The later Chapter 1 correction should use the corresponding bounded wording, for example “repeated separate fresh requests under frozen model conditions.”

The Chapter 1 wording on medium difficulty is otherwise consistent: it identifies the designation as task-set metadata and does not claim external calibration. The frozen JSONL task records do not contain a difficulty field; the designation is documented in the pre-freeze task-design record and qualitative rubric, and is not an analytical variable.

## 6. Figure/table numbering assessment

The target block now uses the requested order of first appearance:

1. Figure 3-1: Frozen task-condition-repetition design (Section 3.4).
2. Figure 3-2: Final v2.6 experimental workflow and preservation boundary (Section 3.5).
3. Figure 3-3: Direct npm extraction, registry evidence, and conservative adjudication pipeline (Sections 3.7--3.9).
4. Figure 3-4: Derivation of primary and secondary metrics (Sections 3.10--3.11).
5. Figure 3-5: `risk-model-1.0.0` Impact × Detectability framework (Section 3.13).

Only Sections 3.1--3.4 exist in the target draft. When later Chapter 3 sections are assembled, their workflow, pipeline, metrics, and risk figures must use Figures 3-2 through 3-5 respectively. `chapter3_methodology_reconciliation.md` still contains the earlier optional-design Figure 3-5 plan; that planning document requires a later controlled update and was not altered in this block verification.

Table 3-1 no longer contains an achieved-count field. Tables 3-2 through 3-4 are structural/methodology tables and remain appropriately numbered.

## 7. Unsupported or overstated claims

No unsupported claim remains in the corrected block concerning task count, category names, task distribution, prompt rendering, manifest construction, route assignment, or v2.6 succession. The following boundaries were verified as retained: no randomisation claim, no causal attribution to internal model properties, no representativeness claim, no statistical-independence claim, and no final-result values.

The task construction text is supported as qualified: all 30 tasks specify Node.js TypeScript, a complete `package.json`, exact dependency versions and scripts, package/API explanation, and reproducible commands; fixture requirements occur only where the task calls for fixtures. The neutral package instruction is now described without claiming a universal identical ending.

## 8. Corrections applied

Applied only to `docs/report_drafts/chapter3_sections_3_1_to_3_4.md`:

- revised the research-design and repetition wording;
- removed the results-oriented Table 3-1 row;
- corrected the neutral package-instruction statement; and
- changed the block-local figure references and placeholder to Figures 3-1 and 3-2 in requested first-appearance order.

No frozen artifact, manifest, raw response, collection state, configuration, or analysis output was modified.

## 9. Remaining restrictions

- Final v2.6 collection and provenance-consistent final analysis remain pending; Chapter 4 must supply achieved counts and final results only after verification.
- Manual-collection operational detail must not exceed the authoritative 180/180 assignment evidence.
- Appendix references remain `[APPENDIX REFERENCE PENDING]`.
- Later Chapter 3 figures and Chapter 1 repetition terminology require the follow-up stated above.
- Progress-log update needed: **NO**. Final-paper note needed: **NO**. Draft reconciliation needed: **YES**; this verification record provides it.

## 10. Evidence index

| Evidence | Verified use |
| --- | --- |
| `prompts/tasks/final_2.0.0.jsonl` | 30 records; six exact category names; five records per category; task wording and the placement of the neutral instruction. |
| `docs/task_set_v2_design.md` | Dependency-intensive rationale; pre-freeze scope review; 16 narrowed tasks and one reviewed unchanged task; fixture/output requirements. |
| `prompts/prompt_template_v2.6.0.md` | One placeholder; single-response and no-environment instructions. |
| `scripts/render_api_prompts.py` and `scripts/create_experiment_freeze_v2_6.py` | Hash validation, category checks, deterministic rendering, and byte identity with v2.5. |
| `manifests/api_final_v2.6.0_manifest.csv` and `scripts/create_api_manifest.py` | Fields, identifiers, all-pending freeze state, repetition order, and cyclic/repetition-shifted model order. |
| `config/experiment_freeze_v2.6.0.json` and `docs/experiment_freeze_v2.6.0.md` | Frozen 360-row design, model conditions, prompt hashes, unchanged prompt inputs, and v2.6 amendments. |
| `docs/current_research_status.md`, `docs/research_progress_log.md`, and `docs/final_paper_notes.md` | Fresh v2.6 separation, v2.5 ceiling history, exclusion of earlier observations, 180/180 assignment, and final-results-pending status. |
| `docs/decision_log.md`, `docs/analysis_specification_v1.0.md`, and `docs/final_report_support/chapter3_methodology_reconciliation.md` | Measurement boundaries, terminology constraints, and no-obsolete-methodology controls. |
| `docs/report_drafts/chapter1_complete_draft.md` and `docs/report_drafts/chapter2_complete_draft.md` | Chapter 1 terminology consistency review and Chapter 2 methodological-context check. |
