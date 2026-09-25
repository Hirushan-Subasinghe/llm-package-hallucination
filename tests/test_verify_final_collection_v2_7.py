"""Deterministic tests for the read-only FINAL_COMPLETION_CHECK verifier.

Unit tests use small synthetic fixtures in temporary directories; they never
touch frozen inputs or raw evidence.  Integration tests run the verifier
against the consolidated canonical-worktree evidence and confirm that it
writes nothing and leaves the frozen v2.7 script and state unchanged.
"""

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import create_experiment_freeze_v2_7 as frozen
import verify_final_collection_v2_7 as final

sha = lambda content: hashlib.sha256(content).hexdigest()


def entry(run_id, model, interface, status, evidence="present", order=1):
    return {"cohort_order": order, "run_id": run_id, "model_condition_id": model,
            "collection_interface": interface, "status": status,
            "evidence": None if evidence is None else {"path": run_id}}


def real_rows_and_state():
    rows = frozen.final_study_rows()
    frozen_state = json.loads(frozen.STATE.read_text(encoding="utf-8"))
    live = frozen.derive_collection_state(rows, frozen_state["derived_at_utc"])
    live["source_v2_6_state_snapshot"] = frozen_state["source_v2_6_state_snapshot"]
    return rows, frozen_state, live


class DesignTests(unittest.TestCase):
    def setUp(self):
        self.rows = frozen.final_study_rows()
        self.model_set = json.loads(frozen.MODEL_SET.read_text(encoding="utf-8"))

    def test_frozen_design_passes(self):
        summary = final.check_design(self.rows, self.model_set)
        self.assertEqual(summary["rows_per_model"], {"M1": 90, "M3": 90, "M4": 90})
        self.assertEqual(summary["interface"], {"api": 140, "manual": 130})
        self.assertEqual(summary["m2_rows"], 0)

    def test_m2_row_is_rejected(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["model_condition_id"] = "M2"
        with self.assertRaises(ValueError):
            final.check_design(rows, self.model_set)

    def test_missing_row_is_rejected(self):
        with self.assertRaises(ValueError):
            final.check_design(self.rows[:-1], self.model_set)

    def test_model_set_with_m2_is_rejected(self):
        model_set = copy.deepcopy(self.model_set)
        model_set["models"].append({"condition_id": "M2"})
        with self.assertRaisesRegex(final.VerificationError, "exactly M1, M3, M4"):
            final.check_design(self.rows, model_set)


class FinalStatusTests(unittest.TestCase):
    def build(self, api=None, manual=None):
        api = api or final.EXPECTED_API_STATUS
        manual = manual or final.EXPECTED_MANUAL_COMPLETED
        entries = []
        for status, count in api.items():
            entries += [entry(f"A-{status}-{i}", "M1", "api", status) for i in range(count)]
        for model, count in manual.items():
            entries += [entry(f"M-{model}-{i}", model, "manual", "completed") for i in range(count)]
        return entries

    def test_expected_counts_pass(self):
        counts = final.check_final_statuses(self.build())
        self.assertEqual(counts["api"], {"completed": 105, "truncated": 16, "failed": 19, "pending": 0})
        self.assertEqual(counts["manual_completed_by_model"], {"M1": 50, "M3": 49, "M4": 31})

    def test_pending_api_row_fails(self):
        entries = self.build()
        entries[0]["status"] = "pending"
        with self.assertRaisesRegex(final.VerificationError, "API statuses"):
            final.check_final_statuses(entries)

    def test_unknown_api_status_fails(self):
        entries = self.build()
        entries[0]["status"] = "interrupted"
        with self.assertRaisesRegex(final.VerificationError, "API statuses"):
            final.check_final_statuses(entries)

    def test_pending_manual_row_fails(self):
        entries = self.build()
        entries[-1]["status"] = "pending"
        with self.assertRaisesRegex(final.VerificationError, "manual completion"):
            final.check_final_statuses(entries)


class TransitionTests(unittest.TestCase):
    def states(self):
        before = {"rows": [entry("A", "M1", "api", "truncated", order=1),
                           entry("B", "M3", "manual", "pending", evidence=None, order=2)]}
        after = {"rows": [entry("A", "M1", "api", "truncated", order=1),
                          entry("B", "M3", "manual", "completed", order=2)]}
        return before, after

    def test_only_manual_pending_to_completed_is_allowed(self):
        before, after = self.states()
        self.assertEqual(final.check_transitions(before, after),
                         {"api:truncated->truncated": 1, "manual:pending->completed": 1})

    def test_api_status_change_fails(self):
        before, after = self.states()
        after["rows"][0]["status"] = "completed"
        with self.assertRaisesRegex(final.VerificationError, "API row changed"):
            final.check_transitions(before, after)

    def test_api_evidence_change_fails(self):
        before, after = self.states()
        after["rows"][0]["evidence"] = {"path": "other"}
        with self.assertRaisesRegex(final.VerificationError, "API row changed"):
            final.check_transitions(before, after)

    def test_manual_row_still_pending_fails(self):
        before, after = self.states()
        after["rows"][1] = before["rows"][1]
        with self.assertRaisesRegex(final.VerificationError, "not completed"):
            final.check_transitions(before, after)

    def test_row_set_change_fails(self):
        before, after = self.states()
        after["rows"].reverse()
        with self.assertRaisesRegex(final.VerificationError, "different rows"):
            final.check_transitions(before, after)


class ManualEvidenceTests(unittest.TestCase):
    PROMPT, RESPONSE = b"prompt bytes", b"response bytes"

    def fixture(self, tmp):
        root = Path(tmp)
        directory = root / "RUN-1"
        directory.mkdir()
        (directory / "prompt.txt").write_bytes(self.PROMPT)
        (directory / "response.md").write_bytes(self.RESPONSE)
        (directory / "metadata.json").write_text(json.dumps({"raw_response_sha256": sha(self.RESPONSE)}))
        rows = [{"run_id": "RUN-1", "collection_interface": "manual", "expected_prompt_sha256": sha(self.PROMPT)}]
        entries = [{"run_id": "RUN-1", "evidence": {"prompt_sha256": sha(self.PROMPT), "response_sha256": sha(self.RESPONSE)}}]
        return root, rows, entries

    def test_matching_evidence_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, rows, entries = self.fixture(tmp)
            self.assertEqual(final.check_manual_evidence(rows, entries, root), 1)

    def test_changed_response_bytes_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, rows, entries = self.fixture(tmp)
            (root / "RUN-1" / "response.md").write_bytes(b"altered")
            with self.assertRaisesRegex(final.VerificationError, "response bytes"):
                final.check_manual_evidence(rows, entries, root)

    def test_changed_prompt_bytes_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, rows, entries = self.fixture(tmp)
            (root / "RUN-1" / "prompt.txt").write_bytes(b"altered")
            with self.assertRaisesRegex(final.VerificationError, "prompt bytes"):
                final.check_manual_evidence(rows, entries, root)

    def test_unexpected_manual_directory_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, rows, entries = self.fixture(tmp)
            (root / "RUN-EXTRA").mkdir()
            with self.assertRaisesRegex(final.VerificationError, "unexpected"):
                final.check_manual_evidence(rows, entries, root)


class RawInventoryTests(unittest.TestCase):
    def fixture(self, tmp):
        root = Path(tmp)
        raw = root / "data/final/raw"
        (raw / "RUN-1").mkdir(parents=True)
        (raw / ".gitkeep").write_bytes(b"")
        (raw / "RUN-1" / "response.md").write_bytes(b"evidence")
        lines = sorted(f"{sha((root / p).read_bytes())}  {p}" for p in ("data/final/raw/.gitkeep", "data/final/raw/RUN-1/response.md"))
        inventory = root / "inventory.sha256"
        inventory.write_text("\n".join(lines) + "\n")
        return root, raw, inventory

    def check(self, root, raw, inventory):
        return final.check_raw_inventory(inventory, root, raw, expected_sha256=sha(inventory.read_bytes()), expected_files=2)

    def test_matching_inventory_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self.check(*self.fixture(tmp)), 2)

    def test_inventory_sha_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, raw, inventory = self.fixture(tmp)
            with self.assertRaisesRegex(final.VerificationError, "inventory SHA-256"):
                final.check_raw_inventory(inventory, root, raw, expected_sha256="0" * 64, expected_files=2)

    def test_modified_raw_file_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, raw, inventory = self.fixture(tmp)
            (raw / "RUN-1" / "response.md").write_bytes(b"altered")
            with self.assertRaisesRegex(final.VerificationError, "differs from inventory"):
                self.check(root, raw, inventory)

    def test_unlisted_raw_file_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, raw, inventory = self.fixture(tmp)
            (raw / "RUN-2").mkdir()
            (raw / "RUN-2" / "response.md").write_bytes(b"new")
            with self.assertRaisesRegex(final.VerificationError, "unlisted"):
                self.check(root, raw, inventory)

    def test_missing_raw_file_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, raw, inventory = self.fixture(tmp)
            (raw / "RUN-1" / "response.md").unlink()
            with self.assertRaisesRegex(final.VerificationError, "missing"):
                self.check(root, raw, inventory)


class RawDirectoryClassificationTests(unittest.TestCase):
    ROWS = [{"run_id": "API-v2.6-T-01-M1-R01", "collection_interface": "api"},
            {"run_id": "API-v2.6-T-01-M3-R01", "collection_interface": "manual"}]
    M2 = {"data/final/raw/API-v2.6-T-01-M2-R01"}

    def classify(self, *names):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw = root / "data/final/raw"
            for name in names:
                (raw / name).mkdir(parents=True)
            return final.classify_raw_directories(raw, self.ROWS, self.M2, root)

    def test_final_m2_and_historical_directories_are_separated(self):
        classes = self.classify("API-v2.6-T-01-M1-R01", "API-v2.6-T-01-M2-R01", "API-v2.5-T-01-M1-R01", "API-T-01-M1-R01")
        self.assertEqual(classes["final_study_api"], ["API-v2.6-T-01-M1-R01"])
        self.assertEqual(classes["historical_m2"], ["API-v2.6-T-01-M2-R01"])
        self.assertEqual(classes["historical_other_versions"], ["API-T-01-M1-R01", "API-v2.5-T-01-M1-R01"])

    def test_retained_api_row_without_evidence_fails(self):
        with self.assertRaisesRegex(final.VerificationError, "without v2.6 evidence"):
            self.classify("API-v2.6-T-01-M2-R01")

    def test_unlisted_v2_6_directory_fails(self):
        with self.assertRaisesRegex(final.VerificationError, "unexpected raw run directories"):
            self.classify("API-v2.6-T-01-M1-R01", "API-v2.6-T-01-M2-R01", "API-v2.6-T-02-M2-R01")

    def test_v2_7_directory_fails(self):
        with self.assertRaisesRegex(final.VerificationError, "unexpected raw run directories"):
            self.classify("API-v2.6-T-01-M1-R01", "API-v2.6-T-01-M2-R01", "API-v2.7-T-01-M1-R01")

    def test_raw_api_directory_for_manual_row_fails(self):
        with self.assertRaisesRegex(final.VerificationError, "unexpected raw run directories"):
            self.classify("API-v2.6-T-01-M1-R01", "API-v2.6-T-01-M2-R01", "API-v2.6-T-01-M3-R01")

    def test_missing_m2_directory_fails(self):
        with self.assertRaisesRegex(final.VerificationError, "M2 evidence"):
            self.classify("API-v2.6-T-01-M1-R01")


class FrozenHashTests(unittest.TestCase):
    def test_nested_pairs_are_found_and_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_bytes(b"a")
            record = {"x": {"path": "a.txt", "sha256": sha(b"a")}, "y": [{"path": "a.txt", "sha256": sha(b"a")}]}
            self.assertEqual(final.check_frozen_hashes(record, root), 2)
            (root / "a.txt").write_bytes(b"changed")
            with self.assertRaisesRegex(final.VerificationError, "differs"):
                final.check_frozen_hashes(record, root)

    def test_real_freeze_record_has_43_matching_pairs(self):
        record = json.loads(final.FREEZE_RECORD.read_text(encoding="utf-8"))
        self.assertEqual(final.check_frozen_hashes(record, ROOT), 43)


class EligibilityTests(unittest.TestCase):
    ENTRIES = [entry("C", "M1", "api", "completed"), entry("T", "M1", "api", "truncated"),
               entry("F", "M4", "api", "failed"), entry("P", "M3", "manual", "pending", evidence=None),
               entry("MC", "M3", "manual", "completed")]

    def test_truncated_failed_and_pending_are_never_candidates(self):
        candidates = final.primary_candidate_run_ids(self.ENTRIES)
        self.assertEqual(candidates, ["C", "MC"])
        summary = final.eligibility_summary(self.ENTRIES)
        self.assertEqual(summary["excluded_by_frozen_policy"], {"failed": 1, "pending": 1, "truncated": 1})
        self.assertEqual(summary["candidate_rows"], 2)

    def test_frozen_policies_must_exclude_truncated_and_failed(self):
        record = json.loads(final.FREEZE_RECORD.read_text(encoding="utf-8"))
        final.check_policies_exclude(record)
        altered = copy.deepcopy(record)
        altered["truncation_policy"]["exclude_from_primary_shr_phr_denominators"] = False
        with self.assertRaisesRegex(final.VerificationError, "truncation_policy"):
            final.check_policies_exclude(altered)


class CompletionRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.frozen_state, cls.live = real_rows_and_state()
        cls.counts = final.status_counts(cls.live["rows"])
        cls.transitions = final.check_transitions(cls.frozen_state, cls.live)
        cls.record = json.loads(final.COMPLETION_RECORD.read_text(encoding="utf-8"))
        cls.markdown = final.COMPLETION_MARKDOWN.read_text(encoding="utf-8")
        cls.record_sha = final.digest(final.COMPLETION_RECORD)

    def check(self, record, record_sha=None):
        final.check_completion_record(record, self.frozen_state, self.live, self.counts, self.transitions,
                                      self.markdown, record_sha or self.record_sha)

    def test_real_record_agrees_with_evidence(self):
        self.check(self.record)

    def test_changed_row_status_fails(self):
        record = copy.deepcopy(self.record)
        record["rows"][0]["final_observed_status"] = "failed"
        with self.assertRaisesRegex(final.VerificationError, "status differs"):
            self.check(record)

    def test_changed_evidence_hash_fails(self):
        record = copy.deepcopy(self.record)
        record["rows"][-1]["evidence"]["response_sha256"] = "0" * 64
        with self.assertRaisesRegex(final.VerificationError, "evidence hashes differ"):
            self.check(record)

    def test_eligibility_claim_fails(self):
        record = copy.deepcopy(self.record)
        record["primary_analysis_eligibility"]["determined_by_this_record"] = True
        with self.assertRaisesRegex(final.VerificationError, "eligibility"):
            self.check(record)

    def test_markdown_must_state_json_hash(self):
        with self.assertRaisesRegex(final.VerificationError, "SHA-256"):
            self.check(self.record, record_sha="0" * 64)


class IntegrationTests(unittest.TestCase):
    PROTECTED = (final.FROZEN_SCRIPT, frozen.STATE, final.FREEZE_RECORD, final.COMPLETION_RECORD, final.RAW_INVENTORY)

    def test_cli_passes_and_writes_nothing(self):
        before = {path: path.read_bytes() for path in self.PROTECTED}
        status_before = subprocess.run(["git", "status", "--porcelain", "--ignored"], cwd=ROOT, capture_output=True, text=True).stdout
        completed = subprocess.run([sys.executable, str(ROOT / "scripts/verify_final_collection_v2_7.py")],
                                   cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        self.assertIn("FINAL_COMPLETION_CHECK: PASS", completed.stdout)
        self.assertEqual({path: path.read_bytes() for path in self.PROTECTED}, before)
        status_after = subprocess.run(["git", "status", "--porcelain", "--ignored"], cwd=ROOT, capture_output=True, text=True).stdout
        self.assertEqual(status_after, status_before)

    def test_frozen_script_and_state_are_unchanged(self):
        self.assertEqual(final.digest(final.FROZEN_SCRIPT), final.FROZEN_SCRIPT_SHA256)
        record = json.loads(final.FREEZE_RECORD.read_text(encoding="utf-8"))
        self.assertEqual(final.digest(frozen.STATE), record["initial_collection_state"]["sha256"])
        self.assertEqual(json.loads(frozen.STATE.read_text(encoding="utf-8"))["status_counts"],
                         {"completed": 105, "failed": 19, "pending": 130, "truncated": 16})

    def test_frozen_snapshot_check_is_distinct_and_still_fails_on_live_state_only(self):
        # FROZEN_SNAPSHOT_CHECK compares the pre-completion snapshot with a live
        # re-derivation, so it is expected to fail after manual completion.
        completed = subprocess.run([sys.executable, str(final.FROZEN_SCRIPT), "--check"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 1)
        self.assertIn("v2.7 collection state no longer matches preserved evidence", completed.stderr)


if __name__ == "__main__":
    unittest.main()
