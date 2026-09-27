"""Separate flow-conserving DC model: prepare, then three fixed LP proposals."""
from __future__ import annotations
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
from fractions import Fraction as Q
import gzip
import json
import math
from pathlib import Path
import shutil
import sys
import time

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import research8h_exact_fixed_schedule as arithmetic
import research8h_branch_flow_check as variant

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/research8h/branch_flow_encoding'
OLD = ROOT / 'results/research8h/hour_of_day'
PROTOCOL = ROOT / 'docs/research8h/BRANCH_FLOW_ENCODING_PROTOCOL.md'
DESIGN = ROOT / 'docs/research8h/BRANCH_FLOW_ENCODING_DESIGN.md'
CASES = ('january_identity', 'seed_26100200', 'seed_26093200', 'seed_26093201')
TARGETS = CASES[2:]
CALLS = (('identity_proposal', 60.), ('seed_26093200', 30.), ('seed_26093201', 30.))
CAP = Q(23195); TAU = Q.from_float(1e-5)
CUTOFF = datetime(2026, 9, 27, 4, tzinfo=timezone.utc)
PHASE = 1800.; ARITHMETIC_PHASE = 900.
TEST_REPORT = ROOT / 'results/research8h/branch_flow_implementation_tests.json'
OPTIONS = {k: val for k, val in arithmetic.OPTIONS.items() if k != 'time_limit'}
require = arithmetic.require
rat = arithmetic.rat
parse_rat = arithmetic.parse_rat
sha = arithmetic.sha
save = arithmetic.save
terms = arithmetic.row_terms
endpoint = arithmetic.endpoint
primal = variant.primal


def helper_gate():
    require(sha(Path(arithmetic.__file__)) == '733f57ae928c72dcf063c224e728d1ad1a01d52e93c068f63147d988c16e3a77', 'Reviewed arithmetic changed')
    require(sha(Path(primal.__file__)) == variant.OLD_CHECKER_SHA, 'Reviewed rational checker changed')
    return primal.kernel()


def read_labels(path):
    with gzip.open(path, 'rt', newline='') as f: return list(csv.DictReader(f))


def write_labels(path, rows):
    with gzip.open(path, 'xt', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['row', 'family', 'hour_0based', 'uid', 'old_row'])
        writer.writeheader(); writer.writerows(rows)


def load_native(v, path):
    data = v.read_npz(path, ('pmin', 'pmax', 'net', 'rows', 'source_hour', 'nodal'))
    require(data['pmin'].shape == data['pmax'].shape == (168, 41) and data['nodal'].shape == (168, 24), 'Native matrix shapes')
    require(data['net'].shape == data['rows'].shape == data['source_hour'].shape == (168,), 'Native vector shapes')
    require(sorted(data['source_hour'].values) == list(range(168)), 'Source hour is not permutation')
    return data


def full_objective(meta):
    names = meta['unit_names']; thermal = meta['thermal_unit_names']
    fossil = [names.index(name) for name in thermal if name != '121_NUCLEAR_1']
    require(len(fossil) == 23 and [names[j] for j in fossil] == meta['fossil_units'], 'Fossil roster')
    return tuple(float(j < 6888 and j % 41 in fossil) for j in range(29400))


def export_model(directory, rowlist, low, high, col_low, col_high, integer, cost, labels, meta):
    import numpy as np
    from scipy.sparse import coo_matrix, save_npz
    directory.mkdir(parents=True, exist_ok=False)
    rr = []; cc = []; vv = []
    for i, row in enumerate(rowlist):
        for j, a in sorted(row.items()):
            require(Q(float(a)) == a, 'Non-binary64 model coefficient')
            if a: rr.append(i); cc.append(j); vv.append(float(a))
    for x in (*col_low, *col_high): require(Q(float(x)) == x, 'Non-binary64 box endpoint')
    for x in (*low, *high):
        if x is not None: require(Q(float(x)) == x, 'Non-binary64 row endpoint')
    matrix = coo_matrix((vv, (rr, cc)), shape=(len(rowlist), len(col_low))).tocsr()
    save_npz(directory / 'matrix.npz', matrix)
    np.savez_compressed(directory / 'bounds.npz', column_lower=[float(x) for x in col_low], column_upper=[float(x) for x in col_high],
        row_lower=[-np.inf if x is None else float(x) for x in low], row_upper=[np.inf if x is None else float(x) for x in high])
    np.savez_compressed(directory / 'integrality.npz', integrality=np.asarray(integer, dtype=np.uint8))
    np.savez_compressed(directory / 'objective.npz', objective=np.asarray(cost, dtype=np.float64))
    meta = {**meta, 'rows':matrix.shape[0], 'columns':matrix.shape[1], 'nonzeros':matrix.nnz}
    write_labels(directory / 'row_metadata.csv.gz', labels); save(directory / 'model_metadata.json', meta)


def build_variant(v, case, common_graph=None, common_delta=None):
    source = OLD / case; old = v.load_model(source); labels = read_labels(source / 'row_metadata.csv.gz')
    meta = v.json_read(source / 'model_metadata.json'); native = load_native(v, source / 'native_inputs.npz')
    require((old.rows, old.cols) == (34681, 23016) and len(labels) == old.rows, 'Old capped case dimensions')
    integer = arithmetic.get_vector(v, source / 'integrality.npz', 'integrality', ('|u1',), old.cols)
    require(integer == tuple(int(6888 <= j < 18984) for j in range(old.cols)), 'Original full binary mask')
    old_cost = arithmetic.get_vector(v, source / 'objective.npz', 'objective', ('<f8',), old.cols)
    require(not any(old_cost), 'Old HOD objective is expected to be zero feasibility')
    require(meta['budget_MWh'] == 23195 and meta['individual_mean_constraints'] == 0, 'Old cap or means changed')
    spec = primal.native_spec(arithmetic.GEN, meta); cost = full_objective(meta)
    branch_by_hour = {t: [] for t in range(168)}; node_by_hour = {t: {} for t in range(168)}; aggregates = {}
    retained = []; low = []; high = []; newlabels = []; caps = []
    for i, label in enumerate(labels):
        require(int(label['row']) == i, 'Old row label index'); t = int(label['hour_0based'])
        family = label['family']
        if family == 'branch_flow': branch_by_hour[t].append(i)
        elif family == 'nodal_balance': node_by_hour[t][int(label['uid'])] = i
        elif family == 'aggregate_balance': aggregates[t] = i
        else:
            require(family in ('thermal_upper', 'thermal_lower', 'transition', 'exclusive_transition', 'minimum_up', 'minimum_down', 'fossil_energy_cap'), 'Unexpected retained family')
            newlabels.append(dict(row=len(retained), family=family, hour_0based=t, uid=label['uid'], old_row=i))
            retained.append(terms(old, i)); low.append(endpoint(old.row_lower[i])); high.append(endpoint(old.row_upper[i]))
            if family == 'fossil_energy_cap': caps.append(len(retained) - 1)
    require(len(caps) == 1 and len(retained) == 24097, 'Retained row/cap count')
    require(retained[caps[0]] == {j: Q(x) for j, x in enumerate(cost) if x}
            and low[caps[0]] is None and high[caps[0]] == CAP, 'Actual cap row differs')
    graphs = []; old_nodal = []; rhs_deltas = []
    busids = meta['bus_ids']; require(len(busids) == 24, 'Bus roster')
    for t in range(168):
        require(len(branch_by_hour[t]) == 38 and set(node_by_hour[t]) == set(busids) and t in aggregates, 'Hourly row count')
        graph = []
        for e, i in enumerate(branch_by_hour[t]):
            row = terms(old, i); require(len(row) == 2, 'Branch must have exactly two nonzero coefficients')
            positive = [(j, a) for j, a in row.items() if a > 0]; negative = [(j, a) for j, a in row.items() if a < 0]
            require(len(positive) == len(negative) == 1 and positive[0][1] == -negative[0][1], 'Branch coefficients not exact opposites')
            u = positive[0][0] - 18984 - 24 * t; w = negative[0][0] - 18984 - 24 * t
            require(0 <= u < 24 and 0 <= w < 24 and u != w, 'Nonlocal branch')
            require(math.isfinite(old.row_lower[i]) and 0 < old.row_upper[i] == -old.row_lower[i] < math.inf, 'Branch limits')
            graph.append(dict(branch=e, uid=labels[i]['uid'], positive_bus=u, negative_bus=w,
                coefficient=rat(positive[0][1]), lower=rat(Q(old.row_lower[i])), upper=rat(Q(old.row_upper[i]))))
        if common_graph is None: common_graph = graph
        require(graph == common_graph, 'Branch coefficient/limit/topology block changes')
        graphs.append(graph)
        coefficients = [[Q(0)] * 24 for _ in range(24)]
        aggregate = aggregates[t]
        require(terms(old, aggregate) == {t * 41 + j: Q(1) for j in range(41)} and
            old.row_lower[aggregate] == old.row_upper[aggregate] == native['net'].values[t], 'Old aggregate provenance')
        rhs_deltas.append(rat(sum((Q(x) for x in native['nodal'].values[t * 24:(t + 1) * 24]), Q(0)) - Q(native['net'].values[t])))
        for bus, busid in enumerate(busids):
            i = node_by_hour[t][busid]; row = terms(old, i)
            expected_p = {t * 41 + j: Q(1) for j, s in enumerate(spec) if s['bus'] == busid}
            require({j: a for j, a in row.items() if j < 6888} == expected_p, 'Generator incidence changed')
            require(all(j in expected_p or 18984 + 24 * t <= j < 18984 + 24 * (t + 1) for j in row), 'Unexpected nodal coordinate')
            require(old.row_lower[i] == old.row_upper[i] == native['nodal'].values[t * 24 + bus], 'Native nodal RHS')
            for j, a in row.items():
                if j >= 18984: coefficients[bus][j - 18984 - t * 24] = a
        old_nodal.append(coefficients)
    new_angles = [[Q(0)] * 24 for _ in range(24)]
    for edge in common_graph:
        u, w, b = edge['positive_bus'], edge['negative_bus'], parse_rat(edge['coefficient'])
        new_angles[u][u] -= b; new_angles[u][w] += b; new_angles[w][u] += b; new_angles[w][w] -= b
    for old_angles in old_nodal:
        delta = [[new_angles[i][j] - old_angles[i][j] for j in range(24)] for i in range(24)]
        if common_delta is None: common_delta = delta
        require(delta == common_delta, 'Changed hour-normalized nodal difference')
    for t in range(168):
        for bus, busid in enumerate(busids):
            old_i = node_by_hour[t][busid]
            row = {t * 41 + j: Q(1) for j, s in enumerate(spec) if s['bus'] == busid}
            for edge in common_graph:
                if bus == edge['positive_bus']: row[23016 + t * 38 + edge['branch']] = Q(-1)
                if bus == edge['negative_bus']: row[23016 + t * 38 + edge['branch']] = Q(1)
            newlabels.append(dict(row=len(retained), family='nodal_flow_incidence', hour_0based=t, uid=busid, old_row=old_i))
            retained.append(row); load = Q(native['nodal'].values[t * 24 + bus]); low.append(load); high.append(load)
        for edge in common_graph:
            e, u, w = edge['branch'], edge['positive_bus'], edge['negative_bus']; b = parse_rat(edge['coefficient'])
            row = {23016 + 38 * t + e: Q(1), 18984 + 24 * t + u: -b, 18984 + 24 * t + w: b}
            newlabels.append(dict(row=len(retained), family='flow_definition', hour_0based=t, uid=edge['uid'], old_row=branch_by_hour[t][e]))
            retained.append(row); low.append(Q(0)); high.append(Q(0))
    col_low = [Q(x) for x in old.lower] + [parse_rat(e['lower']) for _ in range(168) for e in common_graph]
    col_high = [Q(x) for x in old.upper] + [parse_rat(e['upper']) for _ in range(168) for e in common_graph]
    integer = integer + (0,) * (168 * 38)
    require(len(retained) == 34513 and len(col_low) == 29400, 'Variant dimensions')
    meta = {**meta, 'rows':34513, 'columns':29400, 'offsets':{**meta['offsets'], 'flow':23016},
        'column_order':'P, U, Y, Z, theta, flow; hour-major within each block',
        'model_variant':'flow-conserving DC, distinct from old independently rounded angle model',
        'objective':'sum of 23 fossil-unit hourly dispatch values', 'omitted_aggregate_rows':168,
        'aggregate_authority':'exact sum of native nodal loads', 'cap_row':caps[0]}
    directory = OUT / case
    export_model(directory, retained, low, high, col_low, col_high, integer, cost, newlabels, meta)
    shutil.copyfile(source / 'native_inputs.npz', directory / 'native_inputs.npz')
    shutil.copyfile(source / 'permutation.csv', directory / 'permutation.csv')
    save(directory / 'graph.json', common_graph); save(directory / 'native_spec.json', spec)
    save(directory / 'representation_differences.json', dict(nodal_delta=[dict(bus=i, theta=j, value=rat(a))
        for i, row in enumerate(common_delta) for j, a in enumerate(row) if a],
        native_nodal_sum_minus_old_net=rhs_deltas, changed_nodal_coefficients=sum(bool(x) for row in common_delta for x in row),
        old_model_bindings=primal.model_bindings(source), old_objective_was_zero=True, strictly_equivalent_claim=False,
        feasible_set_nesting_claim=False, common_nodal_difference_verified_all168hours=True))
    return common_graph, common_delta, native


def make_proposal(v):
    m = v.load_model(OUT / CASES[0]); labels = read_labels(OUT / CASES[0] / 'row_metadata.csv.gz')
    fixed = {r['column']: parse_rat(r['value']) for r in v.json_read(arithmetic.OUT / 'fixed_schedule.json')}
    require(set(fixed) == set(range(6888, 18984)), 'Fixed schedule original mask')
    old_vector = arithmetic.get_vector(v, OLD / CASES[0] / 'constructive_vector.npz', 'vector', ('<f8',), 23016)
    require(all(Q(old_vector[j]) == x for j, x in fixed.items()), 'Original canonical identity schedule changed')
    blocks = []; mapping = {}
    objective = full_objective(v.json_read(OUT / CASES[0] / 'model_metadata.json'))
    for t in range(168):
        columns = list(range(t * 41, (t + 1) * 41)) + list(range(18984 + t * 24, 18984 + (t + 1) * 24)) + list(range(23016 + t * 38, 23016 + (t + 1) * 38))
        for j, original in enumerate(columns): mapping[original] = (t, j)
        blocks.append(dict(hour=t, columns=columns, lower=[Q(m.lower[j]) for j in columns], upper=[Q(m.upper[j]) for j in columns],
                           objective=[Q(objective[j]) for j in columns], rows=[]))
    constants = []; cap_rows = []
    for i, label in enumerate(labels):
        if label['family'] == 'fossil_energy_cap': cap_rows.append(i); continue
        row = terms(m, i); shift = sum((a * fixed[j] for j, a in row.items() if j in fixed), Q(0))
        free = {j: a for j, a in row.items() if j not in fixed}; lo, hi = endpoint(m.row_lower[i]), endpoint(m.row_upper[i])
        if not free:
            require((lo is None or shift >= lo) and (hi is None or shift <= hi), 'Fixed constant row fails')
            constants.append(dict(row=i, activity=rat(shift), lower=arithmetic.encode_bound(lo), upper=arithmetic.encode_bound(hi))); continue
        hours = {mapping[j][0] for j in free}; require(len(hours) == 1, 'Proposal continuous temporal coupling')
        t = next(iter(hours)); require(int(label['hour_0based']) == t, 'Actual proposal hour differs')
        blocks[t]['rows'].append(dict(original_row=i, family=label['family'], uid=label['uid'], fixed_shift=shift,
            terms={mapping[j][1]: a for j, a in free.items()}, lower=None if lo is None else lo - shift, upper=None if hi is None else hi - shift))
    require(len(constants) == 16032 and len(cap_rows) == 1, 'Proposal constant/cap denominator')
    for b in blocks:
        require(Counter(r['family'] for r in b['rows']) == Counter(thermal_upper=24, thermal_lower=24, nodal_flow_incidence=24, flow_definition=38), 'Proposal row count')
    rr = []; low = []; high = []; lab = []
    for b in blocks:
        for r in b['rows']:
            rr.append({b['hour'] * 103 + j: a for j, a in r['terms'].items()}); low.append(r['lower']); high.append(r['upper'])
            lab.append(dict(row=len(lab), family=r['family'], hour_0based=b['hour'], uid=r['uid'], old_row=r['original_row']))
    export_model(OUT / 'identity_proposal', rr, low, high, [x for b in blocks for x in b['lower']], [x for b in blocks for x in b['upper']],
                 [0] * (168 * 103), [float(x) for b in blocks for x in b['objective']], lab,
                 dict(rows=18480, columns=17304, deleted_full_cap_rows=cap_rows, fixed_state_columns=12096,
                      column_order='hour-major blocks of P41, theta24, flow38', objective='23-fossil sum'))
    with gzip.open(OUT / 'exact_blocks.json.gz', 'xt', encoding='utf-8') as f: json.dump(arithmetic.encoded_blocks(blocks), f, separators=(',', ':'))
    save(OUT / 'constant_rows.json', constants)
    shutil.copyfile(arithmetic.OUT / 'fixed_schedule.json', OUT / 'fixed_schedule.json')
    return blocks, fixed


def prepare():
    require(not OUT.exists(), 'Variant output already exists'); v = helper_gate(); started = time.perf_counter()
    require(sha(OLD / 'input_manifest.csv') == '078082667f83322d3540ad3ac215ebcc996d0d31b04fd52bfa75c1d2fd814fcc', 'Old HOD manifest changed')
    with (OLD / 'input_manifest.csv').open(encoding='utf-8-sig', newline='') as f: old_bindings = list(csv.DictReader(f))
    files = []
    for case in CASES:
        for name in ('matrix.npz','bounds.npz','integrality.npz','objective.npz','native_inputs.npz','model_metadata.json','row_metadata.csv.gz','permutation.csv','constructive_vector.npz'):
            p = OLD / case / name; matches = [r for r in old_bindings if r['path'].replace('\\','/').endswith('/hour_of_day/' + case + '/' + name)]
            require(len(matches) == 1 and sha(p) == matches[0]['sha256'] and p.stat().st_size == int(matches[0]['bytes']), 'Old case binding: ' + str(p)); files.append(p)
    require(sha(arithmetic.GEN) == '988466f29132b73739de60c9204dd4a2a9ceb0adf572e5966c086611272f4068', 'Native generator provenance')
    require(sha(arithmetic.OUT/'input_manifest.json') == '397fdbdd982ec11dc7265d842733df40fc0ad66a22922ea40e06cfebdaf03da9', 'Original attempt schedule provenance changed')
    previous=v.json_read(arithmetic.OUT/'input_manifest.json')
    schedule_records=[r for r in previous if Path(r['path']) == arithmetic.OUT/'fixed_schedule.json']
    require(len(schedule_records)==1,'Original fixed schedule missing from prior manifest')
    arithmetic.verify_bindings(schedule_records)
    OUT.mkdir(parents=True, exist_ok=False); graph = delta = None; all_native = {}
    for case in CASES: graph, delta, all_native[case] = build_variant(v, case, graph, delta)
    identity = all_native[CASES[0]]
    require(identity['source_hour'].values == tuple(range(168)), 'Identity source-hour map')
    for case in CASES:
        native = all_native[case]; order = native['source_hour'].values
        with (OLD/case/'permutation.csv').open(encoding='utf-8-sig',newline='') as f: table=list(csv.DictReader(f))
        require(tuple(int(r['new_hour_0based']) for r in table)==tuple(range(168)) and
                tuple(int(r['source_hour_0based']) for r in table)==order, 'CSV/native permutation mismatch')
        for key in ('pmin','pmax','net','nodal','rows'):
            width = math.prod(identity[key].shape[1:]) if len(identity[key].shape) > 1 else 1
            expected = tuple(x for t in order for x in identity[key].values[t * width:(t + 1) * width])
            require(native[key].values == expected, 'Joint native package differs: ' + case + '/' + key)
    blocks, fixed = make_proposal(v)
    control_order = all_native[CASES[1]]['source_hour'].values
    require(all(fixed[6888 + t * 24 + k] == fixed[6888 + control_order[t] * 24 + k] for t in range(168) for k in range(24)), 'Control does not preserve U sequence')
    save(OUT / 'preparation_report.json', dict(elapsed_s=time.perf_counter()-started, cases=CASES, ordinary_denominator=2,
        full_model_rows=34513, full_model_columns=29400, original_binary_columns=12096,
        identity_hour_blocks=168, identity_continuous_columns_per_hour=103, identity_continuous_rows_per_hour=110,
        constant_rows=16032, identity_cap_deleted_for_proposal_only=True, strict_capped_acceptance_required=True,
        all_joint_packages_and_control_U_preserved=True, optimizer_calls=0, actual_basis_reconstructions=0,
        control_changed_hours=sum(t != source for t, source in enumerate(control_order))))
    files += [Path(__file__), Path(variant.__file__), Path(arithmetic.__file__), Path(primal.__file__), primal.KERNEL,
              PROTOCOL, DESIGN, TEST_REPORT, OLD / 'input_manifest.csv', OLD / 'prepared_freeze.json',
              arithmetic.GEN, arithmetic.OUT / 'fixed_schedule.json', arithmetic.OUT / 'input_manifest.json']
    files += sorted(p for p in OUT.rglob('*') if p.is_file())
    records = arithmetic.bindings(files); save(OUT / 'input_manifest.json', records); arithmetic.verify_bindings(records)
    save(OUT / 'prepared_freeze.json', dict(utc=datetime.now(timezone.utc).isoformat(), manifest_sha256=sha(OUT/'input_manifest.json'),
        bindings=len(records), calls=CALLS, cases=CASES, options=OPTIONS, phase_seconds=PHASE, arithmetic_seconds=ARITHMETIC_PHASE,
        bit_limit=8192, cutoff=CUTOFF.isoformat(), optimizer_calls=0, separate_root_GO_required=True,
        ray_candidates=['+raw','+projected','-raw','-projected'], source_sha256=sha(Path(__file__)), checker_sha256=sha(Path(variant.__file__)), protocol_sha256=sha(PROTOCOL)))
    print(json.dumps(dict(status='PREPARED_VARIANT_NO_OPTIMIZATION', manifest_sha256=sha(OUT/'input_manifest.json'))), flush=True)


def tick_factory(deadline, overall):
    def tick():
        if time.perf_counter() >= min(deadline, overall) or datetime.now(timezone.utc) >= CUTOFF:
            raise arithmetic.PhaseLimit('Variant arithmetic/overall/04UTC guard')
    return tick


def solve_case(case, seconds, overall, call_state):
    import highspy
    import numpy as np
    from scipy.sparse import load_npz, csr_matrix, csc_matrix
    directory = OUT / case; matrix = load_npz(directory/'matrix.npz').tocsr()
    with np.load(directory/'bounds.npz',allow_pickle=False) as f: bounds = {k:f[k].copy() for k in f.files}
    with np.load(directory/'objective.npz',allow_pickle=False) as f: cost=f['objective'].copy()
    h = highspy.Highs(); require(h.version() == '1.12.0', 'Solver version changed')
    for key,value in {**OPTIONS,'time_limit':seconds,'log_file':str(directory/'solver.log')}.items():
        require(h.setOptionValue(key,value) == highspy.HighsStatus.kOk, 'Rejected option '+key)
    lp=highspy.HighsLp();lp.num_col_,lp.num_row_=matrix.shape[1],matrix.shape[0]
    lp.col_cost_=cost;lp.col_lower_,lp.col_upper_=bounds['column_lower'],bounds['column_upper']
    lp.row_lower_,lp.row_upper_=bounds['row_lower'],bounds['row_upper']
    lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise
    lp.a_matrix_.start_,lp.a_matrix_.index_,lp.a_matrix_.value_=matrix.indptr,matrix.indices,matrix.data
    require(h.passModel(lp)==highspy.HighsStatus.kOk, 'Proposal/model rejected')
    accepted=h.getLp();require(accepted.a_matrix_.format_ in (highspy.MatrixFormat.kRowwise,highspy.MatrixFormat.kColwise),'Matrix format')
    builder=csr_matrix if accepted.a_matrix_.format_==highspy.MatrixFormat.kRowwise else csc_matrix
    loaded=builder((accepted.a_matrix_.value_,accepted.a_matrix_.index_,accepted.a_matrix_.start_),shape=matrix.shape).tocsr()
    require((loaded!=matrix).nnz==0,'Solver altered coefficients')
    for a,b in ((accepted.col_lower_,bounds['column_lower']),(accepted.col_upper_,bounds['column_upper']),
                (accepted.row_lower_,bounds['row_lower']),(accepted.row_upper_,bounds['row_upper']),(accepted.col_cost_,cost)):
        require(np.array_equal(a,b),'Solver altered endpoints/objective')
    def remaining(): return min(overall-time.perf_counter(),(CUTOFF-datetime.now(timezone.utc)).total_seconds())
    decision=dict(case=case,configured_seconds=seconds,utc=datetime.now(timezone.utc).isoformat(),remaining_s=remaining())
    if remaining()<seconds+5: decision.update(status='NOT_STARTED_GUARD',optimizer_calls=0);save(directory/'solver_result.json',decision);return decision
    save(directory/'launch_decision.json',decision)
    if remaining()<seconds+5: decision.update(status='NOT_STARTED_GUARD_AFTER_DECISION',optimizer_calls=0);save(directory/'solver_result.json',decision);return decision
    start=time.perf_counter()
    try:
        call_state.update(optimizer_calls=1, started_perf=start)
        status=h.run();elapsed=time.perf_counter()-start;basis=h.getBasis();point=h.getSolution();info=h.getInfo()
        save(directory/'basis.json',dict(valid=basis.valid,column_status=[x.name for x in basis.col_status],row_status=[x.name for x in basis.row_status]))
        np.savez_compressed(directory/'numerical_point.npz',vector=np.asarray(point.col_value),row_activity=np.asarray(point.row_value))
        has_ray=False
        if case in TARGETS and h.getModelStatus()==highspy.HighsModelStatus.kInfeasible:
            exists_status, exists=h.getDualRayExist()
            if exists_status==highspy.HighsStatus.kOk and exists:
                ray_status,has_ray,ray=h.getDualRay()
                require(ray_status==highspy.HighsStatus.kOk and has_ray,'Existing ray retrieval failed')
                np.savez_compressed(directory/'raw_solver_ray.npz',ray=np.asarray(ray))
        result=dict(case=case,status=h.modelStatusToString(h.getModelStatus()),call_status=str(status),
            actual_seconds=elapsed,configured_seconds=seconds,soft_overrun_seconds=max(0.,elapsed-seconds),
            basis_valid=basis.valid,value_valid=point.value_valid,has_existing_ray=has_ray,
            ray_getter_called_only_after_exists=True,optimizer_calls=1,simplex_iterations=info.simplex_iteration_count,
            numerical_objective=None if not math.isfinite(info.objective_function_value) else info.objective_function_value)
    except Exception as error: result=dict(case=case,status='SOLVER_EXCEPTION',reason=type(error).__name__+': '+str(error),optimizer_calls=1,actual_seconds=time.perf_counter()-start)
    save(directory/'solver_result.json',result);return result


def check_target(v,case,result,tick,manifest_hash):
    directory=OUT/case;model=v.load_model(directory);candidates=[];selected=None
    if (directory/'raw_solver_ray.npz').exists():
        raw=v.vector(v.read_npz(directory/'raw_solver_ray.npz',('ray',))['ray'],('<f8',),model.rows,'raw ray')
        require(all(math.isfinite(x) for x in raw),'Nonfinite ray')
        for orientation in (1,-1):
            values=[orientation*x for x in raw]
            projected=[0. if (x>0 and not math.isfinite(model.row_lower[i])) or (x<0 and not math.isfinite(model.row_upper[i])) else x for i,x in enumerate(values)]
            for name,array in (('raw',values),('projected',projected)):
                tick(); item=dict(orientation=orientation,kind=name)
                certificate=dict(orientation=orientation,candidate=name,model_artifacts={k:sha(directory/k) for k in ('matrix.npz','bounds.npz')},
                    raw_solver_ray_sha256=sha(directory/'raw_solver_ray.npz'),row_metadata_sha256=sha(directory/'row_metadata.csv.gz'),
                    experiment_manifest_sha256=manifest_hash,distinct_flow_conserving_variant=True,
                    multipliers=[dict(row=i,value_hex=x.hex()) for i,x in enumerate(array) if x])
                try:
                    verification=v.check_ray(model,{i:Q(x) for i,x in enumerate(array) if x},TAU)
                    item['verification']=verification;certificate['verification']=verification
                except v.InvalidInput as error: item['rejected_reason']=str(error)
                path=directory/f'ray_{orientation:+d}_{name}.json';save(path,certificate);item['certificate_file']=path.name;candidates.append(item)
        chosen=next((x for x in candidates if x.get('verification',{}).get('expanded_pass')),None)
        if chosen is None: chosen=next((x for x in candidates if x.get('verification',{}).get('strict_pass')),None)
        if chosen is not None: selected=chosen
    report=dict(case=case,binary_status='UNKNOWN',ray_candidates=candidates,selected=selected)
    if selected:
        report['binary_status']='CERTIFIED_VARIANT_NEGATIVE';report['robust_expanded']=selected['verification']['expanded_pass']
    elif (directory/'numerical_point.npz').exists():
        data=v.read_npz(directory/'numerical_point.npz',('vector','row_activity'))['vector']
        if data.shape==(model.cols,) and all(math.isfinite(x) for x in data.values):
            tick();report['continuous_point_only']=v.check_point(model,data.values,(0,)*model.cols,TAU)
    save(directory/'classification.json',report);return report


def point_artifact(directory,point):
    save(directory/'rational_point.json',dict(schema='exact-fixed-schedule-point-v1',model_bindings=primal.model_bindings(directory),
        columns=len(point),values=[dict(column=j,value=rat(x)) for j,x in enumerate(point)]))


def reconstruct_identity(v,tick):
    directory=OUT/'identity_proposal';basis=v.json_read(directory/'basis.json') if (directory/'basis.json').exists() else {}
    with gzip.open(OUT/'exact_blocks.json.gz','rt',encoding='utf-8') as f: blocks=arithmetic.decoded_blocks(json.load(f))
    fixed={r['column']:parse_rat(r['value']) for r in v.json_read(OUT/'fixed_schedule.json')}
    point=[None]*29400
    for j,value in fixed.items():point[j]=value
    valid=basis.get('valid',False) and len(basis.get('column_status',[]))==17304 and len(basis.get('row_status',[]))==18480
    ledger=[];limited=False
    for b in blocks:
        t=b['hour'];record=dict(hour=t)
        if not valid:record['status']='UNRESOLVED_NO_BASIS'
        elif limited:record['status']='NOT_EVALUATED_PHASE_LIMIT'
        else:
            try:
                x,detail=arithmetic.reconstruct_hour(b,basis['column_status'][t*103:(t+1)*103],basis['row_status'][t*110:(t+1)*110],tick)
                record.update(detail);record['status']='EXACT_HOUR_POINT' if detail['exact_hour_pass'] else 'UNRESOLVED_CANDIDATE_VIOLATES'
                record['values']=[dict(column=j,value=rat(a)) for j,a in zip(b['columns'],x)]
                for j,value in zip(b['columns'],x):point[j]=value
            except arithmetic.PhaseLimit as error:limited=True;record.update(status='NOT_EVALUATED_PHASE_LIMIT',reason=str(error))
            except Exception as error:record.update(status='UNRESOLVED_RECONSTRUCTION',reason=type(error).__name__+': '+str(error))
        save(directory/f'hour_{t:03d}.json',record);ledger.append(dict(hour=t,status=record['status']))
    save(directory/'hour_outcomes.json',ledger)
    report=dict(identity_strict_capped=False,control_strict_capped=False,hour_denominator=168,counts=dict(Counter(x['status'] for x in ledger)))
    if all(x['status']=='EXACT_HOUR_POINT' for x in ledger):
        tick();point_artifact(OUT/CASES[0],point)
        check=variant.replay(OUT/CASES[0],OUT/CASES[0]/'rational_point.json',OUT/'fixed_schedule.json',tick)
        save(OUT/CASES[0]/'strict_point_check.json',check);report['identity_strict_capped']=check['accepted_strict_capped']
        if check['accepted_strict_capped']:
            native=load_native(v,OUT/CASES[1]/'native_inputs.npz');order=native['source_hour'].values;mapped=list(point)
            for t,source in enumerate(order):
                for offset,width in ((0,41),(18984,24),(23016,38)):
                    mapped[offset+t*width:offset+(t+1)*width]=point[offset+source*width:offset+(source+1)*width]
            point_artifact(OUT/CASES[1],mapped)
            control=variant.replay(OUT/CASES[1],OUT/CASES[1]/'rational_point.json',OUT/'fixed_schedule.json',tick)
            require(control['exact_objective']==check['exact_objective'],'Mapped exact fossil energy changed')
            save(OUT/CASES[1]/'strict_point_check.json',control);report['control_strict_capped']=control['accepted_strict_capped']
    save(OUT/'identity_control_classification.json',report);return report


def run():
    v=helper_gate();require(not (OUT/'execution_marker.json').exists(),'Single variant execution already attempted')
    freeze=v.json_read(OUT/'prepared_freeze.json');require(sha(OUT/'input_manifest.json')==freeze['manifest_sha256'],'Manifest changed')
    records=v.json_read(OUT/'input_manifest.json');validation=time.perf_counter();arithmetic.verify_bindings(records)
    require(freeze['calls']==[list(x) for x in CALLS] and freeze['options']==OPTIONS,'Frozen call plan/options changed')
    save(OUT/'execution_marker.json',dict(utc=datetime.now(timezone.utc).isoformat(),manifest_sha256=freeze['manifest_sha256'],validation_seconds=time.perf_counter()-validation))
    start=time.perf_counter();overall=start+PHASE;calls=[]
    for case,seconds in CALLS:
        call_state=dict(optimizer_calls=0)
        try:calls.append(solve_case(case,seconds,overall,call_state))
        except Exception as error:
            attempted=call_state['optimizer_calls']
            record=dict(case=case,status='POSTCALL_ERROR' if attempted else 'PRECALL_ERROR',optimizer_calls=attempted,
                        reason=type(error).__name__+': '+str(error))
            if attempted: record['actual_seconds']=time.perf_counter()-call_state['started_perf']
            save(OUT/case/('postcall_error.json' if attempted else 'precall_error.json'),record);calls.append(record)
    save(OUT/'calls.json',calls)
    math_start=time.perf_counter();tick=tick_factory(math_start+ARITHMETIC_PHASE,overall);targets=[]
    for case in TARGETS:
        try:targets.append(check_target(v,case,next(x for x in calls if x['case']==case),tick,freeze['manifest_sha256']))
        except Exception as error:
            record=dict(case=case,binary_status='UNKNOWN',reason=type(error).__name__+': '+str(error))
            save(OUT/case/'classification_error.json',record);targets.append(record)
    try:controls=reconstruct_identity(v,tick)
    except Exception as error:
        controls=dict(identity_strict_capped=False,control_strict_capped=False,reason=type(error).__name__+': '+str(error))
        save(OUT/'identity_control_error.json',controls)
    arithmetic.verify_bindings(records)
    save(OUT/'outcomes.json',dict(ordinary_denominator=2,targets=targets,controls=controls,original_model_claims_unchanged=True))
    elapsed=time.perf_counter()-start;math_elapsed=time.perf_counter()-math_start
    save(OUT/'completion.json',dict(optimizer_calls=sum(x['optimizer_calls'] for x in calls),configured_maximum_calls=3,
        actual_solve_seconds=sum(x.get('actual_seconds',0.) for x in calls),phase_seconds=elapsed,phase_budget=PHASE,
        arithmetic_seconds=math_elapsed,arithmetic_budget=ARITHMETIC_PHASE,arithmetic_soft_overrun=max(0.,math_elapsed-ARITHMETIC_PHASE),
        phase_soft_overrun=max(0.,elapsed-PHASE),ordinary_denominator=2,identity_hour_denominator=168,
        independent_postrun_review_required=True,original_model_equivalence_claim=False))
    print(json.dumps(dict(controls=controls,targets=[dict(case=x['case'],status=x['binary_status']) for x in targets])),flush=True)


def synthetic():
    # Only tiny invented graph data; no native/model archive is opened.
    b=Q(3,8);theta=[Q(2,3),Q(1,3)];flow=b*(theta[0]-theta[1]);p=[Q(5,8),Q(1,8)];load=[Q(1,2),Q(1,4)]
    require(p[0]-flow==load[0] and p[1]+flow==load[1] and sum(p)==sum(load),'Flow incidence fixture')
    require(flow==Q(1,8),'Branch rational definition fixture')
    old_net=sum(load)+Q(1,2**52);require(sum(p)!=old_net,'Old aggregate difference fixture')
    a=[[Q(2),Q(1),Q(0)],[Q(0),Q(0),Q(3)],[Q(0),Q(4),Q(5)]]
    x,pivots=arithmetic.exact_solve(a,[Q(1),Q(1),Q(1)])
    require(x==[Q(7,12),Q(-1,6),Q(1,3)] and pivots[1]['chosen_current_row']==2,'Three-dimensional exact division/pivot fixture')
    return dict(status='SYNTHETIC_ONLY_PASS',tests=['two_bus_flow_definition','signed_incidence_conservation','old_aggregate_is_distinct',
        'three_by_three_Bareiss_nonunit_division_and_late_swap'],actual_models_read=0,optimizer_calls=0,
        source_sha256=sha(Path(__file__)),checker_sha256=sha(Path(variant.__file__)))


def main():
    parser=argparse.ArgumentParser();g=parser.add_mutually_exclusive_group(required=True)
    g.add_argument('--synthetic-only',action='store_true');g.add_argument('--prepare-only',action='store_true');g.add_argument('--run-prepared',action='store_true')
    parser.add_argument('--report',type=Path);a=parser.parse_args()
    if a.synthetic_only:
        require(a.report is not None and not a.report.exists(),'New synthetic report required')
        try:result=synthetic()
        except Exception as error:save(a.report,dict(status='SYNTHETIC_FAILED',reason=str(error),optimizer_calls=0));raise
        save(a.report,result);print(json.dumps(result))
    elif a.prepare_only:prepare()
    else:run()


if __name__=='__main__':main()
