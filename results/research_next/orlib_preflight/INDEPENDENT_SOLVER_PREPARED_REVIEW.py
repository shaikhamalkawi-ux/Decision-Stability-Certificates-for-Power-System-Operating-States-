"""Independent immutable transport/plan gate; no producer imports or rebuilding."""
import gzip
import hashlib
import json
import math
import time
from fractions import Fraction
from pathlib import Path, PurePosixPath

BASE = Path(__file__).resolve().parent
ROOT = BASE / "solver_prepared01"
RUN_SHA = "30bcdeda411263c4782d34328bbfe3ec6f77814a1c0a80d5d526844a52a79306"
ADAPTER_SHA = "e2b137f6a7ba23d1a9b12663ee1deee7bf2a3fffdd1f95d4718fb9ba37d17dc1"
SOLVER_SHA = "2659f11efe5d817fe70f007e514b99dbc992408db3482e825719175bee458e5a"
PROTOCOL_SHA = "c7b4e5033095b6119838c8bea6d79362fadcecd736cecdb6abb1daf9585d05ff"
INPUT_SHA = "8cf0b37220f521cd1365c4a0ad05199bafb0a634eeb28cc0642c1e31b4c3b205"

def sha(b):
    return hashlib.sha256(b).hexdigest()

def require(ok, message):
    if not ok:
        raise ValueError(message)

def main():
    start = time.perf_counter()
    manifest_bytes = (ROOT / "run_manifest.json").read_bytes()
    require(sha(manifest_bytes) == RUN_SHA, "Trusted solver manifest")
    manifest = json.loads(manifest_bytes)
    require(manifest["schema"] == "orlib-run-manifest-v1" and len(manifest["files"]) == 29, "Run manifest schema/count")
    snapshots, folded = {"run_manifest.json": manifest_bytes}, set()
    for item in manifest["files"]:
        name = item["path"]
        rel = PurePosixPath(name)
        require(not rel.is_absolute() and ":" not in name and "\\" not in name and all(p not in (".", "..") for p in rel.parts), "Unsafe path")
        require(name.casefold() not in folded, "Path alias")
        folded.add(name.casefold())
        path = ROOT.joinpath(*rel.parts)
        require(not path.is_symlink() and path.resolve().is_relative_to(ROOT.resolve()), "Escaping path")
        b = path.read_bytes()
        require(len(b) == item["bytes"] and sha(b) == item["sha256"], "Payload bytes: " + name)
        snapshots[name] = b
    require({p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file()} == set(snapshots), "Complete 30-file pre-execution inventory")
    require(not (ROOT / "execution_started.json").exists() and not (ROOT / "outputs").exists(), "Execution not yet started")
    require(sha(snapshots["inputs/manifest.json"]) == INPUT_SHA, "Original manifest transport")
    original = json.loads(snapshots["inputs/manifest.json"])
    expected_inputs = {r["path"] for r in original["files"]} | {"manifest.json"}
    require({p.removeprefix("inputs/") for p in snapshots if p.startswith("inputs/")} == expected_inputs, "Exact original archive file set")
    for rel in expected_inputs:
        require(snapshots["inputs/" + rel] == (BASE / "prepared01" / rel).read_bytes(), "Original prepared payload transport: " + rel)
    for name, expected in (("inputs/researchnext_orlib_uc.py", ADAPTER_SHA),
                           ("researchnext_orlib_solve.py", SOLVER_SHA), ("ORLIB_SOLVER_PROTOCOL.md", PROTOCOL_SHA)):
        require(sha(snapshots[name]) == expected, "Reviewed source binding")
    reviewed = {"INDEPENDENT_PREPARED_REVIEW.json": "29bbf8a5e661bc9027262a004fc6c2a66c3df1ef687eaab29dfdfbba9586a3e8",
                "INDEPENDENT_PREPARED_REVIEW.md": "4ec1f4070ef946317de7ace2eae80eb643f6087893f7afbc832d8bcd237171dc",
                "SOLVER_SOURCE_REVIEW.md": "dea3c2ea5f9c95cf0b870f1c0a8daa4e40c10f81c2b36e8ca287bb00515102c6"}
    for rel, expected in reviewed.items():
        require(sha((BASE / rel).read_bytes()) == expected, "Closed review binding")
    require(json.loads((BASE / "INDEPENDENT_PREPARED_REVIEW.json").read_bytes())["status"] == "PASS_PREPARED_ARCHIVE", "Prior archive review")
    plan = json.loads(snapshots["plan.json"])
    names = [f"{name}__{variant}" for name in ("identity", "reverse_4_19", "rotate_left1_4_19")
             for variant in ("native_penalized", "hard_service")]
    require(plan["schema"] == "orlib-solver-plan-v1" and plan["status"] == "PREPARED_NOT_RUN", "Prospective plan")
    require(plan["models"] == names and plan["sequence"] == [{"model": n, "kind": k} for n in names for k in ("mip", "lp")], "Fixed 12-call sequence")
    require(plan["options"] == {"mip": {"time_limit": 300.0, "threads": 1, "random_seed": 0, "presolve": "on", "mip_rel_gap": 1e-8},
                                "lp": {"time_limit": 30.0, "threads": 1, "random_seed": 0, "solver": "simplex", "presolve": "off"}}, "Fixed options")
    require(plan["phase_seconds"] == 2700 and plan["guard_padding_seconds"] == 5 and plan["solver_calls"] == 0, "Budget/no-call state")
    require(plan["source_adapter_sha256"] == ADAPTER_SHA and plan["solver_source_sha256"] == SOLVER_SHA
            and plan["solver_protocol_sha256"] == PROTOCOL_SHA and plan["adapter_manifest_sha256"] == INPUT_SHA, "Plan source hashes")
    require(plan["adapter_protocol_sha256"] == "4fb15c1525405561a7c9ce19f5d4bb01dde55ff014b70bd55173d067f929f04a", "Adapter protocol")
    tau = Fraction.from_float(1e-5)
    require(plan["tau_binary64"] == 1e-5 and plan["tau_exact"]["numerator"] == str(tau.numerator)
            and plan["tau_exact"]["denominator"] == str(tau.denominator), "Exact expanded tolerance")
    require(plan["binary_columns_per_model"] == 960 and plan["native_export_identity"] == "NOT_TESTED", "Mask/scope in plan")
    raw = json.loads(gzip.decompress(snapshots["inputs/selected_case.json.gz"]))
    case = json.loads(snapshots["inputs/normalized_case.json"])
    units = {g["name"]: g for g in case["units"]}
    history_fields = {"up": "Minimum uptime (h)", "down": "Minimum downtime (h)", "age": "Initial status (h)",
                      "initial_power": "Initial power (MW)", "ru": "Ramp up limit (MW)", "rd": "Ramp down limit (MW)"}
    for name, g in units.items():
        for field, native in history_fields.items():
            require(g[field] == raw["Generators"][name][native], "Raw initial/dwell/ramp transport")
    mask = {f"{f}:g{g}:{t}" for f in ("U", "Y", "Z", "D") for g in range(10) for t in range(24)}
    model_records = []
    for name in names:
        model = json.loads(snapshots["inputs/" + name + ".json"])
        require(len(model["columns"]) == 2472 and len(model["rows"]) == 4384, "Full model dimensions")
        require({c["name"] for c in model["columns"] if c["binary"]} == mask and model["binary_count"] == 960, "Full binary mask")
        for c in model["columns"]:
            require(math.isfinite(c["lower"]) and math.isfinite(c["upper"]) and c["lower"] <= c["upper"], "Finite boxes")
            parts = c["name"].split(":")
            family, unit, hour = parts[:3]
            expected_cost = 0.0
            if family == "U":
                expected_cost = units[unit]["min_cost"]
            elif family == "D":
                expected_cost = units[unit]["startup_cost"]
            elif family == "S":
                expected_cost = units[unit]["slopes"][int(parts[3])]
            elif family == "C":
                expected_cost = case["penalty"][model["order"][int(hour)]]
            require(c["objective"] == expected_cost, "Native encoded objective coordinate")
        model_records.append({"model": name, "rows": 4384, "columns": 2472, "original_binary_coordinates": 960,
                              "objective_matches_bound_normalized_cost_fields": True})
    for rel, data in snapshots.items():
        require((ROOT / rel).read_bytes() == data, "Frozen archive changed during gate")
    return {"status": "PASS_PREPARED_ORLIB", "run_manifest_sha256": RUN_SHA, "adapter_sha256": ADAPTER_SHA,
            "solver_sha256": SOLVER_SHA, "solver_protocol_sha256": PROTOCOL_SHA, "adapter_manifest_sha256": INPUT_SHA,
            "bound_payloads": 29, "total_files_including_manifest": 30, "byte_identical_prior_payloads_including_manifest": 26,
            "models": model_records, "planned_MIP_calls": 6, "planned_LP_calls": 6, "execution_marker_absent": True,
            "closed_reviews": reviewed, "frozen_bytes_unchanged": True,
            "review_scope": "All frozen bytes and exact prior-archive transport; full model sizes, masks, finite boxes and every encoded cost; fixed order/options/tau; raw initial/dwell/ramp fields. Variant/package/row semantics inherited from unchanged independently audited archive; bound arithmetic/witness semantics from final source review.",
            "not_claimed": ["Runtime Julia/JuMP export equality", "Solver outcome", "Binary witness", "Independent model reconstruction"],
            "producer_imports": 0, "model_rebuilds": 0, "optimizer_calls": 0, "witness_checks": 0,
            "runtime_record_as_prepared": plan["runtime"], "review_seconds": time.perf_counter() - start,
            "review_source_sha256": sha(Path(__file__).read_bytes())}

if __name__ == "__main__":
    output = BASE / "INDEPENDENT_SOLVER_PREPARED_REVIEW.json"
    require(not output.exists(), "Preserve prior gate output")
    try:
        result = main()
    except Exception as exc:
        with output.open("x", encoding="utf-8") as stream:
            json.dump({"status": "REVIEW_FAILURE", "error": repr(exc)}, stream, indent=2)
        raise
    with output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))
