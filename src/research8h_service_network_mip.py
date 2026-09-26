"""Four frozen full-DC-network service MIPs; no named generator targets."""
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
from scipy.sparse import csr_matrix, hstack, load_npz, save_npz, vstack

from research8h_service_network import assemble as assemble_network, reconstruct_angles
from temporal_information_pilot import nodal_check
from temporal_lp_certificate import assemble as assemble_units, check_vector, digest, save
from v8r1_rts_seasonal import inputs, load_model

ROOT = Path(__file__).resolve().parents[1]
CASES = [f"seed_{seed}" for seed in range(26092600, 26092604)]
TOL = 1e-5
SECONDS = 120


def build(model, pmin, pmax, net, rows, budget, archive=None):
    unit, ub, um, ul = assemble_units(model, pmin, pmax, net, np.zeros(pmax.shape[1]))
    keep = np.array([label["family"] != "target_mean" for label in ul])
    assert (~keep).sum() == 41
    network, nb, _, nm, nl, nodal = assemble_network(model, pmin, pmax, rows, budget)
    npower, nunit, nangle = pmax.size, unit.shape[1], len(pmax) * len(model.busids)
    unit_cap = hstack([network[-1, :npower], csr_matrix((1, nunit-npower))], format="csr")
    unit = vstack([unit[keep], unit_cap], format="csr")
    ub["row_lower"] = np.r_[ub["row_lower"][keep], -np.inf]
    ub["row_upper"] = np.r_[ub["row_upper"][keep], budget]
    if archive is not None:
        archived = load_npz(archive / "matrix.npz")
        assert unit.shape == archived.shape and (unit != archived).nnz == 0
        with np.load(archive / "bounds.npz") as old:
            assert all(np.array_equal(ub[key], old[key]) for key in ub)
    labels = [label.copy() for label, selected in zip(ul, keep) if selected]
    labels.append({"family": "fossil_energy_cap", "hour_0based": -1, "uid": "23_fossil_units"})
    matrix = vstack([
        hstack([unit, csr_matrix((unit.shape[0], nangle))]),
        hstack([network[:-1, :npower], csr_matrix((network.shape[0]-1, nunit-npower)), network[:-1, npower:]])
    ], format="csr")
    bounds = {"column_lower": np.r_[ub["column_lower"], nb["column_lower"][npower:]],
              "column_upper": np.r_[ub["column_upper"], nb["column_upper"][npower:]],
              "row_lower": np.r_[ub["row_lower"], nb["row_lower"][:-1]],
              "row_upper": np.r_[ub["row_upper"], nb["row_upper"][:-1]]}
    labels.extend({"family": x["family"], "hour_0based": x["hour_0based"], "uid": x["name"]} for x in nl[:-1])
    for i, label in enumerate(labels):
        label["row"] = i
    integrality = np.r_[np.zeros(npower, dtype=np.uint8), np.ones(nunit-npower, dtype=np.uint8), np.zeros(nangle, dtype=np.uint8)]
    metadata = {**um, "rows": matrix.shape[0], "columns": matrix.shape[1], "nonzeros": matrix.nnz,
                "offsets": {**um["offsets"], "theta": nunit}, "buses": len(model.busids),
                "branches": len(model.branches), "bus_ids": model.busids,
                "budget_MWh": budget, "fossil_units": nm["fossil_units"], "individual_mean_constraints": 0,
                "binary_columns": int(integrality.sum()), "objective": "zero feasibility objective",
                "unit_matrix_exactly_matches_service_archive": archive is not None,
                "column_order": "P,U,Y,Z,theta; each block hour-major"}
    return matrix, bounds, integrality, metadata, labels, nodal


def unpack(vector, h, ng, nk, nb):
    npower, ns = h*ng, h*nk
    return (vector[:npower].reshape(h, ng), vector[npower:npower+ns].reshape(h, nk),
            vector[npower+ns:npower+2*ns].reshape(h, nk), vector[npower+2*ns:npower+3*ns].reshape(h, nk),
            vector[npower+3*ns:].reshape(h, nb))


def direct_check(model, p, u, y, z, theta, pmin, pmax, net, rows, nodal, fossil, budget):
    """Check native physical rules directly, with no mean-target argument."""
    arrays = [p, u, y, z, theta, pmin, pmax, net, nodal]
    if not all(np.all(np.isfinite(a)) for a in arrays):
        return {"pass": False, "reason": "nonfinite value"}
    ti = np.asarray(model.urows)
    hydro = model.dec.Category.eq("Hydro").to_numpy()
    ub = np.rint(u).astype(int)
    negative = lambda a: max(0., float(np.max(a)))
    residuals = {
        "negative_dispatch_MW": negative(-p), "availability_MW": negative(p-pmax),
        "balance_MW": float(np.max(np.abs(p.sum(1)-net))),
        "hydro_fixed_MW": float(np.max(np.abs(p[:, hydro]-pmin[:, hydro]))),
        "binary_UYZ": max(float(np.max(np.abs(a-np.rint(a)))) for a in (u,y,z)),
        "state_lower": max(negative(-a) for a in (u,y,z)),
        "state_upper": max(negative(a-1) for a in (u,y,z)),
        "raw_commitment_upper_MW": negative(p[:,ti]-pmax[:,ti]*u),
        "raw_commitment_lower_MW": negative(pmin[:,ti]*u-p[:,ti]),
        "rounded_commitment_upper_MW": negative(p[:,ti]-pmax[:,ti]*ub),
        "rounded_commitment_lower_MW": negative(pmin[:,ti]*ub-p[:,ti]),
        "transition_identity": float(np.max(np.abs(np.diff(u,axis=0)-y[1:]+z[1:]))),
        "exclusive_transition": negative(y+z-1),
        "initial_transition": max(float(np.max(np.abs(y[0]))),float(np.max(np.abs(z[0])))),
        "startup_matches_observed": float(np.max(np.abs(y[1:]-np.maximum(np.diff(ub,axis=0),0)))),
        "shutdown_matches_observed": float(np.max(np.abs(z[1:]-np.maximum(-np.diff(ub,axis=0),0))))}
    thermal = model.dec.iloc[ti]
    up = np.ceil(thermal["Min Up Time Hr"].to_numpy(float)).astype(int)
    down = np.ceil(thermal["Min Down Time Hr"].to_numpy(float)).astype(int)
    violations = []
    for q in range(len(ti)):
        for t in range(1,len(p)):
            change = ub[t,q]-ub[t-1,q]
            if change and np.any(ub[t:min(len(p), t+(up[q] if change>0 else down[q])),q] != ub[t,q]):
                violations.append({"thermal_index": q, "hour_0based": t})
    residuals["observed_residence_violations"] = len(violations)
    online = (ub[1:]==1) & (ub[:-1]==1)
    rate = thermal["Ramp Rate MW/Min"].to_numpy(float)*60
    residuals["native_on_on_ramp_MW"] = negative(np.where(online, np.abs(np.diff(p[:,ti],axis=0))-rate, 0.))
    reconstructed, _ = nodal_check(model, p, rows)
    max_nodal = max_line = 0.
    for power, angles, load in zip(p,theta,nodal):
        injection = -load.copy()
        for j, generator in model.dec.iterrows():
            injection[model.bi[int(generator["Bus ID"])]] += power[j]
        max_nodal = max(max_nodal, float(np.max(np.abs(model.Bbus@angles-injection))))
        max_line = max(max_line, negative(np.abs(model.bl*(model.A.T@angles))-model.rate))
    residuals.update(provided_nodal_balance_MW=max_nodal, provided_branch_excess_MW=max_line,
        angle_bound_rad=negative(np.abs(theta)-np.pi), slack_angle_rad=float(np.max(np.abs(theta[:,model.slack]))))
    energy = sum((Fraction.from_float(float(v)) for v in p[:,fossil].ravel()), Fraction(0))
    excess = max(Fraction(0), energy-Fraction.from_float(budget))
    residuals["fossil_cap_excess_MWh"] = float(excess)
    return {"pass": bool(all(v<=TOL for v in residuals.values()) and reconstructed["pass"]),
        "tolerance": TOL, "residuals": residuals, "dispatch_reconstructed_network": reconstructed,
        "residence_violations": violations, "fossil_energy_MWh": float(energy), "budget_MWh": budget,
        "exact_binary64_fossil_energy_numerator": str(energy.numerator),
        "exact_binary64_fossil_energy_denominator": str(energy.denominator),
        "exact_binary64_fossil_cap_excess_numerator": str(excess.numerator),
        "exact_binary64_fossil_cap_excess_denominator": str(excess.denominator),
        "individual_mean_target": "none; no mean equality used in verification"}


def run_case(model, case, directory, data, reference_means, names, thermal_names):
    matrix, bounds, integrality, metadata, _, nodal, pmin, pmax, net, rows = data
    lp = highspy.HighsLp()
    lp.num_row_, lp.num_col_ = matrix.shape
    lp.col_cost_ = np.zeros(matrix.shape[1])
    lp.col_lower_, lp.col_upper_ = bounds["column_lower"], bounds["column_upper"]
    lp.row_lower_, lp.row_upper_ = bounds["row_lower"], bounds["row_upper"]
    lp.integrality_ = [highspy.HighsVarType.kInteger if v else highspy.HighsVarType.kContinuous for v in integrality]
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.num_row_, lp.a_matrix_.num_col_ = matrix.shape
    lp.a_matrix_.start_, lp.a_matrix_.index_, lp.a_matrix_.value_ = matrix.indptr, matrix.indices, matrix.data
    solver = highspy.Highs()
    for option,value in [("time_limit",float(SECONDS)),("threads",1),("random_seed",0),("mip_rel_gap",1e-8),
                          ("presolve","on"),("log_to_console",False),("log_file",str(directory/"solver.log"))]:
        assert solver.setOptionValue(option,value) == highspy.HighsStatus.kOk
    assert solver.passModel(lp) == highspy.HighsStatus.kOk
    started = time.perf_counter(); solver.run(); elapsed = time.perf_counter()-started
    status, solution, info = solver.getModelStatus(), solver.getSolution(), solver.getInfo()
    record = {"case":case,"model_status":solver.modelStatusToString(status),"solver_version":solver.version(),
        "elapsed_s":elapsed,"time_limit_s":SECONDS,"verdict":"UNKNOWN","optimization_calls":1,
        "mip_node_count":int(info.mip_node_count),"matrix_sha256":digest(directory/"matrix.npz"),
        "bounds_sha256":digest(directory/"bounds.npz"),"integrality_sha256":digest(directory/"integrality.npz")}
    if solution.value_valid:
        vector = np.asarray(solution.col_value)
        np.savez_compressed(directory/"returned_vector.npz",vector=vector)
        record["matrix_vector_check"] = check_vector(matrix,bounds,vector)
        p,u,y,z,theta = unpack(vector,len(pmax),len(names),len(thermal_names),len(model.busids))
        fossil = [names.index(uid) for uid in metadata["fossil_units"]]
        check = direct_check(model,p,u,y,z,theta,pmin,pmax,net,rows,nodal,fossil,metadata["budget_MWh"])
        save(directory/"witness_verification.json",check)
        record["physical_verification_pass"] = check["pass"]
        if record["matrix_vector_check"]["pass"] and check["pass"]:
            record["verdict"] = "ADMITTED_BINARY_DC_NETWORK_SERVICE"
            for filename,values,columns in [("dispatch",p,names),("commitment",u,thermal_names),
                ("startup",y,thermal_names),("shutdown",z,thermal_names),("angles",theta,model.busids)]:
                pd.DataFrame(values,columns=columns).to_csv(directory/f"{filename}.csv",index=False)
            means = p.mean(0)
            pd.DataFrame({"uid":names,"reference_mean_MW":reference_means,"witness_mean_MW":means,
                "change_MW":means-reference_means}).to_csv(directory/"descriptive_mean_changes.csv",index=False)
            record["descriptive_mean_L1_change_MW"] = float(np.abs(means-reference_means).sum())
    if status == highspy.HighsModelStatus.kInfeasible:
        assert record["verdict"] != "ADMITTED_BINARY_DC_NETWORK_SERVICE"
        record["verdict"] = "NUMERICAL_MIP_INFEASIBLE_NOT_EXACT_CERTIFICATE"
    save(directory/"result.json",record)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-v3",type=Path,required=True)
    args = parser.parse_args()
    output = ROOT/"results/research8h/service_network_mip"
    output.mkdir(parents=True,exist_ok=False)
    protocol = ROOT/"docs/research8h/SERVICE_NETWORK_MIP_PROTOCOL.md"
    budget_path = ROOT/"results/research8h/service_cap/pre_run_freeze.json"
    budget = json.loads(budget_path.read_text())["budget_MWh"]
    save(output/"pre_run_freeze.json",{"frozen_at_utc":datetime.now(timezone.utc).isoformat(),
        "script_sha256":digest(Path(__file__)),"protocol_sha256":digest(protocol),"source_budget_sha256":digest(budget_path),
        "cases":CASES,"seconds_per_case":SECONDS,"total_configured_solver_seconds":4*SECONDS,
        "threads":1,"random_seed":0,"presolve":"on","mip_rel_gap":1e-8,"budget_MWh":budget,
        "warm_start":False,"objective":"zero feasibility objective","individual_mean_constraints":0})
    model = load_model(args.source_v3)
    names,_,base_lo,base_hi,base_net,native_paths = inputs(model,args.source_v3,7)
    native_rows = pd.read_csv(native_paths[1])["row"].to_numpy(int)
    thermal = model.dec.iloc[model.urows]
    thermal_names = thermal["GEN UID"].tolist()
    rate = thermal["Ramp Rate MW/Min"].to_numpy(float)*60
    variation = thermal["PMax MW"].to_numpy(float)-thermal["PMin MW"].to_numpy(float)
    assert np.all(rate>=variation)
    assert np.all(base_lo[:,model.urows]==thermal["PMin MW"].to_numpy(float))
    assert np.all(base_hi[:,model.urows]==thermal["PMax MW"].to_numpy(float))
    pd.DataFrame({"uid":thermal_names,"hourly_ramp_MW":rate,"largest_on_on_change_MW":variation,
        "redundancy_margin_MW":rate-variation}).to_csv(output/"ramp_redundancy.csv",index=False)
    reference = ROOT/"results/v8/network_repair"
    pp,up = reference/"network_repair_dispatch.csv",reference/"network_fixed_commitment.csv"
    rp,ru = pd.read_csv(pp)[names].to_numpy(float),pd.read_csv(up)[thermal_names].to_numpy(float)
    ry,rz = np.zeros_like(ru),np.zeros_like(ru)
    ry[1:],rz[1:] = np.maximum(np.diff(ru,axis=0),0),np.maximum(-np.diff(ru,axis=0),0)
    identity = build(model,base_lo,base_hi,base_net,native_rows,budget,ROOT/"results/research8h/service_cap/identity")
    im,ib,_,ime,_,ino = identity
    rt = reconstruct_angles(model,rp,ino)
    ref_vector = np.concatenate([a.ravel() for a in (rp,ru,ry,rz,rt)])
    preflight = {"matrix":check_vector(im,ib,ref_vector),"physical":direct_check(model,rp,ru,ry,rz,rt,
        base_lo,base_hi,base_net,native_rows,ino,[names.index(s) for s in ime["fossil_units"]],budget),
        "meaning":"Original reference checked in the unfixed binary service model; no optimization."}
    save(output/"identity_reference_preflight.json",preflight)
    assert preflight["matrix"]["pass"] and preflight["physical"]["pass"],preflight
    paths = [Path(__file__),protocol,budget_path,pp,up,*native_paths,args.source_v3/"code/dscgrid_model.py",
        *sorted((args.source_v3/"raw").rglob("*.csv")),ROOT/"src/research8h_service_network.py",
        ROOT/"src/temporal_lp_certificate.py",ROOT/"src/temporal_information_pilot.py",ROOT/"src/v8r1_rts_seasonal.py"]
    for case in ["identity",*CASES]:
        paths.extend(ROOT/"results/research8h/service_cap"/case/name for name in ("matrix.npz","bounds.npz"))
    prepared = []
    for case in CASES:
        permutation = ROOT/"results/temporal_information/twins"/case/"permutation.csv"
        paths.append(permutation)
        table = pd.read_csv(permutation)
        order = table["source_hour_0based"].to_numpy(int)
        rows = table["source_native_row"].to_numpy(int)
        assert np.array_equal(table["new_hour_0based"],np.arange(168))
        assert sorted(order)==list(range(168)) and np.array_equal(rows,native_rows[order])
        lo,hi,net = [],[],[]
        for row in rows:
            low,high = model.avail_at(int(row)); lo.append(low); hi.append(high)
            net.append(float(model.load_ts.loc[int(row),str(model.AREA)])-model.rtpv_at(int(row)).sum())
        lo,hi,net = np.asarray(lo),np.asarray(hi),np.asarray(net)
        assert np.array_equal(lo,base_lo[order]) and np.array_equal(hi,base_hi[order]) and np.array_equal(net,base_net[order])
        archive = ROOT/"results/research8h/service_cap"/case
        matrix,bounds,integrality,metadata,labels,nodal = build(model,lo,hi,net,rows,budget,archive)
        assert np.array_equal(nodal,ino[order])
        directory = output/case; directory.mkdir()
        save_npz(directory/"matrix.npz",matrix)
        np.savez_compressed(directory/"bounds.npz",**bounds)
        np.savez_compressed(directory/"integrality.npz",integrality=integrality)
        np.savez_compressed(directory/"objective.npz",objective=np.zeros(matrix.shape[1]))
        np.savez_compressed(directory/"native_inputs.npz",pmin=lo,pmax=hi,net=net,nodal=nodal,rows=rows,source_hour=order)
        save(directory/"model_metadata.json",metadata)
        pd.DataFrame(labels).to_csv(directory/"row_metadata.csv.gz",index=False,compression="gzip")
        save(directory/"paired_preservation.json",{"source_permutation_sha256":digest(permutation),
            "permutation_bijection":True,"native_rows_exact":True,"pmin_pmax_net_exact_joint_reorder":True,
            "nodal_load_exact_joint_reorder":True,"same_service_budget_MWh":budget,
            "source_service_unit_matrix_exact_match":True,"independent_mean_constraints":0})
        paths.extend(directory/name for name in ("matrix.npz","bounds.npz","integrality.npz","objective.npz","native_inputs.npz"))
        prepared.append((case,directory,(matrix,bounds,integrality,metadata,labels,nodal,lo,hi,net,rows)))
    pd.DataFrame([{"path":str(p),"sha256":digest(p),"bytes":p.stat().st_size} for p in dict.fromkeys(paths)]).to_csv(output/"input_manifest.csv",index=False)
    save(output/"models_frozen_before_first_solve.json",{"frozen_at_utc":datetime.now(timezone.utc).isoformat(),
        "input_manifest_sha256":digest(output/"input_manifest.csv"),"identity_reference_preflight_pass":True,"cases":CASES})
    results = []
    for case,directory,data in prepared:
        result = run_case(model,case,directory,data,rp.mean(0),names,thermal_names)
        results.append(result); save(output/"summary.json",results)
        print(json.dumps({key:result[key] for key in ("case","model_status","verdict","elapsed_s")}),flush=True)
    pd.DataFrame([{k:v for k,v in r.items() if not isinstance(v,(dict,list))} for r in results]).to_csv(output/"summary.csv",index=False)


if __name__ == "__main__":
    main()
