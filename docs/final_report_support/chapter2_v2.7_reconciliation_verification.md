# Chapter 2 v2.7 Reconciliation Verification

**Task ID:** CHAPTER-2-V2.7-RECONCILIATION-01

**Date:** 2026-09-25

**Target file:** `docs/report_drafts/chapter2_complete_draft.md`

**Scope:** Review the whole Chapter 2 literature review and update only those statements affected by the change from the superseded v2.6.0 four-condition design to the frozen v2.7.0 three-condition final study. No commit was made.

**Outcome:** No edit was required. The draft file is byte-unchanged (SHA-256 `5671aab74c513cd337db97f77203a1c65f4db2275d07cb095a98a31c6178adbd`; `git diff` empty).

## 1. Sources consulted

The v2.7 experiment records are held in the data-collection repository (`~/Dev/ai-hallucination-study`, tag `v2.7.0-freeze` on commit `bba890d`). They are not present in this integration repository, so they were read there. The integration copy of `docs/current_research_status.md` still describes v2.6 as current and was therefore not relied on for design facts; the data-collection repository copy (updated 2026-09-25) was used.

| Priority | Source | Used for |
| --- | --- | --- |
| 1 | `docs/experiment_freeze_v2.7.0.md` (at `v2.7.0-freeze`) | Design change table (4 to 3 conditions, 360 to 270, 180/180 to 140/130), M2 exclusion |
| 1 | `manifests/api_final_v2.7.0_manifest.csv` (at `v2.7.0-freeze`) | Recounted: 270 rows; M1, M3, M4 at 90 each; 0 M2 rows; 140 `api` / 130 `manual`; six categories of 45 |
| 2 | `docs/current_research_status.md` (data-collection repository) | Confirms v2.7.0 is the active final study |
| 4 | `docs/final_paper_notes.md` (2026-09-25 v2.7 entry) | Chapter 2 instruction: "minor wording updates wherever four selected conditions or Qwen/M2 appear as part of the final comparison" |
| 5 | `docs/report_drafts/chapter2_complete_draft.md` | Full review (Sections 2.1 to 2.10, Tables 2.1 and 2.2, Figures 2-1 and 2-2) |

## 2. Sections changed

None.

## 3. Sections intentionally unchanged

| Section | Reason |
| --- | --- |
| 2.1 Chapter Introduction | Describes the study only as confined to Node.js/npm; no model count or design total. |
| 2.2 to 2.7 | Literature review. References to "repetition", "hybrid", "API", and "three considerations/categories/conclusions" concern cited literature or argument structure, not the present study's design. |
| 2.8 Comparative Dimensions (incl. Table 2.2) | Concerns prior studies only. Table 2.2 has no row for the present study; line 227 states that the present study's comparisons are described in Chapter 3. |
| 2.9.1, 2.9.2 | Literature synthesis and interpretive limitations; no design statement. |
| 2.9.3 Implementation-based rationale | The only section connecting literature to the final design. It refers to "repeated independent generations under frozen model conditions" and "grouped comparisons across model conditions" without a count, version, or observation total, and explicitly reserves methodological detail for Chapter 3. This wording is correct under v2.7. Adding a model count was considered and not done, because the section deliberately stays at design level and the count is already stated in Chapter 1 (Section 1.8) and belongs in Chapter 3. |
| 2.9.4 Statement of the research gap | Refers to "the evaluated model conditions" without a count; correct under v2.7. |
| 2.10 Chapter Summary | Refers forward to Chapter 3 for "model conditions" without a count; correct under v2.7. |

## 4. Stale final-study statements replaced

None found, so none replaced. The draft never stated a model-condition count, a planned-observation total, an API/manual split, a study version, or any model identity for the present study.

## 5. Stale-term search results

Search run on the file for the required terms plus `Qwen`, `Darkbloom`, `Groq`, `OpenRouter`, the retained model identifiers, `M1` to `M4`, `v2.`, `270`, `four`, `three`, `hybrid`, `API`, `manual`, and `repetition`.

| Term | Hits | Line(s) | Classification |
| --- | ---: | --- | --- |
| `M2` | 0 | | |
| `M1–M4` / `M1-M4` | 0 | | |
| `four model` / `four models` / `4 model` | 0 | | |
| `360` | 0 | | |
| `180 API` / `180 manual` | 0 | | |
| `v2.6` (and any `v2.`) | 0 | | |
| `Qwen`, `Darkbloom`, `Groq`, `OpenRouter`, model identifiers | 0 | | |
| `four` (any) | 1 | 227 | Legitimate: "four dimensions along which prior research varies" (literature structure) |
| `repetition` | 2 | 23, 141 | Legitimate: discussion of Spracklen et al. (2025) and of repetition as a literature design dimension |
| `hybrid` | 1 | 175 | Legitimate: cited detection approach [Yang et al., 2026], not the collection interface |
| `API` | 3 | 21, 175, 219 | Legitimate: API misuse / API hallucination literature |

Stale current-study wording remaining: **0**. Stale 360 wording: **0**. M2 final-analysis inclusion: **0**.

## 6. Figure and caption impacts

| Figure | Content | Encodes model count / 360 / M1 to M4 / v2.6? | Action |
| --- | --- | --- | --- |
| Figure 2-1 (Section 2.4) | Conceptual chain from generated reference to possible supply-chain risk | No | None |
| Figure 2-2 (Section 2.9) | Literature synthesis ending in "controlled Node.js/npm empirical study" | No | None |

Both figures are placeholders (`[SPACE RESERVED FOR FIGURE 2-x]`) with no asset under `docs/report_assets/figures/`. No figure asset requires regeneration.

## 7. Reference-count impact

None. The file is unchanged, so all 39 distinct bracketed in-text citations and all narrative citations are retained. No literature was added or removed.

## 8. Empirical-result leakage check

None. The chapter contains no v2.7 collection-status counts, prevalence values, rates, rankings, statistical results, or risk scores. Section 2.1 continues to state that the review does not introduce empirical findings from the present study.

## 9. Style checks

| Check | Result |
| --- | --- |
| Em dashes (U+2014) | 0 |
| Prose double hyphens | 0 (the seven `---` lines are Markdown horizontal rules) |
| Literature-review structure | Unchanged: Sections 2.1 to 2.10, 35 section/subsection headings, Tables 2.1 and 2.2, Figures 2-1 and 2-2 |

## 10. Related items outside this task's scope

- `docs/final_report_support/claims_evidence_matrix.md` rows CH1-004 ("four model/API conditions") and CH1-006 ("v2.6 contains 360 planned observations") still record the v2.6 design as `VERIFIED`, and CH1-014 refers to a "v2.6 analysis". These are Chapter 1 claim rows and were not changed here. They should be updated to the v2.7 design (or annotated as superseded) in a separate claims-matrix reconciliation.
- The integration copy of `docs/current_research_status.md` still describes v2.6 as the current phase. The v2.7 status exists only in the data-collection repository copy.
- No `CH2-` rows in the claims matrix mention a model count, 360, M2, or v2.6.

## 11. Documentation determinations

- Progress-log update needed: YES (short entry recording that Chapter 2 was reviewed against v2.7 and needed no change).
- Final-paper note needed: NO.
- Draft reconciliation needed: NO for Chapter 2. YES for the claims matrix (Section 10).

## 12. Final recommendation

**READY_FOR_V2.7.** Chapter 2 describes the present study only at a count-independent design level, contains no four-condition, 360-observation, M2, or v2.6-as-current wording, and its figures are conceptual and independent of model count. No edit to the chapter was required.
