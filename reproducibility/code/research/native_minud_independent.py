from pathlib import Path
import sys,time,json
import numpy as np,pandas as pd
from scipy.optimize import milp, Bounds, LinearConstraint
from scipy.sparse import lil_matrix,csr_matrix
ROOT=Path(__file__).resolve().parents[1]; V3=ROOT/'upstream_lock'/'V3'; sys.path.insert(0,str(V3/'code')); import dscgrid_model as m
cols=m.dec['GEN UID'].tolist();NG=len(cols);tidx=np.flatnonzero(m.thermal.to_numpy(bool));K=len(tidx);PMIN=m.dec['PMin MW'].to_numpy(float);UT=np.ceil(m.dec.loc[tidx,'Min Up Time Hr'].astype(float)).astype(int).to_numpy();DT=np.ceil(m.dec.loc[tidx,'Min Down Time Hr'].astype(float)).astype(int).to_numpy()
def data(mo):
 T=pd.read_csv(V3/'processed'/f'month_{mo:02d}_first_week_dispatch.csv')[cols].to_numpy(float);rr=pd.read_csv(V3/'processed'/f'month_{mo:02d}_first_week_hourly_summary.csv')['row'].astype(int).to_numpy();pmins=[];pmaxs=[];net=[]
 for r in rr:
  pmin,pmax=m.avail_at(int(r));pmins.append(pmin);pmaxs.append(pmax);net.append(float(m.load_ts.loc[int(r),str(m.AREA)])-m.rtpv_at(int(r)).sum())
 return T,np.asarray(pmins),np.asarray(pmaxs),np.asarray(net)
def solve(mo,tl=60):
 T,pmins,pmaxs,net=data(mo);H=len(T);mu=T.mean(0);npv=H*NG;nu=H*K;ny=H*K;nz=H*K;iu=npv;iy=iu+nu;iz=iy+ny;n=iz+nz
 P=lambda t,j:t*NG+j;U=lambda t,k:iu+t*K+k;Y=lambda t,k:iy+t*K+k;Z=lambda t,k:iz+t*K+k
 c=np.zeros(n);lb=np.zeros(n);ub=np.r_[pmaxs.ravel(),np.ones(nu+ny+nz)];integ=np.zeros(n,np.uint8);integ[iu:]=1
 R=[];LO=[];HI=[]
 def add(d,lo=-np.inf,hi=np.inf):R.append(d);LO.append(lo);HI.append(hi)
 for t in range(H):
  for j in range(NG):
   if str(m.dec.iloc[j]['Category'])=='Hydro': lb[P(t,j)]=pmins[t,j];ub[P(t,j)]=pmaxs[t,j]
  for k,j in enumerate(tidx):
   mn=float(PMIN[j]);mx=float(pmaxs[t,j]);add({P(t,j):1,U(t,k):-mx},hi=0);add({P(t,j):-1,U(t,k):mn},hi=0)
   if t==0:
    # free pre-horizon state: do not define a startup/shutdown at t0; fix y0=z0=0
    lb[Y(t,k)]=ub[Y(t,k)]=0;lb[Z(t,k)]=ub[Z(t,k)]=0
   else:
    # u_t-u_{t-1}=y_t-z_t
    add({U(t,k):1,U(t-1,k):-1,Y(t,k):-1,Z(t,k):1},lo=0,hi=0)
    # cannot start and stop simultaneously
    add({Y(t,k):1,Z(t,k):1},hi=1)
   # weak/free-boundary minimum up/down: only observed starts/stops constrain observed hours
   su=max(1,t-int(UT[k])+1)
   if t>=1: add({**{Y(tau,k):1 for tau in range(su,t+1)},U(t,k):-1},hi=0)
   sd=max(1,t-int(DT[k])+1)
   if t>=1:
    d={Z(tau,k):1 for tau in range(sd,t+1)};d[U(t,k)]=1;add(d,hi=1)
  add({P(t,j):1 for j in range(NG)},lo=float(net[t]),hi=float(net[t]))
 for j in range(NG):add({P(t,j):1/H for t in range(H)},lo=float(mu[j]),hi=float(mu[j]))
 M=lil_matrix((len(R),n));
 for r,d in enumerate(R):
  for q,v in d.items():M[r,q]=v
 st=time.time();res=milp(c,integrality=integ,bounds=Bounds(lb,ub),constraints=LinearConstraint(csr_matrix(M),np.array(LO),np.array(HI)),options={'time_limit':tl,'mip_rel_gap':1e-8,'presolve':True})
 return {'month':mo,'success':bool(res.success),'status':int(res.status),'message':res.message,'time_s':time.time()-st,'mip_gap':getattr(res,'mip_gap',None),'formulation':'independent_yz_weak_free_boundary_no_network'}
outs=[]
for mo in [3,7]:
 z=solve(mo,60);print(json.dumps(z,default=str),flush=True);outs.append(z)
OUT=ROOT/'results'/'reproduction'; OUT.mkdir(parents=True,exist_ok=True); pd.DataFrame(outs).to_csv(OUT/'native_minud_independent.csv',index=False)
