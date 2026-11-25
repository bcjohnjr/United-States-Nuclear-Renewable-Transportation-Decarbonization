#!/usr/bin/env python3
"""V9.10 BT23 authenticated-download intake: FAIL CLOSED on empty/partial exports.

This is an acquisition and provenance gate, not an attempt to bypass ORNL login.
It never relabels analyst resource caps as observed county quantities.

Usage:
 python us910_bt23_evidence_gate.py --inspect BT23_EXPORTS.zip
 python us910_bt23_evidence_gate.py --inspect BT23_EXPORTS/\n
 After official export of ALL state/price tiers:
 python us910_bt23_evidence_gate.py --validate BT23_EXPORTS/ --attest-all-states-prices
 python us910_bt23_evidence_gate.py --model BT23_EXPORTS/ --attest-all-states-prices
"""
from __future__ import annotations
import argparse,hashlib,json,sys,zipfile
from datetime import datetime,timezone
from pathlib import Path
from us99_bt23_supply import ingest,adapt_params,export_files
ROOT=Path(__file__).resolve().parent
PORTAL='https://bioenergykdf.ornl.gov/bt23-agricultural-download'


def candidates(path):
 p=Path(path)
 if p.is_dir():
  files=sorted(q for q in p.rglob('*') if q.is_file() and q.suffix.lower() in ('.csv','.zip'))
  # Do not traverse sample/diagnostic archives unless explicitly chosen.
  return files
 if p.is_file():return [p]
 raise FileNotFoundError(f'No BT23 export at {path}; download official CSV/ZIP and put it in BT23_EXPORTS/')


def inventory(paths):
 records=[];csv_count=0
 for p in paths:
  if p.suffix.lower()=='.csv':
   csv_count+=1;records.append(dict(path=p.name,bytes=p.stat().st_size,csv_members=1,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
  elif p.suffix.lower()=='.zip':
   with zipfile.ZipFile(p) as z:
    corrupt=z.testzip();
    if corrupt:raise ValueError(f'Corrupt ZIP member: {corrupt}')
    names=[i.filename for i in z.infolist() if not i.is_dir()]
    csvs=[x for x in names if x.lower().endswith('.csv')]
    csv_count+=len(csvs)
    records.append(dict(path=p.name,bytes=p.stat().st_size,csv_members=len(csvs),file_members=names[:80],sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
  else:raise ValueError(f'Expected CSV or ZIP, got {p.name}')
 return {'files':records,'csv_members':csv_count}


def status_write(result,path):
 result['checked_utc']=datetime.now(timezone.utc).isoformat();result['official_portal']=PORTAL
 Path(path).write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')


def main(argv=None):
 ap=argparse.ArgumentParser(description='Official BT23 CSV/ZIP evidence gate; does not authenticate or fabricate data')
 mode=ap.add_mutually_exclusive_group(required=True)
 mode.add_argument('--inspect',metavar='EXPORT');mode.add_argument('--validate',metavar='EXPORT');mode.add_argument('--model',metavar='EXPORT')
 ap.add_argument('--attest-all-states-prices',action='store_true',help='You personally confirm portal filters include all U.S. states/counties, all offered-price levels and one exact scenario. This is an attestation, not independent completeness validation.')
 ap.add_argument('--out',default='BT23_V910_EVIDENCE_STATUS.json')
 ap.add_argument('--minimum-county-count',type=int,default=1000)
 a=ap.parse_args(argv);source=a.inspect or a.validate or a.model
 report={'archive_path':str(source),'regional_data_present':False,'usable_as_national_reference':False,'access_status':'NOT_YET_VERIFIED'}
 try:
  files=candidates(source);report.update(inventory(files))
  if report['csv_members']==0:
   report['status']='EMPTY_DIRECTORY_OR_ZIP';report['action']='The archive has zero CSV data. Use ORNL authenticated download; saving an empty folder as ZIP is not an export.'
   status_write(report,a.out);print('BT23 IMPORT BLOCKED: ZERO CSV FILES; NO COUNTY RECORDS.',file=sys.stderr);print('Read:',a.out);return 2
  if a.inspect:
   report['status']='CSV_PRESENT_BUT_NOT_VERIFIED';report['action']='Run --validate after complete official export; --inspect only inventories files.'
   status_write(report,a.out);print('CSV present: NOT validated or included in optimisation.');return 0
  # A partial export is a diagnostic, never silently treated as national.
  try: data=ingest(files,allow_partial=True,min_counties=a.minimum_county_count)
  except Exception as e:
   report['status']='REJECTED_SOURCE_ROWS';report['detail']=str(e);status_write(report,a.out);print('IMPORT REJECTED:',e,file=sys.stderr);return 3
  report.update(dict(counties=data['counties'],states=data['states'],price_levels=data['price_levels'],resources=sorted({t['resource'] for t in data['tiers']}),price_tiers=len(data['tiers']),incremental_national_mt=data['incremental_national_mt'],source_sha256=data['source_sha256']))
  deficiencies=[]
  if data['counties']<a.minimum_county_count:deficiencies.append('County count below screening minimum; incomplete national export suspected')
  if data['states']<30:deficiencies.append('Fewer than 30 states; incomplete national export suspected')
  if len(data['price_levels'])<2:deficiencies.append('Only one offered-price tier: cannot infer a price-dependent supply curve')
  if len({t['resource'] for t in data['tiers']})<3:deficiencies.append('Too few field residue types for comprehensive agricultural resource crosswalk')
  if not a.attest_all_states_prices:deficiencies.append('User has not confirmed filters included all U.S. states and price tiers')
  if deficiencies:
   report['status']='PARTIAL_OR_UNATTESTED';report['deficiencies']=deficiencies
   report['action']='Obtain a complete official export or rerun with --attest-all-states-prices only if the ORNL export filters were verified.'
   status_write(report,a.out);print('BT23: NOT NATIONAL-READY:','; '.join(deficiencies),file=sys.stderr);return 4
  report['status']='NATIONAL_CANDIDATE_WITH_USER_ATTESTATION';report['regional_data_present']=True
  report['usable_as_national_reference']=True
  report['caveat']='User-attested coverage; county soil suitability, logistics, spatial siting and resource chemistry still need verification.'
  export_files(data,ROOT/'BT23_VALIDATED')
  if a.model:
   from us99_agricultural_accounts import analyse
   # analyse consumes exact records, replaces analyst category tiers with eligible BT23 price/commodity increments and runs national LP.
   results=analyse(files,include_fixed=False)
   report['model_complete']=True;report['bt23_case']=[dict(case=z['case'],annual_cost_bn=z['annual_cost_bn'],crop_mt=z['crop_htl_mt']) for z in results['scenarios'] if 'BT23' in z['case']]
  status_write(report,a.out)
  # Produce the SINGLE shareable output archive, not an empty folder ZIP.
  export=ROOT/'BT23_OFFICIAL_COUNTY_EXPORT_FOR_V910.zip'
  idx=0
  with zipfile.ZipFile(export,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
   z.write(a.out,arcname='BT23_V910_EVIDENCE_STATUS.json')
   for source in files:
    if source.suffix.lower()=='.csv':
     idx+=1;z.write(source,arcname=f'ORIGINAL_BT23_{idx:03d}_{source.name}')
    else:
     with zipfile.ZipFile(source) as original:
      for entry in original.infolist():
       if not entry.is_dir() and entry.filename.lower().endswith('.csv'):
        idx+=1
        z.writestr(f'ORIGINAL_BT23_{idx:03d}_{Path(entry.filename).name}', original.read(entry))
   for more in ('BT23_IMPORT_AUDIT.json','BT23_STATE_RESOURCE_PRICE_INCREMENTS.csv'):
    path=ROOT/'BT23_VALIDATED'/more
    if path.exists():z.write(path,arcname=more)
  print('PASS:',report['status'],'county count',report['counties'],'price levels',len(report['price_levels']))
  print('UPLOAD THIS ONE ZIP:',export)
  return 0
 except Exception as e:
  report['status']='REJECTED_INPUT';report['detail']=str(e);status_write(report,a.out);print('ERROR:',e,file=sys.stderr);return 5
if __name__=='__main__':sys.exit(main())
