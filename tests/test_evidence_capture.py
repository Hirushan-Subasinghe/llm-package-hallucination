import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from experiment.baseline_manifest import build_manifest_records, serialize_manifest
from experiment.evidence_capture import CaptureError, capture_generation, progress, record_failure

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "prompts/tasks/final_1.0.0.jsonl"
TEMPLATE = ROOT / "prompts/templates/master_prompt_v1.0.0.md"
GENERATION_ID = "chatgpt-web-AUTH-001-R1"


class EvidenceCaptureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.manifest = self.root / "data/manifests/baseline.jsonl"
        self.manifest.parent.mkdir(parents=True)
        self.manifest.write_bytes(serialize_manifest(build_manifest_records(TASKS, TEMPLATE)))
        self.input = self.root / "response.bin"
        self.raw_bytes = b"```js\r\nconst x = 1;  \r\n```\x00\xff"
        self.input.write_bytes(self.raw_bytes)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def capture(self, **options):
        return capture_generation(
            self.manifest,
            self.root / "data/raw",
            GENERATION_ID,
            self.input,
            "2026-09-08T10:30:00+05:30",
            **options,
        )

    def test_valid_capture_preserves_bytes_hash_and_identity(self) -> None:
        metadata = self.capture(visible_model_version="visible-test-version")
        raw_path = self.root / "data" / metadata["raw_output_path"]
        self.assertEqual(raw_path.read_bytes(), self.raw_bytes)
        self.assertEqual(metadata["raw_output_sha256"], hashlib.sha256(self.raw_bytes).hexdigest())
        self.assertEqual(metadata["task_id"], "AUTH-001")
        self.assertEqual(metadata["workflow"], "ChatGPT Web")
        self.assertEqual(metadata["run_number"], 1)
        self.assertEqual(metadata["visible_model_version"], "visible-test-version")
        stored = json.loads((self.root / "data/metadata/baseline/chatgpt-web/AUTH-001/R1.json").read_text())
        self.assertEqual(stored, metadata)
        self.assertEqual(progress(self.manifest, self.root / "data/metadata/baseline")["COMPLETED"], 1)

    def test_absent_model_version_is_null(self) -> None:
        self.assertIsNone(self.capture()["visible_model_version"])

    def test_unknown_generation_is_rejected(self) -> None:
        with self.assertRaisesRegex(CaptureError, "unknown"):
            capture_generation(
                self.manifest, self.root / "data/raw", "unknown", self.input,
                "2026-09-08T10:30:00+05:30",
            )

    def test_overwrite_is_rejected(self) -> None:
        self.capture()
        with self.assertRaisesRegex(CaptureError, "already has"):
            self.capture()

    def test_failure_attempts_are_unique_append_only_and_do_not_complete(self) -> None:
        for suffix in ("a", "b"):
            record_failure(
                self.manifest,
                self.root / "data/failed",
                GENERATION_ID,
                f"attempt-{suffix}",
                "2026-09-08T10:30:00+05:30",
                "provider-timeout",
            )
        failures = list((self.root / "data/failed/baseline").glob("*.json"))
        self.assertEqual(len(failures), 2)
        self.assertEqual(progress(self.manifest, self.root / "data/metadata/baseline")["COMPLETED"], 0)
        with self.assertRaisesRegex(CaptureError, "overwrite"):
            record_failure(
                self.manifest,
                self.root / "data/failed",
                GENERATION_ID,
                "attempt-a",
                "2026-09-08T10:31:00+05:30",
                "network-service-error",
            )
        self.assertEqual(len(list((self.root / "data/failed/baseline").glob("*.json"))), 2)


if __name__ == "__main__":
    unittest.main()
