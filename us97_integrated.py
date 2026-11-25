#!/usr/bin/env python3
"""Source-weighted EIA2050 + explicit multi-crop + macroalgal nutrient routing.
Economic inputs remain labelled [A]; returns are not permitted untreated HTL
wastewater or claimed agronomically validated soil replenishment.
"""
import json,csv
from pathlib import Path
import us97_circular_feedstocks as C
import us97_aeo_boundary as E
import us95_aeo_reference_bridge as B
ROOT=Path(__file__).resolve().parent

def run():
    if not (ROOT/'US97_AEO_Boundary.json').exists():E.run()
    boundary=json.loads((ROOT/'US97_AEO_Boundary.json').read_text())
    source=boundary['results'][1]
    net_bev=source['net_bev_differential_usd_yr']
    _,a=B.read_source()
    cases={}
    for name,kw,offshore in [
       ('soil_costed_economic_crop',{},False),
       ('soil_costed_no_crop',{'cap_mt':0},False),
       ('crop_no_pyro_soil_credit',{'apply_pyro_to_soil':False},False),
       ('crop_low_nutrient_recovery',{'release_fraction':.5},False),
       ('crop_no_stable_hydrochar',{'allow_stable_hydrochar':False},False),
       ('crop_seaweed_220gw_imposed',{},True),
    ]:
        cases[name]=C.one(name,C.build_params(a,bevpremium=net_bev,**kw),offshore=offshore)
        print(name,'cost',round(cases[name]['annual_cost_bn'],2),'crop',round(cases[name]['crop_htl_mt'],2),'seaweed',round(cases[name]['seaweed_htl_mt'],2))
    # With marine HTL in the imposed offshore deployment, at most an assumed
    # FRACTION of a treated marine nutrient concentrate might pass salinity/
    # heavy-metal and soil application controls; no cost credit in base solver.
    marine=cases['crop_seaweed_220gw_imposed']['marine']['recovered_treated_product_kt']
    land=cases['crop_seaweed_220gw_imposed'];fraction=.5
    possible={e:min(land[e+'_imports_kt'],marine[e]*fraction) for e in ('n','p','k')}
    # Fertilizer displacement in fields forfeits an equal external-sale credit
    # in the original offshore objective: use the actually different farm and offshore market prices.
    # Additional purification/transport/application assumed $0.20bn/yr.
    marine_land=dict(assumed_permit_eligible_fraction=fraction,eligible_treated_marine_npk_to_cropland_kt=possible,
        residual_elemental_imports_kt={e:land[e+'_imports_kt']-possible[e] for e in possible},
        purification_desalting_and_field_logistics_extra_bn=.20,
        avoided_fertilizer_purchase_value_bn=sum(possible[e]*({'n':1.25,'p':2.60,'k':.90}[e])/1000 for e in possible),
        foregone_existing_offshore_fertilizer_sale_credit_bn=sum(possible[e]*({'n':1.00,'p':1.50,'k':.70}[e])/1000 for e in possible),
        extra_cost_after_opportunity_cost_bn=.20+sum(possible[e]*({'n':1.00,'p':1.50,'k':.70}[e])/1000 for e in possible)-sum(possible[e]*({'n':1.25,'p':2.60,'k':.90}[e])/1000 for e in possible),
        note='Hypothetical nutrient reallocation; marine contaminant screening required. Not simultaneously sold and applied. No marine char soil-carbon credit.')
    result=dict(version='9.7',stock_weighted_bev_net_usd_yr=net_bev,
        source_weighted_reference_partial_bn=source['reference_screen_bn'],
        source_weighted_reference_emissions_partial_mt=source['reference_partial_wtw_mt'],
        baseline_non_soil_costed_alternative_bn=source['alternative_cost_bn'],
        scenario=cases,marine_to_land_optional=marine_land,
        limitations=['Feedstock-specific cap and nutrient coefficients hypothetical [A], national cap 166 Mt not a field permit',
         'HTL hydrochar stable C and methane pyrolysis carbon agronomic equivalence unverified',
         'No raw HTL water return. Nutrient recovery implies additional treatment and regulated application.',
         'Marine co-processing HTL yields additive, not measured blended yield or salt-management performance',
         'No hourly reliability or feasible reactor construction schedule demonstrated'])
    (ROOT/'US97_Integrated_Circular_EIA.json').write_text(json.dumps(result,indent=2))
    rows=[]
    for k,r in cases.items():
        rows.append(dict(case=k,system_cost_bn=r['annual_cost_bn'],incremental_vs_aeo_ref_bn=r['annual_cost_bn']-source['reference_screen_bn'],
          avoided_co2e_mt=source['reference_partial_wtw_mt']-r['emissions_wtw_mt'],
          cost_per_tonne_usd=1000*(r['annual_cost_bn']-source['reference_screen_bn'])/(source['reference_partial_wtw_mt']-r['emissions_wtw_mt']),
          crop_mt=r['crop_htl_mt'],marine_htl_mt=r['seaweed_htl_mt'],n_import_kt=r['n_imports_kt'],p_import_kt=r['p_imports_kt'],k_import_kt=r['k_imports_kt']))
    with (ROOT/'us97_integrated_results.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
    return result
if __name__=='__main__':run()
