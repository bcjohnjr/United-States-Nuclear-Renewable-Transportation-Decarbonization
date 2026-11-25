#!/usr/bin/env python3
"""V9.9 feasibility, plant-available nutrient and explicit crop-LCA accounting.

The LCA replacement screen removes the crop portion of the legacy *generic*
10 g/MJ residue fuel term before adding individual agricultural processes; it
retains explicit transport/fuel hydrogen and electricity components in the
existing system ledger. Residue collection/transport, biogenic carbon and
counterfactual field emissions remain only bounded. No claim of certified LCA.
"""
from __future__ import annotations
import copy,csv,json,argparse,math
from pathlib import Path
import us97_circular_feedstocks as C
import us97_integrated as J
import us98_agri_lca as L
import us97_aeo_boundary as B
import us95_aeo_reference_bridge as A
import us2_model as M
from us99_bt23_supply import ingest,adapt_params,export_files
R=Path(__file__).resolve().parent
USD2026='model base-dollar year; see AEO bridge price-year adjustments'
# The three factors are *not* experimental and are explicitly independent.
DEFAULT_CHAIN={e:dict(process_recovery={'n':0.25,'p':0.375,'k':0.40}[e],
 treatment_storage_retention={'n':0.80,'p':0.85,'k':0.90}[e],
 plant_available_field_fraction={'n':0.70,'p':0.55,'k':0.85}[e]) for e in 'npk'}
def plant_available(p,chain=DEFAULT_CHAIN):
 p=copy.deepcopy(p);cr=p['CROP_RESIDUE']
 for i,f in enumerate(cr['feedstocks']):
  nr={e:math.prod(chain[e].values()) for e in 'npk'}
  f['recovered_fraction']=nr
  _,cap,orig=p['BIOMASS']['tiers'][i]
  # Remove original nutrient charge by using f['delivered_usd_t'] when preserved;
  # here old tiers also contain wastewater and hydrochar logistics.
  fixed=(f['delivered_usd_t']+cr['wastewater_treatment_usd_t']+cr['hydrochar_testing_transport_usd_t'])
  fert=sum(f['elemental_kg_t'][e]*(1-nr[e])*cr['nutrient_replacement_usd_per_kg'][e] for e in 'npk')
  p['BIOMASS']['tiers'][i]=(f['name'],cap,fixed+fert)
 return p

def carbon_land(p,available_hectares=20e6,annual_additional_tC_ha=.5):
 if available_hectares<0 or annual_additional_tC_ha<0:raise ValueError('negative cover crop area/rate')
 p=copy.deepcopy(p);p['CROP_RESIDUE']['cover_crop_max_stable_c_mt']=available_hectares*annual_additional_tC_ha/1e6
 return p

def integrated_lca(case,assumed_crop_ci_g_mj=None,collection_tco2_t=.020,field_counterfactual_mt=None):
 """Audited partial agricultural emissions substitution in Mt CO2e/year.

 The published transport model uses CI_RESIDUES_GRASSES_G_MJ on the combined
 terrestrial residues/grass liquid-energy route. Only the crop portion of that
 route is replaced; process H2, electricity and noncrop liquid emissions stay.
 Sampling a hypothetical route factor requires adjusting the inherited total
 *before* removing the same factor. Otherwise a random subtraction alone
 spuriously changes lifecycle emissions even with identical process activity.
 This is a conditional boundary test, not a certified agricultural LCA.
 """
 from us2_model import CI_RESIDUES_GRASSES_G_MJ as base_ci
 crop_energy_twh=float(case.get('crop_htl_liquid_twh',0))
 pool=case.get('mixed_residue_liquid_twh')
 if crop_energy_twh < -1e-9 or (pool is not None and crop_energy_twh>float(pool)+1e-6):
  raise ValueError('Crop fuel output exceeds mixed terrestrial-route energy budget')
 scenario_ci=base_ci if assumed_crop_ci_g_mj is None else float(assumed_crop_ci_g_mj)
 if not 0<=scenario_ci<=200:raise ValueError('invalid generic mixed-route coefficient')
 # 1 TWh * 1 g/MJ = 0.0036 Mt CO2e (3600 TJ per TWh).
 factor_mt_per_g_mj=crop_energy_twh*.0036
 legacy=float(case['emissions_wtw_mt'])
 scenario_legacy=legacy + factor_mt_per_g_mj*(scenario_ci-base_ci)
 generic_mt=factor_mt_per_g_mj*scenario_ci
 ledger=L.ledger(case)
 collection_mt=float(case['crop_htl_mt'])*collection_tco2_t
 gross=ledger['gross_candidate_addon_mt']+collection_mt
 substituted=scenario_legacy-generic_mt+gross
 if field_counterfactual_mt is not None:substituted-=float(field_counterfactual_mt)
 return dict(case=case['case'],legacy_mt=legacy,
  route_ci_model_g_mj=base_ci,route_ci_scenario_g_mj=scenario_ci,
  scenario_adjusted_legacy_mt=scenario_legacy,
  crop_liquid_twh=crop_energy_twh,mixed_route_liquid_twh=pool,
  generic_crop_ci_replaced_mt=generic_mt,
  process_inventory_mt=gross,field_counterfactual_mt=field_counterfactual_mt,
  replaced_route_screen_mt=substituted,
  maximal_gross_addition_screen_mt=legacy+gross,
  crop_mt=case['crop_htl_mt'],effective_npk_imports_kt={e:case[e+'_imports_kt'] for e in 'npk'},
  source='The 10 g/MJ generic mixed terrestrial route is adjusted consistently then substituted only for crop liquid energy; process H2, electricity and noncrop terms retained.',
  qualifier='Conditional partial agricultural LCA, not an independently calibrated cradle-to-grave national inventory; source-field emissions and chemistry unknown')

def analyse(bt23_files=None,include_fixed=False):
 boundary=json.loads((R/'US97_AEO_Boundary.json').read_text());premium=boundary['results'][1]['net_bev_differential_usd_yr']
 _,aeo=A.read_source()
 # Conservatively exclude all novel soil C credit. The restoration ceiling is
 # hard LP bound on annual stable C; no automatic purchased limitless service.
 opts={'release_fraction':.5,'apply_pyro_to_soil':False,'allow_stable_hydrochar':False}
 p=C.build_params(aeo,bevpremium=premium,**opts)
 p=carbon_land(plant_available(p),20e6,.5)
 original=C.one('V9.9 chemistry- and land-limited analyst crop screen',p)
 cases=[original];regional=None
 if bt23_files:
  report=ingest(bt23_files)
  export_files(report,R/'BT23_VALIDATED')
  pbt=adapt_params(p,report,logistics_usd_metric_t=25,storage_usd_metric_t=10,plant_field_fraction=1.0)
  pbt=plant_available(pbt)
  try:regional=C.one('BT23 state/price marginal supply in national LP',pbt);cases.append(regional)
  except Exception as e:raise RuntimeError('BT23-derived national model infeasible: do not silently use assumed 166 Mt caps') from e
  (R/'US99_BT23_MODEL_INPUTS.json').write_text(json.dumps(pbt['bt23_assumption_metadata'],indent=2))
 # Same constraints, no crop candidate; no separate processing/crop add on
 no=C.build_params(aeo,bevpremium=premium,**opts,cap_mt=0)
 no=carbon_land(plant_available(no),20e6,.5)
 none=C.one('V9.9 matched no-crop alternative',no)
 cases.append(none)
 lca=[integrated_lca(c) for c in cases]
 results=dict(version='9.9',regional_data_present=regional is not None,scenarios=cases,
   lca_accounting=lca,reference_partial_mt=json.loads((R/'US97_Integrated_Circular_EIA.json').read_text())['source_weighted_reference_emissions_partial_mt'],
   nutrient_availability_chain=DEFAULT_CHAIN,cover_crop_land_constraint=dict(available_ha=20e6,accumulation_tC_ha_yr=.5,max_stable_c_mt=10.0),
   limitations=['BT23 county supply only when an official authenticated export is supplied; otherwise full 166-Mt analyst ceiling is NOT a calibrated capacity',
     'Plant-availability and treatment fractions are independent analyst assumptions, not experimental HTL data',
     'Generic 10 g/MJ agricultural route is SUBSTITUTED with gross explicit process inventory as a range, not added twice',
     'No explicit hourly energy network feasibility or farm-grade regional siting verified'])
 (R/'US99_Scenario_Analysis.json').write_text(json.dumps(results,indent=2))
 with (R/'us99_crop_soil_lca.csv').open('w',newline='') as f:
  keys=['case','annual_cost_bn','emissions_legacy_mt','crop_htl_mt','n_imports_kt','p_imports_kt','k_imports_kt','cover_crop_c_mt','lca_replacement_mt','lca_max_addition_mt']
  w=csv.DictWriter(f,keys);w.writeheader()
  for c,l in zip(cases,lca):
   w.writerow(dict(case=c['case'],annual_cost_bn=c['annual_cost_bn'],emissions_legacy_mt=c['emissions_wtw_mt'],crop_htl_mt=c['crop_htl_mt'],
    **{f'{e}_imports_kt':c[f'{e}_imports_kt'] for e in 'npk'},cover_crop_c_mt=c['cover_crop_stable_c_mt'],
    lca_replacement_mt=l['replaced_route_screen_mt'],lca_max_addition_mt=l['maximal_gross_addition_screen_mt']))
 if include_fixed:
  rows=[]
  for hubs in (0,30,60,100,150,166,250):
   r=M.solve_learning(p,scenario='least_cost',blend_vol=0,fixed_hubs=hubs)
   rows.append(dict(hubs=hubs,annual_cost_bn=r['transport_cost_bn'],crop_mt=r.get('crop_residue_soil',{}).get('feedstock_mt',0),
     cover_c_mt=r.get('crop_residue_soil',{}).get('cover_crop_extra_stable_c_mt',0)))
   print('HUB',hubs,round(rows[-1]['annual_cost_bn'],3),flush=True)
  with (R/'us99_joint_conservative_reactors.csv').open('w',newline='') as f:
   w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
  results['fixed_hub_cases']=rows;(R/'US99_Scenario_Analysis.json').write_text(json.dumps(results,indent=2))
 return results
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--bt23',nargs='*');ap.add_argument('--fixed-hubs',action='store_true');a=ap.parse_args()
 d=analyse(a.bt23,include_fixed=a.fixed_hubs)
 for q in d['scenarios']:print('RESULT',q['case'],round(q['annual_cost_bn'],3),'crop',round(q['crop_htl_mt'],3),'N',round(q['n_imports_kt'],1),flush=True)
