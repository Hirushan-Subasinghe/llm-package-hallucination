# Data Collection Generation Guide

This guide describes how a data-collection operator captures the frozen AI-generated outputs for the study **AI Hallucination Attack Surface: A Risk Assessment of Fake APIs and Libraries in AI-Generated Code**. The operator collects and preserves evidence; the operator does not interpret dependencies or decide whether a package is hallucinated.

## Purpose

The collection procedure produces an auditable record for each controlled generation. The final baseline contains 30 tasks x 4 workflows x 3 generations = 360 outputs. A separate pilot contains 6 pre-specified tasks x 4 workflows x 1 generation = 24 outputs. Pilot records are never part of the final baseline.

## Workflows

The four workflows are `chatgpt_web`, `gemini_web`, `codex_cli`, and `antigravity_cli`. The same frozen v1.0.0 task prompt is used for every workflow and repetition.

The pilot tasks are fixed before execution: `AUTH-04`, `DB-03`, `FILE-02`, `API-04`, `SEC-03`, and `LOG-04`. Do not change this selection because of observed hallucinations.

## Operator Rules

- Use only the frozen files under `prompts/`.
- Use a fresh conversation, session, or isolated CLI workspace for every run.
- Submit exactly once and do not send follow-up prompts.
- Do not add wording, clarification, package names, warnings, or verification requests.
- Preserve the first complete response exactly as captured.
- Record metadata immediately after capture, including visible workflow and model information.
- Use `not_exposed` when a proprietary configuration or model version is not visible.
- Never execute generated code, install dependencies, or validate packages during generation.
- Never regenerate because an answer looks poor or contains no apparent hallucination.

The operator must copy the prompt produced by the prompt-rendering script and must not manually reconstruct the prompt. A prompt hash verifies that the recorded/rendered text matches the frozen prompt source. It does not cryptographically prove that a human pasted exactly that text into a proprietary web interface; the session procedure and metadata provide the operational evidence for submission.

## Run Procedure

1. Render or confirm the frozen prompts and manifests:

   ```text
   python scripts/render_generation_prompts.py
   ```

2. Select the assigned run ID from the appropriate manifest. Pilot IDs begin with `PILOT-`; final IDs begin with `BASE-`. Run IDs are deterministic and contain no timestamps, for example `PILOT-AUTH-04-chatgpt_web-R01` or `BASE-DB-03-gemini_web-R02`.

The manifests describe the pre-specified collection plan and are not modified as runs are collected. Actual progress is represented by each run's metadata and derived by `verify_collection.py`.

3. Initialize the run:

   ```text
   python scripts/init_collection_run.py <RUN_ID>
   ```

4. Verify the prompt hash:

   ```text
   python scripts/verify_prompt_hash.py --run-id <RUN_ID>
   ```

5. Copy the contents of that run's `prompt.txt` into the assigned workflow. Do not reconstruct it from the task description.

6. Capture the required response or transcript and preserve it in the initialized run directory.

7. Complete metadata using only information visibly exposed by the workflow. Do not guess model versions, temperature, seeds, or other hidden settings.

8. Finalize the run:

   ```text
   python scripts/finalize_collection_run.py <RUN_ID>
   ```

9. Inspect any failure report. Do not delete data or retry generation automatically. Escalate collection errors to the study researcher.

## Web Workflows

For ChatGPT Web and Gemini Web:

- Start a fresh chat/session for every run; do not continue a previous chat.
- Use the exact rendered prompt and submit once.
- Wait until the first response finishes; send no follow-up messages.
- Save the full response exactly as `response.md`.
- Record visible workflow and model information; record `not_exposed` when the exact model/version is not shown.
- Do not enable or invoke external tools, browsing, or search unless those capabilities are automatically inseparable from the selected workflow. Record that fact in metadata.
- Do not manually ask the workflow to browse npm or verify packages.

Fresh sessions operationally reduce carry-over context, but they do not imply statistical independence of proprietary model outputs.

## CLI Workflows

For Codex CLI and Antigravity CLI:

- Use the initialized run's isolated `artifacts/` directory as the workspace, or another isolated temporary workspace whose contents are copied into `artifacts/` without alteration.
- Capture the complete terminal or agent interaction as `transcript.txt`.
- Preserve every file created or modified by the coding workflow under `artifacts/`.
- If the workflow provides a final textual answer, preserve it as `response.md` as well.
- Record errors, tool interruptions, and CLI exit status.
- Prevent unsafe command execution wherever possible. If the workflow proposes or attempts to execute a command, stop it when possible and record the event.
- Never run generated programs, scripts, tests, or package-manager commands. Generated files are research data only.

The finalizer requires `metadata.json` and `transcript.txt` for CLI runs. `response.md` is optional for CLI runs.

## Raw and Generated-File Preservation

Web responses are stored as `data/<phase>/raw/<run_id>/response.md`. CLI transcripts are stored as `transcript.txt`, and generated files are stored under `artifacts/`. The finalizer records SHA-256 hashes without changing captured AI content. Raw data is append-only once collection begins.

## Metadata

Each run has `metadata.json` containing the run identity, phase, prompt ID and version, category, workflow, visible tool/provider/model values, workflow type, configuration values, UTC timestamp, exact prompt text and hash, raw capture path and hash, collection method, non-personal operator label, notes, and collection status. Collection-specific CLI fields include `transcript_path`, `artifact_directory`, and `cli_exit_status`.

Use the operator label `collector_01` unless the researcher assigns another non-personally-identifying label. Timestamps are ISO 8601 UTC. Do not store the collector's personal name.

## Error Handling

An unknown run ID, prompt-hash mismatch, missing required capture, missing metadata, or metadata identity mismatch is a collection error. The scripts report `FAIL`, preserve existing files, and mark the run incomplete or error where appropriate. They never call an AI API, install packages, execute generated code, or automatically retry a generation.

## Pilot Decision Rules

The pilot tests prompt rendering, prompt integrity, response capture, metadata collection, dependency-extraction compatibility, registry-validation pipeline compatibility, and classification-workflow compatibility. The appearance of hallucinated packages is observational and is not the formal pilot pass/fail criterion.

If the pilot contains zero confirmed hallucinations, do not modify prompts solely to produce hallucinations. Instead check:

1. Whether workflows produced analyzable implementations.
2. Whether external npm dependencies were recommended where applicable.
3. Whether the extractor identified dependency recommendations correctly.
4. Whether registry validation worked correctly.
5. Whether the dependencies were genuinely valid.

If the collection and analysis pipeline works correctly, a zero-hallucination pilot does not by itself invalidate the study. Any major methodology or prompt modification after pilot review requires a new version and documentation before final baseline collection.

## Prohibited Actions

Never:

- install unknown or hallucinated packages;
- execute generated code or run unknown scripts;
- run `npm install`, `npx`, or other package-manager installation commands using generated dependencies;
- publish, register, reserve, or claim package names;
- create packages to test namespace availability;
- attempt registration to test claimability;
- validate packages against npm during generation.

Later registry validation uses read-only queries only. Generated files are treated as research data, not trusted software.

## Completion Checklist

- [ ] Correct pilot or baseline run ID selected from the manifest.
- [ ] Fresh web session or isolated CLI workspace used.
- [ ] Prompt copied from `prompt.txt` generated by the rendering script.
- [ ] Prompt submitted once with no follow-up or operator-added wording.
- [ ] Full response or CLI transcript preserved exactly.
- [ ] CLI artifacts preserved, if applicable.
- [ ] Visible metadata recorded; unavailable values marked `not_exposed`.
- [ ] No generated code, script, package, or registry operation was executed.
- [ ] Finalizer reports `PASS` and run metadata records `collection_status: completed`.
- [ ] Any interruption or anomaly is recorded in metadata notes.