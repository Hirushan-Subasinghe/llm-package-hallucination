#!/usr/bin/env python3
"""Create or verify the frozen 360-row v2 API manifest."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

from collect_api_run import DEFAULT_CONFIG, load_config
from render_api_prompts import EXPECTED_TASK_SHA256, RENDERED_DIR, TASKS_PATH, sha256_bytes


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST_PATH = ROOT / "manifests" / "api_final_v2.1.0_manifest.csv"
DEFAULT_RENDERED_DIR = ROOT / "data" / "generated_prompts" / "v2.1.0"
DEFAULT_RUN_PREFIX = "API-v2.1"
MANIFEST_PATH_V2_0 = ROOT / "manifests" / "api_final_v2.0.0_manifest.csv"
RENDERED_DIR_V2_0 = ROOT / "data" / "generated_prompts" / "v2.0.0"
RUN_PREFIX_V2_0 = "API"

MANIFEST_PATH = DEFAULT_MANIFEST_PATH
FIELDS = (
    "collection_order",
    "run_id",
    "phase",
    "task_id",
    "category",
    "task_set_version",
    "model_set_version",
    "model_condition_id",
    "model_id",
    "api_provider",
    "underlying_provider_pin",
    "run_repetition",
    "rendered_prompt_path",
    "expected_prompt_sha256",
    "collection_status",
)


def load_frozen_tasks() -> list[dict[str, str]]:
    content = TASKS_PATH.read_bytes()
    if sha256_bytes(content) != EXPECTED_TASK_SHA256:
        raise ValueError("Task file does not match the frozen approved hash")
    return [json.loads(line) for line in content.decode("utf-8").splitlines() if line.strip()]


def make_rows(
    config: dict,
    tasks: list[dict[str, str]],
    rendered_dir: Path = DEFAULT_RENDERED_DIR,
    run_prefix: str = DEFAULT_RUN_PREFIX,
) -> list[dict[str, str]]:
    if config.get("status") != "frozen_for_collection":
        raise ValueError("Model set must be frozen before manifest creation")
    models = {model["condition_id"]: model for model in config["models"]}
    base_order = ("M1", "M2", "M3", "M4")
    rows: list[dict[str, str]] = []
    order = 1
    for repetition in range(1, 4):
        repetition_offset = repetition - 1
        for task_position, task in enumerate(tasks):
            rotation = (task_position + repetition_offset) % len(base_order)
            model_order = base_order[rotation:] + base_order[:rotation]
            prompt_path = rendered_dir / f"{task['task_id']}.txt"
            if not prompt_path.is_file():
                raise ValueError(f"Rendered prompt is missing: {prompt_path}")
            prompt_hash = hashlib.sha256(prompt_path.read_bytes()).hexdigest()
            for condition_id in model_order:
                model = models[condition_id]
                routing = model.get("openrouter_routing")
                provider_pin = routing["underlying_provider_slug"] if routing else "not_applicable"
                rows.append({
                    "collection_order": str(order),
                    "run_id": f"{run_prefix}-{task['task_id']}-{condition_id}-R{repetition:02d}",
                    "phase": "final",
                    "task_id": task["task_id"],
                    "category": task["category"],
                    "task_set_version": "final-2.0.0",
                    "model_set_version": config["model_set_version"],
                    "model_condition_id": condition_id,
                    "model_id": model["model_id"],
                    "api_provider": model["api_provider"],
                    "underlying_provider_pin": provider_pin,
                    "run_repetition": f"R{repetition:02d}",
                    "rendered_prompt_path": str(prompt_path.resolve().relative_to(ROOT)),
                    "expected_prompt_sha256": prompt_hash,
                    "collection_status": "pending",
                })
                order += 1
    validate_rows(rows)
    return rows


def validate_rows(rows: list[dict[str, str]]) -> None:
    if len(rows) != 360:
        raise ValueError("Official API manifest must contain exactly 360 rows")
    if len({row["run_id"] for row in rows}) != 360:
        raise ValueError("Official API manifest run IDs must be unique")
    if [int(row["collection_order"]) for row in rows] != list(range(1, 361)):
        raise ValueError("Collection order must be contiguous from 1 through 360")
    if Counter(row["model_condition_id"] for row in rows) != Counter({model: 90 for model in ("M1", "M2", "M3", "M4")}):
        raise ValueError("Official API manifest must contain 90 rows per model")
    if Counter(row["run_repetition"] for row in rows) != Counter({rep: 120 for rep in ("R01", "R02", "R03")}):
        raise ValueError("Official API manifest must contain 120 rows per repetition")
    if any(row["collection_status"] != "pending" for row in rows):
        raise ValueError("Every official API manifest row must begin pending")


def csv_bytes(rows: list[dict[str, str]]) -> bytes:
    import io

    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create or verify the frozen v2 API manifest")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH, help="Manifest path")
    parser.add_argument("--rendered-dir", type=Path, default=DEFAULT_RENDERED_DIR, help="Rendered prompts dir")
    parser.add_argument("--run-prefix", type=str, default=DEFAULT_RUN_PREFIX, help="Run ID prefix")
    parser.add_argument("--check", action="store_true", help="Verify without writing")
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    rendered_dir = args.rendered_dir.resolve()
    try:
        rows = make_rows(
            load_config(DEFAULT_CONFIG),
            load_frozen_tasks(),
            rendered_dir=rendered_dir,
            run_prefix=args.run_prefix,
        )
        content = csv_bytes(rows)
        if manifest_path.exists():
            if manifest_path.read_bytes() != content:
                raise ValueError(f"Existing official API manifest {manifest_path} differs from deterministic output")
        elif args.check:
            raise ValueError(f"Official API manifest does not exist: {manifest_path}")
        else:
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_bytes(content)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    action = "Verified" if args.check else "Created"
    print(f"{action} 360-row manifest at {manifest_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
