"""Read-only independent HOD post-run proof, point, provenance and accounting audit."""
import csv, importlib.util, json, math, sys, time
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/research8h/hour_of_day'
sp=importlib.util.spec_from_file_location('hod_review_helpers',ROOT/'results/research8h/seasonal_cap_prepared_review.py')
a=importlib.util.module_from_spec(sp);sys.modules[sp.name]=a;sp.loader.exec_module(a);v=a.reader
CASES=('seed_26093200','seed_26093201')
MANIFEST='078082667f83322d3540ad3ac215ebcc996d0d31b04fd52bfa75c1d2fd814fcc'
def jq(r):return Q(int(r['numerator']),int(r['denominator']))
def main():
    started=time.perf_counter()
    before=v.manifest_check(OUT/'input_manifest.csv',expected=MANIFEST)
    assert before['entries_checked']==125
    freeze=a.js(OUT/'prepared_freeze.json');prepared=a.js(OUT/'independent_prepared_review.json')
    assert freeze['optimizations_started']==0 and freeze['manifest_sha256']==MANIFEST
    assert 'PASS' in prepared['status']
    outputs=a.js(OUT/'outcomes.json');completion=a.js(OUT/'completion.json')
    assert tuple(x['case'] for x in outputs)==CASES
    assert all(x['verdict']=='CERTIFIED_INFEASIBLE_EXPANDED_MODEL' and x['route']=='EXACT_ROBUST_LP_RAY' and x['LP_calls']==1 and x['MIP_calls']==0 for x in outputs)
    audit_paths=[OUT/f for f in ('outcomes.json','completion.json','postrun_allocation_audit.json','aborted_instrumentation_attempt.json','execution_started.json','timed_execution_started.json')]
    for c in CASES:audit_paths.extend(p for p in (OUT/c/'lp').iterdir() if p.is_file())
    initial_hash={str(p.relative_to(ROOT)):v.sha(p) for p in audit_paths}
    results=[];lpseconds=0;logs=[]
    for c in CASES:
        d=OUT/c;lp=d/'lp';m=v.load_model(lp);names=a.labels(lp/'row_metadata.csv.gz')
        assert not (d/'mip').exists()
        for f in ('matrix.npz','bounds.npz','integrality.npz','row_metadata.csv.gz'):assert v.sha(lp/f)==v.sha(d/f)
        cert=a.js(lp/'dual_certificate.json');rec=a.js(lp/'result.json')
        v.ray_bindings(lp,cert,OUT/'input_manifest.csv',())
        assert cert['orientation']==1 and cert['candidate']=='projected_to_row_sign_cone'
        assert rec['model_status']=='Infeasible' and rec['time_limit_s']==30 and rec['elapsed_s']<30
        assert rec['certificate_verification']==cert['verification']
        raw=v.read_npz(lp/'raw_solver_ray.npz',('multipliers',))['multipliers']
        assert raw.dtype=='<f8' and raw.shape==(m.rows,) and all(math.isfinite(x) for x in raw.values)
        parsed={}
        for x in cert['multipliers']:
            assert type(x['row']) is int and x['row'] not in parsed and 0<=x['row']<m.rows
            f=float.fromhex(x['value_hex']);assert math.isfinite(f) and f!=0;parsed[x['row']]=Q(f)
        expected={};invalid=[]
        for r,dv in enumerate(raw.values):
            if not dv:continue
            if math.isfinite(m.row_lower[r] if dv>0 else m.row_upper[r]):expected[r]=Q(dv)
            else:invalid.append(r)
        assert expected==parsed and len(invalid)==cert['verification']['inadmissible_raw_entries']
        raw_rejected=False
        try:v.check_ray(m,{r:Q(x) for r,x in enumerate(raw.values) if x},Q.from_float(1e-5))
        except v.InvalidInput:raw_rejected=True
        assert raw_rejected
        exact=v.check_ray(m,parsed,Q.from_float(1e-5))
        assert exact['status']=='CERTIFIED_EXPANDED_INFEASIBLE' and exact['expanded_pass'] and exact['strict_pass']
        assert all(v.archived_ray_comparison(cert,exact).values())
        assert exact['row_multiplier_nonzeros']==cert['verification']['row_multiplier_nonzeros']
        assert exact['combined_column_nonzeros']==cert['verification']['combined_column_nonzeros']
        with (lp/'sparse_multipliers.csv').open(newline='') as f:sparse=list(csv.DictReader(f))
        assert len(sparse)==len(parsed)
        assert {int(x['row']):Q(float(x['multiplier'])) for x in sparse}==parsed
        family=dict(Counter(names[r]['family'] for r in parsed))
        assert family==cert['support']['row_family_counts'] and family.get('fossil_energy_cap')==1
        assert not any('mean' in f for f in family)
        cap=next(r for r in parsed if names[r]['family']=='fossil_energy_cap')
        assert m.row_lower[cap]==-math.inf and m.row_upper[cap]==23195 and parsed[cap]<0
        assert all(x==1 for x in a.row(m,cap).values()) and len(a.row(m,cap))==168*23
        log=lp/'solver.log';txt=log.read_text();assert txt.count('Running HiGHS')==1 and 'Model status' in txt and 'Infeasible' in txt
        logs.append(log.stat());lpseconds+=rec['elapsed_s']
        result=dict(case=c,status=exact['status'],solver_seconds=rec['elapsed_s'],raw_ray_rejected=True,raw_sign_projected_entries=len(invalid),projected_ray_exactly_matches_archive=True,exact=exact,row_family_support=family,source_and_lp_model_hashes_match=True,certificate_sha256=v.sha(lp/'dual_certificate.json'))
        results.append(result);print(json.dumps({'case':c,'status':exact['status'],'expanded_gap':exact['expanded_separation_gap']['float']}),flush=True)
    assert logs[0].st_mtime_ns<=logs[1].st_ctime_ns
    positives=[];statics=[]
    for c in ('january_identity',*CASES,'seed_26100200'):
        d=OUT/c;m=v.load_model(d);names=a.labels(d/'row_metadata.csv.gz');mask=a.array(d/'integrality.npz','integrality');point=a.array(d/'constructive_vector.npz','vector')
        assert mask==(0,)*6888+(1,)*12096+(0,)*4032
        exact=a.point_audit(m,point,mask,names);saved=a.js(d/'constructive_check.json')
        assert exact['static_expanded_pass'] and not exact['full_strict_pass']
        assert exact['full_expanded_pass']==saved['full_exact']['expanded_pass']==(c not in CASES)
        assert jq(exact['maximum_column_violation'])==jq(saved['full_exact']['maximum_column_violation'])
        assert jq(exact['maximum_row_violation'])==jq(saved['full_exact']['maximum_row_violation'])
        meta=a.js(d/'model_metadata.json');fossil=[meta['unit_names'].index(x) for x in meta['fossil_units']]
        energy=sum((Q(point[t*41+j]) for t in range(168) for j in fossil),Q(0))
        assert energy==jq(saved['exact_fossil_MWh'])==Q(1654798412944827657145,72057594037927936)
        record=dict(case=c,static_expanded_pass=True,full_expanded_pass=exact['full_expanded_pass'],strict_pass=False,original_binary_coordinates=12096,exact_fossil_MWh=v.rat(energy),maximum_column_violation=exact['maximum_column_violation'],maximum_row_violation=exact['maximum_row_violation'])
        statics.append(record)
        if c not in CASES:
            assert saved['constructive_expanded_pass'] and saved['numerical']['physical']['pass'];positives.append(record)
    assert completion['LP_calls']==2 and completion['MIP_calls']==0 and completion['ordinary_denominator']==2
    assert completion['actual_LP_seconds']==lpseconds and completion['actual_MIP_seconds']==0
    assert completion['phase_elapsed_s']>=lpseconds and completion['phase_elapsed_s']<1200
    abort=a.js(OUT/'aborted_instrumentation_attempt.json');allocation=a.js(OUT/'postrun_allocation_audit.json')
    assert abort['optimization_calls']==0 and abort['frozen_execution_marker_absent'] and abort['solver_logs_and_result_files_absent']
    assert allocation['aborted_optional_instrumentation']['record_sha256']==v.sha(OUT/'aborted_instrumentation_attempt.json')
    assert allocation['actual_LP_seconds']==lpseconds and allocation['MIP_calls']==0 and allocation['LP_calls']==2
    assert not allocation['hard_wall_time_cap_claim'] and allocation['allocation_start_not_instrumented']
    assert v.manifest_check(OUT/'input_manifest.csv',expected=MANIFEST)['entries_checked']==125
    assert all(v.sha(ROOT/p)==h for p,h in initial_hash.items())
    out=dict(status='INDEPENDENT_HOD_POSTRUN_PASS',optimizer_calls=0,frozen_entries=125,all_frozen_and_replayed_output_hashes_unchanged=True,manifest_sha256=MANIFEST,ray_results=results,positive_controls=positives,all_constructive_static_points=statics,LP_calls=2,MIP_calls=0,actual_LP_seconds=lpseconds,phase_elapsed_seconds=completion['phase_elapsed_s'],aborted_wrapper_scope='Archived producer record reports no execution marker or solver artifacts at termination; this audit cannot independently reconstruct past process state. Two current solver logs each show one invocation.',review_source_sha256=v.sha(Path(__file__)),reader_sha256=v.sha(ROOT/'src/research8h_standalone_verify.py'),point_helper_sha256=v.sha(ROOT/'results/research8h/seasonal_cap_prepared_review.py'),replayed_output_hashes=initial_hash,elapsed_seconds=time.perf_counter()-started,scope='Archived full-network uniform expanded binary64 model; no new native data reassembly, optimization, independent week or physically observed shuffled trajectory')
    with (OUT/'independent_postrun_review.json').open('x',encoding='utf-8') as f:json.dump(out,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({'status':out['status'],'seconds':out['elapsed_seconds']}),flush=True)
if __name__=='__main__':main()
