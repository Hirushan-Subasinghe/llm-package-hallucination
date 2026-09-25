#!/usr/bin/env python3
"""Build a read-only response inventory for the experimental dataset.

This script never modifies manifests, state files, or raw model responses.
It inspects the planned manifest rows alongside any immutable raw run directories
and outputs a structured inventory in results/ (or specified path).

Decision D035 is applied here as a derived status overlay: a raw observation
recorded as completed/truncated whose provider finish_reason is neither "stop"
nor "length" (e.g. "error") is inventoried as failed/FAILED.  The raw metadata
is never rewritten; the row keeps the raw status and finish reason and carries
``status_correction = "D035"``.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "manifests" / "api_final_v2.2.0_manifest.csv"
DEFAULT_RAW_ROOT = ROOT / "data" / "final" / "raw"
DEFAULT_STATE = ROOT / "data" / "final" / "api_batch_state_v2.2.0.json"
DEFAULT_OUTPUT_JSON = ROOT / "results" / "response_inventory_v2.2.0.json"
DEFAULT_OUTPUT_CSV = ROOT / "results" / "response_inventory_v2.2.0.csv"

INVENTORY_COLUMNS = [
    "run_id",
    "collection_order",
    "provider",
    "tool",
    "model",
    "model_condition_id",
    "workflow",
    "task_id",
    "category",
    "replicate",
    "manifest_path",
    "rendered_prompt_path",
    "expected_prompt_sha256",
    "response_artifact_path",
    "collection_status",
    "completion_status",
    "truncated",
    "token_count",
    "interface_pass",
    "raw_collection_status",
    "provider_finish_reason",
    "status_correction",
]

D035_STATUS_CORRECTION = "D035"
NORMAL_FINISH_REASONS = frozenset({"stop", "length"})


def load_manifest_rows(manifest_path: Path) -> list[dict[str, str]]:
    """Read manifest rows deterministically, preserving collection order."""
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Manifest file not found: {manifest_path}")
    with manifest_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"Manifest is empty: {manifest_path}")
    try:
        rows.sort(key=lambda r: int(r["collection_order"]))
    except (KeyError, ValueError) as error:
        raise ValueError(f"Manifest missing or invalid collection_order: {error}") from error
    return rows


def relative_to_root(path: Path, root: Path = ROOT) -> str:
    """Format path relative to repository root if possible, else as resolved str."""
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def empty_run_status(collection_status: str = "pending") -> dict[str, Any]:
    return {
        "collection_status": collection_status,
        "completion_status": None,
        "truncated": None,
        "token_count": None,
        "response_artifact_path": None,
        "raw_collection_status": None,
        "provider_finish_reason": None,
        "status_correction": None,
    }


def inspect_run_directory(run_dir: Path, root: Path = ROOT) -> dict[str, Any]:
    """Inspect an immutable raw run directory (read-only).

    Returns the derived inventory status fields for the run.  The raw
    ``collection_status`` and ``finish_reason`` are reported unchanged; only
    the derived ``collection_status``/``completion_status`` reflect D035.
    """
    if not run_dir.is_dir():
        return empty_run_status()

    metadata_path = run_dir / "metadata.json"
    if not metadata_path.is_file():
        return empty_run_status()

    try:
        with metadata_path.open(encoding="utf-8") as handle:
            metadata: dict[str, Any] = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return empty_run_status("failed")

    raw_collection_status = str(metadata.get("collection_status", "pending"))
    collection_status = raw_collection_status
    completion_status: Optional[str] = metadata.get("response_completion_status")
    finish_reason = metadata.get("finish_reason")
    status_correction: Optional[str] = None

    # D035: a provider-declared abnormal termination is failed even when
    # partial content was preserved.  Records without a finish_reason field
    # (non-API pilot collections) are outside the rule.
    if (
        collection_status in {"completed", "truncated"}
        and "finish_reason" in metadata
        and finish_reason not in NORMAL_FINISH_REASONS
    ):
        collection_status = "failed"
        completion_status = "FAILED"
        status_correction = D035_STATUS_CORRECTION

    is_truncated: Optional[bool] = None
    if collection_status in {"completed", "truncated"}:
        is_truncated = (
            collection_status == "truncated"
            or completion_status == "TRUNCATED"
            or finish_reason == "length"
        )
    elif collection_status == "failed":
        is_truncated = False

    token_count: Optional[int] = None
    resp_tokens = metadata.get("response_token_metadata")
    if isinstance(resp_tokens, dict) and resp_tokens.get("total_completion_tokens") is not None:
        try:
            token_count = int(resp_tokens["total_completion_tokens"])
        except (ValueError, TypeError):
            pass

    if token_count is None:
        usage = metadata.get("token_usage")
        if isinstance(usage, dict) and usage.get("completion_tokens") is not None:
            try:
                token_count = int(usage["completion_tokens"])
            except (ValueError, TypeError):
                pass

    response_artifact_path: Optional[str] = None
    response_rel_name = metadata.get("response_path", "response.md")
    response_file = run_dir / str(response_rel_name)
    if response_file.is_file():
        response_artifact_path = relative_to_root(response_file, root)

    return {
        "collection_status": collection_status,
        "completion_status": completion_status,
        "truncated": is_truncated,
        "token_count": token_count,
        "response_artifact_path": response_artifact_path,
        "raw_collection_status": raw_collection_status,
        "provider_finish_reason": finish_reason,
        "status_correction": status_correction,
    }


def failed_run_ids_from_state(state_path: Path) -> set[str]:
    """Return run IDs with an explicit terminal batch-failure event.

    A reserved request slot proves only that an attempt may have started, so it
    is deliberately not treated as a failure.  The batch collector emits
    ``temporarily_blocked_or_failed`` only after its per-run collector raises.
    """
    if not state_path.is_file():
        return set()
    try:
        with state_path.open(encoding="utf-8") as handle:
            state: dict[str, Any] = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return set()
    events = state.get("events")
    if not isinstance(events, list):
        return set()
    return {
        event["run_id"]
        for event in events
        if isinstance(event, dict)
        and event.get("event") == "temporarily_blocked_or_failed"
        and isinstance(event.get("run_id"), str)
    }


def has_preserved_failed_attempt(run_dir: Path) -> bool:
    """Whether the run directory contains collector-designated failure evidence."""
    failed_attempts = run_dir / "failed_attempts"
    return failed_attempts.is_dir() and any(
        path.is_dir() and path.name.startswith("attempt-")
        for path in failed_attempts.iterdir()
    )


def build_inventory_row(
    manifest_row: dict[str, str],
    manifest_path: Path,
    raw_root: Path,
    failed_run_ids: set[str],
    root: Path = ROOT,
) -> dict[str, Any]:
    """Construct an inventory record for one manifest row."""
    run_id = manifest_row["run_id"]
    collection_order = int(manifest_row["collection_order"])
    provider = manifest_row.get("api_provider", "")
    model = manifest_row.get("model_id", "")
    model_condition_id = manifest_row.get("model_condition_id", "")
    task_id = manifest_row.get("task_id", "")
    category = manifest_row.get("category", "")
    replicate = manifest_row.get("run_repetition", "")
    rendered_prompt_path = manifest_row.get("rendered_prompt_path", "")
    expected_prompt_sha256 = manifest_row.get("expected_prompt_sha256", "")

    run_dir = raw_root / run_id
    run_status = inspect_run_directory(run_dir, root=root)
    collection_status = run_status["collection_status"]

    # Metadata is authoritative.  Only in its absence do collector-preserved
    # failure artifacts or a terminal batch failure event distinguish a failed
    # attempt from a never-attempted pending run.
    if collection_status == "pending" and (
        run_id in failed_run_ids or has_preserved_failed_attempt(run_dir)
    ):
        collection_status = "failed"

    manifest_rel_path = relative_to_root(manifest_path, root)

    return {
        "run_id": run_id,
        "collection_order": collection_order,
        "provider": provider,
        "tool": None,
        "model": model,
        "model_condition_id": model_condition_id,
        "workflow": None,
        "task_id": task_id,
        "category": category,
        "replicate": replicate,
        "manifest_path": manifest_rel_path,
        "rendered_prompt_path": rendered_prompt_path,
        "expected_prompt_sha256": expected_prompt_sha256,
        "response_artifact_path": run_status["response_artifact_path"],
        "collection_status": collection_status,
        "completion_status": run_status["completion_status"],
        "truncated": run_status["truncated"],
        "token_count": run_status["token_count"],
        "interface_pass": None,
        "raw_collection_status": run_status["raw_collection_status"],
        "provider_finish_reason": run_status["provider_finish_reason"],
        "status_correction": run_status["status_correction"],
    }


def build_response_inventory(
    manifest_path: Path = DEFAULT_MANIFEST,
    raw_root: Path = DEFAULT_RAW_ROOT,
    state_path: Path = DEFAULT_STATE,
    root: Path = ROOT,
) -> list[dict[str, Any]]:
    """Build complete inventory list for all manifest rows."""
    manifest_rows = load_manifest_rows(manifest_path)
    failed_run_ids = failed_run_ids_from_state(state_path)
    inventory = [
        build_inventory_row(row, manifest_path, raw_root, failed_run_ids, root=root)
        for row in manifest_rows
    ]
    return inventory


def write_inventory_json(inventory: list[dict[str, Any]], output_path: Path) -> None:
    """Write inventory records to a formatted JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(inventory, indent=2) + "\n"
    output_path.write_text(content, encoding="utf-8")


def write_inventory_csv(inventory: list[dict[str, Any]], output_path: Path) -> None:
    """Write inventory records to a CSV file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=INVENTORY_COLUMNS)
        writer.writeheader()
        for item in inventory:
            writer.writerow({
                k: ("" if v is None else v) for k, v in item.items()
            })


def summarize_inventory(inventory: list[dict[str, Any]]) -> dict[str, int]:
    """Compute summary counts by collection_status."""
    counts: dict[str, int] = {}
    for item in inventory:
        status = item["collection_status"]
        counts[status] = counts.get(status, 0) + 1
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Build read-only response inventory for experimental dataset")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="Path to manifest CSV")
    parser.add_argument("--raw-root", type=Path, default=DEFAULT_RAW_ROOT, help="Path to raw data directory")
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE, help="Read-only batch state path")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON, help="Path for JSON output")
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV, help="Path for CSV output")
    parser.add_argument("--quiet", action="store_true", help="Suppress console summary")
    args = parser.parse_args()

    try:
        inventory = build_response_inventory(
            manifest_path=args.manifest,
            raw_root=args.raw_root,
            state_path=args.state,
            root=ROOT,
        )
        if args.output_json:
            write_inventory_json(inventory, args.output_json)
        if args.output_csv:
            write_inventory_csv(inventory, args.output_csv)
    except (OSError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    if not args.quiet:
        counts = summarize_inventory(inventory)
        print(f"Manifest: {args.manifest}")
        print(f"Total planned runs: {len(inventory)}")
        for status, count in sorted(counts.items()):
            print(f"  {status}: {count}")
        corrected = [item["run_id"] for item in inventory if item["status_correction"] == D035_STATUS_CORRECTION]
        print(f"D035 status corrections (raw completed/truncated -> failed): {len(corrected)}")
        for run_id in corrected:
            print(f"  {run_id}")
        if args.output_json:
            print(f"Wrote JSON inventory: {args.output_json}")
        if args.output_csv:
            print(f"Wrote CSV inventory: {args.output_csv}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
