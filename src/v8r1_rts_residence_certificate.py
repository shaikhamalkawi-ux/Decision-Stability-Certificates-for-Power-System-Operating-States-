"""Independent necessary-condition certificate and direct archived-ramp audit.

Uses interval propagation and exact finite-state count reachability, not an
optimization solver. A failed necessary condition certifies infeasibility;
a passed condition does not certify full-system feasibility.
"""
import argparse
import csv
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import random

import numpy as np
import pandas as pd

MONTHS = [1, 2, 3, 4, 5, 6, 7, 10]
POWER_TOL = 1e-5
ENERGY_TOL = 168 * POWER_TOL


def reachability(forced_on, forced_off, minimum_up, minimum_down):
    """Reachable online-hour counts with unconstrained pre/post-horizon dwell."""
    states = {}
    for status in (0, 1):
        if (forced_on[0] and not status) or (forced_off[0] and status):
            continue
        states[(status, 0)] = 1 << status
    for hour in range(1, len(forced_on)):
        next_states = {}
        for (status, residual), counts in states.items():
            choices = [(status, max(0, residual - 1))]
            if residual == 0:
                switched = 1 - status
                duration = minimum_up if switched else minimum_down
                choices.append((switched, max(0, duration - 1)))
            for new_status, new_residual in choices:
                if (forced_on[hour] and not new_status) or (forced_off[hour] and new_status):
                    continue
                key = (new_status, new_residual)
                next_states[key] = next_states.get(key, 0) | (counts << new_status)
        states = next_states
    mask = 0
    for counts in states.values():
        mask |= counts
    return [count for count in range(len(forced_on) + 1) if mask & (1 << count)]


def propagate(lower, upper, energy, demand, thermal_indices, thermal_minimum):
    """Safe necessary bounds from aggregate balance, energy and thermal gap."""
    lower, upper = lower.copy(), upper.copy()
    for iteration in range(1000):
        loop_lower, loop_upper = lower.copy(), upper.copy()
        previous_lower, previous_upper = lower.copy(), upper.copy()
        lower = np.maximum(lower, demand[:, None] - POWER_TOL - (previous_upper.sum(axis=1)[:, None] - previous_upper))
        upper = np.minimum(upper, demand[:, None] + POWER_TOL - (previous_lower.sum(axis=1)[:, None] - previous_lower))
        previous_lower, previous_upper = lower.copy(), upper.copy()
        lower = np.maximum(lower, energy[None, :] - ENERGY_TOL - (previous_upper.sum(axis=0)[None, :] - previous_upper))
        upper = np.minimum(upper, energy[None, :] + ENERGY_TOL - (previous_lower.sum(axis=0)[None, :] - previous_lower))
        for q, unit in enumerate(thermal_indices):
            force_off = upper[:, unit] < thermal_minimum[q] - POWER_TOL
            force_on = lower[:, unit] > POWER_TOL
            upper[force_off, unit] = np.minimum(upper[force_off, unit], POWER_TOL)
            lower[force_on, unit] = np.maximum(lower[force_on, unit], thermal_minimum[q] - POWER_TOL)
        if np.max(lower - upper) > 5 * POWER_TOL:
            raise ValueError("Static necessary bounds contradict: inspect source/tolerance assumptions before residence certificate.")
        change = max(np.max(np.abs(lower - loop_lower)), np.max(np.abs(upper - loop_upper)))
        if change < 1e-8:
            return lower, upper, iteration + 1
    return lower, upper, 1000


def validate_reachability():
    """Independent exhaustive sequence check of the finite-state algorithm."""
    rng = random.Random(914)
    checks = 0
    for horizon in range(1, 10):
        for minimum_up in range(5):
            for minimum_down in range(5):
                for _ in range(5):
                    forced = [rng.choice([-1, 0, 1]) for _ in range(horizon)]
                    on, off = [x == 1 for x in forced], [x == 0 for x in forced]
                    expected = set()
                    for sequence in itertools.product((0, 1), repeat=horizon):
                        if any((on[t] and not sequence[t]) or (off[t] and sequence[t]) for t in range(horizon)):
                            continue
                        good = True
                        for t in range(1, horizon):
                            if sequence[t] != sequence[t - 1]:
                                duration = minimum_up if sequence[t] else minimum_down
                                if any(sequence[s] != sequence[t] for s in range(t, min(horizon, t + duration))):
                                    good = False
                                    break
                        if good:
                            expected.add(sum(sequence))
                    assert set(reachability(on, off, minimum_up, minimum_down)) == expected
                    checks += 1
    return {"checks": checks, "result": "PASS", "horizons": "1 through9", "minimum_times": "0 through4",
            "method": "exhaustive enumeration of binary sequences;1125 randomized forced-state configurations;seed914"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-v3", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("source_model", args.source_v3 / "code/dscgrid_model.py")
    source = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "dp_exhaustive_validation.json").write_text(json.dumps(validate_reachability(), indent=2), encoding="utf-8")
    all_records = []
    failure_rows = []
    columns = source.dec["GEN UID"].tolist()
    ti = np.flatnonzero(source.thermal.to_numpy(bool))
    raw_min = source.dec.iloc[ti]["PMin MW"].to_numpy(float)
    raw_max = source.dec.iloc[ti]["PMax MW"].to_numpy(float)
    up = np.ceil(source.dec.iloc[ti]["Min Up Time Hr"].to_numpy(float)).astype(int)
    down = np.ceil(source.dec.iloc[ti]["Min Down Time Hr"].to_numpy(float)).astype(int)
    ramp = source.dec.iloc[ti]["Ramp Rate MW/Min"].to_numpy(float) * 60.0
    assert np.all(np.isfinite(ramp)) and np.all(ramp >= 0)
    redundancy = pd.DataFrame({"uid": source.dec.iloc[ti]["GEN UID"].to_numpy(),
        "native_ramp_MW_per_min": ramp / 60, "hourly_ramp_MW": ramp,
        "pmin_MW": raw_min, "pmax_MW": raw_max, "maximum_on_on_change_MW": raw_max - raw_min,
        "redundancy_margin_MW": ramp - (raw_max - raw_min), "on_on_ramp_redundant": ramp >= raw_max - raw_min})
    redundancy.to_csv(args.output / "native_hourly_ramp_redundancy.csv", index=False)
    for month in MONTHS:
        target_path = args.source_v3 / "processed" / f"month_{month:02d}_first_week_dispatch.csv"
        summary_path = args.source_v3 / "processed" / f"month_{month:02d}_first_week_hourly_summary.csv"
        dispatch = pd.read_csv(target_path)[columns].to_numpy(float)
        summary = pd.read_csv(summary_path)
        assert len(summary) == len(dispatch) == 168
        demand, lower, upper = [], [], []
        for _, entry in summary.iterrows():
            row = int(entry["row"])
            stamp = pd.Timestamp(entry["timestamp"])
            native = source.load_ts.loc[row]
            assert (int(native.Year), int(native.Month), int(native.Day), int(native.Period)) == (stamp.year, stamp.month, stamp.day, stamp.hour + 1)
            lo, hi = source.avail_at(row)
            lower.append(lo)
            upper.append(hi)
            demand.append(float(native[str(source.AREA)]) - source.rtpv_at(row).sum())
        pmin, pmax, demand = np.asarray(lower), np.asarray(upper), np.asarray(demand)
        hydro = source.dec.Category.eq("Hydro").to_numpy()
        status = (dispatch[:, ti] > POWER_TOL).astype(int)
        on_on = status[1:].astype(bool) & status[:-1].astype(bool)
        ramp_excess = np.where(on_on, np.abs(np.diff(dispatch[:, ti], axis=0)) - ramp, 0)
        residuals = {"balance_MW": float(np.abs(dispatch.sum(axis=1) - demand).max()),
            "negative_MW": float(max(0, -dispatch.min())),
            "upper_MW": float(max(0, (dispatch - pmax).max())),
            "conditional_lower_MW": float(max(0, (pmin[:, ti] * status - dispatch[:, ti]).max())),
            "conditional_upper_MW": float(max(0, (dispatch[:, ti] - pmax[:, ti] * status).max())),
            "hydro_fixed_MW": float(np.abs(dispatch[:, hydro] - pmin[:, hydro]).max()),
            "on_on_ramp_excess_MW": float(max(0, ramp_excess.max()))}
        assert all(value <= POWER_TOL for value in residuals.values()), (month, residuals)
        initial_lower = np.zeros_like(dispatch)
        initial_lower[:, hydro] = pmin[:, hydro]
        lo, hi, iterations = propagate(initial_lower, pmax, dispatch.sum(axis=0), demand, ti, raw_min)
        assert np.max(lo - dispatch) <= 5 * POWER_TOL and np.max(dispatch - hi) <= 5 * POWER_TOL
        unit_results = []
        for q, unit in enumerate(ti):
            assert np.allclose(pmin[:, unit], raw_min[q]) and np.allclose(pmax[:, unit], raw_max[q])
            on = lo[:, unit] > POWER_TOL
            off = hi[:, unit] < raw_min[q] - POWER_TOL
            counts = reachability(on, off, int(up[q]), int(down[q]))
            energy = float(dispatch[:, unit].sum())
            # Small outward tolerance accounts for per-hour power feasibility.
            min_count = max(0, int(np.ceil((energy - ENERGY_TOL) / (raw_max[q] + POWER_TOL))))
            max_count = min(168, int(np.floor((energy + ENERGY_TOL) / (raw_min[q] - POWER_TOL))))
            admitted_counts = [count for count in counts if min_count <= count <= max_count]
            unit_results.append({"uid": columns[unit], "energy_MWh": energy,
                "pmin_MW": raw_min[q], "pmax_MW": raw_max[q], "min_up_hours": int(up[q]), "min_down_hours": int(down[q]),
                "forced_on_hours_0based": np.flatnonzero(on).tolist(), "forced_off_hours_0based": np.flatnonzero(off).tolist(),
                "energy_count_lower": min_count, "energy_count_upper": max_count,
                "residence_reachable_counts": counts, "energy_compatible_counts": admitted_counts,
                "necessary_condition": "FAIL" if not admitted_counts else "PASS"})
        failures = [item["uid"] for item in unit_results if item["necessary_condition"] == "FAIL"]
        for item in unit_results:
            if item["necessary_condition"] != "FAIL":
                continue
            counts = item["residence_reachable_counts"]
            least = min(counts) if counts else None
            failure_rows.append({"month": month, "unit": item["uid"], "target_energy_MWh": item["energy_MWh"],
                "energy_online_min": item["energy_count_lower"], "energy_online_max": item["energy_count_upper"],
                "residence_online_min": least, "residence_online_max": max(counts) if counts else None,
                "minimum_energy_MWh": item["pmin_MW"] * least if least is not None else None,
                "minimum_energy_excess_MWh": item["pmin_MW"] * least - item["energy_MWh"] if least is not None else None,
                "obstruction": "online-count energy budget" if counts else "forced on/off pattern incompatible with residence"})
        record = {"month": month, "archived_ramp_witness": "PASS", "ramp_source_unit": "MW/min multiplied by60 for consecutive one-hour snapshots",
            "archived_residuals": residuals, "mean_identity": "witness is the original target dispatch, so its complete coordinate mean is identical by construction",
            "propagation_iterations": iterations, "power_tolerance_MW": POWER_TOL, "coordinate_energy_tolerance_MWh": ENERGY_TOL,
            "residence_certificate": "INFEASIBLE_NECESSARY_CONDITION" if failures else "NOT_ESTABLISHED", "failing_units": failures,
            "units": unit_results, "dispatch_sha256": hashlib.sha256(target_path.read_bytes()).hexdigest(),
            "summary_sha256": hashlib.sha256(summary_path.read_bytes()).hexdigest()}
        pd.DataFrame(lo, columns=columns).to_csv(args.output / f"month_{month:02d}_necessary_lower_MW.csv", index=False)
        pd.DataFrame(hi, columns=columns).to_csv(args.output / f"month_{month:02d}_necessary_upper_MW.csv", index=False)
        (args.output / f"month_{month:02d}_certificate.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
        all_records.append({key: value for key, value in record.items() if key != "units"})
        print(json.dumps(all_records[-1]), flush=True)
    (args.output / "summary.json").write_text(json.dumps(all_records, indent=2), encoding="utf-8")
    pd.DataFrame(failure_rows).to_csv(args.output / "failure_margins.csv", index=False)
    used = [Path(__file__), args.source_v3 / "code/dscgrid_model.py", *sorted((args.source_v3 / "raw").rglob("*.csv"))]
    pd.DataFrame([{"path": str(p), "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size} for p in used]).to_csv(args.output / "input_manifest.csv", index=False)


if __name__ == "__main__":
    main()
