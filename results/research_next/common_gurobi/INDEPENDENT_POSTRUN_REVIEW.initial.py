"""Independent closed failure/readback audit; never imports Gurobi or producer."""
from pathlib import Path
import csv,hashlib,importlib.util,json,sys,time,re
from datetime import datetime
sys.dont_write_bytecode=True
T=time.perf_counter();ROOT=Path(__file__).resolve().parents[3];ARM=ROOT/'results/research_next/common_gurobi';PRE=ARM/'prepared';RUN=ARM/'run01'
def req(b,s):
 if not b:raise ValueError(s)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def verify(items,relative=False):
 seen=set()
 for r in items:
  p=ROOT/r['path'] if relative else Path(r['path']);key=str(p.resolve()).casefold();req(key not in seen,'duplicate binding');seen.add(key)
  b=p.read_bytes();req(len(b)==int(r['bytes']) and hashlib.sha256(b).hexdigest()==r['sha256'],'changed '+str(p))
 return seen
inventory=ARM/'producer_output_inventory.csv';req(sha(inventory)=='a604995726f1ca5ae4928bdc65c60e51034fae52add32fca98018876cd4dc767','inventory')
outputs=list(csv.DictReader(inventory.read_text(encoding='utf-8-sig').splitlines()));req(len(outputs)==42,'outputs42');verify(outputs,True)
manifest=PRE/'input_manifest.json';freeze=PRE/'prepared_freeze.json'
req(sha(manifest)=='a7f5dd3ca95663543460f01c0045c7e62b430aed7a7d1facd6f370aa2f07eb07','manifest')
req(sha(freeze)=='c91dac7c583a42493e0eae6f9b3b493140a0997661bb748a08a3d08d168cb926','freeze')
items=read(manifest)['files'];req(len(items)==86,'inputs86');verify(items)
req(sha(ARM/'INDEPENDENT_PREPARED_REVIEW.json')=='9f7fe1f6bef0647283dc5f64d1f7b9786976398971d6ae69e27f40822fdd8c6d','inherited new-map prepared audit')
closure=read(RUN/'failure_closure.json');failure=read(RUN/'execution_failure.json');start=read(RUN/'execution_started.json');admit=read(RUN/'admission.json');plan=read(PRE/'plan.json')
req(sha(RUN/'failure_closure.json')=='22401b45326159af3aec4821f9b970ec90ad65db326be35c5661b62108443209','closure')
req(sha(ARM/'READOUT.md')=='fb16e6f9be9fdd2819480f93701bd248d4f0b53e265ca9f89e66ccb826b6076e','readout')
req(failure['stage']=='sole_optimize' and failure['error_type']=='GurobiError' and failure['backend_errno']==10010,'failure scope')
l=failure['call_ledger'];req(l['attempted']==1 and l['returned']==0 and l['actual_seconds']==closure['invocation_seconds'],'ledger')
req(l['last_admission_remaining_seconds']>=1805 and admit['admitted'] and admit['remaining_seconds']>=1805,'actual guard')
req(closure['optimizer_invocations_attempted']==1 and closure['optimizer_invocations_returned']==0 and closure['process_exit_code']==1,'closure ledger')
req(closure['scientific_verdict']==failure['scientific_verdict']=='UNKNOWN' and closure['scientific_search_established'] is False and closure['numeric_solver_status_returned'] is False,'scientific status')
req(closure['accepted_points']==closure['exact_negative_certificates']==0,'no proofs')
req(closure['no_retry'] and closure['no_fallback'] and closure['no_license_change'],'no retry')
expected={'admission.json','backend_readback.json','backend_readback.npz','call_ready.json','execution_failure.json','execution_started.json','failure_closure.json','private_log_receipt.json'}
req({p.name for p in RUN.iterdir()}==expected,'exact8 public run files/no solution')
req(start['expected_freeze_sha256']==sha(freeze) and start['source_sha256']==read(freeze)['source_sha256'],'actual launch provenance')
span=(datetime.fromisoformat(failure['utc'])-datetime.fromisoformat(start['utc'])).total_seconds();req(abs(span-closure['execution_marker_to_error_timestamp_seconds'])<1e-9,'timestamp span')
req(closure['timestamp_span_is_not_complete_perf_counter_phase'] is True,'honest timing')
e=closure['installed_error_definition'];ep=ROOT/e['path'];b=ep.read_bytes();req(len(b)==e['bytes'] and hashlib.sha256(b).hexdigest()==e['sha256'],'public error definition')
text=b.decode('utf-8');req(re.search(r'SIZE_LIMIT_EXCEEDED\s*=\s*10010',text) and 'Exceeded licensed model size limit' in text,'10010 interpretation')
receipt=read(RUN/'private_log_receipt.json');req(receipt['raw_logs_public'] is False and receipt['content_privacy_review']=='NOT_PERFORMED','private logs remain private')
# Do not open, hash or print the private logs.
k=ROOT/'src/research8h_standalone_verify.py';req(sha(k)=='708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f','kernel')
s=importlib.util.spec_from_file_location('common_gurobi_readback_reader',k);v=importlib.util.module_from_spec(s);sys.modules[s.name]=v;s.loader.exec_module(v)
m=v.load_model(PRE/'joint');mapping=read(PRE/'backend_rows.json')['rows'];br=read(RUN/'backend_readback.json')
req(sha(RUN/'backend_readback.npz')==br['backend_readback_sha256'],'actual readback hash')
a=v.read_npz(RUN/'backend_readback.npz',('data','indices','indptr','shape','rhs','sense','column_lower','column_upper','objective','integrality'))
def vec(name,dtypes,n):return tuple(v.vector(a[name],dtypes,n,name))
shape=vec('shape',('<i4','<i8'),2);req(shape==(82130,33936),'readback shape')
data=vec('data',('<f8',),316712);indices=vec('indices',('<i4','<i8'),316712);ptr=vec('indptr',('<i4','<i8'),82131)
rhs=vec('rhs',('<f8',),82130);senses=vec('sense',('|S1',),82130)
req(ptr[0]==0 and ptr[-1]==len(data) and all(x<=y for x,y in zip(ptr,ptr[1:])),'CSR pointers')
req(vec('column_lower',('<f8',),m.cols)==m.lower and vec('column_upper',('<f8',),m.cols)==m.upper,'every original column bound')
req(all(x==0 for x in vec('objective',('<f8',),m.cols)),'zero objective')
bits=tuple(v.vector(v.read_npz(PRE/'joint/integrality.npz',('integrality',))['integrality'],('|u1',),m.cols,'original bits'))
req(vec('integrality',('|u1',),m.cols)==bits and sum(bits)==12096,'actual binary declarations')
for r,role in enumerate(mapping):
 i=role['original_row'];actual=list(zip(indices[ptr[r]:ptr[r+1]],data[ptr[r]:ptr[r+1]]));wanted=list(zip(m.indices[m.indptr[i]:m.indptr[i+1]],m.data[m.indptr[i]:m.indptr[i+1]]))
 req(actual==sorted(wanted),'backend coefficient row '+str(r))
 req(rhs[r].hex()==role['rhs_hex'] and senses[r].decode('ascii')==role['sense'],'backend finite endpoint '+str(r))
req(br['options']==plan['options'] and br['columns']==m.cols and br['binaries']==12096 and br['backend_rows']==len(mapping) and br['coefficient_uses']==len(data) and br['optimizer_calls']==0,'readback report/options')
verify(items);verify(outputs,True);req(sha(inventory)=='a604995726f1ca5ae4928bdc65c60e51034fae52add32fca98018876cd4dc767','inventory stable')
report=dict(status='INDEPENDENT_POSTRUN_FAILURE_AND_READBACK_PASS',utc=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),reviewer_sha256=sha(__file__),frozen_bindings=86,producer_inventory_entries=42,inventory_sha256=sha(inventory),freeze_sha256=sha(freeze),failure_closure_sha256=sha(RUN/'failure_closure.json'),all_inputs_outputs_unchanged=True,backend_original_rows=m.rows,backend_rows=len(mapping),columns=m.cols,binaries=sum(bits),coefficient_uses=len(data),all_readback_coefficients_endpoints_boxes_objective_mask_match=True,optimize_attempted=1,optimize_returned=0,invocation_seconds=l['actual_seconds'],error_code=10010,error_meaning='SIZE_LIMIT_EXCEEDED; exceeded licensed model size limit',scientific_verdict='UNKNOWN',scientific_search_established=False,numeric_solver_status=False,points=0,certificates=0,phase_duration_not_fully_recorded=True,marker_to_failure_timestamp_seconds=span,private_log_content_read=False,producer_imports=0,optimizer_imports=0,optimizer_calls=0,old_joint_reassembly=False,elapsed_seconds=time.perf_counter()-T)
with (ARM/'INDEPENDENT_POSTRUN_REVIEW.json').open('x',encoding='utf-8') as out:json.dump(report,out,indent=2);out.write('\n')
print(json.dumps(report))
