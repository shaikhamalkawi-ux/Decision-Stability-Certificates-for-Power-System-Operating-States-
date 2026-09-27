"""Invented source-cache control only; never open a scientific bundle."""
from pathlib import Path
import argparse
import ast
import hashlib
import importlib.util
import json
import os
import py_compile
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
DEV = Path(__file__).resolve().parent

def digest(data):
    return hashlib.sha256(data).hexdigest()

def load_source(path, name):
    source = path.read_bytes()
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    exec(compile(source, str(path), 'exec'), module.__dict__)
    return module

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture-dir', required=True)
    parser.add_argument('--report', required=True)
    args = parser.parse_args()
    fixture = Path(args.fixture_dir).resolve()
    report = Path(args.report).resolve()
    assert fixture.is_relative_to((ROOT / '.work').resolve()) and not fixture.exists()
    assert report.parent == DEV and not report.exists()
    fixture.mkdir(parents=True)
    source_path = ROOT / 'src/researchnext_portable_state_cut.py'
    current = source_path.read_bytes()
    previous = (DEV / 'pre_review_source.py').read_bytes()
    assert digest(previous) == 'c8d79c7e477f1d8f8ae9f3f41193a936cdbf869177199e4dbf866878554618b6'
    def reconstruct_ast(blob):
        return ast.dump(next(n for n in ast.parse(blob).body if isinstance(n, ast.FunctionDef) and n.name == 'reconstruct'), include_attributes=False)
    assert reconstruct_ast(current) == reconstruct_ast(previous)
    producer = load_source(source_path, 'invented_portable_verifier_control')
    good = fixture / 'invented_decoder.py'
    other = fixture / 'invented_alternate.py'
    good.write_bytes(b"MARKER = 'source'\n")
    other.write_bytes(b"MARKER = 'cached'\n")
    stamp = 1700000000
    os.utime(good, (stamp, stamp))
    os.utime(other, (stamp, stamp))
    assert good.stat().st_size == other.stat().st_size
    cached = Path(importlib.util.cache_from_source(str(good)))
    py_compile.compile(str(other), cfile=str(cached), dfile=str(good), doraise=True,
                       invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
    frozen = {p: p.read_bytes() for p in (good, other, cached)}
    expected = digest(frozen[good])
    spec = importlib.util.spec_from_file_location('invented_legacy_loader', good)
    legacy = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = legacy
    spec.loader.exec_module(legacy)
    assert legacy.MARKER == 'cached', 'Control must reproduce bytecode-cache loading despite dont_write_bytecode'
    safe = producer.load_verified_source(good, expected, 'invented_verified_loader')
    assert safe.MARKER == 'source', 'Reviewed loader must execute the captured verified source'
    rejected = False
    try:
        producer.load_verified_source(good, '0' * 64, 'invented_bad_digest')
    except ValueError:
        rejected = True
    assert rejected and 'invented_bad_digest' not in sys.modules
    assert all(p.read_bytes() == b for p, b in frozen.items())
    assert source_path.read_bytes() == current
    result = dict(status='PASS_INVENTED_STALE_CACHE_CONTROL', source_sha256=digest(current),
                  control_source_sha256=digest(Path(__file__).read_bytes()),
                  preserved_source_sha256=digest(previous), mathematical_reconstruct_ast_unchanged=True,
                  legacy_loader_read_cached_marker=True, verified_loader_read_source_marker=True,
                  wrong_source_digest_rejected_before_module_execution=True,
                  source_and_fixture_bytes_unchanged=True, scientific_files_read=0,
                  scientific_replays=0, optimizer_calls=0,
                  scope='One invented source/cache substitution plus digest rejection; no scientific certificate or decoder executed.',
                  fixtures=[dict(path=str(p.relative_to(ROOT)).replace('\\','/'), sha256=digest(b), bytes=len(b)) for p,b in frozen.items()])
    with report.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
