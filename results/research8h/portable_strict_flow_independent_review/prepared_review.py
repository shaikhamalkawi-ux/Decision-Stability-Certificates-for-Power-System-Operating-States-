"""Independent byte/provenance gate only; no replay imports or model arithmetic."""
from pathlib import Path, PurePosixPath
import csv
import hashlib
import io
import json
import os
import re
import stat
import subprocess
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / '.work/research8h_delivery/DSC_Temporal_Research_2026-09-27_Checkpoint05.zip'
BASE_SHA = '495dcd6831ddbcd1c8263b32a536d5d9ff7ef2943fe54250c1c5532359e366d7'
COMMIT = '579ecf20452b7838fdc5802744b24f597af5e1c7'
PREFIXES = ('src/research8h_', 'docs/research8h/', 'results/research8h/', 'results/seasonal_uncapped/', 'reproducibility/')
ADDITIONS = {
    'reproducibility/replay_strict_flow.py': '52dbe3b74c1709a36ab23b31768a8e1f1c24a1daa00df2abba7b03bd2e96fad7',
    'docs/research8h/PORTABLE_STRICT_FLOW_REPLAY_PROTOCOL.md': '7d619dc7c7e7bb76da71dd7ee2496f507875bbd5ed0fb356e50417791e66557a',
}
NATIVE = 'reproducibility/native_sources'
INITIAL_MANIFESTS = (
    ('results/research8h/branch_flow_encoding/input_manifest.json', '0981491f326dbd3f34e2825d501cbff54d74bf18e5c3d924edf420a4950532d4', 103, 'historical', ''),
    ('results/research8h/branch_flow_encoding/artifact_manifest.csv', 'a86ee29993a253e7018965cf9ce66dc177e220129eba849a4529960a09e237c4', 277, 'relative', ''),
    ('results/research8h/branch_flow_strict_energy/input_manifest.json', '7ffffe82e6046daff5dcd610337c2e8cb333009c38ec9acfcdb9741f8cbadbb7', 355, 'historical', ''),
    ('results/research8h/branch_flow_strict_energy/artifact_manifest.csv', '89475add4fdc688cf7227a201fa870712602cc67269b0ad7bacdfa7f8ef65648', 466, 'relative', ''),
    (NATIVE + '/FILE_MANIFEST.csv', '8b18311c646c0ae68d85765c57b690e2db5b5ffc071d1ab1b734b2db88d866b8', 24, 'relative', NATIVE),
)

def require(value, message):
    if not value:
        raise ValueError(message)

def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()

def canonical(value):
    require(type(value) is str and value and ':' not in value and '\\' not in value, 'Invalid relative path')
    p = PurePosixPath(value)
    require(not p.is_absolute() and '..' not in p.parts and str(p) == value and value != '.', 'Escaping/noncanonical path')
    for part in p.parts:
        require(part.rstrip(' .') == part, 'Windows ambiguous path')
        require(part.split('.')[0].upper() not in {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)), *(f'LPT{i}' for i in range(1, 10))}, 'Reserved device path')
    return value

def no_link(path):
    mode = os.lstat(path)
    require(not stat.S_ISLNK(mode.st_mode) and not (getattr(mode, 'st_file_attributes', 0) & 0x400), 'Link/reparse point: ' + str(path))

def safe_parents(path):
    for p in (path, *path.parents):
        if p.exists() or p.is_symlink():
            no_link(p)

def inventory(root):
    result = {}
    folded = set()
    dirs = 0
    safe_parents(root)
    for current, names, files in os.walk(root, followlinks=False):
        no_link(Path(current))
        dirs += 1
        for name in names:
            no_link(Path(current) / name)
        for name in files:
            p = Path(current) / name
            no_link(p)
            require(p.is_file(), 'Nonregular file')
            n = canonical(p.relative_to(root).as_posix())
            require(n.casefold() not in folded, 'Casefold collision')
            folded.add(n.casefold())
            result[n] = (p.stat().st_size, sha(p))
    return result, dirs

def rows(data, json_format=False):
    if json_format:
        values = json.loads(data.decode('utf-8-sig'))
    else:
        reader = csv.DictReader(io.StringIO(data.decode('utf-8-sig')))
        require(len(reader.fieldnames or []) == 3 and set(reader.fieldnames) == {'path', 'bytes', 'sha256'}, 'Manifest header')
        values = list(reader)
    require(type(values) is list and values, 'Empty or invalid manifest')
    result = {}
    folded = set()
    for row in values:
        require(set(row) == {'path', 'bytes', 'sha256'}, 'Manifest fields')
        n = row['path'].replace('\\', '/')
        require(n.casefold() not in folded, 'Duplicate manifest row')
        folded.add(n.casefold())
        require(re.fullmatch('[0-9a-f]{64}', row['sha256']) and str(row['bytes']).isdigit(), 'Invalid descriptor')
        result[n] = (int(row['bytes']), row['sha256'])
    return result

def zip_table(archive):
    table = {}
    folded = set()
    for info in archive.infolist():
        require(not info.is_dir(), 'Unexpected ZIP directory')
        n = canonical(info.filename)
        require(n.casefold() not in folded, 'ZIP duplicate/case collision')
        folded.add(n.casefold())
        require(stat.S_IFMT(info.external_attr >> 16) in (0, stat.S_IFREG) and not (info.external_attr & 0x400), 'Special ZIP member')
        require(not info.flag_bits & 1 and info.compress_type in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED), 'Unsupported ZIP encoding')
        table[n] = info
    for n in table:
        require(not any(str(p) in table for p in PurePosixPath(n).parents if str(p) != '.'), 'ZIP file ancestor collision')
    return table

def main():
    start = time.perf_counter()
    require(len(sys.argv) == 4, 'Usage: reviewer candidate_root trusted_outer_sha trusted_zip_sha')
    out = Path(sys.argv[1]).resolve()
    package = out / 'package'
    trusted_outer, trusted_zip = sys.argv[2:]
    require(re.fullmatch('[0-9a-f]{64}', trusted_outer) and re.fullmatch('[0-9a-f]{64}', trusted_zip), 'Invalid trusted digests')
    safe_parents(out)
    require(not out.is_relative_to(ROOT.resolve()), 'Candidate is not relocated')
    require(not (out / 'reports').exists(), 'Replay reports unexpectedly exist before gate')
    freeze = json.loads((out / 'prepared_freeze.json').read_text(encoding='utf-8'))
    require(freeze['wrapper_imported'] is False and freeze['mathematical_replay'] is False and freeze['optimizer_calls'] == 0 and freeze['execution_authorized'] is False, 'Wrong preparation status')
    require(freeze['evidence_commit'] == COMMIT and freeze['outer_manifest_sha256'] == trusted_outer and freeze['candidate_sha256'] == trusted_zip, 'Freeze/trusted identity mismatch')
    require(freeze['builder_sha256'] == '0a9527bc2cdbe2adaba2637b0e9bd5bdd51ced15c35cf50c34a0cc86947f933f', 'Builder identity')
    require(sha(out / 'preparation_builder.py') == freeze['builder_sha256'], 'Saved builder differs')
    require(freeze['base_payloads_preserved'] == 3501 and freeze['existing_base_modifications'] == 0, 'Base preservation declaration')
    failed = ROOT / 'results/research8h/portable_strict_flow_replay/failed_candidate01'
    require(sha(failed / 'provenance.json') == freeze['failed_candidate01_provenance_sha256'] == 'c24f43ae82a22d92d9bda4f6f97c4321df772f7a0db91ac65cb65cf7d12c406f', 'Failed-attempt provenance')
    failed_records = json.loads((failed / 'provenance.json').read_text(encoding='utf-8'))['files']
    for record in failed_records:
        p = failed / canonical(record['path'])
        safe_parents(p)
        require(p.stat().st_size == record['bytes'] and sha(p) == record['sha256'], 'Failed-attempt copy differs')
    require(sha(failed / 'scope_diagnosis.json') == freeze['diagnosis_sha256'] == 'cc470ab7b88f5ef429fe8809fb326842dc0bf9f954008cee991ac92d7701bb1b', 'Diagnosis identity')
    require(sha(package / 'FILE_MANIFEST.csv') == trusted_outer, 'Outer manifest digest')
    outer = rows((package / 'FILE_MANIFEST.csv').read_bytes())
    for n in outer:
        canonical(n)
    disk, directories = inventory(package)
    require(set(disk) == set(outer) | {'FILE_MANIFEST.csv'}, 'Candidate inventory mismatch')
    require(all(disk[n] == value for n, value in outer.items()), 'Outer payload digest mismatch')
    require(len(outer) == 4566 and len(disk) == freeze['candidate_files'] and directories == freeze['directories_checked'], 'Candidate counts')

    require(BASE.stat().st_size == 88756097 and sha(BASE) == BASE_SHA, 'Base ZIP identity')
    with zipfile.ZipFile(BASE) as archive:
        index = zip_table(archive)
        original_manifest_bytes = archive.read('FILE_MANIFEST.csv')
        original = rows(original_manifest_bytes)
        require(len(original) == 3501 and set(index) == set(original) | {'FILE_MANIFEST.csv'}, 'Base complete inventory')
        for n, value in original.items():
            data = archive.read(n)
            require((len(data), sha_bytes(data)) == value and disk.get(n) == value, 'Base payload was changed: ' + n)
    require((out / 'base_FILE_MANIFEST.csv').read_bytes() == original_manifest_bytes, 'Saved base manifest differs')

    git = lambda *args: subprocess.check_output(['git', *args], cwd=ROOT)
    require(git('rev-parse', '--verify', COMMIT).decode().strip() == COMMIT, 'Unavailable pinned commit')
    tree = []
    for item in git('ls-tree', '-r', '-z', COMMIT).split(b'\0'):
        if not item:
            continue
        meta, raw_path = item.split(b'\t', 1)
        mode, kind, oid = meta.decode('ascii').split()
        n = raw_path.decode('utf-8')
        if not n.startswith(PREFIXES):
            continue
        canonical(n)
        require(kind == 'blob' and mode in ('100644', '100755'), 'Unsupported Git object')
        tree.append((n, oid))
    require(len(tree) == 4462 and len({n.casefold() for n, _ in tree}) == len(tree), 'Pinned overlay file set')
    expected = dict(original)
    verified_blobs = {}
    proc = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for n, oid in tree:
            proc.stdin.write((oid + '\n').encode('ascii'))
            proc.stdin.flush()
            header = proc.stdout.readline().decode('ascii').strip().split()
            require(len(header) == 3 and header[:2] == [oid, 'blob'], 'Git response header')
            size = int(header[2])
            data = proc.stdout.read(size)
            require(len(data) == size and proc.stdout.read(1) == b'\n', 'Truncated Git response')
            require(hashlib.sha1(b'blob ' + str(size).encode() + b'\0' + data).hexdigest() == oid, 'Git object mismatch')
            value = (size, sha_bytes(data))
            require(n not in original or original[n] == value, 'Git overlay would replace old bytes: ' + n)
            require(disk.get(n) == value, 'Candidate differs from pinned Git object: ' + n)
            expected[n] = value
            verified_blobs[n] = dict(git_blob=oid, bytes=size, sha256=value[1])
        proc.stdin.close()
        require(proc.wait() == 0, 'Git reader failure')
    finally:
        if proc.poll() is None:
            proc.terminate()
            proc.wait()
    producer_overlay = json.loads((out / 'git17_overlay.json').read_text(encoding='utf-8'))
    require(producer_overlay['commit'] == COMMIT and tuple(producer_overlay['prefixes']) == PREFIXES, 'Producer overlay scope')
    producer_records = {r['path']: r for r in producer_overlay['files']}
    require(set(producer_records) == set(verified_blobs), 'Producer Git set mismatch')
    for n, r in verified_blobs.items():
        p = producer_records[n]
        require(all(p[k] == v for k, v in r.items()), 'Producer Git descriptor mismatch')
        require(p['previous_sha256'] == (original[n][1] if n in original else None), 'Producer old-file descriptor')
        require(p['changed'] == (n not in original), 'Producer overwrite flag')
    for n, h in ADDITIONS.items():
        require(n not in expected and disk[n][1] == h and sha(ROOT / n) == h, 'Reviewed addition mismatch')
        expected[n] = disk[n]
    candidate_metadata = json.loads((package / 'STRICT_FLOW_CANDIDATE.json').read_text(encoding='utf-8'))
    require(candidate_metadata == dict(schema='strict-flow-candidate-v1', evidence_commit=COMMIT, scope='strict-flow-capped-and-uncapped-v1'), 'Candidate metadata identity')
    expected['STRICT_FLOW_CANDIDATE.json'] = disk['STRICT_FLOW_CANDIDATE.json']
    require(expected == outer, 'Candidate contains additions outside declared union')

    queue = list(INITIAL_MANIFESTS)
    manifests, bindings = {}, {}
    def remap(n):
        for prefix, target in (
            ('C:/Users/gmalkawi/.codex/worktrees/dsc-v8r1-evidence/3/.work/v8r1_rts_inputs/', NATIVE + '/rts_inputs/'),
            ('C:/Users/gmalkawi/.codex/worktrees/dsc-temporal-information/3/', ''),
        ):
            if n.startswith(prefix):
                return canonical(target + canonical(n[len(prefix):]))
        raise ValueError('Unknown historical prefix: ' + n)
    while queue:
        path, digest, count, mode, base = queue.pop(0)
        if path in manifests:
            require(manifests[path]['sha256'] == digest, 'Conflicting manifest versions')
            continue
        require(disk[path][1] == digest, 'Historical manifest digest')
        desc = rows((package / path).read_bytes(), path.endswith('.json'))
        require(count is None or len(desc) == count, 'Historical manifest count')
        seen = set()
        for n, value in desc.items():
            actual = remap(n) if mode == 'historical' else canonical((base + '/' if base else '') + canonical(n))
            require(actual not in seen, 'Historical remap collision')
            seen.add(actual)
            require(disk.get(actual) == value, 'Historical bound file differs: ' + actual)
            require(actual not in bindings or bindings[actual] == value, 'Historical cross-manifest version conflict')
            bindings[actual] = value
            if PurePosixPath(actual).name in ('input_manifest.csv', 'input_manifest.json'):
                queue.append((actual, value[1], None, 'historical', ''))
        manifests[path] = dict(sha256=digest, entries=len(desc), mode=mode, base=base)
    require(len(manifests) == 11 and len(bindings) == 1133, 'Recursive closure counts')
    claimed = json.loads((out / 'recursive_manifest_closure.json').read_text(encoding='utf-8'))
    require(claimed['manifests'] == manifests and claimed['unique_bound_payloads'] == len(bindings), 'Producer closure report mismatch')
    candidate_zip = Path(freeze['candidate_zip'])
    require(candidate_zip.parent == out and sha(candidate_zip) == trusted_zip and candidate_zip.stat().st_size == freeze['candidate_bytes'], 'Candidate ZIP identity')
    with zipfile.ZipFile(candidate_zip) as archive:
        index = zip_table(archive)
        require(set(index) == set(disk), 'Candidate ZIP inventory')
        for n, value in disk.items():
            data = archive.read(n)
            require((len(data), sha_bytes(data)) == value, 'Candidate ZIP member mismatch: ' + n)
    final, final_dirs = inventory(package)
    require(final == disk and final_dirs == directories and sha(BASE) == BASE_SHA, 'Inputs changed during gate')
    require(not (out / 'reports').exists(), 'Replay began during preparation gate')
    report = dict(status='INDEPENDENT_PREPARED_REVIEW_PASS', candidate=str(out), base_payloads_preserved=len(original), pinned_git_blobs=len(tree), candidate_payloads=len(outer), candidate_files=len(disk), directories_checked=directories, recursive_manifests=manifests, unique_historical_payloads=len(bindings), outer_manifest_sha256=trusted_outer, candidate_zip_sha256=trusted_zip, evidence_commit=COMMIT, all_git_blob_objects_checked=True, no_links_or_reparse_points=True, no_unexpected_overlay_replacements=True, wrapper_imported=False, model_arithmetic_replay=False, optimizer_calls=0, network_calls=0, reviewer_sha256=sha(Path(__file__)), elapsed_s=time.perf_counter()-start)
    target = Path(__file__).with_name('prepared_review.json')
    with target.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps(report), flush=True)

if __name__ == '__main__':
    main()
