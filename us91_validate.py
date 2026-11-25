"""Integrity checks for the author-review V9.1 release, no network dependency."""
from pathlib import Path
import csv,json,math,re,sys,hashlib
from PIL import Image
R=Path(__file__).resolve().parent
S=json.loads((R/'scenarios.json').read_text());A=json.loads((R/'us91_scientific_sensitivities.json').read_text());C=json.loads((R/'us9_crop_residue_results.json').read_text())
assert S['least_cost']['blend_vol']==0.0
for key,expected in [('least_cost',526.8657331030288),('design_sweet_spot',577.4173071102817),('design',640.8344436749152),('post_gas_least_cost',564.6229023763825),('sustainable_fission_nuclear_only',565.9122309144708),('sustainable_fission_nuclear_only_premium',604.2821030833117),('least_cost_vhtr',523.9237705997714)]:
 assert math.isclose(S[key]['transport_cost_bn'],expected,rel_tol=1e-7),(key,S[key]['transport_cost_bn'])
assert math.isclose(S['least_cost']['enduse']['el_total'],1836.7235486634781,rel_tol=1e-10)
assert math.isclose(A['bev_premium_break_even_usd_per_car_year'],343.414819,abs_tol=.02)
assert math.isclose(A['petroleum_2050_proxy_25pct_gasoline_saving_bn'],508.1794,abs_tol=.02)
for k,name,share in [('least_cost','least_cost',.749),('design_sweet_spot','sweet_spot',.440),('design','design',.097)]:
 with (R/f'monte_carlo_{name}.csv').open() as f: rows=list(csv.DictReader(f))
 assert len(rows)==1000
 n=sum(float(x['transport_cost_bn'])<float(x['petro_2025']) for x in rows)/1000
 assert abs(n-share)<1e-8,(k,n)
 assert abs(A['monte_carlo_conditional'][name]['share_cheaper']-share)<1e-8
assert math.isclose(C['paired_crop_full_sustainable_cap_forced']['transport_cost_bn'],532.4372666,abs_tol=.01)
assert math.isclose(C['paired_without_crop']['transport_cost_bn'],537.3551668,abs_tol=.01)
assert abs(float(A['grid_harvester']['energy']['conventional_mj'])-90.9)<.05
assert abs(float(A['grid_harvester']['energy']['faired_hose_10pct_mj'])-33.9)<.05
for k,v in S.items():
 if isinstance(v,dict) and 'objective_reconciliation' in v and k not in ('least_cost_blend20_sensitivity','design_blend20_sensitivity'):
  assert abs(v['objective_reconciliation']['residual_bn'])<1e-6,(k,'LP objective mismatch')
active=['ScienceFig1_energy_and_liquids.tif','ScienceFig2_national_system.tif','ScienceFig3_offshore_sensitivity.tif','ScienceFig4_cost_and_paired_uncertainty.tif','ScienceFigS1_grid_harvester.tif','ScienceFigS22_GridHarvester_Energy_Efficiency.tif','ScienceFigS23_Reference_and_BEV_Breakeven.tif','Poster_US_Map.tif']
for f in active:
 im=Image.open(R/f)
 assert im.format=='TIFF' and min(im.size)>1500 and all(abs(x-600)<.1 for x in im.info.get('dpi',(0,0))),f
m=(R/'MANUSCRIPT_V9.1.md').read_text();s=(R/'SUPPLEMENTARY_MATERIALS_V9.1.md').read_text()
assert all(x in m for x in ('526.9','577.4','640.8','74.9%','343','508.2','11.1%'))
assert len(re.findall(r'\b\d+\.\s',m.split('## References and Notes',1)[1].split('## Acknowledgments',1)[0]))>=18
assert 'US\\$517.0' not in s and 'US$517.0' not in s
assert all(len(re.findall(rf'^\*\*Table S{i}\.',s,re.M))==1 for i in range(1,11))
assert '90.9 MJ' in s and '33.9 MJ' in s and '62.7%' in s
if '--release-only' in sys.argv:
 bad=[p.name for p in R.iterdir() if p.suffix.lower() in ('.pdf','.png','.jpg','.jpeg','.webp')]
 assert not bad,bad
print('V9.1 PASS: seven core scenarios, no-blend cost boundary, three Monte Carlo samples, paired soil case, Grid Harvester energetics, TIFF tags, document numerical claims.')
