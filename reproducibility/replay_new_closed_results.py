"""Fixed stdlib replay of fresh energy and HOD subset points; see its protocol.

No producer import, optimization, network request, or physical model assembly.
Run only from a reviewed package with a separately supplied manifest digest.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile
import time
from types import SimpleNamespace

SELF = "reproducibility/replay_new_closed_results.py"
PROTOCOL = "docs/research8h/PORTABLE_NEW_RESULTS_REPLAY_PROTOCOL.md"
HELPER = "reproducibility/replay_closed_research.py"
HELPER_SHA = "c6cf226ac82ecb5551dee2241e89b2fd1c990fdde3e27878758331b3f998fb85"
KERNEL = "src/research8h_standalone_verify.py"
KERNEL_SHA = "708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f"
ADDENDUM = "reproducibility/native_sources"
ADDENDUM_SHA = "8b18311c646c0ae68d85765c57b690e2db5b5ffc071d1ab1b734b2db88d866b8"
OLD_ROOT = "C:/Users/gmalkawi/.codex/worktrees/dsc-temporal-information/3"
OLD_NATIVE = "C:/Users/gmalkawi/.codex/worktrees/dsc-v8r1-evidence/3/.work/v8r1_rts_inputs"
R = "results/research8h/"
ENERGY = R + "fresh_january_energy"
FRESH = R + "fresh_january_weeks"
SUBSET = R + "hod_reoptimized_subsets"
FIXED = R + "hod_fixed_ray_transfer"
HOD = R + "hour_of_day"
TAU = Q.from_float(1e-5)
MASK = (0,) * 6888 + (1,) * 12096 + (0,) * 4032
PROJECTED = (0,) * 6888 + (1,) * 4032 + (0,) * 12096
IDENTITIES = ("week_2_identity", "week_3_identity")
TARGETS = ("seed_26093210", "seed_26093211", "seed_26093220", "seed_26093221")
WEEKS = dict(zip(TARGETS, (2, 2, 3, 3)))
CAPS = {2: 26532, 3: 48319}
HOD_CASES = ("seed_26093200", "seed_26093201")
RULES = ("two_cc", "locality48")
SUBSET_CASES = tuple(case + "__" + rule for case in HOD_CASES for rule in RULES)
NONBINARY_COUNTS = dict(zip(SUBSET_CASES, (245, 273, 255, 382)))
TEMPORAL = {"transition", "exclusive_transition", "minimum_up", "minimum_down"}
DWELL = {"minimum_up", "minimum_down"}
STATIC = {"aggregate_balance", "thermal_upper", "thermal_lower", "nodal_balance", "branch_flow", "fossil_energy_cap"}
LAYOUT = dict(P=0, U=6888, Y=10920, Z=14952, theta=18984)
NATIVE_NAMES = ("pmin", "pmax", "net", "rows", "nodal", "source_hour")
NATIVE_SHAPES = dict(pmin=(168, 41), pmax=(168, 41), net=(168,), rows=(168,), nodal=(168, 24), source_hour=(168,))
ENERGY_MANIFEST = "44b382d30a30b8485beda0cf080d22cd991b55a9f37491939f633d147bc14f2a"
SUBSET_MANIFEST = "1d3c54426828dcca5684ca21d6f1af95f2c05cfc87631423ae939a354c867119"
# mode: absolute historical, arm-relative, or repository-relative. No guessing.
MANIFESTS = (
    (ENERGY + "/input_manifest.csv", ENERGY_MANIFEST, 378, "historical", ""),
    (SUBSET + "/input_manifest.json", SUBSET_MANIFEST, 155, "historical", ""),
    (ENERGY + "/producer_artifact_manifest.csv", "f48d012ff996f86e1981afe3b2d79165b0c80ae47f0cfdde43922fc17cbd4b90", 169, "relative", ENERGY),
    (SUBSET + "/artifact_manifest.csv", "ba2c7a894fc7a2aa1984f05b9246233e73eb278a2c5abf93b99c5951add1c025", 71, "relative", ""),
    (FRESH + "/references/input_manifest.csv", "df48d8f6f60f51e43afa21ba4fcbd1438f274b86fb4a29e8fccbae3ae845fe26", None, "historical", ""),
    (FRESH + "/targets/input_manifest.csv", "56c5240486a8274ecb076b3aca49db236db4a7d72b865392016868119f7938dd", None, "historical", ""),
    (HOD + "/input_manifest.csv", "078082667f83322d3540ad3ac215ebcc996d0d31b04fd52bfa75c1d2fd814fcc", None, "historical", ""),
    (FIXED + "/input_manifest.json", "3753fdcd4bb9d4f04c45f538631f019e54ff17d5c834266d0807a1353b89366a", None, "historical", ""),
)


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    def invalid(value):
        raise ValueError("Nonfinite JSON: " + value)
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "Duplicate JSON key: " + key)
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding="utf-8-sig"), parse_constant=invalid, object_pairs_hook=unique)


def fraction(record):
    return Q(int(record["numerator"]), int(record["denominator"]))


def packed(value):
    return dict(numerator=str(value.numerator), denominator=str(value.denominator), approximate=float(value))


def bit_equal(left, right):
    return len(left) == len(right) and all(a == b and (not isinstance(a, float) or a.hex() == b.hex()) for a, b in zip(left, right))


def relative_name(name):
    require(isinstance(name, str), "Path must be a string")
    name = name.replace("\\", "/")
    path = PurePosixPath(name)
    require(name and not path.is_absolute() and ":" not in name and ".." not in path.parts,
            "Unsafe relative path: " + name)
    require(str(path) == name and name != ".", "Noncanonical relative path: " + name)
    return name


def historical_relative(name):
    name = name.replace("\\", "/")
    for old, new in ((OLD_NATIVE, ADDENDUM + "/rts_inputs"), (OLD_ROOT, "")):
        if name.startswith(old + "/"):
            tail = relative_name(name[len(old) + 1:])
            return relative_name(new + "/" + tail if new else tail)
    raise ValueError("Unmapped historical path: " + name)


def validate_records(records, expected=None):
    require(isinstance(records, list) and records, "Empty/invalid manifest")
    if expected is not None:
        require(len(records) == expected, "Manifest count mismatch")
    seen = set()
    for row in records:
        require(set(row) == {"path", "sha256", "bytes"}, "Manifest row fields")
        name = row["path"].replace("\\", "/")
        require(name not in seen, "Duplicate normalized manifest path")
        seen.add(name)
        require(re.fullmatch("[0-9a-f]{64}", row["sha256"]) is not None and int(row["bytes"]) >= 0,
                "Invalid manifest hash/size")


def full_mask(mask):
    require(tuple(mask) == MASK, "Expected original U/Y/Z mask, not a projected or zero mask")


def outward6(value, upper=False):
    integer = -((-value * 1000000).__floor__()) if upper else (value * 1000000).__floor__()
    whole, decimal = divmod(abs(integer), 1000000)
    return ("-" if integer < 0 else "") + f"{whole}.{decimal:06d}"


def check_decimals(value):
    if isinstance(value, dict):
        if {"numerator", "denominator", "outward_floor_6dp", "outward_ceiling_6dp"} <= value.keys():
            x = fraction(value)
            require(Q(str(value["outward_floor_6dp"])) == Q(outward6(x)), "Wrong outward lower display")
            require(Q(str(value["outward_ceiling_6dp"])) == Q(outward6(x, True)), "Wrong outward upper display")
        for item in value.values():
            check_decimals(item)
    elif isinstance(value, list):
        for item in value:
            check_decimals(item)


def ranges(li, ui, lt, ut):
    require(li <= ui, "Inverted identity bounds")
    if ut is None:
        return None
    require(lt <= ut, "Inverted target bounds")
    result = {"optimum_difference_MWh": (lt-ui, ut-li),
              "target_optimum_excess_over_chosen_incumbent_MWh": (lt-ui, ut-ui)}
    if li > 0 and lt > 0:
        result.update(optimal_relative_penalty=(lt/ui-1, ut/li-1),
                      optimal_relative_penalty_percent=(100*(lt/ui-1), 100*(ut/li-1)))
    return result


def project_dual(model, raw):
    require(len(raw) == model.rows and all(math.isfinite(x) for x in raw), "Invalid raw row dual")
    return tuple(0. if ((x > 0 and not math.isfinite(model.row_lower[i])) or
                        (x < 0 and not math.isfinite(model.row_upper[i]))) else x for i, x in enumerate(raw))


def row(model, index):
    lo, hi = model.indptr[index:index+2]
    return model.indices[lo:hi], model.data[lo:hi]


def same_row(left, i, right, j):
    li, ld = row(left, i); ri, rd = row(right, j)
    return li == ri and bit_equal(ld, rd) and bit_equal(
        (left.row_lower[i], left.row_upper[i]), (right.row_lower[j], right.row_upper[j]))


def same_models(left, right):
    require((left.rows, left.cols) == (right.rows, right.cols) and left.indices == right.indices and left.indptr == right.indptr,
            "Different model shape/sparsity")
    require(all(bit_equal(getattr(left, field), getattr(right, field))
                for field in ("data", "lower", "upper", "row_lower", "row_upper")), "Different model coefficients/bounds")


def selected_rows(model, labels, rule, production=True):
    require(rule in RULES and len(labels) == model.rows, "Unknown rule or row labels")
    if production:
        require({x["family"] for x in labels} == STATIC | TEMPORAL, "Unexpected full-parent families")
    kept = []
    for i, label in enumerate(labels):
        require(int(label["row"]) == i and label["family"] in STATIC | TEMPORAL, "Invalid row label")
        family = label["family"]
        if rule == "two_cc" and family in TEMPORAL and label["uid"] not in {"107_CC_1", "118_CC_1"}:
            continue
        if rule == "locality48" and family in DWELL:
            columns, values = row(model, i)
            support = [j for j, x in zip(columns, values) if x]
            require(support and all(6888 <= j < 18984 for j in support), "Dwell row has nonstate or empty support")
            if any(not 60 <= ((j-6888) % 4032)//24 <= 107 for j in support):
                continue
        kept.append(i)
    if production:
        require(len(kept) == (19985 if rule == "two_cc" else 28689), "Wrong fixed-rule row count")
    kept_set = set(kept)
    require(all(i in kept_set for i, x in enumerate(labels) if x["family"] in STATIC), "Static/background row dropped")
    return tuple(kept)


def verify_row_subset(reduced, full, labels, parent_labels, kept, original_key=None):
    require(reduced.rows == len(kept) == len(labels) and reduced.cols == full.cols and
            tuple(sorted(set(kept))) == tuple(kept) and all(0 <= r < full.rows for r in kept), "Invalid row selection")
    require(bit_equal(reduced.lower, full.lower) and bit_equal(reduced.upper, full.upper), "Column boxes changed")
    for i, old in enumerate(kept):
        require(same_row(reduced, i, full, old), "Retained row differs from parent")
        require(int(labels[i]["row"]) == i and all(labels[i][k] == parent_labels[old][k]
                for k in ("family", "hour_0based", "uid")), "Retained row labels differ")
        if original_key is not None:
            require(int(labels[i][original_key]) == old, "Wrong retained-parent row label")


class Replay:
    def __init__(self, root, output, manifest_digest, evidence_commit):
        self.root, self.output, self.manifest_digest, self.evidence_commit = root, output, manifest_digest, evidence_commit
        self.used = set(); self.historical = {}; self.resolved_bindings = {}
        require(re.fullmatch("[0-9a-f]{64}", manifest_digest) is not None, "Invalid outer-manifest digest")
        require(re.fullmatch("[0-9a-f]{40}", evidence_commit) is not None, "Expected explicit reviewed package commit")
        require(sha(root / "FILE_MANIFEST.csv") == manifest_digest, "Outer manifest differs from reviewed delivery")
        sys.dont_write_bytecode = True
        self.h = self.import_pinned(HELPER, HELPER_SHA, "new_replay_frozen_helpers")
        self.v = self.import_pinned(KERNEL, KERNEL_SHA, "new_replay_exact_kernel")
        self.package = self.h.relative_manifest(root, root / "FILE_MANIFEST.csv", manifest_digest)
        for name in (SELF, PROTOCOL, HELPER, KERNEL):
            self.path(name)
        require(sha(Path(__file__)) == sha(self.path(SELF)), "Executing wrapper differs from package")
        self.initial_inventory = self.inventory()
        require(self.initial_inventory == set(self.package) | {"FILE_MANIFEST.csv"}, "Unmanifested/missing package files")
        self.addendum = self.h.relative_manifest(root / ADDENDUM, self.path(ADDENDUM + "/FILE_MANIFEST.csv"), ADDENDUM_SHA)
        require(len(self.addendum) == 24 and all(ADDENDUM + "/" + x in self.package for x in self.addendum), "Native addendum closure")
        mapping = self.js(ADDENDUM + "/path_map.json")
        require(mapping["maps"] == [dict(original_prefix=OLD_ROOT, portable_relative_root="."),
                dict(original_prefix=OLD_NATIVE, portable_relative_root=ADDENDUM + "/rts_inputs")], "Changed prefix map")
        source = self.js(ADDENDUM + "/source_bindings.json")
        require(source["native_file_count"] == len(source["files"]) == 17 and source["native_bytes"] == 3734672 and
                not source["conflicting_provenance"], "Native provenance inventory mismatch")
        require(len({x["original_path"] for x in source["files"]}) == 17 and sum(x["bytes"] for x in source["files"]) == 3734672,
                "Native duplicate or byte count")
        for entry in source["files"]:
            relative = historical_relative(entry["original_path"])
            require(relative == ADDENDUM + "/" + relative_name(entry["portable_path"]), "Native per-file map mismatch")
            self.h.check_file(self.path(relative), entry)
        for manifest, digest, count, mode, base in MANIFESTS:
            self.check_manifest(manifest, digest, count, mode, base)
        self.review_gates()
        with self.path(ADDENDUM + "/rts_inputs/raw/RTS-GMLC_v0.2.3/gen.csv").open(encoding="utf-8-sig", newline="") as stream:
            roster = list(csv.DictReader(stream))
        require(len({x["GEN UID"] for x in roster}) == len(roster), "Duplicate native generator UID")
        self.fuels = {x["GEN UID"]: x["Fuel"] for x in roster}
        self.save("provenance", dict(status="NEW_REPLAY_PACKAGE_AND_PROVENANCE_PASS", package_payloads=len(self.package),
                  historical_manifests=self.historical, unique_historical_files=len(self.resolved_bindings),
                  package_manifest_sha256=manifest_digest, package_evidence_commit=evidence_commit,
                  commit_authentication="Recorded reviewed delivery identifier; no remote Git query", native_reconstruction=False))

    def import_pinned(self, name, digest, module_name):
        path = self.hpath(name)
        require(sha(path) == digest, "Unreviewed helper/kernel source")
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module; spec.loader.exec_module(module)
        return module

    def hpath(self, name):
        relative = relative_name(name); path = (self.root / relative).resolve()
        require(path.is_relative_to(self.root), "Path escapes package")
        return path

    def path(self, name):
        relative = relative_name(name)
        require(relative in self.package, "Input absent from package manifest: " + relative)
        self.used.add(relative)
        return self.hpath(relative)

    def inventory(self):
        return {p.relative_to(self.root).as_posix() for p in self.root.rglob("*") if p.is_file()}

    def js(self, name):
        return read_json(self.path(name))

    def array(self, directory, name, key, kind=None, length=None):
        a = self.v.read_npz(self.path(directory + "/" + name), (key,))[key]
        if kind is not None:
            return self.v.vector(a, kind, length, name)
        return a.values

    def model(self, directory):
        self.path(directory + "/matrix.npz"); self.path(directory + "/bounds.npz")
        return self.v.load_model(self.hpath(directory))

    def labels(self, directory):
        with gzip.open(self.path(directory + "/row_metadata.csv.gz"), "rt", encoding="utf-8", newline="") as stream:
            return list(csv.DictReader(stream))

    def save(self, name, report):
        require(re.fullmatch("[a-zA-Z0-9_]+", name) is not None, "Report name must be a basename")
        with (self.output / (name + ".json")).open("x", encoding="utf-8") as stream:
            json.dump(report, stream, indent=2, allow_nan=False); stream.write("\n")
        print(json.dumps(dict(check=name, status=report.get("status", "PASS"))), flush=True)

    def check_manifest(self, name, digest, count, mode, base):
        path = self.path(name); require(sha(path) == digest, "Historical manifest digest mismatch: " + name)
        if path.suffix == ".json":
            entries = self.js(name)
        else:
            with path.open(encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream)
                require(len(reader.fieldnames or []) == 3 and set(reader.fieldnames) == {"path", "sha256", "bytes"}, "CSV manifest fields")
                entries = list(reader)
        validate_records(entries, count)
        resolved = set()
        for entry in entries:
            relative = historical_relative(entry["path"]) if mode == "historical" else relative_name(
                (base + "/" if base else "") + relative_name(entry["path"]))
            p = self.path(relative); key = str(p)
            require(key not in resolved, "Two manifest paths resolve to one file")
            resolved.add(key)
            binding = (entry["sha256"], int(entry["bytes"]))
            require(key not in self.resolved_bindings or self.resolved_bindings[key] == binding, "Conflicting historical binding")
            self.resolved_bindings[key] = binding
            self.h.check_file(p, entry)
        self.historical[name] = dict(sha256=digest, entries_checked=len(entries), path_mode=mode, relative_base=base)

    def review_bindings(self, bindings, base=""):
        seen = set()
        for name, digest in bindings.items():
            relative = relative_name((base + "/" if base else "") + relative_name(name))
            require(relative not in seen, "Duplicate normalized review binding")
            seen.add(relative)
            require(sha(self.path(relative)) == digest, "Independent review binding mismatch: " + relative)

    def review_gates(self):
        fresh = self.js(R + "fresh_energy_review/postrun.json")
        require(fresh["status"] == "INDEPENDENT_FRESH_ENERGY_POSTRUN_PASS" and fresh["ordinary_denominator"] == 4 and
                fresh["identity_denominator"] == 2 and fresh["all_hashes_unchanged"] and fresh["accepted_binary_uppers"] == 4,
                "Fresh post-run review gate")
        require(fresh["manifest_sha256"] == ENERGY_MANIFEST and fresh["frozen_bindings"] == 378, "Fresh prepared binding")
        self.review_bindings(fresh["input_and_result_hashes"])
        prepared = self.js(R + "fresh_energy_review/prepared.json")
        require(prepared["status"] == "INDEPENDENT_FRESH_ENERGY_PREPARED_PASS" and prepared["manifest_sha256"] == ENERGY_MANIFEST,
                "Fresh prepared review gate")
        subset = self.js(R + "hod_reoptimized_subsets_independent_review/postrun_review.json")
        require(subset["status"] == "INDEPENDENT_HOD_SUBSET_POSTRUN_PASS" and subset["manifest_sha256"] == SUBSET_MANIFEST and
                subset["full_denominator"] == subset["continuous_positive_count"] == 4 and subset["binary_target_witnesses_established"] == 0 and
                subset["all_producer_files_unchanged"] and len(subset["producer_file_hashes"]) == 61, "Subset post-run gate")
        self.review_bindings(subset["producer_file_hashes"], SUBSET)
        pre = self.js(R + "hod_reoptimized_subsets_independent_review/prepared_review.json")
        require(pre["status"] == "INDEPENDENT_PREPARED_SUBSET_GATE_PASS" and pre["manifest_sha256"] == SUBSET_MANIFEST, "Subset prepared gate")
        ledger = self.js(R + "fresh_targets_postrun_review/final_ledger.json")
        require(ledger["status"] == "INDEPENDENT_FRESH_TARGET_FINAL_REVIEW_PASS" and ledger["ordinary_denominator"] == 4 and
                ledger["unknown_case"] == "seed_26093211", "Historical capped review gate")
        self.review_bindings(ledger["replayed_output_hashes"])
        self.h.fresh_ledger(self.js(FRESH + "/targets/outcomes.json"))

    def metadata(self, directory):
        meta = self.js(directory + "/model_metadata.json")
        require(meta["offsets"] == LAYOUT and (meta["hours"], meta["units"], meta["thermal_units"], meta["buses"]) == (168, 41, 24, 24),
                "Unexpected native column layout")
        require(len(meta["unit_names"]) == len(set(meta["unit_names"])) == 41 and len(meta["thermal_unit_names"]) == 24,
                "Unexpected generator roster")
        return meta

    def fossil_cost(self, meta, cols):
        fossil = [j for j, uid in enumerate(meta["unit_names"]) if self.fuels[uid] in ("Coal", "Oil", "NG")]
        require(len(fossil) == 23 and [meta["unit_names"][j] for j in fossil] == meta["fossil_units"] and
                "121_NUCLEAR_1" not in meta["fossil_units"], "Native fossil objective mismatch")
        support = {t*41+j for t in range(168) for j in fossil}
        return tuple(1. if j in support else 0. for j in range(cols))

    def cap_row(self, model, labels, cap, cost):
        found = [i for i, label in enumerate(labels) if label["family"] == "fossil_energy_cap"]
        require(len(found) == 1, "Expected exactly one cap row")
        index = found[0]
        require(model.row_lower[index] == -math.inf and model.row_upper[index] == float(cap), "Wrong cap bounds")
        columns, values = row(model, index)
        require({j: x for j, x in zip(columns, values) if x} == {j: x for j, x in enumerate(cost) if x}, "Cap/objective support differs")
        return index

    def native_transport(self, directory, week, identity):
        ref = FRESH + f"/references/week_{week}"
        parent = ref if identity else FRESH + "/targets/" + directory.rsplit("/", 1)[1]
        require(sha(self.path(directory + "/native_inputs.npz")) == sha(self.path(parent + "/native_inputs.npz")), "Copied native inputs changed")
        original = self.v.read_npz(self.path(ref + "/native_inputs.npz"), NATIVE_NAMES)
        current = self.v.read_npz(self.path(directory + "/native_inputs.npz"), NATIVE_NAMES)
        for key in NATIVE_NAMES:
            require(original[key].shape == current[key].shape == NATIVE_SHAPES[key] and original[key].dtype == current[key].dtype,
                    "Native shape/dtype mismatch")
        order = current["source_hour"].values
        require(original["source_hour"].values == tuple(range(168)) and original["rows"].values == tuple(range((week-1)*168, week*168)),
                "Wrong native reference week")
        require(sorted(order) == list(range(168)) and order[:48] == tuple(range(48)) and order[120:] == tuple(range(120, 168)) and
                all(t % 24 == s % 24 for t, s in enumerate(order)), "Changed HOD permutation/edges")
        if identity:
            require(order == tuple(range(168)), "Identity input is permuted")
        for key in ("pmin", "pmax", "net", "nodal", "rows"):
            a, b = original[key], current[key]; width = math.prod(a.shape[1:])
            expected = tuple(x for t in order for x in a.values[t*width:(t+1)*width])
            require(bit_equal(b.values, expected), "Native 107-package transport mismatch: " + key)
        if not identity:
            require(sha(self.path(directory + "/permutation.csv")) == sha(self.path(parent + "/permutation.csv")), "Permutation CSV changed")
            with self.path(directory + "/permutation.csv").open(encoding="utf-8-sig", newline="") as stream:
                permutation = list(csv.DictReader(stream))
            require(tuple(int(x["source_hour_0based"]) for x in permutation) == order and
                    tuple(int(x["native_row_0based"]) for x in permutation) == current["rows"].values, "Permutation/native row mismatch")

    def energy_model(self, case, week):
        directory = ENERGY + "/" + case; identity = case in IDENTITIES
        model = self.model(directory); labels = self.labels(directory); meta = self.metadata(directory)
        require((model.rows, model.cols) == (34680, 23016), "Fresh uncapped shape")
        mask = self.array(directory, "original_integrality.npz", "integrality", ("|u1", "<i4", "<i8"), model.cols); full_mask(mask)
        require(self.array(directory, "integrality.npz", "integrality") == PROJECTED, "Wrong declared U-only solver mask")
        cost = self.array(directory, "objective.npz", "objective", ("<f8",), model.cols)
        require(bit_equal(cost, self.fossil_cost(meta, model.cols)), "Wrong uncapped fossil objective")
        parent_dir = FRESH + "/targets/" + case; parent = self.model(parent_dir); parent_labels = self.labels(parent_dir)
        require((parent.rows, parent.cols) == (34681, 23016), "Fresh capped shape")
        full_mask(self.array(parent_dir, "integrality.npz", "integrality"))
        cap = self.cap_row(parent, parent_labels, CAPS[week], cost)
        keep = tuple(i for i in range(parent.rows) if i != cap)
        verify_row_subset(model, parent, labels, parent_labels, keep)
        for i, label in enumerate(labels):
            if "source_row_0based" in label:
                require(int(label["source_row_0based"]) == keep[i], "Wrong cap-deleted source row")
        retained = self.array(directory, "retained_parent_rows.npz", "rows")
        require(retained == (tuple(range(model.rows)) if identity else keep), "Wrong special identity/target row map")
        require(not any(x["family"] == "fossil_energy_cap" or "mean" in x["family"] for x in labels), "Cap or mean row retained")
        require(meta["energy_cap_constraints"] == meta["individual_mean_constraints"] == 0 and "budget_MWh" not in meta and
                meta["original_binary_columns"] == 12096 and meta["binary_columns"] == 4032, "Uncapped metadata contradicts model")
        if identity:
            reference = FRESH + f"/references/week_{week}"
            same_models(model, self.model(reference))
            require(bit_equal(cost, self.array(reference, "objective.npz", "objective")), "Reference objective mismatch")
        self.native_transport(directory, week, identity)
        return directory, model, cost, mask, dict(case=case, week=week, removed_cap_row=cap, source_cap_MWh=CAPS[week],
                exact_cap_only_relation=True, original_binary_coordinates=12096, native_107_transport=True, raw_native_assembly=False)

    def lower_bound(self, directory, model, cost, result):
        require(result["new_lower_bound_status"] == "EXACT_EXPANDED_OBJECTIVE_LOWER_BOUND" and result["prepared_manifest_sha256"] == ENERGY_MANIFEST,
                "Missing closed exact lower-bound result")
        for name, digest in result["model_artifacts"].items():
            require(sha(self.path(directory + "/" + relative_name(name))) == digest, "LP model-artifact mismatch")
        raw_arrays = self.v.read_npz(self.path(directory + "/lp/raw_duals.npz"), ("row_dual", "column_dual"))
        raw = self.v.vector(raw_arrays["row_dual"], ("<f8",), model.rows, "raw row dual")
        self.v.vector(raw_arrays["column_dual"], ("<f8",), model.cols, "raw column dual")
        projected = self.array(directory + "/lp", "projected_row_dual.npz", "row_dual", ("<f8",), model.rows)
        require(bit_equal(projected, project_dual(model, raw)), "Raw/projected dual disagreement")
        report, residual = self.h.objective_lower(model, cost, projected, TAU)
        saved = self.js(directory + "/lp/exact_lower_bound.json")
        require(all(fraction(saved[k]) == fraction(v) for k, v in report.items()) and fraction(saved["tau"]) == TAU,
                "Archived exact dual bound differs")
        require(sum(x != y for x, y in zip(raw, projected)) == saved["projected_entries"], "Wrong dual projection count")
        archived = self.js(directory + "/lp/exact_stationarity_residual.json")
        require([(int(x["column"]), fraction(x)) for x in archived] == [(j, q) for j, q in enumerate(residual) if q],
                "Exact stationarity residual differs or is duplicated")
        zero, _ = self.h.objective_lower(model, cost, (0.,)*model.rows, TAU)
        saved_zero = self.js(directory + "/zero_dual_baseline.json")
        require(all(fraction(saved_zero[k]) == fraction(v) for k, v in zero.items()), "Zero-dual baseline differs")
        require(fraction(result["expanded_lower_MWh"]) == fraction(report["expanded_lower_bound_MWh"]) and
                fraction(result["nominal_lower_MWh"]) == fraction(report["nominal_lower_bound_MWh"]), "LP lower claim mismatch")
        lower = max(fraction(report["expanded_lower_bound_MWh"]), fraction(zero["expanded_lower_bound_MWh"]))
        return lower, dict(dual_bound=report, zero_dual_bound=zero, selected_lower_MWh=packed(lower),
                           raw_projection_replayed=True, exact_sparse_residual_replayed=True, exact_optimality_claim=False)

    def point(self, directory, vector_name, model, mask):
        full_mask(mask)
        point = self.array(directory, vector_name, "vector", ("<f8",), model.cols)
        check = self.v.check_point(model, point, mask, TAU)
        require(check["expanded_pass"] and check["original_binary_coordinates_exact"] and check["binary_coordinates"] == 12096,
                "Rejected original-mask binary upper/control")
        return point, check

    def energy(self):
        brackets = self.js(ENERGY + "/energy_brackets.json"); identities = self.js(ENERGY + "/identity_energy_bounds.json")
        require([x["case"] for x in brackets] == list(TARGETS) and set(identities) == {"2", "3"}, "Energy denominator changed")
        check_decimals(brackets); check_decimals(identities)
        lps, mips = self.js(ENERGY + "/lp_results.json"), self.js(ENERGY + "/mip_results.json")
        require(list(lps) == list(IDENTITIES + TARGETS) and list(mips) == list(TARGETS), "Closed solve-result denominator changed")
        completion = self.js(ENERGY + "/completion.json")
        require(completion["ordinary_denominator"] == 4 and completion["new_identity_MIP_calls"] == 0 and
                completion["accepted_target_uppers"] == 4 and completion["all_frozen_hashes_unchanged"], "Energy completion gate")
        reference_bounds = {}; interval_records = []; cap_checks = []
        for case in IDENTITIES + TARGETS:
            week = int(case.split("_")[1]) if case in IDENTITIES else WEEKS[case]
            directory, model, cost, mask, relation = self.energy_model(case, week)
            lp = self.js(directory + "/lp/result.json"); require(lp == lps[case], "LP aggregate/per-case result mismatch")
            lower, lower_report = self.lower_bound(directory, model, cost, lp)
            if case in IDENTITIES:
                reference = FRESH + f"/references/week_{week}"
                binding = self.js(directory + "/reference_binding.json")
                require(sha(self.path(directory + "/reference_upper_vector.npz")) == sha(self.path(reference + "/recovered_vector.npz")) ==
                        binding["reference_point_sha256"], "Reference vector binding mismatch")
                point, check = self.point(directory, "reference_upper_vector.npz", model, mask)
                upper = sum((Q(c)*Q(x) for c, x in zip(cost, point)), Q(0))
                saved = identities[str(week)]
                require(fraction(saved["lower_MWh"]) == lower and fraction(saved["upper_MWh"]) == upper == fraction(binding["reference_upper_MWh"]),
                        "Reference energy bounds mismatch")
                prior = self.js(R + f"fresh_reference_postrun_review/week_{week}.json")
                require(prior["status"] == "INDEPENDENT_EXPANDED_BINARY_REFERENCE_PASS" and fraction(prior["exact_fossil_MWh"]) == upper,
                        "Native reference review mismatch")
                self.review_bindings(prior["replayed_files_sha256"])
                scaled = upper*Q(101, 100)
                cap = -(-scaled.numerator // scaled.denominator)
                require(cap == CAPS[week] == binding["source_cap_MWh"] == self.js(FRESH + f"/targets/week_{week}_cap.json")["budget_MWh"],
                        "Reference cap construction mismatch")
                require(0 < lower <= upper and binding["reference_native_no_cap_check"]["pass"], "Invalid reference interval/native archived flag")
                reference_bounds[week] = (lower, upper)
                report = dict(status="REFERENCE_EXACT_ENERGY_BOUNDS_PASS", relation=relation, lower=lower_report,
                              verified_upper_MWh=packed(upper), original_binary_point=check, native_physical_assembler_rerun=False)
            else:
                mip = self.js(directory + "/mip/result.json"); require(mip == mips[case], "MIP aggregate/per-case result mismatch")
                require(mip["verdict"] == "VERIFIED_UNCAPPED_BINARY_WITNESS_EXPANDED_MODEL" and mip["prepared_manifest_sha256"] == ENERGY_MANIFEST,
                        "Required closed target upper absent")
                for name, digest in mip["model_artifacts"].items():
                    require(sha(self.path(directory + "/" + relative_name(name))) == digest, "MIP mathematical input mismatch")
                point, check = self.point(directory, "mip/recovered_vector.npz", model, mask)
                raw = self.array(directory, "mip/raw_vector.npz", "vector", ("<f8",), model.cols)
                require(bit_equal(raw[:6888], point[:6888]) and bit_equal(raw[18984:], point[18984:]), "Recovery changed P/theta bytes")
                u = point[6888:10920]
                require(all(abs(Q(raw[6888+j])-Q(x)) <= TAU for j, x in enumerate(u)), "Raw U outside recovery tolerance")
                for t in range(168):
                    for j in range(24):
                        change = 0 if t == 0 else u[t*24+j]-u[(t-1)*24+j]
                        require(point[10920+t*24+j] == max(change, 0) and point[14952+t*24+j] == max(-change, 0), "Noncanonical Y/Z recovery")
                raw_check = self.v.check_point(model, raw, (0,)*model.cols, TAU)
                require(raw_check["expanded_pass"], "Raw continuous diagnostic fails expanded model")
                saved_check = self.js(directory + "/mip/exact_point_check.json")
                require(check["strict_pass"] == saved_check["strict_pass"] == mip["exact_strict_pass"] and
                        all(fraction(check[k]) == fraction(saved_check[k]) for k in ("maximum_column_violation", "maximum_row_violation")),
                        "Target point exact diagnostics differ")
                require(mip["native_no_cap_pass"] and self.js(directory + "/mip/native_no_cap_check.json")["pass"], "Archived native check failed")
                upper = sum((Q(c)*Q(x) for c, x in zip(cost, point)), Q(0))
                require(upper == fraction(mip["verified_upper_MWh"]) == fraction(mip["candidate_fossil_MWh"]), "Target exact energy differs")
                saved = next(x for x in brackets if x["case"] == case); li, ui = reference_bounds[week]
                require(saved["week"] == week and saved["finite_uncapped_feasibility_established"] and saved["upper_MWh"] is not None,
                        "Wrong week or absent finite upper")
                require(all(fraction(saved[k]) == x for k, x in (("lower_MWh", lower), ("upper_MWh", upper),
                        ("identity_lower_MWh", li), ("identity_reference_upper_MWh", ui))), "Selected energy bounds differ")
                require(saved["positive_lower_penalty_necessary_if_target_nonempty"] == (lower > ui), "Penalty sign claim differs")
                computed = ranges(li, ui, lower, upper)
                for key, (lo, hi) in computed.items():
                    require(fraction(saved[key]["lower"]) == lo and fraction(saved[key]["upper"]) == hi, "Exact interval differs: " + key)
                interval = dict(case=case, week=week, **{k: dict(lower=packed(lo), upper=packed(hi),
                              outward_display=[outward6(lo), outward6(hi, True)]) for k, (lo, hi) in computed.items()})
                interval_records.append(interval)
                cap_checks.append(dict(case=case, cap_MWh=CAPS[week], expanded_cap=packed(Q(CAPS[week])+TAU),
                    uncapped_lower_MWh=packed(lower), lower_proves_cap_infeasible=lower > Q(CAPS[week])+TAU,
                    historical_verdict="UNKNOWN" if case == "seed_26093211" else "CERTIFIED_INFEASIBLE_EXPANDED_MODEL"))
                report = dict(status="TARGET_EXACT_ENERGY_BOUNDS_PASS", relation=relation, lower=lower_report,
                    verified_upper_MWh=packed(upper), original_binary_point=check, raw_continuous_point=raw_check,
                    P_theta_bytes_preserved=True, canonical_YZ=True, intervals=interval, native_physical_assembler_rerun=False)
            self.save("energy_" + case, report)
        require([x["case"] for x in interval_records] == list(TARGETS), "Incomplete intervals")
        unresolved = next(x for x in cap_checks if x["case"] == "seed_26093211")
        require(not unresolved["lower_proves_cap_infeasible"], "Historical UNKNOWN diagnostic changed unexpectedly")
        self.save("fresh_intervals", dict(status="FOUR_FRESH_INTERVALS_REPLAYED", records=interval_records, ordinary_denominator=4))
        self.save("historical_caps", dict(status="HISTORICAL_CAP_LEDGER_PRESERVED", records=cap_checks, ledger_mutated=False))

    def subsets(self):
        outcomes = self.js(SUBSET + "/outcomes.json")
        require([x["id"] for x in outcomes] == list(SUBSET_CASES), "Subset denominator/order changed")
        for case in HOD_CASES:
            parent = HOD + "/" + case; full = self.model(parent); labels = self.labels(parent); meta = self.metadata(parent)
            require((full.rows, full.cols) == (34681, 23016), "HOD full-parent dimensions")
            full_mask(self.array(parent, "integrality.npz", "integrality"))
            self.cap_row(full, labels, 23195, self.fossil_cost(meta, full.cols))
            for rule in RULES:
                name = case + "__" + rule; directory = SUBSET + "/" + name; old = FIXED + "/models/" + case + "/" + rule
                for filename in ("matrix.npz", "bounds.npz", "integrality.npz", "model_metadata.json", "row_metadata.csv.gz", "retained_parent_rows.npz"):
                    require(sha(self.path(directory + "/" + filename)) == sha(self.path(old + "/" + filename)), "Copied fixed template changed")
                binding = self.js(directory + "/model_binding.json")
                require(historical_relative(binding["source_directory"] + "/matrix.npz") == old + "/matrix.npz", "Wrong fixed-template source binding")
                model = self.model(directory); names = self.labels(directory); kept = selected_rows(full, labels, rule)
                require(self.array(directory, "retained_parent_rows.npz", "rows") == kept, "Fixed row mask mismatch")
                verify_row_subset(model, full, names, labels, kept, "original_row")
                mask = self.array(directory, "integrality.npz", "integrality"); full_mask(mask)
                reduced_meta = self.metadata(directory)
                for key in ("unit_names", "thermal_unit_names", "bus_ids", "offsets", "hours", "units", "thermal_units", "buses", "column_order", "fossil_units"):
                    require(reduced_meta[key] == meta[key], "Subset column/native metadata changed")
                self.cap_row(model, names, 23195, self.fossil_cost(meta, model.cols))
                counts = Counter(x["family"] for x in names)
                if rule == "locality48":
                    require(counts["minimum_up"] == 1023 and counts["minimum_down"] == 1001, "Locality dwell count")
                point = self.array(directory, "returned_vector.npz", "vector", ("<f8",), model.cols)
                check = self.v.check_point(model, point, (0,)*model.cols, TAU)
                nonbinary = sum(flag and x not in (0., 1.) for flag, x in zip(mask, point))
                require(check["expanded_pass"] and check["binary_coordinates"] == 0 and not check["strict_pass"] and
                        nonbinary == NONBINARY_COUNTS[name], "Expected continuous-only expanded point not reproduced")
                require(check == self.js(directory + "/exact_continuous_point.json"), "Stored subset exact-point report mismatch")
                result = self.js(directory + "/result.json")
                require(result == next(x for x in outcomes if x["id"] == name) and result["verdict"] == "VERIFIED_EXPANDED_CONTINUOUS_POINT" and
                        result["original_binary_model_not_solved"] and not result["exact_strict_continuous_pass"], "Subset result label mismatch")
                self.save("subset_" + name, dict(status="EXPANDED_CONTINUOUS_TEMPLATE_ADMISSION", point_check=check,
                    actual_binary_coordinates_checked=0, original_mask_validated=True, exact_nonbinary_original_states=nonbinary,
                    binary_witness_established=False, rows=len(kept), columns=model.cols, unchanged_static_network_cap_box=True,
                    fixed_template_linear_separator_excluded=True, strict_nominal_feasibility_established=False))
        claims = self.js(SUBSET + "/positive_controls.json")
        require((claims["full_control_denominator"], claims["control_rule_denominator"]) == (2, 4) and len(claims["controls"]) == 4,
                "Control denominator mismatch")
        controls = []
        for case in ("january_identity", "seed_26100200"):
            parent = HOD + "/" + case; model = self.model(parent); labels = self.labels(parent); meta = self.metadata(parent)
            self.cap_row(model, labels, 23195, self.fossil_cost(meta, model.cols))
            mask = self.array(parent, "integrality.npz", "integrality"); point, check = self.point(parent, "constructive_vector.npz", model, mask)
            for rule in RULES:
                kept = selected_rows(model, labels, rule)
                with self.path(SUBSET + f"/control_{case}_{rule}_rows.csv").open(encoding="utf-8-sig", newline="") as stream:
                    reader = csv.DictReader(stream); require(reader.fieldnames == ["subset_row", "parent_row"], "Control mapping columns")
                    mapping = list(reader)
                require([(int(x["subset_row"]), int(x["parent_row"])) for x in mapping] == list(enumerate(kept)), "Control rule-map mismatch")
                matches = [x for x in claims["controls"] if x["case"] == case and x["rule"] == rule]; require(len(matches) == 1, "Duplicate/missing control claim")
                claim = matches[0]
                require(claim["point_sha256"] == sha(self.path(parent + "/constructive_vector.npz")) and
                        claim["original_full_model_matrix_sha256"] == sha(self.path(parent + "/matrix.npz")) and
                        claim["inherited_exact_expanded_binary"] and claim["all_columns_boxes_unchanged"] and
                        not claim["strict_positive_claim"] and claim["rows"] == len(kept), "Control inheritance claim mismatch")
                controls.append(dict(case=case, rule=rule, full_point=check, inherited_by_exact_row_deletion=True,
                    retained_rows=len(kept), own_bounds_sha256=sha(self.path(parent + "/bounds.npz")), own_vector_sha256=claim["point_sha256"]))
        self.save("HOD_control_inheritances", dict(status="TWO_FULL_BINARY_CONTROLS_FOUR_RULE_INHERITANCES_PASS", records=controls,
                  full_control_denominator=2, inheritance_denominator=4, new_energy_targets=0))

    def finish(self, started):
        require(self.h.relative_manifest(self.root, self.root / "FILE_MANIFEST.csv", self.manifest_digest) == self.package,
                "Package payload changed during replay")
        require(self.inventory() == self.initial_inventory, "Package file set changed during replay")
        for name, digest, count, mode, base in MANIFESTS:
            self.check_manifest(name, digest, count, mode, base)
        require(self.h.relative_manifest(self.root / ADDENDUM, self.path(ADDENDUM + "/FILE_MANIFEST.csv"), ADDENDUM_SHA) == self.addendum,
                "Native addendum changed")
        self.save("summary", dict(status="NEW_CLOSED_RESULTS_PORTABLE_REPLAY_PASS", lower_bounds=6,
            reference_binary_uppers=2, target_binary_uppers=4, fresh_interval_records=4, expanded_continuous_subset_points=4,
            auxiliary_full_HOD_controls=2, control_subset_inheritances=4, capped_26093211_verdict="UNKNOWN",
            optimization_calls=0, network_calls=0, native_physical_assembler_calls=0, all_package_hashes_unchanged=True,
            package_file_set_unchanged=True, package_manifest_sha256=self.manifest_digest, package_evidence_commit=self.evidence_commit,
            package_payloads=len(self.package), accessed_payloads=len(self.used), wrapper_sha256=sha(Path(__file__)),
            helper_sha256=HELPER_SHA, kernel_sha256=KERNEL_SHA, python=sys.version, elapsed_s=time.perf_counter()-started,
            exact_optimality_claim=False, second_machine_execution_claim=False,
            scope="Fixed archived expanded-model mathematics and provenance; no new scientific cases, optimization, physical reconstruction or strict nominal upper claims."))


def focused_checks(h, v, fixture_parent):
    """Small synthetic tests of new routing; no frozen evidence is mutated."""
    tests = []
    def rejects(name, operation):
        try:
            operation()
        except (ValueError, KeyError):
            tests.append(name)
        else:
            raise ValueError("Expected rejection: " + name)
    toy = SimpleNamespace(rows=1, cols=1, lower=(0.,), upper=(1.,), row_lower=(.2,), row_upper=(math.inf,),
                          data=(1.,), indices=(0,), indptr=(0, 1))
    for label, dual, nominal in (("positive_row_endpoint", 1., Q.from_float(.2)),
                                 ("imperfect_dual_requires_box", .5, Q.from_float(.2)/2),
                                 ("negative_residual_uses_upper", 2., 2*Q.from_float(.2)-1)):
        report, _ = h.objective_lower(toy, (1.,), (dual,), TAU)
        require(fraction(report["nominal_lower_bound_MWh"]) == nominal, label); tests.append(label)
    zero, _ = h.objective_lower(toy, (1.,), (0.,), TAU)
    require(fraction(zero["expanded_lower_bound_MWh"]) == -TAU, "Expanded zero-dual incorrectly clipped"); tests.append("negative_zero_dual_not_clipped")
    negative = SimpleNamespace(**{**vars(toy), "row_lower": (-math.inf,), "row_upper": (-.2,), "data": (-1.,)})
    bound, _ = h.objective_lower(negative, (1.,), (-1.,), TAU)
    require(fraction(bound["nominal_lower_bound_MWh"]) == Q.from_float(.2), "Negative row endpoint sign"); tests.append("negative_row_endpoint")
    require(project_dual(toy, (-1.,)) == (0.,), "Wrong infinite-endpoint projection"); tests.append("explicit_infinite_endpoint_projection")
    rejects("nonfinite_dual", lambda: project_dual(toy, (math.nan,)))
    rejects("projected_mask_not_original", lambda: full_mask(PROJECTED))
    model = v.validate_model(v.Model(1, 1, (1.,), (0,), (0, 1), (0.,), (1.,), (0.,), (1.,)))
    continuous = v.check_point(model, (.5,), (0,), TAU); binary = v.check_point(model, (.5,), (1,), TAU)
    require(continuous["expanded_pass"] and continuous["binary_coordinates"] == 0 and not binary["expanded_pass"], "Fractional mask distinction")
    tests.append("zero_mask_never_binary_witness")
    computed = ranges(Q(2), Q(4), Q(6), Q(10))
    require(computed["optimum_difference_MWh"] == (2, 8) and computed["target_optimum_excess_over_chosen_incumbent_MWh"] == (2, 6) and
            computed["optimal_relative_penalty"] == (Q(1, 2), 4), "Wrong optimum interval denominator")
    require(ranges(Q(2), Q(4), Q(3), Q(5))["optimum_difference_MWh"] == (-1, 3) and ranges(Q(2), Q(4), Q(3), None) is None,
            "Crossing interval or missing upper filtered")
    tests.extend(("optimum_vs_incumbent_interval", "crossing_zero_and_no_upper"))
    require(outward6(Q(-1, 3000000)) == "-0.000001" and outward6(Q(-1, 3000000), True) == "0.000000" and
            outward6(Q(1, 3000000)) == "0.000000" and outward6(Q(1, 3000000), True) == "0.000001", "Outward negative/positive rounding")
    tests.append("outward_rounding_both_signs")
    boundary = SimpleNamespace(rows=4, cols=23016, indptr=(0, 2, 4, 6, 8),
        indices=(6888+59*24, 6888+60*24, 6888+60*24, 10920+60*24, 14952+107*24, 6888+107*24, 6888+107*24, 6888+108*24), data=(1.,)*8)
    labels = [dict(row=str(i), family="minimum_up", hour_0based="60", uid="107_CC_1") for i in range(4)]
    require(selected_rows(boundary, labels, "locality48", False) == (1, 2), "Actual dwell support boundary")
    tests.append("locality_actual_support_not_label")
    label = [dict(row="0", family="transition", hour_0based="1", uid="101_CT_1")]
    tiny = SimpleNamespace(rows=1, cols=23016, indptr=(0, 1), indices=(6888,), data=(1.,))
    require(selected_rows(tiny, label, "two_cc", False) == (), "Other-unit transition was retained"); tests.append("two_cc_drops_other_transitions")
    rejects("path_escape", lambda: historical_relative(OLD_ROOT + "/../outside"))
    rejects("prefix_lookalike", lambda: historical_relative(OLD_ROOT + "0/src/a.py"))
    require(historical_relative(OLD_ROOT.replace("/", "\\") + "\\src\\a.py") == "src/a.py", "Windows remapping")
    tests.append("windows_prefix_normalization")
    duplicate = [dict(path="a/b", sha256="0"*64, bytes=1), dict(path="a\\b", sha256="0"*64, bytes=1)]
    rejects("normalized_manifest_duplicate", lambda: validate_records(duplicate))
    rejects("missing_historical_unknown", lambda: h.fresh_ledger([]))
    with tempfile.TemporaryDirectory(prefix="new-replay-fixtures-", dir=fixture_parent) as directory:
        p = Path(directory); (p / "duplicate.json").write_text('{"x":1,"x":2}', encoding="utf-8")
        rejects("duplicate_json_key", lambda: read_json(p / "duplicate.json"))
        (p / "nonfinite.json").write_text('{"x":NaN}', encoding="utf-8")
        rejects("nonfinite_json", lambda: read_json(p / "nonfinite.json"))
    return dict(status="NEW_REPLAY_FOCUSED_CHECKS_PASS", tests=tests, optimizer_calls=0,
                unchanged_kernel_fixture_suite_rerun=False, frozen_evidence_modified=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--report-dir", type=Path, required=True)
    parser.add_argument("--expected-package-manifest-sha256", required=True)
    parser.add_argument("--package-evidence-commit", required=True)
    args = parser.parse_args()
    root, output = args.package_root.resolve(), args.report_dir.resolve()
    require(root.is_dir() and not output.exists() and not output.is_relative_to(root) and not root.is_relative_to(output),
            "Use an existing package and a new report directory outside it")
    output.mkdir(parents=True, exist_ok=False); started = time.perf_counter()
    try:
        replay = Replay(root, output, args.expected_package_manifest_sha256, args.package_evidence_commit)
        replay.save("focused_checks", focused_checks(replay.h, replay.v, output))
        replay.energy(); replay.subsets(); replay.finish(started)
    except Exception as error:
        report = dict(status="NEW_CLOSED_RESULTS_PORTABLE_REPLAY_FAILED", error_type=type(error).__name__, error=str(error),
                      optimizer_calls=0, elapsed_s=time.perf_counter()-started, partial_external_reports_preserved=True)
        with (output / "failure.json").open("x", encoding="utf-8") as stream:
            json.dump(report, stream, indent=2, allow_nan=False); stream.write("\n")
        print(json.dumps(report), flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
