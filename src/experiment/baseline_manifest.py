"""Build and validate the frozen 360-cell baseline manifest."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any

from experiment.prompt_renderer import PLACEHOLDER, read_tasks, read_template

WORKFLOWS = (
    ("chatgpt-web", "ChatGPT Web", "web"),
    ("gemini-web", "Gemini Web", "web"),
    ("codex-cli", "Codex CLI", "cli"),
    ("antigravity-cli-gemini", "Antigravity CLI — Gemini", "cli"),
)
RUNS = (1, 2, 3)
EXPECTED_CATEGORIES = {
    "Authentication and Authorization",
    "Database Connectivity and Integration",
    "File Handling and Processing",
    "API Development and Endpoints",
    "Security Features and Encryption",
    "Logging and Caching",
}


class BaselineManifestError(ValueError):
    """Raised when the baseline design or an existing manifest is invalid."""


def build_manifest_records(
    tasks_path: Path, template_path: Path, *, prompt_version: str = "1.0.0"
) -> list[dict[str, Any]]:
    """Return the deterministic baseline Cartesian product in stable order."""
    tasks = read_tasks(tasks_path)
    template = read_template(template_path)
    if len(tasks) != 30:
        raise BaselineManifestError(f"expected exactly 30 final tasks; found {len(tasks)}")
    if {task["status"] for task in tasks} != {"final"}:
        raise BaselineManifestError("every baseline task must have final status")
    counts = Counter(task["category"] for task in tasks)
    if set(counts) != EXPECTED_CATEGORIES or set(counts.values()) != {5}:
        raise BaselineManifestError("expected exactly five final tasks in each category")

    records: list[dict[str, Any]] = []
    for workflow_slug, workflow, interface in WORKFLOWS:
        for task in sorted(tasks, key=lambda item: item["task_id"]):
            prompt = template.replace(PLACEHOLDER, task["task_description"]).encode("utf-8")
            for run_number in RUNS:
                generation_id = f'{workflow_slug}-{task["task_id"]}-R{run_number}'
                records.append(
                    {
                        "generation_id": generation_id,
                        "task_id": task["task_id"],
                        "category": task["category"],
                        "workflow": workflow,
                        "interface": interface,
                        "run_number": run_number,
                        "experiment_condition": "baseline",
                        "prompt_version": prompt_version,
                        "prompt_sha256": hashlib.sha256(prompt).hexdigest(),
                        "status": "PENDING",
                    }
                )
    validate_manifest(records)
    return records


def validate_manifest(records: list[dict[str, Any]]) -> None:
    """Validate all locked baseline invariants."""
    if len(records) != 360:
        raise BaselineManifestError(f"expected 360 records; found {len(records)}")
    ids = [record["generation_id"] for record in records]
    if len(set(ids)) != 360:
        raise BaselineManifestError("generation IDs must be unique")
    tasks = {record["task_id"] for record in records}
    if len(tasks) != 30:
        raise BaselineManifestError("manifest must contain exactly 30 tasks")
    expected = {
        (task_id, workflow, run)
        for task_id in tasks
        for _, workflow, _ in WORKFLOWS
        for run in RUNS
    }
    actual = {
        (record["task_id"], record["workflow"], record["run_number"])
        for record in records
    }
    if actual != expected:
        raise BaselineManifestError("baseline task/workflow/run product is incomplete")
    if {record["experiment_condition"] for record in records} != {"baseline"}:
        raise BaselineManifestError("manifest may contain baseline records only")
    if {record["status"] for record in records} != {"PENDING"}:
        raise BaselineManifestError("canonical manifest status must remain PENDING")


def serialize_manifest(records: list[dict[str, Any]]) -> bytes:
    """Serialize JSONL deterministically as UTF-8."""
    validate_manifest(records)
    return "".join(
        json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
        for record in records
    ).encode("utf-8")


def write_manifest(output_path: Path, contents: bytes) -> str:
    """Create a manifest, accepting an existing file only when byte-identical."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with output_path.open("xb") as output:
            output.write(contents)
        return "created"
    except FileExistsError:
        if output_path.read_bytes() == contents:
            return "unchanged"
        raise BaselineManifestError(
            f"refusing to overwrite non-identical manifest: {output_path}"
        ) from None


def load_manifest(path: Path) -> list[dict[str, Any]]:
    """Load and validate a baseline JSONL manifest."""
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as source:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                raise BaselineManifestError(f"blank manifest line {line_number}")
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise BaselineManifestError(
                    f"invalid manifest JSON at line {line_number}: {error.msg}"
                ) from error
            if not isinstance(record, dict):
                raise BaselineManifestError(f"manifest line {line_number} is not an object")
            records.append(record)
    validate_manifest(records)
    return records
