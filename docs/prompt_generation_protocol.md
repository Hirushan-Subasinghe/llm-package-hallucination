# Prompt Generation Protocol

## Separation of responsibilities

`prompts/templates/master_prompt_v1.0.0.md` contains the frozen full-study
experimental instructions. It has exactly one variable,
`{{TASK_DESCRIPTION}}`. The historical `v0.1.0` template and pilot artifacts are
preserved unchanged.

`prompts/tasks/final_1.0.0.jsonl` contains the 30 frozen functional tasks and
their metadata. `prompts/tasks/pilot_samples.jsonl` contains six sample records
and is not baseline research data.

`src/experiment/prompt_renderer.py` validates both inputs and combines them
deterministically. It replaces only the task-description variable, writes the
exact UTF-8 canonical prompt bytes, and records their SHA-256 hashes. The
descriptive `external_dependency_requirement` field is never rendered and must
not control package selection.

## Prompt control and neutrality

One canonical master prompt supplies the same substantive requirements to all
four workflows. Provider- or workflow-specific rewriting is forbidden, including
changes made after observing earlier results.

Package validity and hallucination terminology are excluded to avoid measurement
priming. The prompt does not force an external dependency: built-in-only
solutions and empty third-party dependency declarations are valid when the task
does not require an external package.

## Authoritative workflow flow

Each canonical prompt is independently submitted to exactly these AI coding
tools/workflows:

- ChatGPT Web
- Gemini Web
- Codex CLI
- Antigravity CLI — Gemini

The list is not a chained conversation and does not describe four equivalent LLM
architectures. Each task/workflow condition requires three successful independent
baseline runs. The full baseline is:

```text
30 tasks × 4 workflows × 3 successful runs = 360 successful outputs
```

Technical failure attempts and retries are recorded separately and do not count
as successful repetitions. Web runs use new chats/sessions; CLI runs use clean
workspaces without preceding generated artifacts. Provider-state limitations
that cannot be disabled are recorded rather than hidden.

## SHA-256 integrity evidence

The renderer computes SHA-256 from the exact bytes written for each prompt. A
manifest hash detects any intervening byte-level change. The execution and raw
capture stages must additionally associate this canonical prompt hash with the
generation record.

## Versioning

Template version `1.0.0` identifies the frozen full-study wording and response
structure. Task-set version `final-1.0.0` identifies the 30-task collection. Both
are recorded in prompt manifests and generation metadata. Historical
`pilot-0.1.0` artifacts remain preserved and are not baseline observations.

## Experimental safety

Prompt rendering produces no AI response, executes no generated code, performs
no npm validation, and makes no provider or registry request. Later execution
must preserve independence, isolation, unchanged raw output, append-only attempt
evidence, and credential safety.
