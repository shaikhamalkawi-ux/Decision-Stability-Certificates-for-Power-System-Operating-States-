"""Independent exact endpoint summation; reuse only the pinned stdlib array decoder."""
import argparse
from collections import defaultdict
import csv
from datetime import datetime,timezone
from fractions import Fraction as F
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import time
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
ARM=ROOT/'results/research_next/union_affine_cut_schema2';PRE=ARM/'prepared';RUN=ARM/'run01'
KERNEL=ROOT/'src/research8h_standalone_verify.py'
PIN={
 'source':'03f02661cbe33757d1ee7a9255a144b643b2cb541c986785f8eeeb7038b92ff6',
 'protocol':'83380d167530d8b040fe353cb9a91af058e150f5b3cf00629bab787fc0deefaa',
 'freeze':'30a47bf54cdceb32e82836ab6bb5cf77de01c695f46e91aa243c799446d1a8c2',
 'manifest':'65235741d7860d9e99b0650c45ac209ba38ac028b758e4f12f1505ad2800f53c',
 'kernel':'708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f',
}
TAU=F.from_float(1e-5);WORLDS=('identity','days_321');U=set(range(6888,10920))
def need(ok,message):
    if not ok:raise AssertionError(message)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def fraction(x):
    n=int(x['numerator']);d=int(x['denominator']);need(d>0,'Positive rational denominator');q=F(n,d)
    need(q.numerator==n and q.denominator==d,'Canonical rational')
    if 'approximate' in x:need(x['approximate']==float(q),'Rational display mismatch')
    return q
def rat(q):return dict(numerator=str(q.numerator),denominator=str(q.denominator),approximate=float(q))
def check_desc(x):
    p=Path(x['path']);need(p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],'Changed input '+str(p))
def row(m,r):return {m.indices[k]:F(m.data[k]) for k in range(m.indptr[r],m.indptr[r+1])}
def upper(m,key):
    kind,index,side=key;need(side in ('lower','upper'),'Endpoint side')
    if kind=='row':
        need(0<=index<m.rows,'Row coordinate');q=row(m,index);bound=(m.row_upper if side=='upper' else m.row_lower)[index]
    else:
        need(kind=='box' and 0<=index<m.cols,'Box coordinate');q={index:F(1)};bound=(m.upper if side=='upper' else m.lower)[index]
    need(math.isfinite(bound),'Finite endpoint');sign=1 if side=='upper' else -1
    return {j:sign*a for j,a in q.items()},sign*F(bound)+TAU
def add(vec,q,w):
    for j,a in q.items():vec[j]+=w*a
def termkey(x):return (x['kind'],x['index'],x['side'])
def nonzero(v):return {j:a for j,a in enumerate(v) if a}
def decoder():
    need(sha(KERNEL)==PIN['kernel'],'Pinned decoder hash')
    s=importlib.util.spec_from_file_location('affine_independent_array_decoder',KERNEL);v=importlib.util.module_from_spec(s)
    sys.modules[s.name]=v;s.loader.exec_module(v);return v
def main(args):
    started=time.perf_counter();need(not (ARM/'independent_postrun_review.json').exists(),'One completed independent replay only')
    refs={'source':ROOT/'src/researchnext_union_affine_cut_schema2.py','protocol':ROOT/'docs/research_next/UNION_AFFINE_CUT_SCHEMA2_PROTOCOL.md',
          'freeze':PRE/'prepared_freeze.json','manifest':PRE/'input_manifest.json','kernel':KERNEL}
    for k,p in refs.items():need(sha(p)==PIN[k],'Trusted input '+k)
    need(sha(RUN/'outcomes.json')==args.outcomes_sha and sha(RUN/'completion.json')==args.completion_sha,'Trusted closed outputs')
    inv=ARM/'producer_output_inventory.csv';need(sha(inv)==args.inventory_sha,'Trusted producer inventory')
    with inv.open(encoding='utf-8-sig',newline='') as f:inventory=list(csv.DictReader(f))
    outs=[]
    for x in inventory:
        p=Path(x['path']);p=p if p.is_absolute() else ROOT/p;p=p.resolve()
        need(p.is_relative_to(ARM.resolve()),'Public producer inventory scope')
        outs.append(dict(path=str(p),bytes=int(x['bytes']),sha256=x['sha256']))
    need(len({x['path'].casefold() for x in outs})==len(outs),'Unique output descriptors')
    inputs=read(PRE/'input_manifest.json')['files'];need(len(inputs)==73,'Frozen input denominator')
    for x in inputs+outs:check_desc(x)
    completion=read(RUN/'completion.json');outcomes=read(RUN/'outcomes.json')
    need(completion['status']=='CLOSED_PENDING_INDEPENDENT_REVIEW' and completion['completed']==completion['cases']==2,'Completed two-case ledger')
    need(completion['optimizer_calls']==outcomes['optimizer_calls']==outcomes['selection_changes']==0,'No calls or changed selection')
    need(completion['all_inputs_unchanged'] is True and outcomes['denominator']==2 and outcomes['unrestricted_common_verdict']=='UNKNOWN','Closure scope')
    need(not (RUN/'failure.json').exists(),'Completed replay has producer failure')
    marker=read(RUN/'execution_started.json');need(marker['freeze_sha256']==PIN['freeze'] and marker['optimizer_calls']==0,'Execution marker')
    need(completion['soft_overrun_seconds']==max(0,completion['elapsed_seconds']-120),'Soft runtime accounting')
    v=decoder();models=[v.load_model(PRE/w) for w in WORLDS]
    fixed={x['column']:F(x['value']) for x in read(PRE/'candidate_schedule.json')['fixed_columns']}
    need(set(fixed)==set(range(6888,18984)) and all(x in (0,1) for x in fixed.values()),'Exact complete union bits')
    point=v.vector(v.read_npz(PRE/'continuous_control.npz',('vector','row_value','row_dual','col_dual'))['vector'],('<f8',),33936,'saved unrounded LP vector')
    need(all(math.isfinite(x) for x in point),'Finite control');point=tuple(F(x) for x in point)
    maps=read(PRE/'joint/column_maps.json');need(maps['worlds']==list(WORLDS),'World ordering')
    oldfloor=read(PRE/'floor_result.json');need(fraction(oldfloor['tau'])==TAU,'Original tau')
    reports=[];algebra=[]
    for wi,w in enumerate(WORLDS):
        m=models[wi];need((m.rows,m.cols)==(34681,23016),'Original dimensions')
        bits=v.vector(v.read_npz(PRE/w/'integrality.npz',('integrality',))['integrality'],('|u1',),m.cols,'original mask')
        need(tuple(bits)==tuple(int(6888<=j<18984) for j in range(m.cols)),'Full original binary mask')
        mapping=maps['original_to_joint'][wi];need(len(mapping)==23016 and all(mapping[j]==j for j in fixed),'Same shared-state projection')
        meta=read(PRE/w/'model_metadata.json');fi={meta['unit_names'].index(n) for n in meta['fossil_units']}
        need(len(fi)==23 and len(meta['unit_names'])==41,'Fossil roster')
        d=read(PRE/w/'derivations.json');cut=read(RUN/(w+'_cut.json'));old=oldfloor['worlds'][wi]
        need(cut['world']==old['world']==w and cut['status']=='VERIFIED_GLOBAL_EXPANDED_AFFINE_NECESSARY_CUT','Cut identity/status')
        need(len(cut['hourly_selected_proof'])==len(d['hourly'])==168,'All hours retained')
        # Recreate only the already frozen selections; no maximum/source search.
        expected=defaultdict(F);hour_counts=[]
        for t,h in enumerate(d['hourly']):
            need(h['hour']==t,'Old hour order');record=cut['hourly_selected_proof'][t]
            need(record['hour']==t and record['active']==h['active'],'Frozen hourly branch')
            terms=[]
            if h['active']=='individual_lower_sum':selected=[(41*t+j,True) for j in sorted(fi)]
            else:
                need(h['active']=='balance_minus_other_upper','Recognized frozen branch')
                key=('row',h['aggregate_row'],'lower');q,r=upper(m,key)
                need(q=={41*t+j:F(-1) for j in range(41)},'Actual aggregate roster')
                terms.append((key,F(1)));selected=[(41*t+j,False) for j in range(41) if j not in fi]
            for j,lower in selected:
                item=d['variables'][j];need(item['column']==j,'Selected generation record')
                origin=item[('lower' if lower else 'upper')+'_source']
                key=('row',origin['row'],origin['side']) if 'row' in origin else ('box',origin['box'],origin['side'])
                q,r=upper(m,key);need(set(q)-{j}<=U,'Actual singleton U-only support')
                a=q.get(j,F(0));need(a<0 if lower else a>0,'Required endpoint orientation');weight=F(1)/abs(a)
                nv=sum((weight*c*fixed[k] for k,c in q.items() if k!=j),F(0));bound=nv-weight*r if lower else weight*r-nv
                need(bound==fraction(item['lower' if lower else 'upper']),'Selected original bound at fixed union')
                terms.append((key,weight))
            got=[(termkey(x),fraction(x['multiplier'])) for x in record['terms']];need(got==terms,'Unchanged full endpoint selection and normalization')
            qh=defaultdict(F);rh=F(0)
            for key,weight in terms:
                need(weight>0,'Positive endpoint multiplier');q,r=upper(m,key);expected[key]+=weight;add(qh,q,weight);rh+=weight*r
            qh={j:a for j,a in qh.items() if a}
            need({j:a for j,a in qh.items() if j<6888}=={41*t+j:F(-1) for j in fi},'Exact full hourly generation cancellation')
            need(set(qh)-{41*t+j for j in fi}<=U,'No unwanted hourly columns')
            value=-rh+sum((a*fixed[j] for j,a in qh.items() if j in U),F(0))
            need(value==fraction(h['selected_floor'])==fraction(record['union_selected_floor']),'Exact inherited hourly value')
            hour_counts.append(len(terms))
        capkey=('row',old['cap_row'],'upper');cq,cap=upper(m,capkey)
        need(cq=={41*t+j:F(1) for t in range(168) for j in fi} and cap==F(23195)+TAU,'Full original cap endpoint')
        expected[capkey]+=1;claimed={}
        for x in cut['endpoint_multipliers']:
            key=termkey(x);need(key not in claimed,'Duplicate combined endpoint');claimed[key]=fraction(x['multiplier']);need(claimed[key]>0,'Nonpositive multiplier')
        need(dict(expected)==claimed,'Complete aggregate endpoint weights match fixed selections')
        vec=[F(0)]*m.cols;rhs=F(0)
        for key,weight in claimed.items():
            q,r=upper(m,key);add(vec,q,weight);rhs+=weight*r
        coeff=nonzero(vec);need(set(coeff)<=U,'Complete non-U cancellation')
        archived={x['column']:fraction(x['coefficient']) for x in cut['coefficients']}
        need(len(archived)==len(cut['coefficients']) and list(archived)==sorted(archived) and archived==coeff,'Every exact coefficient')
        alpha=cap-rhs;need(fraction(cut['equivalent_upper_rhs'])==rhs and fraction(cut['alpha'])==alpha and fraction(cut['cap'])==cap,'Exact constant/RHS/cap')
        union=alpha+sum((a*fixed[j] for j,a in coeff.items()),F(0));gap=union-cap
        cv=alpha+sum((a*point[mapping[j]] for j,a in coeff.items()),F(0));slack=cap-cv
        need(union==fraction(cut['union_value'])==fraction(old['necessary_fossil_energy_floor']),'Union floor')
        need(gap==fraction(cut['union_violation'])==fraction(old['floor_minus_cap']) and gap>0,'Union violation')
        need(cv==fraction(cut['continuous_control_value']) and slack==fraction(cut['continuous_control_slack']) and slack>=0,'Unrounded continuous control')
        neg=[j for j in sorted(coeff) if coeff[j]<0];bad=[j for j in neg if fixed[j]!=1];corollary=not bad
        need(cut['monotonicity_negative_columns']==neg and cut['monotonicity_failed_negative_zero_columns']==bad and cut['all_componentwise_binary_supersets_rejected']==corollary,'Conditional exact binary superset condition')
        support=dict(U_coefficients=len(coeff),positive_U_coefficients=sum(a>0 for a in coeff.values()),negative_U_coefficients=len(neg),
            row_endpoints=sum(k[0]=='row' for k in claimed),box_endpoints=sum(k[0]=='box' for k in claimed),
            unique_rows=len({k[1] for k in claimed if k[0]=='row'}),U_hours=len({(j-6888)//24 for j in coeff}),
            selected_hours=168,unmerged_selected_endpoint_uses=sum(hour_counts)+1,global_cap_dependencies=1)
        need(cut['support']==support and cut['complete_original_columns_checked']==23016,'Proof-support accounting')
        need(cut['control_unrounded'] and not cut['old_full_point_membership_replayed'] and cut['new_derived_row_expansion']==0 and fraction(cut['tau'])==TAU,'Scope/tau flags')
        case=outcomes['cases'][wi];need(case['world']==w and case['sha256']==sha(RUN/(w+'_cut.json')) and case['support']==support,'Outcome artifact binding')
        need(fraction(case['union_violation'])==gap and fraction(case['continuous_control_slack'])==slack and case['binary_superset_corollary']==corollary,'Outcome scalar agreement')
        reports.append(dict(world=w,complete_columns=23016,union_violation=rat(gap),continuous_control_slack=rat(slack),binary_superset_corollary=corollary,support=support))
        algebra.append((alpha,coeff,cap))
    identical=algebra[0]==algebra[1];need(outcomes['both_cuts_identical']==identical,'Two-cut equality report')
    for x in inputs+outs:check_desc(x)
    for k,p in refs.items():need(sha(p)==PIN[k],'Final trusted source/transport')
    need(sha(inv)==args.inventory_sha and sha(RUN/'outcomes.json')==args.outcomes_sha and sha(RUN/'completion.json')==args.completion_sha,'Closed reports unchanged')
    report=dict(status='PASS_INDEPENDENT_EXACT_AFFINE_REPLAY',utc=datetime.now(timezone.utc).isoformat(),reviewer_source_sha256=sha(__file__),trusted_inputs=PIN,
        trusted_outputs=dict(outcomes=args.outcomes_sha,completion=args.completion_sha,inventory=args.inventory_sha),inputs_checked_twice=len(inputs),outputs_checked_twice=len(outs),
        denominator=2,cases=reports,both_cuts_identical=identical,optimizer_calls=0,producer_imports=0,producer_helper_reused=False,
        pinned_array_decoder_reused=True,source_reselection=0,old_full_point_membership_replays=0,continuous_point_rounded=False,
        unrestricted_common_verdict='UNKNOWN',elapsed_seconds=time.perf_counter()-started,producer_elapsed_seconds=completion['elapsed_seconds'],producer_soft_overrun_seconds=completion['soft_overrun_seconds'])
    with (ARM/'independent_postrun_review.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps(report),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--outcomes-sha',required=True);p.add_argument('--completion-sha',required=True);p.add_argument('--inventory-sha',required=True);main(p.parse_args())
