"""Prepare and separately execute five fixed-identity-commitment redispatch LPs."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from fractions import Fraction
import json
from pathlib import Path
import shutil
import sys
import time
sys.dont_write_bytecode=True
import highspy
import numpy as np
import pandas as pd
from scipy.sparse import load_npz

from research8h_day_blocks import load_case
from research8h_seasonal_uncapped import exact_point_check, rational_record
from research8h_service_network_mip import direct_check, unpack
from temporal_lp_certificate import check_vector, digest, exact_ray_check, save
from v8r1_rts_seasonal import load_model

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"results/research8h/day_blocks"
IDENTITY=ROOT/"results/research8h/seasonal_transfer/january_identity"
OUT=ROOT/"results/research8h/day_fixed_identity"
PROTOCOL=ROOT/"docs/research8h/DAY_FIXED_IDENTITY_PROTOCOL.md"
CASES=["days_132","days_213","days_231","days_312","days_321"]
STATE=np.arange(6888,18984)
FREE=np.r_[np.arange(6888),np.arange(18984,23016)]
TOL=1e-5


def read(path):return json.loads(path.read_text(encoding="utf-8"))
def arrays(path):
    with np.load(path) as z:return {k:z[k].copy() for k in z.files}
def finite(value):return float(value) if np.isfinite(value) else None
def energy(vector,objective):
    return sum((Fraction.from_float(float(vector[j])) for j in np.flatnonzero(objective)),Fraction(0))
def frame_bytes_equal(a,b):return np.array_equal(np.asarray(a).view(np.uint64),np.asarray(b).view(np.uint64))


def check_sources(path):
    rows=pd.read_csv(path).to_dict("records")
    assert all(Path(x["path"]).stat().st_size==x["bytes"] and digest(Path(x["path"]))==x["sha256"] for x in rows)
    return rows


def fixed_bounds(bounds,anchor):
    result={k:v.copy() for k,v in bounds.items()}
    assert len(anchor)==12096 and np.all((anchor==0)|(anchor==1))
    assert np.all(bounds["column_lower"][STATE]<=anchor) and np.all(anchor<=bounds["column_upper"][STATE])
    result["column_lower"][STATE]=anchor;result["column_upper"][STATE]=anchor
    assert all(np.array_equal(result[k],bounds[k]) for k in ["row_lower","row_upper"])
    assert all(frame_bytes_equal(result[k][FREE],bounds[k][FREE]) for k in ["column_lower","column_upper"])
    assert np.array_equal(result["column_lower"][STATE],anchor) and np.array_equal(result["column_upper"][STATE],anchor)
    return result


def roster_objective(model,metadata):
    names=model.dec["GEN UID"].tolist()
    assert names==metadata["unit_names"] and metadata["offsets"]=={"P":0,"U":6888,"Y":10920,"Z":14952,"theta":18984}
    fossil=[j for j in model.urows if model.dec.iloc[j]["Fuel"] in {"Coal","Oil","NG"}]
    assert len(fossil)==23 and [names[j] for j in fossil]==metadata["fossil_units"]
    assert "121_NUCLEAR_1" not in metadata["fossil_units"]
    c=np.zeros(23016);c[[t*41+j for t in range(168) for j in fossil]]=1.
    assert np.count_nonzero(c)==3864
    return c,fossil


def validate_parent(A,b,integer,labels,meta):
    assert A.shape==(34681,23016) and np.isfinite(b["column_lower"]).all() and np.isfinite(b["column_upper"]).all()
    assert np.array_equal(np.flatnonzero(integer),STATE)
    assert meta["individual_mean_constraints"]==0 and meta["budget_MWh"]==23195
    assert not labels.family.str.contains("mean").any()
    caps=np.flatnonzero(labels.family.eq("fossil_energy_cap"))
    assert len(caps)==1 and b["row_upper"][caps[0]]==23195 and np.isneginf(b["row_lower"][caps[0]])
    return int(caps[0])


def native_check(model,vector,native,fossil):
    p,u,y,z,theta=unpack(vector,168,41,24,24)
    return direct_check(model,p,u,y,z,theta,native["pmin"],native["pmax"],native["net"],native["rows"],native["nodal"],fossil,23195)


def prepare():
    OUT.mkdir(parents=True,exist_ok=False)
    old_freeze=read(SOURCE/"prepared_freeze.json")
    assert old_freeze["cases"]==CASES and digest(SOURCE/"input_manifest.csv")==old_freeze["manifest_sha256"]
    sources=check_sources(SOURCE/"input_manifest.csv")
    source_v3=Path(old_freeze["source_v3"]);model=load_model(source_v3)
    A,b,integer,labels,meta,native=load_case(IDENTITY)
    validate_parent(A,b,integer,labels,meta)
    original=arrays(IDENTITY/"constructive_vector.npz")["vector"]
    assert original.shape==(23016,) and np.isfinite(original).all()
    anchor=original[STATE].copy();assert np.all((anchor==0)|(anchor==1))
    np.savez_compressed(OUT/"identity_state_anchor.npz",values=anchor,columns=STATE)
    objective,fossil=roster_objective(model,meta)
    assert np.array_equal(A.getrow(validate_parent(A,b,integer,labels,meta)).toarray().ravel(),objective)
    fixed=fixed_bounds(b,anchor)
    control_exact=exact_point_check(A,fixed,original,integer)
    control_native=native_check(model,original,native,fossil)
    assert control_exact["expanded_pass"] and control_native["pass"]
    save(OUT/"identity_control.json",{"exact_fixed_model":control_exact,"native_full_model":control_native,
         "source_vector_sha256":digest(IDENTITY/"constructive_vector.npz"),"optimization_calls":0})
    paths=[Path(__file__),PROTOCOL,SOURCE/"prepared_freeze.json",SOURCE/"input_manifest.csv",SOURCE/"prepared_cases.json",
           ROOT/"docs/research8h/DAY_BLOCK_PROTOCOL.md",OUT/"identity_state_anchor.npz",OUT/"identity_control.json"]
    paths.extend(Path(x["path"]) for x in sources)
    paths.extend(ROOT/"src"/name for name in ["research8h_day_blocks.py","research8h_seasonal_uncapped.py",
        "research8h_service_network_mip.py","research8h_service_network.py","research8h_seasonal_reference.py",
        "research8h_seasonal_transfer.py","research8h_u_only_continuation.py","temporal_lp_certificate.py",
        "v8r1_rts_seasonal.py","temporal_information_pilot.py"])
    paths.extend(IDENTITY/name for name in ["matrix.npz","bounds.npz","integrality.npz","row_metadata.csv.gz",
        "model_metadata.json","native_inputs.npz","constructive_vector.npz"])
    records=[]
    for case in CASES:
        parent=SOURCE/case;A,b,integer,labels,meta,native=load_case(parent)
        cap=validate_parent(A,b,integer,labels,meta);c,fossil=roster_objective(model,meta)
        assert np.array_equal(c,objective) and np.array_equal(A.getrow(cap).toarray().ravel(),c)
        bound=fixed_bounds(b,anchor)
        directory=OUT/case;directory.mkdir()
        for filename in ["matrix.npz","integrality.npz","row_metadata.csv.gz","model_metadata.json","native_inputs.npz","permutation.csv"]:
            shutil.copyfile(parent/filename,directory/filename)
            assert digest(parent/filename)==digest(directory/filename)
        np.savez_compressed(directory/"bounds.npz",**bound)
        np.savez_compressed(directory/"objective.npz",objective=c)
        changed=np.flatnonzero((bound["column_lower"]!=b["column_lower"])|(bound["column_upper"]!=b["column_upper"]))
        assert set(changed).issubset(set(STATE))
        old_point=arrays(parent/"constructive_vector.npz")["vector"]
        same_anchor=frame_bytes_equal(old_point[STATE],anchor)
        old_check=read(parent/"constructive_check.json")
        known_full_positive=bool(old_check["full_exact"]["expanded_pass"] and old_check["numerical"]["binary_network_pass"])
        known_fixed_positive=False
        if same_anchor and known_full_positive:
            known_fixed_positive=bool(exact_point_check(A,bound,old_point,integer)["expanded_pass"])
            assert known_fixed_positive
        record={"case":case,"rows":A.shape[0],"columns":A.shape[1],"matrix_exact_parent_copy":True,
                "all_row_bounds_unchanged":True,"P_theta_bounds_bitwise_unchanged":True,"fixed_state_columns":len(STATE),
                "actually_changed_column_bounds":len(changed),"cap_MWh":23195,"mean_rows":0,
                "native_inputs_sha256":digest(parent/"native_inputs.npz"),"parent_matrix_sha256":digest(parent/"matrix.npz"),
                "parent_bounds_sha256":digest(parent/"bounds.npz"),"anchor_sha256":digest(OUT/"identity_state_anchor.npz"),
                "old_constructive_full_positive":known_full_positive,"old_constructive_states_equal_identity":same_anchor,
                "known_exact_fixed_model_positive":known_fixed_positive,"included_in_five_LPs_regardless":True,
                "negative_scope":"Fixed identity U/Y/Z only; no infeasibility inference for unfixed UC."}
        save(directory/"model_binding.json",record);records.append(record)
        paths.extend(parent/name for name in ["matrix.npz","bounds.npz","integrality.npz","native_inputs.npz",
            "row_metadata.csv.gz","model_metadata.json","permutation.csv","constructive_vector.npz","constructive_check.json"])
        paths.extend(directory.iterdir())
    save(OUT/"prepared_cases.json",records);paths.append(OUT/"prepared_cases.json")
    unique=list(dict.fromkeys(paths))
    manifest=[{"path":str(p),"sha256":digest(p),"bytes":p.stat().st_size} for p in unique]
    save(OUT/"input_manifest.json",manifest)
    save(OUT/"prepared_freeze.json",{"utc":datetime.now(timezone.utc).isoformat(),"cases":CASES,
         "source_sha256":digest(Path(__file__)),"protocol_sha256":digest(PROTOCOL),
         "manifest_sha256":digest(OUT/"input_manifest.json"),"source_v3":str(source_v3),"LP_seconds":60,
         "threads":1,"random_seed":0,"presolve":"off","solver":"simplex","optimization_calls":0,
         "all_five_models_frozen_before_solve":True,"requires_parent_review_and_GO":True})
    print(json.dumps({"event":"PREPARED_NO_SOLVES","cases":CASES,"bound_files":len(manifest)}),flush=True)


def check_manifest():
    freeze=read(OUT/"prepared_freeze.json")
    assert freeze["cases"]==CASES and digest(OUT/"input_manifest.json")==freeze["manifest_sha256"]
    manifest=read(OUT/"input_manifest.json")
    assert all(Path(x["path"]).stat().st_size==x["bytes"] and digest(Path(x["path"]))==x["sha256"] for x in manifest)
    return freeze,manifest


def ray_from_solver(solver,A,b,directory):
    status,exists,values=solver.getDualRay()
    report={"retrieval_status":str(status),"exists":bool(exists),"candidates":[]}
    if not exists:return report,None
    raw=np.asarray(values,dtype=float);np.savez_compressed(directory/"raw_solver_ray.npz",ray=raw)
    if raw.shape!=(A.shape[0],) or not np.isfinite(raw).all():
        report["reason"]="invalid returned ray";return report,None
    selected=None
    for orientation in [1,-1]:
        d=orientation*raw
        forbidden=((d>0)&~np.isfinite(b["row_lower"]))|((d<0)&~np.isfinite(b["row_upper"]))
        projected=d.copy();projected[forbidden]=0.
        for label,candidate in [("raw",d),("projected_to_row_sign_cone",projected)]:
            check=exact_ray_check(A,b,candidate)
            entry={"orientation":orientation,"candidate":label,"projected_entries":int(forbidden.sum()),"verification":check}
            report["candidates"].append(entry)
            if check.get("pass") and check.get("robust_pass") and selected is None:
                selected={**entry,"multipliers":[{"row":int(i),"value_hex":float(candidate[i]).hex()} for i in np.flatnonzero(candidate)],
                    "model_artifacts":{"matrix.npz":digest(directory/"matrix.npz"),"bounds.npz":digest(directory/"bounds.npz")},
                    "raw_solver_ray_sha256":digest(directory/"raw_solver_ray.npz"),
                    "row_metadata_sha256":digest(directory/"row_metadata.csv.gz"),
                    "experiment_manifest_sha256":digest(OUT/"input_manifest.json"),
                    "scope":"Rejects only the fixed identity U/Y/Z restriction; does not reject the full unfixed UC model."}
    if selected is not None:save(directory/"fixed_schedule_certificate.json",selected)
    return report,selected


def run_prepared():
    freeze,manifest=check_manifest()
    with (OUT/"execution_started.json").open("x",encoding="utf-8") as stream:
        json.dump({"utc":datetime.now(timezone.utc).isoformat(),"planned_LP_calls":5,"no_routing_or_retries":True},stream,indent=2)
    anchor=arrays(OUT/"identity_state_anchor.npz")["values"]
    model=load_model(Path(freeze["source_v3"]));results=[]
    for case in CASES:
        directory=OUT/case;A,b,integer,labels,meta,native=load_case(directory)
        parent_b=arrays(SOURCE/case/"bounds.npz");c=arrays(directory/"objective.npz")["objective"]
        expected,fossil=roster_objective(model,meta);assert np.array_equal(c,expected)
        lp=highspy.HighsLp();lp.num_row_,lp.num_col_=A.shape
        lp.col_cost_,lp.col_lower_,lp.col_upper_=c,b["column_lower"],b["column_upper"]
        lp.row_lower_,lp.row_upper_=b["row_lower"],b["row_upper"]
        lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise
        lp.a_matrix_.num_row_,lp.a_matrix_.num_col_=A.shape
        lp.a_matrix_.start_,lp.a_matrix_.index_,lp.a_matrix_.value_=A.indptr,A.indices,A.data
        solver=highspy.Highs();options={"time_limit":60.,"threads":1,"random_seed":0,"solver":"simplex","presolve":"off",
            "log_to_console":False,"log_file":str(directory/"solver.log")}
        for key,value in options.items():assert solver.setOptionValue(key,value)==highspy.HighsStatus.kOk
        assert solver.passModel(lp)==highspy.HighsStatus.kOk
        started=time.perf_counter();run_status=solver.run();elapsed=time.perf_counter()-started
        status,solution,info=solver.getModelStatus(),solver.getSolution(),solver.getInfo()
        result={"case":case,"verdict":"UNKNOWN","model_status":solver.modelStatusToString(status),"run_status":str(run_status),
                "elapsed_s":elapsed,"options":options,"optimization_calls":1,"solver_version":solver.version(),
                "numerical_objective_MWh":finite(info.objective_function_value),"simplex_iterations":int(info.simplex_iteration_count),
                "solution_value_valid":bool(solution.value_valid),"solution_dual_valid":bool(solution.dual_valid),
                "exact_optimality_claim":False,"fixed_schedule_negative_is_not_full_UC_negative":True}
        if solution.dual_valid:
            np.savez_compressed(directory/"raw_duals.npz",row_dual=np.asarray(solution.row_dual),column_dual=np.asarray(solution.col_dual))
        accepted=False
        if solution.value_valid:
            raw=np.asarray(solution.col_value);np.savez_compressed(directory/"raw_vector.npz",vector=raw)
            valid=raw.shape==(23016,) and np.isfinite(raw).all()
            result["raw_matrix_check"]=check_vector(A,b,raw) if valid else {"pass":False,"reason":"invalid/nonfinite vector"}
            eligible=bool(valid and np.all(np.abs(raw[STATE]-anchor)<=TOL));result["eligible_for_identity_anchoring"]=eligible
            if eligible:
                point=raw.copy();point[STATE]=anchor
                unchanged=frame_bytes_equal(point[FREE],raw[FREE]);assert unchanged
                assert frame_bytes_equal(point[STATE],anchor)
                np.savez_compressed(directory/"anchored_vector.npz",vector=point)
                fixed=exact_point_check(A,b,point,integer);unfixed=exact_point_check(A,parent_b,point,integer)
                physical=native_check(model,point,native,fossil)
                save(directory/"fixed_exact_point_check.json",fixed);save(directory/"unfixed_exact_point_check.json",unfixed)
                save(directory/"native_full_check.json",physical)
                E=energy(point,c);cap_excess=E-Fraction(23195)
                result.update(P_theta_bitwise_unchanged=unchanged,UYZ_exactly_identity=True,
                    exact_fixed_expanded_pass=fixed["expanded_pass"],exact_unfixed_expanded_pass=unfixed["expanded_pass"],
                    exact_fixed_strict_pass=fixed["strict_pass"],exact_unfixed_strict_pass=unfixed["strict_pass"],
                    native_full_check_pass=physical["pass"],fossil_energy_MWh=rational_record(E),cap_excess_MWh=rational_record(cap_excess))
                accepted=bool(fixed["expanded_pass"] and unfixed["expanded_pass"] and physical["pass"])
                if accepted:
                    assert cap_excess<=Fraction.from_float(TOL)
                    result["verdict"]="VERIFIED_FIXED_IDENTITY_REDISPATCH_EXPANDED_MODEL"
                    result["full_unfixed_expanded_model_positive"]=True
                    p,u,y,z,theta=unpack(point,168,41,24,24)
                    for name,values,cols in [("dispatch",p,meta["unit_names"]),("commitment",u,meta["thermal_unit_names"]),
                        ("startup",y,meta["thermal_unit_names"]),("shutdown",z,meta["thermal_unit_names"]),("angles",theta,meta["bus_ids"])]:
                        pd.DataFrame(values,columns=cols).to_csv(directory/(name+".csv"),index=False)
        if status==highspy.HighsModelStatus.kInfeasible:
            ray,certificate=ray_from_solver(solver,A,b,directory);result["ray_diagnostics"]=ray
            if certificate is not None:
                binding=read(directory/"model_binding.json")
                assert not accepted and not binding["known_exact_fixed_model_positive"],"Fatal positive/fixed-ray contradiction"
                result["verdict"]="REJECTED_FIXED_IDENTITY_SCHEDULE_EXACT_EXPANDED_CERTIFICATE"
                result["full_unfixed_infeasibility_claim"]=False
            elif not accepted:result["unknown_reason"]="Numerical infeasibility without robust exact fixed-schedule ray"
        save(directory/"result.json",result);results.append(result);save(OUT/"results.json",results)
        print(json.dumps({k:result[k] for k in ["case","model_status","verdict","elapsed_s"]}),flush=True)
    assert all(digest(Path(x["path"]))==x["sha256"] for x in manifest)
    counts={key:sum(r["verdict"]==key for r in results) for key in sorted({r["verdict"] for r in results})}
    save(OUT/"completion.json",{"utc":datetime.now(timezone.utc).isoformat(),"optimization_calls":5,"denominator":5,
         "all_frozen_hashes_unchanged":True,"outcomes":counts,"negative_scope":"fixed identity schedule only",
         "prior_day_block_artifacts_edited":False,"new_data_or_replication":False})


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare-only",action="store_true");mode.add_argument("--run-prepared",action="store_true")
    args=parser.parse_args()
    if args.prepare_only:prepare()
    else:run_prepared()
