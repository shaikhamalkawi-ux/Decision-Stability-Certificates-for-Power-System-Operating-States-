"""External, stdlib-only supplement for the two original January energy intervals."""
from __future__ import annotations
import argparse
import csv
from datetime import datetime, timezone
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import time

sys.dont_write_bytecode = True
COMMIT = '3f51758b521967739131701b106be60036a3fdd4'
OUTER = '4c9f6db4561470775c5e567956c48825de44a6700b0cdcd1607ca50770089409'
OLD_ROOT = 'C:/Users/gmalkawi/.codex/worktrees/dsc-temporal-information/3'
OLD_NATIVE = 'C:/Users/gmalkawi/.codex/worktrees/dsc-v8r1-evidence/3/.work/v8r1_rts_inputs'
ADDENDUM = 'reproducibility/native_sources'
GEN = ADDENDUM + '/rts_inputs/raw/RTS-GMLC_v0.2.3/gen.csv'
ENERGY = 'results/research8h/energy_lp_refinement'
PRIOR = 'results/research8h/energy_price_bounds'
SOURCE = 'results/research8h/seasonal_transfer'
UNCAPPED = 'results/seasonal_uncapped'
CASES = ('january_identity', 'seed_26093100', 'seed_26093101')
MASK = (0,) * 6888 + (1,) * 12096 + (0,) * 4032
TAU = Q.from_float(1e-5)
HELPERS = (
    ('src/research8h_standalone_verify.py', '708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'),
    ('reproducibility/replay_closed_research.py', 'c6cf226ac82ecb5551dee2241e89b2fd1c990fdde3e27878758331b3f998fb85'))
MANIFESTS = (
    (ENERGY + '/input_manifest.json', 'b85b1260ded4d4f0a2576c921a4d84581360bfe7adddac361d5ad8826fd6e32d', 59),
    (UNCAPPED + '/input_manifest.csv', '59ad33b7ef6c6854d9acb3bcca837a521b10dd695711124e204c5c6f4e3a5352', 55))


def need(value, message):
    if not value: raise ValueError(message)


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'Duplicate JSON key'); result[key] = value
        return result
    def invalid(value): raise ValueError('Nonfinite JSON: ' + value)
    return json.loads(Path(path).read_text(encoding='utf-8-sig'), object_pairs_hook=pairs, parse_constant=invalid)


def relative(value):
    need(type(value) is str and '\\' not in value, 'Expected POSIX relative path')
    p = PurePosixPath(value)
    need(value and not p.is_absolute() and ':' not in value and '..' not in p.parts and str(p) == value and value != '.', 'Unsafe path')
    return value


def historical(value):
    value = value.replace('\\', '/')
    for prefix, target in ((OLD_NATIVE, ADDENDUM + '/rts_inputs'), (OLD_ROOT, '')):
        if value.startswith(prefix + '/'):
            tail = relative(value[len(prefix) + 1:])
            return relative(target + '/' + tail if target else tail)
    raise ValueError('Unknown historical root: ' + value)


def no_link(path):
    info = path.lstat()
    need(not stat.S_ISLNK(info.st_mode) and not (getattr(info, 'st_file_attributes', 0) & 0x400), 'Link/reparse prohibited')


def safe_components(path):
    for item in (path, *path.parents):
        if item.exists() or item.is_symlink(): no_link(item)


def csv_records(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        need(len(reader.fieldnames or []) == 3 and set(reader.fieldnames) == {'path', 'sha256', 'bytes'}, 'Manifest CSV schema')
        return list(reader)


def rational(record): return Q(int(record['numerator']), int(record['denominator']))
def rat(value): return dict(numerator=str(value.numerator), denominator=str(value.denominator), approximate=float(value))


def selected_new(new, prior, selected):
    need(new >= prior and new == selected, 'New bound does not dominate prior and equal archived selection')
    return new  # The stored prior is never used as a proof or fallback.


def decimal(value, upper=False):
    scale = 10**6
    integer = -((-value.numerator * scale) // value.denominator) if upper else value.numerator * scale // value.denominator
    sign = '-' if integer < 0 else ''; integer = abs(integer)
    return f'{sign}{integer // scale}.{integer % scale:06d}'


class Replay:
    def __init__(self, root, output, self_hash):
        self.root = root; self.output = output; self.self_hash = self_hash
        self.used = set(); self.bindings = {}; self.manifests = {}; self.math_start = None
        self.roles = {case: 'NOT_EVALUATED' for case in CASES}
        manifest = root / 'FILE_MANIFEST.csv'; no_link(manifest)
        need(sha(manifest) == OUTER, 'Trusted outer mismatch')
        rows = csv_records(manifest); self.package = {}; folded = set()
        for item in rows:
            name = relative(item['path']); need(name.casefold() not in folded, 'Manifest alias/case collision')
            folded.add(name.casefold()); self.package[name] = item
        self.before = self.snapshot()
        need(set(self.before) == set(self.package) | {'FILE_MANIFEST.csv'}, 'Complete package file-set mismatch')
        for name, record in self.package.items(): self.binding(name, record)
        need(self.js('PACKAGE_PROVENANCE.json')['git_commit'] == COMMIT, 'Trusted Git20 provenance mismatch')
        self.manifest(ADDENDUM + '/FILE_MANIFEST.csv', '8b18311c646c0ae68d85765c57b690e2db5b5ffc071d1ab1b734b2db88d866b8', 24, ADDENDUM)
        mapping = self.js(ADDENDUM + '/path_map.json')
        need(mapping['maps'] == [dict(original_prefix=OLD_ROOT, portable_relative_root='.'), dict(original_prefix=OLD_NATIVE, portable_relative_root=ADDENDUM + '/rts_inputs')], 'Native prefix map')
        native = self.js(ADDENDUM + '/source_bindings.json')
        need(native['native_file_count'] == len(native['files']) == 17 and native['native_bytes'] == 3734672 and not native['conflicting_provenance'], 'Native addendum scope')
        for item in native['files']:
            name = historical(item['original_path']); need(name == ADDENDUM + '/' + relative(item['portable_path']), 'Native alias'); self.binding(name, item)
        for args in MANIFESTS: self.manifest(*args)
        audit = self.path(PRIOR + '/audit_freeze.json')
        need(sha(audit) == '53d531d6817984ed857e60471087eae6099332a43be62b8da37fe85bf7b99e49', 'Prior audit binding')
        self.bind_rows(read(audit)['inputs'], 49)
        # Follow only input manifests reached by these two original interval arms.
        while True:
            pending = [n for n in self.reached if PurePosixPath(n).name in ('input_manifest.csv', 'input_manifest.json') and n not in self.manifests]
            if not pending: break
            for name in sorted(pending): self.manifest(name, self.bindings[name][1], None)
        need(sha(self.path(GEN)) == '988466f29132b73739de60c9204dd4a2a9ceb0adf572e5966c086611272f4068', 'Native GEN bytes')
        for name, digest in ((ENERGY + '/independent_review.json', '94c10b498dc600f92d55c77987325a106d7dcbb64f201a284a8295b756528401'), (PRIOR + '/independent_review.json', 'd70d955763a5aa7aa7c6a3ac0f889a2786e112939493452ad2bf51e6030bfd1d')):
            need(sha(self.path(name)) == digest, 'Original independent review binding')
        self.save('provenance', dict(status='FINAL20_PACKAGE_AND_ORIGINAL_ENERGY_PROVENANCE_PASS', package_payloads=len(self.package), package_manifest_sha256=OUTER, package_evidence_commit=COMMIT, historical_manifests=self.manifests, native_reconstruction=False, prior_derivations_replayed=False))
        self.math_start = time.perf_counter()
        modules = []
        for i, (name, digest) in enumerate(HELPERS):
            self.tick(); path = self.path(name); need(sha(path) == digest, 'Pinned helper changed')
            spec = importlib.util.spec_from_file_location('unrestricted_helper_' + str(i), path)
            module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module; spec.loader.exec_module(module); modules.append(module)
        self.v, self.h = modules

    def tick(self):
        if self.math_start is not None and time.perf_counter() - self.math_start >= 300:
            raise TimeoutError('300-second soft arithmetic phase limit; remaining roles retained')

    def snapshot(self):
        result = {}; folded = set()
        for path in self.root.rglob('*'):
            no_link(path)
            if path.is_file():
                name = relative(path.relative_to(self.root).as_posix()); need(name.casefold() not in folded, 'Filesystem case collision'); folded.add(name.casefold())
                result[name] = (path.stat().st_size, sha(path))
        return result

    def path(self, name):
        name = relative(name); need(name in self.package, 'Missing package input: ' + name)
        path = self.root / name; no_link(path); need(path.resolve().is_relative_to(self.root), 'Escaping path'); self.used.add(name); return path

    def js(self, name): return read(self.path(name))

    def binding(self, name, record):
        need(re.fullmatch('[0-9a-f]{64}', record['sha256']) is not None and str(record['bytes']).isdigit(), 'Invalid hash/size')
        value = (int(record['bytes']), record['sha256']); need(self.before.get(name) == value, 'Bound bytes differ: ' + name)
        need(name not in self.bindings or self.bindings[name] == value, 'Conflicting bindings'); self.bindings[name] = value

    def bind_rows(self, rows, count, base=None):
        need(type(rows) is list and (count is None or len(rows) == count), 'Historical manifest count/schema')
        if not hasattr(self, 'reached'): self.reached = set()
        seen = set()
        for item in rows:
            need(set(item) == {'path', 'sha256', 'bytes'}, 'Historical record schema')
            name = historical(item['path']) if base is None else relative(base + '/' + relative(item['path']))
            need(name.casefold() not in seen, 'Historical alias'); seen.add(name.casefold()); self.binding(name, item); self.reached.add(name)

    def manifest(self, name, digest, count, base=None):
        path = self.path(name); need(sha(path) == digest, 'Historical manifest digest')
        rows = read(path) if path.suffix == '.json' else csv_records(path)
        self.bind_rows(rows, count, base); self.manifests[name] = dict(sha256=digest, entries=len(rows))

    def save(self, name, record):
        with (self.output / (name + '.json')).open('x', encoding='utf-8') as stream:
            json.dump(record, stream, indent=2, allow_nan=False); stream.write('\n')
        print(json.dumps(dict(check=name, status=record.get('status', 'PASS'))), flush=True)

    def array(self, name, key, count, keys=None):
        obj = self.v.read_npz(self.path(name), keys or (key,))[key]
        need(obj.shape == (count,), 'Array shape'); return obj.values

    def model(self, directory):
        self.path(directory + '/matrix.npz'); self.path(directory + '/bounds.npz')
        return self.v.load_model(self.root / directory)

    def labels(self, directory):
        with gzip.open(self.path(directory + '/row_metadata.csv.gz'), 'rt', encoding='utf-8', newline='') as stream: return list(csv.DictReader(stream))

    @staticmethod
    def row(model, i):
        a, b = model.indptr[i:i + 2]; return tuple(zip(model.indices[a:b], model.data[a:b]))

    def relation(self, case):
        directory = ENERGY + '/' + case; parent = SOURCE + '/' + case
        model = self.model(directory); capped = self.model(parent); labels = self.labels(directory); old = self.labels(parent)
        need((model.rows, model.cols) == (34680, 23016) and (capped.rows, capped.cols) == (34681, 23016), 'Model dimensions')
        caps = [i for i, row in enumerate(old) if row['family'] == 'fossil_energy_cap']
        need(len(caps) == 1 and capped.row_lower[caps[0]] == -math.inf and capped.row_upper[caps[0]] == 23195., 'Sole original cap')
        keep = [i for i in range(capped.rows) if i != caps[0]]
        need(model.lower == capped.lower and model.upper == capped.upper and len(labels) == model.rows and len(old) == capped.rows, 'Column bounds/row metadata')
        for i, j in enumerate(keep):
            need(self.row(model, i) == self.row(capped, j) and model.row_lower[i] == capped.row_lower[j] and model.row_upper[i] == capped.row_upper[j], 'Not cap-only row deletion')
            need(all(labels[i][k] == old[j][k] for k in ('family', 'hour_0based', 'uid')), 'Row label relation')
        need(not any('mean' in r['family'] or r['family'] == 'fossil_energy_cap' for r in labels), 'Unexpected mean/cap')
        mask = self.array(directory + '/original_integrality.npz', 'integrality', model.cols)
        need(mask == MASK == self.array(parent + '/integrality.npz', 'integrality', model.cols), 'Original full binary mask')
        cost = self.array(directory + '/objective.npz', 'objective', model.cols)
        need(tuple((j, x) for j, x in enumerate(cost) if x) == self.row(capped, caps[0]), 'Objective/cap mismatch')
        meta = self.js(parent + '/model_metadata.json')
        need(meta['offsets'] == dict(P=0, U=6888, Y=10920, Z=14952, theta=18984), 'Column ordering')
        with self.path(GEN).open(encoding='utf-8-sig', newline='') as stream: fuels = {r['GEN UID']: r['Fuel'] for r in csv.DictReader(stream)}
        names = meta['unit_names']; fossil = [j for j, name in enumerate(names) if fuels[name] in ('Coal', 'Oil', 'NG')]
        need(len(names) == len(set(names)) == 41 and len(fossil) == 23 and [names[j] for j in fossil] == meta['fossil_units'] and names[23] == '121_NUCLEAR_1' and 23 not in fossil, 'Fossil roster')
        support = {t * 41 + j for t in range(168) for j in fossil}
        need(cost == tuple(float(j in support) for j in range(model.cols)), 'Actual fossil objective')
        inherited = parent if case == CASES[0] else UNCAPPED + '/' + case
        vector = inherited + ('/constructive_vector.npz' if case == CASES[0] else '/recovered_vector.npz')
        if case != CASES[0]:
            for name in ('matrix.npz', 'bounds.npz'): need(sha(self.path(directory + '/' + name)) == sha(self.path(inherited + '/' + name)), 'Refinement/uncapped parent bytes')
            need(sha(self.path(inherited + '/native_inputs.npz')) == sha(self.path(parent + '/native_inputs.npz')), 'Native input inheritance')
            need(self.array(inherited + '/original_integrality.npz', 'integrality', model.cols) == MASK, 'U-only mask used for upper')
            self.path(inherited + '/native_no_cap_check.json'); self.path(inherited + '/exact_point_check.json')
        else:
            self.path(parent + '/native_inputs.npz'); self.path(parent + '/raw_reference_check.json'); self.path(parent + '/rounded_reference_check.json')
        binding = self.js(directory + '/model_and_upper_binding.json')
        need(historical(binding['positive_vector_path']) == vector and sha(self.path(vector)) == binding['positive_vector_sha256'], 'Upper vector binding')
        retained = self.array(directory + '/retained_parent_rows.npz', 'rows', model.rows)
        need(retained == tuple(keep if case == CASES[0] else range(model.rows)), 'Refinement parent row map')
        return model, cost, mask, vector

    def case(self, case):
        self.tick(); model, cost, mask, vector = self.relation(case); directory = ENERGY + '/' + case
        self.roles[case] = 'MODEL_RELATION_VERIFIED'; self.tick()
        point = self.array(vector, 'vector', model.cols); checked = self.v.check_point(model, point, mask, TAU)
        need(checked['expanded_pass'] and checked['binary_coordinates'] == 12096, 'Original binary upper rejected')
        upper = sum((Q(c) * Q(x) for c, x in zip(cost, point)), Q(0)); self.tick()
        raw = self.array(directory + '/raw_duals.npz', 'row_dual', model.rows, ('row_dual', 'column_dual'))
        need(all(math.isfinite(v) for v in raw), 'Nonfinite raw dual')
        forbidden = [(x > 0 and not math.isfinite(model.row_lower[i])) or (x < 0 and not math.isfinite(model.row_upper[i])) for i, x in enumerate(raw)]
        projected = tuple(0. if bad else x for x, bad in zip(raw, forbidden))
        need(projected == self.array(directory + '/projected_row_dual.npz', 'row_dual', model.rows), 'Raw sign projection mismatch')
        report, residual = self.h.objective_lower(model, cost, projected, TAU)
        exact = self.js(directory + '/exact_lower_bound.json')
        need(all(rational(exact[k]) == rational(value) for k, value in report.items()) and rational(exact['tau']) == TAU, 'Exact objective components')
        need(exact['projected_entries'] == sum(forbidden) and exact['projected_row_dual_nonzeros'] == sum(x != 0 for x in projected) and exact['exact_residual_nonzeros'] == sum(x != 0 for x in residual), 'Dual/residual counts')
        sparse = self.js(directory + '/exact_stationarity_residual.json')
        need(len({x['column'] for x in sparse}) == len(sparse) and {x['column']: rational(x) for x in sparse} == {i: x for i, x in enumerate(residual) if x}, 'Sparse exact residual')
        result = self.js(directory + '/result.json'); prior = self.js(directory + '/prior_bounds.json')
        new = rational(report['expanded_lower_bound_MWh'])
        lower = selected_new(new, rational(prior['lower_MWh']), rational(result['best_lower_MWh']))
        need(new == rational(result['new_lower_MWh']) and rational(prior['lower_MWh']) == rational(result['previous_lower_MWh']), 'Archived selection metadata')
        need(0 < lower <= upper and upper == rational(prior['binary_upper_MWh']) == rational(result['unchanged_binary_upper_MWh']) == rational(self.js(directory + '/model_and_upper_binding.json')['binary_upper_MWh']), 'Verified upper/lower enclosure')
        self.roles[case] = 'FULL_POINT_AND_NEW_BOUND_VERIFIED'
        self.save(case, dict(status='EXPANDED_ORIGINAL_BINARY_ENERGY_ENCLOSURE_PASS', lower=rat(lower), upper=rat(upper), point=checked, exact_bound=report, prior_proof_replayed=False, prior_used_as_endpoint=False, native_physical_audit_inherited=True))
        self.tick(); return lower, upper

    def intervals(self, values):
        li, ui = values[CASES[0]]; old = self.js(ENERGY + '/refined_brackets.json'); relative_old = self.js(ENERGY + '/relative_penalty_bounds.json')
        need([x['case'] for x in old] == list(CASES[1:]) == [x['case'] for x in relative_old['results']], 'Two-interval denominator')
        need(relative_old['source_refined_brackets_sha256'] == sha(self.path(ENERGY + '/refined_brackets.json')), 'Relative source binding')
        outputs = []
        for case, row, rel in zip(CASES[1:], old, relative_old['results']):
            self.tick(); lt, ut = values[case]; ranges = self.h.intervals(li, ui, lt, ut)
            for key, expected in (('identity_optimum_bounds_MWh', (li, ui)), ('target_optimum_bounds_MWh', (lt, ut)), ('optimum_difference_MWh', ranges['optimum_difference_MWh']), ('target_optimum_excess_over_chosen_reference_MWh', ranges['target_optimum_excess_over_chosen_incumbent_MWh'])):
                need(tuple(rational(row[key][side]) for side in ('lower', 'upper')) == expected, 'Absolute enclosure arithmetic')
                for side, value in zip(('lower', 'upper'), expected):
                    for upper, field in ((False, 'outward_floor_6dp'), (True, 'outward_ceiling_6dp')): need(row[key][side][field] == float(decimal(value, upper)), 'Absolute outward display')
            for key, expected in (('relative_optimum_penalty', ranges['optimal_relative_penalty']), ('relative_optimum_penalty_percent', ranges['optimal_relative_penalty_percent'])):
                for side, value in zip(('lower', 'upper'), expected):
                    record = rel[key][side]; need(rational(record) == value and record['decimal_floor_6dp'] == decimal(value) and record['decimal_ceiling_6dp'] == decimal(value, True), 'Relative exact/outward arithmetic')
            outputs.append(dict(case=case, intervals={k: [rat(x) for x in pair] for k, pair in ranges.items()}))
        self.save('intervals', dict(status='TWO_ORIGINAL_UNRESTRICTED_INTERVALS_PASS', cases=outputs, interval_denominator=2, identity_dependency_roles=1))

    def finish(self, start):
        self.tick(); math_elapsed = time.perf_counter() - self.math_start
        need(self.snapshot() == self.before, 'Package bytes or file set changed')
        need(sha(Path(__file__)) == self.self_hash, 'External wrapper changed')
        self.save('summary', dict(status='PORTABLE_ORIGINAL_UNRESTRICTED_ENERGY_PASS', roles=self.roles, intervals=2, point_roles=3, new_dual_bounds=3, prior_proofs_replayed=0, optimizer_calls=0, network_calls=0, native_reconstruction=False, native_audits_inherited=True, package_files_unchanged=True, self_sha256=self.self_hash, package_manifest_sha256=OUTER, package_evidence_commit=COMMIT, math_seconds=math_elapsed, total_seconds=time.perf_counter()-start, python=sys.version, second_machine_claim=False))


def focused():
    need(selected_new(Q(4), Q(3), Q(4)) == 4, 'Selection fixture')
    rejected = 0
    for args in ((Q(2), Q(3), Q(3)), (Q(4), Q(3), Q(5))):
        try: selected_new(*args)
        except ValueError: rejected += 1
    need(rejected == 2, 'Selection rejection fixtures')
    need(decimal(Q(-1, 3)) == '-0.333334' and decimal(Q(-1, 3), True) == '-0.333333', 'Signed outward fixture')
    for value in ('../x', 'a//b', '/x', 'C:/x'):
        try: relative(value)
        except ValueError: continue
        raise ValueError('Path fixture accepted')
    return dict(status='NEW_SELECTION_DISPLAY_PATH_FIXTURES_PASS', checks=8, old_kernel_tests_repeated=False)


def main():
    need(sys.flags.isolated == 1 and sys.flags.no_site == 1, 'Use Python -I -S')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package-root', required=True, type=Path); parser.add_argument('--report-dir', required=True, type=Path)
    parser.add_argument('--expected-self-sha256', required=True); parser.add_argument('--expected-package-manifest-sha256', required=True)
    parser.add_argument('--package-evidence-commit', required=True); parser.add_argument('--initial-run', action='store_true')
    args = parser.parse_args(); start = time.perf_counter()
    need(re.fullmatch('[0-9a-f]{64}', args.expected_self_sha256) is not None and sha(Path(__file__)) == args.expected_self_sha256, 'Trusted external self hash')
    need(args.expected_package_manifest_sha256 == OUTER and args.package_evidence_commit == COMMIT, 'Wrong trusted final20 identity')
    if args.initial_run: need(datetime.now(timezone.utc) < datetime(2026, 9, 27, 5, 30, tzinfo=timezone.utc), 'Initial execution latest-start guard')
    safe_components(args.package_root); safe_components(args.report_dir)
    root = args.package_root.resolve(); output = args.report_dir.resolve(); source = Path(__file__).resolve()
    need(root.is_dir() and not output.exists() and not source.is_relative_to(root) and not output.is_relative_to(root) and not root.is_relative_to(output), 'External source/fresh external reports required')
    output.mkdir(parents=True, exist_ok=False); replay = None
    try:
        replay = Replay(root, output, args.expected_self_sha256); replay.save('focused_checks', focused())
        values = {case: replay.case(case) for case in CASES}; replay.intervals(values); replay.finish(start)
    except Exception as error:
        report = dict(status='SUPPLEMENT_REPLAY_FAILED_OR_INCOMPLETE', error_type=type(error).__name__, error=str(error), roles=replay.roles if replay else {c: 'NOT_EVALUATED' for c in CASES}, model_denominator=3, interval_denominator=2, elapsed_seconds=time.perf_counter()-start, optimizer_calls=0, partial_reports_preserved=True)
        with (output / 'failure.json').open('x', encoding='utf-8') as stream: json.dump(report, stream, indent=2); stream.write('\n')
        print(json.dumps(report), flush=True); return 1
    return 0


if __name__ == '__main__': raise SystemExit(main())
