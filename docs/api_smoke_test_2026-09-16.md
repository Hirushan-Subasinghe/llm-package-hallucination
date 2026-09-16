# Excluded API Smoke Test — 2026-09-16

The freeze record was written at `2026-09-16T06:14:40.985134Z` before these requests. `SMOKE-API-001` is not one of the 30 frozen tasks, is absent from the official manifest, and all outputs under `data/smoke/api/` are excluded from every research metric. Response content and package quality were not evaluated.

Exactly one logical smoke generation was sent to each frozen condition with the same smoke prompt, common sampling parameters, provider pins, one user message, `tool_choice: "none"`, and no tools.

| Condition | Infrastructure result | Identity/routing | Tool result |
| --- | --- | --- | --- |
| M1 | HTTP 200, completed | Returned `cohere/north-mini-code:free`; resolved provider `Cohere` | 0 tool calls |
| M2 | HTTP 403, failed before model response; edge body `error code: 1010` | No returned model/provider metadata | No model message returned |
| M3 | HTTP 403, failed before model response; edge body `error code: 1010` | No returned model/provider metadata | No model message returned |
| M4 | HTTP 200, completed | Returned `nvidia/nemotron-3-ultra-550b-a55b:free`; resolved provider `Nvidia` | 0 tool calls |

M1 and M4 preserve raw provider responses, response text, token usage, finish reason, request/response hashes, and safe headers. M2 and M3 preserve the request, HTTP error body, safe headers, and attempt hash. No API key is serialized in smoke artifacts.

The two 403 responses were not retried because the frozen infrastructure retry policy permits only HTTP 429, transport failures, or HTTP 5xx. The collector now sends a fixed research-client User-Agent because the read-only metadata preflight required an explicit User-Agent at the same edge. No additional completion request was made after that implementation correction.

At that point, official collection was blocked until Groq completion access could be resolved. Any additional smoke completion required separate prospective authorization; it had to remain excluded and could not be selected based on response content.

## Groq transport diagnostic and authorized re-smoke

A later manual diagnostic sent a conventional HTTP/1.1 request to `https://api.groq.com/openai/v1/chat/completions` with `Authorization: Bearer <credential>`, `Content-Type: application/json`, `Accept: application/json`, and `User-Agent: ai-hallucination-study/1.0`. Groq returned HTTP 200, the exact requested `openai/gpt-oss-120b` model, a Groq request ID, and Groq rate-limit headers. This isolates the earlier failures away from account authorization, model availability, and general network access and provides strongest evidence of an incompatibility in the original Python `urllib.request` completion transport/header profile. The diagnostic's 16-token cap ended with `finish_reason: "length"` after reasoning-token consumption; it was intentionally too small for content evaluation and is not an experimental observation.

The post-freeze infrastructure correction changes no experimental semantic. The collector now uses the already-installed `requests` 2.33.1 client (`urllib3` 2.7.0), sends the three stable non-secret headers above, preserves the Bearer authorization header in memory only, sends the same compact UTF-8 JSON bytes, and disables redirects. Normal environment-proxy behavior remains enabled; no proxy environment variable was set during this correction. No package was installed, and no browser impersonation, rotating header, Cloudflare bypass, proxy rotation, or fingerprint spoofing was introduced.

The model set, task file, rendered prompt bytes and hashes, official manifest, sampling parameters, no-tools behavior, and collection order remain frozen. The experiment freeze record was not regenerated for this transport-only change.

The first execution of the authorized re-smoke (`SMOKE-API-002`) ran inside a network-restricted local sandbox. Both conditions exhausted the frozen transport retry schedule (initial attempt plus 2-, 5-, and 10-second retries) without receiving any HTTP status or response headers. These pre-transmission failure records are preserved separately and were not overwritten. A credential-free HTTP/1.1 HEAD check outside that sandbox reached Groq and returned Groq/Cloudflare headers, confirming the local execution restriction. The two requested, actually transmitted observations were therefore stored in the separate `SMOKE-API-003` series outside the network sandbox.

| Condition | Transmitted re-smoke result | Identity/tools | Token and reasoning metadata |
| --- | --- | --- | --- |
| M2 | First attempt HTTP 200; completed; `finish_reason: "stop"` | Returned exact `qwen/qwen3.8-27b`; 0 tool calls | 274 completion tokens; no reasoning-token or visible-response-token count exposed |
| M3 | First attempt HTTP 200; completed; `finish_reason: "stop"` | Returned exact `openai/gpt-oss-120b`; 0 tool calls | 1,293 completion tokens, including 663 exposed reasoning tokens; no visible-response-token count exposed; raw message reasoning field preserved in the provider response |

Both transmitted observations preserve the raw provider JSON, exact assistant content, token usage, finish reason, safe Groq request/rate-limit headers, and SHA-256 hashes. Credential scanning found no API key in stored artifacts. Content quality and package names were not inspected. Together with the unchanged original M1/M4 successes, all four frozen conditions are infrastructure-ready. This readiness does not itself start or authorize official collection; all 360 official rows remain pending.
