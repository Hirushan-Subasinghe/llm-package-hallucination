#!/usr/bin/env python3
"""Create or verify the independent prospective v2.6 freeze; never overwrite it."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from collect_api_run import load_config
from create_api_manifest import csv_bytes, load_frozen_tasks, make_rows
from render_api_prompts import expected_rendered

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "prompts/tasks/final_2.0.0.jsonl"
MODEL_SET = ROOT / "config/api_model_set_1.4.0.json"
TEMPLATE = ROOT / "prompts/prompt_template_v2.6.0.md"
PROMPTS = ROOT / "data/generated_prompts/v2.6.0"
MANIFEST = ROOT / "manifests/api_final_v2.6.0_manifest.csv"
STATE = ROOT / "data/final/api_batch_state_v2.6.0.json"
OUTPUT_JSON = ROOT / "config/experiment_freeze_v2.6.0.json"
OUTPUT_MARKDOWN = ROOT / "docs/experiment_freeze_v2.6.0.md"
SCHEMAS = (
    ROOT / "schemas/api_model_set_v2_6.schema.json",
    ROOT / "schemas/api_manifest_row.schema.json",
    ROOT / "schemas/api_collection_metadata.schema.json",
    ROOT / "schemas/task_record_v2.schema.json",
)
CEILINGS = {"M1": 64000, "M2": 32768, "M3": 65536, "M4": 65536}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_record(*, preserved_initial_state_sha256: str | None = None) -> dict:
    config = load_config(MODEL_SET)
    old = json.loads((ROOT / "config/api_model_set_1.3.0.json").read_text(encoding="utf-8"))
    if config["task_set_sha256"] != digest(TASKS):
        raise ValueError("Task-set hash differs from the frozen task set")
    if {m["condition_id"]: m["max_output_tokens"] for m in config["models"]} != CEILINGS:
        raise ValueError("v2.6 output ceilings do not match the protocol")
    if [m["model_id"] for m in config["models"]] != [m["model_id"] for m in old["models"]]:
        raise ValueError("v2.6 model identities differ from v2.5")
    for key in ("interaction_protocol", "retry_policy", "batch_pacing"):
        if config[key] != old[key]:
            raise ValueError(f"v2.6 changed frozen {key}")
    old_common = dict(old["candidate_common_parameters"])
    old_common.pop("max_output_tokens")
    if config["candidate_common_parameters"] != old_common:
        raise ValueError("v2.6 changed common sampling parameters")
    for index in (0, 2, 3):
        current = dict(config["models"][index]); current.pop("max_output_tokens")
        if current != old["models"][index]:
            raise ValueError("Non-M2 model condition changed beyond output ceiling")
    m2 = config["models"][1]
    routing = m2.get("openrouter_routing", {})
    if (m2["api_provider"], m2["api_base_url"], m2["api_key_environment_variable"], m2["output_token_parameter"]) != ("OpenRouter", "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY", "max_tokens"):
        raise ValueError("M2 OpenRouter endpoint or request field differs")
    if routing != {"pinning_status": "pinned", "underlying_provider_slug": "darkbloom", "underlying_provider_name": "Darkbloom", "allow_fallbacks": False, "require_parameters": True, "allow_unpinned_after_documented_decision": False, "only_pinned_provider": True}:
        raise ValueError("M2 Darkbloom-only routing differs")
    expected_m2 = dict(old["models"][1])
    expected_m2.pop("provider_owner")
    expected_m2.update(api_provider="OpenRouter", api_base_url="https://openrouter.ai/api/v1", api_key_environment_variable="OPENROUTER_API_KEY", provider_model_status_at_freeze="listed_on_openrouter", output_token_parameter="max_tokens", max_output_tokens=32768, openrouter_routing=routing)
    if m2 != expected_m2:
        raise ValueError("M2 changed beyond required provider-specific fields and ceiling")
    if TEMPLATE.read_bytes() != (ROOT / "prompts/prompt_template_v2.5.0.md").read_bytes():
        raise ValueError("v2.6 prompt template differs from v2.5")
    expected = expected_rendered(TEMPLATE)
    prompts = sorted(PROMPTS.glob("*.txt"))
    if len(prompts) != 30 or {p.stem for p in prompts} != set(expected):
        raise ValueError("v2.6 rendered prompt set is incomplete")
    for path in prompts:
        if path.read_bytes() != expected[path.stem] or path.read_bytes() != (ROOT / "data/generated_prompts/v2.5.0" / path.name).read_bytes():
            raise ValueError(f"v2.6 rendered prompt differs: {path.name}")
    with MANIFEST.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 360 or len({row["run_id"] for row in rows}) != 360 or any(row["collection_status"] != "pending" or not row["run_id"].startswith("API-v2.6-") for row in rows):
        raise ValueError("v2.6 manifest must have 360 unique pending rows")
    if MANIFEST.read_bytes() != csv_bytes(make_rows(config, load_frozen_tasks(), PROMPTS, "API-v2.6")):
        raise ValueError("v2.6 manifest is not deterministic")
    state = json.loads(STATE.read_text(encoding="utf-8"))
    if state.get("manifest_sha256") != digest(MANIFEST):
        raise ValueError("v2.6 state belongs to a different manifest")
    state_is_fresh = state.get("events") == [] and state.get("provider_next_allowed_at_epoch") == {}
    if not state_is_fresh and preserved_initial_state_sha256 is None:
        raise ValueError("v2.6 initial state is not fresh")
    if state_is_fresh and list((ROOT / "data/final/raw").glob("API-v2.6-*")):
        raise ValueError("v2.6 raw observation already exists")
    return {
        "freeze_record_version": "experiment-freeze-v2.6.0",
        "freeze_record_created_at_utc": utc_now(),
        "dataset_strategy": "fresh_separate_360_observation_experiment",
        "historical_v2_5_context": {"status": "prospectively_stopped", "primary_metric_inclusion": False, "preservation": "All v2.5 observations remain separate methodological evidence."},
        "protocol_amendment": "M2 moves from Groq to Darkbloom-only OpenRouter; output ceilings become model-specific. Other frozen conditions remain unchanged.",
        "final_protocol_intent": True,
        "remaining_ceiling_hits": "preserve_once_as_right_censored_truncations_without_restart",
        "initial_batch_state": {"path": str(STATE.relative_to(ROOT)), "sha256": digest(STATE) if state_is_fresh else preserved_initial_state_sha256, "collected_observations": 0},
        "task_set": {"version": "final-2.0.0", "path": str(TASKS.relative_to(ROOT)), "sha256": digest(TASKS), "record_count": 30},
        "model_set": {"version": config["model_set_version"], "path": str(MODEL_SET.relative_to(ROOT)), "sha256": digest(MODEL_SET), "models": [{"condition_id": m["condition_id"], "model_id": m["model_id"], "api_provider": m["api_provider"], "provider_pin": m["openrouter_routing"]["underlying_provider_slug"] if m["api_provider"] == "OpenRouter" else "not_applicable", "max_output_tokens": m["max_output_tokens"]} for m in config["models"]]},
        "prompt_template": {"version": "2.6.0", "path": str(TEMPLATE.relative_to(ROOT)), "sha256": digest(TEMPLATE)},
        "rendered_prompts": [{"path": str(path.relative_to(ROOT)), "sha256": digest(path)} for path in prompts],
        "official_manifest": {"path": str(MANIFEST.relative_to(ROOT)), "sha256": digest(MANIFEST), "row_count": 360, "pending_rows": 360, "completed_rows": 0, "rows_per_model": dict(sorted(Counter(row["model_condition_id"] for row in rows).items())), "rows_per_repetition": dict(sorted(Counter(row["run_repetition"] for row in rows).items())), "rows_per_category": dict(sorted(Counter(row["category"] for row in rows).items()))},
        "sampling_parameters": config["candidate_common_parameters"] | {"max_output_tokens_by_model": CEILINGS, "messages": "one_user_message_only", "previous_context": False, "tools_exposed": False, "browsing": False, "retrieval": False, "execution": False},
        "retry_policy": config["retry_policy"],
        "batch_pacing": {"sequential_requests_only": True, "minimum_artificial_interval_seconds": 0, "provider_enforced_throttling": "HTTP 429 Retry-After and configured HTTP 5xx/transport retries remain unchanged from v2.5."},
        "failure_policy": {"preserve_failed_observation_once": True, "continue_after_preserved_failure": True, "retry_failed_observation": False, "regenerate_for_success": False, "substitute_model_or_provider": False, "exclude_from_primary_shr_phr_denominators": True},
        "truncation_policy": {"preserve_truncated_observation_once": True, "regenerate_for_truncation": False, "exclude_from_primary_shr_phr_denominators": True},
        "schemas": [{"path": str(path.relative_to(ROOT)), "sha256": digest(path)} for path in SCHEMAS],
        "provider_evidence": ["https://openrouter.ai/qwen/qwen3.8-27b", "https://openrouter.ai/provider/darkbloom", "https://openrouter.ai/docs/guides/routing/provider-selection", "https://openrouter.ai/cohere/north-mini-code:free", "https://console.groq.com/docs/model/openai/gpt-oss-120b", "https://openrouter.ai/nvidia/nemotron-3-ultra-550b-a55b:free"],
    }


def markdown(record: dict) -> str:
    model_rows = "\n".join(f"| {m['condition_id']} | `{m['model_id']}` | {m['api_provider']} | `{m['provider_pin']}` | {m['max_output_tokens']} |" for m in record["model_set"]["models"])
    prompt_rows = "\n".join(f"| `{item['path']}` | `{item['sha256']}` |" for item in record["rendered_prompts"])
    return f"""# Experiment Freeze Record — v2.6.0

Created prospectively at `{record['freeze_record_created_at_utc']}` before v2.6 collection.

v2.5 was prospectively stopped. v2.6 is a fresh independent 360-observation experiment beginning at observation 1. No v2.5 observation is reused or included in v2.6 primary SHR/PHR. No v2.6 result exists yet.

## Frozen inputs

- Task set: `{record['task_set']['sha256']}` (`{record['task_set']['path']}`)
- Model set: `{record['model_set']['sha256']}` (`{record['model_set']['path']}`)
- Prompt template: `{record['prompt_template']['sha256']}` (`{record['prompt_template']['path']}`)
- Manifest: `{record['official_manifest']['sha256']}` (`{record['official_manifest']['path']}`), 360 unique pending rows
- Initial state: `{record['initial_batch_state']['sha256']}` (`{record['initial_batch_state']['path']}`), zero observations/events/pacing history

## Model conditions

| Condition | Model | API provider | Underlying provider pin | Max output tokens |
| --- | --- | --- | --- | ---: |
{model_rows}

M2 uses OpenRouter `provider.order` and `provider.only` restricted to `darkbloom`, with `allow_fallbacks: false` and `require_parameters: true`. The model ID remains `qwen/qwen3.8-27b`. No model fallback is supplied.

The v2.6 provider preflight used static authoritative documentation and the repository's request builder. It did not send a live compatibility request. The model-set `final_preflight_timestamp_utc` records completion of that documentation review.

## Protocol

The v2.5 to v2.6 changes are M2's Groq-to-OpenRouter provider move and the four model-specific output ceilings above. The 30 tasks, template and rendered prompt bytes, three repetitions, temperature 0.6, top_p 0.95, uncontrolled seed, single user message, no tools, browsing, retrieval, code execution or function calling, no substitution, infrastructure retry/backoff, preserved-failure continuation, truncation handling, and zero artificial pacing remain unchanged.

v2.6 is intended as the final protocol version. Remaining ceiling hits are preserved once as right-censored truncations, excluded from primary SHR/PHR, and do not trigger another restart. Failed observations are also preserved once and excluded from primary SHR/PHR. No live v2.6 API request was sent during freeze preparation.

## Provider evidence

""" + "".join(f"- {url}\n" for url in record["provider_evidence"]) + f"""
## Rendered prompts

| Path | SHA-256 |
| --- | --- |
{prompt_rows}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Create or verify the v2.6 freeze")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.check:
            record = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
            state = json.loads(STATE.read_text(encoding="utf-8"))
            progressed = bool(state.get("events"))
            expected = build_record(preserved_initial_state_sha256=record["initial_batch_state"]["sha256"] if progressed else None)
            expected["freeze_record_created_at_utc"] = record["freeze_record_created_at_utc"]
            if record != expected or OUTPUT_MARKDOWN.read_text(encoding="utf-8") != markdown(record):
                raise ValueError("v2.6 freeze differs from prospective inputs")
            print("PASS: verified v2.6 freeze JSON, Markdown, hashes, prompts, manifest, state, and zero raw observations")
            return 0
        if OUTPUT_JSON.exists() or OUTPUT_MARKDOWN.exists():
            raise ValueError("Refusing to overwrite an existing v2.6 freeze record")
        record = build_record()
        with OUTPUT_JSON.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(record, indent=2, sort_keys=True) + "\n")
        with OUTPUT_MARKDOWN.open("x", encoding="utf-8") as handle:
            handle.write(markdown(record))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: wrote v2.6 freeze JSON and Markdown")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
