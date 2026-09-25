# AI Hallucination Attack Surface Study

Repository scaffold for the undergraduate cybersecurity research project:

**AI Hallucination Attack Surface: A Risk Assessment of Fake APIs and Libraries in AI-Generated Code**

Current implementation scope is limited to **Node.js and npm** as research targets, while **Python** is the primary orchestration language for automation scripts and data processing.

## Status

- Candidate pre-collection redesign documented for four fixed open-weight API model conditions.
- Candidate dependency-intensive task set `final-2.0.0` created for review; it is not rendered or manifested.
- API preflight and single-run collection scaffolding implemented but no official API request has been sent.
- Historical v1 web/CLI collection infrastructure and pilot artifacts are retained for provenance.
- No risk scoring implementation.
- No dependency/package installation performed.

## Directory Layout and Purpose

- `AGENTS.md`: Repository-level operating and integrity instructions.
- `README.md`: Project overview and usage conventions.
- `prompts/`: Standardized prompt assets used to drive experiments.
  - `tasks/final_2.0.0.jsonl`: Candidate v2 dependency-intensive task definitions; not yet rendered or frozen.
  - `prompt_template_v1.0.0.md`: Frozen canonical prompt template.
  - `prompts_v1.0.0.csv`: Frozen tabular prompt definitions for scripted runs.
  - `prompts_v1.0.0.json`: Frozen JSON prompt definitions for scripted runs.
  - `prompt_template.md`, `prompts_v0.1.csv`, and `prompts_v0.1.json`: Historical v0.1 records.
- `data/`: Research datasets and artifacts.
  - `fixtures/`: Synthetic test fixtures and non-experimental examples for parser/validator tests.
  - `pilot/`: Pilot-phase experimental data (strictly separate from final dataset).
    - `raw/`: Append-only raw model responses.
    - `extracted/`: Dependency extraction outputs derived from pilot raw data.
    - `validated/`: Registry validation outputs derived from pilot extracted data.
  - `final/`: Final-phase experimental data (strictly separate from pilot data).
    - `raw/`: Append-only raw model responses.
    - `extracted/`: Dependency extraction outputs derived from final raw data.
    - `validated/`: Registry validation outputs derived from final extracted data.
  - `processed/`: Cleaned/aggregated intermediate artifacts for analysis.
  - `manual_review/`: Human review notes/labels requiring adjudication.
- `src/`: Python orchestration and pipeline code.
  - `extraction/`: Dependency extraction logic.
  - `validation/`: npm registry validation logic (read-only API queries).
  - `classification/`: Hallucination classification logic.
  - `pipeline/`: End-to-end orchestration scripts/workflows.
- `tests/`: Automated tests for Python scripts and data-handling logic.
- `schemas/`: JSON/CSV schema definitions and validation contracts.
- `results/`: Generated analysis outputs (non-raw), summaries, and reports.
- `logs/`: Run logs and execution traces.
- `docs/`: Study documentation.
  - `decision_log.md`: Methodology and implementation decisions.
  - `experiment_protocol.md`: Protocol specification and run procedure.
  - `mentor_progress.md`: Supervisor update notes and milestone tracking.

## Data Separation Rules

- Keep `data/fixtures`, `data/pilot`, and `data/final` strictly separated.
- Never mix pilot records into final datasets.
- Treat `data/*/raw` as append-only once data collection begins.

## Safety and Execution Guardrails

- Never store experimental generated code in executable source locations such as `src/` or `tests/`.
- Store raw model outputs only under `data/pilot/raw/` or `data/final/raw/`.
- If generated code snippets must be retained for analysis, store as inert text artifacts under `data/...` and do not execute them.
- Keep local secrets in `.env` only; never commit secrets.

## Next Implementation Steps (Planned)

1. Add schemas for raw, extracted, and validated artifacts.
2. Implement Python extraction pipeline scripts.
3. Implement read-only npm registry validation scripts.
4. Add classification logic and tests.

## Data Collection

See [docs/api_model_protocol.md](docs/api_model_protocol.md) and [docs/generation_guide.md](docs/generation_guide.md) before any collection. The commands below are historical v1 tooling and must not be used to generate the official v2 dataset.

```text
python scripts/render_generation_prompts.py
python scripts/init_collection_run.py <RUN_ID>
python scripts/finalize_collection_run.py <RUN_ID>
python scripts/verify_collection.py --phase pilot
```

Codex pilot rows can be collected reproducibly after preparing a clean, external authenticated `CODEX_HOME`:

```text
python scripts/collect_codex_runs.py --phase pilot --run-id <PILOT_CODEX_RUN_ID> --limit 1 --codex-home /absolute/path/to/clean-codex-home
```

The historical runner rejects baseline rows, uses a fresh read-only external workspace, sends exact verified prompt bytes through stdin, and preserves `response.md`, JSONL `transcript.txt`, `stderr.txt`, metadata, and SHA-256 hashes. It never installs dependencies or executes generated code.

The v2 model set, task set, prompt template, rendered prompts, and 360-row manifest were frozen on 2026-09-16. `scripts/preflight_api_models.py` performs only read-only availability inspection; `scripts/collect_api_run.py` is the one-row collector and `scripts/collect_api_batch.py` is its sequential, resumable driver. Excluded smoke observations made after the freeze now establish infrastructure readiness for all four conditions following the documented Groq transport correction. No official manifest row has been collected, and official collection remains a separate deliberate action. None of these scripts installs dependencies or executes generated responses.
