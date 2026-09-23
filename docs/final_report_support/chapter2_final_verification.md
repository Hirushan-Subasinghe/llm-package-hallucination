# Chapter 2 Final Verification — CHAPTER-2-ASSEMBLY-AND-FINAL-VERIFICATION-01

## 1. Final verdict

**PASS**

The complete chapter was mechanically assembled from the three verified and corrected blocks. The only assembly edit removed one duplicated metadata-only-context sentence in Section 2.7. No citation, table cell, experimental file, frozen file, or result claim was changed.

## 2. Structural verification

The assembled draft contains the required top-level headings, in order: 2.1; 2.2 with 2.2.1--2.2.2; 2.3 with 2.3.1--2.3.2; 2.4 with 2.4.1--2.4.3; 2.5 with 2.5.1--2.5.3; 2.6 with 2.6.1--2.6.3; 2.7 with 2.7.1--2.7.3; 2.8 with 2.8.1--2.8.5; 2.9 with 2.9.1--2.9.4; and 2.10. Heading numbering and ordering are correct. Table 2.1 and Table 2.2, including their notes, are retained.

## 3. Citation-coverage verification

An independent scan of the assembled chapter finds **34/34 approved references**, with no unapproved reference. The final in-text reference list is:

1. Agarwal et al. (2024)
2. Al-Zofi (2025)
3. Daoud (2026)
4. Duan et al. (2020)
5. Dubey and Madisetti (2026)
6. Gandhi (2026)
7. Gao et al. (2025)
8. Jain et al. (2025)
9. Zhao et al. (2025)
10. AlSobeh et al. (2025)
11. Ladisa et al. (2023)
12. Le-Anh et al. (2026)
13. Li et al. (2026)
14. Lian et al. (2024)
15. Liu (2026)
16. Liu et al. (2025a)
17. Liu et al. (2025b)
18. Liu et al. (2026)
19. Ohm and Stuke (2023)
20. Pashchenko et al. (2022)
21. Qu et al. (2026)
22. Spracklen et al. (2025)
23. Tian et al. (2025)
24. Tileria et al. (2026)
25. Tripathi et al. (2025)
26. Twist et al. (2026)
27. Wang et al. (2025)
28. Washio and Miyao (2022)
29. Williams et al. (2025)
30. Woesle et al. (2025)
31. Yadav et al. (2026)
32. Yang et al. (2026)
33. Zheng et al. (2026)
34. Zhuo et al. (2025)

Citation-form checks pass: Gandhi appears only as **Gandhi (2026)**; Gandhi (2025), Spracklen (2024), and Ohm et al. (2020) do not appear. Liu et al. (2025a) remains a single, explicitly non-transferable contextual use for code-change-to-natural-language generation; Zheng et al. (2026) remains a single Rust-crate contextual use.

## 4. Metadata-only audit

All 23 metadata-only references are used only at topic, title, or related-work level. They are not assigned a numerical result, measured effectiveness, causal conclusion, prevalence, comparative outcome, or measured security outcome. In particular, the agentic-development paragraph identifies Gandhi, Qu, Yadav, and Tripathi as topic-level context and explicitly says that no empirical finding about those settings is drawn. Liu et al. (2025a) and Zheng et al. (2026) retain their explicit scope boundaries.

## 5. Table 2.1 verification

**PASS.** The table correctly preserves actor/intent, registry involvement, and relationship to LLM output for typosquatting, dependency confusion, accidental dependency error, package hallucination, and slopsquatting. Package hallucination is a model-output reliability defect, not an attack. Slopsquatting remains a downstream adversarial-registration scenario. The note correctly defers the dissertation's conservative operational confirmation and adjudication rules to Chapter 3.

## 6. Table 2.2 verification

**PASS.** Every populated cell remains within the verified study-design record. The Zhao and Tian rows retain dashes rather than inferred ecosystem, task, or model-condition detail. The note identifies the table as a limited comparison of study designs and expressly excludes numerical-result comparison or ranking.

## 7. Whole-chapter repetition and cohesion

The chapter deliberately reinforces the package-hallucination definition, its non-attack status, registry time-boundedness, and the Node.js/npm scope where those concepts perform different functions: definition, security interpretation, validation/classification, comparison, and research-gap rationale. No additional cross-block removal is warranted.

The transitions 2.4 -> 2.5, 2.7 -> 2.8, 2.8 -> 2.9, and 2.9 -> 2.10 are coherent. The assembled chapter reads as one literature review, rather than as three unconnected blocks.

## 8. Chapter 1 consistency

**PASS.** Chapter 2 is consistent with Chapter 1's Node.js/npm-only empirical scope; conservative confirmed package-name hallucination construct; separation of broader dependency failures; primary PHR/SHR and secondary/exploratory DFR/RDFR; conditional supply-chain framing; bounded research gap; and rule-based practical-risk framing. It neither reintroduces Java/Maven experiments nor represents installation, active exploitation, or package registration as performed. It does not alter the dissertation title.

## 9. Chapter 3 boundary

**PASS.** Chapter 2 provides only an appropriate high-level rationale for standardised Node.js/npm tasks, frozen conditions, controlled collection, extraction/normalisation, registry evidence, conservative adjudication, the primary/secondary measures, and the practical-risk framework. Detailed operational mechanics remain deferred to Chapter 3. The removed execution-safety rationale has not been reintroduced.

## 10. Numeric, result, and novelty check

**PASS.** No unverified numeric literature claim, dissertation result, model/category ranking, significance result, or risk distribution occurs. The word “unexplored” occurs only in an explicit rejection of that novelty claim. The chapter contains no first-study, no-prior-work, or unsupported unique-method claim.

## 11. Word-count summary

| Section | Words |
|---|---:|
| 2.1 | 408 |
| 2.2 | 1,276 |
| 2.3 | 1,255 |
| 2.4 | 1,752 |
| 2.5 | 1,972 |
| 2.6 | 1,470 |
| 2.7 | 1,507 |
| 2.8 | 1,703 |
| 2.9 | 1,448 |
| 2.10 | 395 |
| **Complete file total** | **13,192** |

At Times New Roman 12 pt with 1.5 line spacing, headings, and the two tables, this is approximately **32--36 pages**. No reduction is recommended solely to meet an approximate page target.

## 12. Exact correction made during assembly

One clearly duplicated sentence was removed from the Section 2.7 agentic-development context paragraph.

**Before:**

> These works are cited as topic-level context only. They provide topic-level context for broader discussions of AI-assisted and agentic development. Autonomous or agentic operation was not a variable in the present study, and no empirical finding about such settings is drawn from these sources.

**After:**

> These works are cited as topic-level context only. Autonomous or agentic operation was not a variable in the present study, and no empirical finding about such settings is drawn from these sources.

## 13. Word-readiness

**READY_FOR_WORD**

Milestone assessment: progress-log update **NO**; final-paper note update **NO**; draft reconciliation update **NO**.
