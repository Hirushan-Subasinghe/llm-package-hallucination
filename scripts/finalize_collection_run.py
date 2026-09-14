#!/usr/bin/env python3
"""Finalize a captured run after checking collection integrity."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone

from collection_common import REQUIRED_METADATA, find_run, load_metadata, run_directory, sha256_bytes, write_metadata


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_id")
    args = parser.parse_args()
    try:
        row, _ = find_run(args.run_id)
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
        if metadata.get("workflow", "").endswith("_web"):
            response_path = directory / "response.md"
            required_path = response_path
        else:
            response_path = directory / "transcript.txt"
            required_path = response_path
        if not required_path.is_file():
            errors.append(f"missing required capture: {required_path.name}")
        if errors:
            metadata["collection_status"] = "error"
            write_metadata(metadata_path, metadata)
            print("FAIL:")
            for error in errors:
                print(f"- {error}")
            return 1
        relative_capture = response_path.relative_to(directory)
        metadata["raw_response_path"] = str((directory / relative_capture).relative_to(run_directory(row).parents[2]))
        metadata["raw_response_sha256"] = sha256_bytes(response_path.read_bytes())
        metadata["timestamp"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        metadata["collection_status"] = "completed"
        if not metadata.get("workflow", "").endswith("_web"):
            metadata["transcript_path"] = str(response_path.relative_to(directory))
        write_metadata(metadata_path, metadata)
        print(f"PASS: finalized {args.run_id}")
        print(f"Raw capture SHA-256: {metadata['raw_response_sha256']}")
        return 0
    except (OSError, ValueError, KeyError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())