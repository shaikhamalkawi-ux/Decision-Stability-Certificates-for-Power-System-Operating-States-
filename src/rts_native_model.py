from __future__ import annotations
import numpy as np, pandas as pd
from scipy.optimize import milp, Bounds, LinearConstraint
from scipy.sparse import lil_matrix, csr_matrix
from pathlib import Path

PACKAGE_ROOT=Path(__file__).resolve().parents[1]
BASE=PACKAGE_ROOT/'raw/RTS-GMLC_v0.2.3'
AREA=1
buses=pd.read_csv(BASE/'bus.csv'); buses=buses[buses.Area==AREA].copy().reset_index(drop=True)
busids=buses['Bus ID'].astype(int).tolist(); bi={b:i for i,b in enumerate(busids)}
branches=pd.read_csv(BASE/'branch.csv')
branches=branches[branches['From Bus'].isin(busids)&branches['To Bus'].isin(busids)].copy().reset_index(drop=True)
gens=pd.read_csv(BASE/'gen.csv'); gens=gens[gens['Bus ID'].isin(busids)].copy().reset_index(drop=True)
# Remove zero-P generators and RTPV from decision variables; RTPV is fixed negative load.
dec=gens[(gens['PMax MW']>0)&(gens.Category!='Solar RTPV')].copy().reset_index(drop=True)
thermal=(dec['PMin MW']>0)&(~dec.Category.isin(['Hydro','Solar PV','Wind']))
urows=np.where(thermal.to_numpy())[0]

# source-derived marginal cost
fp=pd.to_numeric(dec['Fuel Price $/MMBTU'],errors='coerce').fillna(0).to_numpy(float)
hr=pd.to_numeric(dec['HR_avg_0'],errors='coerce').fillna(0).to_numpy(float)
vom=pd.to_numeric(dec['VOM'],errors='coerce').fillna(0).to_numpy(float)
cost=fp*hr/1000+vom
# tiny deterministic tie breakers; renewable/hydro still preferred
cost=cost+1e-7*np.arange(len(dec))

load_ts=pd.read_csv(BASE/'timeseries_data_files/Load/DAY_AHEAD_regional_Load.csv')
pv_ts=pd.read_csv(BASE/'timeseries_data_files/PV/DAY_AHEAD_pv.csv')
wind_ts=pd.read_csv(BASE/'timeseries_data_files/WIND/DAY_AHEAD_wind.csv')
hydro_ts=pd.read_csv(BASE/'timeseries_data_files/Hydro/DAY_AHEAD_hydro.csv')
rtpv_ts=pd.read_csv(BASE/'timeseries_data_files/RTPV/DAY_AHEAD_rtpv.csv')

# nodal proportions within area
prop=(buses['MW Load']/buses['MW Load'].sum()).to_numpy(float)
# line coefficients
A=np.zeros((len(busids),len(branches)))
bl=np.zeros(len(branches)); rate=branches['Cont Rating'].to_numpy(float)
for l,r in branches.iterrows():
    A[bi[int(r['From Bus'])],l]=1; A[bi[int(r['To Bus'])],l]=-1
    tap=float(r['Tr Ratio']); tap=tap if tap>0 else 1.0
    bl[l]=100.0/(float(r.X)*tap)
Bbus=A@np.diag(bl)@A.T

slack=int(np.where(buses['Bus Type'].astype(str).str.lower()=='ref')[0][0])

def avail_at(row:int):
    pmax=dec['PMax MW'].to_numpy(float).copy(); pmin=dec['PMin MW'].to_numpy(float).copy()
    for j,g in dec.iterrows():
        uid=g['GEN UID']; cat=g.Category
        if cat=='Solar PV': pmax[j]=float(pv_ts.loc[row,uid]); pmin[j]=0
        elif cat=='Wind': pmax[j]=float(wind_ts.loc[row,uid]); pmin[j]=0
        elif cat=='Hydro':
            val=float(hydro_ts.loc[row,uid]); pmax[j]=val; pmin[j]=val
    return pmin,pmax

def rtpv_at(row:int):
    out=np.zeros(len(busids))
    for _,g in gens[gens.Category=='Solar RTPV'].iterrows():
        out[bi[int(g['Bus ID'])]] += float(rtpv_ts.loc[row,g['GEN UID']])
    return out

def solve_hour(row:int, network=True):
    ng=len(dec); nu=len(urows); nb=len(busids)
    ip=0; iu=ng; ith=ng+nu; ish=ng+nu+nb; nvar=ng+nu+nb+nb
    c=np.zeros(nvar); c[ip:ip+ng]=cost; c[ish:ish+nb]=10000.0
    lb=np.full(nvar,-np.inf); ub=np.full(nvar,np.inf)
    pmin,pmax=avail_at(row)
    lb[ip:ip+ng]=0; ub[ip:ip+ng]=pmax
    lb[iu:iu+nu]=0; ub[iu:iu+nu]=1
    lb[ith:ith+nb]=-np.pi; ub[ith:ith+nb]=np.pi
    load_total=float(load_ts.loc[row,str(AREA)]); load=prop*load_total
    rt=rtpv_at(row)
    lb[ish:ish+nb]=0; ub[ish:ish+nb]=load
    lb[ith+slack]=ub[ith+slack]=0
    integrality=np.zeros(nvar,int); integrality[iu:iu+nu]=1
    rows=[]; lo=[]; hi=[]
    # p/u linking
    for k,j in enumerate(urows):
        rr={ip+j:1,iu+k:-pmax[j]}; rows.append(rr); lo.append(-np.inf); hi.append(0)
        rr={ip+j:-1,iu+k:pmin[j]}; rows.append(rr); lo.append(-np.inf); hi.append(0)
    # nodal balance
    for b in range(nb):
        rr={}
        for j,g in dec.iterrows():
            if bi[int(g['Bus ID'])]==b: rr[ip+j]=rr.get(ip+j,0)+1
        rr[ish+b]=1
        if network:
            for k,val in enumerate(Bbus[b]):
                if abs(val)>0: rr[ith+k]=rr.get(ith+k,0)-float(val)
        rows.append(rr); rhs=float(load[b]-rt[b]); lo.append(rhs); hi.append(rhs)
    if not network:
        # replace individual balances by one system balance: remove last nb, add system
        rows=rows[:-nb]; lo=lo[:-nb]; hi=hi[:-nb]
        rr={ip+j:1 for j in range(ng)}
        for b in range(nb): rr[ish+b]=1
        rows.append(rr); rhs=float(load.sum()-rt.sum()); lo.append(rhs); hi.append(rhs)
    else:
        # line limits
        for l,r in branches.iterrows():
            rr={ith+bi[int(r['From Bus'])]:bl[l], ith+bi[int(r['To Bus'])]:-bl[l]}
            rows.append(rr); lo.append(-rate[l]); hi.append(rate[l])
    M=lil_matrix((len(rows),nvar),dtype=float)
    for i,rr in enumerate(rows):
        for j,v in rr.items(): M[i,j]=v
    res=milp(c,integrality=integrality,bounds=Bounds(lb,ub),constraints=LinearConstraint(csr_matrix(M),np.array(lo),np.array(hi)),options={'time_limit':60})
    if not res.success:
        raise RuntimeError((row,res.message))
    x=res.x
    p=x[ip:ip+ng]; shed=x[ish:ish+nb]
    theta=x[ith:ith+nb]
    flows=np.diag(bl)@A.T@theta if network else np.zeros(len(branches))
    return {'p':p,'u':x[iu:iu+nu],'theta':theta,'shed':shed,'flows':flows,'objective':res.fun,'load':load,'rtpv':rt,'pmin':pmin,'pmax':pmax}

if __name__=='__main__':
    for row in [0,8,12,24*181+12]:
        r=solve_hour(row)
        print(row, 'obj',r['objective'],'load',r['load'].sum(),'rtpv',r['rtpv'].sum(),'gen',r['p'].sum(),'shed',r['shed'].sum(),'maxflow',np.abs(r['flows']).max(),'n_on',r['u'].sum())
