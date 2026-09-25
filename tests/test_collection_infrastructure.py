import csv
import contextlib
import hashlib
import io
import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import init_collection_run
import finalize_collection_run
import verify_collection
from collection_common import MANIFESTS, sha256_bytes


class CollectionInfrastructureTests(unittest.TestCase):
    def test_rendered_prompts_and_manifests(self):
        tasks = json.loads((ROOT / "prompts/prompts_v1.0.0.json").read_text(encoding="utf-8"))
        rendered = ROOT / "data/generated_prompts/v1.0.0"
        self.assertEqual(len(list(rendered.glob("*.txt"))), 30)
        self.assertTrue(all(task["task_description"] in (rendered / f"{task['prompt_id']}.txt").read_text(encoding="utf-8") for task in tasks))
        self.assertTrue(all("[TASK_DESCRIPTION]" not in path.read_text(encoding="utf-8") for path in rendered.glob("*.txt")))
        for manifest, expected in (("pilot_manifest.csv", 24), ("baseline_manifest.csv", 360)):
            with (ROOT / "manifests" / manifest).open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), expected)
            self.assertEqual(len({row["run_id"] for row in rows}), expected)
            self.assertTrue(all(row["collection_status"] == "pending" for row in rows))
            self.assertTrue(all(row["expected_prompt_sha256"] == sha256_bytes((ROOT / row["rendered_prompt_path"]).read_bytes()) for row in rows))
        with (ROOT / "manifests/baseline_manifest.csv").open(newline="", encoding="utf-8") as handle:
            baseline = list(csv.DictReader(handle))
        self.assertEqual(Counter(row["category"] for row in baseline), Counter({
            "authentication_authorization": 60,
            "database_connectivity": 60,
            "file_processing": 60,
            "api_development": 60,
            "security_encryption": 60,
            "logging_caching": 60,
        }))
        self.assertEqual(Counter(row["workflow"] for row in baseline), Counter({
            "chatgpt_web": 90,
            "gemini_web": 90,
            "codex_cli": 90,
            "antigravity_cli": 90,
        }))
        self.assertEqual(Counter(row["run_number"] for row in baseline), Counter({"01": 120, "02": 120, "03": 120}))

    def test_pilot_selection_and_counts(self):
        expected_tasks = {"AUTH-04", "DB-03", "FILE-02", "API-04", "SEC-03", "LOG-04"}
        with (ROOT / "manifests/pilot_manifest.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual({row["prompt_id"] for row in rows}, expected_tasks)
        self.assertEqual({row["workflow"] for row in rows}, {"chatgpt_web", "gemini_web", "codex_cli", "antigravity_cli"})
        self.assertEqual({row["run_number"] for row in rows}, {"01"})

    def test_initializer_rejects_unknown_run(self):
        with patch.object(sys, "argv", ["init_collection_run.py", "UNKNOWN-RUN"]):
            with patch("builtins.print"):
                self.assertEqual(init_collection_run.main(), 1)

    def test_initializer_does_not_overwrite_completed_data(self):
        row = {
            "run_id": "TEST-RUN",
            "phase": "pilot",
        }
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "run"
            directory.mkdir()
            (directory / "metadata.json").write_text(json.dumps({"collection_status": "completed"}), encoding="utf-8")
            with patch.object(sys, "argv", ["init_collection_run.py", "TEST-RUN"]), patch.object(init_collection_run, "find_run", return_value=(row, MANIFESTS["pilot"])), patch.object(init_collection_run, "run_directory", return_value=directory):
                with patch("builtins.print"):
                    self.assertEqual(init_collection_run.main(), 1)

    def test_renderer_resets_manifest_status_to_planned_pending(self):
        import render_generation_prompts
        tasks = render_generation_prompts.load_tasks()
        rendered = {
            task["prompt_id"]: (
                f"data/generated_prompts/v1.0.0/{task['prompt_id']}.txt",
                sha256_bytes((ROOT / f"data/generated_prompts/v1.0.0/{task['prompt_id']}.txt").read_bytes()),
            )
            for task in tasks
        }
        with patch.object(render_generation_prompts, "render_tasks", return_value=rendered), patch.object(render_generation_prompts, "write_manifest") as writer:
            self.assertEqual(render_generation_prompts.main(), 0)
        written_rows = [call.args[1] for call in writer.call_args_list]
        self.assertEqual([len(rows) for rows in written_rows], [24, 360])
        self.assertTrue(all(row["collection_status"] == "pending" for rows in written_rows for row in rows))

    def test_initialize_finalize_preserves_manifest_and_verifier_uses_metadata(self):
        run_id = "PILOT-AUTH-04-chatgpt_web-R01"
        with (ROOT / "manifests/pilot_manifest.csv").open(newline="", encoding="utf-8") as handle:
            row = next(item for item in csv.DictReader(handle) if item["run_id"] == run_id)
        manifest_path = ROOT / "manifests/pilot_manifest.csv"
        before_hash = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / run_id
            with patch.object(sys, "argv", ["init_collection_run.py", run_id]), patch.object(init_collection_run, "run_directory", return_value=directory):
                self.assertEqual(init_collection_run.main(), 0)
            (directory / "response.md").write_text("Temporary synthetic capture.\n", encoding="utf-8")
            with patch.object(sys, "argv", ["finalize_collection_run.py", run_id]), patch.object(finalize_collection_run, "run_directory", return_value=directory):
                self.assertEqual(finalize_collection_run.main(), 0)
            self.assertEqual(hashlib.sha256(manifest_path.read_bytes()).hexdigest(), before_hash)
            metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["collection_status"], "completed")
            with patch.object(verify_collection, "read_manifest", return_value=([row], manifest_path)), patch.object(verify_collection, "run_directory", return_value=directory):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(verify_collection.verify_phase("pilot"), 0)
                self.assertIn("completed: 1", output.getvalue())


if __name__ == "__main__":
    unittest.main()
