"""V7: transparent community co-production and RAS-to-Asparagopsis process screen.

Inputs are hypotheses, not operational design or validated nationwide forecasts.
The total nutrient balance comes from V6 (not double-counted). Stages for the
RAS nutrient concentrate are represented at process-block resolution without
assuming successful seawater integration, pathogen clearance or feed approval.

Economic screen is an INDEPENDENT community boundary, not an incremental
modification to the transport LP or evidence of a profitable facility.
"""
from __future__ import annotations
import csv, json
from dataclasses import dataclass,asdict,replace
from pathlib import Path
import numpy as np
from us2_inputs import FOOD, AG
from us6_nutrient_balance import scenario_result

ROOT=Path(__file__).resolve().parent

@dataclass(frozen=True)
class CommunityInputs:
    # RAS blowdown/concentrate volume, NOT total internal RAS circulation [A].
    process_water_m3_per_t_seafood: float=10.0
    capture_energy_kwh_m3: float=1.2
    disinfection_energy_kwh_m3: float=0.6
    salinity_conditioning_energy_kwh_m3: float=0.7
    electricity_price_usd_mwh: float=85.0
    treatment_opex_usd_m3_excl_energy: float=1.00
    installed_treatment_usd_per_m3_day: float=3500.0
    treatment_plant_life_years: float=20.0
    wacc: float=0.08
    # Community assets are in a separate financial boundary; illustrative [A].
    greenhouse_installed_usd_ha: float=900_000.0
    greenhouse_opex_usd_t_produce: float=900.0
    ras_installed_usd_per_t_annual_capacity: float=15_000.0
    ras_opex_excl_feed_usd_t_seafood: float=1200.0
    aquafeed_price_usd_t: float=1500.0
    greenhouse_life_years: float=25.0
    ras_life_years: float=20.0
    supplemental_elemental_n_usd_t: float=3000.0
    supplemental_elemental_p_usd_t: float=5000.0
    # Labels are explicit assumptions; no credit for byproducts without permits/quality.
    fertiliser_credit_usd_t: float=0.0


def _crf(r:float,n:float)->float:
    return r/(1-(1+r)**(-n)) if r>0 else 1/n


def evaluate(sc:dict, nz:dict, p:CommunityInputs=CommunityInputs()):
    f=sc['food']; seafood_mt=f['fish_shrimp_mt']; sea_target_mt=f['asparagopsis']['seaweed_mt_dry']
    marine_stream_m3=seafood_mt*1e6*p.process_water_m3_per_t_seafood
    flow_day=marine_stream_m3/365
    # This is separate treated blowdown/solids stream; no assertion all RAS water crosses membranes.
    capture_gwh=marine_stream_m3*p.capture_energy_kwh_m3/1e6
    sanitation_gwh=marine_stream_m3*p.disinfection_energy_kwh_m3/1e6
    salinity_gwh=marine_stream_m3*p.salinity_conditioning_energy_kwh_m3/1e6
    total_gwh=capture_gwh+sanitation_gwh+salinity_gwh
    treatment_capex_bn=flow_day*p.installed_treatment_usd_per_m3_day/1e9
    treatment_annual_bn=treatment_capex_bn*_crf(p.wacc,p.treatment_plant_life_years)
    treatment_opex_bn=marine_stream_m3*p.treatment_opex_usd_m3_excl_energy/1e9
    energy_bn=total_gwh*p.electricity_price_usd_mwh/1e6
    gh_capex_bn=f['greenhouse_ha']*p.greenhouse_installed_usd_ha/1e9
    gh_annual_bn=gh_capex_bn*_crf(p.wacc,p.greenhouse_life_years)
    gh_opex_bn=f['vegetables_mt']*1e6*p.greenhouse_opex_usd_t_produce/1e9
    ras_capex_bn=seafood_mt*1e6*p.ras_installed_usd_per_t_annual_capacity/1e9
    ras_annual_bn=ras_capex_bn*_crf(p.wacc,p.ras_life_years)
    ras_opex_bn=seafood_mt*1e6*p.ras_opex_excl_feed_usd_t_seafood/1e9
    feed_bn=nz['feed_mt']*1e6*p.aquafeed_price_usd_t/1e9
    asp_bn=f['asparagopsis']['cost_bn'] # existing annual seaweed target production assumption, no double count
    added_n_bn=nz['external_target_n_kt']*1000*p.supplemental_elemental_n_usd_t/1e9
    added_p_bn=nz['external_target_p_kt']*1000*p.supplemental_elemental_p_usd_t/1e9
    cost={
        'greenhouse_capital_annual':gh_annual_bn, 'greenhouse_operating':gh_opex_bn,
        'ras_capital_annual':ras_annual_bn,'ras_operations_excluding_feed':ras_opex_bn,
        'aquafeed':feed_bn,'existing_asparagopsis_cultivation_assumption':asp_bn,
        'new_nutrient_plant_capital_annual':treatment_annual_bn,
        'nutrient_plant_operations':treatment_opex_bn,
        'nutrient_treatment_energy':energy_bn,
        'supplemental_elemental_n':added_n_bn,'supplemental_elemental_p':added_p_bn}
    revenue={'vegetables_gross':f['vegetables_value_bn'],'seafood_gross':f['fish_value_bn']}
    vals={
       'scenario': 'full_target_supplemented',
       'process_stages':[
         'Separate freshwater/brackish RAS solids and controlled bleedwater from fish tanks',
         'Mechanically thicken captured solids; independently treat dissolved nitrogen and phosphorus',
         'Stabilize, filter and test nutrient concentrates (pathogens, pharmaceuticals, metals and other contaminants)',
         'Condition nutrient solution to target Asparagopsis salinity, pH, N:P ratio and water-quality limits',
         'Meter nutrient concentrates into isolated seaweed tanks; recirculate and monitor',
         'Treat or dispose of unused streams through permitted routes; test final animal feed independently'
       ],
       'aquaculture_process_water_million_m3_year': marine_stream_m3/1e6,
       'aquaculture_process_water_m3_day':flow_day,
       'capture_energy_gwh':capture_gwh, 'disinfection_energy_gwh':sanitation_gwh,
       'salinity_conditioning_energy_gwh':salinity_gwh, 'total_treatment_energy_gwh':total_gwh,
       'annual_community_cost_bn':sum(cost.values()),'annual_community_gross_sales_bn':sum(revenue.values()),
       'community_operating_margin_before_unmodelled_items_bn':sum(revenue.values())-sum(cost.values()),
       'cost_breakdown_bn':cost,'gross_sales_bn':revenue,
       'greenhouse_installed_capex_bn':gh_capex_bn,'ras_installed_capex_bn':ras_capex_bn,
       'treatment_installed_capex_bn':treatment_capex_bn,
       'not_included':['labour taxes, insurance and land acquisition beyond assumed operating allowances',
                       'water intake/permit costs and disposal liabilities',
                       'distribution and cooling-network capital beyond simple plant assumptions',
                       'independent food/feed product qualification and regulatory approvals',
                       'sale of residual recovered fertilizer or carbon offsets'],
       'physical_validation_status':'conceptual process-flow screen; no demonstrated integrated saline Asparagopsis RAS plant',
       'nutrition':{
           'vegetables_mt':f['vegetables_mt'],'seafood_mt':seafood_mt,
           'gross_direct_food_calorie_equivalent_m':f.get('greenhouse_seafood_gross_calorie_equiv_m', 3.487),
           'edible_assumption_adjusted_calorie_equivalent_m':f.get('greenhouse_seafood_edible_calorie_equiv_m',2.58),
           'hemp_meal_mt':f['hemp_meal_mt'], 'hemp_meal_status':'potential food or feed after processing; excluded from direct-food calorie claim',
           'grain_drying_mt':f['grain_dried_mt'],'grain_status':'drying service; not newly produced food'
       },
       'nutrient':{
           'n_recovered_kt':nz['nitrogen']['delivered_recovered_kt'],
           'p_recovered_kt':nz['phosphorus']['delivered_recovered_kt'],
           'n_eligible_for_seaweed_kt':nz['nitrogen']['eligible_for_seaweed_kt'],
           'p_eligible_for_seaweed_kt':nz['phosphorus']['eligible_for_seaweed_kt'],
           'seaweed_target_mt_dry':sea_target_mt,'nutrient_only_support_mt_dry':nz['closed_loop_asparagopsis_mt_dry'],
           'additional_n_kt':nz['external_target_n_kt'],'additional_p_kt':nz['external_target_p_kt'],
           'n_fertiliser_candidate_after_target_kt':nz['nitrogen']['fertiliser_candidate_target_kt'],
           'p_fertiliser_candidate_after_target_kt':nz['phosphorus']['fertiliser_candidate_target_kt']
       },
       'inputs':asdict(p),
       'transport_cost_bn_unchanged':sc['transport_cost_bn'],
       'transport_objective_includes_community_costs':False,
    }
    return vals


def methane_sensitivity(nz:dict, adoption_multiplier:float, efficacy_multiplier:float,
                        bioactive_retention_multiplier:float, extra_nutrients:bool):
    # These are multiplicative sensitivity factors, not measured nationwide response functions.
    original_target=nz['target_asparagopsis_mt_dry']
    needed=original_target*adoption_multiplier
    supply=original_target if extra_nutrients else nz['closed_loop_asparagopsis_mt_dry']
    coverage=min(1,supply/max(needed,1e-12))
    emission=nz['target_methane_reduction_mtco2e']*adoption_multiplier*efficacy_multiplier*bioactive_retention_multiplier*coverage
    return dict(adoption_multiplier=adoption_multiplier,efficacy_multiplier=efficacy_multiplier,
                bioactive_retention_multiplier=bioactive_retention_multiplier,
                external_nutrients=extra_nutrients,seaweed_demand_mt_dry=needed,
                seaweed_coverage=coverage,conditional_methane_avoided_mtco2e=emission,
                baseline_cattle_emissions_not_removed_twice=True)


def main(write_figures=True):
    s=json.loads((ROOT/'scenarios.json').read_text())
    z=json.loads((ROOT/'nutrient_balance_v6.json').read_text())['scenarios']['least_cost']
    p=CommunityInputs()
    r=evaluate(s['least_cost'],z,p)
    sensitivity={}
    for name,change in {
       'low_process_cost':dict(process_water_m3_per_t_seafood=4.,installed_treatment_usd_per_m3_day=2200.,capture_energy_kwh_m3=0.7,
                               disinfection_energy_kwh_m3=0.3,salinity_conditioning_energy_kwh_m3=0.4),
       'central_process_cost':{},
       'high_process_cost':dict(process_water_m3_per_t_seafood=25.,installed_treatment_usd_per_m3_day=8000.,capture_energy_kwh_m3=2.5,
                                disinfection_energy_kwh_m3=1.2,salinity_conditioning_energy_kwh_m3=2.0,
                                treatment_opex_usd_m3_excl_energy=2.5)}.items():
        sensitivity[name]=evaluate(s['least_cost'],z,replace(p,**change))
    m={
       'full_target_central_conditional':methane_sensitivity(z,1.,1.,1.,True),
       'no_new_seaweed_nutrients_central_conditional':methane_sensitivity(z,1.,1.,1.,False),
       'lower_adoption_and_product_potency_no_supplement':methane_sensitivity(z,.6,.75,.65,False),
       'low_active_compound_no_supplement':methane_sensitivity(z,1.,1.,.5,False),
       'full_target_reduced_potency':methane_sensitivity(z,1.,.8,.7,True)}
    r['sensitivity_process_costs']={k:{'treatment_energy_gwh':v['total_treatment_energy_gwh'],
       'total_community_cost_bn':v['annual_community_cost_bn'],
       'nutrient_plant_annual_cost_bn':sum(v['cost_breakdown_bn'][i] for i in ('new_nutrient_plant_capital_annual','nutrient_plant_operations','nutrient_treatment_energy'))} for k,v in sensitivity.items()}
    r['cattle_methane_scenarios']=m
    r['nationwide_fertilizer_independence_claimed']=False
    r['n_fertilizer_market_reference_mt']=11.4
    r['potential_n_fertilizer_share_percent']=100*z['nitrogen']['fertiliser_candidate_target_kt']/(11.4*1000)
    r['version']='7.0'
    (ROOT/'community_screen_v7.json').write_text(json.dumps(r,indent=2)+'\n')
    with (ROOT/'community_methane_sensitivity_v7.csv').open('w',newline='') as f:
       w=csv.DictWriter(f,fieldnames=['scenario','adoption_multiplier','efficacy_multiplier','bioactive_retention_multiplier','external_nutrients','seaweed_coverage','seaweed_demand_mt_dry','conditional_methane_avoided_mtco2e'])
       w.writeheader()
       for k,v in m.items(): w.writerow({field:k if field=='scenario' else v[field] for field in w.fieldnames})
    if write_figures:
       make_figures(r)
    print(f"V7 community process water {r['aquaculture_process_water_million_m3_year']:.2f} million m3/year, nutrient treatment electricity {r['total_treatment_energy_gwh']:.1f} GWh/year")
    print(f"V7 gross primary food energy equiv {r['nutrition']['gross_direct_food_calorie_equivalent_m']:.3f}m; adjusted {r['nutrition']['edible_assumption_adjusted_calorie_equivalent_m']:.3f}m")
    print('V7 conditional community costs, cattle sensitivities and supplementary figures pass')
    return r


def make_figures(r):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    plt.rcParams.update({'font.size':10,'font.family':'DejaVu Sans','pdf.fonttype':42})
    # S16 stages and energy; annotated as conceptual design to avoid claim of validated site.
    fig,(ax1,ax2)=plt.subplots(2,1,figsize=(12,6.4),gridspec_kw={'height_ratios':[1.9,1]},layout='constrained')
    ax1.axis('off')
    names=['Seafood RAS\nfeed + tanks','Solids capture\n+ concentrate','Microbial +\ncontaminant tests','Isolated saline\nAsparagopsis tanks','Cattle-feed QC\n+ eligible product']
    xs=[0.012,0.212,0.412,0.612,0.812]
    for i,(x,t) in enumerate(zip(xs,names)):
        rect=FancyBboxPatch((x,0.49),.173,.27,boxstyle='round,pad=.01',ec='#277481',fc='#e8f4f1',transform=ax1.transAxes)
        ax1.add_patch(rect);ax1.text(x+.0865,.625,t,ha='center',va='center',fontsize=10,transform=ax1.transAxes)
        if i<4:ax1.annotate('',xy=(x+.195,.625),xytext=(x+.174,.625),arrowprops=dict(arrowstyle='->',lw=1.5,color='#526875'),xycoords=ax1.transAxes)
    ax1.text(.5,.91,'Conceptual nutrient-concentrate handling; no demonstrated national facility or safety approval',ha='center',fontsize=12,fontweight='bold',transform=ax1.transAxes)
    ax1.text(.5,.28,'Outside seaweed inputs: aquafeed supplies the original N/P; supplemental N is required for the full target',ha='center',color='#9e4a33',fontsize=10,transform=ax1.transAxes)
    ax1.text(.5,.10,'Side-stream rejects, brine, biosolids and contaminants must follow permitted treatment or disposal routes',ha='center',fontsize=10,transform=ax1.transAxes)
    vals=[r['capture_energy_gwh'],r['disinfection_energy_gwh'],r['salinity_conditioning_energy_gwh']]
    ax2.barh(['Capture / concentration','Disinfection / monitoring','Salinity conditioning'],vals,color=['#2f7ba1','#579e93','#a3b36c'])
    ax2.set_xlabel('Electricity for treated side-stream (GWh/year; assumption-based)')
    for i,v in enumerate(vals):ax2.text(v+.3,i,f'{v:.1f} GWh',va='center',fontsize=10)
    ax2.set_xlim(0,max(vals)*1.32);ax2.invert_yaxis()
    fig.suptitle('S16 | RAS-to-seaweed nutrient treatment: physical-process and energy screen',fontweight='bold',fontsize=14)
    for ext in ('png','pdf'):fig.savefig(ROOT/f'ScienceFigS16_RAS_process.{ext}',dpi=220,bbox_inches='tight')
    plt.close(fig)
    fig,(a,b)=plt.subplots(1,2,figsize=(11,4.1),layout='constrained')
    labels=['Vegetables\n(raw)','Seafood\n(raw)','Hemp meal\n(potential only)']
    f=r['nutrition']; den=2200*365*1e6
    veg=f['vegetables_mt']*1e9*FOOD['kcal_per_kg_veg']/den
    fish=f['seafood_mt']*1e9*FOOD['kcal_per_kg_fish']/den
    hemp=f['hemp_meal_mt']*1e9*3500/den
    a.bar(range(3),[veg,fish,hemp],color=['#449a69','#4289a4','#c4a268'])
    a.set_xticks(range(3),labels);a.set_ylabel('Million 2,200-kcal/day equivalents')
    a.set_title('(A) Distinguish gross primary food from potential coproduct',loc='left',fontsize=9)
    a.text(1,10,'Hemp excluded\nfrom primary food total',ha='center',fontsize=9)
    a.set_ylim(0,13)
    m=r['cattle_methane_scenarios'];order=['full_target_central_conditional','no_new_seaweed_nutrients_central_conditional','low_active_compound_no_supplement','lower_adoption_and_product_potency_no_supplement']
    x=[m[k]['conditional_methane_avoided_mtco2e'] for k in order]
    b.barh(range(len(order)),x,color=['#74499b','#33996b','#b67f36','#8c9198'])
    b.set_yticks(range(len(order)),['Full target\nconditional','RAS nutrients\nonly','RAS nutrients, half\nactive potency','Reduced adoption,\nefficacy & potency'])
    b.set_xlabel('Conditional avoided enteric emissions (Mt CO2e/yr)');b.invert_yaxis()
    b.set_title('(B) Livestock response remains conditional',loc='left',fontsize=9)
    for i,v in enumerate(x):b.text(v+.4,i,f'{v:.1f}',va='center',fontsize=9)
    b.set_xlim(0,max(x)*1.22)
    fig.suptitle('S17 | Food-energy accounting and livestock response sensitivities',fontsize=12,fontweight='bold')
    for ext in ('png','pdf'):fig.savefig(ROOT/f'ScienceFigS17_food_methane.{ext}',dpi=220,bbox_inches='tight')
    plt.close(fig)

if __name__=='__main__':main()
