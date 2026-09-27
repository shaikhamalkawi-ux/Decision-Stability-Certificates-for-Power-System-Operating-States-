"""Structural and copy-integrity checks for the separately rendered v3 drafts."""
from pathlib import Path
import csv
import hashlib
import json
import re
import zipfile
from xml.etree import ElementTree as E
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
DIRECTORY = ROOT / 'docs/research8h/manuscript_v3'
WORK = ROOT / '.work/research8h_manuscripts/v3'
EN_PAGES = 13  # All final pages directly inspected by root.
AR_PAGES = 7
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math'}
SCIENCE = 'd491d49fd2d21a798df2911a9b0987532e5dbf7d'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
records = []
for name, source, equations, references, pages, render in [
    ('Temporal_Feasibility_Research_Note_v3_DRAFT', 'note_en.json', 8, 11, EN_PAGES, 'render_en01'),
    ('Scientific_Decision_AR_v3_DRAFT', 'decision_ar.json', 0, 10, AR_PAGES, 'render_ar01')]:
    data = json.loads((DIRECTORY / source).read_text(encoding='utf-8'))
    assert len(data['references']) == references
    assert [b['id'] for b in data['blocks'] if b['t'] == 'eq'] == [str(n) for n in range(1, equations + 1)]
    assert sum(b['t'] == 'table' for b in data['blocks']) == 6
    assert sum(b['t'] == 'figure' for b in data['blocks']) == 1
    prose = '\n'.join(b.get('text', '') for b in data['blocks'])
    assert SCIENCE in prose
    # Citation ranges and Arabic or English list separators share one order audit.
    cited = []
    for match in re.findall(r'\[([\d\s,،–-]+)\]', prose):
        for part in re.split(r'[,،]', match):
            pair = re.split('[–-]', part.strip())
            nums = range(int(pair[0]), int(pair[-1]) + 1) if len(pair) == 2 else [int(pair[0])]
            for n in nums:
                if n not in cited:
                    cited.append(n)
    assert cited == list(range(1, references + 1)), cited
    with zipfile.ZipFile(DIRECTORY / (name + '.docx')) as zipped:
        xml = E.fromstring(zipped.read('word/document.xml'))
        assert len(xml.findall('.//m:oMath', NS)) == equations
        assert len(xml.findall('.//w:tbl', NS)) == 6
        assert len([n for n in zipped.namelist() if n.startswith('word/media/')]) == 1
        doc_text = ''.join(n.text or '' for n in xml.findall('.//w:t', NS)).replace('\u2066','').replace('\u2069','')
        for table_block in (b for b in data['blocks'] if b['t']=='table'):
            for row in table_block['rows']:
                for cell in row:
                    assert str(cell) in doc_text, (name, cell)
        assert all(b['caption'] in doc_text for b in data['blocks'] if b['t'] in ('table','figure'))
        rels = E.fromstring(zipped.read('word/_rels/document.xml.rels'))
        urls = [r.attrib['Target'] for r in rels if r.attrib.get('TargetMode') == 'External']
        assert all(u.startswith('https://') for u in urls)
        assert all(u in urls for _, u in data['references'])
    markdown = (DIRECTORY / (name + '.md')).read_text(encoding='utf-8')
    images = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', markdown)
    assert len(images) == 1 and (DIRECTORY / images[0]).is_file()
    for suffix in ('.docx', '.md'):
        assert (DIRECTORY / (name + suffix)).read_bytes() == (WORK / (name + suffix)).read_bytes()
    assert (DIRECTORY / source).read_bytes() == (WORK / source).read_bytes()
    assert (DIRECTORY / (name + '.pdf')).read_bytes() == (WORK / render / (name + '.pdf')).read_bytes()
    assert len(PdfReader(str(DIRECTORY / (name + '.pdf'))).pages) == pages
    pngs = [WORK / render / f'page-{n}.png' for n in range(1, pages + 1)]
    assert all(p.is_file() for p in pngs)
    records.append(dict(document=name, source_sha256=sha(DIRECTORY / source), pages=pages,
                        native_math_objects=equations, tables=6, embedded_images=1,
                        references=references, reference_first_appearance_pass=True,
                        all_reference_links_present=True, markdown_figure_resolves=True,
                        archive_equals_visually_reviewed_working_bytes=True,
                        rendered_page_sha256={p.name: sha(p) for p in pngs}))
report = dict(status='PASS', science_commit=SCIENCE, documents=records,
              visual_review='Root directly inspected every final English and Arabic page. The unchanged standalone eight-case graphic was also inspected earlier in this session. No clipped text, broken equations, reversed numerical intervals or missing table/figure content observed.',
              scientific_review=['MANUSCRIPT_V3_SCIENTIFIC_REVIEW.md', 'MANUSCRIPT_V3_CLAIM_REVIEW.md', 'MANUSCRIPT_V3_REFERENCE_AUDIT.md'],
              scope='Separate author-review research drafts; not journal-readiness approval. Separate original expanded-angle and strict-flow results and seasonal follow-up included; portable scope stated explicitly.',
              checker_source_sha256=sha(Path(__file__)))
(DIRECTORY / 'DOCUMENT_QA.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
files = sorted(p for p in DIRECTORY.iterdir() if p.is_file() and p.name != 'FILE_MANIFEST.csv')
with (DIRECTORY / 'FILE_MANIFEST.csv').open('x', encoding='utf-8', newline='') as stream:
    writer = csv.DictWriter(stream, fieldnames=['path', 'bytes', 'sha256'])
    writer.writeheader()
    writer.writerows({'path': p.name, 'bytes': p.stat().st_size, 'sha256': sha(p)} for p in files)
print(json.dumps({'status': 'PASS', 'documents': 2, 'pages': EN_PAGES+AR_PAGES, 'manifest_payloads': len(files)}))
