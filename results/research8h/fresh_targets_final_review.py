"""Independent final ledger for fresh January targets, with exact LP point replay."""
import importlib.util,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'results/research8h/fresh_january_weeks/targets';OUT=ROOT/'results/research8h/fresh_targets_postrun_review'
sp=importlib.util.spec_from_file_location('fresh_final_helpers',ROOT/'results/research8h/seasonal_cap_prepared_review.py');a=importlib.util.module_from_spec(sp);sys.modules[sp.name]=a;sp.loader.exec_module(a);v=a.reader
CASES=('seed_26093210','seed_26093211','seed_26093220','seed_26093221')
def main():
    started=time.perf_counter();freeze=a.js(BASE/'prepared_freeze.json');v.manifest_check(BASE/'input_manifest.csv',expected=freeze['manifest_sha256'])
    rays=a.js(OUT/'negative_certificates.json');assert rays['status']=='INDEPENDENT_THREE_FRESH_NEGATIVE_CERTIFICATES_PASS'
    assert all(v.sha(ROOT/p)==sha for p,sha in rays['replayed_output_hashes'].items())
    results=a.js(BASE/'outcomes.json');completion=a.js(BASE/'completion.json');assert tuple(x['case'] for x in results)==CASES
    files=[BASE/n for n in ('outcomes.json','completion.json','final_manifest_check.json','execution_started.json')]
    for c in CASES:
        for part in ('lp','mip'):
            if (BASE/c/part).exists():files.extend(p for p in (BASE/c/part).iterdir() if p.is_file())
    hashes={str(p.relative_to(ROOT)):v.sha(p) for p in files};calls=[]
    for item in results:
        c=item['case'];d=BASE/c;lp=a.js(d/'lp/result.json');assert item['LP_calls']==lp['optimization_calls']==1 and lp['time_limit_s']==30
        log=d/'lp/solver.log';text=log.read_text();assert text.count('Running HiGHS')==1
        calls.append(dict(case=c,kind='LP',seconds=lp['elapsed_s'],limit=30,log_mtime_ns=log.stat().st_mtime_ns))
        if c=='seed_26093211':
            assert item['verdict']=='UNKNOWN' and item['MIP_calls']==1 and item['route']=='MIP'
            assert lp['verdict']=='NUMERICAL_CONTINUOUS_FEASIBLE_BINARY_UNKNOWN' and lp['solution_value_valid'] and lp['returned_vector_check']['pass']
            m=v.load_model(d/'lp');point=a.array(d/'lp/returned_vector.npz','vector');names=a.labels(d/'lp/row_metadata.csv.gz')
            exact=a.point_audit(m,point,(0,)*m.cols,names);assert exact['full_expanded_pass']
            assert not all(x in (0,1) for x in point[6888:18984]);exact_fractional=sum(x not in (0,1) for x in point[6888:18984])
            mip=a.js(d/'mip/result.json');assert mip['verdict']=='UNKNOWN' and mip['optimization_calls']==1 and not mip['solution_value_valid'] and mip['model_status']=='Time limit reached' and mip['time_limit_s']==300
            assert not any((d/'mip'/f).exists() for f in ('raw_vector.npz','recovered_vector.npz','returned_vector.npz'))
            log=d/'mip/solver.log';assert log.read_text().count('Running HiGHS')==1
            mipcall=dict(case=c,kind='MIP',seconds=mip['elapsed_s'],limit=300,log_mtime_ns=log.stat().st_mtime_ns)
        else:
            assert item['verdict']==lp['verdict']=='CERTIFIED_INFEASIBLE_EXPANDED_MODEL' and item['MIP_calls']==0 and item['route']=='EXACT_ROBUST_LP_RAY' and not (d/'mip').exists()
            assert any(x['case']==c and x['status']=='CERTIFIED_EXPANDED_INFEASIBLE' for x in rays['cases'])
    calls.append(mipcall);assert all(x['log_mtime_ns']<=y['log_mtime_ns'] for x,y in zip(calls,calls[1:]))
    assert completion['intended_ordinary_cases']==4 and completion['intended_controls']==2 and completion['LP_calls']==4 and completion['MIP_calls']==1
    assert abs(sum(x['seconds'] for x in calls if x['kind']=='LP')-completion['actual_LP_seconds'])<1e-8 and mipcall['seconds']==completion['actual_MIP_seconds']
    assert completion['phase_elapsed_s']>=sum(x['seconds'] for x in calls) and completion['phase_overrun_s']==max(0,completion['phase_elapsed_s']-2100)
    assert a.js(BASE/'final_manifest_check.json')['pass'];assert all(v.sha(ROOT/p)==sha for p,sha in hashes.items());v.manifest_check(BASE/'input_manifest.csv',expected=freeze['manifest_sha256'])
    out=dict(status='INDEPENDENT_FRESH_TARGET_FINAL_REVIEW_PASS',optimizer_calls=0,ordinary_denominator=4,certified_expanded_negatives=3,verified_target_binary_positives=0,binary_unknown=1,negative_case_ids=[x['case'] for x in rays['cases']],unknown_case='seed_26093211',unknown_LP_exact_expanded_continuous_point=exact,unknown_LP_exact_nonbinary_state_coordinates=exact_fractional,unknown_MIP_no_returned_incumbent=True,call_order_source_reviewed_and_log_completion_times_consistent=True,calls=calls,solver_calls=5,actual_LP_seconds=completion['actual_LP_seconds'],actual_MIP_seconds=completion['actual_MIP_seconds'],phase_elapsed_s=completion['phase_elapsed_s'],total_soft_solver_overrun_s=sum(max(0,x['seconds']-x['limit']) for x in calls),manifest_sha256=freeze['manifest_sha256'],frozen_bindings=246,all_hashes_unchanged=True,negative_review_sha256=v.sha(OUT/'negative_certificates.json'),replayed_output_hashes=hashes,review_source_sha256=v.sha(Path(__file__)),elapsed_seconds=time.perf_counter()-started,scope='Full denominator retained. Log completion order supports reviewed sequential source; no unrecorded precise solver start times inferred. No nominal strict feasibility or population success-rate claim.')
    with (OUT/'final_ledger.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({'status':out['status'],'seconds':out['elapsed_seconds'],'negatives':3,'unknown':1}),flush=True)
if __name__=='__main__':main()
