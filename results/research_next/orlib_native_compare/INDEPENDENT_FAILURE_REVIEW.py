"""Closed failed-comparison audit: hashes, ledger and semantic names only."""
from pathlib import Path
import json, hashlib, time
from collections import Counter
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
ARM = ROOT / 'results/research_next/orlib_native_compare'
PRE = ARM / 'prepared'
RUN = ARM / 'run01'
MANIFEST = 'fe20e2535ad3f36e669dbafb1ff9d588d791f0e8c04bbedfa0557bc1830d8b29'
SOURCE = '83ee49f623b9bb9b90a27ecbf808e305369ae02046add59a643afb002c0db507'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def need(ok, why):
    if not ok: raise AssertionError(why)
def bindings(items):
    for e in items:
        p=Path(e['path']); b=p.read_bytes()
        need(len(b)==e['bytes'] and hashlib.sha256(b).hexdigest()==e['sha256'], str(p))
def reported_alias(a):
    # Independently transcribed naming contract; no coefficient/function evaluation.
    f,k=a['family'],a['key']
    state={'is_on':'U','switch_on':'Y','switch_off':'Z','startup':'D'}
    if f in state: return f'{state[f]}:{k[0]}:{k[1]-1}'
    if f in ('prod_above','mfg'): return f'{"Q" if f=="prod_above" else "mfg"}:{k[1]}:{k[2]-1}'
    if f=='reserve': return f'R:{k[2]}:{k[3]-1}'
    if f=='segprod': return f'S:{k[1]}:{k[2]-1}:{k[3]-1}'
    system={'curtail':'C','reserve_shortfall':'F','net_injection':'N'}
    need(f in system,'Unexpected semantic family')
    return f'{system[f]}:{k[2]-1}'

def main():
    start=time.perf_counter()
    need(sha(PRE/'manifest.json')==MANIFEST,'Trusted manifest')
    manifest=read(PRE/'manifest.json'); bindings(manifest['inputs']+manifest['copies'])
    need(sha(ROOT/'src/researchnext_orlib_native_compare.py')==SOURCE,'Source')
    snapshot={p.name:sha(p) for p in RUN.iterdir() if p.is_file()}
    need(set(snapshot)=={'started.json','failure.json'},'Exact failed-run layout')
    started=read(RUN/'started.json'); failure=read(RUN/'failure.json')
    need(started['manifest_sha256']==MANIFEST and started['source_sha256']==SOURCE,'Started pins')
    need(started['optimizer_calls']==0,'Zero optimizer')
    need(failure['exception_type']=='ValueError' and failure['message']=='Exactly declared native projection','Failure cause')
    need(failure['no_retry'] and failure['no_equivalence_claim'],'Failure scope')
    need(0<=failure['elapsed_seconds']<120,'Failure timing')
    # Parsing the JSON container is unavoidable; only variable/alias/name metadata
    # is accessed. Constraints, numerical bounds, parsed-instance values and objective
    # are neither traversed nor compared.
    raw=read(PRE/'raw.json'); model=read(PRE/'model.json')
    aliases=raw['semantic_aliases']; ids=[v['index'] for v in raw['variables']]
    names=[reported_alias(a) for a in aliases]
    need(len(ids)==len(set(ids))==len(aliases)==len(set(names))==2712,'Native unique inventory')
    need({a['variable'] for a in aliases}==set(ids),'Complete alias coverage')
    columns=[c['name'] for c in model['columns']]
    need(len(columns)==len(set(columns))==2472,'Adapter inventory')
    omitted={n for n in names if n.startswith('mfg:')}
    need(len(omitted)==240,'Declared omitted inventory')
    expected=set(columns)|omitted
    missing=sorted(expected-set(names)); extra=sorted(set(names)-expected)
    wanted_extra={f'{f}:{t}' for f in ('C','F','N') for t in range(24)}
    wanted_missing={f'{f}:system:{t}' for f in ('C','F','N') for t in range(24)}
    need(set(extra)==wanted_extra and set(missing)==wanted_missing,'Only the 72 system aliases differ')
    diagnostic_names={n.replace(':',':system:',1) if n in wanted_extra else n for n in names}
    need(diagnostic_names==expected,'Naming-only diagnostic restores inventory, not model equivalence')
    bindings(manifest['inputs']+manifest['copies'])
    need(sha(PRE/'manifest.json')==MANIFEST,'Manifest unchanged')
    need(snapshot=={p.name:sha(p) for p in RUN.iterdir() if p.is_file()},'Producer outputs unchanged')
    out=dict(status='PASS_INDEPENDENT_FAILURE_BOUNDARY_AND_NAME_DIAGNOSIS',utc=datetime.now(timezone.utc).isoformat(),
        reviewer_source_sha256=sha(Path(__file__)),manifest_sha256=MANIFEST,source_sha256=SOURCE,
        input_descriptors_checked=12,producer_outputs=snapshot,producer_elapsed_seconds=failure['elapsed_seconds'],
        native_variables=2712,adapter_columns=2472,declared_omitted_names=240,
        native_family_counts=dict(Counter(a['family'] for a in aliases)),
        adapter_family_counts=dict(Counter(n.split(':')[0] for n in columns)),
        missing_names=missing,extra_names=extra,corrected_name_set_matches=True,
        diagnosis='System-family mapping omitted the literal system component; actual adapter names retain it.',
        coefficient_comparisons=0,producer_imports=0,comparison_retries=0,Julia_calls=0,optimizer_calls=0,
        parsed_parameter_comparison_verdict='NOT_PERSISTED_BY_FAILED_PRODUCER',
        nominal_native_equivalence='NOT_ESTABLISHED',expanded_native_equivalence='NOT_ESTABLISHED',
        elapsed_seconds=time.perf_counter()-start)
    with (ARM/'INDEPENDENT_FAILURE_REVIEW.json').open('x',encoding='utf-8') as f:
        json.dump(out,f,indent=2,allow_nan=False);f.write('\n')
    print(out['status'],out['elapsed_seconds'])
if __name__=='__main__': main()
