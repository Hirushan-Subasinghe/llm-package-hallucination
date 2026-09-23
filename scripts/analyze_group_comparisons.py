#!/usr/bin/env python3
"""PIPE-09: reusable grouped-descriptive and statistical-comparison infrastructure.

Builds on the PIPE-07 package/response-level derived datasets and reuses
PIPE-08's loading, cross-validation, and PHR/SHR computation
(scripts/calculate_primary_metrics.py) rather than re-implementing it.

Produces two outputs:

  1. A grouped descriptive summary: one record per requested group value
     (model_condition_id, category, repetition, or model_condition_id x
     category), each with the same PHR/SHR/count fields as PIPE-08 but scoped
     to that group only.
  2. A statistical comparison result across those same groups, for two binary
     outcomes: package-level "confirmed hallucination vs not" and
     response-level "contains a confirmed hallucination vs not".

This script implements its own statistical primitives (Fisher's exact test,
chi-square with an explicit expected-cell assumption gate, a deterministic
Monte Carlo permutation test for a 2xC table when chi-square assumptions
fail, Holm-Bonferroni multiple-comparison correction, odds ratios, and risk
differences with confidence intervals) using only the Python standard
library. No new dependency (e.g. scipy/statsmodels) is added: this
environment has neither installed, and the brief instructs against adding a
dependency without explicit need. A general R>2 x C>2 comparison, and a fully
exact Freeman-Halton RxC p-value, are intentionally NOT implemented (both
would require either a new dependency or a materially harder from-scratch
algorithm this project cannot safely verify); such cases return a structured
not_testable result rather than a fabricated or unverified p-value. Every
statistical comparison this study actually needs is a binary outcome (2 rows)
by up to a handful of groups (C columns), which the implemented 2x2/2xC paths
fully cover.

This script never outputs a ranking, "best"/"worst" label, or a model
comparison verdict -- only neutral per-group descriptive statistics and
pairwise/omnibus comparison numbers (p-values, effect sizes, confidence
intervals). It performs no registry query, model call, or code execution, and
it computes nothing from real v2.2/v2.6 data unless explicitly pointed at
provenance-consistent PIPE-07 outputs by the caller.
"""

import argparse
import json
import math
import random
from collections import defaultdict
from pathlib import Path

import calculate_primary_metrics as metrics_lib

ANALYSIS_VERSION = "pipe-09-group-comparisons-1.1.0"
SUMMARY_FORMAT_VERSION = "pipe-09-grouped-summary-1.1.0"
COMPARISON_FORMAT_VERSION = "pipe-09-comparison-1.1.0"
METHODOLOGY_NOTE = (
    "Neutral descriptive/comparison statistics only; no model ranking, best/worst "
    "label, or ranking field is ever produced. See docs/decision_log.md D033/D037 for "
    "the underlying PHR/SHR denominators and confirmation routing."
)

ALLOWED_GROUP_BY = (
    ("model_condition_id",),
    ("category",),
    ("repetition",),
    ("model_condition_id", "category"),
)
Z_95 = 1.959963984540054  # standard normal 97.5th percentile, for 95% two-sided CIs
DEFAULT_MONTE_CARLO_ITERATIONS = 20000
DEFAULT_MONTE_CARLO_SEED = 1234567891


def require(condition, message):
    if not condition:
        raise ValueError(message)


def write_new_or_identical(path, data):
    """Preserve historical PIPE-09 outputs; reruns may only reproduce bytes."""
    if path.exists():
        require(path.read_bytes() == data,
                f"Existing PIPE-09 output differs; preserve it and choose a new output directory: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


# --------------------------------------------------------------------------
# Pure-stdlib statistical primitives
# --------------------------------------------------------------------------

def _regularized_upper_incomplete_gamma(a, x):
    """Q(a, x): the regularized upper incomplete gamma function, a > 0, x >= 0.

    Standard series (x < a + 1) / continued-fraction (x >= a + 1) evaluation
    (Numerical Recipes ss6.2), used here only for the chi-square upper-tail
    p-value: p = Q(df / 2, statistic / 2).
    """
    require(a > 0, "a must be positive")
    if x < 0:
        return 1.0
    if x == 0:
        return 1.0
    log_gamma_a = math.lgamma(a)
    if x < a + 1.0:
        # Lower incomplete gamma series, then Q = 1 - P.
        term = 1.0 / a
        total = term
        n = a
        for _ in range(500):
            n += 1.0
            term *= x / n
            total += term
            if abs(term) < abs(total) * 1e-16:
                break
        lower = total * math.exp(-x + a * math.log(x) - log_gamma_a)
        return max(0.0, min(1.0, 1.0 - lower))
    # Continued fraction for the upper incomplete gamma (Lentz's algorithm).
    tiny = 1e-300
    b = x + 1.0 - a
    c = 1.0 / tiny
    d = 1.0 / b
    h = d
    for i in range(1, 501):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-16:
            break
    upper = math.exp(-x + a * math.log(x) - log_gamma_a) * h
    return max(0.0, min(1.0, upper))


def normal_cdf(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def chi_square_test(table):
    """Pearson chi-square test on an RxC table (list of row lists of counts).

    Returns (statistic, degrees_of_freedom, p_value, assumptions_met, reason).
    assumptions_met follows Cochran's rule: every expected cell count >= 5.
    """
    rows = len(table)
    cols = len(table[0]) if rows else 0
    require(rows >= 2 and cols >= 2, "chi_square_test requires at least a 2x2 table")
    row_totals = [sum(row) for row in table]
    col_totals = [sum(table[r][c] for r in range(rows)) for c in range(cols)]
    grand_total = sum(row_totals)
    require(grand_total > 0, "chi_square_test requires a non-empty table")

    expected = [[row_totals[r] * col_totals[c] / grand_total for c in range(cols)] for r in range(rows)]
    min_expected = min(expected[r][c] for r in range(rows) for c in range(cols))
    assumptions_met = min_expected >= 5.0
    reason = ("all expected cell counts are >= 5" if assumptions_met else
              f"minimum expected cell count {min_expected:.3f} is below the Cochran threshold of 5")

    statistic = sum(
        (table[r][c] - expected[r][c]) ** 2 / expected[r][c]
        for r in range(rows) for c in range(cols) if expected[r][c] > 0
    )
    df = (rows - 1) * (cols - 1)
    p_value = _regularized_upper_incomplete_gamma(df / 2.0, statistic / 2.0) if df > 0 else None
    return statistic, df, p_value, assumptions_met, reason


def fisher_exact_2x2(a, b, c, d):
    """Exact two-sided Fisher's exact test p-value for a 2x2 table [[a,b],[c,d]]."""
    row1, row2 = a + b, c + d
    col1, col2 = a + c, b + d
    total = row1 + row2
    require(total > 0, "fisher_exact_2x2 requires a non-empty table")

    def hypergeom_prob(x):
        # P(A = x) given fixed margins (row1, row2, col1, total).
        if x < 0 or x > col1 or (row1 - x) < 0 or (row1 - x) > row2:
            return 0.0
        return math.exp(
            math.lgamma(row1 + 1) + math.lgamma(row2 + 1) + math.lgamma(col1 + 1) + math.lgamma(col2 + 1)
            - math.lgamma(total + 1) - math.lgamma(x + 1) - math.lgamma(row1 - x + 1)
            - math.lgamma(col1 - x + 1) - math.lgamma(row2 - col1 + x + 1)
        )

    observed_prob = hypergeom_prob(a)
    low = max(0, col1 - row2)
    high = min(row1, col1)
    epsilon = observed_prob * 1e-7
    p_value = sum(prob for x in range(low, high + 1)
                  if (prob := hypergeom_prob(x)) <= observed_prob + epsilon)
    return max(0.0, min(1.0, p_value))


def odds_ratio_with_ci(a, b, c, d, z=Z_95):
    """Odds ratio and Wald log-OR confidence interval, with Haldane-Anscombe
    continuity correction (+0.5 to every cell) applied only when a zero cell
    would otherwise make the odds ratio or its variance undefined."""
    if 0 in (a, b, c, d):
        a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5
        corrected = True
    else:
        corrected = False
    odds_ratio = (a * d) / (b * c)
    log_or = math.log(odds_ratio)
    standard_error = math.sqrt(1.0 / a + 1.0 / b + 1.0 / c + 1.0 / d)
    low = math.exp(log_or - z * standard_error)
    high = math.exp(log_or + z * standard_error)
    return {"odds_ratio": odds_ratio, "ci_low": low, "ci_high": high,
            "haldane_anscombe_correction_applied": corrected}


def _wilson_score_interval(successes, total, z=Z_95):
    if total == 0:
        return None, None, None
    p_hat = successes / total
    denominator = 1 + z * z / total
    center = (p_hat + z * z / (2 * total)) / denominator
    half_width = (z * math.sqrt(p_hat * (1 - p_hat) / total + z * z / (4 * total * total))) / denominator
    return p_hat, max(0.0, center - half_width), min(1.0, center + half_width)


def risk_difference_with_ci(successes_a, total_a, successes_b, total_b, z=Z_95):
    """Risk (rate) difference p_a - p_b with a Newcombe/Wilson-score confidence interval."""
    require(total_a > 0 and total_b > 0, "risk_difference_with_ci requires non-empty groups")
    p_a, low_a, high_a = _wilson_score_interval(successes_a, total_a, z)
    p_b, low_b, high_b = _wilson_score_interval(successes_b, total_b, z)
    difference = p_a - p_b
    low = difference - math.sqrt((p_a - low_a) ** 2 + (high_b - p_b) ** 2)
    high = difference + math.sqrt((high_a - p_a) ** 2 + (p_b - low_b) ** 2)
    return {"risk_difference": difference, "ci_low": max(-1.0, low), "ci_high": min(1.0, high)}


def holm_correction(p_values):
    """Holm-Bonferroni step-down adjusted p-values, preserving input order."""
    m = len(p_values)
    if m == 0:
        return []
    indexed = sorted(range(m), key=lambda i: p_values[i])
    adjusted = [None] * m
    running_max = 0.0
    for rank, index in enumerate(indexed):
        value = min(1.0, (m - rank) * p_values[index])
        running_max = max(running_max, value)
        adjusted[index] = running_max
    return adjusted


def monte_carlo_2xc_pvalue(table, iterations, seed):
    """Deterministic permutation p-value for a 2xC table under fixed margins.

    Pools all N = sum(column totals) labeled units (label = column of origin)
    and repeatedly draws, without replacement, a random subset of size
    row1_total to play the role of "row-1" successes, recomputing the
    chi-square-style statistic on each resample. This is the exact conditional
    randomization distribution for a 2xC table given fixed margins (a Monte
    Carlo approximation of the Freeman-Halton/Fisher-exact RxC p-value,
    specialized to two rows). Seeded for full rerun determinism.
    """
    rows = len(table)
    require(rows == 2, "monte_carlo_2xc_pvalue only supports two-row tables")
    cols = len(table[0])
    col_totals = [table[0][c] + table[1][c] for c in range(cols)]
    row1_total = sum(table[0])
    pooled = []
    for column_index, count in enumerate(col_totals):
        pooled.extend([column_index] * count)
    total = len(pooled)
    require(total > 0, "monte_carlo_2xc_pvalue requires a non-empty table")
    if row1_total == 0 or row1_total == total:
        # Only one table is consistent with these margins (every unit is a
        # "row 2" or every unit is a "row 1"), so the observed table is the
        # entire null distribution: statistic 0, p-value 1 by definition.
        return 0.0, 1.0

    def statistic_of(row1_counts):
        resampled = [row1_counts, [col_totals[c] - row1_counts[c] for c in range(cols)]]
        statistic, _df, _p, _ok, _reason = chi_square_test(resampled)
        return statistic

    observed_statistic = statistic_of(table[0])
    generator = random.Random(seed)
    at_least_as_extreme = 0
    for _ in range(iterations):
        sample = generator.sample(pooled, row1_total)
        row1_counts = [0] * cols
        for column_index in sample:
            row1_counts[column_index] += 1
        if statistic_of(row1_counts) >= observed_statistic - 1e-12:
            at_least_as_extreme += 1
    p_value = at_least_as_extreme / iterations
    return observed_statistic, p_value


# --------------------------------------------------------------------------
# Grouping
# --------------------------------------------------------------------------

def parse_group_by(raw):
    fields = tuple(part.strip() for part in raw.split(",") if part.strip())
    require(fields in ALLOWED_GROUP_BY,
            f"--group-by must be one of {['+'.join(g) for g in ALLOWED_GROUP_BY]}, got {raw!r}")
    return fields


def group_key(response_row, group_by):
    return tuple(response_row[field] for field in group_by)


def build_group_index(response_by_run, packages_by_run, group_by):
    groups = defaultdict(lambda: {"run_ids": [], "package_rows": []})
    for run_id, response_row in response_by_run.items():
        key = group_key(response_row, group_by)
        groups[key]["run_ids"].append(run_id)
        groups[key]["package_rows"].extend(packages_by_run.get(run_id, []))
    return groups


def summarize_group(group_by, key, run_ids, package_rows, response_by_run):
    response_subset = {run_id: response_by_run[run_id] for run_id in run_ids}
    package_subset = {(row["run_id"], row["normalized_package"]): row for row in package_rows}
    packages_by_run_subset = defaultdict(list)
    for row in package_rows:
        packages_by_run_subset[row["run_id"]].append(row)
    metrics = metrics_lib.compute_metrics(package_subset, response_subset, packages_by_run_subset)
    record = {"group": dict(zip(group_by, key))}
    record.update(metrics)
    ineligible_response_count = len(run_ids) - metrics["eligible_response_count"]
    record["ineligible_response_count"] = ineligible_response_count
    return record


def build_grouped_summary(response_by_run, packages_by_run, group_by):
    groups = build_group_index(response_by_run, packages_by_run, group_by)
    records = [
        summarize_group(group_by, key, value["run_ids"], value["package_rows"], response_by_run)
        for key, value in groups.items()
    ]
    return sorted(records, key=lambda record: tuple(str(record["group"][field]) for field in group_by))


# --------------------------------------------------------------------------
# Comparisons
# --------------------------------------------------------------------------

def compare_two_groups(label_a, counts_a, label_b, counts_b):
    successes_a, total_a = counts_a
    successes_b, total_b = counts_b
    if total_a == 0 or total_b == 0:
        return {"method": "not_testable", "reason": f"group {label_a if total_a == 0 else label_b} has zero total"}
    a, b = successes_a, total_a - successes_a
    c, d = successes_b, total_b - successes_b
    p_value = fisher_exact_2x2(a, b, c, d)
    return {
        "method": "fisher_exact",
        "groups": [label_a, label_b],
        "table": [[a, b], [c, d]],
        "p_value": p_value,
        "odds_ratio": odds_ratio_with_ci(a, b, c, d),
        "risk_difference": risk_difference_with_ci(successes_a, total_a, successes_b, total_b),
    }


def compare_groups(group_counts, monte_carlo_iterations, monte_carlo_seed):
    """group_counts: ordered dict label -> (successes, total)."""
    usable = [(label, counts) for label, counts in group_counts.items() if counts[1] > 0]
    excluded = [label for label, counts in group_counts.items() if counts[1] == 0]
    if len(usable) < 2:
        return {"method": "not_testable",
                "reason": f"fewer than two groups with a non-zero denominator ({len(usable)} usable)",
                "excluded_zero_total_groups": excluded}
    if len(usable) == 2:
        (label_a, counts_a), (label_b, counts_b) = usable
        result = compare_two_groups(label_a, counts_a, label_b, counts_b)
        result["excluded_zero_total_groups"] = excluded
        return result

    labels = [label for label, _ in usable]
    table = [[counts[0] for _, counts in usable], [counts[1] - counts[0] for _, counts in usable]]
    statistic, df, chi_p, assumptions_met, reason = chi_square_test(table)
    if assumptions_met:
        omnibus = {"method": "chi_square", "groups": labels, "table": table,
                   "statistic": statistic, "degrees_of_freedom": df, "p_value": chi_p,
                   "assumptions_met": True, "assumption_reason": reason}
    else:
        mc_statistic, mc_p = monte_carlo_2xc_pvalue(table, monte_carlo_iterations, monte_carlo_seed)
        omnibus = {"method": "monte_carlo_permutation", "groups": labels, "table": table,
                   "statistic": mc_statistic, "p_value": mc_p,
                   "iterations": monte_carlo_iterations, "seed": monte_carlo_seed,
                   "assumptions_met": False, "assumption_reason": reason,
                   "chi_square_reference_statistic": statistic, "chi_square_reference_p_value": chi_p}

    pairwise = []
    raw_p_values = []
    for i in range(len(usable)):
        for j in range(i + 1, len(usable)):
            label_a, counts_a = usable[i]
            label_b, counts_b = usable[j]
            pair_result = compare_two_groups(label_a, counts_a, label_b, counts_b)
            pairwise.append(pair_result)
            raw_p_values.append(pair_result.get("p_value", 1.0))
    adjusted = holm_correction(raw_p_values)
    for pair_result, adjusted_p in zip(pairwise, adjusted):
        pair_result["holm_adjusted_p_value"] = adjusted_p

    return {"omnibus": omnibus, "pairwise_comparisons": pairwise,
            "multiple_comparison_correction": "holm", "excluded_zero_total_groups": excluded}


def build_comparisons(grouped_summary, monte_carlo_iterations, monte_carlo_seed):
    def label_of(record):
        return "|".join(str(record["group"][field]) for field in record["group"])

    package_level_counts = {label_of(r): (r["phr"]["numerator"], r["phr"]["denominator"]) for r in grouped_summary}
    response_level_counts = {label_of(r): (r["shr"]["numerator"], r["shr"]["denominator"]) for r in grouped_summary}

    return {
        "package_level_confirmed_vs_not": compare_groups(
            package_level_counts, monte_carlo_iterations, monte_carlo_seed),
        "response_level_contains_confirmed_vs_not": compare_groups(
            response_level_counts, monte_carlo_iterations, monte_carlo_seed),
    }


# --------------------------------------------------------------------------
# I/O
# --------------------------------------------------------------------------

def load_inputs(package_dataset_path, response_dataset_path):
    _pkg_doc, _pkg_records, package_by_key, package_hash = metrics_lib.load_package_dataset(package_dataset_path)
    _resp_doc, _resp_records, response_by_run, response_hash = metrics_lib.load_response_dataset(response_dataset_path)
    packages_by_run = metrics_lib.cross_validate(package_by_key, response_by_run)
    return package_by_key, response_by_run, packages_by_run, package_hash, response_hash


def run(package_dataset_path, response_dataset_path, group_by_raw, version_label,
        monte_carlo_iterations=DEFAULT_MONTE_CARLO_ITERATIONS, monte_carlo_seed=DEFAULT_MONTE_CARLO_SEED):
    group_by = parse_group_by(group_by_raw)
    package_by_key, response_by_run, packages_by_run, package_hash, response_hash = load_inputs(
        package_dataset_path, response_dataset_path)
    grouped_summary = build_grouped_summary(response_by_run, packages_by_run, group_by)
    comparisons = build_comparisons(grouped_summary, monte_carlo_iterations, monte_carlo_seed)

    provenance = {"package_dataset_input_hash": package_hash, "response_dataset_input_hash": response_hash}
    summary_output = {
        "format_version": SUMMARY_FORMAT_VERSION, "analysis_version": ANALYSIS_VERSION,
        "source_version_label": version_label, "group_by": list(group_by),
        "methodology_note": METHODOLOGY_NOTE, "provenance": provenance, "records": grouped_summary,
    }
    comparison_output = {
        "format_version": COMPARISON_FORMAT_VERSION, "analysis_version": ANALYSIS_VERSION,
        "source_version_label": version_label, "group_by": list(group_by),
        "methodology_note": METHODOLOGY_NOTE, "provenance": provenance, "comparisons": comparisons,
    }
    return summary_output, comparison_output


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--package-dataset", required=True)
    parser.add_argument("--response-dataset", required=True)
    parser.add_argument("--group-by", required=True,
                         help="One of: model_condition_id | category | repetition | model_condition_id,category")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--version-label", required=True)
    parser.add_argument("--monte-carlo-iterations", type=int, default=DEFAULT_MONTE_CARLO_ITERATIONS)
    parser.add_argument("--monte-carlo-seed", type=int, default=DEFAULT_MONTE_CARLO_SEED)
    args = parser.parse_args(argv)

    summary_output, comparison_output = run(
        args.package_dataset, args.response_dataset, args.group_by, args.version_label,
        args.monte_carlo_iterations, args.monte_carlo_seed)

    output_dir = Path(args.output_dir)
    summary_path = output_dir / f"grouped_summary_{args.version_label}.json"
    comparison_path = output_dir / f"group_comparisons_{args.version_label}.json"
    write_new_or_identical(summary_path, (json.dumps(summary_output, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    write_new_or_identical(comparison_path, (json.dumps(comparison_output, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))

    print(f"Wrote {len(summary_output['records'])} group summary row(s) to {summary_path} "
          f"and comparisons to {comparison_path}. No ranking was produced.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
