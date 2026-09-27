"""One read-only hash/provenance closeout; no solver import or scientific replay."""
from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
ARM = ROOT/'results/research_next/common_gurobi'
PRE = ARM/'prepared'
RUN = ARM/'run01'

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def binding(p): return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=digest(p))
def save(p,v):
    with p.open('x',encoding='utf-8') as f: json.dump(v,f,indent=2);f.write('\n')

assert digest(PRE/'prepared_freeze.json')=='c91dac7c583a42493e0eae6f9b3b493140a0997661bb748a08a3d08d168cb926'
freeze=read(PRE/'prepared_freeze.json')
assert digest(PRE/'input_manifest.json')==freeze['manifest_sha256']
items=read(PRE/'input_manifest.json')['files']
assert len(items)==86
for item in items:
    p=Path(item['path']);raw=p.read_bytes()
    assert len(raw)==item['bytes'] and hashlib.sha256(raw).hexdigest()==item['sha256']
failure=read(RUN/'execution_failure.json')
assert failure['stage']=='sole_optimize' and failure['backend_errno']==10010
assert failure['call_ledger']['attempted']==1 and failure['call_ledger']['returned']==0
assert not (RUN/'solver_returned.json').exists() and not (RUN/'raw_solution.npz').exists()
error_source=ROOT/'.work/auer_projection_env/Lib/site-packages/gurobipy/_errorconst.py'
error_text=error_source.read_text(encoding='utf-8')
assert 'SIZE_LIMIT_EXCEEDED      = 10010' in error_text
assert 'SIZE_LIMIT_EXCEEDED: Exceeded licensed model size limit' in error_text
start=read(RUN/'execution_started.json')
span=(datetime.fromisoformat(failure['utc'])-datetime.fromisoformat(start['utc'])).total_seconds()
save(RUN/'failure_closure.json',dict(
    status='CLOSED_LICENSE_CAPACITY_FAILURE_PENDING_INDEPENDENT_REVIEW',utc=datetime.now(timezone.utc).isoformat(),
    scientific_verdict='UNKNOWN',scientific_search_established=False,
    numeric_solver_status_returned=False,accepted_points=0,exact_negative_certificates=0,
    process_session=34813,process_exit_code=1,optimizer_invocations_attempted=1,optimizer_invocations_returned=0,
    invocation_seconds=failure['call_ledger']['actual_seconds'],
    execution_marker_to_error_timestamp_seconds=span,timestamp_span_is_not_complete_perf_counter_phase=True,
    all86_frozen_inputs_unchanged=True,manifest=binding(PRE/'input_manifest.json'),freeze=binding(PRE/'prepared_freeze.json'),
    error_code=10010,error_name='SIZE_LIMIT_EXCEEDED',
    error_meaning='Exceeded licensed model size limit',installed_error_definition=binding(error_source),
    error_definition_lines=[16,56],raw_log_content_read=False,raw_logs_public=False,
    no_retry=True,no_fallback=True,no_license_change=True,no_new_probe_or_install=True,
    command=['.work/auer_projection_env/Scripts/python.exe','src/researchnext_common_gurobi.py','--run-prepared',
             '--expected-freeze-sha256',digest(PRE/'prepared_freeze.json')],
    closure_source=binding(Path(__file__)),scientific_arithmetic_replays=0,solver_imports=0))
with (ARM/'READOUT.md').open('x',encoding='utf-8') as f:
    f.write(f'''# Original common model: Gurobi attempt closed without a search result

The single authorized invocation stopped with Gurobi error **10010, SIZE_LIMIT_EXCEEDED**. The installed Gurobi 13.0 error definitions identify this as exceeding the licensed model-size limit. It is an environment/license-capacity result, not mathematical infeasibility or solver incompatibility. The original common-binary question remains **UNKNOWN**.

The backend construction and exact API readback completed: 69,362 original rows became 82,130 finite-side rows, with 33,936 unchanged columns, all 12,096 original binaries, zero objective, and 316,712 coefficient uses after splitting. No diving restrictions, additional variables or changed scientific coefficients were introduced. This successful translation is not a feasible-point or negative certificate.

The call ledger records one optimize invocation attempted and zero returned. That invocation lasted {failure['call_ledger']['actual_seconds']:.15f} seconds before the capacity error. No numeric optimization status, incumbent, candidate or certificate was returned, and scientific search was not established. The execution-marker-to-error UTC timestamp span was {span:.6f} seconds; it is not a complete perf-counter phase duration. The declared allocation was 1,800 solver seconds within a 2,400-second soft phase. There was no retry, alternate backend, warm start, additional LP, license change, purchase or installation.

All 86 frozen input bindings, the prepared manifest and freeze were rechecked unchanged during this separate hash-only closeout. The prepared freeze remains `c91dac7c583a42493e0eae6f9b3b493140a0997661bb748a08a3d08d168cb926`; source/protocol remain `9f5515fb99ac43cba3756f1e2b5a9f3a0ad9df7c143860922edd9ae99cd000ec` / `9fd3bc026acad8ca940b9338c257094fb5f5fefb7de4ecd076f81762fa1ebb71`.

Raw startup and solver logs stay private under `.work/researchnext_common_gurobi/run01`. Their content was not read for this closure or copied into the public results; the receipt records only path, size and SHA256. Numeric error interpretation came from the installed package's public error definitions. The independent post-run gate remains pending. Existing common/diving results are unchanged.

`run01/failure_closure.json` records the command, process exit/session, input hashes and installed error-definition binding. `run01/backend_readback.npz` and its JSON record preserve the complete pre-call API readback. `run01/execution_failure.json` preserves the original error-stage/call ledger. `producer_output_inventory.csv` binds all current producer files and the source/protocol; independent review files are deliberately excluded until final closure.
''')
paths=[ROOT/'src/researchnext_common_gurobi.py',ROOT/'docs/research_next/COMMON_GUROBI_PROTOCOL.md']
paths += [p for p in ARM.rglob('*') if p.is_file() and not p.name.startswith('INDEPENDENT_') and p.name!='producer_output_inventory.csv']
assert len(set(paths))==len(paths)
with (ARM/'producer_output_inventory.csv').open('x',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['path','bytes','sha256']);w.writeheader()
    for p in sorted(paths):w.writerow(binding(p))
print(json.dumps(dict(status='HASH_ONLY_CLOSURE_PASS',bound_files=len(paths),failure_closure_sha256=digest(RUN/'failure_closure.json'),
                     readout_sha256=digest(ARM/'READOUT.md'),inventory_sha256=digest(ARM/'producer_output_inventory.csv'))))
