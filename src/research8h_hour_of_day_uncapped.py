"""Prepare only or run the fixed two-case uncapped HOD continuation once."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from fractions import Fraction
import json
from pathlib import Path
import shutil
import sys
import time
sys.dont_write_bytecode = True
import highspy
import numpy as np
import pandas as pd
from scipy.sparse import load_npz, save_npz

from research8h_day_blocks import load_case
from research8h_energy_lp_refinement import exact_bound
from research8h_energy_price_bounds import arrays, from_rat, objective_and_roster
from research8h_hour_of_day import bit_equal, local_sources
from research8h_seasonal_reference import physical_check
from research8h_seasonal_transfer import energy, transitions
from research8h_seasonal_uncapped import check_manifest, exact_point_check
from research8h_service_network_mip import unpack
from research8h_u_only_continuation import audit_projection
from temporal_lp_certificate import check_vector, digest, save
from v8r1_rts_seasonal import load_model

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/"results/research8h/hour_of_day"
IDENTITY = ROOT/"results/research8h/energy_lp_refinement"
OUT = ROOT/"results/research8h/hour_of_day_uncapped"
PROTOCOL = ROOT/"docs/research8h/HOUR_OF_DAY_UNCAPPED_PROTOCOL.md"
CASES = ["seed_26093200","seed_26093201"]
CUTOFF = datetime(2026,9,27,4,0,0,tzinfo=timezone.utc)
PHASE_SECONDS = 2100
TOL = 1e-5


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def finite(value):
    value = float(value)
    return value if np.isfinite(value) else None


def rational(value):
    scale = 1000000
    lo = value.numerator*scale//value.denominator
    hi = -((-value.numerator*scale)//value.denominator)
    def decimal(n):
        return ("-" if n<0 else "")+str(abs(n)//scale)+"."+str(abs(n)%scale).zfill(6)
    return {"numerator":str(value.numerator),"denominator":str(value.denominator),
        "approximate":float(value),"outward_floor_6dp":decimal(lo),"outward_ceiling_6dp":decimal(hi)}


def check_json_manifest(path, expected):
    assert digest(path) == expected
    rows = read(path)
    assert all(digest(Path(r["path"]))==r["sha256"] for r in rows)
    return {"pass":True,"files":len(rows),"manifest_sha256":expected}


def delete_cap(A,b,labels):
    caps = np.flatnonzero(labels.family.eq("fossil_energy_cap").to_numpy())
    assert len(caps)==1 and not labels.family.str.contains("mean").any()
    cap = int(caps[0]);keep = np.delete(np.arange(A.shape[0]),cap)
    assert np.isneginf(b["row_lower"][cap]) and b["row_upper"][cap]==23195
    reduced = A[keep].tocsr()
    bounds = {k:v[keep].copy() if k.startswith("row_") else v.copy() for k,v in b.items()}
    rows = labels.iloc[keep].copy().reset_index(drop=True)
    rows["source_row_0based"] = keep;rows["row"] = np.arange(len(rows))
    assert not rows.family.isin(["fossil_energy_cap","target_mean"]).any()
    assert all(bit_equal(bounds[k],b[k]) for k in ["column_lower","column_upper"])
    return reduced,bounds,rows,keep,cap


def verify_identity(model,native_gen):
    freeze = read(IDENTITY/"prepared_freeze.json")
    prior_check = check_json_manifest(IDENTITY/"input_manifest.json",freeze["input_manifest_sha256"])
    assert read(IDENTITY/"independent_review.json")["status"] == "PASS_COMPLETE"
    parent = SOURCE/"january_identity"
    A,b,integer,labels,meta,native = load_case(parent)
    uncapped,ub,ul,keep,cap = delete_cap(A,b,labels)
    c,fossil = objective_and_roster(meta,native_gen)
    archive = IDENTITY/"january_identity"
    oldA = load_npz(archive/"matrix.npz").tocsr();oldb = arrays(archive/"bounds.npz")
    assert (oldA!=uncapped).nnz==0 and all(bit_equal(oldb[k],ub[k]) for k in ub)
    assert bit_equal(arrays(archive/"objective.npz")["objective"],c)
    assert np.array_equal(arrays(archive/"original_integrality.npz")["integrality"],integer)
    dual = arrays(archive/"projected_row_dual.npz")["row_dual"]
    report,projected,residual = exact_bound(uncapped,ub,c,dual)
    saved = read(archive/"exact_lower_bound.json")
    for field in ["nominal_lower_bound_MWh","expanded_lower_bound_MWh","row_term","finite_box_term","row_dual_l1","stationarity_residual_l1"]:
        assert report[field] == saved[field]
    result = read(archive/"result.json")
    lower = from_rat(report["expanded_lower_bound_MWh"])
    assert lower == from_rat(result["best_lower_MWh"])
    vector = arrays(parent/"constructive_vector.npz")["vector"]
    exact = exact_point_check(uncapped,ub,vector,integer)
    p,u,y,z,theta = unpack(vector,168,41,24,24)
    native_check = physical_check(model,p,u,y,z,theta,native["pmin"],native["pmax"],native["net"],
        native["rows"],native["nodal"],fossil)
    assert exact["expanded_pass"] and native_check["pass"]
    upper = energy(p,fossil)
    assert upper == from_rat(result["unchanged_binary_upper_MWh"]) and 0<lower<=upper
    binding = {"case":"january_identity","optimization_calls":0,"prior_manifest_check":prior_check,
        "matrix_objective_bounds_original_integrality_equal_after_only_cap_deletion":True,
        "exact_projected_dual_replay":True,"exact_uncapped_binary_upper_check":exact,"native_no_cap_check":native_check,
        "lower_MWh":rational(lower),"reference_upper_MWh":rational(upper),"parent_cap_row_0based":cap,
        "scope":"same uncapped uniformly expanded original-binary January identity"}
    paths = [IDENTITY/"prepared_freeze.json",IDENTITY/"input_manifest.json",IDENTITY/"independent_review.json"]
    paths.extend(archive/name for name in ["matrix.npz","bounds.npz","objective.npz","original_integrality.npz",
        "projected_row_dual.npz","exact_lower_bound.json","result.json"])
    paths.extend(parent/name for name in ["matrix.npz","bounds.npz","integrality.npz","row_metadata.csv.gz",
        "model_metadata.json","native_inputs.npz","constructive_vector.npz"])
    return binding,paths


def prepare(source_v3):
    OUT.mkdir(parents=True,exist_ok=False)
    save(OUT/"freeze_before_preparation.json",{"utc":datetime.now(timezone.utc).isoformat(),
        "source_sha256":digest(Path(__file__)),"protocol_sha256":digest(PROTOCOL),"cases":CASES,"optimization_calls":0})
    assert read(SOURCE/"independent_postrun_review.json")["status"] == "INDEPENDENT_HOD_POSTRUN_PASS"
    source_freeze = read(SOURCE/"prepared_freeze.json")
    assert digest(SOURCE/"input_manifest.csv") == source_freeze["manifest_sha256"]
    save(OUT/"parent_manifest_check.json",check_manifest(SOURCE/"input_manifest.csv"))
    prior_outcomes = read(SOURCE/"outcomes.json")
    assert [x["case"] for x in prior_outcomes] == CASES
    assert all(x["verdict"]=="CERTIFIED_INFEASIBLE_EXPANDED_MODEL" for x in prior_outcomes)
    model = load_model(source_v3)
    gen_paths = list((source_v3/"raw").rglob("gen.csv"));assert len(gen_paths)==1
    native_gen = pd.read_csv(gen_paths[0],keep_default_na=False).to_dict("records")
    identity,identity_paths = verify_identity(model,native_gen)
    save(OUT/"reused_identity_bounds.json",identity)
    paths = [PROTOCOL,*local_sources(Path(__file__)),SOURCE/"prepared_freeze.json",SOURCE/"input_manifest.csv",
        SOURCE/"independent_postrun_review.json",SOURCE/"outcomes.json",SOURCE/"completion.json",*identity_paths,
        source_v3/"code/dscgrid_model.py",*sorted((source_v3/"raw").rglob("*.csv"))]
    prepared = []
    for case in CASES:
        parent = SOURCE/case
        oldA,oldb,old_integer,oldlabels,oldmeta,native = load_case(parent)
        A,b,labels,keep,cap = delete_cap(oldA,oldb,oldlabels)
        c,fossil = objective_and_roster(oldmeta,native_gen)
        assert oldmeta["unit_names"]==model.dec["GEN UID"].tolist()
        assert oldmeta["thermal_unit_names"]==model.dec.iloc[model.urows]["GEN UID"].tolist()
        assert np.array_equal(oldA.getrow(cap).toarray().ravel(),c)
        assert np.count_nonzero(c)==3864 and np.all(c[6888:]==0)
        integer,projection = audit_projection(A,b,oldmeta,labels,old_integer)
        assert np.array_equal(np.flatnonzero(integer),np.arange(6888,10920))
        meta = {**oldmeta,"rows":A.shape[0],"nonzeros":A.nnz,"binary_columns":int(integer.sum()),
            "original_binary_columns":int(old_integer.sum()),"energy_cap_constraints":0,
            "removed_source_cap_MWh":oldmeta["budget_MWh"],"objective":"minimize native23-fossil electrical MWh; no cap",
            "original_source_case":case,"individual_mean_constraints":0}
        del meta["budget_MWh"]
        directory = OUT/case;directory.mkdir()
        save_npz(directory/"matrix.npz",A);np.savez_compressed(directory/"bounds.npz",**b)
        np.savez_compressed(directory/"integrality.npz",integrality=integer)
        np.savez_compressed(directory/"original_integrality.npz",integrality=old_integer)
        np.savez_compressed(directory/"objective.npz",objective=c)
        np.savez_compressed(directory/"retained_parent_rows.npz",rows=keep)
        shutil.copyfile(parent/"native_inputs.npz",directory/"native_inputs.npz")
        shutil.copyfile(parent/"permutation.csv",directory/"permutation.csv")
        labels.to_csv(directory/"row_metadata.csv.gz",index=False,compression="gzip")
        save(directory/"model_metadata.json",meta);save(directory/"projection_audit.json",projection)
        baseline,_,_ = exact_bound(A,b,c,np.zeros(A.shape[0]))
        save(directory/"zero_dual_baseline.json",baseline)
        record = {"case":case,"source_matrix_sha256":digest(parent/"matrix.npz"),
            "source_bounds_sha256":digest(parent/"bounds.npz"),"source_native_sha256":digest(parent/"native_inputs.npz"),
            "source_integrality_sha256":digest(parent/"integrality.npz"),"deleted_row_0based":cap,
            "deleted_family":"fossil_energy_cap","all_other_rows_and_bounds_unchanged":True,
            "native_and_permutation_bytes_unchanged":True,"objective_equals_deleted_cap_row":True,
            "no_means_or_cap":True,"projected_binary_columns":4032,"original_binary_columns":12096,
            "matrix_sha256":digest(directory/"matrix.npz"),"bounds_sha256":digest(directory/"bounds.npz"),
            "objective_sha256":digest(directory/"objective.npz"),"zero_dual_expanded_lower_MWh":baseline["expanded_lower_bound_MWh"]}
        save(directory/"model_binding.json",record);prepared.append(record)
        paths.extend(parent/name for name in ["matrix.npz","bounds.npz","integrality.npz","row_metadata.csv.gz",
            "model_metadata.json","native_inputs.npz","permutation.csv"])
        print(json.dumps({"event":"PREPARED_TARGET","case":case,"rows":A.shape[0],"removed_cap_row":cap}),flush=True)
    save(OUT/"prepared_cases.json",prepared)
    paths.extend(sorted(p for p in OUT.rglob("*") if p.is_file()))
    manifest = [{"path":str(p.resolve()),"sha256":digest(p),"bytes":p.stat().st_size} for p in dict.fromkeys(paths)]
    pd.DataFrame(manifest).to_csv(OUT/"input_manifest.csv",index=False)
    save(OUT/"prepared_freeze.json",{"utc":datetime.now(timezone.utc).isoformat(),"cases":CASES,
        "source_sha256":digest(Path(__file__)),"protocol_sha256":digest(PROTOCOL),
        "manifest_sha256":digest(OUT/"input_manifest.csv"),"source_v3":str(source_v3.resolve()),
        "MIP_seconds":600,"LP_seconds":60,"phase_seconds":PHASE_SECONDS,"MIP_start_guard_seconds":605,
        "LP_start_guard_seconds":65,"absolute_launch_cutoff_utc":CUTOFF.isoformat(),
        "MIPs_before_LPs":True,"new_identity_solves":0,"optimization_calls":0,"bound_files":len(manifest),
        "requires_root_code_review_independent_prepared_PASS_and_explicit_GO":True})
    print(json.dumps({"event":"PREPARED_NO_SOLVES","manifest_sha256":digest(OUT/"input_manifest.csv"),"bound_files":len(manifest)}),flush=True)


def load_target(directory):
    A = load_npz(directory/"matrix.npz").tocsr();b = arrays(directory/"bounds.npz")
    return A,b,arrays(directory/"objective.npz")["objective"],arrays(directory/"integrality.npz")["integrality"]


def solver_model(A,b,c,integer=None):
    lp = highspy.HighsLp();lp.num_row_,lp.num_col_=A.shape
    lp.col_cost_,lp.col_lower_,lp.col_upper_=c,b["column_lower"],b["column_upper"]
    lp.row_lower_,lp.row_upper_=b["row_lower"],b["row_upper"]
    lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise
    lp.a_matrix_.num_row_,lp.a_matrix_.num_col_=A.shape
    lp.a_matrix_.start_,lp.a_matrix_.index_,lp.a_matrix_.value_=A.indptr,A.indices,A.data
    if integer is not None:
        lp.integrality_=[highspy.HighsVarType.kInteger if x else highspy.HighsVarType.kContinuous for x in integer]
    return lp


def run_mip(model,directory,case,may_start):
    A,b,c,integer=load_target(directory);sub=directory/"mip";sub.mkdir()
    solver=highspy.Highs()
    options={"time_limit":600.,"threads":1,"random_seed":0,"presolve":"on","mip_rel_gap":1e-8,
        "log_to_console":False,"log_file":str(sub/"solver.log")}
    for key,value in options.items():assert solver.setOptionValue(key,value)==highspy.HighsStatus.kOk
    assert solver.passModel(solver_model(A,b,c,integer))==highspy.HighsStatus.kOk
    if not may_start():
        result={"case":case,"verdict":"UNKNOWN","reason":"PHASE_OR_UTC_ACTUAL_CALL_GUARD",
            "optimization_calls":0,"elapsed_s":0.,"options":options,"solver_run_called":False}
        save(sub/"result.json",result)
        return result
    started=time.perf_counter();utc=datetime.now(timezone.utc).isoformat()
    run_status=solver.run();elapsed=time.perf_counter()-started
    status,solution,info=solver.getModelStatus(),solver.getSolution(),solver.getInfo()
    result={"case":case,"verdict":"UNKNOWN","started_utc":utc,"ended_utc":datetime.now(timezone.utc).isoformat(),
        "elapsed_s":elapsed,"optimization_calls":1,"model_status":solver.modelStatusToString(status),
        "run_status":str(run_status),"options":options,"solver_version":solver.version(),
        "solution_value_valid":bool(solution.value_valid),"numerical_objective_MWh":finite(info.objective_function_value),
        "numerical_lower_bound_MWh":finite(info.mip_dual_bound),"numerical_relative_gap":finite(info.mip_gap),
        "mip_node_count":int(info.mip_node_count),"exact_optimality_claim":False}
    result["model_artifacts"]={name:digest(directory/name) for name in ["matrix.npz","bounds.npz","objective.npz",
        "integrality.npz","original_integrality.npz","native_inputs.npz"]}
    result["prepared_manifest_sha256"]=digest(OUT/"input_manifest.csv")
    if solution.value_valid:
        raw=np.asarray(solution.col_value);np.savez_compressed(sub/"raw_vector.npz",vector=raw)
        result["raw_matrix_check"]=check_vector(A,b,raw)
        p,u,y,z,theta=unpack(raw,168,41,24,24)
        eligible=bool(np.isfinite(raw).all() and np.all(np.abs(u-np.rint(u))<=TOL)
            and np.all((np.rint(u)>=0)&(np.rint(u)<=1)))
        result["eligible_for_recovery"]=eligible
        if eligible:
            rounded=np.rint(u);yy,zz=transitions(rounded)
            point=np.concatenate([a.ravel() for a in [p,rounded,yy,zz,theta]])
            pp,_,_,_,tt=unpack(point,168,41,24,24)
            assert bit_equal(p,pp) and bit_equal(theta,tt)
            np.savez_compressed(sub/"recovered_vector.npz",vector=point)
            meta=read(directory/"model_metadata.json");native=arrays(directory/"native_inputs.npz")
            fossil=[meta["unit_names"].index(uid) for uid in meta["fossil_units"]]
            exact=exact_point_check(A,b,point,arrays(directory/"original_integrality.npz")["integrality"])
            physical=physical_check(model,pp,rounded,yy,zz,tt,native["pmin"],native["pmax"],native["net"],
                native["rows"],native["nodal"],fossil)
            recovered=check_vector(A,b,point)
            save(sub/"exact_point_check.json",exact);save(sub/"native_no_cap_check.json",physical)
            result.update(P_theta_bytes_preserved=True,recovered_matrix_check=recovered,native_no_cap_pass=physical["pass"],
                exact_strict_pass=exact["strict_pass"],exact_expanded_pass=exact["expanded_pass"],
                candidate_fossil_MWh=rational(energy(pp,fossil)))
            if result["raw_matrix_check"]["pass"] and recovered["pass"] and physical["pass"] and exact["expanded_pass"]:
                result["verdict"]="VERIFIED_UNCAPPED_BINARY_WITNESS_EXPANDED_MODEL"
                result["verified_upper_MWh"]=rational(energy(pp,fossil))
            else:result["candidate_not_accepted_as_upper_bound"]=True
    save(sub/"result.json",result)
    return result


def run_lp(directory,case,may_start):
    A,b,c,integer=load_target(directory);sub=directory/"lp";sub.mkdir()
    solver=highspy.Highs()
    options={"time_limit":60.,"threads":1,"random_seed":0,"solver":"simplex","presolve":"off",
        "log_to_console":False,"log_file":str(sub/"solver.log")}
    for key,value in options.items():assert solver.setOptionValue(key,value)==highspy.HighsStatus.kOk
    assert solver.passModel(solver_model(A,b,c))==highspy.HighsStatus.kOk
    if not may_start():
        result={"case":case,"new_lower_bound_status":"NOT_RUN_PHASE_OR_UTC_ACTUAL_CALL_GUARD",
            "optimization_calls":0,"elapsed_s":0.,"options":options,"solver_run_called":False}
        save(sub/"result.json",result)
        return result
    started=time.perf_counter();utc=datetime.now(timezone.utc).isoformat()
    run_status=solver.run();elapsed=time.perf_counter()-started
    status,solution,info=solver.getModelStatus(),solver.getSolution(),solver.getInfo()
    result={"case":case,"started_utc":utc,"ended_utc":datetime.now(timezone.utc).isoformat(),
        "elapsed_s":elapsed,"optimization_calls":1,"model_status":solver.modelStatusToString(status),
        "run_status":str(run_status),"options":options,"solver_version":solver.version(),
        "primal_valid":bool(solution.value_valid),"dual_valid":bool(solution.dual_valid),
        "numerical_objective_MWh":finite(info.objective_function_value),"simplex_iterations":int(info.simplex_iteration_count),
        "exact_optimality_claim":False,"new_lower_bound_status":"UNAVAILABLE_RETURNED_DUAL"}
    result["model_artifacts"]={name:digest(directory/name) for name in ["matrix.npz","bounds.npz","objective.npz"]}
    result["prepared_manifest_sha256"]=digest(OUT/"input_manifest.csv")
    if solution.value_valid:
        primal=np.asarray(solution.col_value)
        np.savez_compressed(sub/"primal.npz",vector=primal,row_value=np.asarray(solution.row_value))
        result["numerical_primal_check"]=check_vector(A,b,primal)
        result["continuous_primal_not_binary_upper"]=True
    if solution.dual_valid:
        raw=np.asarray(solution.row_dual)
        np.savez_compressed(sub/"raw_duals.npz",row_dual=raw,column_dual=np.asarray(solution.col_dual))
        if raw.shape==(A.shape[0],) and np.isfinite(raw).all():
            report,projected,q=exact_bound(A,b,c,raw)
            np.savez_compressed(sub/"projected_row_dual.npz",row_dual=projected)
            save(sub/"exact_lower_bound.json",report);save(sub/"exact_stationarity_residual.json",q)
            result.update(new_lower_bound_status="EXACT_EXPANDED_OBJECTIVE_LOWER_BOUND",
                expanded_lower_MWh=report["expanded_lower_bound_MWh"],nominal_lower_MWh=report["nominal_lower_bound_MWh"])
        else:result["new_lower_bound_status"]="NONFINITE_OR_WRONG_SHAPE_DUAL"
    save(sub/"result.json",result)
    return result


def finalize_bounds(mips,lps):
    identity=read(OUT/"reused_identity_bounds.json")
    li,eref=from_rat(identity["lower_MWh"]),from_rat(identity["reference_upper_MWh"])
    rows=[]
    for case in CASES:
        baseline=from_rat(read(OUT/case/"zero_dual_baseline.json")["expanded_lower_bound_MWh"])
        fresh=from_rat(lps[case]["expanded_lower_MWh"]) if "expanded_lower_MWh" in lps[case] else None
        lower=max(baseline,fresh) if fresh is not None else baseline
        upper=from_rat(mips[case]["verified_upper_MWh"]) if "verified_upper_MWh" in mips[case] else None
        row={"case":case,"lower_MWh":rational(lower),"upper_MWh":None if upper is None else rational(upper),
            "identity_lower_MWh":rational(li),"identity_reference_upper_MWh":rational(eref),
            "MIP_verdict":mips[case]["verdict"],"LP_lower_bound_status":lps[case].get("new_lower_bound_status","NOT_RUN"),
            "finite_uncapped_feasibility_established":upper is not None,
            "scope":"uncapped uniformly expanded original-binary models; identity reused, not reoptimized"}
        if upper is not None:
            if lower>upper:
                save(OUT/"fatal_bound_contradiction.json",row)
                raise AssertionError("Exact lower exceeds accepted binary upper")
            row["optimum_difference_MWh"]={"lower":rational(lower-eref),"upper":rational(upper-li)}
            row["target_optimum_excess_over_chosen_incumbent_MWh"]={"lower":rational(lower-eref),"upper":rational(upper-eref)}
            if li>0 and lower>0:
                lo,hi=lower/eref-1,upper/li-1
                row["optimal_relative_penalty"]={"lower":rational(lo),"upper":rational(hi)}
                row["optimal_relative_penalty_percent"]={"lower":rational(100*lo),"upper":rational(100*hi)}
        rows.append(row)
    save(OUT/"energy_brackets.json",rows)
    return rows


def run_prepared(source_v3):
    invocation_utc=datetime.now(timezone.utc);invocation_clock=time.perf_counter()
    freeze=read(OUT/"prepared_freeze.json")
    assert freeze["cases"]==CASES and freeze["source_v3"]==str(source_v3.resolve())
    assert digest(OUT/"input_manifest.csv")==freeze["manifest_sha256"]
    before=check_manifest(OUT/"input_manifest.csv")
    with (OUT/"execution_started.json").open("x",encoding="utf-8") as stream:
        json.dump({"invocation_utc":invocation_utc.isoformat(),"utc_after_entry_validation":datetime.now(timezone.utc).isoformat(),
            "pre_execution_hash_check":before,"max_MIP_calls":2,"max_LP_calls":2,"new_identity_solves":0},stream,indent=2)
    model=load_model(source_v3)
    phase=time.perf_counter();phase_utc=datetime.now(timezone.utc)
    save(OUT/"allocation_started.json",{"utc":phase_utc.isoformat(),"perf_counter":phase,
        "entry_validation_and_native_loading_s":phase-invocation_clock,"soft_phase_seconds":PHASE_SECONDS,
        "absolute_launch_cutoff_utc":CUTOFF.isoformat()})
    decisions=[];mips={};lps={}
    def allowed(kind,case,guard):
        now=datetime.now(timezone.utc)
        phase_left=PHASE_SECONDS-(time.perf_counter()-phase);cutoff_left=(CUTOFF-now).total_seconds()
        admitted=min(phase_left,cutoff_left)>=guard
        decisions.append({"kind":kind,"case":case,"utc":now.isoformat(),"phase_remaining_s":phase_left,
            "cutoff_remaining_s":cutoff_left,"guard_s":guard,"admitted":admitted})
        save(OUT/"launch_decisions.json",decisions)
        return admitted
    for case in CASES:
        mips[case]=run_mip(model,OUT/case,case,lambda case=case:allowed("MIP",case,605))
        save(OUT/"mip_results.json",mips)
        print(json.dumps({"stage":"MIP","case":case,"verdict":mips[case]["verdict"],"elapsed_s":mips[case]["elapsed_s"]}),flush=True)
    for case in CASES:
        lps[case]=run_lp(OUT/case,case,lambda case=case:allowed("LP",case,65))
        save(OUT/"lp_results.json",lps)
        print(json.dumps({"stage":"LP","case":case,"status":lps[case]["new_lower_bound_status"],"elapsed_s":lps[case]["elapsed_s"]}),flush=True)
    rows=finalize_bounds(mips,lps)
    after=check_manifest(OUT/"input_manifest.csv");save(OUT/"final_manifest_check.json",after)
    ended=datetime.now(timezone.utc);elapsed=time.perf_counter()-phase
    save(OUT/"completion.json",{"utc":ended.isoformat(),"ordinary_denominator":2,
        "MIP_calls":sum(r["optimization_calls"] for r in mips.values()),"LP_calls":sum(r["optimization_calls"] for r in lps.values()),
        "new_identity_solves":0,"phase_elapsed_s":elapsed,"soft_allocation_s":PHASE_SECONDS,
        "soft_allocation_overrun_s":max(0.,elapsed-PHASE_SECONDS),"UTC_cutoff_overrun_s":max(0.,(ended-CUTOFF).total_seconds()),
        "invocation_elapsed_s":time.perf_counter()-invocation_clock,"actual_MIP_seconds":sum(r["elapsed_s"] for r in mips.values()),
        "actual_LP_seconds":sum(r["elapsed_s"] for r in lps.values()),"all_frozen_hashes_unchanged":True,
        "accepted_upper_witnesses":sum(r["finite_uncapped_feasibility_established"] for r in rows),
        "nominal_exact_optimality_claim":False,"postrun_independent_replay_required":True})


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-v3",type=Path,required=True)
    modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--prepare-only",action="store_true");modes.add_argument("--run-prepared",action="store_true")
    args=parser.parse_args()
    if args.prepare_only:prepare(args.source_v3)
    else:run_prepared(args.source_v3)
