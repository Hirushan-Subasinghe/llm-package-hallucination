# Final v2.7 Manual Capture Timing Provenance

**Task:** FINAL-COLLECTION-PROVENANCE-CHECKPOINT-01
**Checked (UTC):** 2026-09-25T07:27:36Z
**Nature:** a read-only timing check of existing manual evidence. It describes when evidence was captured and records no research results. No manual evidence was checked out, copied, modified, or regenerated.

## 1. Reference timestamp

- v2.7 freeze timestamp: `2026-09-24T23:22:58.369305Z`. Source: `config/experiment_freeze_v2.7.0.json` → `freeze_record_created_at_utc`. The same value appears in `data/final/collection_state_v2.7.0.json` → `derived_at_utc`.
- Freeze commit: `bba890d9aa5838f06bee4b1bd0e85d9e61b444f8`, tag `v2.7.0-freeze`.

## 2. Evidence examined

Every metadata file was read directly from the pinned commits with `git ls-tree` and `git show <sha>:<path>`. No checkout was performed.

| Model | Ref | Pinned commit | Path |
|---|---|---|---|
| M1 | `origin/collection/m1-manual-v2.6` | `1e062808dd26462b8afca2967aebc102eff066bf` | `data/final/manual_raw/v2.6.0/<run_id>/metadata.json` |
| M3 | `origin/collection/m3-manual-v2.6` | `ee952dca123a7eda1e7ea5e8c7f9518ed2e70608` | same |
| M4 | `origin/collection/m4-manual-v2.6` | `fb0d56ad0069c3f95b37493dcbcdf72a98c8c3ce` | same |

- Timing field: `captured_at_utc`. It is the only UTC timestamp field in the manual metadata schema, and it is written by `scripts/collect_hybrid_manual.py` (D035) at capture time.
- Each `run_id` was cross-checked against `manifests/api_final_v2.7.0_manifest.csv`. Every run is a v2.7 row with `collection_interface=manual` and the matching `model_condition_id`.
- The union is 130 unique run IDs with no duplicates. Content-hash verification of all 130 manual rows against the frozen manifest was already done in `docs/final_v2.7_consolidation_preflight.md` §2 and was not repeated here.

## 3. Result

Comparison rule: `captured_at_utc` < `2026-09-24T23:22:58.369305Z`, evaluated as timezone-aware UTC datetimes.

| Model | Manual runs | Captured before freeze | Pre-freeze range (UTC) | Captured after freeze | Post-freeze range (UTC) |
|---|---:|---:|---|---:|---|
| M1 | 50 | **36** | 2026-09-24T20:04:40Z – 2026-09-24T23:17:32Z | 14 | 2026-09-24T23:25:08Z – 2026-09-25T00:45:57Z |
| M3 | 49 | **49** | 2026-09-24T08:34:12Z – 2026-09-24T18:51:32Z | 0 | — |
| M4 | 31 | **0** | — | 31 | 2026-09-24T23:48:15Z – 2026-09-25T02:55:15Z |
| **Total** | **130** | **85** | | **45** | |

**Verified: 85 manual captures (M1 36 + M3 49) predate the v2.7 freeze timestamp.**

## 4. Interpretation (provenance only)

- The 85 pre-freeze captures were **not** produced by a v2.7 collection event. They were captured with the D035 HYBRID v2.6 manual scaffold, stored under `data/final/manual_raw/v2.6.0/`, and carry their original `API-v2.6-…` run IDs and v2.6 prompt paths (`data/generated_prompts/v2.6.0/…`).
- v2.7 **reused** them as compatible retained v2.6 evidence without regeneration. Compatibility holds because:
  - v2.7 membership is a mechanical removal of M2 rows that uses no outcome field (D036);
  - run IDs, prompt bytes and interface assignment are unchanged between v2.6 and v2.7;
  - the M1, M3 and M4 definitions are identical in model sets 1.4.0 and 1.5.0.
- The frozen `data/final/collection_state_v2.7.0.json` records all 130 manual rows as `pending`, including the 85 already captured on the then-unmerged manual branches. The frozen file is not edited. Manual completion must be recorded in a separate, append-only derived record after consolidation.
- The 45 post-freeze captures (M1 14, M4 31) used the same scaffold, root, run IDs and prompts.
- **Required disclosure:** Chapter 3 must state that 85 of the 130 manual observations were captured before the formal v2.7 freeze and were reused, not regenerated. This report does not edit Chapter 3.
