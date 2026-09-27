"""Prepared byte/receipt gate only; never parse scientific coefficient payloads."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import time
ROOT=Path(__file__).resolve().parents[3]
ARM=ROOT/'results/research_next/orlib_native_compare';PRE=ARM/'prepared'
MANIFEST='fe20e2535ad3f36e669dbafb1ff9d588d791f0e8c04bbedfa0557bc1830d8b29'
SOURCE='83ee49f623b9bb9b90a27ecbf808e305369ae02046add59a643afb002c0db507'
PROTOCOL='d0667b109ef0ceb50022726a68675b67c3b46f438e764d76402dcd3267701ba9'
def need(ok,msg):
    if not ok:raise AssertionError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def desc(x):
    p=Path(x['path']);b=p.read_bytes();need(len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256'],'Changed admitted bytes '+str(p));return b
def main():
    began=time.perf_counter();need(not (ARM/'run01').exists(),'Run must remain absent')
    need(sha(PRE/'manifest.json')==MANIFEST,'Trusted prepared manifest')
    m=read(PRE/'manifest.json');need(m['source_sha256']==SOURCE and m['protocol_sha256']==PROTOCOL and m['comparison_runs']==0,'Reviewed source/protocol and zero-comparison gate')
    need(len(m['inputs'])==7 and len(m['copies'])==5,'Fixed descriptor denominator')
    items=m['inputs']+m['copies'];need(len({x['path'].casefold() for x in items})==12,'Unique descriptors')
    for x in items:desc(x)
    expected=['official_completion.json','raw.json','parsed.json','model.json','normal.json']
    for original,copied,name in zip(m['inputs'][:5],m['copies'],expected):
        need(Path(copied['path']).resolve()==(PRE/name).resolve(),'Exact copied payload role')
        need(desc(original)==desc(copied),'Exact captured payload equality')
    need(Path(m['inputs'][5]['path']).resolve()==(ROOT/'src/researchnext_orlib_native_compare.py').resolve() and m['inputs'][5]['sha256']==SOURCE,'Comparator source identity')
    need(Path(m['inputs'][6]['path']).resolve()==(ROOT/'docs/research_next/ORLIB_NATIVE_COMPARE_PROTOCOL.md').resolve() and m['inputs'][6]['sha256']==PROTOCOL,'Protocol identity')
    need(m['inputs'][3]['sha256']=='5abc7c12289d6428081f49646553863abaa041abfd4bac6215d7d49130b2f725','Frozen identity/native-penalized model')
    need(m['inputs'][4]['sha256']=='be57cd1fd925fb5c106b8e90979dcc866c0b27068b368ec018e4068d03067df8','Frozen normalized case')
    completion=read(PRE/'official_completion.json')
    need(completion['status']=='OFFICIAL_RAW_EXPORT_COMPLETE_PENDING_COMPARISON','Raw export completion status')
    need(completion['optimizer_calls']==0 and completion['native_build_attempts']==completion['native_read_attempts']==1 and completion['inputs_unchanged'],'One raw native read/build, no optimizer')
    need(completion['raw_model_sha256']==m['inputs'][1]['sha256'] and completion['parsed_instance_sha256']==m['inputs'][2]['sha256'],'Receipt binds exact copied raw/parsed payloads')
    need({p.name for p in PRE.iterdir() if p.is_file()}==set(expected+['manifest.json']),'Prepared file layout')
    for x in items:desc(x)
    need(sha(PRE/'manifest.json')==MANIFEST and not (ARM/'run01').exists(),'Final transport and run absence')
    report=dict(status='PASS_INDEPENDENT_PREPARED_BYTE_GATE',utc=datetime.now(timezone.utc).isoformat(),reviewer_source_sha256=sha(__file__),manifest_sha256=MANIFEST,
        comparator_source_sha256=SOURCE,protocol_sha256=PROTOCOL,original_descriptors=7,captured_copies=5,descriptors_checked_at_entry_and_close=12,
        exact_payload_byte_relations=5,official_export_receipt_sha256=m['inputs'][0]['sha256'],official_read_attempts=1,official_build_attempts=1,
        scientific_coefficient_payloads_parsed=0,comparison_runs=0,producer_imports=0,Julia_calls=0,optimizer_calls=0,run_absent_at_entry_and_close=True,
        verdict_scope='Prepared bytes/receipt/source roles only; no native coefficient equivalence claim',elapsed_seconds=time.perf_counter()-began)
    with (ARM/'INDEPENDENT_PREPARED_REVIEW.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps(report),flush=True)
if __name__=='__main__':main()
