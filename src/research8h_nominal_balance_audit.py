"""Read-only exact audit of aggregate versus nodal balance redundancy."""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from fractions import Fraction as Q
import gzip
import json
from pathlib import Path
import time

import research8h_standalone_verify as independent

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results/research8h/nominal_balance_audit"
MONTHS = (1, 4, 7, 10)


def write(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def main():
    started = time.perf_counter()
    OUTPUT.mkdir(parents=True, exist_ok=False)
    paths = [Path(__file__), ROOT / "src/research8h_standalone_verify.py",
             ROOT / "docs/research8h/NOMINAL_BALANCE_AUDIT_PROTOCOL.md"]
    directories = [ROOT / f"results/research8h/seasonal_reference/month_{m:02d}" for m in MONTHS]
    paths += [d / name for d in directories for name in ("matrix.npz", "bounds.npz", "row_metadata.csv.gz")]
    bindings = [{"path": str(p), "sha256": independent.sha(p), "bytes": p.stat().st_size} for p in paths]
    write(OUTPUT / "freeze.json", {"utc": datetime.now(timezone.utc).isoformat(), "months": MONTHS,
          "inputs": bindings, "optimization_calls": 0})
    summaries = []
    for month, directory in zip(MONTHS, directories):
        model = independent.load_model(directory)
        with gzip.open(directory / "row_metadata.csv.gz", "rt", newline="") as stream:
            labels = list(csv.DictReader(stream))
        assert len(labels) == model.rows
        records = []
        for hour in range(168):
            selected = [(int(r["row"]), 1 if r["family"] == "aggregate_balance" else -1)
                        for r in labels if int(r["hour_0based"]) == hour
                        and r["family"] in ("aggregate_balance", "nodal_balance")]
            assert len(selected) == 25 and sum(sign == 1 for _, sign in selected) == 1
            coefficients = {}
            rhs = Q(0)
            for row, sign in selected:
                assert model.row_lower[row] == model.row_upper[row]
                rhs += sign * Q(model.row_lower[row])
                for e in range(model.indptr[row], model.indptr[row + 1]):
                    j = model.indices[e]
                    coefficients[j] = coefficients.get(j, Q(0)) + sign * Q(model.data[e])
            coefficients = {j: c for j, c in coefficients.items() if c}
            low = sum((c * Q(model.lower[j] if c > 0 else model.upper[j]) for j, c in coefficients.items()), Q(0))
            high = sum((c * Q(model.upper[j] if c > 0 else model.lower[j]) for j, c in coefficients.items()), Q(0))
            differences = []
            for orientation in (1, -1):
                # Same checker computes nominal and expanded separation without
                # any optimization, sign projection, or changing the model.
                checked = independent.check_ray(model, {r: Q(orientation * s) for r, s in selected}, Q(1e-5))
                differences.append({"orientation": orientation, "check": checked})
            strict_separation = rhs < low or rhs > high
            assert strict_separation == any(c["check"]["strict_pass"] for c in differences)
            records.append({"hour_0based": hour, "exact_redundancy": not coefficients and rhs == 0,
                "rhs_difference": independent.rat(rhs), "box_minimum": independent.rat(low),
                "box_maximum": independent.rat(high), "strict_separation": strict_separation,
                "expanded_separation": any(c["check"]["expanded_pass"] for c in differences),
                "nonzero_difference_coefficients": [{"column": j, "value": independent.rat(c)} for j, c in sorted(coefficients.items())],
                "selected_rows": [{"row": r, "multiplier": s} for r, s in selected], "ray_checks": differences})
        write(OUTPUT / f"month_{month:02d}.json", records)
        summaries.append({"month": month, "hours": 168,
            "exact_redundancy_hours": sum(r["exact_redundancy"] for r in records),
            "strict_separation_hours": sum(r["strict_separation"] for r in records),
            "expanded_separation_hours": sum(r["expanded_separation"] for r in records),
            "maximum_absolute_rhs_difference": independent.rat(max(abs(Q(int(r["rhs_difference"]["numerator"]), int(r["rhs_difference"]["denominator"]))) for r in records))})
        print(json.dumps(summaries[-1]), flush=True)
    assert all(independent.sha(Path(r["path"])) == r["sha256"] and Path(r["path"]).stat().st_size == r["bytes"] for r in bindings)
    write(OUTPUT / "summary.json", {"months": summaries, "all_frozen_inputs_unchanged": True,
          "optimization_calls": 0, "elapsed_s": time.perf_counter() - started,
          "scope": "Selected equality redundancy and box tests only; nonseparation is not feasibility."})


if __name__ == "__main__":
    main()
