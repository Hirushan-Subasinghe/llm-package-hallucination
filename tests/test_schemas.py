import copy
import hashlib
from pathlib import Path
import unittest

from experiment.prompt_renderer import read_tasks
from experiment.schema_validation import (
    SchemaValidationError,
    load_schema,
    validate_generation_metadata,
    validate_task,
    validate_task_records,
)


ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "prompts/tasks/pilot_samples.jsonl"


def metadata(workflow: str = "Codex CLI", interface: str = "cli") -> dict:
    return {
        "generation_id": "codex-cli-AUTH-001-R1",
        "task_id": "AUTH-001",
        "category": "Authentication and Authorization",
        "workflow": workflow,
        "interface": interface,
        "run_number": 1,
        "experiment_condition": "baseline",
        "generation_timestamp": "2026-09-02T10:01:00+05:30",
        "raw_output_path": "data/raw/baseline/AUTH-001.txt",
        "raw_output_sha256": hashlib.sha256(b"response").hexdigest(),
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
        with self.assertRaises(SchemaValidationError):
            validate_task(task)

    def test_unknown_category_fails(self):
        task = read_tasks(PILOT)[0].copy()
        task["category"] = "Other"
        with self.assertRaises(SchemaValidationError):
            validate_task(task)

    def test_duplicate_ids_fail(self):
        tasks = read_tasks(PILOT)[:2]
        tasks[1] = copy.deepcopy(tasks[0])
        with self.assertRaises(SchemaValidationError):
            validate_task_records(tasks)

    def test_missing_required_task_field_fails(self):
        task = read_tasks(PILOT)[0].copy()
        del task["task_description"]
        with self.assertRaises(SchemaValidationError):
            validate_task(task)

    def test_node_npm_scope_is_enforced(self):
        for field, invalid in (("ecosystem", "python"), ("runtime", "Python"), ("package_manager", "pip")):
            task = read_tasks(PILOT)[0].copy()
            task[field] = invalid
            with self.subTest(field=field), self.assertRaises(SchemaValidationError):
                validate_task(task)

    def test_invalid_task_status_is_rejected(self):
        task = read_tasks(PILOT)[0].copy()
        task["status"] = "observed"
        with self.assertRaises(SchemaValidationError):
            validate_task(task)

    def test_whitespace_only_task_text_is_rejected(self):
        for field in ("task_description", "task_family"):
            task = read_tasks(PILOT)[0].copy()
            task[field] = " \n\t "
            with self.subTest(field=field), self.assertRaises(SchemaValidationError):
                validate_task(task)

    def test_unknown_task_fields_are_rejected(self):
        task = read_tasks(PILOT)[0].copy()
        task["expected_package_names"] = []
        with self.assertRaises(SchemaValidationError):
            validate_task(task)

    def test_runs_one_two_and_three_are_accepted(self):
        for run_number in (1, 2, 3):
            value = metadata()
            value["run_number"] = run_number
            with self.subTest(run_number=run_number):
                self.assertEqual(validate_generation_metadata(value)["run_number"], run_number)

    def test_run_four_is_rejected_for_baseline(self):
        value = metadata()
        value["run_number"] = 4
        with self.assertRaises(SchemaValidationError):
            validate_generation_metadata(value)

    def test_all_authoritative_workflows_are_accepted(self):
        workflows = {
            "ChatGPT Web": "web",
            "Gemini Web": "web",
            "Codex CLI": "cli",
            "Antigravity CLI — Gemini": "cli",
        }
        for workflow, interface in workflows.items():
            with self.subTest(workflow=workflow):
                self.assertEqual(validate_generation_metadata(metadata(workflow, interface))["workflow"], workflow)

    def test_obsolete_workflows_are_rejected(self):
        for workflow, interface in (("Claude Code", "cli"), ("Gemini CLI", "cli"), ("GitHub Copilot CLI", "cli")):
            with self.subTest(workflow=workflow), self.assertRaises(SchemaValidationError):
                validate_generation_metadata(metadata(workflow, interface))

    def test_workflow_interface_pairing_is_enforced(self):
        with self.assertRaises(SchemaValidationError):
            validate_generation_metadata(metadata("ChatGPT Web", "cli"))
        with self.assertRaises(SchemaValidationError):
            validate_generation_metadata(metadata("Codex CLI", "web"))

    def test_web_records_need_no_cli_metadata_or_visible_version(self):
        value = metadata("ChatGPT Web", "web")
        self.assertNotIn("cli_version", value)
        self.assertNotIn("visible_model_version", value)
        self.assertEqual(validate_generation_metadata(value)["interface"], "web")

    def test_optional_visible_version_and_installation_flag(self):
        value = metadata("Gemini Web", "web")
        value.update(visible_model_version="visible-version", installation_command_generated=False)
        validated = validate_generation_metadata(value)
        self.assertEqual(validated["visible_model_version"], "visible-version")
        self.assertFalse(validated["installation_command_generated"])

    def test_baseline_and_persistence_conditions_are_accepted(self):
        for condition in ("baseline", "persistence"):
            value = metadata()
            value["experiment_condition"] = condition
            with self.subTest(condition=condition):
                self.assertEqual(validate_generation_metadata(value)["experiment_condition"], condition)

    def test_unknown_experiment_condition_is_rejected(self):
        value = metadata()
        value["experiment_condition"] = "pilot"
        with self.assertRaises(SchemaValidationError):
            validate_generation_metadata(value)

    def test_timestamp_requires_timezone(self):
        value = metadata()
        value["generation_timestamp"] = "2026-09-02T10:01:00"
        with self.assertRaises(SchemaValidationError):
            validate_generation_metadata(value)

    def test_raw_output_hash_is_required(self):
        value = metadata()
        del value["raw_output_sha256"]
        with self.assertRaises(SchemaValidationError):
            validate_generation_metadata(value)

    def test_failed_attempt_is_distinguishable(self):
        value = metadata()
        value.update(
            attempt_id="attempt-AUTH-001-codex-r1-a1",
            attempt_status="failed",
            failure_category="local-runner-failure",
            timeout=False,
            raw_output_path=None,
            raw_output_sha256=None,
        )
        self.assertEqual(validate_generation_metadata(value)["attempt_status"], "failed")
        del value["failure_category"]
        with self.assertRaises(SchemaValidationError):
            validate_generation_metadata(value)

    def test_unknown_metadata_fields_are_rejected(self):
        value = metadata()
        value["provider_specific_prompt"] = "changed"
        with self.assertRaises(SchemaValidationError):
            validate_generation_metadata(value)


if __name__ == "__main__":
    unittest.main()
