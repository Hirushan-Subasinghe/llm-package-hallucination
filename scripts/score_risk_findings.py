#!/usr/bin/env python3
"""PIPE-06: deterministic risk scoring for confirmed research findings.

Implements risk-model-1.0.0 exactly as frozen in docs/risk_assessment_protocol.md:
risk score = Impact (1-5) x Detectability (1-4); security_sensitive_context is a
separate, non-scored flag. The model is a rule-based ordinal prioritization aid,
never a probability or predictive model.

Only a finding whose research_classification is one of the four eligible
hallucination categories AND whose evidence_status is "resolved" may receive a
score. Every other finding -- ineligible category, AMBIGUOUS, VALID,
LEGACY_OR_REMOVED, BUILTIN_OR_LOCAL, UNRESOLVED, OTHER_IMPLEMENTATION_ERROR, or an
otherwise-eligible category with unresolved evidence -- remains unscored:
eligibility=false, risk_score=null, risk_band=null. An unscored finding is never
encoded as risk score 0.

No network requests, package installation, or generated-code execution. This
script only scores synthetic or previously classified finding candidates supplied
on disk; it performs no experimental data collection.
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

RISK_MODEL_VERSION = "risk-model-1.0.0"
FORMAT_VERSION = "pipe-06-risk-1.0.0"

ELIGIBLE_CATEGORIES = frozenset({
    "CONFIRMED_HALLUCINATION",
    "PACKAGE_VERSION_HALLUCINATION",
    "PACKAGE_API_HALLUCINATION",
    "PACKAGE_CAPABILITY_HALLUCINATION",
})
INELIGIBLE_CATEGORIES = frozenset({
    "VALID",
    "LEGACY_OR_REMOVED",
    "AMBIGUOUS",
    "BUILTIN_OR_LOCAL",
    "UNRESOLVED",
    "OTHER_IMPLEMENTATION_ERROR",
})
ALL_CATEGORIES = ELIGIBLE_CATEGORIES | INELIGIBLE_CATEGORIES
EVIDENCE_STATES = frozenset({"resolved", "unresolved"})

RECORD_FIELDS = (
    "finding_id", "run_ids", "normalized_package", "affected_version_or_range",
    "research_classification", "evidence_status", "source_evidence",
    "expected_consequence", "eligibility", "eligibility_basis",
    "impact_score", "impact_rationale", "detectability_score",
    "detectability_rationale", "risk_score", "risk_band",
    "security_sensitive_context", "security_sensitive_rationale",
    "risk_model_version", "assessor_id", "assessed_at", "provenance",
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


def risk_band(score):
    """Deterministic risk-model-1.0.0 band assignment. `score` is None for unscored findings."""
    if score is None:
        return None
    if 1 <= score <= 4:
        return "LOW"
    if 5 <= score <= 8:
        return "MODERATE"
    if 9 <= score <= 14:
        return "HIGH"
    if 15 <= score <= 20:
        return "CRITICAL"
    raise ValueError(f"risk_score {score} falls outside the defined risk-model-1.0.0 band ranges (1-20)")


def score_finding(candidate):
    """Validate one finding candidate and apply risk-model-1.0.0. Returns a full PIPE-06 record.

    Raises ValueError for structurally invalid or research-integrity-violating input
    (e.g. an out-of-range score, missing required rationale/evidence for an eligible
    finding, or a score attached to an ineligible/unresolved finding). Never guesses
    a value and never assigns risk_score=0 to mean "unscored".
    """
    require(isinstance(candidate, dict), "Finding candidate must be an object")

    require_text(candidate.get("finding_id"), "finding_id is required")
    run_ids = candidate.get("run_ids")
    require(isinstance(run_ids, list) and run_ids and
            all(isinstance(item, str) and item.strip() for item in run_ids),
            "run_ids must be a non-empty array of non-empty strings")
    require_text(candidate.get("normalized_package"), "normalized_package is required")

    affected_version_or_range = candidate.get("affected_version_or_range")
    require(affected_version_or_range is None or isinstance(affected_version_or_range, str),
            "affected_version_or_range must be a string or null")

    classification = candidate.get("research_classification")
    require(classification in ALL_CATEGORIES,
            f"Unknown research_classification: {classification!r}")

    evidence_status = candidate.get("evidence_status")
    require(evidence_status in EVIDENCE_STATES,
            f"evidence_status must be one of {sorted(EVIDENCE_STATES)}, got {evidence_status!r}")

    category_eligible = classification in ELIGIBLE_CATEGORIES
    eligible = category_eligible and evidence_status == "resolved"

    if not category_eligible:
        eligibility_basis = (
            f"research_classification '{classification}' is not one of the eligible "
            "hallucination categories under risk-model-1.0.0 eligibility rules"
        )
    elif evidence_status != "resolved":
        eligibility_basis = (
            f"'{classification}' is an eligible hallucination category but evidence_status "
            "is 'unresolved'; scoring evidence is not yet resolved, so the finding stays unscored"
        )
    else:
        eligibility_basis = (
            f"'{classification}' is an eligible confirmed finding with resolved scoring evidence"
        )

    source_evidence = candidate.get("source_evidence")
    expected_consequence = candidate.get("expected_consequence")
    impact_score = candidate.get("impact_score")
    impact_rationale = candidate.get("impact_rationale")
    detectability_score = candidate.get("detectability_score")
    detectability_rationale = candidate.get("detectability_rationale")

    if eligible:
        require_text(source_evidence, "source_evidence is required for an eligible finding")
        require_text(expected_consequence, "expected_consequence is required for an eligible finding")
        require(isinstance(impact_score, int) and not isinstance(impact_score, bool),
                "impact_score (integer) is required for an eligible finding")
        require(1 <= impact_score <= 5, f"impact_score must be an integer 1-5, got {impact_score!r}")
        require_text(impact_rationale, "impact_rationale is required for an eligible finding")
        require(isinstance(detectability_score, int) and not isinstance(detectability_score, bool),
                "detectability_score (integer) is required for an eligible finding")
        require(1 <= detectability_score <= 4,
                f"detectability_score must be an integer 1-4, got {detectability_score!r}")
        require_text(detectability_rationale, "detectability_rationale is required for an eligible finding")
        risk_score = impact_score * detectability_score
        band = risk_band(risk_score)
    else:
        require(impact_score is None, "impact_score must not be set on an ineligible or evidence-unresolved finding")
        require(detectability_score is None,
                "detectability_score must not be set on an ineligible or evidence-unresolved finding")
        require(impact_rationale is None,
                "impact_rationale must not be set on an ineligible or evidence-unresolved finding")
        require(detectability_rationale is None,
                "detectability_rationale must not be set on an ineligible or evidence-unresolved finding")
        risk_score = None
        band = None

    require(isinstance(candidate.get("security_sensitive_context"), bool),
            "security_sensitive_context (boolean) is required")
    require_text(candidate.get("security_sensitive_rationale"), "security_sensitive_rationale is required")

    require_text(candidate.get("assessor_id"), "assessor_id is required")
    require(is_utc(candidate.get("assessed_at")), "assessed_at must be an ISO-8601 UTC timestamp ending in 'Z'")

    provenance = candidate.get("provenance")
    require(isinstance(provenance, list) and provenance and
            all(isinstance(item, str) and item.strip() for item in provenance),
            "provenance must be a non-empty array of non-empty strings")

    return {
        "finding_id": candidate["finding_id"],
        "run_ids": list(run_ids),
        "normalized_package": candidate["normalized_package"],
        "affected_version_or_range": affected_version_or_range,
        "research_classification": classification,
        "evidence_status": evidence_status,
        "source_evidence": source_evidence,
        "expected_consequence": expected_consequence,
        "eligibility": eligible,
        "eligibility_basis": eligibility_basis,
        "impact_score": impact_score,
        "impact_rationale": impact_rationale,
        "detectability_score": detectability_score,
        "detectability_rationale": detectability_rationale,
        "risk_score": risk_score,
        "risk_band": band,
        "security_sensitive_context": candidate["security_sensitive_context"],
        "security_sensitive_rationale": candidate["security_sensitive_rationale"],
        "risk_model_version": RISK_MODEL_VERSION,
        "assessor_id": candidate["assessor_id"],
        "assessed_at": candidate["assessed_at"],
        "provenance": list(provenance),
    }


def score_findings(candidates):
    """Score every candidate and return records in deterministic finding_id order."""
    require(isinstance(candidates, list), "Input must be a JSON array of finding candidates")
    records = [score_finding(candidate) for candidate in candidates]
    seen = set()
    for record in records:
        require(record["finding_id"] not in seen, f"Duplicate finding_id: {record['finding_id']}")
        seen.add(record["finding_id"])
    return sorted(records, key=lambda record: record["finding_id"])


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
                f"Existing PIPE-06 output differs; preserve it and choose a new output directory: {path}")
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


def write_outputs(output_dir, records, source_input_hash, version_label):
    base = Path(output_dir)
    envelope = {
        "format_version": FORMAT_VERSION,
        "risk_model_version": RISK_MODEL_VERSION,
        "source_input_hash": source_input_hash,
        "records": records,
    }
    json_path = base / f"risk_findings_{version_label}.json"
    csv_path = base / f"risk_findings_{version_label}.csv"
    json_bytes = (json.dumps(envelope, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    csv_data = csv_bytes(records, RECORD_FIELDS)
    atomic_write_new_or_identical(json_path, json_bytes)
    atomic_write_new_or_identical(csv_path, csv_data)
    return json_path, csv_path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True,
                         help="JSON array of finding candidates (synthetic fixtures for infrastructure work)")
    parser.add_argument("--output-dir", default="results/risk")
    parser.add_argument("--version-label", default="pilot",
                         help="Suffix distinguishing pilot/synthetic runs from any future real dataset version")
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    input_bytes = input_path.read_bytes()
    candidates = json.loads(input_bytes)
    source_input_hash = hashlib.sha256(input_bytes).hexdigest()

    records = score_findings(candidates)
    json_path, csv_path = write_outputs(args.output_dir, records, source_input_hash, args.version_label)

    scored = sum(record["eligibility"] for record in records)
    print(f"Wrote {len(records)} risk-finding record(s) to {json_path} and {csv_path}; "
          f"{scored} scored under {RISK_MODEL_VERSION}, {len(records) - scored} unscored.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
