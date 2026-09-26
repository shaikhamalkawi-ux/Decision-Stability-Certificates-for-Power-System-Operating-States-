"""Frozen continuous mean-repair radii with exact row-dual/box lower bounds."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
import highspy
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, hstack, load_npz, save_npz, vstack

ROOT = Path(__file__).resolve().parents[1]
CASES = ["identity", *(f"seed_{s}" for s in range(26092600,26092604))]
TOL = 1e-5
BINDINGS = {"temporal_lp_certificate.py":"6191c5760811cab0ec22b2fb1376a5be3aa47cb548e1260c4a17e2563d9802e4",
    "research8h_service_cap.py":"28852854da72e6ad7218aa2af18ec41a61c0e2e6438f992bc3481bb520adb40e",
    "v8r1_rts_seasonal.py":"bca0127d7b2771c6da3b6a838c8caa7fb6ce0df4eafd9a512326aabd8daf7dc2"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+"\n",encoding="utf-8")


def frac(x):
    return Fraction.from_float(float(x))


def rational_record(x):
    approximate = float(x)
    lower = approximate
    if frac(lower)>x:
        lower = float(np.nextafter(lower,-np.inf))
    return {"numerator":str(x.numerator),"denominator":str(x.denominator),
        "approximate":approximate,"binary64_rounded_down":lower}


for name,expected in BINDINGS.items():
    assert sha(ROOT/"src"/name)==expected,(name,"bound source changed")
from temporal_lp_certificate import check_vector
from v8r1_rts_seasonal import inputs,load_model


def exact_lower_bound(matrix,bounds,objective,raw):
    """Any projected row multiplier is valid; every arithmetic operation is exact."""
    assert raw.shape==(matrix.shape[0],) and np.isfinite(raw).all()
    assert np.isfinite(bounds["column_lower"]).all() and np.isfinite(bounds["column_upper"]).all()
    forbidden=((raw>0)&~np.isfinite(bounds["row_lower"]))|((raw<0)&~np.isfinite(bounds["row_upper"]))
    dual=raw.copy();dual[forbidden]=0.
    q={int(j):frac(objective[j]) for j in np.flatnonzero(objective)}
    beta=Fraction(0);dual_norm=Fraction(0)
    for row in np.flatnonzero(dual):
        d=frac(dual[row]);dual_norm+=abs(d)
        endpoint=bounds["row_lower" if d>0 else "row_upper"][row]
        assert np.isfinite(endpoint)
        beta+=d*frac(endpoint)
        for k in range(matrix.indptr[row],matrix.indptr[row+1]):
            column=int(matrix.indices[k])
            q[column]=q.get(column,Fraction(0))-d*frac(matrix.data[k])
    q={j:v for j,v in q.items() if v}
    box=Fraction(0);residual_norm=Fraction(0)
    for column,value in q.items():
        endpoint=bounds["column_lower" if value>=0 else "column_upper"][column]
        box+=value*frac(endpoint);residual_norm+=abs(value)
    lower=beta+box
    relaxed=lower-frac(TOL)*(dual_norm+residual_norm)
    report={"arithmetic":"exact rational interpretation of archived binary64 coefficients, bounds, objective and multiplier",
        "raw_lower_bound":rational_record(lower),"nominal_lower_bound_with_epsilon_nonnegativity":rational_record(max(Fraction(0),lower)),
        "outward_tolerance_lower_bound":rational_record(relaxed),"row_term":rational_record(beta),
        "box_term":rational_record(box),"projected_entries":int(forbidden.sum()),
        "largest_projected_magnitude":float(np.abs(raw[forbidden]).max()) if forbidden.any() else 0.,
        "row_multiplier_nonzeros":int(np.count_nonzero(dual)),"stationarity_residual_nonzeros":len(q),
        "row_multiplier_l1":rational_record(dual_norm),"stationarity_residual_l1":rational_record(residual_norm),
        "outward_tolerance":TOL,"outward_model":"Every finite row and column bound expanded by tau, including epsilon box to [-tau,1+tau]; mixed-units numerical robustness, not physical uncertainty.",
        "scope":"Objective lower bound, not an exact optimum and not a binary/DC-network certificate."}
    residuals=[{"column":j,**rational_record(v)} for j,v in sorted(q.items())]
    return report,dual,residuals


def exact_means(mean_matrix,targets,scales,vector,epsilon):
    records=[];largest=Fraction(0)
    for j in range(mean_matrix.shape[0]):
        mean=sum((frac(mean_matrix.data[k])*frac(vector[int(mean_matrix.indices[k])])
            for k in range(mean_matrix.indptr[j],mean_matrix.indptr[j+1])),Fraction(0))
        delta=mean-frac(targets[j]);radius=abs(delta)/frac(scales[j]);largest=max(largest,radius)
        records.append({"unit_index":j,"target_mean_MW":float(targets[j]),"nameplate_MW":float(scales[j]),
            "saved_primal_mean_MW":float(mean),"mean_shift_MW":float(delta),"normalized_absolute_shift":float(radius),
            "exact_mean":rational_record(mean),"exact_normalized_absolute_shift":rational_record(radius),
            "mean_band_exactly_satisfied_by_raw_epsilon":bool(radius<=frac(epsilon))})
    return records,rational_record(largest)


def read_bounds(path):
    with np.load(path) as arrays:
        return {key:arrays[key].copy() for key in arrays.files}


def prepare(case,output,names,scales,source_hi,source_lo,source_rows,source_fossil,freeze):
    src=ROOT/"results/research8h/service_cap"/case
    old=ROOT/"results/temporal_information/lp_certificate"/case
    status=json.loads((src/"result.json").read_text())
    assert sha(src/"matrix.npz")==status["matrix_sha256"] and sha(src/"bounds.npz")==status["bounds_sha256"]
    base=load_npz(src/"matrix.npz");bb=read_bounds(src/"bounds.npz")
    original=load_npz(old/"matrix.npz");ob=read_bounds(old/"bounds.npz")
    labels=pd.read_csv(src/"row_metadata.csv.gz");ol=pd.read_csv(old/"row_metadata.csv.gz")
    metadata=json.loads((old/"model_metadata.json").read_text())
    assert metadata["unit_names"]==names and base.shape==(24265,18984)
    assert np.isfinite(bb["column_lower"]).all() and np.isfinite(bb["column_upper"]).all()
    selected=ol.family.eq("target_mean").to_numpy()
    assert selected.sum()==41 and ol.loc[selected,"uid"].tolist()==names
    means=original[selected].tocsr();targets=ob["row_upper"][selected]
    assert np.array_equal(targets,ob["row_lower"][selected])
    assert np.all(targets>=0) and np.all(targets<=scales)
    assert (base[:-1]!=original[~selected]).nnz==0
    assert np.array_equal(bb["column_lower"],ob["column_lower"]) and np.array_equal(bb["column_upper"],ob["column_upper"])
    assert np.array_equal(bb["row_lower"][:-1],ob["row_lower"][~selected])
    assert np.array_equal(bb["row_upper"][:-1],ob["row_upper"][~selected])
    assert labels.family.eq("fossil_energy_cap").sum()==1 and labels.family.iloc[-1]=="fossil_energy_cap"
    assert not labels.family.eq("target_mean").any()
    assert bb["row_upper"][-1]==freeze["budget_MWh"] and np.isneginf(bb["row_lower"][-1])
    cap=base[-1]
    wanted=np.array([t*41+j for t in range(168) for j in source_fossil])
    assert np.array_equal(np.sort(cap.indices),np.sort(wanted)) and np.all(cap.data==1.)
    assert freeze["fossil_units"]==[names[j] for j in source_fossil]
    paths=[src/p for p in ["matrix.npz","bounds.npz","model_metadata.json","row_metadata.csv.gz","result.json"]]
    paths.extend(old/p for p in ["matrix.npz","bounds.npz","model_metadata.json","row_metadata.csv.gz","result.json"])
    if case=="identity":
        order=np.arange(168)
    else:
        path=ROOT/"results/temporal_information/twins"/case/"permutation.csv"
        table=pd.read_csv(path);order=table.source_hour_0based.to_numpy(int)
        assert np.array_equal(np.sort(order),np.arange(168))
        assert np.array_equal(table.source_native_row.to_numpy(int),source_rows[order])
        paths.append(path)
    assert np.array_equal(bb["column_upper"][:6888].reshape(168,41),source_hi[order])
    assert np.all(source_hi[order]<=scales) and np.all(scales>0)
    for j in range(41):
        assert np.array_equal(means[j].indices,np.arange(168)*41+j)
        assert np.all(means[j].data==np.float64(1/168))
    extensions=[];upper=[];newlabels=[]
    for j,uid in enumerate(names):
        for direction,name in [(1,"mean_upper_band"),(-1,"mean_lower_band")]:
            extensions.append(hstack([direction*means[j],csr_matrix([[-scales[j]]])],format="csr"))
            upper.append(direction*targets[j]);newlabels.append({"family":name,"hour_0based":-1,"uid":uid})
    matrix=vstack([hstack([base,csr_matrix((base.shape[0],1))],format="csr"),*extensions],format="csr")
    bounds={"column_lower":np.r_[bb["column_lower"],0.],"column_upper":np.r_[bb["column_upper"],1.],
        "row_lower":np.r_[bb["row_lower"],np.full(82,-np.inf)],"row_upper":np.r_[bb["row_upper"],upper]}
    objective=np.zeros(matrix.shape[1]);objective[-1]=1.
    all_labels=labels.to_dict("records")+newlabels
    for row,label in enumerate(all_labels):label["row"]=row
    assert matrix.shape==(24347,18985) and np.count_nonzero(objective)==1
    directory=output/case;directory.mkdir()
    save_npz(directory/"matrix.npz",matrix);save_npz(directory/"original_mean_rows.npz",means)
    np.savez_compressed(directory/"bounds.npz",**bounds)
    np.savez_compressed(directory/"objective.npz",objective=objective)
    np.savez_compressed(directory/"mean_inputs.npz",targets=targets,scales=scales)
    pd.DataFrame(all_labels).to_csv(directory/"row_metadata.csv.gz",index=False,compression="gzip")
    pd.DataFrame({"uid":names,"target_mean_MW":targets,"native_nameplate_MW":scales}).to_csv(directory/"mean_targets_and_scales.csv",index=False)
    pd.DataFrame({"hour_0based":np.arange(168),"source_hour_0based":order,"source_native_row":source_rows[order]}).to_csv(directory/"source_order.csv",index=False)
    save(directory/"model_metadata.json",{**metadata,"rows":matrix.shape[0],"columns":matrix.shape[1],"nonzeros":matrix.nnz,
        "epsilon_column":matrix.shape[1]-1,"epsilon_bounds":[0,1],"objective":"epsilon only",
        "all_states_continuous":True,"network":"aggregate balance; no DC constraints","mean_equality_rows":0,
        "mean_band_rows":82,"same_fossil_cap_MWh":freeze["budget_MWh"],"fossil_units":freeze["fossil_units"],
        "base_archive_rows_and_bounds_exact_match":True,"native_availability_exact_match":True,
        "mean_row_coefficients_and_targets_copied_exactly":True,"all_source_caps_within_positive_nameplates":True})
    paths.extend(directory/p for p in ["matrix.npz","bounds.npz","objective.npz","original_mean_rows.npz","mean_inputs.npz"])
    return directory,(matrix,bounds,objective,means,targets,scales,cap),paths


def number(x):
    x=float(x)
    return x if np.isfinite(x) else None


def run(case,directory,data,names):
    matrix,bounds,objective,means,targets,scales,cap=data
    lp=highspy.HighsLp();lp.num_row_,lp.num_col_=matrix.shape
    lp.col_cost_,lp.col_lower_,lp.col_upper_=objective,bounds["column_lower"],bounds["column_upper"]
    lp.row_lower_,lp.row_upper_=bounds["row_lower"],bounds["row_upper"]
    lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise
    lp.a_matrix_.num_row_,lp.a_matrix_.num_col_=matrix.shape
    lp.a_matrix_.start_,lp.a_matrix_.index_,lp.a_matrix_.value_=matrix.indptr,matrix.indices,matrix.data
    solver=highspy.Highs()
    options={"time_limit":60.,"threads":1,"random_seed":0,"solver":"simplex","presolve":"off",
        "log_to_console":False,"log_file":str(directory/"solver.log")}
    for key,value in options.items():assert solver.setOptionValue(key,value)==highspy.HighsStatus.kOk
    assert solver.passModel(lp)==highspy.HighsStatus.kOk
    started=time.perf_counter();run_status=solver.run();elapsed=time.perf_counter()-started
    status,solution,info=solver.getModelStatus(),solver.getSolution(),solver.getInfo()
    result={"case":case,"model_status":solver.modelStatusToString(status),"run_status":str(run_status),
        "solver_version":solver.version(),"elapsed_s":elapsed,"options":options,"optimization_calls":1,
        "solution_value_valid":bool(solution.value_valid),"solution_dual_valid":bool(solution.dual_valid),
        "numeric_objective_epsilon":number(info.objective_function_value),"primal_solution_status":int(info.primal_solution_status),
        "dual_solution_status":int(info.dual_solution_status),"max_primal_infeasibility":number(info.max_primal_infeasibility),
        "max_dual_infeasibility":number(info.max_dual_infeasibility),"simplex_iterations":int(info.simplex_iteration_count),
        "verdict":"UNKNOWN_NO_VERIFIED_PRIMAL","exact_optimum_claim":False}
    if solution.value_valid:
        vector=np.asarray(solution.col_value)
        np.savez_compressed(directory/"primal.npz",vector=vector,row_value=np.asarray(solution.row_value))
        check=check_vector(matrix,bounds,vector);save(directory/"primal_check.json",check)
        result["primal_verification_pass"]=check["pass"]
        if np.isfinite(vector).all():
            tables,exact_radius=exact_means(means,targets,scales,vector,float(vector[-1]))
            for row,uid in zip(tables,names):row["uid"]=uid
            save(directory/"exact_mean_diagnostics.json",{"units":tables,"largest_required_radius_for_saved_P":exact_radius,
                "warning":"Even exact satisfaction of these bands would not repair retained-row residuals."})
            pd.DataFrame([{key:value for key,value in row.items() if not isinstance(value,dict)} for row in tables]).to_csv(directory/"mean_shifts.csv",index=False)
            pd.DataFrame(vector[:6888].reshape(168,41),columns=names).to_csv(directory/"continuous_dispatch.csv",index=False)
            result.update(raw_primal_epsilon=float(vector[-1]),maximum_normalized_mean_shift=exact_radius["approximate"],
                fossil_energy_MWh=float((cap@vector[:-1])[0]),
                fractional_state_coordinates=int(np.count_nonzero(np.abs(vector[6888:-1]-np.rint(vector[6888:-1]))>TOL)))
            if check["pass"]:
                result["verdict"]="TOLERANCE_VERIFIED_CONTINUOUS_MEAN_REPAIR_CANDIDATE"
                result["numeric_primal_upper_estimate"]=max(0.,float(vector[-1]))
                result["upper_estimate_qualification"]="Numerical candidate at absolute matrix/box tolerance 1e-5; not a rigorous upper bound on the exact LP optimum. Raw epsilon and residuals retained."
    if solution.dual_valid:
        raw=np.asarray(solution.row_dual);column=np.asarray(solution.col_dual)
        np.savez_compressed(directory/"raw_duals.npz",row_dual=raw,column_dual=column)
        report,projected,residuals=exact_lower_bound(matrix,bounds,objective,raw)
        np.savez_compressed(directory/"projected_row_dual.npz",row_dual=projected)
        save(directory/"exact_lower_bound.json",report)
        save(directory/"exact_stationarity_residual.json",residuals)
        result["exact_nominal_lower_bound_approximate"]=report["nominal_lower_bound_with_epsilon_nonnegativity"]["approximate"]
        result["exact_outward_tolerance_lower_bound_approximate"]=report["outward_tolerance_lower_bound"]["approximate"]
        if case=="identity":
            control=json.loads((directory.parent/"identity_existing_witness_control.json").read_text())
            assert not (control["epsilon_zero_check"]["pass"] and int(report["outward_tolerance_lower_bound"]["numerator"])>0),"Exact bound contradicts tolerance-feasible identity control"
    save(directory/"result.json",result)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-v3",type=Path,required=True)
    parser.add_argument("--output",type=Path,default=ROOT/"results/research8h/mean_repair")
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    protocol=ROOT/"docs/research8h/MEAN_REPAIR_PROTOCOL.md"
    cap_freeze=ROOT/"results/research8h/service_cap/pre_run_freeze.json"
    frozen=json.loads(cap_freeze.read_text())
    assert frozen["cases"]==CASES
    for relative,expected in frozen["input_sha256"].items():assert sha(ROOT/relative)==expected,(relative,"old source changed")
    model=load_model(args.source_v3)
    names,unused,lo,hi,net,native_paths=inputs(model,args.source_v3,7)
    scales=model.dec["PMax MW"].to_numpy(float)
    assert np.isfinite(scales).all() and np.all(scales>0) and np.all(hi<=scales)
    assert len(names)==41 and model.dec["GEN UID"].tolist()==names
    native_rows=pd.read_csv(native_paths[1])["row"].to_numpy(int)
    fossil=[int(j) for j in model.urows if model.dec.iloc[j]["Fuel"] in {"Coal","Oil","NG"}]
    assert len(fossil)==23
    save(args.output/"pre_run_freeze.json",{"utc":datetime.now(timezone.utc).isoformat(),"cases":CASES,
        "protocol_sha256":sha(protocol),"script_sha256":sha(Path(__file__)),"bound_sources":BINDINGS,
        "seconds_per_case":60,"threads":1,"random_seed":0,"solver":"simplex","presolve":"off",
        "objective":"epsilon","epsilon_box":[0,1],"same_budget_MWh":frozen["budget_MWh"],
        "nameplates_positive":True,"min_scale_MW":float(scales.min()),"max_scale_MW":float(scales.max()),
        "source_hourly_max_excess_above_nameplate_MW":float((hi-scales).max()),
        "interpretation":"Continuous named-unit mean-repair radius normalized by native nameplate; no DC/binary inference."})
    paths=[Path(__file__),protocol,cap_freeze,*[ROOT/"src"/p for p in BINDINGS],*native_paths,
        args.source_v3/"code/dscgrid_model.py",*sorted((args.source_v3/"raw").rglob("*.csv"))]
    prepared=[]
    for case in CASES:
        directory,data,used=prepare(case,args.output,names,scales,hi,lo,native_rows,fossil,frozen)
        prepared.append((case,directory,data));paths.extend(used)
    matrix,bounds,objective,*_=prepared[0][2]
    zero,_,_=exact_lower_bound(matrix,bounds,objective,np.zeros(matrix.shape[0]))
    assert zero["raw_lower_bound"]["numerator"]=="0"
    save(args.output/"zero_multiplier_sanity_check.json",zero)
    reference=ROOT/"results/v8/network_repair"
    pp,up=reference/"network_repair_dispatch.csv",reference/"network_fixed_commitment.csv"
    p=pd.read_csv(pp)[names].to_numpy(float);u=pd.read_csv(up)[model.dec.iloc[model.urows]["GEN UID"]].to_numpy(float)
    y,z=np.zeros_like(u),np.zeros_like(u)
    y[1:],z[1:]=np.maximum(np.diff(u,axis=0),0),np.maximum(-np.diff(u,axis=0),0)
    control=check_vector(matrix,bounds,np.r_[p.ravel(),u.ravel(),y.ravel(),z.ravel(),0.])
    assert control["pass"],control
    save(args.output/"identity_existing_witness_control.json",{"epsilon_zero_check":control,
        "meaning":"Tolerance control, not an exact rational feasible solution; coefficients/means unretuned."})
    paths.extend([pp,up]);paths.extend(ROOT/p for p in frozen["input_sha256"])
    manifest=[{"path":str(p),"sha256":sha(p),"bytes":p.stat().st_size} for p in dict.fromkeys(paths)]
    pd.DataFrame(manifest).to_csv(args.output/"input_manifest.csv",index=False)
    save(args.output/"all_models_frozen_before_first_solve.json",{"utc":datetime.now(timezone.utc).isoformat(),
        "manifest_sha256":sha(args.output/"input_manifest.csv"),"cases":CASES,"identity_epsilon_zero_control_pass":True})
    results=[]
    for case,directory,data in prepared:
        result=run(case,directory,data,names);results.append(result);save(args.output/"summary.json",results)
        print(json.dumps({key:result.get(key) for key in ["case","model_status","verdict","elapsed_s",
            "numeric_objective_epsilon","exact_nominal_lower_bound_approximate","exact_outward_tolerance_lower_bound_approximate"]}),flush=True)
    assert all(sha(Path(x["path"]))==x["sha256"] for x in manifest)
    pd.DataFrame([{key:value for key,value in row.items() if not isinstance(value,(list,dict))} for row in results]).to_csv(args.output/"summary.csv",index=False)
    save(args.output/"completion.json",{"utc":datetime.now(timezone.utc).isoformat(),"optimization_calls":5,
        "source_and_frozen_model_hashes_unchanged":True,"exact_optimum_claim":False})


if __name__=="__main__":main()
