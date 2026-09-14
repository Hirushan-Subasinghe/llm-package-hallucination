#!/usr/bin/env python3
"""Render frozen task prompts and generate deterministic collection manifests."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPTS_PATH = ROOT / "prompts" / "prompts_v1.0.0.json"
TEMPLATE_PATH = ROOT / "prompts" / "prompt_template_v1.0.0.md"
RENDERED_DIR = ROOT / "data" / "generated_prompts" / "v1.0.0"
MANIFEST_DIR = ROOT / "manifests"
WORKFLOWS = ("chatgpt_web", "gemini_web", "codex_cli", "antigravity_cli")
PILOT_TASKS = ("AUTH-04", "DB-03", "FILE-02", "API-04", "SEC-03", "LOG-04")
MANIFEST_FIELDS = (
    "run_id",
    "phase",
    "prompt_id",
    "category",
    "workflow",
    "run_number",
    "prompt_set_version",
    "rendered_prompt_path",
    "expected_prompt_sha256",
    "collection_status",
)


def load_tasks() -> list[dict[str, str]]:
    tasks = json.loads(PROMPTS_PATH.read_text(encoding="utf-8"))
    if not isinstance(tasks, list) or len(tasks) != 30:
        raise ValueError("prompts_v1.0.0.json must contain exactly 30 tasks")
    required = {"prompt_id", "category", "task_description", "prompt_set_version"}
    seen: set[str] = set()
    for task in tasks:
        if not required <= task.keys():
            raise ValueError(f"Task is missing required fields: {task}")
        if task["prompt_id"] in seen:
            raise ValueError(f"Duplicate prompt ID: {task['prompt_id']}")
        if task["prompt_set_version"] != "1.0.0":
            raise ValueError(f"Unexpected prompt-set version: {task['prompt_id']}")
        seen.add(task["prompt_id"])
    return tasks


def render_tasks(tasks: list[dict[str, str]]) -> dict[str, tuple[str, str]]:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    occurrences = template.count("[TASK_DESCRIPTION]")
    if occurrences != 1:
        raise ValueError(
            f"Template must contain [TASK_DESCRIPTION] exactly once, found {occurrences}"
        )

    RENDERED_DIR.mkdir(parents=True, exist_ok=True)
    rendered: dict[str, tuple[str, str]] = {}
    for task in tasks:
        prompt = template.replace("[TASK_DESCRIPTION]", task["task_description"])
        path = RENDERED_DIR / f"{task['prompt_id']}.txt"
        path.write_text(prompt, encoding="utf-8", newline="")
        rendered[task["prompt_id"]] = (str(path.relative_to(ROOT)), hashlib.sha256(prompt.encode("utf-8")).hexdigest())
    return rendered


def make_run_id(prefix: str, prompt_id: str, workflow: str, run_number: int) -> str:
    return f"{prefix}-{prompt_id}-{workflow}-R{run_number:02d}"


def manifest_rows(tasks: list[dict[str, str]], rendered: dict[str, tuple[str, str]], phase: str) -> list[dict[str, str]]:
    selected = tasks if phase == "final" else [task for task in tasks if task["prompt_id"] in PILOT_TASKS]
    rows: list[dict[str, str]] = []
    prefix = "BASE" if phase == "final" else "PILOT"
    repetitions = (1, 2, 3) if phase == "final" else (1,)
    for task in selected:
        path, digest = rendered[task["prompt_id"]]
        for workflow in WORKFLOWS:
            for run_number in repetitions:
                rows.append(
                    {
                        "run_id": make_run_id(prefix, task["prompt_id"], workflow, run_number),
                        "phase": phase,
                        "prompt_id": task["prompt_id"],
                        "category": task["category"],
                        "workflow": workflow,
                        "run_number": f"{run_number:02d}",
                        "prompt_set_version": "1.0.0",
                        "rendered_prompt_path": path,
                        "expected_prompt_sha256": digest,
                        "collection_status": "pending",
                    }
                )
    return rows


def write_manifest(name: str, rows: list[dict[str, str]]) -> None:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    path = MANIFEST_DIR / name
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    try:
        tasks = load_tasks()
        rendered = render_tasks(tasks)
        write_manifest("pilot_manifest.csv", manifest_rows(tasks, rendered, "pilot"))
        write_manifest("baseline_manifest.csv", manifest_rows(tasks, rendered, "final"))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"Rendered {len(rendered)} prompts to {RENDERED_DIR.relative_to(ROOT)}")
    print("Generated manifests: 24 pilot runs and 360 baseline runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())