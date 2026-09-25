#!/usr/bin/env python3
"""Synthetic, offline tests for PIPE-06 risk-model-1.0.0 scoring.

All fixtures below are synthetic and invented for this test only. None of them
represent a real collected observation, a real package name, or a real research
result; the v2.2 `webauthn2` candidate and any other live finding are never
referenced or scored here.
"""

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import score_risk_findings as scorer


def eligible_candidate(finding_id="FIND-0001", classification="CONFIRMED_HALLUCINATION",
                        impact=3, detectability=3, evidence_status="resolved", **overrides):
    candidate = {
        "finding_id": finding_id,
        "run_ids": ["SYN-RUN-0001"],
        "normalized_package": "synthetic-fixture-package",
        "affected_version_or_range": None,
        "research_classification": classification,
        "evidence_status": evidence_status,
        "source_evidence": "Synthetic response text: `npm install synthetic-fixture-package`.",
        "expected_consequence": "Synthetic dependency install would fail because the name does not exist.",
        "impact_score": impact,
        "impact_rationale": "Synthetic rationale: install failure with limited downstream effect.",
        "detectability_score": detectability,
        "detectability_rationale": "Synthetic rationale: caught at dependency resolution time.",
        "security_sensitive_context": False,
        "security_sensitive_rationale": "Synthetic rationale: no auth/crypto/secret-handling path involved.",
        "assessor_id": "synthetic-assessor",
        "assessed_at": "2026-09-22T00:00:00Z",
        "provenance": ["synthetic://pipe-05/FIND-0001"],
    }
    candidate.update(overrides)
    return candidate


def ineligible_candidate(finding_id="FIND-0002", classification="VALID",
                          evidence_status="resolved", **overrides):
    candidate = {
        "finding_id": finding_id,
        "run_ids": ["SYN-RUN-0002"],
        "normalized_package": "synthetic-other-package",
        "affected_version_or_range": None,
        "research_classification": classification,
        "evidence_status": evidence_status,
        "source_evidence": None,
        "expected_consequence": None,
        "impact_score": None,
        "impact_rationale": None,
        "detectability_score": None,
        "detectability_rationale": None,
        "security_sensitive_context": False,
        "security_sensitive_rationale": "Synthetic rationale: not applicable to an unscored finding.",
        "assessor_id": "synthetic-assessor",
        "assessed_at": "2026-09-22T00:00:00Z",
        "provenance": ["synthetic://pipe-05/FIND-0002"],
    }
    candidate.update(overrides)
    return candidate


class MinimumMaximumEligibleScoreTests(unittest.TestCase):
    def test_minimum_eligible_score(self):
        record = scorer.score_finding(eligible_candidate(impact=1, detectability=1))
        self.assertTrue(record["eligibility"])
        self.assertEqual(record["risk_score"], 1)
        self.assertEqual(record["risk_band"], "LOW")

    def test_maximum_eligible_score(self):
        record = scorer.score_finding(eligible_candidate(impact=5, detectability=4))
        self.assertTrue(record["eligibility"])
        self.assertEqual(record["risk_score"], 20)
        self.assertEqual(record["risk_band"], "CRITICAL")


class ImpactTimesDetectabilityTests(unittest.TestCase):
    def test_calculation_is_multiplicative(self):
        cases = [(1, 1, 1), (2, 3, 6), (3, 4, 12), (5, 2, 10), (4, 4, 16)]
        for impact, detectability, expected in cases:
            with self.subTest(impact=impact, detectability=detectability):
                record = scorer.score_finding(eligible_candidate(impact=impact, detectability=detectability))
                self.assertEqual(record["risk_score"], expected)


class RiskBandBoundaryTests(unittest.TestCase):
    def test_every_documented_band_boundary(self):
        # (impact, detectability, expected_score, expected_band) covering all four
        # boundary edges: 1-4 LOW, 5-8 MODERATE, 9-14 HIGH, 15-20 CRITICAL.
        cases = [
            (1, 1, 1, "LOW"),
            (2, 2, 4, "LOW"),
            (1, 4, 4, "LOW"),
            (5, 1, 5, "MODERATE"),
            (2, 4, 8, "MODERATE"),
            (3, 3, 9, "HIGH"),
            (5, 2, 10, "HIGH"),
            (4, 3, 12, "HIGH"),
            (4, 4, 16, "CRITICAL"),
            (5, 3, 15, "CRITICAL"),
            (5, 4, 20, "CRITICAL"),
        ]
        for impact, detectability, expected_score, expected_band in cases:
            with self.subTest(impact=impact, detectability=detectability):
                record = scorer.score_finding(eligible_candidate(impact=impact, detectability=detectability))
                self.assertEqual(record["risk_score"], expected_score)
                self.assertEqual(record["risk_band"], expected_band)

    def test_risk_band_function_direct_boundaries(self):
        self.assertEqual(scorer.risk_band(1), "LOW")
        self.assertEqual(scorer.risk_band(4), "LOW")
        self.assertEqual(scorer.risk_band(5), "MODERATE")
        self.assertEqual(scorer.risk_band(8), "MODERATE")
        self.assertEqual(scorer.risk_band(9), "HIGH")
        self.assertEqual(scorer.risk_band(14), "HIGH")
        self.assertEqual(scorer.risk_band(15), "CRITICAL")
        self.assertEqual(scorer.risk_band(20), "CRITICAL")
        self.assertIsNone(scorer.risk_band(None))


class SecuritySensitiveFlagTests(unittest.TestCase):
    def test_flag_is_independent_of_numeric_score(self):
        low_but_sensitive = scorer.score_finding(
            eligible_candidate(finding_id="FIND-LOW-SENS", impact=1, detectability=1,
                                security_sensitive_context=True,
                                security_sensitive_rationale="Synthetic rationale: touches auth token handling."))
        high_not_sensitive = scorer.score_finding(
            eligible_candidate(finding_id="FIND-HIGH-NOSENS", impact=5, detectability=4,
                                security_sensitive_context=False,
                                security_sensitive_rationale="Synthetic rationale: purely cosmetic formatting path."))
        self.assertEqual(low_but_sensitive["risk_score"], 1)
        self.assertTrue(low_but_sensitive["security_sensitive_context"])
        self.assertEqual(high_not_sensitive["risk_score"], 20)
        self.assertFalse(high_not_sensitive["security_sensitive_context"])


class EligibilityPathTests(unittest.TestCase):
    def test_confirmed_hallucination_eligible_path(self):
        record = scorer.score_finding(eligible_candidate(classification="CONFIRMED_HALLUCINATION"))
        self.assertTrue(record["eligibility"])
        self.assertIsNotNone(record["risk_score"])
        self.assertIsNotNone(record["risk_band"])

    def test_secondary_eligible_categories_also_score(self):
        for classification in ("PACKAGE_VERSION_HALLUCINATION", "PACKAGE_API_HALLUCINATION",
                                "PACKAGE_CAPABILITY_HALLUCINATION"):
            with self.subTest(classification=classification):
                record = scorer.score_finding(eligible_candidate(
                    finding_id=f"FIND-{classification}", classification=classification))
                self.assertTrue(record["eligibility"])
                self.assertIsNotNone(record["risk_score"])

    def test_valid_finding_remains_unscored(self):
        record = scorer.score_finding(ineligible_candidate(classification="VALID"))
        self.assertFalse(record["eligibility"])
        self.assertIsNone(record["risk_score"])
        self.assertIsNone(record["risk_band"])

    def test_ambiguous_finding_remains_unscored(self):
        record = scorer.score_finding(ineligible_candidate(classification="AMBIGUOUS"))
        self.assertFalse(record["eligibility"])
        self.assertIsNone(record["risk_score"])
        self.assertIsNone(record["risk_band"])

    def test_legacy_or_removed_remains_unscored(self):
        # The frozen protocol's Eligibility section explicitly excludes
        # LEGACY_OR_REMOVED; it does not say otherwise, so it stays unscored.
        record = scorer.score_finding(ineligible_candidate(classification="LEGACY_OR_REMOVED"))
        self.assertFalse(record["eligibility"])
        self.assertIsNone(record["risk_score"])
        self.assertIsNone(record["risk_band"])

    def test_builtin_or_local_remains_unscored(self):
        record = scorer.score_finding(ineligible_candidate(classification="BUILTIN_OR_LOCAL"))
        self.assertFalse(record["eligibility"])
        self.assertIsNone(record["risk_score"])

    def test_unresolved_evidence_remains_unscored(self):
        # research_classification is itself an eligible category, but the
        # scoring evidence is not yet resolved, so the finding must stay unscored.
        record = scorer.score_finding(ineligible_candidate(
            classification="CONFIRMED_HALLUCINATION", evidence_status="unresolved"))
        self.assertFalse(record["eligibility"])
        self.assertIsNone(record["risk_score"])
        self.assertIsNone(record["risk_band"])
        self.assertIn("unresolved", record["eligibility_basis"])


class NullEncodingTests(unittest.TestCase):
    def test_null_used_for_unscored_score_and_band_never_zero(self):
        for classification in scorer.INELIGIBLE_CATEGORIES:
            with self.subTest(classification=classification):
                record = scorer.score_finding(ineligible_candidate(
                    finding_id=f"FIND-{classification}", classification=classification))
                self.assertIsNone(record["risk_score"])
                self.assertIsNone(record["risk_band"])
                self.assertNotEqual(record["risk_score"], 0)


class InvalidRangeRejectionTests(unittest.TestCase):
    def test_invalid_impact_range_rejected(self):
        for bad_impact in (0, 6, -1):
            with self.subTest(impact=bad_impact):
                with self.assertRaises(ValueError):
                    scorer.score_finding(eligible_candidate(impact=bad_impact))

    def test_invalid_detectability_range_rejected(self):
        for bad_detectability in (0, 5, -1):
            with self.subTest(detectability=bad_detectability):
                with self.assertRaises(ValueError):
                    scorer.score_finding(eligible_candidate(detectability=bad_detectability))


class MissingRationaleRejectionTests(unittest.TestCase):
    def test_missing_impact_rationale_rejected(self):
        with self.assertRaises(ValueError):
            scorer.score_finding(eligible_candidate(impact_rationale=None))

    def test_missing_detectability_rationale_rejected(self):
        with self.assertRaises(ValueError):
            scorer.score_finding(eligible_candidate(detectability_rationale=None))

    def test_missing_source_evidence_rejected(self):
        with self.assertRaises(ValueError):
            scorer.score_finding(eligible_candidate(source_evidence=None))

    def test_missing_expected_consequence_rejected(self):
        with self.assertRaises(ValueError):
            scorer.score_finding(eligible_candidate(expected_consequence=None))

    def test_score_on_ineligible_finding_rejected(self):
        with self.assertRaises(ValueError):
            scorer.score_finding(ineligible_candidate(classification="AMBIGUOUS", impact_score=3))


class DeterministicOrderingAndRerunTests(unittest.TestCase):
    def test_deterministic_output_ordering(self):
        candidates = [
            eligible_candidate(finding_id="FIND-C"),
            eligible_candidate(finding_id="FIND-A"),
            ineligible_candidate(finding_id="FIND-B", classification="VALID"),
        ]
        records = scorer.score_findings(candidates)
        self.assertEqual([record["finding_id"] for record in records], ["FIND-A", "FIND-B", "FIND-C"])

    def test_rerun_determinism(self):
        candidates = [
            eligible_candidate(finding_id="FIND-X", impact=3, detectability=4),
            ineligible_candidate(finding_id="FIND-Y", classification="AMBIGUOUS"),
        ]
        first = scorer.score_findings(copy.deepcopy(candidates))
        second = scorer.score_findings(copy.deepcopy(candidates))
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))

    def test_duplicate_finding_id_rejected(self):
        candidates = [eligible_candidate(finding_id="DUP"), eligible_candidate(finding_id="DUP")]
        with self.assertRaises(ValueError):
            scorer.score_findings(candidates)


if __name__ == "__main__":
    unittest.main()
