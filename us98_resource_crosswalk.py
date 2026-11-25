#!/usr/bin/env python3
"""BT23/USDA resource crosswalk and conservative cap screens.
No downloaded county-level BT23 resource CSV ships with this package. In its
absence the code MUST NOT claim a geographically validated sustainable supply.
Use --bt23-csv path/to/actual_ornl_export.csv to parse official FIPS rows.
"""
from __future__ import annotations
from pathlib import Path
import argparse,csv,json,collections
R=Path(__file__).resolve().parent
FIPS={'AL':'Alabama','IA':'Iowa','IL':'Illinois'}
# Primary BT23 types differ from agricultural processing wastes and bagasse.
BT23_PRIMARY={'Corn stover','Wheat straw','Rice straw','Barley straw','Oats straw','Sorghum stubble','Cotton field residues'}
BT23_TO_V98={'Corn stover':'Corn stalks and leaves (excluding cobs/husks)','Wheat straw':'Wheat straw and chaff','Rice straw':'Rice straw','Barley straw':'Barley, oat and rye straw','Oats straw':'Barley, oat and rye straw','Sorghum stubble':'Grain sorghum stalks and leaves','Cotton field residues':'Cotton stalks'}
def csv_ingest(path,scenario='mature-market medium',price=70):
 totals=collections.defaultdict(float);counties=set();accepted=0
 with open(path,encoding='utf-8-sig',newline='') as f:
  for r in csv.DictReader(f):
   k={x.lower().replace(' ','_').strip():v for x,v in r.items()}
   typ=(k.get('resource') or k.get('feedstock') or '').strip()
   scen=(k.get('scenario_name') or k.get('scenario') or '').strip()
   price_s=k.get('price_offered') or k.get('price') or ''
   p=float(price_s or -1)
   if typ not in BT23_PRIMARY or scen!=scenario or abs(p-price)>.001:continue
   prod=float((k.get('production') or k.get('production_total') or '0').replace(',',''))
   if prod<0:raise ValueError('negative production')
   unit=(k.get('production_unit') or k.get('productionunit') or 'dt').lower()
   if unit not in ('dt','dry ton','dry tons','dry short tons'):raise ValueError('BT23 export mass unit must be documented dry SHORT tons: '+unit)
   state=k.get('state_name') or k.get('state') or 'unidentified';fid=k.get('fips') or 'unidentified'
   if fid=='unidentified':raise ValueError('no county FIPS: cannot claim geographic validation')
   totals[(state,typ)]+=prod*.90718474/1e6
   counties.add(fid);accepted+=1
 rows=[{'state':st,'bt23_resource':typ,'model_crosswalk':BT23_TO_V98[typ],'sustainable_screen_mt_dry':round(x,6),'source_scenario':scenario,'offered_usd_short_t':price} for (st,typ),x in sorted(totals.items())]
 return {'input':str(path),'records':accepted,'counties':len(counties),'rows':rows,'total_unique_mt':sum(x['sustainable_screen_mt_dry'] for x in rows),'warnings':['Crosswalk does not split corn stover into husks vs stalks; allocate only once','This is an economic supply scenario, not a farm-specific soil management plan']}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--bt23-csv');ap.add_argument('--scenario',default='mature-market medium');ap.add_argument('--price',type=float,default=70);a=ap.parse_args()
 if a.bt23_csv:
  report=csv_ingest(a.bt23_csv,a.scenario,a.price)
  with (R/'us98_bt23_regional_rows.csv').open('w',newline='') as f:
   w=csv.DictWriter(f,list(report['rows'][0]) if report['rows'] else ['state','bt23_resource','model_crosswalk','sustainable_screen_mt_dry','source_scenario','offered_usd_short_t']);w.writeheader();w.writerows(report['rows'])
 else:
  report={'source':'DOE BT23 ORNL county-level download tool; https://bioenergykdf.ornl.gov/bt23-agricultural-download',
   'regional_resource_data_present':False,'status':'NOT GEOGRAPHICALLY VALIDATED','no_county_inventories_in_release':True,
   'national_166mt_metric_ceiling':'Converted from ~183 million dry US short tons; includes primary crops only in BT23, not verified separate processing waste',
   'strict_screen':'Processing/fruit waste, bagasse and independent corn cobs/husks separated until state/processing data crosswalk verified.',
   'required_download':'Obtain original ORNL BT23 data by FIPS, resource, price, scenario; preserve competing uses, erosivity and price basis.'}
 (R/'US98_BT23_Resource_Audit.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))
if __name__=='__main__':main()
