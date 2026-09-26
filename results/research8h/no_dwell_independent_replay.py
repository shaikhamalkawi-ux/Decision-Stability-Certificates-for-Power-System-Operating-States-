"""Independent stdlib-only replay of archived no-dwell row/column bijections.
No producer modules, optimizer, NumPy or SciPy are imported.
"""
import csv, gzip, importlib.util, json, math, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/research8h/no_dwell_symmetry'
sp=importlib.util.spec_from_file_location('symmetry_archive_reader',ROOT/'src/research8h_standalone_verify.py')
v=importlib.util.module_from_spec(sp);sys.modules[sp.name]=v;sp.loader.exec_module(v)
FILES=('matrix.npz','bounds.npz','integrality.npz','objective.npz','row_metadata.csv.gz','model_metadata.json','native_inputs.npz')
BASE=ROOT/'results/research8h/seasonal_transfer/january_identity'
TARGETS=[ROOT/f'results/research8h/seasonal_transfer/seed_{s}' for s in (26093100,26093101,26100100)]+[ROOT/f'results/research8h/day_blocks/days_{s}' for s in (132,213,231,312,321)]
LOCAL={'aggregate_balance','thermal_upper','thermal_lower','nodal_balance','branch_flow'}
DWELL={'minimum_up','minimum_down'}
AUX={'transition','exclusive_transition'}
BLOCKS=((0,41),(6888,24),(18984,24))
KEPT=tuple(range(10920))+tuple(range(18984,23016))

def js(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def row(m,r):return {m.indices[e]:m.data[e] for e in range(m.indptr[r],m.indptr[r+1]) if m.data[e]!=0}
def native(p):return v.read_npz(p,('pmin','pmax','net','rows','nodal','source_hour'))
def checkhash(records):
    for r in records:
        p=Path(r['path']);assert p.stat().st_size==r['bytes'] and v.sha(p)==r['sha256'],str(p)

def read(d):
    m=v.load_model(d)
    assert (m.rows,m.cols)==(34681,23016)
    for r in range(m.rows):
        ids=m.indices[m.indptr[r]:m.indptr[r+1]]
        assert all(a<b for a,b in zip(ids,ids[1:]))
    with gzip.open(d/'row_metadata.csv.gz','rt',newline='') as f:lab=list(csv.DictReader(f))
    assert len(lab)==m.rows
    meta=js(d/'model_metadata.json')
    assert meta['offsets']==dict(P=0,U=6888,Y=10920,Z=14952,theta=18984)
    assert meta['hours']==168 and meta['units']==41 and meta['thermal_units']==24
    assert meta['individual_mean_constraints']==0 and meta['budget_MWh']==23195
    mask=v.read_npz(d/'integrality.npz',('integrality',))['integrality']
    assert mask.shape==(23016,) and mask.values==(0,)*6888+(1,)*12096+(0,)*4032
    obj=v.read_npz(d/'objective.npz',('objective',))['objective']
    assert obj.dtype=='<f8' and obj.shape==(23016,) and all(x==0 for x in obj.values)
    order=native(d/'native_inputs.npz')['source_hour']
    assert order.shape==(168,) and sorted(order.values)==list(range(168))
    assert order.values[:48]==tuple(range(48)) and order.values[120:]==tuple(range(120,168))
    for j in range(6888,18984):
        assert m.lower[j]==0 and m.upper[j]==(0 if 10920<=j<10944 or 14952<=j<14976 else 1)
    keys={};counts={};retained={}
    names=meta['thermal_unit_names'];assert len(names)==len(set(names))==24
    fossil=tuple(meta['unit_names'].index(s) for s in meta['fossil_units'])
    assert len(fossil)==len(set(fossil))==23
    for r,x in enumerate(lab):
        assert int(x['row'])==r
        family=x['family'];h=int(x['hour_0based']);uid=x['uid'];key=(family,h,uid)
        assert family in LOCAL|DWELL|AUX|{'fossil_energy_cap'} and key not in keys
        keys[key]=r;counts[family]=counts.get(family,0)+1
        rr=row(m,r)
        if family in AUX:
            assert 1<=h<168 and uid in names
            q=names.index(uid);u=6888+24*h+q;y=10920+24*h+q;z=14952+24*h+q
            if family=='transition':
                assert rr=={u:1.,u-24:-1.,y:-1.,z:1.}
                assert m.row_lower[r]==m.row_upper[r]==0
            else:
                assert rr=={y:1.,z:1.} and m.row_lower[r]==-math.inf and m.row_upper[r]==1
        elif family in DWELL:
            continue
        else:
            assert all(j in KEPT for j in rr)
            if family=='fossil_energy_cap':
                assert h==-1 and rr=={t*41+q:1. for t in range(168) for q in fossil}
                assert m.row_lower[r]==-math.inf and m.row_upper[r]==23195
            else:
                assert 0<=h<168
                for j in rr:
                    assert any(start<=j<start+168*width and (j-start)//width==h for start,width in BLOCKS)
            retained[key]=r
    assert counts['transition']==counts['exclusive_transition']==4008
    assert counts['minimum_up']==counts['minimum_down']==4008
    assert counts['fossil_energy_cap']==1 and len(retained)==18649
    for family in AUX:
        assert all((family,h,u) in keys for h in range(1,168) for u in names)
    return m,meta,mask.values,order.values,retained,counts

def main():
    start=time.perf_counter();manifest=js(OUT/'input_manifest.json')
    expect={str(p.resolve()) for p in [ROOT/'src/research8h_no_dwell_symmetry.py',ROOT/'docs/research8h/NO_DWELL_SYMMETRY_PROTOCOL.md',*[d/f for d in [BASE,*TARGETS] for f in FILES]]}
    assert len(manifest)==len(expect)==65 and {str(Path(r['path']).resolve()) for r in manifest}==expect
    checkhash(manifest)
    before=js(OUT/'before_audit.json');assert before['optimizer_calls']==0 and before['input_manifest_sha256']==v.sha(OUT/'input_manifest.json')
    bm,bmeta,bmask,border,brows,bcounts=read(BASE);assert border==tuple(range(168))
    old=js(OUT/'summary.json');assert old['pass'] and old['optimizer_calls']==0 and len(old['cases'])==8
    results=[]
    for case,d in zip(old['cases'],TARGETS):
        m,meta,mask,order,rows,counts=read(d)
        assert all(meta[k]==bmeta[k] for k in ('unit_names','thermal_unit_names','bus_ids','fossil_units'))
        assert counts==bcounts
        permutation={start+t*width+q:start+order[t]*width+q for start,width in BLOCKS for t in range(168) for q in range(width)}
        assert set(permutation)==set(permutation.values())==set(KEPT)
        assert all((m.lower[j],m.upper[j],mask[j])==(bm.lower[k],bm.upper[k],bmask[k]) for j,k in permutation.items())
        used=set()
        for (family,h,uid),r in rows.items():
            oldkey=(family,order[h] if h>=0 else h,uid);assert oldkey in brows
            br=brows[oldkey];assert br not in used;used.add(br)
            assert {permutation[j]:x for j,x in row(m,r).items()}==row(bm,br)
            assert (m.row_lower[r],m.row_upper[r])==(bm.row_lower[br],bm.row_upper[br])
        assert used==set(brows.values())
        changed=sum(t!=h for t,h in enumerate(order))
        assert case['retained_rows']==len(rows) and case['retained_columns']==len(KEPT) and case['changed_hours']==changed
        assert Path(case['case'])==d.relative_to(ROOT)
        result=dict(case=d.name,pass_all=True,retained_rows=len(rows),retained_columns=len(KEPT),changed_hours=changed,exact_row_column_bijections=True,canonical_integer_auxiliary_lift_templates=True,zero_objective_and_fossil_functional_checked=True)
        results.append(result);print(json.dumps(result),flush=True)
    checkhash(manifest)
    out=dict(status='INDEPENDENT_NO_DWELL_REPLAY_PASS',optimizer_calls=0,frozen_bindings=65,all_hashes_match_before_after=True,manifest_sha256=v.sha(OUT/'input_manifest.json'),review_source_sha256=v.sha(Path(__file__)),reader_sha256=v.sha(ROOT/'src/research8h_standalone_verify.py'),cases=results,elapsed_seconds=time.perf_counter()-start,scope='Exact supplied-matrix no-dwell projection symmetry; no native source reconstruction or new feasibility verdict')
    with (OUT/'independent_replay.json').open('x',encoding='utf-8') as f:json.dump(out,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({'status':out['status'],'seconds':out['elapsed_seconds']}),flush=True)

if __name__=='__main__':main()
