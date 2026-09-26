"""Exact raw-observation and transition-graph audit; no optimization or quantization."""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode=True
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/"docs/research8h/OBSERVATION_AUDIT.md"
BOUND_SOURCES={"v8r1_rts_seasonal.py":"bca0127d7b2771c6da3b6a838c8caa7fb6ce0df4eafd9a512326aabd8daf7dc2",
    "temporal_information_pilot.py":"f2e50b7dccb0e1869c8667a00e32c9d2f1d3f1f641459d4ccb802abe0074d4a0"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path,value):
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+"\n",encoding="utf-8")


for name,expected in BOUND_SOURCES.items():
    assert sha(ROOT/"src"/name)==expected,(name,"bound source changed")
from v8r1_rts_seasonal import inputs,load_model
from temporal_information_pilot import nodal_check


def bigrams(states):
    return Counter(zip(states[:-1],states[1:]))


def graph_check(states):
    counts=Counter(states)
    edges=bigrams(states)
    successors,predecessors=defaultdict(set),defaultdict(set)
    out_degree,in_degree=Counter(),Counter()
    for (left,right),count in edges.items():
        successors[left].add(right);predecessors[right].add(left)
        out_degree[left]+=count;in_degree[right]+=count
    degree=[{"state_id":state,"observations":counts[state],"distinct_successors":len(successors[state]),
        "distinct_predecessors":len(predecessors[state]),"out_edge_occurrences":out_degree[state],
        "in_edge_occurrences":in_degree[state]} for state in sorted(counts)]
    summary={"hours":len(states),"unique_states":len(counts),"repeated_state_classes":sum(n>1 for n in counts.values()),
        "observations_in_repeated_classes":sum(n for n in counts.values() if n>1),
        "repeated_observations_beyond_first":sum(n-1 for n in counts.values()),"maximum_state_multiplicity":max(counts.values()),
        "bigram_occurrences":sum(edges.values()),"unique_bigram_types":len(edges),
        "repeated_bigram_types":sum(n>1 for n in edges.values()),"self_loop_occurrences":sum(n for (a,b),n in edges.items() if a==b),
        "distinct_successor_branching_states":[s for s in sorted(counts) if len(successors[s])>1],
        "distinct_predecessor_branching_states":[s for s in sorted(counts) if len(predecessors[s])>1],
        "start_state":states[0],"end_state":states[-1],"Euler_trail_count":"NOT_ENUMERATED"}
    summary["nontrivial_successor_branching"]=bool(summary["distinct_successor_branching_states"])
    reconstruction={"applicable_all_states_distinct":len(counts)==len(states),
        "uniqueness_verdict":"NOT_ESTABLISHED_BY_THIS_SIMPLE_PATH_TEST"}
    if len(counts)==len(states):
        start,end=states[0],states[-1]
        assert start!=end and len(edges)==len(states)-1 and all(n==1 for n in edges.values())
        assert (in_degree[start],out_degree[start])==(0,1)
        assert (in_degree[end],out_degree[end])==(1,0)
        assert all((in_degree[s],out_degree[s])==(1,1) for s in counts if s not in {start,end})
        remaining=edges.copy();recovered=[start]
        for _ in range(len(states)-1):
            options=[right for right in successors[recovered[-1]] if remaining[(recovered[-1],right)]>0]
            assert len(options)==1
            edge=(recovered[-1],options[0]);remaining[edge]-=1;recovered.append(options[0])
        assert recovered==states and recovered[-1]==end and not any(remaining.values())
        reconstruction.update({"uniqueness_verdict":"UNIQUE_EXACT_LABELLED_CHRONOLOGY",
            "simple_path_degree_check":True,"complete_edge_consumption":True,"recovered_state_sequence":recovered,
            "argument":"The sole outgoing edge forces each successor by induction from the fixed start."})
    return summary,degree,edges,reconstruction


def audit_alphabet(name,array,columns,output,byte_dtype):
    assert array.shape==(168,len(columns)) and np.isfinite(array).all()
    encoded=np.asarray(array,dtype=byte_dtype)
    keys=[row.tobytes() for row in encoded]
    unique=sorted(set(keys))
    mapping={key:index for index,key in enumerate(unique)}
    states=[mapping[key] for key in keys]
    hashes={hashlib.sha256(key).hexdigest() for key in unique}
    assert len(hashes)==len(unique),"Hash collision; bytes remain primary labels"
    counts=Counter(keys)
    dictionary=[{"state_id":mapping[key],"sha256":hashlib.sha256(key).hexdigest(),"observations":counts[key],
        "exact_row_bytes_hex":key.hex()} for key in unique]
    summary,degree,edges,reconstruction=graph_check(states)
    summary.update({"alphabet":name,"coordinates":len(columns),"key_dtype":byte_dtype,
        "key_includes_timestamp_or_native_row":False,"key_includes_dispatch_P":False,
        "key_includes_commitment_U":name=="endogenous_U24"})
    if byte_dtype=="<f8":
        summary["negative_zero_coordinates"]=int(np.count_nonzero((array==0)&np.signbit(array)))
        summary["exact_numerical_tuple_unique_states"]=len({tuple(float(x) for x in row) for row in array})
        summary["byte_and_exact_numerical_class_counts_agree"]=summary["exact_numerical_tuple_unique_states"]==len(unique)
    directory=output/name
    directory.mkdir()
    pd.DataFrame(dictionary).to_csv(directory/"state_dictionary.csv",index=False)
    pd.DataFrame(degree).to_csv(directory/"state_degrees.csv",index=False)
    pd.DataFrame([{"from_state":a,"to_state":b,"count":n} for (a,b),n in sorted(edges.items())]).to_csv(directory/"bigram_counts.csv",index=False)
    pd.DataFrame({"hour_0based":range(168),"state_id":states}).to_csv(directory/"state_sequence.csv",index=False)
    diagnostics=[{"column":label,"unique_exact_values":len({float(x) for x in array[:,j]})} for j,label in enumerate(columns)]
    pd.DataFrame(diagnostics).to_csv(directory/"coordinate_unique_counts.csv",index=False)
    save(directory/"columns.json",columns)
    save(directory/"reconstruction_check.json",reconstruction)
    save(directory/"summary.json",summary)
    np.savez_compressed(directory/"exact_observation_array.npz",values=encoded)
    return summary,states


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-v3",type=Path,required=True)
    parser.add_argument("--output",type=Path,default=ROOT/"results/research8h/observation_audit")
    args=parser.parse_args()
    if (args.output/"summary.json").exists():
        raise FileExistsError("Preserve existing audit; use a new output directory for a separately defined run")
    args.output.mkdir(parents=True,exist_ok=True)
    source=load_model(args.source_v3)
    columns,_,pmin,pmax,demand,paths=inputs(source,args.source_v3,7)
    hourly=pd.read_csv(paths[1]);rows=hourly["row"].to_numpy(int)
    p_path=ROOT/"results/v8/network_repair/network_repair_dispatch.csv"
    u_path=ROOT/"results/v8/network_repair/network_fixed_commitment.csv"
    p=pd.read_csv(p_path)[columns].to_numpy(float)
    thermal_names=source.dec.iloc[np.flatnonzero(source.thermal.to_numpy(bool))]["GEN UID"].tolist()
    u=pd.read_csv(u_path)[thermal_names].to_numpy(float)
    assert u.shape==(168,24) and np.isin(u,[0,1]).all()
    network,nodal=nodal_check(source,p,rows)
    assert network["pass"]
    direct=np.asarray([source.prop*float(source.load_ts.loc[int(row),str(source.AREA)])-source.rtpv_at(int(row)) for row in rows])
    assert np.array_equal(nodal,direct) and nodal.shape==(168,24) and pmin.shape==pmax.shape==(168,41)
    save(args.output/"source_grounding.json",{"nodal_reconstruction_exact_match":True,"network_witness":network,
        "max_nodal_sum_minus_aggregate_MW":float(np.abs(nodal.sum(axis=1)-demand).max()),
        "P_used_only_for_existing_network_witness_check_not_exogenous_state_key":True})
    bound_columns=[f"pmin::{uid}" for uid in columns]+[f"pmax::{uid}" for uid in columns]
    specifications=[("full_exogenous",np.column_stack([nodal,pmin,pmax]),[f"nodal_net_load::{bus}" for bus in source.busids]+bound_columns,"<f8"),
        ("aggregate_exogenous",np.column_stack([demand,pmin,pmax]),["aggregate_net_demand"]+bound_columns,"<f8"),
        ("endogenous_U24",u,[f"U::{uid}" for uid in thermal_names],"u1")]
    orders=[]
    for seed in range(260926100,260926116):
        path=ROOT/f"results/research8h/markov_twins/seed_{seed}/permutation.csv"
        order=pd.read_csv(path)["source_hour_0based"].to_numpy(int)
        assert np.array_equal(np.sort(order),np.arange(168))
        assert np.array_equal(order[:48],np.arange(48)) and np.array_equal(order[120:],np.arange(120,168))
        orders.append((seed,path,order))
    used=[Path(__file__),PROTOCOL,*[ROOT/"src"/name for name in BOUND_SOURCES],p_path,u_path,*paths,
        args.source_v3/"code/dscgrid_model.py",*sorted((args.source_v3/"raw").rglob("*.csv")),*[path for _,path,_ in orders]]
    manifest=[{"path":str(path),"sha256":sha(path),"bytes":path.stat().st_size} for path in dict.fromkeys(used)]
    pd.DataFrame(manifest).to_csv(args.output/"input_manifest.csv",index=False)
    save(args.output/"definitions_record.json",{"utc":datetime.now(timezone.utc).isoformat(),"protocol_sha256":sha(PROTOCOL),
        "script_sha256":sha(Path(__file__)),"hours":168,"no_optimization":True,"no_quantization":True,
        "byte_equality":"exact little-endian binary64 exogenous rows; uint8 commitment rows; no P/timestamp in exogenous key"})
    summaries=[];comparison=[]
    for name,array,names,dtype in specifications:
        summary,states=audit_alphabet(name,array,names,args.output,dtype)
        original=bigrams(states)
        ambiguities=[]
        for seed,path,order in orders:
            permuted=[states[i] for i in order]
            alternative=bigrams(permuted)
            preserved=alternative==original
            changed=permuted!=states
            record={"alphabet":name,"seed":seed,"state_sequence_changed":changed,
                "bigram_counts_exactly_preserved":preserved,"endpoints_preserved":permuted[0]==states[0] and permuted[-1]==states[-1],
                "bigram_count_L1_difference":sum(abs(original[e]-alternative[e]) for e in set(original)|set(alternative))}
            comparison.append(record)
            if changed and preserved and record["endpoints_preserved"]:
                ambiguities.append(seed)
        summary["archived_Markov_orders_preserving_bigrams"]=sum(r["alphabet"]==name and r["bigram_counts_exactly_preserved"] for r in comparison)
        summary["concrete_alternative_label_sequence_seeds"]=ambiguities
        summary["observed_nonuniqueness_witness_exists"]=bool(ambiguities)
        if summary["unique_states"]==168:
            assert not ambiguities
        summaries.append(summary)
        save(args.output/name/"summary.json",summary)
    pd.DataFrame(comparison).to_csv(args.output/"archived_markov_comparison.csv",index=False)
    pd.DataFrame({"hour_0based":range(168),"source_native_row":rows,"timestamp":hourly["timestamp"]}).to_csv(args.output/"hour_mapping.csv",index=False)
    save(args.output/"summary.json",summaries)
    pd.DataFrame([{k:v for k,v in row.items() if not isinstance(v,(list,dict))} for row in summaries]).to_csv(args.output/"summary.csv",index=False)
    assert all(sha(Path(entry["path"]))==entry["sha256"] for entry in manifest)
    save(args.output/"completion.json",{"utc":datetime.now(timezone.utc).isoformat(),"source_hashes_match":True,
        "alphabets":3,"archived_permutations_compared":16,"new_optimizations":0,"new_permutation_searches":0})
    print(json.dumps(summaries,indent=2),flush=True)


if __name__=="__main__":
    main()
