import csv, hashlib, io, json, os, stat, time, zipfile
from pathlib import Path, PurePosixPath
ROOT = Path(r'C:/Users/gmalkawi/.codex/worktrees/dsc-temporal-information/3')
PREP = ROOT/'.work/portable_new_results_candidate01'
PKG = PREP/'package'
OUT = ROOT/'results/research8h/portable_new_results_independent_review'
EXPECTED = {'freeze':'0b02331d14718871d30a7c0f933f07047f851459dbdfa09b4202714b76111c89','base':'495dcd6831ddbcd1c8263b32a536d5d9ff7ef2943fe54250c1c5532359e366d7','candidate':'d098c9b6154fcfa02645c1395d55e338fb04fb3c4ef7dd9bad35548463d01ad9','manifest':'4fbe3109b23ce965c13cc1f26bce12f99e4aad65e52c93ec51bc670d753a9534'}
ADDITIONS={'reproducibility/replay_new_closed_results.py':'073d04a21dac59fc34926912ac3a58b6399b32e40017584047828608a5606b51','docs/research8h/PORTABLE_NEW_RESULTS_REPLAY_PROTOCOL.md':'72093987ce0d0ea421ed5238e1cad8a977c233b1b26953610569f44b72e82df2'}
def require(v,s):
    if not v: raise ValueError(s)
def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()
def data_sha(data): return hashlib.sha256(data).hexdigest()
def name(s):
    require(isinstance(s,str) and s and '\\' not in s and ':' not in s,'Unsafe archive path')
    p=PurePosixPath(s)
    require(not p.is_absolute() and '..' not in p.parts and str(p)==s,'Noncanonical archive path')
    return s
def manifest(data):
    reader=csv.DictReader(io.StringIO(data.decode('utf-8-sig')))
    require(len(reader.fieldnames or [])==3 and set(reader.fieldnames)=={'path','sha256','bytes'},'Manifest columns')
    result={}
    for r in reader:
        n=name(r['path']); require(n not in result,'Duplicate manifest path')
        require(len(r['sha256'])==64 and all(c in '0123456789abcdef' for c in r['sha256']),'Invalid digest')
        result[n]=(r['sha256'],int(r['bytes']))
    return result
def zip_records(path):
    result={}
    with zipfile.ZipFile(path) as z:
        seen=set()
        for i in z.infolist():
            n=name(i.filename[:-1] if i.is_dir() else i.filename)
            require(n not in seen,'Duplicate ZIP entry');seen.add(n)
            mode=i.external_attr>>16; flags=i.external_attr&65535; kind=stat.S_IFMT(mode)
            require(not stat.S_ISLNK(mode) and not (flags & 0x400),'ZIP link/reparse')
            require(kind in (0,stat.S_IFDIR,stat.S_IFREG),'ZIP special file')
            if i.is_dir(): continue
            b=z.read(i); result[n]=(data_sha(b),len(b))
        m=z.read('FILE_MANIFEST.csv')
    return result,m
start=time.perf_counter()
require(digest(PREP/'prepared_freeze.json')==EXPECTED['freeze'],'Freeze digest')
f=json.loads((PREP/'prepared_freeze.json').read_text())
base=Path(f['base_zip']); candidate=Path(f['candidate_zip'])
require(digest(base)==EXPECTED['base'] and base.stat().st_size==88756097,'Base ZIP identity')
require(digest(candidate)==EXPECTED['candidate'] and candidate.stat().st_size==67347208,'Candidate ZIP identity')
base_files,base_csv=zip_records(base); new_files,new_csv=zip_records(candidate)
bm=manifest(base_csv); nm=manifest(new_csv)
require(len(bm)==3501 and len(nm)==3503,'Payload denominator')
require(data_sha(base_csv)==f['base_manifest_sha256'] and data_sha(new_csv)==EXPECTED['manifest'],'Manifest identities')
require(set(base_files)==set(bm)|{'FILE_MANIFEST.csv'},'Base inventory')
require(set(new_files)==set(nm)|{'FILE_MANIFEST.csv'},'Candidate ZIP inventory')
require(all(base_files[n]==v for n,v in bm.items()),'Base payload hashes')
require(all(new_files[n]==v for n,v in nm.items()),'Candidate ZIP payload hashes')
require(set(nm)-set(bm)==set(ADDITIONS) and set(bm)<=set(nm),'Exactly two new payloads')
require(all(nm[n]==v for n,v in bm.items()),'Base preservation')
for n,d in ADDITIONS.items(): require(nm[n][0]==d and digest(ROOT/n)==d,'Reviewed new source differs')
files={}; directories=0
for ancestor in [PKG,*list(PKG.parents)[:3]]:
    s=ancestor.lstat();require(not stat.S_ISLNK(s.st_mode) and not (getattr(s,'st_file_attributes',0)&0x400),'Package component link')
for current, dirs, leaves in os.walk(PKG,followlinks=False):
    for leaf in dirs+leaves:
        p=Path(current)/leaf;s=p.lstat()
        require(not stat.S_ISLNK(s.st_mode) and not (getattr(s,'st_file_attributes',0)&0x400),'Extracted link/reparse')
        require(stat.S_ISDIR(s.st_mode) or stat.S_ISREG(s.st_mode),'Extracted special file')
        require(p.resolve().is_relative_to(PKG.resolve()),'Extracted escape')
        if stat.S_ISDIR(s.st_mode):directories+=1
        else:files[p.relative_to(PKG).as_posix()]=(digest(p),s.st_size)
require(files==new_files,'Extracted inventory/payload mismatch')
report=ROOT/'results/research8h/portable_new_closed_replay/checkpoint05_candidate01'
require(not report.exists() and not report.resolve().is_relative_to(PKG.resolve()) and not PKG.resolve().is_relative_to(report.resolve()),'New external report path')
require(not f['wrapper_imported'] and not f['synthetic_checks_run'] and not f['mathematical_replay_called'] and not f['optimizer_calls'],'Preparation execution scope')
require(digest(base)==EXPECTED['base'] and digest(candidate)==EXPECTED['candidate'] and digest(PREP/'prepared_freeze.json')==EXPECTED['freeze'],'Final bindings')
result=dict(status='INDEPENDENT_PORTABLE_NEW_PREPARED_PASS',base_payloads=3501,candidate_payloads=3503,total_files=len(files),directories=directories,all_base_payload_hashes_preserved=True,exact_two_reviewed_additions=True,all_zip_and_filesystem_links_reparse_specialfiles_rejected=True,all_payloads_and_inventories_checked=True,base_sha256=EXPECTED['base'],candidate_sha256=EXPECTED['candidate'],outer_manifest_sha256=EXPECTED['manifest'],freeze_sha256=EXPECTED['freeze'],new_external_report_path=str(report),wrapper_imports=0,mathematical_replays=0,optimizer_calls=0,elapsed_s=time.perf_counter()-start)
OUT.mkdir(exist_ok=True)
with (OUT/'prepared_review.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result))
