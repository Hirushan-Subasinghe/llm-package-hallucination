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
import run_api_interface_suitability as suitability


class APIInterfaceSuitabilityTests(unittest.TestCase):
    def test_frozen_wrapper_and_excluded_task_render_exactly(self):
        protocol, task, prompt = suitability.load_and_validate_inputs()
        template = suitability.TEMPLATE_PATH.read_text(encoding="utf-8")
        self.assertEqual(prompt, template.replace("[TASK_DESCRIPTION]", task["prompt"]).encode())
        self.assertEqual(protocol["conditions"], ["M1", "M2", "M3", "M4"])
        self.assertEqual(len(protocol["pass_criteria"]), 7)
        self.assertTrue(protocol["excluded_from_official_dataset"])
        self.assertTrue(protocol["excluded_from_hallucination_metrics"])

    def test_interface_assessment_accepts_substantive_inline_response(self):
        content = """package.json\n```json\n{}\n```\nsrc/server.ts\n```ts\nconsole.log('ok')\n```"""
        result = suitability.interface_assessment(
            http_model_response_valid=True,
            message={"role": "assistant", "content": content},
            content=content,
            finish_reason="stop",
        )
        self.assertEqual(result["suitability"], "PASS")
        self.assertTrue(result["inline_implementation"])

    def test_interface_assessment_rejects_structured_and_simulated_tool_calls(self):
        structured = suitability.interface_assessment(
            http_model_response_valid=True,
            message={"tool_calls": [{"function": {"name": "bash"}}]},
            content="I will inspect the repository.",
            finish_reason="tool_calls",
        )
        simulated = suitability.interface_assessment(
            http_model_response_valid=True,
            message={},
            content="<tool_call><function=read_file></function></tool_call>",
            finish_reason="stop",
        )
        self.assertEqual(structured["suitability"], "FAIL")
        self.assertTrue(structured["structured_tool_calls_returned"])
        self.assertEqual(simulated["suitability"], "FAIL")
        self.assertTrue(simulated["simulated_tool_markup"])

    def test_one_request_uses_frozen_settings_and_preserves_first_valid_response(self):
        config = copy.deepcopy(collect_api_run.load_config(collect_api_run.DEFAULT_CONFIG))
        model = config["models"][2]
        content = "package.json\n```json\n{}\n```\nsrc/index.ts\n```ts\nexport {}\n```"
        response = {
            "id": "suitability-test",
            "model": model["model_id"],
            "choices": [{"message": {"role": "assistant", "content": content}, "finish_reason": "stop"}],
            "usage": {"completion_tokens": 20},
        }
        calls = []

        def transport(*args):
            calls.append(args)
            return collect_api_run.HTTPResult(200, {}, json.dumps(response).encode())

        with tempfile.TemporaryDirectory() as temporary, \
                patch.object(suitability, "OUTPUT_ROOT", Path(temporary)), \
                patch.object(suitability, "request_once", side_effect=transport), \
                patch.dict("os.environ", {"GROQ_API_KEY": "test-only-secret"}, clear=False):
            metadata = suitability.run_one(config, model, b"test prompt")
            directory = Path(temporary) / "SUITABILITY-API-001-M3"
            request = json.loads((directory / "request.json").read_text())
            self.assertEqual(len(calls), 1)
            self.assertEqual(request["messages"], [{"role": "user", "content": "test prompt"}])
            self.assertEqual(request["temperature"], 0.6)
            self.assertEqual(request["top_p"], 0.95)
            self.assertEqual(request["max_completion_tokens"], 6000)
            self.assertEqual(request["tool_choice"], "none")
            self.assertNotIn("tools", request)
            self.assertNotIn("seed", request)
            self.assertEqual(metadata["interface_assessment"]["suitability"], "PASS")
            self.assertEqual((directory / "response.md").read_text(), content)
            for path in directory.rglob("*"):
                if path.is_file():
                    self.assertNotIn(b"test-only-secret", path.read_bytes())


if __name__ == "__main__":
    unittest.main()
