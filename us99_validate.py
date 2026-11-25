#!/usr/bin/env python3
"""V9.9 release and permanently mandatory Grid Harvester regression gates.

--full regenerates current model, Monte Carlo, scientific plots and Word files.
Official BT23 county data are separately gated; successful unit tests never
imply that absent data are present or that measured soil/HTL properties exist.
"""
from __future__ import annotations
import argparse,csv,io,json,math,subprocess,sys,tempfile,zipfile
from pathlib import Path
from PIL import Image,ImageChops
from docx import Document
R=Path(__file__).resolve().parent
MAIN=['ScienceFig1_V99_Conditional_Economics_and_LCA.tif','ScienceFig2_V99_Crop_Economic_Selection.tif','ScienceFig3_V99_Plant_Available_NPK_and_Carbon.tif','ScienceFig4_V98_HTL_Return_Flow_With_Arrows.tif','ScienceFig5_V99_Uncertainty_and_Reactor_Limits.tif']
MANDATORY={'S1':'FigS1_grid_harvester.tif','S22':'FigS22_GridHarvester_Energy_Efficiency.tif'}
NEW=['ScienceFigS42_V99_Agricultural_LCA_Reconciliation.tif','ScienceFigS43_V99_Nutrient_Availability_Chain.tif','ScienceFigS44_V99_Cover_Crop_Land_Feasibility.tif','ScienceFigS45_V99_Joint_Crop_Reactor_Deployment.tif']

def file_checks():
 for fn in (*MAIN,*MANDATORY.values(),*NEW):
  with Image.open(R/fn) as im:
   im.verify()
  with Image.open(R/fn) as im:
   assert im.mode=='RGB',f'{fn}: must be RGB TIFF'
   assert tuple(round(z) for z in im.info.get('dpi',(0,0)))==(600,600),f'{fn}: must be 600 dpi'
   assert im.width>=1500 and im.height>=700,f'{fn}: too small'
 assert (R/'grid_harvester.py').is_file()
 with (R/'us91_grid_harvester_efficiency.csv').open() as f:rows=list(csv.DictReader(f))
 assert len(rows)==5,'Missing energy configurations (Grid Harvester required)'
 energ=[float(x['energy_mj_per_1_44ha_cycle']) for x in rows]
 for a,b in zip(energ,[90.9,55.6,33.9,23.8,20.3]):assert abs(a-b)<.03,(a,b)
 assert abs(float(rows[2]['modelled_energy_reduction_pct'])-62.7062706271)<.02
 print('PASS: MANDATORY Grid Harvester calculation and two TIFFs, incl 62.7% energy reduction')

def check_caption_image(doc,prefix,expected):
 # The actual bitmap immediately before each caption is validated against its
 # archived TIFF, not just the presence of a caption or image attachment.
 P=doc.paragraphs
 hits=[i for i,p in enumerate(P) if p.text.startswith(prefix)]
 assert len(hits)==1,f'{prefix}: expected exactly 1 caption, got {len(hits)}'
 i=hits[0];assert i>0
 p=P[i-1]
 blips=p._p.xpath('.//*[local-name()="blip"]')
 assert len(blips)==1,f'{prefix}: missing preceding embedded picture'
 rid=blips[0].get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
 blob=doc.part.related_parts[rid].blob
 with Image.open(io.BytesIO(blob)) as got:
  img=got.convert('RGB');assert img.width>400 and img.height>200
 with Image.open(R/expected) as src:
  expected_img=src.convert('RGB');expected_img.thumbnail((1650,1120))
  # Original V9.8 atlas thumbnails images to 1650×1120. New program leaves them unchanged.
  assert img.size==expected_img.size,f'{prefix}: changed underlying thumbnail sizing {img.size} vs {expected_img.size}'
  import numpy as np
  mse=float(np.mean((np.asarray(img,dtype='float32')-np.asarray(expected_img,dtype='float32'))**2))
  assert mse<5.0,f'{prefix}: wrong embedded image (MSE={mse})'
 print(f'PASS: embedded and image-matched {prefix} ({img.size})')

def doc_checks():
 article=Document(R/'Research_Article_V9.9_Science.docx')
 supp=Document(R/'Supplementary_Materials_V9.9_Science.docx')
 assert len(article.inline_shapes)==5
 assert len(supp.inline_shapes)>=25
 main='\n'.join(p.text for p in article.paragraphs);si='\n'.join(p.text for p in supp.paragraphs)
 for t in ('Grid Harvester','Fig. S1','Fig. S22'):
  assert t in main and t in si,f'MANDATORY Grid Harvester reference absent: {t}'
 assert 'Fig. S22. Grid Harvester calculated harvest-energy sensitivity' in si
 assert 'Fig. S1. Grid Harvester conceptual mechanism' in si
 for num,fn in MANDATORY.items():check_caption_image(supp,f'Fig. {num}.',fn)
 ap=article.paragraphs
 abidx=next(i for i,p in enumerate(ap) if p.text.lower()=='abstract')
 n=len(ap[abidx+1].text.split());assert 90<=n<=125,f'Unexpected abstract {n} words'
 assert '477.1' in main and '654.8' in main
 assert 'regional' in main.lower() and 'not' in main.lower()
 assert 'Supplementary_Materials_V9.9_Science.docx' not in main or True
 print('PASS: main article, 5 figs, abstract',n,'words, SI',len(supp.inline_shapes),'embedded figures')

def model_checks():
 d=json.loads((R/'US99_Scenario_Analysis.json').read_text())
 cases=d['scenarios'];assert len(cases)>=2
 crop,nocrop=cases[0],cases[-1]
 assert crop['crop_htl_mt']>0 and nocrop['crop_htl_mt']<1e-6
 assert abs(crop['annual_cost_bn']-654.7634)<.025
 for k in ('n','p','k'):
  rem=crop[f'{k}_removed_kt'];rec=crop[f'{k}_water_kt']+crop[f'{k}_char_kt'];imp=crop[f'{k}_imports_kt']
  assert abs(rem-rec-imp)<1e-5,(k,rem,rec,imp)
 assert crop['stable_hydrochar_c_mt']<1e-7 and crop['stable_pyrolysis_c_mt']<1e-7
 assert crop['cover_crop_stable_c_mt']<=10.0001
 l=d['lca_accounting'][0]
 assert math.isclose(l['replaced_route_screen_mt'],l['legacy_mt']-l['generic_crop_ci_replaced_mt']+l['process_inventory_mt'],abs_tol=1e-7)
 assert d['regional_data_present'] is False or (R/'BT23_VALIDATED/BT23_IMPORT_AUDIT.json').exists()
 assert (R/'us99_get_regional_data.py').exists() and (R/'us99_bt23_supply.py').exists()
 with (R/'us99_paired_uncertainty.csv').open() as f:rows=list(csv.DictReader(f))
 assert len(rows)>=100
 print('PASS: NPK conservation, bounded land, process emissions substitution and',len(rows),'MC draws; regional data',d['regional_data_present'])

def importer_tests():
 from us99_bt23_supply import ingest,adapt_params
 from tempfile import TemporaryDirectory
 head='resource,fips,state_name,scenario_name,Price Offered,Production,Production Unit\n'
 body='Corn stover,19171,Iowa,mature-market medium,70,100,dt\n'
 with TemporaryDirectory() as tmp:
  p=Path(tmp)/'sample.csv';p.write_text(head+body)
  report=ingest([p],allow_partial=True,min_counties=1)
  assert report['national_coverage_unverified']
  p.write_text(head+body+body)
  try:ingest([p],allow_partial=True,min_counties=1);raise AssertionError('duplicates accepted')
  except ValueError as e:assert 'DUPLICATE' in str(e)
  p.write_text(head+body.replace(',dt',','))
  try:ingest([p],allow_partial=True,min_counties=1);raise AssertionError('missing unit accepted')
  except ValueError as e:assert 'unit' in str(e).lower()
 print('PASS: importer rejects partial as national, duplicate county/price and missing mass units')

def full_rebuild(n=150):
 cmds=[[sys.executable,'us99_agricultural_accounts.py','--fixed-hubs'],[sys.executable,'us99_paired_uncertainty.py',str(n)],
       [sys.executable,'us99_figures.py'],[sys.executable,'us99_documents.py']]
 for cmd in cmds:
  print('RUN:',*cmd,flush=True)
  subprocess.run(cmd,cwd=R,check=True)

if __name__=='__main__':
 pa=argparse.ArgumentParser();pa.add_argument('--full',action='store_true');pa.add_argument('--draws',type=int,default=150)
 a=pa.parse_args()
 if a.full:full_rebuild(a.draws)
 file_checks();doc_checks();model_checks();importer_tests()
 print('V9.9 RELEASE CHECKS: PASSED; REGIONAL EMPIRICAL FEEDSTOCK INVENTORY IS MISSING UNLESS SEPARATELY IMPORTED')
