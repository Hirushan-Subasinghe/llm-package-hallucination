#!/usr/bin/env python3
"""Synthetic, offline tests for PIPE-09 grouped descriptive/statistical-comparison infrastructure.

All fixtures are synthetic and invented for this test only. No real v2.2 or
v2.6 data is read here, and no model ranking is asserted or produced.
"""

import json
import math
import sys
import tempfile
import unittest
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import analyze_group_comparisons as grp


def package_row(run_id, normalized_package, meta, occurrence_count=1,
                 validation_status="exists", classification="VALID"):
    collection_status = meta["collection_status"]
    metric_eligible = collection_status == "completed"
    return {
        "run_id": run_id, "collection_order": meta["collection_order"],
        "model_condition_id": meta["model_condition_id"], "provider": "OpenRouter",
        "model": "synthetic-model", "task_id": meta["task_id"], "category": meta["category"],
        "repetition": meta["repetition"], "collection_status": collection_status,
        "completion_status": ("COMPLETED" if collection_status == "completed"
                               else "TRUNCATED" if collection_status == "truncated" else None),
        "truncated": collection_status == "truncated",
        "normalized_package": normalized_package, "occurrence_count": occurrence_count,
        "source_types": ["es_import"], "validation_status": validation_status,
        "research_classification": classification,
        "adjudication_status": "REVIEWED" if classification not in (None, "VALID") else
                                ("AUTO_VALID" if classification == "VALID" else "VALIDATION_UNRESOLVED"),
        "primary_confirmed_hallucination": classification == "CONFIRMED_HALLUCINATION",
        "primary_confirmation_path": "PIPE05_REVIEWED" if classification == "CONFIRMED_HALLUCINATION" else "NONE",
        "primary_confirmation_version": "synthetic-pipe05" if classification == "CONFIRMED_HALLUCINATION" else None,
        "primary_confirmation_source_hash": "e" * 64 if classification == "CONFIRMED_HALLUCINATION" else None,
        "pipe05b_adjudication_outcome": None,
        "metric_eligible": metric_eligible,
        "provenance": [f"synthetic://pipe-05/{run_id}/{normalized_package}"],
    }


def response_row_from_packages(run_id, meta, packages):
    collection_status = meta["collection_status"]
    confirmed = sum(1 for row in packages if row["primary_confirmed_hallucination"])
    ambiguous = sum(1 for row in packages if row["research_classification"] == "AMBIGUOUS")
    unresolved = sum(1 for row in packages if row["validation_status"] == "unresolved")
    return {
        "run_id": run_id, "collection_order": meta["collection_order"],
        "model_condition_id": meta["model_condition_id"], "task_id": meta["task_id"],
        "category": meta["category"], "repetition": meta["repetition"],
        "collection_status": collection_status,
        "completion_status": ("COMPLETED" if collection_status == "completed"
                               else "TRUNCATED" if collection_status == "truncated" else None),
        "truncated": collection_status == "truncated",
        "package_reference_count": sum(row["occurrence_count"] for row in packages),
        "unique_package_count": len(packages),
        "confirmed_hallucinated_package_count": confirmed,
        "ambiguous_package_count": ambiguous,
        "unresolved_package_count": unresolved,
        "contains_confirmed_package_hallucination": confirmed > 0,
        "metric_eligible": collection_status == "completed",
    }


class Scenario:
    def __init__(self):
        self.package_rows = []
        self.response_meta = {}
        self._order = 0

    def response(self, run_id, collection_status="completed", model_condition_id="M1",
                 task_id="TASK-01", category="AUTH-FED", repetition="R01"):
        self._order += 1
        self.response_meta[run_id] = {
            "collection_status": collection_status, "model_condition_id": model_condition_id,
            "task_id": task_id, "category": category, "repetition": repetition,
            "collection_order": self._order,
        }
        return self

    def package(self, run_id, normalized_package, **kwargs):
        self.package_rows.append(package_row(run_id, normalized_package, self.response_meta[run_id], **kwargs))
        return self

    def response_rows(self):
        by_run = defaultdict(list)
        for row in self.package_rows:
            by_run[row["run_id"]].append(row)
        return [response_row_from_packages(run_id, meta, by_run.get(run_id, []))
                for run_id, meta in self.response_meta.items()]

    def write(self, tmp_path):
        base = Path(tmp_path)
        package_path = base / "package_dataset.json"
        response_path = base / "response_dataset.json"
        envelope_extra = {"inventory_input_hash": "a" * 64, "unique_packages_input_hash": "b" * 64,
                           "validation_joined_input_hash": "c" * 64, "classification_joined_input_hash": "d" * 64}
        package_path.write_text(json.dumps({"format_version": "pipe-07-analysis-1.1.0", **envelope_extra,
                                             "records": self.package_rows}))
        response_path.write_text(json.dumps({"format_version": "pipe-07-analysis-1.1.0", **envelope_extra,
                                              "records": self.response_rows()}))
        return package_path, response_path


class TempDirCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp_path = Path(self._tmp.name)

    def run_group(self, scenario, group_by, **kwargs):
        package_path, response_path = scenario.write(self.tmp_path)
        return grp.run(package_path, response_path, group_by, "synthetic-test", **kwargs)


def confirmed_response(run_id, model, category, repetition="R01"):
    def apply(scenario):
        scenario.response(run_id, "completed", model_condition_id=model, category=category, repetition=repetition)
        scenario.package(run_id, f"fake-{run_id}", validation_status="not_found",
                          classification="CONFIRMED_HALLUCINATION")
        return scenario
    return apply


def valid_response(run_id, model, category, repetition="R01"):
    def apply(scenario):
        scenario.response(run_id, "completed", model_condition_id=model, category=category, repetition=repetition)
        scenario.package(run_id, f"real-{run_id}", classification="VALID")
        return scenario
    return apply


class DescriptivePHRByModelTests(TempDirCase):
    def test_descriptive_phr_by_model(self):
        scenario = Scenario()
        for i in range(5):
            valid_response(f"M1-R{i}", "M1", "AUTH-FED")(scenario)
        for i in range(5):
            confirmed_response(f"M2-R{i}", "M2", "AUTH-FED")(scenario)
        summary, _comparisons = self.run_group(scenario, "model_condition_id")
        by_model = {tuple(r["group"].values()): r for r in summary["records"]}
        self.assertEqual(by_model[("M1",)]["phr"], {"numerator": 0, "denominator": 5, "rate": 0.0})
        self.assertEqual(by_model[("M2",)]["phr"], {"numerator": 5, "denominator": 5, "rate": 1.0})


class DescriptiveSHRByModelTests(TempDirCase):
    def test_descriptive_shr_by_model(self):
        scenario = Scenario()
        valid_response("R1", "M1", "AUTH-FED")(scenario)
        confirmed_response("R2", "M1", "AUTH-FED")(scenario)
        summary, _c = self.run_group(scenario, "model_condition_id")
        record = summary["records"][0]
        self.assertEqual(record["shr"], {"numerator": 1, "denominator": 2, "rate": 0.5})


class DescriptiveByCategoryTests(TempDirCase):
    def test_descriptive_by_category(self):
        scenario = Scenario()
        valid_response("R1", "M1", "AUTH-FED")(scenario)
        confirmed_response("R2", "M1", "PKI-CRYPTO")(scenario)
        summary, _c = self.run_group(scenario, "category")
        groups = {tuple(r["group"].values()) for r in summary["records"]}
        self.assertEqual(groups, {("AUTH-FED",), ("PKI-CRYPTO",)})


class ZeroEventGroupsTests(TempDirCase):
    def test_zero_event_groups(self):
        scenario = Scenario()
        for i in range(3):
            valid_response(f"M1-{i}", "M1", "AUTH-FED")(scenario)
        for i in range(3):
            valid_response(f"M2-{i}", "M2", "AUTH-FED")(scenario)
        summary, comparisons = self.run_group(scenario, "model_condition_id")
        for record in summary["records"]:
            self.assertEqual(record["phr"]["numerator"], 0)
        result = comparisons["comparisons"]["package_level_confirmed_vs_not"]
        self.assertEqual(result["method"], "fisher_exact")
        self.assertAlmostEqual(result["p_value"], 1.0, places=9)


class OneGroupNotTestableTests(TempDirCase):
    def test_single_group_not_testable(self):
        scenario = Scenario()
        valid_response("R1", "M1", "AUTH-FED")(scenario)
        _summary, comparisons = self.run_group(scenario, "model_condition_id")
        result = comparisons["comparisons"]["package_level_confirmed_vs_not"]
        self.assertEqual(result["method"], "not_testable")
        self.assertIn("reason", result)


class FisherTwoByTwoPathTests(TempDirCase):
    def test_fisher_exact_used_for_two_groups(self):
        scenario = Scenario()
        for i in range(4):
            valid_response(f"M1-{i}", "M1", "AUTH-FED")(scenario)
        confirmed_response("M2-0", "M2", "AUTH-FED")(scenario)
        for i in range(1, 4):
            valid_response(f"M2-{i}", "M2", "AUTH-FED")(scenario)
        _summary, comparisons = self.run_group(scenario, "model_condition_id")
        result = comparisons["comparisons"]["package_level_confirmed_vs_not"]
        self.assertEqual(result["method"], "fisher_exact")
        self.assertIn("odds_ratio", result)
        self.assertIn("risk_difference", result)


class ChiSquareAssumptionTests(TempDirCase):
    def test_chi_square_allowed_when_assumptions_hold(self):
        statistic, df, p_value, assumptions_met, reason = grp.chi_square_test(
            [[20, 20, 20], [80, 80, 80]])
        self.assertTrue(assumptions_met)
        self.assertIsNotNone(p_value)

    def test_chi_square_fallback_when_assumptions_fail(self):
        scenario = Scenario()
        confirmed_response("A1", "M1", "AUTH-FED")(scenario)
        valid_response("B1", "M2", "AUTH-FED")(scenario)
        valid_response("C1", "M3", "AUTH-FED")(scenario)
        _summary, comparisons = self.run_group(scenario, "model_condition_id",
                                                 monte_carlo_iterations=500, monte_carlo_seed=1)
        result = comparisons["comparisons"]["package_level_confirmed_vs_not"]
        self.assertIn(result["omnibus"]["method"], ("monte_carlo_permutation",))
        self.assertFalse(result["omnibus"]["assumptions_met"])


class SparseTableTests(TempDirCase):
    def test_sparse_rxc_table_handled_safely(self):
        scenario = Scenario()
        confirmed_response("A1", "M1", "AUTH-FED")(scenario)
        for i in range(2):
            valid_response(f"B{i}", "M2", "AUTH-FED")(scenario)
        for i in range(2):
            valid_response(f"C{i}", "M3", "AUTH-FED")(scenario)
        for i in range(2):
            valid_response(f"D{i}", "M4", "AUTH-FED")(scenario)
        _summary, comparisons = self.run_group(scenario, "model_condition_id",
                                                 monte_carlo_iterations=300, monte_carlo_seed=7)
        result = comparisons["comparisons"]["package_level_confirmed_vs_not"]
        self.assertIn("omnibus", result)
        self.assertGreaterEqual(result["omnibus"]["p_value"], 0.0)
        self.assertLessEqual(result["omnibus"]["p_value"], 1.0)


class OddsRatioTests(unittest.TestCase):
    def test_odds_ratio_basic(self):
        result = grp.odds_ratio_with_ci(10, 10, 3, 17)
        self.assertAlmostEqual(result["odds_ratio"], (10 * 17) / (10 * 3))
        self.assertLess(result["ci_low"], result["odds_ratio"])
        self.assertGreater(result["ci_high"], result["odds_ratio"])

    def test_odds_ratio_zero_cell_uses_haldane_anscombe(self):
        result = grp.odds_ratio_with_ci(5, 0, 3, 17)
        self.assertTrue(result["haldane_anscombe_correction_applied"])


class RiskDifferenceTests(unittest.TestCase):
    def test_risk_difference_basic(self):
        result = grp.risk_difference_with_ci(10, 20, 3, 20)
        self.assertAlmostEqual(result["risk_difference"], 0.5 - 0.15)
        self.assertLessEqual(result["ci_low"], result["risk_difference"])
        self.assertGreaterEqual(result["ci_high"], result["risk_difference"])


class ConfidenceIntervalBehaviorTests(unittest.TestCase):
    def test_ci_widens_with_smaller_sample(self):
        small = grp.risk_difference_with_ci(1, 2, 0, 2)
        large = grp.risk_difference_with_ci(50, 100, 0, 100)
        small_width = small["ci_high"] - small["ci_low"]
        large_width = large["ci_high"] - large["ci_low"]
        self.assertGreater(small_width, large_width)


class MultipleComparisonCorrectionTests(TempDirCase):
    def test_holm_correction_applied_and_ge_raw(self):
        scenario = Scenario()
        confirmed_response("A1", "M1", "AUTH-FED")(scenario)
        confirmed_response("A2", "M1", "AUTH-FED")(scenario)
        for i in range(5):
            valid_response(f"B{i}", "M2", "AUTH-FED")(scenario)
        for i in range(5):
            valid_response(f"C{i}", "M3", "AUTH-FED")(scenario)
        _summary, comparisons = self.run_group(scenario, "model_condition_id",
                                                 monte_carlo_iterations=200, monte_carlo_seed=3)
        result = comparisons["comparisons"]["package_level_confirmed_vs_not"]
        self.assertEqual(result["multiple_comparison_correction"], "holm")
        for pair in result["pairwise_comparisons"]:
            self.assertGreaterEqual(pair["holm_adjusted_p_value"], pair["p_value"] - 1e-12)

    def test_holm_correction_function_matches_known_case(self):
        adjusted = grp.holm_correction([0.01, 0.04, 0.03, 0.20])
        self.assertEqual(adjusted, [0.04, 0.09, 0.09, 0.20])


class IncompleteGroupCoverageTests(TempDirCase):
    def test_incomplete_group_coverage_excludes_zero_total(self):
        scenario = Scenario()
        for i in range(3):
            valid_response(f"M1-{i}", "M1", "AUTH-FED")(scenario)
        _summary, comparisons = self.run_group(scenario, "model_condition_id")
        result = comparisons["comparisons"]["package_level_confirmed_vs_not"]
        self.assertEqual(result["method"], "not_testable")


class TruncationExclusionTests(TempDirCase):
    def test_truncated_rows_excluded_through_metric_eligible(self):
        scenario = Scenario()
        for i in range(3):
            valid_response(f"M1-{i}", "M1", "AUTH-FED")(scenario)
        scenario.response("M1-T", "truncated", model_condition_id="M1", category="AUTH-FED")
        scenario.package("M1-T", "fake-trunc-pkg", validation_status="not_found",
                          classification="CONFIRMED_HALLUCINATION")
        summary, _c = self.run_group(scenario, "model_condition_id")
        record = summary["records"][0]
        self.assertEqual(record["phr"]["denominator"], 3)
        self.assertEqual(record["truncated_response_count"], 1)


class ZeroPackageShrEligibleTests(TempDirCase):
    def test_zero_package_completed_response_remains_shr_eligible(self):
        scenario = Scenario()
        scenario.response("R1", "completed", model_condition_id="M1", category="AUTH-FED")  # no packages
        summary, _c = self.run_group(scenario, "model_condition_id")
        record = summary["records"][0]
        self.assertEqual(record["shr"]["denominator"], 1)
        self.assertEqual(record["eligible_response_count"], 1)


class NumeratorExclusionGroupTests(TempDirCase):
    def test_ambiguous_and_unresolved_excluded_from_confirmed_numerator(self):
        scenario = Scenario()
        scenario.response("R1", "completed", model_condition_id="M1", category="AUTH-FED")
        scenario.package("R1", "maybe-pkg", validation_status="not_found", classification="AMBIGUOUS")
        scenario.response("R2", "completed", model_condition_id="M1", category="AUTH-FED")
        scenario.package("R2", "flaky-pkg", validation_status="unresolved", classification=None)
        summary, _c = self.run_group(scenario, "model_condition_id")
        record = summary["records"][0]
        self.assertEqual(record["phr"]["numerator"], 0)
        self.assertEqual(record["ambiguous_package_row_count"], 1)
        self.assertEqual(record["unresolved_package_row_count"], 1)


class DeterministicOrderingTests(TempDirCase):
    def test_deterministic_ordering_of_groups(self):
        scenario = Scenario()
        valid_response("R1", "M3", "AUTH-FED")(scenario)
        valid_response("R2", "M1", "AUTH-FED")(scenario)
        valid_response("R3", "M2", "AUTH-FED")(scenario)
        summary, _c = self.run_group(scenario, "model_condition_id")
        models = [tuple(r["group"].values()) for r in summary["records"]]
        self.assertEqual(models, [("M1",), ("M2",), ("M3",)])


class RerunDeterminismTests(TempDirCase):
    def test_rerun_determinism(self):
        scenario = Scenario()
        confirmed_response("A1", "M1", "AUTH-FED")(scenario)
        valid_response("B1", "M2", "AUTH-FED")(scenario)
        valid_response("C1", "M3", "AUTH-FED")(scenario)
        package_path, response_path = scenario.write(self.tmp_path)
        first = grp.run(package_path, response_path, "model_condition_id", "synthetic-test",
                         monte_carlo_iterations=300, monte_carlo_seed=99)
        second = grp.run(package_path, response_path, "model_condition_id", "synthetic-test",
                          monte_carlo_iterations=300, monte_carlo_seed=99)
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))


class ExplicitInputsOnlyTests(TempDirCase):
    def test_cli_requires_explicit_paths(self):
        with self.assertRaises(SystemExit):
            grp.main([])

    def test_invalid_group_by_rejected(self):
        scenario = Scenario()
        valid_response("R1", "M1", "AUTH-FED")(scenario)
        with self.assertRaises(ValueError):
            self.run_group(scenario, "task_id")

    def test_cli_end_to_end(self):
        scenario = Scenario()
        valid_response("R1", "M1", "AUTH-FED")(scenario)
        confirmed_response("R2", "M2", "AUTH-FED")(scenario)
        package_path, response_path = scenario.write(self.tmp_path)
        output_dir = self.tmp_path / "out"
        result = grp.main([
            "--package-dataset", str(package_path),
            "--response-dataset", str(response_path),
            "--group-by", "model_condition_id",
            "--output-dir", str(output_dir),
            "--version-label", "synthetic-test",
        ])
        self.assertEqual(result, 0)
        self.assertTrue((output_dir / "grouped_summary_synthetic-test.json").exists())
        self.assertTrue((output_dir / "group_comparisons_synthetic-test.json").exists())


class ProvenanceHashTests(TempDirCase):
    def test_provenance_hashes_present(self):
        import hashlib
        scenario = Scenario()
        valid_response("R1", "M1", "AUTH-FED")(scenario)
        package_path, response_path = scenario.write(self.tmp_path)
        summary, comparisons = grp.run(package_path, response_path, "model_condition_id", "synthetic-test")
        expected_pkg_hash = hashlib.sha256(package_path.read_bytes()).hexdigest()
        self.assertEqual(summary["provenance"]["package_dataset_input_hash"], expected_pkg_hash)
        self.assertEqual(comparisons["provenance"]["package_dataset_input_hash"], expected_pkg_hash)


class NoRankingOutputTests(TempDirCase):
    def test_no_ranking_field_anywhere_in_output(self):
        scenario = Scenario()
        for i in range(3):
            confirmed_response(f"A{i}", "M1", "AUTH-FED")(scenario)
        for i in range(3):
            valid_response(f"B{i}", "M2", "AUTH-FED")(scenario)
        for i in range(3):
            valid_response(f"C{i}", "M3", "AUTH-FED")(scenario)
        summary, comparisons = self.run_group(scenario, "model_condition_id",
                                                monte_carlo_iterations=200, monte_carlo_seed=5)
        forbidden_keys = ("rank", "ranking", "best", "worst", "winner", "best_model", "worst_model")

        def walk_keys(node):
            if isinstance(node, dict):
                for key, value in node.items():
                    if key != "methodology_note":
                        yield key
                        yield from walk_keys(value)
            elif isinstance(node, list):
                for item in node:
                    yield from walk_keys(item)

        found_keys = {key.lower() for key in walk_keys(summary)} | {key.lower() for key in walk_keys(comparisons)}
        for word in forbidden_keys:
            self.assertNotIn(word, found_keys, f"Forbidden ranking-like key {word!r} found in PIPE-09 output")


if __name__ == "__main__":
    unittest.main()
