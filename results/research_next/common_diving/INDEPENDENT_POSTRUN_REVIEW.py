"""Read-only closed common-diving audit; no solver or producer imports."""
from pathlib import Path
from fractions import Fraction as Q
import argparse
import csv
import hashlib
import importlib.util
import json
import math
import struct
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
ARM = ROOT/'results/research_next/common_diving'
PRE = ARM/'prepared'
RUN = ARM/'run01'
ORIGINAL = ROOT/'results/research_next/common_commitment/prepared'
TAU = Q.from_float(1e-5)
PINS = {
 'src/researchnext_common_diving.py':'d5b5fb33c30dbe2ad15bace67ecfa42cb3e4b076769f8ff8a0341827124d30ba',
 'docs/research_next/COMMON_DIVING_PROTOCOL.md':'6b4df1dfa036fbc9a617dc996d66d0dddb52c1c00e2acdd9cdcf528eb767d318',
 'src/research8h_standalone_verify.py':'708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f',
 'results/research_next/common_diving/prepared/prepared_freeze.json':'b8a3c14d4e9826b63542a0d84377092c005b81fc9078f6803d923007ff06d3e6',
 'results/research_next/common_diving/prepared/input_manifest.json':'843b0e9087bef847f006b502b9bac3ce4f85475de3772ea5b35db89c834f30b3',
 'results/research_next/common_diving/INDEPENDENT_PREPARED_REVIEW.json':'fb80353c3cbd2ddd22049126f38ba87a0593a2be535fe42d835bc4ef3633a0ac',
}

def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def frac(r): return Q(int(r['numerator']),int(r['denominator']))
def rat(x): return dict(numerator=str(x.numerator),denominator=str(x.denominator),approximate=float(x))
def pack(values): return b''.join(struct.pack('<d',x) for x in values)

def exact_point(m, values, mask):
    assert len(values) == len(mask) == m.cols and all(math.isfinite(x) for x in values)
    x = tuple(Q(z) for z in values)
    row_max = box_max = Q(0)
    row_strict = row_wide = box_strict = box_wide = 0
    for j,(l,u) in enumerate(zip(m.lower,m.upper)):
        for g in (Q(l)-x[j],x[j]-Q(u)):
            box_max=max(box_max,g);box_strict+=g>0;box_wide+=g>TAU
    cache={a:Q(a) for a in set(m.data)}
    for i in range(m.rows):
        s=sum((cache[m.data[k]]*x[m.indices[k]] for k in range(m.indptr[i],m.indptr[i+1])),Q(0))
        for endpoint,side in ((m.row_lower[i],-1),(m.row_upper[i],1)):
            if not math.isfinite(endpoint): continue
            g=(s-Q(endpoint))*side
            row_max=max(row_max,g);row_strict+=g>0;row_wide+=g>TAU
    nonbinary=[j for j,b in enumerate(mask) if b and x[j] not in (0,1)]
    return dict(strict_pass=not(row_strict or box_strict or nonbinary),
                expanded_pass=not(row_wide or box_wide or nonbinary),
                original_binary_coordinates=sum(mask),nonbinary_count=len(nonbinary),rows_checked=m.rows,
                columns_checked=m.cols,coefficient_uses=len(m.data),maximum_row_violation=rat(row_max),
                maximum_column_violation=rat(box_max),strict_row_sides=row_strict,expanded_row_sides=row_wide,
                strict_column_sides=box_strict,expanded_column_sides=box_wide)

def native(v, point, folder):
    arrays=v.read_npz(folder/'native_inputs.npz',('pmin','pmax','net','rows','source_hour','nodal'))
    metadata=load(folder/'model_metadata.json');spec=load(folder/'native_spec.json')
    names=metadata['unit_names'];units=metadata['thermal_unit_names']
    assert len(names)==41 and len(units)==24 and len(spec)==41
    thermal_indices=[names.index(n) for n in units]
    fossil=set(metadata['fossil_units']);assert len(fossil)==23 and '121_NUCLEAR_1' not in fossil
    x=tuple(Q(p) for p in point);pmin=arrays['pmin'].values;pmax=arrays['pmax'].values
    maxgap=Q(0);violations=0;energy=Q(0)
    def check(g):
        nonlocal maxgap,violations
        maxgap=max(maxgap,g);violations+=g>TAU
    def boolean(ok): check(Q(0) if ok else Q(1))
    for t in range(168):
        production=x[41*t:41*t+41]
        check(abs(sum(production,Q(0))-Q(arrays['net'].values[t])))
        for j,p in enumerate(production):
            low,high=Q(pmin[41*t+j]),Q(pmax[41*t+j])
            check(max(Q(0),-p,p-high))
            if spec[j]['category']=='Hydro': check(abs(p-low))
            if names[j] in fossil:energy+=p
        for k,j in enumerate(thermal_indices):
            u=x[6888+24*t+k];y=x[10920+24*t+k];z=x[14952+24*t+k]
            boolean(u in (0,1) and y in (0,1) and z in (0,1))
            low,high=Q(pmin[41*t+j]),Q(pmax[41*t+j])
            check(max(Q(0),low*u-production[j],production[j]-high*u))
            if t==0:
                boolean(y==0 and z==0)
                continue
            previous=x[6888+24*(t-1)+k]
            expected_y=Q(int(previous==0 and u==1));expected_z=Q(int(previous==1 and u==0))
            boolean(y==expected_y and z==expected_z)
            if u!=previous:
                dwell=spec[j]['minimum_up'] if u==1 else spec[j]['minimum_down']
                boolean(all(x[6888+24*s+k]==u for s in range(t,min(168,t+dwell))))
            if u==previous==1:
                rate=frac(spec[j]['hourly_rational'])
                check(max(Q(0),abs(production[j]-x[41*(t-1)+j])-rate))
    check(max(Q(0),energy-23195))
    return dict(expanded_pass=violations==0,violations=violations,maximum_violation=rat(maxgap),
                exact_fossil_energy=rat(energy),cap_MWh=23195,
                native_network='All unchanged DC rows and theta boxes checked through original model.',
                ramp_semantics='Inherited pinned binary64 hourly conversion rationalization; no new unit conversion.')

def main(args):
    started=time.perf_counter();report=ARM/'INDEPENDENT_POSTRUN_REVIEW.json'
    assert not report.exists()
    for p,h in PINS.items():assert digest(ROOT/p)==h,p
    assert digest(RUN/'result.json')==args.expected_result_sha256
    assert digest(RUN/'completion.json')==args.expected_completion_sha256
    inventory=ARM/'producer_output_inventory.csv'
    assert digest(inventory)==args.expected_inventory_sha256
    outputs=list(csv.DictReader(inventory.open(encoding='utf-8-sig')))
    assert len({e['path'].casefold() for e in outputs})==len(outputs)
    snapshot={}
    for e in outputs:
        p=(ROOT/e['path']).resolve();assert p.is_relative_to(ARM.resolve())
        b=p.read_bytes();assert len(b)==int(e['bytes']) and hashlib.sha256(b).hexdigest()==e['sha256']
        snapshot[p]=b
    runfiles={p.resolve() for p in RUN.rglob('*') if p.is_file()}
    assert runfiles=={p for p in snapshot if p.is_relative_to(RUN.resolve())}
    bound=load(PRE/'input_manifest.json')['files'];assert len(bound)==66
    inputs={}
    for e in bound:
        p=Path(e['path']);b=p.read_bytes();assert len(b)==e['bytes'] and hashlib.sha256(b).hexdigest()==e['sha256']
        inputs[p]=b
    result=load(RUN/'result.json');done=load(RUN/'completion.json');ledger=done['call_ledger']
    assert done['planned_calls']==1 and done['optimizer_calls']==ledger['attempted']
    assert ledger['attempted'] in (0,1) and ledger['returned']==ledger['attempted']
    assert all(done[k] is True for k in ('all_frozen_bytes_unchanged','no_added_lp_or_ray_getter',
                                       'no_alternative_neighborhood_or_retry','posthoc','parent_initial_run_unchanged'))
    assert done['nominal_feasibility_claim'] is False and result['neighborhood_failure_is_not_full_infeasibility'] is True
    assert done['phase_soft_overrun']==max(0,done['phase_seconds']-300)
    assert not (RUN/'execution_failure.json').exists()
    candidate_review=None
    if ledger['attempted']:
        assert ledger['last_admission_remaining_seconds']>=125
        assert (RUN/'call_ready.json').exists() and load(RUN/'admission.json')['admitted']
        assert result['actual_seconds']==ledger['actual_seconds']
        assert result['soft_overrun_seconds']==max(0,ledger['actual_seconds']-120)
        expected=dict(time_limit=120.0,threads=1,random_seed=0,presolve='on',mip_rel_gap=1e-8,
                      log_to_console=False,log_file=str((RUN/'solver.log').resolve()))
        assert result['options']==expected
        returned=load(RUN/'solver_returned.json')
        for k in ('options','solver_version','run_status','model_status','value_valid','dual_valid','mip_node_count','actual_seconds','soft_overrun_seconds'):
            assert result[k]==returned[k]
        helper=ROOT/'src/research8h_standalone_verify.py'
        spec=importlib.util.spec_from_file_location('diving_closed_stdlib_reader',helper)
        v=importlib.util.module_from_spec(spec);sys.modules[spec.name]=v;spec.loader.exec_module(v)
        model=v.load_model(ORIGINAL/'joint')
        mask=tuple(v.vector(v.read_npz(ORIGINAL/'joint/integrality.npz',('integrality',))['integrality'],('|u1',),model.cols,'full mask'))
        assert sum(mask)==12096
        raw=v.vector(v.read_npz(RUN/'raw_solution.npz',('vector',))['vector'],('<f8',),model.cols,'raw MIP vector')
        eligible=bool(result['value_valid']) and all(math.isfinite(x) for x in raw)
        recovered=list(raw)
        if eligible:
            for j,b in enumerate(mask):
                if not b:continue
                near=[k for k in (0,1) if abs(Q(raw[j])-k)<=TAU]
                if len(near)!=1:eligible=False;break
                recovered[j]=float(near[0])
        if 'candidate_eligible' in result:assert result['candidate_eligible']==eligible
        if eligible:
            cand=v.vector(v.read_npz(RUN/'candidate_vector.npz',('vector',))['vector'],('<f8',),model.cols,'candidate')
            assert pack(cand)==pack(recovered)
            assert pack([x for x,b in zip(raw,mask) if not b])==pack([x for x,b in zip(cand,mask) if not b])
            restriction=load(PRE/'restriction.json')
            assert all(cand[e['column']]==e['fixed_bit'] for e in restriction['fixed'])
            joint=exact_point(model,cand,mask);restricted=exact_point(v.load_model(PRE),cand,mask)
            maps=load(ORIGINAL/'joint/column_maps.json')['original_to_joint'];world_reports=[];states=[]
            for w,mapping in zip(('identity','days_321'),maps):
                folder=ORIGINAL/w;wm=v.load_model(folder)
                wb=tuple(v.vector(v.read_npz(folder/'integrality.npz',('integrality',))['integrality'],('|u1',),wm.cols,'world full mask'))
                point=v.vector(v.read_npz(RUN/(w+'_vector.npz'),('vector',))['vector'],('<f8',),wm.cols,'world vector')
                assert pack(point)==pack([cand[j] for j in mapping]) and sum(wb)==12096
                ep=exact_point(wm,point,wb);np=native(v,point,folder)
                world_reports.append(dict(world=w,original=ep,native=np))
                states.append(tuple(point[j] for j,b in enumerate(wb) if b))
            common=states[0]==states[1] and len(states[0])==12096 and all(s in (0,1) for s in states[0])
            accepted=common and joint['expanded_pass'] and restricted['expanded_pass'] and all(w['original']['expanded_pass'] and w['native']['expanded_pass'] for w in world_reports)
            producer=load(RUN/'exact_candidate_checks.json')
            assert producer['accepted_common_witness']==accepted==result['accepted_common_witness']
            assert producer['common_all12096_bits']==common
            for label,own in [('joint_original',joint),('restricted_model',restricted)]:
                assert producer[label]['expanded_pass']==own['expanded_pass'] and producer[label]['strict_pass']==own['strict_pass']
            for own,old in zip(world_reports,producer['worlds']):
                assert own['world']==old['world']
                for key in ('expanded_pass','strict_pass'):assert own['original'][key]==old['original'][key]
                assert own['native']['expanded_pass']==old['native']['expanded_pass']
                assert own['native']['violations']==old['native']['violations']
                for key in ('maximum_violation','exact_fossil_energy'):assert frac(own['native'][key])==frac(old['native'][key])
            candidate_review=dict(joint=joint,restricted=restricted,worlds=world_reports,common_all12096_bits=common,
                                  continuous_bytes_unchanged=True,all_fixed_bits_exact=True,accepted=accepted)
        else:
            assert not result['accepted_common_witness']
            assert not (RUN/'candidate_vector.npz').exists() and not (RUN/'exact_candidate_checks.json').exists()
    else:
        assert result['verdict'] in ('NOT_RUN_PHASE_GUARD','NOT_RUN_POST_WRITE_PHASE_GUARD')
        assert not result['accepted_common_witness']
    if result['accepted_common_witness']:
        assert result['verdict']=='VERIFIED_EXPANDED_COMMON_COMMITMENT'
    else:
        assert result['verdict'] in ('UNKNOWN','UNKNOWN_REJECTED_CANDIDATE','NOT_RUN_PHASE_GUARD','NOT_RUN_POST_WRITE_PHASE_GUARD')
    for p,b in inputs.items():assert p.read_bytes()==b
    for p,b in snapshot.items():assert p.read_bytes()==b
    for p,h in PINS.items():assert digest(ROOT/p)==h
    assert digest(inventory)==args.expected_inventory_sha256
    assert runfiles=={p.resolve() for p in RUN.rglob('*') if p.is_file()}
    output=dict(status='PASS_INDEPENDENT_COMMON_DIVING_POSTRUN',review_source_sha256=digest(__file__),
        trusted_output_inventory_sha256=args.expected_inventory_sha256,result_sha256=args.expected_result_sha256,
        completion_sha256=args.expected_completion_sha256,input_bindings_checked_twice=66,
        output_bindings_checked_twice=len(outputs),call_ledger=ledger,producer_verdict=result['verdict'],
        original_question_verdict='VERIFIED_EXPANDED_COMMON_COMMITMENT' if result['accepted_common_witness'] else 'UNKNOWN',
        restricted_failure_proves_full_infeasibility=False,candidate_review=candidate_review,
        no_solver_or_producer_import=True,optimizer_calls=0,prepared_matrix_transport_repeated=False,
        original_run_unchanged=True,seconds=time.perf_counter()-started)
    with report.open('x',encoding='utf-8') as f:json.dump(output,f,indent=2);f.write('\n')
    print(json.dumps(output))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--expected-inventory-sha256',required=True)
    p.add_argument('--expected-result-sha256',required=True);p.add_argument('--expected-completion-sha256',required=True)
    main(p.parse_args())
