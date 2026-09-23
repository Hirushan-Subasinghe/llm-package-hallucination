#!/usr/bin/env python3
"""Build and verify the derived v2.6 hybrid interface-allocation layer.

This utility is deliberately read-only with respect to the frozen v2.6
manifest and preserved raw observations.  It assigns every preserved v2.6 raw
observation to the API interface, then fills each remaining API quota using
the earliest never-attempted row for that model in frozen manifest order.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests" / "api_final_v2.6.0_manifest.csv"
RAW_ROOT = ROOT / "data" / "final" / "raw"
ASSIGNMENT = ROOT / "manifests" / "hybrid_assignment_v1.0.0.csv"
REPORT = ROOT / "reports" / "hybrid_assignment_v1.0.0_report.md"

FROZEN_MANIFEST_SHA256 = "b2b2750b3ae4ce96a867df14117b05c12f214760ef7036d6bbf2f78e44939b7f"
API_TARGETS = {"M1": 40, "M2": 40, "M3": 41, "M4": 59}
MANUAL_TARGETS = {"M1": 50, "M2": 50, "M3": 49, "M4": 31}
MODELS = tuple(API_TARGETS)
ASSIGNMENT_FIELDS = (
    "collection_order",
    "run_id",
    "model_condition_id",
    "run_repetition",
    "task_id",
    "category",
    "collection_interface",
    "api_attempted_before_hybrid",
    "pre_hybrid_collection_status",
    "assignment_reason",
)
ATTEMPTED_STATUSES = {"completed", "truncated", "failed"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_manifest() -> list[dict[str, str]]:
    with MANIFEST.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 360:
        raise ValueError(f"frozen manifest has {len(rows)} rows, expected 360")
    if set(rows[0]) < {"collection_order", "run_id", "model_condition_id", "run_repetition", "task_id", "category"}:
        raise ValueError("frozen manifest is missing required columns")
    if len({row["run_id"] for row in rows}) != len(rows):
        raise ValueError("frozen manifest run IDs are not unique")
    if [int(row["collection_order"]) for row in rows] != list(range(1, 361)):
        raise ValueError("frozen manifest collection_order is not exactly 1..360")
    if Counter(row["model_condition_id"] for row in rows) != Counter({model: 90 for model in MODELS}):
        raise ValueError("frozen manifest does not contain 90 rows per model")
    return rows


def read_preserved_observations(manifest_run_ids: set[str]) -> dict[str, str]:
    """Return preserved v2.6 run IDs mapped to their authoritative status."""
    observations: dict[str, str] = {}
    for metadata_path in sorted(RAW_ROOT.glob("API-v2.6-*/metadata.json")):
        try:
            metadata: dict[str, Any] = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError(f"cannot read preserved metadata {metadata_path}: {error}") from error
        run_id = metadata.get("run_id")
        status = metadata.get("collection_status")
        if not isinstance(run_id, str) or not isinstance(status, str):
            raise ValueError(f"preserved metadata is missing run_id or collection_status: {metadata_path}")
        if metadata_path.parent.name != run_id:
            raise ValueError(f"preserved metadata directory does not match run_id: {metadata_path}")
        if run_id not in manifest_run_ids:
            raise ValueError(f"preserved raw observation is absent from frozen manifest: {run_id}")
        if status not in ATTEMPTED_STATUSES:
            raise ValueError(f"preserved raw observation is not finalized: {run_id} ({status})")
        if run_id in observations:
            raise ValueError(f"duplicate preserved raw observation: {run_id}")
        observations[run_id] = status
    return observations


def make_assignment() -> list[dict[str, str]]:
    """Derive all interface assignments from frozen order and raw metadata only."""
    manifest_hash_before = sha256(MANIFEST)
    if manifest_hash_before != FROZEN_MANIFEST_SHA256:
        raise ValueError("frozen manifest SHA-256 differs from the v2.6 freeze record")
    manifest = read_manifest()
    observations = read_preserved_observations({row["run_id"] for row in manifest})
    attempted_by_model = Counter(
        row["model_condition_id"] for row in manifest if row["run_id"] in observations
    )
    if any(attempted_by_model[model] > API_TARGETS[model] for model in MODELS):
        raise ValueError("preserved API observations exceed a model API target")

    additional_api_ids: set[str] = set()
    for model in MODELS:
        remaining = API_TARGETS[model] - attempted_by_model[model]
        eligible = [
            row for row in manifest
            if row["model_condition_id"] == model and row["run_id"] not in observations
        ]
        if len(eligible) < remaining:
            raise ValueError(f"not enough never-attempted rows to fill {model} API quota")
        additional_api_ids.update(row["run_id"] for row in eligible[:remaining])

    output: list[dict[str, str]] = []
    for source in manifest:
        run_id = source["run_id"]
        if run_id in observations:
            interface = "api"
            attempted = "true"
            status = observations[run_id]
            reason = "preserved_existing_api_observation"
        elif run_id in additional_api_ids:
            interface = "api"
            attempted = "false"
            status = "pending"
            reason = "additional_api_quota_by_manifest_order"
        else:
            interface = "manual"
            attempted = "false"
            status = "pending"
            reason = "manual_after_api_quota"
        output.append({
            "collection_order": source["collection_order"],
            "run_id": run_id,
            "model_condition_id": source["model_condition_id"],
            "run_repetition": source["run_repetition"],
            "task_id": source["task_id"],
            "category": source["category"],
            "collection_interface": interface,
            "api_attempted_before_hybrid": attempted,
            "pre_hybrid_collection_status": status,
            "assignment_reason": reason,
        })
    manifest_hash_after = sha256(MANIFEST)
    if manifest_hash_after != manifest_hash_before:
        raise ValueError("frozen manifest changed while deriving the assignment")
    return output


def csv_bytes(rows: list[dict[str, str]]) -> bytes:
    from io import StringIO

    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=ASSIGNMENT_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def read_assignment() -> list[dict[str, str]]:
    with ASSIGNMENT.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != ASSIGNMENT_FIELDS:
            raise ValueError("hybrid assignment columns differ from the required schema")
        return list(reader)


def verify_assignment(rows: list[dict[str, str]]) -> dict[str, Any]:
    """Assert the full assignment contract and return reportable facts."""
    manifest_hash_before = sha256(MANIFEST)
    if manifest_hash_before != FROZEN_MANIFEST_SHA256:
        raise ValueError("frozen manifest SHA-256 differs from the v2.6 freeze record")
    manifest = read_manifest()
    expected_rows = make_assignment()
    if rows != expected_rows:
        raise ValueError("hybrid assignment does not exactly match deterministic derivation")
    if len(rows) != 360 or len({row["run_id"] for row in rows}) != 360:
        raise ValueError("hybrid assignment must contain exactly 360 unique run IDs")
    if [int(row["collection_order"]) for row in rows] != list(range(1, 361)):
        raise ValueError("hybrid assignment collection_order is not exactly 1..360")

    observations = read_preserved_observations({row["run_id"] for row in manifest})
    attempted_rows = [row for row in rows if row["api_attempted_before_hybrid"] == "true"]
    if len(attempted_rows) != len(observations):
        raise ValueError("assignment attempted-row count differs from preserved raw observations")
    if any(row["collection_interface"] != "api" for row in attempted_rows):
        raise ValueError("a preserved raw observation is assigned manual")
    if {row["run_id"] for row in attempted_rows} != set(observations):
        raise ValueError("assignment does not contain exactly the preserved raw observation set")

    interface_counts = Counter(row["collection_interface"] for row in rows)
    if interface_counts != Counter({"api": 180, "manual": 180}):
        raise ValueError(f"interface counts are incorrect: {dict(interface_counts)}")
    per_model: dict[str, dict[str, int]] = {}
    for model in MODELS:
        model_rows = [row for row in rows if row["model_condition_id"] == model]
        api_count = sum(row["collection_interface"] == "api" for row in model_rows)
        manual_count = sum(row["collection_interface"] == "manual" for row in model_rows)
        if api_count != API_TARGETS[model] or manual_count != MANUAL_TARGETS[model]:
            raise ValueError(f"{model} allocation is {api_count} API / {manual_count} manual")
        per_model[model] = {"api": api_count, "manual": manual_count}

    additional_rows = [row for row in rows if row["assignment_reason"] == "additional_api_quota_by_manifest_order"]
    if len(additional_rows) != 61:
        raise ValueError(f"additional API count is {len(additional_rows)}, expected 61")
    for model in MODELS:
        expected_eligible = [
            row for row in manifest
            if row["model_condition_id"] == model and row["run_id"] not in observations
        ]
        expected_ids = [
            row["run_id"] for row in expected_eligible[:API_TARGETS[model] - sum(
                source["model_condition_id"] == model for source in manifest if source["run_id"] in observations
            )]
        ]
        actual_ids = [
            row["run_id"] for row in additional_rows if row["model_condition_id"] == model
        ]
        if actual_ids != expected_ids:
            raise ValueError(f"{model} additional API rows are not earliest eligible manifest rows")
    if any(row["model_condition_id"] == "M4" for row in additional_rows):
        raise ValueError("M4 received an additional API assignment")

    manifest_hash_after = sha256(MANIFEST)
    if manifest_hash_after != manifest_hash_before:
        raise ValueError("frozen manifest changed during verification")
    return {
        "per_model": per_model,
        "attempted_count": len(observations),
        "additional_rows": additional_rows,
        "manual_rows": [row for row in rows if row["collection_interface"] == "manual"],
        "manifest_hash_before": manifest_hash_before,
        "manifest_hash_after": manifest_hash_after,
        "assignment_hash": sha256(ASSIGNMENT),
    }


def markdown_report(facts: dict[str, Any]) -> str:
    count_rows = "\n".join(
        f"| {model} | {API_TARGETS[model]} | {MANUAL_TARGETS[model]} | {facts['per_model'][model]['api']} | {facts['per_model'][model]['manual']} |"
        for model in MODELS
    )
    def numbered(rows: list[dict[str, str]]) -> str:
        return "\n".join(f"{row['collection_order']}. `{row['run_id']}` ({row['model_condition_id']})" for row in rows)
    m1 = [row for row in facts["additional_rows"] if row["model_condition_id"] == "M1"]
    m2 = [row for row in facts["additional_rows"] if row["model_condition_id"] == "M2"]
    m3 = [row for row in facts["additional_rows"] if row["model_condition_id"] == "M3"]
    return f"""# HYBRID Assignment Verification Report — v1.0.0

This is a derived allocation layer. It does not replace or modify the frozen v2.6 manifest, prompts, model configuration, generation settings, collection state, or raw observations.

## A. Exact assignment counts

| Model | API target | Manual target | Verified API | Verified manual |
| --- | ---: | ---: | ---: | ---: |
{count_rows}
| **Total** | **180** | **180** | **180** | **180** |

Preserved API-attempted rows: **{facts['attempted_count']}**. Additional API-assigned rows: **{len(facts['additional_rows'])}**. M4 additional API-assigned rows: **0**.

## B. Additional API-assigned rows ({len(facts['additional_rows'])})

{numbered(facts['additional_rows'])}

## C. Manual-assigned rows ({len(facts['manual_rows'])})

{numbered(facts['manual_rows'])}

## D. Additional M3 API rows (3)

{numbered(m3)}

## E. M4 allocation confirmation

M4 has 59 preserved API-attempted rows and receives zero additional API assignments. Its remaining 31 rows are manual-assigned.

## F. Frozen manifest SHA-256

- Before derivation: `{facts['manifest_hash_before']}`
- After verification: `{facts['manifest_hash_after']}`

## G. Hybrid assignment SHA-256

`{facts['assignment_hash']}`

## H. Verification results

- PASS: 360 unique run IDs and collection order 1 through 360.
- PASS: API/manual total is 180/180.
- PASS: M1 40/50, M2 40/50, M3 41/49, and M4 59/31 API/manual.
- PASS: all 119 preserved raw observations are API-assigned; none is manual-assigned.
- PASS: 61 additional API rows are the earliest eligible never-attempted rows by frozen manifest order.
- PASS: M1/M2/M3 additional counts are 24/34/3; M4 is 0.
- PASS: frozen manifest SHA-256 is unchanged.

## Per-model additional API lists

### M1 (24)

{numbered(m1)}

### M2 (34)

{numbered(m2)}

### M3 (3)

{numbered(m3)}
"""


def write_new(path: Path, content: bytes) -> None:
    if path.exists():
        raise ValueError(f"refusing to overwrite existing derived artifact: {path.relative_to(ROOT)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(content)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create or verify the v2.6 hybrid assignment")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true", help="write new derived assignment and report once")
    group.add_argument("--verify", action="store_true", help="verify existing derived assignment and report")
    args = parser.parse_args()
    try:
        if args.write:
            rows = make_assignment()
            write_new(ASSIGNMENT, csv_bytes(rows))
            facts = verify_assignment(read_assignment())
            write_new(REPORT, markdown_report(facts).encode("utf-8"))
            print("PASS: wrote deterministic hybrid assignment and verification report")
        else:
            facts = verify_assignment(read_assignment())
            expected_report = markdown_report(facts)
            if not REPORT.is_file() or REPORT.read_text(encoding="utf-8") != expected_report:
                raise ValueError("hybrid assignment report differs from deterministic verification output")
            print("PASS: verified hybrid assignment, report, quotas, preserved raw observations, order, and manifest hash")
    except (OSError, ValueError, csv.Error, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
