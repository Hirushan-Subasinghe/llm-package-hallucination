#!/usr/bin/env python3
"""Verify the completed v2.7 final-study collection (FINAL_COMPLETION_CHECK); read-only.

This is a separate, non-frozen companion to the frozen
``scripts/create_experiment_freeze_v2_7.py``.  That script's ``--check``
(FROZEN_SNAPSHOT_CHECK) compares the frozen initial collection state with a live
re-derivation.  The frozen state recorded the 130 manual rows as ``pending``, so
the check cannot pass once the manual evidence is present.  Neither the frozen
script nor the frozen state is edited.  Instead, this verifier:

* reuses the frozen script's pure, read-only helpers unchanged (manifest filter,
  model-set rules, evidence derivation);
* confirms that the frozen snapshot and every frozen hash are unchanged;
* confirms that the only transitions since the freeze are manual
  ``pending`` -> ``completed`` rows;
* verifies the D043 raw-evidence inventory and the manual evidence hashes;
* confirms that the derived record ``reports/final_collection_completion_v2.7.0.json``
  agrees with the evidence.

It writes nothing and never calls a model, provider, or registry.  Collection
status is not analysis eligibility: truncated and failed API rows are reported
as excluded from primary denominators under the frozen truncation and failure
policies, and completed rows are only candidates, subject to downstream rules
such as D035.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import create_experiment_freeze_v2_7 as frozen  # noqa: E402  (frozen module; imported read-only)

ROOT = frozen.ROOT
FREEZE_RECORD = frozen.OUTPUT_JSON
FREEZE_MARKDOWN = frozen.OUTPUT_MARKDOWN
FROZEN_SCRIPT = ROOT / "scripts/create_experiment_freeze_v2_7.py"
COMPLETION_RECORD = ROOT / "reports/final_collection_completion_v2.7.0.json"
COMPLETION_MARKDOWN = ROOT / "reports/final_collection_completion_v2.7.0.md"
RAW_INVENTORY = ROOT / "reports/final_v2.7_raw_evidence_inventory.sha256"

FREEZE_TAG = "v2.7.0-freeze"
FREEZE_COMMIT = "bba890d9aa5838f06bee4b1bd0e85d9e61b444f8"
RAW_INVENTORY_SHA256 = "1f79cdecbd573b57f5121dc04fcd5e3aadcca8d46d005cebf4628a8fa75634e7"
RAW_INVENTORY_FILES = 1552
FREEZE_RECORD_SHA256 = "f6fbb15192dee3d5744bc15890c0df81615e3c70ea76a41d9dbfbe7cb27bcfc5"
FROZEN_SCRIPT_SHA256 = "6318922ac50309d378064fe2ba10765ea20faaafa1f750954dfb2120d72c370c"

RETAINED = ("M1", "M3", "M4")
EXPECTED_ROWS = 270
EXPECTED_ROWS_PER_MODEL = 90
EXPECTED_INTERFACE = {"api": 140, "manual": 130}
EXPECTED_API_STATUS = {"completed": 105, "truncated": 16, "failed": 19, "pending": 0}
EXPECTED_MANUAL_COMPLETED = {"M1": 50, "M3": 49, "M4": 31}
EXPECTED_M2_HISTORICAL_DIRECTORIES = 11
# Collection statuses that the frozen v2.7 truncation/failure policies exclude
# from primary SHR/PHR denominators.  ``pending`` has no observation at all.
PRIMARY_EXCLUDED_STATUSES = frozenset({"truncated", "failed", "pending"})


class VerificationError(ValueError):
    """A final-completion invariant does not hold."""


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


# 1-5: design -----------------------------------------------------------------

def check_design(rows: list[dict[str, str]], model_set: dict) -> dict:
    """270 rows, exactly M1/M3/M4 with 90 each, zero M2, 140 API / 130 manual."""
    frozen.validate_manifest_rows(rows)  # frozen rule set; raises ValueError
    require(len(rows) == EXPECTED_ROWS, f"manifest has {len(rows)} rows, expected {EXPECTED_ROWS}")
    models = Counter(row["model_condition_id"] for row in rows)
    require(tuple(sorted(models)) == RETAINED, f"retained models are {sorted(models)}, expected {list(RETAINED)}")
    require(all(count == EXPECTED_ROWS_PER_MODEL for count in models.values()), f"rows per model differ: {dict(models)}")
    require(models.get(frozen.EXCLUDED, 0) == 0, "M2 rows present in the final-study manifest")
    require([model["condition_id"] for model in model_set.get("models", [])] == list(RETAINED),
            "model set conditions are not exactly M1, M3, M4")
    interface = Counter(row["collection_interface"] for row in rows)
    require(dict(interface) == EXPECTED_INTERFACE, f"interface assignment is {dict(interface)}, expected {EXPECTED_INTERFACE}")
    return {"rows": len(rows), "rows_per_model": dict(sorted(models.items())), "m2_rows": 0,
            "interface": dict(sorted(interface.items()))}


# 6-7: final statuses -----------------------------------------------------------

def status_counts(entries: list[dict]) -> dict:
    api = Counter(entry["status"] for entry in entries if entry["collection_interface"] == "api")
    manual = Counter(entry["status"] for entry in entries if entry["collection_interface"] == "manual")
    manual_completed = Counter(entry["model_condition_id"] for entry in entries
                               if entry["collection_interface"] == "manual" and entry["status"] == "completed")
    return {"api": {status: api.get(status, 0) for status in EXPECTED_API_STATUS} | dict(api),
            "manual": dict(manual), "manual_completed_by_model": dict(sorted(manual_completed.items()))}


def check_final_statuses(entries: list[dict]) -> dict:
    counts = status_counts(entries)
    require(counts["api"] == EXPECTED_API_STATUS, f"API statuses are {counts['api']}, expected {EXPECTED_API_STATUS}")
    require(counts["manual_completed_by_model"] == EXPECTED_MANUAL_COMPLETED,
            f"manual completion is {counts['manual_completed_by_model']}, expected {EXPECTED_MANUAL_COMPLETED}")
    require(counts["manual"] == {"completed": sum(EXPECTED_MANUAL_COMPLETED.values())},
            f"manual statuses are {counts['manual']}, expected 130 completed")
    return counts


# Snapshot transitions -------------------------------------------------------------

def check_transitions(frozen_state: dict, live_state: dict) -> dict:
    """API rows must equal the frozen snapshot exactly; manual rows may only move pending -> completed."""
    frozen_rows = frozen_state["rows"]
    live_rows = live_state["rows"]
    require([row["run_id"] for row in frozen_rows] == [row["run_id"] for row in live_rows],
            "frozen and live collection states describe different rows")
    transitions: Counter = Counter()
    for before, after in zip(frozen_rows, live_rows):
        for key in ("cohort_order", "model_condition_id", "collection_interface"):
            require(before[key] == after[key], f"row identity changed since freeze: {before['run_id']} ({key})")
        interface = before["collection_interface"]
        if interface == "api":
            require(before == after, f"API row changed since freeze: {before['run_id']}")
        else:
            require(before["status"] == "pending" and before["evidence"] is None,
                    f"frozen manual row was not pending: {before['run_id']}")
            require(after["status"] == "completed" and after["evidence"] is not None,
                    f"manual row is not completed with evidence: {after['run_id']}")
        transitions[f"{interface}:{before['status']}->{after['status']}"] += 1
    return dict(sorted(transitions.items()))


# 8: manual evidence ----------------------------------------------------------------

def check_manual_evidence(rows: list[dict[str, str]], entries: list[dict], manual_root: Path) -> int:
    """Each manual row's prompt bytes equal the frozen prompt hash; no extra manual directory exists."""
    manual_rows = {row["run_id"]: row for row in rows if row["collection_interface"] == "manual"}
    present = {path.name for path in manual_root.iterdir() if path.is_dir()} if manual_root.is_dir() else set()
    require(present == set(manual_rows),
            f"manual evidence directories differ from manual-assigned rows: "
            f"missing {sorted(set(manual_rows) - present)[:5]}, unexpected {sorted(present - set(manual_rows))[:5]}")
    by_run = {entry["run_id"]: entry for entry in entries}
    for run_id, row in manual_rows.items():
        directory = manual_root / run_id
        evidence = by_run[run_id]["evidence"]
        require(evidence is not None, f"manual row has no evidence: {run_id}")
        require(digest(directory / "prompt.txt") == row["expected_prompt_sha256"] == evidence["prompt_sha256"],
                f"manual prompt bytes differ from frozen prompt: {run_id}")
        metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
        require(digest(directory / "response.md") == metadata.get("raw_response_sha256") == evidence["response_sha256"],
                f"manual response bytes differ from recorded hash: {run_id}")
    return len(manual_rows)


# 9-10: raw inventory (D043) -------------------------------------------------------

def check_raw_inventory(inventory: Path, root: Path, raw_root: Path,
                        expected_sha256: str = RAW_INVENTORY_SHA256, expected_files: int = RAW_INVENTORY_FILES) -> int:
    require(digest(inventory) == expected_sha256, "raw evidence inventory SHA-256 differs from D043")
    listed: dict[str, str] = {}
    for number, line in enumerate(inventory.read_text(encoding="utf-8").splitlines(), 1):
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        require(match is not None, f"malformed inventory line {number}")
        require(match.group(2) not in listed, f"duplicate inventory path: {match.group(2)}")
        listed[match.group(2)] = match.group(1)
    require(len(listed) == expected_files, f"inventory lists {len(listed)} files, expected {expected_files}")
    on_disk = set()
    for path in raw_root.rglob("*"):
        require(not path.is_symlink(), f"raw evidence contains a symbolic link: {path.relative_to(root)}")
        if path.is_file():
            on_disk.add(str(path.relative_to(root)))
    require(on_disk == set(listed), f"raw files differ from inventory: missing {sorted(set(listed) - on_disk)[:5]}, "
                                    f"unlisted {sorted(on_disk - set(listed))[:5]}")
    for relative, expected in listed.items():
        require(digest(root / relative) == expected, f"raw evidence file differs from inventory: {relative}")
    return len(listed)


def classify_raw_directories(raw_root: Path, rows: list[dict[str, str]], m2_paths: set[str], root: Path) -> dict:
    """Separate preserved raw directories into final-study API observations and historical evidence.

    Preservation is not eligibility: only the 140 API-assigned v2.7 rows are
    final-study observations.  The 11 M2 directories and every earlier-version
    directory are historical evidence only.  Any other ``API-v2.6-*`` directory,
    any ``API-v2.7-*`` directory, or a raw API directory for a manual row fails.
    """
    api_rows = {row["run_id"] for row in rows if row["collection_interface"] == "api"}
    manual_rows = {row["run_id"] for row in rows if row["collection_interface"] == "manual"}
    final, m2, historical, unexpected = [], [], [], []
    for directory in sorted(path for path in raw_root.iterdir() if path.is_dir()):
        name, relative = directory.name, str(directory.relative_to(root))
        if name in api_rows:
            final.append(name)
        elif relative in m2_paths:
            m2.append(name)
        elif name.startswith(("API-v2.6-", "API-v2.7-")) or name in manual_rows:
            unexpected.append(name)
        else:
            historical.append(name)
    require(not unexpected, f"unexpected raw run directories treated as neither final nor historical: {unexpected[:5]}")
    require(set(final) == api_rows, f"retained v2.7 API rows without v2.6 evidence: {sorted(api_rows - set(final))[:5]}")
    require({str(raw_root.relative_to(root) / name) for name in m2} == m2_paths,
            "historical M2 evidence differs from the frozen M2 inventory")
    return {"final_study_api": final, "historical_m2": m2, "historical_other_versions": historical}


# 11-12: freeze tag and frozen hashes ----------------------------------------------

def frozen_hash_pairs(record: object) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    if isinstance(record, dict):
        if isinstance(record.get("path"), str) and isinstance(record.get("sha256"), str):
            pairs.append((record["path"], record["sha256"]))
        for value in record.values():
            pairs.extend(frozen_hash_pairs(value))
    elif isinstance(record, list):
        for value in record:
            pairs.extend(frozen_hash_pairs(value))
    return pairs


def check_frozen_hashes(record: dict, root: Path) -> int:
    pairs = frozen_hash_pairs(record)
    require(pairs, "freeze record lists no frozen hashes")
    for path, expected in pairs:
        require((root / path).is_file(), f"frozen file missing: {path}")
        require(digest(root / path) == expected, f"frozen file differs from its recorded hash: {path}")
    return len(pairs)


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(ROOT), capture_output=True, text=True)


def check_freeze_tag(record: dict) -> int:
    resolved = git("rev-parse", f"{FREEZE_TAG}^{{commit}}")
    require(resolved.returncode == 0, f"cannot resolve {FREEZE_TAG}: {resolved.stderr.strip()}")
    require(resolved.stdout.strip() == FREEZE_COMMIT, f"{FREEZE_TAG} points to {resolved.stdout.strip()}, expected {FREEZE_COMMIT}")
    frozen_paths = sorted({path for path, _ in frozen_hash_pairs(record)} | {
        str(FREEZE_RECORD.relative_to(ROOT)), str(FREEZE_MARKDOWN.relative_to(ROOT)), str(FROZEN_SCRIPT.relative_to(ROOT))})
    unchanged = git("diff", "--quiet", FREEZE_COMMIT, "--", *frozen_paths)
    require(unchanged.returncode == 0, f"frozen tracked files differ from {FREEZE_TAG}")
    return len(frozen_paths)


# 13: derived completion record ------------------------------------------------------

def check_completion_record(record: dict, frozen_state: dict, live_state: dict, counts: dict,
                            transitions: dict, markdown_text: str, record_sha256: str) -> None:
    rows = record.get("rows", [])
    require(len(rows) == len(live_state["rows"]), "completion record row count differs from the evidence")
    frozen_by_run = {row["run_id"]: row for row in frozen_state["rows"]}
    for derived, live in zip(rows, live_state["rows"]):
        run_id = live["run_id"]
        require(derived.get("run_id") == run_id and derived.get("cohort_order") == live["cohort_order"],
                f"completion record order differs at {run_id}")
        require(derived.get("model_condition_id") == live["model_condition_id"]
                and derived.get("collection_interface") == live["collection_interface"],
                f"completion record identity differs: {run_id}")
        require(derived.get("final_observed_status") == live["status"], f"completion record status differs: {run_id}")
        require(derived.get("evidence") == live["evidence"], f"completion record evidence hashes differ: {run_id}")
        require(derived.get("frozen_initial_status") == frozen_by_run[run_id]["status"],
                f"completion record frozen status differs: {run_id}")
    observed = record.get("final_observed_state", {})
    api_observed = {k: v for k, v in counts["api"].items() if v}
    require(observed.get("api_status_counts") == api_observed, "completion record API counts differ from the evidence")
    require(observed.get("manual_completed_by_model") == counts["manual_completed_by_model"],
            "completion record manual counts differ from the evidence")
    require(observed.get("status_counts_by_model") == live_state["status_counts_by_model"],
            "completion record per-model counts differ from the evidence")
    require(observed.get("assigned_rows") == EXPECTED_ROWS and observed.get("pending_rows") == 0
            and observed.get("m2_rows") == 0, "completion record totals differ")
    require(record.get("transitions_from_frozen_state") == transitions, "completion record transitions differ")
    require(record.get("api_rows_changed_since_freeze") == 0, "completion record reports changed API rows")
    planned = record.get("frozen_planned_state", {})
    require(planned.get("sha256") == digest(frozen.STATE) and planned.get("status_counts") == frozen_state["status_counts"],
            "completion record frozen-state reference differs")
    freeze = record.get("freeze", {})
    require(freeze.get("tag") == FREEZE_TAG and freeze.get("commit") == FREEZE_COMMIT
            and freeze.get("freeze_record_sha256") == FREEZE_RECORD_SHA256
            and freeze.get("manifest_sha256") == digest(frozen.MANIFEST), "completion record freeze reference differs")
    raw = record.get("evidence_sources", {}).get("api_raw", {})
    require(raw.get("inventory_sha256") == RAW_INVENTORY_SHA256 and raw.get("inventory_regular_files") == RAW_INVENTORY_FILES,
            "completion record raw-inventory reference differs")
    require(record.get("derivation", {}).get("generator_script_sha256") == FROZEN_SCRIPT_SHA256,
            "completion record derivation script hash differs")
    require(record.get("primary_analysis_eligibility", {}).get("determined_by_this_record") is False,
            "completion record must not determine primary-analysis eligibility")
    stated = re.search(r"final_collection_completion_v2\.7\.0\.json` \(SHA-256 `([0-9a-f]{64})`\)", markdown_text)
    require(stated is not None and stated.group(1) == record_sha256,
            "completion Markdown does not state the JSON record's SHA-256")


# 14: collection status is not eligibility ---------------------------------------------

def check_policies_exclude(freeze_record: dict) -> None:
    for policy in ("truncation_policy", "failure_policy"):
        require(freeze_record.get(policy, {}).get("exclude_from_primary_shr_phr_denominators") is True,
                f"frozen {policy} does not exclude from primary denominators")


def eligibility_summary(entries: list[dict]) -> dict:
    """Truncated/failed rows are never primary candidates; completed rows are candidates only."""
    excluded = Counter(entry["status"] for entry in entries if entry["status"] in PRIMARY_EXCLUDED_STATUSES)
    candidates = primary_candidate_run_ids(entries)
    return {"excluded_by_frozen_policy": dict(sorted(excluded.items())), "candidate_rows": len(candidates),
            "note": "candidates have collection status completed; primary eligibility is decided downstream "
                    "(including the D035 finish-reason overlay), not by this verifier"}


def primary_candidate_run_ids(entries: list[dict]) -> list[str]:
    return [entry["run_id"] for entry in entries if entry["status"] == "completed"]


# Orchestration ---------------------------------------------------------------------------

def run_checks() -> list[tuple[str, str]]:
    results: list[tuple[str, str]] = []

    def done(name: str, detail: object) -> None:
        results.append((name, str(detail)))

    frozen.verify_sources()
    freeze_record = json.loads(FREEZE_RECORD.read_text(encoding="utf-8"))
    require(digest(FREEZE_RECORD) == FREEZE_RECORD_SHA256, "v2.7 freeze record differs from its frozen hash")
    require(digest(FROZEN_SCRIPT) == FROZEN_SCRIPT_SHA256, "frozen v2.7 freeze script differs from its recorded hash")
    model_set = json.loads(frozen.MODEL_SET.read_text(encoding="utf-8"))
    frozen.validate_model_set(model_set)
    rows = frozen.final_study_rows()
    require(frozen.MANIFEST.read_bytes() == frozen.csv_bytes(frozen.build_manifest_rows()),
            "v2.7 manifest is not the deterministic v2.6-minus-M2 filter")
    done("design (270 rows; M1/M3/M4 x 90; M2 0; API 140 / manual 130)", check_design(rows, model_set))

    frozen_state = json.loads(frozen.STATE.read_text(encoding="utf-8"))
    require(digest(frozen.STATE) == freeze_record["initial_collection_state"]["sha256"],
            "frozen collection state differs from its freeze-record hash")
    live_state = frozen.derive_collection_state(rows, frozen_state["derived_at_utc"])
    live_state["source_v2_6_state_snapshot"] = frozen_state["source_v2_6_state_snapshot"]
    counts = check_final_statuses(live_state["rows"])
    done("final API statuses", counts["api"])
    done("final manual completion", counts["manual_completed_by_model"])
    transitions = check_transitions(frozen_state, live_state)
    done("transitions from frozen snapshot", transitions)

    done("manual evidence hashes", f"{check_manual_evidence(rows, live_state['rows'], frozen.MANUAL_RAW_ROOT)} rows verified")
    done("raw evidence inventory (D043)", f"{check_raw_inventory(RAW_INVENTORY, ROOT, frozen.API_RAW_ROOT)} files verified; "
                                         f"inventory SHA-256 {RAW_INVENTORY_SHA256}")
    m2_paths = {item["path"] for item in freeze_record["m2_exclusion"]["preserved_evidence"]}
    require(len(m2_paths) == EXPECTED_M2_HISTORICAL_DIRECTORIES, "frozen M2 evidence inventory size differs")
    classes = classify_raw_directories(frozen.API_RAW_ROOT, rows, m2_paths, ROOT)
    done("raw directory classification", {key: len(value) for key, value in classes.items()})

    done("frozen tracked hashes", f"{check_frozen_hashes(freeze_record, ROOT)} pairs match")
    done(f"{FREEZE_TAG} -> {FREEZE_COMMIT}", f"{check_freeze_tag(freeze_record)} frozen paths unchanged since tag")

    completion = json.loads(COMPLETION_RECORD.read_text(encoding="utf-8"))
    check_completion_record(completion, frozen_state, live_state, counts, transitions,
                            COMPLETION_MARKDOWN.read_text(encoding="utf-8"), digest(COMPLETION_RECORD))
    done("derived completion record agrees with evidence", str(COMPLETION_RECORD.relative_to(ROOT)))

    check_policies_exclude(freeze_record)
    done("analysis eligibility not asserted", eligibility_summary(live_state["rows"]))
    return results


def main() -> int:
    argparse.ArgumentParser(description="Read-only FINAL_COMPLETION_CHECK for the completed v2.7 final study").parse_args()
    try:
        results = run_checks()
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"FINAL_COMPLETION_CHECK: FAIL: {error}", file=sys.stderr)
        return 1
    for name, detail in results:
        print(f"PASS  {name}: {detail}")
    print("FINAL_COMPLETION_CHECK: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
