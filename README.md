# AI Hallucination Attack Surface Study

Repository scaffold for the undergraduate cybersecurity research project:

**AI Hallucination Attack Surface: A Risk Assessment of Fake APIs and Libraries in AI-Generated Code**

Current implementation scope is limited to **Node.js and npm** as research targets, while **Python** is the primary orchestration language for automation scripts and data processing.

## Status

- Scaffolding only.
- No model API integrations implemented.
- No risk scoring implementation.
- No dependency/package installation performed.

## Directory Layout and Purpose

- `AGENTS.md`: Repository-level operating and integrity instructions.
- `README.md`: Project overview and usage conventions.
- `prompts/`: Standardized prompt assets used to drive experiments.
  - `prompt_template.md`: Canonical prompt template.
  - `prompts_v0.1.csv`: Tabular prompt definitions for scripted runs.
  - `prompts_v0.1.json`: JSON prompt definitions for scripted runs.
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
