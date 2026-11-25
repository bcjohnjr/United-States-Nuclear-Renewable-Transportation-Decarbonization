#!/usr/bin/env python3
"""Obtain independent county harvest-area cross-checks from USDA NASS Quick Stats.

This API is not a replacement for DOE/ORNL BT23 residue removal supply curves.
Requires the user's own free USDA-NASS API key. No key is written to disk or logs.
"""
from __future__ import annotations
import argparse,csv,io,os,sys,json,hashlib,zipfile,getpass,time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parent
API='https://quickstats.nass.usda.gov/api/api_GET/'
COMMODITIES=['CORN','WHEAT','SOYBEANS','RICE','SORGHUM','COTTON','BARLEY','OATS']
def fetch(key,crop,year,output):
 params={'key':key,'commodity_desc':crop,'year':str(year),'agg_level_desc':'COUNTY',
         'statisticcat_desc':'AREA HARVESTED','domain_desc':'TOTAL','unit_desc':'ACRES','format':'CSV'}
 # source_desc sometimes filters away a legitimate county crop result; keep both
 # SURVEY and CENSUS observations, labeling each row's actual source.
 url=API+'?'+urlencode(params)
 req=Request(url,headers={'User-Agent':'US-transport-academic-supply-crosscheck/9.9','Accept':'text/csv'})
 with urlopen(req,timeout=60) as r:raw=r.read()
 if len(raw)>300_000_000:raise ValueError('Unexpectedly large USDA API response')
 body=raw.decode('utf-8-sig')
 if body.lstrip().startswith('{') or '<html' in body.lower()[:500]:raise ValueError('USDA API returned error/HTML rather than CSV. Check key and query limits. '+body[:150].replace(key,'[REDACTED]'))
 reader=csv.DictReader(io.StringIO(body));head={x.lower().strip() for x in reader.fieldnames or []}
 if not {'year','state_name','county_name','value','commodity_desc','agg_level_desc'}.issubset(head):raise ValueError('USDA expected CSV header absent: '+str(reader.fieldnames))
 rows=list(reader)
 if not rows:raise ValueError('No USDA county crop observations (not a zero supply estimate)')
 if any(x.get('agg_level_desc','').upper()!='COUNTY' for x in rows):raise ValueError('Unexpected mixed geography in USDA API response')
 output.write_bytes(raw)
 return {'commodity':crop,'year':year,'source':'USDA NASS Quick Stats','records':len(rows),
         'states':len({x.get('state_name') for x in rows}),'sha256':hashlib.sha256(raw).hexdigest(),'file':output.name,
         'note':'Harvested acreage only: cannot infer sustainable removable straw, husks or delivered prices from acres alone'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--year',action='append',type=int,default=[]);a=ap.parse_args()
 years=a.year or [2022,2023]
 key=os.environ.get('NASS_API_KEY') or getpass.getpass('Enter USDA NASS Quick Stats API key (not stored): ').strip()
 if not key:raise ValueError('API key is required. Register at https://quickstats.nass.usda.gov/api')
 output=ROOT/'USDA_QUICKSTATS_COUNTY';output.mkdir(exist_ok=True)
 reports=[];fail=[]
 for yr in years:
  for c in COMMODITIES:
   target=output/f'USDA_NASS_{c}_{yr}_COUNTY.csv'
   try:
    reports.append(fetch(key,c,yr,target));print('DOWNLOADED',target.name,reports[-1]['records'],'observations',flush=True)
   except Exception as e:
    fail.append(dict(year=yr,crop=c,error=str(e).replace(key,'[REDACTED]')))
    print('UNAVAILABLE',yr,c,str(e).replace(key,'[REDACTED]')[:180],flush=True)
   time.sleep(.25)
 manifest={'year_list':years,'source':'https://quickstats.nass.usda.gov/api/','successes':reports,'failures':fail,
           'limitation':'USDA harvested acreage does not establish agronomic sustainable removal; paired DOE BT23 offered-price residues required.'}
 (output/'USDA_SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
 path=ROOT/'USDA_QUICKSTATS_COUNTY_V99.zip'
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
  for f in sorted(output.iterdir()):
   if f.is_file():z.write(f,arcname=f.name)
 print('READY',path,'successful crop-years',len(reports),'failed',len(fail))
 print('Attach resulting ZIP with the ORNL BT23 export ZIP. No data are silently invented.')
 return 0 if reports else 3
if __name__=='__main__':sys.exit(main())
