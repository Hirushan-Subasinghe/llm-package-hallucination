# Final v2.7 Canonical Worktree — Verification Guards Validation

**Task:** FINAL-V2.7-CANONICAL-WORKTREE-CLEANUP-01
**Date (UTC):** 2026-09-25
**Worktree / branch:** `~/Dev/ai-hallucination-final`, `integration/v2.7-final` (starting HEAD `dd8ef46`)
**Decision:** D045
**Nature:** integrity tooling, guard, and documentation changes. No research results. No frozen input, generation setting, raw or manual response, collection state, or evidence inventory was modified. Nothing was installed, no model or registry was called, and nothing was pushed.

## 1. Summary

| Check | Result |
|---|---|
| FINAL_COMPLETION_CHECK: `python3 scripts/verify_final_collection_v2_7.py` | **PASS** |
| FROZEN_SNAPSHOT_CHECK: `python3 scripts/create_experiment_freeze_v2_7.py --check` | **FAIL** (expected, §2) |
| `python3 scripts/create_hybrid_assignment_v1_0.py --verify` | PASS |
| `python3 scripts/create_experiment_freeze_v2_6.py --check` (historical) | PASS |
| `sha256sum -c --quiet reports/final_v2.7_raw_evidence_inventory.sha256` | PASS |
| Full suite: `python3 -m unittest discover -s tests` | 413 run, 413 passed, 0 failed, 0 errors |
| Frozen script `create_experiment_freeze_v2_7.py` | unchanged, `6318922a…d72c370c` |
| Frozen state `data/final/collection_state_v2.7.0.json` | unchanged, `55a32c0d…3709a6` |
| `git diff bba890d` over config, manifests, prompts, generated prompts, schemas, frozen state and script | empty |

## 2. Why the frozen v2.7 check no longer matches the final evidence

- `create_experiment_freeze_v2_7.py --check` re-derives the collection state from the evidence on disk. It then requires that re-derivation to equal the frozen `data/final/collection_state_v2.7.0.json`.
- The frozen state is the prospective snapshot taken at freeze (`2026-09-24T23:22:58.369305Z`). No manual evidence was in the freeze commit, so the snapshot records all 130 manual rows as `pending`.
- All 130 manual rows are now complete, so the live re-derivation records them as `completed`. The check fails with `v2.7 collection state no longer matches preserved evidence`. All its earlier steps pass.
- This failure does not mean the evidence or the implementation is defective. It is how a snapshot-equality check behaves once post-freeze evidence exists.

### Why the frozen script and state were not edited

Both are frozen experiment artifacts: they are hash-listed in, or referenced by, the v2.7 freeze record and tag `v2.7.0-freeze`. Editing either would change frozen evidence after the fact. It would also make the freeze record unverifiable. The two checks are therefore kept apart:

| Check | Command | Verifies | Expected now |
|---|---|---|---|
| FROZEN_SNAPSHOT_CHECK | `create_experiment_freeze_v2_7.py --check` (frozen) | The freeze-time snapshot equals a live re-derivation | FAIL after completion |
| FINAL_COMPLETION_CHECK | `verify_final_collection_v2_7.py` (new, non-frozen) | The completed state, the frozen hashes, and the transitions since the freeze | PASS |

The dissertation must not claim that the original freeze check passes unchanged after evidence completion. `docs/final_paper_notes.md` (2026-09-25, "Frozen initial collection state versus derived final completion record") already records this.

## 3. New verifier: `scripts/verify_final_collection_v2_7.py`

- The verifier is read-only and has no options. It imports the frozen script's pure helpers unchanged (`final_study_rows`, `validate_manifest_rows`, `validate_model_set`, `build_manifest_rows`, `derive_collection_state`, `verify_sources`). It writes nothing and makes no network call.
- It exits 0 and prints `FINAL_COMPLETION_CHECK: PASS` only if every check holds. Otherwise it exits 1 with `FINAL_COMPLETION_CHECK: FAIL: <reason>`.

| # | Check | Observed |
|---:|---|---|
| 1–4 | The manifest is the deterministic v2.6-minus-M2 filter with 270 unique rows. The model set is exactly M1, M3, M4, with 90 rows each and 0 M2 rows. | PASS |
| 5 | Interface assignment: API 140, manual 130. | PASS |
| 6 | API statuses: completed 105, truncated 16, failed 19, pending 0. | PASS |
| 7 | Manual completed: M1 50, M3 49, M4 31 (130). No manual row is in any other status. | PASS |
| — | Transitions from the frozen snapshot: every API row equals its frozen entry exactly, including its evidence hashes. The only other change is manual `pending` → `completed` (130). | PASS |
| 8 | Manual evidence: the directory set equals the 130 manual rows. For each row, the `prompt.txt` SHA-256 equals the manifest's `expected_prompt_sha256`, and the `response.md` SHA-256 equals the metadata `raw_response_sha256` and the derived-record hash. | 130 verified |
| 9–10 | The D043 inventory SHA-256 is `1f79cdec…a75634e7` and it lists 1,552 files. Each file hash matches, no raw file is outside the inventory, and there are no symbolic links. | 1,552 verified |
| — | Raw directory classification (§4). | 140 final API, 11 historical M2, 78 earlier-version historical |
| 11 | `v2.7.0-freeze^{commit}` = `bba890d9aa5838f06bee4b1bd0e85d9e61b444f8`. | PASS |
| 12 | All 43 `path`/`sha256` pairs in the v2.7 freeze record match. The freeze record (`f6fbb151…`), the frozen script (`6318922a…`), and the v2.6 source hashes match. `git diff --quiet` against the freeze commit is empty for all 46 frozen paths. | PASS |
| 13 | The derived record `reports/final_collection_completion_v2.7.0.json` matches the live derivation for every row's status and evidence hashes. It also matches the frozen initial status, all totals and transitions, the freeze, inventory and script references, and the JSON SHA-256 stated in its Markdown. | PASS |
| 14 | Collection status is not treated as eligibility (§5). | PASS |

`tests/test_verify_final_collection_v2_7.py` adds 40 deterministic tests.

- Synthetic fixtures in temporary directories cover each failure mode:
  - an M2 row, a missing row, or an M2 model;
  - pending or unknown API statuses, and a pending manual row;
  - an API status or evidence change since the freeze, or a changed row set;
  - altered manual prompt or response bytes, or an extra manual directory;
  - an inventory hash mismatch, or a modified, unlisted, or missing raw file;
  - an unexpected `API-v2.6-*` or `API-v2.7-*` directory, a raw API directory for a manual row, or a missing M2 directory;
  - frozen-hash drift;
  - an eligibility claim, or a changed status or hash in the derived record.
- Integration tests run the CLI against the real evidence. They confirm three things:
  - the CLI passes and leaves `git status --porcelain --ignored` unchanged;
  - the frozen script and state are unchanged;
  - the frozen snapshot check still fails, and only with the documented message.

## 4. Obsolete raw-directory test corrected

- **Previous test:** `RepositoryStateUnchangedTests.test_raw_final_contains_no_active_v2_6_run_directories` (`tests/test_repository_guard.py`) asserted that `data/final/raw/API-v2.6-*` was empty.
- **Why it was valid before:** it came from the former analysis repository. There, raw v2.6 evidence was never meant to exist, and the test guarded against a repeat of the accidental collection now held in `data/quarantine/accidental_v2.6_collection_2026-09-22/`.
- **Why it became invalid:**
  - After consolidation (D043), this worktree must hold the raw evidence.
  - The 140 retained v2.7 API observations keep their historical `API-v2.6-*` run IDs.
  - The 11 M2 directories are preserved as historical evidence.
  - The test therefore failed on 151 required directories. Deleting or renaming evidence to satisfy it would violate the frozen-evidence rules.
- **Replacement:** `test_raw_final_directories_are_exactly_final_or_historical_evidence` uses the verifier's `classify_raw_directories` and asserts the following:
  - every one of the 140 API-assigned v2.7 rows has its historical v2.6 evidence directory;
  - the 11 M2 directories match the frozen M2 evidence inventory exactly and are disjoint from the v2.7 manifest;
  - no other `API-v2.6-*`, any `API-v2.7-*`, or any raw API directory for a manual-assigned row exists;
  - all remaining directories are earlier-version historical evidence, disjoint from the manifest.
- **New companion test:** `test_evidence_preservation_does_not_imply_analytical_eligibility` asserts that the 35 truncated or failed rows and all M2 run IDs are never primary candidates.

## 5. Collection status is not analysis eligibility

- The verifier checks that the frozen `truncation_policy` and `failure_policy` both set `exclude_from_primary_shr_phr_denominators: true`. It reports the truncated (16) and failed (19) rows as excluded by frozen policy.
- The 235 rows with collection status `completed` are reported only as candidates. Primary eligibility is decided downstream, including the D035 finish-reason overlay, not by this verifier.
- The verifier requires the derived record's `primary_analysis_eligibility.determined_by_this_record` to be `false`.

## 6. Canonical worktree guard changes

| File | Change |
|---|---|
| `AGENTS.md` §Purpose, §Worktree Safety | Now names this worktree and branch as the canonical location for the final v2.7 evidence, analysis, report drafting, and dissertation work. States that final collection is complete, that no collection is authorised in any worktree, and that `~/Dev/ai-hallucination-study` is the historical collection origin only. Points to the final verifier. |
| `.analysis-repository-marker` | Text reworded to match. The file name is kept, because the guard and tests resolve it by name. |
| `scripts/repository_guard.py` | Docstring reworded. `REFUSAL_MESSAGE` is now "Live data collection is disabled: final v2.7 data collection is complete and frozen. No new experimental responses may be collected." Behavior is unchanged: the guard refuses whenever the marker exists, and there is no command-line or environment override. |
| `scripts/collect_hybrid_api_batch.py` | Now calls the guard unless `--list` or `--dry-run` is given. |
| `scripts/collect_hybrid_manual.py` | Now calls the guard for `--capture-stdin` and for `--prepare` without `--dry-run`. `--list`, `--show-next`, the default display, and `--prepare --dry-run` remain read-only and allowed. |
| `tests/test_repository_guard.py` | Updated the message and module docstring. Added CLI tests showing that both hybrid collectors refuse writes and allow their read-only modes without creating state, raw or manual directories. Added the verifier to the analysis-only script list. Replaced the obsolete raw-directory test (§4). |

- Historical tooling tests call collection functions directly with temporary roots, or patch `ANALYSIS_REPOSITORY_MARKER` in-process. Ordinary execution has no bypass.
- Frozen generation settings, model sets, retry and pacing rules, and token limits are untouched.
- The hybrid collectors still pin the v2.6 manifest and assignment. Their read-only listings therefore show historical v2.6 rows (including M2) as unobserved. This is historical-tooling behavior only, and no write is possible.
- `finalize_collection_run.py` and `finalize_interrupted_api_run.py` were not changed:
  - Neither creates a new observation. The first finalizes an already-initialized directory whose initialization is guarded. The second records an offline failure for a stranded request.
  - The existing tests require `finalize_collection_run.py` to stay guard-free.

## 7. Documentation updates

- `docs/current_research_status.md` gains a "Canonical worktree" section. It records that raw evidence is copied and verified here, names the derived completion record, states that the frozen state is unchanged and holds the pre-completion pending state, and distinguishes the two checks. It also corrects the stale "raw-evidence copy pending" and "will be recorded" text and the open items.
- `docs/decision_log.md`:
  - D043 `status` is corrected from "copy … pending consolidation" to implemented and reverified.
  - D045 records this task's guard and verifier decision.
- `docs/final_paper_notes.md` needed no change; it already records all four facts:
  - Chapter 3 completeness statements cite the derived record;
  - the frozen state is the prospective freeze snapshot;
  - 85 manual captures predate the freeze;
  - the original freeze check does not pass unchanged after completion.
- Chapter 3 prose was not edited.

## 8. Final test results

```text
python3 scripts/verify_final_collection_v2_7.py      → FINAL_COMPLETION_CHECK: PASS
python3 scripts/create_hybrid_assignment_v1_0.py --verify → PASS
python3 scripts/create_experiment_freeze_v2_6.py --check  → PASS
python3 scripts/create_experiment_freeze_v2_7.py --check  → FAIL: v2.7 collection state no longer matches preserved evidence (expected)
python3 -m unittest discover -s tests                 → Ran 413 tests, OK
```

The suite grew from 370 tests to 413: 40 verifier tests, 2 hybrid-guard tests, and 1 eligibility test were added, and the replaced raw-directory test is counted once. After the suite, `git status` showed only this task's changes and the pre-existing untracked `data/derived_checkpoints/` and `data/quarantine/`. The raw inventory still passed.

## 9. Readiness

- The completed v2.7 collection now has a passing, deterministic integrity check in the canonical worktree.
- The frozen snapshot is preserved.
- New collection is blocked in this worktree.
- **Recommendation: READY_FOR_FINAL_ANALYSIS.** Analysis adaptation must use the 270-row v2.7 cohort, assert zero M2 rows, and apply the controlling eligibility rules (D033, D035, D037). All final results remain `[FINAL RESULT PENDING]`.
