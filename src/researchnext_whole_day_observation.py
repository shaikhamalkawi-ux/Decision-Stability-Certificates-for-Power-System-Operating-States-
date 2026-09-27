"""Prospective whole-day observation study: separate prepare/run gates.

Reuse all five old week-one native/model archives. Construct only reordered
native arrays/projections for weeks two/three, never a UC matrix or UC solve.
Actual Auer-helper calls reuse the unchanged reviewed execution function.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/research_next/whole_day_observation_preflight"
PREPARED = OUT / "prepared"
RUN = OUT / "run01"
PROTOCOL = ROOT / "docs/research_next/WHOLE_DAY_OBSERVATION_PROTOCOL.md"
BASE_SOURCE = ROOT / "src/researchnext_auer_execution.py"
BASE_SHA = "a18058186dde3dfe0dbd6717c27636e76ef59debbbcfbd36f7bb887c7a232d9c"
BASE_ROOT = ROOT / "results/research_next/auer_execution"
BASE_MANIFEST_SHA = "abd3c49c3f5c3ab41bff76afc9648c380717d8892a4aeeb9c5fd6ff68bb9398a"
OLD_DAYS = ROOT / "results/research8h/day_blocks"
OLD_DAYS_MANIFEST_SHA = "5f15b13ce9b15abb1ff6256a4e10fc568ab5384e01a324160b0e522b31c8927d"
IDENTITIES = (
    (1, ROOT / "results/research8h/hour_of_day/january_identity", "january_identity"),
    (2, ROOT / "results/research8h/fresh_january_weeks/targets/week_2_identity", "week_2_identity"),
    (3, ROOT / "results/research8h/fresh_january_weeks/targets/week_3_identity", "week_3_identity"),
)
ORDERS = list(itertools.permutations((1, 2, 3)))
NATIVE_KEYS = ("pmin", "pmax", "net", "rows", "source_hour", "nodal")
MODEL_PROVENANCE = ("matrix.npz", "bounds.npz", "integrality.npz", "row_metadata.csv.gz")
PHASE_SECONDS = 1200
RPS = ("rp01", "rp02", "rp03")


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
    with Path(path).open("x", encoding="utf-8") as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write("\n")


def load_base():
    require(sha(BASE_SOURCE) == BASE_SHA, "Frozen execution helper changed")
    spec = importlib.util.spec_from_file_location("whole_day_frozen_auer_execution", BASE_SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def hour_order(order):
    require(tuple(sorted(order)) == (1, 2, 3), "Not an interior day permutation")
    return list(range(48)) + [48 + 24*(d-1) + k for d in order for k in range(24)] + list(range(120, 168))


def old_index():
    manifest = OLD_DAYS / "input_manifest.csv"
    require(sha(manifest) == OLD_DAYS_MANIFEST_SHA, "Historical day-block manifest changed")
    with manifest.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    lookup = {}
    for row in rows:
        key = str(Path(row["path"]).resolve()).casefold()
        require(key not in lookup, "Duplicate historical day-block binding")
        lookup[key] = {"path": str(Path(row["path"]).resolve()), "sha256": row["sha256"], "bytes": int(row["bytes"])}
    return lookup


def native_arrays(path):
    import numpy as np
    with np.load(path, allow_pickle=False) as z:
        require(set(z.files) == set(NATIVE_KEYS), "Unexpected native archive members")
        arrays = {k: z[k].copy() for k in NATIVE_KEYS}
    for key, width in (("pmin", 41), ("pmax", 41), ("net", 1), ("nodal", 24)):
        x = arrays[key]
        require(x.dtype.str == "<f8" and x.shape == ((168,) if width == 1 else (168, width)), "Native schema mismatch")
        require(np.isfinite(x).all(), "Nonfinite native input")
    for key in ("rows", "source_hour"):
        require(arrays[key].shape == (168,) and arrays[key].dtype.kind in "iu", "Native source coordinate schema")
    require(np.all(arrays["pmin"] <= arrays["pmax"]), "Inverted source power bounds")
    return arrays


def package_rows(arrays):
    import numpy as np
    result = np.column_stack([arrays["pmin"], arrays["pmax"], arrays["net"], arrays["nodal"]])
    require(result.shape == (168, 107) and result.dtype.str == "<f8", "Full107-coordinate schema")
    return result


def exact_mapping(original, candidate, order):
    permutation = hour_order(order)
    for key in NATIVE_KEYS:
        expected = original[key][permutation]
        require(candidate[key].dtype == expected.dtype and candidate[key].shape == expected.shape
                and candidate[key].tobytes(order="C") == expected.tobytes(order="C"), "Byte mapping failure: " + key)
    before, after = package_rows(original), package_rows(candidate)
    a_days = [before[i:i+24].tobytes(order="C") for i in range(0, 168, 24)]
    b_days = [after[i:i+24].tobytes(order="C") for i in range(0, 168, 24)]
    require(sorted(a_days) == sorted(b_days), "Whole joint-day multiset changed")
    require(before[:48].tobytes() == after[:48].tobytes() and before[120:].tobytes() == after[120:].tobytes(),
            "Fixed48-hour boundaries changed")
    require(all(t % 24 == source % 24 for t, source in enumerate(permutation)), "Hour-of-day mismatch")
    return {"complete_107_coordinates_bitwise_mapped": True, "all_six_native_arrays_mapped": True,
            "whole_24h_joint_day_multiset_equal": True, "fixed_first_last_48h_equal": True,
            "hour_of_day_preserved": True, "source_hour_indices": permutation}


def fixed_schedule(cases):
    result = []
    for week in (1, 2, 3):
        selected = [c for c in cases if c["week"] == week]
        require([tuple(c["day_order"]) for c in selected] == ORDERS, "Whole-day order denominator changed")
        for index, case in enumerate(selected + [selected[0]]):
            result.append({**case, "invocation": len(result)+1,
                           "comparison_role": "identity_repeat" if index == 6 else ("identity" if index == 0 else "target")})
    require(len(result) == 21, "Expected21fixed invocations")
    return result


def prepare():
    import numpy as np
    base = load_base()
    base.no_links(PREPARED)
    require(not PREPARED.exists() and not RUN.exists(), "Exclusive fresh preparation required")
    PREPARED.mkdir(parents=True)
    initial = [base.binding(__file__), base.binding(PROTOCOL), base.binding(BASE_SOURCE),
               base.binding(BASE_ROOT / "input_manifest.json"), base.binding(OLD_DAYS / "input_manifest.csv")]
    require(initial[3]["sha256"] == BASE_MANIFEST_SHA and initial[4]["sha256"] == OLD_DAYS_MANIFEST_SHA,
            "Inherited manifests changed")
    save(PREPARED / "initial_guard.json", {"utc": utc(), "bindings": initial, "scientific_clustering_calls": 0})
    inherited = read(BASE_ROOT / "input_manifest.json")["files"]
    base.check_bindings(inherited)
    require(base.installed_inventory() == read(base.PRE / "isolated_environment.json")["installed_distributions"],
            "Environment differs from frozen readiness")
    require(sys.executable == read(base.PRE / "isolated_environment.json")["executable"] and sys.flags.isolated,
            "Use frozen isolated interpreter with -I")
    base.dependency_closure()
    adapter = base.load_adapter()
    adapter.author_closure(adapter.AUTHOR)
    old = old_index()
    original_index = {x["path"].casefold(): x for x in inherited}
    gen_path, _ = adapter.native_paths()
    gen = adapter.gen_records(gen_path)
    bindings = initial + inherited
    cases, generated, common = [], [], None
    projection_dir = PREPARED / "projections"
    projection_dir.mkdir()
    for week, identity_dir, original_projection in IDENTITIES:
        for name in ("native_inputs.npz", "model_metadata.json", "permutation.csv"):
            p = identity_dir / name
            require(str(p.resolve()).casefold() in original_index, "Identity input not bound by old projection")
            require(base.binding(p) == original_index[str(p.resolve()).casefold()], "Identity input changed")
        original = native_arrays(identity_dir / "native_inputs.npz")
        meta = read(identity_dir / "model_metadata.json")
        require((meta["hours"], meta["units"], meta["thermal_units"], len(meta["bus_ids"])) == (168,41,24,24),
                "Identity coordinate schema changed")
        for order in ORDERS:
            label = "".join(map(str, order))
            name = f"week_{week}_days_{label}"
            expected = {key: values[hour_order(order)].copy() for key, values in original.items()}
            historical_parent = None
            if order == (1,2,3):
                arrays = original
                native_path = identity_dir / "native_inputs.npz"
                provenance_kind = "existing_identity_native_input"
            elif week == 1:
                source_dir = OLD_DAYS / f"days_{label}"
                for filename in ("native_inputs.npz", "model_metadata.json", "permutation.csv", *MODEL_PROVENANCE):
                    p = source_dir / filename
                    key = str(p.resolve()).casefold()
                    require(key in old and base.binding(p) == old[key], "Historical day model/input binding mismatch")
                    bindings.append(old[key])
                arrays = native_arrays(source_dir / "native_inputs.npz")
                inherited_meta = read(source_dir / "model_metadata.json")
                require(all(inherited_meta[k] == meta[k] for k in ("unit_names", "bus_ids", "offsets", "hours", "units")),
                        "Historical day coordinate identity differs")
                with (source_dir / "permutation.csv").open(encoding="utf-8-sig", newline="") as f:
                    recorded = list(csv.DictReader(f))
                require(len(recorded) == 168 and [int(x["new_hour_0based"]) for x in recorded] == list(range(168))
                        and [int(x["source_hour_0based"]) for x in recorded] == hour_order(order), "Old day order differs")
                require([int(x["source_native_row"]) for x in recorded] == arrays["rows"].tolist(), "Native source row differs")
                native_path = source_dir / "native_inputs.npz"
                historical_parent = str(source_dir)
                provenance_kind = "existing_week1_day_archive_reused_no_native_or_model_rebuild"
            else:
                arrays = expected
                directory = PREPARED / "new_native_inputs" / name
                directory.mkdir(parents=True)
                native_path = directory / "native_inputs.npz"
                np.savez_compressed(native_path, **arrays)
                # Reload to prove the saved native-only copy, with no model assembler.
                arrays = native_arrays(native_path)
                generated.append(base.binding(native_path))
                provenance_kind = "new_week2_or_3_native_permutation_only_no_UC_model"
            mapping = exact_mapping(original, arrays, order)
            projected = adapter.project_arrays(meta, gen, {k: arrays[k].tolist() for k in ("pmin", "pmax", "net", "nodal")})
            if order == (1,2,3):
                require(projected == read(base.PROJECTION / (original_projection + ".json")), "Original projection changed")
            static = {k: projected[k] for k in ("vres", "native_static_units", "bus_ids", "semantics", "hours", "scenario")}
            require(common is None or static == common, "Common static projection metadata differs")
            common = static
            path = projection_dir / (name + ".json")
            save(path, projected)
            generated.append(base.binding(path))
            map_path = PREPARED / (name + "_mapping.json")
            save(map_path, {"week": week, "day_order": list(order), "native_input_path": str(native_path),
                           "provenance_kind": provenance_kind, "historical_model_parent": historical_parent, **mapping})
            generated.append(base.binding(map_path))
            cases.append({"week": week, "case": name, "day_order": list(order),
                          "role": "identity" if order == (1,2,3) else "target",
                          "projection_file": path.name, "projection_sha256": sha(path),
                          "native_input_path": str(native_path), "provenance_kind": provenance_kind})
    save(PREPARED / "cases.json", {"cases": cases})
    schedule = fixed_schedule(cases)
    save(PREPARED / "schedule.json", {"invocations": schedule})
    unique = {}
    for row in bindings + generated:
        key = row["path"].casefold()
        require(key not in unique or unique[key] == row, "Conflicting input binding")
        unique[key] = row
    final = sorted(unique.values(), key=lambda x: x["path"].casefold())
    save(PREPARED / "input_manifest.json", {"files": final})
    base.check_bindings(final)
    save(PREPARED / "prepared_freeze.json", {"utc": utc(), "source_sha256": sha(__file__), "protocol_sha256": sha(PROTOCOL),
         "base_helper_sha256": BASE_SHA, "manifest_sha256": sha(PREPARED / "input_manifest.json"),
         "cases_sha256": sha(PREPARED / "cases.json"), "schedule_sha256": sha(PREPARED / "schedule.json"),
         "bindings": len(final), "unique_cases": 18, "targets": 15, "invocations": 21,
         "week1_old_native_archives_reused": 5, "new_native_permutations_week2_3": 10,
         "new_UC_model_builds": 0, "clustering_calls": 0, "optimizer_calls": 0,
         "all_initial_and_generated_hashes_pass": True})


def normalized_rows(rows, mapping=None):
    result = [{key: mapping[value] if mapping is not None and key == "rp" else value for key, value in row.items()}
              for row in rows]
    return sorted(result, key=lambda x: json.dumps(x, sort_keys=True, separators=(",", ":")))


def compatible_maps(original, target, original_hindex, target_hindex):
    """All relative target->original label maps; secondary uses only these maps."""
    require(set(original["tables"]) == set(target["tables"]) and set(original["matrices"]) == set(target["matrices"]),
            "Observation schema differs")
    primary, joint = [], []
    for permutation in itertools.permutations(range(3)):
        mapping = {RPS[i]: RPS[permutation[i]] for i in range(3)}
        if any(normalized_rows(original["tables"][name]) != normalized_rows(target["tables"][name], mapping)
               for name in original["tables"]):
            continue
        inverse = [permutation.index(i) for i in range(3)]
        if any(original["matrices"][name] != [[matrix[i][j] for j in inverse] for i in inverse]
               for name, matrix in target["matrices"].items()):
            continue
        primary.append(mapping)
        mapped_hindex = [{**row, "rp": mapping[row["rp"]]} for row in target_hindex]
        if mapped_hindex == original_hindex:
            joint.append(mapping)
    return {"primary_compatible_maps": primary, "primary_and_hindex_compatible_maps": joint,
            "primary_equal": bool(primary), "primary_and_hindex_equal": bool(joint)}


def compare_results(outcomes, schedule):
    def payload(index):
        c = schedule[index]
        directory = RUN / f"call_{c['invocation']:02d}_{c['case']}"
        observation = read(directory / "observation.json")
        hindex = read(directory / "clustering_details.json")["hindex_provenance"]
        require(len(hindex) == 168 and [row["p"] for row in hindex] == [f"h{t+1:04d}" for t in range(168)],
                "Hindex is not in original chronological coordinate order")
        return observation, hindex
    comparisons = []
    for week in (1,2,3):
        indices = [i for i, c in enumerate(schedule) if c["week"] == week]
        original_index, repeat = indices[0], indices[-1]
        stable = False
        if outcomes[original_index]["status"] == outcomes[repeat]["status"] == "OBSERVATION_COMPUTED":
            original, original_hindex = payload(original_index)
            repeated, repeated_hindex = payload(repeat)
            stable = compatible_maps(original, repeated, original_hindex, repeated_hindex)["primary_and_hindex_equal"]
        for index in indices[1:]:
            c = schedule[index]
            result = {"week": week, "case": c["case"], "day_order": c["day_order"], "role": c["comparison_role"],
                      "joint_identity_repeat_stable": stable, "primary_outcome": "UNKNOWN", "primary_plus_hindex_outcome": "UNKNOWN"}
            if stable and outcomes[index]["status"] == "OBSERVATION_COMPUTED":
                target, target_hindex = payload(index)
                matched = compatible_maps(original, target, original_hindex, target_hindex)
                result.update(matched)
                result["primary_outcome"] = "EQUAL" if matched["primary_equal"] else "DIFFERENT"
                result["primary_plus_hindex_outcome"] = "EQUAL" if matched["primary_and_hindex_equal"] else "DIFFERENT"
            comparisons.append(result)
    return comparisons


def run_prepared():
    phase = time.perf_counter()
    base = load_base()
    require(not RUN.exists(), "Exactly one run; retries require a new protocol")
    transport_bindings = [base.binding(PREPARED / name) for name in
                          ("prepared_freeze.json", "cases.json", "schedule.json", "input_manifest.json")]
    freeze = read(PREPARED / "prepared_freeze.json")
    require(freeze["source_sha256"] == sha(__file__) and freeze["protocol_sha256"] == sha(PROTOCOL), "Frozen source changed")
    for key, filename in (("manifest_sha256","input_manifest.json"),("cases_sha256","cases.json"),("schedule_sha256","schedule.json")):
        require(freeze[key] == sha(PREPARED / filename), "Prepared file changed")
    bindings = read(PREPARED / "input_manifest.json")["files"]
    base.check_bindings(bindings)
    require(base.installed_inventory() == read(base.PRE / "isolated_environment.json")["installed_distributions"], "Environment changed")
    require(sys.executable == read(base.PRE / "isolated_environment.json")["executable"] and sys.flags.isolated,
            "Use frozen isolated interpreter with -I")
    base.dependency_closure()
    adapter = base.load_adapter()
    adapter.author_closure(adapter.AUTHOR)
    schedule = read(PREPARED / "schedule.json")["invocations"]
    require(schedule == fixed_schedule(read(PREPARED / "cases.json")["cases"]), "Schedule differs")
    base.no_links(RUN)
    RUN.mkdir()
    save(RUN / "execution_started.json", {"utc": utc(), "source_sha256": sha(__file__), "protocol_sha256": sha(PROTOCOL),
         "executable": sys.executable, "phase_seconds": PHASE_SECONDS, "input_hashes_pass": True,
         "optimizer_calls_before_marker": 0})
    utilities, case_type = adapter.load_author(adapter.AUTHOR)
    # This in-memory plumbing substitution changes no helper source, projection,
    # clustering option or observation function. No old directory is written.
    base.PROJECTION, base.OUT, base.PHASE_SECONDS = PREPARED / "projections", RUN, PHASE_SECONDS
    outcomes = []
    for case in schedule:
        directory = RUN / f"call_{case['invocation']:02d}_{case['case']}"
        directory.mkdir()
        state = {"calls_started": 0}
        try:
            result = base.execute_case(adapter, utilities, case_type, case, directory, phase, state)
        except Exception as error:
            result = {"status": "UNKNOWN", "error_type": type(error).__name__, "calls_started": state["calls_started"],
                      "solver_actual_seconds": state.get("actual_seconds",0), "error_message_omitted_to_avoid_license_details": True}
        result.update({"invocation": case["invocation"], "case": case["case"], "role": case["comparison_role"]})
        save(directory / "result.json", result)
        outcomes.append(result)
    comparisons = compare_results(outcomes, schedule)
    save(RUN / "outcomes.json", {"invocations": outcomes, "comparisons": comparisons})
    base.check_bindings(bindings)
    base.check_bindings(transport_bindings)
    elapsed = time.perf_counter() - phase
    save(RUN / "completion.json", {"utc": utc(), "status": "COMPLETE", "fixed_targets": 15, "fixed_invocations": 21,
         "calls_started": sum(o["calls_started"] for o in outcomes), "uc_calls": 0, "new_UC_models": 0,
         "solver_seconds": math.fsum(o.get("solver_actual_seconds",0) for o in outcomes),
         "soft_call_overruns": [{"invocation": o["invocation"], "seconds": o["solver_actual_seconds"]-30}
                                 for o in outcomes if o.get("solver_actual_seconds",0)>30],
         "phase_seconds": elapsed, "phase_limit_seconds": PHASE_SECONDS, "phase_overrun": max(0,elapsed-PHASE_SECONDS),
         "unknown_invocations": sum(o["status"]=="UNKNOWN" for o in outcomes), "all_hashes_unchanged": True,
         "prepared_transport_hashes_unchanged": True, "prepared_transport_bindings": transport_bindings,
         "no_retries_or_fallback": True, "week2_3_fixed_ray_scores_computed": 0})


def self_test():
    # Invented values only; no base-module import, actual arrays or solver.
    checks = []
    def check(name, condition):
        require(condition, name)
        checks.append(name)
    for order in ORDERS:
        p = hour_order(order)
        check("bijection_"+str(order), sorted(p)==list(range(168)) and p[:48]==list(range(48)) and p[120:]==list(range(120,168)))
        check("clock_and_complete_days_"+str(order), all(i%24==p[i]%24 for i in range(168)) and
              all(p[s:s+24]==list(range(p[s],p[s]+24)) for s in range(0,168,24)))
    rows = [tuple(t*107+j for j in range(107)) for t in range(168)]
    permuted = [rows[i] for i in hour_order((3,1,2))]
    day_token = lambda a: sorted(tuple(a[i:i+24]) for i in range(0,168,24))
    check("all107_joint_day_tokens_preserved", day_token(rows)==day_token(permuted))
    altered = list(permuted); altered[50] = altered[50][:-1]+(-1,)
    check("last_coordinate_corruption_rejected", day_token(rows)!=day_token(altered))
    # Fully symmetric primary observation has six maps; the compatible Hindex
    # selects one. A first-map-only implementation would give the wrong answer.
    obs = {"tables":{"profiles":[{"rp":rp,"k":"k0001","value":"same"} for rp in RPS]},
           "matrices":{"N":[[1,0,0],[0,1,0],[0,0,1]]}}
    h = [{"p":str(i),"rp":rp,"k":"k0001"} for i,rp in enumerate(RPS)]
    ht = [{**r,"rp":RPS[(i+1)%3]} for i,r in enumerate(h)]
    x=compatible_maps(obs,obs,h,ht)
    check("all_primary_maps_not_first_only",len(x["primary_compatible_maps"])==6 and len(x["primary_and_hindex_compatible_maps"])==1)
    repeated = [{**r,"rp":"rp01"} for r in ht]
    x=compatible_maps(obs,obs,h,repeated)
    check("primary_collision_hindex_distinct",x["primary_equal"] and not x["primary_and_hindex_equal"])
    unique=json.loads(json.dumps(obs))
    for i,r in enumerate(unique["tables"]["profiles"]):
        r["value"]=str(i)
    x=compatible_maps(unique,unique,h,ht)
    check("incompatible_secondary_map_rejected",len(x["primary_compatible_maps"])==1 and not x["primary_and_hindex_equal"])
    changed=json.loads(json.dumps(unique)); changed["tables"]["profiles"][0]["value"]="changed"
    check("full_selected_profile_is_consumed",not compatible_maps(unique,changed,h,h)["primary_equal"])
    OUT.mkdir(parents=True,exist_ok=True)
    report={"status":"PASS","source_sha256":sha(__file__),"protocol_sha256":sha(PROTOCOL),
            "checks":checks,"fixture_count":len(checks),"scientific_reads":0,"author_imports":0,"solver_calls":0}
    save(OUT/"implementation_fixtures.json",report)
    print(json.dumps({"status":"PASS","fixture_count":len(checks),"scientific_reads":0,"solver_calls":0}))


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-test",action="store_true")
    group.add_argument("--prepare-only",action="store_true")
    group.add_argument("--run-prepared",action="store_true")
    args=parser.parse_args()
    if args.self_test:
        self_test()
    elif args.prepare_only:
        prepare()
    else:
        run_prepared()
