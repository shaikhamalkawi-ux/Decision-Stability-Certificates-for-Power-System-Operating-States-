"""Strict UNCAPPED rational points; capped parent checker remains unchanged."""
from __future__ import annotations
import argparse
import csv
import gzip
from fractions import Fraction as Q
import json
import math
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import research8h_rational_witness_check as primal

OLD_CHECKER_SHA = '9cb836d420308a2ffc5b6e50e78cb565a823d5b65d1223c0f53d98910de5680d'
require = primal.require
rat = primal.rat
parse_rat = primal.parse_rat


def check_native(v, point, directory, tick=lambda: None):
    directory = Path(directory); meta = v.json_read(directory / 'model_metadata.json')
    graph = v.json_read(directory / 'graph.json'); spec = v.json_read(directory / 'native_spec.json')
    arrays = v.read_npz(directory / 'native_inputs.npz', ('pmin', 'pmax', 'net', 'rows', 'source_hour', 'nodal'))
    require(len(point) == 29400 and all(type(x) is Q for x in point), 'Variant rational point shape')
    require(arrays['pmin'].shape == arrays['pmax'].shape == (168, 41) and arrays['nodal'].shape == (168, 24), 'Native shapes')
    require(all(math.isfinite(x) for key in ('pmin', 'pmax', 'net', 'nodal') for x in arrays[key].values), 'Nonfinite native data')
    names = meta['unit_names']; ti = [names.index(n) for n in meta['thermal_unit_names']]
    require([s['uid'] for s in spec] == names and len(graph) == 38, 'Native roster or graph')
    bus_index = {int(bus): j for j, bus in enumerate(meta['bus_ids'])}
    violations = 0; first = []; energy = Q(0)
    def fail(t, entity, rule):
        nonlocal violations
        violations += 1
        if len(first) < 20: first.append(dict(hour=t, entity=entity, rule=rule))
    for t in range(168):
        tick(); p = point[t * 41:(t + 1) * 41]; theta = point[18984 + t * 24:18984 + (t + 1) * 24]
        flow = point[23016 + t * 38:23016 + (t + 1) * 38]
        native_load = [Q(x) for x in arrays['nodal'].values[t * 24:(t + 1) * 24]]
        # This new model intentionally uses the exact nodal sum, never the old rounded net value.
        if sum(p, Q(0)) != sum(native_load, Q(0)): fail(t, 'ALL', 'exact_nodal_sum_conservation')
        injection = [Q(0)] * 24
        for j, value in enumerate(p):
            low = Q(arrays['pmin'].values[t * 41 + j]); high = Q(arrays['pmax'].values[t * 41 + j])
            if not 0 <= value <= high: fail(t, j, 'availability')
            if spec[j]['category'] == 'Hydro' and value != low: fail(t, j, 'hydro_fixed')
            injection[bus_index[spec[j]['bus']]] += value
            if names[j] in meta['fossil_units']: energy += value
        for e, line in enumerate(graph):
            u, w = line['positive_bus'], line['negative_bus']; b = parse_rat(line['coefficient'])
            if flow[e] != b * (theta[u] - theta[w]): fail(t, e, 'flow_definition')
            if not parse_rat(line['lower']) <= flow[e] <= parse_rat(line['upper']): fail(t, e, 'flow_limit')
            injection[u] -= flow[e]; injection[w] += flow[e]
        for j, value in enumerate(injection):
            if value != native_load[j]: fail(t, j, 'native_nodal_incidence')
        for k, j in enumerate(ti):
            u = point[6888 + t * 24 + k]; y = point[10920 + t * 24 + k]; z = point[14952 + t * 24 + k]
            if any(x not in (0, 1) for x in (u, y, z)): fail(t, j, 'binary'); continue
            low = Q(arrays['pmin'].values[t * 41 + j]); high = Q(arrays['pmax'].values[t * 41 + j])
            if not low * u <= p[j] <= high * u: fail(t, j, 'committed_output')
            if t == 0:
                if y or z: fail(t, j, 'initial_transition')
                continue
            previous = point[6888 + (t - 1) * 24 + k]; delta = u - previous
            if y != max(delta, 0) or z != max(-delta, 0): fail(t, j, 'canonical_transition')
            if delta:
                length = spec[j]['minimum_up' if delta > 0 else 'minimum_down']
                if any(point[6888 + h * 24 + k] != u for h in range(t, min(168, t + length))): fail(t, j, 'residence')
            if u == previous == 1 and abs(p[j] - point[(t - 1) * 41 + j]) > parse_rat(spec[j]['hourly_rational']):
                fail(t, j, 'on_on_ramp')
    return dict(pass_native=violations == 0, violations=violations, first_violations=first,
        exact_fossil_energy=rat(energy), cap_MWh=None, fossil_cap_absent=True, tau=0,
        aggregate_authority='exact sum of archived native nodal net loads; old rounded net is provenance only',
        ramp_convention='rationalization of binary64(native MW/min * 60.0)', distinct_model_variant=True)


def replay(directory, point_path, schedule_path, tick=lambda: None):
    require(primal.sha(Path(primal.__file__)) == OLD_CHECKER_SHA, 'Old strict checker changed')
    v = primal.kernel(); directory = Path(directory); model = v.load_model(directory)
    with gzip.open(directory / 'row_metadata.csv.gz', 'rt', newline='') as f: labels = list(csv.DictReader(f))
    require(model.rows == 34512 and model.cols == 29400 and len(labels) == model.rows, 'Uncapped full model dimensions')
    require(not any(r['family'] == 'fossil_energy_cap' for r in labels), 'Uncapped checker refuses a cap row')
    require(v.json_read(directory / 'model_metadata.json')['fossil_cap_absent'] is True, 'Explicit uncapped metadata required')
    point = primal.read_point(v, point_path, directory)
    mask = v.vector(v.read_npz(directory / 'integrality.npz', ('integrality',))['integrality'], ('|u1',), model.cols, 'mask')
    objective = v.vector(v.read_npz(directory / 'objective.npz', ('objective',))['objective'], ('<f8',), model.cols, 'objective')
    fixed = {r['column']: parse_rat(r['value']) for r in v.json_read(schedule_path)}
    result = primal.check_point(v, model, point, mask, fixed, objective, tick)
    result['native'] = check_native(v, point, directory, tick)
    result['accepted_strict_uncapped'] = result['pass_strict'] and result['native']['pass_native']
    result['point_sha256'] = primal.sha(point_path)
    result['model_variant'] = 'flow-conserving DC; not equivalent to the old independently rounded angle model'
    result['optimizer_calls'] = 0
    return result


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--model', required=True, type=Path)
    parser.add_argument('--point', required=True, type=Path); parser.add_argument('--schedule', required=True, type=Path)
    parser.add_argument('--report', required=True, type=Path); a = parser.parse_args()
    require(not a.report.exists(), 'Report already exists')
    result = replay(a.model, a.point, a.schedule)
    with a.report.open('x', encoding='utf-8') as f: json.dump(result, f, indent=2, allow_nan=False); f.write('\n')
    print(json.dumps({'accepted_strict_uncapped': result['accepted_strict_uncapped']}))
    return 0 if result['accepted_strict_uncapped'] else 1


if __name__ == '__main__': raise SystemExit(main())
