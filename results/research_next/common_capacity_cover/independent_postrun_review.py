"""Independent saved recurrence and exact threshold replay; no producer import."""
from pathlib import Path
from fractions import Fraction as F
import csv,gzip,hashlib,json,math,time
ROOT=Path(__file__).resolve().parents[3];ARM=Path(__file__).resolve().parent;PRE=ARM/'prepared';RUN=ARM/'run01';TAU=F.from_float(1e-5)
def need(x,s):
    if not x:raise AssertionError(s)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def desc(p):return dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))
def rational(x):return F(int(x['numerator']),int(x['denominator']))
def packed(x):return dict(numerator=str(x.numerator),denominator=str(x.denominator),approximate=float(x))
def hexq(x):
    y=float.fromhex(x);need(math.isfinite(y),'Finite admitted box/row');return F(y)
def main():
    started=time.perf_counter()
    need(sha(ARM/'independent_prepared_review.json')=='a9c4fdc0f2accd12f986ad6281210e4223b2104c5ccab88f792c8f227bf17210','Independent actual-premise gate')
    need(sha(PRE/'prepared_freeze.json')=='06a487622eabdf54e254307d9a9c684e95338f08331c0363d15399a0ce188988','Freeze')
    need(sha(ARM/'producer_output_inventory.csv')=='3c65aa50c352d268ab2e9b1fb494a13e6a6e381571be8b92d506bd66fd9f87da','Closed output inventory')
    freeze=read(PRE/'prepared_freeze.json');need(desc(PRE/'input_manifest.json')==freeze['input_manifest'],'Input manifest')
    inputs=read(PRE/'input_manifest.json')['files'];need(len(inputs)==71,'Input denominator')
    for x in inputs:need(desc(Path(x['path']))==x,'Unchanged input')
    with (ARM/'producer_output_inventory.csv').open(encoding='utf-8',newline='') as f:outputs=list(csv.DictReader(f))
    need(len(outputs)==10,'Closed output count')
    for x in outputs:
        p=ROOT/x['path'];need(p.stat().st_size==int(x['bytes']) and sha(p)==x['sha256'],'Closed output binding')
    a=read(PRE/'admission.json');need(desc(PRE/'admission.json')==freeze['admission'],'Admitted premises')
    completion=read(RUN/'completion.json');need(completion['status']=='COMPLETE' and completion['optimizer_calls']==0 and completion['threshold_queries']==168,'Complete authorized calculation')
    need(0<=completion['elapsed_seconds']<120 and completion['phase_limit_seconds']==120,'Recorded soft phase limit')
    tables=read(RUN/'tables.json')['tables'];need(len(tables)==len(a['tuples'])==completion['distinct_dp_tables'],'Full table denominator')
    suffixes=[];table_checks=[]
    for g,record in zip(a['tuples'],tables):
        need(g['group']==record['group']==len(suffixes),'Group order');weights=g['capacity'];costs=g['cost']
        need(len(weights)==len(costs)==23 and all(type(x) is int and x>=0 for x in weights+costs),'Exact admitted items')
        size=sum(weights)+1;need(size==record['states_per_layer'] and size<=100001,'Resource dimensions')
        for key in ('recurrence','terminal'):need(desc(Path(record[key]['path']))==record[key],'Saved table descriptor')
        with gzip.open(record['recurrence']['path'],'rt',encoding='utf-8') as f:layers=[json.loads(line) for line in f]
        need(len(layers)==record['layers']==24,'Every prefix layer retained')
        previous=None;cell_checks=0;finite=[]
        for k,item in enumerate(layers):
            row=item['values'];need(item['layer']==k and len(row)==size,'Layer coordinate')
            need(all(x is None or type(x) is int and x>=0 for x in row),'Integer cost/unreachable schema')
            if k==0:need(row==[0]+[None]*(size-1),'Exact initial empty subset layer')
            else:
                b=weights[k-1];cost=costs[k-1]
                for capacity,actual in enumerate(row):
                    possibilities=[]
                    if previous[capacity] is not None:possibilities.append(previous[capacity])
                    if capacity>=b and previous[capacity-b] is not None:possibilities.append(previous[capacity-b]+cost)
                    expected=min(possibilities) if possibilities else None
                    need(actual==expected,'Complete previous-layer 0/1 recurrence')
                    cell_checks+=1
            finite.append(sum(x is not None for x in row));previous=row
        need(finite==record['finite_states_per_layer'],'All finite-state counts')
        terminal=read(record['terminal']['path']);need(terminal['group']==g['group'] and terminal['capacity']==weights and terminal['cost']==costs,'Terminal roster')
        need(terminal['terminal_exact_capacity_cost']==previous,'Complete terminal frontier')
        saved=terminal['terminal_at_least_capacity_cost'];need(len(saved)==size,'Suffix denominator')
        best=None
        for capacity in reversed(range(size)):
            if previous[capacity] is not None:best=previous[capacity] if best is None else min(best,previous[capacity])
            need(saved[capacity]==best,'Every suffix minimum')
        suffixes.append(saved);table_checks.append(dict(group=g['group'],layers=24,states_per_layer=size,recurrence_cells_checked=cell_checks,initial_cells_checked=size,suffix_cells_checked=size))
    qs=read(RUN/'hourly_queries.json')['hours'];need(len(qs)==168,'168 fixed queries')
    totals=[F(0),F(0)];no_cover=[]
    for t,q in enumerate(qs):
        need(q['hour']==t and q['group']==a['hour_group'][t] and len(q['worlds'])==2,'Query mapping')
        ds=[]
        for wi,w in enumerate(a['worlds']):
            h=w['hours'][t];entry=q['worlds'][wi]
            balance=hexq(h['aggregate_lower_hex'])-TAU
            upper=sum((hexq(x['upper_hex'])+TAU for x in h['nonfossil_upper_boxes']),F(0))
            lower=sum((hexq(x['lower_hex'])-TAU for x in h['fossil_lower_boxes']),F(0))
            need(len(h['nonfossil_upper_boxes'])==18 and len(h['fossil_lower_boxes'])==23,'Admitted box counts')
            d=max(balance-upper,lower);ds.append(d)
            need(entry['world']==w['world'],'World identity')
            for key,value in dict(aggregate_lower=balance,nonfossil_upper_sum=upper,direct_fossil_lower=lower,d=d).items():need(rational(entry[key])==value,'Exact row/box floor')
        required=max(ds)-23*TAU
        # Different exact ceiling expression; no fractional capacity truncation.
        integer=max(0,(required.numerator+required.denominator-1)//required.denominator)
        suffix=suffixes[q['group']];minimum=suffix[integer] if integer<len(suffix) else None
        need(rational(q['required_capacity'])==required and q['integer_threshold']==integer and q['minimum_committed_output']==minimum,'Exact capacity threshold and complete-table minimum')
        if minimum is None:
            no_cover.append(t);need(all('selected_floor' not in x for x in q['worlds']),'No invented floor for empty cover')
        else:
            for wi,entry in enumerate(q['worlds']):
                floor=max(ds[wi],F(minimum)-23*TAU);totals[wi]+=floor
                need(rational(entry['selected_floor'])==floor,'Integer cost to original fossil lower bound')
    result=read(RUN/'result.json');need(result['no_capacity_cover_hours']==no_cover and rational(result['tau'])==TAU,'Result tolerance/empty cover')
    need(result['optimizer_calls']==0 and result['scientific_dp_tables']==len(tables) and result['scientific_threshold_queries']==168,'Executed scope')
    summaries=[]
    for wi,w in enumerate(a['worlds']):
        cap=hexq(w['cap_upper_hex'])+TAU;r=result['worlds'][wi];need(r['world']==w['world'] and rational(r['expanded_cap'])==cap,'Original expanded cap')
        if no_cover:need(r['energy_floor'] is None and r['floor_minus_cap'] is None and not r['cap_rejected'],'Empty-cover classification')
        else:need(rational(r['energy_floor'])==totals[wi] and rational(r['floor_minus_cap'])==totals[wi]-cap and r['cap_rejected']==(totals[wi]>cap),'Strict exact cap comparison')
        summaries.append(dict(world=w['world'],floor=None if no_cover else packed(totals[wi]),floor_minus_cap=None if no_cover else packed(totals[wi]-cap),cap_rejected=r['cap_rejected']))
    negative=bool(no_cover or any(x['cap_rejected'] for x in summaries))
    need(result['status']==('UNIVERSAL_COMMON_REJECTION_PENDING_REVIEW' if negative else 'NO_REJECTION_FROM_THIS_BOUND'),'Scientific classification')
    need(result['original_question']==('PENDING_INDEPENDENT_PROOF_REVIEW' if negative else 'UNKNOWN'),'Original question scope')
    for x in inputs:need(desc(Path(x['path']))==x,'Input changed during review')
    for x in outputs:
        p=ROOT/x['path'];need(p.stat().st_size==int(x['bytes']) and sha(p)==x['sha256'],'Output changed during review')
    report=dict(status='PASS_INDEPENDENT_CAPACITY_COVER_POSTRUN',tables=table_checks,queries=168,worlds=summaries,no_cover_hours=no_cover,
        rejection=negative,original_common_binary_verdict='REJECTED' if negative else 'UNKNOWN',not_a_feasibility_witness=True,
        inherited_independent_original_premise_review_sha256='a9c4fdc0f2accd12f986ad6281210e4223b2104c5ccab88f792c8f227bf17210',
        inputs_unchanged=71,producer_outputs_unchanged=10,optimizer_calls=0,producer_imports=0,new_DP_generation=0,
        scope='Verification of every saved recurrence/suffix cell and exact original-premise threshold/floor/cap arithmetic; no alternate bound or dwell attribution.',
        elapsed_seconds=time.perf_counter()-started,review_source_sha256=sha(__file__))
    with (ARM/'independent_postrun_review.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps(report))
if __name__=='__main__':main()
