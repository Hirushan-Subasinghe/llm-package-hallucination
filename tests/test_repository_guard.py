"""Tests for the hard guard against new data collection in the canonical final worktree.

Context: a collection command was once accidentally run from the former
analysis repository (python3 scripts/collect_api_batch_v2_6.py --exclude-model
M2 --limit 1), creating two non-official run artifacts that have since been
quarantined. This worktree is now the canonical final v2.7 worktree, and final
data collection is complete and frozen, so the guard refuses any new
collection here. See scripts/repository_guard.py and .analysis-repository-marker.

Every collection entry point's CLI main() must call
assert_live_collection_allowed() before it could generate or record a
response, so refusal happens before any network call, provider call, raw-run
directory creation, manual-capture write, or batch-state mutation -- while
leaving analysis-only scripts (verification, manifest/freeze-record creation)
and explicit read-only modes completely unaffected.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import repository_guard

EXPECTED_MESSAGE = (
    "Live data collection is disabled: final v2.7 data collection is complete and frozen. "
    "No new experimental responses may be collected."
)

# Every entry point whose CLI can drive a real provider request or state
# mutation, all funneling through the same repository_guard sentinel check.
API_LIVE_COLLECTION_SCRIPTS = [
    "collect_api_run.py",
    "collect_api_batch.py",
    "collect_api_batch_v2_4.py",
    "collect_api_batch_v2_5.py",
    "collect_api_batch_v2_6.py",
    "preflight_api_models.py",
    "run_api_smoke_tests.py",
    "run_api_interface_suitability.py",
]

# Scripts that only read/verify already-collected data or generate local
# planning artifacts (manifests, freeze records). None of these may reference
# the guard: they must keep working unmodified inside this repository.
#
# init_collection_run.py is NOT in this list: although it makes no network or
# provider call, its main() can create a raw-run directory and metadata.json
# in this repository, so it also carries the guard (see
# InitCollectionRunGuardTests below). finalize_collection_run.py is a
# separate, later step (writes into an already-initialized directory) and is
# out of scope for this change.
ANALYSIS_ONLY_SCRIPTS = [
    "verify_collection.py",
    "verify_prompt_hash.py",
    "verify_api_smoke.py",
    "verify_api_interface_suitability.py",
    "create_api_manifest.py",
    "create_experiment_freeze.py",
    "create_experiment_freeze_v2_6.py",
    "collection_common.py",
    "finalize_collection_run.py",
    "render_api_prompts.py",
    "verify_final_collection_v2_7.py",
]

ANALYSIS_ONLY_SCRIPTS_WITH_HELP = [
    "verify_collection.py",
    "verify_prompt_hash.py",
    "create_api_manifest.py",
    "create_experiment_freeze.py",
    "create_experiment_freeze_v2_6.py",
    "finalize_collection_run.py",
]


def run_script(name: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / name), *args],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )


class MarkerAndGuardUnitTests(unittest.TestCase):
    """Pure unit tests of the sentinel check itself, independent of any script."""

    def test_marker_file_exists_at_repository_root(self):
        self.assertTrue(repository_guard.ANALYSIS_REPOSITORY_MARKER.is_file())
        self.assertEqual(repository_guard.ANALYSIS_REPOSITORY_MARKER.parent, repository_guard.ROOT)

    def test_marker_path_is_derived_from_this_files_location_not_cwd(self):
        # Robustness requirement: identity must not depend on the process's
        # current working directory or on a hard-coded path string.
        with tempfile.TemporaryDirectory() as elsewhere:
            import os

            original = os.getcwd()
            try:
                os.chdir(elsewhere)
                self.assertTrue(repository_guard.ANALYSIS_REPOSITORY_MARKER.is_file())
            finally:
                os.chdir(original)

    def test_assert_raises_live_collection_disabled_with_exact_message(self):
        with self.assertRaises(repository_guard.LiveCollectionDisabled) as ctx:
            repository_guard.assert_live_collection_allowed()
        self.assertEqual(str(ctx.exception), EXPECTED_MESSAGE)

    def test_refusal_is_a_value_error_for_uniform_cli_error_handling(self):
        # Every entry point's main() catches (OSError, ValueError, ...); the
        # guard's exception must be caught by that same handler.
        self.assertTrue(issubclass(repository_guard.LiveCollectionDisabled, ValueError))

    def test_no_refusal_when_marker_is_absent(self):
        with patch.object(
            repository_guard,
            "ANALYSIS_REPOSITORY_MARKER",
            Path(tempfile.gettempdir()) / "no-such-analysis-repository-marker",
        ):
            repository_guard.assert_live_collection_allowed()  # must not raise


class CLIRefusalTests(unittest.TestCase):
    """Reproduce the accident and its sibling entry points as real subprocesses."""

    def test_v2_6_accident_command_is_refused(self):
        completed = run_script("collect_api_batch_v2_6.py", "--exclude-model", "M2", "--limit", "1")
        self.assertEqual(completed.returncode, 1)
        self.assertIn(EXPECTED_MESSAGE, completed.stderr)

    def test_every_api_live_collection_entry_point_refuses(self):
        # Minimal arguments satisfying each script's own required-flag parsing,
        # so execution reaches the guard rather than an unrelated argparse
        # usage error. None of these paths exist; if the guard did not fire
        # first, the script would fail later for a different reason (missing
        # manifest/output path), not with the collection-safety message.
        required_arguments = {
            "collect_api_run.py": ["--manifest", "irrelevant.csv", "--run-id", "irrelevant"],
            "preflight_api_models.py": ["--output", str(Path(tempfile.gettempdir()) / "unused_preflight.json")],
        }
        for name in API_LIVE_COLLECTION_SCRIPTS:
            with self.subTest(script=name):
                completed = run_script(name, *required_arguments.get(name, []))
                self.assertEqual(completed.returncode, 1, msg=completed.stderr)
                self.assertIn(EXPECTED_MESSAGE, completed.stderr)

    def test_codex_collection_entry_point_refuses(self):
        with tempfile.TemporaryDirectory() as codex_home:
            completed = run_script("collect_codex_runs.py", "--codex-home", codex_home)
        self.assertEqual(completed.returncode, 1)
        self.assertIn(EXPECTED_MESSAGE, completed.stderr)

    def test_hybrid_api_batch_refuses_collection_but_allows_read_only_modes(self):
        with tempfile.TemporaryDirectory() as tmp:
            state, raw = Path(tmp) / "state.json", Path(tmp) / "raw"
            paths = ["--state", str(state), "--raw-root", str(raw)]
            refused = run_script("collect_hybrid_api_batch.py", "--limit", "1", *paths)
            self.assertEqual(refused.returncode, 1)
            self.assertIn(EXPECTED_MESSAGE, refused.stderr)
            for mode in ("--list", "--dry-run"):
                with self.subTest(mode=mode):
                    allowed = run_script("collect_hybrid_api_batch.py", mode, *paths)
                    self.assertEqual(allowed.returncode, 0, msg=allowed.stderr)
                    self.assertNotIn(EXPECTED_MESSAGE, allowed.stdout + allowed.stderr)
            self.assertFalse(state.exists())
            self.assertFalse(raw.exists())

    def test_hybrid_manual_refuses_writes_but_allows_read_only_modes(self):
        with tempfile.TemporaryDirectory() as tmp:
            manual_root = Path(tmp) / "manual"
            root = ["--manual-root", str(manual_root)]
            for args in (["--prepare"], ["--capture-stdin", "--run-id", "API-v2.6-DOC-BINARY-01-M1-R02"]):
                with self.subTest(args=args):
                    refused = run_script("collect_hybrid_manual.py", *args, *root)
                    self.assertEqual(refused.returncode, 1)
                    self.assertIn(EXPECTED_MESSAGE, refused.stderr)
            for args in (["--list"], ["--show-next"], ["--prepare", "--dry-run"]):
                with self.subTest(args=args):
                    allowed = run_script("collect_hybrid_manual.py", *args, *root)
                    self.assertEqual(allowed.returncode, 0, msg=allowed.stderr)
            self.assertFalse(manual_root.exists())

    def test_argparse_still_wins_over_the_guard_for_malformed_cli_input(self):
        # Invalid CLI syntax must still produce argparse's own usage error
        # (exit 2) rather than being masked by the collection-safety refusal;
        # the guard only needs to run before any *side effect*, and argparse
        # parsing itself has none.
        completed = run_script("collect_api_batch_v2_6.py", "--exclude-model", "M9", "--dry-run")
        self.assertEqual(completed.returncode, 2)
        self.assertIn("invalid choice", completed.stderr)
        self.assertNotIn(EXPECTED_MESSAGE, completed.stderr)


class InitCollectionRunGuardTests(unittest.TestCase):
    """init_collection_run.py makes no network/provider call, but its main()
    can create a raw-run directory and write metadata.json in this
    repository, which is also prohibited here. See scripts/init_collection_run.py.
    """

    PILOT_RUN_ID = "PILOT-AUTH-04-chatgpt_web-R01"

    def target_directory(self) -> Path:
        # Mirrors collection_common.RAW_ROOTS["pilot"] / run_id for this manifest row.
        return ROOT / "data" / "pilot" / "raw" / self.PILOT_RUN_ID

    def test_refuses_in_the_analysis_repository(self):
        completed = run_script("init_collection_run.py", self.PILOT_RUN_ID)
        self.assertEqual(completed.returncode, 1)
        self.assertIn(EXPECTED_MESSAGE, completed.stderr)

    def test_creates_no_raw_run_directory(self):
        target = self.target_directory()
        self.assertFalse(target.exists(), "precondition: target run directory must not already exist")
        completed = run_script("init_collection_run.py", self.PILOT_RUN_ID)
        self.assertEqual(completed.returncode, 1)
        self.assertFalse(target.exists(), "no raw-run directory may be created by a refused invocation")

    def test_leaves_pilot_manifest_collection_state_unmodified(self):
        manifest_path = ROOT / "manifests" / "pilot_manifest.csv"
        before = manifest_path.read_bytes()
        run_script("init_collection_run.py", self.PILOT_RUN_ID)
        self.assertEqual(manifest_path.read_bytes(), before)

    def test_refuses_before_any_manifest_lookup_or_metadata_write(self):
        # find_run() is the first thing initialize_run() does; patching it to
        # explode proves the guard fires strictly before that call (and
        # therefore before run_directory(), mkdir(), and write_metadata(),
        # all of which happen later in the same function).
        import init_collection_run

        argv = ["init_collection_run.py", self.PILOT_RUN_ID]
        with patch.object(sys, "argv", argv), patch.object(
            init_collection_run, "find_run", side_effect=AssertionError("no manifest lookup may occur in this test")
        ):
            exit_code = init_collection_run.main()
        self.assertEqual(exit_code, 1)

    def test_help_still_exits_zero_before_the_guard(self):
        # argparse's own --help handling has no side effects, so it is
        # allowed to take precedence, consistent with the other entry points.
        completed = run_script("init_collection_run.py", "--help")
        self.assertEqual(completed.returncode, 0)
        self.assertNotIn(EXPECTED_MESSAGE, completed.stdout + completed.stderr)

    def test_missing_required_argument_still_exits_two(self):
        # Existing argparse usage-error behavior (missing positional run_id)
        # is unchanged: it still wins over the collection-safety refusal.
        completed = run_script("init_collection_run.py")
        self.assertEqual(completed.returncode, 2)
        self.assertIn("required", completed.stderr)
        self.assertNotIn(EXPECTED_MESSAGE, completed.stderr)


class RefusalPrecedesSideEffectsTests(unittest.TestCase):
    """In-process main() calls with the real transport patched to explode.

    If the guard did not fire first, these transports would raise
    AssertionError, which is not caught by any entry point's except clause,
    so the test itself would error instead of observing a clean exit code 1.
    This is a direct proof that refusal happens strictly before any network
    or provider call, not merely before a successful one.
    """

    def setUp(self):
        for name in (
            "collect_api_run",
            "collect_api_batch",
            "collect_api_batch_v2_4",
            "collect_api_batch_v2_5",
            "collect_api_batch_v2_6",
            "preflight_api_models",
            "run_api_smoke_tests",
            "run_api_interface_suitability",
            "collect_codex_runs",
        ):
            sys.modules.pop(name, None)

    def test_collect_api_run_refuses_before_requests_post(self):
        import collect_api_run

        argv = ["collect_api_run.py", "--manifest", "irrelevant.csv", "--run-id", "irrelevant"]
        with patch.object(sys, "argv", argv), patch(
            "requests.post", side_effect=AssertionError("no live API request may occur in this test")
        ):
            exit_code = collect_api_run.main()
        self.assertEqual(exit_code, 1)

    def test_v2_6_batch_refuses_before_state_mutation_and_raw_directory_creation(self):
        import collect_api_batch_v2_6 as v2_6

        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "state.json"
            raw_root = Path(tmp) / "raw"
            argv = [
                "collect_api_batch_v2_6.py",
                "--manifest", str(ROOT / "manifests/api_final_v2.6.0_manifest.csv"),
                "--config", str(ROOT / "config/api_model_set_1.4.0.json"),
                "--state", str(state_path),
                "--raw-root", str(raw_root),
                "--limit", "1",
                "--exclude-model", "M2",
            ]
            with patch.object(sys, "argv", argv), patch(
                "requests.post", side_effect=AssertionError("no live API request may occur in this test")
            ):
                exit_code = v2_6.main()
            self.assertEqual(exit_code, 1)
            self.assertFalse(state_path.exists(), "batch-state file must not be created before refusal")
            self.assertFalse(raw_root.exists(), "raw-run directory root must not be created before refusal")

    def test_preflight_refuses_before_urlopen(self):
        import preflight_api_models

        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "preflight.json"
            argv = ["preflight_api_models.py", "--output", str(output_path)]
            with patch.object(sys, "argv", argv), patch(
                "urllib.request.urlopen", side_effect=AssertionError("no live provider call may occur in this test")
            ):
                exit_code = preflight_api_models.main()
            self.assertEqual(exit_code, 1)
            self.assertFalse(output_path.exists(), "preflight snapshot must not be written before refusal")

    def test_codex_collection_refuses_before_subprocess_run(self):
        import collect_codex_runs

        with tempfile.TemporaryDirectory() as codex_home:
            argv = ["collect_codex_runs.py", "--codex-home", codex_home]
            with patch.object(sys, "argv", argv), patch(
                "subprocess.run", side_effect=AssertionError("no codex process may be launched in this test")
            ):
                exit_code = collect_codex_runs.main()
        self.assertEqual(exit_code, 1)


class AnalysisOnlyScriptsUnaffectedTests(unittest.TestCase):
    """The safety mechanism must not change behavior for non-collection scripts."""

    def test_analysis_only_scripts_do_not_reference_the_guard(self):
        for name in ANALYSIS_ONLY_SCRIPTS:
            with self.subTest(script=name):
                source = (ROOT / "scripts" / name).read_text(encoding="utf-8")
                self.assertNotIn("repository_guard", source)
                self.assertNotIn("assert_live_collection_allowed", source)

    def test_analysis_only_scripts_still_start_normally(self):
        for name in ANALYSIS_ONLY_SCRIPTS_WITH_HELP:
            with self.subTest(script=name):
                completed = run_script(name, "--help")
                self.assertEqual(completed.returncode, 0, msg=completed.stderr)
                self.assertNotIn("Live data collection is disabled", completed.stdout + completed.stderr)

    def test_pure_helpers_importable_from_collect_api_run_without_triggering_guard(self):
        # create_api_manifest.py, create_experiment_freeze*.py, verify_api_smoke.py,
        # and verify_api_interface_suitability.py all import plain helpers/constants
        # from collect_api_run without ever calling its main(); using them must
        # not raise LiveCollectionDisabled.
        import collect_api_run

        config = collect_api_run.load_config(collect_api_run.DEFAULT_CONFIG)
        self.assertIn("model_set_version", config)
        self.assertEqual(collect_api_run.sha256_bytes(b"x"), collect_api_run.sha256_bytes(b"x"))
        collect_api_run.utc_now()


class RepositoryStateUnchangedTests(unittest.TestCase):
    """Proof that exercising the guard leaves frozen experiment state and evidence untouched."""

    STATE_PATH = ROOT / "data/final/api_batch_state_v2.6.0.json"
    QUARANTINE_DIR = ROOT / "data/quarantine/accidental_v2.6_collection_2026-09-22"

    def test_v2_6_batch_state_file_is_byte_identical_to_head(self):
        head_bytes = subprocess.run(
            ["git", "show", "HEAD:data/final/api_batch_state_v2.6.0.json"],
            capture_output=True, cwd=str(ROOT), check=True,
        ).stdout
        self.assertEqual(self.STATE_PATH.read_bytes(), head_bytes)

    # Replaces test_raw_final_contains_no_active_v2_6_run_directories, which
    # asserted that data/final/raw/API-v2.6-* was empty. That held in the former
    # analysis repository, where no raw v2.6 evidence was meant to exist, but it
    # became invalid once D043 evidence was copied into this canonical worktree:
    # the 140 retained v2.7 API observations keep their API-v2.6-* run IDs, and
    # the 11 M2 directories are preserved as historical evidence. Raw evidence is
    # never deleted or renamed to satisfy a test. See
    # docs/final_v2.7_canonical_worktree_validation.md.
    def test_raw_final_directories_are_exactly_final_or_historical_evidence(self):
        import create_experiment_freeze_v2_7 as frozen
        import verify_final_collection_v2_7 as final

        rows = frozen.final_study_rows()
        record = json.loads(final.FREEZE_RECORD.read_text(encoding="utf-8"))
        m2_paths = {item["path"] for item in record["m2_exclusion"]["preserved_evidence"]}
        classes = final.classify_raw_directories(ROOT / "data/final/raw", rows, m2_paths, ROOT)
        api_rows = {row["run_id"] for row in rows if row["collection_interface"] == "api"}
        manifest_ids = {row["run_id"] for row in rows}

        # Every retained v2.7 API row has its historical v2.6 evidence directory.
        self.assertEqual(set(classes["final_study_api"]), api_rows)
        self.assertEqual(len(classes["final_study_api"]), 140)
        # M2 directories are historical only and never in the v2.7 manifest.
        self.assertEqual(len(classes["historical_m2"]), 11)
        self.assertTrue(manifest_ids.isdisjoint(classes["historical_m2"]))
        self.assertTrue(all("-M2-" in name for name in classes["historical_m2"]))
        # No other raw run ID is treated as a final-study observation.
        self.assertTrue(manifest_ids.isdisjoint(classes["historical_other_versions"]))
        self.assertFalse(any(name.startswith(("API-v2.6-", "API-v2.7-")) for name in classes["historical_other_versions"]))
        self.assertEqual(list((ROOT / "data/final/raw").glob("API-v2.7-*")), [])

    def test_evidence_preservation_does_not_imply_analytical_eligibility(self):
        import create_experiment_freeze_v2_7 as frozen
        import verify_final_collection_v2_7 as final

        rows = frozen.final_study_rows()
        state = json.loads(frozen.STATE.read_text(encoding="utf-8"))
        entries = frozen.derive_collection_state(rows, state["derived_at_utc"])["rows"]
        candidates = set(final.primary_candidate_run_ids(entries))
        not_candidates = {entry["run_id"] for entry in entries if entry["status"] in {"truncated", "failed"}}
        self.assertEqual(len(not_candidates), 35)
        self.assertTrue(candidates.isdisjoint(not_candidates))
        # Preserved M2 evidence exists on disk but is never a candidate.
        self.assertFalse(any("-M2-" in run_id for run_id in candidates))

    def test_quarantine_evidence_is_untouched(self):
        self.assertTrue(self.QUARANTINE_DIR.is_dir())
        completed = subprocess.run(
            ["git", "status", "--porcelain", str(self.QUARANTINE_DIR)],
            capture_output=True, text=True, cwd=str(ROOT), check=True,
        )
        # The quarantine directory is untracked (preserved evidence, not
        # committed history); this only asserts nothing here is staged for
        # deletion or modification by git, i.e. it still matches what is on disk.
        for line in completed.stdout.splitlines():
            self.assertFalse(line.startswith(" D") or line.startswith("D "), line)


if __name__ == "__main__":
    unittest.main()
