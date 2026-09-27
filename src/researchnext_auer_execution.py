"""Prospective authentic Auer-helper projection experiment; separately gated.

The adapter and author/TSAM source stay frozen. This harness controls only solver
options, captures its returned state, and compares the complete declared
no-storage preprocessing observation. No UC problem is solved.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata as metadata
import importlib.util
import itertools
import json
import math
from pathlib import Path
import sys
import time
from types import SimpleNamespace
import zipfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
PRE = ROOT / "results/research_next/auer_projection_preflight"
PROJECTION = PRE / "prepared"
OUT = ROOT / "results/research_next/auer_execution"
PROTOCOL = ROOT / "docs/research_next/AUER_EXECUTION_PROTOCOL.md"
ADAPTER = ROOT / "src/researchnext_auer_projection.py"
ADAPTER_SHA = "9d1f036568935d62ac665e22cf0f4440e39ea3bf02b4b42488a2c1b47ce980b4"
ADAPTER_PROTOCOL_SHA = "fdd6d1527586fde9def72ea0984c155cc3b2b9887f0b136e122d87c6e721ad81"
CASES_SHA = "b7ef56d295d919dbaad18696ad6260b58cc69740e9c16fe1f3ec60fd3be82570"
BINDINGS_SHA = "ca10b778d4135925fc5d25493b0b3333ff106f0d8f2bbaeda003c5ce8c3e3fcd"
WHEEL = ROOT / ".work/auer_projection_tsam_2_3_9/tsam-2.3.9-py3-none-any.whl"
WHEEL_SHA = "edcc4febb9e1dacc028bc819d710974ede8f563467c3d235a250f46416f93a1b"
SOLVER_OPTIONS = {"TimeLimit": 30, "Threads": 1, "Seed": 0, "MIPGap": 0.0}
PHASE_SECONDS = 900
CALL_GUARD_SECONDS = 35
FEATURES = ["Hydro", "Solar PV", "Wind", "demand"]
TABLES = {
    "demand": ("dPower_Demand", ["scenario", "rp", "k", "i", "value"]),
    "profiles": ("dPower_VRESProfiles", ["scenario", "rp", "k", "g", "value"]),
    "inflows": ("dPower_Inflows", ["scenario", "rp", "k", "g", "value"]),
    "weights_rp": ("dPower_WeightsRP", ["scenario", "rp", "pWeight_rp"]),
    "weights_k": ("dPower_WeightsK", ["scenario", "k", "pWeight_k"]),
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def save(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def no_links(path):
    for p in [Path(path).absolute(), *Path(path).absolute().parents]:
        if p.exists():
            require(not p.is_symlink() and not (getattr(p.lstat(), "st_file_attributes", 0) & 1024),
                    f"Link/reparse path unsupported: {p}")


def binding(path):
    p = Path(path).resolve()
    no_links(path)
    return {"path": str(p), "sha256": sha(p), "bytes": p.stat().st_size}


def check_bindings(rows):
    seen = set()
    for row in rows:
        key = str(Path(row["path"]).resolve()).casefold()
        require(key not in seen, "Duplicate binding")
        seen.add(key)
        require(binding(row["path"]) == row, f"Bound input changed: {row['path']}")


def load_adapter():
    require(sha(ADAPTER) == ADAPTER_SHA, "Adapter changed")
    spec = importlib.util.spec_from_file_location("auer_projection_frozen", ADAPTER)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def installed_inventory():
    return sorted([{"name": d.metadata["Name"], "version": d.version} for d in metadata.distributions()],
                  key=lambda x: x["name"].lower())


def dependency_closure():
    """Metadata and bytes only; no scientific library imported here."""
    require(sha(WHEEL) == WHEEL_SHA, "Official TSAM wheel changed")
    dist = metadata.distribution("tsam")
    require(dist.version == "2.3.9", "TSAM version mismatch")
    rows = []
    with zipfile.ZipFile(WHEEL) as z:
        for name in sorted(z.namelist()):
            if name.startswith("tsam/") and name.endswith(".py"):
                p = Path(dist.locate_file(name)).resolve()
                require(p.read_bytes() == z.read(name), f"Installed TSAM source differs from wheel: {name}")
                rows.append(binding(p))
    require(rows, "No TSAM source closure")
    return rows


def fixed_schedule(cases):
    result = []
    for week in (1, 2, 3):
        selected = [c for c in cases if c["week"] == week]
        require([c["role"] for c in selected] == ["identity", "target", "target", "positive_control"],
                "Unexpected fixed denominator/order")
        for occurrence, case in enumerate(selected + [selected[0]]):
            result.append({**case, "invocation": len(result) + 1,
                           "comparison_role": "identity_repeat" if occurrence == 4 else case["role"]})
    require(len(result) == 15, "Expected fifteen calls")
    return result


def prepare():
    require(not OUT.exists(), "Exclusive new output directory required")
    no_links(OUT)
    OUT.mkdir(parents=True)
    # Capture all source/protocol inputs before anything that reads study inputs.
    initial = [binding(__file__), binding(PROTOCOL), binding(ADAPTER),
               binding(ROOT / "docs/research_next/AUER_PROJECTION_PROTOCOL.md")]
    require(initial[2]["sha256"] == ADAPTER_SHA and initial[3]["sha256"] == ADAPTER_PROTOCOL_SHA,
            "Frozen projection source changed")
    require(sha(PROJECTION / "cases.json") == CASES_SHA and sha(PROJECTION / "input_bindings.json") == BINDINGS_SHA,
            "Projection preparation changed")
    adapter = load_adapter()
    adapter.author_closure(adapter.AUTHOR)
    require(read(PRE / "synthetic_license_probe.json")["usable_for_tiny_test"], "No usable synthetic Gurobi probe")
    require(read(PRE / "author_schema_fixtures.json")["status"] == "PASS", "Author schema fixture failure")
    env = read(PRE / "isolated_environment.json")
    require(installed_inventory() == env["installed_distributions"], "Environment changed after readiness probe")
    require(sys.executable == env["executable"], "Run with the isolated readiness interpreter")
    source_rows = dependency_closure()
    cases = read(PROJECTION / "cases.json")["cases"]
    invocations = fixed_schedule(cases)
    paths = [p for p in PROJECTION.iterdir() if p.is_file()]
    paths += [PRE / n for n in ("isolated_environment.json", "synthetic_license_probe.json",
                               "author_schema_fixtures.json", "probe_completion.json", "environment_probe.py")]
    paths += [WHEEL, adapter.AUTHOR / "AUTHOR_CLOSURE.json"]
    paths += [adapter.AUTHOR / name for name in adapter.AUTHOR_HASHES]
    raw = read(PROJECTION / "input_bindings.json")
    raw_rows = raw["files"] if isinstance(raw, dict) and "files" in raw else raw
    # The projection record is authoritative; reject unsupported schema instead of guessing.
    require(isinstance(raw_rows, list), "Unsupported projection binding schema")
    check_bindings(raw_rows)
    rows = initial + [binding(p) for p in paths] + source_rows + raw_rows
    unique = {}
    for row in rows:
        key = row["path"].casefold()
        require(key not in unique or unique[key] == row, "Conflicting binding")
        unique[key] = row
    rows = sorted(unique.values(), key=lambda x: x["path"].casefold())
    for case in cases:
        require(sha(PROJECTION / case["projection_file"]) == case["projection_sha256"], "Projection changed")
    common = None
    for case in cases:
        projected = read(PROJECTION / case["projection_file"])
        static = {k: projected[k] for k in ("vres", "native_static_units", "bus_ids", "semantics", "hours", "scenario")}
        require(common is None or static == common, "Claimed common static metadata differs")
        common = static
    save(OUT / "schedule.json", {"invocations": invocations})
    save(OUT / "input_manifest.json", {"files": rows})
    check_bindings(rows)
    save(OUT / "prepared_freeze.json", {"utc": utc(), "input_manifest_sha256": sha(OUT / "input_manifest.json"),
         "schedule_sha256": sha(OUT / "schedule.json"), "source_sha256": sha(__file__),
         "protocol_sha256": sha(PROTOCOL), "bindings": len(rows), "invocations": 15,
         "scientific_clustering_calls": 0, "uc_calls": 0, "solver_options": SOLVER_OPTIONS,
         "environment_match_to_readiness": True, "same_as_full_author_environment": False})


def number(value):
    value = float(value)
    require(math.isfinite(value), "Nonfinite observation")
    return (0.0 if value == 0 else value).hex()


def rows_for(frame, columns):
    records = frame.reset_index()[columns].to_dict("records")
    result = []
    for record in records:
        result.append({key: number(value) if key in {"value", "pWeight_rp", "pWeight_k"}
                       else str(value) for key, value in record.items()})
    return result


def canonical_observation(tables, matrices):
    """Exact binary64 equality, simultaneous RP relabeling; no source-day IDs."""
    rps = ["rp01", "rp02", "rp03"]
    serializations = []
    for permutation in itertools.permutations(range(3)):
        mapping = {rps[old]: f"r{new}" for new, old in enumerate(permutation)}
        result = {}
        for name, records in tables.items():
            transformed = [{key: mapping[value] if key == "rp" else value for key, value in row.items()}
                           for row in records]
            result[name] = sorted(transformed, key=lambda row: json.dumps(row, sort_keys=True))
        for name, matrix in matrices.items():
            result[name] = [[matrix[i][j] for j in permutation] for i in permutation]
        serializations.append(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return min(serializations)


def full_observation(result):
    tables = {key: rows_for(getattr(result["case"], field), columns)
              for key, (field, columns) in TABLES.items()}
    matrices = {name: [[number(v) for v in row] for row in result[name].to_numpy().tolist()]
                for name in ("N", "P_to", "P_from")}
    canonical = canonical_observation(tables, matrices)
    return {"tables": tables, "matrices": matrices,
            "canonical": canonical, "canonical_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
            "excluded_provenance_fields": ["source day index", "p", "rp_num", "k_num", "id", "dataSource", "dataPackage"],
            "hindex_scientific_use": "Excluded only for this no-storage preprocessing contract"}


def execute_case(adapter, utilities, case_type, case, directory, phase_start, call_state):
    import numpy as np
    import pyomo.environ as pyo
    import tsam.timeseriesaggregation as tsam_module
    import tsam.utils.k_medoids_exact as exact_module
    from pyomo.opt import TerminationCondition, SolverStatus
    require(PHASE_SECONDS - (time.perf_counter() - phase_start) >= CALL_GUARD_SECONDS, "Phase guard before case")
    projected = read(PROJECTION / case["projection_file"])
    cs = adapter.as_author_case(projected)
    raw_features = utilities._extract_scenario_data(cs, "s1", "maxInvestment")
    features = utilities._prepare_aggregated_data(raw_features, False)
    require(sorted(set(features.columns) - {"scenario", "rp", "k"}) == FEATURES, "Unexpected actual features")
    counts = raw_features.groupby(["k", "i"]).size()
    actual_multiplicities = {}
    for bus, expected in projected["projection_audit"]["author_demand_row_multiplicity_by_bus"].items():
        values = counts.xs(bus, level="i").tolist()
        require(len(values) == 168 and set(map(int, values)) == {expected}, "Actual feature multiplicity mismatch")
        actual_multiplicities[bus] = expected
    save(directory / "actual_features.json", {"columns": FEATURES, "hours": 168,
         "values_hex": [[number(x) for x in row] for row in features.sort_values("k")[FEATURES].to_numpy()],
         "demand_multiplicity_by_bus": actual_multiplicities, "raw_rows": len(raw_features)})
    capture = []
    original_class, original_opt = tsam_module.TimeSeriesAggregation, exact_module.opt

    def factory(*args, **kwargs):
        instance = original_class(*args, **kwargs)
        capture.append(instance)
        return instance

    class SolverProxy:
        def __init__(self, actual):
            self.actual = actual

        def solve(self, model, *args, **kwargs):
            require(not args and not kwargs and call_state["calls_started"] == 0, "Unexpected TSAM solve signature/retry")
            require(list(model.i) == list(range(7)) and list(model.j) == list(range(7)) and model.no_k == 3,
                    "Not the declared seven-day three-medoid model")
            variables = list(model.component_data_objects(pyo.Var))
            constraints = list(model.component_data_objects(pyo.Constraint, active=True))
            require(len(variables) == 49 and all(v.is_binary() for v in variables) and len(constraints) == 57,
                    "Unexpected k-medoids formulation size")
            distance = np.asarray(model.d)
            require(distance.shape == (7, 7) and np.isfinite(distance).all(), "Invalid distance matrix")
            save(directory / "solver_input.json", {"distances_hex": [[number(v) for v in row] for row in distance],
                 "binary_variables": 49, "constraints": 57, "options": SOLVER_OPTIONS,
                 "remaining_phase_seconds": PHASE_SECONDS - (time.perf_counter() - phase_start), "utc": utc()})
            self.actual.options.update(SOLVER_OPTIONS)
            # Recheck after I/O, directly before the sole actual call.
            require(PHASE_SECONDS - (time.perf_counter() - phase_start) >= CALL_GUARD_SECONDS,
                    "Phase guard immediately before solve")
            call_state["calls_started"] = 1
            call_state["start_utc"] = utc()
            started = time.perf_counter()
            try:
                response = self.actual.solve(model, tee=False)
            finally:
                call_state["actual_seconds"] = time.perf_counter() - started
            save(directory / "termination.json", {"status": str(response.solver.status),
                 "termination": str(response.solver.termination_condition), "call_state": dict(call_state)})
            require(response.solver.status == SolverStatus.ok and response.solver.termination_condition == TerminationCondition.optimal,
                    f"Solver did not return numerical optimal status: {response.solver.termination_condition}")
            z = [[float(pyo.value(model.z[i, j])) for j in model.j] for i in model.i]
            rounded = [[round(v) for v in row] for row in z]
            require(all(math.isfinite(v) and abs(v - round(v)) <= 1e-6 for row in z for v in row), "Nonbinary assignment")
            require(all(v in (0, 1) for row in rounded for v in row), "Rounded assignment outside binary domain")
            require(all(sum(rounded[i][j] for i in range(7)) == 1 for j in range(7)), "Invalid cluster assignment")
            require(sum(rounded[i][i] for i in range(7)) == 3 and
                    all(rounded[i][j] <= rounded[i][i] for i in range(7) for j in range(7)), "Invalid medoid choices")
            save(directory / "solver_result.json", {"status": str(response.solver.status),
                 "termination": str(response.solver.termination_condition), "assignment_hex": [[number(v) for v in row] for row in z],
                 "objective_hex": number(pyo.value(model.obj)), "call_state": dict(call_state),
                 "optimality_scope": "numerical solver status; no exact combinatorial optimality proof"})
            return response

    def solver_factory(name, *args, **kwargs):
        require(name == "gurobi" and not args and not kwargs, "Backend substitution rejected")
        return SolverProxy(original_opt.SolverFactory(name))

    try:
        tsam_module.TimeSeriesAggregation = factory
        exact_module.opt = SimpleNamespace(SolverFactory=solver_factory)
        result = adapter.author_representation(projected, utilities, case_type, scientific_execution_enabled=True)
        require(len(capture) == 1 and call_state["calls_started"] == 1, "Unexpected scientific call count")
        aggregation = capture[0]
        require(aggregation.normalizedPeriodlyProfiles.shape == (7, 96), "Unexpected normalized daily shape")
        save(directory / "clustering_details.json", {
             "normalized_daily_profiles_hex": [[number(v) for v in row] for row in aggregation.normalizedPeriodlyProfiles.to_numpy()],
             "medoid_source_day_indices": [int(x) for x in aggregation.clusterCenterIndices],
             "cluster_order": [int(x) for x in aggregation.clusterOrder],
             "weights": {str(k): int(v) for k, v in aggregation._clusterPeriodNoOccur.items()},
             "hindex_provenance": result["case"].dPower_Hindex.reset_index()[["p", "rp", "k"]].to_dict("records")})
        observation = full_observation(result)
        save(directory / "observation.json", observation)
        return {"status": "OBSERVATION_COMPUTED", "canonical_sha256": observation["canonical_sha256"],
                "calls_started": 1, "solver_actual_seconds": call_state["actual_seconds"]}
    finally:
        tsam_module.TimeSeriesAggregation, exact_module.opt = original_class, original_opt
        save(directory / "call_ledger.json", call_state)


def compare(outcomes, schedule):
    def equal(a, b):
        left = OUT / f"call_{a['invocation']:02d}_{a['case']}" / "observation.json"
        right = OUT / f"call_{b['invocation']:02d}_{b['case']}" / "observation.json"
        return read(left)["canonical"] == read(right)["canonical"]
    comparisons = []
    for week in (1, 2, 3):
        indices = [i for i, case in enumerate(schedule) if case["week"] == week]
        original, *others = indices
        repeat = indices[-1]
        stable = (outcomes[original]["status"] == outcomes[repeat]["status"] == "OBSERVATION_COMPUTED" and
                  equal(outcomes[original], outcomes[repeat]))
        for index in others:
            a, b = outcomes[original], outcomes[index]
            valid = stable and a["status"] == b["status"] == "OBSERVATION_COMPUTED"
            comparisons.append({"week": week, "case": schedule[index]["case"], "role": schedule[index]["comparison_role"],
                 "identity_repeat_stable": stable,
                 "outcome": ("EQUAL_COMPLETE_PROJECTED_OBSERVATION" if equal(a, b)
                             else "DISTINCT_COMPLETE_PROJECTED_OBSERVATION") if valid else "UNKNOWN",
                 "UC_feasibility_tested": False})
    return comparisons


def run_prepared():
    started = time.perf_counter()
    freeze = read(OUT / "prepared_freeze.json")
    require(freeze["source_sha256"] == sha(__file__) and freeze["protocol_sha256"] == sha(PROTOCOL), "Frozen runner changed")
    require(freeze["input_manifest_sha256"] == sha(OUT / "input_manifest.json") and
            freeze["schedule_sha256"] == sha(OUT / "schedule.json"), "Frozen files changed")
    bindings = read(OUT / "input_manifest.json")["files"]
    check_bindings(bindings)
    require(installed_inventory() == read(PRE / "isolated_environment.json")["installed_distributions"], "Environment changed")
    require(sys.executable == read(PRE / "isolated_environment.json")["executable"] and sys.flags.isolated,
            "Use the same isolated readiness interpreter with -I")
    adapter = load_adapter()
    dependency_closure()
    schedule = read(OUT / "schedule.json")["invocations"]
    require(schedule == fixed_schedule(read(PROJECTION / "cases.json")["cases"]), "Schedule changed")
    save(OUT / "execution_started.json", {"utc": utc(), "source_sha256": sha(__file__),
         "executable": sys.executable, "isolated": sys.flags.isolated, "phase_seconds": PHASE_SECONDS,
         "prepared_input_hash_check": "PASS", "scientific_calls_before_marker": 0})
    utilities, case_type = adapter.load_author(adapter.AUTHOR)
    outcomes = []
    for case in schedule:
        directory = OUT / f"call_{case['invocation']:02d}_{case['case']}"
        directory.mkdir()
        # Caller-owned state preserves attempted-call accounting even if a later
        # result/ledger write fails after the optimizer returned.
        call_state = {"calls_started": 0}
        try:
            result = execute_case(adapter, utilities, case_type, case, directory, started, call_state)
        except Exception as error:
            result = {"status": "UNKNOWN", "error_type": type(error).__name__,
                      "calls_started": call_state["calls_started"], "solver_actual_seconds": call_state.get("actual_seconds", 0),
                      "error_message_omitted_to_avoid_license_details": True}
        result.update({"invocation": case["invocation"], "case": case["case"], "role": case["comparison_role"]})
        save(directory / "result.json", result)
        outcomes.append(result)
    save(OUT / "outcomes.json", {"invocations": outcomes, "comparisons": compare(outcomes, schedule)})
    check_bindings(bindings)
    elapsed = time.perf_counter() - started
    save(OUT / "completion.json", {"utc": utc(), "status": "COMPLETE", "invocation_denominator": 15,
         "calls_started": sum(x["calls_started"] for x in outcomes), "uc_calls": 0,
         "solver_seconds": math.fsum(x.get("solver_actual_seconds", 0) for x in outcomes),
         "solver_soft_overruns": [{"invocation": x["invocation"], "seconds": x["solver_actual_seconds"]-30}
                                  for x in outcomes if x.get("solver_actual_seconds", 0) > 30],
         "phase_seconds": elapsed, "phase_guard_seconds": PHASE_SECONDS, "phase_overrun": max(0, elapsed-PHASE_SECONDS),
         "all_input_hashes_unchanged": True, "no_fallback_or_retry": True,
         "unknowns": sum(x["status"] == "UNKNOWN" for x in outcomes)})


def self_test():
    tables = {"demand": [{"rp": "rp01", "k": "k0001", "value": number(-0.0)},
                          {"rp": "rp02", "k": "k0001", "value": number(2)},
                          {"rp": "rp03", "k": "k0001", "value": number(4)}]}
    matrix = {"N": [[number(v) for v in row] for row in [[1,2,0],[0,1,1],[2,0,0]]]}
    baseline = canonical_observation(tables, matrix)
    permutation = [2,0,1]
    rename = {f"rp{old+1:02d}": f"rp{new+1:02d}" for new, old in enumerate(permutation)}
    relabeled = {key: [{**r, "rp": rename[r["rp"]]} for r in records] for key, records in tables.items()}
    shifted = {key: [[m[i][j] for j in permutation] for i in permutation] for key, m in matrix.items()}
    require(baseline == canonical_observation(relabeled, shifted), "RP isomorphism rejected")
    changed = json.loads(json.dumps(tables)); changed["demand"][0]["value"] = number(1e-300)
    require(baseline != canonical_observation(changed, matrix), "Tiny finite profile difference erased")
    require(number(-0.0) == number(0.0), "Signed zero policy")
    require(baseline != canonical_observation(relabeled, matrix), "Unmapped transition coordinates ignored")
    try:
        number(float("nan"))
    except ValueError:
        pass
    else:
        raise AssertionError("Nonfinite observation accepted")
    print(json.dumps({"status": "PASS", "invented_fixtures": 5, "scientific_reads": 0, "solver_calls": 0}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare-only", action="store_true")
    group.add_argument("--run-prepared", action="store_true")
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.prepare_only:
        prepare()
    elif args.run_prepared:
        run_prepared()
    else:
        self_test()
