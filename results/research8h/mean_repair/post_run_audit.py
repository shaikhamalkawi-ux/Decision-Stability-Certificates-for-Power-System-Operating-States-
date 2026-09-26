"""Append-only source/hash and exact fossil-cap audit; no solver import or calls."""
import csv
from datetime import datetime,timezone
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(value):
    return {"numerator":str(value.numerator),"denominator":str(value.denominator),"approximate":float(value)}


def main():
    target=HERE/"post_run_audit.json"
    if target.exists():raise FileExistsError("Preserve earlier audit")
    completion=json.loads((HERE/"completion.json").read_text())
    assert completion["optimization_calls"]==5
    with (HERE/"input_manifest.csv").open(newline="",encoding="utf-8") as f:
        manifest=list(csv.DictReader(f))
    mismatches=[row["path"] for row in manifest if sha(Path(row["path"]))!=row["sha256"]]
    assert not mismatches,mismatches
    freeze=json.loads((HERE/"all_models_frozen_before_first_solve.json").read_text())
    assert sha(HERE/"input_manifest.csv")==freeze["manifest_sha256"]
    cases=[]
    for result in json.loads((HERE/"summary.json").read_text()):
        directory=HERE/result["case"]
        with gzip.open(directory/"row_metadata.csv.gz","rt",newline="",encoding="utf-8") as f:
            labels=list(csv.DictReader(f))
        cap_rows=[int(x["row"]) for x in labels if x["family"]=="fossil_energy_cap"]
        assert len(cap_rows)==1
        row=cap_rows[0]
        with np.load(directory/"matrix.npz") as m:
            start,end=m["indptr"][row:row+2]
            indices=m["indices"][start:end].copy();coefficients=m["data"][start:end].copy()
        with np.load(directory/"bounds.npz") as b:
            cap=Fraction.from_float(float(b["row_upper"][row]))
        assert len(indices)==168*23 and np.all(coefficients==1.)
        base={"case":result["case"],"model_status":result["model_status"],"cap_row":row,
            "fossil_dispatch_coordinates":len(indices),"cap_MWh":record(cap),
            "primal_exists":(directory/"primal.npz").exists()}
        if base["primal_exists"]:
            with np.load(directory/"primal.npz") as p:vector=p["vector"].copy()
            energy=sum((Fraction.from_float(float(vector[int(j)]))*Fraction.from_float(float(a))
                for j,a in zip(indices,coefficients)),Fraction(0))
            excess=max(Fraction(0),energy-cap)
            base.update(exact_binary64_fossil_energy_MWh=record(energy),
                exact_binary64_fossil_cap_excess_MWh=record(excess),
                fossil_cap_exactly_satisfied=energy<=cap,
                fossil_cap_within_declared_tolerance=excess<=Fraction.from_float(1e-5),
                raw_primal_epsilon=float(vector[-1]),
                reported_float_sum_difference_MWh=float(energy)-result.get("fossil_energy_MWh",float(energy)))
            if result.get("primal_verification_pass"):
                assert base["fossil_cap_within_declared_tolerance"]
        cases.append(base)
    report={"utc":datetime.now(timezone.utc).isoformat(),"audit_script_sha256":sha(Path(__file__)),
        "frozen_input_manifest_sha256":sha(HERE/"input_manifest.csv"),"all_source_model_hashes_match":True,
        "manifest_files":len(manifest),"cases":cases,"optimization_calls":0,
        "qualification":"Exact binary64 fossil sum/cap residual supplements the existing tolerance matrix check; it does not assert exact feasibility of other rows or a rigorous primal upper bound."}
    target.write_text(json.dumps(report,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({"hashes_pass":True,"cases":len(cases),"exact_cap_satisfaction":[x.get("fossil_cap_exactly_satisfied") for x in cases]}),flush=True)


if __name__=="__main__":main()
