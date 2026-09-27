"""Independent replay of the three completed fresh-week exact negative certificates."""
import csv,importlib.util,json,math,sys,time
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'results/research8h/fresh_january_weeks/targets';OUT=ROOT/'results/research8h/fresh_targets_postrun_review'
sp=importlib.util.spec_from_file_location('fresh_ray_helpers',ROOT/'results/research8h/seasonal_cap_prepared_review.py');a=importlib.util.module_from_spec(sp);sys.modules[sp.name]=a;sp.loader.exec_module(a);v=a.reader
CASES=('seed_26093210','seed_26093220','seed_26093221')
def main():
    started=time.perf_counter();freeze=a.js(BASE/'prepared_freeze.json');manifest=v.manifest_check(BASE/'input_manifest.csv',expected=freeze['manifest_sha256']);pre=a.js(BASE/'independent_prepared_review.json')
    assert pre['status']=='INDEPENDENT_FRESH_TARGET_PREPARED_PASS' and manifest['entries_checked']==246
    records=[];hashes={}
    for case in CASES:
        d=BASE/case;lp=d/'lp';files=sorted(p for p in lp.iterdir() if p.is_file());hashes.update({str(p.relative_to(ROOT)):v.sha(p) for p in files})
        m=v.load_model(lp);names=a.labels(lp/'row_metadata.csv.gz');cert=a.js(lp/'dual_certificate.json');result=a.js(lp/'result.json')
        assert result['verdict']=='CERTIFIED_INFEASIBLE_EXPANDED_MODEL' and result['model_status']=='Infeasible' and result['time_limit_s']==30
        for f in ('matrix.npz','bounds.npz','integrality.npz','row_metadata.csv.gz'):assert v.sha(lp/f)==v.sha(d/f)
        v.ray_bindings(lp,cert,BASE/'input_manifest.csv',())
        assert cert['orientation']==1 and cert['candidate']=='projected_to_row_sign_cone' and result['certificate_verification']==cert['verification']
        raw=v.read_npz(lp/'raw_solver_ray.npz',('multipliers',))['multipliers'];assert raw.dtype=='<f8' and raw.shape==(m.rows,) and all(math.isfinite(x) for x in raw.values)
        parsed={}
        for item in cert['multipliers']:
            r=item['row'];assert type(r)is int and r not in parsed and 0<=r<m.rows
            value=float.fromhex(item['value_hex']);assert value!=0 and math.isfinite(value);parsed[r]=Q(value)
        expected={};bad=[]
        for r,value in enumerate(raw.values):
            if not value:continue
            if math.isfinite(m.row_lower[r] if value>0 else m.row_upper[r]):expected[r]=Q(value)
            else:bad.append(r)
        assert expected==parsed and len(bad)==cert['verification']['inadmissible_raw_entries']
        rejected=False
        try:v.check_ray(m,{r:Q(x) for r,x in enumerate(raw.values) if x},Q.from_float(1e-5))
        except v.InvalidInput:rejected=True
        assert rejected==bool(bad)
        exact=v.check_ray(m,parsed,Q.from_float(1e-5));assert exact['status']=='CERTIFIED_EXPANDED_INFEASIBLE' and all(v.archived_ray_comparison(cert,exact).values())
        assert exact['row_multiplier_nonzeros']==cert['verification']['row_multiplier_nonzeros'] and exact['combined_column_nonzeros']==cert['verification']['combined_column_nonzeros']
        with (lp/'sparse_multipliers.csv').open(newline='') as f:csvrows=list(csv.DictReader(f))
        assert len(csvrows)==len(parsed) and {int(x['row']):Q(float(x['multiplier'])) for x in csvrows}==parsed
        families=dict(Counter(names[r]['family'] for r in parsed));assert families==cert['support']['row_family_counts'] and families.get('fossil_energy_cap')==1 and not any('mean' in k for k in families)
        cap=next(r for r in parsed if names[r]['family']=='fossil_energy_cap');p=next(x for x in pre['cases'] if x['case']==case)
        assert m.row_lower[cap]==-math.inf and m.row_upper[cap]==p['budget_MWh'] and parsed[cap]<0
        assert a.row(m,cap)=={t*41+j:1. for t in range(168) for j in range(23)}
        assert p['point_check']['static_expanded_pass'] and not p['point_check']['full_expanded_pass']
        positive=[x for x in pre['cases'] if x['week']==p['week'] and x['role']!='ordinary'];assert len(positive)==2 and all(x['point_check']['full_expanded_pass'] for x in positive)
        log=(lp/'solver.log').read_text();assert log.count('Running HiGHS')==1 and 'Infeasible' in log and not (d/'mip').exists()
        records.append(dict(case=case,week=p['week'],budget_MWh=p['budget_MWh'],status=exact['status'],exact=exact,raw_ray_rejected=rejected,projected_bad_entries=len(bad),source_and_target_lp_hashes_equal=True,family_support=families,solver_seconds=result['elapsed_s'],controls_inherited_from_frozen_independent_exact_positive_gate=True))
        print(json.dumps({'case':case,'expanded_gap':exact['expanded_separation_gap']['float'],'status':exact['status']}),flush=True)
    assert all(v.sha(ROOT/p)==sha for p,sha in hashes.items());v.manifest_check(BASE/'input_manifest.csv',expected=freeze['manifest_sha256'])
    OUT.mkdir(exist_ok=True);out=dict(status='INDEPENDENT_THREE_FRESH_NEGATIVE_CERTIFICATES_PASS',optimizer_calls=0,complete_target_stage_claim=False,manifest_sha256=freeze['manifest_sha256'],frozen_bindings=246,all_hashes_unchanged=True,cases=records,replayed_output_hashes=hashes,review_source_sha256=v.sha(Path(__file__)),elapsed_seconds=time.perf_counter()-started,scope='Three completed exact negative rays and their preverified reference/control bindings; remaining fourth ordinary outcome and final call accounting await stage completion.')
    with (OUT/'negative_certificates.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2,allow_nan=False);f.write('\n')
if __name__=='__main__':main()
