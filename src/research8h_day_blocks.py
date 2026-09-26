"""Frozen five-order January day-block sensitivity test."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from itertools import permutations
import json
from pathlib import Path
import shutil
import time

import highspy
import numpy as np
import pandas as pd
from scipy.sparse import load_npz

import research8h_seasonal_transfer as transfer
from research8h_seasonal_uncapped import exact_point_check, check_manifest, rational_record
from research8h_service_network_mip import build, direct_check, unpack
from research8h_u_only_continuation import audit_projection
from temporal_lp_certificate import check_vector, digest, save
from v8r1_rts_seasonal import load_model

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'results/research8h/seasonal_transfer'
OUTPUT = ROOT/'results/research8h/day_blocks'
PROTOCOL = ROOT/'docs/research8h/DAY_BLOCK_PROTOCOL.md'
ORDERS = [p for p in permutations(range(3)) if p != (0, 1, 2)]
TOL = 1e-5


def load_case(directory):
    matrix = load_npz(directory/'matrix.npz').tocsr()
    with np.load(directory/'bounds.npz') as a:
        bounds = {k:a[k].copy() for k in a.files}
    with np.load(directory/'integrality.npz') as a:
        integer = a['integrality'].copy()
    labels = pd.read_csv(directory/'row_metadata.csv.gz')
    meta = json.loads((directory/'model_metadata.json').read_text())
    with np.load(directory/'native_inputs.npz') as a:
        native = {k:a[k].copy() for k in a.files}
    return matrix, bounds, integer, labels, meta, native


def prepare(source_v3):
    OUTPUT.mkdir(parents=True, exist_ok=False)
    save(OUTPUT/'source_hash_check.json', check_manifest(SOURCE/'input_manifest.csv'))
    model = load_model(source_v3)
    identity = SOURCE/'january_identity'
    matrix, bounds, integer, labels, meta, native = load_case(identity)
    assert meta['budget_MWh'] == 23195 and meta['individual_mean_constraints'] == 0
    assert meta['unit_names'] == model.dec['GEN UID'].tolist()
    assert meta['thermal_unit_names'] == model.dec.iloc[model.urows]['GEN UID'].tolist()
    fossil = [meta['unit_names'].index(uid) for uid in meta['fossil_units']]
    assert len(fossil) == 23
    native_fossil = [int(j) for j in model.urows if model.dec.iloc[j]['Fuel'] in {'Coal','Oil','NG'}]
    assert fossil == native_fossil
    assert [meta['unit_names'][j] for j in model.urows if j not in fossil] == ['121_NUCLEAR_1']
    with np.load(identity/'constructive_vector.npz') as a:
        reference = a['vector'].copy()
    rp, ru, ry, rz, rt = unpack(reference, 168, 41, 24, 24)
    paths = [Path(__file__), PROTOCOL, SOURCE/'input_manifest.csv',
        source_v3/'code/dscgrid_model.py', *sorted((source_v3/'raw').rglob('*.csv'))]
    for filename in ['research8h_seasonal_transfer.py', 'research8h_seasonal_uncapped.py',
        'research8h_seasonal_reference.py', 'research8h_service_network_mip.py',
        'research8h_service_network.py', 'research8h_u_only_continuation.py',
        'temporal_lp_certificate.py', 'temporal_information_pilot.py', 'v8r1_rts_seasonal.py']:
        paths.append(ROOT/'src'/filename)
    controls = {}
    for case in ['january_identity', 'seed_26100100']:
        d = SOURCE/case
        a,b,integ,_,_,_ = load_case(d)
        with np.load(d/'constructive_vector.npz') as v:
            point = v['vector']
        controls[case] = exact_point_check(a,b,point,integ)
        assert controls[case]['expanded_pass']
        paths.extend(d/name for name in ['matrix.npz','bounds.npz','integrality.npz',
            'row_metadata.csv.gz','model_metadata.json','native_inputs.npz','constructive_vector.npz'])
    save(OUTPUT/'exact_positive_controls.json', controls)
    prepared = []
    for day_order in ORDERS:
        name = 'days_' + ''.join(str(j+1) for j in day_order)
        order = np.arange(168)
        order[48:120] = np.concatenate([np.arange(48+24*j,72+24*j) for j in day_order])
        inverse = np.argsort(order)
        assert np.array_equal(order[inverse], np.arange(168))
        assert np.array_equal(order[:48], np.arange(48)) and np.array_equal(order[120:], np.arange(120,168))
        assert np.array_equal(order % 24, np.arange(168) % 24)
        for block in range(7):
            assert np.all(np.diff(order[24*block:24*(block+1)]) == 1)
        for x in [native['pmin'],native['pmax'],native['net'],native['nodal'],native['rows'],rp,ru,rt]:
            assert np.array_equal(x[order][inverse],x)
        n = {k:native[k][order] for k in ['pmin','pmax','net','rows']}
        n['source_hour'] = order
        data = build(model,n['pmin'],n['pmax'],n['net'],n['rows'],23195)
        assert np.array_equal(data[-1],native['nodal'][order])
        directory = OUTPUT/name
        transfer.archive_model(directory,data,n)
        cc, vector = transfer.check_candidate(model,data,n,rp[order],ru[order],rt[order],fossil,23195)
        transfer.save_witness(directory,vector,model)
        assert cc['static_network_cap_pass']
        assert transfer.energy(rp[order],fossil) == transfer.energy(rp,fossil)
        rowlabels = pd.DataFrame(data[4])
        static = ~rowlabels.family.isin(['minimum_up','minimum_down']).to_numpy()
        assert (~static).sum() > 0
        sb = {k:(v[static] if k.startswith('row_') else v) for k,v in data[1].items()}
        static_exact = exact_point_check(data[0][static].tocsr(),sb,vector,data[2])
        full_exact = exact_point_check(data[0],data[1],vector,data[2])
        assert static_exact['expanded_pass']
        if full_exact['expanded_pass']:
            assert cc['binary_network_pass'], 'exact/native constructive acceptance discrepancy'
        constructive_pass = full_exact['expanded_pass'] and cc['binary_network_pass']
        projected, audit = audit_projection(data[0],data[1],data[3],rowlabels,data[2])
        np.savez_compressed(directory/'projected_integrality.npz',integrality=projected)
        save(directory/'projection_audit.json',audit)
        save(directory/'constructive_check.json',{'numerical':cc,'static_exact':static_exact,'full_exact':full_exact})
        lp_directory = directory/'lp'; lp_directory.mkdir()
        for filename in ['matrix.npz','bounds.npz','integrality.npz','row_metadata.csv.gz']:
            shutil.copyfile(directory/filename,lp_directory/filename)
        changed = np.flatnonzero(np.diff(order) != 1)
        preservation = {'bijection':True,'fixed_edges':True,'hour_of_day_exact':True,
            'within_day_order_exact':True,'package_roundtrips_exact':True,'nodal_reconstruction_exact':True,
            'fossil_energy_exactly_preserved':True,'changed_hours':int(np.count_nonzero(order != np.arange(168))),
            'changed_adjacent_pairs_after_hours':changed.tolist(),'changed_adjacent_pair_count':len(changed),
            'day_order_1based':[j+1 for j in day_order]}
        save(directory/'preservation.json',preservation)
        pd.DataFrame({'new_hour_0based':np.arange(168),'source_hour_0based':order,
            'source_native_row':n['rows']}).to_csv(directory/'permutation.csv',index=False)
        prepared.append({'case':name,'constructive_expanded_pass':constructive_pass,**preservation})
    save(OUTPUT/'prepared_cases.json',prepared)
    paths.extend(sorted(p for p in OUTPUT.rglob('*') if p.is_file()))
    pd.DataFrame([{'path':str(p),'sha256':digest(p),'bytes':p.stat().st_size}
        for p in dict.fromkeys(paths)]).to_csv(OUTPUT/'input_manifest.csv',index=False)
    freeze={'utc':datetime.now(timezone.utc).isoformat(),'source_sha256':digest(Path(__file__)),
        'protocol_sha256':digest(PROTOCOL),'manifest_sha256':digest(OUTPUT/'input_manifest.csv'),
        'source_v3':str(source_v3.resolve()),'cases':[r['case'] for r in prepared],
        'LP_seconds':30,'MIP_seconds':300,'phase_seconds':2100,'minimum_MIP_remaining_seconds':305,
        'optimizations_started':0,'cap_MWh':23195,'individual_means':0}
    save(OUTPUT/'prepared_freeze.json',freeze)
    print(json.dumps({'event':'PREPARED_NO_SOLVES',**freeze}),flush=True)


def solve_mip(model,directory,case):
    matrix,bounds,original_integer,labels,meta,native = load_case(directory)
    with np.load(directory/'projected_integrality.npz') as a:
        integer = a['integrality']
    sub = directory/'mip'; sub.mkdir()
    lp = highspy.HighsLp(); lp.num_row_,lp.num_col_ = matrix.shape
    lp.col_cost_ = np.zeros(matrix.shape[1])
    lp.col_lower_,lp.col_upper_ = bounds['column_lower'],bounds['column_upper']
    lp.row_lower_,lp.row_upper_ = bounds['row_lower'],bounds['row_upper']
    lp.integrality_ = [highspy.HighsVarType.kInteger if v else highspy.HighsVarType.kContinuous for v in integer]
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.num_row_,lp.a_matrix_.num_col_ = matrix.shape
    lp.a_matrix_.start_,lp.a_matrix_.index_,lp.a_matrix_.value_ = matrix.indptr,matrix.indices,matrix.data
    solver = highspy.Highs()
    for k,v in {'time_limit':300.,'threads':1,'random_seed':0,'presolve':'on','mip_rel_gap':1e-8,
        'log_to_console':False,'log_file':str(sub/'solver.log')}.items():
        assert solver.setOptionValue(k,v) == highspy.HighsStatus.kOk
    assert solver.passModel(lp) == highspy.HighsStatus.kOk
    started = time.perf_counter(); solver.run(); elapsed = time.perf_counter()-started
    status,solution = solver.getModelStatus(),solver.getSolution()
    result = {'case':case,'verdict':'UNKNOWN','model_status':solver.modelStatusToString(status),
        'elapsed_s':elapsed,'time_limit_s':300,'optimization_calls':1,'solver_version':solver.version()}
    if solution.value_valid:
        raw = np.asarray(solution.col_value)
        np.savez_compressed(sub/'raw_vector.npz',vector=raw)
        result['raw_matrix_check'] = check_vector(matrix,bounds,raw)
        p,u,y,z,theta = unpack(raw,168,41,24,24)
        eligible = bool(np.isfinite(raw).all() and np.all(np.abs(u-np.rint(u))<=TOL)
            and np.all((np.rint(u)>=0)&(np.rint(u)<=1)))
        result['eligible_for_recovery'] = eligible
        if eligible:
            u = np.rint(u); y,z = transfer.transitions(u)
            point = np.concatenate([a.ravel() for a in (p,u,y,z,theta)])
            np.savez_compressed(sub/'recovered_vector.npz',vector=point)
            result['recovered_matrix_check'] = check_vector(matrix,bounds,point)
            fossil = [meta['unit_names'].index(uid) for uid in meta['fossil_units']]
            physical = direct_check(model,p,u,y,z,theta,native['pmin'],native['pmax'],native['net'],
                native['rows'],native['nodal'],fossil,23195)
            exact = exact_point_check(matrix,bounds,point,original_integer)
            save(sub/'physical_check.json',physical); save(sub/'exact_point_check.json',exact)
            result['physical_pass'] = physical['pass']
            result['exact_expanded_pass'] = exact['expanded_pass']
            result['exact_strict_pass'] = exact['strict_pass']
            result['fossil_MWh'] = rational_record(transfer.energy(p,fossil))
            if all([result['raw_matrix_check']['pass'],result['recovered_matrix_check']['pass'],physical['pass']]):
                result['verdict'] = 'VERIFIED_FEASIBLE_EXPANDED_MODEL' if exact['expanded_pass'] else 'NUMERICAL_TOLERANCE_ONLY_CANDIDATE'
    if status == highspy.HighsModelStatus.kInfeasible and result['verdict']=='UNKNOWN':
        result['verdict'] = 'NUMERICAL_MIP_INFEASIBLE_NOT_EXACT_CERTIFICATE'
    save(sub/'result.json',result)
    return result


def run_prepared(source_v3):
    freeze = json.loads((OUTPUT/'prepared_freeze.json').read_text())
    assert freeze['source_v3'] == str(source_v3.resolve())
    assert digest(OUTPUT/'input_manifest.csv') == freeze['manifest_sha256']
    audit = check_manifest(OUTPUT/'input_manifest.csv')
    with (OUTPUT/'execution_started.json').open('x',encoding='utf-8') as f:
        json.dump({'utc':datetime.now(timezone.utc).isoformat(),'pre_execution_hash_check':audit},f,indent=2)
    model = load_model(source_v3); phase_started = time.perf_counter()
    prepared = json.loads((OUTPUT/'prepared_cases.json').read_text())
    transfer.OUTPUT = OUTPUT
    outcomes = {}; lp_results = {}
    for item in prepared:
        case = item['case']; directory = OUTPUT/case
        if item['constructive_expanded_pass']:
            outcomes[case] = {'case':case,'verdict':'VERIFIED_FEASIBLE_EXPANDED_MODEL',
                'route':'CONSTRUCTIVE_REFERENCE','LP_calls':0,'MIP_calls':0}
            continue
        matrix,bounds,integer,labels,meta,native = load_case(directory)
        sub = directory/'lp'
        # Exact matrix/bounds/labels copies were frozen before any solve.
        rec = transfer.solve_lp(matrix,bounds,integer,labels.to_dict('records'),sub)
        if (sub/'dual_certificate.json').exists():
            cert = json.loads((sub/'dual_certificate.json').read_text())
            support = cert['support']
            support['distinct_uid_labels_including_bus_and_branch_tags'] = support.pop('individual_units_in_nonzero_rows')
            active = labels.iloc[[m['row'] for m in cert['multipliers']]]
            temporal = active[active.family.isin(['transition','exclusive_transition','minimum_up','minimum_down'])]
            support['temporal_generator_uids'] = sorted(set(temporal.uid.astype(str)))
            support['temporal_generator_count'] = len(support['temporal_generator_uids'])
            support['interpretation'] = ('Full-network fossil-cap model with no individual mean rows. '
                'Global energy cap involves all 168 hours. UID labels can denote generators, buses or branches. '
                'Support is not minimum memory or minimum raw information.')
            save(sub/'dual_certificate.json',cert)
        rec.update(matrix_sha256=digest(directory/'matrix.npz'),bounds_sha256=digest(directory/'bounds.npz'),case=case)
        save(sub/'result.json',rec); lp_results[case] = rec
        if rec['verdict']=='REJECTED_EXACT_BINARY64_CERTIFICATE':
            outcomes[case] = {'case':case,'verdict':'CERTIFIED_INFEASIBLE_EXPANDED_MODEL',
                'route':'EXACT_ROBUST_LP_RAY','LP_calls':1,'MIP_calls':0}
        print(json.dumps({'stage':'LP','case':case,'verdict':rec['verdict'],'elapsed_s':rec['elapsed_s']}),flush=True)
    for item in prepared:
        case = item['case']
        if case in outcomes:
            continue
        if 2100-(time.perf_counter()-phase_started)<305:
            outcomes[case] = {'case':case,'verdict':'UNKNOWN','route':'PHASE_BUDGET','LP_calls':1,'MIP_calls':0}
        else:
            result = solve_mip(model,OUTPUT/case,case)
            outcomes[case] = {'case':case,'verdict':result['verdict'],'route':'MIP','LP_calls':1,'MIP_calls':1,
                'MIP_elapsed_s':result['elapsed_s']}
            print(json.dumps({'stage':'MIP',**outcomes[case]}),flush=True)
        save(OUTPUT/'outcomes_partial.json',list(outcomes.values()))
    ordered = [outcomes[item['case']] for item in prepared]
    save(OUTPUT/'outcomes.json',ordered)
    pd.DataFrame(ordered).to_csv(OUTPUT/'outcomes.csv',index=False)
    save(OUTPUT/'final_manifest_check.json',check_manifest(OUTPUT/'input_manifest.csv'))
    save(OUTPUT/'completion.json',{'cases':5,'LP_calls':len(lp_results),
        'MIP_calls':sum(r['MIP_calls'] for r in ordered),'phase_elapsed_s':time.perf_counter()-phase_started,
        'actual_LP_seconds':sum(r['elapsed_s'] for r in lp_results.values()),
        'actual_MIP_seconds':sum(r.get('MIP_elapsed_s',0) for r in ordered),
        'nominal_model_positive_claim':False,'all_outcomes_retained':True})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-v3',type=Path,required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--prepare-only',action='store_true')
    group.add_argument('--run-prepared',action='store_true')
    args = parser.parse_args()
    if args.prepare_only:
        prepare(args.source_v3)
    else:
        run_prepared(args.source_v3)


if __name__ == '__main__':
    main()
