#!/usr/bin/env python3
"""Reproducible AEO2026-to-U.S. model *partial* harmonisation.
User-supplied EIA AEO2026 downloaded spreadsheet CSVs, source SHA256 manifest.
This is not a fully matched national reference costing or lifecycle GHG comparison.
"""
import csv,hashlib,io,json,pathlib,sys,zipfile,copy,math
from dataclasses import dataclass
ROOT=pathlib.Path(__file__).resolve().parent
AEO=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'AEO2026_2050_TRANSPORT_DATA.zip'
sys.path.insert(0,str(ROOT))
import us2_model as M
import us2_inputs as I

def read_aeo(path):
    with zipfile.ZipFile(path) as z:
        entries=list(csv.DictReader(io.StringIO(z.read('download_manifest.csv').decode('utf-8-sig'))))
        assert len(entries)==38,'The downloader should include all 38 selected EIA files'
        for e in entries:
            p=e['file'].replace('\\','/')
            assert e['status']=='downloaded' and hashlib.sha256(z.read(p)).hexdigest()==e['sha256'], f'Incomplete/altered EIA file: {p}'
        lookups={}
        def a(t,n,year='2050'):
            if t not in lookups:
                q=[p for p in z.namelist() if p.startswith(f'csv_all_sheets/CounterfactualBaseline/Table_{t:02d}/') and p.endswith('.csv')]
                assert len(q)==1,(t,q)
                lookups[t]={int(r['excel_row']):r for r in csv.DictReader(io.StringIO(z.read(q[0]).decode('utf-8-sig')))}
            r=lookups[t][n]; return float(r['AB' if year=='2050' else 'C'])
        provenance={"case":"AEO2026 Counterfactual Baseline","source_file_count":38,"sha256_all_passed":True,"source_archive_sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
        data={
        'ldv_2025_vmt_bn':a(7,15,'2025'),'ldv_2050_vmt_bn':a(7,15),
        'hdv_2025_vmt_bn':a(7,17,'2025'),'hdv_2050_vmt_bn':a(7,17),
        'rail_2025_ton_miles_bn':a(7,24,'2025'),'rail_2050_ton_miles_bn':a(7,24),
        'ship_dom_2025_ton_miles_bn':a(7,25,'2025'),'ship_dom_2050_ton_miles_bn':a(7,25),
        'air_2025_seat_miles_bn':a(7,22,'2025'),'air_2050_seat_miles_bn':a(7,22),
        'air_2025_jet_trillion_btu':a(36,57,'2025'),'air_2050_jet_trillion_btu':a(36,57),
        'pipeline_2025_fuel_trillion_btu':a(36,105,'2025'),'pipeline_2050_fuel_trillion_btu':a(36,105),
        'ldv_2050_stock_m':a(39,33)+a(39,56),
        'ldv_2050_bev_m':sum(a(39,n) for n in [20,21,22,43,44,45]),
        'freight_2050_fleet_m':a(49,205),
        'eia_energy_exp_2050_bn_2025_usd':a(3,73)+a(3,75),
        'eia_transport_direct_co2_2050_mt':a(70,89),
        'gasoline_price_2050_2025usd_gal':a(12,39),
        'diesel_price_2050_2025usd_gal':a(12,41),
        }
    return provenance,data

def run():
    prov,aeo=read_aeo(AEO)
    factor=lambda a,b: aeo[a]/aeo[b]
    vmt_ldv=factor('ldv_2050_vmt_bn','ldv_2025_vmt_bn')
    vmt_hdv=factor('hdv_2050_vmt_bn','hdv_2025_vmt_bn')
    rail=factor('rail_2050_ton_miles_bn','rail_2025_ton_miles_bn')
    ship=factor('ship_dom_2050_ton_miles_bn','ship_dom_2025_ton_miles_bn')
    air_energy=factor('air_2050_jet_trillion_btu','air_2025_jet_trillion_btu')
    air_service=factor('air_2050_seat_miles_bn','air_2025_seat_miles_bn')
    pipeline=factor('pipeline_2050_fuel_trillion_btu','pipeline_2025_fuel_trillion_btu')
    base=M.default_params()
    initial= M.base_demand(base)[0]
    ldv_ref_kwh_mi=initial['ldv']/aeo['ldv_2025_vmt_bn']
    hdv_ref_kwh_mi=initial['hdv']/aeo['hdv_2025_vmt_bn']
    # The ratios reference the actual *base demand* in the national model, not the
    # unrelated 1.41 kWh/mi and 21.1 MJ/mi engineering examples.
    def setup(air_factor,marine_factor,absolute_drive):
        p=M.default_params()
        for k,f in [('gasoline_mbd',vmt_ldv),('onroad_diesel_bgal',vmt_hdv),('rail_diesel_bgal',rail),
                    ('jet_mbd',air_factor),('marine_distillate_bgal',marine_factor),('marine_resid_mbd',marine_factor),('pipeline_ng_quad',pipeline)]:
            p['BASE'][k]*=f
        p['VEH']['ldv_stock_m']=aeo['ldv_2050_stock_m']
        if absolute_drive:
            p['ENDUSE']['r_ldv_bev']=.33/ldv_ref_kwh_mi
            p['ENDUSE']['r_ldv_fcev']=.55/ldv_ref_kwh_mi
            p['ENDUSE']['r_hdv_elec']=2.40/hdv_ref_kwh_mi
            p['ENDUSE']['r_hdv_fcev']=4.44/hdv_ref_kwh_mi
        return p
    cases=[]
    for label,af,sf,absdrive in [
        ('EIA 2050 mode activity; jet-fuel-energy scaling; domestic shipping; physical drive intensities',air_energy,ship,True),
        ('EIA 2050 mode activity; available-seat-mile scaling; domestic shipping; physical drive intensities',air_service,ship,True),
        ('Same activity; original energy ratios (diagnostic)',air_energy,ship,False),
    ]:
        p=setup(af,sf,absdrive)
        r=M.solve_learning(p,scenario='least_cost',blend_vol=0)
        # Existing BEV stock in EIA is not an incremental fleet conversion.
        ref_bev_premium_bn=aeo['ldv_2050_bev_m']*p['VEH']['ldv_bev_net_usd_yr']/1000
        ev_result=M.enduse_2050(p)
        cases.append({
            'scenario':label,
            'annual_alternative_model_cost_bn_2026usd':round(r['transport_cost_bn'],6),
            'alternative_model_wtw_mtco2e':round(r['emissions']['total_mt'],6),
            'reactor_hubs':r['hubs'],
            'ldv_stock_m':p['VEH']['ldv_stock_m'],
            'ref_2050_existing_bev_stock_m':aeo['ldv_2050_bev_m'],
            'additional_bevs_vs_aeo_m':max(0, p['VEH']['ldv_stock_m']*p['ENDUSE']['ldv']['bev']-aeo['ldv_2050_bev_m']),
            'existing_aeo_bev_premium_included_in_model_bn':round(ref_bev_premium_bn,4),
            'alt_cost_if_current_bev_premium_is_reference_credited_bn':round(r['transport_cost_bn']-ref_bev_premium_bn,6),
            'transport_electricity_twh':round(ev_result['el_total'],6),
            'transport_liquids_twh':round(ev_result['liq_total'],6),
            'jet_activity_factor':af,
            'marine_activity_factor':sf,
            'relative_drive_ratios_reanchored_to_2025_AEO_VMT':absdrive,
        })
    result={
    'provenance':prov,'aeo_2050':aeo,
    'scaling_factors':dict(ldv_vmt=vmt_ldv,hdv_vmt=vmt_hdv,rail_ton_miles=rail,domestic_shipping_ton_miles=ship,air_jet_energy=air_energy,air_seat_miles=air_service,pipeline_fuel=pipeline),
    'absolute_drive_reference':{'ldv_base_kwh_per_mile':ldv_ref_kwh_mi,'hdv_base_kwh_per_mile':hdv_ref_kwh_mi,'bev_ldv_kwh_per_mile':.33,'fcev_ldv_kwh_per_mile':.55,'bev_hdv_kwh_per_mile':2.4,'fcev_hdv_kwh_per_mile':4.44},
    'cases':cases,
    'matched_cost_or_abatement_cost_established':False,
    'reasons_not_a_matched_cost_comparison':[
        'EIA 2050 reference expenditure is energy only in 2025 dollars and tax inclusive; the alternative includes modeled infrastructure and annual net vehicle premiums in 2026 dollars.',
        'The AEO counterfactual baseline already contains about 154 million EVs; the alternative assumes a 95% BEV mix. Existing fleet ownership and turnover costs are not matched.',
        'The user model also covers farm, construction/mining machinery, industrial trucks and includes different international shipping/aviation boundaries.',
        'AEO direct CO2 is not equal to modeled well-to-wheel CO2e; no valid comparable cost per tonne is calculated.',
        'AEO technology-specific VMT and joint stock-by-size-class plus depreciation/maintenance assumptions are not uniquely available from tables alone.',
        'Results are exploratory screening diagnostics, and aviation service proxies do not prove operational feasibility.'
    ]}
    (ROOT/'US94_AEO2026_2050_Service_Scenarios.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    keys=['scenario','annual_alternative_model_cost_bn_2026usd','alternative_model_wtw_mtco2e','reactor_hubs','ldv_stock_m','ref_2050_existing_bev_stock_m','additional_bevs_vs_aeo_m','existing_aeo_bev_premium_included_in_model_bn','alt_cost_if_current_bev_premium_is_reference_credited_bn','transport_electricity_twh','transport_liquids_twh','jet_activity_factor','marine_activity_factor','relative_drive_ratios_reanchored_to_2025_AEO_VMT']
    with (ROOT/'US94_AEO2026_2050_Service_Scenarios.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,keys);w.writeheader();w.writerows(cases)
    print(json.dumps({'factors':result['scaling_factors'],'cases':cases},indent=2))
if __name__=='__main__':run()
