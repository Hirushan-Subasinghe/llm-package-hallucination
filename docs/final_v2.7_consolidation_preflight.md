# FINAL-V2.7-CONSOLIDATION-PREFLIGHT-02

**Prepared (UTC):** 2026-09-25
**Repository:** `~/Dev/ai-hallucination-study` (shared `.git` for all three worktrees)
**Nature:** read-only audit plus a consolidation plan. Nothing was merged, rebased, stashed, reset, deleted, copied, committed, or checked out. No branch or worktree was created. The only write operations were:

- `git fetch origin --prune --tags`, which updated remote-tracking refs only. No remote ref changed as a result.
- Creating this file, which is untracked.

Conflicts were forecast with `git merge-tree --write-tree`. This command writes only unreachable tree and blob objects. It does not change refs, the index, or any worktree.

**Scope of verification:** every hash and count below was recomputed from repository objects or files on disk during this audit. None was copied from earlier documents.

---

## 1. Refs (Part 1)

| Branch | Local HEAD | Remote (`origin/…`) | Notes |
|---|---|---|---|
| `feature/data-collection` | `44c7f0091cc0033a16b9509d6252f2020dacf96c` | `8accdc54df5678df7ae978f50751476542d73ca1` | Local is 5 commits ahead of the remote (the v2.7 commits `f845261..44c7f00`), and they are **not pushed**. Checked out in `~/Dev/ai-hallucination-study`. |
| `collection/m1-manual-v2.6` | *(no local branch)* | `1e062808dd26462b8afca2967aebc102eff066bf` | Exists only as a remote branch. |
| `collection/m3-manual-v2.6` | *(no local branch)* | `ee952dca123a7eda1e7ea5e8c7f9518ed2e70608` | Exists only as a remote branch. |
| `collection/m4-manual-v2.6` | *(no local branch)* | `fb0d56ad0069c3f95b37493dcbcdf72a98c8c3ce` | Exists only as a remote branch. |
| `analysis/pipeline` | `7733bd48a26f50dedf3a1d9b75436bf6325be52e` | *(none)* | **Local only, no remote backup.** Checked out in `~/Dev/ai-hallucination-analysis`. |
| `integration/final-report` | `628de2487f229112a342291d1f7ebe14488fad54` | *(none)* | **Local only, no remote backup.** Checked out in `~/Dev/ai-hallucination-integration`. |
| `main` | `5247c2bccb58ecd6c86b9b7e92d800ade0378282` | same | Equals `v2.6.0-freeze`. |

**Freeze tag:** `v2.7.0-freeze` is an annotated tag and resolves to `bba890d9aa5838f06bee4b1bd0e85d9e61b444f8`. **Confirmed unchanged.** The freeze commit is an ancestor of the local `feature/data-collection`.

**Frozen inputs:** all 39 hashed inputs in `config/experiment_freeze_v2.7.0.json` match both the working tree and the tag. The 39 inputs are:

- the manifest
- the model set
- the prompt template
- the task set
- the initial collection state
- 30 rendered prompts
- 4 schemas

`config/experiment_freeze_v2.7.0.json` itself is also byte-identical between HEAD and the tag.

---

## 2. Manual-branch verification (Part 2)

**Method:** the script at `scratchpad/verify_manual.py` read every file with `git show <origin ref>:<path>`, without any checkout. It checked each run against the frozen `manifests/api_final_v2.7.0_manifest.csv` and against the rendered prompt bytes at `v2.7.0-freeze`.

| Check | M1 | M3 | M4 |
|---|---|---|---|
| Source ref | `origin/collection/m1-manual-v2.6` @ `1e06280` | `origin/collection/m3-manual-v2.6` @ `ee952dc` | `origin/collection/m4-manual-v2.6` @ `fb0d56a` |
| Forked from the approved manual-capture workflow | yes, merge-base `8accdc5` ("feat(collection): add hybrid manual capture workflow", D035 on this branch) | yes, `8accdc5` | yes, `8accdc5` |
| Run directories | **50** | **49** | **31** |
| Tracked files under `data/final/manual_raw/v2.6.0/` | 150 | 147 | 93 |
| Each run has exactly `metadata.json`, `prompt.txt`, `response.md` | yes | yes | yes |
| All runs are v2.7 rows with `collection_interface=manual` for this model | yes | yes | yes |
| Missing assigned runs / extra runs | 0 / 0 | 0 / 0 | 0 / 0 |
| M2 runs | 0 | 0 | 0 |
| `prompt.txt` SHA-256 = manifest `expected_prompt_sha256` = frozen rendered prompt = `metadata.prompt_sha256` | all | all | all |
| `metadata.raw_response_sha256` and `raw_response_size_bytes` match `response.md` | all | all | all |
| Metadata identity (`run_id`, model, `expected_model_id`, `actual_model`, `task_id`, `run_repetition`, `collection_order` = `source_collection_order`) | all match | all match | all match |
| `response_status` | 50 completed | 49 completed | 31 completed |
| `actual_interface` | OpenRouter Chatroom web UI | Groq Playground web UI | OpenRouter Chatroom web UI |
| `operator_id` | collector_01 | collector_01 | collector_01 |
| Overwritten evidence: history since `8accdc5` | add-only (150 A). The only M entries are the 2 append-log docs. | add-only (147 A across 3 commits, no manual_raw path touched twice) | add-only (93 A) |
| Other paths changed | `docs/final_paper_notes.md`, `docs/research_progress_log.md` | same | same |

**Union:** 50 + 49 + 31 = **130 unique run IDs**. There are **0 duplicates**, and the union equals exactly the 130 manual-assigned rows of the v2.7 manifest.

### Provenance facts to disclose (not defects)

These come from the metadata `captured_at_utc` values. The v2.7 freeze timestamp is `2026-09-24T23:22:58.369305Z`.

- **M3:** all 49 runs were captured before the freeze, between 2026-09-24T08:34Z and 18:51Z.
- **M1:** 36 runs were captured before the freeze and 14 after, between 20:04Z and 00:45Z.
- **M4:** all 31 runs were captured after the freeze, between 23:48Z and 02:55Z.

The frozen `data/final/collection_state_v2.7.0.json` therefore records all 130 manual rows as `pending`, although 85 had already been captured on unmerged branches.

This does not invalidate the observations, for three reasons:

- The v2.7 membership rule does not depend on outcomes.
- Prompts, run IDs and interface assignment are unchanged.
- M1, M3 and M4 definitions are identical in model sets 1.4.0 and 1.5.0.

It should still be disclosed in Chapter 3 and in the decision log.

**Authorship as observed:** commit `d581af8` (M3, 34 observations) is authored by "Dineth Bandara Kandegedara". All other manual commits are authored by "Lisath Methsadu". All metadata records `operator_id: collector_01`.

---

## 3. API final state (Part 3)

The source of truth is `data/final/collection_state_v2.7.0.json` (hash-verified against the freeze), checked against the raw directories on disk.

| Model | API-assigned | completed | truncated | failed | pending |
|---|---|---|---|---|---|
| M1 | 40 | 27 | 10 | 3 | 0 |
| M3 | 41 | 36 | 0 | 5 | 0 |
| M4 | 59 | 42 | 6 | 11 | 0 |
| **Total** | **140** | **105** | **16** | **19** | **0** |

All 140 API rows point to a directory in `data/final/raw/`. For each of them, all of the following hold:

- `metadata.json` SHA-256 matches `evidence.metadata_sha256`.
- `prompt.txt` SHA-256 matches `evidence.prompt_sha256`.
- `response.md` SHA-256 matches `evidence.response_sha256` wherever one is recorded.
- The metadata status equals the state status.

**Problems found: 0.** No API-assigned v2.7 row lacks an immutable final state. No API row is pending.

Other raw directories on disk:

- **M2 historical evidence:** the 11 `API-v2.6-*-M2-*` directories are present on disk. They are the only v2.6 raw directories outside the v2.7 manifest.
- **Earlier versions:** `API-*` (2), `API-v2.1` (4), `API-v2.2` (10), `API-v2.3` (8), `API-v2.4` (30) and `API-v2.5` (24) are also present.
- **Total:** 229 directories, about 48 MB.

### Is final v2.7 data generation complete?

**Yes, at the evidence level:**

- 140 of 140 API rows have terminal states. Failed and truncated rows are final under the freeze policy: no retry and no regeneration.
- 130 of 130 manual rows have completed evidence.

**However,** no v2.7 collection-state record yet reflects manual completion; the frozen state still says `pending`. A new, append-only derived record is needed, for example `data/final/collection_state_v2.7.0_final.json` or an equivalent approved name. It must not edit the frozen file. This is post-merge bookkeeping, not missing data.

### Modified `data/final/api_batch_state_v2.6.0.json`

This file needs a **dedicated provenance checkpoint before consolidation (MUST_CHECKPOINT).**

- The working-tree SHA-256 is `1a3af56d138d3da1c3e67c1f04f55b27e4ab5d0ec786ab31d7c2cd17cb6b695c`. **This is exactly the hash that the frozen v2.7 collection state cites** as `source_v2_6_state_snapshot.sha256`.
- The committed (HEAD) version is `631b20b2…` and is **not** the cited snapshot.
- The difference is append-only:
  - The first 1008 events are identical.
  - 65 events were appended, dated 2026-09-23T14:00Z onwards: M1 23 completed, M3 2 completed, M2 1 completed, plus reservation and failure events.
  - `updated_at_utc` and `provider_next_allowed_at_epoch` were advanced.
- The file mtime is 2026-09-24 03:17Z, before the freeze.

Without a commit, the cited snapshot cannot be reproduced from git. A new worktree would also receive the older HEAD version, and `tests/test_repository_guard.py::test_v2_6_batch_state_file_is_byte_identical_to_head` compares against HEAD.

---

## 4. Branch relationships (Part 4)

```
main (5247c2b = v2.6.0-freeze)
 └─ 5a379d7 ───────────┬── fa01ad4, fc02f0a, 102320f ── 7733bd4            analysis/pipeline
                       │                     └──────────┐
 └─ … 5d7de91 ─────────┼────────────────────────── 2607907 (merge) … 628de24  integration/final-report
      └─ 57e51f7, ce13048, d912b66, 7b2a23f, 8accdc5 ┬─ f845261, bba890d*, f86218f, 1c8fd9b, 44c7f00  feature/data-collection
                                                     ├─ d68460e, 1e06280            collection/m1-manual-v2.6
                                                     ├─ d581af8, 4ae8344, ee952dc   collection/m3-manual-v2.6
                                                     └─ 44d3e24, fb0d56a            collection/m4-manual-v2.6
   * bba890d = v2.7.0-freeze
```

| Pair | Merge-base | Unique commits (left / right) |
|---|---|---|
| feature/data-collection vs each manual branch | `8accdc5` | fdc 5 / m1 2, m3 3, m4 2 |
| feature/data-collection vs integration/final-report | `5d7de91` | fdc 10 / ifr 41 |
| feature/data-collection vs analysis/pipeline | `5a379d7` | fdc 12 / ap 4 |
| integration/final-report vs analysis/pipeline | `102320f` | ifr 40 / ap **1** (`7733bd4` only) |

Notes on these relationships:

- `integration/final-report` already contains `analysis/pipeline` up to `102320f`, through merge `2607907`. `analysis/pipeline` adds only `7733bd4`, the fix for Fisher comparisons with zero events.
- `integration/final-report` has already reconciled the decision-ID collisions. The source D032, D033, D034, D035 and D036 on `feature/data-collection` become integrated D038, D040, D041, D042 and D039. Integrated D032–D037 remain the analysis decisions.
- The frozen `config/experiment_freeze_v2.7.0.json` still cites `"decision_log_entry": "D036"`, meaning the source ID. The integrated D039 entry documents this alias, and that is sufficient.

### Recommended target

- **Canonical worktree:** `~/Dev/ai-hallucination-final`. Appropriate, and it matches the sibling-directory convention (`ai-hallucination-analysis`, `ai-hallucination-integration`).
- **Canonical branch:** `integration/v2.7-final`. Appropriate. It follows the existing `integration/…` prefix and carries the study version. No rename is justified.
- **Base branch:** `feature/data-collection`, at the Phase-0 checkpoint commit and not at `44c7f00`. Reasons:
  - Its first-parent history is the frozen data lineage and contains `v2.7.0-freeze`.
  - All three manual branches fork from it.
  - Every frozen input, the v2.7 state, the manifest and the collection scripts are authoritative there.
  - Merging report and analysis work on top keeps `git log --first-parent` readable as "frozen data → evidence → analysis/report".
- **Rejected alternative: base on `integration/final-report`.** It is possible and yields the same final tree, but it places the frozen data lineage on a second-parent path.

---

## 5. Merge order (Part 5)

### Candidate order evaluated

The candidate order was: fdc → M1 → M3 → M4 → analysis/pipeline → integration/final-report. It is **not optimal**:

- Merging `analysis/pipeline` before `integration/final-report` makes you resolve the D032–D037 decision-ID collision **by hand**. It produces 4 conflicting files, including a 258-line hunk in `decision_log.md` and a hunk in `current_research_status.md`. `integration/final-report` has already resolved exactly this collision, with an audit trail.
- If `integration/final-report` is merged first, `analysis/pipeline` then adds just one commit and conflicts only in the two append-only logs.

### Recommended order

Every step uses `git merge --no-ff`. Every source branch diverged, so real merge commits are needed in any case. `--no-ff` guarantees one auditable merge commit per source.

| Step | Source | Pinned SHA | Why here |
|---|---|---|---|
| 0 | base: `feature/data-collection` (after Phase-0 checkpoint commits) | new tip | frozen data lineage |
| 1 | `origin/collection/m3-manual-v2.6` | `ee952dca123a7eda1e7ea5e8c7f9518ed2e70608` | completed first (2026-09-24T19:55Z); append-log entries stay chronological |
| 2 | `origin/collection/m1-manual-v2.6` | `1e062808dd26462b8afca2967aebc102eff066bf` | completed 2026-09-25T00:54Z |
| 3 | `origin/collection/m4-manual-v2.6` | `fb0d56ad0069c3f95b37493dcbcdf72a98c8c3ce` | completed 2026-09-25T02:58Z |
| 4 | `integration/final-report` | `628de2487f229112a342291d1f7ebe14488fad54` | brings analysis ≤`102320f`, reconciled decision IDs, Chapters 1–3, figures, references |
| 5 | `analysis/pipeline` | `7733bd48a26f50dedf3a1d9b75436bf6325be52e` | adds only `7733bd4` |

M1, M3 and M4 do not conflict on data; they touch disjoint `manual_raw` paths. Their order only affects how the two append-only logs are interleaved, so chronological order is used. Merge by pinned SHA so that exactly the verified content is merged.

---

## 6. Conflict forecast (Part 6)

These are pairwise results from `git merge-tree --write-tree`. **Only four documentation files conflict. No code, schema, test, manifest, state, data, report-draft or asset file conflicts.**

| Step | Conflicting files (hunks / conflict lines, pairwise estimate) | Authoritative side and resolution |
|---|---|---|
| 1 M3 | `docs/final_paper_notes.md` (1/51), `docs/research_progress_log.md` (1/107) | **Manual union.** Both are append-only logs. Keep every entry from both sides verbatim, in timestamp order, and rewrite nothing. |
| 2 M1 | same two files | same: union |
| 3 M4 | same two files | same: union |
| 4 integration/final-report | `docs/decision_log.md` (2/134) | **Take the integration/final-report side** (`git checkout --theirs`). It already contains all five source decisions from `feature/data-collection`, renumbered D038–D042 with `original_branch_decision_id` provenance. All five titles were verified as present. Afterwards, append any Phase-0 decision (see §9 B1/B2) using **D043 or higher**. |
| 4 | `docs/current_research_status.md` (2/75) | **Take the integration/final-report side as the base**, because it is v2.7-synchronised and uses integrated IDs. Then, in a separate post-merge commit, update it by hand to cover: manual collection complete (130), raw-evidence location, and the canonical worktree. Also remove its statement "v2.7 freeze records … are not present in this integration worktree". |
| 4 | `docs/final_paper_notes.md` (2/452), `docs/research_progress_log.md` (2/726) | **Manual union**, as above. Large because integration/final-report added about 40 commits of entries. |
| 5 analysis/pipeline | `docs/final_paper_notes.md` (1/235), `docs/research_progress_log.md` (2/473) | **Manual union.** `7733bd4` entries are dated 2026-09-24. Integration already contains the `102320f` entries, so drop only exact duplicates of text that is already present. |

**Auto-merged but semantically sensitive.** These merge without conflict but must pass tests after the merge:

- `scripts/collect_api_run.py` and `tests/test_api_collection.py` were changed on both fdc and integration/final-report. The trial merge has no duplicate definitions and no markers. Both sides implement the same D035-style abnormal-finish rule, as source D032/57e51f7 and integrated D035.
- `AGENTS.md` becomes the integration/final-report version, which says "integrated final-report worktree … live collection authoritative in `~/Dev/ai-hallucination-study`". It needs a wording update after the merge (researcher decision).
- `.analysis-repository-marker` and `scripts/repository_guard.py` enter the canonical branch. The guard blocks the legacy live-collection entry points, which is appropriate now that generation is complete. The new `collect_hybrid_*.py` scripts from fdc do **not** call the guard (researcher decision).
- The following are added cleanly and have no counterpart on the other sides: analysis scripts and schemas (PIPE-05B…PIPE-10), `docs/report_drafts/*` (Chapters 1–3), `docs/report_assets/figures/chapter3/created by me/*` (5 PNGs), `docs/references/approved_references.md`, and `docs/final_report_support/*`.
- `data/final/manual_raw/**`, the v2.7 config, manifest and state, and `hybrid_assignment` are added cleanly (fdc and manual-only).

---

## 7. Data safety (Part 7)

| Item | Carried by git merge? | Status |
|---|---|---|
| 130 manual observations (`data/final/manual_raw/v2.6.0/`) | **Yes** (tracked) | Safe |
| v2.7 frozen config, manifest, state, model set, schemas, prompts | **Yes** | Safe. The merge never rewrites tagged commits. |
| `v2.7.0-freeze` tag and commit `bba890d` | not touched by merge | Safe. Do not use `--force`, `tag -f` or rebase. |
| **140 retained API observations** (`data/final/raw/API-v2.6-*`) | **NO: `data/final/raw/*` is gitignored** | **BLOCKER B2**: they exist only on disk in `~/Dev/ai-hallucination-study` |
| M2 historical evidence (11 `API-v2.6-*-M2-*` dirs) | **NO**, same reason | BLOCKER B2 |
| Pre-v2.6 raw evidence (v2.1–v2.5, 78 dirs) | **NO**, same reason. `tests/test_api_freeze.py` needs it (2 failures in both worktrees that lack it). | BLOCKER B2 |
| v2.6 batch-state snapshot cited by v2.7 state | only after Phase-0 commit | **BLOCKER B1** |
| Analysis code, schemas, tests | Yes | Safe |
| Derived checkpoints (`data/derived_checkpoints/…`, analysis worktree) | **NO**: untracked, and only in `~/Dev/ai-hallucination-analysis` | Referenced by the progress log (entries at lines 712 and 722). See §8. |
| Quarantine evidence (`data/quarantine/accidental_v2.6_collection_2026-09-22/`) | **NO**: untracked, analysis worktree only | Required by `test_repository_guard.py::test_quarantine_evidence_is_untouched`. See §8. |
| Chapters 1–3, Chapter 3 figures, references, report support | Yes | Safe |
| Decision, progress and final-paper history | Yes, via merge commits and union resolution | Safe if resolved as described in §6 |

**Credential scan of the evidence that would need to be tracked:** no `sk-or-v1-…` or `gsk_…` patterns were found. Raw metadata records the value `"authorization_scheme": "Bearer (credential omitted)"`.

---

## 8. Dirty and untracked items (Part 8)

`.venv/`, `__pycache__/` and pytest caches are environment noise and are omitted.

| Worktree | Path | Classification | Reason |
|---|---|---|---|
| study (fdc) | `data/final/api_batch_state_v2.6.0.json` (M) | **MUST_CHECKPOINT** | Its bytes are the snapshot cited by the frozen v2.7 state (§3). Append-only diff. |
| study | `m4_all_web_prompts.txt` (untracked, 47,026 B) | TEMPORARY → SAFE_TO_DELETE_LATER | An operator helper export: 31 M4 manual prompts rendered for the web UI. It is derivable from the manifest and frozen prompts. Keep it until the post-merge validation passes. |
| study | `m4_manual_prompt_list.txt` (untracked, 1,677 B) | TEMPORARY → SAFE_TO_DELETE_LATER | CSV of the 31 M4 manual run IDs, derivable from the manifest. |
| study | `data/final/raw/**` (ignored, 229 dirs, ~48 MB) | **MUST_CHECKPOINT** (form is a RESEARCHER_DECISION, see B2) | The only copy of all API, M2 and historical raw evidence. |
| study | `data/pilot/raw/**` (ignored, 11 files) | KEEP_UNTRACKED | Pilot data, kept separate per rule 9. |
| study | `node_modules/` with `fake-auth@0.1.7` and `js-base64@2.6.4` (ignored), plus **tracked** `package.json` / `package-lock.json` (added in `5333f9e`, 2026-09-22) | **RESEARCHER_DECISION_REQUIRED** | An npm package was installed in the research repository and not documented in any decision log. `fake-auth` was not found in the raw experimental data by the quick search. Rules 5 and 6 need an explanation or a decision entry. Do not delete without a decision. |
| analysis | `data/derived_checkpoints/interim_val_01b_20260922T112234Z/` and `…_pipe05c-final-01/` (untracked, 2.6 MB, with SHA256SUMS) | **DERIVED_BUT_REQUIRED** | Referenced as "permanent" snapshots by the progress log. They contain v2.6-interim derived artifacts and copies of raw responses. Recommend a tracked checkpoint commit on `analysis/pipeline` before step 5, or carrying them into the canonical worktree. |
| analysis | `data/quarantine/accidental_v2.6_collection_2026-09-22/` (untracked, 164 KB) | **RESEARCHER_DECISION_REQUIRED** | Preserved incident evidence (D-record `fc02f0a`). The test expects it to exist *and* to stay untracked. Decide whether to track it or to keep it untracked in the canonical worktree. Never delete it. |
| analysis | `data/manual_review/pipe05b_…json`, `pipe05c_…json` (ignored) | DERIVED_BUT_REQUIRED | Adjudication inputs behind the pipe05b/05c result folders. They are interim v2.6, so preserve them. |
| analysis | `results/**` (ignored: v2.2.0 pipeline outputs, snapshots, pipe05b folders) | KEEP_UNTRACKED | Regenerable derived outputs; the v2.6-interim ones are non-final. |
| analysis | `node_modules/` (same `fake-auth`) and tracked `package.json` | RESEARCHER_DECISION_REQUIRED | Same issue as in the study worktree. |
| integration | only `__pycache__` | none | Clean |

---

## 9. Blockers before merge

**B1. Commit the v2.6 batch-state checkpoint on `feature/data-collection`.** This is a dedicated commit. After committing, verify that SHA-256 = `1a3af56d…b695c`.

**B2. Decide how the ignored raw evidence reaches the canonical worktree.** Without this, the canonical worktree has 0 of 140 API observations and no M2 or historical evidence. Options:

- **(A) Recommended: a dedicated evidence commit on `feature/data-collection`.** It narrowly un-ignores `data/final/raw/` and tracks all 229 directories byte-for-byte (~48 MB), with a `SHA256SUMS` file. This mirrors how manual evidence is already tracked. It needs a decision entry, **numbered D043 or higher** to avoid a new collision with the integrated IDs, because it changes the original ".gitignore: track structure, not collected records" policy.
- **(B)** Leave the data untracked and point the analysis at `--raw-root ~/Dev/ai-hallucination-study/data/final/raw`. The drawback: the tests that hard-code `ROOT/data/final/raw` still fail.
- **(C)** Symlink the ignored `data/final/raw` into the new worktree. It is cheap, but the evidence stays unversioned.

**B3. Reconcile the analysis-repository guard tests with a data-bearing canonical branch (researcher decision).**

- `test_raw_final_contains_no_active_v2_6_run_directories` asserts that there are **no** `API-v2.6-*` directories. It will fail as soon as the raw evidence is present, which it must be for the final analysis.
- `test_quarantine_evidence_is_untouched` needs the quarantine directory.
- The fix is a documented post-merge test adjustment, not a data change.

**B4. Back up the local-only branches (strongly recommended).** Push `feature/data-collection` (5 unpushed v2.7 commits, including the freeze commit), `analysis/pipeline` and `integration/final-report`, together with the `v2.7.0-freeze` tag. Outward-facing, so the researcher decides.

**B5. Preserve `data/derived_checkpoints/` and the quarantine directory (§8)** before any worktree clean-up, and decide how they are carried.

**Not merge blockers, but required before Chapters 4–6:**

- The analysis scripts are **not v2.7-aware**. `build_response_inventory.py` defaults to the v2.2 manifest, and no script reads `data/final/manual_raw/` or `collection_state_v2.7.0.json`. Extending the pipeline to the 270-row v2.7 cohort (140 API + 130 manual) is post-consolidation work.
- A derived v2.7 final collection-state record for the manual rows is needed (§3).
- The pre-freeze manual captures need disclosure (§2).
- `fake-auth` needs a decision (§8).
- `AGENTS.md` needs a wording update.
- The guard needs coverage for `collect_hybrid_*.py`.

---

## 10. Commands to run later, after the blockers are resolved

Nothing below was executed.

```bash
# ---- Phase 0: provenance checkpoints on feature/data-collection (researcher-approved) ----
cd ~/Dev/ai-hallucination-study
sha256sum data/final/api_batch_state_v2.6.0.json   # expect 1a3af56d138d3da1c3e67c1f04f55b27e4ab5d0ec786ab31d7c2cd17cb6b695c
git add data/final/api_batch_state_v2.6.0.json
git commit -m "data: checkpoint v2.6 batch-state snapshot cited by v2.7 collection state"
# B2 option A (only if approved; record decision D043+ first):
#   narrow .gitignore exception for data/final/raw/, generate data/final/raw/SHA256SUMS,
#   git add data/final/raw && git commit -m "data: track preserved raw API evidence (v2.x incl. M2)"
# B5 (on analysis/pipeline, if approved): commit data/derived_checkpoints/ as a derived-evidence checkpoint;
#   if so, re-pin step 5 below to the new analysis/pipeline SHA.

# ---- Phase 1: canonical worktree/branch ----
git fetch origin --prune --tags
git rev-parse 'v2.7.0-freeze^{commit}'             # must print bba890d9aa5838f06bee4b1bd0e85d9e61b444f8
git worktree add -b integration/v2.7-final ~/Dev/ai-hallucination-final feature/data-collection
cd ~/Dev/ai-hallucination-final

# ---- Phase 2: merges (resolve per §6; after each: verify, then `git commit` to conclude) ----
git merge --no-ff ee952dca123a7eda1e7ea5e8c7f9518ed2e70608 \
  -m "merge: collection/m3-manual-v2.6 (49 manual M3 observations) into integration/v2.7-final"
#   conflicts: docs/final_paper_notes.md docs/research_progress_log.md -> union, then:
#   git add docs/final_paper_notes.md docs/research_progress_log.md && git commit --no-edit
git merge --no-ff 1e062808dd26462b8afca2967aebc102eff066bf \
  -m "merge: collection/m1-manual-v2.6 (50 manual M1 observations) into integration/v2.7-final"
git merge --no-ff fb0d56ad0069c3f95b37493dcbcdf72a98c8c3ce \
  -m "merge: collection/m4-manual-v2.6 (31 manual M4 observations) into integration/v2.7-final"
git merge --no-ff 628de2487f229112a342291d1f7ebe14488fad54 \
  -m "merge: integration/final-report (analysis ≤102320f, Chapters 1–3, reconciled decision IDs)"
#   git checkout --theirs docs/decision_log.md docs/current_research_status.md
#   union-resolve docs/final_paper_notes.md docs/research_progress_log.md
#   git add … && git commit --no-edit
git merge --no-ff 7733bd48a26f50dedf3a1d9b75436bf6325be52e \
  -m "merge: analysis/pipeline (7733bd4 zero-event Fisher fix)"

# ---- Phase 3: separate post-merge reconciliation commits (not inside merge commits) ----
#   docs/current_research_status.md, AGENTS.md wording, guard tests (B3),
#   derived v2.7 final collection-state record, decision entries D043+.
```

Do **not** use `-X ours`, `-X theirs` or `--strategy-option` on whole merges. Resolve per file only.

---

## 11. Post-merge validation (Part 9)

Run these in `~/Dev/ai-hallucination-final`. Every step must pass.

```bash
cd ~/Dev/ai-hallucination-final

# 1. Manual evidence 50+49+31 = 130, and 4. no duplicates, plus the manual-evidence part of 5
python3 - <<'EOF'
import csv, json, hashlib, pathlib, collections
man = {r['run_id']: r for r in csv.DictReader(open('manifests/api_final_v2.7.0_manifest.csv'))}
root = pathlib.Path('data/final/manual_raw/v2.6.0')
runs = [p.name for p in root.iterdir() if p.is_dir()]
c = collections.Counter(man[r]['model_condition_id'] for r in runs)
assert len(runs) == len(set(runs)) == 130 and c == {'M1': 50, 'M3': 49, 'M4': 31}, c
assert set(runs) == {k for k, r in man.items() if r['collection_interface'] == 'manual'}
for r in runs:
    d = root / r
    assert sorted(p.name for p in d.iterdir()) == ['metadata.json', 'prompt.txt', 'response.md'], r
    m = json.loads((d / 'metadata.json').read_text())
    assert hashlib.sha256((d / 'response.md').read_bytes()).hexdigest() == m['raw_response_sha256'], r
    assert hashlib.sha256((d / 'prompt.txt').read_bytes()).hexdigest() == man[r]['expected_prompt_sha256'], r
print('manual OK', dict(c))
EOF
for s in ee952dca123a7eda1e7ea5e8c7f9518ed2e70608 1e062808dd26462b8afca2967aebc102eff066bf fb0d56ad0069c3f95b37493dcbcdf72a98c8c3ce; do
  test -z "$(git diff --diff-filter=MDR --name-only $s HEAD -- data/final/manual_raw)" && echo "$s manual_raw unaltered"; done

# 2. Manifest: 270 rows, 90 per model, 45 per category, M2 = 0
python3 - <<'EOF'
import csv, collections
r = list(csv.DictReader(open('manifests/api_final_v2.7.0_manifest.csv')))
m = collections.Counter(x['model_condition_id'] for x in r); c = collections.Counter(x['category'] for x in r)
assert len(r) == 270 and len({x['run_id'] for x in r}) == 270
assert m == {'M1': 90, 'M3': 90, 'M4': 90} and set(c.values()) == {45} and len(c) == 6 and 'M2' not in m
print('manifest OK')
EOF

# 3. v2.7 freeze unchanged
test "$(git rev-parse 'v2.7.0-freeze^{commit}')" = bba890d9aa5838f06bee4b1bd0e85d9e61b444f8
git merge-base --is-ancestor bba890d9aa5838f06bee4b1bd0e85d9e61b444f8 HEAD
python3 - <<'EOF'
import json, hashlib, subprocess
d = json.load(open('config/experiment_freeze_v2.7.0.json'))
items = [d[k] for k in ('official_manifest', 'model_set', 'prompt_template', 'task_set', 'initial_collection_state')] + d['rendered_prompts'] + d['schemas']
bad = [i['path'] for i in items if hashlib.sha256(open(i['path'], 'rb').read()).hexdigest() != i['sha256']]
tag = subprocess.run(['git', 'show', 'v2.7.0-freeze:config/experiment_freeze_v2.7.0.json'], capture_output=True, check=True).stdout
assert not bad and tag == open('config/experiment_freeze_v2.7.0.json', 'rb').read(), bad
print('freeze OK', len(items), 'items')
EOF
sha256sum data/final/api_batch_state_v2.6.0.json   # 1a3af56d…b695c

# 5. Every v2.7 row has final evidence/state (API part; the manual part is in step 1)
python3 - <<'EOF'
import json, hashlib, os
s = json.load(open('data/final/collection_state_v2.7.0.json'))
h = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
api = [r for r in s['rows'] if r['collection_interface'] == 'api']
assert len(api) == 140 and all(r['status'] in ('completed', 'truncated', 'failed') for r in api)
for r in api:
    e = r['evidence']; p = e['path']
    assert h(p + '/metadata.json') == e['metadata_sha256'] and h(p + '/prompt.txt') == e['prompt_sha256'], r['run_id']
    if e['response_sha256']: assert h(p + '/response.md') == e['response_sha256'], r['run_id']
m2 = [x for x in os.listdir('data/final/raw') if x.startswith('API-v2.6-') and '-M2-' in x]
assert len(m2) == 11, m2
print('API evidence OK; M2 historical dirs:', len(m2))
EOF

# 6. Analysis-pipeline tests
python3 -m unittest tests.test_adjudicate_review_required_packages tests.test_analyze_group_comparisons \
  tests.test_build_analysis_dataset tests.test_calculate_dependency_reliability_metrics \
  tests.test_calculate_primary_metrics tests.test_score_risk_findings tests.test_extract_package_references \
  tests.test_response_inventory -v
# 7. Full suite (baseline counts: fdc 164 OK; analysis 339 (2 fail, raw absent); integration 333 (3 fail, raw/quarantine absent))
python3 -m unittest discover -s tests

# 8. No conflict markers or unmerged paths
test -z "$(git diff --name-only --diff-filter=U)"
! git grep -nE '^(<<<<<<<|>>>>>>>)( |$)' -- . ':!*.bin'

# 9 and 10. Chapters 1–3 and assets preserved byte-for-byte from integration/final-report
test -z "$(git diff --name-only 628de2487f229112a342291d1f7ebe14488fad54 HEAD -- docs/report_drafts docs/report_assets docs/references docs/final_report_support)"
ls docs/report_drafts/chapter{1,2,3}_complete_draft.md
grep -c 'v2.7' docs/report_drafts/chapter3_complete_draft.md

# 11. Status/progress/final-paper docs reconciled
grep -n 'D039\|D040\|D041\|D042' docs/decision_log.md | head
grep -niE 'manual.*pending|not present in this integration worktree' docs/current_research_status.md   # expect no stale hits after Phase 3

# 12. Clean state
git status --porcelain            # expect empty (ignored .venv/__pycache__/raw-if-untracked excluded)
```

---

## 12. Go/no-go

**NO-GO for executing the merges now.** The five merges themselves are low-risk: only four documentation files conflict, the resolution rules are clear, and no data, code or frozen file conflicts. The consolidated tree, however, would currently **lack all 140 API observations, the M2 historical evidence and the cited v2.6 state snapshot**, and would fail the repository's own freeze and guard tests.

**It becomes GO once:**

1. B1 is committed.
2. B2 is decided and implemented.
3. B3 is decided.
4. B4 backups are pushed (recommended).
5. B5 evidence is preserved.

At that point, use the §10 commands in the §5 order, followed by all §11 checks.
