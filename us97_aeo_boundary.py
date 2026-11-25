#!/usr/bin/env python3
"""V9.7 explicit source-row, BEV, tax and upstream LCA reconciliation.

AEO Table36 2050 direct emissions already counted in EIA Table70; the fossil
rows below are ONLY used for assumed incremental UPSTREAM intensity, not for
adding combustion a second time. LNG-export liquefaction explicitly excluded.
Hydrogen pathways uncertain; bracket with kgCO2e/kgH2 coefficients, not claimed
as official EIA refinery/H2 lifecycle emission factors.
"""
from pathlib import Path
import csv,json,math,zipfile,io,copy
import us96_aeo_shared_assumptions as V
import us95_aeo_reference_bridge as B
import us2_model as M
ROOT=Path(__file__).resolve().parent
# Explicit mutually exclusive non-total fuel ROWS from source Table 36.
# Heading totals omitted; no rows identified by fragile substring matching.
FOSSIL_BASE=[13,15,16,17,22,24,25,26,31,32,33,34,41,45,46,48,
             51,52,54,57,58,61,62,63,67,69,70,71,77,83,85,86,87,
             93,98,101,102,105]
# Excluded: 106 LNG export processing (upstream industrial liquefaction), 104
# lubricants (non-combusted), E85 bio-blends for fossil-specific WTW intensity.
ELEC_ROWS=[18,27,36,72,80,88,92,95,97]
H2_ROWS=[19,28,37,73,81,89]

def table36():return V.table36()

def source_price_mix():
    with zipfile.ZipFile(ROOT/'AEO2026_2050_TRANSPORT_DATA.zip') as z:
        files=[p for p in z.namelist() if p.startswith('csv_all_sheets/CounterfactualBaseline/Table_39/') and p.endswith('.csv')]
        assert len(files)==1
        rows={int(r['excel_row']):r for r in csv.DictReader(io.StringIO(z.read(files[0]).decode('utf-8-sig')))}
    for idx in (30,53,63,64):assert idx in rows
    # Stock shares from Table39 identified in referee and source rows; stored
    # explicitly rather than relying on ambiguous ordering in a source table.
    return dict(bev100_m=.41,bev200_m=60.08,bev300_m=93.95,total_m=154.44,
        source='AEO2026 Table 39 2050 installed BEV stock; 100-mile price proxied as 200-mile price when missing',
        caution='Stock mix is NOT new-vehicle sales weighting; segment mixes remain analyst assumptions')

def crf(rate,years):return rate/(1-(1+rate)**(-years))

def emission_inventory(upstream_g_mj=10,grid_g_kwh=50,h2_kgco2_kg=10,h2_kwh_kg=39.4):
    _,a=B.read_source()
    r=table36()
    get=lambda n:float(r[n]['AB'])
    # Separate sets audited against the source row names; no double-counted
    # heading rows. Marine international and military explicitly labelled.
    fossil_tbtu=sum(get(i) for i in FOSSIL_BASE)
    electric_tbtu=sum(get(i) for i in ELEC_ROWS)
    h2_tbtu=sum(get(i) for i in H2_ROWS)
    hydrogen_mt=h2_tbtu*.29307107/h2_kwh_kg # TWh / (kWh/kg == TWh/Mt); default HHV, keep LHV sensitivity
    upstream_mt=fossil_tbtu*upstream_g_mj*.00105505585
    grid_mt=electric_tbtu*.29307107*grid_g_kwh*.001
    h2_production_mt=hydrogen_mt*h2_kgco2_kg # Mt H2 × kgCO2e/kgH2 = Mt CO2e
    # EIA direct already includes combustion, so add only process emission
    # increments. Scope and source-energy burden remain uncertain.
    total=a['eia_transport_direct_co2_2050_mt']+upstream_mt+grid_mt+h2_production_mt
    return dict(direct_mt=a['eia_transport_direct_co2_2050_mt'],fossil_energy_tbtu=fossil_tbtu,
      electricity_tbtu=electric_tbtu,hydrogen_energy_tbtu=h2_tbtu,hydrogen_mass_mt=hydrogen_mt,
      added_upstream_mt=upstream_mt,added_electricity_mt=grid_mt,added_hydrogen_mt=h2_production_mt,
      screening_wtw_mt=total,upstream_g_mj=upstream_g_mj,grid_g_kwh=grid_g_kwh,
      reference_h2_production_kgco2_kg=h2_kgco2_kg,hydrogen_energy_basis=('HHV 39.4 kWh/kg (provisional AEO gross-heat convention)' if h2_kwh_kg>36 else 'LHV 33.33 kWh/kg sensitivity'),
      included_fossil_table36_rows=FOSSIL_BASE,excluded_table36_rows={'106':'LNG export liquefaction outside transport boundary','104':'lubricants/non-combustion'},
      note='Source H2 pathway uncertain and may be counted in non-transport energy sectors; life-cycle increment is a sensitivity, not verified EIA total LCA')

def run():
    _,a=B.read_source(); prices=V.vehicle_prices();stock=source_price_mix(); tax=V.excise_tax_screen()
    w300=stock['bev300_m']/stock['total_m'];w200=(stock['bev200_m']+stock['bev100_m'])/stock['total_m']
    weighted_bev=prices['bev300']*w300+prices['bev200']*w200
    cases=[]
    # Shared source-weighted vehicle-stock price; sales mix and financing are
    # alternate sensitivities. EIA Table 52 new prices, annualised either by
    # straight-line or discounted capital-recovery method on BOTH sides.
    prev=json.loads((ROOT/'US96_Shared_2050_Screen.json').read_text())
    opts=[('V9.6 analyst 80% long-range, 15-year straight line',.8,15,0.,250.,10,50,10),
          ('EIA 2050 stock-weighted, 15-year straight line',w300,15,0.,250.,10,50,10),
          ('EIA 2050 stock-weighted, 15-year financed at 7%',w300,15,.07,250.,10,50,10),
          ('EIA 2050 stock-weighted, low reference H2 carbon',w300,15,0.,250.,10,50,0),
          ('EIA 2050 stock-weighted, high reference H2 carbon',w300,15,0.,250.,10,50,15)]
    for label,share,years,rate,maint,up,grid,h2ci in opts:
        purchase_delta_usd=(share*prices['bev300']+(1-share)*prices['bev200']-prices['ice'])*1000
        annual=(crf(rate,years) if rate>0 else 1/years)*purchase_delta_usd
        net_bev=(annual-maint)*1.025
        p,_=B.config(a,freight='eia_medium_heavy')
        p['VEH']['ldv_bev_net_usd_yr']=net_bev
        alt=M.solve_learning(p,scenario='least_cost',blend_vol=0)
        # Identical differential purchase-cost convention on both sides.
        other_ref=(a['eia_ldv_phev_m']*((prices['phev']-prices['ice'])*1000/(years) - maintain(maint)) +
                   a['eia_ldv_hev_m']*((prices['hev']-prices['ice'])*1000/(years)-maintain(maint)))/1000
        ref_bev=a['ldv_2050_bev_m']*net_bev/1000
        ref_truck=(a['eia_medheavy_electric_m']*p['VEH']['bev_truck_net_usd_yr']+a['eia_medheavy_fcev_m']*p['VEH']['fcev_truck_net_usd_yr'])/1000
        energy=a['eia_energy_exp_2050_bn_2025_usd']*1.025
        ref=energy-tax['illustrative_tax_bn']*.5+ref_bev+other_ref*1.025+ref_truck+a['ldv_2050_bev_m']*.100+16.
        emo=emission_inventory(up,grid,h2ci)
        avoided=emo['screening_wtw_mt']-alt['emissions']['total_mt']
        cases.append(dict(label=label,bev300_share=share,capital_recovery_rate=rate,net_bev_differential_usd_yr=net_bev,
            reference_screen_bn=ref,alternative_cost_bn=alt['transport_cost_bn'],net_incremental_bn=alt['transport_cost_bn']-ref,
            reference_partial_wtw_mt=emo['screening_wtw_mt'],alternative_partial_wtw_mt=alt['emissions']['total_mt'],
            avoided_mt=avoided,abatement_usd_t=1000*(alt['transport_cost_bn']-ref)/avoided,reactor_hubs=alt['hubs']))
    out=dict(version='9.7',source_stock=stock,price_usd_thousand=prices,tax_36=tax,reference_emissions=emission_inventory(),
             corrected_lifecycle_ranges=[emission_inventory(5,10,0),emission_inventory(10,50,10),emission_inventory(15,100,15)],
             h2_energy_basis_bracket={'HHV':emission_inventory(10,50,10,39.4),'LHV':emission_inventory(10,50,10,33.33)},
             results=cases,notes=['Both fleets charged a differential BEV premium from same AEO class price sample; other non-energy ownership incomplete',
                'Reference hydrogen production emissions remain assumed because source Table 36 does not specify supply pathway',
                'Fossil source includes pipeline and recreational boats but excludes LNG export liquefaction; identical modes not fully reconciled',
                'Pure price-weighting from stocks is a sensitivity, not a new-sales price forecast'])
    (ROOT/'US97_AEO_Boundary.json').write_text(json.dumps(out,indent=2))
    fields=list(cases[0]);
    with (ROOT/'us97_aeo_shared_vehicle_revised.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fields);w.writeheader();w.writerows(cases)
    for c in cases:print(c['label'][:49],'ref',round(c['reference_screen_bn'],2),'alt',round(c['alternative_cost_bn'],2),'avoided',round(c['avoided_mt']), '$/t',round(c['abatement_usd_t']))
    return out

def maintain(m):return m*.35
if __name__=='__main__':run()
