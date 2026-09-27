"""Independent prepared-only backend map gate; no producer or optimizer import."""
import json,hashlib,importlib.util,sys,math,time
from pathlib import Path
from collections import Counter
sys.dont_write_bytecode=True
T=time.perf_counter()
ROOT=Path(__file__).resolve().parents[3]
ARM=ROOT/'results/research_next/common_gurobi'
PRE=ARM/'prepared'; OLD=ROOT/'results/research_next/common_commitment/prepared'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(x,s):
 if not x: raise ValueError(s)
def check(items):
 seen=set()
 for item in items:
  p=Path(item['path']); key=str(p.resolve()).casefold()
  require(key not in seen,'duplicate');seen.add(key)
  b=p.read_bytes();require(len(b)==item['bytes'] and hashlib.sha256(b).hexdigest()==item['sha256'],'binding '+str(p))
 return seen
require(not (ARM/'run01').exists(),'run already exists at start')
freeze=PRE/'prepared_freeze.json';manifest=PRE/'input_manifest.json'
require(sha(freeze)=='c91dac7c583a42493e0eae6f9b3b493140a0997661bb748a08a3d08d168cb926','freeze')
require(sha(manifest)=='a7f5dd3ca95663543460f01c0045c7e62b430aed7a7d1facd6f370aa2f07eb07','manifest')
f=read(freeze); items=read(manifest)['files'];require(len(items)==86,'86 bindings');covered=check(items)
source=ROOT/'src/researchnext_common_gurobi.py';protocol=ROOT/'docs/research_next/COMMON_GUROBI_PROTOCOL.md'
require(sha(source)==f['source_sha256']=='9f5515fb99ac43cba3756f1e2b5a9f3a0ad9df7c143860922edd9ae99cd000ec','source')
require(sha(protocol)==f['protocol_sha256']=='9fd3bc026acad8ca940b9338c257094fb5f5fefb7de4ecd076f81762fa1ebb71','protocol')
require(f['optimizer_calls']==f['gurobi_imports']==0,'prepare scope')
old_items=read(OLD/'input_manifest.json')['files']; require(len(old_items)==48,'inherited denominator')
require(all(x in items for x in old_items),'48 inherited exact bindings')
expected={'joint/'+s for s in ['matrix.npz','bounds.npz','integrality.npz','column_maps.json','row_origins.json']}
for w in ('identity','days_321'):
 expected|={w+'/'+s for s in ['matrix.npz','bounds.npz','integrality.npz','model_metadata.json','native_inputs.npz','permutation.csv','row_metadata.csv.gz','native_spec.json']}
expected.add('gen.csv')
actual=set()
for pair in read(PRE/'copy_provenance.json')['copies']:
 a=Path(pair['original']['path']);b=Path(pair['copy']['path']);rel=a.relative_to(OLD).as_posix()
 require(b==PRE/rel and rel not in actual,'copy role');actual.add(rel)
 require(pair['original'] in items and pair['copy'] in items,'copy binding')
 require(a.read_bytes()==b.read_bytes(),'full copied bytes')
require(actual==expected and len(actual)==22,'22 exact copy roles')
k=ROOT/'src/research8h_standalone_verify.py'; require(sha(k)=='708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f','kernel')
s=importlib.util.spec_from_file_location('gurobi_prepared_independent_npz',k);v=importlib.util.module_from_spec(s);sys.modules[s.name]=v;s.loader.exec_module(v)
m=v.load_model(PRE/'joint')
bits=tuple(v.vector(v.read_npz(PRE/'joint/integrality.npz',('integrality',))['integrality'],('|u1',),m.cols,'bits'))
require((m.rows,m.cols,len(m.data),sum(bits))==(69362,33936,291176,12096),'dimensions')
require(bits==tuple(int(6888<=j<18984) for j in range(m.cols)),'all original bits')
require(all(math.isfinite(a) and math.isfinite(b) and a<=b for a,b in zip(m.lower,m.upper)),'finite original boxes')
rows=read(PRE/'backend_rows.json');require(sha(PRE/'backend_rows.json')=='42de642c90a9c9481cba65d6b425e59d570837297cb88c07bcc762b86e4c0be4','row map SHA')
expected_rows=[]
for i,(lo,hi) in enumerate(zip(m.row_lower,m.row_upper)):
 require(not math.isnan(lo) and not math.isnan(hi) and lo<=hi,'row bounds')
 if lo==hi:
  require(math.isfinite(lo),'equality finite'); sides=[('=','equality',lo)]
 else:
  sides=[]
  if lo!=-math.inf:sides.append(('>','lower',lo))
  if hi!=math.inf:sides.append(('<','upper',hi))
 require(sides,'unbounded row')
 for sense,side,rhs in sides:expected_rows.append(dict(original_row=i,sense=sense,side=side,rhs_hex=rhs.hex()))
require(rows['rows']==expected_rows and len(expected_rows)==82130,'all exact endpoint splitting')
require(rows['no_auxiliary_variables'] and rows['original_rows']==m.rows and rows['backend_rows']==82130,'map header')
p=read(PRE/'plan.json')
opts=dict(TimeLimit=1800.0,Threads=1,Seed=0,MIPFocus=1,SolutionLimit=1,MIPGap=1e-8,Presolve=-1,FeasibilityTol=1e-8,IntFeasTol=1e-9)
require(p['options']==opts and p['calls']==1 and p['phase_seconds']==2400.0 and p['start_guard_seconds']==1805.0,'plan')
require(p['full_original_binaries']==12096 and p['objective']=='zero feasibility','unchanged question')
require(all(p[x] for x in ['no_warm_start','no_lp','no_ray','no_iis','no_retry','no_install_or_license_change']),'exclusions')
require(p['runtime']['packages']=={'gurobipy':'13.0.0','numpy':'2.5.3','scipy':'1.18.1'},'declared environment')
require(p['runtime']['gurobi_imported_for_preparation'] is False,'no license validation claim')
check(items)
require(sha(freeze)=='c91dac7c583a42493e0eae6f9b3b493140a0997661bb748a08a3d08d168cb926' and sha(manifest)==f['manifest_sha256'],'transport unchanged')
require(not (ARM/'run01').exists(),'run appeared during gate')
report=dict(status='INDEPENDENT_PREPARED_PASS',utc=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),reviewer_sha256=sha(__file__),freeze_sha256=sha(freeze),manifest_sha256=sha(manifest),source_sha256=sha(source),protocol_sha256=sha(protocol),bindings=86,inherited_bindings=48,exact_byte_copies=22,rows=m.rows,cols=m.cols,original_binaries=sum(bits),stored_coefficients=len(m.data),backend_rows=len(expected_rows),backend_senses=dict(Counter(r['sense'] for r in expected_rows)),options=opts,phase_seconds=p['phase_seconds'],run_absent_start_end=True,no_producer_import=True,no_gurobi_import=True,no_optimizer=True,no_old_assembly_or_witness_replay=True,old_joint_assembly_review_inherited_by_hash='956b37cbcdd49571a6a79611da197a5be840a5c2747ffbd60576c90805d58e6b',license_capacity='UNKNOWN; not tested by this review',backend_API_readback='pending authorized execution before optimize',elapsed_seconds=time.perf_counter()-T)
with (ARM/'INDEPENDENT_PREPARED_REVIEW.json').open('x',encoding='utf-8') as out:json.dump(report,out,indent=2);out.write('\n')
print(json.dumps(report))
