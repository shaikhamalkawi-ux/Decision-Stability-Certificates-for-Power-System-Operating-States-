"""Finite chronological-group deletion with exact Farkas rechecking.

All writes are contained in results/research8h/sparse_farkas. The source models
and earlier results are read-only. --verify-archived imports no optimizer.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import pandas as pd
from scipy.sparse import load_npz

from temporal_lp_certificate import exact_ray_check, check_vector

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "results/temporal_information/lp_certificate"
CASES = [f"seed_{seed}" for seed in range(26092600, 26092604)]
CHRON = {"transition", "exclusive_transition", "minimum_up", "minimum_down"}
THRESHOLDS = [0.0, 1e-14, 1e-12, 1e-10, 1e-8, 1e-6, 1e-4, 1e-3, 1e-2]


def save(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_case(case):
    directory = BASE / case
    certificate = json.loads((directory / "dual_certificate.json").read_text(encoding="utf-8"))
    for name, expected in certificate["model_artifacts"].items():
        if sha(directory / name) != expected:
            raise AssertionError((case, "input hash mismatch", name))
    matrix = load_npz(directory / "matrix.npz")
    with np.load(directory / "bounds.npz") as archive:
        bounds = {key: archive[key] for key in archive.files}
    metadata = json.loads((directory / "model_metadata.json").read_text(encoding="utf-8"))
    labels = pd.read_csv(directory / "row_metadata.csv.gz")
    multipliers = np.zeros(matrix.shape[0])
    for item in certificate["multipliers"]:
        multipliers[item["row"]] = float.fromhex(item["value_hex"])
    chrono_mask = labels.family.isin(CHRON).to_numpy(bool)
    return matrix, bounds, metadata, labels, multipliers, chrono_mask


def column_hour(column, metadata):
    offsets = metadata["offsets"]
    if column < offsets["U"]:
        return column // metadata["units"]
    for kind in ("Z", "Y", "U"):
        if column >= offsets[kind]:
            return (column - offsets[kind]) // metadata["thermal_units"]
    raise AssertionError(column)


def support(matrix, labels, metadata, multipliers, chrono_mask):
    active = np.flatnonzero(multipliers)
    chrono = active[chrono_mask[active]]
    chronological_columns = set()
    for row in chrono:
        chronological_columns.update(int(c) for c in matrix.indices[matrix.indptr[row]:matrix.indptr[row + 1]])
    hour_refs = sorted({column_hour(column, metadata) for column in chronological_columns})
    chosen_labels = labels.iloc[active]
    chron_labels = labels.iloc[chrono]
    return {"total_rows": len(active), "chronological_rows": len(chrono),
            "chronological_row_anchor_hours": sorted(set(int(x) for x in chron_labels.hour_0based)),
            "chronological_variable_reference_hours": hour_refs,
            "chronological_variable_reference_hour_count": len(hour_refs),
            "chronological_unit_count": int(chron_labels.uid.nunique()),
            "chronological_units": sorted(set(chron_labels.uid)),
            "row_family_counts": dict(Counter(chosen_labels.family)),
            "target_mean_rows_in_proof": int((chosen_labels.family == "target_mean").sum()),
            "all_target_mean_rows_retained_in_search": int((labels.family == "target_mean").sum()),
            "all_static_rows_retained_in_search": int(np.count_nonzero(~chrono_mask)),
            "all_variable_bounds_retained_in_search": 2 * matrix.shape[1],
            "global_energy_dependency_hours": metadata["hours"],
            "interpretation": "Proof support only; every full-week target mean and variable bound remains available. Chronological row anchors alone undercount their preceding-hour dependencies."}


def score(value):
    return (value["chronological_variable_reference_hour_count"], value["chronological_rows"], value["total_rows"])


def candidates(matrix, bounds, metadata, labels, chrono_mask, ray, thresholds, orientations=(1,)):
    records, best = [], None
    for orientation in orientations:
        candidate = orientation * ray
        wrong = ((candidate > 0) & ~np.isfinite(bounds["row_lower"])) | ((candidate < 0) & ~np.isfinite(bounds["row_upper"]))
        candidate[wrong] = 0
        largest = float(np.max(np.abs(candidate)))
        for threshold in thresholds:
            pruned = candidate.copy()
            if threshold:
                pruned[np.abs(pruned) < threshold * largest] = 0.0
            check = exact_ray_check(matrix, bounds, pruned)
            details = support(matrix, labels, metadata, pruned, chrono_mask)
            record = {"orientation": orientation, "relative_threshold": threshold,
                      "explicit_sign_projected_entries": int(np.count_nonzero(wrong)),
                      "pruned_entries": int(np.count_nonzero(candidate) - np.count_nonzero(pruned)),
                      "check": check, "support": details}
            records.append(record)
            if check.get("pass") and check.get("robust_pass"):
                if best is None or score(details) < score(best[2]):
                    best = (pruned, check, details, record)
    return best, records


def solve_relaxation(matrix, bounds, retained, seconds):
    import highspy
    reduced = matrix[retained].tocsr()
    lp = highspy.HighsLp()
    lp.num_row_, lp.num_col_ = reduced.shape
    lp.col_cost_ = np.zeros(reduced.shape[1])
    lp.col_lower_, lp.col_upper_ = bounds["column_lower"], bounds["column_upper"]
    lp.row_lower_, lp.row_upper_ = bounds["row_lower"][retained], bounds["row_upper"][retained]
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.num_row_, lp.a_matrix_.num_col_ = reduced.shape
    lp.a_matrix_.start_, lp.a_matrix_.index_, lp.a_matrix_.value_ = reduced.indptr, reduced.indices, reduced.data
    solver = highspy.Highs()
    for key, value in [("time_limit", float(seconds)), ("threads", 1), ("random_seed", 0),
                       ("solver", "simplex"), ("presolve", "off"), ("log_to_console", False)]:
        solver.setOptionValue(key, value)
    solver.passModel(lp)
    started = time.monotonic()
    solver.run()
    status = solver.getModelStatus()
    result = {"status": solver.modelStatusToString(status), "elapsed_s": time.monotonic() - started,
              "time_limit_s": seconds, "solver_version": solver.version(),
              "retained_rows": len(retained), "rejected_with_exact_certificate": False}
    ray, vector = None, None
    if status == highspy.HighsModelStatus.kInfeasible:
        ray_status, exists, value = solver.getDualRay()
        result["ray_status"], result["ray_exists"] = str(ray_status), bool(exists)
        if exists:
            ray = np.zeros(matrix.shape[0])
            ray[retained] = np.asarray(value, dtype=float)
    else:
        solution = solver.getSolution()
        if solution.value_valid:
            vector = np.asarray(solution.col_value)
            sub_bounds = {**bounds, "row_lower": bounds["row_lower"][retained], "row_upper": bounds["row_upper"][retained]}
            result["continuous_vector_check"] = check_vector(reduced, sub_bounds, vector)
    return result, ray, vector


def proof_json(case, multipliers, check, details, retained_chron, method):
    return {"case": case, "method": method,
            "model_artifacts": {name: sha(BASE / case / name) for name in ("matrix.npz", "bounds.npz")},
            "multipliers": [{"row": int(row), "value_hex": float(multipliers[row]).hex()} for row in np.flatnonzero(multipliers)],
            "retained_chronological_rows": sorted(retained_chron),
            "check": check, "support": details,
            "scope": "Exact archived binary64 model; all 41 target means, every static row and all variable bounds remain retained."}


def bound_support(matrix, bounds, multipliers, metadata):
    combined = {}
    for row in np.flatnonzero(multipliers):
        weight = Fraction.from_float(float(multipliers[row]))
        for entry in range(matrix.indptr[row], matrix.indptr[row + 1]):
            column = int(matrix.indices[entry])
            combined[column] = combined.get(column, Fraction(0)) + weight * Fraction.from_float(float(matrix.data[entry]))
    result = []
    for column, weight in sorted(combined.items()):
        if not weight:
            continue
        side = "upper" if weight > 0 else "lower"
        result.append({"column": column, "hour_0based": column_hour(column, metadata),
                       "side": side, "bound_hex": float(bounds[f"column_{side}"][column]).hex(),
                       "exact_weight_numerator": str(weight.numerator), "exact_weight_denominator": str(weight.denominator)})
    return result


def run_case(case, output, global_deadline, case_seconds, max_attempts, solve_seconds):
    started = time.monotonic()
    deadline = min(global_deadline, started + case_seconds)
    directory = output / case
    directory.mkdir(parents=True, exist_ok=True)
    matrix, bounds, metadata, labels, original, chrono_mask = load_case(case)
    initial_check = exact_ray_check(matrix, bounds, original)
    assert initial_check["pass"] and initial_check["robust_pass"]
    original_support = support(matrix, labels, metadata, original, chrono_mask)
    best, pruning = candidates(matrix, bounds, metadata, labels, chrono_mask, original, THRESHOLDS)
    assert best is not None
    save(directory / "initial_pruning_attempts.json", pruning)
    ray, check, details, _ = best
    active = set(int(row) for row in np.flatnonzero(ray) if chrono_mask[row])
    static = np.flatnonzero(~chrono_mask)
    history = []
    unit_order = sorted(set(labels.loc[list(active), "uid"]))
    groups = [("unit", uid, labels.uid.eq(uid).to_numpy()) for uid in unit_order]
    for width in (24, 8, 1):
        for begin in range(0, metadata["hours"], width):
            groups.append((f"hour_block_{width}", begin,
                           ((labels.hour_0based >= begin) & (labels.hour_0based < begin + width)).to_numpy()))
    termination = "EXHAUSTED_FIXED_GROUP_ORDER"
    for family, value, mask in groups:
        proposed_removal = sorted(row for row in active if mask[row])
        if not proposed_removal:
            continue
        remaining = deadline - time.monotonic()
        if len(history) >= max_attempts or remaining < 1:
            termination = "ATTEMPT_CAP" if len(history) >= max_attempts else "WALL_BUDGET"
            break
        trial_id = len(history)
        trial = directory / f"attempt_{trial_id:03d}"
        trial.mkdir(exist_ok=True)
        kept_chron = active - set(proposed_removal)
        retained = np.sort(np.r_[static, np.asarray(sorted(kept_chron), dtype=int)])
        result, proposed_ray, vector = solve_relaxation(matrix, bounds, retained, min(solve_seconds, remaining))
        result.update({"attempt": trial_id, "group_family": family, "group_value": value,
                       "removed_chronological_rows": proposed_removal,
                       "retained_chronological_rows": sorted(kept_chron)})
        if proposed_ray is not None:
            np.savez_compressed(trial / "raw_ray.npz", multipliers=proposed_ray)
            candidate, attempts = candidates(matrix, bounds, metadata, labels, chrono_mask, proposed_ray,
                                             (0.0, 1e-10), orientations=(1, -1))
            save(trial / "candidate_checks.json", attempts)
            if candidate is not None:
                new_ray, new_check, new_support, selected = candidate
                new_active = set(int(row) for row in np.flatnonzero(new_ray) if chrono_mask[row])
                assert new_active <= kept_chron
                assert len(new_active) < len(active)
                ray, check, details, active = new_ray, new_check, new_support, new_active
                result["rejected_with_exact_certificate"] = True
                result["accepted_support"] = details
                save(trial / "certificate.json", proof_json(case, ray, check, details, active,
                                                             {"group": family, "value": value, "selected_candidate": selected}))
        if vector is not None:
            np.savez_compressed(trial / "continuous_vector.npz", vector=vector, retained_rows=retained)
        save(trial / "result.json", result)
        history.append(result)
        save(directory / "attempt_history.json", history)
        print(json.dumps({"case": case, "attempt": trial_id, "group": family, "value": value,
                          "status": result["status"], "accepted": result["rejected_with_exact_certificate"],
                          "chronological_rows": len(active)}), flush=True)
    proof = proof_json(case, ray, check, details, active, {"name": "fixed greedy chronological-group deletion", "termination": termination})
    save(directory / "certificate.json", proof)
    save(directory / "exact_variable_bound_support.json", bound_support(matrix, bounds, ray, metadata))
    result = {"case": case, "initial_support": original_support, "final_support": details,
              "improved_chronological_row_count": details["chronological_rows"] < original_support["chronological_rows"],
              "improved_chronological_reference_hour_count": details["chronological_variable_reference_hour_count"] < original_support["chronological_variable_reference_hour_count"],
              "lp_attempts": len(history), "accepted_deletions": sum(r["rejected_with_exact_certificate"] for r in history),
              "solver_elapsed_s": sum(r["elapsed_s"] for r in history), "case_elapsed_s": time.monotonic() - started,
              "termination": termination, "exact_check": check,
              "minimality": "No minimal cardinality or inclusion-minimality claim; finite group order and budgets."}
    save(directory / "result.json", result)
    return result


def verify_archive(output):
    records = []
    for case in CASES:
        directory = output / case
        proof = json.loads((directory / "certificate.json").read_text(encoding="utf-8"))
        matrix, bounds, metadata, labels, _, chrono_mask = load_case(case)
        for name, expected in proof["model_artifacts"].items():
            assert sha(BASE / case / name) == expected, (case, name)
        ray = np.zeros(matrix.shape[0])
        for entry in proof["multipliers"]:
            ray[entry["row"]] = float.fromhex(entry["value_hex"])
        check = exact_ray_check(matrix, bounds, ray)
        assert check["pass"] and check["robust_pass"], (case, check)
        active = set(int(row) for row in np.flatnonzero(ray) if chrono_mask[row])
        assert active == set(proof["retained_chronological_rows"])
        details = support(matrix, labels, metadata, ray, chrono_mask)
        assert details == proof["support"], case
        expected_bounds = bound_support(matrix, bounds, ray, metadata)
        saved_bounds = json.loads((directory / "exact_variable_bound_support.json").read_text(encoding="utf-8"))
        assert saved_bounds == expected_bounds, case
        records.append({"case": case, "pass": True, "check": check, "support": details,
                        "exact_nonzero_variable_bound_terms": len(expected_bounds)})
    save(output / "solver_free_replay.json", records)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "results/research8h/sparse_farkas")
    parser.add_argument("--wall-seconds", type=float, default=840)
    parser.add_argument("--case-seconds", type=float, default=195)
    parser.add_argument("--max-attempts", type=int, default=64)
    parser.add_argument("--solve-seconds", type=float, default=12)
    parser.add_argument("--verify-archived", action="store_true")
    args = parser.parse_args()
    if args.verify_archived:
        print(json.dumps(verify_archive(args.output), indent=2), flush=True)
        return
    args.output.mkdir(parents=True, exist_ok=True)
    protocol = ROOT / "docs/research8h/SPARSE_FARKAS_PROTOCOL.md"
    files = [Path(__file__), protocol, ROOT / "src/temporal_lp_certificate.py"]
    for case in CASES:
        files.extend(BASE / case / name for name in ("matrix.npz", "bounds.npz", "dual_certificate.json", "model_metadata.json", "row_metadata.csv.gz"))
    save(args.output / "frozen_design.json", {"cases": CASES, "thresholds": THRESHOLDS,
          "wall_seconds": args.wall_seconds, "case_seconds": args.case_seconds,
          "max_attempts_per_case": args.max_attempts, "solve_seconds": args.solve_seconds,
          "inputs": [{"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for path in files]})
    deadline = time.monotonic() + args.wall_seconds
    records = []
    for case in CASES:
        records.append(run_case(case, args.output, deadline, args.case_seconds, args.max_attempts, args.solve_seconds))
        save(args.output / "summary.json", records)
    verify_archive(args.output)
    print(json.dumps([{"case": r["case"], "chron_rows_before": r["initial_support"]["chronological_rows"],
                       "chron_rows_after": r["final_support"]["chronological_rows"],
                       "reference_hours_before": r["initial_support"]["chronological_variable_reference_hour_count"],
                       "reference_hours_after": r["final_support"]["chronological_variable_reference_hour_count"]}
                      for r in records], indent=2), flush=True)


if __name__ == "__main__":
    main()
