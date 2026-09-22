#!/usr/bin/env python3
"""Initialize one operator collection directory without contacting an AI workflow."""

from __future__ import annotations

import argparse
import sys

from collection_common import (
    find_run,
    load_metadata,
    run_directory,
    sha256_bytes,
    utc_now,
    verified_prompt_bytes,
    write_metadata,
)
from repository_guard import assert_live_collection_allowed


def is_pristine_initialized(directory, row, metadata: dict) -> bool:
    allowed = {"prompt.txt", "metadata.json", "artifacts"}
    if metadata.get("collection_status") != "initialized":
        return False
    if metadata.get("run_id") != row["run_id"] or metadata.get("prompt_id") != row["prompt_id"]:
        return False
    if any(path.name not in allowed for path in directory.iterdir()):
        return False
    artifacts = directory / "artifacts"
    if not artifacts.is_dir() or any(artifacts.iterdir()):
        return False
    prompt_copy = directory / "prompt.txt"
    if not prompt_copy.is_file() or sha256_bytes(prompt_copy.read_bytes()) != row["expected_prompt_sha256"]:
        return False
    return (
        not metadata.get("raw_response_path")
        and not metadata.get("raw_response_sha256")
        and metadata.get("cli_exit_status") is None
        and not metadata.get("generation_started_at_utc")
    )


def initialize_run(run_id: str, *, allow_pristine_existing: bool = False):
    row, manifest_path = find_run(run_id)
    directory = run_directory(row)
    metadata_path = directory / "metadata.json"
    if directory.exists() and any(directory.iterdir()):
        existing = load_metadata(metadata_path) if metadata_path.exists() else {}
        if existing.get("collection_status") == "completed":
            raise ValueError("Refusing to overwrite a completed run")
        if allow_pristine_existing and is_pristine_initialized(directory, row, existing):
            return row, manifest_path, directory, existing
        raise ValueError("Run directory is already populated; inspect it before reinitializing")
    prompt_bytes = verified_prompt_bytes(row)
    directory.mkdir(parents=True, exist_ok=False)
    (directory / "prompt.txt").write_bytes(prompt_bytes)
    (directory / "artifacts").mkdir()
    metadata = {
        "run_id": row["run_id"], "phase": row["phase"], "prompt_id": row["prompt_id"],
        "prompt_set_version": row["prompt_set_version"], "category": row["category"],
        "workflow": row["workflow"], "tool_name": row["workflow"], "provider": "not_exposed",
        "model_name": "not_exposed", "model_version": "not_exposed",
        "workflow_type": "web_single_turn" if row["workflow"].endswith("_web") else "agentic_cli",
        "temperature": "not_exposed", "seed": "not_exposed", "max_output_tokens": None,
        "timestamp": utc_now(), "prompt_text": prompt_bytes.decode("utf-8"),
        "prompt_sha256": sha256_bytes(prompt_bytes), "raw_response_path": "",
        "raw_response_sha256": "", "collection_method": "manual_operator_capture",
        "operator_id": "collector_01", "notes": "Initialized; capture response before finalization.",
        "collection_status": "initialized", "transcript_path": "", "artifact_directory": "artifacts",
        "cli_exit_status": None,
    }
    write_metadata(metadata_path, metadata)
    return row, manifest_path, directory, metadata


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_id")
    args = parser.parse_args()
    try:
        assert_live_collection_allowed()
        row, manifest_path, directory, _ = initialize_run(args.run_id)
        print(f"Initialized {row['run_id']} at {directory}")
        print(f"Prompt copy: {directory / 'prompt.txt'}")
        print(f"Manifest: {manifest_path.name}")
        return 0
    except (OSError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
