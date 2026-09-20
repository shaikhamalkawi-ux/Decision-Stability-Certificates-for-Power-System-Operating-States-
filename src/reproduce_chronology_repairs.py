from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import milp, Bounds, LinearConstraint
from scipy.sparse import lil_matrix, csr_matrix

ROOT=Path(__file__).resolve().parents[1]
V3=ROOT/'upstream_lock'/'V3'
sys.path.insert(0,str(V3/'code'))
import dscgrid_model as m
OUT=ROOT/'results'/'reproduction'; OUT.mkdir(parents=True,exist_ok=True)

COLS=m.dec['GEN UID'].tolist(); NG=len(COLS)
TIDX=np.flatnonzero(m.thermal.to_numpy(bool)); K=len(TIDX)
PMIN=m.dec['PMin MW'].to_numpy(float)
UT=np.ceil(m.dec.loc[TIDX,'Min Up Time Hr'].astype(float)).astype(int).to_numpy()
DT=np.ceil(m.dec.loc[TIDX,'Min Down Time Hr'].astype(float)).astype(int).to_numpy()

def load_month(month:int):
    target=pd.read_csv(V3/'processed'/f'month_{month:02d}_first_week_dispatch.csv')[COLS].to_numpy(float)
    rr=pd.read_csv(V3/'processed'/f'month_{month:02d}_first_week_hourly_summary.csv')['row'].astype(int).to_numpy()
    pmins=[]; pmaxs=[]; net=[]
    for r in rr:
        lo,hi=m.avail_at(int(r)); pmins.append(lo); pmaxs.append(hi)
        net.append(float(m.load_ts.loc[int(r),str(m.AREA)]-m.rtpv_at(int(r)).sum()))
    return target,np.asarray(pmins),np.asarray(pmaxs),np.asarray(net)

def solve_repair(month:int, integer:bool, time_limit:float=120.0):
    target,pmins,pmaxs,net=load_month(month); H=len(target); mu=target.mean(0)
    npv=H*NG; nu=H*K; ny=H*K; nz=H*K
    iu=npv; iy=iu+nu; iz=iy+ny; idp=iz+nz; idm=idp+NG; n=idm+NG
    P=lambda t,j:t*NG+j; U=lambda t,k:iu+t*K+k; Y=lambda t,k:iy+t*K+k; Z=lambda t,k:iz+t*K+k
    DP=lambda j:idp+j; DM=lambda j:idm+j
    c=np.zeros(n); c[idp:idp+NG]=1; c[idm:idm+NG]=1
    lb=np.zeros(n); ub=np.r_[pmaxs.ravel(),np.ones(nu+ny+nz),np.full(2*NG,np.inf)]
    integ=np.zeros(n,np.uint8)
    if integer: integ[iu:idp]=1
    rows=[]; lows=[]; highs=[]
    def add(d,lo=-np.inf,hi=np.inf): rows.append(d); lows.append(lo); highs.append(hi)
    for t in range(H):
        for j in range(NG):
            if str(m.dec.iloc[j]['Category'])=='Hydro': lb[P(t,j)]=pmins[t,j]; ub[P(t,j)]=pmaxs[t,j]
        for k,j in enumerate(TIDX):
            mn=float(PMIN[j]); mx=float(pmaxs[t,j])
            add({P(t,j):1,U(t,k):-mx},hi=0)
            add({P(t,j):-1,U(t,k):mn},hi=0)
            if t==0:
                lb[Y(t,k)]=ub[Y(t,k)]=0; lb[Z(t,k)]=ub[Z(t,k)]=0
            else:
                add({U(t,k):1,U(t-1,k):-1,Y(t,k):-1,Z(t,k):1},lo=0,hi=0)
                add({Y(t,k):1,Z(t,k):1},hi=1)
                su=max(1,t-int(UT[k])+1); d={Y(tau,k):1 for tau in range(su,t+1)}; d[U(t,k)]=-1; add(d,hi=0)
                sd=max(1,t-int(DT[k])+1); d={Z(tau,k):1 for tau in range(sd,t+1)}; d[U(t,k)]=1; add(d,hi=1)
        add({P(t,j):1 for j in range(NG)},lo=float(net[t]),hi=float(net[t]))
    for j in range(NG):
        d={P(t,j):1/H for t in range(H)}; d[DP(j)]=-1; d[DM(j)]=1
        add(d,lo=float(mu[j]),hi=float(mu[j]))
    A=lil_matrix((len(rows),n))
    for r,d in enumerate(rows):
        for q,v in d.items(): A[r,q]=v
    t0=time.time()
    res=milp(c,integrality=integ,bounds=Bounds(lb,ub),constraints=LinearConstraint(csr_matrix(A),np.asarray(lows),np.asarray(highs)),
             options={'time_limit':time_limit,'mip_rel_gap':1e-8,'presolve':True})
    rec={'month':month,'integer':integer,'success':bool(res.success),'status':int(res.status),'message':res.message,
         'time_s':time.time()-t0,'objective_MW':None if res.fun is None else float(res.fun),
         'mip_gap':getattr(res,'mip_gap',None),'dual_bound':getattr(res,'mip_dual_bound',None),
         'formulation':'weak-free-boundary no-network source-native min-up/down mean repair'}
    if res.x is not None:
        p=res.x[:npv].reshape(H,NG); newmu=p.mean(0); diff=newmu-mu
        pd.DataFrame({'generator':COLS,'target_mean_MW':mu,'repaired_mean_MW':newmu,'delta_MW':diff,'abs_delta_MW':np.abs(diff)}).sort_values('abs_delta_MW',ascending=False).to_csv(OUT/f'chron_repair_m{month:02d}_{"mip" if integer else "lp"}.csv',index=False)
        rec['sum_abs_delta_MW']=float(np.abs(diff).sum())
        rec['max_coordinate_change_MW']=float(np.abs(diff).max())
    return rec

records=[
    solve_repair(7,True,120.0),
    solve_repair(3,False,120.0),
]
(OUT/'chronology_repair_reproduction.json').write_text(json.dumps(records,indent=2,default=str))
pd.DataFrame(records).to_csv(OUT/'chronology_repair_reproduction.csv',index=False)
print(json.dumps(records,indent=2,default=str))

# Release assertions; tolerate only numerical rounding.
assert records[0]['success'] and abs(records[0]['objective_MW']-8.020508464286115)<1e-6
assert records[0]['mip_gap'] is None or float(records[0]['mip_gap']) <= 1e-8
assert records[1]['success'] and abs(records[1]['objective_MW']-40.01875927564912)<1e-6
