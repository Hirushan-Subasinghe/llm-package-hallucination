"""Deterministically render canonical experimental prompts from JSONL tasks."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

PLACEHOLDER = "{{TASK_DESCRIPTION}}"
REQUIRED_TASK_FIELDS = (
    "task_id",
    "category",
    "difficulty",
    "task_description",
    "task_set_version",
    "status",
)


class PromptValidationError(ValueError):
    """Raised when a template or task definition is invalid."""


def read_template(path: Path) -> str:
    """Read and validate a UTF-8 master prompt template."""
    template = path.read_text(encoding="utf-8")
    count = template.count(PLACEHOLDER)
    if count != 1:
        raise PromptValidationError(
            f"template must contain exactly one {PLACEHOLDER}; found {count}"
        )
    return template


def read_tasks(path: Path) -> list[dict[str, Any]]:
    """Read, validate, and return task definitions in source order."""
    tasks: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    with path.open("r", encoding="utf-8", newline="") as task_file:
        for line_number, line in enumerate(task_file, start=1):
            if not line.strip():
                raise PromptValidationError(f"blank JSONL record at line {line_number}")
            try:
                task = json.loads(line)
            except json.JSONDecodeError as error:
                raise PromptValidationError(
                    f"invalid JSON at line {line_number}: {error.msg}"
                ) from error
            if not isinstance(task, dict):
                raise PromptValidationError(
                    f"task at line {line_number} must be a JSON object"
                )
            missing = [field for field in REQUIRED_TASK_FIELDS if field not in task]
            if missing:
                raise PromptValidationError(
                    f"task at line {line_number} is missing fields: {', '.join(missing)}"
                )
            invalid = [
                field
                for field in REQUIRED_TASK_FIELDS
                if not isinstance(task[field], str) or not task[field].strip()
            ]
            if invalid:
                raise PromptValidationError(
                    f"task at line {line_number} has invalid fields: {', '.join(invalid)}"
                )
            task_id = task["task_id"]
            if task_id in seen_ids:
                raise PromptValidationError(f"duplicate task_id: {task_id}")
            if Path(task_id).name != task_id or task_id in {".", ".."}:
                raise PromptValidationError(f"task_id is not path-safe: {task_id}")
            seen_ids.add(task_id)
            tasks.append(task)
    return tasks


def render_prompts(
    template_path: Path,
    tasks_path: Path,
    output_root: Path,
    *,
    template_version: str,
    manifest_path_root: Path | None = None,
) -> list[dict[str, str]]:
    """Render tasks and write a deterministic JSONL manifest."""
    template = read_template(template_path)
    tasks = read_tasks(tasks_path)
    versions = {task["task_set_version"] for task in tasks}
    if len(versions) != 1:
        raise PromptValidationError("tasks must have exactly one task_set_version")
    task_set_version = next(iter(versions))
    output_directory = output_root / task_set_version
    output_directory.mkdir(parents=True, exist_ok=True)

    manifest: list[dict[str, str]] = []
    for task in sorted(tasks, key=lambda item: item["task_id"]):
        rendered = template.replace(PLACEHOLDER, task["task_description"])
        rendered_bytes = rendered.encode("utf-8")
        output_path = output_directory / f'{task["task_id"]}.txt'
        output_path.write_bytes(rendered_bytes)
        recorded_path = (
            manifest_path_root / task_set_version / output_path.name
            if manifest_path_root is not None
            else output_path
        )
        manifest.append(
            {
                "task_id": task["task_id"],
                "category": task["category"],
                "difficulty": task["difficulty"],
                "task_set_version": task_set_version,
                "template_version": template_version,
                "rendered_prompt_path": recorded_path.as_posix(),
                "sha256": hashlib.sha256(rendered_bytes).hexdigest(),
            }
        )

    manifest_path = output_directory / "manifest.jsonl"
    manifest_text = "".join(
        json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n"
        for entry in manifest
    )
    manifest_path.write_text(manifest_text, encoding="utf-8", newline="")
    return manifest


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--tasks", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--template-version", required=True)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    render_prompts(
        args.template,
        args.tasks,
        args.output_root,
        template_version=args.template_version,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
