"""Byte-only recovery admission; no cut arithmetic, scientific imports or OS probe."""
import argparse
import ast
import csv
from datetime import datetime, timezone
import difflib
import hashlib
import json
from pathlib import Path
import time

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
ARM=ROOT/'results/research_next/common_refinement_jobs'
PRE=ARM/'prepared'
OLD=ROOT/'results/research_next/common_refinement_batch'
SOURCE='fa1548f4d7765ac84e2f74a06df2fde640c713b85a1c27bdc29c99f3bb1b2973'
PROTOCOL='14f9a4f2fb11966eec851e1c69187945f2daa523f1d5fd1a5b389900ecdf7b1f'
DIFF='f9bb269f95a2e44a7126c8daabc83bfd88b4fa603dadc8944a6571e8dca0d50e'
MATH='205b8118a0a01d5cb63a1435b5b8dbdc0089ca1aad7e2cbb153b9117ac63738a'
ENCODING='fa336a6b919b50df691f4ec01b8ef70cadd63e7f800f0fb4b3298c783c642a0f'

def need(x,why):
    if not x: raise ValueError(why)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def key(p): return str(Path(p).resolve()).casefold()
def bound(p):
    p=Path(p).resolve();b=p.read_bytes()
    return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def validate(items):
    need(len({key(x['path']) for x in items})==len(items),'Unique bound inputs')
    for x in items: need(bound(x['path'])==x,'Unchanged binding '+x['path'])
def declarations(tree):
    return {n.targets[0].id:n.value for n in tree.body if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)}

def main(args):
    started=time.perf_counter();target=OUT/'prepared_review.json'
    need(not target.exists() and not (ARM/'run01').exists(),'Fresh independent gate; no execution')
    source=ROOT/'src/researchnext_common_refinement_jobs.py'
    oldsource=ROOT/'src/researchnext_common_refinement_batch.py'
    protocol=ROOT/'docs/research_next/COMMON_REFINEMENT_JOBS_PROTOCOL.md'
    pins={source:SOURCE,protocol:PROTOCOL,ARM/'SOURCE_DIFF.diff':DIFF,
          PRE/'prepared_freeze.json':args.freeze_sha256,PRE/'input_manifest.json':args.manifest_sha256,
          oldsource:'f7f79ecca154169832c8739d9c17889c5c5993aa460f6d115c60018371'}
    for p,h in pins.items(): need(sha(p)==h,'External source/freeze pin')
    freeze=read(PRE/'prepared_freeze.json');items=read(PRE/'input_manifest.json')['files']
    need(freeze['manifest_sha256']==args.manifest_sha256 and freeze['source_sha256']==SOURCE and freeze['protocol_sha256']==PROTOCOL,'Complete freeze links')
    need(len(items)==freeze['bindings']==args.bindings,'Trusted binding denominator');validate(items)
    indexed={key(x['path']):x for x in items}
    source_text=source.read_text(encoding='utf-8-sig');old_text=oldsource.read_text(encoding='utf-8-sig')
    expected=''.join(difflib.unified_diff(old_text.splitlines(keepends=True),source_text.splitlines(keepends=True),
                                       fromfile='closed predecessor f7f79ecca154',tofile='additive jobs recovery'))
    need(expected==(ARM/'SOURCE_DIFF.diff').read_text(encoding='utf-8-sig'),'Complete exact source diff')
    tree,oldtree=ast.parse(source_text),ast.parse(old_text)
    nodes={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
    oldnodes={n.name:n for n in oldtree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
    same_functions=('encoding_for','search_model','actual_transport','solver_call','duplicate_candidate','final_admission','ledger_snapshot','OwnedWindowsJob')
    for name in same_functions:
        need(ast.dump(nodes[name],include_attributes=False)==ast.dump(oldnodes[name],include_attributes=False),'Unchanged recipe/integration function '+name)
    need('sparse_proof' not in nodes and 'anchor_check' not in nodes,'No seed reconstruction functions')
    dec,olddec=declarations(tree),declarations(oldtree)
    for name in ('NB','STATE_START','STATE_STOP','TAU','PHASE','ROUNDS','MAX_CALLS','MAX_BITS','LIMITS','CLOSURE_MARGIN','C','THERMAL','WORLD_FILES','JOINT_FILES','HELPERS'):
        need(ast.dump(dec[name],include_attributes=False)==ast.dump(olddec[name],include_attributes=False),'Unchanged scientific constant/helper roster '+name)
    sourcepins=ast.literal_eval(dec['PINS']);helpers=ast.literal_eval(dec['HELPERS'])
    for rel,digest in list(sourcepins.items())+list(helpers.values()):
        need(indexed[key(ROOT/rel)]['sha256']==digest,'Exact source-declared frozen dependency')
    for folder,count in ((ROOT/'results/research_next/common_master_bounded/prepared',239),
                         (ROOT/'results/research_next/common_phase1/prepared',292),(OLD/'prepared',355)):
        historical=read(folder/'input_manifest.json')['files'];need(len(historical)==count,'Historical denominator')
        need(all(indexed.get(key(x['path']))==x for x in historical),'Complete inherited frozen input closure')
    for folder,count in ((ROOT/'results/research_next/common_phase1',12),(OLD,688)):
        with (folder/'producer_output_inventory.csv').open(encoding='utf-8-sig',newline='') as f: historic=list(csv.DictReader(f))
        need(len(historic)==count,'Closed output denominator')
        for x in historic:
            p=ROOT/x['path'];want=dict(path=str(p.resolve()),bytes=int(x['bytes']),sha256=x['sha256'])
            need(indexed.get(key(p))==want,'Complete historical output closure')
    # Independently specified copy roles; direct byte equality only, never decompress a proof.
    expected_copies={}
    for world in ('identity','days_321'):
        for name in ('matrix.npz','bounds.npz','integrality.npz','model_metadata.json','native_inputs.npz','permutation.csv','row_metadata.csv.gz','native_spec.json'):
            expected_copies[key(PRE/world/name)]=key(OLD/'prepared'/world/name)
    for name in ('matrix.npz','bounds.npz','integrality.npz','column_maps.json','row_origins.json'):
        expected_copies[key(PRE/'joint'/name)]=key(OLD/'prepared/joint'/name)
    for name in ('master.json.gz','premises.json','gen.csv','identity_cut.json','days_321_cut.json','phase_model.npz',
                 'endpoint_map.json.gz','column_encoding.json.gz','control_raw_solution.npz','inherited_fixed_schedule.json','anchor_certificate.json.gz','symbolic_seed_maps.json'):
        expected_copies[key(PRE/name)]=key(OLD/'prepared'/name)
    for world in ('identity','days_321'):
        for hour in range(168):
            for typ in ('proof','encoding'):
                name=f'{world}_{hour:03d}_{typ}.json.gz'
                expected_copies[key(PRE/'seeds'/name)]=key(OLD/'run01/seeds'/name)
    expected_copies[key(PRE/'inherited_seed_completion.json')]=key(OLD/'run01/seeds/completion.json')
    expected_copies[key(PRE/'inherited_initial_duplicate_set.json')]=key(OLD/'run01/initial_duplicate_set.json')
    copies=read(PRE/'copy_provenance.json')['copies']
    need(len(copies)==len(expected_copies)==freeze['copies']==707,'707 exact inherited payloads')
    need({key(x['copy']['path']):key(x['original']['path']) for x in copies}==expected_copies,'Every precise source/destination role')
    for x in copies:
        a,b=x['original'],x['copy']
        need(indexed[key(a['path'])]==a and indexed[key(b['path'])]==b,'Both endpoints bound')
        need(a['bytes']==b['bytes'] and a['sha256']==b['sha256'] and Path(a['path']).read_bytes()==Path(b['path']).read_bytes(),'Direct source byte equality')
    index=read(PRE/'inherited_seed_index.json')
    need(index['cases']==336 and index['no_seed_arithmetic'] and index['mathematical_review_sha256']==MATH and index['encoding_review_sha256']==ENCODING,'Complete admitted inheritance')
    records=index['records'];need(len(records)==336,'Exact seed count')
    need([(r['world'],r['hour']) for r in records]==[(w,t) for w in ('identity','days_321') for t in range(168)],'Prespecified 336 order')
    for r in records:
        need(r['kind']=='seed','No new adaptive proof')
        for kind in ('proof','encoding'):
            p=PRE/'seeds'/f"{r['world']}_{r['hour']:03d}_{kind}.json.gz"
            need(r[kind]==indexed[key(p)],'Exact copied seed index binding')
    duplicate=read(PRE/'inherited_initial_duplicate_set.json')
    old_duplicate=read(OLD/'run01/initial_duplicate_set.json')
    need(duplicate==old_duplicate and duplicate['initialized_before_first_master'] and len(duplicate['states'])==1,'Identical original duplicate entry')
    prev=duplicate['states'][0]
    need(prev['origin']=='closed_initial_nominee' and len(prev['values'])==12096 and all(type(x)is int and x in (0,1) for x in prev['values']),'Full exact duplicate bits, not nominee generation')
    need(hashlib.sha256(bytes(prev['values'])).hexdigest()==prev['sha256'],'Original duplicate byte identity')
    proofreview=read(ROOT/'results/research_next/common_refinement_math_review/review01/review.json')
    encodereview=read(ROOT/'results/research_next/common_refinement_batch_independent_review/postrun_failure_review.json')
    need(proofreview['status']=='PASS_INDEPENDENT_NEW_MATHEMATICS' and proofreview['complete_seed_family_independently_verified'] and proofreview['actual_saved_seed_proof_count']==336,'Previously admitted proof family')
    need(encodereview['status']=='PASS_ZERO_OPTIMIZER_CLOSURE_AND_REQUESTED_ENCODING' and encodereview['requested_encoding_necessary_implications']==336 and encodereview['optimizer_attempts']==0,'Previously admitted requested encodings/no search')
    plan=read(PRE/'plan.json');oldplan=read(OLD/'prepared/plan.json')
    for field in ('runtime','phase_seconds','rounds','maximum_optimizer_calls','limits','closure_margin','initial_master_inherited_without_reassembly','scientific_cut_evaluations','old_witness_replays'):
        need(plan[field]==oldplan[field],'Unchanged declared runtime/budget '+field)
    need(plan['inherited_seed_cases']==336 and 'all handles before assignment' in plan['ownership'],'Inherited scope/ownership declaration')
    tests=read(ARM/'synthetic_tests.json')
    need(tests['source_sha256']==SOURCE and tests['protocol_sha256']==PROTOCOL and tests['status']=='PASS' and len(tests['checks'])==4,'Current focused fixture provenance')
    need(all(tests[k]==0 for k in ('scientific_inputs_read','seed_recomputations','optimizer_calls','backend_imports','real_processes_launched')),'Invented-only tests')
    need(all(freeze[k]==0 for k in ('optimizer_calls','scientific_cut_evaluations','backend_imports')) and freeze['inherited_seed_cases']==336 and freeze['separate_execution_GO_required'],'Copy-only freeze scope')
    validate(items)
    for p,h in pins.items(): need(sha(p)==h,'Closing source/freeze/manifest gate')
    need(not (ARM/'run01').exists(),'No execution at close')
    report={'status':'PASS_SOURCE_DIFF_AND_PREPARED_BYTE_PROVENANCE','utc':datetime.now(timezone.utc).isoformat(),
            'reviewer_sha256':sha(__file__),'elapsed_seconds':time.perf_counter()-started,
            'source_sha256':SOURCE,'protocol_sha256':PROTOCOL,'diff_sha256':DIFF,
            'freeze_sha256':args.freeze_sha256,'manifest_sha256':args.manifest_sha256,
            'input_bindings':len(items),'exact_payload_copies':707,'copied_seed_proofs':336,'copied_requested_encodings':336,
            'source_functions_AST_identical':list(same_functions),'scientific_constants_and_helper_pins_unchanged':True,
            'captured_helper_loader_source_reviewed':True,'all_handles_before_assignment_source_reviewed':True,
            'separate_jobs_membership_and_unassigned_handle_cleanup_source_reviewed':True,
            'controller_worker_final_four_file_gate_source_reviewed':True,
            'all_files_unchanged':True,'run_absent_entry_close':True,'seed_math_replayed':False,
            'producer_or_helper_imports':0,'scientific_coefficient_evaluations':0,'optimizer_calls':0,'OS_process_probes':0,
            'encoder_helper_author_disclosed':True,'future_actual_backend_and_lifecycle_still_require_review':True,
            'limitations':['Harmless observed probe covers SCIP interpreter, not a live optimizer timeout or LP interpreter.',
                           'Incomplete pre-GO handle capture remains unverified cleanup and forces failure; no successful closure assumed.',
                           'Copied proof mathematics is inherited from pinned independent reviews; no new proof or nominal-to-expanded equivalence asserted.'],
            'execution_authorization':'Separate root GO required.'}
    with target.open('x',encoding='utf-8') as f: json.dump(report,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({'status':report['status'],'report_sha256':sha(target),'elapsed_seconds':report['elapsed_seconds']}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--freeze-sha256',required=True);p.add_argument('--manifest-sha256',required=True);p.add_argument('--bindings',required=True,type=int)
    main(p.parse_args())
