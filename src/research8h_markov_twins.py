"""Fixed Euler-trail test preserving exact full-commitment transition counts."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import save_npz

from temporal_information_pilot import nodal_check, transitions
from temporal_lp_certificate import assemble, check_vector, digest, save, solve_case
from v8r1_rts_seasonal import inputs, load_model, verify

ROOT = Path(__file__).resolve().parents[1]
SEEDS = list(range(260926100, 260926116))


def pairs(states):
    return Counter(zip(states[:-1], states[1:]))


def euler_order(states, seed):
    outgoing = {}
    for hour in range(48, 120):
        outgoing.setdefault(states[hour], []).append(hour)
    rng = np.random.Generator(np.random.PCG64(seed))
    for state in sorted(outgoing):
        rng.shuffle(outgoing[state])
    node_stack = [states[48]]
    edge_stack, reverse_path = [], []
    while node_stack:
        current = node_stack[-1]
        if outgoing.get(current):
            edge = outgoing[current].pop()
            edge_stack.append(edge)
            node_stack.append(states[edge + 1])
        else:
            node_stack.pop()
            if edge_stack:
                reverse_path.append(edge_stack.pop())
    path = list(reversed(reverse_path))
    assert sorted(path) == list(range(48, 120))
    assert states[path[0]] == states[48] and states[path[-1] + 1] == states[120]
    assert all(states[left + 1] == states[right] for left, right in zip(path[:-1], path[1:]))
    order = np.arange(168)
    order[48:120] = path
    assert pairs([states[h] for h in order]) == pairs(states)
    return order


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-v3", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "results/research8h/markov_twins")
    args = parser.parse_args()
    if (args.output / "summary.json").exists():
        raise FileExistsError("Preserve previous results; choose a fresh output directory.")
    args.output.mkdir(parents=True, exist_ok=True)
    protocol = ROOT / "docs/research8h/MARKOV_TWINS_PROTOCOL.md"
    save(args.output / "pre_run_freeze.json", {"protocol_sha256": digest(protocol),
         "script_sha256": digest(Path(__file__)), "seeds": SEEDS, "seconds_per_LP": 30,
         "sampling": "randomized outgoing-edge Hierholzer, not uniform over Euler trails",
         "phase": "prospective fixed sample from previously studied July witness"})
    model = load_model(args.source_v3)
    columns, _, pmin, pmax, demand, source_paths = inputs(model, args.source_v3, 7)
    rows = pd.read_csv(source_paths[1])["row"].to_numpy(int)
    witness = ROOT / "results/v8/network_repair"
    p_path, u_path = witness / "network_repair_dispatch.csv", witness / "network_fixed_commitment.csv"
    p = pd.read_csv(p_path)[columns].to_numpy(float)
    u = pd.read_csv(u_path)[model.dec.iloc[model.urows]["GEN UID"]].to_numpy(float)
    y, z = transitions(u)
    original = verify(model, p, u, pmin, pmax, demand, p.mean(0), "minud", y, z)
    network, nodal = nodal_check(model, p, rows)
    assert original["pass"] and network["pass"]
    states = [tuple(int(value) for value in row) for row in np.rint(u)]
    package = np.column_stack([rows, nodal, pmin, pmax, p, u])
    package_hash = hashlib.sha256(np.ascontiguousarray(package).tobytes()).hexdigest()
    dictionary = {state: i for i, state in enumerate(sorted(set(states)))}
    pd.DataFrame([{"state_id": index, "commitment_bits": "".join(map(str, state))}
                  for state, index in dictionary.items()]).to_csv(args.output / "state_dictionary.csv", index=False)
    pd.DataFrame([{"from_state": dictionary[left], "to_state": dictionary[right], "count": count}
                  for (left, right), count in sorted(pairs(states).items())]).to_csv(
                      args.output / "unchanged_global_transition_counts.csv", index=False)
    save(args.output / "positive_control.json", {"chronology": original, "network": network,
        "state_definition": "complete endogenous 24-unit binary commitment vector", "unique_states": len(dictionary)})
    matrix, bounds, metadata, _ = assemble(model, pmin, pmax, demand, p.mean(0))
    baseline_vector = np.concatenate([a.ravel() for a in (p, u, y, z)])
    assert check_vector(matrix, bounds, baseline_vector)["pass"]
    summaries, seen_orders, seen_states = [], set(), set()
    for seed in SEEDS:
        order = euler_order(states, seed)
        directory = args.output / f"seed_{seed}"
        directory.mkdir()
        assert np.array_equal(order[:48], np.arange(48)) and np.array_equal(order[120:], np.arange(120, 168))
        assert np.array_equal(package[order][np.argsort(order)], package)
        preserved = hashlib.sha256(np.ascontiguousarray(package[order][np.argsort(order)]).tobytes()).hexdigest()
        assert preserved == package_hash
        permuted_states = [states[t] for t in order]
        assert pairs(permuted_states) == pairs(states)
        mean_error = float(np.max(np.abs(p[order].mean(0) - p.mean(0))))
        assert mean_error < 1e-9
        py, pz = transitions(u[order])
        replay = verify(model, p[order], u[order], pmin[order], pmax[order], demand[order], p.mean(0), "minud", py, pz)
        static = verify(model, p[order], u[order], pmin[order], pmax[order], demand[order], p.mean(0), "ramp")
        static_network, _ = nodal_check(model, p[order], rows[order])
        assert static["pass"] and static_network["pass"]
        full_positive = replay["pass"] and static["pass"] and static_network["pass"]
        pd.DataFrame({"new_hour_0based": np.arange(168), "source_hour_0based": order,
            "source_native_row": rows[order], "state_id": [dictionary[s] for s in permuted_states]}).to_csv(directory / "permutation.csv", index=False)
        save(directory / "preservation_and_witness.json", {"package_inverse_restoration_sha256": preserved,
            "original_package_sha256": package_hash, "global_transition_counts_exact": True,
            "fixed_edges": True, "mean_error_MW": mean_error, "seed_chronology": replay,
            "static_and_ramp": static, "static_network": static_network,
            "seed_is_full_network_chronology_witness": full_positive})
        matrix, bounds, metadata, labels = assemble(model, pmin[order], pmax[order], demand[order], p.mean(0))
        save_npz(directory / "matrix.npz", matrix)
        np.savez_compressed(directory / "bounds.npz", **bounds)
        save(directory / "model_metadata.json", metadata)
        result = solve_case(matrix, bounds, directory, labels, 30, p.size)
        result.update({"case": f"seed_{seed}", "matrix_sha256": digest(directory / "matrix.npz"),
                       "bounds_sha256": digest(directory / "bounds.npz")})
        save(directory / "lp_result.json", result)
        negative = result["verdict"] == "REJECTED_EXACT_BINARY64_CERTIFICATE"
        assert not (negative and full_positive), "Contradiction between seed witness and LP certificate"
        combined = "ADMITTED_NETWORK_WITNESS" if full_positive else ("REJECTED_EXACT_BINARY64_CERTIFICATE" if negative else "UNKNOWN")
        order_key = tuple(int(v) for v in order)
        state_key = tuple(permuted_states)
        summaries.append({"seed": seed, "verdict": combined, "LP_verdict": result["verdict"],
            "LP_seconds": result["elapsed_s"], "seed_residence_violations": replay["residuals"]["residence_violations"],
            "raw_order_previously_seen": order_key in seen_orders, "state_sequence_previously_seen": state_key in seen_states,
            "commitment_sequence_identical_to_original": state_key == tuple(states),
            "changed_hour_positions": int(np.count_nonzero(order != np.arange(168))),
            "transition_count_preservation": "PASS", "package_multiset_preservation": "PASS"})
        seen_orders.add(order_key); seen_states.add(state_key)
        save(args.output / "summary.json", summaries)
        pd.DataFrame(summaries).to_csv(args.output / "summary.csv", index=False)
        print(json.dumps(summaries[-1]), flush=True)
    save(args.output / "overview.json", {"cases": len(summaries), "unique_raw_orders": len(seen_orders),
        "unique_commitment_sequences": len(seen_states), "verdict_counts": dict(Counter(r["verdict"] for r in summaries)),
        "meaning": "Commitment-state one-step counts are preserved, not exogenous representative-period transition statistics."})
    used = [Path(__file__), protocol, ROOT / "src/temporal_lp_certificate.py", ROOT / "src/temporal_information_pilot.py",
            ROOT / "src/v8r1_rts_seasonal.py", p_path, u_path, *source_paths,
            args.source_v3 / "code/dscgrid_model.py", *sorted((args.source_v3 / "raw").rglob("*.csv"))]
    pd.DataFrame([{"path": str(path), "sha256": digest(path), "bytes": path.stat().st_size} for path in dict.fromkeys(used)]).to_csv(
        args.output / "input_manifest.csv", index=False)


if __name__ == "__main__":
    main()
