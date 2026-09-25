"""Tests for the hard guard against live data collection in this analysis repository.

Context: a collection command was once accidentally run from this repository
(python3 scripts/collect_api_batch_v2_6.py --exclude-model M2 --limit 1),
creating two non-official run artifacts that have since been quarantined. See
scripts/repository_guard.py and .analysis-repository-marker.

Every live-collection entry point's CLI main() must call
assert_live_collection_allowed() before doing anything else, so refusal
happens before any network call, provider call, raw-run directory creation,
or batch-state mutation -- while leaving analysis-only scripts (verification,
manifest/freeze-record creation) completely unaffected.
"""

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
    "Live data collection is disabled in the analysis repository. "
    "Use ~/Dev/ai-hallucination-study."
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
    """Proof that exercising the guard leaves frozen experiment state untouched."""

    STATE_PATH = ROOT / "data/final/api_batch_state_v2.6.0.json"
    QUARANTINE_DIR = ROOT / "data/quarantine/accidental_v2.6_collection_2026-09-22"

    def test_v2_6_batch_state_file_is_byte_identical_to_head(self):
        head_bytes = subprocess.run(
            ["git", "show", "HEAD:data/final/api_batch_state_v2.6.0.json"],
            capture_output=True, cwd=str(ROOT), check=True,
        ).stdout
        self.assertEqual(self.STATE_PATH.read_bytes(), head_bytes)

    def test_raw_final_contains_no_active_v2_6_run_directories(self):
        raw_root = ROOT / "data/final/raw"
        matches = list(raw_root.glob("API-v2.6-*"))
        self.assertEqual(matches, [], f"unexpected active v2.6 run directories: {matches}")

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
