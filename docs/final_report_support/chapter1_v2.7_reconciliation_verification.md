# Chapter 1 v2.7 Reconciliation Verification

**Task ID:** CHAPTER-1-V2.7-RECONCILIATION-01

**Date:** 2026-09-25

**Target file:** `docs/report_drafts/chapter1_complete_draft.md`

**Scope:** Update only the Chapter 1 statements affected by the change from the superseded v2.6.0 four-condition design to the frozen v2.7.0 three-condition final study. No commit was made.

## 1. Sources consulted

The v2.7 experiment records are held in the data-collection repository (`~/Dev/ai-hallucination-study`, branch `feature/data-collection`, tag `v2.7.0-freeze` on commit `bba890d`). They were read there because they are not present in this integration repository.

| Priority | Source | Used for |
| --- | --- | --- |
| 1 | `config/experiment_freeze_v2.7.0.json`, `docs/experiment_freeze_v2.7.0.md` | Design counts, retained models, M2 exclusion rationale |
| 1 | `config/api_model_set_1.5.0.json` | Exact model identifiers for M1, M3, M4 |
| 1 | `manifests/api_final_v2.7.0_manifest.csv` | Recounted: 270 rows; M1/M3/M4 90 each; 0 M2 rows; 6 categories of 45 |
| 1 | `docs/final_study_v2.7_migration_verification.md`, `docs/v2.7_freeze_tag_verification.md` | Timing of exclusion, preservation of M2 evidence, 140/130 split |
| 2 | `docs/current_research_status.md` | Confirms v2.7.0 is the active final study |
| 3 | `docs/research_progress_log.md` (2026-09-25 freeze entry) | Freeze tag and design summary |
| 4 | `docs/final_paper_notes.md` (2026-09-25 v2.7 entry) | Chapter 1 change list and disclosure requirements |

## 2. Sections changed

| Section | Change |
| --- | --- |
| Front matter (status block) | `Final v2.6 findings` changed to `Final v2.7.0 findings`; a `Design basis` line referencing the v2.7.0 freeze and this file was added. |
| 1.8 Scope and Delimitations (second paragraph, first sentence) | Four-condition, 360-observation v2.6 design replaced with the v2.7.0 three-condition, 270-observation design, interface allocation, and concise M2 disclosure. |
| 1.9 Research Contributions (final paragraph) | `pending final v2.6 analysis` changed to `pending final analysis of the frozen v2.7.0 study`. |

Sections 1.1 to 1.7, 1.10, and 1.11 were reviewed and left unchanged. They refer to "model conditions", "frozen model conditions", and "three planned separate generations" without a model count or observation total, so they remain correct under v2.7.

## 3. Obsolete statements replaced

| Location | Obsolete statement | Replacement |
| --- | --- | --- |
| Front matter | "Final v2.6 findings remain `[FINAL RESULT PENDING]`." | "Final v2.7.0 findings remain `[FINAL RESULT PENDING]`." |
| 1.8 | "The frozen v2.6 design comprises four frozen model conditions and three planned repetitions for each task-condition combination, giving 360 planned observations." | See section 4 below. |
| 1.9 | "The empirical contribution remains pending final v2.6 analysis." | "The empirical contribution remains pending final analysis of the frozen v2.7.0 study." |

The previous draft did not contain "180 API", "180 manual", "M1–M4", or any statement about future M2 collection, so none needed replacement.

## 4. Current v2.7 facts inserted (Section 1.8)

> The final frozen study, v2.7.0, comprises three frozen model conditions, identified as M1 (`cohere/north-mini-code:free`), M3 (`openai/gpt-oss-120b`), and M4 (`nvidia/nemotron-3-ultra-550b-a55b:free`), and three planned repetitions for each task-condition combination, giving 270 planned observations. Of these, 140 observations are assigned to API collection and 130 to manual collection; this interface allocation is not balanced across model conditions, and its implications are addressed in Chapter 3.

| Fact | Chapter 1 value | Source value | Match |
| --- | --- | --- | --- |
| Final study version | v2.7.0 | `experiment-freeze-v2.7.0` | YES |
| Tasks / categories | 30 / 6 (unchanged sentence in 1.8, first paragraph) | 30 / 6 | YES |
| Model conditions | 3 | 3 | YES |
| Retained IDs | M1, M3, M4 (not renumbered) | M1, M3, M4 | YES |
| Model identifiers | as in `api_model_set_1.5.0.json` | identical strings | YES |
| Repetitions | 3 | 3 | YES |
| Planned observations | 270 | 270 | YES |
| API / manual | 140 / 130 | 140 / 130 | YES |
| Interface balance | stated as not balanced across conditions | `balanced: false` | YES |

## 5. M2 disclosure wording

> One originally planned condition, M2, was removed after partial collection and before final analysis because its intended collection protocol could not be completed consistently. Previously collected M2 evidence has been preserved but is excluded from final-study analysis, and the retained conditions keep their original identifiers. Chapter 3 reports this decision in full.

Checks:

- States three retained conditions: YES (preceding sentence).
- States removal before final analysis: YES.
- Discloses that removal followed partial collection, so it is not presented as wholly prospective: YES (required by `final_paper_notes.md` 2026-09-25 entry).
- Gives the operational reason only: YES.
- Suggests removal because of empirical performance: NO.
- States M2 evidence preserved but excluded: YES.
- Defers detail (11 of 90 attempted, failure types, whole-condition exclusion) to Chapter 3: YES.

## 6. Stale-term search results

Search run on the revised file for `M2`, `M1–M4` / `M1-M4`, `four model`, `four models`, `4 model`, `360`, `180 API`, `180 manual`, `v2.6`, plus `four` (any), `Qwen`, `Darkbloom`, and wording about future collection.

| Term | Hits | Line | Classification |
| --- | ---: | --- | --- |
| `M2` | 2 | 101 (both in the disclosure) | Legitimate contextual disclosure of the excluded condition |
| `M1–M4` / `M1-M4` | 0 | | |
| `four model` / `four models` / `4 model` | 0 | | |
| `four` (any) | 0 | | |
| `360` | 0 | | |
| `180 API` / `180 manual` | 0 | | |
| `v2.6` | 0 | | |
| `Qwen` / `Darkbloom` | 0 | | |
| Future M2 collection wording | 0 | | |

Stale current-study wording remaining: **0**.

## 7. Style checks

| Check | Result |
| --- | --- |
| Em dashes (U+2014) | 0 |
| Prose double hyphens | 0 (the eleven `---` lines are Markdown horizontal rules) |
| Claims of statistical independence | None introduced |

## 8. Research questions and objectives

Unchanged. Sections 1.5 (aim), 1.6 (O1 to O4), and 1.7 (RQ1 to RQ4) refer to "the evaluated model conditions" without a count, so no embedded model-count assumption required correction.

## 9. Empirical result leakage

None. The v2.7 collection-state counts (completed, truncated, failed, pending) were deliberately not added to Chapter 1, and no prevalence, rate, ranking, statistical, or risk value appears. The chapter continues to mark final findings as `[FINAL RESULT PENDING]`.

## 10. Final recommendation

**READY_FOR_V2.7.** Chapter 1 now describes the frozen v2.7.0 three-condition, 270-observation final study, carries a concise and accurate M2 disclosure, and contains no stale four-condition, 360-observation, or v2.6-as-active wording. Chapters 2 and 3 still require their own v2.7 reconciliation.
