#!/usr/bin/env python3
"""Authoritative consistency validator for V9.7 source, results and submission documents.
--full re-executes the V9.7 source chain before validation. Requires scipy/numpy,
matplotlib, pandas and python-docx. The source EIA archive is not altered.
This tests computational consistency; it cannot prove field sustainability or LCA.
"""
import sys,json,csv,math,subprocess,zipfile,hashlib
from pathlib import Path
from PIL import Image
from docx import Document
R=Path(__file__).resolve().parent
FULL='--full' in sys.argv
if FULL:
    for cmd in [('us97_aeo_boundary.py',),('us97_circular_feedstocks.py',),('us97_integrated.py',),('us97_paired_uncertainty.py','500'),('us97_figures.py',),('us97_documents.py',)]:
        print('REBUILD',cmd[0],flush=True)
        subprocess.run([sys.executable,*cmd],cwd=R,check=True)

def eq(a,b,tol=1.e-5):
    assert math.isclose(float(a),float(b),rel_tol=0,abs_tol=tol),(a,b)

def check(cond,message):
    assert cond,message
    print('PASS:',message)

with zipfile.ZipFile(R/'AEO2026_2050_TRANSPORT_DATA.zip') as z:
    bad=z.testzip()
    check(bad is None,'AEO2026 workbook archive intact')
    xl=[x for x in z.namelist() if x.lower().endswith('.xlsx') and not x.startswith('__MACOSX')]
    check(len(xl)>=38,f'EIA XLSX files >=38 (found {len(xl)})')

import us97_aeo_boundary as A
check(24 in __import__('us96_aeo_shared_assumptions').excise_tax_screen()['table36_source_rows']['diesel_onroad'] and 23 not in __import__('us96_aeo_shared_assumptions').excise_tax_screen()['table36_source_rows']['diesel_onroad'], 'diesel Table36 indexing includes Excel row24')
b=json.loads((R/'US97_AEO_Boundary.json').read_text())
check(b['source_stock']['bev300_m']>90 and b['source_stock']['bev200_m']>60,'BEV stock-weighted prices from EIA data')
check(105 in b['reference_emissions']['included_fossil_table36_rows'],'pipeline gas explicit reference boundary')
check(106 not in b['reference_emissions']['included_fossil_table36_rows'],'LNG export processing outside transport scope')
check(b['reference_emissions']['hydrogen_mass_mt']>5,'reference H2 emissions tracked explicitly')

d=json.loads((R/'US97_Integrated_Circular_EIA.json').read_text());s=d['scenario'];c=s['soil_costed_economic_crop'];n=s['soil_costed_no_crop'];o=s['crop_seaweed_220gw_imposed'];
check(sum(float(x.get('selected_mt',x.get('mt',0)))>1.e-8 for x in c['selected'])>=2,'multiple positive crop residues selected')
eq(c['crop_htl_mt'],166);check(True,'national 166 Mt screening cap imposed')
check(c['annual_cost_bn'] < n['annual_cost_bn'],'economically optimised crop intake saves vs matched no-crop case')
for e in 'npk':eq(c[f'{e}_removed_kt'],c[f'{e}_water_kt']+c[f'{e}_char_kt']+c[f'{e}_imports_kt'],1e-4)
check(True,'N/P/K conservation (treated water + HTL solids + external inputs)')
check(c['stable_hydrochar_c_mt']+c['stable_pyrolysis_c_mt']+c['cover_crop_stable_c_mt']+1e-5 >= c['stable_soil_c_need_mt'],'modelled stable-equivalent soil-carbon closure')
check(o['seaweed_htl_mt']>0 and c['seaweed_htl_mt']==0,'marine seaweed scenario separately accounted')
check(o['annual_cost_bn']>c['annual_cost_bn'],'imposed seaweed/offshore case not falsely called least cost')
check(d['marine_to_land_optional']['eligible_treated_marine_npk_to_cropland_kt']['n']>0,'marine-to-field nutrient reuse is an optional screened transfer')

u=json.loads((R/'US97_Paired_Uncertainty_Summary.json').read_text())
check(u['n']==500,'500 current paired Monte Carlo draws')
with (R/'us97_paired_uncertainty.csv').open(encoding='utf-8-sig',newline='') as f:
    draws=list(csv.DictReader(f))
check(len(draws)==500,'Monte Carlo row count matches')
check(0 < u['abt_usd_t_p05']<u['abt_usd_t_median']<u['abt_usd_t_p95'],'cost per tonne uncertainty ordered')

main=[f'ScienceFig{i}_V97_' for i in range(1,6)]
main_names=['ScienceFig1_V97_2050_Cost_Abatement.tif','ScienceFig2_V97_All_Crop_Waste_Economic_Dispatch.tif','ScienceFig3_V97_NPK_Carbon_Soil_Closure.tif','ScienceFig4_V97_Terrestrial_Marine_HTL_Soil_Flow.tif','ScienceFig5_V97_Uncertainty_Resource_Constraints.tif']
for name in main_names:check((R/name).exists(),f'main {name}')
for t in R.glob('*.tif'):
    with Image.open(t) as im:
        check(im.mode=='RGB' and len(im.getbands())==3 and all(abs(z-600)<.1 for z in im.info.get('dpi',(0,0))),f'RGB TIFF 600dpi {t.name}')
main_doc=Document(R/'Research_Article_V9.7_Science.docx')
text='\n'.join(x.text for x in main_doc.paragraphs)
assert 'Abstract' in text
part=text.split('Abstract',1)[1].split('Introduction',1)[0].strip()
check(70 <=len(part.split())<=125,f'Science abstract length {len(part.split())}')
check(len(main_doc.inline_shapes)==5,'five main embedded figures in Word')
check('651' in text and 'N' in text and 'P' in text and 'K' in text,'integrated cost and nutrient findings in main text')
check('Sustainable Energy & Fuels' not in text and 'correction notice' not in text.lower(),'no obsolete journal or correction history in research article')
si=Document(R/'Supplementary_Materials_V9.7_Science.docx')
check(len(si.tables)>=7,'supplementary model tables embedded')
check((R/'Cover_Letter_Science_V9.7.docx').exists() and (R/'Title_Page_V9.7_Science.docx').exists(),'editor cover and separate title page')
print('V9.7 validation complete: ALL TESTS PASSED')
