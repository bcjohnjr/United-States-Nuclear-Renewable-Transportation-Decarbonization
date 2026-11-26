"""Same-service petroleum counterfactual and constrained incremental gas routing.
No change to legacy vehicle technology shares or production LP; sequential LP allocation.
All gas volumes in TWh LHV except explicitly HHV pipeline values. Costs USD bn/yr.
"""
import json,csv,math
from pathlib import Path
from scipy.optimize import linprog
import us95_aeo_reference_bridge as A, us97_circular_feedstocks as C, us99_agricultural_accounts as U, us2_model as M, us915_methane as W
P=Path(__file__).resolve().parent

def run():
    _,a=A.read_source(); b=json.loads((P/'US97_AEO_Boundary.json').read_text())['results'][1]
    def params(cap):return U.carbon_land(U.plant_available(C.build_params(a,bevpremium=b['net_bev_differential_usd_yr'],release_fraction=.5,apply_pyro_to_soil=False,allow_stable_hydrochar=False,cap_mt=cap)),20e6,.5)
    p=params(166); r=M.solve_learning(p,scenario='least_cost',blend_vol=0,osw_scale=0.,kelp_force=False)
    c=C.one('central rerun',p); no=C.one('no crop rerun',params(0))
    alt=U.integrated_lca(c)['replaced_route_screen_mt']; cost=r['transport_cost_bn']; ref=1638.8; aeo_cost=477.1
    assert abs(cost-654.7633815744267)<1e-6 and abs(alt-229.38444669755273)<1e-6
    petro=r['petroleum']; pipe=r['enduse']['gas_resid_twh']; hhv_lhv=55.5/50
    # Existing fuel convention is BTU (HHV); convert LHV delivered biomethane to same basis.
    cap=pipe/hhv_lhv; avoided_gas_value=3.412*(p['GAS']['price_mmbtu']+.5)*hhv_lhv # $/MWh LHV
    direct_ci=202. # kg fossil CO2/MWh LHV only; no fossil upstream credit.
    references=[dict(name='AEO2026 partial reference',ref_cost_bn=aeo_cost,ref_emissions_mt=ref)]
    for label in ('late_2025','nov_2026'):
        references.append(dict(name='Continued petroleum — '+label+' inherited price case',ref_cost_bn=petro['prices'][label]['pretax_bn']+petro['pipeline_gas_bn'],ref_emissions_mt=petro['wtw_mt']))
    # price scaling applied only to petroleum liquids, gas price held fixed.
    for k in (.7,1.3):references.append(dict(name=f'Continued petroleum — {k:.1f}x late-2025 liquid price',ref_cost_bn=petro['prices']['late_2025']['pretax_bn']*k+petro['pipeline_gas_bn'],ref_emissions_mt=petro['wtw_mt']))
    rows=[]
    for name,inputs in W.SCENARIOS.items():
        for carbon in (0,100,200):
            w=W.evaluate(inputs); q=w['biomethane_twh']; sale=inputs['gas_price']; gross_cost=w['biogas_cost_bn']+w['asp_cost_bn']
            # Allocate all delivered gas once. Objective minimizes incremental resource-cost screen minus carbon value.
            opt=linprog([-avoided_gas_value-carbon*direct_ci/1000,-sale],A_eq=[[1,1]],b_eq=[q],bounds=[(0,cap),(0,None)],method='highs')
            assert opt.success,opt.message
            internal,external=opt.x; assert abs(internal+external-q)<1e-8
            assert internal*hhv_lhv<=pipe+1e-8
            gas_credit=internal*direct_ci/1000; added=w['incremental_net_avoided_mt']; netcost=gross_cost-(internal*avoided_gas_value+external*sale)/1000
            if internal<1e-8:assert abs(netcost-w['incremental_net_cost_bn'])<1e-8
            for z in references:
                baseline=z['ref_emissions_mt']; basecost=z['ref_cost_bn']; trans_alt=alt-gas_credit
                rows.append(dict(scenario=name,carbon_shadow_usd_t=carbon,reference=z['name'],ref_cost_bn=basecost,ref_emissions_mt=baseline,transport_cost_before_ad_bn=cost,transport_emissions_before_ad_mt=alt,internal_biomethane_lhv_twh=internal,external_biomethane_lhv_twh=external,displaced_pipeline_hhv_twh=internal*hhv_lhv,gas_direct_credit_mt=gas_credit,agri_net_avoided_mt=added,incremental_programme_cost_bn=netcost,combined_cost_bn=cost+netcost,combined_cost_saving_bn=basecost-cost-netcost,combined_cost_saving_pct=100*(basecost-cost-netcost)/basecost,transport_reduction_before_ad_pct=100*(1-alt/baseline),transport_reduction_after_gas_pct=100*(1-trans_alt/baseline),combined_avoided_mt=baseline-trans_alt+added))
    out=dict(version='9.16',baseline_rerun_cost_bn=cost,baseline_rerun_lca_mt=alt,no_crop_cost_bn=no['annual_cost_bn'],crop_saving_bn=no['annual_cost_bn']-cost,service_demand_twh=r['enduse']['demand'],petroleum_breakdown=petro,gas_pipeline_hhv_twh=pipe,gas_pipeline_lhv_twh=cap,gas_avoided_value_usd_mwh_lhv=avoided_gas_value,gas_direct_kg_mwh_lhv=direct_ci,references=references,rows=rows,limitations=['Same-service petroleum screen uses inherited pretax price cases, not forecasts; common conventional vehicle ownership excluded, alternative net premiums retained. Scope is model services, not exact EIA mode coverage.','Sequential annual gas-routing LP only, not national spatial collection or joint hourly investment optimisation. Carbon shadow values rank routing, are not revenues. External sales receive zero displacement credit.','No fertilizer, soil-carbon, external gas abatement, heat or food revenue added; agricultural module standalone costs include heat/nutrients. GWP factors not fully harmonised.'])
    (P/'US916_Coupled_Results.json').write_text(json.dumps(out,indent=2))
    with (P/'us916_coupled_scenarios.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    print('PASS same-service central transport rerun, paired no-crop solve, gas allocation and cost/energy balances; 45 cases')
    for x in rows:
        if x['scenario']=='central' and x['carbon_shadow_usd_t'] in (0,100) and '0.' not in x['reference'] and '1.3' not in x['reference']:print(x)
    return out
if __name__=='__main__':run()
