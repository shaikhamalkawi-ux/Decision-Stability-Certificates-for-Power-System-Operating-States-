"""Independent archived-premise audit only; no scientific DP or optimizer."""
from pathlib import Path
from fractions import Fraction
from datetime import datetime, timezone
import csv, gzip, hashlib, importlib.util, json, math, sys, time

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
PRE=ROOT/'results/research_next/selected_dwell_cover/prepared'
OUT=Path(__file__).resolve().parent
SOURCE=ROOT/'src/researchnext_selected_dwell_cover.py'
PROTOCOL=ROOT/'docs/research_next/SELECTED_DWELL_COVER_PROTOCOL.md'
EXPECTED={
 str(SOURCE):'55ae4f33da561a35ec1c5200eb3862000b1a8f5ccf462152e1bbb42d2f2a9f09',
 str(PROTOCOL):'7b694b832e4d934c136d7d6c7c47be2501c3610b5286ad660a1fcb10807ce6ea',
 str(PRE/'prepared_freeze.json'):'9cf1f83465a83596c2f837dd122c91463dcdca2f5648780a69afd99228443098',
 str(PRE/'input_manifest.json'):'57951a4d2160230ef917f7745a3d074f9eca4cb445eb43c3345cb6df44d5395c',
 str(PRE/'admission.json'):'c56b5f4951edd08a43f31f7b283b513c43b1af274590f5fe13266cbebe4cb7b8',
 str(PRE.parent/'synthetic_tests.json'):'47a94bec88acb96d4d057dd8775bc42a1911c62b31f024bb189db0b4edd8f5dc',
}
KERNEL=ROOT/'src/research8h_standalone_verify.py'
KERNEL_SHA='708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'
SELECTED=('115_STEAM_3','116_STEAM_1','118_CC_1')
SPEC=((62,155,8,8),(62,155,8,8),(170,355,8,5))
FAMILIES=('transition','exclusive_transition','minimum_up','minimum_down')

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def require(ok,msg):
    if not ok:raise AssertionError(msg)
def binding(x):
    p=Path(x['path']);b=p.read_bytes()
    require(len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256'],'Binding mismatch '+str(p))
def save(name,obj):
    with (OUT/name).open('x',encoding='utf-8') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')
def row(m,i):return {m.indices[e]:m.data[e] for e in range(m.indptr[i],m.indptr[i+1])}
def check_row(m,i,terms,lo,hi):
    require(row(m,i)=={k:v for k,v in terms.items() if v} and m.row_lower[i]==lo and m.row_upper[i]==hi,'Exact row mismatch '+str(i))

def main():
    started=time.perf_counter();require(not (OUT/'prepared_review.json').exists(),'One audit only')
    snapshots={p:sha(p) for p in EXPECTED}
    require(snapshots==EXPECTED,'External pinned digest mismatch')
    freeze=read(PRE/'prepared_freeze.json');manifest=read(PRE/'input_manifest.json')['files'];adm=read(PRE/'admission.json')
    require(freeze['status']==adm['status']=='PREPARED_NO_SCIENTIFIC_DP','Preparation status')
    require(freeze['bindings']==len(manifest)==101,'Full manifest denominator')
    require(len({x['path'].casefold() for x in manifest})==101,'Manifest uniqueness')
    for x in manifest:binding(x)
    binding(freeze['input_manifest']);binding(freeze['admission'])
    for x in (freeze,adm):
        require(x['scientific_dp_runs']==x['scientific_threshold_queries']==x['optimizer_calls']==0,'Unexpected science count')
    fixtures=read(PRE.parent/'synthetic_tests.json')
    require(fixtures['status']=='PASS' and len(fixtures['checks'])==11,'Fixture receipt')
    require(fixtures['source_sha256']==EXPECTED[str(SOURCE)] and fixtures['protocol_sha256']==EXPECTED[str(PROTOCOL)],'Fixture versions')
    require(fixtures['scientific_inputs_read']==fixtures['scientific_dp_runs']==fixtures['optimizer_calls']==0,'Fixture scope')
    copies=read(PRE/'copy_manifest.json')['files'];require(len(copies)==freeze['copies']==14,'Copy denominator')
    for pair in copies:
        binding(pair['original']);binding(pair['copy'])
        require(Path(pair['original']['path']).read_bytes()==Path(pair['copy']['path']).read_bytes(),'Copied bytes differ')
    require(sha(KERNEL)==KERNEL_SHA,'Decoder pin')
    spec=importlib.util.spec_from_file_location('selected_dwell_independent_decoder',KERNEL)
    v=importlib.util.module_from_spec(spec);sys.modules[spec.name]=v;spec.loader.exec_module(v)
    old=read(PRE/'capacity_admission.json');binding(adm['inherited_capacity_premises'])
    require(old['status']=='PREPARED_PREMISES_ONLY' and old['shared_U_mapping_checked'],'Inherited capacity admission')
    require(old['original_binary_columns']==adm['original_binary_columns']==12096,'Binary scope')
    tau=Fraction.from_float(1e-5)
    require((old['tau']['numerator'],old['tau']['denominator'])==(str(tau.numerator),str(tau.denominator)),'Exact tau')
    require(adm['tau']==old['tau'] and 0<tau<1,'Tau correspondence')
    require(len(old['tuples'])==1 and old['hour_group']==[0]*168,'Static coefficient tuple')
    a,b=old['tuples'][0]['cost'],old['tuples'][0]['capacity'];fossil=old['fossil_names'];thermal=old['thermal_names'];names=old['unit_names']
    require(len(a)==len(b)==len(fossil)==23 and len(thermal)==24 and len(names)==41,'Rosters')
    require(all(type(x) is int and x>=0 for x in a+b),'Integer cover premises')
    with (PRE/'gen.csv').open(encoding='utf-8-sig',newline='') as f:gen={x['GEN UID']:x for x in csv.DictReader(f)}
    require([n for n in names if gen[n]['Fuel'] in ('Coal','NG','Oil')]==fossil,'Native fossil roster')
    require(tuple(x['uid'] for x in adm['selected'])==SELECTED,'Fixed selected labels')
    for name,expected,record in zip(SELECTED,SPEC,adm['selected']):
        g=gen[name];up=math.ceil(Fraction(g['Min Up Time Hr']));down=math.ceil(Fraction(g['Min Down Time Hr']))
        require((Fraction(g['PMin MW']),Fraction(g['PMax MW']),up,down)==expected,'Exact selected native parameters')
        require((record['PMin'],record['PMax'],record['minimum_up'],record['minimum_down'])==expected,'Selected admission parameters')
        require(record['fossil_index']==fossil.index(name) and record['thermal_index']==thermal.index(name),'Selected indices')
    rest=[i for i,n in enumerate(fossil) if n not in SELECTED]
    require(len(rest)==20 and adm['remaining_fossil_indices']==rest and adm['remaining_fossil_names']==[fossil[i] for i in rest],'Unfixed remaining twenty')
    require(adm['remaining_capacity']==[b[i] for i in rest] and adm['remaining_cost']==[a[i] for i in rest],'Remaining coefficients')
    maps=read(PRE/'column_maps.json');require(maps['worlds']==['identity','days_321'],'World order')
    mask=lambda folder,n:tuple(v.vector(v.read_npz(folder/'integrality.npz',('integrality',))['integrality'],('|u1',),n,'mask'))
    jm=tuple(v.vector(v.read_npz(PRE/'joint_integrality.npz',('integrality',))['integrality'],('|u1',),33936,'joint mask'))
    require(jm==tuple(int(6888<=j<18984) for j in range(33936)),'Joint original mask')
    world_results=[]
    for wi,world in enumerate(('identity','days_321')):
        folder=PRE/world;m=v.load_model(folder);meta=read(folder/'model_metadata.json')
        require((m.rows,m.cols,len(m.data))==(34681,23016,145588),'Archived model dimensions')
        require(mask(folder,m.cols)==tuple(int(6888<=j<18984) for j in range(m.cols)),'All original binaries')
        require(meta['offsets']==dict(P=0,U=6888,Y=10920,Z=14952,theta=18984),'Offsets')
        require(meta['unit_names']==names and meta['thermal_unit_names']==thermal and meta['fossil_units']==fossil,'Model roster')
        require(meta['individual_mean_constraints']==0 and meta['budget_MWh']==23195,'Cap/no-means scope')
        mapping=maps['original_to_joint'][wi]
        require(len(mapping)==m.cols and mapping[6888:18984]==list(range(6888,18984)),'Shared all-state mapping')
        with gzip.open(folder/'row_metadata.csv.gz','rt',encoding='utf-8-sig',newline='') as f:labels=list(csv.DictReader(f))
        require(len(labels)==m.rows and [int(x['row']) for x in labels]==list(range(m.rows)),'Row label coverage')
        indexed={}
        for i,label in enumerate(labels):
            key=(label['family'],int(label['hour_0based']),label['uid'])
            require(key not in indexed,'Duplicate semantic row key');indexed[key]=i
        expected_keys={(family,t,name) for family in FAMILIES for t in range(1,168) for name in SELECTED}
        actual_keys={key for key in indexed if key[0] in FAMILIES and key[2] in SELECTED}
        require(actual_keys==expected_keys,'Complete exact selected temporal row set including boundary')
        admission_world=adm['worlds'][wi];require(admission_world['world']==world,'Admission world labels')
        recorded={x['row']:x for x in admission_world['temporal_rows']};recorded_boxes={x['column']:x for x in admission_world['state_boxes']}
        require(len(recorded)==len(admission_world['temporal_rows'])==2004 and len(recorded_boxes)==len(admission_world['state_boxes'])==1512,'Admission record denominator')
        rows_checked=set();boxes_checked=set()
        for name,(_,_,up,down) in zip(SELECTED,SPEC):
            k=thermal.index(name)
            for t in range(168):
                cols={kind:meta['offsets'][kind]+24*t+k for kind in ('U','Y','Z')}
                for kind,c in cols.items():
                    hi=0 if t==0 and kind!='U' else 1
                    require(m.lower[c]==0 and m.upper[c]==hi,'Actual selected initial/all-hour box')
                    require(recorded_boxes[c]=={'column':c,'lower':0,'upper':hi},'Saved box check differs')
                    boxes_checked.add(c)
                if t==0:continue
                u,y,z=cols['U'],cols['Y'],cols['Z']
                terms={
                  'transition':({u:1,u-24:-1,y:-1,z:1},0,0),
                  'exclusive_transition':({y:1,z:1},-math.inf,1),
                  'minimum_up':({**{10920+24*s+k:1 for s in range(max(1,t-up+1),t+1)},u:-1},-math.inf,0),
                  'minimum_down':({**{14952+24*s+k:1 for s in range(max(1,t-down+1),t+1)},u:1},-math.inf,1)}
                for family,(coefs,lo,hi) in terms.items():
                    rid=indexed[(family,t,name)];check_row(m,rid,coefs,lo,hi);rows_checked.add(rid)
                    require(recorded[rid]==dict(row=rid,uid=name,hour=t,family=family,terms=[[j,c] for j,c in sorted(coefs.items())],lower=None if lo==-math.inf else lo,upper=hi),'Saved exact temporal premise differs')
        require(rows_checked==set(recorded) and boxes_checked==set(recorded_boxes),'Full saved premise coverage')
        # Recheck all23 thermal-row slack premises without computing a floor/table.
        thermal_rows=0
        for fi,name in enumerate(fossil):
            j,k=names.index(name),thermal.index(name)
            for t in range(168):
                p,u=41*t+j,6888+24*t+k
                check_row(m,indexed[('thermal_upper',t,name)],{p:1,u:-b[fi]},-math.inf,0)
                check_row(m,indexed[('thermal_lower',t,name)],{p:-1,u:a[fi]},-math.inf,0);thermal_rows+=2
        cap_ids=[i for i,x in enumerate(labels) if x['family']=='fossil_energy_cap'];require(len(cap_ids)==1,'One original cap')
        capterms={41*t+names.index(name):1 for t in range(168) for name in fossil}
        check_row(m,cap_ids[0],capterms,-math.inf,23195)
        world_results.append({'world':world,'selected_temporal_rows':len(rows_checked),'selected_state_boxes':len(boxes_checked),'all_fossil_thermal_rows':thermal_rows,'cap_rows':1})
    require(adm['state_bound']==3328 and adm['hour_state_bound']==559104 and adm['candidate_transition_bound']==4472832,'Static design resource counts')
    require(adm['mature_free_initial'] and adm['clipped_terminal'] and adm['integral_expanded_rows_imply_nominal_binary_rows'],'Boundary declarations')
    for x in manifest:binding(x)
    require({p:sha(p) for p in EXPECTED}==EXPECTED,'Reviewed inputs changed')
    require(not (PRE.parent/'run01').exists(),'Scientific run already exists during preflight')
    result={'status':'PASS_SOURCE_AND_PREPARED_PREMISES_ONLY','utc':datetime.now(timezone.utc).isoformat(),
      'elapsed_seconds':time.perf_counter()-started,'reviewer_source_sha256':sha(__file__),
      'trusted_bindings':EXPECTED,'manifest_bindings_rehashed':101,'byte_identical_copies':14,'worlds':world_results,
      'invented_control_groups_receipt_checked':11,'controls_rerun':False,'producer_imported':False,
      'decoder_sha256':KERNEL_SHA,'scientific_dp_runs':0,'scientific_threshold_queries':0,'scientific_graph_runs':0,
      'model_builds':0,'optimizer_calls':0,'inputs_unchanged':True,'bound_or_rejection_claim':False}
    save('prepared_review.json',result);print(json.dumps({'status':result['status'],'elapsed_seconds':result['elapsed_seconds'],'report_sha256':sha(OUT/'prepared_review.json')}))

if __name__=='__main__':
    try:main()
    except BaseException as e:
        save('prepared_review_failure.json',{'status':'FAIL_PRESERVED_NO_RETRY','exception_type':type(e).__name__,'message':str(e),'scientific_dp_runs':0,'optimizer_calls':0})
        raise
