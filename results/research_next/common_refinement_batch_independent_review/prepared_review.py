"""Read-only byte/provenance and symbolic-map admission; no scientific cuts."""
from pathlib import Path
from datetime import datetime, timezone
import ast
import csv
import gzip
import hashlib
import json
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ARM = ROOT / 'results/research_next/common_refinement_batch'
PRE = ARM / 'prepared'
OLD = ROOT / 'results/research_next/common_master_bounded'
PHASE = ROOT / 'results/research_next/common_phase1'
PINS = {
    'src/researchnext_common_refinement_batch.py': 'f7f79ecca154169832c8739d9c17889c5c5993aa460f6d528d6f115c60018371',
    'docs/research_next/COMMON_REFINEMENT_BATCH_PROTOCOL.md': 'bc47f198b8a6f711c80ce315418749ef4b1b2b9b1afea38568901bd8e2fd6e0d',
    'results/research_next/common_refinement_batch/synthetic_tests.json': '98d51d0f4cb3c0a8ab6dd2eec44ffba39f745271ea63c78a5aabb0d5ad87c9ab',
    'results/research_next/common_refinement_batch/prepared/prepared_freeze.json': '7642265df13848db01ad0627381c6e294ddea30569a5dbc2b344e2e952372b85',
    'results/research_next/common_refinement_batch/prepared/input_manifest.json': '34311c0d425e453a24781079a007eef2369bb8cbf2e3e75eab13f523498916ef',
    'src/researchnext_cut_encoding.py': '286620b092dcf6088f7973c5b3e4569f598d125a20562abe52989e9aaf8af22d',
    'results/research_next/common_master_bounded/INDEPENDENT_POSTRUN_REVIEW.json': 'd5b2c4baac6605ef98f6cc025757c5f36c372166931ba7afe870d5509fdc9ad2',
    'results/research_next/common_phase1_independent_review/postrun_review.json': '8d16937fb7493b314d439dad48123c6c12dd94c69062b346d9bf8da56858e526',
}
THERMAL = (
    '101_CT_1', '101_CT_2', '101_STEAM_3', '101_STEAM_4',
    '102_CT_1', '102_CT_2', '102_STEAM_3', '102_STEAM_4',
    '113_CT_1', '113_CT_2', '113_CT_3', '113_CT_4',
    '115_STEAM_1', '115_STEAM_3', '116_STEAM_1', '118_CC_1',
    '123_STEAM_2', '123_STEAM_3', '123_CT_1', '123_CT_4', '123_CT_5',
)


def demand(ok, why):
    if not ok:
        raise ValueError(why)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))


def key(p):
    return str(Path(p).resolve()).casefold()


def record(p):
    p = Path(p).resolve()
    data = p.read_bytes()
    return {'path': str(p), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def check_items(items):
    demand(len({key(x['path']) for x in items}) == len(items), 'Unique input paths')
    for x in items:
        demand(record(x['path']) == x, 'File binding mismatch: ' + x['path'])


def main():
    started = time.perf_counter()
    demand(not (OUT / 'prepared_review.json').exists(), 'One new review receipt')
    demand(not (ARM / 'run01').exists(), 'Scientific run absent at entry')
    before = {p: sha(ROOT / p) for p in PINS}
    demand(before == PINS, 'Externally pinned source/freeze/review identities')
    freeze = read(PRE / 'prepared_freeze.json')
    manifest = read(PRE / 'input_manifest.json')['files']
    demand(len(manifest) == 355 == freeze['bindings'], '355 frozen bindings')
    check_items(manifest)
    indexed = {key(x['path']): x for x in manifest}
    demand(freeze['manifest_sha256'] == PINS['results/research_next/common_refinement_batch/prepared/input_manifest.json'], 'Freeze manifest link')
    demand(freeze['source_sha256'] == PINS['src/researchnext_common_refinement_batch.py'], 'Freeze source link')
    demand(freeze['protocol_sha256'] == PINS['docs/research_next/COMMON_REFINEMENT_BATCH_PROTOCOL.md'], 'Freeze protocol link')
    demand(freeze['copies'] == 32 and freeze['symbolic_seed_cases'] == 336, 'Frozen scope')
    demand(all(freeze[x] == 0 for x in ('optimizer_calls', 'scientific_cut_evaluations', 'backend_imports')), 'Preparation-only ledger')
    demand(freeze['separate_execution_GO_required'] is True, 'Separate authority')

    # Parse declarations without importing or executing the producer or any helper.
    tree = ast.parse((ROOT / 'src/researchnext_common_refinement_batch.py').read_text(encoding='utf-8-sig'))
    declarations = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in ('PINS', 'HELPERS'):
                declarations[name] = ast.literal_eval(node.value)
    demand(set(declarations) == {'PINS', 'HELPERS'}, 'Actual source pin declarations')
    for rel, digest in list(declarations['PINS'].items()) + list(declarations['HELPERS'].values()):
        demand(indexed[key(ROOT / rel)]['sha256'] == digest, 'Pin included exactly in frozen manifest: ' + rel)
    inherited_counts = {}
    for folder, count in ((OLD / 'prepared', 239), (PHASE / 'prepared', 292)):
        old = read(folder / 'input_manifest.json')['files']
        demand(len(old) == count, 'Historical manifest denominator')
        for x in old:
            demand(indexed.get(key(x['path'])) == x, 'Historical input binding retained')
        inherited_counts[folder.parent.name] = count
    with (PHASE / 'producer_output_inventory.csv').open(encoding='utf-8-sig', newline='') as f:
        historical_output = list(csv.DictReader(f))
    demand(len(historical_output) == 12, 'Phase-I complete closed output denominator')
    for x in historical_output:
        p = ROOT / x['path']
        demand(indexed.get(key(p)) == {'path': str(p.resolve()), 'bytes': int(x['bytes']), 'sha256': x['sha256']}, 'Closed phase-I output binding')
    for rel in ('results/research_next/common_master_bounded/INDEPENDENT_POSTRUN_REVIEW.json',
                'results/research_next/common_phase1_independent_review/postrun_review.json'):
        demand(read(ROOT / rel)['status'] == 'PASS_INDEPENDENT_POSTRUN', 'Inherited independent scientific admission')

    worlds = ('identity', 'days_321')
    world_files = ('matrix.npz', 'bounds.npz', 'integrality.npz', 'model_metadata.json',
                   'native_inputs.npz', 'permutation.csv', 'row_metadata.csv.gz', 'native_spec.json')
    joint_files = ('matrix.npz', 'bounds.npz', 'integrality.npz', 'column_maps.json', 'row_origins.json')
    expected_copies = {}
    for world in worlds:
        for name in world_files:
            expected_copies[key(PRE / world / name)] = key(OLD / 'prepared' / world / name)
    for name in joint_files:
        expected_copies[key(PRE / 'joint' / name)] = key(OLD / 'prepared/joint' / name)
    for name in ('master.json.gz', 'premises.json', 'gen.csv', 'identity_cut.json', 'days_321_cut.json'):
        expected_copies[key(PRE / name)] = key(OLD / 'prepared' / name)
    for name in ('phase_model.npz', 'endpoint_map.json.gz', 'column_encoding.json.gz', 'control_raw_solution.npz', 'fixed_schedule.json'):
        destination = 'inherited_fixed_schedule.json' if name == 'fixed_schedule.json' else name
        expected_copies[key(PRE / destination)] = key(PHASE / 'prepared' / name)
    expected_copies[key(PRE / 'anchor_certificate.json.gz')] = key(PHASE / 'run01/exact_candidate.json.gz')
    copies = read(PRE / 'copy_provenance.json')['copies']
    actual_copies = {key(x['copy']['path']): key(x['original']['path']) for x in copies}
    demand(len(copies) == len(actual_copies) == len(expected_copies) == 32 and actual_copies == expected_copies, 'Exact independent copy-role map')
    for x in copies:
        original, copied = x['original'], x['copy']
        demand(indexed[key(original['path'])] == original and indexed[key(copied['path'])] == copied, 'Copy provenance membership')
        demand(original['sha256'] == copied['sha256'] and original['bytes'] == copied['bytes'], 'Inherited payload unchanged')
        demand(Path(original['path']).read_bytes() == Path(copied['path']).read_bytes(), 'Direct byte equality')

    # Symbolic provenance only: no matrix coefficients, endpoints, q, support or margins.
    origins = read(PRE / 'joint/row_origins.json')['origins']
    demand(len(origins) == 69362, 'Original joint row count')
    origin_keys = [tuple(x) for x in origins]
    demand(len(set(origin_keys)) == 69362, 'Unique joint origin pairs')
    demand(set(origin_keys) == {(wi, r) for wi in range(2) for r in range(34681)}, 'Both complete original row ranges')
    reverse = {v: r for r, v in enumerate(origin_keys)}
    seed = read(PRE / 'symbolic_seed_maps.json')
    demand(seed['common_weight'] == ['6004799503160661', '144115188075855872'], 'Exact declared frozen weight, not 1/24')
    demand(seed['no_coefficients_or_endpoints_evaluated'] is True, 'Symbolic-only preparation')
    expected = []
    for wi, world in enumerate(worlds):
        with gzip.open(PRE / world / 'row_metadata.csv.gz', 'rt', encoding='utf-8-sig', newline='') as f:
            labels = list(csv.DictReader(f))
        demand(len(labels) == 34681, 'World metadata row denominator')
        by_key = {}
        for r, label in enumerate(labels):
            demand(int(label['row']) == r, 'Metadata indexed by original row')
            k = (label['family'], int(label['hour_0based']), label['uid'])
            by_key.setdefault(k, []).append(r)
        for hour in range(168):
            specification = [('aggregate_balance', 'ALL', 'lower', 1)]
            specification += [('thermal_upper', uid, 'upper', -1) for uid in THERMAL]
            specification += [('nodal_balance', '107', 'upper', -1), ('branch_flow', '10', 'upper', -1)]
            rows = []
            for family, uid, side, sign in specification:
                matches = by_key.get((family, hour, uid), [])
                demand(len(matches) == 1, 'One original row per prescribed template key')
                r = matches[0]
                rows.append({'family': family, 'uid': uid, 'side': side, 'sign': sign,
                             'original_row': r, 'joint_row': reverse[(wi, r)]})
            demand(len(rows) == len({x['joint_row'] for x in rows}) == 24, '24 unique selected rows')
            expected.append({'world': world, 'world_index': wi, 'hour': hour, 'rows': rows})
    demand(len(expected) == 336 and seed['cases'] == expected, 'All336 symbolic cases including exact order, side and mapping')

    plan = read(PRE / 'plan.json')
    demand(plan['phase_seconds'] == 2400.0 and plan['rounds'] == 8 and plan['maximum_optimizer_calls'] == 24, 'Finite declared study')
    demand(plan['limits'] == {'master': 120.0, 'recourse': 60.0, 'phase1': 60.0, 'transport_only': 0.0} and plan['closure_margin'] == 5.0, 'Fixed limits')
    demand(plan['initial_master_inherited_without_reassembly'] is True and plan['scientific_cut_evaluations'] == 0 and plan['old_witness_replays'] == 0, 'Plan preparation scope')
    runtime = plan['runtime']
    demand(runtime['master'] == {'python': [3, 12, 14], 'packages': {'pyscipopt': '6.2.1', 'numpy': '2.3.5'}}, 'Master environment')
    demand(runtime['redispatch'] == {'python': [3, 12, 14], 'packages': {'numpy': '2.3.5', 'scipy': '1.18.1', 'highspy': '1.12.0'}}, 'LP environment')
    for name in ('master_executable', 'LP_executable'):
        demand(key(runtime[name]) in indexed, 'Frozen interpreter bytes')
    fixtures = read(ARM / 'synthetic_tests.json')
    demand(fixtures['status'] == 'PASS' and len(fixtures['checks']) == 4, 'Four invented fixture groups')
    demand(fixtures['source_sha256'] == freeze['source_sha256'] and fixtures['protocol_sha256'] == freeze['protocol_sha256'], 'Current fixture provenance')
    demand(fixtures['optimizer_calls'] == fixtures['backend_imports'] == fixtures['scientific_inputs_read'] == 0, 'Synthetic receipt scope')
    demand(not fixtures['old_test_suites_repeated'], 'No historical fixture replay')
    check_items(manifest)
    demand({p: sha(ROOT / p) for p in PINS} == before, 'Pinned transport/source unchanged at close')
    demand(not (ARM / 'run01').exists(), 'Scientific run absent at close')
    report = {
        'status': 'PASS_SOURCE_AND_PREPARED_WITH_EXPLICIT_FINAL_TRANSPORT_GATE',
        'utc': datetime.now(timezone.utc).isoformat(),
        'reviewer_sha256': sha(__file__), 'elapsed_seconds': time.perf_counter() - started,
        'pins': PINS, 'input_bindings': 355, 'byte_identical_copies': 32,
        'historical_input_denominators': inherited_counts, 'closed_phase_outputs_bound': 12,
        'joint_row_origins': 69362, 'symbolic_seed_cases': 336, 'selected_symbolic_rows_per_case': 24,
        'symbolic_row_uses': 8064, 'seed_weight': seed['common_weight'],
        'original_model_master_phase_and_masks': 'Identical copied bytes and closed independent admission inherited; no old full mathematics replay.',
        'all_inputs_and_pinned_transport_unchanged': True, 'run_absent_entry_and_close': True,
        'full_source_and_pinned_helper_integration_read': True,
        'reviewer_authored_encoding_helper': True,
        'independence_scope': 'Independent caller/provenance/map review; no claim of independent encoding-helper implementation.',
        'scientific_cut_evaluations': 0, 'control_evaluations': 0, 'optimizer_calls': 0,
        'producer_or_helper_imports': 0, 'old_witness_replays': 0,
        'source_limitations': [
            'Controller closing validate(items) excludes freeze and manifest transport files; parent has required independent final rehash against the exact external GO constants before scientific admission/publication.',
            'Windows Job and authenticated handshake are source-reviewed only. Four invented groups do not exercise operating-system ownership or termination.',
            'A failed pre-GO process assignment may leave an unassigned actual worker awaiting its30-second self-exit; it has no optimizer authority.',
            'Nominal recourse proposal can miss an expanded-model witness; failure is UNKNOWN, not an expanded-model infeasibility proof.',
        ],
        'execution_authorization': 'Not issued by this review; root separate GO required.',
        'final_independent_transport_gate': {
            'prepared_freeze_sha256': PINS['results/research_next/common_refinement_batch/prepared/prepared_freeze.json'],
            'input_manifest_sha256': PINS['results/research_next/common_refinement_batch/prepared/input_manifest.json'],
            'required_before_any_scientific_admission_or_publication': True,
        },
    }
    with (OUT / 'prepared_review.json').open('x', encoding='utf-8') as f:
        json.dump(report, f, indent=2, allow_nan=False)
        f.write('\n')
    print(json.dumps({'status': report['status'], 'elapsed_seconds': report['elapsed_seconds'],
                      'report_sha256': sha(OUT / 'prepared_review.json')}))


if __name__ == '__main__':
    main()
