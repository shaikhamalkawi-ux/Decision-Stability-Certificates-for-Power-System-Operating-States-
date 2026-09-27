"""Independent completed fresh-reference point replay; no optimizer imports/calls."""
import argparse,importlib.util,json,struct,sys,time
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'results/research8h/fresh_january_weeks/references';OUT=ROOT/'results/research8h/fresh_reference_postrun_review'
sp=importlib.util.spec_from_file_location('fresh_postrun_helpers',ROOT/'results/research8h/seasonal_cap_prepared_review.py');a=importlib.util.module_from_spec(sp);sys.modules[sp.name]=a;sp.loader.exec_module(a);v=a.reader

def main(week):
    started=time.perf_counter();d=BASE/f'week_{week}';result=a.js(d/'result.json');freeze=a.js(BASE/'prepared_freeze.json')
    v.manifest_check(BASE/'input_manifest.csv',expected=freeze['manifest_sha256'])
    assert result['week']==week and result['optimization_calls']==1
    files=[p for p in d.iterdir() if p.is_file()];hashes={str(p.relative_to(ROOT)):v.sha(p) for p in files}
    out=dict(week=week,optimizer_calls=0,producer_verdict=result['verdict'],model_status=result.get('model_status'),reported_solver_seconds=result.get('elapsed_s'),exact_optimality_claim=False,review_source_sha256=v.sha(Path(__file__)))
    if result['verdict']=='VERIFIED_REFERENCE_EXPANDED_MODEL':
        m=v.load_model(d);names=a.labels(d/'row_metadata.csv.gz');mask=a.array(d/'integrality.npz','integrality')
        assert mask==(0,)*6888+(1,)*12096+(0,)*4032
        raw=a.array(d/'raw_vector.npz','vector');point=a.array(d/'recovered_vector.npz','vector');tau=Q.from_float(1e-5)
        assert len(raw)==len(point)==23016
        for lo,hi in ((0,6888),(18984,23016)):
            assert struct.pack('<'+str(hi-lo)+'d',*raw[lo:hi])==struct.pack('<'+str(hi-lo)+'d',*point[lo:hi])
        u=point[6888:10920];assert all(x in (0,1) for x in u)
        assert all(abs(Q(raw[6888+j])-Q(x))<=tau for j,x in enumerate(u))
        for t in range(168):
            for q in range(24):
                delta=0 if t==0 else u[t*24+q]-u[(t-1)*24+q]
                assert point[10920+t*24+q]==max(0,delta) and point[14952+t*24+q]==max(0,-delta)
        exact=a.point_audit(m,point,mask,names);saved=a.js(d/'exact_point_check.json')
        assert exact['full_expanded_pass'] and exact['full_strict_pass']==saved['strict_pass']==result['exact_strict_pass']
        for k in ('maximum_column_violation','maximum_row_violation'):
            assert Q(int(exact[k]['numerator']),int(exact[k]['denominator']))==Q(int(saved[k]['numerator']),int(saved[k]['denominator']))
        c=a.array(d/'objective.npz','objective');energy=sum((Q(x)*Q(y) for x,y in zip(c,point)),Q(0));stored=result['fossil_energy']
        assert energy==Q(int(stored['numerator']),int(stored['denominator']))
        assert result['native_no_cap_pass'] and a.js(d/'native_no_cap_check.json')['pass']
        assert result['raw_matrix_check']['pass'] and result['recovered_matrix_check']['pass']
        out.update(status='INDEPENDENT_EXPANDED_BINARY_REFERENCE_PASS',original_binary_coordinates=12096,P_theta_bytes_preserved=True,U_recovery_exactly_checked=True,YZ_canonical_exact=True,exact_point=exact,exact_fossil_MWh=v.rat(energy),strict_pass=exact['full_strict_pass'],native_scope='Stored producer native check passes; native data reproduced independently at prepared gate, no repeated native assembler call')
    else:
        assert result['verdict']=='UNKNOWN_NO_REFERENCE';out.update(status='NO_ACCEPTED_REFERENCE_RETAINED',no_feasibility_claim=True)
    assert all(v.sha(ROOT/p)==h for p,h in hashes.items())
    v.manifest_check(BASE/'input_manifest.csv',expected=freeze['manifest_sha256'])
    out.update(replayed_files_sha256=hashes,all_input_and_result_hashes_unchanged=True,manifest_sha256=freeze['manifest_sha256'],elapsed_seconds=time.perf_counter()-started)
    OUT.mkdir(exist_ok=True)
    with (OUT/f'week_{week}.json').open('x',encoding='utf-8') as f:json.dump(out,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({'week':week,'status':out['status'],'seconds':out['elapsed_seconds']}),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--week',type=int,choices=(2,3),required=True);main(p.parse_args().week)
