#!/usr/bin/env python3
"""Sequential v2.6 collector; dry-run never sends a request or changes state."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from collect_api_batch import ordered_rows, run_batch
from collect_api_run import DEFAULT_RAW_ROOT, load_config
from repository_guard import assert_live_collection_allowed

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "manifests/api_final_v2.6.0_manifest.csv"
DEFAULT_CONFIG = ROOT / "config/api_model_set_1.4.0.json"
DEFAULT_STATE = ROOT / "data/final/api_batch_state_v2.6.0.json"
VALID_MODEL_CONDITIONS = ("M1", "M2", "M3", "M4")


def filter_excluded_models(
    rows: list[dict[str, object]], excluded_conditions: list[str] | None
) -> list[dict[str, object]]:
    """Drop rows whose model_condition_id is excluded, preserving manifest order.

    This is an in-memory operational filter only: it never touches the manifest
    file, never renumbers collection_order, and never marks an excluded pending
    row failed/skipped/completed. Excluded rows are simply absent from this
    invocation's attempt list, so a later included row can be collected while
    an earlier excluded row remains pending.
    """
    if not excluded_conditions:
        return rows
    invalid = sorted(set(excluded_conditions) - set(VALID_MODEL_CONDITIONS))
    if invalid:
        raise ValueError(f"Unknown model condition(s) for --exclude-model: {', '.join(invalid)}")
    excluded = set(excluded_conditions)
    return [row for row in rows if row["model_condition_id"] not in excluded]


def main() -> int:
    parser = argparse.ArgumentParser(description="Sequential prospective v2.6 API batch collector")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--raw-root", type=Path, default=DEFAULT_RAW_ROOT)
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--exclude-model",
        action="append",
        choices=VALID_MODEL_CONDITIONS,
        default=None,
        metavar="CONDITION",
        help=(
            "Model condition id to exclude from this invocation's pending-row "
            "selection (repeatable, e.g. --exclude-model M2). Operational "
            "scheduling filter only: the manifest, collection_order, and any "
            "existing completed/truncated/failed observations are untouched, "
            "and excluded pending rows remain pending."
        ),
    )
    args = parser.parse_args()
    try:
        assert_live_collection_allowed()
        if args.limit < 1:
            raise ValueError("--limit must be at least 1")
        rows = filter_excluded_models(ordered_rows(args.manifest), args.exclude_model)
        result = run_batch(
            load_config(args.config), rows,
            manifest_hash=hashlib.sha256(args.manifest.read_bytes()).hexdigest(),
            state_path=args.state, raw_root=args.raw_root,
            limit=args.limit, dry_run=args.dry_run, continue_after_failed=True,
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
