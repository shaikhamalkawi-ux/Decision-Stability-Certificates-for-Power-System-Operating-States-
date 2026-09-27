import csv,gzip,hashlib,importlib.util,json,math,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(r'C:/Users/gmalkawi/.codex/worktrees/dsc-temporal-information/3')
ARM=ROOT/'results/research8h/tau_fixed_evidence'
OUT=ROOT/'results/research8h/tau_fixed_evidence_independent_review'
SRC=ROOT/'src/research8h_tau_fixed_evidence.py';PROTO=ROOT/'docs/research8h/TAU_FIXED_EVIDENCE_PROTOCOL.md'
KERNEL=ROOT/'src/research8h_standalone_verify.py'
HOD='results/research8h/hour_of_day';FRESH='results/research8h/fresh_january_weeks/targets';ENERGY='results/research8h/fresh_january_energy';HODE='results/research8h/hour_of_day_uncapped'
CASES=('seed_26093200','seed_26093201','seed_26093210','seed_26093211','seed_26093220','seed_26093221')
WEEKS=dict(zip(CASES,(1,1,2,2,3,3)));CAPS={1:23195,2:26532,3:48319}
MASK=(0,)*6888+(1,)*12096+(0,)*4032
SOURCE_SHA='e87c56855235cd083dcee07267ea76077e949359684eb10c6a9cc21647c61288'
PROTOCOL_SHA='2c2e5094d5a0baf1e0e7b518348ba05b87f8b517f48dc6a392904149a5339217'
def need(a,s):
    if not a:raise ValueError(s)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def array(path,key,dtype,length):return v.vector(v.read_npz(ROOT/path,(key,))[key],dtype,length,key)
def bits(a,b):return len(a)==len(b) and all(x.hex()==y.hex() for x,y in zip(a,b))
def labels(directory):
    with gzip.open(ROOT/directory/'row_metadata.csv.gz','rt',encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def load(directory):
    if directory not in models:models[directory]=v.load_model(ROOT/directory)
    return models[directory]
def cost(meta):
    names=meta['unit_names'];need(len(names)==41 and len(set(names))==41,'41 generator roster')
    fossil=[j for j,n in enumerate(names) if fuels[n] in ('Coal','Oil','NG')]
    need(len(fossil)==23 and set(names[j] for j in fossil)==set(meta['fossil_units']),'23 fossil units')
    return tuple(float(j<6888 and j%41 in fossil) for j in range(23016))
def check_cap(directory,week,c):
    m=load(directory);lab=labels(directory);need(len(lab)==34681 and m.rows==34681 and m.cols==23016,'Capped model size')
    need(all(int(x['row'])==i for i,x in enumerate(lab)),'Row labels')
    caps=[i for i,r in enumerate(lab) if r['family']=='fossil_energy_cap'];need(len(caps)==1 and not any('mean' in x['family'] for x in lab),'Cap/no means')
    i=caps[0];need(m.row_lower[i]==-math.inf and m.row_upper[i]==CAPS[week],'Old fixed cap')
    terms={m.indices[z]:m.data[z] for z in range(m.indptr[i],m.indptr[i+1]) if m.data[z]}
    need(terms=={j:x for j,x in enumerate(c) if x},'Cap fossil functional');return i
def cap_only(uncapped,parent,week,c):
    m=load(uncapped);full=load(parent);i=check_cap(parent,week,c)
    need((m.rows,m.cols)==(34680,23016) and bits(m.lower,full.lower) and bits(m.upper,full.upper),'Cap-only boxes/dimensions')
    old_rows=[r for r in range(full.rows) if r!=i]
    for r,old in enumerate(old_rows):
        a,b=m.indptr[r:r+2];p,q=full.indptr[old:old+2]
        need(m.indices[a:b]==full.indices[p:q] and bits(m.data[a:b],full.data[p:q]),'Cap-only coefficient correspondence')
        need(bits((m.row_lower[r],m.row_upper[r]),(full.row_lower[old],full.row_upper[old])),'Cap-only row bounds')
    need(array(parent+'/integrality.npz','integrality',('|u1',),23016)==MASK,'Parent original mask')
    return dict(uncapped=uncapped,parent=parent,week=week,cap=CAPS[week],deleted_row=i,retained_rows=34680,identical_columns_boxes_and_coefficients=True)
start=time.perf_counter();need(not (ARM/'execution_started.json').exists(),'Execution already started')
need(sha(SRC)==SOURCE_SHA and sha(PROTO)==PROTOCOL_SHA,'Reviewed source/protocol changed')
f=read(ARM/'prepared_freeze.json');need(f['source_sha256']==SOURCE_SHA and f['protocol_sha256']==PROTOCOL_SHA,'Freeze source bindings')
need(f['status']=='TAU_FIXED_EVIDENCE_PREPARED_ONLY' and f['optimizer_calls']==f['arithmetic_calls']==0,'Preparation scope')
need(sha(ARM/'cases.json')==f['descriptor_sha256'] and sha(ARM/'input_manifest.csv')==f['manifest_sha256'],'Freeze descriptor/manifest')
with (ARM/'input_manifest.csv').open(encoding='utf-8-sig',newline='') as file:entries=list(csv.DictReader(file))
need(len(entries)==f['selected_input_files'] and len({r['path'] for r in entries})==len(entries),'Unique selected manifest')
for r in entries:
    p=(ROOT/r['path']).resolve();need(p.is_relative_to(ROOT) and p.stat().st_size==int(r['bytes']) and sha(p)==r['sha256'],'Selected binding '+r['path'])
plan=read(ARM/'cases.json');expected=[];identity_parents={};identity_models={}
for week in (1,2,3):
    identity=HOD+'/january_identity' if week==1 else FRESH+f'/week_{week}_identity'
    control=HOD+'/seed_26100200' if week==1 else FRESH+('/seed_26100210' if week==2 else '/seed_26100220')
    for kind,directory in (('identity',identity),('control',control)):
        expected.append(dict(role=f'cap_{kind}_w{week}',week=week,model=directory,mask=directory+'/integrality.npz',vector=directory+'/constructive_vector.npz',metadata=directory+'/model_metadata.json'))
    uncapped='results/research8h/energy_lp_refinement/january_identity' if week==1 else ENERGY+f'/week_{week}_identity'
    expected.append(dict(role=f'energy_identity_w{week}',week=week,model=uncapped,mask=uncapped+'/original_integrality.npz',vector=identity+'/constructive_vector.npz' if week==1 else uncapped+'/reference_upper_vector.npz',metadata=identity+'/model_metadata.json' if week==1 else uncapped+'/model_metadata.json'))
    identity_parents[week]=identity;identity_models[week]=uncapped
for case in CASES:
    week=WEEKS[case];directory=(HODE if week==1 else ENERGY)+'/'+case
    expected.append(dict(role='energy_'+case,week=week,model=directory,mask=directory+'/original_integrality.npz',vector=directory+'/mip/recovered_vector.npz',metadata=directory+'/model_metadata.json'))
need(plan['points']==expected and len(plan['points'])==15,'Exactly15 fixed point roles')
need([r['case'] for r in plan['energy']]==list(CASES) and [r['case'] for r in plan['negatives']]==[c for c in CASES if c!='seed_26093211'],'Fixed six/five denominators')
need(plan['capped_unknown']=='seed_26093211' and plan['capped_ordinary_denominator']==6,'Preserved unknown')
need(sha(KERNEL)=='708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f','NPZ parser binding')
spec=importlib.util.spec_from_file_location('tau_prepared_npz_decoder',KERNEL);v=importlib.util.module_from_spec(spec);sys.modules[spec.name]=v;spec.loader.exec_module(v)
models={}
with (ROOT/'reproducibility/native_sources/rts_inputs/raw/RTS-GMLC_v0.2.3/gen.csv').open(encoding='utf-8-sig',newline='') as file:native=list(csv.DictReader(file))
need(len({r['GEN UID'] for r in native})==len(native),'No native UID duplicates');fuels={r['GEN UID']:r['Fuel'] for r in native}
roles=[];relations=[]
for p in expected:
    m=load(p['model']);mask=array(p['mask'],'integrality',('|u1',),23016);vec=array(p['vector'],'vector',('<f8',),23016)
    need(mask==MASK and all(math.isfinite(x) for x in vec) and all(x in (0.,1.) for x,fixed in zip(vec,mask) if fixed),'Original binary point/mask schema')
    meta=read(ROOT/p['metadata']);need(meta['offsets']==dict(P=0,U=6888,Y=10920,Z=14952,theta=18984),'Original layout');c=cost(meta)
    if p['role'].startswith('cap_'):check_cap(p['model'],p['week'],c)
    else:
        need(bits(array(p['model']+'/objective.npz','objective',('<f8',),23016),c),'Uncapped objective')
        need(not any(r['family']=='fossil_energy_cap' or 'mean' in r['family'] for r in labels(p['model'])),'Uncapped rows')
        parent=identity_parents[p['week']] if p['role'].startswith('energy_identity_') else (HOD if p['week']==1 else FRESH)+'/'+p['role'][7:]
        relations.append(cap_only(p['model'],parent,p['week'],c))
    roles.append(dict(role=p['role'],rows=m.rows,columns=m.cols,exact_binary_coordinates=12096,mask_sha256=sha(ROOT/p['mask']),vector_sha256=sha(ROOT/p['vector'])))
need(len(relations)==9,'Nine actual cap-only relationships')
for item in plan['negatives']:
    need(item['week']==WEEKS[item['case']] and item['model']==item['parent']+'/lp','Negative model identity')
    for n in ('matrix.npz','bounds.npz'):need(sha(ROOT/item['model']/n)==sha(ROOT/item['parent']/n),'Ray actual capped model')
    cert=read(ROOT/item['model']/'dual_certificate.json');v.ray_bindings(ROOT/item['model'],cert,None,())
    raw=array(item['model']+'/raw_solver_ray.npz','multipliers',('<f8',),34681);need(all(math.isfinite(x) for x in raw),'Raw ray schema')
for r in entries:need(sha(ROOT/r['path'])==r['sha256'],'Final selected hash')
need(not (ARM/'execution_started.json').exists(),'Execution started during prepared review')
result=dict(status='INDEPENDENT_TAU_FIXED_EVIDENCE_PREPARED_PASS',selected_bindings=len(entries),manifest_sha256=f['manifest_sha256'],descriptor_sha256=f['descriptor_sha256'],source_sha256=SOURCE_SHA,protocol_sha256=PROTOCOL_SHA,point_roles=roles,actual_cap_only_relationships=relations,five_ray_model_bindings_checked=True,threshold_evaluations=0,ray_or_dual_sensitivity_evaluations=0,optimizer_calls=0,producer_imports=0,elapsed_s=time.perf_counter()-start)
with (OUT/'prepared_review.json').open('x') as file:json.dump(result,file,indent=2);file.write('\n')
print(json.dumps({'status':result['status'],'bindings':len(entries),'point_roles':len(roles),'cap_only_relationships':len(relations),'elapsed_s':result['elapsed_s']}))
