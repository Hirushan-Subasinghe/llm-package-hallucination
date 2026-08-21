#!/usr/bin/env python3
"""Render the repository's pilot canonical prompts."""

from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

from experiment.prompt_renderer import render_prompts  # noqa: E402


def main() -> int:
    render_prompts(
        REPOSITORY_ROOT / "prompts/templates/master_prompt_v0.1.0.md",
        REPOSITORY_ROOT / "prompts/tasks/pilot_samples.jsonl",
        REPOSITORY_ROOT / "prompts/rendered",
        template_version="0.1.0",
        manifest_path_root=Path("prompts/rendered"),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
