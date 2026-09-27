"""Prospective paired-world common-commitment test; separate prepare/run gates."""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.metadata
import importlib.util
import io
import json
import math
from pathlib import Path
import struct
import sys
import time
from types import SimpleNamespace

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/research_next/common_commitment"
PRE = OUT / "prepared"
RUN = OUT / "run01"
PROTOCOL = ROOT / "docs/research_next/COMMON_COMMITMENT_PROTOCOL.md"
KERNEL = ROOT / "src/research8h_standalone_verify.py"
KERNEL_SHA = "708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f"
NATIVE_HELPER = ROOT / "src/research8h_rational_witness_check.py"
NATIVE_HELPER_SHA = "9cb836d420308a2ffc5b6e50e78cb565a823d5b65d1223c0f53d98910de5680d"
GEN = ROOT / "reproducibility/native_sources/rts_inputs/raw/RTS-GMLC_v0.2.3/gen.csv"
GEN_SHA = "988466f29132b73739de60c9204dd4a2a9ceb0adf572e5966c086611272f4068"
WORLDS = ("identity", "days_321")
SOURCES = (ROOT / "results/research8h/hour_of_day/january_identity", ROOT / "results/research8h/day_blocks/days_321")
HISTORICAL = ((ROOT / "results/research8h/hour_of_day/input_manifest.csv", "078082667f83322d3540ad3ac215ebcc996d0d31b04fd52bfa75c1d2fd814fcc"),
              (ROOT / "results/research8h/day_blocks/input_manifest.csv", "5f15b13ce9b15abb1ff6256a4e10fc568ab5384e01a324160b0e522b31c8927d"))
PAYLOADS = ("matrix.npz", "bounds.npz", "integrality.npz", "model_metadata.json", "native_inputs.npz", "permutation.csv", "row_metadata.csv.gz")
SELECTION = (("results/research_next/whole_day_observation_preflight/run01/outcomes.json", "094a603e382a2f4d4b0fd6dd38f2a889ac664e46fea16389d3b226e0339f0bce"),
             ("results/research_next/whole_day_observation_preflight/INDEPENDENT_RESULT_REVIEW.json", "67ec0ae2a75e5c1b239143b5f63f3bca317f4d6f2ec2e0ac4e1b30143a3a441d"))
TAU = Q.from_float(1e-5)
PHASE = 1200.0
OPTIONS = {"mip": dict(time_limit=600.0, threads=1, random_seed=0, presolve="on", mip_rel_gap=1e-8),
           "lp": dict(time_limit=60.0, threads=1, random_seed=0, presolve="off", solver="simplex")}

def require(ok, message):
    if not ok:
        raise ValueError(message)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as f:
        json.dump(value, f, indent=2, allow_nan=False); f.write("\n")

def utc():
    return datetime.now(timezone.utc).isoformat()

def rat(value):
    return dict(numerator=str(value.numerator), denominator=str(value.denominator), approximate=float(value))

def binding(path):
    path = Path(path).resolve()
    return dict(path=str(path), bytes=path.stat().st_size, sha256=sha(path))

def capture(path, expected_sha, expected_size=None):
    """Validate, bind and copy one identical byte snapshot."""
    path = Path(path).resolve()
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    require(digest == expected_sha and (expected_size is None or len(data) == expected_size), "Captured input differs: " + str(path))
    return data, dict(path=str(path), bytes=len(data), sha256=digest)

def validate_bindings(items):
    require(len({x["path"].casefold() for x in items}) == len(items), "Duplicate binding")
    for item in items:
        require(binding(item["path"]) == item, "Changed input: " + item["path"])

def module(path, expected, name):
    require(sha(path) == expected, "Reviewed helper changed")
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result

def kernel():
    return module(KERNEL, KERNEL_SHA, "common_commitment_exact_kernel")

def mask_at(v, directory, cols):
    a = v.read_npz(Path(directory)/"integrality.npz", ("integrality",))["integrality"]
    return tuple(v.vector(a, ("|u1",), cols, "full original mask"))

def merge_models(a, b, mask):
    """Pure coordinate identification, also exercised on invented structures."""
    require(a.cols == b.cols == len(mask) and all(x in (0, 1) for x in mask), "Mask/coordinate mismatch")
    private = [j for j, flag in enumerate(mask) if not flag]
    maps = [list(range(a.cols)), [None]*a.cols]
    for j, flag in enumerate(mask):
        if flag:
            maps[1][j] = j
    for k, j in enumerate(private):
        maps[1][j] = a.cols+k
    lower, upper = list(a.lower), list(a.upper)
    for j, flag in enumerate(mask):
        if flag:
            lower[j], upper[j] = max(a.lower[j], b.lower[j]), min(a.upper[j], b.upper[j])
            require(lower[j] <= upper[j], "Empty shared nominal box")
    lower.extend(b.lower[j] for j in private); upper.extend(b.upper[j] for j in private)
    data, indices, indptr = [], [], [0]
    row_lower, row_upper, origins = [], [], []
    for world, model in enumerate((a, b)):
        require(len(set(maps[world])) == model.cols, "Noninjective per-world map")
        for row in range(model.rows):
            entries = sorted((maps[world][model.indices[e]], model.data[e]) for e in range(model.indptr[row], model.indptr[row+1]))
            require(len({j for j, _ in entries}) == len(entries), "Merged duplicate coefficient")
            indices.extend(j for j, _ in entries); data.extend(c for _, c in entries); indptr.append(len(data))
            row_lower.append(model.row_lower[row]); row_upper.append(model.row_upper[row])
            origins.append([world, row])
    model = dict(rows=a.rows+b.rows, cols=a.cols+len(private), data=tuple(data), indices=tuple(indices), indptr=tuple(indptr),
                 lower=tuple(lower), upper=tuple(upper), row_lower=tuple(row_lower), row_upper=tuple(row_upper))
    return model, maps, tuple(mask)+(0,)*len(private), origins

def projected_candidates(raw, model):
    require(len(raw) == model.rows and all(math.isfinite(x) for x in raw), "Invalid raw ray")
    result = []
    for sign, label in ((1, "positive"), (-1, "negative")):
        signed = {i:Q(sign*x) for i,x in enumerate(raw) if x}
        invalid = [i for i,d in signed.items() if not math.isfinite(model.row_lower[i] if d > 0 else model.row_upper[i])]
        result.append((label+"_raw", signed, invalid))
        result.append((label+"_sign_projected", {i:d for i,d in signed.items() if i not in set(invalid)}, invalid))
    return result

def source_labels(directory):
    with gzip.open(Path(directory)/"row_metadata.csv.gz", "rt", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))

def validate_original(v, directory, meta, model, mask, spec):
    require((model.rows, model.cols, sum(mask)) == (34681, 23016, 12096), "Original full model dimensions")
    require(mask == tuple(int(6888 <= j < 18984) for j in range(23016)), "Original U/Y/Z full mask")
    require(meta["offsets"] == dict(P=0,U=6888,Y=10920,Z=14952,theta=18984), "Offsets")
    require((meta["hours"],meta["units"],meta["thermal_units"],meta["buses"]) == (168,41,24,24), "Coordinate dimensions")
    require(meta["budget_MWh"] == 23195 and meta["individual_mean_constraints"] == 0, "Cap or mean scope")
    require([r["uid"] for r in spec] == meta["unit_names"], "Native generator roster")
    require(len(meta["fossil_units"]) == 23 and set(meta["fossil_units"]) == set(meta["thermal_unit_names"])-{"121_NUCLEAR_1"}, "Fossil roster")
    arrays = v.read_npz(Path(directory)/"native_inputs.npz", ("pmin","pmax","net","rows","source_hour","nodal"))
    require(arrays["pmin"].shape == arrays["pmax"].shape == (168,41) and arrays["nodal"].shape == (168,24), "Native array shapes")
    require(arrays["net"].shape == arrays["rows"].shape == arrays["source_hour"].shape == (168,), "Native coordinates")
    require(all(arrays[k].dtype == "<f8" and all(math.isfinite(x) for x in arrays[k].values) for k in ("pmin","pmax","net","nodal")), "Finite native arrays")
    labels = source_labels(directory)
    require(len(labels) == model.rows and [int(r["row"]) for r in labels] == list(range(model.rows)), "Original row labels")
    caps, nodals, balances = 0, 0, 0
    expected_cap = {41*t+meta["unit_names"].index(name):1.0 for t in range(168) for name in meta["fossil_units"]}
    for i,label in enumerate(labels):
        family, t = label["family"], int(label["hour_0based"])
        if family == "fossil_energy_cap":
            caps += 1
            terms = {model.indices[e]:model.data[e] for e in range(model.indptr[i],model.indptr[i+1])}
            require(terms == expected_cap and model.row_lower[i] == -math.inf and model.row_upper[i] == 23195, "Original cap row")
        elif family == "nodal_balance":
            nodals += 1
            bus = meta["bus_ids"].index(int(label["uid"]))
            require(model.row_lower[i] == model.row_upper[i] == arrays["nodal"].values[24*t+bus], "Nodal native endpoint")
        elif family == "aggregate_balance":
            balances += 1
            require(model.row_lower[i] == model.row_upper[i] == arrays["net"].values[t], "Aggregate native endpoint")
    require((caps,nodals,balances) == (1,4032,168), "Complete original network/budget rows")
    return dict(rows=model.rows, columns=model.cols, binaries=sum(mask), cap_rows=caps, native_nodal_rows=nodals,
                aggregate_rows=balances, native48hour_units=[x["uid"] for x in spec if max(x["minimum_up"],x["minimum_down"]) == 48])

def native_check(v, point, directory, metadata, spec):
    """Exact supplemental native checks; original DC matrix replay is separate."""
    arrays = v.read_npz(Path(directory)/"native_inputs.npz", ("pmin","pmax","net","rows","source_hour","nodal"))
    x = tuple(Q(value) for value in point)
    names = metadata["unit_names"]; thermal = [names.index(n) for n in metadata["thermal_unit_names"]]
    maximum, violations, first, energy = Q(0), 0, [], Q(0)
    def record(gap, rule, t, unit):
        nonlocal maximum, violations
        maximum = max(maximum, gap)
        if gap > TAU:
            violations += 1
            if len(first) < 20: first.append(dict(rule=rule,hour=t,unit=unit,gap=rat(gap)))
    def discrete(ok,rule,t,unit):
        record(Q(0) if ok else Q(1),rule,t,unit)
    for t in range(168):
        p = x[41*t:41*(t+1)]
        record(abs(sum(p,Q(0))-Q(arrays["net"].values[t])),"aggregate",t,"ALL")
        for j,power in enumerate(p):
            low, high = Q(arrays["pmin"].values[41*t+j]),Q(arrays["pmax"].values[41*t+j])
            record(max(-power,power-high,Q(0)),"availability",t,j)
            if spec[j]["category"] == "Hydro": record(abs(power-low),"hydro_fixed",t,j)
            if names[j] in metadata["fossil_units"]: energy += power
        for k,j in enumerate(thermal):
            u,y,z = (x[offset+24*t+k] for offset in (6888,10920,14952))
            discrete(all(a in (0,1) for a in (u,y,z)),"binary",t,j)
            low,high = Q(arrays["pmin"].values[41*t+j]),Q(arrays["pmax"].values[41*t+j])
            record(max(low*u-p[j],p[j]-high*u,Q(0)),"committed_output",t,j)
            if t == 0:
                discrete(y == z == 0,"initial_transitions",t,j)
                continue
            previous = x[6888+24*(t-1)+k]; change = u-previous
            discrete(y == max(change,0) and z == max(-change,0),"canonical_transitions",t,j)
            if change:
                length = spec[j]["minimum_up" if change > 0 else "minimum_down"]
                discrete(all(x[6888+24*h+k] == u for h in range(t,min(168,t+length))),"native_residence",t,j)
            if u == previous == 1:
                rate = Q(int(spec[j]["hourly_rational"]["numerator"]),int(spec[j]["hourly_rational"]["denominator"]))
                record(max(abs(p[j]-x[41*(t-1)+j])-rate,Q(0)),"native_on_on_ramp",t,j)
    record(max(energy-Q(23195),Q(0)),"23_fossil_cap",-1,"ALL")
    return dict(expanded_pass=violations==0,tau=rat(TAU),maximum_violation=rat(maximum),violations=violations,
                first_violations=first,exact_fossil_energy=rat(energy),cap_MWh=23195,
                native_network="Every unchanged original DC row and theta box checked by separate full exact model replay",
                ramp_conversion="binary64(MW/min * 60.0), then rationalized",nominal_feasibility_claim=False)

def prepare():
    import numpy as np
    from scipy.sparse import csr_matrix, save_npz
    require(not PRE.exists() and not RUN.exists(), "Fresh preparation only")
    input_bindings = [binding(__file__),binding(PROTOCOL),binding(KERNEL),binding(NATIVE_HELPER)]
    gen_bytes, gen_binding = capture(GEN, GEN_SHA)
    input_bindings.append(gen_binding)
    selection_data = []
    for rel,expected in SELECTION:
        data, captured = capture(ROOT/rel, expected)
        input_bindings.append(captured); selection_data.append(json.loads(data))
    selected = [r for r in selection_data[0]["comparisons"] if r["week"]==1 and r["role"]=="target" and r["primary_plus_hindex_outcome"]=="EQUAL"]
    require(len(selected)==1 and selected[0]["day_order"]==[3,2,1],"Posthoc selection declaration differs")
    v = kernel(); native = module(NATIVE_HELPER,NATIVE_HELPER_SHA,"common_commitment_native_spec")
    PRE.mkdir(parents=True)
    save(PRE/"preparation_started.json",dict(utc=utc(),source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),optimizer_calls=0))
    copied, models, masks, metas, original_checks = [], [], [], [], []
    (PRE/"gen.csv").write_bytes(gen_bytes)
    for world,source,(historical,digest) in zip(WORLDS,SOURCES,HISTORICAL):
        manifest_bytes, manifest_binding = capture(historical,digest)
        input_bindings.append(manifest_binding)
        entries = list(csv.DictReader(io.StringIO(manifest_bytes.decode("utf-8-sig"),newline="")))
        index = {str(Path(r["path"]).resolve()).casefold():r for r in entries}
        require(len(index)==len(entries),"Duplicate historical manifest path")
        directory = PRE/world; directory.mkdir()
        for name in PAYLOADS:
            p = source/name; require(str(p.resolve()).casefold() in index,"Missing historical input binding")
            r=index[str(p.resolve()).casefold()]
            data, captured = capture(p,r["sha256"],int(r["bytes"]))
            input_bindings.append(captured); (directory/name).write_bytes(data); copied.append(str(directory/name))
        m=v.load_model(directory); mask=mask_at(v,directory,m.cols); meta=read(directory/"model_metadata.json")
        spec=native.native_spec(PRE/"gen.csv",meta); save(directory/"native_spec.json",spec)
        original_checks.append(validate_original(v,directory,meta,m,mask,spec))
        models.append(m); masks.append(mask); metas.append(meta)
    require(masks[0]==masks[1],"World mask mismatch")
    require(all(metas[0][k]==metas[1][k] for k in ("offsets","unit_names","thermal_unit_names","bus_ids","fossil_units")),"World coordinate names differ")
    for j,flag in enumerate(masks[0]):
        if flag: require((models[0].lower[j],models[0].upper[j])==(models[1].lower[j],models[1].upper[j]),"Scientific shared binary bounds differ")
    merged,maps,mask,origins=merge_models(*models,masks[0]); joint=v.validate_model(v.Model(**merged))
    require((joint.rows,joint.cols,sum(mask))==(69362,33936,12096),"Joint dimensions")
    directory=PRE/"joint"; directory.mkdir()
    matrix=csr_matrix((np.array(joint.data),np.array(joint.indices),np.array(joint.indptr)),shape=(joint.rows,joint.cols))
    save_npz(directory/"matrix.npz",matrix)
    np.savez_compressed(directory/"bounds.npz",column_lower=np.array(joint.lower),column_upper=np.array(joint.upper),
                        row_lower=np.array(joint.row_lower),row_upper=np.array(joint.row_upper))
    np.savez_compressed(directory/"integrality.npz",integrality=np.array(mask,dtype=np.uint8))
    save(directory/"column_maps.json",dict(worlds=WORLDS,original_to_joint=maps,shared_original_columns=[j for j,f in enumerate(masks[0]) if f]))
    save(directory/"row_origins.json",dict(origins=origins))
    require(v.load_model(directory)==joint and mask_at(v,directory,joint.cols)==mask,"Serialized joint differs")
    save(PRE/"assembly_checks.json",dict(original_checks=original_checks,joint_rows=joint.rows,joint_columns=joint.cols,
         original_binary_coordinates=12096,new_model_family="coordinate-identified pair of original angle encodings",nominal_proposal=True,
         original_files_copied_unchanged=copied,posthoc_selected_collision=selected[0],optimizer_calls=0))
    runtime = dict(python=sys.version,executable=sys.executable,
                   packages={name:importlib.metadata.version(name) for name in ("numpy","scipy","highspy")})
    save(PRE/"plan.json",dict(worlds=WORLDS,sequence=["mip","lp"],options=OPTIONS,phase_seconds=PHASE,tau=rat(TAU),runtime=runtime,
         original_objective="zero feasibility",numeric_proposal_bounds="nominal",acceptance_bounds="exact uniform tau expansion",
         solver_calls=0,warm_starts=0,retries=0,source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL)))
    validate_bindings(input_bindings)
    generated=[binding(p) for p in PRE.rglob("*") if p.is_file()]
    all_bindings=input_bindings+generated
    save(PRE/"input_manifest.json",dict(files=all_bindings))
    validate_bindings(all_bindings)
    save(PRE/"prepared_freeze.json",dict(utc=utc(),source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),
         manifest_sha256=sha(PRE/"input_manifest.json"),bindings=len(all_bindings),joint_rows=69362,joint_columns=33936,
         shared_binaries=12096,optimizer_calls=0,independent_prepared_gate_and_execution_GO_required=True))

def load_prepared(expected):
    require(sha(PRE/"prepared_freeze.json")==expected,"External prepared freeze mismatch")
    freeze=read(PRE/"prepared_freeze.json")
    require(freeze["source_sha256"]==sha(__file__) and freeze["protocol_sha256"]==sha(PROTOCOL),"Frozen source/protocol changed")
    require(sha(PRE/"input_manifest.json")==freeze["manifest_sha256"],"Input manifest changed")
    bindings=read(PRE/"input_manifest.json")["files"]; validate_bindings(bindings)
    plan=read(PRE/"plan.json")
    require(plan["options"]==OPTIONS and plan["sequence"]==["mip","lp"] and plan["tau"]==rat(TAU) and plan["phase_seconds"]==PHASE,"Plan mismatch")
    v=kernel(); model=v.load_model(PRE/"joint"); mask=mask_at(v,PRE/"joint",model.cols)
    return v,model,mask,bindings

def numerical_model(model,mask,kind,highspy,np):
    lp=highspy.HighsLp(); lp.num_row_,lp.num_col_=model.rows,model.cols
    lp.col_cost_=np.zeros(model.cols); lp.col_lower_=np.array(model.lower); lp.col_upper_=np.array(model.upper)
    lp.row_lower_=np.array(model.row_lower); lp.row_upper_=np.array(model.row_upper)
    lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise
    lp.a_matrix_.num_row_,lp.a_matrix_.num_col_=model.rows,model.cols
    lp.a_matrix_.start_=np.array(model.indptr,dtype=np.int32); lp.a_matrix_.index_=np.array(model.indices,dtype=np.int32)
    lp.a_matrix_.value_=np.array(model.data)
    if kind=="mip": lp.integrality_=[highspy.HighsVarType.kInteger if f else highspy.HighsVarType.kContinuous for f in mask]
    return lp

def solve_one(v,model,mask,kind,phase,ledger):
    import highspy
    import numpy as np
    directory=RUN/kind; directory.mkdir()
    h=highspy.Highs(); options={**OPTIONS[kind],"log_to_console":False,"log_file":str((directory/"solver.log").resolve())}
    for key,value in options.items(): require(h.setOptionValue(key,value)==highspy.HighsStatus.kOk,"Rejected solver option")
    require(h.passModel(numerical_model(model,mask,kind,highspy,np))==highspy.HighsStatus.kOk,"Rejected numerical model")
    result=dict(kind=kind,verdict="UNKNOWN",calls_started=0,accepted_common_witness=False,accepted_joint_negative=False,options=options)
    remaining=PHASE-(time.perf_counter()-phase); needed=options["time_limit"]+5
    save(directory/"admission.json",dict(utc=utc(),remaining_seconds=remaining,required_seconds=needed,admitted=remaining>=needed))
    if remaining < needed:
        result["verdict"]="NOT_RUN_PHASE_GUARD"; save(directory/"result.json",result); return result
    save(directory/"call_ready.json",dict(utc=utc(),not_an_assertion_of_actual_call=True))
    if PHASE-(time.perf_counter()-phase) < needed:
        result["verdict"]="NOT_RUN_POST_WRITE_PHASE_GUARD"; save(directory/"result.json",result); return result
    clock=time.perf_counter(); ledger["current"].update(attempted=True,started_utc=utc()); ledger["attempted"]+=1
    ledger["calls"].append(ledger["current"])
    status=h.run(); elapsed=time.perf_counter()-clock
    ledger["returned"]+=1; ledger["current"].update(returned=True,ended_utc=utc(),elapsed_seconds=elapsed)
    solution=h.getSolution(); info=h.getInfo()
    result.update(calls_started=1,solver_version=h.version(),run_status=str(status),model_status=h.modelStatusToString(h.getModelStatus()),
                  actual_seconds=elapsed,soft_overrun_seconds=max(0,elapsed-options["time_limit"]),
                  value_valid=bool(solution.value_valid),dual_valid=bool(solution.dual_valid),
                  mip_node_count=int(info.mip_node_count),simplex_iterations=int(info.simplex_iteration_count))
    save(directory/"solver_returned.json",result)
    raw=np.array(solution.col_value,dtype=np.float64)
    np.savez_compressed(directory/"raw_solution.npz",vector=raw,row_value=np.array(solution.row_value),row_dual=np.array(solution.row_dual),col_dual=np.array(solution.col_dual))
    if kind=="mip" and solution.value_valid and len(raw)==model.cols and np.isfinite(raw).all():
        binary=np.array(mask,dtype=bool); rounded=np.rint(raw[binary])
        eligible=bool(np.isin(rounded,[0.,1.]).all()) and all(abs(Q(float(a))-Q(float(b)))<=TAU for a,b in zip(raw[binary],rounded))
        result["candidate_eligible"]=eligible
        if eligible:
            candidate=raw.copy(); candidate[binary]=rounded
            require(candidate[~binary].tobytes()==raw[~binary].tobytes(),"Continuous candidate changed")
            np.savez_compressed(directory/"candidate_vector.npz",vector=candidate)
            joint_check=v.check_point(model,candidate.tolist(),mask,TAU)
            maps=read(PRE/"joint/column_maps.json")["original_to_joint"]
            checks=[]; states=[]
            for world,mapping in zip(WORLDS,maps):
                original=v.load_model(PRE/world); original_mask=mask_at(v,PRE/world,original.cols)
                projected=[float(candidate[j]) for j in mapping]
                np.savez_compressed(directory/(world+"_vector.npz"),vector=np.array(projected))
                check=v.check_point(original,projected,original_mask,TAU)
                native=native_check(v,projected,PRE/world,read(PRE/world/"model_metadata.json"),read(PRE/world/"native_spec.json"))
                checks.append(dict(world=world,original=check,native=native))
                states.append([Q(projected[j]) for j,flag in enumerate(original_mask) if flag])
            common=states[0]==states[1] and all(s in (0,1) for s in states[0])
            accepted=joint_check["expanded_pass"] and common and all(c["original"]["expanded_pass"] and c["native"]["expanded_pass"] for c in checks)
            save(directory/"exact_candidate_checks.json",dict(joint=joint_check,worlds=checks,common_all12096_bits=common,
                 continuous_bytes_unchanged=True,accepted_common_witness=accepted,nominal_feasibility_claim=False))
            result.update(accepted_common_witness=accepted,verdict="VERIFIED_EXPANDED_COMMON_COMMITMENT" if accepted else "UNKNOWN_REJECTED_CANDIDATE")
    if kind=="lp":
        exists_status,exists=h.getDualRayExist()
        result.update(dual_ray_exist_status=str(exists_status),dual_ray_already_exists=bool(exists),ray_recovery_solves=0)
        if exists_status==highspy.HighsStatus.kOk and exists:
            ray_status,returned,ray=h.getDualRay()
            result.update(dual_ray_status=str(ray_status),ray_retrieved=bool(returned))
            if returned:
                raw_ray=tuple(map(float,ray)); np.savez_compressed(directory/"raw_ray.npz",multipliers=np.array(raw_ray))
                if len(raw_ray)==model.rows and all(map(math.isfinite,raw_ray)):
                    candidates=[]
                    for label,sparse,invalid in projected_candidates(raw_ray,model):
                        try: check=v.check_ray(model,sparse,TAU)
                        except v.InvalidInput as exc: check=dict(status="INVALID_CANDIDATE",expanded_pass=False,reason=str(exc))
                        candidates.append(dict(label=label,raw_inadmissible_rows=invalid,
                            multipliers=[dict(row=i,value_hex=float(d).hex()) for i,d in sorted(sparse.items())],verification=check,
                            model_bindings={name:sha(PRE/"joint"/name) for name in ("matrix.npz","bounds.npz","integrality.npz","column_maps.json","row_origins.json")},
                            input_manifest_sha256=sha(PRE/"input_manifest.json")))
                    save(directory/"ray_candidates.json",candidates)
                    result["accepted_joint_negative"]=any(c["verification"]["expanded_pass"] for c in candidates)
                    if result["accepted_joint_negative"]: result["verdict"]="CERTIFIED_NO_COMMON_COMMITMENT_IN_EXPANDED_JOINT_RELAXATION"
                else: result["invalid_returned_ray"]=True
    save(directory/"result.json",result)
    return result

def run_prepared(expected):
    phase=time.perf_counter(); require(not RUN.exists(),"Exactly one prospective execution")
    v,model,mask,bindings=load_prepared(expected)
    transport=[binding(PRE/"input_manifest.json"),binding(PRE/"prepared_freeze.json")]
    RUN.mkdir(); save(RUN/"execution_started.json",dict(utc=utc(),expected_freeze_sha256=expected,phase_seconds=PHASE,source_sha256=sha(__file__)))
    ledger=dict(attempted=0,returned=0,calls=[],current=None); outcomes=[]
    try:
        for kind in ("mip","lp"):
            ledger["current"]=dict(kind=kind,attempted=False,returned=False)
            result=solve_one(v,model,mask,kind,phase,ledger); outcomes.append(result)
            print(json.dumps(dict(kind=kind,verdict=result["verdict"],calls=result["calls_started"])),flush=True)
        require(not(any(x["accepted_common_witness"] for x in outcomes) and any(x["accepted_joint_negative"] for x in outcomes)),"Exact common point/ray contradiction")
        validate_bindings(bindings); validate_bindings(transport)
        require(sum(x["calls_started"] for x in outcomes)==ledger["attempted"]==ledger["returned"],"Call accounting mismatch")
        save(RUN/"outcomes.json",dict(outcomes=outcomes,pair_denominator=1,planned_calls=2,selection="posthoc unique first-week joint observation collision"))
        elapsed=time.perf_counter()-phase
        save(RUN/"completion.json",dict(utc=utc(),status="CLOSED_PENDING_INDEPENDENT_REVIEW",call_ledger=ledger,
             optimizer_calls=ledger["attempted"],phase_seconds=elapsed,phase_soft_overrun=max(0,elapsed-PHASE),
             all_frozen_bytes_unchanged=True,no_individual_world_solves=True,no_retries=True,nominal_feasibility_claim=False))
    except BaseException as exc:
        save(RUN/"execution_failure.json",dict(utc=utc(),error_type=type(exc).__name__,message=str(exc),call_ledger=ledger,
             partial_outputs_preserved=True,automatic_retry=False))
        raise

def self_test():
    checks=[]
    a=SimpleNamespace(rows=1,cols=2,data=(1.,-1.),indices=(0,1),indptr=(0,2),lower=(0.,0.),upper=(2.,1.),row_lower=(0.,),row_upper=(0.,))
    b=SimpleNamespace(**vars(a)); result,maps,mask,origins=merge_models(a,b,(0,1))
    def check(name,condition):
        require(condition,name); checks.append(name)
    check("one_shared_binary_two_private_dispatches",maps==[[0,1],[2,1]] and mask==(0,1,0) and result["cols"]==3)
    check("row_origin_and_coefficients",origins==[[0,0],[1,0]] and result["indices"]==(0,1,1,2) and result["data"]==(1.,-1.,-1.,1.))
    point=(1.,1.,1.)
    check("same_bits_recovered",[point[maps[w][1]] for w in range(2)]==[1.,1.])
    other=(0.5,1.,1.5)
    check("private_dispatch_not_accidentally_shared",other[maps[0][0]]!=other[maps[1][0]])
    b.lower=(0.,0.25); b.upper=(3.,0.75)
    result,_,_,_=merge_models(a,b,(0,1))
    check("shared_box_intersection",result["lower"][1]==0.25 and result["upper"][1]==0.75)
    q=Q(1,100)
    check("intersection_commutes_with_uniform_expansion",max(Q(a.lower[1])-q,Q(b.lower[1])-q)==Q(result["lower"][1])-q and min(Q(a.upper[1])+q,Q(b.upper[1])+q)==Q(result["upper"][1])+q)
    toy=SimpleNamespace(rows=2,row_lower=(0.,-math.inf),row_upper=(math.inf,1.))
    candidates=projected_candidates((1.,1.),toy)
    check("all_four_fixed_ray_recipes",[c[0] for c in candidates]==["positive_raw","positive_sign_projected","negative_raw","negative_sign_projected"])
    check("opposite_endpoint_projection",set(candidates[1][1])=={0} and set(candidates[3][1])=={1})
    OUT.mkdir(parents=True,exist_ok=True)
    save(OUT/"implementation_fixtures.json",dict(status="PASS_SYNTHETIC_ONLY",source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),
         checks=checks,fixture_count=len(checks),scientific_inputs_read=0,model_preparations=0,optimizer_calls=0))
    print(json.dumps(dict(status="PASS_SYNTHETIC_ONLY",fixture_count=len(checks))))

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-test",action="store_true"); group.add_argument("--prepare-only",action="store_true"); group.add_argument("--run-prepared",action="store_true")
    parser.add_argument("--expected-freeze-sha256")
    args=parser.parse_args()
    if args.self_test: self_test()
    elif args.prepare_only: prepare()
    else:
        require(args.expected_freeze_sha256 is not None,"Trusted external freeze hash required")
        run_prepared(args.expected_freeze_sha256)
