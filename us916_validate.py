from pathlib import Path
import csv,json,hashlib,io,math
from docx import Document
from PIL import Image
import numpy as np
P=Path(__file__).resolve().parent

def main():
 rows=list(csv.DictReader((P/'V915_PRESERVED_ARTWORK_SHA256.csv').open()));assert len(rows)==72
 for q in rows:assert hashlib.sha256((P/q['filename']).read_bytes()).hexdigest()==q['sha256'],q['filename']
 d=json.loads((P/'US916_Coupled_Results.json').read_text());assert len(d['rows'])==45;assert abs(d['baseline_rerun_cost_bn']-654.7633815744267)<1e-6
 for q in d['rows']:
  assert abs(q['combined_cost_saving_bn']-q['ref_cost_bn']+q['combined_cost_bn'])<1e-8
  assert abs(q['combined_avoided_mt']-(q['ref_emissions_mt']-q['transport_emissions_before_ad_mt']+q['gas_direct_credit_mt']+q['agri_net_avoided_mt']))<1e-8
  assert q['displaced_pipeline_hhv_twh']<=d['gas_pipeline_hhv_twh']+1e-8
  assert abs(q['gas_direct_credit_mt']-q['internal_biomethane_lhv_twh']*.202)<1e-8
 cross=list(csv.DictReader((P/'US914_EDITORIAL_FIGURE_PROVENANCE.csv').open()));cross.extend([dict(editorial_name='Figure_S31.tif',original_600dpi_tiff='ScienceFigS51_V915_Methane_Abatement.tif'),dict(editorial_name='Figure_S32.tif',original_600dpi_tiff='ScienceFigS52_V916_Reference_and_Gas_Routing.tif')]);assert len(cross)==37
 for name,rr in [('Research_Article_V9.16_Science.docx',cross[:5]),('Supplementary_Materials_V9.16_Science.docx',cross[5:])]:
  doc=Document(P/name);images=[]
  for par in doc.paragraphs:
   for bl in par._p.xpath('.//*[local-name()="blip"]'):
    assert par.alignment==1,(name,par.text);images.append(doc.part.related_parts[bl.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')].blob)
  assert len(images)==len(rr)
  for b,q in zip(images,rr):
   with Image.open(io.BytesIO(b)) as im:a=np.array(im.convert('RGB').resize((100,100))).astype(float)
   with Image.open(P/q['original_600dpi_tiff']) as im:
    dpi=im.info.get('dpi',(0,0)); assert all(abs(z-600)<1 for z in dpi) or q['original_600dpi_tiff'] in ('FigS1_grid_harvester.tif','FigS13_fuel_transition.tif'),q['original_600dpi_tiff']; y=np.array(im.convert('RGB').resize((100,100))).astype(float)
   assert np.mean((a-y)**2)<20,q['original_600dpi_tiff']
 print('PASS: 72 exact supplied artwork hashes; 37 centered figures and TIFF pixel crosswalk (two original DPI exceptions); 45 gas-routing and reference balances')
if __name__=='__main__':main()
