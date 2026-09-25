#!/usr/bin/env python3
"""Tests for the read-only response inventory builder."""

import csv
import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_response_inventory


class ResponseInventoryTests(unittest.TestCase):
    def setUp(self):
        self.manifest_path = ROOT / "manifests" / "api_final_v2.2.0_manifest.csv"
        self.raw_root = ROOT / "data" / "final" / "raw"

    def test_v2_2_inventory_generation(self):
        """Test building inventory for the active v2.2 experiment."""
        manifest_bytes_before = self.manifest_path.read_bytes()
        manifest_hash_before = hashlib.sha256(manifest_bytes_before).hexdigest()

        inventory = build_response_inventory.build_response_inventory(
            manifest_path=self.manifest_path,
            raw_root=self.raw_root,
            root=ROOT,
        )

        # Stable live invariants only: active collection counts may change.
        self.assertEqual(len(inventory), 360)
        orders = [item["collection_order"] for item in inventory]
        self.assertEqual(orders, list(range(1, 361)))
        self.assertEqual(len({item["run_id"] for item in inventory}), 360)

        manifest_rows = build_response_inventory.load_manifest_rows(self.manifest_path)
        for manifest_row, item in zip(manifest_rows, inventory):
            self.assertEqual(item["run_id"], manifest_row["run_id"])
            self.assertEqual(item["provider"], manifest_row["api_provider"])
            metadata_path = self.raw_root / item["run_id"] / "metadata.json"
            if metadata_path.is_file():
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                self.assertEqual(item["collection_status"], metadata["collection_status"])
                self.assertEqual(item["completion_status"], metadata.get("response_completion_status"))

        manifest_bytes_after = self.manifest_path.read_bytes()
        self.assertEqual(hashlib.sha256(manifest_bytes_after).hexdigest(), manifest_hash_before)

    def test_schema_conformance(self):
        """Verify all inventory fields match the expected inventory schema."""
        inventory = build_response_inventory.build_response_inventory(
            manifest_path=self.manifest_path,
            raw_root=self.raw_root,
            root=ROOT,
        )
        required_keys = set(build_response_inventory.INVENTORY_COLUMNS)
        for item in inventory:
            self.assertEqual(set(item.keys()), required_keys)
            self.assertIsInstance(item["run_id"], str)
            self.assertIsInstance(item["collection_order"], int)
            self.assertIsInstance(item["provider"], str)
            self.assertIsNone(item["tool"])
            self.assertIsInstance(item["model"], str)
            self.assertIsInstance(item["model_condition_id"], str)
            self.assertIsNone(item["workflow"])
            self.assertIsInstance(item["task_id"], str)
            self.assertIsInstance(item["category"], str)
            self.assertIsInstance(item["replicate"], str)
            self.assertIsInstance(item["manifest_path"], str)
            self.assertIsInstance(item["rendered_prompt_path"], str)
            self.assertIsInstance(item["expected_prompt_sha256"], str)
            self.assertIn(item["collection_status"], {"pending", "completed", "truncated", "failed", "requesting", "suspended"})
            if item["collection_status"] == "pending":
                self.assertIsNone(item["completion_status"])
                self.assertIsNone(item["truncated"])
                self.assertIsNone(item["token_count"])
                self.assertIsNone(item["response_artifact_path"])
            else:
                self.assertIn(item["completion_status"], {"COMPLETED", "TRUNCATED", None})
                self.assertIn(item["truncated"], {True, False, None})
                if item["token_count"] is not None:
                    self.assertIsInstance(item["token_count"], int)
            self.assertIsNone(item["interface_pass"])

    def test_isolated_fixture_pipeline(self):
        """Test with temporary directory fixture covering various states."""
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            manifest_path = temp_dir / "test_manifest.csv"
            raw_root = temp_dir / "raw"
            out_json = temp_dir / "out.json"
            out_csv = temp_dir / "out.csv"

            # Create mock manifest with 4 rows (unordered to test sorting)
            manifest_rows = [
                {
                    "collection_order": "3",
                    "run_id": "RUN-03",
                    "phase": "final",
                    "task_id": "TASK-03",
                    "category": "AUTH-FED",
                    "task_set_version": "final-2.0.0",
                    "model_set_version": "api-model-set-1.1.0",
                    "model_condition_id": "M3",
                    "model_id": "test-model-3",
                    "api_provider": "Groq",
                    "underlying_provider_pin": "not_applicable",
                    "run_repetition": "R01",
                    "rendered_prompt_path": "prompts/p3.txt",
                    "expected_prompt_sha256": "3" * 64,
                    "collection_status": "pending",
                },
                {
                    "collection_order": "1",
                    "run_id": "RUN-01",
                    "phase": "final",
                    "task_id": "TASK-01",
                    "category": "AUTH-FED",
                    "task_set_version": "final-2.0.0",
                    "model_set_version": "api-model-set-1.1.0",
                    "model_condition_id": "M1",
                    "model_id": "test-model-1",
                    "api_provider": "OpenRouter",
                    "underlying_provider_pin": "cohere",
                    "run_repetition": "R01",
                    "rendered_prompt_path": "prompts/p1.txt",
                    "expected_prompt_sha256": "1" * 64,
                    "collection_status": "pending",
                },
                {
                    "collection_order": "2",
                    "run_id": "RUN-02",
                    "phase": "final",
                    "task_id": "TASK-02",
                    "category": "AUTH-FED",
                    "task_set_version": "final-2.0.0",
                    "model_set_version": "api-model-set-1.1.0",
                    "model_condition_id": "M2",
                    "model_id": "test-model-2",
                    "api_provider": "Groq",
                    "underlying_provider_pin": "not_applicable",
                    "run_repetition": "R01",
                    "rendered_prompt_path": "prompts/p2.txt",
                    "expected_prompt_sha256": "2" * 64,
                    "collection_status": "pending",
                },
                {
                    "collection_order": "4",
                    "run_id": "RUN-04",
                    "phase": "final",
                    "task_id": "TASK-04",
                    "category": "AUTH-FED",
                    "task_set_version": "final-2.0.0",
                    "model_set_version": "api-model-set-1.1.0",
                    "model_condition_id": "M4",
                    "model_id": "test-model-4",
                    "api_provider": "OpenRouter",
                    "underlying_provider_pin": "nvidia",
                    "run_repetition": "R01",
                    "rendered_prompt_path": "prompts/p4.txt",
                    "expected_prompt_sha256": "4" * 64,
                    "collection_status": "pending",
                },
            ]

            with manifest_path.open("w", encoding="utf-8", newline="") as h:
                writer = csv.DictWriter(h, fieldnames=list(manifest_rows[0].keys()))
                writer.writeheader()
                writer.writerows(manifest_rows)

            # Create mock run directory for RUN-01 (completed)
            run1_dir = raw_root / "RUN-01"
            run1_dir.mkdir(parents=True)
            (run1_dir / "response.md").write_text("# Response 1", encoding="utf-8")
            (run1_dir / "metadata.json").write_text(
                json.dumps({
                    "run_id": "RUN-01",
                    "collection_status": "completed",
                    "response_completion_status": "COMPLETED",
                    "finish_reason": "stop",
                    "response_path": "response.md",
                    "token_usage": {"completion_tokens": 500},
                }),
                encoding="utf-8",
            )

            # Create mock run directory for RUN-02 (truncated)
            run2_dir = raw_root / "RUN-02"
            run2_dir.mkdir(parents=True)
            (run2_dir / "response.md").write_text("# Response 2...", encoding="utf-8")
            (run2_dir / "metadata.json").write_text(
                json.dumps({
                    "run_id": "RUN-02",
                    "collection_status": "truncated",
                    "response_completion_status": "TRUNCATED",
                    "finish_reason": "length",
                    "response_path": "response.md",
                    "response_token_metadata": {"total_completion_tokens": 12000},
                }),
                encoding="utf-8",
            )

            # RUN-03 and RUN-04 are pending (no directory)

            inventory = build_response_inventory.build_response_inventory(
                manifest_path=manifest_path,
                raw_root=raw_root,
                root=temp_dir,
            )

            self.assertEqual(len(inventory), 4)
            self.assertEqual([r["run_id"] for r in inventory], ["RUN-01", "RUN-02", "RUN-03", "RUN-04"])
            self.assertEqual(inventory[0]["collection_status"], "completed")
            self.assertEqual(inventory[0]["token_count"], 500)
            self.assertIs(inventory[0]["truncated"], False)

            self.assertEqual(inventory[1]["collection_status"], "truncated")
            self.assertEqual(inventory[1]["token_count"], 12000)
            self.assertIs(inventory[1]["truncated"], True)

            self.assertEqual(inventory[2]["collection_status"], "pending")
            self.assertIsNone(inventory[2]["token_count"])
            self.assertIsNone(inventory[2]["truncated"])

            self.assertEqual(inventory[3]["collection_status"], "pending")

            # Only explicit failure artifacts, not an ordinary attempt directory,
            # can classify a metadata-less run as failed.
            failed_dir = raw_root / "RUN-03" / "failed_attempts" / "attempt-01"
            failed_dir.mkdir(parents=True)
            ordinary_attempt = raw_root / "RUN-04" / "attempts" / "attempt-01"
            ordinary_attempt.mkdir(parents=True)
            inventory = build_response_inventory.build_response_inventory(
                manifest_path=manifest_path, raw_root=raw_root, root=temp_dir
            )
            self.assertEqual(inventory[2]["collection_status"], "failed")
            self.assertEqual(inventory[3]["collection_status"], "pending")

            state_path = temp_dir / "state.json"
            state_path.write_text(json.dumps({"events": [{
                "event": "temporarily_blocked_or_failed", "run_id": "RUN-04"
            }]}), encoding="utf-8")
            inventory = build_response_inventory.build_response_inventory(
                manifest_path=manifest_path,
                raw_root=raw_root,
                state_path=state_path,
                root=temp_dir,
            )
            self.assertEqual(inventory[3]["collection_status"], "failed")

            # Write outputs
            build_response_inventory.write_inventory_json(inventory, out_json)
            build_response_inventory.write_inventory_csv(inventory, out_csv)

            self.assertTrue(out_json.is_file())
            self.assertTrue(out_csv.is_file())

            loaded_json = json.loads(out_json.read_text(encoding="utf-8"))
            self.assertEqual(len(loaded_json), 4)
            self.assertEqual(loaded_json[0]["run_id"], "RUN-01")

            with out_csv.open(encoding="utf-8", newline="") as h:
                loaded_csv = list(csv.DictReader(h))
            self.assertEqual(len(loaded_csv), 4)
            self.assertEqual(loaded_csv[0]["run_id"], "RUN-01")
            self.assertEqual(loaded_csv[0]["collection_status"], "completed")
            self.assertEqual(loaded_csv[2]["collection_status"], "failed")
            self.assertEqual(loaded_csv[2]["completion_status"], "")


if __name__ == "__main__":
    unittest.main()
