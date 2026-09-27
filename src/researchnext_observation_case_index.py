"""Materialize an index of closed observation comparisons; no scientific replay."""
from pathlib import Path
import csv, hashlib, json, sys
from collections import Counter
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/research_next/observation_case_index'
PINS={
 'results/research_next/auer_execution/outcomes.json':'40dbf5db70cfc96f9397e1212941e153ab53ec6672e408efb4d35ed0cf96f0b3',
 'results/research_next/auer_execution/completion.json':'4db94155b74e24d27036689be5fb387ca9e05264805e046e5f7572c9ef484e9c',
 'results/research_next/auer_projection_preflight/INDEPENDENT_EXECUTION_RESULT_REVIEW.json':'faa6b7e8a1a9804349a03c552190ca04cabf7483bbbd055421451db477204e44',
 'results/research_next/whole_day_observation_preflight/run01/outcomes.json':'094a603e382a2f4d4b0fd6dd38f2a889ac664e46fea16389d3b226e0339f0bce',
 'results/research_next/whole_day_observation_preflight/run01/completion.json':'716683064c992b12b600edf91dea3a42131b9d6241e7b1e5e5d742bb30dfcb8b',
 'results/research_next/whole_day_observation_preflight/INDEPENDENT_RESULT_REVIEW.json':'67ec0ae2a75e5c1b239143b5f63f3bca317f4d6f2ec2e0ac4e1b30143a3a441d',
}
def need(x,msg):
 if not x: raise ValueError(msg)
def digest(b):return hashlib.sha256(b).hexdigest()
def save(name,value):
 with (OUT/name).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,ensure_ascii=False);f.write('\n')
def main():
 need(not OUT.exists(),'Closed index already exists; use an additive new version')
 captured={}
 for p,h in PINS.items():
  b=(ROOT/p).read_bytes();need(digest(b)==h,'Source binding changed: '+p);captured[p]=(b,json.loads(b))
 families=[('HOD','results/research_next/auer_execution/outcomes.json',15,Counter(target=6,positive_control=3,identity_repeat=3)),('WHOLE_DAY','results/research_next/whole_day_observation_preflight/run01/outcomes.json',21,Counter(target=15,identity_repeat=3))]
 rows=[];calls=[];census=[]
 for family,path,count,roles in families:
  doc=captured[path][1];inv=doc['invocations'];comp=doc['comparisons']
  need(len(inv)==count and Counter(x['role'] for x in comp)==roles,'Full family denominator')
  need(len({(x['week'],x['case'],x['role']) for x in comp})==len(comp),'Duplicate comparison')
  need(all(x['status']=='OBSERVATION_COMPUTED' and x['calls_started']==1 for x in inv),'Archived call completion')
  for k,c in enumerate(comp):
   if family=='HOD':
    need(c['outcome'] in ('DISTINCT_COMPLETE_PROJECTED_OBSERVATION','EQUAL_COMPLETE_PROJECTED_OBSERVATION') and c['UC_feasibility_tested'] is False,'HOD schema')
    primary='EQUAL' if c['outcome'].startswith('EQUAL_') else 'DIFFERENT';secondary='NOT_EVALUATED_IN_THIS_STAGE'
   else:
    primary=c['primary_outcome'];secondary=c['primary_plus_hindex_outcome']
    need(primary in ('EQUAL','DIFFERENT') and secondary in ('EQUAL','DIFFERENT'),'Day schema')
    need(c['primary_equal']==(primary=='EQUAL') and c['primary_and_hindex_equal']==(secondary=='EQUAL'),'Saved boolean/result correspondence')
   rows.append(dict(family=family,week=c['week'],case=c['case'],role=c['role'],primary_observation=primary,primary_plus_full_hindex=secondary,uc_solved_in_observation_stage=False,source_path=path,source_sha256=PINS[path],source_record=k))
  for c in inv:calls.append(dict(family=family,**c,source_path=path,source_sha256=PINS[path]))
  targets=[x for x in rows if x['family']==family and x['role']=='target']
  census.append(dict(family=family,invocations=len(inv),comparisons=len(comp),roles=dict(roles),target_primary_equal=sum(x['primary_observation']=='EQUAL' for x in targets),target_primary_plus_hindex_equal=None if family=='HOD' else sum(x['primary_plus_full_hindex']=='EQUAL' for x in targets),optimizer_calls_replayed=0))
 need([(x['target_primary_equal'],x['target_primary_plus_hindex_equal']) for x in census]==[(0,None),(5,3)],'Published census mismatch')
 need(len(rows)==30 and len(calls)==36,'No omitted controls/repeats')
 OUT.mkdir()
 with (OUT/'comparisons.csv').open('x',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 save('invocation_index.json',calls)
 save('census.json',dict(families=census,source_comparisons=30,source_invocations=36,stage_uc_calls=0,new_optimizer_calls=0,new_observation_comparisons=0,scope='Index of previously independently checked records, not new comparison or cross-platform replication'))
 for p,(b,_) in captured.items():need((ROOT/p).read_bytes()==b,'Source changed during index compilation')
 artifacts=[dict(path=str(p.relative_to(ROOT)).replace('\\','/'),bytes=p.stat().st_size,sha256=digest(p.read_bytes())) for p in sorted(OUT.iterdir())]
 save('MANIFEST.json',dict(utc=datetime.now(timezone.utc).isoformat(),source_sha256=digest(Path(__file__).read_bytes()),inputs=[dict(path=p,sha256=PINS[p],bytes=len(b)) for p,(b,_) in captured.items()],artifacts=artifacts,meaning='Machine-readable navigation and denominator preservation only; historical outcomes unchanged'))
 with (OUT/'comparisons.csv').open(encoding='utf-8',newline='') as f:readback=list(csv.DictReader(f))
 need(len(readback)==30 and len(json.loads((OUT/'invocation_index.json').read_text()))==36,'Output readback')
 print(json.dumps(dict(status='INDEX_COMPLETE',comparisons=30,invocations=36,new_optimizer_calls=0,new_scientific_evaluations=0)))
if __name__=='__main__':main()
