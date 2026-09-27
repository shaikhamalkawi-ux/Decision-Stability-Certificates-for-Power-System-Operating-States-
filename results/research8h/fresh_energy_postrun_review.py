"""Independent stdlib post-run fresh-energy audit; no optimizer or producer imports."""
import importlib.util,json,math,struct,sys,time
from datetime import datetime
from fractions import Fraction as Q
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'results/research8h/fresh_january_energy'
sp=importlib.util.spec_from_file_location('fresh_energy_independent_helpers',ROOT/'results/research8h/hour_of_day_uncapped_prepared_review.py');h=importlib.util.module_from_spec(sp);sys.modules[sp.name]=h;sp.loader.exec_module(h)
a=h.a;v=h.v;jq=h.jq;TAU=Q.from_float(1e-5)
CASES=('seed_26093210','seed_26093211','seed_26093220','seed_26093221');IDENTITIES=('week_2_identity','week_3_identity')
MANIFEST='44b382d30a30b8485beda0cf080d22cd991b55a9f37491939f633d147bc14f2a'
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

def binary_upper(d,m,c,names,original,mip):
    if mip['verdict']!='VERIFIED_UNCAPPED_BINARY_WITNESS_EXPANDED_MODEL':
        assert mip['verdict']=='UNKNOWN' and 'verified_upper_MWh' not in mip
        return None,dict(finite_binary_upper_verified=False,verdict=mip['verdict'])
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
    raw_check=a.point_audit(m,raw,(0,)*m.cols,names);assert raw_check['full_expanded_pass']
    upper=sum((Q(x)*Q(y) for x,y in zip(c,point)),Q(0));assert upper==jq(mip['verified_upper_MWh'])==jq(mip['candidate_fossil_MWh'])
    return upper,dict(finite_binary_upper_verified=True,original_binary_coordinates=12096,P_theta_bytes_preserved=True,canonical_YZ_exact=True,point_check=exact,raw_expanded_continuous_point=True,verified_upper_MWh=v.rat(upper))

def main():
    started=time.perf_counter();completion=a.js(BASE/'completion.json');freeze=a.js(BASE/'prepared_freeze.json')
    assert freeze['manifest_sha256']==MANIFEST
    manifest=v.manifest_check(BASE/'input_manifest.csv',expected=MANIFEST);assert manifest['entries_checked']==378
    assert a.js(ROOT/'results/research8h/fresh_energy_review/prepared.json')['status']=='INDEPENDENT_FRESH_ENERGY_PREPARED_PASS'
    assert completion['ordinary_denominator']==4 and completion['new_identity_MIP_calls']==0 and completion['all_frozen_hashes_unchanged'] and not completion['exact_optimality_claim']
    hashes={str(p.relative_to(ROOT)):v.sha(p) for p in BASE.rglob('*') if p.is_file()}
    lps=a.js(BASE/'lp_results.json');mips=a.js(BASE/'mip_results.json');brackets=a.js(BASE/'energy_brackets.json');identities=a.js(BASE/'identity_energy_bounds.json')
    assert list(lps)==list(IDENTITIES+CASES) and list(mips)==list(CASES) and [x['case'] for x in brackets]==list(CASES)
    decimals(brackets);decimals(identities)
    expected=[('IDENTITY_LP',x) for x in IDENTITIES]+[('TARGET_MIP',x) for x in CASES]+[('TARGET_LP',x) for x in CASES]
    decisions=a.js(BASE/'launch_decisions.json');assert [(x['kind'],x['case']) for x in decisions]==expected
    calls=[];clock_diagnostics=[]
    for decision in decisions:
        case=decision['case'];kind=decision['kind'];r=mips[case] if kind=='TARGET_MIP' else lps[case];d=BASE/case
        guard=605 if kind=='TARGET_MIP' else 65;limit=600 if kind=='TARGET_MIP' else 60
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
            week=int(case.split('_')[1]);point=a.array(d/'reference_upper_vector.npz','vector');pc=a.point_audit(m,point,mask,names);assert pc['full_expanded_pass']
            upper=sum((Q(x)*Q(y) for x,y in zip(c,point)),Q(0));saved=identities[str(week)];binding=a.js(d/'reference_binding.json')
            assert upper==jq(saved['upper_MWh'])==jq(binding['reference_upper_MWh']) and lower==jq(saved['lower_MWh']) and 0<lower<=upper
            identity_exact[week]=(lower,upper);out.update(reference_point=pc,verified_reference_upper_MWh=v.rat(upper))
        else:
            saved=next(x for x in brackets if x['case']==case);week=saved['week'];li,ui=identity_exact[week]
            upper,point=binary_upper(d,m,c,names,mask,mips[case]);out.update(point)
            assert jq(saved['lower_MWh'])==lower and jq(saved['identity_lower_MWh'])==li and jq(saved['identity_reference_upper_MWh'])==ui
            assert saved['positive_lower_penalty_necessary_if_target_nonempty']==(lower>ui)
            if upper is None:
                assert saved['upper_MWh'] is None and saved['upper_status']=='NO_UPPER' and not saved['finite_uncapped_feasibility_established'] and 'optimum_difference_MWh' not in saved
            else:
                assert lower<=upper and jq(saved['upper_MWh'])==upper and saved['finite_uncapped_feasibility_established']
                intervals={'optimum_difference_MWh':(lower-ui,upper-li),'target_optimum_excess_over_chosen_incumbent_MWh':(lower-ui,upper-ui)}
                if li>0 and lower>0:intervals.update(optimal_relative_penalty=(lower/ui-1,upper/li-1),optimal_relative_penalty_percent=(100*(lower/ui-1),100*(upper/li-1)))
                for key,(lo,hi) in intervals.items():assert jq(saved[key]['lower'])==lo and jq(saved[key]['upper'])==hi
                out.update(intervals_exact=True,intervals={k:{'lower':v.rat(lo),'upper':v.rat(hi)} for k,(lo,hi) in intervals.items()})
        records.append(out);print(json.dumps(dict(case=case,status='EXACT_REPLAY_PASS')),flush=True)
    for kind,key in [('IDENTITY_LP','identity_LP_calls'),('TARGET_LP','target_LP_calls'),('TARGET_MIP','target_MIP_calls')]:assert sum(x['kind']==kind for x in calls)==completion[key]
    miptime=sum(x['seconds'] for x in calls if x['kind']=='TARGET_MIP');lptime=sum(x['seconds'] for x in calls if x['kind']!='TARGET_MIP')
    assert abs(miptime-completion['actual_MIP_seconds'])<1e-8 and abs(lptime-completion['actual_LP_seconds'])<1e-8
    assert sum(bool(x.get('finite_binary_upper_verified')) for x in records)==completion['accepted_target_uppers']
    assert abs(sum(max(0.,x['seconds']-x['limit']) for x in calls)-completion['solver_soft_overrun_s'])<1e-8
    assert all(v.sha(ROOT/p)==sha for p,sha in hashes.items());v.manifest_check(BASE/'input_manifest.csv',expected=MANIFEST)
    report=dict(status='INDEPENDENT_FRESH_ENERGY_POSTRUN_PASS',optimizer_calls=0,ordinary_denominator=4,identity_denominator=2,manifest_sha256=MANIFEST,frozen_bindings=378,cases=records,calls=calls,clock_diagnostics=clock_diagnostics,clock_scope='Actual UTC values checked; wall-adjusted phase estimate is not a saved monotonic final-call measurement.',actual_MIP_seconds=miptime,actual_LP_seconds=lptime,phase_elapsed_s=completion['phase_elapsed_s'],accepted_binary_uppers=completion['accepted_target_uppers'],all_hashes_unchanged=True,input_and_result_hashes=hashes,review_source_sha256=v.sha(Path(__file__)),elapsed_s=time.perf_counter()-started,native_scope='Native model provenance independently checked at prepared gate; stored native no-cap checks inspected, native physical assembler not rerun.',exact_optimality_claim=False)
    with (ROOT/'results/research8h/fresh_energy_review/postrun.json').open('x',encoding='utf-8') as stream:json.dump(report,stream,indent=2,allow_nan=False);stream.write('\n')
    print(json.dumps(dict(status=report['status'],accepted_binary_uppers=report['accepted_binary_uppers'],elapsed_s=report['elapsed_s'])),flush=True)
if __name__=='__main__':main()
