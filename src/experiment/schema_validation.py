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
METADATA_FIELDS = {
    "experiment_run_id", "generation_id", "attempt_id", "task_id", "repetition", "task_set_version",
    "template_version", "canonical_prompt_sha256", "tool_name", "provider_name", "model_name",
    "model_selection_mode", "workflow_type", "interface", "cli_version", "runner_version",
    "experiment_protocol_version", "timestamp_started", "timestamp_finished", "timezone",
    "execution_duration_ms", "workspace_id", "workspace_provenance", "workspace_base_version",
    "filesystem_access", "shell_access", "network_policy", "package_install_policy", "process_exit_code",
    "timeout", "success", "failure_category", "raw_stdout_path", "raw_stderr_path", "raw_response_path",
    "raw_response_sha256", "raw_response_bytes", "files_created", "files_modified", "files_deleted",
    "commands_attempted", "package_install_attempted", "package_install_commands",
}
METADATA_REQUIRED = METADATA_FIELDS - {"raw_response_path", "raw_response_sha256", "raw_response_bytes"}
FAILURE_CATEGORIES = {
    "process-launch-failure", "generation-timeout-before-start", "local-runner-failure",
    "authentication-service-failure", "unknown-infrastructure-failure",
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
    for field in ("experiment_run_id", "generation_id", "attempt_id", "tool_name", "provider_name", "model_name", "timezone", "workspace_id", "workspace_base_version"):
        _nonempty(value[field], field)
    for field, prefix in (("experiment_run_id", "run-"), ("generation_id", "generation-"), ("attempt_id", "attempt-")):
        if not value[field].startswith(prefix): raise SchemaValidationError(f"invalid {field}")
    if not TASK_ID_RE.fullmatch(value["task_id"]): raise SchemaValidationError("invalid task_id")
    if not isinstance(value["repetition"], int) or isinstance(value["repetition"], bool) or value["repetition"] not in {1, 2}: raise SchemaValidationError("invalid repetition")
    if not VERSION_RE.fullmatch(value["task_set_version"]): raise SchemaValidationError("invalid task_set_version")
    for field in ("template_version", "runner_version", "experiment_protocol_version"):
        if not isinstance(value[field], str) or not SEMVER_RE.fullmatch(value[field]): raise SchemaValidationError(f"invalid {field}")
    if not isinstance(value["canonical_prompt_sha256"], str) or not SHA256_RE.fullmatch(value["canonical_prompt_sha256"]): raise SchemaValidationError("invalid canonical_prompt_sha256")
    if value["model_selection_mode"] not in {"fixed", "provider-default", "unavailable"}: raise SchemaValidationError("invalid model_selection_mode")
    if value["workflow_type"] != "agentic-coding" or value["interface"] != "cli": raise SchemaValidationError("invalid workflow/interface")
    parsed_timestamps = []
    for field in ("timestamp_started", "timestamp_finished"):
        try:
            parsed = _datetime.datetime.fromisoformat(value[field].replace("Z", "+00:00"))
        except (AttributeError, TypeError, ValueError):
            raise SchemaValidationError(f"invalid {field}")
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise SchemaValidationError(f"{field} must include timezone information")
        parsed_timestamps.append(parsed)
    if parsed_timestamps[1] < parsed_timestamps[0]:
        raise SchemaValidationError("timestamp_finished precedes timestamp_started")
    if value["execution_duration_ms"] is not None and (not isinstance(value["execution_duration_ms"], int) or value["execution_duration_ms"] < 0): raise SchemaValidationError("invalid execution_duration_ms")
    if value["workspace_provenance"] != "fresh-temporary" or value["filesystem_access"] != "isolated-workspace-only": raise SchemaValidationError("invalid workspace isolation")
    if value["shell_access"] not in {"enabled", "disabled"} or value["network_policy"] not in {"disabled", "restricted"} or value["package_install_policy"] != "blocked-and-recorded": raise SchemaValidationError("invalid execution policy")
    if not isinstance(value["timeout"], bool) or not isinstance(value["success"], bool) or not isinstance(value["package_install_attempted"], bool): raise SchemaValidationError("boolean metadata field is invalid")
    if value["failure_category"] is not None and value["failure_category"] not in FAILURE_CATEGORIES: raise SchemaValidationError("invalid failure_category")
    if value["success"] and value["timeout"]: raise SchemaValidationError("successful metadata cannot time out")
    if value["success"] and value["failure_category"] is not None: raise SchemaValidationError("successful metadata cannot have failure_category")
    if value["success"]:
        if not isinstance(value["raw_response_path"], str) or not value["raw_response_path"].strip(): raise SchemaValidationError("successful metadata requires raw_response_path")
        if not isinstance(value["raw_response_sha256"], str) or not SHA256_RE.fullmatch(value["raw_response_sha256"]): raise SchemaValidationError("successful metadata requires raw_response_sha256")
        if not isinstance(value["raw_response_bytes"], int) or isinstance(value["raw_response_bytes"], bool) or value["raw_response_bytes"] < 0: raise SchemaValidationError("successful metadata requires raw_response_bytes")
    if not value["success"] and not value["failure_category"]: raise SchemaValidationError("failed metadata requires failure_category")
    raw_response_sha256 = value.get("raw_response_sha256")
    if raw_response_sha256 is not None and (not isinstance(raw_response_sha256, str) or not SHA256_RE.fullmatch(raw_response_sha256)): raise SchemaValidationError("invalid raw_response_sha256")
    for field in ("files_created", "files_modified", "files_deleted", "commands_attempted", "package_install_commands"):
        if not isinstance(value[field], list) or not all(isinstance(item, str) for item in value[field]): raise SchemaValidationError(f"invalid {field}")
    return value


def load_schema(name: str) -> dict[str, Any]:
    return json.loads((Path(__file__).resolve().parents[2] / "schemas" / name).read_text(encoding="utf-8"))
