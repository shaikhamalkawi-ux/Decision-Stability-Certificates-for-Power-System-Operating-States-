"""Prepare, then separately run two uncapped January U-only MIPs."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import json
from pathlib import Path
import time

import highspy
import numpy as np
import pandas as pd
from scipy.sparse import load_npz, save_npz

from research8h_seasonal_reference import physical_check
from research8h_service_network_mip import unpack
from research8h_u_only_continuation import audit_projection
from temporal_lp_certificate import check_vector, digest, save
from v8r1_rts_seasonal import load_model

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"results/research8h/seasonal_transfer"
OUTPUT=ROOT/"results/seasonal_uncapped"
CASES=["seed_26093100","seed_26093101"]
SECONDS=600
TOL=1e-5


def rational_record(value):
    return {"numerator":str(value.numerator),"denominator":str(value.denominator),"float":float(value)}


def exact_point_check(matrix,bounds,vector,original_integer):
    """Exact binary64 point membership, strict and uniformly widened bounds."""
    if len(vector)!=matrix.shape[1] or not np.isfinite(vector).all():
        return {"strict_pass":False,"expanded_pass":False,"reason":"invalid vector"}
    point=[Fraction.from_float(float(x)) for x in vector]
    tau=Fraction.from_float(TOL)
    integral=all(point[j].denominator==1 and point[j] in (0,1) for j in np.flatnonzero(original_integer))
    colmax=rowmax=Fraction(0)
    colworst=rowworst=None
    for j,x in enumerate(point):
        for side in ("lower","upper"):
            bound=bounds[f"column_{side}"][j]
            if np.isfinite(bound):
                b=Fraction.from_float(float(bound));violation=b-x if side=="lower" else x-b
                if violation>colmax: colmax,colworst=violation,{"column":j,"side":side}
    for i in range(matrix.shape[0]):
        lhs=sum((Fraction.from_float(float(matrix.data[e]))*point[int(matrix.indices[e])]
                 for e in range(matrix.indptr[i],matrix.indptr[i+1])),Fraction(0))
        for side in ("lower","upper"):
            bound=bounds[f"row_{side}"][i]
            if np.isfinite(bound):
                b=Fraction.from_float(float(bound));violation=b-lhs if side=="lower" else lhs-b
                if violation>rowmax: rowmax,rowworst=violation,{"row":i,"side":side}
    return {"strict_pass":bool(integral and colmax<=0 and rowmax<=0),
        "expanded_pass":bool(integral and colmax<=tau and rowmax<=tau),
        "original_binary_coordinates_exact":integral,"tau":rational_record(tau),
        "maximum_column_violation":rational_record(colmax),"worst_column":colworst,
        "maximum_row_violation":rational_record(rowmax),"worst_row":rowworst,
        "arithmetic":"exact rational interpretation of every archived binary64 matrix/bound/vector coefficient",
        "expanded_model":"every finite row/column bound expanded outward by exactly Fraction.from_float(1e-5)"}


def check_manifest(path):
    records=pd.read_csv(path)
    bad=[]
    for row in records.itertuples(index=False):
        p=Path(row.path)
        if p.stat().st_size!=row.bytes or digest(p)!=row.sha256: bad.append(str(p))
    assert not bad,bad
    return {"pass":True,"files_checked":len(records),"manifest_sha256":digest(path)}


def prepare(source_v3):
    OUTPUT.mkdir(parents=True,exist_ok=False)
    protocol=ROOT/"docs/research8h/SEASONAL_UNCAPPED_PROTOCOL.md"
    model=load_model(source_v3)
    names=model.dec["GEN UID"].tolist()
    thermal=model.dec.iloc[model.urows]["GEN UID"].tolist()
    fossil=[int(j) for j in model.urows if model.dec.iloc[j]["Fuel"] in {"Coal","Oil","NG"}]
    assert len(fossil)==23 and [names[j] for j in model.urows if j not in fossil]==["121_NUCLEAR_1"]
    save(OUTPUT/"source_transfer_manifest_check.json",check_manifest(SOURCE/"input_manifest.csv"))
    paths=[Path(__file__),protocol,SOURCE/"input_manifest.csv",SOURCE/"models_frozen_before_first_solve.json",
        ROOT/"docs/research8h/U_ONLY_CONTINUATION_PROTOCOL.md",
        *[ROOT/"src"/name for name in ["research8h_u_only_continuation.py","research8h_seasonal_reference.py",
        "research8h_service_network_mip.py","research8h_service_network.py","temporal_lp_certificate.py",
        "temporal_information_pilot.py","v8r1_rts_seasonal.py"]],source_v3/"code/dscgrid_model.py",
        *sorted((source_v3/"raw").rglob("*.csv"))]
    for case in CASES:
        src=SOURCE/case
        original=load_npz(src/"matrix.npz")
        with np.load(src/"bounds.npz") as a: old_bounds={k:a[k].copy() for k in a.files}
        with np.load(src/"native_inputs.npz") as a: native={k:a[k].copy() for k in a.files}
        with np.load(src/"integrality.npz") as a: old_integer=a["integrality"].copy()
        meta=json.loads((src/"model_metadata.json").read_text());labels=pd.read_csv(src/"row_metadata.csv.gz")
        assert meta["unit_names"]==names and meta["thermal_unit_names"]==thermal
        assert meta["fossil_units"]==[names[j] for j in fossil] and meta["individual_mean_constraints"]==0
        keep=~labels.family.eq("fossil_energy_cap").to_numpy()
        assert (~keep).sum()==1 and not labels.family.eq("target_mean").any()
        removed=int(np.flatnonzero(~keep)[0])
        matrix=original[keep].tocsr()
        bounds={k:(a[keep] if k.startswith("row_") else a.copy()) for k,a in old_bounds.items()}
        labels=labels.loc[keep].copy().reset_index(drop=True);labels["row"]=np.arange(len(labels))
        integer,audit=audit_projection(matrix,bounds,meta,labels,old_integer)
        objective=np.zeros(matrix.shape[1]);objective[[t*41+j for t in range(168) for j in fossil]]=1.
        assert np.count_nonzero(objective)==23*168 and np.all(objective[meta["offsets"]["U"]:]==0)
        old_cap=meta.pop("budget_MWh")
        meta.update(rows=matrix.shape[0],nonzeros=matrix.nnz,energy_cap_constraints=0,individual_mean_constraints=0,
            binary_columns=int(integer.sum()),objective="minimize total 23-fossil-unit MWh; no cap",
            auxiliary_objective_coefficients_zero=True,removed_source_cap_MWh=old_cap)
        assert not labels.family.isin(["fossil_energy_cap","target_mean"]).any()
        directory=OUTPUT/case;directory.mkdir()
        save_npz(directory/"matrix.npz",matrix)
        np.savez_compressed(directory/"bounds.npz",**bounds)
        np.savez_compressed(directory/"integrality.npz",integrality=integer)
        np.savez_compressed(directory/"original_integrality.npz",integrality=old_integer)
        np.savez_compressed(directory/"objective.npz",objective=objective)
        np.savez_compressed(directory/"native_inputs.npz",**native)
        labels.to_csv(directory/"row_metadata.csv.gz",index=False,compression="gzip")
        save(directory/"model_metadata.json",meta);save(directory/"projection_audit.json",audit)
        save(directory/"model_binding.json",{"source_case":str(src.relative_to(ROOT)),"source_matrix_sha256":digest(src/"matrix.npz"),
            "source_bounds_sha256":digest(src/"bounds.npz"),"source_integrality_sha256":digest(src/"integrality.npz"),
            "deleted_row_0based":removed,"deleted_row_family":"fossil_energy_cap","all_other_rows_and_bounds_unchanged":True,
            "matrix_sha256":digest(directory/"matrix.npz"),"bounds_sha256":digest(directory/"bounds.npz"),
            "projected_integrality_sha256":digest(directory/"integrality.npz"),"objective_sha256":digest(directory/"objective.npz"),
            "native_inputs_exactly_copied":True,"full_binary_checker_integrality_sha256":digest(directory/"original_integrality.npz")})
        paths.extend(src/name for name in ["matrix.npz","bounds.npz","integrality.npz","objective.npz","native_inputs.npz","model_metadata.json","row_metadata.csv.gz"])
        paths.extend(sorted(directory.glob("*")))
    pd.DataFrame([{"path":str(p),"sha256":digest(p),"bytes":p.stat().st_size} for p in dict.fromkeys(paths)]).to_csv(OUTPUT/"input_manifest.csv",index=False)
    freeze={"utc":datetime.now(timezone.utc).isoformat(),"source_sha256":digest(Path(__file__)),"protocol_sha256":digest(protocol),
        "input_manifest_sha256":digest(OUTPUT/"input_manifest.csv"),"cases":CASES,"seconds_per_case":SECONDS,
        "total_configured_solver_seconds":2*SECONDS,"threads":1,"random_seed":0,"presolve":"on","mip_rel_gap":1e-8,
        "warm_start":False,"optimization_calls_per_case":1,"energy_caps":0,"individual_mean_constraints":0,
        "solver_execution_started":False,"requires_parent_go_before_run_prepared":True,"source_v3":str(source_v3.resolve())}
    save(OUTPUT/"prepared_freeze.json",freeze)
    print(json.dumps({"event":"PREPARED_NO_SOLVES","cases":CASES,"source_sha256":freeze["source_sha256"],
        "input_manifest_sha256":freeze["input_manifest_sha256"]}),flush=True)


def finite(value):
    value=float(value)
    return value if np.isfinite(value) else None


def run_prepared(source_v3):
    freeze=json.loads((OUTPUT/"prepared_freeze.json").read_text())
    assert freeze["source_v3"]==str(source_v3.resolve()) and freeze["cases"]==CASES
    assert digest(OUTPUT/"input_manifest.csv")==freeze["input_manifest_sha256"]
    before=check_manifest(OUTPUT/"input_manifest.csv")
    marker=OUTPUT/"execution_started.json"
    with marker.open("x",encoding="utf-8") as stream:
        json.dump({"utc":datetime.now(timezone.utc).isoformat(),"pre_execution_hash_check":before,"planned_calls":2},stream,indent=2)
    model=load_model(source_v3);results=[];overall=time.perf_counter()
    for case in CASES:
        directory=OUTPUT/case
        matrix=load_npz(directory/"matrix.npz")
        with np.load(directory/"bounds.npz") as a: bounds={k:a[k].copy() for k in a.files}
        with np.load(directory/"native_inputs.npz") as a: native={k:a[k].copy() for k in a.files}
        with np.load(directory/"integrality.npz") as a: integer=a["integrality"].copy()
        with np.load(directory/"original_integrality.npz") as a: old_integer=a["integrality"].copy()
        with np.load(directory/"objective.npz") as a: objective=a["objective"].copy()
        meta=json.loads((directory/"model_metadata.json").read_text())
        lp=highspy.HighsLp();lp.num_row_,lp.num_col_=matrix.shape
        lp.col_cost_,lp.col_lower_,lp.col_upper_=objective,bounds["column_lower"],bounds["column_upper"]
        lp.row_lower_,lp.row_upper_=bounds["row_lower"],bounds["row_upper"]
        lp.integrality_=[highspy.HighsVarType.kInteger if x else highspy.HighsVarType.kContinuous for x in integer]
        lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise
        lp.a_matrix_.num_row_,lp.a_matrix_.num_col_=matrix.shape
        lp.a_matrix_.start_,lp.a_matrix_.index_,lp.a_matrix_.value_=matrix.indptr,matrix.indices,matrix.data
        solver=highspy.Highs()
        options={"time_limit":float(SECONDS),"threads":1,"random_seed":0,"presolve":"on","mip_rel_gap":1e-8,
            "log_to_console":False,"log_file":str(directory/"solver.log")}
        for key,value in options.items(): assert solver.setOptionValue(key,value)==highspy.HighsStatus.kOk
        assert solver.passModel(lp)==highspy.HighsStatus.kOk
        started=time.perf_counter();run_status=solver.run();elapsed=time.perf_counter()-started
        status,solution,info=solver.getModelStatus(),solver.getSolution(),solver.getInfo()
        result={"case":case,"model_status":solver.modelStatusToString(status),"run_status":str(run_status),
            "verdict":"UNKNOWN","time_limit_s":SECONDS,"elapsed_s":elapsed,"optimization_calls":1,
            "solver_version":solver.version(),"solver_options":options,"solution_value_valid":bool(solution.value_valid),
            "solver_objective_MWh":finite(info.objective_function_value),
            "solver_reported_numerical_lower_bound_MWh":finite(info.mip_dual_bound),"mip_relative_gap":finite(info.mip_gap),
            "mip_node_count":int(info.mip_node_count),"exact_optimality_claim":False}
        if solution.value_valid:
            raw=np.asarray(solution.col_value);np.savez_compressed(directory/"raw_vector.npz",vector=raw)
            result["raw_matrix_check"]=check_vector(matrix,bounds,raw)
            p,u,y,z,theta=unpack(raw,168,41,24,24)
            eligible=bool(np.isfinite(raw).all() and np.all(np.abs(u-np.rint(u))<=TOL)
                and np.all((np.rint(u)>=0)&(np.rint(u)<=1)))
            result["eligible_for_recovery"]=eligible
            if eligible:
                rounded=np.rint(u);yy,zz=np.zeros_like(rounded),np.zeros_like(rounded)
                yy[1:],zz[1:]=np.maximum(np.diff(rounded,axis=0),0),np.maximum(-np.diff(rounded,axis=0),0)
                recovered=np.concatenate([a.ravel() for a in (p,rounded,yy,zz,theta)])
                np.savez_compressed(directory/"recovered_vector.npz",vector=recovered)
                result["recovered_matrix_check"]=check_vector(matrix,bounds,recovered)
                fossil=[meta["unit_names"].index(uid) for uid in meta["fossil_units"]]
                native_check=physical_check(model,p,rounded,yy,zz,theta,native["pmin"],native["pmax"],native["net"],
                    native["rows"],native["nodal"],fossil)
                save(directory/"native_no_cap_check.json",native_check);result["native_no_cap_pass"]=native_check["pass"]
                exact=exact_point_check(matrix,bounds,recovered,old_integer)
                save(directory/"exact_point_check.json",exact)
                e=sum((Fraction.from_float(float(v)) for v in p[:,fossil].ravel()),Fraction(0))
                result["recovered_fossil_energy"]=rational_record(e)
                result["exact_strict_model_pass"]=exact["strict_pass"]
                result["exact_expanded_model_pass"]=exact["expanded_pass"]
                numerical=result["raw_matrix_check"]["pass"] and result["recovered_matrix_check"]["pass"] and native_check["pass"]
                if numerical and exact["expanded_pass"]:
                    result["verdict"]="VERIFIED_UNCAPPED_BINARY_WITNESS_EXPANDED_MODEL"
                    result["rigorous_energy_upper_bound_scope"]="strict_and_expanded_binary64_models" if exact["strict_pass"] else "uniformly_1e-5_expanded_binary64_model_only"
                    for filename,values,columns in [("dispatch",p,meta["unit_names"]),("commitment",rounded,meta["thermal_unit_names"]),
                        ("startup",yy,meta["thermal_unit_names"]),("shutdown",zz,meta["thermal_unit_names"]),("angles",theta,meta["bus_ids"])]:
                        pd.DataFrame(values,columns=columns).to_csv(directory/f"{filename}.csv",index=False)
                elif numerical:
                    result["verdict"]="NUMERICAL_TOLERANCE_ONLY_CANDIDATE"
        if status==highspy.HighsModelStatus.kInfeasible:
            result["numerical_solver_infeasibility_status"]=True
            if result["verdict"]=="UNKNOWN": result["verdict"]="NUMERICAL_MIP_INFEASIBLE_NOT_EXACT_CERTIFICATE"
        save(directory/"result.json",result);results.append(result);save(OUTPUT/"summary.json",results)
        print(json.dumps({k:result[k] for k in ("case","model_status","verdict","elapsed_s")}),flush=True)
    save(OUTPUT/"final_input_hash_check.json",check_manifest(OUTPUT/"input_manifest.csv"))
    save(OUTPUT/"completion.json",{"calls":len(results),"configured_solver_seconds":2*SECONDS,
        "actual_solver_seconds":sum(r["elapsed_s"] for r in results),"execution_and_checks_seconds":time.perf_counter()-overall})
    pd.DataFrame([{k:v for k,v in r.items() if not isinstance(v,(dict,list))} for r in results]).to_csv(OUTPUT/"summary.csv",index=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-v3",type=Path,required=True)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare-only",action="store_true")
    group.add_argument("--run-prepared",action="store_true")
    args=parser.parse_args()
    if args.prepare_only: prepare(args.source_v3)
    else: run_prepared(args.source_v3)


if __name__=="__main__":
    main()
