#!/usr/bin/env python3
"""V9.7 conditional PAIRWISE 2050 cost/LCA screens (common annual BEV premium).
All ranges analyst-created [A]; not predictive probabilities. Crop/soil
conservation enabled on EVERY sampled alternative, including fertilizer imports.
"""
import random,csv,json,math,sys
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
import us97_circular_feedstocks as C
import us97_aeo_boundary as E
import us95_aeo_reference_bridge as B
import us2_model as M
ROOT=Path(__file__).resolve().parent

def run(n=500,seed=971):
 rng=random.Random(seed);_,a=B.read_source();s=json.loads((ROOT/'US97_AEO_Boundary.json').read_text())['results'][1]
 data=[]
 for j in range(n):
  bev_shift=rng.uniform(-200,300)
  bev=s['net_bev_differential_usd_yr']+bev_shift
  oil=rng.uniform(.70,1.40)
  power=rng.uniform(.78,1.38)
  reactor=rng.uniform(.80,1.55)
  crop_cost=rng.uniform(.80,1.40)
  crop_avail=rng.uniform(.5,1.)
  recover=rng.uniform(.35,1.)
  pyro_soil=rng.random()>.35
  fossil_share=rng.uniform(.55,.85)
  ref_scope=rng.uniform(0,36)
  ref_h2_ci=rng.uniform(0,15)
  grid_g=rng.uniform(10,100)
  upstream=rng.uniform(5,15)
  p=C.build_params(a,bevpremium=bev,cap_mt=166*crop_avail,release_fraction=recover,apply_pyro_to_soil=pyro_soil)
  for k in ('onshore_wind','solar','lwr_smr'):p['ELEC'][k]*=power
  p['capex_mult']=reactor
  for i,(name,cap,cost) in enumerate(p['BIOMASS']['tiers']):p['BIOMASS']['tiers'][i]=(name,cap,cost*crop_cost if i<len(C.CANDIDATES) else cost)
  r=M.solve_learning(p,scenario='least_cost',blend_vol=0)
  ref_energy=a['eia_energy_exp_2050_bn_2025_usd']*1.025*(fossil_share*oil+(1-fossil_share)*power)
  prices=E.V.vehicle_prices(); life=15
  other=(a['eia_ldv_phev_m']*((prices['phev']-prices['ice'])*1000/life-250*.35)+
         a['eia_ldv_hev_m']*((prices['hev']-prices['ice'])*1000/life-250*.35))/1000*1.025
  base_truck=(a['eia_medheavy_electric_m']*p['VEH']['bev_truck_net_usd_yr']+a['eia_medheavy_fcev_m']*p['VEH']['fcev_truck_net_usd_yr'])/1000
  # Oil price applied to the fossil component of the same reference energy pool;
  # BEV purchase differential is common to the two fleets.
  ref=ref_energy-E.V.excise_tax_screen()['illustrative_tax_bn']*.5+a['ldv_2050_bev_m']*bev/1000+other+base_truck+a['ldv_2050_bev_m']*.100+ref_scope
  ref_emo=E.emission_inventory(upstream,grid_g,ref_h2_ci)['screening_wtw_mt']
  delta=r['transport_cost_bn']-ref
  avoid=ref_emo-r['emissions']['total_mt']
  row=dict(draw=j,reference_bn=ref,alternative_bn=r['transport_cost_bn'],incremental_bn=delta,
   avoided_mt=avoid,abatement_usd_t=1000*delta/avoid,
   crop_collected_mt=r.get('crop_residue_soil',{}).get('feedstock_mt',0),
   bev_premium_usd_yr=bev,oil_mult=oil,power_mult=power,reactor_mult=reactor,
   crop_collection_mult=crop_cost,crop_national_cap_mt=166*crop_avail,
   npk_recovery_scale=recover,pyro_soil_credit_enabled=int(pyro_soil),
   fossil_reference_share_assumed=fossil_share,reference_scope_add_bn=ref_scope,
   reference_h2_kgco2_kg=ref_h2_ci,grid_lifecycle_g_kwh=grid_g,upstream_g_mj=upstream)
  data.append(row)
  if (j+1)%100==0:print('Completed',j+1,'/',n,flush=True)
 keys=list(data[0])
 with (ROOT/'us97_paired_uncertainty.csv').open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,keys);w.writeheader();w.writerows(data)
 v=lambda k:np.array([r[k] for r in data])
 correlations={k:round(float(spearmanr(v(k),v('abatement_usd_t')).statistic),3) for k in ['bev_premium_usd_yr','oil_mult','power_mult','reactor_mult','crop_collection_mult','npk_recovery_scale','reference_h2_kgco2_kg']}
 summary=dict(n=n,seed=seed,abt_usd_t_p05=float(np.percentile(v('abatement_usd_t'),5)),abt_usd_t_median=float(np.median(v('abatement_usd_t'))),
  abt_usd_t_p95=float(np.percentile(v('abatement_usd_t'),95)),
  fraction_alt_cheaper_in_assumption_draws=float(np.mean(v('incremental_bn')<0)),
  crop_selected_mt_median=float(np.median(v('crop_collected_mt'))),
  parameter_spearman_against_abatement=correlations,
  warning='Conditional Monte Carlo with assumed ranges, NOT calibrated chances or a full harmonized TCO/LCA. Do not interpret fraction as predictive probability.')
 (ROOT/'US97_Paired_Uncertainty_Summary.json').write_text(json.dumps(summary,indent=2))
 print(json.dumps(summary,indent=2))
 return summary
if __name__=='__main__':run(int(sys.argv[1]) if len(sys.argv)>1 else 500)
