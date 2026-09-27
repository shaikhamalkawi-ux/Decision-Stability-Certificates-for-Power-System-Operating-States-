import argparse, csv, hashlib, io, json, re, subprocess, zipfile
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone

def sha(b): return hashlib.sha256(b).hexdigest()
def safe(s):
    p=PurePosixPath(s)
    assert s and not p.is_absolute() and s==p.as_posix() and '\\' not in s and ':' not in s
    assert all(x not in ('','.','..') and not x.endswith((' ','.')) for x in p.parts)
    assert not any(re.fullmatch(r'(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?',x) for x in p.parts)
    return p

a=argparse.ArgumentParser()
a.add_argument('--expected-commit',required=True)
a.add_argument('--output-dir',required=True)
a.add_argument('--repository-root',required=True)
a=a.parse_args()
source_bytes=Path(__file__).read_bytes()
root=Path(a.repository_root).resolve()
assert re.fullmatch('[0-9a-f]{40}',a.expected_commit)
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()==a.expected_commit
assert subprocess.check_output(['git','rev-parse','HEAD^'],cwd=root,text=True).strip()=='3f51758b521967739131701b106be60036a3fdd4'
assert not subprocess.check_output(['git','diff','--name-only'],cwd=root)
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=root)
mrel='results/research8h/verified_checkpoint21_manifest.csv'
manifest=(root/mrel).read_bytes()
rows=list(csv.DictReader(io.StringIO(manifest.decode('utf-8-sig'))))
assert rows and all(set(r)=={'path','bytes','sha256'} for r in rows)
paths=[r['path'] for r in rows]+[mrel]
assert len(paths)==len(set(paths))==len(set(p.casefold() for p in paths))
for s in paths:
    safe(s)
    assert s.startswith(('docs/research8h/','reproducibility/','results/research8h/'))
    p=root/s
    assert p.is_file() and not p.is_symlink()
    assert not getattr(p.lstat(),'st_file_attributes',0)&0x400
    for parent in p.parents:
        assert not parent.is_symlink() and not getattr(parent.lstat(),'st_file_attributes',0)&0x400
        if parent==root: break
        assert root in parent.parents
changed=subprocess.check_output(['git','diff','--name-status','HEAD^','HEAD'],cwd=root,text=True).splitlines()
assert set(changed)=={'A\t'+p for p in paths}
records=rows+[{'path':mrel,'bytes':str(len(manifest)),'sha256':sha(manifest)}]
requests=''.join(a.expected_commit+':'+r['path']+'\n' for r in records).encode()
raw=subprocess.run(['git','cat-file','--batch'],cwd=root,input=requests,capture_output=True,check=True).stdout
cursor=0; payloads=[]
for r in records:
    end=raw.index(b'\n',cursor); h=raw[cursor:end].split()
    assert len(h)==3 and h[1]==b'blob'
    n=int(h[2]); b=raw[end+1:end+1+n]; cursor=end+n+2
    assert n==int(r['bytes']) and sha(b)==r['sha256'] and b==(root/r['path']).read_bytes()
    payloads.append((r['path'],b))
assert cursor==len(raw)
out=Path(a.output_dir).absolute()
for p in [out,*out.parents]:
    if p.exists(): assert not p.is_symlink() and not getattr(p.lstat(),'st_file_attributes',0)&0x400
assert out.parent.is_dir()
out.mkdir(exist_ok=False)
archive=out/'DSC_Unrestricted_Energy_Replay_Supplement_2026-09-27.zip'
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for name,b in payloads: z.writestr(name,b)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert z.namelist()==[p for p,b in payloads]
    for name,b in payloads: assert z.read(name)==b
assert all((root/n).read_bytes()==b for n,b in payloads)
assert Path(__file__).read_bytes()==source_bytes
data=archive.read_bytes()
record={'status':'SUPPLEMENT_GIT_AND_ZIP_BYTES_VERIFIED','utc':datetime.now(timezone.utc).isoformat(),
 'commit':a.expected_commit,'base_package_commit':'3f51758b521967739131701b106be60036a3fdd4',
 'base_package_sha256':'e4d9b181668a68b0f7db1c0cc8c30182ac56c0a461c1dbd5a37fb63d933a6aa9',
 'manifest_sha256':sha(manifest),'payloads':len(rows),'zip_members':len(payloads),
 'archive':archive.name,'bytes':len(data),'sha256':sha(data),
 'self_sha256':sha(Path(__file__).read_bytes()),'source_unchanged':True,
 'optimizer_calls':0,'mathematical_replay':False,'main_package_modified':False,
 'verification':'Exact additive Git blobs, file sizes and SHA256; ZIP CRC, exact inventory and member bytes.'}
(out/'SUPPLEMENT_VERIFICATION.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record))
