"""Prospective fixed-rule same-week transfer; see TRANSFER_PROTOCOL.md."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time

sys.dont_write_bytecode=True
import numpy as np
import pandas as pd
from scipy.sparse import load_npz,save_npz

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/"docs/research8h/TRANSFER_PROTOCOL.md"
MODELS=["full","two_cc","locality48"]
TWO_CC={"107_CC_1","118_CC_1"}
TEMPORAL={"transition","exclusive_transition","minimum_up","minimum_down"}
REJECT="REJECTED_EXACT_BINARY64_CERTIFICATE"
BOUND_SOURCES={
    "temporal_lp_certificate.py":"6191c5760811cab0ec22b2fb1376a5be3aa47cb548e1260c4a17e2563d9802e4",
    "v8r1_rts_seasonal.py":"bca0127d7b2771c6da3b6a838c8caa7fb6ce0df4eafd9a512326aabd8daf7dc2",
    "temporal_information_pilot.py":"f2e50b7dccb0e1869c8667a00e32c9d2f1d3f1f641459d4ccb802abe0074d4a0",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def array_sha(array):
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def save(path,value):
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+"\n",encoding="utf-8")


for filename,expected in BOUND_SOURCES.items():
    assert sha(ROOT/"src"/filename)==expected,(filename,"bound source changed")
from temporal_lp_certificate import assemble,check_vector,exact_ray_check,solve_case
from v8r1_rts_seasonal import inputs,load_model,verify
from temporal_information_pilot import nodal_check,transitions
from research8h_locality import dwell_support,retain,subset


def replay(directory):
    result=json.loads((directory/"result.json").read_text())
    for name,key in (("matrix.npz","matrix_sha256"),("bounds.npz","bounds_sha256")):
        assert sha(directory/name)==result[key]
    matrix=load_npz(directory/"matrix.npz")
    with np.load(directory/"bounds.npz") as arrays:
        bounds={key:arrays[key] for key in arrays.files}
    if (directory/"dual_certificate.json").exists():
        cert=json.loads((directory/"dual_certificate.json").read_text())
        for name in ("matrix.npz","bounds.npz"):
            assert sha(directory/name)==cert["model_artifacts"][name]
        ray=np.zeros(matrix.shape[0])
        for entry in cert["multipliers"]:
            ray[entry["row"]]=float.fromhex(entry["value_hex"])
        check=exact_ray_check(matrix,bounds,ray)
        if result["verdict"]==REJECT:
            assert check["pass"] and check["robust_pass"]
        return {"type":"exact_certificate","check":check}
    if (directory/"continuous_solution.npz").exists():
        with np.load(directory/"continuous_solution.npz") as arrays:
            check=check_vector(matrix,bounds,arrays["vector"])
        assert check["pass"]
        return {"type":"continuous_witness","check":check,"inferred_UC_status":"UNKNOWN"}
    return {"type":"no_verified_artifact","inferred_UC_status":"UNKNOWN"}


def coverage(records,cases):
    lookup={(r["case"],r["model"]):r for r in records}
    negatives=[c["case"] for c in cases if c["kind"]=="ordinary"]
    positives=[c["case"] for c in cases if c["kind"]=="positive_control"]
    rejected=[name for name in negatives if lookup.get((name,"full"),{}).get("verdict")==REJECT]
    rules={}
    for model in MODELS[1:]:
        hits=[name for name in rejected if lookup.get((name,model),{}).get("verdict")==REJECT]
        rules[model]={"numerator":len(hits),"denominator":len(rejected),
            "coverage":len(hits)/len(rejected) if rejected else None,"covered_cases":hits,
            "not_covered_cases":[name for name in rejected if name not in hits]}
    return {"ordinary_cases":len(negatives),"full_exact_rejections":len(rejected),"rules":rules,
        "verified_positive_controls":len(positives),"positive_control_infeasible_solver_statuses":sum(
            r["kind"]=="positive_control" and r["model_status"]=="Infeasible" for r in records),
        "scheduled_LPs":len(cases)*3,"completed_LPs":len(records),
        "not_run_cases":[{"case":case["case"],"model":model,"status":"NOT_RUN"}
            for case in cases for model in MODELS if (case["case"],model) not in lookup],
        "scope":"prospective fixed-rule transfer on new seeds from the same repaired July week; not external validation"}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-v3",type=Path)
    parser.add_argument("--output",type=Path,default=ROOT/"results/research8h/transfer")
    parser.add_argument("--verify-archived",action="store_true")
    args=parser.parse_args()
    if args.verify_archived:
        records=json.loads((args.output/"results.json").read_text())
        checks=[{"case":r["case"],"model":r["model"],**replay(args.output/r["case"]/r["model"])} for r in records]
        save(args.output/"archive_replay.json",checks)
        print(json.dumps({"replayed":len(checks)}),flush=True)
        return
    if args.source_v3 is None:
        parser.error("--source-v3 is required")
    if (args.output/"sample_freeze.json").exists():
        raise FileExistsError("Preserve existing prospective run; use a separately declared output directory")
    args.output.mkdir(parents=True,exist_ok=True)
    source=load_model(args.source_v3)
    columns,_,pmin,pmax,demand,paths=inputs(source,args.source_v3,7)
    source_rows=pd.read_csv(paths[1])["row"].to_numpy(int)
    p_path=ROOT/"results/v8/network_repair/network_repair_dispatch.csv"
    u_path=ROOT/"results/v8/network_repair/network_fixed_commitment.csv"
    p=pd.read_csv(p_path)[columns].to_numpy(float)
    thermal_names=source.dec.iloc[np.flatnonzero(source.thermal.to_numpy(bool))]["GEN UID"].tolist()
    u=pd.read_csv(u_path)[thermal_names].to_numpy(float)
    assert u.shape==(168,24) and np.array_equal(u,np.rint(u)) and np.isin(u,[0,1]).all()
    means=p.mean(axis=0)
    y,z=transitions(u)
    identity=np.concatenate([a.ravel() for a in (p,u,y,z)])
    imatrix,ibounds,metadata,labels=assemble(source,pmin,pmax,demand,means)
    original_check=check_vector(imatrix,ibounds,identity)
    assert original_check["pass"]
    original_network,nodal_net=nodal_check(source,p,source_rows)
    assert original_network["pass"]
    support=dwell_support(imatrix,metadata,labels)
    masks={"full":np.arange(len(labels)),"two_cc":np.asarray([i for i,l in enumerate(labels)
        if l["family"] not in TEMPORAL or l["uid"] in TWO_CC],dtype=int),
        "locality48":retain(labels,support,48)[0]}
    assert len(masks["full"])==24305 and len(masks["two_cc"])==9609 and len(masks["locality48"])==18313
    classes={}
    for hour in range(48,120):
        classes.setdefault(tuple(map(int,u[hour])),[]).append(hour)
    save(args.output/"positive_class_inventory.json",[{"class":i,"status_bits":list(bits),"size":len(hours),"source_hours":hours}
        for i,(bits,hours) in enumerate(classes.items())])
    package=np.column_stack([source_rows,nodal_net,pmin,pmax,p,u])
    package_hash=array_sha(package)
    old_paths=[ROOT/"results/temporal_information/twins"/name/"permutation.csv"
        for name in ["identity",*[f"seed_{seed}" for seed in range(26092600,26092616)]]]
    prior={array_sha(pd.read_csv(path)["source_hour_0based"].to_numpy(np.int64)):path.parent.name for path in old_paths}
    cases=[]
    seen={}
    for kind,start in (("ordinary",26092700),("positive_control",26092800)):
        for seed in range(start,start+8):
            order=np.arange(168,dtype=np.int64)
            rng=np.random.Generator(np.random.PCG64(seed))
            if kind=="ordinary":
                order[48:120]=rng.permutation(order[48:120])
            else:
                for hours in classes.values():
                    order[hours]=rng.permutation(np.asarray(hours,dtype=np.int64))
            assert np.array_equal(np.sort(order),np.arange(168))
            assert np.array_equal(order[:48],np.arange(48)) and np.array_equal(order[-48:],np.arange(120,168))
            assert np.array_equal(package[order][np.argsort(order)],package)
            pp,uu=p[order],u[order]
            yy,zz=transitions(uu)
            static=verify(source,pp,uu,pmin[order],pmax[order],demand[order],means,"static")
            network,permuted_nodal=nodal_check(source,pp,source_rows[order])
            chronology=verify(source,pp,uu,pmin[order],pmax[order],demand[order],means,"minud",yy,zz)
            ramp=verify(source,pp,uu,pmin[order],pmax[order],demand[order],means,"ramp")
            assert static["pass"] and network["pass"] and np.array_equal(permuted_nodal,nodal_net[order])
            if kind=="positive_control":
                assert np.array_equal(uu,u) and chronology["pass"] and ramp["pass"]
            name=f"{kind}_{seed}"
            directory=args.output/name
            directory.mkdir(exist_ok=True)
            pd.DataFrame({"new_hour_0based":np.arange(168),"source_hour_0based":order,"source_native_row":source_rows[order]}).to_csv(directory/"permutation.csv",index=False)
            vector=np.concatenate([a.ravel() for a in (pp,uu,yy,zz)])
            positive_matrix_checks={}
            if kind=="positive_control":
                cmatrix,cbounds,cmd,clabels=assemble(source,pmin[order],pmax[order],demand[order],means)
                assert cmd==metadata and clabels==labels
                for model_name in MODELS:
                    smatrix,sbounds,_=subset(cmatrix,cbounds,labels,masks[model_name],support)
                    positive_matrix_checks[model_name]=check_vector(smatrix,sbounds,vector)
                    assert positive_matrix_checks[model_name]["pass"]
            np.savez_compressed(directory/"case_arrays.npz",pmin=pmin[order],pmax=pmax[order],demand=demand[order],
                target_means=means,seed_vector=vector,source_order=order)
            signature=array_sha(order)
            record={"case":name,"kind":kind,"seed":seed,"permutation_sha256":signature,
                "permutation_file_sha256":sha(directory/"permutation.csv"),"arrays_sha256":sha(directory/"case_arrays.npz"),
                "changed_hours":int(np.count_nonzero(order!=np.arange(168))),
                "duplicate_of_current_case":seen.get(signature),"duplicate_of_development_case":prior.get(signature),
                "commitment_sequence_unchanged":bool(np.array_equal(uu,u)),"static":static,"network":network,
                "positive_matrix_checks_before_first_LP":positive_matrix_checks,
                "chronology_seed_replay":chronology,"on_on_ramp_seed_replay":ramp,
                "full_package_inverse_restoration_sha256":array_sha(package[order][np.argsort(order)]),
                "individual_mean_max_error_MW":float(np.abs(pp.mean(axis=0)-means).max())}
            assert record["full_package_inverse_restoration_sha256"]==package_hash
            save(directory/"generation_checks.json",record)
            cases.append(record)
            seen.setdefault(signature,name)
    input_paths=[Path(__file__),PROTOCOL,*[ROOT/"src"/name for name in BOUND_SOURCES],ROOT/"src/research8h_locality.py",
        p_path,u_path,*paths,*old_paths,args.source_v3/"code/dscgrid_model.py",*sorted((args.source_v3/"raw").rglob("*.csv"))]
    manifest=[{"path":str(path),"bytes":path.stat().st_size,"sha256":sha(path)} for path in dict.fromkeys(input_paths)]
    pd.DataFrame(manifest).to_csv(args.output/"input_manifest.csv",index=False)
    save(args.output/"sample_freeze.json",{"frozen_before_first_transfer_LP_utc":datetime.now(timezone.utc).isoformat(),
        "protocol_sha256":sha(PROTOCOL),"script_sha256":sha(Path(__file__)),"cases":cases,"models":MODELS,
        "fixed_two_units":sorted(TWO_CC),"fixed_locality_window":[60,107],"per_LP_limit_s":30,"phase_budget_s":1200,
        "model_rows":{name:len(mask) for name,mask in masks.items()},"original_identity_matrix_check":original_check,
        "all_positive_network_chronology_controls_pass":True,"generation":"PCG64; all16 orders saved before solving"})
    print(json.dumps({"frozen":True,"cases":len(cases),"positive_controls":8,"scheduled_LPs":48}),flush=True)
    records=[]
    started=time.monotonic()
    for case in cases:
        directory=args.output/case["case"]
        with np.load(directory/"case_arrays.npz") as arrays:
            matrix,bounds,md,labs=assemble(source,arrays["pmin"],arrays["pmax"],arrays["demand"],arrays["target_means"])
            seed_vector=arrays["seed_vector"]
        assert md==metadata and labs==labels
        for name in MODELS:
            remaining=1200-(time.monotonic()-started)
            if remaining<35:
                save(args.output/"budget_stop.json",{"case":case["case"],"model":name,"remaining_s":remaining})
                save(args.output/"coverage.json",coverage(records,cases))
                return
            output=directory/name
            output.mkdir(exist_ok=True)
            selected,sbounds,slabels=subset(matrix,bounds,labels,masks[name],support)
            if case["kind"]=="positive_control":
                witness=check_vector(selected,sbounds,seed_vector)
                save(output/"positive_seed_matrix_check.json",witness)
                assert witness["pass"]
            save_npz(output/"matrix.npz",selected,compressed=True)
            np.savez_compressed(output/"bounds.npz",**sbounds)
            pd.DataFrame(slabels).to_csv(output/"row_metadata.csv.gz",index=False,compression="gzip")
            result=solve_case(selected,sbounds,output,slabels,30,p.size)
            result.update({"case":case["case"],"kind":case["kind"],"seed":case["seed"],"model":name,
                "rows":selected.shape[0],"columns":selected.shape[1],"matrix_sha256":sha(output/"matrix.npz"),"bounds_sha256":sha(output/"bounds.npz")})
            save(output/"result.json",result)
            result["archive_replay"]=replay(output)
            save(output/"result.json",result)
            records.append(result)
            save(args.output/"results.json",records)
            pd.DataFrame([{k:v for k,v in item.items() if not isinstance(v,(list,dict))} for item in records]).to_csv(args.output/"summary.csv",index=False)
            print(json.dumps({k:result[k] for k in ("case","model","model_status","verdict","elapsed_s")}),flush=True)
            if case["kind"]=="positive_control" and (result["model_status"]=="Infeasible" or result["verdict"]==REJECT):
                save(args.output/"FATAL_POSITIVE_CONTRADICTION.json",result)
                raise AssertionError("Positive network/chronology witness contradicted by LP; preserve and investigate")
    assert all(sha(Path(entry["path"]))==entry["sha256"] for entry in manifest)
    save(args.output/"coverage.json",coverage(records,cases))
    save(args.output/"completion.json",{"utc":datetime.now(timezone.utc).isoformat(),"phase_elapsed_s":time.monotonic()-started,
        "completed_LPs":len(records),"source_hashes_still_match":True,"unique_current_orders":len(seen),
        "duplicate_current_case_count":sum(c["duplicate_of_current_case"] is not None for c in cases),
        "duplicate_development_case_count":sum(c["duplicate_of_development_case"] is not None for c in cases)})


if __name__=="__main__":
    main()
