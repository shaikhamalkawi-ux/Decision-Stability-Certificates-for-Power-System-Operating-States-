"""Read-only stdlib exact replay of six frozen fresh January energy models."""
import csv,importlib.util,json,math,sys,time
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'results/research8h/fresh_january_energy';PARENT=ROOT/'results/research8h/fresh_january_weeks'
sp=importlib.util.spec_from_file_location('energy_gate_helpers',ROOT/'results/research8h/hour_of_day_uncapped_prepared_review.py');h=importlib.util.module_from_spec(sp);sys.modules[sp.name]=h;sp.loader.exec_module(h);a=h.a;v=h.v
SOURCE='0ad4536f7b9be7d681a4e164eb8546cc1755ddccb2b49e90887e92d4f08b250d';PROTOCOL='56ad8786aedeabab42374bb91d923c6453c4f468414a19bea54d352a3e9e8bca';MANIFEST='44b382d30a30b8485beda0cf080d22cd991b55a9f37491939f633d147bc14f2a'
SCHEDULE={2:('seed_26093210','seed_26093211'),3:('seed_26093220','seed_26093221')}
def bits(x,y):return len(x)==len(y) and all(p==q and (not isinstance(p,float) or p.hex()==q.hex()) for p,q in zip(x,y))
def same(m,p):
    assert m.rows==p.rows and m.cols==p.cols and m.indices==p.indices and m.indptr==p.indptr and bits(m.data,p.data)
    assert all(bits(getattr(m,k),getattr(p,k)) for k in ('lower','upper','row_lower','row_upper'))
def uncapped(m,p,names,pnames,keep,budget,c):
    caps=[r for r,x in enumerate(pnames) if x['family']=='fossil_energy_cap'];assert len(caps)==1;cap=caps[0]
    assert keep==tuple(r for r in range(p.rows) if r!=cap) and m.rows==p.rows-1==34680 and m.cols==p.cols==23016
    assert bits(m.lower,p.lower) and bits(m.upper,p.upper)
    assert p.row_lower[cap]==-math.inf and p.row_upper[cap]==budget
    assert a.row(p,cap)=={j:x for j,x in enumerate(c) if x}
    for r,old in enumerate(keep):
        assert a.row(m,r)==a.row(p,old) and m.row_lower[r]==p.row_lower[old] and m.row_upper[r]==p.row_upper[old]
        assert all(names[r][key]==pnames[old][key] for key in ('family','hour_0based','uid'))
        assert int(names[r]['row'])==r
        if 'source_row_0based' in names[r]:assert int(names[r]['source_row_0based'])==old
    assert not any('mean' in x['family'] or x['family']=='fossil_energy_cap' for x in names)
    return cap

def main():
    start=time.perf_counter();freeze=a.js(OUT/'prepared_freeze.json');assert not (OUT/'execution_started.json').exists()
    assert freeze['source_sha256']==SOURCE==v.sha(ROOT/'src/research8h_fresh_january_energy.py')
    assert freeze['protocol_sha256']==PROTOCOL==v.sha(ROOT/'docs/research8h/FRESH_JANUARY_ENERGY_PROTOCOL.md')
    assert freeze['manifest_sha256']==MANIFEST and freeze['optimization_calls']==0 and freeze['new_identity_MIP_calls']==0
    assert freeze['target_cases']==[c for cases in SCHEDULE.values() for c in cases] and freeze['identity_cases']==['week_2_identity','week_3_identity']
    assert [freeze[k] for k in ('max_identity_LP_calls','max_target_MIP_calls','max_target_LP_calls','MIP_seconds','LP_seconds','MIP_guard_seconds','LP_guard_seconds','phase_seconds')]==[2,4,4,600,60,605,65,3600]
    assert freeze['phase_starts_before_entry_validation'] and freeze['cutoff_utc']=='2026-09-27T04:00:00+00:00'
    manifest=v.manifest_check(OUT/'input_manifest.csv',expected=MANIFEST);assert manifest['entries_checked']==378
    for stage in ('references','targets'):
        old=a.js(PARENT/stage/'prepared_freeze.json');v.manifest_check(PARENT/stage/'input_manifest.csv',expected=old['manifest_sha256'])
    final=a.js(ROOT/'results/research8h/fresh_targets_postrun_review/final_ledger.json');assert final['status']=='INDEPENDENT_FRESH_TARGET_FINAL_REVIEW_PASS' and final['ordinary_denominator']==4
    assert all(v.sha(ROOT/p)==sha for p,sha in final['replayed_output_hashes'].items())
    prepared=a.js(OUT/'prepared_cases.json');assert [x['case'] for x in prepared]==[c for w,cases in SCHEDULE.items() for c in (f'week_{w}_identity',*cases)]
    refs={x['week']:x for x in a.js(OUT/'reference_bindings.json')};records=[]
    native_names=('pmin','pmax','net','rows','nodal','source_hour')
    native_path=Path(freeze['source_v3']);gens=list((native_path/'raw').rglob('gen.csv'));assert len(gens)==1
    with gens[0].open(newline='',encoding='utf-8-sig') as f:roster=list(csv.DictReader(f))
    fuel={x['GEN UID']:x['Fuel'] for x in roster}
    for week,cases in SCHEDULE.items():
        prior=a.js(ROOT/f'results/research8h/fresh_reference_postrun_review/week_{week}.json');assert prior['status']=='INDEPENDENT_EXPANDED_BINARY_REFERENCE_PASS'
        assert all(v.sha(ROOT/p)==sha for p,sha in prior['replayed_files_sha256'].items())
        refdir=PARENT/'references'/f'week_{week}';reference=v.load_model(refdir);native=v.read_npz(refdir/'native_inputs.npz',native_names)
        reference_energy=h.jq(prior['exact_fossil_MWh']);scaled=reference_energy*Q(101,100);budget=-(-scaled.numerator//scaled.denominator)
        assert budget==refs[week]['source_cap_MWh']==a.js(PARENT/'targets'/f'week_{week}_cap.json')['budget_MWh']
        assert reference_energy==h.jq(refs[week]['reference_upper_MWh']) and refs[week]['reference_native_no_cap_check']['pass']
        assert refs[week]['reference_point_sha256']==v.sha(refdir/'recovered_vector.npz')
        for case in (f'week_{week}_identity',*cases):
            identity=case.endswith('_identity');d=OUT/case;m=v.load_model(d);names=a.labels(d/'row_metadata.csv.gz');meta=a.js(d/'model_metadata.json')
            capped=PARENT/'targets'/case;p=v.load_model(capped);pnames=a.labels(capped/'row_metadata.csv.gz')
            original=a.array(d/'original_integrality.npz','integrality');solve=a.array(d/'integrality.npz','integrality')
            assert original==a.array(capped/'integrality.npz','integrality')==(0,)*6888+(1,)*12096+(0,)*4032
            assert solve==(0,)*6888+(1,)*4032+(0,)*12096
            projection=a.projection_audit(m,original,solve,meta,names)
            assert meta['original_binary_columns']==12096 and meta['binary_columns']==4032 and meta['energy_cap_constraints']==0 and meta['individual_mean_constraints']==0 and 'budget_MWh' not in meta
            fossil=[j for j,s in enumerate(meta['unit_names']) if fuel[s] in ('Coal','Oil','NG')]
            assert len(fossil)==23 and [meta['unit_names'][j] for j in fossil]==meta['fossil_units'] and meta['unit_names'][23]=='121_NUCLEAR_1' and 23 not in fossil
            cost=a.array(d/'objective.npz','objective');expected={t*41+j:1. for t in range(168) for j in fossil};assert cost==tuple(expected.get(j,0.) for j in range(m.cols))
            reduced_keep=tuple(r for r,x in enumerate(pnames) if x['family']!='fossil_energy_cap')
            cap=uncapped(m,p,names,pnames,reduced_keep,budget,cost)
            retained=a.array(d/'retained_parent_rows.npz','rows');assert retained==(tuple(range(m.rows)) if identity else reduced_keep)
            parent=refdir if identity else capped
            assert v.sha(d/'native_inputs.npz')==v.sha(parent/'native_inputs.npz')
            inputs=v.read_npz(d/'native_inputs.npz',native_names);order=inputs['source_hour'].values
            assert sorted(order)==list(range(168)) and order[:48]==tuple(range(48)) and order[120:]==tuple(range(120,168)) and all(t%24==s%24 for t,s in enumerate(order))
            for key in ('pmin','pmax','net','rows','nodal'):
                x,y=native[key],inputs[key];width=math.prod(x.shape[1:]);assert x.shape==y.shape and x.dtype==y.dtype
                assert bits(y.values,tuple(z for t in order for z in x.values[t*width:(t+1)*width]))
            bound=h.objective_lower(m,cost,(0.,)*m.rows);saved=a.js(d/'zero_dual_baseline.json');assert all(h.jq(bound[k])==h.jq(saved[k]) for k in bound)
            record=dict(case=case,week=week,removed_cap_row_0based=cap,source_cap_MWh=budget,projection=projection,zero_dual_bound=bound,exact_cap_only_removal=True,native_packages_unchanged=True)
            if identity:
                same(m,reference);assert cost==a.array(refdir/'objective.npz','objective') and order==tuple(range(168))
                assert v.sha(d/'reference_upper_vector.npz')==v.sha(refdir/'recovered_vector.npz')
                point=a.array(d/'reference_upper_vector.npz','vector');check=a.point_audit(m,point,original,names)
                assert check['full_expanded_pass'] and not check['full_strict_pass']
                e=sum((Q(c)*Q(x) for c,x in zip(cost,point)),Q(0));assert e==reference_energy
                record.update(exact_same_uncapped_reference=True,upper_MWh=v.rat(e),point_check=check)
            else:
                assert v.sha(d/'permutation.csv')==v.sha(capped/'permutation.csv')
                with (d/'permutation.csv').open(newline='') as f:permutation=list(csv.DictReader(f))
                assert tuple(int(x['source_hour_0based']) for x in permutation)==order and tuple(int(x['native_row_0based']) for x in permutation)==inputs['rows'].values
                assert meta['removed_source_cap_MWh']==budget
            assert not (d/'mip').exists() and not (d/'lp').exists();records.append(record)
            print(json.dumps(dict(case=case,gate='PASS',cap=budget,identity=identity)),flush=True)
    assert not (OUT/'execution_started.json').exists();v.manifest_check(OUT/'input_manifest.csv',expected=MANIFEST)
    report=dict(status='INDEPENDENT_FRESH_ENERGY_PREPARED_PASS',optimizer_calls=0,manifest_sha256=MANIFEST,frozen_bindings=378,all_hashes_match_before_after=True,execution_marker_absent=True,source_sha256=SOURCE,protocol_sha256=PROTOCOL,cases=records,review_source_sha256=v.sha(Path(__file__)),elapsed_seconds=time.perf_counter()-start,scope='Independent stdlib decoding, exact matrix/bound equality, native-package transport and original-mask dyadic binary point replay. Raw native-calendar reconstruction inherited through prior independently reviewed and rehashed reference archives; no new native assembler execution.')
    reviewdir=ROOT/'results/research8h/fresh_energy_review';reviewdir.mkdir(exist_ok=True)
    with (reviewdir/'prepared.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps(dict(status=report['status'],bindings=378,seconds=report['elapsed_seconds'])),flush=True)
if __name__=='__main__':main()
