#!/usr/bin/env python3
"""PIPE-08: reusable primary PHR/SHR metric calculator.

Computes the two frozen primary metrics from decision D033
(docs/decision_log.md) and docs/package_hallucination_taxonomy.md's Metric
Boundaries, using the PIPE-07 package/response-level derived datasets as input:

  PHR = (metric-eligible package rows primary-confirmed under D037)
        / (all metric-eligible package rows)

    Primary unit: one unique normalized package per response,
    (run_id, normalized_package). Repeated occurrences of the same package in
    one response were already deduplicated by PIPE-07/PIPE-03 and never
    inflate this denominator or numerator.

  SHR = (metric-eligible responses containing >= 1 D037 primary-confirmed package)
        / (all metric-eligible responses)

    Primary unit: one completed, non-truncated response. A metric-eligible
    response with zero package references remains in the SHR denominator and
    contributes 0 to the numerator.

metric_eligible is read directly from the PIPE-07 datasets (collection_status
== "completed"); this script does not recompute or redefine that rule. A zero
denominator produces rate=null, never rate=0.

This script performs no registry query, no model call, no code execution, and
no model-condition comparison. It only aggregates two already-produced,
read-only derived datasets after independently cross-validating that they
agree with each other; it refuses to compute anything from datasets that
disagree.
"""

import argparse
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ANALYSIS_VERSION = "pipe-08-metrics-calculator-1.1.0"
FORMAT_VERSION = "pipe-08-primary-metrics-1.1.0"
METRIC_DEFINITION_REFERENCE = (
    "docs/decision_log.md D033 (denominators and units) and D037 (confirmed-hallucination "
    "numerator routing; primary PHR unit = unique (run_id, normalized_package) "
    "per response; primary SHR unit = one completed, non-truncated response); "
    "docs/package_hallucination_taxonomy.md Metric Boundaries"
)
EXPECTED_PACKAGE_FORMAT_VERSION = "pipe-07-analysis-1.1.0"
EXPECTED_RESPONSE_FORMAT_VERSION = "pipe-07-analysis-1.1.0"

CLASSIFICATION_VALUES = frozenset({
    "VALID", "CONFIRMED_HALLUCINATION", "LEGACY_OR_REMOVED", "AMBIGUOUS", "BUILTIN_OR_LOCAL", None,
})


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    data = Path(path).read_bytes()
    return json.loads(data), hashlib.sha256(data).hexdigest()


def load_envelope(path, expected_format_version, label):
    document, digest = read_json(path)
    require(isinstance(document, dict), f"{label} must be a JSON object envelope")
    require(document.get("format_version") == expected_format_version,
            f"{label} format_version mismatch: expected {expected_format_version!r}, "
            f"got {document.get('format_version')!r}")
    records = document.get("records")
    require(isinstance(records, list), f"{label} 'records' must be an array")
    return document, records, digest


def load_package_dataset(path):
    document, records, digest = load_envelope(path, EXPECTED_PACKAGE_FORMAT_VERSION, "--package-dataset")
    by_key = {}
    for row in records:
        require(isinstance(row, dict), "--package-dataset rows must be objects")
        key = (row.get("run_id"), row.get("normalized_package"))
        require(all(key), "--package-dataset row missing run_id or normalized_package")
        require(key not in by_key, f"Duplicate package key in --package-dataset: {key}")
        classification = row.get("research_classification")
        require(classification in CLASSIFICATION_VALUES,
                f"Unsupported research_classification for {key}: {classification!r}")
        require(isinstance(row.get("metric_eligible"), bool),
                f"metric_eligible (boolean) is required for {key}")
        require(isinstance(row.get("primary_confirmed_hallucination"), bool),
                f"primary_confirmed_hallucination (boolean) is required for {key}")
        path = row.get("primary_confirmation_path")
        require(path in {"PIPE05_REVIEWED", "PIPE05B", "NONE"},
                f"Unsupported primary_confirmation_path for {key}: {path!r}")
        require(row["primary_confirmed_hallucination"] == (path != "NONE"),
                f"primary confirmation fields disagree for {key}")
        provenance = row.get("provenance")
        require(isinstance(provenance, list) and provenance,
                f"Non-empty provenance is required for {key}")
        by_key[key] = row
    return document, records, by_key, digest


def load_response_dataset(path):
    document, records, digest = load_envelope(path, EXPECTED_RESPONSE_FORMAT_VERSION, "--response-dataset")
    by_run = {}
    for row in records:
        require(isinstance(row, dict), "--response-dataset rows must be objects")
        run_id = row.get("run_id")
        require(isinstance(run_id, str) and run_id, "--response-dataset row missing run_id")
        require(run_id not in by_run, f"Duplicate run_id in --response-dataset: {run_id}")
        require(isinstance(row.get("metric_eligible"), bool),
                f"metric_eligible (boolean) is required for {run_id}")
        by_run[run_id] = row
    return document, records, by_run, digest


def cross_validate(package_by_key, response_by_run):
    packages_by_run = defaultdict(list)
    for (run_id, _normalized_package), row in package_by_key.items():
        require(run_id in response_by_run,
                f"--package-dataset references a run_id absent from --response-dataset: {run_id}")
        response_row = response_by_run[run_id]
        require(row["metric_eligible"] == response_row["metric_eligible"],
                f"Metric-eligibility disagreement between --package-dataset and --response-dataset "
                f"for {run_id}: package={row['metric_eligible']!r} response={response_row['metric_eligible']!r}")
        packages_by_run[run_id].append(row)

    for run_id, response_row in response_by_run.items():
        packages = packages_by_run.get(run_id, [])
        recomputed_unique_count = len(packages)
        recomputed_confirmed_count = sum(
            1 for row in packages if row["primary_confirmed_hallucination"])
        recomputed_contains_confirmed = recomputed_confirmed_count > 0

        require(recomputed_confirmed_count <= recomputed_unique_count,
                f"Impossible counts for {run_id}: confirmed_hallucinated_package_count "
                f"({recomputed_confirmed_count}) exceeds unique_package_count ({recomputed_unique_count})")
        require(response_row.get("unique_package_count") == recomputed_unique_count,
                f"--response-dataset unique_package_count disagrees with --package-dataset for {run_id}: "
                f"{response_row.get('unique_package_count')!r} != {recomputed_unique_count}")
        require(response_row.get("confirmed_hallucinated_package_count") == recomputed_confirmed_count,
                f"--response-dataset confirmed_hallucinated_package_count disagrees with --package-dataset "
                f"for {run_id}: {response_row.get('confirmed_hallucinated_package_count')!r} != "
                f"{recomputed_confirmed_count}")
        require(response_row.get("contains_confirmed_package_hallucination") == recomputed_contains_confirmed,
                f"--response-dataset contains_confirmed_package_hallucination disagrees with "
                f"--package-dataset for {run_id}")

    return packages_by_run


def rate_or_null(numerator, denominator):
    require(numerator <= denominator, f"Impossible metric: numerator {numerator} exceeds denominator {denominator}")
    if denominator == 0:
        return None
    return numerator / denominator


def compute_metrics(package_by_key, response_by_run, packages_by_run):
    eligible_package_rows = [row for row in package_by_key.values() if row["metric_eligible"]]
    phr_denominator = len(eligible_package_rows)
    phr_numerator = sum(1 for row in eligible_package_rows
                         if row["primary_confirmed_hallucination"])
    phr_rate = rate_or_null(phr_numerator, phr_denominator)

    eligible_response_rows = [row for row in response_by_run.values() if row["metric_eligible"]]
    shr_denominator = len(eligible_response_rows)
    shr_numerator = 0
    for response_row in eligible_response_rows:
        packages = packages_by_run.get(response_row["run_id"], [])
        if any(row["primary_confirmed_hallucination"] for row in packages):
            shr_numerator += 1
    shr_rate = rate_or_null(shr_numerator, shr_denominator)

    ambiguous_package_row_count = sum(1 for row in eligible_package_rows
                                       if row["research_classification"] == "AMBIGUOUS")
    unresolved_package_row_count = sum(1 for row in eligible_package_rows
                                        if row.get("validation_status") == "unresolved")
    truncated_response_count = sum(1 for row in response_by_run.values()
                                    if row.get("collection_status") == "truncated")
    confirmed_by_reviewed = sum(1 for row in eligible_package_rows
                                if row["primary_confirmation_path"] == "PIPE05_REVIEWED")
    confirmed_by_pipe05b = sum(1 for row in eligible_package_rows
                                if row["primary_confirmation_path"] == "PIPE05B")
    eligible_review_required_without_pipe05b = sum(
        1 for row in eligible_package_rows if row["adjudication_status"] == "REVIEW_REQUIRED" and
        row.get("pipe05b_adjudication_outcome") is None)
    eligible_pipe05b_unresolved = sum(
        1 for row in eligible_package_rows if row.get("pipe05b_adjudication_outcome") == "UNRESOLVED")

    return {
        "phr": {"numerator": phr_numerator, "denominator": phr_denominator, "rate": phr_rate},
        "shr": {"numerator": shr_numerator, "denominator": shr_denominator, "rate": shr_rate},
        "eligible_response_count": shr_denominator,
        "eligible_package_row_count": phr_denominator,
        "ambiguous_package_row_count": ambiguous_package_row_count,
        "unresolved_package_row_count": unresolved_package_row_count,
        "truncated_response_count": truncated_response_count,
        "primary_confirmed_by_pipe05_reviewed": confirmed_by_reviewed,
        "primary_confirmed_by_pipe05b": confirmed_by_pipe05b,
        "eligible_review_required_without_pipe05b": eligible_review_required_without_pipe05b,
        "eligible_pipe05b_unresolved": eligible_pipe05b_unresolved,
    }


def build_output(package_document, response_document, package_hash, response_hash,
                  metrics, version_label, generated_at):
    return {
        "format_version": FORMAT_VERSION,
        "analysis_version": ANALYSIS_VERSION,
        "source_version_label": version_label,
        "generated_at": generated_at,
        "metric_definition_reference": METRIC_DEFINITION_REFERENCE,
        **metrics,
        "provenance": {
            "package_dataset_input_hash": package_hash,
            "response_dataset_input_hash": response_hash,
            "package_dataset_upstream_hashes": {
                key: value for key, value in package_document.items()
                if key not in ("format_version", "records")
            },
            "response_dataset_upstream_hashes": {
                key: value for key, value in response_document.items()
                if key not in ("format_version", "records")
            },
        },
    }


def calculate(package_dataset_path, response_dataset_path, version_label, generated_at):
    package_document, _package_records, package_by_key, package_hash = load_package_dataset(package_dataset_path)
    response_document, _response_records, response_by_run, response_hash = load_response_dataset(response_dataset_path)
    packages_by_run = cross_validate(package_by_key, response_by_run)
    metrics = compute_metrics(package_by_key, response_by_run, packages_by_run)
    return build_output(package_document, response_document, package_hash, response_hash,
                         metrics, version_label, generated_at)


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--package-dataset", required=True,
                         help="Path to a PIPE-07 package_response_analysis_*.json envelope")
    parser.add_argument("--response-dataset", required=True,
                         help="Path to a PIPE-07 response_level_analysis_*.json envelope")
    parser.add_argument("--output", required=True, help="Path to write the PIPE-08 metrics JSON")
    parser.add_argument("--version-label", required=True,
                         help="Explicit dataset-version label carried into the output "
                              "(e.g. v2.6.0-interim); never inferred automatically")
    parser.add_argument("--generated-at",
                         help="ISO-8601 UTC timestamp to record as generated_at; defaults to the current "
                              "time. Pass an explicit value for byte-reproducible reruns.")
    args = parser.parse_args(argv)

    generated_at = args.generated_at or utc_now()
    output = calculate(args.package_dataset, args.response_dataset, args.version_label, generated_at)

    output_path = Path(args.output)
    data = (json.dumps(output, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    if output_path.exists():
        require(output_path.read_bytes() == data,
                f"Existing PIPE-08 output differs; preserve it and choose a new output path: {output_path}")
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(data)

    phr, shr = output["phr"], output["shr"]
    print(f"PHR: {phr['numerator']}/{phr['denominator']} = {phr['rate']}; "
          f"SHR: {shr['numerator']}/{shr['denominator']} = {shr['rate']}. Wrote {output_path}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
