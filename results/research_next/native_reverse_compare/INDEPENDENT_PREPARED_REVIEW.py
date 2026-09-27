"""Independent byte/closure gate only; never parse native scientific payloads."""
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

ARM = Path(__file__).resolve().parent
ROOT = ARM.parents[2]
PRE = ARM / 'prepared'
EXPORT = ROOT / 'results/research_next/native_reverse_export'
SOURCE = ROOT / 'src/researchnext_native_reverse_compare.py'
PROTOCOL = ROOT / 'docs/research_next/NATIVE_REVERSE_COMPARE_PROTOCOL.md'
PINS = {
    PRE / 'manifest.json': 'b594e558f7587a1667407d48d39d0bc9f4c7a6804620121e438908d804eb4fc4',
    SOURCE: 'd119ee515815281bf95bd3f669b0bc5a657ed8be90161fe2fd6de6489cfa1e82',
    PROTOCOL: '36535647b0e62db57f526f1c6d5ebcb2e04c2df5a22650a6046a2341344d95d4',
    PRE / 'official_completion.json': '71a3b644ba77340c006f43c4b564155f144032ef46f328c100b0c35b231ac03b',
    PRE / 'launcher_completion.json': 'd52d7b7488d8f3978d3e0278e7f4a142b82cf3354618d5384dd5e551b1942977',
    PRE / 'export_freeze.json': '631ca0a7fa07abcd258dd905bc8017d88705bbfc708033157d5ac3e25cd2e675',
    PRE / 'raw.json': '8cd0adfe027727c1d0599a1a291c8e0b289995bc1749b72f13dfe6795289e6d6',
    PRE / 'parsed.json': '455814d618b3a84fe7d4bd4e2027155f8917d5a9dd57721b76ece2e472bfc227',
    PRE / 'helper.py': 'e9f1065fbd47e9d5b7a67afad92fc6a18816cade310b87c8f1c66a49814c389f',
    PRE / 'model.json': 'a8bb82c4397957c6bdf4264d4265fca7144a09282b819aa15880ab60e22db4bb',
    PRE / 'normal.json': 'be57cd1fd925fb5c106b8e90979dcc866c0b27068b368ec018e4068d03067df8',
}


def require(ok, label):
    if not ok:
        raise ValueError(label)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def descriptor(path):
    path = Path(path)
    data = path.read_bytes()
    return {'path': str(path), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def main():
    start = time.perf_counter()
    report_path = ARM / 'INDEPENDENT_PREPARED_REVIEW.json'
    require(not report_path.exists() and not (ARM / 'run01').exists(), 'Single pre-execution review')
    for path, pin in PINS.items():
        require(sha(path) == pin, 'External source/payload pin ' + str(path))
    manifest = read(PRE / 'manifest.json')
    require(manifest['source_sha256'] == PINS[SOURCE] and manifest['protocol_sha256'] == PINS[PROTOCOL], 'Frozen implementation')
    require(manifest['comparison_runs'] == manifest['native_builds'] == manifest['optimizer_calls'] == 0, 'Preparation only')
    inputs = {e['path']: e for e in manifest['inputs']}
    require(len(inputs) == len(manifest['inputs']), 'Unique originals')
    all_entries = manifest['inputs'] + list(manifest['copies'].values())
    for entry in all_entries:
        require(descriptor(entry['path']) == entry, 'Initial full byte/size binding')
    old = ROOT / 'results/research_next/orlib_preflight/solver_prepared01/inputs'
    originals = {
        'official_completion': EXPORT / 'run01/completion.json',
        'launcher_completion': EXPORT / 'launcher01/completion.json',
        'export_freeze': EXPORT / 'prepared/prepared.json',
        'transport': EXPORT / 'prepared/transport.json',
        'derived_plain': EXPORT / 'prepared/target_case.json',
        'raw': EXPORT / 'run01/official_raw_model.json',
        'parsed': EXPORT / 'run01/official_parsed_instance.json',
        'helper': ROOT / 'src/researchnext_orlib_native_compare_schema2.py',
        'model': old / 'reverse_4_19__native_penalized.json',
        'normal': old / 'normalized_case.json',
        'identity_comparison_review': ROOT / 'results/research_next/orlib_native_compare_schema2/INDEPENDENT_POSTRUN_REVIEW.json',
        'export_prepared_review': EXPORT / 'ROOT_PREPARED_REVIEW.json',
    }
    require(set(originals) == set(manifest['copies']) and len(originals) == 12, 'Exact copy roster')
    for name, original in originals.items():
        copied = Path(manifest['copies'][name]['path'])
        require(copied.parent == PRE and copied.read_bytes() == original.read_bytes(), 'Exact original/copy equality ' + name)
        require(inputs[str(original.resolve())] == descriptor(original), 'Original included in closure')
    freeze = read(PRE / 'export_freeze.json')
    native = read(PRE / 'official_completion.json')
    outer = read(PRE / 'launcher_completion.json')
    prepared_review = read(PRE / 'export_prepared_review.json')
    require(len(freeze['bindings']) == 445, 'All 445 export preparation bindings')
    for entry in freeze['bindings']:
        require(inputs[entry['path']]['sha256'] == entry['sha256'], 'Full inherited source/environment closure')
    for record in (native, outer):
        require(record['status'] == 'OFFICIAL_RAW_EXPORT_COMPLETE_PENDING_COMPARISON', 'Successful closure')
        require(record['case'] == 'reverse_4_19__native_penalized', 'Fixed target')
        require(record['native_read_attempts'] == record['native_build_attempts'] == 1 and record['optimizer_calls'] == 0, 'One export, zero optimizer')
        require(record['inputs_unchanged'] is True and record['derived_case_sha256'] == freeze['derived_case_sha256'], 'Derived case and immutability')
    require(outer['prepared_sha256'] == PINS[PRE / 'export_freeze.json'], 'Actual launcher prepared link')
    require(outer['julia_exit_code'] == 0 and outer['Julia_invocations'] == 1 and not outer['stream_errors'], 'Complete process/log drain')
    require(outer['owned_parent_alive'] is False and outer['automatic_retry'] is False, 'Owned process closed, no retry')
    require(outer['optimizer_calls'] == outer['Pkg_resolution_calls'] == outer['network_calls_requested'] == 0, 'No optimizer/new resolution/network requested')
    require(0 <= outer['elapsed_seconds'] <= 600 and 0 <= outer['native_subphase_elapsed_seconds'] <= 120, 'Both declared timing gates')
    require(outer['overall_overrun_seconds'] == 0 and outer['native_subphase_monitor_overrun_seconds'] == 0, 'No admitted overrun')
    require(not (EXPORT / 'run01/failure.json').exists(), 'No conflicting export failure')
    require(native['raw_model_sha256'] == PINS[PRE / 'raw.json'] and native['parsed_instance_sha256'] == PINS[PRE / 'parsed.json'], 'Official payload relation')
    require(prepared_review['status'] == 'PASS_INDEPENDENT_SOURCE_AND_PREPARED_REVIEW' and prepared_review['prepared_sha256'] == PINS[PRE / 'export_freeze.json'], 'Prior independent transport gate')
    require(prepared_review['input_bindings'] == 445 and prepared_review['all_unchanged'] is True, 'Prior gate scope')
    # Native input map is read only as provenance: no raw/parsed/model JSON is loaded.
    for path, pin in native['input_sha256'].items():
        require(path in inputs and inputs[path]['sha256'] == pin, 'Native input map covered by current frozen closure')
    for entry in outer['artifacts']:
        require(descriptor(entry['path']) == entry, 'Public outer-artifact closure')
    fixture = read(ARM / 'synthetic_controls.json')
    require(fixture['status'] == 'PASS' and fixture['checks'] == 4 and fixture['source_sha256'] == PINS[SOURCE] and fixture['protocol_sha256'] == PINS[PROTOCOL], 'Original wrapper fixture provenance')
    require(fixture['historical_helper_fixtures_not_rerun'] is True and fixture['scientific_inputs_read'] == fixture['optimizer_calls'] == 0, 'Fixture scope')
    for entry in all_entries:
        require(descriptor(entry['path']) == entry, 'Closing full byte binding')
    for path, pin in PINS.items():
        require(sha(path) == pin, 'Closing external pin')
    require(not (ARM / 'run01').exists(), 'Comparator not run during gate')
    report = {'status': 'PASS', 'utc': datetime.now(timezone.utc).isoformat(), 'reviewer_sha256': sha(__file__),
              'elapsed_seconds': time.perf_counter() - start, 'manifest_sha256': PINS[PRE / 'manifest.json'],
              'source_sha256': PINS[SOURCE], 'protocol_sha256': PINS[PROTOCOL],
              'original_bindings': len(inputs), 'copies': 12, 'inherited_export_bindings': 445,
              'native_input_map_entries': len(native['input_sha256']), 'public_export_artifacts_checked': len(outer['artifacts']),
              'copy_bytes_equal': True, 'all_inputs_unchanged': True, 'run_absent_before_after': True,
              'export_elapsed_seconds': outer['elapsed_seconds'], 'native_subphase_seconds': outer['native_subphase_elapsed_seconds'],
              'source_only_comparator_review': '9d5aa298fd2bf43aee3578a726771332db8593dacdeffbc2981d44e856c9cd9a',
              'scientific_payloads_parsed': 0, 'scientific_comparison_calls': 0, 'producer_imports': 0,
              'Julia_calls': 0, 'optimizer_calls': 0, 'private_logs_read': False,
              'nominal_target_equivalence': 'NOT_YET_TESTED', 'expanded_target_equivalence': 'NOT_ESTABLISHED'}
    with report_path.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'status': 'PASS', 'report_sha256': sha(report_path), 'bindings': len(inputs), 'elapsed_seconds': report['elapsed_seconds']}))


if __name__ == '__main__':
    main()
