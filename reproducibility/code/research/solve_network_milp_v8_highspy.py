from __future__ import annotations

import json
import time
from pathlib import Path

import highspy
import numpy as np
import pandas as pd
from scipy.sparse import load_npz


WORKSPACE = Path(__file__).resolve().parents[1]
BASELINE = (
    WORKSPACE
    / ".work"
    / "V7"
    / "DSC_Grid_V7_GBReplicationAndNetworkRepairStrengthening"
)
OUT = WORKSPACE / ".work" / "C_network_milp"
problem = np.load(OUT / "problem_data.npz")
matrix = load_npz(OUT / "constraint_matrix.npz").tocsr()

c = problem["c"]
lb = problem["lb"]
ub = problem["ub"]
row_lower = problem["row_lower"]
row_upper = problem["row_upper"]
integrality = problem["integrality"]
witness_x = problem["witness_x"]
nrow, ncol = matrix.shape

lp = highspy.HighsLp()
lp.num_col_ = ncol
lp.num_row_ = nrow
lp.col_cost_ = c
lp.col_lower_ = lb
lp.col_upper_ = ub
lp.row_lower_ = row_lower
lp.row_upper_ = row_upper
lp.integrality_ = [
    highspy.HighsVarType.kInteger if value else highspy.HighsVarType.kContinuous
    for value in integrality
]
lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
lp.a_matrix_.num_col_ = ncol
lp.a_matrix_.num_row_ = nrow
lp.a_matrix_.start_ = matrix.indptr.astype(np.int32)
lp.a_matrix_.index_ = matrix.indices.astype(np.int32)
lp.a_matrix_.value_ = matrix.data.astype(float)

solver = highspy.Highs()
solver.setOptionValue("time_limit", 600.0)
solver.setOptionValue("mip_rel_gap", 1e-9)
solver.setOptionValue("presolve", "on")
solver.setOptionValue("random_seed", 0)
solver.setOptionValue("log_file", str((OUT / "highs_warm_start_log.txt").resolve()))
solver.setOptionValue("output_flag", True)
pass_status = solver.passModel(lp)
start_status = solver.setSolution(
    ncol,
    np.arange(ncol, dtype=np.int32),
    witness_x.astype(float),
)
print(
    json.dumps(
        {
            "pass_model_status": str(pass_status),
            "set_solution_status": str(start_status),
            "mip_start_objective_MW": float(c @ witness_x),
        },
        indent=2,
    ),
    flush=True,
)

started = time.time()
run_status = solver.run()
elapsed = time.time() - started
model_status = solver.getModelStatus()
info = solver.getInfo()
solution = solver.getSolution()

record = {
    "run_status": str(run_status),
    "model_status": str(model_status),
    "model_status_text": solver.modelStatusToString(model_status),
    "elapsed_s": elapsed,
    "objective_MW": float(info.objective_function_value),
    "mip_dual_bound_MW": float(info.mip_dual_bound),
    "mip_gap": float(info.mip_gap),
    "mip_node_count": int(info.mip_node_count),
    "primal_solution_status": int(info.primal_solution_status),
    "dual_solution_status": int(info.dual_solution_status),
    "max_primal_infeasibility": float(info.max_primal_infeasibility),
    "sum_primal_infeasibilities": float(info.sum_primal_infeasibilities),
    "known_independent_lower_bound_MW": 8.020508464286115,
    "known_start_upper_bound_MW": float(c @ witness_x),
}

x = np.asarray(solution.col_value, dtype=float)
if x.size == ncol:
    H = 168
    NG = 41
    NB = 24
    K = 24
    npv = H * NG
    nth = H * NB
    iu = npv + nth
    nu = H * K
    baseline_v3 = BASELINE / "upstream_lock" / "V3"
    generator_names = pd.read_csv(
        baseline_v3 / "processed" / "month_07_first_week_dispatch.csv", nrows=1
    ).columns.tolist()[1:]
    # The canonical order comes from the model's decision-generator table.
    import sys

    sys.path.insert(0, str(baseline_v3 / "code"))
    import dscgrid_model as model  # noqa: E402

    generator_names = model.dec["GEN UID"].tolist()
    thermal_names = model.dec.iloc[model.urows]["GEN UID"].tolist()
    dispatch = x[:npv].reshape(H, NG)
    commitment = x[iu : iu + nu].reshape(H, K)
    target = pd.read_csv(
        baseline_v3 / "processed" / "month_07_first_week_dispatch.csv"
    )[generator_names].mean(axis=0).to_numpy(float)
    repaired = dispatch.mean(axis=0)
    abs_delta = np.abs(repaired - target)
    record["recomputed_objective_MW"] = float(abs_delta.sum())
    pd.DataFrame(dispatch, columns=generator_names).to_csv(
        OUT / "network_milp_warm_dispatch.csv", index=False
    )
    pd.DataFrame(commitment, columns=thermal_names).round().astype(int).to_csv(
        OUT / "network_milp_warm_commitment.csv", index=False
    )
    pd.DataFrame(
        {
            "generator": generator_names,
            "target_mean_MW": target,
            "repaired_mean_MW": repaired,
            "delta_MW": repaired - target,
            "abs_delta_MW": abs_delta,
        }
    ).to_csv(OUT / "network_milp_warm_mean.csv", index=False)

(OUT / "network_milp_highspy_result.json").write_text(
    json.dumps(record, indent=2), encoding="utf-8"
)
solver.writeSolution(str((OUT / "network_milp_highspy_solution.sol").resolve()), 0)
print(json.dumps(record, indent=2), flush=True)
