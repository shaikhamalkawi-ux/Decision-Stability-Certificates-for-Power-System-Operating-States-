"""Closed-output backend/transport/ledger audit, separate from certificate math.

Drafted before closure. No producer/encoder import, optimizer, model construction,
seed q/control reconstruction, or exact master nomination replay.
"""
import argparse
import csv
from datetime import datetime, timezone
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ARM = ROOT / 'results/research_next/common_refinement_batch'
PRE, RUN = ARM / 'prepared', ARM / 'run01'
FREEZE = '7642265df13848db01ad0627381c6e294ddea30569a5dbc2b344e2e952372b85'
MANIFEST = '34311c0d425e453a24781079a007eef2369bb8cbf2e3e75eab13f523498916ef'
SOURCE = 'f7f79ecca154169832c8739d9c17889c5c5993aa460f6d528d6f115c60018371'
GO = 'e63f49851b1260c63b80a6a9855a4061bde5a87e2aff2aa4826462c02bf2dc2c'
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
    """Recompute dyadic recipe and actual inequality without the encoder helper."""
    terms = proof['state_terms']
    source = {j - START: frac(a) for j, a in terms}
    need(len(source) == len(terms) and all(0 <= j < NB for j in source), 'Complete supplied sparse coordinates')
    need(all(source.values()) and list(source) == sorted(source), 'Exact nonzero source support')
    b = frac(proof['cut_rhs'])
    need(encoding['full_dimension'] == NB and encoding['require_exclusion'] is require_exclusion, 'Encoding domain/mode')
    need(encoding['coordinate_count'] == len(source) and encoding['implicit_exact_zeros']['count'] == NB-len(source), 'Exact-zero completion count')
    need(encoding['source_rhs'] == pair(b) and encoding['upper'] == 'positive_infinity', 'Source RHS and unbounded upper')
    need(encoding['eligible_for_backend'] is True and encoding['constant_row'] is False, 'Nonconstant admitted requested row')
    exponent = encoding['scale_exponent_2']
    need(type(exponent) is int, 'Integer dyadic exponent')
    scale = Q(2**exponent) if exponent >= 0 else Q(1, 2**(-exponent))
    maximum = max(abs(x) for x in source.values())
    need(frac(encoding['scale']) == scale and scale/2 < maximum <= scale, 'Unique smallest enclosing dyadic scale')
    beta = b/scale
    need(frac(encoding['scaled_rhs']) == beta, 'Scaled RHS')
    requested = {}
    residual = Q(0)
    need([x['coordinate'] for x in encoding['coefficients']] == list(source), 'All encoded source terms in order')
    for x in encoding['coefficients']:
        j = x['coordinate']; a = source[j]; alpha = a/scale
        need(frac(x['source']) == a and frac(x['scaled']) == alpha, 'Source/scaled coefficient relation')
        value = finite_hex(x['encoded_hex'])
        need(value == float(alpha) and (value != 0 or alpha == 0), 'One binary64 conversion; no nonzero underflow')
        error = Q(value)-alpha
        need(frac(x['error']) == error, 'Exact requested coefficient error')
        requested[j] = value
        residual += min(error, Q(0))
    target = beta+residual
    nearest = float(target)
    need(math.isfinite(nearest) and (nearest != 0 or target == 0), 'Supported finite endpoint conversion')
    step = Q(nearest) > target
    down = math.nextafter(nearest, -math.inf) if step else nearest
    need(math.isfinite(down) and (down != 0 or target == 0), 'Supported downward endpoint')
    need(encoding['lower'] == {'nearest_hex': nearest.hex(), 'nextafter_negative_infinity': step,
                             'encoded_hex': down.hex(), 'error': pair(Q(down)-target)}, 'Frozen endpoint rounding recipe')
    need(frac(encoding['residual_box_lower']) == residual and frac(encoding['requested_endpoint_target']) == target, 'Exact requested finite-box correction')
    need(encoding['extra_binary_tau'] == encoding['alternative_scales'] == 0, 'No alternate recipe/tau')
    actual = list(actual)
    need(len({j for j, x in actual}) == len(actual), 'Unique actual coordinates')
    observed = {}
    for j, x in actual:
        need(type(j) is int and 0 <= j < NB and math.isfinite(x), 'Actual domain')
        need(j in source or x == 0, 'No nonzero actual term on implicit source zero')
        observed[j] = x
    # Omitted supplied coordinates are zero, not silently copied from requested terms.
    actual_residual = sum((min(Q(observed.get(j, 0.))-a/scale, Q(0)) for j, a in source.items()), Q(0))
    actual_limit = beta+actual_residual
    need(math.isfinite(lower) and Q(lower) <= actual_limit, 'Actual outward implication on the full binary box')
    origin = encoding['origin']
    original_gap = actual_gap = None
    if origin is not None:
        need(len(origin) == NB and all(type(x) is int and x in (0, 1) for x in origin), 'Complete exact origin')
        original_gap = b-sum((a*origin[j] for j, a in source.items()), Q(0))
        actual_gap = Q(lower)-sum((Q(observed.get(j, 0.))*origin[j] for j in source), Q(0))
        need(frac(encoding['original_origin_gap']) == original_gap, 'Original origin gap')
    if require_exclusion:
        need(origin is not None and original_gap > 0 and actual_gap > 0, 'Both exact and actual strict origin exclusion')
    else:
        need(origin is None, 'Seeds do not require an origin')
    return {'outward_valid': True, 'actual_residual_box_lower': pair(actual_residual),
            'actual_outward_lower_limit': pair(actual_limit), 'outward_slack': pair(actual_limit-Q(lower)),
            'original_origin_gap': pair(original_gap) if original_gap is not None else None,
            'actual_origin_gap': pair(actual_gap) if actual_gap is not None else None,
            'strict_origin_exclusion_required': require_exclusion}


def master_readback(folder, request, base):
    binding(request['model'])
    for x in request['bindings']:
        binding(x)
    model = zipped(request['model']['path'])
    need(model['boxes'] == base['boxes'] and model['rows'][:17212] == base['rows'], 'Unchanged full base master')
    need({k: v for k, v in model.items() if k != 'rows'} == {k: v for k, v in base.items() if k != 'rows'}, 'Only appended rows')
    records = request['cuts']
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
        proof = zipped(record['proof']['path']); encoding = zipped(record['encoding']['path'])
        row = model['rows'][17212+i]
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


def array(v, z, name):
    a = z[name]
    return v.vector(a, ('<f8', '<i8', '<i4', '|u1'), a['shape'][0], name)


def lp_readback(v, folder, request, original, mask, inherited_phase):
    values = request['state_values']
    need(len(values) == NB and all(type(x) is int and x in (0, 1) for x in values), 'Full prescribed bits')
    binding(request['nominee'])
    need(read(request['nominee']['path'])['values'] == values, 'Nominee binding')
    fixed = read(folder/'fixed_schedule.json')
    need(fixed == {'fixed_columns': [{'column': START+j, 'value': x} for j, x in enumerate(values)],
                   'state_sha256': hashlib.sha256(bytes(values)).hexdigest()}, 'All original fixed states')
    if request['kind'] == 'recourse':
        names = ('data', 'indices', 'indptr', 'shape', 'column_lower', 'column_upper', 'row_lower', 'row_upper', 'objective', 'original_integrality', 'backend_integrality')
        z = v.read_npz(folder/'backend_readback.npz', names)
        lo, hi = list(original.lower), list(original.upper)
        for j, x in enumerate(values):
            need(lo[START+j] <= x <= hi[START+j], 'Within original bit box')
            lo[START+j] = hi[START+j] = float(x)
        want = {'data': original.data, 'indices': original.indices, 'indptr': original.indptr,
                'shape': (original.rows, original.cols), 'column_lower': tuple(lo), 'column_upper': tuple(hi),
                'row_lower': original.row_lower, 'row_upper': original.row_upper, 'objective': (0.,)*original.cols,
                'original_integrality': mask, 'backend_integrality': (0,)*original.cols}
        fb = v.read_npz(folder/'fixed_bounds.npz', ('column_lower', 'column_upper'))
        need(array(v, fb, 'column_lower') == tuple(lo) and array(v, fb, 'column_upper') == tuple(hi), 'Only state boxes changed')
    else:
        names = ('data', 'indices', 'indptr', 'shape', 'column_lower', 'column_upper', 'row_lower', 'row_upper', 'objective', 'integrality')
        z = v.read_npz(folder/'backend_readback.npz', names)
        phase = v.read_npz(folder/'phase_model.npz', names)
        want = {name: array(v, inherited_phase, name) for name in names}
        for name in ('column_lower', 'column_upper'):
            xs = list(want[name])
            xs[START:STOP] = [float(x) for x in values]
            want[name] = tuple(xs)
        for name in names:
            need(array(v, phase, name) == want[name], 'No phase template change beyond prescribed bits: '+name)
    for name in names:
        need(array(v, z, name) == want[name], 'Every LP readback coefficient/domain/objective value: '+name)
    meta = read(folder/'backend_readback.json')
    need(meta['readback_sha256'] == sha(folder/'backend_readback.npz') and meta['options'] == LP_OPTIONS, 'LP binding/fixed options')
    if request['kind'] == 'phase1':
        need(meta['phase_model_sha256'] == sha(folder/'phase_model.npz'), 'Phase model identity')
    return {'kind': request['kind'], 'rows': want['shape'][0], 'columns': want['shape'][1],
            'coefficient_uses': len(want['data']), 'full_readback': True, 'prescribed_original_bits': NB}


def main(args):
    started = time.perf_counter()
    report_path = OUT/'postrun_transport_review.json'
    need(not report_path.exists(), 'One closed independent review')
    pinpaths = {PRE/'prepared_freeze.json': FREEZE, PRE/'input_manifest.json': MANIFEST,
                ROOT/'src/researchnext_common_refinement_batch.py': SOURCE,
                ARM/'ROOT_EXECUTION_GO.json': GO, ARM/'producer_output_inventory.csv': args.inventory_sha256,
                RUN/'completion.json': args.completion_sha256,
                ROOT/'src/research8h_standalone_verify.py': KERNEL}
    for p, expected in pinpaths.items():
        need(sha(p) == expected, 'External trusted pin: '+str(p))
    authorization = read(ARM/'ROOT_EXECUTION_GO.json')
    for rel, expected in authorization['source_and_transport'].items():
        need(sha(ROOT/rel) == expected, 'Explicit GO transport pin')
    need(authorization['final_transport_rehash_required_against_this_record'] is True, 'Final transport gate authority')
    items = read(PRE/'input_manifest.json')['files']
    need(len(items) == 355, '355 inputs')
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
    spec = importlib.util.spec_from_file_location('batch_transport_npz_decoder', ROOT/'src/research8h_standalone_verify.py')
    v = importlib.util.module_from_spec(spec); sys.modules[spec.name] = v; spec.loader.exec_module(v)
    original = v.load_model(PRE/'joint')
    mask = tuple(v.vector(v.read_npz(PRE/'joint/integrality.npz', ('integrality',))['integrality'], ('|u1',), original.cols, 'original mask'))
    need((original.rows, original.cols, len(original.data)) == (69362, 33936, 291176), 'Original model dimensions')
    need(mask == tuple(int(START <= j < STOP) for j in range(original.cols)), 'Original full mask')
    phase_names = ('data', 'indices', 'indptr', 'shape', 'column_lower', 'column_upper', 'row_lower', 'row_upper', 'objective', 'integrality')
    inherited_phase = v.read_npz(PRE/'phase_model.npz', phase_names)
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
    need(len(workers) <= 25 and len(attempts) <= 24, 'Finite call bounds')
    details = []; deadlines = set(); solver_seconds = 0.; overrun = 0.; worker_kinds = []
    for launch_path in workers:
        folder = launch_path.parent
        launch, request = read(launch_path), read(folder/'request.json')
        kind = request['kind']; worker_kinds.append(kind)
        need(kind in LIMITS and 1 <= request['round'] <= 8, 'Prescribed worker kind/round')
        need(request['source_sha256'] == SOURCE and request['freeze_sha256'] == FREEZE, 'Worker frozen authority')
        need(launch['request_sha256'] == sha(folder/'request.json') and launch['remaining'] >= LIMITS[kind]+5, 'Request binding/start guard')
        need(Path(request['folder']).resolve() == folder.resolve() and Path(request['private']).is_relative_to(ROOT/'.work/researchnext_common_refinement_batch/run01'), 'Unique confined paths')
        command = launch['command']
        need(command[1] == '-I' and Path(command[2]).resolve() == (ROOT/'src/researchnext_common_refinement_batch.py').resolve(), 'Isolated frozen worker command')
        need(command[3:] == ['--worker', '--expected-freeze-sha256', FREEZE, '--request', str((folder/'request.json').resolve()), '--expected-request-sha256', sha(folder/'request.json')], 'Complete command authority')
        deadlines.add(request['deadline_monotonic'])
        closed = read(folder/'worker_closed.json')
        detail = {'folder': str(folder.relative_to(RUN)), 'kind': kind, 'timed_out': closed['timed_out']}
        has_go = (folder/'worker_go.json').exists()
        if has_go:
            ready, go = read(folder/'worker_ready.json'), read(folder/'worker_go.json')
            owned = read(folder/'owned_process_chain.json')
            need(ready['token'] == request['token'] and ready['request_sha256'] == sha(folder/'request.json') and ready['source_sha256'] == SOURCE, 'Authenticated actual worker')
            need(go == {'token': request['token'], 'request_sha256': sha(folder/'request.json'), 'ownership_admitted': True}, 'Exact ownership GO')
            need(owned['launcher_pid'] == closed['launcher_pid'] and owned['actual_pid'] == ready['pid'] and owned['actual_parent_pid'] == ready['parent_pid'], 'Saved actual process chain')
            pids = [x['pid'] for x in owned['processes']]
            expected_pids = [owned['launcher_pid']] + ([] if ready['pid'] == owned['launcher_pid'] else [ready['pid']])
            need(pids == expected_pids and owned['job_kill_on_close'] and all(type(x['creation_filetime']) is int and x['creation_filetime'] > 0 for x in owned['processes']), 'Exact owned handles/creation identities')
            need(ready['pid'] == owned['launcher_pid'] or ready['parent_pid'] == owned['launcher_pid'], 'Direct authenticated launcher chain')
            detail['owned_processes'] = owned['processes']
            detail['owned_handles_reaped'] = closed.get('owned_handles_reaped')
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
        elif (folder/'backend_readback.npz').exists():
            detail['backend'] = lp_readback(v, folder, request, original, mask, inherited_phase)
        if (folder/'completion.json').exists():
            wc = read(folder/'completion.json')
            need(closed.get('completion') == wc, 'Closed worker completion identity')
            if wc['final_admission']['accepted_common']:
                need(kind == 'recourse' and wc['final_admission']['phase_deadline_met'], 'Only in-time recourse can claim full positive')
        if kind == 'transport_only':
            need(not (folder/'optimizer_attempt.json').exists(), 'No terminal optimizer')
        details.append(detail)
    need(len(deadlines) <= 1, 'Shared global monotonic deadline')
    ledger = completion['ledger']
    need(result['ledger'] == ledger, 'Final ledgers agree')
    need(ledger['worker_launch_attempts'] == len(workers) and ledger['optimizer_attempt_records'] == len(attempts) and ledger['optimizer_returned'] == len(returns), 'Complete attempt/return counts')
    need(ledger['attempts_cancelled_before_optimizer'] == len(cancelled) and ledger['entered_calls_from_return_or_error'] == len(returns)+len(errors), 'Cancelled/entered distinction')
    need(len(ledger['calls']) == len(attempts), 'Full solver ledger denominator')
    for rec, path in zip(ledger['calls'], attempts):
        binding(rec['attempt']); need(Path(rec['attempt']['path']).resolve() == path.resolve(), 'Every actual attempt bound')
    for rec in ledger['worker_closures']:
        binding(rec)
    need(result['all_frozen_bytes_unchanged'] and completion['all_frozen_bytes_unchanged'], 'Producer final input validation')
    need(result['provisional_until_completion'] and result['no_global_infeasibility_claim'] and result['one_adaptive_trajectory'], 'Scientific scope')
    need(completion['no_retry'] and completion['no_ninth_nomination'], 'No additional trajectory')
    elapsed = completion['phase_seconds']
    need(elapsed >= solver_seconds and completion['phase_soft_overrun'] == max(0., elapsed-2400.), 'Full phase/call accounting')
    final = completion['final_admission']
    need(final['common_verdict'] == ('VERIFIED_EXPANDED_COMMON_COMMITMENT' if final['accepted_common'] else 'UNKNOWN'), 'No numerical global negative')
    if final['accepted_common']:
        need(final['phase_deadline_met'] and elapsed <= 2400. and result['accepted_common'], 'Authoritative in-time positive')
    if deadlines:
        need(final['phase_deadline_met'] == (final['admission_monotonic'] <= next(iter(deadlines))), 'Final sampled deadline')
    for x in items+outputs:
        binding(x)
    for p, expected in pinpaths.items():
        need(sha(p) == expected, 'Closing external pin including transport files')
    report = {'status': 'PASS_INDEPENDENT_BACKEND_TRANSPORT_AND_LEDGER',
              'utc': datetime.now(timezone.utc).isoformat(), 'source_sha256': sha(__file__),
              'elapsed_seconds': time.perf_counter()-started, 'input_bindings': 355,
              'producer_outputs': len(outputs), 'run_files': len(in_run), 'all_pinned_bytes_unchanged': True,
              'external_final_transport_gate': {'freeze_sha256': FREEZE, 'manifest_sha256': MANIFEST, 'GO_sha256': GO, 'pass': True},
              'workers': details, 'worker_launches': len(workers), 'optimizer_attempts': len(attempts),
              'optimizer_returned': len(returns), 'optimizer_errors': len(errors), 'cancelled_before_call': len(cancelled),
              'returned_solver_seconds': solver_seconds, 'solver_soft_overrun_seconds': overrun, 'phase_seconds': elapsed,
              'producer_common_verdict': final['common_verdict'], 'scientific_certificate_nominee_positive_review': 'Separate Find audit required; not replayed here.',
              'encoder_author_disclosed': True, 'encoder_helper_imported': False,
              'actual_outward_inequalities_independently_recomputed': True,
              'pinned_stdlib_decoder_reused': KERNEL, 'producer_imports': 0, 'optimizer_calls_by_reviewer': 0,
              'private_logs_read': False, 'new_candidates_or_coefficients': 0,
              'limitations': ['Recorded actual owned-process behavior only; no claim of unexercised timeout termination.',
                              'Nominal recourse inability is not expanded-model infeasibility.',
                              'Exact source-row proof and full-positive admission require the complementary mathematical review.']}
    with report_path.open('x', encoding='utf-8') as f:
        json.dump(report, f, indent=2, allow_nan=False); f.write('\n')
    print(json.dumps({'status': report['status'], 'sha256': sha(report_path), 'elapsed_seconds': report['elapsed_seconds']}))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--inventory-sha256', required=True)
    p.add_argument('--completion-sha256', required=True)
    main(p.parse_args())
