#!/usr/bin/env python3
"""Store one already-obtained baseline response without invoking a provider."""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from experiment.evidence_capture import capture_generation  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("generation_id")
    parser.add_argument("input_file", type=Path)
    parser.add_argument("--generation-timestamp", required=True, help="Observed ISO 8601 timestamp with timezone")
    parser.add_argument("--visible-model-version")
    installation = parser.add_mutually_exclusive_group()
    installation.add_argument("--installation-command-generated", action="store_true", dest="installation", default=None)
    installation.add_argument("--no-installation-command-generated", action="store_false", dest="installation")
    parser.set_defaults(installation=None)
    args = parser.parse_args()
    metadata = capture_generation(
        ROOT / "data/manifests/baseline_v1.0.0.jsonl",
        ROOT / "data/raw",
        args.generation_id,
        args.input_file,
        args.generation_timestamp,
        visible_model_version=args.visible_model_version,
        installation_command_generated=args.installation,
    )
    print(f'captured {metadata["generation_id"]}: {metadata["raw_output_path"]}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
