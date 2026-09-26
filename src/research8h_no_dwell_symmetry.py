"""Solver-free exact binary64 structural audit of no-dwell permutation symmetry."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import load_npz

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/research8h/no_dwell_symmetry"
PROTOCOL = ROOT / "docs/research8h/NO_DWELL_SYMMETRY_PROTOCOL.md"
BASE = ROOT / "results/research8h/seasonal_transfer/january_identity"
TARGETS = [ROOT / f"results/research8h/seasonal_transfer/seed_{s}" for s in (26093100,26093101,26100100)] + [ROOT / f"results/research8h/day_blocks/days_{s}" for s in (132,213,231,312,321)]
FILES = ("matrix.npz", "bounds.npz", "integrality.npz", "objective.npz", "row_metadata.csv.gz", "model_metadata.json", "native_inputs.npz")
H, G, K, B = 168, 41, 24, 24
NP, NS, NA = H*G, H*K, H*B
OFF = {"P":0, "U":NP, "Y":NP+NS, "Z":NP+2*NS, "theta":NP+3*NS}
REMOVED = {"minimum_up", "minimum_down", "transition", "exclusive_transition"}
STATIC = {"aggregate_balance", "thermal_upper", "thermal_lower", "nodal_balance", "branch_flow", "fossil_energy_cap"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+"\n", encoding="utf-8")


def read(directory):
    a = load_npz(directory/"matrix.npz")
    assert a.format=="csr" and a.has_canonical_format and np.all(np.isfinite(a.data))
    with np.load(directory/"bounds.npz", allow_pickle=False) as z:
        bounds = {k:z[k].copy() for k in z.files}
    assert all(not np.any(np.isnan(v)) for v in bounds.values())
    assert np.all(np.isfinite(bounds["column_lower"])) and np.all(np.isfinite(bounds["column_upper"]))
    with np.load(directory/"objective.npz", allow_pickle=False) as z:
        assert np.array_equal(z["objective"],np.zeros(a.shape[1]))
    with np.load(directory/"integrality.npz", allow_pickle=False) as z:
        integer = z["integrality"].copy()
    with np.load(directory/"native_inputs.npz", allow_pickle=False) as z:
        order = z["source_hour"].copy()
    labels = pd.read_csv(directory/"row_metadata.csv.gz").to_dict("records")
    meta = json.loads((directory/"model_metadata.json").read_text())
    return a,bounds,integer,order,labels,meta


def terms(a, row):
    return {int(c):float(v) for c,v in zip(a.indices[a.indptr[row]:a.indptr[row+1]], a.data[a.indptr[row]:a.indptr[row+1]]) if v != 0}


def template(data):
    a,b,integer,order,labels,meta = data
    assert a.shape[1] == NP+3*NS+NA and len(labels)==a.shape[0]
    assert np.array_equal(np.sort(order), np.arange(H))
    assert np.array_equal(integer, np.r_[np.zeros(NP),np.ones(3*NS),np.zeros(NA)])
    assert meta["offsets"]==OFF and meta["hours"]==H and meta["units"]==G and meta["thermal_units"]==K
    assert meta["individual_mean_constraints"]==0 and meta["budget_MWh"]==23195
    assert set(x["family"] for x in labels)==STATIC|REMOVED
    assert np.array_equal(b["column_lower"][NP:NP+3*NS], np.zeros(3*NS))
    expected = np.ones(3*NS); expected[NS:NS+K]=0; expected[2*NS:2*NS+K]=0
    assert np.array_equal(b["column_upper"][NP:NP+3*NS], expected)
    kept = np.r_[np.arange(NP+NS),np.arange(OFF["theta"],OFF["theta"]+NA)]
    hour = np.r_[np.repeat(np.arange(H),G),np.repeat(np.arange(H),K),np.full(2*NS,-1),np.repeat(np.arange(H),B)]
    names = meta["thermal_unit_names"]; seen=set(); retain=[]; transition_count=0
    caprows=[]
    for i,label in enumerate(labels):
        assert int(label["row"])==i
        family,t,uid=label["family"],int(label["hour_0based"]),str(label["uid"])
        key=(family,t,uid); assert key not in seen; seen.add(key)
        coeff=terms(a,i)
        if family in {"transition","exclusive_transition"}:
            q=names.index(uid); assert 1<=t<H
            y,z=OFF["Y"]+t*K+q,OFF["Z"]+t*K+q
            want={OFF["U"]+t*K+q:1.,OFF["U"]+(t-1)*K+q:-1.,y:-1.,z:1.} if family=="transition" else {y:1.,z:1.}
            assert coeff==want
            assert b["row_lower"][i]==(0. if family=="transition" else -np.inf)
            assert b["row_upper"][i]==(0. if family=="transition" else 1.)
            transition_count += 1
        if family in REMOVED:
            continue
        assert all(c<OFF["Y"] or c>=OFF["theta"] for c in coeff)
        if family=="fossil_energy_cap":
            assert t==-1 and b["row_lower"][i]==-np.inf and b["row_upper"][i]==23195
            fossil=[meta["unit_names"].index(s) for s in meta["fossil_units"]]
            assert len(fossil)==23 and coeff=={h*G+j:1. for h in range(H) for j in fossil}
            caprows.append(i)
        else:
            assert 0<=t<H and all(hour[c]==t for c in coeff)
        retain.append(i)
    assert transition_count==2*(H-1)*K and len(caprows)==1
    assert all((f,t,uid) in seen for f in ("transition","exclusive_transition") for t in range(1,H) for uid in names)
    return kept,retain


def compare(base, target):
    ba,bb,bi,bo,bl,bm=base; a,b,integer,order,labels,meta=target
    bk,br=template(base); kept,retain=template(target)
    assert np.array_equal(bo,np.arange(H)) and np.array_equal(kept,bk)
    assert meta["unit_names"]==bm["unit_names"] and meta["thermal_unit_names"]==bm["thermal_unit_names"]
    assert meta["bus_ids"]==bm["bus_ids"] and meta["fossil_units"]==bm["fossil_units"]
    assert np.array_equal(order[:48],np.arange(48)) and np.array_equal(order[120:],np.arange(120,168))
    mapped=np.arange(a.shape[1])
    for label,width in (("P",G),("U",K),("theta",B)):
        mapped[OFF[label]:OFF[label]+H*width]=(OFF[label]+order[:,None]*width+np.arange(width)).ravel()
    assert np.array_equal(np.sort(mapped[kept]),kept)
    for key in ("column_lower","column_upper"):
        assert np.array_equal(b[key][kept],bb[key][mapped[kept]])
    assert np.array_equal(integer[kept],bi[mapped[kept]])
    lookup={(bl[i]["family"],int(bl[i]["hour_0based"]),str(bl[i]["uid"])):i for i in br}
    used=[]
    for i in retain:
        x=labels[i]; t=int(x["hour_0based"])
        j=lookup[(x["family"],int(order[t]) if t>=0 else -1,str(x["uid"]))]
        assert {int(mapped[c]):v for c,v in terms(a,i).items()}==terms(ba,j)
        assert b["row_lower"][i]==bb["row_lower"][j] and b["row_upper"][i]==bb["row_upper"][j]
        used.append(j)
    assert sorted(used)==sorted(br)
    return {"pass":True,"retained_rows":len(retain),"retained_columns":len(kept),"row_and_column_maps_bijective":True,"binary64_coefficients_and_bounds_exactly_match":True,"transition_templates_pass":True,"archived_zero_feasibility_objectives_checked":True,"cap_and_cap_defined_fossil_energy_functional_invariant":True,"changed_hours":int(np.count_nonzero(order!=np.arange(H)))}


def main():
    OUT.mkdir(parents=True,exist_ok=False)
    paths=[Path(__file__),PROTOCOL]+[d/f for d in [BASE,*TARGETS] for f in FILES]
    manifest=[{"path":str(p),"bytes":p.stat().st_size,"sha256":sha(p)} for p in paths]
    save(OUT/"input_manifest.json",manifest)
    save(OUT/"before_audit.json",{"utc":datetime.now(timezone.utc).isoformat(),"input_manifest_sha256":sha(OUT/"input_manifest.json"),"optimizer_calls":0,"scope":"binary no-dwell projection and objective-set equivalence; not original full-model feasibility"})
    base=read(BASE); template(base); records=[]
    for d in TARGETS:
        r={"case":str(d.relative_to(ROOT)),**compare(base,read(d))}; records.append(r)
        print(json.dumps(r),flush=True)
    assert all(Path(r["path"]).stat().st_size==r["bytes"] and sha(Path(r["path"]))==r["sha256"] for r in manifest)
    save(OUT/"summary.json",{"pass":True,"cases":records,"frozen_bindings":len(manifest),"all_hashes_unchanged":True,"optimizer_calls":0,"tau_domain":"uniform finite-bound expansion 0 <= tau < 1; original U/Y/Z integers"})


if __name__=="__main__":
    main()
