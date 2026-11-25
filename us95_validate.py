#!/usr/bin/env python3
"""V9.5 release gate (standard library + scipy, numpy, Pillow, python-docx)."""
from __future__ import annotations
import csv,hashlib,json,math,pathlib,subprocess,sys
from PIL import Image
import us2_model as M
import us2_inputs as I
import us95_aeo_reference_bridge as B
HERE=pathlib.Path(__file__).resolve().parent

def check():
  j=json.loads((HERE/'US95_AEO2026_Cost_Emissions_Results.json').read_text())
  m=json.loads((HERE/'us95_paired_aeo_uncertainty_summary.json').read_text())
  prov,a=B.read_source()
  assert prov['sha256_all_passed'] and prov['source_file_count']==38
  assert math.isclose(a['freight_medium_heavy_m'],12.562507,abs_tol=.002)
  orig=M.solve_learning(M.default_params(),scenario='least_cost',blend_vol=0)
  assert math.isclose(orig['transport_cost_bn'],526.865733103,abs_tol=1e-6)
  assert math.isclose(orig['enduse']['h2_mt_direct']*I.H2_LHV_KWH_KG,188.44292525467378,abs_tol=1e-5)
  assert abs(orig['objective_reconciliation']['residual_bn'])<1e-7
  p,_=B.config(a)
  rr=M.solve_learning(p,scenario='least_cost',blend_vol=0)
  assert math.isclose(rr['transport_cost_bn'],j['scenarios']['v95_jet_eia_medium_heavy_fleet']['alternative_cost_bn_2026usd'],abs_tol=1e-5)
  assert math.isclose(rr['emissions']['total_mt'],j['scenarios']['v95_jet_eia_medium_heavy_fleet']['alternative_wtw_mt'],abs_tol=1e-5)
  assert j['reactor_bounded_search']['best_hubs']==945
  assert j['reactor_bounded_search']['best_cost_bn'] < rr['transport_cost_bn']
  assert m['draws']==1000 and m['median_alt_minus_reference_bn']>0
  tifs=list(HERE.glob('*.tif'))
  assert len(tifs)==37,(len(tifs),[p.name for p in tifs])
  for p in tifs:
    with Image.open(p) as im:
      assert all(abs(x-600)<.1 for x in im.info['dpi']),(p,im.info)
      assert im.mode=='RGB',(p,im.mode)
  from docx import Document
  d=Document(HERE/'Research_Article_V9.5.docx');s=Document(HERE/'Supplementary_Materials_V9.5.docx')
  docstrings='\n'.join(p.text for p in d.paragraphs+s.paragraphs)
  assert '188.44 TWh of direct transport hydrogen' in docstrings
  assert '118 TWh of hydrogen' not in docstrings
  for i in range(1,7):assert f'Fig. {i}.' in docstrings
  for i in range(1,32):assert f'Fig. S{i}.' in docstrings
  for i in range(1,20):assert f'Table S{i}.' in docstrings
  refs=set(__import__('re').findall(r'[A-Za-z0-9_]+\.tif',docstrings))
  missing=refs-set(p.name for p in tifs)
  assert not missing,missing
  assert len(s.tables)==19,len(s.tables)
  assert 'SR14.' in docstrings and 'SR23.' in docstrings
  assert len(list(csv.DictReader((HERE/'us95_paired_aeo_cost_screen.csv').open(encoding='utf-8-sig'))))==1000
  print(f'PASS V9.5: 38 official EIA files, original truck conversion, cost reconciliation, freight bridge, bounded learning, 1,000 paired outputs, 37 RGB 600-dpi TIFF figures, 6 main/31 supplementary figure captions, 19 SI tables, and source integrity.')

def full():
  before=json.loads((HERE/'US95_AEO2026_Cost_Emissions_Results.json').read_text())
  import us95_paired_uncertainty as MC
  new=B.make()
  for k,v in before['scenarios'].items():
    assert math.isclose(v['alternative_cost_bn_2026usd'],new['scenarios'][k]['alternative_cost_bn_2026usd'],rel_tol=1e-8)
  MC.run(1000,seed=9526)
  import us95_figures as F
  F.fig6();F.fleet();F.boundary();F.paired();F.crop();F.prices();F.reactor()
  check()

if __name__=='__main__':
  if '--full' in sys.argv:full()
  else:check()
