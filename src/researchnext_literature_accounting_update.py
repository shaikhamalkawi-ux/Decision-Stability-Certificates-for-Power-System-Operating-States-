"""Reconcile existing reading records; no new paper access or scientific computation."""
from pathlib import Path
import csv,json,hashlib,collections
R=Path(__file__).resolve().parents[1]
O=R/'results/research_next/literature_accounting_update'
inputs=['results/research_next/literature_accounting/literature_reading_ledger.csv','results/research_next/reading_regret_2023.json','results/research_next/reading_regret_uc_bounds.json','results/research_next/reading_single_uc_dp.json','results/research_next/reading_exact_lp_oracles.json']
data={p:(R/p).read_bytes() for p in inputs}
assert hashlib.sha256(data[inputs[0]]).hexdigest()=='37a981759fbb9774689a295ffad1274e9ef56f8866d55e5561821ad63ea63990'
rows=list(csv.DictReader(data[inputs[0]].decode('utf-8-sig').splitlines()))
assert len(rows)==45
fields=list(rows[0])
new=[]
for path in inputs[1:]:
 d=json.loads(data[path]); items=d['items'] if 'items' in d else [d]
 for item in items:
  depth='indexed_body_excerpt' if item.get('depth')=='indexed_body_excerpt' else 'selected_body'
  coverage='; '.join(item.get('sections',[])) or item.get('reading_depth',item.get('depth',''))
  new.append(dict(id='A'+str(len(new)+1).zfill(2),title=item['title'],work_type='paper_or_preprint',doi=item['doi'],other_identifier=item.get('version',''),depth_class=depth,body_or_excerpts_read='yes',evidence_files=path,sections_or_coverage=coverage,version_and_dedup_notes='Existing supplementary record; no new reading; not whole paper. '+item.get('doi_type',''),stage='post_cycle04_existing_addendum',count_scope='continuation_substantive_paper'))
assert len(new)==5
combined=rows+new
do=[r['doi'].casefold().strip() for r in combined if r['doi'].strip()]
assert len(do)==len(set(do)), 'Duplicate DOI; manual resolution required'
titles=[' '.join(r['title'].casefold().split()) for r in combined]
assert len(titles)==len(set(titles)), 'Duplicate title; manual resolution required'
sub=[r for r in combined if r['count_scope'] in ('historical_substantive_paper','continuation_substantive_paper')]
body=lambda rr:sum(r['body_or_excerpts_read']=='yes' for r in rr)
assert len(sub)==45 and body(sub)==39 and len(sub)-body(sub)==6
assert len(combined)==50 and body(combined)==41
assert collections.Counter(r['count_scope'] for r in combined)['nonpaper_separate']==3
assert collections.Counter(r['count_scope'] for r in combined)['background_metadata_or_code_only']==2
O.mkdir(exist_ok=False)
with (O/'literature_reading_ledger.csv').open('x',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(combined)
report=dict(scope='Reconciliation of existing records only; no new paper reading',all_distinct_work_records=50,substantive_paper_or_preprint_records=45,substantive_selected_or_indexed_body=39,substantive_limited=6,separate_nonpaper_records=3,separate_background_metadata_or_code_only_papers=2,all_work_body_or_excerpt_records=41,new_readings=0,by_type=dict(collections.Counter(r['work_type'] for r in combined)),input_bindings=[dict(path=p,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()) for p,b in data.items()],source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),ledger_sha256=hashlib.sha256((O/'literature_reading_ledger.csv').read_bytes()).hexdigest(),limitation='Depth is inherited from recorded selected sections, not an independent recreation of reading sessions; full-paper completion is not claimed.')
(O/'reconciliation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['all_distinct_work_records','substantive_paper_or_preprint_records','substantive_selected_or_indexed_body','substantive_limited','new_readings']}))
