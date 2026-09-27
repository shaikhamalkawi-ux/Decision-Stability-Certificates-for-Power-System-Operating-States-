"""Fixed uncapped qualification of all four prescribed fresh January targets.

Preparation and execution require separate independent gates and root GO.
Solver helpers are copied unchanged from the independently reviewed HOD
uncapped runner; they bind this module's separate OUT, not the old arm.
"""
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
from research8h_fresh_january_weeks import native_rows, roster
from research8h_hour_of_day import bit_equal, local_sources
from research8h_seasonal_reference import physical_check
from research8h_seasonal_transfer import energy, transitions
from research8h_seasonal_uncapped import check_manifest, exact_point_check
from research8h_service_network_mip import unpack
from research8h_u_only_continuation import audit_projection
from temporal_lp_certificate import check_vector, digest, save
from v8r1_rts_seasonal import load_model

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/"results/research8h/fresh_january_weeks"
REFERENCES = SOURCE/"references"
TARGETS = SOURCE/"targets"
REVIEWS = ROOT/"results/research8h/fresh_reference_postrun_review"
FINAL_REVIEW = ROOT/"results/research8h/fresh_targets_postrun_review/final_ledger.json"
OUT = ROOT/"results/research8h/fresh_january_energy"
PROTOCOL = ROOT/"docs/research8h/FRESH_JANUARY_ENERGY_PROTOCOL.md"
SCHEDULE = {2:("seed_26093210","seed_26093211"),3:("seed_26093220","seed_26093221")}
IDENTITIES = ["week_2_identity","week_3_identity"]
CASES = [case for pair in SCHEDULE.values() for case in pair]
CUTOFF = datetime(2026,9,27,4,0,0,tzinfo=timezone.utc)
PHASE_SECONDS = 3600
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


def verified_review(path, status, hash_key):
    review = read(path)
    assert review["status"] == status
    checked = []
    for name, expected in review[hash_key].items():
        p = Path(name)
        if not p.is_absolute():
            p = ROOT/p
        assert p.is_file() and digest(p) == expected, str(p)
        checked.append(p)
    return review, [path,*checked]


def delete_cap(A,b,labels,budget,c):
    caps = np.flatnonzero(labels.family.eq("fossil_energy_cap").to_numpy())
    assert len(caps)==1 and not labels.family.str.contains("mean").any()
    cap = int(caps[0]); keep = np.delete(np.arange(A.shape[0]),cap)
    assert np.isneginf(b["row_lower"][cap]) and b["row_upper"][cap] == budget
    assert np.array_equal(A.getrow(cap).toarray().ravel(),c)
    reduced = A[keep].tocsr()
    bounds = {k:v[keep].copy() if k.startswith("row_") else v.copy() for k,v in b.items()}
    rows = labels.iloc[keep].copy().reset_index(drop=True)
    rows["source_row_0based"] = keep; rows["row"] = np.arange(len(rows))
    assert not rows.family.isin(["fossil_energy_cap","target_mean"]).any()
    assert all(bit_equal(bounds[k],b[k]) for k in ["column_lower","column_upper"])
    return reduced,bounds,rows,keep,cap


def check_model(A,b,integer,labels,meta,model,native_gen):
    assert A.shape == (34680,23016) and A.has_canonical_format
    assert np.isfinite(A.data).all() and len(labels)==A.shape[0]
    assert all(not np.isnan(v).any() for v in b.values())
    assert np.isfinite(b["column_lower"]).all() and np.isfinite(b["column_upper"]).all()
    assert np.all(b["row_lower"]<=b["row_upper"])
    assert np.all(b["column_lower"]<=b["column_upper"])
    assert not labels.family.str.contains("mean").any()
    assert not labels.family.eq("fossil_energy_cap").any()
    assert np.array_equal(np.flatnonzero(integer),np.arange(6888,18984))
    names,thermal,fossil,_ = roster(model)
    assert meta["unit_names"]==names and meta["thermal_unit_names"]==thermal
    assert meta["hours"]==168 and meta["individual_mean_constraints"]==0
    c,checked_fossil = objective_and_roster(meta,native_gen)
    assert checked_fossil==fossil and np.count_nonzero(c)==3864
    projected,proof = audit_projection(A,b,meta,labels,integer)
    assert np.array_equal(np.flatnonzero(projected),np.arange(6888,10920))
    return c,fossil,projected,proof


def archive(directory,A,b,integer,projected,c,labels,meta,parent,native,proof,keep):
    directory.mkdir()
    save_npz(directory/"matrix.npz",A)
    np.savez_compressed(directory/"bounds.npz",**b)
    np.savez_compressed(directory/"objective.npz",objective=c)
    np.savez_compressed(directory/"integrality.npz",integrality=projected)
    np.savez_compressed(directory/"original_integrality.npz",integrality=integer)
    np.savez_compressed(directory/"retained_parent_rows.npz",rows=keep)
    shutil.copyfile(parent/"native_inputs.npz",directory/"native_inputs.npz")
    if (parent/"permutation.csv").is_file():
        shutil.copyfile(parent/"permutation.csv",directory/"permutation.csv")
    labels.to_csv(directory/"row_metadata.csv.gz",index=False,compression="gzip")
    newmeta = {**meta,"rows":A.shape[0],"nonzeros":A.nnz,"binary_columns":int(projected.sum()),
        "original_binary_columns":int(integer.sum()),"energy_cap_constraints":0,
        "objective":"minimize native 23-fossil electrical MWh; no cap",
        "individual_mean_constraints":0,"source_directory":str(parent)}
    if "budget_MWh" in newmeta:
        newmeta["removed_source_cap_MWh"] = newmeta.pop("budget_MWh")
    save(directory/"model_metadata.json",newmeta)
    save(directory/"projection_audit.json",proof)
    baseline,_,_ = exact_bound(A,b,c,np.zeros(A.shape[0]))
    save(directory/"zero_dual_baseline.json",baseline)
    assert all(bit_equal(v,arrays(directory/"native_inputs.npz")[k]) for k,v in native.items())


def prepare(source_v3):
    # Read and validate closed parent gates before creating the new output tree.
    final,review_paths = verified_review(FINAL_REVIEW,"INDEPENDENT_FRESH_TARGET_FINAL_REVIEW_PASS","replayed_output_hashes")
    assert final["ordinary_denominator"]==4 and final["all_hashes_unchanged"]
    assert read(TARGETS/"completion.json")["intended_ordinary_cases"]==4
    parents = []
    for parent in [REFERENCES,TARGETS]:
        frozen = read(parent/"prepared_freeze.json")
        assert frozen["source_v3"]==str(source_v3.resolve())
        assert digest(parent/"input_manifest.csv")==frozen["manifest_sha256"]
        assert read(parent/"final_manifest_check.json")["pass"]
        parents.append({"directory":str(parent),**check_manifest(parent/"input_manifest.csv")})
    assert final["manifest_sha256"]==digest(TARGETS/"input_manifest.csv")
    outcomes = read(TARGETS/"outcomes.json")
    assert [x["case"] for x in outcomes]==CASES
    assert [x["week"] for x in outcomes]==[2,2,3,3]
    ref_results = {r["week"]:r for r in read(REFERENCES/"summary.json")}
    assert set(ref_results)=={2,3}
    assert all(r["verdict"]=="VERIFIED_REFERENCE_EXPANDED_MODEL" for r in ref_results.values())
    reference_reviews = {}
    for week in SCHEDULE:
        reviewed,paths = verified_review(REVIEWS/f"week_{week}.json",
            "INDEPENDENT_EXPANDED_BINARY_REFERENCE_PASS","replayed_files_sha256")
        assert reviewed["all_input_and_result_hashes_unchanged"]
        reference_reviews[week]=reviewed;review_paths.extend(paths)
    OUT.mkdir(parents=True,exist_ok=False)
    save(OUT/"freeze_before_preparation.json",{"utc":datetime.now(timezone.utc).isoformat(),
        "source_sha256":digest(Path(__file__)),"protocol_sha256":digest(PROTOCOL),
        "target_cases":CASES,"identity_cases":IDENTITIES,"optimization_calls":0})
    save(OUT/"parent_manifest_checks.json",parents)
    save(OUT/"parent_outcomes_context.json",{"outcomes":outcomes,
        "all_four_selected_without_label_filtering":True,"new_uncapped_outcomes_not_yet_computed":True})
    model=load_model(source_v3)
    gen_paths=list((source_v3/"raw").rglob("gen.csv"));assert len(gen_paths)==1
    native_gen=pd.read_csv(gen_paths[0],keep_default_na=False).to_dict("records")
    paths=[PROTOCOL,*local_sources(Path(__file__)),*review_paths,
        source_v3/"code/dscgrid_model.py",*sorted((source_v3/"raw").rglob("*.csv"))]
    paths.extend(p for parent in [REFERENCES,TARGETS] for p in parent.rglob("*") if p.is_file())
    prepared=[];reference_bindings=[]
    for week,cases in SCHEDULE.items():
        parent=REFERENCES/f"week_{week}"
        A,b,integer,labels,meta,native=load_case(parent)
        c,fossil,projected,proof=check_model(A,b,integer,labels,meta,model,native_gen)
        assert bit_equal(arrays(parent/"objective.npz")["objective"],c)
        fresh,nodal,hours,adapter=native_rows(model,(week-1)*168)
        assert all(bit_equal(fresh[k],native[k]) for k in fresh)
        assert bit_equal(nodal,native["nodal"])
        vector=arrays(parent/"recovered_vector.npz")["vector"]
        p,u,y,z,theta=unpack(vector,168,41,24,24)
        exact=exact_point_check(A,b,vector,integer)
        physical=physical_check(model,p,u,y,z,theta,native["pmin"],native["pmax"],native["net"],
            native["rows"],native["nodal"],fossil)
        assert exact["expanded_pass"] and physical["pass"]
        e=energy(p,fossil)
        assert e==from_rat(ref_results[week]["fossil_energy"])
        assert e==from_rat(reference_reviews[week]["exact_fossil_MWh"])
        ratio=Fraction(101,100)*e;budget=-((-ratio.numerator)//ratio.denominator)
        assert budget==read(TARGETS/f"week_{week}_cap.json")["budget_MWh"]
        ci=TARGETS/f"week_{week}_identity"
        ca,cb,cmask,cl,cm,cn=load_case(ci)
        ra,rb,rl,rkeep,cap=delete_cap(ca,cb,cl,budget,c)
        assert ra.shape==A.shape and (ra!=A).nnz==0
        assert all(bit_equal(rb[k],b[k]) for k in b)
        assert np.array_equal(cmask,integer)
        assert all(bit_equal(native[k],cn[k]) for k in native)
        assert rl[["family","hour_0based","uid"]].equals(labels[["family","hour_0based","uid"]])
        case=f"week_{week}_identity";directory=OUT/case
        archive(directory,A,b,integer,projected,c,labels,meta,parent,native,proof,np.arange(A.shape[0]))
        shutil.copyfile(parent/"recovered_vector.npz",directory/"reference_upper_vector.npz")
        save(directory/"native_adapter_check.json",adapter)
        bound={"case":case,"week":week,"reference_upper_MWh":rational(e),
            "reference_exact_point_check":exact,"reference_native_no_cap_check":physical,
            "reference_point_sha256":digest(parent/"recovered_vector.npz"),
            "same_uncapped_reference_model":True,"capped_identity_matches_after_only_cap_deletion":True,
            "source_cap_MWh":budget,"new_identity_MIP_calls":0}
        save(directory/"reference_binding.json",bound);reference_bindings.append(bound)
        prepared.append({"case":case,"week":week,"role":"identity","parent":str(parent)})
        for case in cases:
            target=TARGETS/case
            ta,tb,ti,tl,tm,tn=load_case(target)
            tc,tf=objective_and_roster(tm,native_gen)
            assert bit_equal(tc,c) and tf==fossil and tm["budget_MWh"]==budget
            reduced,bb,ll,keep,cap=delete_cap(ta,tb,tl,budget,c)
            cc,ff,tproject,tproof=check_model(reduced,bb,ti,ll,tm,model,native_gen)
            assert bit_equal(cc,c) and ff==fossil
            order=tn["source_hour"]
            assert np.array_equal(np.sort(order),np.arange(168))
            assert np.array_equal(order[:48],np.arange(48)) and np.array_equal(order[120:],np.arange(120,168))
            assert np.array_equal(order%24,np.arange(168)%24)
            assert all(bit_equal(tn[k],native[k][order]) for k in ["pmin","pmax","net","rows","nodal"])
            pd_order=pd.read_csv(target/"permutation.csv")
            assert np.array_equal(pd_order["source_hour_0based"].to_numpy(int),order)
            assert np.array_equal(pd_order["native_row_0based"].to_numpy(int),tn["rows"])
            directory=OUT/case
            archive(directory,reduced,bb,ti,tproject,c,ll,tm,target,tn,tproof,keep)
            record={"case":case,"week":week,"role":"target","parent":str(target),
                "deleted_row_0based":cap,"deleted_family":"fossil_energy_cap","removed_cap_MWh":budget,
                "no_other_matrix_or_bound_change":True,"no_mean_rows":True,
                "complete_107_coordinate_packages_and_native_rows_preserved":True,
                "native_and_permutation_file_bytes_unchanged":True,
                "objective_equals_native_roster_and_deleted_cap":True,
                "source_matrix_sha256":digest(target/"matrix.npz"),"source_bounds_sha256":digest(target/"bounds.npz"),
                "source_integrality_sha256":digest(target/"integrality.npz"),"projected_binary_columns":4032,
                "original_binary_columns":12096,"selected_independently_of_capped_label":True}
            save(directory/"model_binding.json",record);prepared.append(record)
    save(OUT/"reference_bindings.json",reference_bindings)
    save(OUT/"prepared_cases.json",prepared)
    paths.extend(p for p in OUT.rglob("*") if p.is_file())
    manifest=[{"path":str(p.resolve()),"sha256":digest(p),"bytes":p.stat().st_size} for p in dict.fromkeys(paths)]
    pd.DataFrame(manifest).to_csv(OUT/"input_manifest.csv",index=False)
    save(OUT/"prepared_freeze.json",{"utc":datetime.now(timezone.utc).isoformat(),"target_cases":CASES,
        "identity_cases":IDENTITIES,"source_sha256":digest(Path(__file__)),"protocol_sha256":digest(PROTOCOL),
        "source_v3":str(source_v3.resolve()),"manifest_sha256":digest(OUT/"input_manifest.csv"),
        "bound_files":len(manifest),"max_identity_LP_calls":2,"max_target_MIP_calls":4,"max_target_LP_calls":4,
        "MIP_seconds":600,"LP_seconds":60,"MIP_guard_seconds":605,"LP_guard_seconds":65,
        "phase_seconds":PHASE_SECONDS,"cutoff_utc":CUTOFF.isoformat(),"phase_starts_before_entry_validation":True,
        "order":"identity LPs; all target MIPs; all target LPs","new_identity_MIP_calls":0,"optimization_calls":0,
        "requires_independent_prepared_PASS_and_explicit_root_GO":True})
    print(json.dumps({"event":"PREPARED_NO_SOLVES","bound_files":len(manifest),
        "manifest_sha256":digest(OUT/"input_manifest.csv")}),flush=True)


def lower_bound(case,lps):
    baseline=from_rat(read(OUT/case/"zero_dual_baseline.json")["expanded_lower_bound_MWh"])
    fresh=from_rat(lps[case]["expanded_lower_MWh"]) if "expanded_lower_MWh" in lps[case] else None
    return max(baseline,fresh) if fresh is not None else baseline


def finalize_bounds(mips,lps):
    identities={}
    for bound in read(OUT/"reference_bindings.json"):
        case=bound["case"];lower=lower_bound(case,lps);upper=from_rat(bound["reference_upper_MWh"])
        assert 0<upper and lower<=upper, "Reference exact lower/upper contradiction"
        identities[bound["week"]]={"case":case,"lower_MWh":rational(lower),"upper_MWh":rational(upper),
            "LP_lower_bound_status":lps[case]["new_lower_bound_status"],"upper_witness_unchanged":True}
    save(OUT/"identity_energy_bounds.json",identities)
    rows=[]
    for week,cases in SCHEDULE.items():
        li=from_rat(identities[week]["lower_MWh"]);ui=from_rat(identities[week]["upper_MWh"])
        for case in cases:
            lower=lower_bound(case,lps)
            upper=from_rat(mips[case]["verified_upper_MWh"]) if "verified_upper_MWh" in mips[case] else None
            record={"case":case,"week":week,"lower_MWh":rational(lower),
                "upper_MWh":None if upper is None else rational(upper),
                "identity_lower_MWh":rational(li),"identity_reference_upper_MWh":rational(ui),
                "MIP_verdict":mips[case]["verdict"],"LP_lower_bound_status":lps[case]["new_lower_bound_status"],
                "upper_status":"NO_UPPER" if upper is None else "VERIFIED_BINARY_UPPER",
                "finite_uncapped_feasibility_established":upper is not None,
                "scope":"uncapped uniformly expanded original-binary models; original weekly reference upper retained",
                "positive_lower_penalty_necessary_if_target_nonempty":bool(lower>ui)}
            if upper is not None:
                if lower>upper:
                    save(OUT/"fatal_bound_contradiction.json",record)
                    raise AssertionError("Target exact lower exceeds accepted binary upper")
                record["optimum_difference_MWh"]={"lower":rational(lower-ui),"upper":rational(upper-li)}
                record["target_optimum_excess_over_chosen_incumbent_MWh"]={"lower":rational(lower-ui),"upper":rational(upper-ui)}
                record["strictly_positive_optimum_difference_certified"]=bool(lower>ui)
                if li>0 and lower>0:
                    lo,hi=lower/ui-1,upper/li-1
                    record["optimal_relative_penalty"]={"lower":rational(lo),"upper":rational(hi)}
                    record["optimal_relative_penalty_percent"]={"lower":rational(100*lo),"upper":rational(100*hi)}
                else:
                    record["relative_interval_status"]="NOT_REPORTED_NONPOSITIVE_LOWER_BOUND"
            else:
                record["difference_interval_status"]="NOT_REPORTED_NO_FINITE_BINARY_UPPER"
                record["relative_interval_status"]="NOT_REPORTED_NO_FINITE_BINARY_UPPER"
            rows.append(record)
    assert [r["case"] for r in rows]==CASES
    save(OUT/"energy_brackets.json",rows)
    return rows


def run_prepared(source_v3):
    invocation=datetime.now(timezone.utc);phase=time.perf_counter()
    freeze=read(OUT/"prepared_freeze.json")
    assert freeze["target_cases"]==CASES and freeze["identity_cases"]==IDENTITIES
    assert freeze["source_v3"]==str(source_v3.resolve())
    assert digest(Path(__file__))==freeze["source_sha256"] and digest(PROTOCOL)==freeze["protocol_sha256"]
    assert digest(OUT/"input_manifest.csv")==freeze["manifest_sha256"]
    before=check_manifest(OUT/"input_manifest.csv")
    with (OUT/"execution_started.json").open("x",encoding="utf-8") as stream:
        json.dump({"invocation_utc":invocation.isoformat(),"utc_after_validation":datetime.now(timezone.utc).isoformat(),
            "pre_execution_hash_check":before,"max_identity_LP_calls":2,"max_target_MIP_calls":4,
            "max_target_LP_calls":4,"new_identity_MIP_calls":0},stream,indent=2)
    save(OUT/"allocation_started.json",{"utc":invocation.isoformat(),"perf_counter":phase,
        "soft_phase_seconds":PHASE_SECONDS,"phase_starts_before_entry_validation_and_native_loading":True,
        "cutoff_utc":CUTOFF.isoformat()})
    model=load_model(source_v3);decisions=[];mips={};lps={}
    def allowed(kind,case,guard):
        now=datetime.now(timezone.utc)
        phase_left=PHASE_SECONDS-(time.perf_counter()-phase);cutoff_left=(CUTOFF-now).total_seconds()
        admitted=min(phase_left,cutoff_left)>=guard
        reason="ADMITTED" if admitted else "NOT_RUN_CUTOFF" if cutoff_left<guard else "NOT_RUN_BUDGET"
        decisions.append({"kind":kind,"case":case,"utc":now.isoformat(),"phase_remaining_s":phase_left,
            "cutoff_remaining_s":cutoff_left,"guard_s":guard,"admitted":admitted,"reason":reason})
        save(OUT/"launch_decisions.json",decisions)
        return admitted
    for case in IDENTITIES:
        lps[case]=run_lp(OUT/case,case,lambda case=case:allowed("IDENTITY_LP",case,65))
        save(OUT/"lp_results.json",lps)
        print(json.dumps({"stage":"IDENTITY_LP","case":case,"status":lps[case]["new_lower_bound_status"]}),flush=True)
    for case in CASES:
        mips[case]=run_mip(model,OUT/case,case,lambda case=case:allowed("TARGET_MIP",case,605))
        save(OUT/"mip_results.json",mips)
        print(json.dumps({"stage":"TARGET_MIP","case":case,"verdict":mips[case]["verdict"],"elapsed_s":mips[case]["elapsed_s"]}),flush=True)
    for case in CASES:
        lps[case]=run_lp(OUT/case,case,lambda case=case:allowed("TARGET_LP",case,65))
        save(OUT/"lp_results.json",lps)
        print(json.dumps({"stage":"TARGET_LP","case":case,"status":lps[case]["new_lower_bound_status"]}),flush=True)
    rows=finalize_bounds(mips,lps)
    save(OUT/"final_manifest_check.json",check_manifest(OUT/"input_manifest.csv"))
    ended=datetime.now(timezone.utc);elapsed=time.perf_counter()-phase
    save(OUT/"completion.json",{"utc":ended.isoformat(),"ordinary_denominator":4,
        "identity_LP_calls":sum(lps[k]["optimization_calls"] for k in IDENTITIES),
        "target_LP_calls":sum(lps[k]["optimization_calls"] for k in CASES),
        "target_MIP_calls":sum(r["optimization_calls"] for r in mips.values()),"new_identity_MIP_calls":0,
        "phase_elapsed_s":elapsed,"soft_allocation_s":PHASE_SECONDS,"soft_allocation_overrun_s":max(0.,elapsed-PHASE_SECONDS),
        "UTC_cutoff_overrun_s":max(0.,(ended-CUTOFF).total_seconds()),
        "actual_MIP_seconds":sum(r["elapsed_s"] for r in mips.values()),"actual_LP_seconds":sum(r["elapsed_s"] for r in lps.values()),
        "solver_soft_overrun_s":sum(max(0.,r["elapsed_s"]-600) for r in mips.values())+sum(max(0.,r["elapsed_s"]-60) for r in lps.values()),
        "accepted_target_uppers":sum(r["finite_uncapped_feasibility_established"] for r in rows),
        "all_frozen_hashes_unchanged":True,"exact_optimality_claim":False,"independent_postrun_replay_required":True})





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


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-v3",type=Path,required=True)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare-only",action="store_true");mode.add_argument("--run-prepared",action="store_true")
    args=parser.parse_args()
    if args.prepare_only:prepare(args.source_v3)
    else:run_prepared(args.source_v3)
