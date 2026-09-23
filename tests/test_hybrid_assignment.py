import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import create_hybrid_assignment_v1_0 as hybrid  # noqa: E402


class HybridAssignmentTests(unittest.TestCase):
    def test_current_derived_assignment_verifies(self):
        facts = hybrid.verify_assignment(hybrid.read_assignment())
        self.assertEqual(facts["attempted_count"], 119)
        self.assertEqual(len(facts["additional_rows"]), 61)
        self.assertEqual(len(facts["manual_rows"]), 180)
        self.assertEqual(facts["per_model"], {
            "M1": {"api": 40, "manual": 50},
            "M2": {"api": 40, "manual": 50},
            "M3": {"api": 41, "manual": 49},
            "M4": {"api": 59, "manual": 31},
        })

    def test_artifact_is_exact_deterministic_derivation(self):
        expected = hybrid.csv_bytes(hybrid.make_assignment())
        self.assertEqual(hybrid.ASSIGNMENT.read_bytes(), expected)


if __name__ == "__main__":
    unittest.main()
