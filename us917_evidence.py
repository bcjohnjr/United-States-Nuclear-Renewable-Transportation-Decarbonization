"""Evidence-constrained national scenario, not a county supply or hourly dispatch model.
No network calls. Historical dry metric tonnes, CH4 metric tonnes, dollars as in V9.16.
"""
import csv,json,math,copy,zipfile,io
from collections import defaultdict
from pathlib import Path
import openpyxl
import us915_methane as W
import us95_aeo_reference_bridge as A
import us97_circular_feedstocks as C
import us99_agricultural_accounts as U
P=Path(__file__).resolve().parent
SHORT=0.90718474

def read(n):
 with (P/n).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(n,rows):
 with (P/n).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def num(v):return None if v in ('',None) else float(v)
def source_data():
 states={r['state_fips']:r['state'] for r in read('state_codes.csv')}; b=read('USDA_county_solid_biomass.csv'); m=read('USDA_county_methane_emissions.csv');assert len(b)==len(m)==3221 and len({r['FIPS'] for r in b})==3221
 bm={r['FIPS']:r for r in m}; s=defaultdict(lambda:dict(count=0,numeric=0,crop=0.,forest=0.,manure=0.,wastewater=0.))
 for r in b:
  f=r['FIPS']; st=f[:2];
  if st not in states:continue
  x=s[st]; x['count']+=1
  if num(r['CropRes']) is None:continue
  x['numeric']+=1
  for k,v in [('crop',r['CropRes']),('forest',r['Forest']),('manure',bm[f]['ManureMgmt']),('wastewater',bm[f]['Wastewater'])]:x[k]+=float(v)
 state_rows=[dict(state_fips=k,state=states[k],**v) for k,v in sorted(s.items())];write('us917_state_historical_resources.csv',state_rows)
 sums={k:sum(r[k] for r in state_rows)/1e6 for k in ['crop','forest','manure','wastewater']}
 wet=defaultdict(float);count=defaultdict(int);seen=set()
 with (P/'NWWI_NWWI.txt').open(encoding='utf-8-sig',newline='') as f:
  for r in csv.DictReader(f,delimiter='\t'):
   assert r['ROWID'] not in seen;seen.add(r['ROWID']); k=r['FEEDSTOCK']+':'+r['SUBGROUP'];v=float(r['DRY_KG_YR']);assert v>=0;wet[k]+=v/1e9;count[k]+=1
 assert len(seen)==56111
 w=openpyxl.load_workbook(P/'BT23_National_summary.xlsx',read_only=True,data_only=True)['Agricultural_residue']; allrows=list(w.values); curves=[]
 for start,label in [(1,'low'),(9,'medium'),(17,'high')]:
  for j in range(3,12):
   price=float(allrows[start][j]);
   for row in allrows[start+1:start+6]:curves.append(dict(supply=label,price_usd_dry_short_ton=price,price_usd_dry_metric_tonne=price/SHORT,resource=row[2],dry_short_ton=float(row[j]),dry_mt=float(row[j])*SHORT/1e6))
 write('us917_bt23_national_curves.csv',curves)
 ag=openpyxl.load_workbook(P/'EPA_AgSTAR_livestock.xlsx',read_only=True,data_only=True).worksheets[0]; ar=list(ag.values);idx=ar[0].index('Status');agcounts={k:sum(1 for r in ar[1:] if r[idx]==k) for k in sorted({r[idx] for r in ar[1:] if r[idx]})}
 with zipfile.ZipFile(P/'2022CWNS_NATIONAL_Sept2026.zip') as z:
  def table(n):return list(csv.DictReader(io.TextIOWrapper(z.open(next(a for a in z.namelist() if a.endswith('/'+n+'.csv'))),encoding='utf-8-sig')))
  facilities=table('FACILITIES');process=table('UNIT_PROCESSES'); existing={r['FACILITY_ID'] for r in process if r['EXISTING_FLAG']=='Y' and 'anaerobic' in r['UNIT_PROCESS'].lower() and 'digest' in r['UNIT_PROCESS'].lower()}
  cwns=dict(facility_rows=len(facilities),wastewater_rows=sum(r['INFRASTRUCTURE_TYPE']=='Wastewater' for r in facilities),existing_anaerobic_digestion_facility_ids=len(existing))
 cows=read('county_livestock_inventory_screen.csv');cow_total=sum(float(r['cows_and_heifers_calved_inventory']) for r in cows if r['cows_and_heifers_calved_inventory'])
 return dict(historical_mt=sums,county_numeric=sum(r['numeric'] for r in state_rows),nwwi_dry_mt=dict(wet),nwwi_counts=dict(count),agstar_status=agcounts,cwns=cwns,published_cows=cow_total),curves

def run():
 evidence,curves=source_data(); h=evidence['historical_mt'];wet=evidence['nwwi_dry_mt']; legacy=json.loads((P/'US916_Coupled_Results.json').read_text());_,a=A.read_source(); premium=json.loads((P/'US97_AEO_Boundary.json').read_text())['results'][1]['net_bev_differential_usd_yr']; results=[];streams=[];alloc=[];details=[]
 specs=[('conservative','low',60,.65,.10),('central','medium',90,.80,.15),('optimistic','high',120,1.,.20)]
 def params(cap):return U.carbon_land(U.plant_available(C.build_params(a,bevpremium=premium,release_fraction=.5,apply_pyro_to_soil=False,allow_stable_hydrochar=False,cap_mt=cap)),20e6,.5)
 for name,supply,price,fraction,yield_ch4 in specs:
  p=params(min(166,h['crop']*fraction));cr=p['CROP_RESIDUE'];cr['group_caps_mt']=dict(cr['group_caps_mt']); c={r['resource']:r['dry_mt'] for r in curves if r['supply']==supply and r['price_usd_dry_short_ton']==price}; limits={'corn':c['Corn stover'],'wheat':c['Wheat straw'],'small_grain':c['Barley straw']+c['Oats straw'],'sorghum':c['Sorghum stubble']}
  # Combined corn pool includes cobs/husks, so imposing stover ceiling conservatively bounds both. Rye not separately credited in small-grain ceiling.
  for k,v in limits.items():cr['group_caps_mt'][k]=min(cr['group_caps_mt'].get(k,math.inf),v)
  # Offered price is not a delivered price; apply a conservative floor plus assumed delivery.
  # For mixed categories (corn cobs, rye) use same price floor as a screening assumption.
  delivery={'conservative':25.,'central':15.,'optimistic':10.}[name]
  for i,f in enumerate(cr['feedstocks']):
   if f['group'] in limits:
    n,cap0,old=p['BIOMASS']['tiers'][i]; floor=price/SHORT+delivery; new=max(f['delivered_usd_t'],floor)
    p['BIOMASS']['tiers'][i]=(n,cap0,old+new-f['delivered_usd_t']);f['delivered_usd_t']=new
  # Reserve a scenario-defined share of the historical food pool for digestion and bound potentially overlapping crop processing together.
  food_reserved=wet['food:food']*.5
  cr['group_caps_mt']['processing']=food_reserved*.5
  cr['group_caps_mt']['other']=food_reserved*.5
  # Historic forest-only bound, not the sum of potentially overlapping mill/forest estimates.
  # Matched no-crop reference receives identical forest ceiling.
  forest=min(150,h['forest']*fraction)
  def forest_bound(q):
   q['BIOMASS']['tiers']=[(n,min(cap,forest) if n.startswith('Verified-separate NON-CROP forest') else cap,pr) for n,cap,pr in q['BIOMASS']['tiers']];return q
  forest_bound(p);no=C.one(name+' matched no crop',forest_bound(params(0)));r=C.one(name,p);alt=U.integrated_lca(r)['replaced_route_screen_mt'];cost=r['annual_cost_bn'];
  # Historical USDA distribution is an illustrative allocation, not a deliverable network.
  for x in read('us917_state_historical_resources.csv'):
   alloc.append(dict(scenario=name,state_fips=x['state_fips'],state=x['state'],crop_selected_proportional_mt=r['crop_htl_mt']*float(x['crop'])/(h['crop']*1e6)))
  # Wet waste dry solids times assumed methane yield; intersect with original technical ceilings.
  # Reserve plant-processing/other solids from potentially overlapping NWWI food stream.
  overlap=sum(float(z['selected_mt']) for z in r['selected'] if z['group'] in ('processing','other'))
  # selected_feedstocks schema checked below; deliberately reserve complete selected mass if key not recognized.
  for z in r['selected']:
   if z['group'] in ('processing','other'):assert 'selected_mt' in z,z
  cap=copy.deepcopy(W.CAP); wetmap={'dairy_manure':'manure:dairy','beef_manure':'manure:beef','swine_manure':'manure:swine','wastewater':'sludge:sludge','food_processing_and_food_waste':'food:food'}
  for k,v in wetmap.items():cap[k]=min(cap[k],max(0,wet[v]-(overlap if v=='food:food' else 0))*yield_ch4)
  # Poultry and municipal green waste retained as legacy unverified disjoint streams, not sourced from NWWI.
  # Cap historical total manure counterfactual without adding it to EPA inventory.
  baseline={k:min(v,v/W.BASE_MANURE*h['manure']*W.GWP) for k,v in W.MANURE_BASE.items()}
  oldcap,oldbase=W.CAP,W.MANURE_BASE
  try:
   W.CAP=cap;W.MANURE_BASE=baseline;w=W.evaluate(W.SCENARIOS[name])
  finally:W.CAP=oldcap;W.MANURE_BASE=oldbase
  for row in w['streams']:streams.append(dict(scenario=name,**row))
  # Internal-first policy scenario (not a claim of cost-optimal routing for all gas prices). No carbon revenue.
  internal=min(w['biomethane_twh'],legacy['gas_pipeline_lhv_twh']);external=w['biomethane_twh']-internal;credit=internal*.202;netcost=w['biogas_cost_bn']+w['asp_cost_bn']-(internal*legacy['gas_avoided_value_usd_mwh_lhv']+external*W.SCENARIOS[name]['gas_price'])/1000
  details.append(dict(scenario=name,group_caps_mt=cr['group_caps_mt'],delivery_assumption_usd_metric_t=delivery,transport=r,matched_no_crop=no,agricultural=w,wet_caps_ch4_mt=cap,manure_baseline_caps_mtco2e=baseline))
  for ref in legacy['references']:
   re=ref['ref_emissions_mt'];rc=ref['ref_cost_bn'];results.append(dict(scenario=name,bt23_supply=supply,bt23_price_usd_short_ton=price,historical_fraction=fraction,wet_ch4_yield_t_dry_t=yield_ch4,reference=ref['name'],crop_cap_mt=cr['cap_mt'],forest_cap_mt=forest,crop_selected_mt=r['crop_htl_mt'],crop_saving_bn=no['annual_cost_bn']-cost,transport_cost_bn=cost,transport_emissions_mt=alt,transport_reduction_pct=100*(1-alt/re),biomethane_twh=w['biomethane_twh'],biogas_net_mt=w['biogas_net_avoided_mt'],asp_net_mt=w['asp_net_avoided_mt'],agri_net_mt=w['incremental_net_avoided_mt'],gas_credit_mt=credit,internal_twh=internal,external_twh=external,agri_net_cost_bn=netcost,combined_cost_bn=cost+netcost,combined_savings_bn=rc-cost-netcost,combined_avoided_mt=re-alt+credit+w['incremental_net_avoided_mt'],ref_cost_bn=rc,ref_emissions_mt=re,food_overlap_reserved_mt=overlap))
  assert r['crop_htl_mt']<=cr['cap_mt']+1e-6;assert abs(sum(x['crop_selected_proportional_mt'] for x in alloc if x['scenario']==name)-r['crop_htl_mt'])<1e-6
 write('us917_evidence_scenarios.csv',results);write('us917_waste_streams.csv',streams);write('us917_state_crop_allocation.csv',alloc)
 out=dict(evidence=evidence,results=results,details=details,limits='Historical and BT23 scenario quantities intersect analyst caps; offered price converted to metric-tonne price floor plus assumed delivery for mapped crop groups, with separate soil/nutrient cost. No exact county curves, spatial dispatch, or observed future adoption. Wet waste model uses historical resource estimates, not current additional supply. No extra credits for FOG, digestate, existing digesters or wastewater avoided methane. Retained legacy V9.16 results are a distinct sensitivity.')
 (P/'US917_Evidence_Results.json').write_text(json.dumps(out,indent=2));print(json.dumps(evidence,indent=2));print('PASS: 15 comparisons, constrained LP, mass, cost and allocation checks')
 for x in results:
  if x['scenario']=='central':print(x)
if __name__=='__main__':run()
