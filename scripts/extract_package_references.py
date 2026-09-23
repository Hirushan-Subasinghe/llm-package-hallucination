#!/usr/bin/env python3
"""Extract explicit direct npm package references from a response inventory.

This derived-analysis stage reads inventory and immutable response artifacts only.
It performs no registry queries, package installation, model calls, or code execution.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shlex
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Any, Iterable, Optional

ROOT = Path(__file__).resolve().parents[1]
EXTRACTOR_VERSION = "pipe-03-package-reference-extractor-1.0.2"
DEFAULT_INVENTORY = ROOT / "results" / "response_inventory_v2.2.0.json"
DEFAULT_RAW_ROOT = ROOT / "data" / "final" / "raw"
DEFAULT_OCCURRENCES_JSON = ROOT / "results" / "package_reference_occurrences_v2.2.0.json"
DEFAULT_OCCURRENCES_CSV = ROOT / "results" / "package_reference_occurrences_v2.2.0.csv"
DEFAULT_UNIQUE_JSON = ROOT / "results" / "package_reference_unique_v2.2.0.json"
DEFAULT_UNIQUE_CSV = ROOT / "results" / "package_reference_unique_v2.2.0.csv"

SOURCE_TYPE_ORDER = {"es_import": 0, "require": 1, "dynamic_import": 2, "npm_install": 3, "package_json": 4}
BUILTIN_MODULES = frozenset({
    "assert", "assert/strict", "async_hooks", "buffer", "child_process", "cluster",
    "console", "constants", "crypto", "dgram", "diagnostics_channel", "dns",
    "dns/promises", "domain", "events", "fs", "fs/promises", "http", "http2",
    "https", "inspector", "inspector/promises", "module", "net", "os", "path",
    "path/posix", "path/win32", "perf_hooks", "process", "punycode", "querystring",
    "readline", "readline/promises", "repl", "sea", "sqlite", "stream",
    "stream/consumers", "stream/promises", "stream/web", "string_decoder", "sys",
    "test", "timers", "timers/promises", "tls", "trace_events", "tty", "url",
    "util", "util/types", "v8", "vm", "wasi", "worker_threads", "zlib",
})

ES_IMPORT_START_RE = re.compile(r"(?m)^[ \t]*import(?:[ \t]+type)?[ \t]+(?!\()")
ES_IMPORT_FROM_RE = re.compile(r"\bfrom[ \t]*(?P<q>['\"])(?P<ref>[^'\"\r\n]+)(?P=q)")
ES_SIDE_EFFECT_IMPORT_RE = re.compile(r"(?P<q>['\"])(?P<ref>[^'\"\r\n]+)(?P=q)")
REQUIRE_RE = re.compile(r"\brequire\s*\(\s*(?P<q>['\"])(?P<ref>[^'\"\r\n]+)(?P=q)\s*\)")
DYNAMIC_IMPORT_RE = re.compile(r"\bimport\s*\(\s*(?P<q>['\"])(?P<ref>[^'\"\r\n]+)(?P=q)\s*\)")
NPM_INSTALL_RE = re.compile(r"(?m)^[ \t]*(?:\$\s*)?npm\s+(?:install|i)\b(?P<args>[^\r\n]*)")
SHELL_CONTROL_OPERATOR_RE = re.compile(r"&&|\|\||;|\|")
DEPENDENCY_OBJECT_RE = re.compile(r'"(?:dependencies|devDependencies|peerDependencies|optionalDependencies)"\s*:\s*\{')

OCCURRENCE_COLUMNS = [
    "run_id", "collection_order", "model_condition_id", "task_id", "category",
    "collection_status", "completion_status", "truncated", "response_artifact_path",
    "occurrence_index", "original_reference", "normalized_package", "source_type",
    "source_text", "source_offset", "version_specifier", "extractor_version",
]
UNIQUE_COLUMNS = [
    "run_id", "collection_order", "model_condition_id", "task_id", "category",
    "normalized_package", "first_occurrence_index", "occurrence_count", "source_types",
    "extractor_version",
]


def normalize_package_reference(reference: str) -> Optional[tuple[str, Optional[str]]]:
    """Return npm package root and explicit version, or None for excluded/invalid input."""
    value = reference.strip()
    if not value or value.startswith(("./", "../", "/", "~/", "file:", "http:", "https:")):
        return None
    if value.startswith("node:"):
        return None
    if value.startswith("@"):
        match = re.match(r"^(@[^/@\s]+/[^/@\s]+)(.*)$", value)
        if not match:
            return None
        root, suffix = match.groups()
    else:
        match = re.match(r"^([^/@\s]+)(.*)$", value)
        if not match:
            return None
        root, suffix = match.groups()
    if root in BUILTIN_MODULES or root.startswith("."):
        return None
    version: Optional[str] = None
    if suffix.startswith("@"):
        version = suffix[1:] or None
    elif suffix and not suffix.startswith("/"):
        return None
    if version and version.startswith("npm:"):
        return None  # npm aliases need a separate, explicit policy.
    return root, version


def line_text(text: str, offset: int) -> str:
    """Return the complete source line containing offset for auditable evidence."""
    start = text.rfind("\n", 0, offset) + 1
    end = text.find("\n", offset)
    return text[start:] if end == -1 else text[start:end]


def extract_es_import_candidates(text: str) -> list[dict[str, Any]]:
    """Extract literal static ESM imports, including multiline declarations.

    A declaration starts only where ``import`` begins a source line. Multiline
    scanning stops at the literal ``from`` clause, another import declaration,
    or a Markdown code-fence boundary. This keeps extraction syntax-driven and
    prevents an incomplete import from consuming later response prose or code.
    """
    candidates: list[dict[str, Any]] = []
    for start_match in ES_IMPORT_START_RE.finditer(text):
        statement_start = start_match.start()
        line_start = statement_start
        first_line = True
        brace_depth = 0
        while line_start < len(text):
            line_end = text.find("\n", line_start)
            if line_end == -1:
                line_end = len(text)
            line = text[line_start:line_end]

            if not first_line and re.match(r"[ \t]*(?:import\b|```)", line):
                break

            search_start = start_match.end() - line_start if first_line else 0
            searchable = line[search_start:]
            # An import-list comment is not a module clause. For named imports,
            # only text after the closing brace can contain the literal `from`.
            code = searchable.split("//", 1)[0]
            brace_depth += code.count("{") - code.count("}")
            clause = code.rsplit("}", 1)[-1] if "}" in code else code
            reference_match = ES_IMPORT_FROM_RE.search(clause) if brace_depth <= 0 else None
            if reference_match is None and first_line:
                reference_match = ES_SIDE_EFFECT_IMPORT_RE.match(searchable)
            if reference_match is not None:
                candidates.append({
                    "offset": statement_start,
                    "source_type": "es_import",
                    "reference": reference_match.group("ref"),
                    "version": None,
                    "source_text": text[statement_start:line_end],
                })
                break

            if ";" in code:
                break
            first_line = False
            line_start = line_end + 1

    return candidates


def matching_brace(text: str, opening_offset: int) -> Optional[int]:
    """Find a JSON-object closing brace, respecting quoted strings."""
    depth, quote, escaped = 0, None, False
    for index in range(opening_offset, len(text)):
        char = text[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
        elif char in {'"', "'"}:
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
    return None


def extract_candidates(text: str) -> list[dict[str, Any]]:
    """Extract syntactically explicit candidate references in source-offset order."""
    candidates: list[dict[str, Any]] = []

    def add_literal_matches(pattern: re.Pattern[str], source_type: str) -> None:
        for match in pattern.finditer(text):
            candidates.append({"offset": match.start(), "source_type": source_type,
                               "reference": match.group("ref"), "version": None,
                               "source_text": line_text(text, match.start())})

    candidates.extend(extract_es_import_candidates(text))
    add_literal_matches(REQUIRE_RE, "require")
    add_literal_matches(DYNAMIC_IMPORT_RE, "dynamic_import")

    for match in NPM_INSTALL_RE.finditer(text):
        # Stop package-operand parsing at a shell control operator so a chained
        # command (e.g. "npm install && npm run build") never contributes the
        # operator or the next command's words as fabricated package names.
        args = match.group("args")
        operator_match = SHELL_CONTROL_OPERATOR_RE.search(args)
        if operator_match is not None:
            args = args[:operator_match.start()]
        try:
            tokens = shlex.split(args, comments=True)
        except ValueError:
            continue
        for token in tokens:
            if token.startswith("-"):
                continue
            candidates.append({"offset": match.start("args") + args.find(token),
                               "source_type": "npm_install", "reference": token, "version": None,
                               "source_text": line_text(text, match.start())})

    for match in DEPENDENCY_OBJECT_RE.finditer(text):
        opening = text.find("{", match.start(), match.end())
        closing = matching_brace(text, opening)
        if closing is None:
            continue
        try:
            dependency_object = json.loads(text[opening:closing + 1])
        except json.JSONDecodeError:
            continue
        if not isinstance(dependency_object, dict):
            continue
        for key, value in dependency_object.items():
            if isinstance(key, str) and isinstance(value, str):
                key_offset = text.find(json.dumps(key), opening, closing + 1)
                candidates.append({"offset": key_offset, "source_type": "package_json",
                                   "reference": key, "version": value,
                                   "source_text": line_text(text, key_offset)})

    return sorted(candidates, key=lambda item: (item["offset"], SOURCE_TYPE_ORDER[item["source_type"]], item["reference"]))


def extract_response_occurrences(text: str, inventory_row: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize eligible candidates and attach inventory provenance."""
    records: list[dict[str, Any]] = []
    for candidate in extract_candidates(text):
        normalized = normalize_package_reference(candidate["reference"])
        if normalized is None:
            continue
        package, embedded_version = normalized
        records.append({
            "run_id": inventory_row["run_id"],
            "collection_order": int(inventory_row["collection_order"]),
            "model_condition_id": inventory_row["model_condition_id"],
            "task_id": inventory_row["task_id"],
            "category": inventory_row["category"],
            "collection_status": inventory_row["collection_status"],
            "completion_status": inventory_row.get("completion_status"),
            "truncated": inventory_row.get("truncated"),
            "response_artifact_path": inventory_row["response_artifact_path"],
            "occurrence_index": 0,
            "original_reference": candidate["reference"],
            "normalized_package": package,
            "source_type": candidate["source_type"],
            "source_text": candidate["source_text"],
            "source_offset": candidate["offset"],
            "version_specifier": candidate["version"] if candidate["version"] is not None else embedded_version,
            "extractor_version": EXTRACTOR_VERSION,
        })
    for index, record in enumerate(records, start=1):
        record["occurrence_index"] = index
    return records


def resolve_response_path(row: dict[str, Any], raw_root: Path, root: Path) -> Optional[Path]:
    artifact = row.get("response_artifact_path")
    if not artifact:
        return None
    path = Path(str(artifact))
    if not path.is_absolute():
        candidate = root / path
        path = candidate if candidate.is_file() else raw_root / row["run_id"] / path.name
    return path if path.is_file() else None


def build_occurrences(inventory: Iterable[dict[str, Any]], raw_root: Path, root: Path = ROOT) -> list[dict[str, Any]]:
    """Read valid completed/truncated response artifacts; safely skip all other rows."""
    output: list[dict[str, Any]] = []
    for row in sorted(inventory, key=lambda item: int(item["collection_order"])):
        if row.get("collection_status") not in {"completed", "truncated"}:
            continue
        response_path = resolve_response_path(row, raw_root, root)
        if response_path is None:
            continue
        output.extend(extract_response_occurrences(response_path.read_text(encoding="utf-8"), row))
    return output


def build_unique_view(occurrences: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deduplicate only by (run_id, normalized_package), retaining occurrence data separately."""
    grouped: OrderedDict[tuple[str, str], dict[str, Any]] = OrderedDict()
    for occurrence in occurrences:
        key = (occurrence["run_id"], occurrence["normalized_package"])
        if key not in grouped:
            grouped[key] = {"run_id": occurrence["run_id"], "collection_order": occurrence["collection_order"],
                            "model_condition_id": occurrence["model_condition_id"], "task_id": occurrence["task_id"],
                            "category": occurrence["category"], "normalized_package": occurrence["normalized_package"],
                            "first_occurrence_index": occurrence["occurrence_index"], "occurrence_count": 0,
                            "source_types": [], "extractor_version": EXTRACTOR_VERSION}
        record = grouped[key]
        record["occurrence_count"] += 1
        if occurrence["source_type"] not in record["source_types"]:
            record["source_types"].append(occurrence["source_type"])
    for record in grouped.values():
        record["source_types"].sort(key=SOURCE_TYPE_ORDER.__getitem__)
    return list(grouped.values())


def write_json(records: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")


def write_csv(records: list[dict[str, Any]], columns: list[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for record in records:
            writer.writerow({column: ";".join(record[column]) if column == "source_types" else ("" if record.get(column) is None else record.get(column)) for column in columns})


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract explicit npm package references from a response inventory")
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--raw-root", type=Path, default=DEFAULT_RAW_ROOT)
    parser.add_argument("--occurrences-json", type=Path, default=DEFAULT_OCCURRENCES_JSON)
    parser.add_argument("--occurrences-csv", type=Path, default=DEFAULT_OCCURRENCES_CSV)
    parser.add_argument("--unique-json", type=Path, default=DEFAULT_UNIQUE_JSON)
    parser.add_argument("--unique-csv", type=Path, default=DEFAULT_UNIQUE_CSV)
    args = parser.parse_args()
    try:
        inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
        if not isinstance(inventory, list):
            raise ValueError("Inventory JSON must contain a list of rows")
        occurrences = build_occurrences(inventory, args.raw_root)
        unique = build_unique_view(occurrences)
        write_json(occurrences, args.occurrences_json)
        write_csv(occurrences, OCCURRENCE_COLUMNS, args.occurrences_csv)
        write_json(unique, args.unique_json)
        write_csv(unique, UNIQUE_COLUMNS, args.unique_csv)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"Extracted occurrence records: {len(occurrences)}")
    print(f"Extracted unique package records: {len(unique)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
