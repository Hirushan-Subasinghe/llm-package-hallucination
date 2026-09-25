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
import extract_package_references


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
                self.assertEqual(item["raw_collection_status"], metadata["collection_status"])
                if item["status_correction"] is None:
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
                self.assertIn(item["completion_status"], {"COMPLETED", "TRUNCATED", "FAILED", None})
                self.assertIn(item["truncated"], {True, False, None})
                if item["token_count"] is not None:
                    self.assertIsInstance(item["token_count"], int)
            self.assertIsNone(item["interface_pass"])
            self.assertIn(item["status_correction"], {None, "D035"})

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


def write_metadata(run_dir, metadata, response_text):
    run_dir.mkdir(parents=True)
    (run_dir / "response.md").write_text(response_text, encoding="utf-8")
    (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def tree_hashes(root):
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*")) if path.is_file()
    }


class D035ProviderAbnormalFinishTests(unittest.TestCase):
    """Synthetic fixtures only; no real observation is read or represented."""

    RUNS = [
        # run_id, raw collection_status, raw completion status, finish_reason, response text
        ("RUN-STOP", "completed", "COMPLETED", "stop", "import express from 'express';\n"),
        ("RUN-LENGTH", "truncated", "TRUNCATED", "length", "import zod from 'zod';\nconst x"),
        ("RUN-ERROR-FULL", "completed", "COMPLETED", "error",
         "import samlify from 'samlify';\nconsole.log('done');\n"),
        ("RUN-ERROR-PARTIAL", "completed", "COMPLETED", "error",
         "import xpath from 'xpath';\nconst familyName = getAttr('familyName"),
        ("RUN-PILOT", "completed", None, None, "import lodash from 'lodash';\n"),
    ]

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.raw_root = self.root / "raw"
        self.manifest_path = self.root / "manifest.csv"
        fields = ["collection_order", "run_id", "task_id", "category", "model_condition_id",
                  "model_id", "api_provider", "run_repetition", "rendered_prompt_path",
                  "expected_prompt_sha256", "collection_status"]
        with self.manifest_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for order, (run_id, *_rest) in enumerate(self.RUNS, start=1):
                writer.writerow({
                    "collection_order": str(order), "run_id": run_id, "task_id": "TASK-01",
                    "category": "AUTH-FED", "model_condition_id": "M4", "model_id": "synthetic-model",
                    "api_provider": "OpenRouter", "run_repetition": "R01",
                    "rendered_prompt_path": "prompts/p.txt", "expected_prompt_sha256": "a" * 64,
                    "collection_status": "pending",
                })
        for run_id, status, completion, finish_reason, text in self.RUNS:
            metadata = {"run_id": run_id, "collection_status": status, "response_path": "response.md",
                        "token_usage": {"completion_tokens": 7599}}
            if completion is not None:
                metadata["response_completion_status"] = completion
            if run_id != "RUN-PILOT":
                metadata["finish_reason"] = finish_reason
            write_metadata(self.raw_root / run_id, metadata, text)

    def build(self):
        return {row["run_id"]: row for row in build_response_inventory.build_response_inventory(
            manifest_path=self.manifest_path, raw_root=self.raw_root, root=self.root)}

    def test_stop_and_length_behaviour_unchanged(self):
        inventory = self.build()
        stop, length = inventory["RUN-STOP"], inventory["RUN-LENGTH"]
        self.assertEqual((stop["collection_status"], stop["completion_status"], stop["truncated"]),
                         ("completed", "COMPLETED", False))
        self.assertEqual((length["collection_status"], length["completion_status"], length["truncated"]),
                         ("truncated", "TRUNCATED", True))
        for row in (stop, length):
            self.assertIsNone(row["status_correction"])
            self.assertEqual(row["raw_collection_status"], row["collection_status"])

    def test_error_finish_with_non_empty_or_partial_content_is_failed(self):
        inventory = self.build()
        for run_id in ("RUN-ERROR-FULL", "RUN-ERROR-PARTIAL"):
            with self.subTest(run_id=run_id):
                row = inventory[run_id]
                self.assertEqual(row["collection_status"], "failed")
                self.assertEqual(row["completion_status"], "FAILED")
                self.assertIs(row["truncated"], False)
                self.assertEqual(row["status_correction"], "D035")
                self.assertEqual(row["raw_collection_status"], "completed")
                self.assertEqual(row["provider_finish_reason"], "error")

    def test_failed_response_remains_preserved_and_referenced(self):
        inventory = self.build()
        for run_id in ("RUN-ERROR-FULL", "RUN-ERROR-PARTIAL"):
            path = inventory[run_id]["response_artifact_path"]
            self.assertEqual(path, f"raw/{run_id}/response.md")
            self.assertTrue((self.root / path).is_file())
            self.assertEqual(inventory[run_id]["token_count"], 7599)

    def test_record_without_finish_reason_field_is_outside_the_rule(self):
        row = self.build()["RUN-PILOT"]
        self.assertEqual(row["collection_status"], "completed")
        self.assertIsNone(row["status_correction"])

    def test_raw_metadata_and_responses_are_not_rewritten(self):
        before = tree_hashes(self.raw_root)
        inventory = list(self.build().values())
        build_response_inventory.write_inventory_json(inventory, self.root / "out" / "inventory.json")
        build_response_inventory.write_inventory_csv(inventory, self.root / "out" / "inventory.csv")
        self.assertEqual(tree_hashes(self.raw_root), before)
        metadata = json.loads((self.raw_root / "RUN-ERROR-PARTIAL" / "metadata.json").read_text())
        self.assertEqual(metadata["collection_status"], "completed")
        self.assertEqual(metadata["response_completion_status"], "COMPLETED")

    def test_d035_marker_is_serialized_to_json_and_csv(self):
        inventory = list(self.build().values())
        json_path, csv_path = self.root / "inventory.json", self.root / "inventory.csv"
        build_response_inventory.write_inventory_json(inventory, json_path)
        build_response_inventory.write_inventory_csv(inventory, csv_path)
        loaded = {row["run_id"]: row for row in json.loads(json_path.read_text())}
        self.assertEqual(loaded["RUN-ERROR-PARTIAL"]["status_correction"], "D035")
        with csv_path.open(encoding="utf-8", newline="") as handle:
            rows = {row["run_id"]: row for row in csv.DictReader(handle)}
        self.assertEqual(rows["RUN-ERROR-PARTIAL"]["status_correction"], "D035")
        self.assertEqual(rows["RUN-ERROR-PARTIAL"]["raw_collection_status"], "completed")
        self.assertEqual(rows["RUN-STOP"]["status_correction"], "")

    def test_schema_declares_every_inventory_column(self):
        schema = json.loads((ROOT / "schemas" / "response_inventory_item.schema.json").read_text())
        self.assertEqual(set(schema["required"]), set(build_response_inventory.INVENTORY_COLUMNS))
        self.assertEqual(set(schema["properties"]), set(build_response_inventory.INVENTORY_COLUMNS))
        for row in self.build().values():
            self.assertEqual(set(row), set(schema["required"]))

    def test_rerun_is_byte_identical(self):
        outputs = []
        for attempt in ("a", "b"):
            inventory = build_response_inventory.build_response_inventory(
                manifest_path=self.manifest_path, raw_root=self.raw_root, root=self.root)
            json_path = self.root / attempt / "inventory.json"
            csv_path = self.root / attempt / "inventory.csv"
            build_response_inventory.write_inventory_json(inventory, json_path)
            build_response_inventory.write_inventory_csv(inventory, csv_path)
            outputs.append((json_path.read_bytes(), csv_path.read_bytes()))
        self.assertEqual(outputs[0], outputs[1])

    def test_pipe03_does_not_extract_packages_from_failed_response(self):
        inventory = build_response_inventory.build_response_inventory(
            manifest_path=self.manifest_path, raw_root=self.raw_root, root=self.root)
        occurrences = extract_package_references.build_occurrences(inventory, self.raw_root, root=self.root)
        run_ids = {occurrence["run_id"] for occurrence in occurrences}
        self.assertIn("RUN-STOP", run_ids)
        self.assertIn("RUN-LENGTH", run_ids)
        self.assertNotIn("RUN-ERROR-FULL", run_ids)
        self.assertNotIn("RUN-ERROR-PARTIAL", run_ids)


if __name__ == "__main__":
    unittest.main()
