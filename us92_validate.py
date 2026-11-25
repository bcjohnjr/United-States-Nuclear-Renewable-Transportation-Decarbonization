"""V9.2 release checks: grounded costs, figure metadata, file references, document hygiene."""
from pathlib import Path
from PIL import Image
import json,csv,re,math
R=Path(__file__).resolve().parent
S=json.loads((R/'scenarios.json').read_text());A=json.loads((R/'us91_scientific_sensitivities.json').read_text())
assert S['least_cost']['blend_vol']==0
for k,v in {'least_cost':526.8657331030288,'design_sweet_spot':577.4173071102817,'design':640.8344436749152,'post_gas_least_cost':564.6229023763825}.items():
 assert abs(S[k]['transport_cost_bn']-v)<1e-5,k
assert abs(S['least_cost']['enduse']['el_total']-1836.7235486634781)<.001
assert S['least_cost']['gw']['offshore_wind']==0 and S['least_cost']['gw']['onshore_wind']>200
main=(R/'MANUSCRIPT_V9.2.md').read_text();sup=(R/'SUPPLEMENTARY_MATERIALS_V9.2.md').read_text()
abstract=main.split('## Abstract',1)[1].split('## Introduction',1)[0].strip()
assert len(abstract.split())<=125
for a in ['526.9','189.1','2,873','−US$24.6','2050','Fig. 2']:
 assert a in main,a
assert 'author-review replacement' not in main and 'should not be cited as available' not in main
for i in range(1,11):assert len(re.findall(rf'^\*\*Table S{i}\.',sup,re.M))==1,i
assert '-0.0' not in sup
rows=list(csv.DictReader((R/'us92_abatement_sensitivity.csv').open()))
assert len(rows)==8
for n,target in [(0,-24.56),(20,.72),(25,7.85),(35,23.24)]:
 row=next(x for x in rows if float(x['gasoline_cut_pct'])==n)
 assert abs(float(row['abatement_usd_t_adjusted_tailpipe'])-target)<.03,(n,row)
assert 'AEO2026' in main and 'not reported' in sup
assert 'Fig. S1' in sup and 'Fig. S23' in sup
# all active images referenced by article or SI, no PDFs or non-TIFF images in delivery
figure_names=set(re.findall(r'`([^`]+\.tif)`',sup))
figure_names|=set(re.findall(r'!\[\]\(([^)]+\.tif)\)',main))
assert len(figure_names)==27,(len(figure_names),figure_names)
for name in figure_names:
 im=Image.open(R/name); dpi=im.info.get('dpi',(0,0))
 assert im.format=='TIFF' and min(im.size)>1000 and all(abs(x-600)<.5 for x in dpi),name
print(f'V9.2 PASS: 4 headline scenarios; 8 abatement sensitivities; abstract {len(abstract.split())} words; Tables S1–S10; {len(figure_names)} TIFFs at 600 dpi.')
