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
            "task_id": "AUTH-001",
            "category": "Authentication and Authorization",
            "difficulty": "medium",
            "task_description": "Task",
            "task_set_version": "pilot-0.1.0",
            "status": "sample",
            "ecosystem": "node.js",
            "runtime": "Node.js",
            "package_manager": "npm",
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

    def test_metadata_only_changes_preserve_rendered_prompt_bytes(self) -> None:
        base = read_tasks(TASKS)[0].copy()
        changed = base.copy()
        changed.update(
            difficulty="hard",
            task_family="metadata-only-family",
            external_dependency_requirement="required",
            security_criticality="low",
            notes="metadata-only note",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first_path = root / "first.jsonl"
            second_path = root / "second.jsonl"
            first_path.write_text(json.dumps(base) + "\n", encoding="utf-8")
            second_path.write_text(json.dumps(changed) + "\n", encoding="utf-8")
            first = render_prompts(TEMPLATE, first_path, root / "first-rendered", template_version="0.1.0")[0]
            second = render_prompts(TEMPLATE, second_path, root / "second-rendered", template_version="0.1.0")[0]
            first_bytes = (root / "first-rendered" / base["task_set_version"] / "AUTH-001.txt").read_bytes()
            second_bytes = (root / "second-rendered" / changed["task_set_version"] / "AUTH-001.txt").read_bytes()
            self.assertEqual(first_bytes, second_bytes)
            self.assertEqual(first["sha256"], second["sha256"])

    def test_approved_pilot_prompt_hashes_are_stable(self) -> None:
        expected = {
            "AUTH-001": "260b4da6c0d8ac7b4ac255d6e6f035c82a11c7f59f9bcda9c1e0dd27d87812cd",
            "DB-001": "b169bff19311d82b829a7385c6d3fb40be81aa0d96693a2719b551a2f4f0d61e",
            "FILE-001": "cf4b6108c2db8c7dd6a400fe7c4cf942a1416b126aa9debb93ef59c908a453cd",
            "API-001": "4a3712b6d65c039c4bddd4c0277bef05b521ac38ef7084970154a85b673f633e",
            "SEC-001": "dc9e1bf8e50c4bbdfca5a3e5a813eb6a318c1b7d75968ecf163c512b58e48a83",
            "LOG-001": "0fc67b42bfa6d86d7dba32e8cd1efa7dea7d349a7317df3f64b5028d64be5a0b",
        }
        with tempfile.TemporaryDirectory() as directory:
            manifest = render_prompts(TEMPLATE, TASKS, Path(directory), template_version="0.1.0")
        self.assertEqual({entry["task_id"]: entry["sha256"] for entry in manifest}, expected)


if __name__ == "__main__":
    unittest.main()
