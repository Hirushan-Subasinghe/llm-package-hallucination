import json
import re
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS_PATH = ROOT / "prompts" / "tasks" / "final_2.0.0.jsonl"
CATEGORIES = {"AUTH-FED", "PKI-CRYPTO", "DOC-BINARY", "ENT-INT", "DATA-ADV", "DIST-OBS"}
OUTCOME_INDUCING_PATTERNS = (
    r"\bhallucinat(?:e|ed|ion|ions)\b",
    r"\binvent packages?\b",
    r"\bobscure packages?\b",
    r"\bpackages? likely to fail\b",
    r"\bverify every package exists\b",
    r"\bonly use real npm packages\b",
)


class TaskSetV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tasks = [json.loads(line) for line in TASKS_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]

    def test_exact_balanced_shape_and_unique_ids(self):
        self.assertEqual(len(self.tasks), 30)
        self.assertEqual(Counter(task["category"] for task in self.tasks), Counter({category: 5 for category in CATEGORIES}))
        ids = [task["task_id"] for task in self.tasks]
        self.assertEqual(len(ids), len(set(ids)))
        for task in self.tasks:
            self.assertRegex(task["task_id"], rf"^{re.escape(task['category'])}-0[1-5]$")

    def test_node_npm_version_and_neutral_wording(self):
        for task in self.tasks:
            self.assertEqual(task["task_set_version"], "final-2.0.0")
            self.assertEqual(task["ecosystem"], "npm")
            self.assertEqual(task["runtime"], "Node.js")
            self.assertIn("complete package.json", task["prompt"])
            self.assertIn("exact dependency versions", task["prompt"])
            self.assertIn("Use suitable npm packages where appropriate", task["prompt"])

    def test_no_outcome_inducing_terms(self):
        for task in self.tasks:
            for pattern in OUTCOME_INDUCING_PATTERNS:
                self.assertIsNone(re.search(pattern, task["prompt"], flags=re.IGNORECASE), (task["task_id"], pattern))


if __name__ == "__main__":
    unittest.main()
