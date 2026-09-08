"""Append-only storage for baseline raw responses and technical failures."""

from __future__ import annotations

from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any

from experiment.baseline_manifest import load_manifest
from experiment.schema_validation import (
    FAILURE_CATEGORIES as SCHEMA_FAILURE_CATEGORIES,
    validate_generation_metadata,
)

FAILURE_CATEGORIES = frozenset(SCHEMA_FAILURE_CATEGORIES)
ATTEMPT_ID_PATTERN = re.compile(r"^attempt-[A-Za-z0-9][A-Za-z0-9._-]*$")


class CaptureError(ValueError):
    """Raised when evidence cannot be stored without violating integrity rules."""


def _timestamp(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise CaptureError("timestamp must be ISO 8601 with a timezone") from error
    if parsed.tzinfo is None:
        raise CaptureError("timestamp must include a timezone")
    return value


def _record_for(manifest_path: Path, generation_id: str) -> dict[str, Any]:
    matches = [
        record for record in load_manifest(manifest_path)
        if record["generation_id"] == generation_id
    ]
    if len(matches) != 1:
        raise CaptureError(f"unknown baseline generation_id: {generation_id}")
    record = matches[0]
    if record["experiment_condition"] != "baseline":
        raise CaptureError("capture utility accepts baseline records only")
    return record


def _exclusive_write(path: Path, contents: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise CaptureError(f"refusing to overwrite append-only record: {path}") from None
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(contents)
            output.flush()
            os.fsync(output.fileno())
    except BaseException:
        # The exclusively created partial file is intentionally retained as evidence.
        raise


def _json_bytes(record: dict[str, Any]) -> bytes:
    return (json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def capture_generation(
    manifest_path: Path,
    data_root: Path,
    generation_id: str,
    input_path: Path,
    generation_timestamp: str,
    *,
    visible_model_version: str | None = None,
    installation_command_generated: bool | None = None,
) -> dict[str, Any]:
    """Preserve an existing response byte-for-byte and create immutable metadata."""
    identity = _record_for(manifest_path, generation_id)
    timestamp = _timestamp(generation_timestamp)
    workflow_slug = generation_id[: -len(f'-{identity["task_id"]}-R{identity["run_number"]}')]
    relative_raw = Path("raw") / workflow_slug / "baseline" / identity["task_id"] / f'R{identity["run_number"]}.txt'
    relative_metadata = Path("metadata") / "baseline" / workflow_slug / identity["task_id"] / f'R{identity["run_number"]}.json'
    raw_path = data_root / relative_raw.relative_to("raw")
    metadata_path = data_root.parent / relative_metadata
    if raw_path.exists() or metadata_path.exists():
        raise CaptureError(f"generation already has stored evidence: {generation_id}")

    raw_bytes = input_path.read_bytes()
    digest = hashlib.sha256(raw_bytes).hexdigest()
    metadata = {
        "generation_id": generation_id,
        "task_id": identity["task_id"],
        "category": identity["category"],
        "workflow": identity["workflow"],
        "interface": identity["interface"],
        "run_number": identity["run_number"],
        "experiment_condition": "baseline",
        "generation_timestamp": timestamp,
        "raw_output_path": relative_raw.as_posix(),
        "raw_output_sha256": digest,
        "visible_model_version": visible_model_version,
        "installation_command_generated": installation_command_generated,
    }
    validate_generation_metadata(metadata)
    _exclusive_write(raw_path, raw_bytes)
    if hashlib.sha256(raw_path.read_bytes()).hexdigest() != digest:
        raise CaptureError("stored raw output failed SHA-256 verification")
    _exclusive_write(metadata_path, _json_bytes(metadata))
    return metadata


def record_failure(
    manifest_path: Path,
    failed_root: Path,
    generation_id: str,
    attempt_id: str,
    attempt_timestamp: str,
    failure_category: str,
    *,
    failure_summary_redacted: str | None = None,
) -> dict[str, Any]:
    """Create one immutable technical-failure attempt record."""
    identity = _record_for(manifest_path, generation_id)
    if not ATTEMPT_ID_PATTERN.fullmatch(attempt_id):
        raise CaptureError("attempt_id must start with 'attempt-' and be path-safe")
    if failure_category not in FAILURE_CATEGORIES:
        raise CaptureError(f"unsupported failure category: {failure_category}")
    timestamp = _timestamp(attempt_timestamp)
    record = {
        "attempt_id": attempt_id,
        "generation_id": generation_id,
        "task_id": identity["task_id"],
        "workflow": identity["workflow"],
        "attempt_timestamp": timestamp,
        "attempt_status": "failed",
        "failure_category": failure_category,
        "failure_summary_redacted": failure_summary_redacted,
    }
    _exclusive_write(failed_root / "baseline" / f"{attempt_id}.json", _json_bytes(record))
    return record


def progress(manifest_path: Path, metadata_root: Path) -> dict[str, int]:
    """Return derived baseline progress without changing the canonical manifest."""
    records = load_manifest(manifest_path)
    completed: set[str] = set()
    if metadata_root.exists():
        for path in metadata_root.rglob("*.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            validate_generation_metadata(data)
            completed.add(data["generation_id"])
    known = {record["generation_id"] for record in records}
    if not completed <= known:
        raise CaptureError("completion metadata contains unknown generation IDs")
    return {"TOTAL": len(records), "COMPLETED": len(completed), "PENDING": len(records) - len(completed)}
