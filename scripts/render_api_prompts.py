#!/usr/bin/env python3
"""Deterministically render the frozen v2 task prompts without model-specific text."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS_PATH = ROOT / "prompts" / "tasks" / "final_2.0.0.jsonl"
TEMPLATE_PATH = ROOT / "prompts" / "prompt_template_v2.0.0.md"
RENDERED_DIR = ROOT / "data" / "generated_prompts" / "v2.0.0"
EXPECTED_TASK_SHA256 = "ef0aff59f8a3934f65379d34036848652b7b5593f595ffa4b449a15af021546b"
CATEGORIES = {"AUTH-FED", "PKI-CRYPTO", "DOC-BINARY", "ENT-INT", "DATA-ADV", "DIST-OBS"}
FORBIDDEN_TEMPLATE_PATTERNS = (
    r"hallucinat",
    r"verify (?:the )?packages?",
    r"only use real npm packages",
    r"web search",
    r"openrouter|groq|cohere|qwen|gpt|nemotron",
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_tasks() -> list[dict[str, str]]:
    content = TASKS_PATH.read_bytes()
    if sha256_bytes(content) != EXPECTED_TASK_SHA256:
        raise ValueError("Frozen task file hash does not match the approved hash")
    tasks = [json.loads(line) for line in content.decode("utf-8").splitlines() if line.strip()]
    if len(tasks) != 30:
        raise ValueError("Frozen v2 task set must contain exactly 30 tasks")
    ids = [task["task_id"] for task in tasks]
    if len(ids) != len(set(ids)):
        raise ValueError("Frozen v2 task IDs must be unique")
    if Counter(task["category"] for task in tasks) != Counter({category: 5 for category in CATEGORIES}):
        raise ValueError("Frozen v2 task set must contain five tasks in each category")
    if any(task["task_set_version"] != "final-2.0.0" for task in tasks):
        raise ValueError("Unexpected task-set version")
    return tasks


def load_template() -> str:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    if template.count("[TASK_DESCRIPTION]") != 1:
        raise ValueError("V2 template must contain [TASK_DESCRIPTION] exactly once")
    for pattern in FORBIDDEN_TEMPLATE_PATTERNS:
        if re.search(pattern, template, flags=re.IGNORECASE):
            raise ValueError(f"V2 template contains forbidden wording: {pattern}")
    return template


def expected_rendered() -> dict[str, bytes]:
    template = load_template()
    return {
        task["task_id"]: template.replace("[TASK_DESCRIPTION]", task["prompt"]).encode("utf-8")
        for task in load_tasks()
    }


def write_or_verify(rendered: dict[str, bytes], *, check_only: bool) -> None:
    if check_only and not RENDERED_DIR.is_dir():
        raise ValueError("Rendered v2 prompt directory does not exist")
    if not check_only:
        RENDERED_DIR.mkdir(parents=True, exist_ok=True)
    expected_names = {f"{task_id}.txt" for task_id in rendered}
    actual_names = {path.name for path in RENDERED_DIR.glob("*.txt")} if RENDERED_DIR.exists() else set()
    if check_only and actual_names != expected_names:
        raise ValueError("Rendered v2 prompt file set does not match the frozen task set")
    for task_id, content in rendered.items():
        path = RENDERED_DIR / f"{task_id}.txt"
        if path.exists():
            if path.read_bytes() != content:
                raise ValueError(f"Refusing to overwrite changed frozen prompt: {path}")
        elif check_only:
            raise ValueError(f"Missing rendered prompt: {path}")
        else:
            path.write_bytes(content)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render or verify frozen v2 API prompts")
    parser.add_argument("--check", action="store_true", help="Verify existing files without writing")
    args = parser.parse_args()
    try:
        rendered = expected_rendered()
        write_or_verify(rendered, check_only=args.check)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    action = "Verified" if args.check else "Rendered"
    print(f"{action} {len(rendered)} frozen prompts in {RENDERED_DIR.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
