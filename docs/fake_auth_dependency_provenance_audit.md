# FAKE-AUTH-DEPENDENCY-PROVENANCE-AUDIT-01

- Audit date (UTC): 2026-09-25
- Auditor role: implementation assistant (Claude Code), audit only
- Repository: `~/Dev/ai-hallucination-study` (branch `feature/data-collection`, HEAD `2f50255`)
- Also inspected: `~/Dev/ai-hallucination-analysis` (`analysis/pipeline`), `~/Dev/ai-hallucination-integration` (`integration/final-report`)
- Trigger: `docs/final_v2.7_consolidation_preflight.md` §8 flagged `fake-auth@0.1.7` as `RESEARCHER_DECISION_REQUIRED`

## 0. Constraints observed during the audit

No package was installed, uninstalled, imported or executed. `package.json`, `package-lock.json` and `node_modules/` were not modified. Nothing was committed. All evidence came from read-only inspection of:

- git history;
- file metadata;
- `node_modules/*/package.json` manifests, read as text;
- npm debug logs in `~/.npm/_logs`;
- npm cache index metadata in `~/.npm/_cacache/index-v5`, covering timestamps and keys only;
- local Codex session transcripts in `~/.codex`.

## 1. Summary of findings

| Question | Finding |
|---|---|
| Introduction commit | `5333f9e21d6f9d367af46fa96588a220182d1655`, "Add package validation and smoke test data", 2026-09-22T04:11:37Z (09:41:37 +0530). This is the only commit touching `package.json` and `package-lock.json`. |
| First local install | 2026-09-21T04:31:02Z (10:01:02 +0530). This is about 24 h before the commit. |
| Direct or transitive | `fake-auth` is a **direct** root dependency (`"fake-auth": "^0.1.7"`). `js-base64@2.6.4` is its only transitive dependency. |
| Reason | Accidental. The PIPE-03 task specification was most likely pasted into an interactive shell in the repository root. It contains the illustrative line `npm install fake-auth`. This is strongly supported inference, not proof (§4). |
| Used by experimental validation | **NO** |
| Executed by the research pipeline | **NO** |
| Part of hallucination confirmation | **NO** |
| Fixture or development artifact | The *name* is a hand-written test fixture string. The *installed package* is an accidental development-environment artifact. The installed package is not a fixture, because no test uses it. |

## 2. Git history

```
git log --follow -- package.json       -> 5333f9e only
git log --follow -- package-lock.json  -> 5333f9e only
git log -S fake-auth --all             -> 5333f9e, 2f50255 (the preflight doc only)
```

Commit `5333f9e` is a bulk commit of 93 files and 8,053 insertions. It covers the smoke data, the batch states, the PIPE-02 to PIPE-05 scripts, schemas and tests. It adds these root files:

- `package.json`: `{"dependencies": {"fake-auth": "^0.1.7"}}`. It has no `name`, no `version` and no `scripts` field.
- `package-lock.json`: lockfile v3, with root name `ai-hallucination-study` (derived from the directory name). It lists `node_modules/fake-auth@0.1.7` and `node_modules/js-base64@2.6.4`.

A `package.json` with nothing but a single `dependencies` entry is the file npm creates when `npm install <pkg>` runs in a directory that has no `package.json`. It is not a hand-authored project manifest.

Follow-up commits:

- `dda63eb` at 09:45:08 +0530, "Clean up gitignore".
- `5449f41` at 09:46:34 +0530, "Ignore node_modules". This added `node_modules/` to `.gitignore`.

So `node_modules/` was never committed. The two manifest files stayed tracked. Nothing in the commit message, `docs/decision_log.md` or `docs/research_progress_log.md` mentions `fake-auth`, `package.json` or `node_modules`.

## 3. Repository references (excluding `node_modules/`, `.git/`, `.venv/`)

| File | Nature |
|---|---|
| `package.json`, `package-lock.json` | The accidental manifests described above |
| `tests/test_extract_package_references.py:135` | Test fixture *string*: `"npm install fake-auth\nimport auth from 'fake-auth';\nrequire('fake-auth');"`. It is passed to the PIPE-03 text extractor to test occurrence counting and deduplication. It is parsed as text only. The test does not install, import or resolve anything. |
| `docs/final_v2.7_consolidation_preflight.md` | The finding that triggered this audit |

The same three non-doc files are present in the analysis and integration worktrees. They inherit them through shared history.

`data/`, `prompts/`, `results/` and all raw responses in all three worktrees: **0 matches** for `fake-auth`. No experimental prompt, raw response, extraction output, PIPE-04 registry validation record or classification record contains the name.

## 4. Reconstruction of how the package was installed

### 4.1 Timeline (UTC)

| Time | Event | Source |
|---|---|---|
| 2026-09-21T04:31:02.273Z | npm fetches the `fake-auth` packument | `~/.npm/_cacache/index-v5` key `make-fetch-happen:request-cache:https://registry.npmjs.org/fake-auth` |
| 04:31:02.749Z to 04:31:04.609Z | npm fetches the `js-base64` packument, then both tarballs | npm cache index |
| 04:31:02 to 04:31:04 (10:01:02 to 10:01:04 +0530) | `node_modules/`, `package.json` and `package-lock.json` are created in the study repository root | File timestamps quoted in the Codex session below (line 574) |
| 04:32:54 (10:02:54 +0530) | Empty 0-byte files named `express`, `lodash`, `normalized_package`, `preserve` and `version_specifier` are created in the repository root | Same Codex session (line 585) |
| 04:37:18Z | The PIPE-03 task specification is submitted to Codex, session `01a0c241-026d-73c0-922c-53c2ebf7d5a0` | `~/.codex/history.jsonl` |
| 05:39 to 05:41Z | That Codex session notices the untracked `package.json`, `node_modules/` and empty files. It concludes that the extractor tests "do not invoke npm, install packages, spawn shell commands, or write repository-root package files". It records provenance as "Uncertain". | Codex rollout `2026-09-21T10-07-15-…jsonl` |
| 2026-09-22T04:11:37Z | Commit `5333f9e` tracks `package.json` and `package-lock.json` | git |
| 2026-09-22T04:16:45Z | `npm install` with **no arguments** runs in the study repository. It re-materialises the two packages from the lockfile, both "cache hit". | `~/.npm/_logs/2026-09-22T04_16_45_633Z-debug-0.log` |
| 2026-09-24T14:14:03Z | `npm ci` runs in `~/Dev/ai-hallucination-analysis` and installs the same two packages | `~/.npm/_logs/2026-09-24T14_14_03_103Z-debug-0.log` |
| 2026-09-24T08:31:01Z and 14:14:05Z | `npm start` runs in the analysis worktree and fails with `Missing script: "start"`. Nothing was executed. | npm debug logs |

The npm debug log of the original 2026-09-21 install was removed by npm log rotation (`logs-max:10`). The exact original command line is therefore not recoverable. `~/.bash_history` has no `fake-auth` entry. That absence does not settle the question, because history may be truncated or not flushed.

### 4.2 Why the PIPE-03 specification is the most likely source

The PIPE-03 specification text submitted to Codex at 04:37:18Z contains these lines:

```
npm install fake-auth                      <- line 105
...
lodash/fp
-> lodash
express/lib/router
-> express
...
-> normalized_package = express
-> preserve version specifier separately when reliably available
...
-> version_specifier = 1.2.3
```

If this text is pasted into bash, the results are:

- `npm install fake-auth` runs as a command. It creates exactly the observed minimal `package.json` and lockfile.
- Each `-> X ...` line is parsed as the command `-` with the output redirection `> X`. That creates an empty file named `X`. The expected files are `lodash`, `express`, `normalized_package`, `preserve` and `version_specifier`. These are **exactly** the five empty files observed at 10:02:54 +0530.

The install happened 6 minutes before the same text was submitted to Codex. The most consistent explanation is an accidental paste of the specification into a terminal in the repository root, before it was pasted into Codex.

### 4.3 Unresolved gaps

- The exact keystrokes and actor cannot be proven, because the original npm log was rotated.
- Later spec lines such as `npm install express` did not leave `express` in `node_modules`. This is consistent with buffered input being consumed or discarded while the first `npm install` was running, but it is not proven.
- Who ran the 2026-09-22 `npm install` and the 2026-09-24 `npm ci`/`npm start` is **unknown**. No Codex transcript contains those commands. The pattern suggests manual "set up / run the project" attempts triggered by the presence of `package.json`.

`fake-auth` is a **real** published npm package: author Gabe Ragland, repository `github.com/gragland/fake-auth`, MIT licence. It is not a hallucinated name. Its name coincides with a string invented as a test example.

## 5. Execution analysis

- **Pipeline code.** PIPE-01 to PIPE-10 are Python. `grep` over `scripts/` in all worktrees found no invocation of `node`, `npm`, `npx`, or `node_modules`. The only `subprocess` use is `collect_codex_runs.py`, which launches the Codex CLI and not Node packages. PIPE-04 validates by read-only HTTP to `registry.npmjs.org`.
- **Install-time lifecycle scripts.**
  - `fake-auth@0.1.7` declares only `build` and `prepare`. npm does not run `prepare` for registry-installed dependencies.
  - `js-base64@2.6.4` declares only `test` and `minify`.
  - The root `package.json` has no scripts.

  So `npm install` and `npm ci` executed **no package code**. They only downloaded and extracted it.
- **Runtime.** No repository file `require`s or `import`s `fake-auth` as code. The test file contains the name only inside a string literal passed to a text parser. `npm start` failed before running anything.

Conclusion: `fake-auth` code has never been executed by the research pipeline, by the tests, or by any recorded npm command.

## 6. Methodology assessment

| AGENTS.md rule | Assessment |
|---|---|
| 5. Never install a package merely because it appears in AI-generated experimental code | **Not violated.** `fake-auth` does not appear in any AI-generated experimental response. It came from a researcher-authored specification example. |
| 6. Never run `npm install`/`npx`/… using dependency names extracted from experimental responses | **Not violated.** The name was not extracted from experimental responses. |
| 7. Validate registry data using read-only HTTP/API queries only | **Not violated** by the pipeline. The install was outside the pipeline and had no effect on any validation record. |
| General hygiene | **Deviation.** A third-party npm package was downloaded into the research repository. Its manifests were committed without a decision entry. The unused `package.json` also invites further `npm install`/`npm ci` runs, which happened twice. |

Methodology contradiction: **NO**. Data, validation outputs, classifications and analysis are unaffected. This is an environment-hygiene and provenance-documentation issue.

## 7. Recommended action (for researcher decision; not performed by this audit)

1. Record a decision entry (next free ID, `D044`) that states:
   - the accidental origin of `package.json`, `package-lock.json` and `fake-auth`;
   - that it is not experimental data;
   - that no package code was executed;
   - the chosen remediation.
2. In a separate reviewed commit, remove the tracked `package.json` and `package-lock.json` from the research repository. The project is Python-only and has no Node dependencies. Removing them in git keeps the history as evidence of the incident. Then delete the untracked `node_modules/` in both the study and analysis worktrees.
3. Optionally add a note to the test fixture comment, or rename the example to a clearly synthetic placeholder. **Do not** change it silently: PIPE-03 test semantics must stay identical. Keeping the fixture string as it is is acceptable, because a string literal is harmless.
4. Before consolidation, re-run the repository-integrity checks to confirm that no other root manifests or stray files remain. The five empty files observed on 2026-09-21 are already absent.
5. Do not run `npm install`, `npm ci` or `npm start` in any study worktree.

## 8. Final verdicts

| Item | Verdict |
|---|---|
| Introduction commit | `5333f9e` (tracked). First local install on 2026-09-21T04:31Z, before the commit. |
| Direct or transitive | Direct root dependency. `js-base64` is transitive. |
| Used by experimental validation | NO |
| Executed by research pipeline | NO |
| Methodology contradiction | NO |
| Decision entry needed | YES |
| Chapter 3 change needed | NO |
| Consolidation blocker | YES, until the decision entry and the removal or retention decision are recorded, because preflight §8 marks it `RESEARCHER_DECISION_REQUIRED`. It is not a data-integrity blocker. |

## 9. Independent re-verification (2026-09-25, second pass)

A second read-only pass rechecked the main claims above. No packages were installed or executed. No files other than this document were modified.

- `git show 5333f9e` confirms that the commit adds `package.json` and `package-lock.json`. The lockfile root is `fake-auth: ^0.1.7`, and `js-base64@2.6.4` is resolved as its only dependency.
- The npm cache index time `1789965062273` equals 2026-09-21T04:31:02.273Z. It matches §4.1.
- In the npm debug logs for 2026-09-22T04:16:45Z and 2026-09-24T14:14:03Z, argv is `"install"` (no package argument) and `"ci"`. Both tarballs came from the cache.
- In `~/.codex/history.jsonl`, exactly one entry contains `npm install fake-auth`. It belongs to session `01a0c241-…`, at 2026-09-21T04:37:18Z. Its `->` lines include `lodash`, `express`, `normalized_package` and `preserve`, which is consistent with §4.2.
- A grep of the repository, excluding `node_modules/`, `.git/` and `.venv/`, finds `fake-auth` only in the two manifests, in the test string literal `tests/test_extract_package_references.py:135`, and in the preflight document. There are no matches in `data/`, `prompts/` or `results/`.
- `scripts/` contains no invocation of `node`, `npm` or `npx`. The only `subprocess` use is the Codex CLI launcher.
- The installed `node_modules/fake-auth/package.json` declares scripts `build` and `prepare` only. Neither of these runs on a dependency install.

Re-verification result: sections 1 to 8 are confirmed, with no changes.
