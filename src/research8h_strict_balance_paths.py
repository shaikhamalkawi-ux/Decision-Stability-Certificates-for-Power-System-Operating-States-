"""Frozen rational branch-path diagnostics; prepare and execution are separate."""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
import csv
import gzip
import hashlib
import heapq
import importlib.util
import json
import math
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/research8h/strict_balance_paths'
PROTOCOL = ROOT / 'docs/research8h/STRICT_BALANCE_PATHS_PROTOCOL.md'
DESIGN = ROOT / 'docs/research8h/STRICT_NOMINAL_WITNESS_DESIGN_ASSESSMENT.md'
OLD = ROOT / 'results/research8h/nominal_balance_audit'
KERNEL = ROOT / 'src/research8h_standalone_verify.py'
KERNEL_SHA = '708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'
OLD_FREEZE_SHA = 'fff9aedad3f9b29df7b4cfdb67ff1c906653d9c152e385419966263fc522bd4f'
MONTHS = (1, 4, 7, 10)
HOURS = 168
ORIENTATIONS = (1, -1)
TAU = Q.from_float(1e-5)
PHASE_SECONDS = 600.
THETA = 18984
BUSES = 24


def require(value, message):
    if not value: raise ValueError(message)


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def rat(value): return dict(numerator=str(value.numerator), denominator=str(value.denominator))
def fraction(value): return Q(int(value['numerator']), int(value['denominator']))


def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False); stream.write('\n')


def verify_bindings(records):
    require(records and len({r['path'] for r in records}) == len(records), 'Empty or duplicate manifest')
    for record in records:
        path = Path(record['path'])
        require(path.is_file() and path.stat().st_size == record['bytes'] and sha(path) == record['sha256'], 'Changed input: ' + str(path))


def kernel():
    require(sha(KERNEL) == KERNEL_SHA, 'Unreviewed NPZ kernel')
    spec = importlib.util.spec_from_file_location('strict_path_npz_kernel', KERNEL)
    module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module; spec.loader.exec_module(module)
    return module


def matrix_row(model, row):
    return tuple((model.indices[e], Q(model.data[e])) for e in range(model.indptr[row], model.indptr[row + 1]))


def inspect_models(v):
    """Validate complete matrices and mappings only; no path or residual calculation."""
    cache = {}; summaries = []; common = None
    for month in MONTHS:
        directory = ROOT / f'results/research8h/seasonal_reference/month_{month:02d}'
        model = v.load_model(directory); metadata = read(directory / 'model_metadata.json')
        with gzip.open(directory / 'row_metadata.csv.gz', 'rt', newline='') as stream: labels = list(csv.DictReader(stream))
        require((model.rows, model.cols) == (34680, 23016) and len(labels) == model.rows, 'Unexpected original model shape')
        require(metadata['offsets'] == dict(P=0, U=6888, Y=10920, Z=14952, theta=THETA), 'Column order changed')
        require((metadata['hours'], metadata['buses'], metadata['branches']) == (HOURS, BUSES, 38), 'Network shape changed')
        by_hour = {t: dict(balance=[], edges=[]) for t in range(HOURS)}
        for row, label in enumerate(labels):
            require(int(label['row']) == row, 'Row label index changed')
            family = label['family']; hour = int(label['hour_0based'])
            if family in ('aggregate_balance', 'nodal_balance'):
                require(hour in by_hour and model.row_lower[row] == model.row_upper[row], 'Balance is not an hourly equality')
                by_hour[hour]['balance'].append((row, 1 if family == 'aggregate_balance' else -1))
            elif family == 'branch_flow':
                require(hour in by_hour, 'Invalid branch hour')
                terms = [(j, c) for j, c in matrix_row(model, row) if c]
                require(len(terms) == 2 and terms[0][1] == -terms[1][1], 'Branch lacks exact opposite coefficients')
                require(all(THETA + hour * BUSES <= j < THETA + (hour + 1) * BUSES for j, _ in terms), 'Branch has a nonlocal angle coordinate')
                positive = next((j, c) for j, c in terms if c > 0)
                negative = next((j, c) for j, c in terms if c < 0)
                require(0 < model.row_upper[row] == -model.row_lower[row] < math.inf, 'Branch bounds are not positive symmetric finite intervals')
                by_hour[hour]['edges'].append(dict(row=row, uid=label['uid'], positive_bus=positive[0] - THETA - hour * BUSES,
                    negative_bus=negative[0] - THETA - hour * BUSES, b=positive[1], rate=Q(model.row_upper[row])))
        for hour, block in by_hour.items():
            require(len(block['balance']) == 25 and sum(s == 1 for _, s in block['balance']) == 1, 'Balance multiplier norm is not 25')
            require(len(block['edges']) == 38, 'Branch count changed')
            pins = [j for j in range(BUSES) if model.lower[THETA + hour * BUSES + j] == model.upper[THETA + hour * BUSES + j] == 0.]
            require(len(pins) == 1, 'Expected one zero reference-column pin')
            block['reference'] = pins[0]
            block['signature'] = tuple((e['uid'], e['positive_bus'], e['negative_bus'], e['b'], e['rate']) for e in block['edges'])
            signature = (tuple(metadata['bus_ids']), pins[0], block['signature'])
            if common is None: common = signature
            require(signature == common, 'Hour-normalized branch/reference block differs')
            # Connectivity is checked without finding or comparing path costs.
            reached = {pins[0]}
            while True:
                grown = reached | {e['positive_bus'] for e in block['edges'] if e['negative_bus'] in reached} | {e['negative_bus'] for e in block['edges'] if e['positive_bus'] in reached}
                if grown == reached: break
                reached = grown
            require(len(reached) == BUSES, 'Branch graph disconnected from the actual pin')
        reference = common[1]
        summaries.append(dict(month=month, rows=model.rows, columns=model.cols, branch_rows=HOURS * 38,
            exact_opposite_branch_coefficients=True, symmetric_finite_limits=True, reference_bus_index=reference,
            reference_bus_ID=metadata['bus_ids'][reference], reference_is_column_bound=True,
            common_hour_normalized_block=True, graph_connected=True, no_paths_or_balance_diagnostics_computed=True))
        cache[month] = (model, labels, metadata, by_hour)
    return cache, summaries


def prepare():
    require(not OUT.exists(), 'Preparation directory already exists')
    require(sha(OLD / 'freeze.json') == OLD_FREEZE_SHA, 'Old nominal audit freeze changed')
    old = read(OLD / 'freeze.json'); verify_bindings(old['inputs'])
    require(read(OLD / 'independent_replay.json')['status'] == 'INDEPENDENT_INTEGER_DYADIC_REPLAY_PASS', 'Old audit independent replay missing')
    started = time.perf_counter(); _, structures = inspect_models(kernel())
    OUT.mkdir(parents=True, exist_ok=False)
    save(OUT / 'structure_preflight.json', dict(months=structures, elapsed_s=time.perf_counter() - started, diagnostic_orientations_executed=0, optimization_calls=0))
    save(OUT / 'prior_readonly_inspection_note.json', dict(event='Prior design-only structural inspection initially assumed reference index zero and stopped at that assertion.',
        correction='The unchanged archives instead pin index 12, bus 113. Current code discovers and validates the actual zero column pin.',
        initial_assertion_failure_retained=True, new_path_bounds_or_separations_in_that_inspection=0, original_files_changed=False))
    paths = [Path(__file__), PROTOCOL, DESIGN, KERNEL, OLD / 'freeze.json', OLD / 'summary.json', OLD / 'independent_replay.json']
    paths += [Path(r['path']) for r in old['inputs']]
    paths += [OLD / f'month_{m:02d}.json' for m in MONTHS]
    paths += [ROOT / f'results/research8h/seasonal_reference/month_{m:02d}/model_metadata.json' for m in MONTHS]
    paths += [OUT / 'structure_preflight.json', OUT / 'prior_readonly_inspection_note.json']
    bindings = [dict(path=str(p.resolve()), bytes=p.stat().st_size, sha256=sha(p)) for p in dict.fromkeys(paths)]
    save(OUT / 'input_manifest.json', bindings); verify_bindings(bindings)
    save(OUT / 'prepared_freeze.json', dict(utc=datetime.now(timezone.utc).isoformat(), source_sha256=sha(Path(__file__)),
        protocol_sha256=sha(PROTOCOL), manifest_sha256=sha(OUT / 'input_manifest.json'), bindings=len(bindings),
        months=MONTHS, hours_per_month=HOURS, orientations=ORIENTATIONS, hour_week_denominator=672,
        orientation_denominator=1344, path_metric='strict exact R/abs(b)', all_nonreference_coordinates_use_paths=True,
        phase_seconds=PHASE_SECONDS, phase_starts_after_recorded_validation=True,
        diagnostic_orientations_executed=0, optimizer_calls=0, separate_root_execution_GO_required=True))
    print(json.dumps(dict(status='PREPARED_NO_DIAGNOSTIC_EXECUTION', bindings=len(bindings), manifest_sha256=sha(OUT / 'input_manifest.json'))), flush=True)


def shortest_paths(edges, reference):
    """One strict metric; exact distance then complete archived row-ID tuple."""
    adjacency = {j: [] for j in range(BUSES)}
    for edge in edges:
        p, n, b = edge['positive_bus'], edge['negative_bus'], edge['b']
        require(b > 0 and edge['rate'] > 0, 'Dijkstra needs strictly positive exact edge costs')
        adjacency[n].append((edge['row'], p, Q(1) / b, edge['rate'] / b))
        adjacency[p].append((edge['row'], n, -Q(1) / b, edge['rate'] / b))
    for entries in adjacency.values(): entries.sort(key=lambda x: (x[0], x[1]))
    best = {reference: (Q(0), (), ())}; queue = [(Q(0), (), reference)]
    while queue:
        distance, ids, bus = heapq.heappop(queue)
        if (distance, ids) != best[bus][:2]: continue
        steps = best[bus][2]
        for row, target, coefficient, cost in adjacency[bus]:
            candidate = (distance + cost, ids + (row,))
            if target not in best or candidate < best[target][:2]:
                target_steps = steps + ((row, bus, target, coefficient),)
                best[target] = (*candidate, target_steps); heapq.heappush(queue, (*candidate, target))
    require(len(best) == BUSES, 'Not every bus has a path')
    return best


def direct_ray(model, multipliers):
    """Evaluate every coefficient of every selected original row, without a float threshold."""
    combined = {}; beta = expanded_beta = norm = Q(0)
    for row, value in sorted(multipliers.items()):
        require(isinstance(value, Q) and value != 0 and 0 <= row < model.rows, 'Invalid rational row multiplier')
        endpoint = model.row_lower[row] if value > 0 else model.row_upper[row]
        require(math.isfinite(endpoint), 'Rational multiplier selects infinite endpoint')
        beta += value * Q(endpoint); norm += abs(value)
        expanded_beta += value * (Q(endpoint) - TAU if value > 0 else Q(endpoint) + TAU)
        for column, coefficient in matrix_row(model, row):
            combined[column] = combined.get(column, Q(0)) + value * coefficient
    maximum = expanded_maximum = Q(0)
    for column, value in combined.items():
        endpoint = model.upper[column] if value >= 0 else model.lower[column]
        maximum += value * Q(endpoint)
        expanded_maximum += value * (Q(endpoint) + TAU if value >= 0 else Q(endpoint) - TAU)
    column_norm = sum(map(abs, combined.values()), Q(0))
    gap = beta - maximum; expanded_gap = expanded_beta - expanded_maximum
    require(expanded_gap == gap - TAU * (norm + column_norm), 'Direct endpoint and norm-form gap differ')
    return dict(beta=rat(beta), box_maximum=rat(maximum), strict_gap=rat(gap), expanded_beta=rat(expanded_beta),
        expanded_box_maximum=rat(expanded_maximum), expanded_gap=rat(expanded_gap), row_l1=rat(norm), column_l1=rat(column_norm),
        all_touched_column_coefficients=[dict(column=j, **rat(c)) for j, c in sorted(combined.items())],
        nonzero_column_count=sum(bool(c) for c in combined.values())), combined


def path_table(edges, reference, paths):
    lookup = {e['row']: e for e in edges}; records = []
    for bus in range(BUSES):
        distance, ids, steps = paths[bus]; coefficients = [Q(0)] * BUSES; reconstructed_distance = Q(0)
        for row, source, target, value in steps:
            edge = lookup[row]
            coefficients[edge['positive_bus']] += value * edge['b']; coefficients[edge['negative_bus']] -= value * edge['b']
            reconstructed_distance += abs(value) * edge['rate']
        expected = [Q(0)] * BUSES; expected[bus] += 1; expected[reference] -= 1
        require(coefficients == expected and reconstructed_distance == distance and tuple(x[0] for x in steps) == ids, 'Exact path reconstruction failed')
        records.append(dict(bus_index=bus, strict_distance=rat(distance), ordered_base_hour_row_ids=list(ids),
            steps=[dict(base_hour_row=row, from_bus=source, to_bus=target, multiplier=rat(value)) for row, source, target, value in steps],
            exact_path_coefficient_identity=True))
    return records


def focused_checks():
    # Fixed synthetic checks only; no scientific diagnostic cases or optimizer.
    edges = [dict(row=10, negative_bus=0, positive_bus=1, b=Q(1), rate=Q(2)),
             dict(row=9, negative_bus=0, positive_bus=2, b=Q(3), rate=Q(3)),
             dict(row=12, negative_bus=2, positive_bus=1, b=Q(7), rate=Q(7))]
    # Add leaves solely to use the same fixed-size path routine.
    edges += [dict(row=100+j, negative_bus=0, positive_bus=j, b=Q(1), rate=Q(10+j)) for j in range(3, BUSES)]
    paths = shortest_paths(edges, 0)
    require(paths[1][1] == (9, 12) and paths[1][0] == 2, 'Equal-distance lexicographic path check failed')
    require(tuple(x[3] for x in paths[1][2]) == (Q(1, 3), Q(1, 7)), 'Path coefficient division lost rational exactness')
    path_table(edges, 0, paths)
    # q_ref=1,q_a=1,q_b=-2: edge gain is nonzero; reference gain is nonzero only at tau>0.
    for expansion in (Q(0), TAU):
        edge_gain = (Q(2) + expansion) * (abs(Q(1)) + abs(Q(-2)) - abs(Q(-1)))
        ref_gain = expansion * (abs(Q(1)) + abs(Q(1)) + abs(Q(-2)) - abs(Q(0)))
        independent_cost = (Q(2) + expansion) + 2 * ((Q(2) + expansion) + (Q(3) + expansion)) + 4 * expansion
        merged_cost = (Q(2) + expansion) + 2 * (Q(3) + expansion)
        require(independent_cost - merged_cost == edge_gain + ref_gain, 'Shared-edge/reference gain identity failed')
        require(edge_gain > 0 and (ref_gain == 0 if expansion == 0 else ref_gain > 0), 'Synthetic gain regime mismatch')
    return dict(status='FOCUSED_PATH_AND_GAIN_CHECKS_PASS', exact_tie_break=True, nondyadic_path_coefficients=True,
        path_reconstruction=True, nonzero_shared_edge_gain_in_both_regimes=True,
        zero_strict_reference_gain=True, nonzero_expanded_reference_gain=True, optimization_calls=0)


def diagnostic(model, block, base_edges, paths, old, month, hour, orientation, paths_hash, model_binding):
    y0 = {row: Q(orientation * sign) for row, sign in block['balance']}
    require(sum(map(abs, y0.values()), Q(0)) == 25, 'Original balance multiplier norm changed')
    q = {}; beta = Q(0)
    for row, value in y0.items():
        beta += value * Q(model.row_lower[row])
        for column, coefficient in matrix_row(model, row): q[column] = q.get(column, Q(0)) + value * coefficient
    start = THETA + hour * BUSES; reference = block['reference']; reference_column = start + reference
    require(all(not c or start <= j < start + BUSES for j, c in q.items()), 'Balance difference has non-angle or cross-hour support')
    local_q = [q.get(start+j, Q(0)) for j in range(BUSES)]
    require(beta == orientation * fraction(old['rhs_difference']), 'Original audit RHS mismatch')
    old_q = {r['column']: orientation * fraction(r['value']) for r in old['nonzero_difference_coefficients']}
    require({j: c for j, c in q.items() if c} == old_q, 'Original audit exact coefficients mismatch')
    base_to_slot = {e['row']: i for i, e in enumerate(base_edges)}
    merged = [Q(0)] * len(base_edges); unmerged_abs = [Q(0)] * len(base_edges); contributions = []
    for bus in range(BUSES):
        if bus == reference: continue
        parts = []
        for base_row, _, _, p in paths[bus][2]:
            slot = base_to_slot[base_row]; value = local_q[bus] * p
            merged[slot] += value; unmerged_abs[slot] += abs(value)
            parts.append(dict(base_hour_row=base_row, actual_hour_row=block['edges'][slot]['row'], value=rat(value)))
        contributions.append(dict(bus_index=bus, angle_column=start+bus, q=rat(local_q[bus]), path_weight_contributions=parts))
    multipliers = dict(y0)
    for edge, value in zip(block['edges'], merged):
        require(edge['row'] not in multipliers, 'Branch and balance rows overlap')
        if value: multipliers[edge['row']] = -value
    report, combined = direct_ray(model, multipliers)
    s = sum(local_q, Q(0))
    require(all(c == (s if j == reference_column else 0) for j, c in combined.items()), 'Original-row reconstruction failed to cancel a column')
    require(combined.get(reference_column, Q(0)) == s, 'Reference residual mismatch')
    require(model.lower[reference_column] == model.upper[reference_column] == 0., 'Original reference is not pinned zero')
    gain_reports = []
    for expansion, gap_name in ((Q(0), 'strict_gap'), (TAU, 'expanded_gap')):
        beta_relaxed = beta - 25 * expansion
        original_q_l1 = sum(map(abs, local_q), Q(0))
        unmerged_cost = sum(((edge['rate'] + expansion) * cost for edge, cost in zip(block['edges'], unmerged_abs)), Q(0))
        merged_cost = sum(((edge['rate'] + expansion) * abs(value) for edge, value in zip(block['edges'], merged)), Q(0))
        edge_gain = unmerged_cost - merged_cost
        reference_gain = expansion * (original_q_l1 - abs(s))
        independent_gap = beta_relaxed - unmerged_cost - expansion * original_q_l1
        direct_formula = beta_relaxed - merged_cost - expansion * abs(s)
        require(edge_gain >= 0 and reference_gain >= 0, 'Negative support cancellation gain')
        require(direct_formula == fraction(report[gap_name]) == independent_gap + edge_gain + reference_gain, 'Direct/path/cancellation gap identity failed')
        gain_reports.append(dict(tau=rat(expansion), independent_per_variable_path_gap=rat(independent_gap),
            merged_edge_cost=rat(merged_cost), unmerged_edge_cost=rat(unmerged_cost), shared_edge_gain=rat(edge_gain),
            reference_gain=rat(reference_gain), assembled_original_row_gap=report[gap_name], exact_identity=True))
    upper_bound = abs(beta) - 25 * TAU
    expanded = fraction(report['expanded_gap']); strict = fraction(report['strict_gap'])
    require(expanded <= upper_bound < 0, 'Expanded upper-bound prediction failed: mandatory review stop')
    return dict(month=month, hour_0based=hour, orientation=orientation,
        status='CERTIFIED_STRICT_REPRESENTATION_INFEASIBLE' if strict > 0 else 'VALID_NONSEPARATING_RATIONAL_CANDIDATE',
        strict_separation=strict > 0, expanded_separation=expanded > 0, original_model_unchanged=True, model_binding=model_binding,
        reference_column=reference_column, reference_bus_index=reference, q_ref=rat(local_q[reference]), sum_q=rat(s), beta=rat(beta),
        all_angle_q=[dict(column=start+j, value=rat(c)) for j, c in enumerate(local_q)],
        original_balance_multipliers=[dict(row=r, **rat(c)) for r, c in sorted(y0.items())], original_balance_l1=rat(Q(25)),
        common_paths_sha256=paths_hash, unmerged_path_contributions=contributions,
        merged_branch_contributions=[dict(row=e['row'], base_hour_row=base['row'], w=rat(w), added_row_multiplier=rat(-w), unmerged_absolute_sum=rat(a))
            for e, base, w, a in zip(block['edges'], base_edges, merged, unmerged_abs)],
        original_matrix_row_multipliers=[dict(row=r, **rat(c)) for r, c in sorted(multipliers.items())],
        direct_original_row_check=report, support_gain_checks=gain_reports,
        expanded_gap_upper_bound_abs_beta_minus_25tau=rat(upper_bound), expanded_prediction_verified=True,
        scope='Exact archived representation diagnostic; nonseparation is not feasibility and strict separation is not physical infeasibility.')


def run_prepared():
    validation_start = time.perf_counter(); freeze = read(OUT / 'prepared_freeze.json')
    require(not (OUT / 'execution_started.json').exists(), 'Execution already attempted; no retries')
    require(sha(Path(__file__)) == freeze['source_sha256'] and sha(PROTOCOL) == freeze['protocol_sha256'], 'Frozen implementation changed')
    require(sha(OUT / 'input_manifest.json') == freeze['manifest_sha256'], 'Frozen manifest changed')
    bindings = read(OUT / 'input_manifest.json'); verify_bindings(bindings)
    cache, structures = inspect_models(kernel())
    require(structures == read(OUT / 'structure_preflight.json')['months'], 'Prepared structural inspection changed')
    validation_seconds = time.perf_counter() - validation_start
    save(OUT / 'execution_started.json', dict(utc=datetime.now(timezone.utc).isoformat(), validation_seconds=validation_seconds,
        arithmetic_phase_seconds=PHASE_SECONDS, phase_starts_after_validation=True, orientation_denominator=1344, optimizer_calls=0))
    phase = time.perf_counter(); completed = 0; ledger = []
    try:
        save(OUT / 'focused_checks.json', focused_checks())
        reference_block = cache[MONTHS[0]][3][0]; base_edges = reference_block['edges']; reference = reference_block['reference']
        paths = shortest_paths(base_edges, reference)
        path_records = path_table(base_edges, reference, paths)
        save(OUT / 'common_paths.json', dict(reference_bus_index=reference, reference_bus_ID=cache[MONTHS[0]][2]['bus_ids'][reference],
            metric='strict exact R/abs(b)', tie_break='exact distance, complete ordered base-hour original row-ID tuple, final heap bus index',
            base_model_month=MONTHS[0], base_hour=0, paths=path_records,
            edges=[dict(base_hour_row=e['row'], uid=e['uid'], positive_bus=e['positive_bus'], negative_bus=e['negative_bus'], b=rat(e['b']), rate=rat(e['rate'])) for e in base_edges]))
        paths_hash = sha(OUT / 'common_paths.json')
        for month in MONTHS:
            model, _, _, blocks = cache[month]; old = read(OLD / f'month_{month:02d}.json')
            directory = ROOT / f'results/research8h/seasonal_reference/month_{month:02d}'
            model_binding = dict(directory=str(directory.resolve()),
                artifacts={name: sha(directory / name) for name in ('matrix.npz', 'bounds.npz', 'row_metadata.csv.gz')},
                experiment_manifest_sha256=freeze['manifest_sha256'])
            require(len(old) == HOURS and [r['hour_0based'] for r in old] == list(range(HOURS)), 'Old audit hour ledger changed')
            with gzip.open(OUT / f'month_{month:02d}.jsonl.gz', 'xt', encoding='utf-8') as stream:
                for hour in range(HOURS):
                    for orientation in ORIENTATIONS:
                        before = time.perf_counter() - phase
                        if before >= PHASE_SECONDS:
                            record = dict(month=month, hour_0based=hour, orientation=orientation, status='NOT_EVALUATED_PHASE_LIMIT', elapsed_before_s=before)
                        else:
                            record = diagnostic(model, blocks[hour], base_edges, paths, old[hour], month, hour, orientation, paths_hash, model_binding)
                            completed += 1
                            record.update(elapsed_before_s=before, elapsed_after_s=time.perf_counter() - phase)
                        stream.write(json.dumps(record, allow_nan=False) + '\n')
                        ledger.append(dict(month=month, hour_0based=hour, orientation=orientation, status=record['status'],
                            strict_separation=record.get('strict_separation'), expanded_separation=record.get('expanded_separation')))
            print(json.dumps(dict(month=month, evaluated_so_far=completed, phase_elapsed_s=time.perf_counter() - phase)), flush=True)
        require(len(ledger) == 1344, 'Scheduled denominator lost')
        verify_bindings(bindings)
        save(OUT / 'outcomes.json', ledger)
        elapsed = time.perf_counter() - phase
        save(OUT / 'completion.json', dict(utc=datetime.now(timezone.utc).isoformat(), orientation_denominator=1344,
            hour_week_denominator=672, evaluated_orientations=completed, not_evaluated=1344-completed,
            strict_separating_orientations=sum(r['strict_separation'] is True for r in ledger),
            expanded_separating_orientations=sum(r['expanded_separation'] is True for r in ledger),
            status_counts=dict(Counter(r['status'] for r in ledger)), all_frozen_hashes_unchanged=True,
            validation_seconds=validation_seconds, arithmetic_phase_seconds=elapsed,
            phase_soft_overrun_s=max(0., elapsed-PHASE_SECONDS), optimizer_calls=0, path_metrics_tried=1,
            all_nonreference_coordinates_use_paths=True, independent_postrun_review_required=True))
    except Exception as error:
        save(OUT / 'failure.json', dict(status='HARD_REVIEW_STOP', error_type=type(error).__name__, error=str(error),
            intended_orientation_denominator=1344, orientations_completed=completed, arithmetic_phase_seconds=time.perf_counter()-phase,
            partial_outputs_preserved=True, optimizer_calls=0, automatic_retry_allowed=False))
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prepare-only', action='store_true'); mode.add_argument('--run-prepared', action='store_true')
    args = parser.parse_args()
    prepare() if args.prepare_only else run_prepared()
