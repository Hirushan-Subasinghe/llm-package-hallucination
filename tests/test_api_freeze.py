import csv
import hashlib
import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import collect_api_batch
import collect_api_run
import create_api_manifest
import render_api_prompts


class APIFreezeTests(unittest.TestCase):
    def test_frozen_task_and_rendered_prompt_shape(self):
        tasks = render_api_prompts.load_tasks()
        rendered = render_api_prompts.expected_rendered()
        self.assertEqual(len(tasks), 30)
        self.assertEqual(len(rendered), 30)
        for task in tasks:
            path = render_api_prompts.RENDERED_DIR / f"{task['task_id']}.txt"
            self.assertEqual(path.read_bytes(), rendered[task["task_id"]])
            self.assertEqual(path.read_text(encoding="utf-8").rstrip("\n"), task["prompt"])

    def test_official_manifest_counts_hashes_and_rotations(self):
        config = collect_api_run.load_config(collect_api_run.DEFAULT_CONFIG)
        rows = create_api_manifest.make_rows(config, create_api_manifest.load_frozen_tasks())
        self.assertEqual(len(rows), 360)
        self.assertEqual(len({row["run_id"] for row in rows}), 360)
        self.assertEqual(Counter(row["model_condition_id"] for row in rows), Counter({model: 90 for model in ("M1", "M2", "M3", "M4")}))
        self.assertEqual(Counter(row["run_repetition"] for row in rows), Counter({rep: 120 for rep in ("R01", "R02", "R03")}))
        self.assertEqual(Counter(row["category"] for row in rows), Counter({category: 60 for category in ("AUTH-FED", "PKI-CRYPTO", "DOC-BINARY", "ENT-INT", "DATA-ADV", "DIST-OBS")}))
        self.assertTrue(all(row["collection_status"] == "pending" for row in rows))
        self.assertEqual([row["model_condition_id"] for row in rows[:4]], ["M1", "M2", "M3", "M4"])
        self.assertEqual([row["model_condition_id"] for row in rows[4:8]], ["M2", "M3", "M4", "M1"])
        self.assertEqual([row["model_condition_id"] for row in rows[120:124]], ["M2", "M3", "M4", "M1"])
        for row in rows:
            prompt = ROOT / row["rendered_prompt_path"]
            self.assertEqual(hashlib.sha256(prompt.read_bytes()).hexdigest(), row["expected_prompt_sha256"])

    def test_batch_dry_run_is_sequential_and_non_mutating(self):
        config = collect_api_run.load_config(collect_api_run.DEFAULT_CONFIG)
        rows = collect_api_batch.ordered_rows(create_api_manifest.MANIFEST_PATH)
        with tempfile.TemporaryDirectory() as temporary:
            state = Path(temporary) / "state.json"
            raw = Path(temporary) / "raw"
            result = collect_api_batch.run_batch(
                config,
                rows,
                manifest_hash=hashlib.sha256(create_api_manifest.MANIFEST_PATH.read_bytes()).hexdigest(),
                state_path=state,
                raw_root=raw,
                dry_run=True,
            )
            self.assertEqual(result["collection_order"], 1)
            self.assertEqual(result["next_run_id"], rows[0]["run_id"])
            self.assertFalse(state.exists())
            self.assertFalse(raw.exists())

    def test_batch_stops_at_existing_incomplete_row_to_preserve_order(self):
        config = collect_api_run.load_config(collect_api_run.DEFAULT_CONFIG)
        rows = collect_api_batch.ordered_rows(create_api_manifest.MANIFEST_PATH)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            state = root / "state.json"
            raw = root / "raw"
            blocked = raw / rows[0]["run_id"]
            blocked.mkdir(parents=True)
            (blocked / "metadata.json").write_text(
                json.dumps({"collection_status": "failed"}) + "\n",
                encoding="utf-8",
            )
            calls = []
            result = collect_api_batch.run_batch(
                config,
                rows,
                manifest_hash=hashlib.sha256(create_api_manifest.MANIFEST_PATH.read_bytes()).hexdigest(),
                state_path=state,
                raw_root=raw,
                collector=lambda *args, **kwargs: calls.append((args, kwargs)),
            )
            self.assertEqual(result["blocked_collection_order"], 1)
            self.assertEqual(result["existing_status"], "failed")
            self.assertEqual(calls, [])
            events = json.loads(state.read_text(encoding="utf-8"))["events"]
            self.assertEqual(events[-1]["event"], "temporarily_blocked_existing_run")

    def test_manifest_file_matches_deterministic_bytes(self):
        config = collect_api_run.load_config(collect_api_run.DEFAULT_CONFIG)
        rows = create_api_manifest.make_rows(config, create_api_manifest.load_frozen_tasks())
        self.assertEqual(create_api_manifest.MANIFEST_PATH.read_bytes(), create_api_manifest.csv_bytes(rows))

    def test_freeze_record_hashes_and_excluded_smoke_artifacts(self):
        freeze_path = ROOT / "config" / "experiment_freeze_2026-09-16.json"
        freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
        self.assertTrue(freeze["freeze_record_written_before_smoke_tests"])
        self.assertFalse(freeze["official_collection_started"])
        for section in ("task_set", "model_set", "prompt_template", "official_manifest"):
            artifact = ROOT / freeze[section]["path"]
            self.assertEqual(hashlib.sha256(artifact.read_bytes()).hexdigest(), freeze[section]["sha256"])
        self.assertEqual(len(freeze["rendered_prompts"]), 30)
        for item in freeze["rendered_prompts"]:
            self.assertEqual(hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest(), item["sha256"])

        smoke_root = ROOT / "data" / "smoke" / "api"
        smoke_dirs = sorted(path for path in smoke_root.glob("SMOKE-API-001-M?") if path.is_dir())
        self.assertEqual(len(smoke_dirs), 4)
        statuses = []
        for directory in smoke_dirs:
            metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
            request = json.loads((directory / "request.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["phase"], "smoke_excluded")
            self.assertTrue(metadata["excluded_from_research_metrics"])
            self.assertEqual(request["tool_choice"], "none")
            self.assertNotIn("tools", request)
            statuses.append(metadata["collection_status"])
        self.assertEqual(Counter(statuses), Counter({"completed": 2, "failed": 2}))
        manifest_text = create_api_manifest.MANIFEST_PATH.read_text(encoding="utf-8")
        self.assertNotIn("SMOKE-API-001", manifest_text)


if __name__ == "__main__":
    unittest.main()
