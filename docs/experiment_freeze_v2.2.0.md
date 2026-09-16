# Experiment Freeze Record — v2.2.0

This record was generated at `2026-09-16T11:56:25.159993Z` **before any official v2.2 API generation request**. Zero official v2.2 observations existed when frozen, and all 360 official manifest rows are pending.

## Background & Historical Abort Context

- **v2.0 Stop Reason:** Official v2.0 collection was halted after exactly two observations (`API-AUTH-FED-01-M1-R01` and `API-AUTH-FED-01-M2-R01`) because models without explicit text-only wrapper instructions returned structured `tool_calls` (M1 Cohere) or simulated `<tool_call>` markup and repository-inspection requests (M2 Qwen) instead of inline code.
- **v2.1 Interface Validation & Token Ceiling Abort:** Official v2.1 collection added the standardized text-only wrapper and collected exactly one observation per model condition (`API-v2.1-AUTH-FED-01-M1-R01` through `M4-R01`). All four models passed the text-only interface gate with substantive inline implementation and zero tool calls. However, 3 of 4 models (M2, M3, M4) hit the 6000-token ceiling with `finish_reason: length` (TRUNCATED), and M1 stopped at 5893/6000 (107 tokens below ceiling). v2.1 collection was stopped before row 5 to double the output token ceiling from 6000 to 12000.
- **Evidence Preservation:** The two v2.0 observations and four v2.1 observations remain immutable methodological evidence in `data/final/raw/` and are strictly excluded from the final v2.2 dataset and research metrics.
- **Suitability Gate (D022 / D023):** Prior to freezing v2.1, all four models passed the prospective interface-suitability test (`SUITABILITY-API-001`) under the standardized text-only wrapper. All four returned HTTP 200, exact requested model ID, `finish_reason: "stop"`, zero structured tool calls, zero simulated tool markup, and substantive inline implementation without tools exposed or executed.

## Frozen Artifacts

- Task set `final-2.0.0`: `ef0aff59f8a3934f65379d34036848652b7b5593f595ffa4b449a15af021546b` (`prompts/tasks/final_2.0.0.jsonl`)
- Model set `api-model-set-1.1.0`: `fe6487a46a5e0b1a05b2858cd3a170553cc5faf5ec727bc40487012939480c76` (`config/api_model_set_1.1.0.json`)
- Prompt template `2.2.0`: `8d3971d6f9f86dfd98a4b5c49c0c13d734b7f650744da682225195f2ea49b528` (`prompts/prompt_template_v2.2.0.md`)
- Official v2.2 manifest: `0cec7f82a0b7d1c035b43410472bdb1565cf981a365595e9f2035d28cacd7ac6` (`manifests/api_final_v2.2.0_manifest.csv`)
- Official manifest rows: 360 total; 360 pending; 0 completed

## Model Conditions and Provider Pins

| Condition | Model ID | API Provider | Pinned Provider Routing |
| --- | --- | --- | --- |
| M1 | `cohere/north-mini-code:free` | OpenRouter | `cohere` |
| M2 | `qwen/qwen3.8-27b` | Groq | `not_applicable` |
| M3 | `openai/gpt-oss-120b` | Groq | `not_applicable` |
| M4 | `nvidia/nemotron-3-ultra-550b-a55b:free` | OpenRouter | `nvidia` |

## Standardized Stateless Text-Only Generation Protocol (12,000 Max Tokens)

- **Prompt Interface:** Standardized frozen text-only wrapper (`prompts/prompt_template_v2.2.0.md`) appended to every task prompt (byte-for-byte identical to v2.1).
- **Sampling Parameters:** Temperature `0.6`, Top-p `0.95`, Max completion tokens `12000` (increased from 6000), Seed omitted (`not_controlled`).
- **Interaction Constraints:** Exactly one user message per request, no prior context, no tools exposed (`tool_choice: "none"`), no browsing, no retrieval augmentation, no code execution, no reasoning-effort parameter.
- **Collection Ordering:** Deterministic balanced Latin-square rotation per task and repetition: `(task_index + repetition_offset) % 4` across 360 contiguous rows.
- **Truncation Policy:** Provider-valid response with `finish_reason: "length"` receives operational status `TRUNCATED` and is preserved without retry. Excluded from primary SHR denominator and primary PHR occurrence population; reported separately in quality metrics.
- **Methodology Versions:** Risk Model `risk-model-1.0.0`; Hallucination Taxonomy `package-hallucination-taxonomy-1.0.0`.

## Rendered Prompts (30 Tasks)

| Path | SHA-256 |
| --- | --- |
| `data/generated_prompts/v2.2.0/AUTH-FED-01.txt` | `9578dd98d4b32a7d526d6e8cb8fd1337472a6ed563e32de08994903a4642b64e` |
| `data/generated_prompts/v2.2.0/AUTH-FED-02.txt` | `0a7587118e54282ebc15031533098e0dcf7c1b76149cbbd511eae1b339314fc2` |
| `data/generated_prompts/v2.2.0/AUTH-FED-03.txt` | `940529e083cb5059287ec238fc2637aebd72b58e281dcd929ae81c4dae2ba889` |
| `data/generated_prompts/v2.2.0/AUTH-FED-04.txt` | `98f5ea52de7d8df9413e82ce9c49bc4249929b09cbed959790141562a88a3422` |
| `data/generated_prompts/v2.2.0/AUTH-FED-05.txt` | `29716f2eb9cb23e17132caf5a290ab72dea7f65faa9a1f77f980b820eb968e0c` |
| `data/generated_prompts/v2.2.0/DATA-ADV-01.txt` | `e32c759d896d42a27d4d4fc64472164455ac3edeaff87d018b740014d4dcb5b0` |
| `data/generated_prompts/v2.2.0/DATA-ADV-02.txt` | `1179c220931eae775e801f6e5c8954554e40bb988b346fe0729cce2c2ec1a865` |
| `data/generated_prompts/v2.2.0/DATA-ADV-03.txt` | `04e21ec3aa46a7465b13f1a8d3ab641e202097474720382abf14f0b180db5602` |
| `data/generated_prompts/v2.2.0/DATA-ADV-04.txt` | `81320c3da7e02c4481e23c83dd0b7ee27022d24626901ff73defa1da4a698782` |
| `data/generated_prompts/v2.2.0/DATA-ADV-05.txt` | `d97d4917892f249490765a6bb4490bbf2b1097d3131458a7a1d4f506fe8b8310` |
| `data/generated_prompts/v2.2.0/DIST-OBS-01.txt` | `93d4eab04e7b9cf3066bf7be00c92fd2b3740dc5d57ba36ca8d2804d36d14a95` |
| `data/generated_prompts/v2.2.0/DIST-OBS-02.txt` | `cfec0f17df0cef3adada4f287d8b11de8e692f4f394d1b4383eb50599104b36f` |
| `data/generated_prompts/v2.2.0/DIST-OBS-03.txt` | `eda2b937c0372df95a3b9e783550484ed00ca183aa199f481fc09e7dafde2af0` |
| `data/generated_prompts/v2.2.0/DIST-OBS-04.txt` | `6fa72b98610e51da69b3465c3d981d8b2f2bef0873c7acdb5607a0f724f66697` |
| `data/generated_prompts/v2.2.0/DIST-OBS-05.txt` | `867e590bb440b0f28099cc5c6e584cf2170f6250422ad75143f06191d5d12b72` |
| `data/generated_prompts/v2.2.0/DOC-BINARY-01.txt` | `767bc383aa87c71b76a17e551dc128950b38ad55c71d0cd35ae1aacf99c0f962` |
| `data/generated_prompts/v2.2.0/DOC-BINARY-02.txt` | `e31044746f5bbc907db563a974a29f56bcafd8a0b14e349f5f6ada1c6336e6f0` |
| `data/generated_prompts/v2.2.0/DOC-BINARY-03.txt` | `81b0a166bc2aff2ce939fd520f888a4f7d0e5314aa35c94ceb16fb82fbf8a073` |
| `data/generated_prompts/v2.2.0/DOC-BINARY-04.txt` | `28944b6ec4e91456629b9531199d07f19ed645e379188d073be6ab3c287ee6f4` |
| `data/generated_prompts/v2.2.0/DOC-BINARY-05.txt` | `7c521b2f482a827c3280bf08f8141a4ca971b0c18d417faa3372abc91bbae0cc` |
| `data/generated_prompts/v2.2.0/ENT-INT-01.txt` | `0c26eb4ae40bae09c47a03a0954ec00b3c4da0f89f6460d13021a1e83200aa0e` |
| `data/generated_prompts/v2.2.0/ENT-INT-02.txt` | `bafa2d5a9cac4af23a2c771546e8f923d02ee792ee07ec6bed061c15b5f9b2d3` |
| `data/generated_prompts/v2.2.0/ENT-INT-03.txt` | `666f44a118109ac44831cdb2076c4803e2312e242fd20f34ce933bd3f3ae5854` |
| `data/generated_prompts/v2.2.0/ENT-INT-04.txt` | `6b85399381327aa2b62226dbd438cb95ab4aea0b2953d40cf703fe65555f43af` |
| `data/generated_prompts/v2.2.0/ENT-INT-05.txt` | `caf93be10c7e32dcc3d565f45756a0b07122b4b6d8c80f09663c6fd3d2eb3fc1` |
| `data/generated_prompts/v2.2.0/PKI-CRYPTO-01.txt` | `49b756d40016b603151cf5e28eb5b8371a748ab560fba83cfc6c7ef028f483e7` |
| `data/generated_prompts/v2.2.0/PKI-CRYPTO-02.txt` | `a02f825ca658d9c5723e1ef6072e73edb58e5504ad2e4a6899287e977a39f123` |
| `data/generated_prompts/v2.2.0/PKI-CRYPTO-03.txt` | `4af44cea218275da4ff02591088980eb855e426bbdbf71d61461231f7ee915e0` |
| `data/generated_prompts/v2.2.0/PKI-CRYPTO-04.txt` | `3a978299b633edff0cb3a45e3c2293ce1b5ed314bc15b4d6e2f8334693831bbf` |
| `data/generated_prompts/v2.2.0/PKI-CRYPTO-05.txt` | `4094b932f8c5fc9265a01d3bf64db2a143efc56c8e376c071b55ab07f2b4153d` |

## Schemas

- `schemas/api_model_set.schema.json` — `b1e1e2a592c8aa0dd7670cb9285a366257dd85c1df23b7a4b64c20caa6b303e5`
- `schemas/api_manifest_row.schema.json` — `494c6c0b62595e1bd1a3f92df1455d11884045575d90905aa12175ccdc887d58`
- `schemas/api_collection_metadata.schema.json` — `2e71b3c546f0fec82cf6a1c031a55659c05a3f02f488f69e613ad681b905819f`
- `schemas/task_record_v2.schema.json` — `b828207953d17493d90be9d781bb0e38f5c220b99fea2486b952a5482789b3f2`
- `schemas/interface_suitability.schema.json` — `8e200c0e00058f213ca39b1f08cdf2348bcbdf5570fc461d702cb53028e7ff4d`

## Experimental Data Boundaries

- Preserved v2.0 observations (`data/final/raw/API-AUTH-FED-01-M1-R01`, `data/final/raw/API-AUTH-FED-01-M2-R01`), preserved v2.1 observations (`data/final/raw/API-v2.1-AUTH-FED-01-M1-R01` through `M4-R01`), smoke tests (`data/smoke/api/`), suitability tests (`data/suitability/api/v2.1.0/`), and historical pilot data (`data/pilot/`) are completely excluded from the official v2.2 dataset and all research metrics.
- As of this freeze, exactly 0 official v2.2 generation observations exist.
