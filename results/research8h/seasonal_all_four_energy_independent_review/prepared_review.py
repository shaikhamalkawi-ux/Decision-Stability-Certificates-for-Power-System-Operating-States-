"""Independent stdlib-only prepared gate for all four seasonal energy targets."""
import argparse,csv,hashlib,importlib.util,json,math,sys,time
from datetime import datetime,timedelta
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'results/research8h/seasonal_all_four_energy';PARENT=ROOT/'results/research8h/seasonal_cap_continuation';REFS=ROOT/'results/research8h/seasonal_reference_continuation'
for rel,sha in [('src/research8h_standalone_verify.py','708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'),('results/research8h/hour_of_day_uncapped_prepared_review.py','ec6c5c129dfb71c9cd7f04643dcf8b81ce806f73652edc8da44080f63daf067f'),('results/research8h/seasonal_cap_prepared_review.py','3de77675460d103298ac17dc7851144362a3ecb87a1e77ec80f522622259433a')]:
    assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==sha
sp=importlib.util.spec_from_file_location('seasonal_energy_review_helpers',ROOT/'results/research8h/hour_of_day_uncapped_prepared_review.py');h=importlib.util.module_from_spec(sp);sys.modules[sp.name]=h;sp.loader.exec_module(h);a=h.a;v=h.v
SOURCE='9b7f7118e232e7c252fadce7dc8c9b45e0f9cbeb1b0d861cc21fcdd0e184541d';PROTOCOL='c8b12b01f3cc0a709d80d7c535e51a20bd8ae211b06841e0586ea549416ad6cf'
SCHEDULE={4:('seed_26093400','seed_26093401'),10:('seed_26094000','seed_26094001')};STARTS={4:2184,10:6576};CAPS={4:43131,10:125172}
PREP={'reference':'cc7ff078ea7e99ac177b3d22be3208cf454ca0726015e4a10c3b65329630758b','target':'d5ae06005d333ee20b6ef5a466c72fd7c5530462ada923fc83a07e26b14e8055'}
POST={'reference':'a0c316f13ca4e632a128e66d0f8abbe4df2f916dca4c5a734634e2a4fd514934','target':'76d3e9648d6b0c7ca8c5a9bc40fb5dcc0efa4f6d52b7056c3e3486d0bf19a279'}
def bits(x,y):return len(x)==len(y) and all(p==q and (not isinstance(p,float) or p.hex()==q.hex()) for p,q in zip(x,y))
def same(m,p):
    assert (m.rows,m.cols,m.indices,m.indptr)==(p.rows,p.cols,p.indices,p.indptr) and bits(m.data,p.data)
    assert all(bits(getattr(m,k),getattr(p,k)) for k in ('lower','upper','row_lower','row_upper'))
def csvrows(p):
    with p.open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def uncapped(m,p,names,pnames,keep,budget,c):
    caps=[r for r,x in enumerate(pnames) if x['family']=='fossil_energy_cap'];assert len(caps)==1;cap=caps[0]
    assert keep==tuple(r for r in range(p.rows) if r!=cap) and m.rows==p.rows-1==34680 and m.cols==p.cols==23016
    assert bits(m.lower,p.lower) and bits(m.upper,p.upper)
    assert p.row_lower[cap]==-math.inf and p.row_upper[cap]==budget and a.row(p,cap)=={j:x for j,x in enumerate(c) if x}
    for r,old in enumerate(keep):
        assert a.row(m,r)==a.row(p,old) and bits((m.row_lower[r],m.row_upper[r]),(p.row_lower[old],p.row_upper[old]))
        assert all(names[r][key]==pnames[old][key] for key in ('family','hour_0based','uid')) and int(names[r]['row'])==r
        if 'source_row_0based' in names[r]:assert int(names[r]['source_row_0based'])==old
    assert not any('mean' in x['family'] or x['family']=='fossil_energy_cap' for x in names)
    return cap

def main(expected):
    start=time.perf_counter();freeze=a.js(OUT/'prepared_freeze.json');assert not (OUT/'execution_started.json').exists()
    assert freeze['source_sha256']==SOURCE==v.sha(ROOT/'src/research8h_seasonal_all_four_energy.py')
    assert freeze['protocol_sha256']==PROTOCOL==v.sha(ROOT/'docs/research8h/SEASONAL_ALL_FOUR_ENERGY_PROTOCOL.md')
    assert freeze['manifest_sha256']==expected and freeze['optimization_calls']==0 and freeze['new_identity_MIP_calls']==0
    assert freeze['target_cases']==[c for cases in SCHEDULE.values() for c in cases] and freeze['identity_cases']==['month_04_identity','month_10_identity']
    assert [freeze[k] for k in ('max_identity_LP_calls','max_target_MIP_calls','max_target_LP_calls','MIP_seconds','LP_seconds','MIP_guard_seconds','LP_guard_seconds','phase_seconds')]==[2,4,4,300,60,305,65,2100]
    assert freeze['phase_starts_before_entry_validation'] and freeze['cutoff_utc']=='2026-09-27T04:00:00+00:00'
    manifest=v.manifest_check(OUT/'input_manifest.csv',expected=expected)
    assert manifest['entries_checked']==freeze['bound_files']
    inventory={str(Path(x['path']).resolve()):x for x in csvrows(OUT/'input_manifest.csv')}
    coverage=[]
    for role,d in [('reference',REFS),('target',PARENT)]:
        assert v.sha(d/'post_run_artifact_manifest.csv')==POST[role]
        v.manifest_check(d/'input_manifest.csv',expected=PREP[role])
        for row in csvrows(d/'post_run_artifact_manifest.csv'):
            path=d/row['path'];assert path.stat().st_size==int(row['bytes']) and v.sha(path)==row['sha256'];assert str(path.resolve()) in inventory
        coverage.append({'role':role,'prepared_manifest':PREP[role],'closed_manifest':POST[role]})
    oldprep=a.js(PARENT/'independent_prepared_review.json');oldpost=a.js(PARENT/'independent_postrun_review.json')
    assert v.sha(PARENT/'independent_prepared_review.json')=='fce0cdef3977caa3244d2f43b78def3bcd8e498d4942d3b3ccfb48bf335b35d0'
    assert v.sha(PARENT/'independent_postrun_review.json')=='14a72a7adb98509d73a6c59ad3303d892dc91d28ea08323fe31d3c87c3cadd0c'
    assert oldprep['status']=='INDEPENDENT_PREPARED_REVIEW_PASS' and oldpost['status']=='INDEPENDENT_POSTRUN_REVIEW_PASS'
    historical=a.js(PARENT/'outcomes.json');assert [x['case'] for x in historical]==freeze['target_cases'] and all(x['verdict']=='UNKNOWN' for x in historical)
    assert not a.js(PARENT/'completion.json')['augmented_at_least_two_weeks']
    oldrefs={x['month']:x for x in oldprep['cases'] if x['kind']=='identity'}
    prepared=a.js(OUT/'prepared_cases.json');assert [x['case'] for x in prepared]==[c for month,cases in SCHEDULE.items() for c in (f'month_{month:02d}_identity',*cases)]
    refs={x['month']:x for x in a.js(OUT/'reference_bindings.json')};records=[]
    native_path=Path(freeze['source_v3']);gens=list((native_path/'raw').rglob('gen.csv'));assert len(gens)==1
    roster=csvrows(gens[0]);fuel={x['GEN UID']:x['Fuel'] for x in roster};calendars={}
    calendar_names=('Load/DAY_AHEAD_regional_Load.csv','PV/DAY_AHEAD_pv.csv','WIND/DAY_AHEAD_wind.csv','Hydro/DAY_AHEAD_hydro.csv','RTPV/DAY_AHEAD_rtpv.csv')
    for filename in calendar_names:
        p=gens[0].parent/'timeseries_data_files'/filename;assert str(p.resolve()) in inventory
        selected={}
        with p.open(newline='',encoding='utf-8-sig') as f:
            for n,row in enumerate(csv.DictReader(f)):
                if any(lo<=n<lo+168 for lo in STARTS.values()):selected[n]=tuple(int(row[k]) for k in ('Year','Month','Day','Period'))
                if n>=STARTS[10]+167:break
        assert len(selected)==336
        for month,lo in STARTS.items():
            for t in range(168):
                dt=datetime(2020,month,1)+timedelta(hours=t);assert selected[lo+t]==(dt.year,dt.month,dt.day,dt.hour+1)
        calendars[filename]={'rows_checked':336,'sha256':v.sha(p)}
    for month,cases in SCHEDULE.items():
        refdir=REFS/f'month_{month:02d}';reference=v.load_model(refdir)
        keys=('pmin','pmax','net','rows','nodal');native=v.read_npz(refdir/'native_inputs.npz',keys)
        assert native['rows'].values==tuple(range(STARTS[month],STARTS[month]+168))
        for hp in (refdir/'source_hours.csv',native_path/'processed'/f'month_{month:02d}_first_week_hourly_summary.csv'):
            assert str(hp.resolve()) in inventory
            hours=csvrows(hp);assert len(hours)==168
            for t,row in enumerate(hours):
                assert int(row['row'])==STARTS[month]+t and datetime.fromisoformat(row['timestamp'])==datetime(2020,month,1)+timedelta(hours=t)
        reference_energy=h.jq(oldrefs[month]['exact_energy']);scaled=reference_energy*Q(101,100);budget=-(-scaled.numerator//scaled.denominator)
        assert budget==CAPS[month]==refs[month]['source_cap_MWh']
        assert reference_energy==h.jq(refs[month]['reference_upper_MWh']) and refs[month]['reference_native_no_cap_check']['pass']
        assert refs[month]['reference_point_sha256']==v.sha(refdir/'recovered_vector.npz')
        for case in (f'month_{month:02d}_identity',*cases):
            identity=case.endswith('_identity');d=OUT/case;m=v.load_model(d);names=a.labels(d/'row_metadata.csv.gz');meta=a.js(d/'model_metadata.json')
            capped=PARENT/case;p=v.load_model(capped);pnames=a.labels(capped/'row_metadata.csv.gz')
            original=a.array(d/'original_integrality.npz','integrality');solve=a.array(d/'integrality.npz','integrality')
            assert original==a.array(capped/'integrality.npz','integrality')==(0,)*6888+(1,)*12096+(0,)*4032
            assert solve==(0,)*6888+(1,)*4032+(0,)*12096
            projection=a.projection_audit(m,original,solve,meta,names)
            assert meta['original_binary_columns']==12096 and meta['binary_columns']==4032 and meta['energy_cap_constraints']==0 and meta['individual_mean_constraints']==0 and 'budget_MWh' not in meta
            fossil=[j for j,s in enumerate(meta['unit_names']) if fuel[s] in ('Coal','Oil','NG')]
            assert len(fossil)==23 and [meta['unit_names'][j] for j in fossil]==meta['fossil_units'] and meta['unit_names'][23]=='121_NUCLEAR_1' and 23 not in fossil
            cost=a.array(d/'objective.npz','objective');co={t*41+j:1. for t in range(168) for j in fossil};assert cost==tuple(co.get(j,0.) for j in range(m.cols))
            keep=tuple(r for r,x in enumerate(pnames) if x['family']!='fossil_energy_cap');cap=uncapped(m,p,names,pnames,keep,budget,cost)
            retained=a.array(d/'retained_parent_rows.npz','rows');assert retained==(tuple(range(m.rows)) if identity else keep)
            parent=refdir if identity else capped;assert v.sha(d/'native_inputs.npz')==v.sha(parent/'native_inputs.npz')
            inputs=v.read_npz(d/'native_inputs.npz',keys if identity else (*keys,'source_hour'))
            order=tuple(range(168)) if identity else inputs['source_hour'].values
            assert sorted(order)==list(range(168)) and order[:48]==tuple(range(48)) and order[120:]==tuple(range(120,168))
            for key in keys:
                x,y=native[key],inputs[key];width=math.prod(x.shape[1:]);assert x.shape==y.shape and x.dtype==y.dtype
                assert bits(y.values,tuple(z for t in order for z in x.values[t*width:(t+1)*width]))
            bound=h.objective_lower(m,cost,(0.,)*m.rows);saved=a.js(d/'zero_dual_baseline.json');assert all(h.jq(bound[k])==h.jq(saved[k]) for k in bound)
            record=dict(case=case,month=month,removed_cap_row_0based=cap,source_cap_MWh=budget,projection=projection,zero_dual_bound=bound,exact_cap_only_removal=True,native_packages_unchanged=True,permutation_scope='Phi0 unrestricted interior; no HOD condition')
            if identity:
                same(m,reference);assert original==a.array(refdir/'original_integrality.npz','integrality') and solve==a.array(refdir/'integrality.npz','integrality')
                assert cost==a.array(refdir/'objective.npz','objective') and v.sha(d/'reference_upper_vector.npz')==v.sha(refdir/'recovered_vector.npz')
                point=a.array(d/'reference_upper_vector.npz','vector');check=a.point_audit(m,point,original,names);assert check['full_expanded_pass']
                energy=sum((Q(c)*Q(x) for c,x in zip(cost,point)),Q(0));assert energy==reference_energy
                record.update(exact_same_uncapped_reference=True,upper_MWh=v.rat(energy),point_check=check)
            else:
                assert v.sha(d/'permutation.csv')==v.sha(capped/'permutation.csv');permutation=csvrows(d/'permutation.csv')
                assert tuple(int(x['new_hour_0based']) for x in permutation)==tuple(range(168))
                assert tuple(int(x['source_hour_0based']) for x in permutation)==order and tuple(int(x['source_native_row']) for x in permutation)==inputs['rows'].values
                assert meta['removed_source_cap_MWh']==budget
            assert not (d/'mip').exists() and not (d/'lp').exists();records.append(record)
            print(json.dumps(dict(case=case,gate='PASS',cap=budget,identity=identity)),flush=True)
    assert not (OUT/'execution_started.json').exists();v.manifest_check(OUT/'input_manifest.csv',expected=expected)
    helpers=[Path(__file__),ROOT/'results/research8h/hour_of_day_uncapped_prepared_review.py',ROOT/'results/research8h/seasonal_cap_prepared_review.py',ROOT/'src/research8h_standalone_verify.py']
    report=dict(status='INDEPENDENT_SEASONAL_ALL_FOUR_ENERGY_PREPARED_PASS',optimizer_calls=0,producer_source_imports=0,manifest_sha256=expected,frozen_bindings=manifest['entries_checked'],all_hashes_match_before_after=True,execution_marker_absent=True,source_sha256=SOURCE,protocol_sha256=PROTOCOL,cases=records,source_closed_manifests=coverage,five_calendars=calendars,reviewer_dependencies={str(p.relative_to(ROOT)):v.sha(p) for p in helpers},elapsed_seconds=time.perf_counter()-start,scope='Independent stdlib decoding, exact cap-only model equality/objectives, original masks/projection, complete native package transport, five raw native calendars and two exact dyadic binary reference points. Numerical native physical assembly is inherited through unchanged independently reviewed parent inputs; no producer/optimizer import.')
    with (Path(__file__).parent/'prepared_review.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps(dict(status=report['status'],bindings=report['frozen_bindings'],seconds=report['elapsed_seconds'])),flush=True)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--manifest',required=True);args=parser.parse_args();main(args.manifest)
