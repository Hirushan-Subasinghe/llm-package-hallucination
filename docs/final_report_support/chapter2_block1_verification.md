# Chapter 2 Block 1 Verification — CHAPTER-2-BLOCK-1-VERIFICATION-01

**Draft reviewed:** `docs/report_drafts/chapter2_sections_2_1_to_2_4.md` (Sections 2.1–2.4; 4,696 words including headings and metadata lines; uncommitted working draft).
**Controlling evidence:** `AGENTS.md`; `docs/report_generation_protocol.md`; `docs/references/approved_references.md`; `docs/final_report_support/chapter2_literature_synthesis.md`; `docs/final_report_support/chapter2_source_verification.md`; `docs/final_report_support/chapter2_reference_coverage_plan.md` (including its pre-draft freeze addendum); `docs/report_drafts/chapter1_complete_draft.md`; `docs/current_research_status.md`; `docs/final_paper_notes.md`.
**Method:** Every citation was counted directly from the draft text by author string and line. Every substantive literature-backed claim was checked only against the evidence summaries, claim rows (LC01–LC20), and concept rows in `chapter2_source_verification.md`. No literature was browsed, no reference was added, no experimental or frozen file was read for results or modified, no result was calculated, and the draft itself was not edited. `recomendations.txt` is not present in this worktree.

Line numbers below refer to the draft file as reviewed.

---

## 1. Verification verdict

**PASS WITH MINOR CORRECTIONS**

The block is well structured, contains no numeric claims, no dissertation results, no unapproved reference, no Gandhi citation, and no citation-year error. It consistently states that package hallucination is not itself an attack and that the study performed no attack, registration, installation, or execution. However, 16 wording-level corrections are required before Sections 2.5–2.10 are drafted on top of this block. They fall into five groups:

1. claims attributed to "the literature" or "these sources" that exceed the verified evidence, or that implicitly sweep metadata-only sources into an agreement claim (C01–C05);
2. the Ladisa et al. (2023) taxonomy description and the "one route among several" synthesis, which go beyond the recorded full-text evidence (C06, C13);
3. assertive verbs ("establishes") and an unsupported frequency claim ("most frequently discussed") (C07, C08, C10);
4. internal process language leaking into dissertation prose ("approved literature", "verified evidence") (C09);
5. conceptual precision in the naming-threat distinctions and Table 2.1, chiefly the overlap between "accidental dependency error" and "package hallucination" and the weakened "may not correspond" definition (C11, C12, C14, C15).

None of the corrections requires a new source, a new number, or a methodology change.

---

## 2. Citation-accounting result

Independent count from the draft text (author-string search, all occurrences inspected in context):

| Approved reference | Verification level | Occurrences | Draft lines | Section(s) |
|---|---|---:|---|---|
| Agarwal et al. (2024) | METADATA_ONLY | 1 | 35 | 2.2.2 |
| Al-Zofi (2025) | FULL_TEXT_VERIFIED | 7 | 79, 85, 87, 95, 103, 104, 107 | 2.4 |
| Daoud (2026) | METADATA_ONLY | 1 | 35 | 2.2.2 |
| Duan et al. (2020) | FULL_TEXT_VERIFIED | 4 | 51, 61, 67, 91 | 2.3, 2.4 |
| Dubey and Madisetti (2026) | METADATA_ONLY | 1 | 31 | 2.2.1 |
| Gao et al. (2025) | FULL_TEXT_VERIFIED | 3 | 23, 35, 37 | 2.2 |
| Zhao et al. (2025) | FULL_TEXT_VERIFIED | 2 | 93, 106 | 2.4 |
| Ladisa et al. (2023) | FULL_TEXT_VERIFIED | 4 | 49, 51, 53, 91 | 2.3, 2.4 |
| Le-Anh et al. (2026) | METADATA_ONLY | 1 | 27 | 2.2.1 |
| Liu et al. (2026) | FULL_TEXT_VERIFIED | 3 | 25, 35, 37 | 2.2 |
| Ohm and Stuke (2023) | METADATA_ONLY | 1 | 51 | 2.3.1 |
| Spracklen et al. (2025) | FULL_TEXT_VERIFIED | 12 | 29, 39, 61, 63, 67, 79, 93, 95, 103, 106, 107, 109 | 2.2–2.4 |
| Tian et al. (2025) | FULL_TEXT_VERIFIED | 2 | 25, 37 | 2.2 |
| Twist et al. (2026) | FULL_TEXT_VERIFIED | 1 | 39 | 2.2.2 |
| Wang et al. (2025) | METADATA_ONLY | 1 | 51 | 2.3.1 |
| Williams et al. (2025) | FULL_TEXT_VERIFIED | 4 | 49, 51, 53, 91 | 2.3, 2.4 |
| Woesle et al. (2025) | FULL_TEXT_VERIFIED | 2 | 23, 35 | 2.2 |
| Zhuo et al. (2025) | METADATA_ONLY | 1 | 27 | 2.2.1 |

Occurrence counts include Table 2.1 cells (lines 103–107).

**Totals**

- Unique approved references cited: **18 of 34**.
- FULL_TEXT_VERIFIED cited: **11 of 11** (Al-Zofi; Duan; Gao; Zhao; Ladisa; Liu et al. (2026); Spracklen; Tian; Twist; Williams; Woesle).
- METADATA_ONLY cited: **7 of 23** (Agarwal; Daoud; Dubey and Madisetti; Le-Anh; Ohm and Stuke; Wang; Zhuo).
- Approved references still unused: **16** (listed in Section 9).
- Non-approved references cited: **0**.

**Comparison with the 34-reference coverage plan**

- All 18 cited references are approved, and each is used in a role compatible with its coverage-matrix entry.
- Allocation departures (none prohibited): Dubey and Madisetti (2026) was planned for 2.7 and is used in 2.2.1; Ohm and Stuke (2023) was planned for 2.6 and is used in 2.3.1; Twist et al. (2026) was planned for 2.5/2.8 and receives an early context use in 2.2.2; Spracklen et al. (2025) receives an additional verified use (LC13) in 2.2.1. Because Dubey and Madisetti and Ohm and Stuke have now used their single planned contextual citation, they must not be re-cited in 2.6/2.7 as independent support for a stronger claim.
- Spracklen et al. (2025) now has 12 occurrences against a planned 4 meaningful roles. The plan states that counts are ceilings for *roles*, not occurrences, and the 12 occurrences cover five verified roles (LC07, LC08/LC09, LC12, LC13, LC20). This is acceptable, but 2.5–2.9 should avoid adding Spracklen citations to sentences that only restate points already made in 2.4.
- Al-Zofi (2025) has 7 occurrences, all within verified LC05/LC06/LC08 definitional roles. Acceptable.
- The drafting summary appended to `docs/research_progress_log.md` (18 cited; 11 full-text; 7 metadata-only; 16 remaining) is **confirmed** by this independent count.

---

## 3. Claim-verification table

Status key: **DIRECTLY_SUPPORTED** — within a verified evidence summary; **SUPPORTED_WITH_QUALIFICATION** — supportable but requires the qualification shown; **CONTEXT_ONLY** — uncited general/technical or author-analytical statement not presented as a literature finding; **OVERSTATED** — exceeds the verified evidence; **UNSUPPORTED** — no verified evidence. "Corr." refers to Section 8.

| ID | Line | Claim (abridged) | Citation(s) | Evidence basis | Status | Corr. |
|---|---:|---|---|---|---|---|
| B01 | 11–15 | Chapter scope; npm boundary; cross-ecosystem work is context; attacks not performed. | — | Chapter 1 §1.8; LC20; AGENTS scope | CONTEXT_ONLY (accurate) | — |
| B02 | 23 | Code hallucination is "the subject of dedicated systematic literature reviews". | Gao | LC01 (one SLR verified) | OVERSTATED (plural "reviews" supported by one citation) | C01 |
| B03 | 23 | Existence of reviews indicates an "established research concern rather than an occasional anomaly". | Gao; Woesle | LC01 (reliability concern) | SUPPORTED_WITH_QUALIFICATION ("occasional anomaly" contrast is rhetorical) | C01 |
| B04 | 23 | Code hallucination as a domain-specific manifestation of wider hallucination. | Gao; Woesle | Concept row; Woesle context only | SUPPORTED_WITH_QUALIFICATION (hedged "may"; acceptable) | — |
| B05 | 25 | "The literature does not suggest … inherently less reliable than code written by developers." | — | No source verified on human-vs-LLM comparison | UNSUPPORTED (literature-wide absence claim) | C02 |
| B06 | 25 | Code can be syntactically correct and plausible yet fail execution/requirements; execution verification proposed. | Tian | LC02 | DIRECTLY_SUPPORTED | — |
| B07 | 25 | Liu et al. frame hallucination beyond functional correctness and empirically categorise it. | Liu et al. (2026) | LC01; concept row | DIRECTLY_SUPPORTED | — |
| B08 | 25 | Kind of check determines which errors are observable. | Tian; Liu | LC11, LC15 | SUPPORTED_WITH_QUALIFICATION (synthesis; acceptable) | — |
| B09 | 27 | Code conforms to formal syntax and external constraints. | — | General technical statement | CONTEXT_ONLY | — |
| B10 | 27 | Related work on not treating code as natural language (repository level) and on API misuse. | Le-Anh; Zhuo | Metadata (titles) | SUPPORTED_WITH_QUALIFICATION (topic-level only) | — |
| B11 | 27 | These strands "direct attention to … files, interfaces, and libraries whose existence … the model cannot guarantee". | Le-Anh; Zhuo (implied) | Metadata only | OVERSTATED (attributes content to metadata-only sources) | C03 |
| B12 | 29 | Spracklen state probabilistic generation contributes to output diversity; examined repetition and temperature. | Spracklen | LC13 | DIRECTLY_SUPPORTED | — |
| B13 | 29 | A single response provides limited evidence; studies need repetition, fixed conditions, preserved outputs. | — (inference from Spracklen) | LC13 constraint: "finding of that design, not a universal causal law" | SUPPORTED_WITH_QUALIFICATION (hedged "may"; framed as implication; acceptable) | — |
| B14 | 31 | Related work on reliable, trustworthy, explainable LLM coding for production. | Dubey and Madisetti | Metadata (title) | SUPPORTED_WITH_QUALIFICATION (topic-level; acceptable) | — |
| B15 | 31 | "The general point that emerges from this literature" — validation is an explicit activity. | Dubey and Madisetti (adjacent) | LC02/LC15 support the point; metadata source does not | SUPPORTED_WITH_QUALIFICATION (must be anchored to verified sources) | C04 |
| B16 | 35 | Code hallucination "is used in the literature for" content presented as valid but unsupported by context or external reality. | — | Concept row: no universal definition; wording mirrors Chapter 1's *study-specific* working definition | OVERSTATED (study definition presented as uncited literature usage) | C05 |
| B17 | 35 | No single universal definition; Gao reviews characterisation, causes, detection/evaluation, mitigation, challenges. | Gao | LC01; concept row; approved title | DIRECTLY_SUPPORTED | — |
| B18 | 35 | Related work on code hallucination generally and security-related code hallucination. | Agarwal; Daoud | Metadata (titles) | SUPPORTED_WITH_QUALIFICATION (topic-level; acceptable) | — |
| B19 | 35 | General LLM-hallucination literature is backdrop but does not itself define code/dependency hallucination. | Woesle | Woesle safe for broad context only | SUPPORTED_WITH_QUALIFICATION (acceptable) | — |
| B20 | 37 | "Across these sources, there is broad agreement" on two points. | Gao; Liu; Tian; Agarwal; Daoud; Woesle (implied) | Only Gao/Liu/Tian verified | OVERSTATED (agreement claim sweeps in metadata-only sources) | C06 |
| B21 | 37 | Hallucinated content presented "in the same fluent, confident form as correct content". | — | LC02 supports "syntactically correct and plausible"; "confident" not verified | OVERSTATED | C06 |
| B22 | 37 | Gao organises conceptually; Liu derives categories from generated code; Tian uses execution. | Gao; Liu; Tian | LC01, LC02, LC11 | DIRECTLY_SUPPORTED | — |
| B23 | 37 | Detection method determines visible errors; external-entity errors need external evidence. | — | LC11, LC15 | SUPPORTED_WITH_QUALIFICATION (synthesis; acceptable) | — |
| B24 | 39 | Library hallucinations studied in developer-query setting; package hallucination for registry-distributed packages. | Twist; Spracklen | LC07, LC10 | DIRECTLY_SUPPORTED | — |
| B25 | 41 | Three carried-forward considerations (definition, method-dependence, external state). | — | LC11, LC12 | SUPPORTED_WITH_QUALIFICATION (acceptable; does not pre-empt 2.9) | — |
| B26 | 49 | Developers commonly incorporate third-party OSS components. | — | LC03 ("no universal dependency count") | CONTEXT_ONLY (no count used; acceptable) | — |
| B27 | 49 | OSS dependencies/components are a context through which attacks can be attempted. | Ladisa; Williams | LC03, LC04 | DIRECTLY_SUPPORTED | — |
| B28 | 51 | Ladisa taxonomy "organising the ways in which the integrity of open-source components and the processes that produce and distribute them may be compromised". | Ladisa | LC04 records only "taxonomises OSS supply-chain attacks" | OVERSTATED (internal organisation of the taxonomy not recorded in verification) | C07 |
| B29 | 51 | Williams identify dependencies as one attack vector. | Williams | LC04 ("identifies dependency attack vectors") | DIRECTLY_SUPPORTED | — |
| B30 | 51 | Duan measure supply-chain attacks on interpreted-language package managers. | Duan | LC04 | DIRECTLY_SUPPORTED | — |
| B31 | 51 | The three works "agree" that component-acquisition mechanisms are an object of security analysis. | Ladisa; Williams; Duan | LC04 | SUPPORTED_WITH_QUALIFICATION (synthesis; acceptable) | — |
| B32 | 51 | Related work has systematised practical detection of supply-chain attacks. | Ohm and Stuke | Metadata (title "SoK: Practical Detection…") | SUPPORTED_WITH_QUALIFICATION (topic-level; acceptable) | — |
| B33 | 51 | Supply-chain perspective extended "to the components and processes surrounding LLMs themselves". | Wang | Metadata (title) | SUPPORTED_WITH_QUALIFICATION (slightly interpretive; optional simplification R1) | R1 |
| B34 | 53 | Supply-chain literature "establishes" dependencies are not neutral and consequences depend on context. | Ladisa; Williams | LC16 = SUPPORTED_WITH_QUALIFICATION | OVERSTATED (verb "establishes" exceeds a qualified claim) | C08 |
| B35 | 55 | Cited taxonomic/agenda work addresses attacks broadly rather than names specifically; study does not examine wider threats. | Ladisa; Williams | LC04; AGENTS scope | SUPPORTED_WITH_QUALIFICATION (acceptable) | — |
| B36 | 59 | Package managers resolve names against registries; meaning determined by registry state at resolution time. | — | General technical description; consistent with Chapter 1 | CONTEXT_ONLY | — |
| B37 | 61 | Duan: registries abused to distribute malicious packages; metadata/static/dynamic analysis. | Duan | LC04, LC15; concept row | DIRECTLY_SUPPORTED | — |
| B38 | 61 | Registry presence does not establish benignity/safety. | Duan; Spracklen | LC12 ("registry presence does not establish safety") | DIRECTLY_SUPPORTED | — |
| B39 | 63 | Spracklen cross-referenced generated names against registry information for Python and JavaScript. | Spracklen | LC12, LC14; concept row | DIRECTLY_SUPPORTED | — |
| B40 | 63 | "Such work establishes that registry comparison is an established means…" | Spracklen | One verified study | OVERSTATED (assertive verb and "established" from one study) | C09 |
| B41 | 63 | Registry comparison alone not shown sufficient to classify every reference. | Spracklen | LC12 | SUPPORTED_WITH_QUALIFICATION (acceptable; defers to 2.6) | — |
| B42 | 65 | npm is Node.js's ecosystem; scoped/unscoped names, subpaths, built-ins, local modules; normalisation in Chapter 3. | — | Study/context definitions (final_paper_notes normalisation rules; AGENTS) | CONTEXT_ONLY (correctly uncited; recommended shortening R2) | R2 |
| B43 | 67 | "The approved literature reviewed here does not provide verified evidence" for registry-policy causal claims. | — | Accurate as to content; wording exposes internal process | SUPPORTED_WITH_QUALIFICATION (wording correction required) | C10 |
| B44 | 69 | Name errors may cause failure, wrong component, or third-party opportunity. | — | Hedged analytical statement; LC09/LC16 | CONTEXT_ONLY (acceptable) | — |
| B45 | 75 | Typosquatting and dependency confusion are "two of the most frequently discussed techniques". | — | No frequency evidence verified | UNSUPPORTED | C11 |
| B46 | 79 | Typosquatting definition: adversary publishes resembling name; users mistype/misread. | Al-Zofi | LC05; concept row | DIRECTLY_SUPPORTED | — |
| B47 | 79 | Spracklen treat similar-name attacks as package confusion, separately from fictitious names. | Spracklen | LC05 | DIRECTLY_SUPPORTED | — |
| B48 | 79 | Defining features: intentional adversarial registration and resemblance to a legitimate name. | Al-Zofi; Spracklen | LC05 | DIRECTLY_SUPPORTED | — |
| B49 | 81 | Similar generated names "are better understood as name confusion than as fabrication". | — | Analytical; anticipates Chapter 3 taxonomy | SUPPORTED_WITH_QUALIFICATION (should be hedged) | C12 |
| B50 | 81 | A confused generated name "becomes part of a typosquatting attack only if" an adversary registered it and a user retrieves it. | — | LC05 concept row: typosquatting is defined by *human* mistyping/misreading; a model-originated name is not within the verified definition | OVERSTATED (extends the verified definition to model output) | C12 |
| B51 | 85 | Dependency confusion: public registration of an internal name; resolution selects public version. | Al-Zofi | LC06; concept row | DIRECTLY_SUPPORTED | — |
| B52 | 85 | "…a package manager configured to consult both sources…" | Al-Zofi | LC06 does not record configuration detail | SUPPORTED_WITH_QUALIFICATION (mechanism detail beyond evidence summary) | C13 |
| B53 | 87 | Dependency confusion distinct from typosquatting and package hallucination; direct support from Al-Zofi only. | Al-Zofi | LC06; concept-row constraint | DIRECTLY_SUPPORTED | — |
| B54 | 87 | Registry absence does not indicate dependency confusion; "may equally reflect" other explanations. | — | LC12; AGENTS | SUPPORTED_WITH_QUALIFICATION ("equally" implies equal likelihood; optional R4) | R4 |
| B55 | 91 | Duan measured malicious-package distribution through registries with combined analyses. | Duan | LC04, LC15 | DIRECTLY_SUPPORTED | — |
| B56 | 91 | Ladisa and Williams place dependency attacks within a broader OSS supply-chain threat landscape. | Ladisa; Williams | LC04 | DIRECTLY_SUPPORTED | — |
| B57 | 91 | "Name-based deception should be understood as one route among several by which dependency-related compromise may be attempted." | Duan; Ladisa; Williams | Verification records breadth, not that the taxonomy positions name-based attacks among other routes | OVERSTATED | C14 |
| B58 | 91 | Consequences of a dependency error depend on context (which package, by whom, controls, behaviour). | Duan; Ladisa; Williams | LC16 (Ladisa, Williams, Spracklen) | SUPPORTED_WITH_QUALIFICATION (acceptable; retained in C14) | — |
| B59 | 93 | Three categories: accidental error ("developer or tool"), adversarial naming, package hallucination ("may not correspond"). | Spracklen; Zhao | LC07; concept row | OVERSTATED / imprecise (categories overlap; literature definition weakened; "defined by the source" omits non-existence criterion) | C15 |
| B60 | 93 | Spracklen: package hallucination = recommends/references non-existent package; Zhao: LLMs recommend non-existent packages. | Spracklen; Zhao | LC07 | DIRECTLY_SUPPORTED | — |
| B61 | 95 | Slopsquatting = malicious registration of LLM-hallucinated names. | Al-Zofi | LC08; concept row | DIRECTLY_SUPPORTED | — |
| B62 | 95 | Spracklen present a comparable scenario (adversary registers; user installs). | Spracklen | LC08, LC09 | DIRECTLY_SUPPORTED ("comparable" correctly avoids attributing the term to Spracklen) | — |
| B63 | 95 | Attack requires additional conditions; hallucinated name is not an attack or compromise; reliability defect. | Al-Zofi; Spracklen | LC08, LC09 | DIRECTLY_SUPPORTED | — |
| B64 | 99–107 | Table 2.1 | Al-Zofi; Spracklen; Zhao | See Section 4 | REQUIRES CORRECTION | C16 |
| B65 | 109 | Non-resolution compatible with several explanations; only "never published" corresponds straightforwardly to literature package hallucination; none is an attack. | — | LC07, LC12; Chapter 1 §1.3 | SUPPORTED_WITH_QUALIFICATION (acceptable analytical statement) | — |
| B66 | 109 | Resolving name does not establish it is the intended package or safe. | Spracklen | LC12 (safety); "intended" is logical | SUPPORTED_WITH_QUALIFICATION (acceptable) | — |
| B67 | 111 | Study did not register, reserve, publish, install, execute, or simulate attacks. | — | Chapter 1 §1.2, §1.8; AGENTS | CONTEXT_ONLY (accurate study statement) | — |

**Claim-status totals (67 rows; each row carries exactly one status):**

- DIRECTLY_SUPPORTED **23** — B06, B07, B12, B17, B22, B24, B27, B29, B30, B37, B38, B39, B46, B47, B48, B51, B53, B55, B56, B60, B61, B62, B63.
- SUPPORTED_WITH_QUALIFICATION **23** — B03, B04, B08, B10, B13, B14, B15, B18, B19, B23, B25, B31, B32, B33, B35, B41, B43, B49, B52, B54, B58, B65, B66.
- CONTEXT_ONLY **7** — B01, B09, B26, B36, B42, B44, B67.
- OVERSTATED **11** — B02, B11, B16, B20, B21, B28, B34, B40, B50, B57, B59.
- UNSUPPORTED **2** — B05, B45.
- Table 2.1 (B64) — audited separately in Section 4 (**1**).

---

## 4. Table 2.1 verification

### 4.1 Row-by-row audit of the draft table

| Row | Definition source-supported? | Actor/intent accurate? | Registry involvement accurate? | Relationship to LLM output accurate? | Consequence too strong? | Status |
|---|---|---|---|---|---|---|
| Typosquatting | YES — Al-Zofi (LC05); Spracklen (similar-name package confusion). | YES — adversary; intentional. | Implicit only ("registers"); acceptable but not explicit. | NOT STATED — the table has no LLM column; the reviewed definition attributes the triggering error to human mistyping/misreading, which the table should make explicit. | No consequence claimed. | MINOR CORRECTION |
| Dependency confusion | YES — Al-Zofi only (LC06). | YES — adversary; intentional. | YES — public registration; resolution selects public over internal. | NOT STATED — should state that it is not defined by LLM output and that the name need not be erroneous. | No. | MINOR CORRECTION |
| Accidental dependency error | Analytical category, correctly labelled as not literature-derived. | YES — no adversary. | Not stated. | **INACCURATE BY OMISSION** — "Developer or tool" overlaps with package hallucination: an LLM is a tool, and an LLM-generated mis-scoped or misspelled name is both "accidental" and LLM-originated. The distinguishing criterion (an intended legitimate package exists) is missing. | No. | CORRECTION REQUIRED |
| Package hallucination | PARTLY — Spracklen and Zhao define it as reference/recommendation of a package that **does not exist** (LC07); the draft's "may not correspond to a legitimate package" weakens the literature definition, and "Mechanism" repeats the definition. | YES — no adversary at generation. "No (at generation)" is ambiguous; clearer as "No adversary involved in producing the name". | Not stated; should record that the literature definition turns on non-existence, while this study's confirmation rule is separate (Chapter 3). | YES — LLM-originated; table does **not** imply it is an attack. | No. | CORRECTION REQUIRED |
| Slopsquatting | YES — Al-Zofi (LC08); Spracklen scenario (LC08/LC09). | YES — downstream adversary. | Implicit ("registers"). | YES — downstream of a hallucination. Should state explicitly that it is a potential scenario not implied by the hallucination. | No; "Relies on a user or process acting" correctly conditional. | MINOR CORRECTION |

### 4.2 Distinction checks

- **Typosquatting vs package hallucination:** preserved in prose (lines 79–81) and table. The prose at line 81 extends "typosquatting" to model-originated names; corrected by C12.
- **Dependency confusion vs package hallucination:** preserved (lines 85–87).
- **Accidental dependency error vs package hallucination:** **not cleanly separated** (line 93 and table row). Corrected by C15/C16.
- **Package hallucination vs slopsquatting:** preserved; the table and line 95 correctly state that slopsquatting requires adversary registration and user/process action.
- **Package hallucination as an attack:** the draft table does **not** imply that package hallucination itself is an attack ("No (at generation)"). The corrected table makes this explicit in the LLM-relationship column.

**Table 2.1 status: REQUIRES MINOR CORRECTION** — replace with the table in C16.

---

## 5. Ladisa-specific findings

Verified evidence for Ladisa et al. (2023) in `chapter2_source_verification.md` is limited to: "discuss OSS dependencies/components as a supply-chain attack surface" (LC03); "taxonomises OSS supply-chain attacks" (LC04); "supply-chain papers address attack paths" (LC16); and the concept-row constraint "broad OSS/package-manager attack context … do not infer compromise". No recorded evidence describes the internal organisation of the taxonomy or states which specific attack categories (including naming attacks) it contains.

**A. Description of the taxonomy (line 51).** "Ladisa et al. (2023) systematise attacks on open-source software supply chains in the form of a taxonomy" is DIRECTLY_SUPPORTED. The continuation "organising the ways in which the integrity of open-source components and the processes that produce and distribute them may be compromised" describes the taxonomy's organising principle, which is **not recorded** in the verification evidence. Verdict: **OVERSTATED — weaken** (C07).

**B. "One route among several" (line 91).** The verified evidence supports that Ladisa, Williams, and Duan address supply-chain attacks broadly, at a level wider than package naming (and line 55 of the draft already says so correctly). It does **not** record that Ladisa's taxonomy positions name-based deception as one of several routes, nor that these works jointly make that comparative claim. The sentence is an author synthesis presented as what the works "suggest". Verdict: **OVERSTATED — weaken** to a statement that the threat landscape these works describe extends beyond the naming techniques reviewed, without attributing a specific taxonomic placement (C14). The following sentence (context-dependent consequences) is supportable under LC16 and is retained.

Other Ladisa uses (lines 49, 53, 91 second clause) are within LC03/LC04/LC16, subject to C08 ("establishes" → "indicates") at line 53.

---

## 6. Metadata-only citation audit

| Reference | Line | Draft use | Conservative topic/context only? | Detailed finding / causal / numeric / definition / comparison? | Verdict |
|---|---:|---|---|---|---|
| Agarwal et al. (2024) | 35 | "related work has examined hallucinations in LLM-generated code more generally" | YES | None in its own sentence. **Indirect:** line 37 "Across these sources, there is broad agreement…" sweeps it into an agreement claim. | PASS after C06 |
| Daoud (2026) | 35 | "as well as security-related code hallucinations specifically" | YES | Same indirect sweep at line 37. | PASS after C06 |
| Le-Anh et al. (2026) | 27 | "implications of not treating code as natural language for repository-level code generation" | YES | **Indirect:** line 27 final sentence says these strands "direct attention to … files, interfaces, and libraries", which attributes content. | PASS after C03 |
| Zhuo et al. (2025) | 27 | "identification and mitigation of API misuse by LLMs" | YES | Same indirect attribution at line 27. | PASS after C03 |
| Dubey and Madisetti (2026) | 31 | "approaches intended to make LLM-based coding more reliable, trustworthy, and explainable for production systems" | YES — no effectiveness claim | **Indirect:** next sentence "The general point that emerges from this literature" can be read as resting on this metadata-only source. | PASS after C04 |
| Ohm and Stuke (2023) | 51 | "systematised the practical detection of software supply-chain attacks" | YES | None. | PASS |
| Wang et al. (2025) | 51 | "extended to the components and processes surrounding LLMs themselves in a proposed research agenda" | YES — broadly | "components and processes surrounding" is a mild interpretation beyond the title; not a finding. | PASS (optional R1) |

No metadata-only reference is the sole support for a number, a definition, a causal conclusion, or a comparison. The three indirect issues are corrected by C03, C04, and C06.

**Cross-chapter observation (outside this block; no action taken):** `chapter1_complete_draft.md` line 32 co-cites Ohm and Stuke (2023) with Al-Zofi (2025) and Duan et al. (2020) for "Registry lookup and static dependency analysis have been described in the literature as approaches for examining package references before installation". `chapter2_source_verification.md` §13 item 1 requires full text before Ohm and Stuke is used for static/dynamic detection claims. The claim remains supported by the co-cited full-text sources, but the researcher may wish to review whether Ohm and Stuke should remain in that Chapter 1 citation group.

---

## 7. Technical-description findings (Section 2.3.2)

Line 65 describes scoped/unscoped names, subpaths, Node.js built-ins, and local modules without citation, and line 59 describes name resolution against registry state without citation.

- **Presentation:** Appropriate. Neither passage is attributed to the literature; line 65 introduces them as "descriptive features of npm" and states that "the specific normalisation rules applied in this dissertation are described in Chapter 3". No citation should be invented for them; none of the approved sources was verified for npm naming mechanics.
- **Accuracy:** The descriptions are consistent with the implemented normalisation rules recorded in `docs/final_paper_notes.md` (strip import subpaths to the package root; distinguish scoped from unscoped; exclude Node.js built-ins, `node:` references, and local/relative/absolute paths) and with `AGENTS.md`.
- **Placement:** The four-feature enumeration is study-operational and belongs more naturally in Chapter 3 (package normalisation). In a literature review it reads as methodology. **Recommendation R2:** shorten line 65 to a two-sentence bridge that names the issue and defers details to Chapter 3 (exact wording in Section 8). This is recommended, not required, because the passage is already correctly framed and uncited.
- Line 59 ("the meaning of a dependency declaration … is determined by the state of the registry at the time the name is resolved") is general technical context consistent with Chapter 1 and needs no change.

---

## 8. Required corrections with exact replacement wording

Sixteen corrections (C01–C16) are **required**. Four further items (R1–R4) are **recommended** and may be applied at the researcher's discretion.

### C01 — Line 23 (plural SLRs from one citation; rhetorical contrast)

**Replace:**
> The research response to this capability has been extensive enough that hallucinations in LLM-generated code have become the subject of dedicated systematic literature reviews [Gao et al., 2025], alongside broader systematic reviews of hallucination in LLMs generally [Woesle et al., 2025]. The existence of these reviews indicates that the reliability of generated code is regarded as an established research concern rather than an occasional anomaly.

**With:**
> Hallucinations in LLM-generated code have become the subject of a dedicated systematic literature review [Gao et al., 2025], alongside broader systematic reviews of hallucination in LLMs generally [Woesle et al., 2025]. The existence of such reviews indicates that the reliability of generated code is treated as an established research concern.

### C02 — Line 25 (unsupported literature-wide absence and human comparison)

**Replace:**
> The literature does not suggest that generated code is uniformly unreliable, nor that it is inherently less reliable than code written by developers. Its emphasis falls instead on the observation that the fluency of generated code is not a sufficient indicator of its correctness.

**With:**
> The studies reviewed here do not characterise generated code as uniformly unreliable. Their emphasis falls instead on the observation that the plausibility of generated code is not a sufficient indicator of its correctness.

### C03 — Line 27 (content attributed to metadata-only sources)

**Replace:**
> These strands of research are relevant here because they direct attention to the points at which generated code depends on entities outside the immediate text of the response—files, interfaces, and libraries—whose existence and behaviour the model cannot guarantee from its output alone.

**With:**
> These strands of research are noted here as context. Their relevance to the present study lies in a more general observation: generated code frequently depends on entities outside the immediate text of the response—files, interfaces, and libraries—whose existence and behaviour cannot be confirmed from the generated output alone.

### C04 — Line 31 (general point anchored to a metadata-only source)

**Replace:**
> The general point that emerges from this literature is that validation of generated code is an explicit activity with its own design choices, rather than a property that can be assumed from the generating model.

**With:**
> The execution-based and review literature discussed above [Tian et al., 2025; Gao et al., 2025] indicates that validation of generated code is an explicit activity with its own design choices, rather than a property that can be assumed from the generating model.

### C05 — Line 35 (study definition presented as uncited literature usage)

**Replace:**
> The term *code hallucination* is used in the literature for generated code, or generated statements about code, that are presented as valid but are not supported by the relevant programming context or external reality. The reviewed studies do not converge on a single universal definition.

**With:**
> Chapter 1 adopted a study-specific working definition of hallucination as generated software output presented as valid but not supported by the relevant external reality. The reviewed studies do not converge on a single universal definition of *code hallucination*.

### C06 — Line 37 (agreement claim sweeping in metadata-only sources; "confident" unverified)

**Replace:**
> Across these sources, there is broad agreement on two points. The first is that hallucination in code is a reliability concern: it affects whether a generated solution can be used as supplied. The second is that hallucinated content may be difficult to recognise by inspection because it is presented in the same fluent, confident form as correct content.

**With:**
> Two points recur across the studies whose full findings are discussed here [Gao et al., 2025; Liu et al., 2026; Tian et al., 2025]. The first is that hallucination in code is a reliability concern: it affects whether a generated solution can be used as supplied. The second is that hallucinated content may not be evident from surface inspection, because generated code can be syntactically correct and plausible while failing to execute or to satisfy the task requirements [Tian et al., 2025].

### C07 — Line 51 (Ladisa taxonomy description; Ladisa concern A)

**Replace:**
> Ladisa et al. (2023) systematise attacks on open-source software supply chains in the form of a taxonomy, organising the ways in which the integrity of open-source components and the processes that produce and distribute them may be compromised.

**With:**
> Ladisa et al. (2023) systematise attacks on open-source software supply chains in the form of a taxonomy.

### C08 — Line 53 (assertive verb for a qualified claim)

**Replace:**
> First, it establishes that a dependency is not a neutral detail of an implementation:

**With:**
> First, it indicates that a dependency is not a neutral detail of an implementation:

**And replace:**
> Second, it establishes that the consequences of a dependency choice depend on the surrounding context,

**With:**
> Second, it indicates that the consequences of a dependency choice depend on the surrounding context,

### C09 — Line 63 (overstatement from one study)

**Replace:**
> Such work establishes that registry comparison is an established means of gathering evidence about generated dependency references.

**With:**
> Such work indicates that registry comparison is a recognised means of gathering evidence about generated dependency references.

### C10 — Line 67 (internal process language in dissertation prose)

**Replace:**
> However, the approved literature reviewed here does not provide verified evidence on which to base causal claims about how particular registry naming or publication policies determine the frequency of package-name errors.

**With:**
> However, the literature reviewed in this chapter does not provide evidence on which to base causal claims about how particular registry naming or publication policies determine the frequency of package-name errors.

### C11 — Line 75 (unsupported frequency claim)

**Replace:**
> This section reviews two of the most frequently discussed techniques, typosquatting and dependency confusion,

**With:**
> This section reviews two techniques that the reviewed literature distinguishes explicitly, typosquatting and dependency confusion,

### C12 — Line 81 (typosquatting extended to model-originated names; unhedged classification)

**Replace:**
> Such cases are better understood as name confusion than as fabrication, and they are relevant to classification because they have a different relationship to the ecosystem from a name with no legitimate counterpart. Second, resemblance alone does not establish that an attack has taken place. A mistyped or confused name in generated code is an error in the output; it becomes part of a typosquatting attack only if an adversary has registered the resembling name and a user retrieves the resulting package.

**With:**
> Such cases may be better understood as name confusion than as fabrication, and they are relevant to classification because they have a different relationship to the ecosystem from a name with no legitimate counterpart. Second, resemblance alone does not establish that an attack has taken place. A mistyped or confused name in generated code is an error in the output; it acquires security significance only if an adversary has registered the resembling name and a user or automated process retrieves the resulting package.

### C13 — Line 85 (mechanism detail beyond the evidence summary)

**Replace:**
> so that a package manager configured to consult both sources resolves the dependency to the public version rather than to the intended internal one.

**With:**
> so that package resolution selects the public version rather than the intended internal one.

### C14 — Line 91 ("one route among several"; Ladisa concern B)

**Replace:**
> Read together, these works suggest that name-based deception should be understood as one route among several by which dependency-related compromise may be attempted, rather than as the whole of dependency risk. They also indicate that the consequences of any particular dependency error depend on context—on which package is retrieved, by whom, under what controls, and with what subsequent behaviour.

**With:**
> Because these works address software supply-chain attacks at a broader level than package naming, they indicate that the threat landscape extends beyond the naming-based techniques reviewed in Sections 2.4.1 and 2.4.2. They also indicate that the consequences of any particular dependency error depend on context—on which package is retrieved, by whom, under what controls, and with what subsequent behaviour [Ladisa et al., 2023; Williams et al., 2025].

### C15 — Line 93 (overlapping categories; weakened literature definition)

**Replace:**
> The first is *accidental dependency error*: a developer or tool cites a package incorrectly—for example, by using an outdated name, the wrong scope, or a misremembered spelling—without any adversary being involved. The second is *adversarial package naming*: an attacker deliberately arranges for a name to resolve to a malicious component, as in typosquatting or dependency confusion. The third is *package hallucination*: an LLM generates a dependency reference naming a package that may not correspond to any legitimate package. Spracklen et al. (2025) use the term package hallucination for the case in which generated code recommends or references a package that does not exist, and Zhao et al. (2025) similarly describe LLMs recommending non-existent packages. Package hallucination is thus defined by the source of the erroneous name—the model's output—rather than by the actions of an attacker.

**With:**
> The first is *accidental dependency error*: a developer or tool, which may include an LLM, cites an intended legitimate package incorrectly—for example, by using an outdated name, the wrong scope, or a misremembered spelling—without any adversary being involved. The second is *adversarial package naming*: an attacker deliberately arranges for a name to resolve to a malicious component, as in typosquatting or dependency confusion. The third is *package hallucination*: Spracklen et al. (2025) use the term for the case in which generated code recommends or references a package that does not exist, and Zhao et al. (2025) similarly describe LLMs recommending non-existent packages. Package hallucination is thus defined by two features—the name originates in model output, and the referenced package does not exist—rather than by the actions of an attacker. The boundary between the first and third categories is not always evident from the name alone, because model output may also contain mis-scoped or misspelled references to real packages; how this boundary was operationalised in the present study is described in Chapter 3.

### C16 — Lines 99–107 (Table 2.1)

**Replace the table caption and table with:**

> **Table 2.1: Package-naming concepts distinguished in the reviewed literature**
>
> | Concept | Origin of the problematic name | Adversarial action required? | Registry involvement | Relationship to LLM output | Principal supporting literature |
> |---|---|---|---|---|---|
> | Typosquatting | A user mistypes or misreads a legitimate package name | Yes — prior registration of a name resembling a legitimate package | Adversary publishes a package under the resembling name | Not defined by LLM output; the reviewed definition attributes the triggering error to human mistyping or misreading | Al-Zofi (2025); Spracklen et al. (2025) |
> | Dependency confusion | An internal package name, used as intended | Yes — public registration of the internal name | Resolution selects the public package rather than the intended internal one | Not defined by LLM output; the name need not be erroneous | Al-Zofi (2025) |
> | Accidental dependency error | A developer or tool, which may include an LLM, cites an intended legitimate package incorrectly (e.g., outdated, mis-scoped, or misspelled name) | No | The name as written may fail to resolve, or may resolve to an unintended package | May occur in LLM output; defined by the existence of an intended legitimate package rather than by the source of the name | Analytical category used in this review |
> | Package hallucination | Generated code recommends or references a package that does not exist | No adversary is involved in producing the name | The referenced package does not exist | Defined by LLM output; a reliability defect, not in itself an attack | Spracklen et al. (2025); Zhao et al. (2025) |
> | Slopsquatting | A name previously hallucinated by an LLM | Yes — downstream malicious registration of the hallucinated name | Adversary publishes a package under the hallucinated name; harm additionally requires a user or process to act on the reference | Downstream of LLM output; a potential attack scenario that exploits a hallucinated name but is not implied by it | Al-Zofi (2025); Spracklen et al. (2025) |
>
> *Note.* The package-hallucination row states the definition used in the cited literature. The present study's conservative confirmation and adjudication rules, under which registry absence alone is not sufficient, are defined in Chapter 3.

### Recommended (optional) items

**R1 — Line 51 (Wang wording).** Replace "and the supply-chain perspective has been extended to the components and processes surrounding LLMs themselves in a proposed research agenda [Wang et al., 2025]" with "and a research agenda has applied the supply-chain perspective to LLMs themselves [Wang et al., 2025]".

**R2 — Line 65 (shorten study-operational npm description).** Replace from "Several descriptive features of npm are relevant…" to "…which external package, if any, it denotes." with:
> Because npm package names may be scoped, imports may refer to subpaths within a package, and generated code may also refer to Node.js built-in modules or local files, the text of a generated import or installation instruction cannot simply be equated with an npm package name.

Retain the following sentence ("The specific normalisation rules applied in this dissertation are described in Chapter 3.").

**R3 — Repeated scope disclaimers.** The "not attacks / not performed / npm only" boundary is stated in 2.1 (line 15), 2.3.1 (line 55), 2.3.2 (line 67), 2.4.2 (line 87), 2.4.3 (line 95), and again in full at line 111. Consider shortening line 111 to its first sentence plus "Section 2.5 turns from these naming threats to the empirical literature on package hallucination itself." Line 15 and line 95 already carry the substance.

**R4 — Line 87.** Replace "it may equally reflect a name that was never published" with "it may also reflect a name that was never published" (avoids implying equal likelihood).

---

## 9. References still unused after Sections 2.1–2.4

Sixteen approved references remain uncited. Planned locations follow `chapter2_reference_coverage_plan.md`.

| Reference | Verification level | Planned section |
|---|---|---|
| Gandhi (2026) | METADATA_ONLY | 2.7 (resolved; cite as Gandhi (2026) only) |
| Jain et al. (2025) | METADATA_ONLY | 2.7 |
| AlSobeh et al. (2025) | METADATA_ONLY | 2.7 |
| Li et al. (2026) | METADATA_ONLY | 2.7 |
| Lian et al. (2024) | METADATA_ONLY | 2.6 |
| Liu (2026) | METADATA_ONLY | 2.7 |
| Liu et al. (2025a) | METADATA_ONLY | 2.8 |
| Liu et al. (2025b) | METADATA_ONLY | 2.7 |
| Pashchenko et al. (2022) | METADATA_ONLY | 2.7 |
| Qu et al. (2026) | METADATA_ONLY | 2.7 |
| Tileria et al. (2026) | METADATA_ONLY | 2.6 |
| Tripathi et al. (2025) | METADATA_ONLY | 2.7 |
| Washio and Miyao (2022) | METADATA_ONLY | 2.7 |
| Yadav et al. (2026) | METADATA_ONLY | 2.7 |
| Yang et al. (2026) | METADATA_ONLY | 2.6 |
| Zheng et al. (2026) | METADATA_ONLY | 2.8 |

All 11 full-text-verified references are already cited. All 16 remaining references are metadata-only, so each must receive a single conservative topic-level use. Section 2.7 is allocated 12 of the 16 (including Gandhi); it will need care to avoid a citation-dumping paragraph (coverage plan §9).

---

## 10. Bibliographic-rule check

| Rule | Result |
|---|---|
| Gandhi not yet cited | CONFIRMED — 0 occurrences of "Gandhi". |
| No "Gandhi (2025)" / "Gandhi, 2025" | CONFIRMED — 0 occurrences. |
| No "Spracklen (2024)" / "Spracklen et al., 2024" | CONFIRMED — all 12 Spracklen occurrences read "2025". |
| No "Ohm et al. (2020)" | CONFIRMED — the single Ohm occurrence is "Ohm and Stuke, 2023". |
| Approved forms used consistently | CONFIRMED — author/year pairs match the approved list; "Liu et al. (2026)" is correctly distinguished from Liu (2026) and Liu et al. (2025a/b); two-author forms ("Dubey and Madisetti", "Ohm and Stuke") match. Narrative citations use Author (year); parenthetical citations use [Author, year], consistent with Chapter 1. |
| "et al." vs approved label "et. al." | The draft uses "et al." throughout, consistent with Chapter 1. The approved list's bracketed labels use "et. al."; this is a label-format artefact of the baseline, not a bibliographic difference. Final bibliography formatting should apply one form under the University author-year style. No change required in this block. |
| Numeric claims | None present (no percentages or counts attributed to literature). |

---

## 11. Synthesis-quality findings

- **Synthesis vs catalogue:** Largely synthetic. Section 2.2.2 (line 37) and Section 2.3.1 (line 51) compare sources by method rather than summarising them one by one. Section 2.4 is organised by concept, not by paper. No paper-by-paper catalogue was found.
- **Citation dumping:** None. The densest sentence (line 51) cites five sources across three sentences, each with a distinct role.
- **Repetition:** The scope and non-attack disclaimers recur six times (R3). Lines 53 and 91 make overlapping context-dependence points; C14 adds the citation to line 91 and keeps them distinct (line 53: general; line 91: naming threats).
- **Chapter 3 material:** The npm naming/normalisation enumeration at line 65 (R2), and the four-explanation list at line 109, preview the Chapter 3 taxonomy. Line 109 is acceptable because it is framed conceptually and is needed to interpret Table 2.1. Line 111 restates methodology already stated in Chapter 1 §1.8 (R3).
- **Premature research-gap claims:** None found. Lines 41 and 109 state methodological requirements ("must state its own operational definition"; "reinforces the need… for explicit operational definitions") without claiming a gap or novelty. They are appropriate foundations for Section 2.9 and should not be restated verbatim there.
- **Section numbering against the protocol:** The draft follows the coverage-plan structure (2.1–2.10), not the illustrative structure in `report_generation_protocol.md` §18 (which says exact titles may be adjusted). No action required.

---

## 12. Readiness decision

**READY_AFTER_CORRECTIONS**

Sections 2.5–2.10 may be drafted once C01–C16 are applied to `docs/report_drafts/chapter2_sections_2_1_to_2_4.md`. Corrections C12, C15, and C16 are the most important for later sections, because Section 2.5 will build directly on the package-hallucination, name-confusion, and slopsquatting distinctions. R1–R4 are optional.

Constraints carried forward to 2.5–2.10:

1. Do not re-cite Dubey and Madisetti (2026) or Ohm and Stuke (2023) as independent support for stronger claims.
2. Place the remaining 16 metadata-only references once each, at topic level only; avoid a 12-citation list in 2.7.
3. Any Spracklen, Twist, or Duan number must carry its full context from `chapter2_source_verification.md` §10; no other number is permitted.
4. Section 2.5 must reuse the corrected C15/C16 definitions and must not describe slopsquatting as observed.
5. Section 2.9 must not claim novelty, priority, or literature absence.

## 13. Milestone assessment

- Progress-log update needed: **YES** (Chapter 2 Block 1 verification milestone). Appendable text provided below. It has not been applied because this task did not authorise it.
- Final-paper note needed: **NO** (no methodological or scope decision changed).
- Draft reconciliation needed: **YES** (C01–C16 must be applied to the Block 1 draft before 2.5–2.10 are drafted).

Appendable progress-log Markdown:

```markdown
### 2026-09-23 — Chapter 2 Block 1 verification (Sections 2.1–2.4)

- Created `docs/final_report_support/chapter2_block1_verification.md` (CHAPTER-2-BLOCK-1-VERIFICATION-01).
- Verdict: PASS WITH MINOR CORRECTIONS; readiness: READY_AFTER_CORRECTIONS.
- An independent count confirmed 18 of 34 approved references cited (11 of 11 full-text-verified; 7 metadata-only). Sixteen metadata-only references remain unused.
- 67 claims checked: 23 directly supported, 23 supported with qualification, 7 context-only, 11 overstated, 2 unsupported, plus Table 2.1 audited separately.
- 16 required wording corrections (C01–C16), including a weakened Ladisa et al. (2023) taxonomy description, removal of the unverified "one route among several" synthesis, separation of accidental dependency error from package hallucination, and a corrected Table 2.1. Four optional recommendations (R1–R4).
- No Gandhi, Spracklen 2024, or Ohm et al. 2020 citation; no numeric claim; no dissertation result stated.
- No reference was added. No frozen or experimental file was modified. No result was calculated. The draft itself was not edited.
```
