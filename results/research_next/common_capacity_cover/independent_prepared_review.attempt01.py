"""Read-only original-premise audit; no scientific DP or threshold calculation."""
from pathlib import Path
from fractions import Fraction as F
import csv,gzip,hashlib,importlib.util,json,math,sys,time
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3];ARM=Path(__file__).resolve().parent;PRE=ARM/'prepared'
KERNEL=ROOT/'src/research8h_standalone_verify.py'
def need(x,s):
    if not x:raise AssertionError(s)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def binding(p):return dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))
def main():
    start=time.perf_counter();need(not (ARM/'run01').exists(),'Scientific run absent')
    source=ROOT/'src/researchnext_common_capacity_cover.py';protocol=ROOT/'docs/research_next/COMMON_CAPACITY_COVER_PROTOCOL.md'
    need(sha(source)=='b0e07f9cba7ea91696ef5884f94666592263003f610fd7104a23ff4760f42ab8','Reviewed source')
    need(sha(protocol)=='157b910ec99e5f0f42a9f80bb5eee42a25382cf16555722d52949c3022b3060f','Reviewed protocol')
    freeze=read(PRE/'prepared_freeze.json');before=[binding(PRE/'prepared_freeze.json'),binding(PRE/'input_manifest.json')]
    need(freeze['source_sha256']==sha(source) and freeze['protocol_sha256']==sha(protocol),'Freeze source/protocol')
    need(binding(PRE/'input_manifest.json')==freeze['input_manifest'] and freeze['input_manifest']['sha256']=='6018b53d796926f5e1ab368958d8a03a3a7e21e67d88702825b057ac672b10e3','Manifest identity')
    items=read(PRE/'input_manifest.json')['files'];need(len(items)==71 and len({x['path'].casefold() for x in items})==71,'71 unique bindings')
    for x in items:need(binding(Path(x['path']))==x,'Input binding')
    need(binding(PRE/'admission.json')==freeze['admission'] and freeze['admission']['sha256']=='0a9abd8f40376f54d834763c118ea9c70642c3a9ca966f91111e2fb6ef32d8dd','Admission pin')
    copies=read(PRE/'copy_manifest.json')['files'];need(len(copies)==13,'Copy count')
    for x in copies:
        need(binding(Path(x['original']['path']))==x['original'] and binding(Path(x['copy']['path']))==x['copy'],'Captured copy binding')
        need(Path(x['original']['path']).read_bytes()==Path(x['copy']['path']).read_bytes(),'Original byte equality')
    need(sha(KERNEL)=='708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f','Decoder hash')
    spec=importlib.util.spec_from_file_location('independent_cover_premises_decoder',KERNEL);v=importlib.util.module_from_spec(spec);sys.modules[spec.name]=v;spec.loader.exec_module(v)
    a=read(PRE/'admission.json');need(a['scientific_dp_tables']==a['scientific_threshold_queries']==a['optimizer_calls']==0,'No scientific calculation admitted')
    need(F(int(a['tau']['numerator']),int(a['tau']['denominator']))==F.from_float(1e-5),'Same exact tau')
    maps=read(PRE/'column_maps.json');need(maps['worlds']==['identity','days_321'],'World order')
    for mp in maps['original_to_joint']:
        need(len(mp)==23016 and len(set(mp))==23016 and mp[6888:18984]==list(range(6888,18984)),'Shared complete states and injective world map')
    jm=v.vector(v.read_npz(PRE/'joint_integrality.npz',('integrality',))['integrality'],('|u1',),33936,'joint mask')
    need(tuple(jm)==tuple(int(6888<=j<18984) for j in range(33936)),'All12096 original joint binary declarations')
    with (PRE/'gen.csv').open(encoding='utf-8-sig',newline='') as f:gen=list(csv.DictReader(f))
    native={x['GEN UID']:x for x in gen};need(len(native)==len(gen),'Native roster unique')
    verified=[];world_tuples=[]
    for wi,world in enumerate(('identity','days_321')):
        folder=PRE/world;m=v.load_model(folder);meta=read(folder/'model_metadata.json');w=a['worlds'][wi]
        need(w['world']==world and len(w['hours'])==168,'World/hour denominator')
        need((m.rows,m.cols,len(m.data))==(34681,23016,145588),'Original model dimensions')
        mask=v.vector(v.read_npz(folder/'integrality.npz',('integrality',))['integrality'],('|u1',),m.cols,'original mask')
        need(tuple(mask)==tuple(int(6888<=j<18984) for j in range(m.cols)),'Original full world mask')
        need(all(m.lower[j]==0 and m.upper[j]==1 for j,b in enumerate(mask) if b),'Exact original state boxes')
        need(all(math.isfinite(m.lower[j]) and math.isfinite(m.upper[j]) for j in range(6888)),'Finite generation boxes')
        names=meta['unit_names'];therm=meta['thermal_unit_names'];fossil=meta['fossil_units']
        need(names==a['unit_names'] and therm==a['thermal_names'] and fossil==a['fossil_names'],'Same ordered world/admission roster')
        need(len(set(names))==41 and len(set(therm))==24 and len(set(fossil))==23,'Roster counts')
        need([n for n in names if native[n]['Fuel'] in ('Coal','NG','Oil')]==fossil,'Actual23 fossil fuel set')
        need(set(therm)-set(fossil)=={'121_NUCLEAR_1'} and native['121_NUCLEAR_1']['Fuel']=='Nuclear','Nuclear excluded')
        need(meta['offsets']==dict(P=0,U=6888,Y=10920,Z=14952,theta=18984),'Full coordinate system')
        fi=[names.index(n) for n in fossil];ni=[j for j in range(41) if j not in fi]
        with gzip.open(folder/'row_metadata.csv.gz','rt',encoding='utf-8-sig',newline='') as f:labels=list(csv.DictReader(f))
        need(len(labels)==m.rows and [int(x['row']) for x in labels]==list(range(m.rows)),'Metadata row indexing')
        def row(i):
            lo,hi=m.indptr[i],m.indptr[i+1];d=dict(zip(m.indices[lo:hi],map(F,m.data[lo:hi])))
            need(len(d)==hi-lo,'No duplicate row coordinate');return d
        cap=w['cap_row'];need(labels[cap]['family']=='fossil_energy_cap','Cap label')
        need(row(cap)=={41*t+j:F(1) for t in range(168) for j in fi} and m.row_lower[cap]==-math.inf and m.row_upper[cap]==23195,'Exact complete original cap')
        need(float.fromhex(w['cap_upper_hex'])==m.row_upper[cap],'Cap captured endpoint')
        tuples=[];checked_rows=set()
        for t,h in enumerate(w['hours']):
            need(h['hour']==t and len(h['thermal_sources'])==24,'Thermal/hour record denominator')
            ar=h['aggregate_row'];need(row(ar)=={41*t+j:F(1) for j in range(41)},'Aggregate actual coefficients')
            need(labels[ar]['family']=='aggregate_balance' and int(labels[ar]['hour_0based'])==t,'Aggregate label')
            need(math.isfinite(m.row_lower[ar]) and m.row_lower[ar]==m.row_upper[ar] and float.fromhex(h['aggregate_lower_hex'])==m.row_lower[ar],'Aggregate endpoint')
            need(h['nonfossil_upper_boxes']==[dict(column=41*t+j,upper_hex=m.upper[41*t+j].hex()) for j in ni],'All18 original nonfossil boxes')
            need(h['fossil_lower_boxes']==[dict(column=41*t+j,lower_hex=m.lower[41*t+j].hex()) for j in fi],'All23 original fossil lower boxes')
            capacity={};cost={}
            for k,s in enumerate(h['thermal_sources']):
                name=therm[k];j=names.index(name);p=41*t+j;u=6888+24*t+k
                need(s['uid']==name and s['P_column']==p and s['U_column']==u,'Original thermal coordinate mapping')
                b=s['PMax'];mn=s['PMin'];need(type(b) is int and type(mn) is int and 0<=mn<=b,'Exact nonnegative integer names')
                need(F(native[name]['PMax MW'])==b and F(native[name]['PMin MW'])==mn,'Native exact nameplate correspondence')
                for family,i,expected in [('thermal_upper',s['upper_row'],{p:F(1),**({u:F(-b)} if b else {})}),('thermal_lower',s['lower_row'],{p:F(-1),**({u:F(mn)} if mn else {})})]:
                    need(i not in checked_rows,'Distinct selected row');checked_rows.add(i)
                    need(row(i)==expected and m.row_lower[i]==-math.inf and m.row_upper[i]==0,'Exact original thermal row and endpoints')
                    need(labels[i]['family']==family and labels[i]['uid']==name and int(labels[i]['hour_0based'])==t,'Original thermal row label')
                capacity[name]=b;cost[name]=mn
            tuples.append((tuple(capacity[n] for n in fossil),tuple(cost[n] for n in fossil)))
        need(len(checked_rows)==8064,'All actual selected thermal rows')
        world_tuples.append(tuples);verified.append(dict(world=world,thermal_rows=8064,aggregate_rows=168,cap_terms=3864,generation_boxes=6888,original_binary_columns=12096))
    need(world_tuples[0]==world_tuples[1],'Identical ordered fossil coefficients across both worlds each hour')
    groups=a['tuples'];need(len(groups)==freeze['distinct_tuples']<=168,'Declared tuple count guard')
    need([g['group'] for g in groups]==list(range(len(groups))) and len(a['hour_group'])==168,'Ordered group mapping')
    distinct=[]
    for t,pair in enumerate(world_tuples[0]):
        if pair not in distinct:distinct.append(pair)
        gi=a['hour_group'][t];need(gi==distinct.index(pair),'First-appearance exact tuple group')
        g=groups[gi];need((tuple(g['capacity']),tuple(g['cost']))==pair and g['sum_capacity']==sum(pair[0])<=100000,'Exact admitted resource tuple')
    need(len(distinct)==len(groups),'No extra tuple or skipped group')
    need(not (ARM/'run01').exists(),'Scientific run still absent')
    for x in items+before:need(binding(Path(x['path']))==x,'Inputs unchanged during review')
    result=dict(status='PASS_PREPARED_CAPACITY_COVER',source_sha256=sha(source),protocol_sha256=sha(protocol),freeze_sha256=sha(PRE/'prepared_freeze.json'),
        bindings=71,byte_identical_copies=13,worlds=verified,distinct_tuples=len(groups),original_common_assembly_inherited=True,
        scientific_dp_tables=0,scientific_threshold_queries=0,optimizer_calls=0,producer_imports=0,all_inputs_unchanged=True,
        exact_row_box_and_binary_premises=True,source_bound_direction_review=True,readiness_scope='No scientific bound, threshold or verdict computed',
        elapsed_seconds=time.perf_counter()-start,review_source_sha256=sha(__file__))
    with (ARM/'independent_prepared_review.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result))
if __name__=='__main__':main()
