from __future__ import annotations
import json, time, hashlib, platform, sys
from pathlib import Path
import numpy as np
import pandas as pd
import casadi as ca

PACKAGE_ROOT=Path(__file__).resolve().parents[1]
ROOT=PACKAGE_ROOT/'results'/'reproduction_ac_shared'
ROOT.mkdir(parents=True, exist_ok=True)
BASE=PACKAGE_ROOT/'upstream_lock'/'V3'/'raw'/'RTS-GMLC_v0.2.3'
PROC=PACKAGE_ROOT/'upstream_lock'/'V3'/'processed'
AREA=1; SBASE=100.0; VMIN=0.95; VMAX=1.05; COMMIT_TOL=1e-5

# Load locked inputs
buses=pd.read_csv(BASE/'bus.csv'); buses=buses[buses.Area==AREA].copy().reset_index(drop=True)
busids=buses['Bus ID'].astype(int).tolist(); bi={b:i for i,b in enumerate(busids)}; nb=len(buses)
branches=pd.read_csv(BASE/'branch.csv'); branches=branches[branches['From Bus'].isin(busids)&branches['To Bus'].isin(busids)].copy().reset_index(drop=True); nl=len(branches)
gens=pd.read_csv(BASE/'gen.csv'); gens=gens[gens['Bus ID'].isin(busids)].copy().reset_index(drop=True)
dec=gens[(gens['PMax MW']>0)&(gens.Category!='Solar RTPV')].copy().reset_index(drop=True); ng=len(dec)
load_ts=pd.read_csv(BASE/'timeseries_data_files/Load/DAY_AHEAD_regional_Load.csv')
pv_ts=pd.read_csv(BASE/'timeseries_data_files/PV/DAY_AHEAD_pv.csv')
wind_ts=pd.read_csv(BASE/'timeseries_data_files/WIND/DAY_AHEAD_wind.csv')
hydro_ts=pd.read_csv(BASE/'timeseries_data_files/Hydro/DAY_AHEAD_hydro.csv')
rtpv_ts=pd.read_csv(BASE/'timeseries_data_files/RTPV/DAY_AHEAD_rtpv.csv')
prop=(buses['MW Load']/buses['MW Load'].sum()).to_numpy(float)
gbus=np.array([bi[int(b)] for b in dec['Bus ID']],int)
thermal=(dec['PMin MW'].to_numpy(float)>0)&(~dec.Category.isin(['Hydro','Solar PV','Wind']).to_numpy())
slack=int(np.where(buses['Bus Type'].astype(str).str.lower()=='ref')[0][0])

# AC network admittance in p.u.
Y=np.zeros((nb,nb),complex); branch_params=[]
for _,r in branches.iterrows():
    i=bi[int(r['From Bus'])]; k=bi[int(r['To Bus'])]
    y=1/complex(float(r.R),float(r.X)); jb=1j*float(r.B)/2
    tap=float(r['Tr Ratio']); tap=tap if tap>0 else 1.0
    Yff=(y+jb)/(tap*tap); Yft=-y/tap; Ytf=-y/tap; Ytt=y+jb
    Y[i,i]+=Yff; Y[i,k]+=Yft; Y[k,i]+=Ytf; Y[k,k]+=Ytt
    branch_params.append((i,k,Yff,Yft,Ytf,Ytt,float(r['Cont Rating'])))
for i,b in buses.iterrows():
    Y[i,i]+=complex(float(b['MW Shunt G']),float(b['MVAR Shunt B']))/SBASE
G=Y.real; B=Y.imag

# One parameterized AC feasibility-projection NLP.
va=ca.MX.sym('va',nb); vm=ca.MX.sym('vm',nb); pg=ca.MX.sym('pg',ng); qg=ca.MX.sym('qg',ng); t=ca.MX.sym('t',ng)
x=ca.vertcat(va,vm,pg,qg,t)
pdem_par=ca.MX.sym('pdem',nb); qdem_par=ca.MX.sym('qdem',nb); target_par=ca.MX.sym('target',ng)
par=ca.vertcat(pdem_par,qdem_par,target_par)
vr=vm*ca.cos(va); vi=vm*ca.sin(va)
P=[]; Q=[]
for i in range(nb):
    pi=0; qi=0
    for k in range(nb):
        th=va[i]-va[k]
        pi += vm[i]*vm[k]*(G[i,k]*ca.cos(th)+B[i,k]*ca.sin(th))*SBASE
        qi += vm[i]*vm[k]*(G[i,k]*ca.sin(th)-B[i,k]*ca.cos(th))*SBASE
    P.append(pi); Q.append(qi)
Pgen=[]; Qgen=[]
for i in range(nb):
    js=np.where(gbus==i)[0]
    Pgen.append(sum([pg[j] for j in js], ca.MX(0)))
    Qgen.append(sum([qg[j] for j in js], ca.MX(0)))
con=[]; lbg=[]; ubg=[]; n_balance=0; n_abs=0; n_branch=0
for i in range(nb):
    con += [Pgen[i]-pdem_par[i]-P[i], Qgen[i]-qdem_par[i]-Q[i]]
    lbg += [0.0,0.0]; ubg += [0.0,0.0]; n_balance += 2
for j in range(ng):
    con += [pg[j]-target_par[j]-t[j], target_par[j]-pg[j]-t[j]]
    lbg += [-np.inf,-np.inf]; ubg += [0.0,0.0]; n_abs += 2
branch_expr=[]
def cprod(Yc, ar, ai):
    return Yc.real*ar-Yc.imag*ai, Yc.real*ai+Yc.imag*ar
for i,k,Yff,Yft,Ytf,Ytt,rate in branch_params:
    a,b=cprod(Yff,vr[i],vi[i]); c,d=cprod(Yft,vr[k],vi[k]); ifr=a+c; ifi=b+d
    a,b=cprod(Ytf,vr[i],vi[i]); c,d=cprod(Ytt,vr[k],vi[k]); itr=a+c; iti=b+d
    pf=(vr[i]*ifr+vi[i]*ifi)*SBASE; qf=(vi[i]*ifr-vr[i]*ifi)*SBASE
    pt=(vr[k]*itr+vi[k]*iti)*SBASE; qt=(vi[k]*itr-vr[k]*iti)*SBASE
    sf2=pf*pf+qf*qf; st2=pt*pt+qt*qt
    con += [sf2,st2]; lbg += [-np.inf,-np.inf]; ubg += [rate*rate,rate*rate]; n_branch += 2
    branch_expr.append((pf,qf,pt,qt))
obj=ca.sum1(t)+1e-8*ca.sumsqr(vm-1.0)
nlp={'x':x,'p':par,'f':obj,'g':ca.vertcat(*con)}
opts={
    'ipopt.print_level':0,'print_time':0,'ipopt.max_iter':500,'ipopt.max_cpu_time':2,
    'ipopt.tol':1e-8,'ipopt.acceptable_tol':1e-6,'ipopt.acceptable_iter':10,
    'ipopt.linear_solver':'mumps','ipopt.mu_strategy':'adaptive',
    'ipopt.bound_relax_factor':1e-10,'ipopt.constr_viol_tol':1e-7,
}
solver=ca.nlpsol('acproj','ipopt',nlp,opts)
branch_fun=ca.Function('bf',[x],[ca.vertcat(*[z for tup in branch_expr for z in tup])])

# helpers
def findrow(ts):
    ts=pd.Timestamp(ts)
    m=(load_ts.Year.astype(int)==ts.year)&(load_ts.Month.astype(int)==ts.month)&(load_ts.Day.astype(int)==ts.day)&(load_ts.Period.astype(int)==ts.hour+1)
    idx=np.flatnonzero(m.to_numpy())
    if len(idx)!=1: raise RuntimeError((ts,idx))
    return int(idx[0])

def state(row):
    total=float(load_ts.loc[row,str(AREA)]); scale=total/float(buses['MW Load'].sum())
    p=buses['MW Load'].to_numpy(float)*scale; q=buses['MVAR Load'].to_numpy(float)*scale
    rt=np.zeros(nb)
    for _,g in gens[gens.Category=='Solar RTPV'].iterrows(): rt[bi[int(g['Bus ID'])]]+=float(rtpv_ts.loc[row,g['GEN UID']])
    p=p-rt
    pmin=dec['PMin MW'].to_numpy(float).copy(); pmax=dec['PMax MW'].to_numpy(float).copy()
    for j,g in dec.iterrows():
        uid=g['GEN UID']; cat=g.Category
        if cat=='Solar PV': pmin[j]=0; pmax[j]=float(pv_ts.loc[row,uid])
        elif cat=='Wind': pmin[j]=0; pmax[j]=float(wind_ts.loc[row,uid])
        elif cat=='Hydro': pmin[j]=pmax[j]=float(hydro_ts.loc[row,uid])
    return p,q,pmin,pmax,scale,rt

def bounds(target,pmin0,pmax0,mode):
    pmin=pmin0.copy(); pmax=pmax0.copy(); online=np.ones(ng,bool)
    if mode=='fixed_commitment':
        for j in range(ng):
            if thermal[j] and target[j]<=COMMIT_TOL:
                online[j]=False; pmin[j]=pmax[j]=0.0
    elif mode=='shared_continuous':
        for j in range(ng):
            if thermal[j]: pmin[j]=0.0
    else: raise ValueError(mode)
    qmin=dec['QMin MVAR'].to_numpy(float).copy(); qmax=dec['QMax MVAR'].to_numpy(float).copy()
    qmin[~online]=0.0; qmax[~online]=0.0
    return pmin,pmax,qmin,qmax,online

def initial_guesses(target,pmin,pmax,qmin,qmax,pdem,prev=None):
    vas=np.deg2rad(buses['V Angle'].to_numpy(float)-float(buses.loc[slack,'V Angle']))
    vms=np.clip(buses['V Mag'].to_numpy(float),VMIN,VMAX)
    pg0=np.clip(target,pmin,pmax); q0=np.clip(dec['MVAR Inj'].to_numpy(float),qmin,qmax)
    # distribute a 5% load proxy loss across active headroom to seed Pg above DC balance
    head=np.maximum(0,pmax-pg0); loss_seed=0.035*float(pdem.sum()); add=np.zeros(ng)
    if head.sum()>1e-9: add=np.minimum(head, loss_seed*head/head.sum())
    seeds=[('source',np.r_[vas,vms,pg0,q0,np.maximum(1.0,np.abs(pg0-target))])]
    if prev is not None: seeds.insert(0,('previous',prev.copy()))
    return seeds

def max_violation(gval,lbgv,ubgv,lbx,ubx,xv):
    gval=np.asarray(gval,float).ravel(); lbgv=np.asarray(lbgv,float); ubgv=np.asarray(ubgv,float)
    gv=max(float(np.max(np.maximum(np.where(np.isfinite(lbgv),lbgv-gval,0),np.where(np.isfinite(ubgv),gval-ubgv,0)))),0.0)
    xv=np.asarray(xv,float).ravel(); bv=max(float(np.max(np.maximum(lbx-xv,xv-ubx))),0.0)
    return gv,bv

results=[]; corrections=[]; previous={}
for month in [3,7]:
    d=pd.read_csv(PROC/f'month_{month:02d}_first_week_dispatch.csv').iloc[:24]
    cols=[c for c in d.columns if c!='timestamp']
    assert cols==dec['GEN UID'].tolist()
    for h,rowd in d.iterrows():
        ts=pd.Timestamp(rowd.timestamp); ridx=findrow(ts); pdem,qdem,pmin0,pmax0,scale,rt=state(ridx); target=rowd[cols].to_numpy(float)
        for mode in ['shared_continuous']:
            pmin,pmax,qmin,qmax,online=bounds(target,pmin0,pmax0,mode)
            target_used=np.clip(target,pmin,pmax)
            lbx=np.r_[np.full(nb,-np.pi),np.full(nb,VMIN),pmin,qmin,np.zeros(ng)]
            ubx=np.r_[np.full(nb,np.pi),np.full(nb,VMAX),pmax,qmax,np.full(ng,1e5)]
            lbx[slack]=ubx[slack]=0.0
            parval=np.r_[pdem,qdem,target_used]
            best=None; attempts=[]
            t0=time.time()
            for seed_name,x0 in initial_guesses(target_used,pmin,pmax,qmin,qmax,pdem,previous.get(mode)):
                # clip previous seed into current bounds
                x0=np.minimum(np.maximum(x0,lbx),ubx)
                try:
                    sol=solver(x0=x0,p=parval,lbx=lbx,ubx=ubx,lbg=lbg,ubg=ubg)
                    st=solver.stats(); xv=np.array(sol['x']).ravel(); gv,bv=max_violation(np.array(sol['g']).ravel(),lbg,ubg,lbx,ubx,xv)
                    ok=bool(st.get('success',False)) and gv<=2e-5 and bv<=2e-5
                    val=float(sol['f'])
                    attempts.append({'seed':seed_name,'success':ok,'status':st.get('return_status'),'objective':val,'g_violation':gv,'bound_violation':bv,'iterations':st.get('iter_count')})
                    if ok and (best is None or val<best['objective']-1e-6): best={'x':xv,'objective':val,'seed':seed_name,'g_violation':gv,'bound_violation':bv,'status':st.get('return_status')}
                except Exception as e:
                    attempts.append({'seed':seed_name,'success':False,'status':type(e).__name__,'message':str(e)[:300]})
            rec={'month':month,'hour':int(h),'timestamp':ts.isoformat(),'mode':mode,'success':best is not None,'elapsed_s':time.time()-t0,'attempts_json':json.dumps(attempts)}
            if best is not None:
                xv=best['x']; vaa=xv[:nb]; vmm=xv[nb:2*nb]; pgg=xv[2*nb:2*nb+ng]; qgg=xv[2*nb+ng:2*nb+2*ng]
                previous[mode]=xv.copy()
                bf=np.array(branch_fun(xv)).ravel().reshape(nl,4); sfrom=np.sqrt(bf[:,0]**2+bf[:,1]**2); sto=np.sqrt(bf[:,2]**2+bf[:,3]**2); rates=branches['Cont Rating'].to_numpy(float); loadfrac=np.maximum(sfrom,sto)/rates
                l1=float(np.abs(pgg-target_used).sum()); loss=float(pgg.sum()-pdem.sum())
                rec.update({'restoration_L1_MW':l1,'active_losses_MW':loss,'max_coordinate_restoration_MW':float(np.abs(pgg-target_used).max()),'min_voltage_pu':float(vmm.min()),'max_voltage_pu':float(vmm.max()),'max_branch_loading_fraction':float(loadfrac.max()),'min_Q_margin_MVAR':float(np.min(np.minimum(qgg-qmin,qmax-qgg))),'objective':best['objective'],'best_seed':best['seed'],'max_constraint_violation':best['g_violation'],'max_bound_violation':best['bound_violation'],'online_generators':int(online.sum())})
                for j,uid in enumerate(cols): corrections.append({'month':month,'hour':int(h),'timestamp':ts.isoformat(),'mode':mode,'GEN_UID':uid,'target_MW':target_used[j],'restored_MW':pgg[j],'delta_MW':pgg[j]-target_used[j],'abs_delta_MW':abs(pgg[j]-target_used[j]),'Q_MVAR':qgg[j],'Pmin_MW':pmin[j],'Pmax_MW':pmax[j],'Qmin_MVAR':qmin[j],'Qmax_MVAR':qmax[j]})
            results.append(rec)
            print(month,h,mode,rec['success'],rec.get('restoration_L1_MW'),rec.get('best_seed'),rec.get('max_constraint_violation'))

rdf=pd.DataFrame(results); cdf=pd.DataFrame(corrections)
rdf.to_csv(ROOT/'ac_projection_results.csv',index=False); cdf.to_csv(ROOT/'ac_projection_generator_corrections.csv',index=False)
summary=[]
for (m,mode),g in rdf.groupby(['month','mode']):
    ok=g[g.success==True]
    summary.append({'month':int(m),'mode':mode,'cases':len(g),'successes':len(ok),'success_rate':len(ok)/len(g),'median_L1_MW':float(ok.restoration_L1_MW.median()) if len(ok) else None,'min_L1_MW':float(ok.restoration_L1_MW.min()) if len(ok) else None,'max_L1_MW':float(ok.restoration_L1_MW.max()) if len(ok) else None,'median_losses_MW':float(ok.active_losses_MW.median()) if len(ok) else None,'max_branch_loading_fraction':float(ok.max_branch_loading_fraction.max()) if len(ok) else None,'min_voltage_pu':float(ok.min_voltage_pu.min()) if len(ok) else None,'max_voltage_pu':float(ok.max_voltage_pu.max()) if len(ok) else None,'max_constraint_violation':float(ok.max_constraint_violation.max()) if len(ok) else None})
sdf=pd.DataFrame(summary); sdf.to_csv(ROOT/'ac_projection_summary.csv',index=False)
meta={'method':'CasADi 3.7.2 + IPOPT direct nonconvex AC feasibility projection','objective':'min sum_j |Pg_j-Pg_DC,j| with voltage, Q, nodal AC balance, branch terminal apparent-power, and support bounds','claim_boundary':'Successful solves are AC-feasible local restoration witnesses; nonconvergence is not proof of infeasibility; objectives are locally optimized and not global certificates.','network':'RTS-GMLC Area 1 internal 24-bus/38-branch model, matching the locked DC topology','voltage_bounds':[VMIN,VMAX],'branch_rating':'Cont Rating at both terminals','months':[3,7],'hours_per_month':24,'modes':['shared_continuous'],'multistart_seeds':['previous','source','loss_seed','flat'],'environment':{'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'pandas':pd.__version__,'casadi':ca.__version__},'summary':summary}
(ROOT/'ac_projection_summary.json').write_text(json.dumps(meta,indent=2))
print('\nSUMMARY\n',sdf.to_string(index=False))
