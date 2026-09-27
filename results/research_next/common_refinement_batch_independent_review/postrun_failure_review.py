"""Closed zero-optimizer failure and requested-encoding review; no solver imports."""
import csv
from datetime import datetime, timezone
from fractions import Fraction as F
import gzip
import hashlib
import json
import math
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ARM = ROOT/'results/research_next/common_refinement_batch'
PRE, RUN = ARM/'prepared', ARM/'run01'
PINS = {
    PRE/'prepared_freeze.json': '7642265df13848db01ad0627381c6e294ddea30569a5dbc2b344e2e952372b85',
    PRE/'input_manifest.json': '34311c0d425e453a24781079a007eef2369bb8cbf2e3e75eab13f523498916ef',
    ARM/'ROOT_EXECUTION_GO.json': 'e63f49851b1260c63b80a6a9855a4061bde5a87e2aff2aa4826462c02bf2dc2c',
    ARM/'producer_output_inventory.csv': '8c0faa1048a6b5d232feb58a75d921fb287abc87c607d71f492d7824739b7f83',
    RUN/'completion.json': 'b445ba6868a2ee044a9dbe1c019bcf2e17dd7ed0d947ef6b08e1b117a0f3886f',
    ARM/'READOUT.md': '74a9c3319ba56b864922b6f041365342ee378634ec3f3c42a4a9d8db2cc81093',
    OUT/'prepared_review.json': '7971a2bfe6c64e183941b6612aa5bec7202e9596dad6867ad330db9cabda0bf3',
}


def need(x, why):
    if not x:
        raise ValueError(why)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))


def gz(p):
    with gzip.open(p, 'rt', encoding='utf-8') as f:
        return json.load(f)


def bind(x):
    b = Path(x['path']).read_bytes()
    need(len(b) == x['bytes'] and hashlib.sha256(b).hexdigest() == x['sha256'], 'Frozen file: '+x['path'])


def q(x):
    f = F(int(x[0]), int(x[1]))
    need(x == [str(f.numerator), str(f.denominator)], 'Canonical rational')
    return f


def pair(x):
    return [str(x.numerator), str(x.denominator)]


def encoding_check(proof, e):
    """Necessary requested row: L <= beta + sum min(a_float-alpha,0)."""
    terms = proof['state_terms']; a = {j-6888: q(c) for j, c in terms}; b = q(proof['cut_rhs'])
    need(len(a) == len(terms) and list(a) == sorted(a) and all(0 <= j < 12096 and c != 0 for j, c in a.items()), 'Complete supplied nonzero state support')
    need(e['schema'] == 'exact_binary_cut_transport_v1' and e['full_dimension'] == 12096 and e['coordinate_count'] == len(a), 'Complete encoding dimensions')
    need(e['implicit_exact_zeros']['count'] == 12096-len(a), 'Exact zero-completion denominator')
    need(e['origin'] is None and e['require_exclusion'] is False and e['source_rhs'] == pair(b), 'Seed source/no origin-exclusion requirement')
    need(e['eligible_for_backend'] and not e['constant_row'] and e['disposition'] == 'READY_FOR_BACKEND_READBACK', 'Requested row eligibility only')
    k = e['scale_exponent_2']; need(type(k) is int, 'Integral scale exponent')
    s = F(1 << k) if k >= 0 else F(1, 1 << (-k))
    need(q(e['scale']) == s and s/2 < max(map(abs, a.values())) <= s, 'Smallest dyadic scale by exact comparison')
    beta = b/s; need(q(e['scaled_rhs']) == beta, 'Scaled exact RHS')
    need([r['coordinate'] for r in e['coefficients']] == list(a), 'All explicit source coefficients')
    err = F(0); numeric = []
    for r in e['coefficients']:
        j = r['coordinate']; alpha = a[j]/s; f = float.fromhex(r['encoded_hex'])
        need(math.isfinite(f) and f != 0 and f == float(alpha), 'Finite nonzero one-round coefficient')
        need(q(r['source']) == a[j] and q(r['scaled']) == alpha and q(r['error']) == F(f)-alpha, 'Exact scaled/error relation')
        err += min(F(f)-alpha, F(0)); numeric.append([j, r['encoded_hex']])
    endpoint = beta+err; nearest = float(endpoint)
    need(math.isfinite(nearest) and (nearest != 0 or endpoint == 0), 'Supported endpoint conversion')
    step = F(nearest) > endpoint
    lower = math.nextafter(nearest, -math.inf) if step else nearest
    need(math.isfinite(lower) and (lower != 0 or endpoint == 0), 'Supported downward endpoint')
    need(e['lower'] == {'nearest_hex': nearest.hex(), 'nextafter_negative_infinity': step,
                       'encoded_hex': lower.hex(), 'error': pair(F(lower)-endpoint)}, 'Exact declared downward rounding')
    need(q(e['residual_box_lower']) == err and q(e['requested_endpoint_target']) == endpoint, 'Exact residual box correction')
    need(F(lower) <= endpoint and e['upper'] == 'positive_infinity', 'Requested outward implication on [0,1]^12096')
    need(e['extra_binary_tau'] == e['alternative_scales'] == 0 and all(e[k] is None for k in ('original_origin_gap','scaled_origin_gap','requested_origin_gap')), 'No extra tau/origin computation')
    return {'source_terms': len(a), 'scale_exponent': k, 'downward_step': step,
            'outward_slack': pair(endpoint-F(lower)), 'necessary_requested_row': True,
            'actual_backend_transport': 'NOT_PERFORMED'}


def main():
    started = time.perf_counter(); target = OUT/'postrun_failure_review.json'
    need(not target.exists(), 'One closed independent review')
    for p, h in PINS.items(): need(sha(p) == h, 'External trusted closure pin')
    items = read(PRE/'input_manifest.json')['files']; need(len(items) == 355, '355 frozen bindings')
    for x in items: bind(x)
    with (ARM/'producer_output_inventory.csv').open(encoding='utf-8-sig', newline='') as f: inv = list(csv.DictReader(f))
    need(len(inv) == len({x['path'] for x in inv}) == 688, '688 unique closed outputs')
    outputs = [{'path': str(ROOT/x['path']), 'bytes': int(x['bytes']), 'sha256': x['sha256']} for x in inv]
    for x in outputs: bind(x)
    runfiles = {str(Path(x['path']).relative_to(RUN)) for x in outputs if Path(x['path']).is_relative_to(RUN)}
    need(runfiles == {str(p.relative_to(RUN)) for p in RUN.rglob('*') if p.is_file()}, 'Complete immutable run inventory')
    go = read(ARM/'ROOT_EXECUTION_GO.json')
    for rel, h in go['source_and_transport'].items(): need(sha(ROOT/rel) == h, 'Closing explicitly required external transport identity')
    need(go['final_transport_rehash_required_against_this_record'] and go['producer_acceptance_provisional_until_independent_final_checks'], 'Final transport gate')
    result = read(RUN/'result.json'); completed = read(RUN/'completion.json'); start = read(RUN/'execution_started.json')
    folder = RUN/'round_01/master'; request = read(folder/'request.json'); ready = read(folder/'worker_ready.json')
    launch = read(folder/'worker_launch_attempt.json'); closed = read(folder/'worker_closed.json')
    need(start['pid'] == 40488 and start['parent_pid'] == 67748 and start['phase_seconds'] == 2400., 'Sole controller record')
    need(request['kind'] == 'master' and request['round'] == 1 and request['freeze_sha256'] == PINS[PRE/'prepared_freeze.json'], 'Only first master request')
    need(ready['pid'] == 4940 and ready['parent_pid'] == closed['launcher_pid'] == 20732, 'Recorded direct launcher/actual chain')
    need(ready['token'] == request['token'] and ready['request_sha256'] == launch['request_sha256'] == sha(folder/'request.json'), 'Authenticated ready/request')
    need(ready['source_sha256'] == request['source_sha256'] == start['source_sha256'] == go['source_and_transport']['src/researchnext_common_refinement_batch.py'], 'Frozen source throughout')
    need(launch['command'] == [str(ROOT/'.work/scip_capability_env01/Scripts/python.exe'), '-I', str(ROOT/'src/researchnext_common_refinement_batch.py'),
        '--worker', '--expected-freeze-sha256', PINS[PRE/'prepared_freeze.json'], '--request', str(folder/'request.json'), '--expected-request-sha256', sha(folder/'request.json')], 'Exact sole frozen command')
    need(launch['remaining'] >= 125 and launch['not_optimizer_attempt'], 'Launch guard, not solver entry')
    forbidden = ('worker_go.json','owned_process_chain.json','optimizer_attempt.json','optimizer_returned.json',
                 'optimizer_error.json','master_backend_readback.json.gz','dynamic_model_binding.json','raw_solution.npz','exact_master_admission.json','completion.json')
    need(all(not (folder/x).exists() for x in forbidden), 'Ownership not admitted; no backend/call/candidate evidence')
    need(len(list(RUN.glob('round_*/*/worker_launch_attempt.json'))) == 1 and len(list(RUN.glob('round_*'))) == 1, 'One worker/round only')
    need(not list(RUN.rglob('optimizer_attempt.json')) and not list(RUN.rglob('*backend_readback*')), 'Zero optimizer and actual backend readbacks')
    need(closed['error_type'] == 'ValueError' and closed['error'] == 'Assign exact process to owned job' and closed['optimizer_attempted'] == 0 and not closed['timed_out'], 'Closed assignment failure boundary')
    need(closed['owned_handles_reaped'] is True and 0 <= closed['elapsed_seconds'] < completed['phase_seconds'], 'Observed error cleanup/timing')
    ledger = completed['ledger']; need(result['ledger'] == ledger, 'Shared complete ledger')
    need(ledger['worker_launch_attempts'] == 1 and all(ledger[k] == 0 for k in ('optimizer_attempt_records','optimizer_returned','attempts_cancelled_before_optimizer','entered_calls_from_return_or_error')) and ledger['calls'] == [], 'Zero optimizer attempts/returns')
    need(len(ledger['worker_closures']) == 1, 'One worker closure'); bind(ledger['worker_closures'][0])
    need(result['seed_count'] == result['total_cut_records'] == 336 and result['new_cut_count'] == result['completed_rounds'] == result['cuts_with_completed_actual_transport'] == 0, 'Exact zero-scientific-search boundary')
    need(result['terminal_cut_numeric_transport'] == 'NOT_ADMITTED' and result['no_global_infeasibility_claim'] and result['provisional_until_completion'], 'Requested encoding not backend evidence')
    need(result['error'] == {'stage':'round_1_master','error_type':'ValueError','message':'Assign exact process to owned job'}, 'Failure stage')
    for doc in (result, completed['final_admission']):
        need(not doc['accepted_common'] and doc['common_verdict'] == 'UNKNOWN' and doc['phase_deadline_met'], 'Conservative final scientific status')
        need(doc['admission_monotonic'] <= request['deadline_monotonic'], 'In-time sampled admission')
    need(completed['phase_seconds'] == 97.25336050003534 and completed['phase_soft_overrun'] == 0 and completed['no_retry'] and completed['no_ninth_nomination'], 'Closed phase ledger')
    process = read(ARM/'EXTERNAL_PROCESS_CLOSURE.json')
    need(process['processes'] == [{'pid': p, 'present': False} for p in (40488,67748,20732,4940)], 'All four exact recorded PIDs subsequently absent')
    transport = read(ARM/'EXTERNAL_TRANSPORT_CLOSURE.json')
    need(transport['status'] == 'PASS_EXTERNAL_TRUSTED_TRANSPORT_REHASH' and transport['controller_session'] == 88649 and transport['controller_exit_code'] == 0, 'Closed controller/external transport receipt')
    for x in transport['checks']:
        need(x['expected_sha256'] == x['actual_sha256'] == sha(ARM/x['path']) and x['bytes'] == (ARM/x['path']).stat().st_size, 'External rehash independently matched')

    cases = read(PRE/'symbolic_seed_maps.json')['cases']; records = request['cuts']
    need(len(cases) == len(records) == 336 and all(x['kind'] == 'seed' for x in records), 'All fixed seed encodings, no adaptive cuts')
    binding_model = request['model']; bind(binding_model); search = gz(binding_model['path']); base = gz(PRE/'master.json.gz')
    need(search['rows'][:17212] == base['rows'] and len(search['rows']) == 17212+336, 'Saved requested search master base+336')
    need({k:v for k,v in search.items() if k != 'rows'} == {k:v for k,v in base.items() if k != 'rows'}, 'No base domains/mask/objective changes')
    checks = []
    for i, (case, rec) in enumerate(zip(cases, records)):
        bind(rec['proof']); bind(rec['encoding'])
        prefix = f"{case['world']}_{case['hour']:03d}"
        need(Path(rec['proof']['path']) == RUN/'seeds'/f'{prefix}_proof.json.gz' and Path(rec['encoding']['path']) == RUN/'seeds'/f'{prefix}_encoding.json.gz', 'Fixed denominator/order')
        proof, encoded = gz(rec['proof']['path']), gz(rec['encoding']['path'])
        need(proof['case'] == case and proof['original_rows'] == 69362 and proof['original_columns'] == 33936 and proof['full_state_dimension'] == 12096, 'Source proof scope only; derivation independently audited elsewhere')
        check = encoding_check(proof, encoded)
        row = search['rows'][17212+i]
        need(row['family'] == 'network_seed' and row['upper'] is None and row['provenance'] == {'proof':rec['proof'],'encoding':rec['encoding'],'exact_scaled_original_row':True,'no_extra_tau':True}, 'Requested row provenance')
        need(row['terms'] == [[x['coordinate'], {'exact':x['scaled'],'binary64_hex':x['encoded_hex'],'rounding_error':x['error']}] for x in encoded['coefficients']], 'Every requested numeric term')
        beta = q(encoded['scaled_rhs']); low = float.fromhex(encoded['lower']['encoded_hex'])
        need(row['lower'] == {'exact':pair(beta),'binary64_hex':low.hex(),'rounding_error':pair(F(low)-beta)}, 'Exact master row vs outward numeric endpoint')
        checks.append({'world':case['world'],'hour':case['hour'],**check})
    seed_files = {p.name for p in (RUN/'seeds').iterdir() if p.is_file()}
    need(seed_files == {f"{c['world']}_{c['hour']:03d}_{suffix}.json.gz" for c in cases for suffix in ('proof','encoding')} | {'completion.json'}, 'All672 records+seed completion only')
    for x in items+outputs: bind(x)
    for p,h in PINS.items(): need(sha(p) == h, 'Closing trusted pin')
    report = {'status':'PASS_ZERO_OPTIMIZER_CLOSURE_AND_REQUESTED_ENCODING', 'utc':datetime.now(timezone.utc).isoformat(),
        'source_sha256':sha(__file__),'elapsed_seconds':time.perf_counter()-started,'input_bindings':355,'producer_outputs':688,'run_files':len(runfiles),
        'external_transport_gate_pass':True,'all_inputs_outputs_unchanged':True,'worker_launches':1,'optimizer_attempts':0,
        'actual_backend_readbacks':0,'master_candidates':0,'new_adaptive_cuts':0,'requested_encodings':checks,
        'requested_encoding_necessary_implications':336,'conditional_on_exact_source_cut_mathematics':True,
        'source_cut_controls_anchor_mathematics':'Separate Find review; not duplicated here.',
        'common_verdict':'UNKNOWN','failure_class':'Windows Job assignment before ownership GO and optimizer entry',
        'assignment_error_code_and_failing_pid':'NOT_RECORDED; not inferred',
        'recorded_exact_pids_later_absent':[40488,67748,20732,4940], 'optimizer_timeout_cleanup_tested':False,
        'phase_seconds':completed['phase_seconds'],'worker_seconds':closed['elapsed_seconds'],
        'source_or_encoder_imports':0,'optimizer_calls_by_reviewer':0,'private_logs_read':False,
        'encoder_authorship_disclosed':True,'own_standalone_exact_inequality_used':True,
        'no_actual_backend_or_search_claim':True,'no_common_negative_claim':True}
    with target.open('x',encoding='utf-8') as f: json.dump(report,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({'status':report['status'],'report_sha256':sha(target),'elapsed_seconds':report['elapsed_seconds']}))


if __name__ == '__main__':
    main()
