#!/usr/bin/env python3
"""Create one flat, hash-manifested V9.11 research archive.
Legacy Word documents excluded except source templates needed for audit/build.
"""
from pathlib import Path
import zipfile,shutil,csv,hashlib,sys,json
ROOT=Path(__file__).resolve().parent
STAGE=Path('/mnt/data/US_TRANSPORT_V9_11_RELEASE')
ZIP=Path('/mnt/data/US_Transport_Decarbonisation_V9_11_SCIENCE_CROP_NPK_LCA_DELIVERED_COST_GRID_HARVESTER_TIFF_600dpi_FLAT.zip')
KEEP_DOCS={
'Research_Article_V9.11_Science.docx','Supplementary_Materials_V9.11_Science.docx','Cover_Letter_Science_V9.11.docx','Title_Page_V9.11_Science.docx',
'SOURCE_V910_Research_Article_V9.10_Science.docx','SOURCE_V910_Supplementary_Materials_V9.10_Science.docx','SOURCE_V910_Cover_Letter_Science_V9.10.docx','SOURCE_V910_Title_Page_V9.10_Science.docx',
'SOURCE_MASTER_V98_Research_Article.docx','SOURCE_MASTER_V98_Supplementary_Materials.docx','SOURCE_MASTER_V98_Cover_Letter.docx','SOURCE_MASTER_V98_Title_Page.docx'
}
KEEP_MD={'README_V9.11.md','V911_CHANGELOG.md','AUTHOR_SIGNOFF_REQUIRED_V911.md',
'BT23_AND_USDA_DOWNLOAD_INSTRUCTIONS_V9.9.md','BT23_REGIONAL_DATA_NEXT_STEPS_V910.md'}
KEEP_BAT={'RUN_V911_VALIDATION.bat','RUN_V910_CHECK_BT23_EXPORT.bat','RUN_DOWNLOAD_OFFICIAL_BT23_DATA.bat','RUN_USDA_COUNTY_DATA.bat'}
KEEP_SH={'RUN_V911_VALIDATION.sh','run_all.sh'}
KEEP_TXT={'requirements-v99.txt','requirements-v911.txt','EDITORIAL_UPLOAD_FILES_V911.txt'}
def keep(p):
 if p.suffix.lower() in {'.py','.csv','.json','.tif'}:return True
 if p.suffix.lower()=='.zip':return p.name=='AEO2026_2050_TRANSPORT_DATA.zip'
 if p.suffix.lower()=='.docx':return p.name in KEEP_DOCS
 if p.suffix.lower()=='.md':return p.name in KEEP_MD
 if p.suffix.lower()=='.bat':return p.name in KEEP_BAT
 if p.suffix.lower()=='.sh':return p.name in KEEP_SH
 if p.suffix.lower()=='.txt':return p.name in KEEP_TXT
 return False

def main():
 if STAGE.exists():shutil.rmtree(STAGE)
 STAGE.mkdir()
 files=[]
 for p in sorted(ROOT.iterdir()):
  if not p.is_file() or not keep(p) or p.name=='MANIFEST_V9.11_SHA256.csv':continue
  target=STAGE/p.name
  shutil.copy2(p,target)
  files.append(target)
 assert len(list(STAGE.glob('*.tif')))==64, len(list(STAGE.glob('*.tif')))
 assert len([p for p in files if p.suffix=='.docx'])==12
 assert len([p for p in files if p.name.startswith('Research_Article_V9.11')])==1
 m=STAGE/'MANIFEST_V9.11_SHA256.csv'
 with m.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['filename','sha256','bytes']);w.writeheader()
  for p in sorted(files,key=lambda x:x.name):w.writerow({'filename':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
 with zipfile.ZipFile(ZIP,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(STAGE.iterdir()):z.write(p,arcname=p.name)
 with zipfile.ZipFile(ZIP) as z:
  assert z.testzip() is None
  assert all('/' not in n for n in z.namelist())
  n=len(z.namelist())
 print('PACKAGED',ZIP,'files',n,'MB',round(ZIP.stat().st_size/1048576,2))
 return ZIP
if __name__=='__main__':main()
