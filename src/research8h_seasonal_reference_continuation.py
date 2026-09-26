"""Prepare, then separately continue three original uncapped reference timeouts."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import json
from pathlib import Path
import shutil
import time

import highspy
import numpy as np
import pandas as pd
from scipy.sparse import load_npz

from research8h_seasonal_reference import assemble_reference, physical_check
from research8h_seasonal_uncapped import check_manifest, exact_point_check, rational_record
from research8h_service_network_mip import unpack
from research8h_u_only_continuation import audit_projection
from temporal_lp_certificate import check_vector, digest, save
from v8r1_rts_seasonal import inputs, load_model

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "results/research8h/seasonal_reference"
OUTPUT = ROOT / "results/research8h/seasonal_reference_continuation"
PROTOCOL = ROOT / "docs/research8h/SEASONAL_REFERENCE_CONTINUATION_PROTOCOL.md"
MONTHS = [4, 7, 10]
SECONDS = 600
TOL = 1e-5
ORIGINAL_MANIFEST = "a4cd70b40e26a9c5019df545364adb06124ce4e46e67c713caf4667ae19c02af"


def arrays(path):
    with np.load(path) as data:
        return {key: data[key].copy() for key in data.files}


def prepare(source_v3):
    OUTPUT.mkdir(parents=True, exist_ok=False)
    old_freeze = json.loads((SOURCE / "all_models_frozen_before_first_solve.json").read_text())
    assert old_freeze["manifest_sha256"] == ORIGINAL_MANIFEST
    assert digest(SOURCE / "input_manifest.csv") == ORIGINAL_MANIFEST
    save(OUTPUT / "original_reference_manifest_check.json", check_manifest(SOURCE / "input_manifest.csv"))
    model = load_model(source_v3)
    names = model.dec["GEN UID"].tolist()
    thermal = model.dec.iloc[model.urows]
    thermal_names = thermal["GEN UID"].tolist()
    fossil = [int(j) for j in model.urows if model.dec.iloc[j]["Fuel"] in {"Coal", "Oil", "NG"}]
    assert (len(names), len(thermal_names), len(model.busids), len(model.branches)) == (41, 24, 24, 38)
    assert len(fossil) == 23 and [names[j] for j in model.urows if j not in fossil] == ["121_NUCLEAR_1"]
    rate = thermal["Ramp Rate MW/Min"].to_numpy(float) * 60
    variation = thermal["PMax MW"].to_numpy(float) - thermal["PMin MW"].to_numpy(float)
    assert np.all(rate >= variation)
    pd.DataFrame({"uid": thermal_names, "native_hourly_ramp_MW": rate,
                  "maximum_on_on_change_MW": variation, "redundancy_margin_MW": rate-variation}).to_csv(
                      OUTPUT / "ramp_redundancy.csv", index=False)
    inventory = model.dec[["GEN UID", "Category", "Fuel", "PMin MW", "PMax MW", "Min Up Time Hr",
                           "Min Down Time Hr", "Ramp Rate MW/Min"]].copy()
    inventory["thermal"] = model.thermal.to_numpy(bool)
    inventory["fossil_objective_coefficient"] = [int(j in fossil) for j in range(41)]
    inventory.to_csv(OUTPUT / "unit_inventory.csv", index=False)
    paths = [Path(__file__), PROTOCOL, SOURCE / "input_manifest.csv",
             SOURCE / "all_models_frozen_before_first_solve.json", SOURCE / "summary.json",
             ROOT / "docs/research8h/SEASONAL_REFERENCE_PROTOCOL.md",
             ROOT / "docs/research8h/U_ONLY_CONTINUATION_PROTOCOL.md",
             *[ROOT / "src" / name for name in ["research8h_seasonal_reference.py",
                 "research8h_seasonal_uncapped.py", "research8h_u_only_continuation.py",
                 "research8h_service_network_mip.py", "research8h_service_network.py",
                 "temporal_lp_certificate.py", "temporal_information_pilot.py", "v8r1_rts_seasonal.py"]],
             source_v3 / "code/dscgrid_model.py", *sorted((source_v3 / "raw").rglob("*.csv")),
             OUTPUT / "original_reference_manifest_check.json", OUTPUT / "unit_inventory.csv",
             OUTPUT / "ramp_redundancy.csv"]
    for month in MONTHS:
        src = SOURCE / f"month_{month:02d}"
        old_result = json.loads((src / "result.json").read_text())
        assert old_result["month"] == month and old_result["model_status"] == "Time limit reached"
        assert old_result["verdict"] == "UNKNOWN_NO_VERIFIED_REFERENCE" and not old_result["solution_value_valid"]
        assert not (src / "returned_vector.npz").exists()
        matrix = load_npz(src / "matrix.npz").tocsr()
        bounds, native = arrays(src / "bounds.npz"), arrays(src / "native_inputs.npz")
        old_integer, objective = arrays(src / "integrality.npz")["integrality"], arrays(src / "objective.npz")["objective"]
        meta = json.loads((src / "model_metadata.json").read_text())
        labels = pd.read_csv(src / "row_metadata.csv.gz")
        assert meta["unit_names"] == names and meta["thermal_unit_names"] == thermal_names
        assert meta["bus_ids"] == model.busids and meta["fossil_units"] == [names[j] for j in fossil]
        assert meta["energy_cap_constraints"] == meta["individual_mean_constraints"] == 0
        assert not labels.family.isin(["fossil_energy_cap", "target_mean"]).any()
        assert matrix.shape == (34680, 23016) and matrix.nnz == 141724
        expected_objective = np.zeros(matrix.shape[1])
        expected_objective[[t*41+j for t in range(168) for j in fossil]] = 1.
        assert np.array_equal(objective, expected_objective)
        assert np.count_nonzero(objective) == 3864 and np.all(objective[meta["offsets"]["U"]:] == 0)

        cols, unused, lo, hi, net, used = inputs(model, source_v3, month)
        assert cols == names
        hours = pd.read_csv(used[1])[["row", "timestamp"]]
        pd.testing.assert_frame_equal(hours, pd.read_csv(src / "source_hours.csv"), check_dtype=False)
        rows = hours["row"].to_numpy(int)
        rebuilt, rebuilt_bounds, rebuilt_integer, rebuilt_objective, rebuilt_meta, rebuilt_labels, nodal = assemble_reference(
            model, lo, hi, net, rows, fossil)
        assert rebuilt.shape == matrix.shape
        assert all(np.array_equal(getattr(matrix, key), getattr(rebuilt, key)) for key in ["indptr", "indices", "data"])
        assert bounds.keys() == rebuilt_bounds.keys()
        assert all(np.array_equal(bounds[key], rebuilt_bounds[key]) for key in bounds)
        assert np.array_equal(old_integer, rebuilt_integer) and np.array_equal(objective, rebuilt_objective)
        assert meta == rebuilt_meta
        pd.testing.assert_frame_equal(labels, pd.DataFrame(rebuilt_labels), check_dtype=False)
        expected_native = {"pmin": lo, "pmax": hi, "net": net, "rows": rows, "nodal": nodal}
        assert native.keys() == expected_native.keys()
        assert all(np.array_equal(native[key], expected_native[key]) for key in native)
        integer, projection = audit_projection(matrix, bounds, meta, labels, old_integer)
        directory = OUTPUT / f"month_{month:02d}"
        directory.mkdir()
        copied = ["matrix.npz", "bounds.npz", "objective.npz", "native_inputs.npz", "row_metadata.csv.gz", "source_hours.csv"]
        for filename in copied:
            shutil.copyfile(src / filename, directory / filename)
            assert digest(src / filename) == digest(directory / filename)
        shutil.copyfile(src / "integrality.npz", directory / "original_integrality.npz")
        shutil.copyfile(src / "model_metadata.json", directory / "original_model_metadata.json")
        shutil.copyfile(src / "result.json", directory / "original_result.json")
        np.savez_compressed(directory / "integrality.npz", integrality=integer)
        meta.update(binary_columns=int(integer.sum()), original_binary_columns=int(old_integer.sum()),
                    auxiliary_objective_coefficients_zero=True, continuation_month=month)
        save(directory / "model_metadata.json", meta)
        save(directory / "projection_audit.json", projection)
        save(directory / "source_reconstruction_audit.json", {"pass": True, "optimization_calls": 0,
            "month": month, "all_csr_entries_exact": True, "all_bounds_exact": True,
            "objective_and_original_integrality_exact": True, "metadata_and_labels_exact": True,
            "all_native_arrays_exact": True, "source_hour_mapping_exact": True,
            "roster": {"generators": 41, "thermal": 24, "fossil": 23, "buses": 24, "branches": 38},
            "shape": list(matrix.shape), "nonzeros": matrix.nnz})
        save(directory / "model_binding.json", {"source_directory": src.relative_to(ROOT).as_posix(),
            "original_result_sha256": digest(src / "result.json"),
            "byte_identical_artifacts": {filename: digest(directory / filename) for filename in copied},
            "original_integrality_sha256": digest(directory / "original_integrality.npz"),
            "projected_integrality_sha256": digest(directory / "integrality.npz"),
            "changed_rows_or_bounds": 0, "changed_objective_coefficients": 0,
            "individual_mean_constraints": 0, "energy_cap_constraints": 0})
        paths.extend(used)
        paths.extend(src / filename for filename in [*copied, "integrality.npz", "model_metadata.json", "result.json"])
        paths.extend(sorted(directory.glob("*")))
    pd.DataFrame([{"path": str(p), "sha256": digest(p), "bytes": p.stat().st_size}
                  for p in dict.fromkeys(paths)]).to_csv(OUTPUT / "input_manifest.csv", index=False)
    freeze = {"utc": datetime.now(timezone.utc).isoformat(), "source_sha256": digest(Path(__file__)),
        "protocol_sha256": digest(PROTOCOL), "input_manifest_sha256": digest(OUTPUT / "input_manifest.csv"),
        "months": MONTHS, "seconds_per_case": SECONDS, "total_configured_solver_seconds": 3*SECONDS,
        "threads": 1, "random_seed": 0, "presolve": "on", "mip_rel_gap": 1e-8, "warm_start": False,
        "optimization_calls_per_case": 1, "energy_caps": 0, "individual_mean_constraints": 0,
        "solver_execution_started": False, "requires_parent_go_before_run_prepared": True,
        "source_v3": str(source_v3.resolve()), "historical_unknowns_preserved": True}
    save(OUTPUT / "prepared_freeze.json", freeze)
    print(json.dumps({"event": "PREPARED_NO_SOLVES", **freeze}), flush=True)


def finite(value):
    value = float(value)
    return value if np.isfinite(value) else None


def run_prepared(source_v3):
    freeze = json.loads((OUTPUT / "prepared_freeze.json").read_text())
    assert freeze["source_v3"] == str(source_v3.resolve()) and freeze["months"] == MONTHS
    assert digest(Path(__file__)) == freeze["source_sha256"] and digest(PROTOCOL) == freeze["protocol_sha256"]
    assert digest(OUTPUT / "input_manifest.csv") == freeze["input_manifest_sha256"]
    before = check_manifest(OUTPUT / "input_manifest.csv")
    with (OUTPUT / "execution_started.json").open("x", encoding="utf-8") as stream:
        json.dump({"utc": datetime.now(timezone.utc).isoformat(), "pre_execution_hash_check": before,
                   "planned_calls": 3}, stream, indent=2)
    model = load_model(source_v3)
    results = []
    overall = time.perf_counter()
    for month in MONTHS:
        directory = OUTPUT / f"month_{month:02d}"
        matrix = load_npz(directory / "matrix.npz")
        bounds, native = arrays(directory / "bounds.npz"), arrays(directory / "native_inputs.npz")
        integer = arrays(directory / "integrality.npz")["integrality"]
        old_integer = arrays(directory / "original_integrality.npz")["integrality"]
        objective = arrays(directory / "objective.npz")["objective"]
        meta = json.loads((directory / "model_metadata.json").read_text())
        lp = highspy.HighsLp()
        lp.num_row_, lp.num_col_ = matrix.shape
        lp.col_cost_, lp.col_lower_, lp.col_upper_ = objective, bounds["column_lower"], bounds["column_upper"]
        lp.row_lower_, lp.row_upper_ = bounds["row_lower"], bounds["row_upper"]
        lp.integrality_ = [highspy.HighsVarType.kInteger if flag else highspy.HighsVarType.kContinuous for flag in integer]
        lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
        lp.a_matrix_.num_row_, lp.a_matrix_.num_col_ = matrix.shape
        lp.a_matrix_.start_, lp.a_matrix_.index_, lp.a_matrix_.value_ = matrix.indptr, matrix.indices, matrix.data
        solver = highspy.Highs()
        options = {"time_limit": float(SECONDS), "threads": 1, "random_seed": 0, "presolve": "on",
                   "mip_rel_gap": 1e-8, "log_to_console": False, "log_file": str(directory / "solver.log")}
        for key, value in options.items():
            assert solver.setOptionValue(key, value) == highspy.HighsStatus.kOk
        assert solver.passModel(lp) == highspy.HighsStatus.kOk
        started = time.perf_counter()
        run_status = solver.run()
        elapsed = time.perf_counter() - started
        status, solution, info = solver.getModelStatus(), solver.getSolution(), solver.getInfo()
        result = {"month": month, "model_status": solver.modelStatusToString(status), "run_status": str(run_status),
            "verdict": "UNKNOWN_NO_VERIFIED_REFERENCE", "time_limit_s": SECONDS, "elapsed_s": elapsed,
            "optimization_calls": 1, "solver_version": solver.version(), "solver_options": options,
            "solution_value_valid": bool(solution.value_valid), "solver_objective_MWh": finite(info.objective_function_value),
            "solver_reported_numerical_lower_bound_MWh": finite(info.mip_dual_bound), "mip_relative_gap": finite(info.mip_gap),
            "mip_node_count": int(info.mip_node_count), "exact_optimality_claim": False, "historical_result_unchanged": True}
        if solution.value_valid:
            raw = np.asarray(solution.col_value)
            np.savez_compressed(directory / "raw_vector.npz", vector=raw)
            result["raw_matrix_check"] = check_vector(matrix, bounds, raw)
            p, u, y, z, theta = unpack(raw, 168, 41, 24, 24)
            eligible = bool(np.isfinite(raw).all() and np.all(np.abs(u-np.rint(u)) <= TOL)
                            and np.all((np.rint(u) >= 0) & (np.rint(u) <= 1)))
            result["eligible_for_recovery"] = eligible
            if eligible:
                rounded = np.rint(u)
                yy, zz = np.zeros_like(rounded), np.zeros_like(rounded)
                yy[1:], zz[1:] = np.maximum(np.diff(rounded, axis=0), 0), np.maximum(-np.diff(rounded, axis=0), 0)
                recovered = np.concatenate([a.ravel() for a in (p, rounded, yy, zz, theta)])
                np.savez_compressed(directory / "recovered_vector.npz", vector=recovered)
                result["recovered_matrix_check"] = check_vector(matrix, bounds, recovered)
                fossil = [meta["unit_names"].index(uid) for uid in meta["fossil_units"]]
                native_check = physical_check(model, p, rounded, yy, zz, theta, native["pmin"], native["pmax"],
                                              native["net"], native["rows"], native["nodal"], fossil)
                save(directory / "native_no_cap_check.json", native_check)
                result["native_no_cap_pass"] = native_check["pass"]
                exact = exact_point_check(matrix, bounds, recovered, old_integer)
                save(directory / "exact_point_check.json", exact)
                energy = sum((Fraction.from_float(float(v)) for v in p[:, fossil].ravel()), Fraction(0))
                result["recovered_fossil_energy"] = rational_record(energy)
                result["exact_strict_model_pass"], result["exact_expanded_model_pass"] = exact["strict_pass"], exact["expanded_pass"]
                result["objective_recovery_difference_MWh"] = abs(float(objective @ recovered) - float(energy))
                objective_ok = result["objective_recovery_difference_MWh"] <= 1e-6
                numerical = result["raw_matrix_check"]["pass"] and result["recovered_matrix_check"]["pass"] and native_check["pass"] and objective_ok
                if numerical and exact["expanded_pass"]:
                    result["verdict"] = "VERIFIED_REFERENCE_BINARY_WITNESS_EXPANDED_MODEL"
                    result["rigorous_energy_upper_bound_scope"] = "strict_and_expanded_binary64_models" if exact["strict_pass"] else "uniformly_1e-5_expanded_binary64_model_only"
                    for filename, values, columns in [("dispatch", p, meta["unit_names"]), ("commitment", rounded, meta["thermal_unit_names"]),
                            ("startup", yy, meta["thermal_unit_names"]), ("shutdown", zz, meta["thermal_unit_names"]), ("angles", theta, meta["bus_ids"])]:
                        pd.DataFrame(values, columns=columns).to_csv(directory / f"{filename}.csv", index=False)
                elif numerical:
                    result["verdict"] = "NUMERICAL_TOLERANCE_ONLY_CANDIDATE"
        if status == highspy.HighsModelStatus.kInfeasible:
            result["numerical_solver_infeasibility_status"] = True
            if result["verdict"] == "UNKNOWN_NO_VERIFIED_REFERENCE":
                result["verdict"] = "NUMERICAL_MIP_INFEASIBLE_NOT_EXACT_CERTIFICATE"
        save(directory / "result.json", result)
        results.append(result)
        save(OUTPUT / "summary.json", results)
        print(json.dumps({k: result[k] for k in ["month", "model_status", "verdict", "elapsed_s"]}), flush=True)
    save(OUTPUT / "final_input_hash_check.json", check_manifest(OUTPUT / "input_manifest.csv"))
    save(OUTPUT / "completion.json", {"calls": len(results), "configured_solver_seconds": 3*SECONDS,
        "actual_solver_seconds": sum(r["elapsed_s"] for r in results), "execution_and_checks_seconds": time.perf_counter()-overall})
    pd.DataFrame([{k: v for k, v in r.items() if not isinstance(v, (dict, list))} for r in results]).to_csv(OUTPUT / "summary.csv", index=False)


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
