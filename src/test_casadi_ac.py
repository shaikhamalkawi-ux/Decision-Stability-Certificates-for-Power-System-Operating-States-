import numpy as np, pandas as pd, casadi as ca
from pathlib import Path
BASE=Path('/mnt/data/v4full/DSC_Grid_V4_ConvexSupportPolyhedralCertificate/upstream/V3/raw/RTS-GMLC_v0.2.3')
PROC=Path('/mnt/data/v4full/DSC_Grid_V4_ConvexSupportPolyhedralCertificate/upstream/V3/processed')
AREA=1; SBASE=100.0
buses=pd.read_csv(BASE/'bus.csv'); buses=buses[buses.Area==AREA].copy().reset_index(drop=True)
busids=buses['Bus ID'].astype(int).tolist(); bi={b:i for i,b in enumerate(busids)}; nb=len(buses)
branches=pd.read_csv(BASE/'branch.csv'); branches=branches[branches['From Bus'].isin(busids)&branches['To Bus'].isin(busids)].copy().reset_index(drop=True); nl=len(branches)
gens=pd.read_csv(BASE/'gen.csv'); gens=gens[gens['Bus ID'].isin(busids)].copy().reset_index(drop=True); dec=gens[(gens['PMax MW']>0)&(gens.Category!='Solar RTPV')].copy().reset_index(drop=True); ng=len(dec)
load_ts=pd.read_csv(BASE/'timeseries_data_files/Load/DAY_AHEAD_regional_Load.csv'); pv_ts=pd.read_csv(BASE/'timeseries_data_files/PV/DAY_AHEAD_pv.csv'); wind_ts=pd.read_csv(BASE/'timeseries_data_files/WIND/DAY_AHEAD_wind.csv'); hydro_ts=pd.read_csv(BASE/'timeseries_data_files/Hydro/DAY_AHEAD_hydro.csv'); rtpv_ts=pd.read_csv(BASE/'timeseries_data_files/RTPV/DAY_AHEAD_rtpv.csv')
# Ybus
Y=np.zeros((nb,nb),complex)
for _,r in branches.iterrows():
    i=bi[int(r['From Bus'])]; k=bi[int(r['To Bus'])]
    y=1/complex(float(r.R),float(r.X)); jb=1j*float(r.B)/2
    tap=float(r['Tr Ratio']); tap=tap if tap>0 else 1.0
    Y[i,i]+=(y+jb)/(tap*tap); Y[k,k]+=y+jb; Y[i,k]+=-y/tap; Y[k,i]+=-y/tap
for i,b in buses.iterrows():
    Y[i,i]+=complex(float(b['MW Shunt G']), float(b['MVAR Shunt B']))/SBASE
G=Y.real; B=Y.imag
# branch admittances for flow
branch_params=[]
for _,r in branches.iterrows():
    i=bi[int(r['From Bus'])]; k=bi[int(r['To Bus'])]
    y=1/complex(float(r.R),float(r.X)); jb=1j*float(r.B)/2; tap=float(r['Tr Ratio']); tap=tap if tap>0 else 1.0
    Yff=(y+jb)/(tap*tap); Yft=-y/tap; Ytf=-y/tap; Ytt=y+jb
    branch_params.append((i,k,Yff,Yft,Ytf,Ytt,float(r['Cont Rating'])))
prop=(buses['MW Load']/buses['MW Load'].sum()).to_numpy(float)
def findrow(ts):
 ts=pd.Timestamp(ts); m=(load_ts.Year==ts.year)&(load_ts.Month==ts.month)&(load_ts.Day==ts.day)&(load_ts.Period==ts.hour+1); return int(np.flatnonzero(m.to_numpy())[0])
def state(row):
 load=prop*float(load_ts.loc[row,str(AREA)]); qload=buses['MVAR Load'].to_numpy(float)*(float(load_ts.loc[row,str(AREA)])/float(buses['MW Load'].sum()))
 rt=np.zeros(nb)
 for _,g in gens[gens.Category=='Solar RTPV'].iterrows(): rt[bi[int(g['Bus ID'])]]+=float(rtpv_ts.loc[row,g['GEN UID']])
 pmin=dec['PMin MW'].to_numpy(float).copy(); pmax=dec['PMax MW'].to_numpy(float).copy()
 for j,g in dec.iterrows():
  uid=g['GEN UID']; cat=g.Category
  if cat=='Solar PV': pmin[j]=0; pmax[j]=float(pv_ts.loc[row,uid])
  elif cat=='Wind': pmin[j]=0; pmax[j]=float(wind_ts.loc[row,uid])
  elif cat=='Hydro': pmin[j]=pmax[j]=float(hydro_ts.loc[row,uid])
 return load-rt,qload,pmin,pmax
# one hour
D=pd.read_csv(PROC/'month_03_first_week_dispatch.csv').iloc[0]
ts=D.timestamp; row=findrow(ts); pdem,qdem,pmin,pmax=state(row); target=D[dec['GEN UID'].tolist()].to_numpy(float)
thermal=(dec['PMin MW'].to_numpy(float)>0)&(~dec.Category.isin(['Hydro','Solar PV','Wind']).to_numpy())
on=np.ones(ng,bool)
for j in range(ng):
 if thermal[j] and target[j]<=1e-5: on[j]=False; pmin[j]=pmax[j]=0
qmin=dec['QMin MVAR'].to_numpy(float).copy(); qmax=dec['QMax MVAR'].to_numpy(float).copy(); qmin[~on]=0; qmax[~on]=0
# symbols
va=ca.MX.sym('va',nb); vm=ca.MX.sym('vm',nb); pg=ca.MX.sym('pg',ng); qg=ca.MX.sym('qg',ng); t=ca.MX.sym('t',ng)
x=ca.vertcat(va,vm,pg,qg,t)
# V rect expressions
vr=vm*ca.cos(va); vi=vm*ca.sin(va)
# injections using G,B
P=[]; Q=[]
for i in range(nb):
 pi=0; qi=0
 for k in range(nb):
  th=va[i]-va[k]
  pi += vm[i]*vm[k]*(G[i,k]*ca.cos(th)+B[i,k]*ca.sin(th))*SBASE
  qi += vm[i]*vm[k]*(G[i,k]*ca.sin(th)-B[i,k]*ca.cos(th))*SBASE
 P.append(pi); Q.append(qi)
# gen aggregation
gbus=np.array([bi[int(b)] for b in dec['Bus ID']])
Pgen=[]; Qgen=[]
for i in range(nb):
 js=np.where(gbus==i)[0]
 Pgen.append(sum([pg[j] for j in js], ca.MX(0)))
 Qgen.append(sum([qg[j] for j in js], ca.MX(0)))
g=[]; lbg=[]; ubg=[]
for i in range(nb):
 g.append(Pgen[i]-pdem[i]-P[i]); lbg.append(0); ubg.append(0)
 g.append(Qgen[i]-qdem[i]-Q[i]); lbg.append(0); ubg.append(0)
# abs
for j in range(ng):
 g += [pg[j]-target[j]-t[j], target[j]-pg[j]-t[j]]; lbg += [-ca.inf,-ca.inf]; ubg += [0,0]
# branch apparent constraints squared
for i,k,Yff,Yft,Ytf,Ytt,rate in branch_params:
 # derive currents real/imag from complex constants
 def cprod(Yc, ar,ai):
  return Yc.real*ar-Yc.imag*ai, Yc.real*ai+Yc.imag*ar
 iff_r1,iff_i1=cprod(Yff,vr[i],vi[i]); iff_r2,iff_i2=cprod(Yft,vr[k],vi[k]); ifr=iff_r1+iff_r2; ifi=iff_i1+iff_i2
 itf_r1,itf_i1=cprod(Ytf,vr[i],vi[i]); itf_r2,itf_i2=cprod(Ytt,vr[k],vi[k]); itr=itf_r1+itf_r2; iti=itf_i1+itf_i2
 # S = V * conj(I): P=vr*ir+vi*ii, Q=vi*ir-vr*ii
 pf=(vr[i]*ifr+vi[i]*ifi)*SBASE; qf=(vi[i]*ifr-vr[i]*ifi)*SBASE
 pt=(vr[k]*itr+vi[k]*iti)*SBASE; qt=(vi[k]*itr-vr[k]*iti)*SBASE
 g += [pf*pf+qf*qf, pt*pt+qt*qt]; lbg += [-ca.inf,-ca.inf]; ubg += [rate*rate,rate*rate]
# objective
obj=ca.sum1(t)+1e-6*ca.sumsqr(vm-buses['V Mag'].to_numpy(float))
nlp={'x':x,'f':obj,'g':ca.vertcat(*g)}
opts={'ipopt.print_level':3,'print_time':0,'ipopt.max_iter':1000,'ipopt.tol':1e-8,'ipopt.acceptable_tol':1e-6,'ipopt.linear_solver':'mumps'}
solv=ca.nlpsol('s','ipopt',nlp,opts)
# bounds
slack=int(np.where(buses['Bus Type'].astype(str).str.lower()=='ref')[0][0])
lbx=np.r_[np.full(nb,-np.pi),np.full(nb,0.95),pmin,qmin,np.zeros(ng)]
ubx=np.r_[np.full(nb,np.pi),np.full(nb,1.05),pmax,qmax,np.full(ng,np.inf)]
lbx[slack]=ubx[slack]=0
# initial x: source angles radians, source vm, clipped target, q source, abs 50/heads maybe
x0=np.r_[np.deg2rad(buses['V Angle'].to_numpy(float)-buses.loc[slack,'V Angle']),np.clip(buses['V Mag'].to_numpy(float),0.95,1.05),np.clip(target,pmin,pmax),np.clip(dec['MVAR Inj'].to_numpy(float),qmin,qmax),np.full(ng,2.0)]
print('load',pdem.sum(), 'targetgen',target.sum(), 'headroom', (pmax-target).clip(min=0).sum())
sol=solv(x0=x0,lbx=lbx,ubx=ubx,lbg=np.array(lbg,float),ubg=np.array(ubg,float))
st=solv.stats(); print(st['success'],st['return_status'],float(sol['f']))
xx=np.array(sol['x']).ravel(); Pg=xx[2*nb:2*nb+ng]; Vm=xx[nb:2*nb]; print('L1',np.abs(Pg-target).sum(),'v',Vm.min(),Vm.max(),'loss added',Pg.sum()-target.sum(),'gen',Pg.sum())
print('max delta',np.max(np.abs(Pg-target)))
# residual
print('max g viol?', np.max(np.maximum(np.array(lbg)-np.array(sol['g']).ravel(), np.array(sol['g']).ravel()-np.array(ubg))))
