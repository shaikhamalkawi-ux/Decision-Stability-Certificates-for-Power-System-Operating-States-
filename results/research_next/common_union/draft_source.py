"""Draft new union source from reviewed I/O/admission text; no model execution."""
from pathlib import Path
import ast,hashlib
ROOT=Path(__file__).resolve().parents[3]
old=ROOT/'src/researchnext_common_gurobi.py'
assert hashlib.sha256(old.read_bytes()).hexdigest()=='9f5515fb99ac43cba3756f1e2b5a9f3a0ad9df7c143860922edd9ae99cd000ec'
s=old.read_text(encoding='utf-8');prefix=s[:s.index('def prepare():')]
prefix=prefix.replace('One separately gated Gurobi search on the original common-commitment model.','One frozen union-closure schedule and fixed-state LP, with full original admission.')
prefix=prefix.replace('common_gurobi','common_union').replace('COMMON_GUROBI','COMMON_UNION')
prefix=prefix.replace("PYTHON = ROOT/'.work/auer_projection_env/Scripts/python.exe'","PYTHON = Path('C:/Users/gmalkawi/OneDrive - Higher Colleges of Technology/Documents 1/ChatGPT/3/.work/solver_env/Scripts/python.exe')")
prefix=prefix.replace('PHASE_SECONDS = 2400.0','PHASE_SECONDS = 240.0')
a=prefix.index('OPTIONS =');b=prefix.index('PINS =',a)
prefix=prefix[:a]+'''OPTIONS = dict(time_limit=60.0,threads=1,random_seed=0,presolve='on',solver='simplex')
PACKAGES = {'numpy':'2.3.5','scipy':'1.18.1','highspy':'1.12.0'}
IDENTITY = ROOT/'results/research8h/hour_of_day/january_identity'
REPAIR = ROOT/'results/research_next/day321_local_repair'
'''+prefix[b:]
prefix='\n'.join(line for line in prefix.split('\n') if "'results/research_next/auer_projection_preflight/" not in line)
pos=prefix.index('\n}\nWORLD_FILES')
prefix=prefix[:pos]+'''
 'results/research8h/hour_of_day/january_identity/constructive_vector.npz':'7c534f8691c761815224ac43773259da5a8e1d3eb2aa892dcb64dc46541672db',
 'results/research8h/hour_of_day/january_identity/constructive_check.json':'4bc4a850eb640021e2566224e0566012be0d7f9ea82b205054b63a11544ae800',
 'results/research8h/hour_of_day/independent_prepared_review.json':'dec49b3358ffbcb1288a8281eb2b3f0f51213c1ab0b7503b3f7baf95c8df542f',
 'results/research_next/day321_local_repair/run01/candidate_vector.npz':'fc9276c52baa182b0eba018df548bb0125290cb2413dd469c1899516c03733c3',
 'results/research_next/day321_local_repair/run01/result.json':'ec7bb3be2d79c5c3b878a7d674da5ca6c625173d07cffa440261018d9f452091',
 'results/research_next/day321_local_repair/INDEPENDENT_POSTRUN_REVIEW.json':'76f3b5121ed7248ee6cd71df61af483408c85a57d15abed6c622a793490bcc49',
 'results/research_next/common_commitment/prepared/plan.json':'0fa3248558e8150c135d22e616f10710017cf0735ed09d96b73c04c35c4c1c83',
 'docs/research_next/COMMON_UNION_CANDIDATE_PROPOSAL.md':'e6bc4ca975aa7e632cb6c1ed0ed7b99d442fb98cd8e7f7825c33be93f0ab8f15',
'''+prefix[pos:]
a=prefix.index('def environment():');b=prefix.index('\ndef row_encoding(',a)
prefix=prefix[:a]+'''def environment():
    require(Path(sys.executable).resolve()==PYTHON.resolve(),'Use pinned existing HiGHS environment')
    versions={n:importlib.metadata.version(n) for n in PACKAGES}
    require(versions==PACKAGES and sys.version_info[:3]==(3,12,14),'Recorded environment differs')
    return dict(python=sys.version,executable=sys.executable,packages=versions,highspy_imported_for_preparation=False)
'''+prefix[b:]
a=prefix.index('def row_encoding(');b=prefix.index('\ndef initial_inputs(',a);prefix=prefix[:a]+prefix[b:]
candidate=s[s.index('def candidate_check('):s.index('\ndef run(',s.index('def candidate_check('))]
candidate=candidate.replace('def candidate_check(v,np,raw,bits):','def candidate_check(v,np,raw,bits,fixed):')
candidate=candidate.replace("        choices=[k for k in (0,1) if abs(Q(float(raw[j]))-k)<=TAU]\n        if len(choices)!=1:return dict(eligible=False,accepted=False)\n        candidate[j]=float(choices[0])","        chosen=fixed[j]\n        if abs(Q(float(raw[j]))-chosen)>TAU:return dict(eligible=False,accepted=False)\n        candidate[j]=float(chosen)")
candidate=candidate.replace('common_gurobi_native_checker','common_union_native_checker')
candidate=candidate.replace('continuous_bytes_unchanged=True,nominal_feasibility_claim=False','continuous_bytes_unchanged=True,prescribed_all12096_bits=True,nominal_feasibility_claim=False')
construction='''def native_residence(u,minimum_up,minimum_down):
    return all(all(u[h]==u[t] for h in range(t,min(len(u),t+(minimum_up if u[t] else minimum_down))))
               for t in range(1,len(u)) if u[t]!=u[t-1])

def union_close(a,b,minimum_down):
    require(len(a)==len(b) and all(x in (0,1) for x in a+b),'Binary input sequence')
    u=[max(x,y) for x,y in zip(a,b)];closed=u.copy();runs=[];t=0
    while t<len(u):
        if u[t]:t+=1;continue
        first=t
        while t<len(u) and not u[t]:t+=1
        fill=first>0 and t<len(u) and t-first<minimum_down
        runs.append(dict(start=first,stop=t,length=t-first,interior=first>0 and t<len(u),filled=fill))
        if fill:closed[first:t]=[1]*(t-first)
    y=[0]+[max(closed[t]-closed[t-1],0) for t in range(1,len(u))]
    z=[0]+[max(closed[t-1]-closed[t],0) for t in range(1,len(u))]
    return u,closed,y,z,runs

def prepare():
    require(not PRE.exists() and not RUN.exists(),'One preparation only')
    runtime=environment();captured=initial_inputs();initial=[x[1] for x in captured.values()];v=kernel()
    import numpy as np
    PRE.mkdir(parents=True)
    save(PRE/'preparation_started.json',dict(utc=utc(),source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),optimizer_calls=0))
    copies=[]
    for folder,names in [('joint',JOINT_FILES),('identity',WORLD_FILES),('days_321',WORLD_FILES)]:
        (PRE/folder).mkdir()
        for name in names:
            src=ORIGINAL/folder/name;data,item=captured[str(src.resolve()).casefold()]
            dest=PRE/folder/name;dest.write_bytes(data);require(sha(dest)==item['sha256'],'Copy mismatch')
            copies.append(dict(original=item,copy=bind(dest)))
    for src,name in [(ORIGINAL/'gen.csv','gen.csv'),(IDENTITY/'constructive_vector.npz','identity_input_vector.npz'),
                     (REPAIR/'run01/candidate_vector.npz','day321_input_vector.npz')]:
        data,item=captured[str(src.resolve()).casefold()];dest=PRE/name;dest.write_bytes(data)
        require(sha(dest)==item['sha256'],'Captured point copy mismatch');copies.append(dict(original=item,copy=bind(dest)))
    proof=read(IDENTITY/'constructive_check.json');require(proof['full_exact']['expanded_pass'] and proof['numerical']['physical']['pass'],'Identity acceptance flag')
    proof=read(ROOT/'results/research8h/hour_of_day/independent_prepared_review.json')
    case=[x for x in proof['cases'] if x['case']=='january_identity'];require(len(case)==1 and case[0]['point_check']['full_expanded_pass'],'Independent identity proof flag')
    proof=read(REPAIR/'INDEPENDENT_POSTRUN_REVIEW.json');require(proof['expanded_pass'] and proof['native_pass'] and proof['candidate_sha256']==sha(PRE/'day321_input_vector.npz'),'Independent target proof binding')
    for name in ('matrix.npz','bounds.npz','integrality.npz','model_metadata.json','native_inputs.npz'):
        require(sha(IDENTITY/name)==sha(PRE/'identity'/name),'Identity proof/model relation')
    m=v.load_model(PRE/'joint');bits=mask(v,PRE/'joint',m.cols)
    require((m.rows,m.cols,len(m.data),sum(bits))==(69362,33936,291176,12096),'Original joint shape')
    require(bits==tuple(int(6888<=j<18984) for j in range(m.cols)),'Complete original state mask')
    metas=[read(PRE/w/'model_metadata.json') for w in ('identity','days_321')]
    specs=[read(PRE/w/'native_spec.json') for w in ('identity','days_321')]
    require(specs[0]==specs[1] and metas[0]['unit_names']==metas[1]['unit_names'] and metas[0]['thermal_unit_names']==metas[1]['thermal_unit_names'],'Native unit semantics differ')
    vectors=[v.vector(v.read_npz(PRE/name,('vector',))['vector'],('<f8',),23016,'verified input vector') for name in ('identity_input_vector.npz','day321_input_vector.npz')]
    require(all(x[j] in (0.,1.) for x in vectors for j in range(6888,18984)),'Input original state bits not exact')
    fixed={};units=[]
    for k,name in enumerate(metas[0]['thermal_unit_names']):
        j=metas[0]['unit_names'].index(name);spec=specs[0][j];up=spec['minimum_up'];down=spec['minimum_down']
        require(type(up) is int and type(down) is int and up>=0 and down>=0,'Native integer dwell')
        a,b=([int(x[6888+24*t+k]) for t in range(168)] for x in vectors)
        require(native_residence(a,up,down) and native_residence(b,up,down),'Input residence premise')
        union,u,y,z,runs=union_close(a,b,down)
        for offset,values in ((6888,u),(10920,y),(14952,z)):
            for t,value in enumerate(values):fixed[offset+24*t+k]=value
        units.append(dict(unit=name,minimum_up=up,minimum_down=down,identity_U=a,day321_U=b,union_U=union,
            closed_U=u,canonical_Y=y,canonical_Z=z,off_runs=runs,closed_residence_pass=native_residence(u,up,down),
            union_additions_vs_identity=sum(x>y for x,y in zip(union,a)),union_additions_vs_day321=sum(x>y for x,y in zip(union,b)),
            closure_added_hours=sum(x>y for x,y in zip(u,union))))
    require(set(fixed)=={j for j,b in enumerate(bits) if b},'Exactly all original state columns fixed')
    issues=[];state_rows=[]
    for j,value in fixed.items():
        if not m.lower[j]<=value<=m.upper[j]:issues.append(dict(column=j,reason='original_binary_box'))
    for i in range(m.rows):
        entries=range(m.indptr[i],m.indptr[i+1])
        if all(bits[m.indices[t]] for t in entries):
            state_rows.append(i);activity=sum((Q(m.data[t])*fixed[m.indices[t]] for t in entries),Q(0))
            if (math.isfinite(m.row_lower[i]) and activity<Q(m.row_lower[i])) or (math.isfinite(m.row_upper[i]) and activity>Q(m.row_upper[i])):
                issues.append(dict(row=i,reason='original_state_only_row'))
    lower=list(m.lower);upper=list(m.upper)
    for j,value in fixed.items():lower[j]=upper[j]=float(value)
    np.savez_compressed(PRE/'fixed_bounds.npz',column_lower=np.array(lower),column_upper=np.array(upper))
    save(PRE/'candidate_schedule.json',dict(units=units,fixed_columns=[dict(column=j,value=fixed[j]) for j in sorted(fixed)],candidate_count=1))
    save(PRE/'candidate_admission.json',dict(admitted=not issues and all(x['closed_residence_pass'] for x in units),
        original_state_only_rows=state_rows,state_rows_checked=len(state_rows),full_original_state_columns=len(fixed),
        issue_count=len(issues),issues=issues,no_continuous_dispatch_evaluated=True,checks='nominal exact state rows/boxes and native residence'))
    save(PRE/'copy_provenance.json',dict(copies=copies))
    save(PRE/'plan.json',dict(options=OPTIONS,phase_seconds=PHASE_SECONDS,start_guard_seconds=65.0,calls=1,candidates=1,
        objective='zero feasibility',all_original_binary_columns_fixed=True,numeric_solver_type='continuous LP with no free integer',
        original_matrix_rows_retained=69362,original_columns_retained=33936,runtime=runtime,
        source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),no_warm_start=True,no_retry=True,no_ray=True))
    validate(initial);items=initial+[bind(p) for p in PRE.rglob('*') if p.is_file()];validate(items)
    save(PRE/'input_manifest.json',dict(files=items));validate(items)
    save(PRE/'prepared_freeze.json',dict(utc=utc(),source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),
        manifest_sha256=sha(PRE/'input_manifest.json'),bindings=len(items),candidate_admitted=read(PRE/'candidate_admission.json')['admitted'],
        optimizer_calls=0,highspy_imports=0,separate_source_prepared_review_and_explicit_GO_required=True))

def load_prepared(expected):
    require(sha(PRE/'prepared_freeze.json')==expected,'External freeze digest')
    freeze=read(PRE/'prepared_freeze.json');require(freeze['source_sha256']==sha(__file__) and freeze['protocol_sha256']==sha(PROTOCOL),'Source/protocol identity')
    require(freeze['manifest_sha256']==sha(PRE/'input_manifest.json'),'Manifest identity')
    bindings=read(PRE/'input_manifest.json')['files'];validate(bindings)
    plan=read(PRE/'plan.json');require(plan['options']==OPTIONS and plan['phase_seconds']==PHASE_SECONDS and plan['runtime']==environment(),'Plan/environment identity')
    v=kernel();m=v.load_model(PRE/'joint');bits=mask(v,PRE/'joint',m.cols)
    schedule=read(PRE/'candidate_schedule.json');fixed={x['column']:x['value'] for x in schedule['fixed_columns']}
    require(len(fixed)==12096 and set(fixed)=={j for j,b in enumerate(bits) if b} and all(x in (0,1) for x in fixed.values()),'Fixed complete binary mask')
    bounds=v.read_npz(PRE/'fixed_bounds.npz',('column_lower','column_upper'))
    lower=v.vector(bounds['column_lower'],('<f8',),m.cols,'fixed lower');upper=v.vector(bounds['column_upper'],('<f8',),m.cols,'fixed upper')
    require(all(lower[j]==upper[j]==fixed[j] if bits[j] else lower[j]==m.lower[j] and upper[j]==m.upper[j] for j in range(m.cols)),'Only complete state box fixing')
    return v,m,bits,fixed,lower,upper,bindings

def build_readback(highspy,np,m,bits,fixed,lower,upper):
    h=highspy.Highs();require(h.version()=='1.12.0','HiGHS version')
    options={**OPTIONS,'log_to_console':False,'log_file':str((PRIVATE/'solver.log').resolve())}
    for key,value in options.items():require(h.setOptionValue(key,value)==highspy.HighsStatus.kOk,'Rejected option')
    lp=highspy.HighsLp();lp.num_row_,lp.num_col_=m.rows,m.cols
    lp.col_cost_=np.zeros(m.cols);lp.col_lower_=np.array(lower);lp.col_upper_=np.array(upper)
    lp.row_lower_=np.array(m.row_lower);lp.row_upper_=np.array(m.row_upper)
    lp.offset_=0.0;lp.sense_=highspy.ObjSense.kMinimize
    lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise;lp.a_matrix_.num_row_,lp.a_matrix_.num_col_=m.rows,m.cols
    lp.a_matrix_.start_=np.array(m.indptr,dtype=np.int32);lp.a_matrix_.index_=np.array(m.indices,dtype=np.int32);lp.a_matrix_.value_=np.array(m.data)
    lp.integrality_=[highspy.HighsVarType.kContinuous]*m.cols
    require(h.passModel(lp)==highspy.HighsStatus.kOk,'Rejected fixed LP')
    got=h.getLp();require((got.num_row_,got.num_col_)==(m.rows,m.cols),'Backend dimensions')
    require(tuple(got.col_lower_)==lower and tuple(got.col_upper_)==upper and tuple(got.row_lower_)==m.row_lower and tuple(got.row_upper_)==m.row_upper,'Backend row/column bounds')
    require(all(c==0 for c in got.col_cost_) and got.offset_==0 and got.sense_==highspy.ObjSense.kMinimize,'Backend objective')
    require(not got.integrality_ or all(t==highspy.HighsVarType.kContinuous for t in got.integrality_),'Unexpected free integrality')
    matrix=got.a_matrix_;entries=[[] for _ in range(m.rows)]
    if matrix.format_==highspy.MatrixFormat.kRowwise:
        require(len(matrix.start_)==m.rows+1,'CSR starts')
        for i in range(m.rows):entries[i]=[(int(matrix.index_[k]),float(matrix.value_[k])) for k in range(matrix.start_[i],matrix.start_[i+1])]
    elif matrix.format_==highspy.MatrixFormat.kColwise:
        require(len(matrix.start_)==m.cols+1,'CSC starts')
        for j in range(m.cols):
            for k in range(matrix.start_[j],matrix.start_[j+1]):entries[matrix.index_[k]].append((j,float(matrix.value_[k])))
    else:raise ValueError('Unsupported readback orientation')
    data=[];indices=[];indptr=[0]
    for i,row in enumerate(entries):
        row.sort();wanted=sorted(zip(m.indices[m.indptr[i]:m.indptr[i+1]],m.data[m.indptr[i]:m.indptr[i+1]]))
        require(row==wanted,'Backend coefficient readback')
        indices.extend(j for j,c in row);data.extend(c for j,c in row);indptr.append(len(data))
    actual={}
    for key,value in OPTIONS.items():
        status,current=h.getOptionValue(key);require(status==highspy.HighsStatus.kOk and current==value,'Backend option changed');actual[key]=current
    np.savez_compressed(RUN/'backend_readback.npz',data=np.array(data),indices=np.array(indices,dtype=np.int64),indptr=np.array(indptr,dtype=np.int64),
        shape=np.array([m.rows,m.cols],dtype=np.int64),column_lower=np.array(got.col_lower_),column_upper=np.array(got.col_upper_),
        row_lower=np.array(got.row_lower_),row_upper=np.array(got.row_upper_),objective=np.array(got.col_cost_),original_integrality=np.array(bits,dtype=np.uint8))
    save(RUN/'backend_readback.json',dict(original_rows=m.rows,columns=m.cols,coefficients=len(data),all_original_bits_fixed=len(fixed),
        unchanged_original_matrix=True,only_state_bounds_fixed=True,no_free_integer_variables=True,options=actual,
        readback_sha256=sha(RUN/'backend_readback.npz'),optimizer_calls=0))
    return h

'''
runner='''def run(expected):
    phase=time.perf_counter();require(not RUN.exists() and not PRIVATE.exists(),'One fresh run only')
    v,m,bits,fixed,lower,upper,bindings=load_prepared(expected);transport=[bind(PRE/'input_manifest.json'),bind(PRE/'prepared_freeze.json')]
    RUN.mkdir();PRIVATE.mkdir(parents=True);save(RUN/'execution_started.json',dict(utc=utc(),freeze_sha256=expected))
    ledger=dict(attempted=0,returned=0);result=dict(verdict='UNKNOWN',accepted_common_witness=False,no_exact_negative_claim=True)
    h=None;stage='candidate_admission'
    try:
        if not read(PRE/'candidate_admission.json')['admitted']:result['verdict']='NOT_RUN_CANDIDATE_DISCRETE_REJECTION'
        else:
            import numpy as np
            import highspy
            stage='backend_construction_readback';h=build_readback(highspy,np,m,bits,fixed,lower,upper)
            remaining=PHASE_SECONDS-(time.perf_counter()-phase)
            save(RUN/'admission.json',dict(utc=utc(),remaining_seconds=remaining,required_seconds=65.0,admitted=remaining>=65))
            if remaining<65:result['verdict']='NOT_RUN_PHASE_GUARD'
            else:
                save(RUN/'call_ready.json',dict(utc=utc(),not_actual_call=True))
                remaining=PHASE_SECONDS-(time.perf_counter()-phase)
                if remaining<65:result['verdict']='NOT_RUN_POST_WRITE_PHASE_GUARD'
                else:
                    stage='sole_fixed_LP';ledger.update(attempted=1,started_utc=utc(),actual_call_remaining_seconds=remaining);clock=time.perf_counter()
                    try:status=h.run()
                    finally:ledger['actual_seconds']=time.perf_counter()-clock
                    ledger.update(returned=1,ended_utc=utc());stage='archive_returned_point'
                    sol=h.getSolution();info=h.getInfo()
                    result.update(model_status=h.modelStatusToString(h.getModelStatus()),run_status=str(status),value_valid=bool(sol.value_valid),
                        actual_seconds=ledger['actual_seconds'],soft_overrun_seconds=max(0,ledger['actual_seconds']-60),simplex_iterations=int(info.simplex_iteration_count))
                    save(RUN/'solver_returned.json',result)
                    raw=np.array(sol.col_value,dtype=np.float64);np.savez_compressed(RUN/'raw_solution.npz',vector=raw)
                    if sol.value_valid:
                        stage='unchanged_original_acceptance';checked=candidate_check(v,np,raw,bits,fixed)
                        result['candidate_eligible']=checked['eligible'];result['accepted_common_witness']=checked['accepted']
                        result['verdict']='VERIFIED_EXPANDED_COMMON_COMMITMENT' if checked['accepted'] else 'UNKNOWN_REJECTED_CANDIDATE'
        stage='close';validate(bindings);validate(transport);save(RUN/'result.json',result);elapsed=time.perf_counter()-phase
        save(RUN/'completion.json',dict(utc=utc(),status='CLOSED_PENDING_INDEPENDENT_REVIEW',call_ledger=ledger,planned_calls=1,
            optimizer_calls=ledger['attempted'],candidates=1,phase_seconds=elapsed,soft_phase_overrun_seconds=max(0,elapsed-PHASE_SECONDS),
            all_inputs_unchanged=True,no_retry_or_additional_candidate=True,nominal_feasibility_claim=False,
            final_write_cleanup_receipt_outside_sample=True))
        print(json.dumps(dict(verdict=result['verdict'],calls=ledger['attempted'])),flush=True)
    except BaseException as exc:
        save(RUN/'execution_failure.json',dict(utc=utc(),stage=stage,error_type=type(exc).__name__,ledger=ledger,scientific_verdict='UNKNOWN',automatic_retry=False))
        raise RuntimeError('Common union stopped; failure preserved; no automatic retry') from None
    finally:
        if h is not None:h.clear()
        save(RUN/'private_log_receipt.json',dict(raw_logs_public=False,privacy_review='NOT_PERFORMED',files=[bind(p) for p in PRIVATE.glob('*.log')]))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--prepare-only',action='store_true');g.add_argument('--run-prepared',action='store_true');p.add_argument('--expected-freeze-sha256');a=p.parse_args()
    if a.prepare_only:prepare()
    else:require(a.expected_freeze_sha256 is not None,'External freeze digest');run(a.expected_freeze_sha256)
'''
out=ROOT/'src/researchnext_common_union.py';assert not out.exists();text=prefix+construction+candidate+runner;ast.parse(text)
out.write_text(text,encoding='utf-8',newline='\n');print(hashlib.sha256(out.read_bytes()).hexdigest())
