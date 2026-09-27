"""Verify every saved selected-dwell recurrence cell; never import the producer."""
from pathlib import Path
from fractions import Fraction as Q
from datetime import datetime, timezone
import csv, gzip, hashlib, itertools, json, math, time

ROOT=Path(__file__).resolve().parents[3]
ARM=ROOT/'results/research_next/selected_dwell_cover'
PRE,RUN=ARM/'prepared',ARM/'run01'
OUT=Path(__file__).resolve().parent
PINS={
 PRE/'prepared_freeze.json':'9cf1f83465a83596c2f837dd122c91463dcdca2f5648780a69afd99228443098',
 PRE/'input_manifest.json':'57951a4d2160230ef917f7745a3d074f9eca4cb445eb43c3345cb6df44d5395c',
 OUT/'prepared_review.json':'676bd93ee4e8192dfe273b49a416cbedb2111dcd92d5d757b906d6142e8dab8c',
 OUT/'prepared_review.py':'6ae62f270013d20827c43481cd36fc6b320278e095b1ea28ad6abdd99ad7daf7',
 RUN/'result.json':'453193dd721951f8fdf7108a06f4d962bfd644884d5195c829312b41d2a72def',
 RUN/'completion.json':'812b82600a7f47fea3309c848fd4bd4b04399f47b81ad8fc1656c5b63c856a2a',
 ARM/'producer_output_inventory.csv':'33f648f395763c95d371de928c650e11f9e5dc83068c4931169b4c0a66832210',
 ROOT/'results/research_next/common_capacity_cover/run01/result.json':'a2d34748019ab31b1bf075addedf55493bdebeed8beeb386e4d218c59cb2fdce',
 ROOT/'results/research_next/common_capacity_cover/independent_postrun_review.json':'1c070d02efed767475e864d1fdf4dcd83a7a3012fc472590bbc13063c696bb19',
}
SELECTED=['115_STEAM_3','116_STEAM_1','118_CC_1']
TAU=Q.from_float(1e-5)
def require(ok,msg):
    if not ok:raise AssertionError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def rat(x):
    q=Q(int(x['numerator']),int(x['denominator']))
    require(str(q.numerator)==x['numerator'] and str(q.denominator)==x['denominator'],'Noncanonical fraction')
    require(x['approximate']==float(q),'Diagnostic approximate fraction mismatch')
    return q
def result_q(q):return {'numerator':str(q.numerator),'denominator':str(q.denominator),'approximate':float(q)}
def binary64(s):
    f=float.fromhex(s);require(math.isfinite(f),'Nonfinite archived binary64');return Q.from_float(f)
def bindings_check(rows):
    require(len({r['path'].casefold() for r in rows})==len(rows),'Duplicate manifest binding')
    for x in rows:
        p=Path(x['path']);data=p.read_bytes()
        require(len(data)==int(x['bytes']) and hashlib.sha256(data).hexdigest()==x['sha256'],'Changed binding '+str(p))
def layer_stream(path):
    with gzip.open(path,'rt',encoding='utf-8') as f:
        for line in f:
            require(bool(line.strip()),'Empty evidence line');yield json.loads(line)
def values_ok(values,n):
    require(len(values)==n and all(x is None or type(x) is int for x in values),'Exact integer/None state vector')
def save(name,obj):
    with (OUT/name).open('x',encoding='utf-8') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')

def main():
    start=time.perf_counter();require(not (OUT/'postrun_review.json').exists(),'One saved-evidence replay only')
    for p,h in PINS.items():require(sha(p)==h,'Pinned input mismatch '+str(p))
    inputs=read(PRE/'input_manifest.json')['files'];require(len(inputs)==101,'Input denominator');bindings_check(inputs)
    with (ARM/'producer_output_inventory.csv').open(encoding='utf-8-sig',newline='') as f:listed=list(csv.DictReader(f))
    require(len(listed)==35,'Producer output inventory denominator')
    outputs=[dict(path=str(ROOT/r['path']),bytes=int(r['bytes']),sha256=r['sha256']) for r in listed];bindings_check(outputs)
    require(read(OUT/'prepared_review.json')['status']=='PASS_SOURCE_AND_PREPARED_PREMISES_ONLY','Independent premise gate')
    completion=read(RUN/'completion.json');begun=read(RUN/'execution_started.json');res=read(RUN/'result.json')
    require(completion['status']=='COMPLETE' and completion['scientific_runs']==1 and completion['optimizer_calls']==0,'Completed sole run')
    require(completion['all_inputs_and_transport_unchanged'] and 0<=completion['elapsed_seconds']<=completion['phase_limit_seconds']==300,'Producer allocation/completion')
    require(begun['freeze_sha256']==PINS[PRE/'prepared_freeze.json'] and begun['selected_units']==SELECTED and begun['scalar_objectives']==1 and begun['alternative_sets']==0,'Fixed execution design')
    adm=read(PRE/'admission.json');old=read(PRE/'capacity_admission.json')
    require(rat(adm['tau'])==rat(old['tau'])==TAU,'Exact tau')
    weights,costs=adm['remaining_capacity'],adm['remaining_cost']
    require(len(weights)==len(costs)==20 and all(type(x) is int and x>=0 for x in weights+costs),'Remaining cover premise')
    width=sum(weights)+1;require(width<=100001,'Capacity guard')
    previous=None;cover_cells=0;cover_count=0
    # Pull recurrence at each exact capacity; no producer recurrence function.
    for entry in layer_stream(RUN/'remaining_cover_layers.jsonl.gz'):
        n=entry['layer'];require(n==cover_count and n<=20,'Complete cover layer order')
        current=entry['values'];values_ok(current,width)
        if n==0:require(current==[0]+[None]*(width-1),'Cover initial layer')
        else:
            w,cost=weights[n-1],costs[n-1]
            for capacity,stored in enumerate(current):
                options=[]
                if previous[capacity] is not None:options.append(previous[capacity])
                if capacity>=w and previous[capacity-w] is not None:options.append(previous[capacity-w]+cost)
                require(stored==(min(options) if options else None),'Cover recurrence cell')
                cover_cells+=1
        previous=current;cover_count+=1
    require(cover_count==21,'All twenty-item cover layers')
    terminal=read(RUN/'remaining_cover_terminal.json')
    require(terminal['capacity']==weights and terminal['cost']==costs and terminal['exact']==previous,'Terminal cover binding')
    suffix=[];best=None
    for value in reversed(previous):
        if value is not None:best=value if best is None else min(best,value)
        suffix.append(best)
    suffix.reverse();require(terminal['at_least']==suffix,'Every suffix minimum')
    hourly=read(RUN/'conditional_hourly_costs.json');require(rat(hourly['tau'])==TAU and len(hourly['hours'])==168,'Hourly proof denominator')
    patterns=list(itertools.product((0,1),repeat=3));qcosts=[];denominators=[];query_count=0
    specs=adm['selected'];require([x['uid'] for x in specs]==SELECTED,'Selected roster')
    require([x['world'] for x in old['worlds']]==['identity','days_321'],'Both original worlds')
    for t,record in enumerate(hourly['hours']):
        require(record['hour']==t and len(record['patterns'])==8 and len(record['worlds'])==2,'Hour/pattern order')
        floors=[]
        for wi,world in enumerate(old['worlds']):
            h=world['hours'][t];require(h['hour']==t and len(h['nonfossil_upper_boxes'])==18 and len(h['fossil_lower_boxes'])==23,'Inherited exact hourly premises')
            balance=binary64(h['aggregate_lower_hex'])-TAU
            nonfossil=sum((binary64(x['upper_hex'])+TAU for x in h['nonfossil_upper_boxes']),Q(0))
            direct=sum((binary64(x['lower_hex'])-TAU for x in h['fossil_lower_boxes']),Q(0))
            floor=max(direct,balance-nonfossil);floors.append(floor)
            saved=record['worlds'][wi];require(saved['world']==world['world'],'World floor order')
            for key,q in (('aggregate_lower',balance),('nonfossil_upper_sum',nonfossil),('direct_fossil_lower',direct),('d',floor)):
                require(rat(saved[key])==q,'Saved floor derivation '+key)
        row=[]
        for pattern,saved in zip(patterns,record['patterns']):
            require(saved['pattern']==list(pattern),'Fixed pattern order')
            own_capacity=sum(bit*spec['PMax'] for bit,spec in zip(pattern,specs));own_cost=sum(bit*spec['PMin'] for bit,spec in zip(pattern,specs))
            threshold=max(floors)-23*TAU-own_capacity;h=max(0,math.ceil(threshold))
            lower=suffix[h] if h<len(suffix) else None
            require(saved['selected_capacity']==own_capacity and saved['selected_cost']==own_cost and rat(saved['required_remaining_capacity'])==threshold and saved['integer_threshold']==h and saved['remaining_minimum_cost']==lower,'Conditional threshold/cover')
            if lower is None:
                require(saved['world_floors'] is None and saved['sum_cost'] is None,'Impossible pattern preserved');row.append(None)
            else:
                perworld=[max(d,own_cost+lower-23*TAU) for d in floors];total=sum(perworld,Q(0))
                require([rat(x) for x in saved['world_floors']]==perworld and rat(saved['sum_cost'])==total,'Both23tau floors and scalar sum')
                row.append(total);denominators.append(total.denominator)
            query_count+=1
        qcosts.append(row)
    cap=sum((binary64(x['cap_upper_hex'])+TAU for x in old['worlds']),Q(0))
    require(cap==2*23195+2*TAU and rat(hourly['combined_cap'])==cap,'Two once-expanded caps')
    denominators.append(cap.denominator);require(all(d>0 and d&(d-1)==0 for d in denominators),'Dyadic input')
    scale=math.lcm(*denominators);require(scale.bit_length()<=256 and int(hourly['scale'])==scale,'Lossless scale')
    scaled=[]
    for qrow,saved in zip(qcosts,hourly['scaled_sum_costs']):
        exact=[None if x is None else x*scale for x in qrow]
        require(all(x is None or x.denominator==1 for x in exact),'Integral scaled objective')
        expected=[None if x is None else x.numerator for x in exact]
        require(saved==expected,'Every scaled hourly cost');values_ok(saved,8);scaled.append(expected)
    require(len(hourly['scaled_sum_costs'])==168 and query_count==1344,'Full query denominator')
    graph=read(RUN/'residence_state_graph.json');dwells=[(s['minimum_up'],s['minimum_down']) for s in specs]
    require(graph['selected_units']==SELECTED and graph['dwells']==[list(x) for x in dwells],'Residence specifications')
    # Independent predecessor construction from the after-current-hour state meaning.
    labels=list(itertools.product(*[[(u,r) for u,d in ((0,down),(1,up)) for r in range(d)] for up,down in dwells]))
    require(graph['labels']==[[list(x) for x in s] for s in labels] and len(labels)==3328,'All canonical state labels')
    index={label:i for i,label in enumerate(labels)};predecessors=[];successors=[[] for _ in labels]
    for k,destination in enumerate(labels):
        local=[]
        for (u,r),(up,down) in zip(destination,dwells):
            duration=up if u else down;choices=[]
            if r==0:choices.append((u,0))
            if r+1<duration:choices.append((u,r+1))
            if r==duration-1:choices.append((1-u,0))
            local.append(choices)
        pred=sorted(index[x] for x in itertools.product(*local));require(len(set(pred))==len(pred),'No duplicate transition')
        predecessors.append(pred)
        for j in pred:successors[j].append(k)
    require(graph['successors']==successors,'Every complete transition edge')
    pindex={p:i for i,p in enumerate(patterns)};pids=[pindex[tuple(u for u,r in s)] for s in labels]
    require(graph['patterns']==[list(x) for x in patterns] and graph['pattern_ids']==pids,'State-to-pattern map')
    initial=[j for j,s in enumerate(labels) if all(r==0 for u,r in s)]
    require(len(initial)==8 and graph['initial_state_ids']==initial and graph['terminal_acceptance']=='all_states_even_if_locked','Mature initial/clipped final')
    previous=None;layers=0;cells=0;edges_checked=0;reachable=[]
    for entry in layer_stream(RUN/'residence_layers.jsonl.gz'):
        t=entry['hour'];require(t==layers and t<168,'Complete residence hour order')
        current=entry['values'];values_ok(current,len(labels))
        if t==0:
            expected=[scaled[0][pids[j]] if j in initial else None for j in range(len(labels))]
            require(current==expected,'Initial current-hour cost exactly once')
        else:
            edges_checked+=sum(len(successors[j]) for j,value in enumerate(previous) if value is not None)
            for k,stored in enumerate(current):
                cost=scaled[t][pids[k]]
                incoming=[previous[j] for j in predecessors[k] if previous[j] is not None]
                expected=None if cost is None or not incoming else min(incoming)+cost
                require(stored==expected,'Saved complete residence recurrence cell')
        reachable.append(sum(x is not None for x in current));previous=current;layers+=1;cells+=len(current)
    require(layers==168 and cells==559104 and edges_checked<=5000000,'Full layered proof denominator')
    finite=[x for x in previous if x is not None];lower=None if not finite else Q(min(finite),scale)
    rejected=lower is None or lower>cap
    require(res['status']==('UNIVERSAL_COMMON_REJECTION_PENDING_REVIEW' if rejected else 'NO_REJECTION_FROM_THIS_BOUND'),'Correct strict verdict')
    require(res['empty_final_graph']==(not finite) and res['selected_units']==SELECTED and res['selection_posthoc_census_guided'],'Fixed case scope')
    require(rat(res['combined_expanded_cap'])==cap and res['scale']==str(scale),'Reported cap/scale')
    require(res['reachable_states_per_hour']==reachable and res['transition_checks']==edges_checked,'Reachability/transition counts')
    for k,n in (('table_layers',21),('conditional_queries',1344),('residence_layers',168),('state_labels',3328),('archived_state_values',559104),('optimizer_calls',0),('new_full_schedule_candidates',0)):
        require(res[k]==n,'Reported denominator '+k)
    require(lower is not None and rat(res['summed_world_energy_floor'])==lower and rat(res['floor_minus_cap'])==lower-cap,'Exact reported final bound')
    require(not rejected and res['original_question']=='UNKNOWN','Current null preserves UNKNOWN')
    old_result=read(ROOT/'results/research_next/common_capacity_cover/run01/result.json')
    old_review=read(ROOT/'results/research_next/common_capacity_cover/independent_postrun_review.json')
    old_sum=sum((rat(x['energy_floor']) for x in old_result['worlds']),Q(0))
    require(old_sum==sum((rat(x['floor']) for x in old_review['worlds']),Q(0)),'Previously reviewed floor identity')
    improvement=lower-old_sum
    bindings_check(inputs);bindings_check(outputs)
    for p,h in PINS.items():require(sha(p)==h,'Pinned file changed during audit')
    report={'status':'PASS_INDEPENDENT_FULL_SELECTED_DWELL_REPLAY','utc':datetime.now(timezone.utc).isoformat(),
      'elapsed_seconds':time.perf_counter()-start,'reviewer_source_sha256':sha(__file__),
      'input_bindings_unchanged':101,'producer_inventory_files_unchanged':35,
      'cover_layers':cover_count,'cover_initial_cells':width,'cover_recurrence_cells':cover_cells,'suffix_cells':width,
      'conditional_queries':query_count,'state_labels':len(labels),'residence_layers':layers,'residence_cells':cells,
      'evaluated_transition_count_verified':edges_checked,'exact_lower':result_q(lower),'exact_combined_cap':result_q(cap),
      'exact_floor_minus_cap':result_q(lower-cap),'prior_sum_floor':result_q(old_sum),'exact_improvement':result_q(improvement),
      'equals_sum_prior_hourly_bounds':improvement==0,'original_common_question':'UNKNOWN',
      'interpretation':'No improvement for this fixed selected-three relaxation; does not prove dwell irrelevant or any common feasible schedule',
      'producer_imports':0,'optimizer_calls':0,'new_cases_or_objectives':0,
      'scope':'Verification of saved exact evidence by independent pull recurrences and predecessor rule; no producer rerun or newly selected bound',
      'trusted_files':{str(p):h for p,h in PINS.items()}}
    save('postrun_review.json',report);print(json.dumps({'status':report['status'],'elapsed_seconds':report['elapsed_seconds'],'report_sha256':sha(OUT/'postrun_review.json'),'exact_improvement':report['exact_improvement']}))

if __name__=='__main__':
    try:main()
    except BaseException as e:
        save('postrun_review_failure.json',{'status':'FAIL_PRESERVED_NO_RETRY','error_type':type(e).__name__,'message':str(e),'optimizer_calls':0,'producer_imports':0})
        raise
