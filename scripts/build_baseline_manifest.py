#!/usr/bin/env python3
"""Create the deterministic frozen 360-cell baseline manifest."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from experiment.baseline_manifest import build_manifest_records, serialize_manifest, write_manifest  # noqa: E402


def main() -> int:
    records = build_manifest_records(
        ROOT / "prompts/tasks/final_1.0.0.jsonl",
        ROOT / "prompts/templates/master_prompt_v1.0.0.md",
    )
    path = ROOT / "data/manifests/baseline_v1.0.0.jsonl"
    result = write_manifest(path, serialize_manifest(records))
    print(f"{result}: {path} ({len(records)} records)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
