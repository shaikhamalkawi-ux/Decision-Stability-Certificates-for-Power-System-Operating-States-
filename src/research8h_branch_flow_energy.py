"""Prospective strict uncapped energy follow-up; explicit prepare/run gates."""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
import gzip
import importlib.util
import json
import math
from pathlib import Path
import shutil
import sys
import time

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import research8h_branch_flow as b
import research8h_branch_flow_energy_check as checker

ROOT=b.ROOT; OUT=ROOT/'results/research8h/branch_flow_strict_energy'; PARENT=b.OUT
OLD=ROOT/'results/research8h/hour_of_day_uncapped'
PROTOCOL=ROOT/'docs/research8h/BRANCH_FLOW_STRICT_ENERGY_PROTOCOL.md'
DESIGN=ROOT/'docs/research8h/BRANCH_FLOW_STRICT_ENERGY_DESIGN.md'
TEST_REPORT=ROOT/'results/research8h/branch_flow_energy_implementation_tests.json'
CASES=('january_identity','seed_26093200','seed_26093201'); TARGETS=CASES[1:]
CALLS=(*CASES,*(x+'_proposal' for x in TARGETS))
PHASE=1800.; MATH_PHASE=900.; CUTOFF=b.CUTOFF; LATEST_START=datetime(2026,9,27,3,35,tzinfo=timezone.utc)
a=b.arithmetic; require=b.require; save=b.save; sha=b.sha; rat=b.rat; parse=b.parse_rat


def gate():
    require(sha(Path(b.__file__))=='bb5889f57ef051dffb196457b3bfbb9626e8c2e046a2b0bcc13ea6b5250fbd77','Parent source changed')
    require(sha(Path(b.variant.__file__))=='41dab33ed8e013d46fd7ae78974d95cab70e9794a906a7c6a12786bb093d4632','Parent checker changed')
    return b.helper_gate()


def lower_bound(model,cost,dual):
    require(len(cost)==model.cols and len(dual)==model.rows,'Objective/dual shape')
    require(all(math.isfinite(x) for x in (*cost,*dual,*model.lower,*model.upper)),'Nonfinite cost/dual/box')
    r=list(map(Q,cost)); beta=Q(0)
    for i,value in enumerate(dual):
        if not value: continue
        endpoint=model.row_lower[i] if value>0 else model.row_upper[i]
        require(math.isfinite(endpoint),'Selected infinite row endpoint')
        weight=Q(value);beta+=weight*Q(endpoint)
        for e in range(model.indptr[i],model.indptr[i+1]): r[model.indices[e]]-=weight*Q(model.data[e])
    box=sum((value*Q(model.lower[j] if value>=0 else model.upper[j]) for j,value in enumerate(r)),Q(0))
    return dict(tau=0,lower_bound=rat(beta+box),row_term=rat(beta),box_term=rat(box)),r


def delete_cap(v,case):
    source=PARENT/case;model=v.load_model(source);labels=b.read_labels(source/'row_metadata.csv.gz')
    meta=v.json_read(source/'model_metadata.json');cost=b.full_objective(meta)
    mask=a.get_vector(v,source/'integrality.npz','integrality',('|u1',),model.cols)
    require(mask==(0,)*6888+(1,)*12096+(0,)*10416,'Full original binary mask')
    require(a.get_vector(v,source/'objective.npz','objective',('<f8',),model.cols)==cost,'Actual fossil objective')
    caps=[i for i,r in enumerate(labels) if r['family']=='fossil_energy_cap'];require(len(caps)==1,'One parent cap')
    cap=caps[0];require(b.terms(model,cap)=={j:Q(x) for j,x in enumerate(cost) if x} and model.row_lower[cap]==-math.inf and model.row_upper[cap]==23195,'Parent cap contents')
    keep=[i for i in range(model.rows) if i!=cap];require(len(keep)==34512,'Only cap deleted')
    newlabels=[{**labels[i],'row':j,'old_row':i} for j,i in enumerate(keep)]
    meta={**meta,'fossil_cap_absent':True,'budget_MWh':None,'cap_row':None,'deleted_parent_cap_row':cap,'parent_model':str(source)}
    b.export_model(OUT/case,[b.terms(model,i) for i in keep],[b.endpoint(model.row_lower[i]) for i in keep],
        [b.endpoint(model.row_upper[i]) for i in keep],list(map(Q,model.lower)),list(map(Q,model.upper)),mask,cost,newlabels,meta)
    for name in ('native_inputs.npz','permutation.csv','graph.json','native_spec.json'):shutil.copyfile(source/name,OUT/case/name)
    save(OUT/case/'cap_deletion.json',dict(parent_rows=keep,deleted_row=cap,parent_bindings=checker.primal.model_bindings(source),only_cap_deleted=True))


def proposal(v,case,fixed):
    model=v.load_model(OUT/case);labels=b.read_labels(OUT/case/'row_metadata.csv.gz');cost=b.full_objective(v.json_read(OUT/case/'model_metadata.json'))
    blocks=[];mapping={};constants=[]
    for t in range(168):
        columns=list(range(t*41,(t+1)*41))+list(range(18984+t*24,18984+(t+1)*24))+list(range(23016+t*38,23016+(t+1)*38))
        mapping.update({j:(t,k) for k,j in enumerate(columns)})
        blocks.append(dict(hour=t,columns=columns,lower=[Q(model.lower[j]) for j in columns],upper=[Q(model.upper[j]) for j in columns],objective=[Q(cost[j]) for j in columns],rows=[]))
    for i,label in enumerate(labels):
        row=b.terms(model,i);shift=sum((value*fixed[j] for j,value in row.items() if j in fixed),Q(0));free={j:value for j,value in row.items() if j not in fixed}
        lo,hi=b.endpoint(model.row_lower[i]),b.endpoint(model.row_upper[i])
        if not free:
            require((lo is None or shift>=lo) and (hi is None or shift<=hi),'Fixed constant row fails')
            constants.append(dict(row=i,activity=rat(shift),lower=a.encode_bound(lo),upper=a.encode_bound(hi)));continue
        hours={mapping[j][0] for j in free};require(len(hours)==1,'Unexpected temporal dispatch coupling');t=next(iter(hours))
        require(t==int(label['hour_0based']),'Hour label')
        blocks[t]['rows'].append(dict(original_row=i,family=label['family'],uid=label['uid'],fixed_shift=shift,terms={mapping[j][1]:value for j,value in free.items()},lower=None if lo is None else lo-shift,upper=None if hi is None else hi-shift))
    require(len(constants)==16032,'Constant denominator')
    for block in blocks: require(Counter(r['family'] for r in block['rows'])==Counter(thermal_upper=24,thermal_lower=24,nodal_flow_incidence=24,flow_definition=38),'Hourly row families')
    rows=[];low=[];high=[];labels=[]
    for block in blocks:
        for r in block['rows']:
            rows.append({103*block['hour']+j:value for j,value in r['terms'].items()});low.append(r['lower']);high.append(r['upper'])
            labels.append(dict(row=len(labels),family=r['family'],hour_0based=block['hour'],uid=r['uid'],old_row=r['original_row']))
    d=OUT/(case+'_proposal')
    b.export_model(d,rows,low,high,[x for block in blocks for x in block['lower']],[x for block in blocks for x in block['upper']],
        [0]*17304,[float(x) for block in blocks for x in block['objective']],labels,dict(column_order='hour-major P41/theta24/flow38',uncapped=True,fixed_binary_columns=12096))
    with gzip.open(d/'exact_blocks.json.gz','xt',encoding='utf-8') as f:json.dump(a.encoded_blocks(blocks),f,separators=(',',':'))
    save(d/'constant_rows.json',constants)


def prepare():
    require(not OUT.exists(),'New output must be absent');v=gate();start=time.perf_counter()
    require(sha(PARENT/'artifact_manifest.csv')=='a86ee29993a253e7018965cf9ce66dc177e220129eba849a4529960a09e237c4','Closed parent inventory changed')
    import csv
    with (PARENT/'artifact_manifest.csv').open(newline='',encoding='utf-8') as f:parent_records=list(csv.DictReader(f))
    for r in parent_records:
        p=ROOT/r['path'];require(sha(p)==r['sha256'] and p.stat().st_size==int(r['bytes']),'Parent binding changed')
    require(sha(OLD/'input_manifest.csv')=='b0ffca41db74d7278c001c776ae3b8656272994d083c8fc215ecbbf665020f8a','Old uncapped input manifest changed')
    require(sha(OLD/'independent_postrun_review.json')=='6039f8bbf0dd882cf34f9ada87ec251e95d1e48296291591e6b58914c680c832','Closed old schedule review changed')
    old_review=v.json_read(OLD/'independent_postrun_review.json')
    require(old_review['status']=='INDEPENDENT_HOD_UNCAPPED_POSTRUN_PASS','Old schedule review status')
    for rel,h in old_review['input_and_result_hashes'].items():require(sha(ROOT/rel.replace('\\','/'))==h,'Old reviewed input/result changed')
    OUT.mkdir();files=[ROOT/r['path'] for r in parent_records]+[PARENT/'artifact_manifest.csv',OLD/'input_manifest.csv',OLD/'independent_postrun_review.json']
    for case in CASES:delete_cap(v,case)
    fixed_path=PARENT/'fixed_schedule.json';fixed={r['column']:parse(r['value']) for r in v.json_read(fixed_path)}
    save(OUT/CASES[0]/'fixed_schedule.json',v.json_read(fixed_path))
    point=checker.primal.read_point(v,PARENT/CASES[0]/'rational_point.json',PARENT/CASES[0]);b.point_artifact(OUT/CASES[0],point)
    identity=checker.replay(OUT/CASES[0],OUT/CASES[0]/'rational_point.json',OUT/CASES[0]/'fixed_schedule.json');require(identity['accepted_strict_uncapped'],'Inherited identity fails uncapped model')
    save(OUT/CASES[0]/'identity_upper.json',identity)
    for case in TARGETS:
        source=OLD/case;raw=source/'mip/recovered_vector.npz'
        accepted=v.json_read(source/'mip/exact_point_check.json');native_check=v.json_read(source/'mip/native_no_cap_check.json')
        require(accepted['expanded_pass'] and accepted['original_binary_coordinates_exact'] and native_check['pass'],'Inherited schedule did not come from accepted old point')
        require(a.get_vector(v,source/'original_integrality.npz','integrality',('|u1',),23016)==(0,)*6888+(1,)*12096+(0,)*4032,'Old full-mask provenance')
        # The old point is provenance for this fixed schedule only; new membership is never inferred.
        vector=a.get_vector(v,raw,'vector',('<f8',),23016);fixed={j:Q(vector[j]) for j in range(6888,18984)}
        require(all(x in (0,1) for x in fixed.values()),'Nonbinary inherited states')
        oldnative=b.load_native(v,source/'native_inputs.npz');newnative=b.load_native(v,OUT/case/'native_inputs.npz')
        require(all(oldnative[k].shape==newnative[k].shape and oldnative[k].values==newnative[k].values for k in oldnative),'Target native package mismatch')
        require(sha(source/'permutation.csv')==sha(OUT/case/'permutation.csv'),'Target permutation mismatch')
        save(OUT/case/'fixed_schedule.json',[dict(column=j,value=rat(x)) for j,x in fixed.items()]);proposal(v,case,fixed)
        files += [raw,source/'mip/exact_point_check.json',source/'mip/native_no_cap_check.json',source/'native_inputs.npz',source/'permutation.csv',source/'original_integrality.npz']
    save(OUT/'preparation_report.json',dict(cases=CASES,call_order=CALLS,optimizer_calls=0,actual_basis_reconstructions=0,target_hour_denominator=336,elapsed_s=time.perf_counter()-start,identity_strict_uncapped=True))
    files += [Path(__file__),Path(checker.__file__),Path(a.__file__),Path(checker.primal.__file__),checker.primal.KERNEL,PROTOCOL,DESIGN,TEST_REPORT]
    files += sorted(p for p in OUT.rglob('*') if p.is_file())
    records=a.bindings(files);save(OUT/'input_manifest.json',records);a.verify_bindings(records)
    save(OUT/'prepared_freeze.json',dict(manifest_sha256=sha(OUT/'input_manifest.json'),bindings=len(records),calls=CALLS,options=b.OPTIONS,limit_per_call=60,phase=PHASE,arithmetic_phase=MATH_PHASE,latest_start=LATEST_START.isoformat(),cutoff=CUTOFF.isoformat(),separate_GO_required=True))
    print('PREPARED_ONLY '+sha(OUT/'input_manifest.json'),flush=True)


def solve(case,overall,state):
    import highspy
    import numpy as np
    from scipy.sparse import load_npz,csr_matrix,csc_matrix
    d=OUT/case;matrix=load_npz(d/'matrix.npz').tocsr()
    with np.load(d/'bounds.npz',allow_pickle=False) as f:bounds={k:f[k].copy() for k in f.files}
    with np.load(d/'objective.npz',allow_pickle=False) as f:cost=f['objective'].copy()
    h=highspy.Highs();require(h.version()=='1.12.0','Solver version')
    for k,x in {**b.OPTIONS,'time_limit':60.,'log_file':str(d/'solver.log')}.items():require(h.setOptionValue(k,x)==highspy.HighsStatus.kOk,'Rejected '+k)
    lp=highspy.HighsLp();lp.num_col_,lp.num_row_=matrix.shape[1],matrix.shape[0];lp.col_cost_=cost
    lp.col_lower_,lp.col_upper_=bounds['column_lower'],bounds['column_upper'];lp.row_lower_,lp.row_upper_=bounds['row_lower'],bounds['row_upper']
    lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise;lp.a_matrix_.start_,lp.a_matrix_.index_,lp.a_matrix_.value_=matrix.indptr,matrix.indices,matrix.data
    require(h.passModel(lp)==highspy.HighsStatus.kOk,'Rejected model');loaded=h.getLp()
    require(loaded.a_matrix_.format_ in (highspy.MatrixFormat.kRowwise,highspy.MatrixFormat.kColwise),'Loaded matrix format')
    ctor=csr_matrix if loaded.a_matrix_.format_==highspy.MatrixFormat.kRowwise else csc_matrix
    check=ctor((loaded.a_matrix_.value_,loaded.a_matrix_.index_,loaded.a_matrix_.start_),shape=matrix.shape).tocsr();require((check!=matrix).nnz==0,'Loaded coefficients changed')
    for x,y in ((loaded.col_cost_,cost),(loaded.col_lower_,bounds['column_lower']),(loaded.col_upper_,bounds['column_upper']),(loaded.row_lower_,bounds['row_lower']),(loaded.row_upper_,bounds['row_upper'])):require(np.array_equal(x,y),'Loaded endpoints/objective changed')
    def remaining():return min(overall-time.perf_counter(),(CUTOFF-datetime.now(timezone.utc)).total_seconds())
    if remaining()<65:return dict(case=case,status='NOT_STARTED_GUARD',optimizer_calls=0)
    save(d/'launch_decision.json',dict(utc=datetime.now(timezone.utc).isoformat(),remaining_seconds=remaining(),configured_seconds=60))
    if remaining()<65:return dict(case=case,status='NOT_STARTED_AFTER_IO_GUARD',optimizer_calls=0)
    start=time.perf_counter();state.update(optimizer_calls=1,started=start);status=h.run();elapsed=time.perf_counter()-start
    basis=h.getBasis();point=h.getSolution();info=h.getInfo()
    save(d/'basis.json',dict(valid=basis.valid,column_status=[x.name for x in basis.col_status],row_status=[x.name for x in basis.row_status]))
    np.savez_compressed(d/'numerical_point.npz',vector=np.asarray(point.col_value))
    if len(point.row_dual)==matrix.shape[0] and np.isfinite(point.row_dual).all():np.savez_compressed(d/'raw_row_dual.npz',row_dual=np.asarray(point.row_dual))
    record=dict(case=case,status=h.modelStatusToString(h.getModelStatus()),call_status=str(status),optimizer_calls=1,actual_seconds=elapsed,configured_seconds=60,soft_overrun=max(0.,elapsed-60),basis_valid=basis.valid,dual_valid=point.dual_valid,numerical_objective=None if not math.isfinite(info.objective_function_value) else info.objective_function_value)
    save(d/'solver_result.json',record);return record


def bounds(v,case,tick):
    d=OUT/case;m=v.load_model(d);cost=a.get_vector(v,d/'objective.npz','objective',('<f8',),m.cols)
    candidates=[('zero',[0.]*m.rows)];path=d/'raw_row_dual.npz'
    if path.exists():
        raw=a.get_vector(v,path,'row_dual',('<f8',),m.rows)
        for sign in (1,-1):
            values=[sign*x for x in raw];projected=[0. if (x>0 and not math.isfinite(m.row_lower[i])) or (x<0 and not math.isfinite(m.row_upper[i])) else x for i,x in enumerate(values)]
            candidates += [(f'{sign:+d}_raw',values),(f'{sign:+d}_projected',projected)]
    reports=[];selected=None
    for name,dual in candidates:
        tick();record=dict(candidate=name,model_bindings=checker.primal.model_bindings(d),raw_dual_sha256=sha(path) if path.exists() else None,multipliers=[dict(row=i,value_hex=x.hex()) for i,x in enumerate(dual) if x])
        try:
            check,residual=lower_bound(m,cost,dual);record.update(check,valid=True,residual=[dict(column=j,value=rat(x)) for j,x in enumerate(residual) if x])
            if selected is None or parse(check['lower_bound'])>parse(selected['lower_bound']):selected=dict(candidate=name,lower_bound=check['lower_bound'])
        except ValueError as error:record.update(valid=False,reason=str(error))
        save(d/('lower_'+name+'.json'),record);reports.append(dict(candidate=name,valid=record['valid']))
    require(selected is not None and parse(selected['lower_bound'])>=0,'Nonnegative zero-candidate floor')
    result=dict(case=case,selected=selected,candidates=reports,tau=0);save(d/'lower_bound.json',result);return result


def reconstruct(v,case,tick):
    d=OUT/(case+'_proposal');basis=v.json_read(d/'basis.json') if (d/'basis.json').exists() else {}
    with gzip.open(d/'exact_blocks.json.gz','rt',encoding='utf-8') as f:blocks=a.decoded_blocks(json.load(f))
    fixed={r['column']:parse(r['value']) for r in v.json_read(OUT/case/'fixed_schedule.json')};point=[None]*29400
    for j,x in fixed.items():point[j]=x
    valid=basis.get('valid',False) and len(basis.get('column_status',[]))==17304 and len(basis.get('row_status',[]))==18480
    ledger=[];limited=False
    for block in blocks:
        t=block['hour'];r=dict(hour=t)
        if not valid:r['status']='UNRESOLVED_NO_BASIS'
        elif limited:r['status']='NOT_EVALUATED_PHASE_LIMIT'
        else:
            try:
                values,detail=a.reconstruct_hour(block,basis['column_status'][t*103:(t+1)*103],basis['row_status'][t*110:(t+1)*110],tick)
                r.update(detail,status='EXACT_HOUR_POINT' if detail['exact_hour_pass'] else 'UNRESOLVED_CANDIDATE_VIOLATES',values=[dict(column=j,value=rat(x)) for j,x in zip(block['columns'],values)])
                for j,x in zip(block['columns'],values):point[j]=x
            except a.PhaseLimit as error:limited=True;r.update(status='NOT_EVALUATED_PHASE_LIMIT',reason=str(error))
            except Exception as error:r.update(status='UNRESOLVED_RECONSTRUCTION',reason=type(error).__name__+': '+str(error))
        save(d/f'hour_{t:03d}.json',r);ledger.append(dict(hour=t,status=r['status']))
    save(d/'hour_outcomes.json',ledger);result=dict(case=case,status='NO_UPPER',counts=dict(Counter(r['status'] for r in ledger)),hour_denominator=168)
    if all(r['status']=='EXACT_HOUR_POINT' for r in ledger):
        tick();b.point_artifact(OUT/case,point);check=checker.replay(OUT/case,OUT/case/'rational_point.json',OUT/case/'fixed_schedule.json',tick)
        save(OUT/case/'strict_uncapped_point_check.json',check)
        if check['accepted_strict_uncapped']:result.update(status='STRICT_UNCAPPED_UPPER',upper_bound=check['exact_objective'])
    save(OUT/case/'upper_bound.json',result);return result


def run():
    v=gate();require(not (OUT/'execution_marker.json').exists(),'Single execution already attempted')
    freeze=v.json_read(OUT/'prepared_freeze.json');require(sha(OUT/'input_manifest.json')==freeze['manifest_sha256'],'Manifest changed')
    require(freeze['calls']==list(CALLS) and freeze['options']==b.OPTIONS,'Call plan/options changed')
    records=v.json_read(OUT/'input_manifest.json');a.verify_bindings(records)
    now=datetime.now(timezone.utc);require(now<=LATEST_START and (CUTOFF-now).total_seconds()>=1500,'Prospective03:35 start gate expired; leave unexecuted')
    save(OUT/'execution_marker.json',dict(utc=now.isoformat(),manifest_sha256=freeze['manifest_sha256']))
    start=time.perf_counter();overall=start+PHASE;calls=[]
    for case in CALLS:
        state=dict(optimizer_calls=0)
        try:record=solve(case,overall,state)
        except Exception as error:
            record=dict(case=case,status='POSTCALL_ERROR' if state['optimizer_calls'] else 'PRECALL_ERROR',optimizer_calls=state['optimizer_calls'],reason=type(error).__name__+': '+str(error))
            if state['optimizer_calls']:record['actual_seconds']=time.perf_counter()-state['started']
            save(OUT/case/'call_error.json',record)
        calls.append(record)
    save(OUT/'calls.json',calls);math_start=time.perf_counter();tick=b.tick_factory(math_start+MATH_PHASE,overall);low={};upper={CASES[0]:v.json_read(OUT/CASES[0]/'identity_upper.json')['exact_objective']};upper_records=[]
    for case in CASES:
        try:low[case]=bounds(v,case,tick)['selected']['lower_bound']
        except Exception as error:save(OUT/case/'lower_error.json',dict(case=case,status='NO_LOWER',reason=type(error).__name__+': '+str(error)))
    for case in TARGETS:
        try:
            result=reconstruct(v,case,tick);upper_records.append(result)
            if 'upper_bound' in result:upper[case]=result['upper_bound']
        except Exception as error:
            result=dict(case=case,status='NO_UPPER',reason=type(error).__name__+': '+str(error));save(OUT/case/'upper_error.json',result);upper_records.append(result)
    for case in CASES:
        if case in low and case in upper:require(parse(low[case])<=parse(upper[case]),'HARD_REVIEW_STOP: lower exceeds strict upper')
    outcomes=[]
    for case in TARGETS:
        record=dict(case=case,status='INCOMPLETE_BOUNDS',lower=low.get(case),upper=upper.get(case))
        if all(k in low and k in upper for k in (CASES[0],case)):
            li,ui,lt,ut=map(parse,(low[CASES[0]],upper[CASES[0]],low[case],upper[case]));record.update(status='FINITE_STRICT_INTERVAL',penalty_lower=rat(lt-ui),penalty_upper=rat(ut-li),strictly_positive=lt>ui)
            if li>0 and lt>=0:record['percent_interval']=[rat(100*(lt/ui-1)),rat(100*(ut/li-1))]
        outcomes.append(record)
    a.verify_bindings(records);save(OUT/'outcomes.json',dict(target_denominator=2,target_hour_denominator=336,targets=outcomes,upper_records=upper_records,identity_lower=low.get(CASES[0]),identity_upper=upper[CASES[0]],tau=0,distinct_flow_model=True))
    elapsed=time.perf_counter()-start;math_elapsed=time.perf_counter()-math_start
    save(OUT/'completion.json',dict(optimizer_calls=sum(r['optimizer_calls'] for r in calls),maximum_calls=5,actual_solve_seconds=sum(r.get('actual_seconds',0) for r in calls),phase_seconds=elapsed,arithmetic_seconds=math_elapsed,phase_soft_overrun=max(0.,elapsed-PHASE),arithmetic_soft_overrun=max(0.,math_elapsed-MATH_PHASE),independent_review_required=True))
    print(json.dumps(outcomes),flush=True)


def synthetic():
    from types import SimpleNamespace
    m=SimpleNamespace(rows=1,cols=1,lower=(0.,),upper=(10.,),row_lower=(3.,),row_upper=(math.inf,),indptr=(0,1),indices=(0,),data=(1.,))
    r,res=lower_bound(m,(2.,),(1.,));require(parse(r['lower_bound'])==3 and res==[Q(1)],'Residual lower fixture')
    r,res=lower_bound(m,(-1.,),(0.,));require(parse(r['lower_bound'])==-10,'Upper-box sign fixture')
    try:lower_bound(m,(1.,),(-1.,))
    except ValueError:pass
    else:raise ValueError('Infinite endpoint should be rejected')
    return dict(status='SYNTHETIC_ONLY_PASS',tests=3,actual_models_read=0,optimizer_calls=0,source_sha256=sha(Path(__file__)),checker_sha256=sha(Path(checker.__file__)))


def main():
    parser=argparse.ArgumentParser();g=parser.add_mutually_exclusive_group(required=True)
    g.add_argument('--prepare-only',action='store_true');g.add_argument('--run-prepared',action='store_true');g.add_argument('--synthetic-only',action='store_true');parser.add_argument('--report',type=Path);args=parser.parse_args()
    if args.prepare_only:prepare()
    elif args.run_prepared:run()
    else:require(args.report is not None and not args.report.exists(),'New report required');save(args.report,synthetic())


if __name__=='__main__':main()
