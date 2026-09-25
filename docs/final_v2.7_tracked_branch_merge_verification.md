# Final v2.7 Tracked-Branch Merge Verification

**Task ID:** FINAL-V2.7-BRANCH-CONSOLIDATION-01

**Date:** 2026-09-25

**Worktree:** `~/Dev/ai-hallucination-final`

**Target branch:** `integration/v2.7-final`

**Scope:** This task merged tracked Git history only. The final worktree is **not yet fully consolidated**. The gitignored raw API evidence (`data/final/raw/**`) and the analysis-local untracked material (`data/derived_checkpoints/`, `data/quarantine/`) have not been copied (see section 9). Nothing was pushed.

## 1. Base

| Item | Value |
| --- | --- |
| Base branch | `origin/feature/data-collection` |
| Base commit (starting `integration/v2.7-final` HEAD) | `38711b818f460117098a5cd1aef3364011830f45` ("chore: document and remove accidental npm dependency") |
| Worktree state at start | clean |

## 2. Source pins (verified before merging)

After `git fetch origin`, each remote branch pointed to its expected commit. No SHA differed.

| Order | Source | Remote branch | Pinned SHA (verified) |
| ---: | --- | --- | --- |
| 1 | M3 manual | `origin/collection/m3-manual-v2.6` | `ee952dca123a7eda1e7ea5e8c7f9518ed2e70608` |
| 2 | M1 manual | `origin/collection/m1-manual-v2.6` | `1e062808dd26462b8afca2967aebc102eff066bf` |
| 3 | M4 manual | `origin/collection/m4-manual-v2.6` | `fb0d56ad0069c3f95b37493dcbcdf72a98c8c3ce` |
| 4 | Final report / integration | `origin/integration/final-report` | `628de2487f229112a342291d1f7ebe14488fad54` |
| 5 | Analysis pipeline | `origin/analysis/pipeline` | `7733bd48a26f50dedf3a1d9b75436bf6325be52e` |

## 3. Merge commits

Every source was merged with `git merge --no-ff` in this order, which created an explicit merge commit each time. There was no rebase, squash, or history rewrite.

| Order | Source | Merge commit | Parents |
| ---: | --- | --- | --- |
| 1 | M3 manual | `8eeb372f674ecb5168c7b999fa49d7daa9b522aa` | `38711b8`, `ee952dc` |
| 2 | M1 manual | `c828e4449de26d8bf31eff5af80fe7a8982c87d5` | `8eeb372`, `1e06280` |
| 3 | M4 manual | `56be98f10b5f3abf55f656c2cd06e6520338eaef` | `c828e44`, `fb0d56a` |
| 4 | integration/final-report | `5b00010e060486e1abe1ca3658e0a75fc0f9cf19` | `56be98f`, `628de24` |
| 5 | analysis/pipeline | `fccaf2ee14bf63a5d2eba84eb15ed656a7bcf92b` | `5b00010`, `7733bd4` |

## 4. Conflicts and exact resolutions

Only documentation files conflicted. No data, code, schema, manifest, configuration, or frozen file conflicted in any merge.

### 4.1 Merges 1–3 (M3, M1, M4 manual)

Conflicted files: `docs/final_paper_notes.md` and `docs/research_progress_log.md`.

- **Cause:** append/append. Each side added new dated entries after the same shared entry. No existing line was edited on either side.
- **Resolution:** both sides were kept. HEAD entries come first, then the source branch's entries, with only the conflict-marker lines removed. For M4, git had aligned the shared "0 missing …" bullets of the M1 and M4 entries into two interleaved hunks. That file was therefore rebuilt as the full HEAD file followed verbatim by the M4 branch's pure tail-append over the merge base, so neither entry was interleaved.
- **Check:** 0 lines of either parent are missing from the result.

### 4.2 Merge 4 (integration/final-report)

Four files conflicted.

**`docs/decision_log.md`**

- The integration/final-report side (D001–D042) was taken, including its decision-number reconciliation. The source `feature/data-collection` D032–D036 are integrated as D038, D040, D041, D042, and D039, each with `original_branch_decision_id` provenance.
- D043 and D044 were then appended verbatim from the data-collection side.
- The data-collection side made no edit to any pre-existing entry. Its only changes after the merge base were appends: D033–D036, which are present as integrated D039–D042 in the taken file, plus D043 and D044.
- The D043 `numbering_note` already states the integrated D037–D042 allocation, so its cross-references remain unambiguous.
- Result: 44 decision headings, D001–D044, with 0 duplicate IDs. No conflicting duplicate D033–D042 meaning was reintroduced.

**`docs/current_research_status.md`**

The HEAD version, which records the verified v2.7 collection-complete state, was used as the authoritative base, with these targeted changes:

- The header and phase line were updated to record tracked-branch consolidation and the pending raw-evidence copy.
- The M2-removal reference "decision D036" was rewritten to integrated **D039** (originally D036 on `feature/data-collection`), because integrated D036 is the DFR/RDFR decision.
- Still-valid integration/final-report content was carried over:
  - the freeze-tag verification path
  - the D040/D042 allocation and scaffold mapping
  - the decision-ID collision records
  - the v2.7 schema path
  - the "no final PHR/SHR, DFR/RDFR, grouped comparison, or risk output exists; `[FINAL RESULT PENDING]`" statement
  - the v2.6 freeze commit, collection start, M2 deferral, and quarantine facts
  - the "excluded from v2.5 and later primary analysis" wording
  - the full "Analysis infrastructure status" section, verbatim
- The manual-branch sentence now says the branches are merged, and the consolidation open item lists the remaining work.
- A dated consolidation note was appended after the infrastructure section. It records that the `feature/data-collection` collector also implements the abnormal-finish-reason rule (`57e51f7`) and that both histories are now merged.
- Two integration-side statements were not carried over because the collection-complete state supersedes them: "v2.7 freeze records … are not present in this integration worktree" and "The 130 manual-assigned rows remain pending manual collection".

**`docs/final_paper_notes.md` and `docs/research_progress_log.md`**

- Both sides were verified as pure appends over the merge base `5d7de91`.
- The result is the HEAD file followed verbatim by the source's appended entries.
- 0 lines of either parent are missing.

### 4.3 Merge 5 (analysis/pipeline)

Conflicted files: `docs/final_paper_notes.md` and `docs/research_progress_log.md`.

- The source side was verified as a pure append over the merge base `102320f`. The result is the HEAD file followed verbatim by the source's appended entries.
- None of the appended entries was an exact duplicate of text already in HEAD, so nothing was dropped.
- The source's "2026-09-23 — Final dissertation reporting control layer established" entry is a **near-duplicate** of the entry already carried from integration/final-report. It differs in two wording details: the formatting of `VERIFIED`/`PENDING`/`REJECTED`, and "was not present" versus "is not currently present". It is kept verbatim as append-only history.
- The source also contains two pairs of same-titled 2026-09-24 entries. These are the source's own history and are kept verbatim.
- 0 lines of either parent are missing.

### 4.4 Auto-merged but semantically sensitive

- **`scripts/collect_api_run.py` and `tests/test_api_collection.py`** were changed on both sides and merged cleanly. All scripts compile.
- **`AGENTS.md`** now carries the integration/final-report wording, which describes an "integrated final-report worktree" and says live collection is authoritative in `~/Dev/ai-hallucination-study`. Preflight §6 and §9 anticipate this, and it needs a wording update as a researcher decision.
- **`.analysis-repository-marker` and `scripts/repository_guard.py`** now block the legacy live-collection entry points in this branch. The `collect_hybrid_*.py` scripts do not call the guard. This is a researcher decision under preflight §9 B3.

## 5. Source ancestry

| Commit | Ancestor of HEAD |
| --- | --- |
| `ee952dc` (M3) | YES |
| `1e06280` (M1) | YES |
| `fb0d56a` (M4) | YES |
| `628de24` (integration/final-report) | YES |
| `7733bd4` (analysis/pipeline) | YES |
| `38711b8` (base) | YES |

## 6. Manual data

| Condition | Directories | Recorded `actual_model` | Recorded `actual_interface` |
| --- | ---: | --- | --- |
| M1 | 50 | `cohere/north-mini-code:free` | OpenRouter Chatroom web UI |
| M3 | 49 | `openai/gpt-oss-120b` | Groq Playground web UI |
| M4 | 31 | `nvidia/nemotron-3-ultra-550b-a55b:free` | OpenRouter Chatroom web UI |
| M2 | 0 | n/a | n/a |
| **Total** | **130** | | |

- Every directory contains exactly `metadata.json`, `prompt.txt`, and `response.md`.
- The set of 130 manual directory names equals the set of manual-assigned `run_id`s in `manifests/api_final_v2.7.0_manifest.csv`.
- `git diff <source> HEAD` over each model's manual directories returns 0 differences for M3 against `ee952dc`, M1 against `1e06280`, and M4 against `fb0d56a`. No manual response file was modified by the merges.

## 7. Frozen study

**Manifest (`manifests/api_final_v2.7.0_manifest.csv`)**

| Check | Expected | Observed |
| --- | ---: | ---: |
| Rows (unique `run_id`) | 270 | 270 (270) |
| M1 / M3 / M4 | 90 / 90 / 90 | 90 / 90 / 90 |
| M2 | 0 | 0 |
| API / manual | 140 / 130 | 140 / 130 |
| AUTH-FED, PKI-CRYPTO, DOC-BINARY, ENT-INT, DATA-ADV, DIST-OBS | 45 each | 45 each |

**Freeze tag**

`v2.7.0-freeze` → `bba890d9aa5838f06bee4b1bd0e85d9e61b444f8`. This was checked after every merge and did not change.

**Frozen hashes**

- All 43 `path`/`sha256` pairs recorded in `config/experiment_freeze_v2.7.0.json` were recomputed against the working tree after every merge: 43 match, 0 mismatch, 0 missing.
- `git diff bba890d HEAD` is empty for all of these:
  - `config/api_model_set_1.5.0.json`
  - `config/experiment_freeze_v2.7.0.json`
  - `data/final/collection_state_v2.7.0.json`
  - `docs/experiment_freeze_v2.7.0.md`
  - `manifests/api_final_v2.7.0_manifest.csv`
  - `schemas/api_model_set_v2_7.schema.json`
  - `scripts/create_experiment_freeze_v2_7.py`
  - `prompts/`
  - `data/generated_prompts/`
  - the v2.6 freeze JSON, v2.6 manifest, model set 1.4.0, and `manifests/hybrid_assignment_v1.0.0.csv`
- No frozen path was changed by any source branch.

**Raw-dependent checks, pending the raw-evidence copy**

- `create_experiment_freeze_v2_7.py --check` currently reports `FAIL: API-assigned retained row has no preserved v2.6 observation: API-v2.6-AUTH-FED-01-M1-R01`.
- `create_hybrid_assignment_v1_0.py --verify` currently reports `FAIL: a pre-HYBRID attempted observation is missing from current raw observations`.
- Both read `data/final/raw/`, which is gitignored and not yet present in this worktree. The same checks fail identically on the base commit in a worktree without raw evidence. They must be rerun after the raw evidence is copied.

## 8. Tests and report assets

**Test suite**

- `python3 -m unittest discover -s tests`: 370 tests, 6 failures, 143 errors.
- The pre-merge base `38711b8`, run in a temporary worktree with no raw evidence, had 164 tests with 5 failures and 143 errors.
- Comparing failing test names, the only failure not present on the base is `test_repository_guard…test_quarantine_evidence_is_untouched`. It is a test introduced by integration/final-report that requires the untracked `data/quarantine/` directory, as expected under preflight §8/B3.
- Every other failure or error is caused by the absent `data/final/raw/` evidence.
- `tests.test_analyze_group_comparisons` (36 tests) passes.

**Report assets**

- Chapter 1–3 drafts are present in `docs/report_drafts/` (9 files):
  - chapter1_complete_draft
  - chapter2_complete_draft and the section files for 2.1–2.4, 2.5–2.7, and 2.8–2.10
  - chapter3_complete_draft and the section files for 3.1–3.4, 3.5–3.9, and 3.10–3.16
- The five Chapter 3 figures are present in `docs/report_assets/figures/chapter3/created by me/`: Figure 3-1, 3-2, 3-3, figure_3_4, and Figure_3-5_Risk_Framework.
- `docs/final_report_support/` (24 files), `docs/references/approved_references.md`, and `docs/report_generation_protocol.md` are present.
- `git diff 628de24 HEAD` over all of these paths is empty.

**Other checks**

- **Decisions:** D043 and D044 are present, and all 44 IDs are unique.
- **Conflict markers:** there are no unmerged paths and no conflict markers in tracked text files.
- **Raw evidence in Git:** only `data/final/raw/.gitkeep` is tracked, and `.gitignore:35 data/final/raw/*` is unchanged.

## 9. Remaining work (not done in this task)

1. **Raw API evidence.** Copy `data/final/raw/` byte-for-byte from `~/Dev/ai-hallucination-study` into this worktree without adding it to Git, then run `sha256sum -c reports/final_v2.7_raw_evidence_inventory.sha256` (D043). After that, rerun `create_experiment_freeze_v2_7.py --check`, `create_experiment_freeze_v2_6.py --check`, `create_hybrid_assignment_v1_0.py --verify`, and the full test suite.
2. **Analysis-local untracked material.** Preserve `~/Dev/ai-hallucination-analysis/data/derived_checkpoints/` and `~/Dev/ai-hallucination-analysis/data/quarantine/`. Neither was copied or deleted by this task.
3. **Guard tests (preflight §9 B3).** `test_raw_final_contains_no_active_v2_6_run_directories` will fail once raw evidence is present, and `test_quarantine_evidence_is_untouched` needs the quarantine directory. The fix is a documented test adjustment, not a data change.
4. **Researcher decisions.** Decide the `AGENTS.md` wording for the canonical worktree and whether the repository guard should cover `collect_hybrid_*.py`.
5. **Push.** `integration/v2.7-final` has not been pushed.
