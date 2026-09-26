"""Read saved five-case outcomes only; no optimizer or model mutation."""
from pathlib import Path
import csv
import gzip
import json
import hashlib

BASE=Path(__file__).resolve().parent
def read(path):return json.loads(path.read_text(encoding="utf-8"))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
results=read(BASE/"results.json")
assert [x["case"] for x in results]==["days_132","days_213","days_231","days_312","days_321"]
records=[]
for result in results:
    directory=BASE/result["case"]
    cert=read(directory/"fixed_schedule_certificate.json")
    assert cert["verification"]["pass"] and cert["verification"]["robust_pass"]
    assert sha(directory/"matrix.npz")==cert["model_artifacts"]["matrix.npz"]
    assert sha(directory/"bounds.npz")==cert["model_artifacts"]["bounds.npz"]
    assert sha(directory/"raw_solver_ray.npz")==cert["raw_solver_ray_sha256"]
    assert sha(directory/"row_metadata.csv.gz")==cert["row_metadata_sha256"]
    assert sha(BASE/"input_manifest.json")==cert["experiment_manifest_sha256"]
    with gzip.open(directory/"row_metadata.csv.gz","rt",encoding="utf-8",newline="") as stream:labels=list(csv.DictReader(stream))
    cap=[int(x["row"]) for x in labels if x["family"]=="fossil_energy_cap"]
    assert len(cap)==1
    cap_d=[x for x in cert["multipliers"] if x["row"]==cap[0]]
    binding=read(directory/"model_binding.json")
    records.append({"case":result["case"],"model_status":result["model_status"],"verdict":result["verdict"],
        "elapsed_s":result["elapsed_s"],"nominal_gap_ray_units":cert["verification"]["separation_gap"],
        "expanded_gap_ray_units":cert["verification"]["robust_separation_gap"],
        "certificate_nonzero_rows":len(cert["multipliers"]),"cap_row_has_nonzero_multiplier":bool(cap_d),
        "cap_multiplier_hex":cap_d[0]["value_hex"] if cap_d else "0x0.0p+0",
        "prior_constructive_full_model_positive":binding["old_constructive_full_positive"],
        "old_constructive_states_equal_identity":binding["old_constructive_states_equal_identity"],
        "accepted_binary_witness":False,"original_unfixed_infeasibility_inference":False,
        "raw_vector_value_valid":result["solution_value_valid"],
        "anchored_fixed_expanded_pass":result.get("exact_fixed_expanded_pass"),
        "anchored_unfixed_expanded_pass":result.get("exact_unfixed_expanded_pass"),
        "native_candidate_pass":result.get("native_full_check_pass")})
(BASE/"summary.json").write_text(json.dumps(records,indent=2,allow_nan=False)+"\n",encoding="utf-8")
with (BASE/"summary.csv").open("w",encoding="utf-8",newline="") as stream:
    writer=csv.DictWriter(stream,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
print(json.dumps(records,indent=2),flush=True)
