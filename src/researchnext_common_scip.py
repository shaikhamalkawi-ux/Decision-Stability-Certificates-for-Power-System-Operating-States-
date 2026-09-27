"""One separately gated numerical SCIP search on the original common-commitment model."""
from __future__ import annotations
import argparse
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import importlib.metadata
import importlib.util
import json
import math
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
ARM = ROOT/'results/research_next/common_scip'
PRE = ARM/'prepared'; RUN = ARM/'run01'
PRIVATE = ROOT/'.work/researchnext_common_scip/run01'
OLD = ROOT/'results/research_next/common_commitment'
ORIGINAL = OLD/'prepared'
PROTOCOL = ROOT/'docs/research_next/COMMON_SCIP_PROTOCOL.md'
BASE = ROOT/'src/researchnext_common_commitment.py'
BASE_SHA = '039af59750b4c165d877b9878ac14af02a202700b46739ba96a8914075ae3284'
KERNEL = ROOT/'src/research8h_standalone_verify.py'
KERNEL_SHA = '708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'
PYTHON = ROOT/'.work/scip_capability_env01/Scripts/python.exe'
TAU = Q.from_float(1e-5)
PHASE_SECONDS = 2400.0
OPTIONS = {'limits/time':1800.0,'limits/solutions':1,'parallel/maxnthreads':1,
           'lp/threads':1,'randomization/randomseedshift':0,'randomization/permutationseed':0,
           'randomization/lpseed':0,'numerics/feastol':1e-8}
PACKAGES = {'pyscipopt':'6.2.1','numpy':'2.3.5'}
PINS = {
 'results/research_next/common_commitment/prepared/prepared_freeze.json':'4f21891d7d1f1793dd92e5b830edf5b5cf62474e5521d788c9aec17929ea9a59',
 'results/research_next/common_commitment/prepared/input_manifest.json':'8ff99b1f4450ac15e91b26a261a85c98d574bbbdac3f7fe149efd9fd07204a5c',
 'results/research_next/common_commitment/run01/completion.json':'f1933f3029955eaf7256206228c272060c8c48df69fff91af7baa06ce2a4f9d7',
 'results/research_next/common_commitment/run01/outcomes.json':'0e85f3d65e5375f384b0a1015178de4babb03b5ebd5392ee0c6f759e6c43776c',
 'results/research_next/common_commitment/INDEPENDENT_PREPARED_REVIEW.json':'956b37cbcdd49571a6a79611da197a5be840a5c2747ffbd60576c90805d58e6b',
 'results/research_next/common_commitment/INDEPENDENT_POSTRUN_REVIEW.json':'f442edeb3f90c5d602a1b60cdef1b96b4d560ebbe97fae28c4ca21c6077eadba',
 'results/research_next/common_diving/run01/result.json':'d8ec206535457068e3bf88437bde71676f88a7ff055ca4c4713ed0dc1230adf1',
 'results/research_next/scip_capability/setup01/capability.json':'c21670a55e870f5abef24efb74d52b2de17d9e235a82eec0da0bfd7a4e74ebed',
 'results/research_next/scip_capability/setup01/completion.json':'bee14a2cbbf2536071c32a738f496baa0cd36a2ebbf6fc0e7347867ecee49c80',
 'results/research_next/scip_capability/setup01/installed_payload_hashes.json':'a188acdf861190c3f77fc1122ab9bb08cf9ac1594d164c0daeb033e6e11ffe33',
 'results/research_next/scip_capability/setup01/downloaded_wheels.json':'b7c19b9f3e63d72c68b8b8489185d62b2ba46642bfa306cf864b57d33b1ee9f9',
 '.work/scip_capability_env01/Lib/site-packages/pyscipopt/scip.pxi':'e6abd57d0f19a30c30d0c1c603e2b69ec890af4b6b3c94aaf44d289bb43efb16',
 '.work/scip_capability_env01/Lib/site-packages/pyscipopt/scip.pyi':'8d44bb57b11ffb5688433b9f32ba1450c0c35c2e8787822ed12a09f29a559aa4',
 'results/research_next/common_gurobi/run01/failure_closure.json':'22401b45326159af3aec4821f9b970ec90ad65db326be35c5661b62108443209',

}
WORLD_FILES = ('matrix.npz','bounds.npz','integrality.npz','model_metadata.json',
               'native_inputs.npz','permutation.csv','row_metadata.csv.gz','native_spec.json')
JOINT_FILES = ('matrix.npz','bounds.npz','integrality.npz','column_maps.json','row_origins.json')

def require(ok, message):
    if not ok: raise ValueError(message)
def utc(): return datetime.now(timezone.utc).isoformat()
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def save(path,value):
    with Path(path).open('x',encoding='utf-8') as f: json.dump(value,f,indent=2,allow_nan=False);f.write('\n')
def bind(path,data=None):
    path=Path(path).resolve();data=path.read_bytes() if data is None else data
    return dict(path=str(path),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
def validate(items):
    require(len({x['path'].casefold() for x in items})==len(items),'Duplicate binding')
    for item in items: require(bind(item['path'])==item,'Changed frozen input: '+item['path'])
def module(path,digest,name):
    require(sha(path)==digest,'Pinned helper changed')
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s)
    sys.modules[name]=m;s.loader.exec_module(m);return m
def kernel(): return module(KERNEL,KERNEL_SHA,'common_scip_npz_kernel')
def mask(v,folder,cols):
    return tuple(v.vector(v.read_npz(folder/'integrality.npz',('integrality',))['integrality'],('|u1',),cols,'full original mask'))
def environment():
    require(Path(sys.executable).resolve()==PYTHON.resolve(),'Use existing isolated SCIP interpreter')
    versions={n:importlib.metadata.version(n) for n in PACKAGES}
    require(versions==PACKAGES and sys.version_info[:3]==(3,12,14),'Recorded backend environment differs')
    return dict(python=sys.version,executable=sys.executable,packages=versions,
                capability='empty-model import/version only; no exact/proof parameters',
                scip_imported_for_preparation=False)

def row_encoding(lower,upper):
    """No auxiliaries: each equality once, otherwise each finite side directly."""
    require(len(lower)==len(upper),'Row interval sizes')
    result=[]
    for i,(lo,hi) in enumerate(zip(lower,upper)):
        require(not math.isnan(lo) and not math.isnan(hi) and lo<=hi,'Invalid interval')
        if math.isfinite(lo) and lo==hi: result.append(dict(original_row=i,sense='=',rhs_hex=lo.hex(),side='equality'))
        else:
            if math.isfinite(lo):result.append(dict(original_row=i,sense='>',rhs_hex=lo.hex(),side='lower'))
            if math.isfinite(hi):result.append(dict(original_row=i,sense='<',rhs_hex=hi.hex(),side='upper'))
        require(math.isfinite(lo) or math.isfinite(hi),'Unexpected fully unbounded scientific row')
    return result

def initial_inputs():
    captured={}
    for rel,digest in PINS.items():
        p=ROOT/rel;b=p.read_bytes();require(hashlib.sha256(b).hexdigest()==digest,'Historical pin changed: '+rel)
        captured[str(p.resolve()).casefold()]=(b,bind(p,b))
    old=json.loads(captured[str((ORIGINAL/'input_manifest.json').resolve()).casefold()][0])['files']
    require(len(old)==48,'Original denominator')
    for item in old:
        p=Path(item['path']);b=p.read_bytes();require(bind(p,b)==item,'Original captured bytes changed')
        key=str(p.resolve()).casefold();require(key not in captured or captured[key][1]==item,'Conflicting binding')
        captured[key]=(b,item)
    installed_path=ROOT/'results/research_next/scip_capability/setup01/installed_payload_hashes.json'
    installed=json.loads(captured[str(installed_path.resolve()).casefold()][0])['files']
    for item in installed:
        p=ROOT/item['path'];b=p.read_bytes()
        require(len(b)==item['bytes'] and hashlib.sha256(b).hexdigest()==item['sha256'],'Installed backend payload changed')
        captured[str(p.resolve()).casefold()]=(b,bind(p,b))
    for p in (Path(__file__),PROTOCOL):
        b=p.read_bytes();captured[str(p.resolve()).casefold()]=(b,bind(p,b))
    require(sha(BASE)==BASE_SHA and sha(KERNEL)==KERNEL_SHA,'Helper identity')
    return captured

def prepare():
    require(not PRE.exists() and not RUN.exists(),'Fresh preparation only')
    runtime=environment();captured=initial_inputs();initial=[x[1] for x in captured.values()];v=kernel()
    PRE.mkdir(parents=True)
    save(PRE/'preparation_started.json',dict(utc=utc(),source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),optimizer_calls=0))
    copied=[]
    for folder,names in [('joint',JOINT_FILES),('identity',WORLD_FILES),('days_321',WORLD_FILES)]:
        (PRE/folder).mkdir()
        for name in names:
            src=ORIGINAL/folder/name;key=str(src.resolve()).casefold()
            require(key in captured,'Missing original snapshot binding')
            data,item=captured[key];dest=PRE/folder/name;dest.write_bytes(data)
            require(bind(dest)['sha256']==item['sha256'],'Copied bytes differ')
            copied.append(dict(original=item,copy=bind(dest)))
    src=ORIGINAL/'gen.csv';data,item=captured[str(src.resolve()).casefold()]
    (PRE/'gen.csv').write_bytes(data);copied.append(dict(original=item,copy=bind(PRE/'gen.csv')))
    m=v.load_model(PRE/'joint');bits=mask(v,PRE/'joint',m.cols)
    require((m.rows,m.cols,len(m.data),sum(bits))==(69362,33936,291176,12096),'Original joint shape')
    require(bits==tuple(int(6888<=j<18984) for j in range(m.cols)),'Full U/Y/Z declaration')
    require(all((not b) or (0<=m.lower[j]<=m.upper[j]<=1) for j,b in enumerate(bits)),'Binary boxes')
    require(all(abs(x)<1e20 for x in (*m.lower,*m.upper,*m.data) if math.isfinite(x)),'Backend finite encoding range')
    require(all(abs(x)<1e20 for x in (*m.row_lower,*m.row_upper) if math.isfinite(x)),'Backend finite endpoint range')
    rows=row_encoding(m.row_lower,m.row_upper)
    save(PRE/'backend_rows.json',dict(rows=rows,no_auxiliary_variables=True,original_rows=m.rows,backend_rows=len(rows)))
    save(PRE/'copy_provenance.json',dict(copies=copied,all_original_models_unmodified=True,no_diving_restrictions=True))
    save(PRE/'plan.json',dict(options=OPTIONS,phase_seconds=PHASE_SECONDS,start_guard_seconds=1805.0,
         calls=1,emphasis='SCIP_PARAMEMPHASIS.FEASIBILITY before explicit options; record full parameter diff',objective='zero feasibility',full_original_binaries=12096,numeric_proposal='nominal original model',
         acceptance='original uniformly expanded joint and both world models plus native checks',runtime=runtime,
         no_warm_start=True,no_lp=True,no_ray=True,no_iis=True,no_retry=True,no_install_or_license_change=True,numerical_backend_only=True,
         source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL)))
    validate(initial);all_items=initial+[bind(p) for p in PRE.rglob('*') if p.is_file()];validate(all_items)
    save(PRE/'input_manifest.json',dict(files=all_items));validate(all_items)
    save(PRE/'prepared_freeze.json',dict(utc=utc(),source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),
         manifest_sha256=sha(PRE/'input_manifest.json'),bindings=len(all_items),original_rows=m.rows,columns=m.cols,
         binary_columns=sum(bits),backend_rows=len(rows),optimizer_calls=0,scip_imports=0,
         separate_prepared_gate_and_explicit_execution_GO_required=True))

def load_prepared(expected):
    require(sha(PRE/'prepared_freeze.json')==expected,'External freeze digest')
    f=read(PRE/'prepared_freeze.json');require(f['source_sha256']==sha(__file__) and f['protocol_sha256']==sha(PROTOCOL),'Source/protocol changed')
    require(f['manifest_sha256']==sha(PRE/'input_manifest.json'),'Manifest changed')
    bindings=read(PRE/'input_manifest.json')['files'];validate(bindings)
    p=read(PRE/'plan.json');require(p['options']==OPTIONS and p['phase_seconds']==PHASE_SECONDS and p['calls']==1,'Plan identity')
    require(p['runtime']==environment(),'Environment changed')
    v=kernel();m=v.load_model(PRE/'joint');bits=mask(v,PRE/'joint',m.cols)
    require((m.rows,m.cols,sum(bits))==(69362,33936,12096),'Original model identity')
    rows=read(PRE/'backend_rows.json')['rows'];require(rows==row_encoding(m.row_lower,m.row_upper),'Backend endpoint map changed')
    return v,m,bits,rows,bindings

def build_and_readback(scip,np,m,bits,rows):
    h=scip.Model('original_common_commitment_scip');h.hideOutput()
    h.setLogfile(str((PRIVATE/'solver.log').resolve()))
    require([h.getMajorVersion(),h.getMinorVersion(),h.getTechVersion()]==[10,0,2],'SCIP version changed')
    before=h.getParams()
    require('exact/enable' not in before and 'certificate/filename' not in before,'Capability differs')
    h.setEmphasis(scip.SCIP_PARAMEMPHASIS.FEASIBILITY,quiet=True)
    for key,value in OPTIONS.items():h.setParam(key,value)
    after=h.getParams();require(all(after[k]==v for k,v in OPTIONS.items()),'Explicit options differ')
    changes={k:dict(before=before[k],after=after[k]) for k in before if before[k]!=after[k]}
    require(set(before)==set(after),'Parameter registry changed')
    save(RUN/'parameters.json',dict(defaults=before,after_setters=after,changed=changes,
         explicit=OPTIONS,emphasis='FEASIBILITY',changed_count=len(changes)))
    variables=[h.addVar(name=f'x{j}',lb=m.lower[j],ub=m.upper[j],obj=0.0,vtype='B' if bits[j] else 'C') for j in range(m.cols)]
    h.setMinimize();constraints=[]
    for k,row in enumerate(rows):
        i=row['original_row'];a,b=m.indptr[i:i+2]
        expr=scip.quicksum(float(m.data[t])*variables[m.indices[t]] for t in range(a,b))
        rhs=float.fromhex(row['rhs_hex'])
        cons=(expr==rhs) if row['sense']=='=' else ((expr>=rhs) if row['sense']=='>' else (expr<=rhs))
        constraints.append(h.addCons(cons,name=f'r{k}'))
    require(h.getStageName()=='PROBLEM','Unexpected model transformation')
    actual_vars=h.getVars(transformed=False);actual_cons=h.getConss(transformed=False)
    require(len(actual_vars)==m.cols and {x.name for x in actual_vars}=={f'x{j}' for j in range(m.cols)},'Column coordinate set changed')
    require(len(actual_cons)==len(rows) and {c.name for c in actual_cons}=={f'r{k}' for k in range(len(rows))},'Constraint coordinate set changed')
    lower=[x.getLbOriginal() for x in variables];upper=[x.getUbOriginal() for x in variables]
    objective=[x.getObj() for x in variables];types=[x.vtype() for x in variables]
    require(tuple(lower)==m.lower and tuple(upper)==m.upper and all(x==0 for x in objective),'Original boxes/objective changed')
    require(types==['BINARY' if b else 'CONTINUOUS' for b in bits] and all(x.isOriginal() for x in variables),'Original full mask changed')
    require(h.getObjoffset(original=True)==0 and h.getObjectiveSense()=='minimize' and h.getNSols()==0,'Objective/warm start differs')
    infinity=h.infinity();data=[];indices=[];indptr=[0];rhs_values=[];senses=[]
    for k,(row,c) in enumerate(zip(rows,constraints)):
        require(c.isOriginal(),'Non-original row before optimization')
        actual_dict=h.getValsLinear(c)
        require(all(name.startswith('x') and name[1:].isdigit() and name==f'x{int(name[1:])}' for name in actual_dict),'Unknown column name')
        actual=sorted((int(name[1:]),value) for name,value in actual_dict.items())
        i=row['original_row'];wanted=sorted(zip(m.indices[m.indptr[i]:m.indptr[i+1]],m.data[m.indptr[i]:m.indptr[i+1]]))
        require(actual==wanted,'Original coefficient readback differs')
        rhs=float.fromhex(row['rhs_hex']);lo=h.getLhs(c);hi=h.getRhs(c)
        expected=(rhs,rhs) if row['sense']=='=' else ((rhs,infinity) if row['sense']=='>' else (-infinity,rhs))
        require((lo,hi)==expected,'Original row endpoint readback differs')
        indices.extend(j for j,a in actual);data.extend(a for j,a in actual);indptr.append(len(data));rhs_values.append(rhs);senses.append(row['sense'])
    require(h.getParams()==after,'Parameters changed during construction')
    np.savez_compressed(RUN/'backend_readback.npz',data=np.array(data),indices=np.array(indices,dtype=np.int64),
        indptr=np.array(indptr,dtype=np.int64),shape=np.array([len(rows),m.cols],dtype=np.int64),
        rhs=np.array(rhs_values),sense=np.array(senses,dtype='S1'),column_lower=np.array(lower),column_upper=np.array(upper),
        objective=np.array(objective),integrality=np.array(bits,dtype=np.uint8))
    save(RUN/'backend_coordinate_order.json',dict(variable_names=[x.name for x in actual_vars],constraint_names=[c.name for c in actual_cons],
         saved_vector_order='created variable handles x0 through x33935, regardless of backend order'))
    save(RUN/'backend_readback.json',dict(all_rows_columns_objective_exact=True,original_rows=m.rows,backend_rows=len(rows),
         columns=m.cols,binaries=sum(bits),coefficient_uses=len(data),no_extra_variables=True,stage='PROBLEM',
         readback_sha256=sha(RUN/'backend_readback.npz'),parameters_sha256=sha(RUN/'parameters.json'),optimizer_calls=0))
    return h,variables,after

def candidate_check(v,np,raw,bits):
    if raw.shape!=(len(bits),) or not np.isfinite(raw).all():return dict(eligible=False,accepted=False)
    candidate=raw.copy()
    for j,b in enumerate(bits):
        if not b:continue
        choices=[k for k in (0,1) if abs(Q(float(raw[j]))-k)<=TAU]
        if len(choices)!=1:return dict(eligible=False,accepted=False)
        candidate[j]=float(choices[0])
    private=np.array([not b for b in bits],dtype=bool)
    require(raw[private].tobytes()==candidate[private].tobytes(),'Continuous point changed')
    np.savez_compressed(RUN/'candidate_vector.npz',vector=candidate)
    joint=v.check_point(v.load_model(PRE/'joint'),candidate.tolist(),bits,TAU)
    maps=read(PRE/'joint/column_maps.json')['original_to_joint'];worlds=[];states=[]
    base=module(BASE,BASE_SHA,'common_scip_native_checker');require(base.TAU==TAU,'Native tolerance changed')
    for world,mapping in zip(('identity','days_321'),maps):
        folder=PRE/world;m=v.load_model(folder);wb=mask(v,folder,m.cols);point=[float(candidate[j]) for j in mapping]
        require(sum(wb)==12096,'Original world binary mask')
        np.savez_compressed(RUN/(world+'_vector.npz'),vector=np.array(point))
        exact=v.check_point(m,point,wb,TAU)
        native=base.native_check(v,point,folder,read(folder/'model_metadata.json'),read(folder/'native_spec.json'))
        worlds.append(dict(world=world,original=exact,native=native));states.append([Q(point[j]) for j,b in enumerate(wb) if b])
    common=len(states[0])==12096 and states[0]==states[1] and all(x in (0,1) for x in states[0])
    accepted=common and joint['expanded_pass'] and all(w['original']['expanded_pass'] and w['native']['expanded_pass'] for w in worlds)
    result=dict(eligible=True,accepted=accepted,joint=joint,worlds=worlds,common_all12096_bits=common,
                continuous_bytes_unchanged=True,nominal_feasibility_claim=False)
    save(RUN/'exact_candidate_checks.json',result);return result
def run(expected):
    phase=time.perf_counter();require(not RUN.exists() and not PRIVATE.exists(),'One fresh execution only')
    v,m,bits,rows,bindings=load_prepared(expected);transport=[bind(PRE/'input_manifest.json'),bind(PRE/'prepared_freeze.json')]
    RUN.mkdir();PRIVATE.mkdir(parents=True)
    save(RUN/'execution_started.json',dict(utc=utc(),expected_freeze_sha256=expected,source_sha256=sha(__file__)))
    ledger=dict(attempted=0,returned=0);result=dict(verdict='UNKNOWN',accepted_common_witness=False,no_exact_negative_claim=True)
    stage='imports';h=None
    try:
        with (PRIVATE/'startup.log').open('x',encoding='utf-8') as stream,redirect_stdout(stream),redirect_stderr(stream):
            import numpy as np
            import pyscipopt as scip
        stage='original_model_construction_and_exact_readback'
        h,variables,parameters=build_and_readback(scip,np,m,bits,rows)
        remaining=PHASE_SECONDS-(time.perf_counter()-phase)
        save(RUN/'admission.json',dict(utc=utc(),remaining_seconds=remaining,required_seconds=1805.0,admitted=remaining>=1805))
        if remaining<1805:result['verdict']='NOT_RUN_PHASE_GUARD'
        else:
            save(RUN/'call_ready.json',dict(utc=utc(),not_actual_start=True))
            actual_remaining=PHASE_SECONDS-(time.perf_counter()-phase);ledger['last_admission_remaining_seconds']=actual_remaining
            if actual_remaining<1805:result['verdict']='NOT_RUN_POST_WRITE_PHASE_GUARD'
            else:
                require(h.getParams()==parameters,'Pre-call parameters changed')
                stage='final_admission_write'
                save(RUN/'optimize_invocation_ready.json',dict(utc=utc(),not_an_actual_call=True))
                actual_remaining=PHASE_SECONDS-(time.perf_counter()-phase)
                if actual_remaining<1805:
                    result['verdict']='NOT_RUN_FINAL_WRITE_PHASE_GUARD'
                else:
                    stage='sole_optimize';ledger.update(attempted=1,started_utc=utc())
                    ledger['actual_call_remaining_seconds']=actual_remaining;clock=time.perf_counter()
                    try:h.optimize()
                    finally:ledger['actual_seconds']=time.perf_counter()-clock
                    ledger.update(returned=1,ended_utc=utc());stage='returned_solution_archive'
                    result.update(solver_version='10.0.2',status=str(h.getStatus()),solution_count=int(h.getNSols()),
                        actual_seconds=ledger['actual_seconds'],soft_overrun_seconds=max(0,ledger['actual_seconds']-1800),
                        solver_runtime=float(h.getSolvingTime()),node_count=int(h.getNNodes()),lp_iterations=int(h.getNLPIterations()),options=OPTIONS)
                    save(RUN/'solver_returned.json',result)
                    save(RUN/'parameters_after_call.json',dict(parameters=h.getParams()))
                    if h.getNSols()>0:
                        sol=h.getBestSol();require(sol is not None,'Solution count without point')
                        raw=np.array([h.getSolVal(sol,x) for x in variables],dtype=np.float64)
                        np.savez_compressed(RUN/'raw_solution.npz',vector=raw)
                        stage='unchanged_original_exact_acceptance';checked=candidate_check(v,np,raw,bits)
                        result['candidate_eligible']=checked['eligible'];result['accepted_common_witness']=checked['accepted']
                        result['verdict']='VERIFIED_EXPANDED_COMMON_COMMITMENT' if checked['accepted'] else 'UNKNOWN_REJECTED_CANDIDATE'
        stage='close';validate(bindings);validate(transport);save(RUN/'result.json',result)
        elapsed=time.perf_counter()-phase
        save(RUN/'completion.json',dict(utc=utc(),status='CLOSED_PENDING_INDEPENDENT_REVIEW',call_ledger=ledger,
            planned_calls=1,optimizer_calls=ledger['attempted'],phase_seconds=elapsed,phase_soft_overrun=max(0,elapsed-PHASE_SECONDS),
            all_frozen_bytes_unchanged=True,no_retries=True,no_lp_ray_iis_or_diving=True,no_warm_start=True,
            nominal_feasibility_claim=False,final_write_cleanup_receipt_outside_sample=True))
        print(json.dumps(dict(verdict=result['verdict'],calls=ledger['attempted'])),flush=True)
    except BaseException as exc:
        save(RUN/'execution_failure.json',dict(utc=utc(),stage=stage,error_type=type(exc).__name__,call_ledger=ledger,
            scientific_verdict='UNKNOWN',partial_outputs_preserved=True,automatic_retry=False))
        raise RuntimeError('Common SCIP stopped; preserved stage/type/call ledger; no automatic retry') from None
    finally:
        if h is not None:h.freeProb()
        save(RUN/'private_log_receipt.json',dict(raw_logs_public=False,privacy_review='NOT_PERFORMED',
            files=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(PRIVATE.glob('*.log'))]))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--prepare-only',action='store_true');g.add_argument('--run-prepared',action='store_true')
    p.add_argument('--expected-freeze-sha256');a=p.parse_args()
    if a.prepare_only:prepare()
    else:require(a.expected_freeze_sha256 is not None,'External freeze digest required');run(a.expected_freeze_sha256)
