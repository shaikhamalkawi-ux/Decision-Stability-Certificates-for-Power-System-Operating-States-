"""Fixed, solver-free replay of closed research evidence; see the protocol.

Only stdlib imports and the hash-pinned stdlib certificate kernel are allowed.
This file never reconstructs native models, calls optimizers, or acquires data.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path, PurePosixPath
import sys
import time
from fractions import Fraction as Q
from types import SimpleNamespace

COMMIT = "520fe5974a4d92892906c42ce51a9d12ef304d3a"
KERNEL = "src/research8h_standalone_verify.py"
KERNEL_SHA = "708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f"
ADDENDUM = "reproducibility/native_sources"
ADDENDUM_SHA = "8b18311c646c0ae68d85765c57b690e2db5b5ffc071d1ab1b734b2db88d866b8"
OLD_ROOT = "C:/Users/gmalkawi/.codex/worktrees/dsc-temporal-information/3"
OLD_NATIVE = "C:/Users/gmalkawi/.codex/worktrees/dsc-v8r1-evidence/3/.work/v8r1_rts_inputs"
R = "results/research8h/"
HOD = R + "hour_of_day"
FRESH = R + "fresh_january_weeks"
UNCAPPED = R + "hour_of_day_uncapped"
ENERGY = R + "energy_lp_refinement"
FIXED = R + "hod_fixed_ray_transfer"
TAU = Q.from_float(1e-5)
MASK = (0,) * 6888 + (1,) * 12096 + (0,) * 4032
MANIFESTS = {
    HOD + "/input_manifest.csv": "078082667f83322d3540ad3ac215ebcc996d0d31b04fd52bfa75c1d2fd814fcc",
    FRESH + "/references/input_manifest.csv": "df48d8f6f60f51e43afa21ba4fcbd1438f274b86fb4a29e8fccbae3ae845fe26",
    FRESH + "/targets/input_manifest.csv": "56c5240486a8274ecb076b3aca49db236db4a7d72b865392016868119f7938dd",
    UNCAPPED + "/input_manifest.csv": "b0ffca41db74d7278c001c776ae3b8656272994d083c8fc215ecbbf665020f8a",
    FIXED + "/input_manifest.json": "3753fdcd4bb9d4f04c45f538631f019e54ff17d5c834266d0807a1353b89366a",
    ENERGY + "/input_manifest.json": "b85b1260ded4d4f0a2576c921a4d84581360bfe7adddac361d5ad8826fd6e32d",
    R + "seasonal_rule_transfer/input_manifest.csv": "a0898f56326a489622d812f685b2f4d816646874ef8528baa4902c6dac42144c",
}
RAYS = [
    (HOD + "/seed_26093200/lp", HOD + "/input_manifest.csv"),
    (HOD + "/seed_26093201/lp", HOD + "/input_manifest.csv"),
    *[(FRESH + f"/targets/seed_{seed}/lp", FRESH + "/targets/input_manifest.csv")
      for seed in (26093210, 26093220, 26093221)],
]
POINTS = [
    (HOD + "/" + case, "constructive_vector.npz", "integrality.npz")
    for case in ("january_identity", "seed_26100200")
] + [
    (FRESH + f"/references/week_{week}", "recovered_vector.npz", "integrality.npz")
    for week in (2, 3)
] + [
    (FRESH + "/targets/" + case, "constructive_vector.npz", "integrality.npz")
    for case in ("week_2_identity", "seed_26100210", "week_3_identity", "seed_26100220")
] + [
    (UNCAPPED + f"/seed_{seed}", "mip/recovered_vector.npz", "original_integrality.npz")
    for seed in (26093200, 26093201)
]
NULLS = [f"seed_{seed}__{kind}" for seed in (26093200, 26093201)
         for kind in ("old_january_locality", "own_full_to_two_cc", "own_full_to_locality48")]


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    def invalid(value):
        raise ValueError("Nonfinite JSON value: " + value)
    return json.loads(Path(path).read_text(encoding="utf-8-sig"), parse_constant=invalid)


def rational(record):
    return Q(int(record["numerator"]), int(record["denominator"]))


def rat(value):
    return {"numerator": str(value.numerator), "denominator": str(value.denominator), "float": float(value)}


def contained(root, name):
    require(isinstance(name, str) and "\\" not in name, "Expected relative POSIX package path")
    parts = PurePosixPath(name)
    require(not parts.is_absolute() and ".." not in parts.parts and ":" not in name,
            "Absolute or escaping package path")
    path = (root / Path(*parts.parts)).resolve()
    require(path.is_relative_to(root.resolve()), "Resolved path escapes package")
    return path


def check_file(path, record):
    require(isinstance(record["sha256"], str) and len(record["sha256"]) == 64,
            "Invalid SHA256 field")
    require(path.is_file() and path.stat().st_size == int(record["bytes"]), "Missing/size-mismatched file: " + str(path))
    require(sha(path) == record["sha256"], "Hash mismatch: " + str(path))


def relative_manifest(directory, manifest, expected=None):
    if expected:
        require(sha(manifest) == expected, "Relative manifest digest mismatch")
    with manifest.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        require(len(reader.fieldnames or []) == 3 and set(reader.fieldnames) == {"path", "sha256", "bytes"},
                "Unexpected relative-manifest fields")
        records = {}
        for row in reader:
            require(set(row) == {"path", "sha256", "bytes"} and row["path"] not in records, "Duplicate/invalid manifest row")
            path = contained(directory, row["path"])
            require(path != manifest.resolve(), "Manifest cannot bind itself")
            check_file(path, row)
            records[row["path"]] = row
    require(bool(records), "Empty relative manifest")
    return records


def objective_lower(model, cost, dual, tau=TAU):
    require(len(cost) == model.cols and len(dual) == model.rows, "Objective/dual length mismatch")
    require(all(math.isfinite(x) for x in (*cost, *dual)), "Nonfinite objective/dual")
    residual = list(map(Q, cost)); beta = norm = Q(0)
    for row, value in enumerate(dual):
        if not value:
            continue
        endpoint = model.row_lower[row] if value > 0 else model.row_upper[row]
        require(math.isfinite(endpoint), "Dual selects infinite row endpoint")
        d = Q(value); beta += d * Q(endpoint); norm += abs(d)
        for e in range(model.indptr[row], model.indptr[row + 1]):
            residual[model.indices[e]] -= d * Q(model.data[e])
    require(all(math.isfinite(x) for x in (*model.lower, *model.upper)), "Nonfinite box")
    box = sum((x * Q(model.lower[j] if x >= 0 else model.upper[j]) for j, x in enumerate(residual)), Q(0))
    residual_norm = sum(map(abs, residual), Q(0))
    nominal = beta + box
    expanded = nominal - tau * (norm + residual_norm)
    direct = beta - tau * norm + sum((x * (Q(model.lower[j]) - tau if x >= 0 else Q(model.upper[j]) + tau)
                                      for j, x in enumerate(residual)), Q(0))
    require(expanded == direct, "Direct endpoint/objective norm identity failed")
    return {"nominal_lower_bound_MWh": rat(nominal), "expanded_lower_bound_MWh": rat(expanded),
            "row_term": rat(beta), "finite_box_term": rat(box), "row_dual_l1": rat(norm),
            "stationarity_residual_l1": rat(residual_norm)}, residual


def intervals(li, ui, lt, ut):
    require(0 < li <= ui and 0 < lt <= ut, "Invalid/nonpositive optimum enclosures")
    return {"optimum_difference_MWh": (lt - ui, ut - li),
            "target_optimum_excess_over_chosen_incumbent_MWh": (lt - ui, ut - ui),
            "optimal_relative_penalty": (lt / ui - 1, ut / li - 1),
            "optimal_relative_penalty_percent": (100 * (lt / ui - 1), 100 * (ut / li - 1))}


def original_mask(mask):
    require(tuple(mask) == MASK, "Expected original full U/Y/Z mask, not projected U-only mask")


def fresh_ledger(rows):
    expected = {26093210: "CERTIFIED_INFEASIBLE_EXPANDED_MODEL", 26093211: "UNKNOWN",
                26093220: "CERTIFIED_INFEASIBLE_EXPANDED_MODEL", 26093221: "CERTIFIED_INFEASIBLE_EXPANDED_MODEL"}
    require(len(rows) == 4 and {r["seed"]: r["verdict"] for r in rows} == expected,
            "Fresh denominator or classification mismatch")


def focused_checks():
    tests = []
    model = SimpleNamespace(cols=1, rows=1, lower=(0.,), upper=(10.,), row_lower=(3.,),
                            row_upper=(math.inf,), indptr=(0, 1), indices=(0,), data=(1.,))
    for name, cost, dual, expected in [
        ("row_bound_expansion", (1.,), (1.,), Q(3) - TAU),
        ("nonstationary_box_residual", (2.,), (1.,), Q(3) - 2 * TAU),
        ("negative_bound_not_clipped", (1.,), (0.,), -TAU),
        ("negative_residual_uses_upper_box", (-1.,), (0.,), -Q(10) - TAU),
    ]:
        report, _ = objective_lower(model, cost, dual)
        require(rational(report["expanded_lower_bound_MWh"]) == expected, name)
        tests.append(name)
    def rejects(name, operation):
        try:
            operation()
        except ValueError:
            tests.append(name)
        else:
            raise ValueError("Expected rejection: " + name)
    rejects("infinite_selected_row_rejected", lambda: objective_lower(model, (1.,), (-1.,)))
    box = intervals(Q(2), Q(4), Q(6), Q(10))
    require(box["optimum_difference_MWh"] == (2, 8) and box["optimal_relative_penalty"] == (Q(1, 2), 4), "Interval direction")
    tests.append("difference_and_relative_endpoints")
    rejects("nonpositive_identity_interval_rejected", lambda: intervals(Q(0), Q(4), Q(6), Q(10)))
    rejects("projected_mask_rejected", lambda: original_mask((0,) * 6888 + (1,) * 4032 + (0,) * 12096))
    rejects("missing_unknown_case_rejected", lambda: fresh_ledger([]))
    rejects("package_parent_escape_rejected", lambda: contained(Path.cwd(), "../outside"))
    rejects("absolute_package_path_rejected", lambda: contained(Path.cwd(), "C:/outside"))
    return {"status": "FOCUSED_NEW_LOGIC_CHECKS_PASS", "tests": tests,
            "old_kernel_fixture_suite_rerun": False, "optimization_calls": 0}


class Replay:
    def __init__(self, root, output):
        self.root, self.output = root, output
        self.package = relative_manifest(root, root / "FILE_MANIFEST.csv")
        for name in (KERNEL, "reproducibility/replay_closed_research.py", "docs/research8h/PORTABLE_CLOSED_REPLAY_PROTOCOL.md"):
            require(name in self.package, "Required implementation not bound by package: " + name)
        require(sha(self.path(KERNEL)) == KERNEL_SHA, "Unreviewed mathematical kernel")
        require(sha(Path(__file__)) == sha(self.path("reproducibility/replay_closed_research.py")),
                "Executing wrapper differs from the packaged wrapper")
        native = root / ADDENDUM
        self.addendum = relative_manifest(native, self.path(ADDENDUM + "/FILE_MANIFEST.csv"), ADDENDUM_SHA)
        require(len(self.addendum) == 24, "Unexpected native addendum payload count")
        require(all(ADDENDUM + "/" + name in self.package for name in self.addendum), "Addendum not fully package-bound")
        mapping = self.json(ADDENDUM + "/path_map.json")
        require(mapping["maps"] == [
            {"original_prefix": OLD_ROOT, "portable_relative_root": "."},
            {"original_prefix": OLD_NATIVE, "portable_relative_root": ADDENDUM + "/rts_inputs"}], "Changed prefix map")
        self.maps = [(OLD_ROOT, str(root)), (OLD_NATIVE, str(native / "rts_inputs"))]
        bindings = self.json(ADDENDUM + "/source_bindings.json")
        require(bindings["native_file_count"] == 17 and bindings["native_bytes"] == 3734672 and not bindings["conflicting_provenance"], "Native inventory scope mismatch")
        require(len(bindings["files"]) == 17 and sum(r["bytes"] for r in bindings["files"]) == 3734672, "Native ledger size mismatch")
        seen = set()
        for record in bindings["files"]:
            require(record["original_path"] not in seen, "Duplicate native original binding")
            seen.add(record["original_path"])
            p = self.remap(record["original_path"])
            require(p == contained(native, record["portable_path"]), "Native prefix/per-file mapping disagreement")
            check_file(p, record)
        # Dynamic imports must not create a __pycache__ inside the archive.
        sys.dont_write_bytecode = True
        spec = importlib.util.spec_from_file_location("closed_replay_exact_kernel", self.path(KERNEL))
        self.v = importlib.util.module_from_spec(spec); sys.modules[spec.name] = self.v; spec.loader.exec_module(self.v)
        self.manifests = {}
        for name, expected in MANIFESTS.items():
            path = self.path(name); require(sha(path) == expected, "Historical manifest digest mismatch: " + name)
            rows = self.json(name) if path.suffix == ".json" else list(csv.DictReader(path.open(encoding="utf-8-sig", newline="")))
            require(isinstance(rows, list) and bool(rows), "Empty/invalid historical manifest")
            names = set()
            for row in rows:
                require(set(row) == {"path", "sha256", "bytes"} and row["path"] not in names, "Historical manifest row schema/duplicate")
                names.add(row["path"]); check_file(self.remap(row["path"]), row)
            self.manifests[name] = {"sha256": expected, "files_checked": len(rows), "digests": sorted({r["sha256"] for r in rows})}
        self.save("provenance", {"status": "PACKAGE_ADDENDUM_AND_REQUIRED_MANIFESTS_PASS", "package_payloads": len(self.package),
                  "native_payloads": 17, "native_bytes": 3734672, "addendum_manifest_sha256": ADDENDUM_SHA,
                  "historical_manifests": self.manifests, "physical_native_reconstruction_performed": False})

    def path(self, name):
        require(name in self.package, "Input absent from package manifest: " + name)
        return contained(self.root, name)

    def remap(self, name):
        name = name.replace("\\", "/")
        for prefix, replacement in self.maps:
            if name == prefix or name.startswith(prefix + "/"):
                relative = name[len(prefix):].lstrip("/")
                path = contained(Path(replacement), relative)
                require(path.is_relative_to(self.root), "Mapped historical path escapes package")
                require(path.relative_to(self.root).as_posix() in self.package, "Mapped historical file not package-bound")
                return path
        raise ValueError("Unmapped historical path: " + name)

    def json(self, name):
        return read_json(self.path(name))

    def array(self, name, key):
        return self.v.read_npz(self.path(name), (key,))[key].values

    def model(self, directory):
        for name in ("matrix.npz", "bounds.npz"):
            self.path(directory + "/" + name)
        return self.v.load_model(contained(self.root, directory))

    def labels(self, directory):
        with gzip.open(self.path(directory + "/row_metadata.csv.gz"), "rt", encoding="utf-8", newline="") as stream:
            return list(csv.DictReader(stream))

    def save(self, name, report):
        require("/" not in name and "\\" not in name, "Report name must be a basename")
        with (self.output / (name + ".json")).open("x", encoding="utf-8") as stream:
            json.dump(report, stream, indent=2, allow_nan=False); stream.write("\n")
        print(json.dumps({"check": name, "status": report.get("status", "PASS")}), flush=True)

    def point(self, directory, vector_name, mask_name, label):
        model = self.model(directory)
        point = self.array(directory + "/" + vector_name, "vector")
        mask = self.array(directory + "/" + mask_name, "integrality"); original_mask(mask)
        report = self.v.check_point(model, point, mask, TAU)
        require(report["expanded_pass"], "Rejected expected original-binary positive: " + directory)
        report.update(model=directory, vector=vector_name, mask=mask_name, original_mask_checked=True)
        self.save(label, report)
        return model, point, mask

    def negative(self, directory, manifest, label):
        certificate = self.json(directory + "/dual_certificate.json")
        require(certificate["experiment_manifest_sha256"] == MANIFESTS[manifest], "Wrong experiment/certificate binding")
        require(set(certificate["model_artifacts"].values()) <= set(self.manifests[manifest]["digests"]), "Manifest does not bind mathematical inputs")
        for name, key in (("raw_solver_ray.npz", "raw_solver_ray_sha256"), ("row_metadata.csv.gz", "row_metadata_sha256")):
            require(sha(self.path(directory + "/" + name)) == certificate[key], "Missing or changed ray provenance binding")
        parent = directory.rsplit("/", 1)[0]
        original_mask(self.array(parent + "/integrality.npz", "integrality"))
        for name in ("matrix.npz", "bounds.npz"):
            require(sha(self.path(directory + "/" + name)) == sha(self.path(parent + "/" + name)), "LP and original-binary model differ")
        bindings = self.v.ray_bindings(contained(self.root, directory), certificate, None, ())
        model = self.model(directory)
        report = self.v.check_ray(model, self.v.parse_multipliers(certificate, model.rows), TAU)
        require(report["status"] == "CERTIFIED_EXPANDED_INFEASIBLE", "Expected negative ray did not separate")
        compare = self.v.archived_ray_comparison(certificate, report)
        require(bool(compare) and all(compare.values()), "Archived exact ray gap mismatch")
        report.update(model=directory, exact_claim_comparison=compare, local_model_bindings=bindings,
                      experiment_manifest_verified_by_wrapper=manifest)
        self.save(label, report)

    def unknown(self):
        fresh_ledger(self.json(FRESH + "/targets/outcomes.json"))
        directory = FRESH + "/targets/seed_26093211"
        model = self.model(directory); point = self.array(directory + "/lp/returned_vector.npz", "vector")
        mask = self.array(directory + "/integrality.npz", "integrality"); original_mask(mask)
        report = self.v.check_point(model, point, (0,) * model.cols, TAU)
        nonbinary = sum(flag and value not in (0., 1.) for flag, value in zip(mask, point))
        require(report["expanded_pass"] and nonbinary > 0, "Expected continuous-only nonbinary point")
        mip = self.json(directory + "/mip/result.json")
        require(mip["verdict"] == "UNKNOWN" and mip["model_status"] == "Time limit reached" and not mip["solution_value_valid"], "Unknown MIP status changed")
        require(mip["optimization_calls"] == 1, "Unexpected unknown-case MIP count")
        for name in ("raw_vector.npz", "recovered_vector.npz"):
            require(not (self.root / directory / "mip" / name).exists(), "Unexpected MIP point for no-incumbent outcome")
        report.update(status="CONTINUOUS_POINT_VERIFIED_BINARY_VERDICT_UNKNOWN", exact_nonbinary_original_coordinates=nonbinary,
                      original_binary_mask_not_applied_to_LP=True, binary_verdict="UNKNOWN", ordinary_denominator=4)
        self.save("fresh_continuous_and_unknown", report)

    def nulls(self):
        require(self.json(FIXED + "/candidate_order.json") == NULLS, "Fixed-null candidate order changed")
        for i, name in enumerate(NULLS):
            directory = FIXED + "/candidates/" + name
            candidate = self.json(directory + "/candidate.json")
            require(candidate["id"] == name, "Fixed candidate identity mismatch")
            model_dir = FIXED + "/" + candidate["model_directory"].replace("\\", "/")
            require(sha(self.remap(candidate["source_certificate"])) == candidate["source_certificate_sha256"], "Fixed candidate source binding mismatch")
            self.path(model_dir + "/row_metadata.csv.gz")
            self.v.ray_bindings(contained(self.root, model_dir), candidate, None, ())
            model = self.model(model_dir)
            report = self.v.check_ray(model, self.v.parse_multipliers(candidate, model.rows), TAU)
            require(report["status"] == "VALID_NONSEPARATING_RAY", "Fixed null no longer nonseparating")
            saved = self.json(directory + "/exact_check.json")["verification"]
            for key in ("separation_gap", "expanded_separation_gap"):
                require(rational(report[key]) == rational(saved[key]), "Fixed null exact gap mismatch")
            report.update(candidate=name, model=model_dir, feasibility_claim=False)
            self.save("fixed_null_" + str(i), report)

    @staticmethod
    def row(model, row):
        return {model.indices[e]: model.data[e] for e in range(model.indptr[row], model.indptr[row + 1]) if model.data[e]}

    def uncapped_relation(self, directory, parent):
        model, capped = self.model(directory), self.model(parent)
        labels, parent_labels = self.labels(directory), self.labels(parent)
        cap = [i for i, r in enumerate(parent_labels) if r["family"] == "fossil_energy_cap"]
        require(len(cap) == 1 and capped.row_lower[cap[0]] == -math.inf and capped.row_upper[cap[0]] == 23195., "Wrong parent cap")
        keep = [i for i in range(capped.rows) if i != cap[0]]
        require(model.rows + 1 == capped.rows and model.cols == capped.cols == 23016, "Uncapped shape mismatch")
        require(model.lower == capped.lower and model.upper == capped.upper, "Column boxes changed with cap deletion")
        require(len(labels) == model.rows and len(parent_labels) == capped.rows, "Row labels shape mismatch")
        for new, old in enumerate(keep):
            require(self.row(model, new) == self.row(capped, old) and model.row_lower[new] == capped.row_lower[old]
                    and model.row_upper[new] == capped.row_upper[old], "Cap-only deletion mismatch")
            require(all(labels[new][key] == parent_labels[old][key] for key in ("family", "hour_0based", "uid")), "Cap-deleted row label mismatch")
        require(not any(r["family"] == "fossil_energy_cap" or "mean" in r["family"] for r in labels), "Cap/mean retained in uncapped model")
        mask = self.array(directory + "/original_integrality.npz", "integrality"); original_mask(mask)
        require(mask == self.array(parent + "/integrality.npz", "integrality"), "Original parent mask mismatch")
        cost = self.array(directory + "/objective.npz", "objective")
        require({j: x for j, x in enumerate(cost) if x} == self.row(capped, cap[0]), "Objective differs from deleted cap row")
        # The inherited identity archive has no duplicated model metadata.
        # Its parent declares the unchanged hour-major column layout.
        meta = self.json(parent + "/model_metadata.json")
        with self.path(ADDENDUM + "/rts_inputs/raw/RTS-GMLC_v0.2.3/gen.csv").open(encoding="utf-8", newline="") as stream:
            fuels = {r["GEN UID"]: r["Fuel"] for r in csv.DictReader(stream)}
        units = meta["unit_names"]; fossil = [j for j, uid in enumerate(units) if fuels[uid] in ("Coal", "Oil", "NG")]
        require(len(units) == 41 and len(fossil) == 23 and {units[j] for j in fossil} == set(meta["fossil_units"]), "Native fossil roster mismatch")
        expected = {t * 41 + j for t in range(168) for j in fossil}
        require(cost == tuple(1. if j in expected else 0. for j in range(model.cols)), "Fossil objective support mismatch")
        return model, cost, mask

    def lower(self, directory, dual_directory, model, cost):
        dual = self.array(dual_directory + "/projected_row_dual.npz", "row_dual")
        report, residual = objective_lower(model, cost, dual)
        saved = self.json(dual_directory + "/exact_lower_bound.json")
        require(all(rational(saved[k]) == rational(v) for k, v in report.items()), "Exact objective lower-bound claim mismatch")
        archived = self.json(dual_directory + "/exact_stationarity_residual.json")
        require(len({r["column"] for r in archived}) == len(archived), "Duplicate sparse objective residual")
        require({r["column"]: rational(r) for r in archived} == {j: x for j, x in enumerate(residual) if x}, "Exact sparse objective residual mismatch")
        zero, _ = objective_lower(model, cost, (0.,) * model.rows)
        lower = max(rational(report["expanded_lower_bound_MWh"]), rational(zero["expanded_lower_bound_MWh"]))
        report.update(status="EXACT_EXPANDED_OBJECTIVE_LOWER_BOUND", model=directory, selected_lower_MWh=rat(lower),
                      sparse_residual_matches=True, zero_dual_bound=zero, exact_optimality_claim=False)
        return lower, report

    def energy(self):
        identity = ENERGY + "/january_identity"
        model, cost, mask = self.uncapped_relation(identity, HOD + "/january_identity")
        point = self.array(HOD + "/january_identity/constructive_vector.npz", "vector")
        checked = self.v.check_point(model, point, mask, TAU)
        require(checked["expanded_pass"], "Uncapped identity point rejected")
        li, report = self.lower(identity, identity, model, cost)
        ui = sum((Q(c) * Q(x) for c, x in zip(cost, point)), Q(0))
        reuse = self.json(UNCAPPED + "/reused_identity_bounds.json")
        require(li == rational(reuse["lower_MWh"]) and ui == rational(reuse["reference_upper_MWh"]), "Inherited identity bounds mismatch")
        report.update(verified_upper_MWh=rat(ui), original_binary_point=checked)
        self.save("energy_identity", report)
        brackets = self.json(UNCAPPED + "/energy_brackets.json")
        require([r["case"] for r in brackets] == ["seed_26093200", "seed_26093201"], "HOD energy denominator changed")
        for item in brackets:
            case = item["case"]; directory = UNCAPPED + "/" + case
            model, cost, mask = self.uncapped_relation(directory, HOD + "/" + case)
            point = self.array(directory + "/mip/recovered_vector.npz", "vector")
            checked = self.v.check_point(model, point, mask, TAU)
            require(checked["expanded_pass"], "HOD uncapped binary upper rejected")
            lt, report = self.lower(directory, directory + "/lp", model, cost)
            ut = sum((Q(c) * Q(x) for c, x in zip(cost, point)), Q(0))
            mip = self.json(directory + "/mip/result.json")
            require(ut == rational(mip["verified_upper_MWh"]), "MIP upper-energy claim mismatch")
            require(all(rational(item[key]) == value for key, value in (("lower_MWh", lt), ("upper_MWh", ut),
                    ("identity_lower_MWh", li), ("identity_reference_upper_MWh", ui))), "Archived optimum bounds mismatch")
            ranges = intervals(li, ui, lt, ut)
            for key, (lo, hi) in ranges.items():
                require(rational(item[key]["lower"]) == lo and rational(item[key]["upper"]) == hi, "Interval arithmetic mismatch: " + key)
            report.update(verified_upper_MWh=rat(ut), original_binary_point=checked,
                          intervals={k: {"lower": rat(lo), "upper": rat(hi)} for k, (lo, hi) in ranges.items()})
            self.save("energy_" + case, report)

    def finish(self, started):
        require(relative_manifest(self.root, self.root / "FILE_MANIFEST.csv") == self.package, "Package changed during replay")
        require(relative_manifest(self.root / ADDENDUM, self.path(ADDENDUM + "/FILE_MANIFEST.csv"), ADDENDUM_SHA) == self.addendum,
                "Native addendum changed during replay")
        self.save("summary", {"status": "CLOSED_RESEARCH_PORTABLE_REPLAY_PASS", "evidence_commit": COMMIT,
                  "negative_rays": 5, "fixed_positive_points": 10, "additional_uncapped_identity_check": 1,
                  "continuous_unknown_diagnostic": 1, "fixed_nonseparating_candidates": 6,
                  "objective_lower_bounds": 3, "HOD_energy_intervals": 2, "fresh_ordinary_denominator": 4,
                  "required_historical_manifests": len(MANIFESTS), "package_payloads": len(self.package),
                  "native_addendum_payloads": 24, "all_package_hashes_unchanged": True, "optimization_calls": 0,
                  "network_calls": 0, "native_reconstruction": False, "elapsed_s": time.perf_counter() - started,
                  "python": sys.version, "wrapper_sha256": sha(Path(__file__)), "kernel_sha256": KERNEL_SHA,
                  "package_root": str(self.root), "second_machine_execution_claim": False,
                  "scope": "Exact archived expanded-model mathematics and selected closed provenance; no new optimization, physical reconstruction or active follow-up outcomes."})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--report-dir", type=Path, required=True)
    args = parser.parse_args()
    root, output = args.package_root.resolve(), args.report_dir.resolve()
    require(root.is_dir() and not output.exists() and not output.is_relative_to(root),
            "Use an existing package and a NEW report directory outside it")
    output.mkdir(parents=True, exist_ok=False); started = time.perf_counter()
    try:
        replay = Replay(root, output)
        replay.save("focused_checks", focused_checks())
        for i, (directory, vector, mask) in enumerate(POINTS):
            replay.point(directory, vector, mask, "point_" + str(i))
        for i, (directory, manifest) in enumerate(RAYS):
            replay.negative(directory, manifest, "negative_" + str(i))
        replay.unknown(); replay.nulls(); replay.energy(); replay.finish(started)
    except Exception as error:
        report = {"status": "CLOSED_RESEARCH_REPLAY_FAILED", "error_type": type(error).__name__, "error": str(error),
                  "optimization_calls": 0, "elapsed_s": time.perf_counter() - started, "partial_reports_preserved": True}
        with (output / "failure.json").open("x", encoding="utf-8") as stream:
            json.dump(report, stream, indent=2); stream.write("\n")
        print(json.dumps(report), flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
