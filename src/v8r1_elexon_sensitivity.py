#!/usr/bin/env python3
"""Fixed-date B1610 sensitivity; see docs/V8R1_ELEXON_SENSITIVITY_PROTOCOL.md.

Example (the original frozen directory is never modified):
  python src/v8r1_elexon_sensitivity.py --original-raw ORIGINAL_RAW --acquire
  python src/v8r1_elexon_sensitivity.py --original-raw ORIGINAL_RAW --analyze

No interpolation, zero-padding, clipping, registry refresh or date selection.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import shutil
import ssl
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd
import requests
import scipy
from scipy.optimize import linear_sum_assignment, linprog
from scipy.sparse import eye, kron, vstack
from scipy.spatial.distance import cdist

ROOT = Path(__file__).resolve().parents[1]
JANUARY = tuple(f"2023-01-{d:02d}" for d in (4, 11, 18, 25))
JULY = tuple(f"2023-07-{d:02d}" for d in (5, 12, 19, 26))
DATES = JANUARY + JULY
ORIGINAL_DATES = ("2023-01-11", "2023-07-12")
REGISTRY = "BMU_REFERENCE_ALL_2026-09-20.json"
BASE = "https://data.elexon.co.uk/bmrs/api/v1"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def url_for(day: str) -> str:
    return BASE + "/datasets/B1610/stream?" + urlencode({
        "from": f"{day}T00:00Z", "to": f"{day}T00:00Z",
        "settlementPeriodFrom": 1, "settlementPeriodTo": 48,
    })


def acquire_one(day: str, raw: Path) -> dict:
    destination = raw / f"B1610_{day}.json"
    metadata = destination.with_suffix(".acquisition.json")
    if destination.exists() or metadata.exists():
        if not (destination.exists() and metadata.exists()):
            raise RuntimeError(f"Unpaired raw/metadata file: {destination}")
        saved = json.loads(metadata.read_text(encoding="utf-8"))
        if saved["sha256"] != sha256(destination):
            raise RuntimeError(f"Existing raw hash mismatch: {destination}")
        return saved
    stamp = datetime.now(timezone.utc).isoformat()
    record = {"date": day, "file": destination.name, "url": url_for(day),
              "acquired_utc": stamp, "http_status": None}
    partial = destination.with_suffix(".partial")
    try:
        # The OS trust store is used with certificate verification enabled.
        # On Windows this admits the configured system CA chain rather than
        # relying solely on a separately packaged certifi root list.
        request = Request(record["url"], headers={"User-Agent": "DSC-Grid V8R1 fixed-date sensitivity"})
        with urlopen(request, timeout=180, context=ssl.create_default_context()) as response:
            record["http_status"] = response.status
            with partial.open("wb") as stream:
                for block in iter(lambda: response.read(1024 * 1024), b""):
                    stream.write(block)
        # Parse before admission; keep successful HTTP body bytes unchanged.
        with partial.open(encoding="utf-8") as stream:
            payload = json.load(stream)
        if not isinstance(payload, list) or not payload:
            raise ValueError("B1610 response is not a nonempty JSON record list")
        record.update({"bytes": partial.stat().st_size, "sha256": sha256(partial),
                       "raw_rows": len(payload),
                       "completed_utc": datetime.now(timezone.utc).isoformat()})
        partial.replace(destination)
        save_json(metadata, record)
        print(f"Acquired {day}: {record['raw_rows']} rows, {record['bytes']} bytes", flush=True)
        return record
    except Exception as error:
        record.update({"error": str(error), "failed_utc": datetime.now(timezone.utc).isoformat(),
                       "http_status": getattr(error, "code", record["http_status"])})
        failure_path = raw / f"B1610_{day}.failure.{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')}.json"
        save_json(failure_path, record)
        raise


def acquire(args) -> None:
    args.raw.mkdir(parents=True, exist_ok=True)
    source = args.original_raw / REGISTRY
    target = args.raw / REGISTRY
    if target.exists() and sha256(source) != sha256(target):
        raise RuntimeError("Frozen registry hash mismatch")
    if not target.exists():
        shutil.copyfile(source, target)
    records, failures = [], []
    # Two streams limit provider load and peak memory.
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {pool.submit(acquire_one, day, args.raw): day for day in DATES}
        for future in as_completed(futures):
            try:
                records.append(future.result())
            except Exception as error:
                failures.append({"date": futures[future], "error": str(error)})
    records.sort(key=lambda r: r["date"])
    save_json(args.output / "acquisition_register.json", records)
    save_json(args.output / "acquisition_failures.json", failures)
    history = [json.loads(p.read_text(encoding="utf-8")) | {"outcome": "failed_attempt"}
               for p in sorted(args.raw.glob("B1610_*.failure.*.json"))]
    history.extend(record | {"outcome": "successful_acquisition"} for record in records)
    save_json(args.output / "acquisition_attempt_history.json", history)
    save_json(args.output / "frozen_registry_provenance.json", {
        "file": REGISTRY, "source": "Original V8 frozen acquisition-date registry",
        "bytes": target.stat().st_size, "sha256": sha256(target),
        "limitation": "2026 acquisition-date classification; not a historical 2023 registry snapshot",
    })
    if failures:
        raise RuntimeError(f"{len(failures)} requested days failed; no date substitution allowed")


def load_day(path: Path, day: str, production_ids: set[str], output: Path | None):
    raw = pd.read_json(path)
    if set(raw["settlementDate"].astype(str)) != {day}:
        raise ValueError(f"Unexpected settlement date in {path}")
    periods = pd.to_numeric(raw["settlementPeriod"], errors="coerce")
    if not periods.isin(range(1, 49)).all():
        raise ValueError(f"Unexpected settlement period in {path}")
    rows = raw.loc[raw["bmUnit"].isin(production_ids)].copy()
    duplicate_count = int(rows.duplicated(["bmUnit", "settlementPeriod"]).sum())
    if duplicate_count:
        raise ValueError(f"{duplicate_count} duplicate classified BMU/period keys in {path}")
    quantities = pd.to_numeric(rows["quantity"], errors="coerce")
    rows["quantity"] = quantities.where(np.isfinite(quantities))
    pivot = rows.pivot(index="settlementPeriod", columns="bmUnit", values="quantity").reindex(range(1, 49))
    complete = sorted(pivot.columns[pivot.notna().all(axis=0)])
    incomplete = sorted(set(pivot.columns) - set(complete))
    absent = sorted(production_ids - set(pivot.columns))
    exclusions = []
    for unit in incomplete:
        exclusions.append({"date": day, "bmUnit": unit, "reason": "missing_or_nonfinite_periods",
                           "periods_missing_or_nonfinite": ";".join(map(str, pivot.index[pivot[unit].isna()])),
                           "complete_period_count": int(pivot[unit].notna().sum())})
    for unit in absent:
        exclusions.append({"date": day, "bmUnit": unit, "reason": "absent_all_periods",
                           "periods_missing_or_nonfinite": ";".join(map(str, range(1, 49))),
                           "complete_period_count": 0})
    negative = rows.loc[rows["quantity"] < 0, ["bmUnit", "settlementPeriod", "settlementRunType", "quantity"]].copy()
    negative["average_MW"] = 2 * negative["quantity"]
    values = 2.0 * pivot[complete].astype(float)
    diagnostics = {
        "date": day, "raw_rows": len(raw), "raw_unique_bmus": int(raw["bmUnit"].nunique()),
        "registered_transmission_production_rows": len(rows),
        "registered_transmission_production_observed_units": int(rows["bmUnit"].nunique()),
        "classification_registry_units": len(production_ids),
        "complete_coordinates": len(complete), "incomplete_coordinates": len(incomplete),
        "absent_classified_coordinates": len(absent), "duplicate_bmu_period_rows": duplicate_count,
        "nonfinite_or_nonnumeric_classified_values": int((~np.isfinite(quantities)).sum()),
        "negative_classified_values": len(negative),
        "negative_complete_coordinate_values": int((values < 0).sum().sum()),
        "negative_classified_units": int(negative["bmUnit"].nunique()),
        "converted_average_power_min_MW": float(values.min().min()),
        "converted_average_power_max_MW": float(values.max().max()),
        "settlement_run_type_counts_all_rows": {str(k): int(v) for k, v in raw["settlementRunType"].value_counts(dropna=False).items()},
        "settlement_run_type_counts_classified_rows": {str(k): int(v) for k, v in rows["settlementRunType"].value_counts(dropna=False).items()},
    }
    if output is not None:
        output.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(exclusions, columns=["date", "bmUnit", "reason", "periods_missing_or_nonfinite", "complete_period_count"]).to_csv(output / f"excluded_units_{day}.csv", index=False)
        negative.to_csv(output / f"negative_values_{day}.csv", index=False)
        values.to_csv(output / f"b1610_average_MW_{day}.csv", index_label="settlementPeriod", float_format="%.12g")
    return values, diagnostics


def measure(x: np.ndarray, y: np.ndarray, verify_lp: bool = True):
    if x.shape != y.shape or x.shape[0] != 48 or not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("Expected equal finite 48-period state matrices")
    mean_l1 = float(np.abs(x.mean(axis=0) - y.mean(axis=0)).sum())
    cost = cdist(x, y, metric="cityblock")
    ri, ci = linear_sum_assignment(cost)
    w1 = float(cost[ri, ci].mean())
    same = float(np.abs(x - y).sum(axis=1).mean())
    tolerance = 1e-7 * max(1.0, w1)
    if not mean_l1 <= w1 + tolerance or not w1 <= same + tolerance:
        raise AssertionError("M <= W1 <= same-period inequality failed")
    metrics = {"n_coordinates": x.shape[1], "n_atoms_each_day": 48,
               "M_mean_L1_MW": mean_l1, "W1_empirical_L1_MW": w1,
               "G_shape_MW": w1 - mean_l1,
               "shape_share_percent": 100 * (w1 - mean_l1) / w1 if w1 else None,
               "W1_same_settlement_period_L1_MW": same,
               "same_period_premium_MW": same - w1,
               "same_period_premium_percent": 100 * (same - w1) / w1 if w1 else None,
               "inequalities_verified": True}
    if verify_lp:
        n = x.shape[0]
        constraints = vstack([kron(eye(n), np.ones((1, n))), kron(np.ones((1, n)), eye(n))], format="csr")
        result = linprog(cost.ravel(), A_eq=constraints, b_eq=np.full(2*n, 1/n), bounds=(0, None), method="highs")
        if not result.success or abs(result.fun - w1) > tolerance:
            raise AssertionError(f"Transportation LP / Hungarian mismatch: {result.message}")
        metrics.update({"transportation_LP_W1_MW": float(result.fun),
                        "LP_assignment_abs_difference_MW": float(abs(result.fun - w1)),
                        "transportation_LP_verified": True})
    assignment = pd.DataFrame({"source_settlement_period": ri + 1,
                               "target_settlement_period": ci + 1,
                               "L1_cost_MW": cost[ri, ci]})
    return metrics, assignment


def compare_revision(old_path: Path, new_path: Path, day: str, production_ids: set[str], output: Path):
    keys = ["bmUnit", "settlementPeriod"]
    old, new = pd.read_json(old_path), pd.read_json(new_path)
    for label, frame in (("old", old), ("new", new)):
        if frame.duplicated(keys).any():
            raise ValueError(f"Duplicate keys in {label} raw revision comparison")
    merged = old[keys + ["quantity", "settlementRunType"]].merge(new[keys + ["quantity", "settlementRunType"]], on=keys, how="outer", suffixes=("_old", "_new"), indicator=True)
    common = merged.loc[merged["_merge"] == "both"].copy()
    common["quantity_difference_MWh"] = common["quantity_new"] - common["quantity_old"]
    common["quantity_changed"] = ~(common["quantity_old"].eq(common["quantity_new"]) | (common["quantity_old"].isna() & common["quantity_new"].isna()))
    common["settlement_run_changed"] = ~(common["settlementRunType_old"].eq(common["settlementRunType_new"]) | (common["settlementRunType_old"].isna() & common["settlementRunType_new"].isna()))
    changed = common.loc[common["quantity_changed"] | common["settlement_run_changed"]].copy()
    changed["classified_transmission_production"] = changed["bmUnit"].isin(production_ids)
    changed.to_csv(output / f"provider_revised_keys_{day}.csv", index=False)
    missing = merged.loc[merged["_merge"] != "both"].copy()
    missing.to_csv(output / f"provider_changed_key_coverage_{day}.csv", index=False)
    classified = common.loc[common["bmUnit"].isin(production_ids)]
    def stats(frame):
        absolute = frame["quantity_difference_MWh"].abs()
        return {"common_keys": len(frame), "quantity_changed_keys": int(frame["quantity_changed"].sum()),
                "settlement_run_changed_keys": int(frame["settlement_run_changed"].sum()),
                "nonfinite_quantity_changes": int((frame["quantity_changed"] & absolute.isna()).sum()),
                "max_abs_quantity_change_MWh": float(absolute.max()) if absolute.notna().any() else None,
                "sum_abs_quantity_change_MWh": float(absolute.sum())}
    return {"date": day, "old_sha256": sha256(old_path), "new_sha256": sha256(new_path),
            "raw_bytes_identical": sha256(old_path) == sha256(new_path),
            "old_rows": len(old), "new_rows": len(new),
            "old_only_keys": int((merged["_merge"] == "left_only").sum()),
            "new_only_keys": int((merged["_merge"] == "right_only").sum()),
            "all_units": stats(common), "classified_transmission_production": stats(classified)}


def summarize(frame: pd.DataFrame) -> dict:
    output = {"n_pairs": len(frame), "n_positive_shape_gaps": int((frame["G_shape_MW"] > 1e-6).sum()),
              "n_positive_same_period_premiums": int((frame["same_period_premium_MW"] > 1e-6).sum())}
    for column in ("n_coordinates", "M_mean_L1_MW", "W1_empirical_L1_MW", "G_shape_MW", "shape_share_percent", "same_period_premium_MW", "same_period_premium_percent"):
        output[column] = {"min": float(frame[column].min()), "median": float(frame[column].median()), "max": float(frame[column].max())}
    return output


def analyze(args) -> None:
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    if sha256(args.raw / REGISTRY) != sha256(args.original_raw / REGISTRY):
        raise RuntimeError("Registry differs from original frozen input")
    reference = pd.read_json(args.raw / REGISTRY)
    production = reference.loc[(reference["bmUnitType"] == "T") & (reference["productionOrConsumptionFlag"] == "P") & reference["elexonBmUnit"].str.startswith("T_", na=False)]
    production_ids = set(production["elexonBmUnit"])
    registry_columns = ["elexonBmUnit", "bmUnitName", "fuelType", "bmUnitType", "productionOrConsumptionFlag"]
    # EIC aliases may create multiple registry rows for one BMU. Membership is
    # an identifier set, exactly as in V8; do not duplicate its numeric column.
    duplicate_registry = production.loc[production["elexonBmUnit"].duplicated(keep=False)]
    duplicate_registry.to_csv(output / "registry_duplicate_identifier_rows.csv", index=False)
    registry_info = production[registry_columns].drop_duplicates().rename(columns={"elexonBmUnit": "bmUnit", "bmUnitName": "name_acquisition_date_registry", "fuelType": "fuelType_acquisition_date_registry"})
    if registry_info["bmUnit"].duplicated().any():
        raise ValueError("Conflicting registry labels for the same classified BMU; do not choose one silently")
    save_json(output / "registry_classification_diagnostics.json", {
        "classified_registry_rows": len(production), "unique_classified_BMU_identifiers": len(production_ids),
        "duplicate_identifier_rows": len(duplicate_registry),
        "duplicate_identifiers": sorted(duplicate_registry["elexonBmUnit"].unique()),
        "disposition": "Identical classification/name/fuel labels collapse to one BMU coordinate; full EIC-alias rows retained separately.",
    })
    registry_info.to_csv(output / "classified_registry_units.csv", index=False)
    pivots, diagnostics, register, negative_units = {}, [], [], []
    for day in DATES:
        path = args.raw / f"B1610_{day}.json"
        metadata = json.loads(path.with_suffix(".acquisition.json").read_text(encoding="utf-8"))
        if sha256(path) != metadata["sha256"]:
            raise RuntimeError(f"Acquired input changed: {path}")
        pivots[day], diagnostic = load_day(path, day, production_ids, output / "daily")
        diagnostics.append(diagnostic)
        negative = pd.read_csv(output / "daily" / f"negative_values_{day}.csv")
        if len(negative):
            grouped = negative.groupby("bmUnit", as_index=False).agg(
                negative_period_count=("quantity", "count"), min_outturn_MW=("average_MW", "min"),
                mean_negative_outturn_MW=("average_MW", "mean"), sum_negative_energy_MWh=("quantity", "sum"))
            grouped["date"] = day
            negative_units.append(grouped.merge(registry_info, on="bmUnit", how="left", validate="one_to_one"))
        register.append({"input_role": "new_acquisition", "file": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
        print(f"Analyzed {day}: {pivots[day].shape[1]} complete coordinates", flush=True)
    fixed = sorted(set.intersection(*(set(p.columns) for p in pivots.values())))
    if not fixed:
        raise ValueError("No fixed common coordinate universe")
    pd.DataFrame({"bmUnit": fixed}).to_csv(output / "fixed_common_coordinates.csv", index=False)
    if negative_units:
        pd.concat(negative_units, ignore_index=True).sort_values(["min_outturn_MW", "date", "bmUnit"]).to_csv(output / "negative_outturn_unit_summary.csv", index=False)
    fuel_coverage = []
    for day, pivot in pivots.items():
        admitted = registry_info.loc[registry_info["bmUnit"].isin(pivot.columns)].copy()
        admitted["fuelType_acquisition_date_registry"] = admitted["fuelType_acquisition_date_registry"].fillna("UNSPECIFIED")
        for fuel, units in admitted.groupby("fuelType_acquisition_date_registry"):
            fuel_coverage.append({"date": day, "fuelType_acquisition_date_registry": fuel,
                                  "complete_units": len(units), "fixed_common_units": int(units["bmUnit"].isin(fixed).sum())})
    pd.DataFrame(fuel_coverage).to_csv(output / "registry_fuel_coverage_by_day.csv", index=False)
    pd.DataFrame(diagnostics).to_csv(output / "daily_diagnostics.csv", index=False)
    save_json(output / "daily_diagnostics.json", diagnostics)
    pair_results, universe_rows, assignments = [], [], []
    for jan_idx, january in enumerate(JANUARY):
        for jul_idx, july in enumerate(JULY):
            pair_id = f"{january}__{july}"
            common = sorted(set(pivots[january].columns) & set(pivots[july].columns))
            for universe, coordinates in (("pairwise_common", common), ("fixed_common_eight_days", fixed)):
                metrics, assignment = measure(pivots[january][coordinates].to_numpy(float), pivots[july][coordinates].to_numpy(float))
                prefix = {"pair_id": pair_id, "january_day": january, "july_day": july,
                          "primary_ordinal_pair": jan_idx == jul_idx, "universe": universe}
                pair_results.append(prefix | metrics)
                universe_rows.extend({"pair_id": pair_id, "universe": universe, "bmUnit": unit} for unit in coordinates)
                for key, value in prefix.items():
                    assignment[key] = value
                assignments.append(assignment)
    results = pd.DataFrame(pair_results)
    results.to_csv(output / "pair_metrics.csv", index=False, float_format="%.12g")
    pd.DataFrame(universe_rows).to_csv(output / "pair_coordinate_universes.csv", index=False)
    pd.concat(assignments, ignore_index=True).to_csv(output / "optimal_transport_assignments.csv", index=False, float_format="%.12g")
    summary = {universe: {"primary_four_ordinal_pairs": summarize(frame.loc[frame["primary_ordinal_pair"]]),
                          "secondary_all_sixteen_pairs_nonindependent": summarize(frame)}
               for universe, frame in results.groupby("universe", sort=True)}
    save_json(output / "sensitivity_summary.json", {"design": "Fixed January/July 2023 Wednesday sample; descriptive and observational",
        "state_definition": "Signed B1610 registered-generation BMU outturn vectors in average MW; finite negative values retained",
        "protocol_sha256": sha256(ROOT / "docs/V8R1_ELEXON_SENSITIVITY_PROTOCOL.md"),
        "dates": list(DATES), "n_fixed_common_coordinates": len(fixed), "results": summary,
        "limitations": ["Acquisition-date registry is not a historical 2023 snapshot.",
                        "Production-flagged coordinates include PS-coded units and station-demand names; values are signed outturns, not uniformly nonnegative generation dispatch. Signs alone do not establish causes.",
                        "Days recur in secondary pairs; no independence or significance claim.",
                        "Distances do not establish chronological feasibility or causal operating changes.",
                        "Two months and one weekday do not establish annual or weather-adjusted robustness.",
                        "Positive shape gap magnitude is empirical; nonnegativity follows the metric inequality."]})
    old_pivots, revisions = {}, []
    for day in ORIGINAL_DATES:
        old_path = args.original_raw / f"B1610_{day}.json"
        old_pivots[day], _ = load_day(old_path, day, production_ids, None)
        revisions.append(compare_revision(old_path, args.raw / old_path.name, day, production_ids, output))
        register.append({"input_role": "original_frozen_baseline", "file": old_path.name, "bytes": old_path.stat().st_size, "sha256": sha256(old_path)})
    old_common = sorted(set(old_pivots[ORIGINAL_DATES[0]].columns) & set(old_pivots[ORIGINAL_DATES[1]].columns))
    old_metrics, _ = measure(old_pivots[ORIGINAL_DATES[0]][old_common].to_numpy(float), old_pivots[ORIGINAL_DATES[1]][old_common].to_numpy(float))
    archived = json.loads((ROOT / "results/v8/elexon/b1610_operational_evidence_metrics.json").read_text(encoding="utf-8"))
    checks = []
    for field in ("M_mean_L1_MW", "W1_empirical_L1_MW", "G_shape_MW", "W1_same_settlement_period_L1_MW"):
        difference = abs(old_metrics[field] - archived[field])
        checks.append({"field": field, "recomputed": old_metrics[field], "archived": archived[field], "absolute_difference": difference, "pass": difference <= 1e-7})
    if not all(row["pass"] for row in checks) or len(old_common) != archived["n_common_coordinates"]:
        raise AssertionError("Original frozen baseline does not reproduce")
    new_baseline = results.loc[(results["january_day"] == ORIGINAL_DATES[0]) & (results["july_day"] == ORIGINAL_DATES[1]) & (results["universe"] == "pairwise_common")].iloc[0].to_dict()
    save_json(output / "baseline_and_provider_revisions.json", {"original_frozen_recomputed_metrics": old_metrics,
        "original_common_coordinate_count": len(old_common), "archived_metric_checks": checks,
        "reacquired_original_dates_metrics": new_baseline, "provider_revisions_by_day": revisions})
    register.append({"input_role": "frozen_registry", "file": REGISTRY, "bytes": (args.raw / REGISTRY).stat().st_size, "sha256": sha256(args.raw / REGISTRY)})
    pd.DataFrame(register).to_csv(output / "analysis_input_sha256_register.csv", index=False)
    save_json(output / "environment.json", {"python": sys.version, "platform": platform.platform(),
        "numpy": np.__version__, "pandas": pd.__version__, "scipy": scipy.__version__, "requests": requests.__version__,
        "script_sha256": sha256(Path(__file__)), "completed_utc": datetime.now(timezone.utc).isoformat(),
        "analysis_method": "Hungarian assignments cross-checked by scipy HiGHS transportation LP"})
    save_json(output / "verification.json", {"status": "PASS", "original_archived_metric_checks": len(checks),
        "original_archived_metric_checks_passed": sum(row["pass"] for row in checks),
        "sensitivity_comparisons": len(results), "sensitivity_LP_cross_checks_passed": int(results["transportation_LP_verified"].sum()),
        "sensitivity_metric_inequality_checks_passed": int(results["inequalities_verified"].sum()),
        "max_LP_assignment_abs_difference_MW": float(results["LP_assignment_abs_difference_MW"].max()),
        "raw_input_hashes_verified": len(DATES), "registry_identity_verified": True})
    print(json.dumps({"status": "PASS", "fixed_common_coordinates": len(fixed), "summary": summary}, indent=2), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-raw", type=Path, required=True)
    parser.add_argument("--raw", type=Path, default=ROOT / ".work/elexon_sensitivity/raw")
    parser.add_argument("--output", type=Path, default=ROOT / "results/v8r1/elexon")
    parser.add_argument("--acquire", action="store_true")
    parser.add_argument("--analyze", action="store_true")
    args = parser.parse_args()
    if not (args.acquire or args.analyze):
        parser.error("Specify --acquire and/or --analyze")
    if args.raw.resolve() == args.original_raw.resolve():
        parser.error("New acquisition directory must differ from original frozen directory")
    if args.acquire:
        acquire(args)
    if args.analyze:
        analyze(args)


if __name__ == "__main__":
    main()
