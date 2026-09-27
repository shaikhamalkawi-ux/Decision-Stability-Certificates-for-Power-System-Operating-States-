"""Link saved, independently checked observations to historical recourse proofs.

No optimization, model construction, clustering or numerical proof replay.
Requires the historical Git object and original prepared paths to be available.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import subprocess
import time
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

BASE_COMMIT = "d0c4be05899b70797902f191f0062ac898ea7137"
OLD = "results/research8h/day_fixed_identity"
NEW = "results/research_next/whole_day_observation_preflight"
ORDERS = ("132", "213", "231", "312", "321")
PINNED = {
    NEW + "/run01/outcomes.json": "094a603e382a2f4d4b0fd6dd38f2a889ac664e46fea16389d3b226e0339f0bce",
    NEW + "/run01/completion.json": "716683064c992b12b600edf91dea3a42131b9d6241e7b1e5e5d742bb30dfcb8b",
    NEW + "/INDEPENDENT_RESULT_REVIEW.json": "67ec0ae2a75e5c1b239143b5f63f3bca317f4d6f2ec2e0ac4e1b30143a3a441d",
    OLD + "/input_manifest.json": "6158935e240ac3e20918c40964d9f86ae9b6eb6a1cb6dc8c01ba2c16c1125f60",
    OLD + "/identity_control.json": "175ac8142ace70a21cf6a4b2d66708ca1c02f481aaeb9429d73e8749bb3f086c",
    OLD + "/identity_state_anchor.npz": "63a9a79ebd01cf594b5fbc7bac1d5af809563defbc9b8ce369c175ba98acbb16",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    out = args.out.resolve()
    require(not out.exists(), "Output already exists; no silent retry/overwrite")
    require(out.is_relative_to(root / "results/research_next"), "Output scope")
    start = time.perf_counter()
    snapshot = {}
    external_allowed = {}
    historical_git_verified = []

    def read(path, expected=None):
        p = Path(path)
        if not p.is_absolute():
            p = root / p
        p = p.resolve()
        internal = p.is_relative_to(root)
        require(internal or p in external_allowed, "Input outside repository and pinned manifests")
        rel = p.relative_to(root).as_posix() if internal else p.as_posix()
        data = p.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if expected is not None:
            require(digest == expected, "Hash mismatch: " + rel)
        if not internal:
            require(digest == external_allowed[p], "External pinned input differs")
        record = {"sha256": digest, "bytes": len(data)}
        if rel in snapshot:
            require(snapshot[rel] == record, "Input changed while reading: " + rel)
        snapshot[rel] = record
        return data

    def load(path):
        return json.loads(read(path))

    def historical(path):
        current = read(path)
        archived = subprocess.run(
            ["git", "show", BASE_COMMIT + ":" + path], cwd=root,
            check=True, capture_output=True,
        ).stdout
        require(current == archived, "Historical Git object differs: " + path)
        historical_git_verified.append(path)
        return json.loads(current) if path.endswith(".json") else current

    read(Path(__file__).resolve())
    read("docs/research_next/WHOLE_DAY_FIXED_COMMITMENT_LINK_PROTOCOL.md")
    for path, digest in PINNED.items():
        read(path, digest)
    review = historical(OLD + "/independent_review.json")
    historical("docs/research8h/DAY_FIXED_IDENTITY_PROTOCOL.md")
    historical("src/research8h_day_fixed_identity.py")
    control = historical(OLD + "/identity_control.json")
    old_manifest = historical(OLD + "/input_manifest.json")
    historical(OLD + "/identity_state_anchor.npz")
    prepared_cases = historical(OLD + "/prepared_cases.json")
    require(review["status"] == "PASS_COMPLETE", "Old review incomplete")
    require(review["denominator"] == review["fixed_schedule_robust_negatives"] == 5, "Old denominator")
    require(review["unknown"] == 0, "Old negative unknown")
    require(review["all_200_frozen_hashes_and_byte_counts_pass"], "Old review binding failure")
    require(len(old_manifest) == 200, "Old manifest denominator")
    for item in old_manifest:
        p = Path(item["path"]).resolve()
        if not p.is_relative_to(root):
            external_allowed[p] = item["sha256"]
    for item in old_manifest:
        require(len(read(item["path"], item["sha256"])) == item["bytes"], "Old input length")
    identity = control["exact_fixed_model"]
    require(identity["expanded_pass"] and identity["original_binary_coordinates_exact"], "Identity witness")
    require(not identity["strict_pass"], "Unexpected nominal control scope")
    require(Fraction(int(identity["tau"]["numerator"]), int(identity["tau"]["denominator"])) == Fraction.from_float(1e-5), "Tau")
    require(control["native_full_model"]["pass"] and control["native_full_model"]["budget_MWh"] == 23195, "Native control scope")

    # The observer used an older identical identity model in a different folder.
    # Gzip headers differ, so compare decompressed row metadata explicitly.
    identity_bridge = []
    for filename in ("matrix.npz", "bounds.npz", "integrality.npz", "native_inputs.npz", "model_metadata.json", "row_metadata.csv.gz"):
        a = "results/research8h/seasonal_transfer/january_identity/" + filename
        b = "results/research8h/hour_of_day/january_identity/" + filename
        av, bv = read(a), read(b)
        mode = "identical_file_bytes"
        if filename.endswith(".gz"):
            mode = "identical_decompressed_bytes"
            av, bv = gzip.decompress(av), gzip.decompress(bv)
        require(av == bv, "Identity model bridge: " + filename)
        identity_bridge.append({"file": filename, "old": a, "observer": b, "comparison": mode, "compared_sha256": hashlib.sha256(av).hexdigest()})

    independent = load(NEW + "/INDEPENDENT_RESULT_REVIEW.json")
    require(independent["status"] == "PASS_SAVED_OUTPUT_AND_CLAIM_AUDIT", "New observation review failed")
    require(independent["target_denominator"] == 15 and independent["invocation_denominator"] == 21, "New denominator")
    require(independent["unknowns"] == 0 and independent["all_three_joint_identity_repeats_equal"], "New outcome scope")
    for rel, digest in independent["producer_snapshot"].items():
        read(NEW + "/run01/" + rel, digest)
    completion = load(NEW + "/run01/completion.json")
    require(len(completion["prepared_transport_bindings"]) == 4, "Transport denominator")
    for item in completion["prepared_transport_bindings"]:
        require(len(read(item["path"], item["sha256"])) == item["bytes"], "Transport length")
    new_manifest = load(NEW + "/prepared/input_manifest.json")["files"]
    require(len(new_manifest) == 170, "New input denominator")
    for item in new_manifest:
        p = Path(item["path"]).resolve()
        if not p.is_relative_to(root):
            require(p not in external_allowed or external_allowed[p] == item["sha256"], "Conflicting external binding")
            external_allowed[p] = item["sha256"]
    for item in new_manifest:
        require(len(read(item["path"], item["sha256"])) == item["bytes"], "New input length")
    cases = load(NEW + "/prepared/cases.json")["cases"]
    load(NEW + "/prepared/schedule.json")
    load(NEW + "/prepared/prepared_freeze.json")
    outcomes = load(NEW + "/run01/outcomes.json")
    require(outcomes["comparisons"] == independent["comparisons"], "Independent comparison disagreement")
    require(len(outcomes["invocations"]) == 21, "Complete call ledger")
    rows = []
    for order in ORDERS:
        name = "days_" + order
        case_name = "week_1_" + name
        comparison = next(c for c in outcomes["comparisons"] if c["case"] == case_name and c["role"] == "target")
        case = next(c for c in cases if c["case"] == case_name)
        native = next(c for c in independent["native_input_checks"] if c["case"] == case_name)
        require(native["actual_107_coordinate_sequence_changed"], "Trivial target")
        require(case["day_order"] == [int(c) for c in order], "Order mapping")
        binding = historical(OLD + "/" + name + "/model_binding.json")
        require(binding == next(c for c in prepared_cases if c["case"] == name), "Prepared binding mismatch")
        old_native = "results/research8h/day_blocks/" + name + "/native_inputs.npz"
        require(Path(case["native_input_path"]).resolve() == (root / old_native).resolve(), "Not same native archive")
        read(old_native, binding["native_inputs_sha256"])
        read("results/research8h/day_blocks/" + name + "/matrix.npz", binding["parent_matrix_sha256"])
        read("results/research8h/day_blocks/" + name + "/bounds.npz", binding["parent_bounds_sha256"])
        require(binding["fixed_state_columns"] == 12096 and binding["cap_MWh"] == 23195 and binding["mean_rows"] == 0, "Fixed model scope")
        require(binding["matrix_exact_parent_copy"] and binding["all_row_bounds_unchanged"] and binding["P_theta_bounds_bitwise_unchanged"], "Not only state fixation")
        require(binding["anchor_sha256"] == PINNED[OLD + "/identity_state_anchor.npz"], "Different commitment")
        prior = next(c for c in review["cases"] if c["case"] == name)
        require(prior["verdict"] == "REJECTED_FIXED_IDENTITY_SCHEDULE_EXACT_EXPANDED_CERTIFICATE", "Old verdict")
        for filename, digest in prior["output_artifact_sha256"].items():
            read(OLD + "/" + name + "/" + filename, digest)
        certificate = historical(OLD + "/" + name + "/fixed_schedule_certificate.json")
        verification = certificate["verification"]
        gap = Fraction(int(verification["exact_robust_gap_numerator"]), int(verification["exact_robust_gap_denominator"]))
        reviewed_gap = prior["independent_certificate_replay"]["robust_gap"]
        require(gap == Fraction(int(reviewed_gap["numerator"]), int(reviewed_gap["denominator"])) and gap > 0, "Saved exact gap disagreement")
        require(verification["pass"] and verification["robust_pass"], "Saved proof status")
        require(prior["independent_certificate_replay"]["scope_fixed_identity_only"], "Scope mismatch")
        metadata = list(csv.DictReader(io.StringIO(gzip.decompress(read(OLD + "/" + name + "/row_metadata.csv.gz")).decode("utf-8"))))
        selected_rows = []
        for multiplier in certificate["multipliers"]:
            row_index = multiplier["row"]
            m = metadata[row_index]
            require(int(m["row"]) == row_index, "Metadata row indexing")
            selected_rows.append({**m, "multiplier_hex": multiplier["value_hex"]})
        hours = sorted({int(m["hour_0based"]) for m in selected_rows if m["hour_0based"] not in ("", "-1")})
        families = sorted({m["family"] for m in selected_rows})
        single_hour_capacity_rows = len(hours) == 1 and set(families) <= {"aggregate_balance", "thermal_upper"}
        rows.append({
            "case": case_name, "day_order": case["day_order"], "link": "PASS_SAVED_EVIDENCE_LINK",
            "primary_observation": comparison["primary_outcome"],
            "primary_plus_full_hindex": comparison["primary_plus_hindex_outcome"],
            "actual_native_hours_changed": native["physical_hour_positions_changed"],
            "identity_fixed_commitment_predicate": True, "target_fixed_commitment_predicate": False,
            "historical_robust_gap": reviewed_gap,
            "selected_certificate_rows": selected_rows,
            "selected_row_families": families, "selected_hours_0based": hours,
            "single_hour_balance_and_capacity_row_certificate": single_hour_capacity_rows,
            "historical_unrestricted_target": "EXPANDED_BINARY_FEASIBLE" if binding["old_constructive_full_positive"] else "UNKNOWN",
            "primary_fixed_recourse_counterexample": comparison["primary_equal"],
            "joint_fixed_recourse_counterexample": comparison["primary_and_hindex_equal"],
            "unrestricted_uc_infeasibility_inferred": False,
        })

    # Recheck captured inputs once; this is a hash check, not a proof replay.
    for rel, entry in list(snapshot.items()):
        read(rel, entry["sha256"])
    report = {
        "status": "PASS_SAVED_EVIDENCE_LINK", "utc": datetime.now(timezone.utc).isoformat(),
        "historical_git_commit": BASE_COMMIT, "historical_git_verified_files": historical_git_verified,
        "identity_model_bridge": identity_bridge, "denominator": 5, "rows": rows,
        "primary_counterexamples": sum(r["primary_fixed_recourse_counterexample"] for r in rows),
        "joint_counterexamples": sum(r["joint_fixed_recourse_counterexample"] for r in rows),
        "input_binding_count": len(snapshot), "inputs_unchanged": True,
        "new_optimizer_calls": 0, "new_clustering_calls": 0, "old_proof_replays": 0,
        "elapsed_before_write_seconds": time.perf_counter() - start,
        "scope": "Archived exact tau-expanded fixed-identity-commitment recourse predicate. A saved-proof linkage, not a new operating experiment or independent numerical proof replay. Nominal-strict identity positive is unavailable. No claim about unrestricted UC cost/feasibility, a common alternative commitment, or the published author's reconstructed reference.",
        "limitation": "Primary-plus-Hindex equality hides within-cluster physical profile information; it does not establish that the chronological cluster-label sequence was lost. The days321 proof selects only hour119 aggregate balance and thermal upper-bound rows, plus variable box bounds: no selected intertemporal or energy-cap row. It demonstrates a one-hour fixed-commitment capacity rejection, not an isolated ramp/dwell mechanism. No scientific-priority claim.",
    }
    out.mkdir(parents=True)
    (out / "input_bindings.json").write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("status", "denominator", "primary_counterexamples", "joint_counterexamples", "input_binding_count", "elapsed_before_write_seconds")}))


if __name__ == "__main__":
    main()
