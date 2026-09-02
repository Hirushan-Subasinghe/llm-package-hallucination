# System Documentation

## 1. System overview

This repository contains the first implemented stage of a reproducible academic
experiment for studying third-party npm package hallucination in AI-generated
Node.js code.

The implemented system converts versioned task definitions into canonical,
provider-neutral prompts. It validates the inputs, renders prompts
deterministically, stores the exact UTF-8 prompt bytes, and produces a JSONL
manifest containing provenance metadata and a SHA-256 digest for every prompt.

The repository is experimental infrastructure. It does not contain research
conclusions, and the pilot tasks are not collected observations.

### Current development boundary

| Capability | Status |
| --- | --- |
| Versioned master prompt | Implemented |
| Versioned pilot task definitions | Implemented |
| Input validation | Implemented (strict task schema and vocabularies) |
| Deterministic prompt rendering | Implemented |
| SHA-256 prompt manifest | Implemented |
| Automated renderer tests | Implemented |
| Provider configuration skeleton | Present, disabled |
| Isolated provider execution | Not implemented |
| Independent repetitions and retry recording | Not implemented |
| Append-only raw response capture | Not implemented |
| npm registry validation | Not implemented |
| Hallucination classification | Not implemented |
| Statistical analysis or risk scoring | Not implemented |

## 2. Research and safety constraints

The repository treats generated model output as research evidence. Such output
must not be edited to improve it, selectively retained, or automatically
executed. Dependencies named by a model must not be installed, and generated
applications must not be started or published.

The system must never fabricate model responses, npm lookup results,
timestamps, model identifiers, or statistics. Successful raw responses and
technical-failure records are intended to become append-only records when the
provider-execution stage is implemented. Credentials and secret-bearing error
content must never be recorded.

Provider executions are required to use isolated, clean temporary working
directories that do not expose repository instructions, source code, other
models' responses, or previous repetition state. Each repetition must be an
independent invocation. These requirements are project policy; provider
execution enforcing them does not yet exist.

## 3. Architecture

The implemented data flow is:

```text
master prompt template ─┐
                        ├─> validation ─> deterministic renderer
JSONL task definitions ─┘                         │
                                                  ├─> one UTF-8 prompt per task
                                                  └─> JSONL integrity manifest
```

The wider intended experiment is:

```text
Task definition -> Master template -> Deterministic renderer
                -> Canonical prompt -> Isolated provider execution
                -> Append-only raw evidence -> Later validation and analysis
```

Only the stages through canonical prompt generation are implemented.

### Component map

| Path | Responsibility |
| --- | --- |
| `prompts/templates/master_prompt_v0.1.0.md` | Fixed provider-neutral experimental instructions |
| `prompts/tasks/pilot_samples.jsonl` | Six sample task definitions and task metadata |
| `src/experiment/prompt_renderer.py` | Validation, rendering, hashing, and manifest generation |
| `scripts/render_prompts.py` | Repository-specific entry point for the pilot task set |
| `prompts/rendered/pilot-0.1.0/` | Versioned canonical prompt artifacts and manifest |
| `tests/test_prompt_renderer.py` | Unit and reproducibility tests |
| `config/providers.example.yaml` | Disabled placeholder configuration for future providers |
| `docs/prompt_generation_protocol.md` | Methodological rationale for prompt generation |
| `logs/.gitkeep` | Placeholder directory; no logging system is implemented |

The Python package uses a `src/` layout. It has no runtime third-party
dependencies and requires Python 3.11 or later.

## 4. Prompt inputs

### 4.1 Master template

The master template fixes the target environment, implementation requirements,
and response structure presented to a provider. Its sole variable is:

```text
{{TASK_DESCRIPTION}}
```

The renderer requires this placeholder to occur exactly once. A missing or
repeated placeholder is rejected. Provider names and experiment-revealing terms
are intentionally absent from the template to avoid provider-specific wording
and measurement priming.

The current template version is `0.1.0`. Changing its wording should result in
a new template version and, by convention, a new versioned template file.

### 4.2 Task definitions

Tasks are stored as JSON Lines: one JSON object per nonblank line. Source order
does not determine output order.

Every record must contain these non-empty string fields:

| Field | Meaning |
| --- | --- |
| `task_id` | Unique identifier and output filename stem |
| `category` | Functional category represented by the task |
| `difficulty` | Declared task difficulty |
| `task_description` | Exact text inserted into the master template |
| `task_set_version` | Version shared by every record in the input file |
| `status` | Lifecycle label such as `sample` |

The renderer also enforces the following rules:

- each line must be nonblank and valid JSON;
- each record must be a JSON object;
- required values must be non-empty strings;
- `task_id` values must be unique and safe as individual filenames; and
- all records must declare exactly one common `task_set_version`.

Unknown additional JSON fields are currently accepted but are not copied to the
manifest.

The pilot set is `pilot-0.1.0` and contains six medium-difficulty samples:

| Task ID | Category |
| --- | --- |
| `API-001` | API Development and Endpoints |
| `AUTH-001` | Authentication and Authorization |
| `DB-001` | Database Connectivity and Integration |
| `FILE-001` | File Handling and Processing |
| `LOG-001` | Logging and Caching |
| `SEC-001` | Security Features and Encryption |

These are pilot candidates, not a final frozen dataset and not research
observations.

## 5. Rendering behavior

The public rendering function is:

```python
render_prompts(
    template_path,
    tasks_path,
    output_root,
    *,
    template_version,
    manifest_path_root=None,
)
```

Rendering proceeds as follows:

1. Read the template as UTF-8 and validate its one placeholder.
2. Parse and validate every JSONL task record in source order.
3. Verify that the input contains one task-set version.
4. Create `<output_root>/<task_set_version>/` if necessary.
5. Sort tasks lexicographically by `task_id`.
6. Replace the sole placeholder with the task description.
7. Encode the resulting prompt as UTF-8 and write `<task_id>.txt`.
8. Compute SHA-256 over the exact bytes written.
9. Write a compact, deterministically ordered `manifest.jsonl`.

The implementation adds no timestamp, random value, platform-specific metadata,
or provider-specific text. Given identical input bytes and arguments, repeated
renders produce byte-identical prompt and manifest files.

The renderer currently overwrites files at the selected rendered-output path.
That behavior is suitable for reproducibly derived prompt artifacts, but it must
not be reused for future append-only raw response storage.

### Manifest schema

Each manifest line contains:

| Field | Meaning |
| --- | --- |
| `task_id` | Task identifier |
| `category` | Task category copied from the source record |
| `difficulty` | Difficulty copied from the source record |
| `task_set_version` | Version of the task collection |
| `template_version` | Version supplied to the renderer |
| `rendered_prompt_path` | Path recorded for the prompt artifact |
| `sha256` | Lowercase hexadecimal SHA-256 of exact prompt bytes |

The repository entry point supplies `prompts/rendered` as
`manifest_path_root`, making stored paths repository-relative. Direct library
callers that omit it receive paths based on the provided output root.

The manifest proves byte identity between a preserved prompt and the digest; it
does not prove that a provider received the prompt or identify a provider run.

## 6. Setup and operation

From the repository root, create an isolated Python environment and install the
project in editable mode:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Render the canonical pilot prompts:

```sh
python scripts/render_prompts.py
```

The command writes six prompt files plus the manifest under
`prompts/rendered/pilot-0.1.0/`. It performs no network requests, invokes no AI
provider, executes no generated JavaScript, and installs no npm package.

### Generic command-line interface

The renderer module also exposes a parameterized CLI:

```sh
python -m experiment.prompt_renderer \
  --template prompts/templates/master_prompt_v0.1.0.md \
  --tasks prompts/tasks/pilot_samples.jsonl \
  --output-root /tmp/rendered-prompts \
  --template-version 0.1.0
```

This generic CLI does not set `manifest_path_root`; consequently, the recorded
path follows the supplied output root rather than the repository-relative path
used by `scripts/render_prompts.py`.

Invalid inputs raise `PromptValidationError`. Filesystem and UTF-8 errors are
reported through their normal Python exceptions. The CLI does not currently
convert validation errors into a custom structured diagnostic format.

## 7. Verification and tests

Run the complete test suite with:

```sh
python -m unittest discover -s tests -v
```

The tests verify:

- all six pilot records parse;
- each prompt is created at the expected path;
- rendered prompts contain no unresolved placeholder;
- a template must contain exactly one placeholder;
- missing task fields and duplicate task IDs are rejected;
- consecutive renders are byte-identical;
- manifest hashes match the generated prompt bytes;
- provider names are absent from the master template; and
- experiment-sensitive package-validity terminology is absent from the master
  template.

The suite uses temporary directories for generated test artifacts and does not
contact providers or package registries.

The preparation-stage task and generation metadata schemas, retry policy, raw
data policy, isolation policy, and versioning rules are documented in
[`experimental_protocol.md`](experimental_protocol.md). JSON Schema documents
are under `schemas/`; validation is dependency-free and rejects unknown task
fields.

### Manual integrity check

A prompt digest can be independently checked with:

```sh
sha256sum prompts/rendered/pilot-0.1.0/API-001.txt
```

The result should equal the `sha256` value for `API-001` in the adjacent
manifest. A mismatch means the artifact bytes or manifest have changed.

## 8. Provider configuration status

`config/providers.example.yaml` describes planned entries for OpenAI Codex CLI,
Anthropic Claude Code, Google Gemini CLI, and GitHub Copilot CLI. Every provider
is disabled. Execution mode, executable path, exact model identifier, CLI
version, and timeout are intentionally unset.

This file is a configuration skeleton, not an executor. No code currently reads
it. The provider list does not imply that access has been verified, a model has
been selected, or any model response has been collected. Exact model identifiers
must be verified and frozen before final collection; CLI versions must be
captured at execution time rather than guessed.

When provider support is implemented, providers must receive the same canonical
prompt for a task. The documented provider flow is an ordering of provider
families, not a chained conversation. Outputs and conversation state must never
pass from one provider or repetition to another.

## 9. Reproducibility and versioning

Template and task-set versions are independent:

- the template version identifies fixed instructions and response structure;
- the task-set version identifies the collection of functional tasks; and
- both are included in every manifest record.

For a reproducible prompt build, preserve the template, task JSONL, renderer
revision, generated prompt, and manifest together. The SHA-256 value detects a
byte change but does not explain why it occurred. Git history supplies the
source-level provenance for tracked artifacts.

Before changing a frozen experimental input, create a new version instead of
silently replacing the old version. Do not infer that the current pilot set is
frozen merely because rendered artifacts are checked into the repository.

## 10. Known limitations

- JSON Schema documents are descriptive artifacts; the dependency-free Python
  validator is the executable enforcement used by the renderer and tests.
- Task descriptions may themselves contain template-like text; only the master
  template's placeholder count is validated.
- An empty task file reaches the common-version check and fails with a generic
  validation message rather than a dedicated empty-input error.
- Existing derived prompt files and manifests are overwritten on rerender.
- Stale prompt files from tasks removed from a task set are not automatically
  removed.
- The template version is supplied by the caller and is not cross-checked
  against the template filename or contents.
- There is no automated verification that committed rendered artifacts match
  current inputs unless the renderer or tests are run.
- There is no provider executor, isolation layer, attempt ledger, response
  schema, redaction layer, or append-only storage enforcement.
- There is no npm package extraction, registry lookup, classification, analysis,
  or reporting implementation.

## 11. Future integration requirements

The following describes required future work, not present functionality.

An isolated provider-execution stage should use a clean temporary directory for
every repetition, disable persistent provider context where possible, and record
limitations where it is not possible. It should preserve prompt hashes and
verified model/tool metadata, give successful generations unique immutable
identifiers, and distinguish repetitions from retry attempts.

Technical failures should be append-only records separate from successful raw
responses. Records should retain identifiers, intended model, time, prompt hash,
runtime version, failure category, exit status, timeout status, and a redacted
error summary when available. They must never become hallucination observations.

Raw response preservation should store exact provider output without rewriting
it and refuse silent overwrite. Later npm validation, hallucination
classification, statistical analysis, and risk scoring should be separate stages
with their own documented methodology and must not be folded into prompt
generation.

## 12. Contributor guidance

Keep experimental instructions provider-neutral and render them through the
single deterministic pipeline. Do not introduce provider-specific rewrites
without explicit methodological approval. Add or update tests whenever renderer
validation or output semantics change.

Do not run generated model code or install dependencies named in it. Do not
commit automatically. A requested commit requires tests, formatting and static
checks when configured, status and diff inspection, a secrets check, an exact
commit summary, and explicit user approval.

For the rationale behind the canonical prompt design, see
[`prompt_generation_protocol.md`](prompt_generation_protocol.md).
