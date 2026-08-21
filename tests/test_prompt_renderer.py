import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from experiment.prompt_renderer import (
    PLACEHOLDER,
    PromptValidationError,
    read_tasks,
    read_template,
    render_prompts,
)

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "prompts/templates/master_prompt_v0.1.0.md"
TASKS = ROOT / "prompts/tasks/pilot_samples.jsonl"


class PromptRendererTests(unittest.TestCase):
    def test_valid_template_rendering_and_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_root = Path(directory) / "rendered"
            manifest = render_prompts(
                TEMPLATE, TASKS, output_root, template_version="0.1.0"
            )
            self.assertEqual(len(manifest), 6)
            for entry in manifest:
                prompt_path = output_root / "pilot-0.1.0" / f'{entry["task_id"]}.txt'
                self.assertEqual(entry["rendered_prompt_path"], prompt_path.as_posix())
                self.assertTrue(prompt_path.is_file())
                self.assertNotIn(PLACEHOLDER, prompt_path.read_text(encoding="utf-8"))

    def test_template_requires_exactly_one_placeholder(self) -> None:
        for contents in ("no placeholder", f"{PLACEHOLDER} {PLACEHOLDER}"):
            with self.subTest(contents=contents), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "template.md"
                path.write_text(contents, encoding="utf-8")
                with self.assertRaises(PromptValidationError):
                    read_template(path)

    def test_missing_required_task_field_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tasks.jsonl"
            path.write_text('{"task_id":"A"}\n', encoding="utf-8")
            with self.assertRaisesRegex(PromptValidationError, "missing fields"):
                read_tasks(path)

    def test_duplicate_task_ids_are_rejected(self) -> None:
        task = {
            "task_id": "A",
            "category": "Category",
            "difficulty": "medium",
            "task_description": "Task",
            "task_set_version": "pilot",
            "status": "sample",
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tasks.jsonl"
            line = json.dumps(task)
            path.write_text(f"{line}\n{line}\n", encoding="utf-8")
            with self.assertRaisesRegex(PromptValidationError, "duplicate task_id"):
                read_tasks(path)

    def test_six_pilot_records_are_parsed(self) -> None:
        self.assertEqual(len(read_tasks(TASKS)), 6)

    def test_second_render_is_byte_identical_and_hash_matches(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_root = Path(directory) / "rendered"
            first = render_prompts(
                TEMPLATE, TASKS, output_root, template_version="0.1.0"
            )
            first_bytes = {
                path.relative_to(output_root): path.read_bytes()
                for path in output_root.rglob("*")
                if path.is_file()
            }
            second = render_prompts(
                TEMPLATE, TASKS, output_root, template_version="0.1.0"
            )
            second_bytes = {
                path.relative_to(output_root): path.read_bytes()
                for path in output_root.rglob("*")
                if path.is_file()
            }
            self.assertEqual(first, second)
            self.assertEqual(first_bytes, second_bytes)
            for entry in second:
                path = Path(entry["rendered_prompt_path"])
                self.assertEqual(
                    entry["sha256"], hashlib.sha256(path.read_bytes()).hexdigest()
                )

    def test_provider_names_are_absent_from_master_template(self) -> None:
        template = TEMPLATE.read_text(encoding="utf-8").casefold()
        for name in (
            "chatgpt",
            "claude",
            "gemini",
            "copilot",
            "openai",
            "anthropic",
            "google",
            "github",
        ):
            with self.subTest(name=name):
                self.assertNotIn(name, template)

    def test_experimental_terminology_is_absent_from_master_template(self) -> None:
        template = TEMPLATE.read_text(encoding="utf-8").casefold()
        for term in (
            "hallucination",
            "slopsquatting",
            "package validity",
            "registry verification",
            "package exists",
            "package does not exist",
        ):
            with self.subTest(term=term):
                self.assertNotIn(term, template)


if __name__ == "__main__":
    unittest.main()
