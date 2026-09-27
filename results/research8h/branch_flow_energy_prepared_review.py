"""Independent prepared gate: strict uncapped branch-flow energy. No producer import."""
import ast,csv,gzip,hashlib,importlib.util,json,math,sys,time
from fractions import Fraction as Q
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'results/research8h/branch_flow_strict_energy';PARENT=ROOT/'results/research8h/branch_flow_encoding'
def req(x,m):
 if not x:raise AssertionError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def js(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def q(r):return Q(int(r['numerator']),int(r['denominator']))
def vec(p,k):return v.read_npz(p,(k,))[k].values
def row(m,i):return {m.indices[e]:Q(m.data[e]) for e in range(m.indptr[i],m.indptr[i+1]) if m.data[e]}
def labels(p):
 with gzip.open(p,'rt',encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def bound(x):return None if not math.isfinite(x) else Q(x)
def encbound(x):return None if x is None else q(x)
start=time.perf_counter();kernel=ROOT/'src/research8h_standalone_verify.py';req(sha(kernel)=='708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f','Kernel')
spec=importlib.util.spec_from_file_location('strict_energy_prepared_kernel',kernel);v=importlib.util.module_from_spec(spec);sys.modules[spec.name]=v;spec.loader.exec_module(v)
freeze=js(OUT/'prepared_freeze.json');manifest=js(OUT/'input_manifest.json');req(sha(OUT/'input_manifest.json')==freeze['manifest_sha256'] and len(manifest)==freeze['bindings'],'Freeze')
for e in manifest:
 p=Path(e['path']);req(p.is_file() and p.stat().st_size==int(e['bytes']) and sha(p)==e['sha256'],'Frozen '+str(p))
req(not (OUT/'execution_marker.json').exists(),'No execution yet')
req(freeze['calls']==['january_identity','seed_26093200','seed_26093201','seed_26093200_proposal','seed_26093201_proposal'],'Calls')
req(freeze['phase']==1800 and freeze['arithmetic_phase']==900 and freeze['limit_per_call']==60,'Budgets')
req(freeze['latest_start']=='2026-09-27T03:35:00+00:00' and freeze['cutoff']=='2026-09-27T04:00:00+00:00','Clock')
for rel,digest in [('src/research8h_branch_flow_energy.py','7e19ad3f6a5c0535f6b422ed28cc36034997daefb516ed3c91f07b4920e08ea5'),('src/research8h_branch_flow_energy_check.py','13d1debeb82d76e595c2700554d39a27c5b01259e03b0d35edabe21e8c3175e9'),('docs/research8h/BRANCH_FLOW_STRICT_ENERGY_PROTOCOL.md','608003f505015b89ed6f36bdf87ef81e39ff4c0e07463206bfe613031be30886')]:req(sha(ROOT/rel)==digest,'Source '+rel)
oldast=ast.parse((ROOT/'src/research8h_branch_flow_check.py').read_text());newast=ast.parse((ROOT/'src/research8h_branch_flow_energy_check.py').read_text());of=next(n for n in oldast.body if isinstance(n,ast.FunctionDef) and n.name=='check_native');nf=next(n for n in newast.body if isinstance(n,ast.FunctionDef) and n.name=='check_native')
req(isinstance(of.body[-2],ast.If) and 'unchanged_cap' in ast.dump(of.body[-2]),'Known sole cap test')
req(ast.dump(ast.Module(body=of.body[:-2],type_ignores=[]))==ast.dump(ast.Module(body=nf.body[:-1],type_ignores=[])),'Native physical body identical except cap')
results=[]
for case in ('january_identity','seed_26093200','seed_26093201'):
 d=OUT/case;s=PARENT/case;m=v.load_model(d);old=v.load_model(s);lab=labels(d/'row_metadata.csv.gz');olab=labels(s/'row_metadata.csv.gz');meta=js(d/'model_metadata.json');caps=[i for i,r in enumerate(olab) if r['family']=='fossil_energy_cap'];req(len(caps)==1,'One cap');keep=[i for i in range(old.rows) if i!=caps[0]]
 req((m.rows,m.cols)==(34512,29400) and m.lower==old.lower and m.upper==old.upper,'Full dimensions/boxes');req(meta['fossil_cap_absent'] is True and meta['budget_MWh'] is None,'Explicit no cap');req(js(d/'cap_deletion.json')['parent_rows']==keep,'Cap row map')
 for j,i in enumerate(keep):
  req(row(m,j)==row(old,i) and m.row_lower[j]==old.row_lower[i] and m.row_upper[j]==old.row_upper[i],'Only cap deleted')
  req(int(lab[j]['old_row'])==i and all(lab[j][k]==olab[i][k] for k in ('family','hour_0based','uid')),'Labels')
 req(vec(d/'integrality.npz','integrality')==(0,)*6888+(1,)*12096+(0,)*10416,'Full mask');cost=vec(d/'objective.npz','objective');req(cost==vec(s/'objective.npz','objective'),'Objective')
 for name in ('native_inputs.npz','permutation.csv','graph.json','native_spec.json'):req(sha(d/name)==sha(s/name),'Native retained '+name)
 fixed={r['column']:q(r['value']) for r in js(d/'fixed_schedule.json')};req(set(fixed)==set(range(6888,18984)) and all(x in (0,1) for x in fixed.values()),'Schedule original mask')
 if case=='january_identity':
  pt=js(d/'rational_point.json');oldpt=js(s/'rational_point.json');req(pt['values']==oldpt['values'],'Identity point unchanged');requirebindings={name:sha(d/name) for name in ('matrix.npz','bounds.npz','integrality.npz','objective.npz')};req(pt['model_bindings']==requirebindings,'Identity rebound')
  xs=[q(r['value']) for r in pt['values']];req(len(xs)==m.cols and [r['column'] for r in pt['values']]==list(range(m.cols)),'Point order')
  req(all(Q(l)<=x<=Q(u) for l,x,u in zip(m.lower,xs,m.upper)) and all(xs[j]==x for j,x in fixed.items()),'Strict point box/binary')
  for i in range(m.rows):
   value=sum((a*xs[j] for j,a in row(m,i).items()),Q(0));req((not math.isfinite(m.row_lower[i]) or value>=Q(m.row_lower[i])) and (not math.isfinite(m.row_upper[i]) or value<=Q(m.row_upper[i])),'Strict identity row')
  energy=sum((Q(c)*x for c,x in zip(cost,xs)),Q(0));req(energy==q(js(d/'identity_upper.json')['exact_objective']),'Identity energy')
 else:
  oldpoint=vec(ROOT/'results/research8h/hour_of_day_uncapped'/case/'mip/recovered_vector.npz','vector');req(all(x==Q(oldpoint[j]) for j,x in fixed.items()),'Only declared old schedule')
  prop=OUT/(case+'_proposal');pm=v.load_model(prop);req((pm.rows,pm.cols)==(18480,17304),'Proposal dimensions');req(not any(vec(prop/'integrality.npz','integrality')),'Continuous proposal')
  with gzip.open(prop/'exact_blocks.json.gz','rt',encoding='utf-8') as f:blocks=json.load(f)
  req(len(blocks)==168,'168 blocks');byold={};pcols=[];count=0
  for t,block in enumerate(blocks):
   cols=list(range(t*41,(t+1)*41))+list(range(18984+t*24,18984+(t+1)*24))+list(range(23016+t*38,23016+(t+1)*38));req(block['hour']==t and block['columns']==cols and len(block['rows'])==110,'Block map');pcols+=cols
   for key,values in [('lower',m.lower),('upper',m.upper),('objective',cost)]:req([q(x) for x in block[key]]==[Q(values[j]) for j in cols],'Block '+key)
   for r in block['rows']:
    oi=r['original_row'];req(oi not in byold,'Unique row');byold[oi]=(count,t,cols,r);count+=1
  req(pm.lower==tuple(m.lower[j] for j in pcols) and pm.upper==tuple(m.upper[j] for j in pcols) and vec(prop/'objective.npz','objective')==tuple(cost[j] for j in pcols),'Proposal boxes/objective')
  constants={r['row']:r for r in js(prop/'constant_rows.json')};req(len(constants)==16032 and set(constants).isdisjoint(byold) and set(constants)|set(byold)==set(range(m.rows)),'Complete row partition')
  for i in range(m.rows):
   rr=row(m,i);shift=sum((a*fixed[j] for j,a in rr.items() if j in fixed),Q(0));free={j:a for j,a in rr.items() if j not in fixed};lo,hi=bound(m.row_lower[i]),bound(m.row_upper[i])
   if i in constants:
    r=constants[i];req(not free and q(r['activity'])==shift and encbound(r['lower'])==lo and encbound(r['upper'])==hi and (lo is None or shift>=lo) and (hi is None or shift<=hi),'Constant row')
   else:
    pi,t,cols,r=byold[i];mapping={j:k for k,j in enumerate(cols)};terms={mapping[j]:a for j,a in free.items()};l=None if lo is None else lo-shift;u=None if hi is None else hi-shift
    req({j:q(a) for j,a in r['terms']}==terms and q(r['fixed_shift'])==shift and encbound(r['lower'])==l and encbound(r['upper'])==u,'Exact block algebra');req(row(pm,pi)=={t*103+j:a for j,a in terms.items()} and bound(pm.row_lower[pi])==l and bound(pm.row_upper[pi])==u,'Proposal row algebra')
 results.append(dict(case=case,only_cap_deleted=True,full_original_mask=True,native_unchanged=True,identity_strict_rebound=case=='january_identity',proposal_checked=case!='january_identity'))
for e in manifest:req(sha(Path(e['path']))==e['sha256'],'Input changed during review')
req(not (OUT/'execution_marker.json').exists(),'No execution during review')
report=dict(status='INDEPENDENT_STRICT_ENERGY_PREPARED_PASS',frozen_bindings=len(manifest),cases=results,optimizer_calls=0,producer_imports=0,native_physical_body_identical_except_cap=True,elapsed_s=time.perf_counter()-start,source_sha256=sha(Path(__file__)))
reportpath=ROOT/'results/research8h/branch_flow_energy_prepared_review.json';req(not reportpath.exists(),'One review');reportpath.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
