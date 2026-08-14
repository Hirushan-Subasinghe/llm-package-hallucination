# Repository Instructions

## Research Context and Scope

This repository contains experimental software for the undergraduate cybersecurity research project:

> AI Hallucination Attack Surface: A Risk Assessment of Fake APIs and Libraries in AI-Generated Code.

The current implementation phase is limited to Node.js and npm.

The research pipeline is:

standardized prompt
→ AI-generated response
→ raw response preservation
→ dependency extraction
→ npm registry validation
→ classification
→ later risk assessment and statistical analysis

## Research Integrity and Security Rules

1. Act as the implementation assistant, not as an experimental model in the dataset.
2. Never generate experimental observations represented as results from ChatGPT, Claude, Gemini, or GitHub Copilot.
3. Never invent research results.
4. Never modify raw experimental responses after they are stored.
5. Never install a package merely because it appears in AI-generated experimental code.
6. Never run `npm install`, `npx`, `yarn add`, `pnpm add`, `bun add`, or execute generated code using dependency names extracted from experimental responses.
7. Validate registry data using read-only HTTP/API queries only.
8. Never register, reserve, publish, or claim hallucinated package names.
9. Keep pilot/test data clearly separated from final experimental data.
10. Use ISO-8601 UTC for all timestamps.
11. Preserve model, tool, and version information exactly as observed.
12. If temperature, seed, or model-version information is not exposed, record `not_exposed`; never guess it.
13. Treat raw data as append-only during data collection.
14. Record SHA-256 hashes for raw responses where practical.
15. Never place API keys or secrets in the repository.
16. Use `.env` only for local secrets and ensure `.env` is gitignored.
17. Prefer deterministic scripts, explicit schemas, and automated tests.
18. Do not silently change the research methodology. Record implementation decisions in `docs/decision_log.md`.
19. Treat direct Node.js dependencies as the current unit of analysis. Do not recursively analyze transitive dependencies unless explicitly requested later.
20. Do not classify Node.js built-in modules or relative/local imports as external dependencies.

