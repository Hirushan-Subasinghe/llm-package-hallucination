#!/usr/bin/env python3
"""Initialize one operator collection directory without contacting an AI workflow."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone

from collection_common import ROOT, find_run, run_directory, sha256_bytes, write_metadata


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_id")
    args = parser.parse_args()
    try:
        row, manifest_path = find_run(args.run_id)
        directory = run_directory(row)
        metadata_path = directory / "metadata.json"
        if directory.exists() and any(directory.iterdir()):
            existing = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
            if existing.get("collection_status") == "completed":
                raise ValueError("Refusing to overwrite a completed run")
            raise ValueError("Run directory is already populated; inspect it before reinitializing")
        prompt_path = ROOT / row["rendered_prompt_path"]
        prompt_bytes = prompt_path.read_bytes()
        actual_hash = sha256_bytes(prompt_bytes)
        if actual_hash != row["expected_prompt_sha256"]:
            raise ValueError("Rendered prompt hash does not match manifest")
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
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "prompt_text": prompt_bytes.decode("utf-8"), "prompt_sha256": actual_hash,
            "raw_response_path": "", "raw_response_sha256": "", "collection_method": "manual_operator_capture",
            "operator_id": "collector_01", "notes": "Initialized; capture response before finalization.",
            "collection_status": "initialized", "transcript_path": "", "artifact_directory": "artifacts",
            "cli_exit_status": None,
        }
        write_metadata(metadata_path, metadata)
        print(f"Initialized {row['run_id']} at {directory}")
        print(f"Prompt copy: {directory / 'prompt.txt'}")
        print(f"Manifest: {manifest_path.relative_to(ROOT)}")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())