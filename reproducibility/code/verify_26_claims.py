#!/usr/bin/env python3
"""Independent arithmetic reproduction of DSC-Grid's central released claims.

This script intentionally does not import any DSC-Grid analysis module.  It reads
only released derived CSV artifacts, reconstructs empirical L1 transport with a new
implementation, and writes a claim-by-claim audit table.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment


STATIC_EXPECTED = {
    2: (397.001, 411.690),
    3: (329.223, 357.682),
    4: (641.069, 667.672),
    5: (781.466, 790.280),
    6: (1039.444, 1047.087),
    7: (1587.737384570594, 1592.540955999171),
    10: (1174.326, 1181.694),
}


def empirical_l1(a: np.ndarray, b: np.ndarray) -> float:
    """Equal-weight empirical W1 for two equally sized samples."""
    cost = np.empty((a.shape[0], b.shape[0]), dtype=float)
    for i in range(a.shape[0]):
        cost[i, :] = np.abs(b - a[i, :]).sum(axis=1)
    rows, cols = linear_sum_assignment(cost)
    return float(cost[rows, cols].mean())


def add(rows: list[dict], claim: str, expected: float, got: float,
        tolerance: float, evidence: str, method: str) -> None:
    deviation = abs(float(got) - float(expected))
    rows.append({
        "claim": claim,
        "expected": float(expected),
        "reproduced": float(got),
        "absolute_deviation": deviation,
        "tolerance": tolerance,
        "status": "PASS" if deviation <= tolerance else "FAIL",
        "evidence": evidence,
        "method": method,
    })


def read_static_csvs(package: Path) -> dict[int, pd.DataFrame]:
    """Read author-generated dispatch outputs; upstream raw inputs are excluded."""
    root = package / "data" / "processed" / "rts"
    return {month: pd.read_csv(root / f"month_{month:02d}_first_week_dispatch.csv")
            .drop(columns="timestamp") for month in (1, 2, 3, 4, 5, 6, 7, 10)}


def audit_static(package: Path, rows: list[dict]) -> None:
    dispatch = read_static_csvs(package)
    source = dispatch[1].to_numpy(float)
    for month, (m_expected, w_expected) in STATIC_EXPECTED.items():
        target = dispatch[month].to_numpy(float)
        mean_move = float(np.abs(target.mean(axis=0) - source.mean(axis=0)).sum())
        w1 = empirical_l1(source, target)
        # Rounded table entries are audited at table precision except for July,
        # whose full-precision lock is present in the release.
        tol = 5e-4 if month != 7 else 1e-8
        add(rows, f"RTS month {month:02d} mean L1 (MW)", m_expected, mean_move,
            tol, "author-generated RTS dispatch CSVs", "direct means; no project imports")
        add(rows, f"RTS month {month:02d} empirical W1 (MW)", w_expected, w1,
            tol, "author-generated RTS dispatch CSVs", "Hungarian assignment on L1 costs")


def audit_gb(package: Path, rows: list[dict]) -> None:
    root = package / "data" / "processed" / "gb"
    jan = pd.read_csv(root / "january_generator_dispatch.csv", index_col=0)
    jul = pd.read_csv(root / "july_generator_dispatch.csv", index_col=0)
    # Carrier classifications were derived from frozen generation metadata.
    # This arithmetic check does not regenerate or validate upstream parameters.
    metadata = pd.read_csv(root / "coordinate_classification.csv")
    carriers = metadata.set_index("name")["carrier"].to_dict()
    coordinates = [c for c in jan.columns.intersection(jul.columns)
                   if carriers.get(c) != "EU_import"]
    a = jan[coordinates].to_numpy(float)
    b = jul[coordinates].to_numpy(float)
    mean_move = float(np.abs(b.mean(axis=0) - a.mean(axis=0)).sum())
    w1 = empirical_l1(a, b)
    shape = w1 - mean_move
    t_a = pd.to_datetime(jan.index)
    t_b = pd.to_datetime(jul.index)
    hour_total = 0.0
    for hour in range(24):
        hour_total += empirical_l1(a[t_a.hour == hour], b[t_b.hour == hour]) * 7
    hour_w1 = hour_total / len(a)
    values = {
        "GB common internal coordinates": (2685.0, float(len(coordinates))),
        "GB mean L1 (MW)": (16785.25504628075, mean_move),
        "GB empirical W1 (MW)": (18651.979267728475, w1),
        "GB shape gap (MW)": (1866.7242214477264, shape),
        "GB hour-conditioned W1 (MW)": (19888.552386016217, hour_w1),
        "GB hour premium (MW)": (1236.5731182877425, hour_w1 - w1),
    }
    for claim, (expected, got) in values.items():
        add(rows, claim, expected, got, 1e-7, "generated PyPSA-GB dispatch and derived carrier classifications",
            "independent filtering, L1 assignment, and clock-hour grouping")


def audit_repairs_and_ac(package: Path, rows: list[dict]) -> None:
    chronology = package / "data" / "processed" / "chronology" / "native_minud_repair_month_07.csv"
    july_repair = float(pd.read_csv(chronology)["abs_delta_MW"].sum())
    add(rows, "July no-network repair artifact sum (MW)", 8.020508464286115,
        july_repair, 1e-9, "native_minud_repair_month_07.csv",
        "sum of released per-coordinate absolute mean changes")

    network = package / "data" / "processed" / "network_repair" / "network_repair_mean.csv"
    network_frame = pd.read_csv(network)
    network_sum = float(network_frame["abs"].sum())
    add(rows, "July network witness repair artifact sum (MW)", 11.9262964643,
        network_sum, 1e-8, "network_repair_mean.csv",
        "sum of released per-coordinate absolute mean changes")

    ac = pd.read_csv(package / "data" / "processed" / "ac_shared" / "ac_projection_results.csv")
    for month, expected in ((3, 39.208762), (7, 31.080193)):
        subset = ac[(ac["month"] == month) & ac["success"].astype(bool)]
        add(rows, f"AC month {month:02d} successful witnesses", 24.0,
            float(len(subset)), 0.0, "ac_projection_results.csv", "row count")
        add(rows, f"AC month {month:02d} median restoration (MW)", expected,
            float(subset["restoration_L1_MW"].median()), 5e-7,
            "ac_projection_results.csv", "median over released successful witnesses")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    rows: list[dict] = []
    audit_static(args.package, rows)
    audit_gb(args.package, rows)
    audit_repairs_and_ac(args.package, rows)
    args.output.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(args.output / "clean_room_claim_audit.csv", index=False,
                 quoting=csv.QUOTE_MINIMAL)
    summary = {
        "script": "verify_26_claims.py",
        "imports_project_modules": False,
        "scope": "arithmetic consistency of frozen generated outputs; not full pipeline or scientific validation",
        "release": "v8-reproducibility.20260926",
        "claims": int(len(frame)),
        "passed": int((frame.status == "PASS").sum()),
        "failed": int((frame.status == "FAIL").sum()),
        "overall": "PASS" if (frame.status == "PASS").all() else "FAIL",
    }
    (args.output / "clean_room_claim_audit.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    if summary["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
