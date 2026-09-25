"""Hard guard: prevent live data collection from ever running in this repository.

This repository is a derived-analysis workspace only. Official experimental
data collection is performed exclusively in ~/Dev/ai-hallucination-study.

Every live-collection entry point's CLI ``main()`` must call
``assert_live_collection_allowed()`` as its first action, before argument
parsing, config loading, network calls, provider calls, raw-run directory
creation, or batch-state mutation. Identity is determined by the presence of
the ``.analysis-repository-marker`` sentinel file at the repository root
(resolved from this file's own location, not from the process's current
working directory), so the guard still works regardless of how or from where
the script is invoked.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_REPOSITORY_MARKER = ROOT / ".analysis-repository-marker"

REFUSAL_MESSAGE = (
    "Live data collection is disabled in the analysis repository. "
    "Use ~/Dev/ai-hallucination-study."
)


class LiveCollectionDisabled(ValueError):
    """Raised when a live-collection entry point is invoked in the analysis repository."""


def assert_live_collection_allowed() -> None:
    if ANALYSIS_REPOSITORY_MARKER.is_file():
        raise LiveCollectionDisabled(REFUSAL_MESSAGE)
