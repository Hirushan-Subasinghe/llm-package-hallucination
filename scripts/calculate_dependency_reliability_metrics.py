#!/usr/bin/env python3
"""PIPE-10: D036 secondary/exploratory dependency-reliability calculator.

Consumes explicit PIPE-07 v1.1 datasets and either an explicit PIPE-05B v1.1
envelope or an explicit declaration that none was supplied.  It never discovers
inputs, queries npm, installs packages, or changes primary PHR/SHR results.
"""
import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

FORMAT_VERSION = "pipe-10-dependency-reliability-metrics-1.0.0"
CALCULATOR_VERSION = "pipe-10-dependency-reliability-calculator-1.0.0"
PIPE07_FORMAT = "pipe-07-analysis-1.1.0"
PIPE05B_FORMAT = "pipe-05b-adjudication-1.1.0"
PIPE05B_VERSION = "pipe-05b-adjudicator-1.1.0"
Z95 = 1.959963984540054

def require(ok, message):
    if not ok: raise ValueError(message)

def _is_utc(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).utcoffset() == timezone.utc.utcoffset(None)
    except ValueError:
        return False

def read(path):
    raw = Path(path).read_bytes(); return json.loads(raw), hashlib.sha256(raw).hexdigest()

def load_pipe07(path, label):
    doc, digest = read(path)
    require(isinstance(doc, dict) and doc.get("format_version") == PIPE07_FORMAT,
            f"{label} must use {PIPE07_FORMAT}")
    require(isinstance(doc.get("records"), list), f"{label} records must be an array")
    return doc, digest

def load_adjudication(path, package_doc):
    doc, digest = read(path)
    require(isinstance(doc, dict) and doc.get("format_version") == PIPE05B_FORMAT and
            doc.get("adjudication_version") == PIPE05B_VERSION,
            "Unsupported PIPE-05B format/adjudication version")
    require(doc.get("source_input_hash") == package_doc.get("classification_joined_input_hash"),
            "PIPE-05B source_input_hash disagrees with PIPE-07 classification source hash")
    by_key = {}
    for row in doc.get("records", []):
        key = (row.get("run_id"), row.get("normalized_package"))
        require(all(isinstance(x, str) and x for x in key), "PIPE-05B record missing key")
        require(key not in by_key, f"Duplicate PIPE-05B key: {key}")
        require(row.get("adjudication_version") == PIPE05B_VERSION, f"Unsupported PIPE-05B record version: {key}")
        require(row.get("adjudication_outcome") in {"CONFIRMED_HALLUCINATION", "LEGACY_OR_REMOVED",
                "NAMESPACE_CONFUSION", "PACKAGE_NAME_CONFUSION", "INVALID_OR_REDUNDANT_TYPES_PACKAGE",
                "ECOSYSTEM_CONFUSION", "OTHER_DEPENDENCY_ERROR", "SELF_REFERENCE_OR_LOCAL_PACKAGE", "UNRESOLVED"},
                f"Unsupported PIPE-05B outcome: {key}")
        outcome = row.get("adjudication_outcome")
        require(row.get("confirmed_package_hallucination") is (outcome == "CONFIRMED_HALLUCINATION"),
                f"PIPE-05B confirmed_package_hallucination/outcome disagreement: {key}")
        if outcome == "CONFIRMED_HALLUCINATION":
            required_checks = {"historical": "no_prior_evidence", "normalization": "external_npm_reference",
                               "ambiguity": "cleared", "namespace": "cleared", "ecosystem": "cleared",
                               "types_package": "cleared"}
            sources = row.get("evidence_sources")
            require(row.get("dependency_failure") is True and
                    row.get("external_dependency_eligible") is True and
                    row.get("evidence_status") == "resolved" and row.get("checks") == required_checks and
                    isinstance(sources, list) and sources and
                    all(isinstance(source, dict) and isinstance(source.get("source"), str) and source["source"].strip()
                        and isinstance(source.get("summary"), str) and source["summary"].strip()
                        and _is_utc(source.get("checked_at")) for source in sources) and
                    _is_utc(row.get("reviewed_at")),
                    f"PIPE-05B confirmation guard violated: {key}")
        if outcome == "UNRESOLVED":
            require(row.get("external_dependency_eligible") is None and row.get("dependency_failure") is None,
                    f"Invalid UNRESOLVED PIPE-05B combination: {key}")
        by_key[key] = row
    return by_key, digest

def wilson(successes, total):
    if not total: return None
    p = successes / total; denom = 1 + Z95 * Z95 / total
    center = (p + Z95 * Z95 / (2 * total)) / denom
    delta = Z95 * math.sqrt(p * (1 - p) / total + Z95 * Z95 / (4 * total * total)) / denom
    return {"rate": p, "lower": max(0.0, center-delta), "upper": min(1.0, center+delta)}

def classify(row, adjudication):
    status, classification = row["adjudication_status"], row["research_classification"]
    if status == "AUTO_VALID" and classification == "VALID": return "EXTERNAL_NON_FAILURE", None, None
    if status == "VALIDATION_UNRESOLVED": return "UNDETERMINED", "REGISTRY_UNRESOLVED", None
    if status == "REVIEW_REQUIRED" and classification == "AMBIGUOUS":
        if adjudication is None: return "UNDETERMINED", "UNADJUDICATED", None
        eligible, failure = adjudication.get("external_dependency_eligible"), adjudication.get("dependency_failure")
        outcome = adjudication.get("adjudication_outcome")
        if eligible is True and failure is True: return "EXTERNAL_FAILURE", None, outcome
        if eligible is True and failure is False: return "EXTERNAL_NON_FAILURE", None, outcome
        if eligible is False: return "NOT_EXTERNAL", None, outcome
        if eligible is None: return "UNDETERMINED", "PIPE05B_UNRESOLVED", outcome
        raise ValueError("Invalid PIPE-05B eligibility/failure combination")
    if status == "REVIEWED":
        if classification in ("CONFIRMED_HALLUCINATION", "LEGACY_OR_REMOVED"):
            return "EXTERNAL_FAILURE", None, classification
        if classification == "BUILTIN_OR_LOCAL": return "NOT_EXTERNAL", None, classification
        if classification == "AMBIGUOUS": return "UNDETERMINED", "PIPE05_REVIEWED_AMBIGUOUS", classification
    raise ValueError(f"Unsupported PIPE-05 combination: {status}/{classification}")

def calculate(package_path, response_path, adjudication_path=None, no_pipe05b_adjudication=None):
    if no_pipe05b_adjudication is None: no_pipe05b_adjudication = adjudication_path is None
    require((adjudication_path is not None) != no_pipe05b_adjudication,
            "Specify exactly one PIPE-05B input mode")
    pdoc, phash = load_pipe07(package_path, "--package-dataset")
    rdoc, rhash = load_pipe07(response_path, "--response-dataset")
    adjudications, ahash = ({}, None) if no_pipe05b_adjudication else load_adjudication(adjudication_path, pdoc)
    packages = {}; by_run = defaultdict(list)
    for row in pdoc["records"]:
        key=(row.get("run_id"),row.get("normalized_package")); require(all(key) and key not in packages, "Duplicate/missing PIPE-07 package key")
        packages[key]=row; by_run[key[0]].append(row)
    require(set(adjudications) <= set(packages), "PIPE-05B key has no PIPE-07 row")
    responses = {}
    for row in rdoc["records"]:
        run=row.get("run_id"); require(isinstance(run,str) and run and run not in responses,"Duplicate/missing PIPE-07 response run_id"); responses[run]=row
    require(set(by_run) <= set(responses), "PIPE-07 package row has no response row")
    # Validate every supplied adjudication before eligibility filtering.  An
    # ineligible source remains auditable, but malformed evidence must never be
    # silently ignored merely because it is excluded from a rate denominator.
    for key, adj in adjudications.items():
        source = packages[key]
        require(adj.get("source_truncated") == source.get("truncated"),
                f"PIPE-05B source_truncated mismatch: {key}")
        require(source.get("adjudication_status") == "REVIEW_REQUIRED" and
                source.get("research_classification") == "AMBIGUOUS",
                f"PIPE-05B source is not REVIEW_REQUIRED/AMBIGUOUS: {key}")
    resolved=[]; counts=Counter(); reasons=Counter(); outcomes=Counter(); confirmed_failures=0
    for key,row in sorted(packages.items()):
        if not row.get("metric_eligible"): continue
        adj=adjudications.get(key)
        state, reason, outcome=classify(row,adj); counts[state]+=1
        if reason: reasons[reason]+=1
        if state == "EXTERNAL_FAILURE":
            outcomes[outcome or "UNSPECIFIED"]+=1
            if row.get("primary_confirmed_hallucination"): confirmed_failures += 1
        resolved.append((key[0],state))
    R=[r for r in responses.values() if r.get("metric_eligible")]
    states=defaultdict(list)
    for run,state in resolved: states[run].append(state)
    response_counts=Counter(); zero=0; with_external=0
    for response in R:
        ss=states[response["run_id"]]
        if not ss: zero += 1
        if any(s in ("EXTERNAL_FAILURE","EXTERNAL_NON_FAILURE") for s in ss): with_external += 1
        result="POSITIVE" if "EXTERNAL_FAILURE" in ss else "INDETERMINATE" if "UNDETERMINED" in ss else "NEGATIVE"
        response_counts[result]+=1
    F,N,U=counts["EXTERNAL_FAILURE"],counts["EXTERNAL_NON_FAILURE"],counts["UNDETERMINED"]
    P, I = response_counts["POSITIVE"], response_counts["INDETERMINATE"]
    dden=F+N; rden=len(R)-I
    require(sum(counts[s] for s in ("EXTERNAL_FAILURE","EXTERNAL_NON_FAILURE","NOT_EXTERNAL","UNDETERMINED")) == len(resolved), "D036 package invariant failed")
    return {"format_version":FORMAT_VERSION,"calculator_version":CALCULATOR_VERSION,
      "metric_definition_reference":"docs/decision_log.md D033, D034, D035, D036, D037",
      "pipe05b_adjudication_input_status":"not_supplied" if no_pipe05b_adjudication else "supplied",
      "package_level":{"total_metric_eligible_package_rows":len(resolved), **{k:counts[k] for k in ("EXTERNAL_FAILURE","EXTERNAL_NON_FAILURE","NOT_EXTERNAL","UNDETERMINED")},"undetermined_by_reason":dict(sorted(reasons.items())),"confirmed_hallucinations_among_failures":confirmed_failures,"failures_by_adjudication_outcome":dict(sorted(outcomes.items()))},
      "response_level":{"eligible_completed_responses":len(R), **{k:response_counts[k] for k in ("POSITIVE","NEGATIVE","INDETERMINATE")},"zero_package_responses":zero,"responses_with_externally_eligible_package":with_external},
      "dfr":{"numerator":F,"denominator":dden,"rate":None if not dden else F/dden,"wilson_95":wilson(F,dden),"bounds":None if not U else {"lower":F/(F+N+U),"upper":(F+U)/(F+N+U)}},
      "rdfr":{"numerator":P,"denominator":rden,"rate":None if not rden else P/rden,"wilson_95":wilson(P,rden),"bounds":None if not I else {"lower":P/len(R),"upper":(P+I)/len(R)}},
      "completeness_gate":{"label":"FINAL" if reasons["UNADJUDICATED"]==0 and reasons["REGISTRY_UNRESOLVED"]==0 else "INTERIM_OR_INCOMPLETE","unadjudicated":reasons["UNADJUDICATED"],"registry_unresolved":reasons["REGISTRY_UNRESOLVED"]},
      "provenance":{"package_dataset_input_hash":phash,"response_dataset_input_hash":rhash,"pipe05b_adjudication_input_hash":ahash}}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--package-dataset",required=True); p.add_argument("--response-dataset",required=True); p.add_argument("--output",required=True)
    g=p.add_mutually_exclusive_group(required=True); g.add_argument("--pipe05b-adjudication"); g.add_argument("--no-pipe05b-adjudication",action="store_true")
    a=p.parse_args(argv); output=calculate(a.package_dataset,a.response_dataset,a.pipe05b_adjudication,a.no_pipe05b_adjudication); raw=(json.dumps(output,indent=2)+"\n").encode(); path=Path(a.output)
    if path.exists(): require(path.read_bytes()==raw, f"Existing PIPE-10 output differs; choose a new path: {path}")
    else: path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(raw)
    print(f"DFR: {output['dfr']['numerator']}/{output['dfr']['denominator']}; RDFR: {output['rdfr']['numerator']}/{output['rdfr']['denominator']}. Wrote {path}.")
if __name__ == "__main__": raise SystemExit(main())
