#!/usr/bin/env python3
"""PIPE-07: version-agnostic derived analysis-dataset builder.

Joins four already-produced, read-only derived inputs:

  --inventory            response inventory (build_response_inventory.py output;
                          one row per planned manifest run, including pending/
                          failed/truncated rows)
  --unique-packages      PIPE-03 unique normalized package-per-response records
                          (extract_package_references.py "package_json" output)
  --validation-joined    PIPE-04 joined registry-evidence records
                          (validate_npm_packages.py "joined_json" output)
  --classification-joined  PIPE-05 joined research-classification records
                          (classify_npm_packages.py "joined_json" output)

into two reusable derived datasets:

  A. package/response-level analysis dataset: one row per (run_id, normalized_package)
  B. response-level analysis dataset: one row per response in the inventory,
     including pending, failed, and truncated rows with zero package counts

Neither dataset calculates PHR, SHR, prevalence, or any risk score. This script
only counts and joins already-produced evidence; it never queries a registry,
executes generated code, or reads/writes a manifest, prompt, raw response, or
collection-state file.

All four input paths are explicit, required CLI arguments. There is no "latest
file" auto-discovery, so every run is fully auditable from its exact inputs.

Metric eligibility (frozen rule): a response, and every package row derived from
it, is `metric_eligible` only when its response-inventory `collection_status` is
exactly "completed". This excludes pending, requesting, truncated, failed, and
suspended rows from primary SHR/PHR eligibility, consistent with
docs/package_hallucination_taxonomy.md ("completed, non-truncated generations")
and docs/final_paper_notes.md's "Truncation precedence" note, which states that
this frozen exclusion rule supersedes the older docs/analysis_specification_v1.0.md
Sections 10/17 wording that truncated responses "may" be included in the primary
analysis. A completed, non-truncated response with zero package references still
receives a response-level row with metric_eligible=true and all counts at zero.

Failed observations (D035): a response the inventory marks failed -- including a
D035-corrected provider abnormal termination such as finish_reason "error" with
partial content -- keeps its response-level row (metric_eligible=false) but never
contributes package rows. PIPE-03 does not extract failed responses, so a package
row for a failed run means the PIPE-03/04/05 inputs were built from a different
(e.g. pre-D035) inventory; that mismatch is rejected rather than silently dropped.
The failed run's raw response.md is untouched and remains available for audit.
"""

import argparse
import csv
import hashlib
import io
import json
import os
import tempfile
from collections import defaultdict
from pathlib import Path

BUILDER_VERSION = "pipe-07-analysis-builder-1.1.0"
FORMAT_VERSION = "pipe-07-analysis-1.1.0"
PIPE05B_FORMAT_VERSION = "pipe-05b-adjudication-1.1.0"
PIPE05B_ADJUDICATION_VERSION = "pipe-05b-adjudicator-1.1.0"

INVENTORY_STATUS_VALUES = frozenset({
    "pending", "requesting", "completed", "truncated", "failed", "suspended",
})
PACKAGE_ROW_STATUS_VALUES = frozenset({"completed", "truncated"})
VALIDATION_STATUS_VALUES = frozenset({"exists", "not_found", "unresolved"})
CLASSIFICATION_VALUES = frozenset({
    "VALID", "CONFIRMED_HALLUCINATION", "LEGACY_OR_REMOVED", "AMBIGUOUS", "BUILTIN_OR_LOCAL",
})
ADJUDICATION_VALUES = frozenset({
    "AUTO_VALID", "REVIEW_REQUIRED", "REVIEWED", "VALIDATION_UNRESOLVED",
})

EXTRACTION_SHARED_FIELDS = (
    "collection_order", "model_condition_id", "task_id", "category",
    "first_occurrence_index", "occurrence_count", "source_types", "extractor_version",
)
INVENTORY_SHARED_FIELDS = ("collection_order", "model_condition_id", "task_id", "category")
RUNTIME_SHARED_FIELDS = ("collection_status", "completion_status", "truncated", "response_artifact_path")
REGISTRY_SHARED_FIELDS = (
    "validation_status", "registry", "request_url", "http_status",
    "checked_at", "validator_version", "evidence_summary", "error_type", "retry_count",
)

PACKAGE_ROW_FIELDS = (
    "run_id", "collection_order", "model_condition_id", "provider", "model",
    "task_id", "category", "repetition", "collection_status", "completion_status",
    "truncated", "normalized_package", "occurrence_count", "source_types",
    "validation_status", "research_classification", "adjudication_status",
    "primary_confirmed_hallucination", "primary_confirmation_path",
    "primary_confirmation_version", "primary_confirmation_source_hash",
    "pipe05b_adjudication_outcome",
    "metric_eligible", "provenance",
)
RESPONSE_ROW_FIELDS = (
    "run_id", "collection_order", "model_condition_id", "task_id", "category",
    "repetition", "collection_status", "completion_status", "truncated",
    "package_reference_count", "unique_package_count",
    "confirmed_hallucinated_package_count", "ambiguous_package_count",
    "unresolved_package_count", "contains_confirmed_package_hallucination",
    "metric_eligible",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    data = Path(path).read_bytes()
    return json.loads(data), hashlib.sha256(data).hexdigest()


def load_inventory(path):
    records, digest = read_json(path)
    require(isinstance(records, list), "--inventory must be a JSON array")
    by_run = {}
    for row in records:
        require(isinstance(row, dict), "Inventory rows must be objects")
        run_id = row.get("run_id")
        require(isinstance(run_id, str) and run_id, "Inventory row missing run_id")
        require(run_id not in by_run, f"Duplicate run_id in --inventory: {run_id}")
        require(row.get("collection_status") in INVENTORY_STATUS_VALUES,
                f"Unknown collection_status for {run_id}: {row.get('collection_status')!r}")
        by_run[run_id] = row
    return records, by_run, digest


def load_unique(path):
    records, digest = read_json(path)
    require(isinstance(records, list), "--unique-packages must be a JSON array")
    by_key = {}
    for row in records:
        require(isinstance(row, dict), "--unique-packages rows must be objects")
        key = (row.get("run_id"), row.get("normalized_package"))
        require(all(key), "--unique-packages row missing run_id or normalized_package")
        require(key not in by_key, f"Duplicate --unique-packages key: {key}")
        by_key[key] = row
    return records, by_key, digest


def load_envelope(path, expected_format_version, label):
    document, digest = read_json(path)
    require(isinstance(document, dict), f"{label} must be a JSON object envelope")
    require(document.get("format_version") == expected_format_version,
            f"{label} format_version mismatch: expected {expected_format_version!r}, "
            f"got {document.get('format_version')!r}")
    records = document.get("records")
    require(isinstance(records, list), f"{label} 'records' must be an array")
    return records, digest


def load_validation_joined(path):
    records, digest = load_envelope(path, "pipe-04-evidence-1.0.0", "--validation-joined")
    by_key = {}
    for row in records:
        require(isinstance(row, dict), "--validation-joined rows must be objects")
        key = (row.get("run_id"), row.get("normalized_package"))
        require(all(key), "--validation-joined row missing run_id or normalized_package")
        require(key not in by_key, f"Duplicate --validation-joined key: {key}")
        require(row.get("validation_status") in VALIDATION_STATUS_VALUES,
                f"Unknown validation_status for {key}: {row.get('validation_status')!r}")
        by_key[key] = row
    return records, by_key, digest


def load_classification_joined(path):
    records, digest = load_envelope(path, "pipe-05-classification-1.0.0", "--classification-joined")
    by_key = {}
    for row in records:
        require(isinstance(row, dict), "--classification-joined rows must be objects")
        key = (row.get("run_id"), row.get("normalized_package"))
        require(all(key), "--classification-joined row missing run_id or normalized_package")
        require(key not in by_key, f"Duplicate --classification-joined key: {key}")
        classification = row.get("classification")
        require(classification is None or classification in CLASSIFICATION_VALUES,
                f"Unsupported research_classification for {key}: {classification!r}")
        require(row.get("adjudication_status") in ADJUDICATION_VALUES,
                f"Unknown adjudication_status for {key}: {row.get('adjudication_status')!r}")
        by_key[key] = row
    return records, by_key, digest


def _is_utc(value):
    from datetime import datetime, timezone
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).utcoffset() == timezone.utc.utcoffset(None)
    except ValueError:
        return False


def load_pipe05b(path, classification_hash):
    """Load and conservatively validate an explicitly supplied PIPE-05B envelope."""
    document, digest = read_json(path)
    require(isinstance(document, dict), "--pipe05b-adjudication must be a JSON object envelope")
    require(document.get("format_version") == PIPE05B_FORMAT_VERSION,
            "Unsupported PIPE-05B format_version")
    require(document.get("adjudication_version") == PIPE05B_ADJUDICATION_VERSION,
            "Unsupported PIPE-05B adjudication_version")
    require(document.get("source_input_hash") == classification_hash,
            "PIPE-05B source_input_hash disagrees with PIPE-07 classification source hash")
    records = document.get("records")
    require(isinstance(records, list), "PIPE-05B records must be an array")
    by_key = {}
    required_checks = {"historical": "no_prior_evidence", "normalization": "external_npm_reference",
                       "ambiguity": "cleared", "namespace": "cleared", "ecosystem": "cleared",
                       "types_package": "cleared"}
    for row in records:
        require(isinstance(row, dict), "PIPE-05B record must be an object")
        key = (row.get("run_id"), row.get("normalized_package"))
        require(all(isinstance(v, str) and v for v in key), "PIPE-05B record missing run_id/normalized_package")
        require(key not in by_key, f"Duplicate PIPE-05B key: {key}")
        require(row.get("adjudication_version") == PIPE05B_ADJUDICATION_VERSION,
                f"Unsupported PIPE-05B record adjudication_version for {key}")
        outcome = row.get("adjudication_outcome")
        require(outcome in {"CONFIRMED_HALLUCINATION", "LEGACY_OR_REMOVED", "NAMESPACE_CONFUSION",
                            "PACKAGE_NAME_CONFUSION", "INVALID_OR_REDUNDANT_TYPES_PACKAGE",
                            "ECOSYSTEM_CONFUSION", "OTHER_DEPENDENCY_ERROR",
                            "SELF_REFERENCE_OR_LOCAL_PACKAGE", "UNRESOLVED"},
                f"Unsupported PIPE-05B adjudication outcome for {key}")
        require(row.get("confirmed_package_hallucination") is (outcome == "CONFIRMED_HALLUCINATION"),
                f"PIPE-05B confirmed_package_hallucination/outcome disagreement for {key}")
        if outcome == "CONFIRMED_HALLUCINATION":
            require(row.get("confirmed_package_hallucination") is True and
                    row.get("dependency_failure") is True and
                    row.get("external_dependency_eligible") is True and
                    row.get("evidence_status") == "resolved" and
                    row.get("checks") == required_checks and
                    isinstance(row.get("evidence_sources"), list) and row["evidence_sources"] and
                    all(isinstance(x, dict) and isinstance(x.get("source"), str) and x["source"].strip() and
                        isinstance(x.get("summary"), str) and x["summary"].strip() and _is_utc(x.get("checked_at"))
                        for x in row["evidence_sources"]) and _is_utc(row.get("reviewed_at")),
                    f"PIPE-05B confirmation guard violated for {key}")
        by_key[key] = row
    return by_key, digest


def cross_validate(inventory_by_run, unique_by_key, validation_by_key, classification_by_key):
    require(set(validation_by_key) == set(unique_by_key),
            "--validation-joined and --unique-packages key sets differ")
    require(set(classification_by_key) == set(unique_by_key),
            "--classification-joined and --unique-packages key sets differ")
    for key, unique_row in unique_by_key.items():
        run_id, _normalized_package = key
        require(run_id in inventory_by_run,
                f"--unique-packages references a run_id absent from --inventory: {run_id}")
        inventory_row = inventory_by_run[run_id]
        require(inventory_row["collection_status"] in PACKAGE_ROW_STATUS_VALUES,
                f"A package row exists for {run_id}, whose inventory collection_status is "
                f"{inventory_row['collection_status']!r}; only completed/truncated responses can "
                "have extracted package references (rebuild PIPE-03/04/05 from this inventory; "
                "failed responses, including D035 corrections, are not extracted)")
        for field in INVENTORY_SHARED_FIELDS:
            require(unique_row.get(field) == inventory_row.get(field),
                    f"Inventory/--unique-packages metadata conflict at {key} field {field!r}: "
                    f"{inventory_row.get(field)!r} != {unique_row.get(field)!r}")

        validation_row = validation_by_key[key]
        for field in EXTRACTION_SHARED_FIELDS:
            require(validation_row.get(field) == unique_row.get(field),
                    f"--validation-joined/--unique-packages conflict at {key} field {field!r}")
        for field in RUNTIME_SHARED_FIELDS:
            require(validation_row.get(field) == inventory_row.get(field),
                    f"--validation-joined/--inventory conflict at {key} field {field!r}")

        classification_row = classification_by_key[key]
        for field in EXTRACTION_SHARED_FIELDS + RUNTIME_SHARED_FIELDS + REGISTRY_SHARED_FIELDS:
            require(classification_row.get(field) == validation_row.get(field),
                    f"--classification-joined/--validation-joined conflict at {key} field {field!r}")


def build_package_rows(inventory_by_run, unique_by_key, classification_by_key, pipe05b_by_key, pipe05b_hash,
                       classification_hash):
    rows = []
    for key in sorted(unique_by_key):
        run_id, normalized_package = key
        inventory_row = inventory_by_run[run_id]
        unique_row = unique_by_key[key]
        classification_row = classification_by_key[key]
        metric_eligible = inventory_row["collection_status"] == "completed"
        reviewed_path = (classification_row["adjudication_status"] == "REVIEWED" and
                         classification_row["classification"] == "CONFIRMED_HALLUCINATION")
        adjudication = pipe05b_by_key.get(key)
        pipe05b_path = adjudication is not None and adjudication["adjudication_outcome"] == "CONFIRMED_HALLUCINATION"
        # Check exclusivity before the source-shape assertion so a deliberately
        # malformed dual confirmation has a deterministic, specific failure.
        require(not (reviewed_path and adjudication is not None),
                f"Key appears on both PIPE05_REVIEWED and PIPE05B paths: {key}")
        if adjudication is not None:
            require(adjudication.get("source_truncated") == inventory_row["truncated"],
                    f"PIPE-05B source_truncated disagrees with PIPE-07 for {key}")
            require(classification_row["adjudication_status"] == "REVIEW_REQUIRED" and
                    classification_row["classification"] == "AMBIGUOUS",
                    f"PIPE-05B source row is not REVIEW_REQUIRED / AMBIGUOUS for {key}")
        primary_path = "PIPE05_REVIEWED" if reviewed_path else "PIPE05B" if pipe05b_path else "NONE"
        provenance = [
            f"pipe-03:extractor_version={unique_row['extractor_version']}",
            f"pipe-04:validator_version={classification_row['validator_version']};"
            f"checked_at={classification_row['checked_at']}",
            f"pipe-05:classifier_version={classification_row['classifier_version']};"
            f"adjudication_status={classification_row['adjudication_status']}",
            f"response_artifact_path={inventory_row['response_artifact_path']}",
        ]
        rows.append({
            "run_id": run_id,
            "collection_order": inventory_row["collection_order"],
            "model_condition_id": inventory_row["model_condition_id"],
            "provider": inventory_row["provider"],
            "model": inventory_row["model"],
            "task_id": inventory_row["task_id"],
            "category": inventory_row["category"],
            "repetition": inventory_row["replicate"],
            "collection_status": inventory_row["collection_status"],
            "completion_status": inventory_row["completion_status"],
            "truncated": inventory_row["truncated"],
            "normalized_package": normalized_package,
            "occurrence_count": unique_row["occurrence_count"],
            "source_types": list(unique_row["source_types"]),
            "validation_status": classification_row["validation_status"],
            "research_classification": classification_row["classification"],
            "adjudication_status": classification_row["adjudication_status"],
            "primary_confirmed_hallucination": primary_path != "NONE",
            "primary_confirmation_path": primary_path,
            "primary_confirmation_version": (classification_row["classifier_version"] if reviewed_path else
                                              adjudication["adjudication_version"] if pipe05b_path else None),
            "primary_confirmation_source_hash": (None if primary_path == "NONE" else
                                                  pipe05b_hash if pipe05b_path else classification_hash),
            "pipe05b_adjudication_outcome": None if adjudication is None else adjudication["adjudication_outcome"],
            "metric_eligible": metric_eligible,
            "provenance": provenance,
        })
    return sorted(rows, key=lambda row: (row["collection_order"], row["run_id"], row["normalized_package"]))


def build_response_rows(inventory_records, package_rows):
    packages_by_run = defaultdict(list)
    for row in package_rows:
        packages_by_run[row["run_id"]].append(row)

    response_rows = []
    for inventory_row in inventory_records:
        run_id = inventory_row["run_id"]
        packages = packages_by_run.get(run_id, [])
        package_reference_count = sum(row["occurrence_count"] for row in packages)
        unique_package_count = len(packages)
        confirmed = sum(1 for row in packages if row["primary_confirmed_hallucination"])
        ambiguous = sum(1 for row in packages if row["research_classification"] == "AMBIGUOUS")
        unresolved = sum(1 for row in packages if row["validation_status"] == "unresolved")

        require(unique_package_count <= package_reference_count,
                f"Impossible counts for {run_id}: unique_package_count "
                f"({unique_package_count}) exceeds package_reference_count ({package_reference_count})")
        require(confirmed <= unique_package_count and ambiguous <= unique_package_count
                and unresolved <= unique_package_count,
                f"Impossible counts for {run_id}: a classification subtotal exceeds unique_package_count")

        metric_eligible = inventory_row["collection_status"] == "completed"
        response_rows.append({
            "run_id": run_id,
            "collection_order": inventory_row["collection_order"],
            "model_condition_id": inventory_row["model_condition_id"],
            "task_id": inventory_row["task_id"],
            "category": inventory_row["category"],
            "repetition": inventory_row["replicate"],
            "collection_status": inventory_row["collection_status"],
            "completion_status": inventory_row["completion_status"],
            "truncated": inventory_row["truncated"],
            "package_reference_count": package_reference_count,
            "unique_package_count": unique_package_count,
            "confirmed_hallucinated_package_count": confirmed,
            "ambiguous_package_count": ambiguous,
            "unresolved_package_count": unresolved,
            "contains_confirmed_package_hallucination": confirmed > 0,
            "metric_eligible": metric_eligible,
        })
    return sorted(response_rows, key=lambda row: (row["collection_order"], row["run_id"]))


def build_datasets(inventory_path, unique_path, validation_joined_path, classification_joined_path,
                   pipe05b_adjudication_path=None, no_pipe05b_adjudication=None):
    if no_pipe05b_adjudication is None:
        # Library callers remain usable; CLI callers must make the declaration explicitly.
        no_pipe05b_adjudication = pipe05b_adjudication_path is None
    require((pipe05b_adjudication_path is not None) != no_pipe05b_adjudication,
            "Specify exactly one of --pipe05b-adjudication or --no-pipe05b-adjudication")
    inventory_records, inventory_by_run, inventory_hash = load_inventory(inventory_path)
    _unique_records, unique_by_key, unique_hash = load_unique(unique_path)
    _validation_records, validation_by_key, validation_hash = load_validation_joined(validation_joined_path)
    _classification_records, classification_by_key, classification_hash = \
        load_classification_joined(classification_joined_path)

    pipe05b_by_key, pipe05b_hash = ({}, None) if no_pipe05b_adjudication else load_pipe05b(
        pipe05b_adjudication_path, classification_hash)
    require(set(pipe05b_by_key) <= set(classification_by_key),
            "PIPE-05B key has no PIPE-07 row")
    cross_validate(inventory_by_run, unique_by_key, validation_by_key, classification_by_key)

    package_rows = build_package_rows(inventory_by_run, unique_by_key, classification_by_key,
                                      pipe05b_by_key, pipe05b_hash, classification_hash)
    response_rows = build_response_rows(inventory_records, package_rows)

    hashes = {
        "inventory_input_hash": inventory_hash,
        "unique_packages_input_hash": unique_hash,
        "validation_joined_input_hash": validation_hash,
        "classification_joined_input_hash": classification_hash,
        "pipe05b_adjudication_input_status": "not_supplied" if no_pipe05b_adjudication else "supplied",
        "pipe05b_adjudication_input_hash": pipe05b_hash,
    }
    return package_rows, response_rows, hashes


def csv_bytes(records, fields):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for record in records:
        writer.writerow({
            field: json.dumps(record[field], separators=(",", ":"), ensure_ascii=False)
            if isinstance(record[field], (list, dict)) else record[field]
            for field in fields
        })
    return stream.getvalue().encode("utf-8")


def atomic_write_new_or_identical(path, data):
    if path.exists():
        require(path.read_bytes() == data,
                f"Existing PIPE-07 output differs; preserve it and choose a new output directory: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        os.unlink(temporary)


def write_outputs(output_dir, package_rows, response_rows, hashes, version_label):
    base = Path(output_dir)
    paths = {
        "package_json": base / f"package_response_analysis_{version_label}.json",
        "package_csv": base / f"package_response_analysis_{version_label}.csv",
        "response_json": base / f"response_level_analysis_{version_label}.json",
        "response_csv": base / f"response_level_analysis_{version_label}.csv",
    }

    def envelope(records):
        return {"format_version": FORMAT_VERSION, "builder_version": BUILDER_VERSION,
                **hashes, "records": records}

    files = {
        "package_json": (json.dumps(envelope(package_rows), indent=2, ensure_ascii=False) + "\n").encode("utf-8"),
        "package_csv": csv_bytes(package_rows, PACKAGE_ROW_FIELDS),
        "response_json": (json.dumps(envelope(response_rows), indent=2, ensure_ascii=False) + "\n").encode("utf-8"),
        "response_csv": csv_bytes(response_rows, RESPONSE_ROW_FIELDS),
    }
    for key, path in paths.items():
        atomic_write_new_or_identical(path, files[key])
    return paths


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--inventory", required=True,
                         help="Path to a response-inventory JSON array (build_response_inventory.py output)")
    parser.add_argument("--unique-packages", required=True,
                         help="Path to a PIPE-03 unique-package-per-response JSON array")
    parser.add_argument("--validation-joined", required=True,
                         help="Path to a PIPE-04 joined registry-evidence JSON envelope")
    parser.add_argument("--classification-joined", required=True,
                         help="Path to a PIPE-05 joined research-classification JSON envelope")
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--pipe05b-adjudication", help="Explicit PIPE-05B adjudication envelope; never auto-discovered")
    choice.add_argument("--no-pipe05b-adjudication", action="store_true",
                        help="Explicitly declare that no PIPE-05B adjudication envelope is supplied")
    parser.add_argument("--output-dir", required=True,
                         help="Directory to write the two derived datasets into")
    parser.add_argument("--version-label", required=True,
                         help="Explicit dataset-version suffix for output filenames "
                              "(e.g. v2.2.0-interim); never inferred automatically")
    args = parser.parse_args(argv)

    package_rows, response_rows, hashes = build_datasets(
        args.inventory, args.unique_packages, args.validation_joined, args.classification_joined,
        args.pipe05b_adjudication, args.no_pipe05b_adjudication)
    paths = write_outputs(args.output_dir, package_rows, response_rows, hashes, args.version_label)

    eligible_responses = sum(row["metric_eligible"] for row in response_rows)
    print(f"Wrote {len(package_rows)} package-level row(s) to {paths['package_json']} and "
          f"{len(response_rows)} response-level row(s) to {paths['response_json']} "
          f"({eligible_responses} metric-eligible responses). No PHR/SHR/prevalence was calculated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
