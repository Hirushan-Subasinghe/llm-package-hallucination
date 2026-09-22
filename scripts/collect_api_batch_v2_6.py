#!/usr/bin/env python3
"""Sequential v2.6 collector; dry-run never sends a request or changes state."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from collect_api_batch import ordered_rows, run_batch
from collect_api_run import DEFAULT_RAW_ROOT, load_config

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "manifests/api_final_v2.6.0_manifest.csv"
DEFAULT_CONFIG = ROOT / "config/api_model_set_1.4.0.json"
DEFAULT_STATE = ROOT / "data/final/api_batch_state_v2.6.0.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Sequential prospective v2.6 API batch collector")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--raw-root", type=Path, default=DEFAULT_RAW_ROOT)
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        if args.limit < 1:
            raise ValueError("--limit must be at least 1")
        result = run_batch(
            load_config(args.config), ordered_rows(args.manifest),
            manifest_hash=hashlib.sha256(args.manifest.read_bytes()).hexdigest(),
            state_path=args.state, raw_root=args.raw_root,
            limit=args.limit, dry_run=args.dry_run, continue_after_failed=True,
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
