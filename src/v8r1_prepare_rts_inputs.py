"""Reconstruct portable RTS inputs from pinned sources and published targets.

No optimization is performed and no new dispatch target is generated. HTTPS
certificate verification is always enabled. The legacy V3 directory is an
optional one-time comparison reference, never an input required by a reader.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import urllib.error
import urllib.request

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MONTHS = [1, 2, 3, 4, 5, 6, 7, 10]
COMMIT = "3ece0d3725c844056132393ee252b3083dd4eab4"
BASE = f"https://raw.githubusercontent.com/GridMod/RTS-GMLC/{COMMIT}/"
MODEL_SHA256 = "01d3e67440b1380b62ed68da07e61ac6895b930ada583ffa8af09a370850be78"
SOURCES = [
    ("bus.csv", "RTS_Data/SourceData/bus.csv", "cec3f776222812d43eaeaf7ac85b577719dc565f354a04e120c12a647ddb710e"),
    ("branch.csv", "RTS_Data/SourceData/branch.csv", "e92d16d13b1c5d2899f7871c0c99c3eb94605528beef157bf9e1ccbcffe5ef4e"),
    ("gen.csv", "RTS_Data/SourceData/gen.csv", "988466f29132b73739de60c9204dd4a2a9ceb0adf572e5966c086611272f4068"),
    ("timeseries_data_files/Hydro/DAY_AHEAD_hydro.csv", "RTS_Data/timeseries_data_files/Hydro/DAY_AHEAD_hydro.csv", "4030660920df850138472c5561322c71e5037813c8e3232d3f9bde512a40606d"),
    ("timeseries_data_files/Load/DAY_AHEAD_regional_Load.csv", "RTS_Data/timeseries_data_files/Load/DAY_AHEAD_regional_Load.csv", "7a9470d32d49068a91334cb36db54cceb2feb5cb1f702b0fa0847af8bac6cf21"),
    ("timeseries_data_files/PV/DAY_AHEAD_pv.csv", "RTS_Data/timeseries_data_files/PV/DAY_AHEAD_pv.csv", "bfede6e558df5ea0f244b6326940a4ee0b95138643aa8a062897c67134c9c185"),
    ("timeseries_data_files/RTPV/DAY_AHEAD_rtpv.csv", "RTS_Data/timeseries_data_files/RTPV/DAY_AHEAD_rtpv.csv", "13a6933c2e0a513e1a453143876dadef6977e6add7701a21f56fe6a753afce42"),
    ("timeseries_data_files/WIND/DAY_AHEAD_wind.csv", "RTS_Data/timeseries_data_files/WIND/DAY_AHEAD_wind.csv", "6a1a8dc7d10a518523b3b319902ecc1ca1c400223832b26c6edb3a6e69d01dbc"),
]


def sha(content):
    return hashlib.sha256(content).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_model(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def model_static_equal(prepared, original):
    checks = {}
    for name in ("buses", "branches", "gens", "dec", "thermal", "load_ts", "pv_ts", "wind_ts", "hydro_ts", "rtpv_ts"):
        checks[name] = bool(getattr(prepared, name).equals(getattr(original, name)))
    for name in ("urows", "cost", "prop", "A", "bl", "rate", "Bbus"):
        checks[name] = bool(np.array_equal(getattr(prepared, name), getattr(original, name), equal_nan=True))
    for name in ("AREA", "slack", "busids", "bi"):
        checks[name] = getattr(prepared, name) == getattr(original, name)
    require(all(checks.values()), "Prepared and original static model arrays differ.")
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / ".work/v8r1_rts_inputs")
    parser.add_argument("--report", type=Path, default=ROOT / "results/v8r1/rts_input_reconstruction.json")
    parser.add_argument("--baseline-v3", type=Path, help="Optional legacy reference for exact author-side equivalence checks")
    parser.add_argument("--refresh", action="store_true", help="Download the pinned eight CSVs even when verified local files exist")
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    code_path = output / "code/dscgrid_model.py"
    raw_path = output / "raw/RTS-GMLC_v0.2.3"
    processed = output / "processed"
    code_path.parent.mkdir(parents=True, exist_ok=True)
    processed.mkdir(parents=True, exist_ok=True)
    # Normalize checkout line endings only; this restores the author's exact LF bytes.
    model_content = (ROOT / "src/rts_native_model.py").read_bytes().replace(b"\r\n", b"\n")
    require(sha(model_content) == MODEL_SHA256, "Author model source hash differs from the admitted source.")
    code_path.write_bytes(model_content)
    report = {"status": "INCOMPLETE", "upstream_repository": "GridMod/RTS-GMLC", "upstream_commit": COMMIT,
        "tls_verification": "enabled; urllib default trust configuration; no certificate bypass",
        "optimization_runs": 0, "new_targets_generated": 0, "model_sha256": MODEL_SHA256,
        "native_sources": [], "weeks": [], "baseline_comparison_requested": bool(args.baseline_v3)}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    try:
        for relative, upstream, expected in SOURCES:
            destination = raw_path / relative
            if destination.exists() and not args.refresh and sha(destination.read_bytes()) == expected:
                content = destination.read_bytes()
                method = "reused previously hash-verified pinned content"
            else:
                request = urllib.request.Request(BASE + upstream, headers={"User-Agent": "DSC-Grid-reproducibility"})
                # Default HTTPS verification is deliberately retained.
                with urllib.request.urlopen(request, timeout=90) as response:
                    content = response.read()
                method = "downloaded official pinned raw URL over verified HTTPS"
            actual = sha(content)
            require(actual == expected, f"Pinned source hash mismatch for {relative}: {actual}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)
            row = {"path": "raw/RTS-GMLC_v0.2.3/" + relative, "url": BASE + upstream,
                "sha256": actual, "expected_sha256": expected, "bytes": len(content), "acquisition": method}
            if args.baseline_v3:
                original = args.baseline_v3 / "raw/RTS-GMLC_v0.2.3" / relative
                row["legacy_baseline_sha256"] = sha(original.read_bytes())
                row["identical_to_legacy_baseline"] = row["legacy_baseline_sha256"] == actual
                require(row["identical_to_legacy_baseline"], f"Legacy baseline raw file differs: {relative}")
            report["native_sources"].append(row)
            args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
        prepared = load_model(code_path, "portable_rts_model")
        original_model = None
        if args.baseline_v3:
            original_code = args.baseline_v3 / "code/dscgrid_model.py"
            require(sha(original_code.read_bytes()) == MODEL_SHA256, "Legacy author code differs.")
            original_model = load_model(original_code, "legacy_rts_model")
            report["static_model_equivalence"] = model_static_equal(prepared, original_model)
        cols = prepared.dec["GEN UID"].tolist()
        require(len(cols) == 41 and len(prepared.urows) == 24, "Unexpected decision/thermal dimensions.")
        keys = [tuple(map(int, row)) for row in prepared.load_ts[["Year", "Month", "Day", "Period"]].to_numpy()]
        require(len(set(keys)) == len(keys), "Native load timestamps are not unique.")
        row_lookup = {key: index for index, key in enumerate(keys)}
        for month in MONTHS:
            filename = f"month_{month:02d}_first_week_dispatch.csv"
            public_path = ROOT / "reproducibility/data/processed/rts" / filename
            content = public_path.read_bytes()
            target_path = processed / filename
            target_path.write_bytes(content)
            target = pd.read_csv(target_path)
            require(len(target) == 168 and set(target.columns) == set(cols + ["timestamp"]), "Unexpected published target schema.")
            target_array = target[cols].to_numpy(float)
            require(np.isfinite(target_array).all(), "Nonfinite published target dispatch.")
            stamps = pd.to_datetime(target["timestamp"])
            require(stamps.iloc[0] == pd.Timestamp(2020, month, 1), "Unexpected target week.")
            require(np.all(np.diff(stamps.to_numpy()) == np.timedelta64(1, "h")), "Target is not 168 consecutive hourly snapshots.")
            native_rows = []
            for stamp in stamps:
                key = (stamp.year, stamp.month, stamp.day, stamp.hour + 1)
                require(key in row_lookup, f"Timestamp absent from native table: {stamp}")
                native_rows.append(row_lookup[key])
            # Only the two columns consumed by the new chronology scripts are rebuilt.
            # Historical objectives, flows and commitment counts are not fabricated.
            summary = pd.DataFrame({"timestamp": target["timestamp"], "row": native_rows})
            summary_path = processed / f"month_{month:02d}_first_week_hourly_summary.csv"
            summary.to_csv(summary_path, index=False, lineterminator="\n")
            week = {"month": month, "snapshots": 168, "coordinates": 41, "first_native_row": native_rows[0],
                "last_native_row": native_rows[-1], "target_source": public_path.relative_to(ROOT).as_posix(),
                "target_sha256": sha(content), "target_copy_byte_identical": target_path.read_bytes() == content,
                "row_summary_sha256": sha(summary_path.read_bytes()), "summary_fields": ["timestamp", "row"],
                "target_optimization_performed": False}
            if args.baseline_v3:
                original_target = pd.read_csv(args.baseline_v3 / "processed" / filename)[cols].to_numpy(float)
                original_summary = pd.read_csv(args.baseline_v3 / "processed" / summary_path.name)
                week["target_arrays_identical_to_legacy"] = bool(np.array_equal(target_array, original_target))
                week["timestamp_strings_identical_to_legacy"] = target["timestamp"].tolist() == original_summary["timestamp"].tolist()
                week["rowmaps_identical_to_legacy"] = native_rows == original_summary["row"].astype(int).tolist()
                exact_arrays = True
                for row in native_rows:
                    pmin, pmax = prepared.avail_at(row)
                    old_min, old_max = original_model.avail_at(row)
                    exact_arrays &= np.array_equal(pmin, old_min) and np.array_equal(pmax, old_max)
                    exact_arrays &= np.array_equal(prepared.rtpv_at(row), original_model.rtpv_at(row))
                    exact_arrays &= float(prepared.load_ts.loc[row, str(prepared.AREA)]) == float(original_model.load_ts.loc[row, str(original_model.AREA)])
                week["hourly_model_arrays_identical_to_legacy"] = bool(exact_arrays)
                require(all(week[key] for key in ("target_arrays_identical_to_legacy", "timestamp_strings_identical_to_legacy", "rowmaps_identical_to_legacy", "hourly_model_arrays_identical_to_legacy")), f"Legacy equivalence failed for month{month}.")
            report["weeks"].append(week)
        report["status"] = "PORTABLE_INPUTS_VERIFIED"
        report["prepared_directory"] = str(output.relative_to(ROOT)) if output.is_relative_to(ROOT) else str(output)
        report["verified_native_files"] = len(report["native_sources"])
        report["verified_weeks"] = len(report["weeks"])
        report["baseline_equivalence"] = "PASS: all8 raw hashes, static arrays, hourly arrays, target arrays and rowmaps match" if args.baseline_v3 else "not requested; pinned raw hashes and published target reconstruction verified"
        args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps({"status": report["status"], "prepared_directory": report["prepared_directory"],
            "verified_native_files": 8, "verified_weeks": 8, "baseline_equivalence": report["baseline_equivalence"],
            "report": str(args.report)}, indent=2))
    except Exception as exc:
        report["status"] = "FAILED"
        report["error"] = str(exc)
        args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
        raise


if __name__ == "__main__":
    main()
