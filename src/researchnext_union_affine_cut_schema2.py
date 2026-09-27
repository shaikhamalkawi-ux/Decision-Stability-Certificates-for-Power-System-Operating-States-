"""Two fixed, inherited-proof affine cuts; no selection search or optimizer."""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import time
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
ARM=ROOT/'results/research_next/union_affine_cut_schema2';PRE=ARM/'prepared';RUN=ARM/'run01'
OLD=ROOT/'results/research_next/common_union/prepared'
FLOOR=ROOT/'results/research_next/union_energy_floor'
COMMON=ROOT/'results/research_next/common_commitment'
PROTOCOL=ROOT/'docs/research_next/UNION_AFFINE_CUT_SCHEMA2_PROTOCOL.md'
FAILED_PRE=ROOT/'results/research_next/union_affine_cut/prepared'
KERNEL=ROOT/'src/research8h_standalone_verify.py'
TAU=Q.from_float(1e-5);BUDGET=120.0;WORLDS=('identity','days_321')
PINS={
 'src/researchnext_union_affine_cut.py':'746022d4ef39c7a5bc97969c32b644cc268b1a5c3a4ddf79d64082537bb7f541',
 'docs/research_next/UNION_AFFINE_CUT_PROTOCOL.md':'2ab0739a10463712d1d31b19433e97a085c50086035661c14246e4da0d66e036',
 'results/research_next/union_affine_cut/prepared/prepared_freeze.json':'5c3199380ed8e6502384f5a3790104291f7723b8a086911aa6c53606de99b7dc',
 'results/research_next/union_affine_cut/prepared/input_manifest.json':'21402d45b3d1796c99ff8e5c51e14953a1f2bb4eae51a4eed70facdd91d1696a',
 'results/research_next/union_affine_cut/run01/failure.json':'e5934c8fc7d1bad2e93746170113379f072a642024ee6e0a57bbae2f83eaee7b',
 'results/research_next/union_affine_cut/CONTROL_SCHEMA_DIAGNOSIS.json':'55b27d44a5dff0206c5ba179290068fbae393b92b2fa40475ee5155b09f38b01',
 'src/research8h_standalone_verify.py':'708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f',
 'docs/research_next/UNION_AFFINE_CUT_PROPOSAL.md':'83feed5e953c0a5897d0754465815f1b30992f226f6743c379eb74461c487092',
 'src/researchnext_union_energy_floor.py':'dfb8069926c180edd266a5b8bc92a0154737627ab437a83d7f6fa80eb8bb53ee',
 'docs/research_next/UNION_ENERGY_FLOOR_PROTOCOL.md':'b743544e02be563c750abf3f73ebcca13ee7c10b8cb9a3fea7d91774997e61ec',
 'results/research_next/common_union/prepared/prepared_freeze.json':'8d5e348d91db8ae082a1a036d2359ac382891b25849e9e682fb833e9ae52d0a2',
 'results/research_next/common_union/prepared/input_manifest.json':'1337e9674d15fc52023733b8c72b1140c20d01a472a287fd43a90cd5719d3a2d',
 'results/research_next/union_energy_floor/started.json':'6f8b0150abc8ecad2e53a4c727dca85c6fa68374f2298787f0755a2ecd81ac95',
 'results/research_next/union_energy_floor/result.json':'3d6577baf7f63c538fd1a7717a369dad625714d3f2edf3d731b4f1f72be39d49',
 'results/research_next/union_energy_floor/identity_derivations.json':'ddb42e1a8f6fddbd3091cfda0f1105a4f50223f9109ff985c7783f9881b07260',
 'results/research_next/union_energy_floor/days_321_derivations.json':'d8c767688bf12b30efcc850ddd6f0cd01b49671a1952dcc361cef296e7fa6671',
 'results/research_next/union_energy_floor/INDEPENDENT_REVIEW.json':'4ce224e7242bbad68ccfd5a9a5220b63e0b66d1db97848dda3098fa56743da9e',
 'results/research_next/common_commitment/INDEPENDENT_POSTRUN_REVIEW.json':'f442edeb3f90c5d602a1b60cdef1b96b4d560ebbe97fae28c4ca21c6077eadba',
 'results/research_next/common_commitment/INDEPENDENT_LP_NONBINARY_STATES.json':'bc371fa53ae5f94d3f1536eefc526871b60d4de2f7bae4b027a088d9d2ba4282',
 'results/research_next/common_commitment/run01/lp/raw_solution.npz':'90c8b308a6ce8e7671adbe3059887d6ce27489fa3d68aa601c2474b32d2d462a',
 'results/research_next/common_commitment/prepared/input_manifest.json':'8ff99b1f4450ac15e91b26a261a85c98d574bbbdac3f7fe149efd9fd07204a5c',
}

def need(x,message):
    if not x:raise ValueError(message)
def utc():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,x):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(x,f,indent=2,allow_nan=False);f.write('\n')
def desc(p,data=None):
    p=Path(p).resolve();data=p.read_bytes() if data is None else data
    return dict(path=str(p),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
def check_bindings(items):
    need(len({x['path'].casefold() for x in items})==len(items),'Duplicate binding')
    for x in items:need(desc(x['path'])==x,'Frozen input changed')
def rat(q):return dict(numerator=str(q.numerator),denominator=str(q.denominator),approximate=float(q))
def unrat(x):return Q(int(x['numerator']),int(x['denominator']))
def sparse(x):return [dict(column=j,coefficient=rat(a)) for j,a in sorted(x.items()) if a]
def decoder():
    need(sha(KERNEL)==PINS['src/research8h_standalone_verify.py'],'Decoder changed')
    spec=importlib.util.spec_from_file_location('union_affine_cut_decoder',KERNEL);v=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=v;spec.loader.exec_module(v);return v

def prepare():
    need(not PRE.exists() and not RUN.exists(),'Fresh preparation only');captured={}
    def capture(p,expected=None):
        data=Path(p).read_bytes();item=desc(p,data);key=item['path'].casefold()
        need(expected is None or item==expected,'Captured historical binding differs')
        need(key not in captured or captured[key][1]==item,'Conflicting captured source');captured[key]=(data,item);return data
    for rel,digest in PINS.items():need(hashlib.sha256(capture(ROOT/rel)).hexdigest()==digest,'Pinned input changed: '+rel)
    inherited=json.loads(captured[str((OLD/'input_manifest.json').resolve()).casefold()][0])['files']
    lookup={x['path'].casefold():x for x in inherited};need(len(inherited)==94 and len(lookup)==94,'Union manifest scope')
    names=['candidate_schedule.json','joint/column_maps.json']+[f'{w}/{n}' for w in WORLDS for n in ('matrix.npz','bounds.npz','integrality.npz','model_metadata.json')]
    for name in names:capture(OLD/name,lookup[str((OLD/name).resolve()).casefold()])
    old_manifest=json.loads(captured[str((COMMON/'prepared/input_manifest.json').resolve()).casefold()][0])['files']
    old_map={x['path'].casefold():x for x in old_manifest};need(len(old_manifest)==48,'Original common manifest scope')
    # Bind actual old point/model correspondence without repeating point membership.
    for name in ['joint/column_maps.json']+[f'{w}/{n}' for w in WORLDS for n in ('matrix.npz','bounds.npz','integrality.npz','model_metadata.json')]:
        p=COMMON/'prepared'/name;data=capture(p,old_map[str(p.resolve()).casefold()])
        need(data==captured[str((OLD/name).resolve()).casefold()][0],'Accepted control world/model relation')
    failed_manifest=json.loads(captured[str((FAILED_PRE/'input_manifest.json').resolve()).casefold()][0])['files']
    failed_lookup={x['path'].casefold():x for x in failed_manifest}
    inherited_copy_names=names+[f'{w}/derivations.json' for w in WORLDS]+['floor_result.json','continuous_control.npz']
    for name in inherited_copy_names:capture(FAILED_PRE/name,failed_lookup[str((FAILED_PRE/name).resolve()).casefold()])
    for p in (Path(__file__),PROTOCOL):capture(p)
    initial=[x[1] for x in captured.values()];PRE.mkdir(parents=True)
    save(PRE/'preparation_started.json',dict(utc=utc(),optimizer_calls=0,cut_arithmetic=0))
    copies=[]
    copy_pairs=[(OLD/n,n) for n in names]+[(FLOOR/f'{w}_derivations.json',f'{w}/derivations.json') for w in WORLDS]
    copy_pairs +=[(FLOOR/'result.json','floor_result.json'),(COMMON/'run01/lp/raw_solution.npz','continuous_control.npz')]
    for src,name in copy_pairs:
        data,item=captured[str(src.resolve()).casefold()]
        need(data==captured[str((FAILED_PRE/name).resolve()).casefold()][0],'Schema successor must inherit identical model/selection/control bytes')
        dest=PRE/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
        need(sha(dest)==item['sha256'],'Byte copy changed');copies.append(dict(source=item,copy=desc(dest)))
    need(len(copies)==14,'Copy count')
    proof=json.loads(captured[str((COMMON/'INDEPENDENT_POSTRUN_REVIEW.json').resolve()).casefold()][0])
    need(proof['posthoc_continuous_check']['expanded_pass'] and proof['posthoc_continuous_check']['point_changed_or_rounded']==False,'Inherited continuous control admission')
    census=json.loads(captured[str((COMMON/'INDEPENDENT_LP_NONBINARY_STATES.json').resolve()).casefold()][0])
    need(census['raw_solution_sha256']==PINS['results/research_next/common_commitment/run01/lp/raw_solution.npz'],'Control hash admission')
    save(PRE/'copy_provenance.json',dict(copies=copies,all_model_and_selection_bytes_unchanged=True))
    save(PRE/'plan.json',dict(worlds=list(WORLDS),cut_count=2,phase_seconds=BUDGET,selection='exact archived variable sources and hourly active label; no reselection',
        arithmetic='exact binary64 rationals',tau=rat(TAU),optimizer_calls=0,union_recomputations=0,control_point_rounded=False,
        no_old_full_point_replay=True,negative_control='saved accepted expanded continuous joint point',full_common_verdict='UNKNOWN'))
    check_bindings(initial);items=initial+[desc(p) for p in PRE.rglob('*') if p.is_file()];check_bindings(items)
    save(PRE/'input_manifest.json',dict(files=items));check_bindings(items)
    save(PRE/'prepared_freeze.json',dict(utc=utc(),source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),manifest_sha256=sha(PRE/'input_manifest.json'),
        bindings=len(items),copies=len(copies),optimizer_calls=0,cut_arithmetic=0,separate_execution_GO_required=True))

def upper_endpoint(coefficients,endpoint,side,tau):
    """Original finite lower/upper endpoint as q*x <= r, expanded exactly once."""
    need(side in ('lower','upper'),'Endpoint side');sign=1 if side=='upper' else -1
    return {j:sign*a for j,a in coefficients.items() if a},sign*endpoint+tau

def normalize_generation(q,r,column,lower):
    a=q.get(column,Q(0));need(a<0 if lower else a>0,'Wrong generation inequality direction')
    weight=1/abs(a);need(weight>0,'Nonpositive endpoint multiplier')
    return {j:weight*x for j,x in q.items()},weight*r,weight

def combine_endpoints(endpoint,weights,columns,checkpoint):
    vector=[Q(0)]*columns;rhs=Q(0)
    for key,weight in sorted(weights.items()):
        checkpoint();need(weight>=0,'Nonnegative combined endpoint multipliers');q,r=endpoint(key);rhs+=weight*r
        for j,a in q.items():
            need(0<=j<columns,'Original full column coordinate');vector[j]+=weight*a
    return vector,rhs

def run(expected):
    began=time.perf_counter();need(not RUN.exists(),'Single new arithmetic execution')
    need(sha(PRE/'prepared_freeze.json')==expected,'External freeze');f=read(PRE/'prepared_freeze.json')
    need(f['source_sha256']==sha(__file__) and f['protocol_sha256']==sha(PROTOCOL),'Source/protocol changed')
    need(f['manifest_sha256']==sha(PRE/'input_manifest.json'),'Manifest changed');items=read(PRE/'input_manifest.json')['files'];check_bindings(items)
    transport=[desc(PRE/'input_manifest.json'),desc(PRE/'prepared_freeze.json')]
    RUN.mkdir();save(RUN/'execution_started.json',dict(utc=utc(),freeze_sha256=expected,optimizer_calls=0))
    outputs=[];current=None
    def budget():
        if time.perf_counter()-began>BUDGET:raise TimeoutError('Prospective 120-second arithmetic phase')
    try:
        budget();v=decoder();fixed={x['column']:Q(x['value']) for x in read(PRE/'candidate_schedule.json')['fixed_columns']}
        U=set(range(6888,10920));need(set(fixed)==set(range(6888,18984)) and set(fixed.values())<={Q(0),Q(1)},'Complete union states')
        control=v.vector(v.read_npz(PRE/'continuous_control.npz',('vector','row_value','row_dual','col_dual'))['vector'],('<f8',),33936,'unrounded control')
        need(all(math.isfinite(x) for x in control),'Finite control');control=tuple(map(Q,control))
        mappings=read(PRE/'joint/column_maps.json')['original_to_joint'];need(len(mappings)==2,'Two worlds')
        floor=read(PRE/'floor_result.json');need(unrat(floor['tau'])==TAU,'Same original expansion')
        for wn,world in enumerate(WORLDS):
            current=world;budget();m=v.load_model(PRE/world);meta=read(PRE/world/'model_metadata.json');d=read(PRE/world/'derivations.json')
            need((m.rows,m.cols)==(34681,23016),'Original shape')
            bits=v.vector(v.read_npz(PRE/world/'integrality.npz',('integrality',))['integrality'],('|u1',),m.cols,'full mask')
            need({j for j,b in enumerate(bits) if b}==set(fixed),'Original full state mask')
            mapping=mappings[wn];need(len(mapping)==m.cols and all(mapping[j]==j for j in fixed),'Shared state mapping')
            fossil={meta['unit_names'].index(n) for n in meta['fossil_units']};need(len(fossil)==23 and len(meta['unit_names'])==41,'Fossil roster')
            capset={41*t+j for t in range(168) for j in fossil};summary=floor['worlds'][wn]
            need(summary['world']==world and len(d['variables'])==6888 and len(d['hourly'])==168,'Fixed proof denominator')
            cache={};weights={};hour_records=[]
            def endpoint(key):
                if key not in cache:
                    kind,i,side=key
                    if kind=='row':
                        need(0<=i<m.rows,'Row range');lo,hi=m.indptr[i],m.indptr[i+1]
                        coeff=dict(zip(m.indices[lo:hi],map(Q,m.data[lo:hi])));need(len(coeff)==hi-lo,'Duplicate sparse column')
                        value=m.row_lower[i] if side=='lower' else m.row_upper[i]
                    else:
                        need(kind=='box' and 0<=i<m.cols,'Box coordinate');coeff={i:Q(1)};value=m.lower[i] if side=='lower' else m.upper[i]
                    need(math.isfinite(value),'Finite selected endpoint');cache[key]=upper_endpoint(coeff,Q(value),side,TAU)
                return cache[key]
            def add(key,weight):
                need(weight>=0,'Nonnegative proof multiplier');weights[key]=weights.get(key,Q(0))+weight
            for t,hour in enumerate(d['hourly']):
                budget();need(hour['hour']==t,'Hour label');active=hour['active'];terms=[];qhour={};rhour=Q(0)
                def local(key,weight):
                    nonlocal rhour
                    q,r=endpoint(key);add(key,weight);rhour+=weight*r
                    for j,a in q.items():qhour[j]=qhour.get(j,Q(0))+weight*a
                    terms.append(dict(kind=key[0],index=key[1],side=key[2],multiplier=rat(weight)))
                if active=='individual_lower_sum':selected=[(41*t+j,True) for j in sorted(fossil)]
                else:
                    need(active=='balance_minus_other_upper','Archived active label');key=('row',hour['aggregate_row'],'lower');q,r=endpoint(key)
                    need(q=={41*t+j:Q(-1) for j in range(41)},'Actual original aggregate lower row')
                    local(key,Q(1));selected=[(41*t+j,False) for j in range(41) if j not in fossil]
                for j,lower in selected:
                    item=d['variables'][j];need(item['column']==j,'Generation record coordinate');origin=item[('lower' if lower else 'upper')+'_source']
                    key=('row',origin['row'],origin['side']) if 'row' in origin else ('box',origin['box'],origin['side'])
                    if key[0]=='box':need(key[1]==j,'Selected box coordinate')
                    q,r=endpoint(key);need(set(q)-{j}<=U,'Actual selected proof is U-only')
                    nq,nr,weight=normalize_generation(q,r,j,lower)
                    value=(sum((a*fixed[k] for k,a in nq.items() if k!=j),Q(0))-nr) if lower else (nr-sum((a*fixed[k] for k,a in nq.items() if k!=j),Q(0)))
                    need(value==unrat(item['lower' if lower else 'upper']),'Selected source union value')
                    local(key,weight)
                qhour={j:a for j,a in qhour.items() if a};power={j:a for j,a in qhour.items() if j<6888}
                need(power=={41*t+j:Q(-1) for j in fossil},'Full hourly generation cancellation')
                need(set(qhour)-set(power)<=U,'No Y/Z/theta residual')
                evaluated=-rhour+sum((a*fixed[j] for j,a in qhour.items() if j in U),Q(0))
                need(evaluated==unrat(hour['selected_floor']),'Archived hourly branch value')
                hour_records.append(dict(hour=t,active=active,terms=terms,union_selected_floor=rat(evaluated)))
            capkey=('row',summary['cap_row'],'upper');cq,cap=endpoint(capkey)
            need(cq=={j:Q(1) for j in capset} and cap==Q(23195)+TAU,'Actual global cap unchanged')
            add(capkey,Q(1));vector,rhs=combine_endpoints(endpoint,weights,m.cols,budget)
            coeff={j:a for j,a in enumerate(vector) if a};need(set(coeff)<=U,'Full original column cancellation')
            alpha=cap-rhs;union_value=alpha+sum((a*fixed[j] for j,a in coeff.items()),Q(0));gap=union_value-cap
            need(union_value==unrat(summary['necessary_fossil_energy_floor']) and gap==unrat(summary['floor_minus_cap']) and gap>0,'Inherited rejection exact')
            control_value=alpha+sum((a*control[mapping[j]] for j,a in coeff.items()),Q(0));slack=cap-control_value
            need(slack>=0,'Hard failure: accepted continuous control violates derived cut')
            negative=[j for j,a in coeff.items() if a<0];bad=[j for j in negative if fixed[j]!=1]
            monotone=not bad
            endpoints=[dict(kind=k[0],index=k[1],side=k[2],multiplier=rat(w)) for k,w in sorted(weights.items()) if w]
            output=dict(world=world,status='VERIFIED_GLOBAL_EXPANDED_AFFINE_NECESSARY_CUT',alpha=rat(alpha),coefficients=sparse(coeff),cap=rat(cap),
                equivalent_upper_rhs=rat(rhs),endpoint_multipliers=endpoints,hourly_selected_proof=hour_records,
                complete_original_columns_checked=m.cols,all_nonU_coefficients_exact_zero=True,all_endpoint_multipliers_nonnegative=True,
                union_value=rat(union_value),union_violation=rat(gap),continuous_control_value=rat(control_value),continuous_control_slack=rat(slack),
                control_unrounded=True,old_full_point_membership_replayed=False,all_componentwise_binary_supersets_rejected=monotone,
                monotonicity_negative_columns=negative,monotonicity_failed_negative_zero_columns=bad,
                support=dict(U_coefficients=len(coeff),positive_U_coefficients=sum(a>0 for a in coeff.values()),negative_U_coefficients=len(negative),
                    row_endpoints=sum(k[0]=='row' for k,w in weights.items() if w),box_endpoints=sum(k[0]=='box' for k,w in weights.items() if w),
                    unique_rows=len({k[1] for k,w in weights.items() if w and k[0]=='row'}),U_hours=len({(j-6888)//24 for j in coeff}),
                    selected_hours=168,unmerged_selected_endpoint_uses=sum(len(h['terms']) for h in hour_records)+1,global_cap_dependencies=1),
                tau=rat(TAU),new_derived_row_expansion=0,unrestricted_common_verdict='UNKNOWN',no_binary_feasibility_claim=True)
            save(RUN/(world+'_cut.json'),output);outputs.append(dict(world=world,status=output['status'],path=str(RUN/(world+'_cut.json')),sha256=sha(RUN/(world+'_cut.json')),
                union_violation=rat(gap),continuous_control_slack=rat(slack),binary_superset_corollary=monotone,support=output['support']))
        budget();check_bindings(items);check_bindings(transport)
        cuts=[read(RUN/(w+'_cut.json')) for w in WORLDS]
        equal=all(cuts[0][k]==cuts[1][k] for k in ('alpha','coefficients','cap'))
        save(RUN/'outcomes.json',dict(cases=outputs,denominator=2,both_cuts_identical=equal,optimizer_calls=0,selection_changes=0,
            unrestricted_common_verdict='UNKNOWN',claims='necessary affine cuts and conditional binary-superset exclusion only'))
        elapsed=time.perf_counter()-began
        save(RUN/'completion.json',dict(utc=utc(),status='CLOSED_PENDING_INDEPENDENT_REVIEW',elapsed_seconds=elapsed,soft_overrun_seconds=max(0,elapsed-BUDGET),
            all_inputs_unchanged=True,cases=2,completed=len(outputs),optimizer_calls=0,final_completion_write_outside_sample=True))
        print(json.dumps(dict(completed=len(outputs),identical=equal,elapsed_seconds=elapsed)))
    except BaseException as exc:
        save(RUN/'failure.json',dict(utc=utc(),type=type(exc).__name__,message=str(exc),current_world=current,completed=outputs,denominator=2,
            remaining=[w for w in WORLDS if w not in {o['world'] for o in outputs}],no_retry=True,optimizer_calls=0,unrestricted_common_verdict='UNKNOWN'))
        raise

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--prepare-only',action='store_true');g.add_argument('--run-prepared',action='store_true');p.add_argument('--expected-freeze-sha256');a=p.parse_args()
    if a.prepare_only:prepare()
    else:need(a.expected_freeze_sha256 is not None,'External freeze required');run(a.expected_freeze_sha256)
