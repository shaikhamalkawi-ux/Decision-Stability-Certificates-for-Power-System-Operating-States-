"""Append-only producer reporting after the frozen runner closes; no optimizer."""
from pathlib import Path
from datetime import datetime
from fractions import Fraction
import csv
import hashlib
import json

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
CASES = ["seed_26093210", "seed_26093211", "seed_26093220", "seed_26093221"]
IDENTITIES = ["week_2_identity", "week_3_identity"]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text(encoding="utf-8"))
frac = lambda v: Fraction(int(v["numerator"]), int(v["denominator"]))


def write(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def interval(record):
    return "["+record["lower"]["outward_floor_6dp"]+", "+record["upper"]["outward_ceiling_6dp"]+"]"


def check_outward(value):
    if isinstance(value,dict):
        if {"numerator","denominator","outward_floor_6dp","outward_ceiling_6dp"} <= value.keys():
            exact=frac(value)
            assert Fraction(value["outward_floor_6dp"]) <= exact <= Fraction(value["outward_ceiling_6dp"])
        for child in value.values():check_outward(child)
    elif isinstance(value,list):
        for child in value:check_outward(child)


def main():
    for name in ["allocation_audit.json","new_cap_implication.json","summary.csv","summary.json","READOUT.md"]:
        assert not (OUT/name).exists(),name
    completion=read(OUT/"completion.json")
    freeze=read(OUT/"prepared_freeze.json")
    assert completion["ordinary_denominator"]==4
    assert completion["new_identity_MIP_calls"]==0
    assert completion["all_frozen_hashes_unchanged"]
    assert sha(OUT/"input_manifest.csv")==freeze["manifest_sha256"]
    with (OUT/"input_manifest.csv").open(encoding="utf-8",newline="") as stream:
        bindings=list(csv.DictReader(stream))
    assert len(bindings)==378
    for binding in bindings:
        p=Path(binding["path"])
        assert p.stat().st_size==int(binding["bytes"]) and sha(p)==binding["sha256"]
    rows=read(OUT/"energy_brackets.json")
    check_outward(rows)
    check_outward(read(OUT/"identity_energy_bounds.json"))
    assert [r["case"] for r in rows]==CASES
    mips,lps=read(OUT/"mip_results.json"),read(OUT/"lp_results.json")
    assert list(mips)==CASES and list(lps)==IDENTITIES+CASES
    assert completion["target_MIP_calls"]==sum(x["optimization_calls"] for x in mips.values())
    assert completion["identity_LP_calls"]==sum(lps[k]["optimization_calls"] for k in IDENTITIES)
    assert completion["target_LP_calls"]==sum(lps[k]["optimization_calls"] for k in CASES)
    decisions=read(OUT/"launch_decisions.json")
    expected=[("IDENTITY_LP",k) for k in IDENTITIES]+[("TARGET_MIP",k) for k in CASES]+[("TARGET_LP",k) for k in CASES]
    assert [(d["kind"],d["case"]) for d in decisions]==expected
    cutoff=datetime.fromisoformat(freeze["cutoff_utc"])
    launch_audit=[]
    for d in decisions:
        result=mips[d["case"]] if d["kind"]=="TARGET_MIP" else lps[d["case"]]
        row={"kind":d["kind"],"case":d["case"],"admitted":d["admitted"],"guard_s":d["guard_s"],
            "recorded_decision_utc":d["utc"],"optimization_calls":result["optimization_calls"]}
        assert bool(result["optimization_calls"])==d["admitted"]
        if result["optimization_calls"]:
            start=datetime.fromisoformat(result["started_utc"])
            end=datetime.fromisoformat(result["ended_utc"])
            latency=(start-datetime.fromisoformat(d["utc"])).total_seconds()
            actual_cutoff=(cutoff-start).total_seconds()
            # Phase estimate uses elapsed wall time since the perf-counter sample;
            # it is not a separate monotonic clock reading at the actual call.
            estimated_phase=d["phase_remaining_s"]-latency
            consistent=latency>=0 and actual_cutoff>=d["guard_s"] and estimated_phase>=d["guard_s"]
            row.update(actual_started_utc=result["started_utc"],actual_ended_utc=result["ended_utc"],
                decision_to_actual_start_s=latency,actual_UTC_remaining_s=actual_cutoff,
                estimated_phase_remaining_at_start_s=estimated_phase,
                observed_start_consistent_with_recorded_admission=consistent,
                negative_wall_time_jump_observed=latency<0,
                solver_elapsed_s=result["elapsed_s"],wall_start_to_end_s=(end-start).total_seconds(),
                nominal_solver_limit_s=600 if d["kind"]=="TARGET_MIP" else 60)
        else:
            assert result["elapsed_s"]==0 and not result["solver_run_called"]
        launch_audit.append(row)
    discrepancies=[r for r in launch_audit if r.get("observed_start_consistent_with_recorded_admission") is False]
    timing={"calls":launch_audit,"observed_admission_start_discrepancies":discrepancies,
        "maximum_decision_to_actual_start_s":max((r.get("decision_to_actual_start_s",0.) for r in launch_audit),default=0.),
        "phase_estimate_clock_caveat":"Saved monotonic remaining time less observed wall-clock latency; no hard latency guarantee.",
        "completion":completion,"optimizer_calls_by_this_reporting_script":0}
    summary=[];cap_implications=[]
    old={r["case"]:r["verdict"] for r in read(OUT/"parent_outcomes_context.json")["outcomes"]}
    for r in rows:
        case=r["case"];lower=frac(r["lower_MWh"]);li=frac(r["identity_lower_MWh"]);ui=frac(r["identity_reference_upper_MWh"])
        out={"week":r["week"],"case":case,"MIP_status":mips[case].get("model_status","NOT_RUN"),
            "MIP_seconds":mips[case]["elapsed_s"],"numerical_MIP_gap":mips[case].get("numerical_relative_gap"),
            "LP_status":lps[case].get("model_status","NOT_RUN"),"LP_seconds":lps[case]["elapsed_s"],
            "upper_status":r["upper_status"],"target_lower_MWh_floor":r["lower_MWh"]["outward_floor_6dp"],
            "target_upper_MWh_ceiling":None,"optimum_difference_MWh":None,"optimal_relative_percent":None,
            "strict_nominal_witness_pass":mips[case].get("exact_strict_pass"),
            "expanded_original_binary_witness_pass":mips[case].get("exact_expanded_pass"),
            "native_no_cap_pass":mips[case].get("native_no_cap_pass")}
        cap=Fraction(read(OUT/case/"model_binding.json")["removed_cap_MWh"])
        expanded_cap=cap+Fraction.from_float(1e-5)
        excludes=lower>expanded_cap
        out.update(historical_capped_verdict=old[case],removed_cap_MWh=int(cap),
            exact_lower_excludes_old_expanded_cap=excludes)
        cap_implications.append({"case":case,"historical_capped_verdict":old[case],
            "removed_cap_MWh":int(cap),"expanded_cap_exact":{"numerator":str(expanded_cap.numerator),"denominator":str(expanded_cap.denominator)},
            "lower_MWh":r["lower_MWh"],"strict_lower_greater_than_expanded_cap":excludes,
            "new_exclusion_for_historically_UNKNOWN":old[case]=="UNKNOWN" and excludes,
            "historical_ledger_modified":False,
            "reason":"A valid uncapped lower bound greater than B+tau contradicts the old expanded cap; no such implication is claimed otherwise."})
        if r["upper_MWh"] is not None:
            upper=frac(r["upper_MWh"]);assert lower<=upper and li<=ui
            d=r["optimum_difference_MWh"]
            assert frac(d["lower"])==lower-ui and frac(d["upper"])==upper-li
            chosen=r["target_optimum_excess_over_chosen_incumbent_MWh"]
            assert frac(chosen["lower"])==lower-ui and frac(chosen["upper"])==upper-ui
            out["target_upper_MWh_ceiling"]=r["upper_MWh"]["outward_ceiling_6dp"]
            out["optimum_difference_MWh"]=interval(d)
            if "optimal_relative_penalty_percent" in r:
                pct=r["optimal_relative_penalty_percent"]
                assert li>0 and lower>0
                assert frac(pct["lower"])==100*(lower/ui-1) and frac(pct["upper"])==100*(upper/li-1)
                out["optimal_relative_percent"]=interval(pct)
        else:
            assert r["upper_status"]=="NO_UPPER" and "optimum_difference_MWh" not in r
        summary.append(out)
    write(OUT/"allocation_audit.json",timing)
    write(OUT/"new_cap_implication.json",cap_implications)
    with (OUT/"summary.csv").open("x",encoding="utf-8",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(summary[0]));writer.writeheader();writer.writerows(summary)
    output={"status":"PRODUCER_SUMMARY_EXACT_ARITHMETIC_AND_TIMING_AUDIT_COMPLETE",
        "ordinary_denominator":4,"rows":summary,"manifest_sha256":freeze["manifest_sha256"],
        "frozen_files_rechecked":len(bindings),"all_frozen_hashes_unchanged":True,
        "postrun_independent_review_required":True,"new_optimization_calls":0,
        "reporting_source_sha256":sha(Path(__file__)),
        "artifact_sha256":{name:sha(OUT/name) for name in ["energy_brackets.json","identity_energy_bounds.json",
            "mip_results.json","lp_results.json","completion.json","allocation_audit.json","new_cap_implication.json","summary.csv"]}}
    write(OUT/"summary.json",output)
    lines=["# Fresh January uncapped energy qualification", "",
        "Producer results are closed; independent post-run replay is required before publication. All four prescribed targets are retained regardless of their prior capped labels. No source, protocol, case or solver limit was changed after the 378-file freeze.","",
        "| Week | Target | Binary upper status | Exact lower, floor MWh | Binary upper, ceiling MWh | Optimum difference interval MWh | Relative optimum interval % |",
        "|---|---|---|---:|---:|---|---|"]
    for r in summary:
        lines.append(f"| {r['week']} | {r['case']} | {r['upper_status']} | {r['target_lower_MWh_floor']} | {r['target_upper_MWh_ceiling'] or 'NO_UPPER'} | {r['optimum_difference_MWh'] or 'not established'} | {r['optimal_relative_percent'] or 'not established'} |")
    lines += ["", "All values concern the same uncapped uniformly expanded original-binary models. The rows remove only each target's frozen fossil-energy cap; there are no named-unit mean targets. Fossil output means electricity from the native 23 Coal/Oil/NG units over one-hour intervals, excluding nuclear. It is not fuel, emissions or financial cost.","",
        "Exact objective lower bounds come from signed row multipliers, finite-box residual correction and uniform finite-bound widening by Fraction.from_float(1e-5). The unchanged reference binary witnesses supply the weekly upper bounds. Accepted target witnesses must satisfy every widened row/column bound and all 12,096 original binary coordinates, plus the native no-cap check. Strict nominal flags are reported separately in summary.csv; tolerance-expanded membership is not strict membership or exact optimality.","",
        "For each week the optimum difference is enclosed by [L_target - U_identity, U_target - L_identity]. The separate excess over the chosen reference incumbent uses [L_target - U_identity, U_target - U_identity]. Relative optimum bounds use [L_target/U_identity - 1, U_target/L_identity - 1] only with positive lower bounds. These are different quantities. Rational records in energy_brackets.json are authoritative; displayed intervals round outward. A NO_UPPER case establishes neither finite uncapped feasibility nor a finite difference interval. Nonpositive or zero-containing intervals are retained unchanged.","",
        "The append-only new_cap_implication.json compares each exact uncapped lower bound with the original cap plus exact tau. Only a strict inequality L > B+tau proves exclusion under that old expanded cap. It records any new implication for a historical UNKNOWN without modifying the historical capped ledger.","",
        "| Target | MIP status | MIP seconds | Numerical gap | LP status | LP seconds |",
        "|---|---|---:|---:|---|---:|"]
    for r in summary:
        lines.append(f"| {r['case']} | {r['MIP_status']} | {r['MIP_seconds']:.6f} | {r['numerical_MIP_gap']} | {r['LP_status']} | {r['LP_seconds']:.6f} |")
    lines += ["",f"Completed calls: {completion['identity_LP_calls']} identity LPs, {completion['target_MIP_calls']} target MIPs and {completion['target_LP_calls']} target LPs; zero new identity MIPs. Phase elapsed {completion['phase_elapsed_s']:.6f} s against the 3600 s soft allocation; phase overrun {completion['soft_allocation_overrun_s']:.6f} s, UTC cutoff overrun {completion['UTC_cutoff_overrun_s']:.6f} s. Actual solver soft-limit overruns total {completion['solver_soft_overrun_s']:.6f} s.","",
        f"The admission-to-recorded-start latency audit found {len(discrepancies)} observed discrepancies; maximum decision-to-start latency was {timing['maximum_decision_to_actual_start_s']:.6f} s. allocation_audit.json preserves every decision and actual timestamp. The phase-at-start check extrapolates the recorded monotonic remaining time using wall-clock latency, and does not establish a hard filesystem-latency bound. Actual starts/ends and observed overruns remain authoritative.","",
        "These are two previously fixed January weeks of the same isolated Area 1 model. They are not independent-network replications, field interventions or claims about realistic reconstructed weather. The same original initial/terminal conventions, native arrays, DC network and no-storage scope remain in force. Solver timings on the shared host are not performance benchmarks.","",
        "Prepared manifest SHA256: `"+freeze['manifest_sha256']+"`. All 378 frozen bindings were rehashed after completion. The producer summary and this readout make no claim that the separate independent post-run gate has already passed.",""]
    with (OUT/"READOUT.md").open("x",encoding="utf-8") as stream:stream.write("\n".join(lines))
    print(json.dumps({"summary_sha256":sha(OUT/"summary.json"),"readout_sha256":sha(OUT/"READOUT.md"),
        "rows":summary,"timing_discrepancies":len(discrepancies)}))


if __name__=="__main__":
    main()
