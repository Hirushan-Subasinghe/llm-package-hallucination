# Final Chapter 1 Verification — FINAL-CHAPTER-1-VERIFICATION-01

**Verification date:** 2026-09-23  
**Draft reviewed:** `docs/report_drafts/chapter1_complete_draft.md`  
**Method:** Repository-only verification against the controlling study documents, frozen-design records, taxonomy, risk protocol, analysis specification, and baseline dissertation. No web search, result calculation, or frozen/experimental-file modification was performed.

## 1. Verification Verdict

**PASS WITH MINOR CORRECTIONS**

The chapter accurately represents the implemented Node.js/npm study, preserves the dissertation title, uses the controlling outcome hierarchy, and does not state final findings. One wording correction is required to avoid implying that final practical-risk scoring has already been performed.

## 2. Study-Design Claim Verification

| Claim | Chapter location | Repository evidence | Status | Required action |
|---|---|---|---|---|
| Dissertation title is unchanged. | Title block | Draft-reconciliation §2; claims matrix CH1-013; baseline title page | VERIFIED | None |
| Empirical scope is Node.js/npm. | 1.1, 1.2, 1.8 | D001; claims matrix CH1-001; v2.6 task/freeze records | VERIFIED | None |
| Scope is explicit, direct package/dependency references. | 1.2, 1.8 | Taxonomy Scope Controls; analysis specification §§2–3; claims matrix CH1-001 | VERIFIED | None |
| The design has 30 final tasks. | 1.8 | Task-set design; v2.6 freeze; claims matrix CH1-002 | VERIFIED | None |
| Tasks span six functional categories. | 1.8 | Task-set design; v2.6 freeze; claims matrix CH1-003 | VERIFIED | None |
| “Medium difficulty” is task-set metadata, not independent validation. | 1.8 | D013; task-set design; evidence audit C1R-03 | VERIFIED | None |
| The design has four frozen model conditions. | 1.8 | Model-set configuration; v2.6 freeze; claims matrix CH1-004 | VERIFIED | None |
| Each task-condition combination has three planned repetitions. | 1.8 | v2.6 manifest/freeze; claims matrix CH1-005 | VERIFIED | None |
| The manifest contains 360 planned observations. | 1.8 | v2.6 manifest/freeze; claims matrix CH1-006 | VERIFIED | None |
| Collection is described as controlled. | 1.3, 1.4, 1.8, 1.10 | v2.6 freeze; current status; evidence audit §9 | VERIFIED | None |
| Package references are extracted and normalised. | 1.4, 1.8, 1.9 | Analysis specification §§2–3; taxonomy; PIPE-03 documentation | VERIFIED | None |
| npm validation is read-only. | 1.2, 1.4, 1.8, 1.9 | Taxonomy Analytical Stages/Scope Controls; current status; PIPE-04 documentation | VERIFIED | None |
| Classification and adjudication are conservative. | 1.2–1.4, 1.8–1.9 | Taxonomy Primary Outcome/Evidence; D037; PIPE-05/05B documentation | VERIFIED | None |
| Confirmed package-name hallucination requires an external npm reference and alternatives ruled out. | 1.3 | Taxonomy Primary Outcome; D037 confirmation guard; evidence audit C1R-05 | VERIFIED | None |
| npm `404`/`not_found` alone is insufficient. | 1.3 | Taxonomy; analysis specification §6; D037 | VERIFIED | None |
| Unresolved cases are not counted as confirmed hallucinations. | 1.3 | Taxonomy; D036–D037 | VERIFIED | None |
| PHR and SHR are primary measures. | 1.3, 1.6, 1.8–1.9 | D033, D037; taxonomy Metric Boundaries; claims matrix CH1-007 | VERIFIED | None |
| DFR/RDFR are secondary/exploratory and not hallucination rates. | 1.3, 1.6, 1.8–1.9 | D036; taxonomy Metric Boundaries; claims matrix CH1-008 | VERIFIED | None |
| Grouped comparisons are descriptive and, where estimable, statistical. | 1.3, 1.6–1.8 | Evidence audit §9; D036; PIPE-09 status | VERIFIED | None |
| Practical risk uses the Impact × Detectability model. | 1.6, 1.8–1.9 | D032; risk protocol; claims matrix CH1-009 | VERIFIED | None |
| Risk is restricted to eligible confirmed package-hallucination findings. | 1.1, 1.3, 1.5–1.9 | Risk protocol Eligibility; D032; evidence audit C1R-06 | VERIFIED, wording correction required | Replace the sentence identified in §5. |
| Explicit delimitations match the implemented study. | 1.8 | D001, D008, D009, D013, D015; taxonomy Scope Controls; risk protocol; final-paper notes; claims matrix CH1-010–CH1-012 | VERIFIED | None |
| No final result, rate, ranking, significance claim, or risk distribution is stated. | Title block; 1.1–1.11 | Current status; progress log; claims matrix CH1-014–CH1-016 | VERIFIED | None |
| No superseded SLR, autonomy-comparison, or mitigation-study framing remains. | 1.1–1.11, especially 1.6–1.10 | Draft reconciliation L–O; report protocol §§4, 7–9; D008, D009, D015 | VERIFIED | None |

## 3. Citation-Use Review

The chapter contains **22 individual citation uses**, reviewed in the following 15 source-and-sentence groups. All cited works are present in the approved-reference list. This review uses the Chapter 1 literature reconciliation only; it does not claim external source verification.

| Citation | Chapter location | Status | Notes |
|---|---|---|---|
| Gao et al. (2025) | 1.1 | SAFE | Supports the retained code-hallucination reliability context (L01). |
| Woesle et al. (2025) | 1.1 | SAFE | Supports the bounded statement that hallucination is a subject of systematic review. |
| Spracklen et al. (2025); Al-Zofi (2025) | 1.1 | SAFE | Supports package-hallucination context (L03). |
| Liu et al. (2026) | 1.2 | SAFE | Supports the retained AI-assisted-programming context (L02). |
| Dubey and Madisetti (2026) | 1.2 | SAFE | Supports the cited debugging/reliability context (L02). |
| Gao et al. (2025); Tian et al. (2025) | 1.2 | SAFE | Supports code-hallucination reliability context and execution-based verification context (L01–L02). |
| Ladisa et al. (2023); Duan et al. (2020); Williams et al. (2025) | 1.2 | SAFE_WITH_CAUTION | Used only for general supply-chain context; reconciliation L04 permits this with caution. |
| Spracklen et al. (2025); Al-Zofi (2025) | 1.2 | SAFE | Supports package-hallucination context (L03). |
| Al-Zofi (2025) | 1.2, typosquatting/dependency-confusion sentence | SAFE | Supports distinctions required by L05–L06. |
| Al-Zofi (2025) | 1.2, slopsquatting sentence | SAFE_WITH_CAUTION | Reconciliation L07 permits brief literature context only; the chapter correctly states that it is not the study’s attack activity. |
| Al-Zofi (2025); Duan et al. (2020); Ohm and Stuke (2023) | 1.2, registry/static-analysis sentence | SAFE_WITH_CAUTION | Reconciliation L15 supports the general validation-context claim; the study-specific interpretation is correctly methodological rather than attributed. |
| Spracklen et al. (2025) | 1.4 | SAFE_WITH_CAUTION | The sentence describes the cited work at a high level and does not import a prevalence claim; reconciliation requires continued caution for Chapter 1 gap claims. |
| Zhao et al. (2025) | 1.4 | SAFE_WITH_CAUTION | The sentence identifies it as package-hallucination testing context only; no effectiveness claim is made. |
| Al-Zofi (2025) | 1.4 | SAFE_WITH_CAUTION | Used as a high-level review/context statement only. |
| Ladisa et al. (2023); Williams et al. (2025) | 1.4 | SAFE_WITH_CAUTION | General supply-chain context only (L04); no literature-wide absence or novelty claim follows. |

No citation use is classified as `UNSUPPORTED`.

## 4. Terminology Consistency Findings

- **PHR / SHR:** Expanded once in 1.3 as Package Hallucination Rate and Sample Hallucination Rate, then used consistently as the primary measures.
- **DFR / RDFR:** Expanded once in 1.3 as Dependency Failure Rate and Response Dependency Failure Rate, then used consistently as secondary/exploratory dependency-resolution measures rather than hallucination rates.
- **Confirmed package-name hallucination:** Consistently distinguished from namespace confusion, package-name confusion, legacy/removed status, self/local references, and unresolved evidence.
- **Dependency-resolution failure:** Used consistently as the broader exact-name construct; it is not merged into the primary hallucination construct.
- **Model conditions / controlled collection protocol:** Consistent with the v2.6 study-design terminology. The chapter contains no obsolete autonomy/workflow condition.
- **Practical-risk framework / Impact × Detectability:** Consistent with `risk-model-1.0.0`, its post-classification sequencing, and its non-predictive purpose.

No inconsistent terminology variant was found. The one correction below is a tense/claim-boundary correction, not a terminology change.

## 5. Required Correction

**Location:** Section 1.8, final sentence of the second paragraph.

**Current sentence:**

> The implemented practical-risk assessment is applied only to eligible confirmed package-hallucination findings.

**Required replacement:**

> Under the implemented practical-risk framework, assessment is limited to eligible confirmed package-hallucination findings.

**Reason:** The risk protocol establishes eligibility and sequencing, but final v2.6 risk scoring has not been performed. The replacement preserves the verified methodological boundary without implying completed analysis.

## 6. Results and Superseded-Methodology Controls

**No final result was invented.** The chapter expressly retains `[FINAL RESULT PENDING]` and does not report a prevalence value, final denominator, model/category ranking, statistical result, risk distribution, or final hallucination count. The progress log and current status confirm that final v2.6 analysis has not been produced.

**No superseded methodology remains.** The chapter does not describe a final Java/Maven or PyPI experiment, human-participant/developer survey, developer-expertise variable, autonomous-agent or autocomplete comparison, verification mediator, package registration or installation, execution, slopsquatting attack, mitigation-system evaluation, predictive modelling, 70/30 split, Cohen’s Kappa analysis, expert validation, temporal holdout, or SLR as the study design. Such topics occur only as appropriately delimited literature context or future work.

## 7. Word-Readiness Decision

**READY AFTER MINOR CORRECTIONS**

Apply the single replacement in §5, then proceed to Word formatting. No broader Chapter 1 rewrite is required.

## 8. Milestone Documentation Assessment

- **Progress-log update needed:** NO — this is a report-verification artifact, not a research or collection milestone.
- **Final-paper note needed:** NO — the single wording correction is recorded in this verification report.
- **Draft reconciliation update needed:** NO — the verification confirms the existing reconciliation, subject only to the documented minor correction.
