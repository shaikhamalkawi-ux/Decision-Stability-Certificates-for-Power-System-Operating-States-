"""Independent exact semantic comparison of one raw native MOI export; no solver."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import time

ROOT = Path(__file__).resolve().parents[1]
ARM = ROOT/'results/research_next/orlib_native_compare_schema2'
PRE = ARM/'prepared'
RUN = ARM/'run01'
PROTOCOL = ROOT/'docs/research_next/ORLIB_NATIVE_COMPARE_SCHEMA2_PROTOCOL.md'
HISTORY = ROOT/'results/research_next/orlib_native_compare'
ORIGINAL_SOURCE = ROOT/'src/researchnext_orlib_native_compare.py'
ORIGINAL_PROTOCOL = ROOT/'docs/research_next/ORLIB_NATIVE_COMPARE_PROTOCOL.md'
OFFICIAL = ROOT/'results/research_next/orlib_julia_export/official_export_reuse01'
OLD = ROOT/'results/research_next/orlib_preflight/solver_prepared01/inputs'
MODEL_SHA = '5abc7c12289d6428081f49646553863abaa041abfd4bac6215d7d49130b2f725'
CASE_SHA = 'be57cd1fd925fb5c106b8e90979dcc866c0b27068b368ec018e4068d03067df8'

def need(ok, why):
    if not ok: raise ValueError(why)
def utc(): return datetime.now(timezone.utc).isoformat()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p, x):
    with Path(p).open('x', encoding='utf-8') as f:
        json.dump(x, f, indent=2, allow_nan=False); f.write('\n')
def binding(p):
    p=Path(p).resolve(); b=p.read_bytes()
    return dict(path=str(p), bytes=len(b), sha256=hashlib.sha256(b).hexdigest())
def validate(items):
    for b in items: need(binding(b['path'])==b, 'Input changed: '+b['path'])
def rq(x): return [str(x.numerator), str(x.denominator)] if x is not None else None
def qp(x):
    need(type(x) in (int,float) and math.isfinite(x), 'Expected finite Python numeric')
    return Q(x)
def native(x):
    if isinstance(x,dict):
        need(set(x)=={'type','bits_hex','display'} and x['type']=='Float64', 'Unsupported exact native value')
        need(re.fullmatch('[0-9a-f]{16}', x['bits_hex']) is not None, 'Float64 bit representation')
        v=struct.unpack('>d', bytes.fromhex(x['bits_hex']))[0]
        need(math.isfinite(v), 'Unexpected nonfinite native value')
        return Q(v)
    if isinstance(x,list): return [native(v) for v in x]
    if type(x) is int: return Q(x)
    need(type(x) in (bool,str) or x is None, 'Unsupported native literal')
    return x
def canon(coeff, lower, upper):
    c=tuple(sorted((name,value) for name,value in coeff.items() if value))
    if c and c[0][1]<0:
        c=tuple((name,-value) for name,value in c)
        lower,upper=((-upper if upper is not None else None),(-lower if lower is not None else None))
    return c,lower,upper
def row_json(key):
    c,lo,hi=key
    return dict(coefficients=[[n,rq(q)] for n,q in c], lower=rq(lo), upper=rq(hi))
def signature_hash(keys):
    values=sorted((json.dumps(row_json(k),sort_keys=True,separators=(',',':')),v) for k,v in keys.items())
    return hashlib.sha256(json.dumps(values,separators=(',',':')).encode()).hexdigest()

def alias_name(family, key, scenario, bus, reserve, units):
    need(isinstance(key,list), 'Semantic key must be tuple/list')
    states={'is_on':'U','switch_on':'Y','switch_off':'Z'}
    if family in states:
        need(len(key)==2 and key[0] in units and type(key[1]) is int and 1<=key[1]<=24, 'State alias')
        return f'{states[family]}:{key[0]}:{key[1]-1}'
    if family=='startup':
        need(len(key)==3 and key[0] in units and type(key[1]) is int and 1<=key[1]<=24 and key[2]==1, 'Single startup alias')
        return f'D:{key[0]}:{key[1]-1}'
    need(key and key[0]==scenario, 'Scenario alias')
    if family in ('prod_above','mfg'):
        need(len(key)==3 and key[1] in units and type(key[2]) is int and 1<=key[2]<=24, 'Production alias')
        return f'{"Q" if family=="prod_above" else "mfg"}:{key[1]}:{key[2]-1}'
    if family=='reserve':
        need(len(key)==4 and key[1]==reserve and key[2] in units and type(key[3]) is int and 1<=key[3]<=24, 'Reserve alias')
        return f'R:{key[2]}:{key[3]-1}'
    if family=='segprod':
        need(len(key)==4 and key[1] in units and type(key[2]) is int and 1<=key[2]<=24 and type(key[3]) is int and 1<=key[3]<=4, 'Segment alias')
        return f'S:{key[1]}:{key[2]-1}:{key[3]-1}'
    if family in ('curtail','net_injection','reserve_shortfall'):
        need(len(key)==3 and key[1]==(reserve if family=='reserve_shortfall' else bus) and type(key[2]) is int and 1<=key[2]<=24, 'System alias')
        return f'{dict(curtail="C",net_injection="N",reserve_shortfall="F")[family]}:system:{key[2]-1}'
    raise ValueError('Unsupported native variable family: '+family)

def set_bounds(s):
    kind=s['type']
    if kind=='MathOptInterface.EqualTo{Float64}':
        v=native(s['value']); return v,v
    if kind=='MathOptInterface.LessThan{Float64}': return None,native(s['upper'])
    if kind=='MathOptInterface.GreaterThan{Float64}': return native(s['lower']),None
    if kind=='MathOptInterface.Interval{Float64}': return native(s['lower']),native(s['upper'])
    raise ValueError('Unsupported bound set: '+kind)
def affine(f, names):
    need(f['type']=='MathOptInterface.ScalarAffineFunction{Float64}', 'Unsupported affine type')
    c=defaultdict(Q)
    for t in f['terms']:
        need(t['variable'] in names, 'Unknown term variable')
        c[names[t['variable']]]+=native(t['coefficient'])
    return {n:a for n,a in c.items() if a},native(f['constant'])

def compare_parsed(p, n):
    differences=[]
    def check(label, actual, expected):
        if actual!=expected: differences.append(dict(field=label,actual=repr(actual),expected=repr(expected)))
    check('horizon',p['time'],24); check('scenario_time',p['scenario_time'],24)
    check('scenario_name',p['scenario_name'],'s1')
    check('native_default_read_and_repair',p['native_default_read_and_repair'],True)
    check('time_step_minutes',p['time_step_minutes'],60)
    check('probability',native(p['probability']),Q(1))
    check('power_balance_penalty',native(p['power_balance_penalty']),list(map(qp,n['penalty'])))
    need(len(p['buses'])==len(p['reserves'])==1, 'Single native bus/reserve')
    check('bus',p['buses'][0]['name'],n['bus']);check('load',native(p['buses'][0]['load']),list(map(qp,n['load'])))
    r=p['reserves'][0];check('reserve_name',r['name'],n['reserve_name']);check('reserve_type',r['type'],'spinning')
    check('reserve_amount',native(r['amount']),list(map(qp,n['reserve'])));check('shortfall_penalty',native(r['shortfall_penalty']),Q(-1))
    ns={g['name']:g for g in n['units']};ps={g['name']:g for g in p['thermal_units']}
    need(len(ns)==len(ps)==10 and set(ns)==set(ps), 'Parsed unit roster')
    vector_fields={'max_power':'pmax','min_power':'pmin','min_power_cost':'min_cost'}
    scalar_fields={'min_uptime':'up','min_downtime':'down','ramp_up_limit':'ru','ramp_down_limit':'rd',
                   'startup_limit':'su','shutdown_limit':'sd','initial_status':'age','initial_power':'initial_power'}
    for name,g in ns.items():
        a=ps[name]; check(name+'.bus',a['bus'],n['bus'])
        for f,k in vector_fields.items(): check(name+'.'+f,native(a[f]),[qp(g[k])]*24)
        for f,k in scalar_fields.items(): check(name+'.'+f,native(a[f]),qp(g[k]))
        check(name+'.must_run',native(a['must_run']),[False]*24)
        check(name+'.commitment_status',native(a['commitment_status']),[None]*24)
        check(name+'.reserve_names',a['reserve_names'],[n['reserve_name']])
        need(len(a['cost_segments'])==4 and len(a['startup_categories'])==1,'Native cost dimensions')
        for k,s in enumerate(a['cost_segments']):
            check(name+f'.width{k}',native(s['mw']),[qp(g['widths'][k])]*24)
            check(name+f'.slope{k}',native(s['cost']),[qp(g['slopes'][k])]*24)
        cat=a['startup_categories'][0]
        check(name+'.startup_delay',native(cat['delay']),qp(g['startup_delay']))
        check(name+'.startup_cost',native(cat['cost']),qp(g['startup_cost']))
    return differences

def compare(raw, parsed, model, normal):
    parsed_differences=compare_parsed(parsed,normal)
    need(raw['schema']=='official-orlib-MOI-raw-binary64-v1' and raw['optimizer_state']=='NO_OPTIMIZER','Native raw contract')
    need(raw['duplicate_rows_preserved'] and not raw['mfg_omitted'] and not raw['finite_boxes_added'] and not raw['coefficient_normalization_performed'],'Unchanged raw export')
    ids=[v['index'] for v in raw['variables']]; need(len(ids)==len(set(ids)),'Unique raw variables')
    units={g['name'] for g in normal['units']};names={}
    for a in raw['semantic_aliases']:
        i=a['variable'];need(i in ids and i not in names,'Unique valid alias')
        names[i]=alias_name(a['family'],a['key'],parsed['scenario_name'],normal['bus'],normal['reserve_name'],units)
    need(set(names)==set(ids) and len(set(names.values()))==len(names),'Full semantic inventory')
    cols={x['name']:x for x in model['columns']};need(len(cols)==len(model['columns'])==2472,'Adapter retained columns')
    omitted={f'mfg:{g}:{t}' for g in units for t in range(24)}
    need(set(names.values())==set(cols)|omitted,'Exactly declared native projection')
    domains={n:[None,None] for n in names.values()};binaries=set();rows=Counter();row_names=defaultdict(list);typed=Counter();ci_seen=set()
    for row in raw['constraints']:
        signature=(row['function_type'],row['set_type'],row['index']);need(signature not in ci_seen,'Duplicate typed backend index');ci_seen.add(signature)
        typed[(row['function_type'],row['set_type'])]+=1
        f,s=row['function'],row['set'];need(f['type']==row['function_type'] and s['type']==row['set_type'],'Typed constraint relation')
        if f['type']=='MathOptInterface.VariableIndex':
            name=names[f['variable']]
            if s['type']=='MathOptInterface.ZeroOne':
                need(name not in binaries,'Duplicate binary declaration');binaries.add(name);lo,hi=Q(0),Q(1)
            else:lo,hi=set_bounds(s)
            oldlo,oldhi=domains[name]
            domains[name]=[lo if oldlo is None else oldlo if lo is None else max(lo,oldlo),hi if oldhi is None else oldhi if hi is None else min(hi,oldhi)]
        else:
            c,constant=affine(f,names);need(not set(c)&omitted,'Active omitted-variable row occurrence')
            lo,hi=set_bounds(s); key=canon(c, None if lo is None else lo-constant,None if hi is None else hi-constant)
            rows[key]+=1;row_names[key].append(dict(name=row['name'],typed_index=signature))
    reported={(x['function_type'],x['set_type']):x['count'] for x in raw['typed_counts']}
    need(dict(typed)==reported,'Complete typed native row counts')
    need(len(ids)==raw['counts']['all_variables'] and sum(rows.values())==raw['counts']['scalar_affine_rows'],'Native measured counts')
    need(binaries=={names[j] for j in raw['binary_variable_indices']} and len(binaries)==raw['counts']['native_ZeroOne_constraints'],'Native full binary census')
    binary_difference=sorted(binaries^{n for n,c in cols.items() if c['binary']})
    obj,constant=affine(raw['objective'],names);need(not set(obj)&omitted,'Active omitted-variable objective occurrence')
    projection_ok=all(domains[n]==[Q(0),None] for n in omitted)
    needed=Counter();adapter_names=defaultdict(list)
    for row in model['rows']:
        c=defaultdict(Q)
        for i,a in row['coefficients']:c[model['columns'][i]['name']]+=qp(a)
        k=canon(c,None if row['lower'] is None else qp(row['lower']),None if row['upper'] is None else qp(row['upper']))
        needed[k]+=1;adapter_names[k].append(row['name'])
    missing=needed-rows;extra=rows-needed
    objective_differences=[dict(name=n,native=rq(obj.get(n,Q(0))),adapter=rq(qp(c['objective']))) for n,c in cols.items() if obj.get(n,Q(0))!=qp(c['objective'])]
    bounds=[];allowed=[];bad=[];unit_data={g['name']:g for g in normal['units']}
    for n,c in cols.items():
        actual=domains[n];expected=[qp(c['lower']),qp(c['upper'])]
        if actual==expected:continue
        role=n.split(':')[0];justified=False
        if role in ('Q','R'):
            _,g,t=n.split(':');width=Q(float(unit_data[g]['pmax'])-float(unit_data[g]['pmin']))
            headroom=canon({f'Q:{g}:{t}':Q(1),f'R:{g}:{t}':Q(1),f'U:{g}:{t}':-width},None,Q(0))
            justified=(actual==[Q(0),None] and expected==[Q(0),width] and rows[headroom]>0 and domains[f'Q:{g}:{t}'][0]==0 and domains[f'R:{g}:{t}'][0]==0 and f'U:{g}:{t}' in binaries)
        elif role=='N':
            justified=(actual==[None,None] and expected==[Q(0),Q(0)] and rows[canon({n:Q(1)},Q(0),Q(0))]>0)
        item=dict(name=n,native=[rq(x) for x in actual],adapter=[rq(x) for x in expected],nominal_implication_checked=justified)
        bounds.append(item);(allowed if justified else bad).append(n)
    exact_rows=not missing and not extra
    exact_objective=not objective_differences and constant==0 and raw['objective_sense']=='MIN_SENSE'
    nominal=exact_rows and exact_objective and projection_ok and not binary_difference and not bad
    return dict(status='EXACT_NOMINAL_COMPARISON_PASS' if nominal and not parsed_differences else 'MISMATCH_RECORDED',
        parsed_differences=parsed_differences,parsed_exact_agreement=not parsed_differences,
        native_variables=len(ids),retained_variables=len(cols),omitted_variables=len(omitted),native_affine_rows=sum(rows.values()),adapter_affine_rows=sum(needed.values()),
        native_binary_count=len(binaries),binary_symmetric_difference=binary_difference,unused_mfg_projection_and_zero_lift=projection_ok,
        row_multisets_exact=exact_rows,native_canonical_multiset_sha256=signature_hash(rows),adapter_canonical_multiset_sha256=signature_hash(needed),
        missing_native_rows=[dict(row=row_json(k),multiplicity=v,adapter_names=adapter_names[k]) for k,v in missing.items()],
        extra_native_rows=[dict(row=row_json(k),multiplicity=v,native_names=row_names[k]) for k,v in extra.items()],
        objective_exact=exact_objective,objective_constant=rq(constant),objective_sense=raw['objective_sense'],objective_differences=objective_differences,
        column_domain_differences=bounds,allowed_nominal_domain_extensions=len(allowed),unjustified_domain_differences=bad,
        nominal_projection_equivalence=nominal,expanded_native_equivalence='NOT_ESTABLISHED',old_expanded_cost_bounds_transferred=False,
        tolerance_for_comparison=0,coefficient_rescaling=False,optimizer_calls=0,native_model_builds=0)

def prepare(expected_completion):
    need(not PRE.exists() and not RUN.exists(),'Fresh preparation only')
    done=OFFICIAL/'completion.json';need(sha(done)==expected_completion,'Externally supplied export closure')
    receipt=read(done);need(receipt['status']=='OFFICIAL_RAW_EXPORT_COMPLETE_PENDING_COMPARISON' and receipt['optimizer_calls']==0 and receipt['native_build_attempts']==receipt['native_read_attempts']==1 and receipt['inputs_unchanged'],'Successful one-build original export')
    source={done:'official_completion.json',OFFICIAL/'official_raw_model.json':'raw.json',OFFICIAL/'official_parsed_instance.json':'parsed.json',OLD/'identity__native_penalized.json':'model.json',OLD/'normalized_case.json':'normal.json'}
    need(sha(OFFICIAL/'official_raw_model.json')==receipt['raw_model_sha256'] and sha(OFFICIAL/'official_parsed_instance.json')==receipt['parsed_instance_sha256'],'Export payload hashes')
    need(sha(OLD/'identity__native_penalized.json')==MODEL_SHA and sha(OLD/'normalized_case.json')==CASE_SHA,'Frozen adapter inputs')
    need(sha(ORIGINAL_SOURCE)=='83ee49f623b9bb9b90a27ecbf808e305369ae02046add59a643afb002c0db507','Original source preserved')
    need(sha(HISTORY/'prepared/manifest.json')=='fe20e2535ad3f36e669dbafb1ff9d588d791f0e8c04bbedfa0557bc1830d8b29','Original freeze preserved')
    need(sha(HISTORY/'run01/failure.json')=='819f59c1b1918bf4672a4efc39f92e767c9601ec5492e824b2edbe36b08a673c','Original failure preserved')
    items=[binding(p) for p in list(source)+[Path(__file__),PROTOCOL,ORIGINAL_SOURCE,ORIGINAL_PROTOCOL,HISTORY/'prepared/manifest.json',HISTORY/'run01/failure.json']]
    captured={p:p.read_bytes() for p in source};validate(items)
    descriptions={b['path']:b for b in items}
    for p,data in captured.items():
        b=descriptions[str(p.resolve())]
        need(len(data)==b['bytes'] and hashlib.sha256(data).hexdigest()==b['sha256'],'Captured input differs from admitted bytes')
    PRE.mkdir(parents=True)
    for p,name in source.items():
        (PRE/name).write_bytes(captured[p])
        need((PRE/name).read_bytes()==captured[p], 'Captured copy changed')
    copies=[binding(PRE/name) for name in source.values()];validate(items)
    save(PRE/'manifest.json',dict(inputs=items,copies=copies,source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),utc=utc(),comparison_runs=0))
    print(json.dumps(dict(status='PREPARED_ONLY',manifest_sha256=sha(PRE/'manifest.json'))))

def run(expected):
    start=time.perf_counter();need(not RUN.exists(),'Single comparison only');need(sha(PRE/'manifest.json')==expected,'External comparison freeze')
    manifest=read(PRE/'manifest.json');items=manifest['inputs']+manifest['copies'];validate(items)
    need(sha(__file__)==manifest['source_sha256'] and sha(PROTOCOL)==manifest['protocol_sha256'],'Frozen source/protocol')
    RUN.mkdir();save(RUN/'started.json',dict(utc=utc(),manifest_sha256=expected,source_sha256=sha(__file__),optimizer_calls=0))
    try:
        result=compare(*(read(PRE/n) for n in ('raw.json','parsed.json','model.json','normal.json')))
        save(RUN/'comparison.json',result);validate(items);need(sha(PRE/'manifest.json')==expected,'Manifest changed')
        elapsed=time.perf_counter()-start;need(elapsed<=120,'120-second soft phase exceeded; result not admitted')
        save(RUN/'completion.json',dict(status='COMPLETE_PENDING_INDEPENDENT_REVIEW',utc=utc(),elapsed_seconds=elapsed,all_inputs_unchanged=True,optimizer_calls=0,final_completion_write_excluded=True))
        print(json.dumps({k:result[k] for k in ('status','native_variables','native_affine_rows','row_multisets_exact','objective_exact','nominal_projection_equivalence')}))
    except BaseException as e:
        save(RUN/'failure.json',dict(utc=utc(),exception_type=type(e).__name__,message=str(e),elapsed_seconds=time.perf_counter()-start,no_retry=True,no_equivalence_claim=True));raise

def self_test():
    out=ARM/'synthetic_controls.json';need(not out.exists(),'One fixture set only')
    def hx(x):return dict(type='Float64',bits_hex=struct.pack('>d',x).hex(),display=repr(x))
    for family,role,key in [('curtail','C','b'),('reserve_shortfall','F','r'),('net_injection','N','b')]:
        need(alias_name(family,['s',key,1],'s','b','r',{'g'})==f'{role}:system:0','System alias schema')
    need(native(hx(0.1))==Q.from_float(0.1),'Exact float decoder')
    need(native(hx(math.nextafter(1.0,2.0)))!=native(hx(1.0)),'One ULP cannot collapse')
    a=canon({'a':Q(1),'b':Q(-2)},Q(0),Q(3));b=canon({'b':Q(2),'a':Q(-1)},Q(-3),Q(0));need(a==b,'Signed endpoint reversal')
    need(Counter([a,a])!=Counter([a]),'Multiplicity retained')
    c,k=affine(dict(type='MathOptInterface.ScalarAffineFunction{Float64}',constant=hx(2.),terms=[dict(variable=9,coefficient=hx(1.))]),{9:'a'})
    need(canon(c,None,Q(5)-k)==canon({'a':Q(1)},None,Q(3)),'Exact affine constant')
    for f in [lambda:alias_name('unsupported',['s','g0',1],'s','b','r',{'g0'}),lambda:set_bounds(dict(type='unsupported'))]:
        try:f()
        except ValueError:pass
        else:raise AssertionError('Unsupported schema admitted')
    ARM.mkdir(parents=True,exist_ok=True);save(out,dict(status='PASS',checks=10,utc=utc(),source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),scientific_arrays_read=0,comparison_runs=0,optimizer_calls=0))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['self-test','prepare','run']);p.add_argument('--expected-sha');args=p.parse_args()
    if args.mode=='self-test':self_test()
    elif args.mode=='prepare':need(args.expected_sha is not None,'Explicit export closure pin required');prepare(args.expected_sha)
    else:need(args.expected_sha is not None,'Explicit manifest pin required');run(args.expected_sha)
