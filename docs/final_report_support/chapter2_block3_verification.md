# Chapter 2 Block 3 Verification — CHAPTER-2-BLOCK-3-VERIFICATION-01

## 1. Verification verdict

**PASS WITH MINOR CORRECTIONS**

The block is evidence-aware, keeps the two metadata-only citations within their permitted contextual roles, contains no literature numbers or dissertation results, and separates the literature synthesis from the dissertation's design rationale. Five wording corrections are required before assembly, principally to remove absolutes in the comparative synthesis and Chapter 2 summary.

Milestone assessment:

- Progress-log update needed: **NO**.
- Final-paper note needed: **NO**.
- Draft reconciliation needed: **NO**.

## 2. Cumulative citation-coverage result

An independent cross-check of the three Chapter 2 drafts finds **34/34 approved references cited at least once**. Blocks 1 and 2 had covered 32; this block supplies the two planned remaining citations:

| Required check | Result |
|---|---|
| Liu et al. (2025a) | **One** occurrence, at 2.8.4. It is safely restricted to metadata-level context: code-change-to-natural-language generation and detection-metric evaluation; no dependency finding is transferred. |
| Zheng et al. (2026) | **One** occurrence, at 2.8.3. It is safely restricted to metadata-level cross-ecosystem/Rust-crate context; no Rust result, mitigation outcome, or applicability to npm is inferred. |
| Gandhi | **One** occurrence in the cumulative chapter, as **Gandhi (2026)** only (Section 2.7). |
| Spracklen (2024) | **Absent**. |
| Ohm et al. (2020) | **Absent**. |
| Unapproved reference | **None found**. |

The author--year forms are consistent with the approved set. The only non-substantive form variation is the expected narrative/parenthetical distinction (for example, `Spracklen et al. (2025)` and `[Spracklen et al., 2025]`). The approved-list label style `et. al.` versus draft style `et al.` is a baseline-list formatting artefact, not a reference anomaly. No duplicate citation-form anomaly requiring correction was found.

## 3. Section 2.8 claim verification

| Draft location / claim group | Classification | Verification finding |
|---|---|---|
| 2.8 opening: constructs, units, validation procedures, and conditions bound comparison | **DIRECTLY_SUPPORTED** | The verified studies differ in these dimensions; the scope is explicitly prior research. |
| 2.8.1 model sets and model-specific bounds | **SUPPORTED_WITH_QUALIFICATION** | Spracklen, Twist, and Tian support the differing evaluated-model designs. The inference that findings should be bounded by model identity is safe synthesis, provided it does not claim a measured cross-study model effect. |
| 2.8.1 repetition, probabilistic output diversity, and temperature | **DIRECTLY_SUPPORTED** | Correctly attributed to Spracklen et al. (2025); it makes no prevalence, ranking, or universal non-determinism claim. |
| 2.8.1 later version / different access conditions; changing serving conditions | **SAFE_AS_SYNTHESIS** | It is clearly identified as dissertation reasoning. Recording identity, settings, and responses is a defensible traceability rationale, not an attributed empirical result. |
| 2.8.2 task sources, task/domain variation | **SUPPORTED_WITH_QUALIFICATION** | Source-design descriptions are supported. Statements that task sources sample different request spaces and that domain effects may matter are safe analytical reasoning; no direction or magnitude is asserted. |
| 2.8.2 Twist time-related phrasing | **DIRECTLY_SUPPORTED** | The wording correctly limits the point to a varied condition in Twist's setting and transfers no effect. |
| 2.8.2 prompt wording must be held constant for comparison | **OVERSTATED** | Prompt wording must be reported and controlled or accounted for; it need not be held constant in every valid comparative design. Apply C01. |
| 2.8.2 time-bounded registry evidence | **SAFE_AS_SYNTHESIS** | Correctly framed as a time-bounded evidential condition, not a claim that models changed. |
| 2.8.3 multiple ecosystems and Zheng contextual use | **SUPPORTED_WITH_QUALIFICATION** | Spracklen, Twist, and Duan support the described settings; Zheng remains title/metadata context only. The conclusion that results do not automatically transfer is safe synthesis. |
| 2.8.3 ecosystem naming/import conventions and npm examples | **SAFE_AS_SYNTHESIS** | Explicitly labelled analytical reasoning and consistent with the earlier npm scope. It does not masquerade as a cited empirical result. |
| 2.8.4 construct, unit, validation, and classification differences | **DIRECTLY_SUPPORTED** | These differences are supported by the verified study designs. Liu et al. (2026) and Gao et al. (2025) are used within their verified roles. |
| 2.8.4 Liu et al. (2025a) | **CONTEXT_ONLY** | Safe one-time metadata-level use only. It must remain explicitly outside generated dependency references, as it is now. |
| 2.8.5 direct comparability, pooling, and common-frame language | **OVERSTATED** | Study-design variation supports cautious comparison, but it does not establish an absolute prohibition or demonstrate all possible re-analysis/pooling options. Apply C02 and C03. |

No Spracklen claim in Section 2.8 exceeds the verified evidence. No Twist claim attributes a direction, prevalence, risk consequence, or general prompt effect. No metadata-only source is used for a detailed empirical finding.

## 4. Table 2.2 audit

**Decision: KEEP_WITH_CORRECTIONS.** The table adds useful compact synthesis: it makes the construct--task--model--validation differences visible without reporting numerical results. It is not unnecessary duplication, although the prose immediately before and after it should not repeat every cell.

| Study / populated cells | Audit result |
|---|---|
| Spracklen et al. (2025): construct; Python/JavaScript; constructed large-scale prompts; commercial/open-source models; varied temperature; recurrence; registry cross-reference | **SUPPORTED.** Every populated field is within the full-text verification record. |
| Zhao et al. (2025): non-existent-package construct; fuzzing-based coding tasks; systematic testing | **SUPPORTED.** The dashes correctly avoid unverified ecosystem and model-condition detail. “Testing through systematically generated tasks” is a conservative description of the verified HFuzzer design. |
| Twist et al. (2026): library/member construct; Python/PyPI; developer queries; prompt/time phrasing; several LLMs; extraction, normalisation, PyPI/documentation validation | **SUPPORTED.** All cells match the full-text verification record. No outcome or risk inference is encoded in the row. |
| Tian et al. (2025): plausible generated code that fails execution/requirements; multiple models; execution-based validation | **SUPPORTED.** The dashes correctly avoid task and ecosystem inference. |

The table note correctly says a dash denotes a feature not relied on here and correctly excludes numerical comparison. Retain those dashes; do not fill them with inferred study-design information. C01--C03 do not require a table-cell change.

## 5. Spracklen repetition audit

Section 2.8 contains **six** Spracklen citations/uses.

| Location | Classification | Finding |
|---|---|---|
| 2.8.1, model-set comparison | **USEFUL** | Establishes one of the comparative design examples, but the model-set detail is also evident from Table 2.2. Retain prose or table emphasis, not both at full length. |
| 2.8.1, temperature and recurrence | **ESSENTIAL** | Direct evidence for repetition and generation-condition variation. |
| 2.8.2, constructed prompts | **USEFUL** | Supports task-source contrast; concise retention is appropriate. |
| 2.8.3, Python/JavaScript setting | **USEFUL** | Needed for the cross-ecosystem contrast; already compact. |
| 2.8.4, construct/unit/validation contrast | **ESSENTIAL** | Core evidence for the measurement comparison. |
| 2.9.2, repetition/generation limitation | **REDUNDANT** | Repeats the Section 2.8.1 point immediately before the research-gap rationale. The sentence can retain the limitation by cross-reference without re-citing Spracklen. |

**Redundant-use count: 1.** Recommended revision is C04 below. Do not remove the other five uses: each has a distinct evidentiary role or supports the table.

## 6. Section 2.9 research-gap verification

**PASS after C04.** Sections 2.9.1--2.9.2 remain literature-supported synthesis; Section 2.9.3 explicitly labels the dissertation rationale as implementation-based. The block does not claim no prior work, first-study status, absence of detection approaches, broad benchmark absence, or a general prevalence conclusion. It also expressly rejects a unique-combination claim.

The following are unambiguously presented as this dissertation's design rather than literature constructs: standardised Node.js/npm tasks; repeated frozen model conditions; controlled collection; extraction/normalisation; read-only npm evidence; conservative adjudication; grouped comparisons; and the practical-risk framework.

Metric treatment is correct:

- **PHR/SHR** are the primary study measures.
- **DFR/RDFR** are secondary/exploratory study measures, not hallucination rates.
- The text states that the broader DFR/RDFR construct is not limited to confirmed hallucinations; confirmed hallucinations can therefore be included where D036 defines them as external dependency failures.
- No final result, ranking, significance statement, or risk distribution is stated.

The description of the implementation is slightly more detailed than needed in a research-gap section, but it stays at design level and points detailed procedure to Chapter 3. C04 both removes the one redundant Spracklen citation and reduces repeated setup.

## 7. Section 2.10 verification

**PASS after C05.** The summary accurately follows Sections 2.1--2.9, introduces no citation or numerical/result claim, and transitions naturally to Chapter 3. It does, however, use two absolute expressions inconsistent with the chapter's own careful treatment of registry evidence. C05 supplies conservative wording.

## 8. Uncited-synthesis audit

| Analytical point | Decision | Handling |
|---|---|---|
| Ecosystems may differ in naming/import conventions. | **SAFE_AS_SYNTHESIS** | Retain the explicit “matter of analysis” label and npm example; do not attribute it to Zheng. |
| Models and serving conditions may change over time. | **SAFE_AS_SYNTHESIS** | Retain as dissertation reasoning about reproducibility/traceability, not an empirical literature finding. |
| Findings from one ecosystem should not automatically transfer to another. | **SAFE_AS_SYNTHESIS** | Retain as bounded comparative inference from differing study settings. |
| Study-design variation complicates comparison. | **SAFE_AS_SYNTHESIS** | Retain after C02/C03 remove absolute non-comparability/pooling language. |
| Detailed extraction/normalisation, collection, and metric chain in 2.9.3. | **MOVE_TO_CHAPTER_3** (in detail) | A concise rationale is appropriate in 2.9; procedural detail belongs in Chapter 3. |

## 9. Length and redundancy findings

Section 2.8 **should be shortened modestly**, for genuine repetition rather than a page target. The useful table permits a reduction of the prose list of design fields, and C02/C03 reduce repeated comparability conclusions. The 2.9.2 repetition sentence is a genuine duplicate of 2.8.1 and is addressed by C04.

Section 2.9 repeats Chapter 1's bounded-gap and implementation rationale, but this is appropriate at a shorter literature-synthesis level. Do not remove its explicit primary/secondary metric boundary or its rejection of novelty claims. If further shortening is required after C04, move the response-to-metric traceability detail from 2.9.3 to Chapter 3 rather than cutting the gap statement.

## 10. Required corrections with exact replacement wording

**C01 — Section 2.8.2, prompt-comparison requirement (line 25)**

Replace:

> its relevance here is that prompt wording is itself a condition that must be reported and held constant if outcomes are to be compared across models or tasks.

With:

> its relevance here is that prompt wording is itself a condition that should be reported and either controlled or explicitly accounted for when outcomes are compared across models or tasks.

**C02 — Section 2.8.5, direct-comparison conclusion (line 58)**

Replace:

> Section 2.5.2 deferred consideration of individual reported figures to this section; the conclusion reached here is that such figures are not suitable for direct side-by-side comparison, because each is meaningful only within the design that produced it.

With:

> Section 2.5.2 deferred consideration of individual reported figures to this section; the conclusion reached here is that such figures should not be interpreted as directly comparable without accounting for the design conditions that produced them.

**C03 — Section 2.8.5, pooling claim (line 60)**

Replace:

> What they do not provide, and were not designed to provide, is a common frame within which their figures can be pooled.

With:

> The reviewed studies do not supply a single shared design frame that would make their figures directly poolable without further harmonisation.

**C04 — Section 2.9.2, redundant Spracklen repetition use (line 82)**

Replace:

> The fourth limitation concerns generation conditions and sampling. Prior research has examined repetition and varied generation settings [Spracklen et al., 2025], and has shown that prompt formulation is a condition of interest [Twist et al., 2026]. Findings are therefore bounded by the models, settings, prompts, and number of generations sampled, and they may not transfer to other conditions.

With:

> The fourth limitation concerns generation conditions and sampling. As Section 2.8 showed, prior research has treated repetition, generation settings, and prompt formulation as relevant design conditions. Findings are therefore bounded by the models, settings, prompts, and number of generations sampled, and they may not transfer to other conditions.

**C05 — Section 2.10, registry and security-consequence absolutes (lines 104--106)**

Replace:

> It then examined software dependency ecosystems and package registries, establishing that a dependency reference is resolved by name against the time-dependent state of an external registry, and reviewed the supply-chain threats that operate through package names.

With:

> It then examined software dependency ecosystems and package registries, explaining that the resolution status of an external dependency reference is assessed against time-dependent registry evidence, and reviewed supply-chain threats that can operate through package names.

Replace:

> It showed that registry evidence is indispensable but time-bounded and insufficient on its own to classify a reference, that detection and classification are distinct steps, and that the treatment of confused, removed, local, and unresolved references affects measured prevalence. The review of reliability, security, and risk showed that the consequences of a hallucinated reference are conditional on adversarial registration and on the reference being acted upon, and that prevalence alone does not describe practical risk.

With:

> It showed that registry evidence is a key but time-bounded input and is insufficient on its own to classify a reference, that detection and classification are distinct steps, and that the treatment of confused, removed, local, and unresolved references affects measured prevalence. The review of reliability, security, and risk showed that potential security consequences of a hallucinated reference are conditional on adversarial registration and on the reference being acted upon, and that prevalence alone does not describe practical risk.

## 11. Numeric, result, and novelty check

**PASS.** No numeric literature claim, dissertation result, model/category ranking, significance claim, or risk distribution appears in the block. No “first study,” “no prior work,” “unexplored,” or equivalent novelty/absence assertion appears.

## 12. Full Chapter 2 assembly readiness

**READY_AFTER_CORRECTIONS**

Apply C01--C05, retain Table 2.2 with the existing dashes, and then assemble the three verified blocks without modifying Sections 2.1--2.7.
