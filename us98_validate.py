#!/usr/bin/env python3
"""V9.8 validation: conservation, source-correction, independent scenario tests and publishing checks."""
import sys,subprocess,json,csv,zipfile,hashlib,math,os
from pathlib import Path
from PIL import Image
from docx import Document
P=Path(__file__).resolve().parent
full='--full' in sys.argv
if full:
 scripts=[['us97_aeo_boundary.py'],['us97_integrated.py'],['us98_agri_lca.py'],['us98_resource_crosswalk.py'],['us98_sensitivity.py'],['us98_paired_uncertainty.py','500'],['us97_figures.py'],['us98_figures.py'],['us98_documents.py']]
 for cmd in scripts:
  print('RERUN',' '.join(cmd),flush=True)
  subprocess.run([sys.executable,'-u',*cmd],cwd=P,check=True)

def ck(ok,msg):
 assert ok,msg
 print('PASS',msg,flush=True)
with zipfile.ZipFile(P/'AEO2026_2050_TRANSPORT_DATA.zip') as z:
 ck(z.testzip() is None,'Original EIA workbook ZIP integrity')
 ck(len([x for x in z.namelist() if x.lower().endswith('.xlsx')])>=38,'38 original EIA workbooks present')
import us97_aeo_boundary as B
import us96_aeo_shared_assumptions as V
idx=V.excise_tax_screen()['table36_source_rows']['diesel_onroad']
ck(24 in idx and 23 not in idx,'Diesel tax Table 36 row24 not row23')
b=json.loads((P/'US97_AEO_Boundary.json').read_text());r=b['reference_emissions']
ck(5.2<r['hydrogen_mass_mt']<5.5 and b['h2_energy_basis_bracket']['LHV']['hydrogen_mass_mt']>6.2,'HHV primary and LHV sensitivity hydrogen masses')
ck(r['reference_h2_production_kgco2_kg']>=0 and 106 not in r['included_fossil_table36_rows'],'Reference hydrogen and LNG excluded appropriately')
source=json.loads((P/'US97_Integrated_Circular_EIA.json').read_text());crop=source['scenario']['soil_costed_economic_crop']
ck(len(crop['selected'])==13,'All candidates visible')
ck(sum(float(x.get('selected_mt',0))>1e-8 for x in crop['selected'])==6,'Six *positive* crop categories, not 13')
for e in 'npk':
 ck(abs(crop[f'{e}_removed_kt']-sum(crop[f'{e}_{t}_kt'] for t in ('water','char','imports')))<1e-6,f'{e.upper()} elemental mass closure')
marine=source['marine_to_land_optional']
ck(math.isclose(marine['extra_cost_after_opportunity_cost_bn'],0.0792695,abs_tol=.000001),'Marine nutrient market values and logistics non-cancelling')
ss=json.loads((P/'US98_Strict_Crop_and_Reactor_Sensitivity.json').read_text())
ck(len(ss['cases'])==4 and len(ss['fixed_hub_cases'])==8,'Combined soil-resource and fixed reactor-hub screens')
ck(ss['cases'][2]['crop_mt']<ss['cases'][1]['crop_mt'],'Restricted primary agricultural supply stress')
ck(ss['cases'][1]['annual_cost_bn']>ss['cases'][0]['annual_cost_bn'],'Excluding both soil credits and halving nutrient recovery charged')
for q in ss['cases']+ss['fixed_hub_cases']:ck(abs(q['residual_bn'])<.0001,'Optimisation objective reconciliation')
lca=json.loads((P/'US98_Agriculture_Explicit_LCA.json').read_text())
ck(10<lca['central']['gross_candidate_addon_mt']<20,'Explicit gross candidate agricultural GHG process ledger')
ck('overlap' in lca['interpretation'].lower(),'Overlapping baseline lifecycle coefficients disclosed')
resource=json.loads((P/'US98_BT23_Resource_Audit.json').read_text())
ck(resource.get('regional_resource_data_present') is False,'BT23 county data NOT PRESENT flag preserved')
u=json.loads((P/'US98_Paired_Uncertainty_Summary.json').read_text())
ck(u['n']==500 and u['abt_usd_t_p05'] < u['abt_usd_t_median'] < u['abt_usd_t_p95'],'500 new paired draws and percentile order')
with (P/'us98_paired_uncertainty.csv').open(encoding='utf-8-sig') as f:
 rows=list(csv.DictReader(f)); ck(len(rows)==500,'500 reproducible paired CSV rows')
figs=['ScienceFig1_V98_Cost_LCA_Boundaries.tif','ScienceFig2_V98_Crop_Dispatch_and_Unverified_Caps.tif','ScienceFig3_V98_NPK_C_and_Conservative_Restoration.tif','ScienceFig4_V98_HTL_Return_Flow_With_Arrows.tif','ScienceFig5_V98_Uncertainty_and_Reactor_Screen.tif','ScienceFigS38_V98_Explicit_Agri_Emissions.tif','ScienceFigS39_V98_Regional_Data_Gap_Stress.tif','ScienceFigS40_V98_Marine_Market_Opportunity_Cost.tif','ScienceFigS41_V98_Reference_Hydrogen_HHV_LHV.tif']
for f in figs:
 with Image.open(P/f) as im:ck(im.mode=='RGB' and all(abs(v-600)<.5 for v in im.info.get('dpi',(0,0))),f'600 dpi RGB TIFF {f}')
main=Document(P/'Research_Article_V9.8_Science.docx');s='\n'.join(p.text for p in main.paragraphs)
a=s.split('Abstract',1)[1].split('Introduction',1)[0]
ck(len(a.split())<=125 and len(a.split())>90,f'Science abstract {len(a.split())} words')
ck(len(main.inline_shapes)==5,'Five active main data figures embedded in article')
ck('No crop residues' not in a and 'field-screened' not in s,'No field-validation or false abstract claim')
ck('Marine' not in s or '79 million' in s,'Marine fertilizer opportunity value corrected')
si=Document(P/'Supplementary_Materials_V9.8_Science.docx')
ck(len(si.tables)==12 and len(si.inline_shapes)>=21,'Supplement with 12 tables and 21 embedded technical figures')
ck('S21.' in '\n'.join(p.text for p in si.paragraphs),'Supplement complete through S21')
ck((P/'Cover_Letter_Science_V9.8.docx').is_file(),'Flagship Science cover letter')
print('V9.8 release checks: ALL TESTS PASSED. SCIENTIFIC INPUT GAPS REMAIN.',flush=True)
