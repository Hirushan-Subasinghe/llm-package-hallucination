# Experimental protocol and schema freeze

This document freezes preparation-stage rules. It does not collect responses,
contact providers or npm, execute generated code, classify packages, or compute
risk scores.

## Scope and task definitions

The study is Node.js with npm. The primary package-hallucination measure will
consider only direct dependencies explicitly introduced by a generated
solution. Registry validation is a later, independent phase. The final task set
has 30 records: five each for `AUTH`, `DB`, `FILE`, `API`, `SEC`, and `LOG`.
IDs are deterministic (`AUTH-001` through `LOG-005`). The six records currently
in `prompts/tasks/pilot_samples.jsonl` remain samples, not final observations.

Canonical task records are validated by `schemas/task.schema.json` and
`src/experiment/schema_validation.py`. Required scope fields are `ecosystem`
=`node.js`, `runtime`=`Node.js`, and `package_manager`=`npm`. `task_family`,
`external_dependency_requirement`, `security_criticality`, and `notes` are
optional: they describe task design and do not contain expected packages,
answers, registry results, or labels. Unknown fields are rejected to prevent
contamination.

## Generation versus attempt

One planned experimental generation is one task/repetition/provider condition.
The primary design has two independent repetitions, so the future Codex target
is 60 generations. A generation receives a stable `generation_id`; each process
execution receives a unique `attempt_id`. A technical retry keeps the same
generation identity, remains a separate append-only attempt record, and does
not create a third repetition. A successful repetition must have one immutable
successful generation record.

`schemas/generation_metadata.schema.json` defines the required metadata for
each technical attempt, including prompt hash, intended model/tool, timestamps,
workspace controls, process result, raw-artifact paths and action evidence.
Successful records require a non-empty raw-response path, lowercase SHA-256,
and non-negative byte length; they have no failure category and cannot be
timeouts. Failed technical attempts require one controlled infrastructure
failure category and may omit raw-response evidence when no usable model output
exists. Timestamp fields are timezone-aware and finish cannot precede start.

The JSON Schema expresses the conditional success/failure and raw-evidence
rules. Python additionally performs cross-field timestamp ordering and
timezone-awareness checks; storage append-only and overwrite prevention remain
future runner/storage responsibilities.

## Retry policy

Retries are permitted only for infrastructure failures with no usable model
output: process launch failure, timeout before generation began, local runner
failure, or authentication/service failure. A retry is not permitted because
the code is invalid, does not compile, has no dependencies, hallucinates a
package, misunderstands the task, stops after a valid response, or refuses.
The implementation of retries belongs to the future runner; this phase only
freezes the rule and schema.

## Raw data and later phases

Raw stdout, stderr, and response bytes are preserved exactly, with SHA-256 and
byte length recorded. Successful raw records are append-only and must never be
overwritten or manually edited. Technical failures are retained separately and
are not observations. Dependency extraction, npm validation, classification,
and risk analysis are later phases and cannot write labels or results into raw
generation files.

## Isolation

The research/orchestration repository holds task definitions, templates,
schemas, manifests, metadata, and later analysis artifacts. Each future Codex
trial receives a fresh temporary workspace containing only the task's canonical
prompt and the minimum empty workspace needed for the coding task. It must not
contain `AGENTS.md`, repository documentation or source, other prompts or
outputs, validation code, registry results, known lists, scores, or datasets.

The intended flow is:

```text
canonical prompt -> fresh workspace -> fresh Codex invocation
-> raw output/actions -> workspace evidence -> finalized attempt record
-> later dependency extraction -> npm validation -> classification -> analysis
```

Package installation is blocked during generation while attempted commands are
recorded. Unknown packages must never execute on the host. Filesystem isolation
and these execution controls will be implemented and tested by the future
runner; they are not currently enforced by this repository.

## Versioning

Task-set versions use `pilot-X.Y.Z` or `final-X.Y.Z`; the task-set version
changes when task membership or task text changes. Template versions use
`X.Y.Z`; any wording or response-structure change creates a new template file.
Protocol versions use `X.Y.Z`; change them when experimental controls,
metadata semantics, retry rules, isolation, or phase boundaries change. Runner
versions use `X.Y.Z`; change them for execution, capture, or serialization
behavior changes. Every future attempt records all four applicable versions.

## Data conventions

`prompts/tasks` contains canonical JSONL inputs; `prompts/rendered/<version>`
contains derived prompt artifacts and manifests. Future attempt metadata belongs
under `data/metadata`, successful raw artifacts under `data/raw/<provider>`,
and technical failures under `data/failed`. These directories are conventions,
not an execution implementation.
