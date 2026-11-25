#!/usr/bin/env python3
"""Exploratory JOINT uncertainty on *partial* EIA reference cost bridge.

Every distribution is explicitly analyst-defined; these are not probabilities of 2050
outcomes, a complete matched reference, or external forecasts. Common sampled
cost parameters are passed to both comparator sides when their meaning matches.
"""
import csv,json,math,pathlib,random,sys
import us2_model as M
import us95_aeo_reference_bridge as V
HERE=pathlib.Path(__file__).resolve().parent

def run(n=1000,seed=9526):
    _,a=V.read_source();R=random.Random(seed)
    rows=[]
    for i in range(n):
        prem=R.uniform(-100,700)
        oil=R.uniform(.70,1.35)
        grid=R.uniform(.8,1.3)
        reactor=R.uniform(.75,1.55)
        biomass=R.uniform(.80,1.35)
        fleet=R.uniform(.8,1.2)
        jet=R.uniform(a['air_2050_jet_trillion_btu']/a['air_2025_jet_trillion_btu'],a['air_2050_seat_miles_bn']/a['air_2025_seat_miles_bn'])
        usd_adj=R.uniform(1.0,1.05)
        fossil_exp_share=R.uniform(.60,.88)
        offroad_extra=R.uniform(0,38)
        charging_extra=R.uniform(0,300)
        pmult=R.uniform(.5,1.5)
        methane=R.uniform(.01,.035)
        p,_=V.config(a,freight='eia_medium_heavy')
        p['BASE']['jet_mbd']=M.default_params()['BASE']['jet_mbd']*jet
        for k in ('ers_trucks_m','bev_trucks_m','fcev_trucks_m','re_trucks_m'):p['VEH'][k]*=fleet
        p['VEH']['ldv_bev_net_usd_yr']=prem
        p['ELEC']['onshore_wind']*=grid;p['ELEC']['solar']*=grid;p['ELEC']['lwr_smr']*=grid
        for j,t in enumerate(p['BIOMASS']['tiers']):p['BIOMASS']['tiers'][j]=(t[0],t[1],t[2]*biomass)
        p['capex_mult']=reactor
        p['PYRO']['leak_upstream']=methane
        r=M.solve_learning(p,scenario='least_cost',blend_vol=0)
        reference_energy=a['eia_energy_exp_2050_bn_2025_usd']*usd_adj*(fossil_exp_share*oil+(1-fossil_exp_share)*grid)
        # Common net BEV cost premium, but other powertrain premia are explicitly assumed.
        ref_ldv=(a['ldv_2050_bev_m']*prem+a['eia_ldv_phev_m']*150+a['eia_ldv_hev_m']*250)/1000
        ref_trucks=(a['eia_medheavy_electric_m']*2500+a['eia_medheavy_fcev_m']*10000)*pmult/1000
        reference=reference_energy+ref_ldv+ref_trucks+a['ldv_2050_bev_m']*charging_extra/1000+offroad_extra
        delta=r['transport_cost_bn']-reference
        rows.append({'draw':i,'alternative_cost_bn':r['transport_cost_bn'],'reference_screen_cost_bn':reference,'delta_alt_minus_reference_bn':delta,'alt_cheaper_in_this_parameter_draw':int(delta<0),'bev_net_premium_usd_yr':prem,'oil_price_multiplier':oil,'grid_price_multiplier':grid,'reactor_learning_capex_multiplier':reactor,'biomass_cost_multiplier':biomass,'truck_stock_multiplier':fleet,'aviation_service_factor':jet,'fossil_energy_spending_share_assumed':fossil_exp_share,'year_price_adjustment_assumed':usd_adj,'non_energy_offroad_reference_addendum_bn':offroad_extra,'reference_charging_annual_per_bev_assumed':charging_extra,'upstream_methane_leakage':methane,'alternative_wtw_mt':r['emissions']['total_mt'],'not_a_full_2050_matched_comparison':True})
    p=sorted(x['delta_alt_minus_reference_bn'] for x in rows)
    def quant(f):return p[round(f*(len(p)-1))]
    summary={'draws':len(rows),'seed':seed,'median_alt_minus_reference_bn':quant(.5),'p05_delta_bn':quant(.05),'p95_delta_bn':quant(.95),'fraction_negative_cost_gap_in_assumed_draws':sum(x['alt_cheaper_in_this_parameter_draw'] for x in rows)/len(rows),'qualification':'Illustrative uncertainty only; incomplete scope and tax/embodied-emissions reconciliation, distributions not calibrated to predictive forecasts. CANNOT infer probability of cost advantage.'}
    with (HERE/'us95_paired_aeo_cost_screen.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,rows[0].keys());w.writeheader();w.writerows(rows)
    (HERE/'us95_paired_aeo_uncertainty_summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))
    return summary
if __name__=='__main__':run(int(sys.argv[1]) if len(sys.argv)>1 else 1000)
