"""Extract the already verified final20 ZIP into one fresh external replay root."""
from pathlib import Path, PurePosixPath
import csv
import hashlib
import io
import json
import re
import stat
import zipfile

DELIVERY = Path(__file__).resolve().parent
ARCHIVE = DELIVERY / 'DSC_Temporal_Research_2026-09-27_Final.zip'
DESTINATION = Path('C:/Users/gmalkawi/.codex/research-replays/unrestricted-energy-final20-20260927')
PACKAGE = DESTINATION / 'package'
ZIP_SHA = 'e4d9b181668a68b0f7db1c0cc8c30182ac56c0a461c1dbd5a37fb63d933a6aa9'
OUTER_SHA = '4c9f6db4561470775c5e567956c48825de44a6700b0cdcd1607ca50770089409'
COMMIT = '3f51758b521967739131701b106be60036a3fdd4'
sha = lambda b: hashlib.sha256(b).hexdigest()

def no_links(path):
    path = Path(path).absolute()
    for part in [path, *path.parents]:
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        assert not stat.S_ISLNK(info.st_mode), 'Symlink in preparation path'
        assert not (getattr(info, 'st_file_attributes', 0) & 0x400), 'Reparse point in preparation path'

no_links(ARCHIVE)
no_links(DESTINATION)
no_links(PACKAGE)

assert not DESTINATION.exists(), 'Preparation destination must be new'
assert DESTINATION.resolve().parent == Path('C:/Users/gmalkawi/.codex/research-replays').resolve()
assert ARCHIVE.stat().st_size == 127416288 and sha(ARCHIVE.read_bytes()) == ZIP_SHA
with zipfile.ZipFile(ARCHIVE) as zipped:
    infos = zipped.infolist()
    names = [entry.filename for entry in infos]
    folded_names = {name.casefold() for name in names}
    assert len(names) == 4816 and len(set(names)) == len(names)
    assert len(folded_names) == len(names)
    for entry in infos:
        name = entry.filename
        path = PurePosixPath(name)
        assert name and path.parts and not path.is_absolute() and '..' not in path.parts
        assert ':' not in name and '\\' not in name and path.as_posix() == name
        assert all(part.rstrip(' .') == part and part not in {'.', '..'} for part in path.parts)
        assert not any(re.fullmatch(r'CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9]',
                                   part.split('.')[0], re.IGNORECASE) for part in path.parts)
        assert not any(parent.as_posix().casefold() in folded_names
                       for parent in path.parents if parent.as_posix() != '.')
        assert not entry.is_dir() and not stat.S_ISLNK(entry.external_attr >> 16)
        assert (PACKAGE / name).resolve().is_relative_to(PACKAGE.resolve())
    outer = zipped.read('FILE_MANIFEST.csv')
    assert sha(outer) == OUTER_SHA
    reader = csv.DictReader(io.StringIO(outer.decode('utf-8')))
    assert reader.fieldnames == ['path', 'bytes', 'sha256']
    records = list(reader)
    assert len(records) == 4815 and len({r['path'] for r in records}) == 4815
    assert {r['path'] for r in records} | {'FILE_MANIFEST.csv'} == set(names)
    expected = {r['path']: r for r in records}
    assert json.loads(zipped.read('PACKAGE_PROVENANCE.json'))['git_commit'] == COMMIT
    DESTINATION.mkdir()
    PACKAGE.mkdir()
    no_links(PACKAGE)
    for entry in infos:
        data = zipped.read(entry)  # The ZIP reader also checks each member CRC.
        if entry.filename != 'FILE_MANIFEST.csv':
            record = expected[entry.filename]
            assert len(data) == int(record['bytes']) and sha(data) == record['sha256']
        target = PACKAGE / entry.filename
        target.parent.mkdir(parents=True, exist_ok=True)
        no_links(target)
        with target.open('xb') as stream:
            stream.write(data)

assert {p.relative_to(PACKAGE).as_posix() for p in PACKAGE.rglob('*') if p.is_file()} == set(names)
for path in PACKAGE.rglob('*'):
    no_links(path)
for name, record in expected.items():
    data = (PACKAGE / name).read_bytes()
    assert len(data) == int(record['bytes']) and sha(data) == record['sha256']
assert sha((PACKAGE / 'FILE_MANIFEST.csv').read_bytes()) == OUTER_SHA
receipt = dict(status='UNCHANGED_FINAL20_PACKAGE_EXTRACTED_AND_VERIFIED',
               archive_sha256=ZIP_SHA, outer_manifest_sha256=OUTER_SHA,
               evidence_commit=COMMIT, package_root=str(PACKAGE),
               payload_files=4815, complete_files=4816, scientific_computations=0,
               producer_imports=0, optimizer_calls=0, network_calls=0,
               source_sha256=sha(Path(__file__).read_bytes()))
with (DESTINATION / 'PREPARATION.json').open('x', encoding='utf-8') as stream:
    json.dump(receipt, stream, indent=2)
    stream.write('\n')
print(json.dumps(receipt), flush=True)
