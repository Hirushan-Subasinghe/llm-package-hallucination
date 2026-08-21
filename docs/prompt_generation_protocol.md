# Prompt Generation Protocol

## Separation of responsibilities

`prompts/templates/master_prompt_v0.1.0.md` contains the fixed experimental instructions. It has exactly one variable, `{{TASK_DESCRIPTION}}`.

`prompts/tasks/pilot_samples.jsonl` contains the variable functional tasks and their task metadata. These records are demonstration and pilot candidates rather than observations.

`src/experiment/prompt_renderer.py` validates both inputs and combines them deterministically. It replaces only the task-description variable, writes the exact UTF-8 canonical prompt bytes, and records their SHA-256 hashes.

## Why this matters

Using one canonical master prompt reduces prompt-wording variation between AI tools. Each tool receives the same rendered instructions for a given task, so provider-specific prompt rewriting does not become an uncontrolled experimental variable.

Package validity and hallucination terminology are deliberately excluded from the experimental prompt to reduce measurement priming. The prompt asks the model to select packages, APIs, and implementation approaches as it normally would when solving the task, without disclosing that package validity is under study.

Future registry, network, and tool restrictions are enforced by the provider execution environment rather than stated inside the experimental prompt. This keeps operational controls separate from the experimental instructions presented to the model.

## Provider flow

The intended flow is:

Canonical Prompt → ChatGPT → Gemini → GitHub Copilot → Claude when provider access becomes available

This shows the intended provider families, not a chained conversation: each provider invocation and repetition must remain independent. Provider availability does not alter the canonical prompt itself. Claude remains part of the planned infrastructure while its access is pending.

## SHA-256 integrity evidence

The renderer computes SHA-256 from the exact bytes written for each prompt. The manifest hash therefore provides evidence that the input text presented later is the preserved canonical prompt, and detects any intervening byte-level change.

## Versioning

The template version identifies the fixed wording and structure of the master prompt. The task-set version identifies a particular collection of variable functional tasks. Either can evolve independently, and both are recorded in every manifest entry.

`pilot-0.1.0` is a sample pilot task set. It is not the final frozen research dataset.

## Experimental safety

Prompt rendering produces no generated response, executes no generated code, and performs no npm validation. It makes no provider or package-registry request. Later provider execution must preserve the repository's isolation, independence, raw-data, and credential-handling requirements.
