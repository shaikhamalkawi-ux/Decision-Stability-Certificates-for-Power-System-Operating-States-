"""Fixed eight-week native chronology extension; see the recorded protocol."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import time
from pathlib import Path

import highspy
import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix

ROOT = Path(__file__).resolve().parents[1]
MONTHS = [1, 2, 3, 4, 5, 6, 7, 10]
TOL = 1e-5


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_model(v3):
    spec = importlib.util.spec_from_file_location('rts_native', v3 / 'code/dscgrid_model.py')
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    return model


def inputs(model, v3, month):
    cols = model.dec['GEN UID'].tolist()
    archived = v3 / 'processed' / f'month_{month:02d}_first_week_dispatch.csv'
    summary = v3 / 'processed' / f'month_{month:02d}_first_week_hourly_summary.csv'
    published = ROOT / 'reproducibility/data/processed/rts' / archived.name
    target = pd.read_csv(archived)[cols].to_numpy(float)
    public = pd.read_csv(published)
    assert np.max(np.abs(target - public[cols].to_numpy(float))) < 1e-9
    hourly = pd.read_csv(summary)
    assert len(hourly) == len(target) == 168
    assert public['timestamp'].tolist() == hourly['timestamp'].tolist()
    stamps = pd.to_datetime(hourly['timestamp'])
    assert stamps.iloc[0] == pd.Timestamp(2020, month, 1)
    assert np.all(np.diff(stamps.to_numpy()) == np.timedelta64(1, 'h'))
    pmin, pmax, net = [], [], []
    for row, stamp in zip(hourly['row'], stamps):
        native = model.load_ts.loc[int(row)]
        assert (int(native['Year']), int(native['Month']), int(native['Day']), int(native['Period'])) == (stamp.year, stamp.month, stamp.day, stamp.hour + 1)
        lo, hi = model.avail_at(int(row))
        pmin.append(lo)
        pmax.append(hi)
        net.append(float(native[str(model.AREA)]) - model.rtpv_at(int(row)).sum())
    return cols, target, np.array(pmin), np.array(pmax), np.array(net), [archived, summary, published]


def verify(model, p, u, pmin, pmax, net, mu, family, y=None, z=None):
    arrays = [p, u, pmin, pmax, net, mu] + ([y, z] if family == 'minud' else [])
    if any(a is None or not np.all(np.isfinite(a)) for a in arrays):
        return {'pass': False, 'tolerance': TOL, 'residuals': {'nonfinite_input': 1}}
    ti = np.flatnonzero(model.thermal.to_numpy(bool))
    hydro = model.dec.Category.eq('Hydro').to_numpy()
    ut = np.ceil(model.dec.iloc[ti]['Min Up Time Hr']).astype(int).to_numpy()
    dt = np.ceil(model.dec.iloc[ti]['Min Down Time Hr']).astype(int).to_numpy()
    ramp = model.dec.iloc[ti]['Ramp Rate MW/Min'].to_numpy(float) * 60
    residuals = {
        'negative_dispatch_MW': float(max(0., -p.min())),
        'availability_MW': float(max(0., (p - pmax).max())),
        'balance_MW': float(np.max(np.abs(p.sum(axis=1) - net))),
        'mean_MW': float(np.max(np.abs(p.mean(axis=0) - mu))),
        'hydro_fixed_MW': float(np.max(np.abs(p[:, hydro] - pmin[:, hydro]))),
        'binary': float(np.max(np.abs(u - np.round(u)))),
        'status_lower': float(max(0., -u.min())),
        'status_upper': float(max(0., (u - 1).max())),
        'commit_upper_MW': float(max(0., (p[:, ti] - pmax[:, ti] * u).max())),
        'commit_lower_MW': float(max(0., (pmin[:, ti] * u - p[:, ti]).max())),
    }
    ub = np.rint(u).astype(int)
    residuals['commit_upper_rounded_MW'] = float(max(0., (p[:, ti] - pmax[:, ti] * ub).max()))
    residuals['commit_lower_rounded_MW'] = float(max(0., (pmin[:, ti] * ub - p[:, ti]).max()))
    if family == 'ramp':
        online = (ub[1:] == 1) & (ub[:-1] == 1)
        residuals['online_ramp_MW'] = float(max(0., np.where(online, np.abs(np.diff(p[:, ti], axis=0)) - ramp, 0).max()))
    if family == 'minud':
        residuals['transition_lower'] = float(max(0., -y.min(), -z.min()))
        residuals['transition_upper'] = float(max(0., (y - 1).max(), (z - 1).max()))
        residuals['transition_binary'] = float(max(np.abs(y - np.round(y)).max(), np.abs(z - np.round(z)).max()))
        residuals['transition_identity'] = float(np.abs(np.diff(u, axis=0) - y[1:] + z[1:]).max())
        residuals['no_simultaneous_transition'] = float(max(0., (y + z - 1).max()))
        residuals['initial_transition'] = float(max(np.abs(y[0]).max(), np.abs(z[0]).max()))
        # Verify residence times from rounded status changes, independently of
        # the rolling-window constraints used to formulate the optimization.
        violations = 0
        for k in range(len(ti)):
            for t in range(1, len(p)):
                change = ub[t, k] - ub[t - 1, k]
                if change == 1:
                    violations += int(np.any(ub[t:min(len(p), t + ut[k]), k] != 1))
                elif change == -1:
                    violations += int(np.any(ub[t:min(len(p), t + dt[k]), k] != 0))
        residuals['residence_violations'] = violations
    return {'pass': all(v <= TOL for v in residuals.values()), 'tolerance': TOL, 'residuals': residuals}


def solve(model, month, family, target, pmin, pmax, net, output, seconds):
    h, ng = target.shape
    ti = np.flatnonzero(model.thermal.to_numpy(bool))
    k = len(ti)
    npv, nu = h * ng, h * k
    iy, iz = npv + nu, npv + 2 * nu
    n = npv + (3 if family == 'minud' else 1) * nu
    lower = np.zeros(n)
    upper = np.r_[pmax.ravel(), np.ones(n - npv)]
    for j in np.flatnonzero(model.dec.Category.eq('Hydro').to_numpy()):
        lower[np.arange(h) * ng + j] = pmin[:, j]
    if family == 'minud':
        upper[iy:iy+k] = upper[iz:iz+k] = 0
    pr = lambda t, j: t * ng + j
    ur = lambda t, q: npv + t * k + q
    yr = lambda t, q: iy + t * k + q
    zr = lambda t, q: iz + t * k + q
    ri, ci, vals, lo, hi = [], [], [], [], []
    def add(terms, l=-np.inf, u=np.inf):
        r = len(lo)
        for col, value in terms.items():
            ri.append(r); ci.append(col); vals.append(value)
        lo.append(l); hi.append(u)
    ut = np.ceil(model.dec.iloc[ti]['Min Up Time Hr']).astype(int).to_numpy()
    dt = np.ceil(model.dec.iloc[ti]['Min Down Time Hr']).astype(int).to_numpy()
    ramp = model.dec.iloc[ti]['Ramp Rate MW/Min'].to_numpy(float) * 60
    for t in range(h):
        add({pr(t, j): 1 for j in range(ng)}, net[t], net[t])
        for q, j in enumerate(ti):
            add({pr(t, j): 1, ur(t, q): -pmax[t, j]}, u=0)
            add({pr(t, j): -1, ur(t, q): pmin[t, j]}, u=0)
            if t == 0:
                continue
            if family == 'minud':
                add({ur(t, q): 1, ur(t-1, q): -1, yr(t, q): -1, zr(t, q): 1}, 0, 0)
                add({yr(t, q): 1, zr(t, q): 1}, u=1)
                up = {yr(a, q): 1 for a in range(max(1, t-int(ut[q])+1), t+1)}
                up[ur(t, q)] = -1
                add(up, u=0)
                down = {zr(a, q): 1 for a in range(max(1, t-int(dt[q])+1), t+1)}
                down[ur(t, q)] = 1
                add(down, u=1)
            else:
                # Relax each direction during startup/shutdown; only on/on
                # transitions carry the native rate restriction.
                big = float(max(pmax[t, j], pmax[t-1, j]))
                common = {ur(t, q): big, ur(t-1, q): big}
                add({pr(t, j): 1, pr(t-1, j): -1, **common}, u=ramp[q]+2*big)
                add({pr(t, j): -1, pr(t-1, j): 1, **common}, u=ramp[q]+2*big)
    mu = target.mean(axis=0)
    for j in range(ng):
        add({pr(t, j): 1/h for t in range(h)}, mu[j], mu[j])
    matrix = coo_matrix((vals, (ri, ci)), shape=(len(lo), n)).tocsr()
    lp = highspy.HighsLp()
    lp.num_col_, lp.num_row_ = n, len(lo)
    lp.col_cost_, lp.col_lower_, lp.col_upper_ = np.zeros(n), lower, upper
    lp.row_lower_, lp.row_upper_ = np.array(lo), np.array(hi)
    lp.integrality_ = [highspy.HighsVarType.kContinuous] * npv + [highspy.HighsVarType.kInteger] * (n-npv)
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.num_col_, lp.a_matrix_.num_row_ = n, len(lo)
    lp.a_matrix_.start_, lp.a_matrix_.index_, lp.a_matrix_.value_ = matrix.indptr, matrix.indices, matrix.data
    solver = highspy.Highs()
    stem = f'month_{month:02d}_{family}'
    for option, value in [('time_limit', float(seconds)), ('threads', 1), ('random_seed', 0), ('mip_rel_gap', 1e-8), ('log_to_console', False), ('log_file', str(output / (stem+'.log')))]:
        solver.setOptionValue(option, value)
    solver.passModel(lp)
    start = time.monotonic()
    solver.run()
    elapsed = time.monotonic() - start
    status = solver.getModelStatus()
    info = solver.getInfo()
    sol = solver.getSolution()
    max_inf = float(info.max_primal_infeasibility)
    record = {'month': month, 'family': family, 'model_status': solver.modelStatusToString(status), 'elapsed_s': elapsed, 'verdict': 'UNRESOLVED', 'solver_version': solver.version(), 'time_limit_s': seconds, 'rows': len(lo), 'columns': n, 'max_primal_infeasibility': max_inf if np.isfinite(max_inf) else None}
    if sol.value_valid:
        x = np.asarray(sol.col_value)
        p = x[:npv].reshape(h, ng)
        u = x[npv:npv+nu].reshape(h, k)
        y = x[iy:iy+nu].reshape(h, k) if family == 'minud' else None
        z = x[iz:iz+nu].reshape(h, k) if family == 'minud' else None
        check = verify(model, p, u, pmin, pmax, net, mu, family, y, z)
        record['witness_verification'] = check
        if check['pass']:
            record['verdict'] = 'ADMITTED_RELAXATION'
            pd.DataFrame(p, columns=model.dec['GEN UID']).to_csv(output/(stem+'_dispatch.csv'), index=False)
            pd.DataFrame(u, columns=model.dec.iloc[ti]['GEN UID']).to_csv(output/(stem+'_commitment.csv'), index=False)
            if y is not None:
                pd.DataFrame(y, columns=model.dec.iloc[ti]['GEN UID']).to_csv(output/(stem+'_startup.csv'), index=False)
                pd.DataFrame(z, columns=model.dec.iloc[ti]['GEN UID']).to_csv(output/(stem+'_shutdown.csv'), index=False)
    if status == highspy.HighsModelStatus.kInfeasible:
        assert record['verdict'] != 'ADMITTED_RELAXATION'
        record['verdict'] = 'REJECTED_RELAXATION'
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-v3', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=ROOT/'results/v8r1/rts_seasonal')
    parser.add_argument('--seconds', type=float, default=60)
    parser.add_argument('--verify-archived-ramp-only', action='store_true', help='Independently check the archived schedule without rerunning optimization.')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    model = load_model(args.source_v3)
    paths = [args.source_v3/'code/dscgrid_model.py', *sorted((args.source_v3/'raw').rglob('*.csv'))]
    records, baseline = [], []
    for month in MONTHS:
        cols, target, pmin, pmax, net, used = inputs(model, args.source_v3, month)
        paths.extend(used)
        u = (target[:, model.urows] > 1e-5).astype(float)
        check = verify(model, target, u, pmin, pmax, net, target.mean(axis=0), 'static')
        assert check['pass'], (month, check)
        baseline.append({'month': month, **check})
        if args.verify_archived_ramp_only:
            ramp_check = verify(model, target, u, pmin, pmax, net, target.mean(axis=0), 'ramp')
            records.append({'month': month, 'family': 'ramp', 'evidence': 'archived_static_schedule', 'verdict': 'ADMITTED_RELAXATION' if ramp_check['pass'] else 'NO_ARCHIVED_WITNESS', 'witness_verification': ramp_check})
            print(json.dumps({'month': month, 'archived_ramp_pass': ramp_check['pass']}), flush=True)
            continue
        for family in ['ramp', 'minud']:
            record = solve(model, month, family, target, pmin, pmax, net, args.output, args.seconds)
            records.append(record)
            (args.output/'results.json').write_text(json.dumps(records, indent=2, allow_nan=False), encoding='utf-8')
            print(json.dumps({k: record[k] for k in ['month','family','model_status','verdict','elapsed_s']}), flush=True)
    (args.output/'results.json').write_text(json.dumps(records, indent=2, allow_nan=False), encoding='utf-8')
    (args.output/'baseline_verification.json').write_text(json.dumps(baseline, indent=2), encoding='utf-8')
    pd.DataFrame([{k:v for k,v in r.items() if k != 'witness_verification'} for r in records]).to_csv(args.output/'summary.csv', index=False)
    pd.DataFrame([{'path': str(p), 'sha256': digest(p), 'bytes': p.stat().st_size} for p in dict.fromkeys(paths)]).to_csv(args.output/'input_manifest.csv', index=False)


if __name__ == '__main__':
    main()
