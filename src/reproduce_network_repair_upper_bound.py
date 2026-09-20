from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import linprog
from scipy.sparse import lil_matrix, csr_matrix

ROOT = Path(__file__).resolve().parents[1]
V3 = ROOT / "upstream_lock" / "V3"
sys.path.insert(0, str(V3 / "code"))
import dscgrid_model as dm

WIT = ROOT / "results" / "network_repair"
OUT = ROOT / "results" / "reproduction_network_repair"
OUT.mkdir(parents=True, exist_ok=True)

T = 168
ng = len(dm.dec)
nb = len(dm.busids)
dispatch_src = pd.read_csv(V3 / "processed" / "month_07_first_week_dispatch.csv")
target_mean = dispatch_src.drop(columns=["timestamp"]).mean(axis=0).loc[dm.dec["GEN UID"]].to_numpy(float)

u_df = pd.read_csv(WIT / "network_fixed_commitment.csv")
thermal_uids = dm.dec.iloc[dm.urows]["GEN UID"].tolist()
U = u_df[thermal_uids].to_numpy(float)
ku_by_j = {j: k for k, j in enumerate(dm.urows)}

npv = T * ng
nth = T * nb
iz = npv + nth
n = iz + ng
c = np.zeros(n)
c[iz:] = 1.0
lb = np.full(n, -np.inf)
ub = np.full(n, np.inf)
lb[iz:] = 0.0

rows_ts = []
for t in range(T):
    ts = pd.Timestamp(dispatch_src.loc[t, "timestamp"])
    mask = (
        (dm.load_ts.Year.astype(int) == ts.year)
        & (dm.load_ts.Month.astype(int) == ts.month)
        & (dm.load_ts.Day.astype(int) == ts.day)
        & (dm.load_ts.Period.astype(int) == ts.hour + 1)
    )
    idx = np.flatnonzero(mask.to_numpy())
    assert len(idx) == 1
    row = int(idx[0])
    rows_ts.append(row)
    pmin, pmax = dm.avail_at(row)
    for j in range(ng):
        k = t * ng + j
        if j in ku_by_j:
            ku = ku_by_j[j]
            if U[t, ku] > 0.5:
                lb[k], ub[k] = pmin[j], pmax[j]
            else:
                lb[k] = ub[k] = 0.0
        else:
            lb[k], ub[k] = pmin[j], pmax[j]
    for b in range(nb):
        lb[npv + t * nb + b] = -np.pi
        ub[npv + t * nb + b] = np.pi
    lb[npv + t * nb + dm.slack] = 0.0
    ub[npv + t * nb + dm.slack] = 0.0

# Nodal balance equalities.
neq = T * nb
Aeq = lil_matrix((neq, n))
beq = np.zeros(neq)
r = 0
for t, row in enumerate(rows_ts):
    ltot = float(dm.load_ts.loc[row, str(dm.AREA)])
    ld = dm.prop * ltot
    rt = dm.rtpv_at(row)
    for b in range(nb):
        for j, g in dm.dec.iterrows():
            if dm.bi[int(g["Bus ID"])] == b:
                Aeq[r, t * ng + j] = 1.0
        for k, val in enumerate(dm.Bbus[b]):
            if abs(val) > 0:
                Aeq[r, npv + t * nb + k] = -float(val)
        beq[r] = float(ld[b] - rt[b])
        r += 1

# Branch thermal limits + L1 mean-repair epigraph.
nub = T * len(dm.branches) * 2 + ng * 2
Aub = lil_matrix((nub, n))
bub = np.zeros(nub)
r = 0
for t in range(T):
    for l, br in dm.branches.iterrows():
        f = dm.bi[int(br["From Bus"])]
        to = dm.bi[int(br["To Bus"])]
        bl = dm.bl[l]
        rate = dm.rate[l]
        Aub[r, npv + t * nb + f] = bl
        Aub[r, npv + t * nb + to] = -bl
        bub[r] = rate
        r += 1
        Aub[r, npv + t * nb + f] = -bl
        Aub[r, npv + t * nb + to] = bl
        bub[r] = rate
        r += 1
for j in range(ng):
    for t in range(T):
        Aub[r, t * ng + j] = 1.0 / T
    Aub[r, iz + j] = -1.0
    bub[r] = target_mean[j]
    r += 1
    for t in range(T):
        Aub[r, t * ng + j] = -1.0 / T
    Aub[r, iz + j] = -1.0
    bub[r] = -target_mean[j]
    r += 1

t0 = time.time()
res = linprog(
    c,
    A_ub=csr_matrix(Aub),
    b_ub=bub,
    A_eq=csr_matrix(Aeq),
    b_eq=beq,
    bounds=list(zip(lb, ub)),
    method="highs",
)
record = {
    "success": bool(res.success),
    "status": int(res.status),
    "message": res.message,
    "time_s": time.time() - t0,
    "formulation": "network-constrained DC repair LP under a frozen source-native min-up/down commitment witness",
    "global_optimality_claim": False,
    "role": "feasible upper bound on the network-constrained chronological mean-repair distance",
}
if not res.success:
    raise RuntimeError(json.dumps(record, indent=2))

p = res.x[:npv].reshape(T, ng)
means = p.mean(0)
absdiff = np.abs(means - target_mean)
repair = float(absdiff.sum())
record.update({
    "repair_MW": repair,
    "solver_fun": float(res.fun),
    "max_coordinate_change_MW": float(absdiff.max()),
})
pd.DataFrame(p, columns=dm.dec["GEN UID"]).to_csv(OUT / "network_repair_dispatch.csv", index=False)
pd.DataFrame({
    "generator": dm.dec["GEN UID"],
    "target": target_mean,
    "repaired": means,
    "delta": means - target_mean,
    "abs": absdiff,
}).to_csv(OUT / "network_repair_mean.csv", index=False)
(OUT / "network_repair_lp_result.json").write_text(json.dumps(record, indent=2))

expected = 11.9262964643
if abs(repair - expected) > 1e-6:
    raise AssertionError(f"upper-bound replay mismatch: got {repair}, expected {expected}")
print(json.dumps(record, indent=2))
