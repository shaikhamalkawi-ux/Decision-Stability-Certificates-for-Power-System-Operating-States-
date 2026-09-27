"""Arithmetic-only summary of completed HOD uncapped evidence; no solver."""
from pathlib import Path
import csv
import hashlib
import json
from fractions import Fraction

BASE=Path(__file__).resolve().parent


def read(path):return json.loads(path.read_text(encoding="utf-8"))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def frac(record):return Fraction(int(record["numerator"]),int(record["denominator"]))


def main():
    completion=read(BASE/"completion.json")
    freeze=read(BASE/"prepared_freeze.json")
    assert digest(BASE/"input_manifest.csv")==freeze["manifest_sha256"]
    manifest=list(csv.DictReader((BASE/"input_manifest.csv").open(newline="",encoding="utf-8")))
    for item in manifest:
        path=Path(item["path"])
        assert digest(path)==item["sha256"] and path.stat().st_size==int(item["bytes"])
    brackets=read(BASE/"energy_brackets.json");mips=read(BASE/"mip_results.json");lps=read(BASE/"lp_results.json")
    rows=[]
    for result in brackets:
        case=result["case"];mip=mips[case];lp=lps[case]
        row={"case":case,"MIP_verdict":mip["verdict"],"MIP_model_status":mip.get("model_status","NOT_RUN"),
            "MIP_calls":mip["optimization_calls"],"MIP_elapsed_s":mip["elapsed_s"],
            "MIP_numerical_gap":mip.get("numerical_relative_gap"),"MIP_exact_strict_pass":mip.get("exact_strict_pass"),
            "MIP_exact_expanded_pass":mip.get("exact_expanded_pass"),
            "LP_calls":lp["optimization_calls"],"LP_elapsed_s":lp["elapsed_s"],
            "LP_model_status":lp.get("model_status","NOT_RUN"),"LP_bound_status":lp["new_lower_bound_status"],
            "target_lower_MWh_outward":result["lower_MWh"]["outward_floor_6dp"],
            "target_upper_MWh_outward":None if result["upper_MWh"] is None else result["upper_MWh"]["outward_ceiling_6dp"],
            "finite_binary_feasibility":result["finite_uncapped_feasibility_established"]}
        for field in ["optimum_difference_MWh","target_optimum_excess_over_chosen_incumbent_MWh","optimal_relative_penalty_percent"]:
            interval=result.get(field)
            row[field+"_lower_outward"]=None if interval is None else interval["lower"]["outward_floor_6dp"]
            row[field+"_upper_outward"]=None if interval is None else interval["upper"]["outward_ceiling_6dp"]
        if result["upper_MWh"] is not None:
            lo,hi=frac(result["lower_MWh"]),frac(result["upper_MWh"])
            li,er=frac(result["identity_lower_MWh"]),frac(result["identity_reference_upper_MWh"])
            assert lo<=hi and li<=er
            assert frac(result["optimum_difference_MWh"]["lower"])==lo-er
            assert frac(result["optimum_difference_MWh"]["upper"])==hi-li
            if "optimal_relative_penalty" in result:
                assert li>0 and lo>0
                assert frac(result["optimal_relative_penalty"]["lower"])==lo/er-1
                assert frac(result["optimal_relative_penalty"]["upper"])==hi/li-1
                for side in ["lower","upper"]:
                    assert frac(result["optimal_relative_penalty_percent"][side])==100*frac(result["optimal_relative_penalty"][side])
        rows.append(row)
    assert sum(r["MIP_calls"] for r in rows)==completion["MIP_calls"]
    assert sum(r["LP_calls"] for r in rows)==completion["LP_calls"]
    summary={"ordinary_denominator":2,"accepted_expanded_binary_witnesses":sum(r["finite_binary_feasibility"] for r in rows),
        "new_identity_solves":0,"frozen_bindings_checked":len(manifest),"all_frozen_hashes_match":True,
        "source_files":{name:digest(BASE/name) for name in ["energy_brackets.json","mip_results.json","lp_results.json",
            "completion.json","reused_identity_bounds.json"]},"summary_source_sha256":digest(Path(__file__)),"rows":rows,
        "scope":"Uncapped uniformly expanded original-binary models; no exact optimum, emissions or replication claim"}
    with (BASE/"summary.json").open("x",encoding="utf-8") as f:json.dump(summary,f,indent=2);f.write("\n")
    with (BASE/"summary.csv").open("x",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print(json.dumps(summary))


if __name__=="__main__":main()
