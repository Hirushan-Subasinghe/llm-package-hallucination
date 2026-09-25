#!/usr/bin/env python3
"""PIPE-05B: conservative, evidence-based secondary adjudication for REVIEW_REQUIRED
npm package references.

This tool never changes the frozen primary PIPE-05 package-name-hallucination
classification. It reads an existing PIPE-05 joined classification envelope
read-only, adjudicates only rows already marked `adjudication_status ==
"REVIEW_REQUIRED"` (`classification == "AMBIGUOUS"`), and writes a wholly
separate, versioned PIPE-05B output. It never writes to a PIPE-05 file, never
recomputes PHR/SHR, and never promotes an uncertain case merely because
evidence is thin -- `UNRESOLVED` is always available and never becomes a
failure automatically.

Each adjudication decision distinguishes two independent judgments:

- `confirmed_package_hallucination` -- true only for `adjudication_outcome ==
  "CONFIRMED_HALLUCINATION"`, i.e. a conservative confirmed package-name
  hallucination under this secondary review. This is evidence for a possible
  a guarded confirmation may be routed by PIPE-07 into primary PHR/SHR under
  D037; PIPE-05 itself is never rewritten.
- `dependency_failure` -- whether the named dependency would fail to resolve
  as declared, independent of whether it is a confirmed hallucination
  (e.g. `LEGACY_OR_REMOVED`, `NAMESPACE_CONFUSION`, or `OTHER_DEPENDENCY_ERROR`
  can all be a dependency failure without being a hallucination).
- `external_dependency_eligible` -- whether the reference is an external npm
  dependency claim at all. `SELF_REFERENCE_OR_LOCAL_PACKAGE` (PIPE-05B.1) marks a
  reference to the generated project itself (its own package.json `name`) or to
  a local/workspace package the same response declares; a registry 404 for such
  a name is not evidence of an invalid external dependency. Those records carry
  `external_dependency_eligible=false`, `dependency_failure=false`, and
  `confirmed_package_hallucination=false`, and must be excluded from both the
  numerator and the denominator of any secondary external-dependency failure
  metric. `UNRESOLVED` records carry `external_dependency_eligible=null`
  (undetermined); every other outcome carries `true`.

No network requests, package installation, or generated-code execution. This
script only adjudicates researcher-supplied evidence on disk; it performs no
live registry queries and no experimental data collection.
"""

import argparse
import csv
import hashlib
import io
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

TOOL_VERSION = "pipe-05b-adjudicator-1.1.0"
FORMAT_VERSION = "pipe-05b-adjudication-1.1.0"
SOURCE_FORMAT_VERSION = "pipe-05-classification-1.0.0"

# "Strong" outcomes assert a specific, evidence-backed dependency-reliability
# explanation and therefore require the fullest evidence bar. "Weak" outcomes
# (OTHER_DEPENDENCY_ERROR, UNRESOLVED) are deliberately lower-bar catch-alls so
# that thin evidence never gets pushed into a specific strong category.
STRONG_OUTCOMES = frozenset({
    "CONFIRMED_HALLUCINATION",
    "LEGACY_OR_REMOVED",
    "NAMESPACE_CONFUSION",
    "PACKAGE_NAME_CONFUSION",
    "INVALID_OR_REDUNDANT_TYPES_PACKAGE",
    "ECOSYSTEM_CONFUSION",
})
WEAK_OUTCOMES = frozenset({"OTHER_DEPENDENCY_ERROR", "UNRESOLVED"})
# Non-dependency outcomes (PIPE-05B.1): the reference is not an external npm
# dependency claim, so it is neither a dependency failure nor a hallucination.
NON_DEPENDENCY_OUTCOMES = frozenset({"SELF_REFERENCE_OR_LOCAL_PACKAGE"})
ALL_OUTCOMES = STRONG_OUTCOMES | WEAK_OUTCOMES | NON_DEPENDENCY_OUTCOMES

EVIDENCE_STATES = frozenset({"resolved", "insufficient"})
INSTALLATION_IMPACTS = frozenset({
    "would_fail_install",
    "would_install_different_package",
    "would_install_but_functionally_invalid",
    "unknown",
    "not_applicable_local_reference",
})

# Required, response-internal evidence for SELF_REFERENCE_OR_LOCAL_PACKAGE.
SELF_REFERENCE_BASES = frozenset({
    "generated_project_own_package_name",
    "generated_local_or_workspace_package",
})
SELF_REFERENCE_CONTEXTS = frozenset({
    "documentation_example",
    "project_source",
    "test_or_script",
    "package_manifest",
})
SELF_REFERENCE_EVIDENCE_FIELDS = frozenset({
    "basis", "declared_name", "declaration_location", "reference_locations",
    "reference_contexts", "symbols_defined_in_response",
})

CHECK_FIELDS = ("historical", "normalization", "ambiguity", "namespace", "ecosystem", "types_package")
CHECK_VALUES = {
    "historical": frozenset({"no_prior_evidence", "prior_or_removed", "inconclusive"}),
    "normalization": frozenset({"external_npm_reference", "builtin_or_local", "inconclusive"}),
    "ambiguity": frozenset({"cleared", "inconclusive"}),
    "namespace": frozenset({"cleared", "confirmed_mismatch", "inconclusive"}),
    "ecosystem": frozenset({"cleared", "confirmed_other_ecosystem", "inconclusive"}),
    "types_package": frozenset({"cleared", "invalid_or_redundant", "inconclusive"}),
}
CONFIRMED_HALLUCINATION_CHECKS = {
    "historical": "no_prior_evidence",
    "normalization": "external_npm_reference",
    "ambiguity": "cleared",
    "namespace": "cleared",
    "ecosystem": "cleared",
    "types_package": "cleared",
}

RECORD_FIELDS = (
    "run_id", "normalized_package", "source_classification", "source_validation_status",
    "source_adjudication_status", "source_truncated", "adjudication_outcome",
    "dependency_failure", "confirmed_package_hallucination", "evidence_status",
    "evidence_sources", "current_registry_evidence", "historical_evidence",
    "response_context_reference", "nearest_legitimate_reference", "installation_impact",
    "checks", "external_dependency_eligible", "self_reference_evidence",
    "rationale", "reviewer", "reviewed_at", "adjudication_version", "provenance",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def require_text(value, message):
    require(isinstance(value, str) and value.strip(), message)


def is_utc(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.utcoffset() == timezone.utc.utcoffset(parsed)
    except ValueError:
        return False


def read_json(path):
    data = Path(path).read_bytes()
    return json.loads(data), hashlib.sha256(data).hexdigest()


def load_source(path):
    """Load a PIPE-05 joined classification envelope read-only. Never modified."""
    document, digest = read_json(path)
    require(isinstance(document, dict), "--source must be a JSON object envelope")
    require(document.get("format_version") == SOURCE_FORMAT_VERSION,
            f"--source format_version must be {SOURCE_FORMAT_VERSION!r}, "
            f"got {document.get('format_version')!r}")
    records = document.get("records")
    require(isinstance(records, list), "--source records must be an array")
    by_key = {}
    for row in records:
        require(isinstance(row, dict), "--source record must be an object")
        run_id, normalized_package = row.get("run_id"), row.get("normalized_package")
        require(isinstance(run_id, str) and run_id and
                isinstance(normalized_package, str) and normalized_package,
                "--source record missing run_id/normalized_package")
        key = (run_id, normalized_package)
        require(key not in by_key, f"Duplicate source record for {key}")
        by_key[key] = row
    return by_key, digest


def require_evidence_sources(evidence_sources, message):
    require(isinstance(evidence_sources, list) and evidence_sources, message)
    for entry in evidence_sources:
        require(isinstance(entry, dict), message)
        require_text(entry.get("source"), f"{message}: source text required")
        require_text(entry.get("summary"), f"{message}: summary text required")
        require(is_utc(entry.get("checked_at")), f"{message}: checked_at must be UTC")


def require_checks(checks):
    require(isinstance(checks, dict) and set(checks) == set(CHECK_FIELDS),
            f"checks must contain exactly {sorted(CHECK_FIELDS)}")
    for field in CHECK_FIELDS:
        require(checks[field] in CHECK_VALUES[field], f"Invalid {field} check: {checks.get(field)!r}")


def require_self_reference_evidence(evidence, normalized_package):
    """Response-internal proof that the name is the generated project itself or a
    local/workspace package it declares -- never inferred from a registry 404."""
    message = "SELF_REFERENCE_OR_LOCAL_PACKAGE requires self_reference_evidence"
    require(isinstance(evidence, dict) and set(evidence) == SELF_REFERENCE_EVIDENCE_FIELDS,
            f"{message} with exactly {sorted(SELF_REFERENCE_EVIDENCE_FIELDS)}")
    require(evidence["basis"] in SELF_REFERENCE_BASES,
            f"{message}.basis in {sorted(SELF_REFERENCE_BASES)}, got {evidence['basis']!r}")
    require(evidence["declared_name"] == normalized_package,
            f"{message}.declared_name equal to the adjudicated package "
            f"{normalized_package!r}, got {evidence['declared_name']!r}")
    require_text(evidence["declaration_location"], f"{message}.declaration_location")
    locations = evidence["reference_locations"]
    require(isinstance(locations, list) and locations and
            all(isinstance(entry, str) and entry.strip() for entry in locations),
            f"{message}.reference_locations as a non-empty array of text")
    contexts = evidence["reference_contexts"]
    require(isinstance(contexts, list) and contexts and set(contexts) <= SELF_REFERENCE_CONTEXTS,
            f"{message}.reference_contexts as a non-empty subset of {sorted(SELF_REFERENCE_CONTEXTS)}")
    require(isinstance(evidence["symbols_defined_in_response"], bool),
            f"{message}.symbols_defined_in_response as a boolean")
    return {
        "basis": evidence["basis"],
        "declared_name": evidence["declared_name"],
        "declaration_location": evidence["declaration_location"],
        "reference_locations": list(locations),
        "reference_contexts": sorted(set(contexts)),
        "symbols_defined_in_response": evidence["symbols_defined_in_response"],
    }


def adjudicate_one(item, source_by_key):
    require(isinstance(item, dict), "Adjudication entries must be objects")
    run_id, normalized_package = item.get("run_id"), item.get("normalized_package")
    key = (run_id, normalized_package)
    require(key in source_by_key, f"Adjudication references unknown run/package pair: {key}")
    source = source_by_key[key]
    require(source.get("adjudication_status") == "REVIEW_REQUIRED" and
            source.get("classification") == "AMBIGUOUS" and
            source.get("review_required") is True,
            f"Source row for {key} is not REVIEW_REQUIRED/AMBIGUOUS")

    outcome = item.get("adjudication_outcome")
    require(outcome in ALL_OUTCOMES, f"Invalid or unsupported adjudication_outcome: {outcome!r}")

    require_text(item.get("reviewer"), "reviewer is required")
    require(is_utc(item.get("reviewed_at")), "reviewed_at must be a UTC timestamp")
    require_text(item.get("rationale"), "rationale is required")

    evidence_status = item.get("evidence_status")
    require(evidence_status in EVIDENCE_STATES,
            f"evidence_status must be one of {sorted(EVIDENCE_STATES)}, got {evidence_status!r}")

    checks = item.get("checks")
    require_checks(checks)

    dependency_failure = item.get("dependency_failure")
    nearest_legitimate_reference = item.get("nearest_legitimate_reference")
    installation_impact = item.get("installation_impact")
    current_registry_evidence = item.get("current_registry_evidence")
    historical_evidence = item.get("historical_evidence")
    evidence_sources = item.get("evidence_sources")
    self_reference_evidence = item.get("self_reference_evidence")

    require(installation_impact != "not_applicable_local_reference" or
            outcome == "SELF_REFERENCE_OR_LOCAL_PACKAGE",
            "installation_impact 'not_applicable_local_reference' is reserved for "
            "SELF_REFERENCE_OR_LOCAL_PACKAGE")
    require(self_reference_evidence is None or outcome == "SELF_REFERENCE_OR_LOCAL_PACKAGE",
            "self_reference_evidence is only valid for SELF_REFERENCE_OR_LOCAL_PACKAGE")

    if outcome == "UNRESOLVED":
        require(evidence_status == "insufficient", "UNRESOLVED requires evidence_status 'insufficient'")
        require(dependency_failure is None, "UNRESOLVED must not assert a dependency_failure value")
        require(installation_impact in (None, "unknown"),
                "UNRESOLVED installation_impact must be null or 'unknown'")
        installation_impact = "unknown"
        evidence_sources = evidence_sources or []
        require(isinstance(evidence_sources, list), "evidence_sources must be an array")
    else:
        require(evidence_status == "resolved", f"{outcome} requires evidence_status 'resolved'")
        require_evidence_sources(evidence_sources,
                                  "Dated evidence_sources required for a non-UNRESOLVED outcome")
        require(installation_impact in INSTALLATION_IMPACTS,
                f"installation_impact must be one of {sorted(INSTALLATION_IMPACTS)}, "
                f"got {installation_impact!r}")

    if outcome in STRONG_OUTCOMES or outcome == "OTHER_DEPENDENCY_ERROR":
        require(isinstance(dependency_failure, bool), f"{outcome} requires an explicit boolean dependency_failure")

    if outcome == "CONFIRMED_HALLUCINATION":
        require(checks == CONFIRMED_HALLUCINATION_CHECKS,
                "CONFIRMED_HALLUCINATION requires every conservative check cleared: "
                "historical=no_prior_evidence, normalization=external_npm_reference, and "
                "ambiguity/namespace/ecosystem/types_package=cleared, ruling out namespace, "
                "ecosystem, and types-package confusion as better explanations")
        require(dependency_failure is True, "CONFIRMED_HALLUCINATION requires dependency_failure=true")
    elif outcome == "LEGACY_OR_REMOVED":
        require(checks["historical"] == "prior_or_removed",
                "LEGACY_OR_REMOVED requires checks.historical='prior_or_removed'")
        require(checks["normalization"] == "external_npm_reference",
                "LEGACY_OR_REMOVED requires checks.normalization='external_npm_reference'")
    elif outcome == "NAMESPACE_CONFUSION":
        require(checks["namespace"] == "confirmed_mismatch",
                "NAMESPACE_CONFUSION requires checks.namespace='confirmed_mismatch'")
        require_text(nearest_legitimate_reference, "NAMESPACE_CONFUSION requires nearest_legitimate_reference")
    elif outcome == "PACKAGE_NAME_CONFUSION":
        require_text(nearest_legitimate_reference, "PACKAGE_NAME_CONFUSION requires nearest_legitimate_reference")
        require(checks["normalization"] == "external_npm_reference",
                "PACKAGE_NAME_CONFUSION requires checks.normalization='external_npm_reference'")
    elif outcome == "INVALID_OR_REDUNDANT_TYPES_PACKAGE":
        require(checks["types_package"] == "invalid_or_redundant",
                "INVALID_OR_REDUNDANT_TYPES_PACKAGE requires checks.types_package='invalid_or_redundant'")
    elif outcome == "ECOSYSTEM_CONFUSION":
        require(checks["ecosystem"] == "confirmed_other_ecosystem",
                "ECOSYSTEM_CONFUSION requires checks.ecosystem='confirmed_other_ecosystem'")
    elif outcome == "SELF_REFERENCE_OR_LOCAL_PACKAGE":
        require(checks["normalization"] == "builtin_or_local",
                "SELF_REFERENCE_OR_LOCAL_PACKAGE requires checks.normalization='builtin_or_local'")
        require(dependency_failure is False,
                "SELF_REFERENCE_OR_LOCAL_PACKAGE requires dependency_failure=false")
        require(installation_impact == "not_applicable_local_reference",
                "SELF_REFERENCE_OR_LOCAL_PACKAGE requires "
                "installation_impact='not_applicable_local_reference'")
        self_reference_evidence = require_self_reference_evidence(
            self_reference_evidence, normalized_package)

    if outcome in STRONG_OUTCOMES or outcome == "OTHER_DEPENDENCY_ERROR":
        require(checks["normalization"] != "builtin_or_local",
                f"{outcome} is an external-dependency outcome and cannot carry "
                "checks.normalization='builtin_or_local'; use SELF_REFERENCE_OR_LOCAL_PACKAGE "
                "with self_reference_evidence")

    require(current_registry_evidence is None or isinstance(current_registry_evidence, dict),
            "current_registry_evidence must be an object or null")
    require(historical_evidence is None or (isinstance(historical_evidence, list) and
            all(isinstance(entry, dict) for entry in historical_evidence)),
            "historical_evidence must be an array of objects or null")
    require(nearest_legitimate_reference is None or
            (isinstance(nearest_legitimate_reference, str) and nearest_legitimate_reference.strip()),
            "nearest_legitimate_reference must be a non-empty string or null")

    confirmed_package_hallucination = outcome == "CONFIRMED_HALLUCINATION"
    if outcome in NON_DEPENDENCY_OUTCOMES:
        external_dependency_eligible = False
    elif outcome == "UNRESOLVED":
        external_dependency_eligible = None
    else:
        external_dependency_eligible = True

    response_context_reference = {
        "response_artifact_path": source.get("response_artifact_path"),
        "task_id": source.get("task_id"),
        "category": source.get("category"),
        "model_condition_id": source.get("model_condition_id"),
        "collection_order": source.get("collection_order"),
        "truncated": source.get("truncated"),
        "first_occurrence_index": source.get("first_occurrence_index"),
    }
    provenance = [
        f"source_classification={source.get('classification')}",
        f"source_classification_basis={source.get('classification_basis')}",
        f"source_adjudication_status={source.get('adjudication_status')}",
        f"source_classifier_version={source.get('classifier_version')}",
        f"source_validator_version={source.get('validator_version')}",
        f"source_checked_at={source.get('checked_at')}",
        f"adjudication_tool_version={TOOL_VERSION}",
    ]

    record = {
        "run_id": run_id,
        "normalized_package": normalized_package,
        "source_classification": source.get("classification"),
        "source_validation_status": source.get("validation_status"),
        "source_adjudication_status": source.get("adjudication_status"),
        "source_truncated": bool(source.get("truncated")),
        "adjudication_outcome": outcome,
        "dependency_failure": dependency_failure,
        "confirmed_package_hallucination": confirmed_package_hallucination,
        "evidence_status": evidence_status,
        "evidence_sources": evidence_sources,
        "current_registry_evidence": current_registry_evidence,
        "historical_evidence": historical_evidence,
        "response_context_reference": response_context_reference,
        "nearest_legitimate_reference": nearest_legitimate_reference,
        "installation_impact": installation_impact,
        "checks": checks,
        "external_dependency_eligible": external_dependency_eligible,
        "self_reference_evidence": self_reference_evidence,
        "rationale": item["rationale"],
        "reviewer": item["reviewer"],
        "reviewed_at": item["reviewed_at"],
        "adjudication_version": TOOL_VERSION,
        "provenance": provenance,
    }
    sort_key = (source.get("collection_order") or 0, normalized_package, run_id)
    return record, sort_key


def adjudicate(items, source_by_key):
    require(isinstance(items, list), "Adjudication input must be a JSON array")
    seen = set()
    scored = []
    for item in items:
        record, sort_key = adjudicate_one(item, source_by_key)
        key = (record["run_id"], record["normalized_package"])
        require(key not in seen, f"Duplicate adjudication for {key}")
        seen.add(key)
        scored.append((sort_key, record))
    scored.sort(key=lambda pair: pair[0])
    return [record for _, record in scored]


def output_paths(output_dir):
    base = Path(output_dir)
    return {
        "json": base / "package_adjudication_pipe05b_v1.json",
        "csv": base / "package_adjudication_pipe05b_v1.csv",
    }


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
                f"Existing PIPE-05B output differs; preserve it and choose a new output directory: {path}")
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


def write_outputs(output_dir, records, source_hash, adjudication_hash):
    paths = output_paths(output_dir)
    envelope = {
        "format_version": FORMAT_VERSION,
        "adjudication_version": TOOL_VERSION,
        "source_input_hash": source_hash,
        "adjudication_input_hash": adjudication_hash,
        "records": records,
    }
    files = {
        "json": (json.dumps(envelope, indent=2, ensure_ascii=False) + "\n").encode("utf-8"),
        "csv": csv_bytes(records, RECORD_FIELDS),
    }
    for key, path in paths.items():
        if path.exists():
            require(path.read_bytes() == files[key], f"Existing PIPE-05B output differs: {path}")
    for key, path in paths.items():
        atomic_write_new_or_identical(path, files[key])
    return paths


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True,
                         help="Explicit path to a PIPE-05 joined classification JSON envelope "
                              "(pipe-05-classification-1.0.0). Never modified.")
    parser.add_argument("--adjudications", required=True,
                         help="Explicit path to a researcher-supplied JSON array of dated, "
                              "evidence-based adjudication decisions. No 'latest' auto-discovery.")
    parser.add_argument("--output-dir", required=True,
                         help="Explicit output directory for the new PIPE-05B envelope files.")
    args = parser.parse_args(argv)

    source_by_key, source_hash = load_source(args.source)
    items, adjudication_hash = read_json(args.adjudications)
    records = adjudicate(items, source_by_key)
    write_outputs(args.output_dir, records, source_hash, adjudication_hash)

    confirmed = sum(record["confirmed_package_hallucination"] for record in records)
    unresolved = sum(record["adjudication_outcome"] == "UNRESOLVED" for record in records)
    not_external = sum(record["external_dependency_eligible"] is False for record in records)
    print(f"Wrote {len(records)} PIPE-05B adjudication record(s); "
          f"{confirmed} confirmed_package_hallucination, {unresolved} UNRESOLVED, "
          f"{not_external} not external-dependency eligible. "
          "This never changes PIPE-05 primary classification; D037 routing is resolved by PIPE-07.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
