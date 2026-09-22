#!/usr/bin/env python3
"""Verify a rendered prompt hash for a run or prompt ID."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from collection_common import ROOT, find_run, read_manifest, sha256_bytes


def verify_rows(rows: list[dict[str, str]]) -> list[tuple[str, bool, str, str]]:
    results = []
    for row in rows:
        path = ROOT / row["rendered_prompt_path"]
        actual = sha256_bytes(path.read_bytes())
        expected = row["expected_prompt_sha256"]
        results.append((row["run_id"], actual == expected, actual, expected))
    return results


def verify_run_prompt(run_id: str) -> tuple[str, bool, str, str]:
    return verify_rows([find_run(run_id)[0]])[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--run-id")
    group.add_argument("--prompt-id")
    args = parser.parse_args()
    try:
        if args.run_id:
            rows = [find_run(args.run_id)[0]]
        else:
            rows = []
            for phase in ("pilot", "final"):
                phase_rows, _ = read_manifest(phase)
                rows.extend(row for row in phase_rows if row["prompt_id"] == args.prompt_id)
            if not rows:
                raise ValueError(f"Unknown prompt ID: {args.prompt_id}")
        results = verify_rows(rows)
        failed = [result for result in results if not result[1]]
        for run_id, passed, actual, expected in results:
            print(f"{'PASS' if passed else 'FAIL'} {run_id} {actual}")
            if not passed:
                print(f"  expected: {expected}")
        return 1 if failed else 0
    except (OSError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
