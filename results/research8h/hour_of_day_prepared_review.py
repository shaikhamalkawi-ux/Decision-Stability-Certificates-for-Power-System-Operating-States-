"""Read-only independent review of frozen January hour-of-day archives."""
from __future__ import annotations
import csv
import importlib.util
import json
import math
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/research8h/hour_of_day"
BASE = ROOT / "results/research8h/seasonal_transfer/january_identity"
spec = importlib.util.spec_from_file_location("hod_review_helpers", ROOT / "results/research8h/seasonal_cap_prepared_review.py")
helpers = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = helpers
spec.loader.exec_module(helpers)
reader, js, array = helpers.reader, helpers.js, helpers.array


def bit_equal(a, b):
    return len(a) == len(b) and all(x == y and (not isinstance(x, float) or x.hex() == y.hex()) for x, y in zip(a, b))


def main():
    begun = time.perf_counter()
    freeze, before = js(OUT / "prepared_freeze.json"), js(OUT / "freeze_before_generation.json")
    assert not (OUT / "execution_started.json").exists()
    assert freeze["source_sha256"] == before["source_sha256"] == "b617d41ab09d18d57c003147b52ae80f369225bc6029121109cee3d53e71d60e"
    assert freeze["protocol_sha256"] == before["protocol_sha256"] == "09b3a45af4224c65b03dd4d3972750ba417f0f26ccc153e51fa9ca3ae4d9829b"
    assert freeze["ordinary_cases"] == ["seed_26093200", "seed_26093201"]
    assert freeze["control_seed"] == 26100200 and freeze["optimizations_started"] == 0
    assert reader.sha(OUT / "input_manifest.csv") == freeze["manifest_sha256"]
    with (OUT / "input_manifest.csv").open(newline="") as stream:
        manifest = list(csv.DictReader(stream))
    assert len(manifest) == freeze["bound_files"] and len({r["path"] for r in manifest}) == len(manifest)
    for r in manifest:
        p = Path(r["path"])
        assert p.stat().st_size == int(r["bytes"]) and reader.sha(p) == r["sha256"]
    base = reader.load_model(BASE)
    baselabels = helpers.labels(BASE / "row_metadata.csv.gz")
    rowmap = {(r["family"], int(r["hour_0based"]), r["uid"]): i for i, r in enumerate(baselabels)}
    assert len(rowmap) == base.rows
    ref = array(BASE / "constructive_vector.npz", "vector")
    original = array(BASE / "integrality.npz", "integrality")
    refnative = reader.read_npz(BASE / "native_inputs.npz", ("pmin", "pmax", "net", "rows", "nodal", "source_hour"))
    expected_cases = ["january_identity", "seed_26093200", "seed_26093201", "seed_26100200"]
    prepared = js(OUT / "prepared_cases.json")
    assert [r["case"] for r in prepared] == expected_cases
    results = []
    orders = []
    for record in prepared:
        case, role = record["case"], record["role"]
        directory = OUT / case
        m = reader.load_model(directory)
        mask, projected = array(directory / "integrality.npz", "integrality"), array(directory / "projected_integrality.npz", "integrality")
        names, meta = helpers.labels(directory / "row_metadata.csv.gz"), js(directory / "model_metadata.json")
        assert names == baselabels and mask == original
        assert m.rows == base.rows == 34681 and m.cols == base.cols == 23016
        assert m.indices == base.indices and m.indptr == base.indptr and bit_equal(m.data, base.data)
        assert meta["unit_names"][:24] == meta["thermal_unit_names"]
        assert meta["fossil_units"] == meta["unit_names"][:23] and meta["unit_names"][23] == "121_NUCLEAR_1"
        assert meta["individual_mean_constraints"] == 0 and meta["budget_MWh"] == 23195
        assert all(v == 0. for v in array(directory / "objective.npz", "objective"))
        projection = helpers.projection_audit(m, mask, projected, meta, names)
        point = array(directory / "constructive_vector.npz", "vector")
        native = reader.read_npz(directory / "native_inputs.npz", ("pmin", "pmax", "net", "rows", "nodal", "source_hour"))
        order = native["source_hour"].values
        assert sorted(order) == list(range(168)) and order[:48] == tuple(range(48)) and order[120:] == tuple(range(120, 168))
        assert all(source % 24 == t % 24 for t, source in enumerate(order))
        assert all(sorted(order[t] for t in (48+h, 72+h, 96+h)) == [48+h, 72+h, 96+h] for h in range(24))
        if role == "ordinary":
            orders.append(order)
        for key in ("pmin", "pmax", "net", "rows", "nodal"):
            a, b = refnative[key], native[key]
            assert a.shape == b.shape and a.dtype == b.dtype
            width = math.prod(a.shape[1:])
            assert bit_equal(b.values, tuple(v for t in order for v in a.values[t * width:(t + 1) * width]))
        blocks = [(meta["offsets"][name], width) for name, width in (("P", 41), ("U", 24), ("Y", 24), ("Z", 24), ("theta", 24))]
        for name, width in (("P", 41), ("U", 24), ("theta", 24)):
            start = meta["offsets"][name]
            assert bit_equal(point[start:start + 168 * width], tuple(v for t in order for v in ref[start + t * width:start + (t + 1) * width]))
        u, y, z = (meta["offsets"][k] for k in ("U", "Y", "Z"))
        for t in range(168):
            for j in range(24):
                delta = 0. if t == 0 else point[u + t*24+j] - point[u + (t-1)*24+j]
                assert point[y+t*24+j] == max(delta, 0.) and point[z+t*24+j] == max(-delta, 0.)
        if role != "ordinary":
            # Binary +0 and -0 denote the same exact integer. Package transport
            # above remains bitwise; the control promise concerns U values.
            assert point[u:y] == ref[u:y]
        local = {"aggregate_balance", "thermal_upper", "thermal_lower", "nodal_balance", "branch_flow"}
        caprows = []
        for r, label in enumerate(names):
            family, hour, uid = label["family"], int(label["hour_0based"]), label["uid"]
            source_hour = order[hour] if family in local else hour
            source_row = rowmap[(family, source_hour, uid)]
            expected = helpers.row(base, source_row)
            if family in local:
                remapped = {}
                for j, value in expected.items():
                    start, width = next((a, w) for a, w in blocks if a <= j < a+168*w)
                    assert (j-start)//width == source_hour
                    remapped[j+(hour-source_hour)*width] = value
                expected = remapped
            assert helpers.row(m, r) == expected
            assert m.row_lower[r] == base.row_lower[source_row] and m.row_upper[r] == base.row_upper[source_row]
            if family == "fossil_energy_cap":
                caprows.append(r)
                assert expected == {t*41+j: 1. for t in range(168) for j in range(23)}
                assert m.row_lower[r] == -math.inf and m.row_upper[r] == 23195
            assert family != "target_mean"
        assert len(caprows) == 1
        for start, width in blocks:
            for t, source in enumerate(order):
                assert bit_equal(m.lower[start+t*width:start+(t+1)*width], base.lower[start+source*width:start+(source+1)*width])
                assert bit_equal(m.upper[start+t*width:start+(t+1)*width], base.upper[start+source*width:start+(source+1)*width])
        random = js(directory / "randomization.json")
        if role == "ordinary":
            assert random["seed"] == int(case.split("_")[1]) and random["redraws"] == 0
            assert len(random["groups"]) == 24 and random["group_order"] == "hour 0 through 23"
            for h, group in enumerate(random["groups"]):
                positions = [48+h, 72+h, 96+h]
                assert group["destination_hours"] == positions and group["source_hours"] == [order[t] for t in positions]
        elif role == "positive_control":
            groups = {}
            for t in range(48, 120):
                key = (t % 24, *map(int, ref[u+t*24:u+(t+1)*24]))
                groups.setdefault(key, []).append(t)
            assert random["seed"] == 26100200 and random["redraws"] == 0
            assert random["group_order"] == "lexicographic (hour,U bits)" and len(random["groups"]) == len(groups)
            for key, group in zip(sorted(groups), random["groups"]):
                assert group["hour_of_day_0based"] == key[0] and group["identity_U_signature"] == list(key[1:])
                positions = groups[key]
                assert group["destination_hours"] == positions and group["source_hours"] == [order[t] for t in positions]
                assert sorted(group["source_hours"]) == positions
        else:
            assert order == tuple(range(168))
        pointcheck = helpers.point_audit(m, point, mask, names)
        producer = js(directory / "constructive_check.json")
        assert pointcheck["static_expanded_pass"] and producer["static_exact"]["expanded_pass"]
        assert pointcheck["full_expanded_pass"] == producer["full_exact"]["expanded_pass"]
        assert pointcheck["full_strict_pass"] == producer["full_exact"]["strict_pass"]
        assert producer["numerical"]["static_network_cap_pass"]
        if role != "ordinary":
            assert pointcheck["full_expanded_pass"] and producer["constructive_expanded_pass"]
            assert producer["numerical"]["physical"]["pass"]
        else:
            assert all(r["family"] in {"minimum_up", "minimum_down"} for r in pointcheck["failed_expanded_rows"])
            for filename in ("matrix.npz", "bounds.npz", "integrality.npz", "row_metadata.csv.gz"):
                assert reader.sha(directory / filename) == reader.sha(directory / "lp" / filename)
            assert not (directory / "lp/solver.log").exists() and not (directory / "mip").exists()
        energy = sum((reader.Q(point[t*41+j]) for t in range(168) for j in range(23)), reader.Q(0))
        refenergy = sum((reader.Q(ref[t*41+j]) for t in range(168) for j in range(23)), reader.Q(0))
        assert energy == refenergy and energy <= 23195
        continuity = [t for t in range(167) if order[t+1] != order[t] + 1]
        changed_pairs = [t for t in range(167) if (order[t], order[t+1]) != (t, t+1)]
        assert record["changed_adjacent_pair_count"] == len(continuity) and record["changed_adjacent_pairs_after_hours"] == continuity
        results.append({"case": case, "role": role, "point_check": pointcheck, "projection": projection,
                        "changed_hours": sum(t != source for t, source in enumerate(order)),
                        "source_continuity_break_count": len(continuity), "positionwise_changed_adjacent_pair_count": len(changed_pairs),
                        "positionwise_changed_adjacent_pairs_after_hours": changed_pairs,
                        "exact_fossil_MWh": reader.rat(energy), "all_model_rows_bounds_and_native_packages_match": True,
                        "U_signed_zero_bit_differences_from_unpermuted_identity": sum(a == b == 0. and a.hex() != b.hex() for a, b in zip(point[u:y], ref[u:y])),
                        "control_group_order_checked": role == "positive_control"})
        print(json.dumps({"case": case, "static_expanded_pass": pointcheck["static_expanded_pass"], "full_expanded_pass": pointcheck["full_expanded_pass"]}), flush=True)
    sampling = js(OUT / "sampling_inventory.json")
    assert sampling["ordinary_denominator"] == 2 and sampling["duplicate_ordinary_permutations"] == (orders[0] == orders[1])
    assert not (OUT / "execution_started.json").exists()
    for r in manifest:
        p = Path(r["path"])
        assert p.stat().st_size == int(r["bytes"]) and reader.sha(p) == r["sha256"]
    report = {"status": "INDEPENDENT_PREPARED_REVIEW_PASS", "optimization_calls": 0,
              "manifest_sha256": freeze["manifest_sha256"], "manifest_files_checked": len(manifest),
              "all_frozen_hashes_match_before_and_after": True, "execution_marker_absent": True,
              "cases": results, "review_script_sha256": reader.sha(__file__),
              "helper_sha256": reader.sha(ROOT / "results/research8h/seasonal_cap_prepared_review.py"),
              "elapsed_s": time.perf_counter() - begun,
              "review_development_note": "An initial replay stopped at an overly strict bitwise equality check of unpermuted control U: +0/-0 represent the same exact binary value. Only that reviewer assertion was corrected; package transport remains bitwise and no producer input, point, seed or outcome was changed. No optimization was run.",
              "scope": "Independent exact integer-dyadic matrix checks and package/mask mapping; native physical reports read, not reassembled; PCG64 calls source-reviewed, group/order records independently checked, PRNG not reimplemented."}
    with (OUT / "independent_prepared_review.json").open("x", encoding="utf8") as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
        stream.write("\n")


if __name__ == "__main__":
    main()
