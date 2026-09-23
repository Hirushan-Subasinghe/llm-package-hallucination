#!/usr/bin/env python3
"""Run the four excluded v2.1 interface-suitability generations exactly once."""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

from collect_api_run import (
    DEFAULT_CONFIG,
    HTTP_CLIENT,
    STABLE_REQUEST_HEADERS,
    TransportFailure,
    build_request,
    load_config,
    request_once,
    resolved_openrouter_provider,
    response_token_metadata,
    retry_after_seconds,
    safe_headers,
    sha256_bytes,
    utc_now,
    write_exclusive,
    write_json,
)
from repository_guard import assert_live_collection_allowed


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = ROOT / "config" / "interface_suitability_v2.1.0.json"
TASK_PATH = ROOT / "prompts" / "suitability" / "SUITABILITY-API-001.json"
TEMPLATE_PATH = ROOT / "prompts" / "prompt_template_v2.1.0.md"
PROMPT_PATH = ROOT / "data" / "generated_prompts" / "suitability" / "v2.1.0" / "SUITABILITY-API-001.txt"
OUTPUT_ROOT = ROOT / "data" / "suitability" / "api" / "v2.1.0"
SUMMARY_PATH = OUTPUT_ROOT / "suitability_summary.json"
EXPECTED_TASK_SET_SHA256 = "ef0aff59f8a3934f65379d34036848652b7b5593f595ffa4b449a15af021546b"
EXPECTED_V2_MANIFEST_SHA256 = "ee0f335ad7f1eee020bd39011f2aeb3e4788ee0381f0a6d30d85cbc5f0d810ea"

SIMULATED_TOOL_MARKUP = re.compile(
    r"<\s*/?\s*(?:tool[_ -]?call|function(?:\s*=|\b)|parameter(?:\s*=|\b))|"
    r"\[\s*/?\s*tool[_ -]?call\s*\]|"
    r"<\|(?:tool_call|function_call|recipient)[^|]*\|>",
    flags=re.IGNORECASE,
)
INSPECTION_REQUEST = re.compile(
    r"(?:let me|i(?:'ll| will)|please)\s+(?:first\s+)?(?:inspect|explore|list|read|open|check)\b.*"
    r"(?:repositor|project|scaffold|director|files?|package\.json)",
    flags=re.IGNORECASE | re.DOTALL,
)


def load_and_validate_inputs() -> tuple[dict, dict, bytes]:
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    if protocol.get("status") != "criteria_frozen_before_requests":
        raise ValueError("Suitability criteria were not frozen before requests")
    if protocol.get("conditions") != ["M1", "M2", "M3", "M4"]:
        raise ValueError("Suitability protocol must contain exactly M1 through M4")
    if len(protocol.get("pass_criteria", [])) != 7:
        raise ValueError("Suitability protocol must freeze all seven pass criteria")
    request = protocol.get("request", {})
    expected_request = {
        "temperature": 0.6,
        "top_p": 0.95,
        "max_output_tokens": 6000,
        "seed": "omitted",
        "tools_exposed": False,
        "tool_choice": "none",
    }
    if any(request.get(key) != value for key, value in expected_request.items()):
        raise ValueError("Suitability request protocol differs from the frozen settings")

    task = json.loads(TASK_PATH.read_text(encoding="utf-8"))
    if task.get("task_id") != "SUITABILITY-API-001" or not task.get("excluded_from_official_dataset"):
        raise ValueError("Suitability task identity or exclusion marker is invalid")
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    if template.count("[TASK_DESCRIPTION]") != 1:
        raise ValueError("V2.1 template must contain one task placeholder")
    expected_prompt = template.replace("[TASK_DESCRIPTION]", task["prompt"]).encode("utf-8")
    prompt = PROMPT_PATH.read_bytes()
    if prompt != expected_prompt:
        raise ValueError("Rendered suitability prompt differs from the common v2.1 wrapper")
    if sha256_bytes((ROOT / "prompts" / "tasks" / "final_2.0.0.jsonl").read_bytes()) != EXPECTED_TASK_SET_SHA256:
        raise ValueError("The 30 frozen task records changed")
    if sha256_bytes((ROOT / "manifests" / "api_final_v2.0.0_manifest.csv").read_bytes()) != EXPECTED_V2_MANIFEST_SHA256:
        raise ValueError("The historical v2.0 manifest changed")
    return protocol, task, prompt


def parse_model_response(body: bytes) -> tuple[dict, dict, str | None, str | None]:
    try:
        response = json.loads(body)
        choice = response["choices"][0]
        message = choice["message"]
    except (UnicodeDecodeError, json.JSONDecodeError, KeyError, IndexError, TypeError) as error:
        raise ValueError("HTTP 200 response is not a valid chat completion") from error
    if not isinstance(response, dict) or not isinstance(choice, dict) or not isinstance(message, dict):
        raise ValueError("HTTP 200 response is not a valid chat completion")
    content = message.get("content")
    if content is not None and not isinstance(content, str):
        raise ValueError("Assistant content is neither text nor null")
    finish_reason = choice.get("finish_reason")
    return response, message, content, finish_reason


def interface_assessment(
    *,
    http_model_response_valid: bool,
    message: dict | None,
    content: str | None,
    finish_reason: str | None,
) -> dict:
    message = message or {}
    content = content or ""
    tool_calls = message.get("tool_calls")
    structured_tool_calls = isinstance(tool_calls, list) and len(tool_calls) > 0
    simulated_markup = bool(SIMULATED_TOOL_MARKUP.search(content))
    lower = content.casefold()
    inline_implementation = (
        "package.json" in lower
        and "```" in content
        and any(marker in lower for marker in ("src/", "tsconfig", "server.ts", "index.ts"))
    )
    inspection_only = bool(INSPECTION_REQUEST.search(content)) and not inline_implementation
    criteria = {
        "http_model_response_valid": http_model_response_valid,
        "no_structured_tool_calls": not structured_tool_calls,
        "finish_reason_not_tool_calls": finish_reason != "tool_calls",
        "no_simulated_tool_markup": not simulated_markup,
        "does_not_stop_for_repository_inspection": not inspection_only,
        "substantive_inline_implementation": inline_implementation,
        "no_actual_tools_exposed_or_executed": True,
    }
    return {
        "structured_tool_calls_returned": structured_tool_calls,
        "structured_tool_call_count": len(tool_calls) if isinstance(tool_calls, list) else 0,
        "simulated_tool_markup": simulated_markup,
        "repository_inspection_only": inspection_only,
        "inline_implementation": inline_implementation,
        "criteria": criteria,
        "suitability": "PASS" if all(criteria.values()) else "FAIL",
    }


def run_one(config: dict, model: dict, prompt: bytes) -> dict:
    condition_id = model["condition_id"]
    run_id = f"SUITABILITY-API-001-{condition_id}"
    directory = OUTPUT_ROOT / run_id
    directory.mkdir(parents=True, exist_ok=False)
    url, headers, request_body = build_request(config, model, prompt)
    request_payload = json.loads(request_body)
    if request_payload.get("tools") is not None or request_payload.get("tool_choice") != "none":
        raise ValueError("Suitability request violates the no-tools protocol")
    if request_payload.get("messages") != [{"role": "user", "content": prompt.decode("utf-8")}]:
        raise ValueError("Suitability request must contain exactly one user message")
    if "seed" in request_payload:
        raise ValueError("Suitability request must omit seed")

    write_exclusive(directory / "prompt.txt", prompt)
    write_exclusive(directory / "request.json", request_body)
    metadata = {
        "run_id": run_id,
        "phase": "interface_suitability_excluded",
        "protocol_version": "interface-suitability-2.1.0",
        "task_id": "SUITABILITY-API-001",
        "excluded_from_official_dataset": True,
        "excluded_from_hallucination_metrics": True,
        "model_condition_id": condition_id,
        "requested_model_id": model["model_id"],
        "returned_model_id": None,
        "api_provider": model["api_provider"],
        "expected_underlying_provider": (model.get("openrouter_routing") or {}).get("underlying_provider_name"),
        "resolved_underlying_provider": None,
        "collection_status": "requesting",
        "generation_started_at_utc": utc_now(),
        "prompt_sha256": sha256_bytes(prompt),
        "request_sha256": sha256_bytes(request_body),
        "http_client": HTTP_CLIENT,
        "stable_request_headers": STABLE_REQUEST_HEADERS,
        "authorization_scheme": "Bearer (credential omitted)",
        "request_message_count": 1,
        "tools_exposed": False,
        "tools_executed": False,
        "tool_choice": "none",
        "sampling_parameters": {
            "temperature": 0.6,
            "top_p": 0.95,
            "max_output_tokens": 6000,
            "seed": "omitted",
        },
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
            if attempt < maximum_attempts and retry_policy["retry_transport_errors"]:
                write_json(directory / "metadata.json", metadata)
                time.sleep(float(retry_policy["backoff_seconds"][attempt - 1]))
                continue
            metadata.update({
                "collection_status": "failed",
                "generation_ended_at_utc": utc_now(),
                "failure_reason": "transport_failure",
                "interface_assessment": interface_assessment(
                    http_model_response_valid=False, message=None, content=None, finish_reason=None
                ),
            })
            write_json(directory / "metadata.json", metadata)
            return metadata

        retryable = (
            result.status in retry_policy["retryable_http_statuses"]
            or (500 <= result.status <= 599 and retry_policy["retry_server_errors"])
        )
        if retryable and attempt < maximum_attempts:
            provider_delay = retry_after_seconds(result.headers) if result.status == 429 else None
            delay = max(float(retry_policy["backoff_seconds"][attempt - 1]), provider_delay or 0.0)
            history["retry_delay_seconds"] = delay
            if provider_delay is not None:
                history["retry_after_seconds"] = provider_delay
            write_json(directory / "metadata.json", metadata)
            time.sleep(delay)
            continue

        metadata["http_status"] = result.status
        metadata["safe_response_headers"] = safe_headers(result.headers)
        if result.status != 200:
            metadata.update({
                "collection_status": "failed",
                "generation_ended_at_utc": utc_now(),
                "failure_reason": f"http_status_{result.status}",
                "interface_assessment": interface_assessment(
                    http_model_response_valid=False, message=None, content=None, finish_reason=None
                ),
            })
            write_json(directory / "metadata.json", metadata)
            return metadata

        write_exclusive(directory / "provider_response.json", result.body)
        try:
            response, message, content, finish_reason = parse_model_response(result.body)
            valid = True
            failure_reason = None
        except ValueError as error:
            response, message, content, finish_reason = {}, {}, None, None
            valid = False
            failure_reason = str(error)
        response_bytes = (content or "").encode("utf-8")
        write_exclusive(directory / "response.md", response_bytes)
        assessment = interface_assessment(
            http_model_response_valid=valid,
            message=message,
            content=content,
            finish_reason=finish_reason,
        )
        resolved_provider = resolved_openrouter_provider(response) if model["api_provider"] == "OpenRouter" else "Groq"
        metadata.update({
            "collection_status": "completed" if valid else "failed",
            "generation_ended_at_utc": utc_now(),
            "returned_model_id": response.get("model"),
            "returned_exact_requested_model": response.get("model") == model["model_id"],
            "resolved_underlying_provider": resolved_provider,
            "finish_reason": finish_reason,
            "completion_token_count": (response.get("usage") or {}).get("completion_tokens"),
            "token_usage": response.get("usage"),
            "response_token_metadata": response_token_metadata(response),
            "provider_response_sha256": sha256_bytes(result.body),
            "response_sha256": sha256_bytes(response_bytes),
            "provider_response_size_bytes": len(result.body),
            "response_size_bytes": len(response_bytes),
            "provider_response_id": response.get("id"),
            "interface_assessment": assessment,
        })
        if failure_reason:
            metadata["failure_reason"] = failure_reason
        write_json(directory / "metadata.json", metadata)
        return metadata
    raise AssertionError("Unreachable suitability retry state")


def main() -> int:
    try:
        assert_live_collection_allowed()
        _, _, prompt = load_and_validate_inputs()
        config = load_config(DEFAULT_CONFIG)
        expected_models = [
            ("M1", "cohere/north-mini-code:free"),
            ("M2", "qwen/qwen3.8-27b"),
            ("M3", "openai/gpt-oss-120b"),
            ("M4", "nvidia/nemotron-3-ultra-550b-a55b:free"),
        ]
        if [(item["condition_id"], item["model_id"]) for item in config["models"]] != expected_models:
            raise ValueError("The four retained model conditions differ from the suitability protocol")
        directories = [OUTPUT_ROOT / f"SUITABILITY-API-001-{condition}" for condition, _ in expected_models]
        if SUMMARY_PATH.exists() or any(path.exists() for path in directories):
            raise ValueError("Refusing to overwrite or repeat a suitability condition")
        results = [run_one(config, model, prompt) for model in config["models"]]
        summary = {
            "protocol_version": "interface-suitability-2.1.0",
            "task_id": "SUITABILITY-API-001",
            "excluded_from_official_dataset": True,
            "excluded_from_hallucination_metrics": True,
            "generated_at_utc": utc_now(),
            "results": [
                {
                    "model_condition_id": item["model_condition_id"],
                    "requested_model_id": item["requested_model_id"],
                    "returned_model_id": item.get("returned_model_id"),
                    "returned_exact_requested_model": item.get("returned_exact_requested_model", False),
                    "http_status": item.get("http_status"),
                    "finish_reason": item.get("finish_reason"),
                    "completion_token_count": item.get("completion_token_count"),
                    "tools_exposed": item["tools_exposed"],
                    "tools_executed": item["tools_executed"],
                    **item["interface_assessment"],
                }
                for item in results
            ],
        }
        write_json(SUMMARY_PATH, summary, exclusive=True)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(json.dumps(summary, sort_keys=True))
    return 0 if all(item["suitability"] == "PASS" for item in summary["results"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
