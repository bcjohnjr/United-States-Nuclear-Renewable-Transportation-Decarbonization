#!/usr/bin/env python3
"""V9.11 resource-delivery, cover-area and residue counterfactual robustness.

No county-derived quantities are claimed. All stress cases use the V9.10
joint-conservative nutrient/soil model and are compared with one matched
no-crop alternative. Crop collection premiums are applied ONLY to crop tiers;
transport, treatment and mineral-fertilizer costs already in tiers are kept.
"""
from __future__ import annotations
import copy,csv,json,math
from pathlib import Path
import us97_circular_feedstocks as C
import us99_agricultural_accounts as G
import us95_aeo_reference_bridge as A
R=Path(__file__).resolve().parent
AVAIL=[0,0.25,0.5,0.75,1]
PREMIUM=[0,20,40,80,120]
LAND=[5,10,15,17.17,20,30]
FIELD=[-0.05,-0.025,0,0.025,0.05]
# Plus = reference field GHG credited (leaving residues would emit);
# negative = collection creates foregone field SOC/N2O benefit relative to leaving residues.
def setup(a,bev,cap_mt=166,delivery_usd_t=0,land_mha=20,accumulation_t_c_ha_yr=0.5):
 if not 0<=cap_mt<=166:raise ValueError('Use a nonnegative analyst ceiling <=166 Mt')
 if delivery_usd_t<0:raise ValueError('Negative delivery surcharge must not create unpriced biomass subsidies')
 p=C.build_params(a,bevpremium=bev,cap_mt=cap_mt,
      release_fraction=.5,apply_pyro_to_soil=False,allow_stable_hydrochar=False)
 p=G.carbon_land(G.plant_available(p),land_mha*1e6,accumulation_t_c_ha_yr)
 tiers=p['BIOMASS']['tiers']
 n=len(C.CANDIDATES)
 for i,(name,cap,cost) in enumerate(tiers[:n]):
  tiers[i]=(name,cap,cost+delivery_usd_t)
 return p

def run():
 boundary=json.loads((R/'US97_AEO_Boundary.json').read_text())
 bev=boundary['results'][1]['net_bev_differential_usd_yr']
 _,a=A.read_source()
 base=C.one('matched no-crop alternative',setup(a,bev,0))
 rows=[]
 for availability in AVAIL:
  for delivery in PREMIUM:
   c=C.one('robustness',setup(a,bev,166*availability,delivery))
   l=G.integrated_lca(c)
   rows.append(dict(resource_ceiling_fraction=availability,analyst_cap_mt=166*availability,
    delivery_surcharge_usd_dry_metric_t=delivery,selected_crop_mt=c['crop_htl_mt'],
    annual_cost_bn=c['annual_cost_bn'],matched_no_crop_bn=base['annual_cost_bn'],
    crop_saving_bn=base['annual_cost_bn']-c['annual_cost_bn'],
    n_external_kt=c['n_imports_kt'],p_external_kt=c['p_imports_kt'],k_external_kt=c['k_imports_kt'],
    process_substitution_alt_mt=l['replaced_route_screen_mt'],
    emissions_legacy_mt=l['legacy_mt'],coverage_status='ANALYST SCREEN ONLY; NOT DOE COUNTY DATA'))
 assert math.isclose(rows[0]['annual_cost_bn'],base['annual_cost_bn'],abs_tol=1e-6)
 write_rows('us911_resource_delivery_grid.csv',rows)
 land=[]
 for area in LAND:
  try:
   c=C.one('cover-land stress',setup(a,bev,166,0,area))
   land.append(dict(assumed_cover_crop_land_mha=area,net_additional_C_t_ha_yr=.5,
    maximum_additional_C_mt=area*.5,selected_crop_mt=c['crop_htl_mt'],annual_cost_bn=c['annual_cost_bn'],
    crop_saving_bn=base['annual_cost_bn']-c['annual_cost_bn'],
    cover_crop_service_mt=c['cover_crop_stable_c_mt'],status='FEASIBLE'))
  except Exception as exc:
   land.append(dict(assumed_cover_crop_land_mha=area,net_additional_C_t_ha_yr=.5,
    maximum_additional_C_mt=area*.5,selected_crop_mt='',annual_cost_bn='',
    crop_saving_bn='',cover_crop_service_mt='',status=f'INFEASIBLE ({type(exc).__name__})'))
 write_rows('us911_cover_land_stress.csv',land)
 central=C.one('V9.11 central',setup(a,bev))
 lca=G.integrated_lca(central)
 baseline=C.one('V9.11 no crop',setup(a,bev,0))
 n_lca=G.integrated_lca(baseline)
 emissions=[]
 for field in FIELD:
  # Counterfactual expressed as Mt CO2e/year = rate (t/t) x collection (Mt).
  l=G.integrated_lca(central,field_counterfactual_mt=field*central['crop_htl_mt'])
  emissions.append(dict(field_residue_counterfactual_tco2e_per_dryt=field,
   assumed_field_counterfactual_mt=field*central['crop_htl_mt'],
   crop_alt_partial_mt=l['replaced_route_screen_mt'],no_crop_alt_partial_mt=n_lca['replaced_route_screen_mt'],
   incremental_crop_emissions_mt=l['replaced_route_screen_mt']-n_lca['replaced_route_screen_mt'],
   crop_saving_bn=baseline['annual_cost_bn']-central['annual_cost_bn'],
   status='ASSUMED BOUND; SOURCE-SPECIFIC FIELD SOC/N2O DATA NOT AVAILABLE'))
 write_rows('us911_field_counterfactual_lca.csv',emissions)
 summary=dict(version='9.11',bt23_county_evidence=False,analyst_national_screen_mt=166,
    modeled_reference_baseline='V9.10 joint-conservative nutrient & biological soil-C assumptions',
    no_crop_annual_bn=base['annual_cost_bn'],central_crop_annual_bn=central['annual_cost_bn'],
    central_crop_selected_mt=central['crop_htl_mt'],crop_saving_bn=base['annual_cost_bn']-central['annual_cost_bn'],
    process_inventory_substituted_central_mt=lca['replaced_route_screen_mt'],
    unmatched_no_crop_emissions_mt=n_lca['replaced_route_screen_mt'],
    crop_emissions_delta_mt=lca['replaced_route_screen_mt']-n_lca['replaced_route_screen_mt'],
    independent_margin_warning='One-factor and two-factor tests of analyst assumptions, not DOE or USDA observed county-specific supplies',
    resource_delivery_grid_count=len(rows),land_stress_count=len(land),field_counterfactual_count=len(emissions),
    source_requirements=['DOE ORNL all-county all-price resource files', 'regional collection, transport and storage data',
      'HTL nutrient partition and bioavailability experiments', 'cropland seasonal cover-area and SOC accumulation records'],
    grid=rows,land=land,field_lca=emissions)
 (R/'US911_Robustness_Results.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
 print('V9.11 STRESS SUMMARY',json.dumps({k:summary[k] for k in ('central_crop_annual_bn','no_crop_annual_bn','crop_saving_bn','resource_delivery_grid_count','land_stress_count')},indent=2))
 return summary

def write_rows(fn,rows):
 with (R/fn).open('w',newline='',encoding='utf-8') as f:
  writer=csv.DictWriter(f,list(rows[0]));writer.writeheader();writer.writerows(rows)

if __name__=='__main__':run()
