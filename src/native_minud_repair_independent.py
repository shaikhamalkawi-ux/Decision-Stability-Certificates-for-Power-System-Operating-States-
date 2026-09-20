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
def solve(mo,tl=120):
 T,pmins,pmaxs,net=data(mo);H=len(T);mu=T.mean(0);npv=H*NG;nu=H*K;ny=H*K;nz=H*K;iu=npv;iy=iu+nu;iz=iy+ny;idp=iz+nz;idm=idp+NG;n=idm+NG
 P=lambda t,j:t*NG+j;U=lambda t,k:iu+t*K+k;Y=lambda t,k:iy+t*K+k;Z=lambda t,k:iz+t*K+k;DP=lambda j:idp+j;DM=lambda j:idm+j
 c=np.zeros(n);c[idp:idp+NG]=1;c[idm:idm+NG]=1
 lb=np.zeros(n);ub=np.r_[pmaxs.ravel(),np.ones(nu+ny+nz),np.full(2*NG,np.inf)];integ=np.zeros(n,np.uint8);integ[iu:idp]=1
 R=[];LO=[];HI=[]
 def add(d,lo=-np.inf,hi=np.inf):R.append(d);LO.append(lo);HI.append(hi)
 for t in range(H):
  for j in range(NG):
   if str(m.dec.iloc[j]['Category'])=='Hydro': lb[P(t,j)]=pmins[t,j];ub[P(t,j)]=pmaxs[t,j]
  for k,j in enumerate(tidx):
   mn=float(PMIN[j]);mx=float(pmaxs[t,j]);add({P(t,j):1,U(t,k):-mx},hi=0);add({P(t,j):-1,U(t,k):mn},hi=0)
   if t==0:
    lb[Y(t,k)]=ub[Y(t,k)]=0;lb[Z(t,k)]=ub[Z(t,k)]=0
   else:
    add({U(t,k):1,U(t-1,k):-1,Y(t,k):-1,Z(t,k):1},lo=0,hi=0);add({Y(t,k):1,Z(t,k):1},hi=1)
   if t>=1:
    su=max(1,t-int(UT[k])+1);d={Y(tau,k):1 for tau in range(su,t+1)};d[U(t,k)]=-1;add(d,hi=0)
    sd=max(1,t-int(DT[k])+1);d={Z(tau,k):1 for tau in range(sd,t+1)};d[U(t,k)]=1;add(d,hi=1)
  add({P(t,j):1 for j in range(NG)},lo=float(net[t]),hi=float(net[t]))
 for j in range(NG):
  d={P(t,j):1/H for t in range(H)};d[DP(j)]=-1;d[DM(j)]=1;add(d,lo=float(mu[j]),hi=float(mu[j]))
 M=lil_matrix((len(R),n))
 for r,d in enumerate(R):
  for q,v in d.items():M[r,q]=v
 st=time.time();res=milp(c,integrality=integ,bounds=Bounds(lb,ub),constraints=LinearConstraint(csr_matrix(M),np.array(LO),np.array(HI)),options={'time_limit':tl,'mip_rel_gap':1e-7,'presolve':True})
 out={'month':mo,'success':bool(res.success),'status':int(res.status),'message':res.message,'time_s':time.time()-st,'repair_L1_MW':None if res.fun is None else float(res.fun),'mip_gap':getattr(res,'mip_gap',None),'dual_bound':getattr(res,'mip_dual_bound',None),'formulation':'minud_yz_weak_free_boundary_no_network_relaxation'}
 if res.x is not None:
  p=res.x[:npv].reshape(H,NG);newmu=p.mean(0);diff=newmu-mu
  out['max_coordinate_change_MW']=float(np.max(np.abs(diff)));out['sum_delta_residual_MW']=float(abs(diff.sum()))
  OUT=ROOT/'results'/'reproduction'; OUT.mkdir(parents=True,exist_ok=True); pd.DataFrame({'generator':cols,'target_mean_MW':mu,'repaired_mean_MW':newmu,'delta_MW':diff,'abs_delta_MW':np.abs(diff)}).sort_values('abs_delta_MW',ascending=False).to_csv(OUT/f'native_minud_repair_month_{mo:02d}.csv',index=False)
 return out
outs=[]
for mo in [3,7]:
 z=solve(mo,120);print(json.dumps(z,default=str),flush=True);outs.append(z)
OUT=ROOT/'results'/'reproduction'; OUT.mkdir(parents=True,exist_ok=True); pd.DataFrame(outs).to_csv(OUT/'native_minud_repair_summary.csv',index=False)
