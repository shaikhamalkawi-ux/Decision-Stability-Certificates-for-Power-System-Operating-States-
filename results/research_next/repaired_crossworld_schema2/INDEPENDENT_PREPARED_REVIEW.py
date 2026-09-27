"""Independent admission of unchanged repaired bits; no cut evaluation or solver."""
from pathlib import Path
from fractions import Fraction as Q
from datetime import datetime,timezone
import ast,hashlib,importlib.util,json,math,struct,sys,time
ROOT=Path(__file__).resolve().parents[3]
ARM=ROOT/'results/research_next/repaired_crossworld_schema2';PRE=ARM/'prepared'
SOURCE='cf951d0dc5ac69df003b919df1e7d6400b71b25fc7e7e7ec7137b2480fc5b32d'
PROTOCOL='0b1d513cbfd47474b39d35572478cc092554f8f862ab5aae029eb14f907cfc85'
FREEZE='6e4565d510fceec0308f97ccf59aeaf41ec787252abd39ba29fad204cda89bcd'
MANIFEST='6948d3d9a4b292273f07297a10a65d7574d208cfe6bcce013eb9bca52868dee4'
KERNEL='708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'
def need(ok,msg):
    if not ok:raise AssertionError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def check(items):
    need(len({i['path'].casefold() for i in items})==len(items),'Unique bindings')
    for i in items:
        p=Path(i['path']);need(p.stat().st_size==i['bytes'] and sha(p)==i['sha256'],str(p))
def functions(path):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef)}
def main():
    started=time.perf_counter();need(not (ARM/'run01').exists(),'Run absent at entry')
    source=ROOT/'src/researchnext_repaired_crossworld_schema2.py';oldsource=ROOT/'src/researchnext_repaired_crossworld.py'
    need(sha(source)==SOURCE and sha(ROOT/'docs/research_next/REPAIRED_CROSSWORLD_SCHEMA2_PROTOCOL.md')==PROTOCOL,'Final source/protocol')
    old,new=functions(oldsource),functions(source)
    need(set(new)-set(old)=={'captured_member_sha'} and not set(old)-set(new),'Only added archive-member helper')
    need(sorted(n for n in old if old[n]!=new[n])==['prepare','self_test'],'Unchanged scientific/gate/acceptance functions')
    need(sha(PRE/'prepared_freeze.json')==FREEZE and sha(PRE/'input_manifest.json')==MANIFEST,'Trusted archive')
    freeze=read(PRE/'prepared_freeze.json');items=read(PRE/'input_manifest.json')['files'];need(len(items)==179,'Manifest denominator');check(items)
    need(freeze['source_sha256']==SOURCE and freeze['protocol_sha256']==PROTOCOL and freeze['manifest_sha256']==MANIFEST,'Freeze source relation')
    need(freeze['optimizer_calls']==freeze['cut_evaluations']==freeze['highspy_imports']==0,'Prepared zero execution')
    bound={str(Path(i['path']).resolve()).casefold():i for i in items}
    for root,n in [('common_commitment',48),('day321_local_repair',65),('union_affine_cut_schema2',73)]:
        inherited=read(ROOT/f'results/research_next/{root}/prepared/input_manifest.json')['files'];need(len(inherited)==n,'Inherited denominator')
        need(all(bound[str(Path(i['path']).resolve()).casefold()]==i for i in inherited),'All original inherited inputs')
    copies=read(PRE/'copy_provenance.json')['copies'];need(len(copies)==25,'Copies denominator')
    for e in copies:
        need(Path(e['original']['path']).read_bytes()==Path(e['copy']['path']).read_bytes(),'Captured exact copy')
        need(bound[str(Path(e['original']['path']).resolve()).casefold()]==e['original'],'Original copy membership')
        need(bound[str(Path(e['copy']['path']).resolve()).casefold()]==e['copy'],'New copy membership')
        relative=Path(e['copy']['path']).relative_to(PRE)
        oldpartial=ROOT/'results/research_next/repaired_crossworld/prepared'/relative
        need(oldpartial.read_bytes()==Path(e['copy']['path']).read_bytes(),'Old partial payload preserved')
    affine=ROOT/'results/research_next/union_affine_cut_schema2/prepared'
    need(sha(affine/'joint/column_maps.json')==sha(PRE/'joint/column_maps.json')=='ced46514e0a6525a21f24aab86dea4b6e3ce0f27440f6dee53a47093dbc0f4bb','Correct actual map member')
    need(str((affine/'joint/column_maps.json').resolve()).casefold() in bound,'Full captured member admission')
    for world in ('identity','days_321'):
        for name in ('matrix.npz','bounds.npz','integrality.npz','model_metadata.json'):
            need(sha(affine/world/name)==sha(PRE/world/name),'Cut model provenance')
    repair=ROOT/'results/research_next/day321_local_repair'
    for name in ('matrix.npz','bounds.npz','integrality.npz','model_metadata.json','native_inputs.npz','native_spec.json'):
        need(sha(repair/'prepared/model'/name)==sha(PRE/'days_321'/name),'Positive model/native provenance')
    need(sha(PRE/'repair_vector.npz')=='fc9276c52baa182b0eba018df548bb0125290cb2413dd469c1899516c03733c3','Fixed positive candidate')
    kernel=ROOT/'src/research8h_standalone_verify.py';need(sha(kernel)==KERNEL,'Decoder pin')
    sys.dont_write_bytecode=True;spec=importlib.util.spec_from_file_location('repaired_crossworld_review_kernel',kernel);v=importlib.util.module_from_spec(spec);sys.modules[spec.name]=v;spec.loader.exec_module(v)
    def mask(folder,n):return tuple(v.vector(v.read_npz(folder/'integrality.npz',('integrality',))['integrality'],('|u1',),n,'mask'))
    identity=v.load_model(PRE/'identity');joint=v.load_model(PRE/'joint')
    need((identity.rows,identity.cols,len(identity.data))==(34681,23016,145588),'Identity dimensions')
    need((joint.rows,joint.cols,len(joint.data))==(69362,33936,291176),'Joint dimensions')
    bits=mask(PRE/'identity',23016);expected=tuple(int(6888<=j<18984) for j in range(23016))
    need(bits==expected and mask(PRE/'days_321',23016)==expected,'Original full world masks')
    need(mask(PRE/'joint',33936)==tuple(int(6888<=j<18984) for j in range(33936)),'Original full joint mask')
    point=v.vector(v.read_npz(PRE/'repair_vector.npz',('vector',))['vector'],('<f8',),23016,'existing point')
    need(all(math.isfinite(x) for x in point),'Finite archived coordinates')
    fixed={j:point[j] for j in range(23016) if bits[j]};need(len(fixed)==12096 and all(a in (0.,1.) for a in fixed.values()),'Full unchanged binary schedule')
    schedule=read(PRE/'fixed_schedule.json');entries=schedule['fixed_columns']
    need(entries==[dict(column=j,value_hex=x.hex()) for j,x in fixed.items()],'Exact saved state hex chronology')
    need(schedule['source_vector_sha256']==sha(PRE/'repair_vector.npz') and schedule['new_schedule_constructions']==0 and schedule['no_permutation_or_canonicalization'],'Fixed source schedule role')
    arrays=v.read_npz(PRE/'fixed_bounds.npz',('column_lower','column_upper'))
    lo=v.vector(arrays['column_lower'],('<f8',),23016,'fixed lower');hi=v.vector(arrays['column_upper'],('<f8',),23016,'fixed upper')
    def bit_equal(a,b):return struct.pack('<d',a)==struct.pack('<d',b)
    for j in range(23016):
        if bits[j]:need(bit_equal(lo[j],fixed[j]) and bit_equal(hi[j],fixed[j]) and identity.lower[j]<=fixed[j]<=identity.upper[j],'Prescribed state box')
        else:need(bit_equal(lo[j],identity.lower[j]) and bit_equal(hi[j],identity.upper[j]),'Continuous box byte preservation')
    state_rows=[]
    for r in range(identity.rows):
        entries=range(identity.indptr[r],identity.indptr[r+1])
        if all(bits[identity.indices[k]] for k in entries):
            val=sum((Q(identity.data[k])*Q(fixed[identity.indices[k]]) for k in entries),Q(0))
            need((not math.isfinite(identity.row_lower[r]) or val>=Q(identity.row_lower[r])) and (not math.isfinite(identity.row_upper[r]) or val<=Q(identity.row_upper[r])),'Nominal state-only membership')
            state_rows.append(r)
    need(len(state_rows)==16032 and state_rows==schedule['state_rows'],'All state-only rows')
    maps=read(PRE/'joint/column_maps.json');need(maps['worlds']==['identity','days_321'],'World order')
    shared=set(range(6888,18984));mapped=[]
    for world,mapping in zip(maps['worlds'],maps['original_to_joint']):
        need(len(mapping)==len(set(mapping))==23016 and all(type(j) is int and 0<=j<33936 for j in mapping),'Injective complete world map')
        need(mapping[6888:18984]==list(range(6888,18984)),'Every shared original state')
        mapped.append(set(mapping));meta=read(PRE/world/'model_metadata.json')
        need(meta['offsets']==dict(P=0,U=6888,Y=10920,Z=14952,theta=18984) and meta['budget_MWh']==23195,'Actual original semantics')
    need(mapped[0]&mapped[1]==shared and mapped[0]|mapped[1]==set(range(33936)),'Private disjoint/full joint coverage')
    # Read schema only; no coefficient-times-U or alpha/cap evaluation.
    for world in maps['worlds']:
        cut=read(PRE/(world+'_cut.json'));support=[c['column'] for c in cut['coefficients']]
        need(cut['world']==world and cut['status']=='VERIFIED_GLOBAL_EXPANDED_AFFINE_NECESSARY_CUT' and len(support)==len(set(support))==82 and all(6888<=j<10920 for j in support),'Frozen U-cut schema')
        need(cut['new_derived_row_expansion']==0,'No new cut tolerance')
    plan=read(PRE/'plan.json')
    need(plan['options']==dict(time_limit=60.,threads=1,random_seed=0,presolve='on',solver='simplex'),'One fixed LP options')
    need(plan['candidates']==plan['maximum_optimizer_calls']==1 and plan['LP_world']=='identity' and plan['phase_seconds']==240 and plan['start_guard_seconds']==65 and plan['gate_scientific_evaluations']==0 and plan['no_retry'] and plan['no_ray'],'Plan scope')
    fixture=read(ARM/'synthetic_tests.json');need(fixture['source_sha256']==SOURCE and fixture['protocol_sha256']==PROTOCOL and len(fixture['checks'])==5 and fixture['status']=='PASS','Final fixture receipt')
    check(items);need(sha(PRE/'prepared_freeze.json')==FREEZE and sha(PRE/'input_manifest.json')==MANIFEST and not (ARM/'run01').exists(),'Frozen/unexecuted at close')
    result=dict(status='PASS_INDEPENDENT_REPAIRED_CROSSWORLD_SCHEMA2_PREPARED',utc=datetime.now(timezone.utc).isoformat(),
      reviewer_source_sha256=sha(__file__),source_sha256=SOURCE,protocol_sha256=PROTOCOL,freeze_sha256=FREEZE,manifest_sha256=MANIFEST,
      bindings=179,exact_copies=25,old_partial_payloads_unchanged=25,inherited_manifests=[48,65,73],
      original_bits_fixed=12096,identity_state_only_rows_exact=16032,continuous_boxes_byte_unchanged=True,
      shared_private_map_checked=True,cut_model_native_provenance=True,scientific_cut_evaluations=0,
      old_full_witness_replays=0,producer_imports=0,solver_imports=0,optimizer_calls=0,
      reused_decoder='pinned standalone kernel; no producer merge/solve routine',run_absent_at_entry_and_close=True,
      elapsed_seconds=time.perf_counter()-started)
    with (ARM/'INDEPENDENT_PREPARED_REVIEW.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
    print(result['status'],result['elapsed_seconds'])
if __name__=='__main__':main()
