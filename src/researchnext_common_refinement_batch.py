"""One prospective, finite seeded common-commitment feasibility trajectory."""
from __future__ import annotations
import argparse
from contextlib import redirect_stderr, redirect_stdout
import csv
from datetime import datetime, timezone
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
ARM = ROOT/'results/research_next/common_refinement_batch'
PRE = ARM/'prepared'; RUN = ARM/'run01'
PRIVATE = ROOT/'.work/researchnext_common_refinement_batch/run01'
PROTOCOL = ROOT/'docs/research_next/COMMON_REFINEMENT_BATCH_PROTOCOL.md'
OLD = ROOT/'results/research_next/common_master_bounded'
PHASE_OLD = ROOT/'results/research_next/common_phase1'
SCIP_PY = ROOT/'.work/scip_capability_env01/Scripts/python.exe'
LP_PY = Path('C:/Users/gmalkawi/OneDrive - Higher Colleges of Technology/Documents 1/ChatGPT/3/.work/solver_env/Scripts/python.exe')
HELPERS = {
 'master':('src/researchnext_common_master_bounded.py','62a2755aa289dc353893d3bf23ccf46ff839dffdf1937d5cdbc4320ce9526c18'),
 'phase':('src/researchnext_common_phase1.py','8af88d286e85f5807ab0bc11cc2450d10596f667e62f4b45c5279c8ebbc2eacb'),
 'kernel':('src/research8h_standalone_verify.py','708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'),
 'transport':('src/researchnext_repaired_crossworld_schema2.py','cf951d0dc5ac69df003b919df1e7d6400b71b25fc7e7e7ec7137b2480fc5b32d'),
 'acceptance':('src/researchnext_common_scip.py','e80a8e80b1a25def3f94564b3a33527a367fc21e4bd87ea52bcdbc2f3e16d8d5'),
 'native':('src/researchnext_common_commitment.py','039af59750b4c165d877b9878ac14af02a202700b46739ba96a8914075ae3284'),
 'encoding':('src/researchnext_cut_encoding.py','286620b092dcf6088f7973c5b3e4569f598d125a20562abe52989e9aaf8af22d'),
}
PINS = {
 'docs/research_next/FINITE_COMMON_REFINEMENT_BATCH_PROPOSAL.md':'ee165cf64fe72d39d5daa8a9ff7e725b5930587a4a0218b156c36d8a05482cbf',
 'docs/research_next/FINITE_COMMON_BATCH_REVIEW_RESOLUTIONS.md':'a6ccc51946bede93639c2a8c92965db551f7f216202230e326c318d678b2d47c',
 'docs/research_next/FINITE_COMMON_NETWORK_SEED_AMENDMENT.md':'035cafc23e92bd78a727b12734c0cdd57b00769ae0d7bcf353231c6deb3b88f7',
 'docs/research_next/PHASE1_NETWORK_TEMPLATE_FEASIBILITY.md':'a6255c7a62cd10bfdf6d4846cdb9b4a87be17b7cd7ef76b8cb5a0f9c9806d2cd',
 'docs/research_next/FINITE_COMMON_NETWORK_SEED_THEORY_REVIEW.md':'1a7dc4a886563f5db3e34958796e35c1313e748c1fecada6698af89dc010e673',
 'docs/research_next/BINARY_CUT_ENCODING_PROTOCOL.md':'bf36b2495741888638963a4eda747f213815282da1cbaec96972470d4b945118',
 'results/research_next/cut_encoding_controls/synthetic_receipt.json':'a3003a79f0c84f4db9b9eca60035d06351016650f78bb1470ecf34a5ca6f7136',
 'results/research_next/common_master_bounded/prepared/prepared_freeze.json':'75e9e276c356290129c85fefa9fdc5fb36f175174efb5b2e131bb96fdbef80d5',
 'results/research_next/common_master_bounded/prepared/input_manifest.json':'7bc0949abcd5aebb0d7ce4f2e68a3efa1105e9d1e25e54fd429dc04f4b33a19d',
 'results/research_next/common_master_bounded/INDEPENDENT_POSTRUN_REVIEW.json':'d5b2c4baac6605ef98f6cc025757c5f36c372166931ba7afe870d5509fdc9ad2',
 'results/research_next/common_phase1/prepared/prepared_freeze.json':'9d2a0768eb785277d9b8ddf04483e0e83ed97ba628fff23e2a32b146649e1496',
 'results/research_next/common_phase1/prepared/input_manifest.json':'9e4640c4bea127601201e3323f43471e2582eb9aab26ed6cb045f566c4f00d70',
 'results/research_next/common_phase1/producer_output_inventory.csv':'17e0c3649d538d82e70c47a5e1183c5e6d4fd48db825343ecfcebe885f3dee92',
 'results/research_next/common_phase1_independent_review/postrun_review.json':'8d16937fb7493b314d439dad48123c6c12dd94c69062b346d9bf8da56858e526',
}
NB = 12096; STATE_START = 6888; STATE_STOP = 18984; TAU = Q.from_float(1e-5)
PHASE = 2400.; ROUNDS = 8; MAX_CALLS = 24; MAX_BITS = 8192
LIMITS = dict(master=120.,recourse=60.,phase1=60.,transport_only=0.)
CLOSURE_MARGIN = 5.; C = Q(6004799503160661,144115188075855872)
THERMAL = ('101_CT_1','101_CT_2','101_STEAM_3','101_STEAM_4','102_CT_1','102_CT_2','102_STEAM_3','102_STEAM_4',
 '113_CT_1','113_CT_2','113_CT_3','113_CT_4','115_STEAM_1','115_STEAM_3','116_STEAM_1','118_CC_1','123_STEAM_2','123_STEAM_3','123_CT_1','123_CT_4','123_CT_5')
WORLD_FILES = ('matrix.npz','bounds.npz','integrality.npz','model_metadata.json','native_inputs.npz','permutation.csv','row_metadata.csv.gz','native_spec.json')
JOINT_FILES = ('matrix.npz','bounds.npz','integrality.npz','column_maps.json','row_origins.json')

def need(ok,message):
    if not ok: raise ValueError(message)
def utc(): return datetime.now(timezone.utc).isoformat()
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def save(path,value):
    with Path(path).open('x',encoding='utf-8') as f: json.dump(value,f,indent=2,allow_nan=False);f.write('\n')
def publish(path,value):
    path=Path(path);temporary=path.with_name(path.name+'.writing');need(not path.exists(),'Fresh handshake marker')
    save(temporary,value);temporary.rename(path)
def zipped(path,value):
    with Path(path).open('xb') as f:
        with gzip.GzipFile(fileobj=f,mode='wb',mtime=0) as z:z.write(json.dumps(value,separators=(',',':'),allow_nan=False).encode())
def unzip(path):
    with gzip.open(path,'rt',encoding='utf-8') as f:return json.load(f)
def bind(path,data=None):
    path=Path(path).resolve();data=path.read_bytes() if data is None else data
    return dict(path=str(path),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
def validate(items):
    need(len({x['path'].casefold() for x in items})==len(items),'Duplicate manifest paths')
    for x in items:need(bind(x['path'])==x,'Changed frozen input: '+x['path'])
def rat(x):return [str(x.numerator),str(x.denominator)]
def frac(x):return Q(int(x[0]),int(x[1]))
def checked(x):
    need(x.numerator.bit_length()<=MAX_BITS and x.denominator.bit_length()<=MAX_BITS,'8192-bit resource guard');return x
def guard(deadline,needed=0.):
    left=deadline-time.perf_counter();need(left>=needed,'Global phase/start guard');return left
def helper(name):
    rel,digest=HELPERS[name];path=ROOT/rel;need(sha(path)==digest,'Helper pin: '+name)
    spec=importlib.util.spec_from_file_location('batch_'+name,path);obj=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=obj;spec.loader.exec_module(obj);return obj
def mask(v):return tuple(v.vector(v.read_npz(PRE/'joint/integrality.npz',('integrality',))['integrality'],('|u1',),33936,'full original mask'))
def state_hash(bits):
    need(len(bits)==NB and all(type(x)is int and x in (0,1) for x in bits),'Complete exact bits');return hashlib.sha256(bytes(bits)).hexdigest()
def support_control(v):
    return tuple(v.vector(v.read_npz(PRE/'control_raw_solution.npz',('vector','row_value','row_dual','col_dual'))['vector'],('<f8',),33936,'unrounded existing control'))

def metadata_templates(metadata,origins):
    origin_map={tuple(x):r for r,x in enumerate(origins)};need(len(origin_map)==len(origins),'Unique joint origins')
    result=[]
    for wi,(world,rows) in enumerate(metadata):
        keys={}
        for r,x in enumerate(rows):
            need(int(x['row'])==r,'Original metadata row order')
            key=(x['family'],int(x['hour_0based']),x['uid']);keys.setdefault(key,[]).append(r)
        for t in range(168):
            selected=[('aggregate_balance','ALL',1,'lower')]+[('thermal_upper',uid,-1,'upper') for uid in THERMAL]+[('nodal_balance','107',-1,'upper'),('branch_flow','10',-1,'upper')]
            entries=[]
            for family,uid,sign,side in selected:
                matches=keys.get((family,t,uid),[]);need(len(matches)==1,'Unique template row key')
                r=matches[0];need((wi,r) in origin_map,'Mapped original row')
                entries.append(dict(family=family,uid=uid,side=side,sign=sign,original_row=r,joint_row=origin_map[(wi,r)]))
            result.append(dict(world=world,world_index=wi,hour=t,rows=entries))
    need(len(result)==336,'Complete fixed seed denominator');return result

def prepare():
    started=time.perf_counter();need(not PRE.exists() and not RUN.exists(),'One fresh preparation')
    captured={}
    def capture(p,expected=None):
        p=Path(p).resolve();data=p.read_bytes();item=bind(p,data);key=str(p).casefold()
        if expected is not None:need(item==expected,'Captured historical bytes mismatch')
        need(key not in captured or captured[key][1]==item,'Conflicting provenance');captured[key]=(data,item);return data
    for rel,digest in PINS.items():need(hashlib.sha256(capture(ROOT/rel)).hexdigest()==digest,'Historical pin')
    for rel,digest in HELPERS.values():need(hashlib.sha256(capture(ROOT/rel)).hexdigest()==digest,'Helper bytes')
    for folder,count in ((OLD/'prepared',239),(PHASE_OLD/'prepared',292)):
        doc=json.loads(captured[str((folder/'input_manifest.json').resolve()).casefold()][0]);need(len(doc['files'])==count,'Historical denominator')
        for x in doc['files']:capture(x['path'],x)
    inventory=captured[str((PHASE_OLD/'producer_output_inventory.csv').resolve()).casefold()][0].decode('utf-8-sig')
    rows=list(csv.DictReader(inventory.splitlines()));need(len(rows)==12,'Closed phase-I output denominator')
    for x in rows:
        p=ROOT/x['path'];capture(p,dict(path=str(p.resolve()),bytes=int(x['bytes']),sha256=x['sha256']))
    for p in (Path(__file__),PROTOCOL,ARM/'synthetic_tests.json',SCIP_PY,LP_PY):capture(p)
    tests=read(ARM/'synthetic_tests.json');need(tests['source_sha256']==sha(__file__) and tests['protocol_sha256']==sha(PROTOCOL),'Fixture source provenance')
    runtime=helper('master').runtimes();initial=[x[1] for x in captured.values()];PRE.mkdir(parents=True)
    save(PRE/'preparation_started.json',dict(utc=utc(),optimizer_calls=0,scientific_cut_evaluations=0));copies=[]
    def copy(src,dst):
        data,item=captured[str(src.resolve()).casefold()];dst.parent.mkdir(parents=True,exist_ok=True)
        with dst.open('xb') as f:f.write(data)
        need(bind(dst)['sha256']==item['sha256'],'Copy exact bytes');copies.append(dict(original=item,copy=bind(dst)))
    for world in ('identity','days_321'):
        for name in WORLD_FILES:copy(OLD/'prepared'/world/name,PRE/world/name)
    for name in JOINT_FILES:copy(OLD/'prepared/joint'/name,PRE/'joint'/name)
    for name in ('master.json.gz','premises.json','gen.csv','identity_cut.json','days_321_cut.json'):copy(OLD/'prepared'/name,PRE/name)
    for name in ('phase_model.npz','endpoint_map.json.gz','column_encoding.json.gz','control_raw_solution.npz','fixed_schedule.json'):copy(PHASE_OLD/'prepared'/name,PRE/('inherited_'+name if name=='fixed_schedule.json' else name))
    copy(PHASE_OLD/'run01/exact_candidate.json.gz',PRE/'anchor_certificate.json.gz')
    metadata=[]
    for world in ('identity','days_321'):
        with gzip.open(PRE/world/'row_metadata.csv.gz','rt',encoding='utf-8-sig',newline='') as f:metadata.append((world,list(csv.DictReader(f))))
    templates=metadata_templates(metadata,read(PRE/'joint/row_origins.json')['origins'])
    save(PRE/'symbolic_seed_maps.json',dict(common_weight=rat(C),cases=templates,no_coefficients_or_endpoints_evaluated=True))
    save(PRE/'copy_provenance.json',dict(copies=copies))
    save(PRE/'plan.json',dict(runtime=runtime,phase_seconds=PHASE,rounds=ROUNDS,maximum_optimizer_calls=MAX_CALLS,limits=LIMITS,closure_margin=CLOSURE_MARGIN,
        initial_master_inherited_without_reassembly=True,scientific_cut_evaluations=0,old_witness_replays=0,helper_rebinding='new PRE plus unique worker RUN/PRIVATE only'))
    validate(initial);items=initial+[bind(p) for p in PRE.rglob('*') if p.is_file()];validate(items);save(PRE/'input_manifest.json',dict(files=items))
    save(PRE/'prepared_freeze.json',dict(utc=utc(),source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),manifest_sha256=sha(PRE/'input_manifest.json'),
        bindings=len(items),copies=len(copies),symbolic_seed_cases=336,optimizer_calls=0,scientific_cut_evaluations=0,backend_imports=0,elapsed_seconds=time.perf_counter()-started,separate_execution_GO_required=True))
    print(json.dumps(dict(status='PREPARED_ONLY',freeze_sha256=sha(PRE/'prepared_freeze.json'),bindings=len(items))),flush=True)

def load_prepared(expected,full=True):
    need(sha(PRE/'prepared_freeze.json')==expected,'Trusted freeze');f=read(PRE/'prepared_freeze.json')
    need(f['source_sha256']==sha(__file__) and f['protocol_sha256']==sha(PROTOCOL),'Frozen source/protocol')
    need(f['manifest_sha256']==sha(PRE/'input_manifest.json'),'Manifest identity');items=read(PRE/'input_manifest.json')['files']
    if full:validate(items)
    return items

def sparse_proof(m,bits,control,d,checkpoint=lambda:None):
    need(all(type(r)is int and 0<=r<m.rows and x for r,x in d.items()),'Exact nonzero row support')
    q={};beta=norm=Q(0);endpoints=[]
    for r,a in sorted(d.items()):
        lo,hi=m.row_lower[r],m.row_upper[r];need(lo<=hi,'Ordered original interval');e=lo if a>0 else hi
        need(math.isfinite(e),'Finite selected endpoint');beta=checked(beta+a*Q(e));norm=checked(norm+abs(a))
        endpoints.append(dict(row=r,side='lower' if a>0 else 'upper',endpoint_hex=e.hex()))
        for k in range(m.indptr[r],m.indptr[r+1]):j=m.indices[k];q[j]=checked(q.get(j,Q(0))+a*Q(m.data[k]))
        checkpoint()
    q={j:a for j,a in q.items() if a!=0};support=cnorm=cv=Q(0);used=[]
    for j,a in sorted(q.items()):
        if bits[j]:cv=checked(cv+a*Q(control[j]))
        else:
            e=m.upper[j] if a>0 else m.lower[j];need(math.isfinite(e),'Finite continuous support')
            support=checked(support+a*Q(e));cnorm=checked(cnorm+abs(a));used.append(dict(column=j,side='upper' if a>0 else 'lower',endpoint_hex=e.hex()))
    loss=checked(TAU*(norm+cnorm));rhs=checked(beta-support-loss)
    return dict(original_rows=m.rows,original_columns=m.cols,full_state_dimension=sum(bits),omitted_coordinates_exact_zero=True,
        original_d=[[r,rat(a)] for r,a in sorted(d.items())],full_q_nonzero=[[j,rat(a)] for j,a in sorted(q.items())],
        state_terms=[[j,rat(a)] for j,a in sorted(q.items()) if bits[j]],selected_original_endpoints=endpoints,continuous_support_endpoints=used,
        beta=rat(beta),original_row_norm=rat(norm),continuous_support=rat(support),continuous_q_norm=rat(cnorm),tau_loss=rat(loss),cut_rhs=rat(rhs),
        control_state_value=rat(cv),control_satisfied=cv>=rhs,all_selected_row_terms_used=True,extra_binary_tau=0,derived_extra_tau=0)

def encoding_for(proof,encoder,origin=None,progress=False):
    terms=proof['state_terms'];coords=[j-STATE_START for j,a in terms];values=[frac(a) for j,a in terms]
    need(all(0<=j<NB for j in coords) and len(set(coords))==len(coords),'Explicit full-mask state coordinates')
    return encoder.encode_binary_cut(values,frac(proof['cut_rhs']),coordinates=coords,
        origin=origin,require_exclusion=progress,full_dimension=NB)

def anchor_check(proof,anchor,old):
    d={r:frac(a) for r,a in proof['original_d']};q={j:frac(a) for j,a in proof['full_q_nonzero']}
    need(len(anchor['original_d'])==proof['original_rows'] and len(anchor['full_A_transpose_d'])==proof['original_columns'],'Anchor full dimensions')
    need(all(d.get(r,Q(0))==frac(a) for r,a in enumerate(anchor['original_d'])) and all(q.get(j,Q(0))==frac(a) for j,a in enumerate(anchor['full_A_transpose_d'])),'Full anchor d/q identity')
    for k in ('beta','original_row_norm','continuous_support','continuous_q_norm','tau_loss','cut_rhs','control_state_value'):need(proof[k]==anchor[k],'Anchor scalar identity: '+k)
    activity=sum((frac(a)*old[j-STATE_START] for j,a in proof['state_terms']),Q(0))
    need(activity==frac(anchor['nominee_state_value']) and frac(proof['cut_rhs'])-activity==frac(anchor['expanded_margin'])>0,'Original nominee excluded by anchor')

def seed_stage(v,m,bits,control,encoder,deadline):
    folder=RUN/'seeds';folder.mkdir();records=[];anchor=unzip(PRE/'anchor_certificate.json.gz')
    fixed=read(PRE/'inherited_fixed_schedule.json')['fixed_columns'];need([x['column'] for x in fixed]==list(range(STATE_START,STATE_STOP)),'Old full nominee map')
    old=[x['value'] for x in fixed];state_hash(old)
    for case in read(PRE/'symbolic_seed_maps.json')['cases']:
        guard(deadline);d={x['joint_row']:C*x['sign'] for x in case['rows']};need(len(d)==24,'Complete unique learned template')
        proof=sparse_proof(m,bits,control,d,lambda:guard(deadline));proof['case']=case
        prefix=f"{case['world']}_{case['hour']:03d}";zipped(folder/(prefix+'_proof.json.gz'),proof)
        need(proof['control_satisfied'],'HARD_REVIEW_STOP: old unrounded control contradicts seed')
        if case['world']=='identity' and case['hour']==80:anchor_check(proof,anchor,old)
        encoding=encoding_for(proof,encoder,progress=False)
        zipped(folder/(prefix+'_encoding.json.gz'),encoding)
        need(encoding['eligible_for_backend'],'Unsupported seed numerical transport or constant row')
        records.append(dict(kind='seed',proof=bind(folder/(prefix+'_proof.json.gz')),encoding=bind(folder/(prefix+'_encoding.json.gz'))))
    need(len(records)==336,'No omitted seed cases');save(folder/'completion.json',dict(cases=336,anchor_full_identity=True,controls_passed=336,optimizer_calls=0))
    return records,old

def search_model(base,records):
    model=dict(base);model['rows']=list(base['rows'])
    for record in records:
        validate([record['proof'],record['encoding']]);e=unzip(record['encoding']['path']);need(e['eligible_for_backend'],'Admitted requested encoding')
        terms=[]
        for x in e['coefficients']:
            exact=frac(x['scaled']);number=float.fromhex(x['encoded_hex'])
            # Every exact nonzero is retained even if its numeric value is zero.
            terms.append([x['coordinate'],dict(exact=rat(exact),binary64_hex=number.hex(),rounding_error=rat(Q(number)-exact))])
        proof=unzip(record['proof']['path']);beta=frac(proof['cut_rhs'])/frac(e['scale'])
        low=float.fromhex(e['lower']['encoded_hex'])
        model['rows'].append(dict(family='network_seed' if record['kind']=='seed' else 'new_phase1_cut',terms=terms,
            lower=dict(exact=rat(beta),binary64_hex=low.hex(),rounding_error=rat(Q(low)-beta)),upper=None,
            provenance=dict(proof=record['proof'],encoding=record['encoding'],exact_scaled_original_row=True,no_extra_tau=True)))
    return model

def actual_transport(master,records,folder,encoder,only_last=False):
    readback=unzip(folder/'master_backend_readback.json.gz')['rows'];start=len(master['rows'])-len(records);actual={}
    for row in readback:
        if row['master_row']<start:continue
        need(row['master_row'] not in actual and row['sense']=='>','One original lower-only transported row')
        actual[row['master_row']]=row
    checks=[]
    for k,record in enumerate(records):
        if only_last and k!=len(records)-1:continue
        need(start+k in actual,'Full actual cut row denominator');a=actual[start+k];e=unzip(record['encoding']['path'])
        result=encoder.verify_actual_binary_cut(e,[(j,float.fromhex(x)) for j,x in a['terms']],float.fromhex(a['lower_hex']),math.inf)
        # The inherited backend readback already proves its finite infinity sentinel is the upper side.
        need(result['admitted'],'Actual backend necessary-row transport or origin exclusion failed')
        checks.append(dict(master_row=start+k,proof_sha256=record['proof']['sha256'],encoding_sha256=record['encoding']['sha256'],verification=result))
    zipped(folder/'actual_cut_transport.json.gz',checks);return checks

class OwnedWindowsJob:
    """Fail closed unless both authenticated launcher/actual worker are in one kill-on-close job."""
    def __init__(self):
        need(os.name=='nt','This pinned execution protocol requires Windows job ownership')
        import ctypes as ct
        from ctypes import wintypes as wt
        self.ct=ct;self.wt=wt;self.k=ct.WinDLL('kernel32',use_last_error=True);self.handles=[]
        class BASIC(ct.Structure):
            _fields_=[('PerProcessUserTimeLimit',ct.c_longlong),('PerJobUserTimeLimit',ct.c_longlong),('LimitFlags',wt.DWORD),
                ('MinimumWorkingSetSize',ct.c_size_t),('MaximumWorkingSetSize',ct.c_size_t),('ActiveProcessLimit',wt.DWORD),
                ('Affinity',ct.c_size_t),('PriorityClass',wt.DWORD),('SchedulingClass',wt.DWORD)]
        class IO(ct.Structure):_fields_=[(n,ct.c_ulonglong) for n in ('ReadOperationCount','WriteOperationCount','OtherOperationCount','ReadTransferCount','WriteTransferCount','OtherTransferCount')]
        class EXTENDED(ct.Structure):
            _fields_=[('BasicLimitInformation',BASIC),('IoInfo',IO),('ProcessMemoryLimit',ct.c_size_t),('JobMemoryLimit',ct.c_size_t),('PeakProcessMemoryUsed',ct.c_size_t),('PeakJobMemoryUsed',ct.c_size_t)]
        self.k.CreateJobObjectW.argtypes=[ct.c_void_p,wt.LPCWSTR];self.k.CreateJobObjectW.restype=wt.HANDLE
        self.k.SetInformationJobObject.argtypes=[wt.HANDLE,ct.c_int,ct.c_void_p,wt.DWORD];self.k.SetInformationJobObject.restype=wt.BOOL
        self.k.OpenProcess.argtypes=[wt.DWORD,wt.BOOL,wt.DWORD];self.k.OpenProcess.restype=wt.HANDLE
        self.k.AssignProcessToJobObject.argtypes=[wt.HANDLE,wt.HANDLE];self.k.AssignProcessToJobObject.restype=wt.BOOL
        self.k.GetProcessTimes.argtypes=[wt.HANDLE,ct.POINTER(wt.FILETIME),ct.POINTER(wt.FILETIME),ct.POINTER(wt.FILETIME),ct.POINTER(wt.FILETIME)]
        self.k.GetProcessTimes.restype=wt.BOOL
        self.k.TerminateJobObject.argtypes=[wt.HANDLE,wt.UINT];self.k.TerminateJobObject.restype=wt.BOOL
        self.k.CloseHandle.argtypes=[wt.HANDLE];self.k.CloseHandle.restype=wt.BOOL
        self.k.WaitForSingleObject.argtypes=[wt.HANDLE,wt.DWORD];self.k.WaitForSingleObject.restype=wt.DWORD
        self.handle=self.k.CreateJobObjectW(None,None);need(bool(self.handle),'Create owned job')
        info=EXTENDED();info.BasicLimitInformation.LimitFlags=0x2000
        need(bool(self.k.SetInformationJobObject(self.handle,9,ct.byref(info),ct.sizeof(info))),'Kill-on-close job setup')
    def add(self,pid):
        h=self.k.OpenProcess(0x0001|0x0100|0x0400|0x00100000,False,pid);need(bool(h),'Open exact authenticated process')
        self.handles.append(h);a,b,c,d=(self.wt.FILETIME() for _ in range(4))
        need(bool(self.k.GetProcessTimes(h,self.ct.byref(a),self.ct.byref(b),self.ct.byref(c),self.ct.byref(d))),'Capture exact process creation')
        need(bool(self.k.AssignProcessToJobObject(self.handle,h)),'Assign exact process to owned job')
        return dict(pid=pid,creation_filetime=(a.dwHighDateTime<<32)|a.dwLowDateTime)
    def stop(self):need(bool(self.k.TerminateJobObject(self.handle,71)),'Terminate owned job only')
    def reaped(self):return all(self.k.WaitForSingleObject(h,5000)==0 for h in self.handles)
    def close(self):
        if self.handle:self.k.CloseHandle(self.handle);self.handle=None
        for h in self.handles:self.k.CloseHandle(h)
        self.handles=[]

def launch(kind,round_id,expected,deadline,requests,number):
    need(kind in LIMITS and number<=25,'Finite worker launch scope');needed=LIMITS[kind]+CLOSURE_MARGIN;guard(deadline,needed)
    folder=RUN/f'round_{round_id:02d}'/kind;folder.mkdir(parents=True);private=PRIVATE/f'round_{round_id:02d}'/kind;private.mkdir(parents=True)
    request=dict(kind=kind,round=round_id,source_sha256=sha(__file__),freeze_sha256=expected,deadline_monotonic=deadline,
        folder=str(folder.resolve()),private=str(private.resolve()),token=uuid.uuid4().hex,**requests)
    path=folder/'request.json';save(path,request);digest=sha(path);exe=SCIP_PY if kind in ('master','transport_only') else LP_PY
    command=[str(exe),'-I',str(Path(__file__).resolve()),'--worker','--expected-freeze-sha256',expected,'--request',str(path.resolve()),'--expected-request-sha256',digest]
    save(folder/'worker_launch_attempt.json',dict(utc=utc(),worker_launch_attempted=1,not_optimizer_attempt=True,command=command,request_sha256=digest,remaining=guard(deadline,needed)))
    child=None;job=None;out=dict(kind=kind,worker_number=number,worker_launch_attempted=1,optimizer_attempted=0,timed_out=False);clock=time.perf_counter()
    try:
        guard(deadline,needed)
        with (private/'worker.log').open('x',encoding='utf-8') as log:
            child=subprocess.Popen(command,stdout=log,stderr=log);out['launcher_pid']=child.pid
            handshake_end=min(deadline,time.perf_counter()+30.)
            while not (folder/'worker_ready.json').exists():
                need(child.poll() is None,'Worker ended before ownership handshake');need(time.perf_counter()<handshake_end,'Owned-worker handshake timeout');time.sleep(.05)
            ready=read(folder/'worker_ready.json')
            need(ready['request_sha256']==digest and ready['token']==request['token'] and ready['source_sha256']==sha(__file__),'Authenticated worker handshake')
            need(ready['pid']==child.pid or ready['parent_pid']==child.pid,'Known direct launcher/actual Python chain')
            job=OwnedWindowsJob();chain=[job.add(child.pid)]
            if ready['pid']!=child.pid:chain.append(job.add(ready['pid']))
            save(folder/'owned_process_chain.json',dict(launcher_pid=child.pid,actual_pid=ready['pid'],actual_parent_pid=ready['parent_pid'],processes=chain,job_kill_on_close=True))
            guard(deadline,needed);publish(folder/'worker_go.json',dict(token=request['token'],request_sha256=digest,ownership_admitted=True));guard(deadline,needed)
            try:child.wait(timeout=max(0.,deadline-time.perf_counter()))
            except subprocess.TimeoutExpired:out['timed_out']=True;job.stop();child.wait(timeout=10.)
            need(job.reaped(),'Owned processes not reaped');out['exit_code']=child.returncode
        if (folder/'optimizer_attempt.json').exists():out['optimizer_attempted']=1
        if (folder/'optimizer_returned.json').exists():out['optimizer_returned']=1
        if (folder/'completion.json').exists():out['completion']=read(folder/'completion.json')
        need(not out['timed_out'] and child.returncode==0 and 'completion' in out,'Worker failure/timeout/missing completion')
        return folder,out
    except BaseException as exc:
        out.update(error_type=type(exc).__name__,error=str(exc))
        if child is not None and child.poll() is None:
            if job is not None:job.stop();child.wait(timeout=10.)
            else:
                # No worker_go was issued: authenticated worker cannot import a backend/call a solver.
                # Kill only our launcher; worker handshake self-times out and exits. No descendant kill claim.
                child.kill();child.wait(timeout=10.);out['pre_go_worker_self_exit_required']=True
        raise
    finally:
        if (folder/'optimizer_attempt.json').exists():out['optimizer_attempted']=1
        if (folder/'optimizer_returned.json').exists():out['optimizer_returned']=1
        out['elapsed_seconds']=time.perf_counter()-clock
        if job is not None:out['owned_handles_reaped']=job.reaped();job.close()
        save(folder/'worker_closed.json',out)

def solver_call(folder,kind,deadline,function):
    guard(deadline,LIMITS[kind]+CLOSURE_MARGIN)
    save(folder/'optimizer_attempt.json',dict(utc=utc(),attempted=1,returned=0,kind=kind,immediately_before_guard_and_call=True,remaining=guard(deadline,LIMITS[kind]+CLOSURE_MARGIN)))
    try:guard(deadline,LIMITS[kind]+CLOSURE_MARGIN)
    except ValueError:
        save(folder/'optimizer_cancelled_before_call.json',dict(utc=utc(),attempt_recorded=1,optimizer_entered=False,reason='post-write start guard'));raise
    started=time.perf_counter()
    try:answer=function()
    except BaseException as exc:
        save(folder/'optimizer_error.json',dict(utc=utc(),attempted=1,optimizer_entered=True,returned=0,actual_seconds=time.perf_counter()-started,error_type=type(exc).__name__));raise
    elapsed=time.perf_counter()-started
    save(folder/'optimizer_returned.json',dict(utc=utc(),attempted=1,optimizer_entered=True,returned=1,actual_seconds=elapsed,solver_soft_overrun=max(0.,elapsed-LIMITS[kind])))
    return answer

def worker(expected,request_path,request_digest):
    path=Path(request_path).resolve();need(path.is_relative_to(RUN.resolve()) and path.name=='request.json','New run request path')
    need(sha(path)==request_digest,'External request binding');request=read(path);kind=request['kind'];folder=path.parent;private=Path(request['private']).resolve()
    need(folder==Path(request['folder']).resolve() and private.is_relative_to(PRIVATE.resolve()),'Confined worker directories')
    need(request['source_sha256']==sha(__file__) and request['freeze_sha256']==expected,'Worker source/freeze')
    publish(folder/'worker_ready.json',dict(pid=os.getpid(),parent_pid=os.getppid(),source_sha256=sha(__file__),request_sha256=request_digest,token=request['token']))
    end=min(request['deadline_monotonic'],time.perf_counter()+30.)
    while not (folder/'worker_go.json').exists():need(time.perf_counter()<end,'No ownership GO');time.sleep(.05)
    go=read(folder/'worker_go.json');need(go==dict(token=request['token'],request_sha256=request_digest,ownership_admitted=True),'Ownership handshake')
    deadline=request['deadline_monotonic'];items=load_prepared(expected);guard(deadline)
    expected_py=SCIP_PY if kind in ('master','transport_only') else LP_PY
    need(Path(sys.executable).resolve()==expected_py.resolve(),'Pinned per-worker interpreter')
    v=helper('kernel');m=v.load_model(PRE/'joint');bits=mask(v);need(sum(bits)==NB,'Original full mask')
    outcome=dict(accepted_common=False,common_verdict='UNKNOWN',kind=kind);h=None
    try:
        if kind in ('master','transport_only'):
            import numpy as np
            import pyscipopt as scip
            validate(request['bindings']);model=unzip(request['model']['path']);records=request['cuts'];base=helper('master')
            base.PRE=PRE;base.RUN=folder;base.PRIVATE=private
            h,variables,params=base.master_backend(scip,np,model,deadline)
            actual_transport(model,records,folder,helper('encoding'),only_last=kind=='transport_only')
            outcome['all_actual_cut_transports_admitted']=True
            outcome['transport_only_checks_new_terminal_cut']=kind=='transport_only'
            save(folder/'dynamic_model_binding.json',dict(search_model=request['model'],base_master_sha256=sha(PRE/'master.json.gz'),readback_sha256=sha(folder/'master_backend_readback.json.gz')))
            if kind=='master':
                need(h.getParams()==params,'Pre-call options unchanged');solver_call(folder,kind,deadline,h.optimize)
                count=int(h.getNSols());outcome.update(status=str(h.getStatus()),solution_count=count,nodes=int(h.getNNodes()),LP_iterations=int(h.getNLPIterations()))
                if count==1:
                    raw=[float(h.getSolVal(h.getBestSol(),x)) for x in variables];np.savez_compressed(folder/'raw_solution.npz',vector=np.array(raw))
                    admission,nominee=base.nominate(raw,model,read(PRE/'premises.json'));save(folder/'exact_master_admission.json',admission)
                    outcome['nominee_accepted']=nominee is not None
                    if nominee is not None:outcome['state_values']=[int(x) for x in nominee]
                else:outcome['nominee_accepted']=False;outcome['reason']='NO_SINGLE_RETURNED_SOLUTION'
        else:
            import numpy as np
            import highspy
            validate([request['nominee']]);need(read(request['nominee']['path'])['values']==request['state_values'],'Bound unchanged exact nominee')
            states=request['state_values'];state_hash(states);fixed={STATE_START+j:float(x) for j,x in enumerate(states)}
            need(all(m.lower[j]<=x<=m.upper[j] for j,x in fixed.items()),'Original exact state boxes')
            save(folder/'fixed_schedule.json',dict(fixed_columns=[dict(column=j,value=int(x)) for j,x in fixed.items()],state_sha256=state_hash(states)))
            if kind=='recourse':
                rx=helper('transport');rx.PRE=PRE;rx.RUN=folder;rx.PRIVATE=private;rx.OPTIONS=dict(time_limit=60.,threads=1,random_seed=0,presolve='on',solver='simplex')
                lo=list(m.lower);hi=list(m.upper)
                for j,x in fixed.items():lo[j]=hi[j]=x
                np.savez_compressed(folder/'fixed_bounds.npz',column_lower=np.array(lo),column_upper=np.array(hi))
                h=highspy.Highs();rx.build_readback(h,highspy,np,m,bits,fixed,tuple(lo),tuple(hi),lambda *a,**k:guard(deadline))
                status=solver_call(folder,kind,deadline,h.run);sol=h.getSolution();outcome.update(status=str(h.getModelStatus()),run_status=str(status),value_valid=bool(sol.value_valid))
                if sol.value_valid:
                    raw=[float(x) for x in sol.col_value];np.savez_compressed(folder/'raw_solution.npz',vector=np.array(raw))
                    candidate=rx.restore_prescribed(raw,fixed,TAU)
                    if candidate is not None:
                        acceptance=helper('acceptance');acceptance.PRE=PRE;acceptance.RUN=folder
                        result=acceptance.candidate_check(v,np,np.array(candidate),bits)
                        need(all(candidate[j]==x for j,x in fixed.items()),'All prescribed common bits unchanged')
                        save(folder/'prescribed_restoration.json',dict(continuous_raw_bytes_unchanged=True,all12096_prescribed_bits=True,prescribed_within_exact_tau=True))
                        outcome['accepted_common']=result['accepted']
            else:
                need(kind=='phase1','Declared worker kind');phase_helper=helper('phase');phase_helper.PRE=folder;phase_helper.RUN=folder;phase_helper.PRIVATE=private
                with np.load(PRE/'phase_model.npz',allow_pickle=False) as z:phase={k:z[k].copy() for k in z.files}
                for j,x in fixed.items():phase['column_lower'][j]=phase['column_upper'][j]=x
                np.savez_compressed(folder/'phase_model.npz',**phase)
                h=phase_helper.backend(highspy,np,phase,deadline);status=solver_call(folder,kind,deadline,h.run);sol=h.getSolution();info=h.getInfo()
                outcome.update(status=str(h.getModelStatus()),run_status=str(status),dual_valid=bool(sol.dual_valid),numerical_objective=float(info.objective_function_value) if math.isfinite(info.objective_function_value) else None)
                raw=[float(x) for x in sol.row_dual]
                np.savez_compressed(folder/'raw_solution.npz',vector=np.array(sol.col_value),row_value=np.array(sol.row_value),row_dual=np.array(raw),col_dual=np.array(sol.col_dual))
                endpoints=unzip(PRE/'endpoint_map.json.gz')
                if sol.dual_valid and len(raw)==len(endpoints) and all(math.isfinite(x) for x in raw):
                    proof=phase_helper.reconstruct(m,bits,fixed,support_control(v),endpoints,raw,TAU,lambda:guard(deadline))
                    zipped(folder/'full_exact_candidate.json.gz',proof)
                    compact=dict(original_rows=m.rows,original_columns=m.cols,full_state_dimension=NB,omitted_coordinates_exact_zero=True,
                        state_terms=[[j,a] for j,a in enumerate(proof['full_A_transpose_d']) if bits[j] and frac(a)!=0],cut_rhs=proof['cut_rhs'],full_proof=bind(folder/'full_exact_candidate.json.gz'))
                    zipped(folder/'cut.json.gz',compact);outcome['strict_exact_nominee_exclusion']=proof['strictly_positive_expanded_margin']
                    if proof['strictly_positive_expanded_margin']:
                        encoding=encoding_for(compact,helper('encoding'),origin=states,progress=True);zipped(folder/'encoding.json.gz',encoding)
                        outcome['requested_encoding_eligible']=encoding['eligible_for_backend']
                else:outcome['strict_exact_nominee_exclusion']=False;outcome['reason']='NO_VALID_FINITE_COMPLETE_DUAL'
        validate(items);guard(deadline);outcome['provisional_until_completion']=True;save(folder/'result.json',outcome)
        final=dict(outcome);final['accepted_common']=bool(outcome['accepted_common'] and time.perf_counter()<=deadline)
        final['common_verdict']='VERIFIED_EXPANDED_COMMON_COMMITMENT' if final['accepted_common'] else 'UNKNOWN';final['phase_deadline_met']=time.perf_counter()<=deadline
        save(folder/'completion.json',dict(utc=utc(),final_admission=final,remaining_phase=deadline-time.perf_counter(),final_write_outside_sample=True))
    except BaseException as exc:
        save(folder/'failure.json',dict(utc=utc(),error_type=type(exc).__name__,message=str(exc),accepted_common=False,common_verdict='UNKNOWN'));raise
    finally:
        if h is not None and kind in ('master','transport_only'):h.freeProb()

def duplicate_candidate(bits,seen):
    digest=state_hash(bits)
    for previous in seen:
        if previous['sha256']==digest or previous['values']==bits:
            need(previous['values']==bits and previous['sha256']==digest,'State digest/value inconsistency')
            return True
    return False

def final_admission(accepted,deadline,now=None):
    now=time.perf_counter() if now is None else now;ok=bool(accepted and now<=deadline)
    return dict(accepted_common=ok,common_verdict='VERIFIED_EXPANDED_COMMON_COMMITMENT' if ok else 'UNKNOWN',phase_deadline_met=now<=deadline,admission_monotonic=now)

def ledger_snapshot():
    launches=sorted(RUN.glob('round_*/*/worker_launch_attempt.json'));attempts=sorted(RUN.glob('round_*/*/optimizer_attempt.json'))
    returns=sorted(RUN.glob('round_*/*/optimizer_returned.json'));cancelled=sorted(RUN.glob('round_*/*/optimizer_cancelled_before_call.json'))
    need(len(launches)<=25 and len(attempts)<=MAX_CALLS,'Finite batch call ceiling')
    return dict(worker_launch_attempts=len(launches),optimizer_attempt_records=len(attempts),optimizer_returned=len(returns),
        attempts_cancelled_before_optimizer=len(cancelled),entered_calls_from_return_or_error=sum(1 for p in RUN.glob('round_*/*/optimizer_returned.json'))+sum(1 for p in RUN.glob('round_*/*/optimizer_error.json')),
        calls=[dict(attempt=bind(p),returned=read(p.parent/'optimizer_returned.json') if (p.parent/'optimizer_returned.json').exists() else None,
                    cancelled_before_call=(p.parent/'optimizer_cancelled_before_call.json').exists()) for p in attempts],
        worker_closures=[bind(p) for p in sorted(RUN.glob('round_*/*/worker_closed.json'))])

def run(expected):
    started=time.perf_counter();deadline=started+PHASE
    need(not RUN.exists() and not PRIVATE.exists(),'Exactly one batch execution');items=load_prepared(expected)
    need(read(PRE/'plan.json')['runtime']==helper('master').runtimes(),'Pinned environments unchanged')
    RUN.mkdir();PRIVATE.mkdir(parents=True);save(RUN/'execution_started.json',dict(utc=utc(),pid=os.getpid(),parent_pid=os.getppid(),freeze_sha256=expected,
        source_sha256=sha(__file__),phase_seconds=PHASE,round_ceiling=ROUNDS,optimizer_call_ceiling=MAX_CALLS))
    accepted=False;reason='UNKNOWN';completed_rounds=0;launches=0;records=[];transported=0;error=None;stage='seed_stage'
    try:
        v=helper('kernel');m=v.load_model(PRE/'joint');bits=mask(v)
        need((m.rows,m.cols,len(m.data),sum(bits))==(69362,33936,291176,NB),'Unchanged original joint model')
        need(bits==tuple(int(STATE_START<=j<STATE_STOP) for j in range(m.cols)),'Explicit original state block')
        maps=read(PRE/'joint/column_maps.json')
        need(maps['worlds']==['identity','days_321'] and all(mp[STATE_START:STATE_STOP]==list(range(STATE_START,STATE_STOP)) for mp in maps['original_to_joint']),'Bound common coordinate identity')
        control=support_control(v);encoder=helper('encoding');records,old=seed_stage(v,m,bits,control,encoder,deadline)
        seen=[dict(sha256=state_hash(old),values=old,origin='closed_initial_nominee')]
        save(RUN/'initial_duplicate_set.json',dict(states=seen,initialized_before_first_master=True))
        base=unzip(PRE/'master.json.gz');need(len(base['rows'])==17212 and len(base['boxes'])==12432,'Inherited master scope')
        for round_id in range(1,ROUNDS+1):
            stage=f'round_{round_id}_master';guard(deadline,125.);round_folder=RUN/f'round_{round_id:02d}';round_folder.mkdir()
            model=search_model(base,records);zipped(round_folder/'search_master.json.gz',model)
            model_binding=bind(round_folder/'search_master.json.gz');bindings=[model_binding]+[r[k] for r in records for k in ('proof','encoding')]
            launches+=1;folder,status=launch('master',round_id,expected,deadline,dict(model=model_binding,cuts=records,bindings=bindings),launches)
            outcome=status['completion']['final_admission'];transported=len(records)
            if not outcome.get('nominee_accepted',False):reason='NO_SINGLE_EXACT_MASTER_NOMINEE';break
            nominee=outcome['state_values'];need(len(nominee)==NB,'Complete nominated state')
            if duplicate_candidate(nominee,seen):reason='REPEATED_NOMINEE';save(round_folder/'duplicate_stop.json',dict(state_sha256=state_hash(nominee),no_additional_solver=True));break
            seen.append(dict(sha256=state_hash(nominee),values=nominee,origin=round_id));save(round_folder/'novel_nominee.json',seen[-1])
            stage=f'round_{round_id}_recourse';launches+=1
            lp,lpstatus=launch('recourse',round_id,expected,deadline,dict(state_values=nominee,nominee=bind(round_folder/'novel_nominee.json')),launches)
            if lpstatus['completion']['final_admission']['accepted_common']:
                accepted=True;reason='FULL_ORIGINAL_EXPANDED_COMMON_WITNESS';completed_rounds=round_id;break
            stage=f'round_{round_id}_phase1';launches+=1
            phase,phstatus=launch('phase1',round_id,expected,deadline,dict(state_values=nominee,nominee=bind(round_folder/'novel_nominee.json')),launches)
            result=phstatus['completion']['final_admission'];completed_rounds=round_id
            if not result.get('strict_exact_nominee_exclusion',False):reason='NO_EXACT_PROGRESSING_PHASE1_CUT';break
            if not result.get('requested_encoding_eligible',False):reason='NONPROGRESSING_OR_UNSUPPORTED_ENCODING';break
            records.append(dict(kind='refinement',round=round_id,proof=bind(phase/'cut.json.gz'),encoding=bind(phase/'encoding.json.gz')))
            save(round_folder/'next_cut.json',records[-1])
            if round_id==ROUNDS:
                reason='EIGHT_ROUND_CEILING';stage='terminal_transport_only';guard(deadline,CLOSURE_MARGIN)
                final_model=search_model(base,records);zipped(round_folder/'terminal_master.json.gz',final_model);binding=bind(round_folder/'terminal_master.json.gz')
                launches+=1;_,status=launch('transport_only',round_id,expected,deadline,dict(model=binding,cuts=records,bindings=[binding]+[r[k] for r in records for k in ('proof','encoding')]),launches)
                need(status['completion']['final_admission']['all_actual_cut_transports_admitted'],'Terminal transport-only admission');transported=len(records)
        validate(items);guard(deadline)
    except BaseException as exc:
        accepted=False;reason='STOPPED_'+type(exc).__name__;error=dict(stage=stage,error_type=type(exc).__name__,message=str(exc))
        save(RUN/'failure.json',dict(utc=utc(),**error,common_verdict='UNKNOWN',no_retry=True))
    finally:
        elapsed=time.perf_counter()-started;final=final_admission(accepted,deadline);ledger=ledger_snapshot()
        integrity=True
        try:validate(items)
        except BaseException as exc:integrity=False;final=final_admission(False,deadline);save(RUN/'final_input_failure.json',dict(error_type=type(exc).__name__,message=str(exc)))
        result=dict(stop_reason=reason,completed_rounds=completed_rounds,new_cut_count=max(0,len(records)-336),seed_count=min(336,len(records)),
            cuts_with_completed_actual_transport=transported,total_cut_records=len(records),terminal_cut_numeric_transport='ADMITTED' if transported==len(records) and records else 'NOT_ADMITTED',
            one_adaptive_trajectory=True,no_global_infeasibility_claim=True,all_frozen_bytes_unchanged=integrity,error=error,ledger=ledger,provisional_until_completion=True,**final)
        save(RUN/'result.json',result);final=final_admission(final['accepted_common'] and integrity,deadline);elapsed=time.perf_counter()-started
        save(RUN/'completion.json',dict(utc=utc(),phase_seconds=elapsed,phase_soft_overrun=max(0.,elapsed-PHASE),final_admission=final,
            stop_reason=reason,ledger=ledger,all_frozen_bytes_unchanged=integrity,final_write_cleanup_outside_sample=True,no_retry=True,no_ninth_nomination=True))
        save(RUN/'private_logs.json',dict(raw_logs_public=False,files=[bind(p) for p in PRIVATE.rglob('*') if p.is_file()]))
        save(RUN/'producer_files.json',dict(files=[bind(p) for p in RUN.rglob('*') if p.is_file()]))
        print(json.dumps(dict(**final,stop_reason=reason,optimizer_attempts=ledger['optimizer_attempt_records'])),flush=True)

def self_test():
    need(not (ARM/'synthetic_tests.json').exists(),'One invented-control run');checks=[]
    class Toy:
        rows=2;cols=3;indptr=(0,2,4);indices=(0,1,0,2);data=(1.,1.,1.,1.)
        row_lower=(2.,-math.inf);row_upper=(2.,1.);lower=(0.,0.,0.);upper=(1.,1.,1.)
    # One exact state and two private recourses; selected rows cancel the state.
    p=sparse_proof(Toy(),(1,0,0),(0.5,1.,0.),{0:Q(1),1:Q(-1)})
    need(p['state_terms']==[] and dict(p['full_q_nonzero'])=={1:rat(Q(1)),2:rat(Q(-1))},'Retain exact signed continuous residuals and zero completion')
    need(frac(p['cut_rhs'])==-4*TAU and p['control_satisfied'],'Both row and continuous tau losses')
    checks.append('complete selected-row accumulation, exact cancellation, signed support and both tau losses')
    class Contradiction(Toy):row_lower=(4.,-math.inf);row_upper=(4.,1.)
    bad=sparse_proof(Contradiction(),(1,0,0),(0.5,1.,0.),{0:Q(1),1:Q(-1)})
    need(not bad['state_terms'] and not bad['control_satisfied'],'Constant contradiction cannot pass old control')
    checks.append('all-zero state separator is a control contradiction, not a global negative')
    zeros=[0]*NB;ones=list(zeros);ones[12]=1;seen=[dict(sha256=state_hash(zeros),values=zeros)]
    need(duplicate_candidate(zeros,seen) and not duplicate_candidate(ones,seen),'Full-bit duplicate set')
    need(final_admission(True,2.,1.)['accepted_common'] and not final_admission(True,2.,3.)['accepted_common'],'Authoritative late closure')
    checks.append('old nominee included in exact hash/value duplicate checks and late admission rejected')
    # Invented labels exercise the same336-case resolver, without reading an archived row.
    metas=[];orig=[]
    for wi,w in enumerate(('identity','days_321')):
        labels=[]
        for t in range(168):
            for fam,uid in [('aggregate_balance','ALL')]+[('thermal_upper',u) for u in THERMAL]+[('nodal_balance','107'),('branch_flow','10')]:
                r=len(labels);labels.append(dict(row=str(r),family=fam,hour_0based=str(t),uid=uid));orig.append([wi,r])
        metas.append((w,labels))
    need(len(metadata_templates(metas,orig))==336,'Full fixed structural denominator')
    broken=[(metas[0][0],metas[0][1][:-1]),metas[1]]
    try:metadata_templates(broken,orig)
    except ValueError:pass
    else:raise AssertionError('Missing key admitted')
    checks.append('complete invented336-map denominator and missing selected key rejection')
    ARM.mkdir(parents=True,exist_ok=True);save(ARM/'synthetic_tests.json',dict(status='PASS',utc=utc(),source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),
        checks=checks,scientific_inputs_read=0,optimizer_calls=0,backend_imports=0,old_test_suites_repeated=False))
    print(json.dumps(dict(status='PASS_INVENTED_ONLY',groups=len(checks))),flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    for flag in ('self-test','prepare-only','run-prepared','worker'):g.add_argument('--'+flag,action='store_true')
    p.add_argument('--expected-freeze-sha256');p.add_argument('--request');p.add_argument('--expected-request-sha256');args=p.parse_args()
    if args.self_test:self_test()
    elif args.prepare_only:prepare()
    elif args.worker:
        need(args.expected_freeze_sha256 and args.request and args.expected_request_sha256,'Bound worker arguments');worker(args.expected_freeze_sha256,args.request,args.expected_request_sha256)
    else:need(args.expected_freeze_sha256,'External freeze required');run(args.expected_freeze_sha256)

if __name__=='__main__':
    try:main()
    except BaseException as exc:
        folder=RUN if RUN.exists() else PRE if PRE.exists() else ARM;folder.mkdir(parents=True,exist_ok=True)
        path=folder/('outer_failure_'+uuid.uuid4().hex+'.json')
        save(path,dict(utc=utc(),error_type=type(exc).__name__,message=str(exc),common_verdict='UNKNOWN',no_retry=True));raise
