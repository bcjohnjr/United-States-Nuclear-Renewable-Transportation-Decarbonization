#!/usr/bin/env python3
"""V9.14 audited paired 2050 screening MC with independently sampled HTL yield and crop delivery cost.

Uses assumed uniform screening ranges, not statistically calibrated empirical distributions.
Per-draw field emissions screen substitutes for the inherited generic crop-fuel CI.
Core non-crop thermal/electric parameters remain at common system assumptions unless sampled.
"""
import random,csv,json,sys
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
import us97_circular_feedstocks as C
import us97_aeo_boundary as E
import us95_aeo_reference_bridge as B
import us2_model as M
from us99_agricultural_accounts import integrated_lca,plant_available,carbon_land
R=Path(__file__).resolve().parent

def run(n=1000,seed=913):
    if n<1:raise ValueError('n must be positive')
    rng=random.Random(seed);_,a=B.read_source()
    s=json.loads((R/'US97_AEO_Boundary.json').read_text())['results'][1]
    price=E.V.vehicle_prices();output=[];invalid=0
    for j in range(n):
        bev=s['net_bev_differential_usd_yr']+rng.uniform(-200,300)
        oil=rng.uniform(.7,1.4);power=rng.uniform(.78,1.38);reactor=rng.uniform(.8,1.55)
        delivery=rng.uniform(0,80) # surcharge, not treatment/nutrient cost multiplier
        cap_mt=166*rng.uniform(0,1);process_recovery=rng.uniform(.35,.8)
        retention=rng.uniform(.6,1.0);plant_fraction=rng.uniform(.4,1.0)
        area_mha=rng.uniform(18,40);soc_tcha=rng.uniform(.45,1.0)
        fossil=rng.uniform(.55,.85);scope=rng.uniform(0,36);h2ci=rng.uniform(0,15)
        grid=rng.uniform(10,100);upstream=rng.uniform(5,15)
        htl_yield=rng.uniform(1.2,3.0)
        collection_emis=rng.uniform(.010,.040)
        legacy_crop_ci=rng.uniform(7,13) # hypothetical route CI is adjusted into legacy emissions before the matching subtraction
        field_rate=rng.uniform(-.05,.05)
        p=C.build_params(a,bevpremium=bev,cap_mt=cap_mt,
            release_fraction=process_recovery,apply_pyro_to_soil=False,allow_stable_hydrochar=False)
        chain={e:dict(process_recovery=C.NPK_REC[e]*process_recovery,
            treatment_storage_retention=retention,plant_available_field_fraction=plant_fraction) for e in 'npk'}
        p=carbon_land(plant_available(p,chain),area_mha*1e6,soc_tcha)
        p['ROUTES']['htl']['mwh_t']=htl_yield
        for k in ('onshore_wind','solar','lwr_smr'):p['ELEC'][k]*=power
        p['capex_mult']=reactor
        for i,(name,cap,cost) in enumerate(p['BIOMASS']['tiers']):
            if i<len(C.CANDIDATES):
                p['BIOMASS']['tiers'][i]=(name,cap,cost+delivery)
        try:r=M.solve_learning(p,scenario='least_cost',blend_vol=0)
        except RuntimeError:
            invalid+=1;continue
        cr=r.get('crop_residue_soil',{});
        c={'case':f'uncertainty_{j}','emissions_wtw_mt':r['emissions']['total_mt'],
            'crop_htl_mt':cr.get('feedstock_mt',0),
            'crop_htl_liquid_twh':cr.get('htl_biocrude_fuel_twh',0),
            'mixed_residue_liquid_twh':r['liquids_twh']['residues_and_grasses'],
            'crop_hydrochar_mt':cr.get('hydrochar_return_mt',0),
            'stable_pyrolysis_c_mt':cr.get('methane_carbon_stable_mt',0),
            'cover_crop_stable_c_mt':cr.get('cover_crop_extra_stable_c_mt',0)}
        for e in 'npk':
            b=cr.get('nutrients',{}).get(e,{})
            for k,src in [('imports','imported_kt'),('water','wastewater_recovered_kt'),('char','hydrochar_recovered_kt')]:
                c[e+'_'+k+'_kt']=b.get(src,0)
        lca=integrated_lca(c,assumed_crop_ci_g_mj=legacy_crop_ci,
            collection_tco2_t=collection_emis,
            field_counterfactual_mt=field_rate*c['crop_htl_mt'])
        ref_energy=a['eia_energy_exp_2050_bn_2025_usd']*1.025*(fossil*oil+(1-fossil)*power)
        other=(a['eia_ldv_phev_m']*((price['phev']-price['ice'])*1000/15-250*.35)+
               a['eia_ldv_hev_m']*((price['hev']-price['ice'])*1000/15-250*.35))/1000*1.025
        base_truck=(a['eia_medheavy_electric_m']*p['VEH']['bev_truck_net_usd_yr']+
            a['eia_medheavy_fcev_m']*p['VEH']['fcev_truck_net_usd_yr'])/1000
        reference=(ref_energy-E.V.excise_tax_screen()['illustrative_tax_bn']*.5+
            a['ldv_2050_bev_m']*bev/1000+other+base_truck+a['ldv_2050_bev_m']*.1+scope)
        reference_ghg=E.emission_inventory(upstream,grid,h2ci)['screening_wtw_mt']
        avoided=reference_ghg-lca['replaced_route_screen_mt']
        if avoided<=0:invalid+=1;continue
        row=dict(draw=j,reference_bn=reference,alternative_bn=r['transport_cost_bn'],
            incremental_bn=r['transport_cost_bn']-reference,avoided_mt=avoided,
            abatement_usd_t=1000*(r['transport_cost_bn']-reference)/avoided,
            legacy_alt_emissions_mt=r['emissions']['total_mt'],
            crop_lca_substituted_alt_mt=lca['replaced_route_screen_mt'],
            crop_lca_upper_addition_mt=lca['maximal_gross_addition_screen_mt'],
            crop_mt=c['crop_htl_mt'],cover_c_mt=c['cover_crop_stable_c_mt'],
            htl_liquid_yield_mwh_dry_t=htl_yield,
            extra_crop_delivery_usd_dry_t=delivery,
            petroleum_price_mult=oil,bev_premium_usd_yr=bev,power_mult=power,
            reactor_mult=reactor,crop_cap_mt=cap_mt,process_recovery_scale=process_recovery,
            treatment_retention=retention,plant_availability=plant_fraction,
            cover_land_mha=area_mha,soil_carbon_tcha_yr=soc_tcha,
            reference_fossil_cost_share=fossil,reference_scope_bn=scope,
            reference_h2_kgco2_kg=h2ci,upstream_gco2_mj=upstream,grid_gco2_kwh=grid,
            crop_collection_tco2_t=collection_emis,legacy_crop_route_gco2_mj=legacy_crop_ci,
            audited_model_route_ci_gco2_mj=M.CI_RESIDUES_GRASSES_G_MJ,
            field_counterfactual_tco2_t=field_rate)
        output.append(row)
        if (j+1)%100==0:print('V914 paired MC',j+1,'/',n,'infeasible',invalid,flush=True)
    if not output:raise RuntimeError('No feasible draws')
    with (R/'us914_paired_uncertainty.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,list(output[0]));w.writeheader();w.writerows(output)
    mat=lambda k:np.array([x[k] for x in output])
    vals=mat('abatement_usd_t')
    variables=('htl_liquid_yield_mwh_dry_t','extra_crop_delivery_usd_dry_t','petroleum_price_mult',
        'bev_premium_usd_yr','power_mult','reactor_mult','crop_cap_mt','process_recovery_scale',
        'treatment_retention','plant_availability','cover_land_mha','soil_carbon_tcha_yr',
        'reference_fossil_cost_share','reference_scope_bn','reference_h2_kgco2_kg',
        'crop_collection_tco2_t','field_counterfactual_tco2_t')
    influence={k:round(float(spearmanr(mat(k),vals).statistic),3) for k in variables}
    summary=dict(version='9.14',route_ci_audit='10 g/MJ fixed in model; sampled route-CI hypothetical is adjusted before crop-specific removal, so sampled CI does not spuriously alter totals',seed=seed,n_requested=n,n_feasible=len(output),n_infeasible=invalid,
        p05_usd_t=float(np.percentile(vals,5)),median_usd_t=float(np.median(vals)),
        p95_usd_t=float(np.percentile(vals,95)),fraction_alt_cheaper=float(np.mean(mat('incremental_bn')<0)),
        median_crop_mt=float(np.median(mat('crop_mt'))),zero_crop_fraction=float(np.mean(mat('crop_mt')<1e-8)),
        rank_correlations=influence,
        caution='Uncalibrated uniform screening ranges, not forecasts. Crop supply and the reference cost boundary remain empirically incomplete; simultaneous variation is not proof of physical yield/energy correlations.')
    (R/'US914_Paired_Uncertainty_Summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print('V914 SUMMARY',json.dumps(summary,indent=2),flush=True)
    return summary
if __name__=='__main__':run(int(sys.argv[1]) if len(sys.argv)>1 else 1000)
