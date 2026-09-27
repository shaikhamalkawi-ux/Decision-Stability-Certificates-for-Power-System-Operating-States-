"""Append a final public-artifact inventory; no scientific replay."""
from pathlib import Path
import csv
import hashlib
import json
ROOT=Path(__file__).resolve().parents[3]
ARM=ROOT/'results/research_next/common_gurobi'
paths=[ROOT/'src/researchnext_common_gurobi.py',ROOT/'docs/research_next/COMMON_GUROBI_PROTOCOL.md']
paths += [p for p in ARM.rglob('*') if p.is_file() and p.name!='artifact_manifest.csv']
assert len(set(paths))==len(paths)
with (ARM/'artifact_manifest.csv').open('x',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['path','bytes','sha256']);w.writeheader()
    for p in sorted(paths):
        raw=p.read_bytes();w.writerow(dict(path=p.relative_to(ROOT).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
print(json.dumps(dict(files=len(paths),manifest_sha256=hashlib.sha256((ARM/'artifact_manifest.csv').read_bytes()).hexdigest(),
                     readout_sha256=hashlib.sha256((ARM/'FINAL_READOUT.md').read_bytes()).hexdigest())))
