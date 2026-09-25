# Decision-ID Collision Reconciliation: D036

**Task:** DECISION-ID-COLLISION-RECONCILIATION-01
**Date:** 2026-09-25
**Worktree:** `~/Dev/ai-hallucination-integration` (branch `integration/final-report`)
**Authoritative data-collection repository:** `~/Dev/ai-hallucination-study` (branch `feature/data-collection`; v2.7 freeze commit `bba890d9aa5838f06bee4b1bd0e85d9e61b444f8`, tag `v2.7.0-freeze`)
**Scope:** Decision-identifier documentation only. No frozen experiment input, raw response, collection state, manifest, configuration, chapter draft, or figure was modified. Nothing was committed.

## 1. Collision identified

Two different decisions used the identifier `D036`:

| Source | Repository / branch | Decision log entry | Meaning |
|---|---|---|---|
| Data-collection D036 | `~/Dev/ai-hallucination-study`, `feature/data-collection` (recorded in commit `bba890d`, tag `v2.7.0-freeze`) | `### D036 — Remove M2 Before Final Analysis and Freeze the Three-Condition v2.7 Final Study` (dated 2026-09-25) | Removal of the whole M2 condition before final analysis; establishes the frozen three-condition (M1, M3, M4), 270-observation v2.7.0 final study. |
| Integration D036 | `~/Dev/ai-hallucination-integration`, `integration/final-report` (inherited from `analysis/pipeline`) | `### D036 — Secondary Dependency-Reliability Metrics: DFR and RDFR` (dated 2026-09-23) | Secondary/exploratory DFR and RDFR exact-name npm dependency-resolution methodology. |

Before this reconciliation, `docs/current_research_status.md` cited the M2-removal decision as "D036 on `feature/data-collection`" and explicitly noted that an integrated alias had not yet been assigned. The claims-evidence matrix (CH1-004) carried a similar branch qualifier without an integrated identifier.

## 2. Precedent used

The integrated decision log's D038 entry (`### D038 — Finalize Stranded v2.6 Active Request as a Preserved Failure`) records the earlier collision:

- the data-collection branch had recorded the recovery decision as `D032`;
- `analysis/pipeline` had independently assigned `D032` to the risk-model decision;
- the integrated branch kept its own `D032` unchanged and appended the data-collection decision under the next free integrated identifier (`D038`), with `integration_reconciliation`, `original_branch_decision_id`, and `historical_preservation` fields;
- the original `feature/data-collection` history was left unchanged.

The same convention was applied here.

## 3. Chosen integrated identifiers

| Decision | Source ID | Integrated ID | Action |
|---|---|---|---|
| M2 removal / three-condition v2.7.0 final-study freeze | `feature/data-collection` D036 | **D039** | New entry appended to `docs/decision_log.md` (the next free integrated ID; no D039 existed in either repository). |
| DFR/RDFR secondary dependency-reliability methodology | integration D036 | **D036** (retained) | No change. As in the D038 precedent, the integration-native decision keeps its identifier. |

The D039 entry reproduces the substantive fields of the source entry without changing their meaning. It adds only integration provenance (`integration_reconciliation`, `original_branch_decision_id`, `source_status`, `historical_preservation`) and one clarifying qualifier: the source entry's reference to the manual-interface decision "D035" is qualified as `feature/data-collection` D035 ("Offline Manual-Observation Preservation Scaffold for HYBRID v2.6"), because integrated D035 is the provider abnormal-termination decision.

Citation rule for future drafting in this worktree:

- a bare `D036` refers to the integrated DFR/RDFR decision;
- the M2-removal decision is cited as integrated `D039`, with "originally `feature/data-collection` D036" where provenance is required.

## 4. References updated

| File | Change |
|---|---|
| `docs/decision_log.md` | Appended `### D039 — Remove M2 Before Final Analysis and Freeze the Three-Condition v2.7 Final Study`. No existing entry was edited. |
| `docs/current_research_status.md` | The v2.7 "Controlling decision" bullet now cites integrated D039, its original `feature/data-collection` D036 identifier, and this record; the superseded "until an integrated alias is assigned" wording was replaced. |
| `docs/final_report_support/claims_evidence_matrix.md` | CH1-004 evidence cell now states the integrated alias D039 alongside the branch-local source ID. |
| `docs/final_report_support/decision_id_collision_reconciliation.md` | This record (new). |

## 5. Files intentionally unchanged

- `~/Dev/ai-hallucination-study/docs/decision_log.md` and all data-collection history: source D036 (and every other source entry) is untouched. SHA-256 of the file at inspection: `d5b1ffa98ee266b18aa4e167d590fe67a24929f52912881ce4c1a6199853a27f`.
- Integrated `### D036` entry: byte-identical before and after (section hash compared).
- `docs/research_progress_log.md` and `docs/final_paper_notes.md`: every D036 reference is a 2026-09-23 entry that refers to the integrated DFR/RDFR decision; historical entries are not rewritten. Appendable text is proposed in §7.
- `docs/report_drafts/chapter1_complete_draft.md`: contains no literal decision identifier; the M2-removal disclosure is prose only.
- `docs/report_drafts/chapter3_complete_draft.md` and other Chapter 3 drafts: contain no literal D036; their D035/D038 references are integrated IDs used with their integrated meanings. Chapter 3 v2.7 reconciliation is a separate pending task.
- All other support documents citing D036 (`analysis_specification_v1.0.md`, `package_hallucination_taxonomy.md`, `report_generation_protocol.md`, Chapter 1–3 audit/verification/reconciliation records): each refers to the DFR/RDFR decision and is therefore unambiguous under the integrated numbering.
- Figures, frozen inputs, manifests, configuration, raw data, and scripts.

## 6. Validation results

| Check | Result |
|---|---|
| Ambiguous current-study D036 references remaining | **0**. The only references to the M2-removal decision (status bullet, CH1-004, D039 entry) carry both the branch qualifier and the integrated D039 alias. All other D036 references concern DFR/RDFR. |
| Historical source D036 entries untouched | PASS (no write to the data-collection repository; integrated D036 section hash unchanged). |
| M2 removal traceable to data-collection D036 | PASS (D039 `original_branch_decision_id` and `integration_reconciliation` fields). |
| DFR/RDFR traceable to integration D036 | PASS (entry unchanged; all existing citations still resolve). |
| Experimental files modified | NONE (only Markdown files under `docs/` changed). |
| Empirical result leakage | NONE (no PHR, SHR, DFR, RDFR, risk, or grouped result added; the M2 attempt counts reproduced in D039 are source-recorded collection-state counts, not research results). |
| `git diff --check` | PASS (no output). |

### Observation outside this task's scope

The data-collection log's D033 ("Formalize HYBRID Collection-Interface Allocation as a Derived Layer"), D034 ("Constrain Future API Selection to Verified HYBRID Assignments"), and D035 ("Offline Manual-Observation Preservation Scaffold for HYBRID v2.6") also share identifiers with different integrated decisions (D033 PHR/SHR units, D034 external-dependency eligibility, D035 abnormal termination). These have not been integrated and were not given aliases here. No current integration document cites them by bare identifier except through the qualified D035 reference inside D039. If the dissertation needs to cite them, a follow-up reconciliation using the same convention (next free IDs D040 onward) is recommended.

## 7. Documentation follow-up

- Progress-log update needed: **YES**
- Final-paper note needed: **NO** (identifier housekeeping only; no methodological change)
- Draft reconciliation needed: **NO** (no chapter contains an ambiguous literal identifier)

Proposed appendable entry for `docs/research_progress_log.md`:

```markdown
### 2026-09-25 — D036 decision-ID collision reconciled

- Identified a decision-ID collision: `feature/data-collection` D036 (M2 removal / three-condition v2.7.0 final-study freeze) versus integrated D036 (secondary DFR/RDFR methodology).
- Following the D038 precedent, integrated D036 is retained for DFR/RDFR, and the M2-removal decision is appended to the integrated decision log as D039 with its original branch identifier recorded. No historical decision entry was altered.
- Updated the v2.7 controlling-decision citation in `docs/current_research_status.md` and claim CH1-004 in the claims-evidence matrix.
- No chapter draft, figure, frozen input, or experimental file was modified; no results were introduced.
- Record: `docs/final_report_support/decision_id_collision_reconciliation.md`.
```
