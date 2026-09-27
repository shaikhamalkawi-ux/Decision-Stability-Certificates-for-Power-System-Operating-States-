"""Independent necessary-row/provenance gate. No producer or solver import."""
import ast, csv, gzip, hashlib, importlib.util, json, math, sys, time
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path

sys.dont_write_bytecode = True
ARM=Path(__file__).resolve().parent; ROOT=ARM.parents[2]; PRE=ARM/'prepared'
OLD=ROOT/'results/research_next/common_master/prepared'
SOURCE=ROOT/'src/researchnext_common_master_bounded.py'
PROTOCOL=ROOT/'docs/research_next/COMMON_MASTER_BOUNDED_PROTOCOL.md'
PINS={SOURCE:'62a2755aa289dc353893d3bf23ccf46ff839dffdf1937d5cdbc4320ce9526c18',
 PROTOCOL:'ff502793f1fa52c6a10a228e2fe5f0d8a5caba5ff77380006c897c3f3e243553',
 PRE/'prepared_freeze.json':'75e9e276c356290129c85fefa9fdc5fb36f175174efb5b2e131bb96fdbef80d5',
 PRE/'input_manifest.json':'7bc0949abcd5aebb0d7ce4f2e68a3efa1105e9d1e25e54fd429dc04f4b33a19d',
 OLD/'prepared_freeze.json':'39fe78153d0ecbb408035d074f35bc7566e4fd1c93dd3d80e118fedb6f90405c',
 OLD/'input_manifest.json':'c446c30eee6edc9b361b55bcb306bfdc8862916095d49a0ae26244753e265562',
 PRE/'master.json.gz':'c873e64e591a2362bf503fcfe25fb6af358e622b7e43e6902935ad13a94a25ab',
 ROOT/'src/researchnext_common_master.py':'0eea17f50b859db72cf6de5ad337263f6c984f7c30830861b5feb7500c39b76e',
 ROOT/'src/research8h_standalone_verify.py':'708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'}
TAU=F.from_float(1e-5); START=6888; STOP=18984; NB=12096; H=168

def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def gz(p):
    with gzip.open(p,'rt',encoding='utf-8') as f:return json.load(f)
def binding(e):
    data=Path(e['path']).read_bytes();need(len(data)==e['bytes'] and hashlib.sha256(data).hexdigest()==e['sha256'],'Binding '+e['path'])
def fraction(x):
    if isinstance(x,dict):return F(int(x['numerator']),int(x['denominator']))
    q=F(int(x[0]),int(x[1]));need([str(q.numerator),str(q.denominator)]==x,'Canonical signed rational');return q
def finite(x):return F(x) if math.isfinite(x) else None
def sparse(m,r):return {m.indices[k]:F(m.data[k]) for k in range(m.indptr[r],m.indptr[r+1])}
def require_original(m,r,c,lo,hi):
    need(sparse(m,r)=={j:a for j,a in c.items() if a} and finite(m.row_lower[r])==lo and finite(m.row_upper[r])==hi,'Original premise row '+str(r))

def main():
    started=time.perf_counter();need(not (ARM/'run01').exists() and not (OLD.parent/'run01').exists(),'No scientific master run')
    for p,pin in PINS.items():need(sha(p)==pin,'External pin '+str(p))
    manifest=read(PRE/'input_manifest.json');oldmanifest=read(OLD/'input_manifest.json')
    need(len(manifest['files'])==239 and len(oldmanifest['files'])==200,'Manifest denominators')
    paths={e['path']:e for e in manifest['files']};need(len(paths)==239,'Unique paths')
    for e in manifest['files']:binding(e)
    need(all(paths.get(e['path'])==e for e in oldmanifest['files']),'Complete inherited closure')
    copied=read(PRE/'successor_copy_provenance.json');need(len(copied['copies'])==29 and copied['master_reassembled'] is False and copied['new_scientific_selection'] is False,'Successor copy scope')
    for e in copied['copies']:
        binding(e['original']);binding(e['copy']);a,b=Path(e['original']['path']),Path(e['copy']['path'])
        need(a.relative_to(OLD)==b.relative_to(PRE) and a.read_bytes()==b.read_bytes(),'Identical inherited payload')
    for e in read(PRE/'copy_provenance.json')['copies']:
        binding(e['original']);binding(e['copy']);need(Path(e['original']['path']).read_bytes()==Path(e['copy']['path']).read_bytes(),'Original mathematical payload copy')
    need(len(read(PRE/'copy_provenance.json')['copies'])==24,'24 original copies')
    f=read(PRE/'prepared_freeze.json');need(f['manifest_sha256']==PINS[PRE/'input_manifest.json'] and f['source_sha256']==PINS[SOURCE] and f['protocol_sha256']==PINS[PROTOCOL],'Freeze relations')
    need((f['rows'],f['columns'],f['binaries'],f['copies'])==(17212,12432,12096,29) and f['optimizer_calls']==f['backend_imports']==0 and f['master_reassembled'] is False,'Frozen scientific scope')
    # Check mathematics unchanged by the additive execution-control successor.
    before=ast.parse((ROOT/'src/researchnext_common_master.py').read_text(encoding='utf-8-sig'))
    after=ast.parse(SOURCE.read_text(encoding='utf-8-sig'))
    funcs=lambda tree:{n.name:ast.dump(n,include_attributes=False) for n in tree.body if isinstance(n,ast.FunctionDef)}
    bf,af=funcs(before),funcs(after)
    unchanged=('assemble','numeric_scalar','encoded_row','smallest_auxiliary','check_exact_rows','nominate','master_backend')
    need(all(bf[n]==af[n] for n in unchanged),'Mathematical and numeric-readback functions unchanged')
    kpath=ROOT/'src/research8h_standalone_verify.py'
    spec=importlib.util.spec_from_file_location('master_review_npz_kernel',kpath);v=importlib.util.module_from_spec(spec);sys.modules[spec.name]=v;spec.loader.exec_module(v)
    def mask(folder,m):return tuple(v.vector(v.read_npz(folder/'integrality.npz',('integrality',))['integrality'],('|u1',),m.cols,'mask'))
    models=[v.load_model(PRE/w) for w in ('identity','days_321')];jm=v.load_model(PRE/'joint')
    need((jm.rows,jm.cols,len(jm.data))==(69362,33936,291176),'Inherited joint dimensions')
    need(mask(PRE/'joint',jm)==tuple(int(START<=j<STOP) for j in range(jm.cols)),'Complete joint binary mask')
    maps=read(PRE/'joint/column_maps.json');need(maps['worlds']==['identity','days_321'],'World mapping roster')
    with (PRE/'gen.csv').open(encoding='utf-8-sig',newline='') as stream:genrows=list(csv.DictReader(stream))
    gen={g['GEN UID']:g for g in genrows};need(len(gen)==len(genrows),'Unique native unit IDs')
    master=gz(PRE/'master.json.gz');premises=read(PRE/'premises.json')
    need(master['columns']==12432 and master['binary_columns']==NB and len(master['boxes'])==12432 and len(master['rows'])==17212 and master['objective']=='all_zero' and fraction(master['tau'])==TAU,'Exact master schema')
    scalar_count=rounded_count=0
    def scalar(x):
        nonlocal scalar_count,rounded_count
        if x is None:return None
        need(set(x)=={'exact','binary64_hex','rounding_error'},'Scalar encoding fields')
        q=fraction(x['exact']);b=float.fromhex(x['binary64_hex']);error=fraction(x['rounding_error'])
        need(math.isfinite(b) and abs(b)<1e20 and (q==0 or b!=0) and b.hex()==float(q).hex() and F(b)-q==error,'Exact declared numerical encoding')
        scalar_count+=1;rounded_count+=bool(error);return q
    decoded=[]
    for e in master['rows']:
        indices=[j for j,a in e['terms']];need(indices==sorted(set(indices)) and all(type(j)is int and 0<=j<12432 for j in indices),'Ordered sparse coordinates')
        terms={j:scalar(a) for j,a in e['terms']};need(terms and all(terms.values()),'No explicit zero row terms')
        decoded.append((e['family'],terms,scalar(e['lower']),scalar(e['upper']),e['provenance']))
    boxes=[(b['kind'],scalar(b['lower']),scalar(b['upper'])) for b in master['boxes']]
    state_rows=[];hour_data=[];metas=[];selected_premises=0
    for wi,(world,m) in enumerate(zip(('identity','days_321'),models)):
        need((m.rows,m.cols,len(m.data))==(34681,23016,145588),'Original world dimensions')
        need(mask(PRE/world,m)==tuple(int(START<=j<STOP) for j in range(m.cols)),'Original full bits')
        mp=maps['original_to_joint'][wi];need(len(mp)==m.cols and len(set(mp))==m.cols and mp[START:STOP]==list(range(START,STOP)),'Shared original bit map')
        need(all(m.lower[j]==jm.lower[mp[j]] and m.upper[j]==jm.upper[mp[j]] for j in range(m.cols)),'Every original mapped box')
        meta=read(PRE/world/'model_metadata.json');metas.append(meta);names=meta['unit_names'];thermal=meta['thermal_unit_names'];fossil=meta['fossil_units']
        need(len(names)==len(set(names))==41 and len(thermal)==24 and len(fossil)==23 and names[:24]==thermal,'Actual ordered native roster')
        need([n for n in names if gen[n]['Fuel'] in ('Coal','NG','Oil')]==fossil and set(thermal)-set(fossil)=={'121_NUCLEAR_1'} and gen['121_NUCLEAR_1']['Fuel']=='Nuclear','Native fossil/nuclear partition')
        need(meta['offsets']==dict(P=0,U=6888,Y=10920,Z=14952,theta=18984),'Actual offsets')
        fi=[names.index(n) for n in fossil];ni=thermal.index('121_NUCLEAR_1');a=[F(gen[n]['PMin MW']) for n in thermal];b=[F(gen[n]['PMax MW']) for n in thermal]
        need(all(x.denominator==y.denominator==1 and 0<=x<=y for x,y in zip(a,b)),'Exact integer nameplate premises')
        state=[]
        for r in range(m.rows):
            c=sparse(m,r)
            if c and all(START<=j<STOP for j in c):
                lo,hi=finite(m.row_lower[r]),finite(m.row_upper[r]);need(all(x.denominator==1 for x in list(c.values())+[q for q in (lo,hi) if q is not None]),'State integrality premise')
                state.append((r,c,lo,hi))
        need(len(state)==16032,'Complete state-only row count');state_rows.append(state)
        need(all(0<=m.lower[j]<=m.upper[j]<=1 and F(m.lower[j]).denominator==F(m.upper[j]).denominator==1 for j in range(START,STOP)),'Exact state boxes')
        need(all(m.lower[j]==0 and m.upper[j]==1 for j in range(6888,6912)) and all(m.lower[j]==m.upper[j]==0 for j in list(range(10920,10944))+list(range(14952,14976))),'Initial mature/free boundary semantics')
        with gzip.open(PRE/world/'row_metadata.csv.gz','rt',encoding='utf-8-sig',newline='') as stream:labels=list(csv.DictReader(stream))
        need(len(labels)==m.rows and [int(e['row']) for e in labels]==list(range(m.rows)),'Complete original labels')
        index={}
        for label in labels:
            if label['family'] not in ('aggregate_balance','thermal_lower','thermal_upper','fossil_energy_cap'):continue
            key=(label['family'],int(label['hour_0based']),label['uid']);need(key not in index,'Unique premise label');index[key]=int(label['row'])
        need(len(index)==8233,'Selected physical-row denominator');selected_premises+=len(index)
        caps=[r for (family,t,name),r in index.items() if family=='fossil_energy_cap'];need(len(caps)==1,'One original cap')
        require_original(m,caps[0],{41*t+j:F(1) for t in range(H) for j in fi},None,F(23195))
        rec=premises['worlds'][wi];need(rec['world']==world and rec['cap_row']==caps[0] and rec['fossil_indices']==fi and rec['nuclear_index']==ni and len(rec['hours'])==H,'Actual premise descriptor')
        hh=[]
        for t,h in enumerate(rec['hours']):
            ar=index[('aggregate_balance',t,'ALL')];lower=finite(m.row_lower[ar]);need(lower is not None,'Finite aggregate')
            require_original(m,ar,{41*t+j:F(1) for j in range(41)},lower,lower)
            sources=[]
            for k,name in enumerate(thermal):
                pc,uc=41*t+k,START+24*t+k;lr=index[('thermal_lower',t,name)];ur=index[('thermal_upper',t,name)]
                require_original(m,lr,{pc:F(-1),uc:a[k]},None,F(0));require_original(m,ur,{pc:F(1),uc:-b[k]},None,F(0))
                sources.append(dict(uid=name,P_column=pc,U_column=uc,lower_row=lr,upper_row=ur))
            nonthermal=[41*t+j for j in range(24,41)];fossilcols=[41*t+j for j in fi]
            need(all(math.isfinite(m.upper[j]) for j in nonthermal) and all(math.isfinite(m.lower[j]) for j in fossilcols),'Finite physical endpoints')
            rho=lower-sum((F(m.upper[j]) for j in nonthermal),F(0))-19*TAU
            flo=sum((F(m.lower[j])-TAU for j in fossilcols),F(0));fhi=sum((b[j] for j in fi),F(0))+23*TAU
            need(h['hour']==t and h['aggregate_row']==ar and h['nonthermal_upper_columns']==nonthermal and h['fossil_lower_columns']==fossilcols and h['thermal_rows']==sources,'Exact all-row provenance')
            need([fraction(x) for x in h['a']]==a and [fraction(x) for x in h['b']]==b and fraction(h['rho'])==rho and fraction(h['box_lower'])==flo and fraction(h['box_upper'])==fhi,'Exact saved aggregate/tolerance formulas')
            need(h['losses']==dict(aggregate=1,nonthermal_boxes=17,nuclear_upper=1,total_rho=19,all_thermal_capacity_total=42),'Tolerance-count provenance')
            hh.append((rho,flo,fhi,a,b,fi,ni,caps[0]))
        hour_data.append(hh)
    need(state_rows[0]==state_rows[1] and all(models[0].lower[j]==models[1].lower[j] and models[0].upper[j]==models[1].upper[j] for j in range(START,STOP)),'Exact common state rows/boxes')
    need(all(metas[0][key]==metas[1][key] for key in ('unit_names','thermal_unit_names','fossil_units')),'Unchanged world rosters')
    need(all(h[3:5]==hour_data[0][0][3:5] for hours in hour_data for h in hours),'One fixed nameplate tuple')
    need(premises['unit_roster']==[metas[0][k] for k in ('unit_names','thermal_unit_names','fossil_units')] and premises['integer_state_rows']==16032 and premises['selected_physical_rows_per_world']==8233 and premises['state_tau_equivalence'] is True and TAU<1 and premises['all_12096_original_states'] is True,'Whole premise summary')
    cursor=0
    def require_master(family,terms,lo,hi,provenance):
        nonlocal cursor
        want=(family,{j:a for j,a in terms.items() if a},lo,hi,provenance)
        need(decoded[cursor]==want,'Master exact row '+str(cursor)+' '+family);cursor+=1
    for r,c,lo,hi in state_rows[0]:require_master('state',{j-START:a for j,a in c.items()},lo,hi,dict(original_row=r,both_worlds=True,integer_tau_equivalence=True))
    for t in range(H):
        threshold=max(0,math.ceil(max(hour_data[0][t][0],hour_data[1][t][0])-23*TAU))
        require_master('integer_capacity',{24*t+j:b for j,b in enumerate(hour_data[0][t][4])},F(threshold),None,dict(hour=t,total_tau_loss=42,binary_only_ceiling=True))
    for world in ('identity','days_321'):
        cut=read(PRE/(world+'_cut.json'));need(cut['status']=='VERIFIED_GLOBAL_EXPANDED_AFFINE_NECESSARY_CUT' and cut['world']==world and fraction(cut['tau'])==TAU and fraction(cut['cap'])==F(23195)+TAU and cut['new_derived_row_expansion']==0,'Inherited global cut scope')
        terms={x['column']-START:fraction(x['coefficient']) for x in cut['coefficients']};need(len(terms)==len(cut['coefficients'])==82 and all(0<=j<4032 and a>0 for j,a in terms.items()),'Complete accepted cut support')
        require_master('inherited_cut',terms,None,fraction(cut['cap'])-fraction(cut['alpha']),dict(world=world,cut_sha256=sha(PRE/(world+'_cut.json')),extra_tau=0))
    for wi,hours in enumerate(hour_data):
        for t,(rho,lo,hi,a,b,fi,ni,caprow) in enumerate(hours):
            j=NB+H*wi+t;need(boxes[j]==('C',lo,hi),'Exact auxiliary box')
            require_master('F_balance',{j:F(1),24*t+ni:b[ni]},rho,None,dict(world=wi,hour=t,loss=19))
            require_master('F_thermal_lower',{j:F(1),**{24*t+k:-a[k] for k in fi}},-23*TAU,None,dict(world=wi,hour=t,loss=23))
            require_master('F_thermal_upper',{j:F(1),**{24*t+k:-b[k] for k in fi}},None,23*TAU,dict(world=wi,hour=t,loss=23))
        require_master('F_cap',{NB+H*wi+t:F(1) for t in range(H)},None,F(23195)+TAU,dict(world=wi,original_cap_row=hours[0][7],loss=1))
    need(cursor==len(decoded)==17212,'Every exact row accounted')
    need(all(boxes[j]==('B',F(models[0].lower[START+j]),F(models[0].upper[START+j])) for j in range(NB)),'Every original state box and bit retained')
    need(len(boxes)==12432,'Every master box accounted')
    plan=read(PRE/'plan.json');controls=read(PRE/'execution_controls.json')
    need(plan['master_options']=={'limits/time':120.,'limits/solutions':1,'parallel/maxnthreads':1,'lp/threads':1,'randomization/randomseedshift':0,'randomization/permutationseed':0,'randomization/lpseed':0,'numerics/feastol':1e-8},'Fixed master options')
    need(plan['LP_options']==dict(time_limit=60.,threads=1,random_seed=0,presolve='on',solver='simplex'),'Fixed LP options')
    need((plan['phase_seconds'],plan['master_start_guard'],plan['LP_start_guard'],plan['maximum_calls'],plan['candidates'])==(360.,125.,65.,2,1),'Fixed prospective budget')
    need(controls['exactly_one_returned_solution'] is True and controls['late_positive_admission'] is False and controls['cleanup_may_exceed_deadline_but_no_late_positive'] is True,'Bounded execution contract')
    for e in manifest['files']:binding(e)
    for p,pin in PINS.items():need(sha(p)==pin,'Closing external pin')
    need(not (ARM/'run01').exists() and not (OLD.parent/'run01').exists(),'No run during audit')
    report=dict(status='PASS_INDEPENDENT_SOURCE_PREPARED',utc=datetime.now(timezone.utc).isoformat(),reviewer_sha256=sha(__file__),elapsed_seconds=time.perf_counter()-started,
       source_sha256=PINS[SOURCE],protocol_sha256=PINS[PROTOCOL],freeze_sha256=PINS[PRE/'prepared_freeze.json'],manifest_sha256=PINS[PRE/'input_manifest.json'],
       bindings=239,inherited_bindings=200,successor_exact_copies=29,original_exact_copies=24,unchanged_master_sha256=PINS[PRE/'master.json.gz'],
       rows=17212,columns=12432,binaries=12096,selected_original_physical_rows=selected_premises,state_rows_each_world=16032,
       exact_scalar_encodings=scalar_count,nonzero_rounding_errors=rounded_count,rows_by_family=dict(Counter(r[0] for r in decoded)),
       all_original_premises_and_saved_rows_checked=True,all_bytes_unchanged=True,nominees_evaluated=0,optimizer_calls=0,backend_imports=0,
       decoder_reuse=PINS[kpath],producer_imports=0,old_joint_assembly_and_cut_proofs='Inherited through closed independent provenance; not rerun',
       execution_authorization=False,scientific_conclusion='Exact master is necessary only; numerical result and any nominee require separate admission and original full recourse checks.')
    with (ARM/'INDEPENDENT_PREPARED_REVIEW.json').open('x',encoding='utf-8') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps({'status':report['status'],'elapsed_seconds':report['elapsed_seconds'],'report_sha256':sha(ARM/'INDEPENDENT_PREPARED_REVIEW.json')}))

if __name__=='__main__':main()
