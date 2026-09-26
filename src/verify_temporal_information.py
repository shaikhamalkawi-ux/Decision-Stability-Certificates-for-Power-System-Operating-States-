"""Reconstruct archived pilot models and recheck saved evidence without solving."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import load_npz

from check_temporal_core import compatible_counts
from temporal_information_pilot import ROOT, certificate, nodal_check, transitions
from temporal_lp_certificate import assemble, digest, exact_ray_check
from v8r1_rts_residence_certificate import POWER_TOL, ENERGY_TOL, propagate
from v8r1_rts_seasonal import inputs, load_model, verify


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-v3", type=Path, required=True)
    parser.add_argument("--report", type=Path, default=ROOT / "results/temporal_information/reconstruction_verification.json")
    args = parser.parse_args()
    source = load_model(args.source_v3)
    base = ROOT / "results/temporal_information"
    columns, _, pmin, pmax, demand, paths = inputs(source, args.source_v3, 7)
    rows = pd.read_csv(paths[1])["row"].to_numpy(int)
    witness = ROOT / "results/v8/network_repair"
    p = pd.read_csv(witness / "network_repair_dispatch.csv")[columns].to_numpy(float)
    ti = np.asarray(source.urows)
    u = pd.read_csv(witness / "network_fixed_commitment.csv")[source.dec.iloc[ti]["GEN UID"]].to_numpy(float)
    y, z = transitions(u)
    positive = verify(source, p, u, pmin, pmax, demand, p.mean(0), "minud", y, z)
    network, nodal = nodal_check(source, p, rows)
    assert positive["pass"] and network["pass"]
    packages = np.column_stack([rows, nodal, pmin, pmax, p, u])
    twins = read(base / "twins/summary.json")
    assert len(twins) == 17
    reconstructed = []
    for record in twins:
        name = record["case"]
        order = pd.read_csv(base / "twins" / name / "permutation.csv")["source_hour_0based"].to_numpy(int)
        assert np.array_equal(np.sort(order), np.arange(168))
        assert np.array_equal(order[:48], np.arange(48)) and np.array_equal(order[-48:], np.arange(120, 168))
        restored = packages[order][np.argsort(order)]
        assert np.array_equal(restored, packages)
        row = {"case": name, "permutation_and_boundary_check": "PASS", "package_restoration": "PASS"}
        if name == "identity" or record["seed"] < 26092604:
            directory = base / "lp_certificate" / name
            matrix, bounds, _, _ = assemble(source, pmin[order], pmax[order], demand[order], p.mean(0))
            archived = load_npz(directory / "matrix.npz")
            assert matrix.shape == archived.shape and (matrix != archived).nnz == 0
            with np.load(directory / "bounds.npz") as archive_bounds:
                assert set(archive_bounds.files) == set(bounds)
                assert all(np.array_equal(bounds[key], archive_bounds[key]) for key in bounds)
            row["archived_model_matches_reconstructed_native_inputs"] = "PASS"
            if name != "identity":
                cert = read(directory / "dual_certificate.json")
                multipliers = np.zeros(matrix.shape[0])
                for item in cert["multipliers"]:
                    multipliers[item["row"]] = float.fromhex(item["value_hex"])
                check = exact_ray_check(matrix, bounds, multipliers)
                assert check["pass"] and check["robust_pass"]
                assert check["exact_gap_numerator"] == cert["verification"]["exact_gap_numerator"]
                assert check["exact_gap_denominator"] == cert["verification"]["exact_gap_denominator"]
                row["exact_reconstructed_model_separation"] = "PASS"
                row["robust_separation_gap"] = check["robust_separation_gap"]
        reconstructed.append(row)
    cores = []
    for record in read(base / "existing_cores/summary.json"):
        if record["core_atoms"] is None:
            continue
        month = record["month"]
        core = read(base / f"existing_cores/month_{month:02d}/compact_core.json")
        _, target, low, high, net, _ = inputs(source, args.source_v3, month)
        hydro = source.dec.Category.eq("Hydro").to_numpy()
        initial = np.zeros_like(low)
        initial[:, hydro] = low[:, hydro]
        bound_low, bound_high, _ = propagate(initial, high, target.sum(0), net, ti,
                                            source.dec.iloc[ti]["PMin MW"].to_numpy(float))
        unit = columns.index(core["uid"])
        native = source.dec.iloc[unit]
        up, down = int(np.ceil(native["Min Up Time Hr"])), int(np.ceil(native["Min Down Time Hr"]))
        energy = target[:, unit].sum()
        nlow = max(0, int(np.ceil((energy - ENERGY_TOL) / (native["PMax MW"] + POWER_TOL))))
        nhigh = min(168, int(np.floor((energy + ENERGY_TOL) / (native["PMin MW"] - POWER_TOL))))
        assert (up, down, nlow, nhigh) == (core["min_up_hours"], core["min_down_hours"], core["energy_count_lower"], core["energy_count_upper"])
        on, off = [], []
        for atom in core["atoms"]:
            hour = atom["hour_0based"]
            if atom["status"]:
                assert bound_low[hour, unit] > POWER_TOL
                on.append(hour)
            else:
                assert bound_high[hour, unit] < native["PMin MW"] - POWER_TOL
                off.append(hour)
        assert not compatible_counts(168, on, off, up, down, nlow, nhigh)
        for hour in on:
            assert compatible_counts(168, [h for h in on if h != hour], off, up, down, nlow, nhigh)
        for hour in off:
            assert compatible_counts(168, on, [h for h in off if h != hour], up, down, nlow, nhigh)
        cores.append({"month": month, "atoms": len(on) + len(off), "reconstructed_forcing_and_independent_core_replay": "PASS"})
    result = {"result": "PASS", "optimization_invoked": False,
              "positive_chronology": positive, "positive_network": network,
              "paired_cases": reconstructed, "previous_corpus_cores": cores,
              "scope": "Native-input model reconstruction and exact arithmetic checking; shared propagation implementation with independent run-age logic.",
              "verifier_sha256": digest(Path(__file__))}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"result": "PASS", "paired_permutations_and_control": len(reconstructed),
                      "reconstructed_LP_models": 5, "exact_negative_certificates": 4, "rechecked_cores": len(cores)}))


if __name__ == "__main__":
    main()
