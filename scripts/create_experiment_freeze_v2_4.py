#!/usr/bin/env python3
"""Create the prospective v2.4 freeze record without touching frozen v2.3 files."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "prompts" / "tasks" / "final_2.0.0.jsonl"
MODEL_SET = ROOT / "config" / "api_model_set_1.2.0.json"
TEMPLATE = ROOT / "prompts" / "prompt_template_v2.4.0.md"
PROMPTS = ROOT / "data" / "generated_prompts" / "v2.4.0"
MANIFEST = ROOT / "manifests" / "api_final_v2.4.0_manifest.csv"
SCHEMAS = (
    ROOT / "schemas" / "api_model_set.schema.json",
    ROOT / "schemas" / "api_manifest_row.schema.json",
    ROOT / "schemas" / "api_collection_metadata.schema.json",
    ROOT / "schemas" / "task_record_v2.schema.json",
)
OUTPUT_JSON = ROOT / "config" / "experiment_freeze_v2.4.0.json"
OUTPUT_MARKDOWN = ROOT / "docs" / "experiment_freeze_v2.4.0.md"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_record() -> dict:
    model_set = json.loads(MODEL_SET.read_text(encoding="utf-8"))
    with MANIFEST.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    prompts = sorted(PROMPTS.glob("*.txt"))
    return {
        "freeze_record_version": "experiment-freeze-v2.4.0",
        "freeze_record_created_at_utc": utc_now(),
        "dataset_strategy": "fresh_separate_360_observation_experiment",
        "protocol_amendment": "Only preserved non-retryable failed observations may be skipped so later manifest rows continue; no retry, regeneration, substitution, or generation-parameter change.",
        "historical_v2_3_context": {
            "status": "prospectively_stopped",
            "stop_run_id": "API-v2.3-AUTH-FED-02-M1-R01",
            "stop_reason": "Frozen v2.3 required a non-retryable provider failure to stop the batch without skipping or substitution.",
            "preservation": "All v2.3 observations and artifacts remain immutable and excluded from the fresh v2.4 dataset."
        },
        "task_set": {"version": "final-2.0.0", "path": str(TASKS.relative_to(ROOT)), "sha256": digest(TASKS), "record_count": 30},
        "model_set": {"version": model_set["model_set_version"], "path": str(MODEL_SET.relative_to(ROOT)), "sha256": digest(MODEL_SET), "models": [{"condition_id": m["condition_id"], "model_id": m["model_id"], "api_provider": m["api_provider"], "provider_pin": m["openrouter_routing"]["underlying_provider_slug"] if m["api_provider"] == "OpenRouter" else "not_applicable"} for m in model_set["models"]]},
        "prompt_template": {"version": "2.4.0", "path": str(TEMPLATE.relative_to(ROOT)), "sha256": digest(TEMPLATE)},
        "rendered_prompts": [{"path": str(path.relative_to(ROOT)), "sha256": digest(path)} for path in prompts],
        "official_manifest": {
            "path": str(MANIFEST.relative_to(ROOT)),
            "sha256": digest(MANIFEST),
            "row_count": len(rows),
            "pending_rows": len(rows),
            "completed_rows": 0,
            "rows_per_model": dict(sorted(Counter(row["model_condition_id"] for row in rows).items())),
            "rows_per_repetition": dict(sorted(Counter(row["run_repetition"] for row in rows).items())),
            "rows_per_category": dict(sorted(Counter(row["category"] for row in rows).items())),
        },
        "sampling_parameters": model_set["candidate_common_parameters"] | {
            "seed": "not_controlled",
            "messages": "one_user_message_only",
            "previous_context": False,
            "tools_exposed": False,
            "browsing": False,
            "retrieval": False,
            "execution": False,
        },
        "retry_policy": model_set["retry_policy"],
        "batch_pacing": {
            "sequential_requests_only": True,
            "minimum_artificial_interval_seconds": 0,
            "provider_enforced_throttling": "HTTP 429 Retry-After and configured HTTP 5xx/transport retries remain unchanged from v2.3.",
        },
        "failure_policy": {
            "preserve_failed_observation_once": True,
            "continue_after_preserved_failure": True,
            "retry_failed_observation": False,
            "regenerate_for_success": False,
            "substitute_model_or_provider": False,
            "exclude_from_primary_shr_phr_denominators": True,
        },
        "schemas": [{"path": str(path.relative_to(ROOT)), "sha256": digest(path)} for path in SCHEMAS],
    }


def markdown(record: dict) -> str:
    prompts = "\n".join(f"| `{item['path']}` | `{item['sha256']}` |" for item in record["rendered_prompts"])
    return f"""# Experiment Freeze Record — v2.4.0

This record was created prospectively at `{record['freeze_record_created_at_utc']}` before v2.4 collection.

## Dataset strategy

v2.4 is a fresh, separate 360-observation experiment. It does not reuse v2.3 observations or state. v2.3 stopped prospectively at `{record['historical_v2_3_context']['stop_run_id']}` because its frozen rule required a non-retryable provider failure to stop the batch.

## Frozen inputs

- Task set `{record['task_set']['version']}`: `{record['task_set']['sha256']}` (`{record['task_set']['path']}`)
- Model set `{record['model_set']['version']}`: `{record['model_set']['sha256']}` (`{record['model_set']['path']}`)
- Prompt template `{record['prompt_template']['version']}`: `{record['prompt_template']['sha256']}` (`{record['prompt_template']['path']}`)
- Official v2.4 manifest: `{record['official_manifest']['sha256']}` (`{record['official_manifest']['path']}`)
- Official manifest rows: 360 total; 360 pending

## Protocol

The only substantive change from v2.3 is failure continuation: a non-retryable provider failure is preserved exactly once with explicit evidence, excluded from primary SHR/PHR denominators, and skipped on future invocations so later manifest rows continue sequentially. It is never retried, regenerated, or replaced by another model/provider.

The 30 tasks, wording, rendered prompt bytes, four model conditions, provider pins, no-fallback/no-tools rules, temperature 0.6, top-p 0.95, 12,000 maximum output tokens, seed behavior, request structure, truncation semantics, infrastructure retry/backoff, and zero researcher-imposed artificial pacing are unchanged.

## Rendered prompts

| Path | SHA-256 |
| --- | --- |
{prompts}
"""


def main() -> int:
    import argparse
    import sys
    parser = argparse.ArgumentParser(description="Create or verify v2.4 experiment freeze record")
    parser.add_argument("--json", type=Path, default=OUTPUT_JSON)
    parser.add_argument("--markdown", type=Path, default=OUTPUT_MARKDOWN)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    json_path = args.json.resolve()
    markdown_path = args.markdown.resolve()
    try:
        if args.check:
            if not json_path.exists() or not markdown_path.exists():
                raise ValueError("Freeze record files do not exist")
            record = json.loads(json_path.read_text(encoding="utf-8"))
            for section in ("task_set", "model_set", "prompt_template", "official_manifest"):
                path = ROOT / record[section]["path"]
                if digest(path) != record[section]["sha256"]:
                    raise ValueError(f"Artifact hash mismatch for {path}")
            for prompt in record["rendered_prompts"]:
                path = ROOT / prompt["path"]
                if digest(path) != prompt["sha256"]:
                    raise ValueError(f"Rendered prompt hash mismatch for {path}")
            for schema in record["schemas"]:
                path = ROOT / schema["path"]
                if digest(path) != schema["sha256"]:
                    raise ValueError(f"Schema hash mismatch for {path}")
            if markdown_path.read_text(encoding="utf-8") != markdown(record):
                raise ValueError("Markdown freeze documentation does not match freeze record")
            print(f"PASS: verified v2.4 freeze records at {json_path.relative_to(ROOT)} and {markdown_path.relative_to(ROOT)}")
            return 0
        if json_path.exists() or markdown_path.exists():
            raise ValueError("Refusing to overwrite an existing freeze record")
        record = build_record()
        json_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        markdown_path.write_text(markdown(record), encoding="utf-8")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"PASS: wrote v2.4 freeze records {json_path.relative_to(ROOT)} and {markdown_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
