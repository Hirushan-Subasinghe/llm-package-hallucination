#!/usr/bin/env python3
"""Synthetic, offline tests for PIPE-07 derived analysis-dataset builder.

All fixtures are synthetic and invented for this test only. None represent a
real collected observation or a real research result; no v2.2 or v2.6 data is
read here.
"""

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_analysis_dataset as builder
import calculate_primary_metrics as primary_metrics
import analyze_group_comparisons as group_comparisons
import calculate_dependency_reliability_metrics as reliability_metrics


def inventory_row(run_id, collection_order, collection_status="completed",
                   model_condition_id="M1", task_id="TASK-01", category="AUTH-FED",
                   replicate="R01", provider="OpenRouter", model="synthetic-model"):
    collected = collection_status in ("completed", "truncated")
    return {
        "run_id": run_id,
        "collection_order": collection_order,
        "provider": provider,
        "tool": None,
        "model": model,
        "model_condition_id": model_condition_id,
        "workflow": None,
        "task_id": task_id,
        "category": category,
        "replicate": replicate,
        "manifest_path": "manifests/synthetic.csv",
        "rendered_prompt_path": f"prompts/{run_id}.md",
        "expected_prompt_sha256": "a" * 64,
        "response_artifact_path": f"data/final/raw/{run_id}/response.md" if collected else None,
        "collection_status": collection_status,
        "completion_status": ("COMPLETED" if collection_status == "completed"
                               else "TRUNCATED" if collection_status == "truncated" else None),
        "truncated": (collection_status == "truncated") if collected else None,
        "token_count": 100 if collected else None,
        "interface_pass": True if collected else None,
    }


def unique_row(run_id, normalized_package, collection_order, occurrence_count=1,
               model_condition_id="M1", task_id="TASK-01", category="AUTH-FED",
               first_occurrence_index=1, source_types=("es_import",),
               extractor_version="pipe-03-test"):
    return {
        "run_id": run_id, "collection_order": collection_order,
        "model_condition_id": model_condition_id, "task_id": task_id, "category": category,
        "normalized_package": normalized_package, "first_occurrence_index": first_occurrence_index,
        "occurrence_count": occurrence_count, "source_types": list(source_types),
        "extractor_version": extractor_version,
    }


def validation_joined_row(unique, inventory_row_for_run, validation_status="exists",
                           http_status=200, evidence_summary="Registry metadata returned the exact package name",
                           error_type=None):
    return {
        **unique,
        "collection_status": inventory_row_for_run["collection_status"],
        "completion_status": inventory_row_for_run["completion_status"],
        "truncated": inventory_row_for_run["truncated"],
        "response_artifact_path": inventory_row_for_run["response_artifact_path"],
        "validation_status": validation_status,
        "registry": "https://registry.npmjs.org",
        "request_url": "https://registry.npmjs.org/" + unique["normalized_package"],
        "http_status": http_status,
        "checked_at": "2026-09-22T00:00:00Z",
        "validator_version": "pipe-04-npm-validator-1.0.0",
        "evidence_summary": evidence_summary,
        "error_type": error_type,
        "retry_count": 0,
        "source_input_hash": "b" * 64,
        "source_occurrences_hash": "c" * 64,
    }


def classification_joined_row(validation, classification=None, adjudication_status="AUTO_VALID"):
    return {
        **validation,
        "classification": classification,
        "classification_basis": "synthetic rationale",
        "adjudication_status": adjudication_status,
        "review_required": False,
        "reviewer_id": None,
        "reviewed_at": None,
        "review_notes": None,
        "review_evidence": [],
        "review_checks": None,
        "classifier_version": "pipe-05-classifier-1.0.0",
    }


class Scenario:
    """Builds mutually consistent inventory/unique/validation/classification fixtures."""

    def __init__(self):
        self.inventory = []
        self.unique = []
        self.validation = []
        self.classification = []
        self._by_run = {}

    def response(self, run_id, collection_order, collection_status="completed", **overrides):
        row = inventory_row(run_id, collection_order, collection_status=collection_status, **overrides)
        self.inventory.append(row)
        self._by_run[run_id] = row
        return self

    def package(self, run_id, normalized_package, occurrence_count=1,
                validation_status="exists", classification=None, adjudication_status="AUTO_VALID"):
        inv = self._by_run[run_id]
        u = unique_row(run_id, normalized_package, inv["collection_order"], occurrence_count=occurrence_count)
        v = validation_joined_row(u, inv, validation_status=validation_status)
        c = classification_joined_row(v, classification=classification, adjudication_status=adjudication_status)
        self.unique.append(u)
        self.validation.append(v)
        self.classification.append(c)
        return self

    def write(self, tmp_path):
        base = Path(tmp_path)
        inventory_path = base / "inventory.json"
        unique_path = base / "unique.json"
        validation_path = base / "validation_joined.json"
        classification_path = base / "classification_joined.json"
        inventory_path.write_text(json.dumps(self.inventory))
        unique_path.write_text(json.dumps(self.unique))
        validation_path.write_text(json.dumps({"format_version": "pipe-04-evidence-1.0.0",
                                                 "records": self.validation}))
        classification_path.write_text(json.dumps({"format_version": "pipe-05-classification-1.0.0",
                                                     "records": self.classification}))
        return inventory_path, unique_path, validation_path, classification_path


class TempDirCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp_path = Path(self._tmp.name)

    def build(self, scenario):
        paths = scenario.write(self.tmp_path)
        return builder.build_datasets(*paths)


class CleanCompletedResponseTests(TempDirCase):
    def test_clean_completed_response_with_valid_packages(self):
        scenario = (Scenario()
                    .response("RUN-1", 1)
                    .package("RUN-1", "express", validation_status="exists", classification="VALID"))
        package_rows, response_rows, _hashes = self.build(scenario)
        self.assertEqual(len(package_rows), 1)
        self.assertEqual(package_rows[0]["research_classification"], "VALID")
        self.assertTrue(package_rows[0]["metric_eligible"])
        self.assertEqual(response_rows[0]["unique_package_count"], 1)
        self.assertEqual(response_rows[0]["confirmed_hallucinated_package_count"], 0)
        self.assertFalse(response_rows[0]["contains_confirmed_package_hallucination"])
        self.assertTrue(response_rows[0]["metric_eligible"])


class ConfirmedHallucinationTests(TempDirCase):
    def test_response_with_confirmed_hallucinated_package(self):
        scenario = (Scenario()
                    .response("RUN-1", 1)
                    .package("RUN-1", "totally-fake-pkg", validation_status="not_found",
                             classification="CONFIRMED_HALLUCINATION", adjudication_status="REVIEWED"))
        package_rows, response_rows, _ = self.build(scenario)
        self.assertEqual(package_rows[0]["research_classification"], "CONFIRMED_HALLUCINATION")
        self.assertEqual(response_rows[0]["confirmed_hallucinated_package_count"], 1)
        self.assertTrue(response_rows[0]["contains_confirmed_package_hallucination"])


class AmbiguousPackageTests(TempDirCase):
    def test_ambiguous_package(self):
        scenario = (Scenario()
                    .response("RUN-1", 1)
                    .package("RUN-1", "maybe-pkg", validation_status="not_found",
                             classification="AMBIGUOUS", adjudication_status="REVIEW_REQUIRED"))
        package_rows, response_rows, _ = self.build(scenario)
        self.assertEqual(package_rows[0]["research_classification"], "AMBIGUOUS")
        self.assertEqual(response_rows[0]["ambiguous_package_count"], 1)
        self.assertEqual(response_rows[0]["confirmed_hallucinated_package_count"], 0)
        self.assertFalse(response_rows[0]["contains_confirmed_package_hallucination"])


class UnresolvedRegistryEvidenceTests(TempDirCase):
    def test_unresolved_registry_evidence(self):
        scenario = (Scenario()
                    .response("RUN-1", 1)
                    .package("RUN-1", "flaky-pkg", validation_status="unresolved",
                             classification=None, adjudication_status="VALIDATION_UNRESOLVED"))
        package_rows, response_rows, _ = self.build(scenario)
        self.assertIsNone(package_rows[0]["research_classification"])
        self.assertEqual(response_rows[0]["unresolved_package_count"], 1)
        self.assertEqual(response_rows[0]["confirmed_hallucinated_package_count"], 0)


class TruncatedResponseTests(TempDirCase):
    def test_truncated_response_retained_but_metric_ineligible(self):
        scenario = (Scenario()
                    .response("RUN-1", 1, collection_status="truncated")
                    .package("RUN-1", "express", validation_status="exists", classification="VALID"))
        package_rows, response_rows, _ = self.build(scenario)
        self.assertEqual(len(package_rows), 1)
        self.assertFalse(package_rows[0]["metric_eligible"])
        self.assertEqual(response_rows[0]["collection_status"], "truncated")
        self.assertFalse(response_rows[0]["metric_eligible"])
        # Still retained, not dropped:
        self.assertEqual(response_rows[0]["unique_package_count"], 1)


class ZeroPackageResponseTests(TempDirCase):
    def test_completed_non_truncated_response_with_zero_external_packages(self):
        scenario = Scenario().response("RUN-1", 1, collection_status="completed")
        package_rows, response_rows, _ = self.build(scenario)
        self.assertEqual(package_rows, [])
        self.assertEqual(len(response_rows), 1)
        row = response_rows[0]
        self.assertTrue(row["metric_eligible"])
        self.assertEqual(row["package_reference_count"], 0)
        self.assertEqual(row["unique_package_count"], 0)
        self.assertFalse(row["contains_confirmed_package_hallucination"])


class RepeatedOccurrenceTests(TempDirCase):
    def test_repeated_occurrence_counts_reflected_correctly(self):
        scenario = (Scenario()
                    .response("RUN-1", 1)
                    .package("RUN-1", "lodash", occurrence_count=4, validation_status="exists",
                             classification="VALID"))
        package_rows, response_rows, _ = self.build(scenario)
        self.assertEqual(package_rows[0]["occurrence_count"], 4)
        self.assertEqual(response_rows[0]["package_reference_count"], 4)
        self.assertEqual(response_rows[0]["unique_package_count"], 1)


class UniquePackageRowsTests(TempDirCase):
    def test_unique_package_rows_not_duplicated(self):
        scenario = (Scenario()
                    .response("RUN-1", 1)
                    .package("RUN-1", "express", occurrence_count=3, validation_status="exists",
                             classification="VALID")
                    .package("RUN-1", "lodash", occurrence_count=2, validation_status="exists",
                             classification="VALID"))
        package_rows, response_rows, _ = self.build(scenario)
        self.assertEqual(len(package_rows), 2)
        self.assertEqual({row["normalized_package"] for row in package_rows}, {"express", "lodash"})
        self.assertEqual(response_rows[0]["unique_package_count"], 2)
        self.assertEqual(response_rows[0]["package_reference_count"], 5)


class ClassificationMappingTests(TempDirCase):
    def test_classification_mapping_preserved(self):
        scenario = (Scenario()
                    .response("RUN-1", 1)
                    .package("RUN-1", "left-pad-but-fake", validation_status="not_found",
                             classification="LEGACY_OR_REMOVED", adjudication_status="REVIEWED"))
        package_rows, _response_rows, _ = self.build(scenario)
        self.assertEqual(package_rows[0]["research_classification"], "LEGACY_OR_REMOVED")
        self.assertEqual(package_rows[0]["validation_status"], "not_found")
        self.assertEqual(package_rows[0]["adjudication_status"], "REVIEWED")


class ResponseLevelCountTests(TempDirCase):
    def test_response_level_counts_derived_correctly(self):
        scenario = (Scenario()
                    .response("RUN-1", 1)
                    .package("RUN-1", "express", validation_status="exists", classification="VALID")
                    .package("RUN-1", "fake-one", validation_status="not_found",
                             classification="CONFIRMED_HALLUCINATION", adjudication_status="REVIEWED")
                    .package("RUN-1", "fake-two", validation_status="not_found",
                             classification="AMBIGUOUS")
                    .package("RUN-1", "flaky", validation_status="unresolved", classification=None,
                             adjudication_status="VALIDATION_UNRESOLVED"))
        _package_rows, response_rows, _ = self.build(scenario)
        row = response_rows[0]
        self.assertEqual(row["unique_package_count"], 4)
        self.assertEqual(row["package_reference_count"], 4)
        self.assertEqual(row["confirmed_hallucinated_package_count"], 1)
        self.assertEqual(row["ambiguous_package_count"], 1)
        self.assertEqual(row["unresolved_package_count"], 1)
        self.assertTrue(row["contains_confirmed_package_hallucination"])


class ContainsConfirmedFlagTests(TempDirCase):
    def test_contains_confirmed_true_when_present(self):
        scenario = (Scenario().response("RUN-1", 1)
                    .package("RUN-1", "fake-pkg", validation_status="not_found",
                             classification="CONFIRMED_HALLUCINATION", adjudication_status="REVIEWED"))
        _p, response_rows, _ = self.build(scenario)
        self.assertTrue(response_rows[0]["contains_confirmed_package_hallucination"])

    def test_contains_confirmed_false_when_absent(self):
        scenario = (Scenario().response("RUN-1", 1)
                    .package("RUN-1", "express", validation_status="exists", classification="VALID"))
        _p, response_rows, _ = self.build(scenario)
        self.assertFalse(response_rows[0]["contains_confirmed_package_hallucination"])


class PendingRowTests(TempDirCase):
    def test_pending_rows_not_treated_as_completed(self):
        scenario = (Scenario()
                    .response("RUN-1", 1, collection_status="completed")
                    .package("RUN-1", "express", validation_status="exists", classification="VALID")
                    .response("RUN-2", 2, collection_status="pending"))
        package_rows, response_rows, _ = self.build(scenario)
        self.assertEqual(len(package_rows), 1)  # pending row contributes no package rows
        pending_row = next(row for row in response_rows if row["run_id"] == "RUN-2")
        self.assertEqual(pending_row["collection_status"], "pending")
        self.assertIsNone(pending_row["completion_status"])
        self.assertFalse(pending_row["metric_eligible"])
        self.assertEqual(pending_row["unique_package_count"], 0)


class D035ProviderAbnormalFinishTests(TempDirCase):
    """A D035-corrected failed response keeps an ineligible row and no package rows."""

    def scenario(self):
        scenario = (Scenario()
                    .response("RUN-1", 1)
                    .package("RUN-1", "express", validation_status="exists", classification="VALID")
                    .response("RUN-2", 2, collection_status="failed"))
        failed = scenario.inventory[1]
        failed.update({
            "completion_status": "FAILED",
            "truncated": False,
            "token_count": 7599,
            "response_artifact_path": "data/final/raw/RUN-2/response.md",
            "raw_collection_status": "completed",
            "provider_finish_reason": "error",
            "status_correction": "D035",
        })
        return scenario

    def test_failed_run_is_not_admitted_to_primary_metrics(self):
        package_rows, response_rows, _ = self.build(self.scenario())
        self.assertEqual({row["run_id"] for row in package_rows}, {"RUN-1"})
        self.assertTrue(all(row["metric_eligible"] for row in package_rows))
        failed = next(row for row in response_rows if row["run_id"] == "RUN-2")
        self.assertEqual((failed["collection_status"], failed["completion_status"]), ("failed", "FAILED"))
        self.assertFalse(failed["metric_eligible"])
        self.assertEqual(failed["unique_package_count"], 0)
        self.assertEqual(sum(row["metric_eligible"] for row in response_rows), 1)

    def test_stale_package_rows_for_failed_run_are_rejected(self):
        scenario = self.scenario()
        # Simulate PIPE-03/04/05 outputs built before D035, when RUN-2 was "completed".
        stale = dict(scenario.inventory[1], collection_status="completed", completion_status="COMPLETED")
        u = unique_row("RUN-2", "samlify", 2)
        v = validation_joined_row(u, stale)
        scenario.unique.append(u)
        scenario.validation.append(v)
        scenario.classification.append(classification_joined_row(v, classification="VALID"))
        with self.assertRaisesRegex(ValueError, "only completed/truncated responses"):
            self.build(scenario)


class ConflictingMetadataTests(TempDirCase):
    def test_conflicting_metadata_causes_failure(self):
        scenario = (Scenario().response("RUN-1", 1)
                    .package("RUN-1", "express", validation_status="exists", classification="VALID"))
        # Corrupt the unique-packages row's task_id so it disagrees with the inventory row.
        scenario.unique[0]["task_id"] = "SOME-OTHER-TASK"
        with self.assertRaises(ValueError):
            self.build(scenario)


class DuplicateUniqueKeyTests(TempDirCase):
    def test_duplicate_unique_key_causes_failure(self):
        scenario = (Scenario().response("RUN-1", 1)
                    .package("RUN-1", "express", validation_status="exists", classification="VALID"))
        scenario.unique.append(copy.deepcopy(scenario.unique[0]))
        with self.assertRaises(ValueError):
            self.build(scenario)


class UnsupportedClassificationLabelTests(TempDirCase):
    def test_unsupported_classification_label_rejected(self):
        scenario = (Scenario().response("RUN-1", 1)
                    .package("RUN-1", "express", validation_status="exists", classification="VALID"))
        scenario.classification[0]["classification"] = "NOT_A_REAL_LABEL"
        with self.assertRaises(ValueError):
            self.build(scenario)


class DeterministicOrderingAndRerunTests(TempDirCase):
    def test_deterministic_output_ordering(self):
        scenario = (Scenario()
                    .response("RUN-2", 2).package("RUN-2", "zeta-pkg", classification="VALID")
                    .response("RUN-1", 1).package("RUN-1", "beta-pkg", classification="VALID")
                    .package("RUN-1", "alpha-pkg", classification="VALID"))
        package_rows, response_rows, _ = self.build(scenario)
        self.assertEqual([(row["run_id"], row["normalized_package"]) for row in package_rows],
                          [("RUN-1", "alpha-pkg"), ("RUN-1", "beta-pkg"), ("RUN-2", "zeta-pkg")])
        self.assertEqual([row["run_id"] for row in response_rows], ["RUN-1", "RUN-2"])

    def test_rerun_determinism(self):
        scenario = (Scenario().response("RUN-1", 1)
                    .package("RUN-1", "express", classification="VALID")
                    .response("RUN-2", 2, collection_status="truncated")
                    .package("RUN-2", "fake-pkg", validation_status="not_found",
                             classification="CONFIRMED_HALLUCINATION"))
        first = self.build(scenario)
        second = self.build(scenario)
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))


class ExplicitInputPathsTests(TempDirCase):
    def test_explicit_input_paths_no_automatic_latest_discovery(self):
        with self.assertRaises(SystemExit):
            builder.main([])  # no arguments at all: argparse must refuse, not guess a "latest" file

    def test_cli_requires_all_four_inputs_explicitly(self):
        scenario = (Scenario().response("RUN-1", 1)
                    .package("RUN-1", "express", classification="VALID"))
        inventory_path, unique_path, validation_path, classification_path = scenario.write(self.tmp_path)
        output_dir = self.tmp_path / "out"
        argv = [
            "--inventory", str(inventory_path),
            "--unique-packages", str(unique_path),
            "--validation-joined", str(validation_path),
            "--classification-joined", str(classification_path),
            "--no-pipe05b-adjudication",
            "--output-dir", str(output_dir),
            "--version-label", "synthetic-test",
        ]
        result = builder.main(argv)
        self.assertEqual(result, 0)
        self.assertTrue((output_dir / "package_response_analysis_synthetic-test.json").exists())
        self.assertTrue((output_dir / "response_level_analysis_synthetic-test.json").exists())


class VersionAgnosticOperationTests(TempDirCase):
    def test_version_agnostic_operation_with_arbitrary_version_label(self):
        # Nothing in the builder or its schemas hard-codes "v2.2"; an arbitrary
        # future-version label must work identically.
        scenario = (Scenario().response("API-v9.9-FAKE-01-M1-R01", 1)
                    .package("API-v9.9-FAKE-01-M1-R01", "express", classification="VALID"))
        package_rows, response_rows, _hashes = self.build(scenario)
        self.assertEqual(package_rows[0]["run_id"], "API-v9.9-FAKE-01-M1-R01")
        self.assertEqual(response_rows[0]["run_id"], "API-v9.9-FAKE-01-M1-R01")


class D037Pipe05BRoutingTests(TempDirCase):
    """Synthetic confirmation guard/routing checks; no research data is loaded."""
    def _pipe05b(self, source_path, records):
        import hashlib
        path = self.tmp_path / "pipe05b.json"
        path.write_text(json.dumps({"format_version": "pipe-05b-adjudication-1.1.0",
            "adjudication_version": "pipe-05b-adjudicator-1.1.0",
            "source_input_hash": hashlib.sha256(source_path.read_bytes()).hexdigest(), "records": records}))
        return path
    def _confirmed(self):
        return {"run_id":"RUN-1","normalized_package":"fake","source_truncated":False,
          "adjudication_version":"pipe-05b-adjudicator-1.1.0","adjudication_outcome":"CONFIRMED_HALLUCINATION",
          "confirmed_package_hallucination":True,"dependency_failure":True,"external_dependency_eligible":True,
          "evidence_status":"resolved","checks":{"historical":"no_prior_evidence","normalization":"external_npm_reference","ambiguity":"cleared","namespace":"cleared","ecosystem":"cleared","types_package":"cleared"},
          "evidence_sources":[{"source":"synthetic","summary":"synthetic","checked_at":"2026-01-01T00:00:00Z"}],"reviewed_at":"2026-01-01T00:00:00Z"}
    def test_guarded_pipe05b_routes_once_and_no_input_is_recorded(self):
        scenario=(Scenario().response("RUN-1",1).package("RUN-1","fake",validation_status="not_found",classification="AMBIGUOUS",adjudication_status="REVIEW_REQUIRED"))
        paths=scenario.write(self.tmp_path); b=self._pipe05b(paths[3],[self._confirmed()])
        package_rows,response_rows,hashes=builder.build_datasets(*paths,pipe05b_adjudication_path=b,no_pipe05b_adjudication=False)
        self.assertEqual(package_rows[0]["primary_confirmation_path"],"PIPE05B"); self.assertTrue(response_rows[0]["contains_confirmed_package_hallucination"]); self.assertEqual(hashes["pipe05b_adjudication_input_status"],"supplied")
        _,_,no_hashes=builder.build_datasets(*paths,no_pipe05b_adjudication=True)
        self.assertEqual(no_hashes["pipe05b_adjudication_input_status"],"not_supplied")
    def test_invalid_guard_and_source_hash_fail_closed(self):
        scenario=(Scenario().response("RUN-1",1).package("RUN-1","fake",validation_status="not_found",classification="AMBIGUOUS",adjudication_status="REVIEW_REQUIRED"))
        paths=scenario.write(self.tmp_path); record=self._confirmed(); record["checks"]["namespace"]="inconclusive"; b=self._pipe05b(paths[3],[record])
        with self.assertRaisesRegex(ValueError,"guard"): builder.build_datasets(*paths,pipe05b_adjudication_path=b,no_pipe05b_adjudication=False)
        b.write_text(json.dumps({"format_version":"pipe-05b-adjudication-1.1.0","adjudication_version":"pipe-05b-adjudicator-1.1.0","source_input_hash":"0"*64,"records":[]}))
        with self.assertRaisesRegex(ValueError,"source_input_hash"): builder.build_datasets(*paths,pipe05b_adjudication_path=b,no_pipe05b_adjudication=False)

    def _review_required_paths(self):
        scenario=(Scenario().response("RUN-1",1).package("RUN-1","fake",validation_status="not_found",classification="AMBIGUOUS",adjudication_status="REVIEW_REQUIRED"))
        return scenario.write(self.tmp_path)

    def _rejected(self, records, pattern, paths=None):
        paths = paths or self._review_required_paths()
        envelope = self._pipe05b(paths[3], records)
        with self.assertRaisesRegex(ValueError, pattern):
            builder.build_datasets(*paths, pipe05b_adjudication_path=envelope,
                                   no_pipe05b_adjudication=False)

    def test_duplicate_and_orphan_pipe05b_keys_fail_closed(self):
        record = self._confirmed()
        self._rejected([record, copy.deepcopy(record)], "Duplicate PIPE-05B key")
        orphan = self._confirmed(); orphan["normalized_package"] = "orphan"
        self._rejected([orphan], "has no PIPE-07 row")

    def test_pipe05b_cannot_attach_to_auto_valid_reviewed_or_both_paths(self):
        cases = (("AUTO_VALID", "VALID", "not REVIEW_REQUIRED"),
                 ("REVIEWED", "LEGACY_OR_REMOVED", "not REVIEW_REQUIRED"),
                 ("REVIEWED", "CONFIRMED_HALLUCINATION", "both PIPE05_REVIEWED and PIPE05B"))
        for status, classification, expected in cases:
            with self.subTest(status=status, classification=classification):
                scenario=(Scenario().response("RUN-1",1).package("RUN-1","fake",validation_status="not_found",classification=classification,adjudication_status=status))
                self._rejected([self._confirmed()], expected, scenario.write(self.tmp_path))

    def test_versions_hash_and_truncation_mismatches_fail_closed(self):
        paths = self._review_required_paths()
        cases = (
            ("format_version", "unsupported", "Unsupported PIPE-05B format_version"),
            ("adjudication_version", "unsupported", "Unsupported PIPE-05B adjudication_version"),
            ("source_input_hash", "0" * 64, "source_input_hash"),
        )
        for field, value, expected in cases:
            with self.subTest(field=field):
                path = self._pipe05b(paths[3], [self._confirmed()])
                doc = json.loads(path.read_text()); doc[field] = value; path.write_text(json.dumps(doc))
                with self.assertRaisesRegex(ValueError, expected):
                    builder.build_datasets(*paths, pipe05b_adjudication_path=path,
                                           no_pipe05b_adjudication=False)
        record = self._confirmed(); record["source_truncated"] = True
        self._rejected([record], "source_truncated")
        record = self._confirmed(); record["adjudication_version"] = "unsupported"
        self._rejected([record], "record adjudication_version")

    def test_confirmation_flag_evidence_and_each_conservative_check_fail_closed(self):
        mutations = [
            ("confirmed_false", lambda r: r.update(confirmed_package_hallucination=False), "confirmed_package_hallucination/outcome"),
            ("nonconfirmed_true", lambda r: r.update(adjudication_outcome="OTHER_DEPENDENCY_ERROR"), "confirmed_package_hallucination/outcome"),
            ("dependency_failure", lambda r: r.update(dependency_failure=False), "guard"),
            ("external_eligible_false", lambda r: r.update(external_dependency_eligible=False), "guard"),
            ("external_eligible_null", lambda r: r.update(external_dependency_eligible=None), "guard"),
            ("evidence_insufficient", lambda r: r.update(evidence_status="insufficient"), "guard"),
            ("empty_sources", lambda r: r.update(evidence_sources=[]), "guard"),
            ("missing_reviewed_at", lambda r: r.pop("reviewed_at"), "guard"),
            ("invalid_reviewed_at", lambda r: r.update(reviewed_at="2026-01-01"), "guard"),
        ]
        for name, mutate, expected in mutations:
            with self.subTest(name=name):
                record = self._confirmed(); mutate(record); self._rejected([record], expected)
        for check, invalid in (("historical", "inconclusive"), ("normalization", "inconclusive"),
                               ("ambiguity", "inconclusive"), ("namespace", "inconclusive"),
                               ("ecosystem", "inconclusive"), ("types_package", "inconclusive")):
            with self.subTest(check=check):
                record = self._confirmed(); record["checks"][check] = invalid
                self._rejected([record], "guard")

    def test_cli_rejects_missing_or_conflicting_explicit_pipe05b_mode(self):
        paths = self._review_required_paths(); output = self.tmp_path / "out"
        common = ["--inventory", str(paths[0]), "--unique-packages", str(paths[1]),
                  "--validation-joined", str(paths[2]), "--classification-joined", str(paths[3]),
                  "--output-dir", str(output), "--version-label", "synthetic"]
        with self.assertRaises(SystemExit): builder.main(common)
        adjudication = self._pipe05b(paths[3], [self._confirmed()])
        with self.assertRaises(SystemExit):
            builder.main(common + ["--pipe05b-adjudication", str(adjudication), "--no-pipe05b-adjudication"])


class SyntheticCrossPipelineConsistencyTests(TempDirCase):
    """D037/D036 reconciliation using invented fixtures only, never v2.6 artifacts."""
    def test_pipe07_to_pipe10_reconciles_and_historical_outputs_are_preserved(self):
        scenario = (Scenario()
                    .response("VALID", 1).package("VALID", "express", classification="VALID")
                    .response("REVIEWED", 2).package("REVIEWED", "old-fake", validation_status="not_found",
                                                       classification="CONFIRMED_HALLUCINATION", adjudication_status="REVIEWED")
                    .response("PIPE05B", 3).package("PIPE05B", "new-fake", validation_status="not_found",
                                                       classification="AMBIGUOUS", adjudication_status="REVIEW_REQUIRED")
                    .response("ZERO", 4))
        paths = scenario.write(self.tmp_path)
        source_hash = __import__("hashlib").sha256(paths[3].read_bytes()).hexdigest()
        adjudication = {"run_id":"PIPE05B","normalized_package":"new-fake","source_truncated":False,
            "adjudication_version":"pipe-05b-adjudicator-1.1.0","adjudication_outcome":"CONFIRMED_HALLUCINATION",
            "confirmed_package_hallucination":True,"dependency_failure":True,"external_dependency_eligible":True,
            "evidence_status":"resolved","checks":{"historical":"no_prior_evidence","normalization":"external_npm_reference","ambiguity":"cleared","namespace":"cleared","ecosystem":"cleared","types_package":"cleared"},
            "evidence_sources":[{"source":"synthetic","summary":"synthetic","checked_at":"2026-01-01T00:00:00Z"}],"reviewed_at":"2026-01-01T00:00:00Z"}
        adj_path = self.tmp_path / "pipe05b-cross.json"
        adj_path.write_text(json.dumps({"format_version":"pipe-05b-adjudication-1.1.0","adjudication_version":"pipe-05b-adjudicator-1.1.0","source_input_hash":source_hash,"records":[adjudication]}))
        package_rows, response_rows, hashes = builder.build_datasets(*paths, pipe05b_adjudication_path=adj_path,
                                                                       no_pipe05b_adjudication=False)
        output_dir = self.tmp_path / "pipe07"
        outputs = builder.write_outputs(output_dir, package_rows, response_rows, hashes, "synthetic")
        primary = primary_metrics.calculate(outputs["package_json"], outputs["response_json"], "synthetic", "2026-01-01T00:00:00Z")
        grouped, _ = group_comparisons.run(outputs["package_json"], outputs["response_json"], "model_condition_id", "synthetic", 10, 1)
        reliability = reliability_metrics.calculate(outputs["package_json"], outputs["response_json"], adj_path)
        self.assertEqual(primary["phr"]["numerator"], 2)  # PIPE-07 resolved numerator == PIPE-08 PHR numerator
        self.assertEqual(sum(row["confirmed_hallucinated_package_count"] for row in response_rows), 2)
        self.assertEqual(primary["shr"]["numerator"], 2)  # response aggregation == PIPE-08 SHR numerator
        self.assertEqual(sum(row["phr"]["numerator"] for row in grouped["records"]), primary["phr"]["numerator"])
        self.assertEqual(sum(row["phr"]["denominator"] for row in grouped["records"]), primary["phr"]["denominator"])
        self.assertEqual(sum(row["shr"]["numerator"] for row in grouped["records"]), primary["shr"]["numerator"])
        self.assertEqual(sum(row["shr"]["denominator"] for row in grouped["records"]), primary["shr"]["denominator"])
        self.assertEqual(reliability["package_level"]["total_metric_eligible_package_rows"], primary["phr"]["denominator"])
        self.assertEqual(reliability["response_level"]["eligible_completed_responses"], primary["shr"]["denominator"])
        self.assertEqual(primary["primary_confirmed_by_pipe05_reviewed"] + primary["primary_confirmed_by_pipe05b"], primary["phr"]["numerator"])
        old_bytes = outputs["package_json"].read_bytes()
        with self.assertRaisesRegex(ValueError, "Existing PIPE-07 output differs"):
            builder.atomic_write_new_or_identical(outputs["package_json"], old_bytes + b"corruption")
        self.assertEqual(outputs["package_json"].read_bytes(), old_bytes)
        old08 = self.tmp_path / "historical-pipe08.json"; old08.write_bytes(b"historical-pipe08")
        with self.assertRaisesRegex(ValueError, "Existing PIPE-08 output differs"):
            primary_metrics.main(["--package-dataset", str(outputs["package_json"]), "--response-dataset",
                                  str(outputs["response_json"]), "--output", str(old08), "--version-label",
                                  "synthetic", "--generated-at", "2026-01-01T00:00:00Z"])
        self.assertEqual(old08.read_bytes(), b"historical-pipe08")
        old09 = self.tmp_path / "historical-pipe09.json"; old09.write_bytes(b"historical-pipe09")
        with self.assertRaisesRegex(ValueError, "Existing PIPE-09 output differs"):
            group_comparisons.write_new_or_identical(old09, b"new-pipe09")
        self.assertEqual(old09.read_bytes(), b"historical-pipe09")


if __name__ == "__main__":
    unittest.main()
