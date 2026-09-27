"""Six fixed HOD ray-transfer candidates; stdlib only, zero optimizers."""
from __future__ import annotations
import argparse,csv,gzip,importlib.util,json,math,struct,sys,time,zipfile
from collections import Counter
from datetime import datetime,timezone
from fractions import Fraction as Q
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
_spec=importlib.util.spec_from_file_location("fixed_ray_archive_verifier",ROOT/"src/research8h_standalone_verify.py")
v=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=v;_spec.loader.exec_module(v)
OUT=ROOT/'results/research8h/hod_fixed_ray_transfer'
PROTOCOL=ROOT/'docs/research8h/HOD_FIXED_RAY_TRANSFER_PROTOCOL.md'
HOD=ROOT/'results/research8h/hour_of_day'
OLD=ROOT/'results/research8h/seasonal_rule_transfer/seed_26093101/locality48'
OLD_PARENT=ROOT/'results/research8h/seasonal_transfer/seed_26093101'
CASES=('seed_26093200','seed_26093201')
RULES=('two_cc','locality48')
TEMPORAL={'transition','exclusive_transition','minimum_up','minimum_down'}
DWELL={'minimum_up','minimum_down'}
STATIC={'aggregate_balance','thermal_upper','thermal_lower','nodal_balance','branch_flow','fossil_energy_cap'}
TWO_CC={'107_CC_1','118_CC_1'}
TAU=Q.from_float(1e-5)
MODEL_FILES=('matrix.npz','bounds.npz','integrality.npz','model_metadata.json','row_metadata.csv.gz')

def read(p):return v.json_read(p)
def save(p,x):
    with p.open('x',encoding='utf-8') as f:json.dump(x,f,indent=2,allow_nan=False);f.write('\n')
def labels(p):
    with gzip.open(p,'rt',newline='') as f:return list(csv.DictReader(f))
def write_csv(p,rows,fields):
    with p.open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def arr(p,key):return v.read_npz(p,(key,))[key].values
def key(x):return x['family'],int(x['hour_0based']),x['uid']
def row(m,r):return {m.indices[e]:m.data[e] for e in range(m.indptr[r],m.indptr[r+1]) if m.data[e]}
def npy(dtype,shape,values):
    fmt={'<f8':'d','<i8':'q','|u1':'B','|S3':'3s'}[dtype]
    assert math.prod(shape)==len(values)
    header=repr(dict(descr=dtype,fortran_order=False,shape=shape)).encode('latin1')
    header+=b' '*((-10-len(header)-1)%64)+b'\n'
    payload=struct.pack('<3s',*values) if dtype=='|S3' else struct.pack('<'+str(len(values))+fmt,*values)
    return b'\x93NUMPY\x01\x00'+struct.pack('<H',len(header))+header+payload
def npz(p,members):
    with zipfile.ZipFile(p,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for name,(dtype,shape,values) in members.items():
            item=zipfile.ZipInfo(name+'.npy',(1980,1,1,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(item,npy(dtype,shape,values))
def archive(d,m,lab,mask,meta,keep):
    d.mkdir(parents=True,exist_ok=False)
    npz(d/'matrix.npz',dict(data=('<f8',(len(m.data),),m.data),indices=('<i8',(len(m.indices),),m.indices),indptr=('<i8',(len(m.indptr),),m.indptr),shape=('<i8',(2,),(m.rows,m.cols)),format=('|S3',(),(b'csr',))))
    npz(d/'bounds.npz',{n:('<f8',(len(x),),x) for n,x in dict(column_lower=m.lower,column_upper=m.upper,row_lower=m.row_lower,row_upper=m.row_upper).items()})
    npz(d/'integrality.npz',{'integrality':('|u1',(len(mask),),mask)})
    npz(d/'retained_parent_rows.npz',{'rows':('<i8',(len(keep),),keep)})
    # Plain CSV and deterministic gzip header; no timestamp-dependent model content.
    import io
    text=io.StringIO(newline='');w=csv.DictWriter(text,fieldnames=('row','family','hour_0based','uid','original_row'));w.writeheader();w.writerows(lab)
    with (d/'row_metadata.csv.gz').open('xb') as f:f.write(gzip.compress(text.getvalue().encode(),mtime=0))
    save(d/'model_metadata.json',meta)
    assert v.load_model(d)==m and arr(d/'integrality.npz','integrality')==mask and arr(d/'retained_parent_rows.npz','rows')==keep

def full(d):
    m=v.load_model(d);lab=labels(d/'row_metadata.csv.gz');meta=read(d/'model_metadata.json')
    mask_array=v.read_npz(d/'integrality.npz',('integrality',))['integrality']
    assert mask_array.shape==(23016,) and mask_array.dtype in ('|u1','<i4','<i8')
    mask=mask_array.values;assert all(type(x) is int and x in (0,1) for x in mask)
    assert (m.rows,m.cols)==(34681,23016) and len(lab)==m.rows
    assert meta['offsets']==dict(P=0,U=6888,Y=10920,Z=14952,theta=18984)
    assert (meta['hours'],meta['units'],meta['thermal_units'],meta['buses'])==(168,41,24,24)
    assert meta['individual_mean_constraints']==0 and meta['budget_MWh']==23195
    assert mask==(0,)*6888+(1,)*12096+(0,)*4032
    assert set(x['family'] for x in lab)==STATIC|TEMPORAL
    assert len({key(x) for x in lab})==len(lab)
    assert all(int(x['row'])==r for r,x in enumerate(lab))
    for r in range(m.rows):
        idx=m.indices[m.indptr[r]:m.indptr[r+1]];assert all(x<y for x,y in zip(idx,idx[1:]))
    fossil=[meta['unit_names'].index(u) for u in meta['fossil_units']]
    assert len(fossil)==len(set(fossil))==23 and '121_NUCLEAR_1' not in meta['fossil_units']
    caps=[r for r,x in enumerate(lab) if x['family']=='fossil_energy_cap'];assert len(caps)==1
    assert row(m,caps[0])=={t*41+j:1. for t in range(168) for j in fossil}
    assert m.row_lower[caps[0]]==-math.inf and m.row_upper[caps[0]]==23195
    return m,lab,meta,mask

def columns_match(a,b):
    for k in ('unit_names','thermal_unit_names','bus_ids','offsets','hours','units','thermal_units','buses','column_order','fossil_units'):assert a[k]==b[k],k

def subset(m,lab,rule):
    keep=[]
    for r,x in enumerate(lab):
        f=x['family'];yes=True
        if rule=='two_cc':yes=f not in TEMPORAL or x['uid'] in TWO_CC
        elif f in DWELL:
            hours=[]
            for j in row(m,r):
                assert 6888<=j<18984
                start=6888 if j<10920 else 10920 if j<14952 else 14952
                hours.append((j-start)//24)
            assert hours;yes=min(hours)>=60 and max(hours)<=107
        if yes:keep.append(r)
    keep=tuple(keep);assert len(keep)==(19985 if rule=='two_cc' else 28689)
    assert {r for r,x in enumerate(lab) if x['family'] in STATIC}<=set(keep)
    data=[];indices=[];ptr=[0]
    for r in keep:
        data.extend(m.data[m.indptr[r]:m.indptr[r+1]]);indices.extend(m.indices[m.indptr[r]:m.indptr[r+1]]);ptr.append(len(data))
    sm=v.Model(len(keep),m.cols,tuple(data),tuple(indices),tuple(ptr),m.lower,m.upper,tuple(m.row_lower[r] for r in keep),tuple(m.row_upper[r] for r in keep));v.validate_model(sm)
    sl=[dict(row=i,family=lab[r]['family'],hour_0based=int(lab[r]['hour_0based']),uid=lab[r]['uid'],original_row=r) for i,r in enumerate(keep)]
    if rule=='locality48':
        counts=Counter(x['family'] for x in sl);assert counts['minimum_up']==1023 and counts['minimum_down']==1001
    return sm,sl,keep

def multipliers(cert):
    out={}
    for x in cert['multipliers']:
        r=x['row'];assert type(r) is int and r not in out
        d=float.fromhex(x['value_hex']);assert math.isfinite(d) and d!=0
        out[r]=Q(d)
    return out

def source_certificate(d):
    cert=read(d/'dual_certificate.json');v.ray_bindings(d,cert,None,())
    ray=multipliers(cert);model=v.load_model(d)
    report=v.check_ray(model,ray,TAU)
    assert report['expanded_pass'] and all(v.archived_ray_comparison(cert,report).values())
    return cert,ray,report

def manifest(records):
    for x in records:v.checked_hash(x['path'],x['sha256'],x['bytes'])

def source_paths():
    files=[Path(__file__),PROTOCOL,ROOT/'src/research8h_standalone_verify.py',ROOT/'docs/research8h/TRANSFER_PROTOCOL.md',ROOT/'docs/research8h/SEASONAL_RULE_TRANSFER_PROTOCOL.md',ROOT/'src/research8h_seasonal_rule_transfer.py',ROOT/'src/research8h_locality.py',HOD/'input_manifest.csv',HOD/'independent_postrun_review.json',ROOT/'results/research8h/seasonal_rule_transfer/input_manifest.csv',ROOT/'results/research8h/seasonal_rule_transfer/independent_review.json']
    for d in [OLD_PARENT,*[HOD/c for c in ('january_identity',*CASES,'seed_26100200')]]:files.extend(d/f for f in MODEL_FILES)
    for c in ('january_identity','seed_26100200'):files.append(HOD/c/'constructive_vector.npz')
    files.extend(OLD/f for f in ('matrix.npz','bounds.npz','row_metadata.csv.gz','retained_parent_rows.npz','dual_certificate.json','raw_solver_ray.npz'))
    for c in CASES:files.extend(HOD/c/'lp'/f for f in ('matrix.npz','bounds.npz','row_metadata.csv.gz','dual_certificate.json','raw_solver_ray.npz'))
    return list(dict.fromkeys(p.resolve() for p in files))

def prepare():
    OUT.mkdir(parents=True,exist_ok=False)
    paths=source_paths();frozen=[dict(path=str(p),bytes=p.stat().st_size,sha256=v.sha(p)) for p in paths]
    save(OUT/'source_manifest.json',frozen);manifest(frozen)
    prior=read(HOD/'independent_postrun_review.json');assert prior['status']=='INDEPENDENT_HOD_POSTRUN_PASS'
    parent_manifest=v.manifest_check(HOD/'input_manifest.csv',expected=prior['manifest_sha256'])
    old_manifest=v.manifest_check(ROOT/'results/research8h/seasonal_rule_transfer/input_manifest.csv')
    base,bl,bmeta,bmask=full(OLD_PARENT);oldmodel=v.load_model(OLD);oldlabels=labels(OLD/'row_metadata.csv.gz')
    oldsubset,expected_labels,oldkeep=subset(base,bl,'locality48')
    assert oldmodel==oldsubset and arr(OLD/'retained_parent_rows.npz','rows')==oldkeep
    assert all(key(x)==key(y) and int(x['original_row'])==y['original_row'] and int(x['row'])==i for i,(x,y) in enumerate(zip(oldlabels,expected_labels)))
    assert len(oldlabels)==len(expected_labels)
    _,oldray,oldcheck=source_certificate(OLD)
    save(OUT/'source_proof_validation.json',{'old_january_locality48':oldcheck,'optimizer_calls':0,'scope':'Original-source validation, not one of six new target candidates'})
    # Positive controls inherit exact expanded feasibility from a bound, completed audit.
    controls=[]
    for c in ('january_identity','seed_26100200'):
        audit=next(x for x in prior['positive_controls'] if x['case']==c)
        assert audit['full_expanded_pass'] and audit['original_binary_coordinates']==12096 and not audit['strict_pass']
        m,lab,meta,mask=full(HOD/c);columns_match(bmeta,meta)
        for rule in RULES:
            sm,sl,keep=subset(m,lab,rule)
            assert sm.lower==m.lower and sm.upper==m.upper
            # subset() copies actual rows/bounds, so the bound full witness is preserved.
            records=[dict(subset_row=i,parent_row=r) for i,r in enumerate(keep)]
            write_csv(OUT/f'control_{c}_{rule}_rows.csv',records,('subset_row','parent_row'))
            controls.append(dict(case=c,rule=rule,expanded_binary_feasibility_inherited=True,strict_positive_claim=False,retained_rows=len(keep),original_point_sha256=v.sha(HOD/c/'constructive_vector.npz'),source_matrix_sha256=v.sha(HOD/c/'matrix.npz'),source_bounds_sha256=v.sha(HOD/c/'bounds.npz'),all_columns_and_boxes_unchanged=True))
    save(OUT/'positive_control_inheritance.json',dict(controls=controls,parent_manifest=parent_manifest,prior_rule_manifest=old_manifest,full_point_replays=0,optimizer_calls=0))
    candidates=[]
    for c in CASES:
        parent=HOD/c;m,lab,meta,mask=full(parent);columns_match(bmeta,meta)
        lookup={key(x):r for r,x in enumerate(lab)}
        fullcert,fullray,fullcheck=source_certificate(parent/'lp')
        assert v.load_model(parent/'lp')==m
        save(OUT/f'{c}_source_proof_validation.json',fullcheck)
        models={}
        for rule in RULES:
            sm,sl,keep=subset(m,lab,rule);d=OUT/'models'/c/rule
            archive(d,sm,sl,mask,{**meta,'rows':sm.rows,'nonzeros':len(sm.data),'restriction_rule':rule},keep)
            models[rule]=(d,sm,sl,keep,{r:i for i,r in enumerate(keep)})
        for name,rule,source_dir,source_ray in [('old_january_locality','locality48',OLD,oldray),('own_full_to_two_cc','two_cc',parent/'lp',fullray),('own_full_to_locality48','locality48',parent/'lp',fullray)]:
            d,sm,sl,keep,target_index=models[rule];mapped={};coordinates=[];dropped=[]
            for source_r,value in source_ray.items():
                source_parent_r=oldkeep[source_r] if name=='old_january_locality' else source_r
                source_label=bl[source_parent_r] if name=='old_january_locality' else lab[source_parent_r]
                target_parent_r=lookup[key(source_label)]
                source_m=oldmodel if name=='old_january_locality' else m
                assert row(source_m,source_r)==row(m,target_parent_r)
                item=dict(source_ray_row=source_r,source_parent_row=source_parent_r,target_parent_row=target_parent_r,family=source_label['family'],hour_0based=int(source_label['hour_0based']),uid=source_label['uid'],value_hex=float(value).hex())
                if target_parent_r in target_index:
                    target_r=target_index[target_parent_r];assert target_r not in mapped
                    mapped[target_r]=value;coordinates.append({**item,'target_subset_row':target_r})
                else:
                    assert name!='old_january_locality';dropped.append(item)
            if name=='old_january_locality':assert len(mapped)==len(oldray)
            identifier=c+'__'+name;candidate_dir=OUT/'candidates'/identifier;candidate_dir.mkdir(parents=True)
            write_csv(candidate_dir/'coordinate_mapping.csv',coordinates,('source_ray_row','source_parent_row','target_parent_row','family','hour_0based','uid','value_hex','target_subset_row'))
            save(candidate_dir/'dropped_source_entries.json',dropped)
            obj=dict(id=identifier,case=c,rule=rule,kind=name,model_directory=str(d.relative_to(OUT)),source_certificate=str((source_dir/'dual_certificate.json').resolve()),source_certificate_sha256=v.sha(source_dir/'dual_certificate.json'),source_multiplier_count=len(source_ray),dropped_multiplier_count=len(dropped),multipliers=[dict(row=r,value_hex=float(x).hex()) for r,x in sorted(mapped.items())],model_artifacts={f:v.sha(d/f) for f in ('matrix.npz','bounds.npz')},row_metadata_sha256=v.sha(d/'row_metadata.csv.gz'),column_mapping='Identity columns: exact P/U/Y/Z/theta offsets, hours, generator and bus ordering checked',sign_repair_or_rescaling=False)
            save(candidate_dir/'candidate.json',obj);candidates.append(identifier)
    assert len(candidates)==6;save(OUT/'candidate_order.json',candidates)
    manifest(frozen)
    all_paths=list(dict.fromkeys([*paths,*sorted(p for p in OUT.rglob('*') if p.is_file())]))
    records=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=v.sha(p)) for p in all_paths]
    save(OUT/'input_manifest.json',records)
    save(OUT/'prepared_freeze.json',dict(utc=datetime.now(timezone.utc).isoformat(),source_sha256=v.sha(Path(__file__)),protocol_sha256=v.sha(PROTOCOL),manifest_sha256=v.sha(OUT/'input_manifest.json'),bindings=len(records),target_candidates=6,target_checks_started=0,optimizer_calls=0,candidate_order=candidates))
    print(json.dumps({'status':'PREPARED_SIX_CANDIDATES_NO_TARGET_CHECKS','bindings':len(records),'manifest_sha256':v.sha(OUT/'input_manifest.json')}),flush=True)

def check_prepared():
    started=time.perf_counter();freeze=read(OUT/'prepared_freeze.json')
    assert freeze['source_sha256']==v.sha(Path(__file__)) and freeze['protocol_sha256']==v.sha(PROTOCOL)
    assert freeze['manifest_sha256']==v.sha(OUT/'input_manifest.json');records=read(OUT/'input_manifest.json');manifest(records)
    save(OUT/'checking_started.json',dict(utc=datetime.now(timezone.utc).isoformat(),optimizer_calls=0,target_candidates=6,manifest_sha256=freeze['manifest_sha256']))
    ids=read(OUT/'candidate_order.json');assert ids==freeze['candidate_order'] and len(ids)==6
    checks=[]
    for identifier in ids:
        cd=OUT/'candidates'/identifier;candidate=read(cd/'candidate.json');d=OUT/candidate['model_directory']
        for f,h in candidate['model_artifacts'].items():v.checked_hash(d/f,h)
        v.checked_hash(d/'row_metadata.csv.gz',candidate['row_metadata_sha256']);v.checked_hash(candidate['source_certificate'],candidate['source_certificate_sha256'])
        m=v.load_model(d);lab=labels(d/'row_metadata.csv.gz');ray=multipliers(candidate)
        invalid=[r for r,x in ray.items() if not math.isfinite(m.row_lower[r] if x>0 else m.row_upper[r])]
        if invalid:result={'status':'INVALID_CANDIDATE','reason':'Nonzero multiplier selects an infinite target row endpoint','inadmissible_rows':invalid,'expanded_pass':False,'no_repair_performed':True}
        else:result=v.check_ray(m,ray,TAU)
        families=dict(Counter(lab[r]['family'] for r in ray));retained=dict(Counter(x['family'] for x in lab))
        record=dict(id=identifier,case=candidate['case'],rule=candidate['rule'],kind=candidate['kind'],verification=result,retained_row_family_counts=retained,nonzero_multiplier_family_counts=families,retained_dwell_rows=sum(retained.get(f,0) for f in DWELL),nonzero_dwell_multipliers=sum(families.get(f,0) for f in DWELL),nonzero_temporal_generator_uids=sorted({lab[r]['uid'] for r in ray if lab[r]['family'] in TEMPORAL}),source_multiplier_count=candidate['source_multiplier_count'],retained_multiplier_count=len(ray),dropped_multiplier_count=candidate['dropped_multiplier_count'],candidate_sha256=v.sha(cd/'candidate.json'),target_model_artifacts=candidate['model_artifacts'],experiment_manifest_sha256=freeze['manifest_sha256'],optimizer_calls=0,interpretation='Fixed sufficient proof candidate; null is not feasibility. Full static/network/cap background remains; no IIS, minimality or raw-information claim.')
        save(cd/'exact_check.json',record);checks.append(record)
        print(json.dumps({'candidate':identifier,'status':result['status'],'expanded_gap':result.get('expanded_separation_gap',{}).get('float')}),flush=True)
    manifest(records)
    save(OUT/'summary.json',dict(target_candidates=6,target_candidate_checks=6,optimizer_calls=0,expanded_rejections=sum(x['verification']['expanded_pass'] for x in checks),all_outcomes_retained=True,all_frozen_hashes_unchanged=True,elapsed_seconds=time.perf_counter()-started,candidates=checks,scope='Post-label arithmetic explanation reuse on two known same-week HOD cases; no new replication or optimization'))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--prepare-only',action='store_true');modes.add_argument('--check-prepared',action='store_true');args=parser.parse_args()
    prepare() if args.prepare_only else check_prepared()
