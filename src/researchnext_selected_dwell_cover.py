"""One exact selected-residence/remaining-cover bound; no optimizer or fallback."""
from __future__ import annotations
import argparse
import csv
from datetime import datetime, timezone
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
ARM = ROOT/'results/research_next/selected_dwell_cover'
PRE, RUN = ARM/'prepared', ARM/'run01'
OLD = ROOT/'results/research_next/common_capacity_cover/prepared'
PROTOCOL = ROOT/'docs/research_next/SELECTED_DWELL_COVER_PROTOCOL.md'
DESIGN = ROOT/'docs/research_next/SELECTED_DWELL_COVER_BOUND_PROPOSAL.md'
KERNEL = ROOT/'src/research8h_standalone_verify.py'
KERNEL_SHA = '708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'
SELECTED = ('115_STEAM_3', '116_STEAM_1', '118_CC_1')
# UID, exact PMin, exact PMax, ceil(native minimum up), ceil(native minimum down).
SPEC = ((62,155,8,8), (62,155,8,8), (170,355,8,5))
WORLDS = ('identity','days_321')
TAU = Q.from_float(1e-5)
SECONDS, MAX_CAPACITY, MAX_CELLS, MAX_EDGES, MAX_DENOM_BITS = 300.,100000,600000,5000000,256
PINS = {
 'docs/research_next/SELECTED_DWELL_COVER_BOUND_PROPOSAL.md':'b6491923aec0912079afceae3e4d82e08574aafb9266a60302d99df1fce8b676',
 'src/temporal_lp_certificate.py':'6191c5760811cab0ec22b2fb1376a5be3aa47cb548e1260c4a17e2563d9802e4',
 'results/research_next/common_capacity_cover/prepared/prepared_freeze.json':'06a487622eabdf54e254307d9a9c684e95338f08331c0363d15399a0ce188988',
 'results/research_next/common_capacity_cover/prepared/input_manifest.json':'6018b53d796926f5e1ab368958d8a03a3a7e21e67d88702825b057ac672b10e3',
 'results/research_next/common_capacity_cover/prepared/admission.json':'0a9abd8f40376f54d834763c118ea9c70642c3a9ca966f91111e2fb6ef32d8dd',
 'results/research_next/common_capacity_cover/independent_prepared_review.json':'a9c4fdc0f2accd12f986ad6281210e4223b2104c5ccab88f792c8f227bf17210',
 'results/research_next/common_capacity_cover/independent_postrun_review.json':'1c070d02efed767475e864d1fdf4dcd83a7a3012fc472590bbc13063c696bb19',
 'results/research_next/common_commitment/INDEPENDENT_LP_NONBINARY_STATES.json':'bc371fa53ae5f94d3f1536eefc526871b60d4de2f7bae4b027a088d9d2ba4282',
 'results/research_next/union_affine_cut_schema2/run01/identity_cut.json':'8ba409f8702486dcdebc7611a98609696348c41d46af8fa38d7e77b5614621cb',
 'results/research_next/union_affine_cut_schema2/run01/days_321_cut.json':'7fe192f2acd9ebd1e14eeecde3ece0e3d5d24ede8408e6047b1cb9dd597f30dd',
 'results/research_next/union_affine_cut_schema2/independent_postrun_review.json':'04b94ab9ca268615e1980066e6654fec58e01b92b96def0049a3dc94cff9a3f8',
}

class Unsupported(ValueError): pass
class Incomplete(RuntimeError): pass
def need(ok,message):
    if not ok: raise ValueError(message)
def support(ok,message):
    if not ok: raise Unsupported(message)
def utc(): return datetime.now(timezone.utc).isoformat()
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def save(path,value):
    with Path(path).open('x',encoding='utf-8') as f:
        json.dump(value,f,indent=2,allow_nan=False); f.write('\n')
def bind(path,data=None):
    p=Path(path).resolve(); b=p.read_bytes() if data is None else data
    return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def validate(items):
    need(len({x['path'].casefold() for x in items})==len(items),'Duplicate binding')
    for item in items: need(bind(item['path'])==item,'Changed binding: '+item['path'])
def rat(q): return dict(numerator=str(q.numerator),denominator=str(q.denominator),approximate=float(q))
def qhex(value):
    f=float.fromhex(value);support(math.isfinite(f),'Nonfinite original endpoint');return Q(f)
def ceil(q): return -((-q.numerator)//q.denominator)
def budget(start):
    if time.perf_counter()-start>=SECONDS: raise Incomplete('300-second soft phase exceeded')
def kernel():
    need(sha(KERNEL)==KERNEL_SHA,'Pinned decoder changed')
    spec=importlib.util.spec_from_file_location('selected_dwell_npz_decoder',KERNEL)
    obj=importlib.util.module_from_spec(spec);sys.modules[spec.name]=obj;spec.loader.exec_module(obj);return obj
def row_dict(m,r): return {m.indices[k]:Q(m.data[k]) for k in range(m.indptr[r],m.indptr[r+1])}
def exact_row(m,r,terms,lo,hi):
    support(row_dict(m,r)==terms and m.row_lower[r]==lo and m.row_upper[r]==hi,'Unexpected actual row '+str(r))

def captured_inputs():
    captured={}
    def add(path,expected=None):
        p=Path(path).resolve();data=p.read_bytes();item=bind(p,data);key=str(p).casefold()
        if expected is not None: need(item==expected,'Historical captured-byte mismatch: '+str(p))
        need(key not in captured or captured[key][1]==item,'Conflicting historical binding')
        captured[key]=(data,item)
    for rel,digest in PINS.items():
        p=ROOT/rel;add(p);need(captured[str(p.resolve()).casefold()][1]['sha256']==digest,'Trusted pin mismatch: '+rel)
    inherited=json.loads(captured[str((OLD/'input_manifest.json').resolve()).casefold()][0])['files']
    need(len(inherited)==71,'Historical premise manifest denominator')
    for item in inherited:add(item['path'],item)
    for p in (Path(__file__),PROTOCOL,KERNEL,ARM/'synthetic_tests.json'):add(p)
    return captured

def prepare():
    started=time.perf_counter();need(not PRE.exists() and not RUN.exists(),'One fresh preparation only')
    captured=captured_inputs();initial=[x[1] for x in captured.values()]
    need(read(ARM/'synthetic_tests.json')['source_sha256']==sha(__file__),'Fixtures belong to another source')
    PRE.mkdir(parents=True)
    save(PRE/'preparation_started.json',dict(utc=utc(),source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),scientific_dp_runs=0,optimizer_calls=0))
    copies=[]
    def copy(source,target):
        data,item=captured[str(source.resolve()).casefold()];target.write_bytes(data)
        need(bind(target)['sha256']==item['sha256'],'Captured copy mismatch');copies.append(dict(original=item,copy=bind(target)))
    for world in WORLDS:
        folder=PRE/world;folder.mkdir()
        for name in ('matrix.npz','bounds.npz','integrality.npz','model_metadata.json','row_metadata.csv.gz'):copy(OLD/world/name,folder/name)
    for name in ('column_maps.json','joint_integrality.npz','gen.csv'):copy(OLD/name,PRE/name)
    copy(OLD/'admission.json',PRE/'capacity_admission.json')
    old=read(PRE/'capacity_admission.json');v=kernel()
    need(old['status']=='PREPARED_PREMISES_ONLY' and old['shared_U_mapping_checked'],'Inherited premise status')
    need(old['tau']==rat(TAU) and old['original_binary_columns']==12096,'Inherited tau/mask')
    support(len(old['tuples'])==1 and old['hour_group']==[0]*168,'Only one static common coefficient tuple is supported')
    fossil=old['fossil_names'];therm=old['thermal_names'];names=old['unit_names']
    need(len(fossil)==23 and len(therm)==24 and len(names)==41,'Inherited roster sizes')
    need(all(n in fossil for n in SELECTED),'Selected units must all be fossil')
    selected_f=[fossil.index(n) for n in SELECTED];selected_t=[therm.index(n) for n in SELECTED]
    remaining=[i for i in range(23) if i not in selected_f]
    group=old['tuples'][0];b,a=group['capacity'],group['cost']
    support(len(a)==len(b)==23 and all(type(x) is int and x>=0 for x in a+b),'Integer nonnegative capacity/cost')
    support(sum(b[i] for i in remaining)<=MAX_CAPACITY,'Remaining cover capacity guard')
    with (PRE/'gen.csv').open(encoding='utf-8-sig',newline='') as f:gen=list(csv.DictReader(f))
    native={x['GEN UID']:x for x in gen};need(len(native)==len(gen),'Unique native labels')
    need([n for n in names if native[n]['Fuel'] in ('Coal','NG','Oil')]==fossil,'Inherited fossil roster/native fuel')
    specs=[]
    for name,fi,ti,expected in zip(SELECTED,selected_f,selected_t,SPEC):
        row=native[name];up=ceil(Q(row['Min Up Time Hr']));down=ceil(Q(row['Min Down Time Hr']))
        support((a[fi],b[fi],up,down)==expected and Q(row['PMin MW'])==a[fi] and Q(row['PMax MW'])==b[fi],'Selected native/nameplate specification')
        support(up>0 and down>0 and 0<TAU<1,'Positive dwell and integral-row tau premise')
        specs.append(dict(uid=name,fossil_index=fi,thermal_index=ti,PMin=a[fi],PMax=b[fi],minimum_up=up,minimum_down=down))
    maps=read(PRE/'column_maps.json');need(maps['worlds']==list(WORLDS),'Original world order')
    jm=v.vector(v.read_npz(PRE/'joint_integrality.npz',('integrality',))['integrality'],('|u1',),33936,'joint mask')
    need(tuple(jm)==tuple(int(6888<=j<18984) for j in range(33936)),'Complete joint original mask')
    world_records=[]
    families=('transition','exclusive_transition','minimum_up','minimum_down')
    for wi,world in enumerate(WORLDS):
        folder=PRE/world;m=v.load_model(folder);meta=read(folder/'model_metadata.json')
        need((m.rows,m.cols,len(m.data))==(34681,23016,145588),'Original world dimensions')
        mask=v.vector(v.read_npz(folder/'integrality.npz',('integrality',))['integrality'],('|u1',),m.cols,'world mask')
        need(tuple(mask)==tuple(int(6888<=j<18984) for j in range(m.cols)),'Full original world mask')
        need(meta['offsets']==dict(P=0,U=6888,Y=10920,Z=14952,theta=18984),'Original coordinate offsets')
        need(meta['unit_names']==names and meta['thermal_unit_names']==therm and meta['fossil_units']==fossil,'Original ordered roster')
        mapping=maps['original_to_joint'][wi]
        need(len(mapping)==23016 and mapping[6888:18984]==list(range(6888,18984)),'All shared state coordinates')
        with gzip.open(folder/'row_metadata.csv.gz','rt',encoding='utf-8-sig',newline='') as f:labels=list(csv.DictReader(f))
        need(len(labels)==m.rows and [int(x['row']) for x in labels]==list(range(m.rows)),'Complete row labels')
        index={}
        for x in labels:
            if x['uid'] in SELECTED and x['family'] in families:
                key=(x['family'],int(x['hour_0based']),x['uid'])
                need(key not in index,'Duplicate selected temporal row');index[key]=int(x['row'])
        support(len(index)==3*167*4,'Selected temporal row denominator')
        checks=[];boxes=[]
        for spec in specs:
            name,k=spec['uid'],spec['thermal_index'];up,down=spec['minimum_up'],spec['minimum_down']
            col=lambda kind,t:meta['offsets'][kind]+24*t+k
            for t in range(168):
                for kind in ('U','Y','Z'):
                    c=col(kind,t);upper=0 if t==0 and kind in ('Y','Z') else 1
                    support(mask[c]==1 and m.lower[c]==0 and m.upper[c]==upper,'Selected exact binary state box')
                    boxes.append(dict(column=c,lower=0,upper=upper))
                if t==0:continue
                equations={
                    'transition':({col('U',t):Q(1),col('U',t-1):Q(-1),col('Y',t):Q(-1),col('Z',t):Q(1)},0.,0.),
                    'exclusive_transition':({col('Y',t):Q(1),col('Z',t):Q(1)},-math.inf,1.),
                    'minimum_up':({**{col('Y',s):Q(1) for s in range(max(1,t-up+1),t+1)},col('U',t):Q(-1)},-math.inf,0.),
                    'minimum_down':({**{col('Z',s):Q(1) for s in range(max(1,t-down+1),t+1)},col('U',t):Q(1)},-math.inf,1.),
                }
                for family,(terms,lo,hi) in equations.items():
                    r=index[(family,t,name)];exact_row(m,r,terms,lo,hi)
                    checks.append(dict(row=r,uid=name,hour=t,family=family,terms=[[c,int(q)] for c,q in sorted(terms.items())],
                        lower=None if lo==-math.inf else int(lo),upper=int(hi)))
        world_records.append(dict(world=world,temporal_rows=checks,state_boxes=boxes,rows_checked=len(checks),boxes_checked=len(boxes)))
    state_bound=math.prod(x['minimum_up']+x['minimum_down'] for x in specs)
    support(state_bound==3328 and 168*state_bound<=MAX_CELLS and 168*state_bound*8<=MAX_EDGES,'Declared state/edge bounds')
    admission=dict(status='PREPARED_NO_SCIENTIFIC_DP',selected=specs,remaining_fossil_indices=remaining,remaining_fossil_names=[fossil[i] for i in remaining],
        remaining_capacity=[b[i] for i in remaining],remaining_cost=[a[i] for i in remaining],worlds=world_records,
        inherited_capacity_premises=bind(PRE/'capacity_admission.json'),tau=rat(TAU),original_binary_columns=12096,
        state_bound=state_bound,hour_state_bound=168*state_bound,candidate_transition_bound=168*state_bound*8,
        integral_expanded_rows_imply_nominal_binary_rows=True,mature_free_initial=True,clipped_terminal=True,
        scientific_dp_runs=0,scientific_threshold_queries=0,optimizer_calls=0)
    save(PRE/'admission.json',admission);save(PRE/'copy_manifest.json',dict(files=copies));validate(initial)
    items={x['path'].casefold():x for x in initial}
    for p in PRE.rglob('*'):
        if p.is_file():items[str(p.resolve()).casefold()]=bind(p)
    manifest=PRE/'input_manifest.json';save(manifest,dict(files=list(items.values())));validate(list(items.values()))
    save(PRE/'prepared_freeze.json',dict(status='PREPARED_NO_SCIENTIFIC_DP',utc=utc(),source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),
        input_manifest=bind(manifest),admission=bind(PRE/'admission.json'),bindings=len(items),copies=len(copies),
        selected_temporal_rows_per_world=2004,selected_state_boxes_per_world=1512,elapsed_seconds=time.perf_counter()-started,
        scientific_dp_runs=0,scientific_threshold_queries=0,optimizer_calls=0))
    print(json.dumps(dict(status='PREPARED',freeze_sha256=sha(PRE/'prepared_freeze.json'),bindings=len(items),copies=len(copies))),flush=True)

def cover_layers(weights,costs,check=lambda:None):
    need(len(weights)==len(costs) and all(type(x) is int and x>=0 for x in weights+costs),'Integer cover input')
    previous=[None]*(sum(weights)+1);previous[0]=0;yield previous.copy()
    for b,a in zip(weights,costs):
        check();current=previous.copy()
        for capacity,value in enumerate(previous):
            if capacity%2048==0:check()
            if value is not None:
                trial=value+a;c=capacity+b
                if c<len(current) and (current[c] is None or trial<current[c]):current[c]=trial
        yield current;previous=current
def suffix_min(values):
    out=[None]*len(values);best=None
    for j in range(len(values)-1,-1,-1):
        if values[j] is not None and (best is None or values[j]<best):best=values[j]
        out[j]=best
    return out
def unit_successors(state,up,down):
    status,lock=state
    continuing=(status,max(0,lock-1))
    return (continuing,) if lock else tuple(sorted((continuing,(1-status,(up if status==0 else down)-1))))
def state_graph(dwells,check=lambda:None):
    labels=list(itertools.product(*[[(status,lock) for status,dwell in ((0,down),(1,up)) for lock in range(dwell)] for up,down in dwells]))
    indexes={s:j for j,s in enumerate(labels)};edges=[]
    for j,state in enumerate(labels):
        if j%128==0:check()
        possible=itertools.product(*(unit_successors(s,up,down) for s,(up,down) in zip(state,dwells)))
        edges.append(sorted(indexes[x] for x in possible))
    patterns=list(itertools.product((0,1),repeat=len(dwells)));pi={p:j for j,p in enumerate(patterns)}
    return labels,edges,patterns,[pi[tuple(s for s,r in label)] for label in labels]
def residence_layers(costs,labels,edges,pattern_ids,check=lambda:None,counter=None):
    previous=[None]*len(labels)
    for j,state in enumerate(labels):
        if all(lock==0 for status,lock in state):previous[j]=costs[0][pattern_ids[j]]
    yield previous
    for t in range(1,len(costs)):
        check();current=[None]*len(labels)
        for j,value in enumerate(previous):
            if j%128==0:check()
            if value is None:continue
            for k in edges[j]:
                if counter is not None:
                    counter['transitions']+=1
                    if counter['transitions']>MAX_EDGES:raise Incomplete('Transition guard exceeded')
                cost=costs[t][pattern_ids[k]]
                if cost is not None:
                    trial=value+cost
                    if current[k] is None or trial<current[k]:current[k]=trial
        yield current;previous=current
def dyadic_scale(values):
    scale=1
    for q in values:
        if q is None:continue
        d=q.denominator;support(d&(d-1)==0,'Non-dyadic exact cost')
        scale=max(scale,d);support(scale.bit_length()<=MAX_DENOM_BITS,'Denominator guard exceeded')
    return scale
def original_sequence_valid(seq,up,down):
    # Independent tiny-fixture check expressed as the original cumulative-window rows.
    y=[0]+[int(seq[t]>seq[t-1]) for t in range(1,len(seq))]
    z=[0]+[int(seq[t]<seq[t-1]) for t in range(1,len(seq))]
    return all(sum(y[max(1,t-up+1):t+1])<=seq[t] and sum(z[max(1,t-down+1):t+1])+seq[t]<=1 for t in range(1,len(seq)))

def self_test():
    need(not (ARM/'synthetic_tests.json').exists(),'One fixture run only');started=time.perf_counter();checks=[]
    for up,down in ((1,1),(2,1),(1,3),(3,2)):
        for horizon in range(1,8):
            for seq in itertools.product((0,1),repeat=horizon):
                reached={(seq[0],0)}
                for t in range(1,horizon):reached={n for state in reached for n in unit_successors(state,up,down) if n[0]==seq[t]}
                need(bool(reached)==original_sequence_valid(seq,up,down),'Automaton/original temporal rows differ')
        checks.append('exhaustive binary sequences h1..7 '+str((up,down)))
    for weights,costs in (([2,3,4],[1,4,2]),([0,2,2],[0,3,1])):
        layers=list(cover_layers(weights,costs))
        for n,row in enumerate(layers):
            expected=[None]*len(row)
            for bits in itertools.product((0,1),repeat=n):
                c=sum(x*b for x,b in zip(bits,weights));a=sum(x*v for x,v in zip(bits,costs))
                if expected[c] is None or a<expected[c]:expected[c]=a
            need(row==expected,'Complete invented cover recurrence')
        suffix=suffix_min(layers[-1])
        for half in range(-2,2*len(suffix)+2):
            h=max(0,ceil(Q(half,2)));got=suffix[h] if h<len(suffix) else None
            candidates=[v for c,v in enumerate(layers[-1]) if v is not None and c>=Q(half,2)]
            need(got==(min(candidates) if candidates else None),'Conditional cover ceiling')
        checks.append('exhaustive cover and rational threshold '+str(weights))
    dwells=((2,2),(2,1));labels,edges,patterns,pids=state_graph(dwells)
    for horizon in range(1,6):
        costs=[[None if (t+p)%7==6 else (t+2)*(p+1)%11-3 for p in range(4)] for t in range(horizon)]
        layers=list(residence_layers(costs,labels,edges,pids));expected=[None]*len(labels)
        for seq in itertools.product(patterns,repeat=horizon):
            if not all(original_sequence_valid([s[j] for s in seq],*dwells[j]) for j in range(2)):continue
            prices=[costs[t][patterns.index(s)] for t,s in enumerate(seq)]
            if any(x is None for x in prices):continue
            # Independently derive final remaining lock from the last observed switch.
            final=[]
            for j,(up,down) in enumerate(dwells):
                switches=[t for t in range(1,horizon) if seq[t][j]!=seq[t-1][j]];status=seq[-1][j]
                lock=max(0,(up if status else down)-(horizon-switches[-1])) if switches else 0
                final.append((status,lock))
            k=labels.index(tuple(final));price=sum(prices)
            if expected[k] is None or price<expected[k]:expected[k]=price
        need(layers[-1]==expected,'Every terminal residence cost versus exhaustive sequences')
    checks.append('two-unit full-state recurrence h1..5 versus exhaustive original-row sequences')
    need(all(x is None for x in list(residence_layers([[None]*4]*2,labels,edges,pids))[-1]),'Empty graph retained')
    need(dyadic_scale([Q(3,8),Q(-1,16),None])==16,'Lossless common dyadic scale')
    for value in (Q(1,3),Q(1,2**256)):
        try:dyadic_scale([value])
        except Unsupported:pass
        else:raise AssertionError('Invalid denominator admitted')
    need(ceil(Q(-1,3))==0 and ceil(Q(1,3))==1 and not Q(2)>Q(2),'Signed ceiling and strict cap equality')
    # An expanded integer residual within tau<1 must be zero (or satisfy nominal upper bound).
    for residual in range(-3,4):
        need((abs(residual)<=TAU)==(residual==0),'Integral expanded equality')
        need((residual<=TAU)==(residual<=0),'Integral expanded inequality')
    checks += ['empty graph','dyadic exact scaling/unsupported denominators','signed ceiling/strict equality','integral tau premise']
    ARM.mkdir(parents=True,exist_ok=True)
    save(ARM/'synthetic_tests.json',dict(status='PASS',utc=utc(),source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),checks=checks,
        scientific_inputs_read=0,scientific_dp_runs=0,optimizer_calls=0,elapsed_seconds=time.perf_counter()-started))
    print(json.dumps(dict(status='PASS_SYNTHETIC_ONLY',checks=len(checks))),flush=True)

def run(expected):
    started=time.perf_counter();need(not RUN.exists(),'One fresh scientific run only')
    fp=PRE/'prepared_freeze.json';need(sha(fp)==expected,'Trusted freeze mismatch');freeze=read(fp)
    need(freeze['source_sha256']==sha(__file__) and freeze['protocol_sha256']==sha(PROTOCOL),'Frozen code mismatch')
    mp=PRE/'input_manifest.json';need(bind(mp)==freeze['input_manifest'],'Frozen manifest mismatch');items=read(mp)['files'];validate(items)
    transport=[bind(fp),bind(mp)];budget(started)
    admission=read(PRE/'admission.json');need(bind(PRE/'admission.json')==freeze['admission'],'Admission binding')
    need(bind(PRE/'capacity_admission.json')==admission['inherited_capacity_premises'],'Inherited premise binding')
    old=read(PRE/'capacity_admission.json');specs=admission['selected']
    RUN.mkdir();save(RUN/'execution_started.json',dict(utc=utc(),freeze_sha256=expected,source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),
        phase_seconds=SECONDS,optimizer_calls=0,selected_units=list(SELECTED),alternative_sets=0,scalar_objectives=1))
    table=RUN/'remaining_cover_layers.jsonl.gz';last=None;count=0
    with table.open('xb') as raw:
        with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as f:
            for layer,row in enumerate(cover_layers(admission['remaining_capacity'],admission['remaining_cost'],lambda:budget(started))):
                f.write((json.dumps(dict(layer=layer,values=row),separators=(',',':'))+'\n').encode());last=row;count+=1
    need(count==21,'Complete remaining-20 recurrence');suffix=suffix_min(last);budget(started)
    save(RUN/'remaining_cover_terminal.json',dict(capacity=admission['remaining_capacity'],cost=admission['remaining_cost'],exact=last,at_least=suffix))
    patterns=list(itertools.product((0,1),repeat=3));queries=[];rational_costs=[];all_fractions=[]
    for t in range(168):
        budget(started);ds=[];deriv=[]
        for world in old['worlds']:
            h=world['hours'][t];need(h['hour']==t and len(h['nonfossil_upper_boxes'])==18 and len(h['fossil_lower_boxes'])==23,'Inherited hour denominator')
            balance=qhex(h['aggregate_lower_hex'])-TAU
            nonfossil=sum((qhex(x['upper_hex'])+TAU for x in h['nonfossil_upper_boxes']),Q(0))
            direct=sum((qhex(x['lower_hex'])-TAU for x in h['fossil_lower_boxes']),Q(0));d=max(balance-nonfossil,direct);ds.append(d)
            deriv.append(dict(world=world['world'],aggregate_lower=rat(balance),nonfossil_upper_sum=rat(nonfossil),direct_fossil_lower=rat(direct),d=rat(d)))
        prices=[];rows=[]
        for pattern in patterns:
            capacity=sum(s*x['PMax'] for s,x in zip(pattern,specs));own=sum(s*x['PMin'] for s,x in zip(pattern,specs))
            threshold=max(ds)-23*TAU-capacity;h=max(0,ceil(threshold));remaining=suffix[h] if h<len(suffix) else None
            floors=None if remaining is None else [max(d,Q(own+remaining)-23*TAU) for d in ds]
            cost=None if floors is None else sum(floors,Q(0));prices.append(cost);all_fractions.append(cost)
            rows.append(dict(pattern=list(pattern),selected_capacity=capacity,selected_cost=own,required_remaining_capacity=rat(threshold),integer_threshold=h,
                remaining_minimum_cost=remaining,world_floors=None if floors is None else [rat(x) for x in floors],sum_cost=None if cost is None else rat(cost)))
        rational_costs.append(prices);queries.append(dict(hour=t,worlds=deriv,patterns=rows))
    cap=sum((qhex(x['cap_upper_hex'])+TAU for x in old['worlds']),Q(0));all_fractions.append(cap)
    scale=dyadic_scale(all_fractions);costs=[]
    for row in rational_costs:
        scaled=[]
        for value in row:
            if value is None:scaled.append(None)
            else:
                q=value*scale;need(q.denominator==1,'Lossless scaled cost');scaled.append(q.numerator)
        costs.append(scaled)
    save(RUN/'conditional_hourly_costs.json',dict(tau=rat(TAU),scale=str(scale),hours=queries,scaled_sum_costs=costs,combined_cap=rat(cap)));budget(started)
    dwells=[(x['minimum_up'],x['minimum_down']) for x in specs]
    labels,edges,ps,pids=state_graph(dwells,lambda:budget(started));need(ps==patterns and len(labels)==admission['state_bound'],'Frozen state denominator')
    save(RUN/'residence_state_graph.json',dict(selected_units=list(SELECTED),dwells=dwells,labels=labels,successors=edges,patterns=patterns,pattern_ids=pids,
        initial_state_ids=[j for j,s in enumerate(labels) if all(lock==0 for status,lock in s)],terminal_acceptance='all_states_even_if_locked'))
    budget(started);counter=dict(transitions=0);layers=0;finite=[];cells=0;last=None
    path=RUN/'residence_layers.jsonl.gz'
    with path.open('xb') as raw:
        with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as f:
            for t,values in enumerate(residence_layers(costs,labels,edges,pids,lambda:budget(started),counter)):
                cells+=len(values)
                if cells>MAX_CELLS:raise Incomplete('Archived state-value guard exceeded')
                f.write((json.dumps(dict(hour=t,values=values),separators=(',',':'))+'\n').encode());layers+=1;finite.append(sum(v is not None for v in values));last=values;budget(started)
    need(layers==168 and cells==559104,'Full scientific hour-state denominator')
    possible=[x for x in last if x is not None];lower=None if not possible else Q(min(possible),scale)
    negative=lower is None or lower>cap
    save(RUN/'result.json',dict(status='UNIVERSAL_COMMON_REJECTION_PENDING_REVIEW' if negative else 'NO_REJECTION_FROM_THIS_BOUND',
        empty_final_graph=not bool(possible),summed_world_energy_floor=None if lower is None else rat(lower),combined_expanded_cap=rat(cap),
        floor_minus_cap=None if lower is None else rat(lower-cap),selected_units=list(SELECTED),selection_posthoc_census_guided=True,
        table_layers=21,conditional_queries=1344,residence_layers=layers,state_labels=len(labels),archived_state_values=cells,
        transition_checks=counter['transitions'],reachable_states_per_hour=finite,scale=str(scale),optimizer_calls=0,new_full_schedule_candidates=0,
        original_question='PENDING_INDEPENDENT_PROOF_REVIEW' if negative else 'UNKNOWN',not_a_dispatch_or_causal_attribution=True,requires_successful_completion_record=True))
    validate(items);validate(transport);budget(started)
    save(RUN/'completion.json',dict(status='COMPLETE',utc=utc(),all_inputs_and_transport_unchanged=True,elapsed_seconds=time.perf_counter()-started,
        phase_limit_seconds=SECONDS,final_completion_write_excluded_from_elapsed_sample=True,optimizer_calls=0,scientific_runs=1,conditional_queries=1344,residence_layers=168))
    print(json.dumps(dict(status='COMPLETE',negative_pending_review=negative,lower=None if lower is None else rat(lower),cap=rat(cap))),flush=True)

def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--self-test',action='store_true');g.add_argument('--prepare-only',action='store_true');g.add_argument('--run-prepared',action='store_true');p.add_argument('--expected-freeze-sha256');args=p.parse_args()
    try:
        if args.self_test:self_test()
        elif args.prepare_only:prepare()
        else:need(bool(args.expected_freeze_sha256),'Explicit trusted freeze required');run(args.expected_freeze_sha256)
    except BaseException as exc:
        folder=RUN if RUN.exists() else PRE if PRE.exists() else ARM;folder.mkdir(parents=True,exist_ok=True)
        if not (folder/'failure.json').exists():save(folder/'failure.json',dict(status='UNSUPPORTED' if isinstance(exc,Unsupported) else 'INCOMPLETE' if isinstance(exc,Incomplete) else 'ERROR',utc=utc(),error_type=type(exc).__name__,message=str(exc),optimizer_calls=0,no_retry=True,no_scientific_verdict=True))
        raise

if __name__=='__main__':main()
