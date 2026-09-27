"""Independent stdlib admission of the fixed target transport and export freeze."""
from pathlib import Path
from datetime import datetime, timezone
import gzip, hashlib, json, struct, time

ROOT = Path(__file__).resolve().parents[3]
ARM = ROOT/'results/research_next/native_reverse_export'
PRE = ARM/'prepared'
EXPECTED = '631ca0a7fa07abcd258dd905bc8017d88705bbfc708033157d5ac3e25cd2e675'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def need(ok, why):
    if not ok:
        raise ValueError(why)

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False)

def bits(x):
    need(type(x) in (int, float), 'Numeric scalar')
    return struct.pack('>d', float(x)).hex()

def main():
    began = time.perf_counter()
    need(sha(PRE/'prepared.json') == EXPECTED, 'External freeze')
    p = read(PRE/'prepared.json')
    need(p['status'] == 'PREPARED_OFFLINE_EXPORT_NO_JULIA' and len(p['bindings']) == 445, 'Fixed prepared scope')
    bound = {e['path']: e['sha256'] for e in p['bindings']}
    need(len(bound) == 445, 'Unique bindings')
    for path, expected in bound.items():
        need(sha(Path(path)) == expected, 'Entry file hash ' + path)
    for leaf, expected in [
        ('researchnext_native_reverse_launcher.py', 'bbfc95b40199956220554a51b4bcd2fa7ab8134e238abb90b4a1129628db73df'),
        ('researchnext_native_reverse_export.jl', '568b4819c78a73fe368002b663d768b16380c2540e3a1c84182abd54af95dfa4'),
        ('researchnext_native_reverse_transport.py', '1640604de92ba2d9711d116c919c57e8e984229d4e7418687acc1fe278963d26')]:
        need(sha(ROOT/'src'/leaf) == expected, 'Full-source review version')
    need(sha(ROOT/'docs/research_next/NATIVE_REVERSE_EXPORT_PROTOCOL.md') == '05ce332e378544ba8c937c26934045d321a58b6edb671d12f00d12da134fc7ad', 'Reviewed protocol')
    order = [0,1,2,3,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,20,21,22,23]
    original_bytes = gzip.decompress((PRE/'original_case.json.gz').read_bytes())
    target_bytes = gzip.decompress((PRE/'target_case.json.gz').read_bytes())
    need(hashlib.sha256(original_bytes).hexdigest() == '3cfa5d6f0135e732edd7cb08f887cda0c7e56b0b8e766185d05b52e0ee1f3308', 'Original official JSON')
    need(target_bytes == (PRE/'target_case.json').read_bytes(), 'Derived gzip/plain bytes')
    original, target = json.loads(original_bytes), json.loads(target_bytes)
    model, normal, transport = read(PRE/'old_target_model.json'), read(PRE/'normalized_case.json'), read(PRE/'transport.json')
    need(model['order'] == order and model['variant'] == 'native_penalized', 'One stored target')
    need(len(model['columns']) == 2472 and len(model['rows']) == 4384 and sum(c['binary'] for c in model['columns']) == 960, 'Original model roster')
    before_load, before_reserve = original['Buses']['b1']['Load (MW)'], original['Reserves']['r1']['Amount (MW)']
    after_load, after_reserve = target['Buses']['b1']['Load (MW)'], target['Reserves']['r1']['Amount (MW)']
    need(all(len(a) == 24 for a in (before_load, before_reserve, after_load, after_reserve)), 'Four explicit series')
    need(canonical(after_load) == canonical([before_load[i] for i in order]), 'Exact scalar types/values under one load permutation')
    need(canonical(after_reserve) == canonical([before_reserve[i] for i in order]), 'Exact one reserve permutation')
    for obj in (original, target):
        obj['Buses']['b1']['Load (MW)'] = '<allowed load>'
        obj['Reserves']['r1']['Amount (MW)'] = '<allowed reserve>'
    need(canonical(original) == canonical(target), 'All other JSON structure/history/attribution unchanged')
    need('Power balance penalty ($/MW)' not in original['Parameters'] and 'Power balance penalty ($/MW)' not in target['Parameters'], 'Absent default preserved')
    rows = {r['name']: r for r in model['rows']}
    columns = {c['name']: c for c in model['columns']}
    need(len(rows) == 4384 and len(columns) == 2472, 'Unique named model records')
    for t, source in enumerate(order):
        need(bits(after_load[t]) == bits(normal['load'][source]) == bits(rows[f'net_injection:{t}']['lower']) == bits(rows[f'net_injection:{t}']['upper']) == bits(columns[f'C:system:{t}']['upper']), 'Destination load semantic bridge')
        need(bits(after_reserve[t]) == bits(normal['reserve'][source]) == bits(rows[f'reserve:{t}']['lower']), 'Destination reserve semantic bridge')
        need(bits(columns[f'C:system:{t}']['objective']) == bits(normal['penalty'][source]) == bits(1000.0), 'Default penalty coefficient bridge')
    need(transport['status'] == 'TRANSPORT_ONLY_PASS' and transport['order_destination_to_source'] == order, 'Recorded transport scope')
    need(transport['outputs']['target_gzip']['sha256'] == sha(PRE/'target_case.json.gz') == p['derived_case_sha256'] == '0acc7728ebab28731f6f2bbc5a97025db1c4381a1a4016f798e040dd72f073d8', 'Derived input freeze')
    need(sha(PRE/'transport.json') == p['transport_sha256'], 'Transport report hash')
    cmd = p['command']
    need(len(cmd) == 12 and Path(cmd[4]) == ROOT/'src/researchnext_native_reverse_export.jl' and Path(cmd[5]) == PRE/'target_case.json.gz' and Path(cmd[8]) == ARM/'run01' and cmd[11] == p['derived_case_sha256'], 'Bound one-case execution command')
    need(p['overall_seconds'] == 600 and p['read_build_export_seconds'] == 120 and p['transport_calls'] == 1, 'Budget and sole transform')
    need(p['Julia_invocations'] == p['native_read_attempts'] == p['native_build_attempts'] == p['optimizer_calls'] == p['target_model_rebuilds'] == p['candidate_or_dual_permutations'] == 0, 'No scientific execution yet')
    need(p['environment']['JULIA_PKG_OFFLINE'] == 'true' and p['environment']['JULIA_NUM_THREADS'] == p['environment']['OPENBLAS_NUM_THREADS'] == '1', 'Admitted offline thread environment')
    need(not (ARM/'run01').exists() and not (ARM/'launcher01').exists(), 'Native execution absent')
    for path, expected in bound.items():
        need(sha(Path(path)) == expected, 'Closing file hash ' + path)
    need(sha(PRE/'prepared.json') == EXPECTED, 'Freeze unchanged')
    result = {'utc': datetime.now(timezone.utc).isoformat(), 'status': 'PASS_INDEPENDENT_SOURCE_AND_PREPARED_REVIEW',
              'prepared_sha256': EXPECTED, 'input_bindings': 445, 'all_unchanged': True,
              'full_transport_launcher_exporter_source_read_by_parent': True,
              'independent_checks': 'One-permutation exact JSON/scalar preservation, 24-hour old-model endpoint/cost bridge, frozen command/source/runtime bindings',
              'producer_or_native_imports': 0, 'scientific_native_builds': 0, 'optimizer_calls': 0,
              'target_model_correspondence': 'NOT_YET_TESTED', 'separate_root_execution_go_required': True,
              'reviewer_source_sha256': sha(Path(__file__)), 'elapsed_seconds': time.perf_counter()-began}
    with (ARM/'ROOT_PREPARED_REVIEW.json').open('x', encoding='utf-8') as out:
        json.dump(result, out, indent=2); out.write('\n')
    print(json.dumps(result))

if __name__ == '__main__':
    main()
