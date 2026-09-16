#!/usr/bin/env python3
"""Collect one future API manifest row without executing generated code.

This script is intentionally dormant until a reviewed v2 manifest exists and the
candidate model configuration has passed preflight and been frozen.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Callable

import requests


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config" / "api_model_set_1.0.0.json"
DEFAULT_RAW_ROOT = ROOT / "data" / "final" / "raw"
REQUIRED_MANIFEST_FIELDS = {
    "run_id",
    "collection_order",
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
}
SAFE_RESPONSE_HEADERS = {
    "content-type",
    "date",
    "request-id",
    "x-request-id",
    "x-groq-region",
    "x-ratelimit-limit-requests",
    "x-ratelimit-limit-tokens",
    "x-ratelimit-remaining-requests",
    "x-ratelimit-remaining-tokens",
    "x-ratelimit-reset-requests",
    "x-ratelimit-reset-tokens",
    "retry-after",
}
HTTP_CLIENT = {
    "library": "requests",
    "version": requests.__version__,
    "http_protocol": "HTTP/1.1",
    "redirects": "disabled",
    "proxy_environment": "honored_if_set",
}
STABLE_REQUEST_HEADERS = {
    "User-Agent": "ai-hallucination-study/1.0",
    "Accept": "application/json",
    "Content-Type": "application/json",
}


class TransportFailure(Exception):
    """A network/transport failure for which infrastructure retry is allowed."""


@dataclass(frozen=True)
class HTTPResult:
    status: int
    headers: dict[str, str]
    body: bytes


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def write_exclusive(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(value)


def write_json(path: Path, value: object, *, exclusive: bool = False) -> None:
    content = (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    if exclusive:
        write_exclusive(path, content)
        return
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(content)
    os.replace(temporary, path)


def load_config(path: Path) -> dict:
    config = json.loads(path.read_text(encoding="utf-8"))
    if config.get("model_set_version") != "api-model-set-1.0.0":
        raise ValueError("Unexpected model_set_version")
    models = config.get("models")
    if not isinstance(models, list) or len(models) != 4:
        raise ValueError("Model configuration must contain exactly four conditions")
    condition_ids = [model.get("condition_id") for model in models]
    if condition_ids != ["M1", "M2", "M3", "M4"]:
        raise ValueError("Model conditions must be ordered M1 through M4")
    if len({model.get("model_id") for model in models}) != 4:
        raise ValueError("Configured model IDs must be unique")
    return config


def load_manifest(path: Path) -> list[dict[str, object]]:
    if path.suffix == ".jsonl":
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    elif path.suffix == ".csv":
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
    else:
        raise ValueError("Future API manifest must be CSV or JSONL")
    for row in rows:
        missing = REQUIRED_MANIFEST_FIELDS - row.keys()
        if missing:
            raise ValueError(f"Manifest row is missing fields: {', '.join(sorted(missing))}")
    return rows


def select_manifest_row(rows: list[dict[str, object]], run_id: str) -> dict[str, object]:
    matches = [row for row in rows if row["run_id"] == run_id]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one manifest row for {run_id}; found {len(matches)}")
    row = matches[0]
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", str(row["run_id"])):
        raise ValueError("Manifest run_id contains unsafe path characters")
    return row


def model_for_row(config: dict, row: dict[str, object]) -> dict:
    models = [model for model in config["models"] if model["condition_id"] == row["model_condition_id"]]
    if len(models) != 1:
        raise ValueError("Manifest model condition is not configured")
    model = models[0]
    if row["model_id"] != model["model_id"] or row["api_provider"] != model["api_provider"]:
        raise ValueError("Manifest model identity does not match frozen configuration")
    return model


def parse_repetition(value: object) -> int:
    text = str(value)
    return int(text[1:]) if re.fullmatch(r"R0[1-3]", text) else int(text)


def validate_collection_ready(config: dict, row: dict[str, object], model: dict) -> None:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", str(row["run_id"])):
        raise ValueError("Manifest run_id contains unsafe path characters")
    if config.get("status") != "frozen_for_collection":
        raise ValueError("Candidate model set is not frozen_for_collection")
    if config["candidate_common_parameters"].get("compatibility_status") != "confirmed":
        raise ValueError("Common sampling parameters have not passed preflight")
    if row["phase"] != "final":
        raise ValueError("This collector scaffold accepts only the future official final phase")
    if row["task_set_version"] != "final-2.0.0":
        raise ValueError("Manifest must use task_set_version final-2.0.0")
    if row["model_set_version"] != "api-model-set-1.0.0":
        raise ValueError("Manifest must use model_set_version api-model-set-1.0.0")
    repetition = parse_repetition(row["run_repetition"])
    if repetition not in (1, 2, 3):
        raise ValueError("Run repetition must be 1, 2, or 3")
    if row["collection_status"] != "pending":
        raise ValueError("Only pending manifest rows may be collected")
    no_tools_mode = model.get("no_tools_request_mode")
    if no_tools_mode not in {"explicit_tool_choice_none", "omit_tools_only"}:
        raise ValueError("No-tools request behavior has not passed preflight")
    if model["api_provider"] == "Groq" and no_tools_mode != "explicit_tool_choice_none":
        raise ValueError("Groq must explicitly enforce tool_choice none")
    if model["api_provider"] == "OpenRouter":
        routing = model["openrouter_routing"]
        if row.get("underlying_provider_pin") != routing.get("underlying_provider_slug"):
            raise ValueError("Manifest underlying provider pin does not match frozen configuration")
        status = routing.get("pinning_status")
        if status == "pinned" and not routing.get("underlying_provider_slug"):
            raise ValueError("Pinned OpenRouter condition is missing its provider slug")
        if status == "unavailable" and not routing.get("allow_unpinned_after_documented_decision"):
            raise ValueError("Unpinned OpenRouter collection lacks a documented approval flag")
        if status not in {"pinned", "unavailable"}:
            raise ValueError("OpenRouter provider preflight is incomplete")
    elif row.get("underlying_provider_pin") != "not_applicable":
        raise ValueError("Groq manifest rows must use underlying_provider_pin not_applicable")


def prompt_bytes_for_row(row: dict[str, object]) -> bytes:
    path = (ROOT / str(row["rendered_prompt_path"])).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        raise ValueError("Rendered prompt path is missing or outside the repository")
    content = path.read_bytes()
    if sha256_bytes(content) != row["expected_prompt_sha256"]:
        raise ValueError("Rendered prompt hash does not match manifest")
    try:
        content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("Rendered prompt is not valid UTF-8") from error
    return content


def build_request(config: dict, model: dict, prompt_bytes: bytes) -> tuple[str, dict[str, str], bytes]:
    parameters = config["candidate_common_parameters"]
    payload = {
        "model": model["model_id"],
        "messages": [{"role": "user", "content": prompt_bytes.decode("utf-8")}],
        "temperature": parameters["temperature"],
        "top_p": parameters["top_p"],
        model["output_token_parameter"]: parameters["max_output_tokens"],
        "stream": False,
    }
    no_tools_mode = model.get("no_tools_request_mode")
    if no_tools_mode == "explicit_tool_choice_none":
        payload["tool_choice"] = "none"
    elif no_tools_mode != "omit_tools_only":
        raise ValueError("No-tools request behavior has not passed preflight")
    # Never add a `tools` member: no function, browser, retrieval, execution, or
    # provider-hosted tool is exposed to an experimental generation.
    if model["api_provider"] == "OpenRouter":
        routing = model["openrouter_routing"]
        provider = {
            "allow_fallbacks": False,
            "require_parameters": True,
        }
        if routing["pinning_status"] == "pinned":
            provider["order"] = [routing["underlying_provider_slug"]]
        payload["provider"] = provider
    api_key_name = model["api_key_environment_variable"]
    api_key = os.environ.get(api_key_name)
    if not api_key:
        raise ValueError(f"Required environment variable is not set: {api_key_name}")
    headers = {
        "Authorization": f"Bearer {api_key}",
        **STABLE_REQUEST_HEADERS,
    }
    if model["api_provider"] == "OpenRouter":
        headers["X-OpenRouter-Metadata"] = "enabled"
    body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return f"{model['api_base_url'].rstrip('/')}/chat/completions", headers, body


def request_once(url: str, headers: dict[str, str], body: bytes, timeout_seconds: float) -> HTTPResult:
    try:
        response = requests.post(
            url,
            data=body,
            headers=headers,
            timeout=timeout_seconds,
            allow_redirects=False,
        )
        return HTTPResult(response.status_code, dict(response.headers.items()), response.content)
    except requests.RequestException as error:
        raise TransportFailure(str(error)) from error


def safe_headers(headers: dict[str, str]) -> dict[str, str]:
    return {key.lower(): value for key, value in headers.items() if key.lower() in SAFE_RESPONSE_HEADERS}


def retry_after_seconds(headers: dict[str, str], *, now: float | None = None) -> float | None:
    value = next((item for key, item in headers.items() if key.lower() == "retry-after"), None)
    if value is None:
        return None
    try:
        seconds = float(value)
        return max(0.0, seconds)
    except ValueError:
        try:
            retry_at = parsedate_to_datetime(value)
            if retry_at.tzinfo is None:
                retry_at = retry_at.replace(tzinfo=timezone.utc)
            current = time.time() if now is None else now
            return max(0.0, retry_at.timestamp() - current)
        except (TypeError, ValueError, OverflowError):
            return None


def parse_valid_response(body: bytes) -> tuple[dict, str]:
    try:
        response = json.loads(body)
        choice = response["choices"][0]
        content = choice["message"]["content"]
        finish_reason = choice.get("finish_reason")
    except (UnicodeDecodeError, json.JSONDecodeError, KeyError, IndexError, TypeError) as error:
        raise ValueError("HTTP 200 response is not a valid chat completion") from error
    if not isinstance(content, str) or (not content and finish_reason != "length"):
        raise ValueError("HTTP 200 response contains no non-empty assistant content")
    return response, content


def response_token_metadata(response: dict) -> dict[str, int | None]:
    """Extract exposed completion/reasoning token counts without guessing missing values."""
    usage = response.get("usage") if isinstance(response.get("usage"), dict) else {}
    details = usage.get("completion_tokens_details")
    details = details if isinstance(details, dict) else {}
    reasoning_tokens = details.get("reasoning_tokens", usage.get("reasoning_tokens"))
    visible_tokens = details.get("visible_tokens", usage.get("visible_tokens"))
    return {
        "total_completion_tokens": usage.get("completion_tokens"),
        "reasoning_tokens": reasoning_tokens,
        "visible_response_tokens": visible_tokens,
    }


def completion_status(response: dict) -> tuple[str, str]:
    finish_reason = response.get("choices", [{}])[0].get("finish_reason")
    if finish_reason == "length":
        return "truncated", "TRUNCATED"
    return "completed", "COMPLETED"


def resolved_openrouter_provider(response: dict) -> str | None:
    metadata = response.get("openrouter_metadata") or {}
    endpoints = metadata.get("endpoints") or {}
    for endpoint in endpoints.get("available") or []:
        if endpoint.get("selected") is True:
            return endpoint.get("provider")
    value = response.get("provider")
    return value if isinstance(value, str) else None


def collect_row(
    config: dict,
    row: dict[str, object],
    *,
    raw_root: Path = DEFAULT_RAW_ROOT,
    timeout_seconds: float = 180.0,
    transport: Callable[[str, dict[str, str], bytes, float], HTTPResult] = request_once,
    sleeper: Callable[[float], None] = time.sleep,
) -> Path:
    model = model_for_row(config, row)
    validate_collection_ready(config, row, model)
    prompt = prompt_bytes_for_row(row)
    run_directory = raw_root / str(row["run_id"])
    if run_directory.exists():
        raise ValueError("Refusing to overwrite an existing API run directory")
    url, headers, request_body = build_request(config, model, prompt)
    try:
        run_directory.mkdir(parents=True, exist_ok=False)
    except FileExistsError as error:
        raise ValueError("Refusing to overwrite an existing API run directory") from error

    write_exclusive(run_directory / "prompt.txt", prompt)
    write_exclusive(run_directory / "request.json", request_body)
    retry_policy = config["retry_policy"]
    metadata = {
        "run_id": row["run_id"],
        "phase": row["phase"],
        "task_id": row["task_id"],
        "category": row["category"],
        "task_set_version": row["task_set_version"],
        "model_set_version": row["model_set_version"],
        "model_condition_id": row["model_condition_id"],
        "requested_model_id": model["model_id"],
        "returned_model_id": None,
        "api_provider": model["api_provider"],
        "resolved_underlying_provider": None,
        "run_repetition": parse_repetition(row["run_repetition"]),
        "collection_order": int(row["collection_order"]),
        "collection_status": "requesting",
        "generation_started_at_utc": utc_now(),
        "prompt_path": "prompt.txt",
        "prompt_sha256": sha256_bytes(prompt),
        "request_path": "request.json",
        "request_sha256": sha256_bytes(request_body),
        "request_endpoint": url,
        "request_method": "POST",
        "http_client": HTTP_CLIENT,
        "stable_request_headers": STABLE_REQUEST_HEADERS,
        "authorization_scheme": "Bearer (credential omitted)",
        "request_message_count": 1,
        "tools_exposed": False,
        "no_tools_request_mode": model["no_tools_request_mode"],
        "sampling_parameters": {
            "temperature": config["candidate_common_parameters"]["temperature"],
            "top_p": config["candidate_common_parameters"]["top_p"],
            "max_output_tokens": config["candidate_common_parameters"]["max_output_tokens"],
            "seed": "not_controlled",
        },
        "retry_history": [],
    }
    write_json(run_directory / "metadata.json", metadata, exclusive=True)

    maximum_attempts = 1 + int(retry_policy["maximum_infrastructure_retries"])
    backoff = retry_policy["backoff_seconds"]
    for attempt_number in range(1, maximum_attempts + 1):
        attempt_started = utc_now()
        try:
            result = transport(url, headers, request_body, timeout_seconds)
            attempt_dir = run_directory / "attempts" / f"attempt-{attempt_number:02d}"
            write_exclusive(attempt_dir / "http_response.bin", result.body)
            write_json(attempt_dir / "response_headers.json", safe_headers(result.headers), exclusive=True)
            history = {
                "attempt_number": attempt_number,
                "started_at_utc": attempt_started,
                "ended_at_utc": utc_now(),
                "outcome": "http_response",
                "http_status": result.status,
                "response_sha256": sha256_bytes(result.body),
            }
            metadata["retry_history"].append(history)
        except TransportFailure as error:
            history = {
                "attempt_number": attempt_number,
                "started_at_utc": attempt_started,
                "ended_at_utc": utc_now(),
                "outcome": "transport_failure",
                "error_type": type(error).__name__,
            }
            metadata["retry_history"].append(history)
            if attempt_number < maximum_attempts and retry_policy["retry_transport_errors"]:
                write_json(run_directory / "metadata.json", metadata)
                sleeper(backoff[attempt_number - 1])
                continue
            metadata.update({"collection_status": "failed", "generation_ended_at_utc": utc_now(), "failure_reason": "transport_failure"})
            write_json(run_directory / "metadata.json", metadata)
            raise ValueError("API collection ended after a transport failure") from error

        retryable_status = result.status == 429 or (500 <= result.status <= 599 and retry_policy["retry_server_errors"])
        if retryable_status and attempt_number < maximum_attempts:
            configured_delay = float(backoff[attempt_number - 1])
            provider_delay = retry_after_seconds(result.headers) if result.status == 429 else None
            delay = max(configured_delay, provider_delay or 0.0)
            history["retry_delay_seconds"] = delay
            if provider_delay is not None:
                history["retry_after_seconds"] = provider_delay
            write_json(run_directory / "metadata.json", metadata)
            sleeper(delay)
            continue
        if result.status != 200:
            metadata.update({
                "collection_status": "failed",
                "generation_ended_at_utc": utc_now(),
                "failure_reason": f"http_status_{result.status}",
                "safe_response_headers": safe_headers(result.headers),
            })
            write_json(run_directory / "metadata.json", metadata)
            raise ValueError(f"API collection failed with HTTP {result.status}")

        try:
            response, assistant_content = parse_valid_response(result.body)
        except ValueError as error:
            metadata.update({"collection_status": "failed", "generation_ended_at_utc": utc_now(), "failure_reason": str(error)})
            write_json(run_directory / "metadata.json", metadata)
            raise

        response_bytes = assistant_content.encode("utf-8")
        write_exclusive(run_directory / "provider_response.json", result.body)
        write_exclusive(run_directory / "response.md", response_bytes)
        resolved_provider = resolved_openrouter_provider(response) if model["api_provider"] == "OpenRouter" else "Groq"
        collection_status, response_completion_status = completion_status(response)
        metadata.update({
            "collection_status": collection_status,
            "response_completion_status": response_completion_status,
            "generation_ended_at_utc": utc_now(),
            "returned_model_id": response.get("model"),
            "resolved_underlying_provider": resolved_provider,
            "response_path": "response.md",
            "response_sha256": sha256_bytes(response_bytes),
            "response_size_bytes": len(response_bytes),
            "provider_response_path": "provider_response.json",
            "provider_response_sha256": sha256_bytes(result.body),
            "provider_response_size_bytes": len(result.body),
            "safe_response_headers": safe_headers(result.headers),
            "token_usage": response.get("usage"),
            "response_token_metadata": response_token_metadata(response),
            "finish_reason": response.get("choices", [{}])[0].get("finish_reason"),
            "provider_response_id": response.get("id"),
            "system_fingerprint": response.get("system_fingerprint"),
            "protocol_deviations": [],
        })
        if response.get("model") != model["model_id"]:
            metadata["protocol_deviations"].append("returned_model_id_differs_from_requested_model_id")
        routing = model.get("openrouter_routing")
        if routing and routing.get("pinning_status") == "pinned":
            expected = routing.get("underlying_provider_name")
            if expected and resolved_provider != expected:
                metadata["protocol_deviations"].append("resolved_provider_differs_from_frozen_provider")
        write_json(run_directory / "metadata.json", metadata)
        return run_directory

    raise AssertionError("Unreachable retry state")


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect exactly one future v2 API manifest row")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--raw-root", type=Path, default=DEFAULT_RAW_ROOT)
    parser.add_argument("--timeout-seconds", type=float, default=180.0)
    args = parser.parse_args()
    try:
        config = load_config(args.config)
        row = select_manifest_row(load_manifest(args.manifest), args.run_id)
        directory = collect_row(config, row, raw_root=args.raw_root, timeout_seconds=args.timeout_seconds)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"PASS: preserved API observation at {directory}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
