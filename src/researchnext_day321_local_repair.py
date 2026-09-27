"""One frozen zero-optimizer day321 local schedule repair, separately prepared/run."""
from __future__ import annotations
import argparse,ast,csv,gzip,hashlib,importlib.util,json,math,struct,sys,time,zipfile
from datetime import datetime,timezone
from fractions import Fraction as Q
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
ARM=ROOT/'results/research_next/day321_local_repair';PRE=ARM/'prepared';RUN=ARM/'run01'
OLD=ROOT/'results/research8h/day_blocks/days_321'
COMMON=ROOT/'results/research_next/common_commitment/prepared'
PROTOCOL=ROOT/'docs/research_next/DAY321_LOCAL_REPAIR_PROTOCOL.md'
PROPOSAL=ROOT/'docs/research_next/DAY321_LOCAL_REPAIR_PROPOSAL.md'
KERNEL=ROOT/'src/research8h_standalone_verify.py';KERNEL_SHA='708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'
HELPER=ROOT/'src/researchnext_common_commitment.py';HELPER_SHA='039af59750b4c165d877b9878ac14af02a202700b46739ba96a8914075ae3284'
OLD_MANIFEST_SHA='8ff99b1f4450ac15e91b26a261a85c98d574bbbdac3f7fe149efd9fd07204a5c'
VECTOR_SHA='71cea67428a6ad45ab753b4839be3f2f4d6c1eb4b5a6965c32a5460e15a8c40f'
CHECK_SHA='88ec521245dbb95d3c1cdc88139c125451f00bbb8c4a1906f4e8d6ff7a3cea5c'
TAU=Q.from_float(1e-5);HOURS=(70,71);DELTA=Q(30);PHASE_SECONDS=120.0;BIT_LIMIT=8192
FILES=('matrix.npz','bounds.npz','integrality.npz','model_metadata.json','native_inputs.npz','row_metadata.csv.gz','native_spec.json')
def require(x,msg):
    if not x:raise ValueError(msg)
def utc():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,x):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(x,f,indent=2,allow_nan=False);f.write('\n')
def rat(q):return dict(numerator=str(q.numerator),denominator=str(q.denominator),approximate=float(q))
def binding(p,data=None):
    p=Path(p).resolve();b=p.read_bytes() if data is None else data
    return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def validate(items):
    require(len({x['path'].casefold() for x in items})==len(items),'duplicate bindings')
    for x in items:require(binding(x['path'])==x,'changed input '+x['path'])
def module(p,digest,name):
    require(sha(p)==digest,'pinned helper');s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def kernel():return module(KERNEL,KERNEL_SHA,'day321_repair_npz')
def vec(v,p,n):return tuple(v.vector(v.read_npz(p,('vector',))['vector'],('<f8',),n,'vector'))
def mask(v,p,n):return tuple(v.vector(v.read_npz(p,('integrality',))['integrality'],('|u1',),n,'mask'))
def write_vector(p,values):
    require(all(math.isfinite(x) for x in values),'nonfinite candidate')
    header=repr(dict(descr='<f8',fortran_order=False,shape=(len(values),)))
    pad=(64-(10+len(header)+1)%64)%64;body=(header+' '*pad+'\n').encode('latin1')
    require(len(body)<65536,'NPY header length')
    payload=b'\x93NUMPY\x01\x00'+struct.pack('<H',len(body))+body+struct.pack('<'+'d'*len(values),*values)
    with zipfile.ZipFile(p,'x',compression=zipfile.ZIP_DEFLATED) as z:z.writestr('vector.npy',payload)
def guard(start):require(time.perf_counter()-start<PHASE_SECONDS,'phase budget exhausted')
def bounded(q):require(max(q.numerator.bit_length(),q.denominator.bit_length())<=BIT_LIMIT,'rational bit guard')
def gauss(a,b,start):
    n=len(b);require(n>0 and len(a)==n and all(len(r)==n for r in a),'square system')
    c=[[Q(x) for x in r]+[Q(y)] for r,y in zip(a,b)]
    for k in range(n):
        guard(start);pivot=next((i for i in range(k,n) if c[i][k]),None)
        require(pivot is not None,'singular exact reduced nodal system')
        c[k],c[pivot]=c[pivot],c[k]
        for i in range(k+1,n):
            if not c[i][k]:continue
            factor=c[i][k]/c[k][k];bounded(factor)
            for j in range(k+1,n+1):c[i][j]-=factor*c[k][j];bounded(c[i][j])
            c[i][k]=Q(0)
    out=[Q(0)]*n
    for i in reversed(range(n)):
        out[i]=(c[i][-1]-sum((c[i][j]*out[j] for j in range(i+1,n)),Q(0)))/c[i][i];bounded(out[i])
    require(all(sum((Q(x)*q for x,q in zip(row,out)),Q(0))==Q(y) for row,y in zip(a,b)),'exact system residual')
    return out

def prepare():
    require(not PRE.exists() and not RUN.exists(),'fresh preparation only')
    require(sha(COMMON/'input_manifest.json')==OLD_MANIFEST_SHA,'old manifest')
    initial=read(COMMON/'input_manifest.json')['files'];require(len(initial)==48,'old denominator');validate(initial)
    captured={}
    for x in initial:
        p=Path(x['path']);b=p.read_bytes();require(binding(p,b)==x,'captured old bytes changed');captured[str(p.resolve()).casefold()]=(b,x)
    for p,digest in [(OLD/'constructive_vector.npz',VECTOR_SHA),(OLD/'constructive_check.json',CHECK_SHA),(KERNEL,KERNEL_SHA),(HELPER,HELPER_SHA),(PROPOSAL,'2bb7065c9c9504df6d2b05b1bb62d046d45546046c4689f338a791025f0f29af')]:
        require(sha(p)==digest,'pinned proposal/input');b=p.read_bytes();captured[str(p.resolve()).casefold()]=(b,binding(p,b))
    for p in (Path(__file__),PROTOCOL,COMMON/'input_manifest.json'):
        b=p.read_bytes();captured[str(p.resolve()).casefold()]=(b,binding(p,b))
    initial=[r for b,r in captured.values()];validate(initial)
    v=kernel();PRE.mkdir(parents=True);(PRE/'model').mkdir()
    copies=[]
    for name in FILES:
        source=COMMON/'days_321'/name;data,item=captured[str(source.resolve()).casefold()];dest=PRE/'model'/name;dest.write_bytes(data);copies.append(dict(source=item,copy=binding(dest)))
    for source,dest in [(COMMON/'gen.csv',PRE/'gen.csv'),(OLD/'constructive_vector.npz',PRE/'original_vector.npz')]:
        data,item=captured[str(source.resolve()).casefold()];dest.write_bytes(data);copies.append(dict(source=item,copy=binding(dest)))
    # Confirm the old constructive vector's archived coordinate/model bridge, without replaying it.
    for name in ('matrix.npz','bounds.npz','integrality.npz','model_metadata.json','native_inputs.npz'):
        source=OLD/name;target=PRE/'model'/name
        require(str(source.resolve()).casefold() in captured,'old bridge input not bound')
        require(captured[str(source.resolve()).casefold()][0]==target.read_bytes(),'old constructive model bridge differs')
    m=v.load_model(PRE/'model');meta=read(PRE/'model/model_metadata.json');bits=mask(v,PRE/'model/integrality.npz',m.cols)
    require((m.rows,m.cols,sum(bits))==(34681,23016,12096),'original full model')
    require(meta['offsets']==dict(P=0,U=6888,Y=10920,Z=14952,theta=18984),'offsets')
    require(meta['unit_names'][2]=='101_STEAM_3' and meta['unit_names'][40]=='122_WIND_1' and meta['thermal_unit_names'][2]=='101_STEAM_3','fixed unit coordinates')
    require(meta['bus_ids'][12]==113 and meta['budget_MWh']==23195 and meta['individual_mean_constraints']==0,'native/slack/cap scope')
    for t in HOURS:
        require(m.lower[18984+24*t+12]==m.upper[18984+24*t+12]==0,'unchanged reference angle')
    before=vec(v,PRE/'original_vector.npz',m.cols)
    require(all(before[j] in (0.,1.) for j,b in enumerate(bits) if b),'old exact states')
    require(all(before[6888+24*t+2]==0 for t in HOURS) and before[14952+24*70+2]==1 and before[10920+24*72+2]==1,'fixed old gap events')
    save(PRE/'copy_provenance.json',dict(copies=copies,old_constructive_model_bridge_exact=True))
    save(PRE/'plan.json',dict(hours_0based=list(HOURS),steam='101_STEAM_3',wind='122_WIND_1',steam_MW_increment=30,wind_MW_increment=-30,state_changes=['U70=1','U71=1','Z70=0','Y72=0'],angle_hours_only=list(HOURS),slack_bus=113,angle_method='exact Fraction Gaussian elimination, first nonzero pivot, then one binary64 rounding',phase_seconds=PHASE_SECONDS,bit_limit=BIT_LIMIT,candidate_count=1,optimizer_calls=0,source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),no_search_or_fallback=True))
    validate(initial);items=initial+[binding(p) for p in PRE.rglob('*') if p.is_file()];validate(items)
    save(PRE/'input_manifest.json',dict(files=items));validate(items)
    save(PRE/'prepared_freeze.json',dict(utc=utc(),source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),manifest_sha256=sha(PRE/'input_manifest.json'),bindings=len(items),candidate_constructions=0,nodal_solves=0,optimizer_calls=0,separate_execution_GO_required=True))
    print(json.dumps(read(PRE/'prepared_freeze.json')),flush=True)

def run(expected):
    start=time.perf_counter();require(not RUN.exists(),'one candidate execution only')
    require(sha(PRE/'prepared_freeze.json')==expected,'external freeze hash')
    f=read(PRE/'prepared_freeze.json');require(f['source_sha256']==sha(__file__) and f['protocol_sha256']==sha(PROTOCOL),'frozen source/protocol')
    require(f['manifest_sha256']==sha(PRE/'input_manifest.json'),'manifest')
    items=read(PRE/'input_manifest.json')['files'];validate(items)
    transport=[binding(PRE/'prepared_freeze.json'),binding(PRE/'input_manifest.json')]
    v=kernel();m=v.load_model(PRE/'model');bits=mask(v,PRE/'model/integrality.npz',m.cols);meta=read(PRE/'model/model_metadata.json')
    before=vec(v,PRE/'original_vector.npz',m.cols);candidate=list(before)
    RUN.mkdir();save(RUN/'execution_started.json',dict(utc=utc(),source_sha256=sha(__file__),freeze_sha256=expected,optimizer_calls=0))
    stage='fixed_candidate';solves=0
    try:
        guard(start);allowed=set();shifts=[]
        for t in HOURS:
            for j,delta in ((2,DELTA),(40,-DELTA)):
                col=41*t+j;candidate[col]=float(Q(before[col])+delta);allowed.add(col)
                require(Q(candidate[col])-Q(before[col])==delta,'fixed MW shift not exactly representable')
                shifts.append(dict(column=col,old_hex=before[col].hex(),new_hex=candidate[col].hex(),exact_change=rat(delta)))
            col=6888+24*t+2;candidate[col]=1.;allowed.add(col)
        for col in (14952+24*70+2,10920+24*72+2):candidate[col]=0.;allowed.add(col)
        labels=list(csv.DictReader(gzip.decompress((PRE/'model/row_metadata.csv.gz').read_bytes()).decode('utf-8-sig').splitlines()))
        require(len(labels)==m.rows and all(int(r['row'])==i for i,r in enumerate(labels)),'row metadata coordinates')
        corrections=[];stage='two_exact_reduced_nodal_solves'
        for t in HOURS:
            theta_cols=[18984+24*t+b for b in range(24) if b!=12];rows=[]
            for bus in meta['bus_ids']:
                matching=[i for i,r in enumerate(labels) if r['family']=='nodal_balance' and int(r['hour_0based'])==t and int(r['uid'])==bus]
                require(len(matching)==1,'unique actual nodal row')
                if bus!=113:rows.append(matching[0])
            a=[];b=[]
            for i in rows:
                coeff={m.indices[e]:Q(m.data[e]) for e in range(m.indptr[i],m.indptr[i+1])}
                require(all(41*t<=j<41*(t+1) or 18984+24*t<=j<18984+24*(t+1) for j in coeff),'nodal row coordinate locality')
                require(m.row_lower[i]==m.row_upper[i],'nodal equality')
                a.append([coeff.get(j,Q(0)) for j in theta_cols])
                b.append(-sum((c*(Q(candidate[j])-Q(before[j])) for j,c in coeff.items() if j<6888),Q(0)))
            delta=gauss(a,b,start);solves+=1;details=[]
            for j,q in zip(theta_cols,delta):
                exact=Q(before[j])+q;candidate[j]=float(exact);require(math.isfinite(candidate[j]),'angle conversion finite');allowed.add(j)
                details.append(dict(column=j,delta=rat(q),exact_new_angle=rat(exact),rounded_hex=candidate[j].hex(),rounding_error=rat(Q(candidate[j])-exact)))
            corrections.append(dict(hour_0based=t,original_rows=rows,theta_columns=theta_cols,exact_linear_system_pass=True,angles=details))
        require(all(candidate[j].hex()==before[j].hex() for j in range(m.cols) if j not in allowed),'untouched coordinate changed')
        write_vector(RUN/'candidate_vector.npz',candidate);point=vec(v,RUN/'candidate_vector.npz',m.cols)
        require(all(a.hex()==b.hex() for a,b in zip(point,candidate)),'binary64 candidate roundtrip')
        require(all(point[j] in (0.,1.) for j,b in enumerate(bits) if b),'all original states binary')
        save(RUN/'candidate_changes.json',dict(shifts=shifts,changed_columns=[j for j,(a,b) in enumerate(zip(before,point)) if a.hex()!=b.hex()],allowed_columns=sorted(allowed),all_untouched_bytes_preserved=True,nodal_corrections=corrections))
        guard(start);stage='complete_original_exact_and_native_acceptance'
        exact=v.check_point(m,list(point),bits,TAU)
        helper=module(HELPER,HELPER_SHA,'day321_repair_native_helper');require(helper.TAU==TAU,'native tolerance')
        native=helper.native_check(v,point,PRE/'model',meta,read(PRE/'model/native_spec.json'))
        fossil=[meta['unit_names'].index(n) for n in meta['fossil_units']];require(len(fossil)==23 and 2 in fossil and 40 not in fossil,'energy roster')
        energy_before=sum((Q(before[41*t+j]) for t in range(168) for j in fossil),Q(0));energy_after=sum((Q(point[41*t+j]) for t in range(168) for j in fossil),Q(0))
        require(energy_after-energy_before==60,'actual exact fossil increment')
        save(RUN/'exact_point_check.json',exact);save(RUN/'native_check.json',native)
        accepted=exact['expanded_pass'] and native['expanded_pass']
        result=dict(verdict='VERIFIED_INDIVIDUAL_DAY321_EXPANDED_MODEL' if accepted else 'UNKNOWN_LOCAL_REPAIR_REJECTED',accepted=accepted,strict_point_pass=exact['strict_pass'],expanded_point_pass=exact['expanded_pass'],native_pass=native['expanded_pass'],original_binary_coordinates=12096,energy_before=rat(energy_before),energy_after=rat(energy_after),exact_energy_increment=rat(energy_after-energy_before),nominal_cap_MWh=23195,actual_expanded_cap=rat(Q(23195)+TAU),individual_only=True,common_commitment_claim=False,old_historical_outcomes_unchanged=True,candidates=1,optimizer_calls=0)
        save(RUN/'result.json',result);stage='close';validate(items);validate(transport);guard(start)
        save(RUN/'completion.json',dict(utc=utc(),status='CLOSED_PENDING_INDEPENDENT_REVIEW',nodal_systems_solved=solves,candidates=1,optimizer_calls=0,phase_seconds=time.perf_counter()-start,phase_limit_seconds=PHASE_SECONDS,all_frozen_inputs_unchanged=True,no_retry_or_fallback=True,final_completion_write_outside_sample=True))
        print(json.dumps(result),flush=True)
    except BaseException as e:
        save(RUN/'failure.json',dict(utc=utc(),stage=stage,error_type=type(e).__name__,message=str(e),scientific_verdict='UNKNOWN',nodal_systems_solved=solves,optimizer_calls=0,phase_seconds=time.perf_counter()-start,no_retry_or_fallback=True));raise

def fixtures():
    require(not PRE.exists() and not RUN.exists(),'source fixtures only before preparation');ARM.mkdir(parents=True,exist_ok=True)
    cases=[([[2,1],[1,3]],[1,2],[Q(1,5),Q(3,5)]),([[0,2],[3,4]],[6,15],[Q(1),Q(3)]),([[Q(1,8),Q(1,2)],[Q(3,8),Q(1,4)]],[Q(9,8),Q(7,8)],[Q(1),Q(2)])]
    for a,b,wanted in cases:require(gauss(a,b,time.perf_counter())==wanted,'invented exact solve')
    failures=0
    for a,b in [([[1,2],[2,4]],[1,2]),([[1,2]],[1])]:
        try:gauss(a,b,time.perf_counter())
        except ValueError:failures+=1
    require(failures==2,'singular/shape rejection')
    p=ARM/'invented_vector.npz';write_vector(p,[0.,-0.,30.,-1.25]);v=kernel();out=vec(v,p,4)
    require([x.hex() for x in out]==[x.hex() for x in [0.,-0.,30.,-1.25]],'invented npy signs roundtrip')
    save(ARM/'source_fixtures.json',dict(status='PASS',source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),tests=6,scientific_arrays_read=0,candidate_constructions=0,optimizer_imports=0,optimizer_calls=0,fixture_vector_sha256=sha(p)))
    print('six invented source fixtures PASS',flush=True)

def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--prepare-only',action='store_true');g.add_argument('--run-prepared',action='store_true');g.add_argument('--source-fixtures',action='store_true');p.add_argument('--expected-freeze-sha256');a=p.parse_args()
    if a.prepare_only:prepare()
    elif a.source_fixtures:fixtures()
    else:require(a.expected_freeze_sha256,'external freeze required');run(a.expected_freeze_sha256)
if __name__=='__main__':main()
