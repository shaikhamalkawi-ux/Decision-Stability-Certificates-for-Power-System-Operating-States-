"""Four frozen January LPs transferring the unchanged July temporal rules."""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
import numpy as np
import pandas as pd
from scipy.sparse import load_npz,save_npz

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"results/research8h/seasonal_transfer"
OUTPUT=ROOT/"results/research8h/seasonal_rule_transfer"
PROTOCOL=ROOT/"docs/research8h/SEASONAL_RULE_TRANSFER_PROTOCOL.md"
SEEDS=[26093100,26093101]
RULES=["two_cc","locality48"]
TEMPORAL={"transition","exclusive_transition","minimum_up","minimum_down"}
DWELL={"minimum_up","minimum_down"}
CC={"107_CC_1","118_CC_1"}
REJECT="REJECTED_EXACT_BINARY64_CERTIFICATE"


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False)+"\n",encoding="utf-8")
def arrays(p):
    with np.load(p) as z:return {k:z[k].copy() for k in z.files}


assert sha(ROOT/"src/temporal_lp_certificate.py")=="6191c5760811cab0ec22b2fb1376a5be3aa47cb548e1260c4a17e2563d9802e4"
PRIOR=ROOT/"results/research8h/transfer"
prior_freeze=json.loads((PRIOR/"sample_freeze.json").read_text())
assert sha(ROOT/"docs/research8h/TRANSFER_PROTOCOL.md")==prior_freeze["protocol_sha256"]
assert sha(ROOT/"src/research8h_transfer.py")==prior_freeze["script_sha256"]
prior_inputs=pd.read_csv(PRIOR/"input_manifest.csv")
locality=[x for x in prior_inputs.itertuples(index=False) if Path(x.path).name=="research8h_locality.py"]
assert len(locality)==1 and sha(ROOT/"src/research8h_locality.py")==locality[0].sha256
from research8h_locality import dwell_support,retain,subset
from temporal_lp_certificate import solve_case,check_vector,exact_ray_check


def load_parent(path):
    A=load_npz(path/"matrix.npz");b=arrays(path/"bounds.npz")
    metadata=json.loads((path/"model_metadata.json").read_text())
    labels=pd.read_csv(path/"row_metadata.csv.gz",dtype={"uid":str}).to_dict("records")
    assert A.shape==(34681,23016) and len(labels)==A.shape[0]
    assert all(label["row"]==i for i,label in enumerate(labels))
    assert not any("mean" in x["family"] for x in labels)
    cap=[i for i,x in enumerate(labels) if x["family"]=="fossil_energy_cap"]
    assert len(cap)==1 and b["row_upper"][cap[0]]==23195 and np.isneginf(b["row_lower"][cap[0]])
    return A,b,metadata,labels


def masks(A,metadata,labels):
    support=dwell_support(A,metadata,labels)
    offsets=metadata["offsets"];state_starts=[offsets[k] for k in ["U","Y","Z"]]
    end=offsets["theta"]
    for row,(first,last) in support.items():
        hours=[]
        for j in A.indices[A.indptr[row]:A.indptr[row+1]]:
            assert state_starts[0]<=j<end
            start=max(x for x in state_starts if x<=j)
            hours.append(int((j-start)//24))
        assert (min(hours),max(hours))==(first,last)
    two=np.array([i for i,x in enumerate(labels) if x["family"] not in TEMPORAL or x["uid"] in CC],dtype=int)
    loc,left,right=retain(labels,support,48)
    assert (left,right)==(60,107)
    result={"two_cc":two,"locality48":loc}
    assert len(two)==19985 and len(loc)==28689
    for rule,keep in result.items():
        assert len(np.unique(keep))==len(keep) and np.all(np.diff(keep)>0)
        kept=set(keep)
        assert all(i in kept for i,x in enumerate(labels) if x["family"] not in TEMPORAL)
        if rule=="two_cc":
            assert all((i in kept)==(x["uid"] in CC) for i,x in enumerate(labels) if x["family"] in TEMPORAL)
        else:
            assert all(i in kept for i,x in enumerate(labels) if x["family"] in {"transition","exclusive_transition"})
            assert all((i in kept)==(60<=first and last<=107) for i,(first,last) in support.items())
    return result,support


def exact_subset(A,b,labels,keep,support):
    S,sb,sl=subset(A,b,labels,keep,support)
    assert (S!=A[keep]).nnz==0
    assert all(np.array_equal(sb[k],b[k][keep] if k.startswith("row_") else b[k]) for k in b)
    return S,sb,sl


def prepare():
    OUTPUT.mkdir(parents=True,exist_ok=False)
    audit_path=BASE/"independent_review.json";audit=json.loads(audit_path.read_text())
    assert audit["status"]=="PASS_COMPLETE" and audit["optimization_calls"]==0
    assert [x["seed"] for x in audit["cases"]]==SEEDS and all(x["robust_Farkas_replay_pass"] for x in audit["cases"])
    paths=[Path(__file__),PROTOCOL,audit_path,ROOT/"docs/research8h/SEASONAL_TRANSFER_INDEPENDENT_REVIEW.md",
        ROOT/"docs/research8h/TRANSFER_PROTOCOL.md",ROOT/"src/research8h_transfer.py",ROOT/"src/research8h_locality.py",
        ROOT/"src/temporal_lp_certificate.py",PRIOR/"sample_freeze.json",PRIOR/"input_manifest.csv"]
    save(OUTPUT/"preparation_freeze.json",{"utc":datetime.now(timezone.utc).isoformat(),"script_sha256":sha(Path(__file__)),
        "protocol_sha256":sha(PROTOCOL),"case_order":[{"seed":s,"rule":r} for s in SEEDS for r in RULES],
        "two_units":sorted(CC),"window":[60,107],"LP_seconds":30,"threads":1,"seed":0,"presolve":"off",
        "solver":"simplex","coverage_denominator":2,"full_January_labels_already_known":True,
        "scope":"Fixed-rule out-of-week evaluation; January adds DC+cap and removes July's named means; not blind or new-network."})
    for seed in SEEDS:
        parent=BASE/f"seed_{seed}";A,b,md,labels=load_parent(parent)
        exactcase=next(x for x in audit["cases"] if x["seed"]==seed)
        assert sha(parent/"matrix.npz")==exactcase["matrix_sha256"] and sha(parent/"bounds.npz")==exactcase["bounds_sha256"]
        assert sha(parent/"lp/dual_certificate.json")==exactcase["certificate_sha256"]
        keep_by_rule,support=masks(A,md,labels)
        paths.extend(parent/p for p in ["matrix.npz","bounds.npz","model_metadata.json","row_metadata.csv.gz","permutation.csv","lp/dual_certificate.json","lp/result.json"])
        for rule in RULES:
            keep=keep_by_rule[rule];S,sb,sl=exact_subset(A,b,labels,keep,support)
            directory=OUTPUT/f"seed_{seed}"/rule;directory.mkdir(parents=True)
            save_npz(directory/"matrix.npz",S);np.savez_compressed(directory/"bounds.npz",**sb)
            np.savez_compressed(directory/"objective.npz",objective=np.zeros(S.shape[1]))
            np.savez_compressed(directory/"retained_parent_rows.npz",rows=keep)
            pd.DataFrame(sl).to_csv(directory/"row_metadata.csv.gz",index=False,compression="gzip")
            counts=pd.Series([x["family"] for x in sl]).value_counts().to_dict()
            save(directory/"subset_proof.json",{"parent_matrix_sha256":sha(parent/"matrix.npz"),"parent_bounds_sha256":sha(parent/"bounds.npz"),
                "exact_row_subset":True,"column_bounds_unchanged":True,"row_bounds_exact_indexed_copy":True,
                "all_static_network_cap_rows_preserved":True,"rows":S.shape[0],"columns":S.shape[1],
                "row_family_counts":counts,"zero_named_mean_rows":True,"cap_MWh":23195,"parent_seed":seed,"rule":rule})
            paths.extend(directory/p for p in ["matrix.npz","bounds.npz","objective.npz","retained_parent_rows.npz","row_metadata.csv.gz","subset_proof.json"])
    inherited=[]
    for case in ["january_identity","seed_26100100"]:
        full=next(x for x in audit["exact_expanded_positive_and_static_replay"] if x["case"]==case)
        assert full["binary_UYZ_exact"] and full["full_bound_expansion_exact_pass"] and full["removed_rows"]==0
        parent=BASE/case;A,b,md,labels=load_parent(parent)
        for filename,key in [("matrix.npz","matrix_sha256"),("bounds.npz","bounds_sha256"),("constructive_vector.npz","constructive_vector_sha256")]:
            assert sha(parent/filename)==full[key]
        keep_by_rule,support=masks(A,md,labels)
        for rule in RULES:
            keep=keep_by_rule[rule];S,sb,sl=exact_subset(A,b,labels,keep,support)
            inherited.append({"case":case,"rule":rule,"rows":len(keep),"full_matrix_sha256":sha(parent/"matrix.npz"),
                "full_bounds_sha256":sha(parent/"bounds.npz"),"constructive_vector_sha256":sha(parent/"constructive_vector.npz"),
                "full_exact_expanded_feasibility_bound_to_completed_audit":True,"binary_UYZ_exact_from_bound_audit":True,
                "exact_row_subset_and_unchanged_column_bounds":True,"inherited_expanded_feasibility":True,
                "proof":"Deleting rows with their corresponding bounds preserves every feasible vector; unchanged column bounds and identical tau expansion commute with row deletion.",
                "witness_matrix_evaluations":0,"native_control_replays":0,"optimization_calls":0})
        paths.extend(parent/p for p in ["matrix.npz","bounds.npz","model_metadata.json","row_metadata.csv.gz","constructive_vector.npz"])
    save(OUTPUT/"positive_inheritance_proof.json",{"exact_audit_sha256":sha(audit_path),"controls":inherited,
        "expansion":"Every finite bound expanded by exact binary64 tau=1e-5, cap to23195+tau; original nominal exact feasibility not asserted."})
    paths.append(OUTPUT/"positive_inheritance_proof.json")
    manifest=[{"path":str(p),"sha256":sha(p),"bytes":p.stat().st_size} for p in dict.fromkeys(paths)]
    pd.DataFrame(manifest).to_csv(OUTPUT/"input_manifest.csv",index=False)
    save(OUTPUT/"all_models_frozen_before_first_solve.json",{"utc":datetime.now(timezone.utc).isoformat(),"manifest_sha256":sha(OUTPUT/"input_manifest.csv"),
        "four_target_models":True,"all_positive_inheritance_proofs_pass":True,"control_optimizations":0,"target_optimizations_so_far":0})
    print(json.dumps({"prepared_models":4,"positive_inheritance_proofs":4,"solves":0}),flush=True)


def replay(directory,result):
    A=load_npz(directory/"matrix.npz");b=arrays(directory/"bounds.npz")
    if (directory/"dual_certificate.json").exists():
        path=directory/"dual_certificate.json";cert=json.loads(path.read_text())
        assert all(sha(directory/name)==cert["model_artifacts"][name] for name in ["matrix.npz","bounds.npz"])
        d=np.zeros(A.shape[0])
        for entry in cert["multipliers"]:d[entry["row"]]=float.fromhex(entry["value_hex"])
        check=exact_ray_check(A,b,d)
        if result["verdict"]==REJECT:assert check["pass"] and check["robust_pass"]
        labels=pd.read_csv(directory/"row_metadata.csv.gz",dtype={"uid":str}).to_dict("records")
        units=sorted({labels[i]["uid"] for i in np.flatnonzero(d) if labels[i]["family"] in TEMPORAL})
        support=cert.get("support",{})
        generic=support.pop("individual_units_in_nonzero_rows",None)
        support.update(generic_non_ALL_label_count_including_network_labels=generic,
            thermal_units_with_temporal_row_support=units,named_mean_rows=0,
            interpretation="Full January static/DC-network/cap background is retained; no named-unit means. Thermal unit support excludes bus/branch labels. Window support does not establish isolated-window sufficiency.")
        cert["support"]=support;save(path,cert)
        return {"kind":"exact_ray_replay","check":check}
    if (directory/"continuous_solution.npz").exists():
        vector=arrays(directory/"continuous_solution.npz")["vector"]
        check=check_vector(A,b,vector);assert check["pass"]
        result["legacy_helper_fractional_tail_count_including_angles"]=result.pop("fractional_state_coordinate_count",None)
        result["fractional_UYZ_coordinates"]=int(np.count_nonzero(np.abs(vector[6888:18984]-np.rint(vector[6888:18984]))>1e-5))
        return {"kind":"continuous_subset_witness","check":check,"full_model_status":"Already certified infeasible; this subset admission does not change that.","binary_admission_claim":False}
    return {"kind":"no_verified_artifact","outcome":"UNKNOWN"}


def run_prepared():
    marker=OUTPUT/"solve_started.json"
    if marker.exists():raise FileExistsError("No retries; preserve prior started run")
    freeze=json.loads((OUTPUT/"all_models_frozen_before_first_solve.json").read_text())
    assert freeze["manifest_sha256"]==sha(OUTPUT/"input_manifest.csv")
    manifest=pd.read_csv(OUTPUT/"input_manifest.csv").to_dict("records")
    assert all(sha(Path(x["path"]))==x["sha256"] for x in manifest)
    save(marker,{"utc":datetime.now(timezone.utc).isoformat(),"declared_LP_calls":4,"threads":1})
    records=[]
    for seed in SEEDS:
        for rule in RULES:
            directory=OUTPUT/f"seed_{seed}"/rule
            A=load_npz(directory/"matrix.npz");b=arrays(directory/"bounds.npz")
            labels=pd.read_csv(directory/"row_metadata.csv.gz",dtype={"uid":str}).to_dict("records")
            result=solve_case(A,b,directory,labels,30,6888)
            result.update(seed=seed,rule=rule,rows=A.shape[0],columns=A.shape[1],optimization_calls=1,
                matrix_sha256=sha(directory/"matrix.npz"),bounds_sha256=sha(directory/"bounds.npz"),
                full_January_label_known_before_this_run="CERTIFIED_INFEASIBLE",
                scope="Fixed prior July rule on January DC+cap/no-mean model; subset admission is not full UC admission.")
            result["archive_replay"]=replay(directory,result)
            save(directory/"result.json",result);records.append(result);save(OUTPUT/"results.json",records)
            print(json.dumps({k:result[k] for k in ["seed","rule","model_status","verdict","elapsed_s"]}),flush=True)
    assert all(sha(Path(x["path"]))==x["sha256"] for x in manifest)
    coverage={}
    for rule in RULES:
        selected=[x for x in records if x["rule"]==rule]
        rejected=[x["seed"] for x in selected if x["verdict"]==REJECT]
        admitted=[x["seed"] for x in selected if x["verdict"]=="ADMITTED_CONTINUOUS_RELAXATION"]
        unknown=[x["seed"] for x in selected if x["seed"] not in rejected+admitted]
        coverage[rule]={"exact_robust_rejections":len(rejected),"known_full_negative_denominator":2,"coverage":len(rejected)/2,
            "rejected_seeds":rejected,"continuous_subset_admissions":admitted,"unknown_seeds":unknown}
    save(OUTPUT/"coverage.json",{"rules":coverage,"full_labels_previously_known":True,
        "scope":"Two known January negatives; not blind, not new-network; no units/window/background constraints retuned."})
    pd.DataFrame([{k:v for k,v in x.items() if not isinstance(v,(list,dict))} for x in records]).to_csv(OUTPUT/"summary.csv",index=False)
    save(OUTPUT/"completion.json",{"utc":datetime.now(timezone.utc).isoformat(),"optimization_calls":4,
        "full_model_optimizations":0,"control_optimizations":0,"native_control_replays":0,
        "all_frozen_source_and_model_hashes_match":True})


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-prepared",action="store_true")
    args=parser.parse_args()
    if args.run_prepared:run_prepared()
    else:prepare()
