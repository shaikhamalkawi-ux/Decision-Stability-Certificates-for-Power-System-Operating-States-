"""Independent solver-free exact energy bounds for the two January orders."""
from __future__ import annotations
import csv
from datetime import datetime, timezone
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
import numpy as np
from scipy.sparse import load_npz

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "results/research8h/seasonal_transfer"
UNCAPPED = ROOT / "results/seasonal_uncapped"
OUTPUT = ROOT / "results/research8h/energy_price_bounds"
PROTOCOL = ROOT / "docs/research8h/ENERGY_PRICE_BOUNDS.md"
CASES = ["seed_26093100", "seed_26093101"]
TAU = Q.from_float(1e-5)


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def f(value): return Q.from_float(float(value))
def save(path, value): path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
def read(path): return json.loads(path.read_text(encoding="utf-8"))
def arrays(path):
    with np.load(path) as z: return {k: z[k].copy() for k in z.files}
def labels(path):
    with gzip.open(path, "rt", encoding="utf-8", newline="") as stream: return list(csv.DictReader(stream))
def rat(value):
    scale = 1000000
    lo = (value.numerator * scale) // value.denominator
    hi = -((-value.numerator * scale) // value.denominator)
    return {"numerator": str(value.numerator), "denominator": str(value.denominator),
            "approximate": float(value), "outward_floor_6dp": lo / scale,
            "outward_ceiling_6dp": hi / scale}
def from_rat(value): return Q(int(value["numerator"]), int(value["denominator"]))


def point_check(A, b, x, binary):
    assert len(x) == A.shape[1] and np.isfinite(x).all()
    point = [f(v) for v in x]
    assert len(binary) == len(point)
    assert np.array_equal(np.flatnonzero(binary), np.arange(6888, 18984))
    exact_binary = all(point[j] in (0, 1) for j in np.flatnonzero(binary))
    col_max, row_max = Q(0), Q(0)
    for j, value in enumerate(point):
        for side in ("lower", "upper"):
            bound = b["column_" + side][j]
            if np.isfinite(bound):
                violation = f(bound) - value if side == "lower" else value - f(bound)
                col_max = max(col_max, violation)
    for i in range(A.shape[0]):
        value = sum((f(A.data[e]) * point[A.indices[e]] for e in range(A.indptr[i], A.indptr[i+1])), Q(0))
        for side in ("lower", "upper"):
            bound = b["row_" + side][i]
            if np.isfinite(bound):
                violation = f(bound) - value if side == "lower" else value - f(bound)
                row_max = max(row_max, violation)
    return {"exact_binary_UYZ": exact_binary,
            "exact_nominal_pass": bool(exact_binary and col_max <= 0 and row_max <= 0),
            "exact_expanded_pass": bool(exact_binary and col_max <= TAU and row_max <= TAU),
            "maximum_exact_column_violation": rat(col_max), "maximum_exact_row_violation": rat(row_max),
            "tau": rat(TAU), "evaluated_rows": A.shape[0], "evaluated_columns": A.shape[1]}, point


def objective_and_roster(meta, native_gen):
    names = meta["unit_names"]
    assert len(names) == 41 and len(set(names)) == 41
    fuel = {r["GEN UID"]: r["Fuel"] for r in native_gen}
    fossil = [j for j, uid in enumerate(names) if fuel[uid] in {"Coal", "Oil", "NG"}]
    assert len(fossil) == 23 and [names[j] for j in fossil] == meta["fossil_units"]
    assert names[23] == "121_NUCLEAR_1" and 23 not in fossil
    assert meta["offsets"] == {"P": 0, "U": 6888, "Y": 10920, "Z": 14952, "theta": 18984}
    assert meta["individual_mean_constraints"] == 0
    objective = np.zeros(23016)
    objective[[t*41+j for t in range(168) for j in fossil]] = 1.
    return objective, fossil


def identity_lower(A, b, rows, native, fossil):
    selected = [i for i, row in enumerate(rows) if row["family"] == "aggregate_balance"]
    assert len(selected) == 168
    by_hour = {int(rows[i]["hour_0based"]): i for i in selected}
    assert set(by_hour) == set(range(168))
    nonfossil = sorted(set(range(41)) - set(fossil))
    assert len(nonfossil) == 18
    per_hour = []
    for t in range(168):
        i = by_hour[t]; start, end = A.indptr[i:i+2]
        assert np.array_equal(A.indices[start:end], np.arange(t*41, (t+1)*41))
        assert np.array_equal(A.data[start:end], np.ones(41))
        assert b["row_lower"][i] == b["row_upper"][i] == native["net"][t]
        lower = sum((f(b["column_lower"][t*41+j])-TAU for j in fossil), Q(0))
        balance = f(b["row_lower"][i])-TAU-sum((f(b["column_upper"][t*41+j])+TAU for j in nonfossil), Q(0))
        value = max(lower, balance)
        per_hour.append({"hour_0based": t, "aggregate_row": i, "fossil_box_bound": rat(lower),
                         "balance_nonfossil_box_bound": rat(balance), "selected_lower_bound": rat(value)})
    total = sum((from_rat(x["selected_lower_bound"]) for x in per_hour), Q(0))
    return total, {"all_168_actual_row_supports_verified": True, "fossil_count": 23,
                   "nonfossil_count": 18, "native_net_equal_actual_row_bounds": True,
                   "hourly_bounds": per_hour, "total_lower_bound_MWh": rat(total)}


def ray_objective_lower(A, b, parent_A, parent_b, row_labels, cert, objective):
    cap = [i for i, row in enumerate(row_labels) if row["family"] == "fossil_energy_cap"]
    assert len(cap) == 1
    cap = cap[0]; keep = np.delete(np.arange(parent_A.shape[0]), cap)
    assert (A != parent_A[keep]).nnz == 0
    assert all(np.array_equal(b[k], parent_b[k][keep] if k.startswith("row_") else parent_b[k]) for k in b)
    caprow = parent_A.getrow(cap).toarray().ravel()
    assert np.array_equal(caprow, objective)
    assert np.isneginf(parent_b["row_lower"][cap]) and parent_b["row_upper"][cap] == 23195
    d = [Q(0)] * parent_A.shape[0]
    for entry in cert["multipliers"]:
        d[entry["row"]] = f(float.fromhex(entry["value_hex"]))
    gamma = -d[cap]; assert gamma > 0
    s = [d[int(i)] / gamma for i in keep]
    q = [f(v) for v in objective]
    row_term = Q(0)
    for i, weight in enumerate(s):
        if not weight: continue
        bound = b["row_lower" if weight > 0 else "row_upper"][i]
        assert np.isfinite(bound)
        row_term += weight * f(bound)
        for e in range(A.indptr[i], A.indptr[i+1]):
            q[A.indices[e]] -= weight * f(A.data[e])
    assert np.isfinite(b["column_lower"]).all() and np.isfinite(b["column_upper"]).all()
    box_term = sum((weight*f(b["column_lower" if weight >= 0 else "column_upper"][j]) for j, weight in enumerate(q)), Q(0))
    nominal = row_term + box_term
    correction = TAU*(sum(map(abs, s), Q(0)) + sum(map(abs, q), Q(0)))
    expanded = nominal - correction
    proof = cert["verification"]
    gap = Q(int(proof["exact_gap_numerator"]), int(proof["exact_gap_denominator"]))
    robust = Q(int(proof["exact_robust_gap_numerator"]), int(proof["exact_robust_gap_denominator"]))
    assert gap > 0 and robust > 0
    assert nominal == Q(23195)+gap/gamma
    assert expanded == Q(23195)+robust/gamma+TAU
    return expanded, {"gamma": rat(gamma), "noncap_row_term": rat(row_term), "box_term": rat(box_term),
                      "nominal_lower_bound_MWh": rat(nominal), "noncap_expansion_correction_MWh": rat(correction),
                      "expanded_lower_bound_MWh": rat(expanded), "cap_removal_identities_exact": True,
                      "bound_valid_for_continuous_and_binary_models": True}


def main():
    OUTPUT.mkdir(parents=True, exist_ok=False)
    paths = [Path(__file__), PROTOCOL, UNCAPPED/"prepared_freeze.json", UNCAPPED/"input_manifest.csv",
             SOURCE/"independent_review.json"]
    freeze = read(UNCAPPED/"prepared_freeze.json")
    native_gen_path = Path(freeze["source_v3"]) / "raw/RTS-GMLC_v0.2.3/RTS_Data/SourceData/gen.csv"
    if not native_gen_path.is_file():
        candidates = list((Path(freeze["source_v3"])/"raw").rglob("gen.csv"))
        assert len(candidates) == 1
        native_gen_path = candidates[0]
    with native_gen_path.open(newline="", encoding="utf-8-sig") as stream: native_gen = list(csv.DictReader(stream))
    paths.append(native_gen_path)
    with (UNCAPPED/"input_manifest.csv").open(newline="", encoding="utf-8") as stream: frozen = list(csv.DictReader(stream))
    assert sha(UNCAPPED/"input_manifest.csv") == freeze["input_manifest_sha256"]
    assert all(sha(Path(x["path"])) == x["sha256"] for x in frozen)
    assert any(Path(x["path"]).resolve() == native_gen_path.resolve() for x in frozen)
    identity_dir = SOURCE/"january_identity"
    identity_files = ["matrix.npz", "bounds.npz", "model_metadata.json", "native_inputs.npz", "row_metadata.csv.gz", "constructive_vector.npz", "integrality.npz"]
    paths.extend(identity_dir/name for name in identity_files)
    availability = {}
    for case in CASES:
        directory = UNCAPPED/case
        availability[case] = (directory/"result.json").is_file()
        if availability[case]:
            names = ["matrix.npz", "bounds.npz", "original_integrality.npz", "objective.npz", "model_metadata.json", "native_inputs.npz", "row_metadata.csv.gz", "result.json", "recovered_vector.npz", "exact_point_check.json", "native_no_cap_check.json"]
            paths.extend(directory/name for name in names if (directory/name).is_file())
            paths.extend(SOURCE/case/name for name in ["matrix.npz", "bounds.npz", "integrality.npz", "native_inputs.npz", "row_metadata.csv.gz", "model_metadata.json", "lp/dual_certificate.json"])
    bound_paths = [{"path": str(p), "sha256": sha(p), "bytes": p.stat().st_size} for p in dict.fromkeys(paths)]
    save(OUTPUT/"audit_freeze.json", {"utc": datetime.now(timezone.utc).isoformat(), "before_numeric_classification": True,
                                    "optimization_calls": 0, "available_completed_case_files": availability, "inputs": bound_paths})
    A = load_npz(identity_dir/"matrix.npz"); b = arrays(identity_dir/"bounds.npz")
    meta = read(identity_dir/"model_metadata.json"); native = arrays(identity_dir/"native_inputs.npz")
    objective, fossil = objective_and_roster(meta, native_gen)
    identity_check, point = point_check(A, b, arrays(identity_dir/"constructive_vector.npz")["vector"], arrays(identity_dir/"integrality.npz")["integrality"])
    assert identity_check["exact_expanded_pass"]
    E_reference = sum((f(c)*p for c, p in zip(objective, point)), Q(0))
    prior = read(SOURCE/"independent_review.json")
    assert E_reference == from_rat(prior["reference_exact_fossil_energy_MWh"])
    L_identity, identity_bound = identity_lower(A, b, labels(identity_dir/"row_metadata.csv.gz"), native, fossil)
    assert L_identity <= E_reference
    save(OUTPUT/"identity_bound.json", {"point_check": identity_check, "E_reference_MWh": rat(E_reference),
                                       "lower_bound": identity_bound, "cap_deletion_preserves_reference": True})
    results = []
    for case in CASES:
        directory = UNCAPPED/case
        if not availability[case]:
            results.append({"case": case, "status": "PENDING_NO_COMPLETED_RESULT_AT_AUDIT_FREEZE"})
            continue
        result = read(directory/"result.json")
        if result["verdict"] != "VERIFIED_UNCAPPED_BINARY_WITNESS_EXPANDED_MODEL":
            results.append({"case": case, "status": "NO_ACCEPTED_EXACT_EXPANDED_WITNESS", "original_verdict": result["verdict"]})
            continue
        target_A = load_npz(directory/"matrix.npz"); target_b = arrays(directory/"bounds.npz")
        target_meta = read(directory/"model_metadata.json")
        target_objective, target_fossil = objective_and_roster(target_meta, native_gen)
        assert np.array_equal(objective, target_objective) and target_fossil == fossil
        assert np.array_equal(target_objective, arrays(directory/"objective.npz")["objective"])
        parent = SOURCE/case; parent_A = load_npz(parent/"matrix.npz"); parent_b = arrays(parent/"bounds.npz")
        native_target, native_parent = arrays(directory/"native_inputs.npz"), arrays(parent/"native_inputs.npz")
        assert native_target.keys() == native_parent.keys()
        assert all(np.array_equal(native_target[k], native_parent[k]) for k in native_target)
        original_integer = arrays(directory/"original_integrality.npz")["integrality"]
        assert np.array_equal(original_integer, arrays(parent/"integrality.npz")["integrality"])
        checked, target_point = point_check(target_A, target_b, arrays(directory/"recovered_vector.npz")["vector"], original_integer)
        assert checked["exact_expanded_pass"]
        U_target = sum((f(c)*p for c, p in zip(objective, target_point)), Q(0))
        assert U_target == from_rat(result["recovered_fossil_energy"])
        cert = read(parent/"lp/dual_certificate.json")
        assert cert["model_artifacts"]["matrix.npz"] == sha(parent/"matrix.npz")
        assert cert["model_artifacts"]["bounds.npz"] == sha(parent/"bounds.npz")
        L_target, ray_check = ray_objective_lower(target_A, target_b, parent_A, parent_b, labels(parent/"row_metadata.csv.gz"), cert, objective)
        prior_case = next(x for x in prior["cases"] if x["seed"] == int(case.split("_")[1]))
        assert L_target == from_rat(prior_case["uncapped_NONCAP_and_box_expanded_energy_lower_bound_MWh"])
        assert L_target <= U_target
        record = {"case": case, "status": "EXACT_EXPANDED_BINARY_ENERGY_BRACKETS_VERIFIED", "point_check": checked,
                  "native_arrays_exactly_match_capped_source": True, "original_integrality_exactly_matches": True,
                  "exact_cap_row_deletion_and_other_bounds_unchanged": True, "ray_objective_bound": ray_check,
                  "target_lower_MWh": rat(L_target), "target_upper_MWh": rat(U_target), "reference_energy_MWh": rat(E_reference),
                  "identity_lower_MWh": rat(L_identity),
                  "optimum_to_optimum_difference_MWh": {"lower": rat(L_target-E_reference), "upper": rat(U_target-L_identity)},
                  "target_optimum_excess_over_chosen_reference_MWh": {"lower": rat(L_target-E_reference), "upper": rat(U_target-E_reference)},
                  "solver_objective_and_bound_not_used_as_exact_proof": True, "optimization_calls": 0}
        save(OUTPUT/(case+".json"), record); results.append(record)
    assert all(sha(Path(x["path"])) == x["sha256"] for x in bound_paths)
    save(OUTPUT/"results.json", results)
    save(OUTPUT/"completion.json", {"utc": datetime.now(timezone.utc).isoformat(), "optimization_calls": 0,
                                   "all_bound_input_hashes_unchanged": True, "files_bound": len(bound_paths),
                                   "uncapped_preparation_manifest_files_checked": len(frozen)})
    print(json.dumps({"results": [{"case": x["case"], "status": x["status"]} for x in results], "optimization_calls": 0}), flush=True)


if __name__ == "__main__": main()
