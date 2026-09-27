"""Independent root replay of six frozen, nonadaptive proof candidates.

Uses only the shared standard-library archive/certificate checker, never the
producer's model-selection or candidate-construction functions. No optimizer.
"""
import csv
import gzip
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("root_ray_verifier", ROOT / "src/research8h_standalone_verify.py")
v = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = v
spec.loader.exec_module(v)
BASE = ROOT / "results/research8h/hod_fixed_ray_transfer"
TAU = Fraction.from_float(1e-5)
TEMPORAL = {"minimum_up", "minimum_down", "transition", "exclusive_transition"}


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def labels(path):
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sparse_row(model, row):
    return {model.indices[k]: model.data[k] for k in range(model.indptr[row], model.indptr[row + 1]) if model.data[k] != 0}


def ray(data):
    values = {}
    for item in data["multipliers"]:
        assert item["row"] not in values
        values[item["row"]] = Fraction.from_float(float.fromhex(item["value_hex"]))
    return values


manifest = read(BASE / "input_manifest.json")
before = {}
for entry in manifest:
    path = Path(entry["path"])
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == entry["sha256"] and path.stat().st_size == entry["bytes"]
    before[str(path)] = digest
assert len(manifest) == 106
assert v.sha(BASE / "input_manifest.json") == "3753fdcd4bb9d4f04c45f538631f019e54ff17d5c834266d0807a1353b89366a"
summary = read(BASE / "summary.json")
assert len(summary["candidates"]) == 6
records = []
for stored in summary["candidates"]:
    candidate_dir = BASE / "candidates" / stored["id"]
    candidate = read(candidate_dir / "candidate.json")
    target_dir = BASE / candidate["model_directory"]
    target = v.load_model(target_dir)
    parent_dir = ROOT / "results/research8h/hour_of_day" / candidate["case"]
    # Resolve the actual archived full parent from the frozen model metadata path.
    metadata = read(target_dir / "model_metadata.json")
    parent_candidates = [Path(x["path"]).parent for x in manifest if Path(x["path"]).name == "matrix.npz" and candidate["case"] in Path(x["path"]).parts and "hod_fixed_ray_transfer" not in Path(x["path"]).parts]
    parent_candidates = [p for p in parent_candidates if (p / "model_metadata.json").exists()]
    assert len(parent_candidates) >= 1
    parent_dir = parent_candidates[0]
    parent = v.load_model(parent_dir)
    parent_labels = labels(parent_dir / "row_metadata.csv.gz")
    target_labels = labels(target_dir / "row_metadata.csv.gz")
    assert parent.rows == 34681 and target.cols == parent.cols == 23016
    expected_rows = []
    for r, lab in enumerate(parent_labels):
        family = lab["family"]
        keep = True
        if candidate["rule"] == "two_cc":
            keep = family not in TEMPORAL or lab["uid"] in {"107_CC_1", "118_CC_1"}
        elif family in {"minimum_up", "minimum_down"}:
            columns = list(sparse_row(parent, r))
            assert columns and all(6888 <= j < 18984 for j in columns)
            hours = [((j - 6888) % 4032) // 24 for j in columns]
            keep = all(60 <= t <= 107 for t in hours)
        if keep:
            expected_rows.append(r)
    actual_rows = v.read_npz(target_dir / "retained_parent_rows.npz", ("rows",))["rows"].values
    assert tuple(expected_rows) == actual_rows
    assert target.rows == (19985 if candidate["rule"] == "two_cc" else 28689)
    assert target.lower == parent.lower and target.upper == parent.upper
    for local, original in enumerate(expected_rows):
        assert sparse_row(target, local) == sparse_row(parent, original)
        assert (target.row_lower[local], target.row_upper[local]) == (parent.row_lower[original], parent.row_upper[original])
        assert int(target_labels[local]["original_row"]) == original
    source_path = Path(candidate["source_certificate"])
    source_values = ray(read(source_path))
    source_model = v.load_model(source_path.parent)
    source_labels = labels(source_path.parent / "row_metadata.csv.gz")
    actual_values = ray(candidate)
    with (candidate_dir / "coordinate_mapping.csv").open(encoding="utf-8", newline="") as handle:
        mapped = list(csv.DictReader(handle))
    assert len(mapped) == len(actual_values)
    mapped_source = set()
    for item in mapped:
        sr, tr = int(item["source_ray_row"]), int(item["target_subset_row"])
        assert sr not in mapped_source
        mapped_source.add(sr)
        assert source_values[sr] == actual_values[tr] == Fraction.from_float(float.fromhex(item["value_hex"]))
        assert sparse_row(source_model, sr) == sparse_row(target, tr)
        assert tuple(source_labels[sr][key] for key in ("family", "hour_0based", "uid")) == tuple(target_labels[tr][key] for key in ("family", "hour_0based", "uid"))
    dropped = read(candidate_dir / "dropped_source_entries.json")
    dropped_rows = {x["source_ray_row"] for x in dropped}
    assert mapped_source.isdisjoint(dropped_rows) and mapped_source | dropped_rows == set(source_values)
    for item in dropped:
        assert source_values[item["source_ray_row"]] == Fraction.from_float(float.fromhex(item["value_hex"]))
    report = v.check_ray(target, actual_values, TAU)
    assert report == stored["verification"]
    assert report["status"] == "VALID_NONSEPARATING_RAY" and not report["strict_pass"] and not report["expanded_pass"]
    records.append({"id": stored["id"], "rows": target.rows, "mapped_coefficients": len(mapped), "status": report["status"], "expanded_gap": report["expanded_separation_gap"]})
for path, digest in before.items():
    assert v.sha(Path(path)) == digest
output = {"status": "PASS_COMPLETE", "utc": datetime.now(timezone.utc).isoformat(), "frozen_bindings": len(manifest), "optimizer_calls": 0, "candidate_replays": records, "limitations": "Shared standalone mathematical checker; independent row-support and unchanged-coefficient mapping audit. A null certificate is not a feasibility witness. No minimum-support or information claim."}
destination = BASE / "root_independent_review.json"
with destination.open("x", encoding="utf-8") as handle:
    json.dump(output, handle, indent=2)
print(json.dumps({"status": output["status"], "bindings": len(manifest), "six_nulls_reproduced": len(records), "optimizer_calls": 0}))
