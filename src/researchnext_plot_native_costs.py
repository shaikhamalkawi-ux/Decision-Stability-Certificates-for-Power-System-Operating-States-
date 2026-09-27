"""Visualize already independently verified native expanded cost brackets."""
from pathlib import Path
from fractions import Fraction
import hashlib,json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"results/research_next/native_cost_brackets_figure"
PINS={
"identity":("results/research_next/native_expanded_identity_independent_review/postrun_review.json","8f13f3a1751e03f2e4487127159420d14717bfff2b2c810a5c829f13bfa1b2e1"),
"reverse":("results/research_next/native_expanded_reverse_independent_review/postrun_review_schema2.json","44eaa3634ce474a0c587b0022bfb03e7b4de347403ee38ede7388d1810313e20")}
def sha(b):return hashlib.sha256(b).hexdigest()
def q(v):return Fraction(int(v["numerator"]),int(v["denominator"]))
def main():
 assert not (OUT/"VISUAL_REVIEW.json").exists(), "Preserve the accepted figure"
 data={};bindings=[]
 for role,(path,digest) in PINS.items():
  b=(ROOT/path).read_bytes();assert sha(b)==digest
  data[role]=json.loads(b);bindings.append(dict(path=path,bytes=len(b),sha256=digest))
 lo=[q(data[k]["native_expanded_lower"]) for k in ("identity","reverse")]
 hi=[q(data[k]["native_expanded_upper"]) for k in ("identity","reverse")]
 delta=[q(v) for v in data["reverse"]["signed_difference_interval"]]
 assert delta==[lo[1]-hi[0],hi[1]-lo[0]] and delta[0]>0
 text_delta=data["reverse"]["outward_6dp"]
 assert text_delta==["9972.898506","63039.576470"]
 OUT.mkdir(parents=True,exist_ok=True)
 plt.rcParams.update({"font.family":"DejaVu Sans","font.size":11,"svg.fonttype":"none"})
 fig,ax=plt.subplots(figsize=(11.5,5.5))
 fig.subplots_adjust(left=.23,right=.96,top=.69,bottom=.31)
 colors=["#176c67","#2b58a0"]
 ax.axvspan(float(hi[0])/1e6,float(lo[1])/1e6,color="#e8c56d",alpha=.28,zorder=0)
 for y,l,u,color in zip([1,0],lo,hi,colors):
  a,b=float(l)/1e6,float(u)/1e6
  ax.plot([a,b],[y,y],color=color,lw=5,solid_capstyle="butt")
  ax.plot([a,b],[y,y],"|",color=color,markersize=16,markeredgewidth=2)
  ax.text(a,y+.20,f"L ≈ {float(l):,.2f}",ha="left",color=color,fontsize=10)
  ax.text(b,y-.26,f"U ≈ {float(u):,.2f}",ha="right",color=color,fontsize=10)
 ax.set_yticks([1,0],labels=["Original hour order","Reversed interior hours"])
 ax.tick_params(axis="y",length=0,pad=13)
 ax.set_xlim(1.905,1.985);ax.set_ylim(-.6,1.5)
 ax.set_xticks([1.91,1.93,1.95,1.97])
 ax.set_xlabel("Encoded UC objective (millions of model cost units)",labelpad=10)
 ax.grid(axis="x",alpha=.16)
 for side in ("top","right","left"):ax.spines[side].set_visible(False)
 ax.spines["bottom"].set_color("#bbbbbb")
 fig.text(.055,.94,"Certified cost intervals for two orders of the same hourly inputs",fontsize=15,fontweight="bold",color="#253445")
 fig.text(.055,.87,"Reverse minus original optimum: [9,972.898506, 63,039.576470]",fontsize=12,color="#253445")
 fig.text(.055,.805,"Bars enclose the optima. Shading marks the positive minimum separation.",fontsize=10,color="#526071")
 fig.text(.055,.17,"Actual UnitCommitment.jl encoding; uniform endpoint expansion tau = binary64(1e-5).",fontsize=9.5,color="#526071")
 fig.text(.055,.115,"One synthetic single-bus case. Costs include startup, production and penalized curtailment.",fontsize=9.5,color="#526071")
 fig.text(.055,.06,"Post hoc fidelity extension of one target/service comparison; three other original comparisons remain untransferred.",fontsize=8.7,color="#526071")
 for ext in ("png","svg"):fig.savefig(OUT/("native_cost_intervals."+ext),dpi=180,facecolor="white")
 plt.close(fig)
 caption=("The bars are finite, independently checked lower/upper brackets for the separately informed optima of the original and reverse_4_19 native-penalized models. The original hourly load/reserve/penalty values and multiplicities are unchanged. The pale band is L_reverse minus U_identity, the positive lower endpoint of the exact optimum-difference interval. All figures use the declared native-expanded binary encoding. No strict nominal upper, common-policy regret, calibrated monetary change, independent network or field effect is claimed. This post hoc fidelity extension retains the original four target/service-comparison denominator; the other three have not been transferred to actual native code by this figure. Endpoint labels on bars are approximate; the difference headline rounds outward. Exact fractions remain in the bound source reports.\n")
 (OUT/"CAPTION.md").write_text(caption,encoding="utf-8")
 for x in bindings:assert sha((ROOT/x["path"]).read_bytes())==x["sha256"]
 report=dict(inputs=bindings,source_sha256=sha(Path(__file__).read_bytes()),data_operation="Visualize already verified archived endpoints; no optimizer or new scientific replay",difference=[str(x) for x in delta],outputs=[])
 for p in sorted(OUT.iterdir()):
  if p.name=="FIGURE_MANIFEST.json":continue
  b=p.read_bytes();report["outputs"].append(dict(name=p.name,bytes=len(b),sha256=sha(b)))
 (OUT/"FIGURE_MANIFEST.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(dict(files=[x["name"] for x in report["outputs"]])))
if __name__=="__main__":main()
