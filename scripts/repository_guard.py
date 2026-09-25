"""Hard guard: final v2.7 data collection is complete, so no new responses may be collected.

This worktree (``~/Dev/ai-hallucination-final``, branch ``integration/v2.7-final``)
is the canonical location for the final v2.7 evidence, analysis, report
drafting and dissertation work.  Final data collection is complete (270/270
assigned rows) and frozen.  Read-only evidence inspection, verification and
analysis are allowed; generating or recording new experimental responses is not.

Every collection entry point's CLI ``main()`` calls
``assert_live_collection_allowed()`` before any network call, provider call,
raw-run directory creation, manual-capture write, or batch-state mutation.
Entry points with an explicit read-only mode (for example ``--list`` or
``--dry-run``) may run that mode without the guard.  Identity is determined by
the presence of the ``.analysis-repository-marker`` sentinel file at the
repository root (resolved from this file's own location, not from the
process's current working directory).  The file keeps its historical name so
that existing references stay valid.

There is no command-line or environment override.  Historical tooling tests
exercise collection functions directly with temporary roots, or patch
``ANALYSIS_REPOSITORY_MARKER`` in-process; ordinary execution cannot bypass
the guard.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_REPOSITORY_MARKER = ROOT / ".analysis-repository-marker"

REFUSAL_MESSAGE = (
    "Live data collection is disabled: final v2.7 data collection is complete and frozen. "
    "No new experimental responses may be collected."
)


class LiveCollectionDisabled(ValueError):
    """Raised when a collection entry point would generate or record a new response."""


def assert_live_collection_allowed() -> None:
    if ANALYSIS_REPOSITORY_MARKER.is_file():
        raise LiveCollectionDisabled(REFUSAL_MESSAGE)
