import csv,gzip,hashlib,importlib.util,json,math,re,sys,time
from collections import Counter
from datetime import datetime,timezone
from fractions import Fraction as F
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(r'C:/Users/gmalkawi/.codex/worktrees/dsc-temporal-information/3')
ARM=ROOT/'results/research8h/branch_flow_strict_energy';OUT=ROOT/'results/research8h/branch_flow_energy_independent_review'
OLD=ROOT/'results/research8h/hour_of_day';GEN=ROOT/'reproducibility/native_sources/rts_inputs/raw/RTS-GMLC_v0.2.3/gen.csv'
CASES=('january_identity','seed_26093200','seed_26093201');TARGETS=CASES[1:]
MANIFEST='7ffffe82e6046daff5dcd610337c2e8cb333009c38ec9acfcdb9741f8cbadbb7'
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
    need((m.rows,m.cols)==(34512,29400) and len(p)==29400 and mask==MASK,'Full variant dimensions/mask')
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
    return dict(pass_strict=count==0,violations=count,first_violations=fails,rows_checked=34512,columns_checked=29400,binary_coordinates=12096,tau=0)
def native_scan(directory,p):
    meta=read(directory/'model_metadata.json');graph=read(directory/'graph.json');data=v.read_npz(directory/'native_inputs.npz',('pmin','pmax','net','rows','source_hour','nodal'))
    need(data['pmin'].shape==data['pmax'].shape==(168,41) and data['nodal'].shape==(168,24),'Native data shapes')
    need(all(math.isfinite(x) for name in ('pmin','pmax','nodal','net') for x in data[name].values),'Finite native data')
    spec_rows=read(directory/'native_spec.json');need([x['uid'] for x in spec_rows]==meta['unit_names'],'Native spec ordering')
    for specrow in spec_rows:
        g=native[specrow['uid']];need(specrow['bus']==int(g['Bus ID']) and specrow['category']==g['Category'],'Raw native bus/category provenance')
        isthermal=specrow['uid'] in meta['thermal_unit_names'];need(specrow['thermal']==isthermal,'Thermal native flag')
        if isthermal:
            need(specrow['minimum_up']==math.ceil(float(g['Min Up Time Hr'])) and specrow['minimum_down']==math.ceil(float(g['Min Down Time Hr'])),'Native residence provenance')
            need(q(specrow['hourly_rational'])==F(float(g['Ramp Rate MW/Min'])*60.0),'Native hourly ramp provenance')
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
    return dict(pass_native=not failures,violations=len(failures),first_violations=failures[:20],energy=enc(energy),aggregate_authority='exact sum of native nodal loads; old net not imposed')

def model_bindings(d):return {n:sha(d/n) for n in ('matrix.npz','bounds.npz','integrality.npz','objective.npz')}
def lower_certificate(m,c,dual):
    r=list(map(F,c));beta=F(0)
    for i,x in dual.items():
        endpoint=m.row_lower[i] if x>0 else m.row_upper[i]
        if not math.isfinite(endpoint):return None
        beta+=x*F(endpoint)
        for z in range(m.indptr[i],m.indptr[i+1]):r[m.indices[z]]-=x*F(m.data[z])
    box=sum((x*F(m.lower[j] if x>=0 else m.upper[j]) for j,x in enumerate(r)),F(0))
    # Independently recombine c*x >= selected row support + residual-box support.
    return dict(lower=beta+box,beta=beta,box=box,residual=r)
def lower_replay(case):
    d=ARM/case;m=v.load_model(d);c=array(d,'objective.npz','objective',('<f8',),m.cols)
    need((m.rows,m.cols)==(34512,29400) and c==cost_for(read(d/'model_metadata.json')),'Full uncapped objective/model')
    path=d/'lower_bound.json'
    if not path.exists():
        need((d/'lower_error.json').exists(),'Explicit missing lower cause')
        return None,dict(case=case,status='NO_LOWER',error=read(d/'lower_error.json'))
    records=read(path);rawpath=d/'raw_row_dual.npz';candidates=[('zero',{})]
    if rawpath.exists():
        raw=array(d,'raw_row_dual.npz','row_dual',('<f8',),m.rows);need(all(math.isfinite(x) for x in raw),'Finite returned dual')
        for sign in (1,-1):
            full={i:F(x)*sign for i,x in enumerate(raw) if x}
            projected={i:x for i,x in full.items() if math.isfinite(m.row_lower[i] if x>0 else m.row_upper[i])}
            candidates.extend([(f'{sign:+d}_raw',full),(f'{sign:+d}_projected',projected)])
    need([x['candidate'] for x in records['candidates']]==[x[0] for x in candidates] and records['tau']==0,'Fixed candidate denominator/order')
    selected=None;reviews=[]
    for (name,dual),decl in zip(candidates,records['candidates']):
        cert=read(d/('lower_'+name+'.json'))
        need(cert['candidate']==name and cert['model_bindings']==model_bindings(d),'Lower candidate/model binding')
        need(cert['raw_dual_sha256']==(sha(rawpath) if rawpath.exists() else None),'Raw dual binding')
        decoded={}
        for item in cert['multipliers']:
            i=item['row'];f=float.fromhex(item['value_hex']);need(type(i) is int and 0<=i<m.rows and i not in decoded and math.isfinite(f) and f!=0,'Multiplier representation')
            decoded[i]=F(f)
        need(decoded==dual,'Predeclared raw/projection recipe')
        computed=lower_certificate(m,c,dual)
        if computed is None:
            need(cert['valid']==decl['valid']==False and 'reason' in cert,'Invalid selected endpoint rejected')
            reviews.append(dict(candidate=name,valid=False));continue
        need(cert['valid']==decl['valid']==True and cert['tau']==0,'Valid lower certificate flag')
        need(q(cert['lower_bound'])==computed['lower'] and q(cert['row_term'])==computed['beta'] and q(cert['box_term'])==computed['box'],'Exact row and residual-box terms')
        need([(x['column'],q(x['value'])) for x in cert['residual']]==[(j,x) for j,x in enumerate(computed['residual']) if x],'Complete exact stationarity residual')
        if selected is None or computed['lower']>selected[1]:selected=(name,computed['lower'])
        reviews.append(dict(candidate=name,valid=True,lower=enc(computed['lower']),residual_nonzeros=sum(bool(x) for x in computed['residual'])))
    need(selected is not None and selected[1]>=0 and records['selected']['candidate']==selected[0] and q(records['selected']['lower_bound'])==selected[1],'Largest valid bound, first tie')
    return selected[1],dict(case=case,status='EXACT_STRICT_LOWER_REPLAY_PASS',selected=selected[0],lower=enc(selected[1]),candidates=reviews)
def point_replay(case):
    global fixed
    d=ARM/case;artifact=read(d/'rational_point.json')
    need(artifact['schema']=='exact-fixed-schedule-point-v1' and artifact['columns']==29400 and len(artifact['values'])==29400,'Rational point shape')
    need(artifact['model_bindings']==model_bindings(d),'Point/model bindings')
    need([x['column'] for x in artifact['values']]==list(range(29400)),'Canonical full coordinates')
    point=[q(x['value']) for x in artifact['values']]
    fixed_rows=read(d/'fixed_schedule.json');fixed={r['column']:q(r['value']) for r in fixed_rows}
    need(len(fixed_rows)==len(fixed)==12096 and set(fixed)==set(range(6888,18984)) and all(x in (0,1) for x in fixed.values()),'Full fixed binary schedule')
    m=v.load_model(d);mask=array(d,'integrality.npz','integrality',('|u1',),29400);scan=strict_scan(m,point,mask);native_result=native_scan(d,point)
    c=array(d,'objective.npz','objective',('<f8',),29400);need(c==cost_for(read(d/'model_metadata.json')),'Native fossil objective')
    energy=sum((F(x)*y for x,y in zip(c,point)),F(0));need(energy==q(native_result['energy']),'Objective/native energy equality')
    accepted=scan['pass_strict'] and native_result['pass_native'];savedpath=d/('identity_upper.json' if case=='january_identity' else 'strict_uncapped_point_check.json')
    if savedpath.exists():
        saved=read(savedpath);need(saved['pass_strict']==scan['pass_strict'] and saved['native']['pass_native']==native_result['pass_native'] and saved['accepted_strict_uncapped']==accepted and q(saved['exact_objective'])==energy,'Strict full/native checker correspondence')
        need(saved['point_sha256']==sha(d/'rational_point.json'),'Point hash')
    else:need(case!='january_identity' and (d/'upper_error.json').exists(),'Unfinished point check must have explicit upper error')
    return energy,dict(case=case,accepted_strict_uncapped=accepted,original_rows=scan,native=native_result,exact_energy=enc(energy),point_sha256=sha(d/'rational_point.json')),point

def main():
    global v,bindings,native
    start=time.perf_counter();completion=read(ARM/'completion.json');outcomes=read(ARM/'outcomes.json');calls=read(ARM/'calls.json');freeze=read(ARM/'prepared_freeze.json')
    bindings=read(ARM/'input_manifest.json');need(len(bindings)==355 and len({r['path'] for r in bindings})==355,'355 frozen bindings');verify_inputs();before=snapshot()
    prepared=read(ROOT/'results/research8h/branch_flow_energy_prepared_review.json');need(prepared['status']=='INDEPENDENT_STRICT_ENERGY_PREPARED_PASS' and prepared['frozen_bindings']==355,'Independent prepared gate')
    need(prepared['source_sha256']==sha(ROOT/'results/research8h/branch_flow_energy_prepared_review.py')=='f8efe7a937fd5b649e31c895ba50790fb48f09ff3f152fd6e771980527662a0f','Parent prepared reviewer identity')
    k=ROOT/'src/research8h_standalone_verify.py';need(sha(k)=='708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f','Pinned decoder')
    spec=importlib.util.spec_from_file_location('strict_energy_independent_npz_kernel',k);v=importlib.util.module_from_spec(spec);sys.modules[spec.name]=v;spec.loader.exec_module(v)
    need(sha(GEN)=='988466f29132b73739de60c9204dd4a2a9ceb0adf572e5966c086611272f4068','Additional raw GEN provenance binding')
    with GEN.open(encoding='utf-8-sig',newline='') as f:raw_native=list(csv.DictReader(f))
    native={r['GEN UID']:r for r in raw_native};need(len(native)==len(raw_native),'Unique native GEN roster')
    callorder=(*CASES,*(x+'_proposal' for x in TARGETS));need([x['case'] for x in calls]==list(callorder)==freeze['calls'],'Five fixed calls/order')
    marker=read(ARM/'execution_marker.json');need(marker['manifest_sha256']==MANIFEST,'Start manifest binding')
    launched=datetime.fromisoformat(marker['utc']);need(launched<=datetime(2026,9,27,3,35,tzinfo=timezone.utc) and (datetime(2026,9,27,4,tzinfo=timezone.utc)-launched).total_seconds()>=1500,'Fixed latest-start gate')
    need(freeze['phase']==1800 and freeze['arithmetic_phase']==900 and freeze['limit_per_call']==60,'Preserved budgets')
    attempted=0;solvetime=0.;ledger=[]
    for call in calls:
        d=ARM/call['case'];need(call['optimizer_calls'] in (0,1),'Attempted-call count');attempted+=call['optimizer_calls'];solvetime+=call.get('actual_seconds',0.)
        if call['optimizer_calls']:
            decision=read(d/'launch_decision.json');need(decision['configured_seconds']==60 and decision['remaining_seconds']>=65,'Saved admission record')
            log=(d/'solver.log').read_text(encoding='utf-8-sig');need(log.count('Running HiGHS')==1,'One numerical invocation')
            if (d/'solver_result.json').exists():need(read(d/'solver_result.json')==call and call['configured_seconds']==60,'Saved solver result')
            else:need(call['status']=='POSTCALL_ERROR' and read(d/'call_error.json')==call,'Truthful attempted post-call failure')
        else:need(call['status'] in ('NOT_STARTED_GUARD','NOT_STARTED_AFTER_IO_GUARD','PRECALL_ERROR'),'Explicit no-call classification')
        ledger.append(dict(case=call['case'],attempted=bool(call['optimizer_calls']),status=call['status'],seconds=call.get('actual_seconds',0.)))
    need(attempted==completion['optimizer_calls']<=completion['maximum_calls']==5 and abs(solvetime-completion['actual_solve_seconds'])<1e-8,'Total numerical accounting')
    need(abs(max(0.,completion['phase_seconds']-1800)-completion['phase_soft_overrun'])<1e-8 and abs(max(0.,completion['arithmetic_seconds']-900)-completion['arithmetic_soft_overrun'])<1e-8,'Soft phase accounting')
    need(outcomes['target_denominator']==2 and outcomes['target_hour_denominator']==336 and outcomes['tau']==0 and outcomes['distinct_flow_model'],'Strict distinct-model denominator')
    lower={};lower_reviews=[]
    for case in CASES:
        value,record=lower_replay(case);lower_reviews.append(record)
        if value is not None:lower[case]=value
    upper={};points=[];hours=[]
    value,record,point=point_replay(CASES[0]);need(record['accepted_strict_uncapped'],'Inherited strict identity');upper[CASES[0]]=value;points.append(record)
    old=read(ROOT/'results/research8h/branch_flow_encoding/january_identity/rational_point.json');need([q(x['value']) for x in old['values']]==point,'Inherited identity values untouched')
    need(q(outcomes['identity_upper'])==value,'Identity upper outcome')
    need((outcomes['identity_lower'] is None and CASES[0] not in lower) or (outcomes['identity_lower'] is not None and q(outcomes['identity_lower'])==lower[CASES[0]]),'Identity lower outcome')
    need([r['case'] for r in outcomes['upper_records']]==list(TARGETS),'Both target upper records retained')
    for case,up in zip(TARGETS,outcomes['upper_records']):
        prop=ARM/(case+'_proposal');path=prop/'hour_outcomes.json'
        if path.exists():
            hl=read(path);need(len(hl)==168 and [x['hour'] for x in hl]==list(range(168)),'168 chronological hourly records')
            with gzip.open(prop/'exact_blocks.json.gz','rt',encoding='utf-8') as f:blocks=json.load(f)
            need(len(blocks)==168,'168 fixed exact blocks')
            counts=Counter();assembled={}
            for entry,block in zip(hl,blocks):
                t=entry['hour'];r=read(prop/f'hour_{t:03d}.json');need(r['hour']==block['hour']==t and r['status']==entry['status'],'Per-hour correspondence');counts[r['status']]+=1
                if 'values' in r:
                    need([x['column'] for x in r['values']]==block['columns'] and len(r['values'])==103,'Fixed103-column mapping')
                    values=[q(x['value']) for x in r['values']];assembled.update(zip(block['columns'],values));bad=0
                    for x,lo,hi in zip(values,block['lower'],block['upper']):
                        if (lo is not None and x<q(lo)) or (hi is not None and x>q(hi)):bad+=1
                    for row in block['rows']:
                        lhs=sum((q(coef)*values[j] for j,coef in row['terms']),F(0));lo=row['lower'];hi=row['upper']
                        if (lo is not None and lhs<q(lo)) or (hi is not None and lhs>q(hi)):bad+=1
                    need(r['exact_hour_pass']==(bad==0),'Independent hourly row/box membership')
                    need((r['status']=='EXACT_HOUR_POINT')==(bad==0),'Hourly candidate classification')
            if 'counts' in up:need(up['counts']==dict(counts) and up['hour_denominator']==168 and read(ARM/case/'upper_bound.json')==up,'Complete reconstruction denominator')
            else:need(up['status']=='NO_UPPER' and read(ARM/case/'upper_error.json')==up,'Post-hour phase failure recorded')
            hours.append(dict(case=case,denominator=168,counts=dict(counts),candidate_hour_memberships_independently_replayed=True))
        else:
            need(up['status']=='NO_UPPER' and (ARM/case/'upper_error.json').exists(),'Missing hour phase explicitly unresolved');hours.append(dict(case=case,status='NO_UPPER',error=read(ARM/case/'upper_error.json')))
        if (ARM/case/'rational_point.json').exists():
            energy,result,point=point_replay(case);points.append(result)
            if path.exists():need(all(point[j]==x for j,x in assembled.items()),'Full point from the fixed hourly candidates')
            if up['status']=='STRICT_UNCAPPED_UPPER':need(result['accepted_strict_uncapped'] and q(up['upper_bound'])==energy,'Accepted strict target upper');upper[case]=energy
            else:
                need(up['status']=='NO_UPPER','Unaccepted point preserved')
                result['producer_upper_unaccepted']=True
                if result['accepted_strict_uncapped']:need((ARM/case/'upper_error.json').exists(),'A valid unaccepted point needs explicit completion failure')
        else:need(up['status']=='NO_UPPER','Missing point cannot be upper')
    targets=[];need([r['case'] for r in outcomes['targets']]==list(TARGETS),'Two target energy intervals')
    for saved in outcomes['targets']:
        case=saved['case'];need((saved['lower'] is None and case not in lower) or (saved['lower'] is not None and q(saved['lower'])==lower[case]),'Target lower outcome');need((saved['upper'] is None and case not in upper) or (saved['upper'] is not None and q(saved['upper'])==upper[case]),'Target upper outcome')
        if all(c in lower and c in upper for c in (CASES[0],case)):
            li,ui,lt,ut=lower[CASES[0]],upper[CASES[0]],lower[case],upper[case];need(li<=ui and lt<=ut,'No lower/upper contradiction')
            need(saved['status']=='FINITE_STRICT_INTERVAL' and q(saved['penalty_lower'])==lt-ui and q(saved['penalty_upper'])==ut-li and saved['strictly_positive']==(lt>ui),'Exact signed optimum-difference enclosure')
            if li>0 and lt>=0:need([q(x) for x in saved['percent_interval']]==[100*(lt/ui-1),100*(ut/li-1)],'Exact percentage interval')
            else:need('percent_interval' not in saved,'No invalid ratio denominator')
        else:need(saved['status']=='INCOMPLETE_BOUNDS' and all(k not in saved for k in ('penalty_lower','penalty_upper','strictly_positive','percent_interval')),'Missing evidence stays incomplete')
        targets.append(saved)
    verify_inputs();need(snapshot()==before,'Frozen inputs or producer outputs changed during review');need(sha(GEN)=='988466f29132b73739de60c9204dd4a2a9ceb0adf572e5966c086611272f4068','Raw GEN changed during review')
    report=dict(status='INDEPENDENT_STRICT_BRANCH_ENERGY_POSTRUN_PASS',model_scope='Distinct flow-conserving uncapped DC variant; strict tau=0 only, not original-model equivalence',frozen_bindings=355,manifest_sha256=MANIFEST,optimizer_calls_by_reviewer=0,producer_imports=0,lower_replays=lower_reviews,point_replays=points,hour_replays=hours,targets=targets,producer_calls=ledger,producer_completion=completion,producer_output_hashes=before,additional_native_gen_sha256=sha(GEN),all_frozen_inputs_and_outputs_unchanged=True,launch_scope='Durable initial03:35 gate and saved call admission records replayed; exact post-I/O call instant is enforced by reviewed source but not separately timestamped.',source_sha256=sha(Path(__file__)),elapsed_s=time.perf_counter()-start)
    with (OUT/'postrun_review.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps(dict(status=report['status'],elapsed_s=report['elapsed_s'],strict_binary_points=sum(p['accepted_strict_uncapped'] for p in points),target_statuses=[x['status'] for x in targets])))
if __name__=='__main__':main()
