# Chapter 3 v2.7 Reconciliation Verification

## 1. Scope

Task: `CHAPTER-3-V2.7-RECONCILIATION-01` (2026-09-25).

Edited file: `docs/report_drafts/chapter3_complete_draft.md` (authoritative compact Chapter 3).

Purpose: reconcile Chapter 3 from the superseded v2.6.0 four-condition design to the frozen v2.7.0 three-condition final study. No frozen experiment input, raw response, manifest, collection state, analysis output, or figure asset was modified. No commit was made.

## 2. Evidence Inspected

Authoritative experiment repository `~/Dev/ai-hallucination-study` at tag `v2.7.0-freeze` (commit `bba890d9aa5838f06bee4b1bd0e85d9e61b444f8`), read via `git show` only:

- `config/experiment_freeze_v2.7.0.json`
- `config/api_model_set_1.5.0.json`
- `manifests/api_final_v2.7.0_manifest.csv`
- `docs/experiment_freeze_v2.7.0.md`

Integration worktree: `docs/current_research_status.md`, `docs/decision_log.md` (D039 to D042), `docs/final_paper_notes.md`, `docs/research_progress_log.md`, and prior Chapter 3 verification records.

Manifest counts were recomputed directly from `manifests/api_final_v2.7.0_manifest.csv` at the tag:

| Check | Recomputed value | Freeze record |
| --- | --- | --- |
| Rows | 270 | 270 |
| Rows per model | M1 90, M3 90, M4 90 | same |
| M2 rows | 0 | 0 |
| Rows per category | 45 each (6 categories) | same |
| API / manual | 140 / 130 | same |
| M1 API / manual | 40 / 50 | same |
| M3 API / manual | 41 / 49 | same |
| M4 API / manual | 59 / 31 | same |

Model identifiers, providers, pins, and output ceilings in Table 3-3 match `api-model-set-1.5.0`: M1 `cohere/north-mini-code:free`, OpenRouter, pinned `cohere`, 64,000; M3 `openai/gpt-oss-120b`, Groq, not applicable, 65,536; M4 `nvidia/nemotron-3-ultra-550b-a55b:free`, OpenRouter, pinned `nvidia`, 65,536.

## 3. Sections Changed

| Section | Change |
| --- | --- |
| 3.1 | Active methodology relabelled v2.6 to v2.7.0 final study (two sentences). |
| 3.2 | Design total changed to 30 tasks, three retained conditions, three repetitions, 270 planned observations; derivation from superseded v2.6.0 stated; pooling sentence clarified to earlier stopped versions; prospective-design statement now discloses the post-partial-collection condition removal as the one exception. |
| 3.2, Table 3-1 | Caption, conditions row, planned-observations row updated; collection-assignment row added (140 / 130, deterministic, not randomised). |
| 3.4.1, Table 3-2 | Planned observations per category 60 to 45; total 360 to 270. |
| 3.4.2 | Freezing sentence notes v2.7.0 configuration and manifest derived from frozen v2.6.0 counterparts without altering retained definitions or rows; manifest paragraph updated to 270 rows, retained run identifiers, and inherited v2.6.0 collection order. |
| 3.4.2, Figure 3-1 placeholder | Factorial sequence and planned total updated; instruction added not to depict M2 and that the existing asset must be regenerated. |
| 3.5.1 | Heading changed to "Final model conditions and exclusion of M2"; opening paragraph changed to three retained conditions frozen in `api-model-set-1.5.0`, no renumbering; M2-specific failure clause removed; M2 disclosure paragraph added. |
| 3.5.1, Table 3-3 | Caption updated; M2 row removed; M1, M3, M4 rows unchanged. |
| 3.5.2 | Hybrid split 180 / 180 changed to 140 / 130, stated as deterministic, non-randomised, inherited without reassignment or rebalancing, with per-model split and uneven association with condition; evidence-reuse paragraph added; interface-effect sentence extended to note route/condition confounding. |
| 3.5.2, Figure 3-2 placeholder | Title v2.6 to v2.7; 140 / 130 unbalanced route shown; reuse note; M2 placement instruction; regeneration note. |
| 3.15 | Integrity sentence refers to earlier stopped protocol versions; limitations updated to three retained conditions, post-partial-collection removal, and uneven route/condition association. |
| 3.16 | Summary updated to v2.7.0, three retained conditions, 270 planned observations, M2 exclusion, deterministic hybrid assignment, and evidence reuse. |

Sections 3.3, 3.6 to 3.14 were not changed.

## 4. Exact Design Changes Reflected

| Element | Superseded v2.6.0 | Current v2.7.0 in Chapter 3 |
| --- | --- | --- |
| Model conditions | 4 (M1, M2, M3, M4) | 3 (M1, M3, M4), not renumbered |
| Planned observations | 360 | 270 |
| Per category | 60 | 45 |
| API / manual | 180 / 180 | 140 / 130 (M1 40/50, M3 41/49, M4 59/31) |
| M2 manifest rows | 90 | 0 |
| Model set | `api-model-set-1.4.0` | `api-model-set-1.5.0` (retained definitions identical) |

## 5. M2 Disclosure

Location: Section 3.5.1, paragraph following Table 3-3; cross-referenced from Section 3.2 and summarised in Sections 3.15 and 3.16.

Wording summary: the superseded v2.6.0 design froze M2 (`qwen/qwen3.8-27b`, OpenRouter, Darkbloom only) and 360 planned observations; partial M2 collection occurred; M2 was removed as a whole condition before final analysis because its intended automated API route could not complete the required collection protocol consistently; the rationale was operational and used collection outcomes only; no extraction, registry, classification, metric, or risk output existed for any condition at the decision point, so the exclusion could not have been based on observed hallucination performance; all 90 planned M2 rows, including completed M2 responses, were excluded; M2 contributes zero rows to the v2.7.0 manifest and all final metrics and denominators; all M2 evidence remains preserved as historical v2.6.0 evidence; the design is disclosed as not wholly prospective in this respect.

The disclosure does not claim M2 was never planned, does not claim the removal was prospective before any collection, and does not imply a result-driven exclusion. M2 per-status collection counts (2 completed, 9 failed) were deliberately not reproduced in Chapter 3 to keep collection-state detail out of the methodology chapter; they remain in the freeze record.

Controlling decision: integrated D039 (originally data-collection D036). Decision IDs are not cited in Chapter 3 prose, consistent with the existing chapter style.

## 6. Evidence-Reuse Statement

Section 3.5.2 states that retained M1, M3, and M4 observations already collected under the compatible frozen v2.6.0 protocol were reused without regeneration where provenance matched, mapped in place by run identifier and SHA-256 digest after verification of design identity, prompt digest, collection assignment, and response digest, and that reused responses retain their original generation provenance (`api-model-set-1.4.0`) and are not represented as new v2.7.0 generations. Source: `evidence_reuse` block of `config/experiment_freeze_v2.7.0.json`. No count of reused rows or collection status is stated in Chapter 3.

## 7. Table Changes

| Table | Change |
| --- | --- |
| 3-1 | Updated: v2.7.0 caption; three retained conditions (M1, M3, M4); 30 × 3 × 3 = 270; added collection-assignment row 140 / 130. |
| 3-2 | Updated: 5 tasks and 45 planned observations per category; total 30 / 270. |
| 3-3 | Updated: caption v2.7.0; M2 row removed; M1, M3, M4 rows unchanged and match `api-model-set-1.5.0`. |
| 3-4 to 3-9 | Unchanged (model-count independent; no v2.6 wording). |

## 8. Figure Impacts

Assets were not modified in this task. Existing SVG assets in `docs/report_assets/figures/chapter3/` were inspected read-only.

| Figure | Asset content found | Placeholder text updated | Regeneration required |
| --- | --- | --- | --- |
| 3-1 | "four frozen model conditions", M1 to M4 including M2, 360 planned observations | YES | YES |
| 3-2 | "v2.6 experimental workflow", "Four model ... M1 to M4", "180 planned manifest rows" per route | YES | YES |
| 3-3 | No model-count, version, or split text (numeric "180" hits are SVG coordinates) | NO | NO |
| 3-4 | No model-count, version, or split text | NO | NO |
| 3-5 | No asset yet; placeholder is model-count independent | NO | NO (draw from unchanged placeholder) |

Note: `figure3_4_metric_derivation.drawio` and `.svg` were untracked at task start and were left untouched.

## 9. Unchanged Methodology

Preserved without substantive change: Node.js/npm-only scope; direct explicit package-reference boundary; COMPLETED / TRUNCATED / FAILED eligibility (D035 abnormal finish reason as FAILED); extraction and normalisation rules; read-only official npm registry evidence; `exists` / `not_found` / `unresolved` evidence states; conservative adjudication taxonomy; `not_found` alone does not confirm hallucination; unique `(run_id, normalized_package)` unit and PHR / SHR (D033); primary/secondary external-dependency treatment (D034); DFR / RDFR as secondary, non-hallucination measures (D036); controlled confirmation routing (D037); grouped statistical procedure; `risk-model-1.0.0`; validation and safety boundaries.

## 10. Word Count

| | Words (`wc -w`) |
| --- | ---: |
| Before | 7,501 |
| After | 8,055 |
| Change | +554 (+7.4%) |

The increase is attributable to the M2 disclosure paragraph (about 180 words), the evidence-reuse paragraph (about 75), the uneven hybrid-split disclosure (about 70), updated figure instructions (about 90), and limitation and prospective-design caveats. No unrelated text was added.

## 11. Stale-Term Search

Terms searched: `v2.6`, `four model`, `four models`, `four-model`, `4 model`, `M1–M4`, `M1 to M4`, `M2`, `360`, `180 API`, `180 manual`, `180/180`, `60 planned`, `60 observations`, table cells `| 60 |`, `four`, `50/50`.

| Line(s) | Hit | Classification |
| --- | --- | --- |
| 5 | "four questions" | Unrelated (research questions); allowed |
| 17 | "superseded four-condition v2.6.0 design" | Historical derivation; allowed |
| 77, 79 | v2.6.0 counterparts / v2.6.0 manifest order | Provenance of derived v2.7.0 inputs; allowed |
| 98 | M2, "superseded four-condition design" in Figure 3-1 instruction | Exclusion / regeneration instruction; allowed |
| 102 | Section heading "exclusion of M2" | M2 disclosure; allowed |
| 116 | v2.6.0, M2, 360 | M2 disclosure; allowed |
| 120 | v2.6.0, M2 | Inherited allocation provenance; allowed |
| 122 | v2.6.0 | Evidence-reuse provenance; allowed |
| 140 | 50/50 | Instruction not to depict a 50/50 split; allowed |
| 143, 144 | v2.6.0, v2.6, M2, 180/180 in Figure 3-2 instructions | Reuse note, M2 placement, regeneration instruction; allowed |
| 380 | M2 in summary | M2 exclusion disclosure; allowed |

| Stale current-study category | Remaining |
| --- | ---: |
| Four-model current wording | 0 |
| 360 as current total | 0 |
| 180 / 180 as current split | 0 |
| M2 as a current condition | 0 |
| 60 per category | 0 |

## 12. Verification Checklist

| Check | Result |
| --- | --- |
| Active version v2.7.0 | PASS |
| Current retained models M1, M3, M4 | PASS |
| 270 planned observations | PASS |
| 45 planned observations per category | PASS |
| API / manual 140 / 130, deterministic, not balanced | PASS |
| M2 final rows = 0 documented | PASS |
| M2 exclusion transparent (planned, partially collected, operational, pre-analysis, not result-driven, preserved) | PASS |
| Retained evidence reuse described accurately, not presented as new generation | PASS |
| Em dashes | 0 |
| En dashes | 0 |
| Prose double hyphens | 0 |
| `git diff --check` | clean |

## 13. Decision IDs Used (support material only)

- D033: primary PHR/SHR unit and eligibility (unchanged, not affected).
- D034: primary/secondary external-dependency treatment (unchanged).
- D035: abnormal finish reason as FAILED (unchanged).
- D036: DFR/RDFR secondary dependency reliability (unchanged).
- D039: M2 removal from final v2.7 study (originally data-collection D036). Supports Section 3.5.1 disclosure.
- D040: HYBRID deterministic API/manual allocation (originally data-collection D033). Supports Section 3.5.2 split.
- D041: API collection only for eligible never-attempted API-assigned rows (originally data-collection D034). Consistent with the unchanged no-reassignment statement in Section 3.5.2.
- D042: offline manual observation capture and preservation workflow (originally data-collection D035). Covered by the unchanged manual-route appendix reference.

No bare data-collection D033 to D036 identifier is used. Chapter 3 prose cites no decision ID.

## 14. Empirical-Result Leakage Check

PASS. No PHR, SHR, DFR, RDFR, grouped comparison, statistical test outcome, or risk distribution appears. No achieved, eligible, completed, truncated, or failed count for any retained condition is stated. The only M2 figures used are design quantities (90 planned rows, 360 superseded planned total) and the qualitative fact that some M2 responses had completed. Percentages found are method definitions (Wilson 95% intervals, 95% confidence intervals).

## 15. Obsolete-Methodology Leakage Check

PASS. Search for Maven, Spring, Java, survey, expertise, autonomy, mediator, exploitability, CVSS, and likelihood returned only pre-existing exclusion statements (Sections 3.1, 3.3) and the risk framework's statement that neither dimension represents likelihood. No obsolete risk model, ecosystem, survey, or execution methodology was introduced.

## 16. Recommendation

**READY_FOR_V2.7** for Chapter 3 text. Outstanding before Word transfer: regenerate Figures 3-1 and 3-2 from the updated placeholders.

## 17. Documentation Follow-Up

- Progress-log update needed: YES
- Final-paper note needed: YES (the 2026-09-24 note at `docs/final_paper_notes.md` stating four conditions, 360 observations, and 180 / 180 is superseded for Chapter 3)
- Draft reconciliation needed: YES (Figures 3-1 and 3-2 regeneration; any other chapter still using v2.6 design figures)

Proposed appendable progress-log entry:

```markdown
### 2026-09-25 — Chapter 3 reconciled to v2.7.0 three-condition final study

- Reconciled `docs/report_drafts/chapter3_complete_draft.md` from the superseded v2.6.0 design to frozen v2.7.0 (tag `v2.7.0-freeze`, commit `bba890d9aa5838f06bee4b1bd0e85d9e61b444f8`): M1, M3, M4; 270 planned observations; 45 per category; 140 API / 130 manual (deterministic, not balanced).
- Added M2 exclusion disclosure (Section 3.5.1; integrated D039) and retained-evidence reuse statement (Section 3.5.2).
- Tables 3-1, 3-2, 3-3 updated; Tables 3-4 to 3-9 unchanged. Word count 7,501 to 8,055.
- Figures 3-1 and 3-2 require regeneration; Figures 3-3 to 3-5 unaffected.
- Verification: `docs/final_report_support/chapter3_v2.7_reconciliation_verification.md`. No empirical results added.
```

Proposed appendable final-paper note:

```markdown
### 2026-09-25 — Chapter 3 v2.7 reconciliation

Chapter 3 now describes the frozen v2.7.0 final study: three retained conditions (M1, M3, M4; not renumbered), 30 tasks, 3 repetitions, 270 planned observations, 45 per category, and a deterministic, unbalanced 140 API / 130 manual assignment (M1 40/50, M3 41/49, M4 59/31). The earlier 2026-09-24 Chapter 3 note specifying four conditions, 360 observations, and 180 / 180 is superseded. Section 3.5.1 discloses that M2 was removed after partial collection and before final analysis for operational reasons, with no result outputs in existence (integrated D039). Retained M1/M3/M4 evidence is reused without regeneration where provenance matched. Figures 3-1 and 3-2 must be regenerated before Word transfer.
```
