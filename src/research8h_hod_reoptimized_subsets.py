"""Four fixed HOD subset LPs; distinct prepare/run gates, no retries or MIPs."""
from __future__ import annotations
import argparse,csv,json,math,shutil,sys,time
from collections import Counter
from datetime import datetime,timezone
from fractions import Fraction as Q
from pathlib import Path
sys.dont_write_bytecode=True
import research8h_hod_fixed_ray_transfer as f
v=f.v
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'results/research8h/hod_fixed_ray_transfer'
HOD=ROOT/'results/research8h/hour_of_day'
OUT=ROOT/'results/research8h/hod_reoptimized_subsets'
PROTOCOL=ROOT/'docs/research8h/HOD_REOPTIMIZED_SUBSET_PROTOCOL.md'
SCHEDULE=tuple((case,rule) for case in ('seed_26093200','seed_26093201') for rule in ('two_cc','locality48'))
CONTROLS=('january_identity','seed_26100200')
OLD_MANIFEST='3753fdcd4bb9d4f04c45f538631f019e54ff17d5c834266d0807a1353b89366a'
HOD_MANIFEST='078082667f83322d3540ad3ac215ebcc996d0d31b04fd52bfa75c1d2fd814fcc'
KERNEL_SHA='708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'
RULE_SOURCE_SHA='a8138ee89545d25e4f35e6f52cfcb49ec697b7467ce0c5c71f911fbed80207e4'
TAU=Q.from_float(1e-5);PHASE=300.;GUARD=35.;LIMIT=30.
CUTOFF=datetime(2026,9,27,4,0,0,tzinfo=timezone.utc)
FILES=(*f.MODEL_FILES,'retained_parent_rows.npz')
def save(p,x):f.save(p,x)
def read(p):return f.read(p)
def name(case,rule):return case+'__'+rule
def fraction(x):return Q(int(x['numerator']),int(x['denominator']))
def check_manifest(path,expected):
    assert v.sha(path)==expected
    records=read(path);assert isinstance(records,list) and records
    assert len({x['path'] for x in records})==len(records)
    f.manifest(records);return len(records)
def verify_subset(parent,archived,rule):
    full,labels,meta,mask=f.full(parent);expected,expected_labels,keep=f.subset(full,labels,rule)
    actual=v.load_model(archived);actual_labels=f.labels(archived/'row_metadata.csv.gz')
    assert actual==expected and f.arr(archived/'retained_parent_rows.npz','rows')==keep
    assert f.arr(archived/'integrality.npz','integrality')==mask
    assert len(actual_labels)==len(expected_labels)
    for i,(x,y) in enumerate(zip(actual_labels,expected_labels)):
        assert f.key(x)==f.key(y) and int(x['row'])==i and int(x['original_row'])==y['original_row']
    f.columns_match(meta,read(archived/'model_metadata.json'))
    return actual,actual_labels,keep,mask

def prepare():
    assert not OUT.exists()
    assert v.sha(ROOT/'src/research8h_standalone_verify.py')==KERNEL_SHA
    assert v.sha(ROOT/'src/research8h_hod_fixed_ray_transfer.py')==RULE_SOURCE_SHA
    check_manifest(OLD/'input_manifest.json',OLD_MANIFEST)
    v.manifest_check(HOD/'input_manifest.csv',expected=HOD_MANIFEST)
    old=read(OLD/'summary.json');audit=read(OLD/'root_independent_review.json')
    assert old['target_candidate_checks']==6 and old['expanded_rejections']==0 and old['optimizer_calls']==0
    assert audit['status']=='PASS_COMPLETE' and len(audit['candidate_replays'])==6
    assert all(x['status']=='VALID_NONSEPARATING_RAY' for x in audit['candidate_replays'])
    prior=read(HOD/'independent_postrun_review.json');assert prior['status']=='INDEPENDENT_HOD_POSTRUN_PASS'
    OUT.mkdir(parents=True,exist_ok=False)
    save(OUT/'preparation_started.json',dict(utc=datetime.now(timezone.utc).isoformat(),source_sha256=v.sha(Path(__file__)),protocol_sha256=v.sha(PROTOCOL),optimizer_calls=0))
    paths=[Path(__file__),PROTOCOL,ROOT/'docs/research8h/HOD_REOPTIMIZED_SUBSET_DESIGN.md',ROOT/'src/research8h_hod_fixed_ray_transfer.py',ROOT/'src/research8h_standalone_verify.py',OLD/'input_manifest.json',OLD/'prepared_freeze.json',OLD/'summary.json',OLD/'root_independent_review.json',OLD/'positive_control_inheritance.json',HOD/'input_manifest.csv',HOD/'independent_postrun_review.json']
    # Include all original bindings, preserving the six earlier nulls and source rules.
    paths.extend(Path(x['path']) for x in read(OLD/'input_manifest.json'))
    for sub in (OLD/'candidates').iterdir():paths.extend(p for p in sub.iterdir() if p.is_file())
    records=[]
    for case,rule in SCHEDULE:
        parent=HOD/case;source=OLD/'models'/case/rule
        m,labels,keep,mask=verify_subset(parent,source,rule)
        d=OUT/name(case,rule);d.mkdir()
        for item in FILES:shutil.copyfile(source/item,d/item);assert v.sha(source/item)==v.sha(d/item);paths.append(source/item)
        assert v.load_model(d)==m
        caps=[r for r,x in enumerate(labels) if x['family']=='fossil_energy_cap'];assert len(caps)==1
        cap=caps[0];assert m.row_lower[cap]==-math.inf and m.row_upper[cap]==23195.
        record=dict(id=name(case,rule),case=case,rule=rule,source_directory=str(source.resolve()),rows=m.rows,columns=m.cols,retained_family_counts=dict(Counter(x['family'] for x in labels)),cap_row=cap,full_static_background_retained=True,all_column_bounds_unchanged=True,original_binary_columns=sum(mask),continuous_LP_mask_only=True)
        save(d/'model_binding.json',record);records.append(record)
    control_records=[]
    inherited=read(OLD/'positive_control_inheritance.json')['controls']
    for case in CONTROLS:
        parent=HOD/case;m,labels,meta,mask=f.full(parent)
        evidence=next(x for x in prior['positive_controls'] if x['case']==case)
        assert evidence['full_expanded_pass'] and evidence['original_binary_coordinates']==12096
        paths.extend(parent/item for item in (*f.MODEL_FILES,'constructive_vector.npz'))
        for rule in ('two_cc','locality48'):
            sm,sl,keep=f.subset(m,labels,rule)
            before=next(x for x in inherited if x['case']==case and x['rule']==rule)
            assert before['expanded_binary_feasibility_inherited'] and not before['strict_positive_claim']
            assert before['original_point_sha256']==v.sha(parent/'constructive_vector.npz') and before['source_matrix_sha256']==v.sha(parent/'matrix.npz') and before['source_bounds_sha256']==v.sha(parent/'bounds.npz')
            oldmap=OLD/f'control_{case}_{rule}_rows.csv'
            with oldmap.open(newline='') as stream:lines=list(csv.DictReader(stream))
            assert [(int(x['subset_row']),int(x['parent_row'])) for x in lines]==list(enumerate(keep))
            assert sm.lower==m.lower and sm.upper==m.upper
            dest=OUT/f'control_{case}_{rule}_rows.csv';shutil.copyfile(oldmap,dest);paths.append(oldmap)
            control_records.append(dict(case=case,rule=rule,rows=len(keep),inherited_exact_expanded_binary=True,strict_positive_claim=False,point_sha256=v.sha(parent/'constructive_vector.npz'),original_full_model_matrix_sha256=v.sha(parent/'matrix.npz'),all_columns_boxes_unchanged=True,full_point_replayed_again=False))
    assert len(control_records)==4
    save(OUT/'positive_controls.json',dict(controls=control_records,full_control_denominator=2,control_rule_denominator=4,optimizer_calls=0))
    save(OUT/'prepared_cases.json',records)
    save(OUT/'prior_nulls_retained.json',dict(source_summary_sha256=v.sha(OLD/'summary.json'),source_review_sha256=v.sha(OLD/'root_independent_review.json'),candidate_denominator=6,negative_certificates=0,all_six_preserved=True,new_question='Feasibility of four unchanged row restrictions; fixed-ray failure does not decide it.'))
    paths.extend(p for p in OUT.rglob('*') if p.is_file())
    bindings=[dict(path=str(p.resolve()),sha256=v.sha(p),bytes=p.stat().st_size) for p in dict.fromkeys(paths)]
    save(OUT/'input_manifest.json',bindings);f.manifest(bindings)
    save(OUT/'prepared_freeze.json',dict(utc=datetime.now(timezone.utc).isoformat(),source_sha256=v.sha(Path(__file__)),protocol_sha256=v.sha(PROTOCOL),manifest_sha256=v.sha(OUT/'input_manifest.json'),bindings=len(bindings),schedule=[name(*x) for x in SCHEDULE],maximum_LP_calls=4,LP_seconds=LIMIT,phase_seconds=PHASE,actual_call_guard_seconds=GUARD,last_start_deadline=CUTOFF.isoformat(),optimizer_calls=0,requires_independent_prepared_PASS_and_root_execution_GO=True))
    print(json.dumps(dict(event='PREPARED_ZERO_OPTIMIZERS',bindings=len(bindings),manifest_sha256=v.sha(OUT/'input_manifest.json'))),flush=True)

def direct_energy_bound(m,labels,ray,ray_report):
    caps=[r for r,x in enumerate(labels) if x['family']=='fossil_energy_cap'];assert len(caps)==1;cap=caps[0]
    weight=ray.get(cap,Q(0))
    if weight>=0:return dict(status='NOT_AVAILABLE_NONNEGATIVE_CAP_MULTIPLIER',cap_row=cap)
    scale=-weight;cost=[Q(0)]*m.cols
    for j,x in f.row(m,cap).items():cost[j]=Q(x)
    residual=cost.copy();beta=norm=Q(0);normalized=[]
    for r,d in ray.items():
        if r==cap:continue
        d=d/scale;endpoint=m.row_lower[r] if d>0 else m.row_upper[r];assert math.isfinite(endpoint)
        beta+=d*Q(endpoint);norm+=abs(d);normalized.append(dict(original_subset_row=r,**v.rat(d)))
        for e in range(m.indptr[r],m.indptr[r+1]):residual[m.indices[e]]-=d*Q(m.data[e])
    box=sum((q*Q(m.lower[j] if q>=0 else m.upper[j]) for j,q in enumerate(residual)),Q(0));qnorm=sum(map(abs,residual),Q(0));nominal=beta+box
    expanded=nominal-TAU*(norm+qnorm)
    widened=beta-TAU*norm+sum((q*(Q(m.lower[j])-TAU if q>=0 else Q(m.upper[j])+TAU) for j,q in enumerate(residual)),Q(0))
    assert expanded==widened
    relation=Q(m.row_upper[cap])+TAU+fraction(ray_report['expanded_separation_gap'])/scale
    assert expanded==relation and expanded>Q(m.row_upper[cap])+TAU
    return dict(status='EXACT_RESTRICTED_UNCAPPED_ENERGY_LOWER_BOUND',excluded_cap_row=cap,normalization=v.rat(scale),nominal_lower_MWh=v.rat(nominal),expanded_lower_MWh=v.rat(expanded),expanded_cap_threshold_MWh=v.rat(Q(m.row_upper[cap])+TAU),positive_margin_MWh=v.rat(expanded-Q(m.row_upper[cap])-TAU),normalized_signed_multipliers=normalized,exact_residual=[dict(column=j,**v.rat(q)) for j,q in enumerate(residual) if q],row_term=v.rat(beta),finite_box_term=v.rat(box),row_l1=v.rat(norm),residual_l1=v.rat(qnorm),direct_widened_identity=True,ray_normalization_identity=True,finite_upper_not_established=True)

def support(labels,ray,keep):
    entries=[]
    for r,d in sorted(ray.items()):
        x=labels[r];entries.append(dict(subset_row=r,parent_row=keep[r],family=x['family'],hour_0based=int(x['hour_0based']),uid=x['uid'],value_hex=float(d).hex()))
    return dict(nonzero_entries=entries,nonzero_family_counts=dict(Counter(x['family'] for x in entries)),retained_family_counts=dict(Counter(x['family'] for x in labels)),temporal_generator_uids=sorted({x['uid'] for x in entries if x['family'] in f.TEMPORAL}),dwell_generator_hours=[dict(uid=uid,hours_0based=sorted({x['hour_0based'] for x in entries if x['uid']==uid and x['family'] in f.DWELL})) for uid in sorted({x['uid'] for x in entries if x['family'] in f.DWELL})],scope='Sufficient restricted explanation on complete static/network/cap background; not IIS, necessity, minimum support or raw information.')

def solve_one(case,rule,phase):
    # Imports occur only in separately authorized execution mode.
    import highspy
    import numpy as np
    d=OUT/name(case,rule);m=v.load_model(d);labels=f.labels(d/'row_metadata.csv.gz');keep=f.arr(d/'retained_parent_rows.npz','rows')
    solver=highspy.Highs();lp=highspy.HighsLp();lp.num_row_,lp.num_col_=m.rows,m.cols
    lp.col_cost_=np.zeros(m.cols);lp.col_lower_=np.array(m.lower);lp.col_upper_=np.array(m.upper)
    lp.row_lower_=np.array(m.row_lower);lp.row_upper_=np.array(m.row_upper)
    lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise;lp.a_matrix_.num_row_,lp.a_matrix_.num_col_=m.rows,m.cols
    lp.a_matrix_.start_=np.array(m.indptr,dtype=np.int32);lp.a_matrix_.index_=np.array(m.indices,dtype=np.int32);lp.a_matrix_.value_=np.array(m.data)
    options=dict(time_limit=LIMIT,threads=1,random_seed=0,solver='simplex',presolve='off',log_to_console=False,log_file=str(d/'solver.log'))
    for key,value in options.items():assert solver.setOptionValue(key,value)==highspy.HighsStatus.kOk
    assert solver.passModel(lp)==highspy.HighsStatus.kOk
    now=datetime.now(timezone.utc);phase_left=PHASE-(time.perf_counter()-phase);utc_left=(CUTOFF-now).total_seconds()
    admitted=min(phase_left,utc_left)>=GUARD
    decision=dict(id=name(case,rule),utc=now.isoformat(),phase_remaining_s=phase_left,cutoff_remaining_s=utc_left,guard_s=GUARD,admitted=admitted)
    save(d/'launch_decision.json',decision)
    result=dict(id=name(case,rule),case=case,rule=rule,verdict='UNKNOWN',optimization_calls=0,elapsed_s=0.,options=options,original_binary_model_not_solved=True)
    if not admitted:
        result['reason']='NOT_RUN_CUTOFF' if utc_left<GUARD else 'NOT_RUN_PHASE';save(d/'result.json',result);return result
    # Final admission is deliberately after the decision-file write; keep it in
    # memory until the call/skip returns so another slow write cannot stale it.
    recheck_now=datetime.now(timezone.utc);recheck_phase_left=PHASE-(time.perf_counter()-phase);recheck_utc_left=(CUTOFF-recheck_now).total_seconds()
    recheck_admitted=min(recheck_phase_left,recheck_utc_left)>=GUARD
    result['actual_call_recheck']=dict(utc=recheck_now.isoformat(),phase_remaining_s=recheck_phase_left,cutoff_remaining_s=recheck_utc_left,guard_s=GUARD,admitted=recheck_admitted)
    if not recheck_admitted:
        result['reason']='NOT_RUN_RECHECK_CUTOFF' if recheck_utc_left<GUARD else 'NOT_RUN_RECHECK_PHASE';save(d/'result.json',result);return result
    start=time.perf_counter();result['started_utc']=recheck_now.isoformat();status=solver.run();elapsed=time.perf_counter()-start
    result.update(optimization_calls=1,elapsed_s=elapsed,ended_utc=datetime.now(timezone.utc).isoformat(),run_status=str(status),model_status=solver.modelStatusToString(solver.getModelStatus()),solver_version=solver.version(),soft_limit_overrun_s=max(0.,elapsed-LIMIT))
    solution=solver.getSolution();result['solution_value_valid']=bool(solution.value_valid)
    if solution.value_valid:
        vector=tuple(map(float,solution.col_value));f.npz(d/'returned_vector.npz',dict(vector=('<f8',(len(vector),),vector)))
        if len(vector)==m.cols and all(map(math.isfinite,vector)):
            point=v.check_point(m,vector,(0,)*m.cols,TAU);save(d/'exact_continuous_point.json',point)
            result['exact_expanded_continuous_pass']=point['expanded_pass'];result['exact_strict_continuous_pass']=point['strict_pass']
            if point['expanded_pass']:result['verdict']='VERIFIED_EXPANDED_CONTINUOUS_POINT'
        else:result['invalid_returned_vector']=True
    if solver.getModelStatus()==highspy.HighsModelStatus.kInfeasible:
        exists_status,exists=solver.getDualRayExist();result.update(dual_ray_exist_status=str(exists_status),dual_ray_already_exists=bool(exists),ray_recovery_solves=0)
        if exists_status==highspy.HighsStatus.kOk and exists:
            rstatus,rexists,returned=solver.getDualRay();result.update(dual_ray_status=str(rstatus),dual_ray_retrieved=bool(rexists))
            if rstatus==highspy.HighsStatus.kOk and rexists:
                raw=tuple(map(float,returned));f.npz(d/'raw_solver_ray.npz',dict(multipliers=('<f8',(len(raw),),raw)))
                if len(raw)==m.rows and all(map(math.isfinite,raw)):
                    sparse={r:Q(x) for r,x in enumerate(raw) if x}
                    forbidden=[r for r,x in sparse.items() if not math.isfinite(m.row_lower[r] if x>0 else m.row_upper[r])]
                    candidates=(('raw',sparse),('explicit_endpoint_sign_projection',{r:x for r,x in sparse.items() if r not in set(forbidden)}))
                    checks=[];accepted=None
                    for kind,ray in candidates:
                        try:check=v.check_ray(m,ray,TAU)
                        except v.InvalidInput as error:check=dict(status='INVALID_CANDIDATE',reason=str(error),expanded_pass=False)
                        checks.append(dict(kind=kind,forbidden_raw_rows=forbidden,verification=check))
                        if check['expanded_pass'] and accepted is None:accepted=(kind,ray,check)
                    save(d/'ray_candidate_checks.json',checks)
                    if accepted is not None:
                        assert result['verdict']!='VERIFIED_EXPANDED_CONTINUOUS_POINT','Contradictory exact point and ray'
                        kind,ray,check=accepted;cert=dict(kind=kind,multipliers=[dict(row=r,value_hex=float(x).hex()) for r,x in sorted(ray.items())],verification=check,model_artifacts={fn:v.sha(d/fn) for fn in ('matrix.npz','bounds.npz')},row_metadata_sha256=v.sha(d/'row_metadata.csv.gz'),raw_solver_ray_sha256=v.sha(d/'raw_solver_ray.npz'),experiment_manifest_sha256=v.sha(OUT/'input_manifest.json'))
                        save(d/'dual_certificate.json',cert);save(d/'support.json',support(labels,ray,keep));save(d/'restricted_energy_lower_bound.json',direct_energy_bound(m,labels,ray,check))
                        result.update(verdict='CERTIFIED_EXPANDED_INFEASIBLE',selected_candidate=kind,exact_expanded_gap=check['expanded_separation_gap'])
                else:result['invalid_returned_ray']=True
    save(d/'result.json',result);return result

def run_prepared():
    phase=time.perf_counter();invocation=datetime.now(timezone.utc)
    freeze=read(OUT/'prepared_freeze.json');assert freeze['schedule']==[name(*x) for x in SCHEDULE]
    assert v.sha(Path(__file__))==freeze['source_sha256'] and v.sha(PROTOCOL)==freeze['protocol_sha256']
    bindings=check_manifest(OUT/'input_manifest.json',freeze['manifest_sha256'])
    save(OUT/'execution_started.json',dict(utc=invocation.isoformat(),validated_utc=datetime.now(timezone.utc).isoformat(),phase_started_before_validation=True,bindings=bindings,maximum_LP_calls=4,phase_seconds=PHASE,last_start_deadline=CUTOFF.isoformat()))
    outcomes=[]
    for case,rule in SCHEDULE:
        result=solve_one(case,rule,phase);outcomes.append(result)
        print(json.dumps(dict(id=result['id'],verdict=result['verdict'],seconds=result['elapsed_s'])),flush=True)
    save(OUT/'outcomes.json',outcomes);check_manifest(OUT/'input_manifest.json',freeze['manifest_sha256'])
    end=datetime.now(timezone.utc);elapsed=time.perf_counter()-phase
    save(OUT/'completion.json',dict(utc=end.isoformat(),case_rule_denominator=4,ordinary_target_denominator=2,positive_control_rule_denominator=4,optimization_calls=sum(x['optimization_calls'] for x in outcomes),actual_solver_seconds=sum(x['elapsed_s'] for x in outcomes),solver_soft_overrun_s=sum(max(0.,x['elapsed_s']-LIMIT) for x in outcomes),phase_elapsed_s=elapsed,phase_soft_overrun_s=max(0.,elapsed-PHASE),UTC_cutoff_overrun_s=max(0.,(end-CUTOFF).total_seconds()),all_frozen_hashes_unchanged=True,prior_six_nulls_unchanged=True,independent_postrun_review_required=True))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prepare-only',action='store_true');mode.add_argument('--run-prepared',action='store_true');args=parser.parse_args()
    if args.prepare_only:prepare()
    else:run_prepared()
