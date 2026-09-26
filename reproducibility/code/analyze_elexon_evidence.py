from __future__ import annotations

import argparse
import gc
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist


parser = argparse.ArgumentParser()
parser.add_argument("raw", type=Path, help="Directory containing the frozen raw JSON files")
parser.add_argument("output", type=Path, help="Directory for derived evidence tables")
parser.add_argument("--reference-file", type=Path, default=None,
                    help="Explicit BMU registry JSON; default is the frozen 2026-09-20 filename")
args = parser.parse_args()

RAW = args.raw
OUT = args.output
OUT.mkdir(parents=True, exist_ok=True)
DATES = ("2023-01-11", "2023-07-12")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_records(path: Path) -> pd.DataFrame:
    with path.open("r", encoding="utf-8") as handle:
        return pd.DataFrame(json.load(handle))


reference_path = args.reference_file if args.reference_file is not None else RAW / "BMU_REFERENCE_ALL_2026-09-20.json"
reference = load_records(reference_path)
production = reference.loc[
    (reference["bmUnitType"] == "T")
    & (reference["productionOrConsumptionFlag"] == "P")
    & reference["elexonBmUnit"].str.startswith("T_", na=False)
].copy()
production_ids = set(production["elexonBmUnit"])
reference_by_id = production.set_index("elexonBmUnit")

pivots: dict[str, pd.DataFrame] = {}
diagnostics: dict[str, dict] = {}
input_register = []

for date in DATES:
    path = RAW / f"B1610_{date}.json"
    raw = load_records(path)
    run_counts = raw["settlementRunType"].value_counts(dropna=False).to_dict()
    rows = raw.loc[raw["bmUnit"].isin(production_ids)].copy()
    duplicate_count = int(rows.duplicated(["bmUnit", "settlementPeriod"]).sum())
    pivot = rows.pivot(index="settlementPeriod", columns="bmUnit", values="quantity").sort_index()
    complete = pivot.columns[pivot.notna().all(axis=0)]
    # B1610 quantity is settlement-period metered energy (MWh).  Convert the
    # 30-minute quantity to average MW before using the dispatch-state metric.
    pivot = 2.0 * pivot.loc[list(range(1, 49)), complete].astype(float)
    pivots[date] = pivot
    diagnostics[date] = {
        "raw_rows": int(len(raw)),
        "registered_transmission_production_rows": int(len(rows)),
        "duplicate_bmu_period_rows": duplicate_count,
        "complete_registered_transmission_production_coordinates": int(pivot.shape[1]),
        "settlement_run_type_counts_all_rows": {str(k): int(v) for k, v in run_counts.items()},
        "converted_average_power_min_MW": float(pivot.min().min()),
        "converted_average_power_max_MW": float(pivot.max().max()),
    }
    input_register.append(
        {"file": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
    )
    del raw, rows
    gc.collect()

common = sorted(set(pivots[DATES[0]].columns) & set(pivots[DATES[1]].columns))
x = pivots[DATES[0]][common].to_numpy(float)
y = pivots[DATES[1]][common].to_numpy(float)

mean_l1 = float(np.abs(x.mean(axis=0) - y.mean(axis=0)).sum())
cost = cdist(x, y, metric="cityblock")
row_ind, col_ind = linear_sum_assignment(cost)
w1 = float(cost[row_ind, col_ind].mean())
shape = w1 - mean_l1
same_period = float(np.abs(x - y).sum(axis=1).mean())

union = sorted(set(pivots[DATES[0]].columns) | set(pivots[DATES[1]].columns))
xu = pivots[DATES[0]].reindex(columns=union, fill_value=0.0).to_numpy(float)
yu = pivots[DATES[1]].reindex(columns=union, fill_value=0.0).to_numpy(float)
union_mean = float(np.abs(xu.mean(axis=0) - yu.mean(axis=0)).sum())
union_cost = cdist(xu, yu, metric="cityblock")
ur, uc = linear_sum_assignment(union_cost)
union_w1 = float(union_cost[ur, uc].mean())

metrics = {
    "source": "Elexon Insights B1610 actual generation output per generation unit",
    "design": "observational matched-weekday two-day comparison; not a field experiment",
    "source_day": DATES[0],
    "target_day": DATES[1],
    "resolution_minutes": 30,
    "state_definition": "common registered transmission-connected production BMUs in the acquisition-date BMU reference table; B1610 half-hour metered-energy coordinates converted to average MW",
    "b1610_unit_conversion": "quantity MWh per 30-minute settlement period divided by 0.5 h (multiplied by 2) to obtain average MW",
    "n_common_coordinates": len(common),
    "n_atoms_each_day": int(x.shape[0]),
    "M_mean_L1_MW": mean_l1,
    "W1_empirical_L1_MW": w1,
    "G_shape_MW": shape,
    "shape_share": shape / w1 if w1 else None,
    "W1_same_settlement_period_L1_MW": same_period,
    "same_period_premium_over_full_W1_MW": same_period - w1,
    "same_period_premium_percent_of_full_W1": 100.0 * (same_period - w1) / w1 if w1 else None,
    "union_zero_padding_sensitivity": {
        "n_coordinates": len(union),
        "M_mean_L1_MW": union_mean,
        "W1_empirical_L1_MW": union_w1,
        "G_shape_MW": union_w1 - union_mean,
    },
    "diagnostics": diagnostics,
    "classification_limitation": "The acquisition-date BMU registry was used to identify transmission production BMUs; it is not asserted to be a historical registry snapshot for 2023.",
    "settlement_run_limitation": "B1610 exposes the latest available settlement-run value per BMU/period; run-type composition is recorded and no cross-run equivalence is assumed.",
}

# Integrate the final Physical Notification ramp segments over each settlement
# period and compare the scheduled trajectory with settled B1610 outturn.  The
# calculation keeps PN and metered outturn distinct; the difference is not
# described as a feasibility violation or operator redispatch.
pn_pivots: dict[str, pd.DataFrame] = {}
pn_diagnostics: dict[str, dict] = {}
for date in DATES:
    path = RAW / f"PN_{date}.json"
    pn = load_records(path)
    pn = pn.loc[pn["bmUnit"].isin(production_ids)].copy()
    pn["timeFrom"] = pd.to_datetime(pn["timeFrom"], utc=True)
    pn["timeTo"] = pd.to_datetime(pn["timeTo"], utc=True)
    pn["duration_s"] = (pn["timeTo"] - pn["timeFrom"]).dt.total_seconds()
    pn = pn.loc[pn["duration_s"] > 0].copy()
    pn["mw_seconds"] = (
        0.5 * (pn["levelFrom"].astype(float) + pn["levelTo"].astype(float))
        * pn["duration_s"]
    )
    integrated = (
        pn.groupby(["settlementPeriod", "bmUnit"], as_index=False)
        .agg(duration_s=("duration_s", "sum"), mw_seconds=("mw_seconds", "sum"))
    )
    integrated["pn_average_MW"] = integrated["mw_seconds"] / integrated["duration_s"]
    complete_groups = integrated.loc[np.isclose(integrated["duration_s"], 1800.0, atol=1e-6)]
    pivot = complete_groups.pivot(
        index="settlementPeriod", columns="bmUnit", values="pn_average_MW"
    ).sort_index()
    complete_columns = pivot.columns[pivot.notna().all(axis=0)]
    pivot = pivot.reindex(index=range(1, 49)).loc[:, complete_columns].astype(float)
    pn_pivots[date] = pivot
    pn_diagnostics[date] = {
        "raw_rows": int(len(pn)),
        "bmu_period_groups": int(len(integrated)),
        "groups_with_exact_1800_s_coverage": int(len(complete_groups)),
        "complete_coordinates": int(pivot.shape[1]),
        "min_group_duration_s": float(integrated["duration_s"].min()),
        "max_group_duration_s": float(integrated["duration_s"].max()),
    }
    input_register.append(
        {"file": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
    )
    del pn, integrated, complete_groups
    gc.collect()

pn_actual_by_day = {}
for date in DATES:
    coords = sorted(set(pn_pivots[date].columns) & set(pivots[date].columns))
    pn_values = pn_pivots[date][coords].to_numpy(float)
    actual_values = pivots[date][coords].to_numpy(float)
    period_l1 = np.abs(pn_values - actual_values).sum(axis=1)
    pn_actual_by_day[date] = {
        "n_coordinates": len(coords),
        "mean_period_L1_MW": float(period_l1.mean()),
        "median_period_L1_MW": float(np.median(period_l1)),
        "max_period_L1_MW": float(period_l1.max()),
        "mean_absolute_coordinate_difference_MW": float(
            np.abs(pn_values - actual_values).mean()
        ),
    }
    pd.DataFrame(
        {
            "settlementPeriod": np.arange(1, 49),
            "PN_to_B1610_L1_MW": period_l1,
        }
    ).to_csv(OUT / f"pn_to_b1610_period_l1_{date}.csv", index=False)

metrics["physical_notification_to_metered_outturn"] = {
    "interpretation": "descriptive PN-to-settled-outturn discrepancy; not a feasibility test, causal redispatch estimate, or field experiment",
    "integration": "piecewise-linear PN segments integrated over complete 30-minute settlement periods",
    "diagnostics": pn_diagnostics,
    "by_day": pn_actual_by_day,
}

pd.DataFrame(
    {
        "bmUnit": common,
        "fuelType_current_registry": [reference_by_id.at[u, "fuelType"] for u in common],
        "name_current_registry": [reference_by_id.at[u, "bmUnitName"] for u in common],
        f"mean_{DATES[0]}_MW": x.mean(axis=0),
        f"mean_{DATES[1]}_MW": y.mean(axis=0),
        "delta_MW": y.mean(axis=0) - x.mean(axis=0),
        "abs_delta_MW": np.abs(y.mean(axis=0) - x.mean(axis=0)),
    }
).sort_values("abs_delta_MW", ascending=False).to_csv(
    OUT / "b1610_mean_coordinate_changes.csv", index=False
)
pd.DataFrame(
    {
        "source_settlement_period": row_ind + 1,
        "target_settlement_period": col_ind + 1,
        "L1_cost_MW": cost[row_ind, col_ind],
    }
).to_csv(OUT / "b1610_optimal_transport_matching.csv", index=False)

for dataset, value_column in (("MNZT", "periodMin"), ("MZT", "periodMin"), ("RURE", "rate1"), ("RDRE", "rate1")):
    summaries = []
    for date in DATES:
        path = RAW / f"{dataset}_{date}.json"
        data = load_records(path)
        values = pd.to_numeric(data[value_column], errors="coerce").dropna()
        summaries.append(
            {
                "dataset": dataset,
                "date": date,
                "rows": int(len(data)),
                "unique_bm_units": int(data["bmUnit"].nunique()),
                "min": float(values.min()) if len(values) else None,
                "median": float(values.median()) if len(values) else None,
                "max": float(values.max()) if len(values) else None,
                "interpretation": "observed updates/events in the requested day; absence is not zero and this is not an exhaustive effective-parameter stock",
            }
        )
        input_register.append(
            {"file": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
        )
    pd.DataFrame(summaries).to_csv(OUT / f"{dataset.lower()}_observed_event_summary.csv", index=False)

physical_coverage = []
for dataset in ("MELS", "MILS"):
    for date in DATES:
        path = RAW / f"{dataset}_{date}.json"
        data = load_records(path)
        physical_coverage.append(
            {
                "dataset": dataset,
                "date": date,
                "rows": int(len(data)),
                "unique_bm_units": int(data["bmUnit"].nunique()),
                "interpretation": "raw physical-limit trajectory evidence retained for provenance; no feasibility conclusion is drawn from this coverage count",
            }
        )
        input_register.append(
            {"file": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
        )
pd.DataFrame(physical_coverage).to_csv(OUT / "mels_mils_source_coverage.csv", index=False)

snapshot_units = [
    "T_KEAD-2",
    "T_LBAR-1",
    "T_TORN-2",
    "T_DRAXX-2",
    "T_SPLN-1",
    "T_HRTL-2",
    "T_HEYM28",
    "T_SHBA-1",
    "T_PEMB-41",
    "T_PEMB-11",
    "T_STAY-1",
    "T_STAY-3",
]
snapshot_rows = []
rate_rows = []
for unit in snapshot_units:
    for date in DATES:
        dynamic_path = RAW / "snapshots" / f"dynamic_{unit}_{date}.json"
        rates_path = RAW / "snapshots" / f"rates_{unit}_{date}.json"
        with dynamic_path.open("r", encoding="utf-8") as handle:
            dynamic_payload = json.load(handle)
        for row in dynamic_payload.get("data", []):
            snapshot_rows.append({"snapshotAt": f"{date}T00:00Z", **row})
        with rates_path.open("r", encoding="utf-8") as handle:
            rates_payload = json.load(handle)
        for row in rates_payload.get("data", []):
            rate_rows.append({"snapshotAt": f"{date}T00:00Z", **row})
        for path in (dynamic_path, rates_path):
            input_register.append(
                {
                    "file": str(path.relative_to(RAW)).replace("\\", "/"),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )

snapshot_table = pd.DataFrame(snapshot_rows)
rates_table = pd.DataFrame(rate_rows)
snapshot_table.to_csv(OUT / "selected_bmu_dynamic_snapshots.csv", index=False)
rates_table.to_csv(OUT / "selected_bmu_rate_snapshots.csv", index=False)
metrics["selected_bmu_parameter_snapshot"] = {
    "selection": "12 high-mean-movement common non-wind/solar transmission production BMUs; deterministic descriptive sample",
    "n_units": len(snapshot_units),
    "dynamic_rows": int(len(snapshot_table)),
    "rate_rows": int(len(rates_table)),
    "MNZT_rows": int((snapshot_table.get("dataset", pd.Series(dtype=str)) == "MNZT").sum()),
    "MZT_rows": int((snapshot_table.get("dataset", pd.Series(dtype=str)) == "MZT").sum()),
    "RURE_rows": int((rates_table.get("dataset", pd.Series(dtype=str)) == "RURE").sum()),
    "RDRE_rows": int((rates_table.get("dataset", pd.Series(dtype=str)) == "RDRE").sum()),
    "interpretation": "effective snapshots valid at the requested instant; sampled evidence of nonzero operational parameters, not a complete-system chronology calibration",
}

input_register.append(
    {
        "file": reference_path.name,
        "bytes": reference_path.stat().st_size,
        "sha256": sha256(reference_path),
    }
)
(OUT / "b1610_operational_evidence_metrics.json").write_text(
    json.dumps(metrics, indent=2), encoding="utf-8"
)
pd.DataFrame([metrics | {"diagnostics": json.dumps(diagnostics)}]).to_csv(
    OUT / "b1610_operational_evidence_metrics.csv", index=False
)
pd.DataFrame(input_register).drop_duplicates("file").sort_values("file").to_csv(
    OUT / "input_sha256_register.csv", index=False
)
print(json.dumps(metrics, indent=2))
