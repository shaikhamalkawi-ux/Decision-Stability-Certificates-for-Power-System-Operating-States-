"""Independent ramp scope basis audit; does not repeat adjacent envelope computation."""
import csv,gzip,hashlib,importlib.util,json,math,sys,time
from fractions import Fraction as Q
from pathlib import Path
sys.dont_write_bytecode=True
T=time.perf_counter();ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'results/research_next/ramp_scope';PRE=ROOT/'results/research_next/common_commitment/prepared'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def req(a,s):
 if not a:raise ValueError(s)
def rat(r):return Q(int(r['numerator']),int(r['denominator']))
req(sha(PRE/'input_manifest.json')=='8ff99b1f4450ac15e91b26a261a85c98d574bbbdac3f7fe149efd9fd07204a5c','manifest')
idx={str(Path(x['path']).resolve()).casefold():x for x in read(PRE/'input_manifest.json')['files']};used={}
def bound(p):
 p=Path(p);r=idx[str(p.resolve()).casefold()];b=p.read_bytes();req(len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'],'binding');used[str(p)]=r;return b
source=ROOT/'src/researchnext_ramp_scope.py';protocol=ROOT/'docs/research_next/RAMP_SCOPE_PROTOCOL.md'
summary=read(OUT/'result.json');snapshot={str(p):sha(p) for p in [source,protocol,OUT/'result.json',OUT/'cases.json']}
req(sha(source)==summary['source_sha256']=='90306e77708a890cb742e81489240caa3098d09d20b03ccee1b634e87af0964b','source')
req(sha(protocol)==summary['protocol_sha256']=='460de8b8c9aa5ff695016ad4495ec084660800f1289ac5a0ed74b7e90449e91b','protocol')
req(sha(OUT/'cases.json')==summary['cases_sha256'],'case hash')
k=ROOT/'src/research8h_standalone_verify.py';req(sha(k)=='708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f','kernel')
s=importlib.util.spec_from_file_location('ramp_basis_stdlib',k);v=importlib.util.module_from_spec(s);sys.modules[s.name]=v;s.loader.exec_module(v)
gen={r['GEN UID']:r for r in csv.DictReader(bound(PRE/'gen.csv').decode('utf-8-sig').splitlines())}
worlds=[]
for world in ('identity','days_321'):
 d=PRE/world
 for n in ['matrix.npz','bounds.npz','native_inputs.npz','model_metadata.json','native_spec.json','row_metadata.csv.gz']:bound(d/n)
 m=v.load_model(d);meta=read(d/'model_metadata.json');spec=read(d/'native_spec.json');arrays=v.read_npz(d/'native_inputs.npz',('pmin','pmax','net','rows','source_hour','nodal'))
 req(meta['offsets']==dict(P=0,U=6888,Y=10920,Z=14952,theta=18984),'offsets')
 req([r['uid'] for r in spec]==meta['unit_names'],'roster')
 therm=meta['thermal_unit_names'];req(therm==[r['uid'] for r in spec if r['thermal']] and len(therm)==24,'thermal order')
 for r in spec:
  if not r['thermal']:continue
  raw=float(gen[r['uid']]['Ramp Rate MW/Min']);rate=Q(float(raw*60.0))
  req(raw.hex()==r['per_minute_binary64_hex'] and float(raw*60.0).hex()==r['hourly_binary64_hex'] and rate==rat(r['hourly_rational']),'native hourly rate convention')
 labels=list(csv.DictReader(gzip.decompress(bound(d/'row_metadata.csv.gz')).decode('utf-8-sig').splitlines()));req(len(labels)==m.rows,'labels')
 seen=set();orientations={}
 for i,label in enumerate(labels):
  req(int(label['row'])==i,'label coordinate')
  family=label['family']
  if family not in ('thermal_upper','thermal_lower'):continue
  t=int(label['hour_0based']);uid=label['uid'];j=meta['unit_names'].index(uid);u=therm.index(uid)
  req(0<=t<168 and (t,uid,family) not in seen,'thermal coverage');seen.add((t,uid,family))
  pcol=41*t+j;ucol=6888+24*t+u;value=arrays['pmax' if family=='thermal_upper' else 'pmin'].values[41*t+j]
  # Canonical <=0 expression, accepting its exact sign-reversed >=0 equivalent.
  coeff={pcol:1.0 if family=='thermal_upper' else -1.0,ucol:-value if family=='thermal_upper' else value};coeff={j:a for j,a in coeff.items() if a!=0}
  actual={m.indices[e]:m.data[e] for e in range(m.indptr[i],m.indptr[i+1])}
  if actual==coeff and m.row_lower[i]==-math.inf and m.row_upper[i]==0:orientation='canonical_upper'
  elif actual=={j:-a for j,a in coeff.items()} and m.row_lower[i]==0 and m.row_upper[i]==math.inf:orientation='reversed_lower'
  else:raise ValueError('thermal row does not imply stated native bound '+str((world,i,family)))
  orientations[orientation]=orientations.get(orientation,0)+1
 req(seen=={(t,n,f) for t in range(168) for n in therm for f in ('thermal_upper','thermal_lower')},'all thermal rows')
 worlds.append(dict(world=world,thermal_rows_verified=len(seen),orientations=orientations,rates_checked=24))
cases=read(OUT/'cases.json')['cases'];req(len(cases)==8016 and summary['cases']==8016 and summary['failures']==0,'reported denominator')
for world in ('identity','days_321'):
 rows=[r for r in cases if r['world']==world];req(len(rows)==4008 and len({(r['unit'],r['hour_0based']) for r in rows})==4008,'case inventory')
 req(all(r['expanded_native_check_implied'] and rat(r['margin'])>=Q.from_float(1e-5) for r in rows),'reported margins')
 req(min(rat(r['margin']) for r in rows)==30,'reported minimum')
for p,r in used.items():req(sha(p)==r['sha256'] and Path(p).stat().st_size==r['bytes'],'input changed')
req(all(sha(p)==h for p,h in snapshot.items()),'producer changed')
report=dict(status='INDEPENDENT_SCOPE_AND_MATRIX_BASIS_PASS',reviewer_sha256=sha(__file__),input_bindings=list(used.values()),producer_snapshot=snapshot,worlds=worlds,thermal_rows_total=sum(w['thermal_rows_verified'] for w in worlds),reported_envelope_cases=8016,reported_minimum_margin=30,adjacent_envelope_computation_repeated=False,formula_review='On/on exact bits and verified thermal rows imply delta <= D+2tau; R-D>=tau implies delta<=R+tau.',scope='On/on supplementary native ramp only; no startup/shutdown or residence redundancy claim.',source_preclose_rehash_limit='Producer binds source/protocol at result save rather than initial snapshot; reviewer checks current trusted hashes, not an independent proof of execution-time source immutability.',optimizer_calls=0,producer_imports=0,elapsed_seconds=time.perf_counter()-T)
with (OUT/'INDEPENDENT_REVIEW.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps({k:report[k] for k in ('status','thermal_rows_total','reported_envelope_cases','elapsed_seconds')}))
