"""Plot the prespecified first paired-order case from recorded pilot results."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from v8r1_rts_seasonal import inputs, load_model

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-v3", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "results/temporal_information/figures")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    model = load_model(args.source_v3)
    _, _, _, _, net, _ = inputs(model, args.source_v3, 7)
    case = ROOT / "results/temporal_information/twins/seed_26092600"
    order = pd.read_csv(case / "permutation.csv")["source_hour_0based"].to_numpy(int)
    negative = json.loads((case / "full_solver_crosscheck.json").read_text())
    positive = json.loads((ROOT / "results/temporal_information/twins/positive_witness_verification.json").read_text())
    assert negative["verdict"] == "REJECTED_RELAXATION"
    assert positive["network"]["pass"] and positive["chronology"]["pass"]
    assert np.array_equal(np.sort(net), np.sort(net[order]))
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
                         "axes.spines.right": False, "svg.fonttype": "none"})
    fig = plt.figure(figsize=(11, 7.1), layout="constrained")
    grid = fig.add_gridspec(2, 2, height_ratios=[1.45, 1])
    ax = fig.add_subplot(grid[0, :])
    hours = np.arange(1, 169)
    ax.axvspan(.5, 48.5, color="#eff2f5", zorder=0)
    ax.axvspan(120.5, 168.5, color="#eff2f5", zorder=0)
    ax.plot(hours, net, color="#2563a6", lw=1.7, label="Original order: verified feasible network schedule")
    ax.plot(hours, net[order], color="#ba492f", lw=1.2, alpha=.85,
            label="Permuted order: no feasible schedule with the same unit means")
    ax.set(xlabel="Position in the synthetic week (hour)", ylabel="Net demand (MW)",
           xlim=(1, 168), title="Same hourly packages and generator means; different chronological verdicts")
    ax.legend(loc="upper left", frameon=False, fontsize=9)
    ax.text(.015, .025, "Shaded: first and last 48 hours are unchanged", transform=ax.transAxes, fontsize=9)
    ax.grid(axis="y", alpha=.2)
    ordered = fig.add_subplot(grid[1, 0])
    ordered.plot(hours, np.sort(net), color="#2563a6", lw=3, label="Original")
    ordered.plot(hours, np.sort(net[order]), color="#ba492f", lw=1.3, ls="--", label="Permuted")
    ordered.set(xlabel="Sorted rank", ylabel="Net demand (MW)", title="The sorted demand curves coincide exactly")
    ordered.legend(frameon=False)
    ordered.grid(alpha=.2)
    text_ax = fig.add_subplot(grid[1, 1])
    text_ax.axis("off")
    text_ax.text(0, .95, "What the experiment establishes", fontsize=12, weight="bold", va="top")
    text_ax.text(0, .78, "168 identical hourly packages; only their order changes.\n"
                 "All 41 generator weekly means are preserved.\n"
                 "The full hourly multiset is checked by inverse permutation.\n\n"
                 "Positive: independently verified DC-network witness.\n"
                 "Negative: full unit-level MILP terminates Infeasible.\n"
                 "The simple single-unit screen returns UNKNOWN.", va="top", fontsize=9.8, linespacing=1.7)
    fig.savefig(args.output / "paired_order_example.png", dpi=180)
    fig.savefig(args.output / "paired_order_example.svg")
    plt.close(fig)
    (args.output / "caption.txt").write_text(
        "Prespecified seed 26092600 applied to the repaired July RTS witness. "
        "Demand is shown for illustration; all time-varying modeled conditions and witness rows "
        "are jointly permuted. An exact inverse-permutation check establishes hourly-multiset "
        "identity. The first and last 48 hours are fixed. The original full-network witness "
        "passes independent validation. The permuted case is infeasible even in the no-network "
        "minimum-up/down MILP with identical complete unit means; it is not merely a failed "
        "replay of the seed dispatch. This is a synthetic model counterexample, not a field experiment.\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
