"""Present closed, independently checked energy differences; no optimization.

Every prescribed case remains visible. Exact arithmetic defines all annotations;
binary64 conversion is used only to place graphical coordinates.
"""
from pathlib import Path
from fractions import Fraction
import hashlib
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/research8h/three_week_energy_figure"
INPUTS = {
    "unrestricted": "results/research8h/energy_lp_refinement/refined_brackets.json",
    "clock_week1": "results/research8h/hour_of_day_uncapped/energy_brackets.json",
    "clock_fresh": "results/research8h/fresh_january_energy/energy_brackets.json",
    "independent_review": "results/research8h/fresh_energy_review/postrun.json",
    "unrestricted_review": "results/research8h/energy_lp_refinement/independent_review.json",
    "clock_week1_review": "results/research8h/hour_of_day_uncapped/independent_postrun_review.json",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(record):
    return Fraction(int(record["numerator"]), int(record["denominator"]))


def outward(value, upper=False, places=6):
    scale = 10 ** places
    n = -((-value * scale).__floor__()) if upper else (value * scale).__floor__()
    sign = "−" if n < 0 else ""
    whole, decimal = divmod(abs(n), scale)
    return f"{sign}{whole:,}.{decimal:0{places}d}"


def packed(value):
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def main():
    # Existence is not an execution gate: the parent must supply a closed review.
    loaded = {key: json.loads((ROOT / path).read_text(encoding="utf-8"))
              for key, path in INPUTS.items()}
    review = loaded["independent_review"]
    assert review["status"] == "INDEPENDENT_FRESH_ENERGY_POSTRUN_PASS"
    assert review["ordinary_denominator"] == 4 and review["all_hashes_unchanged"]
    bindings = {path: sha(ROOT / path) for path in INPUTS.values()}
    normalized = {key.replace("\\", "/"): value for key, value in review["input_and_result_hashes"].items()}
    assert normalized[INPUTS["clock_fresh"]] == bindings[INPUTS["clock_fresh"]]
    old_review = loaded["unrestricted_review"]
    assert old_review["status"] == "PASS_COMPLETE"
    assert old_review["output_summary_bindings"]["refined_brackets.json"] == bindings[INPUTS["unrestricted"]]
    hod_review = loaded["clock_week1_review"]
    assert hod_review["status"] == "INDEPENDENT_HOD_UNCAPPED_POSTRUN_PASS"
    normalized_hod = {key.replace("\\", "/"): value for key, value in hod_review["input_and_result_hashes"].items()}
    assert normalized_hod[INPUTS["clock_week1"]] == bindings[INPUTS["clock_week1"]]
    rows = []
    for group, expected in (("unrestricted", ["seed_26093100", "seed_26093101"]),
                            ("clock_week1", ["seed_26093200", "seed_26093201"]),
                            ("clock_fresh", ["seed_26093210", "seed_26093211",
                                             "seed_26093220", "seed_26093221"])):
        records = loaded[group]
        assert [r["case"] for r in records] == expected
        for record in records:
            case = record["case"]
            if group == "unrestricted":
                identity = record["identity_optimum_bounds_MWh"]
                target = record["target_optimum_bounds_MWh"]
                li, ui, lt, ut = q(identity["lower"]), q(identity["upper"]), q(target["lower"]), q(target["upper"])
            else:
                li, ui, lt = q(record["identity_lower_MWh"]), q(record["identity_reference_upper_MWh"]), q(record["lower_MWh"])
                ut = q(record["upper_MWh"]) if record["upper_MWh"] is not None else None
            assert li > 0 and li <= ui
            if ut is not None:
                assert lt <= ut
                lo, hi = lt - ui, ut - li
                assert lo == q(record["optimum_difference_MWh"]["lower"])
                assert hi == q(record["optimum_difference_MWh"]["upper"])
                status = "finite_optimum_difference_enclosure"
                relative = [100 * (lt / ui - 1), 100 * (ut / li - 1)] if lt > 0 else None
            else:
                # No finite optimum is inferred from a numerical bound alone.
                lo, hi, status, relative = lt - ui, None, "no_accepted_target_upper", None
            week = 1 if group != "clock_fresh" else (2 if case in expected[:2] else 3)
            rows.append({"case": case, "week": week, "group": group, "status": status,
                         "lower": packed(lo), "upper": packed(hi) if hi is not None else None,
                         "difference_display_MWh": [outward(lo), outward(hi, True) if hi is not None else None],
                         "relative_percent": [packed(x) for x in relative] if relative else None,
                         "relative_display_percent": [outward(relative[0]), outward(relative[1], True)] if relative else None})

    OUT.mkdir(parents=True, exist_ok=False)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "svg.fonttype": "none", "axes.spines.top": False,
                         "axes.spines.right": False, "axes.spines.left": False})
    fig, ax = plt.subplots(figsize=(8.3, 5.4))
    colors = {"unrestricted": "#76645A", "clock_week1": "#176482", "clock_fresh": "#176482"}
    xmax = max(float(q(r["upper"] or r["lower"])) for r in rows)
    xmin = min(0, min(float(q(r["lower"])) for r in rows))
    padding = max(100, (xmax - xmin) * .07)
    for i, row in enumerate(rows):
        lo = float(q(row["lower"]))
        hi = float(q(row["upper"])) if row["upper"] else None
        color = colors[row["group"]]
        if hi is not None:
            ax.plot([lo, hi], [i, i], color=color, lw=3.5, solid_capstyle="butt")
            ax.vlines([lo, hi], i - .09, i + .09, color=color, lw=1.2)
            label = f"{outward(q(row['lower']), places=1)} to {outward(q(row['upper']), True, 1)}"
        else:
            ax.plot(lo, i, marker="|", color=color, ms=9)
            label = "No accepted upper witness"
        ax.text(xmax + padding * .3, i, label, va="center", ha="left", fontsize=8.5, color=color)
    labels = [f"Week {r['week']} · {r['case'].removeprefix('seed_')}" for r in rows]
    ax.set_yticks(range(len(rows)), labels)
    ax.tick_params(axis="y", length=0, pad=8)
    ax.set_ylim(len(rows) - .5, -.6)
    ax.set_xlim(xmin - padding, xmax + padding)
    ax.axvline(0, color="#555555", ls="--", lw=1)
    ax.axhline(1.5, color="#C6CDD2", lw=.7)
    ax.axhline(3.5, color="#C6CDD2", lw=.7)
    ax.axhline(5.5, color="#C6CDD2", lw=.7)
    ax.grid(axis="x", color="#E2E6E9", lw=.6)
    ax.set_axisbelow(True)
    ax.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("{x:,.0f}"))
    ax.set_xlabel("Target optimum − original-order optimum (MWh)")
    fig.subplots_adjust(left=.24, right=.74, top=.95, bottom=.22)
    fig.text(.24, .105, "First two rows: unrestricted hours. Remaining six: hour of day preserved.", fontsize=8.7)
    fig.text(.24, .060, "Exact-bound enclosures, not confidence intervals. Zero crossing leaves the sign unresolved.", fontsize=8.4)
    fig.text(.24, .020, "Same RTS Area 1, three January weeks; uniform numerical finite-bound expansion 10⁻⁵.", fontsize=8.4)
    fig.savefig(OUT / "optimal_energy_differences.png", dpi=220)
    fig.savefig(OUT / "optimal_energy_differences.svg")
    plt.close(fig)
    assert all(sha(ROOT / path) == digest for path, digest in bindings.items())
    result = {"input_sha256": bindings, "plot_source_sha256": sha(Path(__file__)),
              "optimizer_calls": 0, "prescribed_cases": 8, "records": rows,
              "display_rounding": "outward exact rational rounding, one decimal in figure and six in tabulated metadata",
              "limits": "No confidence intervals, statistical independence, seasonal or external-network generalization inferred.",
              "images": {p.name: sha(p) for p in OUT.iterdir() if p.suffix in {".png", ".svg"}}}
    (OUT / "provenance.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(rows), "output": str(OUT)}))


if __name__ == "__main__":
    main()
