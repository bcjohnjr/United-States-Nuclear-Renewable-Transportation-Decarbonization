#!/usr/bin/env python3
"""V9.6 AEO2026 2050 shared-assumption comparison. Screening, NOT certified full TCO/LCA.

Sources: archived EIA AEO2026 Table 3, 36, 39, 49, 52, 70 in V9.5.
Explicit [A] choices: 4-class sample weights, vehicle lifetimes, non-capital
maintenance premium, 2025-to-2026 price factor, charging/coverage adjustments,
excise-tax matching, upstream and grid lifecycle factors. `vehicle_cost` is a
DIFFERENTIAL relative to the same conventional vehicle, not full ownership TCO.
"""
import csv, io, json, pathlib, zipfile, copy
from statistics import mean
import us2_model as M
import us95_aeo_reference_bridge as B
import us2_inputs as I
HERE=pathlib.Path(__file__).resolve().parent
CLASSES={'Compact Cars':0.25,'Midsize Cars':0.25,'Small Crossover Cars':0.30,'Large Pickup':0.20}
TECH={'ice':'Gasoline','bev200':'200-Mile Electric Vehicle 4/','bev300':'300-Mile Electric Vehicle 5/','hev':'Gasoline-Electric Hybrid','phev':'Plug-in 50 Gasoline Hybrid 2/'}

def table36():
 with zipfile.ZipFile(HERE/'AEO2026_2050_TRANSPORT_DATA.zip') as z:
  paths=[p for p in z.namelist() if p.startswith('csv_all_sheets/CounterfactualBaseline/Table_36/') and p.endswith('.csv')]
  assert len(paths)==1,paths
  return {int(r['excel_row']):r for r in csv.DictReader(io.StringIO(z.read(paths[0]).decode('utf-8-sig')))}

def vehicle_prices():
 rows=list(csv.DictReader(open(HERE/'aeo2026_2050_new_vehicle_prices.csv',encoding='utf-8-sig')))
 values={(r['technology'],r['vehicle_class']):float(r['new_price_thousand_2025_usd_2050']) for r in rows}
 result={}
 for k,t in TECH.items():
  part={c:values[(t,c)] for c in CLASSES}
  assert all(x>0 for x in part.values()),(k,part)
  result[k]=sum(part[c]*CLASSES[c] for c in CLASSES)
 return result

def excise_tax_screen():
 # On-road classes only; no rail/marine/offroad taxes. All numbers use source
 # Table 36 trillion Btu (AB:2050) and *assumed* 2025-style $/gallon taxes.
 rows=table36()
 petrol=[13,22,31,67,83]
 diesel=[15,24,32,69,77,85]
 gas_tbtu=sum(float(rows[n]['AB']) for n in petrol)
 diesel_tbtu=sum(float(rows[n]['AB']) for n in diesel)
 gas_bgal=gas_tbtu*1e12/I.GAL_GASOLINE_BTU/1e9
 diesel_bgal=diesel_tbtu*1e12/I.GAL_DIESEL_BTU/1e9
 return dict(gasoline_2050_bgal=gas_bgal,diesel_onroad_2050_bgal=diesel_bgal,
             illustrative_tax_bn=gas_bgal*I.TAX['gasoline']+diesel_bgal*I.TAX['diesel'],
             tax_rate_usd_per_gal={'gasoline':I.TAX['gasoline'],'diesel':I.TAX['diesel']},
             table36_source_rows={'gasoline':petrol,'diesel_onroad':diesel})

def run():
 provenance,a=B.read_source()
 prices=vehicle_prices(); tax=excise_tax_screen()
 assert provenance['sha256_all_passed']
 # Class mixes are assumed, not EIA stock-share-derived. Price year factor is assumed.
 opts=[
  dict(case='low_cost_200mi_BEVi',bev_share_300=0.0,life_years=18,maintenance_saving_usd_yr=350,
       price_factor=1.0,tax_deduction_fraction=0,extra_reference_charging_usd_per_bev_yr=200,
       reference_coverage_add_bn=34,upstream_g_mj=5,power_g_kwh=10),
  dict(case='central_80pct_300mi',bev_share_300=0.8,life_years=15,maintenance_saving_usd_yr=250,
       price_factor=1.025,tax_deduction_fraction=0.5,extra_reference_charging_usd_per_bev_yr=100,
       reference_coverage_add_bn=16,upstream_g_mj=10,power_g_kwh=50),
  dict(case='high_cost_300mi_BEVi',bev_share_300=1.0,life_years=12,maintenance_saving_usd_yr=100,
       price_factor=1.05,tax_deduction_fraction=1.0,extra_reference_charging_usd_per_bev_yr=0,
       reference_coverage_add_bn=0,upstream_g_mj=15,power_g_kwh=100)
 ]
 outcomes=[]
 for d in opts:
  share=d['bev_share_300']
  price_bev=share*prices['bev300']+(1-share)*prices['bev200']
  bev_delta_capex_usd_yr=(price_bev-prices['ice'])*1000/d['life_years']
  bev_net=bev_delta_capex_usd_yr-d['maintenance_saving_usd_yr']
  # Keep the same BEV net ownership assumption on reference and alternative.
  p,_=B.config(a)
  p['VEH']['ldv_bev_net_usd_yr']=bev_net*d['price_factor']
  res=M.solve_learning(p,scenario='least_cost',blend_vol=0)
  # The EIA reference stock mix is sourced from Table 39; the class weights are not.
  other_reference=(a['eia_ldv_phev_m']*((prices['phev']-prices['ice'])*1000/d['life_years']-d['maintenance_saving_usd_yr']*.35)
                   +a['eia_ldv_hev_m']*((prices['hev']-prices['ice'])*1000/d['life_years']-d['maintenance_saving_usd_yr']*.35))/1000
  reference_ldv=a['ldv_2050_bev_m']*bev_net*d['price_factor']/1000+other_reference*d['price_factor']
  # No EIA source for truck prices: reuse explicit source model annual truck technology premiums.
  ref_truck=(a['eia_medheavy_electric_m']*p['VEH']['bev_truck_net_usd_yr']+a['eia_medheavy_fcev_m']*p['VEH']['fcev_truck_net_usd_yr'])/1000
  energy_exp=a['eia_energy_exp_2050_bn_2025_usd']*d['price_factor']
  tax_transfer=tax['illustrative_tax_bn']*d['tax_deduction_fraction']
  ref_charge=a['ldv_2050_bev_m']*d['extra_reference_charging_usd_per_bev_yr']/1000
  reference=energy_exp-tax_transfer+reference_ldv+ref_truck+ref_charge+d['reference_coverage_add_bn']
  # The alternative includes some off-road services outside the EIA energy expenditure.
  # 'coverage add' is an explicitly assumed alternative service-cost catch-up.
  alt=res['transport_cost_bn']
  gas_tbtu=a['eia2050_fossil_trillion_btu_table36_screen']; elec_tbtu=a['eia2050_reported_electricity_trillion_btu_table36_sum']
  reference_wtw=a['eia_transport_direct_co2_2050_mt']+gas_tbtu*d['upstream_g_mj']*.00105505585+elec_tbtu*.29307107*d['power_g_kwh']*.001
  avoided=reference_wtw-res['emissions']['total_mt']
  net=alt-reference
  outcomes.append(dict(case=d['case'],eia_energy_2025usd_bn=a['eia_energy_exp_2050_bn_2025_usd'],
    price_factor_assumed=d['price_factor'],reference_energy_2026usd_bn=energy_exp,tax_screen_bn=tax['illustrative_tax_bn'],
    fraction_tax_removed=d['tax_deduction_fraction'],tax_removed_bn=tax_transfer,
    mean_ice_price_2025usd_thousand=prices['ice'],mean_bev_new_price_2025usd_thousand=price_bev,
    bev_cost_net_usd_yr_2026usd=p['VEH']['ldv_bev_net_usd_yr'],
    reference_ldv_net_premium_bn=reference_ldv,reference_truck_net_premium_bn=ref_truck,
    reference_charging_bn=ref_charge,reference_coverage_add_bn=d['reference_coverage_add_bn'],
    reference_screen_bn=reference,alt_screen_bn=alt,incremental_alt_minus_reference_bn=net,
    reference_partial_wtw_mt=reference_wtw,alt_model_wtw_mt=res['emissions']['total_mt'],
    avoided_mt=avoided,cost_per_tonne_avoided_usd=net*1000/avoided,
    hubs_iterative=res['hubs'],alternative_truck_stock_m=sum(p['VEH'][k] for k in ['ers_trucks_m','bev_trucks_m','fcev_trucks_m','re_trucks_m']),
    assumption_status='ILLUSTRATIVE: EIA powertrain price samples + analyst class shares, lifetime, maintenance, tax, scope, LCA; NOT matched full TCO/LCA'))
 out=dict(version='9.6',status='conditional shared-parameter 2050 screening, NOT fully matched TCO/LCA',
  sources=['AEO2026 Counterfactual Baseline original XLSX Tables 3,36,39,49,52,70, all 38 archived workbooks verified'],
  technology_names=TECH,class_weights_assumed=CLASSES,vehicle_prices_2025usd_thousands=prices,
  tax_screen=tax,reference_2050_stock=dict(ldv=a['ldv_2050_stock_m'],bev=a['ldv_2050_bev_m'],phev=a['eia_ldv_phev_m'],hev=a['eia_ldv_hev_m'],medheavy=a['freight_medium_heavy_m']),
  results=outcomes,limitations=[
  'AEO Table 3 expenditure covers a different mode and tax boundary; offroad scope and charging are assumed.',
  'Selected four vehicle classes and weights are NOT a national 2050 sales-weighted fleet price; Table52 new prices are not lifetime cash flows.',
  'Alternative model already includes net powertrain premia; they are rebased using the identical BEV price formula to the AEO reference.',
  'Reference net hybrid and fuel cell premiums and maintenance are only partial ownership differences.',
  'AEO direct transport CO2 + assumed upstream and electricity increments is not a full ISO LCA and not harmonized to alternative embodied vehicle/site emissions.',
  'EIA 2050 aviation service differs between energy and seat-mile growth, and all three cases use the jet-energy proxy.',
  'The model does not include hourly system feasibility, certified biomass soil safeguards, or a feasible nuclear construction programme.',
  'The reference cost ranges are ANALYST CONDITIONAL sensitivities, NOT official EIA 2050 full-cost estimates or probabilities.'
 ])
 (HERE/'US96_Shared_2050_Screen.json').write_text(json.dumps(out,indent=2))
 keys=outcomes[0].keys()
 with (HERE/'us96_shared_2050_scenarios.csv').open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,keys);w.writeheader();w.writerows(outcomes)
 for r in outcomes:print(r['case'],'ref',round(r['reference_screen_bn'],2),'alt',round(r['alt_screen_bn'],2),'delta',round(r['incremental_alt_minus_reference_bn'],2),'avoided',round(r['avoided_mt'],2),'usd/t',round(r['cost_per_tonne_avoided_usd'],2),'bev$/yr',round(r['bev_cost_net_usd_yr_2026usd'],1))
 return out
if __name__=='__main__':run()
