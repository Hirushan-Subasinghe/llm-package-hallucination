# Baseline Manifest and Evidence Capture

This infrastructure does not contact an AI provider. It enumerates the frozen
baseline, preserves already-obtained response bytes, records technical failures,
and reports progress.

## Baseline design and paths

`data/manifests/baseline_v1.0.0.jsonl` contains the deterministic Cartesian
product of 30 final tasks, four workflows, and runs 1–3. Its 360 records remain
`PENDING`; the presence of validated, immutable completion metadata represents
`COMPLETED` so collection does not rewrite the canonical manifest.

Generation IDs have the form `<workflow-slug>-<task-id>-R<run>`, for example
`chatgpt-web-AUTH-001-R1`. Successful evidence is stored at:

```text
data/raw/<workflow-slug>/baseline/<task-id>/R<run>.txt
data/metadata/baseline/<workflow-slug>/<task-id>/R<run>.json
```

The `.txt` extension describes the expected response but capture is byte-based:
the utility performs no decoding, newline conversion, cleanup, parsing, fence
removal, or whitespace normalization. Both raw and metadata files are created
exclusively and cannot be overwritten by the utility.

Build or verify the manifest and inspect progress with:

```sh
PYTHONPATH=src python scripts/build_baseline_manifest.py
PYTHONPATH=src python scripts/inspect_baseline_progress.py
```

An identical existing manifest is reported as unchanged. A different existing
manifest is never overwritten.

## Controlled capture procedure

For ChatGPT Web and Gemini Web:

1. Locate the pending `generation_id` in the manifest.
2. Start a new chat/session and avoid memory, project context, and custom
   instructions where the interface permits.
3. Submit the exact frozen canonical prompt for the manifest task without
   alteration, and verify it against the recorded prompt version and SHA-256.
4. Obtain one response. Do not improve, clean, or repair it.
5. Save/copy the complete response into a temporary local file without editing.
6. Record the actual generation timestamp, including timezone.
7. Run the capture command below. Supply a visible model/version only when it is
   genuinely displayed by the interface.
8. Do not reuse response text or conversational context for another repetition.

For Codex CLI and Antigravity CLI — Gemini, follow the same identity, prompt,
and capture steps, but perform each invocation in a new isolated temporary
working directory. Do not expose this repository, `AGENTS.md`, earlier output,
or unrelated context. Disable package installation and generated-code execution.
Capture the returned textual response and pass it to the same local utility.
The utility does not itself establish provider isolation or invoke either CLI.

```sh
PYTHONPATH=src python scripts/capture_generation.py \
  chatgpt-web-AUTH-001-R1 /temporary/path/response.txt \
  --generation-timestamp 2026-09-08T10:30:00+05:30 \
  --visible-model-version 'only-if-visible'
```

Omit `--visible-model-version` when unavailable; it is stored as `null` and is
never inferred. Use one of `--installation-command-generated` or
`--no-installation-command-generated` only when that observation was actually
made; otherwise the field remains `null`. A generation becomes `COMPLETED` only
after raw bytes have been exclusively written, hashed, verified from disk, and
its completion metadata has been created.

Web and provider-side state cannot always be perfectly disabled or independently
verified. Record known limitations operationally rather than claiming stronger
isolation than the interface provides.

## Technical failures and retries

Technical failures are separate immutable files at
`data/failed/baseline/<attempt-id>.json`. The operator supplies a globally unique,
path-safe attempt ID and an observed timestamp. A retry uses a new attempt ID;
it does not erase a failure and does not become another successful run.

```sh
PYTHONPATH=src python scripts/record_failure.py \
  chatgpt-web-AUTH-001-R1 attempt-chatgpt-web-AUTH-001-R1-01 \
  --attempt-timestamp 2026-09-08T10:30:00+05:30 \
  --failure-category provider-timeout \
  --failure-summary-redacted 'Timed out before a usable response'
```

Only technical failures such as network/service errors, provider timeouts,
authentication failures, or browser/CLI failures preventing a usable response
belong here. Poor or incomplete model content is not a technical failure unless
the frozen protocol defines it as one. Error summaries must be redacted before
capture and must never contain credentials or secret-bearing raw errors.
