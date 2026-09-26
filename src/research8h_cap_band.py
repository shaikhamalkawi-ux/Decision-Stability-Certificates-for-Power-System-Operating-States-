"""Exact arithmetic consequences of independently verified January bounds."""
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"results/research8h/energy_lp_refinement"
OUT=ROOT/"results/research8h/cap_band"
PROTOCOL=ROOT/"docs/research8h/CAP_BAND_PROTOCOL.md"


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def q(record): return Q(int(record["numerator"]),int(record["denominator"]))
def ceil(value): return -((-value.numerator)//value.denominator)
def decimal_integer(n, digits=6):
    sign="-" if n<0 else ""; n=abs(n); scale=10**digits
    return f"{sign}{n//scale}.{n%scale:0{digits}d}"
def record(value):
    return {"numerator":str(value.numerator),"denominator":str(value.denominator),"approximate":float(value),"floor6":decimal_integer((value*10**6).__floor__()),"ceiling6":decimal_integer(ceil(value*10**6))}
def save(path, obj): path.write_text(json.dumps(obj,indent=2,allow_nan=False)+"\n",encoding="utf-8")


def main():
    OUT.mkdir(parents=True,exist_ok=False)
    paths=[Path(__file__),PROTOCOL,BASE/"refined_brackets.json",BASE/"independent_review.json"]
    frozen=[{"path":str(p),"bytes":p.stat().st_size,"sha256":sha(p)} for p in paths]
    save(OUT/"input_manifest.json",frozen)
    save(OUT/"before_arithmetic.json",{"utc":datetime.now(timezone.utc).isoformat(),"input_manifest_sha256":sha(OUT/"input_manifest.json"),"optimizer_calls":0})
    tau=Q.from_float(1e-5); rows=json.loads((BASE/"refined_brackets.json").read_text()); results=[]
    assert [r["case"] for r in rows]==["seed_26093100","seed_26093101"]
    for r in rows:
        ui=q(r["identity_optimum_bounds_MWh"]["upper"])
        li=q(r["identity_optimum_bounds_MWh"]["lower"])
        lt=q(r["target_optimum_bounds_MWh"]["lower"])
        ut=q(r["target_optimum_bounds_MWh"]["upper"])
        assert 0<li<=ui<lt<=ut
        lo,hi=ui-tau,lt-tau
        assert lo+tau==ui and hi+tau==lt and lo<=Q(23195)<hi
        width=hi-lo; half=width/2
        assert width==q(r["optimum_difference_MWh"]["lower"])
        low6=ceil(lo*10**6); high6=ceil(hi*10**6)-1
        assert lo<=Q(low6,10**6)<=Q(high6,10**6)<hi
        first,last=ceil(lo),ceil(hi)-1
        assert first<=last and lo<=first<hi and lo<=last<hi
        assert Q(first-1)<lo and Q(last+1)>=hi
        results.append({"case":r["case"],"band_left_included_MWh":record(lo),"band_right_excluded_MWh":record(hi),"band_width_MWh":record(width),"safe_closed_decimal_subinterval_MWh":[decimal_integer(low6),decimal_integer(high6)],"first_integer_cap_MWh":first,"last_integer_cap_MWh":last,"integer_cap_count":last-first+1,"original_cap23195_inside":True,"order_blind_worst_case_absolute_error_lower_bound_MWh":record(half),"endpoint_assertions_pass":True})
    assert all(Path(x["path"]).stat().st_size==x["bytes"] and sha(Path(x["path"]))==x["sha256"] for x in frozen)
    save(OUT/"cap_bands.json",{"tau":record(tau),"optimizer_calls":0,"all_input_hashes_unchanged":True,"results":results,"scope":"derived consequences for the same two January expanded original-binary cases; no additional empirical replication"})
    print(json.dumps(results),flush=True)


if __name__=="__main__": main()
