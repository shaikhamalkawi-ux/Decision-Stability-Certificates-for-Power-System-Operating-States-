"""Exact two-cut evaluation audit after zero-call rejection; no producer import."""
from pathlib import Path
from fractions import Fraction as Q
from datetime import datetime,timezone
import hashlib,json,math,time
ROOT=Path(__file__).resolve().parents[3]
ARM=ROOT/'results/research_next/repaired_crossworld_schema2';PRE=ARM/'prepared';RUN=ARM/'run01'
FREEZE='6e4565d510fceec0308f97ccf59aeaf41ec787252abd39ba29fad204cda89bcd'
MANIFEST='6948d3d9a4b292273f07297a10a65d7574d208cfe6bcce013eb9bca52868dee4'
PREP_REVIEW='6dbd77c9c81d2965c64f5563db6cd32db4aa453d00492b4c75798b13e7328b61'
def need(ok,msg):
    if not ok:raise AssertionError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def rat(q):return dict(numerator=str(q.numerator),denominator=str(q.denominator),approximate=float(q))
def exact(r):
    q=Q(int(r['numerator']),int(r['denominator']));need(r==rat(q),'Canonical exact fraction');return q
def check(items):
    for i in items:
        p=Path(i['path']);need(p.stat().st_size==i['bytes'] and sha(p)==i['sha256'],str(p))
def main():
    start=time.perf_counter();need(sha(PRE/'prepared_freeze.json')==FREEZE and sha(PRE/'input_manifest.json')==MANIFEST,'Prepared anchors')
    need(sha(ARM/'INDEPENDENT_PREPARED_REVIEW.json')==PREP_REVIEW,'Closed schedule/proof admission')
    freeze=read(PRE/'prepared_freeze.json');items=read(PRE/'input_manifest.json')['files'];need(len(items)==179,'Inputs denominator');check(items)
    snapshot={p.name:sha(p) for p in RUN.iterdir() if p.is_file()}
    need(set(snapshot)=={'completion.json','cut_gate.json','execution_started.json','private_log_receipt.json','result.json','stage_timings.json'},'Exact zero-call result layout')
    schedule=read(PRE/'fixed_schedule.json');fixed={v['column']:Q(float.fromhex(v['value_hex'])) for v in schedule['fixed_columns']}
    need(len(fixed)==len(schedule['fixed_columns'])==12096 and set(fixed)==set(range(6888,18984)) and all(v in (0,1) for v in fixed.values()),'Same full admitted schedule')
    gates=read(RUN/'cut_gate.json');need(gates['optimizer_calls']==0 and gates['no_reselection'] and len(gates['evaluations'])==2,'Two fixed gate records')
    independent=[]
    pins={'identity':'8ba409f8702486dcdebc7611a98609696348c41d46af8fa38d7e77b5614621cb',
          'days_321':'7fe192f2acd9ebd1e14eeecde3ece0e3d5d24ede8408e6047b1cb9dd597f30dd'}
    for world,saved in zip(('identity','days_321'),gates['evaluations']):
        path=PRE/(world+'_cut.json');need(sha(path)==pins[world],'Closed global cut')
        cut=read(path);need(cut['world']==world and cut['status']=='VERIFIED_GLOBAL_EXPANDED_AFFINE_NECESSARY_CUT','Cut identity')
        need(exact(cut['tau'])==Q.from_float(1e-5) and cut['new_derived_row_expansion']==0,'No extra tau')
        cap=exact(cut['cap']);need(cap==Q(23195)+Q.from_float(1e-5),'Original expanded cap')
        columns=[v['column'] for v in cut['coefficients']]
        need(len(columns)==len(set(columns))==82 and all(6888<=j<10920 for j in columns),'Original U-only support')
        products=[exact(e['coefficient'])*fixed[e['column']] for e in cut['coefficients']]
        value=exact(cut['alpha'])+sum(products,Q(0));excess=value-cap
        outcome=dict(world=world,value=rat(value),cap=rat(cap),excess=rat(excess),strictly_violated=excess>0)
        need(outcome==saved,'Exact archived cut evaluation '+world);independent.append(outcome)
    need(independent[1]['strictly_violated'] is False,'Days321 consistency gate takes precedence')
    need(independent[0]['strictly_violated'] is True,'Identity rejects exactly the prescribed candidate')
    result=read(RUN/'result.json');done=read(RUN/'completion.json');launch=read(RUN/'execution_started.json');stages=read(RUN/'stage_timings.json')['stages']
    need(launch['freeze_sha256']==FREEZE and launch['maximum_optimizer_calls']==1 and launch['cut_gate_count']==2,'Sole launch scope')
    need(result['verdict']=='REJECTED_REPAIRED_SCHEDULE_ON_IDENTITY_BY_EXISTING_CUT' and result['original_common_question']=='UNKNOWN','Result scope')
    need(result['candidate_exact_negative'] and not result['accepted_common_witness'] and not result['full_problem_negative_claim'],'Restricted versus unrestricted distinction')
    need(done['status']=='CLOSED_PENDING_INDEPENDENT_REVIEW' and done['call_ledger']=={'attempted':0,'returned':0} and done['optimizer_calls']==0,'No attempted solver')
    need(done['candidates']==1 and done['no_retry_or_ray'] and done['all_inputs_unchanged'] and not done['nominal_feasibility_claim'],'Completion scope')
    need(0<=done['phase_seconds']<=done['phase_limit_seconds']==240 and done['soft_phase_overrun_seconds']==0,'Phase accounting')
    need([x['stage'] for x in stages]==['prepared_archive_validated','two_fixed_cut_evaluations','final_hash_revalidation'],'No backend construction/call stage')
    need(all(math.isclose(s['elapsed_seconds']+s['remaining_seconds'],240,rel_tol=0,abs_tol=1e-8) for s in stages),'Stage remaining')
    need(all(stages[i]['elapsed_seconds']<stages[i+1]['elapsed_seconds'] for i in range(len(stages)-1)) and stages[-1]['elapsed_seconds']<=done['phase_seconds'],'Ordered completion')
    need(read(RUN/'private_log_receipt.json')['files']==[],'No solver log')
    need(not (ROOT/'.work/researchnext_repaired_crossworld_schema2/run01').exists(),'Backend private directory never created')
    check(items);need(snapshot=={p.name:sha(p) for p in RUN.iterdir() if p.is_file()},'Producer files unchanged')
    need(sha(PRE/'prepared_freeze.json')==FREEZE and sha(PRE/'input_manifest.json')==MANIFEST,'Transports unchanged')
    report=dict(status='PASS_INDEPENDENT_REPAIRED_CROSSWORLD_EXACT_CUT_REJECTION',utc=datetime.now(timezone.utc).isoformat(),
      reviewer_source_sha256=sha(__file__),freeze_sha256=FREEZE,manifest_sha256=MANIFEST,prepared_review_sha256=PREP_REVIEW,
      inputs_rehashed_twice=179,producer_snapshot=snapshot,evaluations=independent,prescribed_binary_states=12096,
      exact_global_cut_proof_reused=True,new_cut_or_multiplier=False,days321_consistency_pass=True,identity_repaired_schedule_rejected=True,
      original_common_question='UNKNOWN',full_unrestricted_negative=False,producer_phase_seconds=done['phase_seconds'],
      optimizer_calls=0,solver_imports=0,producer_imports=0,full_old_point_replays=0,
      elapsed_seconds=time.perf_counter()-start)
    with (ARM/'INDEPENDENT_POSTRUN_REVIEW.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
    print(report['status'],report['elapsed_seconds'])
if __name__=='__main__':main()
