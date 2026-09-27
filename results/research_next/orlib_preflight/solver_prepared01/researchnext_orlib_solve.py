"""Bounded OR-LIB solver harness, source only until explicit reviewed gates.

No downloads or installs. prepare-run snapshots an already prepared adapter
archive. run-prepared needs an independently reviewed manifest/hash receipt.
self-test exercises only exact dual-bound arithmetic on synthetic one-column
models and never imports an optimizer or the scientific adapter.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import sys
import time
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path, PurePosixPath

ADAPTER_SHA = "e2b137f6a7ba23d1a9b12663ee1deee7bf2a3fffdd1f95d4718fb9ba37d17dc1"
ADAPTER_PROTOCOL_SHA = "4fb15c1525405561a7c9ce19f5d4bb01dde55ff014b70bd55173d067f929f04a"
TAU = 1e-5
PHASE_SECONDS = 2700.0
MODEL_NAMES = [f"{case}__{variant}" for case in ("identity", "reverse_4_19", "rotate_left1_4_19")
               for variant in ("native_penalized", "hard_service")]
OPTIONS = {
    "mip": {"time_limit": 300.0, "threads": 1, "random_seed": 0, "presolve": "on", "mip_rel_gap": 1e-8},
    "lp": {"time_limit": 30.0, "threads": 1, "random_seed": 0, "solver": "simplex", "presolve": "off"},
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def utc():
    return datetime.now(timezone.utc).isoformat()


def encoded(value):
    return (json.dumps(value, indent=2, allow_nan=False) + "\n").encode("utf-8")


def write_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as f:
        f.write(encoded(value))


def number(value):
    if value is None:
        return None
    value = float(value)
    return value if math.isfinite(value) else None


def F(value):
    require(type(value) in (int, float) and math.isfinite(value), "Nonfinite/nonreal exact-arithmetic input")
    return Fraction.from_float(float(value))


def rat(value):
    try:
        approximate = float(value)
    except OverflowError:
        approximate = None
    return {"numerator": str(value.numerator), "denominator": str(value.denominator), "approximate": approximate}


def from_rat(value):
    return Fraction(int(value["numerator"]), int(value["denominator"]))


def local_file(root, rel):
    require(isinstance(rel, str) and "\\" not in rel and ":" not in rel, "Unsafe relative path")
    p = PurePosixPath(rel)
    require(not p.is_absolute() and p.parts and all(x not in (".", "..") for x in p.parts), "Unsafe path component")
    result = root.joinpath(*p.parts)
    require(result.resolve().is_relative_to(root.resolve()), "Path escapes archive")
    return result


def import_adapter(path):
    path = Path(path)
    require(sha(path.read_bytes()) == ADAPTER_SHA, "Adapter source mismatch")
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("reviewed_orlib_adapter", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def snapshot_adapter_archive(root, expected_manifest, adapter):
    root = Path(root)
    manifest_bytes = (root / "manifest.json").read_bytes()
    require(sha(manifest_bytes) == expected_manifest, "Adapter manifest mismatch")
    manifest = json.loads(manifest_bytes)
    require(manifest["schema"] == "orlib-prepared-manifest-v1", "Unexpected adapter manifest")
    snapshots, folded = {}, set()
    for row in manifest["files"]:
        name = row["path"]
        require(name not in snapshots and name.casefold() not in folded, "Duplicate/case-colliding input")
        b = local_file(root, name).read_bytes()
        require(len(b) == row["bytes"] and sha(b) == row["sha256"], "Prepared input mismatch: " + name)
        snapshots[name] = b
        folded.add(name.casefold())
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
    require(actual == set(snapshots) | {"manifest.json"}, "Unexpected/missing adapter archive files")
    require(sha(snapshots["researchnext_orlib_uc.py"]) == ADAPTER_SHA, "Archived adapter mismatch")
    require(sha(snapshots["ORLIB_TRANSFER_PROTOCOL.md"]) == ADAPTER_PROTOCOL_SHA, "Archived adapter protocol mismatch")
    case = adapter.parse_selected(snapshots["selected_case.json.gz"])
    require(json.loads(snapshots["normalized_case.json"]) == case, "Normalized source mismatch")
    for rel, digest in adapter.SOURCE_SHA.items():
        require(sha(snapshots["upstream/" + rel]) == digest, "Native source binding mismatch")
    orders, models = adapter.prospective_orders(), {}
    for name in MODEL_NAMES:
        case_name, variant = name.split("__")
        model = json.loads(snapshots[name + ".json"])
        require(model == adapter.build(case, variant, orders[case_name]), "Model differs from reviewed adapter: " + name)
        require(model["binary_count"] == 960, "Full original binary mask not preserved")
        require(all(math.isfinite(c["lower"]) and math.isfinite(c["upper"]) for c in model["columns"]), "Infinite column box")
        models[name] = model
    for case_name in orders:
        native, hard = (models[case_name + "__" + v] for v in ("native_penalized", "hard_service"))
        require(native["rows"] == hard["rows"], "Hard-service rows changed")
        for a, b in zip(native["columns"], hard["columns"]):
            expected = dict(a)
            if a["name"].startswith("C:system:"):
                expected["upper"] = 0.0
            require(expected == b, "Hard-service change outside curtailment upper bound")
    snapshots["manifest.json"] = manifest_bytes
    return snapshots, case, models


def prepare_run(input_root, expected_manifest, adapter_path, solver_protocol, output):
    input_root, output = Path(input_root), Path(output)
    require(not output.exists(), "Solver preparation must use a fresh directory")
    runner_bytes = Path(__file__).read_bytes()
    adapter_bytes = Path(adapter_path).read_bytes()
    protocol_bytes = Path(solver_protocol).read_bytes()
    require(Path(solver_protocol).name == "ORLIB_SOLVER_PROTOCOL.md", "Wrong solver protocol")
    adapter = import_adapter(adapter_path)
    snapshots, case, models = snapshot_adapter_archive(input_root, expected_manifest, adapter)
    output.mkdir(parents=True, exist_ok=False)
    for rel, b in snapshots.items():
        p = local_file(output / "inputs", rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b)
    (output / "researchnext_orlib_solve.py").write_bytes(runner_bytes)
    (output / "ORLIB_SOLVER_PROTOCOL.md").write_bytes(protocol_bytes)
    runtime = {"python": sys.version, "numpy": importlib.metadata.version("numpy"),
               "highspy": importlib.metadata.version("highspy")}
    plan = {"schema": "orlib-solver-plan-v1", "status": "PREPARED_NOT_RUN",
            "source_adapter_sha256": ADAPTER_SHA, "adapter_protocol_sha256": ADAPTER_PROTOCOL_SHA,
            "solver_source_sha256": sha(runner_bytes), "solver_protocol_sha256": sha(protocol_bytes),
            "adapter_manifest_sha256": expected_manifest, "models": MODEL_NAMES,
            "sequence": [{"model": n, "kind": kind} for n in MODEL_NAMES for kind in ("mip", "lp")],
            "options": OPTIONS, "phase_seconds": PHASE_SECONDS, "guard_padding_seconds": 5.0,
            "tau_binary64": TAU, "tau_exact": rat(F(TAU)), "runtime": runtime,
            "binary_columns_per_model": 960, "native_export_identity": "NOT_TESTED",
            "solver_calls": 0}
    for rel, b in snapshots.items():
        require(local_file(input_root, rel).read_bytes() == b, "Input changed during solver preparation")
    require(Path(__file__).read_bytes() == runner_bytes and Path(adapter_path).read_bytes() == adapter_bytes,
            "Source changed during solver preparation")
    require(Path(solver_protocol).read_bytes() == protocol_bytes, "Solver protocol changed during preparation")
    write_new(output / "plan.json", plan)
    entries = [{"path": p.relative_to(output).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p.read_bytes())}
               for p in sorted(output.rglob("*")) if p.is_file()]
    write_new(output / "run_manifest.json", {"schema": "orlib-run-manifest-v1", "files": entries})
    return {"status": "PREPARED_NOT_RUN", "files": len(entries), "solver_calls": 0,
            "run_manifest_sha256": sha((output / "run_manifest.json").read_bytes())}


def exact_lower_bound(model, raw, tau=TAU):
    """Arbitrary signed row multipliers + finite-box residual correction."""
    require(len(raw) == len(model["rows"]), "Dual length mismatch")
    projected, altered = [], []
    for i, (value, row) in enumerate(zip(raw, model["rows"])):
        d = F(value)
        if (d > 0 and row["lower"] is None) or (d < 0 and row["upper"] is None):
            altered.append(i)
            d = Fraction(0)
        projected.append(d)
    q = [F(c["objective"]) for c in model["columns"]]
    beta = Fraction(0)
    for d, row in zip(projected, model["rows"]):
        if d == 0:
            continue
        beta += d * F(row["lower"] if d > 0 else row["upper"])
        for j, a in row["coefficients"]:
            q[j] -= F(a) * d
    nominal = beta + sum((v * F(c["lower"] if v >= 0 else c["upper"])
                          for v, c in zip(q, model["columns"])), Fraction(0))
    slope = sum(map(abs, projected), Fraction(0)) + sum(map(abs, q), Fraction(0))
    expanded = nominal - F(tau) * slope
    return {"nominal_lower_bound": rat(nominal), "expanded_lower_bound": rat(expanded),
            "beta": rat(beta), "expansion_slope": rat(slope), "tau": rat(F(tau)),
            "projection_changed_rows": altered, "projected_dual": [float(d) for d in projected],
            "exact_stationarity_residual": [rat(v) for v in q],
            "dual_feasibility_required": False, "exact_optimum_claim": False,
            "expanded_bound_not_clipped_to_zero": True}


def solver_model(model, kind, highspy, np):
    lp = highspy.HighsLp()
    lp.num_row_, lp.num_col_ = len(model["rows"]), len(model["columns"])
    lp.col_cost_ = np.array([c["objective"] for c in model["columns"]], dtype=float)
    lp.col_lower_ = np.array([c["lower"] for c in model["columns"]], dtype=float)
    lp.col_upper_ = np.array([c["upper"] for c in model["columns"]], dtype=float)
    lp.row_lower_ = np.array([-np.inf if r["lower"] is None else r["lower"] for r in model["rows"]])
    lp.row_upper_ = np.array([np.inf if r["upper"] is None else r["upper"] for r in model["rows"]])
    start, indices, values = [0], [], []
    for row in model["rows"]:
        for j, a in row["coefficients"]:
            indices.append(j)
            values.append(a)
        start.append(len(indices))
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.num_row_, lp.a_matrix_.num_col_ = lp.num_row_, lp.num_col_
    lp.a_matrix_.start_ = np.array(start, dtype=np.int32)
    lp.a_matrix_.index_ = np.array(indices, dtype=np.int32)
    lp.a_matrix_.value_ = np.array(values, dtype=float)
    if kind == "mip":
        lp.integrality_ = [highspy.HighsVarType.kInteger if c["binary"] else highspy.HighsVarType.kContinuous
                           for c in model["columns"]]
    return lp


def run_one(case, model, kind, directory, phase_start, adapter, call_ledger):
    import numpy as np
    import highspy

    directory.mkdir(parents=True, exist_ok=False)
    solver = highspy.Highs()
    options = dict(OPTIONS[kind], log_to_console=False, log_file=str((directory / "solver.log").resolve()))
    for k, v in options.items():
        require(solver.setOptionValue(k, v) == highspy.HighsStatus.kOk, "Solver option rejected: " + k)
    require(solver.passModel(solver_model(model, kind, highspy, np)) == highspy.HighsStatus.kOk, "Model rejected")
    result = {"kind": kind, "options": options, "solver_version": solver.version(), "solver_calls": 0,
              "verdict": "UNKNOWN", "exact_optimality_claim": False, "accepted_expanded_upper": None,
              "accepted_nominal_upper": None, "selected_expanded_lower": None, "selected_nominal_lower": None}
    # No scientific timing promise: phase limit and padding are soft guards.
    remaining = PHASE_SECONDS - (time.perf_counter() - phase_start)
    admitted = remaining >= options["time_limit"] + 5.0
    write_new(directory / "admission.json", {"utc": utc(), "remaining_seconds": remaining,
                                             "required_seconds": options["time_limit"] + 5.0, "admitted": admitted})
    if not admitted:
        result.update(verdict="NOT_RUN_PHASE_GUARD", elapsed_seconds=0.0)
        call_ledger["current"]["status"] = result["verdict"]
        write_new(directory / "result.json", result)
        return result
    write_new(directory / "call_ready.json", {"utc": utc(), "kind": kind,
              "meaning": "Setup complete; actual call is conditional on the immediately following guard",
              "not_an_assertion_that_solver_was_called": True})
    # Recheck after the small admission write and immediately before the call.
    remaining = PHASE_SECONDS - (time.perf_counter() - phase_start)
    if remaining < options["time_limit"] + 5.0:
        result.update(verdict="NOT_RUN_POST_WRITE_PHASE_GUARD", elapsed_seconds=0.0)
        call_ledger["current"]["status"] = result["verdict"]
        write_new(directory / "result.json", result)
        return result
    started, started_utc = time.perf_counter(), utc()
    call_ledger["current"].update(status="SOLVER_CALL_ATTEMPTED", attempted=True, started_utc=started_utc)
    call_ledger["attempted_solver_calls"] += 1
    call_ledger["attempts"].append(call_ledger["current"])
    run_status = solver.run()
    elapsed = time.perf_counter() - started
    call_ledger["returned_solver_calls"] += 1
    call_ledger["current"].update(status="SOLVER_RETURNED", returned=True, ended_utc=utc(),
                                  elapsed_seconds=elapsed, run_status=str(run_status))
    solution, info = solver.getSolution(), solver.getInfo()
    result.update(solver_calls=1, started_utc=started_utc, ended_utc=utc(), elapsed_seconds=elapsed,
                  run_status=str(run_status), model_status=solver.modelStatusToString(solver.getModelStatus()),
                  solution_value_valid=bool(solution.value_valid), solution_dual_valid=bool(solution.dual_valid),
                  numeric_objective=number(info.objective_function_value), numeric_mip_bound=number(info.mip_dual_bound),
                  numeric_mip_gap=number(info.mip_gap), primal_solution_status=int(info.primal_solution_status),
                  dual_solution_status=int(info.dual_solution_status), mip_node_count=int(info.mip_node_count),
                  simplex_iterations=int(info.simplex_iteration_count),
                  time_limit_overrun_seconds=max(0.0, elapsed - options["time_limit"]))
    write_new(directory / "solver_returned.json", result)
    raw = np.asarray(solution.col_value, dtype=np.float64)
    np.savez_compressed(directory / "raw_solution.npz", col_value=raw,
                        row_value=np.asarray(solution.row_value, dtype=np.float64),
                        row_dual=np.asarray(solution.row_dual, dtype=np.float64),
                        col_dual=np.asarray(solution.col_dual, dtype=np.float64))
    if kind == "mip" and solution.value_valid and len(raw) == len(model["columns"]) and np.isfinite(raw).all():
        mask = np.array([c["binary"] for c in model["columns"]], dtype=bool)
        rounded = np.rint(raw[mask])
        eligible = bool(np.isin(rounded, [0.0, 1.0]).all())
        max_change = max((abs(F(float(a)) - F(float(b))) for a, b in zip(raw[mask], rounded)), default=Fraction(0))
        eligible = eligible and max_change <= F(TAU)
        result["candidate_eligible"] = eligible
        result["exact_maximum_binary_snap"] = rat(max_change)
        if eligible:
            candidate = raw.copy()
            candidate[mask] = rounded
            require(np.array_equal(np.ascontiguousarray(raw[~mask]).view(np.uint64),
                                   np.ascontiguousarray(candidate[~mask]).view(np.uint64)), "Continuous coordinates changed")
            write_new(directory / "candidate_vector.json", candidate.tolist())
            matrix = adapter.exact_matrix_check(model, candidate.tolist(), TAU)
            direct = adapter.direct_check(case, model, candidate.tolist(), TAU)
            write_new(directory / "exact_candidate_checks.json", {"matrix": matrix, "direct": direct,
                       "all_binary_columns_snapped": int(mask.sum()), "continuous_bytes_preserved": True})
            if matrix["accepted"] and direct["accepted"]:
                require(matrix["exact_objective"] == direct["exact_saved_segment_objective"], "Objective checker mismatch")
                result["verdict"] = "EXACT_EXPANDED_FULL_BINARY_UPPER_WITNESS"
                result["accepted_expanded_upper"] = matrix["exact_objective"]
                strict = matrix["nominal_max_violation"]["numerator"] == "0" and direct["nominal_max_violation"]["numerator"] == "0"
                result["nominal_strict_witness"] = strict
                if strict:
                    result["accepted_nominal_upper"] = matrix["exact_objective"]
            else:
                result["verdict"] = "UNKNOWN_REJECTED_CANDIDATE"
    if kind == "lp":
        floor = exact_lower_bound(model, [0.0] * len(model["rows"]))
        write_new(directory / "zero_dual_bound.json", floor)
        proofs = {"zero_dual_box_floor": floor}
        dual = [float(d) for d in solution.row_dual]
        if solution.dual_valid and len(dual) == len(model["rows"]) and all(math.isfinite(d) for d in dual):
            proof = exact_lower_bound(model, dual)
            write_new(directory / "signed_dual_bound.json", proof)
            proofs["projected_solver_rows_plus_box_residual"] = proof
        nominal_name = max(proofs, key=lambda n: from_rat(proofs[n]["nominal_lower_bound"]))
        expanded_name = max(proofs, key=lambda n: from_rat(proofs[n]["expanded_lower_bound"]))
        result.update(verdict="EXACT_OBJECTIVE_LOWER_BOUND_ONLY", selected_nominal_lower=proofs[nominal_name]["nominal_lower_bound"],
                      selected_expanded_lower=proofs[expanded_name]["expanded_lower_bound"],
                      nominal_bound_source=nominal_name, expanded_bound_source=expanded_name,
                      LP_primal_is_not_a_UC_witness=True)
    write_new(directory / "result.json", result)
    return result


def validate_run_archive(root, expected_manifest):
    root = Path(root)
    b = (root / "run_manifest.json").read_bytes()
    require(sha(b) == expected_manifest, "Run manifest mismatch")
    m = json.loads(b)
    require(m["schema"] == "orlib-run-manifest-v1", "Wrong run manifest schema")
    snapshots, folded = {}, set()
    for r in m["files"]:
        require(r["path"] not in snapshots and r["path"].casefold() not in folded, "Duplicate prepared path")
        data = local_file(root, r["path"]).read_bytes()
        require(len(data) == r["bytes"] and sha(data) == r["sha256"], "Frozen run input changed")
        snapshots[r["path"]] = data
        folded.add(r["path"].casefold())
    plan = json.loads(snapshots["plan.json"])
    require(plan["models"] == MODEL_NAMES and plan["options"] == OPTIONS and plan["phase_seconds"] == PHASE_SECONDS,
            "Plan differs from fixed source")
    require(plan["tau_binary64"] == TAU and plan["tau_exact"] == rat(F(TAU)), "Tau mismatch")
    require(plan["solver_source_sha256"] == sha(Path(__file__).read_bytes()), "Executing source differs from freeze")
    require(plan["solver_protocol_sha256"] == sha(snapshots["ORLIB_SOLVER_PROTOCOL.md"]), "Protocol binding mismatch")
    adapter = import_adapter(root / "inputs/researchnext_orlib_uc.py")
    _, case, models = snapshot_adapter_archive(root / "inputs", plan["adapter_manifest_sha256"], adapter)
    return snapshots, plan, adapter, case, models


def run_prepared(root, expected_manifest, review_path, expected_review):
    root = Path(root)
    phase_start, started_utc = time.perf_counter(), utc()
    snapshots, plan, adapter, case, models = validate_run_archive(root, expected_manifest)
    review_bytes = Path(review_path).read_bytes()
    require(sha(review_bytes) == expected_review, "Independent prepared review hash mismatch")
    review = json.loads(review_bytes)
    require(review["status"] == "PASS_PREPARED_ORLIB" and review["run_manifest_sha256"] == expected_manifest,
            "Independent prepared gate not satisfied")
    require(review["adapter_sha256"] == ADAPTER_SHA and review["solver_sha256"] == plan["solver_source_sha256"],
            "Prepared review source binding mismatch")
    write_new(root / "execution_started.json", {"utc": started_utc, "run_manifest_sha256": expected_manifest,
              "independent_review_sha256": expected_review, "phase_seconds": PHASE_SECONDS, "no_automatic_retry": True})
    (root / "independent_prepared_review.json").write_bytes(review_bytes)
    results = {}
    call_ledger = {"attempted_solver_calls": 0, "returned_solver_calls": 0, "current": None, "attempts": []}
    try:
        for name in MODEL_NAMES:
            results[name] = {}
            for kind in ("mip", "lp"):
                call_ledger["current"] = {"model": name, "kind": kind, "status": "SETUP",
                                          "setup_started_utc": utc(), "attempted": False,
                                          "returned": False, "started_utc": None}
                result = run_one(case, models[name], kind, root / "outputs" / name / kind,
                                 phase_start, adapter, call_ledger)
                results[name][kind] = result
                call_ledger["current"]["result_verdict"] = result["verdict"]
                print(json.dumps({"model": name, "kind": kind, "verdict": result["verdict"],
                                  "model_status": result.get("model_status"), "calls": result["solver_calls"]}), flush=True)
            upper = results[name]["mip"]["accepted_expanded_upper"]
            lower = results[name]["lp"]["selected_expanded_lower"]
            require(upper is None or lower is None or from_rat(lower) <= from_rat(upper), "Exact lower/upper contradiction")
        intervals = []
        for variant in ("native_penalized", "hard_service"):
            ref = results["identity__" + variant]
            for target in ("reverse_4_19", "rotate_left1_4_19"):
                res = results[target + "__" + variant]
                li, ui = ref["lp"]["selected_expanded_lower"], ref["mip"]["accepted_expanded_upper"]
                lt, ut = res["lp"]["selected_expanded_lower"], res["mip"]["accepted_expanded_upper"]
                row = {"variant": variant, "target": target, "reference_lower": li, "reference_upper": ui,
                       "target_lower": lt, "target_upper": ut, "signed_optimum_difference_interval": None,
                       "status": "UNKNOWN_MISSING_FINITE_BRACKET", "tau": rat(F(TAU))}
                if all(x is not None for x in (li, ui, lt, ut)):
                    low, high = from_rat(lt) - from_rat(ui), from_rat(ut) - from_rat(li)
                    require(low <= high, "Inverted exact optimum interval")
                    row.update(status="EXACT_FINITE_SIGNED_COST_INTERVAL", signed_optimum_difference_interval={"lower": rat(low), "upper": rat(high)})
                intervals.append(row)
        write_new(root / "cost_intervals.json", {"scope": "Both optima are in the same declared expanded encoded service variant",
                  "targets_per_variant": 2, "rows": intervals, "no_energy_or_HOD_inference": True})
        for rel, b in snapshots.items():
            require(local_file(root, rel).read_bytes() == b, "Frozen input changed during run")
        require(sha((root / "run_manifest.json").read_bytes()) == expected_manifest, "Run manifest changed")
        elapsed = time.perf_counter() - phase_start
        completed_calls = sum(r[k]["solver_calls"] for r in results.values() for k in ("mip", "lp"))
        require(completed_calls == call_ledger["attempted_solver_calls"] == call_ledger["returned_solver_calls"],
                "Completed result counts differ from caller-owned attempted-call ledger")
        completion = {"status": "PRODUCER_COMPLETE_PENDING_INDEPENDENT_REVIEW", "started_utc": started_utc,
                      "ended_utc": utc(), "elapsed_seconds_including_validation": elapsed,
                      "phase_overrun_seconds": max(0, elapsed - PHASE_SECONDS),
                      "solver_calls": completed_calls, "call_ledger": call_ledger,
                      "planned_calls": 12, "results": results, "frozen_inputs_unchanged": True}
        write_new(root / "completion.json", completion)
        output_files = [{"path": p.relative_to(root).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p.read_bytes())}
                        for p in sorted(root.rglob("*")) if p.is_file() and p.relative_to(root).as_posix() not in snapshots
                        and p.name not in ("run_manifest.json", "output_manifest.json")]
        write_new(root / "output_manifest.json", {"files": output_files})
        return {"status": completion["status"], "solver_calls": completion["solver_calls"], "interval_rows": len(intervals)}
    except BaseException as exc:
        write_new(root / "execution_failure.json", {"utc": utc(), "exception_type": type(exc).__name__,
                  "message": str(exc), "partial_outputs_preserved": True, "automatic_retry": False,
                  "call_ledger": call_ledger})
        raise


def self_test():
    def simple(a, lo, hi):
        return {"columns": [{"objective": 1.0, "lower": 0.0, "upper": 1.0}],
                "rows": [{"coefficients": [[0, a]], "lower": lo, "upper": hi}]}
    m = simple(1.0, 0.2, None)
    checks = []
    for label, model, dual, expected in (
            ("positive_lower_row", m, [1.0], F(0.2)),
            ("negative_upper_row", simple(-1.0, None, -0.2), [-1.0], F(0.2)),
            ("imperfect_stationarity_small_dual", m, [0.5], F(0.5) * F(0.2)),
            ("imperfect_stationarity_large_dual", m, [2.0], 2 * F(0.2) - 1),
            ("infinite_selected_bound_projection", simple(1.0, None, 1.0), [1.0], Fraction(0)),
            ("zero_dual", m, [0.0], Fraction(0))):
        proof = exact_lower_bound(model, dual)
        require(from_rat(proof["nominal_lower_bound"]) == expected, "Synthetic bound test failed: " + label)
        require(from_rat(proof["expanded_lower_bound"]) == expected - F(TAU) * from_rat(proof["expansion_slope"]),
                "Expansion arithmetic mismatch")
        checks.append({"name": label, "status": "PASS"})
    zero = exact_lower_bound(m, [0.0])
    require(from_rat(zero["expanded_lower_bound"]) == -F(TAU), "Expanded zero-dual floor must not be clamped")
    return {"status": "PASS_SYNTHETIC_EXACT_BOUND_TESTS_ONLY", "checks": checks, "solver_calls": 0,
            "scientific_models_built": 0, "scientific_inputs_read": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    test = sub.add_parser("self-test")
    test.add_argument("--report", required=True)
    prep = sub.add_parser("prepare-run")
    for name in ("input-root", "expected-input-manifest", "adapter", "solver-protocol", "output"):
        prep.add_argument("--" + name, required=True)
    run = sub.add_parser("run-prepared")
    for name in ("root", "expected-manifest", "review-report", "expected-review-sha256"):
        run.add_argument("--" + name, required=True)
    args = parser.parse_args()
    if args.command == "self-test":
        result = self_test()
        write_new(args.report, result)
    elif args.command == "prepare-run":
        result = prepare_run(args.input_root, args.expected_input_manifest, args.adapter, args.solver_protocol, args.output)
    else:
        result = run_prepared(args.root, args.expected_manifest, args.review_report, args.expected_review_sha256)
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
