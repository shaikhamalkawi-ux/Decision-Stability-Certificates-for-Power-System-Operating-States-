from pathlib import Path
import json, hashlib, re, zipfile
from xml.etree import ElementTree as E
R=Path(__file__).resolve().parents[2]
D=R/'docs/research8h/manuscript_v1'
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
records=[]
for basename,source,expected_eq,expected_ref,expected_pages in [('Temporal_Feasibility_Research_Note_DRAFT','note_en.json',6,10,9),('Scientific_Decision_AR_DRAFT','decision_ar.json',0,9,5)]:
 data=json.loads((D/source).read_text(encoding='utf-8'))
 assert len(data['references'])==expected_ref
 with zipfile.ZipFile(D/(basename+'.docx')) as z:
  root=E.fromstring(z.read('word/document.xml'))
  assert len(root.findall('.//m:oMath',NS))==expected_eq
  assert len(root.findall('.//w:tbl',NS))==2
  assert len([n for n in z.namelist() if n.startswith('word/media/')])==1
  rels=E.fromstring(z.read('word/_rels/document.xml.rels'))
  urls=[r.attrib['Target'] for r in rels if r.attrib.get('TargetMode')=='External']
  assert all(u.startswith('https://') for u in urls)
  assert all(u in urls for _,u in data['references'])
  text=''.join(root.itertext())
  assert '[1]' in text and '['+str(expected_ref)+']' in text
 md=(D/(basename+'.md')).read_text(encoding='utf-8')
 images=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',md)
 assert len(images)==1 and all((D/x).is_file() for x in images)
 records.append({'document':basename,'references':expected_ref,'native_math_objects':expected_eq,'tables':2,'embedded_images':1,'all_reference_links_present':True,'markdown_image_link_exists':True,'visually_reviewed_pages':expected_pages})
report={'status':'PASS','documents':records,'visual_review':'English final nine rendered pages byte-identical to inspected v4 pages; Arabic all five final pages directly visually inspected. No clipping, broken equations, reversed interval endpoints or missing table/figure content observed.','scientific_review':'DRAFT_MANUSCRIPT_SCIENTIFIC_REVIEW.md and DRAFT_MANUSCRIPT_DELTA_REVIEW.md; final Arabic wording names the third delivery archive.','scope':'Research working drafts through closed evidence commit520fe5974a4d92892906c42ce51a9d12ef304d3a; excludes active fresh-energy follow-up. Not a journal-submission readiness certification.'}
(D/'DOCUMENT_QA.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))
