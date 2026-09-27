"""Closed SCIP/union audit: pinned stdlib kernel, separate native replay, no optimizer."""
from pathlib import Path
from fractions import Fraction as Q
import argparse, ast, csv, hashlib, importlib.util, json, math, struct, sys, time, zipfile
from datetime import datetime
sys.dont_write_bytecode = True
ARM = Path(__file__).resolve().parent
ROOT = ARM.parents[2]
PRE, RUN = ARM/'prepared', ARM/'run01'
ORIGINAL = ROOT/'results/research_next/common_commitment/prepared'
TAU = Q.from_float(1e-5)
KERNEL_SHA = '708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'
CONFIG = {
 'common_union': dict(source='92089c0301bd6a7399728abdf0a9a8964bd570199bc2490ea22e947adfedc1a1',protocol='fdf6ff12aa5afbea4547583d1cdd2d12d774e18905eb2fdb1a6cf12c64b7e06c',freeze='8d5e348d91db8ae082a1a036d2359ac382891b25849e9e682fb833e9ae52d0a2',manifest='1337e9674d15fc52023733b8c72b1140c20d01a472a287fd43a90cd5719d3a2d',bindings=94,limit=60.,phase=240.,guard=65.),
 'common_scip': dict(source='e80a8e80b1a25def3f94564b3a33527a367fc21e4bd87ea52bcdbc2f3e16d8d5',protocol='07b17a4105f9f9c026f26350593814e92b79dd528eff3cb9ad7b0c20e5221597',freeze='b1d7d8553daf3b4a6373d91520cf52adce898008fc961d090d75b599a16d3b50',manifest='7e380d9d9469132088aca75bc2191d0567cedb49ec2f1db662d66d690d79d074',bindings=134,limit=1800.,phase=2400.,guard=1805.),
}

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def frac(r): return Q(int(r['numerator']),int(r['denominator']))
def rat(x): return dict(numerator=str(x.numerator),denominator=str(x.denominator),approximate=float(x))
def packed(v): return b''.join(struct.pack('<d',x) for x in v)
def verify(items, relative=False):
    seen=set()
    for r in items:
        p=(ROOT/r['path'] if relative else Path(r['path'])).resolve()
        assert p not in seen; seen.add(p)
        data=p.read_bytes()
        assert len(data)==int(r['bytes']) and hashlib.sha256(data).hexdigest()==r['sha256'],str(p)
    return seen

def load_kernel():
    p=ROOT/'src/research8h_standalone_verify.py';assert sha(p)==KERNEL_SHA
    s=importlib.util.spec_from_file_location('closed_independent_point_kernel',p)
    v=importlib.util.module_from_spec(s);sys.modules[s.name]=v;s.loader.exec_module(v)
    return v

def full_mask(v,folder,cols):
    return tuple(v.vector(v.read_npz(folder/'integrality.npz',('integrality',))['integrality'],('|u1',),cols,'original full mask'))

def native(v, point, folder):
    a=v.read_npz(folder/'native_inputs.npz',('pmin','pmax','net','rows','source_hour','nodal'))
    meta=read(folder/'model_metadata.json');spec=read(folder/'native_spec.json')
    names=meta['unit_names'];thermal=meta['thermal_unit_names']
    assert len(names)==len(spec)==41 and len(thermal)==24
    fossil=set(meta['fossil_units']);assert len(fossil)==23 and '121_NUCLEAR_1' not in fossil
    x=tuple(Q(p) for p in point);maximum=Q();violations=0;energy=Q()
    def check(g):
        nonlocal maximum,violations
        maximum=max(maximum,g);violations+=g>TAU
    def yes(b):check(Q(0) if b else Q(1))
    for t in range(168):
        powers=x[41*t:41*t+41]
        check(abs(sum(powers,Q())-Q(a['net'].values[t])))
        for j,p in enumerate(powers):
            lo,hi=Q(a['pmin'].values[41*t+j]),Q(a['pmax'].values[41*t+j])
            check(max(Q(),-p,p-hi))
            if spec[j]['category']=='Hydro':check(abs(p-lo))
            if names[j] in fossil:energy+=p
        for k,name in enumerate(thermal):
            j=names.index(name);u,y,z=(x[o+24*t+k] for o in (6888,10920,14952))
            yes(all(b in (0,1) for b in (u,y,z)))
            lo,hi=Q(a['pmin'].values[41*t+j]),Q(a['pmax'].values[41*t+j])
            check(max(Q(),lo*u-powers[j],powers[j]-hi*u))
            if t==0:yes(y==z==0);continue
            prior=x[6888+24*(t-1)+k]
            yes(y==int(prior==0 and u==1) and z==int(prior==1 and u==0))
            if u!=prior:
                length=spec[j]['minimum_up' if u else 'minimum_down']
                yes(all(x[6888+24*h+k]==u for h in range(t,min(168,t+length))))
            if u==prior==1:check(max(Q(),abs(powers[j]-x[41*(t-1)+j])-frac(spec[j]['hourly_rational'])))
    check(max(Q(),energy-23195))
    return dict(expanded_pass=violations==0,violations=violations,maximum_violation=rat(maximum),exact_fossil_energy=rat(energy),cap_MWh=23195,native_network='Complete original DC rows and angle boxes checked by pinned exact kernel.')

def read_backend(v,m,bits,kind):
    path=RUN/'backend_readback.npz';record=read(RUN/'backend_readback.json')
    assert sha(path)==record['readback_sha256']
    if kind=='common_union':
        names=('data','indices','indptr','shape','column_lower','column_upper','row_lower','row_upper','objective','original_integrality')
        a=v.read_npz(path,names)
        assert tuple(a['shape'].values)==(m.rows,m.cols)
        assert tuple(a['data'].values)==m.data and tuple(a['indices'].values)==m.indices and tuple(a['indptr'].values)==m.indptr
        assert tuple(a['row_lower'].values)==m.row_lower and tuple(a['row_upper'].values)==m.row_upper
        fb=v.read_npz(PRE/'fixed_bounds.npz',('column_lower','column_upper'))
        assert a['column_lower'].values==fb['column_lower'].values and a['column_upper'].values==fb['column_upper'].values
        assert tuple(a['original_integrality'].values)==bits
        assert record['all_original_bits_fixed']==12096 and record['no_free_integer_variables']
        assert record['unchanged_original_matrix'] and record['only_state_bounds_fixed']
        assert record['options']==read(PRE/'plan.json')['options']
        backend_rows=m.rows;uses=len(m.data)
    else:
        names=('data','indices','indptr','shape','rhs','sense','column_lower','column_upper','objective','integrality')
        with zipfile.ZipFile(path) as z:
            assert len(z.namelist())==len(names) and set(z.namelist())=={n+'.npy' for n in names}
            a={n:v.parse_npy(z.read(n+'.npy')) for n in names if n!='sense'}
            raw=z.read('sense.npy')
        assert raw[:8]==b'\x93NUMPY\x01\x00';n=struct.unpack('<H',raw[8:10])[0]
        header=ast.literal_eval(raw[10:10+n].decode('latin1'));senses=raw[10+n:]
        assert header==dict(descr='|S1',fortran_order=False,shape=(82130,)) and len(senses)==82130 and set(senses)<={60,61,62}
        assert tuple(a['shape'].values)==(82130,m.cols)
        data,idx,ptr=a['data'].values,a['indices'].values,a['indptr'].values
        assert len(data)==len(idx)==316712 and len(ptr)==82131 and ptr[0]==0 and ptr[-1]==len(data) and all(x<=y for x,y in zip(ptr,ptr[1:]))
        mapping=read(PRE/'backend_rows.json')['rows'];assert len(mapping)==82130
        for k,row in enumerate(mapping):
            i=row['original_row'];expect=list(zip(m.indices[m.indptr[i]:m.indptr[i+1]],m.data[m.indptr[i]:m.indptr[i+1]]))
            assert list(zip(idx[ptr[k]:ptr[k+1]],data[ptr[k]:ptr[k+1]]))==sorted(expect)
            assert a['rhs'].values[k].hex()==row['rhs_hex'] and chr(senses[k])==row['sense']
        assert tuple(a['column_lower'].values)==m.lower and tuple(a['column_upper'].values)==m.upper and tuple(a['integrality'].values)==bits
        order=read(RUN/'backend_coordinate_order.json')
        assert len(order['variable_names'])==m.cols and set(order['variable_names'])=={f'x{j}' for j in range(m.cols)}
        assert len(order['constraint_names'])==82130 and set(order['constraint_names'])=={f'r{j}' for j in range(82130)}
        assert record['stage']=='PROBLEM' and record['no_extra_variables'] and record['all_rows_columns_objective_exact']
        params=read(RUN/'parameters.json');assert sha(RUN/'parameters.json')==record['parameters_sha256']
        assert params['explicit']==read(PRE/'plan.json')['options']
        assert all(params['after_setters'][k]==value for k,value in params['explicit'].items())
        assert params['changed']=={k:dict(before=val,after=params['after_setters'][k]) for k,val in params['defaults'].items() if val!=params['after_setters'][k]}
        assert params['changed_count']==len(params['changed']) and params['emphasis']=='FEASIBILITY'
        backend_rows=len(mapping);uses=len(data)
    assert all(c==0 for c in a['objective'].values) and record['optimizer_calls']==0
    assert record['columns']==m.cols and record['coefficient_uses' if kind=='common_scip' else 'coefficients']==uses
    return dict(original_rows=m.rows,backend_rows=backend_rows,columns=m.cols,original_bits=sum(bits),coefficient_uses=uses,complete_saved_readback_matches=True)

def point_review(v,m,bits,kind,result):
    validity=result['value_valid'] if kind=='common_union' else result['solution_count']>0
    if not validity:
        assert not result['accepted_common_witness'] and not (RUN/'candidate_vector.npz').exists() and not (RUN/'exact_candidate_checks.json').exists()
        if kind=='common_scip':assert not (RUN/'raw_solution.npz').exists()
        return None
    raw=tuple(v.vector(v.read_npz(RUN/'raw_solution.npz',('vector',))['vector'],('<f8',),m.cols,'raw'))
    expected=list(raw);eligible=all(math.isfinite(x) for x in raw)
    fixed={r['column']:r['value'] for r in read(PRE/'candidate_schedule.json')['fixed_columns']} if kind=='common_union' else None
    if eligible:
        for j,b in enumerate(bits):
            if not b:continue
            choices=([fixed[j]] if abs(Q(raw[j])-fixed[j])<=TAU else []) if fixed else [bit for bit in (0,1) if abs(Q(raw[j])-bit)<=TAU]
            if len(choices)!=1:eligible=False;break
            expected[j]=float(choices[0])
    assert result['candidate_eligible']==eligible
    if not eligible:
        assert not result['accepted_common_witness'] and not (RUN/'candidate_vector.npz').exists()
        return dict(eligible=False,accepted=False)
    candidate=tuple(v.vector(v.read_npz(RUN/'candidate_vector.npz',('vector',))['vector'],('<f8',),m.cols,'candidate'))
    assert packed(candidate)==packed(expected)
    assert packed([raw[j] for j,b in enumerate(bits) if not b])==packed([candidate[j] for j,b in enumerate(bits) if not b])
    joint=v.check_point(m,candidate,bits,TAU);producer=read(RUN/'exact_candidate_checks.json')
    assert joint==producer['joint']
    worlds=[];states=[];maps=read(ORIGINAL/'joint/column_maps.json')['original_to_joint']
    for world,mapping,old in zip(('identity','days_321'),maps,producer['worlds']):
        folder=ORIGINAL/world;wm=v.load_model(folder);wb=full_mask(v,folder,wm.cols);assert sum(wb)==12096
        point=tuple(v.vector(v.read_npz(RUN/(world+'_vector.npz'),('vector',))['vector'],('<f8',),wm.cols,world))
        assert packed(point)==packed([candidate[j] for j in mapping])
        exact=v.check_point(wm,point,wb,TAU);n=native(v,point,folder)
        assert old['world']==world and old['original']==exact
        assert n['expanded_pass']==old['native']['expanded_pass'] and n['violations']==old['native']['violations']
        assert all(frac(n[key])==frac(old['native'][key]) for key in ('maximum_violation','exact_fossil_energy'))
        worlds.append(dict(world=world,exact=exact,native=n));states.append(tuple(point[j] for j,b in enumerate(wb) if b))
    common=states[0]==states[1] and len(states[0])==12096 and all(x in (0,1) for x in states[0])
    accepted=common and joint['expanded_pass'] and all(r['exact']['expanded_pass'] and r['native']['expanded_pass'] for r in worlds)
    assert accepted==result['accepted_common_witness']==producer['accepted'] and common==producer['common_all12096_bits']
    if fixed:assert all(candidate[j]==val for j,val in fixed.items()) and producer['prescribed_all12096_bits']
    return dict(eligible=True,accepted=accepted,joint=joint,worlds=worlds,common_all12096_bits=common,continuous_bytes_unchanged=True,exact_kernel_reused=True,native_check_separately_written=True)

def main(args):
    start=time.perf_counter();kind=ARM.name;config=CONFIG[kind]
    report=ARM/'INDEPENDENT_POSTRUN_REVIEW.json';assert not report.exists()
    source=ROOT/f'src/researchnext_{kind}.py';protocol=ROOT/f'docs/research_next/{kind.upper()}_PROTOCOL.md'
    assert sha(source)==config['source'] and sha(protocol)==config['protocol']
    assert sha(PRE/'prepared_freeze.json')==config['freeze'] and sha(PRE/'input_manifest.json')==config['manifest']
    assert sha(RUN/'result.json')==args.expected_result_sha256 and sha(RUN/'completion.json')==args.expected_completion_sha256
    inventory=ARM/'producer_output_inventory.csv';assert sha(inventory)==args.expected_inventory_sha256
    outputs=list(csv.DictReader(inventory.open(encoding='utf-8-sig')));outpaths=verify(outputs,True)
    assert all(p.is_relative_to(ARM.resolve()) for p in outpaths)
    runfiles={p.resolve() for p in RUN.rglob('*') if p.is_file()}
    assert runfiles=={p for p in outpaths if p.is_relative_to(RUN.resolve())}
    inputs=read(PRE/'input_manifest.json')['files'];assert len(inputs)==config['bindings'];verify(inputs)
    result=read(RUN/'result.json');done=read(RUN/'completion.json');plan=read(PRE/'plan.json');ledger=done['call_ledger']
    assert not (RUN/'execution_failure.json').exists()
    assert ledger['attempted']==ledger['returned']==done['optimizer_calls']==done['planned_calls']==1
    assert ledger['actual_call_remaining_seconds']>=config['guard'] and read(RUN/'admission.json')['admitted']
    assert result['actual_seconds']==ledger['actual_seconds'] and result['soft_overrun_seconds']==max(0.,ledger['actual_seconds']-config['limit'])
    assert done['nominal_feasibility_claim'] is False and result['no_exact_negative_claim']
    assert done['phase_seconds']>=ledger['actual_seconds']
    phase_key='soft_phase_overrun_seconds' if kind=='common_union' else 'phase_soft_overrun'
    assert done[phase_key]==max(0.,done['phase_seconds']-config['phase'])
    assert plan['calls']==1 and plan['phase_seconds']==config['phase']
    returned=read(RUN/'solver_returned.json')
    for k,val in returned.items():
        if k not in ('verdict','accepted_common_witness'):assert result[k]==val
    if kind=='common_union':
        assert done['all_inputs_unchanged'] and done['no_retry_or_additional_candidate'] and done['candidates']==1
        assert plan['options']==dict(time_limit=60.,threads=1,random_seed=0,presolve='on',solver='simplex')
    else:
        assert done['all_frozen_bytes_unchanged'] and done['no_retries'] and done['no_lp_ray_iis_or_diving'] and done['no_warm_start']
        assert result['options']==plan['options'] and result['solver_version']=='10.0.2'
        assert read(RUN/'parameters_after_call.json')['parameters']==read(RUN/'parameters.json')['after_setters']
    assert (datetime.fromisoformat(ledger['ended_utc'])-datetime.fromisoformat(ledger['started_utc'])).total_seconds()>=0
    receipt=read(RUN/'private_log_receipt.json');assert not receipt['raw_logs_public'] and receipt['privacy_review']=='NOT_PERFORMED'
    v=load_kernel();m=v.load_model(ORIGINAL/'joint');bits=full_mask(v,ORIGINAL/'joint',m.cols)
    assert (m.rows,m.cols,len(m.data),sum(bits))==(69362,33936,291176,12096)
    backend=read_backend(v,m,bits,kind);candidate=point_review(v,m,bits,kind,result)
    assert result['verdict']==('VERIFIED_EXPANDED_COMMON_COMMITMENT' if result['accepted_common_witness'] else ('UNKNOWN_REJECTED_CANDIDATE' if result.get('candidate_eligible') is not None else 'UNKNOWN'))
    assert not any('ray' in p.name.lower() or 'certificate' in p.name.lower() for p in RUN.iterdir())
    verify(inputs);verify(outputs,True)
    assert sha(inventory)==args.expected_inventory_sha256 and sha(PRE/'prepared_freeze.json')==config['freeze'] and sha(PRE/'input_manifest.json')==config['manifest']
    assert sha(source)==config['source'] and sha(protocol)==config['protocol'] and runfiles=={p.resolve() for p in RUN.rglob('*') if p.is_file()}
    output=dict(status='INDEPENDENT_CLOSED_POSTRUN_PASS',arm=kind,reviewer_sha256=sha(__file__),input_bindings=len(inputs),producer_outputs=len(outputs),trusted_result_sha256=args.expected_result_sha256,trusted_completion_sha256=args.expected_completion_sha256,trusted_inventory_sha256=args.expected_inventory_sha256,source_sha256=config['source'],protocol_sha256=config['protocol'],all_inputs_outputs_unchanged=True,backend=backend,call_ledger=ledger,phase_seconds=done['phase_seconds'],producer_verdict=result['verdict'],original_question_verdict='VERIFIED_EXPANDED_COMMON_COMMITMENT' if result['accepted_common_witness'] else 'UNKNOWN',candidate_review=candidate,optimizer_calls=0,optimizer_imports=0,producer_imports=0,private_logs_read=False,old_joint_reassembly=False,pinned_exact_kernel_reused=True,elapsed_seconds=time.perf_counter()-start)
    with report.open('x',encoding='utf-8') as f:json.dump(output,f,indent=2);f.write('\n')
    print(json.dumps({k:value for k,value in output.items() if k!='candidate_review'}));print('REPORT_SHA256='+sha(report))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--expected-result-sha256',required=True);p.add_argument('--expected-completion-sha256',required=True);p.add_argument('--expected-inventory-sha256',required=True)
    main(p.parse_args())
