"""Synthetic-only D036/PIPE-10 tests; no experiment artifacts are read."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT / "scripts"))
import calculate_dependency_reliability_metrics as calc

def package(run, name, status="AUTO_VALID", classification="VALID", eligible=True):
    return {"run_id":run,"normalized_package":name,"metric_eligible":eligible,"truncated":False,
      "adjudication_status":status,"research_classification":classification,
      "primary_confirmed_hallucination":classification=="CONFIRMED_HALLUCINATION"}
def response(run, eligible=True): return {"run_id":run,"metric_eligible":eligible}
def adjudication(run,name,eligible,failure,outcome="OTHER_DEPENDENCY_ERROR"):
    return {"run_id":run,"normalized_package":name,"source_truncated":False,
      "adjudication_version":"pipe-05b-adjudicator-1.1.0","external_dependency_eligible":eligible,
      "dependency_failure":failure,"adjudication_outcome":outcome,
      "confirmed_package_hallucination":outcome=="CONFIRMED_HALLUCINATION"}

class Pipe10Tests(unittest.TestCase):
 def setUp(self): self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
 def calculate_fixture(self, rows, responses, adjs=None):
  base=Path(self.tmp.name); hash_="d"*64
  env={"format_version":"pipe-07-analysis-1.1.0","classification_joined_input_hash":hash_,"records":rows}
  pp=base/"p.json"; rp=base/"r.json"; pp.write_text(json.dumps(env)); rp.write_text(json.dumps({**env,"records":responses}))
  if adjs is None: return calc.calculate(pp,rp,no_pipe05b_adjudication=True)
  ap=base/"a.json"; ap.write_text(json.dumps({"format_version":"pipe-05b-adjudication-1.1.0","adjudication_version":"pipe-05b-adjudicator-1.1.0","source_input_hash":hash_,"records":adjs}))
  return calc.calculate(pp,rp,ap)
 def test_auto_valid_and_reviewed_outcomes(self):
  out=self.calculate_fixture([package("a","valid"),package("a","old","REVIEWED","LEGACY_OR_REMOVED"),package("a","local","REVIEWED","BUILTIN_OR_LOCAL")],[response("a")])
  self.assertEqual(out["package_level"].get("EXTERNAL_NON_FAILURE"),1); self.assertEqual(out["package_level"].get("EXTERNAL_FAILURE"),1); self.assertEqual(out["package_level"].get("NOT_EXTERNAL"),1)
 def test_adjudicated_failure_nonfailure_and_self_local(self):
  rows=[package("a","f","REVIEW_REQUIRED","AMBIGUOUS"),package("a","n","REVIEW_REQUIRED","AMBIGUOUS"),package("a","l","REVIEW_REQUIRED","AMBIGUOUS")]
  out=self.calculate_fixture(rows,[response("a")],[adjudication("a","f",True,True),adjudication("a","n",True,False),adjudication("a","l",False,False,"SELF_REFERENCE_OR_LOCAL_PACKAGE")])
  self.assertEqual([out["package_level"][x] for x in ("EXTERNAL_FAILURE","EXTERNAL_NON_FAILURE","NOT_EXTERNAL")],[1,1,1])
 def test_undetermined_reasons(self):
  rows=[package("a","u","REVIEW_REQUIRED","AMBIGUOUS"),package("a","r","VALIDATION_UNRESOLVED",None),package("a","m","REVIEWED","AMBIGUOUS")]
  out=self.calculate_fixture(rows,[response("a")])
  self.assertEqual(out["package_level"]["undetermined_by_reason"],{"PIPE05_REVIEWED_AMBIGUOUS":1,"REGISTRY_UNRESOLVED":1,"UNADJUDICATED":1})
  self.assertEqual(out["completeness_gate"]["label"],"INTERIM_OR_INCOMPLETE")
 def test_pipe05b_unresolved_is_terminal_bound(self):
  rows=[package("a","u","REVIEW_REQUIRED","AMBIGUOUS"),package("a","n")]
  out=self.calculate_fixture(rows,[response("a")],[adjudication("a","u",None,None,"UNRESOLVED")])
  self.assertEqual(out["package_level"]["undetermined_by_reason"],{"PIPE05B_UNRESOLVED":1}); self.assertEqual(out["dfr"]["bounds"],{"lower":0.0,"upper":0.5}); self.assertEqual(out["completeness_gate"]["label"],"FINAL")
 def test_response_precedence_zero_and_bounds(self):
  rows=[package("a","f","REVIEWED","CONFIRMED_HALLUCINATION"),package("a","u","VALIDATION_UNRESOLVED",None),package("b","u","VALIDATION_UNRESOLVED",None)]
  out=self.calculate_fixture(rows,[response("a"),response("b"),response("z")])
  self.assertEqual(out["response_level"],{"eligible_completed_responses":3,"POSITIVE":1,"NEGATIVE":1,"INDETERMINATE":1,"zero_package_responses":1,"responses_with_externally_eligible_package":1})
  self.assertEqual(out["rdfr"]["bounds"],{"lower":1/3,"upper":2/3})
 def test_zero_denominators_and_determinism(self):
  out=self.calculate_fixture([], [response("z")]); self.assertIsNone(out["dfr"]["rate"]); self.assertEqual(out["rdfr"]["rate"],0.0)
  self.assertEqual(out,self.calculate_fixture([], [response("z")]))

 def test_reviewed_confirmed_zero_package_and_self_local_only_responses(self):
  rows=[package("failure","f","REVIEWED","CONFIRMED_HALLUCINATION"),
        package("local","l","REVIEWED","BUILTIN_OR_LOCAL")]
  out=self.calculate_fixture(rows,[response("failure"),response("local"),response("zero")])
  self.assertEqual(out["package_level"]["EXTERNAL_FAILURE"],1)
  self.assertEqual(out["response_level"],{"eligible_completed_responses":3,"POSITIVE":1,"NEGATIVE":2,"INDETERMINATE":0,"zero_package_responses":1,"responses_with_externally_eligible_package":1})

 def test_failure_precedes_undetermined_and_undetermined_only_is_indeterminate(self):
  rows=[package("mixed","f","REVIEWED","CONFIRMED_HALLUCINATION"),
        package("mixed","u","VALIDATION_UNRESOLVED",None),
        package("only-u","u2","VALIDATION_UNRESOLVED",None)]
  out=self.calculate_fixture(rows,[response("mixed"),response("only-u")])
  self.assertEqual(out["response_level"]["POSITIVE"],1); self.assertEqual(out["response_level"]["INDETERMINATE"],1)

 def test_zero_rdfr_denominator_bounds_and_completeness_gate(self):
  out=self.calculate_fixture([package("u","x","VALIDATION_UNRESOLVED",None)],[response("u")])
  self.assertIsNone(out["rdfr"]["rate"]); self.assertIsNone(out["rdfr"]["wilson_95"])
  self.assertEqual(out["completeness_gate"],{"label":"INTERIM_OR_INCOMPLETE","unadjudicated":0,"registry_unresolved":1})
  bounded=self.calculate_fixture([package("a","f","REVIEWED","CONFIRMED_HALLUCINATION"),package("b","u","VALIDATION_UNRESOLVED",None)],[response("a"),response("b")])
  self.assertEqual(bounded["dfr"]["bounds"],{"lower":0.5,"upper":1.0}); self.assertEqual(bounded["rdfr"]["bounds"],{"lower":0.5,"upper":1.0})

 def test_invariant_and_unsupported_state_combinations_fail_closed(self):
  rows=[package("a","one"),package("a","two","REVIEWED","BUILTIN_OR_LOCAL")]
  out=self.calculate_fixture(rows,[response("a")])
  self.assertEqual(out["package_level"]["total_metric_eligible_package_rows"],2)  # D033 denominator invariant
  with self.assertRaisesRegex(ValueError,"Unsupported PIPE-05 combination"):
   self.calculate_fixture([package("a","bad","REVIEW_REQUIRED","VALID")],[response("a")])

 def test_pipe05b_orphan_duplicate_hash_format_and_source_mismatch_fail_closed(self):
  base=Path(self.tmp.name); h="d"*64; rows=[package("a","x","REVIEW_REQUIRED","AMBIGUOUS")]; responses=[response("a")]
  pp=base/"p2.json"; rp=base/"r2.json"; pp.write_text(json.dumps({"format_version":"pipe-07-analysis-1.1.0","classification_joined_input_hash":h,"records":rows})); rp.write_text(json.dumps({"format_version":"pipe-07-analysis-1.1.0","classification_joined_input_hash":h,"records":responses}))
  good=adjudication("a","x",True,False)
  cases=[
   ({"format_version":"bad","adjudication_version":"pipe-05b-adjudicator-1.1.0","source_input_hash":h,"records":[]},"Unsupported"),
   ({"format_version":"pipe-05b-adjudication-1.1.0","adjudication_version":"bad","source_input_hash":h,"records":[]},"Unsupported"),
   ({"format_version":"pipe-05b-adjudication-1.1.0","adjudication_version":"pipe-05b-adjudicator-1.1.0","source_input_hash":"0"*64,"records":[]},"source_input_hash"),
   ({"format_version":"pipe-05b-adjudication-1.1.0","adjudication_version":"pipe-05b-adjudicator-1.1.0","source_input_hash":h,"records":[good,dict(good)]},"Duplicate"),
   ({"format_version":"pipe-05b-adjudication-1.1.0","adjudication_version":"pipe-05b-adjudicator-1.1.0","source_input_hash":h,"records":[dict(good,normalized_package="orphan")]},"has no PIPE-07"),
   ({"format_version":"pipe-05b-adjudication-1.1.0","adjudication_version":"pipe-05b-adjudicator-1.1.0","source_input_hash":h,"records":[dict(good,source_truncated=True)]},"source_truncated"),
  ]
  ap=base/"a2.json"
  for doc, expected in cases:
   with self.subTest(expected=expected):
    ap.write_text(json.dumps(doc))
    with self.assertRaisesRegex(ValueError,expected): calc.calculate(pp,rp,ap)

 def test_explicit_mode_regression_many_valid_rows_and_byte_identical_output(self):
  rows=[package("r","valid-%03d"%i) for i in range(100)]
  rows += [package("r","fail-%d"%i,"REVIEWED","CONFIRMED_HALLUCINATION") for i in range(3)]
  out=self.calculate_fixture(rows,[response("r")])
  self.assertEqual((out["dfr"]["numerator"],out["dfr"]["denominator"]),(3,103))
  self.assertEqual(json.dumps(out,sort_keys=True,separators=(",",":")),json.dumps(self.calculate_fixture(rows,[response("r")]),sort_keys=True,separators=(",",":")))
  base=Path(self.tmp.name); pp=base/"mode-p.json"; rp=base/"mode-r.json"; env={"format_version":"pipe-07-analysis-1.1.0","classification_joined_input_hash":"d"*64,"records":[]}; pp.write_text(json.dumps(env)); rp.write_text(json.dumps(env))
  with self.assertRaisesRegex(ValueError,"exactly one PIPE-05B input mode"): calc.calculate(pp,rp,adjudication_path=None,no_pipe05b_adjudication=False)

 def test_cli_rerun_preserves_byte_identical_pipe10_output(self):
  base=Path(self.tmp.name); package_path=base/"cli-p.json"; response_path=base/"cli-r.json"; output_path=base/"pipe10.json"
  envelope={"format_version":"pipe-07-analysis-1.1.0","classification_joined_input_hash":"d"*64,"records":[package("a","valid")]}
  package_path.write_text(json.dumps(envelope)); response_path.write_text(json.dumps({**envelope,"records":[response("a")]}))
  argv=["--package-dataset",str(package_path),"--response-dataset",str(response_path),"--no-pipe05b-adjudication","--output",str(output_path)]
  self.assertEqual(calc.main(argv),None); first=output_path.read_bytes()
  self.assertEqual(calc.main(argv),None); self.assertEqual(output_path.read_bytes(),first)

if __name__=="__main__": unittest.main()
