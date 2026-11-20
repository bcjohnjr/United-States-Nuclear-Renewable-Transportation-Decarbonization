"""V7 regression, boundary and monotonicity checks."""
import json
from pathlib import Path
from dataclasses import replace
from us7_community_screen import CommunityInputs,evaluate,methane_sensitivity
from us6_nutrient_balance import scenario_result
R=Path(__file__).resolve().parent

def run():
  s=json.loads((R/'scenarios.json').read_text())
  z=scenario_result(s['least_cost'])
  r=evaluate(s['least_cost'],z)
  assert abs(z['nitrogen']['mass_balance_residual_target_kt'])<1e-9
  assert abs(z['phosphorus']['mass_balance_residual_target_kt'])<1e-9
  f=s['least_cost']['food']
  assert f['greenhouse_seafood_gross_calorie_equiv_m']<4
  assert f['hemp_meal_potential_calorie_equiv_m']>10
  assert f['greenhouse_seafood_edible_calorie_equiv_m']<f['greenhouse_seafood_gross_calorie_equiv_m']
  assert abs(r['transport_cost_bn_unchanged']-s['least_cost']['transport_cost_bn'])<1e-8
  assert r['annual_community_cost_bn']>0 and r['total_treatment_energy_gwh']>0
  assert r['community_operating_margin_before_unmodelled_items_bn']!=r['transport_cost_bn_unchanged']
  assert methane_sensitivity(z,1,1,.5,False)['conditional_methane_avoided_mtco2e']<methane_sensitivity(z,1,1,1,False)['conditional_methane_avoided_mtco2e']
  lo=evaluate(s['least_cost'],z,replace(CommunityInputs(),process_water_m3_per_t_seafood=4))
  hi=evaluate(s['least_cost'],z,replace(CommunityInputs(),process_water_m3_per_t_seafood=25))
  assert lo['total_treatment_energy_gwh']<r['total_treatment_energy_gwh']<hi['total_treatment_energy_gwh']
  saved=json.loads((R/'community_screen_v7.json').read_text())
  assert abs(saved['annual_community_cost_bn']-r['annual_community_cost_bn'])<1e-9
  assert saved['transport_objective_includes_community_costs'] is False
  assert not saved['nationwide_fertilizer_independence_claimed']
  print('PASS V7 community cost, calorie separation, nutrient mass balance, methane sensitivities and transport boundary')
if __name__=='__main__':run()
