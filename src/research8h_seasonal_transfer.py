"""Frozen January service-order twins, constructive controls, LP then MIP."""
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

from research8h_service_network import reconstruct_angles
from research8h_service_network_mip import build, direct_check, run_case, unpack
from temporal_lp_certificate import certificate_context, check_vector, digest, exact_ray_check, save
from v8r1_rts_seasonal import inputs, load_model

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT/"results/research8h/seasonal_reference"
OUTPUT = ROOT/"results/research8h/seasonal_transfer"
ORDINARY = [26093100, 26093101]
CONTROL = 26100100
SCHEDULE = {1:([26093100,26093101],26100100),4:([26093400,26093401],26100400),10:([26094000,26094001],26101000)}
TOL = 1e-5


def energy(p, fossil):
    return sum((Fraction.from_float(float(v)) for v in p[:,fossil].ravel()), Fraction(0))


def cap_record(p, fossil):
    e = energy(p,fossil)
    scaled = e*Fraction(101,100)
    budget = -(-scaled.numerator//scaled.denominator)
    headroom = Fraction(budget)-e
    return {"reference_energy_numerator":str(e.numerator),"reference_energy_denominator":str(e.denominator),
        "reference_energy_MWh":float(e),"budget_MWh":budget,"headroom_MWh":float(headroom),
        "headroom_numerator":str(headroom.numerator),"headroom_denominator":str(headroom.denominator),
        "relative_headroom":float(headroom/e) if e else None,"formula":"ceil(101*exact_binary64_fossil_sum/100)"}


def transitions(u):
    y,z = np.zeros_like(u),np.zeros_like(u)
    y[1:],z[1:] = np.maximum(np.diff(u,axis=0),0),np.maximum(-np.diff(u,axis=0),0)
    return y,z


def verify_manifest(path):
    table = pd.read_csv(path)
    for row in table.itertuples(index=False):
        p = Path(row.path)
        assert p.stat().st_size == row.bytes and digest(p) == row.sha256, str(p)
    return {"files":len(table),"all_hashes_and_sizes_pass":True,"manifest_sha256":digest(path)}


def archive_model(directory, data, native):
    matrix,bounds,integer,meta,labels,nodal = data
    directory.mkdir(parents=True,exist_ok=False)
    save_npz(directory/"matrix.npz",matrix)
    np.savez_compressed(directory/"bounds.npz",**bounds)
    np.savez_compressed(directory/"integrality.npz",integrality=integer)
    np.savez_compressed(directory/"objective.npz",objective=np.zeros(matrix.shape[1]))
    np.savez_compressed(directory/"native_inputs.npz",**native,nodal=nodal)
    save(directory/"model_metadata.json",meta)
    pd.DataFrame(labels).to_csv(directory/"row_metadata.csv.gz",index=False,compression="gzip")


def check_candidate(model, data, native, p, u, theta, fossil, budget):
    y,z = transitions(u)
    vector = np.concatenate([a.ravel() for a in (p,u,y,z,theta)])
    physical = direct_check(model,p,u,y,z,theta,native["pmin"],native["pmax"],native["net"],
        native["rows"],data[-1],fossil,budget)
    matrix = check_vector(data[0],data[1],vector)
    static_residuals = {k:v for k,v in physical["residuals"].items() if k != "observed_residence_violations"}
    static_pass = all(v<=TOL for v in static_residuals.values()) and physical["dispatch_reconstructed_network"]["pass"]
    return {"static_network_cap_pass":bool(static_pass),"binary_network_pass":bool(physical["pass"] and matrix["pass"]),
        "matrix":matrix,"physical":physical},vector


def save_witness(directory, vector, model):
    np.savez_compressed(directory/"constructive_vector.npz",vector=vector)
    arrays = unpack(vector,168,41,24,24)
    names = model.dec["GEN UID"].tolist(); thermal = model.dec.iloc[model.urows]["GEN UID"].tolist()
    for label,a,cols in zip(["dispatch","commitment","startup","shutdown","angles"],arrays,[names,thermal,thermal,thermal,model.busids]):
        pd.DataFrame(a,columns=cols).to_csv(directory/f"constructive_{label}.csv",index=False)


def solve_lp(matrix,bounds,integer,labels,directory):
    lp=highspy.HighsLp();lp.num_row_,lp.num_col_=matrix.shape
    lp.col_cost_=np.zeros(matrix.shape[1]);lp.col_lower_,lp.col_upper_=bounds["column_lower"],bounds["column_upper"]
    lp.row_lower_,lp.row_upper_=bounds["row_lower"],bounds["row_upper"]
    lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise
    lp.a_matrix_.num_row_,lp.a_matrix_.num_col_=matrix.shape
    lp.a_matrix_.start_,lp.a_matrix_.index_,lp.a_matrix_.value_=matrix.indptr,matrix.indices,matrix.data
    solver=highspy.Highs()
    for key,value in [("time_limit",30.),("threads",1),("random_seed",0),("solver","simplex"),
                      ("presolve","off"),("log_to_console",False),("log_file",str(directory/"solver.log"))]:
        assert solver.setOptionValue(key,value)==highspy.HighsStatus.kOk
    assert solver.passModel(lp)==highspy.HighsStatus.kOk
    started=time.perf_counter();solver.run();elapsed=time.perf_counter()-started
    status=solver.getModelStatus();solution=solver.getSolution()
    record={"model_status":solver.modelStatusToString(status),"elapsed_s":elapsed,"time_limit_s":30,
        "verdict":"UNKNOWN","solver_version":solver.version(),"presolve":"off","solver":"simplex"}
    if solution.value_valid:
        vector=np.asarray(solution.col_value)
        np.savez_compressed(directory/"returned_vector.npz",vector=vector)
        check=check_vector(matrix,bounds,vector);record["returned_vector_check"]=check
        if check["pass"]:
            np.savez_compressed(directory/"continuous_solution.npz",vector=vector)
            record["verdict"]="ADMITTED_CONTINUOUS_RELAXATION"
            record["fractional_state_coordinate_count"]=int(np.count_nonzero(np.abs(vector[integer.astype(bool)]-np.rint(vector[integer.astype(bool)]))>TOL))
    if status==highspy.HighsModelStatus.kInfeasible:
        assert record["verdict"]!="ADMITTED_CONTINUOUS_RELAXATION"
        ray_status,exists,ray=solver.getDualRay()
        record.update(dual_ray_status=str(ray_status),dual_ray_exists=bool(exists),verdict="SOLVER_INFEASIBLE_NO_VERIFIED_RAY")
        if exists:
            ray=np.asarray(ray);np.savez_compressed(directory/"raw_solver_ray.npz",multipliers=ray)
            candidates=[];checks=[]
            for orientation in (1,-1):
                raw=orientation*ray
                bad=((raw>0)&~np.isfinite(bounds["row_lower"]))|((raw<0)&~np.isfinite(bounds["row_upper"]))
                projected=raw.copy();projected[bad]=0.
                for name,candidate in [("raw",raw),("projected_to_row_sign_cone",projected)]:
                    check=exact_ray_check(matrix,bounds,candidate)
                    check.update(candidate=name,orientation=orientation,inadmissible_raw_entries=int(np.count_nonzero(bad)))
                    checks.append(check);candidates.append(candidate)
            record["candidate_checks"]=checks
            valid=[i for i,c in enumerate(checks) if c.get("pass") and c.get("robust_pass")]
            if valid:
                i=valid[0];chosen=candidates[i];check=checks[i]
                cert={"orientation":check["orientation"],"candidate":check["candidate"],"verification":check,
                    "multipliers":[{"row":int(j),"value_hex":float(chosen[j]).hex()} for j in np.flatnonzero(chosen)],
                    "row_metadata_sha256":digest(directory/"row_metadata.csv.gz"),
                    "experiment_manifest_sha256":digest(OUTPUT/"input_manifest.csv"),**certificate_context(directory,labels,chosen)}
                save(directory/"dual_certificate.json",cert)
                pd.DataFrame([{**labels[j],"multiplier":chosen[j]} for j in np.flatnonzero(chosen)]).to_csv(directory/"sparse_multipliers.csv",index=False)
                record.update(verdict="REJECTED_EXACT_BINARY64_CERTIFICATE",certificate_verification=check)
    return record


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-v3",type=Path,required=True)
    args=parser.parse_args()
    started=time.perf_counter()
    OUTPUT.mkdir(parents=True,exist_ok=False)
    protocol=ROOT/"docs/research8h/SEASONAL_TRANSFER_PROTOCOL.md"
    save(OUTPUT/"freeze_before_generation.json",{"utc":datetime.now(timezone.utc).isoformat(),
        "source_sha256":digest(Path(__file__)),"protocol_sha256":digest(protocol),"eligible_heldout_months":[1],
        "no_reference_months":[4,10],"schedule":SCHEDULE,"ordinary_lp_seconds":30,"conditional_mip_seconds":120,
        "phase_limit_seconds":1200,"minimum_seconds_to_start_mip":125,"cap_formula":"ceil(101*exact_stored_fossil_MWh/100)",
        "replication_gate_at_least_two_heldout_weeks":"unattainable in this eligible sample"})
    reference_audit=verify_manifest(REFERENCE/"input_manifest.csv")
    save(OUTPUT/"reference_manifest_check.json",reference_audit)
    reference_results={r["month"]:r for r in json.loads((REFERENCE/"summary.json").read_text())}
    assert reference_results[1]["verdict"]=="VERIFIED_BINARY_DC_NETWORK_REFERENCE"
    assert all(reference_results[m]["verdict"]=="UNKNOWN_NO_VERIFIED_REFERENCE" for m in (4,10))
    scheduled=[]
    for month,(seeds,control) in SCHEDULE.items():
        for seed in [*seeds,control]:
            scheduled.append({"month":month,"seed":seed,"kind":"ordinary" if seed in seeds else "positive_control",
                "status":"SCHEDULED" if month==1 else "NO_REFERENCE_NOT_RUN"})
    save(OUTPUT/"scheduled_cases.json",scheduled)
    model=load_model(args.source_v3)
    names=model.dec["GEN UID"].tolist(); thermal=model.dec.iloc[model.urows]["GEN UID"].tolist()
    fossil=[int(j) for j in model.urows if model.dec.iloc[j]["Fuel"] in {"Coal","Oil","NG"}]
    assert len(fossil)==23 and [names[j] for j in model.urows if j not in fossil]==["121_NUCLEAR_1"]
    rate=model.dec.iloc[model.urows]["Ramp Rate MW/Min"].to_numpy(float)*60
    variation=model.dec.iloc[model.urows]["PMax MW"].to_numpy(float)-model.dec.iloc[model.urows]["PMin MW"].to_numpy(float)
    assert np.all(rate>=variation)
    save(OUTPUT/"ramp_redundancy_check.json",{"all_24_pass":True,"minimum_margin_MW":float((rate-variation).min())})
    source_dir=REFERENCE/"month_01"
    with np.load(source_dir/"returned_vector.npz") as a: ref_vector=a["vector"].copy()
    rp,ru,ry,rz,rt=unpack(ref_vector,168,41,24,24)
    cap=cap_record(rp,fossil); budget=cap["budget_MWh"]
    save(OUTPUT/"january_cap.json",{**cap,"source_vector_sha256":digest(source_dir/"returned_vector.npz"),
        "reference_solver_record":reference_results[1],"fossil_units":[names[j] for j in fossil]})
    _,_,lo,hi,net,used=inputs(model,args.source_v3,1)
    rows=pd.read_csv(used[1])["row"].to_numpy(int)
    with np.load(source_dir/"native_inputs.npz") as a:
        assert all(np.array_equal(value,a[key]) for key,value in [("pmin",lo),("pmax",hi),("net",net),("rows",rows)])
    identity=build(model,lo,hi,net,rows,budget)
    labels=identity[4]; keep=np.array([x["family"]!="fossil_energy_cap" for x in labels])
    assert (identity[0][keep]!=load_npz(source_dir/"matrix.npz")).nnz==0
    with np.load(source_dir/"bounds.npz") as a:
        assert np.array_equal(identity[1]["column_lower"],a["column_lower"]) and np.array_equal(identity[1]["column_upper"],a["column_upper"])
        assert np.array_equal(identity[1]["row_lower"][keep],a["row_lower"]) and np.array_equal(identity[1]["row_upper"][keep],a["row_upper"])
    native={"pmin":lo,"pmax":hi,"net":net,"rows":rows,"source_hour":np.arange(168)}
    identity_dir=OUTPUT/"january_identity"; archive_model(identity_dir,identity,native)
    original_physical=direct_check(model,rp,ru,ry,rz,rt,lo,hi,net,rows,identity[-1],fossil,budget)
    original_matrix=check_vector(identity[0],identity[1],ref_vector)
    save(identity_dir/"raw_reference_check.json",{"physical":original_physical,"matrix":original_matrix})
    assert original_physical["pass"] and original_matrix["pass"]
    ub=np.rint(ru)
    check,vector=check_candidate(model,identity,native,rp,ub,rt,fossil,budget)
    save(identity_dir/"rounded_reference_check.json",check); save_witness(identity_dir,vector,model)
    assert check["binary_network_pass"]
    # July is an implementation check using the old positive network witness,
    # not a replacement for the missing newly optimized July reference.
    old=ROOT/"results/v8/network_repair"
    jp=pd.read_csv(old/"network_repair_dispatch.csv")[names].to_numpy(float)
    ju=pd.read_csv(old/"network_fixed_commitment.csv")[thermal].to_numpy(float)
    _,_,jl,jh,jn,jused=inputs(model,args.source_v3,7); jr=pd.read_csv(jused[1])["row"].to_numpy(int)
    jcap=cap_record(jp,fossil); july=build(model,jl,jh,jn,jr,jcap["budget_MWh"])
    jt=reconstruct_angles(model,jp,july[-1]); jnative={"pmin":jl,"pmax":jh,"net":jn,"rows":jr,"source_hour":np.arange(168)}
    jdir=OUTPUT/"july_implementation_identity"; archive_model(jdir,july,jnative)
    jc,jv=check_candidate(model,july,jnative,jp,ju,jt,fossil,jcap["budget_MWh"])
    save(jdir/"check.json",{**jc,"cap":jcap,"role":"old July implementation check; outside held-out sample"})
    assert jc["binary_network_pass"]
    prepared=[]
    for seed in [*ORDINARY,CONTROL]:
        rng=np.random.Generator(np.random.PCG64(seed)); order=np.arange(168)
        if seed in ORDINARY:
            order[48:120]=rng.permutation(np.arange(48,120))
        else:
            groups={}
            for t in range(48,120): groups.setdefault(tuple(int(v) for v in ub[t]),[]).append(t)
            for positions in groups.values(): order[positions]=rng.permutation(np.asarray(positions))
            assert np.array_equal(ub[order],ub)
        inverse=np.argsort(order)
        assert np.array_equal(order[inverse],np.arange(168)) and np.array_equal(order[:48],np.arange(48)) and np.array_equal(order[120:],np.arange(120,168))
        for a in (lo,hi,net,identity[-1],rp,ub,rt): assert np.array_equal(a[order][inverse],a)
        n={"pmin":lo[order],"pmax":hi[order],"net":net[order],"rows":rows[order],"source_hour":order}
        data=build(model,n["pmin"],n["pmax"],n["net"],n["rows"],budget)
        assert np.array_equal(data[-1],identity[-1][order])
        directory=OUTPUT/f"seed_{seed}"; archive_model(directory,data,n)
        pd.DataFrame({"new_hour_0based":np.arange(168),"source_hour_0based":order,"source_native_row":rows[order]}).to_csv(directory/"permutation.csv",index=False)
        cc,cv=check_candidate(model,data,n,rp[order],ub[order],rt[order],fossil,budget)
        save(directory/"constructive_check.json",cc); save_witness(directory,cv,model)
        assert cc["static_network_cap_pass"] and energy(rp[order],fossil)==energy(rp,fossil)
        if seed==CONTROL: assert cc["binary_network_pass"]
        save(directory/"preservation.json",{"permutation_bijection":True,"edges_fixed":True,"all_package_roundtrips_exact":True,
            "nodal_native_reconstruction_exact":True,"fossil_sum_exactly_preserved":True,"changed_hours":int(np.count_nonzero(order!=np.arange(168))),
            "commitment_sequence_unchanged":bool(np.array_equal(ub[order],ub)),"kind":"ordinary" if seed in ORDINARY else "positive_control"})
        if seed in ORDINARY:
            for phase in ("lp","mip"):
                sub=directory/phase; sub.mkdir()
                save_npz(sub/"matrix.npz",data[0]); np.savez_compressed(sub/"bounds.npz",**data[1])
                np.savez_compressed(sub/"integrality.npz",integrality=data[2])
                pd.DataFrame(data[4]).to_csv(sub/"row_metadata.csv.gz",index=False,compression="gzip")
            prepared.append((seed,directory,data,n))
    paths=[Path(__file__),protocol,ROOT/"docs/research8h/SEASONAL_TRANSFER_DESIGN.md",REFERENCE/"input_manifest.csv",REFERENCE/"summary.json",
        *[ROOT/"src"/x for x in ("research8h_service_network_mip.py","research8h_service_network.py","temporal_lp_certificate.py","temporal_information_pilot.py","v8r1_rts_seasonal.py")],
        old/"network_repair_dispatch.csv",old/"network_fixed_commitment.csv",args.source_v3/"code/dscgrid_model.py",*sorted((args.source_v3/"raw").rglob("*.csv")),*used,*jused,
        *sorted(source_dir.glob("*")),*sorted(p for p in OUTPUT.rglob("*") if p.is_file())]
    pd.DataFrame([{"path":str(p),"sha256":digest(p),"bytes":p.stat().st_size} for p in dict.fromkeys(paths)]).to_csv(OUTPUT/"input_manifest.csv",index=False)
    generation=time.perf_counter()-started
    save(OUTPUT/"models_frozen_before_first_solve.json",{"utc":datetime.now(timezone.utc).isoformat(),"input_manifest_sha256":digest(OUTPUT/"input_manifest.csv"),
        "january_budget_MWh":budget,"generation_and_preflight_seconds":generation,"all_controls_pass":True,"ordinary_seeds":ORDINARY,"control_seed":CONTROL})
    print(json.dumps({"event":"all_models_frozen","budget_MWh":budget,"all_controls_pass":True,"generation_s":generation}),flush=True)
    phase_start=time.perf_counter(); lp_results={}; outcomes=[]
    for seed,directory,data,n in prepared:
        matrix,bounds,integer,meta,labels,nodal=data
        rec=solve_lp(matrix,bounds,integer,labels,directory/"lp")
        if (directory/"lp/continuous_solution.npz").exists():
            with np.load(directory/"lp/continuous_solution.npz") as a: v=a["vector"]
            rec["fractional_state_coordinate_count"]=int(np.count_nonzero(np.abs(v[integer.astype(bool)]-np.rint(v[integer.astype(bool)]))>TOL))
        rec.update(seed=seed,matrix_sha256=digest(directory/"lp/matrix.npz"),bounds_sha256=digest(directory/"lp/bounds.npz"),
            row_metadata_sha256=digest(directory/"lp/row_metadata.csv.gz"),optimization_calls=1)
        save(directory/"lp/result.json",rec); lp_results[seed]=rec
        print(json.dumps({"stage":"LP","seed":seed,"verdict":rec["verdict"],"elapsed_s":rec["elapsed_s"]}),flush=True)
    for seed,directory,data,n in prepared:
        lp=lp_results[seed]
        if lp["verdict"]=="REJECTED_EXACT_BINARY64_CERTIFICATE":
            outcome={"seed":seed,"verdict":"CERTIFIED_INFEASIBLE","mip":"NOT_RUN_EXACT_LP_REJECTION"}
        elif 1200-(time.perf_counter()-phase_start)<125:
            outcome={"seed":seed,"verdict":"UNKNOWN","mip":"NOT_RUN_BUDGET"}
        else:
            matrix,bounds,integer,meta,labels,nodal=data
            payload=(matrix,bounds,integer,meta,labels,nodal,n["pmin"],n["pmax"],n["net"],n["rows"])
            mip=run_case(model,f"seed_{seed}",directory/"mip",payload,rp.mean(0),names,thermal)
            verdict={"ADMITTED_BINARY_DC_NETWORK_SERVICE":"VERIFIED_FEASIBLE","NUMERICAL_MIP_INFEASIBLE_NOT_EXACT_CERTIFICATE":"NUMERICAL_MIP_NEGATIVE"}.get(mip["verdict"],"LP_FEASIBLE_BINARY_UNKNOWN" if lp["verdict"]=="ADMITTED_CONTINUOUS_RELAXATION" else "UNKNOWN")
            outcome={"seed":seed,"verdict":verdict,"mip_verdict":mip["verdict"],"mip_elapsed_s":mip["elapsed_s"]}
            print(json.dumps({"stage":"MIP",**outcome}),flush=True)
        outcome.update(month=1,lp_verdict=lp["verdict"],lp_elapsed_s=lp["elapsed_s"],static_network_control_pass=True)
        outcomes.append(outcome);save(OUTPUT/"ordinary_outcomes.json",outcomes)
    save(OUTPUT/"completion.json",{"generation_and_preflight_seconds":generation,"solve_and_postprocessing_seconds":time.perf_counter()-phase_start,
        "total_elapsed_seconds":time.perf_counter()-started,"eligible_heldout_weeks":1,"ordinary_cases":2,
        "positive_control":"VERIFIED_FEASIBLE_WITHOUT_OPTIMIZATION","april_october":"NO_REFERENCE_NOT_RUN",
        "replication_gate":"NOT_MET_INSUFFICIENT_ELIGIBLE_WEEKS"})
    save(OUTPUT/"final_manifest_check.json",verify_manifest(OUTPUT/"input_manifest.csv"))


if __name__=="__main__":
    main()
