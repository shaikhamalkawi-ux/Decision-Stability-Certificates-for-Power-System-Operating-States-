"""One frozen all-thermal-on DC-network LP under the existing fossil budget."""
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
from scipy.sparse import coo_matrix, save_npz

from temporal_information_pilot import nodal_check
from temporal_lp_certificate import check_vector, digest, save
from v8r1_rts_seasonal import inputs, load_model, verify

ROOT = Path(__file__).resolve().parents[1]
CASES = ["identity", *(f"seed_{seed}" for seed in range(26092600, 26092604))]
TOL = 1e-5


def assemble(model, pmin, pmax, rows, budget):
    h, ng = pmax.shape
    nb, nl = len(model.busids), len(model.branches)
    npower, nangle = h * ng, h * nb
    lower = np.r_[pmin.ravel(), np.full(nangle, -np.pi)]
    upper = np.r_[pmax.ravel(), np.full(nangle, np.pi)]
    angle_slacks = npower + np.arange(h) * nb + model.slack
    lower[angle_slacks] = upper[angle_slacks] = 0
    node_by_generator = [model.bi[int(row["Bus ID"])] for _, row in model.dec.iterrows()]
    fossil = [int(j) for j in model.urows if model.dec.iloc[j]["GEN UID"] != "121_NUCLEAR_1"]
    assert len(fossil) == 23
    assert set(model.dec.iloc[fossil]["Fuel"]) <= {"Coal", "Oil", "NG"}
    rr, cc, vv, lo, hi, labels = [], [], [], [], [], []

    def add(terms, low, high, family, hour, name):
        row = len(lo)
        for column, value in terms:
            if value:
                rr.append(row); cc.append(column); vv.append(value)
        lo.append(low); hi.append(high)
        labels.append({"row": row, "family": family, "hour_0based": hour, "name": str(name)})

    nodal = []
    for t, native in enumerate(rows):
        load = model.prop * float(model.load_ts.loc[int(native), str(model.AREA)]) - model.rtpv_at(int(native))
        nodal.append(load)
        for bus in range(nb):
            terms = [(t * ng + j, 1.0) for j in range(ng) if node_by_generator[j] == bus]
            terms.extend((npower + t * nb + other, -float(value)) for other, value in enumerate(model.Bbus[bus]) if value)
            add(terms, float(load[bus]), float(load[bus]), "nodal_balance", t, model.busids[bus])
        for line, branch in model.branches.iterrows():
            f, to = model.bi[int(branch["From Bus"])], model.bi[int(branch["To Bus"])]
            terms = [(npower + t * nb + f, float(model.bl[line])),
                     (npower + t * nb + to, -float(model.bl[line]))]
            add(terms, -float(model.rate[line]), float(model.rate[line]), "branch_flow", t, line)
    cap_indices = [t * ng + j for t in range(h) for j in fossil]
    add([(column, 1.0) for column in cap_indices], -np.inf, budget, "fossil_energy_cap", -1, "23_fossil_units")
    matrix = coo_matrix((vv, (rr, cc)), shape=(len(lo), npower + nangle)).tocsr()
    assert sorted(matrix[-1].indices.tolist()) == sorted(cap_indices)
    nuclear = model.dec.index[model.dec["GEN UID"].eq("121_NUCLEAR_1")].item()
    assert not any(t * ng + nuclear in cap_indices for t in range(h))
    bounds = {"column_lower": lower, "column_upper": upper,
              "row_lower": np.asarray(lo), "row_upper": np.asarray(hi)}
    objective = np.zeros(npower + nangle)
    metadata = {"hours": h, "units": ng, "buses": nb, "branches": nl,
                "power_columns": npower, "angle_columns": nangle, "columns": matrix.shape[1],
                "rows": matrix.shape[0], "nonzeros": matrix.nnz,
                "unit_names": model.dec["GEN UID"].tolist(), "bus_ids": model.busids,
                "thermal_units": model.dec.iloc[model.urows]["GEN UID"].tolist(),
                "fossil_units": model.dec.iloc[fossil]["GEN UID"].tolist(),
                "fossil_column_indices": cap_indices,
                "budget_MWh": budget, "objective": "zero feasibility objective",
                "individual_mean_constraints": 0, "commitment": "all 24 thermal units ON for all 168 hours",
                "initial_history": "free mature initial ON status, no startup at hour zero",
                "power_column_order": "hour-major then unit", "angle_column_order": "hour-major then bus after power block"}
    return matrix, bounds, objective, metadata, labels, np.asarray(nodal)


def reconstruct_angles(model, p, nodal):
    keep = [bus for bus in range(len(model.busids)) if bus != model.slack]
    reduced = model.Bbus[np.ix_(keep, keep)]
    result = []
    for power, load in zip(p, nodal):
        injection = -load.copy()
        for j, generator in model.dec.iterrows():
            injection[model.bi[int(generator["Bus ID"])]] += power[j]
        theta = np.zeros(len(model.busids))
        theta[keep] = np.linalg.solve(reduced, injection[keep])
        result.append(theta)
    return np.asarray(result)


def direct_check(model, p, theta, pmin, pmax, net, rows, nodal, fossil, budget):
    u = np.ones((len(p), len(model.urows)))
    y = np.zeros_like(u)
    physical = verify(model, p, u, pmin, pmax, net, p.mean(0), "minud", y, y)
    ramps = verify(model, p, u, pmin, pmax, net, p.mean(0), "ramp")
    # No individual mean target is imposed in this experiment; the generic
    # verification API's self-mean check is not presented as target matching.
    physical["residuals"].pop("mean_MW")
    ramps["residuals"].pop("mean_MW")
    reconstructed, _ = nodal_check(model, p, rows)
    max_nodal = max_line = 0.0
    for power, angles, load in zip(p, theta, nodal):
        injection = -load.copy()
        for j, generator in model.dec.iterrows():
            injection[model.bi[int(generator["Bus ID"])]] += power[j]
        max_nodal = max(max_nodal, float(np.max(np.abs(model.Bbus @ angles - injection))))
        flow = model.bl * (model.A.T @ angles)
        max_line = max(max_line, float(np.max(np.abs(flow) - model.rate)))
    energy = sum((Fraction.from_float(float(value)) for value in p[:, fossil].ravel()), Fraction(0))
    excess = max(Fraction(0), energy - Fraction.from_float(budget))
    residuals = {"provided_angle_nodal_balance_MW": max_nodal,
                 "provided_angle_branch_excess_MW": max_line,
                 "angle_bound_rad": max(0., float(np.max(np.abs(theta))) - np.pi),
                 "slack_angle_rad": float(np.max(np.abs(theta[:, model.slack]))),
                 "fossil_cap_excess_MWh": float(excess)}
    good = physical["pass"] and ramps["pass"] and reconstructed["pass"] and max(residuals.values()) <= TOL
    return {"pass": bool(good), "tolerance": TOL, "physical_chronology": physical,
            "native_on_on_ramp": ramps, "dispatch_reconstructed_network": reconstructed,
            "additional_residuals": residuals, "fossil_energy_MWh": float(energy),
            "exact_binary64_fossil_energy_numerator": str(energy.numerator),
            "exact_binary64_fossil_energy_denominator": str(energy.denominator),
            "budget_MWh": budget, "individual_mean_target": "none"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-v3", type=Path, required=True)
    args = parser.parse_args()
    output = ROOT / "results/research8h/service_network"
    output.mkdir(parents=True, exist_ok=False)
    protocol = ROOT / "docs/research8h/SERVICE_NETWORK_PROTOCOL.md"
    cap_source = ROOT / "results/research8h/service_cap/pre_run_freeze.json"
    budget = json.loads(cap_source.read_text())["budget_MWh"]
    save(output / "pre_run_freeze.json", {"frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "script_sha256": digest(Path(__file__)), "protocol_sha256": digest(protocol),
        "source_budget_sha256": digest(cap_source), "budget_MWh": budget,
        "optimization_runs": 1, "time_limit_s": 60, "threads": 1, "random_seed": 0,
        "solver": "simplex", "presolve": "off", "commitment": "all thermal units always ON",
        "permutation_replays_if_feasible": CASES[1:]})
    model = load_model(args.source_v3)
    names, _, pmin, pmax, net, native_paths = inputs(model, args.source_v3, 7)
    rows = pd.read_csv(native_paths[1])["row"].to_numpy(int)
    thermal = model.dec.iloc[model.urows]
    rate = thermal["Ramp Rate MW/Min"].to_numpy(float) * 60
    variation = thermal["PMax MW"].to_numpy(float) - thermal["PMin MW"].to_numpy(float)
    assert np.all(rate >= variation)
    assert np.all(pmin[:, model.urows] == thermal["PMin MW"].to_numpy(float))
    assert np.all(pmax[:, model.urows] == thermal["PMax MW"].to_numpy(float))
    pd.DataFrame({"uid": thermal["GEN UID"], "hourly_ramp_MW": rate,
                  "largest_possible_on_on_change_MW": variation, "redundancy_margin_MW": rate-variation}).to_csv(output / "ramp_redundancy.csv", index=False)
    matrix, bounds, objective, metadata, labels, nodal = assemble(model, pmin, pmax, rows, budget)
    save_npz(output / "matrix.npz", matrix)
    np.savez_compressed(output / "bounds.npz", **bounds)
    np.savez_compressed(output / "objective.npz", objective=objective)
    save(output / "model_metadata.json", metadata)
    pd.DataFrame(labels).to_csv(output / "row_metadata.csv.gz", index=False, compression="gzip")
    reference = ROOT / "results/v8/network_repair"
    p_path, u_path = reference / "network_repair_dispatch.csv", reference / "network_fixed_commitment.csv"
    rp = pd.read_csv(p_path)[names].to_numpy(float)
    ru = pd.read_csv(u_path)[thermal["GEN UID"]].to_numpy(float)
    rt = reconstruct_angles(model, rp, nodal)
    reference_bounds = {key: value.copy() for key, value in bounds.items()}
    lower = reference_bounds["column_lower"][:pmin.size].reshape(pmin.shape)
    upper = reference_bounds["column_upper"][:pmax.size].reshape(pmax.shape)
    lower[:, model.urows] = pmin[:, model.urows] * ru
    upper[:, model.urows] = pmax[:, model.urows] * ru
    grounding = check_vector(matrix, reference_bounds, np.r_[rp.ravel(), rt.ravel()])
    assert grounding["pass"], grounding
    save(output / "reference_network_grounding.json", {"check": grounding,
        "meaning": "Existing reference checked with its own frozen commitment bounds, not claimed feasible for the all-on restriction."})
    save(output / "all_on_aggregate_diagnostic.json", {
        "max_minimum_generation_excess_over_net_load_MW": float(np.max(pmin.sum(1)-net)),
        "minimum_all_on_generation_MW": float(np.min(pmin.sum(1))),
        "minimum_net_load_MW": float(np.min(net)),
        "interpretation": "Diagnostic for this fixed all-on restriction only; not unrestricted UC."})
    manifest_paths = [Path(__file__), protocol, cap_source, p_path, u_path,
        ROOT / "src/temporal_information_pilot.py", ROOT / "src/temporal_lp_certificate.py",
        ROOT / "src/v8r1_rts_seasonal.py", ROOT / "src/reproduce_network_repair_upper_bound.py",
        *native_paths, args.source_v3 / "code/dscgrid_model.py", *sorted((args.source_v3 / "raw").rglob("*.csv"))]
    for case in CASES[1:]:
        manifest_paths.append(ROOT / "results/temporal_information/twins" / case / "permutation.csv")
    pd.DataFrame([{"path": str(path), "sha256": digest(path), "bytes": path.stat().st_size}
                  for path in dict.fromkeys(manifest_paths)]).to_csv(output / "input_manifest.csv", index=False)
    lp = highspy.HighsLp()
    lp.num_row_, lp.num_col_ = matrix.shape
    lp.col_cost_, lp.col_lower_, lp.col_upper_ = objective, bounds["column_lower"], bounds["column_upper"]
    lp.row_lower_, lp.row_upper_ = bounds["row_lower"], bounds["row_upper"]
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.num_row_, lp.a_matrix_.num_col_ = matrix.shape
    lp.a_matrix_.start_, lp.a_matrix_.index_, lp.a_matrix_.value_ = matrix.indptr, matrix.indices, matrix.data
    solver = highspy.Highs()
    for option, value in [("time_limit",60.0),("threads",1),("random_seed",0),("solver","simplex"),
                          ("presolve","off"),("log_to_console",False),("log_file",str(output / "solver.log"))]:
        solver.setOptionValue(option,value)
    solver.passModel(lp)
    started = time.perf_counter(); solver.run(); elapsed = time.perf_counter()-started
    status = solver.getModelStatus(); solution = solver.getSolution()
    result = {"model_status": solver.modelStatusToString(status), "solver_version": solver.version(),
              "elapsed_s": elapsed, "time_limit_s": 60, "verdict": "NO_VERIFIED_ALL_ON_WITNESS",
              "matrix_sha256": digest(output / "matrix.npz"), "bounds_sha256": digest(output / "bounds.npz"),
              "interpretation": "Only the fixed all-thermal-on restriction is tested; failure is not an unrestricted UC rejection."}
    if solution.value_valid:
        vector = np.asarray(solution.col_value)
        np.savez_compressed(output / "returned_vector.npz", vector=vector)
        result["matrix_vector_check"] = check_vector(matrix, bounds, vector)
        if result["matrix_vector_check"]["pass"]:
            p = vector[:pmin.size].reshape(pmin.shape)
            theta = vector[pmin.size:].reshape(len(p), len(model.busids))
            fossil = [names.index(uid) for uid in metadata["fossil_units"]]
            checks = []
            for case in CASES:
                order = np.arange(len(p)) if case == "identity" else pd.read_csv(
                    ROOT / "results/temporal_information/twins" / case / "permutation.csv")["source_hour_0based"].to_numpy(int)
                assert sorted(order) == list(range(len(p)))
                check = direct_check(model, p[order], theta[order], pmin[order], pmax[order], net[order], rows[order], nodal[order], fossil, budget)
                directory = output / case; directory.mkdir()
                save(directory / "witness_verification.json", check)
                pd.DataFrame(p[order],columns=names).to_csv(directory / "dispatch.csv",index=False)
                pd.DataFrame(theta[order],columns=model.busids).to_csv(directory / "angles.csv",index=False)
                pd.DataFrame(np.ones((len(p),len(model.urows)),dtype=int),columns=thermal["GEN UID"]).to_csv(directory / "commitment.csv",index=False)
                assert check["pass"], (case,check)
                checks.append({"case":case,"verdict":"ADMITTED_BINARY_DC_NETWORK_SERVICE","verification":check})
            save(output / "replay_summary.json",checks)
            result["verdict"]="ADMITTED_BINARY_DC_NETWORK_SERVICE_ALL_FIVE_CASES"
            result["verified_cases"]=len(checks)
    if status == highspy.HighsModelStatus.kInfeasible:
        assert result["verdict"] != "ADMITTED_BINARY_DC_NETWORK_SERVICE_ALL_FIVE_CASES"
        result["verdict"]="ALL_ON_RESTRICTION_INFEASIBLE"
    save(output / "result.json",result)
    print(json.dumps(result,indent=2),flush=True)


if __name__=="__main__":
    main()
