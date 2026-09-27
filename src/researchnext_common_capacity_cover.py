"""Exact universal common-state capacity-cover floor; no optimization backend."""
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
ARM = ROOT/'results/research_next/common_capacity_cover'
PRE = ARM/'prepared'
RUN = ARM/'run01'
OLD = ROOT/'results/research_next/common_commitment/prepared'
PROTOCOL = ROOT/'docs/research_next/COMMON_CAPACITY_COVER_PROTOCOL.md'
DESIGN = ROOT/'docs/research_next/COMMON_CAPACITY_COVER_BOUND_DESIGN.md'
KERNEL = ROOT/'src/research8h_standalone_verify.py'
KERNEL_SHA = '708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'
TAU = Q.from_float(1e-5)
SECONDS = 120.0
MAX_CAPACITY = 100000
MAX_TUPLES = 168
WORLDS = ('identity', 'days_321')
PINS = {
 'results/research_next/common_commitment/prepared/prepared_freeze.json': '4f21891d7d1f1793dd92e5b830edf5b5cf62474e5521d788c9aec17929ea9a59',
 'results/research_next/common_commitment/prepared/input_manifest.json': '8ff99b1f4450ac15e91b26a261a85c98d574bbbdac3f7fe149efd9fd07204a5c',
 'results/research_next/common_commitment/INDEPENDENT_PREPARED_REVIEW.json': '956b37cbcdd49571a6a79611da197a5be840a5c2747ffbd60576c90805d58e6b',
 'results/research_next/common_commitment/INDEPENDENT_POSTRUN_REVIEW.json': 'f442edeb3f90c5d602a1b60cdef1b96b4d560ebbe97fae28c4ca21c6077eadba',
 'docs/research_next/COMMON_CAPACITY_COVER_BOUND_DESIGN.md': '1292887f44b46eae60093620c4b062c4b9842d01c1852bb0d8f86c4aba9f6993',
}

class Unsupported(ValueError): pass
class Incomplete(RuntimeError): pass
def need(ok, message):
    if not ok: raise ValueError(message)
def support(ok, message):
    if not ok: raise Unsupported(message)
def utc(): return datetime.now(timezone.utc).isoformat()
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def save(path, value):
    with Path(path).open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2, allow_nan=False); f.write('\n')
def bind(path, data=None):
    p=Path(path).resolve(); b=p.read_bytes() if data is None else data
    return dict(path=str(p), bytes=len(b), sha256=hashlib.sha256(b).hexdigest())
def validate(items):
    need(len({x['path'].casefold() for x in items})==len(items), 'Duplicate binding')
    for x in items: need(bind(x['path'])==x, 'Changed binding: '+x['path'])
def rat(q): return dict(numerator=str(q.numerator), denominator=str(q.denominator), approximate=float(q))
def qhex(value):
    q=float.fromhex(value); need(math.isfinite(q), 'Nonfinite saved endpoint'); return Q(q)
def budget(start):
    if time.perf_counter()-start >= SECONDS: raise Incomplete('120-second soft calculation phase exceeded')
def kernel():
    need(sha(KERNEL)==KERNEL_SHA, 'Pinned decoder changed')
    spec=importlib.util.spec_from_file_location('capacity_cover_npz_decoder', KERNEL)
    v=importlib.util.module_from_spec(spec); sys.modules[spec.name]=v; spec.loader.exec_module(v); return v
def load_mask(v, folder, cols):
    a=v.read_npz(folder/'integrality.npz', ('integrality',))['integrality']
    m=v.vector(a, ('|u1',), cols, 'original integrality')
    need(all(x in (0,1) for x in m), 'Nonbinary mask entry'); return m
def exact_integer(value, label):
    support(math.isfinite(value) and Q(value).denominator==1 and value>=0, 'Unsupported noninteger/negative '+label)
    return int(value)
def ceiling(q): return -((-q.numerator)//q.denominator)
def row_dict(m, r): return {m.indices[k]:Q(m.data[k]) for k in range(m.indptr[r],m.indptr[r+1])}
def exact_row(m, r, expected, lo, hi):
    support(row_dict(m,r)==expected and m.row_lower[r]==lo and m.row_upper[r]==hi, 'Unsupported actual row pattern/endpoints '+str(r))
def shared_tuple(left, right):
    support(left==right, 'Fossil coefficient tuple differs between worlds')
    b,a=left
    support(len(b)==len(a)==23 and all(type(x) is int and x>=0 for x in b+a), 'Unsupported 23-item integer roster')
    support(sum(b)<=MAX_CAPACITY, 'Capacity grid exceeds fixed guard')
    return tuple(b),tuple(a)

def captured_inputs():
    captured={}
    def add(p, expected=None):
        p=p.resolve(); b=p.read_bytes(); item=bind(p,b)
        if expected is not None: need(item==expected, 'Historical input mismatch: '+str(p))
        key=str(p).casefold()
        need(key not in captured or captured[key][1]==item, 'Conflicting historical binding')
        captured[key]=(b,item)
    for rel,digest in PINS.items():
        p=ROOT/rel; add(p); need(captured[str(p.resolve()).casefold()][1]['sha256']==digest, 'Trusted pin mismatch '+rel)
    old=json.loads(captured[str((OLD/'input_manifest.json').resolve()).casefold()][0])['files']
    need(len(old)==48, 'Historical manifest denominator')
    for item in old: add(Path(item['path']), item)
    for p in (Path(__file__), PROTOCOL, KERNEL): add(p)
    need(sha(KERNEL)==KERNEL_SHA, 'Decoder pin')
    return captured

def prepare():
    start=time.perf_counter()
    need(not PRE.exists() and not RUN.exists(), 'Single fresh preparation only')
    captured=captured_inputs(); initial=[x[1] for x in captured.values()]
    PRE.mkdir(parents=True)
    save(PRE/'preparation_started.json', dict(utc=utc(), source_sha256=sha(__file__), protocol_sha256=sha(PROTOCOL), optimizer_calls=0, scientific_dp_tables=0))
    v=kernel(); copies=[]
    def copy(p,dest):
        b,item=captured[str(p.resolve()).casefold()]; dest.write_bytes(b)
        need(bind(dest)['sha256']==item['sha256'], 'Captured copy mismatch')
        copies.append(dict(original=item, copy=bind(dest)))
    for world in WORLDS:
        folder=PRE/world; folder.mkdir()
        for name in ('matrix.npz','bounds.npz','integrality.npz','model_metadata.json','row_metadata.csv.gz'):
            copy(OLD/world/name, folder/name)
    copy(OLD/'joint/column_maps.json', PRE/'column_maps.json')
    copy(OLD/'joint/integrality.npz', PRE/'joint_integrality.npz')
    copy(OLD/'gen.csv', PRE/'gen.csv')
    maps=read(PRE/'column_maps.json')
    need(maps['worlds']==list(WORLDS) and len(maps['original_to_joint'])==2, 'Original world maps')
    for mapping in maps['original_to_joint']:
        need(len(mapping)==23016 and all(type(x) is int and 0<=x<33936 for x in mapping), 'World column map shape')
        need(mapping[6888:18984]==list(range(6888,18984)), 'Shared all original UYZ coordinates')
    jm=v.vector(v.read_npz(PRE/'joint_integrality.npz',('integrality',))['integrality'],('|u1',),33936,'joint original mask')
    need(tuple(jm)==tuple(int(6888<=j<18984) for j in range(33936)), 'Original joint full state declarations')
    with (PRE/'gen.csv').open(encoding='utf-8-sig',newline='') as f: gen=list(csv.DictReader(f))
    need(len({x['GEN UID'] for x in gen})==len(gen), 'Duplicate native generator name')
    native={x['GEN UID']:x for x in gen}; world_records=[]; all_tuples=[]; common_names=None
    for world in WORLDS:
        folder=PRE/world; m=v.load_model(folder); meta=read(folder/'model_metadata.json')
        need((m.rows,m.cols,len(m.data))==(34681,23016,145588), 'Original world dimensions')
        bits=load_mask(v,folder,m.cols)
        need(tuple(bits)==tuple(int(6888<=j<18984) for j in range(m.cols)), 'Original world complete integer mask')
        names=meta['unit_names']; therm=meta['thermal_unit_names']; fossil=meta['fossil_units']
        need(len(names)==len(set(names))==41 and len(therm)==len(set(therm))==24 and len(fossil)==len(set(fossil))==23, 'Unique native roster sizes')
        need(set(therm)<=set(names) and set(fossil)<set(therm), 'Fossil/thermal membership')
        need([n for n in names if native[n]['Fuel'] in ('Coal','NG','Oil')]==fossil, 'Original fossil fuel roster')
        need(set(therm)-set(fossil)=={'121_NUCLEAR_1'} and native['121_NUCLEAR_1']['Fuel']=='Nuclear', 'Nuclear exclusion')
        need(meta['offsets']==dict(P=0,U=6888,Y=10920,Z=14952,theta=18984), 'Original coordinate offsets')
        if common_names is None: common_names=(names,therm,fossil)
        else: need(common_names==(names,therm,fossil), 'Same ordered original rosters')
        fi=[names.index(n) for n in fossil]; ni=[j for j in range(41) if j not in fi]
        with gzip.open(folder/'row_metadata.csv.gz','rt',encoding='utf-8-sig',newline='') as f: labels=list(csv.DictReader(f))
        need(len(labels)==m.rows and [int(x['row']) for x in labels]==list(range(m.rows)), 'Full metadata row denominator')
        index={}
        for label in labels:
            family=label['family']
            if family not in ('thermal_upper','thermal_lower','aggregate_balance','fossil_energy_cap'): continue
            key=(family,int(label['hour_0based']),label['uid'])
            need(key not in index,'Duplicate selected family key');index[key]=int(label['row'])
        support(len(index)==2*24*168+168+1, 'Selected row family denominator')
        cap_candidates=[r for (fam,t,n),r in index.items() if fam=='fossil_energy_cap']
        need(len(cap_candidates)==1,'Unique cap');cap=cap_candidates[0]
        exact_row(m,cap,{41*t+j:Q(1) for t in range(168) for j in fi},-math.inf,23195.)
        hours=[]; tuples=[]
        for t in range(168):
            ar=index[('aggregate_balance',t,'ALL')]
            expected={41*t+j:Q(1) for j in range(41)}
            support(row_dict(m,ar)==expected and math.isfinite(m.row_lower[ar]) and m.row_lower[ar]==m.row_upper[ar], 'Actual aggregate equality')
            minimum={};maximum={};thermal_sources=[]
            for k,name in enumerate(therm):
                j=names.index(name);p=41*t+j;u=6888+24*t+k
                support(m.lower[u]==0 and m.upper[u]==1, 'Original U binary bounds')
                ru=index[('thermal_upper',t,name)];rl=index[('thermal_lower',t,name)]
                upper=row_dict(m,ru);lower=row_dict(m,rl)
                support(upper.get(p)==1 and lower.get(p)==-1,'Thermal generation coefficients')
                b=exact_integer(float(-upper.get(u,Q(0))), 'capacity')
                a=exact_integer(float(lower.get(u,Q(0))), 'minimum output')
                exact_row(m,ru,{p:Q(1),**({u:Q(-b)} if b else {})},-math.inf,0.)
                exact_row(m,rl,{p:Q(-1),**({u:Q(a)} if a else {})},-math.inf,0.)
                support(a<=b, 'Inverted thermal native range')
                support(Q(native[name]['PMax MW'])==b and Q(native[name]['PMin MW'])==a, 'Native nameplate/actual row coefficient correspondence')
                minimum[name]=a;maximum[name]=b
                thermal_sources.append(dict(uid=name,P_column=p,U_column=u,lower_row=rl,upper_row=ru,PMin=a,PMax=b))
            pair=(tuple(maximum[n] for n in fossil),tuple(minimum[n] for n in fossil));tuples.append(pair)
            hours.append(dict(hour=t,aggregate_row=ar,aggregate_lower_hex=m.row_lower[ar].hex(),
                nonfossil_upper_boxes=[dict(column=41*t+j,upper_hex=m.upper[41*t+j].hex()) for j in ni],
                fossil_lower_boxes=[dict(column=41*t+j,lower_hex=m.lower[41*t+j].hex()) for j in fi],
                thermal_sources=thermal_sources))
        all_tuples.append(tuples)
        world_records.append(dict(world=world,cap_row=cap,cap_upper_hex=m.row_upper[cap].hex(),hours=hours))
    groups=[];hour_group=[]
    for t in range(168):
        pair=shared_tuple(all_tuples[0][t],all_tuples[1][t])
        if pair not in groups: groups.append(pair)
        support(len(groups)<=MAX_TUPLES,'Distinct tuple guard')
        hour_group.append(groups.index(pair))
    admission=dict(status='PREPARED_PREMISES_ONLY',worlds=world_records,unit_names=common_names[0],thermal_names=common_names[1],fossil_names=common_names[2],
        tuples=[dict(group=k,capacity=list(b),cost=list(a),sum_capacity=sum(b)) for k,(b,a) in enumerate(groups)],hour_group=hour_group,
        tau=rat(TAU),original_binary_columns=12096,original_rows_per_world=34681,
        selected_thermal_rows_per_world=8064,shared_U_mapping_checked=True,old_joint_assembly_inherited=True,
        scientific_dp_tables=0,scientific_threshold_queries=0,optimizer_calls=0)
    save(PRE/'admission.json',admission);save(PRE/'copy_manifest.json',dict(files=copies))
    validate(initial)
    items={x['path'].casefold():x for x in initial}
    for p in PRE.rglob('*'):
        if p.is_file():items[str(p.resolve()).casefold()]=bind(p)
    manifest=PRE/'input_manifest.json';save(manifest,dict(files=list(items.values())))
    validate(list(items.values()))
    save(PRE/'prepared_freeze.json',dict(status='PREPARED_NO_SCIENTIFIC_DP',utc=utc(),source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),
        input_manifest=bind(manifest),bindings=len(items),admission=bind(PRE/'admission.json'),copies=len(copies),distinct_tuples=len(groups),
        scientific_dp_tables=0,scientific_threshold_queries=0,optimizer_calls=0,elapsed_seconds=time.perf_counter()-start))
    print(json.dumps(dict(status='PREPARED',freeze_sha256=sha(PRE/'prepared_freeze.json'),bindings=len(items),distinct_tuples=len(groups))),flush=True)

def dp_layers(weights,costs,check=lambda:None):
    """Full exact-capacity recurrence; None means unreachable, never infinity arithmetic."""
    need(len(weights)==len(costs) and all(type(x) is int and x>=0 for x in weights+costs),'Integer DP input')
    total=sum(weights); previous=[None]*(total+1);previous[0]=0
    yield previous.copy()
    for b,a in zip(weights,costs):
        check();current=previous.copy()
        for c,value in enumerate(previous):
            if c%2048==0:check()
            if value is not None and c+b<=total:
                trial=value+a
                if current[c+b] is None or trial<current[c+b]:current[c+b]=trial
        yield current
        previous=current
def suffix_costs(last,check=lambda:None):
    out=[None]*len(last);best=None
    for c in range(len(last)-1,-1,-1):
        if c%2048==0:check()
        x=last[c]
        if x is not None and (best is None or x<best):best=x
        out[c]=best
    return out
def read_minimum(suffix,threshold):
    h=max(0,ceiling(threshold))
    return h, suffix[h] if h<len(suffix) else None

def self_test():
    need(not (ARM/'synthetic_tests.json').exists(),'One fixture execution only')
    started=time.perf_counter();checks=[]
    for weights,costs in [([2,3,4],[1,4,2]),([0,2,2],[0,3,1]),([5],[2]),([],[])]:
        layers=list(dp_layers(weights,costs))
        for k,row in enumerate(layers):
            expected=[None]*len(row)
            for bits in itertools.product((0,1),repeat=k):
                c=sum(b*w for b,w in zip(bits,weights));a=sum(b*w for b,w in zip(bits,costs))
                if expected[c] is None or a<expected[c]:expected[c]=a
            need(row==expected,'Invented exhaustive full recurrence mismatch')
        suf=suffix_costs(layers[-1])
        for n in range(-2,2*len(suf)+3):
            q=Q(n,2);h,m=read_minimum(suf,q)
            values=[v for c,v in enumerate(layers[-1]) if v is not None and c>=q]
            need(m==(min(values) if values else None),'Invented threshold/exhaustive mismatch')
        checks.append('exhaustive prefix tables and half-integer thresholds '+str(weights))
    need(ceiling(Q(1,3))==1 and ceiling(Q(-1,3))==0 and ceiling(Q(3))==3,'Exact ceiling')
    need(read_minimum(suffix_costs(list(dp_layers([2],[2]))[-1]),Q(1))==(1,2),'Integer jump over fractional cost 1')
    need(not Q(3)>Q(3) and Q(3)+TAU>Q(3),'Strict endpoint comparison')
    checks += ['exact signed ceiling','integer-cover strict strengthening','strict cap equality']
    for x,y in [(([1]*23,[1]*23),([2]*23,[1]*23)),(([1]*22,[1]*22),([1]*22,[1]*22)),(([100001]*23,[0]*23),([100001]*23,[0]*23))]:
        try:shared_tuple(x,y)
        except Unsupported:checks.append('unsupported tuple/roster/guard rejected')
        else:raise AssertionError('Unsupported invented tuple admitted')
    class Toy:
        indices=(0,1);data=(1.,-2.);indptr=(0,2);row_lower=(-math.inf,);row_upper=(0.,)
    exact_row(Toy(),0,{0:Q(1),1:Q(-2)},-math.inf,0.)
    try:exact_row(Toy(),0,{0:Q(1),2:Q(-2)},-math.inf,0.)
    except Unsupported:checks.append('wrong actual thermal coordinate rejected')
    else:raise AssertionError('Malformed invented row admitted')
    ARM.mkdir(parents=True,exist_ok=True)
    save(ARM/'synthetic_tests.json',dict(status='PASS',utc=utc(),source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),checks=checks,
        scientific_inputs_read=0,scientific_dp_tables=0,optimizer_calls=0,elapsed_seconds=time.perf_counter()-started))
    print(json.dumps(dict(status='PASS_SYNTHETIC_ONLY',checks=len(checks))),flush=True)

def run(expected):
    started=time.perf_counter();need(not RUN.exists(),'One fresh calculation only')
    freeze_path=PRE/'prepared_freeze.json';need(sha(freeze_path)==expected,'Externally supplied freeze mismatch')
    freeze=read(freeze_path);need(sha(__file__)==freeze['source_sha256'] and sha(PROTOCOL)==freeze['protocol_sha256'],'Frozen source/protocol mismatch')
    manifest=PRE/'input_manifest.json';need(bind(manifest)==freeze['input_manifest'],'Frozen manifest mismatch')
    items=read(manifest)['files'];validate(items);budget(started)
    transport=[bind(freeze_path),bind(manifest)]
    admission=read(PRE/'admission.json');need(bind(PRE/'admission.json')==freeze['admission'],'Admission binding')
    RUN.mkdir();save(RUN/'execution_started.json',dict(utc=utc(),freeze_sha256=expected,source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),
        optimizer_calls=0,phase_seconds=SECONDS,max_sum_capacity=MAX_CAPACITY,max_distinct_tuples=MAX_TUPLES))
    cache=[];table_records=[]
    for group in admission['tuples']:
        budget(started);w=group['capacity'];a=group['cost'];support(len(w)==len(a)==23 and sum(w)<=MAX_CAPACITY,'Prepared DP scope')
        path=RUN/('dp_group_'+str(group['group'])+'.jsonl.gz');layers=0;finite=[];last=None
        with path.open('xb') as raw:
            with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as f:
                for layer,values in enumerate(dp_layers(w,a,lambda:budget(started))):
                    f.write((json.dumps(dict(layer=layer,values=values),separators=(',',':'))+'\n').encode())
                    layers+=1;finite.append(sum(v is not None for v in values));last=values
        need(layers==24,'Complete 23-item recurrence');budget(started)
        suffix=suffix_costs(last,lambda:budget(started));cache.append(suffix)
        terminal=RUN/('terminal_group_'+str(group['group'])+'.json')
        save(terminal,dict(group=group['group'],capacity=w,cost=a,terminal_exact_capacity_cost=last,terminal_at_least_capacity_cost=suffix))
        table_records.append(dict(group=group['group'],layers=layers,states_per_layer=len(last),finite_states_per_layer=finite,recurrence=bind(path),terminal=bind(terminal)))
        budget(started)
    need(len(cache)==len(admission['tuples'])<=MAX_TUPLES,'DP table denominator')
    world_hours=[x['hours'] for x in admission['worlds']];totals=[Q(0),Q(0)];queries=[];no_cover=[]
    for t in range(168):
        budget(started);deriv=[];ds=[]
        for wi in range(2):
            h=world_hours[wi][t];need(h['hour']==t,'Prepared hour order')
            balance=qhex(h['aggregate_lower_hex'])-TAU
            nonfossil=sum((qhex(x['upper_hex'])+TAU for x in h['nonfossil_upper_boxes']),Q(0))
            direct=sum((qhex(x['lower_hex'])-TAU for x in h['fossil_lower_boxes']),Q(0))
            need(len(h['nonfossil_upper_boxes'])==18 and len(h['fossil_lower_boxes'])==23,'Hourly selected box denominator')
            d=max(balance-nonfossil,direct);ds.append(d)
            deriv.append(dict(world=WORLDS[wi],aggregate_lower=rat(balance),nonfossil_upper_sum=rat(nonfossil),direct_fossil_lower=rat(direct),d=rat(d)))
        group=admission['hour_group'][t];H=max(ds)-23*TAU;h,M=read_minimum(cache[group],H)
        if M is None:no_cover.append(t)
        else:
            for wi in range(2):
                floor=max(ds[wi],Q(M)-23*TAU);totals[wi]+=floor;deriv[wi]['selected_floor']=rat(floor)
        queries.append(dict(hour=t,group=group,required_capacity=rat(H),integer_threshold=h,minimum_committed_output=M,worlds=deriv))
    results=[]
    for wi,world in enumerate(admission['worlds']):
        cap=qhex(world['cap_upper_hex'])+TAU
        results.append(dict(world=world['world'],expanded_cap=rat(cap),energy_floor=None if no_cover else rat(totals[wi]),
            floor_minus_cap=None if no_cover else rat(totals[wi]-cap),cap_rejected=False if no_cover else totals[wi]>cap))
    negative=bool(no_cover or any(x['cap_rejected'] for x in results))
    save(RUN/'tables.json',dict(tables=table_records));save(RUN/'hourly_queries.json',dict(hours=queries))
    save(RUN/'result.json',dict(status='UNIVERSAL_COMMON_REJECTION_PENDING_REVIEW' if negative else 'NO_REJECTION_FROM_THIS_BOUND',
        no_capacity_cover_hours=no_cover,worlds=results,optimizer_calls=0,tau=rat(TAU),new_schedule_candidates=0,
        scientific_dp_tables=len(cache),scientific_threshold_queries=168,not_dwell_or_network_attribution=True,
        original_question='PENDING_INDEPENDENT_PROOF_REVIEW' if negative else 'UNKNOWN',requires_successful_completion_record=True))
    validate(items);validate(transport);budget(started)
    save(RUN/'completion.json',dict(status='COMPLETE',utc=utc(),optimizer_calls=0,distinct_dp_tables=len(cache),threshold_queries=168,
        all_inputs_and_transport_unchanged=True,elapsed_seconds=time.perf_counter()-started,phase_limit_seconds=SECONDS,
        final_completion_write_excluded_from_elapsed_sample=True))
    print(json.dumps(dict(status='COMPLETE',negative_pending_review=negative,worlds=results)),flush=True)

def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--self-test',action='store_true');g.add_argument('--prepare-only',action='store_true');g.add_argument('--run-prepared',action='store_true')
    p.add_argument('--expected-freeze-sha256');a=p.parse_args()
    try:
        if a.self_test:self_test()
        elif a.prepare_only:prepare()
        else:need(bool(a.expected_freeze_sha256),'Explicit trusted freeze required');run(a.expected_freeze_sha256)
    except BaseException as exc:
        folder=RUN if RUN.exists() else PRE if PRE.exists() else ARM
        folder.mkdir(parents=True,exist_ok=True)
        if not (folder/'failure.json').exists():
            save(folder/'failure.json',dict(status='UNSUPPORTED' if isinstance(exc,Unsupported) else 'INCOMPLETE' if isinstance(exc,Incomplete) else 'ERROR',
                utc=utc(),error_type=type(exc).__name__,message=str(exc),optimizer_calls=0,no_retry=True,no_scientific_verdict=True))
        raise

if __name__=='__main__':main()
