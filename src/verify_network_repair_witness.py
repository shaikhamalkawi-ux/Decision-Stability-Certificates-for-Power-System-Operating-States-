from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
V3 = ROOT / "upstream_lock" / "V3"
sys.path.insert(0, str(V3 / "code"))
import dscgrid_model as m

WIT = ROOT / "results" / "network_repair"
P = pd.read_csv(WIT / "network_repair_dispatch.csv")
Udf = pd.read_csv(WIT / "network_fixed_commitment.csv")
orig = pd.read_csv(V3 / "processed" / "month_07_first_week_dispatch.csv")
cols = m.dec["GEN UID"].tolist()
thermal = m.dec.iloc[m.urows]["GEN UID"].tolist()
assert list(P.columns) == cols
p = P.to_numpy(float)
u = Udf[thermal].to_numpy(int)
T = len(p)
mu = orig[cols].mean().to_numpy(float)
repair = float(np.abs(p.mean(0) - mu).sum())
max_balance = 0.0
max_line = 0.0
max_bound = 0.0
max_ramp = 0.0
minud_bad = []
R = m.dec["Ramp Rate MW/Min"].to_numpy(float) * 60.0
urow_to_k = {j:k for k,j in enumerate(m.urows)}

for t in range(T):
    ts = pd.Timestamp(orig.loc[t, "timestamp"])
    mask = (
        (m.load_ts.Year.astype(int) == ts.year)
        & (m.load_ts.Month.astype(int) == ts.month)
        & (m.load_ts.Day.astype(int) == ts.day)
        & (m.load_ts.Period.astype(int) == ts.hour + 1)
    )
    rr = np.flatnonzero(mask.to_numpy())
    assert len(rr) == 1
    row = int(rr[0])
    pmin, pmax = m.avail_at(row)
    for j in range(len(cols)):
        if j in urow_to_k:
            k = urow_to_k[j]
            lo = pmin[j] * u[t, k]
            hi = pmax[j] * u[t, k]
        else:
            lo, hi = pmin[j], pmax[j]
        max_bound = max(max_bound, max(lo - p[t, j], p[t, j] - hi, 0.0))
    total = float(m.load_ts.loc[row, str(m.AREA)])
    ld = m.prop * total
    rt = m.rtpv_at(row)
    inj = np.zeros(len(m.busids))
    for j, g in m.dec.iterrows():
        inj[m.bi[int(g["Bus ID"])]] += p[t, j]
    inj -= ld - rt
    max_balance = max(max_balance, abs(inj.sum()))
    keep = [i for i in range(len(m.busids)) if i != m.slack]
    th = np.zeros(len(m.busids))
    th[keep] = np.linalg.solve(m.Bbus[np.ix_(keep, keep)], inj[keep])
    fl = np.diag(m.bl) @ m.A.T @ th
    max_line = max(max_line, float(np.max(np.abs(fl) / m.rate)))
    if t > 0:
        for j in m.urows:
            k = urow_to_k[j]
            if u[t, k] and u[t - 1, k]:
                max_ramp = max(max_ramp, max(abs(p[t, j] - p[t - 1, j]) - R[j], 0.0))

for k, j in enumerate(m.urows):
    U = int(np.ceil(float(m.dec.iloc[j]["Min Up Time Hr"])))
    D = int(np.ceil(float(m.dec.iloc[j]["Min Down Time Hr"])))
    seq = u[:, k]
    for t in range(1, T):
        if seq[t] == 1 and seq[t - 1] == 0 and np.any(seq[t:min(T, t + U)] == 0):
            minud_bad.append((thermal[k], "up", t, U))
        if seq[t] == 0 and seq[t - 1] == 1 and np.any(seq[t:min(T, t + D)] == 1):
            minud_bad.append((thermal[k], "down", t, D))

result = {
    "repair_upper_MW": repair,
    "known_lower_bound_MW": 8.020508464286115,
    "max_system_balance_residual_MW": max_balance,
    "max_branch_loading_fraction": max_line,
    "max_power_bound_violation_MW": max_bound,
    "max_native_online_ramp_excess_MW": max_ramp,
    "min_up_down_violations": len(minud_bad),
    "valid_witness": bool(
        max_balance < 1e-6
        and max_line <= 1 + 1e-8
        and max_bound < 1e-6
        and max_ramp < 1e-6
        and not minud_bad
    ),
    "dispatch_sha256": hashlib.sha256((WIT / "network_repair_dispatch.csv").read_bytes()).hexdigest(),
    "commitment_sha256": hashlib.sha256((WIT / "network_fixed_commitment.csv").read_bytes()).hexdigest(),
}
if not result["valid_witness"]:
    raise AssertionError(json.dumps(result, indent=2))
if abs(repair - 11.9262964643) > 1e-6:
    raise AssertionError(f"unexpected repair upper bound {repair}")
print(json.dumps(result, indent=2))
