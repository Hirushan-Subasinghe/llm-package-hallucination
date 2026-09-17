#!/usr/bin/env python3
"""Sequential, resumable driver for the future frozen official API manifest.

This driver never changes manifest rows. Progress is derived from immutable run
directories and a durable pacing state file. It delegates each request and all
infrastructure-only retry behavior to collect_api_run.collect_row.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from collect_api_run import (
    DEFAULT_CONFIG,
    DEFAULT_RAW_ROOT,
    collect_row,
    load_config,
    load_manifest,
    model_for_row,
    utc_now,
    validate_local_preconditions,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "manifests" / "api_final_v2.3.0_manifest.csv"
DEFAULT_STATE = ROOT / "data" / "final" / "api_batch_state_v2.3.0.json"
MANIFEST_V2_2 = ROOT / "manifests" / "api_final_v2.2.0_manifest.csv"
STATE_V2_2 = ROOT / "data" / "final" / "api_batch_state_v2.2.0.json"
MANIFEST_V2_1 = ROOT / "manifests" / "api_final_v2.1.0_manifest.csv"
STATE_V2_1 = ROOT / "data" / "final" / "api_batch_state_v2.1.0.json"
MANIFEST_V2_0 = ROOT / "manifests" / "api_final_v2.0.0_manifest.csv"
STATE_V2_0 = ROOT / "data" / "final" / "api_batch_state.json"


def epoch_to_utc(value: float) -> str:
    return datetime.fromtimestamp(value, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def load_state(path: Path, manifest_hash: str) -> dict:
    if not path.exists():
        return {
            "state_version": "api-batch-state-1.0.0",
            "manifest_sha256": manifest_hash,
            "provider_next_allowed_at_epoch": {},
            "events": [],
        }
    state = json.loads(path.read_text(encoding="utf-8"))
    if state.get("manifest_sha256") != manifest_hash:
        raise ValueError("Batch state belongs to a different manifest")
    return state


def ordered_rows(path: Path) -> list[dict[str, object]]:
    rows = load_manifest(path)
    orders = [int(row["collection_order"]) for row in rows]
    if len(rows) != 360 or sorted(orders) != list(range(1, 361)) or len(set(orders)) != 360:
        raise ValueError("Official manifest collection order is invalid")
    return sorted(rows, key=lambda row: int(row["collection_order"]))


def existing_status(directory: Path) -> str | None:
    metadata_path = directory / "metadata.json"
    if not metadata_path.is_file():
        return None
    try:
        return json.loads(metadata_path.read_text(encoding="utf-8")).get("collection_status")
    except (OSError, json.JSONDecodeError):
        return None


def minimum_interval(config: dict, api_provider: str) -> int:
    pacing = config["batch_pacing"]
    if api_provider == "Groq":
        return int(pacing["minimum_seconds_between_groq_requests"])
    if api_provider == "OpenRouter":
        return int(pacing["minimum_seconds_between_openrouter_requests"])
    raise ValueError(f"Unsupported API provider: {api_provider}")


def run_batch(
    config: dict,
    rows: list[dict[str, object]],
    *,
    manifest_hash: str,
    state_path: Path = DEFAULT_STATE,
    raw_root: Path = DEFAULT_RAW_ROOT,
    limit: int = 1,
    dry_run: bool = False,
    now: Callable[[], float] = time.time,
    sleeper: Callable[[float], None] = time.sleep,
    collector: Callable[..., Path] = collect_row,
) -> dict:
    if config.get("status") != "frozen_for_collection":
        raise ValueError("Batch collection requires the frozen model set")
    state = load_state(state_path, manifest_hash)
    processed = 0
    for row in rows:
        if processed >= limit:
            break
        run_directory = raw_root / str(row["run_id"])
        if run_directory.exists():
            status = existing_status(run_directory)
            if status in {"completed", "truncated"}:
                if not dry_run:
                    state["events"].append({"at_utc": utc_now(), "event": "skipped_preserved_observation", "run_id": row["run_id"], "status": status})
                    state["updated_at_utc"] = utc_now()
                    atomic_json(state_path, state)
                continue
            if not dry_run:
                state["events"].append({"at_utc": utc_now(), "event": "temporarily_blocked_existing_run", "run_id": row["run_id"], "status": status})
                state["updated_at_utc"] = utc_now()
                atomic_json(state_path, state)
            return {
                "processed": processed,
                "blocked_run_id": row["run_id"],
                "blocked_collection_order": int(row["collection_order"]),
                "existing_status": status,
                "state_path": str(state_path),
            }

        model = model_for_row(config, row)
        provider = model["api_provider"]
        current = now()
        not_before = float(state["provider_next_allowed_at_epoch"].get(provider, 0))
        wait_seconds = max(0.0, not_before - current)
        if dry_run:
            return {
                "next_run_id": row["run_id"],
                "collection_order": int(row["collection_order"]),
                "api_provider": provider,
                "wait_seconds": wait_seconds,
            }

        # Complete all local pre-transmission validation BEFORE reserving provider pacing slot.
        # This checks API key existence, model configuration, prompt path/hash, request body construction, and directory checks.
        validate_local_preconditions(config, row, raw_root=raw_root)

        if wait_seconds:
            sleeper(wait_seconds)
            current = now()

        interval = minimum_interval(config, provider)
        state["provider_next_allowed_at_epoch"][provider] = current + interval
        state["events"].append({
            "at_utc": utc_now(),
            "event": "request_slot_reserved",
            "run_id": row["run_id"],
            "collection_order": int(row["collection_order"]),
            "api_provider": provider,
            "next_provider_request_not_before_utc": epoch_to_utc(current + interval),
        })
        state["updated_at_utc"] = utc_now()
        atomic_json(state_path, state)

        try:
            directory = collector(config, row, raw_root=raw_root)
        except Exception as error:
            failure_reason = None
            metadata_path = raw_root / str(row["run_id"]) / "metadata.json"
            try:
                failure_reason = json.loads(metadata_path.read_text(encoding="utf-8")).get("failure_reason")
            except (OSError, json.JSONDecodeError):
                pass
            state["events"].append({
                "at_utc": utc_now(),
                "event": "temporarily_blocked_or_failed",
                "run_id": row["run_id"],
                "error_type": type(error).__name__,
                "failure_reason": failure_reason,
            })
            if failure_reason and failure_reason.startswith("http_status_"):
                state["events"].append({
                    "at_utc": utc_now(),
                    "event": "batch_stopped_nonretryable_provider_failure",
                    "run_id": row["run_id"],
                    "collection_order": int(row["collection_order"]),
                    "failure_reason": failure_reason,
                    "action": "stopped_without_skipping_or_substitution",
                })
            state["updated_at_utc"] = utc_now()
            atomic_json(state_path, state)
            raise
        state["events"].append({"at_utc": utc_now(), "event": "completed", "run_id": row["run_id"], "directory": str(directory)})
        state["updated_at_utc"] = utc_now()
        atomic_json(state_path, state)
        processed += 1
    return {"processed": processed, "state_path": str(state_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Sequential frozen v2 API batch collector")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--raw-root", type=Path, default=DEFAULT_RAW_ROOT)
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        if args.limit < 1:
            raise ValueError("--limit must be at least 1")
        manifest_bytes = args.manifest.read_bytes()
        result = run_batch(
            load_config(args.config),
            ordered_rows(args.manifest),
            manifest_hash=hashlib.sha256(manifest_bytes).hexdigest(),
            state_path=args.state,
            raw_root=args.raw_root,
            limit=args.limit,
            dry_run=args.dry_run,
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
