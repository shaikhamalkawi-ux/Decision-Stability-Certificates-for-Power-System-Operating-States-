"""One exact saved-output residual-order audit; no model or optimizer imports."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from datetime import datetime, timezone
import hashlib,json,math,time
ROOT=Path(__file__).resolve().parents[1]
ARM=ROOT/'results/research_next/residual_order'
PROTOCOL=ROOT/'docs/research_next/RESIDUAL_ORDER_PROTOCOL.md'
PINS={
  "results/research_next/whole_day_observation_preflight/run01/outcomes.json": "094a603e382a2f4d4b0fd6dd38f2a889ac664e46fea16389d3b226e0339f0bce",
  "results/research_next/whole_day_observation_preflight/INDEPENDENT_RESULT_REVIEW.json": "67ec0ae2a75e5c1b239143b5f63f3bca317f4d6f2ec2e0ac4e1b30143a3a441d",
  "results/research_next/whole_day_observation_preflight/prepared/week_1_days_321_mapping.json": "2a0db446f23fca3c86999bfa5b4d1eb1db852791b6684c89f502f12d38492dd1",
  "results/research_next/whole_day_observation_preflight/run01/call_01_week_1_days_123/observation.json": "c0b4d2317731707dc187fc5a6219b46fdfc1393d9f3c9c872683196ea729b8dd",
  "results/research_next/whole_day_observation_preflight/run01/call_01_week_1_days_123/clustering_details.json": "8cc403f9b0e637c10e55f7af769101b28507a5ad75d7c3d9b6567d4f76e3ff64",
  "results/research_next/whole_day_observation_preflight/run01/call_01_week_1_days_123/actual_features.json": "43f5c8541c6ff6ccf16e800e81a5521147ee86f2ac10ac9fe7fef15d05ee7b47",
  "results/research_next/whole_day_observation_preflight/run01/call_06_week_1_days_321/observation.json": "6ebd1f02f0485908c592fcf296b2b01943c36d90350a83bcaba5500ed15ea7ab",
  "results/research_next/whole_day_observation_preflight/run01/call_06_week_1_days_321/clustering_details.json": "e1c13650dd7d5dc6e8f370379acb0051c58671a22563f24bf5c9e8536822be9a",
  "results/research_next/whole_day_observation_preflight/run01/call_06_week_1_days_321/actual_features.json": "92558d3297ce783ee75ad7696f555f95158690c84c4cb441c871972a364af51a"
}
BASE='results/research_next/whole_day_observation_preflight/'
CALLS=('call_01_week_1_days_123','call_06_week_1_days_321')
def require(ok,message):
    if not ok: raise ValueError(message)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,x):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(x,f,indent=2,allow_nan=False);f.write('\n')
def rational(s):
    v=float.fromhex(s);require(math.isfinite(v),'Finite hex value');return Q.from_float(v)
def fraction(q):return {'numerator':str(q.numerator),'denominator':str(q.denominator),'approximate':float(q)}
def matrix(v,rows,cols):
    require(len(v)==rows and all(len(row)==cols for row in v),'Fixed shape')
    return tuple(tuple(rational(z) for z in row) for row in v)
def rp(k):return f'rp{k+1:02d}'
def run():
    clock=time.perf_counter();require(not ARM.exists(),'One fresh audit only')
    pins=dict(PINS);pins['src/researchnext_residual_order.py']=sha(__file__);pins[str(PROTOCOL.relative_to(ROOT)).replace('\\','/')]=sha(PROTOCOL)
    for p,d in pins.items():require(sha(ROOT/p)==d,'Initial hash '+p)
    ARM.mkdir(parents=True)
    save(ARM/'input_manifest.json',{'files':[{'path':p,'sha256':d} for p,d in pins.items()],'historical_git':'aecef6c5159db3153af9189b79e3dd5e2ca38f8f','utc':datetime.now(timezone.utc).isoformat()})
    out=read(ROOT/(BASE+'run01/outcomes.json'))
    comparisons=[x for x in out['comparisons'] if x['week']==1 and x['case']=='week_1_days_321']
    require(len(comparisons)==1,'One comparison');c=comparisons[0]
    require(c['primary_and_hindex_equal'] and c['joint_identity_repeat_stable'],'Prior closed collision')
    maps=c['primary_and_hindex_compatible_maps'];require(len(maps)==1,'Sole representative map');label_map=maps[0]
    require(set(label_map)==set(map(rp,range(3))) and set(label_map.values())==set(label_map),'Bijective representative map')
    mapping=read(ROOT/(BASE+'prepared/week_1_days_321_mapping.json'));perm=mapping['source_hour_indices']
    require(sorted(perm)==list(range(168)),'Hour bijection')
    dayperm=[perm[24*d]//24 for d in range(7)]
    require(sorted(dayperm)==list(range(7)) and all(perm[t]==24*dayperm[t//24]+t%24 for t in range(168)),'Whole-day permutation')
    observations=[];details=[];actual=[];daily=[];clusters=[];medoids=[];hindex=[]
    for call in CALLS:
        folder=ROOT/(BASE+'run01/'+call);observations.append(read(folder/'observation.json'));d=read(folder/'clustering_details.json');a=read(folder/'actual_features.json')
        details.append(d);actual.append(matrix(a['values_hex'],168,4));daily.append(matrix(d['normalized_daily_profiles_hex'],7,96));cl=d['cluster_order'];mi=d['medoid_source_day_indices'];hi=d['hindex_provenance']
        require(len(cl)==7 and set(cl)=={0,1,2} and len(mi)==3 and len(set(mi))==3 and all(type(i) is int and 0<=i<7 for i in mi),'Saved cluster/medoid schema')
        require(all(cl[mi[k]]==k for k in range(3)),'Medoid assigned to own cluster')
        require(len(hi)==168 and all(h['p']==f'h{t+1:04d}' and h['rp']==rp(cl[t//24]) and h['k']==f'k{t%24+1:04d}' for t,h in enumerate(hi)),'Hindex cluster semantics')
        require(a['hours']==168 and len(a['columns'])==4,'Four actually consumed features')
        clusters.append(cl);medoids.append(mi);hindex.append(hi)
    tests={}
    tests['canonical_primary_equal']=observations[0]['canonical']==observations[1]['canonical']
    tests['complete_hindex_equal_under_saved_map']=all(label_map[a['rp']]==b['rp'] and a['p']==b['p'] and a['k']==b['k'] for a,b in zip(*hindex))
    tests['identity_labels_invariant_under_day_permutation']=all(clusters[0][d]==clusters[0][dayperm[d]] for d in range(7))
    tests['actual_four_features_exactly_permuted']=all(actual[1][t]==actual[0][perm[t]] for t in range(168))
    tests['normalized_daily_vectors_exactly_permuted']=all(daily[1][d]==daily[0][dayperm[d]] for d in range(7))
    reconstructed=[tuple(daily[w][medoids[w][clusters[w][d]]] for d in range(7)) for w in range(2)]
    tests['medoid_reconstruction_equal_at_every_day']=reconstructed[0]==reconstructed[1]
    residuals=[tuple(tuple(x-y for x,y in zip(daily[w][d],reconstructed[w][d])) for d in range(7)) for w in range(2)]
    tests['residual_vectors_exactly_permuted']=all(residuals[1][d]==residuals[0][dayperm[d]] for d in range(7))
    tests['chronological_residual_sequences_differ']=residuals[0]!=residuals[1]
    bycluster=[]
    for k in range(3):
        target_label=label_map[rp(k)];target_k=int(target_label[2:])-1
        aa=Counter(residuals[0][d] for d in range(7) if clusters[0][d]==k);bb=Counter(residuals[1][d] for d in range(7) if clusters[1][d]==target_k)
        bycluster.append({'identity_cluster':rp(k),'target_cluster':target_label,'identity_days':sum(aa.values()),'target_days':sum(bb.values()),'joint_residual_multisets_equal':aa==bb})
    tests['all_cluster_residual_multisets_equal']=all(x['joint_residual_multisets_equal'] for x in bycluster)
    norms=[sum((x*x for row in r for x in row),Q(0)) for r in residuals]
    tests['exact_total_squared_residual_norm_equal']=norms[0]==norms[1]
    tests['nonzero_approximation_error_both']=all(v>0 for v in norms)
    save(ARM/'exact_residual_vectors.json',{'worlds':[{'world':name,'days':[[fraction(x) for x in row] for row in rr]} for name,rr in zip(('identity','days321'),residuals)]})
    for p,d in pins.items():require(sha(ROOT/p)==d,'Closing hash '+p)
    result={'status':'STRUCTURAL_PASS' if all(tests.values()) else 'STRUCTURAL_TESTS_NOT_ALL_TRUE','utc':datetime.now(timezone.utc).isoformat(),'tests':tests,'day_source_indices_0based':dayperm,'label_map':label_map,'clusters':bycluster,'total_squared_residual_norm':[fraction(x) for x in norms],'changed_daily_residual_positions':sum(a!=b for a,b in zip(*residuals)),'all_frozen_inputs_unchanged':True,'clustering_calls':0,'optimizer_calls':0,'model_builds':0,'exact_residual_vectors_sha256':sha(ARM/'exact_residual_vectors.json'),'elapsed_seconds':time.perf_counter()-clock,'scope':'4 actually consumed clustering features in 7x96 normalized daily vectors; no operating causality/negative/107-dimensional error claim'}
    save(ARM/'result.json',result);print(json.dumps(result),flush=True)
if __name__=='__main__':run()
