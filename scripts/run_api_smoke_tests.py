#!/usr/bin/env python3
"""Run exactly one excluded infrastructure smoke generation per frozen condition."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

from collect_api_run import (
    DEFAULT_CONFIG,
    HTTPResult,
    TransportFailure,
    build_request,
    completion_status,
    HTTP_CLIENT,
    load_config,
    parse_valid_response,
    request_once,
    response_token_metadata,
    resolved_openrouter_provider,
    retry_after_seconds,
    safe_headers,
    sha256_bytes,
    STABLE_REQUEST_HEADERS,
    utc_now,
    write_exclusive,
    write_json,
)
from repository_guard import assert_live_collection_allowed


ROOT = Path(__file__).resolve().parents[1]
PROMPT_PATH = ROOT / "prompts" / "smoke" / "SMOKE-API-001.txt"
SMOKE_ROOT = ROOT / "data" / "smoke" / "api"
FREEZE_RECORD = ROOT / "config" / "experiment_freeze_2026-09-16.json"


def run_one(config: dict, model: dict, prompt: bytes, *, run_prefix: str = "SMOKE-API-001") -> dict:
    condition_id = model["condition_id"]
    if not re.fullmatch(r"SMOKE-API-[0-9]{3}", run_prefix):
        raise ValueError("Smoke run prefix must have the form SMOKE-API-NNN")
    run_id = f"{run_prefix}-{condition_id}"
    directory = SMOKE_ROOT / run_id
    directory.mkdir(parents=True, exist_ok=False)
    url, headers, request_body = build_request(config, model, prompt)
    payload = json.loads(request_body)
    if payload.get("tools") is not None or payload.get("tool_choice") != "none":
        raise ValueError("Smoke request does not enforce the frozen no-tools protocol")
    if payload.get("messages") != [{"role": "user", "content": prompt.decode("utf-8")}]:
        raise ValueError("Smoke request must contain exactly the smoke user message")

    write_exclusive(directory / "prompt.txt", prompt)
    write_exclusive(directory / "request.json", request_body)
    metadata = {
        "run_id": run_id,
        "phase": "smoke_excluded",
        "excluded_from_research_metrics": True,
        "smoke_task_id": "SMOKE-API-001",
        "smoke_attempt_series": run_prefix,
        "model_condition_id": condition_id,
        "requested_model_id": model["model_id"],
        "api_provider": model["api_provider"],
        "expected_underlying_provider": (model.get("openrouter_routing") or {}).get("underlying_provider_name"),
        "collection_status": "requesting",
        "generation_started_at_utc": utc_now(),
        "prompt_sha256": sha256_bytes(prompt),
        "request_sha256": sha256_bytes(request_body),
        "http_client": HTTP_CLIENT,
        "stable_request_headers": STABLE_REQUEST_HEADERS,
        "authorization_scheme": "Bearer (credential omitted)",
        "tools_exposed": False,
        "tool_choice": "none",
        "retry_history": [],
    }
    write_json(directory / "metadata.json", metadata, exclusive=True)

    retry_policy = config["retry_policy"]
    maximum_attempts = 1 + int(retry_policy["maximum_infrastructure_retries"])
    for attempt in range(1, maximum_attempts + 1):
        started = utc_now()
        try:
            result = request_once(url, headers, request_body, 180.0)
            attempt_dir = directory / "attempts" / f"attempt-{attempt:02d}"
            write_exclusive(attempt_dir / "http_response.bin", result.body)
            write_json(attempt_dir / "response_headers.json", safe_headers(result.headers), exclusive=True)
            history = {
                "attempt_number": attempt,
                "started_at_utc": started,
                "ended_at_utc": utc_now(),
                "outcome": "http_response",
                "http_status": result.status,
                "response_sha256": sha256_bytes(result.body),
            }
            metadata["retry_history"].append(history)
        except TransportFailure as error:
            metadata["retry_history"].append({
                "attempt_number": attempt,
                "started_at_utc": started,
                "ended_at_utc": utc_now(),
                "outcome": "transport_failure",
                "error_type": type(error).__name__,
            })
            if attempt < maximum_attempts:
                write_json(directory / "metadata.json", metadata)
                time.sleep(float(retry_policy["backoff_seconds"][attempt - 1]))
                continue
            metadata.update({"collection_status": "failed", "failure_reason": "transport_failure", "generation_ended_at_utc": utc_now()})
            write_json(directory / "metadata.json", metadata)
            return metadata

        retryable = result.status == 429 or 500 <= result.status <= 599
        if retryable and attempt < maximum_attempts:
            provider_delay = retry_after_seconds(result.headers) if result.status == 429 else None
            delay = max(float(retry_policy["backoff_seconds"][attempt - 1]), provider_delay or 0.0)
            history["retry_delay_seconds"] = delay
            write_json(directory / "metadata.json", metadata)
            time.sleep(delay)
            continue
        if result.status != 200:
            metadata.update({"collection_status": "failed", "failure_reason": f"http_status_{result.status}", "generation_ended_at_utc": utc_now(), "safe_response_headers": safe_headers(result.headers)})
            write_json(directory / "metadata.json", metadata)
            return metadata

        try:
            response, content = parse_valid_response(result.body)
        except ValueError as error:
            metadata.update({"collection_status": "failed", "failure_reason": str(error), "generation_ended_at_utc": utc_now()})
            write_json(directory / "metadata.json", metadata)
            return metadata
        message = response.get("choices", [{}])[0].get("message", {})
        tool_calls = message.get("tool_calls") or []
        resolved_provider = resolved_openrouter_provider(response) if model["api_provider"] == "OpenRouter" else "Groq"
        response_bytes = content.encode("utf-8")
        write_exclusive(directory / "provider_response.json", result.body)
        write_exclusive(directory / "response.md", response_bytes)
        status, response_completion_status = completion_status(response)
        metadata.update({
            "collection_status": status if not tool_calls else "protocol_violation",
            "response_completion_status": response_completion_status,
            "generation_ended_at_utc": utc_now(),
            "returned_model_id": response.get("model"),
            "resolved_underlying_provider": resolved_provider,
            "tool_calls_returned": len(tool_calls),
            "provider_response_sha256": sha256_bytes(result.body),
            "response_sha256": sha256_bytes(response_bytes),
            "token_usage": response.get("usage"),
            "response_token_metadata": response_token_metadata(response),
            "finish_reason": response.get("choices", [{}])[0].get("finish_reason"),
            "provider_response_id": response.get("id"),
            "safe_response_headers": safe_headers(result.headers),
        })
        write_json(directory / "metadata.json", metadata)
        return metadata
    raise AssertionError("Unreachable smoke retry state")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run excluded API infrastructure smoke observations")
    parser.add_argument("--conditions", nargs="+", choices=("M1", "M2", "M3", "M4"), default=["M1", "M2", "M3", "M4"])
    parser.add_argument("--run-prefix", default="SMOKE-API-001")
    parser.add_argument("--summary-name", default="smoke_summary.json")
    args = parser.parse_args()
    try:
        assert_live_collection_allowed()
        config = load_config(DEFAULT_CONFIG)
        if config.get("status") != "frozen_for_collection":
            raise ValueError("Smoke tests require a frozen model configuration")
        freeze = json.loads(FREEZE_RECORD.read_text(encoding="utf-8"))
        if freeze.get("freeze_record_written_before_smoke_tests") is not True:
            raise ValueError("Freeze record does not assert pre-smoke creation")
        prompt = PROMPT_PATH.read_bytes()
        selected = [model for model in config["models"] if model["condition_id"] in args.conditions]
        if [model["condition_id"] for model in selected] != args.conditions:
            raise ValueError("Smoke conditions must be unique and in frozen model order")
        directories = [SMOKE_ROOT / f"{args.run_prefix}-{model['condition_id']}" for model in selected]
        if any(path.exists() for path in directories):
            raise ValueError("Refusing to overwrite or repeat an existing smoke observation")
        results = []
        for model in selected:
            results.append(run_one(config, model, prompt, run_prefix=args.run_prefix))
        summary = {
            "smoke_task_id": "SMOKE-API-001",
            "smoke_attempt_series": args.run_prefix,
            "excluded_from_research_metrics": True,
            "results": [
                {
                    "model_condition_id": item["model_condition_id"],
                    "collection_status": item["collection_status"],
                    "returned_model_id": item.get("returned_model_id"),
                    "resolved_underlying_provider": item.get("resolved_underlying_provider"),
                    "tool_calls_returned": item.get("tool_calls_returned"),
                }
                for item in results
            ],
        }
        write_json(SMOKE_ROOT / args.summary_name, summary, exclusive=True)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(json.dumps(summary, sort_keys=True))
    return 0 if all(item["collection_status"] in {"completed", "truncated"} for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
