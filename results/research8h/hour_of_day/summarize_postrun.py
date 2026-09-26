"""Summarize frozen HOD outcomes and timing; no modeling or optimization."""
from datetime import datetime, timezone
from fractions import Fraction
import csv
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    with path.open("x",encoding="utf-8") as f:
        json.dump(value,f,indent=2)
        f.write("\n")


def main():
    completion = read(BASE/"completion.json")
    freeze = read(BASE/"prepared_freeze.json")
    manifest = list(csv.DictReader((BASE/"input_manifest.csv").open(newline="",encoding="utf-8")))
    assert digest(BASE/"input_manifest.csv") == freeze["manifest_sha256"]
    for r in manifest:
        p = Path(r["path"])
        assert p.stat().st_size == int(r["bytes"]) and digest(p) == r["sha256"]
    outcomes = read(BASE/"outcomes.json")
    rows = []
    for outcome in outcomes:
        case = outcome["case"];directory = BASE/case
        result = read(directory/"lp/result.json")
        cert = read(directory/"lp/dual_certificate.json")
        verify = cert["verification"]
        for name,hash_value in cert["model_artifacts"].items():
            assert digest(directory/"lp"/name) == hash_value
        assert digest(directory/"lp/raw_solver_ray.npz") == cert["raw_solver_ray_sha256"]
        assert digest(directory/"lp/row_metadata.csv.gz") == cert["row_metadata_sha256"]
        assert cert["experiment_manifest_sha256"] == freeze["manifest_sha256"]
        raw_gap = Fraction(int(verify["exact_gap_numerator"]),int(verify["exact_gap_denominator"]))
        expanded_gap = Fraction(int(verify["exact_robust_gap_numerator"]),int(verify["exact_robust_gap_denominator"]))
        assert raw_gap > 0 and expanded_gap > 0 and verify["pass"] and verify["robust_pass"]
        preservation = read(directory/"preservation.json")
        adjacency = next(r for r in read(BASE/"adjacency_addendum.json")["cases"] if r["case"] == case)
        rows.append({"case":case,"verdict":outcome["verdict"],"LP_calls":outcome["LP_calls"],
            "MIP_calls":outcome["MIP_calls"],"LP_elapsed_s":result["elapsed_s"],
            "exact_nominal_gap_approx_ray_units":float(raw_gap),"exact_expanded_gap_approx_ray_units":float(expanded_gap),
            "certificate_nonzero_rows":verify["row_multiplier_nonzeros"],
            "raw_inadmissible_entries_projected":verify["inadmissible_raw_entries"],
            "changed_hours":preservation["changed_hours"],
            "broken_source_continuity_count":adjacency["broken_source_continuity_count"],
            "literal_positionwise_changed_pair_count":adjacency["literal_positionwise_changed_pair_count"],
            "certificate_sha256":digest(directory/"lp/dual_certificate.json")})
    assert completion["LP_calls"] == 2 and completion["MIP_calls"] == 0
    marker = read(BASE/"execution_started.json")
    stopped = read(BASE/"aborted_instrumentation_attempt.json")
    initial = read(BASE/"timed_execution_started.json")
    audit = {"status":"COMPLETED_DIRECT_INVOCATION_WITH_NO_SOLVER_RETRY","optimization_calls":2,
        "LP_calls":2,"MIP_calls":0,"frozen_inputs_checked":len(manifest),
        "frozen_manifest_sha256":freeze["manifest_sha256"],
        "execution_marker_utc_before_native_loading":marker["utc"],
        "completion_file_modified_utc":datetime.fromtimestamp((BASE/"completion.json").stat().st_mtime,timezone.utc).isoformat(),
        "allocation_start_utc":None,"allocation_start_not_instrumented":True,
        "reported_phase_elapsed_s":completion["phase_elapsed_s"],"configured_soft_allocation_s":1200,
        "reported_phase_overrun_s":max(0.,completion["phase_elapsed_s"]-1200),
        "actual_LP_seconds":completion["actual_LP_seconds"],"actual_MIP_seconds":completion["actual_MIP_seconds"],
        "each_LP_requested_s":30,"maximum_LP_requested_limit_overrun_s":max(0.,max(r["LP_elapsed_s"] for r in rows)-30),
        "hard_wall_time_cap_claim":False,"solver_performance_benchmark_claim":False,
        "timing_scope":"Frozen phase excludes entry validation/native loading. Completion mtime is not an exact allocation timestamp.",
        "aborted_optional_instrumentation":{"optimization_calls":0,"termination_confirmed_without_execution_marker":True,
            "invocation_to_termination_confirmation_s":(datetime.fromisoformat(stopped["observed_after_termination_utc"])-
                datetime.fromisoformat(initial["observed_process_invocation_utc"])).total_seconds(),
            "record_sha256":digest(BASE/"aborted_instrumentation_attempt.json"),
            "excluded_from_solver_allocation":True},
        "summary_source_sha256":digest(Path(__file__)),"created_utc":datetime.now(timezone.utc).isoformat()}
    save(BASE/"postrun_allocation_audit.json",audit)
    save(BASE/"summary.json",{"ordinary_denominator":2,"exact_expanded_negatives":2,
        "exact_expanded_positives":0,"unknown":0,"controls_outside_denominator":2,
        "independent_postrun_replay_required":True,"rows":rows})
    with (BASE/"summary.csv").open("x",newline="",encoding="utf-8") as f:
        writer = csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print(json.dumps({"audit":audit,"rows":rows}))


if __name__ == "__main__":
    main()
