"""Replace individual target means by a frozen aggregate fossil-energy cap."""
from __future__ import annotations

from datetime import datetime, timezone
from fractions import Fraction
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, load_npz, save_npz, vstack

from temporal_lp_certificate import check_vector, digest, save, solve_case

ROOT = Path(__file__).resolve().parents[1]
CASES = ["identity", *(f"seed_{s}" for s in range(26092600, 26092604))]
SECONDS = 45


def main():
    archive = ROOT / "results/temporal_information/lp_certificate"
    output = ROOT / "results/research8h/service_cap"
    output.mkdir(parents=True, exist_ok=False)
    protocol = ROOT / "docs/research8h/SERVICE_CAP_PROTOCOL.md"
    metadata = json.loads((archive / "identity/model_metadata.json").read_text())
    names = metadata["unit_names"]
    fossil = [u for u in metadata["thermal_unit_names"] if u != "121_NUCLEAR_1"]
    assert len(fossil) == 23 and len(names) == 41
    thermal = metadata["thermal_unit_names"]
    p_path = ROOT / "results/v8/network_repair/network_repair_dispatch.csv"
    u_path = ROOT / "results/v8/network_repair/network_fixed_commitment.csv"
    p = pd.read_csv(p_path)[names].to_numpy(float)
    u = pd.read_csv(u_path)[thermal].to_numpy(float)
    y, z = np.zeros_like(u), np.zeros_like(u)
    y[1:], z[1:] = np.maximum(np.diff(u, axis=0), 0), np.maximum(-np.diff(u, axis=0), 0)
    witness = np.concatenate([a.ravel() for a in (p, u, y, z)])
    exact_energy = sum((Fraction.from_float(float(v)) for v in p[:, [names.index(s) for s in fossil]].ravel()), Fraction(0))
    rounded = float(exact_energy)
    if Fraction.from_float(rounded) < exact_energy:
        rounded = float(np.nextafter(rounded, np.inf))
    budget = rounded + 1e-6
    manifest = {str(path.relative_to(ROOT)): digest(path) for path in (Path(__file__), protocol, p_path, u_path)}
    models = []
    for case in CASES:
        src = archive / case
        result = json.loads((src / "result.json").read_text())
        for name, key in (("matrix.npz", "matrix_sha256"), ("bounds.npz", "bounds_sha256")):
            assert digest(src / name) == result[key]
        for name in ("matrix.npz", "bounds.npz", "model_metadata.json", "row_metadata.csv.gz", "result.json"):
            manifest[str((src / name).relative_to(ROOT))] = digest(src / name)
        matrix = load_npz(src / "matrix.npz")
        with np.load(src / "bounds.npz") as data:
            bounds = {key: data[key].copy() for key in data.files}
        labels = pd.read_csv(src / "row_metadata.csv.gz")
        keep = ~labels.family.eq("target_mean").to_numpy()
        assert (~keep).sum() == len(names)
        indices = np.asarray([t * len(names) + names.index(s) for t in range(len(p)) for s in fossil])
        cap_row = csr_matrix((np.ones(len(indices)), (np.zeros(len(indices), dtype=int), indices)), shape=(1, matrix.shape[1]))
        matrix = vstack([matrix[keep], cap_row], format="csr")
        bounds["row_lower"] = np.r_[bounds["row_lower"][keep], -np.inf]
        bounds["row_upper"] = np.r_[bounds["row_upper"][keep], budget]
        new_labels = labels.loc[keep].copy().reset_index(drop=True)
        new_labels["row"] = np.arange(len(new_labels))
        row = {"row": len(new_labels), "family": "fossil_energy_cap", "hour_0based": -1, "uid": "ALL"}
        new_labels = pd.concat([new_labels, pd.DataFrame([row])], ignore_index=True)
        directory = output / case
        directory.mkdir()
        save_npz(directory / "matrix.npz", matrix)
        np.savez_compressed(directory / "bounds.npz", **bounds)
        new_labels.to_csv(directory / "row_metadata.csv.gz", index=False, compression="gzip")
        save(directory / "model_metadata.json", {**metadata, "rows": matrix.shape[0], "nonzeros": matrix.nnz, "removed_target_rows": 41, "fossil_units": fossil, "budget_MWh": budget})
        if case == "identity":
            check = check_vector(matrix, bounds, witness)
            save(output / "identity_witness_check.json", check)
            assert check["pass"], check
        models.append((case, directory, matrix, bounds, new_labels.to_dict("records")))
    save(output / "pre_run_freeze.json", {"frozen_at_utc": datetime.now(timezone.utc).isoformat(), "cases": CASES, "seconds_per_case": SECONDS, "input_sha256": manifest, "energy_exact_numerator": str(exact_energy.numerator), "energy_exact_denominator": str(exact_energy.denominator), "budget_MWh": budget, "rounding_slack_MWh": 1e-6, "fossil_units": fossil})
    results = []
    for case, directory, matrix, bounds, labels in models:
        result = solve_case(matrix, bounds, directory, labels, SECONDS, p.size)
        result.update(case=case, matrix_sha256=digest(directory / "matrix.npz"), bounds_sha256=digest(directory / "bounds.npz"))
        save(directory / "result.json", result)
        results.append(result)
        save(output / "summary.json", results)
        print(json.dumps({"case": case, "verdict": result["verdict"], "elapsed_s": result["elapsed_s"]}), flush=True)
    pd.DataFrame([{k: v for k, v in r.items() if not isinstance(v, (dict, list))} for r in results]).to_csv(output / "summary.csv", index=False)


if __name__ == "__main__":
    main()
