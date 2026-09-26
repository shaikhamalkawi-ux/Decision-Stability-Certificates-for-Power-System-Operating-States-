from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
V3 = ROOT / 'upstream_lock' / 'V3'
sys.path.insert(0, str(V3 / 'code'))
import dscgrid_model as m

OUT = ROOT / 'results' / 'reproduction'
OUT.mkdir(parents=True, exist_ok=True)
cols = m.dec['GEN UID'].tolist()
ramp = m.dec['Ramp Rate MW/Min'].to_numpy(float) * 60.0
rows=[]
summary={}
for month in (3,7):
    d=pd.read_csv(V3/'processed'/f'month_{month:02d}_first_week_dispatch.csv')
    hs=pd.read_csv(V3/'processed'/f'month_{month:02d}_first_week_hourly_summary.csv')
    p=d[cols].to_numpy(float)
    source_rows=hs['row'].astype(int).to_numpy()
    max_bound=0.0; max_balance=0.0; n_online=0; n_vio=0
    # Per-hour source availability and system balance.
    for t,r in enumerate(source_rows):
        pmin,pmax=m.avail_at(int(r))
        # Thermal Pmin applies only when online; zero is an admitted off-state.
        low=pmin.copy()
        thermal=m.thermal.to_numpy(bool)
        low[thermal & (p[t] <= 1e-6)] = 0.0
        max_bound=max(max_bound,float(np.max(np.maximum(low-p[t],p[t]-pmax))))
        net=float(m.load_ts.loc[int(r),str(m.AREA)]-m.rtpv_at(int(r)).sum())
        max_balance=max(max_balance,abs(float(p[t].sum()-net)))
    # Native steady online-to-online ramp only. Startup/shutdown is deliberately excluded.
    for t in range(1,len(p)):
        onprev=p[t-1]>1e-6; oncur=p[t]>1e-6; diff=p[t]-p[t-1]
        for j,uid in enumerate(cols):
            if onprev[j] and oncur[j]:
                n_online += 1
                vio=max(0.0,abs(float(diff[j]))-float(ramp[j]))
                n_vio += int(vio>1e-7)
                rows.append({'month':month,'hour':t,'GEN_UID':uid,'delta_MW':float(diff[j]),
                             'native_hourly_ramp_limit_MW':float(ramp[j]),'violation_MW':vio})
    summary[str(month)]={'hours':len(p),'max_source_bound_violation_MW':max(0.0,max_bound),
                         'max_system_balance_residual_MW':max_balance,
                         'online_to_online_transitions':n_online,'ramp_exceedances':n_vio,
                         'exact_target_mean_admitted_by_target_trajectory': bool(max_bound<=1e-6 and max_balance<=1e-6 and n_vio==0)}

pd.DataFrame(rows).to_csv(OUT/'native_ramp_witness_audit.csv',index=False)
(OUT/'native_ramp_witness_summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
if not all(v['exact_target_mean_admitted_by_target_trajectory'] for v in summary.values()):
    raise SystemExit(1)
