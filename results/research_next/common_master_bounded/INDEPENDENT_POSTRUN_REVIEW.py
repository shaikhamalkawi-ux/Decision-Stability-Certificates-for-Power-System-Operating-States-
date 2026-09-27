"""Closed saved-master/readback/recourse audit; no solver or producer import."""
import csv,gzip,hashlib,importlib.util,json,math,sys,time
from datetime import datetime,timezone
from fractions import Fraction as F
from pathlib import Path
sys.dont_write_bytecode=True
ARM=Path(__file__).resolve().parent;ROOT=ARM.parents[2];PRE=ARM/'prepared';RUN=ARM/'run01';LP=RUN/'lp'
TAU=F.from_float(1e-5);NB=12096;START=6888;STOP=18984;NC=12432;H=168
PINS={PRE/'prepared_freeze.json':'75e9e276c356290129c85fefa9fdc5fb36f175174efb5b2e131bb96fdbef80d5',
 PRE/'input_manifest.json':'7bc0949abcd5aebb0d7ce4f2e68a3efa1105e9d1e25e54fd429dc04f4b33a19d',
 ARM/'producer_output_inventory.csv':'a7201af2fc77e7a556c5b0fc2ee0634f812808f0e4f092b64656baf24d668428',
 RUN/'completion.json':'3488a998b8d01cf279cddb20c9f6e22f04afd1ff3fdaf2d98260909c2d395883',
 RUN/'master_exact_admission.json':'983c62c4aaec8969ecc02ee774a55aa1fe2b95edf74d884dbae6f69e28b5a87a',
 ROOT/'src/research8h_standalone_verify.py':'708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f',
 ARM/'INDEPENDENT_PREPARED_REVIEW.json':'e7f4856d6778234c10a0372adad13be472912fc9176d1436d6db381feb7b2018'}
def need(x,label):
    if not x:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def gz(p):
    with gzip.open(p,'rt',encoding='utf-8') as f:return json.load(f)
def frac(x):return F(int(x[0]),int(x[1]))
def scalar(x):return None if x is None else frac(x['exact'])
def binding(e):
    b=Path(e['path']).read_bytes();need(len(b)==e['bytes'] and hashlib.sha256(b).hexdigest()==e['sha256'],'Bound file '+e['path'])
def main():
    start=time.perf_counter();out=ARM/'INDEPENDENT_POSTRUN_REVIEW.json';need(not out.exists(),'One independent replay')
    for p,h in PINS.items():need(sha(p)==h,'Trusted closure/input pin')
    manifest=read(PRE/'input_manifest.json');need(len(manifest['files'])==239,'239 frozen bindings')
    for e in manifest['files']:binding(e)
    with (ARM/'producer_output_inventory.csv').open(encoding='utf-8-sig',newline='') as f:inventory=list(csv.DictReader(f))
    need(len(inventory)==25 and len({x['path'] for x in inventory})==25,'25 unique public outputs')
    outputs=[dict(path=str(ROOT/x['path']),bytes=int(x['bytes']),sha256=x['sha256']) for x in inventory]
    for e in outputs:binding(e)
    expected_run={str((ROOT/x['path']).relative_to(RUN)) for x in inventory if (ROOT/x['path']).is_relative_to(RUN)}
    need(len(expected_run)==23 and {str(p.relative_to(RUN)) for p in RUN.rglob('*') if p.is_file()}==expected_run,'Complete unchanged run-file denominator')
    k=ROOT/'src/research8h_standalone_verify.py';s=importlib.util.spec_from_file_location('master_postrun_npz',k);v=importlib.util.module_from_spec(s);sys.modules[s.name]=v;s.loader.exec_module(v)
    master=gz(PRE/'master.json.gz');premises=read(PRE/'premises.json');plan=read(PRE/'plan.json')
    need(len(master['rows'])==17212 and len(master['boxes'])==NC and master['binary_columns']==NB,'Prepared master denominator')
    backend=gz(RUN/'master_backend_readback.json.gz')
    need(backend['nominal_numeric_search_only'] is True and backend['all_actual_numeric_coefficients_read_back'] is True and backend['exact_rational_master_sha256']==sha(PRE/'master.json.gz'),'Search readback scope')
    need(len(backend['boxes'])==NC,'Every numeric backend box')
    for j,(got,want) in enumerate(zip(backend['boxes'],master['boxes'])):
        need(got['lower_hex']==want['lower']['binary64_hex'] and got['upper_hex']==want['upper']['binary64_hex'],'Numeric box exact hex')
        need(float.fromhex(got['objective_hex'])==0 and got['type']==('BINARY' if j<NB else 'CONTINUOUS'),'Full bit types and zero objective')
    cursor=0;numeric_terms=0
    for r,e in enumerate(master['rows']):
        lo,hi=e['lower'],e['upper']
        sides=[('=',lo)] if lo is not None and hi is not None and lo==hi else ([('>',lo)] if lo is not None else [])+([('<',hi)] if hi is not None else [])
        for sense,endpoint in sides:
            got=backend['rows'][cursor];cursor+=1
            need(got['master_row']==r and got['sense']==sense and got['rhs_hex']==endpoint['binary64_hex'],'All backend endpoint-side mappings')
            need(got['terms']==[[j,a['binary64_hex']] for j,a in e['terms']],'All exact numerical search coefficients')
            value=float.fromhex(endpoint['binary64_hex']);lower,upper=(value,value) if sense=='=' else ((value,1e20) if sense=='>' else (-1e20,value))
            need(float.fromhex(got['lower_hex'])==lower and float.fromhex(got['upper_hex'])==upper,'Actual SCIP finite side/infinity sentinel')
            numeric_terms+=len(got['terms'])
    need(cursor==len(backend['rows']),'Complete backend row denominator')
    params=read(RUN/'master_parameters.json');returned=read(RUN/'master_solver_returned.json')
    need(params['explicit']==plan['master_options'],'Declared search options')
    for name,value in plan['master_options'].items():need(params['after_setters'][name]==returned['parameters_after_call'][name]==value,'Prescribed option maintained')
    need(params['changed']=={k:dict(before=params['defaults'][k],after=params['after_setters'][k]) for k in params['defaults'] if params['defaults'][k]!=params['after_setters'][k]},'Full setter delta')
    internal_delta={k:dict(before=params['after_setters'][k],after=returned['parameters_after_call'][k]) for k in params['after_setters'] if params['after_setters'][k]!=returned['parameters_after_call'][k]}
    need(returned['master_solutions']==1 and returned['master_status']=='optimal' and returned['nodes']==11,'Only one returned nominal master solution')
    raw=v.vector(v.read_npz(RUN/'master_raw_solution.npz',('vector',))['vector'],('<f8',),NC,'sole master raw vector')
    need(all(math.isfinite(x) for x in raw),'Finite complete raw incumbent')
    bits=[];nonexact=0
    for value in raw[:NB]:
        q=F(value);near=[k for k in (0,1) if abs(q-k)<=TAU];need(len(near)==1,'Unique prescribed restored binary')
        bits.append(F(near[0]));nonexact+=q!=near[0]
    admission=read(RUN/'master_exact_admission.json')
    need(admission['accepted'] is True and admission['issues']==[] and admission['no_extra_tau'] is True and admission['original_shared_state_values']==[int(x) for x in bits],'Exact saved sole-state admission')
    auxiliary=[]
    for rec in premises['worlds']:
        fi,ni=rec['fossil_indices'],rec['nuclear_index']
        for t,h in enumerate(rec['hours']):
            u=bits[24*t:24*(t+1)];a=list(map(frac,h['a']));b=list(map(frac,h['b']))
            auxiliary.append(max(frac(h['box_lower']),frac(h['rho'])-b[ni]*u[ni],sum((a[j]*u[j] for j in fi),F(0))-23*TAU))
    need(len(auxiliary)==336 and [frac(x) for x in admission['auxiliary_exact']]==auxiliary,'Deterministic minimum exact auxiliary envelope')
    point=bits+auxiliary
    for j,(q,box) in enumerate(zip(point,master['boxes'])):
        need(scalar(box['lower'])<=q<=scalar(box['upper']) and (j>=NB or q in (0,1)),'Full exact master box/binary')
    for r,e in enumerate(master['rows']):
        activity=sum((scalar(a)*point[j] for j,a in e['terms']),F(0));lo,hi=scalar(e['lower']),scalar(e['upper'])
        need((lo is None or activity>=lo) and (hi is None or activity<=hi),'Full exact necessary master row '+str(r))
    request=read(RUN/'LP_request.json');fixed=read(LP/'fixed_schedule.json')
    need(request['state_values']==[int(x) for x in bits] and request['conditional_on_exact_admission'] is True,'Conditional one-state nomination')
    need(request['freeze_sha256']==PINS[PRE/'prepared_freeze.json'] and request['source_sha256']==read(PRE/'prepared_freeze.json')['source_sha256'],'Worker frozen source/request')
    need(request['master_admission_sha256']==fixed['master_admission_sha256']==sha(RUN/'master_exact_admission.json') and request['master_raw_sha256']==sha(RUN/'master_raw_solution.npz'),'One raw/exact incumbent relation')
    need(fixed['fixed_columns']==[dict(column=START+j,value=int(x)) for j,x in enumerate(bits)],'All 12096 original fixed states')
    m=v.load_model(PRE/'joint');need((m.rows,m.cols,len(m.data))==(69362,33936,291176),'Original joint shape')
    original_mask=tuple(v.vector(v.read_npz(PRE/'joint/integrality.npz',('integrality',))['integrality'],('|u1',),m.cols,'original joint mask'))
    need(original_mask==tuple(int(START<=j<STOP) for j in range(m.cols)),'Unchanged complete joint mask')
    lower=list(m.lower);upper=list(m.upper)
    for j,q in enumerate(bits):need(lower[START+j]<=q<=upper[START+j],'Original exact state box');lower[START+j]=upper[START+j]=float(q)
    fb=v.read_npz(LP/'fixed_bounds.npz',('column_lower','column_upper'))
    need(tuple(lower)==v.vector(fb['column_lower'],('<f8',),m.cols,'fixed lower') and tuple(upper)==v.vector(fb['column_upper'],('<f8',),m.cols,'fixed upper'),'Only selected original state boxes fixed')
    members=('data','indices','indptr','shape','column_lower','column_upper','row_lower','row_upper','objective','original_integrality','backend_integrality')
    rb=v.read_npz(LP/'backend_readback.npz',members)
    expected={'data':(m.data,('<f8',)),'indices':(m.indices,('<i8',)),'indptr':(m.indptr,('<i8',)),
       'shape':((m.rows,m.cols),('<i8',)),'column_lower':(tuple(lower),('<f8',)),'column_upper':(tuple(upper),('<f8',)),
       'row_lower':(m.row_lower,('<f8',)),'row_upper':(m.row_upper,('<f8',)),
       'objective':((0.,)*m.cols,('<f8',)),'original_integrality':(original_mask,('|u1',)),'backend_integrality':((0,)*m.cols,('|u1',))}
    for name,(values,dtypes) in expected.items():need(v.vector(rb[name],dtypes,len(values),name)==values,'Every recourse backend value '+name)
    rmeta=read(LP/'backend_readback.json');need(rmeta['readback_sha256']==sha(LP/'backend_readback.npz') and rmeta['options']==plan['LP_options'],'Conditional LP readback/options')
    need(rmeta['original_bits_fixed']==NB and rmeta['same_original_matrix'] is True and rmeta['only_state_boxes_changed'] is True and rmeta['all_backend_continuous'] is True,'LP original model semantics')
    completion=read(RUN/'completion.json');result=read(RUN/'result.json');lc=read(LP/'completion.json');lr=read(LP/'result.json');ls=read(LP/'solver_returned.json')
    ledger=completion['ledger'];need(ledger['master_attempted']==ledger['master_returned']==ledger['LP_worker_invoked']==1 and ledger['LP']['attempted']==ledger['LP']['returned']==1,'Exactly two total solver calls')
    need(ledger['LP']==lc['call_ledger'] and ledger['LP_worker_exit_code']==0 and ledger['LP_worker']['returncode']==0 and not ledger['LP_worker']['timed_out'],'Normal sole worker return')
    need(returned['ledger']['master_actual_seconds']==ledger['master_actual_seconds'] and returned['ledger']['master_returned']==1,'Master returned ledger')
    need(lr['status']==ls['status']=='HighsModelStatus.kInfeasible' and lr['run_status']==ls['run_status']=='HighsStatus.kOk' and lr['valid_solution'] is ls['valid_solution'] is False,'Numerical LP failure only')
    need(result['master_candidate_accepted'] is True and result['master_solutions']==1 and result['sole_returned_solution'] is True,'Only exact necessary nominee')
    for doc in (completion['final_admission'],lc['final_admission'],result,lr):
        need(doc['accepted_common'] is False and doc['common_verdict']=='UNKNOWN' and doc['phase_deadline_met'] is True,'No positive or exact negative admission')
        need(doc['admission_monotonic']<=doc['deadline_monotonic']==request['deadline_monotonic'],'Authoritative phase deadline')
    need(result['provisional_until_completion'] is lr['provisional_until_completion'] is True,'Provisional result convention')
    need(0<=ledger['master_actual_seconds']<=120 and 0<=ledger['LP']['actual_seconds']<=60 and 0<=completion['phase_seconds']<=360,'Recorded phase/call limits')
    need(completion['phase_seconds']>=ledger['master_actual_seconds']+ledger['LP']['actual_seconds'],'Phase includes both calls')
    need(completion['soft_phase_overrun']==completion['master_soft_overrun']==lc['LP_soft_overrun']==0 and completion['no_retries'] and completion['no_exact_negative'] and lc['no_negative_claim'],'Conservative closed accounting')
    need(read(RUN/'master_call_ready.json')['remaining']>=125 and read(RUN/'LP_launch_ready.json')['remaining']>=65 and read(LP/'call_ready.json')['remaining']>=65,'Admission guard values')
    need(read(LP/'invocation_boundary.json')['not_proof_call_started'] is True,'Boundary marker limitation')
    need(not any((LP/name).exists() for name in ('raw_solution.npz','candidate_vector.npz','exact_candidate_checks.json','failure.json')) and not any('ray' in p.name.lower() for p in RUN.rglob('*')),'No accepted/rejected physical point or exact negative certificate')
    process=read(ARM/'PROCESS_CLOSURE.json')
    need(process['exit_code']==0 and process['retries']==process['external_termination_calls']==0 and process['known_owned_pids_still_present']==[],'Closed process receipt')
    need(process['known_owned_pids_checked']==[73636,18184,24456] and process['no_windows_descendant_timeout_test_claim'] is True,'Known PID scope only')
    need(process['conditional_worker']['actual_descendant_pid'] is None and process['conditional_worker']['descendant_not_observed_before_normal_completion'] is True and not process['conditional_worker']['timed_out'],'No fabricated child/timeout evidence')
    need(process['authoritative_common_verdict']=='UNKNOWN','Process verdict')
    for e in manifest['files']+outputs:binding(e)
    for p,h in PINS.items():need(sha(p)==h,'Closing trusted pin')
    report=dict(status='PASS_INDEPENDENT_POSTRUN',utc=datetime.now(timezone.utc).isoformat(),reviewer_sha256=sha(__file__),elapsed_seconds=time.perf_counter()-start,
      input_bindings=239,producer_outputs=25,producer_run_files=23,all_files_unchanged=True,freeze_sha256=PINS[PRE/'prepared_freeze.json'],inventory_sha256=PINS[ARM/'producer_output_inventory.csv'],
      exact_master_rows=17212,exact_master_columns=NC,exact_bits=NB,nonexact_raw_bits_restored=nonexact,auxiliary_envelope_values=336,
      exact_necessary_nominee_verified=True,master_backend_rows=cursor,master_backend_term_uses=numeric_terms,master_numeric_readback_complete=True,
      full_joint_rows=m.rows,full_joint_columns=m.cols,joint_coefficient_values=len(m.data),full_fixed_LP_readback_complete=True,
      original_full_integrality_preserved_as_fixed_states=True,master_internal_postcall_parameter_delta=internal_delta,
      master_calls=1,LP_calls=1,master_seconds=ledger['master_actual_seconds'],LP_seconds=ledger['LP']['actual_seconds'],phase_seconds=completion['phase_seconds'],
      LP_status='NUMERICAL_INFEASIBLE_NO_VALID_POINT_NO_EXACT_NEGATIVE_CERTIFICATE',common_verdict='UNKNOWN',
      no_network_witness=True,no_global_negative=True,windows_timeout_descendant_termination_tested=False,actual_LP_descendant_pid_unobserved=True,
      producer_imports=0,optimizer_calls_by_reviewer=0,model_rebuilds=0,new_candidates=0,private_logs_read=False,decoder_reuse=PINS[k])
    with out.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps({'status':report['status'],'report_sha256':sha(out),'elapsed_seconds':report['elapsed_seconds']}))

if __name__=='__main__':main()
