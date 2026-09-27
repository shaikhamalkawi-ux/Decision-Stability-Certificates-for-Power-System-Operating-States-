"""Read-only byte/schema/transport review; does not import the adapter or solve."""
import gzip
import hashlib
import json
import math
import time
from collections import Counter
from pathlib import Path, PurePosixPath

BASE = Path(__file__).resolve().parent
ARCHIVE = BASE / "prepared01"
EXPECTED = "8cf0b37220f521cd1365c4a0ad05199bafb0a634eeb28cc0642c1e31b4c3b205"

def sha(data):
    return hashlib.sha256(data).hexdigest()

def check(ok, message):
    if not ok:
        raise ValueError(message)

def main():
    start = time.perf_counter()
    manifest_bytes = (ARCHIVE / "manifest.json").read_bytes()
    check(sha(manifest_bytes) == EXPECTED, "Trusted manifest mismatch")
    manifest = json.loads(manifest_bytes)
    check(manifest["schema"] == "orlib-prepared-manifest-v1", "Manifest schema")
    snapshots = {"manifest.json": manifest_bytes}
    folded = set()
    for item in manifest["files"]:
        name = item["path"]
        p = PurePosixPath(name)
        check(not p.is_absolute() and "\\" not in name and ":" not in name
              and all(x not in (".", "..") for x in p.parts), "Unsafe path")
        check(name.casefold() not in folded, "Duplicate/case alias")
        folded.add(name.casefold())
        path = ARCHIVE.joinpath(*p.parts)
        check(not path.is_symlink() and path.resolve().is_relative_to(ARCHIVE.resolve()), "Link/path escape")
        b = path.read_bytes()
        check(len(b) == item["bytes"] and sha(b) == item["sha256"], "Payload mismatch: " + name)
        snapshots[name] = b
    check(len(manifest["files"]) == 25, "Payload denominator")
    check({p.relative_to(ARCHIVE).as_posix() for p in ARCHIVE.rglob("*") if p.is_file()} == set(snapshots), "File inventory")
    descriptor = json.loads(snapshots["descriptor.json"])
    case = json.loads(snapshots["normalized_case.json"])
    raw_bytes = gzip.decompress(snapshots["selected_case.json.gz"])
    check(sha(raw_bytes) == "3cfa5d6f0135e732edd7cb08f887cda0c7e56b0b8e766185d05b52e0ee1f3308", "Raw case bytes")
    raw = json.loads(raw_bytes)
    check(case["load"] == raw["Buses"]["b1"]["Load (MW)"], "Raw load normalization")
    check(case["reserve"] == raw["Reserves"]["r1"]["Amount (MW)"], "Raw reserve normalization")
    check("Power balance penalty ($/MW)" not in raw["Parameters"] and case["penalty"] == [1000.0] * 24, "Declared native default penalty")
    check(case["horizon"] == 24 and len(case["units"]) == 10, "Selected case dimensions")
    check(descriptor["solver_calls"] == 0 and descriptor["status"] == "PREPARED_NOT_SOLVED", "Preparation-only descriptor")
    check(descriptor["runtime_JuMP_matrix_equivalence"] == "NOT_TESTED", "Runtime-export scope")
    identity = list(range(24))
    orders = {"identity": identity, "reverse_4_19": identity[:4] + identity[4:20][::-1] + identity[20:],
              "rotate_left1_4_19": identity[:4] + identity[5:20] + [4] + identity[20:]}
    models = {}
    records = []
    for case_name, order in orders.items():
        check(sorted(order) == identity and order[:4] == identity[:4] and order[20:] == identity[20:], "Fixed boundary order")
        original_packages = list(zip(case["load"], case["reserve"], case["penalty"]))
        transported = [original_packages[s] for s in order]
        check(Counter(transported) == Counter(original_packages), "Complete hourly package multiset")
        for variant in ("native_penalized", "hard_service"):
            name = case_name + "__" + variant
            m = json.loads(snapshots[name + ".json"])
            models[name] = m
            check(m["order"] == order and m["variant"] == variant and m["horizon"] == 24, "Model order/variant")
            check(len(m["rows"]) == 4384 and len(m["columns"]) == 2472 and m["binary_count"] == 960, "Model dimensions")
            columns = {c["name"]: c for c in m["columns"]}
            rows = {r["name"]: r for r in m["rows"]}
            check(len(columns) == 2472 and len(rows) == 4384, "Unique coordinate names")
            binary_names = {c["name"] for c in m["columns"] if c["binary"]}
            expected_binary = {f"{f}:g{g}:{t}" for f in ("U", "Y", "Z", "D") for g in range(10) for t in range(24)}
            check(binary_names == expected_binary, "Complete original four-family binary mask")
            for c in m["columns"]:
                check(all(math.isfinite(c[k]) for k in ("lower", "upper", "objective")) and c["lower"] <= c["upper"], "Finite ordered column bounds/cost")
                if c["binary"]:
                    check(c["lower"] == 0 and c["upper"] == 1, "Binary box")
            for r in m["rows"]:
                indices = [j for j, a in r["coefficients"]]
                check(indices == sorted(set(indices)) and all(0 <= j < 2472 and math.isfinite(a) and a != 0 for j, a in r["coefficients"]), "Sparse coordinate validity")
                check(all(r[k] is None or math.isfinite(r[k]) for k in ("lower", "upper")), "Row endpoint validity")
            for t, (load, reserve, penalty) in enumerate(transported):
                check(rows[f"net_injection:{t}"]["lower"] == load == rows[f"net_injection:{t}"]["upper"], "Raw load to balance")
                check(rows[f"reserve:{t}"]["lower"] == reserve and rows[f"reserve:{t}"]["upper"] is None, "Raw reserve to lower side")
                c = columns[f"C:system:{t}"]
                check(c["lower"] == 0 and c["upper"] == (load if variant == "native_penalized" else 0) and c["objective"] == penalty, "Curtailment load/penalty transport")
                for f in ("F", "N"):
                    check(columns[f"{f}:system:{t}"]["lower"] == columns[f"{f}:system:{t}"]["upper"] == 0, "Native shortfall/injection boxes")
            records.append({"model": name, "rows": 4384, "columns": 2472, "binaries": 960,
                            "moved_hour_positions": sum(t != s for t, s in enumerate(order)), "package_multiset_equal": True})
        native, hard = (models[case_name + "__" + v] for v in ("native_penalized", "hard_service"))
        check(native["rows"] == hard["rows"], "Variant rows identical")
        changed = []
        for a, b in zip(native["columns"], hard["columns"]):
            expected = dict(a)
            if a["name"].startswith("C:system:"):
                expected["upper"] = 0.0
                changed.append(a["name"])
            check(expected == b, "Variant change outside C upper bounds")
        check(len(changed) == 24, "C variant difference denominator")
    for name, m in models.items():
        baseline = models["identity__" + m["variant"]]
        order = m["order"]
        for a, b in zip(baseline["rows"], m["rows"]):
            expected = dict(a)
            if a["name"].startswith("net_injection:"):
                t = int(a["name"].split(":")[-1])
                expected["lower"] = expected["upper"] = case["load"][order[t]]
            elif a["name"].startswith("reserve:"):
                t = int(a["name"].split(":")[-1])
                expected["lower"] = case["reserve"][order[t]]
            check(expected == b, "Target modifies static/chronological row or coefficient")
        for a, b in zip(baseline["columns"], m["columns"]):
            expected = dict(a)
            if a["name"].startswith("C:system:"):
                t = int(a["name"].split(":")[-1])
                expected["objective"] = case["penalty"][order[t]]
                expected["upper"] = case["load"][order[t]] if m["variant"] == "native_penalized" else 0.0
            check(expected == b, "Target modifies undeclared column/binary/cost")
        check({k:v for k,v in m.items() if k not in ("rows", "columns", "order")} ==
              {k:v for k,v in baseline.items() if k not in ("rows", "columns", "order")}, "Undeclared model metadata change")
    check(len(descriptor["models"]) == 6 and {x["file"] for x in descriptor["models"]} == {n + ".json" for n in models}, "Descriptor denominator")
    for rel, b in snapshots.items():
        check((ARCHIVE / rel).read_bytes() == b, "Input changed during review")
    return {"status": "PASS_PREPARED_ARCHIVE", "manifest_sha256": EXPECTED, "payload_count": 25,
            "file_count_with_manifest": 26, "upstream_bound_files": 14, "models": records,
            "all_archive_bytes_unchanged": True, "model_rebuilds": 0, "optimizer_calls": 0, "witness_calls": 0,
            "scope": "Independent byte/schema/coordinate/variant/package audit; no adapter import or runtime JuMP matrix-equivalence test",
            "review_seconds": time.perf_counter() - start, "review_source_sha256": sha(Path(__file__).read_bytes())}

if __name__ == "__main__":
    report = BASE / "INDEPENDENT_PREPARED_REVIEW.json"
    check(not report.exists(), "Preserve existing review")
    try:
        result = main()
    except Exception as exc:
        result = {"status": "REVIEW_FAILURE", "error": repr(exc)}
        with report.open("x", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        raise
    with report.open("x", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
