"""Preparation only. Copy verified bytes; never import replay or run model math."""
from pathlib import Path,PurePosixPath
import csv,hashlib,io,json,os,re,stat,subprocess,time,zipfile
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.work/research8h_delivery/DSC_Temporal_Research_2026-09-27_Checkpoint05.zip'
BASE_SHA='495dcd6831ddbcd1c8263b32a536d5d9ff7ef2943fe54250c1c5532359e366d7';BASE_BYTES=88756097
COMMIT='579ecf20452b7838fdc5802744b24f597af5e1c7'
PREFIXES=('src/','docs/','results/','reproducibility/')
OUT=Path('C:/Users/gmalkawi/.codex/research-replays/strict-flow-20260927-candidate01')
PACKAGE=OUT/'package';ZIP=OUT/'strict_flow_candidate01.zip'
ADDITIONS={
 'reproducibility/replay_strict_flow.py':'52dbe3b74c1709a36ab23b31768a8e1f1c24a1daa00df2abba7b03bd2e96fad7',
 'docs/research8h/PORTABLE_STRICT_FLOW_REPLAY_PROTOCOL.md':'7d619dc7c7e7bb76da71dd7ee2496f507875bbd5ed0fb356e50417791e66557a'}
OLD_ROOT='C:/Users/gmalkawi/.codex/worktrees/dsc-temporal-information/3'
OLD_NATIVE='C:/Users/gmalkawi/.codex/worktrees/dsc-v8r1-evidence/3/.work/v8r1_rts_inputs'
NATIVE='reproducibility/native_sources'
MANIFESTS=(
 ('results/research8h/branch_flow_encoding/input_manifest.json','0981491f326dbd3f34e2825d501cbff54d74bf18e5c3d924edf420a4950532d4',103,'historical',''),
 ('results/research8h/branch_flow_encoding/artifact_manifest.csv','a86ee29993a253e7018965cf9ce66dc177e220129eba849a4529960a09e237c4',277,'relative',''),
 ('results/research8h/branch_flow_strict_energy/input_manifest.json','7ffffe82e6046daff5dcd610337c2e8cb333009c38ec9acfcdb9741f8cbadbb7',355,'historical',''),
 ('results/research8h/branch_flow_strict_energy/artifact_manifest.csv','89475add4fdc688cf7227a201fa870712602cc67269b0ad7bacdfa7f8ef65648',466,'relative',''),
 (NATIVE+'/FILE_MANIFEST.csv','8b18311c646c0ae68d85765c57b690e2db5b5ffc071d1ab1b734b2db88d866b8',24,'relative',NATIVE))

def need(v,message):
 if not v:raise ValueError(message)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
def no_link(p):
 s=os.lstat(p);need(not stat.S_ISLNK(s.st_mode) and not(getattr(s,'st_file_attributes',0)&0x400),'Link/reparse: '+str(p))
def safe_components(p):
 for q in reversed((p.absolute(),*p.absolute().parents)):
  if q.exists() or q.is_symlink():no_link(q)
def name(value):
 need(type(value) is str and value and '\\' not in value and ':' not in value,'Invalid package path')
 p=PurePosixPath(value);need(not p.is_absolute() and '..' not in p.parts and str(p)==value and value!='.','Noncanonical/escaping path')
 for part in p.parts:
  need(part.rstrip(' .')==part,'Windows ambiguous component')
  need(part.split('.')[0].upper() not in {'CON','PRN','AUX','NUL',*(f'COM{i}' for i in range(1,10)),*(f'LPT{i}' for i in range(1,10))},'Windows reserved component')
 return value
def zip_index(z):
 entries={};folded=set()
 for entry in z.infolist():
  need(not entry.is_dir(),'Unexpected directory ZIP entry');n=name(entry.filename)
  need(n.casefold() not in folded,'Duplicate/casefold ZIP path');folded.add(n.casefold())
  need(stat.S_IFMT(entry.external_attr>>16) in (0,stat.S_IFREG) and not(entry.external_attr&0x400),'Special/link ZIP entry')
  need(not(entry.flag_bits&1) and entry.compress_type in (zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED),'Encrypted/unsupported ZIP entry');entries[n]=entry
 for n in entries:need(not any(str(p) in entries for p in PurePosixPath(n).parents if str(p)!='.'),'File/ancestor collision')
 return entries
def table(data,is_json=False):
 if is_json:rows=json.loads(data.decode('utf-8-sig'))
 else:
  reader=csv.DictReader(io.StringIO(data.decode('utf-8-sig')));need(len(reader.fieldnames or [])==3 and set(reader.fieldnames)=={'path','sha256','bytes'},'Manifest header');rows=list(reader)
 need(type(rows) is list and rows,'Manifest list');seen=set()
 for r in rows:
  need(set(r)=={'path','sha256','bytes'} and re.fullmatch('[0-9a-f]{64}',r['sha256']) and str(r['bytes']).isdigit(),'Manifest schema')
  n=r['path'].replace('\\','/');need(n.casefold() not in seen,'Duplicate manifest path');seen.add(n.casefold())
 return rows
def inventory():
 found={};folded=set();directories=0
 for d,ds,fs in os.walk(PACKAGE,followlinks=False):
  no_link(Path(d));directories+=1
  for s in ds:no_link(Path(d)/s)
  for f in fs:
   p=Path(d)/f;no_link(p);need(stat.S_ISREG(p.stat().st_mode),'Nonregular payload');n=name(p.relative_to(PACKAGE).as_posix())
   need(n.casefold() not in folded,'Casefold filesystem collision');folded.add(n.casefold());found[n]=dict(path=n,sha256=sha(p),bytes=p.stat().st_size)
 return found,directories
def save(file,data):
 with (OUT/file).open('x',encoding='utf-8') as f:json.dump(data,f,indent=2,allow_nan=False);f.write('\n')
def write_payload(n,data,replace=False):
 n=name(n);p=PACKAGE/n;need(p.resolve().is_relative_to(PACKAGE.resolve()),'Escaping destination')
 p.parent.mkdir(parents=True,exist_ok=True);safe_components(p.parent)
 if p.exists():need(replace,'Unexpected existing payload');no_link(p)
 with p.open('wb' if replace else 'xb') as f:f.write(data)
 return dict(path=n,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def git_overlay():
 tree=[]
 for entry in git('ls-tree','-r','-z',COMMIT).split(b'\0'):
  if not entry:continue
  meta,path=entry.split(b'\t',1);mode,kind,oid=meta.decode('ascii').split();n=path.decode('utf-8')
  if not n.startswith(PREFIXES):continue
  name(n);need(kind=='blob' and mode in ('100644','100755'),'Nonregular research Git entry');tree.append((n,oid))
 need(tree and len({n.casefold() for n,_ in tree})==len(tree),'Empty/colliding Git overlay');return sorted(tree)
def closure(expected):
 verified={};bindings={};queue=list(MANIFESTS)
 def remap(n):
  n=n.replace('\\','/')
  for old,new in ((OLD_NATIVE,NATIVE+'/rts_inputs'),(OLD_ROOT,'')):
   if n.startswith(old+'/'):
    tail=name(n[len(old)+1:]);return name(new+'/'+tail if new else tail)
  raise ValueError('Unmapped historical path: '+n)
 while queue:
  path,digest,count,mode,base=queue.pop(0)
  if path in verified:need(verified[path]['sha256']==digest,'Conflicting recursive manifest digest');continue
  need(path in expected and expected[path]['sha256']==digest,'Missing/changed historical manifest: '+path)
  rows=table((PACKAGE/path).read_bytes(),path.endswith('.json'))
  if count is not None:need(len(rows)==count,'Historical manifest count')
  local=set()
  for r in rows:
   n=remap(r['path']) if mode=='historical' else name((base+'/' if base else '')+name(r['path'].replace('\\','/')))
   need(n not in local,'Historical alias collision');local.add(n)
   value=(int(r['bytes']),r['sha256']);need(n in expected and (expected[n]['bytes'],expected[n]['sha256'])==value,'Missing/conflicting portable dependency: '+n)
   need(n not in bindings or bindings[n]==value,'Conflicting provenance alias');bindings[n]=value
   if PurePosixPath(n).name in ('input_manifest.csv','input_manifest.json'):queue.append((n,r['sha256'],None,'historical',''))
  verified[path]=dict(sha256=digest,entries=len(rows),mode=mode,base=base)
 return verified,bindings
def main():
 started=time.perf_counter();safe_components(BASE);safe_components(OUT)
 need(not OUT.exists(),'Fresh external candidate directory already exists');need(not OUT.resolve().is_relative_to(ROOT.resolve()),'Candidate must be outside worktree')
 need(BASE.stat().st_size==BASE_BYTES and sha(BASE)==BASE_SHA,'Wrong immutable Drive05 ZIP')
 need(git('rev-parse','--verify',COMMIT).decode().strip()==COMMIT,'Published Git17 commit unavailable')
 for n,h in ADDITIONS.items():safe_components(ROOT/n);need(sha(ROOT/n)==h,'Reviewed source/protocol changed')
 overlay=git_overlay();OUT.mkdir(parents=True);PACKAGE.mkdir()
 save('preparation_started.json',dict(utc=datetime.now(timezone.utc).isoformat(),base_sha256=BASE_SHA,evidence_commit=COMMIT,overlay_prefixes=PREFIXES,overlay_files=len(overlay),reviewed_additions=ADDITIONS,wrapper_imported=False,mathematical_replay=False,optimizer_calls=0))
 (OUT/'preparation_builder.py').write_bytes(Path(__file__).read_bytes())
 with zipfile.ZipFile(BASE) as z:
  index=zip_index(z);raw=z.read('FILE_MANIFEST.csv');original={name(r['path']):dict(path=name(r['path']),sha256=r['sha256'],bytes=int(r['bytes'])) for r in table(raw)}
  need(len(original)==3501 and set(index)==set(original)|{'FILE_MANIFEST.csv'},'Base inventory mismatch');(OUT/'base_FILE_MANIFEST.csv').write_bytes(raw)
  expected={}
  for n,r in original.items():
   data=z.read(n);need(len(data)==r['bytes'] and hashlib.sha256(data).hexdigest()==r['sha256'],'Base member mismatch: '+n);expected[n]=write_payload(n,data)
 overlay_records=[];process=subprocess.Popen(['git','cat-file','--batch'],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 try:
  for n,oid in overlay:
   process.stdin.write((oid+'\n').encode('ascii'));process.stdin.flush();header=process.stdout.readline().decode('ascii').strip().split();need(len(header)==3 and header[:2]==[oid,'blob'],'Git batch header')
   size=int(header[2]);data=process.stdout.read(size);need(len(data)==size and process.stdout.read(1)==b'\n','Truncated Git blob')
   need(hashlib.sha1(b'blob '+str(size).encode()+b'\0'+data).hexdigest()==oid,'Git blob object check')
   newsha=hashlib.sha256(data).hexdigest();previous=expected.get(n)
   if n.startswith(NATIVE+'/'):need(previous is not None and previous['sha256']==newsha,'Native addendum changed in Git overlay')
   if previous is None or previous['sha256']!=newsha:expected[n]=write_payload(n,data,replace=previous is not None)
   overlay_records.append(dict(path=n,git_blob=oid,sha256=newsha,bytes=size,previous_sha256=previous['sha256'] if previous else None,changed=previous is None or previous['sha256']!=newsha))
  process.stdin.close();need(process.wait()==0,'Git batch process failed')
 finally:
  if process.poll() is None:process.terminate();process.wait()
 save('git17_overlay.json',dict(commit=COMMIT,prefixes=PREFIXES,files=overlay_records,all_blob_objects_verified=True))
 for n,h in ADDITIONS.items():
  need(n not in expected,'Reviewed addition already in science/base payload');data=(ROOT/n).read_bytes();need(hashlib.sha256(data).hexdigest()==h,'Source changed');expected[n]=write_payload(n,data)
 metadata=dict(schema='strict-flow-candidate-v1',evidence_commit=COMMIT,scope='strict-flow-capped-and-uncapped-v1')
 expected['STRICT_FLOW_CANDIDATE.json']=write_payload('STRICT_FLOW_CANDIDATE.json',(json.dumps(metadata,indent=2)+'\n').encode('utf-8'))
 verified,bindings=closure(expected);save('recursive_manifest_closure.json',dict(status='COMPLETE_RECURSIVE_MANIFEST_CLOSURE',manifests=verified,unique_bound_payloads=len(bindings),no_original_host_fallback=True))
 with (PACKAGE/'FILE_MANIFEST.csv').open('x',encoding='utf-8',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=['path','sha256','bytes'],lineterminator='\n');writer.writeheader();writer.writerows(expected[n] for n in sorted(expected))
 outer=sha(PACKAGE/'FILE_MANIFEST.csv');found,dirs=inventory();need(set(found)==set(expected)|{'FILE_MANIFEST.csv'},'Final extracted file set')
 for n,r in expected.items():need(found[n]==r,'Final extracted hash mismatch: '+n)
 with zipfile.ZipFile(ZIP,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for n in sorted(found):z.write(PACKAGE/n,arcname=n)
 with zipfile.ZipFile(ZIP) as z:
  index=zip_index(z);need(set(index)==set(found),'Candidate ZIP inventory')
  for n,r in found.items():
   data=z.read(n);need(len(data)==r['bytes'] and hashlib.sha256(data).hexdigest()==r['sha256'],'Candidate ZIP bytes: '+n)
 need(sha(BASE)==BASE_SHA and BASE.stat().st_size==BASE_BYTES,'Original ZIP changed')
 for n,h in ADDITIONS.items():need(sha(ROOT/n)==h,'Reviewed addition changed during preparation')
 final,_=inventory();need(final==found,'Candidate changed during ZIP verification')
 need(not (OUT/'reports').exists(),'Reports must remain absent before replay GO')
 save('prepared_freeze.json',dict(status='PREPARED_STRICT_FLOW_CANDIDATE_ONLY',utc=datetime.now(timezone.utc).isoformat(),base_zip=str(BASE),base_sha256=BASE_SHA,base_bytes=BASE_BYTES,original_zip_unchanged=True,evidence_commit=COMMIT,overlay_prefixes=PREFIXES,git_blob_checks=len(overlay),changed_or_added_git_payloads=sum(x['changed'] for x in overlay_records),package_root=str(PACKAGE),candidate_zip=str(ZIP),candidate_sha256=sha(ZIP),candidate_bytes=ZIP.stat().st_size,candidate_payloads=len(expected),candidate_files=len(found),outer_manifest_sha256=outer,native_addendum_unchanged=True,recursive_manifests=len(verified),unique_historical_payloads=len(bindings),links_reparse_and_casefold_checks=True,directories_checked=dirs,reviewed_additions=ADDITIONS,candidate_metadata=metadata,builder_sha256=sha(Path(__file__)),elapsed_s=time.perf_counter()-started,wrapper_imported=False,mathematical_replay=False,optimizer_calls=0,network_calls=0,independent_prepared_gate_required=True,execution_authorized=False))
 print(json.dumps(dict(status='PREPARED_STRICT_FLOW_CANDIDATE_ONLY',outer_manifest_sha256=outer,candidate_sha256=sha(ZIP),payloads=len(expected),recursive_manifests=len(verified))),flush=True)
if __name__=='__main__':
 try:main()
 except Exception as error:
  if OUT.exists() and not (OUT/'preparation_failure.json').exists():save('preparation_failure.json',dict(status='PREPARATION_FAILED',error_type=type(error).__name__,error=str(error),wrapper_imported=False,mathematical_replay=False,optimizer_calls=0))
  raise
