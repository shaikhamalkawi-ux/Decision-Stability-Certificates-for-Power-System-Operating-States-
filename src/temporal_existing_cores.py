"""Extract sparse explanations for the previously inspected eight-week corpus."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from temporal_information_pilot import ROOT, certificate, save, sha
from v8r1_rts_seasonal import MONTHS, inputs, load_model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-v3", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "results/temporal_information/existing_cores")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    model = load_model(args.source_v3)
    summary = []
    used = [Path(__file__), ROOT / "src/temporal_information_pilot.py", ROOT / "src/check_temporal_core.py",
            ROOT / "src/v8r1_rts_residence_certificate.py", ROOT / "docs/TEMPORAL_EXISTING_CORES_PROTOCOL.md"]
    for month in MONTHS:
        _, target, pmin, pmax, net, paths = inputs(model, args.source_v3, month)
        output = args.output / f"month_{month:02d}"
        output.mkdir(exist_ok=True)
        result, core = certificate(model, pmin, pmax, net, target.sum(axis=0), output)
        reference_path = ROOT / f"results/v8r1/rts_certificate/month_{month:02d}_certificate.json"
        reference = json.loads(reference_path.read_text(encoding="utf-8"))
        assert result["failing_units"] == reference["failing_units"], (month, result["failing_units"], reference["failing_units"])
        record = {"month": month, "verdict": result["verdict"], "reference_rejection_identity": "PASS",
                  "failing_units": result["failing_units"], "core_unit": core["uid"] if core else None,
                  "original_forced_status_atoms": core["initial_atom_count"] if core else None,
                  "core_atoms": core["retained_atom_count"] if core else None,
                  "core_hours_0based": [atom["hour_0based"] for atom in core["atoms"]] if core else None,
                  "independent_core_check": core["independent_rejection_check"] if core else None,
                  "core_extraction_and_checks_s": result["core_extraction_and_checks_s"],
                  "evaluation_status": "previously inspected development corpus; not held out"}
        summary.append(record)
        used.extend([*paths, reference_path])
        save(args.output / "summary.json", summary)
        print(json.dumps(record), flush=True)
    pd.DataFrame(summary).to_csv(args.output / "summary.csv", index=False)
    used.extend([args.source_v3 / "code/dscgrid_model.py", *sorted((args.source_v3 / "raw").rglob("*.csv"))])
    pd.DataFrame([{"path": str(path), "sha256": sha(path), "bytes": path.stat().st_size}
                  for path in dict.fromkeys(used)]).to_csv(args.output / "input_manifest.csv", index=False)


if __name__ == "__main__":
    main()
