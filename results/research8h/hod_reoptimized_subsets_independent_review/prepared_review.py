"""Independent fixed subset/archive gate; no producer imports or optimizers."""
import csv
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
from collections import Counter
from fractions import Fraction

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'results/research8h/hod_reoptimized_subsets'
HERE = Path(__file__).resolve().parent
HOD = ROOT / 'results/research8h/hour_of_day'
OLD = ROOT / 'results/research8h/hod_fixed_ray_transfer'
KERNEL = ROOT / 'src/research8h_standalone_verify.py'
KERNEL_SHA = '708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'
SOURCE_SHA = '3c9d03015a23a277c0f4642be696843d17f2540bac2a2116247e11e0d80f8041'
PROTOCOL_SHA = 'eafa85dba6f772668a263f19f37eac086915cb1d6d599fabdc91ebac097ff0d2'
TAU = Fraction.from_float(1e-5)
MASK = (0,) * 6888 + (1,) * 12096 + (0,) * 4032
TEMP = {'transition', 'exclusive_transition', 'minimum_up', 'minimum_down'}
DWELL = {'minimum_up', 'minimum_down'}
STATIC = {'aggregate_balance', 'thermal_upper', 'thermal_lower', 'nodal_balance', 'branch_flow', 'fossil_energy_cap'}
RULES = ('two_cc', 'locality48')
CASES = ('seed_26093200', 'seed_26093201')
FILES = ('matrix.npz', 'bounds.npz', 'integrality.npz', 'model_metadata.json', 'row_metadata.csv.gz', 'retained_parent_rows.npz')


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))


def manifest(p, digest):
    assert sha(p) == digest
    if p.suffix == '.json':
        rows = read(p)
    else:
        with p.open(encoding='utf-8-sig', newline='') as stream: rows = list(csv.DictReader(stream))
    assert rows and len({r['path'] for r in rows}) == len(rows)
    for r in rows:
        target = Path(r['path'])
        assert target.is_file() and target.stat().st_size == int(r['bytes']) and sha(target) == r['sha256']
    return rows


def labels(d):
    with gzip.open(d / 'row_metadata.csv.gz', 'rt', newline='') as stream:
        return list(csv.DictReader(stream))


def rows_for_rule(model, lab, rule):
    assert len(lab) == model.rows and {x['family'] for x in lab} == STATIC | TEMP
    kept = []
    for r, label in enumerate(lab):
        assert int(label['row']) == r
        family = label['family']
        if rule == 'two_cc':
            if family in TEMP and label['uid'] not in {'107_CC_1', '118_CC_1'}: continue
        elif rule == 'locality48':
            if family in DWELL:
                supported_hours = []
                for e in range(model.indptr[r], model.indptr[r + 1]):
                    if model.data[e] == 0: continue
                    j = model.indices[e]
                    assert 6888 <= j < 18984
                    supported_hours.append(((j - 6888) % 4032) // 24)
                assert supported_hours
                if any(t < 60 or t > 107 for t in supported_hours): continue
        else: raise AssertionError('Unexpected rule')
        kept.append(r)
    assert len(kept) == (19985 if rule == 'two_cc' else 28689)
    kept_set = set(kept)
    assert all(r in kept_set for r, x in enumerate(lab) if x['family'] in STATIC)
    return tuple(kept)


def main():
    assert not (OUT / 'execution_started.json').exists()
    freeze = read(OUT / 'prepared_freeze.json')
    schedule = [case + '__' + rule for case in CASES for rule in RULES]
    assert freeze['schedule'] == schedule and freeze['optimizer_calls'] == 0
    assert (freeze['maximum_LP_calls'], freeze['LP_seconds'], freeze['phase_seconds'], freeze['actual_call_guard_seconds']) == (4, 30., 300., 35.)
    assert freeze['last_start_deadline'] == '2026-09-27T04:00:00+00:00'
    assert sha(ROOT / 'src/research8h_hod_reoptimized_subsets.py') == freeze['source_sha256'] == SOURCE_SHA
    assert sha(ROOT / 'docs/research8h/HOD_REOPTIMIZED_SUBSET_PROTOCOL.md') == freeze['protocol_sha256'] == PROTOCOL_SHA
    before = manifest(OUT / 'input_manifest.json', freeze['manifest_sha256'])
    old_rows = manifest(OLD / 'input_manifest.json', '3753fdcd4bb9d4f04c45f538631f019e54ff17d5c834266d0807a1353b89366a')
    hod_rows = manifest(HOD / 'input_manifest.csv', '078082667f83322d3540ad3ac215ebcc996d0d31b04fd52bfa75c1d2fd814fcc')
    assert sha(KERNEL) == KERNEL_SHA
    spec = importlib.util.spec_from_file_location('independent_subset_npz_kernel', KERNEL)
    v = importlib.util.module_from_spec(spec); sys.modules[spec.name] = v; spec.loader.exec_module(v)
    def array(d, filename, key): return v.read_npz(d / filename, (key,))[key].values
    summaries = []
    for case in CASES:
        parent = HOD / case; full = v.load_model(parent); lab = labels(parent); meta = read(parent / 'model_metadata.json')
        assert (full.rows, full.cols) == (34681, 23016)
        assert array(parent, 'integrality.npz', 'integrality') == MASK
        assert meta['offsets'] == dict(P=0, U=6888, Y=10920, Z=14952, theta=18984)
        for rule in RULES:
            d = OUT / (case + '__' + rule); old = OLD / 'models' / case / rule
            assert all(sha(d / name) == sha(old / name) for name in FILES)
            reduced = v.load_model(d); reduced_labels = labels(d); keep = rows_for_rule(full, lab, rule)
            assert array(d, 'retained_parent_rows.npz', 'rows') == keep
            assert array(d, 'integrality.npz', 'integrality') == MASK
            assert reduced.lower == full.lower and reduced.upper == full.upper and reduced.cols == full.cols
            assert reduced.rows == len(keep) == len(reduced_labels)
            for i, r in enumerate(keep):
                assert reduced.row_lower[i] == full.row_lower[r] and reduced.row_upper[i] == full.row_upper[r]
                lo, hi = reduced.indptr[i:i + 2]; flo, fhi = full.indptr[r:r + 2]
                assert reduced.indices[lo:hi] == full.indices[flo:fhi] and reduced.data[lo:hi] == full.data[flo:fhi]
                assert int(reduced_labels[i]['row']) == i and int(reduced_labels[i]['original_row']) == r
                assert all(reduced_labels[i][key] == lab[r][key] for key in ('family', 'hour_0based', 'uid'))
            rmeta = read(d / 'model_metadata.json')
            for key in ('unit_names', 'thermal_unit_names', 'bus_ids', 'offsets', 'hours', 'units', 'thermal_units', 'buses', 'column_order', 'fossil_units'):
                assert rmeta[key] == meta[key]
            counts = dict(Counter(x['family'] for x in reduced_labels))
            if rule == 'locality48': assert counts['minimum_up'] == 1023 and counts['minimum_down'] == 1001
            caps = [i for i, x in enumerate(reduced_labels) if x['family'] == 'fossil_energy_cap']; assert len(caps) == 1
            cap = caps[0]; assert reduced.row_lower[cap] == -math.inf and reduced.row_upper[cap] == 23195.
            fossil = [meta['unit_names'].index(uid) for uid in meta['fossil_units']]
            assert len(fossil) == len(set(fossil)) == 23 and '121_NUCLEAR_1' not in meta['fossil_units']
            row = {reduced.indices[e]: reduced.data[e] for e in range(reduced.indptr[cap], reduced.indptr[cap + 1])}
            assert row == {t * 41 + j: 1. for t in range(168) for j in fossil}
            summaries.append(dict(case=case, rule=rule, rows=len(keep), columns=reduced.cols, identical_old_file_pairs=len(FILES), all_actual_rows_bounds_labels_and_masks_match=True, counts=counts, cap_row=cap, cap_terms=len(row)))
    controls = []
    claims = read(OUT / 'positive_controls.json')['controls']; assert len(claims) == 4
    for case in ('january_identity', 'seed_26100200'):
        parent = HOD / case; model = v.load_model(parent); lab = labels(parent)
        mask = array(parent, 'integrality.npz', 'integrality'); assert mask == MASK
        point = array(parent, 'constructive_vector.npz', 'vector')
        check = v.check_point(model, point, mask, TAU)
        assert check['expanded_pass'] and check['original_binary_coordinates_exact'] and not check['strict_pass']
        for rule in RULES:
            keep = rows_for_rule(model, lab, rule)
            with (OUT / f'control_{case}_{rule}_rows.csv').open(newline='') as stream: mapping = list(csv.DictReader(stream))
            assert [(int(x['subset_row']), int(x['parent_row'])) for x in mapping] == list(enumerate(keep))
            claim = next(x for x in claims if x['case'] == case and x['rule'] == rule)
            assert claim['point_sha256'] == sha(parent / 'constructive_vector.npz') and claim['original_full_model_matrix_sha256'] == sha(parent / 'matrix.npz')
            assert claim['inherited_exact_expanded_binary'] and not claim['strict_positive_claim'] and claim['rows'] == len(keep)
            controls.append(dict(case=case, rule=rule, retained_rows=len(keep), original_full_point=check, exact_subset_membership_follows_from_checked_row_deletion=True))
    assert manifest(OUT / 'input_manifest.json', freeze['manifest_sha256']) == before
    assert not (OUT / 'execution_started.json').exists()
    report = dict(status='INDEPENDENT_PREPARED_SUBSET_GATE_PASS', source_sha256=freeze['source_sha256'], protocol_sha256=freeze['protocol_sha256'], manifest_sha256=freeze['manifest_sha256'], frozen_files=len(before), old_manifest_files=len(old_rows), HOD_manifest_files=len(hod_rows), prepared_models=summaries, positive_control_rule_checks=controls, full_binary_point_replays=2, execution_marker_absent=True, all_frozen_hashes_unchanged=True, producer_imports=False, optimizer_imports=False, optimization_calls=0, independent_source_sha256=sha(Path(__file__)), exact_kernel_sha256=KERNEL_SHA)
    with (HERE / 'prepared_review.json').open('x', encoding='utf-8') as stream: json.dump(report, stream, indent=2); stream.write('\n')
    print(json.dumps({k: report[k] for k in ('status', 'frozen_files', 'manifest_sha256', 'full_binary_point_replays', 'optimization_calls')}), flush=True)


if __name__ == '__main__': main()
