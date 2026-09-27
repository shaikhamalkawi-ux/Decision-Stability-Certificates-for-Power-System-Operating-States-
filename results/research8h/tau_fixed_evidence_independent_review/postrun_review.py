import csv,hashlib,importlib.util,json,math,sys,time
from fractions import Fraction as F
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(r'C:/Users/gmalkawi/.codex/worktrees/dsc-temporal-information/3');ARM=ROOT/'results/research8h/tau_fixed_evidence';OUT=ROOT/'results/research8h/tau_fixed_evidence_independent_review'
TAU=F.from_float(1e-5)
def need(x,s):
    if not x:raise ValueError(s)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def frac(d):return F(int(d['numerator']),int(d['denominator']))
def enc(x):return None if x is None else {'numerator':str(x.numerator),'denominator':str(x.denominator)}
def snapshot():return {p.relative_to(ARM).as_posix():sha(p) for p in ARM.rglob('*') if p.is_file()}
def model(d):
    if d not in models:models[d]=v.load_model(ROOT/d)
    return models[d]
def vector(p,k,dtype,length):return v.vector(v.read_npz(ROOT/p,(k,))[k],dtype,length,k)
def qhex(s):
    x=float.fromhex(s);need(math.isfinite(x),'Nonfinite hex multiplier');return F(x)
def scan(m,p):
    need(len(p)==m.cols and all(math.isfinite(x) for x in p),'Finite point shape')
    q=list(map(F,p));columns=rows=F(0)
    for j,x in enumerate(q):columns=max(columns,F(m.lower[j])-x,x-F(m.upper[j]))
    for i in range(m.rows):
        a=sum((F(m.data[z])*q[m.indices[z]] for z in range(m.indptr[i],m.indptr[i+1])),F(0))
        if math.isfinite(m.row_lower[i]):rows=max(rows,F(m.row_lower[i])-a)
        if math.isfinite(m.row_upper[i]):rows=max(rows,a-F(m.row_upper[i]))
    return max(rows,columns),rows,columns,q
# Independent signed-endpoint accumulation used for both certificate types.
def combine(m,d):
    columns=[F(0)]*m.cols;beta=norm=F(0)
    for i,x in d.items():
        endpoint=m.row_lower[i] if x>0 else m.row_upper[i];need(math.isfinite(endpoint),'Inadmissible finite-endpoint sign')
        beta+=x*F(endpoint);norm+=abs(x)
        for z in range(m.indptr[i],m.indptr[i+1]):columns[m.indices[z]]+=x*F(m.data[z])
    return beta,norm,columns
def upper(n,s):
    need(s>=0,'Negative proof slope')
    if n<=0:return 'empty',None if not s else n/s
    return ('unbounded',None) if not s else ('finite',n/s)
def inward(x,up):
    a=x.numerator*10**18;b=x.denominator;n=(a+b-1)//b if up else a//b
    sign='-' if n<0 else '';whole,tail=divmod(abs(n),10**18);return sign+str(whole)+'.'+str(tail).zfill(18)
def range_check(saved,points,proofs):
    lower=max(points.values());uppers=[t[1] for t in proofs.values() if t[1] is not None];hi=min(uppers) if uppers else None
    empty=[n for n,t in proofs.items() if t[0]=='empty'];valid=not empty and (hi is None or lower<hi)
    kind=('unbounded' if hi is None else 'finite') if valid else 'empty';contains=valid and lower<=TAU and (hi is None or TAU<hi)
    need(saved['kind']==kind and frac(saved['lower'])==lower and (None if saved['upper'] is None else frac(saved['upper']))==hi,'Exact range endpoints')
    need(saved['lower_included'] and not saved['upper_included'] and saved['exact_tau0_membership']==contains,'Open/closed membership')
    need(set(saved['active_lower_roles'])=={n for n,x in points.items() if x==lower},'Limiting point ties')
    need(set(saved['active_upper_proofs'])=={n for n,t in proofs.items() if hi is not None and t[1]==hi},'Limiting proof ties')
    need(set(saved['empty_proof_conditions'])==set(empty),'Empty proof conditions')
    need(saved['certified_values_strictly_below_tau0']==(contains and lower<TAU) and saved['certified_values_strictly_above_tau0']==(contains and (hi is None or hi>TAU)),'Two-sided tau0 extension')
    ds=saved['safe_decimal_subset'];lo_d=inward(lower,True);hi_d=None if hi is None else inward(hi,False)
    need(ds['lower']==lo_d and ds['upper']==hi_d and ds['lower_included'] and not ds['upper_included'],'Inward decimal endpoints')
    need(ds['nonempty']==(valid and (hi is None or F(lo_d)<F(hi_d))),'Exact-vs-decimal range collapse')
    need(frac(saved['lower_over_tau0'])==lower/TAU and (None if saved['upper_over_tau0'] is None else frac(saved['upper_over_tau0']))==(None if hi is None else hi/TAU),'Tau0 ratios')
    return dict(kind=kind,lower=enc(lower),upper=enc(hi),tau0_included=contains,lower_limits=saved['active_lower_roles'],upper_limits=saved['active_upper_proofs'],safe_decimal_subset=ds)
start=time.perf_counter();completion=read(ARM/'completion.json');need(completion['status']=='TAU_FIXED_EVIDENCE_EXACT_REPLAY_COMPLETE','Producer incomplete')
need(sha(ARM/'input_manifest.csv')=='79c39fd85153e05b261ebf64ed7bd9e1041ae2311fcd527035339bab6230c4df','Prepared manifest')
with (ARM/'input_manifest.csv').open(encoding='utf-8-sig',newline='') as f:bindings=list(csv.DictReader(f))
need(len(bindings)==211,'Selected bindings')
for r in bindings:need(sha(ROOT/r['path'])==r['sha256'] and (ROOT/r['path']).stat().st_size==int(r['bytes']),'Initial selected hash')
before=snapshot();kernel=ROOT/'src/research8h_standalone_verify.py';need(sha(kernel)=='708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f','Decoder hash')
spec=importlib.util.spec_from_file_location('tau_independent_npz',kernel);v=importlib.util.module_from_spec(spec);sys.modules[spec.name]=v;spec.loader.exec_module(v)
models={};plan=read(ARM/'cases.json');point_records={r['role']:r for r in read(ARM/'point_thresholds.json')['records']};points={};energies={}
MASK=(0,)*6888+(1,)*12096+(0,)*4032
for item in plan['points']:
    m=model(item['model']);mask=vector(item['mask'],'integrality',('|u1',),23016);p=vector(item['vector'],'vector',('<f8',),23016)
    need(mask==MASK and all(x in (0.,1.) for x,flag in zip(p,mask) if flag),'Original binary coordinates')
    threshold,row_v,col_v,q=scan(m,p);saved=point_records[item['role']]
    need(frac(saved['tau_min'])==threshold and saved['threshold_included'] and saved['original_binary_coordinates']==12096,'Point threshold')
    need(frac(saved['exact_point_scan']['maximum_row_violation'])==row_v and frac(saved['exact_point_scan']['maximum_column_violation'])==col_v,'All row/box violations')
    need(saved['strict_nominal_membership']==(threshold==0) and threshold<=TAU,'Strict-vs-expanded point membership')
    meta=read(ROOT/item['metadata']);fossil={meta['unit_names'].index(n) for n in meta['fossil_units']};need(len(fossil)==23,'Fossil roster')
    energy=sum((q[j] for j in range(6888) if j%41 in fossil),F(0));need(frac(saved['fixed_fossil_MWh'])==energy,'Fixed exact fossil energy')
    for key,path in [('matrix_sha256',item['model']+'/matrix.npz'),('bounds_sha256',item['model']+'/bounds.npz'),('mask_sha256',item['mask']),('vector_sha256',item['vector'])]:need(saved[key]==sha(ROOT/path),'Point role binding')
    points[item['role']]=threshold;energies[item['role']]=energy
need(len(points)==15,'Point denominator')
ray_records={r['case']:r for r in read(ARM/'capped_ray_ranges.json')['records']};ray_proofs={};ray_results=[]
for item in plan['negatives']:
    m=model(item['model']);cert=read(ROOT/item['model']/'dual_certificate.json');d={}
    for r in cert['multipliers']:need(r['row'] not in d,'Duplicate multiplier');d[r['row']]=qhex(r['value_hex'])
    raw=vector(item['model']+'/raw_solver_ray.npz','multipliers',('<f8',),m.rows);orientation=cert['orientation'];need(orientation in (-1,1),'Fixed ray orientation')
    expected={}
    for i,raw_x in enumerate(raw):
        x=F(raw_x)*orientation
        if not x:continue
        if cert['candidate']=='projected_to_row_sign_cone' and ((x>0 and not math.isfinite(m.row_lower[i])) or (x<0 and not math.isfinite(m.row_upper[i]))):continue
        expected[i]=x
    need(d==expected,'Existing fixed ray projection');beta,norm,atd=combine(m,d)
    box=sum((x*F(m.upper[j] if x>=0 else m.lower[j]) for j,x in enumerate(atd)),F(0));delta=beta-box;slope=norm+sum(map(abs,atd),F(0));t=upper(delta,slope)
    r=ray_records[item['case']];need(frac(r['delta0'])==delta and frac(r['slope'])==slope and r['degenerate_kind']==t[0] and (None if r['strict_upper'] is None else frac(r['strict_upper']))==t[1],'Ray threshold arithmetic')
    need(delta-TAU*slope>0,'Archived ray tau0 separation')
    range_check(r['pair_range'],{item['identity_role']:points[item['identity_role']]},{item['case']:t})
    range_check(r['with_class_control_range'],{n:points[n] for n in (item['identity_role'],item['control_role'])},{item['case']:t})
    ray_proofs[item['case']]=t;ray_results.append(dict(case=item['case'],delta0=enc(delta),slope=enc(slope),upper=enc(t[1])))
energy_records={r['case']:r for r in read(ARM/'energy_ranges.json')['records']};energy_proofs={};energy_results=[]
for item in plan['energy']:
    m=model(item['model']);c=vector(item['model']+'/objective.npz','objective',('<f8',),m.cols)
    raw_arrays=v.read_npz(ROOT/item['model']/'lp/raw_duals.npz',('row_dual','column_dual'));raw=raw_arrays['row_dual'].values
    proj=vector(item['model']+'/lp/projected_row_dual.npz','row_dual',('<f8',),m.rows);need(len(raw)==m.rows,'Raw objective-dual dimension');d={}
    for i,x in enumerate(raw):
        need(math.isfinite(x),'Finite dual');expected=0. if ((x>0 and not math.isfinite(m.row_lower[i])) or (x<0 and not math.isfinite(m.row_upper[i]))) else x
        need(proj[i].hex()==expected.hex(),'Fixed objective projection')
        if proj[i]:d[i]=F(proj[i])
    beta,norm,atd=combine(m,d);res=[F(x)-a for x,a in zip(c,atd)]
    box=sum((x*F(m.lower[j] if x>=0 else m.upper[j]) for j,x in enumerate(res)),F(0));nominal=beta+box;slope=norm+sum(map(abs,res),F(0))
    ui=energies[item['identity_role']];ut=energies[item['target_role']];t=upper(nominal-ui,slope);r=energy_records[item['case']]
    need(frac(r['nominal_target_lower'])==nominal and frac(r['slope'])==slope and frac(r['energy_numerator'])==nominal-ui,'Energy affine bound')
    need(frac(r['fixed_identity_upper'])==ui and frac(r['fixed_target_upper'])==ut and frac(r['fixed_gap_lower_at_tau0'])==nominal-TAU*slope-ui,'Energy fixed points/tau0 gap')
    need((None if r['strict_upper'] is None else frac(r['strict_upper']))==t[1] and r['degenerate_kind']==t[0],'Energy strict threshold')
    range_check(r['pair_range'],{n:points[n] for n in (item['identity_role'],item['target_role'])},{item['case']:t})
    energy_proofs[item['case']]=t;energy_results.append(dict(case=item['case'],nominal=enc(nominal),slope=enc(slope),identity_upper=enc(ui),upper=enc(t[1])))
need(len(ray_proofs)==5 and len(energy_proofs)==6,'Proof denominators')
common=read(ARM/'common_ranges.json');cap_points={n:x for n,x in points.items() if n.startswith('cap_')};energy_points={n:x for n,x in points.items() if n.startswith('energy_')}
rays={'ray_'+n:x for n,x in ray_proofs.items()};energy={'energy_'+n:x for n,x in energy_proofs.items()}
verified={name:range_check(common[name],p,t) for name,p,t in [('capped',cap_points,rays),('energy',energy_points,energy),('joint',points,{**rays,**energy})]}
need(all(x['tau0_included'] for x in verified.values()),'Common tau0 membership')
need(completion['five_fixed_negative_rays']==5 and completion['six_fixed_energy_duals']==6 and completion['capped_point_roles']==6 and completion['uncapped_point_roles']==9 and completion['optimizer_calls']==completion['network_calls']==0,'Completion scope')
need(read(ARM/'capped_ray_ranges.json')['unchanged_unknown']=='seed_26093211' and read(ARM/'energy_ranges.json')['capped_26093211_still_unknown'],'Historical UNKNOWN preserved')
for r in bindings:need(sha(ROOT/r['path'])==r['sha256'],'Final frozen hash')
need(snapshot()==before,'Producer files changed during review')
result=dict(status='INDEPENDENT_TAU_FIXED_EVIDENCE_POSTRUN_PASS',selected_bindings=211,point_roles=15,fixed_rays=5,fixed_energy_duals=6,point_thresholds={n:enc(x) for n,x in points.items()},ray_thresholds=ray_results,energy_thresholds=energy_results,common_ranges=verified,all_frozen_and_producer_hashes_unchanged=True,producer_hashes=before,optimizer_calls=0,producer_source_imports=0,no_new_candidate_or_optimization=True,elapsed_s=time.perf_counter()-start)
with (OUT/'postrun_review.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'status':result['status'],'elapsed_s':result['elapsed_s'],'joint':verified['joint']}))
