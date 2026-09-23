"""Offline tests for the verified HYBRID-aware v2.6 API selection layer."""

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import collect_hybrid_api_batch as hybrid_api  # noqa: E402


MANIFEST = ROOT / "manifests/api_final_v2.6.0_manifest.csv"
ASSIGNMENT = ROOT / "manifests/hybrid_assignment_v1.0.0.csv"
RAW_ROOT = ROOT / "data/final/raw"
CONFIG = ROOT / "config/api_model_set_1.4.0.json"


class HybridApiSelectionTests(unittest.TestCase):
    def setUp(self):
        self.manifest_bytes = MANIFEST.read_bytes()
        self.assignment_bytes = ASSIGNMENT.read_bytes()
        self.rows = hybrid_api.select_pending_api_rows(MANIFEST, ASSIGNMENT, RAW_ROOT)

    def tearDown(self):
        self.assertEqual(MANIFEST.read_bytes(), self.manifest_bytes)
        self.assertEqual(ASSIGNMENT.read_bytes(), self.assignment_bytes)

    def test_pending_api_counts_and_order(self):
        self.assertEqual(len(self.rows), 61)
        self.assertEqual(Counter(row["model_condition_id"] for row in self.rows), {"M1": 24, "M2": 34, "M3": 3})
        self.assertEqual([int(row["collection_order"]) for row in self.rows], sorted(int(row["collection_order"]) for row in self.rows))
        self.assertEqual(sum(row["model_condition_id"] == "M4" for row in self.rows), 0)

    def test_m3_exclusion_leaves_58_actionable_api_rows(self):
        rows = hybrid_api.select_pending_api_rows(MANIFEST, ASSIGNMENT, RAW_ROOT, exclude_models=["M3"])
        self.assertEqual(len(rows), 58)
        self.assertEqual(Counter(row["model_condition_id"] for row in rows), {"M1": 24, "M2": 34})
        self.assertEqual(rows[0]["run_id"], "API-v2.6-PKI-CRYPTO-02-M2-R01")
        self.assertEqual(rows[0]["collection_order"], "28")

    def test_only_api_assigned_never_attempted_rows_are_selected(self):
        assignment = {row["run_id"]: row for row in hybrid_api.read_verified_assignment(MANIFEST, ASSIGNMENT)}
        selected_ids = {str(row["run_id"]) for row in self.rows}
        self.assertTrue(all(assignment[run_id]["collection_interface"] == "api" for run_id in selected_ids))
        self.assertTrue(all(assignment[run_id]["api_attempted_before_hybrid"] == "false" for run_id in selected_ids))
        self.assertTrue(selected_ids.isdisjoint({row["run_id"] for row in assignment.values() if row["collection_interface"] == "manual"}))

    def test_all_existing_observations_including_failed_are_skipped(self):
        existing = {path.parent.name for path in RAW_ROOT.glob("API-v2.6-*/metadata.json")}
        self.assertEqual(len(existing), 119)
        selected_ids = {str(row["run_id"]) for row in self.rows}
        self.assertTrue(existing.isdisjoint(selected_ids))
        failed = {
            path.parent.name for path in RAW_ROOT.glob("API-v2.6-*/metadata.json")
            if json.loads(path.read_text(encoding="utf-8"))["collection_status"] == "failed"
        }
        self.assertTrue(failed)
        self.assertTrue(failed.isdisjoint(selected_ids))

    def test_dry_run_has_no_api_or_artifact_side_effects(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "state.json"
            raw = Path(tmp) / "raw"
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/collect_hybrid_api_batch.py"), "--dry-run", "--exclude-model", "M3", "--config", str(CONFIG), "--state", str(state), "--raw-root", str(raw)],
                cwd=ROOT, capture_output=True, text=True, check=True,
            )
            self.assertEqual(json.loads(result.stdout)["next_run_id"], "API-v2.6-PKI-CRYPTO-02-M2-R01")
            self.assertFalse(state.exists())
            self.assertFalse(raw.exists())

    def test_frozen_input_hashes_remain_exact(self):
        self.assertEqual(hashlib.sha256(MANIFEST.read_bytes()).hexdigest(), hybrid_api.FROZEN_MANIFEST_SHA256)
        self.assertEqual(hashlib.sha256(ASSIGNMENT.read_bytes()).hexdigest(), hybrid_api.HYBRID_ASSIGNMENT_SHA256)

    def test_changed_assignment_is_rejected_before_selection(self):
        with tempfile.TemporaryDirectory() as tmp:
            altered = Path(tmp) / "hybrid_assignment.csv"
            altered.write_bytes(ASSIGNMENT.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "HYBRID assignment SHA-256"):
                hybrid_api.select_pending_api_rows(MANIFEST, altered, RAW_ROOT)


if __name__ == "__main__":
    unittest.main()
