"""Independent original-row replay of the fixed-union necessary energy floor."""
from pathlib import Path
from fractions import Fraction as F
import datetime,hashlib,importlib.util,json,math,sys,time
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
PRE=ROOT/'results/research_next/common_union/prepared'
KERNEL=ROOT/'src/research8h_standalone_verify.py'
TAU=F.from_float(1e-5)
def need(x,message):
    if not x:raise AssertionError(message)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def desc(p):return dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))
def rational(x):return F(int(x['numerator']),int(x['denominator']))
def encoded(x):return dict(numerator=str(x.numerator),denominator=str(x.denominator),approximate=float(x))
def main():
    start=time.perf_counter()
    need(sha(KERNEL)=='708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f','Pinned decoder')
    need(sha(ROOT/'src/researchnext_union_energy_floor.py')=='dfb8069926c180edd266a5b8bc92a0154737627ab437a83d7f6fa80eb8bb53ee','Producer source')
    need(sha(ROOT/'docs/research_next/UNION_ENERGY_FLOOR_PROTOCOL.md')=='b743544e02be563c750abf3f73ebcca13ee7c10b8cb9a3fea7d91774997e61ec','Protocol')
    started=read(OUT/'started.json');bindings=started['inputs'];need(len(bindings)==14,'Selected input denominator')
    for x in bindings:need(desc(Path(x['path']))==x,'Producer selected input binding')
    need(sha(PRE/'input_manifest.json')=='1337e9674d15fc52023733b8c72b1140c20d01a472a287fd43a90cd5719d3a2d','Historical manifest')
    manifest={x['path'].casefold():x for x in read(PRE/'input_manifest.json')['files']}
    extra=PRE/'joint/column_maps.json';extra_binding=desc(extra);need(extra_binding==manifest[str(extra.resolve()).casefold()],'Original mapping binding')
    snapshots=[desc(p) for p in (OUT/'started.json',OUT/'result.json',OUT/'identity_derivations.json',OUT/'days_321_derivations.json')]
    spec=importlib.util.spec_from_file_location('independent_floor_decoder',KERNEL);v=importlib.util.module_from_spec(spec);sys.modules[spec.name]=v;spec.loader.exec_module(v)
    fixed={x['column']:F(x['value']) for x in read(PRE/'candidate_schedule.json')['fixed_columns']}
    fixedset=set(fixed)
    need(len(fixed)==12096 and set(fixed)==set(range(6888,18984)) and set(fixed.values())<={F(0),F(1)},'Exact complete frozen bits')
    maps=read(extra)['original_to_joint'];need(len(maps)==2,'Two-world mappings')
    for mapping in maps:need(len(mapping)==23016 and all(mapping[j]==j for j in fixed),'World state coordinates equal joint fixed coordinates')
    summaries=read(OUT/'result.json');need(summaries['optimizer_calls']==0 and summaries['unrestricted_common_verdict']=='UNKNOWN','Claim scope')
    need(rational(summaries['tau'])==TAU,'Same expanded tolerance')
    reviewed=[]
    for number,world in enumerate(('identity','days_321')):
        folder=PRE/world;m=v.load_model(folder);metadata=read(folder/'model_metadata.json');d=read(OUT/(world+'_derivations.json'))
        need((m.rows,m.cols)==(34681,23016),'Original dimensions')
        mask=v.vector(v.read_npz(folder/'integrality.npz',('integrality',))['integrality'],('|u1',),m.cols,'binary mask')
        need({j for j,b in enumerate(mask) if b}==set(fixed),'Full original 12096 mask')
        fossil={metadata['unit_names'].index(n) for n in metadata['fossil_units']}
        need(len(fossil)==23 and len(metadata['unit_names'])==41 and metadata['hours']==168,'Physical roster dimensions')
        capset={41*t+j for t in range(168) for j in fossil}
        lo=[F(x)-TAU for x in m.lower[:6888]];hi=[F(x)+TAU for x in m.upper[:6888]]
        rows=[];single=0;aggregate={};caps=[]
        for i in range(m.rows):
            row=dict(zip(m.indices[m.indptr[i]:m.indptr[i+1]],map(F,m.data[m.indptr[i]:m.indptr[i+1]])))
            need(len(row)==m.indptr[i+1]-m.indptr[i],'No duplicate sparse coordinates');rows.append(row)
            live=set(row)-fixedset
            if len(live)==1:
                j=next(iter(live))
                if j<6888:
                    a=row[j];need(a!=0,'Nonzero singleton coefficient');single+=1
                    constant=sum((row[k]*fixed[k] for k in row if k in fixed),F(0))
                    if math.isfinite(m.row_lower[i]):
                        bound=(F(m.row_lower[i])-TAU-constant)/a
                        if a>0:lo[j]=max(lo[j],bound)
                        else:hi[j]=min(hi[j],bound)
                    if math.isfinite(m.row_upper[i]):
                        bound=(F(m.row_upper[i])+TAU-constant)/a
                        if a>0:hi[j]=min(hi[j],bound)
                        else:lo[j]=max(lo[j],bound)
            if len(row)==41 and set(row.values())=={F(1)}:
                t=min(row)//41
                if 0<=t<168 and set(row)==set(range(41*t,41*t+41)):
                    need(t not in aggregate,'Unique aggregate');aggregate[t]=i
            if set(row)==capset and set(row.values())=={F(1)}:caps.append(i)
        need(len(aggregate)==168 and len(caps)==1,'Actual aggregate/cap coordinate roster')
        caprow=caps[0];need(m.row_upper[caprow]==23195,'Original cap unchanged')
        need(len(d['variables'])==6888 and len(d['hourly'])==168,'Complete derivation denominator')
        support=set()
        for j,item in enumerate(d['variables']):
            need(item['column']==j and rational(item['lower'])==lo[j] and rational(item['upper'])==hi[j],'Complete tight singleton intervals')
            for side,expected in [('lower',lo[j]),('upper',hi[j])]:
                origin=item[side+'_source']
                if 'box' in origin:
                    need(origin['box']==j and origin['side']==side,'Box provenance')
                    actual=F(m.lower[j])-TAU if side=='lower' else F(m.upper[j])+TAU
                else:
                    i=origin['row'];row=rows[i];need(set(row)-fixedset=={j},'Reported source is singleton P plus fixed bits')
                    a=row[j];lower=origin['side']=='lower';need((lower==(a>0))==(side=='lower'),'Signed source inequality')
                    endpoint=m.row_lower[i] if lower else m.row_upper[i];need(math.isfinite(endpoint),'Finite source endpoint')
                    actual=(F(endpoint)+(-TAU if lower else TAU)-sum((row[k]*fixed[k] for k in row if k in fixed),F(0)))/a;support.add(i)
                need(actual==expected,'Archived source attains selected interval')
        total=F(0);bad=[]
        for t,h in enumerate(d['hourly']):
            i=aggregate[t];bal_lo=F(m.row_lower[i])-TAU;bal_hi=F(m.row_upper[i])+TAU
            direct=sum((lo[41*t+j] for j in fossil),F(0));balance=bal_lo-sum((hi[41*t+j] for j in range(41) if j not in fossil),F(0))
            floor=max(direct,balance);total+=floor
            lower=sum(lo[41*t:41*t+41],F(0));upper=sum(hi[41*t:41*t+41],F(0))
            if lower>bal_hi or upper<bal_lo:bad.append(t)
            need(h['hour']==t and h['aggregate_row']==i,'Hourly coordinate label')
            for key,value in dict(direct_fossil_floor=direct,balance_minus_nonfossil_upper=balance,selected_floor=floor,total_interval_lower=lower,total_interval_upper=upper,balance_lower=bal_lo,balance_upper=bal_hi).items():
                need(rational(h[key])==value,'Hourly exact derivation')
            need(h['active']==('individual_lower_sum' if direct>=balance else 'balance_minus_other_upper'),'Tie/selection label')
        cap=F(m.row_upper[caprow])+TAU;gap=total-cap;s=summaries['worlds'][number]
        empty=[j for j in range(6888) if lo[j]>hi[j]]
        need(s['world']==world and s['single_generation_rows']==single and s['cap_row']==caprow,'Summary labels')
        need(s['empty_generation_intervals']==empty and s['disjoint_hourly_aggregate_intervals']==bad,'Other contradiction scope')
        need(rational(s['necessary_fossil_energy_floor'])==total and rational(s['expanded_cap'])==cap and rational(s['floor_minus_cap'])==gap,'Exact total/cap/excess')
        need(s['strict_floor_excess']==(gap>0) and s['fixed_schedule_obstruction_pending_independent_review']==bool(empty or bad or gap>0),'Classification')
        reviewed.append(dict(world=world,variables=6888,singleton_rows=single,hours=168,binary_mask=12096,source_rows_used_in_interval_records=len(support),
            necessary_floor=encoded(total),expanded_cap=encoded(cap),excess=encoded(gap),fixed_schedule_rejected=gap>0,empty_intervals=len(empty),disjoint_hour_intervals=len(bad)))
    for x in bindings+snapshots+[extra_binding]:need(desc(Path(x['path']))==x,'Input/output changed during review')
    result=dict(status='INDEPENDENT_EXACT_FIXED_SCHEDULE_OBSTRUCTION_PASS',worlds=reviewed,inputs_verified=len(bindings)+1,producer_outputs_unchanged=snapshots,
        optimizer_calls=0,producer_imports=0,no_new_schedule=True,unrestricted_common_verdict='UNKNOWN',not_an_individual_full_uc_negative=True,
        scope='Exact implication from original expanded boxes/singleton-P rows/aggregate/cap after prescribed state substitution; unused network rows need not be feasible.',
        elapsed_seconds=time.perf_counter()-start,source_sha256=sha(__file__))
    with (OUT/'INDEPENDENT_REVIEW.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result))
if __name__=='__main__':main()
