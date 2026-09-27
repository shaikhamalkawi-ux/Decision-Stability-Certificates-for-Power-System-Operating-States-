"""One Fraction-valued nominal identity witness proposal; no solver or model build."""
from pathlib import Path
from fractions import Fraction
from datetime import datetime, timezone
import argparse, hashlib, importlib.util, json, math, sys, time

F = Fraction
ROOT = Path(__file__).resolve().parents[1]
ARM = ROOT / 'results/research_next/nominal_identity'
PRE, RUN = ARM / 'prepared', ARM / 'run01'
PROTOCOL = ROOT / 'docs/research_next/NOMINAL_IDENTITY_PROTOCOL.md'
OLD = ROOT / 'results/research_next/native_expanded_identity'
LIMIT, BITS, DENOM = 90.0, 512, 1000000
HELPER_SHA = '6390b0f51a9385860ff28683c2610008173ea0fcb8b1ed40b686cbbfd7c06d3c'
PINS = {
    'old_manifest': (OLD/'prepared/manifest.json', '218037265ef5c242f60ee35e54b018e5d7d2bbc58dad0644dd55dd54398538b9'),
    'old_result': (OLD/'run01/result.json', '630481bb4b8249539811a76cbf9197cd6ca577c3c131b21a234d6b6cb64b9c0f'),
    'old_review': (ROOT/'results/research_next/native_expanded_identity_independent_review/postrun_review.json', '8f13f3a1751e03f2e4487127159420d14717bfff2b2c810a5c829f13bfa1b2e1'),
    'proposal': (ROOT/'docs/research_next/NOMINAL_IDENTITY_RECONSTRUCTION_PROPOSAL.md', '29d9a994aee6fe332bbc18da3dbe003447273331931ed566fe11a6b34fca3c4f'),
    'raw': (OLD/'prepared/raw.json', '028ca4d025389eecd6fa91dc278b32f262a358eede3dece50d05080cc61b0160'),
    'normal': (OLD/'prepared/normal.json', 'be57cd1fd925fb5c106b8e90979dcc866c0b27068b368ec018e4068d03067df8'),
    'model': (OLD/'prepared/model.json', '5abc7c12289d6428081f49646553863abaa041abfd4bac6215d7d49130b2f725'),
    'candidate': (OLD/'prepared/candidate.json', 'c24e7218930cf26a18dd1c2fc0fe7f36d1a180580c447ab5307fe07ee8781f6c'),
    'helper': (OLD/'prepared/helper.py', HELPER_SHA),
}


def require(ok, why):
    if not ok:
        raise ValueError(why)


class ConstructionFailure(Exception):
    pass


def construct_need(ok, why):
    if not ok:
        raise ConstructionFailure(why)


def checked(x):
    require(isinstance(x, F), 'Exact Fraction required')
    require(abs(x.numerator).bit_length() <= BITS and x.denominator.bit_length() <= BITS, '512-bit arithmetic guard')
    return x


def frac(x):
    if isinstance(x, F):
        return checked(x)
    require(type(x) in (int, float) and math.isfinite(x), 'Finite original binary64/int')
    return checked(F(x))


def ssum(values):
    out = F(0)
    for value in values:
        out = checked(out + checked(value))
    return out


def rational(x):
    x = checked(x)
    return {'numerator': str(x.numerator), 'denominator': str(x.denominator), 'approximate': float(x)}


def unrat(x):
    return checked(F(int(x['numerator']), int(x['denominator'])))


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))


def save(p, value):
    with Path(p).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def binding(p):
    p = Path(p).resolve()
    data = p.read_bytes()
    return {'path': str(p), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def validate(items):
    for item in items:
        require(binding(item['path']) == item, 'Changed input ' + item['path'])


def utc():
    return datetime.now(timezone.utc).isoformat()


def guard(start):
    require(time.perf_counter() - start <= LIMIT, '90-second soft phase exceeded')


def column_name(family, g, t, k=None):
    return f'{family}:{g}:{t}' + (f':{k}' if k is not None else '')


def load_helper(path):
    require(sha(path) == HELPER_SHA, 'Pinned raw-native coefficient/alias helper')
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location('nominal_identity_native_decoder', path)
    helper = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = helper
    spec.loader.exec_module(helper)
    return helper


def greedy_segments(amount, allowances):
    construct_need(amount >= 0 and all(a >= 0 for a in allowances), 'Negative Q or segment allowance')
    result = []
    for allowance in allowances:
        value = min(amount, allowance)
        result.append(value)
        amount = checked(amount - value)
    construct_need(amount == 0, 'Q exceeds total exact segment allowances')
    return result


def intersect(interval, coefficient, constant, lower, upper):
    require(coefficient != 0, 'Nonzero R coefficient')
    lo, hi = interval
    for endpoint, lower_side in ((lower, True), (upper, False)):
        if endpoint is None:
            continue
        threshold = checked(checked(endpoint - constant) / coefficient)
        if lower_side == (coefficient > 0):
            lo = max(lo, threshold)
        else:
            hi = min(hi, threshold)
    construct_need(lo <= hi, 'Empty exact R interval')
    return lo, hi


def fill_reserve(intervals, required):
    values = [lo for lo, _ in intervals]
    deficit = max(F(0), checked(required - ssum(values)))
    for i, (lo, hi) in enumerate(intervals):
        amount = min(deficit, checked(hi - lo))
        values[i] = checked(values[i] + amount)
        deficit = checked(deficit - amount)
    construct_need(deficit == 0, 'Insufficient exact reserve interval room')
    return values


def row_violation(row, activity):
    return max(F(0), F(0) if row['lower'] is None else checked(frac(row['lower']) - activity),
               F(0) if row['upper'] is None else checked(activity - frac(row['upper'])))


def construct(model, normal, old, start, ledger):
    columns, rows = model['columns'], model['rows']
    names = {c['name']: j for j, c in enumerate(columns)}
    require(len(names) == len(columns) == 2472, 'Complete unique retained columns')
    require(model['order'] == list(range(24)) and model['variant'] == 'native_penalized', 'Fixed identity service')
    require(len(normal['units']) == 10 and len(rows) == 4384, 'Fixed model shape')
    oldq = list(map(frac, old))
    require(len(oldq) == len(columns), 'Original candidate shape')
    x = [None] * len(columns)
    ledger['partial_values'] = x
    binary_indices = [j for j, c in enumerate(columns) if c['binary']]
    require(len(binary_indices) == 960, 'Full original binary mask')
    for j in binary_indices:
        require(oldq[j] in (0, 1) and columns[j]['name'].split(':')[0] in ('U', 'Y', 'Z', 'D'), 'Exact original bits')
        x[j] = oldq[j]
    at = lambda f, g, t, k=None: names[column_name(f, g, t, k)]
    ledger['stage'] = 'Q_reconstruction'
    for g in normal['units']:
        for t in range(24):
            j = at('Q', g['name'], t)
            x[j] = checked(oldq[j].limit_denominator(DENOM))
    ledger['stage'] = 'segments'
    for g in normal['units']:
        for t in range(24):
            u = x[at('U', g['name'], t)]
            result = greedy_segments(x[at('Q', g['name'], t)], [checked(frac(w) * u) for w in g['widths']])
            for k, value in enumerate(result):
                x[at('S', g['name'], t, k)] = value
    ledger['stage'] = 'system_balance'
    for t in range(24):
        x[at('F', 'system', t)] = x[at('N', 'system', t)] = F(0)
        production = ssum(checked(frac(g['pmin']) * x[at('U', g['name'], t)] + x[at('Q', g['name'], t)]) for g in normal['units'])
        j = at('C', 'system', t)
        x[j] = checked(frac(normal['load'][t]) - production)
        construct_need(frac(columns[j]['lower']) <= x[j] <= frac(columns[j]['upper']), 'C outside nominal box')
    rindices = {at('R', g['name'], t) for g in normal['units'] for t in range(24)}
    require(len(rindices) == 240 and {j for j, v in enumerate(x) if v is None} == rindices, 'Only R remains unset')
    ledger['stage'] = 'reserve_schema'
    reserve_rows = {}
    for t in range(24):
        matching = [(i, row) for i, row in enumerate(rows) if row['name'] == f'reserve:{t}']
        require(len(matching) == 1, 'One original reserve row per hour')
        i, row = matching[0]
        expected = {at('R', g['name'], t): F(1) for g in normal['units']}
        expected[at('F', 'system', t)] = F(1)
        require(len(row['coefficients']) == len(expected) and {j: frac(a) for j, a in row['coefficients']} == expected,
                'Exact full reserve support before substitution')
        require(row['upper'] is None and row['lower'] is not None and frac(row['lower']) == frac(normal['reserve'][t]), 'Exact reserve endpoint')
        reserve_rows[i] = t
    intervals = {j: (frac(columns[j]['lower']), frac(columns[j]['upper'])) for j in rindices}
    ledger['stage'] = 'R_intersections'
    counts = {'zero_R_rows': 0, 'one_R_rows': 0, 'reserve_rows': len(reserve_rows)}
    provenance = {j: [] for j in rindices}
    for i, row in enumerate(rows):
        if i % 128 == 0:
            guard(start)
        if i in reserve_rows:
            continue
        support = [(j, frac(a)) for j, a in row['coefficients'] if j in rindices]
        require(len(support) <= 1, 'Unrecognized multiple-R row')
        activity = ssum(checked(frac(a) * x[j]) for j, a in row['coefficients'] if j not in rindices)
        if not support:
            counts['zero_R_rows'] += 1
            construct_need(row_violation(row, activity) == 0, f'Nominal non-R row fails: {i}:{row["name"]}')
        else:
            counts['one_R_rows'] += 1
            j, coefficient = support[0]
            intervals[j] = intersect(intervals[j], coefficient, activity,
                                     None if row['lower'] is None else frac(row['lower']),
                                     None if row['upper'] is None else frac(row['upper']))
            provenance[j].append(i)
    ledger['intervals'] = [{'column': j, 'lower': rational(intervals[j][0]), 'upper': rational(intervals[j][1]),
                            'all_source_rows': provenance[j]} for j in sorted(rindices)]
    ledger['row_counts'] = counts
    ledger['stage'] = 'reserve_fill'
    for t in range(24):
        js = [at('R', g['name'], t) for g in normal['units']]
        values = fill_reserve([intervals[j] for j in js], frac(normal['reserve'][t]))
        for j, value in zip(js, values):
            x[j] = value
    require(all(isinstance(v, F) for v in x) and all(x[j] == oldq[j] for j in binary_indices), 'Complete rational point/unchanged bits')
    ledger['stage'] = 'constructed'
    return x


def matrix_check(model, x, start):
    failures, worst = [], F(0)
    for j, (c, value) in enumerate(zip(model['columns'], x)):
        violation = max(F(0), checked(frac(c['lower']) - value), checked(value - frac(c['upper'])))
        worst = max(worst, violation)
        if violation or (c['binary'] and value not in (0, 1)):
            failures.append({'column': j, 'violation': rational(violation), 'nonbinary': c['binary'] and value not in (0, 1)})
    for i, row in enumerate(model['rows']):
        if i % 128 == 0:
            guard(start)
        activity = ssum(checked(frac(a) * x[j]) for j, a in row['coefficients'])
        violation = row_violation(row, activity)
        worst = max(worst, violation)
        if violation:
            failures.append({'row': i, 'violation': rational(violation)})
    objective = ssum(checked(frac(c['objective']) * x[j]) for j, c in enumerate(model['columns']))
    return {'accepted': not failures, 'tau': rational(F(0)), 'columns': len(x), 'rows': len(model['rows']),
            'max_violation': rational(worst), 'objective': rational(objective), 'failures': failures}


def native_check(raw, normal, model, x, helper, start):
    alias = helper.aliases_from_expected(raw, normal)
    retained = {c['name']: x[j] for j, c in enumerate(model['columns'])}
    values = {i: F(0) if name.startswith('mfg:') else retained[name] for i, name in alias.items()}
    byname = {alias[i]: value for i, value in values.items()}
    failures, worst, binary = [], F(0), []
    affine = variable = 0
    for k, row in enumerate(raw['constraints']):
        if k % 128 == 0:
            guard(start)
        fn, endpoint = row['function'], row['set']
        if fn['type'] == 'MathOptInterface.VariableIndex':
            variable += 1
            activity = values[fn['variable']]
            if endpoint['type'] == 'MathOptInterface.ZeroOne':
                binary.append(fn['variable'])
                if activity not in (0, 1):
                    failures.append({'record': k, 'nonbinary': True})
                continue
        else:
            affine += 1
            coefficients, constant = helper.terms(fn, alias)
            activity = checked(constant + ssum(checked(a * byname[name]) for name, a in coefficients.items()))
        lo, hi = helper.endpoints(endpoint)
        violation = max(F(0), F(0) if lo is None else checked(lo - activity), F(0) if hi is None else checked(activity - hi))
        worst = max(worst, violation)
        if violation:
            failures.append({'record': k, 'violation': rational(violation)})
    require(len(binary) == len(set(binary)) == 960 and set(binary) == set(raw['binary_variable_indices']), 'Complete native exact bits')
    require(len(values) == 2712 and affine == 4384 and variable == 3696 and raw['objective_sense'] == 'MIN_SENSE', 'Full native scope')
    coefficients, constant = helper.terms(raw['objective'], alias)
    objective = checked(constant + ssum(checked(a * byname[name]) for name, a in coefficients.items()))
    return [{'native_index': i, 'name': alias[i], 'value': rational(values[i])} for i in sorted(values)], {
        'accepted': not failures, 'tau': rational(F(0)), 'native_variables': len(values), 'affine_rows': affine,
        'variable_records': variable, 'exact_bits': 960, 'max_violation': rational(worst),
        'objective': rational(objective), 'failures': failures, 'mfg_lift': 0}


def prepare():
    require(not PRE.exists() and not RUN.exists(), 'Fresh preparation only')
    fixed = {name: path for name, (path, _) in PINS.items()}
    for path, expected in PINS.values():
        require(sha(path) == expected, 'Pinned historical evidence')
    fixed['theory_review'] = ROOT/'docs/research_next/NOMINAL_IDENTITY_RECONSTRUCTION_REVIEW.md'
    fixed['old_semantic_source'] = ROOT/'src/researchnext_orlib_uc.py'
    old = read(fixed['old_manifest'])
    originals = {e['path']: e for e in old['inputs'] + list(old['copies'].values())}
    for p in list(fixed.values()) + [Path(__file__), PROTOCOL, ARM/'synthetic_controls.json']:
        e = binding(p)
        require(e['path'] not in originals or originals[e['path']] == e, 'Consistent transitive binding')
        originals[e['path']] = e
    validate(list(originals.values()))
    captured = {name: path.read_bytes() for name, path in fixed.items()}
    for name, data in captured.items():
        e = originals[str(fixed[name].resolve())]
        require(len(data) == e['bytes'] and hashlib.sha256(data).hexdigest() == e['sha256'], 'Captured fixed bytes')
    PRE.mkdir(parents=True)
    copies = {}
    for name, data in captured.items():
        out = PRE/(name + fixed[name].suffix)
        out.write_bytes(data)
        require(out.read_bytes() == data, 'Copy readback')
        copies[name] = binding(out)
    validate(list(originals.values()))
    save(PRE/'manifest.json', {'utc': utc(), 'inputs': list(originals.values()), 'copies': copies,
                              'source_sha256': sha(__file__), 'protocol_sha256': sha(PROTOCOL),
                              'candidate_reconstructions': 0, 'optimizer_calls': 0})
    save(PRE/'freeze.json', {'utc': utc(), 'manifest_sha256': sha(PRE/'manifest.json'), 'source_sha256': sha(__file__),
                            'protocol_sha256': sha(PROTOCOL), 'inputs': len(originals), 'copies': len(copies), 'no_scientific_arithmetic': True})
    print(json.dumps({'status': 'PREPARED_ONLY', 'freeze_sha256': sha(PRE/'freeze.json')}))


def run(expected):
    start = time.perf_counter()
    require(not RUN.exists() and sha(PRE/'freeze.json') == expected, 'One frozen run')
    freeze = read(PRE/'freeze.json')
    require(sha(PRE/'manifest.json') == freeze['manifest_sha256'], 'Frozen manifest')
    manifest = read(PRE/'manifest.json')
    validate(manifest['inputs']); validate(list(manifest['copies'].values()))
    require(sha(__file__) == manifest['source_sha256'] and sha(PROTOCOL) == manifest['protocol_sha256'], 'Frozen implementation')
    readcopy = lambda name: read(manifest['copies'][name]['path'])
    RUN.mkdir()
    save(RUN/'started.json', {'utc': utc(), 'freeze_sha256': expected, 'optimizer_calls': 0, 'candidate_limit': 1})
    ledger = {}
    try:
        model, normal, old = readcopy('model'), readcopy('normal'), readcopy('candidate')
        construction_error = None
        try:
            x = construct(model, normal, old, start, ledger)
        except ConstructionFailure as exc:
            construction_error = str(exc)
            x = None
        partial = ledger.pop('partial_values', None)
        save(RUN/'construction.json', {**ledger, 'complete': x is not None, 'construction_failure': construction_error,
             'partial_or_complete_point': [None if v is None else rational(v) for v in partial], 'denominator_ceiling_Q': DENOM})
        result = {'status': 'NO_NOMINAL_WITNESS_FROM_THIS_CONSTRUCTION', 'nominal_feasibility': 'UNKNOWN',
                  'optimizer_calls': 0, 'Julia_calls': 0, 'candidates': 1, 'old_point_unchanged': True, 'exact_optimality_claim': False}
        if x is not None:
            save(RUN/'rational_point.json', [{'column': j, 'name': c['name'], 'value': rational(x[j])} for j, c in enumerate(model['columns'])])
            helper = load_helper(Path(manifest['copies']['helper']['path']))
            matrix = matrix_check(model, x, start)
            semantic = semantic_check(normal, model, x, 0)
            guard(start)
            lifted, native = native_check(readcopy('raw'), normal, model, x, helper, start)
            require(matrix['objective'] == native['objective'] == semantic['exact_saved_segment_objective'], 'All exact objective interpretations')
            save(RUN/'native_lift.json', lifted)
            save(RUN/'point_checks.json', {'matrix': matrix, 'semantic': semantic, 'native': native,
                 'fraction_candidate_never_float_roundtripped': True, 'semantic_implementation_source_adapted_not_independent': True})
            old_result = readcopy('old_result')
            upper, lower = unrat(native['objective']), unrat(old_result['native_expanded_lower'])
            changed = [j for j, value in enumerate(x) if value != frac(old[j])]
            require(not any(model['columns'][j]['binary'] for j in changed), 'No state changes')
            curtail = ssum(x[j] for j, c in enumerate(model['columns']) if c['name'].startswith('C:'))
            result.update(changed_continuous_columns=changed, changed_count=len(changed), maximum_coordinate_denominator=str(max(v.denominator for v in x)),
                          curtailment_MWh=rational(curtail), hard_service_claim=False,
                          difference_from_old_expanded_upper=rational(upper-unrat(old_result['native_expanded_upper'])))
            if matrix['accepted'] and semantic['accepted'] and native['accepted']:
                require(lower <= upper, 'Lower/upper consistency')
                result.update(status='VERIFIED_NOMINAL_IDENTITY_WITNESS_PENDING_INDEPENDENT_REVIEW', nominal_feasibility='FEASIBLE',
                              nominal_upper=rational(upper), inherited_lower_from_native_expanded_set=rational(lower),
                              lower_is_weaker_expanded_certificate=True, tau=rational(F(0)))
        save(RUN/'result.json', result)
        validate(manifest['inputs']); validate(list(manifest['copies'].values()))
        require(sha(PRE/'freeze.json') == expected and sha(PRE/'manifest.json') == freeze['manifest_sha256'], 'Transport unchanged')
        guard(start)
        save(RUN/'completion.json', {'utc': utc(), 'status': 'CLOSED_PENDING_INDEPENDENT_REVIEW', 'elapsed_seconds': time.perf_counter()-start,
             'optimizer_calls': 0, 'all_inputs_unchanged': True, 'candidate_attempts': 1, 'final_completion_write_excluded': True, 'no_retry': True})
        print(json.dumps({'status': result['status'], 'optimizer_calls': 0}))
    except BaseException as exc:
        partial = ledger.get('partial_values')
        save(RUN/'failure.json', {'utc': utc(), 'error_type': type(exc).__name__, 'message': str(exc), 'stage': ledger.get('stage'),
             'elapsed_seconds': time.perf_counter()-start, 'candidate_attempts': 1, 'no_nominal_verdict': True, 'no_retry': True,
             'partial_point': None if partial is None else [None if v is None else [str(v.numerator), str(v.denominator)] for v in partial]})
        raise


def self_test():
    require(not (ARM/'synthetic_controls.json').exists(), 'One invented fixture pass')
    approximate = F.from_float(0.3333333333333333).limit_denominator(DENOM)
    require(approximate == F(1, 3) and approximate != F.from_float(0.3333333333333333), 'Rational reconstruction does not imply encoded equality')
    require(greedy_segments(F(5), [F(2), F(3), F(4)]) == [F(2), F(3), F(0)], 'Exact segment allocation')
    for action in (lambda: greedy_segments(F(10), [F(9)]), lambda: intersect((F(0), F(1)), F(1), F(0), F(2), None),
                   lambda: fill_reserve([(F(0), F(1))], F(2))):
        try:
            action()
        except ConstructionFailure:
            pass
        else:
            raise ValueError('Expected failed construction')
    require(intersect((F(0), F(10)), F(-2), F(3), F(-9), F(-1)) == (F(2), F(6)), 'Negative coefficient endpoints')
    require(fill_reserve([(F(1), F(3)), (F(2), F(5))], F(8)) == [F(3), F(5)], 'Exact equality at total reserve capacity')
    require(fill_reserve([(F(1), F(3)), (F(2), F(5))], F(2)) == [F(1), F(2)], 'Already sufficient lower sum')
    require(row_violation({'lower': None, 'upper': 0}, F(1, 10**20)) > 0, 'Tiny strict violation is rejected')
    bits = (F(0), F(1), F(1), F(0)); copy = list(bits)
    require(tuple(copy) == bits and all(v in (0, 1) for v in copy), 'Original bits exact')
    ARM.mkdir(parents=True, exist_ok=True)
    save(ARM/'synthetic_controls.json', {'utc': utc(), 'status': 'PASS', 'checks': 9, 'source_sha256': sha(__file__),
         'protocol_sha256': sha(PROTOCOL), 'scientific_candidate_reads': 0, 'optimizer_calls': 0})
    print('PASS 9 invented control groups')


# Fraction-aware semantic_check is inserted from the frozen source specification
# during authoring; it is not an independent implementation of those equations.

def semantic_check(case, model, vector, tau=0.0):
    """Equation-level audit from case and named vector; never reads row coefficients."""
    require(len(vector) == len(model["columns"]), "Direct vector dimension mismatch")
    values = {c["name"]: frac(v) for c, v in zip(model["columns"], vector)}
    require(len(values) == len(vector), "Duplicate column names")
    tolerance, failures, worst = frac(tau), [], Fraction(0)
    require(tolerance >= 0, "Negative tolerance")

    def get(f, g, t, k=None):
        return values[column_name(f, g, t, k)]

    def bounded(label, value, lo, hi):
        nonlocal worst
        violation = max(Fraction(0), value - hi, lo - value)
        worst = max(worst, violation)
        if violation > tolerance:
            failures.append(label)

    def le(label, value, bound):
        nonlocal worst
        violation = max(Fraction(0), value - bound)
        worst = max(worst, violation)
        if violation > tolerance:
            failures.append(label)

    def equal(label, a, b):
        bounded(label, a, b, b)

    total_cost, canonical_cost = Fraction(0), Fraction(0)
    canonical_domain_failures = []
    horizon, order = case["horizon"], model["order"]
    require(sorted(order) == list(range(horizon)), "Invalid direct-check order")
    for g in case["units"]:
        n, width = g["name"], frac(float(g["pmax"] - g["pmin"]))
        for t in range(horizon):
            u, y, z, d, q, r = [get(f, n, t) for f in ("U", "Y", "Z", "D", "Q", "R")]
            for f, value in zip(("U", "Y", "Z", "D"), (u, y, z, d)):
                if value not in (0, 1):
                    failures.append(f"binary:{f}:{n}:{t}")
            bounded(f"q:{n}:{t}", q, Fraction(0), width)
            bounded(f"r:{n}:{t}", r, Fraction(0), width)
            previous = Fraction(g["age"] > 0) if t == 0 else get("U", n, t - 1)
            equal(f"link:{n}:{t}", u - previous, y - z)
            le(f"exclusive:{n}:{t}", y + z, Fraction(1))
            equal(f"category:{n}:{t}", d, y)
            le(f"minup:{n}:{t}", sum((get("Y", n, s) for s in range(max(0, t - g["up"] + 1), t + 1)), Fraction(0)), u)
            le(f"mindown:{n}:{t}", sum((get("Z", n, s) for s in range(max(0, t - g["down"] + 1), t + 1)), Fraction(0)), 1 - u)
            le(f"headroom:{n}:{t}", q + r, width * u)
            seg = [get("S", n, t, k) for k in range(4)]
            for k in range(4):
                bounded(f"segment_box:{n}:{t}:{k}", seg[k], Fraction(0), frac(g["widths"][k]))
                le(f"segment_on:{n}:{t}:{k}", seg[k], frac(g["widths"][k]) * u)
            equal(f"production_definition:{n}:{t}", sum(seg, Fraction(0)), q)
            # Nonbinding SU/SD corrections are zero, but these native rows remain.
            le(f"startup_limit:{n}:{t}", q + r, width * u)
            if t + 1 < horizon:
                le(f"shutdown_limit:{n}:{t}", q, width * u)
            if t:
                le(f"ramp_up:{n}:{t}", q + r - get("Q", n, t - 1), frac(g["ru"]))
                le(f"ramp_down:{n}:{t}", get("Q", n, t - 1) + get("R", n, t - 1) - q, frac(g["rd"]))
            elif g["age"] > 0:
                le(f"initial_ramp_up:{n}", q + r, frac(float(float(g["initial_power"] + g["ru"]) - g["pmin"])))
                le(f"initial_ramp_down:{n}", -q, frac(float(g["rd"] - float(g["initial_power"] - g["pmin"]))))
            total_cost += frac(g["min_cost"]) * u + frac(g["startup_cost"]) * d
            total_cost += sum((frac(s) * v for s, v in zip(g["slopes"], seg)), Fraction(0))
            # Diagnostic canonical production cost; never replace saved segment objective.
            canonical_cost += frac(g["min_cost"]) * u + frac(g["startup_cost"]) * d
            nominal_capacity = sum((frac(w) for w in g["widths"]), Fraction(0)) * u
            if u not in (0, 1) or q < 0 or q > nominal_capacity:
                canonical_domain_failures.append(f"outside_nominal_PWL_domain:{n}:{t}")
            else:
                remaining = q
                for k in range(4):
                    amount = min(remaining, frac(g["widths"][k]) * u)
                    canonical_cost += amount * frac(g["slopes"][k])
                    remaining -= amount
        residual = g["up"] - g["age"] if g["age"] > 0 else g["down"] + g["age"]
        forbidden = "Z" if g["age"] > 0 else "Y"
        equal(f"initial_dwell:{n}", sum((get(forbidden, n, t) for t in range(max(0, min(residual, horizon)))), Fraction(0)), Fraction(0))
    for t, src in enumerate(order):
        curtail, shortfall, injection = (get(f, "system", t) for f in ("C", "F", "N"))
        maximum = frac(case["load"][src]) if model["variant"] == "native_penalized" else Fraction(0)
        bounded(f"curtail:{t}", curtail, Fraction(0), maximum)
        bounded(f"shortfall:{t}", shortfall, Fraction(0), Fraction(0))
        bounded(f"injection_box:{t}", injection, Fraction(0), Fraction(0))
        production = sum((frac(g["pmin"]) * get("U", g["name"], t) + get("Q", g["name"], t) for g in case["units"]), Fraction(0))
        equal(f"nodal:{t}", production + curtail - injection, frac(case["load"][src]))
        equal(f"balance:{t}", injection, Fraction(0))
        available_reserve = shortfall + sum((get("R", g["name"], t) for g in case["units"]), Fraction(0))
        le(f"reserve:{t}", frac(case["reserve"][src]), available_reserve)
        total_cost += curtail * frac(case["penalty"][src])
        canonical_cost += curtail * frac(case["penalty"][src])
    matrix_cost = sum((frac(c["objective"]) * values[c["name"]] for c in model["columns"]), Fraction(0))
    if matrix_cost != total_cost:
        failures.append("objective_coefficients_disagree_with_native_cost")
    return {"accepted": not failures, "tau": rational(tolerance), "nominal_max_violation": rational(worst),
            "exact_saved_segment_objective": rational(total_cost),
            "canonical_greedy_cost_diagnostic": None if canonical_domain_failures else rational(canonical_cost),
            "canonical_domain_failures": canonical_domain_failures,
            "canonical_cost_is_not_substituted_for_saved_objective": True, "failures": failures}



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('self-test', 'prepare-only', 'run-prepared'))
    parser.add_argument('--expected-freeze-sha256')
    args = parser.parse_args()
    if args.mode == 'self-test':
        self_test()
    elif args.mode == 'prepare-only':
        prepare()
    else:
        require(args.expected_freeze_sha256 is not None, 'Explicit external freeze required')
        run(args.expected_freeze_sha256)
