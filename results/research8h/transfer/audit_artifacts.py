"""Post-run replay and cross-model audit; no optimization is performed."""
from pathlib import Path
import hashlib
import json
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"src"))
import numpy as np
import pandas as pd
from scipy.sparse import load_npz
from research8h_transfer import replay,REJECT,MODELS,TEMPORAL,TWO_CC


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output=Path(__file__).resolve().parent
    records=json.loads((output/"results.json").read_text())
    frozen=json.loads((output/"sample_freeze.json").read_text())
    lookup={(r["case"],r["model"]):r for r in records}
    assert len(records)==len(lookup)==48 and len(frozen["cases"])==16
    replayed=[]
    restrictions=[]
    other_negative_full_statuses=[]
    for case in frozen["cases"]:
        name=case["case"]
        directory=output/name
        assert sha(directory/"permutation.csv")==case["permutation_file_sha256"]
        assert sha(directory/"case_arrays.npz")==case["arrays_sha256"]
        full=load_npz(directory/"full/matrix.npz")
        with np.load(directory/"full/bounds.npz") as data:
            full_bounds={key:data[key] for key in data.files}
        full_labels=pd.read_csv(directory/"full/row_metadata.csv.gz")
        for model in MODELS:
            result=lookup[(name,model)]
            replayed.append({"case":name,"model":model,**replay(directory/model)})
            if case["kind"]=="positive_control":
                assert result["model_status"]!="Infeasible" and result["verdict"]!=REJECT
                assert case["positive_matrix_checks_before_first_LP"][model]["pass"]
            if model=="full":
                continue
            labels=pd.read_csv(directory/model/"row_metadata.csv.gz")
            rows=labels["original_row"].to_numpy(int)
            matrix=load_npz(directory/model/"matrix.npz")
            assert matrix.shape==full[rows].shape and (matrix!=full[rows]).nnz==0
            with np.load(directory/model/"bounds.npz") as bounds:
                assert all(np.array_equal(bounds[key],values[rows] if key.startswith("row_") else values)
                    for key,values in full_bounds.items())
            if model=="two_cc":
                expected=full_labels.index[(~full_labels["family"].isin(TEMPORAL))|full_labels["uid"].isin(TWO_CC)].to_numpy()
                assert np.array_equal(rows,expected)
            restrictions.append({"case":name,"model":model,"exact_row_subset_and_unchanged_column_bounds":True})
            if result["verdict"]==REJECT and lookup[(name,"full")]["verdict"]!=REJECT:
                full_status=lookup[(name,"full")]["verdict"]
                assert full_status!="ADMITTED_CONTINUOUS_RELAXATION", "Restricted exact rejection contradicts full LP witness"
                other_negative_full_statuses.append({"case":name,"restricted_model":model,"full_verdict":full_status})
    for item in pd.read_csv(output/"input_manifest.csv").to_dict("records"):
        assert sha(Path(item["path"]))==item["sha256"]
    assert sha(ROOT/"src/research8h_transfer.py")==frozen["script_sha256"]
    assert sha(ROOT/"docs/research8h/TRANSFER_PROTOCOL.md")==frozen["protocol_sha256"]
    (output/"archive_replay.json").write_text(json.dumps(replayed,indent=2),encoding="utf-8")
    result={"all_pass":True,"scheduled_and_completed_LPs":48,"frozen_cases":16,
        "source_and_frozen_case_hashes_match":True,"restricted_model_structural_checks":restrictions,
        "positive_control_contradictions":0,"restricted_negative_full_admission_contradictions":0,
        "restricted_negatives_with_other_full_statuses":other_negative_full_statuses,
        "replay_count":len(replayed),"scope":"solver-free exact certificate/continuous-witness replay plus model-row and hash audits"}
    (output/"post_run_audit.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if not isinstance(v,list)}))


if __name__=="__main__":
    main()
