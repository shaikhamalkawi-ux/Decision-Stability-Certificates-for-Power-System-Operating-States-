"""Schema-only source and byte gate. No scientific payload JSON is parsed."""
from pathlib import Path
import ast, hashlib, json, time
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[3]
ARM=ROOT/'results/research_next/orlib_native_compare_schema2'
OLD=ROOT/'results/research_next/orlib_native_compare'
SOURCE='e9f1065fbd47e9d5b7a67afad92fc6a18816cade310b87c8f1c66a49814c389f'
PROTOCOL='f4ac9b47e6b653c7dfc5a42b6a6c98831204a83c51604355f7676bab87fea775'
MANIFEST='ea2a05148c0d0b23b2c59faea9f0afcfd4a3b386e6e738adb97ca1b4610ab829'
def need(ok,why):
    if not ok: raise AssertionError(why)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def verify(items):
    for e in items:
        p=Path(e['path']); need(p.stat().st_size==e['bytes'] and sha(p)==e['sha256'],str(p))
def main():
    start=time.perf_counter(); run=ARM/'run01'
    need(not run.exists(),'No comparison before gate')
    source=ROOT/'src/researchnext_orlib_native_compare_schema2.py'
    original=ROOT/'src/researchnext_orlib_native_compare.py'
    protocol=ROOT/'docs/research_next/ORLIB_NATIVE_COMPARE_SCHEMA2_PROTOCOL.md'
    manifest=ARM/'prepared/manifest.json'
    need(sha(source)==SOURCE and sha(protocol)==PROTOCOL and sha(manifest)==MANIFEST,'Trusted current pins')
    need(sha(original)=='83ee49f623b9bb9b90a27ecbf808e305369ae02046add59a643afb002c0db507','Original preserved')
    old_functions={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(original.read_text()).body if isinstance(n,ast.FunctionDef)}
    new_functions={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(source.read_text()).body if isinstance(n,ast.FunctionDef)}
    need(set(old_functions)==set(new_functions),'No added/removed functions')
    changed=sorted(n for n in old_functions if old_functions[n]!=new_functions[n])
    need(changed==['alias_name','prepare','self_test'],'Only reviewed function deltas')
    # Full text diff was read independently before this check. In particular, compare,
    # compare_parsed, affine, canon, native, set_bounds and run are AST-identical.
    m=read(manifest); need(len(m['inputs'])==11 and len(m['copies'])==5,'Descriptor counts')
    need(m['source_sha256']==SOURCE and m['protocol_sha256']==PROTOCOL and m['comparison_runs']==0,'Manifest role')
    verify(m['inputs']+m['copies'])
    copies={Path(e['path']).name:e for e in m['copies']}
    need(set(copies)=={'official_completion.json','raw.json','parsed.json','model.json','normal.json'},'Copy names')
    for name,e in copies.items():
        need(Path(e['path']).read_bytes()==(OLD/'prepared'/name).read_bytes(),'Exact old payload: '+name)
    need({p.name for p in (ARM/'prepared').iterdir()}==set(copies)|{'manifest.json'},'Prepared layout')
    fixture=read(ARM/'synthetic_controls.json')
    need(fixture['status']=='PASS' and fixture['checks']==10 and fixture['source_sha256']==SOURCE and fixture['protocol_sha256']==PROTOCOL,'Fixture receipt')
    need(fixture['scientific_arrays_read']==fixture['comparison_runs']==fixture['optimizer_calls']==0,'Synthetic only')
    old_snapshot={n:sha(OLD/'run01'/n) for n in ('started.json','failure.json')}
    need(old_snapshot['failure.json']=='819f59c1b1918bf4672a4efc39f92e767c9601ec5492e824b2edbe36b08a673c','Preserved failure pin')
    verify(m['inputs']+m['copies'])
    need(sha(manifest)==MANIFEST and not run.exists(),'Close gate unchanged/unexecuted')
    need(old_snapshot=={n:sha(OLD/'run01'/n) for n in old_snapshot},'Original records unchanged')
    result=dict(status='PASS_INDEPENDENT_SCHEMA2_SOURCE_AND_PREPARED_GATE',utc=datetime.now(timezone.utc).isoformat(),
        source_sha256=SOURCE,protocol_sha256=PROTOCOL,manifest_sha256=MANIFEST,
        reviewer_source_sha256=sha(Path(__file__)),descriptors_verified_twice=16,
        exact_old_payload_relations=5,changed_functions=changed,
        scientific_comparison_functions_ast_unchanged=True,synthetic_receipt_checks=10,
        old_run_snapshot=old_snapshot,scientific_payloads_parsed=0,producer_imports=0,
        comparison_runs=0,Julia_calls=0,optimizer_calls=0,run_absent_at_entry_and_close=True,
        nominal_equivalence='NOT_ESTABLISHED',expanded_equivalence='NOT_ESTABLISHED',elapsed_seconds=time.perf_counter()-start)
    with (ARM/'INDEPENDENT_PREPARED_REVIEW.json').open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2);f.write('\n')
    print(result['status'],result['elapsed_seconds'])
if __name__=='__main__':main()
