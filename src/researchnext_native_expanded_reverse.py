"""One fixed reverse native-expanded cost certificate; no optimizer or new point."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
from datetime import datetime, timezone
import argparse, hashlib, importlib.util, json, math, sys, time

ROOT = Path(__file__).resolve().parents[1]
ARM = ROOT/'results/research_next/native_expanded_reverse'
PRE, RUN = ARM/'prepared', ARM/'run01'
PROTOCOL = ROOT/'docs/research_next/NATIVE_EXPANDED_REVERSE_PROTOCOL.md'
COMPARE = ROOT/'results/research_next/native_reverse_compare'
IDENTITY = ROOT/'results/research_next/native_expanded_identity'
OLD = ROOT/'results/research_next/orlib_preflight/solver_prepared01'
CASE = OLD/'outputs/reverse_4_19__native_penalized'
ORDER = [0,1,2,3,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,20,21,22,23]
TAU, LIMIT = F.from_float(1e-5), 120.0
PINS = {
 'helper': (ROOT/'results/research_next/orlib_native_compare_schema2/INDEPENDENT_POSTRUN_REVIEW.py', '6390b0f51a9385860ff28683c2610008173ea0fcb8b1ed40b686cbbfd7c06d3c'),
 'kernel': (ROOT/'src/research8h_standalone_verify.py', '708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'),
 'reuse_source': (ROOT/'src/researchnext_native_expanded_identity.py', 'fca0051ebb46cd8128a141e868877b2206bc3b8962b4b83fac43bbea9095129d'),
 'proposal': (ROOT/'docs/research_next/NATIVE_EXPANDED_REVERSE_PROPOSAL.md', 'c9e3504fca0333150bad9edb5c872d8992be1f156169794866884414289d19bd'),
 'theory': (ROOT/'docs/research_next/NATIVE_EXPANDED_CONTAINMENT_PROPOSAL.md', 'b5342b65753d4440c0c19551dba45fb100731cb4fcd9206499ac38a6c23fc1db'),
 'theory_review': (ROOT/'docs/research_next/NATIVE_EXPANDED_CONTAINMENT_REVIEW.md', '20747ec68fb217c65c11779263851bae793c758a19c0be046c889ed93a5c5adb'),
 'comparison_review': (COMPARE/'INDEPENDENT_POSTRUN_REVIEW.json', 'bb44ef305c468a9e334a0a8e5ee63fc84ac8e87aec057c8e05e21ad07a2f8cc6'),
 'comparison': (COMPARE/'run01/comparison.json', 'dadab7744fc3d6f7080c19d2ed550de8a2830c7f019bf482d74dbb2b798364b9'),
 'comparison_manifest': (COMPARE/'prepared/manifest.json', 'b594e558f7587a1667407d48d39d0bc9f4c7a6804620121e438908d804eb4fc4'),
 'comparison_source': (ROOT/'src/researchnext_native_reverse_compare.py', 'd119ee515815281bf95bd3f669b0bc5a657ed8be90161fe2fd6de6489cfa1e82'),
 'comparison_protocol': (ROOT/'docs/research_next/NATIVE_REVERSE_COMPARE_PROTOCOL.md', '36535647b0e62db57f526f1c6d5ebcb2e04c2df5a22650a6046a2341344d95d4'),
 'old_output_manifest': (OLD/'output_manifest.json', '2713685311e705ea0c9b6080dee2594e9d077d37aea844efb0e093f722cf9a52'),
 'old_review': (ROOT/'results/research_next/orlib_preflight/INDEPENDENT_SOLVER_RESULT_REVIEW.json', 'a465a16acf67ca9a0925376f2a2b7d4338a24bac9bb276258d134f930d11f358'),
 'candidate': (CASE/'mip/candidate_vector.json', 'ce8812ec5e37eb9e3bc98f0b71e4ccd768653b97b4dfd12c3aa4c28993ed8152'),
 'raw_lp': (CASE/'lp/raw_solution.npz', '933ffdce78ba1408f9fcfc520313e499b4325f1dcfb151b1afe80fe8ef7e7ef9'),
 'signed_bound': (CASE/'lp/signed_dual_bound.json', 'f4a23b8e50969dd900e833d4bb44b3d39614f0fbd2601e3e7ffc29d2073665c0'),
 'identity_result': (IDENTITY/'run01/result.json', '630481bb4b8249539811a76cbf9197cd6ca577c3c131b21a234d6b6cb64b9c0f'),
 'identity_lower': (IDENTITY/'run01/native_lower_certificate.json', 'f8c53ff207063ef6ee7bc869a582934bb538148a38d0218b617ef1efca64babe'),
 'identity_point': (IDENTITY/'run01/native_point_check.json', '85e5cdeeeeb37ee9ff4ece9a12ad5ff3e22f6d21a7d1a96f3539d68ea50d75fb'),
 'identity_completion': (IDENTITY/'run01/completion.json', '8c4aab6fb4d5a5a50ea226138817c440879d3cdce7f5c7a743913ac107e650ac'),
 'identity_review': (ROOT/'results/research_next/native_expanded_identity_independent_review/postrun_review.json', '8f13f3a1751e03f2e4487127159420d14717bfff2b2c810a5c829f13bfa1b2e1')}


def require(ok, why):
    if not ok:
        raise ValueError(why)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))


def utc():
    return datetime.now(timezone.utc).isoformat()


def save(p, value):
    with Path(p).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def q(value):
    require(type(value) in (int, float) and math.isfinite(value), 'Finite binary64 input')
    return F(value)


def rat(value):
    return {'numerator': str(value.numerator), 'denominator': str(value.denominator), 'approximate': float(value)}


def unrat(value):
    exact = F(int(value['numerator']), int(value['denominator']))
    require(value == rat(exact), 'Canonical archived rational')
    return exact


def binding(p):
    p = Path(p).resolve()
    data = p.read_bytes()
    return {'path': str(p), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def validate(items):
    for item in items:
        require(binding(item['path']) == item, 'Changed input ' + item['path'])


def guard(start):
    require(time.perf_counter() - start <= LIMIT, '120-second soft arithmetic phase exceeded')


def load_module(name, path, expected):
    require(sha(path) == expected, 'Pinned helper import')
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def fixed_roles(model, identity):
    require(model['variant'] == 'native_penalized' and model['horizon'] == 24 and model['order'] == ORDER,
            'Only unchanged reverse/native target')
    require(identity['case'] == 'identity__native_penalized', 'Only closed native identity reference')
    require(identity['status'] == 'CERTIFIED_FINITE_NATIVE_EXPANDED_IDENTITY_BRACKET', 'Closed finite identity')


def prepare():
    require(not PRE.exists() and not RUN.exists(), 'Fresh preparation only')
    for path, digest in PINS.values():
        require(sha(path) == digest, 'Pinned provenance ' + str(path))
    cm = read(PINS['comparison_manifest'][0])
    inherited = cm['inputs'] + list(cm['copies'].values())
    validate(inherited)
    review, comparison = read(PINS['comparison_review'][0]), read(PINS['comparison'][0])
    require(review['status'] == 'PASS_INDEPENDENT_EXACT_NOMINAL_PROJECTION_EQUIVALENCE' and
            review['case'] == 'reverse_4_19__native_penalized' and review['order_destination_to_source'] == ORDER,
            'Closed actual target independent acceptance')
    require(review['manifest_sha256'] == PINS['comparison_manifest'][1], 'Comparison manifest review binding')
    for name, digest in review['producer_snapshot'].items():
        require(sha(COMPARE/'run01'/name) == digest, 'Every reviewed target comparison output')
    require(comparison['nominal_projection_equivalence'] is True and comparison['objective_constant'] == ['0', '1'] and
            comparison['expanded_native_equivalence'] == 'NOT_ESTABLISHED' and comparison['no_cost_transfer_at_this_stage'],
            'Nominal-only target comparison and zero objective constant')
    fixed = {name: path for name, (path, _) in PINS.items()}
    for name in ('raw', 'parsed', 'normal', 'model'):
        fixed[name] = COMPARE/'prepared'/f'{name}.json'
    fixed.update(mip_result=CASE/'mip/result.json', mip_checks=CASE/'mip/exact_candidate_checks.json', lp_result=CASE/'lp/result.json',
                 comparison_completion=COMPARE/'run01/completion.json', comparison_bridge=COMPARE/'run01/expected_parsed_bridge.json',
                 comparison_reviewer=COMPARE/'INDEPENDENT_POSTRUN_REVIEW.py', comparison_memo=COMPARE/'INDEPENDENT_POSTRUN_REVIEW.md',
                 identity_review_source=ROOT/'results/research_next/native_expanded_identity_independent_review/postrun_review.py',
                 identity_review_memo=ROOT/'results/research_next/native_expanded_identity_independent_review/POSTRUN_REVIEW.md')
    require(sha(fixed['comparison_reviewer']) == review['reviewer_source_sha256'], 'Target reviewer source binding')
    ir = read(fixed['identity_review'])
    require(ir['status'] == 'PASS_INDEPENDENT_NATIVE_EXPANDED_POINT_AND_LOWER_REPLAY', 'Closed independent identity')
    require(sha(fixed['identity_review_source']) == ir['reviewer_sha256'], 'Identity reviewer source binding')
    for role in ('identity_result', 'identity_lower', 'identity_point', 'identity_completion'):
        require(sha(fixed[role]) == ir['producer_outputs_unchanged'][fixed[role].name], 'Identity reviewed payload binding')
    fixed_roles(read(fixed['model']), read(fixed['identity_result']))
    require(fixed['model'].read_bytes() == (OLD/'inputs/reverse_4_19__native_penalized.json').read_bytes(), 'Original target model byte bridge')
    lookup = {entry['path']: entry for entry in read(fixed['old_output_manifest'])['files']}
    for role in ('candidate', 'raw_lp', 'signed_bound', 'mip_result', 'mip_checks', 'lp_result'):
        path = fixed[role]
        item = lookup[path.relative_to(OLD).as_posix()]
        require(path.stat().st_size == item['bytes'] and sha(path) == item['sha256'], 'Old output manifest role ' + role)
    # Capture and hash binding only: no point, residual, cost or difference arithmetic.
    originals = {entry['path']: entry for entry in inherited}
    for path in list(fixed.values()) + [Path(__file__), PROTOCOL, ARM/'synthetic_controls.json']:
        item = binding(path)
        require(item['path'] not in originals or originals[item['path']] == item, 'Consistent inherited binding')
        originals[item['path']] = item
    items = list(originals.values())
    validate(items)
    captured = {name: path.read_bytes() for name, path in fixed.items()}
    for name, data in captured.items():
        item = originals[str(fixed[name].resolve())]
        require(len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256'], 'Exact capture')
    PRE.mkdir(parents=True)
    copies = {}
    for name, data in captured.items():
        output = PRE/(name + fixed[name].suffix)
        with output.open('xb') as stream:
            stream.write(data)
        require(output.read_bytes() == data, 'Copied readback')
        copies[name] = binding(output)
    validate(items)
    validate(list(copies.values()))
    save(PRE/'manifest.json', dict(utc=utc(), inputs=items, copies=copies, source_sha256=sha(__file__), protocol_sha256=sha(PROTOCOL),
         case='reverse_4_19__native_penalized', point_replays=0, bound_arithmetic_runs=0, difference_arithmetic_runs=0, optimizer_calls=0))
    save(PRE/'prepared_freeze.json', dict(utc=utc(), manifest_sha256=sha(PRE/'manifest.json'), source_sha256=sha(__file__),
         protocol_sha256=sha(PROTOCOL), input_count=len(items), copy_count=len(copies), target_count=1, scientific_arithmetic_runs=0, optimizer_calls=0))
    print(json.dumps({'status': 'PREPARED_ONLY', 'freeze_sha256': sha(PRE/'prepared_freeze.json'), 'manifest_sha256': sha(PRE/'manifest.json')}))


def derive_bound(model, raw, tau, qr):
    """Same exact signed-row/finite-box algebra as the reviewed identity source."""
    require(len(raw) == len(model['rows']), 'Row multiplier length')
    dual, changed = [], []
    residual = [q(column['objective']) for column in model['columns']]
    beta = F(0)
    for i, (value, row) in enumerate(zip(raw, model['rows'])):
        d = q(value)
        if (d > 0 and row['lower'] is None) or (d < 0 and row['upper'] is None):
            d = F(0)
            changed.append(i)
        dual.append(d)
        if d:
            beta += d*q(row['lower'] if d > 0 else row['upper'])
            for j, a in row['coefficients']:
                residual[j] -= d*q(a)
    nominal = beta + sum((r*q(c['lower'] if r >= 0 else c['upper']) for r, c in zip(residual, model['columns'])), F(0))
    slope = sum(map(abs, dual), F(0)) + sum(map(abs, residual), F(0))
    expanded = nominal - tau*slope
    correction = tau*sum((min(residual[j], F(0)) for j in qr), F(0))
    direct = F(0)
    for d, row in zip(dual, model['rows']):
        if d:
            direct += d*(q(row['lower'])-tau if d > 0 else q(row['upper'])+tau)
    for j, (r, column) in enumerate(zip(residual, model['columns'])):
        direct += r*(q(column['lower'])-tau if r >= 0 else q(column['upper'])+tau+(tau if j in qr else 0))
    require(direct == expanded+correction and correction <= 0, 'Exact direct box/correction identity')
    return dict(dual=dual, changed=changed, residual=residual, beta=beta, nominal=nominal, slope=slope,
                expanded=expanded, correction=correction, native_lower=direct)


def containment_premises(raw, model, alias, helper, start):
    """Recheck the actual target domains/headroom used by the reviewed theorem."""
    columns = {column['name']: column for column in model['columns']}
    require(len(columns) == 2472, 'Unique retained columns')
    domains = {name: [None, None] for name in alias.values()}
    binaries, rows = set(), Counter()
    omitted = {name for name in domains if name.startswith('mfg:')}
    require(len(omitted) == 240 and set(columns) | omitted == set(domains), 'Projection roster')
    for k, row in enumerate(raw['constraints']):
        if k % 256 == 0:
            guard(start)
        function, endpoint = row['function'], row['set']
        if function['type'] == 'MathOptInterface.VariableIndex':
            name = alias[function['variable']]
            if endpoint['type'] == 'MathOptInterface.ZeroOne':
                require(name not in binaries, 'Unique binary domain')
                binaries.add(name)
                lo, hi = F(0), F(1)
            else:
                lo, hi = helper.endpoints(endpoint)
            oldlo, oldhi = domains[name]
            domains[name] = [lo if oldlo is None else oldlo if lo is None else max(lo, oldlo),
                             hi if oldhi is None else oldhi if hi is None else min(hi, oldhi)]
        else:
            coefficients, constant = helper.terms(function, alias)
            require(not set(coefficients) & omitted, 'Disconnected mfg affine support')
            lo, hi = helper.endpoints(endpoint)
            rows[helper.rowkey(coefficients, None if lo is None else lo-constant, None if hi is None else hi-constant)] += 1
    require(all(domains[name] == [F(0), None] for name in omitted), 'Zero lift domains')
    require(len(binaries) == 960 and binaries == {name for name, c in columns.items() if c['binary']}, 'Original full binary roster')
    objective, constant = helper.terms(raw['objective'], alias)
    require(constant == 0 and not set(objective) & omitted and raw['objective_sense'] == 'MIN_SENSE', 'Full native objective zero lift')
    require(all(objective.get(name, F(0)) == q(c['objective']) for name, c in columns.items()), 'Exact retained objective')
    qr, pairs, injections = set(), set(), set()
    for j, column in enumerate(model['columns']):
        name = column['name']
        wanted = [q(column['lower']), q(column['upper'])]
        actual = domains[name]
        parts = name.split(':')
        if parts[0] in ('Q', 'R'):
            _, unit, hour = parts
            qn, rn, un = f'Q:{unit}:{hour}', f'R:{unit}:{hour}', f'U:{unit}:{hour}'
            width = wanted[1]
            require(actual == [F(0), None] and wanted[0] == 0 and width >= 0, 'Target Q/R domain extension')
            require(q(columns[qn]['upper']) == q(columns[rn]['upper']) == width, 'Same encoded headroom width')
            require(domains[qn][0] == domains[rn][0] == 0 and domains[un] == [F(0), F(1)] and un in binaries, 'Target binary headroom premises')
            require(rows[helper.rowkey({qn: F(1), rn: F(1), un: -width}, None, F(0))] > 0, 'Actual native headroom row')
            qr.add(j)
            pairs.add((unit, hour))
        elif parts[0] == 'N':
            require(actual == [None, None] and wanted == [F(0), F(0)] and rows[helper.rowkey({name: F(1)}, F(0), F(0))] > 0, 'Native zero injection equality')
            injections.add(name)
        else:
            require(actual == wanted, 'No other domain extension: ' + name)
    require(len(qr) == 480 and len(pairs) == 240 and len(injections) == 24, 'Complete target containment scope')
    return qr, dict(headroom_pairs=240, QR_coordinates=480, zero_injection_equalities=24, full_binaries=960,
                    disconnected_mfg=240, actual_target_premises_checked=True, expanded_equivalence_claim=False)


def domain_check(value, lower, upper, tau, binary=False):
    if binary:
        return value in (0, 1), F(0)
    violation = max(F(0), lower-value if lower is not None else F(0), value-upper if upper is not None else F(0))
    return violation <= tau, violation


def native_point(raw, model, candidate, alias, helper, tau, start):
    require(len(candidate) == len(model['columns']) == 2472, 'Unchanged candidate shape')
    retained = {column['name']: q(v) for column, v in zip(model['columns'], candidate)}
    reverse_alias = {name: index for index, name in alias.items()}
    values = {index: F(0) if name.startswith('mfg:') else retained[name] for index, name in alias.items()}
    failures, binaries = [], []
    worst, affine_count, variable_count = F(0), 0, 0
    for k, row in enumerate(raw['constraints']):
        if k % 256 == 0:
            guard(start)
        function, endpoint = row['function'], row['set']
        binary = False
        if function['type'] == 'MathOptInterface.VariableIndex':
            variable_count += 1
            value = values[function['variable']]
            binary = endpoint['type'] == 'MathOptInterface.ZeroOne'
            if binary:
                binaries.append(function['variable'])
                lower, upper = None, None
            else:
                lower, upper = helper.endpoints(endpoint)
        else:
            affine_count += 1
            coefficients, constant = helper.terms(function, alias)
            value = constant+sum((a*values[reverse_alias[name]] for name, a in coefficients.items()), F(0))
            lower, upper = helper.endpoints(endpoint)
        accepted, violation = domain_check(value, lower, upper, tau, binary)
        worst = max(worst, violation)
        if not accepted:
            failures.append(dict(constraint=k, kind='nonbinary' if binary else 'endpoint', value=rat(value), nominal_violation=rat(violation)))
    require(len(binaries) == len(set(binaries)) == 960 and set(binaries) == set(raw['binary_variable_indices']), 'All original raw binaries')
    require(affine_count == 4384 and variable_count == 3696 and len(values) == 2712, 'Full raw native point census')
    objective, constant = helper.terms(raw['objective'], alias)
    require(constant == 0 and raw['objective_sense'] == 'MIN_SENSE', 'Native objective constant/sense')
    cost = constant+sum((a*values[reverse_alias[name]] for name, a in objective.items()), F(0))
    return values, dict(accepted=not failures, strict_nominal=not failures and worst == 0, tau=rat(tau), nominal_max_violation=rat(worst),
        native_variables=len(values), affine_rows=affine_count, variable_constraint_records=variable_count, binary_declarations=960,
        objective=rat(cost), failures=failures, omitted_mfg_lift=0, candidate_changed=False)


def outward_decimal(value, places, upper=False):
    scale = 10**places
    scaled = value*scale
    integer = -((-scaled.numerator)//scaled.denominator) if upper else scaled.numerator//scaled.denominator
    sign = '-' if integer < 0 else ''
    integer = abs(integer)
    return f'{sign}{integer//scale}.{integer%scale:0{places}d}'


def signed_difference(lower, upper, identity_lower, identity_upper):
    require(identity_lower <= identity_upper, 'Consistent closed identity')
    if upper is None:
        return dict(status='NO_FINITE_DIFFERENCE_WITHOUT_TARGET_UPPER', interval=None,
                    conditional_lower_if_target_nonempty=rat(lower-identity_upper))
    require(lower <= upper, 'Consistent finite target bracket')
    lo, hi = lower-identity_upper, upper-identity_lower
    require(lo <= hi, 'Ordered difference endpoints')
    displayed = [outward_decimal(lo, 6), outward_decimal(hi, 6, True)]
    require(F(displayed[0]) <= lo and F(displayed[1]) >= hi, 'Outward display')
    return dict(status='FINITE_SIGNED_OPTIMAL_COST_DIFFERENCE_BRACKET', interval=[rat(lo), rat(hi)],
                outward_6dp=displayed, strictly_positive_lower=lo > 0, includes_zero=lo <= 0 <= hi,
                meaning='reverse native-expanded optimum minus identity native-expanded optimum', regret_claim=False)


def run(expected):
    start = time.perf_counter()
    require(not RUN.exists() and sha(PRE/'prepared_freeze.json') == expected, 'One externally frozen run')
    freeze = read(PRE/'prepared_freeze.json')
    require(sha(PRE/'manifest.json') == freeze['manifest_sha256'], 'Manifest freeze')
    manifest = read(PRE/'manifest.json')
    validate(manifest['inputs'])
    validate(list(manifest['copies'].values()))
    require(sha(__file__) == manifest['source_sha256'] and sha(PROTOCOL) == manifest['protocol_sha256'], 'Frozen source/protocol')
    transports = {p.name: sha(p) for p in (PRE/'manifest.json', PRE/'prepared_freeze.json')}
    cp = lambda name: Path(manifest['copies'][name]['path'])
    RUN.mkdir()
    save(RUN/'started.json', dict(utc=utc(), freeze_sha256=expected, manifest_sha256=freeze['manifest_sha256'], optimizer_calls=0))
    try:
        helper = load_module('native_reverse_exact_decoder', cp('helper'), PINS['helper'][1])
        kernel = load_module('native_reverse_npz_reader', cp('kernel'), PINS['kernel'][1])
        raw, normal, model = read(cp('raw')), read(cp('normal')), read(cp('model'))
        identity = read(cp('identity_result'))
        fixed_roles(model, identity)
        require(raw['schema'] == 'official-orlib-MOI-raw-binary64-v1' and raw['optimizer_state'] == 'NO_OPTIMIZER', 'Actual raw source contract')
        require(len(model['rows']) == 4384 and len(model['columns']) == 2472 and sum(c['binary'] for c in model['columns']) == 960, 'Fixed original model scope')
        alias = helper.aliases_from_expected(raw, normal)
        qr, premises = containment_premises(raw, model, alias, helper, start)
        save(RUN/'containment_premises.json', premises)
        values, point = native_point(raw, model, read(cp('candidate')), alias, helper, TAU, start)
        require(unrat(point['objective']) == unrat(read(cp('mip_result'))['accepted_expanded_upper']), 'Unchanged target objective')
        save(RUN/'native_point_check.json', point)
        save(RUN/'lifted_rational_point.json', [{'native_index': i, 'name': alias[i], 'value': rat(values[i])} for i in sorted(values)])
        guard(start)
        arrays = kernel.read_npz(cp('raw_lp'), ('col_value', 'row_value', 'row_dual', 'col_dual'))
        raw_dual = kernel.vector(arrays['row_dual'], ('<f8',), 4384, 'row dual')
        bound = derive_bound(model, raw_dual, TAU, qr)
        old = read(cp('signed_bound'))
        require([q(v) for v in old['projected_dual']] == bound['dual'] and old['projection_changed_rows'] == bound['changed'], 'Original fixed sign projection')
        require([unrat(v) for v in old['exact_stationarity_residual']] == bound['residual'], 'Every target residual')
        for oldkey, newkey in [('beta', 'beta'), ('nominal_lower_bound', 'nominal'), ('expansion_slope', 'slope'), ('expanded_lower_bound', 'expanded')]:
            require(unrat(old[oldkey]) == bound[newkey], 'Replayed target proof ' + oldkey)
        require(unrat(old['tau']) == TAU and old['dual_feasibility_required'] is False and old['exact_optimum_claim'] is False, 'Archived proof convention')
        require(unrat(read(cp('lp_result'))['selected_expanded_lower']) == bound['expanded'], 'Only selected target signed proof')
        save(RUN/'native_lower_certificate.json', dict(tau=rat(TAU), old_expanded_lower=rat(bound['expanded']),
             additional_QR_upper_support_correction=rat(bound['correction']), native_expanded_lower=rat(bound['native_lower']),
             row_endpoint_sum_nominal=rat(bound['beta']), nominal_lower=rat(bound['nominal']), expansion_slope=rat(bound['slope']),
             projected_multipliers=[rat(v) for v in bound['dual']], changed_rows=bound['changed'], residual=[rat(v) for v in bound['residual']],
             QR_indices=sorted(qr), direct_widened_endpoint_sum_agrees=True, no_new_ray_or_dual=True, optimizer_calls=0))
        ir = read(cp('identity_review'))
        require(unrat(identity['tau']) == TAU, 'Identical mathematical expansion')
        for field in ('native_expanded_lower', 'native_expanded_upper', 'strict_nominal_upper'):
            require(identity[field] == ir[field], 'Closed identity result/review equality ' + field)
        identity_lower, identity_upper = unrat(identity['native_expanded_lower']), unrat(identity['native_expanded_upper'])
        require(unrat(read(cp('identity_lower'))['native_expanded_lower']) == identity_lower and
                unrat(read(cp('identity_point'))['objective']) == identity_upper and read(cp('identity_point'))['accepted'], 'Identity proof endpoints unchanged')
        upper = unrat(point['objective']) if point['accepted'] else None
        difference = signed_difference(bound['native_lower'], upper, identity_lower, identity_upper)
        difference.update(identity_result_sha256=sha(cp('identity_result')), identity_review_sha256=sha(cp('identity_review')), identity_arithmetic_replayed=False,
                          target_native_lower=rat(bound['native_lower']), target_native_upper=rat(upper) if upper is not None else None,
                          identity_native_lower=rat(identity_lower), identity_native_upper=rat(identity_upper))
        save(RUN/'signed_difference.json', difference)
        result = dict(status='CERTIFIED_FINITE_NATIVE_EXPANDED_REVERSE_BRACKET' if upper is not None else 'LOWER_ONLY_NO_ACCEPTED_NATIVE_UPPER',
            case='reverse_4_19__native_penalized', native_expanded_lower=rat(bound['native_lower']), native_expanded_upper=rat(upper) if upper is not None else None,
            strict_nominal_upper=rat(upper) if upper is not None and point['strict_nominal'] else None, tau=rat(TAU),
            signed_difference=difference, nominal_comparison_inherited=True, expanded_model_equivalence_claim=False, containment_only=True,
            exact_optimality_claim=False, regret_claim=False, cost_units='encoded UC objective', posthoc_fidelity_extension=True,
            original_target_service_comparisons=4, target_fidelity_extensions_in_this_arm=1, untransferred_comparisons=['rotate_left1_4_19__native_penalized', 'reverse_4_19__hard_service', 'rotate_left1_4_19__hard_service'],
            new_candidates=0, new_optimizers=0, Julia_calls=0, native_builds=0)
        save(RUN/'result.json', result)
        validate(manifest['inputs'])
        validate(list(manifest['copies'].values()))
        require(transports == {name: sha(PRE/name) for name in transports}, 'Prepared transports unchanged')
        guard(start)
        save(RUN/'completion.json', dict(status='COMPLETE_PENDING_INDEPENDENT_REVIEW', utc=utc(), elapsed_seconds=time.perf_counter()-start,
             final_completion_write_excluded=True, all_inputs_unchanged=True, arithmetic_runs=1, optimizer_calls=0, native_builds=0, Julia_calls=0))
        print(json.dumps({'status': result['status'], 'elapsed_seconds': time.perf_counter()-start}))
    except BaseException as exc:
        save(RUN/'failure.json', dict(status='ERROR_OR_TIMEOUT_NO_ADMITTED_BRACKET', utc=utc(), exception_type=type(exc).__name__, message=str(exc),
             elapsed_seconds=time.perf_counter()-start, optimizer_calls=0, no_retry=True))
        raise


def self_test():
    require(not (ARM/'synthetic_controls.json').exists(), 'One invented fixture pass')
    t, width = F(1,8), F(3)
    require(width+2*t-t-width == t and width+2*t > width+t, 'Second tau required')
    require(width*(1+t)+2*t > width+2*t, 'Exact binary premise')
    toy = {'columns': [{'lower': 0., 'upper': 3., 'objective': -2.}, {'lower': 0., 'upper': 3., 'objective': 1.}],
           'rows': [{'lower': None, 'upper': 3., 'coefficients': [[0,1.], [1,1.]]}]}
    bad = derive_bound(toy, [1.], t, {0,1})
    require(bad['changed'] == [0] and bad['correction'] == -2*t, 'Inadmissible row side')
    valid = derive_bound(toy, [-1.], t, {0,1})
    require(valid['residual'] == [F(-1), F(2)] and valid['correction'] == -t, 'Signed residual correction')
    require(domain_check(F(0), F(0), None, t)[0], 'Zero lift')
    require(not domain_check(F(1)+t/2, None, None, t, True)[0] and domain_check(F(1), None, None, t, True)[0], 'Binary never expanded')
    require(domain_check(-t, F(0), None, t)[0] and not domain_check(-2*t, F(0), None, t)[0], 'Expanded endpoint and rejection')
    null = signed_difference(F(-1), None, F(2), F(3))
    require(null['interval'] is None and unrat(null['conditional_lower_if_target_nonempty']) == -4, 'No upper null propagation')
    cross = signed_difference(F(2), F(4), F(3), F(5))
    require([unrat(v) for v in cross['interval']] == [F(-3), F(1)] and cross['includes_zero'], 'Signed interval subtraction')
    require(outward_decimal(F(-1,3), 6) == '-0.333334' and outward_decimal(F(-1,3), 6, True) == '-0.333333' and
            outward_decimal(F(1,3), 6) == '0.333333' and outward_decimal(F(1,3), 6, True) == '0.333334', 'Outward rounding both signs')
    fake_model = dict(variant='native_penalized', horizon=24, order=ORDER)
    fake_identity = dict(case='identity__native_penalized', status='CERTIFIED_FINITE_NATIVE_EXPANDED_IDENTITY_BRACKET')
    fixed_roles(fake_model, fake_identity)
    for changed_model, changed_identity in [(dict(fake_model, order=list(range(24))), fake_identity),
                                             (fake_model, dict(fake_identity, case='reverse_4_19__native_penalized'))]:
        try:
            fixed_roles(changed_model, changed_identity)
        except ValueError:
            pass
        else:
            raise ValueError('Wrong target/identity role accepted')
    require(F.from_float(1e-5) != F(1,100000), 'Binary64 tau')
    ARM.mkdir(parents=True, exist_ok=True)
    save(ARM/'synthetic_controls.json', dict(status='PASS', checks=12, utc=utc(), source_sha256=sha(__file__), protocol_sha256=sha(PROTOCOL),
         scientific_inputs_read=0, scientific_arithmetic_runs=0, optimizer_calls=0))
    print('PASS 12 invented groups')


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
        require(args.expected_freeze_sha256 is not None, 'Explicit freeze required')
        run(args.expected_freeze_sha256)
