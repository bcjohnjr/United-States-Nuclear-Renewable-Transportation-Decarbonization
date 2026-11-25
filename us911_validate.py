#!/usr/bin/env python3
"""V9.11 full reproducibility and editorial consistency tests.

Passing checks DOES NOT validate missing BT23 county input, technology yields,
soil carbon sequestration, complete LCA or journal author approval.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,subprocess,sys
from pathlib import Path
from PIL import Image
from docx import Document
import us99_validate as heritage
import us910_bt23_evidence_gate as gate
ROOT=Path(__file__).resolve().parent
DOC={'main':'Research_Article_V9.11_Science.docx','supp':'Supplementary_Materials_V9.11_Science.docx',
'letter':'Cover_Letter_Science_V9.11.docx','title':'Title_Page_V9.11_Science.docx'}
NEW_FIGS={
 'S46':'ScienceFigS46_V911_Delivered_Cost_Resource_Robustness.tif',
 'S47':'ScienceFigS47_V911_Cover_Crop_Land_Economic_Robustness.tif',
 'S48':'ScienceFigS48_V911_Field_Counterfactual_LCA_Bounds.tif'}

def source_gate():
 path=ROOT/'BT23_UPLOADED_ARCHIVE_AUDIT_V910.json'
 d=json.loads(path.read_text())
 assert d['csv_members']==0 and not d['regional_data_present']
 # No fabricated county input or success claims in downstream output.
 a=json.loads((ROOT/'US911_Robustness_Results.json').read_text())
 assert a['bt23_county_evidence'] is False
 assert not (ROOT/'BT23_VALIDATED').exists()
 assert (ROOT/'us910_bt23_evidence_gate.py').is_file()
 print('PASS: BT23 still unavailable; no assumptions relabelled as county evidence')

def numerics():
 d=json.loads((ROOT/'US911_Robustness_Results.json').read_text())
 crop=float(d['central_crop_annual_bn']);no=float(d['no_crop_annual_bn'])
 assert math.isclose(no-crop,d['crop_saving_bn'],abs_tol=1e-7)
 assert abs(crop-654.7633815744)<1e-5
 assert abs(no-661.5452670834)<1e-5
 assert len(d['grid'])==25 and len(d['land'])==6 and len(d['field_lca'])==5
 indexed={(int(z['analyst_cap_mt']*100),int(z['delivery_surcharge_usd_dry_metric_t'])):z for z in d['grid']}
 for cap in (0,41.5,83,124.5,166):
  last=float('inf')
  for surcharge in (0,20,40,80,120):
   q=indexed[(int(cap*100),surcharge)];val=q['crop_saving_bn']
   assert val>=-1e-5 and val<=last+1e-7
   last=val
  if cap==0:assert all(abs(indexed[(0,x)]['selected_crop_mt'])<1e-10 for x in (0,20,40,80,120))
 assert abs(indexed[(16600,40)]['crop_saving_bn']-0.685)<.01
 assert indexed[(16600,120)]['selected_crop_mt']<1e-7
 byarea={float(x['assumed_cover_crop_land_mha']):x for x in d['land']}
 assert byarea[5]['selected_crop_mt']<byarea[20]['selected_crop_mt']
 assert byarea[20]['cover_crop_service_mt']<=10.0+1e-6
 field=d['field_lca'];zero=field[2]
 assert abs(zero['incremental_crop_emissions_mt']-(d['process_inventory_substituted_central_mt']-d['unmatched_no_crop_emissions_mt']))<1e-6
 assert abs(field[0]['incremental_crop_emissions_mt']-field[-1]['incremental_crop_emissions_mt']-16.6)<1e-7
 for row in d['grid']:
  for nutrient in ('n','p','k'):assert row[f'{nutrient}_external_kt']>=0
 heritage.file_checks();heritage.model_checks()
 print('PASS: 25 fully reoptimised cost/resource screens; 6 cover-land screens; 5 field-LCA screens')

def embedded_image(doc,label,fn):
 p=doc.paragraphs
 hits=[i for i,x in enumerate(p) if x.text.startswith('Fig. '+label+'.')]
 assert len(hits)==1,(label,len(hits))
 assert hits[0]>0
 prior=p[hits[0]-1]
 blips=prior._p.xpath('.//*[local-name()="blip"]')
 assert len(blips)==1,(label,'missing figure directly before caption')
 rid=blips[0].get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
 with Image.open(io.BytesIO(doc.part.related_parts[rid].blob)) as im:
  got=im.convert('RGB')
 with Image.open(ROOT/fn) as im:
  want=im.convert('RGB');want.thumbnail((1850,1350))
 assert got.size==want.size,(label,got.size,want.size)
 import numpy as np
 mse=float(np.mean((np.asarray(got,dtype=np.float32)-np.asarray(want,dtype=np.float32))**2))
 assert mse<6,(label,mse)
 print('PASS: actual embedded TIFF-backed Fig.',label,'MSE',round(mse,3))

def figures_and_docs():
 for p in ROOT.glob('*.tif'):
  with Image.open(p) as im:
   im.verify()
  with Image.open(p) as im:
   assert im.mode=='RGB' and all(abs(q-600)<1 for q in im.info.get('dpi',(0,0))),(p.name,im.mode,im.info.get('dpi'))
 article=Document(ROOT/DOC['main']);si=Document(ROOT/DOC['supp'])
 assert len(article.inline_shapes)==5
 assert len(si.inline_shapes)>=28
 for fn in DOC.values():assert (ROOT/fn).is_file()
 m='\n'.join(p.text for p in article.paragraphs);s='\n'.join(p.text for p in si.paragraphs)
 n=next(i for i,p in enumerate(article.paragraphs) if p.text.strip()=='Abstract')
 assert 100<=len(article.paragraphs[n+1].text.split())<=125
 for v in ('S46','S47','S48'):assert 'Fig. '+v+'.' in s
 for v in ('S13','S14','S15'):assert 'Table '+v+'.' in s
 for v in ('Grid Harvester','Fig. S1','Fig. S22'):assert v in m and v in s
 for tag,fn in heritage.MANDATORY.items():heritage.check_caption_image(si,f'Fig. {tag}.',fn)
 for tag,fn in NEW_FIGS.items():embedded_image(si,tag,fn)
 assert 'V9.10' not in m and 'V9.10' not in s.split('S27.')[0][:200]
 assert 'No version-matched public GitHub release' in m
 print('PASS: 5 main figures,',len(si.inline_shapes),'supplement figures, abstract, captions and 600 dpi all TIFFs')

def sha_manifest():
 f=ROOT/'MANIFEST_V9.11_SHA256.csv'
 if not f.is_file():print('INFO: manifest created by final packaging step');return
 rows=list(csv.DictReader(f.open()))
 for row in rows:
  p=ROOT/row['filename'];assert p.is_file(),p
  digest=hashlib.sha256(p.read_bytes()).hexdigest()
  assert digest==row['sha256'],f'Checksum mismatch: {p.name}'
 print('PASS: manifest SHA-256',len(rows),'entries')

def full(draws=150):
 cmds=[['us9_test.py'],['us99_agricultural_accounts.py','--fixed-hubs'],['us99_paired_uncertainty.py',str(draws)],
  ['us99_figures.py'],['us911_robustness.py'],['us911_figures.py'],['us911_documents.py']]
 for parts in cmds:
  print('REGENERATE',' '.join(parts),flush=True)
  subprocess.run([sys.executable,*parts],cwd=ROOT,check=True)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--full',action='store_true');parser.add_argument('--draws',type=int,default=150)
 args=parser.parse_args()
 if args.full:
  sha_manifest()  # Validate the original archive BEFORE regenerating files.
  full(args.draws)
  source_gate();numerics();figures_and_docs()
  if not args.full:sha_manifest()
 print('V9.11 PASS: computational and editorial validation. BT23, experimental HTL and full LCA evidence remain outstanding.')
if __name__=='__main__':main()
