"""Post-pilot continuous dwell relaxation and exact binary64 Farkas checking.

See docs/TEMPORAL_LP_CERTIFICATE.md for the protocol frozen before the runs.
The --verify-archived mode performs no optimization and does not import HiGHS.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix, load_npz, save_npz

ROOT = Path(__file__).resolve().parents[1]
CASES = ["identity", *(f"seed_{seed}" for seed in range(26092600, 26092604))]
TOL = 1e-5


def save(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assemble(source, pmin, pmax, demand, means):
    """Build constraints directly without using any existing optimization code."""
    hours, units = pmax.shape
    thermal = np.flatnonzero(source.thermal.to_numpy(bool))
    nthermal = len(thermal)
    npower, nstate = hours * units, hours * nthermal
    offsets = {"P": 0, "U": npower, "Y": npower + nstate, "Z": npower + 2 * nstate}
    ncols = npower + 3 * nstate
    lower = np.zeros(ncols)
    upper = np.concatenate([pmax.ravel(), np.ones(3 * nstate)])
    hydro = np.flatnonzero(source.dec.Category.eq("Hydro").to_numpy())
    for unit in hydro:
        lower[np.arange(hours) * units + unit] = pmin[:, unit]
    upper[offsets["Y"]:offsets["Y"] + nthermal] = 0
    upper[offsets["Z"]:offsets["Z"] + nthermal] = 0
    up = np.ceil(source.dec.iloc[thermal]["Min Up Time Hr"].to_numpy(float)).astype(int)
    down = np.ceil(source.dec.iloc[thermal]["Min Down Time Hr"].to_numpy(float)).astype(int)
    names = source.dec["GEN UID"].tolist()
    row_ids, column_ids, entries, row_lower, row_upper, labels = [], [], [], [], [], []

    def col(kind, hour, unit):
        width = units if kind == "P" else nthermal
        return offsets[kind] + hour * width + unit

    def row(family, hour, uid, terms, lo=-np.inf, hi=np.inf):
        index = len(row_lower)
        for column, value in terms:
            if value:
                row_ids.append(index)
                column_ids.append(column)
                entries.append(value)
        row_lower.append(lo)
        row_upper.append(hi)
        labels.append({"row": index, "family": family, "hour_0based": hour, "uid": uid})

    for hour in range(hours):
        row("aggregate_balance", hour, "ALL", [(col("P", hour, j), 1.0) for j in range(units)],
            demand[hour], demand[hour])
    for q, unit in enumerate(thermal):
        uid = names[unit]
        for hour in range(hours):
            p, u = col("P", hour, unit), col("U", hour, q)
            row("thermal_upper", hour, uid, [(p, 1.0), (u, -pmax[hour, unit])], hi=0)
            row("thermal_lower", hour, uid, [(u, pmin[hour, unit]), (p, -1.0)], hi=0)
            if hour == 0:
                continue
            y, z = col("Y", hour, q), col("Z", hour, q)
            row("transition", hour, uid, [(u, 1.0), (col("U", hour - 1, q), -1.0),
                                         (y, -1.0), (z, 1.0)], lo=0, hi=0)
            row("exclusive_transition", hour, uid, [(y, 1.0), (z, 1.0)], hi=1)
            row("minimum_up", hour, uid,
                [(col("Y", t, q), 1.0) for t in range(max(1, hour - int(up[q]) + 1), hour + 1)] + [(u, -1.0)], hi=0)
            row("minimum_down", hour, uid,
                [(col("Z", t, q), 1.0) for t in range(max(1, hour - int(down[q]) + 1), hour + 1)] + [(u, 1.0)], hi=1)
    for unit in range(units):
        row("target_mean", -1, names[unit], [(col("P", hour, unit), 1.0 / hours) for hour in range(hours)],
            means[unit], means[unit])
    matrix = coo_matrix((entries, (row_ids, column_ids)), shape=(len(row_lower), ncols)).tocsr()
    bounds = {"column_lower": lower, "column_upper": upper,
              "row_lower": np.asarray(row_lower), "row_upper": np.asarray(row_upper)}
    metadata = {"hours": hours, "units": units, "thermal_units": nthermal,
                "offsets": offsets, "rows": matrix.shape[0], "columns": matrix.shape[1],
                "nonzeros": matrix.nnz, "unit_names": names,
                "thermal_unit_names": [names[j] for j in thermal],
                "column_order": "P,U,Y,Z; each block hour-major then unit-major"}
    return matrix, bounds, metadata, labels


def check_vector(matrix, bounds, vector):
    if len(vector) != matrix.shape[1] or not np.all(np.isfinite(vector)):
        return {"pass": False, "reason": "wrong vector shape or nonfinite coordinate"}
    value = matrix @ vector
    residuals = {"column_lower": max(0.0, float(np.max(bounds["column_lower"] - vector))),
                 "column_upper": max(0.0, float(np.max(vector - bounds["column_upper"]))),
                 "row_lower": max(0.0, float(np.max(bounds["row_lower"] - value))),
                 "row_upper": max(0.0, float(np.max(value - bounds["row_upper"])))}
    return {"pass": max(residuals.values()) <= TOL, "tolerance": TOL, "residuals": residuals}


def fraction(value):
    return Fraction.from_float(float(value))


def certificate_context(directory, labels, multipliers):
    active = np.flatnonzero(multipliers)
    families = {}
    hours, units = set(), set()
    for index in active:
        label = labels[index]
        families[label["family"]] = families.get(label["family"], 0) + 1
        if int(label["hour_0based"]) >= 0:
            hours.add(int(label["hour_0based"]))
        if label["uid"] != "ALL":
            units.add(label["uid"])
    return {"model_artifacts": {name: digest(directory / name) for name in ("matrix.npz", "bounds.npz")},
            "raw_solver_ray_sha256": digest(directory / "raw_solver_ray.npz"),
            "support": {"row_family_counts": dict(sorted(families.items())),
                        "unique_hours_in_nonzero_rows": len(hours),
                        "hours_in_nonzero_rows_0based": sorted(hours),
                        "individual_units_in_nonzero_rows": len(units),
                        "interpretation": "Target-mean rows can involve all hours; this support is not a claim of minimum memory or input compression."}}


def exact_ray_check(matrix, bounds, multipliers, tolerance=TOL):
    """Check lower(y A x) > maximum_box(y A x) with exact rational arithmetic."""
    started = time.perf_counter()
    if multipliers.shape != (matrix.shape[0],) or not np.all(np.isfinite(multipliers)):
        return {"pass": False, "reason": "invalid multiplier vector"}
    if not np.all(np.isfinite(bounds["column_lower"])) or not np.all(np.isfinite(bounds["column_upper"])):
        return {"pass": False, "reason": "this checker requires finite column bounds"}
    combined = {}
    lower_sum, row_norm = Fraction(0), Fraction(0)
    active = np.flatnonzero(multipliers)
    for row_index in active:
        multiplier = fraction(multipliers[row_index])
        bound = bounds["row_lower" if multiplier > 0 else "row_upper"][row_index]
        if not np.isfinite(bound):
            return {"pass": False, "reason": "nonzero multiplier selects an infinite row bound", "row": int(row_index)}
        lower_sum += multiplier * fraction(bound)
        row_norm += abs(multiplier)
        for entry in range(matrix.indptr[row_index], matrix.indptr[row_index + 1]):
            column = int(matrix.indices[entry])
            combined[column] = combined.get(column, Fraction(0)) + multiplier * fraction(matrix.data[entry])
    box_max, column_norm = Fraction(0), Fraction(0)
    combined = {column: coefficient for column, coefficient in combined.items() if coefficient}
    for column, coefficient in combined.items():
        bound = bounds["column_upper" if coefficient > 0 else "column_lower"][column]
        box_max += coefficient * fraction(bound)
        column_norm += abs(coefficient)
    gap = lower_sum - box_max
    robust_gap = gap - fraction(tolerance) * (row_norm + column_norm)
    result = {"pass": gap > 0, "robust_pass": robust_gap > 0,
              "arithmetic": "exact rational interpretation of archived binary64 matrix, bounds and ray",
              "row_multiplier_nonzeros": len(active), "combined_column_nonzeros": len(combined),
              "lower_row_sum": float(lower_sum), "box_maximum": float(box_max),
              "separation_gap": float(gap), "outward_bound_relaxation": tolerance,
              "robust_separation_gap": float(robust_gap),
              "maximum_uniform_bound_relaxation": float(gap / (row_norm + column_norm)) if row_norm + column_norm else None,
              "exact_gap_numerator": str(gap.numerator), "exact_gap_denominator": str(gap.denominator),
              "exact_robust_gap_numerator": str(robust_gap.numerator),
              "exact_robust_gap_denominator": str(robust_gap.denominator),
              "elapsed_s": time.perf_counter() - started,
              "scope": "mathematical model with archived float coefficients; not exact physical measurements"}
    return result


def solve_case(matrix, bounds, output, labels, seconds, power_columns):
    import highspy
    lp = highspy.HighsLp()
    lp.num_row_, lp.num_col_ = matrix.shape
    lp.col_cost_ = np.zeros(matrix.shape[1])
    lp.col_lower_, lp.col_upper_ = bounds["column_lower"], bounds["column_upper"]
    lp.row_lower_, lp.row_upper_ = bounds["row_lower"], bounds["row_upper"]
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.num_row_, lp.a_matrix_.num_col_ = matrix.shape
    lp.a_matrix_.start_, lp.a_matrix_.index_, lp.a_matrix_.value_ = matrix.indptr, matrix.indices, matrix.data
    solver = highspy.Highs()
    # Presolve off allows the simplex run itself to return a ray without a
    # second optimization call beyond the per-case budget.
    for option, value in [("time_limit", float(seconds)), ("threads", 1), ("random_seed", 0),
                          ("solver", "simplex"), ("presolve", "off"), ("log_to_console", False),
                          ("log_file", str(output / "solver.log"))]:
        solver.setOptionValue(option, value)
    solver.passModel(lp)
    started = time.perf_counter()
    solver.run()
    status = solver.getModelStatus()
    result = {"model_status": solver.modelStatusToString(status), "solver_version": solver.version(),
              "elapsed_s": time.perf_counter() - started, "time_limit_s": seconds,
              "verdict": "UNRESOLVED", "presolve": "off", "solver": "simplex"}
    if status == highspy.HighsModelStatus.kInfeasible:
        ray_status, exists, ray = solver.getDualRay()
        result["dual_ray_status"] = str(ray_status)
        result["dual_ray_exists"] = bool(exists)
        if exists:
            ray = np.asarray(ray, dtype=float)
            np.savez_compressed(output / "raw_solver_ray.npz", multipliers=ray)
            candidates, checks = [], []
            for orientation in (1, -1):
                raw = orientation * ray
                inadmissible = ((raw > 0) & ~np.isfinite(bounds["row_lower"])) | ((raw < 0) & ~np.isfinite(bounds["row_upper"]))
                # This is an explicit new candidate vector, not an assertion
                # that the discarded entries are mathematically zero. The
                # exact test below recomputes the entire separation after it.
                projected = raw.copy()
                projected[inadmissible] = 0.0
                for kind, candidate in (("raw", raw), ("projected_to_row_sign_cone", projected)):
                    candidates.append((orientation, kind, candidate))
                    check = exact_ray_check(matrix, bounds, candidate)
                    check["candidate"] = kind
                    check["orientation"] = orientation
                    check["inadmissible_raw_entries"] = int(np.count_nonzero(inadmissible))
                    check["largest_inadmissible_raw_magnitude"] = float(np.max(np.abs(raw[inadmissible]))) if np.any(inadmissible) else 0.0
                    checks.append(check)
            result["candidate_checks"] = checks
            valid = [i for i, check in enumerate(checks) if check["pass"]]
            if valid:
                selection = next((i for i in valid if checks[i]["robust_pass"]), valid[0])
                orientation, kind, chosen = candidates[selection]
                check = checks[selection]
                certificate = {"orientation": orientation, "candidate": kind,
                               "multipliers": [{"row": int(i), "value_hex": float(chosen[i]).hex()}
                                               for i in np.flatnonzero(chosen)],
                               "verification": check,
                               **certificate_context(output, labels, chosen)}
                save(output / "dual_certificate.json", certificate)
                pd.DataFrame([{**labels[i], "multiplier": chosen[i]} for i in np.flatnonzero(chosen)]).to_csv(
                    output / "sparse_multipliers.csv", index=False)
                result["verdict"] = "REJECTED_EXACT_BINARY64_CERTIFICATE" if check["robust_pass"] else "EXACT_SEPARATION_NUMERICALLY_FRAGILE"
                result["certificate_verification"] = check
                result["selected_orientation"] = certificate["orientation"]
                result["certificate_support"] = certificate["support"]
            else:
                result["verdict"] = "SOLVER_INFEASIBLE_NO_VERIFIED_RAY"
        else:
            result["verdict"] = "SOLVER_INFEASIBLE_NO_RAY"
    else:
        solution = solver.getSolution()
        if solution.value_valid:
            vector = np.asarray(solution.col_value, dtype=float)
            check = check_vector(matrix, bounds, vector)
            result["continuous_witness_verification"] = check
            if check["pass"]:
                np.savez_compressed(output / "continuous_solution.npz", vector=vector)
                result["verdict"] = "ADMITTED_CONTINUOUS_RELAXATION"
                result["fractional_state_coordinate_count"] = int(np.count_nonzero(np.abs(vector[power_columns:] - np.rint(vector[power_columns:])) > TOL))
    return result


def verify_archived(output):
    results = []
    for case in CASES:
        directory = output / case
        recorded = json.loads((directory / "result.json").read_text(encoding="utf-8"))
        for name, key in (("matrix.npz", "matrix_sha256"), ("bounds.npz", "bounds_sha256")):
            if digest(directory / name) != recorded[key]:
                raise AssertionError((case, "model artifact hash mismatch", name))
        matrix = load_npz(directory / "matrix.npz")
        with np.load(directory / "bounds.npz") as data:
            bounds = {name: data[name] for name in data.files}
        if (directory / "dual_certificate.json").exists():
            certificate = json.loads((directory / "dual_certificate.json").read_text(encoding="utf-8"))
            for name in ("matrix.npz", "bounds.npz"):
                if digest(directory / name) != certificate["model_artifacts"][name]:
                    raise AssertionError((case, "certificate/model hash mismatch", name))
            multipliers = np.zeros(matrix.shape[0])
            for entry in certificate["multipliers"]:
                multipliers[entry["row"]] = float.fromhex(entry["value_hex"])
            check = exact_ray_check(matrix, bounds, multipliers)
            if not check["pass"] or not check["robust_pass"]:
                raise AssertionError((case, check))
        elif (directory / "continuous_solution.npz").exists():
            with np.load(directory / "continuous_solution.npz") as data:
                check = check_vector(matrix, bounds, data["vector"])
            if not check["pass"]:
                raise AssertionError((case, check))
        else:
            check = {"pass": False, "reason": "no archived solution or certificate"}
        results.append({"case": case, "check": check})
    save(output / "independent_archive_replay.json", results)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-v3", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "results/temporal_information/lp_certificate")
    parser.add_argument("--seconds", type=float, default=60)
    parser.add_argument("--verify-archived", action="store_true")
    args = parser.parse_args()
    if args.verify_archived:
        print(json.dumps(verify_archived(args.output), indent=2), flush=True)
        return
    if args.source_v3 is None:
        parser.error("--source-v3 is required unless --verify-archived is used")
    from v8r1_rts_seasonal import inputs, load_model
    args.output.mkdir(parents=True, exist_ok=True)
    protocol = ROOT / "docs/TEMPORAL_LP_CERTIFICATE.md"
    save(args.output / "frozen_protocol.json", {"protocol_sha256": digest(protocol), "cases": CASES,
                                               "seconds_per_case": args.seconds, "selection": "post-pilot development"})
    source = load_model(args.source_v3)
    columns, _, pmin, pmax, demand, paths = inputs(source, args.source_v3, 7)
    witness_root = ROOT / "results/v8/network_repair"
    p_path, u_path = witness_root / "network_repair_dispatch.csv", witness_root / "network_fixed_commitment.csv"
    p = pd.read_csv(p_path)[columns].to_numpy(float)
    u = pd.read_csv(u_path)[source.dec.iloc[source.urows]["GEN UID"].tolist()].to_numpy(float)
    y, z = np.zeros_like(u), np.zeros_like(u)
    y[1:] = np.maximum(np.diff(u, axis=0), 0)
    z[1:] = np.maximum(-np.diff(u, axis=0), 0)
    identity = np.concatenate([a.ravel() for a in (p, u, y, z)])
    means = p.mean(axis=0)
    matrix, bounds, _, _ = assemble(source, pmin, pmax, demand, means)
    baseline = check_vector(matrix, bounds, identity)
    save(args.output / "baseline_matrix_verification.json", baseline)
    if not baseline["pass"]:
        raise AssertionError(baseline)
    records = []
    input_paths = [Path(__file__), protocol, p_path, u_path, *paths, args.source_v3 / "code/dscgrid_model.py",
                   *sorted((args.source_v3 / "raw").rglob("*.csv"))]
    for case in CASES:
        directory = args.output / case
        directory.mkdir(exist_ok=True)
        order_path = ROOT / "results/temporal_information/twins" / case / "permutation.csv"
        input_paths.append(order_path)
        order = pd.read_csv(order_path)["source_hour_0based"].to_numpy(int)
        if not np.array_equal(np.sort(order), np.arange(len(p))):
            raise AssertionError("Invalid archived permutation")
        matrix, bounds, metadata, labels = assemble(source, pmin[order], pmax[order], demand[order], means)
        save_npz(directory / "matrix.npz", matrix, compressed=True)
        np.savez_compressed(directory / "bounds.npz", **bounds)
        save(directory / "model_metadata.json", metadata)
        pd.DataFrame(labels).to_csv(directory / "row_metadata.csv.gz", index=False, compression="gzip")
        result = solve_case(matrix, bounds, directory, labels, args.seconds, p.size)
        result["case"] = case
        result["matrix_sha256"] = digest(directory / "matrix.npz")
        result["bounds_sha256"] = digest(directory / "bounds.npz")
        save(directory / "result.json", result)
        records.append(result)
        save(args.output / "summary.json", records)
        print(json.dumps({"case": case, "status": result["model_status"], "verdict": result["verdict"],
                          "elapsed_s": result["elapsed_s"]}), flush=True)
    pd.DataFrame([{key: value for key, value in record.items() if not isinstance(value, (list, dict))}
                  for record in records]).to_csv(args.output / "summary.csv", index=False)
    pd.DataFrame([{"path": str(path), "sha256": digest(path), "bytes": path.stat().st_size}
                  for path in dict.fromkeys(input_paths)]).to_csv(args.output / "input_manifest.csv", index=False)
    verify_archived(args.output)


if __name__ == "__main__":
    main()
