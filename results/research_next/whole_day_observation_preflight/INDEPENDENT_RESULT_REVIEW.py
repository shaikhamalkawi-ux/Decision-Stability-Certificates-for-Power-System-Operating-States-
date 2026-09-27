"""Read saved Auer outputs only: no producer import, clustering or solver."""
from collections import Counter
import ast
import struct
import zipfile
import hashlib
import itertools
import json
import math
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "results/research_next/whole_day_observation_preflight"
OUT = BASE / "run01"
PRE = BASE / "prepared"


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



def npz_rows(path):
    arrays = {}
    with zipfile.ZipFile(path) as z:
        assert set(z.namelist()) == {key+'.npy' for key in ('pmin','pmax','net','nodal','rows','source_hour')}
        for key in ('pmin','pmax','net','nodal','rows','source_hour'):
            b = z.read(key+'.npy')
            assert b[:6] == b'\x93NUMPY'
            version = tuple(b[6:8])
            assert version in ((1,0),(2,0))
            width = 2 if version == (1,0) else 4
            length = int.from_bytes(b[8:8+width], 'little')
            h = ast.literal_eval(b[8+width:8+width+length].decode('latin1'))
            assert not h['fortran_order']
            shape, dtype = h['shape'], h['descr']
            expected_width = {'pmin':41,'pmax':41,'net':1,'nodal':24,'rows':1,'source_hour':1}[key]
            assert shape == ((168,) if expected_width==1 else (168,expected_width))
            assert dtype == '<f8' if key in ('pmin','pmax','net','nodal') else dtype in ('<i8','<i4','<u8','<u4')
            data = b[8+width+length:]
            stride = int(dtype[-1]) * expected_width
            assert len(data) == 168*stride
            rows = [data[i*stride:(i+1)*stride] for i in range(168)]
            arrays[key] = {'dtype':dtype,'rows':rows}
    return arrays


def physical_tokens(arrays):
    return [struct.unpack('<107d',b''.join(arrays[k]['rows'][i] for k in ('pmin','pmax','net','nodal'))) for i in range(168)]


def relative_matches(original, target, oi, ti):
    # Relabel by pullback of every target label to an original label, and apply
    # the same relabeling to both matrix axes and the complete chronological list.
    labels = ('rp01','rp02','rp03')
    primaries, joint = [], []
    assert set(original['tables']) == set(target['tables'])
    assert set(original['matrices']) == set(target['matrices'])
    for destination_labels in itertools.permutations(labels):
        mapping = dict(zip(labels,destination_labels))
        inverse = [destination_labels.index(label) for label in labels]
        mapped_tables = {name:[{key:(mapping[value] if key=='rp' else value) for key,value in row.items()} for row in rows]
                         for name,rows in target['tables'].items()}
        equal_tables = all(keyed(original['tables'][name]) == keyed(mapped_tables[name]) for name in mapped_tables)
        equal_matrices = all(original['matrices'][name] == [[target['matrices'][name][i][j] for j in inverse] for i in inverse]
                             for name in target['matrices'])
        if equal_tables and equal_matrices:
            primaries.append(mapping)
            mapped_sequence = [{key:(mapping[value] if key=='rp' else value) for key,value in row.items()} for row in ti]
            if mapped_sequence == oi:
                joint.append(mapping)
    return {'primary_compatible_maps':primaries,'primary_and_hindex_compatible_maps':joint,
            'primary_equal':bool(primaries),'primary_and_hindex_equal':bool(joint)}


started = time.perf_counter()
assert sha(OUT/'outcomes.json') == '094a603e382a2f4d4b0fd6dd38f2a889ac664e46fea16389d3b226e0339f0bce'
assert sha(OUT/'completion.json') == '716683064c992b12b600edf91dea3a42131b9d6241e7b1e5e5d742bb30dfcb8b'
before = {str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
freeze = read(PRE/'prepared_freeze.json')
assert sha(PRE/'prepared_freeze.json') == '3b5da114904111edd8ad3e35d2bb5ad33a7c7cfeead23a5eca5ad1f2995bd422'
assert freeze['source_sha256'] == sha(ROOT/'src/researchnext_whole_day_observation.py') == '62a7f7c7b460b9dbe55c00e2a42f9cb6fbee7611b14bc397995aa1bb26fc1af6'
assert freeze['protocol_sha256'] == sha(ROOT/'docs/research_next/WHOLE_DAY_OBSERVATION_PROTOCOL.md') == 'a93991ee2b8fe7ed9a652ed5227c97e4f1deac6bd35d55aae01aea1a7aa8fcce'
assert sha(ROOT/'src/researchnext_auer_execution.py') == 'a18058186dde3dfe0dbd6717c27636e76ef59debbbcfbd36f7bb887c7a232d9c'
for field,file in (('manifest_sha256','input_manifest.json'),('cases_sha256','cases.json'),('schedule_sha256','schedule.json')):
    assert sha(PRE/file) == freeze[field]
bindings = read(PRE/'input_manifest.json')['files']
assert len(bindings) == 170 and len({r['path'].casefold() for r in bindings}) == 170
for r in bindings:
    p=Path(r['path']); assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
completion=read(OUT/'completion.json')
transport=completion['prepared_transport_bindings']
assert len(transport)==4 and {Path(r['path']).name for r in transport} == {'prepared_freeze.json','cases.json','schedule.json','input_manifest.json'}
for r in transport:
    p=Path(r['path']); assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
cases=read(PRE/'cases.json')['cases']
schedule=read(PRE/'schedule.json')['invocations']
outcomes=read(OUT/'outcomes.json')
assert len(cases)==18 and len(schedule)==len(outcomes['invocations'])==21
orders=list(itertools.permutations((1,2,3)))
assert [c['day_order'] for c in cases] == [list(o) for week in (1,2,3) for o in orders]
expected_schedule=[]
for week in (1,2,3):
    selected=[c for c in cases if c['week']==week]
    assert len(selected)==6
    for index,c in enumerate(selected+[selected[0]]):
        expected_schedule.append({**c,'invocation':len(expected_schedule)+1,
                                  'comparison_role':'identity_repeat' if index==6 else ('identity' if index==0 else 'target')})
assert schedule==expected_schedule
native_checks=[]
common_static=None
for week in (1,2,3):
    selected=[c for c in cases if c['week']==week]
    initial=npz_rows(Path(selected[0]['native_input_path']))
    initial_tokens=physical_tokens(initial)
    assert all(all(math.isfinite(v) for v in token) for token in initial_tokens)
    initial_days=[tuple(initial_tokens[i:i+24]) for i in range(0,168,24)]
    for case in selected:
        arrays=npz_rows(Path(case['native_input_path']))
        permutation=list(range(48))+[48+24*(d-1)+k for d in case['day_order'] for k in range(24)]+list(range(120,168))
        for key in initial:
            assert arrays[key]['dtype']==initial[key]['dtype']
            assert arrays[key]['rows']==[initial[key]['rows'][i] for i in permutation]
        tokens=physical_tokens(arrays)
        assert Counter(tuple(tokens[i:i+24]) for i in range(0,168,24))==Counter(initial_days)
        assert tokens[:48]==initial_tokens[:48] and tokens[120:]==initial_tokens[120:]
        assert all(i%24==p%24 for i,p in enumerate(permutation))
        projection=read(PRE/'projections'/case['projection_file'])
        static={k:projection[k] for k in ('vres','native_static_units','bus_ids','semantics','hours','scenario')}
        assert common_static is None or static==common_static
        common_static=static
        record=read(PRE/(case['case']+'_mapping.json'))
        assert record['source_hour_indices']==permutation and record['day_order']==case['day_order'] and record['week']==week
        changed=sum(a!=b for a,b in zip(initial_tokens,tokens))
        native_checks.append({'week':week,'case':case['case'],'role':case['role'],'physical_hour_positions_changed':changed,
                              'actual_107_coordinate_sequence_changed':bool(changed),'all_six_native_arrays_bitwise_mapped':True,
                              'joint_day_multiset_equal':True,'fixed48h_edges_equal':True})
canonical_strings,durations,checks,observations,hindices=[],[],[],[],[]
for expected, recorded in zip(schedule, outcomes["invocations"]):
    assert recorded["invocation"] == expected["invocation"] and recorded["case"] == expected["case"]
    assert recorded["role"] == expected["comparison_role"] and recorded["status"] == "OBSERVATION_COMPUTED"
    folder = OUT / f"call_{expected['invocation']:02d}_{expected['case']}"
    projection = read(PRE / "projections" / expected["projection_file"])
    assert sha(PRE / "projections" / expected["projection_file"]) == expected["projection_sha256"]
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
    observations.append(obs)
    hindices.append(hindex)
    canonical_strings.append(recovered)
    checks.append({"invocation":expected["invocation"],"case":expected["case"],"complete_selected_tables_exact":True,
                   "rounded_binary_assignment_valid":True,"cluster_order_matches_returned_assignment":True,
                   "medoid_is_in_its_cluster":True,"circular_counts_and_P_exact":True,"canonical_full_string_reproduced":True})

computed=[]
for week in range(3):
    start=week*7
    repeat=relative_matches(observations[start],observations[start+6],hindices[start],hindices[start+6])
    assert repeat['primary_and_hindex_equal']
    for offset in range(1,7):
        pos=start+offset
        matched=relative_matches(observations[start],observations[pos],hindices[start],hindices[pos])
        assert matched['primary_equal'] == (canonical_strings[start]==canonical_strings[pos])
        c=schedule[pos]
        computed.append({'week':week+1,'case':c['case'],'day_order':c['day_order'],'role':c['comparison_role'],
                         'joint_identity_repeat_stable':True,'primary_outcome':'EQUAL' if matched['primary_equal'] else 'DIFFERENT',
                         'primary_plus_hindex_outcome':'EQUAL' if matched['primary_and_hindex_equal'] else 'DIFFERENT',**matched})
assert computed==outcomes['comparisons'] and len(computed)==18
assert sum(c['role']=='target' for c in computed)==15
assert completion['status']=='COMPLETE' and completion['fixed_invocations']==completion['calls_started']==21
assert completion['fixed_targets']==15 and completion['solver_seconds']==math.fsum(durations)
assert completion['unknown_invocations']==completion['uc_calls']==completion['new_UC_models']==0
assert completion['soft_call_overruns']==[] and all(t<=30 for t in durations)
assert completion['phase_seconds']<completion['phase_limit_seconds']==1200 and completion['phase_overrun']==0
assert completion['prepared_transport_hashes_unchanged'] and completion['all_hashes_unchanged'] and completion['no_retries_or_fallback']
for r in bindings+transport:
    p=Path(r['path']); assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
after={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
assert after==before
primary_equal=[c['case'] for c in computed if c['role']=='target' and c['primary_equal']]
joint_equal=[c['case'] for c in computed if c['role']=='target' and c['primary_and_hindex_equal']]
report={'status':'PASS_SAVED_OUTPUT_AND_CLAIM_AUDIT','reviewer_source_sha256':sha(Path(__file__)),
        'input_bindings_unchanged':170,'prepared_transport_bindings_unchanged':4,'producer_files_unchanged':len(before),'producer_snapshot':before,
        'native_input_checks':native_checks,'invocation_checks':checks,'comparisons':computed,'primary_equal_target_cases':primary_equal,
        'primary_plus_hindex_equal_target_cases':joint_equal,'target_denominator':15,'comparison_denominator':18,'invocation_denominator':21,
        'all_three_joint_identity_repeats_equal':True,'unknowns':0,'producer_clustering_calls':21,'producer_uc_calls':0,
        'producer_solver_seconds':completion['solver_seconds'],'producer_phase_seconds':completion['phase_seconds'],
        'reviewer_optimizer_calls':0,'reviewer_clustering_calls':0,'producer_imports':0,
        'scope':'Saved full-profile/whole107 native transport, rounded assignments, transitions, canonical strings and all compatible same-label Hindex maps. No re-clustering, medoid optimum proof, full physical-model equivalence or operational recourse proof replay.',
        'elapsed_before_report_write_seconds':time.perf_counter()-started}
path=BASE/'INDEPENDENT_RESULT_REVIEW.json'
with path.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps({'status':report['status'],'producer_files_unchanged':len(before),'primary_equal_targets':primary_equal,
                  'joint_equal_targets':joint_equal,'native_changed_positions':[r['physical_hour_positions_changed'] for r in native_checks],
                  'report_sha256':sha(path),'seconds':report['elapsed_before_report_write_seconds']}))
