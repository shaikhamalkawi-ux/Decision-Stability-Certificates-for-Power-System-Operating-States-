"""Prepare only, then explicitly run three fixed energy-LP refinements."""
from __future__ import annotations
import argparse
import csv
from datetime import datetime, timezone
from fractions import Fraction as Q
import gzip
import json
from pathlib import Path
import shutil
import sys
import time
sys.dont_write_bytecode = True
import highspy
import numpy as np
from scipy.sparse import csr_matrix, load_npz, save_npz
from research8h_energy_price_bounds import arrays, f, from_rat, labels, objective_and_roster, rat, read, save, sha
from temporal_lp_certificate import check_vector

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT/"results/research8h/energy_price_bounds"
SOURCE = ROOT/"results/research8h/seasonal_transfer"
UNCAPPED = ROOT/"results/seasonal_uncapped"
OUT = ROOT/"results/research8h/energy_lp_refinement"
PROTOCOL = ROOT/"docs/research8h/ENERGY_LP_REFINEMENT_PROTOCOL.md"
CASES = ["january_identity", "seed_26093100", "seed_26093101"]
TAU = f(1e-5)


def exact_bound(A, b, c, raw):
    assert raw.shape == (A.shape[0],) and np.isfinite(raw).all()
    assert np.isfinite(b["column_lower"]).all() and np.isfinite(b["column_upper"]).all()
    forbidden = ((raw>0)&~np.isfinite(b["row_lower"]))|((raw<0)&~np.isfinite(b["row_upper"]))
    d = raw.copy(); d[forbidden] = 0.
    q = [f(v) for v in c]; beta = Q(0); norm_d = Q(0)
    for i in np.flatnonzero(d):
        weight = f(d[i]); norm_d += abs(weight)
        endpoint = b["row_lower" if weight>0 else "row_upper"][i]
        assert np.isfinite(endpoint)
        beta += weight*f(endpoint)
        for e in range(A.indptr[i], A.indptr[i+1]): q[A.indices[e]] -= weight*f(A.data[e])
    box = sum((v*f(b["column_lower" if v>=0 else "column_upper"][j]) for j,v in enumerate(q)), Q(0))
    norm_q = sum(map(abs,q), Q(0)); nominal = beta+box
    expanded = nominal-TAU*(norm_d+norm_q)
    report = {"arithmetic":"exact Fraction arithmetic on archived binary64 inputs",
              "nominal_lower_bound_MWh":rat(nominal), "expanded_lower_bound_MWh":rat(expanded),
              "row_term":rat(beta), "finite_box_term":rat(box), "row_dual_l1":rat(norm_d),
              "stationarity_residual_l1":rat(norm_q), "tau":rat(TAU),
              "projected_entries":int(forbidden.sum()), "raw_dual_is_projected_dual":not bool(forbidden.any()),
              "projected_row_dual_nonzeros":int(np.count_nonzero(d)),
              "exact_residual_nonzeros":sum(v!=0 for v in q),
              "solver_optimality_or_exact_stationarity_required":False,
              "expanded_model":"Every finite row and column bound widened by the exact binary64 value1e-5; no clipping."}
    return report, d, [{"column":j,**rat(v)} for j,v in enumerate(q) if v]


def sanity():
    results=[]
    def one(name,a,lo,hi,d,want,expanded=None):
        b={"row_lower":np.array([lo]),"row_upper":np.array([hi]),"column_lower":np.array([0.]),"column_upper":np.array([1.])}
        report,_,_=exact_bound(csr_matrix([[a]]),b,np.array([1.]),np.array([d]))
        assert from_rat(report["nominal_lower_bound_MWh"])==want
        if expanded is not None: assert from_rat(report["expanded_lower_bound_MWh"])==expanded
        results.append({"case":name,"pass":True,"report":report})
    one("positive_lower",1.,.2,np.inf,1.,f(.2))
    one("negative_upper",-1.,-np.inf,-.2,-1.,f(.2))
    one("zero_dual",1.,.2,np.inf,0.,Q(0),-TAU)
    one("imperfect_positive_q",1.,.2,np.inf,.5,f(.2)/2)
    one("imperfect_negative_q",1.,.2,np.inf,2.,2*f(.2)-1)
    one("inadmissible_sign_projected",1.,-np.inf,.2,1.,Q(0),-TAU)
    return results


def check_manifest():
    frozen=read(OUT/"prepared_freeze.json")
    assert sha(OUT/"input_manifest.json")==frozen["input_manifest_sha256"]
    entries=read(OUT/"input_manifest.json")
    assert all(sha(Path(x["path"]))==x["sha256"] for x in entries)
    return entries


def prepare():
    OUT.mkdir(parents=True,exist_ok=False)
    original_audit=read(OLD/"audit_freeze.json")
    original_bindings={str(Path(x["path"]).resolve()):x for x in original_audit["inputs"]}
    assert all(sha(Path(x["path"]))==x["sha256"] for x in original_audit["inputs"])
    assert read(OLD/"completion.json")["optimization_calls"]==0
    original_results=read(OLD/"results.json")
    assert len(original_results)==2 and all(x["status"]=="EXACT_EXPANDED_BINARY_ENERGY_BRACKETS_VERIFIED" for x in original_results)
    gen_entries=[x for x in original_audit["inputs"] if Path(x["path"]).name=="gen.csv"]
    assert len(gen_entries)==1
    with Path(gen_entries[0]["path"]).open(newline="",encoding="utf-8-sig") as stream: native_gen=list(csv.DictReader(stream))
    paths=[Path(__file__),PROTOCOL,ROOT/"src/research8h_energy_price_bounds.py",ROOT/"src/temporal_lp_certificate.py",
           ROOT/"src/research8h_mean_repair.py",ROOT/"docs/research8h/MEAN_REPAIR_PROTOCOL.md",
           OLD/"audit_freeze.json",OLD/"results.json",OLD/"identity_bound.json",OLD/"completion.json",
           OLD/"independent_review.json",Path(gen_entries[0]["path"])]
    controls=[]
    save(OUT/"synthetic_checker_tests.json",sanity())
    for case in CASES:
        identity=case=="january_identity"
        parent=SOURCE/case if identity else UNCAPPED/case
        A=load_npz(parent/"matrix.npz"); b=arrays(parent/"bounds.npz")
        meta=read(parent/"model_metadata.json"); rows=labels(parent/"row_metadata.csv.gz")
        objective,fossil=objective_and_roster(meta,native_gen)
        assert not any("mean" in row["family"] for row in rows)
        cap=np.array([i for i,row in enumerate(rows) if row["family"]=="fossil_energy_cap"],dtype=int)
        if identity:
            assert len(cap)==1
            keep=np.delete(np.arange(A.shape[0]),cap)
            S=A[keep].tocsr()
            sb={k:v[keep] if k.startswith("row_") else v.copy() for k,v in b.items()}
            upper_point=parent/"constructive_vector.npz"
            binary_path=parent/"integrality.npz"
            previous=original_results[0]
            lower=previous["identity_lower_MWh"];upper=previous["reference_energy_MWh"]
        else:
            assert len(cap)==0 and meta["energy_cap_constraints"]==0
            keep=np.arange(A.shape[0]);S=A;sb=b
            upper_point=parent/"recovered_vector.npz"
            binary_path=parent/"original_integrality.npz"
            previous=next(x for x in original_results if x["case"]==case)
            lower=previous["target_lower_MWh"];upper=previous["target_upper_MWh"]
            assert np.array_equal(arrays(parent/"objective.npz")["objective"],objective)
        assert S.shape==(34680,23016) and (S!=A[keep]).nnz==0
        assert all(np.array_equal(sb[k],b[k][keep] if k.startswith("row_") else b[k]) for k in sb)
        for filename in [parent/"matrix.npz",parent/"bounds.npz",upper_point,binary_path]:
            assert str(filename.resolve()) in original_bindings
            assert sha(filename)==original_bindings[str(filename.resolve())]["sha256"]
        original_binary=arrays(binary_path)["integrality"]
        assert np.array_equal(np.flatnonzero(original_binary),np.arange(6888,18984))
        directory=OUT/case;directory.mkdir()
        if identity:
            save_npz(directory/"matrix.npz",S);np.savez_compressed(directory/"bounds.npz",**sb)
        else:
            shutil.copyfile(parent/"matrix.npz",directory/"matrix.npz")
            shutil.copyfile(parent/"bounds.npz",directory/"bounds.npz")
        np.savez_compressed(directory/"objective.npz",objective=objective)
        np.savez_compressed(directory/"retained_parent_rows.npz",rows=keep)
        shutil.copyfile(binary_path,directory/"original_integrality.npz")
        with gzip.open(directory/"row_metadata.csv.gz","wt",encoding="utf-8",newline="") as stream:
            writer=csv.DictWriter(stream,fieldnames=[*rows[0],"original_row"]);writer.writeheader()
            for i,old_i in enumerate(keep): writer.writerow({**rows[int(old_i)],"row":i,"original_row":int(old_i)})
        save(directory/"prior_bounds.json",{"lower_MWh":lower,"binary_upper_MWh":upper,
             "prior_case":case,"scope":"uncapped uniformly expanded original-binary model"})
        control={"case":case,"parent_matrix_sha256":sha(parent/"matrix.npz"),"parent_bounds_sha256":sha(parent/"bounds.npz"),
                 "exact_row_subset_and_bounds_match":True,"deleted_cap_rows":int(len(cap)),"caps_remaining":0,"mean_rows":0,
                 "positive_vector_path":str(upper_point),"positive_vector_sha256":sha(upper_point),
                 "binary_upper_MWh":upper,"prior_exact_expanded_point_audit":str(OLD/"results.json"),
                 "expanded_witness_inherited":True,"all_LP_variables_continuous":True,"control_optimizations":0}
        save(directory/"model_and_upper_binding.json",control);controls.append(control)
        zero,_,_=exact_bound(S,sb,objective,np.zeros(S.shape[0]))
        assert from_rat(zero["nominal_lower_bound_MWh"])==0
        assert from_rat(zero["expanded_lower_bound_MWh"])==-3864*TAU
        save(directory/"zero_dual_sanity.json",zero)
        paths.extend([parent/"matrix.npz",parent/"bounds.npz",parent/"model_metadata.json",parent/"row_metadata.csv.gz",upper_point,binary_path])
        paths.extend(directory.iterdir())
    save(OUT/"positive_inheritance_proofs.json",controls)
    paths.extend([OUT/"positive_inheritance_proofs.json",OUT/"synthetic_checker_tests.json"])
    manifest=[{"path":str(p),"sha256":sha(p),"bytes":p.stat().st_size} for p in dict.fromkeys(paths)]
    save(OUT/"input_manifest.json",manifest)
    save(OUT/"prepared_freeze.json",{"utc":datetime.now(timezone.utc).isoformat(),"case_order":CASES,
         "input_manifest_sha256":sha(OUT/"input_manifest.json"),"source_sha256":sha(Path(__file__)),"protocol_sha256":sha(PROTOCOL),
         "all_three_models_frozen_before_first_solve":True,"optimization_calls":0,"seconds_per_LP":60,
         "threads":1,"seed":0,"simplex":True,"presolve":"off","requires_explicit_parent_GO":True})
    print(json.dumps({"event":"PREPARED_NO_SOLVES","cases":CASES,"bound_files":len(manifest)}),flush=True)


def finite(v): return float(v) if np.isfinite(v) else None


def run_prepared():
    manifest=check_manifest()
    with (OUT/"execution_started.json").open("x",encoding="utf-8") as stream:
        json.dump({"utc":datetime.now(timezone.utc).isoformat(),"declared_LP_calls":3,"no_retries":True},stream,indent=2)
    results=[]
    for case in CASES:
        directory=OUT/case;A=load_npz(directory/"matrix.npz");b=arrays(directory/"bounds.npz")
        c=arrays(directory/"objective.npz")["objective"]
        lp=highspy.HighsLp();lp.num_row_,lp.num_col_=A.shape
        lp.col_cost_,lp.col_lower_,lp.col_upper_=c,b["column_lower"],b["column_upper"]
        lp.row_lower_,lp.row_upper_=b["row_lower"],b["row_upper"]
        lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise
        lp.a_matrix_.num_row_,lp.a_matrix_.num_col_=A.shape
        lp.a_matrix_.start_,lp.a_matrix_.index_,lp.a_matrix_.value_=A.indptr,A.indices,A.data
        solver=highspy.Highs()
        options={"time_limit":60.,"threads":1,"random_seed":0,"solver":"simplex","presolve":"off",
                 "log_to_console":False,"log_file":str(directory/"solver.log")}
        for key,value in options.items(): assert solver.setOptionValue(key,value)==highspy.HighsStatus.kOk
        assert solver.passModel(lp)==highspy.HighsStatus.kOk
        started=time.perf_counter();run_status=solver.run();elapsed=time.perf_counter()-started
        status,solution,info=solver.getModelStatus(),solver.getSolution(),solver.getInfo()
        result={"case":case,"model_status":solver.modelStatusToString(status),"run_status":str(run_status),
                "solver_version":solver.version(),"elapsed_s":elapsed,"options":options,"optimization_calls":1,
                "primal_valid":bool(solution.value_valid),"dual_valid":bool(solution.dual_valid),
                "numerical_objective_MWh":finite(info.objective_function_value),"simplex_iterations":int(info.simplex_iteration_count),
                "exact_optimality_claim":False,"new_lower_bound_status":"UNAVAILABLE_RETURNED_DUAL"}
        if solution.value_valid:
            vector=np.asarray(solution.col_value)
            np.savez_compressed(directory/"primal.npz",vector=vector,row_value=np.asarray(solution.row_value))
            result["numerical_primal_check"]=check_vector(A,b,vector)
            result["continuous_primal_not_a_binary_upper_bound"]=True
        new=None
        if solution.dual_valid:
            raw=np.asarray(solution.row_dual);np.savez_compressed(directory/"raw_duals.npz",row_dual=raw,column_dual=np.asarray(solution.col_dual))
            if raw.shape==(A.shape[0],) and np.isfinite(raw).all():
                report,projected,residuals=exact_bound(A,b,c,raw)
                np.savez_compressed(directory/"projected_row_dual.npz",row_dual=projected)
                save(directory/"exact_lower_bound.json",report);save(directory/"exact_stationarity_residual.json",residuals)
                replay,again,again_q=exact_bound(A,b,c,arrays(directory/"projected_row_dual.npz")["row_dual"])
                for key in ["nominal_lower_bound_MWh","expanded_lower_bound_MWh","row_term","finite_box_term","row_dual_l1","stationarity_residual_l1"]: assert replay[key]==report[key]
                assert np.array_equal(again,projected) and again_q==residuals
                new=from_rat(report["expanded_lower_bound_MWh"])
                result.update(new_lower_bound_status="EXACT_EXPANDED_OBJECTIVE_LOWER_BOUND",exact_bound=report,saved_projected_dual_replay=True)
            else: result["new_lower_bound_status"]="NONFINITE_OR_WRONG_SHAPE_RETURNED_DUAL"
        prior=read(directory/"prior_bounds.json");old=from_rat(prior["lower_MWh"]);upper=from_rat(prior["binary_upper_MWh"])
        best=max(old,new) if new is not None else old
        result.update(previous_lower_MWh=rat(old),best_lower_MWh=rat(best),unchanged_binary_upper_MWh=rat(upper),
                      improved_lower_bound=bool(best>old),new_lower_MWh=None if new is None else rat(new))
        if best>upper:
            result["fatal_contradiction_with_exact_expanded_binary_witness"]=True
            save(directory/"result.json",result)
            raise AssertionError("Exact objective lower bound exceeds verified binary upper witness")
        save(directory/"result.json",result);results.append(result);save(OUT/"results.json",results)
        print(json.dumps({k:result[k] for k in ["case","model_status","elapsed_s","new_lower_bound_status","improved_lower_bound"]}),flush=True)
    identity=results[0];li=from_rat(identity["best_lower_MWh"]);eref=from_rat(identity["unchanged_binary_upper_MWh"])
    brackets=[]
    for result in results[1:]:
        lt=from_rat(result["best_lower_MWh"]);ut=from_rat(result["unchanged_binary_upper_MWh"])
        brackets.append({"case":result["case"],"target_optimum_bounds_MWh":{"lower":rat(lt),"upper":rat(ut)},
            "identity_optimum_bounds_MWh":{"lower":rat(li),"upper":rat(eref)},
            "optimum_difference_MWh":{"lower":rat(lt-eref),"upper":rat(ut-li)},
            "target_optimum_excess_over_chosen_reference_MWh":{"lower":rat(lt-eref),"upper":rat(ut-eref)},
            "scope":"uncapped uniformly expanded original-binary models; LP used only for lower bounds"})
    save(OUT/"refined_brackets.json",brackets)
    assert all(sha(Path(x["path"]))==x["sha256"] for x in manifest)
    save(OUT/"completion.json",{"utc":datetime.now(timezone.utc).isoformat(),"optimization_calls":3,
         "all_frozen_hashes_unchanged":True,"binary_optimizations":0,"new_data_or_replication":False})


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare-only",action="store_true");mode.add_argument("--run-prepared",action="store_true")
    args=parser.parse_args()
    if args.prepare_only: prepare()
    else: run_prepared()
