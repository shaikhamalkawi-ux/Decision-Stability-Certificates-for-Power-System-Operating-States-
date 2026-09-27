import csv,gzip,hashlib,importlib.util,json,math,re,sys,time
from collections import Counter
from datetime import datetime,timezone
from fractions import Fraction as F
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(r'C:/Users/gmalkawi/.codex/worktrees/dsc-temporal-information/3')
ARM=ROOT/'results/research8h/exact_fixed_schedule'
OUT=ROOT/'results/research8h/exact_fixed_schedule_independent_review'
SOURCE=ROOT/'results/research8h/seasonal_reference/month_01'
CAPPED=ROOT/'results/research8h/seasonal_transfer/january_identity'
GEN=ROOT/'reproducibility/native_sources/rts_inputs/raw/RTS-GMLC_v0.2.3/gen.csv'
KERNEL=ROOT/'src/research8h_standalone_verify.py'
EXPECTED={'manifest':'397fdbdd982ec11dc7265d842733df40fc0ad66a22922ea40e06cfebdaf03da9','kernel':'708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f','source':'733f57ae928c72dcf063c224e728d1ad1a01d52e93c068f63147d988c16e3a77','checker':'9cb836d420308a2ffc5b6e50e78cb565a823d5b65d1223c0f53d98910de5680d'}
def need(ok,why):
    if not ok:raise ValueError(why)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def unique(pairs):
    d={}
    for k,v in pairs:need(k not in d,'Duplicate JSON key');d[k]=v
    return d
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'),object_pairs_hook=unique,parse_constant=lambda s:(_ for _ in ()).throw(ValueError('Nonfinite JSON')))
def q(d):
    need(type(d) is dict and set(d)=={'numerator','denominator'},'Rational schema')
    n,b=d['numerator'],d['denominator']
    need(type(n) is str and type(b) is str and re.fullmatch(r'0|-?[1-9][0-9]*',n) and re.fullmatch(r'[1-9][0-9]*',b),'Rational spelling')
    need(len(n)<=2468 and len(b)<=2467,'Rational textual bit bound')
    a,c=int(n),int(b);need(abs(a).bit_length()<=8192 and c.bit_length()<=8192,'Rational bit bound')
    v=F(a,c);need(v.numerator==a and v.denominator==c,'Rational reduction');return v
def enc(x):return {'numerator':str(x.numerator),'denominator':str(x.denominator)}
def array(folder,file,key,dtype,length):return v.vector(v.read_npz(folder/file,(key,))[key],dtype,length,key)
def snapshot():return {str(p.relative_to(ARM)).replace('\\','/'):sha(p) for p in ARM.rglob('*') if p.is_file()}
def manifest_check(records):
    need(len(records)==34 and len({r['path'] for r in records})==34,'34 unique frozen bindings')
    for r in records:
        p=Path(r['path']);need(p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],'Changed frozen file '+str(p))
def point_check(model,point,mask,fixed):
    failures=[];count=0
    def fail(where):
        nonlocal count
        count+=1
        if len(failures)<20:failures.append(where)
    need(len(point)==model.cols and mask==tuple(int(6888<=j<18984) for j in range(model.cols)),'Full original shape/mask')
    for j,x in enumerate(point):
        if not F(model.lower[j])<=x<=F(model.upper[j]):fail({'column':j,'kind':'box'})
        if mask[j] and (x not in (0,1) or x!=fixed[j]):fail({'column':j,'kind':'fixed_binary'})
    for i in range(model.rows):
        lhs=sum((F(model.data[z])*point[model.indices[z]] for z in range(model.indptr[i],model.indptr[i+1])),F(0))
        if math.isfinite(model.row_lower[i]) and lhs<F(model.row_lower[i]):fail({'row':i,'side':'lower','gap':enc(F(model.row_lower[i])-lhs)})
        if math.isfinite(model.row_upper[i]) and lhs>F(model.row_upper[i]):fail({'row':i,'side':'upper','gap':enc(lhs-F(model.row_upper[i]))})
    return dict(pass_strict=count==0,rows=model.rows,columns=model.cols,binary_coordinates=sum(mask),tau=0,violations=count,first_violations=failures)
def native_check(point,meta):
    data=v.read_npz(SOURCE/'native_inputs.npz',('pmin','pmax','net','rows','nodal'))
    need(data['pmin'].shape==data['pmax'].shape==(168,41) and data['net'].shape==(168,) and data['nodal'].shape==(168,24),'Native shapes')
    need(all(data[n].dtype=='<f8' and all(math.isfinite(x) for x in data[n].values) for n in ('pmin','pmax','net','nodal')),'Native float values')
    with GEN.open(encoding='utf-8-sig',newline='') as f: native=list(csv.DictReader(f))
    need(len({r['GEN UID'] for r in native})==len(native),'Native duplicate'); native={r['GEN UID']:r for r in native}
    names=meta['unit_names'];thermals=meta['thermal_unit_names'];need(len(names)==41 and len(thermals)==24 and len(set(thermals))==24,'Native roster')
    failures=[]
    for t in range(168):
        p=point[t*41:(t+1)*41]
        if sum(p,F(0))!=F(data['net'].values[t]):failures.append([t,'ALL','aggregate'])
        for j,n in enumerate(names):
            lo=F(data['pmin'].values[t*41+j]);hi=F(data['pmax'].values[t*41+j])
            if not 0<=p[j]<=hi:failures.append([t,n,'availability'])
            if native[n]['Category']=='Hydro' and p[j]!=lo:failures.append([t,n,'hydro_fixed'])
        for k,n in enumerate(thermals):
            j=names.index(n);u=point[6888+t*24+k];y=point[10920+t*24+k];z=point[14952+t*24+k]
            lo=F(data['pmin'].values[t*41+j]);hi=F(data['pmax'].values[t*41+j])
            if not lo*u<=p[j]<=hi*u:failures.append([t,n,'committed_output'])
            if not t:
                if y or z:failures.append([t,n,'initial_transition'])
                continue
            prev=point[6888+(t-1)*24+k];delta=u-prev
            if y!=max(delta,0) or z!=max(-delta,0):failures.append([t,n,'canonical_transition'])
            if delta:
                dwell=math.ceil(float(native[n]['Min Up Time Hr' if delta>0 else 'Min Down Time Hr']))
                if any(point[6888+s*24+k]!=u for s in range(t,min(168,t+dwell))):failures.append([t,n,'residence'])
            if u==prev==1 and abs(p[j]-point[(t-1)*41+j])>F(float(native[n]['Ramp Rate MW/Min'])*60.0):failures.append([t,n,'on_on_ramp'])
    return dict(pass_native=not failures,violations=len(failures),first_violations=failures[:20],native_rate_convention='binary64(rate*60) then exact rational',network_scope='original matrix checked separately')
start=time.perf_counter()
need(sha(KERNEL)==EXPECTED['kernel'],'Kernel source changed')
spec=importlib.util.spec_from_file_location('independent_exact_input_decoder',KERNEL);v=importlib.util.module_from_spec(spec);sys.modules[spec.name]=v;spec.loader.exec_module(v)
need(sha(ARM/'input_manifest.json')==EXPECTED['manifest'],'Prepared manifest changed')
records=read(ARM/'input_manifest.json');manifest_check(records);before=snapshot()
freeze=read(ARM/'prepared_freeze.json');need(freeze['source_sha256']==EXPECTED['source'] and freeze['checker_sha256']==EXPECTED['checker'],'Reviewed sources')
completion=read(ARM/'completion.json');outcomes=read(ARM/'outcomes.json')
need(len(outcomes)==168 and [r['hour'] for r in outcomes]==list(range(168)),'Full ordered hour denominator')
need(completion.get('optimizer_calls') in (0,1),'Single optimizer budget')
if completion['optimizer_calls']==1:
    need(completion.get('no_full_UC_negative_claim') is True,'Null scope guard')
    if 'outcome_counts' in completion:need(dict(Counter(r['status'] for r in outcomes))==completion['outcome_counts'],'Ledger counts')
    if (ARM/'solver_result.json').exists():
        sr=read(ARM/'solver_result.json');need(sr['optimizer_calls']==1 and sr['configured_seconds']==60 and not sr['exact_feasibility_claim'],'Solver declaration')
        need(abs(sr['soft_overrun_seconds']-max(0,sr['actual_seconds']-60))<1e-9,'Solver time accounting')
        ld=read(ARM/'launch_decision.json');need(ld['utc_remaining_s']>=65,'Admitted call remaining time')
        need(datetime.fromisoformat(ld['utc'])<datetime(2026,9,27,4,tzinfo=timezone.utc),'Call admission UTC')
        for r in outcomes:
            detail=read(ARM/f"hour_{r['hour']:03d}.json");need(detail['hour']==r['hour'] and detail['status']==r['status'],'Hour file status')
            if r['status']=='EXACT_HOUR_POINT':need(detail['exact_hour_pass'] and detail['violations']==0 and len(detail['values'])==65,'Complete exact hour record')
        need(completion['exact_phase_budget']==900 and abs(completion['exact_soft_overrun_seconds']-max(0,completion['exact_phase_seconds']-900))<1e-9,'Arithmetic phase accounting')
        need(completion['phase_includes_final_hash_and_outcomes_write'] and completion['phase_excludes_completion_record_write'],'Declared phase boundary')
positive=bool(completion.get('accepted_strict',False));point_report=None
if (ARM/'rational_point.json').exists():
    model=v.load_model(SOURCE);meta=read(SOURCE/'model_metadata.json');raw=read(ARM/'rational_point.json')
    need(raw['schema']=='exact-fixed-schedule-point-v1' and raw['columns']==23016 and len(raw['values'])==23016,'Point schema/length')
    need(raw['model_bindings']=={n:sha(SOURCE/n) for n in ('matrix.npz','bounds.npz','integrality.npz','objective.npz')},'Original point bindings')
    need([r['column'] for r in raw['values']]==list(range(23016)),'Canonical point ordering');point=[q(r['value']) for r in raw['values']]
    mask=array(SOURCE,'integrality.npz','integrality',('|u1',),23016)
    old=array(CAPPED,'constructive_vector.npz','vector',('<f8',),23016);fixed={j:F(old[j]) for j,flag in enumerate(mask) if flag}
    saved=read(ARM/'fixed_schedule.json');need(len(saved)==12096 and {r['column']:q(r['value']) for r in saved}==fixed,'Fixed binary schedule identity')
    need(all(x in (0,1) for x in fixed.values()),'Old schedule binary')
    point_report=point_check(model,point,mask,fixed);native=native_check(point,meta);point_report['native']=native
    cost=array(SOURCE,'objective.npz','objective',('<f8',),23016)
    fossil=[meta['unit_names'].index(n) for n in meta['thermal_unit_names'] if n!='121_NUCLEAR_1']
    need(len(fossil)==23 and cost==tuple(float(j<6888 and j%41 in fossil) for j in range(23016)),'Fossil objective')
    energy=sum((F(c)*x for c,x in zip(cost,point)),F(0));point_report['energy']=enc(energy)
    producer=read(ARM/'strict_original_replay.json')
    need(producer['pass_strict']==point_report['pass_strict'] and producer['native']['pass_native']==native['pass_native'] and q(producer['exact_objective'])==energy,'Original replay correspondence')
    need(producer['existing_cap_comparison']['within_cap']==(energy<=23195) and q(producer['existing_cap_comparison']['energy'])==energy,'Cap comparison')
    accepted=point_report['pass_strict'] and native['pass_native']
    need(accepted==positive,'Final acceptance correspondence')
    if accepted and energy<=23195:
        cap=v.load_model(CAPPED);capmask=array(CAPPED,'integrality.npz','integrality',('|u1',),23016);need(capmask==mask,'Capped original mask')
        point_report['capped']=point_check(cap,point,capmask,fixed);need(point_report['capped']['pass_strict'],'Original capped strict replay')
        # The capped feasibility objective is zero. It is deliberately not equated to the uncapped fossil objective.
    if positive:need(all(r['status']=='EXACT_HOUR_POINT' for r in outcomes) and completion['status']=='STRICT_NOMINAL_WITNESS','Full accepted denominator')
else:need(not positive,'Accepted witness missing point')
null_candidate_review=None
if not positive and not (ARM/'rational_point.json').exists() and (ARM/'basis.json').exists():
    hourly=[read(ARM/f'hour_{t:03d}.json') for t in range(168)]
    if all('values' in h for h in hourly):
        with gzip.open(ARM/'exact_blocks.json.gz','rt',encoding='utf-8') as f: blocks=json.load(f,object_pairs_hook=unique)
        basis=read(ARM/'basis.json')
        need(basis['valid'] and len(basis['column_status'])==10920 and len(basis['row_status'])==18648,'Basis denominator')
        need(len(blocks)==168 and [b['hour'] for b in blocks]==list(range(168)),'Block denominator')
        def endpoint(status,lo,hi):
            if lo is not None and hi is not None and lo==hi:return lo
            if status=='kLower' and lo is not None:return lo
            if status=='kUpper' and hi is not None:return hi
            if status=='kZero' and lo is None and hi is None:return F(0)
            raise ValueError('Unsupported archived nonbasic endpoint')
        candidate=[None]*23016
        fixed_list=read(ARM/'fixed_schedule.json');need(len(fixed_list)==12096,'Fixed schedule count')
        fixed={r['column']:q(r['value']) for r in fixed_list};need(len(fixed)==12096,'Unique fixed schedule indices')
        mask=array(SOURCE,'integrality.npz','integrality',('|u1',),23016)
        old=array(CAPPED,'constructive_vector.npz','vector',('<f8',),23016)
        need(fixed=={j:F(old[j]) for j,flag in enumerate(mask) if flag},'Null-candidate fixed schedule provenance')
        for j,x in fixed.items():candidate[j]=x
        per_hour=[];row_cursor=0;active_equations_checked=0;nonbasic_endpoints_checked=0
        for b,h in zip(blocks,hourly):
            t=b['hour'];cols=b['columns'];need([r['column'] for r in h['values']]==cols and len(cols)==65,'Hour candidate columns')
            x=[q(r['value']) for r in h['values']];lo=[q(a) for a in b['lower']];hi=[q(a) for a in b['upper']]
            cs=basis['column_status'][t*65:(t+1)*65];rs=basis['row_status'][row_cursor:row_cursor+111];row_cursor+=111
            basics=[j for j,s in enumerate(cs) if s=='kBasic'];active=[i for i,s in enumerate(rs) if s!='kBasic'];nonbasic=[j for j,s in enumerate(cs) if s!='kBasic']
            need(h['basic_original_columns']==[cols[j] for j in basics] and len(active)==len(basics),'Archived basic column selection')
            need(h['active_original_rows']==[b['rows'][i]['original_row'] for i in active],'Archived active row selection')
            need([r['column'] for r in h['nonbasic']]==[cols[j] for j in nonbasic],'Archived nonbasic coordinate order')
            for j,r in zip(nonbasic,h['nonbasic']):
                need(r['status']==cs[j] and q(r['value'])==x[j]==endpoint(cs[j],lo[j],hi[j]),'Nonbasic endpoint recovery')
                nonbasic_endpoints_checked+=1
            violations=sum(not low<=value<=high for low,value,high in zip(lo,x,hi))
            for i,r in enumerate(b['rows']):
                terms={int(j):q(a) for j,a in r['terms']};need(len(terms)==len(r['terms']),'Duplicate exact coefficient')
                lhs=sum((a*x[j] for j,a in terms.items()),F(0));lower=None if r['lower'] is None else q(r['lower']);upper=None if r['upper'] is None else q(r['upper'])
                if (lower is not None and lhs<lower) or (upper is not None and lhs>upper):violations+=1
                if i in active:
                    k=active.index(i);need(lhs==endpoint(rs[i],lower,upper)==q(h['active_endpoints'][k]),'Exact active basis equation')
                    active_equations_checked+=1
            need(violations==h['violations'] and (violations==0)==h['exact_hour_pass'],'Exact hour violation classification')
            per_hour.append(dict(hour=t,violations=violations,active_equations=len(active),nonbasic_coordinates=len(nonbasic)))
            for j,value in zip(cols,x):need(candidate[j] is None,'Overlapping candidate coordinates');candidate[j]=value
        need(all(type(x) is F for x in candidate),'Full diagnostic candidate coverage')
        original=point_check(v.load_model(SOURCE),candidate,mask,fixed)
        need(not original['pass_strict'],'Unexpected original feasible candidate: inspect null classification')
        null_candidate_review=dict(scope='Diagnostic reconstruction from existing hour records only; no alternate basis or full-UC negative claim',hours_checked=168,active_equations_checked=active_equations_checked,nonbasic_endpoints_checked=nonbasic_endpoints_checked,per_hour=per_hour,original_candidate_check=original)

manifest_check(records);need(snapshot()==before,'Producer outputs changed during replay')
result=dict(status='INDEPENDENT_EXACT_FIXED_SCHEDULE_POSTRUN_PASS',accepted_strict_witness=positive,hours=168,outcome_counts=dict(Counter(r['status'] for r in outcomes)),producer_completion=completion,point_replay=point_report,null_candidate_review=null_candidate_review,frozen_bindings=34,manifest_sha256=EXPECTED['manifest'],producer_hashes=before,optimizer_calls_by_reviewer=0,producer_source_imports=0,elapsed_s=time.perf_counter()-start,no_full_UC_negative_inferred=True)
with (OUT/'postrun_review.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'status':result['status'],'accepted_strict_witness':positive,'counts':result['outcome_counts'],'elapsed_s':result['elapsed_s']}))
