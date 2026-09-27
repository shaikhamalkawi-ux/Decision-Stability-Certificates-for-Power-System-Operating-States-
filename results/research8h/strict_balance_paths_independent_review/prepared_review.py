"""Independent structural/hash prepared gate; no path/gap/solver computation."""
import csv,gzip,hashlib,importlib.util,json,math,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'results/research8h/strict_balance_paths';HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('standalone_strict_prepared_gate',ROOT/'src/research8h_standalone_verify.py');v=importlib.util.module_from_spec(spec);sys.modules[spec.name]=v;spec.loader.exec_module(v)
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SOURCE='4622945e972313ac073f9c04bb55d179c7b4491533e03b44ae31accd06c1a0cd';PROTOCOL='6c28f25ae326bdf1fc195d8dccba270c02f464567fe90f02df76b85027b1f735';MANIFEST='c418af87aba6912c8ed70d65233eed828e6d83772ad8ce5a2ede70d0ac2cfd6f'
def main():
    t=time.perf_counter();freeze=read(OUT/'prepared_freeze.json');assert sha(OUT/'input_manifest.json')==freeze['manifest_sha256']==MANIFEST
    assert sha(ROOT/'src/research8h_strict_balance_paths.py')==freeze['source_sha256']==SOURCE
    assert sha(ROOT/'docs/research8h/STRICT_BALANCE_PATHS_PROTOCOL.md')==freeze['protocol_sha256']==PROTOCOL
    records=read(OUT/'input_manifest.json');assert len(records)==len({r['path'] for r in records})==31
    for r in records:
        p=Path(r['path']);assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
    bound={str(Path(r['path']).resolve()) for r in records}
    assert freeze['months']==[1,4,7,10] and freeze['hours_per_month']==168 and freeze['orientations']==[1,-1]
    assert freeze['hour_week_denominator']==672 and freeze['orientation_denominator']==1344 and freeze['phase_seconds']==600
    assert freeze['diagnostic_orientations_executed']==freeze['optimizer_calls']==0 and freeze['phase_starts_after_recorded_validation']
    assert freeze['path_metric']=='strict exact R/abs(b)' and freeze['all_nonreference_coordinates_use_paths'] and freeze['separate_root_execution_GO_required']
    for fn in ('execution_started.json','common_paths.json','focused_checks.json','outcomes.json','completion.json','failure.json'):assert not (OUT/fn).exists()
    old=ROOT/'results/research8h/nominal_balance_audit';assert sha(old/'freeze.json')=='fff9aedad3f9b29df7b4cfdb67ff1c906653d9c152e385419966263fc522bd4f'
    for r in read(old/'freeze.json')['inputs']:
        p=Path(r['path']);assert str(p.resolve()) in bound and p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
    assert read(old/'independent_replay.json')['status']=='INDEPENDENT_INTEGER_DYADIC_REPLAY_PASS'
    common=None;out=[]
    for month in (1,4,7,10):
        d=ROOT/f'results/research8h/seasonal_reference/month_{month:02d}'
        for fn in ('matrix.npz','bounds.npz','row_metadata.csv.gz','model_metadata.json'):assert str((d/fn).resolve()) in bound
        assert str((old/f'month_{month:02d}.json').resolve()) in bound
        m=v.load_model(d);meta=read(d/'model_metadata.json');assert (m.rows,m.cols)==(34680,23016)
        assert meta['offsets']==dict(P=0,U=6888,Y=10920,Z=14952,theta=18984)
        assert len(meta['bus_ids'])==24 and len(set(meta['bus_ids']))==24
        with gzip.open(d/'row_metadata.csv.gz','rt',newline='') as stream:labels=list(csv.DictReader(stream))
        assert len(labels)==m.rows
        blocks=[[] for _ in range(168)];balances=[[] for _ in range(168)]
        for r,x in enumerate(labels):
            assert int(x['row'])==r
            if x['family'] not in ('branch_flow','aggregate_balance','nodal_balance'):continue
            hour=int(x['hour_0based']);assert 0<=hour<168
            if x['family']!='branch_flow':
                assert math.isfinite(m.row_lower[r]) and m.row_lower[r]==m.row_upper[r];balances[hour].append((r,x['family'],x['uid']));continue
            terms=[(m.indices[e]-18984-hour*24,m.data[e]) for e in range(m.indptr[r],m.indptr[r+1]) if m.data[e]]
            assert len(terms)==2 and all(0<=j<24 for j,_ in terms) and terms[0][1]==-terms[1][1] and terms[0][0]!=terms[1][0]
            assert 0<m.row_upper[r]<math.inf and m.row_lower[r]==-m.row_upper[r]
            blocks[hour].append((r,x['uid'],tuple((j,c.hex()) for j,c in terms),m.row_upper[r].hex()))
        for hour,(edges,eqs) in enumerate(zip(blocks,balances)):
            assert len(edges)==38 and len(eqs)==25 and sum(x[1]=='aggregate_balance' for x in eqs)==1 and len({x[2] for x in eqs if x[1]=='nodal_balance'})==24
            assert not {x[0] for x in edges}&{x[0] for x in eqs}
            pins=[j for j in range(24) if m.lower[18984+24*hour+j]==m.upper[18984+24*hour+j]==0]
            assert len(pins)==1 and pins[0]==12 and str(meta['bus_ids'][12])=='113'
            normalized=(tuple(meta['bus_ids']),pins[0],tuple(x[1:] for x in edges))
            if common is None:common=normalized
            assert normalized==common
            adjacency={j:set() for j in range(24)}
            for _,_,terms,_ in edges:
                u,w=terms[0][0],terms[1][0];adjacency[u].add(w);adjacency[w].add(u)
            visited={pins[0]};stack=[pins[0]]
            while stack:
                for node in adjacency[stack.pop()]-visited:visited.add(node);stack.append(node)
            assert len(visited)==24
        out.append(dict(month=month,rows=m.rows,columns=m.cols,branch_rows=6384,balance_groups=168,exact_branch_pairs_and_symmetric_limits=True,common_hour_normalized_block=True,reference_index=12,reference_bus_ID=113,reference_is_column_bound=True,graph_connected=True,no_path_or_support_computation=True))
    assert read(OUT/'prior_readonly_inspection_note.json')['initial_assertion_failure_retained']
    for r in records:
        p=Path(r['path']);assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
    assert not (OUT/'execution_started.json').exists()
    report=dict(status='INDEPENDENT_STRICT_PATH_PREPARED_PASS',frozen_bindings=31,manifest_sha256=MANIFEST,source_sha256=SOURCE,protocol_sha256=PROTOCOL,all_hashes_match_before_after=True,models=out,diagnostic_orientations_executed=0,optimizer_calls=0,path_computations=0,execution_marker_absent=True,review_source_sha256=sha(Path(__file__)),elapsed_s=time.perf_counter()-t)
    with (HERE/'prepared_review.json').open('x',encoding='utf-8') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps(report))
if __name__=='__main__':main()
