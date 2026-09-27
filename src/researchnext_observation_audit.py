"""Exact unclustered input observations; no optimizer or UC certificate replay."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import struct
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/research_next/observation_audit"
SOURCE = "src/researchnext_observation_audit.py"
PROTOCOL = "docs/research_next/OBSERVATION_AUDIT_PROTOCOL.md"
HELPER = "src/research8h_standalone_verify.py"
HELPER_SHA = "708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f"
HOD = "results/research8h/hour_of_day"
FRESH = "results/research8h/fresh_january_weeks/targets"
MANIFESTS = {
    HOD: "078082667f83322d3540ad3ac215ebcc996d0d31b04fd52bfa75c1d2fd814fcc",
    FRESH: "56c5240486a8274ecb076b3aca49db236db4a7d72b865392016868119f7938dd",
}
WEEKS = (
    (1, HOD, "january_identity", (26093200, 26093201), 26100200),
    (2, FRESH, "week_2_identity", (26093210, 26093211), 26100210),
    (3, FRESH, "week_3_identity", (26093220, 26093221), 26100220),
)
FILES = ("native_inputs.npz", "model_metadata.json", "matrix.npz", "bounds.npz",
         "integrality.npz", "row_metadata.csv.gz", "permutation.csv", "preservation.json",
         "constructive_check.json")
GROUPS = (("pmin", 0, 41), ("pmax", 41, 82), ("net", 82, 83), ("nodal", 83, 107))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path):
    def unique(pairs):
        d = {}
        for key, value in pairs:
            require(key not in d, "duplicate JSON key")
            d[key] = value
        return d
    return json.loads(Path(path).read_text(encoding="utf-8-sig"), object_pairs_hook=unique,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def encoded(value):
    return json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n"


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as f:
        f.write(encoded(value))


def utc():
    return datetime.now(timezone.utc).isoformat()


def descriptor(relative):
    p = ROOT / relative
    require(p.is_file() and not p.is_symlink(), "missing or linked input: " + relative)
    return {"path": relative, "sha256": sha(p), "bytes": p.stat().st_size}


def roles(week):
    w, base, identity, ordinary, control = week
    return [(identity, "identity_self")] + [(f"seed_{s}", "ordinary") for s in ordinary] + [
        (f"seed_{control}", "class_control")]


def prepare():
    p = OUT / "prepared"
    p.mkdir(parents=True, exist_ok=False)
    save(p / "PREPARATION_STARTED.json", {"utc": utc(), "mode": "hash-only", "optimizer_calls": 0})
    bindings = {x: descriptor(x) for x in (SOURCE, PROTOCOL, HELPER)}
    require(bindings[HELPER]["sha256"] == HELPER_SHA, "NPZ reader changed")
    prefix = ROOT.as_posix() + "/"
    for base, expected in MANIFESTS.items():
        mrel = base + "/input_manifest.csv"
        bindings[mrel] = descriptor(mrel)
        require(bindings[mrel]["sha256"] == expected, "historical manifest changed")
        with (ROOT / mrel).open(encoding="utf-8-sig", newline="") as f:
            archived = list(csv.DictReader(f))
        names = [a["path"].replace("\\", "/") for a in archived]
        require(len(names) == len(set(names)), "duplicate historical path")
        mapped = {name[len(prefix):]: a for name, a in zip(names, archived) if name.startswith(prefix)}
        for week in WEEKS:
            if week[1] != base:
                continue
            for case, _ in roles(week):
                for name in FILES:
                    rel = f"{base}/{case}/{name}"
                    record = descriptor(rel)
                    require(rel in mapped and record["sha256"] == mapped[rel]["sha256"]
                            and record["bytes"] == int(mapped[rel]["bytes"]), "old binding mismatch: " + rel)
                    bindings[rel] = record
        for name in ("outcomes.json", "prepared_freeze.json"):
            rel = base + "/" + name
            bindings[rel] = descriptor(rel)
    freeze = {"schema": "observation-audit-freeze-v1", "utc": utc(), "bindings": sorted(bindings.values(), key=lambda r: r["path"]),
              "ordinary_denominator": 6, "comparison_roles": 12, "optimizer_calls": 0,
              "observations_evaluated": 0, "preparation": "selected old bindings plus new source/protocol"}
    save(p / "input_freeze.json", freeze)
    print(encoded({"prepared": str(p), "bindings": len(bindings), "freeze_sha256": sha(p / "input_freeze.json")}))


def verify_freeze():
    freeze = read_json(OUT / "prepared/input_freeze.json")
    seen = set()
    for old in freeze["bindings"]:
        rel = old["path"]
        require(rel not in seen and not Path(rel).is_absolute() and ".." not in Path(rel).parts, "unsafe/duplicate binding")
        seen.add(rel)
        require(descriptor(rel) == old, "frozen input changed: " + rel)
    require({SOURCE, PROTOCOL, HELPER} <= seen and sha(ROOT / HELPER) == HELPER_SHA, "required source binding")
    return freeze


def load_reader():
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("observation_npz_reader", ROOT / HELPER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def token(row):
    require(all(type(x) is float and math.isfinite(x) for x in row), "nonfinite/non-binary64 coordinate")
    return tuple((0.0 if x == 0 else x).hex() for x in row)


def bits(row):
    return struct.pack("<" + "d" * len(row), *row)


def counter_records(counter):
    return [{"item": key, "multiplicity": counter[key]} for key in sorted(counter)]


def observe(sequence, period=24, edge=48):
    require(len(sequence) % period == 0 and edge * 2 <= len(sequence), "invalid observation dimensions")
    days = tuple(tuple(sequence[t:t + period]) for t in range(0, len(sequence), period))
    pairs = tuple(zip(sequence, sequence[1:]))
    return {"hod": tuple(Counter(sequence[h::period]) for h in range(period)),
            "edges": (tuple(sequence[:edge]), tuple(sequence[-edge:]) if edge else ()),
            "days": Counter(days), "day_positions": days, "transitions": Counter(pairs),
            "transition_positions": pairs, "endpoints": (sequence[0], sequence[-1])}


def archive_observation(o):
    return {"hod_joint_snapshots": [counter_records(c) for c in o["hod"]],
            "ordered_fixed_edges": o["edges"], "whole_day_multiset": counter_records(o["days"]),
            "noncyclic_directed_transition_multiset": counter_records(o["transitions"]),
            "ordered_endpoints": o["endpoints"]}


def difference(a, b):
    matched = sum((a & b).values())
    return {"equal": a == b, "matched_occurrences": matched,
            "removed_occurrences": sum(a.values()) - matched, "added_occurrences": sum(b.values()) - matched}


def reconstruct(sequence, observation):
    if len(set(sequence)) != len(sequence):
        return {"status": "NOT_ESTABLISHED_DUPLICATE_JOINT_TOKENS", "unique_tokens": len(set(sequence))}
    successors = {}
    for (a, b), count in observation["transitions"].items():
        require(count == 1 and a not in successors, "unique-token transition branching")
        successors[a] = b
    first, last = observation["endpoints"]
    path, seen = [first], {first}
    while path[-1] in successors:
        nxt = successors[path[-1]]
        require(nxt not in seen, "transition cycle")
        path.append(nxt)
        seen.add(nxt)
    require(path[-1] == last and len(path) == len(sequence) and len(successors) == len(path) - 1
            and tuple(path) == tuple(sequence), "transition reconstruction failed")
    return {"status": "EXACT_SEQUENCE_RECONSTRUCTED_UNDER_DISTINCT_TOKEN_PREMISE",
            "unique_tokens": len(seen), "consumed_edges": len(successors), "reconstructed_token_ids": path}


def compare(a, b, raw_a, raw_b, order):
    hod = [difference(x, y) for x, y in zip(a["hod"], b["hod"])]
    edge_equal = a["edges"] == b["edges"]
    require(all(x["equal"] for x in hod) and edge_equal, "HOD/fixed-edge contract failed")
    days, transitions = difference(a["days"], b["days"]), difference(a["transitions"], b["transitions"])
    days.update(fixed_edge_context_equal=edge_equal, observation_equal=days["equal"] and edge_equal,
                changed_chronological_day_positions=[i for i, (x, y) in enumerate(zip(a["day_positions"], b["day_positions"])) if x != y])
    transitions.update(endpoints_equal=a["endpoints"] == b["endpoints"],
                       observation_equal=transitions["equal"] and a["endpoints"] == b["endpoints"],
                       changed_chronological_pair_positions=[i for i, (x, y) in enumerate(zip(a["transition_positions"], b["transition_positions"])) if x != y])
    return {"hod_plus_edges": {"equal": True, "per_hod": hod, "fixed_edges_equal": edge_equal},
            "whole_day_multiset_plus_edges": days, "directed_hour_transitions_plus_endpoints": transitions,
            "changed_physical_row_positions": [i for i, (x, y) in enumerate(zip(raw_a, raw_b)) if x != y],
            "changed_coordinate_counts": {name: sum(x[j] != y[j] for x, y in zip(raw_a, raw_b) for j in range(lo, hi)) for name, lo, hi in GROUPS},
            "source_continuity_breaks_after_destination_hours": [i for i in range(len(order)-1) if order[i+1] != order[i]+1],
            "literal_changed_adjacent_source_pairs_after_destination_hours": [i for i in range(len(order)-1) if (order[i], order[i+1]) != (i, i+1)]}


def read_case(reader, directory, week):
    native = reader.read_npz(directory / "native_inputs.npz", ("pmin", "pmax", "net", "rows", "source_hour", "nodal"))
    for key, width in (("pmin", 41), ("pmax", 41), ("net", 1), ("nodal", 24)):
        x = native[key]
        require(x.dtype == "<f8" and x.shape == ((168,) if width == 1 else (168, width))
                and all(math.isfinite(v) for v in x.values), "native array contract: " + key)
    for key in ("rows", "source_hour"):
        require(native[key].dtype in ("<i4", "<i8") and native[key].shape == (168,), "index array contract")
    order = native["source_hour"].values
    require(sorted(order) == list(range(168)) and all(t % 24 == s % 24 for t, s in enumerate(order))
            and order[:48] == tuple(range(48)) and order[120:] == tuple(range(120, 168)), "permutation/boundary contract")
    require(native["rows"].values == tuple((week - 1)*168 + t for t in order), "native calendar rows")
    with (directory / "permutation.csv").open(encoding="utf-8-sig", newline="") as f:
        table = list(csv.DictReader(f))
    require(len(table) == 168, "CSV permutation length")
    for t, row in enumerate(table):
        require(int(row.get("new_hour_0based", row.get("local_hour_0based", -1))) == t
                and int(row["source_hour_0based"]) == order[t]
                and int(row.get("source_native_row", row.get("native_row_0based", -1))) == native["rows"].values[t], "CSV/source index mismatch")
        if "hour_of_day_0based" in row:
            require(int(row["hour_of_day_0based"]) == t % 24, "CSV HOD mismatch")
    rows = tuple(tuple(native["pmin"].values[t*41:(t+1)*41]) + tuple(native["pmax"].values[t*41:(t+1)*41])
                 + (native["net"].values[t],) + tuple(native["nodal"].values[t*24:(t+1)*24]) for t in range(168))
    metadata = read_json(directory / "model_metadata.json")
    require(metadata["hours"] == 168 and metadata["units"] == 41 and metadata["buses"] == 24
            and len(set(metadata["unit_names"])) == 41 and len(set(metadata["bus_ids"])) == 24
            and metadata["offsets"] == {"P": 0, "U": 6888, "Y": 10920, "Z": 14952, "theta": 18984}, "model coordinate ordering")
    model = reader.load_model(directory)
    require((model.rows, model.cols) == (34681, 23016), "model shape")
    mask = reader.read_npz(directory / "integrality.npz", ("integrality",))["integrality"]
    require(mask.dtype == "|u1" and mask.shape == (23016,) and mask.values == (0,)*6888 + (1,)*12096 + (0,)*4032, "original full binary mask")
    with gzip.open(directory / "row_metadata.csv.gz", "rt", encoding="utf-8-sig", newline="") as f:
        labels = list(csv.DictReader(f))
    require(len(labels) == model.rows and all(int(row["row"]) == i for i, row in enumerate(labels)), "row-label ordering")
    keys = [(r["family"], int(r["hour_0based"]), r["uid"]) for r in labels]
    require(len(set(keys)) == len(keys), "ambiguous row-label key")
    return {"rows": rows, "order": order, "metadata": metadata, "model": model, "keys": keys, "labels": labels}


def prove_package_mapping(identity, case):
    a, b, order = identity["model"], case["model"], case["order"]
    require(identity["metadata"] == case["metadata"] and identity["labels"] == case["labels"], "metadata mismatch")
    require((a.data, a.indices, a.indptr) == (b.data, b.indices, b.indptr), "coefficient matrix changed")
    inverse = [0]*168
    for t, s in enumerate(order):
        inverse[s] = t
        require(bits(case["rows"][t]) == bits(identity["rows"][s]), "physical package byte mismatch")
    require(all(bits(case["rows"][inverse[t]]) == bits(identity["rows"][t]) for t in range(168)), "inverse package roundtrip")
    for side in ("lower", "upper"):
        av, bv = getattr(a, side), getattr(b, side)
        require(all(bv[t*41+j] == av[order[t]*41+j] for t in range(168) for j in range(41))
                and bv[6888:] == av[6888:], "column-bound package mismatch")
    lookup = {key: i for i, key in enumerate(identity["keys"])}
    for i, (family, hour, uid) in enumerate(case["keys"]):
        key = (family, order[hour], uid) if hour >= 0 else (family, hour, uid)
        require(key in lookup, "mapped row label absent")
        j = lookup[key]
        require((b.row_lower[i], b.row_upper[i]) == (a.row_lower[j], a.row_upper[j]), "row-bound package mismatch")
    return {"all_107_coordinates_bitwise_forward_inverse": True, "coefficient_matrix_equal": True,
            "all_row_and_column_bounds_mapped": True, "full_binary_coordinates": 12096}


def run():
    initial = time.perf_counter()
    freeze = verify_freeze()
    directory = OUT / "run01"
    directory.mkdir(exist_ok=False)
    save(directory / "RUN_STARTED.json", {"utc": utc(), "freeze_sha256": sha(OUT / "prepared/input_freeze.json"),
                                          "python": sys.version, "optimizer_calls": 0})
    reader = load_reader()
    ledger = [{"week": w[0], "case": case, "role": role, "status": "NOT_EVALUATED"} for w in WEEKS for case, role in roles(w)]
    start = time.perf_counter()
    failure = None
    try:
        labels = {}
        for base in MANIFESTS:
            for row in read_json(ROOT / base / "outcomes.json"):
                require(row["case"] not in labels, "duplicate old verdict")
                labels[row["case"]] = row["verdict"]
        for week in WEEKS:
            w, base, identity_name, ordinary, control = week
            if time.perf_counter() - start >= 300:
                break
            identity = read_case(reader, ROOT / base / identity_name, w)
            require(identity["order"] == tuple(range(168)), "identity order")
            dictionary = sorted(set(map(token, identity["rows"])))
            ids = {value: i for i, value in enumerate(dictionary)}
            coordinate_names = [f"{g}:{u}" for g in ("pmin", "pmax") for u in identity["metadata"]["unit_names"]] + ["net"] + [f"nodal:{b}" for b in identity["metadata"]["bus_ids"]]
            save(directory / f"week_{w}_dictionary.json", {"coordinate_names": coordinate_names, "canonical_107_hex_rows": dictionary,
                                                        "id_rule": "lexicographically sorted full numeric content; zero normalized"})
            seq = tuple(ids[token(row)] for row in identity["rows"])
            observation = observe(seq)
            require(encoded(archive_observation(observation)) == encoded(archive_observation(observe(seq))), "nondeterministic identity serialization")
            for case_name, role in roles(week):
                if time.perf_counter() - start >= 300:
                    break
                record = next(r for r in ledger if r["week"] == w and r["case"] == case_name)
                record["status"] = "IN_PROGRESS"
                case = identity if case_name == identity_name else read_case(reader, ROOT / base / case_name, w)
                mapping = prove_package_mapping(identity, case)
                actual = tuple(ids[token(row)] for row in case["rows"])
                observed = observe(actual)
                result = {"week": w, "case": case_name, "role": role, "mapping": mapping,
                          "observations": archive_observation(observed), "sequence_token_ids_PROVENANCE_ONLY": actual,
                          "reconstruction": reconstruct(actual, observed),
                          "comparison": compare(observation, observed, identity["rows"], case["rows"], case["order"]),
                          "published_comparator": "PUBLISHED_COMPARATOR_NOT_EXECUTED"}
                if role == "ordinary":
                    expected = "UNKNOWN" if case_name == "seed_26093211" else "CERTIFIED_INFEASIBLE_EXPANDED_MODEL"
                    require(labels[case_name] == expected, "archived contextual verdict changed")
                    result["inherited_binary_verdict_NOT_RECHECKED"] = labels[case_name]
                save(directory / f"{case_name}.json", result)
                record.update(status="AUDITED", report=f"{case_name}.json")
    except Exception as error:
        failure = {"type": type(error).__name__, "message": str(error)}
        for record in ledger:
            if record["status"] == "IN_PROGRESS":
                record["status"] = "ERROR"
    phase_elapsed = time.perf_counter() - start
    for record in ledger:
        if record["status"] == "NOT_EVALUATED":
            record["status"] = "NOT_EVALUATED_AFTER_ERROR" if failure else "NOT_EVALUATED_PHASE_LIMIT"
    verify_freeze()
    summary = {"status": "FAILED" if failure else "COMPLETE" if all(r["status"] == "AUDITED" for r in ledger) else "PARTIAL_PHASE_LIMIT",
               "ordinary_denominator": 6, "control_roles": 6, "ledger": ledger, "failure": failure,
               "phase_elapsed_seconds": phase_elapsed, "phase_soft_limit_seconds": 300,
               "initial_validation_seconds": start - initial, "utc": utc(), "input_bindings": len(freeze["bindings"]),
               "optimizer_calls": 0, "clustering_calls": 0, "UC_math_replays": 0, "native_CSV_reconstruction": False,
               "published_comparator": "PUBLISHED_COMPARATOR_NOT_EXECUTED",
               "scope": "Post-label exact unclustered information audit; not method performance or general sufficiency."}
    save(directory / "summary.json", summary)
    print(encoded(summary))
    return 0 if summary["status"] == "COMPLETE" else 1


def fixtures():
    tests = []
    def check(name, ok):
        require(ok, name)
        tests.append(name)
    z, nz = (0.0,)*107, (-0.0,)+(0.0,)*106
    check("signed_zero_numeric_equal_bytes_distinct", token(z) == token(nz) and bits(z) != bits(nz))
    changed = z[:-1] + (1.0,)
    check("coordinate_107_is_observed", token(z) != token(changed))
    a, b = [(0., 0.), (1., 1.)], [(0., 1.), (1., 0.)]
    check("joint_not_marginal", all(Counter(x[j] for x in a) == Counter(x[j] for x in b) for j in range(2)) and Counter(map(token, a)) != Counter(map(token, b)))
    seq, swapped = tuple(range(8)), (0, 1, 4, 5, 2, 3, 6, 7)
    x, y = observe(seq, 2, 2), observe(swapped, 2, 2)
    check("whole_day_permutation_retains_hod_days_edges", x["hod"] == y["hod"] and x["days"] == y["days"] and x["edges"] == y["edges"])
    check("whole_day_permutation_changes_raw_transitions", x["transitions"] != y["transitions"])
    check("multiplicity_is_not_set", difference(Counter([1, 1, 2]), Counter([1, 2, 2])) == {"equal": False, "matched_occurrences": 2, "removed_occurrences": 1, "added_occurrences": 1})
    check("noncyclic_edge_count", sum(x["transitions"].values()) == 7 and (7, 0) not in x["transitions"])
    check("unique_path_reconstruction", reconstruct(seq, x)["consumed_edges"] == 7)
    malformed = dict(x, endpoints=(0, 6))
    try:
        reconstruct(seq, malformed)
    except ValueError:
        check("incorrect_endpoint_rejected", True)
    else:
        raise ValueError("incorrect endpoint accepted")
    repeated = (0, 1, 0, 2)
    check("duplicate_token_premise_not_claimed", reconstruct(repeated, observe(repeated, 2, 0))["status"] == "NOT_ESTABLISHED_DUPLICATE_JOINT_TOKENS")
    save(OUT / "implementation_fixtures.json", {"status": "PASS", "tests": tests, "source_sha256": sha(Path(__file__)),
                                                "scientific_arrays_read": 0, "optimizer_calls": 0, "utc": utc()})
    print(encoded({"status": "PASS", "tests": len(tests)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--fixtures-only", action="store_true")
    mode.add_argument("--prepare-only", action="store_true")
    mode.add_argument("--run-prepared", action="store_true")
    args = parser.parse_args()
    if args.fixtures_only:
        fixtures()
    elif args.prepare_only:
        prepare()
    else:
        sys.exit(run())
