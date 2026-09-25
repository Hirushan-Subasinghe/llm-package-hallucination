"""Offline tests for the HYBRID manual-collection guardrail."""

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import collect_hybrid_manual as manual  # noqa: E402


MANIFEST = ROOT / "manifests/api_final_v2.6.0_manifest.csv"
ASSIGNMENT = ROOT / "manifests/hybrid_assignment_v1.0.0.csv"


class HybridManualCollectionTests(unittest.TestCase):
    def setUp(self):
        self.manifest_bytes = MANIFEST.read_bytes()
        self.assignment_bytes = ASSIGNMENT.read_bytes()
        self.temporary = tempfile.TemporaryDirectory()
        self.manual_root = Path(self.temporary.name) / "manual_raw"

    def tearDown(self):
        self.temporary.cleanup()
        self.assertEqual(MANIFEST.read_bytes(), self.manifest_bytes)
        self.assertEqual(ASSIGNMENT.read_bytes(), self.assignment_bytes)

    def test_exactly_31_m4_manual_rows_are_selectable_in_frozen_order(self):
        rows = manual.select_manual_rows(MANIFEST, ASSIGNMENT, include_models=["M4"], manual_root=self.manual_root)
        self.assertEqual(len(rows), 31)
        self.assertTrue(all(row["model_condition_id"] == "M4" for row in rows))
        self.assertEqual([int(row["collection_order"]) for row in rows], sorted(int(row["collection_order"]) for row in rows))
        self.assertEqual(rows[0]["run_id"], "API-v2.6-DIST-OBS-05-M4-R02")
        self.assertEqual(rows[-1]["run_id"], "API-v2.6-DIST-OBS-05-M4-R03")

    def test_no_m4_api_row_is_selectable(self):
        rows = manual.select_manual_rows(MANIFEST, ASSIGNMENT, include_models=["M4"], manual_root=self.manual_root)
        _, assignment = manual.read_verified_rows(MANIFEST, ASSIGNMENT)
        self.assertTrue(all(assignment[row["run_id"]]["collection_interface"] == "manual" for row in rows))
        self.assertNotIn("API-v2.6-AUTH-FED-01-M4-R01", {row["run_id"] for row in rows})

    def test_m4_filter_selects_no_other_model(self):
        rows = manual.select_manual_rows(MANIFEST, ASSIGNMENT, include_models=["M4"], manual_root=self.manual_root)
        self.assertEqual({row["model_condition_id"] for row in rows}, {"M4"})

    def test_assignment_and_frozen_manifest_hashes_are_checked(self):
        self.assertEqual(hashlib.sha256(MANIFEST.read_bytes()).hexdigest(), manual.FROZEN_MANIFEST_SHA256)
        self.assertEqual(hashlib.sha256(ASSIGNMENT.read_bytes()).hexdigest(), manual.HYBRID_ASSIGNMENT_SHA256)
        with tempfile.TemporaryDirectory() as tmp:
            altered = Path(tmp) / "assignment.csv"
            altered.write_bytes(ASSIGNMENT.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "HYBRID assignment SHA-256"):
                manual.select_manual_rows(MANIFEST, altered, include_models=["M4"])

    def test_capture_is_append_only_and_preserves_bytes_and_metadata(self):
        row = manual.select_manual_rows(MANIFEST, ASSIGNMENT, include_models=["M4"], manual_root=self.manual_root)[0]
        response = b"exact pasted output\r\nwith bytes\n"
        directory = manual.capture(
            row, self.manual_root, response, actual_model="nvidia/nemotron-3-ultra-550b-a55b:free",
            actual_interface="approved-manual-interface-pending", response_status="completed",
            operator_id="collector_01", failure_note="",
        )
        self.assertEqual((directory / "response.md").read_bytes(), response)
        metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["collection_order"], int(row["collection_order"]))
        self.assertEqual(metadata["prompt_sha256"], row["expected_prompt_sha256"])
        self.assertEqual(metadata["raw_response_sha256"], hashlib.sha256(response).hexdigest())
        self.assertEqual(metadata["collection_interface"], "manual")
        with self.assertRaisesRegex(ValueError, "refusing overwrite"):
            manual.capture(
                row, self.manual_root, b"replacement", actual_model="M4", actual_interface="manual",
                response_status="completed", operator_id="collector_01", failure_note="",
            )

    def test_pristine_preparation_can_receive_one_capture(self):
        row = manual.select_manual_rows(MANIFEST, ASSIGNMENT, include_models=["M4"], manual_root=self.manual_root)[0]
        directory = manual.prepare(row, self.manual_root, dry_run=False)
        self.assertTrue(manual.is_pristine_preparation(directory, row))
        manual.capture(
            row, self.manual_root, b"first and only response", actual_model="M4 observed label",
            actual_interface="manual interface observed label", response_status="interrupted",
            operator_id="collector_01", failure_note="operator interruption after partial output",
        )
        self.assertEqual((directory / "response.md").read_bytes(), b"first and only response")


if __name__ == "__main__":
    unittest.main()
