import csv
import hashlib
import json
import os
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import collect_api_batch
import collect_api_run
import create_api_manifest
import create_experiment_freeze_v2_6
import render_api_prompts

CONFIG = ROOT / "config/api_model_set_1.4.0.json"
MANIFEST = ROOT / "manifests/api_final_v2.6.0_manifest.csv"
STATE = ROOT / "data/final/api_batch_state_v2.6.0.json"
CEILINGS = {"M1": 64000, "M2": 32768, "M3": 65536, "M4": 65536}


class V26Tests(unittest.TestCase):
    def test_model_specific_requests_and_historical_v25(self):
        config = collect_api_run.load_config(CONFIG)
        self.assertEqual(config["model_set_version"], "api-model-set-1.4.0")
        self.assertNotIn("max_output_tokens", config["candidate_common_parameters"])
        with tempfile.TemporaryDirectory() as tmp:
            altered = json.loads(json.dumps(config))
            altered["models"][0]["max_output_tokens"] = 16000
            path = Path(tmp) / "altered.json"
            path.write_text(json.dumps(altered))
            with self.assertRaises(ValueError):
                collect_api_run.load_config(path)
        for model in config["models"]:
            with self.subTest(condition=model["condition_id"]), patch.dict(os.environ, {model["api_key_environment_variable"]: "test-only"}):
                url, headers, body = collect_api_run.build_request(config, model, b"prompt")
                request = json.loads(body)
                self.assertEqual(request[model["output_token_parameter"]], CEILINGS[model["condition_id"]])
                self.assertEqual(request["messages"], [{"role": "user", "content": "prompt"}])
                self.assertEqual((request["temperature"], request["top_p"]), (0.6, 0.95))
                self.assertEqual(request["tool_choice"], "none")
                self.assertNotIn("tools", request)
                self.assertNotIn("models", request)
                self.assertNotIn("seed", request)
                if model["condition_id"] == "M2":
                    self.assertEqual(url, "https://openrouter.ai/api/v1/chat/completions")
                    self.assertIn("X-OpenRouter-Metadata", headers)
                    self.assertEqual(model["output_token_parameter"], "max_tokens")
                    self.assertEqual(request["provider"], {"allow_fallbacks": False, "require_parameters": True, "order": ["darkbloom"], "only": ["darkbloom"]})
                elif model["api_provider"] == "OpenRouter":
                    self.assertEqual(request["provider"]["order"], [model["openrouter_routing"]["underlying_provider_slug"]])
                    self.assertNotIn("only", request["provider"])
                else:
                    self.assertEqual(url, "https://api.groq.com/openai/v1/chat/completions")
                    self.assertNotIn("provider", request)
        old = collect_api_run.load_config(ROOT / "config/api_model_set_1.3.0.json")
        for model in old["models"]:
            with patch.dict(os.environ, {model["api_key_environment_variable"]: "test-only"}):
                _, _, body = collect_api_run.build_request(old, model, b"prompt")
            self.assertEqual(json.loads(body)[model["output_token_parameter"]], 16000)

    def test_darkbloom_configuration_is_fail_closed(self):
        config = collect_api_run.load_config(CONFIG)
        rows = collect_api_batch.ordered_rows(MANIFEST)
        m2_row = next(row for row in rows if row["model_condition_id"] == "M2")
        model = config["models"][1]
        collect_api_run.validate_collection_ready(config, m2_row, model)
        for key, value in (("underlying_provider_slug", "other"), ("only_pinned_provider", False), ("allow_fallbacks", True), ("require_parameters", False)):
            altered = json.loads(json.dumps(model))
            altered["openrouter_routing"][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                collect_api_run.validate_collection_ready(config, m2_row, altered)

    def test_prompts_manifest_state_and_zero_raw(self):
        template = ROOT / "prompts/prompt_template_v2.6.0.md"
        self.assertEqual(template.read_bytes(), (ROOT / "prompts/prompt_template_v2.5.0.md").read_bytes())
        self.assertEqual(hashlib.sha256(template.read_bytes()).hexdigest(), "8d3971d6f9f86dfd98a4b5c49c0c13d734b7f650744da682225195f2ea49b528")
        expected = render_api_prompts.expected_rendered(template)
        self.assertEqual(len(expected), 30)
        for task_id, data in expected.items():
            self.assertEqual((ROOT / f"data/generated_prompts/v2.6.0/{task_id}.txt").read_bytes(), data)
            self.assertEqual((ROOT / f"data/generated_prompts/v2.5.0/{task_id}.txt").read_bytes(), data)
        rows = collect_api_batch.ordered_rows(MANIFEST)
        self.assertEqual(len({row["run_id"] for row in rows}), 360)
        self.assertTrue(all(row["collection_status"] == "pending" and row["run_id"].startswith("API-v2.6-") for row in rows))
        self.assertEqual(Counter(row["model_condition_id"] for row in rows), {m: 90 for m in CEILINGS})
        self.assertEqual(Counter(row["run_repetition"] for row in rows), {r: 120 for r in ("R01", "R02", "R03")})
        self.assertEqual(Counter(row["category"] for row in rows), {c: 60 for c in ("AUTH-FED", "DATA-ADV", "DIST-OBS", "DOC-BINARY", "ENT-INT", "PKI-CRYPTO")})
        expected_rows = create_api_manifest.make_rows(collect_api_run.load_config(CONFIG), create_api_manifest.load_frozen_tasks(), ROOT / "data/generated_prompts/v2.6.0", "API-v2.6")
        self.assertEqual(MANIFEST.read_bytes(), create_api_manifest.csv_bytes(expected_rows))
        # The real v2.6 state and raw root legitimately progress during collection.
        # Verify the prospective initial-state contract with an isolated fixture.
        with tempfile.TemporaryDirectory() as tmp:
            fixture_state = Path(tmp) / "initial-state.json"
            initial = collect_api_batch.load_state(
                fixture_state, hashlib.sha256(MANIFEST.read_bytes()).hexdigest()
            )
            self.assertEqual(initial["events"], [])
            self.assertEqual(initial["provider_next_allowed_at_epoch"], {})
            self.assertEqual(initial["manifest_sha256"], hashlib.sha256(MANIFEST.read_bytes()).hexdigest())
            self.assertFalse(fixture_state.exists())
            self.assertEqual(list((Path(tmp) / "raw").glob("API-v2.6-*")), [])

    def test_dry_run_and_freeze(self):
        record = json.loads((ROOT / "config/experiment_freeze_v2.6.0.json").read_text())
        # The verifier is deliberately progress-aware: it checks immutable frozen
        # inputs after collection has advanced without rebuilding the initial state.
        with patch.object(sys, "argv", ["create_experiment_freeze_v2_6.py", "--check"]):
            self.assertEqual(create_experiment_freeze_v2_6.main(), 0)
        self.assertEqual((ROOT / "docs/experiment_freeze_v2.6.0.md").read_text(), create_experiment_freeze_v2_6.markdown(record))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = collect_api_batch.run_batch(
                collect_api_run.load_config(CONFIG), collect_api_batch.ordered_rows(MANIFEST),
                manifest_hash=hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
                state_path=root / "initial-state.json", raw_root=root / "raw",
                dry_run=True, continue_after_failed=True,
            )
            self.assertEqual(result, {"next_run_id": "API-v2.6-AUTH-FED-01-M1-R01", "collection_order": 1, "api_provider": "OpenRouter", "wait_seconds": 0.0})
            self.assertFalse((root / "initial-state.json").exists())
            self.assertEqual(list((root / "raw").glob("API-v2.6-*")), [])

    def test_m2_response_provenance_and_truncation_without_network(self):
        config = collect_api_run.load_config(CONFIG)
        row = next(row for row in collect_api_batch.ordered_rows(MANIFEST) if row["model_condition_id"] == "M2")
        payload = {"id": "test", "model": "qwen/qwen3.8-27b", "provider": "darkbloom", "choices": [{"message": {"content": "partial"}, "finish_reason": "length"}], "usage": {"completion_tokens": 32768}}
        calls = []
        def transport(url, headers, body, timeout):
            calls.append((url, json.loads(body)))
            return collect_api_run.HTTPResult(200, {"Content-Type": "application/json", "X-Unrelated": "omit"}, json.dumps(payload).encode())
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-only"}):
            path = collect_api_run.collect_row(config, row, raw_root=Path(tmp), transport=transport)
            metadata = json.loads((path / "metadata.json").read_text())
            self.assertEqual(metadata["collection_status"], "truncated")
            self.assertEqual(metadata["response_completion_status"], "TRUNCATED")
            self.assertEqual(metadata["returned_model_id"], "qwen/qwen3.8-27b")
            self.assertEqual(metadata["resolved_underlying_provider"], "darkbloom")
            self.assertEqual(metadata["protocol_deviations"], [])
            self.assertEqual(metadata["sampling_parameters"]["max_output_tokens"], 32768)
            self.assertEqual(metadata["safe_response_headers"], {"content-type": "application/json"})
            self.assertEqual(len(metadata["retry_history"]), 1)
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0][1]["provider"]["only"], ["darkbloom"])
        payload["model"] = "other/model"
        payload["provider"] = "other-provider"
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-only"}):
            with self.assertRaises(ValueError):
                collect_api_run.collect_row(config, row, raw_root=Path(tmp), transport=transport)
            path = Path(tmp) / row["run_id"]
            metadata = json.loads((path / "metadata.json").read_text())
            self.assertEqual(metadata["collection_status"], "failed")
            self.assertEqual(metadata["failure_reason"], "provider_identity_mismatch")
            self.assertEqual(metadata["returned_model_id"], "other/model")
            self.assertEqual(metadata["resolved_underlying_provider"], "other-provider")
            self.assertEqual(set(metadata["protocol_deviations"]), {"returned_model_id_differs_from_requested_model_id", "resolved_provider_differs_from_frozen_provider"})
            self.assertTrue((path / "provider_response.json").exists())


if __name__ == "__main__":
    unittest.main()
