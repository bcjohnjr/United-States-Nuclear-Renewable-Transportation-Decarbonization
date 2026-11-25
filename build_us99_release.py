#!/usr/bin/env python3
"""Build flat Science V9.9 release; Grid Harvester cannot be omitted."""
from pathlib import Path
import zipfile,hashlib,csv,json
R=Path(__file__).resolve().parent
OUT=R.parent/'US_Transport_Decarbonisation_V9_9_SCIENCE_COMPLETE_GRID_HARVESTER_BT23_DOWNLOADER_600dpi_TIFF_FLAT.zip'
DOCS=['Research_Article_V9.9_Science.docx','Supplementary_Materials_V9.9_Science.docx','Cover_Letter_Science_V9.9.docx','Title_Page_V9.9_Science.docx']
MANDATORY=['FigS1_grid_harvester.tif','FigS22_GridHarvester_Energy_Efficiency.tif','grid_harvester.py','us91_grid_harvester_efficiency.csv','us99_validate.py','RUN_V99_VALIDATION.bat','RUN_DOWNLOAD_OFFICIAL_BT23_DATA.bat','us99_get_regional_data.py','us99_bt23_supply.py']
INCLUDE_DOCS=[x for x in R.glob('SOURCE_MASTER_V98_*.docx')]
# Source scripts, every model output and archived scientific TIFF; no QA PNG/JPG/PDF
files={p.name:p for p in R.iterdir() if p.is_file() and p.suffix.lower() in ('.py','.csv','.json','.tif','.bat','.sh')}
for fname in DOCS+MANDATORY+['AEO2026_2050_TRANSPORT_DATA.zip','README_V9.9.md','BT23_AND_USDA_DOWNLOAD_INSTRUCTIONS_V9.9.md','requirements-v99.txt']:
 p=R/fname;assert p.exists(),f'MISSING RELEASE INPUT {p}';files[p.name]=p
for p in INCLUDE_DOCS:files[p.name]=p
for r in ('requirements-v98.txt','MANIFEST_V9.8_SHA256.csv','README_V9.8.md'):
 files.pop(r,None)
# Drop legacy source artifacts already represented as source masters or current docs
for k in list(files):
 if k.startswith('SOURCE_BASE_') or k.startswith('MANIFEST_V') or k.endswith('_qa.tif'):files.pop(k,None)
# Explicitly disallow older or duplicate DOCX in user submission set
assert all((not k.endswith('.docx') or k in DOCS or k.startswith('SOURCE_MASTER_V98_')) for k in files)
# Mandatory Grid Harvester regression
for k in MANDATORY:assert k in files
rows=[(n,hashlib.sha256(p.read_bytes()).hexdigest(),p.stat().st_size) for n,p in sorted(files.items())]
manifest='filename,sha256,bytes\n'+''.join(f'{n},{h},{size}\n' for n,h,size in rows)
with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for n,p in sorted(files.items()):z.write(p,arcname=n)
 z.writestr('MANIFEST_V9.9_SHA256.csv',manifest)
assert OUT.stat().st_size>1_000_000
with zipfile.ZipFile(OUT) as z:
 assert z.testzip() is None
 names=z.namelist();assert len(names)==len(set(names));assert all('/' not in x for x in names)
 assert not any(x.lower().endswith(('.png','.jpg','.jpeg','.pdf')) for x in names)
 for k in MANDATORY:assert k in names
 assert all(hashlib.sha256(z.read(n)).hexdigest()==h for n,h,_ in rows)
 fig=[x for x in names if x.endswith('.tif')]
 print('RELEASE',OUT.name,round(OUT.stat().st_size/1024/1024,2),'MiB',len(names),'files',len(fig),'TIFFs')
 print('MANDATORY S1+S22 GRID HARVESTER included and manifested')
