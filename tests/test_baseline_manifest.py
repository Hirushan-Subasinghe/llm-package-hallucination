import itertools
import json
from pathlib import Path
import tempfile
import unittest

from experiment.baseline_manifest import (
    BaselineManifestError,
    RUNS,
    WORKFLOWS,
    build_manifest_records,
    serialize_manifest,
    write_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "prompts/tasks/final_1.0.0.jsonl"
TEMPLATE = ROOT / "prompts/templates/master_prompt_v1.0.0.md"


class BaselineManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.records = build_manifest_records(TASKS, TEMPLATE)

    def test_locked_cartesian_product(self) -> None:
        self.assertEqual(len(self.records), 360)
        self.assertEqual(len({r["task_id"] for r in self.records}), 30)
        self.assertEqual({r["workflow"] for r in self.records}, {w[1] for w in WORKFLOWS})
        self.assertEqual({r["run_number"] for r in self.records}, set(RUNS))
        expected = set(itertools.product(
            {r["task_id"] for r in self.records},
            {w[1] for w in WORKFLOWS},
            RUNS,
        ))
        actual = {(r["task_id"], r["workflow"], r["run_number"]) for r in self.records}
        self.assertEqual(actual, expected)

    def test_unique_deterministic_generation_ids(self) -> None:
        ids = [record["generation_id"] for record in self.records]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids[0], "chatgpt-web-API-001-R1")
        self.assertEqual(ids[-1], "antigravity-cli-gemini-SEC-005-R3")

    def test_baseline_only_and_initially_pending(self) -> None:
        self.assertEqual({r["experiment_condition"] for r in self.records}, {"baseline"})
        self.assertEqual({r["status"] for r in self.records}, {"PENDING"})
        self.assertNotIn("persistence", serialize_manifest(self.records).decode())

    def test_repeated_build_is_byte_identical(self) -> None:
        self.assertEqual(
            serialize_manifest(self.records),
            serialize_manifest(build_manifest_records(TASKS, TEMPLATE)),
        )

    def test_existing_different_manifest_is_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.jsonl"
            path.write_text("different\n", encoding="utf-8")
            with self.assertRaises(BaselineManifestError):
                write_manifest(path, serialize_manifest(self.records))
            self.assertEqual(path.read_text(encoding="utf-8"), "different\n")


if __name__ == "__main__":
    unittest.main()
