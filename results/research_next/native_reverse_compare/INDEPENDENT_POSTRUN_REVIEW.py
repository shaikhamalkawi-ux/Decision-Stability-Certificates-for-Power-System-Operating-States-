"""Independent exact native/adapter projection proof, without producer imports."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib, json, math, time

ROOT=Path(__file__).resolve().parents[3]
ARM=ROOT/'results/research_next/native_reverse_compare'
PRE=ARM/'prepared'
RUN=ARM/'run01'
MSHA='b594e558f7587a1667407d48d39d0bc9f4c7a6804620121e438908d804eb4fc4'
PARENT_REVIEW=ROOT/'results/research_next/orlib_native_compare_schema2/INDEPENDENT_POSTRUN_REVIEW.py'
PARENT_SHA='6390b0f51a9385860ff28683c2610008173ea0fcb8b1ed40b686cbbfd7c06d3c'
ORDER=[0,1,2,3,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,20,21,22,23]
def need(ok,why):
    if not ok: raise AssertionError(why)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def check_files(items):
    for e in items:
        p=Path(e['path']);b=p.read_bytes()
        need(len(b)==e['bytes'] and hashlib.sha256(b).hexdigest()==e['sha256'],str(p))
def fp(x):
    need(type(x) in (int,float) and math.isfinite(x),'Finite adapter number')
    return F(x)
def decode(x):
    if type(x) is dict:
        need(set(x)=={'type','bits_hex','display'} and x['type']=='Float64','Native number schema')
        h=x['bits_hex'];need(type(h) is str and len(h)==16 and all(c in '0123456789abcdef' for c in h),'Binary64 hex')
        bits=int(h,16);sign=-1 if bits>>63 else 1;exp=(bits>>52)&2047;mant=bits&((1<<52)-1)
        need(exp!=2047,'Finite native number')
        power=-1074 if exp==0 else exp-1075
        numerator=sign*(mant if exp==0 else (1<<52)+mant)
        return F(numerator*(1<<power),1) if power>=0 else F(numerator,1<<(-power))
    if type(x) is list:return [decode(a) for a in x]
    if type(x) is int:return F(x)
    need(x is None or type(x) in (bool,str),'Native scalar type')
    return x
def recursively_native(x):
    if type(x) is dict:
        return decode(x) if x.get('type')=='Float64' else {k:recursively_native(v) for k,v in x.items()}
    if type(x) is list:return [recursively_native(v) for v in x]
    return decode(x)
def recursively_adapter(x):
    if type(x) is dict:return {k:recursively_adapter(v) for k,v in x.items()}
    if type(x) is list:return [recursively_adapter(v) for v in x]
    return fp(x) if type(x) in (int,float) else x
def endpoints(s):
    t=s['type'].removeprefix('MathOptInterface.')
    if t=='EqualTo{Float64}':v=decode(s['value']);return v,v
    if t=='GreaterThan{Float64}':return decode(s['lower']),None
    if t=='LessThan{Float64}':return None,decode(s['upper'])
    if t=='Interval{Float64}':return decode(s['lower']),decode(s['upper'])
    raise AssertionError('Unsupported set '+t)
def terms(f,alias):
    need(f['type']=='MathOptInterface.ScalarAffineFunction{Float64}','Only scalar affine')
    c=defaultdict(F)
    for term in f['terms']:
        need(term['variable'] in alias,'Term variable')
        c[alias[term['variable']]]+=decode(term['coefficient'])
    return {k:v for k,v in c.items() if v},decode(f['constant'])
def rowkey(c,lo,hi):
    # A row is its ordered multiset of exact upper-bound halfspaces. This is
    # invariant under whole-row sign reversal without producer canonicalization.
    sides=[]
    if hi is not None:sides.append((tuple(sorted((n,a) for n,a in c.items() if a)),hi))
    if lo is not None:sides.append((tuple(sorted((n,-a) for n,a in c.items() if a)),-lo))
    need(sides,'Every archived affine row has an endpoint')
    return tuple(sorted(sides))
def qjson(q):return None if q is None else [str(q.numerator),str(q.denominator)]
def parsed_check(p,n):
    expected={'scenario_name':'s1','time':24,'scenario_time':24,'time_step_minutes':60,
      'native_default_read_and_repair':True,'probability':1,
      'buses':[{'name':n['bus'],'load':n['load']}],
      'power_balance_penalty':n['penalty'],
      'reserves':[{'name':n['reserve_name'],'type':'spinning','amount':n['reserve'],'shortfall_penalty':-1}],
      'thermal_units':[]}
    for g in n['units']:
        expected['thermal_units'].append(dict(name=g['name'],bus=n['bus'],
          max_power=[g['pmax']]*24,min_power=[g['pmin']]*24,min_power_cost=[g['min_cost']]*24,
          min_uptime=g['up'],min_downtime=g['down'],ramp_up_limit=g['ru'],ramp_down_limit=g['rd'],
          startup_limit=g['su'],shutdown_limit=g['sd'],initial_status=g['age'],initial_power=g['initial_power'],
          must_run=[False]*24,commitment_status=[None]*24,reserve_names=[n['reserve_name']],
          cost_segments=[{'mw':[w]*24,'cost':[s]*24} for w,s in zip(g['widths'],g['slopes'])],
          startup_categories=[{'delay':g['startup_delay'],'cost':g['startup_cost']}]))
    actual=recursively_native(p); wanted=recursively_adapter(expected)
    # Unit ordering is presentation, not a model premise; names must be unique.
    a={g['name']:g for g in actual.pop('thermal_units')};w={g['name']:g for g in wanted.pop('thermal_units')}
    need(len(a)==len(w)==10 and a==w,'All exact parsed unit fields')
    need(actual==wanted,'All exact parsed system fields')
    return {'top_level_fields':len(p),'units':len(a),'fields_per_unit':len(next(iter(a.values()))),'all_exact':True}
def aliases_from_expected(raw,n):
    expected={};scenario='s1';bus=n['bus'];reserve=n['reserve_name']
    for g in n['units']:
        name=g['name']
        for t in range(24):
            for family,role in [('is_on','U'),('switch_on','Y'),('switch_off','Z')]:expected[family,(name,t+1)]=f'{role}:{name}:{t}'
            expected['startup',(name,t+1,1)]=f'D:{name}:{t}'
            expected['prod_above',(scenario,name,t+1)]=f'Q:{name}:{t}'
            expected['mfg',(scenario,name,t+1)]=f'mfg:{name}:{t}'
            expected['reserve',(scenario,reserve,name,t+1)]=f'R:{name}:{t}'
            for k in range(4):expected['segprod',(scenario,name,t+1,k+1)]=f'S:{name}:{t}:{k}'
    for t in range(24):
        for family,role,place in [('curtail','C',bus),('net_injection','N',bus),('reserve_shortfall','F',reserve)]:expected[family,('s1',place,t+1)]=f'{role}:system:{t}'
    alias={};seen=set()
    for a in raw['semantic_aliases']:
        key=a['family'],tuple(a['key']);need(key in expected and key not in seen,'Native alias role')
        need(a['variable'] not in alias,'Unique native variable alias');seen.add(key);alias[a['variable']]=expected[key]
    ids=[v['index'] for v in raw['variables']]
    need(len(ids)==len(set(ids))==len(alias)==len(expected)==2712 and set(ids)==set(alias) and seen==set(expected),'Complete alias bijection')
    return alias
def main():
    start=time.perf_counter();need(sha(PRE/'manifest.json')==MSHA,'Pinned freeze')
    manifest=read(PRE/'manifest.json');items=manifest['inputs']+list(manifest['copies'].values());check_files(items)
    need(sha(PARENT_REVIEW)==PARENT_SHA,'Explicit unchanged independent parent checker provenance')
    need(sha(ROOT/'src/researchnext_native_reverse_compare.py')==manifest['source_sha256']=='d119ee515815281bf95bd3f669b0bc5a657ed8be90161fe2fd6de6489cfa1e82','Frozen wrapper')
    need(sha(ROOT/'docs/research_next/NATIVE_REVERSE_COMPARE_PROTOCOL.md')==manifest['protocol_sha256']=='36535647b0e62db57f526f1c6d5ebcb2e04c2df5a22650a6046a2341344d95d4','Frozen protocol')
    snapshot={p.name:sha(p) for p in RUN.iterdir() if p.is_file()}
    need(set(snapshot)=={'started.json','comparison.json','completion.json','expected_parsed_bridge.json'},'Closed single success layout')
    producer=read(RUN/'comparison.json');completion=read(RUN/'completion.json');started=read(RUN/'started.json')
    need(started['manifest_sha256']==MSHA and started['native_builds']==0,'Launch pins')
    need(completion['status']=='COMPLETE_PENDING_INDEPENDENT_REVIEW' and completion['all_inputs_unchanged'],'Completed run')
    need(0<=completion['elapsed_seconds']<=120 and completion['optimizer_calls']==started['optimizer_calls']==0,'Timing and zero optimization')
    raw=read(PRE/'raw.json');p=read(PRE/'parsed.json');model=read(PRE/'model.json');normal=read(PRE/'normal.json')
    need(model['order']==ORDER and model['variant']=='native_penalized' and model['horizon']==24,'Fixed original target')
    bridge=read(RUN/'expected_parsed_bridge.json')
    need(bridge['order_destination_to_source']==ORDER and bridge['only_reordered_fields']==['load','reserve','penalty'],'Recorded one-time expected-input bridge')
    need(bridge['original_normal_sha256']==sha(PRE/'normal.json') and bridge['original_model_sha256']==sha(PRE/'model.json') and bridge['actual_target_plain_sha256']==sha(PRE/'derived_plain.json'),'Exact bridge payloads')
    need(bridge['same_numerical_instance_not_whole_file_metadata_equality'] is True,'Metadata qualification')
    normal={**normal,**{key:[normal[key][source] for source in ORDER] for key in ('load','reserve','penalty')}}
    parsed=parsed_check(p,normal);alias=aliases_from_expected(raw,normal)
    need(raw['schema']=='official-orlib-MOI-raw-binary64-v1' and raw['optimizer_state']=='NO_OPTIMIZER','Raw schema')
    need(raw['duplicate_rows_preserved'] and not raw['mfg_omitted'] and not raw['finite_boxes_added'] and not raw['coefficient_normalization_performed'],'Raw export contract')
    names=set(alias.values());omitted={n for n in names if n.startswith('mfg:')}
    columns={c['name']:c for c in model['columns']}
    need(len(columns)==len(model['columns'])==2472 and names==set(columns)|omitted and len(omitted)==240,'Projection columns')
    domains={n:[None,None] for n in names};binary=set();rows=Counter();typed=Counter();ids=set();term_uses=0
    for row in raw['constraints']:
        f,s=row['function'],row['set'];key=row['function_type'],row['set_type'],row['index']
        need(key not in ids and key[:2]==(f['type'],s['type']),'Unique typed row identity');ids.add(key);typed[key[:2]]+=1
        if f['type']=='MathOptInterface.VariableIndex':
            name=alias[f['variable']]
            if s['type']=='MathOptInterface.ZeroOne':
                need(name not in binary,'Unique binary declaration');binary.add(name);lo,hi=F(0),F(1)
            else:lo,hi=endpoints(s)
            oldlo,oldhi=domains[name]
            domains[name]=[lo if oldlo is None else oldlo if lo is None else max(lo,oldlo),hi if oldhi is None else oldhi if hi is None else min(hi,oldhi)]
        else:
            c,k=terms(f,alias);term_uses+=len(f['terms']);need(not set(c)&omitted,'No omitted affine support')
            lo,hi=endpoints(s);rows[rowkey(c,None if lo is None else lo-k,None if hi is None else hi-k)]+=1
    need(dict(typed)=={(c['function_type'],c['set_type']):c['count'] for c in raw['typed_counts']},'Complete constraint census')
    need(binary=={alias[i] for i in raw['binary_variable_indices']}=={n for n,c in columns.items() if c['binary']} and len(binary)==960,'All original binary declarations')
    need(all(domains[n]==[F(0),None] for n in omitted),'Omitted domain zero lift')
    adapter=Counter()
    for row in model['rows']:
        c=defaultdict(F)
        for j,a in row['coefficients']:
            need(type(j) is int and 0<=j<len(model['columns']),'Adapter sparse index')
            c[model['columns'][j]['name']]+=fp(a)
        adapter[rowkey(c,None if row['lower'] is None else fp(row['lower']),None if row['upper'] is None else fp(row['upper']))]+=1
    need(rows==adapter and sum(rows.values())==sum(adapter.values())==4384,'All affine rows with multiplicity')
    need(raw['counts']=={'all_variables':2712,'native_ZeroOne_constraints':960,'scalar_affine_rows':4384},'Reported counts')
    obj,const=terms(raw['objective'],alias)
    need(not set(obj)&omitted and const==0 and raw['objective_sense']=='MIN_SENSE','Objective zero lift/constant/sense')
    need(all(obj.get(n,F(0))==fp(c['objective']) for n,c in columns.items()),'Every retained objective coefficient')
    roster={g['name']:g for g in normal['units']};extensions=[]
    for name,c in columns.items():
        wanted=[fp(c['lower']),fp(c['upper'])];actual=domains[name]
        if actual==wanted:continue
        pieces=name.split(':')
        if pieces[0] in ('Q','R'):
            _,g,t=pieces;w=F(float(roster[g]['pmax'])-float(roster[g]['pmin']))
            q,r,u=f'Q:{g}:{t}',f'R:{g}:{t}',f'U:{g}:{t}'
            need(actual==[F(0),None] and wanted==[F(0),w] and w>=0,'Headroom extension domain')
            need(domains[q][0]==domains[r][0]==0 and domains[u]==[F(0),F(1)] and u in binary,'Headroom endpoint premises')
            need(rows[rowkey({q:F(1),r:F(1),u:-w},None,F(0))]>0,'Exact native headroom implication')
        elif pieces[0]=='N':
            need(actual==[None,None] and wanted==[F(0),F(0)] and rows[rowkey({name:F(1)},F(0),F(0))]>0,'Exact native N=0 implication')
        else:raise AssertionError('Unexpected domain difference '+name)
        extensions.append(dict(name=name,native=[qjson(v) for v in actual],adapter=[qjson(v) for v in wanted],nominal_implication_checked=True))
    need(len(extensions)==504,'480 headroom +24 zero-injection boxes')
    need(extensions==producer['column_domain_differences'],'Exact archived domain explanation')
    for field in ('parsed_exact_agreement','unused_mfg_projection_and_zero_lift','row_multisets_exact','objective_exact','nominal_projection_equivalence'):
        need(producer[field] is True,'Producer claim '+field)
    for field in ('parsed_differences','binary_symmetric_difference','missing_native_rows','extra_native_rows','objective_differences','unjustified_domain_differences'):
        need(producer[field]==[],'Empty discrepancy '+field)
    need(producer['status']=='EXACT_NOMINAL_COMPARISON_PASS' and producer['allowed_nominal_domain_extensions']==504,'Producer classification')
    need(producer['expanded_native_equivalence']=='NOT_ESTABLISHED' and not producer['old_expanded_cost_bounds_transferred'],'Expanded scope preserved')
    need(producer['tolerance_for_comparison']==0 and not producer['coefficient_rescaling'] and producer['optimizer_calls']==producer['native_model_builds']==0,'Exact-only comparison scope')
    need(producer['case']=='reverse_4_19__native_penalized' and producer['reused_comparator_sha256']=='e9f1065fbd47e9d5b7a67afad92fc6a18816cade310b87c8f1c66a49814c389f','Producer target/helper scope')
    need(producer['native_input_reordered_once'] is True and producer['target_candidate_or_dual_permuted'] is False and producer['no_cost_transfer_at_this_stage'] is True and producer['posthoc_fidelity_extension'] is True,'No silent point/cost transfer')
    need(completion['native_builds']==0 and completion['final_completion_write_excluded'] is True,'Closed no-build scope')
    check_files(items);need(sha(PRE/'manifest.json')==MSHA and sha(PARENT_REVIEW)==PARENT_SHA,'Freeze and independent lineage unchanged')
    need(snapshot=={p.name:sha(p) for p in RUN.iterdir() if p.is_file()},'All producer outputs unchanged')
    report=dict(status='PASS_INDEPENDENT_EXACT_NOMINAL_PROJECTION_EQUIVALENCE',utc=datetime.now(timezone.utc).isoformat(),
      reviewer_source_sha256=sha(Path(__file__)),manifest_sha256=MSHA,source_sha256=manifest['source_sha256'],
      descriptors_verified_twice=len(items),original_bindings=len(manifest['inputs']),copies=len(manifest['copies']),producer_snapshot=snapshot,parsed_fields=parsed,
      independent_parent_reviewer_sha256=PARENT_SHA,case='reverse_4_19__native_penalized',order_destination_to_source=ORDER,
      adaptation_scope='Unchanged independent row/domain/objective/parsed-field algorithms; target expected-series order and closure provenance only.',
      native_variables=2712,retained_variables=2472,omitted_nonnegative_zero_lift_variables=240,binaries=960,
      affine_rows_with_multiplicity=4384,distinct_affine_row_signatures=len(rows),raw_affine_term_uses=term_uses,
      comparison_representation='independent exact upper-halfspace-pair row multisets',
      row_multiset_sha256=hashlib.sha256(repr(sorted(rows.items())).encode()).hexdigest(),
      exact_objective=True,nominal_domain_extensions=504,headroom_extensions=480,zero_injection_extensions=24,
      nominal_projection_equivalence=True,expanded_native_equivalence='NOT_ESTABLISHED',old_expanded_cost_bounds_transferred=False,
      producer_elapsed_seconds=completion['elapsed_seconds'],producer_imports=0,Julia_calls=0,native_builds=0,optimizer_calls=0,
      elapsed_seconds=time.perf_counter()-start)
    with (ARM/'INDEPENDENT_POSTRUN_REVIEW.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
    print(report['status'],report['elapsed_seconds'])
if __name__=='__main__':main()
