#!/usr/bin/env python3
"""V9.7 scenario-level national crop-residue/seaweed/soil NPK screen.

Purpose: test every named candidate crop residual class in the *same* linear
programme, allowing the objective to decline uneconomic biomass, subject to an
aggregate 166 Mt dry/yr national ceiling AND class/group capacity ceilings.
The class-specific caps/chemistry/capture costs below are hypothetical analyst
bounds [A], not DOE state-level harvest estimates or lab-tested HTL recoveries.
The DOE BT23 mature-market crop category is a NATIONAL screening ceiling only.
Never add this set on top of the older 350 Mt mixed crop-and-forest tiers.

Units: Mt dry biomass; kt elemental N, P, K; Mt stable-equivalent C; US$ bn/yr.
Raw process liquor is NOT land-spread. Treated nutrients only after wastewater
purification, salinity/metal testing, permitted rates and field soil assessment.
Separate cofeed routes use additive yields; no assumed co-HTL synergy credit.
"""
from __future__ import annotations
import copy,csv,json
from pathlib import Path
import us2_model as M
import us95_aeo_reference_bridge as A
import us96_aeo_shared_assumptions as P
import us2_inputs as I

ROOT=Path(__file__).resolve().parent
# All category quantities, nutrient contents, recovery and collection costs
# are explicit [A] assumptions, not claims of USDA/DOE category-level supply.
# Corn stover below explicitly EXCLUDES cobs/husks counted in a separate tier.
CANDIDATES=[
  ('Corn stalks and leaves (excluding cobs/husks)','corn',80,52,7.0,1.3,11.0,.065),
  ('Corn cobs and husks (separate field/process stream)','corn',26,46,5.2,1.0,6.0,.045),
  ('Wheat straw and chaff','wheat',45,55,5.4,1.0,10.0,.065),
  ('Rice straw','rice',14,62,6.2,1.0,15.0,.070),
  ('Rice husks (mill residue)','rice',8,45,4.0,0.7,5.0,.020),
  ('Barley, oat and rye straw','small_grain',16,61,6.1,1.0,11.0,.075),
  ('Grain sorghum stalks and leaves','sorghum',16,60,6.1,1.0,10.0,.075),
  ('Cotton stalks','cotton',15,70,8.5,1.5,12.0,.075),
  ('Soybean stems, pods and processing hulls','soybean',20,59,9.5,1.7,12.0,.065),
  ('Sugarcane bagasse and field trash','sugarcane',20,52,6.2,1.0,7.5,.040),
  ('Orchard and nut-crop pruning residues','orchard',20,83,5.5,1.0,6.5,.040),
  ('Vegetable and fruit processing plant solids','processing',15,49,13.0,2.8,12.0,.010),
  ('Other food-crop stalks, peels and harvest residues','other',18,78,9.0,1.5,9.0,.060),
]
GROUP_CAP={'corn':105.0,'rice':20.0}
NPK_REC={'n':0.50,'p':0.75,'k':0.80}
NPK_WATER={'n':0.85,'p':0.25,'k':0.95}

def build_params(a=None,bevpremium=None,collect_floor_mt=0.0,release_fraction=1.0,
                 apply_pyro_to_soil=True,allow_stable_hydrochar=True,
                 cap_mt=166.0,offshore=False):
    if a is None: _,a=A.read_source()
    p,_=A.config(a,freight='eia_medium_heavy')
    if bevpremium is None:
        d=json.loads((ROOT/'US96_Shared_2050_Screen.json').read_text())['results'][1]
        bevpremium=d['bev_cost_net_usd_yr_2026usd']
    p['VEH']['ldv_bev_net_usd_yr']=float(bevpremium)
    cr=p['CROP_RESIDUE'];cr['enabled']=True;cr['cap_mt']=cap_mt
    cr['collect_min_mt']=float(collect_floor_mt)
    cr['feedstocks']=[]
    cr['group_caps_mt']=GROUP_CAP
    cr['hydrochar_stable_fraction']=cr['hydrochar_stable_fraction'] if allow_stable_hydrochar else 0.0
    cr['methane_carbon_stable_fraction']=cr['methane_carbon_stable_fraction'] if apply_pyro_to_soil else 0.0
    # Soil pyrocarbon is a COSTED service, not positive product revenue.
    # The mass is still allocated once through the carbon-market conservation equation.
    for market in p['CARBON']:
        if market[0].startswith('Soil amendment'):
            market[2]=-cr['pyro_carbon_soil_application_usd_t']
    if not apply_pyro_to_soil:
        for market in p['CARBON']:
            if market[0].startswith('Soil amendment'):market[1]=0.0
    # Crop and non-crop pools are disjoint; the latter have unverified [A]
    # capacities. They are reported separately and NOT added to DOE's 166 Mt.
    tiers=[]
    for name,group,cap,cost,n,p_el,k,soc in CANDIDATES:
        nutrient={'n':n,'p':p_el,'k':k}
        capture={e:NPK_REC[e]*release_fraction for e in ('n','p','k')}
        record=dict(name=name,group=group,cap_mt=float(cap),elemental_kg_t=nutrient,
                    recovered_fraction=capture,wastewater_recovered_share=NPK_WATER,
                    stable_soc_c_t_per_dry_t=soc,
                    delivered_usd_t=cost,source_status='[A] uncalibrated category screening capacity')
        cr['feedstocks'].append(record)
        fert=sum(nutrient[e]*(1-capture[e])*cr['nutrient_replacement_usd_per_kg'][e] for e in ('n','p','k'))
        tiers.append((name,cap,cost+cr['wastewater_treatment_usd_t']+cr['hydrochar_testing_transport_usd_t']+fert))
    tiers.extend([
        ('Verified-separate NON-CROP forest residues [A cap]',150.,85.),
        ('Perennial grasses / energy cane [A cap]',200.,100.),
    ])
    p['BIOMASS']['tiers']=tiers
    return p

def marine_bookkeeping(result,p):
    # Offshore macroalgae conversion is already in model variables (kh/kp).
    # HTL marine mass can produce nutrient rich process liquor and hydrochar;
    # PBTL is not assumed to produce HTL hydrochar or HTL liquid effluent.
    spec=p['SEAWEED_PROCESS']; zones=I.SEAWEED
    inventory={e:0.0 for e in ('n','p','k')}
    recovered={e:0.0 for e in ('n','p','k')}
    for z in zones:
        mass=result['x'].get('kh_'+z[0],0.0)
        # z[7] = model's seaweed N mass fraction; S.p / S.k are uniform [A].
        for e,frac,rec in [('n',z[7],spec['n_rec']),('p',spec['p'],spec['p_rec']),('k',spec['k'],spec['k_rec'])]:
            inventory[e]+=mass*1000*frac
            recovered[e]+=mass*1000*frac*rec
    marine_htl_mt=sum(result['x'].get('kh_'+z[0],0) for z in zones)
    marine_pbtl_mt=sum(result['x'].get('kp_'+z[0],0) for z in zones)
    # No untested seaweed-derived recovered NPK is double-credited against
    # cropland fertilizer; marine product has an existing fertilizer credit.
    return dict(seaweed_htl_mt=marine_htl_mt,seaweed_pbtl_mt=marine_pbtl_mt,
        additive_marine_hydrochar_mt=marine_htl_mt*.12,
        n_p_k_htl_feedstock_kt=inventory,recovered_treated_product_kt=recovered,
        crop_field_npk_offset_kt={e:0.0 for e in inventory},
        marine_salts_and_metals_screen='Mandatory; no application to cropland without testing/permits',
        nutrient_accounting='Existing offshore HTL fertilizer coproduct credit remains allocated outside the crop NPK balance; no double credit or immediate soil return assumed')

def one(name,p,offshore=False):
    kw=dict(scenario='design',blend_vol=0.0,osw_scale={z:1 for z in ('nca','cca','or','wa','gom','la')},kelp_force=True) if offshore else dict(scenario='least_cost',blend_vol=0.0,osw_scale=0.0,kelp_force=False)
    r=M.solve_learning(p,**kw)
    crop=r.get('crop_residue_soil') or {}
    marine=marine_bookkeeping(r,p)
    result=dict(case=name,annual_cost_bn=r['transport_cost_bn'],emissions_wtw_mt=r['emissions']['total_mt'],hubs=r['hubs'],
        onshore_gw=r['gw']['onshore_wind'],offshore_gw=r['gw']['offshore_wind'],
        crop_htl_mt=crop.get('feedstock_mt',0),crop_htl_liquid_twh=crop.get('htl_biocrude_fuel_twh',0),
        mixed_residue_liquid_twh=r['liquids_twh']['residues_and_grasses'],
        crop_hydrochar_mt=crop.get('hydrochar_return_mt',0),
        stable_soil_c_need_mt=crop.get('stable_soil_c_required_mt',0),
        stable_hydrochar_c_mt=crop.get('hydrochar_stable_c_mt',0),
        stable_pyrolysis_c_mt=crop.get('methane_carbon_stable_mt',0),
        cover_crop_stable_c_mt=crop.get('cover_crop_extra_stable_c_mt',0),
        fertilizer_cost_bn=crop.get('fertilizer_cost_bn',0),
        seaweed_htl_mt=marine['seaweed_htl_mt'],seaweed_pbtl_mt=marine['seaweed_pbtl_mt'],
        seaweed_hydrochar_screen_mt=marine['additive_marine_hydrochar_mt'],
        objective_residual_bn=r['objective_reconciliation']['residual_bn'],
        biomass_case_note='Local crop feedstock caps and elemental nutrient coefficients are analyst assumptions; not calibrated state-by-state USDA supplies')
    for e in ('n','p','k'):
        b=crop.get('nutrients',{}).get(e,{})
        for nm,key in [('removed','removed_kt'),('water','wastewater_recovered_kt'),('char','hydrochar_recovered_kt'),('imports','imported_kt')]:
            result[f'{e}_{nm}_kt']=b.get(key,0)
        result[f'{e}_seaweed_treated_product_kt']=marine['recovered_treated_product_kt'][e]
    result['selected']=crop.get('selected_feedstocks',[])
    result['marine']=marine
    assert result['crop_htl_mt']<=p['CROP_RESIDUE']['cap_mt']+1e-7
    assert abs(result['objective_residual_bn'])<1e-5
    for e in ('n','p','k'):
        assert abs(result[f'{e}_removed_kt']-result[f'{e}_water_kt']-result[f'{e}_char_kt']-result[f'{e}_imports_kt'])<1e-6
    assert result['stable_hydrochar_c_mt']+result['stable_pyrolysis_c_mt']+result['cover_crop_stable_c_mt']+1e-6>=result['stable_soil_c_need_mt']
    return result

def main():
    _,a=A.read_source()
    pbase,_=A.config(a,freight='eia_medium_heavy')
    central=json.loads((ROOT/'US96_Shared_2050_Screen.json').read_text())['results'][1]
    pbase['VEH']['ldv_bev_net_usd_yr']=central['bev_cost_net_usd_yr_2026usd']
    base=M.solve_learning(pbase,scenario='least_cost',blend_vol=0.0)
    cases=[dict(case='AEO shared-vehicle-price base with legacy mixed residue tiers',r=dict(annual_cost_bn=base['transport_cost_bn'],emissions_wtw_mt=base['emissions']['total_mt'],hubs=base['hubs'])),]
    specs=[
       ('CROP national cap 166 Mt, choose if economic',dict()),
       ('CROP no HTL residue collection permitted',dict(cap_mt=0)),
       ('CROP 166 Mt mandatory physical ceiling test',dict(collect_floor_mt=166)),
       ('CROP half recovered nutrient efficiencies',dict(release_fraction=.5)),
       ('CROP pyrolysis carbon NOT soil equivalent',dict(apply_pyro_to_soil=False)),
       ('CROP hydrochar stable C credit excluded',dict(allow_stable_hydrochar=False)),
    ]
    outputs=[]
    for name,kw in specs:
        p=build_params(a,bevpremium=central['bev_cost_net_usd_yr_2026usd'],**kw)
        result=one(name,p)
        print(name, 'cost',round(result['annual_cost_bn'],2),'crop',round(result['crop_htl_mt'],2),'NPK',*[round(result[e+'_imports_kt']) for e in ('n','p','k')])
        outputs.append(result)
    p=build_params(a,bevpremium=central['bev_cost_net_usd_yr_2026usd'])
    try:
        seaweed=one('CROP + imposed six-zone 220 GW offshore seaweed sensitivity',p,offshore=True)
        outputs.append(seaweed)
        print('marine',seaweed['seaweed_htl_mt'],seaweed['seaweed_pbtl_mt'])
    except Exception as e:
        print('offshore scenario could not be calculated:',repr(e))
    rows=[{k:v for k,v in r.items() if k not in ('selected','marine')} for r in outputs]
    fields=list(rows[0]);assert all(set(r)==set(fields) for r in rows)
    with (ROOT/'us97_crop_seaweed_npk_scenarios.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fields);w.writeheader();w.writerows(rows)
    (ROOT/'us97_crop_seaweed_npk_results.json').write_text(json.dumps(dict(
        version='9.7',baseline=cases[0],national_cap_mt=166.0,feedstock_category_caps_provenance='[A] aggregate distribution hypothetical, NOT DOE category-level data',
        fertilizer_elements='N,P,K elemental; fertilizer oxide and KCl equivalent conversions separate',
        marine_additive_htl_cofeed='Marine and terrestrial HTL treated as additive yield screen; no yield enhancement from mixing credited',
        cases=outputs),indent=2))
    print('wrote',len(outputs),'circular scenarios')
    return outputs

if __name__=='__main__':main()
