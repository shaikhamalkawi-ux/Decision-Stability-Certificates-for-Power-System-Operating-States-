"""Plot previously independently verified energy intervals; no optimization."""
from pathlib import Path
from fractions import Fraction
import hashlib
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"results/research8h/energy_lp_refinement/refined_brackets.json"
OUT=ROOT/"results/research8h/energy_bound_figure"

def value(r): return float(Fraction(int(r["numerator"]),int(r["denominator"])))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

OUT.mkdir(parents=True,exist_ok=True)
source_sha=sha(SOURCE)
records=json.loads(SOURCE.read_text())
series=[("Original order",records[0]["identity_optimum_bounds_MWh"]),
        ("Reordered case 1",records[0]["target_optimum_bounds_MWh"]),
        ("Reordered case 2",records[1]["target_optimum_bounds_MWh"])]
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":11,"axes.labelsize":11,
                    "svg.fonttype":"none","axes.spines.top":False,"axes.spines.right":False})
fig,ax=plt.subplots(figsize=(8.0,3.8))
colors=["#374151","#146080","#A34B2F"]
for y,((label,bounds),color) in enumerate(zip(series,colors)):
    lo,hi=value(bounds["lower"]),value(bounds["upper"])
    ax.plot([lo,hi],[y,y],color=color,lw=5,solid_capstyle="butt")
    ax.plot([lo,lo],[y-.10,y+.10],color=color,lw=1.5)
    ax.plot([hi,hi],[y-.10,y+.10],color=color,lw=1.5)
    qlo=Fraction(int(bounds["lower"]["numerator"]),int(bounds["lower"]["denominator"]))
    qhi=Fraction(int(bounds["upper"]["numerator"]),int(bounds["upper"]["denominator"]))
    showlo=(qlo*100).__floor__()/100; showhi=(qhi*100).__ceil__()/100
    ax.text((lo+hi)/2,y-.20,f"{showlo:,.2f} to {showhi:,.2f}",ha="center",va="bottom",fontsize=10,color=color)
ax.axvline(23195,color="#727272",ls="--",lw=1.1)
ax.text(23195,-.62,"Common nominal cap\n23,195 MWh",ha="left",va="bottom",fontsize=9,color="#4B5563")
ax.set_yticks(range(3),[x[0] for x in series])
ax.invert_yaxis();ax.set_ylim(2.52,-1.04)
ax.set_xlim(22000,26300);ax.set_xticks([22000,23000,24000,25000,26000])
ax.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("{x:,.0f}"))
ax.set_xlabel("Optimal fossil electricity generation (MWh)")
ax.grid(axis="x",color="#DFE3E7",lw=.6);ax.set_axisbelow(True)
ax.tick_params(axis="y",length=0,pad=9)
fig.subplots_adjust(left=.23,right=.98,top=.93,bottom=.28)
fig.text(.23,.095,"Certified lower bounds and feasible binary upper witnesses",fontsize=10)
fig.text(.23,.037,"RTS Area 1, one January week; uniform finite-bound expansion 10⁻⁵",fontsize=9,color="#4B5563")
fig.savefig(OUT/"certified_energy_intervals.png",dpi=220)
fig.savefig(OUT/"certified_energy_intervals.svg")
plt.close(fig)
assert sha(SOURCE)==source_sha
provenance={"source":str(SOURCE.relative_to(ROOT)),"source_sha256":source_sha,"plot_source_sha256":sha(Path(__file__)),
            "optimizer_calls":0,"quantity":"Intervals enclosing optimal fossil electrical generation, not emissions or cost",
            "bounds_domain":"same uncapped original-binary models with every finite bound expanded by Fraction.from_float(1e-5)",
            "cap_line":"nominal cap23195; effective expanded row upper bound23195+tau, visually indistinguishable at this scale",
            "display_rounding":"lower annotations rounded downward, upper annotations upward to two decimals; plotted coordinates from archived exact rational values",
            "image_hashes":{p.name:sha(p) for p in OUT.iterdir() if p.suffix in {".png",".svg"}}}
(OUT/"provenance.json").write_text(json.dumps(provenance,indent=2)+"\n",encoding="utf-8")
print(json.dumps(provenance),flush=True)
