"""Append-only producer closure; hashes and recorded metadata only, no model math."""
import csv
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ARM = Path(__file__).resolve().parent
RUN = ARM / 'run01'
EXPECTED_GO = 'da449965a1febf3bdeac8915c3355f7fd3a6ebc9c8cda864021432c74a69afc0'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_json(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')

go_path = ARM / 'ROOT_EXECUTION_GO.json'
assert digest(go_path) == EXPECTED_GO
go = json.loads(go_path.read_text(encoding='utf-8'))
checks = []
for relative, expected in go['pins'].items():
    actual = digest(ROOT / relative)
    checks.append(dict(path=relative, expected_sha256=expected, actual_sha256=actual))
    assert actual == expected, relative
write_json(ARM / 'EXTERNAL_TRANSPORT_CLOSURE.json', dict(
    utc=datetime.now(timezone.utc).isoformat(), root_go_sha256=EXPECTED_GO,
    all_go_pins_unchanged=True, checks=checks,
    scope='Independent producer-owner hash readback only; not independent scientific review'))

completion = json.loads((RUN / 'completion.json').read_text())
result = json.loads((RUN / 'result.json').read_text())
master = json.loads((RUN / 'round_01/master/result.json').read_text())
write_json(ARM / 'EXECUTION_RECEIPT.json', dict(
    session_id=18854, initial_chunk_id='0ca152', final_chunk_id='a1358f', exit_code=0,
    interpreter='C:/Users/gmalkawi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',
    arguments=['-I', '-S', 'src/researchnext_common_refinement_jobs.py', '--run-prepared',
               '--expected-freeze-sha256', go['freeze_sha256']],
    root_go_sha256=EXPECTED_GO, sole_controller_pid=19896, controller_parent_pid=86124,
    worker_launcher_pid=81996, worker_actual_python_pid=57176,
    scientific_runs=1, retries=0, stdout_final=dict(
        accepted_common=False, common_verdict='UNKNOWN', phase_deadline_met=True,
        stop_reason='NO_SINGLE_EXACT_MASTER_NOMINEE', optimizer_attempts=1),
    authoritative_completion_sha256=digest(RUN / 'completion.json'),
    private_logs_published=False))

readout = '''# Ownership-recovery producer readout

The single authorized recovery run closed with **UNKNOWN**. Its first necessary-master MIP reached the fixed 120-second limit without a returned solution. The declared stop rule ended the arm: there was no new nominee, recourse LP, phase-I LP, new adaptive cut or common witness. Numerical time-limit status is not an infeasibility proof.

| Recorded quantity | Outcome |
|---|---|
| Worker launches / optimizer attempts / returned calls | 1 / 1 / 1 |
| New nominees / completed rounds / new cuts | 0 / 0 / 0 |
| Actual master status | `timelimit`, zero solutions, 2 nodes, 102,174 LP iterations |
| Master call time | 120.03080490004504 seconds |
| Solver soft overrun | 0.030804900045040995 seconds |
| Producer measured overall phase | 290.7008039000211 seconds |
| Overall phase overrun | 0 seconds |
| Inherited seed rows with completed actual backend transport | 336 / 336 |

The 336 exact seed proofs and requested encodings were inherited from the independently reviewed closed predecessor, without recalculating seed q, support, fractional controls or the anchor. This run inserted and read back their numerical rows in the actual master. Producer transport checks admitted all 336; independent post-run review is still required before treating this new backend evidence as independently verified. The result field `terminal_cut_numeric_transport=ADMITTED` refers here to those 336 inherited rows; no new terminal cut exists.

The corrected ownership gate succeeded for launcher PID 81996 and actual Python PID 57176. Both exact handles were captured before assignment; each process joined its own new job, with successful API status, Win32 error 0 and positive selected-job membership before worker GO. The worker closed normally with both retained handles reaped. No timeout termination or cleanup fallback was exercised. This does not demonstrate the unexercised live-solver timeout path or the unused HiGHS-worker path. Controller PID 19896 and parent PID 86124, and both worker PIDs, were absent in the separate exact-PID readback at 14:56:04 UTC; no external termination was performed.

The controller ran once as session 18854 with exit code 0. The producer's final completion is authoritative: no common point was accepted and the phase deadline was met. Controller and worker closing source/protocol/freeze/manifest gates passed; a separate owner hash readback also checked every root-GO pin. The complete 1,769-input manifest remains subject to the independent closing review. Raw solver logs remain private.

This recovery did not resume or overwrite the predecessor: its zero-optimizer ownership failure and 97.2533605-second phase remain separate, as does the harmless 0.6221272-second ownership probe. Recovery preparation took 93.69809979997808 seconds and is reported separately from the scientific phase. The maximum was eight new nominations and 24 calls, but the frozen first-null stop rule used only one call. There was no automatic retry or ninth nomination.

The public inventory binds all `run01` artifacts and the additive execution/transport/process receipts and this readout. No source, protocol, prepared payload or historical file was changed during closure. The scientific conclusion remains the original common-binary UNKNOWN. This is infrastructure and bounded-search evidence, not a new algorithm, temporal impossibility proof or minimum-information result. Split independent mathematical-scope and actual backend/lifecycle reviews are pending at this producer closure.
'''
with (ARM / 'READOUT.md').open('x', encoding='utf-8', newline='\n') as stream:
    stream.write(readout)

paths = sorted([p for p in RUN.rglob('*') if p.is_file()] + [
    ARM / 'EXTERNAL_PROCESS_CLOSURE.json', ARM / 'EXTERNAL_TRANSPORT_CLOSURE.json',
    ARM / 'EXECUTION_RECEIPT.json', ARM / 'READOUT.md', Path(__file__).resolve()],
    key=lambda p: p.relative_to(ROOT).as_posix())
with (ARM / 'producer_output_inventory.csv').open('x', encoding='utf-8', newline='') as stream:
    writer = csv.DictWriter(stream, fieldnames=['path', 'bytes', 'sha256'])
    writer.writeheader()
    for path in paths:
        writer.writerow(dict(path=path.relative_to(ROOT).as_posix(), bytes=path.stat().st_size, sha256=digest(path)))
print(json.dumps(dict(status='PRODUCER_CLOSED_PENDING_INDEPENDENT_REVIEWS', files=len(paths),
    inventory_sha256=digest(ARM / 'producer_output_inventory.csv'),
    completion_sha256=digest(RUN / 'completion.json'), result_sha256=digest(RUN / 'result.json'),
    readout_sha256=digest(ARM / 'READOUT.md'), optimizer_attempts=1, nominees=0, verdict='UNKNOWN')))
