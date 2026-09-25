"""Tests for the operational --exclude-model scheduling filter on the v2.6 collector.

This filter is an in-memory, per-invocation row selector only: it must never
touch the frozen manifest, never renumber collection_order, never retry an
existing failed observation, and must leave excluded pending rows exactly
pending. See scripts/collect_api_batch_v2_6.py:filter_excluded_models.
"""

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import collect_api_batch
import collect_api_run
import collect_api_batch_v2_6 as v2_6

CONFIG = ROOT / "config/api_model_set_1.4.0.json"
MANIFEST = ROOT / "manifests/api_final_v2.6.0_manifest.csv"


def _never_call_network(*_args, **_kwargs):
    raise AssertionError("no live API request may occur in this test")


class ExcludeModelFilterTests(unittest.TestCase):
    """Pure unit tests against filter_excluded_models with a synthetic row list."""

    def setUp(self):
        self.rows = [
            {"run_id": f"R{i}", "collection_order": i, "model_condition_id": condition}
            for i, condition in enumerate(
                ["M1", "M2", "M3", "M4", "M2", "M3", "M4", "M1"], start=1
            )
        ]

    def test_exclude_one_condition_drops_only_that_condition(self):
        filtered = v2_6.filter_excluded_models(self.rows, ["M2"])
        self.assertEqual([row["model_condition_id"] for row in filtered], ["M1", "M3", "M4", "M3", "M4", "M1"])

    def test_pending_excluded_rows_are_simply_absent_not_marked(self):
        filtered = v2_6.filter_excluded_models(self.rows, ["M2"])
        excluded_run_ids = {row["run_id"] for row in self.rows if row["model_condition_id"] == "M2"}
        remaining_run_ids = {row["run_id"] for row in filtered}
        self.assertTrue(excluded_run_ids.isdisjoint(remaining_run_ids))
        # The excluded rows themselves are untouched dicts, not rewritten to any status.
        for row in self.rows:
            if row["run_id"] in excluded_run_ids:
                self.assertNotIn("collection_status", row)

    def test_collection_order_values_are_unchanged_and_unrenumbered(self):
        filtered = v2_6.filter_excluded_models(self.rows, ["M2"])
        original_by_run_id = {row["run_id"]: row["collection_order"] for row in self.rows}
        for row in filtered:
            self.assertEqual(row["collection_order"], original_by_run_id[row["run_id"]])
        # Not renumbered 1..N for the filtered subset.
        self.assertEqual([row["collection_order"] for row in filtered], [1, 3, 4, 6, 7, 8])

    def test_later_row_selectable_while_earlier_excluded_row_stays_pending(self):
        filtered = v2_6.filter_excluded_models(self.rows, ["M2"])
        # collection_order 2 (M2) is skipped; collection_order 3 (M3) is next.
        self.assertEqual(filtered[1]["collection_order"], 3)

    def test_filter_omitted_is_a_true_no_op(self):
        self.assertEqual(v2_6.filter_excluded_models(self.rows, None), self.rows)
        self.assertEqual(v2_6.filter_excluded_models(self.rows, []), self.rows)

    def test_invalid_model_condition_is_rejected(self):
        with self.assertRaises(ValueError):
            v2_6.filter_excluded_models(self.rows, ["M9"])
        with self.assertRaises(ValueError):
            v2_6.filter_excluded_models(self.rows, ["m2"])  # case-sensitive, not a silent match

    def test_does_not_mutate_input_rows(self):
        before = copy.deepcopy(self.rows)
        v2_6.filter_excluded_models(self.rows, ["M2"])
        self.assertEqual(self.rows, before)


class ExcludeModelCLIRejectionTests(unittest.TestCase):
    """Invalid --exclude-model values must be rejected at the CLI boundary with zero side effects."""

    def test_argparse_rejects_unknown_condition_before_any_action(self):
        manifest_before = MANIFEST.read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "state.json"
            raw_root = Path(tmp) / "raw"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/collect_api_batch_v2_6.py"),
                    "--manifest", str(MANIFEST),
                    "--config", str(CONFIG),
                    "--state", str(state_path),
                    "--raw-root", str(raw_root),
                    "--dry-run",
                    "--exclude-model", "M9",
                ],
                capture_output=True,
                text=True,
                cwd=str(ROOT),
            )
            self.assertEqual(completed.returncode, 2)
            self.assertFalse(state_path.exists())
            self.assertFalse(raw_root.exists())
        self.assertEqual(MANIFEST.read_bytes(), manifest_before)


class ExcludeModelBatchIntegrationTests(unittest.TestCase):
    """Integration through run_batch with a mock collector: no network, no manifest writes."""

    def setUp(self):
        self.config = collect_api_run.load_config(CONFIG)
        self.rows = collect_api_batch.ordered_rows(MANIFEST)
        self.manifest_hash = hashlib.sha256(MANIFEST.read_bytes()).hexdigest()
        self.manifest_bytes_before = MANIFEST.read_bytes()
        patcher = patch("requests.post", side_effect=AssertionError("no live API request may occur"))
        patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        self.assertEqual(MANIFEST.read_bytes(), self.manifest_bytes_before, "frozen manifest must stay byte-identical")

    def _run(self, *, exclude, limit, raw_root, state_path, collector):
        rows = v2_6.filter_excluded_models(self.rows, exclude)
        return collect_api_batch.run_batch(
            self.config,
            rows,
            manifest_hash=self.manifest_hash,
            state_path=state_path,
            raw_root=raw_root,
            limit=limit,
            collector=collector,
            continue_after_failed=True,
        )

    def test_exclude_m2_processes_only_non_m2_rows_without_touching_pending_m2(self):
        calls = []

        def fake_collector(config, row, *, raw_root):
            calls.append(row["run_id"])
            directory = raw_root / str(row["run_id"])
            directory.mkdir(parents=True)
            (directory / "metadata.json").write_text(json.dumps({"collection_status": "completed"}), encoding="utf-8")
            return directory

        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "state.json"
            raw_root = Path(tmp) / "raw"
            result = self._run(exclude=["M2"], limit=6, raw_root=raw_root, state_path=state_path, collector=fake_collector)

            self.assertEqual(result["processed"], 6)
            self.assertTrue(all(not run_id.endswith("-M2-R01") for run_id in calls))

            state = json.loads(state_path.read_text(encoding="utf-8"))
            processed_run_ids = {event["run_id"] for event in state["events"] if event["event"] == "completed"}
            self.assertTrue(all("-M2-" not in run_id for run_id in processed_run_ids))

            # No M2 run directory was ever created; pending M2 rows are untouched.
            m2_run_ids = {row["run_id"] for row in self.rows if row["model_condition_id"] == "M2"}
            for run_id in m2_run_ids:
                self.assertFalse((raw_root / run_id).exists())
            self.assertTrue(m2_run_ids.isdisjoint(set(calls)))

    def test_later_manifest_row_collected_while_earlier_m2_row_remains_pending(self):
        calls = []

        def fake_collector(config, row, *, raw_root):
            calls.append(row["run_id"])
            directory = raw_root / str(row["run_id"])
            directory.mkdir(parents=True)
            (directory / "metadata.json").write_text(json.dumps({"collection_status": "completed"}), encoding="utf-8")
            return directory

        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "state.json"
            raw_root = Path(tmp) / "raw"
            # collection_order 1=M1, 2=M2(excluded), 3=M3, 4=M4 for AUTH-FED-01.
            self._run(exclude=["M2"], limit=3, raw_root=raw_root, state_path=state_path, collector=fake_collector)
            self.assertEqual(calls, ["API-v2.6-AUTH-FED-01-M1-R01", "API-v2.6-AUTH-FED-01-M3-R01", "API-v2.6-AUTH-FED-01-M4-R01"])
            self.assertFalse((raw_root / "API-v2.6-AUTH-FED-01-M2-R01").exists())

    def test_existing_failed_m2_observation_is_preserved_and_not_retried(self):
        # Excluding M2 means the M2 row is not even in this invocation's row list, so it
        # cannot be blocked on or retried; a still-pending row (M1, collection_order 1)
        # is collected normally in the same invocation, proving the two are independent.
        def fake_collector(config, row, *, raw_root):
            directory = raw_root / str(row["run_id"])
            directory.mkdir(parents=True)
            (directory / "metadata.json").write_text(json.dumps({"collection_status": "completed"}), encoding="utf-8")
            return directory

        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "state.json"
            raw_root = Path(tmp) / "raw"
            failed_run_id = "API-v2.6-AUTH-FED-01-M2-R01"
            failed_dir = raw_root / failed_run_id
            failed_dir.mkdir(parents=True)
            metadata_path = failed_dir / "metadata.json"
            metadata_path.write_text(json.dumps({"collection_status": "failed", "failure_reason": "http_status_402"}), encoding="utf-8")
            before_metadata = metadata_path.read_bytes()
            before_mtime = metadata_path.stat().st_mtime_ns

            self._run(exclude=["M2"], limit=1, raw_root=raw_root, state_path=state_path, collector=fake_collector)

            self.assertEqual(metadata_path.read_bytes(), before_metadata)
            self.assertEqual(metadata_path.stat().st_mtime_ns, before_mtime)
            if state_path.exists():
                state = json.loads(state_path.read_text(encoding="utf-8"))
                self.assertTrue(all(event.get("run_id") != failed_run_id for event in state["events"]))

    def test_filter_omitted_matches_unfiltered_dry_run_behavior(self):
        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "state.json"
            raw_root = Path(tmp) / "raw"
            baseline = collect_api_batch.run_batch(
                self.config, self.rows, manifest_hash=self.manifest_hash,
                state_path=state_path, raw_root=raw_root, dry_run=True, continue_after_failed=True,
            )
        with tempfile.TemporaryDirectory() as tmp2:
            state_path2 = Path(tmp2) / "state.json"
            raw_root2 = Path(tmp2) / "raw"
            filtered_rows = v2_6.filter_excluded_models(self.rows, None)
            with_filter_omitted = collect_api_batch.run_batch(
                self.config, filtered_rows, manifest_hash=self.manifest_hash,
                state_path=state_path2, raw_root=raw_root2, dry_run=True, continue_after_failed=True,
            )
        self.assertEqual(baseline, with_filter_omitted)


if __name__ == "__main__":
    unittest.main()
