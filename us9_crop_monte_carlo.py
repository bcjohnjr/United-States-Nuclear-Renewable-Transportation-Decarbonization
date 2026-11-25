"""Paired experimental sensitivity of crop-HTL availability, N/P/K capture and soil C.

ALL distributions are elicitation assumptions for SCREENING, not statistical confidence
intervals or forecasts. Each draw solves matched no-crop and crop LP scenarios with
identical other system conditions, avoiding false savings from changing the comparator.
"""
from pathlib import Path
import csv,json,sys
import numpy as np
import us2_model as M
import us9_crop_residue as C
ROOT=Path(__file__).resolve().parent

def main(n=1000,seed=85):
 rng=np.random.default_rng(seed);out=[]
 for i in range(n):
  p=M.default_params();d=p['CROP_RESIDUE']
  supply=float(rng.triangular(80,145,166))
  deliver=float(rng.triangular(45,60,125))
  d['wastewater_treatment_usd_t']=float(rng.triangular(10,20,60))
  d['hydrochar_testing_transport_usd_t']=float(rng.triangular(8,15,35))
  d['stable_soc_c_t_per_dry_t']=float(rng.triangular(.04,.06,.12))
  d['hydrochar_stable_fraction']=float(rng.triangular(.2,.5,.8))
  d['cover_crop_stable_carbon_cost_usd_t_c']=float(rng.triangular(150,250,600))
  d['pyro_carbon_soil_application_usd_t']=float(rng.triangular(30,60,120))
  for k,limits in {'n':(.2,.5,.8),'p':(.3,.7,.9),'k':(.3,.75,.95)}.items():
   d['recovered_fraction'][k]=float(rng.triangular(*limits))
  p['ROUTES']['htl']['char_t_t']=float(rng.triangular(.07,.12,.17))
  p['ROUTES']['htl']['mwh_t']=float(rng.triangular(1.7,2.5,3.1))
  # Same forestry and grass pool, same conversion assumptions, same transport service.
  no=M.solve_learning(C.with_crop(p,supply_mt=0.0),scenario='least_cost',blend_vol=0.0)
  yes=M.solve_learning(C.with_crop(p,supply_mt=supply,crop_base_usd_t=deliver),scenario='least_cost',blend_vol=0.0)
  o=yes.get('crop_residue_soil',{});crop=o.get('feedstock_mt',0)
  out.append(dict(draw=i,available_mt=supply,delivered_usd_t=deliver,htl_mwh_t=p['ROUTES']['htl']['mwh_t'],
    char_yield_t_t=p['ROUTES']['htl']['char_t_t'],soil_soc_target_t_c_per_t=d['stable_soc_c_t_per_dry_t'],
    n_recovery=d['recovered_fraction']['n'],p_recovery=d['recovered_fraction']['p'],k_recovery=d['recovered_fraction']['k'],
    no_crop_cost_bn=no['transport_cost_bn'],with_crop_cost_bn=yes['transport_cost_bn'],
    annual_saving_bn=no['transport_cost_bn']-yes['transport_cost_bn'],crop_used_mt=crop,
    kcl_import_kt=o.get('nutrients',{}).get('k',{}).get('imported_kt',0)/.5245,
    objective_residual_bn=yes['objective_reconciliation']['residual_bn']))
 if out:
  with (ROOT/'us9_crop_monte_carlo.csv').open('w',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
  saving=np.array([v['annual_saving_bn'] for v in out]);used=np.array([v['crop_used_mt'] for v in out])
  j=dict(draws=len(out),paired_savings_bn_p5_p50_p95=[float(x) for x in np.percentile(saving,[5,50,95])],
       share_crop_cost_reducing=float(np.mean(saving>1e-7)),crop_used_mt_p5_p50_p95=[float(x) for x in np.percentile(used,[5,50,95])],
       assumption='Triangular independent parameter draws, NOT predictive probabilities; excludes geographic logistics and soil validation')
  (ROOT/'us9_crop_mc_summary.json').write_text(json.dumps(j,indent=2))
  print(json.dumps(j,indent=2))
 return out
if __name__=='__main__':main(int(sys.argv[1]) if len(sys.argv)>1 else 1000)
