"""Frozen U-only integrality continuation with checked auxiliary recovery."""
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
SECONDS = 600
TOL = 1e-5


def audit_projection(matrix, bounds, meta, labels, old_integer):
    h, ng, nk = meta["hours"], meta["units"], meta["thermal_units"]
    offsets = meta["offsets"]
    p0, u0, y0, z0, a0 = [offsets[k] for k in ("P", "U", "Y", "Z", "theta")]
    assert p0 == 0 and u0 == h*ng and y0 == u0+h*nk and z0 == y0+h*nk and a0 == z0+h*nk
    assert np.array_equal(np.flatnonzero(old_integer), np.arange(u0, a0))
    assert np.all(bounds["column_lower"][u0:a0] == 0)
    upper = bounds["column_upper"][u0:a0].copy()
    expected = np.ones_like(upper)
    expected[y0-u0:y0-u0+nk] = 0
    expected[z0-u0:z0-u0+nk] = 0
    assert np.array_equal(upper, expected)
    checked = {family: 0 for family in ("transition", "exclusive_transition", "minimum_up", "minimum_down")}
    thermal = meta["thermal_unit_names"]
    assert np.array_equal(labels["row"].to_numpy(int), np.arange(matrix.shape[0]))
    for row, label in labels.iterrows():
        start, end = matrix.indptr[row:row+2]
        entries = dict(zip(matrix.indices[start:end].tolist(), matrix.data[start:end].tolist()))
        aux = {j: v for j, v in entries.items() if y0 <= j < a0}
        family = label["family"]
        if not aux:
            assert family not in checked
            continue
        assert family in checked, (row, family)
        t, unit = int(label["hour_0based"]), thermal.index(label["uid"])
        assert 1 <= t < h
        uc, yc, zc = u0+t*nk+unit, y0+t*nk+unit, z0+t*nk+unit
        lo, hi = bounds["row_lower"][row], bounds["row_upper"][row]
        if family == "transition":
            assert entries == {uc: 1., uc-nk: -1., yc: -1., zc: 1.} and lo == hi == 0
        elif family == "exclusive_transition":
            assert entries == {yc: 1., zc: 1.} and np.isneginf(lo) and hi == 1
        else:
            target_start, target_end = (y0, z0) if family == "minimum_up" else (z0, a0)
            assert all(target_start <= j < target_end and v == 1. for j, v in aux.items())
            assert all((j-target_start) % nk == unit and 1 <= (j-target_start)//nk <= t for j in aux)
            assert {j: v for j, v in entries.items() if j not in aux} == {uc: -1. if family == "minimum_up" else 1.}
            assert np.isneginf(lo) and hi == (0 if family == "minimum_up" else 1)
        checked[family] += 1
    assert all(v == (h-1)*nk for v in checked.values())
    integer = np.zeros(matrix.shape[1], dtype=np.uint8)
    integer[u0:y0] = 1
    return integer, {"pass": True, "old_integer_columns": int(old_integer.sum()),
                     "new_integer_columns": int(integer.sum()), "rows_checked_by_family": checked,
                     "all_other_rows_free_of_auxiliary_coordinates": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-v3", type=Path, required=True)
    args = parser.parse_args()
    output = ROOT / "results/research8h/u_only_continuation"
    output.mkdir(parents=True, exist_ok=False)
    archive = ROOT / "results/research8h/service_network_mip"
    protocol = ROOT / "docs/research8h/U_ONLY_CONTINUATION_PROTOCOL.md"
    model = load_model(args.source_v3)
    paths = [Path(__file__), protocol, ROOT/"src/research8h_service_network_mip.py",
             ROOT/"src/research8h_service_network.py", ROOT/"src/temporal_lp_certificate.py",
             ROOT/"src/temporal_information_pilot.py", ROOT/"src/v8r1_rts_seasonal.py",
             args.source_v3/"code/dscgrid_model.py", *sorted((args.source_v3/"raw").rglob("*.csv"))]
    prepared = []
    for case in CASES:
        src = archive/case
        matrix = load_npz(src/"matrix.npz")
        with np.load(src/"bounds.npz") as data:
            bounds = {k: data[k].copy() for k in data.files}
        with np.load(src/"native_inputs.npz") as data:
            native = {k: data[k].copy() for k in data.files}
        with np.load(src/"integrality.npz") as data:
            old_integer = data["integrality"].copy()
        with np.load(src/"objective.npz") as data:
            objective = data["objective"].copy()
        assert np.all(objective == 0)
        meta = json.loads((src/"model_metadata.json").read_text())
        labels = pd.read_csv(src/"row_metadata.csv.gz")
        integer, audit = audit_projection(matrix, bounds, meta, labels, old_integer)
        assert meta["unit_names"] == model.dec["GEN UID"].tolist()
        assert meta["thermal_unit_names"] == model.dec.iloc[model.urows]["GEN UID"].tolist()
        directory = output/case; directory.mkdir()
        np.savez_compressed(directory/"integrality.npz", integrality=integer)
        save(directory/"projection_audit.json", audit)
        save(directory/"model_binding.json", {"source_directory": src.relative_to(ROOT).as_posix(),
            "matrix_sha256": digest(src/"matrix.npz"), "bounds_sha256": digest(src/"bounds.npz"),
            "objective_sha256": digest(src/"objective.npz"),
            "integrality_sha256": digest(directory/"integrality.npz"),
            "budget_MWh": meta["budget_MWh"], "individual_mean_constraints": 0})
        paths.extend(src/name for name in ("matrix.npz", "bounds.npz", "integrality.npz", "objective.npz",
                                          "native_inputs.npz", "model_metadata.json", "row_metadata.csv.gz"))
        paths.append(directory/"integrality.npz")
        prepared.append((case, directory, matrix, bounds, integer, meta, native))
    records = [{"path": str(p), "sha256": digest(p), "bytes": p.stat().st_size} for p in dict.fromkeys(paths)]
    pd.DataFrame(records).to_csv(output/"input_manifest.csv", index=False)
    save(output/"models_frozen_before_first_solve.json", {
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(), "cases": CASES,
        "input_manifest_sha256": digest(output/"input_manifest.csv"), "seconds_per_case": SECONDS,
        "threads": 1, "random_seed": 0, "presolve": "on", "mip_rel_gap": 1e-8,
        "warm_start": False, "objective": "zero", "old_results_preserved": True})
    results = []
    for case, directory, matrix, bounds, integer, meta, native in prepared:
        lp = highspy.HighsLp()
        lp.num_row_, lp.num_col_ = matrix.shape
        lp.col_cost_ = np.zeros(matrix.shape[1])
        lp.col_lower_, lp.col_upper_ = bounds["column_lower"], bounds["column_upper"]
        lp.row_lower_, lp.row_upper_ = bounds["row_lower"], bounds["row_upper"]
        lp.integrality_ = [highspy.HighsVarType.kInteger if flag else highspy.HighsVarType.kContinuous for flag in integer]
        lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
        lp.a_matrix_.num_row_, lp.a_matrix_.num_col_ = matrix.shape
        lp.a_matrix_.start_, lp.a_matrix_.index_, lp.a_matrix_.value_ = matrix.indptr, matrix.indices, matrix.data
        solver = highspy.Highs()
        for option, value in [("time_limit", float(SECONDS)), ("threads", 1), ("random_seed", 0),
                              ("presolve", "on"), ("mip_rel_gap", 1e-8), ("log_to_console", False),
                              ("log_file", str(directory/"solver.log"))]:
            assert solver.setOptionValue(option, value) == highspy.HighsStatus.kOk
        assert solver.passModel(lp) == highspy.HighsStatus.kOk
        started = time.perf_counter(); solver.run(); elapsed = time.perf_counter()-started
        status, solution, info = solver.getModelStatus(), solver.getSolution(), solver.getInfo()
        result = {"case": case, "model_status": solver.modelStatusToString(status),
                  "verdict": "UNKNOWN", "time_limit_s": SECONDS, "elapsed_s": elapsed,
                  "solver_version": solver.version(), "optimization_calls": 1,
                  "solution_value_valid": bool(solution.value_valid), "mip_node_count": int(info.mip_node_count)}
        if solution.value_valid:
            raw = np.asarray(solution.col_value)
            np.savez_compressed(directory/"raw_vector.npz", vector=raw)
            result["raw_matrix_check"] = check_vector(matrix, bounds, raw)
            p, u, y, z, theta = unpack(raw, meta["hours"], meta["units"], meta["thermal_units"], meta["buses"])
            eligible = bool(np.all(np.isfinite(raw)) and np.all(np.abs(u-np.rint(u)) <= TOL)
                            and np.all((np.rint(u) >= 0) & (np.rint(u) <= 1)))
            result["eligible_for_recovery"] = eligible
            if eligible:
                rounded = np.rint(u)
                yy, zz = np.zeros_like(rounded), np.zeros_like(rounded)
                yy[1:], zz[1:] = np.maximum(np.diff(rounded, axis=0), 0), np.maximum(-np.diff(rounded, axis=0), 0)
                recovered = np.concatenate([a.ravel() for a in (p, rounded, yy, zz, theta)])
                np.savez_compressed(directory/"recovered_vector.npz", vector=recovered)
                result["recovered_matrix_check"] = check_vector(matrix, bounds, recovered)
                physical = direct_check(model, p, rounded, yy, zz, theta, native["pmin"], native["pmax"],
                    native["net"], native["rows"], native["nodal"],
                    [meta["unit_names"].index(uid) for uid in meta["fossil_units"]], meta["budget_MWh"])
                save(directory/"physical_check.json", physical)
                result["physical_check_pass"] = physical["pass"]
                if result["raw_matrix_check"]["pass"] and result["recovered_matrix_check"]["pass"] and physical["pass"]:
                    result["verdict"] = "ADMITTED_BINARY_DC_NETWORK_SERVICE"
                    result["fossil_energy_MWh"] = physical["fossil_energy_MWh"]
                    for filename, values, columns in [("dispatch", p, meta["unit_names"]),
                        ("commitment", rounded, meta["thermal_unit_names"]), ("startup", yy, meta["thermal_unit_names"]),
                        ("shutdown", zz, meta["thermal_unit_names"]), ("angles", theta, meta["bus_ids"])]:
                        pd.DataFrame(values, columns=columns).to_csv(directory/f"{filename}.csv", index=False)
        if status == highspy.HighsModelStatus.kInfeasible:
            assert result["verdict"] != "ADMITTED_BINARY_DC_NETWORK_SERVICE"
            result["verdict"] = "NUMERICAL_MIP_INFEASIBLE_NOT_EXACT_CERTIFICATE"
        save(directory/"result.json", result); results.append(result)
        save(output/"summary.json", results)
        print(json.dumps({k: result[k] for k in ("case", "model_status", "verdict", "elapsed_s")}), flush=True)
    pd.DataFrame([{k: v for k, v in r.items() if not isinstance(v, (dict, list))}
                  for r in results]).to_csv(output/"summary.csv", index=False)
    changed = [r["path"] for r in records if digest(Path(r["path"])) != r["sha256"] or Path(r["path"]).stat().st_size != r["bytes"]]
    save(output/"final_input_hash_check.json", {"pass": not changed, "files_checked": len(records), "changed": changed})
    assert not changed


if __name__ == "__main__":
    main()
