"""One phase-I multiplier proposal for the immutable common-master nominee."""
from __future__ import annotations
import argparse
import csv
from datetime import datetime,timezone
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import time

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
ARM=ROOT/'results/research_next/common_phase1';PRE=ARM/'prepared';RUN=ARM/'run01'
PRIVATE=ROOT/'.work/researchnext_common_phase1/run01'
PROTOCOL=ROOT/'docs/research_next/COMMON_PHASE1_PROTOCOL.md'
MASTER=ROOT/'results/research_next/common_master_bounded'
ORIGINAL=ROOT/'results/research_next/common_commitment'
PYTHON=Path('C:/Users/gmalkawi/OneDrive - Higher Colleges of Technology/Documents 1/ChatGPT/3/.work/solver_env/Scripts/python.exe')
KERNEL=ROOT/'src/research8h_standalone_verify.py';KERNEL_SHA='708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'
TRANSPORT=ROOT/'src/researchnext_repaired_crossworld_schema2.py';TRANSPORT_SHA='cf951d0dc5ac69df003b919df1e7d6400b71b25fc7e7e7ec7137b2480fc5b32d'
TAU=Q.from_float(1e-5);PHASE=180.;START_GUARD=65.;MAX_BITS=8192
OPTIONS=dict(time_limit=60.,threads=1,random_seed=0,presolve='on',solver='simplex')
PACKAGES={'numpy':'2.3.5','scipy':'1.18.1','highspy':'1.12.0'}
PINS={
 'docs/research_next/COMMON_NOMINEE_PHASE1_PROPOSAL.md':'7ee2190eb6fd240b9e07924899cea0e7d22f67afba8260f4cd38b84a44cc21db',
 'docs/research_next/COMMON_NOMINEE_PHASE1_THEORY_REVIEW.md':'86f2774978fbe4d1b80670b5cc288fda03d7a2ac8f3d9cacc17c8f16d3c74806',
 'results/research_next/common_master_bounded/prepared/prepared_freeze.json':'75e9e276c356290129c85fefa9fdc5fb36f175174efb5b2e131bb96fdbef80d5',
 'results/research_next/common_master_bounded/prepared/input_manifest.json':'7bc0949abcd5aebb0d7ce4f2e68a3efa1105e9d1e25e54fd429dc04f4b33a19d',
 'results/research_next/common_master_bounded/producer_output_inventory.csv':'a7201af2fc77e7a556c5b0fc2ee0634f812808f0e4f092b64656baf24d668428',
 'results/research_next/common_master_bounded/INDEPENDENT_POSTRUN_REVIEW.json':'d5b2c4baac6605ef98f6cc025757c5f36c372166931ba7afe870d5509fdc9ad2',
 'results/research_next/common_master_bounded/run01/master_exact_admission.json':'983c62c4aaec8969ecc02ee774a55aa1fe2b95edf74d884dbae6f69e28b5a87a',
 'results/research_next/common_master_bounded/run01/lp/fixed_schedule.json':'26362ddab6b43aaa3ce2b605997a0c3460d9615492c13e177f7822c508ebf14a',
 'results/research_next/common_commitment/run01/lp/raw_solution.npz':'90c8b308a6ce8e7671adbe3059887d6ce27489fa3d68aa601c2474b32d2d462a',
 'results/research_next/common_commitment/INDEPENDENT_POSTRUN_REVIEW.json':'f442edeb3f90c5d602a1b60cdef1b96b4d560ebbe97fae28c4ca21c6077eadba',
}

def need(ok,message):
    if not ok:raise ValueError(message)
def utc():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,value):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')
def bind(p,data=None):
    p=Path(p).resolve();data=p.read_bytes() if data is None else data
    return dict(path=str(p),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
def validate(items):
    need(len({x['path'].casefold() for x in items})==len(items),'Duplicate bindings')
    for x in items:need(bind(x['path'])==x,'Frozen bytes changed: '+x['path'])
def rat(x):return [str(x.numerator),str(x.denominator)]
def checked(x):need(x.numerator.bit_length()<=MAX_BITS and x.denominator.bit_length()<=MAX_BITS,'8192-bit arithmetic guard');return x
def encode(x):
    f=float(x);need(math.isfinite(f) and abs(f)<1e20 and (x==0 or f!=0),'Unsupported numeric encoding')
    return dict(exact=rat(x),binary64_hex=f.hex(),rounding_error=rat(Q(f)-x))
def dump_gzip(p,value):
    with Path(p).open('xb') as f:
        with gzip.GzipFile(fileobj=f,mode='wb',mtime=0) as z:z.write(json.dumps(value,separators=(',',':'),allow_nan=False).encode())
def load_gzip(p):
    with gzip.open(p,'rt',encoding='utf-8') as f:return json.load(f)
def module(p,digest,name):
    need(sha(p)==digest,'Pinned helper changed');s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def kernel():return module(KERNEL,KERNEL_SHA,'common_phase1_original_kernel')
def mask(v,p,n):return tuple(v.vector(v.read_npz(p,('integrality',))['integrality'],('|u1',),n,'full original mask'))
def environment():
    need(Path(sys.executable).resolve()==PYTHON.resolve() and sys.version_info[:3]==(3,12,14),'Pinned scientific interpreter')
    packages={n:importlib.metadata.version(n) for n in PACKAGES};need(packages==PACKAGES,'Pinned package versions')
    return dict(executable=sys.executable,python=sys.version,packages=packages)
def guard(deadline,needed=0.):
    remaining=deadline-time.perf_counter();need(remaining>=needed,'Phase deadline/start guard');return remaining

def capture_inputs():
    captured={}
    def add(path,expected=None):
        path=Path(path).resolve();data=path.read_bytes();item=bind(path,data);key=str(path).casefold()
        if expected is not None:need(item==expected,'Captured historical bytes mismatch')
        need(key not in captured or captured[key][1]==item,'Conflicting byte provenance');captured[key]=(data,item)
        return data
    for rel,digest in PINS.items():need(hashlib.sha256(add(ROOT/rel)).hexdigest()==digest,'Pinned input changed: '+rel)
    old=json.loads(captured[str((MASTER/'prepared/input_manifest.json').resolve()).casefold()][0])['files'];need(len(old)==239,'Master input denominator')
    for x in old:add(x['path'],x)
    inventory=captured[str((MASTER/'producer_output_inventory.csv').resolve()).casefold()][0].decode('utf-8-sig')
    rows=list(csv.DictReader(inventory.splitlines()));need(len(rows)==25,'Closed producer denominator')
    for x in rows:
        p=ROOT/x['path'];add(p,dict(path=str(p.resolve()),bytes=int(x['bytes']),sha256=x['sha256']))
    for p,digest in ((KERNEL,KERNEL_SHA),(TRANSPORT,TRANSPORT_SHA)):need(hashlib.sha256(add(p)).hexdigest()==digest,'Helper pin')
    for p in (Path(__file__),PROTOCOL,ARM/'synthetic_tests.json',PYTHON):add(p)
    return captured

def prepare():
    started=time.perf_counter();need(not PRE.exists() and not RUN.exists(),'One preparation only');runtime=environment();captured=capture_inputs()
    initial=[x[1] for x in captured.values()];receipt=read(ARM/'synthetic_tests.json')
    need(receipt['source_sha256']==sha(__file__) and receipt['protocol_sha256']==sha(PROTOCOL),'Fixture provenance')
    PRE.mkdir(parents=True);save(PRE/'preparation_started.json',dict(utc=utc(),source_sha256=sha(__file__),optimizer_calls=0))
    copies=[]
    def copy(src,dst):
        key=str(src.resolve()).casefold();need(key in captured,'Copy source not captured');data,item=captured[key];dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
        need(bind(dst)['sha256']==item['sha256'],'Copy mismatch');copies.append(dict(original=item,copy=bind(dst)))
    for name in ('matrix.npz','bounds.npz','integrality.npz','column_maps.json','row_origins.json'):copy(MASTER/'prepared/joint'/name,PRE/'joint'/name)
    for world in ('identity','days_321'):copy(MASTER/'prepared'/world/'model_metadata.json',PRE/(world+'_metadata.json'))
    for src,name in ((MASTER/'prepared/gen.csv','gen.csv'),(MASTER/'prepared/premises.json','master_premises.json'),
        (MASTER/'run01/lp/fixed_schedule.json','fixed_schedule.json'),(MASTER/'run01/master_exact_admission.json','master_exact_admission.json'),
        (ORIGINAL/'run01/lp/raw_solution.npz','control_raw_solution.npz')):copy(src,PRE/name)
    v=kernel();m=v.load_model(PRE/'joint');bits=mask(v,PRE/'joint/integrality.npz',m.cols)
    need((m.rows,m.cols,len(m.data),sum(bits))==(69362,33936,291176,12096),'Original joint shape')
    need(bits==tuple(int(6888<=j<18984) for j in range(m.cols)),'Full original state block')
    schedule=read(PRE/'fixed_schedule.json');entries=schedule['fixed_columns'];fixed={x['column']:x['value'] for x in entries}
    need(len(entries)==len(fixed)==12096 and sorted(fixed)==[j for j,b in enumerate(bits) if b],'Complete unique original mask')
    need(all(type(x) is int and x in (0,1) and m.lower[j]<=x<=m.upper[j] for j,x in fixed.items()),'Exact fixed nominee/original boxes')
    admission=read(PRE/'master_exact_admission.json')
    need(admission['accepted'] and not admission['issues'] and [fixed[j] for j in sorted(fixed)]==admission['original_shared_state_values'],'Previously accepted sole nominee')
    need(schedule['master_admission_sha256']==sha(PRE/'master_exact_admission.json'),'Nominee provenance')
    maps=read(PRE/'joint/column_maps.json');origins=read(PRE/'joint/row_origins.json')['origins'];premises=read(PRE/'master_premises.json')
    need(maps['worlds']==['identity','days_321'] and len(origins)==m.rows,'World/origin coordinates')
    with (PRE/'gen.csv').open(encoding='utf-8-sig',newline='') as f:gen={x['GEN UID']:x for x in csv.DictReader(f)}
    caps=[]
    for wi,world in enumerate(('identity','days_321')):
        meta=read(PRE/(world+'_metadata.json'));names=meta['unit_names'];fossil=meta['fossil_units'];mp=maps['original_to_joint'][wi]
        need(len(names)==41 and len(fossil)==23 and [n for n in names if gen[n]['Fuel'] in ('Coal','NG','Oil')]==fossil,'Original fossil electrical roster')
        need(mp[6888:18984]==list(range(6888,18984)) and len(mp)==23016,'Original state mapping')
        source_cap=premises['worlds'][wi]['cap_row'];rs=[r for r,o in enumerate(origins) if o==[wi,source_cap]];need(len(rs)==1,'Unique original cap row');r=rs[0]
        terms={m.indices[k]:Q(m.data[k]) for k in range(m.indptr[r],m.indptr[r+1])}
        expected={mp[41*t+names.index(n)]:Q(1) for t in range(168) for n in fossil}
        need(terms==expected and len(terms)==3864 and m.row_lower[r]==-math.inf and m.row_upper[r]==23195.,'Original unchanged cap')
        caps.append(dict(world=world,joint_row=r,source_row=source_cap,coefficient_count=3864,original_upper_hex=m.row_upper[r].hex(),expanded_upper=encode(Q(23195)+TAU)))
    import numpy as np
    lower=[];upper=[];boxes=[]
    for j,b in enumerate(bits):
        need(math.isfinite(m.lower[j]) and math.isfinite(m.upper[j]) and m.lower[j]<=m.upper[j],'Finite original continuous boxes and nonempty intervals')
        lo=Q(fixed[j]) if b else Q(m.lower[j])-TAU;hi=Q(fixed[j]) if b else Q(m.upper[j])+TAU
        el,eu=encode(lo),encode(hi);lower.append(float(lo));upper.append(float(hi));boxes.append(dict(column=j,kind='fixed_original_bit' if b else 'expanded_continuous',lower=el,upper=eu))
    lower.append(0.);upper.append(math.inf);boxes.append(dict(column=m.cols,kind='artificial_s',lower=encode(Q(0)),upper=None))
    data=[];indices=[];indptr=[0];row_lower=[];row_upper=[];endpoints=[]
    for r in range(m.rows):
        need(m.row_lower[r]<=m.row_upper[r],'Original interval admission')
        for side,endpoint,sign in (('lower',m.row_lower[r],1.),('upper',m.row_upper[r],-1.)):
            if not math.isfinite(endpoint):continue
            rhs=Q(endpoint)-TAU if side=='lower' else Q(endpoint)+TAU
            indices.extend(m.indices[m.indptr[r]:m.indptr[r+1]]);data.extend(m.data[m.indptr[r]:m.indptr[r+1]])
            indices.append(m.cols);data.append(sign);indptr.append(len(data))
            row_lower.append(float(rhs) if side=='lower' else -math.inf);row_upper.append(float(rhs) if side=='upper' else math.inf)
            endpoints.append(dict(phase_row=len(endpoints),original_row=r,side=side,original_endpoint_hex=endpoint.hex(),widened=encode(rhs),artificial_coefficient_hex=sign.hex()))
    need(all(any(e['original_row']==c['joint_row'] and e['side']=='upper' for e in endpoints) for c in caps),'Both unchanged caps expanded once')
    np.savez_compressed(PRE/'phase_model.npz',data=np.array(data),indices=np.array(indices,dtype=np.int64),indptr=np.array(indptr,dtype=np.int64),shape=np.array([len(endpoints),m.cols+1],dtype=np.int64),
        column_lower=np.array(lower),column_upper=np.array(upper),row_lower=np.array(row_lower),row_upper=np.array(row_upper),objective=np.array([0.]*m.cols+[1.]),integrality=np.zeros(m.cols+1,dtype=np.uint8))
    dump_gzip(PRE/'endpoint_map.json.gz',endpoints);dump_gzip(PRE/'column_encoding.json.gz',boxes)
    save(PRE/'admission.json',dict(original_rows=m.rows,original_columns=m.cols,original_coefficients=len(m.data),full_original_bits=sum(bits),phase_rows=len(endpoints),phase_columns=m.cols+1,
        phase_coefficients=len(data),finite_original_boxes=True,original_intervals_ordered=True,caps=caps,uniform_tau=rat(TAU),binary_tau=0,new_nominees=0,multiplier_evaluations=0,control_evaluations=0))
    save(PRE/'copy_provenance.json',dict(copies=copies));save(PRE/'plan.json',dict(options=OPTIONS,runtime=runtime,phase_seconds=PHASE,start_guard=START_GUARD,maximum_rational_bits=MAX_BITS,
        calls=1,recipe='lower max(raw,0); upper max(-raw,0); d=lambda-mu; canonical original endpoint',alternative_candidates=0,control='one saved unrounded common LP state, no old point replay'))
    validate(initial);items=initial+[bind(p) for p in PRE.rglob('*') if p.is_file()];validate(items);save(PRE/'input_manifest.json',dict(files=items));validate(items)
    save(PRE/'prepared_freeze.json',dict(utc=utc(),source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),manifest_sha256=sha(PRE/'input_manifest.json'),bindings=len(items),copies=len(copies),
        phase_rows=len(endpoints),phase_columns=m.cols+1,optimizer_calls=0,backend_imports=0,multiplier_evaluations=0,control_evaluations=0,elapsed_seconds=time.perf_counter()-started,separate_execution_GO_required=True))
    print(json.dumps(dict(status='PREPARED_NO_MULTIPLIER_EVALUATION',freeze_sha256=sha(PRE/'prepared_freeze.json'),bindings=len(items))),flush=True)

def reconstruct(m,bits,fixed,control,endpoints,raw,tau,checkpoint=lambda:None):
    need(len(raw)==len(endpoints) and all(math.isfinite(x) for x in raw),'Finite complete returned endpoint dual')
    need(len(bits)==m.cols and set(fixed)=={j for j,b in enumerate(bits) if b},'Certificate state coordinates')
    lam=[Q(0)]*m.rows;mu=[Q(0)]*m.rows;projected=[];seen=set();beta_raw=Q(0)
    for k,(e,value) in enumerate(zip(endpoints,raw)):
        r=e['original_row'];side=e['side'];need((r,side) not in seen,'Unique endpoint map');seen.add((r,side))
        a=max(Q(value),Q(0)) if side=='lower' else max(-Q(value),Q(0));checked(a)
        endpoint=m.row_lower[r] if side=='lower' else m.row_upper[r];need(math.isfinite(endpoint),'Finite projected endpoint')
        if side=='lower':lam[r]=a;beta_raw=checked(beta_raw+a*Q(endpoint))
        else:mu[r]=a;beta_raw=checked(beta_raw-a*Q(endpoint))
        projected.append(dict(phase_row=k,original_row=r,side=side,raw_hex=float(value).hex(),nonnegative_multiplier=rat(a)))
        if k%256==0:checkpoint()
    need(seen=={(r,s) for r in range(m.rows) for s,x in (('lower',m.row_lower[r]),('upper',m.row_upper[r])) if math.isfinite(x)},'All finite endpoints exactly once')
    d=[Q(0)]*m.rows;q=[Q(0)]*m.cols;beta=norm=unmerged=interval_gain=cancellation=Q(0);selected=[]
    for r in range(m.rows):
        need(m.row_lower[r]<=m.row_upper[r],'Ordered source interval for canonical gain');d[r]=checked(lam[r]-mu[r]);unmerged=checked(unmerged+lam[r]+mu[r]);z=min(lam[r],mu[r])
        if z:
            need(math.isfinite(m.row_lower[r]) and math.isfinite(m.row_upper[r]),'Two-endpoint overlap finite')
            interval_gain=checked(interval_gain+z*(Q(m.row_upper[r])-Q(m.row_lower[r])));cancellation=checked(cancellation+2*z)
        if d[r]:
            endpoint=m.row_lower[r] if d[r]>0 else m.row_upper[r];need(math.isfinite(endpoint),'Signed combined endpoint')
            beta=checked(beta+d[r]*Q(endpoint));norm=checked(norm+abs(d[r]));selected.append(dict(row=r,side='lower' if d[r]>0 else 'upper',endpoint_hex=endpoint.hex()))
            for k in range(m.indptr[r],m.indptr[r+1]):j=m.indices[k];q[j]=checked(q[j]+d[r]*Q(m.data[k]))
        if r%256==0:checkpoint()
    need(beta-beta_raw==interval_gain and unmerged-norm==cancellation and interval_gain>=0 and cancellation>=0,'Exact duplicate-endpoint cancellation identities')
    support=continuous_norm=nominee_value=control_value=Q(0);support_records=[]
    for j,c in enumerate(q):
        if bits[j]:nominee_value=checked(nominee_value+c*Q(fixed[j]));control_value=checked(control_value+c*Q(control[j]))
        else:
            endpoint=m.upper[j] if c>=0 else m.lower[j];need(math.isfinite(endpoint),'Finite original support endpoint')
            support=checked(support+c*Q(endpoint));continuous_norm=checked(continuous_norm+abs(c))
            support_records.append(dict(column=j,endpoint_side='upper' if c>=0 else 'lower',endpoint_hex=endpoint.hex()))
        if j%256==0:checkpoint()
    loss=checked(tau*(norm+continuous_norm));rhs=checked(beta-support-loss);margin=checked(rhs-nominee_value)
    need(beta-tau*norm-(beta_raw-tau*unmerged)==interval_gain+tau*cancellation,'Expanded canonical gain identity')
    need(control_value>=rhs,'HARD_REVIEW_STOP: verified unrounded continuous state violates derived cut')
    return dict(status='VERIFIED_GLOBAL_NECESSARY_CUT_REJECTS_NOMINEE' if margin>0 else 'VALID_NONSEPARATING_CANDIDATE',strictly_positive_expanded_margin=margin>0,
        raw_endpoint_projection=projected,original_d=[rat(x) for x in d],full_A_transpose_d=[rat(x) for x in q],selected_original_endpoints=selected,continuous_support_endpoints=support_records,
        beta=rat(beta),beta_raw=rat(beta_raw),canonical_interval_gain=rat(interval_gain),unmerged_multiplier_norm=rat(unmerged),original_row_norm=rat(norm),norm_cancellation=rat(cancellation),
        expanded_canonical_gain=rat(interval_gain+tau*cancellation),continuous_support=rat(support),continuous_q_norm=rat(continuous_norm),tau_loss=rat(loss),cut_rhs=rat(rhs),
        nominee_state_value=rat(nominee_value),expanded_margin=rat(margin),control_state_value=rat(control_value),control_satisfied=True,old_full_point_replayed=False,
        row_support=sum(bool(x) for x in d),state_support=sum(bool(q[j]) for j,b in enumerate(bits) if b),continuous_support_count=sum(bool(q[j]) for j,b in enumerate(bits) if not b),
        extra_binary_tau=0,derived_row_extra_tau=0,all_original_coefficients_retained=True,alternative_multiplier_candidates=0)

def load_prepared(expected):
    need(sha(PRE/'prepared_freeze.json')==expected,'External freeze');f=read(PRE/'prepared_freeze.json')
    need(f['source_sha256']==sha(__file__) and f['protocol_sha256']==sha(PROTOCOL),'Source/protocol unchanged');need(f['manifest_sha256']==sha(PRE/'input_manifest.json'),'Manifest identity')
    items=read(PRE/'input_manifest.json')['files'];validate(items);plan=read(PRE/'plan.json')
    need(plan['runtime']==environment() and plan['options']==OPTIONS and plan['phase_seconds']==PHASE,'Execution plan unchanged');return items

def backend(highspy,np,phase,deadline):
    h=highspy.Highs();need(h.version()=='1.12.0','Backend version')
    for key,value in {**OPTIONS,'log_to_console':False,'log_file':str(PRIVATE/'solver.log')}.items():need(h.setOptionValue(key,value)==highspy.HighsStatus.kOk,'Rejected option')
    nr,nc=map(int,phase['shape']);lp=highspy.HighsLp();lp.num_row_=nr;lp.num_col_=nc
    lp.col_cost_=phase['objective'];lp.col_lower_=phase['column_lower'];lp.col_upper_=phase['column_upper'];lp.row_lower_=phase['row_lower'];lp.row_upper_=phase['row_upper'];lp.offset_=0.;lp.sense_=highspy.ObjSense.kMinimize
    lp.integrality_=[highspy.HighsVarType.kContinuous]*nc;lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise;lp.a_matrix_.num_row_=nr;lp.a_matrix_.num_col_=nc
    lp.a_matrix_.start_=phase['indptr'];lp.a_matrix_.index_=phase['indices'];lp.a_matrix_.value_=phase['data'];need(h.passModel(lp)==highspy.HighsStatus.kOk,'Rejected phase-I model')
    got=h.getLp();need((got.num_row_,got.num_col_)==(nr,nc),'Backend dimensions')
    arrays={key:tuple(getattr(got,field)) for key,field in [('objective','col_cost_'),('column_lower','col_lower_'),('column_upper','col_upper_'),('row_lower','row_lower_'),('row_upper','row_upper_')]}
    for key,value in arrays.items():need(value==tuple(phase[key]),'Full numerical endpoint/objective readback')
    need(got.offset_==0 and got.sense_==highspy.ObjSense.kMinimize,'Only min-s objective')
    ints=tuple(got.integrality_);need(not ints or all(x==highspy.HighsVarType.kContinuous for x in ints),'Every old binary fixed; LP continuous')
    transport=module(TRANSPORT,TRANSPORT_SHA,'phase1_cached_sparse_transport');matrix=got.a_matrix_;fmt=matrix.format_
    need(fmt in (highspy.MatrixFormat.kRowwise,highspy.MatrixFormat.kColwise),'Supported backend sparse format')
    actual=transport.extract_rows(matrix,fmt==highspy.MatrixFormat.kRowwise,nr,nc,lambda *a,**k:guard(deadline));data=[];indices=[];ptr=[0]
    for r,terms in enumerate(actual):
        a,b=phase['indptr'][r:r+2];wanted=sorted(zip(map(int,phase['indices'][a:b]),map(float,phase['data'][a:b])))
        need(terms==wanted,'All actual phase-I coefficients');data.extend(x for j,x in terms);indices.extend(j for j,x in terms);ptr.append(len(data))
        if r%512==0:guard(deadline)
    saved_options={}
    for key,value in OPTIONS.items():
        status,current=h.getOptionValue(key);need(status==highspy.HighsStatus.kOk and current==value,'Backend option readback');saved_options[key]=current
    np.savez_compressed(RUN/'backend_readback.npz',data=np.array(data),indices=np.array(indices,dtype=np.int64),indptr=np.array(ptr,dtype=np.int64),shape=np.array([nr,nc],dtype=np.int64),integrality=np.zeros(nc,dtype=np.uint8),**{key:np.array(val) for key,val in arrays.items()})
    save(RUN/'backend_readback.json',dict(rows=nr,columns=nc,coefficient_uses=len(data),all_numeric_coefficients_endpoints_boxes_objective_verified=True,
        phase_model_sha256=sha(PRE/'phase_model.npz'),readback_sha256=sha(RUN/'backend_readback.npz'),options=saved_options,array_materializations=dict(start=1,indices=1,values=1),optimizer_calls=0))
    return h

def run(expected):
    started=time.perf_counter();deadline=started+PHASE;need(not RUN.exists() and not PRIVATE.exists(),'Single execution only');items=load_prepared(expected)
    transport=[bind(PRE/'prepared_freeze.json'),bind(PRE/'input_manifest.json')];RUN.mkdir();PRIVATE.mkdir(parents=True)
    save(RUN/'execution_started.json',dict(utc=utc(),pid=os.getpid(),parent_pid=os.getppid(),source_sha256=sha(__file__),freeze_sha256=expected,phase_seconds=PHASE))
    ledger=dict(attempted=0,returned=0);result=dict(common_verdict='UNKNOWN',accepted_nominee_rejection=False,no_unrestricted_negative_claim=True);stage='imports'
    try:
        import numpy as np
        import highspy
        with np.load(PRE/'phase_model.npz',allow_pickle=False) as z:phase={key:z[key] for key in z.files}
        stage='backend_readback';h=backend(highspy,np,phase,deadline)
        save(RUN/'call_ready.json',dict(utc=utc(),remaining=guard(deadline,START_GUARD),not_actual_call=True));guard(deadline,START_GUARD)
        stage='sole_phase1_call';ledger.update(attempted=1,started_utc=utc());clock=time.perf_counter()
        try:status=h.run()
        finally:ledger['actual_seconds']=time.perf_counter()-clock
        ledger['returned']=1;sol=h.getSolution();info=h.getInfo()
        result.update(model_status=str(h.getModelStatus()),run_status=str(status),value_valid=bool(sol.value_valid),dual_valid=bool(sol.dual_valid),simplex_iterations=int(info.simplex_iteration_count),
            numerical_phase1_objective=float(info.objective_function_value) if math.isfinite(info.objective_function_value) else None)
        np.savez_compressed(RUN/'raw_solution.npz',vector=np.array(sol.col_value,dtype=np.float64),row_value=np.array(sol.row_value,dtype=np.float64),row_dual=np.array(sol.row_dual,dtype=np.float64),col_dual=np.array(sol.col_dual,dtype=np.float64))
        save(RUN/'solver_returned.json',result)
        raw=[float(x) for x in sol.row_dual];endpoints=load_gzip(PRE/'endpoint_map.json.gz')
        if sol.dual_valid and len(raw)==len(endpoints) and all(math.isfinite(x) for x in raw):
            guard(deadline);stage='single_exact_reconstruction';v=kernel();m=v.load_model(PRE/'joint');bits=mask(v,PRE/'joint/integrality.npz',m.cols)
            fixed={x['column']:x['value'] for x in read(PRE/'fixed_schedule.json')['fixed_columns']}
            z=v.read_npz(PRE/'control_raw_solution.npz',('vector','row_value','row_dual','col_dual'));control=tuple(v.vector(z['vector'],('<f8',),m.cols,'old raw unrounded control'))
            certificate=reconstruct(m,bits,fixed,control,endpoints,raw,TAU,lambda:guard(deadline))
            certificate['model_bindings']={name:sha(PRE/'joint'/name) for name in ('matrix.npz','bounds.npz','integrality.npz','column_maps.json','row_origins.json')}
            certificate['nominee_sha256']=sha(PRE/'fixed_schedule.json');certificate['raw_dual_sha256']=sha(RUN/'raw_solution.npz');certificate['control_sha256']=sha(PRE/'control_raw_solution.npz')
            dump_gzip(RUN/'exact_candidate.json.gz',certificate);result['candidate_status']=certificate['status'];result['accepted_nominee_rejection']=certificate['strictly_positive_expanded_margin']
        else:result['candidate_status']='NO_VALID_FINITE_COMPLETE_RETURNED_DUAL'
        validate(items);validate(transport);result['provisional_until_completion']=True;save(RUN/'result.json',result)
        elapsed=time.perf_counter()-started;admitted=bool(result['accepted_nominee_rejection'] and time.perf_counter()<=deadline)
        save(RUN/'completion.json',dict(utc=utc(),call_ledger=ledger,phase_seconds=elapsed,solver_soft_overrun=max(0,ledger.get('actual_seconds',0)-60),phase_soft_overrun=max(0,elapsed-PHASE),
            all_frozen_bytes_unchanged=True,no_retry=True,no_ray_recovery=True,alternative_multiplier_candidates=0,final_write_cleanup_outside_sample=True,
            final_admission=dict(accepted_nominee_rejection=admitted,status='EXACT_CUT_REJECTS_FIXED_NOMINEE' if admitted else 'NO_ACCEPTED_CERTIFICATE',common_verdict='UNKNOWN',phase_deadline_met=elapsed<=PHASE)))
        print(json.dumps(dict(accepted_nominee_rejection=admitted,common_verdict='UNKNOWN',calls=ledger['attempted'])),flush=True)
    except BaseException as exc:
        save(RUN/'failure.json',dict(utc=utc(),stage=stage,error_type=type(exc).__name__,message=str(exc),call_ledger=ledger,common_verdict='UNKNOWN',accepted_nominee_rejection=False,no_retry=True));raise
    finally:save(RUN/'private_log_receipt.json',dict(raw_logs_public=False,files=[bind(p) for p in PRIVATE.rglob('*') if p.is_file()]))

def self_test():
    need(not (ARM/'synthetic_tests.json').exists(),'One invented control run');checks=[]
    class Toy:
        rows=1;cols=2;data=(1.,1.);indices=(0,1);indptr=(0,2);row_lower=(1.5,);row_upper=(3.,);lower=(0.,0.);upper=(1.,1.)
    endpoints=[dict(original_row=0,side='lower'),dict(original_row=0,side='upper')];tau=Q(1,16)
    good=reconstruct(Toy(),(1,0),{0:0},(0.75,1.),endpoints,[3.,-1.],tau)
    need(good['strictly_positive_expanded_margin'] and good['cut_rhs']==rat(Q(3,4)) and good['canonical_interval_gain']==rat(Q(3,2)),'Signed endpoint/cancellation/full support')
    need(good['expanded_canonical_gain']==rat(Q(13,8)) and good['original_row_norm']==rat(Q(2)),'Two-endpoint tau gain')
    checks.append('exact positive nominee separation, signed endpoint overlap, full q and continuous support')
    null=reconstruct(Toy(),(1,0),{0:1},(0.75,1.),endpoints,[3.,-1.],tau)
    need(not null['strictly_positive_expanded_margin'],'Same globally valid cut preserves other state')
    zero=reconstruct(Toy(),(1,0),{0:0},(0.75,1.),endpoints,[-3.,1.],tau)
    need(zero['original_row_norm']==rat(Q(0)) and not zero['strictly_positive_expanded_margin'],'Inadmissible signs projected to zero only')
    checks.append('nonseparating/equality-zero and one fixed sign-projection recipe')
    bad_control=False
    try:reconstruct(Toy(),(1,0),{0:0},(0.,0.),endpoints,[3.,-1.],tau)
    except ValueError as e:bad_control='HARD_REVIEW_STOP' in str(e)
    need(bad_control,'Contradicting claimed control must fail');checks.append('unrounded fractional-control consistency hard stop')
    class Inverted(Toy):row_lower=(4.,);row_upper=(3.,)
    try:reconstruct(Inverted(),(1,0),{0:0},(0.75,1.),endpoints,[3.,-1.],tau)
    except ValueError:pass
    else:raise AssertionError('Inverted interval admitted')
    try:reconstruct(Toy(),(1,0),{0:0},(0.75,1.),[endpoints[0],endpoints[0]],[3.,1.],tau)
    except ValueError:pass
    else:raise AssertionError('Duplicate endpoint admitted')
    checks.append('inverted intervals and duplicate endpoint metadata rejected')
    need(good['cut_rhs']!=rat(Q(1)) and good['cut_rhs']!=rat(Q(3,4)-2*tau),'Missing continuous/row tau or extra binary tau would change result')
    for q in (Q(1,3),Q(-3,7),TAU):
        e=encode(q);need(Q(float.fromhex(e['binary64_hex']))-q==Q(*map(int,e['rounding_error'])),'Exact float-rounding residual')
    try:checked(Q(1,2**MAX_BITS))
    except ValueError:pass
    else:raise AssertionError('Bit guard ignored')
    checks.append('correct tau components, no binary tau, exact numeric rounding and bit guard')
    ARM.mkdir(parents=True,exist_ok=True);save(ARM/'synthetic_tests.json',dict(status='PASS',utc=utc(),source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),checks=checks,scientific_inputs_read=0,optimizer_calls=0))
    print(json.dumps(dict(status='PASS_SYNTHETIC_ONLY',groups=len(checks))),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--self-test',action='store_true');g.add_argument('--prepare-only',action='store_true');g.add_argument('--run-prepared',action='store_true');p.add_argument('--expected-freeze-sha256');args=p.parse_args()
    try:
        if args.self_test:self_test()
        elif args.prepare_only:prepare()
        else:need(args.expected_freeze_sha256 is not None,'External freeze required');run(args.expected_freeze_sha256)
    except BaseException as exc:
        folder=RUN if RUN.exists() else PRE if PRE.exists() else ARM;folder.mkdir(parents=True,exist_ok=True)
        if not (folder/'failure.json').exists():save(folder/'failure.json',dict(error_type=type(exc).__name__,message=str(exc),no_retry=True,no_accepted_certificate=True))
        raise
