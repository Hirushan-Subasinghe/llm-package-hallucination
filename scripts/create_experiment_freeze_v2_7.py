#!/usr/bin/env python3
"""Create or verify the v2.7 three-condition final-study freeze; never overwrite it.

v2.7 is the frozen v2.6 design minus the whole M2 condition.  Membership is the
exact set difference ``v2.6 run IDs - M2 run IDs``; no outcome field participates.
Retained rows keep their v2.6 run IDs, task/category/repetition identities,
prompt bytes and HYBRID interface assignment.  Existing v2.6 raw evidence is
referenced in place by hash; nothing under ``data/final/raw`` is written, copied,
renamed or regenerated, and no v2.6 input or state file is modified.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Frozen v2.6 source artifacts (verified by hash before any derivation).
SOURCE_FREEZE = ROOT / "config/experiment_freeze_v2.6.0.json"
SOURCE_MODEL_SET = ROOT / "config/api_model_set_1.4.0.json"
SOURCE_MANIFEST = ROOT / "manifests/api_final_v2.6.0_manifest.csv"
SOURCE_ASSIGNMENT = ROOT / "manifests/hybrid_assignment_v1.0.0.csv"
SOURCE_STATE = ROOT / "data/final/api_batch_state_v2.6.0.json"
SOURCE_HASHES = {
    SOURCE_FREEZE: "53736d8a38fb4f497fc525cff7453693cd2ed0154b0c55a14172ea39164d5719",
    SOURCE_MODEL_SET: "cba4a4ec3c785132523beb860db944b5d3b0ecacc429f8d6674889f34b35ad8c",
    SOURCE_MANIFEST: "b2b2750b3ae4ce96a867df14117b05c12f214760ef7036d6bbf2f78e44939b7f",
    SOURCE_ASSIGNMENT: "e4b9295b2efc0fe639092161561e915c1d0c47f9a545df2699f7fe12595dd54f",
}
SOURCE_FREEZE_TAG = "v2.6.0-freeze"
SOURCE_FREEZE_COMMIT = "5247c2bccb58ecd6c86b9b7e92d800ade0378282"
TASKS = ROOT / "prompts/tasks/final_2.0.0.jsonl"
TEMPLATE = ROOT / "prompts/prompt_template_v2.6.0.md"
API_RAW_ROOT = ROOT / "data/final/raw"
# Existing offline manual-capture root; retained M1/M3/M4 manual rows keep their v2.6 run IDs.
MANUAL_RAW_ROOT = ROOT / "data/final/manual_raw/v2.6.0"

# v2.7 outputs.
MODEL_SET = ROOT / "config/api_model_set_1.5.0.json"
MODEL_SET_SCHEMA = ROOT / "schemas/api_model_set_v2_7.schema.json"
MANIFEST = ROOT / "manifests/api_final_v2.7.0_manifest.csv"
STATE = ROOT / "data/final/collection_state_v2.7.0.json"
OUTPUT_JSON = ROOT / "config/experiment_freeze_v2.7.0.json"
OUTPUT_MARKDOWN = ROOT / "docs/experiment_freeze_v2.7.0.md"
SCHEMAS = (
    MODEL_SET_SCHEMA,
    ROOT / "schemas/api_manifest_row.schema.json",
    ROOT / "schemas/api_collection_metadata.schema.json",
    ROOT / "schemas/task_record_v2.schema.json",
)

RETAINED = ("M1", "M3", "M4")
EXCLUDED = "M2"
EXPECTED_ROWS = 270
EXPECTED_INTERFACE = {"M1": {"api": 40, "manual": 50}, "M3": {"api": 41, "manual": 49}, "M4": {"api": 59, "manual": 31}}
FIELDS = (
    "cohort_order", "run_id", "source_collection_order", "phase", "task_id", "category",
    "task_set_version", "model_set_version", "source_model_set_version", "model_condition_id",
    "model_id", "api_provider", "underlying_provider_pin", "run_repetition",
    "rendered_prompt_path", "expected_prompt_sha256", "collection_interface",
)
M2_EXCLUSION_RATIONALE = (
    "Operational: the intended automatic API collection route for M2 (qwen/qwen3.8-27b via "
    "Darkbloom-only OpenRouter) could not complete the required collection protocol consistently."
)


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def digest(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def verify_sources() -> None:
    for path, expected in SOURCE_HASHES.items():
        if digest(path) != expected:
            raise ValueError(f"frozen v2.6 source differs from its recorded hash: {rel(path)}")


def build_model_set(frozen_at_utc: str) -> dict:
    """api-model-set-1.5.0: the 1.4.0 set with M2 removed and nothing else changed."""
    source = json.loads(SOURCE_MODEL_SET.read_text(encoding="utf-8"))
    config = {key: value for key, value in source.items() if key != "models"}
    config["$schema"] = "../schemas/api_model_set_v2_7.schema.json"
    config["model_set_version"] = "api-model-set-1.5.0"
    config["frozen_at_utc"] = frozen_at_utc
    config["models"] = [model for model in source["models"] if model["condition_id"] != EXCLUDED]
    config["source_model_set"] = {
        "version": source["model_set_version"], "path": rel(SOURCE_MODEL_SET), "sha256": digest(SOURCE_MODEL_SET),
        "retained_condition_ids": list(RETAINED), "excluded_condition_ids": [EXCLUDED],
        "retained_condition_definitions": "identical_to_source_model_set",
    }
    return config


def validate_model_set(config: dict) -> None:
    source = json.loads(SOURCE_MODEL_SET.read_text(encoding="utf-8"))
    if config.get("model_set_version") != "api-model-set-1.5.0":
        raise ValueError("unexpected v2.7 model_set_version")
    if [model.get("condition_id") for model in config.get("models", [])] != list(RETAINED):
        raise ValueError("v2.7 model set must contain exactly M1, M3 and M4 in that order")
    expected = {model["condition_id"]: model for model in source["models"]}
    for model in config["models"]:
        if model != expected[model["condition_id"]]:
            raise ValueError(f"retained condition differs from api-model-set-1.4.0: {model['condition_id']}")
    for key, value in source.items():
        if key not in {"$schema", "model_set_version", "frozen_at_utc", "models"} and config.get(key) != value:
            raise ValueError(f"v2.7 model set changed inherited field: {key}")


def build_manifest_rows() -> list[dict[str, str]]:
    """Exact v2.6-minus-M2 filter in original frozen order; interface inherited unchanged."""
    source_rows = read_csv(SOURCE_MANIFEST)
    assignment = {row["run_id"]: row for row in read_csv(SOURCE_ASSIGNMENT)}
    if len(source_rows) != 360 or len(assignment) != 360 or set(assignment) != {row["run_id"] for row in source_rows}:
        raise ValueError("v2.6 manifest and HYBRID assignment must describe the same 360 rows")
    rows = []
    for source in source_rows:
        if source["model_condition_id"] == EXCLUDED:
            continue
        assigned = assignment[source["run_id"]]
        for field in ("collection_order", "model_condition_id", "run_repetition", "task_id", "category"):
            if assigned[field] != source[field]:
                raise ValueError(f"HYBRID assignment identity differs from v2.6 manifest: {source['run_id']}")
        rows.append({
            "cohort_order": str(len(rows) + 1),
            "run_id": source["run_id"],
            "source_collection_order": source["collection_order"],
            "phase": source["phase"],
            "task_id": source["task_id"],
            "category": source["category"],
            "task_set_version": source["task_set_version"],
            "model_set_version": "api-model-set-1.5.0",
            "source_model_set_version": source["model_set_version"],
            "model_condition_id": source["model_condition_id"],
            "model_id": source["model_id"],
            "api_provider": source["api_provider"],
            "underlying_provider_pin": source["underlying_provider_pin"],
            "run_repetition": source["run_repetition"],
            "rendered_prompt_path": source["rendered_prompt_path"],
            "expected_prompt_sha256": source["expected_prompt_sha256"],
            "collection_interface": assigned["collection_interface"],
        })
    return rows


def csv_bytes(rows: list[dict[str, str]]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def validate_manifest_rows(rows: list[dict[str, str]]) -> None:
    if len(rows) != EXPECTED_ROWS or len({row["run_id"] for row in rows}) != EXPECTED_ROWS:
        raise ValueError("v2.7 manifest must contain 270 unique rows")
    if any(row["model_condition_id"] == EXCLUDED for row in rows):
        raise ValueError("M2 must not appear in the v2.7 final-study manifest")
    models = Counter(row["model_condition_id"] for row in rows)
    if models != Counter({condition: 90 for condition in RETAINED}):
        raise ValueError(f"v2.7 rows per model differ: {dict(models)}")
    cells = Counter((row["task_id"], row["model_condition_id"], row["run_repetition"]) for row in rows)
    if len(cells) != EXPECTED_ROWS or len({row["task_id"] for row in rows}) != 30:
        raise ValueError("every task x retained model x repetition cell must occur exactly once")
    if Counter(row["run_repetition"] for row in rows) != Counter({"R01": 90, "R02": 90, "R03": 90}):
        raise ValueError("v2.7 rows per repetition differ")
    categories = Counter(row["category"] for row in rows)
    if len(categories) != 6 or set(categories.values()) != {45}:
        raise ValueError("v2.7 rows per category differ")
    for condition, expected in EXPECTED_INTERFACE.items():
        observed = Counter(row["collection_interface"] for row in rows if row["model_condition_id"] == condition)
        if observed != Counter(expected):
            raise ValueError(f"inherited interface assignment differs for {condition}")
    orders = [int(row["source_collection_order"]) for row in rows]
    if orders != sorted(orders) or [int(row["cohort_order"]) for row in rows] != list(range(1, EXPECTED_ROWS + 1)):
        raise ValueError("v2.7 manifest must preserve original v2.6 relative order")


def final_study_rows(manifest_path: Path = MANIFEST) -> list[dict[str, str]]:
    """The only supported v2.7 final-analysis selection; fails closed if M2 is present."""
    rows = read_csv(manifest_path)
    validate_manifest_rows(rows)
    return rows


def _api_evidence(row: dict[str, str], directory: Path) -> tuple[str, dict]:
    metadata_path = directory / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    identity = (metadata.get("run_id"), metadata.get("task_id"), metadata.get("category"), metadata.get("model_condition_id"),
                metadata.get("requested_model_id"), f"R{metadata.get('run_repetition', 0):02d}", str(metadata.get("collection_order")))
    if identity != (row["run_id"], row["task_id"], row["category"], row["model_condition_id"], row["model_id"],
                    row["run_repetition"], row["source_collection_order"]):
        raise ValueError(f"raw metadata identity differs from v2.7 row: {row['run_id']}")
    prompt_hash = digest(directory / "prompt.txt")
    if metadata.get("prompt_sha256") != row["expected_prompt_sha256"] or prompt_hash != row["expected_prompt_sha256"]:
        raise ValueError(f"raw prompt bytes differ from frozen prompt: {row['run_id']}")
    status = metadata.get("collection_status")
    if status not in {"completed", "truncated", "failed"}:
        raise ValueError(f"API observation is not finalized: {row['run_id']} ({status})")
    response = directory / "response.md"
    response_hash = digest(response) if response.exists() else None
    if response_hash is not None and metadata.get("response_sha256") != response_hash:
        raise ValueError(f"raw response bytes differ from recorded hash: {row['run_id']}")
    return status, {
        "source": "v2.6_api_raw", "path": rel(directory), "metadata_sha256": digest(metadata_path),
        "prompt_sha256": prompt_hash, "response_sha256": response_hash,
        "source_model_set_version": metadata.get("model_set_version"),
    }


def _manual_evidence(row: dict[str, str], directory: Path) -> tuple[str, dict] | None:
    metadata_path = directory / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("response_status") == "initialized":
        return None
    if (metadata.get("run_id"), metadata.get("model_condition_id"), metadata.get("run_repetition"), metadata.get("task_id"),
            metadata.get("prompt_sha256"), metadata.get("collection_interface")) != (
            row["run_id"], row["model_condition_id"], row["run_repetition"], row["task_id"], row["expected_prompt_sha256"], "manual"):
        raise ValueError(f"manual metadata identity differs from v2.7 row: {row['run_id']}")
    response_hash = digest(directory / "response.md")
    if metadata.get("raw_response_sha256") != response_hash:
        raise ValueError(f"manual response bytes differ from recorded hash: {row['run_id']}")
    return metadata["response_status"], {
        "source": "manual_raw", "path": rel(directory), "metadata_sha256": digest(metadata_path),
        "prompt_sha256": digest(directory / "prompt.txt"), "response_sha256": response_hash,
    }


def derive_collection_state(rows: list[dict[str, str]], derived_at_utc: str) -> dict:
    """Read-only provenance mapping of each v2.7 row to already-preserved evidence."""
    entries = []
    for row in rows:
        api_dir, manual_dir = API_RAW_ROOT / row["run_id"], MANUAL_RAW_ROOT / row["run_id"]
        status, evidence = "pending", None
        if row["collection_interface"] == "api":
            if manual_dir.exists():
                raise ValueError(f"API-assigned row has a manual artifact: {row['run_id']}")
            if not api_dir.exists():
                raise ValueError(f"API-assigned retained row has no preserved v2.6 observation: {row['run_id']}")
            status, evidence = _api_evidence(row, api_dir)
        else:
            if api_dir.exists():
                raise ValueError(f"manual-assigned row has an API artifact: {row['run_id']}")
            if manual_dir.exists():
                found = _manual_evidence(row, manual_dir)
                if found is not None:
                    status, evidence = found
        entries.append({
            "cohort_order": int(row["cohort_order"]), "run_id": row["run_id"],
            "model_condition_id": row["model_condition_id"], "collection_interface": row["collection_interface"],
            "status": status, "evidence": evidence,
        })
    by_model: dict[str, Counter] = {condition: Counter() for condition in RETAINED}
    for entry in entries:
        by_model[entry["model_condition_id"]][f"{entry['collection_interface']}_{entry['status']}"] += 1
    return {
        "state_version": "collection-state-v2.7.0",
        "derived_at_utc": derived_at_utc,
        "derivation": "read_only_provenance_mapping_no_regeneration",
        "manifest_path": rel(MANIFEST),
        "manifest_sha256": sha256_bytes(csv_bytes(rows)),
        "source_v2_6_state_snapshot": {"path": rel(SOURCE_STATE), "sha256": digest(SOURCE_STATE),
                                       "note": "rolling v2.6 operational file; read only, never written by v2.7"},
        "status_counts_by_model": {condition: dict(sorted(counts.items())) for condition, counts in by_model.items()},
        "status_counts": dict(sorted(Counter(entry["status"] for entry in entries).items())),
        "rows": entries,
    }


def m2_preserved_evidence() -> list[dict]:
    """Inventory (read-only) of every preserved M2 artifact directory; M2 is historical evidence only."""
    items = []
    for directory in sorted(API_RAW_ROOT.glob("API-v2.6-*-M2-R0*")) + sorted(MANUAL_RAW_ROOT.glob("API-v2.6-*-M2-R0*")):
        metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
        response = directory / "response.md"
        items.append({
            "path": rel(directory), "metadata_sha256": digest(directory / "metadata.json"),
            "response_sha256": digest(response) if response.exists() else None,
            "status": metadata.get("collection_status", metadata.get("response_status")),
            "failure_reason": metadata.get("failure_reason"),
        })
    return items


def build_record(created_at_utc: str, state: dict) -> dict:
    verify_sources()
    source_freeze = json.loads(SOURCE_FREEZE.read_text(encoding="utf-8"))
    model_set = json.loads(MODEL_SET.read_text(encoding="utf-8"))
    validate_model_set(model_set)
    rows = build_manifest_rows()
    validate_manifest_rows(rows)
    if MANIFEST.read_bytes() != csv_bytes(rows):
        raise ValueError("v2.7 manifest is not the deterministic v2.6-minus-M2 filter")
    if digest(TASKS) != source_freeze["task_set"]["sha256"] or digest(TEMPLATE) != source_freeze["prompt_template"]["sha256"]:
        raise ValueError("task set or prompt template differs from v2.6")
    for prompt in source_freeze["rendered_prompts"]:
        if digest(ROOT / prompt["path"]) != prompt["sha256"]:
            raise ValueError(f"rendered prompt differs from v2.6: {prompt['path']}")
    m2 = m2_preserved_evidence()
    m2_status = Counter(item["status"] for item in m2)
    ceilings = {model["condition_id"]: model["max_output_tokens"] for model in model_set["models"]}
    interface = Counter(row["collection_interface"] for row in rows)
    source_m2 = [model for model in json.loads(SOURCE_MODEL_SET.read_text(encoding="utf-8"))["models"] if model["condition_id"] == EXCLUDED][0]
    mapped = [entry for entry in state["rows"] if entry["evidence"] is not None]
    return {
        "freeze_record_version": "experiment-freeze-v2.7.0",
        "freeze_record_created_at_utc": created_at_utc,
        "dataset_strategy": "three_condition_cohort_derived_from_frozen_v2_6_by_whole_condition_exclusion",
        "final_protocol_intent": True,
        "source_experiment": {
            "version": "v2.6.0", "freeze_tag": SOURCE_FREEZE_TAG, "freeze_commit": SOURCE_FREEZE_COMMIT,
            "freeze_record": {"path": rel(SOURCE_FREEZE), "sha256": digest(SOURCE_FREEZE)},
            "manifest": {"path": rel(SOURCE_MANIFEST), "sha256": digest(SOURCE_MANIFEST), "row_count": 360},
            "hybrid_assignment": {"path": rel(SOURCE_ASSIGNMENT), "sha256": digest(SOURCE_ASSIGNMENT), "row_count": 360},
            "model_set": {"path": rel(SOURCE_MODEL_SET), "sha256": digest(SOURCE_MODEL_SET), "version": "api-model-set-1.4.0"},
            "preservation": "All v2.6 inputs, state, raw observations and records are preserved unchanged as historical evidence.",
        },
        "design_change": {
            "planned_observations": {"v2.6.0": 360, "v2.7.0": EXPECTED_ROWS},
            "model_conditions": {"v2.6.0": ["M1", "M2", "M3", "M4"], "v2.7.0": list(RETAINED)},
            "condition_ids_renumbered": False,
            "membership_rule": "v2.6 manifest run IDs minus every M2 run ID; no outcome, status or response field participates.",
            "other_protocol_changes": "none",
        },
        "m2_exclusion": {
            "condition_id": EXCLUDED, "model_id": source_m2["model_id"], "api_provider": source_m2["api_provider"],
            "provider_pin": source_m2["openrouter_routing"]["underlying_provider_slug"],
            "excluded_planned_rows": 90, "scope": "whole_condition",
            "rationale": M2_EXCLUSION_RATIONALE,
            "operational_evidence_at_freeze": {
                "preserved_artifact_directories": len(m2), "completed": m2_status.get("completed", 0),
                "truncated": m2_status.get("truncated", 0), "failed": m2_status.get("failed", 0),
                "failure_reasons": dict(sorted(Counter(item["failure_reason"] for item in m2 if item["failure_reason"]).items())),
                "planned_rows_without_artifact": 90 - len(m2),
            },
            "result_values_used_for_exclusion": False,
            "result_values_note": "The recorded rationale uses collection outcomes only. No v2.6 package-extraction, registry-validation, classification, metric or risk output exists in the repository for M2 or any condition.",
            "timing": "before_final_analysis_after_partial_m2_collection",
            "final_study_metric_inclusion": False,
            "preserved_evidence": m2,
        },
        "official_manifest": {
            "path": rel(MANIFEST), "sha256": digest(MANIFEST), "row_count": EXPECTED_ROWS, "fields": list(FIELDS),
            "rows_per_model": dict(sorted(Counter(row["model_condition_id"] for row in rows).items())),
            "rows_per_repetition": dict(sorted(Counter(row["run_repetition"] for row in rows).items())),
            "rows_per_category": dict(sorted(Counter(row["category"] for row in rows).items())),
            "rows_per_interface": dict(sorted(interface.items())),
            "rows_per_model_interface": {condition: dict(sorted(Counter(row["collection_interface"] for row in rows if row["model_condition_id"] == condition).items())) for condition in RETAINED},
            "run_id_policy": "retained v2.6 run IDs unchanged; cohort_order is contiguous 1-270 and source_collection_order preserves v2.6 order",
        },
        "interface_assignment": {
            "source": "inherited unchanged from hybrid_assignment_v1.0.0 by filtering; no retained row reassigned",
            "api": interface["api"], "manual": interface["manual"], "balanced": False,
            "analysis_note": "Interface is unevenly associated with model condition; analyses must not claim interface balance.",
        },
        "evidence_reuse": {
            "mechanism": "in-place provenance mapping by run ID and SHA-256; no copy, rename, rewrite or regeneration",
            "verified_fields": ["run_id", "task_id", "category", "model_condition_id", "requested_model_id", "run_repetition",
                                "source_collection_order", "prompt_bytes_sha256", "collection_interface", "response_sha256"],
            "mapped_rows": len(mapped),
            "source_model_set_version_of_mapped_api_rows": sorted({entry["evidence"].get("source_model_set_version") for entry in mapped if entry["evidence"]["source"] == "v2.6_api_raw"}),
            "condition_equivalence": "Mapped API observations were generated under api-model-set-1.4.0; their M1/M3/M4 definitions are identical in api-model-set-1.5.0.",
        },
        "initial_collection_state": {
            "path": rel(STATE), "sha256": digest(STATE),
            "status_counts": state["status_counts"], "status_counts_by_model": state["status_counts_by_model"],
        },
        "model_set": {
            "version": model_set["model_set_version"], "path": rel(MODEL_SET), "sha256": digest(MODEL_SET),
            "models": [{"condition_id": m["condition_id"], "model_id": m["model_id"], "api_provider": m["api_provider"],
                        "provider_pin": m["openrouter_routing"]["underlying_provider_slug"] if m["api_provider"] == "OpenRouter" else "not_applicable",
                        "max_output_tokens": m["max_output_tokens"]} for m in model_set["models"]],
        },
        "task_set": source_freeze["task_set"],
        "prompt_template": source_freeze["prompt_template"] | {"reuse": "v2.6 template referenced by unchanged hash; not copied"},
        "rendered_prompts": source_freeze["rendered_prompts"],
        "sampling_parameters": source_freeze["sampling_parameters"] | {"max_output_tokens_by_model": ceilings},
        "retry_policy": source_freeze["retry_policy"],
        "batch_pacing": source_freeze["batch_pacing"],
        "failure_policy": source_freeze["failure_policy"],
        "truncation_policy": source_freeze["truncation_policy"],
        "schemas": [{"path": rel(path), "sha256": digest(path)} for path in SCHEMAS],
        "approval": {"instruction": "FINAL-STUDY-V2.7-MIGRATION-01", "decision_log_entry": "D036",
                     "commit_and_tag": "pending researcher review; not performed by this script"},
    }


def markdown(record: dict) -> str:
    model_rows = "\n".join(f"| {m['condition_id']} | `{m['model_id']}` | {m['api_provider']} | `{m['provider_pin']}` | {m['max_output_tokens']} | {record['official_manifest']['rows_per_model_interface'][m['condition_id']]['api']} | {record['official_manifest']['rows_per_model_interface'][m['condition_id']]['manual']} |" for m in record["model_set"]["models"])
    m2 = record["m2_exclusion"]
    ops = m2["operational_evidence_at_freeze"]
    m2_rows = "\n".join(f"| `{item['path']}` | {item['status']} | `{item['metadata_sha256']}` |" for item in m2["preserved_evidence"])
    state = record["initial_collection_state"]
    return f"""# Experiment Freeze Record — v2.7.0

Created at `{record['freeze_record_created_at_utc']}` before any final-study analysis.

v2.7.0 is the frozen v2.6.0 design with the whole M2 condition removed. Membership is the exact set difference of the v2.6 manifest minus every M2 row; no outcome field participates. Retained M1/M3/M4 rows keep their v2.6 run IDs, task/category/repetition identities, prompt bytes, and HYBRID interface assignment. Model-condition IDs are not renumbered.

## Design change

| | v2.6.0 | v2.7.0 |
| --- | ---: | ---: |
| Model conditions | 4 (M1, M2, M3, M4) | 3 (M1, M3, M4) |
| Planned observations | 360 | {record['official_manifest']['row_count']} |
| API / manual assignment | 180 / 180 | {record['interface_assignment']['api']} / {record['interface_assignment']['manual']} |

No other protocol element changes. The retained split is inherited, not rebalanced; interface is unevenly associated with model condition.

## Frozen inputs

- Source freeze: `{record['source_experiment']['freeze_record']['sha256']}` (`{record['source_experiment']['freeze_record']['path']}`, tag `{record['source_experiment']['freeze_tag']}`)
- Task set: `{record['task_set']['sha256']}` (`{record['task_set']['path']}`)
- Model set: `{record['model_set']['sha256']}` (`{record['model_set']['path']}`)
- Prompt template (reused, not copied): `{record['prompt_template']['sha256']}` (`{record['prompt_template']['path']}`)
- Manifest: `{record['official_manifest']['sha256']}` (`{record['official_manifest']['path']}`), {record['official_manifest']['row_count']} unique rows
- Initial collection state: `{state['sha256']}` (`{state['path']}`)

## Model conditions

| Condition | Model | API provider | Provider pin | Max output tokens | API rows | Manual rows |
| --- | --- | --- | --- | ---: | ---: | ---: |
{model_rows}

## M2 exclusion

M2 (`{m2['model_id']}`, {m2['api_provider']} pinned to `{m2['provider_pin']}`) is excluded in full: {m2['excluded_planned_rows']} planned rows. {m2['rationale']}

At freeze, M2 had {ops['preserved_artifact_directories']} preserved artifact directories ({ops['completed']} completed, {ops['truncated']} truncated, {ops['failed']} failed) and {ops['planned_rows_without_artifact']} planned rows without an artifact. The exclusion applies to the whole condition, including completed M2 outputs. {m2['result_values_note']} The exclusion occurred after partial M2 collection and before final analysis. All M2 evidence remains preserved unchanged as historical v2.6 evidence and is excluded from every v2.7 metric and denominator.

| Preserved M2 directory | Status | Metadata SHA-256 |
| --- | --- | --- |
{m2_rows}

## Evidence reuse

{record['evidence_reuse']['mapped_rows']} retained observations map in place to preserved v2.6 evidence by run ID and SHA-256; nothing is copied, renamed, rewritten, or regenerated. {record['evidence_reuse']['condition_equivalence']}

Initial status counts: {', '.join(f'{k} {v}' for k, v in state['status_counts'].items())}.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Create or verify the v2.7 freeze")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.check:
            record = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
            model_set = json.loads(MODEL_SET.read_text(encoding="utf-8"))
            if model_set != build_model_set(model_set["frozen_at_utc"]) or MODEL_SET.read_text(encoding="utf-8") != json.dumps(model_set, indent=2, sort_keys=True) + "\n":
                raise ValueError("v2.7 model set differs from api-model-set-1.4.0 minus M2")
            state = json.loads(STATE.read_text(encoding="utf-8"))
            if digest(STATE) != record["initial_collection_state"]["sha256"]:
                raise ValueError("v2.7 collection state differs from its frozen initial snapshot")
            rederived = derive_collection_state(build_manifest_rows(), state["derived_at_utc"])
            rederived["source_v2_6_state_snapshot"] = state["source_v2_6_state_snapshot"]
            if state != rederived:
                raise ValueError("v2.7 collection state no longer matches preserved evidence")
            expected = build_record(record["freeze_record_created_at_utc"], state)
            frozen_m2 = {item["path"]: item for item in record["m2_exclusion"]["preserved_evidence"]}
            current_m2 = {item["path"]: item for item in expected["m2_exclusion"]["preserved_evidence"]}
            if any(current_m2.get(path) != item for path, item in frozen_m2.items()):
                raise ValueError("preserved M2 evidence changed or disappeared")
            expected["m2_exclusion"] = record["m2_exclusion"]
            if record != expected or OUTPUT_MARKDOWN.read_text(encoding="utf-8") != markdown(record):
                raise ValueError("v2.7 freeze differs from its inputs")
            print("PASS: verified v2.7 freeze, model set, 270-row manifest, collection state, v2.6 sources, and preserved M2 evidence")
            return 0
        outputs = (MODEL_SET, MANIFEST, STATE, OUTPUT_JSON, OUTPUT_MARKDOWN)
        if any(path.exists() for path in outputs):
            raise ValueError("Refusing to overwrite an existing v2.7 artifact")
        verify_sources()
        now = utc_now()
        model_set = build_model_set(now)
        validate_model_set(model_set)
        rows = build_manifest_rows()
        validate_manifest_rows(rows)
        state = derive_collection_state(rows, now)
        with MODEL_SET.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(model_set, indent=2, sort_keys=True) + "\n")
        with MANIFEST.open("xb") as handle:
            handle.write(csv_bytes(rows))
        with STATE.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(state, indent=2, sort_keys=True) + "\n")
        record = build_record(now, state)
        with OUTPUT_JSON.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(record, indent=2, sort_keys=True) + "\n")
        with OUTPUT_MARKDOWN.open("x", encoding="utf-8") as handle:
            handle.write(markdown(record))
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: wrote v2.7 model set, manifest, collection state, freeze JSON and Markdown")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
