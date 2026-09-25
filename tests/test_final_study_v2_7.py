"""Offline tests for the v2.7 three-condition final-study migration (no network, no writes to v2.6)."""

import csv
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import create_experiment_freeze_v2_7 as v27  # noqa: E402

V26_MANIFEST = ROOT / "manifests/api_final_v2.6.0_manifest.csv"
V26_ASSIGNMENT = ROOT / "manifests/hybrid_assignment_v1.0.0.csv"
V26_STATE = ROOT / "data/final/api_batch_state_v2.6.0.json"
V27_MANIFEST = ROOT / "manifests/api_final_v2.7.0_manifest.csv"
V27_STATE = ROOT / "data/final/collection_state_v2.7.0.json"
V27_FREEZE = ROOT / "config/experiment_freeze_v2.7.0.json"
V27_MODEL_SET = ROOT / "config/api_model_set_1.5.0.json"
FROZEN_V26 = {
    "config/experiment_freeze_v2.6.0.json": "53736d8a38fb4f497fc525cff7453693cd2ed0154b0c55a14172ea39164d5719",
    "config/api_model_set_1.4.0.json": "cba4a4ec3c785132523beb860db944b5d3b0ecacc429f8d6674889f34b35ad8c",
    "manifests/api_final_v2.6.0_manifest.csv": "b2b2750b3ae4ce96a867df14117b05c12f214760ef7036d6bbf2f78e44939b7f",
    "manifests/hybrid_assignment_v1.0.0.csv": "e4b9295b2efc0fe639092161561e915c1d0c47f9a545df2699f7fe12595dd54f",
    "prompts/prompt_template_v2.6.0.md": "8d3971d6f9f86dfd98a4b5c49c0c13d734b7f650744da682225195f2ea49b528",
    "prompts/tasks/final_2.0.0.jsonl": "ef0aff59f8a3934f65379d34036848652b7b5593f595ffa4b449a15af021546b",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class FinalStudyV27Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read_csv(V27_MANIFEST)
        cls.v26 = read_csv(V26_MANIFEST)
        cls.assignment = {row["run_id"]: row for row in read_csv(V26_ASSIGNMENT)}
        cls.state = json.loads(V27_STATE.read_text(encoding="utf-8"))
        cls.freeze = json.loads(V27_FREEZE.read_text(encoding="utf-8"))

    def test_cardinality_models_tasks_categories_repetitions(self):
        self.assertEqual(len(self.rows), 270)
        self.assertEqual(len({row["run_id"] for row in self.rows}), 270)
        self.assertEqual(Counter(row["model_condition_id"] for row in self.rows), Counter({"M1": 90, "M3": 90, "M4": 90}))
        self.assertEqual(sum(row["model_condition_id"] == "M2" for row in self.rows), 0)
        self.assertEqual(len({row["task_id"] for row in self.rows}), 30)
        categories = Counter(row["category"] for row in self.rows)
        self.assertEqual(len(categories), 6)
        self.assertEqual(set(categories.values()), {45})
        self.assertEqual(Counter(row["run_repetition"] for row in self.rows), Counter({"R01": 90, "R02": 90, "R03": 90}))
        cells = {(row["task_id"], row["model_condition_id"], row["run_repetition"]) for row in self.rows}
        self.assertEqual(len(cells), 270)

    def test_interface_assignment_inherited_140_130(self):
        self.assertEqual(Counter(row["collection_interface"] for row in self.rows), Counter({"api": 140, "manual": 130}))
        by_model = Counter((row["model_condition_id"], row["collection_interface"]) for row in self.rows)
        self.assertEqual(by_model, Counter({("M1", "api"): 40, ("M1", "manual"): 50, ("M3", "api"): 41,
                                            ("M3", "manual"): 49, ("M4", "api"): 59, ("M4", "manual"): 31}))
        for row in self.rows:
            self.assertEqual(row["collection_interface"], self.assignment[row["run_id"]]["collection_interface"])

    def test_exact_filter_membership_order_and_identities(self):
        expected = [row for row in self.v26 if row["model_condition_id"] != "M2"]
        self.assertEqual({row["run_id"] for row in self.rows},
                         {row["run_id"] for row in self.v26} - {row["run_id"] for row in self.v26 if row["model_condition_id"] == "M2"})
        self.assertEqual([row["run_id"] for row in self.rows], [row["run_id"] for row in expected])
        self.assertEqual([int(row["cohort_order"]) for row in self.rows], list(range(1, 271)))
        for new, old in zip(self.rows, expected):
            with self.subTest(run_id=new["run_id"]):
                self.assertEqual(new["source_collection_order"], old["collection_order"])
                self.assertEqual(new["source_model_set_version"], old["model_set_version"])
                self.assertEqual(new["model_set_version"], "api-model-set-1.5.0")
                for field in ("run_id", "phase", "task_id", "category", "task_set_version", "model_condition_id", "model_id",
                              "api_provider", "underlying_provider_pin", "run_repetition", "rendered_prompt_path", "expected_prompt_sha256"):
                    self.assertEqual(new[field], old[field])
        self.assertEqual(V27_MANIFEST.read_bytes(), v27.csv_bytes(v27.build_manifest_rows()))

    def test_prompt_digests_equal_v26_and_prompt_bytes(self):
        v26 = {row["run_id"]: row for row in self.v26}
        for row in self.rows:
            self.assertEqual(row["expected_prompt_sha256"], v26[row["run_id"]]["expected_prompt_sha256"])
            self.assertEqual(digest(ROOT / row["rendered_prompt_path"]), row["expected_prompt_sha256"])

    def test_model_set_is_v14_minus_m2_without_renumbering(self):
        config = json.loads(V27_MODEL_SET.read_text(encoding="utf-8"))
        source = json.loads((ROOT / "config/api_model_set_1.4.0.json").read_text(encoding="utf-8"))
        v27.validate_model_set(config)
        self.assertEqual([m["condition_id"] for m in config["models"]], ["M1", "M3", "M4"])
        self.assertEqual(config["models"], [m for m in source["models"] if m["condition_id"] != "M2"])
        self.assertEqual(config, v27.build_model_set(config["frozen_at_utc"]))
        for altered_models in (source["models"], config["models"][:2], [config["models"][0], config["models"][2], config["models"][1]]):
            with self.subTest(ids=[m["condition_id"] for m in altered_models]), self.assertRaises(ValueError):
                v27.validate_model_set(config | {"models": altered_models})
        changed = json.loads(json.dumps(config))
        changed["models"][1]["max_output_tokens"] = 1
        with self.assertRaises(ValueError):
            v27.validate_model_set(changed)
        schema = json.loads((ROOT / "schemas/api_model_set_v2_7.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["models"]["minItems"], 3)
        self.assertEqual(schema["properties"]["models"]["maxItems"], 3)
        self.assertEqual(schema["properties"]["models"]["items"]["properties"]["condition_id"]["enum"], ["M1", "M3", "M4"])

    def test_retained_api_evidence_maps_in_place_without_regeneration(self):
        entries = {entry["run_id"]: entry for entry in self.state["rows"]}
        self.assertEqual(len(entries), 270)
        api = [row for row in self.rows if row["collection_interface"] == "api"]
        self.assertEqual(len(api), 140)
        for row in api:
            entry = entries[row["run_id"]]
            directory = ROOT / "data/final/raw" / row["run_id"]
            with self.subTest(run_id=row["run_id"]):
                self.assertIn(entry["status"], {"completed", "truncated", "failed"})
                self.assertEqual(entry["evidence"]["path"], f"data/final/raw/{row['run_id']}")
                self.assertEqual(entry["evidence"]["metadata_sha256"], digest(directory / "metadata.json"))
                self.assertEqual(entry["evidence"]["prompt_sha256"], row["expected_prompt_sha256"])
                self.assertEqual(entry["evidence"]["source_model_set_version"], "api-model-set-1.4.0")
                metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
                self.assertEqual(metadata["collection_status"], entry["status"])
                self.assertEqual(metadata["run_id"], row["run_id"])
                self.assertEqual(f"R{metadata['run_repetition']:02d}", row["run_repetition"])
                response = directory / "response.md"
                self.assertEqual(entry["evidence"]["response_sha256"], digest(response) if response.exists() else None)
        self.assertEqual(list((ROOT / "data/final/raw").glob("API-v2.7-*")), [])
        self.assertEqual(self.freeze["evidence_reuse"]["mapped_rows"], 140)

    def test_collection_state_counts_and_pending_manual_boundary(self):
        self.assertEqual(Counter(entry["status"] for entry in self.state["rows"]),
                         Counter({"completed": 105, "truncated": 16, "failed": 19, "pending": 130}))
        self.assertEqual(self.state["status_counts_by_model"], {
            "M1": {"api_completed": 27, "api_failed": 3, "api_truncated": 10, "manual_pending": 50},
            "M3": {"api_completed": 36, "api_failed": 5, "manual_pending": 49},
            "M4": {"api_completed": 42, "api_failed": 11, "api_truncated": 6, "manual_pending": 31},
        })
        for entry in self.state["rows"]:
            self.assertEqual(entry["status"] == "pending", entry["collection_interface"] == "manual")
            self.assertNotEqual(entry["model_condition_id"], "M2")
        self.assertEqual(self.state["manifest_sha256"], digest(V27_MANIFEST))
        self.assertEqual(digest(V27_STATE), self.freeze["initial_collection_state"]["sha256"])

    def test_no_v26_file_changed_and_build_does_not_write_v26(self):
        for path, expected in FROZEN_V26.items():
            self.assertEqual(digest(ROOT / path), expected, path)
        for prompt in json.loads((ROOT / "config/experiment_freeze_v2.6.0.json").read_text())["rendered_prompts"]:
            self.assertEqual(digest(ROOT / prompt["path"]), prompt["sha256"])
        self.assertEqual(json.loads(V26_STATE.read_text())["manifest_sha256"], FROZEN_V26["manifests/api_final_v2.6.0_manifest.csv"])
        state_before = digest(V26_STATE)
        raw_before = {path: digest(path) for path in (ROOT / "data/final/raw").glob("API-v2.6-*/metadata.json")}
        v27.derive_collection_state(v27.build_manifest_rows(), "2026-01-01T00:00:00Z")
        v27.build_record("2026-01-01T00:00:00Z", self.state)
        self.assertEqual(digest(V26_STATE), state_before)
        self.assertEqual({path: digest(path) for path in (ROOT / "data/final/raw").glob("API-v2.6-*/metadata.json")}, raw_before)

    def test_m2_evidence_remains_present_historically(self):
        m2_rows = [row for row in self.v26 if row["model_condition_id"] == "M2"]
        self.assertEqual(len(m2_rows), 90)
        self.assertEqual(Counter(self.assignment[row["run_id"]]["collection_interface"] for row in m2_rows), Counter({"api": 40, "manual": 50}))
        preserved = self.freeze["m2_exclusion"]["preserved_evidence"]
        self.assertEqual(len(preserved), 11)
        for item in preserved:
            directory = ROOT / item["path"]
            self.assertTrue(directory.is_dir(), item["path"])
            self.assertEqual(digest(directory / "metadata.json"), item["metadata_sha256"])
            if item["response_sha256"] is not None:
                self.assertEqual(digest(directory / "response.md"), item["response_sha256"])
        ops = self.freeze["m2_exclusion"]["operational_evidence_at_freeze"]
        self.assertEqual((ops["completed"], ops["truncated"], ops["failed"], ops["planned_rows_without_artifact"]), (2, 0, 9, 79))
        self.assertFalse(self.freeze["m2_exclusion"]["result_values_used_for_exclusion"])
        self.assertFalse(self.freeze["m2_exclusion"]["final_study_metric_inclusion"])

    def test_final_study_selection_excludes_m2_and_fails_closed(self):
        rows = v27.final_study_rows()
        self.assertEqual(len(rows), 270)
        self.assertNotIn("M2", {row["model_condition_id"] for row in rows})
        with tempfile.TemporaryDirectory() as tmp:
            tampered = Path(tmp) / "manifest.csv"
            altered = [dict(row) for row in rows]
            altered[0]["model_condition_id"] = "M2"
            tampered.write_bytes(v27.csv_bytes(altered))
            with self.assertRaises(ValueError):
                v27.final_study_rows(tampered)
            tampered.write_bytes(v27.csv_bytes(rows[:-1]))
            with self.assertRaises(ValueError):
                v27.final_study_rows(tampered)

    def test_tampered_retained_evidence_is_rejected(self):
        row = next(row for row in self.rows if row["collection_interface"] == "api")
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp) / "raw"
            shutil.copytree(ROOT / "data/final/raw" / row["run_id"], raw / row["run_id"])
            (raw / row["run_id"] / "prompt.txt").write_bytes(b"different prompt")
            with patch.object(v27, "API_RAW_ROOT", raw), self.assertRaises(ValueError):
                v27.derive_collection_state([row], "2026-01-01T00:00:00Z")

    def test_freeze_is_reproducible(self):
        record = self.freeze
        rebuilt = v27.build_record(record["freeze_record_created_at_utc"], self.state)
        # Frozen M2 evidence must persist unchanged; M2 remains historical v2.6 evidence only.
        current_m2 = {item["path"]: item for item in rebuilt.pop("m2_exclusion")["preserved_evidence"]}
        for item in record["m2_exclusion"]["preserved_evidence"]:
            self.assertEqual(current_m2.get(item["path"]), item)
        self.assertEqual(rebuilt, {key: value for key, value in record.items() if key != "m2_exclusion"})
        self.assertEqual((ROOT / "docs/experiment_freeze_v2.7.0.md").read_text(encoding="utf-8"), v27.markdown(record))
        self.assertEqual(record["design_change"]["planned_observations"], {"v2.6.0": 360, "v2.7.0": 270})
        self.assertFalse(record["design_change"]["condition_ids_renumbered"])


if __name__ == "__main__":
    unittest.main()
