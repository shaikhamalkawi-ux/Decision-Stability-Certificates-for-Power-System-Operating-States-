from pathlib import Path
from datetime import datetime, timezone
import argparse,csv,hashlib,io,json,re,subprocess,zipfile
parser=argparse.ArgumentParser();parser.add_argument("--expected-commit",required=True);parser.add_argument("--checkpoint-count",required=True,type=int);args=parser.parse_args()
assert re.fullmatch("[0-9a-f]{40}",args.expected_commit) and args.checkpoint_count>=18
ROOT=Path(r'C:/Users/gmalkawi/.codex/worktrees/dsc-temporal-information/3')
D=ROOT/'.work/research8h_delivery'
NAME='DSC_Temporal_Research_2026-09-27_Final.zip'
final=D/NAME;partial=D/(NAME+'.partial')
assert not final.exists() and not partial.exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
assert head==args.expected_commit
assert sha((D/'DSC_Temporal_Research_2026-09-27_Checkpoint05.zip').read_bytes()) == '495dcd6831ddbcd1c8263b32a536d5d9ff7ef2943fe54250c1c5532359e366d7'
with zipfile.ZipFile(D/'DSC_Temporal_Research_2026-09-27_Checkpoint05.zip') as z:
 assert z.testzip() is None
 oldmanifest=list(csv.DictReader(io.StringIO(z.read('FILE_MANIFEST.csv').decode())))
 for r in oldmanifest:
  b=z.read(r['path']);assert sha(b)==r['sha256'] and len(b)==int(r['bytes'])
 payload={p:z.read(p) for p in z.namelist() if p not in ['FILE_MANIFEST.csv','FILE_ALLOWLIST.txt','PACKAGE_PROVENANCE.json']}
listing=subprocess.check_output(['git','ls-tree','-r','-z',head,'docs/research8h','results/research8h','results/seasonal_uncapped','src','reproducibility'],cwd=ROOT)
committed=[]
for entry in listing.split(b'\0'):
 if not entry:continue
 header,rel=entry.split(b'\t',1);rel=rel.decode('utf-8')
 mode,kind,oid=header.decode().split()
 if rel.startswith('src/') and not Path(rel).name.startswith('research8h_'):continue
 assert kind=='blob' and mode=='100644' and '..' not in Path(rel).parts
 b=(ROOT/rel).read_bytes()
 assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==oid,rel
 if rel in payload: assert payload[rel]==b, "Git overlay would change an inherited payload: "+rel
 payload[rel]=b;committed.append(rel)
manifest_checks=[]
for name in ["verified_checkpoint_manifest.csv"]+[f"verified_checkpoint{n:02d}_manifest.csv" for n in range(2,args.checkpoint_count+1)]:
 p=ROOT/'results/research8h'/name
 assert p.is_file(), name
 rows=list(csv.DictReader(io.StringIO(p.read_text(encoding='utf-8-sig'))))
 for r in rows:
  rel=r.get('path',r.get('relative_path','')).replace(chr(92),'/')
  if rel.startswith(str(ROOT).replace(chr(92),'/')+'/'):rel=rel[len(str(ROOT))+1:]
  assert rel in payload,(name,rel,list(r))
  assert sha(payload[rel])==r['sha256'] and len(payload[rel])==int(r['bytes'])
 manifest_checks.append({'manifest':name,'payloads':len(rows),'pass':True})
assert len(manifest_checks) == args.checkpoint_count and len({r['manifest'] for r in manifest_checks}) == args.checkpoint_count
readme=(D/'README_FINAL_AR.md').read_text(encoding='utf-8')
payload['README_FINAL_AR.md']=readme.encode('utf-8')
payload['STRICT_FLOW_CANDIDATE.json']=(json.dumps(dict(schema='strict-flow-candidate-v1',evidence_commit='579ecf20452b7838fdc5802744b24f597af5e1c7',scope='strict-flow-capped-and-uncapped-v1'),indent=2)+'\n').encode()
for rel in payload:
 assert rel and not rel.startswith(('/', '\\')) and ':' not in rel and '\\' not in rel and '..' not in Path(rel).parts and Path(rel).as_posix()==rel, rel
assert len({p.casefold() for p in payload})==len(payload)
provenance={'label':'VERIFIED RESEARCH SESSION DELIVERY','created_utc':datetime.now(timezone.utc).isoformat(),
 'git_commit':head,'baseline_commit':'7300129ce9bc4d7d4b6a9911eabe000b1789295e',
 'not_final_manuscript':True,'committed_research_files':len(committed),'source_zip_crc_and_manifest_verified':True,'inherited_payload_bytes_unchanged':True,
 'git_blob_equality_checked_for_every_added_or_refreshed_file':True,'published_manifest_checks':manifest_checks,
 'active_uncommitted_arms_excluded':[],
 'strict_replay_evidence_commit':'579ecf20452b7838fdc5802744b24f597af5e1c7',
 'excluded':['credentials','authentication and browser state','subscription full texts','frozen release changes'],
 'remote_verification_limit':'Local archive CRC/SHA verification; remote content hash requires separate exposed checksum or download readback.'}
payload['PACKAGE_PROVENANCE.json']=(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n').encode()
payload['FILE_ALLOWLIST.txt']=('\n'.join(sorted([*payload,'FILE_ALLOWLIST.txt','FILE_MANIFEST.csv']))+'\n').encode()
rows=[{'path':p,'bytes':len(b),'sha256':sha(b)} for p,b in sorted(payload.items())]
s=io.StringIO(newline='');w=csv.DictWriter(s,fieldnames=['path','bytes','sha256'],lineterminator='\n');w.writeheader();w.writerows(rows)
manifest=s.getvalue().encode()
with zipfile.ZipFile(partial,'x',allowZip64=True) as z:
 for p,b in sorted(payload.items()):
  method=zipfile.ZIP_STORED if p.endswith(('.npz','.gz')) else zipfile.ZIP_DEFLATED
  z.writestr(p,b,compress_type=method,compresslevel=6 if method==zipfile.ZIP_DEFLATED else None)
 z.writestr('FILE_MANIFEST.csv',manifest,compress_type=zipfile.ZIP_DEFLATED)
with zipfile.ZipFile(partial) as z:
 assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))
 assert set(z.namelist())==set(payload)|{'FILE_MANIFEST.csv'}
 for r in rows:
  b=z.read(r['path']);assert sha(b)==r['sha256'] and len(b)==r['bytes']
partial.rename(final)
result={'status':'VERIFIED_LOCAL','created_utc':datetime.now(timezone.utc).isoformat(),'zip_path':str(final),
 'bytes':final.stat().st_size,'sha256':sha(final.read_bytes()),'md5':hashlib.md5(final.read_bytes()).hexdigest(),
 'git_commit':head,'payload_files':len(rows),'zip_members':len(rows)+1,'crc_verified':True,
 'every_member_matches_manifest':True,'outer_manifest_sha256':sha(manifest),'strict_replay_evidence_commit':'579ecf20452b7838fdc5802744b24f597af5e1c7','git_blob_checks':len(committed),'published_manifest_checks':manifest_checks}
(D/'README_FINAL_AR.md').write_bytes(readme.encode('utf-8'))
(D/'FINAL_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
(D/(NAME+'.sha256')).write_text(result['sha256']+'  '+NAME+'\n',encoding='ascii')
print(json.dumps(result),flush=True)
