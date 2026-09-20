#!/usr/bin/env python3
"""Audit whether frozen PyPSA-GB generator inputs support a UC chronology claim."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def month_row(label: str, frame: pd.DataFrame) -> dict:
    committable = frame["committable"].fillna(False).astype(bool)
    return {
        "case": label,
        "generator_rows": int(len(frame)),
        "committable_true": int(committable.sum()),
        "positive_min_up_time": int((frame["min_up_time"].fillna(0) > 0).sum()),
        "positive_min_down_time": int((frame["min_down_time"].fillna(0) > 0).sum()),
        "finite_ramp_limit_up": int(frame["ramp_limit_up"].notna().sum()),
        "finite_ramp_limit_down": int(frame["ramp_limit_down"].notna().sum()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("results_root", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    rows = []
    for label, filename in (
        ("January 2020", "january_generator_metadata.csv"),
        ("July 2020", "july_generator_metadata.csv"),
    ):
        rows.append(month_row(label, pd.read_csv(args.results_root / filename)))
    frame = pd.DataFrame(rows)
    args.output.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output / "pypsa_gb_chronology_parameter_audit.csv", index=False)
    chronology_supported = bool(
        frame[["committable_true", "positive_min_up_time", "positive_min_down_time",
               "finite_ramp_limit_up", "finite_ramp_limit_down"]].to_numpy().any()
    )
    verdict = {
        "verdict": "ADMIT" if chronology_supported else "HOLD",
        "chronology_parameterization_present": chronology_supported,
        "interpretation": (
            "The frozen cases contain chronology parameters." if chronology_supported else
            "The frozen cases are LP dispatch inputs: all generators are non-committable, "
            "minimum up/down times are zero, and ramp limits are absent. A GB UC/chronology "
            "comparison would require imputed semantics and is therefore not admitted."
        ),
    }
    (args.output / "pypsa_gb_chronology_gate.json").write_text(
        json.dumps(verdict, indent=2), encoding="utf-8"
    )
    print(json.dumps({"rows": rows, **verdict}, indent=2))


if __name__ == "__main__":
    main()
