"""Dependency-free validation for canonical tasks and generation metadata."""

from __future__ import annotations

import datetime as _datetime
import json
import re
from pathlib import Path
from typing import Any, Iterable


class SchemaValidationError(ValueError):
    """Raised when a protocol record violates its strict schema."""


TASK_FIELDS = {
    "task_id", "category", "difficulty", "task_description", "task_set_version", "status",
    "ecosystem", "runtime", "package_manager", "task_family", "external_dependency_requirement",
    "security_criticality", "notes",
}
CATEGORIES = {
    "Authentication and Authorization", "Database Connectivity and Integration",
    "File Handling and Processing", "API Development and Endpoints",
    "Security Features and Encryption", "Logging and Caching",
}
TASK_ID_RE = re.compile(r"^(AUTH|DB|FILE|API|SEC|LOG)-[0-9]{3}$")
VERSION_RE = re.compile(r"^(pilot|final)-[0-9]+\.[0-9]+\.[0-9]+$")
SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GENERATION_ID_RE = re.compile(
    r"^(?:generation-[A-Za-z0-9][A-Za-z0-9._-]*|"
    r"(?:chatgpt-web|gemini-web|codex-cli|antigravity-cli-gemini)-"
    r"(?:AUTH|DB|FILE|API|SEC|LOG)-[0-9]{3}-R[1-3])$"
)
METADATA_FIELDS = {
    "generation_id", "task_id", "category", "workflow", "interface", "run_number",
    "experiment_condition", "generation_timestamp", "raw_output_path", "raw_output_sha256",
    "visible_model_version", "installation_command_generated", "attempt_id", "attempt_status",
    "failure_category", "failure_summary_redacted", "process_exit_code", "timeout", "cli_version",
    "runner_version", "canonical_prompt_sha256", "workspace_id", "workspace_provenance",
    "filesystem_access", "shell_access", "network_policy", "package_install_policy",
    "raw_stdout_path", "raw_stderr_path", "files_created", "files_modified", "files_deleted",
    "commands_attempted", "package_install_commands",
}
METADATA_REQUIRED = {
    "generation_id", "task_id", "category", "workflow", "interface", "run_number",
    "experiment_condition", "generation_timestamp", "raw_output_path", "raw_output_sha256",
}
WORKFLOW_INTERFACES = {
    "ChatGPT Web": "web",
    "Gemini Web": "web",
    "Codex CLI": "cli",
    "Antigravity CLI — Gemini": "cli",
}
FAILURE_CATEGORIES = {
    "process-launch-failure", "generation-timeout-before-start", "local-runner-failure",
    "authentication-service-failure", "unknown-infrastructure-failure",
    "network-service-error", "provider-timeout", "authentication-failure",
    "browser-cli-failure",
}


def _object(value: Any, fields: set[str], required: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SchemaValidationError("record must be an object")
    unknown = set(value) - fields
    missing = required - set(value)
    if unknown:
        raise SchemaValidationError(f"unknown fields: {', '.join(sorted(unknown))}")
    if missing:
        raise SchemaValidationError(f"missing fields: {', '.join(sorted(missing))}")
    return value


def _nonempty(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise SchemaValidationError(f"{field} must be a non-empty string")


def validate_task(task: dict[str, Any]) -> dict[str, Any]:
    task = _object(task, TASK_FIELDS, {"task_id", "category", "difficulty", "task_description", "task_set_version", "status", "ecosystem", "runtime", "package_manager"})
    for field in ("task_id", "category", "difficulty", "task_description", "task_set_version", "status", "ecosystem", "runtime", "package_manager"):
        _nonempty(task[field], field)
    if not TASK_ID_RE.fullmatch(task["task_id"]): raise SchemaValidationError("invalid task_id")
    if task["category"] not in CATEGORIES: raise SchemaValidationError("unknown category")
    if task["difficulty"] not in {"easy", "medium", "hard"}: raise SchemaValidationError("invalid difficulty")
    if not VERSION_RE.fullmatch(task["task_set_version"]): raise SchemaValidationError("invalid task_set_version")
    if task["status"] not in {"sample", "draft", "final", "retired"}: raise SchemaValidationError("invalid task status")
    if task["ecosystem"] != "node.js": raise SchemaValidationError("invalid ecosystem")
    if task["runtime"] != "Node.js": raise SchemaValidationError("invalid runtime")
    if task["package_manager"] != "npm": raise SchemaValidationError("invalid package_manager")
    for field in ("task_family", "notes"):
        if field in task and not isinstance(task[field], str): raise SchemaValidationError(f"{field} must be a string")
    for field in ("task_family", "notes"):
        if field in task and not task[field].strip(): raise SchemaValidationError(f"{field} must be non-empty")
    if "external_dependency_requirement" in task and task["external_dependency_requirement"] not in {"none", "optional", "required"}: raise SchemaValidationError("invalid external_dependency_requirement")
    if "security_criticality" in task and task["security_criticality"] not in {"low", "medium", "high"}: raise SchemaValidationError("invalid security_criticality")
    return task


def validate_task_records(tasks: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    records = [validate_task(task) for task in tasks]
    ids = [task["task_id"] for task in records]
    if len(ids) != len(set(ids)): raise SchemaValidationError("duplicate task_id")
    versions = {task["task_set_version"] for task in records}
    if len(versions) != 1: raise SchemaValidationError("tasks must have exactly one task_set_version")
    return records


def validate_generation_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    value = _object(metadata, METADATA_FIELDS, METADATA_REQUIRED)
    for field in ("generation_id", "task_id", "category", "workflow", "interface", "experiment_condition", "generation_timestamp"):
        _nonempty(value[field], field)
    if not GENERATION_ID_RE.fullmatch(value["generation_id"]): raise SchemaValidationError("invalid generation_id")
    if not TASK_ID_RE.fullmatch(value["task_id"]): raise SchemaValidationError("invalid task_id")
    if value["category"] not in CATEGORIES: raise SchemaValidationError("unknown category")
    expected_interface = WORKFLOW_INTERFACES.get(value["workflow"])
    if expected_interface is None or value["interface"] != expected_interface: raise SchemaValidationError("invalid workflow/interface")
    if not isinstance(value["run_number"], int) or isinstance(value["run_number"], bool) or value["run_number"] not in {1, 2, 3}: raise SchemaValidationError("invalid run_number")
    if value["experiment_condition"] not in {"baseline", "persistence"}: raise SchemaValidationError("invalid experiment_condition")
    try:
        timestamp = _datetime.datetime.fromisoformat(value["generation_timestamp"].replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError):
        raise SchemaValidationError("invalid generation_timestamp")
    if timestamp.tzinfo is None or timestamp.utcoffset() is None: raise SchemaValidationError("generation_timestamp must include timezone information")
    visible_version = value.get("visible_model_version")
    if visible_version is not None and (not isinstance(visible_version, str) or not visible_version.strip()): raise SchemaValidationError("invalid visible_model_version")
    installation = value.get("installation_command_generated")
    if installation is not None and not isinstance(installation, bool): raise SchemaValidationError("invalid installation_command_generated")
    attempt_id = value.get("attempt_id")
    if attempt_id is not None and (not isinstance(attempt_id, str) or not attempt_id.startswith("attempt-")): raise SchemaValidationError("invalid attempt_id")
    if value.get("attempt_status") not in {None, "successful", "failed"}: raise SchemaValidationError("invalid attempt_status")
    failure = value.get("failure_category")
    if failure is not None and failure not in FAILURE_CATEGORIES: raise SchemaValidationError("invalid failure_category")
    if value.get("attempt_status") == "failed":
        if attempt_id is None or failure is None: raise SchemaValidationError("failed attempt requires attempt_id and failure_category")
        if value["raw_output_path"] is not None or value["raw_output_sha256"] is not None: raise SchemaValidationError("failed attempt cannot claim successful raw output")
    elif failure is not None:
        raise SchemaValidationError("failure_category requires failed attempt_status")
    else:
        _nonempty(value["raw_output_path"], "raw_output_path")
        if not isinstance(value["raw_output_sha256"], str) or not SHA256_RE.fullmatch(value["raw_output_sha256"]): raise SchemaValidationError("invalid raw_output_sha256")
    for field in ("runner_version",):
        field_value = value.get(field)
        if field_value is not None and (not isinstance(field_value, str) or not SEMVER_RE.fullmatch(field_value)): raise SchemaValidationError(f"invalid {field}")
    prompt_hash = value.get("canonical_prompt_sha256")
    if prompt_hash is not None and (not isinstance(prompt_hash, str) or not SHA256_RE.fullmatch(prompt_hash)): raise SchemaValidationError("invalid canonical_prompt_sha256")
    for field in ("files_created", "files_modified", "files_deleted", "commands_attempted", "package_install_commands"):
        items = value.get(field)
        if items is not None and (not isinstance(items, list) or not all(isinstance(item, str) for item in items)): raise SchemaValidationError(f"invalid {field}")
    return value


def load_schema(name: str) -> dict[str, Any]:
    return json.loads((Path(__file__).resolve().parents[2] / "schemas" / name).read_text(encoding="utf-8"))
