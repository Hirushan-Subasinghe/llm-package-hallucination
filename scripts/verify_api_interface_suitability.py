#!/usr/bin/env python3
"""Verify the excluded v2.1 suitability artifacts and their separation."""

from __future__ import annotations

import json
import os
import sys

from collect_api_run import DEFAULT_CONFIG, load_config, sha256_bytes
from run_api_interface_suitability import (
    OUTPUT_ROOT,
    PROMPT_PATH,
    ROOT,
    SUMMARY_PATH,
    load_and_validate_inputs,
)


def main() -> int:
    try:
        _, _, prompt = load_and_validate_inputs()
        config = load_config(DEFAULT_CONFIG)
        summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
        if not summary.get("excluded_from_official_dataset") or not summary.get("excluded_from_hallucination_metrics"):
            raise ValueError("Suitability summary lacks exclusion markers")
        if [item["model_condition_id"] for item in summary["results"]] != ["M1", "M2", "M3", "M4"]:
            raise ValueError("Suitability summary does not contain exactly M1 through M4")
        models = {model["condition_id"]: model for model in config["models"]}
        for item in summary["results"]:
            condition = item["model_condition_id"]
            directory = OUTPUT_ROOT / f"SUITABILITY-API-001-{condition}"
            metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
            request_bytes = (directory / "request.json").read_bytes()
            request = json.loads(request_bytes)
            if (directory / "prompt.txt").read_bytes() != prompt or PROMPT_PATH.read_bytes() != prompt:
                raise ValueError(f"Suitability prompt mismatch: {condition}")
            if metadata["prompt_sha256"] != sha256_bytes(prompt) or metadata["request_sha256"] != sha256_bytes(request_bytes):
                raise ValueError(f"Suitability input hash mismatch: {condition}")
            if request.get("tools") is not None or request.get("tool_choice") != "none" or "seed" in request:
                raise ValueError(f"Suitability request policy mismatch: {condition}")
            if request.get("messages") != [{"role": "user", "content": prompt.decode("utf-8")}]:
                raise ValueError(f"Suitability message mismatch: {condition}")
            if request.get("temperature") != 0.6 or request.get("top_p") != 0.95:
                raise ValueError(f"Suitability sampling mismatch: {condition}")
            output_parameter = models[condition]["output_token_parameter"]
            if request.get(output_parameter) != 6000:
                raise ValueError(f"Suitability output limit mismatch: {condition}")
            if metadata.get("tools_exposed") is not False or metadata.get("tools_executed") is not False:
                raise ValueError(f"Suitability tool boundary mismatch: {condition}")
            if metadata.get("http_status") == 200:
                provider = (directory / "provider_response.json").read_bytes()
                response = (directory / "response.md").read_bytes()
                if metadata.get("provider_response_sha256") != sha256_bytes(provider):
                    raise ValueError(f"Provider response hash mismatch: {condition}")
                if metadata.get("response_sha256") != sha256_bytes(response):
                    raise ValueError(f"Assistant response hash mismatch: {condition}")
            if item["requested_model_id"] != models[condition]["model_id"]:
                raise ValueError(f"Requested model mismatch: {condition}")
        official_manifest = ROOT / "manifests" / "api_final_v2.0.0_manifest.csv"
        if "SUITABILITY-API-001" in official_manifest.read_text(encoding="utf-8"):
            raise ValueError("Suitability task leaked into the official v2.0 manifest")
        secrets = [os.environ.get(name, "").encode() for name in ("OPENROUTER_API_KEY", "GROQ_API_KEY")]
        for path in OUTPUT_ROOT.rglob("*"):
            if path.is_file() and any(secret and secret in path.read_bytes() for secret in secrets):
                raise ValueError(f"API key serialized in suitability artifact: {path}")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
