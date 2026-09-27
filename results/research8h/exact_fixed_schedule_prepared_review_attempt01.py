"""Independent read-only exact-preparation replay; no producer import or optimizer."""
from pathlib import Path
from fractions import Fraction as Q
import csv, gzip, hashlib, importlib.util, json, math, sys, time
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[2]
out=root/'results/research8h/exact_fixed_schedule'
report_path=root/'results/research8h/exact_fixed_schedule_prepared_review.json'
assert not report_path.exists()
started=time.perf_counter()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
manifest=out/'input_manifest.json'
assert sha(manifest)=='397fdbdd982ec11dc7265d842733df40fc0ad66a22922ea40e06cfebdaf03da9'
k=root/'src/research8h_standalone_verify.py'
assert sha(k)=='708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'
spec=importlib.util.spec_from_file_location('prepared_gate_kernel',k); v=importlib.util.module_from_spec(spec);sys.modules[spec.name]=v;spec.loader.exec_module(v)
read=v.json_read
records=read(manifest)
assert len(records)==34 and len({r['path'] for r in records})==34
for r in records: assert Path(r['path']).stat().st_size==r['bytes'] and sha(r['path'])==r['sha256']
freeze=read(out/'prepared_freeze.json')
assert freeze['manifest_sha256']==sha(manifest) and freeze['optimizer_calls']==freeze['basis_reconstructions']==0
assert not (out/'execution_marker.json').exists()
def q(r):
    x=Q(int(r['numerator']),int(r['denominator']))
    assert str(x.numerator)==r['numerator'] and str(x.denominator)==r['denominator']
    return x
def ep(x): return None if not math.isfinite(x) else Q(x)
def dec(x): return None if x is None else q(x)
def row(m,i): return {m.indices[e]:Q(m.data[e]) for e in range(m.indptr[i],m.indptr[i+1]) if m.data[e]}
def arr(p,key): return v.read_npz(p,(key,))[key].values
src=root/'results/research8h/seasonal_reference/month_01'; capped=root/'results/research8h/seasonal_transfer/january_identity'
m=v.load_model(src); cap=v.load_model(capped)
assert (m.rows,m.cols)==(34680,23016) and (cap.rows,cap.cols)==(34681,23016)
mask=arr(src/'integrality.npz','integrality');cost=arr(src/'objective.npz','objective')
assert mask==tuple(int(6888<=j<18984) for j in range(m.cols))
schedule=arr(capped/'constructive_vector.npz','vector')
fixed={x['column']:q(x['value']) for x in read(out/'fixed_schedule.json')}
assert list(fixed)==list(range(6888,18984)) and all(x in (0,1) and x==Q(schedule[j]) for j,x in fixed.items())
for t in range(168):
 for j in range(24):
  u=fixed[6888+t*24+j]; change=u-fixed[6888+(t-1)*24+j] if t else Q(0)
  assert fixed[10920+t*24+j]==max(change,0) and fixed[14952+t*24+j]==max(-change,0)
with gzip.open(out/'exact_blocks.json.gz','rt',encoding='utf8') as f: blocks=json.load(f)
transforms=read(out/'transformations.json'); constants=read(out/'constant_rows.json')
assert len(blocks)==len(transforms)==168 and len(constants)==16032
constant_map={x['row']:x for x in constants}; seen=set(); constant_count=0
with gzip.open(src/'row_metadata.csv.gz','rt',encoding='utf8',newline='') as f: labels=list(csv.DictReader(f))
A=v.read_npz(out/'proposal_matrix.npz',('data','indices','indptr','shape','format'))
B=v.read_npz(out/'proposal_bounds.npz',('column_lower','column_upper','row_lower','row_upper'))
C=arr(out/'proposal_objective.npz','objective')
assert A['shape'].values==(18648,10920) and A['format'].values==(b'csr',)
pr=0
for t,(block,tr) in enumerate(zip(blocks,transforms)):
 columns=list(range(t*41,(t+1)*41))+list(range(18984+t*24,18984+(t+1)*24))
 assert block['hour']==tr['hour']==t and block['columns']==columns and len(block['rows'])==111
 assert block['reference_column']==18984+t*24+12 and block['reference_bus_ID']==113
 for key,base,proposalkey in [('lower',m.lower,'column_lower'),('upper',m.upper,'column_upper'),('objective',cost,None)]:
  values=[q(x) for x in block[key]]
  assert values==[Q(base[j]) for j in columns]
  proposed=C[t*65:(t+1)*65] if proposalkey is None else B[proposalkey].values[t*65:(t+1)*65]
  assert values==[Q(x) for x in proposed]
 rids=[r['original_row'] for r in block['rows']]
 assert rids==sorted(set(rids))
 aggs=[i for i in rids if labels[i]['family']=='aggregate_balance']; nodes=[i for i in rids if labels[i]['family']=='nodal_balance']
 assert len(aggs)==1 and len(nodes)==24 and tr['aggregate_row']==aggs[0] and tr['retained_nodal_rows']==nodes
 ag=aggs[0]; delta=row(m,ag); beta=Q(m.row_lower[ag]); assert m.row_lower[ag]==m.row_upper[ag]
 for i in nodes:
  assert m.row_lower[i]==m.row_upper[i]
  beta-=Q(m.row_lower[i])
  for j,x in row(m,i).items(): delta[j]=delta.get(j,Q(0))-x
 delta={j:x for j,x in delta.items() if x}
 lam=q(tr['lambda_exact']); maximum=max(map(abs,delta.values()))
 assert lam>0 and (lam.numerator&(lam.numerator-1))==0 and (lam.denominator&(lam.denominator-1))==0 and 1<=lam*maximum<2
 assert tr['difference']==[[columns.index(j),{'numerator':str(x.numerator),'denominator':str(x.denominator)}] for j,x in sorted(delta.items())]
 assert q(tr['rhs_difference'])==beta
 for record in block['rows']:
  i=record['original_row']; assert i not in seen; seen.add(i)
  original=row(m,i); shift=sum((x*fixed[j] for j,x in original.items() if j in fixed),Q(0))
  free={j:x for j,x in original.items() if j not in fixed}
  assert all(j in columns for j in free) and int(labels[i]['hour_0based'])==t and q(record['fixed_shift'])==shift
  expected={columns.index(j):x for j,x in free.items()}
  lo=None if ep(m.row_lower[i]) is None else ep(m.row_lower[i])-shift
  hi=None if ep(m.row_upper[i]) is None else ep(m.row_upper[i])-shift
  if i==ag: expected={columns.index(j):x*lam for j,x in delta.items()};lo=hi=beta*lam
  assert {j:q(x) for j,x in record['terms']}==expected and dec(record['lower'])==lo and dec(record['upper'])==hi
  a,b=A['indptr'].values[pr:pr+2]
  assert {j-t*65:Q(x) for j,x in zip(A['indices'].values[a:b],A['data'].values[a:b])}==expected
  assert ep(B['row_lower'].values[pr])==lo and ep(B['row_upper'].values[pr])==hi
  pr+=1
assert pr==18648
for i in range(m.rows):
 if i in seen: continue
 original=row(m,i); assert all(j in fixed for j in original)
 activity=sum((x*fixed[j] for j,x in original.items()),Q(0)); lo,hi=ep(m.row_lower[i]),ep(m.row_upper[i])
 assert (lo is None or activity>=lo) and (hi is None or activity<=hi)
 r=constant_map[i];assert q(r['activity'])==activity and dec(r['lower'])==lo and dec(r['upper'])==hi
 constant_count+=1
assert constant_count==len(constant_map)==16032 and set(constant_map)|seen==set(range(34680))
assert read(out/'conversion_differences.json')==[]
relation=read(out/'existing_cap_relation.json'); cr=relation['cap_row'];assert cr==24264
assert ep(cap.row_lower[cr]) is None and Q(cap.row_upper[cr])==23195
assert row(cap,cr)=={j:Q(x) for j,x in enumerate(cost) if x}
assert cap.lower==m.lower and cap.upper==m.upper and arr(capped/'integrality.npz','integrality')==mask
assert arr(capped/'objective.npz','objective')==cost
for i in range(cap.rows):
 if i==cr: continue
 j=i-int(i>cr)
 assert row(cap,i)==row(m,j) and (cap.row_lower[i],cap.row_upper[i])==(m.row_lower[j],m.row_upper[j])
meta=read(src/'model_metadata.json')
with (root/'reproducibility/native_sources/rts_inputs/raw/RTS-GMLC_v0.2.3/gen.csv').open(encoding='utf8-sig',newline='') as f: gens={r['GEN UID']:r for r in csv.DictReader(f)}
fossil=[j for j,n in enumerate(meta['unit_names']) if gens[n]['Fuel'] in ('Coal','Oil','NG')]
assert len(fossil)==23 and cost==tuple(float(j<6888 and j%41 in fossil) for j in range(m.cols))
for r in read(out/'native_spec.json'):
 g=gens[r['uid']];rate=float(g['Ramp Rate MW/Min']);hourly=rate*60.0
 assert r['per_minute_binary64_hex']==rate.hex() and r['hourly_binary64_hex']==hourly.hex()
 assert q(r['hourly_rational'])==Q(hourly) and q(r['difference_from_exact_times_60'])==Q(hourly)-60*Q(rate)
 assert r['minimum_up']==math.ceil(float(g['Min Up Time Hr'])) and r['minimum_down']==math.ceil(float(g['Min Down Time Hr']))
for r in records: assert sha(r['path'])==r['sha256']
report={'status':'INDEPENDENT_EXACT_PREPARED_PASS','manifest_sha256':sha(manifest),'bindings':34,'original_rows_checked':34680,'constant_rows':constant_count,'exact_hour_blocks':168,'exact_proposal_rows':pr,'proposal_conversion_differences':0,'existing_cap_row':cr,'cap':23195,'full_original_mask':12096,'native_fossil_and_ramp_conventions_checked':True,'optimizer_calls':0,'basis_reconstructions':0,'producer_or_checker_imported':False,'review_source_sha256':sha(__file__),'elapsed_s':time.perf_counter()-started}
with report_path.open('x',encoding='utf8') as f: json.dump(report,f,indent=2);f.write('\n')
print(json.dumps(report))
