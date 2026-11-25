"""U.S. v8.5 exploratory crop-residue-to-HTL + soil carbon/N/P/K model.

All elemental nutrients are expressed as kg per tonne crop residue or kt element per year;
P2O5 and K2O are NOT used. No claim that sewage-like HTL liquor may be spread untreated:
treatment/contaminant screening and permitted recovered concentrates are obligatory.

BT23 mature-market supply of 183 million *short tons* ~=166 Mt metric is a national
screening ceiling, already soil-conservation constrained. Actual field-by-field extraction
must be limited by erosion and long-term soil carbon criteria. Do not add this to the
v8.4 ambiguous 350 Mt "crop & forest residues" without removing the crop component.

Run: python us9_crop_residue.py
"""
from __future__ import annotations
import csv, json, copy
from pathlib import Path
import us2_model as M

ROOT=Path(__file__).resolve().parent
ELEMENTS=('n','p','k')

def with_crop(p=None, supply_mt=166.0, force_fraction=0.0, nutrient_capture=1.0,
              forest_mt=150.0, crop_base_usd_t=None, pyro_for_soil=True,
              stable_soc_per_t=None, nitrogen_from_legumes=False):
    """Paired counterfactuals (same forest/grass resource cap) prevent double-counting."""
    p=copy.deepcopy(p or M.default_params())
    d=p['CROP_RESIDUE'];d['enabled']=True;d['cap_mt']=supply_mt
    d['collect_min_mt']=min(supply_mt,max(0.0,supply_mt*force_fraction))
    if stable_soc_per_t is not None:d['stable_soc_c_t_per_dry_t']=stable_soc_per_t
    if crop_base_usd_t is not None:d['delivered_usd_t']=crop_base_usd_t
    if nitrogen_from_legumes:
        d['nitrogen_replacement_path']='cover-crop legume fixation, 60 kg available N/ha, $100/ha net annual establishment [A]'
        d['legume_available_n_kg_ha']=60.0
        d['nutrient_replacement_usd_per_kg']['n']=100.0/60.0
    for k in ELEMENTS:d['recovered_fraction'][k]*=nutrient_capture
    npk=sum(d['elemental_kg_t'][k]*(1-d['recovered_fraction'][k])*d['nutrient_replacement_usd_per_kg'][k] for k in ELEMENTS)
    d['incremental_npk_import_usd_t']=npk
    crop_allin=d['delivered_usd_t']+d['wastewater_treatment_usd_t']+d['hydrochar_testing_transport_usd_t']+npk
    p['BIOMASS']['tiers']=[('Crop straw, stover and crop-processing husks: field-screened',supply_mt,crop_allin),
         ('Forest and other non-crop residual supply (assumed, independently capped)',forest_mt,85.0),
         ('Perennial grasses and energy cane',200.0,100.0)]
    for i,(name,cap,value) in enumerate(p['CARBON']):
        if name.startswith('Soil amendment'):
            p['CARBON'][i]=[name,0.0 if not pyro_for_soil else 10.0,
                -d['pyro_carbon_soil_application_usd_t']]
            break
    return p

def row(name,r,params):
    so=r.get('crop_residue_soil') or {}; base=r['petroleum']['prices']['late_2025']['pretax_bn'] + r['petroleum']['pipeline_gas_bn']
    return {'scenario':name,'transport_cost_bn':r['transport_cost_bn'],
            'petroleum_late2025_bn':base,'cost_saving_pct':100*(1-r['transport_cost_bn']/base),
            'crop_htl_mt':so.get('feedstock_mt',0),'crop_htl_liquids_twh':so.get('htl_biocrude_fuel_twh',0),
            'crop_hydrochar_return_mt':so.get('hydrochar_return_mt',0),
            'methane_carbon_to_soil_mt':so.get('methane_carbon_return_mt',0),
            'cover_crop_stable_carbon_mt':so.get('cover_crop_extra_stable_c_mt',0),
            'soil_c_gap_mt':max(0,-so.get('carbon_balance_surplus_mt',0)),
            'n_returned_kt':so.get('nutrients',{}).get('n',{}).get('returned_kt',0),
            'p_returned_kt':so.get('nutrients',{}).get('p',{}).get('returned_kt',0),
            'k_returned_kt':so.get('nutrients',{}).get('k',{}).get('returned_kt',0),
            'n_import_kt':so.get('nutrients',{}).get('n',{}).get('imported_kt',0),
            'p_import_kt':so.get('nutrients',{}).get('p',{}).get('imported_kt',0),
            'k_import_kt':so.get('nutrients',{}).get('k',{}).get('imported_kt',0),
            'saskatchewan_kcl_import_kt':so.get('nutrients',{}).get('k',{}).get('imported_kt',0)/(39.0983/(39.0983+35.45)),
            'fertilizer_replacement_bn':so.get('fertilizer_cost_bn',0),
            'legume_n_area_mha':(so.get('nutrients',{}).get('n',{}).get('imported_kt',0)/params['CROP_RESIDUE']['legume_available_n_kg_ha']) if params['CROP_RESIDUE'].get('legume_available_n_kg_ha') else 0.0,
            'hubs':r['hubs'],'electricity_enduse_twh':r['enduse']['el_total'],
            'h2_enduse_direct_mt':r['enduse']['h2_mt_direct'],
            'model_reconciliation_residual_bn':r['objective_reconciliation']['residual_bn']}

def run(write=True):
    cases={
        'v8.5_truck_corrected_v8.4_resource_pools':None,
        'paired_without_crop':dict(supply_mt=0),
        'paired_crop_economic_optimum':dict(supply_mt=166),
        'paired_crop_half_sustainable_cap_forced':dict(supply_mt=83,force_fraction=1.0),
        'paired_crop_full_sustainable_cap_forced':dict(supply_mt=166,force_fraction=1.0),
        'paired_crop_full_low_nutrient_recovery':dict(supply_mt=166,force_fraction=1.0,nutrient_capture=0.5),
        'paired_crop_full_zero_nutrient_recovery':dict(supply_mt=166,force_fraction=1.0,nutrient_capture=0.0),
        'paired_crop_full_cover_crops_only':dict(supply_mt=166,force_fraction=1.0,pyro_for_soil=False),
        'paired_crop_full_high_soc_need':dict(supply_mt=166,force_fraction=1.0,stable_soc_per_t=0.10),
        'paired_crop_full_high_collection_cost':dict(supply_mt=166,force_fraction=1.0,crop_base_usd_t=90),
        'paired_crop_full_very_high_collection_cost':dict(supply_mt=166,force_fraction=1.0,crop_base_usd_t=125),
        'paired_crop_full_legume_n_source':dict(supply_mt=166,force_fraction=1.0,nitrogen_from_legumes=True),
    }
    results=[];details={}
    for name,setup in cases.items():
        p=M.default_params() if setup is None else with_crop(**setup)
        r=M.solve_learning(p,scenario='least_cost',blend_vol=0.0,osw_scale=0,kelp_force=False)
        z=row(name,r,p)
        if abs(z['model_reconciliation_residual_bn'])>1e-7:raise AssertionError((name,z['model_reconciliation_residual_bn']))
        if z['soil_c_gap_mt']>1e-8:raise AssertionError((name,'soc gap'))
        if name.startswith('paired_crop_full') and abs(z['crop_htl_mt']-166)>1e-7:raise AssertionError((name,'forced cap'))
        results.append(z)
        details[name]={**z,'soil':r.get('crop_residue_soil',{}),
            'biomass_tiers':p['BIOMASS']['tiers'],'crop_parameters':p['CROP_RESIDUE'],
            'route_mt':r['routes_mt'],'costs_bn':r['costs_bn'],
            'carbon_alloc':r['carbon_alloc'],
            'method':'simultaneous least-cost transport LP with explicit crop-HTL and soil-carbon constraints; fixed NPK deficits paid in tier delivered cost'}
    if write:
        (ROOT/'us9_crop_residue_results.json').write_text(json.dumps(details,indent=2))
        with (ROOT/'us9_crop_residue_scenarios.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
        print(f'Saved {len(results)} paired scenarios, with crop NPK and soil-carbon audit')
    return results

if __name__=='__main__':
    for d in run():
        print(f"{d['scenario']:<53} cost ${d['transport_cost_bn']:.2f}bn crop {d['crop_htl_mt']:.2f} Mt, KCl {d['saskatchewan_kcl_import_kt']:.1f} kt")
