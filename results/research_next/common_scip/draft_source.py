"""Source drafting only; copies reviewed acceptance text without executing it."""
from pathlib import Path
import ast
import hashlib
ROOT=Path(__file__).resolve().parents[3]
old=ROOT/'src/researchnext_common_gurobi.py'
assert hashlib.sha256(old.read_bytes()).hexdigest()=='9f5515fb99ac43cba3756f1e2b5a9f3a0ad9df7c143860922edd9ae99cd000ec'
s=old.read_text(encoding='utf-8')
prefix=s[:s.index('def build_and_readback(')]
prefix=prefix.replace('One separately gated Gurobi search','One separately gated numerical SCIP search')
prefix=prefix.replace('common_gurobi','common_scip').replace('COMMON_GUROBI','COMMON_SCIP')
prefix=prefix.replace("ROOT/'.work/auer_projection_env/Scripts/python.exe'","ROOT/'.work/scip_capability_env01/Scripts/python.exe'")
a=prefix.index('OPTIONS =');b=prefix.index('PINS =',a)
prefix=prefix[:a]+'''OPTIONS = {'limits/time':1800.0,'limits/solutions':1,'parallel/maxnthreads':1,
           'lp/threads':1,'randomization/randomseedshift':0,'randomization/permutationseed':0,
           'randomization/lpseed':0,'numerics/feastol':1e-8}
PACKAGES = {'pyscipopt':'6.2.1','numpy':'2.3.5'}
'''+prefix[b:]
prefix='\n'.join(line for line in prefix.split('\n') if "'results/research_next/auer_projection_preflight/" not in line)
pos=prefix.index('\n}\nWORLD_FILES')
prefix=prefix[:pos]+'''
 'results/research_next/scip_capability/setup01/capability.json':'c21670a55e870f5abef24efb74d52b2de17d9e235a82eec0da0bfd7a4e74ebed',
 'results/research_next/scip_capability/setup01/completion.json':'bee14a2cbbf2536071c32a738f496baa0cd36a2ebbf6fc0e7347867ecee49c80',
 'results/research_next/scip_capability/setup01/installed_payload_hashes.json':'a188acdf861190c3f77fc1122ab9bb08cf9ac1594d164c0daeb033e6e11ffe33',
 'results/research_next/scip_capability/setup01/downloaded_wheels.json':'b7c19b9f3e63d72c68b8b8489185d62b2ba46642bfa306cf864b57d33b1ee9f9',
 '.work/scip_capability_env01/Lib/site-packages/pyscipopt/scip.pxi':'e6abd57d0f19a30c30d0c1c603e2b69ec890af4b6b3c94aaf44d289bb43efb16',
 '.work/scip_capability_env01/Lib/site-packages/pyscipopt/scip.pyi':'8d44bb57b11ffb5688433b9f32ba1450c0c35c2e8787822ed12a09f29a559aa4',
 'results/research_next/common_gurobi/run01/failure_closure.json':'22401b45326159af3aec4821f9b970ec90ad65db326be35c5661b62108443209',
'''+prefix[pos:]
a=prefix.index('def environment():');b=prefix.index('\ndef row_encoding(',a)
prefix=prefix[:a]+'''def environment():
    require(Path(sys.executable).resolve()==PYTHON.resolve(),'Use existing isolated SCIP interpreter')
    versions={n:importlib.metadata.version(n) for n in PACKAGES}
    require(versions==PACKAGES and sys.version_info[:3]==(3,12,14),'Recorded backend environment differs')
    return dict(python=sys.version,executable=sys.executable,packages=versions,
                capability='empty-model import/version only; no exact/proof parameters',
                scip_imported_for_preparation=False)
'''+prefix[b:]
needle="    for p in (Path(__file__),PROTOCOL):"
prefix=prefix.replace(needle,'''    installed_path=ROOT/'results/research_next/scip_capability/setup01/installed_payload_hashes.json'
    installed=json.loads(captured[str(installed_path.resolve()).casefold()][0])['files']
    for item in installed:
        p=ROOT/item['path'];b=p.read_bytes()
        require(len(b)==item['bytes'] and hashlib.sha256(b).hexdigest()==item['sha256'],'Installed backend payload changed')
        captured[str(p.resolve()).casefold()]=(b,bind(p,b))
'''+needle)
prefix=prefix.replace("calls=1,objective='zero feasibility'","calls=1,emphasis='SCIP_PARAMEMPHASIS.FEASIBILITY before explicit options; record full parameter diff',objective='zero feasibility'")
prefix=prefix.replace('no_install_or_license_change=True','no_install_or_license_change=True,numerical_backend_only=True')
prefix=prefix.replace('gurobi_imports=0','scip_imports=0')
candidate=s[s.index('def candidate_check('):s.index('\ndef run(',s.index('def candidate_check('))]
candidate=candidate.replace('common_gurobi_native_checker','common_scip_native_checker')
builder='''def build_and_readback(scip,np,m,bits,rows):
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

'''
runner='''def run(expected):
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
                stage='sole_optimize';ledger.update(attempted=1,started_utc=utc())
                save(RUN/'optimize_invocation_started.json',dict(ledger=ledger,invocation_not_successful_search_guarantee=True))
                actual_remaining=PHASE_SECONDS-(time.perf_counter()-phase)
                if actual_remaining<1805:
                    ledger['attempted']=0;result['verdict']='NOT_RUN_FINAL_WRITE_PHASE_GUARD'
                else:
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
'''
out=ROOT/'src/researchnext_common_scip.py'
assert not out.exists()
text=prefix+builder+candidate+runner
ast.parse(text)
out.write_text(text,encoding='utf-8',newline='\n')
print(hashlib.sha256(out.read_bytes()).hexdigest())
