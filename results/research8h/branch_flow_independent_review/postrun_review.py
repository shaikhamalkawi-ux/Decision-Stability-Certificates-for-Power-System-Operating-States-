import csv,gzip,hashlib,importlib.util,json,math,re,sys,time
from collections import Counter
from datetime import datetime,timezone
from fractions import Fraction as F
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(r'C:/Users/gmalkawi/.codex/worktrees/dsc-temporal-information/3')
ARM=ROOT/'results/research8h/branch_flow_encoding';OUT=ROOT/'results/research8h/branch_flow_independent_review'
OLD=ROOT/'results/research8h/hour_of_day';GEN=ROOT/'reproducibility/native_sources/rts_inputs/raw/RTS-GMLC_v0.2.3/gen.csv'
CASES=('january_identity','seed_26100200','seed_26093200','seed_26093201');TARGETS=CASES[2:]
MANIFEST='0981491f326dbd3f34e2825d501cbff54d74bf18e5c3d924edf420a4950532d4'
MASK=(0,)*6888+(1,)*12096+(0,)*10416;TAU=F.from_float(1e-5)
def need(x,s):
    if not x:raise ValueError(s)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def unique(pairs):
    d={}
    for k,x in pairs:need(k not in d,'Duplicate JSON key');d[k]=x
    return d
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'),object_pairs_hook=unique,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('Nonfinite JSON')))
def q(d):
    need(type(d) is dict and set(d)=={'numerator','denominator'},'Rational schema');n,b=d['numerator'],d['denominator']
    need(type(n) is str and type(b) is str and re.fullmatch(r'0|-?[1-9][0-9]*',n) and re.fullmatch(r'[1-9][0-9]*',b),'Canonical rational spelling')
    need(len(n)<=2468 and len(b)<=2467,'Rational input bound');a,c=int(n),int(b);need(abs(a).bit_length()<=8192 and c.bit_length()<=8192,'Rational bit bound')
    x=F(a,c);need((x.numerator,x.denominator)==(a,c),'Reduced rational');return x
def enc(x):return {'numerator':str(x.numerator),'denominator':str(x.denominator)}
def array(directory,name,key,dtype,length):return v.vector(v.read_npz(directory/name,(key,))[key],dtype,length,key)
def snapshot():return {p.relative_to(ARM).as_posix():sha(p) for p in ARM.rglob('*') if p.is_file()}
def verify_inputs():
    need(sha(ARM/'input_manifest.json')==MANIFEST,'Input manifest identity')
    for r in bindings:
        p=Path(r['path']);need(p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],'Frozen input '+str(p))
def cost_for(meta):
    names=meta['unit_names'];need(len(names)==41 and len(set(names))==41,'Generator roster')
    fossil={j for j,n in enumerate(names) if native[n]['Fuel'] in ('Coal','Oil','NG')}
    need(len(fossil)==23 and {names[j] for j in fossil}==set(meta['fossil_units']),'Fossil objective roster')
    return tuple(float(j<6888 and j%41 in fossil) for j in range(29400))
def strict_scan(m,p,mask):
    need((m.rows,m.cols)==(34513,29400) and len(p)==29400 and mask==MASK,'Full variant dimensions/mask')
    fails=[];count=0
    def fail(d):
        nonlocal count
        count+=1
        if len(fails)<20:fails.append(d)
    for j,x in enumerate(p):
        if not F(m.lower[j])<=x<=F(m.upper[j]):fail({'column':j,'kind':'box'})
        if mask[j] and (x not in (0,1) or x!=fixed[j]):fail({'column':j,'kind':'fixed_binary'})
    for i in range(m.rows):
        activity=sum((F(m.data[z])*p[m.indices[z]] for z in range(m.indptr[i],m.indptr[i+1])),F(0))
        if math.isfinite(m.row_lower[i]) and activity<F(m.row_lower[i]):fail({'row':i,'side':'lower','gap':enc(F(m.row_lower[i])-activity)})
        if math.isfinite(m.row_upper[i]) and activity>F(m.row_upper[i]):fail({'row':i,'side':'upper','gap':enc(activity-F(m.row_upper[i]))})
    return dict(pass_strict=count==0,violations=count,first_violations=fails,rows_checked=34513,columns_checked=29400,binary_coordinates=12096,tau=0)
def native_scan(directory,p):
    meta=read(directory/'model_metadata.json');graph=read(directory/'graph.json');data=v.read_npz(directory/'native_inputs.npz',('pmin','pmax','net','rows','source_hour','nodal'))
    need(data['pmin'].shape==data['pmax'].shape==(168,41) and data['nodal'].shape==(168,24),'Native data shapes')
    need(all(math.isfinite(x) for name in ('pmin','pmax','nodal','net') for x in data[name].values),'Finite native data')
    names=meta['unit_names'];thermal=meta['thermal_unit_names'];buses={int(b):i for i,b in enumerate(meta['bus_ids'])};need(len(graph)==38 and len(buses)==24 and len(thermal)==24,'Native topology/roster')
    failures=[];energy=F(0);fossil={n for n in names if native[n]['Fuel'] in ('Coal','Oil','NG')}
    for t in range(168):
        power=p[t*41:(t+1)*41];theta=p[18984+t*24:18984+(t+1)*24];flows=p[23016+t*38:23016+(t+1)*38]
        demand=[F(x) for x in data['nodal'].values[t*24:(t+1)*24]];injection=[F(0)]*24
        if sum(power,F(0))!=sum(demand,F(0)):failures.append([t,'ALL','exact_nodal_sum'])
        for j,n in enumerate(names):
            lo=F(data['pmin'].values[t*41+j]);hi=F(data['pmax'].values[t*41+j]);x=power[j]
            if not 0<=x<=hi:failures.append([t,n,'availability'])
            if native[n]['Category']=='Hydro' and x!=lo:failures.append([t,n,'hydro_fixed'])
            injection[buses[int(native[n]['Bus ID'])]]+=x
            if n in fossil:energy+=x
        for e,line in enumerate(graph):
            need(line['branch']==e,'Canonical branch index');u,w=line['positive_bus'],line['negative_bus'];b=q(line['coefficient'])
            need(0<=u<24 and 0<=w<24 and u!=w and b>0,'Branch orientation')
            if flows[e]!=b*(theta[u]-theta[w]):failures.append([t,e,'flow_definition'])
            if not q(line['lower'])<=flows[e]<=q(line['upper']):failures.append([t,e,'flow_limit'])
            injection[u]-=flows[e];injection[w]+=flows[e]
        for bus,x in enumerate(injection):
            if x!=demand[bus]:failures.append([t,bus,'native_incidence'])
        for k,n in enumerate(thermal):
            j=names.index(n);u=p[6888+t*24+k];y=p[10920+t*24+k];z=p[14952+t*24+k]
            if not F(data['pmin'].values[t*41+j])*u<=power[j]<=F(data['pmax'].values[t*41+j])*u:failures.append([t,n,'committed_output'])
            if not t:
                if y or z:failures.append([t,n,'initial_transition'])
                continue
            previous=p[6888+(t-1)*24+k];change=u-previous
            if y!=max(change,0) or z!=max(-change,0):failures.append([t,n,'canonical_transition'])
            if change:
                dwell=math.ceil(float(native[n]['Min Up Time Hr' if change>0 else 'Min Down Time Hr']))
                if any(p[6888+h*24+k]!=u for h in range(t,min(168,t+dwell))):failures.append([t,n,'residence'])
            if u==previous==1 and abs(power[j]-p[(t-1)*41+j])>F(float(native[n]['Ramp Rate MW/Min'])*60.0):failures.append([t,n,'on_on_ramp'])
    if energy>23195:failures.append([-1,'ALL','fixed_cap'])
    return dict(pass_native=not failures,violations=len(failures),first_violations=failures[:20],energy=enc(energy),aggregate_authority='exact sum of native nodal loads; old net not imposed')
def independent_ray(m,d):
    atd=[F(0)]*m.cols;beta=norm=F(0)
    for i,x in d.items():
        endpoint=m.row_lower[i] if x>0 else m.row_upper[i]
        if not math.isfinite(endpoint):return {'admissible':False}
        beta+=x*F(endpoint);norm+=abs(x)
        for z in range(m.indptr[i],m.indptr[i+1]):atd[m.indices[z]]+=x*F(m.data[z])
    support=sum((x*F(m.upper[j] if x>=0 else m.lower[j]) for j,x in enumerate(atd)),F(0));gap=beta-support;slope=norm+sum(map(abs,atd),F(0))
    return dict(admissible=True,strict_pass=gap>0,expanded_pass=gap-TAU*slope>0,gap=enc(gap),expanded_gap=enc(gap-TAU*slope),slope=enc(slope))
start=time.perf_counter();completion=read(ARM/'completion.json');outcomes=read(ARM/'outcomes.json');calls=read(ARM/'calls.json')
bindings=read(ARM/'input_manifest.json');need(len(bindings)==103 and len({r['path'] for r in bindings})==103,'103 frozen bindings');verify_inputs();before=snapshot()
freeze=read(ARM/'prepared_freeze.json');need(freeze['source_sha256']=='bb5889f57ef051dffb196457b3bfbb9626e8c2e046a2b0bcc13ea6b5250fbd77' and freeze['checker_sha256']=='41dab33ed8e013d46fd7ae78974d95cab70e9794a906a7c6a12786bb093d4632' and freeze['protocol_sha256']=='2e96ae15a1b37d10cb12e354e65238f4cd1479e3c2fc39c9717bc9d5ed21c9e7','Approved sources')
k=ROOT/'src/research8h_standalone_verify.py';need(sha(k)=='708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f','Kernel source')
spec=importlib.util.spec_from_file_location('branch_independent_npz_ray_kernel',k);v=importlib.util.module_from_spec(spec);sys.modules[spec.name]=v;spec.loader.exec_module(v)
with GEN.open(encoding='utf-8-sig',newline='') as f:raw_native=list(csv.DictReader(f))
need(len({r['GEN UID'] for r in raw_native})==len(raw_native),'Unique native generators');native={r['GEN UID']:r for r in raw_native}
fixed_list=read(ARM/'fixed_schedule.json');fixed={r['column']:q(r['value']) for r in fixed_list};need(len(fixed_list)==len(fixed)==12096 and set(fixed)==set(range(6888,18984)) and all(x in (0,1) for x in fixed.values()),'Fixed binary schedule')
oldpoint=array(OLD/'january_identity','constructive_vector.npz','vector',('<f8',),23016);need(all(F(oldpoint[j])==x for j,x in fixed.items()),'Original schedule identity')
need(sha(OLD/'input_manifest.csv')=='078082667f83322d3540ad3ac215ebcc996d0d31b04fd52bfa75c1d2fd814fcc','Old case manifest')
with (OLD/'input_manifest.csv').open(encoding='utf-8-sig',newline='') as f:old_bindings=list(csv.DictReader(f))
for case in CASES:
    for name in ('matrix.npz','bounds.npz','integrality.npz','objective.npz','native_inputs.npz','model_metadata.json','row_metadata.csv.gz','permutation.csv','constructive_vector.npz'):
        matches=[r for r in old_bindings if r['path'].replace('\\','/').endswith('/hour_of_day/'+case+'/'+name)];need(len(matches)==1 and sha(OLD/case/name)==matches[0]['sha256'],'Old-case provenance')
need([c['case'] for c in calls]==['identity_proposal',*TARGETS] and len(calls)==3,'Fixed numerical call order')
for c,limit in zip(calls,(60.,30.,30.)):
    need(c['optimizer_calls'] in (0,1),'Attempted count')
    if c['optimizer_calls']:
        launch=read(ARM/c['case']/'launch_decision.json');need(launch['configured_seconds']==limit and launch['remaining_s']>=limit+5 and datetime.fromisoformat(launch['utc'])<datetime(2026,9,27,4,tzinfo=timezone.utc),'Actual call admission')
        if c['status']!='POSTCALL_ERROR':need(read(ARM/c['case']/'solver_result.json')==c,'Solver record')
        if 'soft_overrun_seconds' in c:need(abs(c['soft_overrun_seconds']-max(0,c['actual_seconds']-limit))<1e-8,'Soft solve accounting')
need(completion['optimizer_calls']==sum(c['optimizer_calls'] for c in calls)<=3 and completion['configured_maximum_calls']==3,'Three-call budget')
need(abs(completion['actual_solve_seconds']-sum(c.get('actual_seconds',0) for c in calls))<1e-8,'Total solve accounting')
need(completion['phase_budget']==1800 and completion['arithmetic_budget']==900 and abs(completion['phase_soft_overrun']-max(0,completion['phase_seconds']-1800))<1e-8 and abs(completion['arithmetic_soft_overrun']-max(0,completion['arithmetic_seconds']-900))<1e-8,'Arithmetic/phase accounting')
need(outcomes['ordinary_denominator']==completion['ordinary_denominator']==2 and completion['identity_hour_denominator']==168 and outcomes['original_model_claims_unchanged'] and not completion['original_model_equivalence_claim'],'Declared model/denominator scope')
ledger=read(ARM/'identity_proposal/hour_outcomes.json');need(len(ledger)==168 and [x['hour'] for x in ledger]==list(range(168)),'Identity hour denominator')
for r in ledger:
    h=read(ARM/'identity_proposal'/f"hour_{r['hour']:03d}.json");need(h['hour']==r['hour'] and h['status']==r['status'],'Hourly record')
    if r['status']=='EXACT_HOUR_POINT':need(h['exact_hour_pass'] and h['violations']==0 and len(h['values'])==103,'Accepted hourly record')
point_results={};point_values={}
for case,flag in zip(CASES[:2],('identity_strict_capped','control_strict_capped')):
    directory=ARM/case;claimed=outcomes['controls'].get(flag,False)
    if not (directory/'rational_point.json').exists():need(not claimed,'Claimed positive missing point');point_results[case]={'point_present':False,'producer_claim':False};continue
    artifact=read(directory/'rational_point.json');need(artifact['schema']=='exact-fixed-schedule-point-v1' and artifact['columns']==29400 and len(artifact['values'])==29400,'Rational full point shape')
    need(artifact['model_bindings']=={n:sha(directory/n) for n in ('matrix.npz','bounds.npz','integrality.npz','objective.npz')},'Point/model bindings')
    need([x['column'] for x in artifact['values']]==list(range(29400)),'Canonical point coordinates');p=[q(x['value']) for x in artifact['values']]
    m=v.load_model(directory);mask=array(directory,'integrality.npz','integrality',('|u1',),29400);check=strict_scan(m,p,mask);ncheck=native_scan(directory,p)
    meta=read(directory/'model_metadata.json');cost=array(directory,'objective.npz','objective',('<f8',),29400);need(cost==cost_for(meta),'Variant fossil objective');energy=sum((F(c)*x for c,x in zip(cost,p)),F(0));need(energy==q(ncheck['energy']),'Native/matrix energy correspondence')
    accepted=check['pass_strict'] and ncheck['pass_native'];need(not claimed or accepted,'Invalid claimed strict positive')
    if (directory/'strict_point_check.json').exists():
        saved=read(directory/'strict_point_check.json');need(saved['pass_strict']==check['pass_strict'] and saved['native']['pass_native']==ncheck['pass_native'] and saved['accepted_strict_capped']==accepted and q(saved['exact_objective'])==energy,'Producer strict point report')
    point_results[case]=dict(point_present=True,producer_claim=claimed,independent_strict_capped=accepted,original_rows=check,native=ncheck,energy=enc(energy));point_values[case]=p
if all(c in point_values for c in CASES[:2]):
    identity,control=(point_values[c] for c in CASES[:2]);data=v.read_npz(ARM/CASES[1]/'native_inputs.npz',('pmin','pmax','net','rows','source_hour','nodal'));order=data['source_hour'].values
    need(sorted(order)==list(range(168)),'Control permutation')
    for t,source in enumerate(order):
        for offset,width in ((0,41),(18984,24),(23016,38)):need(control[offset+t*width:offset+(t+1)*width]==identity[offset+source*width:offset+(source+1)*width],'Mapped P/theta/flow')
    need(control[6888:18984]==identity[6888:18984] and point_results[CASES[0]]['energy']==point_results[CASES[1]]['energy'],'Chronological states and energy preserved')
target_results=[]
need(len(outcomes['targets'])==2 and [x['case'] for x in outcomes['targets']]==list(TARGETS),'Two fixed target outcomes')
for case,declared in zip(TARGETS,outcomes['targets']):
    directory=ARM/case;m=v.load_model(directory);need((m.rows,m.cols)==(34513,29400),'Actual target matrix dimensions')
    need(array(directory,'integrality.npz','integrality',('|u1',),29400)==MASK,'Actual target original binary mask')
    classifications=read(directory/'classification.json') if (directory/'classification.json').exists() else None
    if classifications is None:
        need(declared['binary_status']=='UNKNOWN' and (directory/'classification_error.json').exists(),'Explicit classification failure')
        target_results.append(dict(case=case,binary_status='UNKNOWN',reason=declared.get('reason'),all_candidate_replay_complete=False));continue
    need(classifications==declared,'Target top-level classification correspondence')
    checks=[]
    if (directory/'raw_solver_ray.npz').exists():
        raw=array(directory,'raw_solver_ray.npz','ray',('<f8',),m.rows);need(all(math.isfinite(x) for x in raw),'Finite original raw ray')
        recipe=[(1,'raw'),(1,'projected'),(-1,'raw'),(-1,'projected')]
        need([(x['orientation'],x['kind']) for x in classifications['ray_candidates']]==recipe,'Exactly four fixed ray candidates')
        for (orientation,kind),item in zip(recipe,classifications['ray_candidates']):
            path=directory/f'ray_{orientation:+d}_{kind}.json';cert=read(path)
            need(cert['orientation']==orientation and cert['candidate']==kind and cert['distinct_flow_conserving_variant'],'Fixed candidate identity')
            need(cert['model_artifacts']=={n:sha(directory/n) for n in ('matrix.npz','bounds.npz')} and cert['raw_solver_ray_sha256']==sha(directory/'raw_solver_ray.npz') and cert['row_metadata_sha256']==sha(directory/'row_metadata.csv.gz') and cert['experiment_manifest_sha256']==MANIFEST,'Actual ray/matrix binding')
            expected={}
            for i,x0 in enumerate(raw):
                x=F(x0)*orientation
                if not x:continue
                if kind=='projected' and ((x>0 and not math.isfinite(m.row_lower[i])) or (x<0 and not math.isfinite(m.row_upper[i]))):continue
                expected[i]=x
            decoded={}
            for x in cert['multipliers']:
                need(x['row'] not in decoded,'Duplicate certificate row');f=float.fromhex(x['value_hex']);need(math.isfinite(f),'Finite multiplier');decoded[x['row']]=F(f)
            need(decoded==expected,'Actual fixed raw/projection coefficients')
            own=independent_ray(m,decoded)
            try:kernel_check=v.check_ray(m,decoded,TAU)
            except v.InvalidInput as error:
                need('verification' not in cert and 'rejected_reason' in item and (not own['admissible'] or not decoded),'Rejected candidate classification')
                checks.append(dict(orientation=orientation,kind=kind,rejected=True,reason=str(error)));continue
            need(own['admissible'] and kernel_check==cert['verification']==item['verification'],'Exact kernel replay correspondence')
            for key,ownkey in [('separation_gap','gap'),('expanded_separation_gap','expanded_gap')]:
                actual=kernel_check[key];need(F(int(actual['numerator']),int(actual['denominator']))==q(own[ownkey]),'Independent signed-row/box separation')
            need(kernel_check['strict_pass']==own['strict_pass'] and kernel_check['expanded_pass']==own['expanded_pass'],'Strict and expanded classification')
            checks.append(dict(orientation=orientation,kind=kind,rejected=False,verification=own,certificate_sha256=sha(path)))
    chosen=next((x for x in checks if x.get('verification',{}).get('expanded_pass')),None)
    if chosen is None:chosen=next((x for x in checks if x.get('verification',{}).get('strict_pass')),None)
    if chosen is not None:
        selected=classifications['selected'];need(selected and selected['orientation']==chosen['orientation'] and selected['kind']==chosen['kind'],'First robust otherwise first strict candidate selection')
        need(classifications['binary_status']=='CERTIFIED_VARIANT_NEGATIVE' and classifications['robust_expanded']==chosen['verification']['expanded_pass'],'New-variant negative classification')
    else:need(classifications['selected'] is None and classifications['binary_status']=='UNKNOWN','Uncertified target remains unknown')
    continuous=None
    if 'continuous_point_only' in classifications:
        data=v.read_npz(directory/'numerical_point.npz',('vector','row_activity'))['vector'];need(data.shape==(29400,) and all(math.isfinite(x) for x in data.values),'Finite continuous point')
        continuous=v.check_point(m,data.values,(0,)*29400,TAU);need(continuous==classifications['continuous_point_only'] and continuous['binary_coordinates']==0,'Continuous-only replay')
    target_results.append(dict(case=case,binary_status=classifications['binary_status'],candidates=checks,selected=None if chosen is None else {'orientation':chosen['orientation'],'kind':chosen['kind']},continuous_only=continuous))
verify_inputs();need(snapshot()==before,'Producer artifacts changed during review')
result=dict(status='INDEPENDENT_BRANCH_FLOW_POSTRUN_PASS',model_scope='Distinct flow-conserving DC variant; no original-model equivalence or outcome relabeling',frozen_bindings=103,manifest_sha256=MANIFEST,producer_source_imports=0,optimizer_calls_by_reviewer=0,point_replays=point_results,target_replays=target_results,identity_hour_denominator=168,identity_hour_counts=dict(Counter(r['status'] for r in ledger)),producer_calls=calls,producer_completion=completion,producer_hashes=before,all_frozen_inputs_and_outputs_unchanged=True,elapsed_s=time.perf_counter()-start)
with (OUT/'postrun_review.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'status':result['status'],'elapsed_s':result['elapsed_s'],'points':{n:p.get('independent_strict_capped',False) for n,p in point_results.items()},'targets':[(r['case'],r['binary_status']) for r in target_results]}))
