#!/usr/bin/env python3
"""Strict ORNL BT23 agricultural supply curve import AND model crosswalk.

No portal export is redistributed or fabricated. This module accepts user-exported
original county CSV/ZIP data, verifies rows and cumulative price tiers and replaces
V9.8 analyst category capacities with state/resource/price incremental tiers.
Scenarios using county input remain screening results: spatial siting, USDA crop
rotations, residue competing uses and feedstock chemistry are not yet validated.
"""
from __future__ import annotations
import csv,re,json,hashlib,zipfile,io,collections,argparse,sys
from pathlib import Path
SHORT_TO_METRIC=.90718474
R=Path(__file__).resolve().parent
CANON={
 'corn stover':'Corn stalks and leaves (excluding cobs/husks)',
 'wheat straw':'Wheat straw and chaff',
 'rice straw':'Rice straw',
 'barley straw':'Barley, oat and rye straw',
 'oats straw':'Barley, oat and rye straw',
 'oat straw':'Barley, oat and rye straw',
 'sorghum stubble':'Grain sorghum stalks and leaves',
 'sorghum straw':'Grain sorghum stalks and leaves',
 'cotton field residues':'Cotton stalks',
 'cotton stalks':'Cotton stalks',
 'soybean straw':'Soybean stems, pods and processing hulls',
 'soybean residues':'Soybean stems, pods and processing hulls',
 'pruning residues, citrus':'Orchard and nut-crop pruning residues',
 'pruning residues, noncitrus':'Orchard and nut-crop pruning residues',
 'pruning residues, tree nuts':'Orchard and nut-crop pruning residues',
}
# Price tiered nonnegative marginal supply. No invented 'husk' mass in corn stover.
def _normal(s):return re.sub(r'[^a-z0-9]+','_',str(s or '').strip().lower()).strip('_')
def _read(path):
 p=Path(path)
 if p.suffix.lower()=='.csv':yield p.name,p.read_bytes()
 elif p.suffix.lower()=='.zip':
  with zipfile.ZipFile(p) as z:
   assert z.testzip() is None,'bad ZIP'
   csvs=[f for f in z.namelist() if f.lower().endswith('.csv') and not f.startswith('__MACOSX/') and not f.endswith('/')]
   if not csvs: raise ValueError(f'{p.name}: ZIP HAS NO CSV DATA; directory-only ZIPs do not contain official BT23 records')
   for f in csvs:
     yield p.name+'/'+f,z.read(f)
 else:raise ValueError('Expected official portal CSV or CSV-containing ZIP, not '+str(path))
def ingest(paths,scenario='mature-market medium',allow_partial=False, min_counties=1000):
 # Global county/resource/price uniqueness across all supplied files.
 by={};sha={};seen_scenarios=set();seen_resources=set();excluded=collections.Counter()
 for path in paths:
  for name,raw in _read(path):
   sha[name]=hashlib.sha256(raw).hexdigest()
   reader=csv.DictReader(io.StringIO(raw.decode('utf-8-sig',errors='strict')))
   if not reader.fieldnames:raise ValueError('No CSV header in '+name)
   col={_normal(x):x for x in reader.fieldnames}
   def val(r,*keys):
    for k in keys:
     if k in col and str(r.get(col[k], '')).strip():return str(r[col[k]]).strip()
    return ''
   required=[('fips',),('resource','resource_name','feedstock'),('scenario_name','scenario'),('price_offered','scenario_price_offered','price'),('production_total','production'),('production_unit',)]
   for opts in required:
    if not any(c in col for c in opts):raise ValueError(f'{name}: required column missing: {opts}')
   for line,r in enumerate(reader,2):
    resource=val(r,'resource','resource_name','feedstock').lower();scen=val(r,'scenario_name','scenario').lower()
    seen_scenarios.add(scen);seen_resources.add(resource)
    if scen!=scenario.lower() or resource not in CANON:
     excluded[(scen,resource)]+=1;continue
    rawfid=val(r,'fips').strip()
    if not re.fullmatch(r'[0-9]{1,5}(?:\.0+)?',rawfid):raise ValueError(f'{name}:{line} invalid county FIPS {rawfid!r}')
    fid=rawfid.split('.')[0].zfill(5)
    state=val(r,'state_name','state')
    if not state:raise ValueError(f'{name}:{line} missing state')
    unit=_normal(val(r,'production_unit'))
    if unit not in ('dt','dry_ton','dry_tons','dry_short_ton','dry_short_tons'):
     raise ValueError(f'{name}:{line}: ambiguous mass unit {unit!r}; DO NOT assume dry US short tons')
    try:
     price=float(val(r,'price_offered','scenario_price_offered','price').replace(',','').replace('$',''))
     quantity=float(val(r,'production_total','production').replace(',',''))
    except ValueError as e:raise ValueError(f'{name}:{line} invalid numeric quantity/price') from e
    if not (0<=quantity<1e10 and 0<=price<1e5):raise ValueError(f'{name}:{line} invalid negative or infinite quantity/price')
    key=(fid,resource,scen,price)
    if key in by:raise ValueError(f'DUPLICATE county+resource+scenario+price {key} in {name}:{line}; do not sum duplicated downloads')
    by[key]=dict(fips=fid,state=state,resource=resource,scenario=scen,price_usd_short_t=price,cumulative_dry_short_t=quantity,source=name)
 if not by:raise ValueError(f'ZERO matching data rows for scenario {scenario!r}; do not silently revert to analyst caps. Observed scenarios: {sorted(seen_scenarios)}; resources: {sorted(seen_resources)[:30]}')
 county_ids={key[0] for key in by};states={x['state'] for x in by.values()}
 complete=len(county_ids)>=min_counties and len(states)>=30
 if not complete and not allow_partial:raise ValueError(f'PARTIAL export: only {len(county_ids)} counties / {len(states)} states (minimum {min_counties}/30). Export *all US states* or pass --allow-partial for diagnostic only.')
 series=collections.defaultdict(list)
 for x in by.values():series[(x['fips'],x['resource'])].append(x)
 increments=[];zero=0
 for (fid,res),rows in series.items():
  prev=0.0
  for x in sorted(rows,key=lambda x:x['price_usd_short_t']):
   q=x['cumulative_dry_short_t']
   if q+1e-5<prev:raise ValueError(f'Nonmonotone offered-price supply {fid}/{res}: {q} < {prev}. Data may not be cumulative; inspect source before modelling.')
   dq=max(0,q-prev);prev=q
   if dq<=0:zero+=1;continue
   increments.append(dict(state=x['state'],fips=fid,resource=res,category=CANON[res],price_usd_short_t=x['price_usd_short_t'],incremental_mt=dq*SHORT_TO_METRIC/1e6))
 aggregated=collections.defaultdict(float)
 for x in increments:aggregated[(x['state'],x['resource'],x['price_usd_short_t'])]+=x['incremental_mt']
 tiers=[dict(state=state,resource=res,model_category=CANON[res],price_usd_short_t=price,available_mt=mt)
        for (state,res,price),mt in sorted(aggregated.items())]
 return dict(regional_data_present=True,national_coverage_unverified=not complete,coverage='NATIONAL_CANDIDATE_EXPORT' if complete else 'PARTIAL_DIAGNOSTIC_ONLY',
  scenario=scenario,counties=len(county_ids),states=len(states),county_resource_price_records=len(by),price_levels=sorted({k[3] for k in by}),
  source_sha256=sha,tiers=tiers,incremental_national_mt=sum(t['available_mt'] for t in tiers),zero_price_increments=zero,
  warnings=['BT23 offered price is farmgate in US$/dry short ton; delivered cost adds explicit logistics.',
    'BT23 resource mass is eligible supply under its source conditions, not a field-level claim.',
    'Corn stover includes field fractions; corn cobs/husks MUST NOT be separately added.',
    'All input category nutrient contents remain analyst chemistry assumptions until measured.',
    'Unrecorded processing residues excluded from this official primary-crop crosswalk.'])
def adapt_params(base,report,logistics_usd_metric_t=25,storage_usd_metric_t=10,price_year_multiplier=1.0,plant_field_fraction=0.60):
 """Replace all analyst crop categories in LP with official state/category/price tiers.

 Identical official county-resource flows at successive prices are differenced
 before modelling, so the LP never double counts a price-supply curve.
 """
 import copy
 from us97_circular_feedstocks import CANDIDATES,NPK_REC,NPK_WATER
 p=copy.deepcopy(base)
 if not report['regional_data_present'] or report['national_coverage_unverified']:
  raise ValueError('Cannot claim national BT23 model from absent/partial county export')
 old=p['CROP_RESIDUE'];chem={a[0]:dict(group=a[1],n=a[4],p=a[5],k=a[6],soc=a[7]) for a in CANDIDATES}
 tail=p['BIOMASS']['tiers'][len(old['feedstocks']):]
 feed=[];biomass=[]
 for x in report['tiers']:
  if x['available_mt']<=0:continue
  cat=x['model_category'];v=chem[cat];s=x['state'];r=x['resource'];price=x['price_usd_short_t']; cap=x['available_mt']
  eff={e:NPK_REC[e]*plant_field_fraction for e in 'npk'}
  npk={e:v[e] for e in 'npk'}
  fert=sum(npk[e]*(1-eff[e])*old['nutrient_replacement_usd_per_kg'][e] for e in 'npk')
  delivered=price/SHORT_TO_METRIC*price_year_multiplier+logistics_usd_metric_t+storage_usd_metric_t
  total=delivered+old['wastewater_treatment_usd_t']+old['hydrochar_testing_transport_usd_t']+fert
  label=f'BT23 {r} [{s}] ${price:g}/short ton'
  feed.append(dict(name=label,group=f'bt23_{r}_{s}',cap_mt=cap,elemental_kg_t=npk,
   recovered_fraction=eff,wastewater_recovered_share=NPK_WATER,stable_soc_c_t_per_dry_t=v['soc'],
   delivered_usd_t=delivered,source_status='BT23 county/price supply; nutrient chemistry and delivery adder are model assumptions'))
  biomass.append((label,cap,total))
 if not biomass:raise ValueError('No positive BT23 marginal tiers')
 old['feedstocks']=feed;old['group_caps_mt']={};old['cap_mt']=sum(t[1] for t in biomass);old['collect_min_mt']=0.0
 p['BIOMASS']['tiers']=biomass+tail
 p['bt23_assumption_metadata']=dict(coverage=report['coverage'],counties=report['counties'],tiers=len(feed),
  stage='NATIONAL INPUT INSTALLED IN LP: not geographically optimised siting',delivered_price_adder_usd_t=logistics_usd_metric_t+storage_usd_metric_t,
  plant_field_fraction=plant_field_fraction)
 return p
def export_files(report,target):
 target=Path(target);target.mkdir(parents=True,exist_ok=True)
 output={k:v for k,v in report.items() if k!='tiers'}
 (target/'BT23_IMPORT_AUDIT.json').write_text(json.dumps(output,indent=2))
 with (target/'BT23_STATE_RESOURCE_PRICE_INCREMENTS.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,['state','resource','model_category','price_usd_short_t','available_mt']);w.writeheader();w.writerows(report['tiers'])
def main():
 ap=argparse.ArgumentParser(description='Validate logged-in ORNL BT23 agricultural export and create LP supply tiers')
 ap.add_argument('files',nargs='+',help='Official CSV or ZIP exports')
 ap.add_argument('--scenario',default='mature-market medium');ap.add_argument('--allow-partial',action='store_true');ap.add_argument('--out',default='BT23_VALIDATED')
 a=ap.parse_args();report=ingest(a.files,scenario=a.scenario,allow_partial=a.allow_partial)
 export_files(report,a.out)
 print(json.dumps({k:v for k,v in report.items() if k not in ('tiers','source_sha256')},indent=2))
 if report['national_coverage_unverified']:print('WARNING: PARTIAL EXAMPLE -- DO NOT publish as national.')
if __name__=='__main__':main()
