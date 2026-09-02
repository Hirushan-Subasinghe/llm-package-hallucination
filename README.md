# LLM Package Hallucination Experiment

This repository contains infrastructure for a reproducible academic experiment investigating third-party npm package hallucination in AI-generated Node.js code. It contains experimental tooling, not research conclusions.

The planned high-level pipeline is: task definitions, deterministic prompt rendering, isolated provider execution, and append-only preservation of raw responses and metadata.

> **Safety:** AI-generated code is research evidence. Do not execute it or install dependencies named within it.

**Development status:** Environment setup.

## Documentation

- [Full system documentation](docs/system_documentation.md)
- [Prompt generation protocol](docs/prompt_generation_protocol.md)

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
