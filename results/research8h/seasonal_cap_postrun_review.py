"""Independent arithmetic/classification review of completed seasonal cap calls."""
from __future__ import annotations
import csv
import importlib.util
import json
import math
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/research8h/seasonal_cap_continuation"
spec = importlib.util.spec_from_file_location("cap_review_helpers", ROOT / "results/research8h/seasonal_cap_prepared_review.py")
helpers = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = helpers
spec.loader.exec_module(helpers)
reader, js, array = helpers.reader, helpers.js, helpers.array


def manifest_check():
    freeze = js(OUT / "prepared_freeze.json")
    assert reader.sha(OUT / "input_manifest.csv") == freeze["input_manifest_sha256"]
    with (OUT / "input_manifest.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    for r in rows:
        p = Path(r["path"])
        assert p.stat().st_size == int(r["bytes"]) and reader.sha(p) == r["sha256"]
    return len(rows), freeze["input_manifest_sha256"]


def main():
    begun = time.perf_counter()
    completion, outcomes = js(OUT / "completion.json"), js(OUT / "outcomes.json")
    assert js(OUT / "final_manifest_check.json")["pass"]
    count, manifest = manifest_check()
    prepared_review = js(OUT / "independent_prepared_review.json")
    assert prepared_review["status"] == "INDEPENDENT_PREPARED_REVIEW_PASS"
    assert prepared_review["manifest_sha256"] == manifest
    expected = ["seed_26093400", "seed_26093401", "seed_26094000", "seed_26094001"]
    assert [r["case"] for r in outcomes] == expected
    assert completion["eligible_ordinary_cases"] == completion["intended_ordinary_cases"] == 4
    records, lplogs, miplogs = [], [], []
    lptime = miptime = 0.
    mipcalls = 0
    for outcome in outcomes:
        directory = OUT / outcome["case"]
        m = reader.load_model(directory)
        mask = array(directory / "integrality.npz", "integrality")
        names = helpers.labels(directory / "row_metadata.csv.gz")
        meta = js(directory / "model_metadata.json")
        lp = js(directory / "lp/result.json")
        assert lp["optimization_calls"] == 1 and lp["time_limit_s"] == 30
        assert lp["solver_options"]["solver"] == "simplex" and lp["solver_options"]["presolve"] == "off"
        assert lp["solver_options"]["threads"] == 1 and lp["solver_options"]["random_seed"] == 0
        assert outcome["LP_verdict"] == lp["verdict"] and outcome["LP_calls"] == 1
        lptime += lp["elapsed_s"]
        log = directory / "lp/solver.log"
        assert log.read_text().count("Running HiGHS") == 1
        lplogs.append({"case": outcome["case"], "birth_s": log.stat().st_ctime, "last_write_s": log.stat().st_mtime})
        record = {"case": outcome["case"], "producer_outcome": outcome, "LP_elapsed_s": lp["elapsed_s"],
                  "LP_point_scope": "Continuous relaxation only; original binary mask is retained separately."}
        pointpath = directory / "lp/returned_vector.npz"
        if pointpath.exists():
            point = array(pointpath, "vector")
            audit = helpers.point_audit(m, point, (0,) * m.cols, names)
            fractional = sum(flag and value not in (0., 1.) for flag, value in zip(mask, point))
            fractional_tol = sum(flag and abs(value - round(value)) > 1e-5 for flag, value in zip(mask, point))
            record.update(independent_continuous_point=audit,
                          original_binary_coordinates_not_exact_0_or_1=fractional,
                          original_binary_coordinates_fractional_beyond_tolerance=fractional_tol,
                          LP_point_sha256=reader.sha(pointpath))
            if lp["verdict"] == "NUMERICAL_CONTINUOUS_FEASIBLE_BINARY_UNKNOWN":
                assert lp["returned_vector_check"]["pass"]
                assert fractional_tol == lp["fractional_state_coordinates"]
        assert not (directory / "lp/dual_certificate.json").exists(), "Unexpected certificate requires separate independent ray review"
        mip = directory / "mip"
        if mip.exists():
            result = js(mip / "result.json")
            mipcalls += 1
            assert result["optimization_calls"] == 1 and result["time_limit_s"] == 300
            assert result["solver_options"]["time_limit"] == 300
            assert result["solver_options"]["threads"] == 1 and result["solver_options"]["random_seed"] == 0
            assert result["solver_options"]["presolve"] == "on" and result["solver_options"]["mip_rel_gap"] == 1e-8
            assert outcome["MIP_calls"] == 1 and outcome["verdict"] == result["verdict"]
            miptime += result["elapsed_s"]
            mlog = mip / "solver.log"
            assert mlog.read_text().count("Running HiGHS") == 1
            miplogs.append({"case": outcome["case"], "birth_s": mlog.stat().st_ctime, "last_write_s": mlog.stat().st_mtime})
            record["MIP_elapsed_s"] = result["elapsed_s"]
            record["MIP_soft_limit_overrun_s"] = max(0., result["elapsed_s"] - 300)
            recoveredpath = mip / "recovered_vector.npz"
            if recoveredpath.exists():
                raw = array(mip / "raw_vector.npz", "vector")
                recovered = array(recoveredpath, "vector")
                u, y, z, theta = (meta["offsets"][key] for key in ("U", "Y", "Z", "theta"))
                assert recovered[:u] == raw[:u] and recovered[theta:] == raw[theta:]
                assert all(math.isfinite(v) for v in raw)
                for t in range(168):
                    for j in range(24):
                        q = t * 24 + j
                        assert abs(raw[u+q] - round(raw[u+q])) <= 1e-5
                        assert recovered[u+q] == round(raw[u+q]) and recovered[u+q] in (0., 1.)
                        delta = 0. if t == 0 else recovered[u+q] - recovered[u+q-24]
                        assert recovered[y+q] == max(delta, 0.) and recovered[z+q] == max(-delta, 0.)
                audit = helpers.point_audit(m, recovered, mask, names)
                exact, physical = js(mip / "exact_point_check.json"), js(mip / "physical_check.json")
                assert audit["full_expanded_pass"] == exact["expanded_pass"] and audit["full_strict_pass"] == exact["strict_pass"]
                if result["verdict"] == "VERIFIED_FEASIBLE_EXPANDED_MODEL":
                    assert audit["full_expanded_pass"] and physical["pass"]
                    assert result["raw_matrix_check"]["pass"] and result["recovered_matrix_check"]["pass"]
                record.update(independent_recovered_binary_point=audit, stored_native_physics_pass=physical["pass"],
                              recovered_vector_sha256=reader.sha(recoveredpath), raw_vector_sha256=reader.sha(mip / "raw_vector.npz"),
                              recovery_mapping_exact=True)
            else:
                assert result["verdict"] != "VERIFIED_FEASIBLE_EXPANDED_MODEL"
                record["no_recovered_binary_point"] = True
            if not result["solution_value_valid"]:
                assert not (mip / "raw_vector.npz").exists()
                record["no_solver_incumbent"] = True
        else:
            assert outcome["MIP_calls"] == 0
        records.append(record)
        print(json.dumps({"case": outcome["case"], "producer_verdict": outcome["verdict"],
                          "exact_expanded_continuous_point": record.get("independent_continuous_point", {}).get("full_expanded_pass"),
                          "recovered_binary_point": record.get("independent_recovered_binary_point", {}).get("full_expanded_pass")}), flush=True)
    assert max(r["last_write_s"] for r in lplogs) <= min((r["birth_s"] for r in miplogs), default=math.inf)
    assert all(a["last_write_s"] <= b["birth_s"] for a, b in zip(miplogs, miplogs[1:]))
    assert completion["LP_calls"] == 4 and completion["MIP_calls"] == mipcalls
    assert math.isclose(completion["actual_LP_seconds"], lptime, rel_tol=0., abs_tol=1e-6)
    assert math.isclose(completion["actual_MIP_seconds"], miptime, rel_tol=0., abs_tol=1e-6)
    assert completion["original_replication_gate"] == "NOT_MET_INSUFFICIENT_ELIGIBLE_WEEKS"
    assert completion["new_continuation_weeks_with_certified_negative_and_controls"] == []
    assert completion["augmented_weeks_with_certified_negative_and_controls"] == [1]
    assert not completion["augmented_at_least_two_weeks"]
    finalcount, finalmanifest = manifest_check()
    assert count == finalcount and manifest == finalmanifest
    output = {"status": "INDEPENDENT_POSTRUN_REVIEW_PASS", "optimization_calls": 0,
              "manifest_sha256": manifest, "manifest_files_checked": count, "all_frozen_hashes_match_before_and_after": True,
              "cases": records, "LP_log_timestamps": lplogs, "MIP_log_timestamps": miplogs,
              "all_LPs_before_any_MIP": True, "MIPs_sequential_in_fixed_order": True,
              "actual_LP_seconds": lptime, "actual_MIP_seconds": miptime, "actual_solver_seconds": lptime + miptime,
              "total_MIP_soft_limit_overrun_s": sum(r.get("MIP_soft_limit_overrun_s", 0.) for r in records),
              "completion": completion, "review_elapsed_s": time.perf_counter() - begun,
              "review_script_sha256": reader.sha(__file__), "helper_sha256": reader.sha(ROOT / "results/research8h/seasonal_cap_prepared_review.py"),
              "prepared_review_sha256": reader.sha(OUT / "independent_prepared_review.json"),
              "scope": "Read-only archived-matrix classification; native physical reports checked for consistency, not independently reassembled from CSVs. LP replay does not impose binary integrality and cannot prove binary feasibility."}
    with (OUT / "independent_postrun_review.json").open("x", encoding="utf8") as stream:
        json.dump(output, stream, indent=2, allow_nan=False)
        stream.write("\n")


if __name__ == "__main__":
    main()
