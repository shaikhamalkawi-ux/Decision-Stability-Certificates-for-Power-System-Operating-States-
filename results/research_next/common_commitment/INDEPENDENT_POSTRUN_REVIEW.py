"""One closed-null ledger audit plus post-hoc exact unrounded continuous point check."""
import csv
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import time

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
ARM=ROOT/'results/research_next/common_commitment'
PRE=ARM/'prepared';RUN=ARM/'run01'
OUT=ARM/'INDEPENDENT_POSTRUN_REVIEW.json'
STATE=ARM/'INDEPENDENT_LP_NONBINARY_STATES.json'
PINS={
 'prepared/prepared_freeze.json':'4f21891d7d1f1793dd92e5b830edf5b5cf62474e5521d788c9aec17929ea9a59',
 'prepared/input_manifest.json':'8ff99b1f4450ac15e91b26a261a85c98d574bbbdac3f7fe149efd9fd07204a5c',
 'INDEPENDENT_PREPARED_REVIEW.py':'41f75d9254349021b4d5086064a76cffc830c9b99a7198c768d7587d3d65378e',
 'INDEPENDENT_PREPARED_REVIEW.json':'956b37cbcdd49571a6a79611da197a5be840a5c2747ffbd60576c90805d58e6b',
 'run01/completion.json':'f1933f3029955eaf7256206228c272060c8c48df69fff91af7baa06ce2a4f9d7',
 'run01/outcomes.json':'0e85f3d65e5375f384b0a1015178de4babb03b5ebd5392ee0c6f759e6c43776c',
 'READOUT.md':'ba7740b7039f54c8b1c1197628bf3edd39ab5053f10b071795fa6727458bee40',
 'producer_output_inventory.csv':'06bba03dc70aa221695ad82d717c975fd25946fbb9cf931371b4c8442f54eea6',
}
SOURCE='039af59750b4c165d877b9878ac14af02a202700b46739ba96a8914075ae3284'
PROTOCOL='08838becbd0d679f6131421c566534f19c93f535e7baa3b4b00d30b985ccab21'
KERNEL_SHA='708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'
TAU=Q.from_float(1e-5)

def require(t,m):
    if not t:raise AssertionError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def rat(q):return {'numerator':str(q.numerator),'denominator':str(q.denominator),'approximate':float(q)}
def dt(t):return datetime.fromisoformat(t)
def save(p,obj):
    with p.open('x',encoding='utf-8') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')

def main():
    start=time.monotonic();own=sha(__file__)
    require(not OUT.exists() and not STATE.exists(),'Fresh independent output only')
    for rel,digest in PINS.items():require(sha(ARM/rel)==digest,'Trusted closed binding '+rel)
    bindings=read(PRE/'input_manifest.json')['files']
    require(len(bindings)==48 and len({r['path'].casefold() for r in bindings})==48,'48 unique inputs')
    with (ARM/'producer_output_inventory.csv').open(encoding='utf-8-sig',newline='') as f:outputs=list(csv.DictReader(f))
    require(len(outputs)==16 and len({r['path'] for r in outputs})==16,'16 unique producer files')
    def rehash():
        for r in bindings:
            p=Path(r['path']);require(p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],'Changed prepared input')
        for r in outputs:
            p=ROOT/r['path'];require(p.stat().st_size==int(r['bytes']) and sha(p)==r['sha256'],'Changed producer output')
        expected={str((ROOT/r['path']).resolve()) for r in outputs if r['path'].startswith('results/research_next/common_commitment/run01/')}
        require({str(p.resolve()) for p in RUN.rglob('*') if p.is_file()}==expected and len(expected)==15,'Complete producer run inventory')
        for rel,digest in PINS.items():require(sha(ARM/rel)==digest,'Changed transport/review pin')
    rehash()
    require(sha(ROOT/'src/researchnext_common_commitment.py')==SOURCE and sha(ROOT/'docs/research_next/COMMON_COMMITMENT_PROTOCOL.md')==PROTOCOL,'Final producer source/protocol')
    inherited=read(ARM/'INDEPENDENT_PREPARED_REVIEW.json')
    require(inherited['status']=='PASS_INDEPENDENT_PREPARED_REVIEW' and inherited['saved_rows_independently_checked']==69362 and inherited['saved_coefficients_independently_checked']==291176,'Inherited full transport proof')
    plan=read(PRE/'plan.json');completion=read(RUN/'completion.json');outcomes=read(RUN/'outcomes.json');marker=read(RUN/'execution_started.json')
    require(outcomes['pair_denominator']==1 and outcomes['planned_calls']==2 and outcomes['selection']=='posthoc unique first-week joint observation collision','Posthoc fixed denominator')
    require(completion['status']=='CLOSED_PENDING_INDEPENDENT_REVIEW' and completion['optimizer_calls']==2,'Closed run')
    require(completion['all_frozen_bytes_unchanged'] and completion['no_individual_world_solves'] and completion['no_retries'] and not completion['nominal_feasibility_claim'],'Producer scope')
    ledger=completion['call_ledger'];calls=ledger['calls']
    require(ledger['attempted']==ledger['returned']==2 and [r['kind'] for r in calls]==['mip','lp'],'Exactly two declared attempted/returned calls')
    require(marker['source_sha256']==SOURCE and marker['expected_freeze_sha256']==PINS['prepared/prepared_freeze.json'] and marker['phase_seconds']==1200,'Execution provenance')
    require(plan['sequence']==['mip','lp'] and plan['phase_seconds']==1200,'Plan order/phase')
    results=[];timing=[]
    previous=dt(marker['utc'])
    for position,(kind,limit) in enumerate((('mip',600.0),('lp',60.0))):
        folder=RUN/kind;r=read(folder/'result.json');returned=read(folder/'solver_returned.json')
        require(outcomes['outcomes'][position]==r,'Outcome/result identity')
        require(all(r[k]==value for k,value in returned.items()),'Returned/final record consistency')
        require(r['kind']==kind and r['verdict']=='UNKNOWN' and r['calls_started']==1 and not r['accepted_common_witness'] and not r['accepted_joint_negative'],'Historical UNKNOWN preserved')
        require(r['options']=={**plan['options'][kind],'log_to_console':False,'log_file':str((folder/'solver.log').resolve())},'Exact call options')
        require(r['options']['time_limit']==limit and r['solver_version']=='1.12.0','Solver/limit identity')
        c=calls[position];admission=read(folder/'admission.json');ready=read(folder/'call_ready.json')
        require(c['attempted'] and c['returned'] and c['elapsed_seconds']==r['actual_seconds'],'Attempt ledger matches durations')
        require(previous<=dt(admission['utc'])<=dt(ready['utc'])<=dt(c['started_utc'])<=dt(c['ended_utc']),'Call chronological order')
        previous=dt(c['ended_utc'])
        require(admission['admitted'] and admission['required_seconds']==limit+5 and admission['remaining_seconds']>=admission['required_seconds'],'Initial call admission')
        require(ready['not_an_assertion_of_actual_call'],'Ready receipt distinguished from call')
        require(r['soft_overrun_seconds']==max(0.0,r['actual_seconds']-limit),'Actual overrun retained')
        log=(folder/'solver.log').read_text(encoding='utf-8-sig')
        require('HiGHS 1.12.0' in log and '69362 rows' in log and '33936 cols' in log and '291176 nonzeros' in log,'Actual solver model shape in log')
        if kind=='mip':
            require(r['model_status']=='Time limit reached' and not r['value_valid'] and r['mip_node_count']==0,'No MIP incumbent')
            require('Time limit reached' in log and 'Primal bound      inf' in log,'MIP log agrees')
        else:
            require(r['model_status']=='Optimal' and r['value_valid'] and not r['dual_ray_already_exists'] and r['ray_recovery_solves']==0,'LP/no-ray status')
            require(r['dual_ray_exist_status']=='HighsStatus.kOk' and 'Model status        : Optimal' in log,'LP return/log agreement')
        results.append(r)
        timing.append({'kind':kind,'actual_monotonic_seconds':r['actual_seconds'],'reported_utc_interval_seconds':(dt(c['ended_utc'])-dt(c['started_utc'])).total_seconds(),'soft_overrun_seconds':r['soft_overrun_seconds'],'initial_admission_remaining_seconds':admission['remaining_seconds']})
    require(previous<=dt(completion['utc']) and ledger['current']==calls[-1],'Closed final ledger')
    require(completion['phase_soft_overrun']==max(0.0,completion['phase_seconds']-1200) and completion['phase_seconds']>=sum(r['actual_seconds'] for r in results),'Soft phase accounting')
    require(not any('candidate' in p.name or 'ray' in p.name or p.name.endswith('_vector.npz') for p in RUN.rglob('*') if p.is_file()),'No promoted candidate or returned ray')
    kernel_path=ROOT/'src/research8h_standalone_verify.py';require(sha(kernel_path)==KERNEL_SHA,'Pinned NPZ parser')
    spec=importlib.util.spec_from_file_location('common_closed_npz_reader',kernel_path);v=importlib.util.module_from_spec(spec);sys.modules[spec.name]=v;spec.loader.exec_module(v)
    model=v.load_model(PRE/'joint')
    require((model.rows,model.cols,len(model.data))==(69362,33936,291176),'Frozen joint dimension')
    original_mask=v.vector(v.read_npz(PRE/'joint/integrality.npz',('integrality',))['integrality'],('|u1',),model.cols,'full joint mask')
    require(original_mask==tuple(int(6888<=j<18984) for j in range(33936)),'Original full12096 mask')
    raw=v.read_npz(RUN/'lp/raw_solution.npz',('vector','row_value','row_dual','col_dual'))
    values=v.vector(raw['vector'],('<f8',),model.cols,'LP point')
    require(all(math.isfinite(x) for x in values),'Finite full LP vector')
    point=tuple(Q(x) for x in values)
    # Independent Fraction loop: do not call producer checker or round/alter the LP point.
    max_col=max_row=Q(0);worst_col=worst_row=None;strict_col=strict_row=expanded_col=expanded_row=0
    for j,x in enumerate(point):
        for side,gap in (('lower',Q(model.lower[j])-x),('upper',x-Q(model.upper[j]))):
            if gap>0:strict_col+=1
            if gap>TAU:expanded_col+=1
            if gap>max_col:max_col=gap;worst_col={'column':j,'side':side}
    for r in range(model.rows):
        activity=sum((Q(model.data[e])*point[model.indices[e]] for e in range(model.indptr[r],model.indptr[r+1])),Q(0))
        for side,bound in (('lower',model.row_lower[r]),('upper',model.row_upper[r])):
            if not math.isfinite(bound):continue
            gap=Q(bound)-activity if side=='lower' else activity-Q(bound)
            if gap>0:strict_row+=1
            if gap>TAU:expanded_row+=1
            if gap>max_row:max_row=gap;worst_row={'row':r,'side':side}
    expanded=max_col<=TAU and max_row<=TAU;strict=max_col<=0 and max_row<=0
    names=read(PRE/'identity/model_metadata.json')['thermal_unit_names']
    by_block={block:{'exact_zero':0,'exact_one':0,'exact_nonbinary':0,'strictly_between_zero_and_one':0,'outside_zero_one_interval':0,'farther_than_tau_from_either_bit':0} for block in ('U','Y','Z')}
    state_records=[]
    for block,base in (('U',6888),('Y',10920),('Z',14952)):
        for offset in range(4032):
            j=base+offset;x=point[j];counts=by_block[block]
            if x==0:counts['exact_zero']+=1
            elif x==1:counts['exact_one']+=1
            else:
                counts['exact_nonbinary']+=1
                counts['strictly_between_zero_and_one' if 0<x<1 else 'outside_zero_one_interval']+=1
                distance=min(abs(x),abs(x-1))
                counts['farther_than_tau_from_either_bit']+=int(distance>TAU)
                state_records.append({'joint_column':j,'block':block,'hour_0based':offset//24,'thermal_index':offset%24,'uid':names[offset%24],
                    'binary64_hex':values[j].hex(),'exact_value':rat(x),'distance_to_nearest_bit':rat(distance)})
    counts={key:sum(c[key] for c in by_block.values()) for key in next(iter(by_block.values()))}
    require(counts['exact_zero']+counts['exact_one']+counts['exact_nonbinary']==12096 and counts['exact_nonbinary']==len(state_records),'Complete binary-coordinate census')
    require(counts['exact_nonbinary']>0,'Continuous point must not be promoted to common binary witness')
    fraction_file={'scope':'Post-hoc exact census of the saved unrounded LP vector; original binary domains are relaxed only for continuous membership.',
        'raw_solution_sha256':sha(RUN/'lp/raw_solution.npz'),'original_binary_coordinates':12096,'tau':rat(TAU),'counts':counts,'by_block':by_block,'all_exact_nonbinary_coordinates':state_records}
    point_result={'status':'VERIFIED_EXPANDED_CONTINUOUS_POINT' if expanded else 'CONTINUOUS_POINT_NOT_VERIFIED','posthoc':True,
        'strict_pass':strict,'expanded_pass':expanded,'integrality_relaxed':True,'original_binary_coordinates':12096,'enforced_binary_coordinates':0,
        'rows_checked':model.rows,'columns_checked':model.cols,'coefficients_used':len(model.data),'tau':rat(TAU),
        'maximum_column_violation':rat(max_col),'worst_column':worst_col,'maximum_row_violation':rat(max_row),'worst_row':worst_row,
        'strict_violated_row_sides':strict_row,'strict_violated_column_sides':strict_col,'expanded_violated_row_sides':expanded_row,'expanded_violated_column_sides':expanded_col,
        'state_counts':counts,'state_counts_by_block':by_block,'point_changed_or_rounded':False,
        'implication':'The same expanded joint continuous rows/box admit this point, so no valid Farkas certificate can reject that unchanged relaxation. This does not establish a common binary commitment.' if expanded else 'No additional continuous membership conclusion.'}
    rehash();require(sha(__file__)==own,'Review source stable')
    require(not any(n in sys.modules for n in ('numpy','scipy','highspy','researchnext_common_commitment')),'No producer/scientific imports')
    save(STATE,fraction_file)
    report={'status':'PASS_INDEPENDENT_POSTRUN_REVIEW','utc':datetime.now(timezone.utc).isoformat(),'review_source_sha256':own,
        'producer_source_sha256':SOURCE,'protocol_sha256':PROTOCOL,'trusted_pins':PINS,'input_bindings_checked_twice':48,'closed_output_bindings_checked_twice':16,
        'inherited_prepared_row_transport':{'report_sha256':PINS['INDEPENDENT_PREPARED_REVIEW.json'],'rows':69362,'coefficients':291176,'recomputed_this_turn':False},
        'pair_binary_verdict':'UNKNOWN','accepted_common_binary_witnesses':0,'returned_rays':0,'ray_candidates':0,'actual_call_ledger':timing,
        'actual_total_optimizer_seconds':sum(r['actual_seconds'] for r in results),'phase_seconds':completion['phase_seconds'],'phase_soft_overrun':completion['phase_soft_overrun'],
        'timing_scope':'Monotonic actual durations and separately recorded UTC intervals have distinct sampling points; no invented exact equality or hard-limit claim.',
        'posthoc_continuous_check':point_result,'nonbinary_state_file':{'path':str(STATE),'sha256':sha(STATE),'bytes':STATE.stat().st_size},
        'optimizer_calls_by_reviewer':0,'producer_imports':0,'model_generation':0,'native_witness_replays':0,'old_witness_or_ray_replays':0,
        'elapsed_seconds':time.monotonic()-start}
    save(OUT,report)
    print(json.dumps({'status':report['status'],'report_sha256':sha(OUT),'continuous_status':point_result['status'],'strict_pass':strict,
        'counts':counts,'row_violation':rat(max_row),'column_violation':rat(max_col),'elapsed_seconds':report['elapsed_seconds']}))

if __name__=='__main__':main()
