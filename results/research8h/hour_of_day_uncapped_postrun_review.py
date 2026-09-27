"""Independent post-run HOD uncapped point, dual bound and accounting audit. No optimizers."""
import importlib.util,json,math,struct,sys,time
from datetime import datetime
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'results/research8h/hour_of_day_uncapped'
sp=importlib.util.spec_from_file_location('independent_hod_energy_prepared',ROOT/'results/research8h/hour_of_day_uncapped_prepared_review.py');h=importlib.util.module_from_spec(sp);sys.modules[sp.name]=h;sp.loader.exec_module(h)
a=h.a;v=h.v;jq=h.jq;CASES=h.CASES

def main():
    start=time.perf_counter();completion=a.js(BASE/'completion.json');freeze=a.js(BASE/'prepared_freeze.json')
    manifest=v.manifest_check(BASE/'input_manifest.csv',expected=freeze['manifest_sha256'])
    files=sorted(p for p in BASE.rglob('*') if p.is_file() and p.name!='independent_postrun_review.json')
    hashes={str(p.relative_to(ROOT)):v.sha(p) for p in files}
    assert completion['new_identity_solves']==0 and completion['ordinary_denominator']==2
    identity=a.js(BASE/'reused_identity_bounds.json');li=jq(identity['lower_MWh']);ui=jq(identity['reference_upper_MWh'])
    assert 0<li<=ui and a.js(BASE/'independent_prepared_review.json')['status']=='INDEPENDENT_HOD_UNCAPPED_PREPARED_PASS'
    brackets=a.js(BASE/'energy_brackets.json');assert [x['case'] for x in brackets]==list(CASES)
    decisions=a.js(BASE/'launch_decisions.json');assert [(x['kind'],x['case']) for x in decisions]==[(kind,c) for kind in ('MIP','LP') for c in CASES]
    for d in decisions:
        assert d['guard_s']==(605 if d['kind']=='MIP' else 65)
        assert d['admitted']==(min(d['phase_remaining_s'],d['cutoff_remaining_s'])>=d['guard_s'])
    records=[];calls=[];tau=Q.from_float(1e-5)
    for case,saved_bracket in zip(CASES,brackets):
        d=BASE/case;m=v.load_model(d);names=a.labels(d/'row_metadata.csv.gz');cost=a.array(d/'objective.npz','objective')
        original=a.array(d/'original_integrality.npz','integrality');assert original==(0,)*6888+(1,)*12096+(0,)*4032
        mip=a.js(d/'mip/result.json');lp=a.js(d/'lp/result.json');out=dict(case=case,MIP_verdict=mip['verdict'],LP_model_status=lp.get('model_status'),exact_optimality_claim=False)
        for kind,r in (('MIP',mip),('LP',lp)):
            assert r['optimization_calls'] in (0,1) and not r.get('exact_optimality_claim',False)
            if r['optimization_calls']:
                assert r['options']['time_limit']==(600 if kind=='MIP' else 60)
                assert r['prepared_manifest_sha256']==freeze['manifest_sha256']
                assert all(v.sha(d/name)==sha for name,sha in r['model_artifacts'].items())
                utc=datetime.fromisoformat(r['started_utc']);end=datetime.fromisoformat(r['ended_utc']);assert end>=utc
                calls.append(dict(case=case,kind=kind,started_utc=r['started_utc'],ended_utc=r['ended_utc'],seconds=r['elapsed_s'],limit=r['options']['time_limit']))
        upper=None
        if mip['verdict']=='VERIFIED_UNCAPPED_BINARY_WITNESS_EXPANDED_MODEL':
            raw=a.array(d/'mip/raw_vector.npz','vector');point=a.array(d/'mip/recovered_vector.npz','vector');assert len(raw)==len(point)==23016
            for lo,hi in ((0,6888),(18984,23016)):
                assert struct.pack('<'+str(hi-lo)+'d',*raw[lo:hi])==struct.pack('<'+str(hi-lo)+'d',*point[lo:hi])
            u=point[6888:10920];assert all(x in (0,1) for x in u)
            assert all(abs(Q(raw[6888+j])-Q(x))<=tau for j,x in enumerate(u))
            for t in range(168):
                for j in range(24):
                    change=0 if t==0 else u[t*24+j]-u[(t-1)*24+j]
                    assert point[10920+t*24+j]==max(0,change) and point[14952+t*24+j]==max(0,-change)
            exact=a.point_audit(m,point,original,names);stored=a.js(d/'mip/exact_point_check.json')
            assert exact['full_expanded_pass'] and exact['full_strict_pass']==stored['strict_pass']==mip['exact_strict_pass']
            for field in ('maximum_column_violation','maximum_row_violation'):assert jq(exact[field])==jq(stored[field])
            assert mip['raw_matrix_check']['pass'] and mip['recovered_matrix_check']['pass'] and mip['native_no_cap_pass'] and a.js(d/'mip/native_no_cap_check.json')['pass']
            raw_check=a.point_audit(m,raw,(0,)*m.cols,names);assert raw_check['full_expanded_pass']
            upper=sum((Q(x)*Q(y) for x,y in zip(cost,point)),Q(0));assert upper==jq(mip['verified_upper_MWh'])==jq(mip['candidate_fossil_MWh'])
            out.update(original_binary_coordinates=12096,P_theta_bytes_preserved=True,canonical_YZ_exact=True,recovered_point=exact,raw_expanded_continuous_point=True,verified_upper_MWh=v.rat(upper))
        else:assert mip['verdict']=='UNKNOWN' and 'verified_upper_MWh' not in mip
        baseline=jq(a.js(d/'zero_dual_baseline.json')['expanded_lower_bound_MWh']);lower=baseline
        if lp.get('new_lower_bound_status')=='EXACT_EXPANDED_OBJECTIVE_LOWER_BOUND':
            raw=v.read_npz(d/'lp/raw_duals.npz',('row_dual','column_dual'))['row_dual'].values;projected=a.array(d/'lp/projected_row_dual.npz','row_dual')
            assert len(raw)==len(projected)==m.rows and all(math.isfinite(x) for x in raw)
            expected=tuple(0. if x>0 and not math.isfinite(m.row_lower[r]) or x<0 and not math.isfinite(m.row_upper[r]) else x for r,x in enumerate(raw))
            assert expected==projected
            bound=h.objective_lower(m,cost,projected);stored=a.js(d/'lp/exact_lower_bound.json')
            assert all(jq(bound[k])==jq(stored[k]) for k in bound)
            changed=sum(x!=y for x,y in zip(raw,projected));assert changed==stored['projected_entries']
            assert jq(lp['expanded_lower_MWh'])==jq(bound['expanded_lower_bound_MWh'])
            lower=max(lower,jq(bound['expanded_lower_bound_MWh']))
            out.update(exact_dual_bound=bound,invalid_endpoint_projection_checked=True,projected_entries=changed)
        assert jq(saved_bracket['lower_MWh'])==lower and jq(saved_bracket['identity_lower_MWh'])==li and jq(saved_bracket['identity_reference_upper_MWh'])==ui
        if upper is None:assert saved_bracket['upper_MWh'] is None and not saved_bracket['finite_uncapped_feasibility_established']
        else:
            assert lower<=upper and jq(saved_bracket['upper_MWh'])==upper and saved_bracket['finite_uncapped_feasibility_established']
            expected={'optimum_difference_MWh':(lower-ui,upper-li),'target_optimum_excess_over_chosen_incumbent_MWh':(lower-ui,upper-ui)}
            if lower>0:expected.update(optimal_relative_penalty=(lower/ui-1,upper/li-1),optimal_relative_penalty_percent=(100*(lower/ui-1),100*(upper/li-1)))
            for field,(lo,hi) in expected.items():assert jq(saved_bracket[field]['lower'])==lo and jq(saved_bracket[field]['upper'])==hi
            out['exact_bracket_arithmetic']=True
        out.update(exact_lower_MWh=v.rat(lower),finite_binary_upper_verified=upper is not None);records.append(out)
    calls.sort(key=lambda x:datetime.fromisoformat(x['started_utc']))
    assert len(calls)==completion['MIP_calls']+completion['LP_calls']
    order=[(kind,c) for kind in ('MIP','LP') for c in CASES];assert [(x['kind'],x['case']) for x in calls]==[x for x in order if any(c['kind']==x[0] and c['case']==x[1] for c in calls)]
    assert all(datetime.fromisoformat(x['ended_utc'])<=datetime.fromisoformat(y['started_utc']) for x,y in zip(calls,calls[1:]))
    for kind in ('MIP','LP'):
        assert sum(x['kind']==kind for x in calls)==completion[kind+'_calls']
        assert abs(sum(x['seconds'] for x in calls if x['kind']==kind)-completion['actual_'+kind+'_seconds'])<1e-8
    assert sum(r['finite_binary_upper_verified'] for r in records)==completion['accepted_upper_witnesses']
    assert all(v.sha(ROOT/p)==sha for p,sha in hashes.items());v.manifest_check(BASE/'input_manifest.csv',expected=freeze['manifest_sha256'])
    out=dict(status='INDEPENDENT_HOD_UNCAPPED_POSTRUN_PASS',optimizer_calls=0,manifest_sha256=freeze['manifest_sha256'],frozen_bindings=manifest['entries_checked'],all_frozen_and_replayed_hashes_unchanged=True,cases=records,call_order=calls,actual_MIP_seconds=completion['actual_MIP_seconds'],actual_LP_seconds=completion['actual_LP_seconds'],phase_elapsed_s=completion['phase_elapsed_s'],soft_solver_overrun_s=sum(max(0,x['seconds']-x['limit']) for x in calls),native_scope='Stored native checks pass; native input/matrix provenance established independently at prepared gate. Native physical assembler not rerun.',strict_model_optimality_claim=False,review_source_sha256=v.sha(Path(__file__)),input_and_result_hashes=hashes,elapsed_seconds=time.perf_counter()-start)
    with (BASE/'independent_postrun_review.json').open('x',encoding='utf-8') as f:json.dump(out,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({'status':out['status'],'seconds':out['elapsed_seconds'],'upper_witnesses':completion['accepted_upper_witnesses']}),flush=True)
if __name__=='__main__':main()
