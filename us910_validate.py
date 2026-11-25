#!/usr/bin/env python3
"""V9.10 release validator: numerical V9.9 baseline + positive-source-evidence gate.

It deliberately does NOT claim that passing model tests validates county supplies,
HTL field chemistry, agronomic performance or whole-system carbon closure.
"""
import argparse,csv,hashlib,io,json,subprocess,sys,zipfile
from pathlib import Path
from docx import Document
import us99_validate as prior
import us910_bt23_evidence_gate as bt
R=Path(__file__).resolve().parent
DOCS=['Research_Article_V9.10_Science.docx','Supplementary_Materials_V9.10_Science.docx',
      'Cover_Letter_Science_V9.10.docx','Title_Page_V9.10_Science.docx']


def inspect_data():
 audit=json.loads((R/'BT23_UPLOADED_ARCHIVE_AUDIT_V910.json').read_text())
 assert audit['csv_members']==0 and not audit['regional_data_present']
 assert audit['status']=='EMPTY_DIRECTORY_OR_ZIP'
 # Regression: a directory-only ZIP is an explicit error, not empty national data.
 with __import__('tempfile').TemporaryDirectory() as td:
  empty=Path(td)/'empty.zip'
  with zipfile.ZipFile(empty,'w') as z:z.writestr('BT23_EXPORTS/','')
  z=bt.inventory([empty]);assert z['csv_members']==0
  try:
   from us99_bt23_supply import ingest
   ingest([empty]);raise AssertionError('Empty ZIP unexpectedly passed importer')
  except ValueError as e:assert 'NO CSV DATA' in str(e)
 assert not any(p.name.startswith('BT23_STATE_') for p in R.glob('BT23_STATE_*.csv'))
 print('PASS: empty BT23 upload fails closed, no fabricated county observations')


def docs():
 for fn in DOCS:assert (R/fn).is_file(),fn
 article=Document(R/DOCS[0]);si=Document(R/DOCS[1]);letter=Document(R/DOCS[2])
 a='\n'.join(p.text for p in article.paragraphs);s='\n'.join(p.text for p in si.paragraphs)
 assert len(article.inline_shapes)==5 and len(si.inline_shapes)>=25
 assert article.paragraphs[0].text in s
 assert 'S26. ORNL BT23' in s and 'S9. Paired uncertainty: current 150 draws' in s
 assert '500-draw joint uncertainty' not in s
 assert 'no CSV records' in s and 'unverified assumptions' in a
 assert 'Grid Harvester' in a and 'Fig. S22' in s
 for tag,fn in prior.MANDATORY.items():prior.check_caption_image(si,f'Fig. {tag}.',fn)
 assert all('Sustainable Energy & Fuels' not in p.text for p in letter.paragraphs)
 print('PASS: V9.10 Science docs, 5 main figures, >=25 supplement figures, S1 and S22 bitmap-verified')


def main():
 p=argparse.ArgumentParser();p.add_argument('--full',action='store_true');p.add_argument('--draws',type=int,default=150)
 a=p.parse_args()
 if a.full:
  prior.full_rebuild(a.draws)
  subprocess.run([sys.executable,'us910_documents.py'],cwd=R,check=True)
 prior.file_checks();prior.model_checks();prior.importer_tests();inspect_data();docs()
 print('V9.10 TESTS PASSED: NUMERICAL CONSISTENCY; REGIONAL BT23 RESOURCE VALIDATION STILL MISSING')
if __name__=='__main__':main()
