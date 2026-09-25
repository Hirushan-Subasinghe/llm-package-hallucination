# Final v2.7 Raw Evidence Inventory — Summary

**Task:** FINAL-COLLECTION-PROVENANCE-CHECKPOINT-01
**Generated (UTC):** 2026-09-25T07:27:36Z
**Branch / worktree:** `feature/data-collection` in `~/Dev/ai-hallucination-study`
**Decision:** D043 (`docs/decision_log.md`)
**Nature:** read-only provenance record. It holds collection-state and file-inventory facts only. It contains no research results.

## 1. Inventory file

- File: `reports/final_v2.7_raw_evidence_inventory.sha256`
- SHA-256 of the inventory file: `1f79cdecbd573b57f5121dc04fcd5e3aadcca8d46d005cebf4628a8fa75634e7`
- Format: GNU `sha256sum` output, one line per regular file. Paths are relative to the repository root (`data/final/raw/...`) and sorted in C-locale (bytewise) lexicographic order.
- Generation command, run from the repository root:

```bash
LC_ALL=C find data/final/raw -type f -print0 | LC_ALL=C sort -z | xargs -0 sha256sum \
  > reports/final_v2.7_raw_evidence_inventory.sha256
```

- Determinism: running the command a second time produced a byte-identical file (`cmp`).
- Verification command, from the repository root or any worktree root that holds a byte-for-byte copy:

```bash
sha256sum -c --quiet reports/final_v2.7_raw_evidence_inventory.sha256
```

It passed at generation time, and again after the checkpoint commit.

## 2. Totals

| Measure | Value |
|---|---:|
| Regular files (including `data/final/raw/.gitkeep`) | 1,552 |
| Regular files inside run directories | 1,551 |
| Top-level run directories | 229 |
| Total bytes of all regular files | 46,240,449 |
| Non-regular, non-directory entries (symlinks, etc.) | 0 |
| File names containing whitespace or backslashes | 0 |

Each run directory may contain nested `attempts/attempt-NN/` subdirectories. The run-directory counts below count top-level `data/final/raw/<run_id>/` directories only.

## 3. Breakdown

Groups were assigned mechanically. A directory whose name is an API `run_id` in the frozen `data/final/collection_state_v2.7.0.json` counts as retained v2.7 evidence, grouped by that row's `model_condition_id`. Any other `API-v2.6-*-M2-*` directory counts as historical M2 evidence. Every other directory is grouped by the version prefix in its name.

### 3.1 Retained v2.7 final-study API evidence (M1/M3/M4)

| Model | Run dirs | Files | Bytes | State: completed / truncated / failed / pending |
|---|---:|---:|---:|---|
| M1 | 40 | 276 | 18,565,955 | 27 / 10 / 3 / 0 |
| M3 | 41 | 303 | 4,956,295 | 36 / 0 / 5 / 0 |
| M4 | 59 | 387 | 11,748,158 | 42 / 6 / 11 / 0 |
| **Total** | **140** | **966** | **35,270,408** | **105 / 16 / 19 / 0** |

All 140 API rows in the frozen v2.7 collection state have their evidence directory present at `data/final/raw/<run_id>`. For each row, `metadata.json` and `prompt.txt` match the recorded `evidence.*_sha256`, and so does `response.md` wherever a response hash is recorded. Mismatches: 0.

### 3.2 Historical M2 evidence (superseded v2.6; not final-study observations)

| Group | Run dirs | Files | Bytes |
|---|---:|---:|---:|
| `API-v2.6-*-M2-*` | 11 | 59 | 1,944,524 |

These directories are preserved unchanged, hash-listed in the v2.7 freeze (`m2_exclusion`), and excluded from every v2.7 metric and denominator (D036).

### 3.3 Historical pre-v2.6 evidence (not final-study observations)

| Version prefix | Run dirs | Files | Bytes |
|---|---:|---:|---:|
| `API-*` (unversioned, v2.0 era) | 2 | 14 | 21,713 |
| `API-v2.1-*` | 4 | 28 | 332,961 |
| `API-v2.2-*` | 10 | 70 | 1,322,928 |
| `API-v2.3-*` | 8 | 54 | 1,128,935 |
| `API-v2.4-*` | 30 | 200 | 3,397,719 |
| `API-v2.5-*` | 24 | 160 | 2,821,261 |
| **Total** | **78** | **526** | **9,025,517** |

No `API-v2.6-*` directory falls outside the 140 retained rows and the 11 M2 directories. No `API-v2.7-*` directory exists.

Manual evidence (130 rows) is not under `data/final/raw/`. It is tracked in Git under `data/final/manual_raw/v2.6.0/` on the manual collection branches (see `reports/final_v2.7_manual_timing_provenance.md`), so this inventory does not cover it.

## 4. API batch-state checkpoint

- File: `data/final/api_batch_state_v2.6.0.json`
- Working-tree SHA-256: `1a3af56d138d3da1c3e67c1f04f55b27e4ab5d0ec786ab31d7c2cd17cb6b695c`
- Reference: `data/final/collection_state_v2.7.0.json` → `source_v2_6_state_snapshot.sha256` = `1a3af56d138d3da1c3e67c1f04f55b27e4ab5d0ec786ab31d7c2cd17cb6b695c`. **Exact match.**
- Previously committed version (pre-checkpoint `HEAD` `44c7f00`): `631b20b258b03c3085584ba5dcf3ee9b7cab0bf683e4e21feb054d38e6230ced`
- Nature of the difference from the previous commit:
  - `events` grew from 1,008 to 1,073 entries, and the first 1,008 are identical, so the change is append-only.
  - The collector-maintained fields `updated_at_utc` (`2026-09-23T10:21:55.499559Z` → `2026-09-24T03:17:10.643089Z`) and `provider_next_allowed_at_epoch` (OpenRouter, Groq) advanced.
  - No other top-level key changed.
- The file was staged and committed without modification.

## 5. Integrity statements

- **No raw evidence was modified.** The inventory was produced with read-only `find`/`sort`/`sha256sum`. After the checkpoint commit, `sha256sum -c` against the inventory passed for all 1,552 files.
- **`data/final/raw/` remains gitignored** (`.gitignore`: `data/final/raw/*` with the exception `!data/final/raw/.gitkeep`). The only Git-tracked path under it is `data/final/raw/.gitkeep`, as before. No raw evidence was added to Git (D043).
- Frozen v2.7 inputs are unchanged. All 39 hashed inputs in `config/experiment_freeze_v2.7.0.json` match. The freeze JSON, model set 1.5.0, v2.7 manifest and v2.7 collection state are byte-identical to `v2.7.0-freeze`. `scripts/create_experiment_freeze_v2_7.py --check` passes. The tag `v2.7.0-freeze` resolves to `bba890d9aa5838f06bee4b1bd0e85d9e61b444f8`.
- No observation was generated, regenerated, retried, installed, or executed.

## 6. Next step (not performed here)

Under D043, the canonical final worktree receives a byte-for-byte copy of `data/final/raw/`, and `sha256sum -c reports/final_v2.7_raw_evidence_inventory.sha256` is re-run there before any analysis.
