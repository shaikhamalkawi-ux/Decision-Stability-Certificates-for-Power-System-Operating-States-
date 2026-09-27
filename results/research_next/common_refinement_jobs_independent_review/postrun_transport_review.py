"""Closed-output backend/transport/ledger audit, separate from certificate math.

Drafted before recovery closure; no active outputs inspected. No producer/encoder import, optimizer, model construction,
seed q/control reconstruction, or exact master nomination replay.
"""
import argparse
import csv
from datetime import datetime, timezone
from fractions import Fraction as Q
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ARM = ROOT / 'results/research_next/common_refinement_jobs'
PRE, RUN = ARM / 'prepared', ARM / 'run01'
FREEZE = '8053a3795c9ed14d53c84df5dddefa355fb29572be9ce213758bf75a3922347c'
MANIFEST = '4478c4637b2b81256cc31e9cdc2516b2112309c30096176d5df42ba205dd09a6'
SOURCE = 'fa1548f4d7765ac84e2f74a06df2fde640c713b85a1c27bdc29c99f3bb1b2973'
GO = 'da449965a1febf3bdeac8915c3355f7fd3a6ebc9c8cda864021432c74a69afc0'
PROTOCOL = '14f9a4f2fb11966eec851e1c69187945f2daa523f1d5fd1a5b389900ecdf7b1f'
MATH_REVIEW = '205b8118a0a01d5cb63a1435b5b8dbdc0089ca1aad7e2cbb153b9117ac63738a'
ENCODING_REVIEW = 'fa336a6b919b50df691f4ec01b8ef70cadd63e7f800f0fb4b3298c783c642a0f'
KERNEL = '708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'
NB, START, STOP = 12096, 6888, 18984
LIMITS = {'master': 120., 'recourse': 60., 'phase1': 60., 'transport_only': 0.}
SCIP_OPTIONS = {'limits/time': 120., 'limits/solutions': 1, 'parallel/maxnthreads': 1,
                'lp/threads': 1, 'randomization/randomseedshift': 0,
                'randomization/permutationseed': 0, 'randomization/lpseed': 0,
                'numerics/feastol': 1e-8}
LP_OPTIONS = {'time_limit': 60., 'threads': 1, 'random_seed': 0, 'presolve': 'on', 'solver': 'simplex'}


def need(x, why):
    if not x:
        raise ValueError(why)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))


def zipped(p):
    with gzip.open(p, 'rt', encoding='utf-8') as f:
        return json.load(f)


def binding(x):
    data = Path(x['path']).read_bytes()
    need(len(data) == x['bytes'] and hashlib.sha256(data).hexdigest() == x['sha256'], 'Binding: ' + x['path'])


def frac(x):
    q = Q(int(x[0]), int(x[1]))
    need(x == [str(q.numerator), str(q.denominator)], 'Canonical exact scalar')
    return q


def pair(x):
    return [str(x.numerator), str(x.denominator)]


def finite_hex(s):
    value = float.fromhex(s)
    need(math.isfinite(value), 'Finite numeric coefficient/endpoint')
    return value


def audit_cut_encoding(proof, encoding, actual, lower, require_exclusion):
    """Actual necessary-row implication; no seed source-proof/recipe reconstruction."""
    terms = proof['state_terms']
    source = {j - START: frac(a) for j, a in terms}
    need(len(source) == len(terms) and all(type(j) is int and 0 <= j < NB for j in source), 'Sparse state coordinates')
    need(all(source.values()) and list(source) == sorted(source), 'Exact nonzero ordered source support')
    b = frac(proof['cut_rhs']); scale = frac(encoding['scale'])
    need(scale > 0, 'Positive source scaling')
    need(encoding['full_dimension'] == NB and encoding['require_exclusion'] is require_exclusion, 'Encoding domain/mode')
    need(encoding['coordinate_count'] == len(source) and encoding['implicit_exact_zeros']['count'] == NB-len(source), 'Exact-zero completion count')
    need(encoding['source_rhs'] == pair(b) and encoding['upper'] == 'positive_infinity', 'Source RHS/unbounded upper')
    need(encoding['eligible_for_backend'] is True and encoding['constant_row'] is False, 'Admitted nonconstant row')
    beta = b/scale
    need(frac(encoding['scaled_rhs']) == beta, 'Scaled RHS')
    need([x['coordinate'] for x in encoding['coefficients']] == list(source), 'Complete supplied source support')
    for x in encoding['coefficients']:
        j=x['coordinate']
        need(frac(x['source']) == source[j] and frac(x['scaled']) == source[j]/scale, 'Source/scaled term identity')
    need(encoding['extra_binary_tau'] == encoding['alternative_scales'] == 0, 'No alternate recipe or binary tau')
    actual=list(actual); need(len({j for j,x in actual}) == len(actual), 'Unique actual coordinates')
    observed={}
    for j,x in actual:
        need(type(j) is int and 0 <= j < NB and math.isfinite(x), 'Actual binary domain')
        need(j in source or x == 0, 'No nonzero actual term on implicit zero')
        observed[j]=x
    residual=sum((min(Q(observed.get(j,0.))-a/scale,Q(0)) for j,a in source.items()),Q(0))
    bound=beta+residual
    need(math.isfinite(lower) and Q(lower) <= bound, 'Actual outward implication over full binary box')
    origin=encoding['origin']; exact_gap=actual_gap=None
    if origin is not None:
        need(len(origin)==NB and all(type(x) is int and x in (0,1) for x in origin), 'Complete original bit origin')
        exact_gap=b-sum((a*origin[j] for j,a in source.items()),Q(0))
        actual_gap=Q(lower)-sum((Q(observed.get(j,0.))*origin[j] for j in source),Q(0))
        need(frac(encoding['original_origin_gap'])==exact_gap,'Exact origin gap agreement')
    if require_exclusion:
        need(origin is not None and exact_gap>0 and actual_gap>0,'Exact and actual strict progress')
    else:
        need(origin is None,'Seed mode carries no required exclusion')
    return dict(outward_valid=True,actual_residual_box_lower=pair(residual),actual_outward_lower_limit=pair(bound),
                outward_slack=pair(bound-Q(lower)),original_origin_gap=pair(exact_gap) if exact_gap is not None else None,
                actual_origin_gap=pair(actual_gap) if actual_gap is not None else None,
                strict_origin_exclusion_required=require_exclusion)


def master_readback(folder, request, base):
    binding(request['model'])
    for x in request['bindings']:
        binding(x)
    model = zipped(request['model']['path'])
    need(model['boxes'] == base['boxes'] and model['rows'][:17212] == base['rows'], 'Unchanged full base master')
    need({k: v for k, v in model.items() if k != 'rows'} == {k: v for k, v in base.items() if k != 'rows'}, 'Only appended rows')
    records = request['cuts']
    seeds=read(PRE/'inherited_seed_index.json')['records']
    need(records[:336]==seeds,'All 336 exact inherited seed bindings in order')
    expected_new=request['round']-1 if request['kind']=='master' else 8
    need(len(records)==336+expected_new,'Exact retained-cut denominator at this stage')
    for k,record in enumerate(records[336:],1):
        need(record==read(RUN/f'round_{k:02d}'/'next_cut.json'),'No dropped, reordered or invented refinement')
    need(len(model['rows']) == 17212+len(records) and len(records) >= 336, 'Complete dynamic master rows')
    backend = zipped(folder/'master_backend_readback.json.gz')
    need(backend['exact_rational_master_sha256'] == sha(PRE/'master.json.gz'), 'Readback identifies inherited base')
    need(backend['nominal_numeric_search_only'] and backend['all_actual_numeric_coefficients_read_back'], 'Readback declared scope')
    need(len(backend['boxes']) == len(model['boxes']) == 12432, 'Complete backend column denominator')
    for j, (a, b) in enumerate(zip(backend['boxes'], model['boxes'])):
        need(a['lower_hex'] == b['lower']['binary64_hex'] and a['upper_hex'] == b['upper']['binary64_hex'], 'Full actual numeric box')
        need(float.fromhex(a['objective_hex']) == 0 and a['type'] == ('BINARY' if j < NB else 'CONTINUOUS'), 'Zero cost/full original bit types')
    cursor = 0; coefficient_uses = 0; appended_actual = {}
    for r, row in enumerate(model['rows']):
        lo, hi = row['lower'], row['upper']
        sides = [('=', lo)] if lo is not None and hi is not None and lo == hi else ([('>', lo)] if lo is not None else []) + ([('<', hi)] if hi is not None else [])
        for sense, endpoint in sides:
            actual = backend['rows'][cursor]; cursor += 1
            need((actual['master_row'], actual['sense'], actual['rhs_hex']) == (r, sense, endpoint['binary64_hex']), 'Backend endpoint-side map')
            need(actual['terms'] == [[j, a['binary64_hex']] for j, a in row['terms']], 'Every numeric backend coefficient')
            value = finite_hex(endpoint['binary64_hex'])
            lower, upper = (value, value) if sense == '=' else ((value, 1e20) if sense == '>' else (-1e20, value))
            need(float.fromhex(actual['lower_hex']) == lower and float.fromhex(actual['upper_hex']) == upper, 'Actual sides/SCIP infinity sentinel')
            coefficient_uses += len(actual['terms'])
            if r >= 17212:
                need(sense == '>' and r not in appended_actual, 'One actual lower-only appended row')
                appended_actual[r] = actual
    need(cursor == len(backend['rows']), 'All actual backend rows')
    dynamic = read(folder/'dynamic_model_binding.json')
    need(dynamic == {'search_model': request['model'], 'base_master_sha256': sha(PRE/'master.json.gz'),
                     'readback_sha256': sha(folder/'master_backend_readback.json.gz')}, 'Dynamic readback identity')
    params = read(folder/'master_parameters.json')
    need(params['explicit'] == SCIP_OPTIONS, 'Fixed explicit SCIP options')
    need(all(params['after_setters'][k] == value for k, value in SCIP_OPTIONS.items()), 'Options readback')
    need(params['changed'] == {k: {'before': params['defaults'][k], 'after': v} for k, v in params['after_setters'].items() if params['defaults'][k] != v}, 'Full setter delta')
    transport = zipped(folder/'actual_cut_transport.json.gz')
    expected = list(range(len(records))) if request['kind'] == 'master' else [len(records)-1]
    need(len(transport) == len(expected), 'Declared transport check denominator')
    checks = []
    for i, record in enumerate(records):
        binding(record['proof']); binding(record['encoding'])
        need(record['kind']==('seed' if i<336 else 'refinement'),'Correct appended row role')
        proof = zipped(record['proof']['path']); encoding = zipped(record['encoding']['path'])
        row = model['rows'][17212+i]
        if record['kind']=='refinement':
            origin=read(RUN/f"round_{record['round']:02d}"/'novel_nominee.json')['values']
            need(encoding['origin']==origin,'New refinement bound to its own complete nominated bits')
        need(row['provenance']['proof'] == record['proof'] and row['provenance']['encoding'] == record['encoding'], 'Per-row proof/encoding links')
        need(row['provenance']['exact_scaled_original_row'] and row['provenance']['no_extra_tau'] and row['upper'] is None, 'Exact search-row convention')
        scale = frac(encoding['scale']); beta = frac(proof['cut_rhs'])/scale
        need(frac(row['lower']['exact']) == beta and Q(float.fromhex(row['lower']['binary64_hex']))-beta == frac(row['lower']['rounding_error']), 'Dynamic endpoint exact/float distinction')
        need(row['terms'] == [[x['coordinate'], {'exact': x['scaled'], 'binary64_hex': x['encoded_hex'], 'rounding_error': x['error']}] for x in encoding['coefficients']], 'Complete dynamic exact/numeric coefficient relation')
        actual = appended_actual[17212+i]
        check = audit_cut_encoding(proof, encoding, [(j, finite_hex(x)) for j, x in actual['terms']],
                                   finite_hex(actual['lower_hex']), record['kind'] == 'refinement')
        if i in expected:
            saved = transport[expected.index(i)]
            need(saved['master_row'] == 17212+i and saved['proof_sha256'] == record['proof']['sha256'] and saved['encoding_sha256'] == record['encoding']['sha256'], 'Saved actual-transport bindings')
            reported = saved['verification']
            for k in ('outward_valid', 'actual_residual_box_lower', 'actual_outward_lower_limit', 'outward_slack', 'original_origin_gap', 'actual_origin_gap'):
                need(reported[k] == check[k], 'Independent actual transport scalar '+k)
            need(reported['admitted'] and reported['extra_binary_tau'] == 0 and not reported['fractional_control_evaluated'], 'Saved actual admission scope')
        checks.append(check)
    return {'backend_rows': cursor, 'backend_coefficient_uses': coefficient_uses,
            'new_necessary_rows_independently_transport_checked': len(checks),
            'producer_transport_checks': len(transport), 'numeric_master_readback_complete': True}


def transport_receipt(folder):
    rec=read(folder/'final_transport_pins.json')
    expected={str((PRE/'prepared_freeze.json').resolve()).casefold():FREEZE,
              str((PRE/'input_manifest.json').resolve()).casefold():MANIFEST,
              str((ROOT/'src/researchnext_common_refinement_jobs.py').resolve()).casefold():SOURCE,
              str((ROOT/'docs/research_next/COMMON_REFINEMENT_JOBS_PROTOCOL.md').resolve()).casefold():PROTOCOL}
    rows=rec['files']
    need(len(rows)==4 and len({str(Path(x['path']).resolve()).casefold() for x in rows})==4,'Four distinct final transport receipts')
    got={str(Path(x['path']).resolve()).casefold():x['expected_sha256'] for x in rows}
    need(got==expected,'Receipted expectations match external GO pins')
    need(rec['all_unchanged'] and all(x['actual_sha256']==x['expected_sha256'] for x in rows),'All closing transport bytes unchanged')
    return True


def ownership(folder,request,closed):
    """Read only archived precise-handle identities/assignment/reaping records."""
    present=lambda name:(folder/name).is_file()
    has_go=present('worker_go.json'); result={'GO_issued':has_go,'actual_OS_test_by_reviewer':False}
    captures=sorted(folder.glob('captured_process_*.json'))
    processes=[read(p) for p in captures]
    if processes:
        need(1<=len(processes)<=2 and processes[0]['role']=='launcher','Captured exact process role order')
        need(len({x['pid'] for x in processes})==len(processes),'No duplicate captured process')
        need(all(type(x['creation_filetime']) is int and x['creation_filetime']>0 for x in processes),'Precise creation identities')
        need(all(x['any_job_before']['api_succeeded'] for x in processes),'Captured membership readbacks')
    if present('worker_ready.json'):
        ready=read(folder/'worker_ready.json')
        need(ready['token']==request['token'] and ready['request_sha256']==sha(folder/'request.json') and ready['source_sha256']==SOURCE,'Authenticated actual worker')
        launcher=closed['launcher_pid']
        need(ready['pid']==launcher or ready['parent_pid']==launcher,'Direct authenticated launcher chain')
        wanted=[launcher]+([] if ready['pid']==launcher else [ready['pid']])
        if processes:
            need([x['pid'] for x in processes]==wanted[:len(processes)],'Exact retained process identities')
    else:
        need(not has_go and not processes,'No ownership authority without actual worker handshake')
        wanted=[]
    attempts=sorted(folder.glob('job_assignment_attempt_*.json'))
    assigned=sorted(folder.glob('job_assignment_result_*.json'))
    if attempts:
        before=read(folder/'all_handles_captured.json')
        need(before=={'processes':processes,'no_assignment_yet':True},'All handles precede first assignment')
        need([x['pid'] for x in processes]==wanted,'No assignment before all expected captures')
    need(len(assigned)<=len(attempts)<=len(processes),'Assignment/result denominator')
    assignment_checks=[]
    for i,path in enumerate(attempts):
        a=read(path)
        need(a['order']==i+1 and a['new_job_index']==i and a['process']==processes[i],'Separate prospective job per process')
        need(a['before_any']['api_succeeded'] and a['before_selected']['api_succeeded'],'Before assignment membership APIs')
        if i<len(assigned):
            b=read(assigned[i])
            need(b['order']==i+1 and b['new_job_index']==i and b['process']==processes[i],'Actual assignment identity')
            need(b['before_any']==a['before_any'] and b['before_selected']==a['before_selected'],'Preserved preassignment evidence')
            good=b['assignment_succeeded'] and b['after_any']['api_succeeded'] and b['after_selected']['api_succeeded'] and b['after_selected']['in_job']
            assignment_checks.append(dict(pid=b['process']['pid'],new_job_index=i,succeeded=bool(good),win32_last_error=b['win32_last_error']))
    if has_go:
        go=read(folder/'worker_go.json');chain=read(folder/'owned_process_chain.json')
        need(go=={'token':request['token'],'request_sha256':sha(folder/'request.json'),'ownership_admitted':True},'Exact ownership GO')
        need(len(assigned)==len(processes)==len(wanted) and all(x['succeeded'] for x in assignment_checks),'Every job membership successful before GO')
        need(chain['processes']==processes and chain['launcher_pid']==closed['launcher_pid'] and chain['actual_pid']==ready['pid'] and chain['actual_parent_pid']==ready['parent_pid'],'Owned chain')
        need(all(chain[k] for k in ('one_job_per_process','all_handles_captured_before_assignment','all_memberships_verified_before_GO','job_kill_on_close')),'Declared ownership admission scope')
    if present('owned_cleanup.json'):
        cleanup=read(folder/'owned_cleanup.json')
        need(cleanup['processes']==processes and cleanup['expected_processes']==len(wanted),'Cleanup retains complete captured identities')
        need(all(cleanup[k] for k in ('no_breakaway','no_outer_job_reconfiguration','no_name_based_kill')),'Cleanup confinement')
        need(cleanup['unobserved_child_closure_unverified']==(len(processes)!=len(wanted)),'Unobserved process limitation explicit')
        for act in cleanup['actions']:
            if act['action']=='TerminateJobObject':
                need(0<=act['job_index']<len(processes),'Only retained owned job affected')
            else:
                need(act['action'] in ('TerminateProcess_exact_retained_handle','reap') and act['process'] in processes,'Only retained exact process handle affected')
        if closed.get('owned_handles_reaped'):
            need(cleanup['all_retained_handles_reaped'] and len(processes)==len(wanted)>0,'Complete nonvacuous reaping')
        if 'completion' in closed:
            need(closed.get('owned_handles_reaped') is True and cleanup['all_retained_handles_reaped'],'Completed worker exact handles closed')
        result['cleanup']=cleanup
    else:
        need(not has_go,'Successful worker ownership requires a cleanup receipt')
    result.update(captured_processes=processes,assignment_results=assignment_checks,
                  timed_out=closed['timed_out'],unobserved_child_selfexit_required=closed.get('unobserved_child_selfexit_required',False))
    return result


def main(args):
    started = time.perf_counter()
    report_path = OUT/'postrun_transport_review.json'
    need(not report_path.exists(), 'One closed independent review')
    pinpaths = {PRE/'prepared_freeze.json': FREEZE, PRE/'input_manifest.json': MANIFEST,
                ROOT/'src/researchnext_common_refinement_jobs.py': SOURCE,
                ROOT/'docs/research_next/COMMON_REFINEMENT_JOBS_PROTOCOL.md': PROTOCOL,
                ARM/'ROOT_EXECUTION_GO.json': GO, ARM/'producer_output_inventory.csv': args.inventory_sha256,
                RUN/'completion.json': args.completion_sha256,
                ROOT/'src/research8h_standalone_verify.py': KERNEL}
    for p, expected in pinpaths.items():
        need(sha(p) == expected, 'External trusted pin: '+str(p))
    authorization = read(ARM/'ROOT_EXECUTION_GO.json')
    for rel, expected in authorization['pins'].items():
        need(sha(ROOT/rel) == expected, 'Explicit GO transport pin')
    need(authorization['scientific_claims_provisional_until_independent_closure'] is True, 'Final transport gate authority')
    need(authorization['freeze_sha256']==FREEZE and authorization['maximum_new_nominees']==8 and authorization['maximum_optimizer_attempts']==24 and authorization['overall_seconds']==2400,'Exact execution authority')
    items = read(PRE/'input_manifest.json')['files']
    need(len(items) == 1769, '1769 inputs')
    for x in items:
        binding(x)
    with (ARM/'producer_output_inventory.csv').open(encoding='utf-8-sig', newline='') as f:
        inventory = list(csv.DictReader(f))
    need(len({x['path'] for x in inventory}) == len(inventory), 'Unique public output inventory')
    outputs = [{'path': str(ROOT/x['path']), 'bytes': int(x['bytes']), 'sha256': x['sha256']} for x in inventory]
    for x in outputs:
        binding(x)
    in_run = {str(Path(x['path']).relative_to(RUN)) for x in outputs if Path(x['path']).is_relative_to(RUN)}
    need(in_run == {str(p.relative_to(RUN)) for p in RUN.rglob('*') if p.is_file()}, 'Complete stable run inventory')
    inherited=read(PRE/'inherited_seed_index.json')
    need(inherited['mathematical_review_sha256']==MATH_REVIEW and inherited['encoding_review_sha256']==ENCODING_REVIEW,'Closed seed mathematics/encoding admissions')
    need(len(inherited['records'])==inherited['cases']==336,'Inherited full seed denominator')
    inheritance=read(RUN/'seeds/inherited_completion.json')
    need(inheritance['inherited_cases']==336 and inheritance['new_seed_arithmetic']==0 and inheritance['no_q_control_anchor_recomputation'],'No repeated seed mathematics')
    need(inheritance['copied_index_sha256']==sha(PRE/'inherited_seed_index.json'),'Runtime inherited seed binding')
    runtime=read(PRE/'plan.json')['runtime']
    base = zipped(PRE/'master.json.gz')
    result, completion = read(RUN/'result.json'), read(RUN/'completion.json')
    start = read(RUN/'execution_started.json')
    need(start['freeze_sha256'] == FREEZE and start['source_sha256'] == SOURCE and start['phase_seconds'] == 2400., 'Execution scope')
    need(start['round_ceiling'] == 8 and start['optimizer_call_ceiling'] == 24, 'Execution ceilings')
    workers = sorted(RUN.glob('round_*/*/worker_launch_attempt.json'))
    attempts = sorted(RUN.glob('round_*/*/optimizer_attempt.json'))
    returns = sorted(RUN.glob('round_*/*/optimizer_returned.json'))
    errors = sorted(RUN.glob('round_*/*/optimizer_error.json'))
    cancelled = sorted(RUN.glob('round_*/*/optimizer_cancelled_before_call.json'))
    need(len(workers)==len(attempts)==len(returns)==1 and not errors and not cancelled, 'Closed sole first-master call; no later stages')
    need(result['stop_reason']==completion['stop_reason']=='NO_SINGLE_EXACT_MASTER_NOMINEE', 'Closed numerical null reason')
    need(result['seed_count']==result['total_cut_records']==result['cuts_with_completed_actual_transport']==336 and result['new_cut_count']==result['completed_rounds']==0, '336 inserted inherited cuts; no refinement/complete round')
    need(result['terminal_cut_numeric_transport']=='ADMITTED','All inherited numerical cuts admitted')
    details = []; deadlines = set(); solver_seconds = 0.; overrun = 0.; worker_kinds = []
    for launch_path in workers:
        folder = launch_path.parent
        launch, request = read(launch_path), read(folder/'request.json')
        kind = request['kind']; worker_kinds.append(kind)
        need(kind=='master' and request['round']==1, 'Only first master actually ran')
        need(request['source_sha256'] == SOURCE and request['freeze_sha256'] == FREEZE, 'Worker frozen authority')
        need(launch['request_sha256'] == sha(folder/'request.json') and launch['remaining'] >= LIMITS[kind]+5, 'Request binding/start guard')
        need(Path(request['folder']).resolve() == folder.resolve() and Path(request['private']).is_relative_to(ROOT/'.work/researchnext_common_refinement_jobs/run01'), 'Unique confined paths')
        command = launch['command']
        exe=runtime['master_executable'] if kind in ('master','transport_only') else runtime['LP_executable']
        need(Path(command[0]).resolve()==Path(exe).resolve(),'Pinned stage interpreter')
        need(command[1] == '-I' and Path(command[2]).resolve() == (ROOT/'src/researchnext_common_refinement_jobs.py').resolve(), 'Isolated frozen worker command')
        need(command[3:] == ['--worker', '--expected-freeze-sha256', FREEZE, '--request', str((folder/'request.json').resolve()), '--expected-request-sha256', sha(folder/'request.json')], 'Complete command authority')
        deadlines.add(request['deadline_monotonic'])
        closed = read(folder/'worker_closed.json')
        detail = {'folder': str(folder.relative_to(RUN)), 'kind': kind, 'timed_out': closed['timed_out']}
        has_go = (folder/'worker_go.json').exists()
        detail['ownership']=ownership(folder,request,closed)
        if (folder/'optimizer_attempt.json').exists():
            attempt = read(folder/'optimizer_attempt.json')
            need(has_go and kind != 'transport_only' and attempt['kind'] == kind and attempt['remaining'] >= LIMITS[kind]+5, 'Actual optimizer gate after process ownership')
        if (folder/'optimizer_returned.json').exists():
            returned = read(folder/'optimizer_returned.json')
            need(returned['attempted'] == returned['returned'] == 1 and returned['optimizer_entered'], 'Returned actual optimizer boundary')
            seconds = returned['actual_seconds']; need(seconds >= 0, 'Nonnegative measured invocation')
            need(returned['solver_soft_overrun'] == max(0., seconds-LIMITS[kind]), 'Soft call overrun accounting')
            solver_seconds += seconds; overrun += returned['solver_soft_overrun']
            detail['solver_seconds'] = seconds
        if (folder/'master_backend_readback.json.gz').exists():
            detail['backend'] = master_readback(folder, request, base)
        need(not (folder/'backend_readback.npz').exists(),'No LP backend was created')
        if (folder/'optimizer_attempt.json').exists():
            need('backend' in detail,'Every attempted optimizer has full prior saved backend readback')
        if (folder/'completion.json').exists():
            transport_receipt(folder)
            wc = read(folder/'completion.json')
            need(closed.get('completion') == wc, 'Closed worker completion identity')
            wf=wc['final_admission']
            need(wf['status']=='timelimit' and wf['solution_count']==0 and not wf['nominee_accepted'] and not wf['accepted_common'],'Time limit without candidate, no mathematical infeasibility')
            need(wf['reason']=='NO_SINGLE_RETURNED_SOLUTION','No eligible nominee')
            need(not (folder/'raw_solution.npz').exists() and not (folder/'exact_master_admission.json').exists(),'No candidate arrays/admission manufactured')
            need(wf==dict(read(folder/'result.json'),accepted_common=False,common_verdict='UNKNOWN',phase_deadline_met=wf['phase_deadline_met']),'Worker result/final admission consistency')
            detail['search_status']=wf['status'];detail['nodes']=wf['nodes'];detail['LP_iterations']=wf['LP_iterations'];detail['solution_count']=wf['solution_count']
        if kind == 'transport_only':
            need(not (folder/'optimizer_attempt.json').exists(), 'No terminal optimizer')
        detail['worker_number']=closed['worker_number']
        detail['optimizer_attempt_record_present']=(folder/'optimizer_attempt.json').exists()
        detail['optimizer_returned_record_present']=(folder/'optimizer_returned.json').exists()
        details.append(detail)
    ordered=sorted(details,key=lambda d:d['worker_number'])
    need([d['worker_number'] for d in ordered]==list(range(1,len(ordered)+1)),'Complete launch order')
    allowed=[(r,k) for r in range(1,9) for k in ('master','recourse','phase1')]+[(8,'transport_only')]
    # pathlib serializes Windows separators; use the saved request as the authority instead.
    actual=[(read(RUN/d['folder']/'request.json')['round'],d['kind']) for d in ordered]
    need(actual==allowed[:len(actual)],'Exactly one prospective stage trajectory')
    transport_receipt(RUN)
    need(len(deadlines) <= 1, 'Shared global monotonic deadline')
    ledger = completion['ledger']
    need(result['ledger'] == ledger, 'Final ledgers agree')
    need(ledger['worker_launch_attempts'] == len(workers) and ledger['optimizer_attempt_records'] == len(attempts) and ledger['optimizer_returned'] == len(returns), 'Complete attempt/return counts')
    need(ledger['attempts_cancelled_before_optimizer'] == len(cancelled) and ledger['entered_calls_from_return_or_error'] == len(returns)+len(errors), 'Cancelled/entered distinction')
    need(len(ledger['calls']) == len(attempts), 'Full solver ledger denominator')
    for rec, path in zip(ledger['calls'], attempts):
        need(rec['returned']==(read(path.parent/'optimizer_returned.json') if (path.parent/'optimizer_returned.json').exists() else None),'Full returned-call ledger')
        need(rec['cancelled_before_call']==(path.parent/'optimizer_cancelled_before_call.json').exists(),'Cancellation ledger')
        binding(rec['attempt']); need(Path(rec['attempt']['path']).resolve() == path.resolve(), 'Every actual attempt bound')
    closures=sorted(RUN.glob('round_*/*/worker_closed.json'))
    need(len(ledger['worker_closures'])==len(closures)==len(workers),'All launched worker closures retained')
    for rec,path in zip(ledger['worker_closures'],closures):
        binding(rec); need(Path(rec['path']).resolve()==path.resolve(),'Every exact closure bound')
    need(result['all_frozen_bytes_unchanged'] and completion['all_frozen_bytes_unchanged'], 'Producer final input validation')
    need(result['provisional_until_completion'] and result['no_global_infeasibility_claim'] and result['one_adaptive_trajectory'], 'Scientific scope')
    need(completion['no_retry'] and completion['no_ninth_nomination'], 'No additional trajectory')
    elapsed = completion['phase_seconds']
    need(elapsed >= solver_seconds and completion['phase_soft_overrun'] == max(0., elapsed-2400.), 'Full phase/call accounting')
    final = completion['final_admission']
    need(final['common_verdict'] == ('VERIFIED_EXPANDED_COMMON_COMMITMENT' if final['accepted_common'] else 'UNKNOWN'), 'No numerical global negative')
    need(not final['accepted_common'] and not result['accepted_common'] and final['common_verdict']=='UNKNOWN','Authoritative common problem remains UNKNOWN')
    if deadlines:
        need(final['phase_deadline_met'] == (final['admission_monotonic'] <= next(iter(deadlines))), 'Final sampled deadline')
    for x in items+outputs:
        binding(x)
    for p, expected in pinpaths.items():
        need(sha(p) == expected, 'Closing external pin including transport files')
    report = {'status': 'PASS_INDEPENDENT_BACKEND_TRANSPORT_AND_LEDGER',
              'utc': datetime.now(timezone.utc).isoformat(), 'source_sha256': sha(__file__),
              'elapsed_seconds': time.perf_counter()-started, 'input_bindings': 1769,
              'producer_outputs': len(outputs), 'run_files': len(in_run), 'all_pinned_bytes_unchanged': True,
              'external_final_transport_gate': {'freeze_sha256': FREEZE, 'manifest_sha256': MANIFEST, 'GO_sha256': GO, 'pass': True},
              'workers': details, 'worker_launches': len(workers), 'optimizer_attempts': len(attempts),
              'optimizer_returned': len(returns), 'optimizer_errors': len(errors), 'cancelled_before_call': len(cancelled),
              'returned_solver_seconds': solver_seconds, 'solver_soft_overrun_seconds': overrun, 'phase_seconds': elapsed,
              'producer_common_verdict': final['common_verdict'], 'scientific_certificate_nominee_positive_review': 'Separate Find audit required; not replayed here.',
              'encoder_author_disclosed': True, 'encoder_helper_imported': False,
              'actual_outward_inequalities_independently_recomputed': True,
              'inherited_seed_math_review_sha256': MATH_REVIEW,'inherited_requested_encoding_review_sha256': ENCODING_REVIEW,
              'seed_proof_recipe_recomputation': False,'prepared_admission_repeated': False,'new_OS_probes': 0,
              'decoder_imported': False, 'producer_imports': 0, 'optimizer_calls_by_reviewer': 0,
              'private_logs_read': False, 'new_candidates_or_coefficients': 0,
              'limitations': ['Recorded actual owned-process behavior only; no claim of unexercised timeout termination.',
                              'No recourse, phase-I or new cut ran; the numerical time limit is not infeasibility.',
                              'Inherited seed source proofs are covered by the pinned earlier mathematical review; no new nominee or full positive exists.']}
    with report_path.open('x', encoding='utf-8') as f:
        json.dump(report, f, indent=2, allow_nan=False); f.write('\n')
    print(json.dumps({'status': report['status'], 'sha256': sha(report_path), 'elapsed_seconds': report['elapsed_seconds']}))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--inventory-sha256', required=True)
    p.add_argument('--completion-sha256', required=True)
    main(p.parse_args())
