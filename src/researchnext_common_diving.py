"""One post-hoc LP-guided common-commitment neighborhood; separate prepare/run gates."""
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
import sys
import time

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
ARM=ROOT/'results/research_next/common_diving'
PRE=ARM/'prepared';RUN=ARM/'run01'
OLD=ROOT/'results/research_next/common_commitment'
ORIGINAL=OLD/'prepared'
PROTOCOL=ROOT/'docs/research_next/COMMON_DIVING_PROTOCOL.md'
BASE=ROOT/'src/researchnext_common_commitment.py'
BASE_SHA='039af59750b4c165d877b9878ac14af02a202700b46739ba96a8914075ae3284'
KERNEL=ROOT/'src/research8h_standalone_verify.py'
KERNEL_SHA='708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'
LP_POINT=OLD/'run01/lp/raw_solution.npz'
ANCHORS={
 'prepared/prepared_freeze.json':'4f21891d7d1f1793dd92e5b830edf5b5cf62474e5521d788c9aec17929ea9a59',
 'prepared/input_manifest.json':'8ff99b1f4450ac15e91b26a261a85c98d574bbbdac3f7fe149efd9fd07204a5c',
 'producer_output_inventory.csv':'06bba03dc70aa221695ad82d717c975fd25946fbb9cf931371b4c8442f54eea6',
 'run01/outcomes.json':'0e85f3d65e5375f384b0a1015178de4babb03b5ebd5392ee0c6f759e6c43776c',
 'run01/completion.json':'f1933f3029955eaf7256206228c272060c8c48df69fff91af7baa06ce2a4f9d7',
 'run01/lp/raw_solution.npz':'90c8b308a6ce8e7671adbe3059887d6ce27489fa3d68aa601c2474b32d2d462a',
 'INDEPENDENT_PREPARED_REVIEW.json':'956b37cbcdd49571a6a79611da197a5be840a5c2747ffbd60576c90805d58e6b',
 'INDEPENDENT_POSTRUN_REVIEW.py':'4835a83777f5f14ad606aaf2f6bb18c1365820bb21d23fc350388907b92b1acf',
 'INDEPENDENT_POSTRUN_REVIEW.json':'f442edeb3f90c5d602a1b60cdef1b96b4d560ebbe97fae28c4ca21c6077eadba',
 'INDEPENDENT_LP_NONBINARY_STATES.json':'bc371fa53ae5f94d3f1536eefc526871b60d4de2f7bae4b027a088d9d2ba4282',
}
TAU=Q.from_float(1e-5)
PHASE_SECONDS=300.0
OPTIONS={'time_limit':120.0,'threads':1,'random_seed':0,'presolve':'on','mip_rel_gap':1e-8}

def require(ok,message):
    if not ok:raise ValueError(message)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def utc():return datetime.now(timezone.utc).isoformat()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def save(path,value):
    with Path(path).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')
def rat(value):return {'numerator':str(value.numerator),'denominator':str(value.denominator),'approximate':float(value)}
def binding(path):
    path=Path(path).resolve();data=path.read_bytes()
    return {'path':str(path),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
def validate(items):
    require(len({r['path'].casefold() for r in items})==len(items),'Duplicate binding')
    for r in items:require(binding(r['path'])==r,'Changed bound file '+r['path'])
def module(path,expected,name):
    require(sha(path)==expected,'Pinned helper changed')
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
    return m
def kernel():return module(KERNEL,KERNEL_SHA,'common_diving_stdlib_kernel')
def mask(v,folder,columns):
    return tuple(v.vector(v.read_npz(folder/'integrality.npz',('integrality',))['integrality'],('|u1',),columns,'original full binary mask'))

def fixing_decision(value,tau=TAU):
    require(type(value) is Q and Q(0)<=tau<Q(1,2),'Exact fixing inputs')
    eligible=[bit for bit in (0,1) if abs(value-bit)<=tau]
    require(len(eligible)<=1,'Ambiguous near-bit choice')
    return eligible[0] if eligible else None

def input_bindings():
    for rel,digest in ANCHORS.items():require(sha(OLD/rel)==digest,'Historical anchor changed '+rel)
    require(sha(BASE)==BASE_SHA and sha(KERNEL)==KERNEL_SHA,'Reviewed helper identity')
    items=read(ORIGINAL/'input_manifest.json')['files'];require(len(items)==48,'Original prepared denominator')
    validate(items)
    selected={r['path'].casefold():r for r in items}
    for path in [Path(__file__),PROTOCOL]+[OLD/rel for rel in ANCHORS]:
        b=binding(path);key=b['path'].casefold()
        require(key not in selected or selected[key]==b,'Conflicting input binding')
        selected[key]=b
    result=list(selected.values());validate(result);return result

def prepare():
    require(not PRE.exists() and not RUN.exists(),'Fresh preparation only')
    initial=input_bindings();v=kernel()
    reviewed=read(OLD/'INDEPENDENT_POSTRUN_REVIEW.json')
    require(reviewed['pair_binary_verdict']=='UNKNOWN' and reviewed['posthoc_continuous_check']['expanded_pass'],'Closed parent result scope')
    original=v.load_model(ORIGINAL/'joint');bits=mask(v,ORIGINAL/'joint',original.cols)
    require((original.rows,original.cols,sum(bits))==(69362,33936,12096),'Original model identity')
    require(bits==tuple(int(6888<=j<18984) for j in range(original.cols)),'Complete original U/Y/Z declarations')
    arrays=v.read_npz(LP_POINT,('vector','row_value','row_dual','col_dual'))
    vector=v.vector(arrays['vector'],('<f8',),original.cols,'unrounded archived LP vector')
    require(all(math.isfinite(x) for x in vector),'Finite input point')
    lower=list(original.lower);upper=list(original.upper);fixed=[];free=[]
    for j,flag in enumerate(bits):
        if not flag:continue
        x=Q(vector[j]);bit=fixing_decision(x)
        item={'column':j,'lp_value_hex':vector[j].hex(),'exact_lp_value':rat(x),'nearest_bit_distance':rat(min(abs(x),abs(x-1)))}
        if bit is None:free.append(item)
        else:
            require(Q(original.lower[j])<=bit<=Q(original.upper[j]),'Chosen bit outside original box')
            lower[j]=upper[j]=float(bit);fixed.append({**item,'fixed_bit':bit})
    require((len(fixed),len(free))==(11836,260),'Frozen parent fixing counts changed; do not adapt')
    require(len(fixed)+len(free)==sum(bits),'Complete state partition')
    restricted=v.validate_model(v.Model(original.rows,original.cols,original.data,original.indices,original.indptr,
        tuple(lower),tuple(upper),original.row_lower,original.row_upper))
    import numpy as np
    PRE.mkdir(parents=True)
    save(PRE/'preparation_started.json',{'utc':utc(),'source_sha256':sha(__file__),'protocol_sha256':sha(PROTOCOL),'optimizer_calls':0})
    for name in ('matrix.npz','integrality.npz'):
        source=ORIGINAL/'joint'/name;data=source.read_bytes()
        r=next(r for r in initial if r['path'].casefold()==str(source.resolve()).casefold())
        require(len(data)==r['bytes'] and hashlib.sha256(data).hexdigest()==r['sha256'],'Copy from initial captured binding')
        (PRE/name).write_bytes(data)
    np.savez_compressed(PRE/'bounds.npz',column_lower=np.array(lower),column_upper=np.array(upper),
        row_lower=np.array(original.row_lower),row_upper=np.array(original.row_upper))
    require(v.load_model(PRE)==restricted and mask(v,PRE,original.cols)==bits,'Serialized restricted model differs')
    require(sha(PRE/'matrix.npz')==sha(ORIGINAL/'joint/matrix.npz') and sha(PRE/'integrality.npz')==sha(ORIGINAL/'joint/integrality.npz'),'Rows/mask copied unchanged')
    save(PRE/'restriction.json',{'posthoc':True,'rule':'Fix to unique bit iff exact distance <= Fraction.from_float(1e-5); otherwise leave free.',
        'tau':rat(TAU),'lp_point_sha256':sha(LP_POINT),'fixed_count':len(fixed),'free_count':len(free),'fixed':fixed,'free':free,
        'original_binary_declarations':sum(bits),'original_model':str(ORIGINAL/'joint'),'no_continuous_column_restrictions':True})
    save(PRE/'plan.json',{'options':OPTIONS,'phase_seconds':PHASE_SECONDS,'planned_calls':1,'call_kind':'mip',
        'no_lp':True,'no_warm_start':True,'no_alternate_neighborhood':True,'no_retries':True,
        'objective':'zero feasibility','numerical_model':'nominal original joint plus declared exact bit fixings',
        'acceptance':'expanded original joint and both original world models, exact common binary bits and supplementary native checks',
        'python':sys.version,'executable':sys.executable,'packages':{n:importlib.metadata.version(n) for n in ('numpy','highspy')},
        'source_sha256':sha(__file__),'protocol_sha256':sha(PROTOCOL)})
    validate(initial)
    generated=[binding(p) for p in PRE.rglob('*') if p.is_file()]
    all_items=initial+generated;validate(all_items)
    save(PRE/'input_manifest.json',{'files':all_items})
    validate(all_items)
    save(PRE/'prepared_freeze.json',{'utc':utc(),'source_sha256':sha(__file__),'protocol_sha256':sha(PROTOCOL),
        'manifest_sha256':sha(PRE/'input_manifest.json'),'bindings':len(all_items),'rows':original.rows,'columns':original.cols,
        'original_binaries':sum(bits),'fixed_binaries':11836,'free_binaries':260,'optimizer_calls':0,
        'separate_independent_prepared_gate_and_explicit_GO_required':True})

def load_prepared(expected):
    require(sha(PRE/'prepared_freeze.json')==expected,'External freeze digest')
    freeze=read(PRE/'prepared_freeze.json')
    require(freeze['source_sha256']==sha(__file__) and freeze['protocol_sha256']==sha(PROTOCOL),'Frozen source/protocol')
    require(freeze['manifest_sha256']==sha(PRE/'input_manifest.json'),'Frozen manifest')
    bindings=read(PRE/'input_manifest.json')['files'];validate(bindings)
    plan=read(PRE/'plan.json');require(plan['options']==OPTIONS and plan['planned_calls']==1 and plan['phase_seconds']==PHASE_SECONDS,'Plan identity')
    v=kernel();m=v.load_model(PRE);bits=mask(v,PRE,m.cols)
    require((m.rows,m.cols,sum(bits))==(69362,33936,12096),'Restricted shape and full integer mask')
    restriction=read(PRE/'restriction.json');require(restriction['fixed_count']==11836 and restriction['free_count']==260,'Restriction identity')
    return v,m,bits,restriction,bindings

def check_candidate(v,raw,bits,restriction,np):
    candidate=raw.copy();eligibility=[]
    for j,flag in enumerate(bits):
        if not flag:continue
        bit=fixing_decision(Q(float(raw[j])))
        if bit is None:return {'eligible':False,'accepted_common_witness':False}
        eligibility.append((j,bit));candidate[j]=float(bit)
    require(all(candidate[j]==entry['fixed_bit'] for entry in restriction['fixed'] for j in (entry['column'],)),'Recovered fixed coordinate changed')
    private=np.array([not b for b in bits],dtype=bool)
    require(candidate[private].tobytes()==raw[private].tobytes(),'Continuous candidate changed')
    np.savez_compressed(RUN/'candidate_vector.npz',vector=candidate)
    joint=v.load_model(ORIGINAL/'joint');joint_check=v.check_point(joint,candidate.tolist(),bits,TAU)
    restricted_check=v.check_point(v.load_model(PRE),candidate.tolist(),bits,TAU)
    maps=read(ORIGINAL/'joint/column_maps.json')['original_to_joint'];worlds=[];states=[]
    # Reuse only the hash-pinned prior supplementary checker; never call its solve/merge/run functions.
    base=module(BASE,BASE_SHA,'common_diving_native_checks');require(base.TAU==TAU,'Native tolerance contract')
    for world,mapping in zip(('identity','days_321'),maps):
        folder=ORIGINAL/world;model=v.load_model(folder);original_bits=mask(v,folder,model.cols)
        point=[float(candidate[j]) for j in mapping]
        np.savez_compressed(RUN/(world+'_vector.npz'),vector=np.array(point))
        exact=v.check_point(model,point,original_bits,TAU)
        native=base.native_check(v,point,folder,read(folder/'model_metadata.json'),read(folder/'native_spec.json'))
        worlds.append({'world':world,'original':exact,'native':native});states.append([Q(point[j]) for j,b in enumerate(original_bits) if b])
    common=states[0]==states[1] and len(states[0])==12096 and all(s in (0,1) for s in states[0])
    accepted=common and restricted_check['expanded_pass'] and joint_check['expanded_pass'] and all(w['original']['expanded_pass'] and w['native']['expanded_pass'] for w in worlds)
    result={'eligible':True,'accepted_common_witness':accepted,'joint_original':joint_check,'restricted_model':restricted_check,
        'worlds':worlds,'common_all12096_bits':common,'continuous_bytes_unchanged':True,'fixed_bits_exact':True,'nominal_feasibility_claim':False}
    save(RUN/'exact_candidate_checks.json',result);return result

def run(expected):
    phase=time.perf_counter();require(not RUN.exists(),'Only one execution of this frozen neighborhood')
    v,model,bits,restriction,bindings=load_prepared(expected)
    transport=[binding(PRE/'input_manifest.json'),binding(PRE/'prepared_freeze.json')]
    RUN.mkdir();save(RUN/'execution_started.json',{'utc':utc(),'expected_freeze_sha256':expected,'source_sha256':sha(__file__),'phase_seconds':PHASE_SECONDS})
    ledger={'attempted':0,'returned':0};result={'verdict':'UNKNOWN','accepted_common_witness':False,'neighborhood_failure_is_not_full_infeasibility':True}
    try:
        import numpy as np
        import highspy
        h=highspy.Highs();options={**OPTIONS,'log_to_console':False,'log_file':str((RUN/'solver.log').resolve())}
        for key,value in options.items():require(h.setOptionValue(key,value)==highspy.HighsStatus.kOk,'Rejected option')
        lp=highspy.HighsLp();lp.num_row_,lp.num_col_=model.rows,model.cols
        lp.col_cost_=np.zeros(model.cols);lp.col_lower_=np.array(model.lower);lp.col_upper_=np.array(model.upper)
        lp.row_lower_=np.array(model.row_lower);lp.row_upper_=np.array(model.row_upper)
        lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise;lp.a_matrix_.num_row_,lp.a_matrix_.num_col_=model.rows,model.cols
        lp.a_matrix_.start_=np.array(model.indptr,dtype=np.int32);lp.a_matrix_.index_=np.array(model.indices,dtype=np.int32);lp.a_matrix_.value_=np.array(model.data)
        lp.integrality_=[highspy.HighsVarType.kInteger if b else highspy.HighsVarType.kContinuous for b in bits]
        require(h.passModel(lp)==highspy.HighsStatus.kOk,'Rejected restricted model')
        remaining=PHASE_SECONDS-(time.perf_counter()-phase);needed=OPTIONS['time_limit']+5
        save(RUN/'admission.json',{'utc':utc(),'remaining_seconds':remaining,'required_seconds':needed,'admitted':remaining>=needed})
        if remaining<needed:result['verdict']='NOT_RUN_PHASE_GUARD'
        else:
            save(RUN/'call_ready.json',{'utc':utc(),'not_an_assertion_of_actual_call':True})
            actual_remaining=PHASE_SECONDS-(time.perf_counter()-phase)
            ledger['last_admission_remaining_seconds']=actual_remaining
            if actual_remaining<needed:result['verdict']='NOT_RUN_POST_WRITE_PHASE_GUARD'
            else:
                ledger.update(attempted=1,started_utc=utc());clock=time.perf_counter()
                try:status=h.run()
                finally:ledger['actual_seconds']=time.perf_counter()-clock
                ledger.update(returned=1,ended_utc=utc())
                solution=h.getSolution();info=h.getInfo()
                result.update(options=options,solver_version=h.version(),run_status=str(status),model_status=h.modelStatusToString(h.getModelStatus()),
                    value_valid=bool(solution.value_valid),dual_valid=bool(solution.dual_valid),mip_node_count=int(info.mip_node_count),
                    actual_seconds=ledger['actual_seconds'],soft_overrun_seconds=max(0,ledger['actual_seconds']-OPTIONS['time_limit']))
                save(RUN/'solver_returned.json',result)
                raw=np.array(solution.col_value,dtype=np.float64)
                np.savez_compressed(RUN/'raw_solution.npz',vector=raw)
                if solution.value_valid and raw.shape==(model.cols,) and np.isfinite(raw).all():
                    checks=check_candidate(v,raw,bits,restriction,np);result['candidate_eligible']=checks['eligible']
                    result['accepted_common_witness']=checks['accepted_common_witness']
                    if checks['accepted_common_witness']:result['verdict']='VERIFIED_EXPANDED_COMMON_COMMITMENT'
                    elif checks['eligible']:result['verdict']='UNKNOWN_REJECTED_CANDIDATE'
        validate(bindings);validate(transport)
        save(RUN/'result.json',result)
        elapsed=time.perf_counter()-phase
        save(RUN/'completion.json',{'utc':utc(),'status':'CLOSED_PENDING_INDEPENDENT_REVIEW','call_ledger':ledger,'planned_calls':1,
            'optimizer_calls':ledger['attempted'],'phase_seconds':elapsed,'phase_soft_overrun':max(0,elapsed-PHASE_SECONDS),
            'all_frozen_bytes_unchanged':True,'no_added_lp_or_ray_getter':True,'no_alternative_neighborhood_or_retry':True,
            'posthoc':True,'parent_initial_run_unchanged':True,'nominal_feasibility_claim':False})
        print(json.dumps({'verdict':result['verdict'],'calls':ledger['attempted']}))
    except BaseException as exc:
        save(RUN/'execution_failure.json',{'utc':utc(),'error_type':type(exc).__name__,'message':str(exc),'call_ledger':ledger,
            'partial_outputs_preserved':True,'automatic_retry':False})
        raise

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True);mode.add_argument('--prepare-only',action='store_true');mode.add_argument('--run-prepared',action='store_true')
    parser.add_argument('--expected-freeze-sha256');args=parser.parse_args()
    if args.prepare_only:prepare()
    else:
        require(args.expected_freeze_sha256 is not None,'Trusted prepared digest required');run(args.expected_freeze_sha256)
