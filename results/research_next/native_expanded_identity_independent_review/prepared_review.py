"""Independent provenance-only gate; no producer imports or scientific arithmetic."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, time

ROOT = Path(__file__).resolve().parents[3]
ARM = ROOT / 'results/research_next/native_expanded_identity'
PRE = ARM / 'prepared'
OUT = Path(__file__).with_suffix('.json')
EXPECTED = {
    'prepared_freeze.json': '08429d3134097ba8d8a308559e2dc250c207dca4938af3c2754bb9acdfb6f185',
    'manifest.json': '218037265ef5c242f60ee35e54b018e5d7d2bbc58dad0644dd55dd54398538b9',
}
SOURCE = 'fca0051ebb46cd8128a141e868877b2206bc3b8962b4b83fac43bbea9095129d'
PROTOCOL = '1d5c1f0d5d8ca6282fd185f5c28d7388fa2bcb6f3ba727f3754728697f71a69e'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def check(ok, message):
    if not ok:
        raise AssertionError(message)

def verify(entry):
    path = Path(entry['path'])
    payload = path.read_bytes()
    check(len(payload) == entry['bytes'] and digest(payload) == entry['sha256'], str(path))
    return payload

def main():
    started = time.perf_counter()
    check(not OUT.exists(), 'Fresh reviewer output')
    check(not (ARM / 'run01').exists(), 'Scientific run must remain absent at this gate')
    for name, expected in EXPECTED.items():
        check(digest((PRE / name).read_bytes()) == expected, 'External transport hash ' + name)
    freeze, manifest = read(PRE / 'prepared_freeze.json'), read(PRE / 'manifest.json')
    check(freeze['manifest_sha256'] == EXPECTED['manifest.json'], 'Manifest bridge')
    check(freeze['source_sha256'] == manifest['source_sha256'] == SOURCE, 'Source freeze')
    check(freeze['protocol_sha256'] == manifest['protocol_sha256'] == PROTOCOL, 'Protocol freeze')
    check(freeze['input_count'] == len(manifest['inputs']) == 37, '37 original bindings')
    check(freeze['copy_count'] == len(manifest['copies']) == 23, '23 copied payloads')
    check(freeze['case_count'] == 1 and manifest['case'] == 'identity__native_penalized', 'Fixed identity only')
    check(freeze['scientific_arithmetic_runs'] == freeze['optimizer_calls'] == 0, 'Preparation scope')
    originals = {str(Path(e['path']).resolve()): (e, verify(e)) for e in manifest['inputs']}
    check(len(originals) == 37, 'Unique originals')
    copies = {role: verify(e) for role, e in manifest['copies'].items()}
    for role, payload in copies.items():
        check(any(payload == data for _, data in originals.values()), 'Original byte bridge ' + role)
    compare = ROOT / 'results/research_next/orlib_native_compare_schema2'
    old = ROOT / 'results/research_next/orlib_preflight/solver_prepared01'
    case = old / 'outputs/identity__native_penalized'
    roles = {
        'candidate': case / 'mip/candidate_vector.json',
        'raw_lp': case / 'lp/raw_solution.npz',
        'signed_bound': case / 'lp/signed_dual_bound.json',
        'mip_result': case / 'mip/result.json',
        'mip_checks': case / 'mip/exact_candidate_checks.json',
        'lp_result': case / 'lp/result.json',
    }
    historical = json.loads(copies['old_output_manifest'])
    lookup = {e['path']: e for e in historical['files']}
    for role, path in roles.items():
        entry = lookup[path.relative_to(old).as_posix()]
        check(path.read_bytes() == copies[role], 'Named old-output bridge ' + role)
        check(len(copies[role]) == entry['bytes'] and digest(copies[role]) == entry['sha256'], 'Old output membership ' + role)
    for role in ('raw', 'parsed', 'normal', 'model'):
        check(copies[role] == (compare / 'prepared' / (role + '.json')).read_bytes(), 'Comparison copy ' + role)
    check(copies['model'] == (old / 'inputs/identity__native_penalized.json').read_bytes(), 'Closed solver/native identity model bridge')
    historical_comparison = json.loads(copies['comparison_manifest'])
    for entry in historical_comparison['inputs'] + historical_comparison['copies']:
        check(str(Path(entry['path']).resolve()) in originals, 'Comparison provenance included')
        verify(entry)
    review = json.loads(copies['comparison_review'])
    check(review['status'] == 'PASS_INDEPENDENT_EXACT_NOMINAL_PROJECTION_EQUIVALENCE', 'Closed nominal comparison')
    comparison = json.loads(copies['comparison'])
    check(comparison['nominal_projection_equivalence'] and comparison['row_multisets_exact'], 'Nominal proof premises')
    check(comparison['expanded_native_equivalence'] == 'NOT_ESTABLISHED', 'Expanded equality remains unclaimed')
    check(comparison['native_binary_count'] == 960 and comparison['native_affine_rows'] == 4384, 'Closed model dimensions')
    controls = read(ARM / 'synthetic_controls.json')
    check(controls['status'] == 'PASS' and controls['checks'] == 8, 'Saved invented controls')
    check(controls['source_sha256'] == SOURCE and controls['protocol_sha256'] == PROTOCOL, 'Controls source binding')
    for entry in manifest['inputs']:
        verify(entry)
    for entry in manifest['copies'].values():
        verify(entry)
    for name, expected in EXPECTED.items():
        check(digest((PRE / name).read_bytes()) == expected, 'Unchanged transport ' + name)
    check(not (ARM / 'run01').exists(), 'Scientific run remains absent')
    result = dict(status='PASS_INDEPENDENT_SOURCE_BINDINGS_AND_PREPARED_PROVENANCE',
        utc=datetime.now(timezone.utc).isoformat(), elapsed_seconds=time.perf_counter() - started,
        reviewer_sha256=digest(Path(__file__).read_bytes()), source_sha256=SOURCE,
        protocol_sha256=PROTOCOL, trusted_transports=EXPECTED, original_bindings=37,
        copied_payloads=23, historical_output_roles=6, exact_identity_model_bridge=True,
        preserved_source_bytes=True, scientific_run_absent=True, producer_imports=0,
        scientific_point_replays=0, scientific_bound_evaluations=0, optimizer_calls=0,
        scope='Byte/provenance gate only; theory/source are separately read, no scientific arithmetic admission yet')
    with OUT.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps(result))

if __name__ == '__main__':
    main()
