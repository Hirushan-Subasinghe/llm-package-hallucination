#!/usr/bin/env python3
"""Synthetic, offline tests for PIPE-05B REVIEW_REQUIRED package adjudication.

All fixtures are synthetic. None of the real REVIEW_REQUIRED package names
named in the PIPE-05B task brief are adjudicated here; see
test_no_real_review_required_package_name_used below for the guard list.
"""

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import adjudicate_review_required_packages as adjudicator


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def joined_row(run_id, package, order=1, *, adjudication_status="REVIEW_REQUIRED",
               classification="AMBIGUOUS", review_required=True,
               validation_status="not_found", truncated=False):
    return {
        "run_id": run_id, "collection_order": order, "model_condition_id": "M1",
        "task_id": "SYNTH-TASK-01", "category": "SYNTH-CATEGORY",
        "normalized_package": package, "first_occurrence_index": 1,
        "occurrence_count": 1, "source_types": ["es_import"],
        "extractor_version": "pipe-03-test", "collection_status": "completed",
        "completion_status": "COMPLETED", "truncated": truncated,
        "response_artifact_path": f"raw/{run_id}/response.md",
        "validation_status": validation_status, "registry": "https://registry.npmjs.org",
        "request_url": f"https://registry.npmjs.org/{package}",
        "http_status": 404 if validation_status == "not_found" else None,
        "checked_at": "2026-09-22T00:00:00Z", "validator_version": "pipe-04-npm-validator-1.0.0",
        "evidence_summary": "Official registry returned package-not-found JSON",
        "error_type": None, "retry_count": 0,
        "source_input_hash": "a" * 64, "source_occurrences_hash": "b" * 64,
        "classification": classification, "classification_basis": "Synthetic fixture basis",
        "adjudication_status": adjudication_status, "review_required": review_required,
        "reviewer_id": None, "reviewed_at": None, "review_notes": None,
        "review_evidence": [], "review_checks": None,
        "classifier_version": "pipe-05-classifier-1.0.0",
        "occurrence_evidence": [{
            "run_id": run_id, "occurrence_index": 1, "original_reference": package,
            "normalized_package": package, "source_type": "es_import",
            "source_text": f'import x from "{package}"', "source_offset": 0,
            "version_specifier": None, "response_artifact_path": f"raw/{run_id}/response.md",
            "truncated": truncated,
        }],
    }


def envelope(rows):
    return {"format_version": "pipe-05-classification-1.0.0",
            "source_input_hash": "a" * 64, "source_occurrences_hash": "b" * 64,
            "validation_input_hash": "c" * 64, "validation_joined_input_hash": "d" * 64,
            "adjudication_input_hash": None, "records": rows}


def evidence(source="npm-registry-lookup", summary="Confirmed absent under exact name"):
    return [{"source": source, "summary": summary, "checked_at": "2026-09-22T01:00:00Z"}]


CLEARED_CHECKS = {
    "historical": "no_prior_evidence", "normalization": "external_npm_reference",
    "ambiguity": "cleared", "namespace": "cleared", "ecosystem": "cleared",
    "types_package": "cleared",
}
INCONCLUSIVE_CHECKS = {field: "inconclusive" for field in adjudicator.CHECK_FIELDS}


def decision(run_id="R1", package="fake-pkg", outcome="CONFIRMED_HALLUCINATION", **overrides):
    base = {
        "run_id": run_id, "normalized_package": package, "adjudication_outcome": outcome,
        "reviewer": "reviewer-1", "reviewed_at": "2026-09-22T02:00:00Z",
        "rationale": "Documented synthetic-fixture rationale",
        "evidence_status": "resolved", "evidence_sources": evidence(),
        "current_registry_evidence": None, "historical_evidence": None,
        "nearest_legitimate_reference": None, "installation_impact": "would_fail_install",
        "dependency_failure": True, "checks": dict(CLEARED_CHECKS),
    }
    base.update(overrides)
    return base


OWN_PROJECT = "synthetic-own-project"


def self_reference_row(run_id="R1", package=OWN_PROJECT):
    """Synthetic PIPE-05 row: the generated project's own package.json name, imported
    only in a README usage example, with a clean npm 404."""
    row = joined_row(run_id, package)
    row["occurrence_evidence"][0]["source_text"] = f"import {{ makeClient }} from '{package}';"
    return row


def self_reference_evidence(**overrides):
    base = {
        "basis": "generated_project_own_package_name",
        "declared_name": OWN_PROJECT,
        "declaration_location": 'response package.json "name" field',
        "reference_locations": ["README.md Quick Start code block"],
        "reference_contexts": ["documentation_example"],
        "symbols_defined_in_response": True,
    }
    base.update(overrides)
    return base


def self_reference_decision(package=OWN_PROJECT, **overrides):
    base = dict(
        package=package, outcome="SELF_REFERENCE_OR_LOCAL_PACKAGE",
        checks=dict(INCONCLUSIVE_CHECKS, normalization="builtin_or_local"),
        dependency_failure=False, installation_impact="not_applicable_local_reference",
        current_registry_evidence={"http_status": 404, "validation_status": "not_found"},
        evidence_sources=evidence("response-internal-review",
                                  "package.json name equals the imported package name"),
        self_reference_evidence=self_reference_evidence(declared_name=package),
    )
    base.update(overrides)
    return decision(**base)


class Fixture:
    def __init__(self, root):
        self.root = Path(root)
        self.source = self.root / "source.json"
        self.adjudications = self.root / "adjudications.json"
        self.output = self.root / "out"

    def write_source(self, rows):
        self.source.write_text(json.dumps(envelope(rows)))

    def write_adjudications(self, items):
        self.adjudications.write_text(json.dumps(items))

    def args(self):
        return ["--source", str(self.source), "--adjudications", str(self.adjudications),
                "--output-dir", str(self.output)]


class AdjudicationTests(unittest.TestCase):
    def with_fixture(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        return Fixture(temp.name)

    # 1. confirmed hallucination with strong evidence
    def test_confirmed_hallucination_with_strong_evidence(self):
        fixture = self.with_fixture()
        source = {("R1", "fake-pkg"): joined_row("R1", "fake-pkg")}
        record, _ = adjudicator.adjudicate_one(decision(), source)
        self.assertEqual(record["adjudication_outcome"], "CONFIRMED_HALLUCINATION")
        self.assertTrue(record["confirmed_package_hallucination"])
        self.assertTrue(record["dependency_failure"])
        self.assertEqual(record["checks"], CLEARED_CHECKS)

    # 2. unresolved when evidence insufficient
    def test_unresolved_when_evidence_insufficient(self):
        source = {("R1", "unclear-pkg"): joined_row("R1", "unclear-pkg")}
        record, _ = adjudicator.adjudicate_one(decision(
            package="unclear-pkg", outcome="UNRESOLVED", evidence_status="insufficient",
            evidence_sources=[], dependency_failure=None, installation_impact=None,
            checks=dict(INCONCLUSIVE_CHECKS)), source)
        self.assertEqual(record["adjudication_outcome"], "UNRESOLVED")
        self.assertFalse(record["confirmed_package_hallucination"])
        self.assertIsNone(record["dependency_failure"])
        self.assertEqual(record["installation_impact"], "unknown")

    # 3. namespace confusion
    def test_namespace_confusion(self):
        source = {("R1", "@wrongscope/lib"): joined_row("R1", "@wrongscope/lib")}
        checks = dict(INCONCLUSIVE_CHECKS, namespace="confirmed_mismatch",
                      normalization="external_npm_reference")
        record, _ = adjudicator.adjudicate_one(decision(
            package="@wrongscope/lib", outcome="NAMESPACE_CONFUSION", checks=checks,
            nearest_legitimate_reference="@rightscope/lib", dependency_failure=True), source)
        self.assertEqual(record["adjudication_outcome"], "NAMESPACE_CONFUSION")
        self.assertFalse(record["confirmed_package_hallucination"])
        self.assertEqual(record["nearest_legitimate_reference"], "@rightscope/lib")

    # 4. package-name confusion
    def test_package_name_confusion(self):
        source = {("R1", "expresss"): joined_row("R1", "expresss")}
        checks = dict(INCONCLUSIVE_CHECKS, normalization="external_npm_reference")
        record, _ = adjudicator.adjudicate_one(decision(
            package="expresss", outcome="PACKAGE_NAME_CONFUSION", checks=checks,
            nearest_legitimate_reference="express", dependency_failure=True), source)
        self.assertEqual(record["adjudication_outcome"], "PACKAGE_NAME_CONFUSION")
        self.assertFalse(record["confirmed_package_hallucination"])
        self.assertEqual(record["nearest_legitimate_reference"], "express")

    # 5. invalid/redundant types package
    def test_invalid_or_redundant_types_package(self):
        source = {("R1", "@types/self-typed-lib"): joined_row("R1", "@types/self-typed-lib")}
        checks = dict(INCONCLUSIVE_CHECKS, types_package="invalid_or_redundant")
        record, _ = adjudicator.adjudicate_one(decision(
            package="@types/self-typed-lib", outcome="INVALID_OR_REDUNDANT_TYPES_PACKAGE",
            checks=checks, nearest_legitimate_reference="self-typed-lib",
            dependency_failure=False, installation_impact="would_install_but_functionally_invalid"),
            source)
        self.assertEqual(record["adjudication_outcome"], "INVALID_OR_REDUNDANT_TYPES_PACKAGE")
        self.assertFalse(record["confirmed_package_hallucination"])
        self.assertFalse(record["dependency_failure"])

    # 6. ecosystem confusion
    def test_ecosystem_confusion(self):
        source = {("R1", "requests"): joined_row("R1", "requests")}
        checks = dict(INCONCLUSIVE_CHECKS, ecosystem="confirmed_other_ecosystem")
        record, _ = adjudicator.adjudicate_one(decision(
            package="requests", outcome="ECOSYSTEM_CONFUSION", checks=checks,
            nearest_legitimate_reference="PyPI:requests", dependency_failure=True), source)
        self.assertEqual(record["adjudication_outcome"], "ECOSYSTEM_CONFUSION")
        self.assertFalse(record["confirmed_package_hallucination"])

    # 7. legacy/removed package
    def test_legacy_or_removed(self):
        source = {("R1", "old-lib"): joined_row("R1", "old-lib")}
        checks = dict(INCONCLUSIVE_CHECKS, historical="prior_or_removed",
                      normalization="external_npm_reference")
        record, _ = adjudicator.adjudicate_one(decision(
            package="old-lib", outcome="LEGACY_OR_REMOVED", checks=checks,
            dependency_failure=True), source)
        self.assertEqual(record["adjudication_outcome"], "LEGACY_OR_REMOVED")
        self.assertFalse(record["confirmed_package_hallucination"])
        self.assertTrue(record["dependency_failure"])

    # 8. other dependency error
    def test_other_dependency_error(self):
        source = {("R1", "odd-case"): joined_row("R1", "odd-case")}
        record, _ = adjudicator.adjudicate_one(decision(
            package="odd-case", outcome="OTHER_DEPENDENCY_ERROR", checks=dict(INCONCLUSIVE_CHECKS),
            dependency_failure=True, installation_impact="would_install_different_package"), source)
        self.assertEqual(record["adjudication_outcome"], "OTHER_DEPENDENCY_ERROR")
        self.assertFalse(record["confirmed_package_hallucination"])
        self.assertTrue(record["dependency_failure"])

    # 9. unknown source row fails
    def test_unknown_source_row_fails(self):
        source = {("R1", "fake-pkg"): joined_row("R1", "fake-pkg")}
        with self.assertRaisesRegex(ValueError, "unknown run/package pair"):
            adjudicator.adjudicate_one(decision(run_id="R9", package="not-present"), source)

    # 10. non-review-required source fails
    def test_non_review_required_source_fails(self):
        source = {("R1", "real-pkg"): joined_row("R1", "real-pkg", adjudication_status="AUTO_VALID",
                                                  classification="VALID", review_required=False,
                                                  validation_status="exists")}
        with self.assertRaisesRegex(ValueError, "not REVIEW_REQUIRED/AMBIGUOUS"):
            adjudicator.adjudicate_one(decision(package="real-pkg"), source)

    # 11. duplicate adjudication fails
    def test_duplicate_adjudication_fails(self):
        fixture = self.with_fixture()
        fixture.write_source([joined_row("R1", "fake-pkg")])
        fixture.write_adjudications([decision(), decision()])
        with self.assertRaisesRegex(ValueError, "Duplicate adjudication"):
            adjudicator.main(fixture.args())
        self.assertFalse(fixture.output.exists())

    # 12. missing evidence for confirmed hallucination fails
    def test_missing_evidence_for_confirmed_hallucination_fails(self):
        source = {("R1", "fake-pkg"): joined_row("R1", "fake-pkg")}
        with self.assertRaisesRegex(ValueError, "conservative check"):
            adjudicator.adjudicate_one(decision(checks=dict(INCONCLUSIVE_CHECKS)), source)
        with self.assertRaisesRegex(ValueError, "Dated evidence_sources"):
            adjudicator.adjudicate_one(decision(evidence_sources=[]), source)

    # 13. deterministic output
    def test_deterministic_output(self):
        fixture = self.with_fixture()
        fixture.write_source([joined_row("R2", "zeta-pkg", order=2), joined_row("R1", "alpha-pkg", order=1)])
        fixture.write_adjudications([
            decision(run_id="R2", package="zeta-pkg"),
            decision(run_id="R1", package="alpha-pkg"),
        ])
        self.assertEqual(adjudicator.main(fixture.args()), 0)
        paths = adjudicator.output_paths(fixture.output)
        before = {key: path.read_bytes() for key, path in paths.items()}
        records = json.loads(paths["json"].read_bytes())["records"]
        self.assertEqual([row["normalized_package"] for row in records], ["alpha-pkg", "zeta-pkg"])
        self.assertEqual(adjudicator.main(fixture.args()), 0)
        after = {key: path.read_bytes() for key, path in paths.items()}
        self.assertEqual(before, after)

    # 14. provenance retained
    def test_provenance_retained(self):
        source = {("R1", "fake-pkg"): joined_row("R1", "fake-pkg")}
        record, _ = adjudicator.adjudicate_one(decision(), source)
        joined_provenance = " ".join(record["provenance"])
        self.assertIn("source_classification=AMBIGUOUS", joined_provenance)
        self.assertIn("pipe-05-classifier-1.0.0", joined_provenance)
        self.assertIn(adjudicator.TOOL_VERSION, joined_provenance)
        self.assertEqual(record["adjudication_version"], adjudicator.TOOL_VERSION)

    # 15. truncated case adjudicated but distinguishable from primary metric eligibility
    def test_truncated_case_distinguishable_from_metric_eligibility(self):
        source = {("R1", "fake-pkg"): joined_row("R1", "fake-pkg", truncated=True)}
        record, _ = adjudicator.adjudicate_one(decision(), source)
        self.assertTrue(record["source_truncated"])
        self.assertTrue(record["response_context_reference"]["truncated"])
        self.assertNotIn("metric_eligible", record)
        self.assertNotIn("phr", " ".join(record.keys()).lower())

    # 16. dependency_failure true without confirmed hallucination
    def test_dependency_failure_without_confirmed_hallucination(self):
        source = {("R1", "old-lib"): joined_row("R1", "old-lib")}
        checks = dict(INCONCLUSIVE_CHECKS, historical="prior_or_removed",
                      normalization="external_npm_reference")
        record, _ = adjudicator.adjudicate_one(decision(
            package="old-lib", outcome="LEGACY_OR_REMOVED", checks=checks,
            dependency_failure=True), source)
        self.assertTrue(record["dependency_failure"])
        self.assertFalse(record["confirmed_package_hallucination"])

    # 17. unresolved does not become a failure automatically
    def test_unresolved_is_not_a_failure_automatically(self):
        source = {("R1", "unclear-pkg"): joined_row("R1", "unclear-pkg")}
        record, _ = adjudicator.adjudicate_one(decision(
            package="unclear-pkg", outcome="UNRESOLVED", evidence_status="insufficient",
            evidence_sources=[], dependency_failure=None, installation_impact=None,
            checks=dict(INCONCLUSIVE_CHECKS)), source)
        self.assertIsNone(record["dependency_failure"])
        self.assertFalse(record["confirmed_package_hallucination"])

    # PIPE-05B.1: generated-project self-reference / local package

    # 1-7. own package.json name, README import, npm 404 -> self-reference, not a failure
    def test_self_reference_to_own_project_name(self):
        row = self_reference_row()
        source = {("R1", OWN_PROJECT): row}
        record, _ = adjudicator.adjudicate_one(self_reference_decision(), source)
        self.assertEqual(record["source_validation_status"], "not_found")
        self.assertEqual(record["current_registry_evidence"]["http_status"], 404)
        self.assertIn(OWN_PROJECT, row["occurrence_evidence"][0]["source_text"])
        self.assertEqual(record["adjudication_outcome"], "SELF_REFERENCE_OR_LOCAL_PACKAGE")
        self.assertIs(record["dependency_failure"], False)
        self.assertIs(record["confirmed_package_hallucination"], False)
        self.assertIs(record["external_dependency_eligible"], False)
        self.assertEqual(record["installation_impact"], "not_applicable_local_reference")
        evidence_record = record["self_reference_evidence"]
        self.assertEqual(evidence_record["declared_name"], OWN_PROJECT)
        self.assertEqual(evidence_record["basis"], "generated_project_own_package_name")
        self.assertEqual(evidence_record["reference_contexts"], ["documentation_example"])
        self.assertTrue(evidence_record["symbols_defined_in_response"])

    def test_self_reference_cannot_assert_failure_or_external_impact(self):
        source = {("R1", OWN_PROJECT): self_reference_row()}
        with self.assertRaisesRegex(ValueError, "dependency_failure=false"):
            adjudicator.adjudicate_one(self_reference_decision(dependency_failure=True), source)
        with self.assertRaisesRegex(ValueError, "dependency_failure=false"):
            adjudicator.adjudicate_one(self_reference_decision(dependency_failure=None), source)
        with self.assertRaisesRegex(ValueError, "not_applicable_local_reference"):
            adjudicator.adjudicate_one(self_reference_decision(
                installation_impact="would_fail_install"), source)
        with self.assertRaisesRegex(ValueError, "normalization='builtin_or_local'"):
            adjudicator.adjudicate_one(self_reference_decision(checks=dict(CLEARED_CHECKS)), source)

    # 8. unrelated nonexistent package cannot use the category without evidence
    def test_unrelated_nonexistent_package_cannot_claim_self_reference(self):
        source = {("R1", "unrelated-missing-lib"): joined_row("R1", "unrelated-missing-lib")}
        with self.assertRaisesRegex(ValueError, "requires self_reference_evidence"):
            adjudicator.adjudicate_one(self_reference_decision(
                package="unrelated-missing-lib", self_reference_evidence=None), source)
        # Evidence naming a different project name does not transfer.
        with self.assertRaisesRegex(ValueError, "declared_name equal to the adjudicated package"):
            adjudicator.adjudicate_one(self_reference_decision(
                package="unrelated-missing-lib",
                self_reference_evidence=self_reference_evidence()), source)
        with self.assertRaisesRegex(ValueError, "reference_locations"):
            adjudicator.adjudicate_one(self_reference_decision(
                package="unrelated-missing-lib",
                self_reference_evidence=self_reference_evidence(
                    declared_name="unrelated-missing-lib", reference_locations=[])), source)
        with self.assertRaisesRegex(ValueError, "basis in"):
            adjudicator.adjudicate_one(self_reference_decision(
                package="unrelated-missing-lib",
                self_reference_evidence=self_reference_evidence(
                    declared_name="unrelated-missing-lib", basis="registry_returned_404")), source)
        with self.assertRaisesRegex(ValueError, "requires evidence_status 'resolved'"):
            adjudicator.adjudicate_one(self_reference_decision(evidence_status="insufficient"), {
                ("R1", OWN_PROJECT): self_reference_row()})

    def test_local_reference_markers_reserved_for_self_reference(self):
        source = {("R1", "fake-pkg"): joined_row("R1", "fake-pkg")}
        with self.assertRaisesRegex(ValueError, "only valid for SELF_REFERENCE_OR_LOCAL_PACKAGE"):
            adjudicator.adjudicate_one(decision(
                self_reference_evidence=self_reference_evidence(declared_name="fake-pkg")), source)
        with self.assertRaisesRegex(ValueError, "reserved for SELF_REFERENCE_OR_LOCAL_PACKAGE"):
            adjudicator.adjudicate_one(decision(
                installation_impact="not_applicable_local_reference"), source)
        with self.assertRaisesRegex(ValueError, "cannot carry checks.normalization='builtin_or_local'"):
            adjudicator.adjudicate_one(decision(
                outcome="OTHER_DEPENDENCY_ERROR",
                checks=dict(INCONCLUSIVE_CHECKS, normalization="builtin_or_local")), source)

    def test_external_dependency_eligibility_by_outcome(self):
        source = {("R1", "fake-pkg"): joined_row("R1", "fake-pkg"),
                  ("R1", "unclear-pkg"): joined_row("R1", "unclear-pkg")}
        confirmed, _ = adjudicator.adjudicate_one(decision(), source)
        self.assertIs(confirmed["external_dependency_eligible"], True)
        self.assertIsNone(confirmed["self_reference_evidence"])
        unresolved, _ = adjudicator.adjudicate_one(decision(
            package="unclear-pkg", outcome="UNRESOLVED", evidence_status="insufficient",
            evidence_sources=[], dependency_failure=None, installation_impact=None,
            checks=dict(INCONCLUSIVE_CHECKS)), source)
        self.assertIsNone(unresolved["external_dependency_eligible"])

    # 9. deterministic output including a self-reference record
    def test_self_reference_deterministic_output(self):
        fixture = self.with_fixture()
        fixture.write_source([joined_row("R2", "zeta-pkg", order=2), self_reference_row()])
        fixture.write_adjudications([
            decision(run_id="R2", package="zeta-pkg"),
            self_reference_decision(self_reference_evidence=self_reference_evidence(
                reference_contexts=["test_or_script", "documentation_example", "test_or_script"],
                reference_locations=["README.md Quick Start", "scripts/demo.ts"])),
        ])
        self.assertEqual(adjudicator.main(fixture.args()), 0)
        paths = adjudicator.output_paths(fixture.output)
        before = {key: path.read_bytes() for key, path in paths.items()}
        records = json.loads(paths["json"].read_bytes())["records"]
        self.assertEqual([row["normalized_package"] for row in records], [OWN_PROJECT, "zeta-pkg"])
        self.assertEqual(records[0]["self_reference_evidence"]["reference_contexts"],
                         ["documentation_example", "test_or_script"])
        self.assertEqual([row["external_dependency_eligible"] for row in records], [False, True])
        header = paths["csv"].read_text().splitlines()[0].split(",")
        self.assertEqual(tuple(header), adjudicator.RECORD_FIELDS)
        self.assertEqual(adjudicator.main(fixture.args()), 0)
        after = {key: path.read_bytes() for key, path in paths.items()}
        self.assertEqual(before, after)

    def test_schema_declares_self_reference_outcome_and_fields(self):
        schema = json.loads((ROOT / "schemas" / "package_adjudication_pipe05b_v1.schema.json").read_text())
        self.assertIn("SELF_REFERENCE_OR_LOCAL_PACKAGE", schema["properties"]["adjudication_outcome"]["enum"])
        self.assertEqual(set(schema["required"]), set(adjudicator.RECORD_FIELDS))
        self.assertEqual(set(schema["properties"]), set(adjudicator.RECORD_FIELDS))
        self.assertEqual(schema["properties"]["adjudication_version"]["const"], adjudicator.TOOL_VERSION)
        self.assertEqual(set(schema["properties"]["adjudication_outcome"]["enum"]), adjudicator.ALL_OUTCOMES)
        self.assertEqual(set(schema["properties"]["installation_impact"]["enum"]),
                         adjudicator.INSTALLATION_IMPACTS)
        self_ref = schema["$defs"]["selfReferenceEvidence"]
        self.assertEqual(set(self_ref["required"]), adjudicator.SELF_REFERENCE_EVIDENCE_FIELDS)

    # Additional structural/integration tests

    def test_invalid_taxonomy_label_fails(self):
        source = {("R1", "fake-pkg"): joined_row("R1", "fake-pkg")}
        with self.assertRaisesRegex(ValueError, "Invalid or unsupported adjudication_outcome"):
            adjudicator.adjudicate_one(decision(outcome="DEFINITELY_HALLUCINATED"), source)

    def test_full_main_pipeline_writes_expected_envelope(self):
        fixture = self.with_fixture()
        fixture.write_source([joined_row("R1", "fake-pkg")])
        fixture.write_adjudications([decision()])
        self.assertEqual(adjudicator.main(fixture.args()), 0)
        paths = adjudicator.output_paths(fixture.output)
        data = json.loads(paths["json"].read_bytes())
        self.assertEqual(data["format_version"], "pipe-05b-adjudication-1.1.0")
        self.assertEqual(len(data["records"]), 1)
        self.assertTrue(paths["csv"].exists())

    def test_source_input_not_modified(self):
        fixture = self.with_fixture()
        fixture.write_source([joined_row("R1", "fake-pkg")])
        fixture.write_adjudications([decision()])
        before = digest(fixture.source)
        adjudicator.main(fixture.args())
        self.assertEqual(digest(fixture.source), before)

    def test_no_real_review_required_package_name_used(self):
        # Guard list of the real REVIEW_REQUIRED packages named in the PIPE-05B task
        # brief (not to be adjudicated by this infrastructure-only task). The production
        # script must never hardcode or ship a fixture referencing any of them.
        real_names = {"@types/xpath", "@xmldom/xpath", "pkcs12", "mtls-pfx-loader",
                      "mime-node", "@peculiar/asn1-rs", "@types/pdf-lib"}
        source_text = (ROOT / "scripts" / "adjudicate_review_required_packages.py").read_text()
        for name in real_names:
            self.assertNotIn(name, source_text)
        synthetic_packages = {"fake-pkg", "unclear-pkg", "@wrongscope/lib", "expresss",
                              "@types/self-typed-lib", "requests", "old-lib", "odd-case",
                              "not-present", "real-pkg", "zeta-pkg", "alpha-pkg",
                              OWN_PROJECT, "unrelated-missing-lib"}
        self.assertTrue(real_names.isdisjoint(synthetic_packages))

    def test_no_network_or_subprocess_code(self):
        source = (ROOT / "scripts" / "adjudicate_review_required_packages.py").read_text()
        self.assertNotIn("urllib.request", source)
        self.assertNotIn("subprocess", source)
        self.assertNotIn("npm install", source)


if __name__ == "__main__":
    unittest.main()
