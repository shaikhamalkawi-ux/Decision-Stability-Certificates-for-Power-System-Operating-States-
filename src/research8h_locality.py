"""Frozen row-subset dwell locality LP experiment; no original artifacts changed."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
import numpy as np
import pandas as pd
from scipy.sparse import load_npz, save_npz

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/research8h/LOCALITY_PROTOCOL.md"
WIDTHS = [0, 8, 16, 24, 48, 72, 96, 120, 168]
DWELL = {"minimum_up", "minimum_down"}
BOUND_SOURCES = {
    "temporal_lp_certificate.py": "6191c5760811cab0ec22b2fb1376a5be3aa47cb548e1260c4a17e2563d9802e4",
    "v8r1_rts_seasonal.py": "bca0127d7b2771c6da3b6a838c8caa7fb6ce0df4eafd9a512326aabd8daf7dc2",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+"\n", encoding="utf-8")


def bind_sources():
    for name, expected in BOUND_SOURCES.items():
        assert sha(ROOT/"src"/name) == expected, (name, "bound baseline source changed")


bind_sources()
from temporal_lp_certificate import assemble, check_vector, exact_ray_check, solve_case
from v8r1_rts_seasonal import inputs, load_model


def state_vector(p, u):
    y, z = np.zeros_like(u), np.zeros_like(u)
    y[1:] = np.maximum(0, np.diff(u, axis=0))
    z[1:] = np.maximum(0, -np.diff(u, axis=0))
    return np.concatenate([array.ravel() for array in (p,u,y,z)])


def dwell_support(matrix, metadata, labels):
    """Inspect all nonzero variable columns, not just row endpoint labels."""
    offsets=metadata["offsets"]
    cuts=[offsets[k] for k in ("P","U","Y","Z")]+[matrix.shape[1]]
    widths=[metadata["units"]]+[metadata["thermal_units"]]*3
    support={}
    for label in labels:
        if label["family"] not in DWELL:
            continue
        row=label["row"]
        columns=matrix.indices[matrix.indptr[row]:matrix.indptr[row+1]]
        hours=[]
        for column in columns:
            block=int(np.searchsorted(cuts,column,side="right")-1)
            assert block in (1,2,3), (row,column,"dwell row must only touch state variables")
            hours.append(int((column-cuts[block])//widths[block]))
        assert hours and max(hours)==label["hour_0based"]
        support[row]=(min(hours),max(hours))
    return support


def retain(labels, support, width):
    left,right=(84-width//2,83+width//2) if width else (None,None)
    keep=[]
    for label in labels:
        row=label["row"]
        if label["family"] not in DWELL or (width and left<=support[row][0] and support[row][1]<=right):
            keep.append(row)
    return np.asarray(keep,dtype=int),left,right


def subset(matrix,bounds,labels,keep,support):
    selected=matrix[keep].tocsr()
    selected_bounds={key:(value[keep] if key.startswith("row_") else value.copy()) for key,value in bounds.items()}
    selected_labels=[]
    for local,original in enumerate(keep):
        label={**labels[original],"row":local,"original_row":int(original)}
        if int(original) in support:
            label["dwell_support_first_hour"],label["dwell_support_last_hour"]=support[int(original)]
        selected_labels.append(label)
    return selected,selected_bounds,selected_labels


def replay(directory):
    matrix=load_npz(directory/"matrix.npz")
    with np.load(directory/"bounds.npz") as data:
        bounds={key:data[key] for key in data.files}
    recorded=json.loads((directory/"result.json").read_text())
    assert sha(directory/"matrix.npz")==recorded["matrix_sha256"]
    assert sha(directory/"bounds.npz")==recorded["bounds_sha256"]
    if (directory/"dual_certificate.json").exists():
        certificate=json.loads((directory/"dual_certificate.json").read_text())
        for filename in ("matrix.npz","bounds.npz"):
            assert sha(directory/filename)==certificate["model_artifacts"][filename]
        multipliers=np.zeros(matrix.shape[0])
        for entry in certificate["multipliers"]:
            multipliers[entry["row"]]=float.fromhex(entry["value_hex"])
        check=exact_ray_check(matrix,bounds,multipliers)
        assert check["pass"] and check["robust_pass"]
        return {"type":"exact_binary64_certificate","verification":check}
    if (directory/"continuous_solution.npz").exists():
        with np.load(directory/"continuous_solution.npz") as data:
            check=check_vector(matrix,bounds,data["vector"])
        assert check["pass"]
        return {"type":"continuous_witness_only","verification":check,"UC_verdict":"UNKNOWN"}
    return {"type":"no_verified_artifact","UC_verdict":"UNKNOWN"}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-v3",type=Path)
    parser.add_argument("--output",type=Path,default=ROOT/"results/research8h/locality")
    parser.add_argument("--verify-archived",action="store_true")
    args=parser.parse_args()
    if args.verify_archived:
        records=json.loads((args.output/"summary.json").read_text())
        checks=[{"width":r["width"],**replay(args.output/f"width_{r['width']:03d}")} for r in records]
        save(args.output/"archive_replay.json",checks)
        print(json.dumps({"verified_cases":len(checks)}),flush=True)
        return
    if args.source_v3 is None:
        parser.error("--source-v3 is required")
    if (args.output/"pre_run_freeze.json").exists():
        raise FileExistsError("Existing locality run is preserved; use a separately declared output directory")
    args.output.mkdir(parents=True,exist_ok=True)
    source=load_model(args.source_v3)
    columns,_,pmin,pmax,demand,paths=inputs(source,args.source_v3,7)
    p_path=ROOT/"results/v8/network_repair/network_repair_dispatch.csv"
    u_path=ROOT/"results/v8/network_repair/network_fixed_commitment.csv"
    order_path=ROOT/"results/temporal_information/twins/seed_26092600/permutation.csv"
    p=pd.read_csv(p_path)[columns].to_numpy(float)
    thermal=source.dec.iloc[np.flatnonzero(source.thermal.to_numpy(bool))]["GEN UID"].tolist()
    u=pd.read_csv(u_path)[thermal].to_numpy(float)
    identity=state_vector(p,u)
    means=p.mean(axis=0)
    order=pd.read_csv(order_path)["source_hour_0based"].to_numpy(int)
    assert np.array_equal(np.sort(order),np.arange(168))
    assert np.array_equal(order[:48],np.arange(48)) and np.array_equal(order[-48:],np.arange(120,168))
    original_matrix,original_bounds,metadata,labels=assemble(source,pmin,pmax,demand,means)
    positive=check_vector(original_matrix,original_bounds,identity)
    assert positive["pass"],positive
    matrix,bounds,twin_metadata,twin_labels=assemble(source,pmin[order],pmax[order],demand[order],means)
    assert metadata==twin_metadata and labels==twin_labels
    archive=ROOT/"results/temporal_information/lp_certificate/seed_26092600"
    archived_matrix=load_npz(archive/"matrix.npz")
    assert matrix.shape==archived_matrix.shape and (matrix!=archived_matrix).nnz==0
    with np.load(archive/"bounds.npz") as archived_bounds:
        assert all(np.array_equal(value,archived_bounds[key]) for key,value in bounds.items())
    support=dwell_support(matrix,metadata,labels)
    controls=[]
    previous=set()
    for width in WIDTHS:
        keep,left,right=retain(labels,support,width)
        assert previous.issubset(set(keep))
        previous=set(keep)
        selected,selected_bounds,_=subset(original_matrix,original_bounds,labels,keep,support)
        check=check_vector(selected,selected_bounds,identity)
        assert check["pass"],(width,check)
        controls.append({"width":width,"left":left,"right":right,"identity_witness_check":check})
    assert len(previous)==matrix.shape[0]
    empty_keep,_,_=retain(labels,support,0)
    empty_matrix,empty_bounds,_=subset(matrix,bounds,labels,empty_keep,support)
    empty_check=check_vector(empty_matrix,empty_bounds,state_vector(p[order],u[order]))
    assert empty_check["pass"],empty_check
    save(args.output/"positive_controls.json",{"full_identity":positive,"identity_by_window":controls,
        "empty_twin_with_recomputed_transitions":empty_check,"full_twin_matches_archived_baseline_arrays":True})
    input_paths=[Path(__file__),PROTOCOL,*[ROOT/"src"/name for name in BOUND_SOURCES],
        p_path,u_path,order_path,*paths,args.source_v3/"code/dscgrid_model.py",
        *sorted((args.source_v3/"raw").rglob("*.csv")),archive/"matrix.npz",archive/"bounds.npz"]
    manifest=[{"path":str(path),"bytes":path.stat().st_size,"sha256":sha(path)} for path in dict.fromkeys(input_paths)]
    pd.DataFrame(manifest).to_csv(args.output/"input_manifest.csv",index=False)
    save(args.output/"pre_run_freeze.json",{"utc":datetime.now(timezone.utc).isoformat(),"baseline":"7300129",
        "protocol_sha256":sha(PROTOCOL),"script_sha256":sha(Path(__file__)),"bound_source_sha256":BOUND_SOURCES,
        "case":"seed_26092600","widths":WIDTHS,"seconds_per_LP":30,"phase_wall_budget_s":900,
        "selection":"fixed centered nested windows; no adaptive window or support selection"})
    records=[]
    phase_start=time.monotonic()
    for width in WIDTHS:
        remaining=900-(time.monotonic()-phase_start)
        if remaining<35:
            save(args.output/"budget_stop.json",{"next_width":width,"remaining_s":remaining})
            break
        directory=args.output/f"width_{width:03d}"
        directory.mkdir(exist_ok=True)
        keep,left,right=retain(labels,support,width)
        selected,selected_bounds,selected_labels=subset(matrix,bounds,labels,keep,support)
        save_npz(directory/"matrix.npz",selected,compressed=True)
        np.savez_compressed(directory/"bounds.npz",**selected_bounds)
        pd.DataFrame(selected_labels).to_csv(directory/"row_metadata.csv.gz",index=False,compression="gzip")
        retained_dwell=[label for label in selected_labels if label["family"] in DWELL]
        pd.DataFrame(retained_dwell).to_csv(directory/"retained_dwell_rows.csv",index=False)
        result=solve_case(selected,selected_bounds,directory,selected_labels,30,p.size)
        result.update({"case":"seed_26092600","width":width,"left_hour_0based":left,"right_hour_0based":right,
            "retained_dwell_rows":len(retained_dwell),"rows":selected.shape[0],"columns":selected.shape[1],
            "matrix_sha256":sha(directory/"matrix.npz"),"bounds_sha256":sha(directory/"bounds.npz"),
            "global_transition_and_exclusivity_rows_retained":True,"complete_weekly_means_retained":True})
        if (directory/"dual_certificate.json").exists():
            certificate=json.loads((directory/"dual_certificate.json").read_text())
            active=[selected_labels[entry["row"]] for entry in certificate["multipliers"]]
            active_dwell=[label for label in active if label["family"] in DWELL]
            result["certificate_dwell_row_count"]=len(active_dwell)
            result["certificate_dwell_unit_names"]=sorted({label["uid"] for label in active_dwell})
            result["certificate_dwell_hours"]=sorted({hour for label in active_dwell for hour in range(label["dwell_support_first_hour"],label["dwell_support_last_hour"]+1)})
            pd.DataFrame(active_dwell).to_csv(directory/"certificate_dwell_rows.csv",index=False)
        save(directory/"result.json",result)
        result["archive_replay"]=replay(directory)
        save(directory/"result.json",result)
        records.append(result)
        save(args.output/"summary.json",records)
        pd.DataFrame([{k:v for k,v in item.items() if not isinstance(v,(dict,list))} for item in records]).to_csv(args.output/"summary.csv",index=False)
        print(json.dumps({key:result[key] for key in ("width","retained_dwell_rows","model_status","verdict","elapsed_s")}),flush=True)
    bind_sources()
    assert all(sha(Path(item["path"]))==item["sha256"] for item in manifest)
    save(args.output/"completion.json",{"completed_utc":datetime.now(timezone.utc).isoformat(),
        "phase_elapsed_s":time.monotonic()-phase_start,"case_count":len(records),"source_hashes_still_match":True,
        "shortest_examined_exact_rejecting_width":next((r["width"] for r in records if r["verdict"]=="REJECTED_EXACT_BINARY64_CERTIFICATE"),None)})


if __name__=="__main__":
    main()
