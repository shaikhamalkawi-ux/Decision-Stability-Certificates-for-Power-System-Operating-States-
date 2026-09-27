"""One separately gated Gurobi search on the original common-commitment model."""
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
ARM = ROOT/'results/research_next/common_gurobi'
PRE = ARM/'prepared'; RUN = ARM/'run01'
PRIVATE = ROOT/'.work/researchnext_common_gurobi/run01'
OLD = ROOT/'results/research_next/common_commitment'
ORIGINAL = OLD/'prepared'
PROTOCOL = ROOT/'docs/research_next/COMMON_GUROBI_PROTOCOL.md'
BASE = ROOT/'src/researchnext_common_commitment.py'
BASE_SHA = '039af59750b4c165d877b9878ac14af02a202700b46739ba96a8914075ae3284'
KERNEL = ROOT/'src/research8h_standalone_verify.py'
KERNEL_SHA = '708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'
PYTHON = ROOT/'.work/auer_projection_env/Scripts/python.exe'
TAU = Q.from_float(1e-5)
PHASE_SECONDS = 2400.0
OPTIONS = dict(TimeLimit=1800.0,Threads=1,Seed=0,MIPFocus=1,SolutionLimit=1,
               MIPGap=1e-8,Presolve=-1,FeasibilityTol=1e-8,IntFeasTol=1e-9)
PACKAGES = {'gurobipy':'13.0.0','numpy':'2.5.3','scipy':'1.18.1'}
PINS = {
 'results/research_next/common_commitment/prepared/prepared_freeze.json':'4f21891d7d1f1793dd92e5b830edf5b5cf62474e5521d788c9aec17929ea9a59',
 'results/research_next/common_commitment/prepared/input_manifest.json':'8ff99b1f4450ac15e91b26a261a85c98d574bbbdac3f7fe149efd9fd07204a5c',
 'results/research_next/common_commitment/run01/completion.json':'f1933f3029955eaf7256206228c272060c8c48df69fff91af7baa06ce2a4f9d7',
 'results/research_next/common_commitment/run01/outcomes.json':'0e85f3d65e5375f384b0a1015178de4babb03b5ebd5392ee0c6f759e6c43776c',
 'results/research_next/common_commitment/INDEPENDENT_PREPARED_REVIEW.json':'956b37cbcdd49571a6a79611da197a5be840a5c2747ffbd60576c90805d58e6b',
 'results/research_next/common_commitment/INDEPENDENT_POSTRUN_REVIEW.json':'f442edeb3f90c5d602a1b60cdef1b96b4d560ebbe97fae28c4ca21c6077eadba',
 'results/research_next/common_diving/run01/result.json':'d8ec206535457068e3bf88437bde71676f88a7ff055ca4c4713ed0dc1230adf1',
 'results/research_next/auer_projection_preflight/isolated_environment.json':'431af4e6f9a8a8e10a30f3f690551084b43d84b18b56b761594e9be1123e5366',
 'results/research_next/auer_projection_preflight/synthetic_license_probe.json':'5ef5d25e22f8117a9b7ac5c3508b18b8960b142efacdc72f67749b596715e009',
 'results/research_next/auer_projection_preflight/probe_completion.json':'78356593844606bf71d9deaf9d6163c0e1fc820816d1737488eda2f8a974a00d',
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
def kernel(): return module(KERNEL,KERNEL_SHA,'common_gurobi_npz_kernel')
def mask(v,folder,cols):
    return tuple(v.vector(v.read_npz(folder/'integrality.npz',('integrality',))['integrality'],('|u1',),cols,'full original mask'))
def environment():
    require(Path(sys.executable).resolve()==PYTHON.resolve(),'Use existing isolated Gurobi interpreter')
    versions={n:importlib.metadata.version(n) for n in PACKAGES}
    require(versions==PACKAGES and sys.version_info[:3]==(3,12,14),'Recorded backend environment differs')
    return dict(python=sys.version,executable=sys.executable,packages=versions,
                large_model_license_capacity='UNKNOWN; prior successful calls used small models only',
                license_values_read=False,gurobi_imported_for_preparation=False)

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
         calls=1,objective='zero feasibility',full_original_binaries=12096,numeric_proposal='nominal original model',
         acceptance='original uniformly expanded joint and both world models plus native checks',runtime=runtime,
         no_warm_start=True,no_lp=True,no_ray=True,no_iis=True,no_retry=True,no_install_or_license_change=True,
         source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL)))
    validate(initial);all_items=initial+[bind(p) for p in PRE.rglob('*') if p.is_file()];validate(all_items)
    save(PRE/'input_manifest.json',dict(files=all_items));validate(all_items)
    save(PRE/'prepared_freeze.json',dict(utc=utc(),source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),
         manifest_sha256=sha(PRE/'input_manifest.json'),bindings=len(all_items),original_rows=m.rows,columns=m.cols,
         binary_columns=sum(bits),backend_rows=len(rows),optimizer_calls=0,gurobi_imports=0,
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

def build_and_readback(gp,np,env,m,bits,rows):
    h=gp.Model('original_common_commitment',env=env)
    for key,value in OPTIONS.items():h.setParam(key,value)
    h.setParam('LogToConsole',0);h.setParam('LogFile',str((PRIVATE/'solver.log').resolve()));h.setParam('OutputFlag',1)
    variables=[h.addVar(lb=m.lower[j],ub=m.upper[j],obj=0.0,vtype=gp.GRB.BINARY if bits[j] else gp.GRB.CONTINUOUS,name=f'x{j}') for j in range(m.cols)]
    h.ModelSense=gp.GRB.MINIMIZE;h.ObjCon=0.0;h.update()
    constraints=[]
    for k,row in enumerate(rows):
        i=row['original_row'];a,b=m.indptr[i:i+2]
        lhs=gp.LinExpr(list(m.data[a:b]),[variables[j] for j in m.indices[a:b]])
        constraints.append(h.addLConstr(lhs,row['sense'],float.fromhex(row['rhs_hex']),name=f'r{k}_o{i}_{row["side"]}'))
    h.update()
    require(h.NumVars==m.cols and h.NumConstrs==len(rows) and h.NumBinVars==sum(bits),'Backend dimensions/types')
    require(h.NumQConstrs==h.NumGenConstrs==h.NumSOS==0 and h.ModelSense==gp.GRB.MINIMIZE and h.ObjCon==0,'Unexpected model features')
    lower=h.getAttr('LB',variables);upper=h.getAttr('UB',variables);objective=h.getAttr('Obj',variables);types=h.getAttr('VType',variables)
    require(tuple(lower)==m.lower and tuple(upper)==m.upper and all(c==0 for c in objective),'Backend column bounds/objective changed')
    require(types==[gp.GRB.BINARY if b else gp.GRB.CONTINUOUS for b in bits],'Original binary declaration changed')
    require([x.index for x in variables]==list(range(m.cols)) and h.NumStart==0,'Coordinate order or warm start changed')
    data=[];indices=[];indptr=[0];rhs=[];senses=[]
    for k,(row,c) in enumerate(zip(rows,constraints)):
        i=row['original_row'];expr=h.getRow(c)
        actual=sorted((expr.getVar(j).index,expr.getCoeff(j)) for j in range(expr.size()))
        wanted=sorted(zip(m.indices[m.indptr[i]:m.indptr[i+1]],m.data[m.indptr[i]:m.indptr[i+1]]))
        require(actual==wanted and expr.getConstant()==0,'Backend row coefficients changed')
        require(c.Sense==row['sense'] and c.RHS==float.fromhex(row['rhs_hex']),'Backend row endpoint changed')
        indices.extend(j for j,a in actual);data.extend(a for j,a in actual);indptr.append(len(data));rhs.append(c.RHS);senses.append(c.Sense)
    actual_options={k:h.getParamInfo(k)[2] for k in OPTIONS};require(actual_options==OPTIONS,'Backend options differ')
    np.savez_compressed(RUN/'backend_readback.npz',data=np.array(data),indices=np.array(indices,dtype=np.int64),
        indptr=np.array(indptr,dtype=np.int64),shape=np.array([len(rows),m.cols],dtype=np.int64),
        rhs=np.array(rhs),sense=np.array(senses,dtype='S1'),column_lower=np.array(lower),column_upper=np.array(upper),
        objective=np.array(objective),integrality=np.array(bits,dtype=np.uint8))
    save(RUN/'backend_readback.json',dict(all_rows_columns_objective_exact=True,original_rows=m.rows,
         backend_rows=len(rows),columns=m.cols,binaries=sum(bits),coefficient_uses=len(data),no_extra_variables=True,
         options=actual_options,backend_readback_sha256=sha(RUN/'backend_readback.npz'),optimizer_calls=0))
    return h,variables

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
    base=module(BASE,BASE_SHA,'common_gurobi_native_checker');require(base.TAU==TAU,'Native tolerance changed')
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
    phase=time.perf_counter();require(not RUN.exists() and not PRIVATE.exists(),'One execution only; private logs also fresh')
    v,m,bits,rows,bindings=load_prepared(expected);transport=[bind(PRE/'input_manifest.json'),bind(PRE/'prepared_freeze.json')]
    RUN.mkdir();PRIVATE.mkdir(parents=True)
    save(RUN/'execution_started.json',dict(utc=utc(),expected_freeze_sha256=expected,source_sha256=sha(__file__),private_logs=str(PRIVATE.relative_to(ROOT))))
    ledger=dict(attempted=0,returned=0);result=dict(verdict='UNKNOWN',accepted_common_witness=False,no_exact_negative_claim=True)
    stage='imports';h=env=None
    try:
        with (PRIVATE/'startup.log').open('x',encoding='utf-8') as private_stream, redirect_stdout(private_stream), redirect_stderr(private_stream):
            import numpy as np
            import gurobipy as gp
            require(gp.gurobi.version()==(13,0,0),'Actual solver version differs')
            stage='existing_license_environment_start'
            env=gp.Env(empty=True);env.setParam('OutputFlag',0);env.start()
        stage='original_model_construction_and_exact_readback'
        h,variables=build_and_readback(gp,np,env,m,bits,rows)
        remaining=PHASE_SECONDS-(time.perf_counter()-phase)
        save(RUN/'admission.json',dict(utc=utc(),remaining_seconds=remaining,required_seconds=1805.0,admitted=remaining>=1805))
        if remaining<1805:result['verdict']='NOT_RUN_PHASE_GUARD'
        else:
            save(RUN/'call_ready.json',dict(utc=utc(),not_actual_start=True))
            actual_remaining=PHASE_SECONDS-(time.perf_counter()-phase);ledger['last_admission_remaining_seconds']=actual_remaining
            if actual_remaining<1805:result['verdict']='NOT_RUN_POST_WRITE_PHASE_GUARD'
            else:
                stage='sole_optimize';ledger.update(attempted=1,started_utc=utc());clock=time.perf_counter()
                try:h.optimize()
                finally:ledger['actual_seconds']=time.perf_counter()-clock
                ledger.update(returned=1,ended_utc=utc());stage='returned_solution_archive'
                result.update(solver_version='13.0.0',status_code=int(h.Status),solution_count=int(h.SolCount),
                              actual_seconds=ledger['actual_seconds'],soft_overrun_seconds=max(0,ledger['actual_seconds']-1800),
                              solver_runtime=float(h.Runtime),node_count=float(h.NodeCount),iteration_count=float(h.IterCount),options=OPTIONS)
                save(RUN/'solver_returned.json',result)
                if h.SolCount>0:
                    raw=np.array(h.getAttr('X',variables),dtype=np.float64);np.savez_compressed(RUN/'raw_solution.npz',vector=raw)
                    stage='unchanged_original_exact_acceptance';checked=candidate_check(v,np,raw,bits)
                    result['candidate_eligible']=checked['eligible'];result['accepted_common_witness']=checked['accepted']
                    if checked['accepted']:result['verdict']='VERIFIED_EXPANDED_COMMON_COMMITMENT'
                    else:result['verdict']='UNKNOWN_REJECTED_CANDIDATE'
        stage='close';validate(bindings);validate(transport);save(RUN/'result.json',result)
        elapsed=time.perf_counter()-phase
        save(RUN/'completion.json',dict(utc=utc(),status='CLOSED_PENDING_INDEPENDENT_REVIEW',call_ledger=ledger,
             planned_calls=1,optimizer_calls=ledger['attempted'],phase_seconds=elapsed,phase_soft_overrun=max(0,elapsed-PHASE_SECONDS),
             all_frozen_bytes_unchanged=True,no_retries=True,no_lp_ray_iis_or_diving=True,no_warm_start=True,
             nominal_feasibility_claim=False,final_completion_write_outside_sample=True))
        print(json.dumps(dict(verdict=result['verdict'],calls=ledger['attempted'])),flush=True)
    except BaseException as exc:
        # Do not archive licence identifiers, credentials or private exception strings.
        save(RUN/'execution_failure.json',dict(utc=utc(),stage=stage,error_type=type(exc).__name__,
             backend_errno=getattr(exc,'errno',None),call_ledger=ledger,scientific_verdict='UNKNOWN',
             partial_outputs_preserved=True,automatic_retry=False,license_values_recorded=False))
        raise RuntimeError('Common Gurobi execution stopped; preserved stage/type/code and call ledger; no automatic retry') from None
    finally:
        if h is not None:h.dispose()
        if env is not None:env.dispose()
        # Raw backend/startup text remains private until a separate disclosure review.
        logs=[]
        for p in sorted(PRIVATE.glob('*.log')):
            b=p.read_bytes();logs.append(dict(path=p.relative_to(ROOT).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
        save(RUN/'private_log_receipt.json',dict(raw_logs_public=False,content_privacy_review='NOT_PERFORMED',files=logs))

def fixtures():
    # No arrays, imports, models or solvers: just the new row-endpoint encoding.
    rows=row_encoding((2.,-math.inf,1.,-3.),(2.,4.,math.inf,5.))
    require([(x['original_row'],x['sense']) for x in rows]==[(0,'='),(1,'<'),(2,'>'),(3,'>'),(3,'<')],'Endpoint fixture')
    require([float.fromhex(x['rhs_hex']) for x in rows]==[2.,4.,1.,-3.,5.],'Endpoint values')
    for a in (-4.,-3.,0.,5.,6.):
        require((-3<=a<=5)==(a>=-3 and a<=5),'Two-sided interval equivalence')
    ARM.mkdir(parents=True,exist_ok=True)
    save(ARM/'source_fixtures.json',dict(status='PASS_INVENTED_ONLY',source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),
         checks=['equality_once','upper_only','lower_only','two_finite_sides','exact_endpoint_hex_roundtrip','two_sided_logical_equivalence'],
         scientific_reads=0,gurobi_imports=0,model_preparations=0,optimizer_calls=0))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--source-fixtures',action='store_true');g.add_argument('--prepare-only',action='store_true');g.add_argument('--run-prepared',action='store_true')
    p.add_argument('--expected-freeze-sha256');a=p.parse_args()
    if a.source_fixtures:fixtures()
    elif a.prepare_only:prepare()
    else:require(a.expected_freeze_sha256 is not None,'External freeze digest required');run(a.expected_freeze_sha256)
