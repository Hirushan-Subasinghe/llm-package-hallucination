#!/usr/bin/env python3
"""Inspect configured API model availability and OpenRouter endpoints without generation."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from collect_api_run import DEFAULT_CONFIG, load_config, utc_now, write_json


def get_json(url: str, api_key: str) -> dict:
    request = Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "User-Agent": "ai-hallucination-study-preflight/1.0",
        },
        method="GET",
    )
    try:
        with urlopen(request, timeout=60) as response:
            return json.loads(response.read())
    except HTTPError as error:
        raise ValueError(f"Preflight GET failed with HTTP {error.code}") from error
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Preflight GET failed: {type(error).__name__}") from error


def inspect(config: dict) -> dict:
    snapshot = {
        "preflight_timestamp_utc": utc_now(),
        "model_set_version": config["model_set_version"],
        "generation_requests_sent": 0,
        "models": [],
    }
    groq_models = None
    openrouter_models = None
    for model in config["models"]:
        key_name = model["api_key_environment_variable"]
        api_key = os.environ.get(key_name)
        if not api_key:
            raise ValueError(f"Required environment variable is not set: {key_name}")
        record = {
            "condition_id": model["condition_id"],
            "api_provider": model["api_provider"],
            "model_id": model["model_id"],
            "no_tools_request_mode": model["no_tools_request_mode"],
        }
        if model["api_provider"] == "OpenRouter":
            if openrouter_models is None:
                catalog_url = f"{model['api_base_url'].rstrip('/')}/models"
                openrouter_models = get_json(catalog_url, api_key)
            catalog_matches = [item for item in openrouter_models.get("data", []) if item.get("id") == model["model_id"]]
            author, slug = model["model_id"].split("/", 1)
            url = f"{model['api_base_url'].rstrip('/')}/models/{quote(author, safe='')}/{quote(slug, safe=':')}/endpoints"
            response = get_json(url, api_key)
            model_data = response.get("data", {})
            endpoints = response.get("data", {}).get("endpoints", [])
            record["catalog_inspection_url"] = catalog_url
            record["catalog_available"] = len(catalog_matches) == 1
            record["catalog_record"] = catalog_matches[0] if len(catalog_matches) == 1 else None
            record["inspection_url"] = url
            record["endpoint_model_record"] = {
                "id": model_data.get("id"),
                "name": model_data.get("name"),
                "architecture": model_data.get("architecture"),
            }
            record["available_endpoints"] = [
                {
                    "name": endpoint.get("name"),
                    "provider_name": endpoint.get("provider_name"),
                    "provider_slug": endpoint.get("tag"),
                    "status": endpoint.get("status"),
                    "context_length": endpoint.get("context_length"),
                    "max_completion_tokens": endpoint.get("max_completion_tokens"),
                    "supported_parameters": endpoint.get("supported_parameters", []),
                    "quantization": endpoint.get("quantization"),
                    "pricing": endpoint.get("pricing"),
                    "uptime_last_30m": endpoint.get("uptime_last_30m"),
                }
                for endpoint in endpoints
            ]
            record["required_parameter_names"] = ["temperature", "top_p", "max_tokens", "tool_choice"]
        else:
            if groq_models is None:
                url = f"{model['api_base_url'].rstrip('/')}/models"
                groq_models = get_json(url, api_key)
            matches = [item for item in groq_models.get("data", []) if item.get("id") == model["model_id"]]
            record["inspection_url"] = f"{model['api_base_url'].rstrip('/')}/models"
            record["catalog_available"] = len(matches) == 1 and matches[0].get("active") is True
            record["model_records"] = matches
            record["required_parameter_names"] = ["temperature", "top_p", "max_completion_tokens", "tool_choice"]
        snapshot["models"].append(record)
    return snapshot


def main() -> int:
    parser = argparse.ArgumentParser(description="Perform read-only model/provider preflight; sends no generation request")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        config = load_config(args.config)
        snapshot = inspect(config)
        write_json(args.output, snapshot, exclusive=True)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"PASS: wrote read-only preflight snapshot to {args.output}")
    print("Generation requests sent: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
