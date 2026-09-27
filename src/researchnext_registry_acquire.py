"""One reviewed registry-only acquisition. No Julia, Pkg or scientific model.

Raw transport diagnostics remain private. No retry or partial-file continuation.
"""
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlsplit
import gzip
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import tarfile
import time

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / '.work/researchnext_julia_export/registry_acquire03'
OUTPUT = ROOT / 'results/research_next/registry_acquire03/run01'
PROTOCOL = ROOT / 'docs/research_next/REGISTRY_ACQUIRE03_PROTOCOL.md'
OLD_PARTIAL = ROOT / '.work/researchnext_julia_export/attempt02/General.tar.gz'
OLD_SHA = 'bcad8b91e05724c484a7f991fe4cca99257ed9ec0ccc6cdf5f246b8ed2991210'
COMMIT = '416a13c3e4888af4b245812d8f4ab040a042c38f'
TREE = 'f39bab42a09b8a82574435c6e402e598b3200dc3'
URL = 'https://codeload.github.com/JuliaRegistries/General/tar.gz/' + COMMIT
COMPRESSED_LIMIT = 100_000_000
DECODED_LIMIT = 2_000_000_000
MEMBER_LIMIT = 250_000
FILE_LIMIT = 32_000_000
RESERVED = {'con', 'prn', 'aux', 'nul'} | {'com'+str(n) for n in range(1,10)} | {'lpt'+str(n) for n in range(1,10)}


def utc():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for data in iter(lambda: f.read(1024*1024), b''):
            h.update(data)
    return h.hexdigest()


def write_new(path, data):
    with path.open('x', encoding='utf-8') as f:
        json.dump(data, f, indent=2, allow_nan=False)
        f.write('\n')


def git_object(kind, data):
    return hashlib.sha1(kind + b' ' + str(len(data)).encode() + b'\0' + data).digest()


def tree_hash(files):
    root = {}
    for parts, mode, blob in files:
        node = root
        for name in parts[:-1]:
            if name in node and not isinstance(node[name], dict):
                raise ValueError('File/directory prefix collision')
            node = node.setdefault(name, {})
        if parts[-1] in node:
            raise ValueError('Duplicate Git-tree path')
        node[parts[-1]] = (mode, blob)

    def visit(node):
        ordered = sorted(node.items(), key=lambda pair:
                         (pair[0] + ('/' if isinstance(pair[1], dict) else '')).encode('utf-8'))
        chunks = []
        for name, value in ordered:
            mode, value_hash = (b'40000', visit(value)) if isinstance(value, dict) else value
            chunks.append(mode + b' ' + name.encode('utf-8') + b'\0' + value_hash)
        return git_object(b'tree', b''.join(chunks))
    return visit(root).hex()


def safe_member(info):
    name = info.name
    if not name or name.startswith('/') or '\\' in name or '\0' in name:
        raise ValueError('Unsafe tar member path')
    raw = name[:-1] if name.endswith('/') else name
    parts = tuple(raw.split('/'))
    if parts[0] != 'General-' + COMMIT:
        raise ValueError('Unexpected archive root')
    for part in parts:
        if not part or part in ('.', '..') or ':' in part or part.endswith(('.', ' ')):
            raise ValueError('Noncanonical or Windows-unsafe tar path')
        if part.split('.')[0].casefold() in RESERVED:
            raise ValueError('Reserved Windows tar path')
        part.encode('utf-8', errors='strict')
    if info.issym() or info.islnk() or not (info.isdir() or info.isfile()):
        raise ValueError('Tar link/special member rejected')
    if getattr(info, 'sparse', None) is not None or any(k.startswith('GNU.sparse') for k in info.pax_headers):
        raise ValueError('Sparse tar member rejected')
    if info.isdir() and info.size != 0:
        raise ValueError('Directory with payload rejected')
    return parts[1:]


def inspect_archive(path, guard):
    decoded = 0
    # Consume through gzip EOF: validates trailer CRC and ISIZE, not only tar end.
    with gzip.open(path, 'rb') as f:
        while True:
            guard()
            block = f.read(65536)
            if not block:
                break
            decoded += len(block)
            if decoded > DECODED_LIMIT:
                raise ValueError('Uncompressed registry limit exceeded')
    guard()
    seen = set()
    directories = set()
    implied_directories = set()
    entries = []
    inventory = []
    payload_bytes = 0
    last_end = 0
    members = 0
    with tarfile.open(path, 'r:gz') as tar:
        for info in tar:
            guard()
            members += 1
            if members > MEMBER_LIMIT:
                raise ValueError('Tar member limit exceeded')
            parts = safe_member(info)
            key = '/'.join(parts).casefold()
            if key in seen:
                raise ValueError('Duplicate/case-colliding tar member')
            seen.add(key)
            last_end = max(last_end, info.offset_data + ((info.size+511)//512)*512)
            if not parts:
                if not info.isdir():
                    raise ValueError('Archive root is not a directory')
                continue
            if info.isdir():
                directories.add(parts)
                continue
            if not 0 <= info.size <= FILE_LIMIT:
                raise ValueError('Single registry file limit exceeded')
            payload_bytes += info.size
            if payload_bytes > DECODED_LIMIT:
                raise ValueError('Registry payload limit exceeded')
            data = tar.extractfile(info).read()
            if len(data) != info.size:
                raise ValueError('Tar payload truncated')
            mode = b'100755' if info.mode & 0o111 else b'100644'
            entries.append((parts, mode, git_object(b'blob', data)))
            inventory.append({'path':'/'.join(parts), 'bytes':len(data),
                              'sha256':hashlib.sha256(data).hexdigest(), 'git_mode':mode.decode()})
            for count in range(1, len(parts)):
                implied_directories.add(parts[:count])
    if not entries or not any(row['path']=='Registry.toml' for row in inventory):
        raise ValueError('General Registry.toml is absent')
    if not directories.issubset(implied_directories):
        raise ValueError('Unexpected empty directory outside Git file tree')
    # The tar parser can stop at its terminator before the gzip stream ends.
    # Require at least two terminating zero blocks and no hidden trailing data.
    tail_bytes = 0
    with gzip.open(path, 'rb') as f:
        skipped = 0
        while skipped < last_end:
            guard()
            block = f.read(min(65536,last_end-skipped))
            if not block:
                raise ValueError('Tar data ends before final member')
            skipped += len(block)
        while True:
            guard()
            block = f.read(65536)
            if not block:
                break
            if any(block):
                raise ValueError('Nonzero data after final tar member')
            tail_bytes += len(block)
    if tail_bytes < 1024 or decoded % 512:
        raise ValueError('Missing/invalid tar terminating blocks')
    guard()
    actual_tree = tree_hash(entries)
    if actual_tree != TREE:
        raise ValueError('Full registry Git-tree mismatch')
    return {'gzip_CRC_ISIZE_EOF_verified':True, 'decoded_bytes':decoded,
            'tar_members':members, 'regular_files':len(entries), 'payload_bytes':payload_bytes,
            'tar_zero_tail_bytes':tail_bytes, 'git_tree':actual_tree,
            'links_special_sparse_members':0, 'filesystem_extractions':0}, inventory


def selected_transport(stats_path, headers_path):
    raw = {}
    for line in stats_path.read_text(encoding='utf-8', errors='replace').splitlines():
        key, sep, value = line.partition('=')
        if sep:
            raw[key] = value
    metadata = {}
    for key in ('response_code','num_redirects','ssl_verify_result'):
        metadata[key] = int(raw[key])
    for key in ('size_download','time_total','time_connect','time_appconnect'):
        value = float(raw[key])
        if not math.isfinite(value) or value < 0:
            raise ValueError('Invalid curl metric')
        metadata[key] = value
    effective = urlsplit(raw['url_effective'])
    metadata['effective_scheme'] = effective.scheme
    metadata['effective_host'] = effective.hostname
    # Never expose raw response headers, URL queries, certificates or addresses.
    statuses, hosts, lengths, encodings = [], [], [], []
    if headers_path.stat().st_size > 1_000_000:
        raise ValueError('Response-header limit exceeded')
    for line in headers_path.read_text(encoding='iso-8859-1').splitlines():
        if re.fullmatch(r'HTTP/\S+ [0-9]{3}(?: .*)?', line):
            statuses.append(int(line.split()[1]))
        key, sep, value = line.partition(':')
        if not sep:
            continue
        value = value.strip()
        if key.casefold() == 'location':
            host = urlsplit(value).hostname
            if host is not None:
                hosts.append(host)
        elif key.casefold() == 'content-length' and value.isdecimal():
            lengths.append(int(value))
        elif key.casefold() == 'transfer-encoding':
            encodings.append(value if re.fullmatch(r'[A-Za-z ,;-]+', value) else 'UNPARSED_PRIVATE')
    for host in [metadata['effective_host'], *hosts]:
        if host is None or not re.fullmatch(r'[A-Za-z0-9.-]+', host):
            raise ValueError('Invalid transport hostname')
    metadata.update(HTTP_statuses=statuses, redirect_hosts=hosts,
                    observed_content_lengths=lengths, observed_transfer_encodings=encodings)
    return metadata


def stop_owned(child):
    if child is None or child.poll() is not None:
        return {'termination_needed':False}
    record = {'termination_needed':True, 'pid':child.pid}
    try:
        proc = subprocess.run(['taskkill','/PID',str(child.pid),'/T','/F'], stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, timeout=15, creationflags=subprocess.CREATE_NO_WINDOW)
        record['tree_kill_exit_code'] = proc.returncode
        try:
            with (PRIVATE/'termination.log').open('ab') as f:
                f.write((utc()+'\n').encode()+proc.stdout)
        except BaseException as exc:
            record['termination_log_error'] = type(exc).__name__
    except BaseException as exc:
        record['tree_kill_error'] = type(exc).__name__
    if child.poll() is None:
        try:
            child.kill()
            child.wait(timeout=15)
        except BaseException as exc:
            record['parent_kill_error'] = type(exc).__name__
    record['owned_process_alive'] = child.poll() is None
    return record


def main():
    if sys.argv[1:] != ['--acquire-once']:
        raise ValueError('Explicit --acquire-once required')
    if PRIVATE.exists() or OUTPUT.exists():
        raise FileExistsError('Preserve an existing acquisition; no retry')
    PRIVATE.mkdir(parents=True)
    OUTPUT.mkdir(parents=True)
    started = time.perf_counter()
    deadline = started + 600
    receipt = {'status':'STARTED', 'started_utc':utc(), 'phase_limit_seconds':600,
               'source_sha256':digest(Path(__file__)), 'protocol_sha256':digest(PROTOCOL),
               'commit':COMMIT, 'expected_git_tree':TREE, 'curl_invocations':0,
               'Julia_invocations':0, 'Pkg_add_calls':0, 'model_builds':0, 'optimizer_calls':0,
               'automatic_retry':False, 'partial_file_continuation':False, 'TLS_bypass':False,
               'certificate_injection':False, 'extractions':0}
    write_new(OUTPUT/'started.json', receipt)

    def guard():
        if time.perf_counter() >= deadline:
            raise TimeoutError('Registry-only 600-second allocation exhausted')

    def stage(name):
        guard()
        receipt['stage'] = name
        event = {'stage':name, 'utc':utc(), 'elapsed_seconds':time.perf_counter()-started}
        with (OUTPUT/'stages.jsonl').open('a', encoding='utf-8') as f:
            f.write(json.dumps(event)+'\n'); f.flush()
        print(json.dumps(event), flush=True)

    archive = PRIVATE/'General.tar.gz'
    child = None
    try:
        stage('check_preserved_partial_and_curl')
        if digest(OLD_PARTIAL) != OLD_SHA:
            raise ValueError('Closed attempt02 archive changed')
        receipt['preserved_partial_sha256'] = OLD_SHA
        curl = Path(os.environ.get('SystemRoot', 'C:/Windows'))/'System32/curl.exe'
        if not curl.is_file():
            raise FileNotFoundError('Normal Windows curl is absent')
        receipt['curl_executable_sha256'] = digest(curl)
        fields = ('response_code','url_effective','size_download','num_redirects','ssl_verify_result',
                  'time_total','time_connect','time_appconnect')
        write_out = ''.join(key+'=%{'+key+'}\n' for key in fields)
        headers = PRIVATE/'headers.txt'
        stats = PRIVATE/'transfer_metrics.txt'
        stderr = PRIVATE/'curl_stderr.txt'
        stage('one_normal_TLS_curl_download')
        guard()
        curl_limit = max(1, math.floor(deadline-time.perf_counter()))
        cmd = [str(curl), '--disable', '--location', '--max-redirs', '5', '--retry', '0',
               '--connect-timeout', '30', '--max-time', str(curl_limit), '--max-filesize',str(COMPRESSED_LIMIT),
               '--proto', '=https', '--proto-redir', '=https', '--silent','--show-error','--fail-with-body',
               '--dump-header',str(headers),'--output',str(archive),'--write-out',write_out,URL]
        receipt['configured_curl_seconds'] = curl_limit
        with stats.open('xb') as cout, stderr.open('xb') as cerr:
            try:
                guard()
                child = subprocess.Popen(cmd, cwd=PRIVATE, stdout=cout, stderr=cerr,
                                         creationflags=subprocess.CREATE_NO_WINDOW)
                receipt.update(curl_invocations=1, curl_pid=child.pid, curl_started_utc=utc())
                write_new(OUTPUT/'curl_launch.json', {'pid':child.pid,'started_utc':receipt['curl_started_utc'],
                          'command':cmd,'source_sha256':receipt['source_sha256']})
                child.wait(timeout=max(0.001,deadline-time.perf_counter()))
                receipt.update(curl_exit_code=child.returncode, curl_ended_utc=utc())
            finally:
                receipt['owned_process_cleanup'] = stop_owned(child)
        if stats.exists() and stats.stat().st_size:
            receipt['transport'] = selected_transport(stats, headers)
        if child.returncode != 0:
            raise RuntimeError('Curl transfer failed; private diagnostics preserved')
        metadata = receipt['transport']
        if metadata['response_code'] != 200 or metadata['ssl_verify_result'] != 0 or metadata['effective_scheme'] != 'https':
            raise ValueError('Transport did not meet HTTPS/HTTP200 admission conditions')
        if not 0 < archive.stat().st_size <= COMPRESSED_LIMIT:
            raise ValueError('Compressed archive size outside fixed limit')
        if metadata['size_download'] != archive.stat().st_size:
            raise ValueError('Curl/disk byte count mismatch')
        receipt.update(archive_bytes=archive.stat().st_size, archive_sha256=digest(archive))
        stage('gzip_tar_and_exact_Git_tree_validation')
        validation, inventory = inspect_archive(archive, guard)
        write_new(OUTPUT/'registry_file_inventory.json', {'commit':COMMIT,'git_tree':TREE,'files':inventory})
        receipt['validation'] = validation
        guard()
        if digest(OLD_PARTIAL) != OLD_SHA or digest(Path(__file__)) != receipt['source_sha256'] or digest(PROTOCOL) != receipt['protocol_sha256']:
            raise ValueError('Preserved input/source/protocol changed')
        receipt.update(status='READY_PINNED_REGISTRY_ARCHIVE_ONLY', preserved_inputs_unchanged=True)
    except BaseException as exc:
        receipt.update(status='ACQUISITION_FAILED_PRESERVED_NO_RETRY', exception_type=type(exc).__name__,
                       message=str(exc)[:500])
    finally:
        if child is not None and child.poll() is None:
            receipt['final_owned_process_cleanup'] = stop_owned(child)
    if archive.exists():
        receipt.update(archive_bytes=archive.stat().st_size, archive_sha256=digest(archive))
    receipt.update(ended_utc=utc(),elapsed_seconds=time.perf_counter()-started,
                   allocation_overrun_seconds=max(0,time.perf_counter()-deadline))
    receipt['private_artifacts'] = [{'path':p.name,'bytes':p.stat().st_size,'sha256':digest(p)}
                                   for p in sorted(PRIVATE.iterdir()) if p.is_file()]
    receipt['public_artifacts'] = [{'path':p.name,'bytes':p.stat().st_size,'sha256':digest(p)}
                                  for p in sorted(OUTPUT.iterdir()) if p.is_file()]
    receipt['private_diagnostics_publication'] = 'EXCLUDED_PENDING_SAFETY_REVIEW'
    write_new(OUTPUT/'receipt.json', receipt)
    print(json.dumps({key:receipt[key] for key in ('status','stage','elapsed_seconds','curl_invocations',
                                                  'Julia_invocations','optimizer_calls')}), flush=True)
    return 0 if receipt['status']=='READY_PINNED_REGISTRY_ARCHIVE_ONLY' else 1


if __name__ == '__main__':
    sys.exit(main())
