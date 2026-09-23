#!/usr/bin/env python3
"""Select verified HYBRID API rows and delegate collection to the v2.6 driver.

This layer is intentionally limited to selection.  It verifies the byte hashes
of the frozen manifest and derived HYBRID assignment, excludes manual rows and
already-preserved run directories, then delegates all request, retry, failure,
and pacing behavior to the established v2.6 batch collector.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Iterable

from collect_api_batch import ordered_rows, run_batch
from collect_api_run import DEFAULT_RAW_ROOT, load_config


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "manifests" / "api_final_v2.6.0_manifest.csv"
DEFAULT_ASSIGNMENT = ROOT / "manifests" / "hybrid_assignment_v1.0.0.csv"
DEFAULT_CONFIG = ROOT / "config" / "api_model_set_1.4.0.json"
DEFAULT_STATE = ROOT / "data" / "final" / "api_batch_state_v2.6.0.json"
FROZEN_MANIFEST_SHA256 = "b2b2750b3ae4ce96a867df14117b05c12f214760ef7036d6bbf2f78e44939b7f"
HYBRID_ASSIGNMENT_SHA256 = "e4b9295b2efc0fe639092161561e915c1d0c47f9a545df2699f7fe12595dd54f"
VALID_MODEL_CONDITIONS = ("M1", "M2", "M3", "M4")
ASSIGNMENT_FIELDS = (
    "collection_order", "run_id", "model_condition_id", "run_repetition",
    "task_id", "category", "collection_interface", "api_attempted_before_hybrid",
    "pre_hybrid_collection_status", "assignment_reason",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_models(models: Iterable[str] | None, option: str) -> set[str]:
    selected = set(models or [])
    invalid = sorted(selected - set(VALID_MODEL_CONDITIONS))
    if invalid:
        raise ValueError(f"Unknown model condition(s) for {option}: {', '.join(invalid)}")
    return selected


def read_verified_assignment(manifest_path: Path, assignment_path: Path) -> list[dict[str, str]]:
    """Read the immutable assignment only after both frozen input hashes verify."""
    if sha256(manifest_path) != FROZEN_MANIFEST_SHA256:
        raise ValueError("frozen v2.6 manifest SHA-256 differs from the freeze record")
    if sha256(assignment_path) != HYBRID_ASSIGNMENT_SHA256:
        raise ValueError("HYBRID assignment SHA-256 differs from the verified allocation record")
    with assignment_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != ASSIGNMENT_FIELDS:
            raise ValueError("HYBRID assignment columns differ from the required schema")
        assignment = list(reader)
    if len(assignment) != 360 or len({row["run_id"] for row in assignment}) != 360:
        raise ValueError("HYBRID assignment must contain 360 unique run IDs")
    return assignment


def select_pending_api_rows(
    manifest_path: Path = DEFAULT_MANIFEST,
    assignment_path: Path = DEFAULT_ASSIGNMENT,
    raw_root: Path = DEFAULT_RAW_ROOT,
    *,
    include_models: Iterable[str] | None = None,
    exclude_models: Iterable[str] | None = None,
) -> list[dict[str, object]]:
    """Return only never-attempted, API-assigned rows in frozen collection order.

    An existing run directory is always excluded.  This conservative guard
    keeps this selection layer from ever handing an existing directory to the
    collector, including an existing failed observation or malformed directory.
    The delegated driver retains its own directory guard as a second defense.
    """
    included = _validate_models(include_models, "--model")
    excluded = _validate_models(exclude_models, "--exclude-model")
    if included & excluded:
        overlap = ", ".join(sorted(included & excluded))
        raise ValueError(f"model condition(s) cannot be both included and excluded: {overlap}")

    manifest_rows = ordered_rows(manifest_path)
    assignment = read_verified_assignment(manifest_path, assignment_path)
    by_run_id = {row["run_id"]: row for row in assignment}
    if set(by_run_id) != {str(row["run_id"]) for row in manifest_rows}:
        raise ValueError("HYBRID assignment run IDs do not match the frozen manifest")

    selected: list[dict[str, object]] = []
    for row in manifest_rows:
        run_id = str(row["run_id"])
        assigned = by_run_id[run_id]
        if (
            assigned["collection_order"] != str(row["collection_order"])
            or assigned["model_condition_id"] != str(row["model_condition_id"])
        ):
            raise ValueError(f"HYBRID assignment identity differs from frozen manifest: {run_id}")
        model = str(row["model_condition_id"])
        if assigned["collection_interface"] != "api":
            continue
        if assigned["api_attempted_before_hybrid"] != "false":
            continue
        if raw_root.joinpath(run_id).exists():
            continue
        if included and model not in included:
            continue
        if model in excluded:
            continue
        selected.append(row)
    return selected


def list_rows(rows: list[dict[str, object]]) -> None:
    writer = csv.DictWriter(sys.stdout, fieldnames=("collection_order", "run_id", "model_condition_id"), lineterminator="\n")
    writer.writeheader()
    writer.writerows({field: row[field] for field in writer.fieldnames} for row in rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verified HYBRID-aware v2.6 API batch selector")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--assignment", type=Path, default=DEFAULT_ASSIGNMENT)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--raw-root", type=Path, default=DEFAULT_RAW_ROOT)
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true", help="select only; make no request or writes")
    parser.add_argument("--list", action="store_true", help="print selected rows as CSV; make no request or writes")
    parser.add_argument("--model", action="append", choices=VALID_MODEL_CONDITIONS, metavar="CONDITION", help="include only this model condition (repeatable)")
    parser.add_argument("--exclude-model", action="append", choices=VALID_MODEL_CONDITIONS, metavar="CONDITION", help="exclude this model condition (repeatable; use M3 while TPM-paused)")
    args = parser.parse_args()
    try:
        if args.limit < 1:
            raise ValueError("--limit must be at least 1")
        rows = select_pending_api_rows(
            args.manifest, args.assignment, args.raw_root,
            include_models=args.model, exclude_models=args.exclude_model,
        )
        if args.list:
            list_rows(rows)
            return 0
        result = run_batch(
            load_config(args.config), rows,
            manifest_hash=FROZEN_MANIFEST_SHA256,
            state_path=args.state, raw_root=args.raw_root,
            limit=args.limit, dry_run=args.dry_run, continue_after_failed=True,
        )
    except (OSError, ValueError, csv.Error, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
