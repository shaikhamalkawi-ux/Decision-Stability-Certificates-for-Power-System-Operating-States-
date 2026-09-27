"""Independent solver-free preflight for the two uncapped HOD archives."""
import csv,importlib.util,json,math,sys,time
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'results/research8h/hour_of_day_uncapped';PARENT=ROOT/'results/research8h/hour_of_day';IDENTITY=ROOT/'results/research8h/energy_lp_refinement'
sp=importlib.util.spec_from_file_location('uncapped_hod_helpers',ROOT/'results/research8h/seasonal_cap_prepared_review.py');a=importlib.util.module_from_spec(sp);sys.modules[sp.name]=a;sp.loader.exec_module(a);v=a.reader
CASES=('seed_26093200','seed_26093201');SOURCE='529f640192f437b03e08efb297ca9d97e50b2028fd59f86683ceec2468222867';PROTOCOL='52a37e5b49e43dbc8f7d9c7900f5d14e25b6dc5c59f3007bba30f1bd05c79b91'
def jq(x):return Q(int(x['numerator']),int(x['denominator']))
def objective_lower(m,c,d):
    assert len(c)==m.cols and len(d)==m.rows and all(math.isfinite(x) for x in (*c,*d))
    q=list(map(Q,c));beta=norm=Q(0);tau=Q.from_float(1e-5)
    for r,x in enumerate(d):
        if not x:continue
        selected=m.row_lower[r] if x>0 else m.row_upper[r]
        assert math.isfinite(selected)
        multiplier=Q(x);beta+=multiplier*Q(selected);norm+=abs(multiplier)
        for e in range(m.indptr[r],m.indptr[r+1]):q[m.indices[e]]-=multiplier*Q(m.data[e])
    box=sum((x*Q(m.lower[j] if x>=0 else m.upper[j]) for j,x in enumerate(q)),Q(0))
    widened=sum((x*(Q(m.lower[j])-tau if x>=0 else Q(m.upper[j])+tau) for j,x in enumerate(q)),Q(0))+beta-tau*norm
    nominal=beta+box;expanded=nominal-tau*(norm+sum(map(abs,q),Q(0)))
    assert expanded==widened
    return dict(nominal_lower_bound_MWh=v.rat(nominal),expanded_lower_bound_MWh=v.rat(expanded),row_term=v.rat(beta),finite_box_term=v.rat(box),row_dual_l1=v.rat(norm),stationarity_residual_l1=v.rat(sum(map(abs,q),Q(0))))

def compare_subset(m,p,names,pnames,retained):
    cap=[i for i,x in enumerate(pnames) if x['family']=='fossil_energy_cap'];assert len(cap)==1
    assert retained==tuple(i for i in range(p.rows) if i!=cap[0]) and m.rows+1==p.rows and m.cols==p.cols==23016
    assert m.lower==p.lower and m.upper==p.upper
    for r,old in enumerate(retained):
        assert a.row(m,r)==a.row(p,old) and m.row_lower[r]==p.row_lower[old] and m.row_upper[r]==p.row_upper[old]
        assert names[r]['family']==pnames[old]['family'] and names[r]['hour_0based']==pnames[old]['hour_0based'] and names[r]['uid']==pnames[old]['uid']
        assert int(names[r]['row'])==r
        if 'source_row_0based' in names[r]:assert int(names[r]['source_row_0based'])==old
    assert p.row_lower[cap[0]]==-math.inf and p.row_upper[cap[0]]==23195
    assert not any('mean' in x['family'] or x['family']=='fossil_energy_cap' for x in names)
    return cap[0]

def main():
    start=time.perf_counter();freeze=a.js(OUT/'prepared_freeze.json')
    assert freeze['cases']==list(CASES) and freeze['optimization_calls']==0 and freeze['new_identity_solves']==0 and freeze['MIPs_before_LPs']
    assert freeze['source_sha256']==SOURCE==v.sha(ROOT/'src/research8h_hour_of_day_uncapped.py')
    assert freeze['protocol_sha256']==PROTOCOL==v.sha(ROOT/'docs/research8h/HOUR_OF_DAY_UNCAPPED_PROTOCOL.md')
    assert not (OUT/'execution_started.json').exists()
    manifest=v.manifest_check(OUT/'input_manifest.csv',expected=freeze['manifest_sha256'])
    assert a.js(PARENT/'independent_postrun_review.json')['status']=='INDEPENDENT_HOD_POSTRUN_PASS'
    prior=a.js(IDENTITY/'independent_review.json');assert prior['status']=='PASS_COMPLETE'
    records=[]
    for c in CASES:
        d=OUT/c;pdir=PARENT/c;m=v.load_model(d);p=v.load_model(pdir);names=a.labels(d/'row_metadata.csv.gz');pnames=a.labels(pdir/'row_metadata.csv.gz')
        keep=a.array(d/'retained_parent_rows.npz','rows');cap=compare_subset(m,p,names,pnames,keep)
        for f in ('native_inputs.npz','permutation.csv'):assert v.sha(d/f)==v.sha(pdir/f)
        original=a.array(d/'original_integrality.npz','integrality');solve=a.array(d/'integrality.npz','integrality')
        assert original==a.array(pdir/'integrality.npz','integrality')
        meta=a.js(d/'model_metadata.json');projection=a.projection_audit(m,original,solve,meta,names)
        assert meta['original_binary_columns']==12096 and meta['binary_columns']==4032 and meta['energy_cap_constraints']==0 and 'budget_MWh' not in meta
        cost=a.array(d/'objective.npz','objective');fossil=[meta['unit_names'].index(s) for s in meta['fossil_units']]
        assert len(fossil)==23 and '121_NUCLEAR_1' not in meta['fossil_units']
        expected={t*41+j:1. for t in range(168) for j in fossil};assert a.row(p,cap)==expected
        assert cost==tuple(expected.get(j,0.) for j in range(m.cols))
        report=objective_lower(m,cost,(0.,)*m.rows);saved=a.js(d/'zero_dual_baseline.json')
        assert all(jq(report[k])==jq(saved[k]) for k in report)
        assert not (d/'lp').exists() and not (d/'mip').exists()
        records.append(dict(case=c,exact_single_cap_deletion=True,removed_cap_row=cap,native_permutation_bytes_unchanged=True,objective_exactly_equals_deleted_cap_row=True,projection=projection,zero_dual_expanded_lower_MWh=report['expanded_lower_bound_MWh']))
    d=IDENTITY/'january_identity';pdir=PARENT/'january_identity';m=v.load_model(d);p=v.load_model(pdir);names=a.labels(d/'row_metadata.csv.gz');pnames=a.labels(pdir/'row_metadata.csv.gz')
    keep=tuple(i for i,x in enumerate(pnames) if x['family']!='fossil_energy_cap');cap=compare_subset(m,p,names,pnames,keep)
    original=a.array(d/'original_integrality.npz','integrality');assert original==a.array(pdir/'integrality.npz','integrality')
    cost=a.array(d/'objective.npz','objective');assert {j:x for j,x in enumerate(cost) if x}==a.row(p,cap)
    dual=a.array(d/'projected_row_dual.npz','row_dual');report=objective_lower(m,cost,dual);saved=a.js(d/'exact_lower_bound.json')
    assert all(jq(report[k])==jq(saved[k]) for k in report)
    binding=a.js(OUT/'reused_identity_bounds.json');assert jq(binding['lower_MWh'])==jq(report['expanded_lower_bound_MWh'])
    point=a.array(pdir/'constructive_vector.npz','vector');check=a.point_audit(m,point,original,names)
    assert check['full_expanded_pass'] and not check['full_strict_pass']
    energy=sum((Q(x)*Q(y) for x,y in zip(cost,point)),Q(0));assert energy==jq(binding['reference_upper_MWh'])
    assert binding['native_no_cap_check']['pass'] and binding['matrix_objective_bounds_original_integrality_equal_after_only_cap_deletion']
    assert jq(prior['cases'][0]['unchanged_binary_upper_MWh'])==energy
    assert not (OUT/'execution_started.json').exists()
    v.manifest_check(OUT/'input_manifest.csv',expected=freeze['manifest_sha256'])
    out=dict(status='INDEPENDENT_HOD_UNCAPPED_PREPARED_PASS',optimizer_calls=0,manifest_sha256=freeze['manifest_sha256'],frozen_bindings=manifest['entries_checked'],all_hashes_match_before_after=True,execution_marker_absent=True,cases=records,identity=dict(exact_same_uncapped_model=True,dual_expanded_lower_MWh=report['expanded_lower_bound_MWh'],upper_MWh=v.rat(energy),exact_expanded_binary_point=True,strict_point=False,original_binary_coordinates=12096,native_check='Stored producer replay passes; archived native input binding inherited from independent HOD review'),review_source_sha256=v.sha(Path(__file__)),reader_sha256=v.sha(ROOT/'src/research8h_standalone_verify.py'),helper_sha256=v.sha(ROOT/'results/research8h/seasonal_cap_prepared_review.py'),elapsed_seconds=time.perf_counter()-start)
    with (OUT/'independent_prepared_review.json').open('x',encoding='utf-8') as f:json.dump(out,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({'status':out['status'],'bindings':out['frozen_bindings'],'seconds':out['elapsed_seconds']}),flush=True)
if __name__=='__main__':main()
