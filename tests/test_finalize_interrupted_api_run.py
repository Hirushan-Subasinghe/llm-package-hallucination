import csv
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import finalize_interrupted_api_run as recovery


RUN_ID = "API-v2.6-PKI-CRYPTO-04-M4-R01"


class InterruptedApiRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.raw = root / "raw"
        self.audit = root / "audits"
        self.manifest = root / "manifest.csv"
        prompt = b"preserved prompt\n"
        row = {
            "run_id": RUN_ID, "collection_order": "36", "phase": "final", "task_id": "PKI-CRYPTO-04",
            "category": "PKI-CRYPTO", "task_set_version": "final-2.0.0", "model_set_version": "api-model-set-1.4.0",
            "model_condition_id": "M4", "api_provider": "OpenRouter", "model_id": "preserved/model",
            "run_repetition": "R01", "expected_prompt_sha256": hashlib.sha256(prompt).hexdigest(),
        }
        with self.manifest.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=row.keys())
            writer.writeheader(); writer.writerow(row)
        self.directory = self.raw / RUN_ID
        self.directory.mkdir(parents=True)
        (self.directory / "prompt.txt").write_bytes(prompt)
        (self.directory / "request.json").write_bytes(b'{"preserved":true}')
        self.metadata = {
            "run_id": RUN_ID, "collection_order": 36, "collection_status": "requesting",
            "phase": "final", "task_id": "PKI-CRYPTO-04", "category": "PKI-CRYPTO",
            "task_set_version": "final-2.0.0", "model_set_version": "api-model-set-1.4.0",
            "model_condition_id": "M4", "api_provider": "OpenRouter", "prompt_path": "prompt.txt",
            "request_path": "request.json", "prompt_sha256": hashlib.sha256(prompt).hexdigest(),
            "run_repetition": 1,
            "request_sha256": hashlib.sha256((self.directory / "request.json").read_bytes()).hexdigest(),
            "generation_started_at_utc": "2026-09-22T04:54:12.132229Z", "requested_model_id": "preserved/model",
        }
        (self.directory / "metadata.json").write_text(json.dumps(self.metadata), encoding="utf-8")
        self.manifest_before = self.manifest.read_bytes()

    def recover(self):
        return recovery.finalize_interrupted_run(RUN_ID, manifest=self.manifest, raw_root=self.raw, audit_directory=self.audit)

    def test_stranded_request_is_finalized_offline_and_audited(self):
        with patch("requests.post", side_effect=AssertionError("network must not be called")) as post:
            result = self.recover()
        post.assert_not_called()
        metadata = json.loads((self.directory / "metadata.json").read_text())
        self.assertEqual(metadata["collection_status"], "failed")
        self.assertEqual(metadata["failure_reason"], recovery.FAILURE_REASON)
        self.assertTrue(metadata["generation_ended_at_utc"].endswith("Z"))
        self.assertEqual(metadata["generation_started_at_utc"], self.metadata["generation_started_at_utc"])
        self.assertIn(recovery.OPERATIONAL_NOTE, metadata["protocol_deviations"])
        self.assertNotIn("response_completion_status", metadata)
        self.assertNotIn("finish_reason", metadata)
        self.assertFalse((self.directory / "attempts").exists())
        self.assertFalse((self.directory / "provider_response.json").exists())
        self.assertFalse((self.directory / "response.md").exists())
        self.assertTrue(Path(result["audit_path"]).is_file())
        self.assertEqual(self.manifest.read_bytes(), self.manifest_before)

    def test_completed_truncated_and_failed_cannot_be_overwritten(self):
        for status in ("completed", "truncated", "failed"):
            with self.subTest(status=status):
                changed = dict(self.metadata, collection_status=status)
                (self.directory / "metadata.json").write_text(json.dumps(changed), encoding="utf-8")
                before = (self.directory / "metadata.json").read_bytes()
                with self.assertRaises(ValueError): self.recover()
                self.assertEqual((self.directory / "metadata.json").read_bytes(), before)
                self.assertFalse(self.audit.exists())

    def test_response_evidence_refuses_conversion(self):
        (self.directory / "provider_response.json").write_bytes(b'{"choices":[]}')
        before = (self.directory / "metadata.json").read_bytes()
        with self.assertRaises(ValueError): self.recover()
        self.assertEqual((self.directory / "metadata.json").read_bytes(), before)
        self.assertFalse(self.audit.exists())

    def test_other_v2_6_raw_files_and_manifest_are_unchanged(self):
        other = self.raw / "API-v2.6-OTHER-M1-R01"
        other.mkdir(); (other / "metadata.json").write_bytes(b"other")
        before = recovery.raw_hashes(self.raw)
        self.recover()
        after = recovery.raw_hashes(self.raw)
        self.assertEqual({k: v for k, v in before.items() if not k.startswith(RUN_ID + "/metadata.json")}, {k: v for k, v in after.items() if not k.startswith(RUN_ID + "/metadata.json")})
        self.assertEqual(self.manifest.read_bytes(), self.manifest_before)


if __name__ == "__main__":
    unittest.main()
