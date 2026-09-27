"""Single solver-free review of the frozen common-diving restriction."""
from pathlib import Path
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
import math
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
ARM = ROOT / 'results/research_next/common_diving'
PRE = ARM / 'prepared'
OLD = ROOT / 'results/research_next/common_commitment'
ORIGINAL = OLD / 'prepared'
TAU = Q.from_float(1e-5)
PINS = {
    'src/researchnext_common_diving.py': 'd5b5fb33c30dbe2ad15bace67ecfa42cb3e4b076769f8ff8a0341827124d30ba',
    'docs/research_next/COMMON_DIVING_PROTOCOL.md': '6b4df1dfa036fbc9a617dc996d66d0dddb52c1c00e2acdd9cdcf528eb767d318',
    'src/research8h_standalone_verify.py': '708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f',
    'src/researchnext_common_commitment.py': '039af59750b4c165d877b9878ac14af02a202700b46739ba96a8914075ae3284',
    'results/research_next/common_diving/prepared/prepared_freeze.json': 'b8a3c14d4e9826b63542a0d84377092c005b81fc9078f6803d923007ff06d3e6',
    'results/research_next/common_diving/prepared/input_manifest.json': '843b0e9087bef847f006b502b9bac3ce4f85475de3772ea5b35db89c834f30b3',
    'results/research_next/common_commitment/prepared/input_manifest.json': '8ff99b1f4450ac15e91b26a261a85c98d574bbbdac3f7fe149efd9fd07204a5c',
    'results/research_next/common_commitment/run01/lp/raw_solution.npz': '90c8b308a6ce8e7671adbe3059887d6ce27489fa3d68aa601c2474b32d2d462a',
    'results/research_next/common_commitment/INDEPENDENT_POSTRUN_REVIEW.json': 'f442edeb3f90c5d602a1b60cdef1b96b4d560ebbe97fae28c4ca21c6077eadba',
}

def digest(data):
    return hashlib.sha256(data).hexdigest()

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def rational_record(item, expected):
    assert set(item) == {'numerator', 'denominator', 'approximate'}
    assert item['numerator'] == str(expected.numerator)
    assert item['denominator'] == str(expected.denominator)
    assert item['approximate'] == float(expected)

def main():
    start = time.perf_counter()
    report = ARM / 'INDEPENDENT_PREPARED_REVIEW.json'
    assert not report.exists() and not (ARM / 'run01').exists()
    for name, expected in PINS.items():
        assert digest((ROOT / name).read_bytes()) == expected, name
    manifest = load(PRE / 'input_manifest.json')['files']
    assert len(manifest) == 66
    entries = {str(Path(e['path']).resolve()).casefold(): e for e in manifest}
    assert len(entries) == len(manifest)
    old_entries = load(ORIGINAL / 'input_manifest.json')['files']
    assert len(old_entries) == 48
    for e in old_entries:
        assert entries[str(Path(e['path']).resolve()).casefold()] == e
    captured = {}
    for e in manifest:
        p = Path(e['path']); b = p.read_bytes()
        assert len(b) == e['bytes'] and digest(b) == e['sha256'], str(p)
        captured[p] = b
    freeze = load(PRE / 'prepared_freeze.json')
    assert freeze['manifest_sha256'] == PINS['results/research_next/common_diving/prepared/input_manifest.json']
    assert freeze['bindings'] == 66 and freeze['optimizer_calls'] == 0
    assert freeze['source_sha256'] == PINS['src/researchnext_common_diving.py']
    assert freeze['protocol_sha256'] == PINS['docs/research_next/COMMON_DIVING_PROTOCOL.md']
    assert {p.name for p in PRE.iterdir() if p.is_file()} == {
        'matrix.npz','integrality.npz','bounds.npz','restriction.json','plan.json',
        'preparation_started.json','input_manifest.json','prepared_freeze.json'}
    assert all(p.is_file() for p in PRE.iterdir())
    helper = ROOT / 'src/research8h_standalone_verify.py'
    spec = importlib.util.spec_from_file_location('diving_prepared_npz_reader', helper)
    v = importlib.util.module_from_spec(spec); sys.modules[spec.name] = v; spec.loader.exec_module(v)
    # Only the pinned stdlib serialization/structural reader is used, not any point/ray checker.
    original = v.load_model(ORIGINAL / 'joint'); restricted = v.load_model(PRE)
    assert (original.rows, original.cols, len(original.data)) == (69362,33936,291176)
    assert (restricted.rows, restricted.cols) == (original.rows, original.cols)
    for name in ('matrix.npz','integrality.npz'):
        assert (PRE / name).read_bytes() == (ORIGINAL / 'joint' / name).read_bytes()
    for field in ('data','indices','indptr'):
        assert getattr(original, field) == getattr(restricted, field)
    for field in ('row_lower','row_upper'):
        assert [x.hex() for x in getattr(original,field)] == [x.hex() for x in getattr(restricted,field)]
    bits = v.vector(v.read_npz(PRE/'integrality.npz',('integrality',))['integrality'],('|u1',),original.cols,'mask')
    assert bits == tuple(int(6888 <= j < 18984) for j in range(original.cols))
    assert sum(bits) == 12096
    raw = v.read_npz(OLD/'run01/lp/raw_solution.npz',('vector','row_value','row_dual','col_dual'))
    point = v.vector(raw['vector'],('<f8',),original.cols,'saved LP vector')
    assert all(math.isfinite(x) for x in point)
    restriction = load(PRE/'restriction.json'); rational_record(restriction['tau'],TAU)
    assert restriction['posthoc'] is True and restriction['no_continuous_column_restrictions'] is True
    assert restriction['lp_point_sha256'] == PINS['results/research_next/common_commitment/run01/lp/raw_solution.npz']
    assert Path(restriction['original_model']).resolve() == (ORIGINAL/'joint').resolve()
    expected_fixed, expected_free, newly_fixed_nonbinary, changed_boxes = [], [], 0, 0
    for j in range(original.cols):
        lo, hi = original.lower[j], original.upper[j]
        target_lo, target_hi = restricted.lower[j], restricted.upper[j]
        if not bits[j]:
            assert (lo.hex(),hi.hex()) == (target_lo.hex(),target_hi.hex())
            continue
        x = Q(point[j]); distance = min(abs(x),abs(x-1))
        near = [b for b in (0,1) if abs(x-b) <= TAU]
        assert len(near) <= 1
        expected = {'column':j,'lp_value_hex':point[j].hex(),
                    'exact_lp_value':{'numerator':str(x.numerator),'denominator':str(x.denominator),'approximate':float(x)},
                    'nearest_bit_distance':{'numerator':str(distance.numerator),'denominator':str(distance.denominator),'approximate':float(distance)}}
        if near:
            bit = near[0]; assert Q(lo) <= bit <= Q(hi)
            assert target_lo == target_hi == bit
            expected_fixed.append({**expected,'fixed_bit':bit})
            newly_fixed_nonbinary += x not in (0,1)
        else:
            assert (lo.hex(),hi.hex()) == (target_lo.hex(),target_hi.hex())
            expected_free.append(expected)
        changed_boxes += (lo.hex(),hi.hex()) != (target_lo.hex(),target_hi.hex())
    assert restriction['fixed'] == expected_fixed and restriction['free'] == expected_free
    assert (len(expected_fixed),len(expected_free),newly_fixed_nonbinary) == (11836,260,26)
    assert (restriction['fixed_count'],restriction['free_count'],restriction['original_binary_declarations']) == (11836,260,12096)
    plan = load(PRE/'plan.json')
    assert plan['options'] == dict(time_limit=120.0,threads=1,random_seed=0,presolve='on',mip_rel_gap=1e-8)
    assert plan['phase_seconds'] == 300 and plan['planned_calls'] == 1 and plan['call_kind'] == 'mip'
    assert plan['objective'] == 'zero feasibility'
    assert all(plan[k] is True for k in ('no_lp','no_warm_start','no_alternate_neighborhood','no_retries'))
    assert plan['packages'] == {'numpy':'2.3.5','highspy':'1.12.0'} and plan['python'].startswith('3.12.14 ')
    # The 48 inherited bindings include every original native/model/map/spec object.
    # Their previous full audit is inherited by hashes; no old witness is replayed.
    for p,b in captured.items(): assert p.read_bytes() == b, str(p)
    for name, expected in PINS.items(): assert digest((ROOT/name).read_bytes()) == expected
    assert not (ARM/'run01').exists()
    result = dict(status='PASS_PREPARED_COMMON_DIVING',review_source_sha256=digest(Path(__file__).read_bytes()),
        prepared_freeze_sha256=PINS['results/research_next/common_diving/prepared/prepared_freeze.json'],
        manifest_sha256=PINS['results/research_next/common_diving/prepared/input_manifest.json'],
        source_sha256=PINS['src/researchnext_common_diving.py'],protocol_sha256=PINS['docs/research_next/COMMON_DIVING_PROTOCOL.md'],
        bindings_checked_before_and_after=66,inherited_original_bindings=48,
        rows=original.rows,columns=original.cols,nonzeros=len(original.data),original_binary_declarations=sum(bits),
        exact_fixed_states=len(expected_fixed),free_binary_states=len(expected_free),fixed_nonbinary_near_states=newly_fixed_nonbinary,
        actual_changed_column_boxes=changed_boxes,all_original_rows_unchanged=True,all_continuous_boxes_unchanged=True,
        matrix_and_mask_byte_identical=True,complete_fixed_free_records_recomputed=True,
        original_native_and_map_provenance='Unchanged inherited48 bindings; no native/model regeneration or old point replay.',
        execution_directory_absent=True,optimizer_calls=0,producer_imports=0,point_or_ray_checks=0,
        seconds=time.perf_counter()-start)
    with report.open('x',encoding='utf-8') as f: json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result))

if __name__ == '__main__': main()
