"""Hash/schema/source gate only: no decoder, producer import, or cut arithmetic."""
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

ROOT=Path(__file__).resolve().parents[3]
ARM=ROOT/'results/research_next/union_affine_cut';PRE=ARM/'prepared'
SOURCE=ROOT/'src/researchnext_union_affine_cut.py'
PROTOCOL=ROOT/'docs/research_next/UNION_AFFINE_CUT_PROTOCOL.md'
TRUST={
 'source':'746022d4ef39c7a5bc97969c32b644cc268b1a5c3a4ddf79d64082537bb7f541',
 'protocol':'2ab0739a10463712d1d31b19433e97a085c50086035661c14246e4da0d66e036',
 'freeze':'5c3199380ed8e6502384f5a3790104291f7723b8a086911aa6c53606de99b7dc',
 'manifest':'21402d45b3d1796c99ff8e5c51e14953a1f2bb4eae51a4eed70facdd91d1696a',
}
def need(ok,message):
    if not ok:raise AssertionError(message)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def binding(x):
    p=Path(x['path']);need(p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],'Descriptor mismatch: '+str(p))
def main():
    start=time.perf_counter();need(not (ARM/'run01').exists(),'Scientific execution already exists')
    for key,p in [('source',SOURCE),('protocol',PROTOCOL),('freeze',PRE/'prepared_freeze.json'),('manifest',PRE/'input_manifest.json')]:
        need(sha(p)==TRUST[key],'Trusted '+key+' mismatch')
    source=SOURCE.read_text(encoding='utf-8');tree=ast.parse(source)
    pins=None
    for node in tree.body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PINS' for t in node.targets):pins=ast.literal_eval(node.value)
    need(isinstance(pins,dict) and len(pins)==15,'Source pin dictionary')
    freeze=read(PRE/'prepared_freeze.json');manifest=read(PRE/'input_manifest.json')['files']
    need(freeze['source_sha256']==TRUST['source'] and freeze['protocol_sha256']==TRUST['protocol'] and freeze['manifest_sha256']==TRUST['manifest'],'Freeze links')
    need(freeze['bindings']==len(manifest)==53 and freeze['copies']==14 and freeze['optimizer_calls']==freeze['cut_arithmetic']==0,'Prepared denominator')
    need(freeze['separate_execution_GO_required'] is True,'Separate execution gate')
    bypath={str(Path(x['path']).resolve()).casefold():x for x in manifest};need(len(bypath)==53,'Unique input paths')
    for x in manifest:binding(x)
    for rel,digest in pins.items():
        path=ROOT/rel;need(sha(path)==digest,'Source hardcoded pin')
        need(bypath[str(path.resolve()).casefold()]['sha256']==digest,'Pinned source not bound')
    copy=read(PRE/'copy_provenance.json');need(copy['all_model_and_selection_bytes_unchanged'] and len(copy['copies'])==14,'Copy manifest scope')
    copied=[]
    for x in copy['copies']:
        for key in ('source','copy'):
            binding(x[key]);need(bypath[str(Path(x[key]['path']).resolve()).casefold()]==x[key],'Copy descriptor not manifest bound')
        need(Path(x['source']['path']).read_bytes()==Path(x['copy']['path']).read_bytes(),'Byte copy differs')
        copied.append(str(Path(x['copy']['path']).relative_to(PRE)))
    expected={'candidate_schedule.json','joint/column_maps.json','floor_result.json','continuous_control.npz'}
    expected|={w+'/'+name for w in ('identity','days_321') for name in ('matrix.npz','bounds.npz','integrality.npz','model_metadata.json','derivations.json')}
    need({x.replace('\\','/') for x in copied}==expected,'Exact fourteen-copy membership')
    old=ROOT/'results/research_next/common_commitment/prepared'
    for name in ['joint/column_maps.json']+[w+'/'+n for w in ('identity','days_321') for n in ('matrix.npz','bounds.npz','integrality.npz','model_metadata.json')]:
        need((PRE/name).read_bytes()==(old/name).read_bytes(),'Original accepted-control model byte relation')
        need(str((old/name).resolve()).casefold() in bypath,'Original model not bound')
    plan=read(PRE/'plan.json')
    need(plan['worlds']==['identity','days_321'] and plan['cut_count']==2 and plan['phase_seconds']==120,'Fixed scientific denominator/budget')
    need(plan['selection']=='exact archived variable sources and hourly active label; no reselection','Fixed source selections')
    need(plan['optimizer_calls']==plan['union_recomputations']==0 and plan['control_point_rounded'] is False and plan['no_old_full_point_replay'] is True,'Scope controls')
    need(plan['full_common_verdict']=='UNKNOWN','Full common scope')
    oldreview=read(ROOT/'results/research_next/common_commitment/INDEPENDENT_POSTRUN_REVIEW.json')
    need(oldreview['status']=='PASS_INDEPENDENT_POSTRUN_REVIEW' and oldreview['posthoc_continuous_check']['expanded_pass'] and oldreview['posthoc_continuous_check']['point_changed_or_rounded'] is False,'Inherited exact continuous admission')
    census=read(ROOT/'results/research_next/common_commitment/INDEPENDENT_LP_NONBINARY_STATES.json')
    need(census['raw_solution_sha256']==sha(PRE/'continuous_control.npz'),'Continuous control identity')
    floorreview=read(ROOT/'results/research_next/union_energy_floor/INDEPENDENT_REVIEW.json')
    need(floorreview['status']=='INDEPENDENT_EXACT_FIXED_SCHEDULE_OBSTRUCTION_PASS','Inherited fixed union proof status')
    need([x['world'] for x in floorreview['worlds']]==['identity','days_321'] and all(x['fixed_schedule_rejected'] for x in floorreview['worlds']),'Fixed union two-world proof scope')
    for w in ('identity','days_321'):
        data=read(PRE/w/'derivations.json')
        need(data['world']==w and len(data['variables'])==6888 and len(data['hourly'])==168,'Archived selection record counts')
        need([x['column'] for x in data['variables']]==list(range(6888)) and [x['hour'] for x in data['hourly']]==list(range(168)),'Archived record coordinates')
        need(all(x['active'] in ('individual_lower_sum','balance_minus_other_upper') for x in data['hourly']),'Recognized frozen branch labels')
    fixtures=read(ARM/'SYNTHETIC_CHECKS.json')
    need(fixtures['status']=='PASS_INVENTED_ARITHMETIC_ONLY' and fixtures['count']==len(fixtures['checks'])==11 and all(x['pass_'] for x in fixtures['checks']),'Invented fixture receipt')
    need(fixtures['source_sha256']==TRUST['source'] and fixtures['fixture_sha256']==sha(ARM/'SYNTHETIC_CHECKS.py'),'Fixture source provenance')
    # No helper import or actual arithmetic: these are already read static source obligations.
    obligations=['weight=1/abs(a)','need(weight>=0','need(set(q)-{j}<=U',"need(set(coeff)<=U",'need(slack>=0',"fixed[j]!=1",'new_derived_row_expansion=0']
    need(all(token in source for token in obligations),'Reviewed source obligation missing')
    for x in manifest:binding(x)
    for key,p in [('source',SOURCE),('protocol',PROTOCOL),('freeze',PRE/'prepared_freeze.json'),('manifest',PRE/'input_manifest.json')]:need(sha(p)==TRUST[key],'Close transport changed')
    need(not (ARM/'run01').exists(),'Execution started during prepared audit')
    report=dict(status='PASS_INDEPENDENT_SOURCE_AND_PREPARED_GATE',utc=datetime.now(timezone.utc).isoformat(),reviewer_source_sha256=sha(__file__),trusted=TRUST,
        bindings_checked_at_entry_and_close=53,captured_copies_checked_byte_for_byte=14,original_control_model_maps_byte_relations=9,
        fixed_worlds=['identity','days_321'],cut_denominator=2,archived_hours_per_world=168,archived_generation_bound_records_per_world=6888,
        prior_full_point_membership_inherited_by_hash=True,actual_cut_arithmetic=0,scientific_array_decodes=0,producer_imports=0,optimizer_calls=0,
        synthetic_tests_reexecuted=0,scientific_run_absent_at_entry_and_close=True,source_theory_verdict='No blocker; original expanded-row implication, not universal common rejection',
        conditional_superset_verdict='Requires actual surviving negative coefficients to occur only at frozen union one-bits',
        elapsed_seconds=time.perf_counter()-start)
    with (ARM/'independent_prepared_review.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps(report),flush=True)
if __name__=='__main__':main()
