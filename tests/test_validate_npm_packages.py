#!/usr/bin/env python3
"""Offline, synthetic tests for PIPE-04 registry evidence collection."""

import ast
import json
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.error import URLError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_npm_packages as validator


def response(status, body=None, headers=None):
    if body is None:
        body = {"error": "Not found"} if status == 404 else {"name": "express"}
    return status, json.dumps(body).encode(), headers or {}


class FakeTransport:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.urls = []

    def __call__(self, url, timeout):
        self.urls.append(url)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def unique_row(run="R1", package="express", order=1):
    return {
        "run_id": run, "collection_order": order, "model_condition_id": "M1",
        "task_id": "TASK", "category": "AUTH-FED", "normalized_package": package,
        "first_occurrence_index": 1, "occurrence_count": 1,
        "source_types": ["es_import"], "extractor_version": "pipe-03-test",
    }


def occurrence_row(run="R1", package="express", order=1, truncated=False):
    return {
        **unique_row(run, package, order), "occurrence_index": 1,
        "collection_status": "truncated" if truncated else "completed",
        "completion_status": "TRUNCATED" if truncated else "COMPLETED",
        "truncated": truncated, "response_artifact_path": f"raw/{run}/response.md",
    }


class ValidationTests(unittest.TestCase):
    def validate(self, package="express", outcomes=None, previous=None):
        transport = FakeTransport(outcomes or [response(200, {"name": package})])
        sleeps = []
        result = validator.validate_package(package, "a" * 64, "b" * 64,
                                            transport, sleeps.append,
                                            lambda: "2026-09-21T00:00:00Z", previous)
        return result, transport, sleeps

    def test_exists_200_and_provenance(self):
        result, transport, _ = self.validate()
        self.assertEqual(result["validation_status"], "exists")
        self.assertEqual(result["http_status"], 200)
        self.assertEqual(result["source_input_hash"], "a" * 64)
        self.assertEqual(result["source_occurrences_hash"], "b" * 64)
        self.assertEqual(result["checked_at"], "2026-09-21T00:00:00Z")
        self.assertEqual(len(transport.urls), 1)

    def test_scoped_package_url_is_one_encoded_component(self):
        result, transport, _ = self.validate("@scope/pkg")
        self.assertEqual(transport.urls, ["https://registry.npmjs.org/%40scope%2Fpkg"])
        self.assertEqual(result["validation_status"], "exists")

    def test_clean_404_is_not_found_without_retry(self):
        result, transport, sleeps = self.validate(outcomes=[response(404)])
        self.assertEqual(result["validation_status"], "not_found")
        self.assertEqual(result["retry_count"], 0)
        self.assertEqual(len(transport.urls), 1)
        self.assertEqual(sleeps, [])

    def test_malformed_404_is_unresolved(self):
        result, _, _ = self.validate(outcomes=[response(404, {"error": "proxy failure"})])
        self.assertEqual(result["validation_status"], "unresolved")

    def test_timeout_exhaustion_unresolved(self):
        result, transport, sleeps = self.validate(outcomes=[TimeoutError()] * 3)
        self.assertEqual(result["validation_status"], "unresolved")
        self.assertEqual(result["error_type"], "TimeoutError")
        self.assertEqual(result["retry_count"], 2)
        self.assertEqual(len(transport.urls), 3)
        self.assertEqual(sleeps, [0.5, 1.0])

    def test_connection_error_unresolved(self):
        result, _, _ = self.validate(outcomes=[URLError("DNS")] * 3)
        self.assertEqual(result["validation_status"], "unresolved")
        self.assertEqual(result["error_type"], "URLError")

    def test_429_retry_exhaustion_unresolved(self):
        result, transport, sleeps = self.validate(outcomes=[response(429)] * 3)
        self.assertEqual(result["validation_status"], "unresolved")
        self.assertEqual(result["error_type"], "rate_limited")
        self.assertEqual(len(transport.urls), 3)
        self.assertEqual(sleeps, [0.5, 1.0])

    def test_429_retry_after_too_long_does_not_hammer(self):
        result, transport, sleeps = self.validate(outcomes=[response(429, headers={"Retry-After": "120"})])
        self.assertEqual(result["validation_status"], "unresolved")
        self.assertEqual(result["error_type"], "retry_after_out_of_bounds")
        self.assertEqual(len(transport.urls), 1)
        self.assertEqual(sleeps, [])

    def test_500_and_503_retry_then_unresolved(self):
        result, transport, _ = self.validate(outcomes=[response(500), response(503), response(503)])
        self.assertEqual(result["validation_status"], "unresolved")
        self.assertEqual(result["http_status"], 503)
        self.assertEqual(len(transport.urls), 3)

    def test_malformed_200_is_unresolved_without_retry(self):
        result, transport, _ = self.validate(outcomes=[(200, b"not JSON", {})])
        self.assertEqual(result["validation_status"], "unresolved")
        self.assertEqual(result["error_type"], "malformed_metadata")
        self.assertEqual(len(transport.urls), 1)

    def test_mismatched_metadata_is_unresolved(self):
        result, _, _ = self.validate(outcomes=[response(200, {"name": "other"})])
        self.assertEqual(result["validation_status"], "unresolved")

    def test_oversized_metadata_is_unresolved(self):
        result, _, _ = self.validate(outcomes=[(200, b"x" * (validator.MAX_METADATA_BYTES + 1), {})])
        self.assertEqual(result["validation_status"], "unresolved")
        self.assertEqual(result["error_type"], "oversized_response")

    def test_transient_retry_succeeds(self):
        result, transport, sleeps = self.validate(outcomes=[response(503), response(200)])
        self.assertEqual(result["validation_status"], "exists")
        self.assertEqual(result["retry_count"], 1)
        self.assertEqual(len(transport.urls), 2)
        self.assertEqual(sleeps, [0.5])

    def test_deduplicated_package_calls_and_join(self):
        unique = [unique_row("R2", "express", 2), unique_row("R1", "express", 1),
                  unique_row("R3", "@scope/pkg", 3)]
        by_key = {(row["run_id"], row["normalized_package"]): [
            occurrence_row(row["run_id"], row["normalized_package"], row["collection_order"],
                           row["run_id"] == "R3")] for row in unique}
        transport = FakeTransport([response(200, {"name": "@scope/pkg"}),
                                   response(200, {"name": "express"})])
        records, joined, requested = validator.build_outputs(
            unique, by_key, "a" * 64, "b" * 64, {}, transport,
            lambda _: None, lambda: "2026-09-21T00:00:00Z")
        self.assertEqual(requested, 2)
        self.assertEqual(len(transport.urls), 2)
        self.assertEqual([r["normalized_package"] for r in records], ["@scope/pkg", "express"])
        self.assertEqual([r["run_id"] for r in joined], ["R1", "R2", "R3"])
        self.assertEqual(joined[0]["checked_at"], joined[1]["checked_at"])
        self.assertTrue(joined[2]["truncated"])

    def test_cache_resume_reuses_resolved_and_unresolved_by_default(self):
        rows = [unique_row()]
        keys = {("R1", "express"): [occurrence_row()]}
        existing, _, _ = self.validate(outcomes=[response(404)])
        transport = FakeTransport([])
        first, joined, requested = validator.build_outputs(
            rows, keys, "a" * 64, "b" * 64, {"express": existing}, transport,
            lambda _: None, lambda: "later")
        self.assertEqual(requested, 0)
        self.assertEqual(first[0], existing)
        self.assertEqual(joined[0]["validation_status"], "not_found")
        unresolved, _, _ = self.validate(outcomes=[(200, b"bad", {})])
        second, _, requested = validator.build_outputs(
            rows, keys, "a" * 64, "b" * 64, {"express": unresolved}, transport,
            lambda _: None, lambda: "later")
        self.assertEqual(requested, 0)
        self.assertEqual(second[0], unresolved)

    def test_explicit_unresolved_retry_preserves_history(self):
        old, _, _ = self.validate(outcomes=[(200, b"bad", {})])
        rows = [unique_row()]
        keys = {("R1", "express"): [occurrence_row()]}
        transport = FakeTransport([response(200)])
        records, _, requested = validator.build_outputs(
            rows, keys, "a" * 64, "b" * 64, {"express": old}, transport,
            lambda _: None, lambda: "2026-09-22T00:00:00Z",
            retry_unresolved=True)
        new = records[0]
        self.assertEqual(requested, 1)
        self.assertEqual(new["validation_status"], "exists")
        self.assertEqual(new["history"][0]["error_type"], "malformed_metadata")

    def test_input_hash_and_cache_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            u = root / "unique.json"
            o = root / "occ.json"
            u.write_text(json.dumps([unique_row()]))
            o.write_text(json.dumps([occurrence_row()]))
            rows, keys, uhash, ohash = validator.load_inputs(u, o)
            self.assertEqual(len(rows), 1)
            self.assertEqual(len(keys), 1)
            self.assertEqual(uhash, validator.sha256_bytes(u.read_bytes()))
            record, _, _ = self.validate()
            record["source_input_hash"] = uhash
            record["source_occurrences_hash"] = ohash
            paths = validator.output_paths(root)
            validator.write_outputs(paths, [record], [{**rows[0], **{
                "collection_status": "completed", "completion_status": "COMPLETED",
                "truncated": False, "response_artifact_path": "raw/R1/response.md",
                **{field: record[field] for field in validator.JOIN_FIELDS if field in record}}}],
                uhash, ohash)
            cache = validator.load_cache(paths["package_json"], uhash, ohash, {"express"})
            self.assertEqual(cache["express"], record)
            with self.assertRaises(ValueError):
                validator.load_cache(paths["package_json"], "f" * 64, ohash, {"express"})
            for path in paths.values():
                self.assertTrue(path.exists())

    def test_ordering_and_serialization_are_deterministic(self):
        rows = [unique_row("R2", "express", 2), unique_row("R1", "express", 1)]
        keys = {(r["run_id"], "express"): [occurrence_row(r["run_id"], "express", r["collection_order"])] for r in rows}
        cached, _, _ = self.validate()
        first = validator.build_outputs(rows, keys, "a" * 64, "b" * 64,
                                        {"express": cached}, FakeTransport([]), lambda _: None)
        second = validator.build_outputs(list(reversed(rows)), keys, "a" * 64, "b" * 64,
                                         {"express": cached}, FakeTransport([]), lambda _: None)
        self.assertEqual(first, second)
        self.assertEqual(validator.csv_bytes(first[0], validator.PACKAGE_FIELDS),
                         validator.csv_bytes(second[0], validator.PACKAGE_FIELDS))

    def test_no_install_or_subprocess_and_cli_default_has_no_network(self):
        source = (ROOT / "scripts" / "validate_npm_packages.py").read_text()
        tree = ast.parse(source)
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        self.assertFalse(any(any(alias.name == "subprocess" for alias in node.names)
                             for node in imports if isinstance(node, ast.Import)))
        self.assertNotIn("npm install", source)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            u, o = root / "unique.json", root / "occ.json"
            u.write_text(json.dumps([unique_row()]))
            o.write_text(json.dumps([occurrence_row()]))
            self.assertEqual(validator.main(["--input", str(u), "--occurrences", str(o),
                                             "--output-dir", str(root)]), 0)
            self.assertFalse(any(root.glob("npm_package_validation*")))


if __name__ == "__main__":
    unittest.main()
