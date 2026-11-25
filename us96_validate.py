#!/usr/bin/env python3
"""V9.6 release checks. --full also rebuilds the new scenarios, charts, and Word files."""
import csv,json,math,pathlib,sys,re
from PIL import Image
from docx import Document
import us95_aeo_reference_bridge as V
HERE=pathlib.Path(__file__).resolve().parent

def check():
 provenance,a=V.read_source();assert provenance['sha256_all_passed'] and provenance['source_file_count']==38
 assert math.isclose(a['ldv_2050_bev_m'],154.43543,abs_tol=1e-3)
 model=json.loads((HERE/'US96_Shared_2050_Screen.json').read_text()); rr=model['results'];assert len(rr)==3
 for r in rr:
  assert r['avoided_mt']>1000
  assert abs(r['alt_screen_bn']-r['reference_screen_bn']-r['incremental_alt_minus_reference_bn'])<1e-7
  assert abs(r['cost_per_tonne_avoided_usd']-1000*r['incremental_alt_minus_reference_bn']/r['avoided_mt'])<1e-6
  ref=(r['reference_energy_2026usd_bn']-r['tax_removed_bn']+r['reference_ldv_net_premium_bn']+
       r['reference_truck_net_premium_bn']+r['reference_charging_bn']+r['reference_coverage_add_bn'])
  assert abs(ref-r['reference_screen_bn'])<1e-7
 assert 60<rr[0]['cost_per_tonne_avoided_usd']<70
 assert 120<rr[1]['cost_per_tonne_avoided_usd']<140
 assert 175<rr[2]['cost_per_tonne_avoided_usd']<185
 series=list(csv.DictReader((HERE/'us96_deployment_stress.csv').open()));assert len(series)>=10
 assert int(series[-1]['hubs'])==945
 figs=list(HERE.glob('*.tif'));assert len(figs)==41,(len(figs),[f.name for f in figs])
 for f in figs:
  with Image.open(f) as im:
   assert im.mode=='RGB',f.name
   assert all(abs(v-600)<.2 for v in im.info.get('dpi',(0,0))),f.name
 d=Document(HERE/'Research_Article_V9.6.docx');s=Document(HERE/'Supplementary_Materials_V9.6.docx')
 assert len(d.tables)==2,len(d.tables)
 assert len(s.tables)==21,len(s.tables)
 assert '188.44 TWh' in '\n'.join(p.text for p in s.paragraphs)
 assert 'S6. Land-biomass' in '\n'.join(p.text for p in s.paragraphs)
 abstract=next((d.paragraphs[i+1].text for i,p in enumerate(d.paragraphs[:-1]) if p.text.strip()=='Abstract'))
 assert len(abstract.split())<=250
 text='\n'.join(p.text for p in d.paragraphs+s.paragraphs)
 assert 'Fig. 7.' in text and 'Fig. S33.' in text and 'Table S21.' in text
 refs=set(re.findall(r'[\w.-]+\.tif',text))
 assert not (refs-set(p.name for p in figs)),(refs-set(p.name for p in figs))
 assert 'Science Editor' not in '\n'.join(p.text for p in Document(HERE/'Cover_Letter_Sustainable_Energy_Fuels_V9.6.docx').paragraphs)
 print('PASS V9.6: 38 EIA sources, 3 matched-BEV-price screens and cost arithmetic, 12 deployment points, 41 RGB 600-dpi TIFFs, 2 main/21 SI tables, source references and cover letter')

if __name__=='__main__':
 if '--full' in sys.argv:
  import us96_aeo_shared_assumptions as A
  A.run()
  import subprocess
  subprocess.run([sys.executable,str(HERE/'us96_deployment_stress.py')],check=True,cwd=HERE)
  subprocess.run([sys.executable,str(HERE/'us96_figures.py')],check=True,cwd=HERE)
  subprocess.run([sys.executable,str(HERE/'us96_documents.py')],check=True,cwd=HERE)
 check()
