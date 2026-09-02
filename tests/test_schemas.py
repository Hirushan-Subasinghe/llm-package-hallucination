import copy
import hashlib
from pathlib import Path
import unittest

from experiment.schema_validation import (
    SchemaValidationError,
    load_schema,
    validate_generation_metadata,
    validate_task,
    validate_task_records,
)
from experiment.prompt_renderer import read_tasks


ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "prompts/tasks/pilot_samples.jsonl"


def metadata() -> dict:
    return {
        "experiment_run_id": "run-2026-01",
        "generation_id": "generation-AUTH-001-r1",
        "attempt_id": "attempt-AUTH-001-r1-a1",
        "task_id": "AUTH-001",
        "repetition": 1,
        "task_set_version": "pilot-0.1.0",
        "template_version": "0.1.0",
        "canonical_prompt_sha256": hashlib.sha256(b"prompt").hexdigest(),
        "tool_name": "Codex CLI",
        "provider_name": "OpenAI",
        "model_name": "recorded-model",
        "model_selection_mode": "fixed",
        "workflow_type": "agentic-coding",
        "interface": "cli",
        "cli_version": "1.0.0",
        "runner_version": "0.1.0",
        "experiment_protocol_version": "0.1.0",
        "timestamp_started": "2026-09-02T10:00:00+05:30",
        "timestamp_finished": "2026-09-02T10:01:00+05:30",
        "timezone": "Asia/Colombo",
        "execution_duration_ms": 60000,
        "workspace_id": "workspace-AUTH-001-r1",
        "workspace_provenance": "fresh-temporary",
        "workspace_base_version": "base-0.1.0",
        "filesystem_access": "isolated-workspace-only",
        "shell_access": "enabled",
        "network_policy": "restricted",
        "package_install_policy": "blocked-and-recorded",
        "process_exit_code": 0,
        "timeout": False,
        "success": True,
        "failure_category": None,
        "raw_stdout_path": "data/raw/openai/generation.txt",
        "raw_stderr_path": "data/raw/openai/stderr.txt",
        "raw_response_path": "data/raw/openai/response.txt",
        "raw_response_sha256": hashlib.sha256(b"response").hexdigest(),
        "raw_response_bytes": 8,
        "files_created": ["package.json"],
        "files_modified": [],
        "files_deleted": [],
        "commands_attempted": [],
        "package_install_attempted": False,
        "package_install_commands": [],
    }


class SchemaTests(unittest.TestCase):
    def test_schema_documents_are_valid_json(self):
        for name in ("task.schema.json", "generation_metadata.schema.json", "controlled_vocabularies.json"):
            with self.subTest(name=name):
                document = load_schema(name)
                self.assertEqual(document["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_valid_pilot_compatible_tasks_pass(self):
        tasks = read_tasks(PILOT)
        self.assertEqual(len(validate_task_records(tasks)), 6)

    def test_invalid_task_id_fails(self):
        task = read_tasks(PILOT)[0].copy()
        task["task_id"] = "AUTH-1"
        with self.assertRaises(SchemaValidationError): validate_task(task)

    def test_unknown_category_fails(self):
        task = read_tasks(PILOT)[0].copy()
        task["category"] = "Other"
        with self.assertRaises(SchemaValidationError): validate_task(task)

    def test_duplicate_ids_fail(self):
        tasks = read_tasks(PILOT)[:2]
        tasks[1] = copy.deepcopy(tasks[0])
        with self.assertRaises(SchemaValidationError): validate_task_records(tasks)

    def test_missing_required_field_fails(self):
        task = read_tasks(PILOT)[0].copy()
        del task["task_description"]
        with self.assertRaises(SchemaValidationError): validate_task(task)

    def test_invalid_ecosystem_fails(self):
        task = read_tasks(PILOT)[0].copy()
        task["ecosystem"] = "python"
        with self.assertRaises(SchemaValidationError): validate_task(task)

    def test_invalid_status_fails(self):
        task = read_tasks(PILOT)[0].copy()
        task["status"] = "observed"
        with self.assertRaises(SchemaValidationError): validate_task(task)

    def test_expected_result_fields_are_rejected(self):
        task = read_tasks(PILOT)[0].copy()
        task["expected_package_names"] = []
        with self.assertRaises(SchemaValidationError): validate_task(task)

    def test_valid_generation_metadata_passes(self):
        self.assertEqual(validate_generation_metadata(metadata())["repetition"], 1)

    def test_success_requires_raw_response_hash(self):
        value = metadata()
        value["raw_response_sha256"] = None
        with self.assertRaises(SchemaValidationError): validate_generation_metadata(value)

    def test_success_requires_raw_response_bytes(self):
        value = metadata()
        value["raw_response_bytes"] = None
        with self.assertRaises(SchemaValidationError): validate_generation_metadata(value)

    def test_success_cannot_have_infrastructure_failure(self):
        value = metadata()
        value["failure_category"] = "local-runner-failure"
        with self.assertRaises(SchemaValidationError): validate_generation_metadata(value)

    def test_failed_infrastructure_attempt_can_omit_raw_response(self):
        value = metadata()
        value.update(success=False, failure_category="local-runner-failure", timeout=False)
        value.pop("raw_response_path")
        value.pop("raw_response_sha256")
        value.pop("raw_response_bytes")
        self.assertFalse(validate_generation_metadata(value)["success"])

    def test_timezone_timestamp_variants_and_ordering(self):
        for started, finished in (
            ("2026-09-02T10:00:00Z", "2026-09-02T10:01:00Z"),
            ("2026-09-02T10:00:00+05:30", "2026-09-02T10:01:00+05:30"),
            ("2026-09-02T10:00:00-04:00", "2026-09-02T10:01:00-04:00"),
        ):
            value = metadata()
            value.update(timestamp_started=started, timestamp_finished=finished)
            self.assertIsNotNone(validate_generation_metadata(value))
        value = metadata()
        value["timestamp_started"] = "2026-09-02T10:00:00"
        with self.assertRaises(SchemaValidationError): validate_generation_metadata(value)
        value = metadata()
        value.update(timestamp_started="2026-09-02T10:02:00Z", timestamp_finished="2026-09-02T10:01:00Z")
        with self.assertRaises(SchemaValidationError): validate_generation_metadata(value)

    def test_whitespace_only_free_text_fails(self):
        task = read_tasks(PILOT)[0].copy()
        task["task_description"] = " \n\t "
        with self.assertRaises(SchemaValidationError): validate_task(task)
        task = read_tasks(PILOT)[0].copy()
        task["task_family"] = "  "
        with self.assertRaises(SchemaValidationError): validate_task(task)

    def test_generation_metadata_required_fields_are_enforced(self):
        value = metadata()
        del value["canonical_prompt_sha256"]
        with self.assertRaises(SchemaValidationError): validate_generation_metadata(value)

    def test_invalid_attempt_and_repetition_fail(self):
        value = metadata()
        value["attempt_id"] = "retry-1"
        with self.assertRaises(SchemaValidationError): validate_generation_metadata(value)
        value = metadata()
        value["repetition"] = 3
        with self.assertRaises(SchemaValidationError): validate_generation_metadata(value)


if __name__ == "__main__":
    unittest.main()
