"""Exact arithmetic-only relative-optimum bounds; no optimizer or model edits."""
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

BASE=Path(__file__).resolve().parent
SOURCE=BASE/"refined_brackets.json"

def q(record): return Q(int(record["numerator"]),int(record["denominator"]))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def decimal_outward(value,digits,upper=False):
    scale=10**digits
    integer=-((-value.numerator*scale)//value.denominator) if upper else (value.numerator*scale)//value.denominator
    sign="-" if integer<0 else "";integer=abs(integer)
    return f"{sign}{integer//scale}.{integer%scale:0{digits}d}"
def record(value):
    return {"numerator":str(value.numerator),"denominator":str(value.denominator),"approximate":float(value),
            "decimal_floor_6dp":decimal_outward(value,6),"decimal_ceiling_6dp":decimal_outward(value,6,True)}

output=BASE/"relative_penalty_bounds.json"
if output.exists(): raise FileExistsError("Preserve the existing arithmetic addendum")
source_sha=sha(SOURCE)
rows=json.loads(SOURCE.read_text(encoding="utf-8"));results=[]
for row in rows:
    li=q(row["identity_optimum_bounds_MWh"]["lower"])
    eref=q(row["identity_optimum_bounds_MWh"]["upper"])
    lt=q(row["target_optimum_bounds_MWh"]["lower"])
    ut=q(row["target_optimum_bounds_MWh"]["upper"])
    assert 0<li<=eref and 0<lt<=ut
    lo=lt/eref-1;hi=ut/li-1
    assert lo<=hi
    assert q(row["optimum_difference_MWh"]["lower"])==lt-eref
    assert q(row["optimum_difference_MWh"]["upper"])==ut-li
    results.append({"case":row["case"],"strictly_positive_optimum_bounds_verified":True,
        "relative_optimum_penalty":{"lower":record(lo),"upper":record(hi)},
        "relative_optimum_penalty_percent":{"lower":record(100*lo),"upper":record(100*hi)},
        "unchanged_absolute_optimum_difference_MWh":row["optimum_difference_MWh"],
        "formula":"[L_target/E_reference - 1, U_target/L_identity - 1]",
        "scope":"target optimum / identity optimum - 1 for the same uncapped uniformly expanded original-binary models"})
assert sha(SOURCE)==source_sha
payload={"utc":datetime.now(timezone.utc).isoformat(),"arithmetic_only":True,"optimization_calls":0,
    "source_refined_brackets_sha256":source_sha,"addendum_script_sha256":sha(Path(__file__)),
    "interval_is_not_absolute_difference_divided_by_reference":True,"results":results}
output.write_text(json.dumps(payload,indent=2,allow_nan=False)+"\n",encoding="utf-8")
lines=["case,relative_penalty_lower_ratio_floor6,relative_penalty_upper_ratio_ceiling6,relative_penalty_lower_percent_floor6,relative_penalty_upper_percent_ceiling6,scope"]
for row in results:
    ratio=row["relative_optimum_penalty"];pct=row["relative_optimum_penalty_percent"]
    lines.append(",".join([row["case"],ratio["lower"]["decimal_floor_6dp"],ratio["upper"]["decimal_ceiling_6dp"],pct["lower"]["decimal_floor_6dp"],pct["upper"]["decimal_ceiling_6dp"],"uncapped uniformly expanded original-binary optimal fossil-energy ratio"]))
(BASE/"relative_penalty_bounds.csv").write_text("\n".join(lines)+"\n",encoding="utf-8")
print(json.dumps([{"case":r["case"],"lower_percent":r["relative_optimum_penalty_percent"]["lower"]["decimal_floor_6dp"],"upper_percent":r["relative_optimum_penalty_percent"]["upper"]["decimal_ceiling_6dp"]} for r in results]),flush=True)
