import contextlib
import csv
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import collect_codex_runs
import collection_common
import verify_collection
from collection_common import sha256_bytes
from init_collection_run import initialize_run


class CodexCollectionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.temporary_path = Path(self.temporary.name)
        self.raw_root = self.temporary_path / "pilot" / "raw"
        self.raw_root.mkdir(parents=True)
        self.original_pilot_root = collection_common.RAW_ROOTS["pilot"]
        collection_common.RAW_ROOTS["pilot"] = self.raw_root
        self.codex_home = self.temporary_path / "clean-codex-home"
        self.codex_home.mkdir()
        (self.codex_home / "auth.json").write_text("{}", encoding="utf-8")
        with (ROOT / "manifests/pilot_manifest.csv").open(newline="", encoding="utf-8") as handle:
            self.rows = [row for row in csv.DictReader(handle) if row["workflow"] == "codex_cli"]
        self.manifest_path = ROOT / "manifests/pilot_manifest.csv"

    def tearDown(self):
        collection_common.RAW_ROOTS["pilot"] = self.original_pilot_root
        self.temporary.cleanup()

    def successful_run(self, response=b"final response\n", stdout=b'{"type":"turn.completed"}\n', stderr=b""):
        calls = []

        def fake_run(arguments, **kwargs):
            calls.append((arguments, kwargs))
            self.assertFalse(kwargs.get("shell"))
            self.assertNotIn("resume", arguments)
            self.assertNotIn("fork", arguments)
            output_path = Path(arguments[arguments.index("--output-last-message") + 1])
            self.assertTrue(collect_codex_runs._outside_repository(output_path))
            workspace = Path(arguments[arguments.index("--cd") + 1])
            self.assertTrue(collect_codex_runs._outside_repository(workspace))
            destination = self.raw_root / self.current_row["run_id"]
            self.assertFalse((destination / "response.md").exists())
            self.assertFalse((destination / "transcript.txt").exists())
            self.assertFalse((destination / "stderr.txt").exists())
            output_path.write_bytes(response)
            return subprocess.CompletedProcess(arguments, 0, stdout=stdout, stderr=stderr)

        return fake_run, calls

    def test_success_preserves_exact_bytes_hashes_and_pinned_invocation(self):
        self.current_row = self.rows[0]
        initialize_run(self.current_row["run_id"])
        before = self.manifest_path.read_bytes()
        fake_run, calls = self.successful_run(stderr=b"diagnostic\n")
        success = collect_codex_runs.collect_codex_row(
            self.current_row,
            self.manifest_path,
            self.codex_home,
            temporary_root=self.temporary_path,
            run=fake_run,
        )
        self.assertTrue(success)
        self.assertEqual(len(calls), 1)
        arguments, kwargs = calls[0]
        self.assertEqual(kwargs["input"], (ROOT / self.current_row["rendered_prompt_path"]).read_bytes())
        self.assertEqual(arguments[0:2], ["codex", "exec"])
        for value in (
            "--ephemeral", "--ignore-user-config", "--ignore-rules", "--strict-config",
            "--skip-git-repo-check", "--json",
        ):
            self.assertIn(value, arguments)
        self.assertEqual(arguments[arguments.index("--model") + 1], "gpt-5.6-sol")
        for value in (
            'model_provider="openai"', 'model_reasoning_effort="medium"',
            'service_tier="default"', 'web_search="disabled"',
        ):
            self.assertIn(value, arguments)
        for feature in collect_codex_runs.DISABLED_FEATURES:
            self.assertIn(feature, arguments)
        self.assertEqual(arguments[-1], "-")
        directory = self.raw_root / self.current_row["run_id"]
        self.assertEqual((directory / "response.md").read_bytes(), b"final response\n")
        self.assertEqual((directory / "transcript.txt").read_bytes(), b'{"type":"turn.completed"}\n')
        self.assertEqual((directory / "stderr.txt").read_bytes(), b"diagnostic\n")
        metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["collection_status"], "completed")
        self.assertEqual(metadata["cli_exit_status"], 0)
        self.assertEqual(metadata["raw_response_sha256"], sha256_bytes(b"final response\n"))
        self.assertEqual(metadata["transcript_sha256"], sha256_bytes(b'{"type":"turn.completed"}\n'))
        self.assertEqual(metadata["stderr_sha256"], sha256_bytes(b"diagnostic\n"))
        self.assertEqual(self.manifest_path.read_bytes(), before)

    def test_new_process_shape_is_built_for_each_selected_row(self):
        seen_workspaces = set()
        for row in self.rows[:2]:
            self.current_row = row
            fake_run, calls = self.successful_run(response=f"{row['run_id']}\n".encode())
            self.assertTrue(collect_codex_runs.collect_codex_row(
                row, self.manifest_path, self.codex_home,
                temporary_root=self.temporary_path, run=fake_run,
            ))
            arguments = calls[0][0]
            seen_workspaces.add(arguments[arguments.index("--cd") + 1])
        self.assertEqual(len(seen_workspaces), 2)

    def test_nonzero_exit_preserves_failed_evidence_without_completion(self):
        self.current_row = self.rows[1]

        def failed(arguments, **kwargs):
            Path(arguments[arguments.index("--output-last-message") + 1]).write_bytes(b"partial")
            return subprocess.CompletedProcess(arguments, 7, stdout=b"events", stderr=b"failure")

        self.assertFalse(collect_codex_runs.collect_codex_row(
            self.current_row, self.manifest_path, self.codex_home,
            temporary_root=self.temporary_path, run=failed,
        ))
        directory = self.raw_root / self.current_row["run_id"]
        metadata = json.loads((directory / "metadata.json").read_text())
        self.assertEqual(metadata["collection_status"], "failed")
        self.assertEqual(metadata["cli_exit_status"], 7)
        self.assertFalse((directory / "response.md").exists())
        self.assertEqual((directory / "failed_attempts/attempt-01/response.partial.md").read_bytes(), b"partial")

    def test_timeout_stays_incomplete(self):
        self.current_row = self.rows[2]

        def timeout(arguments, **kwargs):
            raise subprocess.TimeoutExpired(arguments, 1, output=b"partial events", stderr=b"timeout")

        self.assertFalse(collect_codex_runs.collect_codex_row(
            self.current_row, self.manifest_path, self.codex_home,
            timeout_seconds=1, temporary_root=self.temporary_path, run=timeout,
        ))
        metadata = json.loads((self.raw_root / self.current_row["run_id"] / "metadata.json").read_text())
        self.assertEqual(metadata["collection_status"], "failed")
        self.assertTrue(metadata["timed_out"])

    def test_empty_response_stays_incomplete(self):
        self.current_row = self.rows[3]
        fake_run, _ = self.successful_run(response=b"")
        self.assertFalse(collect_codex_runs.collect_codex_row(
            self.current_row, self.manifest_path, self.codex_home,
            temporary_root=self.temporary_path, run=fake_run,
        ))
        metadata = json.loads((self.raw_root / self.current_row["run_id"] / "metadata.json").read_text())
        self.assertEqual(metadata["collection_status"], "failed")

    def test_completed_run_cannot_be_overwritten(self):
        row = self.rows[4]
        _, _, directory, metadata = initialize_run(row["run_id"])
        metadata["collection_status"] = "completed"
        collection_common.write_metadata(directory / "metadata.json", metadata)
        with self.assertRaisesRegex(ValueError, "completed"):
            collect_codex_runs.collect_codex_row(
                row, self.manifest_path, self.codex_home,
                temporary_root=self.temporary_path, run=lambda *args, **kwargs: None,
            )

    def test_pristine_initialized_run_can_continue(self):
        self.current_row = self.rows[5]
        initialize_run(self.current_row["run_id"])
        fake_run, _ = self.successful_run()
        self.assertTrue(collect_codex_runs.collect_codex_row(
            self.current_row, self.manifest_path, self.codex_home,
            temporary_root=self.temporary_path, run=fake_run,
        ))

    def test_preflight_uses_version_and_feature_inspection_only(self):
        calls = []

        def fake_run(arguments, **kwargs):
            calls.append(arguments)
            if arguments[-1] == "--version":
                return subprocess.CompletedProcess(arguments, 0, stdout=b"codex-cli 0.154.0\n", stderr=b"")
            lines = "".join(f"{feature} stable false\n" for feature in collect_codex_runs.DISABLED_FEATURES)
            return subprocess.CompletedProcess(arguments, 0, stdout=lines.encode(), stderr=b"")

        collect_codex_runs.preflight_codex("codex", self.codex_home, run=fake_run)
        self.assertEqual(len(calls), 2)
        self.assertNotIn("exec", calls[0])
        self.assertNotIn("exec", calls[1])

    def test_baseline_is_rejected_and_pilot_does_not_count_as_final(self):
        with self.assertRaisesRegex(ValueError, "Baseline"):
            collect_codex_runs.select_rows("final", None, None)
        self.current_row = self.rows[0]
        fake_run, _ = self.successful_run()
        self.assertTrue(collect_codex_runs.collect_codex_row(
            self.current_row, self.manifest_path, self.codex_home,
            temporary_root=self.temporary_path, run=fake_run,
        ))
        final_root = self.temporary_path / "final" / "raw"
        final_root.mkdir(parents=True)
        original_final = collection_common.RAW_ROOTS["final"]
        collection_common.RAW_ROOTS["final"] = final_root
        try:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(verify_collection.verify_phase("final"), 1)
            self.assertIn("completed: 0", output.getvalue())
        finally:
            collection_common.RAW_ROOTS["final"] = original_final

    def test_tampering_is_detected(self):
        self.current_row = self.rows[0]
        fake_run, _ = self.successful_run()
        self.assertTrue(collect_codex_runs.collect_codex_row(
            self.current_row, self.manifest_path, self.codex_home,
            temporary_root=self.temporary_path, run=fake_run,
        ))
        directory = self.raw_root / self.current_row["run_id"]
        (directory / "response.md").write_bytes(b"tampered")
        with patch.object(verify_collection, "read_manifest", return_value=([self.current_row], self.manifest_path)):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(verify_collection.verify_phase("pilot"), 1)
            self.assertIn("completed: 0", output.getvalue())

    def test_clean_codex_home_validation(self):
        self.assertEqual(collect_codex_runs.validate_codex_home(self.codex_home), self.codex_home.resolve())
        (self.codex_home / "config.toml").write_text("", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "not clean"):
            collect_codex_runs.validate_codex_home(self.codex_home)


if __name__ == "__main__":
    unittest.main()
