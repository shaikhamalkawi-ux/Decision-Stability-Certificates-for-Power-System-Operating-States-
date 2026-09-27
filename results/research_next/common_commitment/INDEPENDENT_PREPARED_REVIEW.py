"""Read-only exact saved-row transport audit. No producer/model-builder/solver import."""
import csv
from datetime import datetime, timezone
from fractions import Fraction
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import struct
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
ARM = ROOT / 'results/research_next/common_commitment'
PRE = ARM / 'prepared'
OUTPUT = ARM / 'INDEPENDENT_PREPARED_REVIEW.json'
PINS = {
    'prepared/prepared_freeze.json': '4f21891d7d1f1793dd92e5b830edf5b5cf62474e5521d788c9aec17929ea9a59',
    'prepared/input_manifest.json': '8ff99b1f4450ac15e91b26a261a85c98d574bbbdac3f7fe149efd9fd07204a5c',
}
SOURCE = '039af59750b4c165d877b9878ac14af02a202700b46739ba96a8914075ae3284'
PROTOCOL = '08838becbd0d679f6131421c566534f19c93f535e7baa3b4b00d30b985ccab21'
KERNEL_SHA = '708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'
GEN_SHA = '988466f29132b73739de60c9204dd4a2a9ceb0adf572e5966c086611272f4068'
PAYLOADS = ('matrix.npz','bounds.npz','integrality.npz','model_metadata.json','native_inputs.npz','permutation.csv','row_metadata.csv.gz')
OLD = (ROOT/'results/research8h/hour_of_day/january_identity', ROOT/'results/research8h/day_blocks/days_321')
HIST = (ROOT/'results/research8h/hour_of_day/input_manifest.csv', ROOT/'results/research8h/day_blocks/input_manifest.csv')

def require(test, message):
    if not test:
        raise AssertionError(message)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def same_float(a,b):
    return struct.pack('<d',a) == struct.pack('<d',b)

def csv_read(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def rows(path):
    with gzip.open(path, 'rt', encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def main():
    start = time.monotonic()
    require(not OUTPUT.exists(), 'Fresh independent report only')
    require(not (ARM/'run01').exists(), 'Producer execution must remain absent')
    own_sha = sha(__file__)
    for rel,digest in PINS.items():
        require(sha(ARM/rel)==digest, 'Trusted transport digest: '+rel)
    freeze=read(PRE/'prepared_freeze.json')
    require(freeze['source_sha256']==SOURCE and freeze['protocol_sha256']==PROTOCOL, 'Frozen source/protocol')
    require(freeze['optimizer_calls']==0 and freeze['bindings']==48, 'Freeze stage/count')
    items=read(PRE/'input_manifest.json')['files']
    require(len(items)==48 and len({r['path'].casefold() for r in items})==48, 'Manifest uniqueness')
    by_path={str(Path(r['path']).resolve()).casefold():r for r in items}
    def all_bindings():
        for r in items:
            p=Path(r['path'])
            require(p.stat().st_size==r['bytes'] and sha(p)==r['sha256'], 'Changed input '+str(p))
    all_bindings()
    require(sha(ROOT/'src/researchnext_common_commitment.py')==SOURCE, 'Source pin')
    require(sha(ROOT/'docs/research_next/COMMON_COMMITMENT_PROTOCOL.md')==PROTOCOL, 'Protocol pin')
    prepared_files={str(p.resolve()).casefold() for p in PRE.rglob('*') if p.is_file()}
    expected={p for p in by_path if p.startswith(str(PRE.resolve()).casefold()+'\\')}
    expected |= {str((PRE/name).resolve()).casefold() for name in ('input_manifest.json','prepared_freeze.json')}
    require(prepared_files==expected, 'Complete prepared inventory')
    kernel_path=ROOT/'src/research8h_standalone_verify.py'
    require(sha(kernel_path)==KERNEL_SHA, 'Reader pin before import')
    spec=importlib.util.spec_from_file_location('common_independent_npz_reader',kernel_path)
    v=importlib.util.module_from_spec(spec);sys.modules[spec.name]=v;spec.loader.exec_module(v)
    worlds=[PRE/'identity',PRE/'days_321']
    original=[]; labels=[]; metas=[]; arrays=[]
    for world,old,historical in zip(worlds,OLD,HIST):
        hist={str(Path(r['path']).resolve()).casefold():r for r in csv_read(historical)}
        for name in PAYLOADS:
            p=old/name;r=hist[str(p.resolve()).casefold()]
            require(sha(p)==r['sha256'] and p.stat().st_size==int(r['bytes']), 'Historical binding')
            require((world/name).read_bytes()==p.read_bytes(), 'Original byte copy '+name)
        original.append(v.load_model(world));metas.append(read(world/'model_metadata.json'))
        labels.append(rows(world/'row_metadata.csv.gz'))
        arrays.append(v.read_npz(world/'native_inputs.npz',('pmin','pmax','net','rows','source_hour','nodal')))
    joint=v.load_model(PRE/'joint')
    mask_expected=tuple(int(6888<=j<18984) for j in range(23016))
    masks=[]
    for folder,m in zip(worlds+[PRE/'joint'],original+[joint]):
        ar=v.read_npz(folder/'integrality.npz',('integrality',))['integrality']
        masks.append(tuple(v.vector(ar,('|u1',),m.cols,'binary mask')))
    require(masks[:2]==[mask_expected,mask_expected] and masks[2]==mask_expected+(0,)*10920, 'All original state bits shared exactly')
    require(all((m.rows,m.cols,len(m.data))==(34681,23016,145588) for m in original), 'Original shapes/nnz')
    require((joint.rows,joint.cols,len(joint.data))==(69362,33936,291176), 'Joint shapes/nnz')
    maps=read(PRE/'joint/column_maps.json')
    require(maps['worlds']==['identity','days_321'], 'World order')
    require(maps['shared_original_columns']==list(range(6888,18984)), 'Saved shared list')
    m0,m1=maps['original_to_joint']
    expected_m1=[j if 6888<=j<18984 else (23016+j if j<6888 else 29904+j-18984) for j in range(23016)]
    require(m0==list(range(23016)) and m1==expected_m1, 'Explicit complete coordinate transport')
    private=set(range(6888))|set(range(18984,23016))
    require(set(m0[j] for j in private).isdisjoint(m1[j] for j in private), 'Private P/theta separation')
    require(set(m0)&set(m1)==set(range(6888,18984)), 'Only state columns shared')
    origins=read(PRE/'joint/row_origins.json')['origins']
    require(origins==[[w,r] for w in range(2) for r in range(34681)], 'Complete original row origins')
    # Compare saved CSR rows through inverse coordinate maps; do not construct a new joint matrix.
    row_count=0; coefficient_count=0
    for wi,(model,mapping) in enumerate(zip(original,(m0,m1))):
        inv={j:i for i,j in enumerate(mapping)}
        for r in range(model.rows):
            jr=wi*34681+r
            require(same_float(model.row_lower[r],joint.row_lower[jr]) and same_float(model.row_upper[r],joint.row_upper[jr]), 'Row endpoint transport')
            require(joint.indptr[jr+1]-joint.indptr[jr]==model.indptr[r+1]-model.indptr[r], 'Row sparsity')
            saved={inv[joint.indices[e]]:struct.pack('<d',joint.data[e]) for e in range(joint.indptr[jr],joint.indptr[jr+1])}
            source={model.indices[e]:struct.pack('<d',model.data[e]) for e in range(model.indptr[r],model.indptr[r+1])}
            require(saved==source, 'Full row coefficient/column transport')
            row_count+=1;coefficient_count+=len(saved)
    a,b=original;tau=Fraction.from_float(1e-5)
    for j in range(joint.cols):
        if j<23016:
            lo=max(a.lower[j],b.lower[j]) if mask_expected[j] else a.lower[j]
            hi=min(a.upper[j],b.upper[j]) if mask_expected[j] else a.upper[j]
        else:
            old=(j-23016 if j<29904 else j-29904+18984)
            lo,hi=b.lower[old],b.upper[old]
        require(math.isfinite(lo) and math.isfinite(hi) and lo<=hi, 'Finite compatible box')
        require(same_float(joint.lower[j],lo) and same_float(joint.upper[j],hi), 'Exact column boxes')
        if j<23016 and mask_expected[j]:
            require(same_float(a.lower[j],b.lower[j]) and same_float(a.upper[j],b.upper[j]), 'Identical shared scientific boxes')
            require(Fraction(lo)-tau==max(Fraction(a.lower[j])-tau,Fraction(b.lower[j])-tau), 'Expanded lower intersection')
            require(Fraction(hi)+tau==min(Fraction(a.upper[j])+tau,Fraction(b.upper[j])+tau), 'Expanded upper intersection')
    require(sha(PRE/'gen.csv')==GEN_SHA, 'Raw GEN immutable')
    gen_rows=csv_read(PRE/'gen.csv');gen={r['GEN UID']:r for r in gen_rows}
    require(len(gen)==len(gen_rows), 'Unique raw units')
    reports=[]
    for wi,(folder,meta,model,labs,arr) in enumerate(zip(worlds,metas,original,labels,arrays)):
        require(meta['offsets']=={'P':0,'U':6888,'Y':10920,'Z':14952,'theta':18984}, 'Offsets')
        require((meta['hours'],meta['units'],meta['thermal_units'],meta['buses'],meta['branches'])==(168,41,24,24,38), 'Native sizes')
        require(meta['column_order']=='P,U,Y,Z,theta; each block hour-major', 'Column semantics')
        require(meta['budget_MWh']==23195 and meta['individual_mean_constraints']==0 and meta['objective']=='zero feasibility objective', 'Service scope')
        require(meta['bus_ids']==list(range(101,125)), 'Bus roster')
        require(len(labs)==34681 and [int(r['row']) for r in labs]==list(range(34681)), 'Row labels complete')
        require(arr['pmin'].shape==arr['pmax'].shape==(168,41) and arr['nodal'].shape==(168,24), 'Native shapes')
        require(all(arr[k].shape==(168,) for k in ('net','rows','source_hour')), 'Native time coordinates')
        for k in ('pmin','pmax','net','nodal'):
            require(arr[k].dtype=='<f8' and all(math.isfinite(x) for x in arr[k].values), 'Finite native data')
        names=meta['unit_names'];thermals=meta['thermal_unit_names'];fs=meta['fossil_units']
        require(len(names)==len(set(names))==41 and len(thermals)==24 and len(fs)==23, 'Unit multiplicities')
        require(thermals==names[:24] and fs==[n for n in thermals if gen[n]['Fuel']!='Nuclear'], '23 fossil roster excludes nuclear')
        specs=read(folder/'native_spec.json');require(len(specs)==41, 'Native spec length')
        for s,n in zip(specs,names):
            g=gen[n];rpm=float(g['Ramp Rate MW/Min']);hour=rpm*60.0;q=Fraction(hour);diff=q-60*Fraction(rpm)
            expected_spec={'uid':n,'bus':int(g['Bus ID']),'category':g['Category'],'thermal':n in thermals,
                'minimum_up':math.ceil(float(g['Min Up Time Hr'])),'minimum_down':math.ceil(float(g['Min Down Time Hr'])),
                'per_minute_binary64_hex':rpm.hex(),'hourly_binary64_hex':hour.hex(),
                'hourly_rational':{'numerator':str(q.numerator),'denominator':str(q.denominator)},
                'difference_from_exact_times_60':{'numerator':str(diff.numerator),'denominator':str(diff.denominator)}}
            require(s==expected_spec,'Native GEN-derived spec')
        families={}
        caps=[]
        for ri,l in enumerate(labs):
            f=l['family'];families[f]=families.get(f,0)+1;t=int(l['hour_0based'])
            if f=='fossil_energy_cap':
                caps.append(ri)
                entries={model.indices[e]:model.data[e] for e in range(model.indptr[ri],model.indptr[ri+1])}
                require(entries=={41*t+j:1.0 for t in range(168) for j,n in enumerate(names) if n in fs}, 'Cap coefficients')
                require(model.row_lower[ri]==-math.inf and model.row_upper[ri]==23195, 'Cap endpoints')
            elif f in ('aggregate_balance','nodal_balance'):
                rhs=arr['net'].values[t] if f=='aggregate_balance' else arr['nodal'].values[24*t+meta['bus_ids'].index(int(l['uid']))]
                require(same_float(model.row_lower[ri],rhs) and same_float(model.row_upper[ri],rhs), 'Native balance identity')
        require(len(caps)==1 and families['aggregate_balance']==168 and families['nodal_balance']==4032, 'Complete service/network constraints')
        reports.append({'world':folder.name,'rows':model.rows,'columns':model.cols,'nnz':len(model.data),'families':families,
            'cap_row':caps[0],'cap_MWh':23195,'fossil_units':len(fs),'native_48h_units':[s['uid'] for s in specs if max(s['minimum_up'],s['minimum_down'])==48]})
    require(all(metas[0][k]==metas[1][k] for k in ('offsets','unit_names','thermal_unit_names','bus_ids','fossil_units')), 'World coordinate labels')
    perm=list(range(48))+list(range(96,120))+list(range(72,96))+list(range(48,72))+list(range(120,168))
    for wi,p in enumerate((list(range(168)),perm)):
        records=csv_read(worlds[wi]/'permutation.csv')
        require([int(r['new_hour_0based']) for r in records]==list(range(168)), 'Destination hours')
        require([int(r['source_hour_0based']) for r in records]==p, 'Exact inherited day321 permutation')
        require(tuple(p)==arrays[wi]['source_hour'].values, 'Native source-hour identity')
        require(tuple(int(r['source_native_row']) for r in records)==arrays[wi]['rows'].values, 'Native row provenance')
        for k,width in (('pmin',41),('pmax',41),('net',1),('nodal',24)):
            for t,source_t in enumerate(p):
                require(all(same_float(arrays[wi][k].values[t*width+j],arrays[0][k].values[source_t*width+j]) for j in range(width)), 'Complete hourly-package permutation')
    plan=read(PRE/'plan.json')
    require(plan['worlds']==['identity','days_321'] and plan['sequence']==['mip','lp'], 'Fixed two-call order')
    require(plan['options']=={'mip':{'time_limit':600.0,'threads':1,'random_seed':0,'presolve':'on','mip_rel_gap':1e-8},'lp':{'time_limit':60.0,'threads':1,'random_seed':0,'presolve':'off','solver':'simplex'}}, 'Frozen exact options')
    require(plan['phase_seconds']==1200 and plan['solver_calls']==plan['warm_starts']==plan['retries']==0, 'Prospective budgets')
    require(Fraction(int(plan['tau']['numerator']),int(plan['tau']['denominator']))==tau, 'Exact acceptance tau')
    require(plan['numeric_proposal_bounds']=='nominal' and plan['acceptance_bounds']=='exact uniform tau expansion', 'Proposal/acceptance separation')
    observations=read(ROOT/'results/research_next/whole_day_observation_preflight/run01/outcomes.json')
    selected=[r for r in observations['comparisons'] if r['week']==1 and r['role']=='target' and r['primary_plus_hindex_outcome']=='EQUAL']
    require(len(selected)==1 and selected[0]['day_order']==[3,2,1], 'Declared posthoc selection')
    assembly=read(PRE/'assembly_checks.json')
    require(assembly['posthoc_selected_collision']==selected[0] and assembly['optimizer_calls']==0, 'Selection linkage')
    require(not any(name in sys.modules for name in ('numpy','scipy','highspy','researchnext_common_commitment')), 'No scientific producer/optimizer imported')
    all_bindings()
    for rel,digest in PINS.items():
        require(sha(ARM/rel)==digest, 'Transport unchanged at close')
    require(sha(__file__)==own_sha and not (ARM/'run01').exists(), 'Source unchanged and producer remains unstarted')
    report={'status':'PASS_INDEPENDENT_PREPARED_REVIEW','utc':datetime.now(timezone.utc).isoformat(),
        'review_source_sha256':own_sha,'producer_source_sha256':SOURCE,'protocol_sha256':PROTOCOL,
        'trusted_transport':PINS,'bindings_checked_twice':48,'saved_rows_independently_checked':row_count,
        'saved_coefficients_independently_checked':coefficient_count,'joint_columns':33936,'shared_binary_columns':12096,
        'private_continuous_columns_per_world':10920,'historical_payload_byte_copies':14,'original_worlds':reports,
        'full_native_package_permutation':True,'posthoc_selection':True,'plan':plan,
        'zero_optimizer_calls':True,'zero_model_generation':True,'zero_old_witness_or_ray_replay':True,
        'producer_run01_absent_at_entry_and_exit':True,'kernel_sha256':KERNEL_SHA,
        'scope':'Saved matrix/box/mask/metadata/native-copy/mapping audit only; no feasibility result or native model reassembly.',
        'elapsed_seconds':time.monotonic()-start}
    with OUTPUT.open('x',encoding='utf-8') as f:
        json.dump(report,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({'status':report['status'],'report_sha256':sha(OUTPUT),'elapsed_seconds':report['elapsed_seconds']}))

if __name__=='__main__':
    main()
