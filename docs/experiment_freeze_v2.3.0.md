# Experiment Freeze Record — v2.3.0

This record was generated at `2026-09-17T10:07:14.819090Z` **before any official v2.3 API generation request**. It defines a fresh 360-observation dataset; all rows are pending and no v2.3 raw observation directory exists.

## v2.2 Stop and Dataset Separation

v2.2 was prospectively stopped with its final inventory at 360 planned, 6 completed, 4 truncated, and 350 pending (10 total collected observations). Those 10 immutable v2.2 observations remain methodological evidence only and are excluded from all v2.3 primary metrics. v2.3 begins a new, separate 360-observation dataset.

The sole intended methodological difference from v2.2 is removal of the unnecessarily conservative researcher-imposed fixed provider spacing under a tight final collection window. Model identities, provider pins, no-fallback rule, task set, prompt text, interaction constraints, sampling parameters, retry philosophy, and truncation handling are unchanged. Payment or account tier is infrastructure availability only; it is not an experimental condition if the frozen model ID, routing, prompt, and generation parameters remain identical.

## Frozen Artifacts

- Task set `final-2.0.0`: `ef0aff59f8a3934f65379d34036848652b7b5593f595ffa4b449a15af021546b` (`prompts/tasks/final_2.0.0.jsonl`)
- Model set `api-model-set-1.2.0`: `e931bf60f1b07a19e975ccd0c71f9f32ecbbd80da4001b006494555801351af4` (`config/api_model_set_1.2.0.json`)
- Prompt template `2.3.0`: `8d3971d6f9f86dfd98a4b5c49c0c13d734b7f650744da682225195f2ea49b528` (`prompts/prompt_template_v2.3.0.md`)
- Official v2.3 manifest: `ac0d0365198e2d16e2b4b600a274307ee82dbafacfd030b4d3eca1423fdef404` (`manifests/api_final_v2.3.0_manifest.csv`)
- Official manifest rows: 360 total; 360 pending; 0 completed

## Collection and Failure Policy

- Sequential collection only. The minimum artificial interval after a successful request is 0 seconds; the next manifest row is attempted immediately.
- Provider-enforced throttling remains binding: HTTP 429 obeys `Retry-After` when supplied, otherwise the frozen infrastructure backoff applies. HTTP 5xx and transport failures use only the frozen infrastructure retry policy.
- A quota, credit, account-limit, or other non-retryable provider failure is preserved as failed infrastructure evidence and stops the batch without skipping, substituting providers/models, or changing a `:free` route to a paid route.
- `finish_reason: length` is an official TRUNCATED observation, preserved exactly once and never regenerated merely for truncation.
- Exactly one user message; no prior context, tools, browsing, retrieval, filesystem, external files, or code execution. Temperature 0.6, top-p 0.95, maximum completion tokens 12000, seed omitted/not controlled.

## Rendered Prompts

| Path | SHA-256 |
| --- | --- |
| `data/generated_prompts/v2.3.0/AUTH-FED-01.txt` | `9578dd98d4b32a7d526d6e8cb8fd1337472a6ed563e32de08994903a4642b64e` |
| `data/generated_prompts/v2.3.0/AUTH-FED-02.txt` | `0a7587118e54282ebc15031533098e0dcf7c1b76149cbbd511eae1b339314fc2` |
| `data/generated_prompts/v2.3.0/AUTH-FED-03.txt` | `940529e083cb5059287ec238fc2637aebd72b58e281dcd929ae81c4dae2ba889` |
| `data/generated_prompts/v2.3.0/AUTH-FED-04.txt` | `98f5ea52de7d8df9413e82ce9c49bc4249929b09cbed959790141562a88a3422` |
| `data/generated_prompts/v2.3.0/AUTH-FED-05.txt` | `29716f2eb9cb23e17132caf5a290ab72dea7f65faa9a1f77f980b820eb968e0c` |
| `data/generated_prompts/v2.3.0/DATA-ADV-01.txt` | `e32c759d896d42a27d4d4fc64472164455ac3edeaff87d018b740014d4dcb5b0` |
| `data/generated_prompts/v2.3.0/DATA-ADV-02.txt` | `1179c220931eae775e801f6e5c8954554e40bb988b346fe0729cce2c2ec1a865` |
| `data/generated_prompts/v2.3.0/DATA-ADV-03.txt` | `04e21ec3aa46a7465b13f1a8d3ab641e202097474720382abf14f0b180db5602` |
| `data/generated_prompts/v2.3.0/DATA-ADV-04.txt` | `81320c3da7e02c4481e23c83dd0b7ee27022d24626901ff73defa1da4a698782` |
| `data/generated_prompts/v2.3.0/DATA-ADV-05.txt` | `d97d4917892f249490765a6bb4490bbf2b1097d3131458a7a1d4f506fe8b8310` |
| `data/generated_prompts/v2.3.0/DIST-OBS-01.txt` | `93d4eab04e7b9cf3066bf7be00c92fd2b3740dc5d57ba36ca8d2804d36d14a95` |
| `data/generated_prompts/v2.3.0/DIST-OBS-02.txt` | `cfec0f17df0cef3adada4f287d8b11de8e692f4f394d1b4383eb50599104b36f` |
| `data/generated_prompts/v2.3.0/DIST-OBS-03.txt` | `eda2b937c0372df95a3b9e783550484ed00ca183aa199f481fc09e7dafde2af0` |
| `data/generated_prompts/v2.3.0/DIST-OBS-04.txt` | `6fa72b98610e51da69b3465c3d981d8b2f2bef0873c7acdb5607a0f724f66697` |
| `data/generated_prompts/v2.3.0/DIST-OBS-05.txt` | `867e590bb440b0f28099cc5c6e584cf2170f6250422ad75143f06191d5d12b72` |
| `data/generated_prompts/v2.3.0/DOC-BINARY-01.txt` | `767bc383aa87c71b76a17e551dc128950b38ad55c71d0cd35ae1aacf99c0f962` |
| `data/generated_prompts/v2.3.0/DOC-BINARY-02.txt` | `e31044746f5bbc907db563a974a29f56bcafd8a0b14e349f5f6ada1c6336e6f0` |
| `data/generated_prompts/v2.3.0/DOC-BINARY-03.txt` | `81b0a166bc2aff2ce939fd520f888a4f7d0e5314aa35c94ceb16fb82fbf8a073` |
| `data/generated_prompts/v2.3.0/DOC-BINARY-04.txt` | `28944b6ec4e91456629b9531199d07f19ed645e379188d073be6ab3c287ee6f4` |
| `data/generated_prompts/v2.3.0/DOC-BINARY-05.txt` | `7c521b2f482a827c3280bf08f8141a4ca971b0c18d417faa3372abc91bbae0cc` |
| `data/generated_prompts/v2.3.0/ENT-INT-01.txt` | `0c26eb4ae40bae09c47a03a0954ec00b3c4da0f89f6460d13021a1e83200aa0e` |
| `data/generated_prompts/v2.3.0/ENT-INT-02.txt` | `bafa2d5a9cac4af23a2c771546e8f923d02ee792ee07ec6bed061c15b5f9b2d3` |
| `data/generated_prompts/v2.3.0/ENT-INT-03.txt` | `666f44a118109ac44831cdb2076c4803e2312e242fd20f34ce933bd3f3ae5854` |
| `data/generated_prompts/v2.3.0/ENT-INT-04.txt` | `6b85399381327aa2b62226dbd438cb95ab4aea0b2953d40cf703fe65555f43af` |
| `data/generated_prompts/v2.3.0/ENT-INT-05.txt` | `caf93be10c7e32dcc3d565f45756a0b07122b4b6d8c80f09663c6fd3d2eb3fc1` |
| `data/generated_prompts/v2.3.0/PKI-CRYPTO-01.txt` | `49b756d40016b603151cf5e28eb5b8371a748ab560fba83cfc6c7ef028f483e7` |
| `data/generated_prompts/v2.3.0/PKI-CRYPTO-02.txt` | `a02f825ca658d9c5723e1ef6072e73edb58e5504ad2e4a6899287e977a39f123` |
| `data/generated_prompts/v2.3.0/PKI-CRYPTO-03.txt` | `4af44cea218275da4ff02591088980eb855e426bbdbf71d61461231f7ee915e0` |
| `data/generated_prompts/v2.3.0/PKI-CRYPTO-04.txt` | `3a978299b633edff0cb3a45e3c2293ce1b5ed314bc15b4d6e2f8334693831bbf` |
| `data/generated_prompts/v2.3.0/PKI-CRYPTO-05.txt` | `4094b932f8c5fc9265a01d3bf64db2a143efc56c8e376c071b55ab07f2b4153d` |
