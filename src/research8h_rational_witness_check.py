"""Exact rational primal replay; no optimizer, NumPy or reconstruction import."""
from __future__ import annotations
import argparse
import csv
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
KERNEL = ROOT / 'src/research8h_standalone_verify.py'
KERNEL_SHA = '708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'
BITS = 8192


def require(value, message):
    if not value: raise ValueError(message)


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def rat(value): return {'numerator': str(value.numerator), 'denominator': str(value.denominator)}


def parse_rat(record):
    require(type(record) is dict and set(record) == {'numerator', 'denominator'}, 'Noncanonical rational object')
    n, d = record['numerator'], record['denominator']
    require(type(n) is str and re.fullmatch(r'0|-?[1-9][0-9]*', n) and
            type(d) is str and re.fullmatch(r'[1-9][0-9]*', d), 'Noncanonical integer encoding')
    require(len(n) <= 2468 and len(d) <= 2467, 'Rational string exceeds bit guard')
    ni, di = int(n), int(d)
    require(abs(ni).bit_length() <= BITS and di.bit_length() <= BITS, 'Rational exceeds bit guard')
    value = Q(ni, di)
    require(value.numerator == ni and value.denominator == di, 'Unreduced rational')
    return value


def kernel():
    require(sha(KERNEL) == KERNEL_SHA, 'Changed reviewed NPZ kernel')
    spec = importlib.util.spec_from_file_location('rational_witness_npz_kernel', KERNEL)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def model_bindings(directory):
    return {name: sha(Path(directory) / name) for name in
            ('matrix.npz', 'bounds.npz', 'integrality.npz', 'objective.npz')}


def check_point(v, model, point, mask, fixed, objective, tick=lambda: None):
    """Direct complete original-row check. Never expands an endpoint."""
    v.validate_model(model)
    require(len(point) == model.cols and all(type(x) is Q for x in point), 'Invalid rational point')
    require(len(mask) == model.cols and all(type(x) is int and x in (0, 1) for x in mask), 'Invalid binary mask')
    require(len(objective) == model.cols, 'Objective length changed')
    require(set(fixed) == {j for j, flag in enumerate(mask) if flag}, 'Fixed schedule does not cover original mask')
    failures = []; violations = 0
    def fail(item):
        nonlocal violations
        violations += 1
        if len(failures) < 20: failures.append(item)
    for j, x in enumerate(point):
        if j % 256 == 0: tick()
        if x < Q(model.lower[j]) or x > Q(model.upper[j]): fail({'column': j, 'kind': 'bound'})
        if mask[j] and (x not in (0, 1) or x != fixed[j]): fail({'column': j, 'kind': 'fixed_binary'})
    for i in range(model.rows):
        if i % 64 == 0: tick()
        activity = sum((Q(model.data[e]) * point[model.indices[e]]
                        for e in range(model.indptr[i], model.indptr[i + 1])), Q(0))
        if math.isfinite(model.row_lower[i]) and activity < Q(model.row_lower[i]):
            fail({'row': i, 'side': 'lower', 'gap': rat(Q(model.row_lower[i]) - activity)})
        if math.isfinite(model.row_upper[i]) and activity > Q(model.row_upper[i]):
            fail({'row': i, 'side': 'upper', 'gap': rat(activity - Q(model.row_upper[i]))})
    energy = sum((Q(c) * x for c, x in zip(objective, point)), Q(0))
    return dict(pass_strict=violations == 0, tau=0, rows_checked=model.rows,
                columns_checked=model.cols, original_binary_coordinates=sum(mask),
                violations=violations, first_violations=failures, exact_objective=rat(energy))


def native_spec(gen_path, metadata):
    with Path(gen_path).open(encoding='utf-8-sig', newline='') as f: records = list(csv.DictReader(f))
    require(len({r['GEN UID'] for r in records}) == len(records), 'Duplicate native generator')
    records = {r['GEN UID']: r for r in records}
    names = metadata['unit_names']; thermal = metadata['thermal_unit_names']
    require(len(names) == 41 and len(set(names)) == 41 and len(thermal) == 24, 'Unexpected native roster')
    result = []
    for name in names:
        r = records[name]
        rate_per_minute = float(r['Ramp Rate MW/Min'])
        # Preserve the old physical check's binary64 multiplication, then interpret its result exactly.
        hourly_binary64 = rate_per_minute * 60.0
        require(math.isfinite(hourly_binary64) and hourly_binary64 >= 0, 'Invalid ramp rate')
        up = math.ceil(float(r['Min Up Time Hr'])); down = math.ceil(float(r['Min Down Time Hr']))
        require(up >= 0 and down >= 0, 'Invalid native residence time')
        result.append(dict(uid=name, bus=int(r['Bus ID']), category=r['Category'],
            thermal=name in thermal, minimum_up=up, minimum_down=down,
            per_minute_binary64_hex=rate_per_minute.hex(), hourly_binary64_hex=hourly_binary64.hex(),
            hourly_rational=rat(Q(hourly_binary64)),
            difference_from_exact_times_60=rat(Q(hourly_binary64) - 60 * Q(rate_per_minute))))
    return result


def check_native(v, point, directory, metadata, spec, tick=lambda: None):
    """Supplementary exact dispatch/state/ramp checks. DC network is checked by original matrix replay."""
    arrays = v.read_npz(Path(directory) / 'native_inputs.npz', ('pmin', 'pmax', 'net', 'rows', 'nodal'))
    require(arrays['pmin'].shape == arrays['pmax'].shape == (168, 41), 'Native output shapes')
    require(arrays['net'].shape == arrays['rows'].shape == (168,) and arrays['nodal'].shape == (168, 24), 'Native load shapes')
    require(arrays['pmin'].dtype == arrays['pmax'].dtype == arrays['net'].dtype == arrays['nodal'].dtype == '<f8', 'Native float dtype')
    require(all(math.isfinite(x) for k in ('pmin', 'pmax', 'net', 'nodal') for x in arrays[k].values), 'Nonfinite native input')
    names = metadata['unit_names']; ti = [names.index(n) for n in metadata['thermal_unit_names']]
    require([s['uid'] for s in spec] == names, 'Native spec roster')
    violations = []; count = 0
    def fail(hour, unit, rule):
        nonlocal count
        count += 1
        if len(violations) < 20: violations.append(dict(hour=hour, unit=unit, rule=rule))
    for t in range(168):
        tick(); p = point[t * 41:(t + 1) * 41]
        if sum(p, Q(0)) != Q(arrays['net'].values[t]): fail(t, 'ALL', 'aggregate')
        for j in range(41):
            lo, hi = Q(arrays['pmin'].values[t * 41 + j]), Q(arrays['pmax'].values[t * 41 + j])
            if not 0 <= p[j] <= hi: fail(t, j, 'availability')
            if spec[j]['category'] == 'Hydro' and p[j] != lo: fail(t, j, 'hydro_fixed')
        for k, j in enumerate(ti):
            u = point[6888 + t * 24 + k]; y = point[10920 + t * 24 + k]; z = point[14952 + t * 24 + k]
            lo, hi = Q(arrays['pmin'].values[t * 41 + j]), Q(arrays['pmax'].values[t * 41 + j])
            if not (u in (0, 1) and y in (0, 1) and z in (0, 1)): fail(t, j, 'binary'); continue
            if not lo * u <= p[j] <= hi * u: fail(t, j, 'committed_output')
            if not t:
                if y or z: fail(t, j, 'initial_transition')
                continue
            previous = point[6888 + (t - 1) * 24 + k]; change = u - previous
            if y != max(change, 0) or z != max(-change, 0): fail(t, j, 'canonical_transition')
            if change:
                length = spec[j]['minimum_up' if change > 0 else 'minimum_down']
                if any(point[6888 + h * 24 + k] != u for h in range(t, min(168, t + length))): fail(t, j, 'residence')
            if u == previous == 1:
                rate = parse_rat(spec[j]['hourly_rational'])
                if abs(p[j] - point[(t - 1) * 41 + j]) > rate: fail(t, j, 'native_on_on_ramp')
    return dict(pass_native=count == 0, tau=0, violations=count, first_violations=violations,
                ramp_conversion='binary64(float(native MW/min) * 60.0), then exact rational',
                network_scope='All original DC rows and native row endpoints checked by full matrix replay; no alternative reassembly',
                free_mature_initial_state=True, horizon_clipped_residence=True)


def read_point(v, path, directory):
    data = v.json_read(path)
    require(data['schema'] == 'exact-fixed-schedule-point-v1', 'Point schema')
    require(data['model_bindings'] == model_bindings(directory), 'Point/model hash mismatch')
    require(data['columns'] == len(data['values']), 'Point column count')
    require([x['column'] for x in data['values']] == list(range(data['columns'])), 'Point indices not canonical')
    return [parse_rat(x['value']) for x in data['values']]


def replay(directory, point_path, schedule_path, gen_path):
    v = kernel(); directory = Path(directory)
    m = v.load_model(directory); point = read_point(v, point_path, directory)
    mask = v.vector(v.read_npz(directory / 'integrality.npz', ('integrality',))['integrality'], ('|u1',), m.cols, 'integrality')
    objective = v.vector(v.read_npz(directory / 'objective.npz', ('objective',))['objective'], ('<f8',), m.cols, 'objective')
    raw = v.vector(v.read_npz(schedule_path, ('vector',))['vector'], ('<f8',), m.cols, 'schedule')
    fixed = {j: Q(raw[j]) for j, f in enumerate(mask) if f}
    report = check_point(v, m, point, mask, fixed, objective)
    metadata = v.json_read(directory / 'model_metadata.json')
    report['native'] = check_native(v, point, directory, metadata, native_spec(gen_path, metadata))
    report['accepted'] = report['pass_strict'] and report['native']['pass_native']
    report['point_sha256'] = sha(point_path)
    report['schedule_sha256'] = sha(schedule_path)
    report['native_generator_sha256'] = sha(gen_path)
    report['optimizer_calls'] = 0
    return report


def main():
    p = argparse.ArgumentParser(); p.add_argument('--model', required=True, type=Path)
    p.add_argument('--point', required=True, type=Path); p.add_argument('--schedule', required=True, type=Path)
    p.add_argument('--native-generators', required=True, type=Path); p.add_argument('--report', required=True, type=Path)
    a = p.parse_args(); require(not a.report.exists(), 'Report already exists')
    result = replay(a.model, a.point, a.schedule, a.native_generators)
    with a.report.open('x', encoding='utf-8') as f: json.dump(result, f, indent=2, allow_nan=False); f.write('\n')
    print(json.dumps({'accepted': result['accepted'], 'optimizer_calls': 0})); return 0 if result['accepted'] else 1


if __name__ == '__main__': raise SystemExit(main())
