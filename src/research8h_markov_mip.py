"""First-four full-unit MIP extension, preserving the original Markov results."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import load_npz

from temporal_lp_certificate import assemble
from v8r1_rts_seasonal import inputs, load_model, solve, verify

ROOT = Path(__file__).resolve().parents[1]
SEEDS = list(range(260926100, 260926104))


def save(path, result):
    path.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def changes(status):
    startup, shutdown = np.zeros_like(status), np.zeros_like(status)
    startup[1:] = np.maximum(np.diff(status, axis=0), 0)
    shutdown[1:] = np.maximum(-np.diff(status, axis=0), 0)
    return startup, shutdown


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-v3", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "results/research8h/markov_mip")
    args = parser.parse_args()
    if (args.output / "pre_run_freeze.json").exists():
        raise FileExistsError("Preserve existing results; use a fresh output directory")
    args.output.mkdir(parents=True, exist_ok=True)
    protocol = ROOT / "docs/research8h/MARKOV_MIP_PROTOCOL.md"
    frozen = {"seeds": SEEDS, "seconds_per_case": 60, "number_of_solves_per_case": 1,
              "selection": "first four fixed prior Markov cases; post-LP extension",
              "protocol_sha256": sha(protocol), "script_sha256": sha(Path(__file__)),
              "physical_solver_sha256": sha(ROOT / "src/v8r1_rts_seasonal.py")}
    save(args.output / "pre_run_freeze.json", frozen)
    model = load_model(args.source_v3)
    names, _, pmin, pmax, net, source_paths = inputs(model, args.source_v3, 7)
    witness = ROOT / "results/v8/network_repair"
    p_path, u_path = witness / "network_repair_dispatch.csv", witness / "network_fixed_commitment.csv"
    p = pd.read_csv(p_path)[names].to_numpy(float)
    thermal_names = model.dec.iloc[model.urows]["GEN UID"].tolist()
    u = pd.read_csv(u_path)[thermal_names].to_numpy(float)
    y, z = changes(u)
    means = p.mean(axis=0)
    baseline = verify(model, p, u, pmin, pmax, net, means, "minud", y, z)
    ramp_baseline = verify(model, p, u, pmin, pmax, net, means, "ramp")
    assert baseline["pass"] and ramp_baseline["pass"]
    save(args.output / "baseline_witness_checks.json", {"physical_chronology": baseline, "native_on_on_ramp": ramp_baseline})
    paths = [Path(__file__), protocol, ROOT / "docs/research8h/MARKOV_TWINS_REVIEW.md",
             ROOT / "src/v8r1_rts_seasonal.py", ROOT / "src/temporal_lp_certificate.py",
             p_path, u_path, *source_paths, args.source_v3 / "code/dscgrid_model.py",
             *sorted((args.source_v3 / "raw").rglob("*.csv"))]
    summaries = []
    for seed in SEEDS:
        prior = ROOT / "results/research8h/markov_twins" / f"seed_{seed}"
        directory = args.output / f"seed_{seed}"
        directory.mkdir()
        order_path = prior / "permutation.csv"
        preserve_path = prior / "preservation_and_witness.json"
        order = pd.read_csv(order_path).source_hour_0based.to_numpy(int)
        assert sorted(order) == list(range(168))
        assert np.array_equal(order[:48], np.arange(48)) and np.array_equal(order[120:], np.arange(120, 168))
        matrix, bounds, _, _ = assemble(model, pmin[order], pmax[order], net[order], means)
        archived = load_npz(prior / "matrix.npz")
        delta = matrix - archived
        assert delta.nnz == 0 or np.max(np.abs(delta.data)) == 0
        with np.load(prior / "bounds.npz") as data:
            assert all(np.array_equal(bounds[key], data[key]) for key in bounds)
        save(directory / "paired_input_links.json", {
            "prior_permutation": str(order_path.relative_to(ROOT)), "permutation_sha256": sha(order_path),
            "prior_preservation": str(preserve_path.relative_to(ROOT)), "preservation_sha256": sha(preserve_path),
            "prior_LP_matrix_sha256": sha(prior / "matrix.npz"),
            "prior_LP_bounds_sha256": sha(prior / "bounds.npz"),
            "reconstructed_continuous_model_exact_match": True,
            "all_41_target_means_unchanged": True})
        result = solve(model, 7, "minud", p, pmin[order], pmax[order], net[order], directory, 60)
        result["case"] = f"seed_{seed}"
        result["operational_verdict"] = "UNKNOWN"
        if result["verdict"] == "ADMITTED_RELAXATION":
            actual_p = pd.read_csv(directory / "month_07_minud_dispatch.csv")[names].to_numpy(float)
            actual_u = pd.read_csv(directory / "month_07_minud_commitment.csv")[thermal_names].to_numpy(float)
            actual_y = pd.read_csv(directory / "month_07_minud_startup.csv")[thermal_names].to_numpy(float)
            actual_z = pd.read_csv(directory / "month_07_minud_shutdown.csv")[thermal_names].to_numpy(float)
            chronology = verify(model, actual_p, actual_u, pmin[order], pmax[order], net[order], means, "minud", actual_y, actual_z)
            ramp = verify(model, actual_p, actual_u, pmin[order], pmax[order], net[order], means, "ramp")
            result["archived_witness_replay"] = {"chronology": chronology, "native_on_on_ramp": ramp}
            assert chronology["pass"] and ramp["pass"], result
            result["operational_verdict"] = "ADMITTED_NO_NETWORK_CHRONOLOGY"
        elif result["verdict"] == "REJECTED_RELAXATION":
            result["operational_verdict"] = "REJECTED_NO_NETWORK_MIP"
            result["rejection_evidence"] = "Explicit numerical mixed-integer solver Infeasible; no exact combinatorial proof asserted."
        result["scope"] = "Full individual-unit chronology and exact complete means, with aggregate balance; no network admission claimed."
        save(directory / "result.json", result)
        summaries.append(result)
        save(args.output / "summary.json", summaries)
        print(json.dumps({"seed": seed, "status": result["model_status"],
                          "verdict": result["operational_verdict"], "elapsed_s": result["elapsed_s"]}), flush=True)
        paths.extend([order_path, preserve_path, prior / "matrix.npz", prior / "bounds.npz"])
    pd.DataFrame([{key: value for key, value in result.items() if not isinstance(value, (dict, list))}
                  for result in summaries]).to_csv(args.output / "summary.csv", index=False)
    pd.DataFrame([{"path": str(path), "sha256": sha(path), "bytes": path.stat().st_size}
                  for path in dict.fromkeys(paths)]).to_csv(args.output / "input_manifest.csv", index=False)


if __name__ == "__main__":
    main()
