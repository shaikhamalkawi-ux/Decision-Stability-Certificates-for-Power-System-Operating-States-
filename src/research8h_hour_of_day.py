"""Prepare, then separately execute two January hour-of-day permutation tests."""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys
import time

sys.dont_write_bytecode = True
import numpy as np
import pandas as pd

from research8h_day_blocks import load_case, solve_mip
import research8h_seasonal_transfer as transfer
from research8h_seasonal_uncapped import check_manifest, exact_point_check, rational_record
from research8h_service_network_mip import build, unpack
from research8h_u_only_continuation import audit_projection
from temporal_lp_certificate import digest, save
from v8r1_rts_seasonal import load_model

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "results/research8h/seasonal_transfer"
OUTPUT = ROOT / "results/research8h/hour_of_day"
PROTOCOL = ROOT / "docs/research8h/HOUR_OF_DAY_PROTOCOL.md"
ORDINARY = [26093200, 26093201]
CONTROL = 26100200
CASES = [f"seed_{seed}" for seed in ORDINARY]
TOL = 1e-5
PHASE_SECONDS = 1200
MIP_GUARD_SECONDS = 305


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def bit_equal(left, right):
    left, right = np.asarray(left), np.asarray(right)
    return left.shape == right.shape and left.dtype == right.dtype and left.tobytes() == right.tobytes()


def local_sources(entry):
    """Resolve the static transitive import closure within src; no imports run."""
    pending, found = [entry.resolve()], set()
    while pending:
        path = pending.pop()
        if path in found:
            continue
        found.add(path)
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8-sig"))):
            names = []
            if isinstance(node, ast.Import):
                names = [x.name.split(".")[0] for x in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module.split(".")[0]]
            for name in names:
                candidate = ROOT / "src" / (name + ".py")
                if candidate.is_file():
                    pending.append(candidate.resolve())
    return sorted(found)


def generate_order(seed, commitment, control=False):
    rng = np.random.Generator(np.random.PCG64(seed))
    before = rng.bit_generator.state
    order = np.arange(168)
    groups = []
    if control:
        inventory = {}
        for t in range(48, 120):
            key = (t % 24, *[int(x) for x in commitment[t]])
            inventory.setdefault(key, []).append(t)
        for key in sorted(inventory):
            positions = np.asarray(inventory[key], dtype=int)
            chosen = rng.permutation(positions)
            order[positions] = chosen
            groups.append({"hour_of_day_0based":key[0], "identity_U_signature":list(key[1:]),
                           "destination_hours":positions.tolist(), "source_hours":chosen.tolist()})
        assert np.array_equal(commitment[order], commitment)
    else:
        for h in range(24):
            positions = np.asarray([48+h, 72+h, 96+h], dtype=int)
            chosen = rng.permutation(positions)
            order[positions] = chosen
            groups.append({"hour_of_day_0based":h, "destination_hours":positions.tolist(),
                           "source_hours":chosen.tolist()})
    assert np.array_equal(np.sort(order), np.arange(168))
    assert np.array_equal(order[:48], np.arange(48))
    assert np.array_equal(order[120:], np.arange(120,168))
    assert np.array_equal(order % 24, np.arange(168) % 24)
    for h in range(24):
        positions = np.asarray([48+h,72+h,96+h])
        assert np.array_equal(np.sort(order[positions]),positions)
    return order, {"seed":seed, "generator":"numpy.random.Generator(PCG64)",
        "numpy_version":np.__version__, "state_before":before, "state_after":rng.bit_generator.state,
        "group_order":"lexicographic (hour,U bits)" if control else "hour 0 through 23",
        "groups":groups, "redraws":0, "identity_draw_retained":bool(np.array_equal(order,np.arange(168)))}


def validate_structure(data, expected_names, expected_thermal, fossil):
    matrix,bounds,integer,meta,labels,nodal = data
    assert matrix.shape == (34681,23016) and nodal.shape == (168,24)
    assert meta["unit_names"] == expected_names and meta["thermal_unit_names"] == expected_thermal
    assert meta["individual_mean_constraints"] == 0 and meta["budget_MWh"] == 23195
    assert np.array_equal(np.flatnonzero(integer), np.arange(6888,18984))
    assert np.isfinite(bounds["column_lower"]).all() and np.isfinite(bounds["column_upper"]).all()
    assert not any("mean" in x["family"] for x in labels)
    caps = [i for i,x in enumerate(labels) if x["family"] == "fossil_energy_cap"]
    assert len(caps) == 1
    row = matrix.getrow(caps[0])
    expected = np.asarray([t*41+j for t in range(168) for j in fossil])
    assert np.array_equal(np.sort(row.indices), np.sort(expected)) and np.all(row.data == 1)
    assert bounds["row_upper"][caps[0]] == 23195 and np.isneginf(bounds["row_lower"][caps[0]])
    assert meta["fossil_units"] == [expected_names[j] for j in fossil]
    return caps[0]


def prepare(source_v3):
    OUTPUT.mkdir(parents=True, exist_ok=False)
    save(OUTPUT/"freeze_before_generation.json", {"utc":datetime.now(timezone.utc).isoformat(),
        "source_sha256":digest(Path(__file__)), "protocol_sha256":digest(PROTOCOL),
        "ordinary_seeds":ORDINARY, "control_seed":CONTROL, "optimization_calls":0})
    save(OUTPUT/"parent_manifest_check.json", check_manifest(SOURCE/"input_manifest.csv"))
    model = load_model(source_v3)
    names = model.dec["GEN UID"].tolist()
    thermal = model.dec.iloc[model.urows]["GEN UID"].tolist()
    fossil = [int(j) for j in model.urows if model.dec.iloc[j]["Fuel"] in {"Coal","Oil","NG"}]
    assert len(fossil) == 23 and [names[j] for j in model.urows if j not in fossil] == ["121_NUCLEAR_1"]
    assert set(fossil) == {j for j,r in model.dec.iterrows() if r["Fuel"] in {"Coal","Oil","NG"}}
    identity = SOURCE/"january_identity"
    matrix,bounds,integer,labels,meta,native = load_case(identity)
    assert np.array_equal(native["rows"],np.arange(168))
    with np.load(identity/"constructive_vector.npz") as f:
        reference = f["vector"].copy()
    rp,ru,ry,rz,rt = unpack(reference,168,41,24,24)
    assert np.isfinite(reference).all() and np.all((ru==0)|(ru==1))
    cy,cz = transfer.transitions(ru)
    assert bit_equal(ry,cy) and bit_equal(rz,cz)
    regenerated = build(model,native["pmin"],native["pmax"],native["net"],native["rows"],23195)
    validate_structure(regenerated,names,thermal,fossil)
    assert (matrix != regenerated[0]).nnz == 0
    assert all(bit_equal(bounds[k],regenerated[1][k]) for k in bounds)
    assert np.array_equal(integer,regenerated[2]) and bit_equal(native["nodal"],regenerated[-1])
    assert labels.astype(str).equals(pd.DataFrame(regenerated[4])[labels.columns].astype(str))
    rate = model.dec.iloc[model.urows]["Ramp Rate MW/Min"].to_numpy(float)*60
    pmax = model.dec.iloc[model.urows]["PMax MW"].to_numpy(float)
    pmin = model.dec.iloc[model.urows]["PMin MW"].to_numpy(float)
    assert np.all(rate >= pmax-pmin)
    assert np.array_equal(native["pmin"][:,model.urows],np.broadcast_to(pmin,(168,24)))
    assert np.array_equal(native["pmax"][:,model.urows],np.broadcast_to(pmax,(168,24)))
    save(OUTPUT/"identity_assembly_binding.json", {"exact_matrix_bounds_labels_integrality_and_nodal_replay":True,
        "parent_matrix_sha256":digest(identity/"matrix.npz"), "parent_bounds_sha256":digest(identity/"bounds.npz"),
        "parent_constructive_vector_sha256":digest(identity/"constructive_vector.npz"),
        "all_24_native_ramp_margins_nonnegative":True, "minimum_ramp_margin_MW":float((rate-pmax+pmin).min()),
        "thermal_hourly_bounds_match_native_nameplate":True, "fossil_names":[names[j] for j in fossil]})
    sources = local_sources(Path(__file__))
    save(OUTPUT/"transitive_source_inventory.json",[{"path":str(p),"sha256":digest(p)} for p in sources])
    paths = [PROTOCOL, *sources, SOURCE/"input_manifest.csv", source_v3/"code/dscgrid_model.py",
             *sorted((source_v3/"raw").rglob("*.csv"))]
    paths.extend(identity/name for name in ["matrix.npz","bounds.npz","integrality.npz","row_metadata.csv.gz",
        "model_metadata.json","native_inputs.npz","constructive_vector.npz"])
    prepared = []
    for seed in [None,*ORDINARY,CONTROL]:
        role = "identity" if seed is None else "positive_control" if seed == CONTROL else "ordinary"
        case = "january_identity" if seed is None else f"seed_{seed}"
        order,draw = (np.arange(168), {"generator":"none; identity", "redraws":0}) if seed is None else generate_order(seed,ru,seed==CONTROL)
        inverse = np.argsort(order)
        for a in [native[k] for k in ["pmin","pmax","net","nodal","rows"]] + [rp,ru,rt]:
            assert bit_equal(a[order][inverse],a)
        n = {k:native[k][order].copy() for k in ["pmin","pmax","net","rows"]}
        n["source_hour"] = order
        data = build(model,n["pmin"],n["pmax"],n["net"],n["rows"],23195)
        cap_row = validate_structure(data,names,thermal,fossil)
        assert bit_equal(data[-1],native["nodal"][order]) and (data[0] != matrix).nnz == 0
        directory = OUTPUT/case
        transfer.archive_model(directory,data,n)
        numerical,vector = transfer.check_candidate(model,data,n,rp[order],ru[order],rt[order],fossil,23195)
        transfer.save_witness(directory,vector,model)
        assert numerical["static_network_cap_pass"]
        assert transfer.energy(rp[order],fossil) == transfer.energy(rp,fossil)
        rowlabels = pd.DataFrame(data[4])
        static = ~rowlabels.family.isin(["minimum_up","minimum_down"]).to_numpy()
        static_bounds = {k:v[static] if k.startswith("row_") else v for k,v in data[1].items()}
        static_exact = exact_point_check(data[0][static].tocsr(),static_bounds,vector,data[2])
        full_exact = exact_point_check(data[0],data[1],vector,data[2])
        assert static_exact["expanded_pass"]
        admitted = bool(full_exact["expanded_pass"] and numerical["binary_network_pass"])
        if full_exact["expanded_pass"]:
            assert numerical["binary_network_pass"], "Exact/native constructive contradiction"
        if role != "ordinary":
            assert admitted, "Identity/control failed; do not proceed or replace"
            assert np.array_equal(ru[order],ru)
        projected,projection = audit_projection(data[0],data[1],data[3],rowlabels,data[2])
        np.savez_compressed(directory/"projected_integrality.npz",integrality=projected)
        np.savez_compressed(directory/"static_row_mask.npz",keep=static)
        save(directory/"projection_audit.json",projection)
        save(directory/"constructive_check.json",{"numerical":numerical,"static_exact":static_exact,
            "full_exact":full_exact,"constructive_expanded_pass":admitted,
            "exact_fossil_MWh":rational_record(transfer.energy(rp[order],fossil)),
            "failed_reference_is_not_model_infeasibility":True})
        save(directory/"randomization.json",draw)
        changed = np.flatnonzero(np.diff(order)!=1)
        preservation = {"bijection":True,"fixed_edges_48":True,"hour_of_day_exact":True,
            "joint_package_roundtrips_bitwise":True,"nodal_native_reconstruction_bitwise":True,
            "exact_fossil_energy_preserved":True,"commitment_sequence_unchanged":bool(np.array_equal(ru[order],ru)),
            "within_day_adjacency_preserved":bool(all(np.all(np.diff(order[24*b:24*(b+1)])==1) for b in range(7))),
            "weather_continuity_claim":False,"changed_hours":int(np.count_nonzero(order!=np.arange(168))),
            "changed_adjacent_pair_count":len(changed),"changed_adjacent_pairs_after_hours":changed.tolist(),
            "changed_adjacent_source_pairs":[{"after_destination_hour":int(t),"left_source_hour":int(order[t]),
                "right_source_hour":int(order[t+1])} for t in changed],
            "cap_row_0based":cap_row,"mean_rows":0,"seed":seed,"role":role}
        save(directory/"preservation.json",preservation)
        pd.DataFrame({"new_hour_0based":np.arange(168),"source_hour_0based":order,
            "source_native_row":n["rows"],"hour_of_day_0based":order%24}).to_csv(directory/"permutation.csv",index=False)
        if role == "ordinary":
            lp = directory/"lp";lp.mkdir()
            for name in ["matrix.npz","bounds.npz","integrality.npz","row_metadata.csv.gz"]:
                shutil.copyfile(directory/name,lp/name)
        prepared.append({"case":case,"constructive_expanded_pass":admitted,**preservation})
        print(json.dumps({"event":"PREPARED_CASE","case":case,"constructive_pass":admitted}),flush=True)
    save(OUTPUT/"prepared_cases.json",prepared)
    ordinary_orders = [pd.read_csv(OUTPUT/c/"permutation.csv").source_hour_0based.to_numpy() for c in CASES]
    save(OUTPUT/"sampling_inventory.json",{"ordinary_denominator":2,"ordinary_cases":CASES,
        "duplicate_ordinary_permutations":bool(np.array_equal(*ordinary_orders)),
        "all_samples_retained":True,"control_outside_denominator":f"seed_{CONTROL}"})
    paths.extend(sorted(p for p in OUTPUT.rglob("*") if p.is_file()))
    rows = [{"path":str(p.resolve()),"sha256":digest(p),"bytes":p.stat().st_size} for p in dict.fromkeys(paths)]
    pd.DataFrame(rows).to_csv(OUTPUT/"input_manifest.csv",index=False)
    freeze = {"utc":datetime.now(timezone.utc).isoformat(),"source_sha256":digest(Path(__file__)),
        "protocol_sha256":digest(PROTOCOL),"manifest_sha256":digest(OUTPUT/"input_manifest.csv"),
        "source_v3":str(source_v3.resolve()),"ordinary_cases":CASES,"control_seed":CONTROL,
        "LP_seconds":30,"MIP_seconds":300,"phase_seconds":PHASE_SECONDS,"minimum_MIP_remaining_seconds":MIP_GUARD_SECONDS,
        "optimizations_started":0,"cap_MWh":23195,"individual_means":0,"bound_files":len(rows),
        "requires_independent_prepared_PASS_and_root_GO":True}
    save(OUTPUT/"prepared_freeze.json",freeze)
    print(json.dumps({"event":"PREPARED_NO_SOLVES",**freeze}),flush=True)


def correct_new_certificate(directory,labels):
    path = directory/"dual_certificate.json"
    if not path.exists():
        return
    cert = read(path);support = cert["support"]
    support["distinct_uid_labels_including_bus_and_branch_tags"] = support.pop("individual_units_in_nonzero_rows")
    active = labels.iloc[[m["row"] for m in cert["multipliers"]]]
    temporal = active[active.family.isin(["transition","exclusive_transition","minimum_up","minimum_down"])]
    support["temporal_generator_uids"] = sorted(set(temporal.uid.astype(str)))
    support["temporal_generator_count"] = len(support["temporal_generator_uids"])
    support["interpretation"] = ("Full-network fossil-cap model; no mean rows. The cap involves all 168 hours. "
        "UID labels include generators, buses and branches. Support is not minimum memory or required raw information.")
    save(path,cert)


def run_prepared(source_v3):
    freeze = read(OUTPUT/"prepared_freeze.json")
    assert freeze["ordinary_cases"] == CASES and freeze["source_v3"] == str(source_v3.resolve())
    assert digest(OUTPUT/"input_manifest.csv") == freeze["manifest_sha256"]
    audit = check_manifest(OUTPUT/"input_manifest.csv")
    with (OUTPUT/"execution_started.json").open("x",encoding="utf-8") as f:
        json.dump({"utc":datetime.now(timezone.utc).isoformat(),"pre_execution_hash_check":audit},f,indent=2)
    model = load_model(source_v3)
    prepared = read(OUTPUT/"prepared_cases.json")
    controls = [x for x in prepared if x["role"] != "ordinary"]
    assert len(controls)==2 and all(x["constructive_expanded_pass"] for x in controls)
    ordinary = [x for x in prepared if x["role"] == "ordinary"]
    assert [x["case"] for x in ordinary] == CASES
    transfer.OUTPUT = OUTPUT
    outcomes,lp_results = {},{}
    phase_started = time.perf_counter()
    for item in ordinary:
        case = item["case"];directory = OUTPUT/case
        if item["constructive_expanded_pass"]:
            outcomes[case] = {"case":case,"verdict":"VERIFIED_FEASIBLE_EXPANDED_MODEL",
                "route":"CONSTRUCTIVE_REFERENCE","LP_calls":0,"MIP_calls":0}
            continue
        if PHASE_SECONDS-(time.perf_counter()-phase_started)<30:
            outcomes[case] = {"case":case,"verdict":"UNKNOWN","route":"PHASE_BUDGET_BEFORE_LP","LP_calls":0,"MIP_calls":0}
            continue
        matrix,bounds,integer,labels,meta,native = load_case(directory)
        rec = transfer.solve_lp(matrix,bounds,integer,labels.to_dict("records"),directory/"lp")
        correct_new_certificate(directory/"lp",labels)
        rec.update(case=case,matrix_sha256=digest(directory/"matrix.npz"),bounds_sha256=digest(directory/"bounds.npz"))
        save(directory/"lp/result.json",rec);lp_results[case] = rec
        if rec["verdict"] == "REJECTED_EXACT_BINARY64_CERTIFICATE":
            outcomes[case] = {"case":case,"verdict":"CERTIFIED_INFEASIBLE_EXPANDED_MODEL",
                "route":"EXACT_ROBUST_LP_RAY","LP_calls":1,"MIP_calls":0}
        print(json.dumps({"stage":"LP","case":case,"verdict":rec["verdict"],"elapsed_s":rec["elapsed_s"]}),flush=True)
    for item in ordinary:
        case = item["case"]
        if case in outcomes:
            continue
        if PHASE_SECONDS-(time.perf_counter()-phase_started)<MIP_GUARD_SECONDS:
            outcomes[case] = {"case":case,"verdict":"UNKNOWN","route":"PHASE_BUDGET_BEFORE_MIP","LP_calls":1,"MIP_calls":0}
        else:
            result = solve_mip(model,OUTPUT/case,case)
            accepted = result["verdict"] == "VERIFIED_FEASIBLE_EXPANDED_MODEL"
            outcomes[case] = {"case":case,"verdict":result["verdict"] if accepted else "UNKNOWN",
                "solver_diagnostic_verdict":result["verdict"],"route":"U_ONLY_MIP","LP_calls":1,"MIP_calls":1,
                "MIP_elapsed_s":result["elapsed_s"]}
            print(json.dumps({"stage":"MIP",**outcomes[case]}),flush=True)
        save(OUTPUT/"outcomes_partial.json",list(outcomes.values()))
    ordered = [outcomes[case] for case in CASES]
    save(OUTPUT/"outcomes.json",ordered)
    pd.DataFrame(ordered).to_csv(OUTPUT/"outcomes.csv",index=False)
    save(OUTPUT/"final_manifest_check.json",check_manifest(OUTPUT/"input_manifest.csv"))
    save(OUTPUT/"completion.json",{"ordinary_denominator":2,"controls_outside_denominator":2,
        "LP_calls":len(lp_results),"MIP_calls":sum(x["MIP_calls"] for x in ordered),
        "phase_elapsed_s":time.perf_counter()-phase_started,
        "actual_LP_seconds":sum(x["elapsed_s"] for x in lp_results.values()),
        "actual_MIP_seconds":sum(x.get("MIP_elapsed_s",0) for x in ordered),
        "nominal_model_positive_claim":False,"all_outcomes_retained":True})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-v3",type=Path,required=True)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--prepare-only",action="store_true")
    modes.add_argument("--run-prepared",action="store_true")
    args = parser.parse_args()
    if args.prepare_only:
        prepare(args.source_v3)
    else:
        run_prepared(args.source_v3)


if __name__ == "__main__":
    main()
