"""Shared paths and validation helpers for collection scripts."""

from __future__ import annotations

import csv
import hashlib
import json
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


def read_manifest(phase: str) -> tuple[list[dict[str, str]], Path]:
    if phase not in MANIFESTS:
        raise ValueError(f"Unknown phase: {phase}")
    path = MANIFESTS[phase]
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle)), path


def find_run(run_id: str) -> tuple[dict[str, str], Path]:
    matches: list[tuple[dict[str, str], Path]] = []
    for phase in MANIFESTS:
        rows, path = read_manifest(phase)
        matches.extend((row, path) for row in rows if row["run_id"] == run_id)
    if len(matches) != 1:
        raise ValueError(f"Unknown or non-unique run ID: {run_id}")
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
    path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
