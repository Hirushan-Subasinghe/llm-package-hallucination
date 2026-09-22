#!/usr/bin/env python3
"""Finalize a captured run after checking collection integrity."""

from __future__ import annotations

import argparse
import sys

from collection_common import (
    REQUIRED_METADATA,
    find_run,
    load_metadata,
    raw_artifact_relative_path,
    run_directory,
    sha256_bytes,
    utc_now,
    write_metadata,
)


CODEX_FIXED_METADATA = {
    "tool_name": "codex_cli",
    "provider": "OpenAI",
    "model_name": "gpt-5.6-sol",
    "model_version": "not_exposed",
    "workflow_type": "agentic_cli",
    "model_reasoning_effort": "medium",
    "service_tier": "default",
    "temperature": "not_exposed",
    "seed": "not_exposed",
    "web_search": "disabled",
    "sandbox_mode": "read-only",
}


def finalize_run(run_id: str) -> dict:
    row, _ = find_run(run_id)
    directory = run_directory(row)
    metadata_path = directory / "metadata.json"
    metadata = load_metadata(metadata_path)
    errors = []
    errors.extend(f"missing metadata field: {field}" for field in REQUIRED_METADATA if field not in metadata)
    if metadata.get("run_id") != row["run_id"] or metadata.get("prompt_id") != row["prompt_id"]:
        errors.append("metadata does not match manifest identity")
    prompt_path = directory / "prompt.txt"
    prompt_bytes = prompt_path.read_bytes() if prompt_path.is_file() else b""
    if not prompt_path.is_file() or sha256_bytes(prompt_bytes) != row["expected_prompt_sha256"]:
        errors.append("prompt copy is missing or does not match manifest hash")
    if metadata.get("prompt_sha256") != row["expected_prompt_sha256"]:
        errors.append("metadata prompt_sha256 does not match manifest hash")
    if metadata.get("prompt_text") != prompt_bytes.decode("utf-8", errors="replace"):
        errors.append("metadata prompt_text does not match prompt copy")

    workflow = metadata.get("workflow", "")
    if workflow.endswith("_web"):
        response_path = directory / "response.md"
        required_paths = [response_path]
    elif workflow == "codex_cli":
        response_path = directory / "response.md"
        required_paths = [response_path, directory / "transcript.txt"]
        if metadata.get("collection_method") == "automated_codex_exec":
            required_paths.append(directory / "stderr.txt")
            if metadata.get("cli_exit_status") != 0:
                errors.append("automated Codex capture did not exit successfully")
            for field, expected in CODEX_FIXED_METADATA.items():
                if metadata.get(field) != expected:
                    errors.append(f"Codex metadata {field} is not the frozen value")
            for field in ("generation_started_at_utc", "generation_ended_at_utc", "codex_cli_version"):
                if not metadata.get(field):
                    errors.append(f"missing automated Codex metadata: {field}")
    else:
        response_path = directory / "transcript.txt"
        required_paths = [response_path]

    for required_path in required_paths:
        if not required_path.is_file():
            errors.append(f"missing required capture: {required_path.name}")
    if workflow == "codex_cli" and response_path.is_file() and not response_path.read_bytes():
        errors.append("Codex final response is empty")

    hash_fields = {
        "raw_response_sha256": response_path,
        "transcript_sha256": directory / "transcript.txt",
        "stderr_sha256": directory / "stderr.txt",
    }
    if metadata.get("collection_method") == "automated_codex_exec":
        for field, path in hash_fields.items():
            if path.is_file() and metadata.get(field) != sha256_bytes(path.read_bytes()):
                errors.append(f"metadata {field} does not match preserved capture")

    if errors:
        metadata["collection_status"] = "error"
        metadata["finalization_errors"] = errors
        write_metadata(metadata_path, metadata)
        raise ValueError("; ".join(errors))

    metadata["raw_response_path"] = raw_artifact_relative_path(row, response_path.name)
    metadata["raw_response_sha256"] = sha256_bytes(response_path.read_bytes())
    metadata["timestamp"] = metadata.get("generation_ended_at_utc") or utc_now()
    metadata["collection_status"] = "completed"
    metadata.pop("finalization_errors", None)
    if not workflow.endswith("_web"):
        metadata["transcript_path"] = "transcript.txt"
    write_metadata(metadata_path, metadata)
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_id")
    args = parser.parse_args()
    try:
        metadata = finalize_run(args.run_id)
        print(f"PASS: finalized {args.run_id}")
        print(f"Raw capture SHA-256: {metadata['raw_response_sha256']}")
        return 0
    except (OSError, ValueError, KeyError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
