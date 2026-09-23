# Chapter 2 Source Verification - CHAPTER-2-SOURCE-VERIFICATION-01

## 1. Verification method

This document verifies the existing approved-reference set only. Repository inspection found no locally stored source papers beyond the baseline dissertation. For priority sources, the approved DOI, title, or approved source URL was used to locate the same work; no new academic reference was added. Full texts were inspected where an openly accessible paper PDF was available. A title, index record, or abstract was never treated as direct support for a detailed finding.

Levels mean: **FULL_TEXT_VERIFIED** = source paper text inspected; **ABSTRACT_ONLY** = source-authored abstract inspected but no full text; **METADATA_ONLY** = only the approved entry/index metadata was checked; **UNAVAILABLE** = no usable source material located. “Direct” support below means the reported claim follows from the inspected source’s own stated design/result; it does not transfer the claim to this dissertation.

All numeric values were checked against their original reported population where possible. The final study’s Node.js/npm definitions, PHR/SHR, DFR/RDFR, and classification requirements remain implementation rules, not literature-derived definitions.

## 2. Source availability and verification-level table

| Approved reference | Verification level | Evidence located / verification note |
|---|---|---|
| Agarwal et al. (2024) | METADATA_ONLY | Approved DOI/title checked; no source text inspected in this task. |
| Al-Zofi (2025) | FULL_TEXT_VERIFIED | Research Square PDF inspected. |
| Daoud (2026) | METADATA_ONLY | Approved metadata only. |
| Duan et al. (2020) | FULL_TEXT_VERIFIED | NDSS paper PDF inspected. |
| Dubey and Madisetti (2026) | METADATA_ONLY | Approved metadata only. |
| Gandhi (2026) | METADATA_ONLY | Approved metadata only; baseline’s year mismatch remains unresolved. |
| Gao et al. (2025) | FULL_TEXT_VERIFIED | arXiv full-text PDF inspected. |
| Jain et al. (2025) | METADATA_ONLY | Approved metadata only. |
| Zhao et al. (2025) | FULL_TEXT_VERIFIED | arXiv full-text PDF for the same titled HFuzzer work inspected. |
| AlSobeh et al. (2025) | METADATA_ONLY | Approved metadata only. |
| Ladisa et al. (2023) | FULL_TEXT_VERIFIED | Open author-hosted paper PDF inspected. |
| Le-Anh et al. (2026) | METADATA_ONLY | Approved metadata only. |
| Li et al. (2026) | METADATA_ONLY | Approved metadata only. |
| Lian et al. (2024) | METADATA_ONLY | Approved metadata only. |
| Liu (2026) | METADATA_ONLY | Approved metadata only. |
| Liu et al. (2025a) | METADATA_ONLY | Approved metadata only. |
| Liu et al. (2025b) | METADATA_ONLY | Approved metadata only. |
| Liu et al. (2026) | FULL_TEXT_VERIFIED | arXiv full-text paper corresponding to *Beyond Functional Correctness* inspected; approved bibliography metadata remains as recorded. |
| Ohm and Stuke (2023) | METADATA_ONLY | Conference/index metadata located; no full text or source abstract inspected. |
| Pashchenko et al. (2022) | METADATA_ONLY | Approved metadata only. |
| Qu et al. (2026) | METADATA_ONLY | Approved metadata only. |
| Spracklen et al. (2025) | FULL_TEXT_VERIFIED | USENIX/arXiv paper PDF inspected. |
| Tian et al. (2025) | FULL_TEXT_VERIFIED | AAAI paper PDF inspected. |
| Tileria et al. (2026) | METADATA_ONLY | Approved metadata only. |
| Tripathi et al. (2025) | METADATA_ONLY | Approved metadata only. |
| Twist et al. (2026) | FULL_TEXT_VERIFIED | arXiv full-text paper inspected. |
| Wang et al. (2025) | METADATA_ONLY | Approved metadata only. |
| Washio and Miyao (2022) | METADATA_ONLY | Approved metadata only. |
| Williams et al. (2025) | FULL_TEXT_VERIFIED | Author-hosted full-text PDF inspected. |
| Woesle et al. (2025) | FULL_TEXT_VERIFIED | Open full text inspected. |
| Yadav et al. (2026) | METADATA_ONLY | Approved metadata only. |
| Yang et al. (2026) | METADATA_ONLY | Approved metadata only. |
| Zheng et al. (2026) | METADATA_ONLY | Approved metadata only. |
| Zhuo et al. (2025) | METADATA_ONLY | Approved metadata only. |

Totals: **34 source-checked records; 11 FULL_TEXT_VERIFIED; 0 ABSTRACT_ONLY; 23 METADATA_ONLY; 0 UNAVAILABLE.**

## 3. Claim-by-claim source verification

The claim IDs are those in `chapter2_literature_synthesis.md`. Safe wording is a drafting constraint, not Chapter 2 prose.

| Claim ID | Claim | Reference | Verification Level | Evidence Summary | Status | Safe Chapter 2 Wording |
|---|---|---|---|---|---|---|
| LC01 | LLM-generated code can contain hallucinated or unreliable elements. | Gao et al. (2025); Liu et al. (2026) | FULL_TEXT_VERIFIED | Gao reviews code-oriented hallucination, causes, detection and evaluation; Liu empirically categorises hallucinations in generated code. | DIRECTLY_SUPPORTED | Code-hallucination research treats hallucination as a reliability concern in LLM-generated code. |
| LC02 | Code hallucination may survive superficial/syntax-oriented checks. | Tian et al. (2025) | FULL_TEXT_VERIFIED | CodeHalu states that syntactically correct, plausible code may not execute or fulfil requirements and uses execution verification. | DIRECTLY_SUPPORTED | Execution-based work shows that syntactic plausibility alone is not a sufficient correctness check. |
| LC03 | Third-party dependencies make dependency references relevant. | Ladisa et al. (2023); Williams et al. (2025) | FULL_TEXT_VERIFIED | Both discuss OSS dependencies/components as a supply-chain attack surface. | SUPPORTED_WITH_QUALIFICATION | Open-source dependencies are a relevant supply-chain security context; do not state an unverified universal dependency count. |
| LC04 | Package managers/registries create supply-chain exposure. | Duan et al. (2020); Ladisa et al. (2023); Williams et al. (2025) | FULL_TEXT_VERIFIED | Duan analyses registry abuse; Ladisa taxonomises OSS supply-chain attacks; Williams identifies dependency attack vectors. | DIRECTLY_SUPPORTED | Package registries and dependencies can be relevant surfaces for software supply-chain attacks. |
| LC05 | Typosquatting is distinct from package hallucination. | Al-Zofi (2025); Spracklen et al. (2025) | FULL_TEXT_VERIFIED | Al-Zofi defines typosquatting as a similar-name attack rooted in human mistyping/misreading; Spracklen describes similar-name package confusion attacks separately from fictitious names. | DIRECTLY_SUPPORTED | Typosquatting involves resemblance to a legitimate name and should be distinguished from an LLM-invented package name. |
| LC06 | Dependency confusion is distinct from package hallucination. | Al-Zofi (2025) | FULL_TEXT_VERIFIED | Al-Zofi describes public registration of an internal package name with public-version resolution; its slopsquatting discussion attributes a different trigger to LLM hallucination. | DIRECTLY_SUPPORTED | Dependency confusion concerns public/private namespace resolution and is distinct from a generated nonexistent-name claim. |
| LC07 | Package-name hallucination is a dependency-reference manifestation of code hallucination. | Spracklen et al. (2025); Zhao et al. (2025) | FULL_TEXT_VERIFIED | Spracklen defines it as code recommending/referencing a package that does not exist; HFuzzer describes LLM recommendation of non-existent packages. | DIRECTLY_SUPPORTED | Prior work uses package hallucination for non-existent package recommendations/references in generated code. |
| LC08 | Slopsquatting is downstream malicious use of hallucinated names. | Al-Zofi (2025); Spracklen et al. (2025) | FULL_TEXT_VERIFIED | Al-Zofi identifies malicious registration of a hallucinated name; Spracklen presents it as an attack scenario dependent on adversary registration and user installation. | SUPPORTED_WITH_QUALIFICATION | Slopsquatting is a potential downstream attack scenario, not an automatic consequence of a hallucinated name. |
| LC09 | Hallucinated names are not equivalent to confirmed exploitation. | Spracklen et al. (2025) | FULL_TEXT_VERIFIED | The paper’s attack model requires additional conditions: adversary registration and a user installing the package. | DIRECTLY_SUPPORTED | A hallucinated package name is a reliability finding; exploitation requires additional attacker and adoption conditions. |
| LC10 | Package hallucination has been studied empirically. | Spracklen et al. (2025); Zhao et al. (2025); Twist et al. (2026) | FULL_TEXT_VERIFIED | Each reports empirical LLM/library/package-hallucination evaluation. | DIRECTLY_SUPPORTED | Empirical studies have examined package or library hallucinations under defined settings. |
| LC11 | Definitions, validation rules, settings, and outcomes differ across studies. | Spracklen; Zhao; Tian; Twist | FULL_TEXT_VERIFIED | The inspected studies use different ecosystems, prompt/task generation, units, and operational criteria (registry/package references, fuzzing, execution, imports/members). | DIRECTLY_SUPPORTED | Reported rates should be compared only with attention to differing constructs, validation procedures, and study designs. |
| LC12 | Registry absence alone may be insufficient to classify hallucination. | Spracklen; Twist | FULL_TEXT_VERIFIED | Spracklen notes registry presence does not establish safety; Twist normalises names and excludes valid explicit versions to avoid over-counting. Neither supplies the final study’s full adjudication taxonomy. | SUPPORTED_WITH_QUALIFICATION | Registry evidence is informative but must be interpreted using an explicit operational rule; Chapter 3 defines this study’s conservative adjudication. |
| LC13 | Repetition/non-determinism matter. | Spracklen et al. (2025) | FULL_TEXT_VERIFIED | The study explicitly examines repetition/persistence and states that probabilistic generation contributes to diverse outputs; it varies temperature. | DIRECTLY_SUPPORTED | Prior package-hallucination research examined repeated outputs and model-setting variation. |
| LC14 | Model, task, and ecosystem differences are relevant comparison dimensions. | Spracklen; Tian; Twist | FULL_TEXT_VERIFIED | Spracklen compares 16 models, Python/JavaScript and settings; Tian evaluates multiple models; Twist varies prompts across seven models. | DIRECTLY_SUPPORTED | Model, prompt/task, and ecosystem choices are relevant boundaries for interpreting reported outcomes. |
| LC15 | Registry/reference checking, static analysis, and execution-based validation exist. | Duan; Zhao; Tian; Twist | FULL_TEXT_VERIFIED | Duan uses metadata/static/dynamic analyses; HFuzzer tests generated tasks; Tian uses execution; Twist extracts imports and validates against PyPI/documentation. | DIRECTLY_SUPPORTED | Prior work uses multiple validation approaches, including registry/reference and execution-based checks. |
| LC16 | Practical/security consequences vary by context. | Ladisa; Williams; Spracklen | FULL_TEXT_VERIFIED | Supply-chain papers address attack paths; Spracklen’s compromise scenario requires conditions beyond a name. | SUPPORTED_WITH_QUALIFICATION | Consequences depend on the surrounding dependency, registry, attacker, and user-adoption context. |
| LC17 | Broad “no prior research” novelty assertions are unsupported. | Spracklen; Zhao; Twist | FULL_TEXT_VERIFIED | Multiple empirical package/library-hallucination studies exist. | DIRECTLY_SUPPORTED | Do not claim the topic is unexplored or that this dissertation is first. |
| LC18 | Mitigation/grounding approaches exist. | Spracklen; Gao; Tian; Twist | FULL_TEXT_VERIFIED | Sources discuss/test mitigation or validation directions, but their efficacy differs by method and setting. | SUPPORTED_WITH_QUALIFICATION | Related work proposes mitigation/validation approaches; this dissertation did not evaluate one. |
| LC19 | Agentic systems are a broader distinct context. | Gandhi; Qu; Yadav | METADATA_ONLY | Titles suggest relevance, but no source text was inspected and Gandhi’s baseline year differs from approved metadata. | NOT_VERIFIABLE | Omit from substantive Chapter 2 unless source text and citation identity are verified. |
| LC20 | Cross-ecosystem literature can contextualise an npm-only experiment. | Spracklen; Duan; Twist | FULL_TEXT_VERIFIED | The sources cover Python/JavaScript/interpreted-language or Python settings; they do not make this study multi-ecosystem. | DIRECTLY_SUPPORTED | Cross-ecosystem work supplies context; the present empirical boundary remains Node.js/npm. |

Claim totals: **DIRECTLY_SUPPORTED 14; SUPPORTED_WITH_QUALIFICATION 5; NOT_SUPPORTED 0; NOT_VERIFIABLE 1.**

## 4. Numeric-claim verification

| Numeric Claim | Source | Exact Source Evidence Found? | Population/Context | Final Action |
|---|---|---|---|---|
| Up to 97% developer generative-AI use | Al-Zofi (2025) | Reported second-hand; no original approved source verified | Adoption statistic cited by the review, not this study | REMOVE_NUMBER |
| Approximately 30% AI-generated code | Al-Zofi (2025) | Reported second-hand; no original approved source verified | Adoption statistic cited by the review | REMOVE_NUMBER |
| Up to 85% under temporal/low-frequency prompts | Twist et al. (2026) | Yes | Up to 84.74% task hallucination rate for a specified 2025 time-based prompt in a Python-library experiment across seven LLMs | USE_ONLY_WITH_CONTEXT |
| 2.23m packages; 5.2% commercial versus 21.7% open-source | Spracklen et al. (2025) | Yes | 2.23m recommended packages across 30 tests; rates are the study’s commercial/open-source aggregates | USE_ONLY_WITH_CONTEXT |
| 39.02% retrieval-related correctness drop | Jain et al. (2025) | No | Full text not verified | UNVERIFIED |
| 43.66% match-metric misclassification | Lian et al. (2024) | No | Full text not verified | UNVERIFIED |
| 15.8% Python; 21.3% JavaScript | Spracklen et al. (2025) | Yes | Average package-hallucination rate in that paper’s Python/JavaScript evaluations | USE_ONLY_WITH_CONTEXT |
| 19.7% across 576,000 samples | Spracklen et al. (2025) | Yes, with correction | 440,445 of 2.23m recommended packages (19.7%); 576,000 is the number of code samples, not the package denominator | USE_ONLY_WITH_CONTEXT |
| Average 180 dependencies | Ohm and Stuke (2023) | No | No source text verified | UNVERIFIED |
| 33.5% static-defense bypass | Qu et al. (2026) | No | No source text verified | UNVERIFIED |
| 2.5% complete evasion | Qu et al. (2026) | No | No source text verified | UNVERIFIED |
| 0.02 self-verification recall | Woesle et al. (2025) | No | Inspected review does not establish the baseline’s asserted value in verified evidence | REMOVE_NUMBER |
| Nearly 3.4m active npm packages | Al-Zofi (2025) | No | Not found in inspected full text; also time-sensitive | REMOVE_NUMBER |
| 82% flagged-dependency removal | Duan et al. (2020) | Yes | 278 of 339 malicious packages reported by MALOSS were confirmed by maintainers | USE_ONLY_WITH_CONTEXT |
| 6,705 npm invalid fabrications; 0 Maven | Spracklen et al. (2025) | No | Not established in inspected source text as stated | REMOVE_NUMBER |
| 90.7% explicit injection interception | Qu et al. (2026) | No | No source text verified | UNVERIFIED |
| 94.8% static lookup detection | Al-Zofi (2025) | No | Not found in inspected review PDF | REMOVE_NUMBER |
| 82% confirmation/removal across 339 packages | Duan et al. (2020) | Yes | Same MALOSS result: 278/339, as above | USE_ONLY_WITH_CONTEXT |
| 8.1% repair; 4.0% test-pass improvement | Li et al. (2026) | No | Full text not verified | UNVERIFIED |
| 61.18% to 16.64% error-rate reduction | Liu et al. (2025b) | No | Full text not verified | UNVERIFIED |
| 38.58% to 47.94% valid invocation | Jain et al. (2025) | No | Full text not verified | UNVERIFIED |

## 5. Concept/definition verification

| Concept | Verified source support | Constraint |
|---|---|---|
| Code hallucination | Tian identifies code that can be syntactically plausible yet fail execution/requirements; Liu provides code-hallucination categories; Gao reviews code-specific hallucination. | No single universal definition should be claimed. |
| Package hallucination | Spracklen: code recommends or references a package that does not exist; Zhao uses non-existent package recommendations. | This literature definition does not replace the dissertation’s conservative confirmation/adjudication rule. |
| Typosquatting | Al-Zofi defines a similar-name package attack induced by human mistyping/misreading; Spracklen treats it as a package-confusion technique. | Definition is directly supported by Al-Zofi, a review. |
| Dependency confusion | Al-Zofi defines public registration of an internal package name where resolution selects the public version. | Direct support presently comes from Al-Zofi only. |
| Slopsquatting | Al-Zofi defines malicious registration of LLM-hallucinated names; Spracklen provides a package-confusion attack scenario. | Present as a conditional downstream attack context, not as a hallucination synonym. |
| Supply-chain/package-manager risk | Ladisa, Duan, and Williams directly support a broad OSS/package-manager attack context. | Do not infer compromise from a registry lookup or generated name. |
| Registry/package validation | Twist validates extracted imports against PyPI with normalisation; Spracklen cross-references package names; Duan uses metadata analysis. | Registry existence does not establish safety; this study’s classification is separately defined. |
| Static/execution validation | Duan covers metadata/static/dynamic analysis; Tian proposes execution verification; Twist performs source-level import/documentation validation. | The present study did not execute generated code or dependencies. |
| Non-determinism/repetition | Spracklen examines repeated hallucinations and varies temperature. | Safe as a finding of that design, not a universal causal law. |
| Model/task/ecosystem variation | Spracklen, Tian, and Twist each vary relevant dimensions. | Compare studies only after stating each study’s construct and conditions. |

## 6. Research-gap verification

### A. Literature-supported

- Empirical package/library-hallucination work exists (Spracklen; Zhao; Twist).
- Code-hallucination work uses different operationalisations, including execution verification, package/import validation, and fuzzing-generated tasks (Tian; Spracklen; Zhao; Twist).
- Model, prompt/task, and ecosystem settings differ among inspected studies, so rates are not directly interchangeable without their definitions and denominators.
- Existing work includes detection/validation and mitigation directions; absence claims about methods are unsupported.

### B. Implementation-based study rationale

- This dissertation’s value proposition is its defined Node.js/npm scope, frozen conditions, response provenance, direct-reference extraction, read-only npm evidence, conservative adjudication, and separation of confirmed package-name hallucination from secondary exact-name dependency failure.
- These are implemented-design facts, not claims that the literature lacks every component or that the study is first.

### C. Unsupported / remove

- “No prior work exists,” “first study,” “package hallucination is unexplored,” or “no detection methods exist.”
- Any claim that one unverified baseline percentage represents the field or the final study population.
- Any claim that the present study observes slopsquatting, exploitation, installation, maliciousness, or loss.
- Any agentic-autonomy paragraph based on Gandhi, Qu, or Yadav until the source text and Gandhi citation identity are verified.

## 7. References safe for direct Chapter 2 use

For the narrow claims documented above: **Spracklen et al. (2025), Al-Zofi (2025), Gao et al. (2025), Ladisa et al. (2023), Duan et al. (2020), Williams et al. (2025), Zhao et al. (2025), Tian et al. (2025), Liu et al. (2026), Woesle et al. (2025), and Twist et al. (2026).**

Direct use is limited to the verified evidence summaries and must retain any stated study context. Woesle is safe for broad LLM-hallucination-review context, not the unverified baseline 0.02 value.

## 8. References safe only with qualification

Spracklen, Al-Zofi, Duan, Tian, Twist, and Liu may support carefully scoped empirical examples, but their rates, ecosystems, definitions, interventions, and task designs must be reported with context. Al-Zofi is a systematic review/preprint and should not be used to transform a cited statistic into a general adoption claim. Cross-ecosystem results are context only, never evidence that Java/Maven, PyPI, or Python were performed-study ecosystems.

## 9. References not usable without further evidence

All METADATA_ONLY references in Section 2 are not usable for detailed findings. Highest-priority unresolved items are **Ohm and Stuke (2023)** (detection claims), **Jain et al. (2025)** (all performance figures), **Lian et al. (2024)** (metric figure), **Qu et al. (2026)** (attack/bypass figures), **Li et al. (2026)** and **Liu et al. (2025b)** (mitigation figures), and **Gandhi (2026)** (bibliographic mismatch with the baseline’s Gandhi 2025 citation).

## 10. Approved numeric claims

No number is approved for unqualified reuse. The following are usable only with the source’s full context and only if needed for synthesis:

- Spracklen: 5.2% commercial and 21.7% open-source aggregate package-hallucination rates in its reported 30-test, 2.23m-recommended-package evaluation.
- Spracklen: 15.8% average for Python and 21.3% for JavaScript in that paper’s evaluation.
- Spracklen: 19.7% (440,445/2.23m recommended packages), while 576,000 denotes its code-sample count.
- Twist: up to 84.74% task hallucination rate under a specified time-based Python-library prompt condition; “up to 85%” is a rounded description and must retain its prompt/task context.
- Duan: 278 of 339 reported malicious packages confirmed by maintainers (82%) in the MALOSS study.

Numeric-audit totals by the 21 baseline claim rows: **SAFE_TO_USE 0; USE_ONLY_WITH_CONTEXT 6 (including the repeated Duan 82% claim); REMOVE_NUMBER or UNVERIFIED 15.**

## 11. Numeric claims that must be removed

Remove or leave unverified all remaining numeric claims in Section 4: 97%; 30%; 39.02%; 43.66%; 180; 33.5%; 2.5%; 0.02; 3.4m; 6,705/0; 90.7%; 94.8%; 8.1%/4.0%; 61.18%/16.64%; and 38.58%/47.94%. Also remove the baseline’s inaccurate framing of 19.7% “across 576,000 samples”: the full Spracklen paper uses 2.23m recommended packages as the rate denominator.

## 12. Final Chapter 2 drafting constraints

- **READY_WITH_RESTRICTED_CLAIMS.** Eleven full-text sources support a substantive, bounded Chapter 2; do not force the remaining 23 metadata-only sources into prose.
- Use direct, non-numeric context on code hallucination, package hallucination, supply-chain risk, naming-attack distinctions, and differing validation approaches.
- Attribute every numeric comparison to its original study population, ecosystem, model set, task/prompt design, and outcome definition; use none unless it adds analytical value.
- Define the final study’s npm classification and PHR/SHR/DFR/RDFR solely from repository evidence and decisions, not literature shorthand.
- Describe slopsquatting as a possible downstream scenario requiring additional conditions. Do not report it as a performed study activity or observed outcome.
- Do not state literature-wide absence/priority claims, and omit agentic framing unless the unverified sources are checked.
- Remain within the approved 34-reference set.

## 13. Open verification issues

1. Obtain full text for Ohm and Stuke before using it for static/dynamic detection claims.
2. Verify Jain, Lian, Qu, Li, and Liu et al. (2025b) before using any baseline effectiveness or benchmark number.
3. Resolve the Gandhi 2025/2026 mismatch and the baseline’s Spracklen 2024 and Ohm et al. 2020 citation mismatches through the approved-reference process.
4. Verify whether Woesle contains the baseline 0.02 assertion; it was not established in this source review.
5. Retain the current restricted-claim verdict until any additional sources are inspected.
