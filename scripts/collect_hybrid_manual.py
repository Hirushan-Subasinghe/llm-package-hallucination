#!/usr/bin/env python3
"""Offline, append-only preparation and capture for HYBRID manual rows.

This utility never invokes a model, API, browser, or generated code.  It only
selects rows already assigned to the manual interface, verifies both governing
CSV files, displays their verified rendered prompt, and (when explicitly asked)
preserves operator-supplied bytes in a separate manual-artifact root.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from collect_hybrid_api_batch import (
    ASSIGNMENT_FIELDS,
    FROZEN_MANIFEST_SHA256,
    HYBRID_ASSIGNMENT_SHA256,
    VALID_MODEL_CONDITIONS,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "manifests" / "api_final_v2.6.0_manifest.csv"
DEFAULT_ASSIGNMENT = ROOT / "manifests" / "hybrid_assignment_v1.0.0.csv"
# Deliberately outside data/final/raw, which is the existing API artifact root.
DEFAULT_MANUAL_ROOT = ROOT / "data" / "final" / "manual_raw" / "v2.6.0"


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _models(models: Iterable[str] | None) -> set[str]:
    result = set(models or [])
    invalid = result - set(VALID_MODEL_CONDITIONS)
    if invalid:
        raise ValueError(f"Unknown model condition(s): {', '.join(sorted(invalid))}")
    return result


def read_verified_rows(manifest_path: Path, assignment_path: Path) -> tuple[list[dict[str, str]], dict[str, dict[str, str]]]:
    """Load only after the freeze and HYBRID artifact identities are verified."""
    if sha256(manifest_path) != FROZEN_MANIFEST_SHA256:
        raise ValueError("frozen v2.6 manifest SHA-256 differs from the freeze record")
    if sha256(assignment_path) != HYBRID_ASSIGNMENT_SHA256:
        raise ValueError("HYBRID assignment SHA-256 differs from the verified allocation record")
    with manifest_path.open(newline="", encoding="utf-8") as handle:
        manifest = list(csv.DictReader(handle))
    with assignment_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != ASSIGNMENT_FIELDS:
            raise ValueError("HYBRID assignment columns differ from the required schema")
        assignment_rows = list(reader)
    if len(manifest) != 360 or len(assignment_rows) != 360:
        raise ValueError("frozen manifest and HYBRID assignment must each contain 360 rows")
    assignment = {row["run_id"]: row for row in assignment_rows}
    if len(assignment) != 360 or set(assignment) != {row["run_id"] for row in manifest}:
        raise ValueError("HYBRID assignment run IDs do not match the frozen manifest")
    for row in manifest:
        assigned = assignment[row["run_id"]]
        for field in ("collection_order", "model_condition_id", "run_repetition", "task_id", "category"):
            if assigned[field] != row[field]:
                raise ValueError(f"HYBRID assignment identity differs from frozen manifest: {row['run_id']}")
    return manifest, assignment


def select_manual_rows(
    manifest_path: Path = DEFAULT_MANIFEST,
    assignment_path: Path = DEFAULT_ASSIGNMENT,
    *,
    include_models: Iterable[str] | None = None,
    manual_root: Path | None = None,
    include_observed: bool = True,
) -> list[dict[str, str]]:
    """Return manual-assigned rows only, in immutable frozen collection order."""
    models = _models(include_models)
    manifest, assignment = read_verified_rows(manifest_path, assignment_path)
    root = DEFAULT_MANUAL_ROOT if manual_root is None else manual_root
    selected = []
    for row in manifest:
        if assignment[row["run_id"]]["collection_interface"] != "manual":
            continue
        if models and row["model_condition_id"] not in models:
            continue
        if not include_observed and (root / row["run_id"]).exists():
            continue
        selected.append(row)
    return selected


def verified_prompt(row: dict[str, str]) -> bytes:
    prompt_path = ROOT / row["rendered_prompt_path"]
    prompt = prompt_path.read_bytes()
    if sha256_bytes(prompt) != row["expected_prompt_sha256"]:
        raise ValueError(f"rendered prompt SHA-256 differs from frozen manifest: {row['run_id']}")
    return prompt


def display_row(row: dict[str, str]) -> None:
    prompt = verified_prompt(row)
    print(json.dumps({
        "collection_interface": "manual",
        "collection_order": int(row["collection_order"]),
        "expected_model_id": row["model_id"],
        "model_condition_id": row["model_condition_id"],
        "prompt_path": row["rendered_prompt_path"],
        "prompt_sha256": row["expected_prompt_sha256"],
        "run_id": row["run_id"],
        "run_repetition": row["run_repetition"],
    }, sort_keys=True))
    sys.stdout.flush()
    sys.stdout.buffer.write(b"\n--- exact rendered prompt (UTF-8 bytes) ---\n")
    sys.stdout.buffer.write(prompt)
    if not prompt.endswith(b"\n"):
        sys.stdout.buffer.write(b"\n")


def prepare(row: dict[str, str], manual_root: Path, *, dry_run: bool) -> Path:
    """Create an empty append-only manual run directory; never overwrite one."""
    directory = manual_root / row["run_id"]
    if directory.exists():
        raise ValueError(f"manual observation already exists; refusing overwrite: {directory}")
    prompt = verified_prompt(row)
    if dry_run:
        return directory
    directory.mkdir(parents=True, exist_ok=False)
    try:
        (directory / "prompt.txt").write_bytes(prompt)
        metadata = {
            "run_id": row["run_id"], "collection_order": int(row["collection_order"]),
            "model_condition_id": row["model_condition_id"], "expected_model_id": row["model_id"],
            "run_repetition": row["run_repetition"], "task_id": row["task_id"], "category": row["category"],
            "collection_interface": "manual", "actual_model": "not_observed",
            "actual_interface": "not_observed", "prompt_path": row["rendered_prompt_path"],
            "prompt_sha256": row["expected_prompt_sha256"], "initialized_at_utc": utc_now(),
            "response_status": "initialized", "raw_response_path": "", "raw_response_sha256": "",
            "raw_response_size_bytes": 0,
        }
        (directory / "metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except Exception:
        # A partial directory is intentionally retained and blocks reuse; it is evidence to inspect.
        raise
    return directory


def is_pristine_preparation(directory: Path, row: dict[str, str]) -> bool:
    """A prepared directory is not yet an observation and may receive one capture."""
    metadata_path = directory / "metadata.json"
    prompt_path = directory / "prompt.txt"
    if not metadata_path.is_file() or not prompt_path.is_file() or (directory / "response.md").exists():
        return False
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return (
        {path.name for path in directory.iterdir()} == {"prompt.txt", "metadata.json"}
        and metadata.get("response_status") == "initialized"
        and metadata.get("run_id") == row["run_id"]
        and metadata.get("prompt_sha256") == row["expected_prompt_sha256"]
        and sha256_bytes(prompt_path.read_bytes()) == row["expected_prompt_sha256"]
    )


def capture(
    row: dict[str, str], manual_root: Path, response: bytes, *, actual_model: str,
    actual_interface: str, response_status: str, operator_id: str, failure_note: str,
) -> Path:
    """Preserve supplied bytes exactly once, with no automatic retry capability."""
    if not actual_model.strip() or not actual_interface.strip():
        raise ValueError("actual model and actual interface must be recorded verbatim")
    directory = manual_root / row["run_id"]
    if directory.exists() and not is_pristine_preparation(directory, row):
        raise ValueError(f"manual observation already exists; refusing overwrite: {directory}")
    prompt = verified_prompt(row)
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=False)
    try:
        prompt_path = directory / "prompt.txt"
        if not prompt_path.exists():
            prompt_path.write_bytes(prompt)
        with (directory / "response.md").open("xb") as handle:
            handle.write(response)
        metadata = {
            "run_id": row["run_id"], "collection_order": int(row["collection_order"]),
            "model_condition_id": row["model_condition_id"], "expected_model_id": row["model_id"],
            "actual_model": actual_model, "actual_interface": actual_interface,
            "collection_interface": "manual", "run_repetition": row["run_repetition"],
            "task_id": row["task_id"], "category": row["category"],
            "prompt_path": row["rendered_prompt_path"], "prompt_sha256": row["expected_prompt_sha256"],
            "captured_at_utc": utc_now(), "operator_id": operator_id,
            "response_status": response_status, "failure_or_interruption_note": failure_note,
            "raw_response_path": str(Path("data/final/manual_raw/v2.6.0") / row["run_id"] / "response.md"),
            "raw_response_sha256": sha256_bytes(response), "raw_response_size_bytes": len(response),
        }
        (directory / "metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except Exception:
        raise
    return directory


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline HYBRID manual collection helper; it never calls a model or API.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--assignment", type=Path, default=DEFAULT_ASSIGNMENT)
    parser.add_argument("--manual-root", type=Path, default=DEFAULT_MANUAL_ROOT)
    parser.add_argument("--model", action="append", choices=VALID_MODEL_CONDITIONS, metavar="CONDITION")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--list", action="store_true", help="list eligible manual rows; no writes")
    action.add_argument("--show-next", action="store_true", help="show next unobserved verified prompt; no writes")
    action.add_argument("--prepare", action="store_true", help="initialize next unobserved manual directory")
    action.add_argument("--capture-stdin", action="store_true", help="record stdin bytes for --run-id exactly once")
    parser.add_argument("--dry-run", action="store_true", help="show what --prepare would initialize; no writes")
    parser.add_argument("--run-id", help="required with --capture-stdin")
    parser.add_argument("--actual-model", default="", help="observed model label/ID, verbatim")
    parser.add_argument("--actual-interface", default="", help="observed interface label, verbatim")
    parser.add_argument("--response-status", choices=("completed", "truncated", "failed", "interrupted"), default="completed")
    parser.add_argument("--operator-id", default="collector_01")
    parser.add_argument("--failure-note", default="")
    args = parser.parse_args()
    try:
        if args.dry_run and args.capture_stdin:
            raise ValueError("--dry-run cannot capture stdin")
        rows = select_manual_rows(args.manifest, args.assignment, include_models=args.model, manual_root=args.manual_root, include_observed=True)
        if args.list:
            writer = csv.DictWriter(sys.stdout, fieldnames=("collection_order", "run_id", "model_condition_id", "run_repetition", "task_id"), lineterminator="\n")
            writer.writeheader()
            writer.writerows({field: row[field] for field in writer.fieldnames} for row in rows)
            return 0
        if args.capture_stdin:
            if not args.run_id:
                raise ValueError("--run-id is required with --capture-stdin")
            matches = [row for row in rows if row["run_id"] == args.run_id]
            if len(matches) != 1:
                raise ValueError("run ID is not a manual-assigned row for the selected model filter")
            directory = capture(matches[0], args.manual_root, sys.stdin.buffer.read(), actual_model=args.actual_model,
                                actual_interface=args.actual_interface, response_status=args.response_status,
                                operator_id=args.operator_id, failure_note=args.failure_note)
            print(f"Preserved manual observation at {directory}")
            return 0
        pending = select_manual_rows(args.manifest, args.assignment, include_models=args.model, manual_root=args.manual_root, include_observed=False)
        if not pending:
            raise ValueError("no unobserved manual-assigned rows remain")
        if args.prepare:
            directory = prepare(pending[0], args.manual_root, dry_run=args.dry_run)
            print(f"{'Would initialize' if args.dry_run else 'Initialized'} {pending[0]['run_id']} at {directory}")
        display_row(pending[0])
        return 0
    except (OSError, ValueError, csv.Error) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
