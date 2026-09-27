"""One independent archived-point/hash/accounting replay; no optimizers."""
import csv
import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'results/research8h/hod_reoptimized_subsets'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))


def main():
    prepared = read(HERE / 'prepared_review.json')
    assert prepared['status'] == 'INDEPENDENT_PREPARED_SUBSET_GATE_PASS'
    assert sha(HERE / 'prepared_review.py') == prepared['independent_source_sha256']
    source = ROOT / 'src/research8h_hod_reoptimized_subsets.py'
    protocol = ROOT / 'docs/research8h/HOD_REOPTIMIZED_SUBSET_PROTOCOL.md'
    assert sha(source) == prepared['source_sha256'] and sha(protocol) == prepared['protocol_sha256']
    assert sha(OUT / 'input_manifest.json') == prepared['manifest_sha256']
    bindings = read(OUT / 'input_manifest.json')
    def frozen():
        for r in bindings:
            p = Path(r['path']); assert p.stat().st_size == r['bytes'] and sha(p) == r['sha256']
    frozen()
    snapshot = {p.relative_to(OUT).as_posix(): sha(p) for p in OUT.rglob('*') if p.is_file()}
    kernel = ROOT / 'src/research8h_standalone_verify.py'
    assert sha(kernel) == prepared['exact_kernel_sha256']
    spec = importlib.util.spec_from_file_location('postrun_exact_subset_kernel', kernel)
    v = importlib.util.module_from_spec(spec); sys.modules[spec.name] = v; spec.loader.exec_module(v)
    outcomes = read(OUT / 'outcomes.json'); completion = read(OUT / 'completion.json')
    expected = [case + '__' + rule for case in ('seed_26093200', 'seed_26093201') for rule in ('two_cc', 'locality48')]
    assert [x['id'] for x in outcomes] == expected
    assert completion['case_rule_denominator'] == 4 and completion['ordinary_target_denominator'] == 2 and completion['positive_control_rule_denominator'] == 4
    cutoff = datetime(2026, 9, 27, 4, tzinfo=timezone.utc)
    results = []
    for identifier, result in zip(expected, outcomes):
        d = OUT / identifier; assert read(d / 'result.json') == result
        assert result['verdict'] == 'VERIFIED_EXPANDED_CONTINUOUS_POINT' and result['optimization_calls'] == 1
        assert result['model_status'] == 'Optimal' and result['solution_value_valid'] and result['original_binary_model_not_solved']
        opts = result['options']
        for k, x in dict(time_limit=30., threads=1, random_seed=0, solver='simplex', presolve='off', log_to_console=False).items(): assert opts[k] == x
        log = (d / 'solver.log').read_text(); assert log.count('Running HiGHS') == 1
        initial = read(d / 'launch_decision.json'); final = result['actual_call_recheck']
        assert initial['admitted'] and final['admitted'] and initial['guard_s'] == final['guard_s'] == 35.
        assert min(final['phase_remaining_s'], final['cutoff_remaining_s']) >= 35.
        assert datetime.fromisoformat(initial['utc']) <= datetime.fromisoformat(final['utc'])
        assert final['utc'] == result['started_utc'] and datetime.fromisoformat(result['ended_utc']) > datetime.fromisoformat(result['started_utc'])
        assert final['cutoff_remaining_s'] == (cutoff - datetime.fromisoformat(final['utc'])).total_seconds()
        model = v.load_model(d); point = v.read_npz(d / 'returned_vector.npz', ('vector',))['vector'].values
        mask = v.read_npz(d / 'integrality.npz', ('integrality',))['integrality'].values
        assert mask == (0,) * 6888 + (1,) * 12096 + (0,) * 4032
        check = v.check_point(model, point, (0,) * model.cols, Fraction.from_float(1e-5))
        assert check == read(d / 'exact_continuous_point.json') and check['expanded_pass']
        nonbinary = sum(bool(flag and x not in (0., 1.)) for flag, x in zip(mask, point))
        assert nonbinary > 0
        assert result['exact_strict_continuous_pass'] == check['strict_pass'] and result['exact_expanded_continuous_pass'] == check['expanded_pass']
        assert not (d / 'dual_certificate.json').exists() and not (d / 'restricted_energy_lower_bound.json').exists()
        assert result['soft_limit_overrun_s'] == max(0., result['elapsed_s'] - 30.)
        results.append(dict(id=identifier, verification=check, original_state_coordinates_not_exactly_binary=nonbinary, zero_integrality_mask_used=True, no_binary_feasibility_claim=True, solver_seconds=result['elapsed_s'], log_has_one_solver_banner=True, guard_checks_pass=True, returned_point_sha256=sha(d / 'returned_vector.npz')))
    assert completion['optimization_calls'] == sum(x['optimization_calls'] for x in outcomes) == 4
    assert completion['actual_solver_seconds'] == sum(x['elapsed_s'] for x in outcomes)
    assert completion['solver_soft_overrun_s'] == sum(x['soft_limit_overrun_s'] for x in outcomes) == 0.
    assert completion['phase_soft_overrun_s'] == max(0., completion['phase_elapsed_s'] - 300.) == 0.
    assert completion['UTC_cutoff_overrun_s'] == max(0., (datetime.fromisoformat(completion['utc']) - cutoff).total_seconds()) == 0.
    assert completion['phase_elapsed_s'] >= completion['actual_solver_seconds']
    frozen(); assert snapshot == {p.relative_to(OUT).as_posix(): sha(p) for p in OUT.rglob('*') if p.is_file()}
    report = dict(status='INDEPENDENT_HOD_SUBSET_POSTRUN_PASS', manifest_sha256=prepared['manifest_sha256'], frozen_files=len(bindings), all_producer_files_unchanged=True, producer_files_checked=len(snapshot), full_denominator=4, continuous_positive_count=4, negative_count=0, unknown_count=0, binary_target_witnesses_established=0, normalized_energy_bounds_established=0, checks=results, solver_calls=4, actual_solver_seconds=completion['actual_solver_seconds'], phase_seconds=completion['phase_elapsed_s'], all_overruns_zero=True, reviewer_optimizer_calls=0, postrun_source_sha256=sha(Path(__file__)), producer_file_hashes=snapshot)
    with (HERE / 'postrun_review.json').open('x', encoding='utf-8') as f: json.dump(report, f, indent=2); f.write('\n')
    print(json.dumps({k: report[k] for k in ('status', 'continuous_positive_count', 'binary_target_witnesses_established', 'actual_solver_seconds', 'reviewer_optimizer_calls')}), flush=True)


if __name__ == '__main__': main()
