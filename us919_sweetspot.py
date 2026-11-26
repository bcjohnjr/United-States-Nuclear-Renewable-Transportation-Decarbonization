import sys,copy,json,csv
from pathlib import Path
P=Path(__file__).resolve().parent
import us97_circular_feedstocks as C,us99_agricultural_accounts as U,us915_methane as W
base=json.load(open(P/'V919_reference_parameters.json'));d=json.load(open(P/'US918_Evidence_Results.json'));cen=next(x for x in d['details'] if x['scenario']=='central');refs=[x for x in d['results'] if x['scenario']=='central'];leg=json.load(open(P/'US916_Coupled_Results.json')); lowref=min(x['ref_cost_bn'] for x in refs if 'petroleum' in x['reference'].lower()); aeo=refs[0]['ref_cost_bn'];
import us95_aeo_reference_bridge as A
_,source=A.read_source();stock=source['ldv_2050_bev_m'];ref_el=json.load(open(P/'US97_AEO_Boundary.json'))['reference_emissions']['electricity_tbtu']*.29307107
# Low endpoints inherited from us2_model.MC, except gas price held fixed for paired reference.
levers=[(('ELEC','onshore_wind'),40), (('ELEC','solar'),38), (('ELEC','vre_firming'),10), (('ELEC','td_adder'),20), (('ELEC','charge_ldv'),20), (('PYRO','capex_kw_h2'),700), (('ROUTES','htl','cost_t'),130), (('ROUTES','pbtl','cost_t'),220), (('VEH','ers_capex_m_per_km'),2.5), (('H2_DELIVERY','vehicle'),1.5)]
# Rebuild resource variants with exactly the V9.18 national and group constraints.
def resource_params(label):
 supply,price,frac,delivery={'conservative':('low',60,.65,25),'central':('medium',90,.8,15),'optimistic':('high',120,1.,10)}[label]
 h=d['evidence']['historical_mt'];w=d['evidence']['nwwi_dry_mt'];p=U.carbon_land(U.plant_available(C.build_params(source,bevpremium=base['VEH']['ldv_bev_net_usd_yr'],release_fraction=.5,apply_pyro_to_soil=False,allow_stable_hydrochar=False,cap_mt=min(166,h['crop']*frac))),20e6,.5)
 cr=p['CROP_RESIDUE'];cr['group_caps_mt']=dict(cr['group_caps_mt'])
 with (P/'us918_bt23_national_curves.csv').open() as f:curves=list(csv.DictReader(f))
 c={r['resource']:float(r['dry_mt']) for r in curves if r['supply']==supply and float(r['price_usd_dry_short_ton'])==price};limits={'corn':c['Corn stover'],'wheat':c['Wheat straw'],'small_grain':c['Barley straw']+c['Oats straw'],'sorghum':c['Sorghum stubble']}
 for k,v in limits.items():cr['group_caps_mt'][k]=min(cr['group_caps_mt'].get(k,float('inf')),v)
 for i,f in enumerate(cr['feedstocks']):
  if f['group'] in limits:
   n,cap,old=p['BIOMASS']['tiers'][i];new=max(f['delivered_usd_t'],price/.90718474+delivery);p['BIOMASS']['tiers'][i]=(n,cap,old+new-f['delivered_usd_t']);f['delivered_usd_t']=new
 for k in ('processing','other'):cr['group_caps_mt'][k]=w['food:food']*.25
 forest=min(150,h['forest']*frac);p['BIOMASS']['tiers']=[(n,min(cap,forest) if n.startswith('Verified-separate NON-CROP forest') else cap,pr) for n,cap,pr in p['BIOMASS']['tiers']]
 return p
# Check the published central input snapshot against its independent reconstruction.
assert json.dumps(resource_params('central'),sort_keys=True)==json.dumps(base,sort_keys=True), 'V9.18 central parameter reconstruction differs'
def eval_case(t,bev,strict=False,floor=0.,jitter=None,methane=None,wet_yield=.15,full=False,restriction=None,resource="central"):
 p=resource_params(resource)
 for path,low in levers:
  obj=p
  for k in path[:-1]:obj=obj[k]
  k=path[-1];obj[k]=obj[k]+t*(low-obj[k])
 p['VEH']['ldv_bev_net_usd_yr']=bev
 p['CROP_RESIDUE']['collect_min_mt']=floor
 for path,v in (jitter or {}).items():
  o=p
  for k in path[:-1]:o=o[k]
  o[path[-1]]=v
 if strict or restriction:
  for i,f in enumerate(p['CROP_RESIDUE']['feedstocks']):
   if (restriction=='none' or (restriction in ('mapped','mapped_wet') and f['group'] not in (('corn','wheat','sorghum','small_grain','processing','other') if restriction=='mapped_wet' else ('corn','wheat','sorghum','small_grain'))) or (strict and (f['group'] not in ('corn','wheat','sorghum') or f['name'].startswith('Corn cobs')))):
    n,_,pr=p['BIOMASS']['tiers'][i];p['BIOMASS']['tiers'][i]=(n,0.,pr);f['cap_mt']=0.
 r=C.one('sweep',p);alt=U.integrated_lca(r)['replaced_route_screen_mt']; overlap=sum(z['selected_mt'] for z in r['selected'] if z['group'] in ('processing','other'));cap=copy.deepcopy(W.CAP); wet=d['evidence']['nwwi_dry_mt']; wm={'dairy_manure':'manure:dairy','beef_manure':'manure:beef','swine_manure':'manure:swine','wastewater':'sludge:sludge','food_processing_and_food_waste':'food:food'}
 for k,v in wm.items():cap[k]=min(cap[k],max(0,wet[v]-(overlap if v=='food:food' else 0))*wet_yield)
 m=copy.deepcopy(methane or W.SCENARIOS[resource]);m['gas_co2']=0
 oldcap,oldbase=W.CAP,W.MANURE_BASE
 try:
  W.CAP=cap;W.MANURE_BASE=cen['manure_baseline_caps_mtco2e'];w=W.evaluate(m)
 finally:W.CAP=oldcap;W.MANURE_BASE=oldbase
 internal=min(w['biomethane_twh'],leg['gas_pipeline_lhv_twh']);external=w['biomethane_twh']-internal;credit=internal*.202;net=w['biogas_cost_bn']+w['asp_cost_bn']-(internal*leg['gas_avoided_value_usd_mwh_lhv']+external*m['gas_price'])/1000
 cost=r['annual_cost_bn']+net
 out=dict(resource=resource,tech_progress=t,bev_net_annual_usd=bev,strict_crop=strict,transport_cost_bn=r['annual_cost_bn'],agri_net_cost_bn=net,combined_cost_bn=cost,savings_low_petroleum_bn=lowref-cost,savings_aeo_fixed_bn=aeo-cost,transport_emissions_mt=alt,combined_avoided_mt=next(x['ref_emissions_mt'] for x in refs if 'petroleum' in x['reference'].lower())-alt+credit+w['incremental_net_avoided_mt'],crop_mt=r['crop_htl_mt'],biomethane_twh=w['biomethane_twh'],asparagopsis_mt=w['asp_dry_mt'],hubs=r['hubs'],wind_gw=r['onshore_gw'],offshore_gw=r['offshore_gw'],agri_avoided_mt=w['incremental_net_avoided_mt'],gas_credit_mt=credit,internal_twh=internal,external_twh=external,restriction=restriction or ('exact' if strict else 'all'),crop_floor_mt=floor)
 assert r['crop_htl_mt']+1e-6>=floor and abs(internal+external-w['biomethane_twh'])<1e-9
 out.update(aeo_bev_matched_bn=aeo+stock*(bev-base['VEH']['ldv_bev_net_usd_yr'])/1000)
 out['aeo_bev_matched_saving_bn']=out['aeo_bev_matched_bn']-cost
 def at(q,path):
  for k in path:q=q[k]
  return q
 dd=sum(at(p,k)-at(base,k) for k,_ in levers[:2])/2+1.125*(at(p,levers[2][0])-at(base,levers[2][0]))+at(p,levers[3][0])-at(base,levers[3][0]);out['aeo_electricity_pass_bn']=out['aeo_bev_matched_bn']+dd*ref_el/1000
 if full:
  raw=C.M.solve_learning(p,scenario='least_cost',blend_vol=0.,osw_scale=0.,kelp_force=False);assert abs(raw['transport_cost_bn']-r['annual_cost_bn'])<1e-7
  return out,dict(transport=r,agricultural={k:v for k,v in w.items() if k not in ('combined_avoided_mt','transport_avoided_mt','transport_reduction_pct','combined_incremental_cost_vs_aeo_bn')},full=raw,parameters=p)
 return out

def write(name,rows):
 with (P/name).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)

def main():
 import random,numpy as np
 prem=base['VEH']['ldv_bev_net_usd_yr']; floor=cen['transport']['crop_htl_mt']; baseline,bd=eval_case(0,prem,full=True);assert abs(baseline['combined_cost_bn']-next(x['combined_cost_bn'] for x in refs if 'late_2025' in x['reference']))<1e-7
 target,td=eval_case(.75,-300,floor=floor,full=True);print('TARGET',target,flush=True)
 rows=[dict(case='reference costs',**baseline),dict(case='full crop floor target',**target)]
 for name,t,b,restr,f in [('free crop target',.75,-300,None,0),('exact mapped target',.75,-300,'exact',0),('mapped groups target',.75,-300,'mapped',0),('mapped and wet target',.75,-300,'mapped_wet',0),('no crop target',.75,-300,'none',0),('strong progress',1,-400,None,floor),('no BEV cost advantage',.75,0,None,floor),('no tech cost progress',0,-300,None,floor)]:
  rows.append(dict(case=name,**eval_case(t,b,strict=restr=='exact',restriction=None if restr=='exact' else restr,floor=f)))
 for resource,y in [('conservative',.10),('optimistic',.20)]:
  rows.append(dict(case=resource+' resource target',**eval_case(.75,-300,resource=resource,wet_yield=y)))
 def get(o,path):
  for k in path:o=o[k]
  return o
 slopes=base['VEH']['ldv_stock_m']*base['ENDUSE']['ldv']['bev']/1000
 frontier=[]
 for t in np.linspace(0,1,21):
  r=eval_case(float(t),0,floor=floor);frontier.append(dict(progress=float(t),zero_bev_cost_bn=r['combined_cost_bn'],break_even_bev_usd_year=(lowref-r['combined_cost_bn'])/slopes))
 rng=random.Random(919);mc=[]
 for i in range(512):
  t=rng.triangular(.35,1,.75); b=rng.triangular(-400,prem,-300); j={path:max(lo,(get(base,path)+t*(lo-get(base,path)))*rng.triangular(.95,1.15,1)) for path,lo in levers};j[('PYRO','leak_upstream')]=rng.triangular(.005,.03,.015)
  m={k:rng.triangular(min(W.SCENARIOS[s][k] for s in W.SCENARIOS),max(W.SCENARIOS[s][k] for s in W.SCENARIOS),W.SCENARIOS['central'][k]) if len({W.SCENARIOS[s][k] for s in W.SCENARIOS})>1 else W.SCENARIOS['central'][k] for k in W.SCENARIOS['central']}
  resource=rng.choices(['conservative','central','optimistic'],weights=[.2,.6,.2])[0];r=eval_case(t,b,jitter=j,methane=m,wet_yield=rng.triangular(.10,.20,.15),resource=resource);mc.append(dict(draw=i,**r))
  if i%32==0:print('draw',i,flush=True)
 timeline=[];pet=[x for x in refs if 'petroleum' in x['reference'].lower()]
 for year in range(2026,2051):
  f=(year-2026)/24;t=.75*f;b=prem+(-300-prem)*f;r=eval_case(t,b,floor=floor)
  for ref in pet:
   for reserve in (0,10,25):
    extra=reserve*4*f*(1-f);hybrid=(1-f)*ref['ref_cost_bn']+f*r['combined_cost_bn']+extra
    timeline.append(dict(year=year,adoption_fraction=f,progress=t,bev_usd_year=b,reference=ref['reference'],ref_cost_bn=ref['ref_cost_bn'],full_alt_annualized_bn=r['combined_cost_bn'],reserve_peak_bn=reserve,extra_transition_bn=extra,hybrid_annualized_bn=hybrid,savings_bn=ref['ref_cost_bn']-hybrid,avoided_mt=f*r['combined_avoided_mt']))
 summaries=[]
 for ref in pet:
  for reserve in (0,10,25):
   z=[r for r in timeline if r['reference']==ref['reference'] and r['reserve_peak_bn']==reserve];first=next((r['year'] for i,r in enumerate(z) if all(q['savings_bn']>1e-8 for q in z[i:])),None);summaries.append(dict(reference=ref['reference'],reserve_peak_bn=reserve,sustained_saving_year=first,discounted_savings_bn=sum(r['savings_bn']/1.07**(r['year']-2026) for r in z),undiscounted_savings_bn=sum(r['savings_bn'] for r in z)))
 summary={k:[float(v) for v in np.quantile([r[k] for r in mc],[.05,.5,.95])] for k in ['combined_cost_bn','savings_low_petroleum_bn','combined_avoided_mt','aeo_bev_matched_saving_bn','crop_mt','biomethane_twh']};summary['fraction_beating_low_petroleum']=sum(r['savings_low_petroleum_bn']>0 for r in mc)/len(mc);summary['fraction_beating_matched_aeo']=sum(r['aeo_bev_matched_saving_bn']>0 for r in mc)/len(mc)
 lv=[dict(parameter='.'.join(path),base=get(base,path),low=lo,target=get(td['parameters'],path),annual_decline_pct=100*(1-(get(td['parameters'],path)/get(base,path))**(1/24)),implied_learning_per_doubling_pct_3_doublings=100*(1-(get(td['parameters'],path)/get(base,path))**(1/3))) for path,lo in levers]
 for n,rs in [('cases',rows),('frontier',frontier),('joint_draws',mc),('transition',timeline),('transition_summary',summaries),('levers',lv)]:write('us919_'+n+'.csv',rs)
 out=dict(version='9.19',baseline=baseline,target=target,cases=rows,baseline_detail=bd,target_detail=td,references=refs,levers=lv,uncertainty=summary,transition_summary=summaries,notes=['Cost endpoints are inherited sensitivity bounds, not validated forecasts.','Matched AEO adjusts BEV differential on both fleets; optional equal-weight generation, firming and distribution pass-through is illustrative only.','Transition holds 2050 service fixed, blends annualized costs and does not model chronological investment or retirement.','512 assumed-distribution draws, three resource supply scenarios, relaxed floor, not probabilities or confidence intervals.','Reactor learning uses original fleet fixed-point iteration.','Readiness-gated adoption assumes cost improvements occur exogenously, no more than 10 percentage points per year of fixed 2050 service, and does not establish physical deployment feasibility.'])
 # Accelerated readiness: target costs reached by specified year; adoption is gated
 # at low-petroleum break-even incl. transition reserve and bounded at 10 pp/year.
 # Greedy maximum affordable adoption; not a construction schedule. No overspend
 # criterion is for an aggregate annualized equivalent only.
 gates=[];gate_summaries=[]
 for profile,pt,pb in [('target',.75,-300),('strong',1,-400)]:
  for ready in (2035,2040,2045,2050):
   for reserve in (0,10,25):
    prev=0.; pathrows=[]
    for year in range(2026,2051):
     f=min(1,(year-2026)/(ready-2026));r=eval_case(pt*f,prem+(pb-prem)*f,floor=floor)
     maxshare=min(1,prev+.10) if year>2026 else 0.
     # For a new share x, savings=x*(lowref-full_alt)-4*reserve*x*(1-x).
     saving=maxshare*(lowref-r['combined_cost_bn'])-reserve*4*maxshare*(1-maxshare)
     share=maxshare if saving>=-1e-9 else prev
     sv=share*(lowref-r['combined_cost_bn'])-reserve*4*share*(1-share)
     pathrows.append(dict(profile=profile,readiness_year=ready,reserve_peak_bn=reserve,year=year,adoption_fraction=share,full_alt_annualized_bn=r['combined_cost_bn'],lowest_petroleum_saving_bn=sv,combined_avoided_mt=share*r['combined_avoided_mt']))
     prev=share
    gates+=pathrows;gate_summaries.append(dict(profile=profile,readiness_year=ready,reserve_peak_bn=reserve,adoption_2050=prev,first_deployment_year=next((r['year'] for r in pathrows if r['adoption_fraction']>0),None),no_annual_overspend=all(r['lowest_petroleum_saving_bn']>=-1e-8 for r in pathrows),discounted_savings_bn=sum(r['lowest_petroleum_saving_bn']/1.07**(r['year']-2026) for r in pathrows)))
 write('us919_gated_transition.csv',gates);write('us919_gated_summary.csv',gate_summaries);out['gated_summary']=gate_summaries
 (P/'US919_Results.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print('SUMMARY',summary,summaries,flush=True)
if __name__=='__main__':main()
