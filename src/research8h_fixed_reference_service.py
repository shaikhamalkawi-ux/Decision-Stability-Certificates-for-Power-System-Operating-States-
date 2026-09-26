"""One frozen fixed-reference dispatch LP for each of four July twins."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import time

import highspy
import numpy as np
import pandas as pd
from scipy.sparse import load_npz

from research8h_service_network_mip import direct_check, unpack
from temporal_lp_certificate import check_vector, digest, save
from v8r1_rts_seasonal import load_model

ROOT = Path(__file__).resolve().parents[1]
CASES = [f"seed_{s}" for s in range(26092600, 26092604)]
SECONDS = 30


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-v3", type=Path, required=True)
    args = parser.parse_args()
    output = ROOT / "results/research8h/fixed_reference_service"
    output.mkdir(parents=True, exist_ok=False)
    archive = ROOT / "results/research8h/service_network_mip"
    protocol = ROOT / "docs/research8h/FIXED_REFERENCE_SERVICE_PROTOCOL.md"
    model = load_model(args.source_v3)
    names = model.dec["GEN UID"].tolist()
    thermal_names = model.dec.iloc[model.urows]["GEN UID"].tolist()
    reference = ROOT / "results/v8/network_repair"
    pp = reference / "network_repair_dispatch.csv"
    up = reference / "network_fixed_commitment.csv"
    rp = pd.read_csv(pp)[names].to_numpy(float)
    ru = pd.read_csv(up)[thermal_names].to_numpy(float)
    assert np.array_equal(ru, np.rint(ru))
    ry, rz = np.zeros_like(ru), np.zeros_like(ru)
    ry[1:], rz[1:] = np.maximum(np.diff(ru, axis=0), 0), np.maximum(-np.diff(ru, axis=0), 0)
    fixed = np.concatenate([a.ravel() for a in (ru, ry, rz)])
    input_paths = [Path(__file__), protocol, pp, up,
                   ROOT / "src/research8h_service_network_mip.py",
                   ROOT / "src/research8h_service_network.py",
                   ROOT / "src/temporal_lp_certificate.py",
                   ROOT / "src/temporal_information_pilot.py",
                   ROOT / "src/v8r1_rts_seasonal.py",
                   args.source_v3 / "code/dscgrid_model.py",
                   *sorted((args.source_v3 / "raw").rglob("*.csv"))]
    prepared = []
    for case in CASES:
        src = archive / case
        matrix = load_npz(src / "matrix.npz")
        with np.load(src / "bounds.npz") as data:
            bounds = {k: data[k].copy() for k in data.files}
        with np.load(src / "native_inputs.npz") as data:
            native = {k: data[k].copy() for k in data.files}
        with np.load(src / "integrality.npz") as data:
            integer = data["integrality"].astype(bool)
        meta = json.loads((src / "model_metadata.json").read_text())
        assert meta["individual_mean_constraints"] == 0
        start, end = rp.size, rp.size + fixed.size
        assert np.array_equal(np.flatnonzero(integer), np.arange(start, end))
        assert np.all(fixed >= bounds["column_lower"][start:end])
        assert np.all(fixed <= bounds["column_upper"][start:end])
        bounds["column_lower"][start:end] = fixed
        bounds["column_upper"][start:end] = fixed
        directory = output / case
        directory.mkdir()
        np.savez_compressed(directory / "fixed_bounds.npz", **bounds)
        save(directory / "model_binding.json", {
            "source_matrix": str((src / "matrix.npz").relative_to(ROOT)),
            "matrix_sha256": digest(src / "matrix.npz"),
            "source_bounds_sha256": digest(src / "bounds.npz"),
            "fixed_bounds_sha256": digest(directory / "fixed_bounds.npz"),
            "fixed_integer_columns": int(integer.sum()),
            "matrix_unchanged": True, "objective": "zero",
            "budget_MWh": meta["budget_MWh"], "mean_constraints": 0})
        input_paths.extend(src / n for n in ("matrix.npz", "bounds.npz", "native_inputs.npz",
                                             "integrality.npz", "model_metadata.json"))
        input_paths.append(directory / "fixed_bounds.npz")
        prepared.append((case, directory, matrix, bounds, meta, native))
    pd.DataFrame([{"path": str(p), "sha256": digest(p), "bytes": p.stat().st_size}
                  for p in dict.fromkeys(input_paths)]).to_csv(output / "input_manifest.csv", index=False)
    save(output / "models_frozen_before_first_solve.json", {
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(), "cases": CASES,
        "input_manifest_sha256": digest(output / "input_manifest.csv"),
        "seconds_per_case": SECONDS, "threads": 1, "random_seed": 0, "presolve": "on",
        "warm_start": False, "fixed_schedule": "original reference, not permuted"})
    results = []
    for case, directory, matrix, bounds, meta, native in prepared:
        lp = highspy.HighsLp()
        lp.num_row_, lp.num_col_ = matrix.shape
        lp.col_cost_ = np.zeros(matrix.shape[1])
        lp.col_lower_, lp.col_upper_ = bounds["column_lower"], bounds["column_upper"]
        lp.row_lower_, lp.row_upper_ = bounds["row_lower"], bounds["row_upper"]
        lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
        lp.a_matrix_.num_row_, lp.a_matrix_.num_col_ = matrix.shape
        lp.a_matrix_.start_, lp.a_matrix_.index_, lp.a_matrix_.value_ = matrix.indptr, matrix.indices, matrix.data
        solver = highspy.Highs()
        for option, value in [("time_limit", float(SECONDS)), ("threads", 1), ("random_seed", 0),
                              ("presolve", "on"), ("log_to_console", False),
                              ("log_file", str(directory / "solver.log"))]:
            assert solver.setOptionValue(option, value) == highspy.HighsStatus.kOk
        assert solver.passModel(lp) == highspy.HighsStatus.kOk
        started = time.perf_counter()
        solver.run()
        elapsed = time.perf_counter() - started
        status, solution = solver.getModelStatus(), solver.getSolution()
        record = {"case": case, "model_status": solver.modelStatusToString(status),
                  "verdict": "UNKNOWN", "elapsed_s": elapsed, "time_limit_s": SECONDS,
                  "optimization_calls": 1, "solver_version": solver.version()}
        if solution.value_valid:
            vector = np.asarray(solution.col_value)
            np.savez_compressed(directory / "returned_vector.npz", vector=vector)
            record["matrix_check"] = check_vector(matrix, bounds, vector)
            p, u, y, z, theta = unpack(vector, len(rp), len(names), len(thermal_names), len(model.busids))
            record["fixed_schedule_exact"] = bool(np.array_equal(
                np.concatenate([a.ravel() for a in (u, y, z)]), fixed))
            check = direct_check(model, p, u, y, z, theta, native["pmin"], native["pmax"],
                                 native["net"], native["rows"], native["nodal"],
                                 [names.index(uid) for uid in meta["fossil_units"]], meta["budget_MWh"])
            save(directory / "physical_check.json", check)
            record["physical_check_pass"] = check["pass"]
            if check["pass"] and record["matrix_check"]["pass"] and record["fixed_schedule_exact"]:
                record["verdict"] = "ADMITTED_BINARY_DC_NETWORK_SERVICE"
                for filename, values, columns in [("dispatch", p, names), ("commitment", u, thermal_names),
                    ("startup", y, thermal_names), ("shutdown", z, thermal_names), ("angles", theta, model.busids)]:
                    pd.DataFrame(values, columns=columns).to_csv(directory / f"{filename}.csv", index=False)
                record["descriptive_mean_L1_change_MW"] = float(np.abs(p.mean(0) - rp.mean(0)).sum())
                record["fossil_energy_MWh"] = check["fossil_energy_MWh"]
                record["budget_MWh"] = meta["budget_MWh"]
        if status == highspy.HighsModelStatus.kInfeasible:
            assert record["verdict"] != "ADMITTED_BINARY_DC_NETWORK_SERVICE"
            record["verdict"] = "FIXED_SCHEDULE_INFEASIBLE_ONLY"
        save(directory / "result.json", record)
        results.append(record)
        save(output / "summary.json", results)
        print(json.dumps({k: record[k] for k in ("case", "model_status", "verdict", "elapsed_s")}), flush=True)
    pd.DataFrame([{k: v for k, v in r.items() if not isinstance(v, (dict, list))}
                  for r in results]).to_csv(output / "summary.csv", index=False)


if __name__ == "__main__":
    main()
