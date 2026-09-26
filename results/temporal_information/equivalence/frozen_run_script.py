"""Fixed weekly-energy pooling diagnostic; see TEMPORAL_EQUIVALENCE_PROTOCOL.md."""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

import highspy
import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix

sys.dont_write_bytecode = True  # Portable source input directory is read-only.
ROOT = Path(__file__).resolve().parents[1]
MONTHS = [1, 2, 3, 4, 5, 6, 7, 10]
TOL = 1e-5
IDENTITY_COLUMNS = {"GEN UID", "Gen ID"}
PROTOCOL = ROOT / "docs/TEMPORAL_EQUIVALENCE_PROTOCOL.md"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False), encoding="utf-8")


def load_model(source):
    path = source / "code/dscgrid_model.py"
    spec = importlib.util.spec_from_file_location("equivalence_native_rts", path)
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    return model


def full_year_profile(model, row):
    uid, category = row["GEN UID"], row["Category"]
    length = len(model.load_ts)
    lo = np.full(length, float(row["PMin MW"]))
    hi = np.full(length, float(row["PMax MW"]))
    if category == "Hydro":
        lo = hi = model.hydro_ts[uid].to_numpy(float)
    elif category == "Solar PV":
        lo = np.zeros(length)
        hi = model.pv_ts[uid].to_numpy(float)
    elif category == "Wind":
        lo = np.zeros(length)
        hi = model.wind_ts[uid].to_numpy(float)
    assert len(lo) == len(hi) == length and np.isfinite(lo).all() and np.isfinite(hi).all()
    payload = np.asarray([lo, hi], dtype="<f8").tobytes()
    return hashlib.sha256(payload).hexdigest()


def make_groups(model, source):
    raw_path = source / "raw/RTS-GMLC_v0.2.3/gen.csv"
    with raw_path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        raw_columns = reader.fieldnames
        raw = {row["GEN UID"]: row for row in reader}
    retained = [name for name in raw_columns if name not in IDENTITY_COLUMNS]
    assert len(raw_columns) == 57 and len(retained) == 55
    by_signature, groups, members = {}, [], []
    fp = pd.to_numeric(model.dec["Fuel Price $/MMBTU"], errors="coerce").fillna(0).to_numpy(float)
    hr = pd.to_numeric(model.dec["HR_avg_0"], errors="coerce").fillna(0).to_numpy(float)
    vom = pd.to_numeric(model.dec["VOM"], errors="coerce").fillna(0).to_numpy(float)
    base_cost = fp * hr / 1000.0 + vom
    for index, row in model.dec.iterrows():
        uid = row["GEN UID"]
        values = {name: raw[uid][name] for name in retained}
        profile = full_year_profile(model, row)
        identity = {"source_attributes": values, "base_marginal_cost": float(base_cost[index]), "annual_bounds_sha256": profile}
        serialized = json.dumps(identity, sort_keys=True, separators=(",", ":"))
        signature = hashlib.sha256(serialized.encode()).hexdigest()
        if signature not in by_signature:
            group_id = f"G{len(groups)+1:03d}"
            by_signature[signature] = len(groups)
            unresolved = {name: value for name, value in values.items() if value.strip().lower() == "unit-specific"}
            missing = {name: value for name, value in values.items() if value.strip().lower() in {"", "na", "nan"}}
            groups.append({"group_id": group_id, "signature_sha256": signature, "members": [], "indices": [],
                "scope": "exact represented model/source-attribute equivalence; no empirical emissions claim",
                **identity, "unit_specific_placeholders": unresolved, "missing_source_values": missing,
                "emissions_equivalence_verified": False})
        group = groups[by_signature[signature]]
        group["members"].append(uid)
        group["indices"].append(int(index))
        members.append({"group_id": group["group_id"], "model_index": int(index), **raw[uid],
            "base_marginal_cost": float(base_cost[index]), "excluded_index_tie_break_cost": float(1e-7*index),
            "annual_bounds_sha256": profile, "signature_sha256": signature})
    for group in groups:
        group["size"] = len(group["members"])
        group["thermal"] = bool(model.thermal.iloc[group["indices"]].all())
        assert len(set(model.dec.iloc[group["indices"]]["Bus ID"])) == 1
    inventory = {"retained_source_columns": retained, "excluded_identity_columns": sorted(IDENTITY_COLUMNS),
        "excluded_derived_field": "author index tie breaker 1e-7*model_index; retained separately in member inventory",
        "units": len(model.dec), "groups": len(groups), "pooled_groups": sum(g["size"] > 1 for g in groups),
        "thermal_units": int(model.thermal.sum()), "thermal_groups": sum(g["thermal"] for g in groups),
        "source_cost_curve_fields_preserved": [c for c in retained if c.startswith(("Output_pct", "HR_"))],
        "emissions_fields_preserved": [c for c in retained if "Emissions" in c or "Sulfur" in c], "inventory": groups}
    return groups, members, inventory


def case_inputs(model, source, month):
    columns = model.dec["GEN UID"].tolist()
    target_path = ROOT / "reproducibility/data/processed/rts" / f"month_{month:02d}_first_week_dispatch.csv"
    public = pd.read_csv(target_path)
    prepared_path = source / "processed" / target_path.name
    prepared = pd.read_csv(prepared_path)
    assert np.array_equal(public[columns].to_numpy(float), prepared[columns].to_numpy(float))
    stamps = pd.to_datetime(public["timestamp"])
    assert len(public) == 168 and stamps.iloc[0] == pd.Timestamp(2020, month, 1)
    assert np.all(np.diff(stamps.to_numpy()) == np.timedelta64(1, "h"))
    keys = {tuple(map(int, entry)): i for i, entry in enumerate(model.load_ts[["Year", "Month", "Day", "Period"]].to_numpy())}
    pmin, pmax, demand, rows = [], [], [], []
    for stamp in stamps:
        row = keys[(stamp.year, stamp.month, stamp.day, stamp.hour + 1)]
        lo, hi = model.avail_at(row)
        pmin.append(lo)
        pmax.append(hi)
        demand.append(float(model.load_ts.loc[row, str(model.AREA)]) - model.rtpv_at(row).sum())
        rows.append(row)
    return {"month": month, "target": public[columns].to_numpy(float), "pmin": np.asarray(pmin),
        "pmax": np.asarray(pmax), "demand": np.asarray(demand), "timestamps": public["timestamp"].tolist(),
        "native_rows": rows, "target_path": target_path, "prepared_target_path": prepared_path}


def check_witness(model, case, groups, p, u, y, z):
    arrays = [p, u, y, z]
    if not all(np.isfinite(array).all() for array in arrays):
        return {"pass": False, "residuals": {"nonfinite": 1}}
    thermal = np.flatnonzero(model.thermal.to_numpy(bool))
    hydro = model.dec.Category.eq("Hydro").to_numpy()
    pmin, pmax, demand = case["pmin"], case["pmax"], case["demand"]
    ub, yb, zb = np.rint(u).astype(int), np.rint(y).astype(int), np.rint(z).astype(int)
    differences = np.diff(ub, axis=0)
    up = np.ceil(model.dec.iloc[thermal]["Min Up Time Hr"].to_numpy(float)).astype(int)
    down = np.ceil(model.dec.iloc[thermal]["Min Down Time Hr"].to_numpy(float)).astype(int)
    ramp = 60 * model.dec.iloc[thermal]["Ramp Rate MW/Min"].to_numpy(float)
    group_errors = [float(p[:, group["indices"]].sum(axis=1).mean() - case["target"][:, group["indices"]].sum(axis=1).mean()) for group in groups]
    residuals = {
        "negative_dispatch_MW": float(max(0., -p.min())),
        "availability_MW": float(max(0., (p-pmax).max())),
        "balance_MW": float(np.abs(p.sum(axis=1)-demand).max()),
        "fixed_hydro_MW": float(np.abs(p[:, hydro]-pmin[:, hydro]).max()),
        "group_mean_MW": float(np.abs(group_errors).max()),
        "binary_integer_distance": float(max(np.abs(u-ub).max(), np.abs(y-yb).max(), np.abs(z-zb).max())),
        "binary_lower": float(max(0., -u.min(), -y.min(), -z.min())),
        "binary_upper": float(max(0., (u-1).max(), (y-1).max(), (z-1).max())),
        "rounded_commit_lower_MW": float(max(0., (pmin[:, thermal]*ub-p[:, thermal]).max())),
        "rounded_commit_upper_MW": float(max(0., (p[:, thermal]-pmax[:, thermal]*ub).max())),
        "transition_identity": float(np.abs(differences-yb[1:]+zb[1:]).max()),
        "simultaneous_transition": float(max(0., (yb+zb-1).max())),
        "initial_transition": float(max(np.abs(yb[0]).max(), np.abs(zb[0]).max())),
    }
    violations = 0
    for q in range(len(thermal)):
        for t in range(1, len(p)):
            if differences[t-1, q] == 1:
                violations += int(np.any(ub[t:min(len(p), t+up[q]), q] != 1))
            elif differences[t-1, q] == -1:
                violations += int(np.any(ub[t:min(len(p), t+down[q]), q] != 0))
    residuals["direct_residence_violations"] = violations
    on_on = (ub[1:] == 1) & (ub[:-1] == 1)
    residuals["redundant_on_on_ramp_MW"] = float(max(0., np.where(on_on, np.abs(np.diff(p[:, thermal], axis=0))-ramp, 0).max()))
    return {"pass": all(value <= TOL for value in residuals.values()), "tolerance": TOL,
        "group_mean_tolerance_MW": TOL, "group_energy_tolerance_MWh": 168*TOL, "residuals": residuals,
        "individual_mean_drift_max_MW": float(np.abs(p.mean(axis=0)-case["target"].mean(axis=0)).max()),
        "individual_means_are_acceptance_constraints": False,
        "group_mean_residuals_MW": {g["group_id"]: error for g, error in zip(groups, group_errors)}}


def solve_grouped(model, case, groups, output, seconds):
    target, pmin, pmax, demand = case["target"], case["pmin"], case["pmax"], case["demand"]
    h, ng = target.shape
    ti = np.flatnonzero(model.thermal.to_numpy(bool))
    k = len(ti)
    npv, nu = h*ng, h*k
    iu, iy, iz = npv, npv+nu, npv+2*nu
    n = npv+3*nu
    lower, upper = np.zeros(n), np.r_[pmax.ravel(), np.ones(3*nu)]
    for j in np.flatnonzero(model.dec.Category.eq("Hydro").to_numpy()):
        lower[np.arange(h)*ng+j] = pmin[:, j]
    upper[iy:iy+k] = 0
    upper[iz:iz+k] = 0
    pcol = lambda t, j: t*ng+j
    ucol = lambda t, q: iu+t*k+q
    ycol = lambda t, q: iy+t*k+q
    zcol = lambda t, q: iz+t*k+q
    ri, ci, val, lo, hi = [], [], [], [], []
    def add(terms, minimum=-np.inf, maximum=np.inf):
        r = len(lo)
        for column, coefficient in terms.items():
            ri.append(r); ci.append(column); val.append(coefficient)
        lo.append(minimum); hi.append(maximum)
    up = np.ceil(model.dec.iloc[ti]["Min Up Time Hr"].to_numpy(float)).astype(int)
    down = np.ceil(model.dec.iloc[ti]["Min Down Time Hr"].to_numpy(float)).astype(int)
    for t in range(h):
        add({pcol(t,j): 1. for j in range(ng)}, demand[t], demand[t])
        for q, j in enumerate(ti):
            add({pcol(t,j): 1., ucol(t,q): -pmax[t,j]}, maximum=0.)
            add({pcol(t,j): -1., ucol(t,q): pmin[t,j]}, maximum=0.)
            if t == 0:
                continue
            add({ucol(t,q):1., ucol(t-1,q):-1., ycol(t,q):-1., zcol(t,q):1.}, 0., 0.)
            add({ycol(t,q):1., zcol(t,q):1.}, maximum=1.)
            terms = {ycol(s,q):1. for s in range(max(1,t-int(up[q])+1),t+1)}
            terms[ucol(t,q)] = -1.
            add(terms, maximum=0.)
            terms = {zcol(s,q):1. for s in range(max(1,t-int(down[q])+1),t+1)}
            terms[ucol(t,q)] = 1.
            add(terms, maximum=1.)
    for group in groups:
        mean = float(target[:, group["indices"]].sum(axis=1).mean())
        add({pcol(t,j):1./h for t in range(h) for j in group["indices"]}, mean, mean)
    matrix = coo_matrix((val,(ri,ci)), shape=(len(lo),n)).tocsr()
    lp = highspy.HighsLp()
    lp.num_col_, lp.num_row_ = n, len(lo)
    lp.col_cost_, lp.col_lower_, lp.col_upper_ = np.zeros(n), lower, upper
    lp.row_lower_, lp.row_upper_ = np.asarray(lo), np.asarray(hi)
    lp.integrality_ = [highspy.HighsVarType.kContinuous]*npv+[highspy.HighsVarType.kInteger]*(3*nu)
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.num_col_, lp.a_matrix_.num_row_ = n, len(lo)
    lp.a_matrix_.start_, lp.a_matrix_.index_, lp.a_matrix_.value_ = matrix.indptr, matrix.indices, matrix.data
    solver = highspy.Highs()
    stem = f"month_{case['month']:02d}_grouped_minud"
    for key, value in (("time_limit",float(seconds)),("threads",1),("random_seed",0),("mip_rel_gap",1e-8),("log_to_console",False),("log_file",str(output/(stem+".log")))):
        solver.setOptionValue(key,value)
    solver.passModel(lp)
    start = time.monotonic()
    solver.run()
    elapsed = time.monotonic()-start
    status, info, solution = solver.getModelStatus(), solver.getInfo(), solver.getSolution()
    record = {"month":case["month"], "family":"grouped_weekly_energy_minud", "verdict":"UNRESOLVED",
        "model_status":solver.modelStatusToString(status), "elapsed_s":elapsed, "time_limit_s":seconds,
        "solver_version":solver.version(), "threads":1, "random_seed":0, "rows":len(lo), "columns":n,
        "energy_coordinates":len(groups), "dispatch_coordinates":ng, "thermal_commitment_coordinates":k,
        "max_primal_infeasibility":float(info.max_primal_infeasibility) if np.isfinite(info.max_primal_infeasibility) else None}
    if solution.value_valid:
        x = np.asarray(solution.col_value)
        p = x[:npv].reshape(h,ng)
        u, y, z = [x[start:start+nu].reshape(h,k) for start in (iu,iy,iz)]
        check = check_witness(model,case,groups,p,u,y,z)
        record["witness_verification"] = check
        if check["pass"]:
            names = model.dec["GEN UID"].tolist()
            thermal_names = model.dec.iloc[ti]["GEN UID"].tolist()
            for suffix, values, columns in (("dispatch",p,names),("commitment",u,thermal_names),("startup",y,thermal_names),("shutdown",z,thermal_names)):
                frame = pd.DataFrame(values,columns=columns)
                frame.insert(0,"timestamp",case["timestamps"])
                frame.to_csv(output/(stem+"_"+suffix+".csv"),index=False)
            reread = [pd.read_csv(output/(stem+"_"+suffix+".csv"))[columns].to_numpy(float)
                for suffix, columns in (("dispatch",names),("commitment",thermal_names),("startup",thermal_names),("shutdown",thermal_names))]
            serialized = check_witness(model,case,groups,*reread)
            record["serialized_witness_verification"] = serialized
            if serialized["pass"]:
                record["verdict"] = "ADMITTED_GROUPED_RELAXATION"
                pd.DataFrame({"uid":names,"original_mean_MW":target.mean(axis=0),"witness_mean_MW":reread[0].mean(axis=0),
                    "mean_drift_MW":reread[0].mean(axis=0)-target.mean(axis=0)}).to_csv(output/(stem+"_individual_mean_drift.csv"),index=False)
    if status == highspy.HighsModelStatus.kInfeasible:
        assert record["verdict"] != "ADMITTED_GROUPED_RELAXATION"
        record["verdict"] = "REJECTED_GROUPED_RELAXATION"
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-v3",type=Path,required=True)
    parser.add_argument("--output",type=Path,default=ROOT/"results/temporal_information/equivalence")
    parser.add_argument("--seconds",type=float,default=60.)
    args = parser.parse_args()
    if args.seconds != 60.:
        raise ValueError("The frozen protocol specifies exactly60 seconds percase.")
    if (args.output/"results.json").exists():
        raise FileExistsError("Existing results are preserved; select a new output directory for a separate declared run.")
    args.output.mkdir(parents=True,exist_ok=True)
    model = load_model(args.source_v3)
    groups, members, inventory = make_groups(model,args.source_v3)
    write_json(args.output/"group_inventory.json",inventory)
    pd.DataFrame(members).to_csv(args.output/"group_members.csv",index=False)
    comparison_path = ROOT/"results/v8r1/rts_seasonal/results.json"
    previous = {r["month"]:r for r in json.loads(comparison_path.read_text()) if r["family"]=="minud"}
    assert set(previous)==set(MONTHS)
    cases = [case_inputs(model,args.source_v3,month) for month in MONTHS]
    for case in cases:
        for group in groups:
            js=group["indices"]
            assert np.all(case["pmin"][:,js]==case["pmin"][:,js[0],None])
            assert np.all(case["pmax"][:,js]==case["pmax"][:,js[0],None])
    targets = [{"month":c["month"],"group_id":g["group_id"],"members":";".join(g["members"]),"size":g["size"],
        "pooled_target_mean_MW":float(c["target"][:,g["indices"]].sum(axis=1).mean()),
        "pooled_target_energy_MWh":float(c["target"][:,g["indices"]].sum())} for c in cases for g in groups]
    pd.DataFrame(targets).to_csv(args.output/"monthly_group_targets.csv",index=False)
    paths = [Path(__file__),PROTOCOL,comparison_path,args.source_v3/"code/dscgrid_model.py",
        *sorted((args.source_v3/"raw").rglob("*.csv")),*[c["target_path"] for c in cases],*[c["prepared_target_path"] for c in cases]]
    manifest=[{"path":str(p),"bytes":p.stat().st_size,"sha256":digest(p)} for p in dict.fromkeys(paths)]
    pd.DataFrame(manifest).to_csv(args.output/"input_manifest.csv",index=False)
    freeze={"frozen_before_grouped_solves_utc":datetime.now(timezone.utc).isoformat(),"protocol_sha256":digest(PROTOCOL),
        "script_sha256":digest(Path(__file__)),"groups":len(groups),"units":len(model.dec),"months":MONTHS,
        "seconds_per_case":60,"group_inventory_sha256":digest(args.output/"group_inventory.json"),
        "source_upstream_commit":"3ece0d3725c844056132393ee252b3083dd4eab4",
        "grouping_scope":"represented model equality; no assertion of actual unit-specific emissions equality"}
    write_json(args.output/"pre_run_freeze.json",freeze)
    print(json.dumps({"frozen":True,"groups":len(groups),"pooled_groups":inventory["pooled_groups"],"thermal_groups":inventory["thermal_groups"]}),flush=True)
    results=[]
    for case in cases:
        record=solve_grouped(model,case,groups,args.output,args.seconds)
        record["individual_published_verdict"]=previous[case["month"]]["verdict"]
        record["individual_published_status"]=previous[case["month"]]["model_status"]
        record["individual_baseline_source_sha256"]=digest(comparison_path)
        results.append(record)
        write_json(args.output/"results.json",results)
        pd.DataFrame([{k:v for k,v in item.items() if k not in {"witness_verification","serialized_witness_verification"}} for item in results]).to_csv(args.output/"summary.csv",index=False)
        print(json.dumps({key:record[key] for key in ("month","model_status","verdict","elapsed_s","individual_published_verdict")}),flush=True)


if __name__=="__main__":
    main()
