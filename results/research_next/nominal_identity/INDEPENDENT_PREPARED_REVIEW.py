"""Independent byte/AST prepared gate; no candidate arithmetic or producer import."""
import ast
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ARM = Path(__file__).resolve().parent
PRE = ARM / 'prepared'
SOURCE = ROOT / 'src/researchnext_nominal_identity.py'
PROTOCOL = ROOT / 'docs/research_next/NOMINAL_IDENTITY_PROTOCOL.md'
PINS = {
    SOURCE: '24d7a34f26d9427ce9fa95129053496e20084888d32db9ea1c53d3047b33a991',
    PROTOCOL: '6c1e275a0a8a69062bd0fe1fd966adbdedf0bdba894170b82acc1dbdb9f5d4d1',
    PRE / 'freeze.json': '37dbfd382db1a8bf4a7905d2e486a606d9b94245f75d6d3e7c32a57b5df77756',
    PRE / 'manifest.json': 'c8f40dc622a042e27b9a80f8fed02583881e0228445104ccb39eaaaf26933164',
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def check(condition, label):
    if not condition:
        raise ValueError(label)


def binding(entry):
    data = Path(entry['path']).read_bytes()
    check(len(data) == entry['bytes'], 'Bound size: ' + entry['path'])
    check(hashlib.sha256(data).hexdigest() == entry['sha256'], 'Bound SHA: ' + entry['path'])


def main():
    start = time.perf_counter()
    check(not (ARM / 'run01').exists(), 'Scientific run must remain absent')
    for path, expected in PINS.items():
        check(digest(path) == expected, 'Trusted pin: ' + str(path))
    freeze, manifest = read(PRE / 'freeze.json'), read(PRE / 'manifest.json')
    check(freeze['manifest_sha256'] == PINS[PRE / 'manifest.json'], 'Freeze manifest')
    check(freeze['source_sha256'] == manifest['source_sha256'] == PINS[SOURCE], 'Source bindings')
    check(freeze['protocol_sha256'] == manifest['protocol_sha256'] == PINS[PROTOCOL], 'Protocol bindings')
    check(freeze['inputs'] == len(manifest['inputs']) == 69, '69 originals')
    check(freeze['copies'] == len(manifest['copies']) == 11, '11 copies')
    check(freeze['no_scientific_arithmetic'] is True and manifest['candidate_reconstructions'] == manifest['optimizer_calls'] == 0, 'Preparation scope')
    entries = {e['path']: e for e in manifest['inputs']}
    check(len(entries) == 69, 'Unique original paths')
    for e in manifest['inputs'] + list(manifest['copies'].values()):
        binding(e)
    copied_old = read(PRE / 'old_manifest.json')
    inherited = copied_old['inputs'] + list(copied_old['copies'].values())
    check(all(entries.get(e['path']) == e for e in inherited), 'Complete old evidence closure')
    originals = {
        'old_manifest': ROOT / 'results/research_next/native_expanded_identity/prepared/manifest.json',
        'old_result': ROOT / 'results/research_next/native_expanded_identity/run01/result.json',
        'old_review': ROOT / 'results/research_next/native_expanded_identity_independent_review/postrun_review.json',
        'proposal': ROOT / 'docs/research_next/NOMINAL_IDENTITY_RECONSTRUCTION_PROPOSAL.md',
        'theory_review': ROOT / 'docs/research_next/NOMINAL_IDENTITY_RECONSTRUCTION_REVIEW.md',
        'old_semantic_source': ROOT / 'src/researchnext_orlib_uc.py',
    }
    for name in ('raw', 'normal', 'model', 'candidate', 'helper'):
        originals[name] = ROOT / 'results/research_next/native_expanded_identity/prepared' / (name + ('.py' if name == 'helper' else '.json'))
    check(set(originals) == set(manifest['copies']), 'Exact copy roster')
    for name, original in originals.items():
        copied = Path(manifest['copies'][name]['path'])
        check(copied.parent == PRE and copied.read_bytes() == original.read_bytes(), 'Full copy equality ' + name)
        check(str(original.resolve()) in entries, 'Original captured ' + name)
    # Syntax comparison only: no module import, scientific JSON parsing, point evaluation or fixture rerun.
    new_tree = ast.parse(SOURCE.read_text(encoding='utf-8-sig'))
    old_tree = ast.parse((PRE / 'old_semantic_source.py').read_text(encoding='utf-8-sig'))
    new_fn = next(n for n in new_tree.body if isinstance(n, ast.FunctionDef) and n.name == 'semantic_check')
    old_fn = next(n for n in old_tree.body if isinstance(n, ast.FunctionDef) and n.name == 'direct_check')
    old_fn.name = new_fn.name
    check(ast.dump(old_fn, include_attributes=False) == ast.dump(new_fn, include_attributes=False), 'Semantic body exactly inherited apart from function name')
    helper_tree = ast.parse((PRE / 'helper.py').read_text(encoding='utf-8-sig'))
    check(any(isinstance(n, ast.If) and '__name__' in ast.unparse(n.test) for n in helper_tree.body), 'Helper main guarded')
    fixture = read(ARM / 'synthetic_controls.json')
    check(fixture['status'] == 'PASS' and fixture['checks'] == 9, 'Recorded invented fixtures')
    check(fixture['source_sha256'] == PINS[SOURCE] and fixture['protocol_sha256'] == PINS[PROTOCOL], 'Fixture provenance')
    check(fixture['scientific_candidate_reads'] == fixture['optimizer_calls'] == 0, 'Fixture scope')
    for e in manifest['inputs'] + list(manifest['copies'].values()):
        binding(e)
    for path, expected in PINS.items():
        check(digest(path) == expected, 'Closing trusted pin')
    check(not (ARM / 'run01').exists(), 'No scientific run during gate')
    result = {
        'status': 'PASS', 'utc': datetime.now(timezone.utc).isoformat(),
        'elapsed_seconds': time.perf_counter() - start,
        'reviewer_sha256': digest(__file__),
        'source_sha256': PINS[SOURCE], 'protocol_sha256': PINS[PROTOCOL],
        'freeze_sha256': PINS[PRE / 'freeze.json'], 'manifest_sha256': PINS[PRE / 'manifest.json'],
        'original_bindings': 69, 'copies': 11, 'inherited_entries': len(inherited),
        'copy_bytes_equal': True, 'semantic_AST_equal_except_name': True,
        'invented_fixture_groups_recorded': 9, 'run_absent_before_after': True,
        'producer_imports': 0, 'scientific_coordinate_arithmetic': 0,
        'candidate_reconstructions': 0, 'optimizer_calls': 0, 'Julia_calls': 0,
        'scope': 'Byte provenance and source/AST admission only; no candidate, row activity or reconstruction evaluated.'
    }
    out = ARM / 'INDEPENDENT_PREPARED_REVIEW.json'
    with out.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'status': 'PASS', 'report_sha256': digest(out), 'elapsed_seconds': result['elapsed_seconds']}))


if __name__ == '__main__':
    main()
