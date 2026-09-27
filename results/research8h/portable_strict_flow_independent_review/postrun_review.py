"""Compact closed-run audit; no model arrays, imports, or repeated certificate arithmetic."""
from pathlib import Path
import hashlib
import json
import math
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path('C:/Users/gmalkawi/.codex/research-replays/strict-flow-20260927-candidate02')
OUTER = 'aba9185a0b9b2357820f57e7e91387a284038b4431e7addb3b60ab53d7c90773'
COMMIT = '579ecf20452b7838fdc5802744b24f597af5e1c7'
SUMMARY = '6bbe5acbe6afda090dbc9c040fbae781f49ed665ff0ed6a457114cfa8a05589a'

def need(value, message):
    if not value:
        raise ValueError(message)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def js(path):
    return json.loads(path.read_text(encoding='utf-8'))

def main():
    start = time.perf_counter()
    package = OUT / 'package'
    reports = OUT / 'reports'
    names = sorted(p.name for p in reports.iterdir())
    expected = sorted(['provenance.json', 'focused_checks.json', 'control_mapping.json', 'ledgers.json', 'intervals.json', 'summary.json'] +
                      ['capped_january_identity.json', 'capped_seed_26100200.json'] +
                      ['uncapped_' + c + '.json' for c in ('january_identity', 'seed_26093200', 'seed_26093201')] +
                      ['rays_seed_' + c + '.json' for c in ('26093200', '26093201')] +
                      ['lower_' + c + '.json' for c in ('january_identity', 'seed_26093200', 'seed_26093201')])
    need(names == expected and len(names) == 16, 'Report inventory')
    inventory = {n: dict(bytes=(reports / n).stat().st_size, sha256=sha(reports / n)) for n in names}
    data = {n: js(reports / n) for n in names}
    need(inventory['summary.json']['sha256'] == SUMMARY, 'Trusted summary digest')
    launch = js(OUT / 'replay_launch.json')
    process = js(OUT / 'replay_process_result.json')
    freeze = js(OUT / 'prepared_freeze.json')
    prepared = js(Path(__file__).with_name('prepared_review.json'))
    need(sha(OUT / 'prepared_freeze.json') == 'eda4180b19c5a6ab06f9e6ca00c76ca1dc2cd4a6eda285c2027dc11e5c2b17b9', 'Prepared freeze changed')
    need(sha(Path(__file__).with_name('prepared_review.json')) == 'bf7bcc7c92ce80232b6a152ba350ce10344033c0544d5a2c68ce5e7d47e13661', 'Independent prepared review changed')
    need(sha(package / 'FILE_MANIFEST.csv') == OUTER, 'Outer digest changed')
    need(sha(package / 'reproducibility/replay_strict_flow.py') == '52dbe3b74c1709a36ab23b31768a8e1f1c24a1daa00df2abba7b03bd2e96fad7', 'Reviewed wrapper changed')
    need(sha(package / 'docs/research8h/PORTABLE_STRICT_FLOW_REPLAY_PROTOCOL.md') == '7d619dc7c7e7bb76da71dd7ee2496f507875bbd5ed0fb356e50417791e66557a', 'Reviewed protocol changed')
    need(js(package / 'STRICT_FLOW_CANDIDATE.json') == dict(schema='strict-flow-candidate-v1', evidence_commit=COMMIT, scope='strict-flow-capped-and-uncapped-v1'), 'Candidate metadata')
    command = launch['command']
    expected_command = [launch['interpreter'], '-I', '-S', str(package / 'reproducibility/replay_strict_flow.py'), '--package-root', str(package), '--report-dir', str(reports), '--expected-package-manifest-sha256', OUTER, '--package-evidence-commit', COMMIT]
    need(command == expected_command, 'Authenticated launch command')
    need(Path(launch['working_directory']) == OUT and not OUT.is_relative_to(ROOT), 'Relocated working directory')
    need(launch['wrapper_attempt'] == process['wrapper_attempts'] == 1 and launch['report_directory_previously_absent'], 'Attempt count/fresh reports')
    need('no wrapper imported or run' in launch['previous_windowsapps_interpreter_probe'], 'Interpreter probe disclosure')
    need(process['exit_code'] == 0 and process['stderr'] == '', 'Process completion')
    messages = [json.loads(line) for line in process['stdout'].splitlines()]
    need(len(messages) == 16 and len({m['check'] for m in messages}) == 16, 'Complete unique stdout ledger')
    for message in messages:
        need(data[message['check'] + '.json']['status'] == message['status'], 'Stdout/report mismatch')
    s = data['summary.json']
    need(s['status'] == 'PORTABLE_STRICT_FLOW_REPLAY_PASS' and s['scope'] == 'strict-flow-capped-and-uncapped-v1', 'Final scope/status')
    for key, value in dict(strict_points=5, selected_negative_certificates=2, ray_candidates=8, selected_lower_bounds=3, lower_candidates=15, penalty_intervals=2, optimizer_calls=0, network_calls=0, native_reconstruction=False, package_files_unchanged=True, second_machine_claim=False).items():
        need(s[key] == value, 'Summary count/scope: ' + key)
    need(s['package_manifest_sha256'] == OUTER and s['package_evidence_commit'] == COMMIT, 'Summary trusted identity')
    need(s['python'] == launch['python'] and s['platform'] == 'win32' and s['python'].startswith('3.12.14 '), 'Interpreter/platform')
    need(0 < s['elapsed_seconds'] <= process['actual_wall_seconds'] and math.isfinite(process['actual_wall_seconds']), 'Runtime accounting')
    p = data['provenance.json']
    need(p['payloads'] == 4566 and prepared['candidate_files'] == freeze['candidate_files'] == 4567, 'Full package count')
    need(p['unique_bindings'] == 1133 and p['historical_manifests'] == prepared['recursive_manifests'], 'Historical scope matches prepared gate')
    need(p['package_manifest_sha256'] == OUTER and p['package_evidence_commit'] == COMMIT, 'Provenance trust anchors')
    need(data['focused_checks.json'] == dict(status='FOCUSED_STRICT_FLOW_CHECKS_PASS', path_rejections=6, arithmetic_checks=4, old_kernel_tests_repeated=False), 'Focused checks')
    for n in names:
        if n.startswith(('capped_', 'uncapped_')):
            point = data[n]
            need(point['status'] == 'STRICT_BINARY_NATIVE_POINT_PASS' and point['tau'] == 0 and point['columns'] == 29400 and point['binary_coordinates'] == 12096, 'Strict full original-mask point role')
            need(point['rows'] == (34513 if n.startswith('capped_') else 34512), 'Cap-only point row count')
    need(data['capped_january_identity.json']['energy'] == data['capped_seed_26100200.json']['energy'] == data['uncapped_january_identity.json']['energy'], 'Identity/control energy role consistency')
    need(data['control_mapping.json'] == dict(status='STRICT_CONTROL_MAPPING_PASS', changed_hours=14), 'Control mapping')
    for c in ('seed_26093200', 'seed_26093201'):
        ray = data['rays_' + c + '.json']
        need(ray['selected'] == '+1_projected' and [v['candidate'] for v in ray['candidates']] == ['+1_raw', '+1_projected', '-1_raw', '-1_projected'], 'Fixed four-ray denominator')
        need(ray['candidates'][0]['rejected'] and ray['candidates'][2]['rejected'], 'Retained inadmissible candidates')
        selected = ray['candidates'][1]['verification']
        need(selected['status'] == 'CERTIFIED_EXPANDED_INFEASIBLE' and selected['strict_pass'] and selected['expanded_pass'], 'Selected strict/expanded ray result')
        need(ray['candidates'][3]['verification']['status'] == 'VALID_NONSEPARATING_RAY', 'Retained nonseparating candidate')
    for c in ('january_identity', 'seed_26093200', 'seed_26093201'):
        lower = data['lower_' + c + '.json']
        need(lower['selected'] == '+1_projected' and [v['candidate'] for v in lower['candidates']] == ['zero', '+1_raw', '+1_projected', '-1_raw', '-1_projected'], 'Fixed five-bound denominator')
        need([v['valid'] for v in lower['candidates']] == [True, False, True, False, True] and lower['lower'] == lower['candidates'][2]['lower'], 'Objective selected/invalid roles')
    intervals = data['intervals.json']['targets']
    need([x['case'] for x in intervals] == ['seed_26093200', 'seed_26093201'], 'Two penalty cases')
    for item in intervals:
        c = item['case']
        need(item['strictly_positive'] and len(item['penalty']) == len(item['percent']) == 2, 'Finite positive interval record')
        need(item['lower'] == data['lower_' + c + '.json']['lower'] and item['upper'] == data['uncapped_' + c + '.json']['energy'], 'Interval role links')
    need(data['ledgers.json'] == dict(status='FIXED_CALL_AND_HOUR_LEDGER_PASS', historical_solver_calls=8, wrapper_solver_calls=0, energy_target_hours=336, capped_identity_hours=168), 'Historical-versus-replay call ledger')
    for n, descriptor in inventory.items():
        need((reports / n).stat().st_size == descriptor['bytes'] and sha(reports / n) == descriptor['sha256'], 'Closed report changed')
    result = dict(status='INDEPENDENT_COMPACT_POSTRUN_REVIEW_PASS', source_sha256=sha(Path(__file__)), report_inventory=inventory, replay_launch_sha256=sha(OUT / 'replay_launch.json'), replay_process_result_sha256=sha(OUT / 'replay_process_result.json'), summary_sha256=SUMMARY, prepared_review_sha256=sha(Path(__file__).with_name('prepared_review.json')), trusted_outer_sha256=OUTER, evidence_commit=COMMIT, authentic_isolated_no_site_command_checked=True, declared_scope_checked=True, strict_point_roles=5, ray_candidates=8, objective_candidates=15, penalty_intervals=2, wrapper_attempts=1, wrapper_elapsed_s=s['elapsed_seconds'], process_elapsed_s=process['actual_wall_seconds'], package_immutability='Reviewed source compares its full before/after snapshot; reported unchanged, consistent with independently verified 4567-file prepared inventory. This compact review does not repeat a whole-package hash or mathematical replay.', candidate01='Preserved preparation failure before wrapper import; not a mathematical replay attempt.', windowsapps_probe='Failed interpreter discovery before wrapper execution; disclosed separately.', repeated_mathematical_replays=0, model_imports=0, optimizer_calls=0, network_calls=0, native_reconstruction=False, second_machine_claim=False, review_elapsed_s=time.perf_counter()-start)
    with Path(__file__).with_name('postrun_review.json').open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps(result), flush=True)

if __name__ == '__main__':
    main()
