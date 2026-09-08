#!/usr/bin/env python3
"""Render the repository's canonical pilot or frozen final prompts."""

import argparse
from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

from experiment.prompt_renderer import render_prompts  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-set", choices=("pilot", "final"), default="pilot")
    args = parser.parse_args(argv)
    if args.task_set == "final":
        template = "master_prompt_v1.0.0.md"
        tasks = "final_1.0.0.jsonl"
        template_version = "1.0.0"
    else:
        template = "master_prompt_v0.1.0.md"
        tasks = "pilot_samples.jsonl"
        template_version = "0.1.0"
    render_prompts(
        REPOSITORY_ROOT / "prompts/templates" / template,
        REPOSITORY_ROOT / "prompts/tasks" / tasks,
        REPOSITORY_ROOT / "prompts/rendered",
        template_version=template_version,
        manifest_path_root=Path("prompts/rendered"),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
