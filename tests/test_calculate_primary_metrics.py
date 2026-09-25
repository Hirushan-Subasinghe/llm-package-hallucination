#!/usr/bin/env python3
"""Synthetic, offline tests for PIPE-08 primary PHR/SHR metric calculation.

All fixtures are synthetic and invented for this test only. No real v2.2 or
v2.6 data is read here, and no real finding is scored or measured.
"""

import copy
import json
import sys
import tempfile
import unittest
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import calculate_primary_metrics as calc

FIXED_TIMESTAMP = "2026-09-22T00:00:00Z"


def package_row(run_id, normalized_package, meta, occurrence_count=1,
                 validation_status="exists", classification="VALID",
                 adjudication_status="AUTO_VALID"):
    collection_status = meta["collection_status"]
    metric_eligible = collection_status == "completed"
    return {
        "run_id": run_id, "collection_order": 1,
        "model_condition_id": meta["model_condition_id"], "provider": "OpenRouter",
        "model": "synthetic-model", "task_id": meta["task_id"], "category": meta["category"],
        "repetition": meta["repetition"], "collection_status": collection_status,
        "completion_status": ("COMPLETED" if collection_status == "completed"
                               else "TRUNCATED" if collection_status == "truncated" else None),
        "truncated": collection_status == "truncated",
        "normalized_package": normalized_package, "occurrence_count": occurrence_count,
        "source_types": ["es_import"], "validation_status": validation_status,
        "research_classification": classification, "adjudication_status": adjudication_status,
        "primary_confirmed_hallucination": classification == "CONFIRMED_HALLUCINATION",
        "primary_confirmation_path": ("PIPE05_REVIEWED" if classification == "CONFIRMED_HALLUCINATION" else "NONE"),
        "primary_confirmation_version": ("synthetic-pipe05" if classification == "CONFIRMED_HALLUCINATION" else None),
        "primary_confirmation_source_hash": ("e" * 64 if classification == "CONFIRMED_HALLUCINATION" else None),
        "pipe05b_adjudication_outcome": None,
        "metric_eligible": metric_eligible,
        "provenance": [f"synthetic://pipe-05/{run_id}/{normalized_package}"],
    }


def response_row_from_packages(run_id, meta, packages):
    collection_status = meta["collection_status"]
    package_reference_count = sum(row["occurrence_count"] for row in packages)
    unique_package_count = len(packages)
    confirmed = sum(1 for row in packages if row["primary_confirmed_hallucination"])
    ambiguous = sum(1 for row in packages if row["research_classification"] == "AMBIGUOUS")
    unresolved = sum(1 for row in packages if row["validation_status"] == "unresolved")
    return {
        "run_id": run_id, "collection_order": 1, "model_condition_id": meta["model_condition_id"],
        "task_id": meta["task_id"], "category": meta["category"], "repetition": meta["repetition"],
        "collection_status": collection_status,
        "completion_status": ("COMPLETED" if collection_status == "completed"
                               else "TRUNCATED" if collection_status == "truncated" else None),
        "truncated": collection_status == "truncated",
        "package_reference_count": package_reference_count,
        "unique_package_count": unique_package_count,
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

    def response(self, run_id, collection_status="completed", model_condition_id="M1",
                 task_id="TASK-01", category="AUTH-FED", repetition="R01"):
        self.response_meta[run_id] = {
            "collection_status": collection_status, "model_condition_id": model_condition_id,
            "task_id": task_id, "category": category, "repetition": repetition,
        }
        return self

    def package(self, run_id, normalized_package, **kwargs):
        row = package_row(run_id, normalized_package, self.response_meta[run_id], **kwargs)
        self.package_rows.append(row)
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
        package_path.write_text(json.dumps({
            "format_version": "pipe-07-analysis-1.1.0",
            "inventory_input_hash": "a" * 64, "unique_packages_input_hash": "b" * 64,
            "validation_joined_input_hash": "c" * 64, "classification_joined_input_hash": "d" * 64,
            "records": self.package_rows,
        }))
        response_path.write_text(json.dumps({
            "format_version": "pipe-07-analysis-1.1.0",
            "inventory_input_hash": "a" * 64, "unique_packages_input_hash": "b" * 64,
            "validation_joined_input_hash": "c" * 64, "classification_joined_input_hash": "d" * 64,
            "records": self.response_rows(),
        }))
        return package_path, response_path


class TempDirCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp_path = Path(self._tmp.name)

    def run_calc(self, scenario, generated_at=FIXED_TIMESTAMP):
        package_path, response_path = scenario.write(self.tmp_path)
        return calc.calculate(package_path, response_path, "synthetic-test", generated_at)


class PHRBasicTests(TempDirCase):
    def test_phr_no_hallucinations(self):
        scenario = Scenario().response("RUN-1").package("RUN-1", "express", classification="VALID")
        output = self.run_calc(scenario)
        self.assertEqual(output["phr"], {"numerator": 0, "denominator": 1, "rate": 0.0})

    def test_phr_one_confirmed_hallucination(self):
        scenario = Scenario().response("RUN-1").package("RUN-1", "totally-fake-pkg",
                                                          validation_status="not_found",
                                                          classification="CONFIRMED_HALLUCINATION")
        output = self.run_calc(scenario)
        self.assertEqual(output["phr"], {"numerator": 1, "denominator": 1, "rate": 1.0})


class RepeatedAndMultiplePackageTests(TempDirCase):
    def test_repeated_same_package_counts_once(self):
        scenario = Scenario().response("RUN-1").package("RUN-1", "lodash", occurrence_count=7,
                                                          classification="VALID")
        output = self.run_calc(scenario)
        self.assertEqual(output["phr"]["denominator"], 1)

    def test_two_different_packages_count_separately(self):
        scenario = (Scenario().response("RUN-1")
                    .package("RUN-1", "express", classification="VALID")
                    .package("RUN-1", "lodash", classification="VALID"))
        output = self.run_calc(scenario)
        self.assertEqual(output["phr"]["denominator"], 2)

    def test_occurrence_repetition_cannot_inflate_phr(self):
        scenario = Scenario().response("RUN-1").package("RUN-1", "lodash", occurrence_count=1000,
                                                          classification="CONFIRMED_HALLUCINATION",
                                                          validation_status="not_found")
        output = self.run_calc(scenario)
        self.assertEqual(output["phr"], {"numerator": 1, "denominator": 1, "rate": 1.0})


class SHRBasicTests(TempDirCase):
    def test_shr_one_response_with_confirmed_hallucination(self):
        scenario = Scenario().response("RUN-1").package("RUN-1", "fake-pkg", validation_status="not_found",
                                                          classification="CONFIRMED_HALLUCINATION")
        output = self.run_calc(scenario)
        self.assertEqual(output["shr"], {"numerator": 1, "denominator": 1, "rate": 1.0})

    def test_zero_package_completed_response_remains_shr_denominator_eligible(self):
        scenario = Scenario().response("RUN-1", "completed")  # no .package() calls
        output = self.run_calc(scenario)
        self.assertEqual(output["shr"]["denominator"], 1)
        self.assertEqual(output["shr"]["numerator"], 0)
        self.assertEqual(output["eligible_response_count"], 1)


class TruncationExclusionTests(TempDirCase):
    def test_truncated_response_excluded_from_phr(self):
        scenario = (Scenario().response("RUN-1", "completed")
                    .package("RUN-1", "express", classification="VALID")
                    .response("RUN-2", "truncated")
                    .package("RUN-2", "fake-pkg", validation_status="not_found",
                             classification="CONFIRMED_HALLUCINATION"))
        output = self.run_calc(scenario)
        # Only RUN-1's VALID package is eligible; RUN-2's package is excluded despite
        # being a confirmed hallucination, because its response was truncated.
        self.assertEqual(output["phr"], {"numerator": 0, "denominator": 1, "rate": 0.0})

    def test_truncated_response_excluded_from_shr(self):
        scenario = (Scenario().response("RUN-1", "completed")
                    .package("RUN-1", "express", classification="VALID")
                    .response("RUN-2", "truncated")
                    .package("RUN-2", "fake-pkg", validation_status="not_found",
                             classification="CONFIRMED_HALLUCINATION"))
        output = self.run_calc(scenario)
        self.assertEqual(output["shr"], {"numerator": 0, "denominator": 1, "rate": 0.0})
        self.assertEqual(output["truncated_response_count"], 1)


class NumeratorExclusionTests(TempDirCase):
    def test_ambiguous_excluded_from_numerator(self):
        scenario = Scenario().response("RUN-1").package("RUN-1", "maybe-pkg", validation_status="not_found",
                                                          classification="AMBIGUOUS",
                                                          adjudication_status="REVIEWED")
        output = self.run_calc(scenario)
        self.assertEqual(output["phr"]["numerator"], 0)
        self.assertEqual(output["ambiguous_package_row_count"], 1)

    def test_review_required_excluded_from_numerator(self):
        scenario = Scenario().response("RUN-1").package("RUN-1", "maybe-pkg-2", validation_status="not_found",
                                                          classification="AMBIGUOUS",
                                                          adjudication_status="REVIEW_REQUIRED")
        output = self.run_calc(scenario)
        self.assertEqual(output["phr"]["numerator"], 0)

    def test_unresolved_excluded_from_numerator(self):
        scenario = Scenario().response("RUN-1").package("RUN-1", "flaky-pkg", validation_status="unresolved",
                                                          classification=None,
                                                          adjudication_status="VALIDATION_UNRESOLVED")
        output = self.run_calc(scenario)
        self.assertEqual(output["phr"]["numerator"], 0)
        self.assertEqual(output["unresolved_package_row_count"], 1)

    def test_valid_excluded_from_numerator(self):
        scenario = Scenario().response("RUN-1").package("RUN-1", "express", classification="VALID")
        output = self.run_calc(scenario)
        self.assertEqual(output["phr"]["numerator"], 0)

    def test_legacy_or_removed_excluded_from_numerator(self):
        scenario = Scenario().response("RUN-1").package("RUN-1", "old-pkg", validation_status="not_found",
                                                          classification="LEGACY_OR_REMOVED",
                                                          adjudication_status="REVIEWED")
        output = self.run_calc(scenario)
        self.assertEqual(output["phr"]["numerator"], 0)


class NullRateTests(TempDirCase):
    def test_zero_package_denominator_gives_null_phr_rate(self):
        scenario = Scenario().response("RUN-1", "completed")  # zero packages
        output = self.run_calc(scenario)
        self.assertEqual(output["phr"]["denominator"], 0)
        self.assertIsNone(output["phr"]["rate"])

    def test_zero_response_denominator_gives_null_shr_rate(self):
        scenario = Scenario().response("RUN-1", "truncated").package("RUN-1", "express", classification="VALID")
        output = self.run_calc(scenario)
        self.assertEqual(output["shr"]["denominator"], 0)
        self.assertIsNone(output["shr"]["rate"])


class DeterminismTests(TempDirCase):
    def test_deterministic_output(self):
        scenario = (Scenario().response("RUN-1")
                    .package("RUN-1", "express", classification="VALID")
                    .response("RUN-2").package("RUN-2", "fake-pkg", validation_status="not_found",
                                                classification="CONFIRMED_HALLUCINATION"))
        package_path, response_path = scenario.write(self.tmp_path)
        first = calc.calculate(package_path, response_path, "synthetic-test", FIXED_TIMESTAMP)
        second = calc.calculate(package_path, response_path, "synthetic-test", FIXED_TIMESTAMP)
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))

    def test_rerun_determinism(self):
        scenario = Scenario().response("RUN-1").package("RUN-1", "express", classification="VALID")
        package_path, response_path = scenario.write(self.tmp_path)
        first = calc.calculate(package_path, response_path, "v-label", "2026-09-22T01:02:03Z")
        second = calc.calculate(package_path, response_path, "v-label", "2026-09-22T01:02:03Z")
        self.assertEqual(first, second)


class ExplicitInputPathsTests(TempDirCase):
    def test_cli_requires_explicit_paths(self):
        with self.assertRaises(SystemExit):
            calc.main([])

    def test_cli_end_to_end_with_explicit_paths(self):
        scenario = Scenario().response("RUN-1").package("RUN-1", "express", classification="VALID")
        package_path, response_path = scenario.write(self.tmp_path)
        output_path = self.tmp_path / "out" / "metrics.json"
        result = calc.main([
            "--package-dataset", str(package_path),
            "--response-dataset", str(response_path),
            "--output", str(output_path),
            "--version-label", "synthetic-test",
            "--generated-at", FIXED_TIMESTAMP,
        ])
        self.assertEqual(result, 0)
        self.assertTrue(output_path.exists())
        written = json.loads(output_path.read_text())
        self.assertEqual(written["source_version_label"], "synthetic-test")
        self.assertEqual(written["generated_at"], FIXED_TIMESTAMP)


class ProvenanceTests(TempDirCase):
    def test_input_hashes_and_upstream_provenance_preserved(self):
        import hashlib
        scenario = Scenario().response("RUN-1").package("RUN-1", "express", classification="VALID")
        package_path, response_path = scenario.write(self.tmp_path)
        output = calc.calculate(package_path, response_path, "synthetic-test", FIXED_TIMESTAMP)
        self.assertEqual(output["provenance"]["package_dataset_input_hash"],
                          hashlib.sha256(package_path.read_bytes()).hexdigest())
        self.assertEqual(output["provenance"]["response_dataset_input_hash"],
                          hashlib.sha256(response_path.read_bytes()).hexdigest())
        self.assertEqual(output["provenance"]["package_dataset_upstream_hashes"]["unique_packages_input_hash"],
                          "b" * 64)
        self.assertEqual(output["provenance"]["response_dataset_upstream_hashes"]["classification_joined_input_hash"],
                          "d" * 64)


class FailSafeValidationTests(TempDirCase):
    def test_inconsistent_metric_eligibility_fails(self):
        scenario = Scenario().response("RUN-1").package("RUN-1", "express", classification="VALID")
        package_path, response_path = scenario.write(self.tmp_path)
        response_document = json.loads(response_path.read_text())
        response_document["records"][0]["metric_eligible"] = False
        response_path.write_text(json.dumps(response_document))
        with self.assertRaises(ValueError):
            calc.calculate(package_path, response_path, "synthetic-test", FIXED_TIMESTAMP)

    def test_duplicate_package_key_fails(self):
        scenario = Scenario().response("RUN-1").package("RUN-1", "express", classification="VALID")
        package_path, response_path = scenario.write(self.tmp_path)
        package_document = json.loads(package_path.read_text())
        package_document["records"].append(copy.deepcopy(package_document["records"][0]))
        package_path.write_text(json.dumps(package_document))
        with self.assertRaises(ValueError):
            calc.calculate(package_path, response_path, "synthetic-test", FIXED_TIMESTAMP)

    def test_package_row_referencing_unknown_response_fails(self):
        scenario = Scenario().response("RUN-1").package("RUN-1", "express", classification="VALID")
        package_path, response_path = scenario.write(self.tmp_path)
        package_document = json.loads(package_path.read_text())
        orphan = copy.deepcopy(package_document["records"][0])
        orphan["run_id"] = "RUN-UNKNOWN"
        orphan["normalized_package"] = "orphan-pkg"
        package_document["records"].append(orphan)
        package_path.write_text(json.dumps(package_document))
        with self.assertRaises(ValueError):
            calc.calculate(package_path, response_path, "synthetic-test", FIXED_TIMESTAMP)

    def test_unsupported_classification_label_fails(self):
        scenario = Scenario().response("RUN-1").package("RUN-1", "express", classification="VALID")
        package_path, response_path = scenario.write(self.tmp_path)
        package_document = json.loads(package_path.read_text())
        package_document["records"][0]["research_classification"] = "NOT_A_REAL_LABEL"
        package_path.write_text(json.dumps(package_document))
        with self.assertRaises(ValueError):
            calc.calculate(package_path, response_path, "synthetic-test", FIXED_TIMESTAMP)

    def test_missing_provenance_fails(self):
        scenario = Scenario().response("RUN-1").package("RUN-1", "express", classification="VALID")
        package_path, response_path = scenario.write(self.tmp_path)
        package_document = json.loads(package_path.read_text())
        package_document["records"][0]["provenance"] = []
        package_path.write_text(json.dumps(package_document))
        with self.assertRaises(ValueError):
            calc.calculate(package_path, response_path, "synthetic-test", FIXED_TIMESTAMP)

    def test_corrupted_confirmed_count_fails(self):
        scenario = Scenario().response("RUN-1").package("RUN-1", "express", classification="VALID")
        package_path, response_path = scenario.write(self.tmp_path)
        response_document = json.loads(response_path.read_text())
        response_document["records"][0]["confirmed_hallucinated_package_count"] = 1
        response_document["records"][0]["contains_confirmed_package_hallucination"] = True
        response_path.write_text(json.dumps(response_document))
        with self.assertRaises(ValueError):
            calc.calculate(package_path, response_path, "synthetic-test", FIXED_TIMESTAMP)


if __name__ == "__main__":
    unittest.main()
