#!/usr/bin/env python3
"""Windows-assisted acquisition of logged-in ORNL BT23/USDA source files.

Does not scrape or bypass login. Opens the publisher's download portal; the user
saves the source export(s) into BT23_EXPORTS. Second run validates and zips.
"""
from __future__ import annotations
import sys,hashlib,json,shutil,zipfile,webbrowser
from pathlib import Path
from datetime import datetime,timezone
from us99_bt23_supply import ingest,export_files
ROOT=Path(__file__).resolve().parent
EXPORTS=ROOT/'BT23_EXPORTS';VALID=ROOT/'BT23_VALIDATED';OUT=ROOT/'BT23_USDA_COUNTY_DATA_FOR_V99.zip'
ORNL='https://bioenergykdf.ornl.gov/bt23-agricultural-download'
USDA='https://www.nass.usda.gov/Quick_Stats/'
def main():
 EXPORTS.mkdir(exist_ok=True)
 print('OFFICIAL BT23 PORTAL:',ORNL)
 print('Select Agriculture -> Agricultural residues; scenario mature-market medium; ALL U.S. states/counties; ALL offered-price tiers.')
 print('Download authenticated original CSV exports to:',EXPORTS)
 print('Keep different price-level exports separate. Do not save page HTML as a CSV.')
 paths=sorted(x for x in EXPORTS.iterdir() if x.suffix.lower() in ('.csv','.zip'))
 if not paths:
  webbrowser.open(ORNL);webbrowser.open(USDA)
  print('\nNO BT23 FILES YET. Login at ORNL, download CSV(s) to BT23_EXPORTS, then run the batch file again.')
  print('USDA Quick Stats may require a free API key; save its county CSV as supplemental source, not an independent residue supply.')
  return 2
 try: report=ingest(paths)
 except Exception as e:
  print('STRICT EXPORT VALIDATION FAILED:',e)
  print('Do NOT use this as a validated national resource input. Correct export filters and download again.')
  return 3
 export_files(report,VALID)
 prov=dict(website=ORNL,date_utc=datetime.now(timezone.utc).isoformat(),scenario=report['scenario'],
    counties=report['counties'],states=report['states'],price_levels=report['price_levels'],source_sha256=report['source_sha256'],
    volume_mt=report['incremental_national_mt'],must_not_claim='Field-level soil suitability and collection logistics remain to be validated')
 (VALID/'BT23_DOWNLOAD_PROVENANCE.json').write_text(json.dumps(prov,indent=2))
 with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for x in paths:z.write(x,arcname='ORIGINAL_BT23_'+x.name)
  for x in VALID.iterdir():
   if x.is_file():z.write(x,arcname=x.name)
 print('\nSUCCESS:',OUT,' (',OUT.stat().st_size,'bytes )')
 print('UPLOAD THIS SINGLE ZIP to ChatGPT and I can rerun regional-supply optimization.')
 return 0
if __name__=='__main__':sys.exit(main())
