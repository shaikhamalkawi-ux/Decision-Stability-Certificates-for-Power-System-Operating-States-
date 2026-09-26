"""Four frozen seasonal fossil-energy references; no per-unit means or energy caps."""
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
from scipy.sparse import load_npz, save_npz

ROOT = Path(__file__).resolve().parents[1]
MONTHS = [1, 4, 7, 10]
TOL = 1e-5
BINDINGS = {
    "research8h_service_network_mip.py": "a8c9c73b9f85b10afbb7aa93672ca595ccff6f30a1584faefeea5599a775c760",
    "research8h_service_network.py": "1cdfa891e4b83e685bb38021709b99066aae6daa994e3c4500e815357f156a41",
    "temporal_lp_certificate.py": "6191c5760811cab0ec22b2fb1376a5be3aa47cb548e1260c4a17e2563d9802e4",
    "v8r1_rts_seasonal.py": "bca0127d7b2771c6da3b6a838c8caa7fb6ce0df4eafd9a512326aabd8daf7dc2",
    "temporal_information_pilot.py": "f2e50b7dccb0e1869c8667a00e32c9d2f1d3f1f641459d4ccb802abe0074d4a0",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


for filename, expected in BINDINGS.items():
    assert sha(ROOT / "src" / filename) == expected, (filename, "source changed")
from research8h_service_network_mip import build, unpack
from research8h_service_network import reconstruct_angles
from temporal_information_pilot import nodal_check
from temporal_lp_certificate import check_vector
from v8r1_rts_seasonal import inputs, load_model


def physical_check(model, p, u, y, z, theta, lo, hi, net, rows, nodal, fossil):
    """Direct no-cap/no-mean physical check, independent of matrix construction."""
    arrays = [p, u, y, z, theta, lo, hi, net, nodal]
    if not all(np.isfinite(a).all() for a in arrays):
        return {"pass": False, "reason": "nonfinite value"}
    ti = np.asarray(model.urows)
    ub = np.rint(u).astype(int)
    pos = lambda a: max(0., float(np.max(a)))
    hydro = model.dec.Category.eq("Hydro").to_numpy()
    r = {
        "negative_dispatch_MW": pos(-p), "availability_MW": pos(p-hi),
        "hydro_fixed_MW": float(np.max(np.abs(p[:, hydro]-lo[:, hydro]))),
        "aggregate_balance_MW": float(np.max(np.abs(p.sum(1)-net))),
        "binary_UYZ": max(float(np.max(np.abs(a-np.rint(a)))) for a in [u,y,z]),
        "state_lower": max(pos(-a) for a in [u,y,z]),
        "state_upper": max(pos(a-1) for a in [u,y,z]),
        "raw_commitment_upper_MW": pos(p[:,ti]-hi[:,ti]*u),
        "raw_commitment_lower_MW": pos(lo[:,ti]*u-p[:,ti]),
        "rounded_commitment_upper_MW": pos(p[:,ti]-hi[:,ti]*ub),
        "rounded_commitment_lower_MW": pos(lo[:,ti]*ub-p[:,ti]),
        "transition_identity": float(np.max(np.abs(np.diff(u,axis=0)-y[1:]+z[1:]))),
        "exclusive_transition": pos(y+z-1),
        "initial_transition": max(float(np.max(np.abs(y[0]))),float(np.max(np.abs(z[0])))),
        "startup_matches_observed": float(np.max(np.abs(y[1:]-np.maximum(np.diff(ub,axis=0),0)))),
        "shutdown_matches_observed": float(np.max(np.abs(z[1:]-np.maximum(-np.diff(ub,axis=0),0)))),
    }
    thermal = model.dec.iloc[ti]
    up = np.ceil(thermal["Min Up Time Hr"].to_numpy(float)).astype(int)
    down = np.ceil(thermal["Min Down Time Hr"].to_numpy(float)).astype(int)
    violations = []
    for q in range(len(ti)):
        for t in range(1, len(p)):
            change = ub[t,q]-ub[t-1,q]
            length = up[q] if change > 0 else down[q]
            if change and np.any(ub[t:min(len(p),t+length),q] != ub[t,q]):
                violations.append({"thermal_index": q, "hour_0based": t})
    r["observed_residence_violations"] = len(violations)
    online = (ub[1:] == 1) & (ub[:-1] == 1)
    rate = thermal["Ramp Rate MW/Min"].to_numpy(float)*60
    r["native_on_on_ramp_MW"] = pos(np.where(online, np.abs(np.diff(p[:,ti],axis=0))-rate, 0.))
    network, native_nodal = nodal_check(model, p, rows)
    assert np.array_equal(native_nodal, nodal)
    injection = -nodal.copy()
    for j, generator in model.dec.iterrows():
        injection[:,model.bi[int(generator["Bus ID"])]] += p[:,j]
    flows = (theta @ model.A)*model.bl
    r.update(provided_nodal_balance_MW=float(np.max(np.abs(theta@model.Bbus.T-injection))),
        provided_branch_excess_MW=pos(np.abs(flows)-model.rate),
        angle_bound_rad=pos(np.abs(theta)-np.pi),
        slack_angle_rad=float(np.max(np.abs(theta[:,model.slack]))))
    energy = sum((Fraction.from_float(float(v)) for v in p[:,fossil].ravel()), Fraction(0))
    return {"pass": bool(all(v <= TOL for v in r.values()) and network["pass"]),
        "tolerance": TOL, "residuals": r, "dispatch_reconstructed_network": network,
        "residence_violations": violations, "fossil_energy_MWh": float(energy),
        "exact_binary64_fossil_energy_numerator": str(energy.numerator),
        "exact_binary64_fossil_energy_denominator": str(energy.denominator),
        "individual_mean_constraints": 0, "energy_cap_constraints": 0}


def assemble_reference(model, lo, hi, net, rows, fossil):
    matrix, bounds, integer, meta, labels, nodal = build(model,lo,hi,net,rows,0.,archive=None)
    keep = np.array([x["family"] != "fossil_energy_cap" for x in labels])
    assert (~keep).sum() == 1 and not any(x["family"] == "target_mean" for x in labels)
    matrix = matrix[keep].tocsr()
    bounds["row_lower"] = bounds["row_lower"][keep]
    bounds["row_upper"] = bounds["row_upper"][keep]
    labels = [dict(x,row=i) for i,x in enumerate(x for x,k in zip(labels,keep) if k)]
    assert not any(x["family"] in {"target_mean","fossil_energy_cap"} for x in labels)
    objective = np.zeros(matrix.shape[1])
    columns = [t*hi.shape[1]+j for t in range(len(hi)) for j in fossil]
    objective[columns] = 1.
    assert np.count_nonzero(objective) == 168*23
    assert meta.pop("budget_MWh") == 0.
    meta.update(rows=matrix.shape[0], nonzeros=matrix.nnz, energy_cap_constraints=0,
        individual_mean_constraints=0, removed_cap_rows=1,
        objective="minimize sum of 23 fossil-unit dispatch values times one hour; equal weights",
        objective_nonzero_columns=len(columns), explicit_ramp_rows=0,
        ramp_semantics="native on/on only; analytically redundant rows omitted and directly checked",
        initial_history="free mature initial status; Y[0]=Z[0]=0",
        terminal_history="residence enforced through hour 167 only; no cyclic closure or post-horizon constraint")
    return matrix,bounds,integer,objective,meta,labels,nodal


def finite(value):
    value = float(value)
    return value if np.isfinite(value) else None


def solve(model, month, directory, data, names, thermal_names, fossil):
    matrix,bounds,integer,objective,meta,labels,nodal,lo,hi,net,rows = data
    lp = highspy.HighsLp()
    lp.num_row_,lp.num_col_ = matrix.shape
    lp.col_cost_,lp.col_lower_,lp.col_upper_ = objective,bounds["column_lower"],bounds["column_upper"]
    lp.row_lower_,lp.row_upper_ = bounds["row_lower"],bounds["row_upper"]
    lp.integrality_ = [highspy.HighsVarType.kInteger if x else highspy.HighsVarType.kContinuous for x in integer]
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.num_row_,lp.a_matrix_.num_col_ = matrix.shape
    lp.a_matrix_.start_,lp.a_matrix_.index_,lp.a_matrix_.value_ = matrix.indptr,matrix.indices,matrix.data
    solver = highspy.Highs()
    options = {"time_limit":120.,"threads":1,"random_seed":0,"mip_rel_gap":1e-8,
        "log_to_console":False,"log_file":str(directory/"solver.log")}
    for key,value in options.items():
        assert solver.setOptionValue(key,value) == highspy.HighsStatus.kOk
    assert solver.passModel(lp) == highspy.HighsStatus.kOk
    start = time.perf_counter();run_status = solver.run();elapsed = time.perf_counter()-start
    status,solution,info = solver.getModelStatus(),solver.getSolution(),solver.getInfo()
    record = {"month":month,"model_status":solver.modelStatusToString(status),"run_status":str(run_status),
        "solver_version":solver.version(),"elapsed_s":elapsed,"solver_options":options,
        "presolve":"solver default","solution_value_valid":bool(solution.value_valid),
        "verdict":"UNKNOWN_NO_VERIFIED_REFERENCE","objective_MWh":finite(info.objective_function_value),
        "mip_dual_bound_MWh":finite(info.mip_dual_bound),"mip_relative_gap":finite(info.mip_gap),
        "mip_node_count":int(info.mip_node_count),"primal_solution_status":int(info.primal_solution_status),
        "max_primal_infeasibility":finite(info.max_primal_infeasibility),
        "numerical_optimality_claim":False,"optimization_calls":1}
    if solution.value_valid:
        vector = np.asarray(solution.col_value)
        np.savez_compressed(directory/"returned_vector.npz",vector=vector)
        p,u,y,z,theta = unpack(vector,168,41,24,24)
        matrix_check = check_vector(matrix,bounds,vector)
        check = physical_check(model,p,u,y,z,theta,lo,hi,net,rows,nodal,fossil)
        save(directory/"witness_verification.json",{"matrix":matrix_check,"physical":check})
        record["matrix_verification_pass"] = matrix_check["pass"]
        record["physical_verification_pass"] = check["pass"]
        for filename,values,columns in [("dispatch",p,names),("commitment",u,thermal_names),
            ("startup",y,thermal_names),("shutdown",z,thermal_names),("angles",theta,model.busids)]:
            pd.DataFrame(values,columns=columns).to_csv(directory/f"candidate_{filename}.csv",index=False)
        if matrix_check["pass"] and check["pass"]:
            record["verdict"] = "VERIFIED_BINARY_DC_NETWORK_REFERENCE"
            record["verified_fossil_energy_MWh"] = check["fossil_energy_MWh"]
            assert abs(float(objective@vector)-check["fossil_energy_MWh"]) <= 1e-6
            assert abs(info.objective_function_value-check["fossil_energy_MWh"]) <= 1e-5
            record["numerical_optimality_claim"] = bool(status == highspy.HighsModelStatus.kOptimal
                and np.isfinite(info.mip_gap) and info.mip_gap <= 1e-8
                and np.isfinite(info.mip_dual_bound))
    if status == highspy.HighsModelStatus.kInfeasible:
        assert record["verdict"] != "VERIFIED_BINARY_DC_NETWORK_REFERENCE"
        record["verdict"] = "NUMERICAL_MIP_INFEASIBLE_NOT_EXACT_CERTIFICATE"
    save(directory/"result.json",record)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-v3",type=Path,required=True)
    parser.add_argument("--output",type=Path,default=ROOT/"results/research8h/seasonal_reference")
    parser.add_argument("--verify-only",action="store_true")
    args = parser.parse_args()
    model = load_model(args.source_v3)
    thermal = model.dec.iloc[model.urows]
    fossil = [int(j) for j in model.urows if model.dec.iloc[j]["Fuel"] in {"Coal","Oil","NG"}]
    excluded = [model.dec.iloc[j]["GEN UID"] for j in model.urows if j not in fossil]
    assert len(fossil)==23 and excluded==["121_NUCLEAR_1"]
    assert len(model.busids)==24 and len(model.branches)==38 and len(model.dec)==41 and len(thermal)==24
    names,thermal_names = model.dec["GEN UID"].tolist(),thermal["GEN UID"].tolist()
    if args.verify_only:
        replay = []
        for month in MONTHS:
            directory = args.output/f"month_{month:02d}"
            with np.load(directory/"native_inputs.npz") as a:
                lo,hi,net,rows,nodal = [a[key] for key in ["pmin","pmax","net","rows","nodal"]]
            if not (directory/"returned_vector.npz").exists():
                replay.append({"month":month,"verdict":"NO_RETURNED_VECTOR"});continue
            with np.load(directory/"returned_vector.npz") as a:
                vector = a["vector"]
            with np.load(directory/"bounds.npz") as a:
                bounds = dict(a)
            check = physical_check(model,*unpack(vector,168,41,24,24),lo,hi,net,rows,nodal,fossil)
            replay.append({"month":month,"matrix":check_vector(load_npz(directory/"matrix.npz"),bounds,vector),"physical":check})
        save(args.output/"independent_archived_replay.json",replay)
        print(json.dumps([{"month":x["month"],"pass":x.get("physical",{}).get("pass")} for x in replay]),flush=True)
        return
    args.output.mkdir(parents=True,exist_ok=False)
    protocol = ROOT/"docs/research8h/SEASONAL_REFERENCE_PROTOCOL.md"
    save(args.output/"pre_run_freeze.json",{"utc":datetime.now(timezone.utc).isoformat(),"months":MONTHS,
        "script_sha256":sha(Path(__file__)),"protocol_sha256":sha(protocol),"bound_sources":BINDINGS,
        "seconds_per_case":120,"threads":1,"random_seed":0,"relative_gap_target":1e-8,"warm_start":False,
        "named_unit_mean_constraints":0,"energy_caps":0,"objective":"23 fossil-unit MWh; equal weights; nuclear excluded",
        "execution_context":"Shared host; another independent thread-one MIP may run concurrently; timings are not a benchmark."})
    inventory = model.dec[["GEN UID","Category","Fuel","PMin MW","PMax MW","Min Up Time Hr","Min Down Time Hr","Ramp Rate MW/Min"]].copy()
    inventory["thermal"] = model.thermal.to_numpy(bool)
    inventory["fossil_objective_coefficient"] = [int(j in fossil) for j in range(len(model.dec))]
    inventory.to_csv(args.output/"unit_inventory.csv",index=False)
    rate = thermal["Ramp Rate MW/Min"].to_numpy(float)*60
    variation = thermal["PMax MW"].to_numpy(float)-thermal["PMin MW"].to_numpy(float)
    assert np.all(rate>=variation)
    pd.DataFrame({"uid":thermal_names,"native_hourly_ramp_MW":rate,"maximum_on_on_change_MW":variation,
        "redundancy_margin_MW":rate-variation}).to_csv(args.output/"ramp_redundancy.csv",index=False)
    paths = [Path(__file__),protocol,*[ROOT/"src"/p for p in BINDINGS],args.source_v3/"code/dscgrid_model.py",
        *sorted((args.source_v3/"raw").rglob("*.csv"))]
    prepared = []
    for month in MONTHS:
        cols,unused,lo,hi,net,used = inputs(model,args.source_v3,month)
        assert cols == names
        table = pd.read_csv(used[1]);rows = table["row"].to_numpy(int)
        assert all(np.isfinite(a).all() for a in [lo,hi,net])
        assert np.all(lo[:,model.urows]==thermal["PMin MW"].to_numpy(float))
        assert np.all(hi[:,model.urows]==thermal["PMax MW"].to_numpy(float))
        matrix,bounds,integer,objective,meta,labels,nodal = assemble_reference(model,lo,hi,net,rows,fossil)
        directory = args.output/f"month_{month:02d}";directory.mkdir()
        save_npz(directory/"matrix.npz",matrix)
        np.savez_compressed(directory/"bounds.npz",**bounds)
        np.savez_compressed(directory/"integrality.npz",integrality=integer)
        np.savez_compressed(directory/"objective.npz",objective=objective)
        np.savez_compressed(directory/"native_inputs.npz",pmin=lo,pmax=hi,net=net,rows=rows,nodal=nodal)
        table[["row","timestamp"]].to_csv(directory/"source_hours.csv",index=False)
        save(directory/"model_metadata.json",meta)
        pd.DataFrame(labels).to_csv(directory/"row_metadata.csv.gz",index=False,compression="gzip")
        paths.extend(used)
        paths.extend(directory/p for p in ["matrix.npz","bounds.npz","integrality.npz","objective.npz","native_inputs.npz"])
        if month == 7:
            witness = ROOT/"results/v8/network_repair"
            pp,up = witness/"network_repair_dispatch.csv",witness/"network_fixed_commitment.csv"
            p,u = pd.read_csv(pp)[names].to_numpy(float),pd.read_csv(up)[thermal_names].to_numpy(float)
            y,z = np.zeros_like(u),np.zeros_like(u)
            y[1:],z[1:] = np.maximum(np.diff(u,axis=0),0),np.maximum(-np.diff(u,axis=0),0)
            theta = reconstruct_angles(model,p,nodal)
            check = physical_check(model,p,u,y,z,theta,lo,hi,net,rows,nodal,fossil)
            matrix_check = check_vector(matrix,bounds,np.concatenate([x.ravel() for x in [p,u,y,z,theta]]))
            assert check["pass"] and matrix_check["pass"]
            save(args.output/"existing_July_witness_preflight.json",{"physical":check,"matrix":matrix_check,"optimization":False})
            paths.extend([pp,up])
        prepared.append((month,directory,(matrix,bounds,integer,objective,meta,labels,nodal,lo,hi,net,rows)))
    manifest = [{"path":str(p),"sha256":sha(p),"bytes":p.stat().st_size} for p in dict.fromkeys(paths)]
    pd.DataFrame(manifest).to_csv(args.output/"input_manifest.csv",index=False)
    save(args.output/"all_models_frozen_before_first_solve.json",{"utc":datetime.now(timezone.utc).isoformat(),
        "manifest_sha256":sha(args.output/"input_manifest.csv"),"months":MONTHS,"no_mean_constraints":True,"no_cap_constraints":True})
    records = []
    for month,directory,data in prepared:
        result = solve(model,month,directory,data,names,thermal_names,fossil)
        records.append(result);save(args.output/"summary.json",records)
        print(json.dumps({k:result[k] for k in ["month","model_status","verdict","elapsed_s","objective_MWh","mip_dual_bound_MWh","mip_relative_gap"]}),flush=True)
    assert all(sha(Path(x["path"]))==x["sha256"] for x in manifest)
    pd.DataFrame([{k:v for k,v in x.items() if not isinstance(v,(list,dict))} for x in records]).to_csv(args.output/"summary.csv",index=False)
    save(args.output/"completion.json",{"utc":datetime.now(timezone.utc).isoformat(),"source_and_model_hashes_unchanged":True,
        "optimization_calls":4,"verified_references":sum(x["verdict"]=="VERIFIED_BINARY_DC_NETWORK_REFERENCE" for x in records)})


if __name__ == "__main__":
    main()
