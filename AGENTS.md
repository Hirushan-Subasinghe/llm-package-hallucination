# Repository Instructions: Final Dissertation Work

## Purpose

This is the integrated final-report/research worktree, not a live data-collection worktree. Live v2.6 collection remains authoritative in `~/Dev/ai-hallucination-study`. Do not attempt live collection here.

## Source of Truth

Resolve conflicts in this order:

1. Actual frozen experiment inputs, outputs, manifests, code, configuration, and verified results.
2. `docs/current_research_status.md`.
3. `docs/research_progress_log.md`.
4. `docs/final_paper_notes.md`.
5. Verified implementation/results produced in the current workflow.
6. `IM2021101.pdf` and earlier dissertation drafts.
7. Older plans, proposals, or chat discussions.

The dissertation must describe what was actually performed.

## Frozen Experiment Integrity

Never modify, regenerate, reinterpret, or silently replace frozen prompts, task manifests, rendered prompts, raw/provider responses, collection state, model configuration, generation settings, token limits, retry/pacing rules, or frozen experiment metadata. Never represent planned-but-unperformed work as performed research.

## Experimental Integrity and Repository Security

- Act only as an implementation/report assistant, never as an experimental model producing synthetic dataset observations. Never fabricate observations or represent generated content as a response from ChatGPT, Claude, Gemini, Copilot, or another evaluated model.
- Never modify stored raw experimental or provider responses. Treat raw collection data as append-only; preserve required hashes and provenance.
- Never install, execute, or test dependencies merely because they appear in an experimental model response. In particular, do not run `npm install`, `npx`, `yarn add`, `pnpm add`, or `bun add`, or execute generated code using dependency names extracted from experimental responses.
- Validate registries/packages only through read-only evidence or API queries. Never register, reserve, publish, or claim names observed as possible hallucinations.
- Keep pilot, test, and synthetic validation data clearly separate from final experimental data. Preserve model, tool, and version information exactly as observed; when a temperature, seed, provider version, or model version is unavailable, record `not_exposed` or the repository-standard unavailable value—never guess. Use ISO-8601 UTC timestamps where records are created.
- Prefer deterministic scripts, explicit schemas, provenance fields, and automated tests. Never silently change methodology; follow the controlling decision/documentation process for every methodological decision.
- For package extraction and classification, apply the implemented normalization rules: Node.js built-ins, `node:` imports, and relative, local, file, or HTTP references are not silently external npm dependencies. Do not recursively analyze transitive dependencies unless the controlling methodology explicitly requires it.
- Never place API keys, tokens, or other secrets in the repository; use the supported local secret/environment mechanisms.

## Current Scope

Use repository evidence for exact details. The implemented final study is Node.js/npm focused. Do not silently reintroduce outdated proposal elements, including Spring Boot/Maven as a final ecosystem, human developer surveys, developer-expertise variables, workflow-autonomy experiments, verification mediators, Java/Maven AST extraction, old planned model/tool sets, old risk models, or unperformed validation procedures.

## Metrics and Classification

Follow controlling decisions in `docs/decision_log.md`; do not redefine them from memory:

- D033: primary PHR/SHR units and denominators.
- D034: primary/secondary external-dependency boundary.
- D035: abnormal provider termination handling.
- D036: secondary/exploratory DFR/RDFR.
- D037: primary confirmed-hallucination routing.
- D038: integrated alias for the live interrupted-request recovery decision.

Registry evidence is not automatically a research classification. An npm `404` / `not_found` alone is not a confirmed hallucination. Use implemented PIPE-05 / PIPE-05B taxonomy and adjudication semantics. Do not relabel namespace confusion, package-name confusion, local/self-reference, legacy/removed, ecosystem confusion, or unresolved states as confirmed hallucinations unless controlling adjudication rules establish it.

## Report Writing and Citations

Before drafting methodology or results, inspect repository evidence. Do not invent model identities, providers, versions, task or observation counts, settings, metrics, results, statistical significance, risk scores, validations, or citations. For an unverified final result, write `[FINAL RESULT PENDING]`; never turn interim results into final findings.

Use only approved dissertation references in `docs/references/approved_references.md` once it exists. If another academic source is needed, write:

```text
NEW SOURCE PROPOSED:
<reason>
```

Do not cite it until researcher approval. Repository files support methodology/results claims but are not literature references.

Trace important dissertation claims through `docs/final_report_support/claims_evidence_matrix.md`. Never mark a claim `VERIFIED` without exact supporting repository evidence.

Use formal academic English and cautious evidence-grounded wording (for example, “the findings indicate…”, “within the evaluated experimental conditions…”, and “at the time of registry validation…”). Avoid unsupported absolutes such as “proves”, “guarantees”, “completely eliminates”, or “never existed”. Write completed methodology in past tense.

## Working Method and Documentation

For substantial report work, use:

`repository audit → evidence summary → old-draft reconciliation → outline → subsection drafting → factual verification → language review → chapter assembly → consistency check`

When present, review `recomendations.txt` as advisory research recommendations during dissertation planning, reporting, and reconciliation. It does not override frozen evidence, verified implementation, current status, decisions, or verified results; unimplemented recommendations are not performed methodology and may inform interpretation, reporting emphasis, limitations, or future work only where consistent with verified evidence.

Do not jump from inspection directly to a supposedly final chapter.

After every significant research/report milestone, determine:

- Progress-log update needed: YES/NO
- Final-paper note needed: YES/NO
- Draft reconciliation needed: YES/NO

If YES, provide exact appendable Markdown, or update it only when explicitly instructed. Never rewrite historical progress-log entries except to correct an explicitly documented mistake.

## Worktree Safety

Do not merge, rebase, stash, reset, clean, delete quarantine/checkpoint evidence, or commit unless explicitly requested.

Do not run live collection from this worktree; the repository guard and `~/Dev/ai-hallucination-study` remain the authoritative collection boundary.
