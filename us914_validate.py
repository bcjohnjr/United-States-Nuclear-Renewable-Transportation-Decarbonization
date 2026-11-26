#!/usr/bin/env python3
"""V9.14 flat-directory code/data, text and editorial integrity audit.
--full rebuilds in a separate temporary flat directory, leaving the released
archive and its SHA256 manifest untouched; no working tree or GitHub checkout needed.
"""
import argparse,csv,hashlib,io,json,math,re,shutil,subprocess,sys,tempfile,zipfile
from pathlib import Path
from PIL import Image
from docx import Document
import numpy as np
import us912_validate as precedent
from us99_agricultural_accounts import integrated_lca
from us2_model import CI_RESIDUES_GRASSES_G_MJ
R=Path(__file__).resolve().parent
DOCS=['Research_Article_V9.14_Science.docx','Supplementary_Materials_V9.14_Science.docx','Cover_Letter_Science_V9.14.docx','Title_Page_V9.14_Science.docx']
FIGS={'1':'ScienceFig1_V914_Conditional_Cost_and_LCA.tif','5':'ScienceFig5_V914_Uncertainty_and_Reactor.tif'}
SFIG={'S1':'FigS1_grid_harvester.tif','S22':'FigS22_GridHarvester_Energy_Efficiency.tif','S30':'ScienceFigS50_V914_Joint_HTL_Yield_Delivery.tif'}

def manifest():
 rows=list(csv.DictReader((R/'MANIFEST_V9.14_SHA256.csv').open(encoding='utf-8-sig')))
 assert len(rows)>250,len(rows)
 for q in rows:
  fn=R/q['filename']; assert fn.is_file(),fn
  assert hashlib.sha256(fn.read_bytes()).hexdigest()==q['sha256'],q['filename']
 print('PASS: immutable flat-root SHA-256:',len(rows),'files',flush=True)

def lifecycle():
 assert CI_RESIDUES_GRASSES_G_MJ==10.0
 d=json.loads((R/'US99_Scenario_Analysis.json').read_text()); c=d['scenarios'][0];no=d['scenarios'][-1]
 assert abs(c['crop_htl_liquid_twh']-431.6)<.00001
 assert abs(c['mixed_residue_liquid_twh']-1173.8782542125234)<1e-5
 assert c['crop_htl_liquid_twh']<c['mixed_residue_liquid_twh']
 ls=[integrated_lca(c,assumed_crop_ci_g_mj=q) for q in [7.0,10.0,13.0]]
 assert max(x['replaced_route_screen_mt'] for x in ls)-min(x['replaced_route_screen_mt'] for x in ls)<1e-10
 assert abs(ls[1]['generic_crop_ci_replaced_mt']-15.5376)<1e-8
 assert abs(ls[1]['replaced_route_screen_mt']-229.38444669755273)<1e-7
 assert abs(integrated_lca(no)['generic_crop_ci_replaced_mt'])<1e-9
 bad=dict(c);bad['mixed_residue_liquid_twh']=1
 try:integrated_lca(bad);raise AssertionError('Failed to reject excess crop-energy fraction')
 except ValueError:pass
 print('PASS: source-linked 10 g/MJ route, 431.6/1173.9-TWh crop-energy budget, no phantom CI sensitivity',flush=True)

def pixel(doc,tag,fn,max_dims):
 ps=doc.paragraphs
 hits=[i for i,p in enumerate(ps) if p.text.startswith('Fig. '+tag+'.')]
 assert len(hits)==1,(tag,hits)
 blips=ps[hits[0]-1]._p.xpath('.//*[local-name()="blip"]'); assert len(blips)==1,tag
 rid=blips[0].get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
 with Image.open(io.BytesIO(doc.part.related_parts[rid].blob)) as z: x=np.array(z.convert('RGB'),dtype=np.float32)
 with Image.open(R/fn) as z:y=z.convert('RGB');y.thumbnail(max_dims);y=np.array(y,dtype=np.float32)
 assert x.shape==y.shape,(tag,x.shape,y.shape)
 mse=float(np.mean((x-y)**2));assert mse<8,(tag,mse)
 return mse

def docs():
 mm=Document(R/DOCS[0]);si=Document(R/DOCS[1]);cover=Document(R/DOCS[2]);title=Document(R/DOCS[3])
 assert (len(mm.inline_shapes),len(si.inline_shapes),len(si.tables))==(5,30,17)
 m='\n'.join(p.text for p in mm.paragraphs);ss='\n'.join(p.text for p in si.paragraphs)
 ai=next(i for i,p in enumerate(mm.paragraphs) if p.text.strip()=='Abstract')
 ab=mm.paragraphs[ai+1].text
 assert 85<=len(ab.split())<=125 and '59.8%' in ab and '1,000' in ab
 assert '15.5376 Mt' in m and '431.6 TWh' in m
 assert 'S1–S32' in m and 'S32. Audited crop-route coefficient' in ss
 assert 'Incremental' in m or 'incremental' in m
 assert 'V9.13' not in '\n'.join([ab,mm.paragraphs[-1].text])
 assert 'Cloud Wash Laundry Corporation' in m
 assert 'Artificial Inventor / Synthetic Scientist V63' in m
 assert 'AI systems are not authors' in m
 assert 'AI systems are not authors' in '\n'.join(p.text for p in cover.paragraphs)
 assert 'RUN_V914_REPRODUCE.bat' in ss
 for tag,fn in FIGS.items():pixel(mm,tag,fn,(1800,1350))
 for tag,fn in SFIG.items():pixel(si,tag,fn,(1650,1120) if tag in ('S1','S22') else (1800,1350))
 caps=[]
 for i,p in enumerate(si.paragraphs):
  v=re.match(r'^Fig\. S(\d+)\.',p.text)
  if v and i and si.paragraphs[i-1]._p.xpath('.//*[local-name()="blip"]'):caps.append(int(v.group(1)))
 assert caps==list(range(1,31)),caps
 for f in R.glob('*.tif'):
  with Image.open(f) as im:
   assert im.mode=='RGB' and all(abs(z-600)<1 for z in im.info.get('dpi',(0,0))),f
 assert len(title.paragraphs)>3
 print('PASS: 4 Word documents, abstract, 17 tables, 5+30 captions/embedded figures, 600-dpi TIFF',flush=True)

def data():
 precedent.outputs()
 st=json.loads((R/'US914_Paired_Uncertainty_Summary.json').read_text())
 rows=list(csv.DictReader((R/'us914_paired_uncertainty.csv').open()))
 assert st['version']=='9.14' and len(rows)==st['n_requested']==st['n_feasible']==1000
 vals=np.array([float(r['abatement_usd_t']) for r in rows])
 assert math.isclose(float(np.median(vals)),st['median_usd_t'],abs_tol=1e-7)
 assert math.isclose(float(np.percentile(vals,5)),st['p05_usd_t'],abs_tol=1e-7)
 assert math.isclose(float(np.percentile(vals,95)),st['p95_usd_t'],abs_tol=1e-7)
 assert abs(st['zero_crop_fraction']-.598)<1e-10
 for v in rows:
  assert abs(float(v['audited_model_route_ci_gco2_mj'])-CI_RESIDUES_GRASSES_G_MJ)<1e-10
  assert abs(float(v['incremental_bn'])-(float(v['alternative_bn'])-float(v['reference_bn'])))<1e-7
  assert abs(float(v['abatement_usd_t'])-1000*float(v['incremental_bn'])/float(v['avoided_mt']))<1e-7
 assert len(list(csv.DictReader((R/'us913_combined_yield_delivery.csv').open())))==16
 with zipfile.ZipFile(R/'AEO2026_2050_TRANSPORT_DATA.zip') as z:
  assert len([f for f in z.namelist() if f.endswith('.xlsx')])>=38
 print('PASS: 1,000 audited paired draws, AEO workbooks, 16 yield-delivery screens, upstream unit gates',flush=True)

def editorial():
 with zipfile.ZipFile(R/'SCIENCE_EDITORIAL_UPLOAD_ONLY_V9.14.zip') as z:
  names=z.namelist()
  assert len(names)==39 and len([n for n in names if n.lower().endswith('.tif')])==35
  for name in DOCS:assert z.read(name)==(R/name).read_bytes()
  prov=list(csv.DictReader((R/'US914_EDITORIAL_FIGURE_PROVENANCE.csv').open()))
  assert len(prov)==35
  for r in prov:assert z.read(r['editorial_name'])==(R/r['original_600dpi_tiff']).read_bytes()
  assert 'Figure_S1.tif' in names and 'Figure_S22.tif' in names
 print('PASS: editor-only ZIP content equals distributed Word files and exact 35 source TIFFs',flush=True)

def quick(verify_manifest=True):
 if verify_manifest:manifest()
 lifecycle();data();docs();editorial()
 print('V9.14.1 EDITORIAL REVISION PASS — scientific screening only; NOT figure-rights/DOI-cleared',flush=True)

def full():
 quick()
 # Copy instead of rebuilding the checksum-verified release in-place: protects the hashes.
 with tempfile.TemporaryDirectory(prefix='us914_flat_repro_') as tmp:
  root=Path(tmp)
  for src in R.iterdir():
   if src.is_file():shutil.copy2(src,root/src.name)
  steps=[['us9_test.py'],['us99_agricultural_accounts.py','--fixed-hubs'],
         ['us911_robustness.py'],['us912_yield_sensitivity.py'],
         ['us913_combined_sensitivity.py'],['us914_paired_uncertainty.py','1000'],
         ['us914_figures.py'],['us914_documents.py']]
  for args in steps:
   print('FLAT-ROOT REBUILD:',*args,flush=True)
   subprocess.run([sys.executable,*args],cwd=root,check=True)
  subprocess.run([sys.executable,'us914_validate.py','--skip-manifest'],cwd=root,check=True)
  # Numerical CSV must be bitwise deterministic on identical machine/solver.
  for name in ('us914_paired_uncertainty.csv','US914_Paired_Uncertainty_Summary.json'):
   assert (root/name).read_bytes()==(R/name).read_bytes(),name
  # DOCX container ZIP metadata can carry creation timestamps. Compare every
  # OOXML part byte-for-byte instead of falsely failing on ZIP headers.
  for name in DOCS:
   with zipfile.ZipFile(root/name) as rebuilt, zipfile.ZipFile(R/name) as released:
    assert rebuilt.namelist()==released.namelist(),name
    assert all(rebuilt.read(p)==released.read(p) for p in rebuilt.namelist()),name
  # The current regenerated TIFFs are pixel/byte deterministic under the
  # pinned environment (old historical figures are checked separately).
  for name in ('ScienceFig1_V914_Conditional_Cost_and_LCA.tif','ScienceFig5_V914_Uncertainty_and_Reactor.tif','ScienceFigS50_V914_Joint_HTL_Yield_Delivery.tif'):
   assert (root/name).read_bytes()==(R/name).read_bytes(),name
  print('PASS: exact MC outputs, all regenerated OOXML parts, three TIFFs',flush=True)
 print('PASS: fresh isolated flat-directory full reproduction; original SHA-256 files unchanged',flush=True)
 manifest()

def main():
 a=argparse.ArgumentParser()
 a.add_argument('--full',action='store_true');a.add_argument('--skip-manifest',action='store_true')
 v=a.parse_args();full() if v.full else quick(not v.skip_manifest)
if __name__=='__main__':main()
