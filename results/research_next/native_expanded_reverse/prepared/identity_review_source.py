"""Independent saved native-point and finite-box proof replay; stdlib only."""
from pathlib import Path
from fractions import Fraction
from collections import defaultdict, Counter
from datetime import datetime, timezone
import ast, hashlib, json, math, struct, time, zipfile

ROOT = Path(__file__).resolve().parents[3]
ARM = ROOT / 'results/research_next/native_expanded_identity'
PRE, RUN = ARM / 'prepared', ARM / 'run01'
OUT = Path(__file__).with_suffix('.json')
TAU = Fraction.from_float(1e-5)
PINS = {
    PRE / 'prepared_freeze.json': '08429d3134097ba8d8a308559e2dc250c207dca4938af3c2754bb9acdfb6f185',
    PRE / 'manifest.json': '218037265ef5c242f60ee35e54b018e5d7d2bbc58dad0644dd55dd54398538b9',
    Path(__file__).with_name('prepared_review.json'): '316a88195aa609c0c33211e98bdbf5279dc30af52e9fcd86cd5398a6efd8df8b',
}

def need(value, message):
    if not value:
        raise AssertionError(message)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def unique(pairs):
    answer = {}
    for key, value in pairs:
        need(key not in answer, 'Duplicate JSON key')
        answer[key] = value
    return answer

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'), object_pairs_hook=unique)

def q(value):
    need(type(value) in (int, float) and math.isfinite(value), 'Finite archived scalar')
    return Fraction(value)

def record(value):
    return dict(numerator=str(value.numerator), denominator=str(value.denominator), approximate=float(value))

def eqrecord(saved, value, label):
    need(saved == record(value), label)

def bits(value):
    need(set(value) == {'type', 'bits_hex', 'display'} and value['type'] == 'Float64', 'Raw Float64 record')
    payload = bytes.fromhex(value['bits_hex'])
    need(len(payload) == 8, 'Eight raw bytes')
    return q(struct.unpack('>d', payload)[0])

def ends(spec):
    kind = spec['type'].split('.')[-1]
    if kind == 'EqualTo{Float64}':
        point = bits(spec['value'])
        return point, point
    if kind == 'LessThan{Float64}':
        return None, bits(spec['upper'])
    if kind == 'GreaterThan{Float64}':
        return bits(spec['lower']), None
    if kind == 'Interval{Float64}':
        return bits(spec['lower']), bits(spec['upper'])
    raise AssertionError('Unsupported endpoint type ' + kind)

def binding_check(entries):
    for entry in entries:
        data = Path(entry['path']).read_bytes()
        need(len(data) == entry['bytes'] and hashlib.sha256(data).hexdigest() == entry['sha256'], entry['path'])

def aliases(raw, normal):
    roster = {unit['name'] for unit in normal['units']}
    result = {}
    for entry in raw['semantic_aliases']:
        family, key = entry['family'], entry['key']
        if family in ('is_on', 'switch_on', 'switch_off'):
            need(len(key) == 2 and key[0] in roster, 'State alias')
            role = dict(is_on='U', switch_on='Y', switch_off='Z')[family]
            name, hour = role + ':' + key[0] + ':' + str(key[1] - 1), key[1]
        elif family == 'startup':
            need(len(key) == 3 and key[0] in roster and key[2] == 1, 'Single native startup category')
            name, hour = 'D:' + key[0] + ':' + str(key[1] - 1), key[1]
        elif family in ('prod_above', 'mfg'):
            need(len(key) == 3 and key[0] == 's1' and key[1] in roster, 'Production alias')
            role = 'Q' if family == 'prod_above' else 'mfg'
            name, hour = role + ':' + key[1] + ':' + str(key[2] - 1), key[2]
        elif family == 'reserve':
            need(len(key) == 4 and key[0] == 's1' and key[1] == normal['reserve_name'] and key[2] in roster, 'Reserve alias')
            name, hour = 'R:' + key[2] + ':' + str(key[3] - 1), key[3]
        elif family == 'segprod':
            need(len(key) == 4 and key[0] == 's1' and key[1] in roster and key[3] in (1, 2, 3, 4), 'Segment alias')
            name, hour = 'S:' + key[1] + ':' + str(key[2] - 1) + ':' + str(key[3] - 1), key[2]
        else:
            need(family in ('curtail', 'net_injection', 'reserve_shortfall'), 'Known system alias')
            need(len(key) == 3 and key[0] == 's1', 'System alias shape')
            place = normal['reserve_name'] if family == 'reserve_shortfall' else normal['bus']
            need(key[1] == place, 'System alias place')
            role = dict(curtail='C', net_injection='N', reserve_shortfall='F')[family]
            name, hour = role + ':system:' + str(key[2] - 1), key[2]
        need(type(hour) is int and 1 <= hour <= 24 and entry['variable'] not in result, 'Unique complete time alias')
        result[entry['variable']] = name
    ids = [entry['index'] for entry in raw['variables']]
    need(len(ids) == len(set(ids)) == len(result) == len(set(result.values())) == 2712 and set(ids) == set(result), 'Full native alias bijection')
    return result

def row_duals(path):
    # Independent narrow NPY reader: no producer/kernel code is imported.
    with zipfile.ZipFile(path) as archive:
        need(set(archive.namelist()) == {'col_value.npy', 'row_value.npy', 'row_dual.npy', 'col_dual.npy'} and len(archive.namelist()) == 4, 'Frozen LP archive schema')
        need(archive.testzip() is None, 'NPZ CRCs')
        blob = archive.read('row_dual.npy')
    need(blob[:8] == b'\x93NUMPY\x01\x00', 'NPY v1 header')
    size = struct.unpack('<H', blob[8:10])[0]
    header = ast.literal_eval(blob[10:10 + size].decode('latin1'))
    need(header == {'descr': '<f8', 'fortran_order': False, 'shape': (4384,)}, 'Fixed signed-dual array')
    payload = blob[10 + size:]
    need(len(payload) == 4384 * 8, 'Exact NPY payload length')
    return [q(value) for value in struct.unpack('<4384d', payload)]

def main():
    clock = time.perf_counter()
    need(not OUT.exists(), 'New independent replay only')
    for path, expected in PINS.items():
        need(sha(path) == expected, 'Trusted preparation or reviewer receipt')
    manifest = read(PRE / 'manifest.json')
    entries = manifest['inputs'] + list(manifest['copies'].values())
    binding_check(entries)
    snapshot = {path.name: sha(path) for path in RUN.iterdir() if path.is_file()}
    need(set(snapshot) == {'started.json', 'completion.json', 'result.json', 'native_point_check.json', 'native_lower_certificate.json', 'lifted_rational_point.json'}, 'Complete six-file producer run')
    started, completion = read(RUN / 'started.json'), read(RUN / 'completion.json')
    need(started['freeze_sha256'] == PINS[PRE / 'prepared_freeze.json'] and started['manifest_sha256'] == PINS[PRE / 'manifest.json'], 'Run freeze binding')
    need(completion['status'] == 'COMPLETE_PENDING_INDEPENDENT_REVIEW' and completion['all_inputs_unchanged'], 'Closed producer')
    need(completion['arithmetic_runs'] == 1 and completion['optimizer_calls'] == started['optimizer_calls'] == 0, 'One arithmetic run, no solver')
    need(0 <= completion['elapsed_seconds'] <= 120 and completion['final_completion_write_excluded'], 'Timing convention')
    raw, model, normal = read(PRE / 'raw.json'), read(PRE / 'model.json'), read(PRE / 'normal.json')
    names = aliases(raw, normal)
    candidate = read(PRE / 'candidate.json')
    columns = model['columns']
    need(len(columns) == len(candidate) == 2472 and len(model['rows']) == 4384, 'Frozen adapter shape')
    index = {column['name']: j for j, column in enumerate(columns)}
    need(len(index) == 2472 and sum(column['binary'] for column in columns) == 960, 'Complete original mask')
    native_index = {name: number for number, name in names.items()}
    omitted = {name for name in names.values() if name.startswith('mfg:')}
    need(len(omitted) == 240 and set(names.values()) == set(index) | omitted, 'Exact zero-lift complement')
    point = {number: Fraction(0) if name in omitted else q(candidate[index[name]]) for number, name in names.items()}
    saved_lift = read(RUN / 'lifted_rational_point.json')
    need(len(saved_lift) == 2712 and [e['native_index'] for e in saved_lift] == sorted(point), 'Saved lift inventory')
    for entry in saved_lift:
        need(entry['name'] == names[entry['native_index']], 'Lift alias')
        eqrecord(entry['value'], point[entry['native_index']], 'Every unchanged candidate/lift value')

    worst = Fraction(0)
    binary = set()
    counts = Counter()
    domains = {number: [None, None] for number in point}
    affine_signatures = set()
    affine_support = set()
    for row in raw['constraints']:
        fun, spec = row['function'], row['set']
        if fun['type'] == 'MathOptInterface.VariableIndex':
            counts['variable_records'] += 1
            number = fun['variable']
            value = point[number]
            if spec['type'] == 'MathOptInterface.ZeroOne':
                need(number not in binary and value in (0, 1), 'Every exact native binary')
                binary.add(number)
                continue
            lo, hi = ends(spec)
            if lo is not None:
                domains[number][0] = lo if domains[number][0] is None else max(lo, domains[number][0])
            if hi is not None:
                domains[number][1] = hi if domains[number][1] is None else min(hi, domains[number][1])
        else:
            need(fun['type'] == 'MathOptInterface.ScalarAffineFunction{Float64}', 'Raw affine only')
            counts['affine_rows'] += 1
            constant = bits(fun['constant'])
            value = constant
            coeff = defaultdict(Fraction)
            for term in fun['terms']:
                coefficient = bits(term['coefficient'])
                value += coefficient * point[term['variable']]
                coeff[names[term['variable']]] += coefficient
                counts['raw_affine_terms'] += 1
            coeff = {name: value for name, value in coeff.items() if value}
            affine_support.update(coeff)
            lo, hi = ends(spec)
            # Exact upper-halfspace representation, used only for containment premises.
            if hi is not None:
                affine_signatures.add((tuple(sorted(coeff.items())), hi - constant))
            if lo is not None:
                affine_signatures.add((tuple(sorted((name, -a) for name, a in coeff.items())), constant - lo))
        violation = max(Fraction(0), lo - value if lo is not None else Fraction(0), value - hi if hi is not None else Fraction(0))
        worst = max(worst, violation)
        need(violation <= TAU, 'Native expanded endpoint violation')
    need(counts['affine_rows'] == 4384 and counts['variable_records'] == 3696 and len(raw['constraints']) == 8080, 'All native constraint records')
    need(len(binary) == 960 and binary == set(raw['binary_variable_indices']), 'All 960 native declarations')
    need({names[number] for number in binary} == {c['name'] for c in columns if c['binary']}, 'Original binary identity')
    need(not (omitted & affine_support), 'No omitted affine support')
    for name in omitted:
        need(domains[native_index[name]] == [Fraction(0), None], 'Omitted native nonnegative domain')

    objective = bits(raw['objective']['constant'])
    obj_coeff = defaultdict(Fraction)
    for term in raw['objective']['terms']:
        coefficient = bits(term['coefficient'])
        objective += coefficient * point[term['variable']]
        obj_coeff[names[term['variable']]] += coefficient
    need(bits(raw['objective']['constant']) == 0 and raw['objective_sense'] == 'MIN_SENSE', 'Native objective constant/sense')
    need(all(obj_coeff.get(name, 0) == 0 for name in omitted), 'Zero omitted objective support')
    need(all(obj_coeff.get(c['name'], 0) == q(c['objective']) for c in columns), 'Full objective coefficient identity')
    saved_point = read(RUN / 'native_point_check.json')
    need(saved_point['accepted'] and saved_point['strict_nominal'] == (worst == 0) and saved_point['failures'] == [], 'Saved point status')
    eqrecord(saved_point['nominal_max_violation'], worst, 'Exact maximum violation')
    eqrecord(saved_point['objective'], objective, 'Exact raw objective')
    eqrecord(saved_point['tau'], TAU, 'Point expansion rational')
    eqrecord(read(PRE / 'mip_result.json')['accepted_expanded_upper'], objective, 'Old accepted objective unchanged')

    qr = [j for j, c in enumerate(columns) if c['name'].split(':')[0] in ('Q', 'R')]
    need(len(qr) == 480, 'Fixed 480 Q/R columns')
    headroom_pairs = 0
    for j in qr:
        name = columns[j]['name']
        role, unit, hour = name.split(':')
        need(domains[native_index[name]] == [Fraction(0), None], 'Native Q/R lower and no finite upper')
        need(q(columns[j]['lower']) == 0 and q(columns[j]['upper']) >= 0, 'Adapter Q/R domains')
        if role == 'Q':
            other, u = 'R:' + unit + ':' + hour, 'U:' + unit + ':' + hour
            width = q(columns[j]['upper'])
            need(q(columns[index[other]]['upper']) == width and native_index[u] in binary, 'Q/R common width and exact U')
            signature = (tuple(sorted({name: Fraction(1), other: Fraction(1), u: -width}.items())), Fraction(0))
            need(signature in affine_signatures, 'Actual native headroom inequality')
            headroom_pairs += 1
    need(headroom_pairs == 240, 'All 240 paired containment premises')
    for c in columns:
        if c['name'].startswith('N:'):
            need((tuple([(c['name'], Fraction(1))]), Fraction(0)) in affine_signatures and (tuple([(c['name'], Fraction(-1))]), Fraction(0)) in affine_signatures, 'Actual N=0 equality')
            need(q(c['lower']) == q(c['upper']) == 0, 'N adapter box')

    raw_dual = row_duals(PRE / 'raw_lp.npz')
    dual, changed = [], []
    atd = [Fraction(0) for _ in columns]
    beta, row_expanded = Fraction(0), Fraction(0)
    for i, (d, row) in enumerate(zip(raw_dual, model['rows'])):
        if d > 0 and row['lower'] is None or d < 0 and row['upper'] is None:
            d = Fraction(0)
            changed.append(i)
        dual.append(d)
        if d:
            endpoint = q(row['lower'] if d > 0 else row['upper'])
            beta += d * endpoint
            row_expanded += d * (endpoint - TAU if d > 0 else endpoint + TAU)
        for j, coefficient in row['coefficients']:
            atd[j] += d * q(coefficient)
    residual = [q(c['objective']) - a for c, a in zip(columns, atd)]
    nominal = beta
    direct_native = row_expanded
    correction = Fraction(0)
    qr_set = set(qr)
    for j, (c, r) in enumerate(zip(columns, residual)):
        low, high = q(c['lower']), q(c['upper'])
        need(low <= high, 'Finite valid original box')
        nominal += min(r * low, r * high)
        extended_high = high + TAU + (TAU if j in qr_set else Fraction(0))
        direct_native += min(r * (low - TAU), r * extended_high)
        if j in qr_set:
            correction += min(Fraction(0), r * TAU)
    slope = sum((abs(d) for d in dual), Fraction(0)) + sum((abs(r) for r in residual), Fraction(0))
    expanded = nominal - TAU * slope
    need(direct_native == expanded + correction and correction <= 0, 'Independent box minimum/correction identity')
    old, lower = read(PRE / 'signed_bound.json'), read(RUN / 'native_lower_certificate.json')
    need(old['dual_feasibility_required'] is False and old['exact_optimum_claim'] is False, 'Original fixed proof semantics')
    need([q(d) for d in old['projected_dual']] == dual and old['projection_changed_rows'] == changed, 'All original projected multipliers')
    need(lower['changed_rows'] == changed and lower['QR_indices'] == qr, 'Saved indices and projection')
    need(len(lower['projected_multipliers']) == 4384 and len(lower['residual']) == len(old['exact_stationarity_residual']) == 2472, 'Full proof arrays')
    for j, r in enumerate(residual):
        eqrecord(old['exact_stationarity_residual'][j], r, 'Old residual')
        eqrecord(lower['residual'][j], r, 'Saved residual')
    for saved, d in zip(lower['projected_multipliers'], dual):
        eqrecord(saved, d, 'Saved projected multiplier')
    for key, value in dict(beta=beta, nominal_lower_bound=nominal, expanded_lower_bound=expanded, expansion_slope=slope, tau=TAU).items():
        eqrecord(old[key], value, 'Old exact proof ' + key)
    for key, value in dict(tau=TAU, old_expanded_lower=expanded, additional_QR_upper_support_correction=correction,
                           native_expanded_lower=direct_native, row_endpoint_sum_nominal=beta, nominal_lower=nominal, expansion_slope=slope).items():
        eqrecord(lower[key], value, 'Native exact proof ' + key)
    eqrecord(read(PRE / 'lp_result.json')['selected_expanded_lower'], expanded, 'Fixed selected proof')
    need(lower['direct_widened_endpoint_sum_agrees'] and lower['no_new_ray_or_dual'] and lower['optimizer_calls'] == 0, 'Saved lower scope')
    result = read(RUN / 'result.json')
    need(result['status'] == 'CERTIFIED_FINITE_NATIVE_EXPANDED_IDENTITY_BRACKET' and direct_native <= objective, 'Ordered finite bracket')
    eqrecord(result['native_expanded_lower'], direct_native, 'Result lower')
    eqrecord(result['native_expanded_upper'], objective, 'Result upper')
    need(result['strict_nominal_upper'] is None and worst > 0, 'Strict nominal upper absent')
    need(result['containment_only'] and not result['expanded_model_equivalence_claim'] and not result['target_cost_difference_claim'] and not result['exact_optimality_claim'], 'Scientific scope')
    binding_check(entries)
    for path, expected in PINS.items():
        need(sha(path) == expected, 'Unchanged trusted transport')
    need(snapshot == {path.name: sha(path) for path in RUN.iterdir() if path.is_file()}, 'Six producer files unchanged')
    report = dict(status='PASS_INDEPENDENT_NATIVE_EXPANDED_POINT_AND_LOWER_REPLAY', utc=datetime.now(timezone.utc).isoformat(),
        elapsed_seconds=time.perf_counter() - clock, reviewer_sha256=sha(__file__), prepared_freeze_sha256=PINS[PRE / 'prepared_freeze.json'],
        originals_verified_twice=37, copies_verified_twice=23, producer_outputs_unchanged=snapshot,
        native_variables=2712, retained_candidate_values=2472, zero_lift_variables=240,
        native_constraint_records=8080, affine_rows=4384, variable_constraint_records=3696,
        original_binary_declarations=960, raw_affine_term_uses=counts['raw_affine_terms'],
        native_expanded_point_accepted=True, native_strict_nominal_point_accepted=False,
        nominal_max_violation=record(worst), native_encoded_objective=record(objective),
        signed_row_multipliers=4384, exact_residual_coordinates=2472, QR_coordinates=480,
        headroom_pairs_rechecked=240, original_expanded_lower=record(expanded),
        additional_QR_upper_support_correction=record(correction), native_expanded_lower=record(direct_native),
        native_expanded_upper=record(objective), strict_nominal_upper=None, exact_bracket_width=record(objective-direct_native),
        producer_elapsed_seconds=completion['elapsed_seconds'], helper_imports=0, producer_imports=0,
        optimizer_calls=0, Julia_calls=0, native_builds=0, new_candidates=0,
        independent_arithmetic='Raw MOI term evaluation and narrow NPY struct decoder; exact signed multipliers plus explicit interval minima',
        inherited_nominal_proof='50191cce91e6a4e8479500bfa0a1740b03d812848ee37620480b3e41ce584080',
        scope='One native-expanded binary identity encoded-cost bracket by nominal correspondence plus containment; no equality, target difference, physical uncertainty or exact optimality claim')
    with OUT.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'status': report['status'], 'elapsed_seconds': report['elapsed_seconds'], 'lower': float(direct_native), 'upper': float(objective), 'correction': float(correction)}))

if __name__ == '__main__':
    main()
