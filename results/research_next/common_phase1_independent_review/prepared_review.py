"""Independent frozen phase-I endpoint/encoding gate; no producer or solver import."""
import ast
import csv
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import time
from datetime import datetime, timezone
from fractions import Fraction as F

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
ARM = ROOT / 'results/research_next/common_phase1'
PRE = ARM / 'prepared'
MASTER = ROOT / 'results/research_next/common_master_bounded'
SOURCE = ROOT / 'src/researchnext_common_phase1.py'
PROTOCOL = ROOT / 'docs/research_next/COMMON_PHASE1_PROTOCOL.md'
KERNEL = ROOT / 'src/research8h_standalone_verify.py'
PINS = {
    SOURCE: '8af88d286e85f5807ab0bc11cc2450d10596f667e62f4b45c5279c8ebbc2eacb',
    PROTOCOL: '6617c67b1c93339487a41c306217c8770142665b9e35e33f23a09225f1e00583',
    PRE / 'prepared_freeze.json': '9d2a0768eb785277d9b8ddf04483e0e83ed97ba628fff23e2a32b146649e1496',
    PRE / 'input_manifest.json': '9e4640c4bea127601201e3323f43471e2582eb9aab26ed6cb045f566c4f00d70',
    KERNEL: '708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f',
    MASTER / 'INDEPENDENT_POSTRUN_REVIEW.json': 'd5b2c4baac6605ef98f6cc025757c5f36c372166931ba7afe870d5509fdc9ad2',
    MASTER / 'producer_output_inventory.csv': 'a7201af2fc77e7a556c5b0fc2ee0634f812808f0e4f092b64656baf24d668428',
    MASTER / 'run01/lp/fixed_schedule.json': '26362ddab6b43aaa3ce2b605997a0c3460d9615492c13e177f7822c508ebf14a',
}
TAU = F.from_float(1e-5)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def gz(path):
    with gzip.open(path, 'rt', encoding='utf-8') as stream:
        return json.load(stream)


def record(path):
    p = Path(path).resolve()
    data = p.read_bytes()
    return {'path': str(p), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def binding(item):
    need(record(item['path']) == item, 'Changed binding: ' + item['path'])


def fraction(pair):
    need(isinstance(pair, list) and len(pair) == 2 and all(isinstance(x, str) for x in pair), 'Fraction schema')
    result = F(int(pair[0]), int(pair[1]))
    need(pair == [str(result.numerator), str(result.denominator)], 'Canonical exact fraction')
    return result


def main():
    started = time.perf_counter()
    need(not (ARM / 'run01').exists(), 'Scientific run must be absent at entry')
    for path, digest in PINS.items():
        need(sha(path) == digest, 'External pin ' + str(path))
    freeze = read(PRE / 'prepared_freeze.json')
    need(freeze['source_sha256'] == PINS[SOURCE] and freeze['protocol_sha256'] == PINS[PROTOCOL]
         and freeze['manifest_sha256'] == PINS[PRE / 'input_manifest.json'], 'Freeze references')
    items = read(PRE / 'input_manifest.json')['files']
    paths = {item['path'].casefold(): item for item in items}
    need(len(items) == len(paths) == 292, 'Unique 292 bindings')
    for item in items:
        binding(item)
    initial = {str(p): sha(p) for p in (PRE / 'prepared_freeze.json', PRE / 'input_manifest.json')}
    inherited = read(MASTER / 'prepared/input_manifest.json')['files']
    need(len(inherited) == 239 and all(paths.get(x['path'].casefold()) == x for x in inherited), 'All prior 239 bindings inherited')
    with (MASTER / 'producer_output_inventory.csv').open(encoding='utf-8-sig', newline='') as stream:
        old_outputs = list(csv.DictReader(stream))
    need(len(old_outputs) == 25, 'Old closed output denominator')
    for row in old_outputs:
        item = {'path': str((ROOT / row['path']).resolve()), 'bytes': int(row['bytes']), 'sha256': row['sha256']}
        need(paths.get(item['path'].casefold()) == item, 'Closed old output bound')
    copied = read(PRE / 'copy_provenance.json')['copies']
    need(len(copied) == 12, 'Twelve copies')
    expected_copies = {
        **{str((PRE / 'joint' / n).resolve()): MASTER / 'prepared/joint' / n
           for n in ('matrix.npz', 'bounds.npz', 'integrality.npz', 'column_maps.json', 'row_origins.json')},
        str((PRE / 'identity_metadata.json').resolve()): MASTER / 'prepared/identity/model_metadata.json',
        str((PRE / 'days_321_metadata.json').resolve()): MASTER / 'prepared/days_321/model_metadata.json',
        str((PRE / 'gen.csv').resolve()): MASTER / 'prepared/gen.csv',
        str((PRE / 'master_premises.json').resolve()): MASTER / 'prepared/premises.json',
        str((PRE / 'fixed_schedule.json').resolve()): MASTER / 'run01/lp/fixed_schedule.json',
        str((PRE / 'master_exact_admission.json').resolve()): MASTER / 'run01/master_exact_admission.json',
        str((PRE / 'control_raw_solution.npz').resolve()): ROOT / 'results/research_next/common_commitment/run01/lp/raw_solution.npz',
    }
    need({x['copy']['path'] for x in copied} == set(expected_copies), 'Exact intended copy set')
    for pair in copied:
        a, b = pair['original'], pair['copy']
        binding(a); binding(b)
        need(Path(a['path']).resolve() == expected_copies[b['path']].resolve(), 'Correct original copy role')
        need(Path(a['path']).read_bytes() == Path(b['path']).read_bytes(), 'Byte-identical copy')
        need(paths.get(a['path'].casefold()) == a and paths.get(b['path'].casefold()) == b, 'Both copy sides frozen')
    listed_pre = {Path(x['path']).resolve() for x in items if Path(x['path']).resolve().is_relative_to(PRE.resolve())}
    actual_pre = {p.resolve() for p in PRE.rglob('*') if p.is_file()}
    need(actual_pre == listed_pre | {p.resolve() for p in map(Path, initial)}, 'Complete prepared inventory')
    need(all(freeze[k] == 0 for k in ('optimizer_calls', 'backend_imports', 'multiplier_evaluations', 'control_evaluations')), 'Preparation-only scope')

    # Only the pinned stdlib decoder is shared. No producer or numerical package import.
    spec = importlib.util.spec_from_file_location('phase1_independent_decoder', KERNEL)
    v = importlib.util.module_from_spec(spec); sys.modules[spec.name] = v; spec.loader.exec_module(v)
    m = v.load_model(PRE / 'joint')
    need((m.rows, m.cols, len(m.data)) == (69362, 33936, 291176), 'Original joint dimensions')
    mask = v.vector(v.read_npz(PRE / 'joint/integrality.npz', ('integrality',))['integrality'], ('|u1',), m.cols, 'original mask')
    need(mask == tuple(int(6888 <= j < 18984) for j in range(m.cols)), 'All original 12096 state declarations')
    schedule = read(PRE / 'fixed_schedule.json')
    entries = schedule['fixed_columns']; fixed = {x['column']: x['value'] for x in entries}
    need(len(entries) == len(fixed) == 12096 and set(fixed) == {j for j, b in enumerate(mask) if b}, 'Unique complete nominee mapping')
    need(all(type(j) is int and type(z) is int and z in (0, 1) and m.lower[j] <= z <= m.upper[j] for j, z in fixed.items()), 'Exact original-box nominee bits')
    admission = read(PRE / 'master_exact_admission.json')
    need(admission['accepted'] is True and not admission['issues'], 'Closed accepted necessary nominee')
    need([fixed[j] for j in sorted(fixed)] == admission['original_shared_state_values'], 'Identical sole nominee')
    need(schedule['master_admission_sha256'] == sha(PRE / 'master_exact_admission.json'), 'Schedule admission hash')

    arrays = v.read_npz(PRE / 'phase_model.npz', ('data', 'indices', 'indptr', 'shape', 'column_lower', 'column_upper', 'row_lower', 'row_upper', 'objective', 'integrality'))
    nr, nc = v.vector(arrays['shape'], ('<i8',), 2, 'phase shape')
    need((nr, nc) == (98546, 33937), 'Phase dimensions')
    vals = v.vector(arrays['data'], ('<f8',), 505786, 'phase data')
    js = v.vector(arrays['indices'], ('<i8',), len(vals), 'phase indices')
    ptr = v.vector(arrays['indptr'], ('<i8',), nr + 1, 'phase pointers')
    lo = v.vector(arrays['column_lower'], ('<f8',), nc, 'phase column lower')
    hi = v.vector(arrays['column_upper'], ('<f8',), nc, 'phase column upper')
    rl = v.vector(arrays['row_lower'], ('<f8',), nr, 'phase row lower')
    ru = v.vector(arrays['row_upper'], ('<f8',), nr, 'phase row upper')
    objective = v.vector(arrays['objective'], ('<f8',), nc, 'phase objective')
    ints = v.vector(arrays['integrality'], ('|u1',), nc, 'phase declarations')
    need(ptr[0] == 0 and ptr[-1] == len(vals) and all(0 <= a <= b <= len(vals) for a, b in zip(ptr, ptr[1:])), 'Phase CSR consistency')
    need(all(math.isfinite(x) for x in vals) and all(0 <= j < nc for j in js), 'Finite phase matrix and valid coordinates')
    need(ints == (0,) * nc and objective == (0.,) * m.cols + (1.,), 'Continuous LP and only min-s objective')
    need(all(math.isfinite(a) and math.isfinite(b) and a <= b for a, b in zip(m.lower, m.upper)), 'Finite nonempty original boxes')
    need(all(not math.isnan(a) and not math.isnan(b) and a <= b for a, b in zip(m.row_lower, m.row_upper)), 'Explicit ordered original row intervals')
    endpoints = gz(PRE / 'endpoint_map.json.gz'); columns = gz(PRE / 'column_encoding.json.gz')
    need(len(endpoints) == nr and len(columns) == nc, 'Full encoding denominators')
    scalar_count = rounded_count = 0
    def encoding(e, exact, actual):
        nonlocal scalar_count, rounded_count
        need(set(e) == {'exact', 'binary64_hex', 'rounding_error'}, 'Encoding fields')
        q = fraction(e['exact']); error = fraction(e['rounding_error'])
        f = float.fromhex(e['binary64_hex'])
        need(q == exact and math.isfinite(f) and abs(f) < 1e20 and (q == 0 or f != 0), 'Finite supported intended scalar')
        need(f.hex() == float(exact).hex() == actual.hex() and error == F(actual) - exact, 'All exact-to-float errors')
        scalar_count += 1; rounded_count += bool(error)
    for j in range(m.cols):
        e = columns[j]; state = bool(mask[j])
        need(set(e) == {'column', 'kind', 'lower', 'upper'} and e['column'] == j and e['kind'] == ('fixed_original_bit' if state else 'expanded_continuous'), 'Box encoding role')
        lower = F(fixed[j]) if state else F(m.lower[j]) - TAU
        upper = F(fixed[j]) if state else F(m.upper[j]) + TAU
        encoding(e['lower'], lower, lo[j]); encoding(e['upper'], upper, hi[j])
    e = columns[-1]
    need(e['column'] == m.cols and e['kind'] == 'artificial_s' and e['upper'] is None and lo[-1] == 0 and hi[-1] == math.inf, 'Single slack with no upper')
    encoding(e['lower'], F(0), lo[-1])
    er = 0; copied_terms = 0; original_two_sided = 0
    for r in range(m.rows):
        a, b = m.indptr[r:r + 2]
        original_two_sided += math.isfinite(m.row_lower[r]) and math.isfinite(m.row_upper[r])
        for side, endpoint, sign in (('lower', m.row_lower[r], 1.), ('upper', m.row_upper[r], -1.)):
            if not math.isfinite(endpoint):
                continue
            need(er < nr, 'No missing phase row')
            e = endpoints[er]
            need(e['phase_row'] == er and e['original_row'] == r and e['side'] == side and e['original_endpoint_hex'] == endpoint.hex() and e['artificial_coefficient_hex'] == sign.hex(), 'Complete lower-first endpoint map')
            pa, pb = ptr[er:er + 2]
            need(js[pa:pb] == m.indices[a:b] + (m.cols,) and vals[pa:pb] == m.data[a:b] + (sign,), 'Every original coefficient plus only signed slack')
            need(len(set(js[pa:pb])) == pb - pa, 'No duplicate phase CSR columns')
            exact = F(endpoint) + (-TAU if side == 'lower' else TAU)
            actual = rl[er] if side == 'lower' else ru[er]
            need((ru[er] == math.inf if side == 'lower' else rl[er] == -math.inf), 'Opposite endpoint absent')
            encoding(e['widened'], exact, actual)
            copied_terms += b - a; er += 1
    need(er == nr and copied_terms + nr == len(vals), 'All finite source endpoints and coefficient uses')

    maps = read(PRE / 'joint/column_maps.json'); origins = read(PRE / 'joint/row_origins.json')['origins']
    premises = read(PRE / 'master_premises.json'); report = read(PRE / 'admission.json')
    with (PRE / 'gen.csv').open(encoding='utf-8-sig', newline='') as stream:
        records = list(csv.DictReader(stream))
    gen = {g['GEN UID']: g for g in records}; need(len(gen) == len(records), 'Unique pinned native roster')
    need(maps['worlds'] == ['identity', 'days_321'] and len(origins) == m.rows, 'Two mapped worlds')
    cap_rows = []
    for wi, world in enumerate(maps['worlds']):
        meta = read(PRE / (world + '_metadata.json')); names = meta['unit_names']; fossils = meta['fossil_units']
        need(len(names) == 41 and len(fossils) == 23 and fossils == [n for n in names if gen[n]['Fuel'] in ('Coal', 'NG', 'Oil')], '23 fossil native electrical units')
        mp = maps['original_to_joint'][wi]
        need(len(mp) == len(set(mp)) == 23016 and mp[6888:18984] == list(range(6888, 18984)), 'Shared state mapping')
        origin = [wi, premises['worlds'][wi]['cap_row']]
        rows = [r for r, o in enumerate(origins) if o == origin]
        need(len(rows) == 1, 'Unique inherited cap row')
        r = rows[0]; cap_rows.append(r); a, b = m.indptr[r:r + 2]
        wanted = {mp[41*t + names.index(n)]: 1. for t in range(168) for n in fossils}
        need(len(wanted) == b-a == 3864 and dict(zip(m.indices[a:b], m.data[a:b])) == wanted, 'Complete unchanged fossil cap coefficients')
        need(m.row_lower[r] == -math.inf and m.row_upper[r] == 23195., 'Original cap unchanged')
        need(sum(e['original_row'] == r and e['side'] == 'upper' for e in endpoints) == 1, 'Each cap expanded exactly once')
        cr = report['caps'][wi]
        need(cr['world'] == world and cr['joint_row'] == r and cr['source_row'] == origin[1] and cr['coefficient_count'] == 3864, 'Cap admission role')
        encoding(cr['expanded_upper'], F(23195) + TAU, float(F(23195) + TAU))
    need(fraction(report['uniform_tau']) == TAU and report['binary_tau'] == 0, 'Exact uniform tau and no state-box tau')
    need((report['original_rows'], report['original_columns'], report['original_coefficients'], report['full_original_bits'], report['phase_rows'], report['phase_columns'], report['phase_coefficients']) == (m.rows, m.cols, len(m.data), sum(mask), nr, nc, len(vals)), 'Admission count agreement')
    plan = read(PRE / 'plan.json')
    need(plan['options'] == {'time_limit': 60., 'threads': 1, 'random_seed': 0, 'presolve': 'on', 'solver': 'simplex'}, 'One prescribed solver option set')
    need(plan['phase_seconds'] == 180. and plan['start_guard'] == 65. and plan['maximum_rational_bits'] == 8192 and plan['calls'] == 1 and plan['alternative_candidates'] == 0, 'Fixed execution budget and candidate denominator')
    need(plan['runtime']['packages'] == {'numpy': '2.3.5', 'scipy': '1.18.1', 'highspy': '1.12.0'}, 'Recorded pinned environment')
    fixtures = read(ARM / 'synthetic_tests.json')
    need(fixtures['status'] == 'PASS' and fixtures['source_sha256'] == PINS[SOURCE] and fixtures['protocol_sha256'] == PINS[PROTOCOL] and len(fixtures['checks']) == 5 and fixtures['scientific_inputs_read'] == fixtures['optimizer_calls'] == 0, 'Original synthetic receipt, not rerun')
    tree = ast.parse(SOURCE.read_text(encoding='utf-8-sig'))
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]
    need(sum(isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name) and n.func.value.id == 'h' and n.func.attr == 'run' for n in calls) == 1, 'Only one source-level h.run call')
    need(not any(isinstance(n.func, ast.Attribute) and n.func.attr in ('getDualRay', 'getIis', 'optimize') for n in calls), 'No hidden ray/IIS/other optimizer route')
    for item in items:
        binding(item)
    need(all(sha(p) == digest for p, digest in initial.items()), 'Transport unchanged')
    need(not (ARM / 'run01').exists(), 'Scientific run remains absent at close')
    result = dict(status='PASS_INDEPENDENT_SOURCE_PREPARED', utc=datetime.now(timezone.utc).isoformat(), reviewer_sha256=sha(__file__), elapsed_seconds=time.perf_counter()-started,
        source_sha256=PINS[SOURCE], protocol_sha256=PINS[PROTOCOL], freeze_sha256=PINS[PRE/'prepared_freeze.json'], input_bindings=len(items), inherited_bindings=len(inherited), inherited_outputs=len(old_outputs), exact_copies=len(copied),
        original_rows=m.rows, original_columns=m.cols, original_coefficients=len(m.data), original_binary_coordinates=sum(mask), phase_rows=nr, phase_columns=nc, phase_coefficients=len(vals),
        source_two_sided_rows=original_two_sided, copied_original_term_uses=copied_terms, every_endpoint_and_coefficient_verified=True, ordered_original_intervals=True, finite_nonempty_original_boxes=True,
        exact_scalar_encodings_checked=scalar_count, nonzero_rounding_errors=rounded_count, cap_rows=cap_rows, unchanged_nominee=True, only_continuous_boxes_expanded=True, binary_tau=0,
        all_frozen_files_unchanged=True, run_absent=True, source_imports=0, optimizer_calls=0, producer_model_generation=0, multiplier_evaluations=0, fractional_control_evaluations=0, old_point_membership_replays=0,
        decoder_reuse=PINS[KERNEL], execution_authorization=False,
        limits=['Numerical phase model is a multiplier proposal; intended rational endpoints are not silently equated to their encodings.', 'Completion final_admission is authoritative; elapsed snapshot and later admission clock may conservatively differ.', '180-second phase and 60-second solver limits are soft; actual owned Windows process chain must be observed before termination. No descendant cleanup test is claimed.', 'Arithmetic guard checks the code-specified accumulators and reconstructed values; not a blanket limit on every transient Python allocation.'])
    with (OUT / 'prepared_review.json').open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, allow_nan=False); stream.write('\n')
    print(json.dumps({'status': result['status'], 'elapsed_seconds': result['elapsed_seconds'], 'report_sha256': sha(OUT / 'prepared_review.json')}))


if __name__ == '__main__':
    try:
        main()
    except BaseException as exc:
        with (OUT / 'prepared_review_failure.json').open('x', encoding='utf-8') as stream:
            json.dump({'reviewer_sha256': sha(__file__), 'error_type': type(exc).__name__, 'message': str(exc), 'optimizer_calls': 0}, stream, indent=2)
        raise
