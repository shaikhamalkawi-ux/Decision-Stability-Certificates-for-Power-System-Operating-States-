"""Independent read-only audit of the prepared flow-incidence variant."""
import csv, gzip, hashlib, importlib.util, json, math, sys, time
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/research8h/branch_flow_encoding'
OLD=ROOT/'results/research8h/hour_of_day'
CASES=('january_identity','seed_26100200','seed_26093200','seed_26093201')
KERNEL=ROOT/'src/research8h_standalone_verify.py'
SHA='708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'
def req(x,m):
    if not x: raise AssertionError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def js(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def rq(x):return Q(int(x['numerator']),int(x['denominator']))
def pack(x):return dict(numerator=str(x.numerator),denominator=str(x.denominator))
def arr(p,k):return v.read_npz(p,(k,))[k].values
def labels(p):
    with gzip.open(p,'rt',encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def row(m,i):return {m.indices[e]:Q(m.data[e]) for e in range(m.indptr[i],m.indptr[i+1]) if m.data[e]}
def eq_bounds(a,b):return len(a)==len(b) and all(x==y for x,y in zip(a,b))
def endpoints(m,i):return (m.row_lower[i],m.row_upper[i])
start=time.perf_counter();req(sha(KERNEL)==SHA,'Kernel changed')
spec=importlib.util.spec_from_file_location('independent_flow_kernel',KERNEL);v=importlib.util.module_from_spec(spec);sys.modules[spec.name]=v;spec.loader.exec_module(v)
freeze=js(OUT/'prepared_freeze.json');manifest=js(OUT/'input_manifest.json')
req(sha(OUT/'input_manifest.json')==freeze['manifest_sha256'],'Manifest digest')
req(len(manifest)==freeze['bindings'],'Binding count')
for e in manifest:
    p=Path(e['path']);req(p.is_file() and p.stat().st_size==int(e['bytes']) and sha(p)==e['sha256'],'Frozen input '+str(p))
req(not (OUT/'execution_marker.json').exists(),'Execution already started')
req(freeze['calls']==[['identity_proposal',60.0],['seed_26093200',30.0],['seed_26093201',30.0]],'Call roster')
req(freeze['phase_seconds']==1800 and freeze['arithmetic_seconds']==900 and freeze['bit_limit']==8192,'Budgets')
req(freeze['ray_candidates']==['+raw','+projected','-raw','-projected'],'Ray recipe')
req(freeze['cutoff']=='2026-09-27T04:00:00+00:00','Cutoff')
for name,digest in [('src/research8h_branch_flow.py',freeze['source_sha256']),('src/research8h_branch_flow_check.py',freeze['checker_sha256']),('docs/research8h/BRANCH_FLOW_ENCODING_PROTOCOL.md',freeze['protocol_sha256'])]:req(sha(ROOT/name)==digest,'Frozen source '+name)
gen=ROOT/'reproducibility/native_sources/rts_inputs/raw/RTS-GMLC_v0.2.3/gen.csv'
req(sha(gen)=='988466f29132b73739de60c9204dd4a2a9ceb0adf572e5966c086611272f4068','Native generator digest')
with gen.open(encoding='utf-8-sig',newline='') as f:gens={r['GEN UID']:r for r in csv.DictReader(f)}
models={};case_results=[];identity_native=None
for case in CASES:
    d=OUT/case;s=OLD/case;old=v.load_model(s);m=v.load_model(d);ol=labels(s/'row_metadata.csv.gz');nl=labels(d/'row_metadata.csv.gz');meta=js(d/'model_metadata.json')
    req((old.rows,old.cols,m.rows,m.cols)==(34681,23016,34513,29400),'Dimensions')
    req(meta['nonzeros']==len(m.data) and 'flow' in meta['column_order'],'Accurate exported metadata')
    oldmeta=js(s/'model_metadata.json')
    for key in ('unit_names','thermal_unit_names','bus_ids'):req(meta[key]==oldmeta[key],'Retained metadata '+key)
    req(meta['offsets']=={**oldmeta['offsets'],'flow':23016},'Flow offset metadata')
    req(len(nl)==m.rows and [int(r['row']) for r in nl]==list(range(m.rows)),'New row labels')
    req(eq_bounds(m.lower[:old.cols],old.lower) and eq_bounds(m.upper[:old.cols],old.upper),'Retained boxes')
    req(arr(d/'integrality.npz','integrality')==tuple(int(6888<=j<18984) for j in range(m.cols)),'Full original mask')
    names=meta['unit_names'];buses=meta['bus_ids'];req(len(names)==41 and len(buses)==24,'Native roster')
    native_specs=js(d/'native_spec.json');req(len(native_specs)==41,'Native spec count')
    for n,ns in zip(names,native_specs):
        g=gens[n];rate=float(g['Ramp Rate MW/Min']);hourly=rate*60.0
        req(ns['uid']==n and ns['bus']==int(g['Bus ID']) and ns['category']==g['Category'] and ns['thermal']==(n in meta['thermal_unit_names']),'Native unit spec')
        req(ns['minimum_up']==math.ceil(float(g['Min Up Time Hr'])) and ns['minimum_down']==math.ceil(float(g['Min Down Time Hr'])),'Native residence')
        req(rq(ns['hourly_rational'])==Q(hourly) and ns['per_minute_binary64_hex']==rate.hex() and ns['hourly_binary64_hex']==hourly.hex() and rq(ns['difference_from_exact_times_60'])==Q(hourly)-60*Q(rate),'Native ramp conversion')
    fossil=[j for j,n in enumerate(names) if gens[n]['Fuel'] in ('Coal','Oil','NG')]
    req(len(fossil)==23 and set(names[j] for j in fossil)==set(meta['fossil_units']),'Native fossil mapping')
    cost=tuple(float(j<6888 and j%41 in fossil) for j in range(m.cols))
    req(arr(d/'objective.npz','objective')==cost,'Fossil objective')
    req(not any(arr(s/'objective.npz','objective')),'Old objective must be zero')
    req(sha(d/'native_inputs.npz')==sha(s/'native_inputs.npz') and sha(d/'permutation.csv')==sha(s/'permutation.csv'),'Native/permutation copy')
    native=v.read_npz(d/'native_inputs.npz',('pmin','pmax','net','nodal','rows','source_hour'))
    order=native['source_hour'].values;req(sorted(order)==list(range(168)),'Source permutation')
    req(all(order[t]==t for t in list(range(48))+list(range(120,168))) and all(t%24==s0%24 for t,s0 in enumerate(order)),'Clock/edge observations')
    if identity_native is None:identity_native=native;req(order==tuple(range(168)),'Identity order')
    for key,width in [('pmin',41),('pmax',41),('net',1),('nodal',24),('rows',1)]:
        req(native[key].values==tuple(x for t in order for x in identity_native[key].values[t*width:(t+1)*width]),'Whole package '+key)
    graph=js(d/'graph.json');diffs=js(d/'representation_differences.json');branch_rows={};nodal_rows={};aggregate_rows={}
    for i,r in enumerate(ol):
        t=int(r['hour_0based'])
        if r['family']=='branch_flow':branch_rows.setdefault(t,[]).append(i)
        if r['family']=='nodal_balance':nodal_rows[(t,int(r['uid']))]=i
        if r['family']=='aggregate_balance':aggregate_rows[t]=i
    req(len(graph)==38 and len(aggregate_rows)==168,'Graph/aggregate count')
    eliminated=[[Q(0)]*24 for _ in range(24)]
    for e,g in enumerate(graph):
        u,w,b=g['positive_bus'],g['negative_bus'],rq(g['coefficient']);req(g['branch']==e and 0<=u<24 and 0<=w<24 and u!=w and b>0,'Graph entry')
        eliminated[u][u]-=b;eliminated[u][w]+=b;eliminated[w][u]+=b;eliminated[w][w]-=b
        for t in range(168):
            oi=branch_rows[t][e];req(row(old,oi)=={18984+t*24+u:b,18984+t*24+w:-b},'Original branch coefficient')
            req(ol[oi]['uid']==g['uid'],'Branch UID')
            req(Q(old.row_lower[oi])==rq(g['lower']) and Q(old.row_upper[oi])==rq(g['upper']),'Original line bounds')
            req(Q(m.lower[23016+t*38+e])==rq(g['lower']) and Q(m.upper[23016+t*38+e])==rq(g['upper']),'Flow boxes')
    seen=[];counts=Counter();maxdelta=Q(0);rhsdelta=[];template=None
    for t in range(168):
        ag=aggregate_rows[t];req(row(old,ag)=={t*41+j:Q(1) for j in range(41)},'Aggregate row')
        req(endpoints(old,ag)==(native['net'].values[t],)*2,'Old net provenance')
        rd=sum((Q(x) for x in native['nodal'].values[t*24:(t+1)*24]),Q(0))-Q(native['net'].values[t]);rhsdelta.append(rd)
        delta=[]
        for i,bid in enumerate(buses):
            oldrow=row(old,nodal_rows[(t,bid)])
            for j in range(24):
                q=eliminated[i][j]-oldrow.get(18984+t*24+j,Q(0))
                if q:delta.append(dict(bus=i,theta=j,value=pack(q)));maxdelta=max(maxdelta,abs(q))
        if template is None:template=delta
        req(delta==template,'Common exact nodal difference')
    req(diffs['nodal_delta']==template and diffs['changed_nodal_coefficients']==len(template),'Stored coefficient differences')
    req([rq(x) for x in diffs['native_nodal_sum_minus_old_net']]==rhsdelta,'Stored RHS differences')
    for i,r in enumerate(nl):
        oi=int(r['old_row']);seen.append(oi);t=int(r['hour_0based']);fam=r['family'];counts[fam]+=1
        req(r['uid']==ol[oi]['uid'] and t==int(ol[oi]['hour_0based']),'Original row map')
        if fam=='nodal_flow_incidence':
            req(ol[oi]['family']=='nodal_balance','Nodal replacement family');bus=buses.index(int(r['uid']))
            exp={t*41+j:Q(1) for j,n in enumerate(names) if int(gens[n]['Bus ID'])==int(r['uid'])}
            req({j:a for j,a in row(old,oi).items() if j<6888}==exp,'Old native generator incidence')
            for e,g in enumerate(graph):
                if bus==g['positive_bus']:exp[23016+t*38+e]=Q(-1)
                if bus==g['negative_bus']:exp[23016+t*38+e]=Q(1)
            req(row(m,i)==exp and endpoints(m,i)==endpoints(old,oi)==(native['nodal'].values[t*24+bus],)*2,'Exact nodal incidence')
        elif fam=='flow_definition':
            req(ol[oi]['family']=='branch_flow','Flow replacement family');e=branch_rows[t].index(oi);g=graph[e];b=rq(g['coefficient'])
            req(row(m,i)=={23016+t*38+e:Q(1),18984+t*24+g['positive_bus']:-b,18984+t*24+g['negative_bus']:b} and endpoints(m,i)==(0.,0.),'Exact flow definition')
        else:req(fam==ol[oi]['family'] and row(m,i)==row(old,oi) and endpoints(m,i)==endpoints(old,oi),'Retained original row')
    req(len(set(seen))==len(seen) and set(seen)==set(range(old.rows))-set(aggregate_rows.values()),'Only aggregate rows omitted')
    caps=[i for i,r in enumerate(nl) if r['family']=='fossil_energy_cap'];req(len(caps)==1 and row(m,caps[0])=={j:Q(c) for j,c in enumerate(cost) if c} and endpoints(m,caps[0])==(-math.inf,23195.),'Unchanged full cap')
    models[case]=(m,nl,cost)
    case_results.append(dict(case=case,rows=m.rows,columns=m.cols,binary_coordinates=12096,retained_and_replaced_rows_checked=len(seen),changed_nodal_coefficients=len(template),max_abs_nodal_coefficient_difference=pack(maxdelta),max_abs_nodal_sum_minus_old_net=pack(max(map(abs,rhsdelta))),families=dict(counts)))
# Independently eliminate exactly the fixed state coordinates and the sole cap.
fixed={int(r['column']):rq(r['value']) for r in js(OUT/'fixed_schedule.json')};req(set(fixed)==set(range(6888,18984)) and all(x in (0,1) for x in fixed.values()),'Fixed canonical state set')
oldpoint=arr(OLD/'january_identity'/'constructive_vector.npz','vector');req(all(x==Q(oldpoint[j]) for j,x in fixed.items()),'Original state vector')
control_order=v.read_npz(OUT/CASES[1]/'native_inputs.npz',('pmin','pmax','net','nodal','rows','source_hour'))['source_hour'].values;req(all(fixed[6888+t*24+k]==fixed[6888+control_order[t]*24+k] for t in range(168) for k in range(24)),'Control U equality')
m,nl,cost=models[CASES[0]];p=v.load_model(OUT/'identity_proposal')
with gzip.open(OUT/'exact_blocks.json.gz','rt',encoding='utf-8') as f:blocks=json.load(f)
proposal_meta=js(OUT/'identity_proposal/model_metadata.json');proposal_labels=labels(OUT/'identity_proposal/row_metadata.csv.gz')
req(proposal_meta['nonzeros']==len(p.data) and len(proposal_labels)==p.rows,'Proposal exported metadata')
req((p.rows,p.cols)==(18480,17304) and len(blocks)==168,'Proposal dimensions')
constants=[];all_free_rows=[];seen_columns=[];rowcounts=Counter()
for b in blocks:
    t=b['hour'];cols=list(range(t*41,(t+1)*41))+list(range(18984+t*24,18984+(t+1)*24))+list(range(23016+t*38,23016+(t+1)*38))
    req(b['columns']==cols and len(b['rows'])==110,'Block mapping');seen_columns+=cols
    for key,values in [('lower',m.lower),('upper',m.upper),('objective',cost)]:req([rq(x) for x in b[key]]==[Q(values[j]) for j in cols],'Block '+key)
    local={j:k for k,j in enumerate(cols)}
    for k,r in enumerate(b['rows']):
        oi=r['original_row'];all_free_rows.append(oi);raw=row(m,oi);shift=sum((a*fixed[j] for j,a in raw.items() if j in fixed),Q(0));exp={local[j]:a for j,a in raw.items() if j not in fixed}
        req(rq(r['fixed_shift'])==shift and {int(j):rq(a) for j,a in r['terms']}==exp,'Exact state substitution')
        lo,hi=endpoints(m,oi);elo=None if not math.isfinite(lo) else Q(lo)-shift;ehi=None if not math.isfinite(hi) else Q(hi)-shift
        req((None if r['lower'] is None else rq(r['lower']))==elo and (None if r['upper'] is None else rq(r['upper']))==ehi,'Exact substituted endpoint')
        pi=t*110+k;req(r['family']==nl[oi]['family'] and r['uid']==nl[oi]['uid'] and int(nl[oi]['hour_0based'])==t,'Block row labels')
        req(int(proposal_labels[pi]['row'])==pi and int(proposal_labels[pi]['old_row'])==oi and int(proposal_labels[pi]['hour_0based'])==t and proposal_labels[pi]['family']==r['family'],'Proposal row labels')
        req(row(p,pi)=={t*103+j:a for j,a in exp.items()},'Numerical proposal exact coefficients')
        req(endpoints(p,pi)==(-math.inf if elo is None else float(elo),math.inf if ehi is None else float(ehi)),'Numerical proposal endpoints')
        req((elo is None or Q(p.row_lower[pi])==elo) and (ehi is None or Q(p.row_upper[pi])==ehi),'No endpoint conversion difference');rowcounts[r['family']]+=1
    req([Q(x) for x in p.lower[t*103:(t+1)*103]]==[Q(m.lower[j]) for j in cols] and [Q(x) for x in p.upper[t*103:(t+1)*103]]==[Q(m.upper[j]) for j in cols],'Proposal boxes')
req(len(set(seen_columns))==17304 and set(seen_columns)|set(fixed)==set(range(m.cols)),'Complete coordinate coverage')
for i,r in enumerate(nl):
    if r['family']=='fossil_energy_cap':continue
    raw=row(m,i)
    if not any(j not in fixed for j in raw):
        val=sum((a*fixed[j] for j,a in raw.items()),Q(0));lo,hi=endpoints(m,i);req((not math.isfinite(lo) or val>=Q(lo)) and (not math.isfinite(hi) or val<=Q(hi)),'Constant state row');constants.append(i)
req(len(constants)==16032 and len(all_free_rows)==len(set(all_free_rows))==18480 and set(constants)|set(all_free_rows)|{i for i,r in enumerate(nl) if r['family']=='fossil_energy_cap'}==set(range(m.rows)),'No proposal row omitted beyond cap/constant substitution')
req([r['row'] for r in js(OUT/'constant_rows.json')]==constants,'Constant row archive')
req(arr(OUT/'identity_proposal/objective.npz','objective')==tuple(cost[j] for j in seen_columns),'Proposal objective')
req(not any(arr(OUT/'identity_proposal/integrality.npz','integrality')),'Continuous proposal mask')
for e in manifest:req(sha(Path(e['path']))==e['sha256'],'Changed during review')
req(not (OUT/'execution_marker.json').exists(),'Concurrent execution')
report=dict(status='INDEPENDENT_BRANCH_FLOW_PREPARED_PASS',manifest_sha256=freeze['manifest_sha256'],bindings=len(manifest),cases=case_results,proposal_rows=18480,proposal_columns=17304,constant_rows=16032,proposal_families=dict(rowcounts),optimizer_calls=0,basis_reconstructions=0,elapsed_s=time.perf_counter()-start,source_sha256=sha(Path(__file__)))
output=ROOT/'results/research8h/branch_flow_prepared_review.json'
with output.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps(report))
