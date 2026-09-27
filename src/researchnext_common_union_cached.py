"""Cached-array transport repair for the single, already frozen union schedule."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
ARM=ROOT/'results/research_next/common_union_cached'; PRE=ARM/'prepared'; RUN=ARM/'run01'
PRIVATE=ROOT/'.work/researchnext_common_union_cached/run01'
OLD=ROOT/'results/research_next/common_union'; OLD_PRE=OLD/'prepared'
LEGACY=ROOT/'src/researchnext_common_union.py'
LEGACY_SHA='92089c0301bd6a7399728abdf0a9a8964bd570199bc2490ea22e947adfedc1a1'
PROTOCOL=ROOT/'docs/research_next/COMMON_UNION_CACHED_PROTOCOL.md'
PHASE=240.0; GUARD=65.0
OPTIONS=dict(time_limit=60.0,threads=1,random_seed=0,presolve='on',solver='simplex')
PINS={
 'prepared/prepared_freeze.json':'8d5e348d91db8ae082a1a036d2359ac382891b25849e9e682fb833e9ae52d0a2',
 'prepared/input_manifest.json':'1337e9674d15fc52023733b8c72b1140c20d01a472a287fd43a90cd5719d3a2d',
 'INDEPENDENT_PREPARED_REVIEW.json':'b7b856c9f7395a46e51569a13d844f53d7bb883bb97d8f76a627b0049cc2c05e',
 'PRECALL_INTERRUPTION.json':'8490bdd6e8de9eea9b3234d60eb65d79da1dd026f553d9e638af1a71cadce184',
 'PREBINDING_PERFORMANCE_PROBE.json':'23abb5eb3d0690727dfbc2cc7ef44cb16a44fe94578a5595675c7cb94af837b2',
 'FAILURE_CLOSURE.json':'8229435b98abd90414fde8d6cdb8c54c107cfbe3f0f0fb47e7e1ebb7523ceeb5',
}

def require(ok,message):
    if not ok:raise ValueError(message)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,value):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')
def utc():return datetime.now(timezone.utc).isoformat()
def bind(p,data=None):
    p=Path(p).resolve();data=p.read_bytes() if data is None else data
    return dict(path=str(p),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
def validate(items):
    require(len({x['path'].casefold() for x in items})==len(items),'Duplicate binding')
    for x in items:require(bind(x['path'])==x,'Changed bound bytes: '+x['path'])
def helper():
    require(sha(LEGACY)==LEGACY_SHA,'Legacy acceptance source changed')
    spec=importlib.util.spec_from_file_location('common_union_cached_pinned_acceptance',LEGACY)
    b=importlib.util.module_from_spec(spec);sys.modules[spec.name]=b;spec.loader.exec_module(b)
    # Only the unchanged candidate checker uses these explicit new archive paths.
    b.PRE=PRE;b.RUN=RUN;b.PRIVATE=PRIVATE
    require(b.OPTIONS==OPTIONS and b.PHASE_SECONDS==PHASE,'Inherited option contract changed')
    return b

def prepared_data(b):
    v=b.kernel();m=v.load_model(PRE/'joint');bits=b.mask(v,PRE/'joint',m.cols)
    require((m.rows,m.cols,len(m.data),sum(bits))==(69362,33936,291176,12096),'Original shape/mask')
    schedule=read(PRE/'candidate_schedule.json');fixed={x['column']:x['value'] for x in schedule['fixed_columns']}
    require(schedule['candidate_count']==1 and len(fixed)==12096 and set(fixed)=={j for j,x in enumerate(bits) if x},'Same complete candidate mask')
    require(all(x in (0,1) for x in fixed.values()),'Nonbinary prescribed state')
    raw=v.read_npz(PRE/'fixed_bounds.npz',('column_lower','column_upper'))
    lower=v.vector(raw['column_lower'],('<f8',),m.cols,'fixed lower');upper=v.vector(raw['column_upper'],('<f8',),m.cols,'fixed upper')
    require(all(lower[j]==upper[j]==fixed[j] if bits[j] else lower[j]==m.lower[j] and upper[j]==m.upper[j] for j in range(m.cols)),'Only inherited state boxes fixed')
    require(read(PRE/'candidate_admission.json')['admitted'],'Inherited candidate was not admitted')
    return v,m,bits,fixed,lower,upper

def prepare():
    require(not PRE.exists() and not RUN.exists(),'Fresh preparation only')
    b=helper();runtime=b.environment();captured={}
    def capture(p,expected=None):
        data=Path(p).read_bytes();item=bind(p,data)
        require(expected is None or item==expected,'Captured historical bytes mismatch')
        key=item['path'].casefold();require(key not in captured or captured[key][1]==item,'Conflicting captured bytes')
        captured[key]=(data,item);return data
    for rel,digest in PINS.items():
        data=capture(OLD/rel);require(hashlib.sha256(data).hexdigest()==digest,'Historical pin changed')
    manifest=json.loads(captured[str((OLD_PRE/'input_manifest.json').resolve()).casefold()][0])
    require(len(manifest['files'])==94,'Old frozen denominator changed')
    for item in manifest['files']:capture(item['path'],item)
    for p in (Path(__file__),PROTOCOL):capture(p)
    require(sha(LEGACY)==LEGACY_SHA,'Pinned acceptance changed')
    initial=[x[1] for x in captured.values()];PRE.mkdir(parents=True)
    save(PRE/'preparation_started.json',dict(utc=utc(),optimizer_calls=0,highspy_imports=0,union_recomputations=0))
    names=[f'joint/{n}' for n in b.JOINT_FILES]+[f'{w}/{n}' for w in ('identity','days_321') for n in b.WORLD_FILES]
    names+=['gen.csv','identity_input_vector.npz','day321_input_vector.npz','candidate_schedule.json','candidate_admission.json','fixed_bounds.npz']
    copies=[]
    for name in names:
        src=OLD_PRE/name;data,item=captured[str(src.resolve()).casefold()];dest=PRE/name
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
        require(bind(dest)['sha256']==item['sha256'],'Inherited byte copy differs')
        copies.append(dict(original=item,copy=bind(dest)))
    require(len(copies)==27,'Copy denominator')
    prepared_data(b) # Shape/fixing identity only; no union construction or dispatch test.
    save(PRE/'copy_provenance.json',dict(copies=copies,union_recomputations=0,new_scientific_candidates=0))
    save(PRE/'plan.json',dict(options=OPTIONS,phase_seconds=PHASE,start_guard_seconds=GUARD,runtime=runtime,
        scientific_candidates_total=1,new_scientific_candidates=0,planned_optimizer_calls=1,
        old_attempt_optimizer_calls=0,transport_repair='cache every backend sparse array once',
        same_original_acceptance_source_sha256=LEGACY_SHA,no_retry=True,no_ray=True))
    validate(initial);items=initial+[bind(p) for p in PRE.rglob('*') if p.is_file()];validate(items)
    save(PRE/'input_manifest.json',dict(files=items));validate(items)
    save(PRE/'prepared_freeze.json',dict(utc=utc(),source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),
        manifest_sha256=sha(PRE/'input_manifest.json'),bindings=len(items),copies=len(copies),optimizer_calls=0,
        source_prepared_review_and_explicit_execution_GO_required=True))

class PhaseGuard(Exception):pass

def extract_rows(matrix,rowwise,rows,cols,checkpoint):
    # Each pybind vector getter materializes a Python list. Read each exactly ONCE.
    start=tuple(matrix.start_);indices=tuple(matrix.index_);values=tuple(matrix.value_)
    require(len(indices)==len(values),'Sparse arrays differ')
    require(len(start)==(rows if rowwise else cols)+1 and start[0]==0 and start[-1]==len(values),'Sparse pointer shape')
    require(all(a<=b for a,b in zip(start,start[1:])),'Sparse pointer monotonicity')
    out=[[] for _ in range(rows)];checkpoint('sparse_arrays_materialized')
    if rowwise:
        for i in range(rows):
            out[i]=[(int(indices[k]),float(values[k])) for k in range(start[i],start[i+1])]
            if i%2048==0:checkpoint('readback_rows_progress',record=False)
    else:
        for j in range(cols):
            for k in range(start[j],start[j+1]):out[int(indices[k])].append((j,float(values[k])))
            if j%2048==0:checkpoint('readback_columns_progress',record=False)
    require(all(0<=j<cols for row in out for j,c in row),'Column coordinate range')
    checkpoint('sparse_rows_materialized');return out

def build_readback(highspy,np,h,m,bits,fixed,lower,upper,checkpoint):
    require(h.version()=='1.12.0','HiGHS version')
    for key,value in {**OPTIONS,'log_to_console':False,'log_file':str((PRIVATE/'solver.log').resolve())}.items():
        require(h.setOptionValue(key,value)==highspy.HighsStatus.kOk,'Rejected fixed option')
    lp=highspy.HighsLp();lp.num_row_,lp.num_col_=m.rows,m.cols
    lp.col_cost_=np.zeros(m.cols);lp.col_lower_=np.array(lower);lp.col_upper_=np.array(upper)
    lp.row_lower_=np.array(m.row_lower);lp.row_upper_=np.array(m.row_upper)
    lp.offset_=0.0;lp.sense_=highspy.ObjSense.kMinimize
    lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise;lp.a_matrix_.num_row_,lp.a_matrix_.num_col_=m.rows,m.cols
    lp.a_matrix_.start_=np.array(m.indptr,dtype=np.int32);lp.a_matrix_.index_=np.array(m.indices,dtype=np.int32);lp.a_matrix_.value_=np.array(m.data)
    lp.integrality_=[highspy.HighsVarType.kContinuous]*m.cols
    checkpoint('lp_object_assembled')
    require(h.passModel(lp)==highspy.HighsStatus.kOk,'Rejected fixed LP');checkpoint('backend_model_passed')
    got=h.getLp();require((got.num_row_,got.num_col_)==(m.rows,m.cols),'Backend dimensions')
    cl=tuple(got.col_lower_);cu=tuple(got.col_upper_);rl=tuple(got.row_lower_);ru=tuple(got.row_upper_)
    cost=tuple(got.col_cost_);integers=tuple(got.integrality_);offset=got.offset_;sense=got.sense_
    require((cl,cu,rl,ru)==(lower,upper,m.row_lower,m.row_upper),'Backend bounds')
    require(all(x==0 for x in cost) and offset==0 and sense==highspy.ObjSense.kMinimize,'Backend objective')
    require(not integers or all(x==highspy.HighsVarType.kContinuous for x in integers),'Free backend integer')
    matrix=got.a_matrix_;fmt=matrix.format_
    require(fmt in (highspy.MatrixFormat.kRowwise,highspy.MatrixFormat.kColwise),'Sparse format')
    entries=extract_rows(matrix,fmt==highspy.MatrixFormat.kRowwise,m.rows,m.cols,checkpoint)
    data=[];indices=[];indptr=[0]
    for i,row in enumerate(entries):
        row.sort();wanted=sorted(zip(m.indices[m.indptr[i]:m.indptr[i+1]],m.data[m.indptr[i]:m.indptr[i+1]]))
        require(row==wanted,'Backend coefficient mismatch')
        indices.extend(j for j,c in row);data.extend(c for j,c in row);indptr.append(len(data))
        if i%2048==0:checkpoint('coefficient_comparison_progress',record=False)
    checkpoint('full_backend_comparison')
    actual={}
    for key,value in OPTIONS.items():
        status,current=h.getOptionValue(key);require(status==highspy.HighsStatus.kOk and current==value,'Option changed');actual[key]=current
    np.savez_compressed(RUN/'backend_readback.npz',data=np.array(data),indices=np.array(indices,dtype=np.int64),
        indptr=np.array(indptr,dtype=np.int64),shape=np.array([m.rows,m.cols],dtype=np.int64),column_lower=np.array(cl),column_upper=np.array(cu),
        row_lower=np.array(rl),row_upper=np.array(ru),objective=np.array(cost),original_integrality=np.array(bits,dtype=np.uint8))
    save(RUN/'backend_readback.json',dict(original_rows=m.rows,columns=m.cols,coefficients=len(data),all_original_bits_fixed=len(fixed),
        unchanged_original_matrix=True,only_state_bounds_fixed=True,no_free_integer_variables=True,options=actual,
        sparse_array_materializations=dict(start=1,indices=1,values=1),readback_sha256=sha(RUN/'backend_readback.npz'),optimizer_calls=0))
    checkpoint('backend_readback_archived');return h

def run(expected):
    phase=time.perf_counter();require(not RUN.exists() and not PRIVATE.exists(),'Fresh run only')
    require(sha(PRE/'prepared_freeze.json')==expected,'External freeze digest')
    f=read(PRE/'prepared_freeze.json');require(f['source_sha256']==sha(__file__) and f['protocol_sha256']==sha(PROTOCOL),'Source/protocol changed')
    require(f['manifest_sha256']==sha(PRE/'input_manifest.json'),'Manifest changed')
    bindings=read(PRE/'input_manifest.json')['files'];validate(bindings)
    b=helper();plan=read(PRE/'plan.json');require(plan['runtime']==b.environment() and plan['options']==OPTIONS,'Runtime/options changed')
    v,m,bits,fixed,lower,upper=prepared_data(b);transport=[bind(PRE/'input_manifest.json'),bind(PRE/'prepared_freeze.json')]
    RUN.mkdir();PRIVATE.mkdir(parents=True);save(RUN/'execution_started.json',dict(utc=utc(),freeze_sha256=expected))
    stages=[];last=phase;ledger=dict(attempted=0,returned=0);h=None
    result=dict(verdict='UNKNOWN',accepted_common_witness=False,no_exact_negative_claim=True)
    def checkpoint(name,record=True):
        nonlocal last
        now=time.perf_counter();remaining=PHASE-(now-phase)
        if record:stages.append(dict(stage=name,elapsed_seconds=now-phase,stage_seconds=now-last,remaining_seconds=remaining));last=now
        if remaining<GUARD:raise PhaseGuard(name)
    try:
        checkpoint('validated_prepared_archive')
        import numpy as np
        import highspy
        checkpoint('imports')
        h=highspy.Highs()
        build_readback(highspy,np,h,m,bits,fixed,lower,upper,checkpoint)
        checkpoint('precall_admission');save(RUN/'call_ready.json',dict(utc=utc(),not_actual_call=True))
        checkpoint('post_ready_write_admission')
        ledger.update(attempted=1,started_utc=utc(),actual_call_remaining_seconds=PHASE-(time.perf_counter()-phase));clock=time.perf_counter()
        try:status=h.run()
        finally:ledger['actual_seconds']=time.perf_counter()-clock
        ledger.update(returned=1,ended_utc=utc());sol=h.getSolution();info=h.getInfo()
        result.update(model_status=h.modelStatusToString(h.getModelStatus()),run_status=str(status),value_valid=bool(sol.value_valid),
            actual_seconds=ledger['actual_seconds'],soft_overrun_seconds=max(0,ledger['actual_seconds']-60),simplex_iterations=int(info.simplex_iteration_count))
        save(RUN/'solver_returned.json',result);raw=np.array(sol.col_value,dtype=np.float64);np.savez_compressed(RUN/'raw_solution.npz',vector=raw)
        if sol.value_valid:
            checked=b.candidate_check(v,np,raw,bits,fixed)
            result['candidate_eligible']=checked['eligible'];result['accepted_common_witness']=checked['accepted']
            result['verdict']='VERIFIED_EXPANDED_COMMON_COMMITMENT' if checked['accepted'] else 'UNKNOWN_REJECTED_CANDIDATE'
    except PhaseGuard as exc:
        result.update(verdict='NOT_RUN_PRECALL_PHASE_GUARD',guard_stage=str(exc));require(ledger['attempted']==0,'Unexpected postcall guard')
    except BaseException as exc:
        save(RUN/'execution_failure.json',dict(utc=utc(),error_type=type(exc).__name__,ledger=ledger,scientific_verdict='UNKNOWN',no_retry=True))
        raise RuntimeError('Cached transport arm stopped; no retry') from None
    finally:
        save(RUN/'stage_timings.json',dict(stages=stages))
        if h is not None:h.clear()
        save(RUN/'private_log_receipt.json',dict(raw_logs_public=False,privacy_review='NOT_PERFORMED',files=[bind(p) for p in PRIVATE.glob('*.log')]))
    validate(bindings);validate(transport);save(RUN/'result.json',result);elapsed=time.perf_counter()-phase
    save(RUN/'completion.json',dict(utc=utc(),status='CLOSED_PENDING_INDEPENDENT_REVIEW',call_ledger=ledger,optimizer_calls=ledger['attempted'],
        phase_seconds=elapsed,soft_phase_overrun_seconds=max(0,elapsed-PHASE),all_inputs_unchanged=True,scientific_candidates_total=1,
        new_scientific_candidates=0,no_retry_or_ray=True,nominal_feasibility_claim=False,final_completion_write_outside_sample=True))
    print(json.dumps(dict(verdict=result['verdict'],calls=ledger['attempted'])),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--prepare-only',action='store_true');g.add_argument('--run-prepared',action='store_true');p.add_argument('--expected-freeze-sha256');a=p.parse_args()
    if a.prepare_only:prepare()
    else:require(a.expected_freeze_sha256 is not None,'External freeze required');run(a.expected_freeze_sha256)
