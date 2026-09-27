"""Independent stdlib post-run seasonal-energy audit; no optimizer or producer imports."""
import csv,hashlib,importlib.util,json,math,struct,sys,time
from datetime import datetime
from fractions import Fraction as Q
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'results/research8h/seasonal_all_four_energy'
for rel,sha in [('src/research8h_standalone_verify.py','708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'),('results/research8h/hour_of_day_uncapped_prepared_review.py','ec6c5c129dfb71c9cd7f04643dcf8b81ce806f73652edc8da44080f63daf067f'),('results/research8h/seasonal_cap_prepared_review.py','3de77675460d103298ac17dc7851144362a3ecb87a1e77ec80f522622259433a')]:
    assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==sha
sp=importlib.util.spec_from_file_location('seasonal_energy_independent_helpers',ROOT/'results/research8h/hour_of_day_uncapped_prepared_review.py');h=importlib.util.module_from_spec(sp);sys.modules[sp.name]=h;sp.loader.exec_module(h)
a=h.a;v=h.v;jq=h.jq;TAU=Q.from_float(1e-5)
CASES=('seed_26093400','seed_26093401','seed_26094000','seed_26094001');IDENTITIES=('month_04_identity','month_10_identity')
MANIFEST='7a5a4cde36105325bcf5fd70e19a06d2997ce39240678ddbb82186f9ead4b078'
def decimals(x):
    if isinstance(x,dict):
        if {'numerator','denominator','outward_floor_6dp','outward_ceiling_6dp'}<=x.keys():
            assert Q(str(x['outward_floor_6dp']))<=jq(x)<=Q(str(x['outward_ceiling_6dp']))
        for item in x.values():decimals(item)
    elif isinstance(x,list):
        for item in x:decimals(item)

def dual_check(d,m,c,lp):
    zero=h.objective_lower(m,c,(0.,)*m.rows);saved=a.js(d/'zero_dual_baseline.json')
    assert all(jq(zero[k])==jq(saved[k]) for k in zero)
    lower=jq(zero['expanded_lower_bound_MWh']);out=dict(zero_dual_lower_MWh=v.rat(lower))
    if lp.get('new_lower_bound_status')=='EXACT_EXPANDED_OBJECTIVE_LOWER_BOUND':
        raw=v.read_npz(d/'lp/raw_duals.npz',('row_dual','column_dual'))['row_dual'].values
        projected=a.array(d/'lp/projected_row_dual.npz','row_dual')
        assert len(raw)==len(projected)==m.rows and all(math.isfinite(x) for x in raw)
        expected=tuple(0. if (x>0 and not math.isfinite(m.row_lower[r])) or (x<0 and not math.isfinite(m.row_upper[r])) else x for r,x in enumerate(raw))
        assert expected==projected
        bound=h.objective_lower(m,c,projected);stored=a.js(d/'lp/exact_lower_bound.json')
        assert all(jq(bound[k])==jq(stored[k]) for k in bound)
        removed=sum(x!=y for x,y in zip(raw,projected));assert removed==stored['projected_entries']
        residual=[Q(x) for x in c]
        for r,x in enumerate(projected):
            if x:
                dx=Q(x)
                for e in range(m.indptr[r],m.indptr[r+1]):residual[m.indices[e]]-=dx*Q(m.data[e])
        archived=a.js(d/'lp/exact_stationarity_residual.json')
        assert [(int(x['column']),jq(x)) for x in archived]==[(j,q) for j,q in enumerate(residual) if q]
        assert jq(lp['expanded_lower_MWh'])==jq(bound['expanded_lower_bound_MWh']) and jq(lp['nominal_lower_MWh'])==jq(bound['nominal_lower_bound_MWh'])
        lower=max(lower,jq(bound['expanded_lower_bound_MWh']))
        out.update(bound=bound,projected_entries=removed,exact_sparse_stationarity_residual_pass=True)
    out['selected_lower_MWh']=v.rat(lower)
    return lower,out

def csvrows(p):
    with p.open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))

def native_direct(d,m,point,names):
    meta=a.js(d/'model_metadata.json');identity=d.name.endswith('_identity')
    keys=('pmin','pmax','net','rows','nodal');native=v.read_npz(d/'native_inputs.npz',keys if identity else (*keys,'source_hour'))
    generators=[NATIVE['gens'][name] for name in meta['unit_names']];buses=meta['bus_ids'];bi={bid:j for j,bid in enumerate(buses)}
    assert buses==NATIVE['buses'] and len(generators)==41
    ti=[j for j,g in enumerate(generators) if float(g['PMin MW'])>0 and g['Category'] not in ('Hydro','Solar PV','Wind')]
    assert [meta['unit_names'][j] for j in ti]==meta['thermal_unit_names'] and len(ti)==24
    fossil=[j for j,g in enumerate(generators) if g['Fuel'] in ('Coal','Oil','NG')];assert len(fossil)==23
    P=[list(map(Q,point[t*41:(t+1)*41])) for t in range(168)]
    U=[list(point[6888+t*24:6888+(t+1)*24]) for t in range(168)]
    Y=[list(point[10920+t*24:10920+(t+1)*24]) for t in range(168)];Z=[list(point[14952+t*24:14952+(t+1)*24]) for t in range(168)]
    theta=[list(map(Q,point[18984+t*24:18984+(t+1)*24])) for t in range(168)]
    assert all(x in (0.,1.) for block in (U,Y,Z) for row in block for x in row)
    maxima={};first=[]
    def audit(family,excess,t,j):
        excess=max(Q(0),excess);maxima[family]=max(maxima.get(family,Q(0)),excess)
        if excess>TAU and len(first)<16:first.append({'family':family,'hour':t,'index':j,'violation':v.rat(excess)})
    lo=native['pmin'].values;hi=native['pmax'].values;net=native['net'].values;nodal=native['nodal'].values
    for t in range(168):
        for j,g in enumerate(generators):
            p=P[t][j];audit('negative_dispatch',-p,t,j);audit('availability',p-Q(hi[t*41+j]),t,j)
            if g['Category']=='Hydro':audit('hydro_fixed',abs(p-Q(lo[t*41+j])),t,j)
        audit('aggregate_balance',abs(sum(P[t],Q(0))-Q(net[t])),t,-1)
        for k,j in enumerate(ti):
            audit('commitment_upper',P[t][j]-Q(hi[t*41+j])*Q(U[t][k]),t,j)
            audit('commitment_lower',Q(lo[t*41+j])*Q(U[t][k])-P[t][j],t,j)
            delta=0 if t==0 else U[t][k]-U[t-1][k]
            assert Y[t][k]==max(0,delta) and Z[t][k]==max(0,-delta)
            if t and delta:
                duration=math.ceil(float(generators[j]['Min Up Time Hr' if delta>0 else 'Min Down Time Hr']))
                assert all(U[z][k]==U[t][k] for z in range(t,min(168,t+duration)))
            if t and U[t][k] and U[t-1][k]:
                rate=Q(float(generators[j]['Ramp Rate MW/Min'])*60.)
                audit('native_on_on_ramp',abs(P[t][j]-P[t-1][j])-rate,t,j)
        for j,x in enumerate(theta[t]):audit('angle_bound',abs(x)-Q(math.pi),t,j)
        audit('reference_angle',abs(theta[t][NATIVE['slack']]),t,NATIVE['slack'])
        for l,edge in enumerate(NATIVE['branches']):
            left,right=bi[int(edge['From Bus'])],bi[int(edge['To Bus'])]
            tap=float(edge['Tr Ratio']);tap=tap if tap>0 else 1.
            coefficient=Q(100./(float(edge['X'])*tap));flow=coefficient*(theta[t][left]-theta[t][right])
            audit('branch_limit',abs(flow)-Q(float(edge['Cont Rating'])),t,l)
    nodal_count=0
    for r,label in enumerate(names):
        if label['family']!='nodal_balance':continue
        t=int(label['hour_0based']);bid=int(float(label['uid']));bus=bi[bid];terms=a.row(m,r)
        expected_p={t*41+j:1. for j,g in enumerate(generators) if int(g['Bus ID'])==bid}
        assert {j:x for j,x in terms.items() if j<6888}==expected_p
        assert all(j<6888 or 18984+t*24<=j<18984+(t+1)*24 for j in terms)
        assert m.row_lower[r]==m.row_upper[r]==nodal[t*24+bus]
        generation=sum((P[t][j] for j,g in enumerate(generators) if int(g['Bus ID'])==bid),Q(0))
        injection=generation-Q(nodal[t*24+bus]);flowterm=sum((Q(coef)*theta[t][j-(18984+t*24)] for j,coef in terms.items() if j>=18984),Q(0))
        audit('provided_nodal_balance',abs(injection+flowterm),t,bus);nodal_count+=1
    assert nodal_count==168*24
    energy=sum((P[t][j] for t in range(168) for j in fossil),Q(0))
    return {'pass':all(x<=TAU for x in maxima.values()),'maximum_residuals':{k:v.rat(x) for k,x in maxima.items()},'first_violations':first,'energy_MWh':v.rat(energy),'original_binary_coordinates':12096,'canonical_transitions_and_clipped_residence':True,'native_nodal_rows':nodal_count,'energy_cap_constraints':0,'native_rounded_Bbus_coefficients_from_frozen_model':True}

def binary_upper(d,m,c,names,original,mip):
    if mip['verdict']!='VERIFIED_UNCAPPED_BINARY_WITNESS_EXPANDED_MODEL':
        assert mip['verdict']=='UNKNOWN' and 'verified_upper_MWh' not in mip
        diagnostics={}
        if (d/'mip/recovered_vector.npz').exists():
            point=a.array(d/'mip/recovered_vector.npz','vector');diagnostics['unaccepted_candidate_point_check']=a.point_audit(m,point,original,names)
            diagnostics['unaccepted_candidate_native_check']=native_direct(d,m,point,names)
            assert mip.get('candidate_not_accepted_as_upper_bound',False)
        return None,dict(finite_binary_upper_verified=False,verdict=mip['verdict'],diagnostics=diagnostics)
    raw=a.array(d/'mip/raw_vector.npz','vector');point=a.array(d/'mip/recovered_vector.npz','vector')
    assert len(raw)==len(point)==m.cols==23016
    for lo,hi in ((0,6888),(18984,23016)):
        assert struct.pack('<'+str(hi-lo)+'d',*raw[lo:hi])==struct.pack('<'+str(hi-lo)+'d',*point[lo:hi])
    u=point[6888:10920];assert all(x in (0,1) for x in u)
    assert all(abs(Q(raw[6888+j])-Q(x))<=TAU for j,x in enumerate(u))
    for t in range(168):
        for j in range(24):
            change=0 if t==0 else u[t*24+j]-u[(t-1)*24+j]
            assert point[10920+t*24+j]==max(0,change) and point[14952+t*24+j]==max(0,-change)
    exact=a.point_audit(m,point,original,names);saved=a.js(d/'mip/exact_point_check.json')
    assert exact['full_expanded_pass'] and exact['full_strict_pass']==saved['strict_pass']==mip['exact_strict_pass']
    for key in ('maximum_column_violation','maximum_row_violation'):assert jq(exact[key])==jq(saved[key])
    assert mip['raw_matrix_check']['pass'] and mip['recovered_matrix_check']['pass'] and mip['native_no_cap_pass'] and a.js(d/'mip/native_no_cap_check.json')['pass']
    raw_check=a.point_audit(m,raw,(0,)*m.cols,names) # Diagnostic only: acceptance is based on the recovered exact full-binary point.
    upper=sum((Q(x)*Q(y) for x,y in zip(c,point)),Q(0));assert upper==jq(mip['verified_upper_MWh'])==jq(mip['candidate_fossil_MWh'])
    native=native_direct(d,m,point,names);assert native['pass'] and jq(native['energy_MWh'])==upper
    return upper,dict(native_direct_check=native,finite_binary_upper_verified=True,original_binary_coordinates=12096,P_theta_bytes_preserved=True,canonical_YZ_exact=True,point_check=exact,raw_expanded_continuous_point=raw_check['full_expanded_pass'],raw_exact_point_check=raw_check,verified_upper_MWh=v.rat(upper))

def historical_cap_point_replays(records,mips):
    results=[]
    for case in CASES:
        old=ROOT/'results/research8h/seasonal_cap_continuation'/case
        if mips[case]['verdict']!='VERIFIED_UNCAPPED_BINARY_WITNESS_EXPANDED_MODEL':
            results.append({'case':case,'status':'NO_NEW_VERIFIED_UPPER_POINT','historical_run_verdict':'UNKNOWN_UNCHANGED'});continue
        d=BASE/case;point=a.array(d/'mip/recovered_vector.npz','vector');m=v.load_model(old);labels=a.labels(old/'row_metadata.csv.gz');mask=a.array(old/'integrality.npz','integrality')
        assert mask==(0,)*6888+(1,)*12096+(0,)*4032 and m.rows==34681 and m.cols==23016
        assert v.sha(old/'native_inputs.npz')==v.sha(d/'native_inputs.npz')
        caps=[i for i,row in enumerate(labels) if row['family']=='fossil_energy_cap'];assert len(caps)==1;cap=caps[0]
        budget=43131 if case in CASES[:2] else 125172
        assert m.row_lower[cap]==-math.inf and m.row_upper[cap]==budget
        cost=a.array(d/'objective.npz','objective');assert a.row(m,cap)=={j:x for j,x in enumerate(cost) if x}
        pc=a.point_audit(m,point,mask,labels);physical=native_direct(old,m,point,labels)
        energy=sum((Q(c)*Q(x) for c,x in zip(cost,point)),Q(0));assert energy==jq(physical['energy_MWh'])
        cap_pass=energy<=Q(budget)+TAU
        assert pc['full_expanded_pass']==cap_pass and physical['pass']
        parent_result=next(x for x in records if x['case']==case);assert parent_result['finite_binary_upper_verified']
        accepted=pc['full_expanded_pass'] and physical['pass'] and cap_pass
        results.append({'case':case,'status':'NEW_POSTHOC_EXPANDED_CAPPED_BINARY_WITNESS' if accepted else 'NEW_UNCAPPED_POINT_FAILS_OLD_CAP',
            'historical_run_verdict':'UNKNOWN_UNCHANGED','actual_parent_model_directory':str(old.relative_to(ROOT)),
            'parent_matrix_sha256':v.sha(old/'matrix.npz'),'parent_bounds_sha256':v.sha(old/'bounds.npz'),
            'parent_original_mask_sha256':v.sha(old/'integrality.npz'),'new_point_sha256':v.sha(d/'mip/recovered_vector.npz'),
            'old_cap_MWh':budget,'tau':v.rat(TAU),'new_point_fossil_MWh':v.rat(energy),
            'strict_cap_margin_MWh':v.rat(Q(budget)-energy),'exact_parent_point_check':pc,'direct_native_check':physical,
            'new_posthoc_expanded_cap_admission':accepted,'scope':'New proof from the later uncapped arm; no relabeling of the historical capped run or retroactive replication-gate success.'})
    return results

def main():
    started=time.perf_counter();completion=a.js(BASE/'completion.json');freeze=a.js(BASE/'prepared_freeze.json')
    assert freeze['manifest_sha256']==MANIFEST
    manifest=v.manifest_check(BASE/'input_manifest.csv',expected=MANIFEST);assert manifest['entries_checked']==397
    assert v.sha(Path(__file__).parent/'prepared_review.json')=='f73522fa656acffebcb417484359df4759e72caaadadf89fdc22f2eeb4632ef1'
    assert a.js(Path(__file__).parent/'prepared_review.json')['status']=='INDEPENDENT_SEASONAL_ALL_FOUR_ENERGY_PREPARED_PASS'
    assert completion['ordinary_denominator']==4 and completion['new_identity_MIP_calls']==0 and completion['all_frozen_hashes_unchanged'] and not completion['exact_optimality_claim']
    assert completion['historical_cap_UNKNOWNs_and_failed_gates_unchanged'] and completion['permutation_scope']=='Phi0 unrestricted interior; not HOD'
    global NATIVE
    native_root=Path(freeze['source_v3']);genfiles=list((native_root/'raw').rglob('gen.csv'));assert len(genfiles)==1
    native_base=genfiles[0].parent;genrows=csvrows(genfiles[0]);busrows=[r for r in csvrows(native_base/'bus.csv') if int(r['Area'])==1];busids=[int(r['Bus ID']) for r in busrows]
    slack=[i for i,r in enumerate(busrows) if r['Bus Type'].lower()=='ref'];assert len(slack)==1
    edges=[r for r in csvrows(native_base/'branch.csv') if int(r['From Bus']) in busids and int(r['To Bus']) in busids];assert len(edges)==38
    NATIVE={'gens':{r['GEN UID']:r for r in genrows},'buses':busids,'slack':slack[0],'branches':edges}
    historical=a.js(ROOT/'results/research8h/seasonal_cap_continuation/outcomes.json');assert [x['case'] for x in historical]==list(CASES) and all(x['verdict']=='UNKNOWN' for x in historical)
    hashes={str(p.relative_to(ROOT)):v.sha(p) for p in BASE.rglob('*') if p.is_file()}
    lps=a.js(BASE/'lp_results.json');mips=a.js(BASE/'mip_results.json');brackets=a.js(BASE/'energy_brackets.json');identities=a.js(BASE/'identity_energy_bounds.json')
    assert list(lps)==list(IDENTITIES+CASES) and list(mips)==list(CASES) and [x['case'] for x in brackets]==list(CASES)
    decimals(brackets);decimals(identities)
    expected=[('IDENTITY_LP',x) for x in IDENTITIES]+[('TARGET_MIP',x) for x in CASES]+[('TARGET_LP',x) for x in CASES]
    decisions=a.js(BASE/'launch_decisions.json');assert [(x['kind'],x['case']) for x in decisions]==expected
    calls=[];clock_diagnostics=[]
    for decision in decisions:
        case=decision['case'];kind=decision['kind'];r=mips[case] if kind=='TARGET_MIP' else lps[case];d=BASE/case
        guard=305 if kind=='TARGET_MIP' else 65;limit=300 if kind=='TARGET_MIP' else 60
        assert decision['guard_s']==guard and decision['admitted']==(min(decision['phase_remaining_s'],decision['cutoff_remaining_s'])>=guard)
        assert r['optimization_calls'] in (0,1) and bool(r['optimization_calls'])==decision['admitted'] and r['options']['time_limit']==limit and not r.get('exact_optimality_claim',False)
        assert r==a.js(d/('mip' if kind=='TARGET_MIP' else 'lp')/'result.json')
        if not r['optimization_calls']:
            assert r['elapsed_s']==0 and not r['solver_run_called'];continue
        assert r['prepared_manifest_sha256']==MANIFEST and all(v.sha(d/name)==sha for name,sha in r['model_artifacts'].items())
        log=(d/('mip' if kind=='TARGET_MIP' else 'lp')/'solver.log').read_text(encoding='utf-8')
        assert log.count('Running HiGHS')==1
        start=datetime.fromisoformat(r['started_utc']);end=datetime.fromisoformat(r['ended_utc']);decision_time=datetime.fromisoformat(decision['utc']);assert end>=start
        latency=(start-decision_time).total_seconds();remaining=(datetime.fromisoformat(freeze['cutoff_utc'])-start).total_seconds();phase_estimate=decision['phase_remaining_s']-latency
        clock_diagnostics.append(dict(case=case,kind=kind,decision_to_start_s=latency,actual_UTC_remaining_s=remaining,wall_adjusted_phase_estimate_s=phase_estimate,observed_consistent=latency>=0 and min(remaining,phase_estimate)>=guard))
        calls.append(dict(case=case,kind=kind,started_utc=r['started_utc'],ended_utc=r['ended_utc'],seconds=r['elapsed_s'],limit=limit))
    assert all(datetime.fromisoformat(x['ended_utc'])<=datetime.fromisoformat(y['started_utc']) for x,y in zip(calls,calls[1:]))
    records=[];identity_exact={}
    for case in IDENTITIES+CASES:
        d=BASE/case;m=v.load_model(d);names=a.labels(d/'row_metadata.csv.gz');c=a.array(d/'objective.npz','objective');mask=a.array(d/'original_integrality.npz','integrality')
        assert mask==(0,)*6888+(1,)*12096+(0,)*4032
        lower,bound=dual_check(d,m,c,lps[case]);out=dict(case=case,dual_bound=bound)
        # LP primal is an optional continuous diagnostic, never an operational upper.
        if lps[case].get('primal_valid'):
            primal=v.read_npz(d/'lp/primal.npz',('vector','row_value'))['vector'].values
            pc=a.point_audit(m,primal,(0,)*m.cols,names);out['LP_continuous_exact_point']=pc
        if case in IDENTITIES:
            month=int(case.split('_')[1]);point=a.array(d/'reference_upper_vector.npz','vector');pc=a.point_audit(m,point,mask,names);assert pc['full_expanded_pass']
            upper=sum((Q(x)*Q(y) for x,y in zip(c,point)),Q(0));saved=identities[str(month)];binding=a.js(d/'reference_binding.json')
            assert upper==jq(saved['upper_MWh'])==jq(binding['reference_upper_MWh']) and lower==jq(saved['lower_MWh']) and lower<=upper and upper>0
            native=native_direct(d,m,point,names);assert native['pass'] and jq(native['energy_MWh'])==upper
            identity_exact[month]=(lower,upper);out.update(reference_point=pc,native_direct_check=native,verified_reference_upper_MWh=v.rat(upper))
        else:
            saved=next(x for x in brackets if x['case']==case);month=saved['month'];li,ui=identity_exact[month]
            upper,point=binary_upper(d,m,c,names,mask,mips[case]);out.update(point)
            assert jq(saved['lower_MWh'])==lower and jq(saved['identity_lower_MWh'])==li and jq(saved['identity_reference_upper_MWh'])==ui
            assert saved['positive_lower_penalty_necessary_if_target_nonempty']==(lower>ui)
            oldcap=43131 if month==4 else 125172
            out['historical_cap_verdict']='UNKNOWN_UNCHANGED'
            out['new_uncapped_bound_excludes_historical_expanded_cap']=bool(lower>Q(oldcap)+TAU)
            out['new_cap_inference_scope']='Separate post-label lower-bound implication only; not a rewrite of the prior experiment or replication gate.'
            if upper is None:
                assert saved['upper_MWh'] is None and saved['upper_status']=='NO_UPPER' and not saved['finite_uncapped_feasibility_established']
                assert not any(k in saved for k in ('optimum_difference_MWh','target_optimum_excess_over_chosen_incumbent_MWh','optimal_relative_penalty','optimal_relative_penalty_percent'))
                assert saved['difference_interval_status']=='NOT_REPORTED_NO_FINITE_BINARY_UPPER'
            else:
                assert lower<=upper and jq(saved['upper_MWh'])==upper and saved['finite_uncapped_feasibility_established'] and saved['upper_status']=='VERIFIED_BINARY_UPPER'
                assert saved['strictly_positive_optimum_difference_certified']==(lower>ui)
                intervals={'optimum_difference_MWh':(lower-ui,upper-li),'target_optimum_excess_over_chosen_incumbent_MWh':(lower-ui,upper-ui)}
                if li>0 and lower>0:intervals.update(optimal_relative_penalty=(lower/ui-1,upper/li-1),optimal_relative_penalty_percent=(100*(lower/ui-1),100*(upper/li-1)))
                for key,(lo,hi) in intervals.items():assert jq(saved[key]['lower'])==lo and jq(saved[key]['upper'])==hi
                out.update(intervals_exact=True,intervals={k:{'lower':v.rat(lo),'upper':v.rat(hi)} for k,(lo,hi) in intervals.items()})
        records.append(out);print(json.dumps(dict(case=case,status='EXACT_REPLAY_PASS')),flush=True)
    for kind,key in [('IDENTITY_LP','identity_LP_calls'),('TARGET_LP','target_LP_calls'),('TARGET_MIP','target_MIP_calls')]:assert sum(x['kind']==kind for x in calls)==completion[key]
    miptime=sum(x['seconds'] for x in calls if x['kind']=='TARGET_MIP');lptime=sum(x['seconds'] for x in calls if x['kind']!='TARGET_MIP')
    assert abs(miptime-completion['actual_MIP_seconds'])<1e-8 and abs(lptime-completion['actual_LP_seconds'])<1e-8
    assert completion['soft_allocation_s']==2100 and abs(max(0.,completion['phase_elapsed_s']-2100)-completion['soft_allocation_overrun_s'])<1e-8
    assert sum(bool(x.get('finite_binary_upper_verified')) for x in records)==completion['accepted_target_uppers']
    assert abs(sum(max(0.,x['seconds']-x['limit']) for x in calls)-completion['solver_soft_overrun_s'])<1e-8
    new_cap_points=historical_cap_point_replays(records,mips)
    assert all(v.sha(ROOT/p)==sha for p,sha in hashes.items());v.manifest_check(BASE/'input_manifest.csv',expected=MANIFEST)
    cap_sidecar=dict(status='INDEPENDENT_POSTHOC_HISTORICAL_CAP_POINT_REPLAY_COMPLETE',optimizer_calls=0,ordinary_denominator=4,all_accepted_new_points_checked=True,cases=new_cap_points,source_sha256=v.sha(Path(__file__)))
    with (Path(__file__).parent/'new_historical_cap_points.json').open('x',encoding='utf-8') as f:json.dump(cap_sidecar,f,indent=2,allow_nan=False);f.write('\n')
    report=dict(status='INDEPENDENT_SEASONAL_ALL_FOUR_ENERGY_POSTRUN_PASS',optimizer_calls=0,ordinary_denominator=4,identity_denominator=2,manifest_sha256=MANIFEST,frozen_bindings=397,cases=records,calls=calls,clock_diagnostics=clock_diagnostics,clock_scope='Actual UTC values checked; wall-adjusted phase estimate is not a saved monotonic final-call measurement.',actual_MIP_seconds=miptime,actual_LP_seconds=lptime,phase_elapsed_s=completion['phase_elapsed_s'],accepted_binary_uppers=completion['accepted_target_uppers'],all_hashes_unchanged=True,input_and_result_hashes=hashes,review_source_sha256=v.sha(Path(__file__)),elapsed_s=time.perf_counter()-started,posthoc_cap_point_sidecar_sha256=v.sha(Path(__file__).parent/'new_historical_cap_points.json'),native_scope='Direct rational generator/availability/hydro/canonical-state/residence/on-on-ramp/supplied-angle graph checks use raw GEN/branch/bus CSVs and native hourly packages. Nodal operator coefficients are the unchanged archived rounded Bbus encoding, already provenance-audited; no native model import or reconstructed-angle numerical solve.',exact_optimality_claim=False)
    with (Path(__file__).parent/'postrun_review.json').open('x',encoding='utf-8') as stream:json.dump(report,stream,indent=2,allow_nan=False);stream.write('\n')
    print(json.dumps(dict(status=report['status'],accepted_binary_uppers=report['accepted_binary_uppers'],elapsed_s=report['elapsed_s'])),flush=True)
if __name__=='__main__':main()
