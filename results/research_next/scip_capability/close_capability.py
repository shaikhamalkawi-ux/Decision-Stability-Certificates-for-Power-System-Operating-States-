"""Capability-only record closure; no package import, model, or solve."""
from pathlib import Path
import csv
import hashlib
import json
ROOT=Path(__file__).resolve().parents[3]
ARM=ROOT/'results/research_next/scip_capability'
OUT=ARM/'setup01'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
c=read(OUT/'capability.json');done=read(OUT/'completion.json')
assert c['scip_version']==[10,0,2] and c['packages']=={'pyscipopt':'6.2.1','numpy':'2.3.5'}
assert c['exact_mode']==dict(parameter_present=False,enable_attempted=False,enabled=False)
assert not c['certificate_filename_parameter_present']
assert done['optimizer_calls']==done['scientific_model_reads']==done['synthetic_solves']==0
assert done['package_manager_attempts']==1 and done['package_manager_retries']==0
for name in ('source','probe','protocol'):
    d=done[name];p=ROOT/d['path'];assert p.stat().st_size==d['bytes'] and sha(p)==d['sha256']
with (ARM/'READOUT.md').open('x',encoding='utf-8') as f:
    f.write(f'''# Isolated SCIP capability: import works, exact parameters absent

The single authorized setup closed successfully in **{done['phase_seconds']:.6f} seconds**, within the1,800-second allocation. The fresh environment is `.work/scip_capability_env01`, with CPython3.12.14, PySCIPOpt6.2.1, NumPy2.3.5 and bundled SCIP10.0.2. There were **zero optimization calls, zero synthetic solves and zero scientific-model reads**.

The one empty Model had zero variables and constraints. Its complete parameter dictionary did **not** contain `exact/enable` or `certificate/filename`; therefore enabling exact mode was not attempted. This installed wheel provides no demonstrated exact-solving/proof-logging route through those documented parameters. The observation is specific to this installed build; it is not a claim that SCIP generally lacks exact capability. Even numerical scientific-model solving has not yet been exercised in this environment.

The two official cp312-win_amd64 wheels were downloaded once each over normal TLS and matched PyPI size/SHA metadata before the sole offline hash-required pip installation:

| Wheel | Bytes | SHA256 |
|---|---:|---|
| PySCIPOpt6.2.1 |48,216,285|`784d8fbee8134c7c1cf590a60972008159033938a5044d9ed28cde9abf4f86be`|
| NumPy2.3.5 |12,782,922|`86945f2ee6d10cdfd67bcb4069c1662dd711f7e2a4343db5cecec06b87cf31aa`|

Fresh venv creation took119.551416s; offline pip213.466282s; the empty-probe child25.596404s (its internal import/model/read interval19.111454s). Each ran once and returned0. There was no retry, fallback, global package change, license modification, source compilation or additional capability probe. Installation/probe logs and wheel payloads remain private, with public hashes only; raw log content was not read for this closeout.

This is a separate infrastructure arm after the closed Gurobi size-limit failure. It does not alter that record or resolve the common-commitment question. A future numerical search or synthetic certificate experiment requires its own prospective contract and authorization. As the [official SCIP FAQ](https://www.scipopt.org/doc/html/FAQ.php) explains, original-instance certification must account for presolve, and cut proofs may need `viprcomp` completion; an enabled parameter alone would not have established certificate validity.

Frozen records: `setup01/capability.json` SHA256 `{sha(OUT/'capability.json')}` and `setup01/completion.json` `{sha(OUT/'completion.json')}`. Commands, timings, official metadata/download hashes, installed binary/metadata hashes and private-log receipts are in `setup01`. Source SHA256 `{done['source']['sha256']}`, probe `{done['probe']['sha256']}`, protocol `{done['protocol']['sha256']}`. The artifact inventory binds the public record without including the isolated environment, wheels or private logs. Final inventory/readout serialization is outside the measured setup phase.
''')
paths=[ROOT/'src/researchnext_scip_capability.py',ROOT/'src/researchnext_scip_probe.py']
paths += [p for p in ARM.rglob('*') if p.is_file() and p.name!='artifact_manifest.csv']
with (ARM/'artifact_manifest.csv').open('x',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['path','bytes','sha256']);w.writeheader()
    for p in sorted(paths):w.writerow(dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)))
print(json.dumps(dict(status='CLOSED',files=len(paths),capability_sha256=sha(OUT/'capability.json'),completion_sha256=sha(OUT/'completion.json'),
    readout_sha256=sha(ARM/'READOUT.md'),manifest_sha256=sha(ARM/'artifact_manifest.csv'))))
