#!/usr/bin/env python3
"""Create the immutable pre-smoke experiment freeze record."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

from collect_api_run import DEFAULT_CONFIG, load_config, utc_now
from create_api_manifest import DEFAULT_MANIFEST_PATH
from render_api_prompts import EXPECTED_TASK_SHA256, TASKS_PATH


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON_PATH = ROOT / "config" / "experiment_freeze_v2.3.0.json"
DEFAULT_MARKDOWN_PATH = ROOT / "docs" / "experiment_freeze_v2.3.0.md"
DEFAULT_MANIFEST_PATH = ROOT / "manifests" / "api_final_v2.3.0_manifest.csv"
DEFAULT_TEMPLATE_PATH = ROOT / "prompts" / "prompt_template_v2.3.0.md"
DEFAULT_RENDERED_DIR = ROOT / "data" / "generated_prompts" / "v2.3.0"

JSON_PATH_V2_1 = ROOT / "config" / "experiment_freeze_v2.1.0.json"
MARKDOWN_PATH_V2_1 = ROOT / "docs" / "experiment_freeze_v2.1.0.md"
JSON_PATH_V2_0 = ROOT / "config" / "experiment_freeze_2026-09-16.json"
MARKDOWN_PATH_V2_0 = ROOT / "docs" / "experiment_freeze_2026-09-16.md"

SCHEMA_PATHS = (
    ROOT / "schemas" / "api_model_set.schema.json",
    ROOT / "schemas" / "api_manifest_row.schema.json",
    ROOT / "schemas" / "api_collection_metadata.schema.json",
    ROOT / "schemas" / "task_record_v2.schema.json",
    ROOT / "schemas" / "interface_suitability.schema.json",
)


def build_v2_3_record() -> dict:
    config = load_config(DEFAULT_CONFIG)
    if config.get("model_set_version") != "api-model-set-1.2.0" or config.get("status") != "frozen_for_collection":
        raise ValueError("v2.3 model configuration is not frozen")
    if digest(TASKS_PATH) != EXPECTED_TASK_SHA256:
        raise ValueError("Task file hash changed before v2.3 freeze record creation")
    prompts = sorted(DEFAULT_RENDERED_DIR.glob("*.txt"))
    if len(prompts) != 30:
        raise ValueError("Expected exactly 30 rendered v2.3 prompts")
    with DEFAULT_MANIFEST_PATH.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 360 or any(row["collection_status"] != "pending" for row in rows):
        raise ValueError("Official v2.3 manifest is not a 360-row all-pending plan")
    return {
        "freeze_record_version": "experiment-freeze-v2.3.0", "freeze_record_created_at_utc": utc_now(), "official_v2_3_collection_started": False, "official_v2_3_observations_count": 0,
        "historical_v2_2_context": {"status": "prospectively_stopped", "final_inventory": {"planned": 360, "completed": 6, "truncated": 4, "pending": 350, "total_collected_observations": 10}, "preservation_and_exclusion": "All 10 v2.2 observations remain immutable methodological evidence in data/final/raw/ and are excluded from the fresh v2.3 primary 360-observation dataset and metrics.", "stop_reason": "v2.2 was prospectively stopped because its fixed researcher-imposed provider spacing was unnecessarily conservative under the final collection window; no model, task, prompt, routing, sampling, retry, or truncation semantics are carried differently into v2.3."},
        "task_set": {"version": "final-2.0.0", "path": str(TASKS_PATH.relative_to(ROOT)), "sha256": digest(TASKS_PATH), "record_count": 30, "categories": {"AUTH-FED": 5, "DATA-ADV": 5, "DIST-OBS": 5, "DOC-BINARY": 5, "ENT-INT": 5, "PKI-CRYPTO": 5}},
        "model_set": {"version": config["model_set_version"], "path": str(DEFAULT_CONFIG.relative_to(ROOT)), "sha256": digest(DEFAULT_CONFIG), "frozen_at_utc": config["frozen_at_utc"], "final_preflight_timestamp_utc": config["final_preflight_timestamp_utc"], "models": [{"condition_id": model["condition_id"], "model_id": model["model_id"], "api_provider": model["api_provider"], "provider_pin": model["openrouter_routing"]["underlying_provider_slug"] if model["api_provider"] == "OpenRouter" else "not_applicable"} for model in config["models"]]},
        "prompt_template": {"version": "2.3.0", "path": str(DEFAULT_TEMPLATE_PATH.relative_to(ROOT)), "sha256": digest(DEFAULT_TEMPLATE_PATH)},
        "sampling_parameters": {"temperature": 0.6, "top_p": 0.95, "max_output_tokens": 12000, "seed": "omitted", "messages": "one_user_message_only", "previous_context": False, "tools_exposed": False, "tool_choice": "none", "browsing": False, "retrieval": False, "execution": False, "model_specific_reasoning_effort": "omitted"},
        "retry_policy": config["retry_policy"], "batch_pacing": {"sequential_requests_only": True, "minimum_artificial_interval_seconds": 0, "provider_enforced_throttling": "HTTP 429 obeys Retry-After when supplied; otherwise the frozen infrastructure backoff applies. Non-retryable quota, credit, account-limit, or other provider failures stop the batch without skipping or substitution."},
        "collection_ordering_rule": "Deterministic balanced Latin-square rotation per task and repetition: (task_index + repetition_offset) % 4 across 360 rows.", "truncation_rule": "Provider-valid response with finish_reason 'length' is preserved exactly once with status TRUNCATED under its original run ID without retry. Excluded from primary SHR denominator and primary PHR occurrence population; reported separately in quality metrics.",
        "rendered_prompts": [{"path": str(path.relative_to(ROOT)), "sha256": digest(path)} for path in prompts],
        "official_manifest": {"path": str(DEFAULT_MANIFEST_PATH.relative_to(ROOT)), "sha256": digest(DEFAULT_MANIFEST_PATH), "row_count": len(rows), "rows_per_model": dict(sorted(Counter(row["model_condition_id"] for row in rows).items())), "rows_per_repetition": dict(sorted(Counter(row["run_repetition"] for row in rows).items())), "rows_per_category": dict(sorted(Counter(row["category"] for row in rows).items())), "completed_rows": 0, "pending_rows": len(rows)},
        "schemas": [{"path": str(path.relative_to(ROOT)), "sha256": digest(path)} for path in SCHEMA_PATHS],
    }


def markdown_v2_3(record: dict) -> str:
    prompt_lines = "\n".join(f"| `{item['path']}` | `{item['sha256']}` |" for item in record["rendered_prompts"])
    return f"""# Experiment Freeze Record — v2.3.0

This record was generated at `{record['freeze_record_created_at_utc']}` **before any official v2.3 API generation request**. It defines a fresh 360-observation dataset; all rows are pending and no v2.3 raw observation directory exists.

## v2.2 Stop and Dataset Separation

v2.2 was prospectively stopped with its final inventory at 360 planned, 6 completed, 4 truncated, and 350 pending (10 total collected observations). Those 10 immutable v2.2 observations remain methodological evidence only and are excluded from all v2.3 primary metrics. v2.3 begins a new, separate 360-observation dataset.

The sole intended methodological difference from v2.2 is removal of the unnecessarily conservative researcher-imposed fixed provider spacing under a tight final collection window. Model identities, provider pins, no-fallback rule, task set, prompt text, interaction constraints, sampling parameters, retry philosophy, and truncation handling are unchanged. Payment or account tier is infrastructure availability only; it is not an experimental condition if the frozen model ID, routing, prompt, and generation parameters remain identical.

## Frozen Artifacts

- Task set `{record['task_set']['version']}`: `{record['task_set']['sha256']}` (`{record['task_set']['path']}`)
- Model set `{record['model_set']['version']}`: `{record['model_set']['sha256']}` (`{record['model_set']['path']}`)
- Prompt template `{record['prompt_template']['version']}`: `{record['prompt_template']['sha256']}` (`{record['prompt_template']['path']}`)
- Official v2.3 manifest: `{record['official_manifest']['sha256']}` (`{record['official_manifest']['path']}`)
- Official manifest rows: {record['official_manifest']['row_count']} total; {record['official_manifest']['pending_rows']} pending; {record['official_manifest']['completed_rows']} completed

## Collection and Failure Policy

- Sequential collection only. The minimum artificial interval after a successful request is 0 seconds; the next manifest row is attempted immediately.
- Provider-enforced throttling remains binding: HTTP 429 obeys `Retry-After` when supplied, otherwise the frozen infrastructure backoff applies. HTTP 5xx and transport failures use only the frozen infrastructure retry policy.
- A quota, credit, account-limit, or other non-retryable provider failure is preserved as failed infrastructure evidence and stops the batch without skipping, substituting providers/models, or changing a `:free` route to a paid route.
- `finish_reason: length` is an official TRUNCATED observation, preserved exactly once and never regenerated merely for truncation.
- Exactly one user message; no prior context, tools, browsing, retrieval, filesystem, external files, or code execution. Temperature 0.6, top-p 0.95, maximum completion tokens 12000, seed omitted/not controlled.

## Rendered Prompts

| Path | SHA-256 |
| --- | --- |
{prompt_lines}
"""


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_v2_2_record() -> dict:
    config = load_config(DEFAULT_CONFIG)
    if config.get("status") != "frozen_for_collection":
        raise ValueError("Model configuration is not frozen")
    if digest(TASKS_PATH) != EXPECTED_TASK_SHA256:
        raise ValueError("Task file hash changed before freeze record creation")
    prompts = sorted(DEFAULT_RENDERED_DIR.glob("*.txt"))
    if len(prompts) != 30:
        raise ValueError("Expected exactly 30 rendered v2.2 prompts")
    with DEFAULT_MANIFEST_PATH.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 360 or any(row["collection_status"] != "pending" for row in rows):
        raise ValueError("Official v2.2 manifest is not a 360-row all-pending plan")
    return {
        "freeze_record_version": "experiment-freeze-v2.2.0",
        "freeze_record_created_at_utc": utc_now(),
        "official_v2_2_collection_started": False,
        "official_v2_2_observations_count": 0,
        "historical_v2_0_context": {
            "aborted_reason": "Official v2.0 collection stopped after exactly two observations (API-AUTH-FED-01-M1-R01 and API-AUTH-FED-01-M2-R01) because models without explicit text-only instructions emitted structured tool_calls (M1) or simulated <tool_call> markup (M2) rather than standalone inline implementation.",
            "preserved_v2_0_observations": [
                "API-AUTH-FED-01-M1-R01",
                "API-AUTH-FED-01-M2-R01",
            ],
            "exclusion_from_v2_2": "The two preserved v2.0 observations remain immutable methodological evidence but are strictly excluded from the final v2.2 dataset.",
        },
        "historical_v2_1_context": {
            "aborted_reason": "Official v2.1 collection was stopped after exactly four observations (API-v2.1-AUTH-FED-01-M1-R01 through M4-R01). All four models passed the text-only interface validity check with substantive inline implementation and zero tool calls. However, 3 of 4 observations (M2, M3, M4) were truncated at the 6000-token ceiling and the fourth (M1) finished only 107 tokens below the ceiling (5893/6000). v2.1 was halted to increase the common output ceiling from 6000 to 12000 tokens in v2.2.0.",
            "preserved_v2_1_observations": [
                "API-v2.1-AUTH-FED-01-M1-R01",
                "API-v2.1-AUTH-FED-01-M2-R01",
                "API-v2.1-AUTH-FED-01-M3-R01",
                "API-v2.1-AUTH-FED-01-M4-R01",
            ],
            "exclusion_from_v2_2": "The four preserved v2.1 observations remain immutable methodological evidence in data/final/raw/ but are strictly excluded from the final v2.2 dataset and research metrics.",
        },
        "interface_suitability_gate": {
            "protocol_version": "interface-suitability-2.1.0",
            "configuration_path": "config/interface_suitability_v2.1.0.json",
            "gate_definition": "All conditions must return HTTP 200, exact requested model, no structured tool_calls, no simulated tool markup, substantive inline implementation, finish reason stop, and zero tools exposed or executed.",
            "task_id": "SUITABILITY-API-001",
            "results": {
                "M1": {"model_id": "cohere/north-mini-code:free", "status": "PASS", "completion_tokens": 1536, "finish_reason": "stop"},
                "M2": {"model_id": "qwen/qwen3.8-27b", "status": "PASS", "completion_tokens": 3211, "finish_reason": "stop"},
                "M3": {"model_id": "openai/gpt-oss-120b", "status": "PASS", "completion_tokens": 2256, "finish_reason": "stop"},
                "M4": {"model_id": "nvidia/nemotron-3-ultra-550b-a55b:free", "status": "PASS", "completion_tokens": 1486, "finish_reason": "stop"},
            },
            "suitability_data_excluded": "Task SUITABILITY-API-001 and all responses under data/suitability/api/v2.1.0/ are excluded from the official research dataset and hallucination metrics.",
        },
        "task_set": {
            "version": "final-2.0.0",
            "path": str(TASKS_PATH.relative_to(ROOT)),
            "sha256": digest(TASKS_PATH),
            "record_count": 30,
            "categories": {
                "AUTH-FED": 5,
                "DATA-ADV": 5,
                "DIST-OBS": 5,
                "DOC-BINARY": 5,
                "ENT-INT": 5,
                "PKI-CRYPTO": 5,
            },
        },
        "model_set": {
            "version": config["model_set_version"],
            "path": str(DEFAULT_CONFIG.relative_to(ROOT)),
            "sha256": digest(DEFAULT_CONFIG),
            "frozen_at_utc": config["frozen_at_utc"],
            "final_preflight_timestamp_utc": config["final_preflight_timestamp_utc"],
            "models": [
                {
                    "condition_id": model["condition_id"],
                    "model_id": model["model_id"],
                    "api_provider": model["api_provider"],
                    "provider_pin": (
                        model["openrouter_routing"]["underlying_provider_slug"]
                        if model["api_provider"] == "OpenRouter"
                        else "not_applicable"
                    ),
                }
                for model in config["models"]
            ],
        },
        "prompt_template": {
            "version": "2.2.0",
            "path": str(DEFAULT_TEMPLATE_PATH.relative_to(ROOT)),
            "sha256": digest(DEFAULT_TEMPLATE_PATH),
        },
        "sampling_parameters": {
            "temperature": 0.6,
            "top_p": 0.95,
            "max_output_tokens": 12000,
            "seed": "omitted",
            "messages": "one_user_message_only",
            "previous_context": False,
            "tools_exposed": False,
            "tool_choice": "none",
            "browsing": False,
            "retrieval": False,
            "execution": False,
            "model_specific_reasoning_effort": "omitted",
        },
        "collection_ordering_rule": "Deterministic balanced Latin-square rotation per task and repetition: (task_index + repetition_offset) % 4 across 360 rows.",
        "truncation_rule": "Provider-valid response with finish_reason 'length' is preserved with status TRUNCATED under original run ID without retry. Excluded from primary SHR denominator and primary PHR occurrence population; reported separately in quality metrics.",
        "methodology_versions": {
            "risk_model": "risk-model-1.0.0",
            "hallucination_taxonomy": "package-hallucination-taxonomy-1.0.0",
        },
        "rendered_prompts": [
            {"path": str(path.relative_to(ROOT)), "sha256": digest(path)} for path in prompts
        ],
        "official_manifest": {
            "path": str(DEFAULT_MANIFEST_PATH.relative_to(ROOT)),
            "sha256": digest(DEFAULT_MANIFEST_PATH),
            "row_count": len(rows),
            "rows_per_model": dict(sorted(Counter(row["model_condition_id"] for row in rows).items())),
            "rows_per_repetition": dict(sorted(Counter(row["run_repetition"] for row in rows).items())),
            "rows_per_category": dict(sorted(Counter(row["category"] for row in rows).items())),
            "completed_rows": 0,
            "pending_rows": len(rows),
        },
        "schemas": [
            {"path": str(path.relative_to(ROOT)), "sha256": digest(path)} for path in SCHEMA_PATHS
        ],
    }


def markdown_v2_2(record: dict) -> str:
    prompt_lines = "\n".join(
        f"| `{item['path']}` | `{item['sha256']}` |" for item in record["rendered_prompts"]
    )
    schema_lines = "\n".join(
        f"- `{item['path']}` — `{item['sha256']}`" for item in record["schemas"]
    )
    return f"""# Experiment Freeze Record — v2.2.0

This record was generated at `{record['freeze_record_created_at_utc']}` **before any official v2.2 API generation request**. Zero official v2.2 observations existed when frozen, and all {record['official_manifest']['pending_rows']} official manifest rows are pending.

## Background & Historical Abort Context

- **v2.0 Stop Reason:** Official v2.0 collection was halted after exactly two observations (`API-AUTH-FED-01-M1-R01` and `API-AUTH-FED-01-M2-R01`) because models without explicit text-only wrapper instructions returned structured `tool_calls` (M1 Cohere) or simulated `<tool_call>` markup and repository-inspection requests (M2 Qwen) instead of inline code.
- **v2.1 Interface Validation & Token Ceiling Abort:** Official v2.1 collection added the standardized text-only wrapper and collected exactly one observation per model condition (`API-v2.1-AUTH-FED-01-M1-R01` through `M4-R01`). All four models passed the text-only interface gate with substantive inline implementation and zero tool calls. However, 3 of 4 models (M2, M3, M4) hit the 6000-token ceiling with `finish_reason: length` (TRUNCATED), and M1 stopped at 5893/6000 (107 tokens below ceiling). v2.1 collection was stopped before row 5 to double the output token ceiling from 6000 to 12000.
- **Evidence Preservation:** The two v2.0 observations and four v2.1 observations remain immutable methodological evidence in `data/final/raw/` and are strictly excluded from the final v2.2 dataset and research metrics.
- **Suitability Gate (D022 / D023):** Prior to freezing v2.1, all four models passed the prospective interface-suitability test (`SUITABILITY-API-001`) under the standardized text-only wrapper. All four returned HTTP 200, exact requested model ID, `finish_reason: "stop"`, zero structured tool calls, zero simulated tool markup, and substantive inline implementation without tools exposed or executed.

## Frozen Artifacts

- Task set `{record['task_set']['version']}`: `{record['task_set']['sha256']}` (`{record['task_set']['path']}`)
- Model set `{record['model_set']['version']}`: `{record['model_set']['sha256']}` (`{record['model_set']['path']}`)
- Prompt template `{record['prompt_template']['version']}`: `{record['prompt_template']['sha256']}` (`{record['prompt_template']['path']}`)
- Official v2.2 manifest: `{record['official_manifest']['sha256']}` (`{record['official_manifest']['path']}`)
- Official manifest rows: {record['official_manifest']['row_count']} total; {record['official_manifest']['pending_rows']} pending; {record['official_manifest']['completed_rows']} completed

## Model Conditions and Provider Pins

| Condition | Model ID | API Provider | Pinned Provider Routing |
| --- | --- | --- | --- |
| M1 | `cohere/north-mini-code:free` | OpenRouter | `cohere` |
| M2 | `qwen/qwen3.8-27b` | Groq | `not_applicable` |
| M3 | `openai/gpt-oss-120b` | Groq | `not_applicable` |
| M4 | `nvidia/nemotron-3-ultra-550b-a55b:free` | OpenRouter | `nvidia` |

## Standardized Stateless Text-Only Generation Protocol (12,000 Max Tokens)

- **Prompt Interface:** Standardized frozen text-only wrapper (`{record['prompt_template']['path']}`) appended to every task prompt (byte-for-byte identical to v2.1).
- **Sampling Parameters:** Temperature `{record['sampling_parameters']['temperature']}`, Top-p `{record['sampling_parameters']['top_p']}`, Max completion tokens `{record['sampling_parameters']['max_output_tokens']}` (increased from 6000), Seed omitted (`not_controlled`).
- **Interaction Constraints:** Exactly one user message per request, no prior context, no tools exposed (`tool_choice: "{record['sampling_parameters']['tool_choice']}"`), no browsing, no retrieval augmentation, no code execution, no reasoning-effort parameter.
- **Collection Ordering:** Deterministic balanced Latin-square rotation per task and repetition: `(task_index + repetition_offset) % 4` across {record['official_manifest']['row_count']} contiguous rows.
- **Truncation Policy:** Provider-valid response with `finish_reason: "length"` receives operational status `TRUNCATED` and is preserved without retry. Excluded from primary SHR denominator and primary PHR occurrence population; reported separately in quality metrics.
- **Methodology Versions:** Risk Model `{record['methodology_versions']['risk_model']}`; Hallucination Taxonomy `{record['methodology_versions']['hallucination_taxonomy']}`.

## Rendered Prompts ({len(record['rendered_prompts'])} Tasks)

| Path | SHA-256 |
| --- | --- |
{prompt_lines}

## Schemas

{schema_lines}

## Experimental Data Boundaries

- Preserved v2.0 observations (`data/final/raw/API-AUTH-FED-01-M1-R01`, `data/final/raw/API-AUTH-FED-01-M2-R01`), preserved v2.1 observations (`data/final/raw/API-v2.1-AUTH-FED-01-M1-R01` through `M4-R01`), smoke tests (`data/smoke/api/`), suitability tests (`data/suitability/api/v2.1.0/`), and historical pilot data (`data/pilot/`) are completely excluded from the official v2.2 dataset and all research metrics.
- As of this freeze, exactly {record['official_v2_2_observations_count']} official v2.2 generation observations exist.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Create or verify experiment freeze record")
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN_PATH)
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
            if markdown_path.read_text(encoding="utf-8") != markdown_v2_3(record):
                raise ValueError("Markdown freeze documentation does not match freeze record")
            print(f"PASS: verified v2.3 freeze records at {json_path.relative_to(ROOT)} and {markdown_path.relative_to(ROOT)}")
            return 0
        if json_path.exists() or markdown_path.exists():
            raise ValueError("Refusing to overwrite an existing freeze record")
        record = build_v2_3_record()
        json_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        markdown_path.write_text(markdown_v2_3(record), encoding="utf-8")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"PASS: wrote v2.3 freeze records {json_path.relative_to(ROOT)} and {markdown_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
