"""Replay only saved partial construction and closure; no new candidate or solver."""
import hashlib
import json
import time
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path

ARM = Path(__file__).resolve().parent
PRE, RUN = ARM / 'prepared', ARM / 'run01'
FREEZE = '37dbfd382db1a8bf4a7905d2e486a606d9b94245f75d6d3e7c32a57b5df77756'
MANIFEST = 'c8f40dc622a042e27b9a80f8fed02583881e0228445104ccb39eaaaf26933164'
REPORT = ARM / 'INDEPENDENT_POSTRUN_REVIEW.json'


def need(ok, label):
    if not ok:
        raise ValueError(label)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def binding(path):
    path = Path(path)
    data = path.read_bytes()
    return {'path': str(path), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def audit_entry(entry):
    need(binding(entry['path']) == entry, 'Unchanged bound file ' + entry['path'])


def pack(value):
    return {'numerator': str(value.numerator), 'denominator': str(value.denominator), 'approximate': float(value)}


def parse(value):
    if value is None:
        return None
    exact = F(int(value['numerator']), int(value['denominator']))
    need(str(exact.numerator) == value['numerator'] and str(exact.denominator) == value['denominator'], 'Canonical rational')
    need(float(exact) == value['approximate'], 'Consistent display only')
    need(abs(exact.numerator).bit_length() <= 512 and exact.denominator.bit_length() <= 512, 'Saved bit guard')
    return exact


def main():
    started = time.perf_counter()
    need(not REPORT.exists(), 'One independent replay')
    need(sha(PRE / 'freeze.json') == FREEZE and sha(PRE / 'manifest.json') == MANIFEST, 'External freeze pins')
    manifest = read(PRE / 'manifest.json')
    inputs = manifest['inputs'] + list(manifest['copies'].values())
    need(len(manifest['inputs']) == 69 and len(manifest['copies']) == 11, 'Input denominator')
    for entry in inputs:
        audit_entry(entry)
    names = {'started.json', 'construction.json', 'result.json', 'completion.json'}
    need({p.name for p in RUN.iterdir()} == names, 'Exactly four closed null files')
    snapshot = [binding(RUN / name) for name in sorted(names)]
    marker, construction, result, completion = [read(RUN / name) for name in ('started.json', 'construction.json', 'result.json', 'completion.json')]
    need(marker['freeze_sha256'] == FREEZE and marker['optimizer_calls'] == 0 and marker['candidate_limit'] == 1, 'One zero-optimizer attempt')
    need(construction['stage'] == 'system_balance' and construction['complete'] is False and construction['construction_failure'] == 'C outside nominal box', 'Recorded construction stop')
    need(construction['denominator_ceiling_Q'] == 1000000 and 'intervals' not in construction and 'row_counts' not in construction, 'No reserve/intersection stage')
    need(result == {'status': 'NO_NOMINAL_WITNESS_FROM_THIS_CONSTRUCTION', 'nominal_feasibility': 'UNKNOWN', 'optimizer_calls': 0, 'Julia_calls': 0, 'candidates': 1, 'old_point_unchanged': True, 'exact_optimality_claim': False}, 'Conservative null verdict')
    need(completion['status'] == 'CLOSED_PENDING_INDEPENDENT_REVIEW' and completion['optimizer_calls'] == 0 and completion['candidate_attempts'] == 1, 'Closed call ledger')
    need(completion['all_inputs_unchanged'] is True and completion['no_retry'] is True and completion['final_completion_write_excluded'] is True, 'Closing scope')
    need(0 <= completion['elapsed_seconds'] <= 90, 'Soft phase completed within limit')
    need(datetime.fromisoformat(completion['utc']) >= datetime.fromisoformat(marker['utc']), 'Timestamp order')
    model, normal, old = [read(PRE / name) for name in ('model.json', 'normal.json', 'candidate.json')]
    columns = model['columns']
    index = {c['name']: j for j, c in enumerate(columns)}
    point = list(map(parse, construction['partial_or_complete_point']))
    need(len(index) == len(columns) == len(point) == len(old) == 2472, 'Complete partial-vector shape')
    need(model['variant'] == 'native_penalized' and model['order'] == list(range(24)), 'Only identity model')
    at = lambda f, g, t, k=None: index[f'{f}:{g}:{t}' + ('' if k is None else f':{k}')]
    bits = [j for j, c in enumerate(columns) if c['binary']]
    need(len(bits) == 960, 'All original binaries')
    for j in bits:
        need(point[j] == F(old[j]) and point[j] in (0, 1), 'Unchanged exact bit')
    q_count = segment_count = 0
    # This uses Python's published Fraction routine to check the one saved rule,
    # not an alternate denominator, candidate or independent-algorithm claim.
    for g in normal['units']:
        for t in range(24):
            j = at('Q', g['name'], t)
            need(point[j] == F(old[j]).limit_denominator(1000000), 'Saved bounded-denominator Q')
            q_count += 1
            remaining = point[j]
            need(remaining >= 0, 'Constructed Q domain')
            for k, width in enumerate(g['widths']):
                allowance = F(width) * point[at('U', g['name'], t)]
                need(allowance >= 0, 'Segment allowance')
                saved = point[at('S', g['name'], t, k)]
                need(saved == min(remaining, allowance), 'Saved greedy segment')
                remaining -= saved
                segment_count += 1
            need(remaining == 0, 'Exact complete segment allocation')
            need(point[at('R', g['name'], t)] is None, 'No reserve assignment')
    need(q_count == 240 and segment_count == 960, 'Fixed construction denominator')
    failed = None
    hours = []
    for t in range(24):
        ci, fi, ni = (at(f, 'system', t) for f in ('C', 'F', 'N'))
        if failed is not None:
            need(all(point[j] is None for j in (ci, fi, ni)), 'No later-hour construction')
            continue
        need(point[fi] == point[ni] == 0, 'Assigned F and N zero')
        contributions = []
        for g in normal['units']:
            u = point[at('U', g['name'], t)]
            q = point[at('Q', g['name'], t)]
            contribution = F(g['pmin']) * u + q
            contributions.append({'unit': g['name'], 'U': int(u), 'pmin': pack(F(g['pmin'])), 'Q': pack(q),
                                  'old_Q': pack(F(old[at('Q', g['name'], t)])), 'production': pack(contribution)})
        production = sum((F(g['pmin']) * point[at('U', g['name'], t)] + point[at('Q', g['name'], t)] for g in normal['units']), F(0))
        exact_c = F(normal['load'][t]) - production
        need(point[ci] == exact_c, 'Saved exact C balance')
        lo, hi = F(columns[ci]['lower']), F(columns[ci]['upper'])
        violation = max(F(0), lo - exact_c, exact_c - hi)
        hours.append({'hour_zero_based': t, 'hour_one_based': t + 1, 'C': pack(exact_c), 'lower': pack(lo), 'upper': pack(hi), 'violation': pack(violation)})
        if violation:
            failed = {'hour_zero_based': t, 'hour_one_based': t + 1, 'column': ci, 'column_name': columns[ci]['name'],
                      'load': pack(F(normal['load'][t])), 'total_production': pack(production), 'C': pack(exact_c),
                      'lower': pack(lo), 'upper': pack(hi), 'violation': pack(violation),
                      'side': 'lower' if exact_c < lo else 'upper', 'unit_contributions': contributions}
    need(failed is not None, 'An actual first failed C exists')
    assigned = sum(value is not None for value in point)
    need(assigned == 2166 and assigned == 2160 + 3 * (failed['hour_zero_based'] + 1), 'Exact early-stop assignment count')
    for entry in inputs + snapshot:
        audit_entry(entry)
    need(sha(PRE / 'freeze.json') == FREEZE and sha(PRE / 'manifest.json') == MANIFEST, 'Closing transport')
    out = {'status': 'PASS', 'utc': datetime.now(timezone.utc).isoformat(), 'reviewer_sha256': sha(__file__),
           'elapsed_seconds': time.perf_counter() - started, 'source_sha256': manifest['source_sha256'],
           'freeze_sha256': FREEZE, 'manifest_sha256': MANIFEST, 'input_bindings': 69, 'copies': 11,
           'producer_outputs': snapshot, 'unchanged_after': True, 'full_original_bits': 960,
           'verified_Q': q_count, 'verified_segments': segment_count, 'assigned_coordinates': assigned,
           'unset_coordinates': len(point) - assigned, 'completed_system_hours': hours,
           'first_failed_C': failed, 'producer_elapsed_seconds': completion['elapsed_seconds'],
           'nominal_feasibility': 'UNKNOWN', 'interpretation': 'Only this fixed construction failed; no nominal infeasibility certificate.',
           'new_candidates': 0, 'alternative_denominators': 0, 'optimizer_calls': 0, 'Julia_calls': 0,
           'producer_imports': 0, 'full_native_point_replay': False,
           'algorithm_reuse': 'Fraction arithmetic and limit_denominator standard library only; independently authored checks of saved partial data.'}
    with REPORT.open('x', encoding='utf-8') as stream:
        json.dump(out, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'status': 'PASS', 'report_sha256': sha(REPORT), 'hour_zero_based': failed['hour_zero_based'],
                      'violation': failed['violation'], 'elapsed_seconds': out['elapsed_seconds']}))


if __name__ == '__main__':
    main()
