# Final v2.7 Evidence Consolidation — Verification

**Task:** FINAL-V2.7-EVIDENCE-CONSOLIDATION-VALIDATION-01
**Date (UTC):** 2026-09-25
**Worktree / branch:** `~/Dev/ai-hallucination-final`, `integration/v2.7-final` (verified at HEAD `da11ae42644dacbe67ba5a7c0ef2b4deedb29f89`)
**Nature:** a read-only verification of consolidated evidence. No research results. No frozen input, raw response, manual evidence, quarantine item, or checkpoint was modified. Nothing was installed, npm was not run, and nothing was pushed.

## 1. Summary

| Check | Result |
|---|---|
| Raw API evidence: 1,552 files verified against the inventory | PASS |
| Raw inventory SHA-256 `1f79cdec…a75634e7` | MATCH |
| Raw evidence tracked by Git | NO (only `data/final/raw/.gitkeep`) |
| `data/derived_checkpoints/` preserved | PASS (byte-identical) |
| `data/quarantine/` preserved | PASS (byte-identical) |
| `data/manual_review/` preserved | PASS (byte-identical) |
| Manual evidence: 130 rows (M1 50, M3 49, M4 31) complete and hash-consistent | PASS |
| Derived final-collection completion record created | YES |
| `create_experiment_freeze_v2_7.py --check` | **FAIL** (expected; the guard is not snapshot-aware, §5.1) |
| `create_experiment_freeze_v2_6.py --check` | PASS |
| `create_hybrid_assignment_v1_0.py --verify` | PASS |
| `v2.7.0-freeze` → `bba890d9aa5838f06bee4b1bd0e85d9e61b444f8` | UNCHANGED |
| Frozen hashes (43 pairs in the v2.7 freeze record) | 43 match, 0 mismatch, 0 missing |
| Full test suite | 370 run, 369 passed, 1 failed, 0 errors, 0 skipped |

## 2. Raw API evidence (D043)

- Source: `~/Dev/ai-hallucination-study/data/final/raw/`.
- Destination: `~/Dev/ai-hallucination-final/data/final/raw/`.
- Inventory: `reports/final_v2.7_raw_evidence_inventory.sha256`. Its SHA-256 is `1f79cdecbd573b57f5121dc04fcd5e3aadcca8d46d005cebf4628a8fa75634e7`, the expected value. It has 1,552 lines.
- `sha256sum -c --quiet reports/final_v2.7_raw_evidence_inventory.sha256` passed in the destination and also passed in the source.
- The destination has 1,552 regular files, and none of them are outside the inventory.
- Git status of the raw evidence: `git ls-files data/final/raw` lists only `.gitkeep`. The rule `.gitignore:35 data/final/raw/*` ignores everything else.

## 3. Analysis-local artifacts

Each directory was compared with `~/Dev/ai-hallucination-analysis/` (branch `analysis/pipeline` @ `7733bd48a26f50dedf3a1d9b75436bf6325be52e`) in two ways: `diff -r --no-dereference`, and a deterministic inventory digest (`LC_ALL=C find <dir> -type f -print0 | LC_ALL=C sort -z | xargs -0 sha256sum | sha256sum`).

| Directory | Files (analysis / final) | Non-regular entries | Inventory digest (identical in both) | `diff -r` | Git status in final worktree |
|---|---:|---:|---|---|---|
| `data/derived_checkpoints/` | 24 / 24 | 0 | `93a2c849a9daec7efe3c4918f92b7a04dd60462342d35569d5667a782a63e7c0` | identical | untracked |
| `data/quarantine/` | 12 / 12 | 0 | `03add83160acaa9172857dac4f7b77414555c32aa6c2a296d3e6d5e25a5eb68c` | identical | untracked |
| `data/manual_review/` | 3 / 3 | 0 | `1bd61d623978010f5f2a606fc2508589cdf0050bc4268dda5b0adcd158f7bd9d` | identical | `.gitkeep` tracked; 2 JSON files ignored (`.gitignore:43`) |

The embedded checksum files were also checked:

- `data/derived_checkpoints/interim_val_01b_20260922T112234Z/SHA256SUMS`: PASS.
- `data/derived_checkpoints/interim_val_01b_20260922T112234Z_pipe05c-final-01/SHA256SUMS`: PASS.
- `data/quarantine/accidental_v2.6_collection_2026-09-22/SHA256SUMS.txt` uses repository-root paths. Its 11 content entries pass. The 12th entry lists the checksum file itself, which cannot match by construction; the file is byte-identical to the analysis copy.

These directories are preserved as they are. Quarantine contents stay preservation material and are **not** final-study evidence. Checkpoints and adjudication inputs remain interim v2.6 material unless the approved workflow later promotes them. None of these directories was committed by this task.

## 4. Final collection state and derived record

- Frozen initial state: `data/final/collection_state_v2.7.0.json`. It is unchanged, with SHA-256 `55a32c0d4a7c6ae493ca701be2dea11995792a09bdb4a9fb8f3024ca073709a6`, which matches the freeze record. It records 105 completed, 16 truncated, 19 failed, and 130 pending (manual).
- Manual evidence (`data/final/manual_raw/v2.6.0/`, tracked):
  - 130 run directories: M1 50, M3 49, M4 31.
  - Each one is a `collection_interface=manual` row of the v2.7 manifest, and no manual row is missing.
  - All prompt hashes equal `expected_prompt_sha256`.
  - All `response.md` hashes equal `raw_response_sha256`.
  - All rows have `response_status=completed`, and `actual_model` equals `expected_model_id` in every row.
  - The manual branch commits `1e06280`, `ee952dc`, and `fb0d56a` are ancestors of HEAD, and so is the provenance checkpoint `2f50255`.
- Manifest: 270 rows (API 140, manual 130; M2 0).
- Derived record, non-frozen and append-only:
  - `reports/final_collection_completion_v2.7.0.json`, SHA-256 `ec7dfe5e0d4f32e82b31f727a4148a709e5f33f05325648ff6b8dd477988d036`.
  - `reports/final_collection_completion_v2.7.0.md`.
  - Final observed state: API 105 completed, 16 truncated, 19 failed, 0 pending; manual 130 completed; 0 pending overall.
  - Transition since freeze: exactly the 130 manual rows, `pending` → `completed`. No API row changed.
- **Path deviation.** The task suggested `results/final_collection_completion_v2.7.0.json`. However, `results/*` is gitignored by repository policy (`.gitignore:26`), so a file there could not be committed without `git add -f` or a policy change. The JSON therefore sits next to the other tracked D043 provenance records in `reports/`.

## 5. Freeze and assignment checks

### 5.1 `python3 scripts/create_experiment_freeze_v2_7.py --check` — FAIL (expected, not an integrity defect)

Output: `FAIL: v2.7 collection state no longer matches preserved evidence`.

Cause: `--check` re-derives the collection state from the evidence currently on disk and requires it to equal the frozen initial snapshot (script lines 480–483). The frozen snapshot records the 130 manual rows as `pending`, because the freeze commit `bba890d` holds no `data/final/manual_raw/` files (`git ls-tree` shows 0). Once the manual branches are merged, the re-derivation reports those rows as `completed`, and the equality can no longer hold. The check was written for the pre-completion state and has no mode that allows later, append-only completion.

The failure was isolated as follows, without modifying the script or any frozen file:

1. **Every other `--check` step passes against the real worktree** (run in memory):
   - the model set matches its rebuild;
   - the frozen state's SHA-256 matches the freeze record;
   - 11/11 preserved M2 evidence entries match;
   - the rebuilt freeze record equals `config/experiment_freeze_v2.7.0.json`;
   - `docs/experiment_freeze_v2.7.0.md` matches its renderer.
2. **Frozen state against re-derived state:**
   - The only differences are `status_counts`, `status_counts_by_model`, and 130 manual rows (M1 50, M3 49, M4 31) that changed from `pending` to `completed`.
   - None of the 140 API rows differ.
3. **Control run:** the unmodified `--check` was run on a scratch `git archive HEAD` export that held the verified raw evidence.
   - With the manual evidence present, it gave the same FAIL.
   - With `data/final/manual_raw/v2.6.0/` removed from the scratch copy only, which is the freeze-time evidence set, it gave `PASS: verified v2.7 freeze, model set, 270-row manifest, collection state, v2.6 sources, and preserved M2 evidence`.

Classification: **B — obsolete v2.7 guard assumption.** The frozen script is itself hash-listed in the freeze record, so it must not be edited. §8 gives the recommended remedy.

### 5.2 Other checks

- `python3 scripts/create_experiment_freeze_v2_6.py --check` → `PASS: verified v2.6 freeze JSON, Markdown, hashes, prompts, manifest, state, and zero raw observations`.
- `python3 scripts/create_hybrid_assignment_v1_0.py --verify` → `PASS: verified hybrid assignment, report, quotas, preserved raw observations, order, and manifest hash`. This check failed before the raw copy (`docs/final_v2.7_tracked_branch_merge_verification.md` §7) and now passes.

### 5.3 Freeze tag and frozen hashes

- `git rev-parse v2.7.0-freeze^{commit}` → `bba890d9aa5838f06bee4b1bd0e85d9e61b444f8`.
- Recursive recomputation of every `path`/`sha256` pair in `config/experiment_freeze_v2.7.0.json` gave 43 pairs: 43 match, 0 mismatch, 0 missing.
- `git diff bba890d HEAD` is empty for all of the following: the v2.7 model set, freeze JSON and Markdown, collection state, manifest, schema, freeze script, `prompts/`, `data/generated_prompts/`, the v2.6 freeze JSON, model set 1.4.0, and `manifests/hybrid_assignment_v1.0.0.csv`.
- Key hashes:
  - `config/experiment_freeze_v2.7.0.json`: `f6fbb15192dee3d5744bc15890c0df81615e3c70ea76a41d9dbfbe7cb27bcfc5`
  - `config/experiment_freeze_v2.6.0.json`: `53736d8a38fb4f497fc525cff7453693cd2ed0154b0c55a14172ea39164d5719`
  - manifest: `2edf2638f08a1079aadd02c174951a912aa2797b56df36997878096b29a4ed20`
  - collection state: `55a32c0d4a7c6ae493ca701be2dea11995792a09bdb4a9fb8f3024ca073709a6`

## 6. Full test suite

Command: `python3 -m unittest discover -s tests`, the documented command, run with system Python 3.14.7. The repository has no virtualenv or pytest configuration.

**Result: 370 run, 369 passed, 1 failed, 0 errors, 0 skipped.**

| Stage | Tests | Failures | Errors |
|---|---:|---:|---:|
| Before the raw copy (`docs/final_v2.7_tracked_branch_merge_verification.md` §8) | 370 | 6 | 143 |
| Now | 370 | 1 | 0 |

- `test_repository_guard.RepositoryStateUnchangedTests.test_quarantine_evidence_is_untouched` now **passes**, as expected, because `data/quarantine/` is preserved.
- The remaining failure is `test_repository_guard.RepositoryStateUnchangedTests.test_raw_final_contains_no_active_v2_6_run_directories` (`tests/test_repository_guard.py:352`).
  - It asserts that `data/final/raw/API-v2.6-*` is empty.
  - It finds 151 directories: the 140 retained v2.7 API observations and the 11 preserved historical M2 directories.
  - The test came from the analysis repository (`fa01ad4`, "Block live collection in analysis repository"). There, raw v2.6 evidence was never meant to exist, because the test guarded against a repeat of the accidental collection now held in `data/quarantine/accidental_v2.6_collection_2026-09-22/`.
  - In the canonical final worktree these directories are the required D043 evidence.
  - Classification: **B — obsolete v2.6/v2.7 guard assumption** (with D, a stale analysis-worktree assumption). It is not an implementation defect, and the test was not changed.
- The suite did not change the worktree. `git status` afterwards showed only the pre-existing untracked directories, and the raw inventory still passed.

## 7. Stale integration text and guards (audit only; nothing changed)

| Location | Stale statement | Why it is stale |
|---|---|---|
| `AGENTS.md` §Purpose | "This is the integrated final-report/research worktree, not a live data-collection worktree. Live v2.6 collection remains authoritative in `~/Dev/ai-hallucination-study`. Do not attempt live collection here." | This is now the canonical final worktree, holding all v2.7 evidence. Collection is complete everywhere, and v2.6 is historical. |
| `AGENTS.md` §Worktree Safety | "Do not run live collection from this worktree; the repository guard and `~/Dev/ai-hallucination-study` remain the authoritative collection boundary." | Same reason. No collection is authorised in any worktree now. |
| `.analysis-repository-marker` (tracked) | "marks this repository as the AI HALLUCINATION ANALYSIS workspace … Official experimental data collection is performed exclusively in ~/Dev/ai-hallucination-study." | This worktree is the canonical final repository, not only the analysis workspace. |
| `scripts/repository_guard.py` docstring and `REFUSAL_MESSAGE` | "This repository is a derived-analysis workspace only…", "Use ~/Dev/ai-hallucination-study." | The refusal redirects users to a worktree where collection is also complete. |
| `scripts/collect_hybrid_api_batch.py`, `scripts/collect_hybrid_manual.py` | Neither calls `assert_live_collection_allowed()`. | These are the v2.6/v2.7 collectors, and they are unguarded in the canonical worktree (already flagged in `docs/final_v2.7_tracked_branch_merge_verification.md` §9 item 4). |
| `tests/test_repository_guard.py:352` | Asserts no `API-v2.6-*` raw directories. | See §6. |
| `docs/current_research_status.md` (header and D043 paragraph) | "raw-evidence copy pending"; "Manual completion will be recorded in a separate … derived record after consolidation". | Both are now done. |
| `docs/decision_log.md` D043 `status` | "byte-for-byte copy into the canonical final worktree pending consolidation" | The copy is done and reverified. |

## 8. Recommended later changes (require researcher approval; not applied)

1. **`AGENTS.md` §Purpose.** Replace the first paragraph with:
   > This is the canonical final v2.7 worktree (`integration/v2.7-final`). It holds all final-study evidence: gitignored raw API evidence verified against `reports/final_v2.7_raw_evidence_inventory.sha256` (D043), tracked manual evidence under `data/final/manual_raw/v2.6.0/`, and preserved analysis-local material. Final v2.7 data collection is complete (270/270). No further data collection is authorised in any worktree; `~/Dev/ai-hallucination-study` is retained only as the historical collection origin.
2. **`AGENTS.md` §Worktree Safety.** Replace the last line with: "Do not run live collection from this or any worktree; final collection is complete. The repository guard remains in force."
3. **Guard coverage.** Keep `.analysis-repository-marker`, since the guard's function stays correct, and reword its text and `REFUSAL_MESSAGE` to "Live data collection is disabled: final v2.7 collection is complete." Add `assert_live_collection_allowed()` as the first action of `collect_hybrid_api_batch.py` and `collect_hybrid_manual.py` `main()`, and extend `CLIRefusalTests.test_every_api_live_collection_entry_point_refuses` to cover them. This is a code change to collection tooling, not to experimental inputs. It needs a decision-log entry.
4. **`test_raw_final_contains_no_active_v2_6_run_directories`.** Replace it with a documented assertion that `data/final/raw/API-v2.6-*` is exactly the D043-inventoried set (verify the inventory, and assert that no `API-v2.7-*` directory exists). Record the change as a documented guard-test adjustment.
5. **v2.7 freeze check.** Do not edit the frozen `create_experiment_freeze_v2_7.py`. Add a separate, non-frozen verifier (for example `scripts/verify_final_collection_completion_v2_7.py --check`). It would run every `--check` step except the live-state equality, then confirm that re-derived rows equal the frozen snapshot for all API rows, that they equal `reports/final_collection_completion_v2.7.0.json` for all rows, and that the only transitions are manual `pending → completed`.
6. **Status and decision text.** Update `docs/current_research_status.md` and the D043 `status` field to record that the copy and reverification are complete (by an appended note, not a historical rewrite).

## 9. Upstream

- `integration/v2.7-final` still tracks `origin/feature/data-collection`. It is 55 commits ahead and 0 behind.
- `origin/integration/v2.7-final` does not exist, and nothing was pushed.
- After the researcher accepts this verification, create the remote branch and set it as upstream with:

  ```bash
  git push -u origin integration/v2.7-final:integration/v2.7-final
  ```

  Use the explicit refspec. Until then, avoid a bare `git push`: the current upstream is `feature/data-collection`, and this branch must not update that ref.

## 10. Readiness

The evidence consolidation is verified:

- raw, manual, and analysis-local evidence are complete and byte-verified;
- frozen inputs are unchanged;
- the hybrid-assignment and v2.6 checks pass.

The one failing freeze check and the one failing test are both explained guard assumptions (class B), not evidence or implementation defects. **Recommendation: READY_FOR_ANALYSIS_ADAPTATION**, with §8 items 4 and 5 done early in adaptation so that the v2.7 integrity checks report PASS in the canonical worktree. All final results remain `[FINAL RESULT PENDING]`.
