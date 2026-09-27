"""One frozen numerical basis proposal, followed by exact rational reconstruction."""
from __future__ import annotations
import argparse
from collections import Counter
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
sys.path.insert(0, str(Path(__file__).resolve().parent))
import research8h_rational_witness_check as checker

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/research8h/exact_fixed_schedule'
SOURCE = ROOT / 'results/research8h/seasonal_reference/month_01'
IDENTITY = ROOT / 'results/research8h/seasonal_transfer/january_identity'
SCHEDULE = IDENTITY / 'constructive_vector.npz'
GEN = ROOT / 'reproducibility/native_sources/rts_inputs/raw/RTS-GMLC_v0.2.3/gen.csv'
OLD_MANIFEST = SOURCE.parent / 'input_manifest.csv'
PROTOCOL = ROOT / 'docs/research8h/EXACT_FIXED_SCHEDULE_WITNESS_PROTOCOL.md'
DESIGN = ROOT / 'docs/research8h/EXACT_FIXED_SCHEDULE_WITNESS_DESIGN.md'
CHECKER = Path(checker.__file__).resolve()
TEST_REPORT = ROOT / 'results/research8h/exact_fixed_schedule_implementation_tests.json'
CUTOFF = datetime(2026, 9, 27, 4, 0, 0, tzinfo=timezone.utc)
SECONDS = 60.0
EXACT_SECONDS = 900.0
BITS = 8192
CAP = Q(23195)
EXPECTED = {
    'matrix.npz': '43eadfdf239a339757187fa4d52e786d1be7277bb93009d5ded1973523bf1386',
    'bounds.npz': 'ea8158050cefbaa9c8bdf5fd387ead50cbd9b803d378fe706a1c2522f5552518',
}
OPTIONS = dict(solver='simplex', simplex_strategy=1, presolve='off', threads=1,
               random_seed=0, time_limit=SECONDS, primal_feasibility_tolerance=1e-7,
               dual_feasibility_tolerance=1e-7, small_matrix_value=1e-12,
               log_to_console=False, output_flag=True)
require = checker.require
sha = checker.sha
rat = checker.rat
parse_rat = checker.parse_rat


class CandidateFailure(ValueError): pass
class PhaseLimit(CandidateFailure): pass
class BitLimit(CandidateFailure): pass


def save(path, value):
    with Path(path).open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2, allow_nan=False); f.write('\n')


def read(path): return checker.kernel().json_read(path)
def row_terms(m, i):
    return {m.indices[e]: Q(m.data[e]) for e in range(m.indptr[i], m.indptr[i + 1]) if m.data[e]}
def endpoint(value): return Q(value) if math.isfinite(value) else None
def encode_bound(value): return None if value is None else rat(value)
def decode_bound(value): return None if value is None else parse_rat(value)
def utc(): return datetime.now(timezone.utc)


def bit_check(value):
    numbers = (value.numerator, value.denominator) if isinstance(value, Q) else (value,)
    if any(abs(x).bit_length() > BITS for x in numbers): raise BitLimit('8192-bit exact arithmetic guard')
    return value


def guarded_clock(deadline):
    def tick():
        if time.perf_counter() >= deadline: raise PhaseLimit('900-second exact arithmetic phase')
        if utc() >= CUTOFF: raise PhaseLimit('UTC cutoff 04:00')
    return tick


def basis_endpoint(status, low, high):
    """HiGHS external statuses describe row activity, not the internal negated row variable."""
    if status == 'kBasic': raise CandidateFailure('Basic coordinate requested as nonbasic')
    if status not in ('kLower', 'kUpper', 'kZero', 'kNonbasic'): raise CandidateFailure('Unknown basis status')
    if low is not None and high is not None and low == high:
        return low  # All recognized nonbasic statuses are unambiguous on a fixed interval.
    if status == 'kLower' and low is not None: return low
    if status == 'kUpper' and high is not None: return high
    if status == 'kZero' and low is None and high is None: return Q(0)
    raise CandidateFailure('Unsupported or nonfinite indicated basis endpoint')


def exact_solve(a, rhs, tick=lambda: None):
    """Fixed row order, first nonzero pivot; integer Bareiss, then rational back substitution."""
    n = len(a)
    require(len(rhs) == n and all(len(row) == n for row in a), 'Nonsquare basis')
    if not n: return [], []
    aug = []
    for row, b in zip(a, rhs):
        tick(); values = [Q(x) for x in row] + [Q(b)]
        for x in values: bit_check(x)
        denominators = [x.denominator for x in values]
        require(all(d & (d - 1) == 0 for d in denominators), 'Basis inputs must be exact dyadics')
        scale = max(denominators)
        aug.append([bit_check(x.numerator * (scale // x.denominator)) for x in values])
    previous = 1; pivots = []
    for k in range(n - 1):
        tick()
        p = next((i for i in range(k, n) if aug[i][k]), None)
        if p is None: raise CandidateFailure('Exact singular basis')
        pivots.append(dict(column=k, chosen_current_row=p))
        if p != k: aug[k], aug[p] = aug[p], aug[k]
        pivot = aug[k][k]
        for i in range(k + 1, n):
            tick()
            for j in range(k + 1, n + 1):
                numerator = bit_check(bit_check(aug[i][j] * pivot) - bit_check(aug[i][k] * aug[k][j]))
                value, remainder = divmod(numerator, previous)
                require(remainder == 0, 'Bareiss nonexact division')
                aug[i][j] = bit_check(value)
            aug[i][k] = 0
        previous = pivot
    if not aug[-1][-2]: raise CandidateFailure('Exact singular basis')
    x = [Q(0)] * n
    for i in range(n - 1, -1, -1):
        tick(); total = Q(aug[i][-1])
        for j in range(i + 1, n): total = bit_check(total - bit_check(aug[i][j] * x[j]))
        x[i] = bit_check(total / aug[i][i])
    require(all(sum((Q(c) * xj for c, xj in zip(row, x)), Q(0)) == b for row, b in zip(a, rhs)),
            'Exact basis solution failed its equations')
    return x, pivots


def scale_difference(terms):
    require(terms and any(terms.values()), 'Zero balance difference is outside fixed design')
    maximum = max(abs(x) for x in terms.values()); scale = Q(1)
    while maximum < 1: maximum *= 2; scale *= 2
    while maximum >= 2: maximum /= 2; scale /= 2
    require(1 <= maximum < 2, 'Scaling normalization')
    return scale


def labels(directory):
    with gzip.open(directory / 'row_metadata.csv.gz', 'rt', newline='') as f: return list(csv.DictReader(f))


def get_vector(v, path, key, dtype, length):
    return v.vector(v.read_npz(path, (key,))[key], dtype, length, key)


def verify_identity_relation(v, model, mask, objective):
    cap_model = v.load_model(IDENTITY); cap_labels = labels(IDENTITY)
    require(cap_model.cols == model.cols and cap_model.rows == model.rows + 1, 'Capped identity dimensions')
    require(cap_model.lower == model.lower and cap_model.upper == model.upper, 'Capped identity column bounds')
    require(get_vector(v, IDENTITY / 'integrality.npz', 'integrality', ('|u1',), model.cols) == mask, 'Capped binary mask')
    caps = [i for i, label in enumerate(cap_labels) if label['family'] == 'fossil_energy_cap']
    require(len(caps) == 1, 'Expected one existing identity cap')
    cap_row = caps[0]
    require(cap_model.row_lower[cap_row] == -math.inf and Q(cap_model.row_upper[cap_row]) == CAP, 'Existing cap changed')
    require(row_terms(cap_model, cap_row) == {j: Q(c) for j, c in enumerate(objective) if c}, 'Cap/objective differs')
    original = 0
    for i in range(cap_model.rows):
        if i == cap_row: continue
        require(row_terms(cap_model, i) == row_terms(model, original), 'Capped non-cap row differs')
        require((cap_model.row_lower[i], cap_model.row_upper[i]) == (model.row_lower[original], model.row_upper[original]),
                'Capped non-cap bounds differ')
        original += 1
    return dict(existing_cap=rat(CAP), cap_row=cap_row, all_other_rows_and_boxes_identical=True)


def inspect_and_transform(v):
    """Preparation-only entry: actual model inspection and exact row replacement."""
    for name, digest in EXPECTED.items(): require(sha(SOURCE / name) == digest, 'Changed original January ' + name)
    require(sha(SCHEDULE) == '7c534f8691c761815224ac43773259da5a8e1d3eb2aa892dcb64dc46541672db', 'Canonical schedule binding')
    require(sha(GEN) == '988466f29132b73739de60c9204dd4a2a9ceb0adf572e5966c086611272f4068', 'Native generators binding')
    require(sha(OLD_MANIFEST) == 'a4cd70b40e26a9c5019df545364adb06124ce4e46e67c713caf4667ae19c02af', 'Original manifest binding')
    with OLD_MANIFEST.open(newline='', encoding='utf-8-sig') as f: old = list(csv.DictReader(f))
    for name in ('matrix.npz', 'bounds.npz', 'integrality.npz', 'objective.npz', 'native_inputs.npz'):
        candidates = [r for r in old if r['path'].replace('\\', '/').endswith('/month_01/' + name)]
        require(len(candidates) == 1 and sha(SOURCE / name) == candidates[0]['sha256']
                and (SOURCE / name).stat().st_size == int(candidates[0]['bytes']), 'Old provenance mismatch: ' + name)
    m = v.load_model(SOURCE); meta = v.json_read(SOURCE / 'model_metadata.json'); lab = labels(SOURCE)
    require((m.rows, m.cols) == (34680, 23016) and len(lab) == m.rows, 'Original model shape')
    require(meta['offsets'] == dict(P=0, U=6888, Y=10920, Z=14952, theta=18984), 'Original offsets')
    require(meta['energy_cap_constraints'] == meta['individual_mean_constraints'] == meta['explicit_ramp_rows'] == 0,
            'Original model is not the declared uncapped no-mean model')
    mask = get_vector(v, SOURCE / 'integrality.npz', 'integrality', ('|u1',), m.cols)
    require(mask == tuple(int(6888 <= j < 18984) for j in range(m.cols)), 'Original mask changed')
    objective = get_vector(v, SOURCE / 'objective.npz', 'objective', ('<f8',), m.cols)
    fossil = [meta['unit_names'].index(n) for n in meta['thermal_unit_names'] if n != '121_NUCLEAR_1']
    expected_c = tuple(float(j < 6888 and j % 41 in fossil) for j in range(m.cols))
    require(len(fossil) == 23 and objective == expected_c, 'Original 23-fossil objective differs')
    raw = get_vector(v, SOURCE / 'returned_vector.npz', 'vector', ('<f8',), m.cols)
    saved = get_vector(v, SCHEDULE, 'vector', ('<f8',), m.cols)
    require(all(math.isfinite(x) for x in (*raw, *saved)), 'Nonfinite old vector')
    fixed = {j: Q(saved[j]) for j, flag in enumerate(mask) if flag}
    require(all(x in (0, 1) for x in fixed.values()), 'Saved schedule not exact binary')
    for t in range(168):
        for k in range(24):
            j = 6888 + t * 24 + k
            require(abs(raw[j] - round(raw[j])) <= 1e-5 and fixed[j] == round(raw[j]), 'Original U schedule differs')
            delta = fixed[j] - fixed[j - 24] if t else Q(0)
            require(fixed[10920 + t * 24 + k] == max(delta, 0)
                    and fixed[14952 + t * 24 + k] == max(-delta, 0), 'Saved transitions are not canonical')
    for j, x in fixed.items(): require(Q(m.lower[j]) <= x <= Q(m.upper[j]), 'Fixed schedule violates a column bound')
    native = v.read_npz(SOURCE / 'native_inputs.npz', ('pmin', 'pmax', 'net', 'rows', 'nodal'))
    require(native['pmin'].shape == native['pmax'].shape == (168, 41) and native['nodal'].shape == (168, 24), 'Native shape')
    spec = checker.native_spec(GEN, meta)
    for t in range(168):
        for j in range(41):
            low = native['pmin'].values[t * 41 + j] if spec[j]['category'] == 'Hydro' else 0.
            require(m.lower[t * 41 + j] == low and m.upper[t * 41 + j] == native['pmax'].values[t * 41 + j], 'Native dispatch boxes')
    blocks = []
    global_map = {}
    for t in range(168):
        columns = list(range(t * 41, (t + 1) * 41)) + list(range(18984 + t * 24, 18984 + (t + 1) * 24))
        for local, j in enumerate(columns): global_map[j] = (t, local)
        pins = [j for j in columns[41:] if m.lower[j] == m.upper[j] == 0]
        require(len(pins) == 1, 'Expected one discovered zero reference pin')
        blocks.append(dict(hour=t, columns=columns, lower=[Q(m.lower[j]) for j in columns],
            upper=[Q(m.upper[j]) for j in columns], objective=[Q(objective[j]) for j in columns],
            rows=[], reference_column=pins[0], reference_bus_ID=meta['bus_ids'][pins[0] - 18984 - 24 * t]))
    constants = []
    for i in range(m.rows):
        require(int(lab[i]['row']) == i, 'Row metadata index')
        terms = row_terms(m, i)
        shift = sum((a * fixed[j] for j, a in terms.items() if j in fixed), Q(0))
        free = {j: a for j, a in terms.items() if j not in fixed}
        lower = endpoint(m.row_lower[i]); upper = endpoint(m.row_upper[i])
        if not free:
            require((lower is None or shift >= lower) and (upper is None or shift <= upper), 'Fixed constant row failure ' + str(i))
            constants.append(dict(row=i, family=lab[i]['family'], activity=rat(shift),
                                  lower=encode_bound(lower), upper=encode_bound(upper)))
            continue
        hours = {global_map[j][0] for j in free}
        require(len(hours) == 1, 'Continuous row links multiple hours')
        t = next(iter(hours)); require(int(lab[i]['hour_0based']) == t, 'Row label disagrees with actual free columns')
        row = dict(original_row=i, family=lab[i]['family'], uid=lab[i]['uid'],
                   terms={global_map[j][1]: a for j, a in free.items()}, fixed_shift=shift,
                   lower=None if lower is None else lower - shift, upper=None if upper is None else upper - shift)
        blocks[t]['rows'].append(row)
        if row['family'] == 'aggregate_balance':
            require(free == {t * 41 + j: Q(1) for j in range(41)} and not shift,
                    'Original aggregate coefficients')
            require(lower == upper == Q(native['net'].values[t]), 'Native aggregate endpoint')
        elif row['family'] == 'nodal_balance':
            bus = int(row['uid']); b = meta['bus_ids'].index(bus)
            require({j: a for j, a in free.items() if j < 6888} ==
                    {t * 41 + j: Q(1) for j, s in enumerate(spec) if s['bus'] == bus}, 'Native generator-to-bus mapping')
            require(lower == upper == Q(native['nodal'].values[t * 24 + b]) and not shift, 'Native nodal endpoint')
        elif row['family'] in ('thermal_upper', 'thermal_lower'):
            j = meta['unit_names'].index(row['uid']); k = meta['thermal_unit_names'].index(row['uid'])
            index = t * 41 + j; uindex = 6888 + t * 24 + k
            expected = {index: Q(1), uindex: -Q(native['pmax'].values[index])} if row['family'] == 'thermal_upper' else {
                index: Q(-1), uindex: Q(native['pmin'].values[index])}
            expected = {j: a for j, a in expected.items() if a}
            require(terms == expected and lower is None and upper == 0, 'Native thermal row')
    require(len(constants) == 16032, 'Constant-row denominator differs')
    transformations = []
    for block in blocks:
        rows = block['rows']
        require(Counter(r['family'] for r in rows) == Counter(aggregate_balance=1, thermal_upper=24,
                thermal_lower=24, nodal_balance=24, branch_flow=38), 'Continuous row family denominator')
        aggregate = next(r for r in rows if r['family'] == 'aggregate_balance')
        nodals = [r for r in rows if r['family'] == 'nodal_balance']
        require(all(r['lower'] == r['upper'] and r['lower'] is not None for r in [aggregate] + nodals), 'Balance is not equality')
        difference = dict(aggregate['terms']); beta = aggregate['lower']
        for row in nodals:
            beta -= row['lower']
            for j, a in row['terms'].items(): difference[j] = difference.get(j, Q(0)) - a
        difference = {j: a for j, a in difference.items() if a}
        require(all(j >= 41 for j in difference) and difference, 'Balance difference not angle-only/nonzero')
        scale = scale_difference(difference)
        transformations.append(dict(hour=block['hour'], aggregate_row=aggregate['original_row'],
            retained_nodal_rows=[r['original_row'] for r in nodals], lambda_exact=rat(scale),
            difference=[[j, rat(a)] for j, a in sorted(difference.items())], rhs_difference=rat(beta)))
        aggregate['terms'] = {j: a * scale for j, a in difference.items()}
        aggregate['lower'] = aggregate['upper'] = beta * scale
        aggregate['family'] = 'exact_scaled_balance_difference'
    relation = verify_identity_relation(v, m, mask, objective)
    return m, meta, mask, objective, fixed, blocks, constants, transformations, spec, relation


def encoded_blocks(blocks):
    out = []
    for block in blocks:
        b = {k: value for k, value in block.items() if k not in ('lower', 'upper', 'objective', 'rows')}
        for key in ('lower', 'upper', 'objective'): b[key] = [rat(x) for x in block[key]]
        b['rows'] = [dict(original_row=r['original_row'], family=r['family'], uid=r['uid'],
            terms=[[j, rat(a)] for j, a in sorted(r['terms'].items())], fixed_shift=rat(r['fixed_shift']),
            lower=encode_bound(r['lower']), upper=encode_bound(r['upper'])) for r in block['rows']]
        out.append(b)
    return out


def decoded_blocks(data):
    for b in data:
        for key in ('lower', 'upper', 'objective'): b[key] = [parse_rat(x) for x in b[key]]
        for r in b['rows']:
            r['terms'] = {int(j): parse_rat(a) for j, a in r['terms']}
            r['fixed_shift'] = parse_rat(r['fixed_shift'])
            r['lower'], r['upper'] = decode_bound(r['lower']), decode_bound(r['upper'])
    return data


def write_proposal(blocks):
    import numpy as np
    from scipy.sparse import coo_matrix, save_npz
    rr = []; cc = []; vv = []; lows = []; highs = []; conversions = []; mapping = []
    def convert(value, location):
        approximate = float(value); require(math.isfinite(approximate), 'Proposal conversion overflow')
        if Q(approximate) != value:
            conversions.append(dict(location=location, exact=rat(value), binary64_hex=approximate.hex(),
                                    difference=rat(Q(approximate) - value)))
        require(not value or approximate != 0, 'Proposal conversion underflow')
        return approximate
    for b in blocks:
        for row in b['rows']:
            i = len(lows); mapping.append(dict(proposal_row=i, hour=b['hour'], original_row=row['original_row']))
            for j, a in sorted(row['terms'].items()):
                rr.append(i); cc.append(b['hour'] * 65 + j); vv.append(convert(a, ['coefficient', i, j]))
            lows.append(-np.inf if row['lower'] is None else convert(row['lower'], ['row_lower', i]))
            highs.append(np.inf if row['upper'] is None else convert(row['upper'], ['row_upper', i]))
    matrix = coo_matrix((vv, (rr, cc)), shape=(len(lows), 168 * 65)).tocsr()
    save_npz(OUT / 'proposal_matrix.npz', matrix)
    np.savez_compressed(OUT / 'proposal_bounds.npz', column_lower=[float(x) for b in blocks for x in b['lower']],
        column_upper=[float(x) for b in blocks for x in b['upper']], row_lower=lows, row_upper=highs)
    np.savez_compressed(OUT / 'proposal_objective.npz', objective=[float(x) for b in blocks for x in b['objective']])
    save(OUT / 'proposal_mapping.json', mapping); save(OUT / 'conversion_differences.json', conversions)
    return len(conversions)


def bindings(paths):
    return [dict(path=str(p.resolve()), bytes=p.stat().st_size, sha256=sha(p)) for p in dict.fromkeys(paths)]


def verify_bindings(records):
    require(records and len({r['path'] for r in records}) == len(records), 'Invalid manifest')
    for r in records:
        p = Path(r['path'])
        require(p.is_file() and p.stat().st_size == r['bytes'] and sha(p) == r['sha256'], 'Changed binding: ' + str(p))


def prepare():
    require(not OUT.exists(), 'Preparation output already exists')
    start = time.perf_counter(); v = checker.kernel()
    m, meta, mask, objective, fixed, blocks, constants, transformations, spec, relation = inspect_and_transform(v)
    OUT.mkdir(parents=True, exist_ok=False)
    with gzip.open(OUT / 'exact_blocks.json.gz', 'xt', encoding='utf-8') as f: json.dump(encoded_blocks(blocks), f, separators=(',', ':'))
    save(OUT / 'constant_rows.json', constants); save(OUT / 'transformations.json', transformations)
    save(OUT / 'fixed_schedule.json', [dict(column=j, value=rat(x)) for j, x in fixed.items()])
    save(OUT / 'native_spec.json', spec); save(OUT / 'existing_cap_relation.json', relation)
    changes = write_proposal(blocks)
    save(OUT / 'preparation_report.json', dict(elapsed_s=time.perf_counter() - start, original_rows=m.rows,
        original_columns=m.cols, constant_rows=len(constants), continuous_rows=sum(len(b['rows']) for b in blocks),
        hours=168, continuous_columns_per_hour=65, conversion_differences=changes,
        reference_columns=[b['reference_column'] for b in blocks], zero_optimizers=True, zero_basis_reconstructions=True))
    originals = [SOURCE / name for name in ('matrix.npz', 'bounds.npz', 'integrality.npz', 'objective.npz',
        'model_metadata.json', 'row_metadata.csv.gz', 'native_inputs.npz', 'returned_vector.npz')]
    originals += [IDENTITY / name for name in ('matrix.npz', 'bounds.npz', 'integrality.npz', 'objective.npz', 'row_metadata.csv.gz')]
    files = [Path(__file__), CHECKER, PROTOCOL, DESIGN, checker.KERNEL, OLD_MANIFEST, GEN, SCHEDULE, TEST_REPORT] + originals
    files += sorted(OUT.iterdir())
    records = bindings(files); save(OUT / 'input_manifest.json', records); verify_bindings(records)
    save(OUT / 'prepared_freeze.json', dict(utc=utc().isoformat(), manifest_sha256=sha(OUT / 'input_manifest.json'),
        bindings=len(records), options=OPTIONS, exact_phase_seconds=EXACT_SECONDS, bit_limit=BITS,
        cutoff_utc=CUTOFF.isoformat(), optimizer_calls=0, basis_reconstructions=0,
        source_sha256=sha(Path(__file__)), checker_sha256=sha(CHECKER), protocol_sha256=sha(PROTOCOL),
        separate_root_execution_GO_required=True))
    print(json.dumps(dict(status='PREPARED_NO_SOLVE_OR_RECONSTRUCTION', manifest_sha256=sha(OUT / 'input_manifest.json'))), flush=True)


def reconstruct_hour(block, col_status, row_status, tick):
    tick(); n = len(block['columns']); rows = block['rows']
    require(len(col_status) == n and len(row_status) == len(rows), 'Basis block dimensions')
    basic = [j for j in range(n) if col_status[j] == 'kBasic']
    nonbasic = [j for j in range(n) if j not in basic]
    active = [i for i in range(len(rows)) if row_status[i] != 'kBasic']
    if len(active) != len(basic): raise CandidateFailure('Per-hour basis count mismatch')
    x = [None] * n
    for j in nonbasic: x[j] = basis_endpoint(col_status[j], block['lower'][j], block['upper'][j])
    endpoints = [basis_endpoint(row_status[i], rows[i]['lower'], rows[i]['upper']) for i in active]
    a = [[rows[i]['terms'].get(j, Q(0)) for j in basic] for i in active]
    rhs = [b - sum((rows[i]['terms'].get(j, Q(0)) * x[j] for j in nonbasic), Q(0)) for i, b in zip(active, endpoints)]
    solved, pivots = exact_solve(a, rhs, tick)
    for j, value in zip(basic, solved): x[j] = value
    failures = []
    for j, value in enumerate(x):
        bit_check(value)
        if not block['lower'][j] <= value <= block['upper'][j]: failures.append(dict(column=j, rule='original_column_bound'))
    for row in rows:
        tick(); lhs = sum((a * x[j] for j, a in row['terms'].items()), Q(0))
        if (row['lower'] is not None and lhs < row['lower']) or (row['upper'] is not None and lhs > row['upper']):
            failures.append(dict(original_row=row['original_row'], rule='exact_transformed_row'))
    return x, dict(basic_original_columns=[block['columns'][j] for j in basic],
        nonbasic=[dict(column=block['columns'][j], value=rat(x[j]), status=col_status[j]) for j in nonbasic],
        active_original_rows=[rows[i]['original_row'] for i in active], active_endpoints=[rat(x) for x in endpoints],
        pivots=pivots, exact_hour_pass=not failures, violations=len(failures), first_violations=failures[:20])


def run():
    v = checker.kernel(); freeze = v.json_read(OUT / 'prepared_freeze.json')
    require(not (OUT / 'execution_marker.json').exists(), 'Single execution already attempted')
    require(sha(OUT / 'input_manifest.json') == freeze['manifest_sha256'], 'Manifest changed')
    records = v.json_read(OUT / 'input_manifest.json'); validation_start = time.perf_counter(); verify_bindings(records)
    require(freeze['options'] == OPTIONS and freeze['exact_phase_seconds'] == EXACT_SECONDS and freeze['bit_limit'] == BITS, 'Frozen settings changed')
    import highspy
    import numpy as np
    from scipy.sparse import load_npz
    h = highspy.Highs(); require(h.version() == '1.12.0', 'Installed solver version differs')
    with gzip.open(OUT / 'exact_blocks.json.gz', 'rt', encoding='utf-8') as f: blocks = decoded_blocks(json.load(f))
    matrix = load_npz(OUT / 'proposal_matrix.npz').tocsr()
    with np.load(OUT / 'proposal_bounds.npz', allow_pickle=False) as f: bounds = {k: f[k].copy() for k in f.files}
    with np.load(OUT / 'proposal_objective.npz', allow_pickle=False) as f: objective = f['objective'].copy()
    lp = highspy.HighsLp(); lp.num_col_, lp.num_row_ = matrix.shape[1], matrix.shape[0]
    lp.col_cost_ = objective; lp.col_lower_, lp.col_upper_ = bounds['column_lower'], bounds['column_upper']
    lp.row_lower_, lp.row_upper_ = bounds['row_lower'], bounds['row_upper']
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.start_, lp.a_matrix_.index_, lp.a_matrix_.value_ = matrix.indptr, matrix.indices, matrix.data
    for key, value in {**OPTIONS, 'log_file': str(OUT / 'solver.log')}.items():
        require(h.setOptionValue(key, value) == highspy.HighsStatus.kOk, 'Rejected option ' + key)
    require(h.passModel(lp) == highspy.HighsStatus.kOk, 'Proposal model rejected/warned')
    # Check that the numerical engine accepted exactly the submitted proposal.
    # This is not a test of exact original-model feasibility.
    accepted_lp = h.getLp()
    from scipy.sparse import csr_matrix, csc_matrix
    builder = csr_matrix if accepted_lp.a_matrix_.format_ == highspy.MatrixFormat.kRowwise else csc_matrix
    require(accepted_lp.a_matrix_.format_ in (highspy.MatrixFormat.kRowwise, highspy.MatrixFormat.kColwise), 'Unexpected returned proposal format')
    accepted_matrix = builder((accepted_lp.a_matrix_.value_, accepted_lp.a_matrix_.index_, accepted_lp.a_matrix_.start_),
                              shape=(accepted_lp.num_row_, accepted_lp.num_col_)).tocsr()
    require(accepted_matrix.shape == matrix.shape and (accepted_matrix != matrix).nnz == 0, 'Solver altered proposal coefficients')
    for actual, expected in ((accepted_lp.col_cost_, objective), (accepted_lp.col_lower_, bounds['column_lower']),
                             (accepted_lp.col_upper_, bounds['column_upper']), (accepted_lp.row_lower_, bounds['row_lower']),
                             (accepted_lp.row_upper_, bounds['row_upper'])):
        require(np.array_equal(np.asarray(actual), expected), 'Solver altered proposal endpoints/objective')
    validation_seconds = time.perf_counter() - validation_start
    save(OUT / 'execution_marker.json', dict(utc=utc().isoformat(), prepared_manifest_sha256=freeze['manifest_sha256'],
        validation_seconds=validation_seconds, requested_optimizer_calls=1, requested_hours=168))
    if (CUTOFF - utc()).total_seconds() < SECONDS + 5:
        save(OUT / 'outcomes.json', [dict(hour=t, status='NOT_EVALUATED_UTC_START_GUARD') for t in range(168)])
        save(OUT / 'completion.json', dict(status='NOT_STARTED_UTC_GUARD', optimizer_calls=0, hours=168)); return
    save(OUT / 'launch_decision.json', dict(utc=utc().isoformat(), utc_remaining_s=(CUTOFF - utc()).total_seconds(), options=OPTIONS))
    # Recheck at the actual call site after durable launch-decision I/O.
    if (CUTOFF - utc()).total_seconds() < SECONDS + 5:
        save(OUT / 'outcomes.json', [dict(hour=t, status='NOT_EVALUATED_UTC_START_GUARD') for t in range(168)])
        save(OUT / 'completion.json', dict(status='NOT_STARTED_UTC_GUARD_AFTER_DECISION', optimizer_calls=0, hours=168)); return
    start = time.perf_counter()
    try:
        solve_status = h.run(); solve_seconds = time.perf_counter() - start
        basis = h.getBasis(); solution = h.getSolution(); info = h.getInfo()
    except Exception as error:
        save(OUT / 'solver_exception.json', dict(reason=type(error).__name__ + ': ' + str(error),
            attempted_optimizer_calls=1, actual_seconds=time.perf_counter() - start))
        save(OUT / 'outcomes.json', [dict(hour=t, status='UNRESOLVED_SOLVER_EXCEPTION') for t in range(168)])
        verify_bindings(records)
        save(OUT / 'completion.json', dict(status='UNRESOLVED_SOLVER_EXCEPTION', optimizer_calls=1, hours=168,
            no_full_UC_negative_claim=True)); return
    col_status = [x.name for x in basis.col_status]; row_status = [x.name for x in basis.row_status]
    save(OUT / 'basis.json', dict(valid=basis.valid, column_status=col_status, row_status=row_status))
    np.savez_compressed(OUT / 'numerical_proposal_point.npz', vector=np.asarray(solution.col_value), row_activity=np.asarray(solution.row_value))
    save(OUT / 'solver_result.json', dict(call_status=str(solve_status), model_status=h.modelStatusToString(h.getModelStatus()),
        basis_valid=basis.valid, value_valid=solution.value_valid, objective_numerical=None if not math.isfinite(info.objective_function_value) else info.objective_function_value,
        configured_seconds=SECONDS, actual_seconds=solve_seconds, soft_overrun_seconds=max(0., solve_seconds - SECONDS),
        simplex_iterations=info.simplex_iteration_count, optimizer_calls=1, exact_feasibility_claim=False))
    phase_start = time.perf_counter(); tick = guarded_clock(phase_start + EXACT_SECONDS)
    outcomes = []; full = [None] * 23016; fixed_data = v.json_read(OUT / 'fixed_schedule.json')
    fixed = {r['column']: parse_rat(r['value']) for r in fixed_data}
    for j, value in fixed.items(): full[j] = value
    phase_limited = False; row_offset = 0
    valid_basis = basis.valid and len(col_status) == 168 * 65 and len(row_status) == 168 * 111
    for block in blocks:
        t = block['hour']; record = dict(hour=t)
        if not valid_basis: record['status'] = 'UNRESOLVED_NO_VALID_BASIS'
        elif phase_limited: record['status'] = 'NOT_EVALUATED_PHASE_LIMIT'
        else:
            try:
                x, detail = reconstruct_hour(block, col_status[t * 65:(t + 1) * 65], row_status[row_offset:row_offset + 111], tick)
                record.update(detail); record['status'] = 'EXACT_HOUR_POINT' if detail['exact_hour_pass'] else 'UNRESOLVED_RECONSTRUCTED_POINT_VIOLATES'
                record['values'] = [dict(column=j, value=rat(a)) for j, a in zip(block['columns'], x)]
                for j, value in zip(block['columns'], x): full[j] = value
            except PhaseLimit as error:
                phase_limited = True; record.update(status='NOT_EVALUATED_PHASE_LIMIT', reason=str(error))
            except CandidateFailure as error: record.update(status='UNRESOLVED_BASIS_RECONSTRUCTION', reason=str(error))
            except Exception as error: record.update(status='UNRESOLVED_IMPLEMENTATION_ERROR', reason=type(error).__name__ + ': ' + str(error))
        save(OUT / f'hour_{t:03d}.json', record); outcomes.append(dict(hour=t, status=record['status']))
        row_offset += 111
    accepted = False; postcheck_status = 'NOT_ATTEMPTED_INCOMPLETE_HOURS'
    if all(r['status'] == 'EXACT_HOUR_POINT' for r in outcomes):
        try:
            tick(); model = v.load_model(SOURCE)
            mask = get_vector(v, SOURCE / 'integrality.npz', 'integrality', ('|u1',), model.cols)
            cost = get_vector(v, SOURCE / 'objective.npz', 'objective', ('<f8',), model.cols)
            report = checker.check_point(v, model, full, mask, fixed, cost, tick)
            meta = v.json_read(SOURCE / 'model_metadata.json')
            report['native'] = checker.check_native(v, full, SOURCE, meta, v.json_read(OUT / 'native_spec.json'), tick)
            accepted = report['pass_strict'] and report['native']['pass_native']
            energy = parse_rat(report['exact_objective'])
            report['existing_cap_comparison'] = dict(cap=rat(CAP), energy=rat(energy), within_cap=energy <= CAP)
            if accepted and energy <= CAP:
                cap_model = v.load_model(IDENTITY)
                report['existing_capped_identity_check'] = checker.check_point(v, cap_model, full, mask, fixed, cost, tick)
                require(report['existing_capped_identity_check']['pass_strict'], 'Original capped identity consistency failure')
            save(OUT / 'rational_point.json', dict(schema='exact-fixed-schedule-point-v1', model_bindings=checker.model_bindings(SOURCE),
                columns=23016, values=[dict(column=j, value=rat(x)) for j, x in enumerate(full)]))
            save(OUT / 'strict_original_replay.json', report)
            postcheck_status = 'STRICT_NOMINAL_WITNESS' if accepted else 'UNRESOLVED_ORIGINAL_OR_NATIVE_REPLAY_FAILURE'
        except PhaseLimit as error: accepted = False; postcheck_status = 'UNRESOLVED_FINAL_REPLAY_PHASE_LIMIT'; save(OUT / 'final_replay_limit.json', dict(reason=str(error)))
        except Exception as error:
            accepted = False; postcheck_status = 'UNRESOLVED_FINAL_REPLAY_ERROR'
            save(OUT / 'final_replay_error.json', dict(reason=type(error).__name__ + ': ' + str(error)))
    verify_bindings(records)
    save(OUT / 'outcomes.json', outcomes)
    elapsed = time.perf_counter() - phase_start
    save(OUT / 'completion.json', dict(status=postcheck_status, accepted_strict=accepted, independent_replay_pending=accepted,
        optimizer_calls=1, original_hour_denominator=168, outcome_counts=dict(Counter(r['status'] for r in outcomes)),
        solve_seconds=solve_seconds, exact_phase_seconds=elapsed, exact_phase_budget=EXACT_SECONDS,
        exact_soft_overrun_seconds=max(0., elapsed - EXACT_SECONDS), phase_includes_final_hash_and_outcomes_write=True,
        phase_excludes_completion_record_write=True, fixed_schedule_only=True, no_full_UC_negative_claim=True))
    print(json.dumps(dict(status=postcheck_status, accepted_strict=accepted, counts=dict(Counter(r['status'] for r in outcomes)))), flush=True)


def synthetic_tests():
    """Small synthetic data only. No actual model files, preparation or optimizer."""
    v = checker.kernel(); passed = []
    def test(name, condition): require(condition, 'Synthetic test: ' + name); passed.append(name)
    def rejects(name, operation, error=ValueError):
        try: operation()
        except error: passed.append(name); return
        raise AssertionError('Did not reject: ' + name)
    test('lower_activity_endpoint', basis_endpoint('kLower', Q(2), Q(5)) == 2)
    test('upper_activity_endpoint', basis_endpoint('kUpper', Q(2), Q(5)) == 5)
    test('fixed_nonbasic_unambiguous', basis_endpoint('kNonbasic', Q(2), Q(2)) == 2)
    test('free_zero', basis_endpoint('kZero', None, None) == 0)
    rejects('ambiguous_nonbasic', lambda: basis_endpoint('kNonbasic', Q(0), Q(1)))
    rejects('bounded_zero_unsupported', lambda: basis_endpoint('kZero', Q(-1), Q(1)))
    x, _ = exact_solve([[Q(3)]], [Q(1)]); test('nondyadic_solution', x == [Q(1, 3)])
    x, pivots = exact_solve([[Q(0), Q(2)], [Q(3), Q(1)]], [Q(2), Q(4)])
    test('row_pivot_swap', x == [Q(1), Q(1)] and pivots[0]['chosen_current_row'] == 1)
    rejects('exact_singularity', lambda: exact_solve([[Q(1), Q(2)], [Q(2), Q(4)]], [Q(1), Q(2)]))
    eps = Q(1, 2 ** 60); a = [[Q(1), Q(1)], [Q(1), Q(1) + eps]]
    x, _ = exact_solve(a, [Q(1), Q(1) + eps * 2]); test('near_dependency_retained', x == [-1, 2])
    test('power_two_rescale', scale_difference({0: eps, 1: -2 * eps}) * 2 * eps == 1)
    rejects('bit_guard', lambda: bit_check(2 ** BITS), BitLimit)
    rejects('phase_guard', lambda: exact_solve([[Q(1)]], [Q(1)], lambda: (_ for _ in ()).throw(PhaseLimit('fixture'))), PhaseLimit)
    model = v.Model(2, 2, (3., 1.), (0, 1), (0, 1, 2), (0., 0.), (1., 1.), (1., 1.), (1., 1.))
    point = [Q(1, 3), Q(1)]; mask = (0, 1); fixed = {1: Q(1)}
    test('strict_nondyadic_point', checker.check_point(v, model, point, mask, fixed, (1., 0.))['pass_strict'])
    test('corrupted_point_rejected', not checker.check_point(v, model, [Q(1, 3) + eps, Q(1)], mask, fixed, (1., 0.))['pass_strict'])
    test('fixed_state_corruption_rejected', not checker.check_point(v, model, [Q(1, 3), Q(0)], mask, fixed, (1., 0.))['pass_strict'])
    constant_bad = v.Model(1, 1, (), (), (0, 0), (0.,), (1.,), (1.,), (1.,))
    test('constant_row_failure_retained', not checker.check_point(v, constant_bad, [Q(0)], (0,), {}, (0.,))['pass_strict'])
    test('canonical_fraction_roundtrip', parse_rat(rat(Q(-2, 3))) == Q(-2, 3))
    rejects('unreduced_fraction', lambda: parse_rat(dict(numerator='2', denominator='6')))
    rejects('negative_zero_encoding', lambda: parse_rat(dict(numerator='-0', denominator='1')))
    block = dict(columns=[0, 1], lower=[Q(0), Q(0)], upper=[Q(2), Q(2)], rows=[
        dict(original_row=0, lower=Q(1), upper=Q(1), terms={0: Q(1), 1: Q(1)})])
    x, detail = reconstruct_hour(block, ['kBasic', 'kLower'], ['kUpper'], lambda: None)
    test('block_basis_endpoint_reconstruction', x == [1, 0] and detail['exact_hour_pass'])
    return dict(status='SYNTHETIC_ONLY_PASS', count=len(passed), tests=passed, actual_models_read=0,
        actual_model_transformations=0, actual_basis_reconstructions=0, optimizer_calls=0,
        source_sha256=sha(Path(__file__)), checker_sha256=sha(CHECKER))


def main():
    p = argparse.ArgumentParser(); g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('--synthetic-only', action='store_true'); g.add_argument('--prepare-only', action='store_true')
    g.add_argument('--run-prepared', action='store_true'); p.add_argument('--report', type=Path)
    a = p.parse_args()
    if a.synthetic_only:
        require(a.report is not None and not a.report.exists(), 'New synthetic report path required')
        try: result = synthetic_tests()
        except Exception as error:
            save(a.report, dict(status='SYNTHETIC_ONLY_FAILED', reason=type(error).__name__ + ': ' + str(error),
                source_sha256=sha(Path(__file__)), checker_sha256=sha(CHECKER), actual_models_read=0, optimizer_calls=0))
            raise
        save(a.report, result); print(json.dumps(result))
    elif a.prepare_only: prepare()
    else: run()


if __name__ == '__main__': main()
