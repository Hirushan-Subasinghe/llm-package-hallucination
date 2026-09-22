#!/usr/bin/env python3
"""PIPE-04: read-only npm registry evidence for PIPE-03 package roots.

This stage records registry responses, never research classifications. No request is
made unless the CLI is invoked with --live. It uses only the Python standard library.
"""

import argparse
import csv
import hashlib
import io
import json
import os
import socket
import ssl
import tempfile
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import HTTPRedirectHandler, Request, build_opener

VERSION = "pipe-04-npm-validator-1.0.0"
FORMAT_VERSION = "pipe-04-evidence-1.0.0"
REGISTRY = "https://registry.npmjs.org"
MAX_RETRIES = 2  # Three attempts total, only for operational failures.
BACKOFF_SECONDS = (0.5, 1.0)
MAX_RETRY_AFTER_SECONDS = 5.0
REQUEST_INTERVAL_SECONDS = 0.25
TIMEOUT_SECONDS = 10.0
MAX_METADATA_BYTES = 32 * 1024 * 1024
PACKAGE_FIELDS = (
    "normalized_package", "validation_status", "registry", "request_url",
    "http_status", "checked_at", "validator_version", "evidence_summary",
    "error_type", "retry_count", "source_input_hash",
    "source_occurrences_hash", "history",
)
JOIN_FIELDS = (
    "run_id", "collection_order", "model_condition_id", "task_id", "category",
    "normalized_package", "first_occurrence_index", "occurrence_count",
    "source_types", "extractor_version", "collection_status",
    "completion_status", "truncated", "response_artifact_path",
    "validation_status", "registry", "request_url", "http_status",
    "checked_at", "validator_version", "evidence_summary", "error_type",
    "retry_count", "source_input_hash", "source_occurrences_hash",
)


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def request_url(package):
    # Encoding the whole name is essential for @scope/package.
    return f"{REGISTRY}/{quote(package, safe='')}"


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def registry_transport(url, timeout=TIMEOUT_SECONDS):
    """Return (HTTP status, response bytes, headers) without following redirects."""
    request = Request(url, headers={"Accept": "application/vnd.npm.install-v1+json", "User-Agent": VERSION}, method="GET")
    opener = build_opener(NoRedirects)
    try:
        with opener.open(request, timeout=timeout) as response:
            return response.status, response.read(MAX_METADATA_BYTES + 1), dict(response.headers)
    except HTTPError as error:
        return error.code, error.read(MAX_METADATA_BYTES + 1), dict(error.headers)


def retry_delay(headers, retry_index, now=None):
    """Return bounded delay, or None when Retry-After exceeds the safe retry window."""
    value = next((v for k, v in headers.items() if k.lower() == "retry-after"), None)
    if value is None:
        return BACKOFF_SECONDS[retry_index]
    try:
        seconds = float(value)
    except ValueError:
        try:
            target = parsedate_to_datetime(value)
            current = now or datetime.now(timezone.utc)
            seconds = (target - current).total_seconds()
        except (TypeError, ValueError, OverflowError):
            return None
    seconds = max(0.0, seconds)
    return seconds if seconds <= MAX_RETRY_AFTER_SECONDS else None


def interpret_response(package, status, body):
    """Map only authoritative, structurally expected responses to resolved states."""
    if len(body) > MAX_METADATA_BYTES:
        return "unresolved", "Registry response exceeded metadata size limit", "oversized_response"
    try:
        document = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        document = None
    if status == 200:
        if isinstance(document, dict) and document.get("name") == package:
            return "exists", "Registry metadata returned the exact package name", None
        return "unresolved", "HTTP 200 metadata missing or mismatching package name", "malformed_metadata"
    if status == 404:
        if isinstance(document, dict) and str(document.get("error", "")).strip().lower() in {"not found", "not_found"}:
            return "not_found", "Official registry returned package-not-found JSON", None
        return "unresolved", "HTTP 404 did not contain expected package-not-found JSON", "unexpected_404"
    if status == 429:
        return "unresolved", "Registry rate limit", "rate_limited"
    if 500 <= status <= 599:
        return "unresolved", f"Registry HTTP {status}", "server_error"
    return "unresolved", f"Unexpected registry HTTP {status}", "unexpected_http_status"


def validate_package(package, input_hash, occurrences_hash, transport=registry_transport,
                     sleep=time.sleep, clock=utc_now, previous=None):
    url = request_url(package)
    history = []
    if previous is not None:
        history = list(previous["history"])
        history.append({key: previous[key] for key in (
            "validation_status", "http_status", "checked_at", "evidence_summary",
            "error_type", "retry_count")})
    retry_count = 0
    for attempt in range(MAX_RETRIES + 1):
        headers = {}
        try:
            status, body, headers = transport(url, TIMEOUT_SECONDS)
            outcome, summary, error_type = interpret_response(package, status, body)
        except (URLError, TimeoutError, ConnectionError, socket.timeout, ssl.SSLError, OSError) as error:
            status = None
            outcome, summary = "unresolved", "Registry transport failed"
            error_type = type(error).__name__
        except Exception as error:  # An unexpected adapter failure is never absence evidence.
            status = None
            outcome, summary = "unresolved", "Unexpected registry transport failure"
            error_type = type(error).__name__
        transient = error_type in {"rate_limited", "server_error"} or status is None
        if outcome != "unresolved" or not transient or attempt == MAX_RETRIES:
            break
        delay = retry_delay(headers, attempt)
        if delay is None:
            summary = "Retry-After is invalid or exceeds the bounded retry window"
            error_type = "retry_after_out_of_bounds"
            break
        retry_count += 1
        sleep(delay)
    return {
        "normalized_package": package, "validation_status": outcome,
        "registry": REGISTRY, "request_url": url, "http_status": status,
        "checked_at": clock(), "validator_version": VERSION,
        "evidence_summary": summary, "error_type": error_type,
        "retry_count": retry_count, "source_input_hash": input_hash,
        "source_occurrences_hash": occurrences_hash, "history": history,
    }


def load_inputs(unique_path, occurrences_path):
    unique_bytes = Path(unique_path).read_bytes()
    occurrence_bytes = Path(occurrences_path).read_bytes()
    unique = json.loads(unique_bytes)
    occurrences = json.loads(occurrence_bytes)
    if not isinstance(unique, list) or not isinstance(occurrences, list):
        raise ValueError("PIPE-03 inputs must be JSON arrays")
    by_key = {}
    for occurrence in occurrences:
        key = (occurrence["run_id"], occurrence["normalized_package"])
        by_key.setdefault(key, []).append(occurrence)
    seen = set()
    for row in unique:
        key = (row["run_id"], row["normalized_package"])
        if key in seen or key not in by_key:
            raise ValueError(f"Duplicate or unmatched PIPE-03 unique key: {key}")
        seen.add(key)
        if len(by_key[key]) != row["occurrence_count"]:
            raise ValueError(f"PIPE-03 occurrence count mismatch: {key}")
        for field in ("collection_order", "model_condition_id", "task_id", "category"):
            if any(item[field] != row[field] for item in by_key[key]):
                raise ValueError(f"PIPE-03 metadata mismatch at {key}: {field}")
    if seen != set(by_key):
        raise ValueError("PIPE-03 occurrences contain keys absent from unique input")
    return unique, by_key, sha256_bytes(unique_bytes), sha256_bytes(occurrence_bytes)


def output_paths(output_dir):
    base = Path(output_dir)
    return {
        "package_json": base / "npm_package_validation_v2.2.0.json",
        "package_csv": base / "npm_package_validation_v2.2.0.csv",
        "joined_json": base / "npm_package_validation_joined_v2.2.0.json",
        "joined_csv": base / "npm_package_validation_joined_v2.2.0.csv",
    }


def load_cache(path, input_hash, occurrences_hash, packages):
    if not path.exists():
        return {}
    document = json.loads(path.read_text(encoding="utf-8"))
    if (document.get("format_version") != FORMAT_VERSION or
            document.get("source_input_hash") != input_hash or
            document.get("source_occurrences_hash") != occurrences_hash):
        raise ValueError("Existing PIPE-04 cache has a different format or source hash")
    records = document["records"]
    cache = {item["normalized_package"]: item for item in records}
    if len(cache) != len(records) or set(cache) != set(packages):
        raise ValueError("Existing PIPE-04 cache has duplicate or unexpected packages")
    if any(item["validator_version"] != VERSION or item["source_input_hash"] != input_hash or
           item["source_occurrences_hash"] != occurrences_hash for item in records):
        raise ValueError("Existing PIPE-04 cache record provenance differs")
    return cache


def build_outputs(unique, by_key, input_hash, occurrences_hash, cache,
                  transport=registry_transport, sleep=time.sleep, clock=utc_now,
                  retry_unresolved=False, request_interval=REQUEST_INTERVAL_SECONDS):
    packages = sorted({row["normalized_package"] for row in unique})
    records = []
    requested = 0
    for package in packages:
        previous = cache.get(package)
        if previous is not None and (previous["validation_status"] != "unresolved" or not retry_unresolved):
            record = previous
        else:
            if requested:
                sleep(request_interval)
            record = validate_package(package, input_hash, occurrences_hash,
                                      transport, sleep, clock, previous)
            requested += 1
        records.append(record)
    by_package = {item["normalized_package"]: item for item in records}
    joined = []
    for row in sorted(unique, key=lambda item: (item["collection_order"], item["first_occurrence_index"], item["normalized_package"])):
        key = (row["run_id"], row["normalized_package"])
        source = by_key[key][0]
        evidence = by_package[row["normalized_package"]]
        joined.append({
            **row,
            "collection_status": source["collection_status"],
            "completion_status": source["completion_status"],
            "truncated": source["truncated"],
            "response_artifact_path": source["response_artifact_path"],
            **{field: evidence[field] for field in (
                "validation_status", "registry", "request_url", "http_status",
                "checked_at", "validator_version", "evidence_summary", "error_type",
                "retry_count", "source_input_hash", "source_occurrences_hash")},
        })
    return records, joined, requested


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def csv_bytes(records, fields):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for record in records:
        writer.writerow({key: json.dumps(record[key], separators=(",", ":"))
                         if isinstance(record[key], (list, dict)) else record[key]
                         for key in fields})
    return stream.getvalue().encode("utf-8")


def write_outputs(paths, records, joined, input_hash, occurrences_hash):
    def envelope(items):
        return {"format_version": FORMAT_VERSION, "source_input_hash": input_hash,
                "source_occurrences_hash": occurrences_hash, "records": items}
    atomic_write(paths["package_json"], (json.dumps(envelope(records), indent=2, ensure_ascii=False) + "\n").encode())
    atomic_write(paths["package_csv"], csv_bytes(records, PACKAGE_FIELDS))
    atomic_write(paths["joined_json"], (json.dumps(envelope(joined), indent=2, ensure_ascii=False) + "\n").encode())
    atomic_write(paths["joined_csv"], csv_bytes(joined, JOIN_FIELDS))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="results/package_reference_unique_v2.2.0.json")
    parser.add_argument("--occurrences", default="results/package_reference_occurrences_v2.2.0.json")
    parser.add_argument("--output-dir", default="results")
    parser.add_argument("--live", action="store_true", help="Explicitly authorize read-only npm metadata requests")
    parser.add_argument("--retry-unresolved", action="store_true", help="Retry cached unresolved records, preserving prior evidence")
    args = parser.parse_args(argv)
    unique, by_key, input_hash, occurrences_hash = load_inputs(args.input, args.occurrences)
    paths = output_paths(args.output_dir)
    if not args.live:
        print(f"No network request made. {len(unique)} response-package rows; "
              f"{len({row['normalized_package'] for row in unique})} distinct package names.")
        print("Add --live after implementation review to perform validation.")
        return 0
    if not paths["package_json"].exists() and any(path.exists() for path in paths.values()):
        raise ValueError("Partial PIPE-04 output exists without package JSON cache; refusing overwrite")
    cache = load_cache(paths["package_json"], input_hash, occurrences_hash,
                       {row["normalized_package"] for row in unique})
    records, joined, requested = build_outputs(unique, by_key, input_hash,
                                                occurrences_hash, cache,
                                                retry_unresolved=args.retry_unresolved)
    write_outputs(paths, records, joined, input_hash, occurrences_hash)
    print(f"Saved {len(records)} package records and {len(joined)} joined rows; "
          f"queried {requested} distinct packages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
