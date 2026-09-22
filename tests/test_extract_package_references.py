#!/usr/bin/env python3
"""Synthetic tests for PIPE-03 explicit npm package-reference extraction."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import extract_package_references as extractor


def row(run_id="RUN-01", order=1, status="completed", truncated=False, artifact="data/final/raw/RUN-01/response.md"):
    return {
        "run_id": run_id, "collection_order": order, "model_condition_id": "M1",
        "task_id": "TASK-01", "category": "AUTH-FED", "collection_status": status,
        "completion_status": "TRUNCATED" if truncated else "COMPLETED", "truncated": truncated,
        "response_artifact_path": artifact,
    }


class PackageReferenceExtractorTests(unittest.TestCase):
    def records(self, text):
        return extractor.extract_response_occurrences(text, row())

    def packages(self, text):
        return [(record["normalized_package"], record["source_type"], record["version_specifier"]) for record in self.records(text)]

    def test_import_forms_and_subpath_normalization(self):
        records = self.packages("""import express from 'express';
import { map } from "lodash/fp";
import '@scope/package';
import { x } from '@scope/package/subpath';
""")
        self.assertEqual(records, [
            ("express", "es_import", None), ("lodash", "es_import", None),
            ("@scope/package", "es_import", None), ("@scope/package", "es_import", None),
        ])

    def test_multiline_named_imports_scoped_aliases_comments_and_subpaths(self):
        records = self.packages("""import {
  primary as renamed,
  // from 'not-a-package' is a comment, not the module clause
  secondary,
} from "fido2-lib";
import type {
  RegistrationResponseJSON,
}   from '@simplewebauthn/types';
import {
  asn1,
} from "@peculiar/asn1-schema/models";
import {
  verifyRegistrationResponse,
} from '@simplewebauthn/server';
import {
  jwtVerify,
} from 'jose';
""")
        self.assertEqual(records, [
            ("fido2-lib", "es_import", None),
            ("@simplewebauthn/types", "es_import", None),
            ("@peculiar/asn1-schema", "es_import", None),
            ("@simplewebauthn/server", "es_import", None),
            ("jose", "es_import", None),
        ])

    def test_multiline_builtin_imports_remain_excluded(self):
        records = self.packages("""import {
  createHash,
} from 'crypto';
import {
  randomBytes,
} from 'node:crypto';
""")
        self.assertEqual(records, [])

    def test_multiline_default_and_named_import(self):
        self.assertEqual(self.packages("""import defaultExport,
  { named as renamed }
  from 'actual-package';
"""), [("actual-package", "es_import", None)])

    def test_multiline_import_evidence_and_deterministic_ordering(self):
        text = """import alpha from 'alpha';
import {
  beta as renamedBeta,
} from '@scope/beta/subpath';
const gamma = await import('gamma');
"""
        first = self.records(text)
        second = self.records(text)
        self.assertEqual(first, second)
        self.assertEqual(
            [record["normalized_package"] for record in first],
            ["alpha", "@scope/beta", "gamma"],
        )
        self.assertEqual([record["occurrence_index"] for record in first], [1, 2, 3])
        self.assertEqual([record["source_offset"] for record in first], sorted(record["source_offset"] for record in first))
        self.assertIn("} from '@scope/beta/subpath';", first[1]["source_text"])

    def test_require_and_dynamic_import(self):
        records = self.packages("const x = require('express');\nconst y = await import('@scope/pkg/subpath');")
        self.assertEqual(records, [("express", "require", None), ("@scope/pkg", "dynamic_import", None)])

    def test_npm_install_one_multiple_flags_and_versions(self):
        records = self.packages("""npm install express
npm i lodash @scope/package
npm install --save cookie-parser
npm install -D jest
npm install express@4.21.0 @scope/package@1.2.3
""")
        self.assertEqual(records, [
            ("express", "npm_install", None), ("lodash", "npm_install", None),
            ("@scope/package", "npm_install", None), ("cookie-parser", "npm_install", None),
            ("jest", "npm_install", None), ("express", "npm_install", "4.21.0"),
            ("@scope/package", "npm_install", "1.2.3"),
        ])

    def test_all_package_json_dependency_sections(self):
        records = self.packages('''{
  "dependencies": {"express": "^4.0.0"},
  "devDependencies": {"jest": "29.0.0"},
  "peerDependencies": {"react": ">=18"},
  "optionalDependencies": {"fsevents": "2.3.0"}
}''')
        self.assertEqual(records, [
            ("express", "package_json", "^4.0.0"), ("jest", "package_json", "29.0.0"),
            ("react", "package_json", ">=18"), ("fsevents", "package_json", "2.3.0"),
        ])

    def test_duplicate_occurrences_are_preserved_and_unique_view_deduplicates(self):
        occurrences = self.records("npm install fake-auth\nimport auth from 'fake-auth';\nrequire('fake-auth');")
        self.assertEqual([item["occurrence_index"] for item in occurrences], [1, 2, 3])
        unique = extractor.build_unique_view(occurrences)
        self.assertEqual(len(unique), 1)
        self.assertEqual(unique[0]["normalized_package"], "fake-auth")
        self.assertEqual(unique[0]["occurrence_count"], 3)
        self.assertEqual(unique[0]["source_types"], ["es_import", "require", "npm_install"])

    def test_builtin_and_local_url_exclusions(self):
        records = self.records("""import fs from 'fs';
import crypto from 'node:crypto';
import './local';
import '/srv/app';
import 'file:///tmp/x';
import 'https://example.test/pkg';
import valid from 'valid-package';
require('path/posix');
""")
        self.assertEqual([(r["normalized_package"], r["source_type"]) for r in records], [("valid-package", "es_import")])

    def test_malformed_fence_and_prose_do_not_create_inferences(self):
        text = """A package-like word fake-package appears in normal prose.
```json
{"dependencies": {"recoverable": "1.0.0"}}
```typescript
import broken from 'not-closed
"""
        self.assertEqual(self.packages(text), [("recoverable", "package_json", "1.0.0")])

    def test_deterministic_ordering_and_repeated_runs(self):
        text = """import z from 'zeta';
npm install alpha beta
const q = require('gamma');
"""
        first = self.records(text)
        second = self.records(text)
        self.assertEqual(first, second)
        self.assertEqual([record["normalized_package"] for record in first], ["zeta", "alpha", "beta", "gamma"])
        self.assertEqual([record["occurrence_index"] for record in first], [1, 2, 3, 4])

    def test_inventory_skips_pending_and_extracts_truncated_with_marker(self):
        with tempfile.TemporaryDirectory() as tmp_name:
            tmp = Path(tmp_name)
            raw_root = tmp / "raw"
            (raw_root / "DONE").mkdir(parents=True)
            (raw_root / "TRUNC").mkdir(parents=True)
            (raw_root / "DONE" / "response.md").write_text("import x from 'done-package';", encoding="utf-8")
            (raw_root / "TRUNC" / "response.md").write_text("require('truncated-package');", encoding="utf-8")
            inventory = [
                row("PENDING", 1, "pending", None, None),
                row("DONE", 2, "completed", False, "data/final/raw/DONE/response.md"),
                row("TRUNC", 3, "truncated", True, "data/final/raw/TRUNC/response.md"),
            ]
            records = extractor.build_occurrences(inventory, raw_root, root=tmp)
        self.assertEqual([record["run_id"] for record in records], ["DONE", "TRUNC"])
        self.assertFalse(records[0]["truncated"])
        self.assertTrue(records[1]["truncated"])

    def test_output_is_json_serializable_with_schema_fields(self):
        occurrence = self.records("import x from 'package-name';")[0]
        unique = extractor.build_unique_view([occurrence])[0]
        self.assertEqual(set(occurrence), set(extractor.OCCURRENCE_COLUMNS))
        self.assertEqual(set(unique), set(extractor.UNIQUE_COLUMNS))
        json.dumps([occurrence, unique])


if __name__ == "__main__":
    unittest.main()
