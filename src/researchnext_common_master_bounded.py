"""Execution-control successor; inherit the exact prepared master without reassembly."""
from __future__ import annotations
import argparse
from contextlib import redirect_stderr, redirect_stdout
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
import subprocess
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
ARM = ROOT/'results/research_next/common_master_bounded'; PRE = ARM/'prepared'; RUN = ARM/'run01'
PRIVATE = ROOT/'.work/researchnext_common_master_bounded/run01'
PROTOCOL = ROOT/'docs/research_next/COMMON_MASTER_BOUNDED_PROTOCOL.md'
INHERITED = ROOT/'results/research_next/common_master/prepared'
INHERITED_FREEZE_SHA = '39fe78153d0ecbb408035d074f35bc7566e4fd1c93dd3d80e118fedb6f90405c'
INHERITED_MANIFEST_SHA = 'c446c30eee6edc9b361b55bcb306bfdc8862916095d49a0ae26244753e265562'
INHERITED_SOURCE_SHA = '0eea17f50b859db72cf6de5ad337263f6c984f7c30830861b5feb7500c39b76e'
INHERITED_PROTOCOL_SHA = '7d28d1aff986a0cac5e2ff6179712abce7baf14ba3e3a6c3f02bd04372d9c3d2'
ORIGINAL = ROOT/'results/research_next/common_commitment/prepared'
AFFINE = ROOT/'results/research_next/union_affine_cut_schema2'
SCIP_PY = ROOT/'.work/scip_capability_env01/Scripts/python.exe'
LP_PY = Path('C:/Users/gmalkawi/OneDrive - Higher Colleges of Technology/Documents 1/ChatGPT/3/.work/solver_env/Scripts/python.exe')
SC = ROOT/'src/researchnext_common_scip.py'
SC_SHA = 'e80a8e80b1a25def3f94564b3a33527a367fc21e4bd87ea52bcdbc2f3e16d8d5'
RX = ROOT/'src/researchnext_repaired_crossworld_schema2.py'
RX_SHA = 'cf951d0dc5ac69df003b919df1e7d6400b71b25fc7e7e7ec7137b2480fc5b32d'
KERNEL = ROOT/'src/research8h_standalone_verify.py'
KERNEL_SHA = '708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'
BASE = ROOT/'src/researchnext_common_commitment.py'
BASE_SHA = '039af59750b4c165d877b9878ac14af02a202700b46739ba96a8914075ae3284'
WORLDS = ('identity','days_321'); TAU = Q.from_float(1e-5)
STATE_START = 6888; STATE_STOP = 18984; NB = 12096; H = 168; NC = NB+2*H
PHASE = 360.; MASTER_GUARD = 125.; LP_GUARD = 65.
SCIP_OPTIONS = {'limits/time':120.,'limits/solutions':1,'parallel/maxnthreads':1,'lp/threads':1,
    'randomization/randomseedshift':0,'randomization/permutationseed':0,'randomization/lpseed':0,'numerics/feastol':1e-8}
LP_OPTIONS = dict(time_limit=60.,threads=1,random_seed=0,presolve='on',solver='simplex')
WORLD_FILES = ('matrix.npz','bounds.npz','integrality.npz','model_metadata.json','native_inputs.npz','permutation.csv','row_metadata.csv.gz','native_spec.json')
JOINT_FILES = ('matrix.npz','bounds.npz','integrality.npz','column_maps.json','row_origins.json')
PINS = {
 'docs/research_next/CUT_CONSTRAINED_COMMITMENT_MASTER_PROPOSAL.md':'4abcf46f04bfdb9c58dac29ec357984af8e2e618e89d49b9956700d0ed7f7849',
 'results/research_next/common_commitment/prepared/input_manifest.json':'8ff99b1f4450ac15e91b26a261a85c98d574bbbdac3f7fe149efd9fd07204a5c',
 'results/research_next/common_commitment/prepared/prepared_freeze.json':'4f21891d7d1f1793dd92e5b830edf5b5cf62474e5521d788c9aec17929ea9a59',
 'results/research_next/common_commitment/INDEPENDENT_PREPARED_REVIEW.json':'956b37cbcdd49571a6a79611da197a5be840a5c2747ffbd60576c90805d58e6b',
 'results/research_next/union_affine_cut_schema2/prepared/input_manifest.json':'65235741d7860d9e99b0650c45ac209ba38ac028b758e4f12f1505ad2800f53c',
 'results/research_next/union_affine_cut_schema2/run01/identity_cut.json':'8ba409f8702486dcdebc7611a98609696348c41d46af8fa38d7e77b5614621cb',
 'results/research_next/union_affine_cut_schema2/run01/days_321_cut.json':'7fe192f2acd9ebd1e14eeecde3ece0e3d5d24ede8408e6047b1cb9dd597f30dd',
 'results/research_next/union_affine_cut_schema2/independent_postrun_review.json':'04b94ab9ca268615e1980066e6654fec58e01b92b96def0049a3dc94cff9a3f8',
 'results/research_next/scip_capability/setup01/capability.json':'c21670a55e870f5abef24efb74d52b2de17d9e235a82eec0da0bfd7a4e74ebed',
 'results/research_next/scip_capability/setup01/installed_payload_hashes.json':'a188acdf861190c3f77fc1122ab9bb08cf9ac1594d164c0daeb033e6e11ffe33',
}

def need(ok, message):
    if not ok: raise ValueError(message)
def utc(): return datetime.now(timezone.utc).isoformat()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p, value):
    with Path(p).open('x',encoding='utf-8') as f: json.dump(value,f,indent=2,allow_nan=False); f.write('\n')
def bind(p, data=None):
    p=Path(p).resolve(); data=p.read_bytes() if data is None else data
    return dict(path=str(p),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
def validate(items):
    need(len({x['path'].casefold() for x in items})==len(items),'Duplicate bindings')
    for item in items: need(bind(item['path'])==item,'Frozen bytes changed: '+item['path'])
def rat(q): return [str(q.numerator),str(q.denominator)]
def frac(x):
    if isinstance(x,dict): return Q(int(x['numerator']),int(x['denominator']))
    return Q(int(x[0]),int(x[1]))
def module(path,digest,name):
    need(sha(path)==digest,'Pinned helper changed: '+str(path))
    spec=importlib.util.spec_from_file_location(name,path); obj=importlib.util.module_from_spec(spec)
    sys.modules[name]=obj; spec.loader.exec_module(obj); return obj
def kernel(): return module(KERNEL,KERNEL_SHA,'common_master_exact_kernel')
def mask(v,folder,n): return tuple(v.vector(v.read_npz(folder/'integrality.npz',('integrality',))['integrality'],('|u1',),n,'full mask'))
def row(m,r): return {m.indices[k]:Q(m.data[k]) for k in range(m.indptr[r],m.indptr[r+1])}
def equal_row(m,r,terms,lo,hi): need(row(m,r)==terms and m.row_lower[r]==lo and m.row_upper[r]==hi,'Unsupported original row '+str(r))
def ceiling(q): return -((-q.numerator)//q.denominator)
def read_gzip(p):
    with gzip.open(p,'rt',encoding='utf-8') as f: return json.load(f)
def save_gzip(p,doc):
    with Path(p).open('xb') as raw:
        with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as f: f.write(json.dumps(doc,separators=(',',':'),allow_nan=False).encode())
def numeric_scalar(q):
    if q is None:return None
    value=float(q); need(math.isfinite(value) and abs(value)<1e20 and (q==0 or value!=0),'Unsupported binary64 encoding')
    return dict(exact=rat(q),binary64_hex=value.hex(),rounding_error=rat(Q(value)-q))
def exact_scalar(x): return None if x is None else frac(x['exact'])
def numeric_value(x,default): return default if x is None else float.fromhex(x['binary64_hex'])
def encoded_row(terms,lo,hi,family,provenance):
    terms={j:Q(a) for j,a in terms.items() if a}
    need(terms and all(type(j) is int and 0<=j<NC for j in terms),'Master sparse coordinates')
    return dict(family=family,terms=[[j,numeric_scalar(a)] for j,a in sorted(terms.items())],
        lower=numeric_scalar(lo),upper=numeric_scalar(hi),provenance=provenance)
def versions(exe,packages):
    code='import sys,json,importlib.metadata as m;print(json.dumps(dict(python=list(sys.version_info[:3]),packages={p:m.version(p) for p in '+repr(packages)+'})))'
    p=subprocess.run([str(exe),'-I','-c',code],capture_output=True,text=True,timeout=30)
    need(p.returncode==0,'Environment metadata query failed'); return json.loads(p.stdout)
def runtimes():
    sc=versions(SCIP_PY,['pyscipopt','numpy']); lp=versions(LP_PY,['numpy','scipy','highspy'])
    need(sc==dict(python=[3,12,14],packages={'pyscipopt':'6.2.1','numpy':'2.3.5'}),'SCIP runtime changed')
    need(lp==dict(python=[3,12,14],packages={'numpy':'2.3.5','scipy':'1.18.1','highspy':'1.12.0'}),'HiGHS runtime changed')
    return dict(master=sc,redispatch=lp,master_executable=str(SCIP_PY),LP_executable=str(LP_PY))

def capture_inputs():
    captured={}
    def capture(p,expected=None):
        p=Path(p).resolve(); data=p.read_bytes(); item=bind(p,data); key=str(p).casefold()
        if expected is not None: need(item==expected,'Captured historical bytes mismatch')
        need(key not in captured or captured[key][1]==item,'Conflicting input provenance'); captured[key]=(data,item)
    for rel,digest in PINS.items(): capture(ROOT/rel); need(captured[str((ROOT/rel).resolve()).casefold()][1]['sha256']==digest,'Historical pin changed')
    for folder,n in ((ORIGINAL,48),(AFFINE/'prepared',73)):
        doc=json.loads(captured[str((folder/'input_manifest.json').resolve()).casefold()][0]);need(len(doc['files'])==n,'Historical denominator')
        for item in doc['files']:capture(item['path'],item)
    installed=read(ROOT/'results/research_next/scip_capability/setup01/installed_payload_hashes.json')['files']
    for item in installed:
        path=ROOT/item['path'];capture(path);actual=captured[str(path.resolve()).casefold()][1]
        need(actual['sha256']==item['sha256'] and actual['bytes']==item['bytes'],'Installed SCIP bytes changed')
    for path,digest in ((SC,SC_SHA),(RX,RX_SHA),(KERNEL,KERNEL_SHA),(BASE,BASE_SHA)):
        capture(path);need(captured[str(path.resolve()).casefold()][1]['sha256']==digest,'Helper pin')
    for path in (Path(__file__),PROTOCOL,ARM/'synthetic_tests.json',SCIP_PY,LP_PY):capture(path)
    return captured

def assemble(v):
    models=[v.load_model(PRE/w) for w in WORLDS]; jm=v.load_model(PRE/'joint')
    need((jm.rows,jm.cols,len(jm.data))==(69362,33936,291176),'Joint model shape')
    need(mask(v,PRE/'joint',jm.cols)==tuple(int(STATE_START<=j<STATE_STOP) for j in range(jm.cols)),'Full joint bits')
    maps=read(PRE/'joint/column_maps.json');need(maps['worlds']==list(WORLDS),'World order')
    with (PRE/'gen.csv').open(encoding='utf-8-sig',newline='') as f: roster=list(csv.DictReader(f))
    gen={x['GEN UID']:x for x in roster};need(len(gen)==len(roster),'Unique native names')
    records=[]; state_sets=[]; metas=[]; expected_roster=None
    for wi,(world,m) in enumerate(zip(WORLDS,models)):
        need((m.rows,m.cols,len(m.data))==(34681,23016,145588),'World dimensions')
        need(mask(v,PRE/world,m.cols)==tuple(int(STATE_START<=j<STATE_STOP) for j in range(m.cols)),'World full bits')
        mp=maps['original_to_joint'][wi];need(len(mp)==m.cols and len(set(mp))==m.cols and all(0<=j<jm.cols for j in mp),'Map domain')
        need(mp[STATE_START:STATE_STOP]==list(range(STATE_START,STATE_STOP)),'All shared state coordinates')
        need(all(m.lower[j]==jm.lower[mp[j]] and m.upper[j]==jm.upper[mp[j]] for j in range(m.cols)),'Original mapped boxes')
        meta=read(PRE/world/'model_metadata.json');metas.append(meta)
        names=meta['unit_names'];therm=meta['thermal_unit_names'];fossil=meta['fossil_units']
        need(len(names)==len(set(names))==41 and len(therm)==len(set(therm))==24 and len(fossil)==len(set(fossil))==23,'Roster sizes')
        need(names[:24]==therm and [n for n in names if gen[n]['Fuel'] in ('Coal','NG','Oil')]==fossil,'Ordered native partition')
        need(set(therm)-set(fossil)=={'121_NUCLEAR_1'} and gen['121_NUCLEAR_1']['Fuel']=='Nuclear','Nuclear partition')
        need(meta['offsets']==dict(P=0,U=6888,Y=10920,Z=14952,theta=18984),'Coordinate offsets')
        if expected_roster is None:expected_roster=(names,therm,fossil)
        else:need(expected_roster==(names,therm,fossil),'Unchanged world rosters')
        state=[]
        for r in range(m.rows):
            terms=row(m,r)
            if terms and all(STATE_START<=j<STATE_STOP for j in terms):
                need(all(a.denominator==1 for a in terms.values()),'Integral state coefficients')
                need(all(not math.isfinite(x) or Q(x).denominator==1 for x in (m.row_lower[r],m.row_upper[r])),'Integral state endpoints')
                state.append((r,terms,m.row_lower[r],m.row_upper[r]))
        need(len(state)==16032,'Complete state-row count');state_sets.append(state)
        need(all(0<=m.lower[j]<=m.upper[j]<=1 and Q(m.lower[j]).denominator==Q(m.upper[j]).denominator==1 for j in range(STATE_START,STATE_STOP)),'Integral state boxes')
        need(all(m.lower[j]==0 and m.upper[j]==1 for j in range(6888,6912)),'Mature free U0')
        need(all(m.lower[j]==m.upper[j]==0 for j in list(range(10920,10944))+list(range(14952,14976))),'Fixed initial Y0/Z0')
        with gzip.open(PRE/world/'row_metadata.csv.gz','rt',encoding='utf-8-sig',newline='') as f:labels=list(csv.DictReader(f))
        need(len(labels)==m.rows and [int(x['row']) for x in labels]==list(range(m.rows)),'Row label denominator')
        index={}
        for x in labels:
            if x['family'] not in ('aggregate_balance','thermal_upper','thermal_lower','fossil_energy_cap'):continue
            key=(x['family'],int(x['hour_0based']),x['uid']);need(key not in index,'Unique selected row');index[key]=int(x['row'])
        need(len(index)==8233,'Physical premise row count')
        caps=[r for (fam,t,n),r in index.items() if fam=='fossil_energy_cap'];need(len(caps)==1,'One cap')
        fi=[names.index(n) for n in fossil];ni=therm.index('121_NUCLEAR_1');cap=caps[0]
        equal_row(m,cap,{41*t+j:Q(1) for t in range(H) for j in fi},-math.inf,23195.)
        hours=[]
        for t in range(H):
            ar=index[('aggregate_balance',t,'ALL')];equal_row(m,ar,{41*t+j:Q(1) for j in range(41)},m.row_lower[ar],m.row_lower[ar])
            need(math.isfinite(m.row_lower[ar]),'Finite aggregate endpoint');a=[];b=[];sources=[]
            for k,name in enumerate(therm):
                p=41*t+k;u=6888+24*t+k;lr=index[('thermal_lower',t,name)];ur=index[('thermal_upper',t,name)]
                av=Q(gen[name]['PMin MW']);bv=Q(gen[name]['PMax MW'])
                need(av.denominator==bv.denominator==1 and 0<=av<=bv,'Exact nonnegative integer nameplates')
                equal_row(m,lr,{p:Q(-1),**({u:av} if av else {})},-math.inf,0.)
                equal_row(m,ur,{p:Q(1),**({u:-bv} if bv else {})},-math.inf,0.)
                a.append(av);b.append(bv);sources.append(dict(uid=name,P_column=p,U_column=u,lower_row=lr,upper_row=ur))
            need(all(math.isfinite(m.upper[41*t+j]) for j in range(24,41)),'Finite 17 nonthermal boxes')
            need(all(math.isfinite(m.lower[41*t+j]) for j in fi),'Finite fossil lower boxes')
            rho=Q(m.row_lower[ar])-sum((Q(m.upper[41*t+j]) for j in range(24,41)),Q(0))-19*TAU
            direct=sum((Q(m.lower[41*t+j])-TAU for j in fi),Q(0));upper=sum((b[j] for j in fi),Q(0))+23*TAU
            hours.append(dict(hour=t,rho=rat(rho),box_lower=rat(direct),box_upper=rat(upper),
                a=[rat(x) for x in a],b=[rat(x) for x in b],aggregate_row=ar,nonthermal_upper_columns=[41*t+j for j in range(24,41)],
                fossil_lower_columns=[41*t+j for j in fi],thermal_rows=sources,losses=dict(aggregate=1,nonthermal_boxes=17,nuclear_upper=1,total_rho=19,all_thermal_capacity_total=42)))
        records.append(dict(world=world,cap_row=cap,fossil_indices=fi,nuclear_index=ni,hours=hours))
    need(state_sets[0]==state_sets[1],'State rows must be exactly identical in both worlds')
    need(all(models[0].lower[j]==models[1].lower[j] and models[0].upper[j]==models[1].upper[j] for j in range(STATE_START,STATE_STOP)),'Same state boxes')
    need(all(records[0]['hours'][0][k]==rec['hours'][t][k] for rec in records for t in range(H) for k in ('a','b')),'One unchanged thermal coefficient tuple')
    rows=[]
    for r,terms,lo,hi in state_sets[0]:
        rows.append(encoded_row({j-STATE_START:a for j,a in terms.items()},Q(lo) if math.isfinite(lo) else None,Q(hi) if math.isfinite(hi) else None,'state',dict(original_row=r,both_worlds=True,integer_tau_equivalence=True)))
    boxes=[dict(lower=numeric_scalar(Q(models[0].lower[j])),upper=numeric_scalar(Q(models[0].upper[j])),kind='B') for j in range(STATE_START,STATE_STOP)]
    for t in range(H):
        h=records[0]['hours'][t];threshold=max(0,ceiling(max(frac(rec['hours'][t]['rho']) for rec in records)-23*TAU))
        rows.append(encoded_row({24*t+k:frac(x) for k,x in enumerate(h['b'])},Q(threshold),None,'integer_capacity',dict(hour=t,total_tau_loss=42,binary_only_ceiling=True)))
    for wi,world in enumerate(WORLDS):
        cut=read(PRE/(world+'_cut.json'))
        need(cut['status']=='VERIFIED_GLOBAL_EXPANDED_AFFINE_NECESSARY_CUT' and cut['world']==world and frac(cut['tau'])==TAU and frac(cut['cap'])==Q(23195)+TAU and cut['new_derived_row_expansion']==0,'Cut scope/tolerance')
        need(cut['all_nonU_coefficients_exact_zero'] and cut['all_endpoint_multipliers_nonnegative'],'Accepted cut proof flags')
        terms={x['column']-STATE_START:frac(x['coefficient']) for x in cut['coefficients']}
        need(len(terms)==len(cut['coefficients'])==82 and all(0<=j<4032 and a>0 for j,a in terms.items()),'Cut U support')
        rows.append(encoded_row(terms,None,frac(cut['cap'])-frac(cut['alpha']),'inherited_cut',dict(world=world,cut_sha256=sha(PRE/(world+'_cut.json')),extra_tau=0)))
    for wi,rec in enumerate(records):
        fi=rec['fossil_indices'];ni=rec['nuclear_index']
        for t,h in enumerate(rec['hours']):
            f=NB+H*wi+t;a=list(map(frac,h['a']));b=list(map(frac,h['b']))
            boxes.append(dict(lower=numeric_scalar(frac(h['box_lower'])),upper=numeric_scalar(frac(h['box_upper'])),kind='C'))
            rows.append(encoded_row({f:Q(1),24*t+ni:b[ni]},frac(h['rho']),None,'F_balance',dict(world=wi,hour=t,loss=19)))
            rows.append(encoded_row({f:Q(1),**{24*t+j:-a[j] for j in fi}},-23*TAU,None,'F_thermal_lower',dict(world=wi,hour=t,loss=23)))
            rows.append(encoded_row({f:Q(1),**{24*t+j:-b[j] for j in fi}},None,23*TAU,'F_thermal_upper',dict(world=wi,hour=t,loss=23)))
        rows.append(encoded_row({NB+H*wi+t:Q(1) for t in range(H)},None,Q(23195)+TAU,'F_cap',dict(world=wi,original_cap_row=rec['cap_row'],loss=1)))
    need(len(rows)==17212 and len(boxes)==12432,'Prospective master denominator')
    return dict(rows=rows,boxes=boxes,columns=NC,binary_columns=NB,objective='all_zero',tau=rat(TAU),semantics='exact rational necessary master; numeric fields only propose a candidate'),dict(worlds=records,integer_state_rows=16032,selected_physical_rows_per_world=8233,state_tau_equivalence=TAU<1,all_12096_original_states=True,unit_roster=expected_roster)

def prepare():
    started=time.perf_counter();need(not PRE.exists() and not RUN.exists(),'One preparation only')
    captured={}
    def capture(path,expected=None):
        path=Path(path).resolve();data=path.read_bytes();item=bind(path,data);key=str(path).casefold()
        if expected is not None:need(item==expected,'Inherited captured bytes mismatch')
        need(key not in captured or captured[key][1]==item,'Conflicting inherited bindings');captured[key]=(data,item)
        return data,item
    for path,digest in ((INHERITED/'prepared_freeze.json',INHERITED_FREEZE_SHA),(INHERITED/'input_manifest.json',INHERITED_MANIFEST_SHA),
                        (ROOT/'src/researchnext_common_master.py',INHERITED_SOURCE_SHA),(ROOT/'docs/research_next/COMMON_MASTER_PROTOCOL.md',INHERITED_PROTOCOL_SHA)):
        data,item=capture(path);need(item['sha256']==digest,'Inherited source/freeze pin')
    inherited=json.loads(captured[str((INHERITED/'input_manifest.json').resolve()).casefold()][0])['files'];need(len(inherited)==200,'Inherited denominator')
    for item in inherited:capture(item['path'],item)
    for path in (Path(__file__),PROTOCOL,ARM/'synthetic_tests.json',ARM/'SOURCE_DIFF.patch',ARM/'PROTOCOL_DIFF.patch'):capture(path)
    initial=[x[1] for x in captured.values()]
    receipt=read(ARM/'synthetic_tests.json');need(receipt['source_sha256']==sha(__file__) and receipt['protocol_sha256']==sha(PROTOCOL),'Fixture source binding')
    PRE.mkdir(parents=True);save(PRE/'successor_preparation_started.json',dict(utc=utc(),optimizer_calls=0,source_sha256=sha(__file__),scientific_reassembly=False))
    copies=[]
    for item in inherited:
        src=Path(item['path'])
        if not src.is_relative_to(INHERITED):continue
        rel=src.relative_to(INHERITED);dst=PRE/rel;dst.parent.mkdir(parents=True,exist_ok=True)
        data,descriptor=captured[str(src.resolve()).casefold()];dst.write_bytes(data)
        need(bind(dst)['sha256']==descriptor['sha256'],'Byte-inherited payload differs');copies.append(dict(original=descriptor,copy=bind(dst)))
    need(len(copies)==29,'All original prepared payloads except manifest/freeze')
    save(PRE/'successor_copy_provenance.json',dict(copies=copies,master_reassembled=False,new_scientific_selection=False))
    save(PRE/'execution_controls.json',dict(exactly_one_returned_solution=True,owned_child_timeout='remaining common monotonic phase',
        late_positive_admission=False,phase_seconds=PHASE,master_start_guard=MASTER_GUARD,LP_start_guard=LP_GUARD,
        cleanup_may_exceed_deadline_but_no_late_positive=True,source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL)))
    validate(initial);items=initial+[bind(p) for p in PRE.rglob('*') if p.is_file()];validate(items)
    save(PRE/'input_manifest.json',dict(files=items));validate(items)
    save(PRE/'prepared_freeze.json',dict(utc=utc(),source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),manifest_sha256=sha(PRE/'input_manifest.json'),
        bindings=len(items),copies=len(copies),rows=17212,columns=NC,binaries=NB,optimizer_calls=0,backend_imports=0,elapsed_seconds=time.perf_counter()-started,
        inherited_freeze_sha256=INHERITED_FREEZE_SHA,master_reassembled=False,master_sha256=sha(PRE/'master.json.gz'),
        separate_independent_prepared_review_and_explicit_execution_GO_required=True))
    print(json.dumps(dict(status='PREPARED_NO_OPTIMIZER',freeze_sha256=sha(PRE/'prepared_freeze.json'),bindings=len(items))),flush=True)

def check_exact_rows(model,point):
    issues=[]
    for j,(x,box) in enumerate(zip(point,model['boxes'])):
        if x<exact_scalar(box['lower']) or x>exact_scalar(box['upper']) or (box['kind']=='B' and x not in (0,1)):issues.append(dict(column=j))
    for r,entry in enumerate(model['rows']):
        activity=sum((exact_scalar(a)*point[j] for j,a in entry['terms']),Q(0));lo=exact_scalar(entry['lower']);hi=exact_scalar(entry['upper'])
        if (lo is not None and activity<lo) or (hi is not None and activity>hi):issues.append(dict(row=r,family=entry['family']))
    return issues
def smallest_auxiliary(bits,hours,fi,ni,tau):
    values=[]
    for t,h in enumerate(hours):
        a=list(map(frac,h['a']));b=list(map(frac,h['b']));u=bits[24*t:24*(t+1)]
        values.append(max(frac(h['box_lower']),frac(h['rho'])-b[ni]*u[ni],sum((a[j]*u[j] for j in fi),Q(0))-len(fi)*tau))
    return values
def nominate(raw,model,premises):
    if len(raw)!=NC or not all(math.isfinite(x) for x in raw):return dict(accepted=False,reason='invalid_raw_shape_or_nonfinite'),None
    bits=[]
    for x in raw[:NB]:
        choices=[k for k in (0,1) if abs(Q(x)-k)<=TAU]
        if len(choices)!=1:return dict(accepted=False,reason='nonintegral_state'),None
        bits.append(Q(choices[0]))
    aux=[]
    for rec in premises['worlds']:aux+=smallest_auxiliary(bits,rec['hours'],rec['fossil_indices'],rec['nuclear_index'],TAU)
    point=bits+aux;issues=check_exact_rows(model,point)
    return dict(accepted=not issues,issues=issues,original_shared_state_values=[int(x) for x in bits],auxiliary_exact=[rat(x) for x in aux],
        auxiliary_rule='deterministic componentwise minimum, not physical redispatch',no_extra_tau=True),bits if not issues else None

def load_prepared(expected):
    need(sha(PRE/'prepared_freeze.json')==expected,'Trusted freeze digest');f=read(PRE/'prepared_freeze.json')
    need(f['source_sha256']==sha(__file__) and f['protocol_sha256']==sha(PROTOCOL),'Frozen source/protocol')
    need(f['manifest_sha256']==sha(PRE/'input_manifest.json'),'Frozen manifest');items=read(PRE/'input_manifest.json')['files'];validate(items)
    return items,read_gzip(PRE/'master.json.gz'),read(PRE/'premises.json')
def guard(deadline,needed=0.):
    remaining=deadline-time.perf_counter();need(remaining>=needed,'Phase start/progress guard');return remaining
def sole_solution(count):return type(count) is int and count==1
def phase_admission(accepted,deadline,now=None):
    when=time.perf_counter() if now is None else now
    return dict(accepted_common=bool(accepted and when<=deadline),common_verdict='VERIFIED_EXPANDED_COMMON_COMMITMENT' if accepted and when<=deadline else 'UNKNOWN',
                phase_deadline_met=when<=deadline,admission_monotonic=when,deadline_monotonic=deadline)
def wait_owned(child,deadline,clock=time.perf_counter):
    timeout=max(0.,deadline-clock())
    try:
        child.wait(timeout=timeout)
        return dict(timed_out=False,returncode=child.returncode,owned_pid=child.pid)
    except subprocess.TimeoutExpired:
        child.kill();child.wait()
        return dict(timed_out=True,returncode=child.returncode,owned_pid=child.pid,terminated_only_owned_child=True)

def master_backend(scip,np,model,deadline):
    h=scip.Model('necessary_common_commitment_master');h.hideOutput();h.setLogfile(str(PRIVATE/'master.log'))
    need([h.getMajorVersion(),h.getMinorVersion(),h.getTechVersion()]==[10,0,2],'SCIP version')
    before=h.getParams();h.setEmphasis(scip.SCIP_PARAMEMPHASIS.FEASIBILITY,quiet=True)
    for key,value in SCIP_OPTIONS.items():h.setParam(key,value)
    after=h.getParams();need(all(after[k]==v for k,v in SCIP_OPTIONS.items()),'SCIP options')
    save(RUN/'master_parameters.json',dict(explicit=SCIP_OPTIONS,defaults=before,after_setters=after,changed={k:dict(before=before[k],after=after[k]) for k in before if before[k]!=after[k]}))
    variables=[h.addVar(name=f'x{j}',lb=numeric_value(b['lower'],-math.inf),ub=numeric_value(b['upper'],math.inf),obj=0.,vtype=b['kind']) for j,b in enumerate(model['boxes'])]
    h.setMinimize();constraints=[];encoding=[]
    for r,entry in enumerate(model['rows']):
        expr=scip.quicksum(numeric_value(a,0.)*variables[j] for j,a in entry['terms']);lo=entry['lower'];hi=entry['upper']
        sides=[('=',lo)] if lo is not None and hi is not None and lo==hi else ([('>',lo)] if lo is not None else [])+([('<',hi)] if hi is not None else [])
        for sense,value in sides:
            rhs=numeric_value(value,0.);cons=(expr==rhs) if sense=='=' else ((expr>=rhs) if sense=='>' else (expr<=rhs))
            constraints.append(h.addCons(cons,name=f'r{len(constraints)}'));encoding.append(dict(master_row=r,sense=sense,rhs_hex=rhs.hex()))
        if r%1024==0:guard(deadline)
    need(h.getStageName()=='PROBLEM' and h.getNSols()==0,'No transformed/warm-start model')
    need(len(h.getVars(transformed=False))==NC and len(h.getConss(transformed=False))==len(encoding),'Backend shape')
    need(h.getObjectiveSense()=='minimize' and h.getObjoffset(original=True)==0,'Zero objective sense')
    readback=[];infinity=h.infinity()
    for j,(x,b) in enumerate(zip(variables,model['boxes'])):
        need(x.isOriginal() and x.name==f'x{j}' and x.getLbOriginal()==numeric_value(b['lower'],-math.inf) and x.getUbOriginal()==numeric_value(b['upper'],math.inf),'Backend numeric boxes')
        need(x.getObj()==0 and x.vtype()==('BINARY' if j<NB else 'CONTINUOUS'),'Backend objective/full binary declarations')
    for k,(cons,mapping) in enumerate(zip(constraints,encoding)):
        r=mapping['master_row'];actual=sorted((int(name[1:]),float(a)) for name,a in h.getValsLinear(cons).items())
        want=[(j,numeric_value(a,0.)) for j,a in model['rows'][r]['terms']]
        need(cons.isOriginal() and cons.name==f'r{k}' and actual==want,'Numeric search coefficient readback')
        rhs=float.fromhex(mapping['rhs_hex']);sense=mapping['sense'];lo,hi=(rhs,rhs) if sense=='=' else ((rhs,infinity) if sense=='>' else (-infinity,rhs))
        need((h.getLhs(cons),h.getRhs(cons))==(lo,hi),'Numeric endpoint readback')
        readback.append(dict(**mapping,terms=[[j,a.hex()] for j,a in actual],lower_hex=lo.hex(),upper_hex=hi.hex()))
        if k%1024==0:guard(deadline)
    need(h.getParams()==after,'Options altered during construction')
    save_gzip(RUN/'master_backend_readback.json.gz',dict(rows=readback,boxes=[dict(lower_hex=x.getLbOriginal().hex(),upper_hex=x.getUbOriginal().hex(),objective_hex=x.getObj().hex(),type=x.vtype()) for x in variables],
        nominal_numeric_search_only=True,exact_rational_master_sha256=sha(PRE/'master.json.gz'),all_actual_numeric_coefficients_read_back=True))
    return h,variables,after

def run(expected):
    started=time.perf_counter();deadline=started+PHASE;need(Path(sys.executable).resolve()==SCIP_PY.resolve(),'Use pinned SCIP interpreter')
    need(not RUN.exists() and not PRIVATE.exists(),'Single fresh execution');items,model,premises=load_prepared(expected)
    need(read(PRE/'plan.json')['runtime']==runtimes(),'Runtime metadata changed');transport=[bind(PRE/'prepared_freeze.json'),bind(PRE/'input_manifest.json')]
    RUN.mkdir();PRIVATE.mkdir(parents=True);save(RUN/'execution_started.json',dict(utc=utc(),freeze_sha256=expected,source_sha256=sha(__file__),phase_seconds=PHASE))
    ledger=dict(master_attempted=0,master_returned=0,LP_worker_invoked=0);result=dict(common_verdict='UNKNOWN',accepted_common=False);h=None;stage='imports'
    try:
        with (PRIVATE/'startup.log').open('x',encoding='utf-8') as f,redirect_stdout(f),redirect_stderr(f):
            import numpy as np
            import pyscipopt as scip
        stage='master_backend';h,variables,params=master_backend(scip,np,model,deadline)
        save(RUN/'master_call_ready.json',dict(utc=utc(),remaining=guard(deadline,MASTER_GUARD),not_an_actual_call=True));guard(deadline,MASTER_GUARD)
        need(h.getParams()==params,'Pre-call option identity');stage='master_call';clock=time.perf_counter();ledger.update(master_attempted=1,master_started_utc=utc())
        try:h.optimize()
        finally:ledger['master_actual_seconds']=time.perf_counter()-clock
        ledger['master_returned']=1;result.update(master_status=str(h.getStatus()),master_solutions=int(h.getNSols()),nodes=int(h.getNNodes()),LP_iterations=int(h.getNLPIterations()))
        save(RUN/'master_solver_returned.json',dict(**result,ledger=ledger,parameters_after_call=h.getParams()))
        result['sole_returned_solution']=sole_solution(result['master_solutions'])
        if result['sole_returned_solution']:
            guard(deadline)
            stage='master_exact_nomination';sol=h.getBestSol();raw=[float(h.getSolVal(sol,x)) for x in variables]
            np.savez_compressed(RUN/'master_raw_solution.npz',vector=np.array(raw));admission,bits=nominate(raw,model,premises);save(RUN/'master_exact_admission.json',admission)
            result['master_candidate_accepted']=admission['accepted']
            if bits is not None:
                stage='LP_worker_preparation';save(RUN/'LP_request.json',dict(freeze_sha256=expected,source_sha256=sha(__file__),deadline_monotonic=deadline,
                    state_values=[int(x) for x in bits],master_admission_sha256=sha(RUN/'master_exact_admission.json'),master_raw_sha256=sha(RUN/'master_raw_solution.npz'),conditional_on_exact_admission=True))
                request_sha=sha(RUN/'LP_request.json');save(RUN/'LP_launch_ready.json',dict(utc=utc(),remaining=guard(deadline,LP_GUARD),not_a_solver_call=True))
                guard(deadline,LP_GUARD);ledger['LP_worker_invoked']=1;stage='LP_worker'
                with (PRIVATE/'LP_worker.log').open('x',encoding='utf-8') as log:
                    child=subprocess.Popen([str(LP_PY),'-I',str(Path(__file__).resolve()),'--redispatch-worker','--expected-freeze-sha256',expected,'--expected-request-sha256',request_sha],stdout=log,stderr=log)
                    worker=wait_owned(child,deadline)
                ledger['LP_worker']=worker;ledger['LP_worker_exit_code']=child.returncode
                save(RUN/'LP_worker_closed.json',dict(utc=utc(),**worker))
                if (RUN/'lp/completion.json').exists():ledger['LP']=read(RUN/'lp/completion.json')['call_ledger']
                elif (RUN/'lp/failure.json').exists():ledger['LP']=read(RUN/'lp/failure.json').get('call_ledger',dict(attempted=0,stage='before_LP_call_ledger'))
                elif (RUN/'lp/invocation_boundary.json').exists():ledger['LP']=dict(attempted='UNKNOWN_ZERO_OR_ONE',returned=0,invocation_boundary_reached=True,worker_interrupted=True)
                else:ledger['LP']=dict(attempted=0,returned=0,invocation_boundary_reached=False)
                if child.returncode==0 and not worker['timed_out']:
                    r=read(RUN/'lp/completion.json')['final_admission'];result['accepted_common']=r['accepted_common'];result['common_verdict']=r['common_verdict']
                else:result['worker_failure_preserved']=True
        else:result['nomination_reason']='NO_SOLUTION' if result['master_solutions']==0 else 'MULTIPLE_SOLUTIONS_NOT_ADMITTED'
        validate(items);validate(transport);result.update(phase_admission(result['accepted_common'],deadline));result['provisional_until_completion']=True;save(RUN/'result.json',result)
        final=phase_admission(result['accepted_common'],deadline)
        elapsed=time.perf_counter()-started;save(RUN/'completion.json',dict(utc=utc(),status='CLOSED_PENDING_INDEPENDENT_REVIEW',ledger=ledger,phase_seconds=elapsed,
            soft_phase_overrun=max(0,elapsed-PHASE),master_soft_overrun=max(0,ledger.get('master_actual_seconds',0)-120),all_frozen_bytes_unchanged=True,
            no_retries=True,no_exact_negative=True,final_write_cleanup_outside_sample=True,final_admission=final))
        print(json.dumps(final),flush=True)
    except BaseException as exc:
        save(RUN/'failure.json',dict(stage=stage,error_type=type(exc).__name__,message=str(exc),ledger=ledger,common_verdict='UNKNOWN',no_retry=True));raise
    finally:
        if h is not None:h.freeProb()
        save(RUN/'private_log_receipt.json',dict(raw_logs_public=False,files=[bind(p) for p in PRIVATE.rglob('*') if p.is_file()]))

def redispatch_worker(expected,request_digest):
    need(Path(sys.executable).resolve()==LP_PY.resolve(),'Pinned LP environment');items,model,premises=load_prepared(expected)
    need(sha(RUN/'LP_request.json')==request_digest,'External request binding');request=read(RUN/'LP_request.json')
    need(request['freeze_sha256']==expected and request['source_sha256']==sha(__file__),'Request provenance')
    need(request['master_admission_sha256']==sha(RUN/'master_exact_admission.json') and request['master_raw_sha256']==sha(RUN/'master_raw_solution.npz'),'Master output binding')
    import numpy as np
    import highspy
    raw=np.load(RUN/'master_raw_solution.npz',allow_pickle=False)['vector'];admission,bits=nominate([float(x) for x in raw],model,premises)
    need(admission==read(RUN/'master_exact_admission.json') and bits is not None and [int(x) for x in bits]==request['state_values'],'Same sole exact candidate')
    deadline=request['deadline_monotonic'];folder=RUN/'lp';need(not folder.exists(),'One LP worker');folder.mkdir();(PRIVATE/'lp').mkdir()
    rx=module(RX,RX_SHA,'common_master_cached_highs_transport');rx.PRE=PRE;rx.RUN=folder;rx.PRIVATE=PRIVATE/'lp';rx.OPTIONS=LP_OPTIONS
    v=kernel();m=v.load_model(PRE/'joint');fullmask=mask(v,PRE/'joint',m.cols);fixed={STATE_START+j:float(x) for j,x in enumerate(bits)}
    lower=list(m.lower);upper=list(m.upper)
    for j,x in fixed.items():need(lower[j]<=x<=upper[j],'Fixed state box');lower[j]=upper[j]=x
    np.savez_compressed(folder/'fixed_bounds.npz',column_lower=np.array(lower),column_upper=np.array(upper))
    save(folder/'fixed_schedule.json',dict(master_admission_sha256=sha(RUN/'master_exact_admission.json'),fixed_columns=[dict(column=j,value=int(x)) for j,x in fixed.items()]))
    stages=[];ledger=dict(attempted=0,returned=0);h=highspy.Highs();result=dict(accepted_common=False,common_verdict='UNKNOWN')
    def checkpoint(label,record=True,**ignored):
        remaining=guard(deadline)
        if record:stages.append(dict(label=label,remaining=remaining))
    try:
        rx.build_readback(h,highspy,np,m,fullmask,fixed,tuple(lower),tuple(upper),checkpoint)
        save(folder/'call_ready.json',dict(utc=utc(),remaining=guard(deadline,LP_GUARD),not_actual_call=True));guard(deadline,LP_GUARD)
        save(folder/'invocation_boundary.json',dict(utc=utc(),not_proof_call_started=True,meaning='immediately before last phase guard and sole h.run'))
        guard(deadline,LP_GUARD)
        ledger.update(attempted=1,started_utc=utc());clock=time.perf_counter()
        try:status=h.run()
        finally:ledger['actual_seconds']=time.perf_counter()-clock
        ledger['returned']=1;sol=h.getSolution();result.update(status=str(h.getModelStatus()),run_status=str(status),valid_solution=bool(sol.value_valid))
        save(folder/'solver_returned.json',result)
        if sol.value_valid:
            raw=[float(x) for x in sol.col_value];np.savez_compressed(folder/'raw_solution.npz',vector=np.array(raw))
            candidate=rx.restore_prescribed(raw,fixed,TAU)
            if candidate is not None:
                sc=module(SC,SC_SHA,'common_master_unchanged_acceptance');sc.PRE=PRE;sc.RUN=folder
                checked=sc.candidate_check(v,np,np.array(candidate),fullmask)
                need(all(candidate[j]==x for j,x in fixed.items()),'Prescribed complete shared states')
                save(folder/'prescribed_restoration.json',dict(all12096_fixed_states=True,continuous_raw_bytes_unchanged=True,raw_sha256=sha(folder/'raw_solution.npz'),prescribed_within_exact_tau=True))
                result.update(phase_admission(checked['accepted'],deadline))
        validate(items);save(folder/'stage_timings.json',stages);result.update(phase_admission(result['accepted_common'],deadline));result['provisional_until_completion']=True;save(folder/'result.json',result)
        final=phase_admission(result['accepted_common'],deadline)
        remaining=deadline-time.perf_counter()
        save(folder/'completion.json',dict(utc=utc(),call_ledger=ledger,LP_soft_overrun=max(0,ledger.get('actual_seconds',0)-60),remaining_phase=remaining,no_retry=True,no_negative_claim=True,
            final_admission=final,final_write_outside_sample=True))
    except BaseException as exc:
        save(folder/'failure.json',dict(error_type=type(exc).__name__,message=str(exc),call_ledger=ledger,common_verdict='UNKNOWN',no_retry=True));raise

def self_test():
    need(not (ARM/'synthetic_tests.json').exists(),'One invented fixture run');checks=[]
    need([sole_solution(x) for x in (0,1,2,10,True,1.)]==[False,True,False,False,False,False],'Exactly one returned integer solution count')
    checks.append('zero/one/multiple solver solutions; no best-of-batch selection')
    need(phase_admission(True,2.,1.)['accepted_common'] and phase_admission(True,2.,2.)['accepted_common'],'Within/deadline boundary admission')
    need(not phase_admission(True,2.,3.)['accepted_common'] and not phase_admission(False,2.,1.)['accepted_common'],'Late or mathematically rejected positives remain UNKNOWN')
    provisional=phase_admission(True,2.,1.);final=phase_admission(provisional['accepted_common'],2.,3.)
    need(final['common_verdict']=='UNKNOWN','Late final closure overrides provisional positive');checks.append('early/boundary/late authoritative closure')
    class Child:
        pid=123456
        def __init__(self,timeout):self.timeout=timeout;self.calls=[];self.returncode=None
        def wait(self,timeout=None):
            self.calls.append(('wait',timeout))
            if self.timeout and len(self.calls)==1:raise subprocess.TimeoutExpired('invented-child',timeout)
            self.returncode=-9 if self.timeout else 0;return self.returncode
        def kill(self):self.calls.append(('kill',None))
    normal=Child(False);receipt=wait_owned(normal,10.,lambda:4.)
    need(not receipt['timed_out'] and normal.calls==[('wait',6.)],'Remaining phase wait')
    expired=Child(True);receipt=wait_owned(expired,10.,lambda:11.)
    need(receipt['timed_out'] and receipt['terminated_only_owned_child'] and expired.calls==[('wait',0.),('kill',None),('wait',None)],'Only owned expired child terminated and reaped')
    checks.append('invented owned-child normal return and zero-remaining timeout termination; no process launched')
    ARM.mkdir(parents=True,exist_ok=True);save(ARM/'synthetic_tests.json',dict(status='PASS',utc=utc(),source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),checks=checks,scientific_inputs_read=0,optimizer_calls=0))
    print(json.dumps(dict(status='PASS_SYNTHETIC_ONLY',groups=len(checks))),flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    for flag in ('self-test','prepare-only','run-prepared','redispatch-worker'):g.add_argument('--'+flag,action='store_true')
    p.add_argument('--expected-freeze-sha256');p.add_argument('--expected-request-sha256');a=p.parse_args()
    if a.self_test:self_test()
    elif a.prepare_only:prepare()
    else:
        need(a.expected_freeze_sha256 is not None,'External freeze required')
        if a.run_prepared:run(a.expected_freeze_sha256)
        else:need(a.expected_request_sha256 is not None,'External request required');redispatch_worker(a.expected_freeze_sha256,a.expected_request_sha256)
if __name__=='__main__':
    try:main()
    except BaseException as exc:
        folder=RUN if RUN.exists() else PRE if PRE.exists() else ARM;folder.mkdir(parents=True,exist_ok=True)
        if not (folder/'failure.json').exists():save(folder/'failure.json',dict(error_type=type(exc).__name__,message=str(exc),no_retry=True,no_scientific_conclusion=True))
        raise
