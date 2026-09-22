"""Shared paths and validation helpers for collection scripts."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = {
    "pilot": ROOT / "manifests" / "pilot_manifest.csv",
    "final": ROOT / "manifests" / "baseline_manifest.csv",
}
RAW_ROOTS = {
    "pilot": ROOT / "data" / "pilot" / "raw",
    "final": ROOT / "data" / "final" / "raw",
}
REQUIRED_METADATA = (
    "run_id", "phase", "prompt_id", "prompt_set_version", "category", "workflow",
    "tool_name", "provider", "model_name", "model_version", "workflow_type",
    "temperature", "seed", "max_output_tokens", "timestamp", "prompt_text",
    "prompt_sha256", "raw_response_path", "raw_response_sha256", "collection_method",
    "operator_id", "notes", "collection_status",
)


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_manifest(phase: str) -> tuple[list[dict[str, str]], Path]:
    if phase not in MANIFESTS:
        raise ValueError(f"Unknown phase: {phase}")
    path = MANIFESTS[phase]
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle)), path


def validate_manifest_row(row: dict[str, str]) -> None:
    required = {
        "run_id", "phase", "prompt_id", "category", "workflow", "run_number",
        "prompt_set_version", "rendered_prompt_path", "expected_prompt_sha256",
        "collection_status",
    }
    missing = required - row.keys()
    if missing:
        raise ValueError(f"Manifest row is missing fields: {', '.join(sorted(missing))}")
    if row["phase"] not in MANIFESTS:
        raise ValueError(f"Unknown manifest phase: {row['phase']}")
    if row["prompt_set_version"] != "1.0.0":
        raise ValueError(f"Unexpected prompt-set version: {row['prompt_set_version']}")
    if row["collection_status"] != "pending":
        raise ValueError(f"Manifest planning status must remain pending: {row['run_id']}")
    digest = row["expected_prompt_sha256"]
    if len(digest) != 64 or any(character not in "0123456789abcdefABCDEF" for character in digest):
        raise ValueError(f"Invalid expected prompt SHA-256: {row['run_id']}")


def verified_prompt_bytes(row: dict[str, str]) -> bytes:
    validate_manifest_row(row)
    path = ROOT / row["rendered_prompt_path"]
    content = path.read_bytes()
    if sha256_bytes(content) != row["expected_prompt_sha256"]:
        raise ValueError(f"Rendered prompt hash does not match manifest: {row['run_id']}")
    return content


def find_run(run_id: str) -> tuple[dict[str, str], Path]:
    matches: list[tuple[dict[str, str], Path]] = []
    for phase in MANIFESTS:
        rows, path = read_manifest(phase)
        matches.extend((row, path) for row in rows if row["run_id"] == run_id)
    if len(matches) != 1:
        raise ValueError(f"Unknown or non-unique run ID: {run_id}")
    validate_manifest_row(matches[0][0])
    return matches[0]


def run_directory(row: dict[str, str]) -> Path:
    return RAW_ROOTS[row["phase"]] / row["run_id"]


def load_metadata(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        metadata = json.load(handle)
    if not isinstance(metadata, dict):
        raise ValueError("metadata.json must contain an object")
    return metadata


def write_metadata(path: Path, metadata: dict) -> None:
    content = (json.dumps(metadata, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def write_bytes_exclusive(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(content)


def raw_artifact_relative_path(row: dict[str, str], filename: str) -> str:
    return str(Path(row["phase"]) / "raw" / row["run_id"] / filename)
