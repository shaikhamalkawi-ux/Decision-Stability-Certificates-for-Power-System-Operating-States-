"""Frozen paired-order RTS pilot with independently checked rejection cores.

No rejection is inferred merely from an invalid permuted seed schedule.
All positive/negative/unknown statuses are evidence-specific.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from v8r1_rts_seasonal import inputs, load_model, solve, verify
from v8r1_rts_residence_certificate import (
    POWER_TOL, ENERGY_TOL, propagate, reachability, validate_reachability,
)
from check_temporal_core import compatible_counts, validate as validate_checker

ROOT = Path(__file__).resolve().parents[1]
SEEDS = list(range(26092600, 26092616))
EDGE = 48


def save(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False), encoding="utf-8")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transitions(u):
    y = np.zeros_like(u)
    z = np.zeros_like(u)
    y[1:] = np.maximum(0, np.diff(u, axis=0))
    z[1:] = np.maximum(0, -np.diff(u, axis=0))
    return y, z


def nodal_check(model, dispatch, rows):
    """Reconstruct nodal injections and DC flows from portable native inputs."""
    keep = [i for i in range(len(model.busids)) if i != model.slack]
    b = model.Bbus[np.ix_(keep, keep)]
    max_balance = max_line_excess = max_nodal = max_loading = 0.0
    nodal_net = []
    for p, row in zip(dispatch, rows):
        total = float(model.load_ts.loc[int(row), str(model.AREA)])
        net = model.prop * total - model.rtpv_at(int(row))
        nodal_net.append(net)
        injection = -net.copy()
        for j, generator in model.dec.iterrows():
            injection[model.bi[int(generator["Bus ID"])]] += p[j]
        angle = np.zeros(len(model.busids))
        angle[keep] = np.linalg.solve(b, injection[keep])
        flow = model.bl * (model.A.T @ angle)
        max_balance = max(max_balance, float(abs(injection.sum())))
        max_nodal = max(max_nodal, float(np.max(np.abs(model.Bbus @ angle - injection))))
        max_line_excess = max(max_line_excess, float(np.max(np.abs(flow) - model.rate)))
        max_loading = max(max_loading, float(np.max(np.abs(flow) / model.rate)))
    result = {"balance_MW": max_balance, "nodal_balance_MW": max_nodal,
              "branch_excess_MW": max_line_excess, "max_branch_loading": max_loading}
    result["pass"] = max(max_balance, max_nodal, max_line_excess) <= POWER_TOL
    return result, np.asarray(nodal_net)


def reject(on, off, up, down, low, high):
    return not any(low <= count <= high for count in reachability(on, off, up, down))


def compact_core(unit, lower, upper, horizon):
    """Greedy deletion in increasing-hour order; inclusion-minimal, not smallest."""
    on = np.zeros(horizon, dtype=bool)
    off = np.zeros(horizon, dtype=bool)
    on[unit["forced_on_hours_0based"]] = True
    off[unit["forced_off_hours_0based"]] = True
    initial_atoms = int(on.sum() + off.sum())
    params = (unit["min_up_hours"], unit["min_down_hours"],
              unit["energy_count_lower"], unit["energy_count_upper"])
    assert reject(on, off, *params)
    for hour in range(horizon):
        for values in (on, off):
            if not values[hour]:
                continue
            values[hour] = False
            if not reject(on, off, *params):
                values[hour] = True
    assert reject(on, off, *params)
    independent = compatible_counts(horizon, np.flatnonzero(on).tolist(),
                                    np.flatnonzero(off).tolist(), *params)
    assert not independent, (unit["uid"], independent)
    irreducible_checks = []
    for hour in range(horizon):
        for status, values in ((1, on), (0, off)):
            if not values[hour]:
                continue
            values[hour] = False
            admitted = compatible_counts(horizon, np.flatnonzero(on).tolist(),
                                         np.flatnonzero(off).tolist(), *params)
            values[hour] = True
            assert admitted, "Retained status is redundant"
            irreducible_checks.append({"removed_hour": hour, "removed_status": status,
                                       "remaining_compatible_count_example": admitted[0]})
    atoms = []
    for hour in range(horizon):
        if on[hour] or off[hour]:
            atoms.append({"hour_0based": hour, "status": int(on[hour]),
                          "necessary_lower_MW": float(lower[hour]),
                          "necessary_upper_MW": float(upper[hour])})
    return {"uid": unit["uid"], "horizon": horizon,
            "pmin_MW": unit["pmin_MW"], "pmax_MW": unit["pmax_MW"],
            "energy_MWh": unit["energy_MWh"], "min_up_hours": params[0],
            "min_down_hours": params[1], "energy_count_lower": params[2],
            "energy_count_upper": params[3], "initial_atom_count": initial_atoms,
            "retained_atom_count": len(atoms), "atoms": atoms,
            "independent_rejection_check": "PASS",
            "single_atom_removal_checks": irreducible_checks,
            "minimality": "inclusion-minimal among the selected unit's forced-status atoms; not global minimum cardinality",
            "input_dependency": "Full 168-hour availability and demand, all 41 target energies, and all-unit propagation are retained; this is explanation sparsity, not demonstrated raw-data compression."}


def certificate(model, pmin, pmax, net, energy, output):
    ti = np.flatnonzero(model.thermal.to_numpy(bool))
    hydro = model.dec.Category.eq("Hydro").to_numpy()
    h = len(net)
    mins = model.dec.iloc[ti]["PMin MW"].to_numpy(float)
    maxs = model.dec.iloc[ti]["PMax MW"].to_numpy(float)
    up = np.ceil(model.dec.iloc[ti]["Min Up Time Hr"].to_numpy(float)).astype(int)
    down = np.ceil(model.dec.iloc[ti]["Min Down Time Hr"].to_numpy(float)).astype(int)
    assert h == 168 and max(up.max(), down.max()) <= EDGE
    assert np.all(pmin[:, ti] == mins) and np.all(pmax[:, ti] == maxs)
    initial_lower = np.zeros_like(pmin)
    initial_lower[:, hydro] = pmin[:, hydro]
    started = time.perf_counter()
    lo, hi, iterations = propagate(initial_lower, pmax, energy, net, ti, mins)
    propagation_s = time.perf_counter() - started
    started = time.perf_counter()
    units = []
    for q, j in enumerate(ti):
        on = lo[:, j] > POWER_TOL
        off = hi[:, j] < mins[q] - POWER_TOL
        counts = reachability(on, off, int(up[q]), int(down[q]))
        lower_count = max(0, int(np.ceil((energy[j] - ENERGY_TOL) / (maxs[q] + POWER_TOL))))
        upper_count = min(h, int(np.floor((energy[j] + ENERGY_TOL) / (mins[q] - POWER_TOL))))
        compatible = [c for c in counts if lower_count <= c <= upper_count]
        units.append({"uid": str(model.dec.iloc[j]["GEN UID"]), "unit_index": int(j),
                      "energy_MWh": float(energy[j]), "pmin_MW": float(mins[q]),
                      "pmax_MW": float(maxs[q]), "min_up_hours": int(up[q]),
                      "min_down_hours": int(down[q]), "energy_count_lower": lower_count,
                      "energy_count_upper": upper_count, "residence_reachable_counts": counts,
                      "energy_compatible_counts": compatible,
                      "forced_on_hours_0based": np.flatnonzero(on).tolist(),
                      "forced_off_hours_0based": np.flatnonzero(off).tolist(),
                      "necessary_condition": "PASS" if compatible else "FAIL"})
    reachability_s = time.perf_counter() - started
    failures = [u for u in units if u["necessary_condition"] == "FAIL"]
    started = time.perf_counter()
    core = None
    if failures:
        first = failures[0]
        core = compact_core(first, lo[:, first["unit_index"]], hi[:, first["unit_index"]], h)
        save(output / "compact_core.json", core)
    extraction_s = time.perf_counter() - started
    result = {"verdict": "REJECTED_NECESSARY_CONDITION" if failures else "UNKNOWN",
              "failing_units": [u["uid"] for u in failures], "units": units,
              "propagation_iterations": iterations, "propagation_s": propagation_s,
              "reachability_s": reachability_s, "core_extraction_and_checks_s": extraction_s,
              "power_tolerance_MW": POWER_TOL, "energy_tolerance_MWh": ENERGY_TOL}
    pd.DataFrame(lo, columns=model.dec["GEN UID"]).to_csv(output / "necessary_lower_MW.csv", index=False)
    pd.DataFrame(hi, columns=model.dec["GEN UID"]).to_csv(output / "necessary_upper_MW.csv", index=False)
    save(output / "certificate.json", result)
    return result, core


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-v3", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "results/temporal_information/twins")
    parser.add_argument("--seconds", type=float, default=60)
    parser.add_argument("--skip-solvers", action="store_true", help="Only replay certificate/witness checks; records cross-check omission.")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    model = load_model(args.source_v3)
    columns, _, pmin, pmax, net, paths = inputs(model, args.source_v3, 7)
    source_rows = pd.read_csv(paths[1])["row"].to_numpy(int)
    witness_dir = ROOT / "results/v8/network_repair"
    p_path = witness_dir / "network_repair_dispatch.csv"
    u_path = witness_dir / "network_fixed_commitment.csv"
    p = pd.read_csv(p_path)[columns].to_numpy(float)
    thermal_names = model.dec.iloc[model.urows]["GEN UID"].tolist()
    u = pd.read_csv(u_path)[thermal_names].to_numpy(float)
    mu, energy = p.mean(axis=0), p.sum(axis=0)
    y, z = transitions(u)
    check = verify(model, p, u, pmin, pmax, net, mu, "minud", y, z)
    ramp = verify(model, p, u, pmin, pmax, net, mu, "ramp")
    network, nodal_net = nodal_check(model, p, source_rows)
    assert check["pass"] and ramp["pass"] and network["pass"], (check, ramp, network)
    save(args.output / "positive_witness_verification.json",
         {"chronology": check, "on_on_ramp": ramp, "network": network,
          "dispatch_sha256": sha(p_path), "commitment_sha256": sha(u_path),
          "target": "verified repaired network witness's complete mean, not the original static mean"})
    save(args.output / "dp_exhaustive_validation.json", validate_reachability())
    save(args.output / "independent_checker_validation.json", validate_checker())
    pd.DataFrame({"uid": columns, "target_mean_MW": mu, "target_energy_MWh": energy}).to_csv(
        args.output / "shared_target.csv", index=False)
    packages = np.column_stack([source_rows, nodal_net, pmin, pmax, p, u])
    package_hash = hashlib.sha256(np.ascontiguousarray(packages).tobytes()).hexdigest()
    summary = []
    pending = []
    for index, seed in enumerate([None, *SEEDS]):
        name = "identity" if seed is None else f"seed_{seed}"
        output = args.output / name
        output.mkdir(exist_ok=True)
        order = np.arange(len(p))
        if seed is not None:
            order[EDGE:-EDGE] = np.random.Generator(np.random.PCG64(seed)).permutation(order[EDGE:-EDGE])
        inverse = np.argsort(order)
        assert np.array_equal(np.sort(order), np.arange(len(p)))
        assert np.array_equal(order[:EDGE], np.arange(EDGE))
        assert np.array_equal(order[-EDGE:], np.arange(len(p) - EDGE, len(p)))
        assert np.array_equal(packages[order][inverse], packages)
        restored_hash = hashlib.sha256(np.ascontiguousarray(packages[order][inverse]).tobytes()).hexdigest()
        assert restored_hash == package_hash
        mean_error = float(np.max(np.abs(p[order].mean(axis=0) - mu)))
        assert mean_error < 1e-9
        static = verify(model, p[order], u[order], pmin[order], pmax[order], net[order], mu, "static")
        static_network, permuted_nodal = nodal_check(model, p[order], source_rows[order])
        assert static["pass"] and static_network["pass"]
        assert np.array_equal(permuted_nodal[inverse], nodal_net)
        py, pz = transitions(u[order])
        replay = verify(model, p[order], u[order], pmin[order], pmax[order], net[order], mu, "minud", py, pz)
        pd.DataFrame({"new_hour_0based": np.arange(len(p)), "source_hour_0based": order,
                      "source_native_row": source_rows[order]}).to_csv(output / "permutation.csv", index=False)
        result, core = certificate(model, pmin[order], pmax[order], net[order], energy, output)
        if seed is None:
            assert result["verdict"] == "UNKNOWN", "False rejection of verified positive control"
        preservation = {"original_package_sha256": package_hash, "inverse_restored_package_sha256": restored_hash,
                        "joint_hourly_multiset_exactly_preserved": True, "mean_error_MW": mean_error,
                        "fixed_edge_hours_each_side": EDGE, "static_witness": static,
                        "static_network_witness": static_network,
                        "permuted_seed_chronology_check": replay,
                        "warning": "A failed seed replay alone does not rule out an alternative schedule."}
        save(output / "preservation_and_seed_checks.json", preservation)
        record = {"case": name, "seed": seed, "subset": "control" if seed is None else ("development" if seed < SEEDS[8] else "held_out_same_week"),
                  "certificate_verdict": result["verdict"],
                  "combined_verdict": "ADMITTED_NETWORK_WITNESS" if seed is None else result["verdict"],
                  "failing_unit_count": len(result["failing_units"]),
                  "core_unit": core["uid"] if core else None,
                  "core_atoms": core["retained_atom_count"] if core else None,
                  "propagation_s": result["propagation_s"], "reachability_s": result["reachability_s"],
                  "core_extraction_and_checks_s": result["core_extraction_and_checks_s"],
                  "permuted_seed_residence_violations": replay["residuals"]["residence_violations"],
                  "full_solver_status": "NOT_SELECTED" if index > 4 or index == 0 else "PENDING"}
        summary.append(record)
        if 1 <= index <= 4:
            pending.append((record, order, output))
        save(args.output / "summary.json", summary)
        print(json.dumps(record), flush=True)
    for record, order, output in pending:
        if args.skip_solvers:
            record["full_solver_status"] = "SKIPPED_BY_CLI"
            continue
        # Only target.mean is used in solve: retain the unchanged original mean.
        full = solve(model, 7, "minud", p, pmin[order], pmax[order], net[order], output, args.seconds)
        save(output / "full_solver_crosscheck.json", full)
        record["full_solver_status"] = full["model_status"]
        record["full_solver_verdict"] = full["verdict"]
        record["full_solver_elapsed_s"] = full["elapsed_s"]
        assert not (record["certificate_verdict"] == "REJECTED_NECESSARY_CONDITION" and full["verdict"] == "ADMITTED_RELAXATION"), "Certificate/feasible-witness contradiction"
        if record["certificate_verdict"] == "UNKNOWN":
            record["combined_verdict"] = full["verdict"]
        save(args.output / "summary.json", summary)
        print(json.dumps({"case": record["case"], "full_solver": full["verdict"], "seconds": full["elapsed_s"]}), flush=True)
    save(args.output / "summary.json", summary)
    pd.DataFrame(summary).to_csv(args.output / "summary.csv", index=False)
    inputs_used = [Path(__file__), ROOT / "src/check_temporal_core.py", ROOT / "src/v8r1_rts_seasonal.py",
                   ROOT / "src/v8r1_rts_residence_certificate.py", ROOT / "docs/TEMPORAL_INFORMATION_PROTOCOL.md",
                   p_path, u_path, *paths, args.source_v3 / "code/dscgrid_model.py",
                   *sorted((args.source_v3 / "raw").rglob("*.csv"))]
    pd.DataFrame([{"path": str(path), "sha256": sha(path), "bytes": path.stat().st_size}
                  for path in dict.fromkeys(inputs_used)]).to_csv(args.output / "input_manifest.csv", index=False)


if __name__ == "__main__":
    main()
