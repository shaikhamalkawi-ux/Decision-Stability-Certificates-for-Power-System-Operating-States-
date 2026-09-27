"""One unchanged repaired schedule, two inherited cut gates, one identity LP at most."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import importlib.metadata
import importlib.util
import json
import math
from pathlib import Path
import struct
import sys
import time

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
ARM=ROOT/'results/research_next/repaired_crossworld_schema2';PRE=ARM/'prepared';RUN=ARM/'run01'
PRIVATE=ROOT/'.work/researchnext_repaired_crossworld_schema2/run01'
ORIGINAL=ROOT/'results/research_next/common_commitment/prepared'
REPAIR=ROOT/'results/research_next/day321_local_repair'
AFFINE=ROOT/'results/research_next/union_affine_cut_schema2'
PROTOCOL=ROOT/'docs/research_next/REPAIRED_CROSSWORLD_SCHEMA2_PROTOCOL.md'
BASE=ROOT/'src/researchnext_common_commitment.py'
BASE_SHA='039af59750b4c165d877b9878ac14af02a202700b46739ba96a8914075ae3284'
KERNEL=ROOT/'src/research8h_standalone_verify.py'
KERNEL_SHA='708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'
PYTHON=Path('C:/Users/gmalkawi/OneDrive - Higher Colleges of Technology/Documents 1/ChatGPT/3/.work/solver_env/Scripts/python.exe')
PACKAGES={'numpy':'2.3.5','scipy':'1.18.1','highspy':'1.12.0'}
TAU=Q.from_float(1e-5);PHASE=240.;GUARD=65.
OPTIONS=dict(time_limit=60.,threads=1,random_seed=0,presolve='on',solver='simplex')
WORLDS=('identity','days_321')
WORLD_FILES=('matrix.npz','bounds.npz','integrality.npz','model_metadata.json','native_inputs.npz','permutation.csv','row_metadata.csv.gz','native_spec.json')
JOINT_FILES=('matrix.npz','bounds.npz','integrality.npz','column_maps.json','row_origins.json')
PINS={
 'src/researchnext_repaired_crossworld.py':'c64409480c5649b84620e96bfbb173d1779fca8a5a1c42eef7a2a2c7fedf6aa8',
 'docs/research_next/REPAIRED_CROSSWORLD_PROTOCOL.md':'0cb5126e78ebefaa5d259016cde7aa575ebe633be33a0da15d7b17603d10c746',
 'results/research_next/repaired_crossworld/failure.json':'b41de7c0f0a5bedef3b78494f4e0abec3a9c2ce7d7aa04c4b81f5299c410f7ce',
 'results/research_next/repaired_crossworld/prepared/failure.json':'66642eca1af66d3c224c3e49daa4ade684defcc5d699cb5255275d279bfe11f7',
 'docs/research_next/REPAIRED_SCHEDULE_CROSSWORLD_PROPOSAL.md':'ad35cb3231b4e1d10e06c18a80f645f39a183c1f974dce52e7904cb0c88aef99',
 'results/research_next/common_commitment/prepared/prepared_freeze.json':'4f21891d7d1f1793dd92e5b830edf5b5cf62474e5521d788c9aec17929ea9a59',
 'results/research_next/common_commitment/prepared/input_manifest.json':'8ff99b1f4450ac15e91b26a261a85c98d574bbbdac3f7fe149efd9fd07204a5c',
 'results/research_next/common_commitment/INDEPENDENT_PREPARED_REVIEW.json':'956b37cbcdd49571a6a79611da197a5be840a5c2747ffbd60576c90805d58e6b',
 'results/research_next/day321_local_repair/prepared/prepared_freeze.json':'78f9c1eb621da6f9e177689849971004544d6ab419e5141a7dcf35145dd2ccf2',
 'results/research_next/day321_local_repair/prepared/input_manifest.json':'9c79243cb96114a91786ed3e3bc349a96549b036f5016172fd4b33e57a1b4fe1',
 'results/research_next/day321_local_repair/run01/candidate_vector.npz':'fc9276c52baa182b0eba018df548bb0125290cb2413dd469c1899516c03733c3',
 'results/research_next/day321_local_repair/INDEPENDENT_POSTRUN_REVIEW.json':'76f3b5121ed7248ee6cd71df61af483408c85a57d15abed6c622a793490bcc49',
 'results/research_next/union_affine_cut_schema2/prepared/prepared_freeze.json':'30a47bf54cdceb32e82836ab6bb5cf77de01c695f46e91aa243c799446d1a8c2',
 'results/research_next/union_affine_cut_schema2/prepared/input_manifest.json':'65235741d7860d9e99b0650c45ac209ba38ac028b758e4f12f1505ad2800f53c',
 'results/research_next/union_affine_cut_schema2/run01/identity_cut.json':'8ba409f8702486dcdebc7611a98609696348c41d46af8fa38d7e77b5614621cb',
 'results/research_next/union_affine_cut_schema2/run01/days_321_cut.json':'7fe192f2acd9ebd1e14eeecde3ece0e3d5d24ede8408e6047b1cb9dd597f30dd',
 'results/research_next/union_affine_cut_schema2/independent_postrun_review.json':'04b94ab9ca268615e1980066e6654fec58e01b92b96def0049a3dc94cff9a3f8',
 'results/research_next/selected_dwell_cover_independent_review/postrun_review.json':'8eaa8fdc9e00e417f8d4b16eba1c0d967f8310fe2f3d2ade2989e197255d51f4',
 'results/research_next/common_union/PRECALL_INTERRUPTION.json':'8490bdd6e8de9eea9b3234d60eb65d79da1dd026f553d9e638af1a71cadce184',
 'results/research_next/common_union/PREBINDING_PERFORMANCE_PROBE.json':'23abb5eb3d0690727dfbc2cc7ef44cb16a44fe94578a5595675c7cb94af837b2',
}

class PhaseGuard(RuntimeError):pass
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
    need(len({x['path'].casefold() for x in items})==len(items),'Duplicate binding')
    for item in items:need(bind(item['path'])==item,'Changed frozen bytes: '+item['path'])
def rat(x):return dict(numerator=str(x.numerator),denominator=str(x.denominator),approximate=float(x))
def fraction(x):
    n,d=int(x['numerator']),int(x['denominator']);need(d>0,'Positive rational denominator');return Q(n,d)
def module(path,digest,name):
    need(sha(path)==digest,'Pinned helper changed')
    spec=importlib.util.spec_from_file_location(name,path);obj=importlib.util.module_from_spec(spec);sys.modules[name]=obj;spec.loader.exec_module(obj);return obj
def kernel():return module(KERNEL,KERNEL_SHA,'repaired_crossworld_exact_kernel')
def mask(v,folder,n):return tuple(v.vector(v.read_npz(folder/'integrality.npz',('integrality',))['integrality'],('|u1',),n,'original mask'))
def vector(v,path,n):return tuple(v.vector(v.read_npz(path,('vector',))['vector'],('<f8',),n,'saved vector'))
def environment():
    need(Path(sys.executable).resolve()==PYTHON.resolve() and sys.version_info[:3]==(3,12,14),'Pinned Python environment')
    packages={n:importlib.metadata.version(n) for n in PACKAGES};need(packages==PACKAGES,'Pinned packages')
    return dict(executable=sys.executable,python=sys.version,packages=packages)
def float_bytes(values):return b''.join(struct.pack('<d',float(x)) for x in values)

def capture_inputs():
    captured={}
    def capture(p,expected=None):
        p=Path(p).resolve();data=p.read_bytes();item=bind(p,data);key=str(p).casefold()
        if expected is not None:need(item==expected,'Historical captured bytes mismatch')
        need(key not in captured or captured[key][1]==item,'Conflicting historical binding')
        captured[key]=(data,item);return data
    for rel,digest in PINS.items():need(hashlib.sha256(capture(ROOT/rel)).hexdigest()==digest,'Pinned input changed: '+rel)
    for folder,count in ((ORIGINAL,48),(REPAIR/'prepared',65),(AFFINE/'prepared',73)):
        doc=json.loads(captured[str((folder/'input_manifest.json').resolve()).casefold()][0]);need(len(doc['files'])==count,'Inherited manifest denominator')
        for item in doc['files']:capture(item['path'],item)
    for path in (Path(__file__),PROTOCOL,BASE,KERNEL,ARM/'synthetic_tests.json'):capture(path)
    need(sha(BASE)==BASE_SHA and sha(KERNEL)==KERNEL_SHA,'Acceptance helper pins')
    return captured

def captured_member_sha(captured,path):
    key=str(Path(path).resolve()).casefold()
    need(key in captured,'Required exact archived manifest member is absent: '+str(path))
    return captured[key][1]['sha256']

def validate_cut_schema(cut,world):
    need(cut['status']=='VERIFIED_GLOBAL_EXPANDED_AFFINE_NECESSARY_CUT' and cut['world']==world,'Inherited cut scope')
    need(fraction(cut['tau'])==TAU and fraction(cut['cap'])==Q(23195)+TAU and cut['new_derived_row_expansion']==0,'Exactly inherited expanded cut')
    need(cut['all_nonU_coefficients_exact_zero'] and cut['all_endpoint_multipliers_nonnegative'],'Inherited proof flags')
    cols=[x['column'] for x in cut['coefficients']]
    need(len(cols)==len(set(cols))==82 and all(type(j) is int and 6888<=j<10920 for j in cols),'Original U-only support')
    need(all(fraction(x['coefficient'])>0 for x in cut['coefficients']),'Inherited nonnegative support')

def prepare():
    started=time.perf_counter();need(not PRE.exists() and not RUN.exists(),'One preparation only')
    runtime=environment();captured=capture_inputs();initial=[x[1] for x in captured.values()];v=kernel()
    receipt=read(ARM/'synthetic_tests.json');need(receipt['source_sha256']==sha(__file__) and receipt['protocol_sha256']==sha(PROTOCOL),'Fixture provenance')
    PRE.mkdir(parents=True);save(PRE/'preparation_started.json',dict(utc=utc(),source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),optimizer_calls=0,cut_evaluations=0))
    copies=[]
    def copy(source,target):
        data,item=captured[str(source.resolve()).casefold()];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        need(sha(target)==item['sha256'],'Captured byte copy mismatch');copies.append(dict(original=item,copy=bind(target)))
    for world in WORLDS:
        for name in WORLD_FILES:copy(ORIGINAL/world/name,PRE/world/name)
    for name in JOINT_FILES:copy(ORIGINAL/'joint'/name,PRE/'joint'/name)
    copy(ORIGINAL/'gen.csv',PRE/'gen.csv');copy(REPAIR/'run01/candidate_vector.npz',PRE/'repair_vector.npz')
    for world in WORLDS:copy(AFFINE/'run01'/(world+'_cut.json'),PRE/(world+'_cut.json'))
    proof=read(REPAIR/'INDEPENDENT_POSTRUN_REVIEW.json')
    need(proof['expanded_pass'] and proof['native_pass'] and proof['candidate_sha256']==sha(PRE/'repair_vector.npz'),'Accepted exact individual source')
    need(read(ROOT/'results/research_next/selected_dwell_cover_independent_review/postrun_review.json')['original_common_question']=='UNKNOWN','Dwell gate scope')
    relations=[]
    for world in WORLDS:
        for name in ('matrix.npz','bounds.npz','integrality.npz','model_metadata.json'):
            need(sha(AFFINE/'prepared'/world/name)==sha(PRE/world/name),'Cut original-model relation')
            relations.append(dict(role='cut_'+world,name=name,sha256=sha(PRE/world/name)))
    need(captured_member_sha(captured,AFFINE/'prepared/joint/column_maps.json')==sha(PRE/'joint/column_maps.json'),'Cut shared coordinate relation')
    for name in ('matrix.npz','bounds.npz','integrality.npz','model_metadata.json','native_inputs.npz','native_spec.json'):
        need(sha(REPAIR/'prepared/model'/name)==sha(PRE/'days_321'/name),'Positive original-model/native relation')
        relations.append(dict(role='positive_days321',name=name,sha256=sha(PRE/'days_321'/name)))
    for world in WORLDS:validate_cut_schema(read(PRE/(world+'_cut.json')),world)
    m=v.load_model(PRE/'identity');bits=mask(v,PRE/'identity',m.cols);joint=v.load_model(PRE/'joint');jb=mask(v,PRE/'joint',joint.cols)
    need((m.rows,m.cols,len(m.data),sum(bits))==(34681,23016,145588,12096),'Original identity dimensions')
    need((joint.rows,joint.cols,len(joint.data),sum(jb))==(69362,33936,291176,12096),'Original joint dimensions')
    need(bits==tuple(int(6888<=j<18984) for j in range(m.cols)) and jb==tuple(int(6888<=j<18984) for j in range(joint.cols)),'Full original masks')
    repair=vector(v,PRE/'repair_vector.npz',23016);need(all(math.isfinite(x) for x in repair),'Finite accepted point')
    fixed={j:repair[j] for j,b in enumerate(bits) if b};need(len(fixed)==12096 and all(x in (0.,1.) for x in fixed.values()),'Prescribed exact original bits')
    maps=read(PRE/'joint/column_maps.json');need(maps['worlds']==list(WORLDS),'Original mapping order')
    for world,mapping in zip(WORLDS,maps['original_to_joint']):
        need(len(mapping)==23016 and len(set(mapping))==23016 and mapping[6888:18984]==list(range(6888,18984)),'Complete shared original state map')
        need(all(type(j) is int and 0<=j<33936 for j in mapping),'Joint index range')
        need(mask(v,PRE/world,23016)==bits,'World original mask identity')
        meta=read(PRE/world/'model_metadata.json');need(meta['offsets']==dict(P=0,U=6888,Y=10920,Z=14952,theta=18984) and meta['budget_MWh']==23195,'Original model semantics')
    need(set(maps['original_to_joint'][0])|set(maps['original_to_joint'][1])==set(range(33936)),'Full joint map coverage')
    lower=list(m.lower);upper=list(m.upper)
    for j,x in fixed.items():need(m.lower[j]<=x<=m.upper[j],'Original state box');lower[j]=upper[j]=x
    state_rows=[]
    for r in range(m.rows):
        entries=range(m.indptr[r],m.indptr[r+1])
        if all(bits[m.indices[k]] for k in entries):
            val=sum((Q(m.data[k])*Q(fixed[m.indices[k]]) for k in entries),Q(0))
            need((not math.isfinite(m.row_lower[r]) or val>=Q(m.row_lower[r])) and (not math.isfinite(m.row_upper[r]) or val<=Q(m.row_upper[r])),'Exact unchanged schedule state row')
            state_rows.append(r)
    need(len(state_rows)==16032,'All original identity state-only rows')
    import numpy as np
    np.savez_compressed(PRE/'fixed_bounds.npz',column_lower=np.array(lower),column_upper=np.array(upper))
    save(PRE/'fixed_schedule.json',dict(source_vector_sha256=sha(PRE/'repair_vector.npz'),fixed_columns=[dict(column=j,value_hex=x.hex()) for j,x in fixed.items()],
        state_rows=state_rows,full_binary_count=12096,no_permutation_or_canonicalization=True,new_schedule_constructions=0))
    save(PRE/'copy_provenance.json',dict(copies=copies,model_proof_relations=relations))
    save(PRE/'plan.json',dict(options=OPTIONS,phase_seconds=PHASE,start_guard_seconds=GUARD,runtime=runtime,candidates=1,maximum_optimizer_calls=1,
        cut_gate_worlds=list(WORLDS),gate_scientific_evaluations=0,LP_world='identity',original_rows=34681,original_columns=23016,
        acceptance='unchanged original full identity/joint/both worlds and native constraints',no_retry=True,no_ray=True))
    validate(initial);items=initial+[bind(p) for p in PRE.rglob('*') if p.is_file()];validate(items)
    save(PRE/'input_manifest.json',dict(files=items));validate(items)
    save(PRE/'prepared_freeze.json',dict(utc=utc(),source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),manifest_sha256=sha(PRE/'input_manifest.json'),
        bindings=len(items),copies=len(copies),state_rows_checked=len(state_rows),optimizer_calls=0,cut_evaluations=0,highspy_imports=0,
        elapsed_seconds=time.perf_counter()-started,separate_source_prepared_review_and_explicit_execution_GO_required=True))
    print(json.dumps(dict(status='PREPARED_NO_CUT_OR_LP',bindings=len(items),freeze_sha256=sha(PRE/'prepared_freeze.json'))),flush=True)

def cut_value(cut,fixed):
    value=fraction(cut['alpha'])+sum((fraction(x['coefficient'])*Q(fixed[x['column']]) for x in cut['coefficients']),Q(0))
    cap=fraction(cut['cap']);return dict(value=rat(value),cap=rat(cap),excess=rat(value-cap),strictly_violated=value>cap)
def restore_prescribed(raw,fixed,tau):
    if not all(math.isfinite(x) for x in raw):return None
    out=list(raw)
    for j,value in fixed.items():
        if abs(Q(raw[j])-Q(value))>tau:return None
        out[j]=value
    need(float_bytes(x for j,x in enumerate(raw) if j not in fixed)==float_bytes(x for j,x in enumerate(out) if j not in fixed),'Continuous coordinates changed')
    return out
def combine(points,maps,ncols,shared):
    out=[None]*ncols
    for point,mapping in zip(points,maps):
        need(len(point)==len(mapping),'Projection shape')
        for old,j in enumerate(mapping):
            if out[j] is not None:need(j in shared and point[old]==out[j],'Shared coordinate mismatch')
            else:out[j]=point[old]
    need(all(x is not None for x in out),'Composite coverage')
    for point,mapping in zip(points,maps):
        need(float_bytes(point[j] for j,k in enumerate(mapping) if k not in shared)==float_bytes(out[k] for k in mapping if k not in shared),'Private continuous bytes changed')
    return out

def extract_rows(matrix,rowwise,nrows,ncols,checkpoint):
    # pybind vector getters return new lists. Materialize each exactly once.
    start=tuple(matrix.start_);indices=tuple(matrix.index_);values=tuple(matrix.value_)
    need(len(indices)==len(values) and len(start)==(nrows if rowwise else ncols)+1 and start[0]==0 and start[-1]==len(values),'Sparse array shape')
    need(all(a<=b for a,b in zip(start,start[1:])),'Sparse pointer monotonicity')
    need(all(0<=j<(ncols if rowwise else nrows) for j in indices),'Sparse index range');out=[[] for _ in range(nrows)]
    for i in range(nrows if rowwise else ncols):
        if rowwise:out[i]=[(int(indices[k]),float(values[k])) for k in range(start[i],start[i+1])]
        else:
            for k in range(start[i],start[i+1]):out[indices[k]].append((i,float(values[k])))
        if i%2048==0:checkpoint('sparse_readback_progress',record=False)
    return [sorted(row) for row in out]

def build_readback(h,highspy,np,m,bits,fixed,lower,upper,checkpoint):
    need(h.version()=='1.12.0','Backend version')
    for key,value in {**OPTIONS,'log_to_console':False,'log_file':str((PRIVATE/'solver.log').resolve())}.items():need(h.setOptionValue(key,value)==highspy.HighsStatus.kOk,'Rejected option')
    lp=highspy.HighsLp();lp.num_row_,lp.num_col_=m.rows,m.cols
    lp.col_cost_=np.zeros(m.cols);lp.col_lower_=np.array(lower);lp.col_upper_=np.array(upper)
    lp.row_lower_=np.array(m.row_lower);lp.row_upper_=np.array(m.row_upper);lp.offset_=0.;lp.sense_=highspy.ObjSense.kMinimize
    lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise;lp.a_matrix_.num_row_,lp.a_matrix_.num_col_=m.rows,m.cols
    lp.a_matrix_.start_=np.array(m.indptr,dtype=np.int32);lp.a_matrix_.index_=np.array(m.indices,dtype=np.int32);lp.a_matrix_.value_=np.array(m.data)
    lp.integrality_=[highspy.HighsVarType.kContinuous]*m.cols;checkpoint('LP_assembled');need(h.passModel(lp)==highspy.HighsStatus.kOk,'Rejected model')
    got=h.getLp();need((got.num_row_,got.num_col_)==(m.rows,m.cols),'Readback shape')
    cl=tuple(got.col_lower_);cu=tuple(got.col_upper_);rl=tuple(got.row_lower_);ru=tuple(got.row_upper_);cost=tuple(got.col_cost_);integers=tuple(got.integrality_)
    need((cl,cu,rl,ru)==(lower,upper,m.row_lower,m.row_upper),'Readback bounds')
    need(all(x==0 for x in cost) and got.offset_==0 and got.sense_==highspy.ObjSense.kMinimize,'Zero objective')
    need(not integers or all(x==highspy.HighsVarType.kContinuous for x in integers),'Unexpected free integrality')
    matrix=got.a_matrix_;fmt=matrix.format_;need(fmt in (highspy.MatrixFormat.kRowwise,highspy.MatrixFormat.kColwise),'Sparse format')
    rows=extract_rows(matrix,fmt==highspy.MatrixFormat.kRowwise,m.rows,m.cols,checkpoint);data=[];indices=[];indptr=[0]
    for i,row in enumerate(rows):
        need(row==list(zip(m.indices[m.indptr[i]:m.indptr[i+1]],m.data[m.indptr[i]:m.indptr[i+1]])),'Exact backend coefficients')
        indices.extend(j for j,c in row);data.extend(c for j,c in row);indptr.append(len(data))
        if i%2048==0:checkpoint('coefficient_comparison',record=False)
    actual={}
    for key,value in OPTIONS.items():
        status,current=h.getOptionValue(key);need(status==highspy.HighsStatus.kOk and current==value,'Option readback');actual[key]=current
    np.savez_compressed(RUN/'backend_readback.npz',data=np.array(data),indices=np.array(indices,dtype=np.int64),indptr=np.array(indptr,dtype=np.int64),
        shape=np.array([m.rows,m.cols],dtype=np.int64),column_lower=np.array(cl),column_upper=np.array(cu),row_lower=np.array(rl),row_upper=np.array(ru),
        objective=np.array(cost),original_integrality=np.array(bits,dtype=np.uint8),backend_integrality=np.zeros(m.cols,dtype=np.uint8))
    save(RUN/'backend_readback.json',dict(rows=m.rows,columns=m.cols,coefficients=len(data),original_bits_fixed=len(fixed),same_original_matrix=True,
        only_state_boxes_changed=True,all_backend_continuous=True,options=actual,array_materializations=dict(start=1,indices=1,values=1),
        readback_sha256=sha(RUN/'backend_readback.npz'),optimizer_calls=0));checkpoint('full_backend_readback_archived')

def accepted_candidate(v,np,raw,fixed,checkpoint):
    if raw.shape!=(23016,):return dict(eligible=False,accepted=False)
    point=restore_prescribed(tuple(float(x) for x in raw),fixed,TAU)
    if point is None:return dict(eligible=False,accepted=False)
    need(all(point[j]==x for j,x in fixed.items()),'Prescribed complete state block')
    np.savez_compressed(RUN/'identity_candidate.npz',vector=np.array(point));base=module(BASE,BASE_SHA,'repaired_crossworld_native_checker');need(base.TAU==TAU,'Native tau')
    repair=vector(v,PRE/'repair_vector.npz',23016);maps=read(PRE/'joint/column_maps.json')['original_to_joint'];world_results=[]
    for world,values in zip(WORLDS,(point,repair)):
        folder=PRE/world;m=v.load_model(folder);bits=mask(v,folder,m.cols)
        need(all(values[j]==x for j,x in fixed.items()),'Identical prescribed bits in each world')
        exact=v.check_point(m,values,bits,TAU);native=base.native_check(v,values,folder,read(folder/'model_metadata.json'),read(folder/'native_spec.json'))
        world_results.append(dict(world=world,exact=exact,native=native));checkpoint('acceptance_'+world,precall=False)
    composite=combine((point,repair),maps,33936,set(fixed));np.savez_compressed(RUN/'composite_joint_candidate.npz',vector=np.array(composite))
    jm=v.load_model(PRE/'joint');jb=mask(v,PRE/'joint',jm.cols);joint=v.check_point(jm,composite,jb,TAU);checkpoint('joint_full_acceptance',precall=False)
    accepted=joint['expanded_pass'] and all(x['exact']['expanded_pass'] and x['native']['expanded_pass'] for x in world_results)
    result=dict(eligible=True,accepted=accepted,worlds=world_results,joint=joint,all12096_prescribed_bits_equal=True,raw_identity_continuous_bytes_unchanged=True,
        original_repair_continuous_bytes_unchanged=True,nominal_feasibility_claim=False,original_masks_used=True)
    save(RUN/'exact_candidate_checks.json',result);return result

def self_test():
    need(not (ARM/'synthetic_tests.json').exists(),'One invented fixture run');started=time.perf_counter();checks=[]
    def q(x):return rat(Q(x))
    cut=dict(alpha=q(2),cap=q(5),coefficients=[dict(column=1,coefficient=q(3))])
    need(not cut_value(cut,{1:1.})['strictly_violated'],'Exact equality cut gate')
    cut['cap']=q(Q(5)-Q(1,16));need(cut_value(cut,{1:1.})['strictly_violated'],'Strict positive cut gate')
    cut['cap']=q(6);need(not cut_value(cut,{1:1.})['strictly_violated'],'Passing necessary gate')
    checks.append('exact affine pass/equality/rejection')
    raw=(float.fromhex('-0x0.0p+0'),1.-2**-30,2.5)
    restored=restore_prescribed(raw,{1:1.},Q(1,100000));need(restored is not None and float_bytes((restored[0],restored[2]))==float_bytes((raw[0],raw[2])),'Preserve private bytes')
    need(restore_prescribed(raw,{1:0.},TAU) is None and restore_prescribed((math.nan,0.),{1:0.},TAU) is None,'Reject wrong/nonfinite states')
    need(restore_prescribed((float(TAU),),{0:0.},TAU)==[0.] and restore_prescribed((math.nextafter(float(TAU),math.inf),),{0:0.},TAU) is None,'Exact tau eligibility boundary')
    checks.append('prescribed rather than nearest bits and signed-zero continuous bytes')
    need(combine(((2.,1.),(3.,1.)),((0,1),(2,1)),3,{1})==[2.,1.,3.],'Composite maps')
    try:combine(((2.,1.),(3.,0.)),((0,1),(2,1)),3,{1})
    except ValueError:pass
    else:raise AssertionError('Conflicting shared states admitted')
    try:combine(((2.,1.),),((0,1),),3,{1})
    except ValueError:pass
    else:raise AssertionError('Incomplete composite admitted')
    checks.append('private mapping and shared-state mismatch')
    class Tiny:
        def __init__(self,arrays):self.arrays=arrays;self.calls=[0,0,0]
        def fetch(self,n):self.calls[n]+=1;need(self.calls[n]==1,'Repeated pybind property access');return list(self.arrays[n])
        start_=property(lambda s:s.fetch(0));index_=property(lambda s:s.fetch(1));value_=property(lambda s:s.fetch(2))
    expected=[[(0,1.),(2,-2.)],[(1,3.)]]
    for rowwise,arrays in ((True,([0,2,3],[0,2,1],[1.,-2.,3.])),(False,([0,1,2,3],[0,1,0],[1.,3.,-2.]))):
        toy=Tiny(arrays);need(extract_rows(toy,rowwise,2,3,lambda *a,**k:None)==expected and toy.calls==[1,1,1],'Cached sparse transport')
    checks.append('CSR and CSC readback with getters forbidden after first access')
    toy_root=ROOT/'invented_unread_archive';toy_path=toy_root/'prepared/joint/column_maps.json';toy_data=b'invented map'
    toy={str(toy_path.resolve()).casefold():(toy_data,bind(toy_path,toy_data))}
    need(captured_member_sha(toy,toy_path)==hashlib.sha256(toy_data).hexdigest(),'Full manifest member name')
    try:captured_member_sha(toy,toy_root/'prepared/column_maps.json')
    except ValueError:pass
    else:raise AssertionError('Undeclared shortened manifest member admitted')
    checks.append('exact full manifest map member and wrong shortened name rejected')
    ARM.mkdir(parents=True,exist_ok=True);save(ARM/'synthetic_tests.json',dict(status='PASS',utc=utc(),source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),
        checks=checks,scientific_inputs_read=0,scientific_cut_evaluations=0,optimizer_calls=0,elapsed_seconds=time.perf_counter()-started));print(json.dumps(dict(status='PASS_SYNTHETIC_ONLY',groups=len(checks))),flush=True)

def run(expected):
    phase=time.perf_counter();need(not RUN.exists() and not PRIVATE.exists(),'One fresh execution only')
    fp=PRE/'prepared_freeze.json';need(sha(fp)==expected,'Trusted freeze');freeze=read(fp)
    need(freeze['source_sha256']==sha(__file__) and freeze['protocol_sha256']==sha(PROTOCOL),'Frozen source/protocol')
    mp=PRE/'input_manifest.json';need(sha(mp)==freeze['manifest_sha256'],'Frozen manifest');bindings=read(mp)['files'];validate(bindings)
    plan=read(PRE/'plan.json');need(plan['runtime']==environment() and plan['options']==OPTIONS,'Frozen runtime/options')
    transport=[bind(fp),bind(mp)];v=kernel();m=v.load_model(PRE/'identity');bits=mask(v,PRE/'identity',m.cols)
    prescribed=read(PRE/'fixed_schedule.json');fixed={x['column']:float.fromhex(x['value_hex']) for x in prescribed['fixed_columns']}
    need(len(fixed)==12096 and set(fixed)=={j for j,x in enumerate(bits) if x} and all(x in (0.,1.) for x in fixed.values()),'Full prescribed bits')
    repair=vector(v,PRE/'repair_vector.npz',23016);need(all(float_bytes([repair[j]])==float_bytes([x]) for j,x in fixed.items()),'Stored states were altered')
    b=v.read_npz(PRE/'fixed_bounds.npz',('column_lower','column_upper'));lower=v.vector(b['column_lower'],('<f8',),m.cols,'fixed lower');upper=v.vector(b['column_upper'],('<f8',),m.cols,'fixed upper')
    need(all(lower[j]==upper[j]==fixed[j] if bits[j] else lower[j]==m.lower[j] and upper[j]==m.upper[j] for j in range(m.cols)),'Only state box fixing')
    RUN.mkdir();save(RUN/'execution_started.json',dict(utc=utc(),freeze_sha256=expected,maximum_optimizer_calls=1,cut_gate_count=2))
    ledger=dict(attempted=0,returned=0);stages=[];last=phase;h=None
    result=dict(verdict='UNKNOWN',original_common_question='UNKNOWN',accepted_common_witness=False,full_problem_negative_claim=False,requires_completed_within_phase=True)
    def checkpoint(stage,record=True,precall=True):
        nonlocal last
        now=time.perf_counter();remaining=PHASE-(now-phase)
        if record:stages.append(dict(stage=stage,elapsed_seconds=now-phase,stage_seconds=now-last,remaining_seconds=remaining));last=now
        if remaining<(GUARD if precall else 0):raise PhaseGuard(stage)
    try:
        checkpoint('prepared_archive_validated');gates=[]
        for world in WORLDS:
            cut=read(PRE/(world+'_cut.json'));validate_cut_schema(cut,world);gates.append(dict(world=world,**cut_value(cut,fixed)))
        save(RUN/'cut_gate.json',dict(evaluations=gates,optimizer_calls=0,no_reselection=True));checkpoint('two_fixed_cut_evaluations')
        need(not gates[1]['strictly_violated'],'Contradiction with accepted days321 individual point')
        if gates[0]['strictly_violated']:result.update(verdict='REJECTED_REPAIRED_SCHEDULE_ON_IDENTITY_BY_EXISTING_CUT',candidate_exact_negative=True)
        else:
            import numpy as np
            import highspy
            PRIVATE.mkdir(parents=True);h=highspy.Highs();build_readback(h,highspy,np,m,bits,fixed,lower,upper,checkpoint)
            checkpoint('precall_guard');save(RUN/'call_ready.json',dict(utc=utc(),not_actual_call=True))
            checkpoint('post_ready_write_guard');save(RUN/'call_started.json',dict(utc=utc(),dispatch_intent=True,optimizer_call_has_not_started=True))
            checkpoint('post_started_write_guard');ledger.update(attempted=1,started_utc=utc(),remaining_seconds=PHASE-(time.perf_counter()-phase));clock=time.perf_counter()
            try:status=h.run()
            finally:ledger['actual_seconds']=time.perf_counter()-clock
            ledger.update(returned=1,ended_utc=utc());sol=h.getSolution();info=h.getInfo()
            result.update(model_status=h.modelStatusToString(h.getModelStatus()),run_status=str(status),value_valid=bool(sol.value_valid),
                actual_seconds=ledger['actual_seconds'],soft_solver_overrun_seconds=max(0,ledger['actual_seconds']-60),simplex_iterations=int(info.simplex_iteration_count))
            save(RUN/'solver_returned.json',result);raw=np.array(sol.col_value,dtype=np.float64);np.savez_compressed(RUN/'raw_identity_solution.npz',vector=raw);checkpoint('solver_output_archived',precall=False)
            if sol.value_valid:
                checked=accepted_candidate(v,np,raw,fixed,checkpoint);result['candidate_eligible']=checked['eligible'];result['accepted_common_witness']=checked['accepted']
                result['verdict']='VERIFIED_EXPANDED_COMMON_COMMITMENT' if checked['accepted'] else 'UNKNOWN_REJECTED_RETURNED_POINT'
                if checked['accepted']:result['original_common_question']='FEASIBLE_IN_EXPANDED_MODEL'
        validate(bindings);validate(transport);checkpoint('final_hash_revalidation',precall=False)
    except PhaseGuard as exc:
        result.update(verdict='INCOMPLETE_PHASE_GUARD',guard_stage=str(exc),original_common_question='UNKNOWN',accepted_common_witness=False)
    except BaseException as exc:
        save(RUN/'execution_failure.json',dict(utc=utc(),error_type=type(exc).__name__,message=str(exc),call_ledger=ledger,scientific_verdict='UNKNOWN',no_retry=True));raise
    finally:
        save(RUN/'stage_timings.json',dict(stages=stages))
        if h is not None:h.clear()
        save(RUN/'private_log_receipt.json',dict(raw_logs_public=False,privacy_review='NOT_PERFORMED',files=[bind(p) for p in PRIVATE.glob('*.log')]))
    if time.perf_counter()-phase>PHASE:result.update(verdict='INCOMPLETE_PHASE_GUARD',guard_stage='closeout',original_common_question='UNKNOWN',accepted_common_witness=False)
    save(RUN/'result.json',result);elapsed=time.perf_counter()-phase
    save(RUN/'completion.json',dict(status='CLOSED_PENDING_INDEPENDENT_REVIEW' if elapsed<=PHASE else 'INCOMPLETE_PHASE_LIMIT',utc=utc(),call_ledger=ledger,optimizer_calls=ledger['attempted'],
        phase_seconds=elapsed,soft_phase_overrun_seconds=max(0,elapsed-PHASE),phase_limit_seconds=PHASE,candidates=1,no_retry_or_ray=True,
        all_inputs_unchanged=result['verdict']!='INCOMPLETE_PHASE_GUARD',nominal_feasibility_claim=False,final_completion_write_outside_sample=True))
    print(json.dumps(dict(verdict=result['verdict'],optimizer_calls=ledger['attempted'])),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--self-test',action='store_true');g.add_argument('--prepare-only',action='store_true');g.add_argument('--run-prepared',action='store_true');p.add_argument('--expected-freeze-sha256');args=p.parse_args()
    try:
        if args.self_test:self_test()
        elif args.prepare_only:prepare()
        else:need(args.expected_freeze_sha256 is not None,'Trusted freeze required');run(args.expected_freeze_sha256)
    except BaseException as exc:
        folder=RUN if RUN.exists() else PRE if PRE.exists() else ARM;folder.mkdir(parents=True,exist_ok=True)
        if not (folder/'failure.json').exists():save(folder/'failure.json',dict(utc=utc(),error_type=type(exc).__name__,message=str(exc),mode='self_test' if args.self_test else 'prepare' if args.prepare_only else 'run',no_retry=True,no_scientific_verdict=True))
        raise
