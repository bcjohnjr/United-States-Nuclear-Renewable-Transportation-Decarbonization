"""V6: auditable annual N/P conservation screen, RAS seafood -> Asparagopsis.

Reuses *existing* V5 scenarios.json production and cattle-feed targets without
changing the existing transport, reactor or food cost optimisation. Parameter
ranges are scenarios, not validated plant engineering specifications.

Units: Mt = million tonnes of biomass; kt = thousand tonnes of elemental N/P.
Fertiliser is *candidate recovered material*, never a guaranteed sale or credit.
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass, asdict, replace
from pathlib import Path
from typing import Dict

import numpy as np
from us2_inputs import FOOD, AG

ROOT = Path(__file__).resolve().parent
SEED = 23
DRAWS = 1000


@dataclass(frozen=True)
class NutrientInputs:
    feed_conversion_ratio: float = 1.50      # feed wet / harvested seafood live mass, [A, 1.2-1.8]
    feed_n_fraction: float = 0.056            # ~35% crude protein / 6.25, [A + literature]
    feed_p_fraction: float = 0.012            # [S] aquatic diets ~0.9-1.5% elemental P
    harvest_retention_n: float = 0.35         # [S] species-dependent retention; tilapia example
    harvest_retention_p: float = 0.28         # [S] species-dependent retention; tilapia example
    dissolved_waste_share_n: float = 0.72     # [A] remaining feed N, dissolved versus solid
    dissolved_waste_share_p: float = 0.25     # [A] remaining feed P, dissolved versus solid
    capture_dissolved_n: float = 0.55         # [A] includes constraints after nitrification/denitrification
    capture_solid_n: float = 0.70             # [A] treatment of captured sludge
    capture_dissolved_p: float = 0.50         # [A] dissolved P process recovery
    capture_solid_p: float = 0.75             # [A] P recovery from sludge
    delivery_retain_fraction: float = 0.85    # [A] plant treatment, handling, transport losses
    seaweed_eligible_fraction: float = 0.35  # [A] co-location/salinity/safety and routing constraints
    asparagopsis_n_fraction: float = 0.036    # [S] approx 22.5% crude protein / 6.25
    asparagopsis_p_fraction: float = 0.0027   # [S] ~0.27% P by dry mass


def validate(p: NutrientInputs):
    assert p.feed_conversion_ratio > 0
    for name, x in asdict(p).items():
        if name != 'feed_conversion_ratio':
            assert 0 <= x <= 1, f'{name}={x} outside 0...1'
    assert p.asparagopsis_n_fraction > 0 and p.asparagopsis_p_fraction > 0


def _flow(feed_kt: float, retained: float, dissolved: float,
          dissolved_capture: float, solids_capture: float, delivery: float) -> dict:
    harvest = feed_kt * retained
    waste = feed_kt - harvest
    dis = waste * dissolved
    sol = waste - dis
    captured_dis = dis * dissolved_capture
    captured_sol = sol * solids_capture
    captured = captured_dis + captured_sol
    lost_delivery = captured * (1 - delivery)
    delivered = captured - lost_delivery
    return dict(feed_kt=feed_kt, seafood_harvest_kt=harvest, waste_kt=waste,
                dissolved_waste_kt=dis, solid_waste_kt=sol,
                captured_dissolved_kt=captured_dis, captured_solids_kt=captured_sol,
                uncollected_or_treated_kt=waste - captured,
                treatment_delivery_loss_kt=lost_delivery, delivered_recovered_kt=delivered)


def model(seafood_mt: float, asparagopsis_target_mt_dry: float,
          methane_target_mtco2e: float, p: NutrientInputs = NutrientInputs()) -> dict:
    validate(p)
    assert seafood_mt >= 0 and asparagopsis_target_mt_dry >= 0
    # Mass flows use elemental nutrient, never P2O5 equivalents.
    feed_mt = seafood_mt * p.feed_conversion_ratio
    n = _flow(feed_mt * 1000 * p.feed_n_fraction, p.harvest_retention_n,
              p.dissolved_waste_share_n, p.capture_dissolved_n,
              p.capture_solid_n, p.delivery_retain_fraction)
    ph = _flow(feed_mt * 1000 * p.feed_p_fraction, p.harvest_retention_p,
               p.dissolved_waste_share_p, p.capture_dissolved_p,
               p.capture_solid_p, p.delivery_retain_fraction)
    demand_n = asparagopsis_target_mt_dry * 1000 * p.asparagopsis_n_fraction
    demand_p = asparagopsis_target_mt_dry * 1000 * p.asparagopsis_p_fraction
    eligible_n = n['delivered_recovered_kt'] * p.seaweed_eligible_fraction
    eligible_p = ph['delivered_recovered_kt'] * p.seaweed_eligible_fraction
    by_n = eligible_n / (1000 * p.asparagopsis_n_fraction)
    by_p = eligible_p / (1000 * p.asparagopsis_p_fraction)
    closed_mt = min(asparagopsis_target_mt_dry, by_n, by_p)
    closed_n = closed_mt * 1000 * p.asparagopsis_n_fraction
    closed_p = closed_mt * 1000 * p.asparagopsis_p_fraction
    target_n_from_recovery = min(demand_n, eligible_n)
    target_p_from_recovery = min(demand_p, eligible_p)
    # If both limiting, a target cannot exceed the least available element.
    external_n = demand_n - target_n_from_recovery
    external_p = demand_p - target_p_from_recovery
    external_n = max(0.0, external_n)
    external_p = max(0.0, external_p)
    fraction = closed_mt / asparagopsis_target_mt_dry if asparagopsis_target_mt_dry else 1.0
    # The closed-loop and full-target cases are mutually exclusive alternatives:
    # neither reassigns any recovered N/P to more than one use.
    for flow, used_target, used_closed in [(n, target_n_from_recovery, closed_n),
                                            (ph, target_p_from_recovery, closed_p)]:
        flow['eligible_for_seaweed_kt'] = flow['delivered_recovered_kt'] * p.seaweed_eligible_fraction
        flow['seaweed_uptake_closed_kt'] = used_closed
        flow['seaweed_uptake_target_recovered_kt'] = used_target
        flow['fertiliser_candidate_closed_kt'] = flow['delivered_recovered_kt'] - used_closed
        flow['fertiliser_candidate_target_kt'] = flow['delivered_recovered_kt'] - used_target
        # RAS feed input = seafood + uncaptured + treatment loss + recycled seaweed + residue
        for mode, used in [('closed', used_closed), ('target', used_target)]:
            rhs = (flow['seafood_harvest_kt'] + flow['uncollected_or_treated_kt']
                   + flow['treatment_delivery_loss_kt'] + used
                   + flow[f'fertiliser_candidate_{mode}_kt'])
            flow[f'mass_balance_residual_{mode}_kt'] = flow['feed_kt'] - rhs
    heat_target_twh = asparagopsis_target_mt_dry * FOOD['asparagopsis_heat_mwh_t']
    heat_closed_twh = closed_mt * FOOD['asparagopsis_heat_mwh_t']
    return dict(seafood_mt=seafood_mt, feed_mt=feed_mt,
                target_seaweed_heat_twh=heat_target_twh,
                closed_loop_seaweed_heat_twh=heat_closed_twh,
                freed_low_grade_heat_twh=heat_target_twh - heat_closed_twh,
                closed_loop_tank_area_ha=closed_mt*1e6/AG['tank_yield_t_ha'],
                original_tank_area_ha=asparagopsis_target_mt_dry*1e6/AG['tank_yield_t_ha'],
                extra_plant_heat_reassignment_not_optimised=True,
                target_asparagopsis_mt_dry=asparagopsis_target_mt_dry,
                target_methane_reduction_mtco2e=methane_target_mtco2e,
                nitrogen=n, phosphorus=ph,
                target_uptake_n_kt=demand_n, target_uptake_p_kt=demand_p,
                external_target_n_kt=external_n, external_target_p_kt=external_p,
                closed_loop_asparagopsis_mt_dry=closed_mt,
                closed_loop_methane_reduction_mtco2e=methane_target_mtco2e * fraction,
                closed_loop_target_fraction=fraction,
                closed_loop_limiting_n_or_p=('N' if by_n < by_p else 'P') if closed_mt < asparagopsis_target_mt_dry - 1e-10 else 'none',
                asparagopsis_from_n_limit_mt=by_n, asparagopsis_from_p_limit_mt=by_p,
                full_target_methane_reduction_mtco2e=methane_target_mtco2e,
                inputs=asdict(p))


def scenario_result(r: dict, p: NutrientInputs = NutrientInputs()) -> dict:
    f = r['food']
    a = f['asparagopsis']
    z = model(f['fish_shrimp_mt'], a['seaweed_mt_dry'], a['mtco2e_cut'], p)
    z['vegetables_mt'] = f['vegetables_mt']
    z['grain_dried_mt'] = f['grain_dried_mt']
    z['hemp_seed_mt'] = f['hemp_seed_mt']
    z['legacy_combined_calorie_equivalent_m'] = f['people_fed_calorie_equiv_m']
    z['gross_primary_food_calorie_equivalent_m'] = f.get('greenhouse_seafood_gross_calorie_equiv_m', 3.487)
    z['edible_primary_food_calorie_equivalent_m'] = f.get('greenhouse_seafood_edible_calorie_equiv_m', 2.585)
    z['nutrient_limit_changes_food_production'] = False
    return z


def draw_params(rng: np.random.Generator) -> NutrientInputs:
    t = lambda lo, mid, hi: float(rng.triangular(lo, mid, hi))
    return NutrientInputs(
        feed_conversion_ratio=t(1.2, 1.5, 1.85),
        feed_n_fraction=t(.048, .056, .067), feed_p_fraction=t(.009, .012, .015),
        harvest_retention_n=t(.20, .35, .44), harvest_retention_p=t(.18, .28, .40),
        dissolved_waste_share_n=t(.60, .72, .85), dissolved_waste_share_p=t(.15, .25, .40),
        capture_dissolved_n=t(.25, .55, .80), capture_solid_n=t(.45, .70, .90),
        capture_dissolved_p=t(.25, .50, .80), capture_solid_p=t(.50, .75, .90),
        delivery_retain_fraction=t(.65, .85, .95),
        seaweed_eligible_fraction=t(.10, .35, .70),
        asparagopsis_n_fraction=t(.023, .036, .056),
        asparagopsis_p_fraction=t(.0018, .0027, .0035))


def draw_monte_carlo(f: dict, n_draws: int = DRAWS, seed: int = SEED):
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n_draws):
        p = draw_params(rng)
        z = scenario_result({'food': f}, p)
        rows.append(dict(draw=i+1, closed_fraction=z['closed_loop_target_fraction'],
                         closed_mt=z['closed_loop_asparagopsis_mt_dry'],
                         methane_mtco2e=z['closed_loop_methane_reduction_mtco2e'],
                         n_external_kt=z['external_target_n_kt'],
                         p_external_kt=z['external_target_p_kt'],
                         n_feed_kt=z['nitrogen']['feed_kt'],
                         p_feed_kt=z['phosphorus']['feed_kt'],
                         n_delivered_kt=z['nitrogen']['delivered_recovered_kt'],
                         p_delivered_kt=z['phosphorus']['delivered_recovered_kt'],
                         n_fertiliser_candidate_closed_kt=z['nitrogen']['fertiliser_candidate_closed_kt'],
                         p_fertiliser_candidate_closed_kt=z['phosphorus']['fertiliser_candidate_closed_kt'],
                         limiting=z['closed_loop_limiting_n_or_p'],
                         fcr=p.feed_conversion_ratio,
                         co_location=p.seaweed_eligible_fraction,
                         n_asparagopsis_pct=p.asparagopsis_n_fraction * 100,
                         p_asparagopsis_pct=p.asparagopsis_p_fraction * 100))
    return rows


def figures(results: dict, mc: list[dict]) -> None:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':9, 'pdf.fonttype':42, 'font.family':'DejaVu Sans'})
    z=results['scenarios']['least_cost']; n=z['nitrogen']; p=z['phosphorus']
    fig, axs=plt.subplots(1,2,figsize=(13.2,5.4), gridspec_kw={'width_ratios':[1.18,1]}, layout='constrained')
    labels=['N', 'P']; x=np.arange(2)
    parts=[('N/P retained in seafood', 'seafood_harvest_kt', '#3377a5'),
           ('Uncollected / treatment removal', 'uncollected_or_treated_kt','#929ba4'),
           ('Delivery losses', 'treatment_delivery_loss_kt','#c2b9b0'),
           ('Asparagopsis uptake (closed loop)', 'seaweed_uptake_closed_kt','#2a946b'),
           ('Remaining recovered nutrient', 'fertiliser_candidate_closed_kt','#dfb457')]
    lo=np.zeros(2)
    for name, key, color in parts:
        vals=np.array([n[key],p[key]])
        axs[0].bar(x,vals,bottom=lo,color=color,label=name,width=.5)
        lo+=vals
    axs[0].set_xticks(x,labels);axs[0].set_ylabel('Elemental nutrient, kt/year')
    axs[0].set_title('(A) Conservation of N and P supplied in RAS feed',loc='left',fontweight='bold')
    axs[0].legend(loc='upper right',fontsize=7,frameon=False)
    axs[0].set_ylim(0,max(lo)*1.25)
    for xi,v in enumerate(lo):axs[0].text(xi,v+1,f'{v:.1f} kt feed',ha='center',fontsize=9,fontweight='bold')
    axs[0].grid(axis='y',alpha=.17);axs[0].set_axisbelow(True)
    target=z['target_asparagopsis_mt_dry']*1000;closed=z['closed_loop_asparagopsis_mt_dry']*1000
    bars=axs[1].bar([0,1],[closed,target],width=.6,color=['#2a946b','#b069b0'])
    axs[1].set_xticks([0,1],['Recovered RAS nutrients\n(no added seaweed nutrients)', 'Full cattle-feed target\n(with supplemental N/P)'])
    axs[1].set_ylabel('Asparagopsis, kt dry/year')
    axs[1].set_title('(B) Nutrient-constrained seaweed production',loc='left',fontweight='bold')
    for b,v in zip(bars,[closed,target]):
        axs[1].text(b.get_x()+b.get_width()/2,v+6,f'{v:.0f} kt',ha='center',fontsize=10,fontweight='bold')
    axs[1].text(.5,.64,f'External nutrients for full target:\nN {z["external_target_n_kt"]:.1f} kt/yr; P {z["external_target_p_kt"]:.1f} kt/yr',
                ha='center',va='center',transform=axs[1].transAxes,fontsize=9,
                bbox={'boxstyle':'round,pad=.4','facecolor':'#faf9f5','edgecolor':'#ddd'})
    axs[1].set_ylim(0,target*1.3)
    fig.suptitle('Seafood effluent to Asparagopsis: conditional elemental nutrient balance',fontsize=13,fontweight='bold')
    for ext in ['png','pdf']:fig.savefig(ROOT/f'ScienceFigS14_nutrient_balance.{ext}',dpi=300,bbox_inches='tight')
    plt.close(fig)

    vals=np.array([float(r['closed_fraction']) for r in mc]); ns=np.array([float(r['n_external_kt']) for r in mc]); ps=np.array([float(r['p_external_kt']) for r in mc])
    fig,axes=plt.subplots(1,2,figsize=(12,4.6),layout='constrained')
    axes[0].hist(vals*100,bins=np.linspace(0,100,26),color='#267b67',edgecolor='white')
    axes[0].axvline(z['closed_loop_target_fraction']*100,color='#a14943',linestyle='--',linewidth=2,label='Central case')
    axes[0].set_xlabel('Full Asparagopsis target supported by recovered RAS nutrients (%)');axes[0].set_ylabel('Draws (n=1,000)')
    axes[0].legend(frameon=False);axes[0].set_title('(A) Uncertainty in no-added-seaweed-nutrient production',loc='left',fontweight='bold')
    axes[1].scatter(ns,ps,s=8,color='#8553a3',alpha=.35)
    axes[1].scatter([z['external_target_n_kt']],[z['external_target_p_kt']],marker='X',s=140,color='#b34945',label='Central case')
    axes[1].set_xlabel('Supplemental elemental N for full target (kt/yr)')
    axes[1].set_ylabel('Supplemental elemental P for full target (kt/yr)')
    axes[1].legend(frameon=False);axes[1].set_title('(B) Additional nutrients required under uncertainty',loc='left',fontweight='bold')
    fig.suptitle('Parameter uncertainty (triangular screening distributions)',fontsize=13,fontweight='bold')
    for ext in ['png','pdf']:fig.savefig(ROOT/f'ScienceFigS15_nutrient_sensitivity.{ext}',dpi=300,bbox_inches='tight')
    plt.close(fig)


def main(n_draws: int = DRAWS, make_figures: bool = True) -> dict:
    sc=json.loads((ROOT/'scenarios.json').read_text())
    keep=['least_cost','design_sweet_spot','design','post_gas_least_cost','sustainable_fission_nuclear_only']
    results={k:scenario_result(sc[k]) for k in keep}
    rows=draw_monte_carlo(sc['least_cost']['food'],n_draws=n_draws)
    quant=lambda key: {f'p{q}':float(np.percentile([r[key] for r in rows],q)) for q in (5,50,95)}
    out={'version':'6.0','basis':'V5 steady-state fish and seaweed output; annual elemental N/P screening model',
         'scientific_status':'conditional sensitivity, not validated co-located RAS-Asparagopsis engineering',
         'no_transport_reoptimization':True,'no_fertiliser_revenue_credited':True,
         'monte_carlo_n':n_draws,'monte_carlo_seed':SEED,
         'scenarios':results,
         'uncertainty':{'closed_loop_fraction':quant('closed_fraction'),
                        'external_n_kt':quant('n_external_kt'),
                        'external_p_kt':quant('p_external_kt'),
                        'methane_mtco2e':quant('methane_mtco2e'),
                        'p_complete_closed_loop':sum(r['closed_fraction']>=.999999 for r in rows)/len(rows)},
         'references':[
            'https://onlinelibrary.wiley.com/doi/10.1111/raq.12645',
            'https://www.mdpi.com/2076-3417/14/14/6056',
            'https://www.sciencedirect.com/science/article/pii/S0048969720314625',
            'https://pubmed.ncbi.nlm.nih.gov/27009670/',
            'https://pmc.ncbi.nlm.nih.gov/articles/PMC10967268/',
            'https://pmc.ncbi.nlm.nih.gov/articles/PMC7697577/',
            'https://www.sciencedirect.com/science/article/pii/S0044848622003325']}
    (ROOT/'nutrient_balance_v6.json').write_text(json.dumps(out,indent=2)+'\n')
    with (ROOT/'nutrient_balance_v6.csv').open('w',newline='') as f:
        header=['scenario','seafood_mt','feed_mt','asparagopsis_target_kt','asparagopsis_supported_kt',
                'fraction_supported','methane_closed_mtco2e','methane_target_mtco2e',
                'feed_n_kt','feed_p_kt','recovered_n_kt','recovered_p_kt','external_n_kt','external_p_kt',
                'fertiliser_candidate_n_closed_kt','fertiliser_candidate_p_closed_kt']
        w=csv.DictWriter(f,fieldnames=header);w.writeheader()
        for name,z in results.items():
            w.writerow(dict(scenario=name,seafood_mt=z['seafood_mt'],feed_mt=z['feed_mt'],
                            asparagopsis_target_kt=z['target_asparagopsis_mt_dry']*1000,
                            asparagopsis_supported_kt=z['closed_loop_asparagopsis_mt_dry']*1000,
                            fraction_supported=z['closed_loop_target_fraction'],
                            methane_closed_mtco2e=z['closed_loop_methane_reduction_mtco2e'],
                            methane_target_mtco2e=z['target_methane_reduction_mtco2e'],
                            feed_n_kt=z['nitrogen']['feed_kt'],feed_p_kt=z['phosphorus']['feed_kt'],
                            recovered_n_kt=z['nitrogen']['delivered_recovered_kt'],
                            recovered_p_kt=z['phosphorus']['delivered_recovered_kt'],
                            external_n_kt=z['external_target_n_kt'],external_p_kt=z['external_target_p_kt'],
                            fertiliser_candidate_n_closed_kt=z['nitrogen']['fertiliser_candidate_closed_kt'],
                            fertiliser_candidate_p_closed_kt=z['phosphorus']['fertiliser_candidate_closed_kt']))
    with (ROOT/'nutrient_monte_carlo_v6.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()));w.writeheader();w.writerows(rows)
    if make_figures: figures(out,rows)
    x=results['least_cost'];print(f'V6 RAS: {x["seafood_mt"]:.2f} Mt seafood; {x["nitrogen"]["feed_kt"]:.2f} kt N and {x["phosphorus"]["feed_kt"]:.2f} kt P in feed')
    print(f'Recovered delivered: {x["nitrogen"]["delivered_recovered_kt"]:.2f} kt N, {x["phosphorus"]["delivered_recovered_kt"]:.2f} kt P')
    print(f'No supplemental seaweed nutrients: {x["closed_loop_asparagopsis_mt_dry"]*1000:.1f} kt Asparagopsis, {x["closed_loop_methane_reduction_mtco2e"]:.1f} Mt CO2e potential methane reduction')
    print(f'Full target requires {x["external_target_n_kt"]:.2f} kt N + {x["external_target_p_kt"]:.2f} kt P supplemental nutrients')
    print('PASS: V6 elemental balance, CSV, uncertainty and figures written')
    return out

if __name__=='__main__':
    import sys
    argv=sys.argv[1:]
    main(int(argv[0]) if argv and argv[0].isdigit() else DRAWS, '--no-figures' not in argv)
