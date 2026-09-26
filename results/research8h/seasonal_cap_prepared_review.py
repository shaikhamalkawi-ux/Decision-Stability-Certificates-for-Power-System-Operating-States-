"""Independent solver-free prepared-archive review; original artifacts are read-only."""
from __future__ import annotations
import csv
import gzip
import importlib.util
import json
import math
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/research8h/seasonal_cap_continuation"
spec = importlib.util.spec_from_file_location("standalone_review_reader", ROOT / "src/research8h_standalone_verify.py")
reader = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = reader
spec.loader.exec_module(reader)


def js(path):
    return json.loads(Path(path).read_text())


def array(path, name):
    return reader.read_npz(path, (name,))[name].values


def labels(path):
    with gzip.open(path, "rt", newline="") as stream:
        return list(csv.DictReader(stream))


def ratio(n, d):
    g = math.gcd(n, d)
    return {"numerator": str(n // g), "denominator": str(d // g), "float": n / d}


def point_audit(m, point, mask, names):
    """Independent scaled-integer arithmetic; no experimental Fraction checker."""
    values = (*m.data, *m.lower, *m.upper, *point, 1e-5,
              *(v for v in (*m.row_lower, *m.row_upper) if math.isfinite(v)))
    assert all(math.isfinite(v) for v in values)
    e = max(v.as_integer_ratio()[1].bit_length() - 1 for v in values)
    scale, square = 1 << e, 1 << (2 * e)
    def si(v):
        n, d = v.as_integer_ratio()
        return n * (scale // d)
    p = tuple(map(si, point))
    c = tuple(map(si, m.data))
    tau = si(1e-5) * scale
    assert len(mask) == len(point) == m.cols
    assert all(type(v) is int and v in (0, 1) for v in mask)
    binary = all(not flag or point[j] in (0., 1.) for j, flag in enumerate(mask))
    colmax = max(0, *(si(lo) - v for lo, v in zip(m.lower, p)), *(v - si(hi) for v, hi in zip(p, m.upper))) * scale
    rowmax = staticmax = 0
    failing = []
    for r in range(m.rows):
        lhs = sum(c[k] * p[m.indices[k]] for k in range(m.indptr[r], m.indptr[r + 1]))
        excess = max([0] + ([si(m.row_lower[r]) * scale - lhs] if math.isfinite(m.row_lower[r]) else [])
                     + ([lhs - si(m.row_upper[r]) * scale] if math.isfinite(m.row_upper[r]) else []))
        rowmax = max(rowmax, excess)
        if names[r]["family"] not in {"minimum_up", "minimum_down"}:
            staticmax = max(staticmax, excess)
        if excess > tau:
            failing.append({"row": r, "family": names[r]["family"], "hour": int(names[r]["hour_0based"]), "uid": names[r]["uid"]})
    return {"binary_exact": binary, "binary_count": sum(mask),
            "full_expanded_pass": binary and max(colmax, rowmax) <= tau,
            "full_strict_pass": binary and max(colmax, rowmax) == 0,
            "static_expanded_pass": binary and max(colmax, staticmax) <= tau,
            "maximum_column_violation": ratio(colmax, square), "maximum_row_violation": ratio(rowmax, square),
            "static_maximum_row_violation": ratio(staticmax, square), "failed_expanded_rows": failing,
            "integer_scale_exponent": e}


def row(m, r):
    return {m.indices[k]: m.data[k] for k in range(m.indptr[r], m.indptr[r + 1])}


def projection_audit(m, original, projected, meta, names):
    u, y, z, theta = (meta["offsets"][name] for name in ("U", "Y", "Z", "theta"))
    assert list(original) == [int(u <= j < theta) for j in range(m.cols)]
    assert list(projected) == [int(u <= j < y) for j in range(m.cols)]
    assert sum(original) == 12096 and sum(projected) == 4032
    assert all(m.lower[j] == 0 and m.upper[j] == 1 for j in range(u, y))
    for start in (y, z):
        assert all(m.lower[j] == 0 and m.upper[j] == 0 for j in range(start, start + 24))
        assert all(m.lower[j] == 0 and m.upper[j] == 1 for j in range(start + 24, start + 4032))
    families = {name: 0 for name in ("transition", "exclusive_transition", "minimum_up", "minimum_down")}
    for r, label in enumerate(names):
        entries = row(m, r)
        f = label["family"]
        if f not in families:
            assert all(not y <= j < theta for j in entries)
            continue
        families[f] += 1
        t, q = int(label["hour_0based"]), meta["thermal_unit_names"].index(label["uid"])
        assert 1 <= t < 168
        ut, yt, zt = u + t * 24 + q, y + t * 24 + q, z + t * 24 + q
        if f == "transition":
            assert entries == {ut: 1., ut - 24: -1., yt: -1., zt: 1.}
            assert m.row_lower[r] == m.row_upper[r] == 0
        elif f == "exclusive_transition":
            assert entries == {yt: 1., zt: 1.}
            assert m.row_lower[r] == -math.inf and m.row_upper[r] == 1
        else:
            auxiliary = y if f == "minimum_up" else z
            assert entries.pop(ut) == (-1 if f == "minimum_up" else 1)
            assert entries and all(value == 1. and auxiliary + 24 <= j < auxiliary + 4032
                                   and (j - auxiliary) % 24 == q and (j - auxiliary) // 24 <= t
                                   for j, value in entries.items())
            assert auxiliary + t * 24 + q in entries
            hours = sorted((j - auxiliary) // 24 for j in entries)
            assert hours == list(range(hours[0], t + 1))
            assert m.row_lower[r] == -math.inf and m.row_upper[r] == (0 if f == "minimum_up" else 1)
    assert set(families.values()) == {4008}
    return {"pass": True, "family_counts": families, "original_binary": sum(original), "projected_binary": sum(projected)}


def main():
    started = time.perf_counter()
    freeze = js(OUT / "prepared_freeze.json")
    assert not (OUT / "execution_started.json").exists()
    assert freeze["optimizations_started"] == 0 and freeze["all_controls_pass"]
    assert freeze["source_sha256"] == "fe7253d9d6217a26ad3162422e91cc90dba83350526faed1443d54c8500b29ab"
    assert freeze["protocol_sha256"] == "14349e3ea185f0cd4089ab5d2745afbbd4c7d5240064893b5f3ffe0065b6bbb2"
    assert reader.sha(OUT / "input_manifest.csv") == freeze["input_manifest_sha256"]
    with (OUT / "input_manifest.csv").open(newline="") as stream:
        manifest = list(csv.DictReader(stream))
    assert len({r["path"] for r in manifest}) == len(manifest)
    for r in manifest:
        assert Path(r["path"]).stat().st_size == int(r["bytes"]) and reader.sha(r["path"]) == r["sha256"]
    records = []
    for month, seeds, control in ((4, (26093400, 26093401), 26100400), (10, (26094000, 26094001), 26101000)):
        ref = ROOT / f"results/research8h/seasonal_reference_continuation/month_{month:02d}"
        reference = array(ref / "recovered_vector.npz", "vector")
        original = reader.load_model(ref)
        original_mask = array(ref / "original_integrality.npz", "integrality")
        reference_native = reader.read_npz(ref / "native_inputs.npz", ("pmin", "pmax", "net", "rows", "nodal"))
        detail = js(OUT / f"month_{month:02d}_reference.json")
        cap = detail["cap"]
        e = sum((reader.Q(v) for t in range(168) for v in reference[t * 41:t * 41 + 23]), reader.Q(0))
        expected_cap = -(-(e * reader.Q(101, 100)).numerator // (e * reader.Q(101, 100)).denominator)
        assert cap["budget_MWh"] == expected_cap
        assert reader.Q(int(cap["reference_energy_numerator"]), int(cap["reference_energy_denominator"])) == e
        assert reader.Q(int(cap["headroom_numerator"]), int(cap["headroom_denominator"])) == expected_cap - e
        for case, kind in [(f"month_{month:02d}_identity", "identity"), *((f"seed_{seed}", "ordinary") for seed in seeds), (f"seed_{control}", "class_control")]:
            directory = OUT / case
            m = reader.load_model(directory)
            meta = js(directory / "model_metadata.json")
            names = labels(directory / "row_metadata.csv.gz")
            assert len(names) == m.rows and all(int(r["row"]) == j for j, r in enumerate(names))
            assert meta["unit_names"][:24] == meta["thermal_unit_names"]
            assert meta["fossil_units"] == meta["unit_names"][:23]
            assert meta["thermal_unit_names"][23] == "121_NUCLEAR_1"
            assert meta["individual_mean_constraints"] == 0 and meta["budget_MWh"] == expected_cap
            assert not any(r["family"] == "target_mean" for r in names)
            capped = [j for j, r in enumerate(names) if r["family"] == "fossil_energy_cap"]
            assert len(capped) == 1
            caprow = capped[0]
            assert row(m, caprow) == {t * 41 + j: 1. for t in range(168) for j in range(23)}
            assert m.row_lower[caprow] == -math.inf and m.row_upper[caprow] == expected_cap
            assert all(v == 0. for v in array(directory / "objective.npz", "objective"))
            mask = array(directory / "integrality.npz", "integrality")
            assert mask == original_mask
            point = array(directory / "constructive_vector.npz", "vector")
            native = reader.read_npz(directory / "native_inputs.npz", ("pmin", "pmax", "net", "rows", "nodal", "source_hour"))
            order = native["source_hour"].values
            assert sorted(order) == list(range(168)) and order[:48] == tuple(range(48)) and order[120:] == tuple(range(120, 168))
            if kind == "identity":
                assert order == tuple(range(168))
                keep = [r for r in range(m.rows) if r != caprow]
                assert len(keep) == original.rows and m.cols == original.cols
                assert m.lower == original.lower and m.upper == original.upper
                for r, old_r in zip(keep, range(original.rows)):
                    assert row(m, r) == row(original, old_r)
                    assert m.row_lower[r] == original.row_lower[old_r] and m.row_upper[r] == original.row_upper[old_r]
                base_model = m
                base_rows = {(r["family"], int(r["hour_0based"]), r["uid"]): j for j, r in enumerate(names)}
                assert len(base_rows) == m.rows
            else:
                projected = array(directory / "projected_integrality.npz", "integrality")
                projection = projection_audit(m, mask, projected, meta, names)
                assert js(directory / "projection_audit.json")["pass"]
                with (directory / "permutation.csv").open(newline="") as stream:
                    permutation = list(csv.DictReader(stream))
                assert [int(r["new_hour_0based"]) for r in permutation] == list(range(168))
                assert tuple(int(r["source_hour_0based"]) for r in permutation) == order
                assert tuple(int(r["source_native_row"]) for r in permutation) == native["rows"].values
                # All local physical rows must be the exact package permutation;
                # every chronological row must remain the identity formulation.
                blocks = [(meta["offsets"][name], width) for name, width in
                          (("P", 41), ("U", 24), ("Y", 24), ("Z", 24), ("theta", 24))]
                local = {"aggregate_balance", "thermal_upper", "thermal_lower", "nodal_balance", "branch_flow"}
                for r, label in enumerate(names):
                    family, hour, uid = label["family"], int(label["hour_0based"]), label["uid"]
                    source_hour = order[hour] if family in local else hour
                    original_row = base_rows[(family, source_hour, uid)]
                    expected = row(base_model, original_row)
                    if family in local:
                        remapped = {}
                        for j, value in expected.items():
                            block, width = next((start, width) for start, width in blocks if start <= j < start + 168 * width)
                            assert (j - block) // width == source_hour
                            remapped[j + (hour - source_hour) * width] = value
                        expected = remapped
                    assert row(m, r) == expected
                    assert m.row_lower[r] == base_model.row_lower[original_row] and m.row_upper[r] == base_model.row_upper[original_row]
                for block, width in blocks:
                    for t, source_hour in enumerate(order):
                        a, b = block + t * width, block + source_hour * width
                        assert m.lower[a:a + width] == base_model.lower[b:b + width]
                        assert m.upper[a:a + width] == base_model.upper[b:b + width]
            for key in ("pmin", "pmax", "net", "rows", "nodal"):
                source, target = reference_native[key], native[key]
                assert source.shape == target.shape and source.shape[0] == 168
                width = math.prod(source.shape[1:])
                assert target.values == tuple(value for t in order for value in source.values[t * width:(t + 1) * width])
            for name, width in (("P", 41), ("U", 24), ("theta", 24)):
                offset = meta["offsets"][name]
                assert point[offset:offset + 168 * width] == tuple(value for t in order for value in reference[offset + t * width:offset + (t + 1) * width])
            u, y, z = (meta["offsets"][name] for name in ("U", "Y", "Z"))
            for t in range(168):
                for j in range(24):
                    delta = 0 if t == 0 else point[u + t * 24 + j] - point[u + (t - 1) * 24 + j]
                    assert point[y + t * 24 + j] == max(delta, 0) and point[z + t * 24 + j] == max(-delta, 0)
            if kind == "class_control":
                assert point[u:y] == reference[u:y]
            check = point_audit(m, point, mask, names)
            reported = js(directory / "constructive_check.json")
            assert check["static_expanded_pass"] and reported["static_exact"]["expanded_pass"]
            assert check["full_expanded_pass"] == reported["full_exact"]["expanded_pass"]
            assert check["full_strict_pass"] == reported["full_exact"]["strict_pass"]
            assert reported["numerical"]["static_network_cap_pass"]
            if kind != "ordinary":
                assert check["full_expanded_pass"] and reported["constructive_expanded_pass"]
                assert reported["numerical"]["physical"]["pass"]
            else:
                assert all(r["family"] in {"minimum_up", "minimum_down"} for r in check["failed_expanded_rows"])
                for filename in ("matrix.npz", "bounds.npz", "integrality.npz", "row_metadata.csv.gz"):
                    assert reader.sha(directory / filename) == reader.sha(directory / "lp" / filename)
                assert not (directory / "lp" / "solver.log").exists() and not (directory / "mip").exists()
            got_energy = sum((reader.Q(v) for t in range(168) for v in point[t * 41:t * 41 + 23]), reader.Q(0))
            assert got_energy == e
            records.append({"case": case, "month": month, "kind": kind, "cap_MWh": expected_cap,
                            "exact_energy": reader.rat(e), "point_audit": check,
                            "changed_hours": sum(t != source for t, source in enumerate(order)),
                            "projection_checked": kind != "identity", "native_package_mapping_exact": True,
                            "all_matrix_rows_and_bounds_follow_frozen_package_mapping": True,
                            "stored_native_numerical_check_scope": "Read and cross-checked; not an independent native-model reconstruction in this replay."})
            print(json.dumps({"case": case, "static_expanded_pass": check["static_expanded_pass"], "full_expanded_pass": check["full_expanded_pass"]}), flush=True)
    assert freeze["cases"] == ["seed_26093400", "seed_26093401", "seed_26094000", "seed_26094001"]
    assert not (OUT / "execution_started.json").exists()
    for r in manifest:
        assert Path(r["path"]).stat().st_size == int(r["bytes"]) and reader.sha(r["path"]) == r["sha256"]
    result = {"status": "INDEPENDENT_PREPARED_REVIEW_PASS", "manifest_sha256": freeze["input_manifest_sha256"],
              "manifest_files_checked": len(manifest), "all_hashes_match_before_and_after": True,
              "execution_marker_absent": True, "optimization_calls": 0, "cases": records,
              "review_script_sha256": reader.sha(__file__), "reader_sha256": reader.sha(ROOT / "src/research8h_standalone_verify.py"),
              "elapsed_s": time.perf_counter() - started,
              "scope": "Independent all-hash/box/CSR/mask/package/cap/point review; seed PRNG is source-reviewed, not separately reimplemented."}
    with (OUT / "independent_prepared_review.json").open("x", encoding="utf8") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")


if __name__ == "__main__":
    main()
