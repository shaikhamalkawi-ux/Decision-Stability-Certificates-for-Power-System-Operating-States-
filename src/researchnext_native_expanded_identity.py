"""One archived identity: native expanded upper and containment lower, no optimizer."""
from pathlib import Path
from fractions import Fraction as F
from datetime import datetime, timezone
import argparse, hashlib, importlib.util, json, math, sys, time

ROOT=Path(__file__).resolve().parents[1]
ARM=ROOT/'results/research_next/native_expanded_identity'
PRE=ARM/'prepared'
RUN=ARM/'run01'
PROTOCOL=ROOT/'docs/research_next/NATIVE_EXPANDED_IDENTITY_PROTOCOL.md'
COMPARE=ROOT/'results/research_next/orlib_native_compare_schema2'
OLD=ROOT/'results/research_next/orlib_preflight/solver_prepared01'
CASE=OLD/'outputs/identity__native_penalized'
TAU=F.from_float(1e-5)
LIMIT=120.0
PINS={
 'helper':(COMPARE/'INDEPENDENT_POSTRUN_REVIEW.py','6390b0f51a9385860ff28683c2610008173ea0fcb8b1ed40b686cbbfd7c06d3c'),
 'kernel':(ROOT/'src/research8h_standalone_verify.py','708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'),
 'comparison_review':(COMPARE/'INDEPENDENT_POSTRUN_REVIEW.json','50191cce91e6a4e8479500bfa0a1740b03d812848ee37620480b3e41ce584080'),
 'comparison':(COMPARE/'run01/comparison.json','2ad303026121cbef1952f234c2e65eade9ac897fb669aa138a1ffcae6ffb3125'),
 'comparison_manifest':(COMPARE/'prepared/manifest.json','ea2a05148c0d0b23b2c59faea9f0afcfd4a3b386e6e738adb97ca1b4610ab829'),
 'old_output_manifest':(OLD/'output_manifest.json','2713685311e705ea0c9b6080dee2594e9d077d37aea844efb0e093f722cf9a52'),
 'old_review':(ROOT/'results/research_next/orlib_preflight/INDEPENDENT_SOLVER_RESULT_REVIEW.json','a465a16acf67ca9a0925376f2a2b7d4338a24bac9bb276258d134f930d11f358'),
 'candidate':(CASE/'mip/candidate_vector.json','c24e7218930cf26a18dd1c2fc0fe7f36d1a180580c447ab5307fe07ee8781f6c'),
 'raw_lp':(CASE/'lp/raw_solution.npz','42551c9d8dc9acdaa64cfdbc44062586b6cb6ca3949d8606d301abeb89b2e71a'),
 'signed_bound':(CASE/'lp/signed_dual_bound.json','d1ca08949c6187e8c6c04d07c857fdae4b67117fcb70a117e87c57290ec5943c'),
 'theory':(ROOT/'docs/research_next/NATIVE_EXPANDED_CONTAINMENT_PROPOSAL.md','b5342b65753d4440c0c19551dba45fb100731cb4fcd9206499ac38a6c23fc1db'),
 'theory_review':(ROOT/'docs/research_next/NATIVE_EXPANDED_CONTAINMENT_REVIEW.md','20747ec68fb217c65c11779263851bae793c758a19c0be046c889ed93a5c5adb')}

def require(ok,why):
    if not ok:raise ValueError(why)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def utc():return datetime.now(timezone.utc).isoformat()
def save(p,x):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(x,f,indent=2,allow_nan=False);f.write('\n')
def q(x):
    require(type(x) in (int,float) and math.isfinite(x),'Finite binary64 input')
    return F(x)
def rat(x):return {'numerator':str(x.numerator),'denominator':str(x.denominator),'approximate':float(x)}
def unrat(x):
    r=F(int(x['numerator']),int(x['denominator']));require(x==rat(r),'Canonical archived rational record');return r
def binding(p):
    p=Path(p).resolve();b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def validate(items):
    for e in items:require(binding(e['path'])==e,'Changed input '+e['path'])
def load_module(name,path,expected):
    require(sha(path)==expected,'Pinned helper import')
    sys.dont_write_bytecode=True
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def guard(start):require(time.perf_counter()-start<=LIMIT,'120-second soft arithmetic phase exceeded')

def derive_bound(model,raw,tau,qr):
    require(len(raw)==len(model['rows']),'Row multiplier length')
    dual=[];changed=[];residual=[q(c['objective']) for c in model['columns']];beta=F(0)
    for i,(x,row) in enumerate(zip(raw,model['rows'])):
        d=q(x)
        if (d>0 and row['lower'] is None) or (d<0 and row['upper'] is None):d=F(0);changed.append(i)
        dual.append(d)
        if d:
            beta+=d*q(row['lower'] if d>0 else row['upper'])
            for j,a in row['coefficients']:residual[j]-=d*q(a)
    nominal=beta+sum((r*q(c['lower'] if r>=0 else c['upper']) for r,c in zip(residual,model['columns'])),F(0))
    slope=sum(map(abs,dual),F(0))+sum(map(abs,residual),F(0))
    expanded=nominal-tau*slope
    correction=tau*sum((min(residual[j],F(0)) for j in qr),F(0))
    # A second expression uses every widened endpoint directly.
    direct=F(0)
    for d,row in zip(dual,model['rows']):
        if d:direct+=d*(q(row['lower'])-tau if d>0 else q(row['upper'])+tau)
    for j,(r,c) in enumerate(zip(residual,model['columns'])):
        direct+=r*(q(c['lower'])-tau if r>=0 else q(c['upper'])+tau+(tau if j in qr else 0))
    require(direct==expanded+correction and correction<=0,'Exact correction/direct box identity')
    return dict(dual=dual,changed=changed,residual=residual,beta=beta,nominal=nominal,slope=slope,expanded=expanded,correction=correction,native_lower=direct)

def prepare():
    require(not PRE.exists() and not RUN.exists(),'Fresh one-case preparation only')
    for path,digest in PINS.values():require(sha(path)==digest,'Pinned provenance '+str(path))
    compare_manifest=read(PINS['comparison_manifest'][0]);validate(compare_manifest['inputs']+compare_manifest['copies'])
    require(read(PINS['comparison_review'][0])['status']=='PASS_INDEPENDENT_EXACT_NOMINAL_PROJECTION_EQUIVALENCE','Closed exact comparison gate')
    require(read(PINS['comparison'][0])['nominal_projection_equivalence'] is True,'Nominal premise')
    fixed={name:path for name,(path,_) in PINS.items()}
    for name in ('raw','parsed','normal','model'):fixed[name]=COMPARE/'prepared'/f'{name}.json'
    fixed.update(mip_result=CASE/'mip/result.json',mip_checks=CASE/'mip/exact_candidate_checks.json',lp_result=CASE/'lp/result.json',
      comparison_completion=COMPARE/'run01/completion.json',comparison_review_memo=COMPARE/'INDEPENDENT_POSTRUN_REVIEW.md',
      old_review_source=ROOT/'results/research_next/orlib_preflight/INDEPENDENT_SOLVER_RESULT_REVIEW.py',
      old_review_memo=ROOT/'results/research_next/orlib_preflight/INDEPENDENT_SOLVER_RESULT_REVIEW.md')
    output_lookup={e['path']:e for e in read(PINS['old_output_manifest'][0])['files']}
    for name in ('candidate','raw_lp','signed_bound','mip_result','mip_checks','lp_result'):
        p=fixed[name];e=output_lookup[p.relative_to(OLD).as_posix()]
        require(p.stat().st_size==e['bytes'] and sha(p)==e['sha256'],'Old output manifest role '+name)
    require(fixed['model'].read_bytes()==(OLD/'inputs/identity__native_penalized.json').read_bytes(),'Actual identity bridge')
    # Entry capture precedes payload copying; no point, dual or containment arithmetic.
    originals={str(p.resolve()):binding(p) for p in list(fixed.values())+[Path(__file__),PROTOCOL]}
    for e in compare_manifest['inputs']+compare_manifest['copies']:originals[e['path']]=e
    items=list(originals.values());validate(items);captured={name:p.read_bytes() for name,p in fixed.items()}
    for name,data in captured.items():
        e=originals[str(fixed[name].resolve())];require(len(data)==e['bytes'] and hashlib.sha256(data).hexdigest()==e['sha256'],'Capture changed')
    PRE.mkdir(parents=True);copies={}
    for name,data in captured.items():
        suffix=fixed[name].suffix;out=PRE/(name+suffix);out.write_bytes(data);require(out.read_bytes()==data,'Copy readback');copies[name]=binding(out)
    validate(items);validate(list(copies.values()))
    manifest={'utc':utc(),'inputs':items,'copies':copies,'source_sha256':sha(__file__),'protocol_sha256':sha(PROTOCOL),
      'case':'identity__native_penalized','scientific_point_replays':0,'bound_arithmetic_runs':0,'optimizer_calls':0}
    save(PRE/'manifest.json',manifest)
    save(PRE/'prepared_freeze.json',dict(utc=utc(),manifest_sha256=sha(PRE/'manifest.json'),source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),
      input_count=len(items),copy_count=len(copies),case_count=1,scientific_arithmetic_runs=0,optimizer_calls=0))
    print(json.dumps({'status':'PREPARED_ONLY','freeze_sha256':sha(PRE/'prepared_freeze.json'),'manifest_sha256':sha(PRE/'manifest.json')}))

def native_point(raw,model,x,alias,h,tau,start):
    require(len(x)==len(model['columns'])==2472,'Frozen candidate shape')
    retained={c['name']:q(v) for c,v in zip(model['columns'],x)}
    reverse_alias={n:i for i,n in alias.items()}
    values={i:F(0) if n.startswith('mfg:') else retained[n] for i,n in alias.items()}
    failures=[];worst=F(0);binaries=[];affine_count=0;variable_count=0
    for k,row in enumerate(raw['constraints']):
        if k%256==0:guard(start)
        f,s=row['function'],row['set']
        if f['type']=='MathOptInterface.VariableIndex':
            variable_count+=1;v=values[f['variable']]
            if s['type']=='MathOptInterface.ZeroOne':
                binaries.append(f['variable'])
                if v not in (0,1):failures.append({'constraint':k,'kind':'nonbinary','value':rat(v)})
                continue
            lo,hi=h.endpoints(s)
        else:
            affine_count+=1;c,constant=h.terms(f,alias);v=constant+sum((a*values[reverse_alias[n]] for n,a in c.items()),F(0))
            lo,hi=h.endpoints(s)
        violation=max(F(0),lo-v if lo is not None else F(0),v-hi if hi is not None else F(0));worst=max(worst,violation)
        if violation>tau:failures.append({'constraint':k,'kind':'endpoint','nominal_violation':rat(violation)})
    require(len(binaries)==len(set(binaries))==960 and set(binaries)==set(raw['binary_variable_indices']),'Every original native binary')
    require(affine_count==4384,'Every native affine row')
    obj,constant=h.terms(raw['objective'],alias)
    objective=constant+sum((a*values[reverse_alias[n]] for n,a in obj.items()),F(0))
    require(raw['objective_sense']=='MIN_SENSE','Native objective sense')
    return values,dict(accepted=not failures,strict_nominal=not failures and worst==0,tau=rat(tau),nominal_max_violation=rat(worst),
      native_variables=len(values),affine_rows=affine_count,variable_constraint_records=variable_count,binary_declarations=960,
      objective=rat(objective),failures=failures,omitted_mfg_lift=0)

def run(expected):
    start=time.perf_counter();require(not RUN.exists(),'One scientific run only')
    require(sha(PRE/'prepared_freeze.json')==expected,'External freeze pin');freeze=read(PRE/'prepared_freeze.json')
    require(sha(PRE/'manifest.json')==freeze['manifest_sha256'],'Manifest freeze')
    m=read(PRE/'manifest.json');validate(m['inputs']);validate(list(m['copies'].values()))
    require(sha(__file__)==m['source_sha256'] and sha(PROTOCOL)==m['protocol_sha256'],'Frozen source/protocol')
    transport={p.name:sha(p) for p in (PRE/'manifest.json',PRE/'prepared_freeze.json')}
    cp=lambda n:Path(m['copies'][n]['path'])
    RUN.mkdir();save(RUN/'started.json',dict(utc=utc(),freeze_sha256=expected,manifest_sha256=freeze['manifest_sha256'],optimizer_calls=0))
    try:
        h=load_module('native_identity_math_helper',cp('helper'),PINS['helper'][1]);kernel=load_module('native_identity_npz_reader',cp('kernel'),PINS['kernel'][1])
        raw=read(cp('raw'));normal=read(cp('normal'));model=read(cp('model'));alias=h.aliases_from_expected(raw,normal)
        require(len(model['rows'])==4384 and sum(c['binary'] for c in model['columns'])==960,'Full model scope')
        qr={j for j,c in enumerate(model['columns']) if c['name'].split(':')[0] in ('Q','R')}
        require(len(qr)==480,'Fixed Q/R scope')
        x=read(cp('candidate'));values,point=native_point(raw,model,x,alias,h,TAU,start)
        require(unrat(point['objective'])==unrat(read(cp('mip_result'))['accepted_expanded_upper']),'Unchanged old upper objective')
        save(RUN/'native_point_check.json',point)
        save(RUN/'lifted_rational_point.json',[{'native_index':i,'name':alias[i],'value':rat(values[i])} for i in sorted(values)])
        guard(start)
        arrays=kernel.read_npz(cp('raw_lp'),('col_value','row_value','row_dual','col_dual'))
        rawdual=kernel.vector(arrays['row_dual'],('<f8',),4384,'row dual')
        bound=derive_bound(model,rawdual,TAU,qr);old=read(cp('signed_bound'))
        require([q(v) for v in old['projected_dual']]==bound['dual'] and old['projection_changed_rows']==bound['changed'],'Original sign projection')
        require([unrat(v) for v in old['exact_stationarity_residual']]==bound['residual'],'Every original residual')
        for oldkey,newkey in [('beta','beta'),('nominal_lower_bound','nominal'),('expansion_slope','slope'),('expanded_lower_bound','expanded')]:
            require(unrat(old[oldkey])==bound[newkey],'Replayed original proof '+oldkey)
        require(unrat(old['tau'])==TAU and old['dual_feasibility_required'] is False and old['exact_optimum_claim'] is False,'Original proof scope')
        require(unrat(read(cp('lp_result'))['selected_expanded_lower'])==bound['expanded'],'Selected signed proof identity')
        lower=dict(tau=rat(TAU),old_expanded_lower=rat(bound['expanded']),additional_QR_upper_support_correction=rat(bound['correction']),
          native_expanded_lower=rat(bound['native_lower']),row_endpoint_sum_nominal=rat(bound['beta']),nominal_lower=rat(bound['nominal']),
          expansion_slope=rat(bound['slope']),projected_multipliers=[rat(v) for v in bound['dual']],changed_rows=bound['changed'],
          residual=[rat(v) for v in bound['residual']],QR_indices=sorted(qr),direct_widened_endpoint_sum_agrees=True,
          no_new_ray_or_dual=True,optimizer_calls=0)
        save(RUN/'native_lower_certificate.json',lower)
        upper=unrat(point['objective']) if point['accepted'] else None
        if upper is not None:require(bound['native_lower']<=upper,'Consistent finite bracket')
        result=dict(status='CERTIFIED_FINITE_NATIVE_EXPANDED_IDENTITY_BRACKET' if upper is not None else 'LOWER_ONLY_NO_ACCEPTED_NATIVE_UPPER',
          case='identity__native_penalized',native_expanded_lower=rat(bound['native_lower']),native_expanded_upper=rat(upper) if upper is not None else None,
          strict_nominal_upper=rat(upper) if upper is not None and point['strict_nominal'] else None,tau=rat(TAU),
          nominal_comparison_inherited=True,expanded_model_equivalence_claim=False,containment_only=True,
          target_cost_difference_claim=False,exact_optimality_claim=False,cost_units='encoded UC objective',
          cases=1,new_candidates=0,new_optimizers=0,Julia_calls=0,native_builds=0)
        save(RUN/'result.json',result);validate(m['inputs']);validate(list(m['copies'].values()))
        require(transport=={n:sha(PRE/n) for n in transport},'Prepared transports unchanged');guard(start)
        save(RUN/'completion.json',dict(status='COMPLETE_PENDING_INDEPENDENT_REVIEW',utc=utc(),elapsed_seconds=time.perf_counter()-start,
          final_completion_write_excluded=True,all_inputs_unchanged=True,arithmetic_runs=1,optimizer_calls=0))
        print(json.dumps({'status':result['status'],'elapsed_seconds':time.perf_counter()-start}))
    except BaseException as e:
        save(RUN/'failure.json',dict(status='ERROR_OR_TIMEOUT_NO_ADMITTED_BRACKET',utc=utc(),exception_type=type(e).__name__,message=str(e),
          elapsed_seconds=time.perf_counter()-start,optimizer_calls=0,no_retry=True));raise

def self_test():
    require(not (ARM/'synthetic_controls.json').exists(),'One invented fixture pass')
    t=F(1,8);w=F(3)
    require((w+2*t)+(-t)-w==t and w+2*t>w+t,'Native expansion can need second tau')
    require(w*(1+t)+2*t>w+2*t,'Relaxing binary U would invalidate claimed bound')
    toy={'columns':[{'name':'Q:g:0','lower':0.,'upper':3.,'objective':-2.}, {'name':'R:g:0','lower':0.,'upper':3.,'objective':1.}],
      'rows':[{'lower':None,'upper':3.,'coefficients':[[0,1.],[1,1.]]}]}
    b=derive_bound(toy,[1.],t,{0,1});require(b['changed']==[0] and b['correction']==-2*t,'Inadmissible side and negative residual correction')
    b2=derive_bound(toy,[-1.],t,{0,1});require(b2['correction']==-t and b2['residual']==[F(-1),F(2)],'Valid signed row residual')
    for a in (F(0),F(1),F(2),F(3)):
        for bval in (F(0),F(1),F(2),F(3)):
            if a+bval<=3+t:require(-2*a+bval>=b2['native_lower'],'Invented feasible-point lower bound')
    require(F(0)>=-t and -t<=0<=t,'Zero lift and N expanded box')
    require(F.from_float(1e-5)!=F(1,100000),'Exact binary64 tau distinct from decimal rational')
    require(unrat(rat(F(-7,13)))==F(-7,13),'Rational round trip')
    ARM.mkdir(parents=True,exist_ok=True);save(ARM/'synthetic_controls.json',dict(status='PASS',checks=8,utc=utc(),source_sha256=sha(__file__),
      protocol_sha256=sha(PROTOCOL),scientific_inputs_read=0,scientific_arithmetic_runs=0,optimizer_calls=0))
    print('PASS 8 invented controls')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=('self-test','prepare-only','run-prepared'));parser.add_argument('--expected-freeze-sha256');a=parser.parse_args()
    if a.mode=='self-test':self_test()
    elif a.mode=='prepare-only':prepare()
    else:require(a.expected_freeze_sha256 is not None,'Explicit freeze required');run(a.expected_freeze_sha256)
