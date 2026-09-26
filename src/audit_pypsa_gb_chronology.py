#!/usr/bin/env python3
"""Inventory frozen GB chronology fields without inferring upstream absence."""

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
    parser.add_argument("--upstream-parameter-audit", type=Path,
                        help="Optional parameter_admission.csv from the separately pinned source audit")
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
    frozen_parameters_present = bool(
        frame[["committable_true", "positive_min_up_time", "positive_min_down_time",
               "finite_ramp_limit_up", "finite_ramp_limit_down"]].to_numpy().any()
    )
    verdict = {
        "verdict": "HOLD",
        "scope": "native matched-network UC/chronology comparison",
        "frozen_chronology_fields_present": frozen_parameters_present,
        "native_chronology_comparison_admitted": False,
        "interpretation": (
            "Chronology fields are present in the frozen extracts, but field presence alone "
            "does not validate a complete matched-network chronology experiment."
            if frozen_parameters_present else
            "The frozen LP extracts have no activated commitment, minimum-time or ramp fields. "
            "This describes these extracts only; it does not establish that upstream PyPSA-GB "
            "lacks UC parameters. A matched-network chronology comparison remains on hold "
            "pending parameter admission, full model inputs, eligibility and boundary-state validation."
        ),
    }
    if args.upstream_parameter_audit:
        upstream = pd.read_csv(args.upstream_parameter_audit)
        verdict["upstream_source_audit"] = {
            "path": str(args.upstream_parameter_audit),
            "keep_rows": int((upstream["admission"] == "KEEP").sum()),
            "hold_rows": int((upstream["admission"] == "HOLD").sum()),
            "interpretation": "KEEP entries retain their stated scope; optional source-defined "
                              "sensitivities do not by themselves admit a native network experiment.",
        }
    (args.output / "pypsa_gb_chronology_gate.json").write_text(
        json.dumps(verdict, indent=2), encoding="utf-8"
    )
    print(json.dumps({"rows": rows, **verdict}, indent=2))


if __name__ == "__main__":
    main()
