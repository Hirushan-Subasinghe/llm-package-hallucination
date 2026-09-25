#!/usr/bin/env python3
"""PIPE-05: deterministic package-name classification from frozen derived evidence.

No network requests, generated-code execution, package installation, or metrics.
Optional adjudications are researcher-supplied evidence, never inferred from 404s.
"""

import argparse
import csv
import hashlib
import io
import json
import os
import tempfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

VERSION = "pipe-05-classifier-1.0.0"
FORMAT_VERSION = "pipe-05-classification-1.0.0"
FINAL_CLASSES = {"VALID", "CONFIRMED_HALLUCINATION", "LEGACY_OR_REMOVED",
                 "AMBIGUOUS", "BUILTIN_OR_LOCAL"}
REVIEW_CLASSES = FINAL_CLASSES - {"VALID"}
PACKAGE_FIELDS = (
    "normalized_package", "validation_status", "registry_evidence",
    "classification", "classification_basis", "adjudication_status",
    "review_required", "reviewer_id", "reviewed_at", "review_notes",
    "review_evidence", "review_checks", "run_ids", "occurrence_evidence", "classifier_version",
)
JOIN_EXTRA_FIELDS = (
    "classification", "classification_basis", "adjudication_status",
    "review_required", "reviewer_id", "reviewed_at", "review_notes",
    "review_evidence", "review_checks", "occurrence_evidence", "classifier_version",
)
OCCURRENCE_FIELDS = (
    "run_id", "occurrence_index", "original_reference", "normalized_package",
    "source_type", "source_text", "source_offset", "version_specifier",
    "response_artifact_path", "truncated",
)
REGISTRY_FIELDS = (
    "validation_status", "registry", "request_url", "http_status",
    "checked_at", "validator_version", "evidence_summary", "error_type",
    "retry_count",
)


def read_json(path):
    data = Path(path).read_bytes()
    return json.loads(data), hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def is_utc(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.utcoffset() == timezone.utc.utcoffset(parsed)
    except ValueError:
        return False


def validated_inputs(unique_path, occurrence_path, validation_path, joined_path):
    unique, unique_hash = read_json(unique_path)
    occurrences, occurrence_hash = read_json(occurrence_path)
    validation, validation_hash = read_json(validation_path)
    joined, joined_hash = read_json(joined_path)
    require(isinstance(unique, list) and isinstance(occurrences, list), "PIPE-03 inputs must be arrays")
    require(isinstance(validation, dict) and isinstance(joined, dict), "PIPE-04 inputs must be envelopes")
    require(validation.get("format_version") == joined.get("format_version") == "pipe-04-evidence-1.0.0",
            "PIPE-04 format mismatch")
    require(validation.get("source_input_hash") == joined.get("source_input_hash") == unique_hash,
            "PIPE-04 unique-input hash mismatch")
    require(validation.get("source_occurrences_hash") == joined.get("source_occurrences_hash") == occurrence_hash,
            "PIPE-04 occurrence-input hash mismatch")
    packages = validation.get("records")
    joined_rows = joined.get("records")
    require(isinstance(packages, list) and isinstance(joined_rows, list), "PIPE-04 records must be arrays")
    package_by_name = {}
    for record in packages:
        name = record["normalized_package"]
        require(isinstance(name, str) and name and name not in package_by_name,
                "Duplicate or empty package-level validation name")
        require(record["source_input_hash"] == unique_hash and
                record["source_occurrences_hash"] == occurrence_hash, "Package-level provenance mismatch")
        require(record["registry"] == "https://registry.npmjs.org" and
                record["request_url"] == "https://registry.npmjs.org/" + quote(name, safe=""),
                "Registry endpoint/name mismatch")
        require(record["validator_version"] == "pipe-04-npm-validator-1.0.0",
                "Unexpected registry validator version")
        require(is_utc(record["checked_at"]), "Registry timestamp must be UTC")
        state = record["validation_status"]
        require(state in {"exists", "not_found", "unresolved"}, "Unknown registry state")
        if state == "exists":
            require(record["http_status"] == 200 and record["error_type"] is None and
                    record["evidence_summary"] == "Registry metadata returned the exact package name",
                    "Malformed exists evidence")
        elif state == "not_found":
            require(record["http_status"] == 404 and record["error_type"] is None and
                    record["evidence_summary"] == "Official registry returned package-not-found JSON",
                    "Malformed not_found evidence")
        else:
            require(bool(record["error_type"]) and bool(record["evidence_summary"]),
                    "Unresolved registry evidence lacks a reason")
        package_by_name[name] = record
    require(len(package_by_name) == len(packages), "Duplicate package validation")
    unique_by_key = {}
    for row in unique:
        key = (row["run_id"], row["normalized_package"])
        require(key not in unique_by_key, "Duplicate response-package key")
        unique_by_key[key] = row
    joined_by_key = {}
    for row in joined_rows:
        key = (row["run_id"], row["normalized_package"])
        require(key not in joined_by_key and key in unique_by_key, "Duplicate or unexpected joined key")
        require(row["normalized_package"] in package_by_name, "Joined name lacks package validation")
        package = package_by_name[row["normalized_package"]]
        for field in REGISTRY_FIELDS:
            require(row[field] == package[field], f"Joined registry mismatch: {key} {field}")
        for field in ("collection_order", "model_condition_id", "task_id", "category",
                      "first_occurrence_index", "occurrence_count", "source_types", "extractor_version"):
            require(row[field] == unique_by_key[key][field], f"Joined extraction mismatch: {key} {field}")
        joined_by_key[key] = row
    require(set(joined_by_key) == set(unique_by_key), "Joined response-package coverage mismatch")
    require(set(package_by_name) == {key[1] for key in unique_by_key}, "Package validation coverage mismatch")
    occurrence_by_key = defaultdict(list)
    for occurrence in occurrences:
        key = (occurrence["run_id"], occurrence["normalized_package"])
        require(key in unique_by_key, "Occurrence lacks unique response-package row")
        occurrence_by_key[key].append(occurrence)
    require(set(occurrence_by_key) == set(unique_by_key), "Occurrence coverage mismatch")
    for key, items in occurrence_by_key.items():
        row = unique_by_key[key]
        joined_row = joined_by_key[key]
        require(len(items) == row["occurrence_count"], f"Occurrence count mismatch: {key}")
        require(min(item["occurrence_index"] for item in items) == row["first_occurrence_index"],
                f"First occurrence mismatch: {key}")
        require(len({item["occurrence_index"] for item in items}) == len(items),
                f"Duplicate occurrence index: {key}")
        require(set(item["source_type"] for item in items) == set(row["source_types"]),
                f"Source type mismatch: {key}")
        for item in items:
            for field in ("collection_order", "model_condition_id", "task_id", "category"):
                require(item[field] == row[field], f"Occurrence metadata mismatch: {key} {field}")
            for field in ("collection_status", "completion_status", "truncated", "response_artifact_path"):
                require(item[field] == joined_row[field], f"Occurrence provenance mismatch: {key} {field}")
    hashes = {
        "unique_input_hash": unique_hash, "occurrences_input_hash": occurrence_hash,
        "validation_input_hash": validation_hash, "validation_joined_input_hash": joined_hash,
    }
    return unique, occurrences, packages, joined_rows, occurrence_by_key, hashes


def load_adjudications(path, package_by_name):
    if path is None:
        return {}, None
    data, digest = read_json(path)
    require(isinstance(data, list), "Adjudication input must be an array")
    reviews = {}
    for item in data:
        require(isinstance(item, dict), "Adjudication entries must be objects")
        name = item.get("normalized_package")
        require(name in package_by_name and name not in reviews, "Unknown or duplicate adjudication package")
        require(package_by_name[name]["validation_status"] == "not_found",
                "Adjudication input is only for not_found packages")
        label = item.get("classification")
        require(label in REVIEW_CLASSES, "Invalid or unsupported reviewed classification")
        require(isinstance(item.get("reviewer_id"), str) and item["reviewer_id"].strip(),
                "Reviewer identifier required")
        require(is_utc(item.get("reviewed_at")), "UTC review timestamp required")
        require(isinstance(item.get("rationale"), str) and item["rationale"].strip(),
                "Review rationale required")
        evidence = item.get("evidence")
        require(isinstance(evidence, list) and evidence and all(
            isinstance(entry, dict) and isinstance(entry.get("source"), str) and entry["source"].strip()
            and isinstance(entry.get("summary"), str) and entry["summary"].strip()
            and is_utc(entry.get("checked_at")) for entry in evidence),
            "Dated review evidence required")
        checks = item.get("checks")
        require(isinstance(checks, dict), "Historical, normalization, and ambiguity checks required")
        require(set(checks) == {"historical", "normalization", "ambiguity"},
                "Review checks must contain exactly the three documented checks")
        require(checks.get("historical") in {"no_prior_evidence", "prior_or_removed", "inconclusive"},
                "Invalid historical check")
        require(checks.get("normalization") in {"external_npm_reference", "builtin_or_local", "inconclusive"},
                "Invalid normalization check")
        require(checks.get("ambiguity") in {"cleared", "inconclusive"}, "Invalid ambiguity check")
        if label == "CONFIRMED_HALLUCINATION":
            require(checks == {"historical": "no_prior_evidence", "normalization": "external_npm_reference",
                               "ambiguity": "cleared"}, "Confirmed hallucination requires all conservative checks")
        elif label == "LEGACY_OR_REMOVED":
            require(checks["historical"] == "prior_or_removed" and
                    checks["normalization"] == "external_npm_reference", "Legacy classification requires prior-existence evidence")
        elif label == "BUILTIN_OR_LOCAL":
            require(checks["normalization"] == "builtin_or_local", "Builtin/local classification requires normalization review")
        reviews[name] = item
    return reviews, digest


def classify_package(registry_record, review=None):
    state = registry_record["validation_status"]
    if state == "exists":
        label, basis, adjudication, needs_review = (
            "VALID", "Official npm metadata returned the exact normalized package name",
            "AUTO_VALID", False)
    elif state == "unresolved":
        label, basis, adjudication, needs_review = (
            None, "Operational registry evidence is unresolved; no research classification assigned",
            "VALIDATION_UNRESOLVED", False)
    elif review is None:
        label, basis, adjudication, needs_review = (
            "AMBIGUOUS", "Clean npm 404 is insufficient without historical, normalization, and ambiguity review",
            "REVIEW_REQUIRED", True)
    else:
        label, basis, adjudication, needs_review = (
            review["classification"], "Dated human adjudication with historical, normalization, and ambiguity checks",
            "REVIEWED", False)
    require(label is None or label in FINAL_CLASSES, "Invalid research classification")
    return {
        "classification": label, "classification_basis": basis,
        "adjudication_status": adjudication, "review_required": needs_review,
        "reviewer_id": review["reviewer_id"] if review else None,
        "reviewed_at": review["reviewed_at"] if review else None,
        "review_notes": review["rationale"] if review else None,
        "review_evidence": review["evidence"] if review else [],
        "review_checks": review["checks"] if review else None,
        "classifier_version": VERSION,
    }


def build_records(unique, occurrences, packages, joined, by_key, reviews):
    joined_by_key = {(row["run_id"], row["normalized_package"]): row for row in joined}
    package_by_name = {row["normalized_package"]: row for row in packages}
    names = sorted(package_by_name)
    decisions = {name: classify_package(package_by_name[name], reviews.get(name)) for name in names}
    occurrence_evidence_by_key = {}
    for key, items in by_key.items():
        occurrence_evidence_by_key[key] = [
            {field: item[field] for field in OCCURRENCE_FIELDS}
            for item in sorted(items, key=lambda record: record["occurrence_index"])]
    package_rows = []
    for name in names:
        source = package_by_name[name]
        response_keys = sorted((key for key in by_key if key[1] == name),
                               key=lambda key: (joined_by_key[key]["collection_order"],
                                                joined_by_key[key]["first_occurrence_index"], key[0]))
        package_rows.append({
            "normalized_package": name,
            "validation_status": source["validation_status"],
            "registry_evidence": {field: source[field] for field in REGISTRY_FIELDS},
            **decisions[name],
            "run_ids": [key[0] for key in response_keys],
            "occurrence_evidence": [item for key in response_keys for item in occurrence_evidence_by_key[key]],
        })
    joined_rows = []
    for source in sorted(joined, key=lambda row: (row["collection_order"], row["first_occurrence_index"],
                                                  row["normalized_package"], row["run_id"])):
        key = (source["run_id"], source["normalized_package"])
        joined_rows.append({**source, **decisions[source["normalized_package"]],
                            "occurrence_evidence": occurrence_evidence_by_key[key]})
    return package_rows, joined_rows


def output_paths(output_dir):
    base = Path(output_dir)
    return {
        "package_json": base / "package_classification_v2.2.0.json",
        "package_csv": base / "package_classification_v2.2.0.csv",
        "joined_json": base / "package_classification_joined_v2.2.0.json",
        "joined_csv": base / "package_classification_joined_v2.2.0.csv",
    }


def csv_bytes(records, fields):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for record in records:
        writer.writerow({field: json.dumps(record[field], separators=(",", ":"), ensure_ascii=False)
                         if isinstance(record[field], (list, dict)) else record[field] for field in fields})
    return stream.getvalue().encode("utf-8")


def atomic_write_new_or_identical(path, data):
    if path.exists():
        require(path.read_bytes() == data, f"Existing PIPE-05 output differs; preserve it and choose a new output directory: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        # Atomic, exclusive creation: never replace a concurrent or prior output.
        os.link(temporary, path)
    finally:
        os.unlink(temporary)


def write_outputs(paths, package_rows, joined_rows, hashes, review_hash):
    def envelope(records):
        return {"format_version": FORMAT_VERSION, **hashes,
                "adjudication_input_hash": review_hash, "records": records}
    files = {
        "package_json": (json.dumps(envelope(package_rows), indent=2, ensure_ascii=False) + "\n").encode("utf-8"),
        "package_csv": csv_bytes(package_rows, PACKAGE_FIELDS),
        "joined_json": (json.dumps(envelope(joined_rows), indent=2, ensure_ascii=False) + "\n").encode("utf-8"),
        "joined_csv": csv_bytes(joined_rows, tuple(joined_rows[0]) if joined_rows else JOIN_EXTRA_FIELDS),
    }
    for key, path in paths.items():
        if path.exists():
            require(path.read_bytes() == files[key], f"Existing PIPE-05 output differs: {path}")
    for key, path in paths.items():
        atomic_write_new_or_identical(path, files[key])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unique", default="results/package_reference_unique_v2.2.0.json")
    parser.add_argument("--occurrences", default="results/package_reference_occurrences_v2.2.0.json")
    parser.add_argument("--validation", default="results/npm_package_validation_v2.2.0.json")
    parser.add_argument("--validation-joined", default="results/npm_package_validation_joined_v2.2.0.json")
    parser.add_argument("--adjudications", help="Optional researcher-supplied dated JSON review decisions")
    parser.add_argument("--output-dir", default="results")
    args = parser.parse_args(argv)
    unique, occurrences, packages, joined, by_key, hashes = validated_inputs(
        args.unique, args.occurrences, args.validation, args.validation_joined)
    reviews, review_hash = load_adjudications(
        args.adjudications, {row["normalized_package"]: row for row in packages})
    package_rows, joined_rows = build_records(unique, occurrences, packages, joined, by_key, reviews)
    write_outputs(output_paths(args.output_dir), package_rows, joined_rows, hashes, review_hash)
    print(f"Wrote {len(package_rows)} package classifications and {len(joined_rows)} response-package rows; "
          f"{sum(row['review_required'] for row in package_rows)} package(s) require adjudication.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
