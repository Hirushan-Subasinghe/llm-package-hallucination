#!/usr/bin/env python3
"""Verify excluded API smoke artifacts without evaluating response content."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from collect_api_run import DEFAULT_CONFIG, load_config, sha256_bytes
from run_api_smoke_tests import PROMPT_PATH, SMOKE_ROOT


def main() -> int:
    try:
        config = load_config(DEFAULT_CONFIG)
        prompt = PROMPT_PATH.read_bytes()
        expected_series = {
            "SMOKE-API-001": {"M1", "M2", "M3", "M4"},
            "SMOKE-API-002": {"M2", "M3"},
            "SMOKE-API-003": {"M2", "M3"},
        }
        directories = sorted(path for path in SMOKE_ROOT.glob("SMOKE-API-???-M?") if path.is_dir())
        actual_series = {
            prefix: {path.name.rsplit("-", 1)[-1] for path in directories if path.name.startswith(f"{prefix}-")}
            for prefix in expected_series
        }
        if actual_series != expected_series:
            raise ValueError(f"Unexpected excluded smoke directory set: {actual_series}")
        results = []
        models = {model["condition_id"]: model for model in config["models"]}
        for directory in directories:
            condition_id = directory.name.rsplit("-", 1)[-1]
            model = models[condition_id]
            metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
            request_bytes = (directory / "request.json").read_bytes()
            request = json.loads(request_bytes)
            if (directory / "prompt.txt").read_bytes() != prompt:
                raise ValueError(f"Smoke prompt mismatch: {directory}")
            if metadata["prompt_sha256"] != sha256_bytes(prompt) or metadata["request_sha256"] != sha256_bytes(request_bytes):
                raise ValueError(f"Smoke prompt/request hash mismatch: {directory}")
            if request.get("tools") is not None or request.get("tool_choice") != "none":
                raise ValueError(f"Smoke no-tools policy mismatch: {directory}")
            if request.get("messages") != [{"role": "user", "content": prompt.decode("utf-8")}]:
                raise ValueError(f"Smoke message mismatch: {directory}")
            if request.get("temperature") != 0.6 or request.get("top_p") != 0.95:
                raise ValueError(f"Smoke sampling mismatch: {directory}")
            status = metadata["collection_status"]
            if status in {"completed", "truncated"}:
                provider_bytes = (directory / "provider_response.json").read_bytes()
                response_bytes = (directory / "response.md").read_bytes()
                if metadata["provider_response_sha256"] != sha256_bytes(provider_bytes) or metadata["response_sha256"] != sha256_bytes(response_bytes):
                    raise ValueError(f"Smoke response hash mismatch: {directory}")
                if metadata.get("returned_model_id") != model["model_id"] or metadata.get("tool_calls_returned") != 0:
                    raise ValueError(f"Smoke model/tool metadata mismatch: {directory}")
                if status == "truncated" and metadata.get("finish_reason") != "length":
                    raise ValueError(f"Truncated smoke lacks length finish reason: {directory}")
                routing = model.get("openrouter_routing")
                if routing and str(metadata.get("resolved_underlying_provider", "")).casefold() != str(routing["underlying_provider_name"]).casefold():
                    raise ValueError(f"Smoke underlying provider mismatch: {directory}")
            results.append({
                "model_condition_id": model["condition_id"],
                "smoke_attempt_series": directory.name.rsplit("-", 1)[0],
                "requested_model_id": model["model_id"],
                "collection_status": status,
                "returned_model_id": metadata.get("returned_model_id"),
                "resolved_underlying_provider": metadata.get("resolved_underlying_provider"),
                "tool_calls_returned": metadata.get("tool_calls_returned"),
                "failure_reason": metadata.get("failure_reason"),
                "attempt_count": len(metadata.get("retry_history", [])),
            })
        secrets = [os.environ.get(name, "").encode() for name in ("OPENROUTER_API_KEY", "GROQ_API_KEY")]
        for path in SMOKE_ROOT.rglob("*"):
            if path.is_file():
                content = path.read_bytes()
                if any(secret and secret in content for secret in secrets):
                    raise ValueError(f"API key serialized in smoke artifact: {path}")
        summary = {
            "smoke_task_id": "SMOKE-API-001",
            "excluded_from_research_metrics": True,
            "content_quality_not_evaluated": True,
            "results": results,
        }
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
