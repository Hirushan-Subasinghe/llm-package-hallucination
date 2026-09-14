#!/usr/bin/env python3
"""Report collection-integrity status without interpreting generated dependencies."""

from __future__ import annotations

import argparse
import sys

from collection_common import REQUIRED_METADATA, ROOT, load_metadata, read_manifest, run_directory, sha256_bytes


def verify_phase(phase: str) -> int:
    rows, _ = read_manifest(phase)
    expected = 24 if phase == "pilot" else 360
    counts = {"completed": 0, "pending": 0, "error/incomplete": 0, "missing directories": 0, "prompt-hash mismatches": 0, "metadata problems": 0}
    for row in rows:
        directory = run_directory(row)
        if not directory.is_dir():
            counts["missing directories"] += 1
            continue
        metadata_path = directory / "metadata.json"
        if not metadata_path.is_file():
            counts["error/incomplete"] += 1
            continue
        try:
            metadata = load_metadata(metadata_path)
            prompt_path = ROOT / row["rendered_prompt_path"]
            prompt_copy = directory / "prompt.txt"
            integrity_ok = True
            if sha256_bytes(prompt_path.read_bytes()) != row["expected_prompt_sha256"]:
                counts["prompt-hash mismatches"] += 1
                integrity_ok = False
            if not prompt_copy.is_file() or sha256_bytes(prompt_copy.read_bytes()) != row["expected_prompt_sha256"]:
                counts["prompt-hash mismatches"] += 1
                integrity_ok = False
            if any(field not in metadata for field in REQUIRED_METADATA):
                counts["metadata problems"] += 1
                integrity_ok = False
            if metadata.get("run_id") != row["run_id"] or metadata.get("prompt_id") != row["prompt_id"]:
                counts["metadata problems"] += 1
                integrity_ok = False
            if metadata.get("workflow", "").endswith("_web"):
                capture_path = directory / "response.md"
            else:
                capture_path = directory / "transcript.txt"
            if not capture_path.is_file():
                integrity_ok = False
            if metadata.get("collection_status") == "completed" and integrity_ok:
                counts["completed"] += 1
            elif metadata.get("collection_status") in ("pending", "initialized"):
                counts["pending"] += 1
            else:
                counts["error/incomplete"] += 1
        except (OSError, ValueError):
            counts["metadata problems"] += 1
    print(f"Phase: {phase}")
    print(f"Expected runs: {expected}")
    print(f"Manifest rows: {len(rows)}")
    for label, count in counts.items():
        print(f"{label}: {count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("pilot", "final"), required=True)
    args = parser.parse_args()
    try:
        return verify_phase(args.phase)
    except (OSError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())