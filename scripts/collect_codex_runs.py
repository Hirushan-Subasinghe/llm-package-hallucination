#!/usr/bin/env python3
"""Collect frozen pilot prompts through isolated, non-interactive Codex CLI runs."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from collection_common import (
    ROOT,
    read_manifest,
    raw_artifact_relative_path,
    sha256_bytes,
    utc_now,
    verified_prompt_bytes,
    write_bytes_exclusive,
    write_metadata,
)
from finalize_collection_run import finalize_run
from init_collection_run import initialize_run
from repository_guard import assert_live_collection_allowed


EXPECTED_CODEX_VERSION = "codex-cli 0.154.0"
MODEL = "gpt-5.6-sol"
DISABLED_FEATURES = (
    "apps",
    "hooks",
    "plugins",
    "remote_plugin",
    "multi_agent",
    "memories",
    "goals",
    "shell_tool",
    "skill_mcp_dependency_install",
    "browser_use",
    "browser_use_external",
    "computer_use",
)
FORBIDDEN_CODEX_HOME_ENTRIES = (
    "config.toml",
    "AGENTS.md",
    "hooks.json",
    "skills",
    "plugins",
    "memories_1.sqlite",
    "history.jsonl",
    "sessions",
)


def _outside_repository(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT.resolve())
        return False
    except ValueError:
        return True


def validate_codex_home(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    if not resolved.is_dir():
        raise ValueError(f"Dedicated CODEX_HOME does not exist: {resolved}")
    if not _outside_repository(resolved):
        raise ValueError("Dedicated CODEX_HOME must be outside the research repository")
    if not (resolved / "auth.json").is_file():
        raise ValueError("Dedicated CODEX_HOME must contain auth.json")
    contaminated = [name for name in FORBIDDEN_CODEX_HOME_ENTRIES if (resolved / name).exists()]
    if contaminated:
        raise ValueError(f"Dedicated CODEX_HOME is not clean: {', '.join(contaminated)}")
    return resolved


def preflight_codex(codex_binary: str, codex_home: Path, *, run=subprocess.run) -> None:
    environment = os.environ.copy()
    environment["CODEX_HOME"] = str(codex_home)
    version = run(
        [codex_binary, "--version"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=environment,
        shell=False,
        check=False,
    )
    version_text = version.stdout.decode("utf-8", errors="replace").strip()
    if version.returncode != 0 or version_text != EXPECTED_CODEX_VERSION:
        raise ValueError(f"Expected {EXPECTED_CODEX_VERSION}, observed {version_text or 'unavailable'}")

    arguments = [codex_binary]
    for feature in DISABLED_FEATURES:
        arguments.extend(("--disable", feature))
    arguments.extend(("features", "list"))
    features = run(
        arguments,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=environment,
        shell=False,
        check=False,
    )
    output = features.stdout.decode("utf-8", errors="replace")
    if features.returncode != 0:
        raise ValueError("Codex feature preflight failed")
    for feature in DISABLED_FEATURES:
        matching = [line.split() for line in output.splitlines() if line.split()[:1] == [feature]]
        if len(matching) != 1 or matching[0][-1] != "false":
            raise ValueError(f"Codex feature disable was not effective: {feature}")


def build_codex_arguments(codex_binary: str, workspace: Path, staged_response: Path) -> list[str]:
    arguments = [
        codex_binary,
        "exec",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--strict-config",
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
        "--cd",
        str(workspace),
        "--model",
        MODEL,
        "--config",
        'model_provider="openai"',
        "--config",
        'model_reasoning_effort="medium"',
        "--config",
        'service_tier="default"',
        "--config",
        'web_search="disabled"',
    ]
    for feature in DISABLED_FEATURES:
        arguments.extend(("--disable", feature))
    arguments.extend(("--json", "--output-last-message", str(staged_response), "-"))
    return arguments


def _failure_directory(directory: Path) -> Path:
    path = directory / "failed_attempts" / "attempt-01"
    if path.exists():
        raise ValueError("Failed attempt evidence already exists; automatic retry is prohibited")
    path.mkdir(parents=True)
    return path


def _preserve_failure(
    directory: Path,
    metadata: dict,
    response: bytes | None,
    transcript: bytes,
    stderr: bytes,
    reason: str,
) -> None:
    failure = _failure_directory(directory)
    captures = {}
    if response is not None:
        path = failure / "response.partial.md"
        write_bytes_exclusive(path, response)
        captures["response"] = {"path": str(path.relative_to(directory)), "sha256": sha256_bytes(response)}
    for name, content in (("transcript.txt", transcript), ("stderr.txt", stderr)):
        path = failure / name
        write_bytes_exclusive(path, content)
        captures[name.removesuffix(".txt")] = {
            "path": str(path.relative_to(directory)),
            "sha256": sha256_bytes(content),
        }
    metadata["collection_status"] = "failed"
    metadata["failure_reason"] = reason
    metadata["failed_capture"] = captures
    write_metadata(directory / "metadata.json", metadata)


def collect_codex_row(
    row: dict[str, str],
    manifest_path: Path,
    codex_home: Path,
    *,
    codex_binary: str = "codex",
    timeout_seconds: int | None = None,
    temporary_root: Path | None = None,
    run=subprocess.run,
) -> bool:
    if row.get("phase") != "pilot" or row.get("workflow") != "codex_cli":
        raise ValueError("Automated Codex collection currently accepts pilot codex_cli rows only")
    manifest_before = manifest_path.read_bytes()
    prompt_source_bytes = verified_prompt_bytes(row)
    _, _, directory, metadata = initialize_run(row["run_id"], allow_pristine_existing=True)
    if metadata.get("collection_status") == "completed":
        raise ValueError("Refusing to overwrite a completed run")

    prompt_copy = (directory / "prompt.txt").read_bytes()
    if prompt_copy != prompt_source_bytes:
        raise ValueError("Initialized prompt copy differs from the frozen rendered prompt")
    metadata.update({
        "tool_name": "codex_cli",
        "provider": "OpenAI",
        "model_name": MODEL,
        "model_version": "not_exposed",
        "workflow_type": "agentic_cli",
        "model_reasoning_effort": "medium",
        "service_tier": "default",
        "temperature": "not_exposed",
        "seed": "not_exposed",
        "max_output_tokens": None,
        "web_search": "disabled",
        "sandbox_mode": "read-only",
        "session_ephemeral": True,
        "user_config_ignored": True,
        "rules_ignored": True,
        "skip_git_repo_check": True,
        "disabled_features": list(DISABLED_FEATURES),
        "codex_cli_version": "0.154.0",
        "collection_method": "automated_codex_exec",
        "manifest_path": str(manifest_path.relative_to(ROOT)),
        "manifest_sha256": sha256_bytes(manifest_before),
        "generation_started_at_utc": utc_now(),
        "generation_ended_at_utc": "",
        "attempt_number": 1,
        "collection_status": "running",
        "notes": "Automated pilot Codex collection; no automatic retry.",
    })
    write_metadata(directory / "metadata.json", metadata)

    with tempfile.TemporaryDirectory(prefix=f"codex-collection-{row['run_id']}-", dir=temporary_root) as temporary:
        temporary_path = Path(temporary).resolve()
        if not _outside_repository(temporary_path):
            raise ValueError("Temporary collection directory must be outside the repository")
        workspace = temporary_path / "workspace"
        staging = temporary_path / "staging"
        workspace.mkdir()
        staging.mkdir()
        staged_response = staging / "response.md"
        arguments = build_codex_arguments(codex_binary, workspace, staged_response)
        metadata["invocation_argv"] = arguments
        metadata["workspace_isolation"] = "fresh_external_temporary_directory"
        metadata["codex_home_isolation"] = "dedicated_clean_external"
        write_metadata(directory / "metadata.json", metadata)

        environment = os.environ.copy()
        environment["CODEX_HOME"] = str(codex_home)
        started = time.monotonic()
        timed_out = False
        returncode = None
        try:
            result = run(
                arguments,
                input=prompt_copy,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=workspace,
                env=environment,
                timeout=timeout_seconds,
                shell=False,
                check=False,
            )
            transcript = result.stdout or b""
            stderr = result.stderr or b""
            returncode = result.returncode
        except subprocess.TimeoutExpired as error:
            timed_out = True
            transcript = error.stdout or b""
            stderr = error.stderr or b""
        except OSError as error:
            transcript = b""
            stderr = str(error).encode("utf-8", errors="replace")
        duration_ms = round((time.monotonic() - started) * 1000)

        response = staged_response.read_bytes() if staged_response.is_file() else None
        metadata.update({
            "generation_ended_at_utc": utc_now(),
            "duration_ms": duration_ms,
            "cli_exit_status": returncode,
            "timed_out": timed_out,
        })
        if manifest_path.read_bytes() != manifest_before:
            _preserve_failure(directory, metadata, response, transcript, stderr, "Manifest changed during generation")
            return False
        if timed_out:
            _preserve_failure(directory, metadata, response, transcript, stderr, "Codex process timed out")
            return False
        if returncode != 0:
            _preserve_failure(directory, metadata, response, transcript, stderr, f"Codex exited with status {returncode}")
            return False
        if response is None or not response:
            _preserve_failure(directory, metadata, response, transcript, stderr, "Codex final response is missing or empty")
            return False

        staged_transcript = staging / "transcript.txt"
        staged_stderr = staging / "stderr.txt"
        staged_transcript.write_bytes(transcript)
        staged_stderr.write_bytes(stderr)
        destinations = {
            "response.md": response,
            "transcript.txt": transcript,
            "stderr.txt": stderr,
        }
        for name, content in destinations.items():
            write_bytes_exclusive(directory / name, content)
        metadata.update({
            "raw_response_path": raw_artifact_relative_path(row, "response.md"),
            "raw_response_sha256": sha256_bytes(response),
            "raw_response_size_bytes": len(response),
            "transcript_path": "transcript.txt",
            "transcript_sha256": sha256_bytes(transcript),
            "transcript_size_bytes": len(transcript),
            "stderr_path": "stderr.txt",
            "stderr_sha256": sha256_bytes(stderr),
            "stderr_size_bytes": len(stderr),
            "collection_status": "captured",
        })
        write_metadata(directory / "metadata.json", metadata)
        finalize_run(row["run_id"])
        return True


def select_rows(phase: str, run_id: str | None, limit: int | None):
    if phase != "pilot":
        raise ValueError("Baseline Codex automation is locked until pilot approval and a deliberate code change")
    rows, manifest_path = read_manifest(phase)
    selected = [row for row in rows if row["workflow"] == "codex_cli"]
    if run_id is not None:
        selected = [row for row in selected if row["run_id"] == run_id]
        if not selected:
            raise ValueError(f"Run ID is not a pilot Codex row: {run_id}")
    if limit is not None:
        if limit < 1:
            raise ValueError("--limit must be a positive integer")
        selected = selected[:limit]
    return selected, manifest_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("pilot", "final"), default="pilot")
    parser.add_argument("--run-id")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--codex-home", type=Path, required=True)
    parser.add_argument("--codex-binary", default="codex")
    parser.add_argument("--timeout-seconds", type=int)
    args = parser.parse_args()
    try:
        assert_live_collection_allowed()
        codex_home = validate_codex_home(args.codex_home)
        rows, manifest_path = select_rows(args.phase, args.run_id, args.limit)
        preflight_codex(args.codex_binary, codex_home)
        validate_codex_home(codex_home)
        failures = 0
        for row in rows:
            print(f"Collecting {row['run_id']}")
            if not collect_codex_row(
                row,
                manifest_path,
                codex_home,
                codex_binary=args.codex_binary,
                timeout_seconds=args.timeout_seconds,
            ):
                failures += 1
                print(f"FAILED: {row['run_id']}; evidence preserved; no retry attempted", file=sys.stderr)
        return 1 if failures else 0
    except (OSError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
