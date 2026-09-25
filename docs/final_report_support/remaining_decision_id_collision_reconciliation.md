# Remaining Decision-ID Collision Reconciliation: D033, D034, D035

**Task:** REMAINING-DECISION-ID-COLLISION-RECONCILIATION-01
**Date:** 2026-09-25
**Worktree:** `~/Dev/ai-hallucination-integration` (branch `integration/final-report`)
**Authoritative data-collection repository:** `~/Dev/ai-hallucination-study` (branch `feature/data-collection`; HEAD `44c7f00` at inspection, `v2.7.0-freeze-3-g44c7f00`)
**Scope:** Decision-identifier documentation only. No frozen experiment input, raw response, collection state, manifest, configuration, chapter draft, figure, or empirical result was modified. Nothing was committed.
**Predecessor record:** `docs/final_report_support/decision_id_collision_reconciliation.md` (D036 → D039). Its §6 "Observation outside this task's scope" identified the collisions resolved here. That record is historical and was not edited.

## 1. Collisions found

Three identifiers carry different decisions in the two worktrees:

| ID | Data-collection meaning (`feature/data-collection`) | Integration meaning (`integration/final-report`) |
|---|---|---|
| D033 | Formalize HYBRID Collection-Interface Allocation as a Derived Layer (2026-09-23) | Formalize Primary PHR Unit as Unique Normalized Package per Response and Confirm SHR Unit (2026-09-22) |
| D034 | Constrain Future API Selection to Verified HYBRID Assignments (2026-09-23) | Preserve D033 Primary PHR; Introduce External-Dependency Sensitivity Eligibility (2026-09-22) |
| D035 | Offline Manual-Observation Preservation Scaffold for HYBRID v2.6 (2026-09-23) | Provider Error Finish Reasons Are Failed, Metric-Ineligible Observations (2026-09-22) |

No other collisions were found for D033–D035. No `D040` or later identifier existed in either worktree before this task.

## 2. Source (data-collection) decision meanings

From `~/Dev/ai-hallucination-study/docs/decision_log.md` (SHA-256 `d5b1ffa98ee266b18aa4e167d590fe67a24929f52912881ce4c1a6199853a27f`, byte-identical to the file at tag `v2.7.0-freeze`):

- **Source D033:** creates the deterministic derived artifact `manifests/hybrid_assignment_v1.0.0.csv`, assigning each frozen v2.6 manifest row to `api` or `manual`. All 119 previously API-attempted rows are kept as API; remaining API quotas are filled from the earliest never-attempted rows in frozen manifest order (targets M1 40/50, M2 40/50, M3 41/49, M4 59/31). Assignment is independent of response outcome and is collection-design provenance, not an eligibility rule.
- **Source D034:** future v2.6 API collection is selected only by `scripts/collect_hybrid_api_batch.py`, which verifies the frozen manifest and HYBRID-assignment hashes and passes only API-assigned, never-attempted rows in frozen `collection_order` to the unchanged v2.6 collector. It adds no observations and never retries or substitutes.
- **Source D035:** adds `scripts/collect_hybrid_manual.py`, an offline-only selector and byte-preserving capture scaffold for manual-assigned rows under the separate root `data/final/manual_raw/v2.6.0/<run_id>/`. It invokes no model, API, browser, or generated code; it preserves failed or interrupted manual attempts once; and it requires a researcher-approved manual interface before any manual generation.

## 3. Integration decision meanings (unchanged)

- **Integrated D033:** the primary PHR unit is one unique `(run_id, normalized_package)` row per response; the primary SHR unit is one completed, non-truncated evaluable response; `TRUNCATED` observations are excluded from primary eligibility.
- **Integrated D034:** D033 primary PHR/SHR remain unchanged; `SELF_REFERENCE_OR_LOCAL_PACKAGE` and other `external_dependency_eligible` states affect only a separately labelled secondary/exploratory external-dependency sensitivity analysis.
- **Integrated D035:** a provider `finish_reason` other than `stop` or `length` (including `error`) makes an observation failed/`FAILED` and metric-ineligible, even when partial content exists; applied as a derived inventory overlay without editing raw artifacts.

These are the meanings named in `AGENTS.md` and `docs/report_generation_protocol.md`, and cited throughout the chapter drafts and support records.

## 4. Aliases assigned

The D038/D039 convention was applied: the integration-native decision keeps its identifier, and the data-collection decision is appended under the next free integrated identifier. The highest existing integrated identifier was D039, so the next free identifiers were D040–D042.

| Source decision | Integrated alias | Integrated ID retained |
|---|---|---|
| `feature/data-collection` D033 (HYBRID allocation) | **D040** | D033 = PHR/SHR units |
| `feature/data-collection` D034 (HYBRID API selection) | **D041** | D034 = external-dependency eligibility boundary |
| `feature/data-collection` D035 (manual preservation scaffold) | **D042** | D035 = abnormal provider termination |

Each alias entry in `docs/decision_log.md` reproduces every source field verbatim. It adds only integration provenance fields: `integration_reconciliation`, `original_branch_decision_id`, `integration_note`, `historical_preservation`, and `integration_record`. There are four intentional textual differences from the source. A verbatim line-comparison script confirmed that no other source line differs:

1. D041 `status`: appended "(status as recorded in the source entry on 2026-09-23)".
2. D041 `current_operational_state`: key annotated "(as recorded in the source entry, 2026-09-23)", because the snapshot is historical.
3. D042 `status`: appended "(status as recorded in the source entry)".
4. D042 `manual-interface boundary`: the source's bare "D033" is qualified as "[source `feature/data-collection` D033; integrated D040]", because a bare D033 would otherwise resolve to the PHR/SHR-unit decision in this worktree.

Citation rule for future drafting in this worktree:

- a bare D033, D034, or D035 refers to the integrated metric/eligibility/termination decision;
- the HYBRID allocation, HYBRID API selection, and manual preservation scaffold are cited as D040, D041, and D042 respectively, with "originally `feature/data-collection` D033/D034/D035" where provenance is required.

## 5. Provenance

| Alias | Source repository / branch | Source introducing commit | Tag containing it |
|---|---|---|---|
| D040 | `~/Dev/ai-hallucination-study`, `feature/data-collection` | `ce13048bc7a426e856b8c46fd7f70e68540e781b` (2026-09-23, "research: record deterministic v2.6 hybrid allocation") | `v2.7.0-freeze` |
| D041 | same | `7b2a23f707ef037c1880f5b4f1e00bd369b742ba` (2026-09-23, "feat(collection): enforce hybrid API assignment") | `v2.7.0-freeze` |
| D042 | same | `8accdc54df5678df7ae978f50751476542d73ca1` (2026-09-23, "feat(collection): add hybrid manual capture workflow") | `v2.7.0-freeze` |

Implementation artifacts present in the source repository at tag `v2.7.0-freeze` (checked read-only with `git ls-tree`): `manifests/hybrid_assignment_v1.0.0.csv`, `scripts/create_hybrid_assignment_v1_0.py`, `scripts/collect_hybrid_api_batch.py`, and `scripts/collect_hybrid_manual.py`.

## 6. References updated

| File | Change |
|---|---|
| `docs/decision_log.md` | Appended D040, D041, and D042. No existing entry was edited. |
| `docs/current_research_status.md` | (a) v2.7 interface-assignment bullet: added "Allocation decision: integrated D040 (originally D033 on `feature/data-collection`; not the integrated D033 PHR/SHR-unit decision)". (b) Evidence-reuse bullet: added the D042 manual-scaffold citation with its source ID and the researcher-approved-interface requirement. (c) Controlling-decision bullet: the collision-record pointer now also names this record. |
| `docs/final_report_support/claims_evidence_matrix.md` | CH1-006 (140 API / 130 manual) evidence cell now cites `docs/decision_log.md` D039 and D040, stating that D040 is `feature/data-collection` D033 rather than integrated D033. Status and claim text were not changed. |
| `docs/final_report_support/remaining_decision_id_collision_reconciliation.md` | This record (new). |

Before this task, no current-study reference used D033, D034, or D035 in the data-collection meaning without qualification. Every such reference already had the integrated meaning. The only data-collection-meaning reference was inside integrated D039 and was already qualified, and it now resolves to D042 as noted in D042's `integration_note`. The updates above therefore add citations where the HYBRID allocation and manual scaffold were described without any decision ID. They do not correct misattributed identifiers.

## 7. Files intentionally unchanged

- `~/Dev/ai-hallucination-study` (all files, including `docs/decision_log.md`): read-only. Its source D033–D035 entries keep their original IDs, and the file hash is unchanged.
- Integrated D033–D039 entries: section hashes before and after this task are identical.
- `docs/report_drafts/chapter1_complete_draft.md`: contains no literal D033/D034/D035.
- `docs/report_drafts/chapter3_complete_draft.md`: contains no literal D033/D034/D035. Its §3.5.2 "Hybrid collection and preservation boundary" prose cites no decision ID and was not changed. Chapter 3 v2.7 reconciliation is a separate pending task, and it may cite D040–D042 there.
- `docs/report_drafts/chapter3_sections_3_5_to_3_9.md`: D035 references (lines 38, 63, 81) use the integrated abnormal-termination meaning.
- `docs/final_paper_notes.md`: D033/D034/D035 references (e.g., lines 432–433, 494–532, 557, 576) all use integrated meanings. The 2026-09-23 hybrid-allocation note (line 582) cites no decision ID. Historical notes are not rewritten.
- `docs/research_progress_log.md`: all D033/D034/D035 references use integrated meanings, and historical entries are not rewritten. Appendable text is proposed in §9.
- `docs/final_report_support/decision_id_collision_reconciliation.md`: historical predecessor record. Its "not given aliases here" statement was accurate at the time and is superseded by this record.
- `AGENTS.md`, `docs/report_generation_protocol.md`, `docs/analysis_specification_v1.0.md`, `docs/package_hallucination_taxonomy.md`, and the Chapter 1–3 audit, verification, and reconciliation records: all D033/D034/D035 references use integrated meanings.
- Figures (including the untracked `figure3_4_metric_derivation.*`), frozen inputs, manifests, configuration, raw data, collection state, and scripts.

## 8. Validation results

| Check | Result |
|---|---|
| Integrated D033 unchanged | PASS (section SHA-256 `d322b220…3fda68` before and after) |
| Integrated D034 unchanged | PASS (`dccc13ee…39dc4d` before and after) |
| Integrated D035 unchanged | PASS (`4f459ad0…e414a` before and after) |
| Integrated D036–D039 unchanged | PASS (section hashes identical; `git diff` on `docs/decision_log.md` contains additions only, 0 removed lines) |
| Source D033 has unique integration alias | PASS (D040) |
| Source D034 has unique integration alias | PASS (D041) |
| Source D035 has unique integration alias | PASS (D042) |
| Duplicate `### Dnnn` headings in integrated log | NONE |
| Source fields reproduced verbatim | PASS (line comparison; only the four intentional qualifiers in §4 differ) |
| Ambiguous current-study D033/D034/D035 references remaining | **0**. A keyword scan (D033–D035 co-occurring with HYBRID/allocation/manual-interface terms, excluding lines with explicit source qualification) returned one line, `chapter3_methodology_reconciliation.md:73`. It is a false positive: there, D035 denotes the integrated abnormal-termination rule, and "hybrid" appears in an unrelated sentence. |
| Chapter methodology meaning changed | NO (no chapter draft modified) |
| Empirical result leakage | NONE (no PHR, SHR, DFR, RDFR, risk, or grouped value added; the row counts in D040/D041 are source-recorded allocation and collection-state counts, not research results) |
| Experimental files modified | NONE (only Markdown under `docs/` changed) |
| Data-collection repository modified | NONE (`docs/decision_log.md` SHA-256 unchanged; clean status) |
| `git diff --check` | PASS (no output) |

## 9. Documentation follow-up

- Progress-log update needed: **YES**
- Final-paper note needed: **NO** (identifier housekeeping only; no methodological change)
- Draft reconciliation needed: **NO** for existing chapters (no ambiguous literal identifier). The pending Chapter 3 v2.7 reconciliation should cite D040–D042, not D033–D035, if it names the HYBRID allocation, HYBRID API selection, or manual scaffold.

Proposed appendable entry for `docs/research_progress_log.md`:

```markdown
### 2026-09-25 — Remaining decision-ID collisions D033–D035 resolved

- Resolved the cross-worktree D033, D034, and D035 decision-ID collisions before Chapter 3 v2.7 reconciliation.
- Integrated D033 (primary PHR/SHR units), D034 (primary/secondary external-dependency boundary), and D035 (abnormal provider termination) remain unchanged.
- Following the D038/D039 precedent, the data-collection decisions are represented in the integration worktree as D040 (HYBRID collection-interface allocation; originally `feature/data-collection` D033, commit `ce13048`), D041 (HYBRID-constrained API selection; originally D034, commit `7b2a23f`), and D042 (offline manual-observation preservation scaffold; originally D035, commit `8accdc5`), all contained in tag `v2.7.0-freeze`. Source decision meanings are preserved verbatim; no historical decision entry was altered.
- Added D040/D042 citations in `docs/current_research_status.md` and a D039/D040 citation in claim CH1-006 of the claims-evidence matrix.
- No chapter draft, figure asset, frozen experimental input, or empirical result was modified.
- Record: `docs/final_report_support/remaining_decision_id_collision_reconciliation.md`.
```
