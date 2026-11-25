"""Version 9.1: comparator, vehicle premium, no-blending and Grid Harvester sensitivity output.
No forecast probabilities: model draws are conditional assumed input distributions.
"""
from pathlib import Path
import csv,json,math
import numpy as np
from scipy.stats import spearmanr
from scipy.optimize import brentq
import us2_model as M
from grid_harvester import energy,turning
ROOT=Path(__file__).resolve().parent
S=json.loads((ROOT/'scenarios.json').read_text())
B=S['least_cost']['petroleum']
P=B['prices']['late_2025']['pretax_bn']+B['pipeline_gas_bn']
G=M.I.BASE['gasoline_mbd']*42e6*365*(M.I.PRICES['late_2025']['gasoline']-M.I.TAX['gasoline'])/1e9
cases={k:S[k]['transport_cost_bn'] for k in ['least_cost','design_sweet_spot','design','post_gas_least_cost','sustainable_fission_nuclear_only','sustainable_fission_nuclear_only_premium','least_cost_blend20_sensitivity']}
# This sensitivity changes fuel use but NOT new vehicle purchase costs or fleet composition.
rows=[]
for reduction in [0,.05,.10,.15,.20,.25,.30,.35]:
    ref=P-reduction*G
    rows.append({'gasoline_fuel_efficiency_improvement_pct':round(reduction*100,2),'petroleum_comparator_bn':ref,
    'least_cost_transport_bn':cases['least_cost'],'saving_bn':ref-cases['least_cost'],'saving_pct':100*(ref-cases['least_cost'])/ref,
    'fully_specified_2050_ice_costs':False})
with (ROOT/'us91_2050_reference_sensitivity.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
# Full reoptimisation for marginal annual BEV premium (not linear extrapolation of an unrelated case).
vrows=[]
def run_premium(prem):
    p=M.default_params();p['VEH']['ldv_bev_net_usd_yr']=prem
    r=M.solve_learning(p,scenario='least_cost',blend_vol=0)
    return r['transport_cost_bn'],r['hubs']
for premium in [-400,-200,0,100,200,300,400,500,700]:
    c,h=run_premium(premium)
    vrows.append({'bev_net_premium_usd_per_car_year':premium,'system_cost_bn':c,'saving_vs_2025petrol_pct':100*(P-c)/P,'hubs':h})
with (ROOT/'us91_bev_premium.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=vrows[0]);w.writeheader();w.writerows(vrows)
be=brentq(lambda x:run_premium(x)[0]-P,100,700,xtol=1e-4)
mc={}
for key,name in [('least_cost','least_cost'),('design_sweet_spot','sweet_spot'),('design','design')]:
    with (ROOT/f'monte_carlo_{name}.csv').open(newline='') as f: rr=list(csv.DictReader(f))
    xx=np.array([float(r['transport_cost_bn']) for r in rr]);yy=np.array([float(r['petro_2025']) for r in rr]);sr=100*(1-xx/yy)
    corrs={c:float(spearmanr([float(r[c]) for r in rr],xx).statistic) for c in rr[0] if '/' in c or c in ['yield_level','reactor_case','carbon_market_scale','carbon_value_scale']}
    mc[name]={'draws':len(rr),'cost_bn_p5_p50_p95':[float(x) for x in np.percentile(xx,[5,50,95])],
    'saving_pct_p5_p50_p95':[float(x) for x in np.percentile(sr,[5,50,95])],
    'median_cost_bn':float(np.median(xx)),'median_paired_comparator_bn':float(np.median(yy)),
    'share_cheaper':float(np.mean(sr>0)),
    'pearson_cost_premium':float(np.corrcoef(np.array([float(r['VEH/ldv_bev_net_usd_yr']) for r in rr]),xx)[0,1]),
    'spearman':dict(sorted(corrs.items(),key=lambda kv:-abs(kv[1]))[:12])}
    with (ROOT/f'us91_paired_savings_{name}.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['draw','transport_cost_bn','paired_petroleum_comparator_bn','paired_saving_pct']);w.writeheader()
        for i,(a,b,c) in enumerate(zip(xx,yy,sr)):w.writerow({'draw':i,'transport_cost_bn':a,'paired_petroleum_comparator_bn':b,'paired_saving_pct':c})
E=energy();T=turning()
gh=[]
for lab,e_mj in [('Conventional reference',E['conventional_mj']),('Grid Harvester bare hose, 10% solids',E['bare_hose_10pct_mj'])]+[(f'Grid Harvester faired, {r["dry_solids_fraction"]:.0%} solids',r['grid_total_mj']) for r in E['rows']]:
    gh.append({'configuration':lab,'energy_mj_per_1_44ha_cycle':e_mj,'relative_energy_pct':100*e_mj/E['conventional_mj'],'modelled_energy_reduction_pct':100*(1-e_mj/E['conventional_mj']),'conventional_to_case_efficiency_multiplier':E['conventional_mj']/e_mj})
with (ROOT/'us91_grid_harvester_efficiency.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=gh[0]);w.writeheader();w.writerows(gh)
result={'version':'9.1','transport_only_blend_vol':0,'petroleum_2025_bn':P,'petroleum_gasoline_component_bn':G,
 'cases_cost_bn':cases,'bev_premium_break_even_usd_per_car_year':be,
 'petroleum_2050_proxy_25pct_gasoline_saving_bn':P-.25*G,
 'monte_carlo_conditional':mc,'grid_harvester':{'energy':E,'turning':T,'figure_rows':gh},
 'qualification':'All fuel comparators use late-2025 price levels. 2050 gasoline efficiency rows are fuel-only sensitivity, not AEO2026 reference reproduction. Grid Harvester outputs are engineering assumptions calibrated to reference design, not measured at sea.'}
(ROOT/'us91_scientific_sensitivities.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'costs':cases,'bev_premium_break_even':be,'mc':{k: (v['saving_pct_p5_p50_p95'],v['share_cheaper']) for k,v in mc.items()}},indent=2))
