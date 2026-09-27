"""Post-hoc affine budget diagnostic; no model generation or optimization.

Read the closed fixed-ray family records using exact rational arithmetic.
The cap changes only its RHS, so G(C) = G(C0) + d_cap * (C-C0).
This does not select or run new caps and is not a second proof replay.
"""
import csv
import gzip
import hashlib
import io
import json
from fractions import Fraction as Q
from pathlib import Path
from time import perf_counter
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "results/research_next/hod_ray_stress"
RUN = BASE / "run01"
COMPLETION_SHA = "ac6b1da871bed6d24c229c6855acc447f37fbdfe0836a0ba1b3f75ad992be64b"


def rational(value):
    return Q(int(value["numerator"]), int(value["denominator"]))


def encode(value):
    return {"numerator": str(value.numerator),
            "denominator": str(value.denominator), "display": float(value)}


def main():
    started = perf_counter()
    bindings = {}

    def read(path):
        raw = path.read_bytes()
        bindings[str(path.relative_to(ROOT)).replace("\\", "/")] = hashlib.sha256(raw).hexdigest()
        return raw

    raw = read(RUN / "completion.json")
    assert hashlib.sha256(raw).hexdigest() == COMPLETION_SHA
    done = json.loads(raw)
    assert done["status"] == "COMPLETE" and done["error"] is None
    assert done["optimizer_calls"] == done["ray_refits"] == 0
    assert len(done["contexts"]) == 12 and len(done["extrema"]) == 6
    results = []
    for week in (1, 2, 3):
        family = json.loads(read(RUN / f"week_{week}_family.json"))
        solution = family["solution"]
        assert family["physical_family_size"] == solution["labeled_family_size"] == 6 ** 24
        assert family["gate"]["all_family_coefficients_invariant"] is True
        assert len(solution["groups"]) == 24
        assert all(len(g["assignments"]) == 6 for g in solution["groups"])
        low, high = rational(solution["minimum"]), rational(solution["maximum"])
        contexts = [r for r in done["contexts"] if r["week"] == week]
        assert len(contexts) == 4 and all(low <= rational(r["expanded_margin"]) <= high for r in contexts)
        for role, expected in (("minimum", low), ("maximum", high)):
            records = [r for r in done["extrema"] if r["week"] == week and r["which"] == role]
            assert len(records) == 1 and rational(records[0]["expanded_margin"]) == expected
        folder = RUN / f"week_{week}_maximum"
        rows = list(csv.DictReader(io.StringIO(gzip.decompress(read(folder / "row_metadata.csv.gz")).decode())))
        caps = [r for r in rows if r["family"] == "fossil_energy_cap"]
        assert len(caps) == 1
        caprow = int(caps[0]["row"])
        endpoint = [e for e in family["selected_endpoint_catalogue"] if e["kind"] == "row" and e["index"] == caprow]
        assert len(endpoint) == 1 and endpoint[0]["ownership"] == "fixed"
        coefficient = rational(endpoint[0]["coefficient"])
        cap = rational(endpoint[0]["identity_endpoint"])
        assert coefficient < 0 and cap in (23195, 26532, 48319)
        thresholds = {}
        for label, gap in (("all_orders", low), ("some_order", high)):
            threshold = cap - gap / coefficient
            assert gap + coefficient * (threshold - cap) == 0
            thresholds[label] = encode(threshold)
        results.append({"week": week, "recorded_cap_MWh": encode(cap),
                        "cap_row": caprow, "cap_multiplier": encode(coefficient),
                        "expanded_margin_minimum": encode(low),
                        "expanded_margin_maximum": encode(high),
                        "strict_budget_threshold_MWh": thresholds})
    read(Path(__file__).resolve())
    assert all(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == sha for path, sha in bindings.items())
    report = {
        "utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS_RECORD_CONSISTENCY_AND_AFFINE_DIAGNOSTIC",
        "prospective": False,
        "scope": "Post-hoc arithmetic on a closed fixed-ray experiment, not new optimization or independent proof replay.",
        "rule": "For nonnegative C strictly below all_orders threshold every family member is separated; below some_order threshold at least one is separated. Equality has zero margin. No feasibility converse.",
        "formula": "G(C) = G(C0) + d_cap * (C-C0); C_star = C0 - G(C0)/d_cap, d_cap < 0",
        "fixed": "A, ray, q, finite boxes, tau, data family and assignment extremizers; only the cap RHS varies algebraically.",
        "new_models": 0, "optimizer_calls": 0, "full_model_replays": 0,
        "results": results, "input_sha256": bindings,
        "elapsed_before_write_seconds": perf_counter() - started,
    }
    target = BASE / "POSTHOC_CAP_DIAGNOSTIC.json"
    with target.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"status": report["status"], "results": results, "seconds": report["elapsed_before_write_seconds"]}, indent=2))


if __name__ == "__main__":
    main()
