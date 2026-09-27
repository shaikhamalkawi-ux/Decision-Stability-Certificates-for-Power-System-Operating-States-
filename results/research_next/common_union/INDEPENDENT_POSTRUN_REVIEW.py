"""Closed zero-call UNION audit; no scientific arrays, producer imports or optimizer."""
from pathlib import Path
import ast,csv,hashlib,json,time
from datetime import datetime
ROOT=Path(__file__).resolve().parents[3]
ARM=ROOT/'results/research_next/common_union';PRE=ARM/'prepared';RUN=ARM/'run01'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def verify(items,relative=False):
    seen=set()
    for r in items:
        p=(ROOT/r['path'] if relative else Path(r['path'])).resolve()
        assert p not in seen;seen.add(p)
        data=p.read_bytes();assert len(data)==int(r['bytes']) and hashlib.sha256(data).hexdigest()==r['sha256'],str(p)
    return seen
def main():
    started=time.perf_counter();output=ARM/'INDEPENDENT_POSTRUN_REVIEW.json';assert not output.exists()
    pins={
      ROOT/'src/researchnext_common_union.py':'92089c0301bd6a7399728abdf0a9a8964bd570199bc2490ea22e947adfedc1a1',
      ROOT/'docs/research_next/COMMON_UNION_PROTOCOL.md':'fdf6ff12aa5afbea4547583d1cdd2d12d774e18905eb2fdb1a6cf12c64b7e06c',
      PRE/'prepared_freeze.json':'8d5e348d91db8ae082a1a036d2359ac382891b25849e9e682fb833e9ae52d0a2',
      PRE/'input_manifest.json':'1337e9674d15fc52023733b8c72b1140c20d01a472a287fd43a90cd5719d3a2d',
      ARM/'INDEPENDENT_PREPARED_REVIEW.json':'b7b856c9f7395a46e51569a13d844f53d7bb883bb97d8f76a627b0049cc2c05e',
      ARM/'FAILURE_CLOSURE.json':'8229435b98abd90414fde8d6cdb8c54c107cfbe3f0f0fb47e7e1ebb7523ceeb5',
      ARM/'READOUT.md':'6886c308002b67c7fe43423b55575c61b4f317045712e2068c62a9f37ab55d2a',
      ARM/'producer_output_inventory.csv':'5d9e431d71830696f53e85f0259e97a808653148c88cd2948346b2b5e8af4fc1',
    }
    for p,h in pins.items():assert sha(p)==h,str(p)
    items=read(PRE/'input_manifest.json')['files'];assert len(items)==94;verify(items)
    outputs=list(csv.DictReader((ARM/'producer_output_inventory.csv').open(encoding='utf-8-sig')))
    assert len(outputs)==39;paths=verify(outputs,True)
    assert all(p.is_relative_to(ARM.resolve()) for p in paths)
    actual={p.resolve() for p in RUN.rglob('*') if p.is_file()}
    assert actual=={(RUN/'execution_started.json').resolve()}
    assert actual=={p for p in paths if p.is_relative_to(RUN.resolve())}
    f=read(ARM/'FAILURE_CLOSURE.json');interruption=read(ARM/'PRECALL_INTERRUPTION.json')
    marker=read(RUN/'execution_started.json');probe=read(ARM/'PREBINDING_PERFORMANCE_PROBE.json')
    freeze=read(PRE/'prepared_freeze.json');plan=read(PRE/'plan.json')
    assert f['status']=='PRECALL_INTERRUPTED_READBACK_IMPLEMENTATION_FAILURE' and f['scientific_verdict']=='UNKNOWN'
    assert f['optimizer_calls']==interruption['scientific_optimizer_calls']==0 and f['process_exit_code']==1 and f['session_id']==79040
    assert not f['backend_readback_complete'] and not f['call_ready_present'] and f['no_candidate_or_certificate']
    assert f['source_and_freeze_unchanged'] and f['no_retry']
    assert f['phase_stopwatch_unavailable_after_forced_interruption'] and f['phase_guard_was_after_readback_not_an_interrupting_wall_limit']
    assert interruption['scientific_verdict']=='UNKNOWN' and not interruption['call_ready_present'] and not interruption['backend_readback_present'] and not interruption['automatic_retry']
    assert interruption['source_sha256']==freeze['source_sha256'] and interruption['freeze_sha256']==marker['freeze_sha256']==sha(PRE/'prepared_freeze.json')
    assert '--run-prepared' in interruption['command_line'] and marker['freeze_sha256'] in interruption['command_line']
    interval=(datetime.fromisoformat(interruption['utc'])-datetime.fromisoformat(marker['utc'])).total_seconds()
    assert abs(interval-f['execution_marker_to_interruption_seconds'])<=1e-6 and interval>plan['phase_seconds']
    assert probe['kind']=='invented_three_array_property_identity_probe' and probe['scientific_model_reads']==probe['optimizer_calls']==0
    assert probe['highs_version']=='1.12.0' and probe['index_type']=='list'
    assert all(probe[k] is False for k in ('index_repeated_access_same_object','value_repeated_access_same_object','start_repeated_access_same_object'))
    assert not f['private_logs_public'] and f['private_log_contents_not_inspected']
    # Inspect control flow, never execute/import it: completed readback precedes admission and h.run.
    source=(ROOT/'src/researchnext_common_union.py').read_text(encoding='utf-8')
    tree=ast.parse(source);functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    runtext=ast.get_source_segment(source,functions['run']);build=ast.get_source_segment(source,functions['build_readback'])
    assert runtext.index('h=build_readback')<runtext.index("save(RUN/'admission.json'")<runtext.index('h.run()')
    assert build.index("save(RUN/'backend_readback.json'")<build.index('return h')
    assert 'matrix.index_[k]' in build and 'matrix.value_[k]' in build and 'matrix.start_[i]' in build
    assert len([n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='run'])==1
    # A complete backend readback is absent, so no array-equivalence claim is made.
    verify(items);verify(outputs,True)
    for p,h in pins.items():assert sha(p)==h
    assert actual=={p.resolve() for p in RUN.rglob('*') if p.is_file()}
    result=dict(status='INDEPENDENT_ZERO_CALL_FAILURE_REVIEW_PASS',review_source_sha256=sha(__file__),frozen_input_bindings=94,producer_outputs=39,all_inputs_outputs_unchanged=True,optimizer_attempts=0,optimizer_returns=0,scientific_verdict='UNKNOWN',solver_status_returned=False,accepted_points=0,certificates=0,backend_readback_complete=False,backend_coefficients_validated_in_this_review=False,prepared_state_gate_inherited=True,execution_marker_to_interruption_seconds=interval,phase_stopwatch_unavailable=True,phase_guard_not_interrupting=True,probe_invented_and_not_repeated=True,source_control_flow_checked=True,producer_imports=0,optimizer_imports=0,optimizer_calls=0,scientific_array_decodes=0,private_logs_read=False,producer_failure_closure_sha256=sha(ARM/'FAILURE_CLOSURE.json'),producer_inventory_sha256=sha(ARM/'producer_output_inventory.csv'),review_scope='Pre-call implementation interruption only; neither candidate nor unrestricted infeasibility established.',elapsed_seconds=time.perf_counter()-started)
    with output.open('x',encoding='utf-8') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps(result));print('REPORT_SHA256='+sha(output))
if __name__=='__main__':main()
