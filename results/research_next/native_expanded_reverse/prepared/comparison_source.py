"""One exact reverse-target native comparison, reusing the frozen comparator."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, copy, hashlib, importlib.util, json, sys, time

ROOT = Path(__file__).resolve().parents[1]
ARM = ROOT/'results/research_next/native_reverse_compare'
PRE, RUN = ARM/'prepared', ARM/'run01'
EXPORT = ROOT/'results/research_next/native_reverse_export'
PROTOCOL = ROOT/'docs/research_next/NATIVE_REVERSE_COMPARE_PROTOCOL.md'
OLD = ROOT/'results/research_next/orlib_preflight/solver_prepared01/inputs'
HELPER = ROOT/'src/researchnext_orlib_native_compare_schema2.py'
HELPER_SHA = 'e9f1065fbd47e9d5b7a67afad92fc6a18816cade310b87c8f1c66a49814c389f'
PREPARED_EXPORT_SHA = '631ca0a7fa07abcd258dd905bc8017d88705bbfc708033157d5ac3e25cd2e675'
ORDER = [0,1,2,3,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,20,21,22,23]

def need(ok, why):
    if not ok:
        raise ValueError(why)

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def save(p, obj):
    with Path(p).open('x', encoding='utf-8') as stream:
        json.dump(obj, stream, indent=2, allow_nan=False); stream.write('\n')

def binding(p):
    p = Path(p).resolve(); data = p.read_bytes()
    return {'path': str(p), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}

def validate(items):
    for item in items:
        need(binding(item['path']) == item, 'Input changed ' + item['path'])

def utc():
    return datetime.now(timezone.utc).isoformat()

def helper(path):
    need(sha(path) == HELPER_SHA, 'Reviewed unchanged comparator')
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location('reverse_native_nominal_compare_math', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module; spec.loader.exec_module(module)
    return module

def expected_normal(normal, order):
    need(order == ORDER and len(order) == 24 and sorted(order) == list(range(24)), 'Exactly the old frozen target order')
    expected = copy.deepcopy(normal)
    for key in ('load', 'reserve', 'penalty'):
        need(type(normal[key]) is list and len(normal[key]) == 24, 'Complete original series')
        expected[key] = [normal[key][source] for source in order]
    return expected

def prepare(official_sha, launcher_sha):
    need(not PRE.exists() and not RUN.exists(), 'Fresh target preparation')
    need(sha(EXPORT/'prepared/prepared.json') == PREPARED_EXPORT_SHA, 'Approved export freeze')
    official, outer = EXPORT/'run01/completion.json', EXPORT/'launcher01/completion.json'
    need(sha(official) == official_sha and sha(outer) == launcher_sha, 'Externally supplied two completion hashes')
    native_done, launcher_done = read(official), read(outer)
    for item in (native_done, launcher_done):
        need(item['status'] == 'OFFICIAL_RAW_EXPORT_COMPLETE_PENDING_COMPARISON' and item['case'] == 'reverse_4_19__native_penalized', 'Successfully closed fixed target')
        need(item['native_read_attempts'] == item['native_build_attempts'] == 1 and item['optimizer_calls'] == 0 and item['inputs_unchanged'], 'One closed native read/build')
    need(launcher_done['julia_exit_code'] == 0 and launcher_done['Julia_invocations'] == 1 and not launcher_done['stream_errors'], 'Closed native process/logs')
    need(0 <= launcher_done['elapsed_seconds'] <= 600 and 0 <= launcher_done['native_subphase_elapsed_seconds'] <= 120, 'Complete temporal gates')
    need(not (EXPORT/'run01/failure.json').exists(), 'No native failure alongside completion')
    prep = read(EXPORT/'prepared/prepared.json')
    need(native_done['derived_case_sha256'] == launcher_done['derived_case_sha256'] == prep['derived_case_sha256'], 'Derived case relation')
    fixed = {'official_completion': official, 'launcher_completion': outer,
             'export_freeze': EXPORT/'prepared/prepared.json', 'transport': EXPORT/'prepared/transport.json',
             'derived_plain': EXPORT/'prepared/target_case.json', 'raw': EXPORT/'run01/official_raw_model.json',
             'parsed': EXPORT/'run01/official_parsed_instance.json', 'helper': HELPER,
             'model': OLD/'reverse_4_19__native_penalized.json', 'normal': OLD/'normalized_case.json',
             'identity_comparison_review': ROOT/'results/research_next/orlib_native_compare_schema2/INDEPENDENT_POSTRUN_REVIEW.json',
             'export_prepared_review': EXPORT/'ROOT_PREPARED_REVIEW.json'}
    need(sha(fixed['raw']) == native_done['raw_model_sha256'] and sha(fixed['parsed']) == native_done['parsed_instance_sha256'], 'Actual native payload hashes')
    need(sha(fixed['model']) == 'a8bb82c4397957c6bdf4264d4265fca7144a09282b819aa15880ab60e22db4bb' and sha(fixed['normal']) == 'be57cd1fd925fb5c106b8e90979dcc866c0b27068b368ec018e4068d03067df8', 'Original unchanged target/normal')
    need(sha(HELPER) == HELPER_SHA and sha(fixed['identity_comparison_review']) == '50191cce91e6a4e8479500bfa0a1740b03d812848ee37620480b3e41ce584080', 'Inherited comparator lineage')
    originals = {}
    for entry in prep['bindings']:
        path = Path(entry['path']); item = binding(path)
        need(item['sha256'] == entry['sha256'], 'Export transitive input')
        originals[item['path']] = item
    for path in list(fixed.values()) + [Path(__file__), PROTOCOL, ARM/'synthetic_controls.json']:
        item = binding(path)
        need(item['path'] not in originals or item == originals[item['path']], 'Consistent input union')
        originals[item['path']] = item
    captured = {name: path.read_bytes() for name, path in fixed.items()}
    for name, data in captured.items():
        item = originals[str(fixed[name].resolve())]
        need(len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256'], 'Captured exact input bytes')
    PRE.mkdir(parents=True); copies = {}
    for name, data in captured.items():
        out = PRE/(name + fixed[name].suffix); out.write_bytes(data)
        need(out.read_bytes() == data, 'Copied readback'); copies[name] = binding(out)
    validate(list(originals.values()))
    save(PRE/'manifest.json', {'utc': utc(), 'inputs': list(originals.values()), 'copies': copies,
         'source_sha256': sha(__file__), 'protocol_sha256': sha(PROTOCOL), 'comparison_runs': 0, 'native_builds': 0, 'optimizer_calls': 0})
    print(json.dumps({'status': 'PREPARED_ONLY', 'manifest_sha256': sha(PRE/'manifest.json')}))

def run(expected):
    began = time.perf_counter(); need(not RUN.exists() and sha(PRE/'manifest.json') == expected, 'One exact frozen comparison')
    m = read(PRE/'manifest.json'); validate(m['inputs']); validate(list(m['copies'].values()))
    need(sha(__file__) == m['source_sha256'] and sha(PROTOCOL) == m['protocol_sha256'], 'Frozen wrapper/protocol')
    cp = lambda name: Path(m['copies'][name]['path'])
    RUN.mkdir(); save(RUN/'started.json', {'utc': utc(), 'manifest_sha256': expected, 'optimizer_calls': 0, 'native_builds': 0})
    try:
        h = helper(cp('helper'))
        model, normal = read(cp('model')), read(cp('normal'))
        need(model['variant'] == 'native_penalized' and model['horizon'] == 24, 'Fixed model variant/horizon')
        transformed = expected_normal(normal, model['order'])
        save(RUN/'expected_parsed_bridge.json', {'order_destination_to_source': model['order'],
             'only_reordered_fields': ['load', 'reserve', 'penalty'], 'original_normal_sha256': sha(cp('normal')),
             'original_model_sha256': sha(cp('model')), 'actual_target_plain_sha256': sha(cp('derived_plain')),
             'same_numerical_instance_not_whole_file_metadata_equality': True})
        result = h.compare(read(cp('raw')), read(cp('parsed')), model, transformed)
        result.update(case='reverse_4_19__native_penalized', reused_comparator_sha256=HELPER_SHA,
                      native_input_reordered_once=True, target_candidate_or_dual_permuted=False,
                      no_cost_transfer_at_this_stage=True, posthoc_fidelity_extension=True)
        save(RUN/'comparison.json', result)
        validate(m['inputs']); validate(list(m['copies'].values())); need(sha(PRE/'manifest.json') == expected, 'Stable manifest')
        elapsed = time.perf_counter()-began; need(elapsed <= 120, '120-second soft arithmetic phase')
        save(RUN/'completion.json', {'utc': utc(), 'status': 'COMPLETE_PENDING_INDEPENDENT_REVIEW',
             'elapsed_seconds': elapsed, 'all_inputs_unchanged': True, 'optimizer_calls': 0, 'native_builds': 0,
             'final_completion_write_excluded': True})
        print(json.dumps({k: result[k] for k in ('status', 'nominal_projection_equivalence', 'row_multisets_exact', 'objective_exact', 'parsed_exact_agreement')}))
    except BaseException as exc:
        save(RUN/'failure.json', {'utc': utc(), 'error_type': type(exc).__name__, 'message': str(exc),
             'elapsed_seconds': time.perf_counter()-began, 'no_native_equivalence_admitted': True, 'no_retry': True})
        raise

def self_test():
    need(not (ARM/'synthetic_controls.json').exists(), 'One invented wrapper fixture pass')
    original = {'load': [float(i)+0.1 for i in range(24)], 'reserve': [float(i)/10 for i in range(24)],
                'penalty': [1000+i for i in range(24)], 'units': [{'name': 'g', 'age': -2}], 'metadata': 'kept'}
    snapshot = json.dumps(original, sort_keys=True)
    transformed = expected_normal(original, ORDER)
    need(all(transformed[key][t] == original[key][ORDER[t]] for key in ('load', 'reserve', 'penalty') for t in range(24)), 'Single destination/source permutation')
    need(transformed['units'] == original['units'] and transformed['metadata'] == original['metadata'], 'No static change')
    need(json.dumps(original, sort_keys=True) == snapshot and transformed is not original, 'No original mutation')
    try:
        expected_normal(original, list(range(24)))
    except ValueError:
        pass
    else:
        raise ValueError('Unselected order accepted')
    ARM.mkdir(parents=True, exist_ok=True)
    save(ARM/'synthetic_controls.json', {'utc': utc(), 'status': 'PASS', 'checks': 4,
         'source_sha256': sha(__file__), 'protocol_sha256': sha(PROTOCOL), 'reused_helper_sha256': HELPER_SHA,
         'historical_helper_fixtures_not_rerun': True, 'scientific_inputs_read': 0, 'optimizer_calls': 0})
    print('PASS 4 invented target-bridge controls')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('self-test', 'prepare', 'run'))
    parser.add_argument('--official-sha'); parser.add_argument('--launcher-sha'); parser.add_argument('--expected-sha')
    args = parser.parse_args()
    if args.mode == 'self-test':
        self_test()
    elif args.mode == 'prepare':
        need(args.official_sha and args.launcher_sha, 'Two externally admitted completion hashes')
        prepare(args.official_sha, args.launcher_sha)
    else:
        need(args.expected_sha, 'Explicit comparison freeze'); run(args.expected_sha)
