#!/usr/bin/env python3
"""Offline-only finalization for one stranded v2.6 API observation.

This utility exists for a narrow recovery case: a request was sent but process
interruption occurred before any response bytes were preserved.  It never
imports an HTTP client, never constructs a request, and refuses any run for
which response evidence might still be recoverable.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "manifests" / "api_final_v2.6.0_manifest.csv"
DEFAULT_RAW_ROOT = ROOT / "data" / "final" / "raw"
DEFAULT_AUDIT_DIRECTORY = ROOT / "data" / "final" / "recovery_audits"
FAILURE_REASON = "researcher_interrupted_active_request"
OPERATIONAL_NOTE = "recovery_finalized_after_researcher_interrupted_active_request"


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def atomic_json(path: Path, value: object) -> None:
    content = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def exclusive_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    with path.open("xb") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())


def load_target_row(manifest: Path, run_id: str) -> tuple[dict[str, str], bytes]:
    manifest_bytes = manifest.read_bytes()
    rows = list(csv.DictReader(manifest_bytes.decode("utf-8").splitlines()))
    matches = [row for row in rows if row.get("run_id") == run_id]
    if len(matches) != 1:
        raise ValueError("run ID does not match exactly one requested v2.6 manifest target")
    row = matches[0]
    if row.get("model_set_version") != "api-model-set-1.4.0" or not run_id.startswith("API-v2.6-"):
        raise ValueError("recovery is restricted to a v2.6 manifest target")
    return row, manifest_bytes


def response_evidence(directory: Path) -> list[str]:
    candidates = [directory / "provider_response.json", directory / "response.md"]
    attempts = directory / "attempts"
    if attempts.is_dir():
        candidates.extend(attempts.glob("attempt-*/http_response.bin"))
    return [str(path.relative_to(directory)) for path in candidates if path.is_file()]


def raw_hashes(raw_root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(raw_root)): sha256_bytes(path.read_bytes())
        for path in sorted(raw_root.glob("API-v2.6-*/**/*"))
        if path.is_file()
    }


def validate_stranded_run(row: dict[str, str], directory: Path) -> tuple[dict, bytes, bytes]:
    metadata_path = directory / "metadata.json"
    prompt_path = directory / "prompt.txt"
    request_path = directory / "request.json"
    if not metadata_path.is_file() or not prompt_path.is_file() or not request_path.is_file():
        raise ValueError("required metadata, prompt, or request evidence is missing")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("collection_status") != "requesting":
        raise ValueError("only a stranded requesting observation may be finalized")
    if metadata.get("generation_ended_at_utc") is not None:
        raise ValueError("a stranded requesting observation must not already have an end timestamp")
    if response_evidence(directory):
        raise ValueError("response evidence exists and may be recoverable; refusing conversion")
    prompt = prompt_path.read_bytes()
    request = request_path.read_bytes()
    required_identity = {
        "run_id": "run_id", "phase": "phase", "task_id": "task_id", "category": "category",
        "task_set_version": "task_set_version", "model_set_version": "model_set_version",
        "model_condition_id": "model_condition_id", "api_provider": "api_provider",
    }
    for metadata_key, row_key in required_identity.items():
        if metadata.get(metadata_key) != row[row_key]:
            raise ValueError(f"metadata {metadata_key} does not match requested manifest target")
    if metadata.get("collection_order") != int(row["collection_order"]):
        raise ValueError("metadata collection_order does not match requested manifest target")
    if metadata.get("requested_model_id") != row.get("model_id"):
        raise ValueError("metadata requested_model_id does not match requested manifest target")
    if metadata.get("run_repetition") != int(str(row["run_repetition"])[1:]):
        raise ValueError("metadata run_repetition does not match requested manifest target")
    if metadata.get("prompt_path") != "prompt.txt" or metadata.get("request_path") != "request.json":
        raise ValueError("metadata prompt/request paths are not the required preserved evidence")
    if sha256_bytes(prompt) != row["expected_prompt_sha256"] or metadata.get("prompt_sha256") != row["expected_prompt_sha256"]:
        raise ValueError("preserved prompt does not match manifest evidence")
    if metadata.get("request_sha256") != sha256_bytes(request):
        raise ValueError("preserved request does not match metadata evidence")
    if not metadata.get("generation_started_at_utc"):
        raise ValueError("generation_started_at_utc is required preserved evidence")
    return metadata, prompt, request


def finalize_interrupted_run(
    run_id: str,
    *,
    manifest: Path = DEFAULT_MANIFEST,
    raw_root: Path = DEFAULT_RAW_ROOT,
    audit_directory: Path = DEFAULT_AUDIT_DIRECTORY,
) -> dict:
    """Finalize exactly one response-less v2.6 `requesting` run, offline."""
    row, manifest_bytes = load_target_row(manifest, run_id)
    directory = raw_root / run_id
    metadata, prompt, request = validate_stranded_run(row, directory)
    metadata_path = directory / "metadata.json"
    audit_path = audit_directory / f"{run_id}.pre_recovery_sha256.json"
    audit = {
        "audit_version": "interrupted-api-recovery-1.0.0",
        "recorded_at_utc": utc_now(),
        "operation": "offline_finalize_interrupted_request",
        "run_id": run_id,
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "target_before": {
            "metadata.json": sha256_bytes(metadata_path.read_bytes()),
            "prompt.txt": sha256_bytes(prompt),
            "request.json": sha256_bytes(request),
        },
        "all_v2_6_raw_files_before": raw_hashes(raw_root),
    }
    # The audit is immutable and is written before changing the sole permitted
    # artifact. Existing audit evidence blocks an accidental second invocation.
    exclusive_json(audit_path, audit)
    notes = list(metadata.get("protocol_deviations", []))
    if OPERATIONAL_NOTE not in notes:
        notes.append(OPERATIONAL_NOTE)
    metadata.update({
        "collection_status": "failed",
        "failure_reason": FAILURE_REASON,
        "generation_ended_at_utc": utc_now(),
        "protocol_deviations": notes,
    })
    metadata.pop("response_completion_status", None)
    metadata.pop("finish_reason", None)
    atomic_json(metadata_path, metadata)
    return {
        "run_id": run_id,
        "failure_reason": FAILURE_REASON,
        "audit_path": str(audit_path),
        "metadata_path": str(metadata_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline-only finalization of a stranded v2.6 API request")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--raw-root", type=Path, default=DEFAULT_RAW_ROOT)
    parser.add_argument("--audit-directory", type=Path, default=DEFAULT_AUDIT_DIRECTORY)
    args = parser.parse_args()
    try:
        print(json.dumps(finalize_interrupted_run(args.run_id, manifest=args.manifest, raw_root=args.raw_root, audit_directory=args.audit_directory), sort_keys=True))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
