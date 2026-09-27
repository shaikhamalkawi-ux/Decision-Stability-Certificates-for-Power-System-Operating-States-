"""Independent returned-point replay against the unchanged original day321 model."""
from pathlib import Path
from fractions import Fraction as Q
import hashlib,importlib.util,json,sys,time
from datetime import datetime,timezone
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
ARM=ROOT/'results/research_next/day321_local_repair';PRE=ARM/'prepared';RUN=ARM/'run01'
ORIGINAL=ROOT/'results/research_next/common_commitment/prepared/days_321'
def require(ok,s):
    if not ok:raise ValueError(s)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(p,d,name):
    require(sha(p)==d,'helperpin');s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def bindings(items):
    for item in items:
        b=Path(item['path']).read_bytes();require(len(b)==item['bytes'] and hashlib.sha256(b).hexdigest()==item['sha256'],'binding')
def rat(x):return {'numerator':str(x.numerator),'denominator':str(x.denominator),'approximate':float(x)}
t=time.perf_counter()
require(sha(PRE/'prepared_freeze.json')=='78f9c1eb621da6f9e177689849971004544d6ab419e5141a7dcf35145dd2ccf2','freeze')
require(sha(PRE/'input_manifest.json')=='9c79243cb96114a91786ed3e3bc349a96549b036f5016172fd4b33e57a1b4fe1','manifest')
items=read(PRE/'input_manifest.json')['files'];require(len(items)==65,'bindings');bindings(items)
closed={str(p):sha(p) for p in sorted(RUN.iterdir()) if p.is_file()}
completion=read(RUN/'completion.json');result=read(RUN/'result.json')
require(sha(RUN/'completion.json')=='dfa93964513047ad2cd49b3324d9b3ca154948bdc9eeac3531f007196452400c','completion')
require(sha(RUN/'result.json')=='ec7bb3be2d79c5c3b878a7d674da5ca6c625173d07cffa440261018d9f452091','result')
require(completion['candidates']==1 and completion['nodal_systems_solved']==2 and completion['optimizer_calls']==0 and completion['all_frozen_inputs_unchanged'],'ledger')
v=module(ROOT/'src/research8h_standalone_verify.py','708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f','repair_independent_npz')
m=v.load_model(ORIGINAL);bits=tuple(v.vector(v.read_npz(ORIGINAL/'integrality.npz',('integrality',))['integrality'],('|u1',),m.cols,'original mask'))
require((m.rows,m.cols,sum(bits))==(34681,23016,12096),'fulloriginaldimensions')
def point(p):return tuple(v.vector(v.read_npz(p,('vector',))['vector'],('<f8',),m.cols,'point'))
p=point(RUN/'candidate_vector.npz');old=point(ROOT/'results/research8h/day_blocks/days_321/constructive_vector.npz')
require(all(x in (0.,1.) for x,b in zip(p,bits) if b),'exact fullbits')
state={6888+24*70+2:1.,6888+24*71+2:1.,14952+24*70+2:0.,10920+24*72+2:0.}
shifts={41*h+j:Q(d) for h in (70,71) for j,d in ((2,30),(40,-30))}
angles={18984+24*h+b for h in (70,71) for b in range(24) if b!=12}
allowed=set(state)|set(shifts)|angles
require(all(p[j]==x for j,x in state.items()),'state recipe')
require(all(Q(p[j])-Q(old[j])==d for j,d in shifts.items()),'power recipe')
require(all(p[j].hex()==old[j].hex() for j in range(m.cols) if j not in allowed),'outside locality')
require(all(p[18984+24*h+12].hex()==old[18984+24*h+12].hex() for h in (70,71)),'unchanged reference')
exact=v.check_point(m,list(p),bits,Q.from_float(1e-5))
require(exact==read(RUN/'exact_point_check.json'),'independent original point result')
base=module(ROOT/'src/researchnext_common_commitment.py','039af59750b4c165d877b9878ac14af02a202700b46739ba96a8914075ae3284','repair_independent_native')
meta=read(ORIGINAL/'model_metadata.json');native=base.native_check(v,p,ORIGINAL,meta,read(ORIGINAL/'native_spec.json'))
require(native==read(RUN/'native_check.json'),'independent native result')
fossil=[meta['unit_names'].index(n) for n in meta['fossil_units']];require(len(fossil)==23,'fossil roster')
e0=sum((Q(old[41*h+j]) for h in range(168) for j in fossil),Q(0));e1=sum((Q(p[41*h+j]) for h in range(168) for j in fossil),Q(0))
require(e1-e0==60 and e1<=Q(23195),'exact energy and nominal budget')
require(result['energy_after']==rat(e1) and result['energy_before']==rat(e0),'energy receipt')
accepted=exact['expanded_pass'] and native['expanded_pass']
require(accepted and result['accepted'] and not exact['strict_pass'],'scope')
bindings(items)
require(all(sha(Path(path))==digest for path,digest in closed.items()),'closed producer outputs unchanged')
report={'status':'INDEPENDENT_ORIGINAL_POINT_NATIVE_LOCALITY_PASS','utc':datetime.now(timezone.utc).isoformat(),'reviewer_sha256':sha(__file__),'producer_source_sha256':'d77d1f5cd6a0225730cfb2c119e27628e156b45db884e03d75259fc65b888ccc','input_bindings':65,'original_rows':m.rows,'original_columns':m.cols,'original_binary_coordinates':sum(bits),'expanded_pass':accepted,'strict_pass':False,'native_pass':native['expanded_pass'],'actual_changed_coordinates':sum(a.hex()!=b.hex() for a,b in zip(old,p)),'allowed_changed_coordinates':len(allowed),'locality_pass':True,'energy_after':rat(e1),'exact_increment_MWh':60,'producer_output_hashes':closed,'candidate_sha256':sha(RUN/'candidate_vector.npz'),'optimizer_calls':0,'producer_imports':0,'candidate_regenerations':0,'nodal_resolves':0,'checker_kernel_reused_by_pinned_hash':True,'independent_model':str(ORIGINAL.relative_to(ROOT)),'elapsed_seconds':time.perf_counter()-t,'scope':'Individual original day321 tau-expanded encoding; no common-action, regret or mechanism claim'}
with (ARM/'INDEPENDENT_POSTRUN_REVIEW.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps(report),flush=True)
