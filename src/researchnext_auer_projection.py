"""Author-code projection adapter; this revision has NO scientific clustering CLI.

--preflight is metadata/source/static-roster inspection. --self-test uses synthetic
inputs only. --prepare-only reads the fixed archives but does not import TSAM or
author modules. The dormant author_representation function is source-reviewable;
an execution harness/solver protocol needs a separate reviewed revision.
"""
from __future__ import annotations

import argparse
import ast
import copy
import csv
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import importlib
import importlib.metadata
import itertools
import json
import math
from pathlib import Path
import shutil
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/research_next/AUER_PROJECTION_PROTOCOL.md"
OUTPUT = ROOT / "results/research_next/auer_projection_preflight"
AUTHOR = ROOT / ".work/auer_projection_author_ce97428"
MAIN_COMMIT = "ce97428aa225037dcbcd848889ef55f3b67c17ba"
SUB_COMMIT = "8b1f53a75d152645e5ff8c7d5f417befaf316da5"
AUTHOR_HASHES = {
    "InOutModule/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "InOutModule/Utilities.py": "f9d6b69fc319ccd51c1e2cffa6ddc6f120e5eab457e451849331f914ce5984f2",
    "InOutModule/CaseStudy.py": "dccce27eaa9db4dbeda6e71224e7019da503d654c9613ed481ed7a6220f26663",
    "InOutModule/ExcelReader.py": "8b1e2aa76b767afaf95ca849593887b0dcaa4fa17a7c340c05863a0c7b258960",
    "InOutModule/printer.py": "1f03b1fcf2210a1e8e526f6bda0899aa025a823df95b29c292cf21beee92c6ad",
    "InOutModule/LICENSE": "b5f75f2e1c80f1fa9d731275c324ecf63c1bf3f1aa77630c04062f35db35a2f1",
    "LEGO_LICENSE": "30b265e3d9342fe74130c5b82388fb7c39b2144d0e9cb09f706074c5b21df309",
    "environment.yml": "de49e8bd5a46a5a7de7cb859ab983caa3688e17b0bd408ad091e635e30233a34",
}
PARENTS = {
    "week1": ("results/research8h/hour_of_day", "078082667f83322d3540ad3ac215ebcc996d0d31b04fd52bfa75c1d2fd814fcc"),
    "fresh": ("results/research8h/fresh_january_weeks/targets", "56c5240486a8274ecb076b3aca49db236db4a7d72b865392016868119f7938dd"),
}
SCHEDULE = [
    (1, "week1", "january_identity", "identity"),
    (1, "week1", "seed_26093200", "target"),
    (1, "week1", "seed_26093201", "target"),
    (1, "week1", "seed_26100200", "positive_control"),
    (2, "fresh", "week_2_identity", "identity"),
    (2, "fresh", "seed_26093210", "target"),
    (2, "fresh", "seed_26093211", "target"),
    (2, "fresh", "seed_26100210", "positive_control"),
    (3, "fresh", "week_3_identity", "identity"),
    (3, "fresh", "seed_26093220", "target"),
    (3, "fresh", "seed_26093221", "target"),
    (3, "fresh", "seed_26100220", "positive_control"),
]
EXPECTED_VERSIONS = {"pandas": "2.2.3", "tsam": "2.3.9", "pyomo": "6.9.2",
                     "gurobipy": "13.0.0", "rich": "14.0.0", "openpyxl": "3.1.5",
                     "matplotlib": "3.10.3"}


def utc():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_new(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def no_links(path):
    path = Path(path).absolute()
    for candidate in [path, *path.parents]:
        if candidate.exists():
            s = candidate.lstat()
            require(not candidate.is_symlink() and not (getattr(s, "st_file_attributes", 0) & 1024),
                    f"Symlink/reparse path unsupported: {candidate}")


def author_closure(directory):
    directory = Path(directory)
    require(directory.is_dir(), "Author snapshot absent")
    no_links(directory)
    inventory = []
    for name, expected in AUTHOR_HASHES.items():
        path = directory / name
        no_links(path)
        require(path.is_file() and digest(path) == expected, f"Author source mismatch: {name}")
        inventory.append({"path": name, "sha256": expected, "bytes": path.stat().st_size})
    provenance = read(directory / "AUTHOR_CLOSURE.json")
    require(provenance["main_commit"] == MAIN_COMMIT and provenance["submodule_commit"] == SUB_COMMIT,
            "Author revision mismatch")
    actual = {str(p.relative_to(directory)).replace("\\", "/") for p in directory.rglob("*") if p.is_file()}
    require(actual == set(AUTHOR_HASHES) | {"AUTHOR_CLOSURE.json"}, "Unexpected author snapshot file")
    imports = {}
    for name in AUTHOR_HASHES:
        if name.endswith(".py"):
            tree = ast.parse((directory / name).read_text(encoding="utf-8-sig"))
            imports[name] = sorted({n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
                                   | {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names})
    require("MIT License" in (directory / "InOutModule/LICENSE").read_text(), "License not MIT")
    return {"files": inventory, "provenance_sha256": digest(directory / "AUTHOR_CLOSURE.json"),
            "imports_static": imports, "source_execution": False}


def environment():
    packages = {}
    for name in sorted(set(EXPECTED_VERSIONS) | {"numpy", "scipy", "highspy"}):
        try:
            version = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            version = None
        packages[name] = {"installed_version": version, "author_pin": EXPECTED_VERSIONS.get(name)}
    matches = all(packages[name]["installed_version"] == version for name, version in EXPECTED_VERSIONS.items())
    return {"executable": sys.executable, "python": sys.version, "isolated": sys.flags.isolated,
            "no_site": sys.flags.no_site, "packages": packages,
            "author_package_pins_match": matches,
            "gurobi_python_package_available": packages["gurobipy"]["installed_version"] is not None,
            "gurobi_license": "NOT_CHECKED; package presence does not establish a license",
            "solver_calls": 0, "network_calls": 0, "license_environment_values_recorded": False}


def parent_index(key):
    relative, expected = PARENTS[key]
    manifest = ROOT / relative / "input_manifest.csv"
    require(digest(manifest) == expected, f"Parent manifest changed: {key}")
    with manifest.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    result = {}
    for row in rows:
        path = str(Path(row["path"]).resolve()).casefold()
        require(path not in result, "Duplicate parent manifest path")
        result[path] = row
    return result


def check_bound(path, indices):
    path = Path(path)
    no_links(path)
    expected = [index[str(path.resolve()).casefold()] for index in indices if str(path.resolve()).casefold() in index]
    require(expected, f"Input not covered by a pinned parent manifest: {path}")
    sha, size = digest(path), path.stat().st_size
    require(all(row["sha256"] == sha and int(row["bytes"]) == size for row in expected), f"Input changed: {path}")
    return {"path": str(path.resolve()), "sha256": sha, "bytes": size}


def native_paths():
    freeze = read(ROOT / PARENTS["week1"][0] / "prepared_freeze.json")
    native_root = Path(freeze["source_v3"])
    return native_root / "raw/RTS-GMLC_v0.2.3/gen.csv", native_root / "code/dscgrid_model.py"


def gen_records(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    by_id = {}
    for row in rows:
        require(row["GEN UID"] not in by_id, "Duplicate generator UID")
        by_id[row["GEN UID"]] = row
    return by_id


def scalar(value):
    value = float(value)
    require(math.isfinite(value), "Nonfinite projection value")
    return value


def structural_roster(meta, gen):
    buses = [str(int(b)) for b in meta["bus_ids"]]
    names = meta["unit_names"]
    require(len(buses) == len(set(buses)) and len(names) == len(set(names)), "Duplicate roster identity")
    records = []
    for uid in names:
        require(uid in gen, f"Missing native unit: {uid}")
        g = gen[uid]
        require(g["Category"] != "Solar RTPV", "Rooftop PV is already subtracted from demand")
        require(str(int(g["Bus ID"])) in buses, "Unit bus outside roster")
        rating = scalar(g["PMax MW"])
        require(rating > 0, "Nonpositive native rating")
        records.append({"g": uid, "i": str(int(g["Bus ID"])), "tec": g["Category"],
                        "MaxProd": rating, "MinProd": scalar(g["PMin MW"]),
                        "MinUpTime": scalar(g["Min Up Time Hr"]), "MinDownTime": scalar(g["Min Down Time Hr"]),
                        "ExisUnits": 1.0, "EnableInvest": 0.0, "MaxInvest": 0.0})
    counts = {b: 0 for b in buses}
    for g in records:
        if g["tec"] in {"Solar PV", "Wind", "Hydro"}:
            counts[g["i"]] += 1
    return records, {b: max(1, n) for b, n in counts.items()}


def project_arrays(meta, gen, native, hours=168):
    """Plain records only; no author/numpy import and no clustering."""
    names, buses = meta["unit_names"], meta["bus_ids"]
    require(len(native["nodal"]) == hours and len(native["pmin"]) == hours
            and len(native["pmax"]) == hours and len(native["net"]) == hours, "Wrong horizon")
    units, multiplicity = structural_roster(meta, gen)
    demand, profiles, inflows, errors = [], [], [], []
    max_net_discrepancy = 0.0
    for t in range(hours):
        lo, hi, nd = native["pmin"][t], native["pmax"][t], native["nodal"][t]
        require(len(lo) == len(hi) == len(names) and len(nd) == len(buses), "Wrong package width")
        k = f"k{t+1:04d}"
        for b, val in zip(buses, nd):
            demand.append({"scenario": "s1", "rp": "rp01", "k": k, "i": str(int(b)), "value": scalar(val)})
        max_net_discrepancy = max(max_net_discrepancy, abs(scalar(native["net"][t]) - sum(map(scalar, nd))))
        for j, g in enumerate(units):
            lower, upper = scalar(lo[j]), scalar(hi[j])
            require(lower <= upper, "Inverted native power bounds")
            common = {"scenario": "s1", "rp": "rp01", "k": k, "g": g["g"]}
            if g["tec"] in {"Solar PV", "Wind"}:
                require(lower == 0, "Unexpected renewable minimum omitted by projection")
                cf = upper / g["MaxProd"]
                require(math.isfinite(cf) and cf >= 0, "Invalid capacity-factor signal")
                profiles.append({**common, "value": cf})
                recovered = cf * g["MaxProd"]
                if recovered != upper:
                    delta = Fraction.from_float(recovered) - Fraction.from_float(upper)
                    errors.append({"t": t, "g": g["g"], "original_hex": upper.hex(),
                                   "recovered_hex": recovered.hex(), "delta_n": str(delta.numerator),
                                   "delta_d": str(delta.denominator)})
            elif g["tec"] == "Hydro":
                require(lower == upper, "Expected fixed native hydro bounds")
                inflows.append({**common, "value": upper})
            else:
                require(lower == g["MinProd"] and upper == g["MaxProd"], "Omitted thermal bounds vary")
    vres = [{**g, "scenario": "s1"} for g in units if g["tec"] in {"Solar PV", "Wind", "Hydro"}]
    return {"schema": "auer_supported_signal_projection_v1", "hours": hours, "scenario": "s1",
            "demand": demand, "vres": vres, "profiles": profiles, "inflows": inflows,
            "native_static_units": units, "bus_ids": list(map(int, buses)),
            "semantics": {"demand": "native nodal load less rooftop PV; no rooftop VRES added",
                          "utility_vres": "native upper availability divided by native nameplate rating",
                          "hydro": "fixed native output supplied as inflow SIGNAL; no operational equivalence",
                          "omitted": ["independent aggregate-net equation", "hydro must-dispatch constraint"],
                          "no_storage": True, "no_operational_model": True},
            "projection_audit": {"demand_roundtrip": "copied binary64", "hydro_roundtrip": "copied binary64",
                                 "vres_roundtrip_mismatches": errors,
                                 "max_net_vs_nodal_sum_MW": max_net_discrepancy,
                                 "author_demand_row_multiplicity_by_bus": multiplicity}}


class ProjectedCase:
    """Declared adapter object for unchanged author functions, not a LEGO UC model."""
    def copy(self):
        return copy.deepcopy(self)


def as_author_case(projected):
    import pandas as pd
    cs = ProjectedCase()
    cs.dGlobal_Scenarios = pd.DataFrame({"relativeWeight": [1.0]}, index=["s1"])
    cs.dPower_Demand = pd.DataFrame(projected["demand"]).set_index(["rp", "k", "i"])
    cs.dPower_VRES = pd.DataFrame(projected["vres"]).set_index("g")
    cs.dPower_VRESProfiles = pd.DataFrame(projected["profiles"]).set_index(["rp", "k", "g"])
    cs.dPower_Inflows = pd.DataFrame(projected["inflows"]).set_index(["rp", "k", "g"])
    cs.dPower_Storage = pd.DataFrame(columns=["g", "scenario", "i", "tec", "ExisUnits", "EnableInvest", "MaxInvest"]).set_index("g")
    return cs


def load_author(directory):
    author_closure(directory)  # Trust bytes before executing imported source.
    env = environment()
    require(env["author_package_pins_match"], "Pinned author environment unavailable; no backend substitution")
    require(not any(n == "ExcelReader" or n.startswith("InOutModule") for n in sys.modules), "Author modules already loaded")
    old = list(sys.path)
    try:
        sys.path[:0] = [str(Path(directory).resolve()), str((Path(directory) / "InOutModule").resolve())]
        utilities = importlib.import_module("InOutModule.Utilities")
        case_type = importlib.import_module("InOutModule.CaseStudy").CaseStudy
        for module_name in ["InOutModule", "InOutModule.Utilities", "InOutModule.CaseStudy", "InOutModule.printer", "ExcelReader"]:
            module = sys.modules[module_name]
            actual = Path(module.__file__).resolve()
            require(actual.is_relative_to(Path(directory).resolve()), "Author import escaped snapshot")
    finally:
        sys.path[:] = old
    return utilities, case_type


def author_representation(projected, utilities, case_type, *, scientific_execution_enabled=False):
    """Dormant reviewed call route. No CLI in this revision can enable it."""
    require(scientific_execution_enabled, "Scientific clustering not enabled in preflight revision")
    cs = as_author_case(projected)
    features = utilities._extract_scenario_data(cs, "s1", "maxInvestment")
    aggregated_features = utilities._prepare_aggregated_data(features, False)
    require(len(aggregated_features) == 168 and aggregated_features["k"].nunique() == 168,
            "Author features not one row per hour")
    reduced = utilities.apply_kmedoids_aggregation(cs, 3, rp_length=24, cluster_strategy="aggregated",
                    capacity_normalization="maxInvestment", sum_production=False, solver="gurobi", inplace=False)
    n, p_to, p_from = case_type.get_rpTransitionMatrices(reduced, clip_method="none", clip_value=0)
    reduced.rpTransitionMatrixAbsolute, reduced.rpTransitionMatrixRelativeTo, reduced.rpTransitionMatrixRelativeFrom = n, p_to, p_from
    require(n.to_numpy().sum() == 7 and n.shape == (3, 3), "Circular day-count invariant failed")
    return {"case": reduced, "features": aggregated_features, "N": n, "P_to": p_to, "P_from": p_from,
            "observation_tables": ["dPower_Demand", "dPower_VRESProfiles", "dPower_Inflows", "dPower_WeightsRP", "dPower_WeightsK"],
            "hindex_role": "retained for provenance; must be consumed for any future LDES or schedule-reconstruction claim",
            "author_kmedoids_calls": 1, "uc_optimizer_calls": 0}


def synthetic_tests():
    meta = {"unit_names": ["T", "PV1", "PV2", "H"], "bus_ids": [1, 2]}
    def g(uid, bus, cat, maximum, minimum=0):
        return {"GEN UID": uid, "Bus ID": str(bus), "Category": cat, "PMax MW": str(maximum),
                "PMin MW": str(minimum), "Min Up Time Hr": "48", "Min Down Time Hr": "48"}
    gen = {x["GEN UID"]: x for x in [g("T", 2, "NG CC", 10, 2), g("PV1", 1, "Solar PV", 3),
                                     g("PV2", 1, "Solar PV", 7), g("H", 2, "Hydro", 6)]}
    native = {"pmin": [[2, 0, 0, 4]], "pmax": [[10, 1, 2, 4]], "nodal": [[-1, 5]], "net": [4]}
    p = project_arrays(meta, gen, native, hours=1)
    require(p["demand"][0]["value"] == -1 and len(p["profiles"]) == 2 and len(p["inflows"]) == 1,
            "Supported negative-net/utility-PV/hydro schema failed")
    require(p["projection_audit"]["author_demand_row_multiplicity_by_bus"] == {"1": 2, "2": 1},
            "Multiplicity should reflect two generators at one demand bus")
    require(all(x["MinUpTime"] == 48 for x in p["native_static_units"]), "Dwell clipped in adapter")
    cases = []
    for label, mutate in [
        ("rooftop_double_count", lambda a,b,c: b["PV1"].update(Category="Solar RTPV")),
        ("hydro_not_fixed", lambda a,b,c: c["pmin"][0].__setitem__(3, 3)),
        ("varying_thermal_bound", lambda a,b,c: c["pmax"][0].__setitem__(0, 9)),
        ("nonfinite_demand", lambda a,b,c: c["nodal"][0].__setitem__(0, math.nan)),
        ("zero_rating", lambda a,b,c: b["PV1"].update({"PMax MW": "0"})),
        ("duplicate_identity", lambda a,b,c: a["unit_names"].__setitem__(2, "PV1")),
        ("renewable_minimum", lambda a,b,c: c["pmin"][0].__setitem__(1, 0.1)),
        ("wrong_width", lambda a,b,c: c["nodal"][0].append(3)),
    ]:
        a,b,c = copy.deepcopy((meta, gen, native)); mutate(a,b,c)
        try:
            project_arrays(a,b,c,hours=1)
        except ValueError:
            cases.append({"case": label, "rejected": True})
        else:
            raise AssertionError(f"Invalid projection accepted: {label}")
    try:
        author_representation({}, None, None)
    except ValueError:
        cases.append({"case": "scientific_execution_disabled", "rejected": True})
    else:
        raise AssertionError("Scientific guard failed")
    return {"synthetic_only": True, "positive_schema_checks": 3, "adversarial_cases": cases,
            "author_imports": 0, "archived_array_reads": 0, "clustering_calls": 0}


def preflight(directory):
    indices = [parent_index(k) for k in PARENTS]
    gen_path, model_path = native_paths()
    meta_path = ROOT / PARENTS["week1"][0] / "january_identity/model_metadata.json"
    bindings = [check_bound(p, indices) for p in [gen_path, model_path, meta_path]]
    units, mult = structural_roster(read(meta_path), gen_records(gen_path))
    return {"utc": utc(), "status": "SOURCE_AND_ENVIRONMENT_PREFLIGHT_ONLY",
            "environment": environment(), "author_source_closure": author_closure(directory),
            "static_native_bindings": bindings, "native_unit_count": len(units),
            "projected_signal_unit_count": sum(g["tec"] in {"Solar PV","Wind","Hydro"} for g in units),
            "predicted_author_demand_row_multiplicity": mult, "multiplicity_is_not_physical_load_scaling": True,
            "native_demand_semantics": "gross nodal load minus fixed rooftop PV, as source-inspected; utility PV/wind not subtracted",
            "scientific_array_reads": 0, "author_imports": 0, "clustering_calls": 0,
            "initial_probe_correction": "An earlier -I -S metadata probe hid site packages; -I with no_site=0 is authoritative."}


def prepare(directory):
    """Later separately authorized array preparation; never clusters."""
    import numpy as np
    initial_paths = [Path(__file__), PROTOCOL, Path(directory) / "AUTHOR_CLOSURE.json",
                     *[Path(directory) / name for name in AUTHOR_HASHES],
                     *[ROOT / relative / "input_manifest.csv" for relative, _ in PARENTS.values()]]
    initial_hashes = {str(path.resolve()): digest(path) for path in initial_paths}
    author_info = author_closure(directory)
    indices = {k: parent_index(k) for k in PARENTS}
    gen_path, model_path = native_paths()
    bindings = [check_bound(p, list(indices.values())) for p in [gen_path, model_path]]
    gen = gen_records(gen_path)
    target = OUTPUT / "prepared"
    target.mkdir(parents=True, exist_ok=False)
    save_new(target / "initial_source_guard.json", {"utc": utc(), "sha256": initial_hashes})
    cases = []
    for week, parent, name, role in SCHEDULE:
        folder = ROOT / PARENTS[parent][0] / name
        for filename in ["native_inputs.npz", "model_metadata.json", "permutation.csv"]:
            bindings.append(check_bound(folder / filename, [indices[parent]]))
        with np.load(folder / "native_inputs.npz", allow_pickle=False) as z:
            native = {key: z[key].tolist() for key in ["pmin", "pmax", "net", "nodal"]}
        projected = project_arrays(read(folder / "model_metadata.json"), gen, native)
        filename = name + ".json"
        save_new(target / filename, projected)
        cases.append({"week": week, "case": name, "role": role, "projection_file": filename,
                      "projection_sha256": digest(target / filename)})
    invocations = []
    for week in [1,2,3]:
        block = [case for case in cases if case["week"] == week]
        invocations.extend({"invocation": case["case"], "projection_file": case["projection_file"], "role": case["role"]} for case in block)
        identity = next(c for c in block if c["role"] == "identity")
        invocations.append({"invocation": identity["case"] + "_repeat", "projection_file": identity["projection_file"], "role": "determinism_repeat"})
    save_new(target / "input_bindings.json", bindings)
    save_new(target / "cases.json", {"cases": cases, "future_invocations": invocations})
    for path, expected in initial_hashes.items():
        require(digest(path) == expected, f"Source/protocol/parent/author changed during preparation: {path}")
    for entry in bindings:
        require(digest(entry["path"]) == entry["sha256"] and Path(entry["path"]).stat().st_size == entry["bytes"],
                f"Input changed during preparation: {entry['path']}")
    for case in cases:
        require(digest(target / case["projection_file"]) == case["projection_sha256"], "Projection output changed")
    save_new(target / "close_hash_check.json", {"initial_source_files": len(initial_hashes),
             "input_bindings": len(bindings), "projection_files": len(cases), "all_unchanged": True})
    save_new(target / "prepared_freeze.json", {"utc": utc(), "source_sha256": initial_hashes[str(Path(__file__).resolve())],
        "protocol_sha256": initial_hashes[str(PROTOCOL.resolve())], "author_closure": author_info,
        "case_count": 12, "target_count": 6, "future_invocations": 15,
        "bindings_sha256": digest(target / "input_bindings.json"), "cases_sha256": digest(target / "cases.json"),
        "initial_guard_sha256": digest(target / "initial_source_guard.json"),
        "close_check_sha256": digest(target / "close_hash_check.json"),
        "author_imports": 0, "clustering_calls": 0, "scientific_execution_enabled": False})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--prepare-only", action="store_true")
    p.add_argument("--author-dir", type=Path, default=AUTHOR)
    args = p.parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    if args.prepare_only:
        prepare(args.author_dir)
        result = {"status": "PREPARED_NO_CLUSTERING"}
    else:
        result = synthetic_tests() if args.self_test else preflight(args.author_dir)
        result["source_sha256"] = digest(__file__)
        result["protocol_sha256"] = digest(PROTOCOL)
        save_new(OUTPUT / ("synthetic_tests.json" if args.self_test else "preflight.json"), result)
    print(json.dumps(result if args.prepare_only else {"status": "PASS", "mode": "self-test" if args.self_test else "preflight",
          "clustering_calls": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
