#!/usr/bin/env python3
"""V9.5 source-traceable *screening* reconciliation of EIA 2050 and the alternative.

NOT a validated like-for-like 2050 national total-cost / full LCA comparison.
Reads the original 38-workbook archive; explicitly tags all unsourced allowances.
Does not overwrite the legacy historical-price scenario or claim fuel-only costs are comparable.
"""
from __future__ import annotations
import argparse, csv, io, json, math, pathlib, sys, zipfile, hashlib, copy
from statistics import median
from collections import defaultdict
import us2_model as M
import us2_inputs as I
import us9_crop_residue as C
import us94_aeo_service_bridge as B

HERE=pathlib.Path(__file__).resolve().parent
AEO=HERE/'AEO2026_2050_TRANSPORT_DATA.zip'


def read_source():
    provenance,a=B.read_aeo(AEO)
    with zipfile.ZipFile(AEO) as z:
        def rows(table):
            paths=[p for p in z.namelist() if p.startswith(f'csv_all_sheets/CounterfactualBaseline/Table_{table:02d}/') and p.endswith('.csv')]
            if len(paths)!=1:raise RuntimeError((table,paths))
            return {int(r['excel_row']):r for r in csv.DictReader(io.StringIO(z.read(paths[0]).decode('utf-8-sig')))}
        t49=rows(49);t39=rows(39);t52=rows(52);t36=rows(36)
        at=lambda table,n:float(table[n]['AB'])
        a['freight_medium_2050_m']=at(t49,190)
        a['freight_heavy_2050_m']=at(t49,204)
        a['freight_light_medium_2050_m']=at(t49,176)
        a['freight_medium_heavy_m']=a['freight_medium_2050_m']+a['freight_heavy_2050_m']
        a['eia_ldv_phev_m']=at(t39,63)
        a['eia_ldv_hev_m']=at(t39,64)
        a['eia_ldv_fcev_m']=at(t39,65) if False else at(t39,30)+at(t39,53)
        a['eia_medheavy_electric_m']=at(t49,183)+at(t49,197)
        a['eia_medheavy_fcev_m']=sum(at(t49,n) for n in [186,187,200,201])
        a['eia_2025_transport_direct_mt']=float(rows(70)[89]['C'])
        tech={}
        for name,offset in [('gasoline',12),('bev_300mi',136),('bev_200mi',118),('hybrid',154)]:
            tech[name]={c:at(t52,offset+offsetrow) for c,offsetrow in {'compact':3,'midsize':4,'small_crossover':7,'large_pickup':10}.items()}
        a['new_2050_vehicle_price_thousand_2025usd_selected_classes']=tech
        electricity=0.0;fossil=0.0;count=0
        for n,r in t36.items():
            try:e=float(r['AB'])
            except (ValueError,TypeError):continue
            name=(r.get('B') or '').lower().strip()
            if 'electricity' in name and e>0: electricity+=e
            if any(k in name for k in ['motor gasoline','distillate fuel oil','diesel','jet fuel','residual oil','compressed natural gas','liquefied natural gas','compressed/liquefied natural gas','propane','aviation gasoline']) and e>0:
                fossil+=e;count+=1
        a['eia2050_reported_electricity_trillion_btu_table36_sum']=electricity
        a['eia2050_fossil_trillion_btu_table36_screen']=fossil
    return provenance,a


def config(a,air_name='jet_energy',freight='eia_medium_heavy',lightweight=True):
    factors={
      'ldv':a['ldv_2050_vmt_bn']/a['ldv_2025_vmt_bn'],
      'hdv':a['hdv_2050_vmt_bn']/a['hdv_2025_vmt_bn'],
      'rail':a['rail_2050_ton_miles_bn']/a['rail_2025_ton_miles_bn'],
      'marine':a['ship_dom_2050_ton_miles_bn']/a['ship_dom_2025_ton_miles_bn'],
      'pipeline':a['pipeline_2050_fuel_trillion_btu']/a['pipeline_2025_fuel_trillion_btu'],
      'air': a['air_2050_jet_trillion_btu']/a['air_2025_jet_trillion_btu'] if air_name=='jet_energy' else a['air_2050_seat_miles_bn']/a['air_2025_seat_miles_bn']
    }
    p=M.default_params()
    for key,f in [('gasoline_mbd',factors['ldv']),('onroad_diesel_bgal',factors['hdv']),('rail_diesel_bgal',factors['rail']),('jet_mbd',factors['air']),('marine_distillate_bgal',factors['marine']),('marine_resid_mbd',factors['marine']),('pipeline_ng_quad',factors['pipeline'])]:p['BASE'][key]*=f
    p['VEH']['ldv_stock_m']=a['ldv_2050_stock_m']
    base=M.base_demand(M.default_params())[0]
    p['ENDUSE']['r_ldv_bev']=.33/(base['ldv']/a['ldv_2025_vmt_bn'])
    p['ENDUSE']['r_ldv_fcev']=.55/(base['ldv']/a['ldv_2025_vmt_bn'])
    p['ENDUSE']['r_hdv_elec']=2.40/(base['hdv']/a['hdv_2025_vmt_bn'])
    p['ENDUSE']['r_hdv_fcev']=4.44/(base['hdv']/a['hdv_2025_vmt_bn'])
    p['lightweight']=bool(lightweight)
    if freight!='original_assumed':
        stock=a['freight_medium_heavy_m'] if freight=='eia_medium_heavy' else a['freight_2050_fleet_m']
        for k,share in [('ers_trucks_m',.45),('bev_trucks_m',.30),('re_trucks_m',.15),('fcev_trucks_m',.07)]:p['VEH'][k]=share*stock
    return p,factors


def bounded(p,maximum=1500):
    best=None
    for n in range(maximum+1):
        cap=M.reactor_cost(p['reactor_case'],max(4*n,1))['fleet_avg_kwt_with_idc']*p.get('capex_mult',1)
        try:r=M.solve(p,scenario='least_cost',blend_vol=0.0,capex_kwt=cap,fixed_hubs=n)
        except RuntimeError:continue
        cost=r['transport_cost_bn']
        if best is None or cost<best[1]:best=(n,cost,r)
    return {'method':'integer hub count 0..%d with fleet average learning cost at each N'%maximum,
            'best_hubs':best[0],'best_cost_bn':best[1], 'best_wtw_mt':best[2]['emissions']['total_mt'],
            'best_onshore_gw':best[2]['gw']['onshore_wind'],'best_solar_gw':best[2]['gw']['solar'],
            'best_offshore_gw':best[2]['gw']['offshore_wind'],'best_electricity_export_twh':best[2]['el_export_twh'],
            'reactor_modules_at_best':4*best[0], 'upper_boundary_selected':best[0]==maximum,
            'comment':'Global within explicit integer-hub search bounds and assumptions only; full fleet learning assumed.'}


def reference_screen(a,alt_cost):
    # EIA fuel expenditures are inclusive of fuel taxes and 2025 price level.
    # Every other entry here is an ASSUMPTION, not an EIA supplied model result.
    energy=a['eia_energy_exp_2050_bn_2025_usd']
    ev_m=a['ldv_2050_bev_m'];phev_m=a['eia_ldv_phev_m'];hev_m=a['eia_ldv_hev_m']
    h2_ldv_m=a['eia_ldv_fcev_m']
    md_ev=a['eia_medheavy_electric_m'];md_h2=a['eia_medheavy_fcev_m']
    scenarios=[]
    for label,usd_adjust,charge_per_bev,add_offroad,vehicle_net_scale in [
       ('low_reference_scope_allowance',1.00,0,0,0.5),
       ('central_assumption_bridge',1.025,100,16,1),
       ('upper_assumption_bridge',1.04,300,34,1.5),
    ]:
        # Model net DIFFERENTIAL vs conventional stock, NOT all-in vehicle ownership.
        prem=(ev_m*100+phev_m*150+hev_m*250+h2_ldv_m*900+md_ev*2500+md_h2*10000)*vehicle_net_scale/1000
        charge=ev_m*charge_per_bev/1000
        value=energy*usd_adjust+prem+charge+add_offroad
        scenarios.append({'scenario':label,'eia_energy_expenditure_2025usd_bn':energy,'illustrative_price_year_factor_2025_to_2026':usd_adjust,'reference_net_powertrain_premium_bn_2026usd':prem,'reference_extra_charging_non_tariff_bn_2026usd':charge,'reference_offroad_scope_addendum_bn_2026usd':add_offroad,'reference_screen_total_bn_2026usd':value,'alternative_cost_bn_2026usd':alt_cost,'arithmetic_gap_alt_minus_screen_bn':alt_cost-value,'is_a_matched_total_system_comparison':False})
    return scenarios


def emissions_screen(a,alternative_mt):
    direct=a['eia_transport_direct_co2_2050_mt']; fossil=a['eia2050_fossil_trillion_btu_table36_screen'];electric=a['eia2050_reported_electricity_trillion_btu_table36_sum']
    cases=[]
    for k,(upstream_g_mj,elec_g_kwh) in {'low':(5,10),'mid':(10,50),'high':(15,100)}.items():
        # 1 trillion BTU = 1.05505585 billion MJ; hence 0.00105505585 Mt/(g/MJ) per TBtu
        up=fossil*upstream_g_mj*0.00105505585
        # 1 TBtu = 0.29307107 TWh; 1g/kWh x 1TWh = 0.001 Mt
        power=electric*0.29307107*elec_g_kwh*0.001
        total=direct+up+power
        cases.append({'scenario':k,'eia_direct_mt':direct,'screen_upstream_g_per_mj':upstream_g_mj,'screen_electricity_g_per_kwh':elec_g_kwh,'screen_fossil_upstream_mt':up,'screen_electricity_lifecycle_mt':power,'partial_reference_wtw_mt':total,'alternative_model_wtw_mt':alternative_mt,'partial_avoided_mt':total-alternative_mt,'matched_boundary_verified':False})
    return cases


def make():
    prov,a=read_source()
    cases={}
    for name,air,freight,lw,crop,force in [
      ('v94_jet_existing_truck_stock','jet_energy','original_assumed',True,False,False),
      ('v95_jet_eia_medium_heavy_fleet','jet_energy','eia_medium_heavy',True,False,False),
      ('v95_seatmiles_eia_medium_heavy_fleet','seat_miles','eia_medium_heavy',True,False,False),
      ('v95_no_lightweighting','jet_energy','eia_medium_heavy',False,False,False),
      ('v95_conservative_biomass_optional_crop','jet_energy','eia_medium_heavy',True,True,False),
      ('v95_conservative_biomass_forced_full_crop','jet_energy','eia_medium_heavy',True,True,True),
    ]:
        p,factors=config(a,air,freight,lw)
        if crop:p=C.with_crop(p,supply_mt=166.0,force_fraction=int(force),forest_mt=150.0)
        r=M.solve_learning(p,scenario='least_cost',blend_vol=0.0)
        so=r.get('crop_residue_soil') or {}
        cases[name]={'alternative_cost_bn_2026usd':r['transport_cost_bn'],'alternative_wtw_mt':r['emissions']['total_mt'],'hubs':r['hubs'],'electricity_twh':r['enduse']['el_total'],'hydrogen_direct_twh':r['enduse']['h2_mt_direct']*I.H2_LHV_KWH_KG,'hydrogen_direct_mt':r['enduse']['h2_mt_direct'],'total_hydrogen_production_mt':sum(r['h2_mt'][k] for k in ['pyrolysis','electrolysis','steam_electrolysis','sulfur_iodine']),'crop_mt':so.get('feedstock_mt',0),'nitrogen_import_kt':so.get('nutrients',{}).get('n',{}).get('imported_kt',0),'phosphorus_import_kt':so.get('nutrients',{}).get('p',{}).get('imported_kt',0),'potassium_import_kt':so.get('nutrients',{}).get('k',{}).get('imported_kt',0),'soil_c_gap_mt':max(0,-so.get('carbon_balance_surplus_mt',0)),'objective_residual_bn':r['objective_reconciliation']['residual_bn'],'truck_stock_m_in_costs':sum(p['VEH'][k] for k in ['ers_trucks_m','bev_trucks_m','fcev_trucks_m','re_trucks_m']),'lightweight':lw,'aviation_proxy':air,'crop_supply_restriction_enabled':bool(crop)}
        if not crop:print(name,'cost',round(r['transport_cost_bn'],3),'hubs',round(r['hubs'],3),'emission',round(r['emissions']['total_mt'],3),flush=True)
    p,_=config(a)
    b=bounded(p,maximum=1500)
    hb=bounded(M.default_params(),maximum=1500)
    print('bounded AEO',b,'bounded historical',hb,flush=True)
    result={'version':'9.5 research revision','provenance':prov,'eia_source_values':a,'comparability_limits':['EIA reference energy expenditures include fuel taxes and are in 2025 USD, unlike alternative system cost in 2026 USD.','Alternative cost assumes fixed end-use mixes, selected offroad services, annual mean (not time series) dispatch and assumed net vehicle premiums.','EIA truck-size category mapping requires reconciliation with truck-use service and alternative stock; 12.56 million is a medium-plus-heavy sensitivity, not a measured conversion fleet.','EIA direct CO2 and model well-to-wheel CO2e are not the same scope. Emissions ranges below are conditional upstream screens, not complete LCA.','Aviation jet-energy proxy and available-seat-mile proxy differ in aircraft efficiency and occupancy.','Agricultural soil carbon, fertilizer, residue availability and other biophysical constraints are screening parameters, not field-calibrated validation.'], 'scenarios':cases,'reactor_bounded_search':b,'historical_bounded_search':hb,'reference_cost_screens':reference_screen(a,cases['v95_jet_eia_medium_heavy_fleet']['alternative_cost_bn_2026usd']),'reference_emissions_screens':emissions_screen(a,cases['v95_jet_eia_medium_heavy_fleet']['alternative_wtw_mt']),'fully_matched_2050_comparison_complete':False}
    (HERE/'US95_AEO2026_Cost_Emissions_Results.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    for label,rows in [('us95_scenario_results.csv',[dict(scenario=k,**v) for k,v in cases.items()]),('us95_aeo_reference_cost_screens.csv',result['reference_cost_screens']),('us95_aeo_reference_emissions_screens.csv',result['reference_emissions_screens'])]:
        with (HERE/label).open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,rows[0].keys());w.writeheader();w.writerows(rows)
    return result

if __name__=='__main__':make()
