#!/usr/bin/env python3
"""Create the immutable pre-smoke experiment freeze record."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

from collect_api_run import DEFAULT_CONFIG, load_config, utc_now
from create_api_manifest import MANIFEST_PATH
from render_api_prompts import EXPECTED_TASK_SHA256, RENDERED_DIR, TASKS_PATH, TEMPLATE_PATH


ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "config" / "experiment_freeze_2026-09-16.json"
MARKDOWN_PATH = ROOT / "docs" / "experiment_freeze_2026-09-16.md"
SCHEMA_PATHS = (
    ROOT / "schemas" / "api_model_set.schema.json",
    ROOT / "schemas" / "api_manifest_row.schema.json",
    ROOT / "schemas" / "api_collection_metadata.schema.json",
    ROOT / "schemas" / "task_record_v2.schema.json",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_record() -> dict:
    config = load_config(DEFAULT_CONFIG)
    if config.get("status") != "frozen_for_collection":
        raise ValueError("Model configuration is not frozen")
    if digest(TASKS_PATH) != EXPECTED_TASK_SHA256:
        raise ValueError("Task file hash changed before freeze record creation")
    prompts = sorted(RENDERED_DIR.glob("*.txt"))
    if len(prompts) != 30:
        raise ValueError("Expected exactly 30 rendered v2 prompts")
    with MANIFEST_PATH.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 360 or any(row["collection_status"] != "pending" for row in rows):
        raise ValueError("Official manifest is not a 360-row all-pending plan")
    return {
        "freeze_record_version": "experiment-freeze-2026-09-16",
        "freeze_record_created_at_utc": utc_now(),
        "freeze_record_written_before_smoke_tests": True,
        "official_collection_started": False,
        "task_set": {
            "version": "final-2.0.0",
            "path": str(TASKS_PATH.relative_to(ROOT)),
            "sha256": digest(TASKS_PATH),
            "record_count": 30,
        },
        "model_set": {
            "version": config["model_set_version"],
            "path": str(DEFAULT_CONFIG.relative_to(ROOT)),
            "sha256": digest(DEFAULT_CONFIG),
            "frozen_at_utc": config["frozen_at_utc"],
            "final_preflight_timestamp_utc": config["final_preflight_timestamp_utc"],
        },
        "prompt_template": {
            "version": "2.0.0",
            "path": str(TEMPLATE_PATH.relative_to(ROOT)),
            "sha256": digest(TEMPLATE_PATH),
        },
        "rendered_prompts": [
            {"path": str(path.relative_to(ROOT)), "sha256": digest(path)} for path in prompts
        ],
        "official_manifest": {
            "path": str(MANIFEST_PATH.relative_to(ROOT)),
            "sha256": digest(MANIFEST_PATH),
            "row_count": len(rows),
            "rows_per_model": dict(sorted(Counter(row["model_condition_id"] for row in rows).items())),
            "rows_per_repetition": dict(sorted(Counter(row["run_repetition"] for row in rows).items())),
            "completed_rows": 0,
        },
        "schemas": [
            {"path": str(path.relative_to(ROOT)), "sha256": digest(path)} for path in SCHEMA_PATHS
        ],
    }


def markdown(record: dict) -> str:
    prompt_lines = "\n".join(
        f"| `{item['path']}` | `{item['sha256']}` |" for item in record["rendered_prompts"]
    )
    schema_lines = "\n".join(
        f"- `{item['path']}` — `{item['sha256']}`" for item in record["schemas"]
    )
    return f"""# Experiment Freeze Record — 2026-09-16

This record was written at `{record['freeze_record_created_at_utc']}` **before any API smoke-test completion request**. Official collection had not started and all 360 official manifest rows were pending.

## Frozen artifacts

- Task set `final-2.0.0`: `{record['task_set']['sha256']}`
- Model set `api-model-set-1.0.0`: `{record['model_set']['sha256']}`
- Prompt template `2.0.0`: `{record['prompt_template']['sha256']}`
- Official manifest: `{record['official_manifest']['sha256']}`
- Official manifest rows: 360; completed: 0

## Rendered prompts

| Path | SHA-256 |
| --- | --- |
{prompt_lines}

## Schemas

{schema_lines}

Smoke task `SMOKE-API-001` and all files under `data/smoke/api/` are excluded from the official manifest and every research metric.
"""


def main() -> int:
    try:
        if JSON_PATH.exists() or MARKDOWN_PATH.exists():
            raise ValueError("Refusing to overwrite an existing freeze record")
        record = build_record()
        JSON_PATH.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        MARKDOWN_PATH.write_text(markdown(record), encoding="utf-8")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"PASS: wrote pre-smoke freeze records {JSON_PATH.relative_to(ROOT)} and {MARKDOWN_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
