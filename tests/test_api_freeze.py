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
import create_experiment_freeze
import render_api_prompts


class APIFreezeTests(unittest.TestCase):
    def test_frozen_task_and_rendered_prompt_shape(self):
        tasks = render_api_prompts.load_tasks()
        # Verify v2.3 rendered prompts
        rendered_v2_3 = render_api_prompts.expected_rendered(render_api_prompts.DEFAULT_TEMPLATE_PATH)
        self.assertEqual(len(tasks), 30)
        self.assertEqual(len(rendered_v2_3), 30)
        for task in tasks:
            path = render_api_prompts.DEFAULT_RENDERED_DIR / f"{task['task_id']}.txt"
            self.assertEqual(path.read_bytes(), rendered_v2_3[task["task_id"]])

        # Verify historical v2.2 prompts remain intact
        rendered_v2_2 = render_api_prompts.expected_rendered(render_api_prompts.TEMPLATE_PATH_V2_2)
        for task in tasks:
            path = render_api_prompts.RENDERED_DIR_V2_2 / f"{task['task_id']}.txt"
            self.assertEqual(path.read_bytes(), rendered_v2_2[task["task_id"]])

        # Verify historical v2.1 prompts also remain intact
        rendered_v2_1 = render_api_prompts.expected_rendered(render_api_prompts.TEMPLATE_PATH_V2_1)
        self.assertEqual(len(rendered_v2_1), 30)
        for task in tasks:
            path = render_api_prompts.RENDERED_DIR_V2_1 / f"{task['task_id']}.txt"
            self.assertEqual(path.read_bytes(), rendered_v2_1[task["task_id"]])

        # Verify historical v2.0 prompts also remain intact
        rendered_v2_0 = render_api_prompts.expected_rendered(ROOT / "prompts" / "prompt_template_v2.0.0.md")
        for task in tasks:
            path = ROOT / "data" / "generated_prompts" / "v2.0.0" / f"{task['task_id']}.txt"
            self.assertEqual(path.read_bytes(), rendered_v2_0[task["task_id"]])

    def test_official_v2_3_manifest_counts_hashes_and_rotations(self):
        config = collect_api_run.load_config(collect_api_run.DEFAULT_CONFIG)
        rows = create_api_manifest.make_rows(
            config,
            create_api_manifest.load_frozen_tasks(),
            rendered_dir=create_api_manifest.DEFAULT_RENDERED_DIR,
            run_prefix="API-v2.3",
        )
        self.assertEqual(len(rows), 360)
        self.assertEqual(len({row["run_id"] for row in rows}), 360)
        self.assertEqual(Counter(row["model_condition_id"] for row in rows), Counter({model: 90 for model in ("M1", "M2", "M3", "M4")}))
        self.assertEqual(Counter(row["run_repetition"] for row in rows), Counter({rep: 120 for rep in ("R01", "R02", "R03")}))
        self.assertEqual(Counter(row["category"] for row in rows), Counter({category: 60 for category in ("AUTH-FED", "PKI-CRYPTO", "DOC-BINARY", "ENT-INT", "DATA-ADV", "DIST-OBS")}))
        self.assertTrue(all(row["collection_status"] == "pending" for row in rows))
        self.assertEqual([row["model_condition_id"] for row in rows[:4]], ["M1", "M2", "M3", "M4"])
        self.assertEqual([row["model_condition_id"] for row in rows[4:8]], ["M2", "M3", "M4", "M1"])
        self.assertEqual([row["model_condition_id"] for row in rows[120:124]], ["M2", "M3", "M4", "M1"])
        self.assertTrue(all(row["run_id"].startswith("API-v2.3-") for row in rows))
        for row in rows:
            prompt = ROOT / row["rendered_prompt_path"]
            self.assertEqual(hashlib.sha256(prompt.read_bytes()).hexdigest(), row["expected_prompt_sha256"])

    def test_batch_dry_run_is_sequential_and_non_mutating(self):
        config = collect_api_run.load_config(collect_api_run.DEFAULT_CONFIG)
        rows = collect_api_batch.ordered_rows(create_api_manifest.DEFAULT_MANIFEST_PATH)
        with tempfile.TemporaryDirectory() as temporary:
            state = Path(temporary) / "state.json"
            raw = Path(temporary) / "raw"
            result = collect_api_batch.run_batch(
                config,
                rows,
                manifest_hash=hashlib.sha256(create_api_manifest.DEFAULT_MANIFEST_PATH.read_bytes()).hexdigest(),
                state_path=state,
                raw_root=raw,
                dry_run=True,
            )
            self.assertEqual(result["collection_order"], 1)
            self.assertEqual(result["next_run_id"], rows[0]["run_id"])
            self.assertEqual(result["next_run_id"], "API-v2.3-AUTH-FED-01-M1-R01")
            self.assertEqual(result["wait_seconds"], 0)
            self.assertFalse(state.exists())
            self.assertFalse(raw.exists())

    def test_batch_stops_at_existing_incomplete_row_to_preserve_order(self):
        config = collect_api_run.load_config(collect_api_run.DEFAULT_CONFIG)
        rows = collect_api_batch.ordered_rows(create_api_manifest.DEFAULT_MANIFEST_PATH)
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
                manifest_hash=hashlib.sha256(create_api_manifest.DEFAULT_MANIFEST_PATH.read_bytes()).hexdigest(),
                state_path=state,
                raw_root=raw,
                collector=lambda *args, **kwargs: calls.append((args, kwargs)),
            )
            self.assertEqual(result["blocked_collection_order"], 1)
            self.assertEqual(result["existing_status"], "failed")
            self.assertEqual(calls, [])
            events = json.loads(state.read_text(encoding="utf-8"))["events"]
            self.assertEqual(events[-1]["event"], "temporarily_blocked_existing_run")

    def test_manifest_files_match_deterministic_bytes(self):
        config = collect_api_run.load_config(collect_api_run.DEFAULT_CONFIG)
        tasks = create_api_manifest.load_frozen_tasks()

        # Test v2.3
        rows_v2_3 = create_api_manifest.make_rows(
            config,
            tasks,
            rendered_dir=create_api_manifest.DEFAULT_RENDERED_DIR,
            run_prefix="API-v2.3",
        )
        self.assertEqual(create_api_manifest.DEFAULT_MANIFEST_PATH.read_bytes(), create_api_manifest.csv_bytes(rows_v2_3))

        # Test historical v2.2
        config_v2_2 = collect_api_run.load_config(collect_api_run.CONFIG_V2_2)
        rows_v2_2 = create_api_manifest.make_rows(config_v2_2, tasks, rendered_dir=create_api_manifest.RENDERED_DIR_V2_2, run_prefix="API-v2.2")
        self.assertEqual(create_api_manifest.MANIFEST_PATH_V2_2.read_bytes(), create_api_manifest.csv_bytes(rows_v2_2))

        # Test v2.1 historical
        config_v2_0 = collect_api_run.load_config(collect_api_run.CONFIG_V2_0)
        rows_v2_1 = create_api_manifest.make_rows(
            config_v2_0,
            tasks,
            rendered_dir=create_api_manifest.RENDERED_DIR_V2_1,
            run_prefix="API-v2.1",
        )
        self.assertEqual(create_api_manifest.MANIFEST_PATH_V2_1.read_bytes(), create_api_manifest.csv_bytes(rows_v2_1))

        # Test v2.0 historical
        rows_v2_0 = create_api_manifest.make_rows(
            config_v2_0,
            tasks,
            rendered_dir=create_api_manifest.RENDERED_DIR_V2_0,
            run_prefix="API",
        )
        self.assertEqual(create_api_manifest.MANIFEST_PATH_V2_0.read_bytes(), create_api_manifest.csv_bytes(rows_v2_0))

    def test_freeze_record_v2_3_hashes_and_zero_observations(self):
        freeze_path = ROOT / "config" / "experiment_freeze_v2.3.0.json"
        freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
        self.assertFalse(freeze["official_v2_3_collection_started"])
        self.assertEqual(freeze["official_v2_3_observations_count"], 0)
        self.assertEqual(freeze["freeze_record_version"], "experiment-freeze-v2.3.0")
        self.assertEqual(freeze["sampling_parameters"]["max_output_tokens"], 12000)
        for section in ("task_set", "model_set", "prompt_template", "official_manifest"):
            artifact = ROOT / freeze[section]["path"]
            self.assertEqual(hashlib.sha256(artifact.read_bytes()).hexdigest(), freeze[section]["sha256"])
        self.assertEqual(len(freeze["rendered_prompts"]), 30)
        for item in freeze["rendered_prompts"]:
            self.assertEqual(hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest(), item["sha256"])
        for item in freeze["schemas"]:
            self.assertEqual(hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest(), item["sha256"])

        # Check markdown freeze documentation consistency
        md_path = ROOT / "docs" / "experiment_freeze_v2.3.0.md"
        self.assertTrue(md_path.exists())
        self.assertEqual(md_path.read_text(encoding="utf-8"), create_experiment_freeze.markdown_v2_3(freeze))
        self.assertIn(f"- Model set `{freeze['model_set']['version']}`: `{freeze['model_set']['sha256']}` (`{freeze['model_set']['path']}`)", md_path.read_text(encoding="utf-8"))
        self.assertIn("api-model-set-1.2.0", md_path.read_text(encoding="utf-8"))

        # v2.3 observations are now frozen historical evidence.
        raw_root = ROOT / "data" / "final" / "raw"
        self.assertEqual(len(list(raw_root.glob("API-v2.3-*"))), 8)
        failed_v2_3 = raw_root / "API-v2.3-AUTH-FED-02-M1-R01"
        self.assertEqual(
            json.loads((failed_v2_3 / "metadata.json").read_text(encoding="utf-8"))["collection_status"],
            "failed",
        )

        # v2.2 was prospectively stopped after ten preserved observations.
        v2_2_runs = list(raw_root.glob("API-v2.2-*"))
        self.assertEqual(len(v2_2_runs), 10)
        self.assertEqual(freeze["historical_v2_2_context"]["final_inventory"], {"planned": 360, "completed": 6, "truncated": 4, "pending": 350, "total_collected_observations": 10})
        v2_1_m1 = raw_root / "API-v2.1-AUTH-FED-01-M1-R01"
        v2_1_m2 = raw_root / "API-v2.1-AUTH-FED-01-M2-R01"
        v2_1_m3 = raw_root / "API-v2.1-AUTH-FED-01-M3-R01"
        v2_1_m4 = raw_root / "API-v2.1-AUTH-FED-01-M4-R01"
        self.assertTrue(v2_1_m1.is_dir())
        self.assertTrue(v2_1_m2.is_dir())
        self.assertTrue(v2_1_m3.is_dir())
        self.assertTrue(v2_1_m4.is_dir())
        self.assertTrue((raw_root / "API-AUTH-FED-01-M1-R01").is_dir())
        self.assertTrue((raw_root / "API-AUTH-FED-01-M2-R01").is_dir())

    def test_v2_4_freeze_is_fresh_and_preserves_input_bytes(self):
        import create_experiment_freeze_v2_4
        freeze_path = ROOT / "config" / "experiment_freeze_v2.4.0.json"
        freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
        self.assertEqual(freeze["dataset_strategy"], "fresh_separate_360_observation_experiment")
        self.assertTrue(freeze["failure_policy"]["continue_after_preserved_failure"])
        self.assertFalse(freeze["failure_policy"]["retry_failed_observation"])
        self.assertFalse(freeze["failure_policy"]["substitute_model_or_provider"])
        self.assertTrue(freeze["failure_policy"]["exclude_from_primary_shr_phr_denominators"])
        self.assertEqual(freeze["official_manifest"]["row_count"], 360)
        self.assertEqual(freeze["official_manifest"]["pending_rows"], 360)
        self.assertEqual(freeze["official_manifest"]["rows_per_model"], {"M1": 90, "M2": 90, "M3": 90, "M4": 90})
        self.assertEqual(freeze["official_manifest"]["rows_per_repetition"], {"R01": 120, "R02": 120, "R03": 120})
        self.assertEqual(freeze["official_manifest"]["rows_per_category"], {
            "AUTH-FED": 60, "DATA-ADV": 60, "DIST-OBS": 60, "DOC-BINARY": 60, "ENT-INT": 60, "PKI-CRYPTO": 60
        })
        manifest_path = ROOT / "manifests" / "api_final_v2.4.0_manifest.csv"
        manifest_bytes = manifest_path.read_bytes()
        self.assertEqual(hashlib.sha256(manifest_bytes).hexdigest(), freeze["official_manifest"]["sha256"])
        with manifest_path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 360)
        self.assertTrue(all(r["collection_status"] == "pending" for r in rows))
        self.assertTrue(all(r["run_id"].startswith("API-v2.4-") for r in rows))

        for item in freeze["rendered_prompts"]:
            v24 = ROOT / item["path"]
            v23 = ROOT / item["path"].replace("v2.4.0", "v2.3.0")
            self.assertEqual(v24.read_bytes(), v23.read_bytes())
            self.assertEqual(hashlib.sha256(v24.read_bytes()).hexdigest(), item["sha256"])
        self.assertEqual(
            (ROOT / "prompts" / "prompt_template_v2.4.0.md").read_bytes(),
            (ROOT / "prompts" / "prompt_template_v2.3.0.md").read_bytes(),
        )

        # Verify initial batch state file for v2.4
        state_path = ROOT / "data" / "final" / "api_batch_state_v2.4.0.json"
        self.assertTrue(state_path.exists())
        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["collection_status"], "ready_for_prospective_collection")
        # The initial state has since advanced through official v2.4 collection.
        self.assertIsInstance(state["events"], list)
        self.assertGreater(len(state["events"]), 0)
        self.assertEqual(state["manifest_sha256"], freeze["official_manifest"]["sha256"])

        # Verify markdown documentation
        md_path = ROOT / "docs" / "experiment_freeze_v2.4.0.md"
        self.assertTrue(md_path.exists())
        self.assertEqual(md_path.read_text(encoding="utf-8"), create_experiment_freeze_v2_4.markdown(freeze))

    def test_freeze_record_v2_1_historical_context_and_preserved_observations(self):
        freeze_path = ROOT / "config" / "experiment_freeze_v2.1.0.json"
        freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
        self.assertEqual(freeze["freeze_record_version"], "experiment-freeze-v2.1.0")
        for section in ("task_set", "model_set", "prompt_template", "official_manifest"):
            artifact = ROOT / freeze[section]["path"]
            self.assertEqual(hashlib.sha256(artifact.read_bytes()).hexdigest(), freeze[section]["sha256"])
        self.assertEqual(len(freeze["rendered_prompts"]), 30)
        for item in freeze["rendered_prompts"]:
            self.assertEqual(hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest(), item["sha256"])

        raw_root = ROOT / "data" / "final" / "raw"
        v2_1_runs = sorted(path.name for path in raw_root.glob("API-v2.1-*"))
        self.assertEqual(len(v2_1_runs), 4)
        self.assertEqual(v2_1_runs, [
            "API-v2.1-AUTH-FED-01-M1-R01",
            "API-v2.1-AUTH-FED-01-M2-R01",
            "API-v2.1-AUTH-FED-01-M3-R01",
            "API-v2.1-AUTH-FED-01-M4-R01",
        ])

    def test_freeze_record_v2_0_historical_hashes_and_excluded_smoke_artifacts(self):
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
        manifest_text = create_api_manifest.MANIFEST_PATH_V2_0.read_text(encoding="utf-8")
        self.assertNotIn("SMOKE-API-001", manifest_text)


if __name__ == "__main__":
    unittest.main()
