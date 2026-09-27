"""One invented license test and solver-free author-schema tests; no study inputs."""
import hashlib
import importlib.metadata as metadata
import importlib.util
import json
from pathlib import Path
import sys
import time
from types import SimpleNamespace

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def save(name, value):
    with (OUT / name).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


started = time.perf_counter()
source = ROOT / "src/researchnext_auer_projection.py"
assert hashlib.sha256(source.read_bytes()).hexdigest() == "9d1f036568935d62ac665e22cf0f4440e39ea3bf02b4b42488a2c1b47ce980b4"
spec = importlib.util.spec_from_file_location("projection_adapter", source)
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)
env = adapter.environment()
env["installed_distributions"] = sorted(
    [{"name": d.metadata["Name"], "version": d.version} for d in metadata.distributions()],
    key=lambda d: d["name"].lower())
env["probe_source_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
env["python_patch_difference"] = {"author": "3.12.11", "local": sys.version.split()[0]}
save("isolated_environment.json", env)
assert env["author_package_pins_match"], "Do not probe a mismatched environment"

# Gurobi is allowed only this invented one-variable LP. Suppress the banner and
# do not persist error text, license environment values, credentials or endpoints.
import gurobipy as gp
license_result = {"synthetic_only": True, "optimizer_calls_started": 0, "variables": 1,
                  "study_input_reads": 0, "license_values_recorded": False}
try:
    with gp.Env(empty=True) as e:
        e.setParam("OutputFlag", 0)
        e.start()
        with gp.Model(env=e) as m:
            m.Params.TimeLimit = 5
            m.Params.Threads = 1
            x = m.addVar(lb=0, ub=2)
            m.addConstr(x >= 1)
            m.setObjective(x)
            license_result["optimizer_calls_started"] = 1
            m.optimize()
            license_result.update(status=int(m.Status), solver_runtime=float(m.Runtime),
                                  usable_for_tiny_test=bool(m.Status == gp.GRB.OPTIMAL and x.X == 1))
except gp.GurobiError as error:
    license_result.update(usable_for_tiny_test=False, error_type=type(error).__name__, error_code=int(error.errno))
save("synthetic_license_probe.json", license_result)

# These are invented arrays and a hand-provided medoid assignment. No clustering
# is performed. They exercise author extraction, copying and circular transitions.
import numpy as np
utilities, case_type = adapter.load_author(adapter.AUTHOR)
meta = {"unit_names": ["T", "PV1", "PV2", "H"], "bus_ids": [1, 2]}
def g(uid, bus, category, maximum, minimum=0):
    return {"GEN UID": uid, "Bus ID": str(bus), "Category": category, "PMax MW": str(maximum),
            "PMin MW": str(minimum), "Min Up Time Hr": "48", "Min Down Time Hr": "48"}
gen = {r["GEN UID"]: r for r in [g("T",2,"NG CC",10,2),g("PV1",1,"Solar PV",3),
                                  g("PV2",1,"Solar PV",7),g("H",2,"Hydro",6)]}
native = {"pmin": [[2,0,0,4] for _ in range(168)], "pmax": [[10,1,2,4] for _ in range(168)],
          "nodal": [[-1,5] for _ in range(168)], "net": [4 for _ in range(168)]}
projected = adapter.project_arrays(meta, gen, native)
cs = adapter.as_author_case(projected)
features = utilities._extract_scenario_data(cs, "s1", "maxInvestment")
aggregated = utilities._prepare_aggregated_data(features, False)
assert len(features) == 504 and len(aggregated) == 168
assert np.array_equal(aggregated["demand"].to_numpy(), np.full(168,3.0))
assert np.array_equal(aggregated["Solar PV"].to_numpy(), np.full(168,3.0))
assert np.array_equal(aggregated["Hydro"].to_numpy(), np.full(168,4.0))
fake = SimpleNamespace(clusterCenterIndices=[0,2,5], _clusterPeriodNoOccur={0:3,1:2,2:2},
                       _clusterOrder=np.array([0,1,0,1,2,0,2]))
reduced = utilities.apply_representative_periods(cs, {"s1":fake}, rp_length=24, inplace=False)
n,p_to,p_from = case_type.get_rpTransitionMatrices(reduced, clip_method="none", clip_value=0)
assert np.array_equal(n.to_numpy(),np.array([[0,2,1],[1,0,1],[2,0,0]]))
assert len(reduced.dPower_Demand) == 144 and len(reduced.dPower_VRESProfiles) == 144
assert len(reduced.dPower_Inflows) == 72 and len(reduced.dPower_Hindex) == 168
assert not hasattr(reduced, "rpTransitionMatrixAbsolute")  # Helper did not populate cache.
save("author_schema_fixtures.json", {"status":"PASS", "invented_inputs_only":True,
      "clustering_calls":0, "author_extraction_rows":504, "author_aggregated_hours":168,
      "multiple_generators_repeat_demand":True, "selected_full_tables_preserved":True,
      "circular_counts_match":True, "transition_cache_requires_refresh":True,
      "adapter_sha256":hashlib.sha256(source.read_bytes()).hexdigest()})
save("probe_completion.json", {"status":"PASS", "elapsed_seconds":time.perf_counter()-started,
     "scientific_input_reads":0, "scientific_clustering_calls":0,
     "synthetic_optimizer_calls":license_result["optimizer_calls_started"],
     "author_sources_unchanged":adapter.author_closure(adapter.AUTHOR)})
print(json.dumps({"status":"PASS", "synthetic_license_usable":license_result.get("usable_for_tiny_test"),
                  "scientific_clustering_calls":0}))
