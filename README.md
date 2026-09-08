# LLM Package Hallucination Experiment

This repository contains infrastructure for a reproducible academic experiment investigating third-party npm package hallucination in AI-generated Node.js code. It contains experimental tooling, not research conclusions.

The frozen baseline uses 30 Node.js/npm tasks across ChatGPT Web, Gemini Web,
Codex CLI, and Antigravity CLI — Gemini, with three successful independent runs
per task/workflow condition (360 successful baseline outputs). The high-level
pipeline is task definitions, deterministic prompt rendering, isolated or
fresh-session workflow execution, and append-only preservation of raw responses
and metadata.

> **Safety:** AI-generated code is research evidence. Do not execute it or install dependencies named within it.

**Development status:** Environment setup.

## Documentation

- [Full system documentation](docs/system_documentation.md)
- [Frozen experimental protocol](docs/experimental_protocol.md)
- [Prompt generation protocol](docs/prompt_generation_protocol.md)
- [Baseline manifest and evidence capture](docs/baseline_capture.md)

## Development setup

This project uses a `src/` package layout. Create and activate a virtual
environment, then install the project in editable mode before running tests or
development commands:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
```

Render the canonical pilot prompts with:

```sh
python scripts/render_prompts.py
```

Render the frozen final prompts with:

```sh
python scripts/render_prompts.py --task-set final
```

Rendering creates canonical prompt artifacts only; it does not invoke an AI
workflow or generate research data.

Build the deterministic 360-cell baseline manifest with:

```sh
PYTHONPATH=src python scripts/build_baseline_manifest.py
```

Raw response capture and technical-failure recording are local, append-only
operations documented in `docs/baseline_capture.md`; they do not automate or
contact any provider.
