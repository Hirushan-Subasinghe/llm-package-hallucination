#!/usr/bin/env python3
"""Inspect baseline completion counts without modifying research records."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from experiment.evidence_capture import progress  # noqa: E402


if __name__ == "__main__":
    counts = progress(
        ROOT / "data/manifests/baseline_v1.0.0.jsonl",
        ROOT / "data/metadata/baseline",
    )
    print(" ".join(f"{key}={value}" for key, value in counts.items()))
