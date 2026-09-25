#!/usr/bin/env python3
"""Synthetic, offline tests for PIPE-05 package-name classification."""

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import classify_npm_packages as classifier


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unique_row(run, package, order, count=1):
    return {
        "run_id": run, "collection_order": order, "model_condition_id": "M1",
        "task_id": "TASK", "category": "AUTH-FED", "normalized_package": package,
        "first_occurrence_index": 1, "occurrence_count": count,
        "source_types": ["es_import"], "extractor_version": "pipe-03-test",
    }


def occurrence_row(run, package, order, index=1, truncated=False):
    return {
        "run_id": run, "collection_order": order, "model_condition_id": "M1",
        "task_id": "TASK", "category": "AUTH-FED",
        "collection_status": "truncated" if truncated else "completed",
        "completion_status": "TRUNCATED" if truncated else "COMPLETED",
        "truncated": truncated, "response_artifact_path": f"raw/{run}/response.md",
        "occurrence_index": index, "original_reference": package,
        "normalized_package": package, "source_type": "es_import",
        "source_text": f'import x from "{package}"', "source_offset": 10 * index,
        "version_specifier": None, "extractor_version": "pipe-03-test",
    }


def registry_row(package, state):
    status = {"exists": 200, "not_found": 404, "unresolved": 503}[state]
    summary = {"exists": "Registry metadata returned the exact package name",
               "not_found": "Official registry returned package-not-found JSON",
               "unresolved": "Registry HTTP 503"}[state]
    return {
        "normalized_package": package, "validation_status": state,
        "registry": "https://registry.npmjs.org",
        "request_url": "https://registry.npmjs.org/" + package,
        "http_status": status, "checked_at": "2026-09-21T06:00:00Z",
        "validator_version": "pipe-04-npm-validator-1.0.0",
        "evidence_summary": summary,
        "error_type": "server_error" if state == "unresolved" else None,
        "retry_count": 0, "history": [],
    }


def review(package="missing", label="CONFIRMED_HALLUCINATION", checks=None):
    return {
        "normalized_package": package, "classification": label,
        "reviewer_id": "reviewer-1", "reviewed_at": "2026-09-22T00:00:00Z",
        "rationale": "Documented review of registry absence and historical identity",
        "evidence": [{"source": "dated-authoritative-evidence", "summary": "Reviewed history and name identity",
                      "checked_at": "2026-09-22T00:00:00Z"}],
        "checks": checks or {"historical": "no_prior_evidence",
                             "normalization": "external_npm_reference", "ambiguity": "cleared"},
    }


class Fixture:
    def __init__(self, root):
        self.root = Path(root)
        self.unique = self.root / "unique.json"
        self.occurrences = self.root / "occurrences.json"
        self.validation = self.root / "validation.json"
        self.joined = self.root / "joined.json"
        self.output = self.root / "out"

    def write(self, states=None, malformed=None):
        states = states or {"real": "exists", "missing": "not_found", "unstable": "unresolved"}
        unique = [unique_row("R2", "real", 2), unique_row("R1", "real", 1, 2),
                  unique_row("R1", "missing", 1), unique_row("R2", "unstable", 2)]
        occurrences = [occurrence_row("R1", "real", 1, 1),
                       occurrence_row("R1", "real", 1, 2),
                       occurrence_row("R1", "missing", 1),
                       occurrence_row("R2", "real", 2, truncated=True),
                       occurrence_row("R2", "unstable", 2, truncated=True)]
        self.unique.write_text(json.dumps(unique))
        self.occurrences.write_text(json.dumps(occurrences))
        uh, oh = digest(self.unique), digest(self.occurrences)
        packages = []
        for name, state in states.items():
            item = registry_row(name, state)
            item["source_input_hash"] = uh
            item["source_occurrences_hash"] = oh
            packages.append(item)
        if malformed:
            malformed(packages)
        joined = []
        for row in unique:
            item = next(package for package in packages if package["normalized_package"] == row["normalized_package"])
            source = next(x for x in occurrences if x["run_id"] == row["run_id"] and
                          x["normalized_package"] == row["normalized_package"])
            joined.append({**row, **{field: source[field] for field in (
                "collection_status", "completion_status", "truncated", "response_artifact_path")},
                **{field: item[field] for field in classifier.REGISTRY_FIELDS},
                "source_input_hash": uh, "source_occurrences_hash": oh})
        envelope = {"format_version": "pipe-04-evidence-1.0.0",
                    "source_input_hash": uh, "source_occurrences_hash": oh}
        self.validation.write_text(json.dumps({**envelope, "records": packages}))
        self.joined.write_text(json.dumps({**envelope, "records": joined}))
        return unique, occurrences, packages, joined

    def args(self, adjudications=None):
        args = ["--unique", str(self.unique), "--occurrences", str(self.occurrences),
                "--validation", str(self.validation), "--validation-joined", str(self.joined),
                "--output-dir", str(self.output)]
        if adjudications:
            args.extend(["--adjudications", str(adjudications)])
        return args


class ClassificationTests(unittest.TestCase):
    def with_fixture(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        fixture = Fixture(temp.name)
        fixture.write()
        return fixture

    def build(self, fixture):
        data = classifier.validated_inputs(fixture.unique, fixture.occurrences,
                                           fixture.validation, fixture.joined)
        unique, occurrences, packages, joined, by_key, hashes = data
        rows, joined_rows = classifier.build_records(unique, occurrences, packages, joined,
                                                     by_key, {})
        return rows, joined_rows, hashes

    def test_exists_is_valid_package_name_only(self):
        rows, _, _ = self.build(self.with_fixture())
        real = next(row for row in rows if row["normalized_package"] == "real")
        self.assertEqual(real["classification"], "VALID")
        self.assertEqual(real["validation_status"], "exists")
        self.assertEqual(real["adjudication_status"], "AUTO_VALID")
        self.assertIn("package name", real["classification_basis"].lower())

    def test_not_found_is_ambiguous_review_required(self):
        rows, _, _ = self.build(self.with_fixture())
        missing = next(row for row in rows if row["normalized_package"] == "missing")
        self.assertEqual(missing["classification"], "AMBIGUOUS")
        self.assertEqual(missing["validation_status"], "not_found")
        self.assertEqual(missing["adjudication_status"], "REVIEW_REQUIRED")
        self.assertTrue(missing["review_required"])
        self.assertIsNone(missing["reviewer_id"])

    def test_unresolved_has_no_research_classification(self):
        rows, _, _ = self.build(self.with_fixture())
        unstable = next(row for row in rows if row["normalized_package"] == "unstable")
        self.assertEqual(unstable["validation_status"], "unresolved")
        self.assertIsNone(unstable["classification"])
        self.assertEqual(unstable["adjudication_status"], "VALIDATION_UNRESOLVED")

    def test_repeated_package_and_occurrences_preserved(self):
        rows, joined, _ = self.build(self.with_fixture())
        real = next(row for row in rows if row["normalized_package"] == "real")
        self.assertEqual(real["run_ids"], ["R1", "R2"])
        self.assertEqual(len(real["occurrence_evidence"]), 3)
        self.assertEqual(len([row for row in joined if row["normalized_package"] == "real"]), 2)
        self.assertEqual(len(next(row for row in joined if row["run_id"] == "R1" and
                                  row["normalized_package"] == "real")["occurrence_evidence"]), 2)

    def test_source_evidence_and_raw_path_traceable(self):
        rows, joined, _ = self.build(self.with_fixture())
        missing = next(row for row in rows if row["normalized_package"] == "missing")
        evidence = missing["occurrence_evidence"][0]
        self.assertEqual(evidence["source_text"], 'import x from "missing"')
        self.assertEqual(evidence["source_offset"], 10)
        self.assertEqual(evidence["response_artifact_path"], "raw/R1/response.md")
        self.assertEqual(next(row for row in joined if row["normalized_package"] == "missing")["http_status"], 404)

    def test_truncation_is_preserved_not_filtered(self):
        _, joined, _ = self.build(self.with_fixture())
        truncated = [row for row in joined if row["truncated"]]
        self.assertEqual(len(truncated), 2)
        self.assertTrue(all(row["occurrence_evidence"][0]["truncated"] for row in truncated))

    def test_review_vocabulary_rejects_unresolved_as_classification(self):
        fixture = self.with_fixture()
        path = fixture.root / "review.json"
        path.write_text(json.dumps([review(label="UNRESOLVED")]))
        _, _, packages, _, _, _ = classifier.validated_inputs(
            fixture.unique, fixture.occurrences, fixture.validation, fixture.joined)
        with self.assertRaisesRegex(ValueError, "classification"):
            classifier.load_adjudications(path, {x["normalized_package"]: x for x in packages})

    def test_confirmed_review_requires_conservative_checks(self):
        fixture = self.with_fixture()
        path = fixture.root / "review.json"
        path.write_text(json.dumps([review(checks={"historical": "inconclusive",
                                                   "normalization": "external_npm_reference",
                                                   "ambiguity": "cleared"})]))
        _, _, packages, _, _, _ = classifier.validated_inputs(
            fixture.unique, fixture.occurrences, fixture.validation, fixture.joined)
        with self.assertRaisesRegex(ValueError, "conservative checks"):
            classifier.load_adjudications(path, {x["normalized_package"]: x for x in packages})

    def test_documented_review_can_distinguish_legacy_and_builtin(self):
        fixture = self.with_fixture()
        packages = classifier.validated_inputs(fixture.unique, fixture.occurrences,
                                               fixture.validation, fixture.joined)[2]
        mapping = {x["normalized_package"]: x for x in packages}
        path = fixture.root / "review.json"
        legacy = review(label="LEGACY_OR_REMOVED", checks={
            "historical": "prior_or_removed", "normalization": "external_npm_reference",
            "ambiguity": "cleared"})
        path.write_text(json.dumps([legacy]))
        reviews, _ = classifier.load_adjudications(path, mapping)
        self.assertEqual(classifier.classify_package(mapping["missing"], reviews["missing"])["classification"],
                         "LEGACY_OR_REMOVED")
        self.assertEqual(classifier.classify_package(mapping["missing"], reviews["missing"])["review_checks"],
                         legacy["checks"])
        builtin = review(label="BUILTIN_OR_LOCAL", checks={
            "historical": "inconclusive", "normalization": "builtin_or_local",
            "ambiguity": "cleared"})
        path.write_text(json.dumps([builtin]))
        reviews, _ = classifier.load_adjudications(path, mapping)
        self.assertEqual(classifier.classify_package(mapping["missing"], reviews["missing"])["classification"],
                         "BUILTIN_OR_LOCAL")

    def test_deterministic_ordering_and_rerun_bytes(self):
        fixture = self.with_fixture()
        self.assertEqual(classifier.main(fixture.args()), 0)
        paths = classifier.output_paths(fixture.output)
        before = {key: path.read_bytes() for key, path in paths.items()}
        self.assertEqual(classifier.main(fixture.args()), 0)
        self.assertEqual(before, {key: path.read_bytes() for key, path in paths.items()})
        records = json.loads(paths["package_json"].read_text())["records"]
        self.assertEqual([row["normalized_package"] for row in records], ["missing", "real", "unstable"])

    def test_inputs_not_modified(self):
        fixture = self.with_fixture()
        before = {path: digest(path) for path in (fixture.unique, fixture.occurrences,
                                                  fixture.validation, fixture.joined)}
        classifier.main(fixture.args())
        self.assertEqual(before, {path: digest(path) for path in before})

    def test_malformed_registry_evidence_fails_safely(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        fixture = Fixture(temp.name)
        fixture.write(malformed=lambda packages: packages[0].update({"http_status": 404}))
        with self.assertRaisesRegex(ValueError, "Malformed exists evidence"):
            classifier.main(fixture.args())
        self.assertFalse(fixture.output.exists())

    def test_mismatched_source_hash_fails_safely(self):
        fixture = self.with_fixture()
        data = json.loads(fixture.validation.read_text())
        data["source_input_hash"] = "0" * 64
        fixture.validation.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            classifier.main(fixture.args())

    def test_registry_endpoint_must_match_name(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        fixture = Fixture(temp.name)
        fixture.write(malformed=lambda packages: packages[0].update({
            "request_url": "https://registry.npmjs.org/different"}))
        with self.assertRaisesRegex(ValueError, "endpoint/name mismatch"):
            classifier.main(fixture.args())

    def test_review_requires_dated_evidence(self):
        fixture = self.with_fixture()
        item = review()
        item["evidence"] = []
        path = fixture.root / "review.json"
        path.write_text(json.dumps([item]))
        packages = classifier.validated_inputs(fixture.unique, fixture.occurrences,
                                               fixture.validation, fixture.joined)[2]
        with self.assertRaisesRegex(ValueError, "Dated review evidence"):
            classifier.load_adjudications(path, {x["normalized_package"]: x for x in packages})

    def test_no_network_or_subprocess_code(self):
        source = (ROOT / "scripts" / "classify_npm_packages.py").read_text()
        self.assertNotIn("urllib.request", source)
        self.assertNotIn("subprocess", source)
        self.assertNotIn("npm install", source)


if __name__ == "__main__":
    unittest.main()
