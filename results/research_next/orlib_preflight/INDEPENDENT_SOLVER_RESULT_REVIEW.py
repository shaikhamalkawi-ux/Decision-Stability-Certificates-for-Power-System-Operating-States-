"""Independent exact saved-point/dual replay; standard library, zero optimizers."""
import ast
import hashlib
import json
import math
import struct
import time
import zipfile
from fractions import Fraction as Q
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE / "solver_prepared01"
TAU = Q.from_float(1e-5)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(p.read_text(encoding="utf-8-sig"))

def f(v):
    assert type(v) in (int, float) and math.isfinite(v)
    return Q.from_float(float(v))

def rat(v):
    return {"numerator": str(v.numerator), "denominator": str(v.denominator), "approximate": float(v)}

def exact(r):
    result = Q(int(r["numerator"]), int(r["denominator"]))
    assert r == rat(result)
    return result

def raw_arrays(p):
    result = {}
    with zipfile.ZipFile(p) as z:
        assert set(z.namelist()) == {k + ".npy" for k in ("col_value", "row_value", "row_dual", "col_dual")}
        for name in z.namelist():
            b = z.read(name)
            assert b[:6] == b"\x93NUMPY" and tuple(b[6:8]) in ((1, 0), (2, 0))
            n = 2 if b[6] == 1 else 4
            length = int.from_bytes(b[8:8+n], "little")
            header = ast.literal_eval(b[8+n:8+n+length].decode("latin1"))
            assert header["descr"] == "<f8" and not header["fortran_order"] and len(header["shape"]) == 1
            data = b[8+n+length:]
            assert len(data) == 8 * header["shape"][0]
            result[name[:-4]] = list(struct.unpack("<" + str(header["shape"][0]) + "d", data))
    return result

def matrix_point(m, x):
    worst = Q(0)
    for c, v in zip(m["columns"], x):
        if c["binary"]:
            assert v in (0, 1)
        worst = max(worst, f(c["lower"]) - v, v - f(c["upper"]))
    for row in m["rows"]:
        activity = sum((f(a) * x[j] for j, a in row["coefficients"]), Q(0))
        if row["lower"] is not None:
            worst = max(worst, f(row["lower"]) - activity)
        if row["upper"] is not None:
            worst = max(worst, activity - f(row["upper"]))
    objective = sum((f(c["objective"]) * v for c, v in zip(m["columns"], x)), Q(0))
    assert worst <= TAU
    return worst, objective

def native_point(case, m, x):
    values = {c["name"]: v for c, v in zip(m["columns"], x)}
    worst, cost, greedy = Q(0), Q(0), Q(0)
    domain = []
    def v(family, unit, hour, segment=None):
        key = f"{family}:{unit}:{hour}" + ("" if segment is None else f":{segment}")
        return values[key]
    def box(value, lower, upper):
        nonlocal worst
        worst = max(worst, lower - value, value - upper)
    def le(left, right):
        nonlocal worst
        worst = max(worst, left - right)
    def eq(left, right):
        box(left, right, right)
    for g in case["units"]:
        name = g["name"]
        width = f(float(g["pmax"] - g["pmin"]))
        for t in range(24):
            u, y, z, d, q, r = [v(k, name, t) for k in ("U", "Y", "Z", "D", "Q", "R")]
            assert all(b in (0, 1) for b in (u, y, z, d))
            previous = Q(g["age"] > 0) if t == 0 else v("U", name, t-1)
            eq(u - previous, y - z)
            le(y + z, 1)
            eq(d, y)
            le(sum((v("Y", name, s) for s in range(max(0, t-g["up"]+1), t+1)), Q(0)), u)
            le(sum((v("Z", name, s) for s in range(max(0, t-g["down"]+1), t+1)), Q(0)), 1-u)
            box(q, Q(0), width); box(r, Q(0), width)
            le(q+r, width*u)
            segments = [v("S", name, t, k) for k in range(4)]
            for k, segment in enumerate(segments):
                box(segment, Q(0), f(g["widths"][k]))
                le(segment, f(g["widths"][k])*u)
            eq(q, sum(segments, Q(0)))
            le(q+r, width*u)
            if t < 23:
                le(q, width*u)
            if t:
                le(q+r-v("Q", name, t-1), f(g["ru"]))
                le(v("Q", name, t-1)+v("R", name, t-1)-q, f(g["rd"]))
            elif g["age"] > 0:
                le(q+r, f(float(float(g["initial_power"]+g["ru"])-g["pmin"])))
                le(-q, f(float(g["rd"]-float(g["initial_power"]-g["pmin"]))))
            fixed_cost = f(g["min_cost"])*u + f(g["startup_cost"])*d
            cost += fixed_cost + sum((f(s)*a for s, a in zip(g["slopes"], segments)), Q(0))
            greedy += fixed_cost
            capacity = sum((f(w) for w in g["widths"]), Q(0))*u
            if q < 0 or q > capacity:
                domain.append(f"outside_nominal_PWL_domain:{name}:{t}")
            else:
                remaining = q
                for k in range(4):
                    amount = min(remaining, f(g["widths"][k])*u)
                    greedy += amount*f(g["slopes"][k]); remaining -= amount
        family = "Z" if g["age"] > 0 else "Y"
        residual = g["up"]-g["age"] if g["age"] > 0 else g["down"]+g["age"]
        eq(sum((v(family, name, t) for t in range(max(0, min(residual, 24)))), Q(0)), Q(0))
    for t, source in enumerate(m["order"]):
        c, reserve, injection = [v(k, "system", t) for k in ("C", "F", "N")]
        box(c, Q(0), f(case["load"][source]) if m["variant"] == "native_penalized" else Q(0))
        box(reserve, Q(0), Q(0)); box(injection, Q(0), Q(0))
        production = sum((f(g["pmin"])*v("U", g["name"], t)+v("Q", g["name"], t) for g in case["units"]), Q(0))
        eq(production+c-injection, f(case["load"][source])); eq(injection, Q(0))
        le(f(case["reserve"][source]), reserve+sum((v("R", g["name"], t) for g in case["units"]), Q(0)))
        cost += f(case["penalty"][source])*c
        greedy += f(case["penalty"][source])*c
    assert worst <= TAU
    return worst, cost, domain, None if domain else greedy

def lower(m, raw, saved):
    assert len(raw) == len(m["rows"]) and all(math.isfinite(d) for d in raw)
    dual, changed = [], []
    for i, (value, row) in enumerate(zip(raw, m["rows"])):
        d = f(value)
        if (d > 0 and row["lower"] is None) or (d < 0 and row["upper"] is None):
            changed.append(i); d = Q(0)
        dual.append(d)
    residual = [f(c["objective"]) for c in m["columns"]]
    endpoints = Q(0)
    for d, row in zip(dual, m["rows"]):
        if not d:
            continue
        endpoints += d*f(row["lower"] if d > 0 else row["upper"])
        for j, a in row["coefficients"]:
            residual[j] -= d*f(a)
    nominal = endpoints + sum((q*f(c["lower"] if q >= 0 else c["upper"]) for q, c in zip(residual, m["columns"])), Q(0))
    slope = sum((abs(d) for d in dual), Q(0)) + sum((abs(q) for q in residual), Q(0))
    expanded = nominal - TAU*slope
    assert saved["projection_changed_rows"] == changed
    assert list(map(f, saved["projected_dual"])) == dual
    assert list(map(exact, saved["exact_stationarity_residual"])) == residual
    assert exact(saved["beta"]) == endpoints and exact(saved["expansion_slope"]) == slope
    assert exact(saved["nominal_lower_bound"]) == nominal and exact(saved["expanded_lower_bound"]) == expanded
    assert exact(saved["tau"]) == TAU and not saved["dual_feasibility_required"] and not saved["exact_optimum_claim"]
    assert saved["expanded_bound_not_clipped_to_zero"]
    return nominal, expanded

def main():
    start = time.perf_counter()
    trusted = {"run_manifest.json": "30bcdeda411263c4782d34328bbfe3ec6f77814a1c0a80d5d526844a52a79306",
               "completion.json": "e67b5049f77191848ef0700f2e5698d84c8992eeb31aac5e20d22290878a8cf6",
               "cost_intervals.json": "84d1dfe74d8a115ebffc336e03840cdcae174982138fb1bbf3eadd92de6dbc8c",
               "output_manifest.json": "2713685311e705ea0c9b6080dee2594e9d077d37aea844efb0e093f722cf9a52"}
    for name, value in trusted.items():
        assert sha(ROOT/name) == value
    before = {p.relative_to(ROOT).as_posix(): sha(p) for p in ROOT.rglob("*") if p.is_file()}
    inputs, outputs = read(ROOT/"run_manifest.json")["files"], read(ROOT/"output_manifest.json")["files"]
    assert len(inputs) == 29 and len(outputs) == 96
    for row in inputs+outputs:
        p = ROOT/row["path"]
        assert p.resolve().is_relative_to(ROOT.resolve()) and p.stat().st_size == row["bytes"] and sha(p) == row["sha256"]
    plan = read(ROOT/"plan.json"); completion = read(ROOT/"completion.json")
    assert sha(ROOT/"independent_prepared_review.json") == "bc8bdbb62f7a4d92f32c22d8e921ecee35fd7d6b10059b1a8d7bac797d6e2273"
    case = read(ROOT/"inputs/normalized_case.json")
    ledger = completion["call_ledger"]
    assert completion["solver_calls"] == completion["planned_calls"] == ledger["attempted_solver_calls"] == ledger["returned_solver_calls"] == 12
    assert [{k:a[k] for k in ("model", "kind")} for a in ledger["attempts"]] == plan["sequence"]
    assert completion["frozen_inputs_unchanged"] and completion["phase_overrun_seconds"] == 0
    assert completion["elapsed_seconds_including_validation"] <= plan["phase_seconds"] == 2700
    durations, points, bounds, brackets, model_records = [], [], [], {}, []
    for name in plan["models"]:
        model = read(ROOT/"inputs"/(name+".json"))
        assert (len(model["rows"]), len(model["columns"]), sum(c["binary"] for c in model["columns"])) == (4384, 2472, 960)
        mask = [i for i,c in enumerate(model["columns"]) if c["binary"]]
        upper = None
        for kind in ("mip", "lp"):
            directory = ROOT/"outputs"/name/kind
            result = read(directory/"result.json")
            assert completion["results"][name][kind] == result
            returned = read(directory/"solver_returned.json")
            for key in ("solver_calls", "started_utc", "elapsed_seconds", "model_status", "solution_value_valid", "solution_dual_valid", "options"):
                assert result[key] == returned[key]
            assert result["solver_calls"] == 1 and not result["exact_optimality_claim"]
            assert result["solver_version"] == "1.12.0"
            assert {k:result["options"][k] for k in plan["options"][kind]} == plan["options"][kind]
            admission = read(directory/"admission.json")
            assert admission["admitted"] and admission["remaining_seconds"] >= admission["required_seconds"] == plan["options"][kind]["time_limit"] + 5
            attempt = next(a for a in ledger["attempts"] if (a["model"],a["kind"]) == (name,kind))
            assert attempt["attempted"] and attempt["returned"] and attempt["status"] == "SOLVER_RETURNED"
            assert attempt["started_utc"] == result["started_utc"] and attempt["elapsed_seconds"] == result["elapsed_seconds"]
            assert attempt["result_verdict"] == result["verdict"]
            assert result["time_limit_overrun_seconds"] == max(0, result["elapsed_seconds"]-plan["options"][kind]["time_limit"])
            durations.append(result["elapsed_seconds"])
            arrays = raw_arrays(directory/"raw_solution.npz")
            assert len(arrays["col_value"]) == 2472 and len(arrays["row_value"]) == 4384
            if kind == "mip":
                if result["accepted_expanded_upper"] is None:
                    assert not result["solution_value_valid"] and result["verdict"] == "UNKNOWN"
                    assert not (directory/"candidate_vector.json").exists()
                    assert result["accepted_nominal_upper"] is None
                    continue
                candidate = read(directory/"candidate_vector.json")
                raw = arrays["col_value"]
                assert len(candidate) == len(raw) == 2472 and all(math.isfinite(v) for v in raw+candidate)
                assert all(round(raw[j]) in (0,1) and f(candidate[j]) == round(raw[j]) for j in mask)
                change = max(abs(f(raw[j])-f(candidate[j])) for j in mask)
                assert change <= TAU and exact(result["exact_maximum_binary_snap"]) == change
                for j,c in enumerate(model["columns"]):
                    if not c["binary"]:
                        assert struct.pack("<d", raw[j]) == struct.pack("<d", candidate[j])
                x = list(map(f,candidate))
                worst, objective = matrix_point(model,x)
                direct_worst, direct_objective, domain, greedy = native_point(case,model,x)
                assert objective == direct_objective == exact(result["accepted_expanded_upper"])
                checks = read(directory/"exact_candidate_checks.json")
                assert checks["all_binary_columns_snapped"] == 960 and checks["continuous_bytes_preserved"]
                for label,w in (("matrix",worst),("direct",direct_worst)):
                    saved = checks[label]
                    assert saved["accepted"] and saved["failures"] == [] and exact(saved["tau"]) == TAU
                    assert exact(saved["nominal_max_violation"]) == w
                assert exact(checks["matrix"]["exact_objective"]) == objective
                assert exact(checks["direct"]["exact_saved_segment_objective"]) == objective
                assert checks["direct"]["canonical_domain_failures"] == domain
                assert checks["direct"]["canonical_greedy_cost_diagnostic"] == (None if greedy is None else rat(greedy))
                strict = worst == direct_worst == 0
                assert result["nominal_strict_witness"] == strict
                assert result["accepted_nominal_upper"] == (rat(objective) if strict else None)
                upper = objective
                points.append({"model":name,"full_binary_coordinates":960,"expanded_accepted":True,"nominal_accepted":strict,
                               "matrix_max_violation":rat(worst),"native_max_violation":rat(direct_worst),"objective":rat(objective)})
            else:
                assert result["accepted_expanded_upper"] is None and result["LP_primal_is_not_a_UC_witness"]
                zero = lower(model,[0.0]*4384,read(directory/"zero_dual_bound.json"))
                assert result["solution_dual_valid"]
                dual = lower(model,arrays["row_dual"],read(directory/"signed_dual_bound.json"))
                candidates = {"zero_dual_box_floor":zero,"projected_solver_rows_plus_box_residual":dual}
                selected_nominal = max(candidates,key=lambda n:candidates[n][0])
                selected_expanded = max(candidates,key=lambda n:candidates[n][1])
                assert result["nominal_bound_source"] == selected_nominal and result["expanded_bound_source"] == selected_expanded
                lb = candidates[selected_expanded][1]
                assert exact(result["selected_expanded_lower"]) == lb and exact(result["selected_nominal_lower"]) == candidates[selected_nominal][0]
                assert upper is None or lb <= upper
                brackets[name] = (lb,upper)
                bounds.append({"model":name,"retained_candidates":2,"expanded_lower":rat(lb),"nominal_lower":rat(candidates[selected_nominal][0]),
                               "numeric_LP_status":result["model_status"],"infeasibility_claim":False})
        model_records.append({"model":name,"upper_available":upper is not None,"numerical_MIP_status":completion["results"][name]["mip"]["model_status"]})
    intervals = read(ROOT/"cost_intervals.json")["rows"]
    assert len(intervals) == 4
    expected_order = [(v,t) for v in ("native_penalized","hard_service") for t in ("reverse_4_19","rotate_left1_4_19")]
    assert [(r["variant"],r["target"]) for r in intervals] == expected_order
    for row in intervals:
        li,ui = brackets["identity__"+row["variant"]]
        lt,ut = brackets[row["target"]+"__"+row["variant"]]
        for key,v in (("reference_lower",li),("reference_upper",ui),("target_lower",lt),("target_upper",ut)):
            assert row[key] == (None if v is None else rat(v))
        assert exact(row["tau"]) == TAU
        if ui is None or ut is None:
            assert row["status"] == "UNKNOWN_MISSING_FINITE_BRACKET" and row["signed_optimum_difference_interval"] is None
        else:
            lo,hi = lt-ui,ut-li
            assert lo <= hi and row["status"] == "EXACT_FINITE_SIGNED_COST_INTERVAL"
            assert row["signed_optimum_difference_interval"] == {"lower":rat(lo),"upper":rat(hi)}
    for row in inputs+outputs:
        assert sha(ROOT/row["path"]) == row["sha256"]
    after = {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob("*") if p.is_file()}
    assert after == before
    return {"status":"PASS_INDEPENDENT_EXACT_POINT_BOUND_INTERVAL_REPLAY","review_source_sha256":sha(Path(__file__)),
            "trusted_roots":trusted,"frozen_inputs_unchanged":29,"bound_outputs_unchanged":96,"producer_snapshot":before,
            "points":points,"bounds":bounds,"model_outcomes":model_records,"cost_intervals":intervals,
            "point_count":len(points),"retained_bound_candidates":12,"interval_denominator":4,
            "producer_optimizer_calls":12,"producer_solver_seconds":math.fsum(durations),
            "producer_phase_seconds":completion["elapsed_seconds_including_validation"],"reviewer_optimizer_calls":0,
            "producer_imports":0,"model_rebuilds":0,"runtime_JuMP_export_equivalence":"NOT_TESTED",
            "scope":"Exact replay of stored binary64 expanded encoding and source-equation checks; four expanded-only binary points, 12 retained objective bounds, four signed/null intervals; no scientific solve, exact optimum or hard-service infeasibility proof.",
            "review_seconds":time.perf_counter()-start}

if __name__ == "__main__":
    target = BASE/"INDEPENDENT_SOLVER_RESULT_REVIEW.json"
    assert not target.exists()
    try:
        report = main()
    except Exception as exc:
        failure = BASE/"INDEPENDENT_SOLVER_RESULT_REVIEW_FAILURE.json"
        with failure.open("x",encoding="utf-8") as fobj:
            json.dump({"error":repr(exc),"source_sha256":sha(Path(__file__))},fobj,indent=2)
        raise
    with target.open("x",encoding="utf-8") as fobj:
        json.dump(report,fobj,indent=2);fobj.write("\n")
    print(json.dumps({"status":report["status"],"points":len(report["points"]),"retained_bounds":12,"intervals":4,
                      "report_sha256":sha(target),"seconds":report["review_seconds"]}))
