#!/usr/bin/env python3
"""V9.8 explicit *incremental candidate* agricultural lifecycle inventory.

IMPORTANT: out['emissions']['total_mt'] already has stylized liquid-fuel lifecycle
factors. No overlap audit of those published coefficients is available. These
new categories are therefore reported as a GROSS ADD-ON SCREEN only; the lower
bound for incremental emissions is zero when fully included already, and the
upper bound is the gross total. Do not call the sum a measured LCA.
Assumptions [A] are named and independently variable, not field/lab measurements.
"""
import csv,json,math
from pathlib import Path
R=Path(__file__).resolve().parent
ASSUMPTIONS={
 'fertilizer_prod_kgco2_per_kg_element':{'n':4.0,'p':2.0,'k':0.8},
 'soil_n2o_n_fraction_of_applied_n':0.01,
 'n2o_100yr_gwp':273,
 'htl_wastewater_treatment_tco2e_per_t_dry':0.035,
 'hydrochar_transport_application_tco2e_per_t_char':0.020,
 'methane_carbon_transport_tco2e_per_t_soil_carbon':0.015,
 'cover_crop_establishment_tco2e_per_t_stable_c':0.05,
 'direct_crop_land_use_change_mtco2e_yr':'NOT QUANTIFIED',
 'field_soil_stock_trend_mtco2e_yr':'NOT QUANTIFIED',
 'overlap_with_existing_liquid_fuel_ci':'UNKNOWN: gross components could partially reside in generic lifecycle coeffs',
}
def ledger(case, ef=0.01, treatment=0.035, fertilizer_scale=1):
  c=case; ifc=lambda e:float(c.get(e+'_imports_kt',0))
  recovered_N=float(c.get('n_water_kt',0))+float(c.get('n_char_kt',0))
  fertilizer=sum(ifc(e)*ASSUMPTIONS['fertilizer_prod_kgco2_per_kg_element'][e]/1000 for e in 'npk')*fertilizer_scale
  applied_n=ifc('n')+recovered_N
  n2o=applied_n*ef*(44/28)*ASSUMPTIONS['n2o_100yr_gwp']/1000
  water=float(c['crop_htl_mt'])*treatment
  hydro=float(c['crop_hydrochar_mt'])*ASSUMPTIONS['hydrochar_transport_application_tco2e_per_t_char']
  pyro=float(c['stable_pyrolysis_c_mt'])*ASSUMPTIONS['methane_carbon_transport_tco2e_per_t_soil_carbon']
  cover=float(c['cover_crop_stable_c_mt'])*ASSUMPTIONS['cover_crop_establishment_tco2e_per_t_stable_c']
  lines={'fertilizer_manufacture_mt':fertilizer,'soil_n2o_sensitivity_mt':n2o,'aqueous_treatment_mt':water,'hydrochar_transport_application_mt':hydro,'pyrocarbon_delivery_mt':pyro,'cover_crop_establishment_mt':cover}
  return dict(case=c['case'],gross_candidate_addon_mt=sum(lines.values()),lines=lines,assumptions={'n2o_n_fraction':ef,'treatment_tco2e_per_t_feedstock':treatment,'fertilizer_prod_scale':fertilizer_scale},
   legacy_model_emissions_mt=c['emissions_wtw_mt'],
   **{'upper_screen_emissions_if_all_additional_mt':c['emissions_wtw_mt']+sum(lines.values())},
   unquantified=['feedstock-specific upstream cultivation/indirect land use','long-run soil carbon stock changes','fertilizer production and HTL coefficient overlap','methane-carbon soil biological performance','marine salt removal for ocean scenario'])
def main():
 data=json.loads((R/'US97_Integrated_Circular_EIA.json').read_text());sc=data['scenario'];case=sc['soil_costed_economic_crop'];no=sc['soil_costed_no_crop'];
 base=ledger(case)
 tests=[ledger(case,ef=a,treatment=b,fertilizer_scale=c) for a,b,c in [(.005,.02,.7),(.01,.035,1.0),(.02,.07,1.3)]]
 for k in ['crop_no_pyro_soil_credit','crop_low_nutrient_recovery','crop_no_stable_hydrochar']:
  tests.append(ledger(sc[k]))
 out={'version':'9.8','central':base,'cases':tests,'assumptions':ASSUMPTIONS,
    'interpretation':'Gross candidate agriculture-related emissions that require a route-level factor overlap audit before adding them to national WTW totals. The paired range [legacy, legacy+gross] is NOT a probabilistic CI.',
    'reference_hydrogen_energy_basis':'EIA generally reports gross heat content; HHV mass conversion shown with LHV check in US97_AEO_Boundary.json',
    'citation_reading':['https://pubs.rsc.org/en/content/articlehtml/2026/ew/d5ew00569h','https://www.eia.gov/totalenergy/conversion/factors/']}
 (R/'US98_Agriculture_Explicit_LCA.json').write_text(json.dumps(out,indent=2));
 with (R/'us98_agri_lca_sensitivity.csv').open('w',newline='') as f:
  keys=['case','n2o_n_fraction','treatment_tco2e_per_t_feedstock','fertilizer_prod_scale','legacy_model_emissions_mt','gross_candidate_addon_mt','upper_screen_emissions_if_all_additional_mt'];w=csv.DictWriter(f,keys);w.writeheader();
  for t in tests:w.writerow({k:t['assumptions'].get(k,t.get(k)) for k in keys})
 print('AGRILCA base gross candidates Mt:',round(base['gross_candidate_addon_mt'],3),'legacy',base['legacy_model_emissions_mt'],'upper',round(base['upper_screen_emissions_if_all_additional_mt'],3));return out
if __name__=='__main__':main()
