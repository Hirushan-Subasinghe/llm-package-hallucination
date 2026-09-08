#!/usr/bin/env python3
"""Append one technical-failure attempt without changing generation progress."""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from experiment.evidence_capture import FAILURE_CATEGORIES, record_failure  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("generation_id")
    parser.add_argument("attempt_id")
    parser.add_argument("--attempt-timestamp", required=True, help="Observed ISO 8601 timestamp with timezone")
    parser.add_argument("--failure-category", required=True, choices=sorted(FAILURE_CATEGORIES))
    parser.add_argument("--failure-summary-redacted")
    args = parser.parse_args()
    record = record_failure(
        ROOT / "data/manifests/baseline_v1.0.0.jsonl",
        ROOT / "data/failed",
        args.generation_id,
        args.attempt_id,
        args.attempt_timestamp,
        args.failure_category,
        failure_summary_redacted=args.failure_summary_redacted,
    )
    print(f'recorded failed {record["attempt_id"]} for {record["generation_id"]}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
