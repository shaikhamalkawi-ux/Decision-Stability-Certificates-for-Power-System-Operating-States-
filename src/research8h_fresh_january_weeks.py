"""Separately gated reference and clock-preserving target stages for two new weeks."""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import shutil
import sys
import time

sys.dont_write_bytecode = True
import highspy
import numpy as np
import pandas as pd
from scipy.sparse import load_npz

import research8h_seasonal_cap_continuation as cap_tools
from research8h_seasonal_reference import assemble_reference, physical_check
from research8h_seasonal_transfer import archive_model, cap_record, energy, transitions
from research8h_seasonal_uncapped import check_manifest, exact_point_check, rational_record
from research8h_service_network_mip import build, unpack
from research8h_u_only_continuation import audit_projection
from temporal_lp_certificate import check_vector, digest, save
from v8r1_rts_seasonal import load_model

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results/research8h/fresh_january_weeks"
PROTOCOL = ROOT / "docs/research8h/FRESH_JANUARY_WEEKS_PROTOCOL.md"
SCHEDULE = {2: (168, [26093210, 26093211], 26100210), 3: (336, [26093220, 26093221], 26100220)}
CUTOFF = datetime(2026, 9, 27, 4, tzinfo=timezone.utc)
TOL = 1e-5


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def arrays(path):
    with np.load(path) as data:
        return {key: data[key].copy() for key in data.files}


def bit_equal(a, b):
    a, b = np.asarray(a), np.asarray(b)
    return a.shape == b.shape and a.dtype == b.dtype and a.tobytes() == b.tobytes()


def local_sources(entry):
    pending, found = [entry.resolve()], set()
    while pending:
        path = pending.pop()
        if path in found:
            continue
        found.add(path)
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8-sig"))):
            names = [x.name.split(".")[0] for x in node.names] if isinstance(node, ast.Import) else (
                [node.module.split(".")[0]] if isinstance(node, ast.ImportFrom) and node.module else [])
            for name in names:
                candidate = ROOT / "src" / (name + ".py")
                if candidate.is_file():
                    pending.append(candidate.resolve())
    return sorted(found)


def roster(model):
    names = model.dec["GEN UID"].tolist()
    thermal = model.dec.iloc[model.urows]
    fossil = [int(j) for j in model.urows if model.dec.iloc[j]["Fuel"] in {"Coal", "Oil", "NG"}]
    assert (len(names), len(thermal), len(model.busids), len(model.branches)) == (41, 24, 24, 38)
    assert len(fossil) == 23 and [names[j] for j in model.urows if j not in fossil] == ["121_NUCLEAR_1"]
    margins = thermal["Ramp Rate MW/Min"].to_numpy(float)*60-thermal["PMax MW"].to_numpy(float)+thermal["PMin MW"].to_numpy(float)
    assert np.all(margins >= 0)
    return names, thermal["GEN UID"].tolist(), fossil, margins


def native_rows(model, start):
    assert start in [168, 336]
    rows = np.arange(start, start+168)
    expected = pd.date_range("2020-01-01", periods=504, freq="h")[rows]
    fields = ["Year", "Month", "Day", "Period"]
    calendar = np.array([[t.year, t.month, t.day, t.hour+1] for t in expected], dtype=int)
    for table in [model.load_ts, model.pv_ts, model.wind_ts, model.hydro_ts, model.rtpv_ts]:
        assert np.array_equal(table.loc[rows, fields].to_numpy(int), calendar)
    lo, hi, net, nodal = [], [], [], []
    for row in rows:
        lower, upper = model.avail_at(int(row))
        load = float(model.load_ts.loc[int(row), str(model.AREA)])
        rtpv = model.rtpv_at(int(row))
        lo.append(lower); hi.append(upper)
        net.append(load-rtpv.sum())
        nodal.append(model.prop*load-rtpv)
    native = {"pmin": np.asarray(lo), "pmax": np.asarray(hi), "net": np.asarray(net),
              "rows": rows, "source_hour": np.arange(168)}
    nodal = np.asarray(nodal)
    assert all(np.isfinite(a).all() for a in [native["pmin"], native["pmax"], native["net"], nodal])
    thermal = model.dec.iloc[model.urows]
    assert np.array_equal(native["pmin"][:, model.urows], np.broadcast_to(thermal["PMin MW"].to_numpy(float), (168, 24)))
    assert np.array_equal(native["pmax"][:, model.urows], np.broadcast_to(thermal["PMax MW"].to_numpy(float), (168, 24)))
    hydro = model.dec.Category.eq("Hydro").to_numpy()
    assert np.array_equal(native["pmin"][:, hydro], native["pmax"][:, hydro])
    residual = float(np.max(np.abs(native["net"]-nodal.sum(1))))
    assert residual <= 1e-9
    table = pd.DataFrame({"local_hour_0based": np.arange(168), "native_row_0based": rows, "timestamp": expected.astype(str)})
    return native, nodal, table, {"five_calendars_match": True, "consecutive_hours": 168,
        "start_native_row": start, "end_native_row_inclusive": start+167,
        "net_vs_nodal_summation_residual_MW": residual, "optimization_calls": 0}


def paths_for(source_v3):
    return [PROTOCOL, ROOT / "docs/research8h/FRESH_JANUARY_WEEKS_DESIGN_PROPOSAL.md",
            *local_sources(Path(__file__)), source_v3 / "code/dscgrid_model.py",
            *sorted((source_v3 / "raw").rglob("*.csv"))]


def freeze(directory, paths, source_v3, stage, cases, extra=None):
    paths = list(dict.fromkeys([*paths, *sorted(p for p in directory.rglob("*") if p.is_file())]))
    pd.DataFrame([{"path": str(p), "sha256": digest(p), "bytes": p.stat().st_size} for p in paths]).to_csv(directory / "input_manifest.csv", index=False)
    record = {"utc": datetime.now(timezone.utc).isoformat(), "stage": stage, "cases": cases,
        "source_sha256": digest(Path(__file__)), "protocol_sha256": digest(PROTOCOL),
        "manifest_sha256": digest(directory / "input_manifest.csv"), "source_v3": str(source_v3.resolve()),
        "cutoff_utc": CUTOFF.isoformat(), "optimizer_calls_started": 0, "requires_independent_PASS_and_root_GO": True}
    record.update(extra or {})
    save(directory / "prepared_freeze.json", record)
    print(json.dumps({"event": "PREPARED_NO_SOLVES", **record}), flush=True)


def execution_start(directory, source_v3, stage):
    frozen = read(directory / "prepared_freeze.json")
    assert frozen["stage"] == stage and frozen["source_v3"] == str(source_v3.resolve())
    assert digest(Path(__file__)) == frozen["source_sha256"] and digest(PROTOCOL) == frozen["protocol_sha256"]
    assert digest(directory / "input_manifest.csv") == frozen["manifest_sha256"]
    before = check_manifest(directory / "input_manifest.csv")
    with (directory / "execution_started.json").open("x", encoding="utf-8") as stream:
        json.dump({"utc": datetime.now(timezone.utc).isoformat(), "stage": stage, "pre_execution_hash_check": before}, stream, indent=2)
    return frozen


def guard(started, allocation, needed):
    utc_remaining = (CUTOFF-datetime.now(timezone.utc)).total_seconds()
    if utc_remaining < needed:
        return "NOT_RUN_CUTOFF"
    if allocation-(time.perf_counter()-started) < needed:
        return "NOT_RUN_BUDGET"
    return None


def selftest():
    """Synthetic guard and signed-zero regression checks; no native models."""
    global CUTOFF
    class Fake:
        calls = 0
        label = "delegated"
        def run(self):
            self.calls += 1
            return "ok"
    original = CUTOFF
    tests = []
    try:
        CUTOFF = datetime.now(timezone.utc)+timedelta(days=1)
        fake = Fake(); proxy = GuardedSolver(fake, time.perf_counter(), 35)
        assert proxy.label == "delegated" and proxy.run() == "ok" and fake.calls == 1
        tests.append("delegation_when_both_budgets_suffice")
        fake = Fake()
        try:
            GuardedSolver(fake, time.perf_counter()-2200, 35).run()
            raise AssertionError("phase guard did not stop")
        except CallNotStarted as error:
            assert str(error) == "NOT_RUN_BUDGET" and fake.calls == 0
        tests.append("phase_remaining_guard")
        for offset, name in [(10, "positive_UTC_remaining_below_guard"), (-1, "expired_UTC_cutoff")]:
            CUTOFF = datetime.now(timezone.utc)+timedelta(seconds=offset)
            fake = Fake()
            try:
                GuardedSolver(fake, time.perf_counter(), 35).run()
                raise AssertionError("UTC guard did not stop")
            except CallNotStarted as error:
                assert str(error) == "NOT_RUN_CUTOFF" and fake.calls == 0
            tests.append(name)
    finally:
        CUTOFF = original
    commitment = np.zeros((168, 24)); commitment[48:72, 0] = -0.0
    order, draw = generate_order(26100210, commitment, True)
    assert np.array_equal(commitment[order], commitment) and not bit_equal(commitment[order], commitment)
    assert bit_equal(commitment[order][np.argsort(order)], commitment)
    assert draw["U_semantically_unchanged"] and not draw["U_bitwise_unchanged"]
    tests.append("signed_zero_control_semantics_and_bitwise_roundtrip")
    return {"pass": True, "tests": tests, "optimizer_calls": 0, "native_models_generated": 0}


def prepare_references(source_v3):
    directory = OUTPUT / "references"
    directory.mkdir(parents=True, exist_ok=False)
    save(directory / "guard_and_control_selftest.json", selftest())
    model = load_model(source_v3)
    names, thermal, fossil, margins = roster(model)
    save(directory / "roster.json", {"unit_names": names, "thermal_names": thermal,
        "fossil_names": [names[j] for j in fossil], "bus_ids": model.busids,
        "branches": len(model.branches), "minimum_ramp_margin_MW": float(margins.min())})
    for week, (start, seeds, control) in SCHEDULE.items():
        native, nodal, hours, audit = native_rows(model, start)
        a, b, integer, objective, meta, labels, assembled_nodal = assemble_reference(
            model, native["pmin"], native["pmax"], native["net"], native["rows"], fossil)
        assert bit_equal(nodal, assembled_nodal)
        assert a.shape == (34680, 23016) and not any(x["family"] in ["target_mean", "fossil_energy_cap"] for x in labels)
        expected = np.zeros(23016); expected[[t*41+j for t in range(168) for j in fossil]] = 1.
        assert np.array_equal(objective, expected)
        data = (a, b, integer, meta, labels, assembled_nodal)
        case = directory / f"week_{week}"
        archive_model(case, data, native)
        np.savez_compressed(case / "objective.npz", objective=objective)
        projected, projection = audit_projection(a, b, meta, pd.DataFrame(labels), integer)
        np.savez_compressed(case / "projected_integrality.npz", integrality=projected)
        save(case / "projection_audit.json", projection)
        save(case / "native_adapter_audit.json", audit)
        hours.to_csv(case / "source_hours.csv", index=False)
    freeze(directory, paths_for(source_v3), source_v3, "references", ["week_2", "week_3"],
           {"seconds_per_case": 600, "phase_seconds": 1800, "start_guard_seconds": 605,
            "objective": "23 fossil-unit MWh", "no_warm_start_or_retry": True})


def finite(v):
    v = float(v)
    return v if np.isfinite(v) else None


def solve_reference(model, directory, phase_started):
    matrix, bounds, original_integer, meta, labels, native = cap_tools.load_case(directory)
    projected = arrays(directory / "projected_integrality.npz")["integrality"]
    objective = arrays(directory / "objective.npz")["objective"]
    lp = highspy.HighsLp(); lp.num_row_, lp.num_col_ = matrix.shape
    lp.col_cost_, lp.col_lower_, lp.col_upper_ = objective, bounds["column_lower"], bounds["column_upper"]
    lp.row_lower_, lp.row_upper_ = bounds["row_lower"], bounds["row_upper"]
    lp.integrality_ = [highspy.HighsVarType.kInteger if v else highspy.HighsVarType.kContinuous for v in projected]
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.num_row_, lp.a_matrix_.num_col_ = matrix.shape
    lp.a_matrix_.start_, lp.a_matrix_.index_, lp.a_matrix_.value_ = matrix.indptr, matrix.indices, matrix.data
    solver = highspy.Highs()
    options = {"time_limit": 600., "threads": 1, "random_seed": 0, "presolve": "on", "mip_rel_gap": 1e-8,
               "log_to_console": False, "log_file": str(directory / "solver.log")}
    for key, value in options.items():
        assert solver.setOptionValue(key, value) == highspy.HighsStatus.kOk
    assert solver.passModel(lp) == highspy.HighsStatus.kOk
    reason = guard(phase_started, 1800, 605)
    if reason:
        return {"verdict": "UNKNOWN_NO_REFERENCE", "route": reason, "optimization_calls": 0,
                "solver_created_but_not_run": True, "solver_options": options}
    started = time.perf_counter(); run_status = solver.run(); elapsed = time.perf_counter()-started
    status, solution, info = solver.getModelStatus(), solver.getSolution(), solver.getInfo()
    result = {"verdict": "UNKNOWN_NO_REFERENCE", "model_status": solver.modelStatusToString(status),
        "run_status": str(run_status), "elapsed_s": elapsed, "optimization_calls": 1,
        "solver_version": solver.version(), "solver_options": options, "solution_value_valid": bool(solution.value_valid),
        "solver_objective_MWh": finite(info.objective_function_value), "numerical_lower_bound_MWh": finite(info.mip_dual_bound),
        "mip_relative_gap": finite(info.mip_gap), "mip_node_count": int(info.mip_node_count), "exact_optimality_claim": False}
    if solution.value_valid:
        raw = np.asarray(solution.col_value); np.savez_compressed(directory / "raw_vector.npz", vector=raw)
        result["raw_matrix_check"] = check_vector(matrix, bounds, raw)
        p, u, y, z, theta = unpack(raw, 168, 41, 24, 24)
        eligible = bool(np.isfinite(raw).all() and np.all(np.abs(u-np.rint(u)) <= TOL)
                        and np.all((np.rint(u) >= 0) & (np.rint(u) <= 1)))
        result["eligible_for_recovery"] = eligible
        if eligible:
            u = np.rint(u); y, z = transitions(u)
            point = np.concatenate([v.ravel() for v in [p, u, y, z, theta]])
            np.savez_compressed(directory / "recovered_vector.npz", vector=point)
            result["recovered_matrix_check"] = check_vector(matrix, bounds, point)
            fossil = [meta["unit_names"].index(uid) for uid in meta["fossil_units"]]
            physical = physical_check(model, p, u, y, z, theta, native["pmin"], native["pmax"], native["net"], native["rows"], native["nodal"], fossil)
            exact = exact_point_check(matrix, bounds, point, original_integer)
            save(directory / "native_no_cap_check.json", physical); save(directory / "exact_point_check.json", exact)
            result.update(native_no_cap_pass=physical["pass"], exact_expanded_pass=exact["expanded_pass"],
                exact_strict_pass=exact["strict_pass"], fossil_energy=rational_record(energy(p, fossil)))
            if result["raw_matrix_check"]["pass"] and result["recovered_matrix_check"]["pass"] and physical["pass"] and exact["expanded_pass"]:
                result["verdict"] = "VERIFIED_REFERENCE_EXPANDED_MODEL"
                for name, values, columns in [("dispatch", p, meta["unit_names"]), ("commitment", u, meta["thermal_unit_names"]),
                        ("startup", y, meta["thermal_unit_names"]), ("shutdown", z, meta["thermal_unit_names"]), ("angles", theta, meta["bus_ids"])]:
                    pd.DataFrame(values, columns=columns).to_csv(directory / f"{name}.csv", index=False)
    if status == highspy.HighsModelStatus.kInfeasible and result["verdict"] == "UNKNOWN_NO_REFERENCE":
        result["numerical_solver_infeasible_not_exact_proof"] = True
    save(directory / "result.json", result)
    return result


def run_references(source_v3):
    started = time.perf_counter(); directory = OUTPUT / "references"
    frozen = execution_start(directory, source_v3, "references")
    assert frozen["cases"] == ["week_2", "week_3"]
    model = load_model(source_v3); results = []
    for week in SCHEDULE:
        reason = guard(started, 1800, 605)
        case = directory / f"week_{week}"
        result = {"verdict": "UNKNOWN_NO_REFERENCE", "route": reason, "optimization_calls": 0} if reason else solve_reference(model, case, started)
        result["week"] = week
        save(case / "result.json", result); results.append(result); save(directory / "summary.json", results)
        print(json.dumps({"stage": "REFERENCE", "week": week, "verdict": result["verdict"], "elapsed_s": result.get("elapsed_s")}), flush=True)
    save(directory / "final_manifest_check.json", check_manifest(directory / "input_manifest.csv"))
    elapsed = time.perf_counter()-started
    save(directory / "completion.json", {"weeks_recorded": 2, "optimization_calls": sum(r["optimization_calls"] for r in results),
        "actual_solver_seconds": sum(r.get("elapsed_s", 0) for r in results), "phase_elapsed_s": elapsed,
        "phase_seconds": 1800, "phase_overrun_s": max(0., elapsed-1800), "target_execution_authorized": False})


def generate_order(seed, commitment, control):
    assert commitment.shape == (168, 24) and np.isfinite(commitment).all()
    assert np.all((commitment == 0) | (commitment == 1))
    rng = np.random.Generator(np.random.PCG64(seed)); before = rng.bit_generator.state
    order = np.arange(168); groups = []
    if control:
        inventory = {}
        for t in range(48, 120):
            inventory.setdefault((t % 24, *[int(v) for v in commitment[t]]), []).append(t)
        items = [(key, np.asarray(inventory[key])) for key in sorted(inventory)]
    else:
        items = [((h,), np.asarray([48+h, 72+h, 96+h])) for h in range(24)]
    for key, positions in items:
        chosen = rng.permutation(positions); order[positions] = chosen
        groups.append({"key": list(key), "destination": positions.tolist(), "source": chosen.tolist()})
    assert np.array_equal(np.sort(order), np.arange(168)) and np.array_equal(order % 24, np.arange(168) % 24)
    assert np.array_equal(order[:48], np.arange(48)) and np.array_equal(order[120:], np.arange(120, 168))
    if control:
        # Exact binary semantics identify +0.0 and -0.0; payload roundtrips
        # below remain bitwise checked and no draw is replaced.
        assert np.array_equal(commitment[order], commitment)
    return order, {"seed": seed, "generator": "Generator(PCG64)", "numpy_version": np.__version__,
        "state_before": before, "state_after": rng.bit_generator.state, "groups": groups, "redraws": 0,
        "identity_draw_retained": bool(np.array_equal(order, np.arange(168))),
        "U_semantically_unchanged": bool(np.array_equal(commitment[order], commitment)),
        "U_bitwise_unchanged": bit_equal(commitment[order], commitment)}


def validate_cap(data, budget, fossil):
    a, b, integer, meta, labels, nodal = data
    assert a.shape == (34681, 23016) and meta["budget_MWh"] == budget
    assert meta["individual_mean_constraints"] == 0 and not any("mean" in r["family"] for r in labels)
    rows = [i for i, r in enumerate(labels) if r["family"] == "fossil_energy_cap"]
    assert len(rows) == 1
    row = a.getrow(rows[0]); expected = np.array([t*41+j for t in range(168) for j in fossil])
    assert np.array_equal(np.sort(row.indices), np.sort(expected)) and np.all(row.data == 1)
    assert np.isneginf(b["row_lower"][rows[0]]) and b["row_upper"][rows[0]] == budget
    assert np.array_equal(np.flatnonzero(integer), np.arange(6888, 18984))
    return rows[0]


def prepare_targets(source_v3):
    references = OUTPUT / "references"
    assert read(references / "completion.json")["weeks_recorded"] == 2
    assert read(references / "final_manifest_check.json")["pass"]
    ref_freeze = read(references / "prepared_freeze.json")
    assert digest(references / "input_manifest.csv") == ref_freeze["manifest_sha256"]
    results = {r["week"]: r for r in read(references / "summary.json")}
    assert set(results) == {2, 3}
    directory = OUTPUT / "targets"; directory.mkdir(exist_ok=False)
    save(directory / "reference_hash_check.json", check_manifest(references / "input_manifest.csv"))
    model = load_model(source_v3); names, thermal, fossil, margins = roster(model)
    paths = [*paths_for(source_v3), references / "input_manifest.csv", references / "prepared_freeze.json",
             references / "completion.json", references / "summary.json", references / "final_manifest_check.json"]
    scheduled, prepared = [], []
    for week, (start, seeds, control) in SCHEDULE.items():
        src = references / f"week_{week}"; record = results[week]
        eligible = record["verdict"] == "VERIFIED_REFERENCE_EXPANDED_MODEL"
        for seed in [*seeds, control]:
            scheduled.append({"week": week, "seed": seed, "kind": "ordinary" if seed in seeds else "control",
                              "status": "SCHEDULED" if eligible else "NO_REFERENCE"})
        paths.append(src / "result.json")
        if not eligible:
            continue
        a, b, integer, meta, labels, native = cap_tools.load_case(src)
        fresh, nodal, hours, adapter = native_rows(model, start)
        assert all(bit_equal(fresh[k], native[k]) for k in fresh) and bit_equal(nodal, native["nodal"])
        reference = arrays(src / "recovered_vector.npz")["vector"]
        p, u, y, z, theta = unpack(reference, 168, 41, 24, 24)
        assert exact_point_check(a, b, reference, integer)["expanded_pass"]
        assert physical_check(model, p, u, y, z, theta, native["pmin"], native["pmax"], native["net"], native["rows"], native["nodal"], fossil)["pass"]
        cap = cap_record(p, fossil); budget = float(cap["budget_MWh"])
        assert int(budget) == cap["budget_MWh"] and rational_record(energy(p, fossil)) == record["fossil_energy"]
        save(directory / f"week_{week}_cap.json", {**cap, "reference_result": record, "reference_vector_sha256": digest(src / "recovered_vector.npz")})
        for seed in [None, *seeds, control]:
            case = f"week_{week}_identity" if seed is None else f"seed_{seed}"
            order, draw = (np.arange(168), {"generator": "identity", "redraws": 0}) if seed is None else generate_order(seed, u, seed == control)
            inverse = np.argsort(order)
            for value in [native[k] for k in ["pmin", "pmax", "net", "rows", "nodal"]] + [p, u, theta]:
                assert bit_equal(value[order][inverse], value)
            n = {k: native[k][order] for k in ["pmin", "pmax", "net", "rows"]}; n["source_hour"] = order
            data = build(model, n["pmin"], n["pmax"], n["net"], n["rows"], budget)
            cap_row = validate_cap(data, budget, fossil)
            assert bit_equal(data[-1], native["nodal"][order])
            if seed is None:
                keep = np.arange(data[0].shape[0]) != cap_row
                assert (data[0][keep] != a).nnz == 0
                assert all(bit_equal(data[1][k][keep] if k.startswith("row_") else data[1][k], b[k]) for k in b)
                assert np.array_equal(data[2], integer)
            d = directory / case; archive_model(d, data, n)
            checks = cap_tools.constructive(model, d, data, n, p[order], u[order], theta[order], fossil, budget)
            assert energy(p[order], fossil) == energy(p, fossil)
            if seed is None or seed == control:
                assert checks["constructive_expanded_pass"]
            projected, projection = audit_projection(data[0], data[1], data[3], pd.DataFrame(data[4]), data[2])
            np.savez_compressed(d / "projected_integrality.npz", integrality=projected)
            save(d / "projection_audit.json", projection); save(d / "draw.json", draw)
            save(d / "preservation.json", {"bitwise_package_roundtrips": True, "native_nodal_exact": True,
                "hour_of_day_preserved": True, "edges_fixed": True, "fossil_energy_exactly_preserved": True,
                "changed_hours": int(np.count_nonzero(order != np.arange(168))),
                "source_continuity_breaks_after_destination_hours": np.flatnonzero(np.diff(order) != 1).tolist(),
                "literal_changed_adjacent_source_pairs_after_destination_hours": np.flatnonzero(
                    (order[:-1] != np.arange(167)) | (order[1:] != np.arange(1, 168))).tolist()})
            pd.DataFrame({"local_hour_0based": np.arange(168), "source_hour_0based": order,
                          "native_row_0based": n["rows"]}).to_csv(d / "permutation.csv", index=False)
            if seed in seeds:
                sub = d / "lp"; sub.mkdir()
                for filename in ["matrix.npz", "bounds.npz", "integrality.npz", "row_metadata.csv.gz"]:
                    shutil.copyfile(d / filename, sub / filename)
                prepared.append({"case": case, "week": week, "seed": seed, "budget_MWh": cap["budget_MWh"],
                                 "constructive_expanded_pass": checks["constructive_expanded_pass"]})
        paths.extend(sorted(p for p in src.iterdir() if p.is_file()))
    save(directory / "scheduled_cases.json", scheduled); save(directory / "prepared_cases.json", prepared)
    freeze(directory, paths, source_v3, "targets", [r["case"] for r in prepared],
        {"phase_seconds": 2100, "LP_seconds": 30, "MIP_seconds": 300, "LP_guard_seconds": 35,
         "MIP_guard_seconds": 305, "intended_ordinary_cases": 4, "intended_controls": 2})


class CallNotStarted(Exception):
    pass


class GuardedSolver:
    """Delegate a frozen backend, checking the cutoff immediately before run."""
    def __init__(self, solver, phase_started, needed):
        self.solver, self.phase_started, self.needed = solver, phase_started, needed

    def __getattr__(self, name):
        return getattr(self.solver, name)

    def run(self):
        reason = guard(self.phase_started, 2100, self.needed)
        if reason:
            raise CallNotStarted(reason)
        return self.solver.run()


def guarded_target(kind, model, directory, phase_started):
    """No frozen file edits; helper contexts are process-local and restored."""
    old_factory, old_context = cap_tools.solver_for, cap_tools.OUTPUT
    needed = 35 if kind == "lp" else 305

    def factory(*args, **kwargs):
        solver, options = old_factory(*args, **kwargs)
        return GuardedSolver(solver, phase_started, needed), options

    try:
        cap_tools.solver_for = factory
        cap_tools.OUTPUT = OUTPUT / "targets"
        result = cap_tools.solve_lp(directory) if kind == "lp" else cap_tools.solve_mip(model, directory)
        return result, None
    except CallNotStarted as error:
        reason = str(error)
        save(directory / kind / "result.json", {"verdict": "UNKNOWN", "route": reason,
             "optimization_calls": 0, "solver_created_but_not_run": True})
        return None, reason
    finally:
        cap_tools.solver_for, cap_tools.OUTPUT = old_factory, old_context


def run_targets(source_v3):
    started = time.perf_counter(); directory = OUTPUT / "targets"
    frozen = execution_start(directory, source_v3, "targets")
    prepared = read(directory / "prepared_cases.json")
    assert [r["case"] for r in prepared] == frozen["cases"]
    model = load_model(source_v3); outcomes, lp_results, mip_results = {}, {}, {}
    for item in prepared:
        case = item["case"]
        if item["constructive_expanded_pass"]:
            outcomes[case] = {**item, "verdict": "VERIFIED_FEASIBLE_EXPANDED_MODEL", "route": "CONSTRUCTIVE_REFERENCE", "LP_calls": 0, "MIP_calls": 0}
            continue
        reason = guard(started, 2100, 35)
        if reason:
            outcomes[case] = {**item, "verdict": "UNKNOWN", "route": reason, "LP_calls": 0, "MIP_calls": 0}
            continue
        result, reason = guarded_target("lp", model, directory / case, started)
        if reason:
            outcomes[case] = {**item, "verdict": "UNKNOWN", "route": reason, "LP_calls": 0, "MIP_calls": 0}
            continue
        lp_results[case] = result
        if result["verdict"] == "CERTIFIED_INFEASIBLE_EXPANDED_MODEL":
            outcomes[case] = {**item, "verdict": result["verdict"], "route": "EXACT_ROBUST_LP_RAY", "LP_calls": 1, "MIP_calls": 0}
        print(json.dumps({"stage": "LP", "case": case, "verdict": result["verdict"], "elapsed_s": result["elapsed_s"]}), flush=True)
    for item in prepared:
        case = item["case"]
        if case in outcomes:
            continue
        assert case in lp_results
        reason = guard(started, 2100, 305)
        if reason:
            outcome = {**item, "verdict": "UNKNOWN", "route": reason, "LP_calls": 1, "MIP_calls": 0}
        else:
            result, reason = guarded_target("mip", model, directory / case, started)
            if reason:
                outcome = {**item, "verdict": "UNKNOWN", "route": reason, "LP_calls": 1, "MIP_calls": 0}
            else:
                mip_results[case] = result
                exact_verdict = result["verdict"] if result["verdict"] == "VERIFIED_FEASIBLE_EXPANDED_MODEL" else "UNKNOWN"
                outcome = {**item, "verdict": exact_verdict, "diagnostic": result["verdict"], "route": "MIP", "LP_calls": 1,
                           "MIP_calls": 1, "MIP_elapsed_s": result["elapsed_s"]}
                print(json.dumps({"stage": "MIP", **outcome}), flush=True)
        outcomes[case] = outcome; save(directory / "outcomes_partial.json", list(outcomes.values()))
    ordered = list(outcomes.values())
    for item in read(directory / "scheduled_cases.json"):
        if item["kind"] == "ordinary" and item["status"] == "NO_REFERENCE":
            ordered.append({"case": f"seed_{item['seed']}", "week": item["week"], "seed": item["seed"],
                            "verdict": "NO_REFERENCE", "route": "NO_REFERENCE", "LP_calls": 0, "MIP_calls": 0})
    ordered.sort(key=lambda r: (r["week"], r["seed"]))
    assert len(ordered) == 4
    save(directory / "outcomes.json", ordered); pd.DataFrame(ordered).to_csv(directory / "outcomes.csv", index=False)
    save(directory / "final_manifest_check.json", check_manifest(directory / "input_manifest.csv"))
    elapsed = time.perf_counter()-started
    save(directory / "completion.json", {"intended_ordinary_cases": 4, "intended_controls": 2,
        "LP_calls": len(lp_results), "MIP_calls": len(mip_results), "actual_LP_seconds": sum(r["elapsed_s"] for r in lp_results.values()),
        "actual_MIP_seconds": sum(r["elapsed_s"] for r in mip_results.values()), "phase_elapsed_s": elapsed,
        "phase_seconds": 2100, "phase_overrun_s": max(0., elapsed-2100), "prior_results_and_gates_unchanged": True})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-v3", type=Path, required=True)
    modes = parser.add_mutually_exclusive_group(required=True)
    for name in ["prepare-references", "run-references", "prepare-targets", "run-targets"]:
        modes.add_argument("--"+name, action="store_true")
    args = parser.parse_args()
    for name, function in [("prepare_references", prepare_references), ("run_references", run_references),
                           ("prepare_targets", prepare_targets), ("run_targets", run_targets)]:
        if getattr(args, name):
            function(args.source_v3)
            break


if __name__ == "__main__":
    main()
