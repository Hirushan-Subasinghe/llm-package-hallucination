# Final v2.7 Collection Completion — Derived Record

**Task:** FINAL-V2.7-EVIDENCE-CONSOLIDATION-VALIDATION-01
**Created (UTC):** 2026-09-25T08:56:33Z
**Branch / worktree:** `integration/v2.7-final` in `~/Dev/ai-hallucination-final` (HEAD at derivation `da11ae42644dacbe67ba5a7c0ef2b4deedb29f89`)
**Machine-readable record:** `reports/final_collection_completion_v2.7.0.json` (SHA-256 `ec7dfe5e0d4f32e82b31f727a4148a709e5f33f05325648ff6b8dd477988d036`)
**Nature:** a non-frozen, append-only derived record of collection state. It holds no research results.

## 1. What this record is and is not

- This record supplements the frozen initial state `data/final/collection_state_v2.7.0.json`. It does **not** replace, overwrite, or re-freeze that file.
- The frozen file is unchanged. Its SHA-256 is `55a32c0d4a7c6ae493ca701be2dea11995792a09bdb4a9fb8f3024ca073709a6`, and it still matches `initial_collection_state.sha256` in `config/experiment_freeze_v2.7.0.json`.
- The frozen file records the 130 manual rows as `pending`, because the freeze commit held no manual evidence. This record states the final observed status of those rows after the three manual collection branches were merged.
- It states collection status only. It does not decide primary-analysis eligibility (see §5).

## 2. Derivation

The record was produced with a read-only call of `derive_collection_state(build_manifest_rows(), <frozen derived_at_utc>)` from the unmodified frozen script `scripts/create_experiment_freeze_v2_7.py` (SHA-256 `6318922ac50309d378064fe2ba10765ea20faaafa1f750954dfb2120d72c370c`). The call ran against the consolidated worktree evidence, and each row was compared with the frozen initial state. The function writes nothing, and no evidence was generated, regenerated, or modified.

## 3. Frozen planned state and final observed state

| Measure | Frozen initial state (2026-09-24T23:22:58.369305Z) | Final observed state |
|---|---:|---:|
| Assigned rows | 270 | 270 |
| M2 rows | 0 | 0 |
| API completed / truncated / failed / pending | 105 / 16 / 19 / 0 | 105 / 16 / 19 / 0 |
| Manual completed / pending | 0 / 130 | 130 / 0 |
| Pending, all rows | 130 | 0 |

| Condition | API completed | API truncated | API failed | Manual completed | Total |
|---|---:|---:|---:|---:|---:|
| M1 | 27 | 10 | 3 | 50 | 90 |
| M3 | 36 | 0 | 5 | 49 | 90 |
| M4 | 42 | 6 | 11 | 31 | 90 |
| **Total** | **105** | **16** | **19** | **130** | **270** |

**Transitions since freeze:** 130 manual rows moved from `pending` to `completed`. None of the 140 API rows changed, in status or in evidence hashes.

**Manual capture timing:** 85 captures predate the freeze timestamp (M1 36, M3 49), and 45 postdate it (M1 14, M4 31). This agrees with `reports/final_v2.7_manual_timing_provenance.md`.

## 4. Evidence sources

| Source | Location | Provenance |
|---|---|---|
| API raw evidence (gitignored, D043) | `data/final/raw/` | Copied from `~/Dev/ai-hallucination-study/data/final/raw/`. Verified against `reports/final_v2.7_raw_evidence_inventory.sha256`: 1,552 files, inventory SHA-256 `1f79cdecbd573b57f5121dc04fcd5e3aadcca8d46d005cebf4628a8fa75634e7`. |
| M1 manual evidence (tracked) | `data/final/manual_raw/v2.6.0/` | `origin/collection/m1-manual-v2.6` @ `1e062808dd26462b8afca2967aebc102eff066bf`. Merged by `c828e4449de26d8bf31eff5af80fe7a8982c87d5`. |
| M3 manual evidence (tracked) | same | `origin/collection/m3-manual-v2.6` @ `ee952dca123a7eda1e7ea5e8c7f9518ed2e70608`. Merged by `8eeb372f674ecb5168c7b999fa49d7daa9b522aa`. |
| M4 manual evidence (tracked) | same | `origin/collection/m4-manual-v2.6` @ `fb0d56ad0069c3f95b37493dcbcdf72a98c8c3ce`. Merged by `56be98f10b5f3abf55f656c2cd06e6520338eaef`. |
| Provenance checkpoint | — | `2f5025547715f15469e564721ebd8a8bb9b01c76` ("data: checkpoint final v2.7 collection provenance") |
| Freeze | — | Tag `v2.7.0-freeze` → `bba890d9aa5838f06bee4b1bd0e85d9e61b444f8`. Manifest `manifests/api_final_v2.7.0_manifest.csv`, SHA-256 `2edf2638f08a1079aadd02c174951a912aa2797b56df36997878096b29a4ed20`. |

Each row entry in the JSON record includes its evidence path and its `metadata.json`, `prompt.txt`, and `response.md` SHA-256 values.

## 5. Primary-analysis eligibility

This record does **not** decide primary-analysis eligibility. Completed, truncated, and failed are collection statuses. The record does not claim that truncated or failed API rows are eligible for primary analysis. Eligibility is governed by the controlling decisions (including D033 and D035) and by the frozen truncation and failure policy, and the v2.7 analysis pipeline applies them.

## 6. Verification

See `docs/final_v2.7_evidence_consolidation_verification.md`.
