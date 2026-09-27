"""Independent archived rational path/certificate replay; no producer or optimizer."""
import csv,gzip,hashlib,importlib.util,json,sys,time
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent;OUT=ROOT/'results/research8h/strict_balance_paths'
sp=importlib.util.spec_from_file_location('strict_path_independent_decoder',ROOT/'src/research8h_standalone_verify.py');v=importlib.util.module_from_spec(sp);sys.modules[sp.name]=v;sp.loader.exec_module(v)
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();TAU=Q.from_float(1e-5)
def q(x):
    n,d=int(x['numerator']),int(x['denominator']);assert d>0;f=Q(n,d);assert (f.numerator,f.denominator)==(n,d);return f
def row(m,r):return {m.indices[e]:Q(m.data[e]) for e in range(m.indptr[r],m.indptr[r+1])}
def combine(m,y):
    a={};b=eb=norm=Q(0)
    for r,d in y.items():
        assert d and 0<=r<m.rows;endpoint=Q(m.row_lower[r] if d>0 else m.row_upper[r]);b+=d*endpoint;eb+=d*(endpoint-TAU if d>0 else endpoint+TAU);norm+=abs(d)
        for j,c in row(m,r).items():a[j]=a.get(j,Q(0))+d*c
    mx=sum((c*Q(m.upper[j] if c>=0 else m.lower[j]) for j,c in a.items()),Q(0))
    emx=sum((c*(Q(m.upper[j])+TAU if c>=0 else Q(m.lower[j])-TAU) for j,c in a.items()),Q(0));qn=sum(map(abs,a.values()),Q(0));g=b-mx;eg=eb-emx
    assert eg==g-TAU*(norm+qn)
    return a,dict(beta=b,expanded_beta=eb,box_maximum=mx,expanded_box_maximum=emx,strict_gap=g,expanded_gap=eg,row_l1=norm,column_l1=qn)
def pairs(entries,key='row'):
    items=[(x[key],q(x)) for x in entries];assert len(dict(items))==len(items) and items==sorted(items);return dict(items)
def main():
    begun=time.perf_counter();frozen=read(OUT/'prepared_freeze.json');assert read(HERE/'prepared_review.json')['status']=='INDEPENDENT_STRICT_PATH_PREPARED_PASS'
    assert sha(OUT/'input_manifest.json')==frozen['manifest_sha256']=='c418af87aba6912c8ed70d65233eed828e6d83772ad8ce5a2ede70d0ac2cfd6f'
    bindings=read(OUT/'input_manifest.json');assert len(bindings)==31
    for x in bindings:assert sha(Path(x['path']))==x['sha256'] and Path(x['path']).stat().st_size==x['bytes']
    snapshots={str(p.relative_to(ROOT)):sha(p) for p in OUT.rglob('*') if p.is_file()};done=read(OUT/'completion.json');ledger=read(OUT/'outcomes.json')
    assert not (OUT/'failure.json').exists();assert done['optimizer_calls']==0 and done['path_metrics_tried']==1
    cp=read(OUT/'common_paths.json');cp_hash=sha(OUT/'common_paths.json');reference=cp['reference_bus_index'];assert reference==12 and str(cp['reference_bus_ID'])=='113'
    assert cp['metric']=='strict exact R/abs(b)' and cp['base_model_month']==1 and cp['base_hour']==0
    edges={x['base_hour_row']:x for x in cp['edges']};assert len(edges)==38
    paths={x['bus_index']:x for x in cp['paths']};assert set(paths)==set(range(24))
    distances={j:q(p['strict_distance']) for j,p in paths.items()};terms={};adj={j:[] for j in range(24)}
    for r,e in edges.items():
        b,R=q(e['b']),q(e['rate']);assert b>0 and R>0;u,w=e['positive_bus'],e['negative_bus'];adj[u].append((w,r,R/b));adj[w].append((u,r,R/b))
        assert distances[u]<=distances[w]+R/b and distances[w]<=distances[u]+R/b
    for j,p in paths.items():
        current=reference;coef=[Q(0)]*24;cost=Q(0);seq=[];ps=[]
        for step in p['steps']:
            r=step['base_hour_row'];e=edges[r];b,R=q(e['b']),q(e['rate']);d=q(step['multiplier']);assert step['from_bus']==current
            assert (current,step['to_bus'],d) in ((e['negative_bus'],e['positive_bus'],1/b),(e['positive_bus'],e['negative_bus'],-1/b))
            current=step['to_bus'];seq.append(r);ps.append((r,d));coef[e['positive_bus']]+=d*b;coef[e['negative_bus']]-=d*b;cost+=abs(d)*R
        expected=[Q(0)]*24;expected[j]+=1;expected[reference]-=1
        assert current==j and coef==expected and cost==distances[j] and seq==p['ordered_base_hour_row_ids'];terms[j]=ps
    # Potential inequalities certify shortest distance; increasing-distance DP checks the full lexicographic tie rule independently of producer Dijkstra.
    lex={reference:()}
    for j in sorted((j for j in range(24) if j!=reference),key=lambda j:(distances[j],j)):
        options=[lex[n]+(r,) for n,r,c in adj[j] if distances[n]+c==distances[j]];assert options
        lex[j]=min(options);assert lex[j]==tuple(paths[j]['ordered_base_hour_row_ids'])
    counts=Counter();months=[];actualledger=[];last_after=0.;evaluated=0;skip=0
    for month in (1,4,7,10):
        d=ROOT/f'results/research8h/seasonal_reference/month_{month:02d}';m=v.load_model(d)
        with gzip.open(d/'row_metadata.csv.gz','rt',newline='') as stream:labels=list(csv.DictReader(stream))
        mhash={name:sha(d/name) for name in ('matrix.npz','bounds.npz','row_metadata.csv.gz')};monthcounts=Counter()
        with gzip.open(OUT/f'month_{month:02d}.jsonl.gz','rt',encoding='utf-8') as stream:records=[json.loads(s) for s in stream]
        assert [(x['hour_0based'],x['orientation']) for x in records]==[(h,s) for h in range(168) for s in (1,-1)]
        for rec in records:
            h,o=rec['hour_0based'],rec['orientation'];assert rec['month']==month;status=rec['status'];counts[status]+=1;monthcounts[status]+=1
            actualledger.append(dict(month=month,hour_0based=h,orientation=o,status=status,strict_separation=rec.get('strict_separation'),expanded_separation=rec.get('expanded_separation')))
            if status=='NOT_EVALUATED_PHASE_LIMIT':assert rec['elapsed_before_s']>=600;skip+=1;continue
            assert last_after<=rec['elapsed_before_s']<600 and rec['elapsed_after_s']>=rec['elapsed_before_s'];last_after=rec['elapsed_after_s'];evaluated+=1
            assert rec['common_paths_sha256']==cp_hash and rec['model_binding']['artifacts']==mhash and rec['model_binding']['experiment_manifest_sha256']==frozen['manifest_sha256']
            yy={r:Q(o*(1 if x['family']=='aggregate_balance' else -1)) for r,x in enumerate(labels) if int(x['hour_0based'])==h and x['family'] in ('aggregate_balance','nodal_balance')}
            assert len(yy)==25 and yy==pairs(rec['original_balance_multipliers']) and q(rec['original_balance_l1'])==25
            qq,bb=combine(m,yy);beta=bb['beta'];base=18984+24*h;qlocal=[qq.get(base+j,Q(0)) for j in range(24)];s=sum(qlocal,Q(0))
            assert {j:c for j,c in qq.items() if c}=={x['column']:q(x['value']) for x in rec['all_angle_q'] if q(x['value'])}
            assert q(rec['beta'])==beta and q(rec['q_ref'])==qlocal[reference] and q(rec['sum_q'])==s and rec['reference_column']==base+reference
            brow=[r for r,x in enumerate(labels) if x['family']=='branch_flow' and int(x['hour_0based'])==h];assert len(brow)==38
            mapped=dict(zip(edges,brow));assert month!=1 or h!=0 or all(k==r for k,r in mapped.items())
            merged={r:Q(0) for r in edges};unmerged={r:Q(0) for r in edges};contrib=rec['unmerged_path_contributions'];assert [x['bus_index'] for x in contrib]==[j for j in range(24) if j!=reference]
            for saved in contrib:
                j=saved['bus_index'];assert saved['angle_column']==base+j and q(saved['q'])==qlocal[j]
                expected=[]
                for r,p in terms[j]:
                    value=qlocal[j]*p;merged[r]+=value;unmerged[r]+=abs(value);expected.append((r,mapped[r],value))
                assert [(x['base_hour_row'],x['actual_hour_row'],q(x['value'])) for x in saved['path_weight_contributions']]==expected
            for r,e in edges.items():
                ar=mapped[r];assert labels[ar]['uid']==e['uid'] and row(m,ar)=={base+e['positive_bus']:q(e['b']),base+e['negative_bus']:-q(e['b'])}
                assert Q(m.row_upper[ar])==-Q(m.row_lower[ar])==q(e['rate'])
                if merged[r]:yy[ar]=-merged[r]
            assert yy==pairs(rec['original_matrix_row_multipliers'])
            assert [(x['row'],x['base_hour_row'],q(x['w']),q(x['added_row_multiplier']),q(x['unmerged_absolute_sum'])) for x in rec['merged_branch_contributions']]==[(mapped[r],r,merged[r],-merged[r],unmerged[r]) for r in edges]
            combined,direct=combine(m,yy);saved=rec['direct_original_row_check']
            assert all(q(saved[k])==value for k,value in direct.items()) and pairs(saved['all_touched_column_coefficients'],'column')==combined
            assert {j:c for j,c in combined.items() if c}==({base+reference:s} if s else {}) and saved['nonzero_column_count']==int(bool(s))
            assert m.lower[base+reference]==m.upper[base+reference]==0
            assert len(rec['support_gain_checks'])==2
            for ex,gain in zip((Q(0),TAU),rec['support_gain_checks']):
                cost=sum(((q(edges[r]['rate'])+ex)*abs(merged[r]) for r in edges),Q(0));uncost=sum(((q(edges[r]['rate'])+ex)*unmerged[r] for r in edges),Q(0));edgegain=uncost-cost;refgain=ex*(sum(map(abs,qlocal),Q(0))-abs(s));ind=beta-25*ex-uncost-ex*sum(map(abs,qlocal),Q(0));assembled=beta-25*ex-cost-ex*abs(s)
                assert edgegain>=0 and refgain>=0 and assembled==ind+edgegain+refgain==direct['strict_gap' if not ex else 'expanded_gap']
                assert q(gain['tau'])==ex and q(gain['independent_per_variable_path_gap'])==ind and q(gain['merged_edge_cost'])==cost and q(gain['unmerged_edge_cost'])==uncost and q(gain['shared_edge_gain'])==edgegain and q(gain['reference_gain'])==refgain and q(gain['assembled_original_row_gap'])==assembled
            upper=abs(beta)-25*TAU;assert direct['expanded_gap']<=upper<0 and q(rec['expanded_gap_upper_bound_abs_beta_minus_25tau'])==upper
            strict=direct['strict_gap']>0;assert rec['strict_separation']==strict and not rec['expanded_separation']
            assert status==('CERTIFIED_STRICT_REPRESENTATION_INFEASIBLE' if strict else 'VALID_NONSEPARATING_RATIONAL_CANDIDATE')
        months.append(dict(month=month,orientation_count=len(records),statuses=dict(monthcounts)));print(json.dumps(months[-1]),flush=True)
    assert actualledger==ledger and len(ledger)==1344 and evaluated==done['evaluated_orientations'] and skip==done['not_evaluated']
    assert dict(counts)==done['status_counts'] and sum(x['strict_separation'] is True for x in ledger)==done['strict_separating_orientations'] and sum(x['expanded_separation'] is True for x in ledger)==done['expanded_separating_orientations']
    assert done['arithmetic_phase_seconds']>=last_after and done['phase_soft_overrun_s']==max(0,done['arithmetic_phase_seconds']-600)
    assert all(sha(ROOT/p)==x for p,x in snapshots.items())
    for x in bindings:assert sha(Path(x['path']))==x['sha256'] and Path(x['path']).stat().st_size==x['bytes']
    report=dict(status='INDEPENDENT_STRICT_PATH_POSTRUN_PASS',months=months,orientation_denominator=1344,evaluated=evaluated,not_evaluated=skip,status_counts=dict(counts),common_paths_shortest_potential_proof=True,independent_lexicographic_optimal_path_DP=True,all_original_rational_rows_and_endpoints_replayed=True,reference_and_shared_edge_gain_identities=True,expanded_abs_beta_bound_verified=True,all31_inputs_and_result_hashes_unchanged=True,producer_validation_s=done['validation_seconds'],producer_phase_s=done['arithmetic_phase_seconds'],optimizer_calls=0,producer_source_imported=False,review_source_sha256=sha(Path(__file__)),producer_hashes=snapshots,elapsed_s=time.perf_counter()-begun,scope='Nonseparating fixed rational candidates do not prove strict feasibility; no physical inference.')
    with (HERE/'postrun_review.json').open('x',encoding='utf-8') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps({k:x for k,x in report.items() if k!='producer_hashes'}))
if __name__=='__main__':main()
