"""Source/result/binding inspection only; no residual arithmetic or clustering."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import time
ROOT=Path(__file__).resolve().parents[3]
ARM=ROOT/'results/research_next/residual_order'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bind(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
started=time.perf_counter()
manifest=read(ARM/'input_manifest.json');items=manifest['files'];assert len(items)==11
for d in items:assert sha(ROOT/d['path'])==d['sha256']
assert sha(ROOT/'src/researchnext_residual_order.py')=='1cfd5ecae0843bddba0c93607450f1e506738a20d0133b21fdf2c33b09f47a98'
assert sha(ROOT/'docs/research_next/RESIDUAL_ORDER_PROTOCOL.md')=='283d0719a399327db5063e0cfb1fba4a891fc2cceefb788427e4cf0e0cc0732e'
result=read(ARM/'result.json')
assert result['status']=='STRUCTURAL_PASS' and len(result['tests'])==11 and all(result['tests'].values())
assert sha(ARM/'exact_residual_vectors.json')==result['exact_residual_vectors_sha256']
assert result['optimizer_calls']==result['clustering_calls']==result['model_builds']==0
assert result['total_squared_residual_norm'][0]==result['total_squared_residual_norm'][1]
base=ROOT/'results/research_next/whole_day_observation_preflight/run01'
folders=[base/'call_01_week_1_days_123',base/'call_06_week_1_days_321']
features=[read(p/'actual_features.json') for p in folders]
details=[read(p/'clustering_details.json') for p in folders]
assert features[0]['columns']==features[1]['columns'] and len(features[0]['columns'])==4
for d in details:
    assert len(d['normalized_daily_profiles_hex'])==7 and all(len(row)==96 for row in d['normalized_daily_profiles_hex'])
    assert len(d['cluster_order'])==7 and len(d['medoid_source_day_indices'])==3
    assert all(d['cluster_order'][i]==k for k,i in enumerate(d['medoid_source_day_indices']))
paths=[ROOT/'src/researchnext_residual_order.py',ROOT/'docs/research_next/RESIDUAL_ORDER_PROTOCOL.md',
       ARM/'input_manifest.json',ARM/'result.json',ARM/'exact_residual_vectors.json',
       ROOT/'src/researchnext_auer_execution.py',
       ROOT/'.work/auer_projection_env/Lib/site-packages/tsam/timeseriesaggregation.py',
       ROOT/'.work/auer_projection_env/Lib/site-packages/tsam/periodAggregation.py']
record=dict(status='PASS_SOURCE_RESULT_BINDING_REVIEW',utc=datetime.now(timezone.utc).isoformat(),
    elapsed_seconds=time.perf_counter()-started,bound_inputs=11,all_inputs_hash_match=True,
    same_four_feature_columns=features[0]['columns'],saved_medoid_indices=[d['medoid_source_day_indices'] for d in details],
    changed_positions_reported=result['changed_daily_residual_positions'],
    squared_norm_reported=result['total_squared_residual_norm'][0],
    all11_saved_tests_true=True,residual_arithmetic_independently_recomputed=False,
    normalization_or_clustering_recomputed=False,optimizer_calls=0,
    scope='exact residuals to saved normalized unrescaled medoids in four clustering features; no107-dimensional or final rescaled-profile error claim',
    reviewed_files=[bind(p) for p in paths],review_source=bind(Path(__file__)))
with (ARM/'INDEPENDENT_SOURCE_RESULT_REVIEW.json').open('x',encoding='utf-8') as f:json.dump(record,f,indent=2);f.write('\n')
print(json.dumps(dict(status=record['status'],seconds=record['elapsed_seconds'],report_sha256=sha(ARM/'INDEPENDENT_SOURCE_RESULT_REVIEW.json'))))
