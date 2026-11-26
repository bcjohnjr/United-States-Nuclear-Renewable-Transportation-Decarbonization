"""V9.15 incremental methane/waste screening module, not a rerun of transport LP.
All monetary amounts in 2026 USD, emissions Mt CO2e/yr, methane Mt/yr, energy TWh LHV/yr.
Inputs other than explicitly sourced ceilings and inherited seaweed target are analyst sensitivities.
"""
import csv,json,math,random,statistics
from pathlib import Path
P=Path(__file__).resolve().parent
# NREL 2013, gross technical methane generation potential (not incremental supply).
MANURE_BASE={'dairy_manure':33.5,'swine_manure':24.3,'poultry_manure':3.0,'beef_manure':4.2,'other_manure':.1}
# Allocate the old NREL national ceiling using EPA 2023 manure-emissions shares as a proxy only.
CAP={**{k:1.905253*v/65.1 for k,v in MANURE_BASE.items()},'food_processing_and_food_waste':1.157883*.75,'municipal_green_plant_waste':1.157883*.25,'wastewater':2.339339}
# Food/green split is an assumption within one shared cap. No dedicated crop residues (166 Mt already used in HTL).
BASE_MANURE=65.1 # EPA 2023 national remaining manure CH4 emissions, AR5 GWP28
GWP=28.; LHV=50/3.6 # TWh/Mt CH4
TRANSPORT_REF=1638.8; TRANSPORT_ALT=229.38; COST_REF=477.1; COST_ALT=654.7633815744267
# scenario values: eligibility remaining after existing recovery / collection / biological realization / gas handling loss / flare / parasitic gas / collection+AD+upgrading cost per gross MWh / monitoring cost / nonmethane lifecycle kg/MWh
SCENARIOS={
 'conservative':dict(eligible=.35,collect=.60,yield_frac=.80,leak=.055,flare=.03,parasitic=.15,plant_cost=100,monitor=5,process_kg=45,baseline_mcf=.35,asp_adopt=.6,asp_eff=.75,asp_ret=.65,asp_cost=6500,asp_lca=18,gas_price=15,gas_co2=0),
 'central':dict(eligible=.60,collect=.80,yield_frac=.90,leak=.01,flare=.02,parasitic=.10,plant_cost=65,monitor=4,process_kg=25,baseline_mcf=.60,asp_adopt=.8,asp_eff=.85,asp_ret=.8,asp_cost=5000,asp_lca=10,gas_price=25,gas_co2=0),
 'optimistic':dict(eligible=.80,collect=.95,yield_frac=.98,leak=.002,flare=.01,parasitic=.05,plant_cost=40,monitor=3,process_kg=15,baseline_mcf=.80,asp_adopt=1,asp_eff=1,asp_ret=1,asp_cost=4000,asp_lca=5,gas_price=40,gas_co2=0)}
# gas_co2=0 avoids credit for unspecified gas end use (sale value is conditional). External combustion substitution sensitivity only.
def evaluate(p):
    heritage=json.loads((P/'nutrient_balance_v6.json').read_text())['scenarios']['least_cost']
    target=heritage['target_asparagopsis_mt_dry']; target_avoid=heritage['target_methane_reduction_mtco2e']
    rows=[]
    for key,cap in CAP.items():
        gross=cap*p['eligible']*p['collect']*p['yield_frac']; leak=gross*p['leak']; flare=gross*p['flare']; parasitic=gross*p['parasitic']; delivered=gross-leak-flare-parasitic
        assert delivered>=0 and abs(gross-leak-flare-parasitic-delivered)<1e-10
        gross_energy=gross*LHV; energy=delivered*LHV
        # Counterfactual only manure; no speculative landfill/wastewater credits.
        avoided=min(MANURE_BASE[key],gross*p['baseline_mcf']*GWP) if key in MANURE_BASE else 0.
        process=gross_energy*p['process_kg']/1000 # TWh * kg/MWh / 1000 -> Mt
        # Recovered NPK in digestate is physical screening only: based on assumed dry VS and total nutrients per t VS.
        vs=gross/.20 # Mt VS, assumed 0.20 t CH4/t VS
        n,pn,k=[vs*a*.8 for a in (.04,.008,.02)] # Mt elemental, 80% conserved; never automatically displaced
        expense=gross_energy*(p['plant_cost']+p['monitor'])/1000
        value=energy*p['gas_price']/1000
        rows.append(dict(stream=key,potential_ch4_mt=cap,gross_ch4_mt=gross,leaked_ch4_mt=leak,flared_ch4_mt=flare,parasitic_ch4_mt=parasitic,delivered_ch4_mt=delivered,delivered_twh=energy,baseline_avoided_mt=avoided,leak_mtco2e=leak*GWP,process_mtco2e=process,external_gas_displacement_mt=energy*p['gas_co2']/1000,net_avoided_mt=avoided-leak*GWP-process+energy*p['gas_co2']/1000,cost_bn=expense,gas_value_bn=value,digestate_N_mt=n,digestate_P_mt=pn,digestate_K_mt=k))
    total=lambda key:sum(r[key] for r in rows)
    asp=target*p['asp_adopt']; asp_gross=target_avoid*p['asp_adopt']*p['asp_eff']*p['asp_ret']; asp_lca=asp*p['asp_lca']; asp_net=asp_gross-asp_lca; asp_cost=asp*p['asp_cost']/1000
    # Scale inherited 25 MWh/t heat demand; standalone cost includes heat and nutrients, no unallocated free heat.
    asp_heat=asp*25.; asp_n=asp*.036; asp_p=asp*.0027
    # No fertilizer credit: baseline manure nutrients often already fertilize fields; no validated incremental displacement.
    net=total('net_avoided_mt')+asp_net; cost=total('cost_bn')-total('gas_value_bn')+asp_cost
    return dict(inputs=p,streams=rows,biomethane_twh=total('delivered_twh'),leaked_ch4_mt=total('leaked_ch4_mt'),biogas_net_avoided_mt=total('net_avoided_mt'),digestate_N_mt=total('digestate_N_mt'),digestate_P_mt=total('digestate_P_mt'),digestate_K_mt=total('digestate_K_mt'),asp_dry_mt=asp,asp_heat_twh=asp_heat,asp_elemental_N_mt=asp_n,asp_elemental_P_mt=asp_p,asp_gross_avoided_mt=asp_gross,asp_lca_mt=asp_lca,asp_net_avoided_mt=asp_net,asp_cost_bn=asp_cost,biogas_cost_bn=total('cost_bn'),gas_value_bn=total('gas_value_bn'),incremental_net_cost_bn=cost,incremental_net_avoided_mt=net,combined_avoided_mt=TRANSPORT_REF-TRANSPORT_ALT+net,transport_avoided_mt=TRANSPORT_REF-TRANSPORT_ALT,transport_reduction_pct=100*(1-TRANSPORT_ALT/TRANSPORT_REF),combined_incremental_cost_vs_aeo_bn=COST_ALT-COST_REF+cost,external_gas_credit_mt=total('external_gas_displacement_mt'))
def main():
    res={k:evaluate(v) for k,v in SCENARIOS.items()}
    # same central physical programme, no new leak mitigation vs ambitious target; no double counting as separate scenarios
    res['central_5pct_leak']=evaluate(dict(SCENARIOS['central'],leak=.05,monitor=0))
    res['central_no_gas_value']=evaluate(dict(SCENARIOS['central'],gas_price=0))
    res['central_external_gas_displacement']=evaluate(dict(SCENARIOS['central'],gas_co2=202)) # kg CO2/MWh LHV fossil gas combustion; external matched energy only
    rng=random.Random(915); draws=[]
    for i in range(1000):
        p={k:rng.triangular(min(SCENARIOS[s][k] for s in ('conservative','central','optimistic')),max(SCENARIOS[s][k] for s in ('conservative','central','optimistic')),SCENARIOS['central'][k]) if len(set(SCENARIOS[s][k] for s in ('conservative','central','optimistic')))>1 else SCENARIOS['central'][k] for k in SCENARIOS['central']}
        r=evaluate(p); draws.append(dict(draw=i,**p,**{k:r[k] for k in ['incremental_net_avoided_mt','incremental_net_cost_bn','combined_avoided_mt','biomethane_twh']}))
    def quant(a,q):
        a=sorted(a); i=(len(a)-1)*q; return a[int(i)]*(1-i%1)+a[math.ceil(i)]*(i%1)
    summary={k:[quant([x[k] for x in draws],q) for q in [.05,.5,.95]] for k in ['incremental_net_avoided_mt','incremental_net_cost_bn','combined_avoided_mt','biomethane_twh']}
    (P/'US915_Methane_Results.json').write_text(json.dumps(dict(scenarios=res,triangular_screen_5_50_95=summary),indent=2))
    for filename,rs in [('us915_methane_scenarios.csv',[dict(scenario=k,**{a:b for a,b in v.items() if a not in ('inputs','streams')}) for k,v in res.items()]),('us915_methane_streams.csv',[dict(scenario=k,**r) for k,v in res.items() for r in v['streams']]),('us915_methane_uncertainty.csv',draws)]:
        with (P/filename).open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
    for r in res.values():
        assert r['transport_reduction_pct']==100*(1-TRANSPORT_ALT/TRANSPORT_REF)
        assert sum(s['potential_ch4_mt'] for s in r['streams'] if 'waste' in s['stream'] and s['stream']!='wastewater')<=1.157883+1e-9
        assert r['external_gas_credit_mt']>=0
        assert sum(s['baseline_avoided_mt'] for s in r['streams']) <= BASE_MANURE
        assert abs(sum(CAP[k] for k in MANURE_BASE)-1.905253)<1e-10
    assert res['central']['incremental_net_avoided_mt']>res['central_5pct_leak']['incremental_net_avoided_mt']
    assert res['central_no_gas_value']['incremental_net_cost_bn']>=res['central']['incremental_net_cost_bn']
    print('PASS methane mass balance, shared waste cap, fixed transport boundary, leakage and cost monotonicity; 1000 diagnostic draws')
    print(json.dumps({k:{a:round(b,3) for a,b in v.items() if isinstance(b,(int,float))} for k,v in res.items()},indent=2))
    print(summary)
if __name__=='__main__':main()
