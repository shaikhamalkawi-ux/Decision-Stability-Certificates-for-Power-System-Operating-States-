"""Prepare then test fixed April/October service-order continuation cases."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import time

import highspy
import numpy as np
import pandas as pd
from scipy.sparse import load_npz

from research8h_seasonal_reference import physical_check as no_cap_check
from research8h_seasonal_transfer import archive_model, cap_record, check_candidate, energy, save_witness, transitions
from research8h_seasonal_uncapped import check_manifest, exact_point_check, rational_record
from research8h_service_network_mip import build, direct_check, unpack
from research8h_u_only_continuation import audit_projection
from temporal_lp_certificate import certificate_context, check_vector, digest, exact_ray_check, save
from v8r1_rts_seasonal import inputs, load_model

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "results/research8h/seasonal_reference_continuation"
REFERENCE_MANIFEST = "cc7ff078ea7e99ac177b3d22be3208cf454ca0726015e4a10c3b65329630758b"
OUTPUT = ROOT / "results/research8h/seasonal_cap_continuation"
PROTOCOL = ROOT / "docs/research8h/SEASONAL_CAP_CONTINUATION_PROTOCOL.md"
SCHEDULE = {4: ([26093400, 26093401], 26100400), 10: ([26094000, 26094001], 26101000)}
TOL = 1e-5
PHASE_SECONDS = 2400


def arrays(path):
    with np.load(path) as data:
        return {k: data[k].copy() for k in data.files}


def load_case(directory):
    return (load_npz(directory / "matrix.npz").tocsr(), arrays(directory / "bounds.npz"),
            arrays(directory / "integrality.npz")["integrality"],
            json.loads((directory / "model_metadata.json").read_text()),
            pd.read_csv(directory / "row_metadata.csv.gz"), arrays(directory / "native_inputs.npz"))


def constructive(model, directory, data, native, p, u, theta, fossil, budget):
    checks, vector = check_candidate(model, data, native, p, u, theta, fossil, budget)
    save_witness(directory, vector, model)
    labels = pd.DataFrame(data[4])
    static = ~labels.family.isin(["minimum_up", "minimum_down"]).to_numpy()
    assert (~static).sum() == 2*167*24
    static_bounds = {key: (value[static] if key.startswith("row_") else value) for key, value in data[1].items()}
    static_exact = exact_point_check(data[0][static].tocsr(), static_bounds, vector, data[2])
    full_exact = exact_point_check(data[0], data[1], vector, data[2])
    result = {"numerical": checks, "static_exact": static_exact, "full_exact": full_exact,
              "constructive_expanded_pass": bool(checks["binary_network_pass"] and full_exact["expanded_pass"])}
    save(directory / "constructive_check.json", result)
    assert checks["static_network_cap_pass"] and static_exact["expanded_pass"]
    return result


def prepare(source_v3):
    # Completion is required before opening the new archive or selecting eligibility.
    completion = json.loads((REFERENCE / "completion.json").read_text())
    assert completion["calls"] == 3
    assert digest(REFERENCE / "input_manifest.csv") == REFERENCE_MANIFEST
    ref_freeze = json.loads((REFERENCE / "prepared_freeze.json").read_text())
    assert ref_freeze["input_manifest_sha256"] == REFERENCE_MANIFEST and ref_freeze["months"] == [4, 7, 10]
    assert ref_freeze["seconds_per_case"] == 600 and not ref_freeze["warm_start"]
    assert json.loads((REFERENCE / "final_input_hash_check.json").read_text())["pass"]
    reference_results = {r["month"]: r for r in json.loads((REFERENCE / "summary.json").read_text())}
    assert set(reference_results) == {4, 7, 10}
    OUTPUT.mkdir(parents=True, exist_ok=False)
    save(OUTPUT / "reference_manifest_check.json", check_manifest(REFERENCE / "input_manifest.csv"))
    model = load_model(source_v3)
    names, thermal = model.dec["GEN UID"].tolist(), model.dec.iloc[model.urows]["GEN UID"].tolist()
    fossil = [int(j) for j in model.urows if model.dec.iloc[j]["Fuel"] in {"Coal", "Oil", "NG"}]
    assert (len(names), len(thermal), len(model.busids), len(model.branches)) == (41, 24, 24, 38)
    assert len(fossil) == 23 and [names[j] for j in model.urows if j not in fossil] == ["121_NUCLEAR_1"]
    rate = model.dec.iloc[model.urows]["Ramp Rate MW/Min"].to_numpy(float)*60
    variation = model.dec.iloc[model.urows]["PMax MW"].to_numpy(float)-model.dec.iloc[model.urows]["PMin MW"].to_numpy(float)
    assert np.all(rate >= variation)
    save(OUTPUT / "ramp_redundancy.json", {"all_24_pass": True, "minimum_margin_MW": float((rate-variation).min())})
    paths = [Path(__file__), PROTOCOL, REFERENCE / "input_manifest.csv", REFERENCE / "prepared_freeze.json",
        REFERENCE / "completion.json", REFERENCE / "summary.json", REFERENCE / "final_input_hash_check.json",
        ROOT / "docs/research8h/SEASONAL_REFERENCE_CONTINUATION_PROTOCOL.md",
        ROOT / "docs/research8h/SEASONAL_TRANSFER_PROTOCOL.md",
        *[ROOT / "src" / name for name in ["research8h_seasonal_reference_continuation.py",
            "research8h_seasonal_reference.py", "research8h_seasonal_transfer.py", "research8h_seasonal_uncapped.py",
            "research8h_service_network_mip.py", "research8h_service_network.py", "research8h_u_only_continuation.py",
            "temporal_lp_certificate.py", "temporal_information_pilot.py", "v8r1_rts_seasonal.py"]],
        source_v3 / "code/dscgrid_model.py", *sorted((source_v3 / "raw").rglob("*.csv"))]
    initial = ROOT / "results/research8h/seasonal_transfer"
    initial_completion = json.loads((initial / "completion.json").read_text())
    assert initial_completion["replication_gate"] == "NOT_MET_INSUFFICIENT_ELIGIBLE_WEEKS"
    initial_context = {"original_replication_gate": initial_completion["replication_gate"],
                       "known_success_month": 1, "certificate_replays": [], "optimization_calls": 0}
    paths.append(initial / "completion.json")
    for seed in [26093100, 26093101]:
        d = initial / f"seed_{seed}" / "lp"
        cert = json.loads((d / "dual_certificate.json").read_text())
        for filename, expected in cert["model_artifacts"].items():
            assert digest(d / filename) == expected
        assert digest(d / "row_metadata.csv.gz") == cert["row_metadata_sha256"]
        a, b = load_npz(d / "matrix.npz").tocsr(), arrays(d / "bounds.npz")
        ray = np.zeros(a.shape[0])
        for multiplier in cert["multipliers"]:
            ray[multiplier["row"]] = float.fromhex(multiplier["value_hex"])
        replay = exact_ray_check(a, b, ray)
        assert replay["pass"] and replay["robust_pass"]
        for key in ["exact_gap_numerator", "exact_gap_denominator", "exact_robust_gap_numerator", "exact_robust_gap_denominator"]:
            assert replay[key] == cert["verification"][key]
        keep = ~pd.read_csv(d / "row_metadata.csv.gz").family.isin(["minimum_up", "minimum_down"]).to_numpy()
        static_bounds = {key: (value[keep] if key.startswith("row_") else value) for key, value in b.items()}
        static_point = arrays(d.parent / "constructive_vector.npz")["vector"]
        static_integer = arrays(d / "integrality.npz")["integrality"]
        static_replay = exact_point_check(a[keep].tocsr(), static_bounds, static_point, static_integer)
        assert static_replay["expanded_pass"]
        initial_context["certificate_replays"].append({"seed": seed, "certificate_sha256": digest(d / "dual_certificate.json"),
            "replay": replay, "ordinary_static_exact_expanded_replay": static_replay})
        paths.extend(d / name for name in ["matrix.npz", "bounds.npz", "dual_certificate.json", "row_metadata.csv.gz", "integrality.npz"])
        paths.append(d.parent / "constructive_vector.npz")
    for case in ["january_identity", "seed_26100100"]:
        d = initial / case
        a, b, integer, unused_meta, unused_labels, unused_native = load_case(d)
        point = arrays(d / "constructive_vector.npz")["vector"]
        replay = exact_point_check(a, b, point, integer)
        assert replay["expanded_pass"]
        initial_context[case] = {"exact_expanded_replay": replay, "vector_sha256": digest(d / "constructive_vector.npz")}
        paths.extend(d / name for name in ["matrix.npz", "bounds.npz", "integrality.npz", "model_metadata.json", "row_metadata.csv.gz", "native_inputs.npz", "constructive_vector.npz"])
    save(OUTPUT / "initial_arm_context.json", initial_context)
    prepared, scheduled, eligibility = [], [], []
    for month, (seeds, control_seed) in SCHEDULE.items():
        src = REFERENCE / f"month_{month:02d}"
        record = reference_results[month]
        assert record == json.loads((src / "result.json").read_text())
        eligible = record["verdict"] == "VERIFIED_REFERENCE_BINARY_WITNESS_EXPANDED_MODEL"
        eligibility.append({"month": month, "eligible": eligible, "reference_verdict": record["verdict"],
                            "reference_result_sha256": digest(src / "result.json")})
        paths.append(src / "result.json")
        for seed in [*seeds, control_seed]:
            scheduled.append({"month": month, "seed": seed, "kind": "ordinary" if seed in seeds else "class_control",
                              "status": "SCHEDULED" if eligible else "NO_REFERENCE_NOT_RUN"})
        if not eligible:
            continue
        assert record["exact_expanded_model_pass"] and record["native_no_cap_pass"]
        original, rb, unused, rm, rl, rn = load_case(src)
        old_integer = arrays(src / "original_integrality.npz")["integrality"]
        reference = arrays(src / "recovered_vector.npz")["vector"]
        rp, ru, ry, rz, rt = unpack(reference, 168, 41, 24, 24)
        assert rm["unit_names"] == names and rm["thermal_unit_names"] == thermal
        assert rm["fossil_units"] == [names[j] for j in fossil] and rm["energy_cap_constraints"] == 0
        assert not rl.family.isin(["target_mean", "fossil_energy_cap"]).any()
        reference_exact = exact_point_check(original, rb, reference, old_integer)
        reference_native = no_cap_check(model, rp, ru, ry, rz, rt, rn["pmin"], rn["pmax"], rn["net"], rn["rows"], rn["nodal"], fossil)
        assert reference_exact["expanded_pass"] and reference_native["pass"] and check_vector(original, rb, reference)["pass"]
        cap = cap_record(rp, fossil)
        assert rational_record(energy(rp, fossil)) == record["recovered_fossil_energy"]
        budget = float(cap["budget_MWh"])
        assert int(budget) == cap["budget_MWh"]
        save(OUTPUT / f"month_{month:02d}_reference.json", {"reference_exact": reference_exact,
            "reference_native": reference_native, "cap": cap, "reference_result": record,
            "reference_vector_sha256": digest(src / "recovered_vector.npz"), "fossil_units": [names[j] for j in fossil]})
        cols, ignored, lo, hi, net, used = inputs(model, source_v3, month)
        rows = pd.read_csv(used[1])["row"].to_numpy(int)
        assert cols == names
        assert all(np.array_equal(value, rn[key]) for key, value in [("pmin", lo), ("pmax", hi), ("net", net), ("rows", rows)])
        identity = build(model, lo, hi, net, rows, budget)
        identity_labels = pd.DataFrame(identity[4])
        keep = ~identity_labels.family.eq("fossil_energy_cap").to_numpy()
        assert (~keep).sum() == 1 and not identity_labels.family.eq("target_mean").any()
        assert (identity[0][keep] != original).nnz == 0
        assert all(np.array_equal(identity[1][key][keep] if key.startswith("row_") else identity[1][key], rb[key]) for key in rb)
        assert np.array_equal(identity[2], old_integer) and np.array_equal(identity[-1], rn["nodal"])
        native = {"pmin": lo, "pmax": hi, "net": net, "rows": rows, "source_hour": np.arange(168)}
        identity_dir = OUTPUT / f"month_{month:02d}_identity"
        archive_model(identity_dir, identity, native)
        identity_check = constructive(model, identity_dir, identity, native, rp, ru, rt, fossil, budget)
        assert identity_check["constructive_expanded_pass"]
        for seed in [*seeds, control_seed]:
            rng = np.random.Generator(np.random.PCG64(seed))
            order = np.arange(168)
            if seed in seeds:
                order[48:120] = rng.permutation(np.arange(48, 120))
            else:
                groups = {}
                for t in range(48, 120):
                    groups.setdefault(tuple(int(v) for v in ru[t]), []).append(t)
                for positions in groups.values():
                    order[positions] = rng.permutation(np.asarray(positions))
                assert np.array_equal(ru[order], ru)
            inverse = np.argsort(order)
            assert np.array_equal(order[inverse], np.arange(168))
            assert np.array_equal(order[:48], np.arange(48)) and np.array_equal(order[120:], np.arange(120, 168))
            for a in [lo, hi, net, rows, identity[-1], rp, ru, rt]:
                assert np.array_equal(a[order][inverse], a)
            n = {"pmin": lo[order], "pmax": hi[order], "net": net[order], "rows": rows[order], "source_hour": order}
            data = build(model, n["pmin"], n["pmax"], n["net"], n["rows"], budget)
            assert np.array_equal(data[-1], identity[-1][order])
            directory = OUTPUT / f"seed_{seed}"
            archive_model(directory, data, n)
            cc = constructive(model, directory, data, n, rp[order], ru[order], rt[order], fossil, budget)
            assert energy(rp[order], fossil) == energy(rp, fossil)
            if seed == control_seed:
                assert cc["constructive_expanded_pass"]
            labels = pd.DataFrame(data[4])
            projected, projection = audit_projection(data[0], data[1], data[3], labels, data[2])
            np.savez_compressed(directory / "projected_integrality.npz", integrality=projected)
            save(directory / "projection_audit.json", projection)
            pd.DataFrame({"new_hour_0based": np.arange(168), "source_hour_0based": order,
                          "source_native_row": rows[order]}).to_csv(directory / "permutation.csv", index=False)
            save(directory / "preservation.json", {"bijection": True, "fixed_48_hour_edges": True,
                "all_package_roundtrips_exact": True, "nodal_native_reconstruction_exact": True,
                "exact_fossil_sum_preserved": True, "changed_hours": int(np.count_nonzero(order != np.arange(168))),
                "commitment_sequence_unchanged": bool(np.array_equal(ru[order], ru)),
                "kind": "ordinary" if seed in seeds else "class_control"})
            if seed in seeds:
                lp_dir = directory / "lp"
                lp_dir.mkdir()
                for name in ["matrix.npz", "bounds.npz", "integrality.npz", "row_metadata.csv.gz"]:
                    shutil.copyfile(directory / name, lp_dir / name)
                prepared.append({"case": f"seed_{seed}", "month": month, "seed": seed,
                    "budget_MWh": cap["budget_MWh"], "constructive_expanded_pass": cc["constructive_expanded_pass"]})
        paths.extend(used)
        paths.extend(sorted(p for p in src.glob("*") if p.is_file()))
    save(OUTPUT / "eligibility.json", eligibility)
    save(OUTPUT / "scheduled_cases.json", scheduled)
    save(OUTPUT / "prepared_cases.json", prepared)
    paths.extend(sorted(p for p in OUTPUT.rglob("*") if p.is_file()))
    pd.DataFrame([{"path": str(p), "sha256": digest(p), "bytes": p.stat().st_size}
                  for p in dict.fromkeys(paths)]).to_csv(OUTPUT / "input_manifest.csv", index=False)
    freeze = {"utc": datetime.now(timezone.utc).isoformat(), "source_sha256": digest(Path(__file__)),
        "protocol_sha256": digest(PROTOCOL), "input_manifest_sha256": digest(OUTPUT / "input_manifest.csv"),
        "reference_manifest_sha256": REFERENCE_MANIFEST, "source_v3": str(source_v3.resolve()),
        "cases": [r["case"] for r in prepared], "schedule": SCHEDULE, "eligibility": eligibility,
        "LP_seconds": 30, "MIP_seconds": 300, "phase_seconds": PHASE_SECONDS,
        "minimum_MIP_remaining_seconds": 305, "optimizations_started": 0, "all_controls_pass": True,
        "original_failed_replication_gate_unchanged": True, "requires_parent_go": True}
    save(OUTPUT / "prepared_freeze.json", freeze)
    print(json.dumps({"event": "PREPARED_NO_SOLVES", **freeze}), flush=True)


def solver_for(matrix, bounds, integer, seconds, directory, is_lp):
    lp = highspy.HighsLp()
    lp.num_row_, lp.num_col_ = matrix.shape
    lp.col_cost_ = np.zeros(matrix.shape[1])
    lp.col_lower_, lp.col_upper_ = bounds["column_lower"], bounds["column_upper"]
    lp.row_lower_, lp.row_upper_ = bounds["row_lower"], bounds["row_upper"]
    if not is_lp:
        lp.integrality_ = [highspy.HighsVarType.kInteger if v else highspy.HighsVarType.kContinuous for v in integer]
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.num_row_, lp.a_matrix_.num_col_ = matrix.shape
    lp.a_matrix_.start_, lp.a_matrix_.index_, lp.a_matrix_.value_ = matrix.indptr, matrix.indices, matrix.data
    options = {"time_limit": float(seconds), "threads": 1, "random_seed": 0,
        "presolve": "off" if is_lp else "on", "log_to_console": False, "log_file": str(directory / "solver.log")}
    options.update({"solver": "simplex"} if is_lp else {"mip_rel_gap": 1e-8})
    solver = highspy.Highs()
    for key, value in options.items():
        assert solver.setOptionValue(key, value) == highspy.HighsStatus.kOk
    assert solver.passModel(lp) == highspy.HighsStatus.kOk
    return solver, options


def solve_lp(directory):
    matrix, bounds, integer, meta, labels, native = load_case(directory)
    sub = directory / "lp"
    solver, options = solver_for(matrix, bounds, integer, 30, sub, True)
    started = time.perf_counter()
    run_status = solver.run()
    elapsed = time.perf_counter()-started
    status, solution = solver.getModelStatus(), solver.getSolution()
    result = {"model_status": solver.modelStatusToString(status), "run_status": str(run_status),
        "elapsed_s": elapsed, "time_limit_s": 30, "verdict": "UNKNOWN", "solver_version": solver.version(),
        "solver_options": options, "optimization_calls": 1, "solution_value_valid": bool(solution.value_valid)}
    if solution.value_valid:
        vector = np.asarray(solution.col_value)
        np.savez_compressed(sub / "returned_vector.npz", vector=vector)
        check = check_vector(matrix, bounds, vector)
        result["returned_vector_check"] = check
        if check["pass"]:
            result["verdict"] = "NUMERICAL_CONTINUOUS_FEASIBLE_BINARY_UNKNOWN"
            result["fractional_state_coordinates"] = int(np.count_nonzero(np.abs(vector[integer.astype(bool)]-np.rint(vector[integer.astype(bool)])) > TOL))
    if status == highspy.HighsModelStatus.kInfeasible:
        ray_status, exists, ray = solver.getDualRay()
        result.update(dual_ray_status=str(ray_status), dual_ray_exists=bool(exists), verdict="SOLVER_INFEASIBLE_NO_VERIFIED_RAY")
        if exists:
            ray = np.asarray(ray)
            np.savez_compressed(sub / "raw_solver_ray.npz", multipliers=ray)
            candidates, checks = [], []
            for sign in [1, -1]:
                raw = sign*ray
                bad = ((raw > 0) & ~np.isfinite(bounds["row_lower"])) | ((raw < 0) & ~np.isfinite(bounds["row_upper"]))
                projected = raw.copy()
                projected[bad] = 0.
                for name, candidate in [("raw", raw), ("projected_to_row_sign_cone", projected)]:
                    check = exact_ray_check(matrix, bounds, candidate)
                    check.update(candidate=name, orientation=sign, inadmissible_raw_entries=int(np.count_nonzero(bad)))
                    candidates.append(candidate)
                    checks.append(check)
            result["candidate_checks"] = checks
            valid = [i for i, c in enumerate(checks) if c.get("pass") and c.get("robust_pass")]
            if valid:
                chosen, check = candidates[valid[0]], checks[valid[0]]
                context = certificate_context(sub, labels.to_dict("records"), chosen)
                support = context["support"]
                support["distinct_uid_labels_including_bus_and_branch_tags"] = support.pop("individual_units_in_nonzero_rows")
                active = labels.iloc[np.flatnonzero(chosen)]
                temporal = active[active.family.isin(["transition", "exclusive_transition", "minimum_up", "minimum_down"])]
                support["temporal_generator_uids"] = sorted(set(temporal.uid.astype(str)))
                support["temporal_generator_count"] = len(support["temporal_generator_uids"])
                support["global_cap_has_nonzero_multiplier"] = bool(active.family.eq("fossil_energy_cap").any())
                support["global_cap_scope"] = {"hours": 168, "fossil_units": 23, "dispatch_coordinates": 3864}
                support["reference_energy_dependency"] = "cap derives from the full reference 23-unit by 168-hour fossil sum"
                support["interpretation"] = "No individual mean rows. Full matrix/bounds are archived. Row/hour support is not minimum memory or minimum raw information."
                cert = {"orientation": check["orientation"], "candidate": check["candidate"], "verification": check,
                    "multipliers": [{"row": int(j), "value_hex": float(chosen[j]).hex()} for j in np.flatnonzero(chosen)],
                    "row_metadata_sha256": digest(sub / "row_metadata.csv.gz"),
                    "experiment_manifest_sha256": digest(OUTPUT / "input_manifest.csv"), **context}
                save(sub / "dual_certificate.json", cert)
                table = active.copy()
                table["multiplier"] = chosen[np.flatnonzero(chosen)]
                table.to_csv(sub / "sparse_multipliers.csv", index=False)
                result.update(verdict="CERTIFIED_INFEASIBLE_EXPANDED_MODEL", certificate_verification=check)
    result.update(matrix_sha256=digest(directory / "matrix.npz"), bounds_sha256=digest(directory / "bounds.npz"))
    save(sub / "result.json", result)
    return result


def solve_mip(model, directory):
    matrix, bounds, original_integer, meta, labels, native = load_case(directory)
    integer = arrays(directory / "projected_integrality.npz")["integrality"]
    sub = directory / "mip"
    sub.mkdir()
    solver, options = solver_for(matrix, bounds, integer, 300, sub, False)
    started = time.perf_counter()
    run_status = solver.run()
    elapsed = time.perf_counter()-started
    status, solution, info = solver.getModelStatus(), solver.getSolution(), solver.getInfo()
    result = {"model_status": solver.modelStatusToString(status), "run_status": str(run_status),
        "elapsed_s": elapsed, "time_limit_s": 300, "verdict": "UNKNOWN", "solver_version": solver.version(),
        "solver_options": options, "optimization_calls": 1, "solution_value_valid": bool(solution.value_valid),
        "mip_node_count": int(info.mip_node_count), "exact_optimality_claim": False}
    if solution.value_valid:
        raw = np.asarray(solution.col_value)
        np.savez_compressed(sub / "raw_vector.npz", vector=raw)
        result["raw_matrix_check"] = check_vector(matrix, bounds, raw)
        p, u, y, z, theta = unpack(raw, 168, 41, 24, 24)
        eligible = bool(np.isfinite(raw).all() and np.all(np.abs(u-np.rint(u)) <= TOL)
                        and np.all((np.rint(u) >= 0) & (np.rint(u) <= 1)))
        result["eligible_for_recovery"] = eligible
        if eligible:
            u = np.rint(u)
            y, z = transitions(u)
            point = np.concatenate([a.ravel() for a in (p, u, y, z, theta)])
            np.savez_compressed(sub / "recovered_vector.npz", vector=point)
            result["recovered_matrix_check"] = check_vector(matrix, bounds, point)
            fossil = [meta["unit_names"].index(uid) for uid in meta["fossil_units"]]
            physical = direct_check(model, p, u, y, z, theta, native["pmin"], native["pmax"], native["net"],
                                    native["rows"], native["nodal"], fossil, float(meta["budget_MWh"]))
            exact = exact_point_check(matrix, bounds, point, original_integer)
            save(sub / "physical_check.json", physical)
            save(sub / "exact_point_check.json", exact)
            result.update(physical_pass=physical["pass"], exact_expanded_pass=exact["expanded_pass"],
                          exact_strict_pass=exact["strict_pass"], fossil_MWh=rational_record(energy(p, fossil)))
            if result["raw_matrix_check"]["pass"] and result["recovered_matrix_check"]["pass"] and physical["pass"]:
                result["verdict"] = "VERIFIED_FEASIBLE_EXPANDED_MODEL" if exact["expanded_pass"] else "NUMERICAL_TOLERANCE_ONLY_CANDIDATE"
    if status == highspy.HighsModelStatus.kInfeasible and result["verdict"] == "UNKNOWN":
        result["verdict"] = "NUMERICAL_MIP_INFEASIBLE_NOT_EXACT_CERTIFICATE"
    save(sub / "result.json", result)
    return result


def run_prepared(source_v3):
    phase_start = time.perf_counter()
    freeze = json.loads((OUTPUT / "prepared_freeze.json").read_text())
    assert freeze["source_v3"] == str(source_v3.resolve())
    assert digest(Path(__file__)) == freeze["source_sha256"] and digest(PROTOCOL) == freeze["protocol_sha256"]
    assert digest(OUTPUT / "input_manifest.csv") == freeze["input_manifest_sha256"]
    before = check_manifest(OUTPUT / "input_manifest.csv")
    with (OUTPUT / "execution_started.json").open("x", encoding="utf-8") as stream:
        json.dump({"utc": datetime.now(timezone.utc).isoformat(), "pre_execution_hash_check": before,
                   "phase_clock_starts_before_validation": True}, stream, indent=2)
    model = load_model(source_v3)
    prepared = json.loads((OUTPUT / "prepared_cases.json").read_text())
    assert [r["case"] for r in prepared] == freeze["cases"]
    lp_results, outcomes, mip_results = {}, {}, {}
    for item in prepared:
        case = item["case"]
        result = solve_lp(OUTPUT / case)
        lp_results[case] = result
        assert not (item["constructive_expanded_pass"] and result["verdict"] == "CERTIFIED_INFEASIBLE_EXPANDED_MODEL"), "Contradictory exact positive and negative: stop execution"
        print(json.dumps({"stage": "LP", "case": case, "verdict": result["verdict"], "elapsed_s": result["elapsed_s"]}), flush=True)
    for item in prepared:
        case = item["case"]
        lp = lp_results[case]
        if lp["verdict"] == "CERTIFIED_INFEASIBLE_EXPANDED_MODEL":
            outcome = {"verdict": lp["verdict"], "route": "EXACT_ROBUST_LP_RAY", "MIP_calls": 0}
        elif item["constructive_expanded_pass"]:
            outcome = {"verdict": "VERIFIED_FEASIBLE_EXPANDED_MODEL", "route": "CONSTRUCTIVE_REFERENCE", "MIP_calls": 0}
        elif PHASE_SECONDS-(time.perf_counter()-phase_start) < 305:
            outcome = {"verdict": "UNKNOWN", "route": "NOT_RUN_PHASE_BUDGET", "MIP_calls": 0}
        else:
            result = solve_mip(model, OUTPUT / case)
            mip_results[case] = result
            outcome = {"verdict": result["verdict"], "route": "MIP", "MIP_calls": 1, "MIP_elapsed_s": result["elapsed_s"]}
            print(json.dumps({"stage": "MIP", "case": case, **outcome}), flush=True)
        outcome.update(case=case, month=item["month"], seed=item["seed"], budget_MWh=item["budget_MWh"],
                       LP_calls=1, LP_verdict=lp["verdict"], LP_elapsed_s=lp["elapsed_s"],
                       static_control_exact_expanded_pass=True)
        outcomes[case] = outcome
        save(OUTPUT / "outcomes_partial.json", list(outcomes.values()))
    ordered = [outcomes[item["case"]] for item in prepared]
    for scheduled in json.loads((OUTPUT / "scheduled_cases.json").read_text()):
        if scheduled["kind"] == "ordinary" and scheduled["status"] == "NO_REFERENCE_NOT_RUN":
            ordered.append({"case": f"seed_{scheduled['seed']}", "month": scheduled["month"], "seed": scheduled["seed"],
                            "verdict": "NO_REFERENCE", "route": "NO_REFERENCE_NOT_RUN", "LP_calls": 0, "MIP_calls": 0})
    ordered.sort(key=lambda r: (r["month"], r["seed"]))
    save(OUTPUT / "outcomes.json", ordered)
    pd.DataFrame(ordered).to_csv(OUTPUT / "outcomes.csv", index=False)
    save(OUTPUT / "final_manifest_check.json", check_manifest(OUTPUT / "input_manifest.csv"))
    phase_elapsed = time.perf_counter()-phase_start
    negative_months = sorted({r["month"] for r in ordered if r["verdict"] == "CERTIFIED_INFEASIBLE_EXPANDED_MODEL"})
    augmented_months = [1, *negative_months]
    save(OUTPUT / "completion.json", {"eligible_ordinary_cases": len(prepared), "intended_ordinary_cases": 4,
        "intended_class_controls": 2, "LP_calls": len(lp_results), "MIP_calls": len(mip_results),
        "actual_LP_seconds": sum(r["elapsed_s"] for r in lp_results.values()),
        "actual_MIP_seconds": sum(r["elapsed_s"] for r in mip_results.values()),
        "phase_elapsed_s": phase_elapsed, "phase_allocation_s": PHASE_SECONDS, "phase_overrun_s": max(0., phase_elapsed-PHASE_SECONDS),
        "all_cases_retained": True, "original_failed_replication_gate_unchanged": True,
        "original_replication_gate": "NOT_MET_INSUFFICIENT_ELIGIBLE_WEEKS",
        "new_continuation_weeks_with_certified_negative_and_controls": negative_months,
        "augmented_weeks_with_certified_negative_and_controls": augmented_months,
        "augmented_at_least_two_weeks": len(augmented_months) >= 2,
        "augmented_evidence_includes_previously_known_January_success": True,
        "exact_unwidened_positive_claim": False, "scope": "later stronger-reference April/October continuation"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-v3", type=Path, required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare-only", action="store_true")
    group.add_argument("--run-prepared", action="store_true")
    args = parser.parse_args()
    if args.prepare_only:
        prepare(args.source_v3)
    else:
        run_prepared(args.source_v3)


if __name__ == "__main__":
    main()
