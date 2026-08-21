# Project Instructions

## Purpose

This repository builds infrastructure for a reproducible academic experiment measuring third-party npm package hallucination in AI-generated Node.js/npm code.

Codex develops the experimental environment only. Codex must never fabricate research data.

## Research integrity rules

Never:

- fabricate LLM responses;
- fabricate npm results;
- fabricate timestamps;
- fabricate model identifiers;
- fabricate statistical results;
- modify raw responses after capture;
- delete inconvenient experimental outputs;
- rewrite a response because it appears wrong; or
- selectively preserve only results supporting a hypothesis.

## Generated code safety

Generated LLM code is research evidence. Never automatically:

- execute it;
- run `npm install`;
- run `npm start`;
- run `node` on it;
- install dependencies named inside it;
- publish packages; or
- register hallucinated package names.

## Prompt integrity

The prompt pipeline is:

Task definition -> master template -> deterministic renderer -> canonical prompt -> provider execution

Provider-specific rewrites of the experimental prompt are forbidden unless explicitly approved as part of the methodology.

## Provider isolation

Provider execution must eventually occur from isolated temporary working directories that do not expose:

- `AGENTS.md`;
- repository source;
- responses from other models; or
- unrelated project context.

## Experimental repetition independence

Every experimental repetition is an independent provider invocation. Never continue a previous conversation or session for a new repetition unless the methodology explicitly defines continuation as a tested condition.

For every repetition:

- do not expose previous responses to later repetitions;
- do not expose another provider's output to a provider;
- do not reuse generated source files or working-directory state between repetitions;
- use a clean isolated temporary working directory where technically possible; and
- disable or avoid provider-side persistent memory, project context, custom instructions, and repository instructions where the interface permits.

If provider-side state cannot be fully disabled, record the limitation in metadata rather than hiding it.

A retry caused by a technical failure is an `attempt`, not automatically a new valid experimental repetition. Successful repetitions must have unique, immutable generation identifiers.

## Raw-data integrity

Raw successful responses are append-only. Existing successful raw records must never be silently overwritten.

Technical failures must be recorded separately and their records are also append-only research-operational evidence. Retain, when available:

- attempt identifier;
- task identifier;
- provider and tool;
- intended model identifier;
- timestamp;
- prompt hash;
- CLI or runtime version;
- failure category;
- exit code;
- timeout status; and
- redacted error summary.

Never store credentials or secret-bearing raw error content. Technical failures must never be classified as hallucination observations. A successful retry must create a new attempt record and must not erase the failed attempt.

## Secrets

Never print, log, commit, or expose:

- API keys;
- OAuth tokens;
- cookies;
- passwords;
- access tokens; or
- private credentials.

Use provider-native authenticated CLI sessions or environment variables when later required.

## Git

Never commit automatically.

Before every requested commit:

1. Run relevant tests.
2. Run formatting and static validation if configured.
3. Inspect `git status`.
4. Inspect the staged and uncommitted diff.
5. Check for secrets.
6. Report exactly what will be committed.
7. Wait for explicit user approval.

Never use destructive Git commands unless explicitly requested.

## Scope control

Do not implement later research stages unless specifically instructed. In particular, do not implement npm validation, hallucination classification, statistical analysis, or risk scoring during environment-setup tasks.
