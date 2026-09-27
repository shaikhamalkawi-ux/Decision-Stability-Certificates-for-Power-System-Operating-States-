"""Read saved Auer outputs only: no producer import, clustering or solver."""
from collections import Counter
import hashlib
import itertools
import json
import math
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "results/research_next/auer_execution"
PRE = ROOT / "results/research_next/auer_projection_preflight"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hx(value):
    value = float(value)
    assert math.isfinite(value)
    return (0.0 if value == 0 else value).hex()


def keyed(records):
    return Counter(json.dumps(row, sort_keys=True, separators=(",", ":")) for row in records)


def canonical(tables, matrices):
    variants = []
    for new_to_old in itertools.permutations(range(3)):
        rename = {"rp%02d" % (old+1): "r%d" % new for new, old in enumerate(new_to_old)}
        candidate = {}
        for name in tables:
            rows = []
            for row in tables[name]:
                changed = dict(row)
                if "rp" in changed:
                    changed["rp"] = rename[changed["rp"]]
                rows.append(changed)
            candidate[name] = sorted(rows, key=lambda r: json.dumps(r, sort_keys=True))
        for name in matrices:
            candidate[name] = [[matrices[name][i][j] for j in new_to_old] for i in new_to_old]
        variants.append(json.dumps(candidate, sort_keys=True, separators=(",", ":")))
    return min(variants)


started = time.perf_counter()
assert sha(OUT / "outcomes.json") == "40dbf5db70cfc96f9397e1212941e153ab53ec6672e408efb4d35ed0cf96f0b3"
assert sha(OUT / "completion.json") == "4db94155b74e24d27036689be5fb387ca9e05264805e046e5f7572c9ef484e9c"
before = {str(p.relative_to(OUT)): sha(p) for p in OUT.rglob("*") if p.is_file()}
bindings = read(OUT / "input_manifest.json")["files"]
assert len(bindings) == 85 and len({r["path"].casefold() for r in bindings}) == 85
for row in bindings:
    p = Path(row["path"])
    assert p.stat().st_size == row["bytes"] and sha(p) == row["sha256"]
assert sha(ROOT / "src/researchnext_auer_execution.py") == "a18058186dde3dfe0dbd6717c27636e76ef59debbbcfbd36f7bb887c7a232d9c"
schedule = read(OUT / "schedule.json")["invocations"]
outcomes = read(OUT / "outcomes.json")
completion = read(OUT / "completion.json")
assert len(schedule) == len(outcomes["invocations"]) == 15
canonical_strings, durations, checks = [], [], []
for expected, recorded in zip(schedule, outcomes["invocations"]):
    assert recorded["invocation"] == expected["invocation"] and recorded["case"] == expected["case"]
    assert recorded["role"] == expected["comparison_role"] and recorded["status"] == "OBSERVATION_COMPUTED"
    folder = OUT / f"call_{expected['invocation']:02d}_{expected['case']}"
    projection = read(PRE / "prepared" / expected["projection_file"])
    assert sha(PRE / "prepared" / expected["projection_file"]) == expected["projection_sha256"]
    obs = read(folder / "observation.json")
    detail = read(folder / "clustering_details.json")
    solver = read(folder / "solver_result.json")
    termination = read(folder / "termination.json")
    ledger = read(folder / "call_ledger.json")
    inp = read(folder / "solver_input.json")
    assert read(folder / "result.json") == recorded
    assert ledger == solver["call_state"] == termination["call_state"]
    assert ledger["calls_started"] == recorded["calls_started"] == 1
    assert solver["status"] == termination["status"] == "ok"
    assert solver["termination"] == termination["termination"] == "optimal"
    assert recorded["solver_actual_seconds"] == ledger["actual_seconds"] >= 0
    durations.append(ledger["actual_seconds"])
    assert inp["options"] == {"TimeLimit":30,"Threads":1,"Seed":0,"MIPGap":0.0}
    assert inp["remaining_phase_seconds"] >= 35 and inp["binary_variables"] == 49 and inp["constraints"] == 57
    dist = [[float.fromhex(v) for v in row] for row in inp["distances_hex"]]
    assert len(dist) == 7 and all(len(row) == 7 and all(math.isfinite(v) for v in row) for row in dist)
    z = [[float.fromhex(v) for v in row] for row in solver["assignment_hex"]]
    assert len(z) == 7 and all(len(row) == 7 for row in z)
    assert all(math.isfinite(v) and abs(v-round(v)) <= 1e-6 and round(v) in (0,1) for row in z for v in row)
    binary = [[round(v) for v in row] for row in z]
    assert all(sum(binary[i][j] for i in range(7)) == 1 for j in range(7))
    facilities = [i for i in range(7) if binary[i][i]]
    assert len(facilities) == 3 and all(binary[i][j] <= binary[i][i] for i in range(7) for j in range(7))
    order = [facilities.index(next(i for i in range(7) if binary[i][j])) for j in range(7)]
    assert detail["cluster_order"] == order
    medoids = detail["medoid_source_day_indices"]
    assert len(medoids) == 3 and all(type(m) is int and 0 <= m < 7 and order[m] == rp for rp,m in enumerate(medoids))
    assert math.isfinite(float.fromhex(solver["objective_hex"]))
    normalized = detail["normalized_daily_profiles_hex"]
    assert len(normalized) == 7 and all(len(row) == 96 and all(math.isfinite(float.fromhex(v)) for v in row) for row in normalized)
    tables = obs["tables"]
    assert set(tables) == {"demand","profiles","inflows","weights_rp","weights_k"}
    # Verify full selected raw projection tables, rather than only feature sums.
    for name, identity, count in (("demand","i",1728),("profiles","g",792),("inflows","g",432)):
        wanted = []
        for rp, day in enumerate(medoids):
            for row in projection[name]:
                source_hour = int(row["k"][1:])-1
                if source_hour//24 == day:
                    wanted.append({"scenario":row["scenario"],"rp":f"rp{rp+1:02d}","k":f"k{source_hour%24+1:04d}",identity:str(row[identity]),"value":hx(row["value"])})
        assert len(wanted) == len(tables[name]) == count and keyed(wanted) == keyed(tables[name]), name
    weights = Counter(order)
    assert detail["weights"] == {str(k):weights[k] for k in range(3)}
    expected_rp = [{"scenario":"s1","rp":f"rp{r+1:02d}","pWeight_rp":hx(weights[r])} for r in range(3)]
    expected_k = [{"scenario":"s1","k":f"k{k:04d}","pWeight_k":hx(1)} for k in range(1,25)]
    assert keyed(tables["weights_rp"]) == keyed(expected_rp) and keyed(tables["weights_k"]) == keyed(expected_k)
    hindex = [{"p":f"h{d*24+k:04d}","rp":f"rp{order[d]+1:02d}","k":f"k{k:04d}"} for d in range(7) for k in range(1,25)]
    assert detail["hindex_provenance"] == hindex
    n = [[0]*3 for _ in range(3)]
    for a,b in zip(order[-1:]+order[:-1],order): n[a][b] += 1
    expected_matrices = {"N":[[hx(v) for v in row] for row in n],
                         "P_to":[[hx(n[i][j]/sum(n[i])) for j in range(3)] for i in range(3)],
                         "P_from":[[hx(n[i][j]/sum(n[k][j] for k in range(3))) for j in range(3)] for i in range(3)]}
    assert obs["matrices"] == expected_matrices
    recovered = canonical(tables,obs["matrices"])
    assert recovered == obs["canonical"] and hashlib.sha256(recovered.encode()).hexdigest() == obs["canonical_sha256"] == recorded["canonical_sha256"]
    canonical_strings.append(recovered)
    checks.append({"invocation":expected["invocation"],"case":expected["case"],"complete_selected_tables_exact":True,
                   "rounded_binary_assignment_valid":True,"cluster_order_matches_returned_assignment":True,
                   "medoid_is_in_its_cluster":True,"circular_counts_and_P_exact":True,"canonical_full_string_reproduced":True})
computed = []
for week in range(3):
    start = week*5
    assert canonical_strings[start] == canonical_strings[start+4]
    for offset in (1,2,3,4):
        pos = start+offset
        equal = canonical_strings[start] == canonical_strings[pos]
        computed.append({"week":week+1,"case":schedule[pos]["case"],"role":schedule[pos]["comparison_role"],
                         "identity_repeat_stable":True,"outcome":"EQUAL_COMPLETE_PROJECTED_OBSERVATION" if equal else "DISTINCT_COMPLETE_PROJECTED_OBSERVATION","UC_feasibility_tested":False})
assert computed == outcomes["comparisons"]
assert all(r["outcome"].startswith("DISTINCT") for r in computed if r["role"] != "identity_repeat")
assert completion["status"] == "COMPLETE" and completion["invocation_denominator"] == completion["calls_started"] == 15
assert completion["solver_seconds"] == math.fsum(durations) and completion["unknowns"] == completion["uc_calls"] == 0
assert completion["solver_soft_overruns"] == [] and all(t <= 30 for t in durations)
assert completion["phase_seconds"] < completion["phase_guard_seconds"] == 900 and completion["phase_overrun"] == 0
for row in bindings: assert sha(Path(row["path"])) == row["sha256"]
after = {str(p.relative_to(OUT)): sha(p) for p in OUT.rglob("*") if p.is_file()}
assert after == before
report = {"status":"PASS_SAVED_OUTPUT_AND_CLAIM_AUDIT","reviewer_source_sha256":sha(Path(__file__)),
          "input_bindings_unchanged":85,"producer_files_unchanged":len(before),"producer_snapshot":before,
          "invocation_checks":checks,"comparisons":computed,"six_targets_distinct":True,"three_controls_distinct":True,"three_repeats_equal":True,
          "unknowns":0,"producer_clustering_calls":15,"producer_uc_calls":0,"producer_solver_seconds":completion["solver_seconds"],
          "producer_phase_seconds":completion["phase_seconds"],"reviewer_optimizer_calls":0,"reviewer_clustering_calls":0,"producer_imports":0,
          "scope":"Saved output mapping, rounded assignment, transitions, canonical equality and accounting; no re-clustering, exact optimality proof or physical UC equivalence.",
          "elapsed_before_report_write_seconds":time.perf_counter()-started}
path = PRE/"INDEPENDENT_EXECUTION_RESULT_REVIEW.json"
with path.open("x",encoding="utf-8") as f:json.dump(report,f,indent=2);f.write("\n")
print(json.dumps({"status":report["status"],"producer_files_unchanged":len(before),"report_sha256":sha(path),"seconds":report["elapsed_before_report_write_seconds"]}))
