import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import collect_api_run


class APICollectionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.raw_root = Path(self.temporary.name) / "raw"
        self.config = collect_api_run.load_config(collect_api_run.DEFAULT_CONFIG)
        self.config = copy.deepcopy(self.config)
        self.config["status"] = "frozen_for_collection"
        self.config["candidate_common_parameters"]["compatibility_status"] = "confirmed"
        self.prompt_path = ROOT / "data" / "generated_prompts" / "v1.0.0" / "AUTH-01.txt"

    def tearDown(self):
        self.temporary.cleanup()

    def row(self, condition_id="M3"):
        model = next(model for model in self.config["models"] if model["condition_id"] == condition_id)
        prompt = self.prompt_path.read_bytes()
        return {
            "collection_order": "1",
            "run_id": f"V2-AUTH-FED-01-{condition_id}-R01",
            "phase": "final",
            "task_id": "AUTH-FED-01",
            "category": "AUTH-FED",
            "task_set_version": "final-2.0.0",
            "model_set_version": "api-model-set-1.0.0",
            "model_condition_id": condition_id,
            "model_id": model["model_id"],
            "api_provider": model["api_provider"],
            "underlying_provider_pin": (
                model["openrouter_routing"]["underlying_provider_slug"]
                if model["api_provider"] == "OpenRouter"
                else "not_applicable"
            ),
            "run_repetition": "1",
            "rendered_prompt_path": str(self.prompt_path.relative_to(ROOT)),
            "expected_prompt_sha256": collect_api_run.sha256_bytes(prompt),
            "collection_status": "pending",
        }

    def test_frozen_model_conditions_and_provider_pins(self):
        self.assertEqual(
            [(model["condition_id"], model["api_provider"], model["model_id"]) for model in self.config["models"]],
            [
                ("M1", "OpenRouter", "cohere/north-mini-code:free"),
                ("M2", "Groq", "qwen/qwen3.8-27b"),
                ("M3", "Groq", "openai/gpt-oss-120b"),
                ("M4", "OpenRouter", "nvidia/nemotron-3-ultra-550b-a55b:free"),
            ],
        )
        self.assertEqual(self.config["models"][0]["openrouter_routing"]["pinning_status"], "pinned")
        self.assertEqual(self.config["models"][0]["openrouter_routing"]["underlying_provider_slug"], "cohere")
        self.assertEqual(self.config["models"][3]["openrouter_routing"]["pinning_status"], "pinned")
        self.assertEqual(self.config["models"][3]["openrouter_routing"]["underlying_provider_slug"], "nvidia")
        self.assertTrue(all(model["no_tools_request_mode"] == "explicit_tool_choice_none" for model in self.config["models"]))

    def test_candidate_configuration_blocks_collection(self):
        candidate = copy.deepcopy(collect_api_run.load_config(collect_api_run.DEFAULT_CONFIG))
        candidate["status"] = "candidate_pending_researcher_review"
        with self.assertRaisesRegex(ValueError, "not frozen"):
            collect_api_run.validate_collection_ready(
                candidate,
                self.row(),
                self.config["models"][2],
            )

    def test_request_has_one_user_message_explicitly_disables_tools_and_omits_seed(self):
        row = self.row()
        response = {
            "id": "test-completion",
            "model": row["model_id"],
            "choices": [{"message": {"role": "assistant", "content": "exact response\n"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 2, "total_tokens": 12},
        }
        seen = []

        def transport(url, headers, body, timeout):
            seen.append((url, headers, json.loads(body), timeout))
            return collect_api_run.HTTPResult(200, {"X-Request-ID": "request-1", "Set-Cookie": "secret"}, json.dumps(response).encode())

        with patch.dict("os.environ", {"GROQ_API_KEY": "test-only-secret"}, clear=False):
            directory = collect_api_run.collect_row(
                self.config,
                row,
                raw_root=self.raw_root,
                transport=transport,
                sleeper=lambda _: None,
            )
        self.assertEqual(len(seen), 1)
        payload = seen[0][2]
        headers = seen[0][1]
        self.assertEqual(headers["User-Agent"], "ai-hallucination-study/1.0")
        self.assertEqual(headers["Accept"], "application/json")
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertEqual(headers["Authorization"], "Bearer test-only-secret")
        self.assertEqual(payload["messages"], [{"role": "user", "content": self.prompt_path.read_text()}])
        self.assertEqual(payload["temperature"], 0.6)
        self.assertEqual(payload["top_p"], 0.95)
        self.assertEqual(payload["max_completion_tokens"], 6000)
        self.assertEqual(payload["tool_choice"], "none")
        self.assertNotIn("tools", payload)
        self.assertNotIn("seed", payload)
        self.assertEqual((directory / "response.md").read_bytes(), b"exact response\n")
        metadata = json.loads((directory / "metadata.json").read_text())
        self.assertEqual(metadata["collection_status"], "completed")
        self.assertEqual(metadata["http_client"]["library"], "requests")
        self.assertEqual(metadata["stable_request_headers"], collect_api_run.STABLE_REQUEST_HEADERS)
        self.assertEqual(metadata["safe_response_headers"], {"x-request-id": "request-1"})
        for path in directory.rglob("*"):
            if path.is_file():
                self.assertNotIn(b"test-only-secret", path.read_bytes())

    def test_requests_transport_preserves_body_headers_and_disables_redirects(self):
        response = type("Response", (), {
            "status_code": 200,
            "headers": {"Content-Type": "application/json"},
            "content": b'{}',
        })()
        with patch.object(collect_api_run.requests, "post", return_value=response) as post:
            result = collect_api_run.request_once(
                "https://api.groq.com/openai/v1/chat/completions",
                {"Authorization": "Bearer test-only-secret", **collect_api_run.STABLE_REQUEST_HEADERS},
                b'{"exact":"bytes"}',
                12.5,
            )
        self.assertEqual(result.status, 200)
        post.assert_called_once_with(
            "https://api.groq.com/openai/v1/chat/completions",
            data=b'{"exact":"bytes"}',
            headers={"Authorization": "Bearer test-only-secret", **collect_api_run.STABLE_REQUEST_HEADERS},
            timeout=12.5,
            allow_redirects=False,
        )

    def test_length_finish_is_preserved_as_truncated_without_retry(self):
        row = self.row()
        calls = []
        response = {
            "id": "test-truncated",
            "model": row["model_id"],
            "choices": [{"message": {"role": "assistant", "content": ""}, "finish_reason": "length"}],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 6000,
                "total_tokens": 6010,
                "completion_tokens_details": {"reasoning_tokens": 5999},
            },
        }

        def transport(*_):
            calls.append(1)
            return collect_api_run.HTTPResult(200, {}, json.dumps(response).encode())

        with patch.dict("os.environ", {"GROQ_API_KEY": "test-only-secret"}, clear=False):
            directory = collect_api_run.collect_row(
                self.config,
                row,
                raw_root=self.raw_root,
                transport=transport,
                sleeper=lambda _: None,
            )
        self.assertEqual(calls, [1])
        self.assertEqual((directory / "response.md").read_bytes(), b"")
        metadata = json.loads((directory / "metadata.json").read_text())
        self.assertEqual(metadata["collection_status"], "truncated")
        self.assertEqual(metadata["response_completion_status"], "TRUNCATED")
        self.assertEqual(metadata["finish_reason"], "length")
        self.assertEqual(metadata["response_token_metadata"], {
            "total_completion_tokens": 6000,
            "reasoning_tokens": 5999,
            "visible_response_tokens": None,
        })
        self.assertEqual(len(metadata["retry_history"]), 1)

    def test_openrouter_omit_only_mode_sends_neither_tools_nor_tool_choice(self):
        model = self.config["models"][0]
        model["no_tools_request_mode"] = "omit_tools_only"
        with patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-only-secret"}, clear=False):
            _, _, body = collect_api_run.build_request(self.config, model, self.prompt_path.read_bytes())
        payload = json.loads(body)
        self.assertNotIn("tools", payload)
        self.assertNotIn("tool_choice", payload)

    def test_pending_no_tools_preflight_blocks_collection(self):
        row = self.row("M1")
        model = self.config["models"][0]
        model["no_tools_request_mode"] = "pending_preflight"
        model["openrouter_routing"].update({
            "pinning_status": "pinned",
            "underlying_provider_slug": "reviewed-provider-slug",
            "underlying_provider_name": "Reviewed Provider",
        })
        row["underlying_provider_pin"] = "reviewed-provider-slug"
        with self.assertRaisesRegex(ValueError, "No-tools request behavior"):
            collect_api_run.validate_collection_ready(self.config, row, model)

    def test_retry_after_is_obeyed_for_rate_limit(self):
        row = self.row()
        responses = [
            collect_api_run.HTTPResult(429, {"Retry-After": "7"}, b"rate limited"),
            collect_api_run.HTTPResult(200, {}, json.dumps({
                "model": row["model_id"],
                "choices": [{"message": {"content": "kept"}, "finish_reason": "stop"}],
                "usage": {},
            }).encode()),
        ]
        sleeps = []
        with patch.dict("os.environ", {"GROQ_API_KEY": "test-only-secret"}, clear=False):
            collect_api_run.collect_row(
                self.config,
                row,
                raw_root=self.raw_root,
                transport=lambda *_: responses.pop(0),
                sleeper=sleeps.append,
            )
        self.assertEqual(sleeps, [7.0])

    def test_openrouter_requires_preflight_and_pins_without_fallback(self):
        row = self.row("M1")
        model = self.config["models"][0]
        model["openrouter_routing"]["pinning_status"] = "pending_preflight"
        with self.assertRaisesRegex(ValueError, "preflight"):
            collect_api_run.validate_collection_ready(self.config, row, model)
        model["no_tools_request_mode"] = "explicit_tool_choice_none"
        model["openrouter_routing"].update({
            "pinning_status": "pinned",
            "underlying_provider_slug": "reviewed-provider-slug",
            "underlying_provider_name": "Reviewed Provider",
        })
        row["underlying_provider_pin"] = "reviewed-provider-slug"
        collect_api_run.validate_collection_ready(self.config, row, model)
        with patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-only-secret"}, clear=False):
            _, _, body = collect_api_run.build_request(self.config, model, self.prompt_path.read_bytes())
        payload = json.loads(body)
        self.assertEqual(payload["tool_choice"], "none")
        self.assertNotIn("tools", payload)
        self.assertEqual(payload["provider"]["order"], ["reviewed-provider-slug"])
        self.assertFalse(payload["provider"]["allow_fallbacks"])
        self.assertTrue(payload["provider"]["require_parameters"])

    def test_only_infrastructure_failures_retry_and_every_attempt_is_logged(self):
        row = self.row()
        responses = [
            collect_api_run.HTTPResult(429, {}, b"rate limited"),
            collect_api_run.HTTPResult(500, {}, b"server error"),
            collect_api_run.HTTPResult(200, {}, json.dumps({
                "model": row["model_id"],
                "choices": [{"message": {"content": "kept"}, "finish_reason": "stop"}],
                "usage": {},
            }).encode()),
        ]
        sleeps = []

        def transport(*_):
            return responses.pop(0)

        with patch.dict("os.environ", {"GROQ_API_KEY": "test-only-secret"}, clear=False):
            directory = collect_api_run.collect_row(
                self.config,
                row,
                raw_root=self.raw_root,
                transport=transport,
                sleeper=sleeps.append,
            )
        metadata = json.loads((directory / "metadata.json").read_text())
        self.assertEqual([item["http_status"] for item in metadata["retry_history"]], [429, 500, 200])
        self.assertEqual(sleeps, [2, 5])
        self.assertEqual((directory / "attempts" / "attempt-01" / "http_response.bin").read_bytes(), b"rate limited")

    def test_http_200_without_valid_content_is_not_retried(self):
        calls = []

        def transport(*_):
            calls.append(1)
            return collect_api_run.HTTPResult(200, {}, b'{"choices":[]}')

        with patch.dict("os.environ", {"GROQ_API_KEY": "test-only-secret"}, clear=False):
            with self.assertRaisesRegex(ValueError, "valid chat completion"):
                collect_api_run.collect_row(
                    self.config,
                    self.row(),
                    raw_root=self.raw_root,
                    transport=transport,
                    sleeper=lambda _: None,
                )
        self.assertEqual(len(calls), 1)

    def test_transport_errors_never_serialize_api_key(self):
        self.config["retry_policy"]["maximum_infrastructure_retries"] = 0
        row = self.row()

        def transport(*_):
            raise collect_api_run.TransportFailure("transport detail test-only-secret")

        with patch.dict("os.environ", {"GROQ_API_KEY": "test-only-secret"}, clear=False):
            with self.assertRaisesRegex(ValueError, "transport failure"):
                collect_api_run.collect_row(
                    self.config,
                    row,
                    raw_root=self.raw_root,
                    transport=transport,
                    sleeper=lambda _: None,
                )
        for path in (self.raw_root / row["run_id"]).rglob("*"):
            if path.is_file():
                self.assertNotIn(b"test-only-secret", path.read_bytes())

    def test_existing_run_directory_is_never_overwritten(self):
        row = self.row()
        directory = self.raw_root / row["run_id"]
        directory.mkdir(parents=True)
        (directory / "sentinel").write_text("keep")
        with self.assertRaisesRegex(ValueError, "overwrite"):
            collect_api_run.collect_row(self.config, row, raw_root=self.raw_root)
        self.assertEqual((directory / "sentinel").read_text(), "keep")


if __name__ == "__main__":
    unittest.main()
