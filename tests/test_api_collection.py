import copy
import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import collect_api_batch
import collect_api_run
import create_api_manifest


class APICollectionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.raw_root = Path(self.temporary.name) / "raw"
        self.config = collect_api_run.load_config(collect_api_run.DEFAULT_CONFIG)
        self.config = copy.deepcopy(self.config)
        self.config["status"] = "frozen_for_collection"
        self.config["candidate_common_parameters"]["compatibility_status"] = "confirmed"
        self.prompt_path = ROOT / "data" / "generated_prompts" / "v2.3.0" / "AUTH-FED-01.txt"

    def tearDown(self):
        self.temporary.cleanup()

    def row(self, condition_id="M3", run_prefix="API-v2.3"):
        model = next(model for model in self.config["models"] if model["condition_id"] == condition_id)
        prompt = self.prompt_path.read_bytes()
        return {
            "collection_order": "1",
            "run_id": f"{run_prefix}-AUTH-FED-01-{condition_id}-R01",
            "phase": "final",
            "task_id": "AUTH-FED-01",
            "category": "AUTH-FED",
            "task_set_version": "final-2.0.0",
            "model_set_version": self.config["model_set_version"],
            "model_condition_id": condition_id,
            "model_id": model["model_id"],
            "api_provider": model["api_provider"],
            "underlying_provider_pin": (
                model["openrouter_routing"]["underlying_provider_slug"]
                if model["api_provider"] == "OpenRouter"
                else "not_applicable"
            ),
            "run_repetition": "R01",
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
        self.assertEqual(payload["max_completion_tokens"], 12000)
        self.assertEqual(payload["tool_choice"], "none")
        self.assertNotIn("tools", payload)
        self.assertNotIn("seed", payload)
        self.assertEqual((directory / "response.md").read_bytes(), b"exact response\n")
        metadata = json.loads((directory / "metadata.json").read_text())
        self.assertEqual(metadata["collection_status"], "completed")
        self.assertEqual(metadata["http_client"]["library"], "requests")
        self.assertEqual(metadata["stable_request_headers"], collect_api_run.STABLE_REQUEST_HEADERS)
        self.assertEqual(metadata["safe_response_headers"], {"x-request-id": "request-1"})
        self.assertEqual(metadata["sampling_parameters"]["max_output_tokens"], 12000)
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
                "completion_tokens": 12000,
                "total_tokens": 12010,
                "completion_tokens_details": {"reasoning_tokens": 11999},
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
            "total_completion_tokens": 12000,
            "reasoning_tokens": 11999,
            "visible_response_tokens": None,
        })
        self.assertEqual(len(metadata["retry_history"]), 1)

    def test_completion_status_maps_only_stop_and_length_as_normal_d035(self):
        def status(finish_reason):
            return collect_api_run.completion_status({"choices": [{"finish_reason": finish_reason}]})

        self.assertEqual(status("stop"), ("completed", "COMPLETED"))
        self.assertEqual(status("length"), ("truncated", "TRUNCATED"))
        for abnormal in ("error", "content_filter", "tool_calls", None):
            self.assertEqual(status(abnormal), ("failed", "FAILED"), abnormal)

    def test_error_finish_is_preserved_once_as_failed_without_retry_d035(self):
        for label, content in (
            ("non-empty", "# Complete-looking section\n\nconst ok = true;\n"),
            ("partial", "const familyName = getAttr('familyName"),
        ):
            with self.subTest(content=label):
                row = self.row()
                row["run_id"] = f"API-v2.3-AUTH-FED-01-M3-R01-{label}"
                calls = []
                body = json.dumps({
                    "id": "test-error-finish",
                    "model": row["model_id"],
                    "choices": [{"message": {"role": "assistant", "content": content}, "finish_reason": "error"}],
                    "usage": {"prompt_tokens": 10, "completion_tokens": 7599, "total_tokens": 7609},
                }).encode()

                def transport(*_):
                    calls.append(1)
                    return collect_api_run.HTTPResult(200, {}, body)

                with patch.dict("os.environ", {"GROQ_API_KEY": "test-only-secret"}, clear=False):
                    with self.assertRaisesRegex(ValueError, "abnormal termination"):
                        collect_api_run.collect_row(
                            self.config, row, raw_root=self.raw_root,
                            transport=transport, sleeper=lambda _: None,
                        )
                directory = self.raw_root / row["run_id"]
                self.assertEqual(calls, [1])
                self.assertEqual((directory / "response.md").read_bytes(), content.encode())
                self.assertEqual((directory / "provider_response.json").read_bytes(), body)
                metadata = json.loads((directory / "metadata.json").read_text())
                self.assertEqual(metadata["collection_status"], "failed")
                self.assertEqual(metadata["response_completion_status"], "FAILED")
                self.assertEqual(metadata["finish_reason"], "error")
                self.assertEqual(metadata["failure_reason"], "provider_finish_reason_error")
                self.assertEqual(len(metadata["retry_history"]), 1)

    def test_error_finish_is_skipped_as_preserved_failure_not_regenerated_d035(self):
        row = self.row()
        directory = self.raw_root / row["run_id"]
        directory.mkdir(parents=True)
        (directory / "metadata.json").write_text(json.dumps({
            "collection_status": "failed", "finish_reason": "error",
            "failure_reason": "provider_finish_reason_error",
        }))
        state_path = Path(self.temporary.name) / "state.json"
        manifest_hash = "0" * 64

        def collector(*_args, **_kwargs):
            raise AssertionError("a preserved failed observation must not be regenerated")

        collect_api_batch.run_batch(
            self.config, [row], state_path=state_path, manifest_hash=manifest_hash,
            raw_root=self.raw_root, limit=1, collector=collector, continue_after_failed=True,
        )
        events = json.loads(state_path.read_text())["events"]
        self.assertEqual(events[-1]["event"], "skipped_preserved_failed_observation")

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
        self.assertEqual(payload["max_tokens"], 12000)

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

    def test_missing_api_key_does_not_advance_provider_pacing(self):
        row = self.row("M2")  # Groq model
        state_path = Path(self.temporary.name) / "test_state.json"
        manifest_hash = "mock_hash"

        # Ensure GROQ_API_KEY is not set
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(ValueError, "Required environment variable is not set: GROQ_API_KEY"):
                collect_api_batch.run_batch(
                    self.config,
                    [row],
                    manifest_hash=manifest_hash,
                    state_path=state_path,
                    raw_root=self.raw_root,
                    now=lambda: 1000.0,
                )

        # Verify state was never mutated with a reservation
        if state_path.exists():
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertNotIn("Groq", state.get("provider_next_allowed_at_epoch", {}))
            events = state.get("events", [])
            self.assertFalse(any(event.get("event") == "request_slot_reserved" for event in events))

    def test_local_validation_failure_does_not_advance_provider_pacing(self):
        row = self.row("M2")
        row["expected_prompt_sha256"] = "0000000000000000000000000000000000000000000000000000000000000000"
        state_path = Path(self.temporary.name) / "test_state.json"
        manifest_hash = "mock_hash"

        with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}, clear=False):
            with self.assertRaisesRegex(ValueError, "Rendered prompt hash does not match manifest"):
                collect_api_batch.run_batch(
                    self.config,
                    [row],
                    manifest_hash=manifest_hash,
                    state_path=state_path,
                    raw_root=self.raw_root,
                    now=lambda: 1000.0,
                )

        if state_path.exists():
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertNotIn("Groq", state.get("provider_next_allowed_at_epoch", {}))
            events = state.get("events", [])
            self.assertFalse(any(event.get("event") == "request_slot_reserved" for event in events))

    def test_actual_http_transmission_attempt_reserves_pacing(self):
        row = self.row("M2")
        state_path = Path(self.temporary.name) / "test_state.json"
        manifest_hash = "mock_hash"
        now_time = 1000.0
        called = []

        def mock_collector(cfg, r, raw_root):
            called.append(r["run_id"])
            out_dir = raw_root / r["run_id"]
            out_dir.mkdir(parents=True)
            return out_dir

        with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}, clear=False):
            result = collect_api_batch.run_batch(
                self.config,
                [row],
                manifest_hash=manifest_hash,
                state_path=state_path,
                raw_root=self.raw_root,
                now=lambda: now_time,
                collector=mock_collector,
            )

        self.assertEqual(called, [row["run_id"]])
        state = json.loads(state_path.read_text(encoding="utf-8"))
        groq_interval = self.config["batch_pacing"]["minimum_seconds_between_groq_requests"]
        self.assertEqual(state["provider_next_allowed_at_epoch"]["Groq"], now_time + groq_interval)
        events = state["events"]
        reservation_events = [e for e in events if e.get("event") == "request_slot_reserved"]
        self.assertEqual(len(reservation_events), 1)
        self.assertEqual(reservation_events[0]["run_id"], row["run_id"])
        self.assertEqual(reservation_events[0]["api_provider"], "Groq")

    def test_v2_3_zero_pacing_is_accepted_and_historical_v2_2_pacing_is_unchanged(self):
        self.assertEqual(collect_api_batch.minimum_interval(self.config, "Groq"), 0)
        self.assertEqual(collect_api_batch.minimum_interval(self.config, "OpenRouter"), 0)
        historical = collect_api_run.load_config(collect_api_run.CONFIG_V2_2)
        self.assertEqual(collect_api_batch.minimum_interval(historical, "Groq"), 2700)
        self.assertEqual(collect_api_batch.minimum_interval(historical, "OpenRouter"), 1800)

    def test_nonretryable_quota_failure_stops_batch_with_recovery_evidence(self):
        row = self.row("M2")
        state_path = Path(self.temporary.name) / "test_state.json"

        def quota_failure(_config, current_row, *, raw_root):
            directory = raw_root / current_row["run_id"]
            directory.mkdir(parents=True)
            (directory / "metadata.json").write_text(json.dumps({
                "collection_status": "failed", "failure_reason": "http_status_402"
            }), encoding="utf-8")
            raise ValueError("API collection failed with HTTP 402")

        with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}, clear=False):
            with self.assertRaisesRegex(ValueError, "HTTP 402"):
                collect_api_batch.run_batch(
                    self.config, [row], manifest_hash="mock_hash", state_path=state_path,
                    raw_root=self.raw_root, collector=quota_failure,
                )
        events = json.loads(state_path.read_text(encoding="utf-8"))["events"]
        self.assertEqual(events[-1]["event"], "batch_stopped_nonretryable_provider_failure")
        self.assertEqual(events[-1]["failure_reason"], "http_status_402")
        self.assertEqual(events[-1]["action"], "stopped_without_skipping_or_substitution")

    def test_completed_and_truncated_preserved_runs_are_skipped(self):
        row_completed = self.row("M1")
        row_completed["run_id"] = "API-v2.2-AUTH-FED-01-M1-R01"
        row_completed["collection_order"] = "1"
        row_truncated = self.row("M2")
        row_truncated["run_id"] = "API-v2.2-AUTH-FED-01-M2-R01"
        row_truncated["collection_order"] = "2"

        # Create preserved directories
        dir1 = self.raw_root / row_completed["run_id"]
        dir1.mkdir(parents=True)
        (dir1 / "metadata.json").write_text(json.dumps({"collection_status": "completed"}), encoding="utf-8")

        dir2 = self.raw_root / row_truncated["run_id"]
        dir2.mkdir(parents=True)
        (dir2 / "metadata.json").write_text(json.dumps({"collection_status": "truncated"}), encoding="utf-8")

        state_path = Path(self.temporary.name) / "test_state.json"
        manifest_hash = "mock_hash"
        called = []

        collect_api_batch.run_batch(
            self.config,
            [row_completed, row_truncated],
            manifest_hash=manifest_hash,
            state_path=state_path,
            raw_root=self.raw_root,
            limit=2,
            collector=lambda *args, **kwargs: called.append(args),
        )

        self.assertEqual(called, [])
        state = json.loads(state_path.read_text(encoding="utf-8"))
        skipped = [e for e in state["events"] if e.get("event") == "skipped_preserved_observation"]
        self.assertEqual(len(skipped), 2)
        self.assertEqual(skipped[0]["status"], "completed")
        self.assertEqual(skipped[1]["status"], "truncated")

    def test_v2_4_preserved_failed_run_is_skipped_and_next_row_continues(self):
        failed = self.row("M1")
        failed["run_id"] = "API-v2.4-AUTH-FED-02-M1-R01"
        failed["collection_order"] = "1"
        next_row = self.row("M2")
        next_row["run_id"] = "API-v2.4-AUTH-FED-02-M2-R01"
        next_row["collection_order"] = "2"
        failed_dir = self.raw_root / failed["run_id"]
        failed_dir.mkdir(parents=True)
        (failed_dir / "metadata.json").write_text(json.dumps({
            "collection_status": "failed",
            "failure_reason": "HTTP 200 response contains no non-empty assistant content",
        }), encoding="utf-8")
        called = []

        def collector(_config, row, *, raw_root):
            called.append((row["run_id"], row["model_id"], row["api_provider"]))
            directory = raw_root / row["run_id"]
            directory.mkdir(parents=True)
            (directory / "metadata.json").write_text(json.dumps({"collection_status": "completed"}), encoding="utf-8")
            return directory

        state_path = Path(self.temporary.name) / "v2_4_state.json"
        with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}, clear=False):
            collect_api_batch.run_batch(
                self.config,
                [failed, next_row],
                manifest_hash="v2.4-test",
                state_path=state_path,
                raw_root=self.raw_root,
                collector=collector,
                continue_after_failed=True,
            )
        self.assertEqual(called, [(next_row["run_id"], next_row["model_id"], next_row["api_provider"])])
        events = json.loads(state_path.read_text(encoding="utf-8"))["events"]
        self.assertEqual(events[0]["event"], "skipped_preserved_failed_observation")
        self.assertEqual(events[0]["action"], "continued_to_next_manifest_row_without_retry_or_substitution")

    def test_v2_4_failed_run_is_never_retried_or_substituted(self):
        failed = self.row("M1")
        failed["run_id"] = "API-v2.4-AUTH-FED-02-M1-R01"
        failed_dir = self.raw_root / failed["run_id"]
        failed_dir.mkdir(parents=True)
        (failed_dir / "metadata.json").write_text(json.dumps({
            "collection_status": "failed",
            "failure_reason": "http_status_402",
        }), encoding="utf-8")
        calls = []
        state_path = Path(self.temporary.name) / "v2_4_state.json"
        collect_api_batch.run_batch(
            self.config,
            [failed],
            manifest_hash="v2.4-test",
            state_path=state_path,
            raw_root=self.raw_root,
            collector=lambda *_args, **_kwargs: calls.append("called"),
            continue_after_failed=True,
        )
        self.assertEqual(calls, [])
        self.assertEqual(
            json.loads(state_path.read_text(encoding="utf-8"))["events"][0]["status"],
            "failed",
        )

    def test_v2_3_existing_failed_run_blocks_batch_continuation(self):
        failed = self.row("M1")
        failed["run_id"] = "API-v2.3-AUTH-FED-02-M1-R01"
        failed_dir = self.raw_root / failed["run_id"]
        failed_dir.mkdir(parents=True)
        (failed_dir / "metadata.json").write_text(json.dumps({
            "collection_status": "failed",
            "failure_reason": "HTTP 200 response contains no non-empty assistant content",
        }), encoding="utf-8")
        calls = []
        state_path = Path(self.temporary.name) / "v2_3_state.json"
        result = collect_api_batch.run_batch(
            self.config,
            [failed],
            manifest_hash="v2.3-test",
            state_path=state_path,
            raw_root=self.raw_root,
            collector=lambda *_args, **_kwargs: calls.append("called"),
            continue_after_failed=False,
        )
        self.assertEqual(result["blocked_run_id"], failed["run_id"])
        self.assertEqual(result["existing_status"], "failed")
        self.assertEqual(calls, [])
        events = json.loads(state_path.read_text(encoding="utf-8"))["events"]
        self.assertEqual(events[0]["event"], "temporarily_blocked_existing_run")
        self.assertEqual(events[0]["status"], "failed")

    def test_http_200_with_empty_assistant_content_is_failed_nonretryable_run(self):
        row = self.row("M1")
        calls = []

        def transport(*_):
            calls.append(1)
            return collect_api_run.HTTPResult(
                200,
                {},
                json.dumps({
                    "model": row["model_id"],
                    "choices": [{"message": {"content": None}, "finish_reason": "length"}],
                    "usage": {},
                }).encode(),
            )

        with patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key"}, clear=False):
            with self.assertRaisesRegex(ValueError, "HTTP 200 response contains no non-empty assistant content"):
                collect_api_run.collect_row(
                    self.config,
                    row,
                    raw_root=self.raw_root,
                    transport=transport,
                    sleeper=lambda _: None,
                )
        self.assertEqual(len(calls), 1)  # Not retried
        meta_path = self.raw_root / row["run_id"] / "metadata.json"
        self.assertTrue(meta_path.exists())
        metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        self.assertEqual(metadata["collection_status"], "failed")
        self.assertEqual(metadata["failure_reason"], "HTTP 200 response contains no non-empty assistant content")

    def test_historical_observations_are_never_regenerated_by_v2_3(self):
        rows_v2_3 = create_api_manifest.make_rows(
            self.config,
            create_api_manifest.load_frozen_tasks(),
            rendered_dir=create_api_manifest.DEFAULT_RENDERED_DIR,
            run_prefix="API-v2.3",
        )
        for row in rows_v2_3:
            self.assertTrue(row["run_id"].startswith("API-v2.3-"))
            self.assertFalse(row["run_id"].startswith("API-v2.2-"))
            self.assertFalse(row["run_id"].startswith("API-v2.1-"))
            self.assertFalse(row["run_id"].startswith("API-AUTH-"))


if __name__ == "__main__":
    unittest.main()
