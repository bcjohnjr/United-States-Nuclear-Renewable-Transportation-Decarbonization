"""V6 independent N/P conservation, scenario and uncertainty regression tests."""
from dataclasses import replace
import json
from pathlib import Path

from us6_nutrient_balance import NutrientInputs, model, scenario_result, draw_monte_carlo, ROOT


def approx(a,b,tol=1e-8):
    return abs(a-b)<=tol*max(1.0,abs(a),abs(b))


def test():
    s=json.loads((ROOT/'scenarios.json').read_text());base=s['least_cost']
    z=scenario_result(base)
    assert approx(z['seafood_mt'],1.0)
    assert approx(z['target_asparagopsis_mt_dry'],base['food']['asparagopsis']['seaweed_mt_dry'])
    assert approx(z['target_methane_reduction_mtco2e'],base['food']['asparagopsis']['mtco2e_cut'])
    assert z['closed_loop_limiting_n_or_p']=='N'
    assert z['closed_loop_target_fraction']<1 and z['external_target_n_kt']>0
    assert z['external_target_p_kt']==0
    assert approx(z['closed_loop_methane_reduction_mtco2e'],z['target_methane_reduction_mtco2e']*z['closed_loop_target_fraction'])
    assert approx(z['freed_low_grade_heat_twh'],z['target_seaweed_heat_twh']-z['closed_loop_seaweed_heat_twh'])
    for nutrient in ('nitrogen','phosphorus'):
        f=z[nutrient]
        assert approx(f['feed_kt'],f['seafood_harvest_kt']+f['waste_kt'])
        assert approx(f['waste_kt'],f['dissolved_waste_kt']+f['solid_waste_kt'])
        assert approx(f['delivered_recovered_kt']+f['treatment_delivery_loss_kt'],f['captured_dissolved_kt']+f['captured_solids_kt'])
        assert abs(f['mass_balance_residual_closed_kt'])<1e-7
        assert abs(f['mass_balance_residual_target_kt'])<1e-7
        assert f['seaweed_uptake_closed_kt']<=f['eligible_for_seaweed_kt']+1e-6
        assert f['seaweed_uptake_target_recovered_kt']<=f['eligible_for_seaweed_kt']+1e-6
        assert f['fertiliser_candidate_closed_kt']>=0
    # Zero seafood feed cannot sustain a marine-seaweed biomass target.
    zero=model(0,z['target_asparagopsis_mt_dry'],z['target_methane_reduction_mtco2e'])
    assert zero['closed_loop_asparagopsis_mt_dry']==0
    assert approx(zero['external_target_n_kt'],zero['target_uptake_n_kt'])
    assert approx(zero['external_target_p_kt'],zero['target_uptake_p_kt'])
    # Prevent treating unapproved/non-compatible nutrients as seaweed feed.
    withheld=model(1,z['target_asparagopsis_mt_dry'],45,replace(NutrientInputs(),seaweed_eligible_fraction=0))
    assert withheld['closed_loop_asparagopsis_mt_dry']==0
    # Perfect routing/recovery still cannot create nutrients beyond feed inputs.
    full=replace(NutrientInputs(),seaweed_eligible_fraction=1,delivery_retain_fraction=1,
                 capture_dissolved_n=1,capture_dissolved_p=1,capture_solid_n=1,capture_solid_p=1)
    f=model(1,z['target_asparagopsis_mt_dry'],45,full)
    assert f['closed_loop_target_fraction']>=z['closed_loop_target_fraction']
    for k in ('nitrogen','phosphorus'):
        assert f[k]['delivered_recovered_kt']<=f[k]['feed_kt']
    # Each production scenario draws its inputs from the same original saved V5 results.
    saved=json.loads((ROOT/'nutrient_balance_v6.json').read_text())
    for name,out in saved['scenarios'].items():
        fresh=scenario_result(s[name])
        assert approx(fresh['closed_loop_asparagopsis_mt_dry'],out['closed_loop_asparagopsis_mt_dry'])
        assert approx(fresh['external_target_n_kt'],out['external_target_n_kt'])
        for k in ('nitrogen','phosphorus'):
            assert abs(out[k]['mass_balance_residual_target_kt']) < 1e-7
    # 1000 seeded uncertainty draws deterministic, mass conserving and nonnegative.
    n_draws=saved['monte_carlo_n']
    rows=draw_monte_carlo(base['food'],n_draws,23)
    again=draw_monte_carlo(base['food'],n_draws,23)
    assert rows==again
    assert len(rows)==n_draws
    assert all(0<=r['closed_fraction']<=1 for r in rows)
    assert all(r['n_external_kt']>=0 and r['p_external_kt']>=0 for r in rows)
    assert saved['monte_carlo_n']==n_draws
    assert approx(saved['uncertainty']['closed_loop_fraction']['p50'],
                  __import__('numpy').median([r['closed_fraction'] for r in rows]))
    print('PASS: V6 feed, seafood, treatment, seaweed, residual, alternative-case and seeded Monte Carlo tests')

if __name__=='__main__':test()
