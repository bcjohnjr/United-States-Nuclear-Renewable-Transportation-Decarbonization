#!/usr/bin/env python3
"""Build a single flat, all-in-one V9.12 ZIP plus contained clean editorial ZIP."""
from __future__ import annotations
import csv,hashlib,io,os,re,shutil,zipfile
from pathlib import Path
from PIL import Image
from docx import Document
R=Path(__file__).resolve().parent
DEST=Path('/mnt/data')
NAME='US_Transport_Decarbonisation_V9_12_SCIENCE_COMPLETE_YIELD_LCA_GRID_HARVESTER_TIFF_600dpi_FLAT.zip'
STAGE=DEST/'US_TRANSPORT_V9_12_RELEASE'
EDITOR='SCIENCE_EDITORIAL_UPLOAD_ONLY_V9.12.zip'
DOCS=['Research_Article_V9.12_Science.docx','Supplementary_Materials_V9.12_Science.docx',
      'Cover_Letter_Science_V9.12.docx','Title_Page_V9.12_Science.docx']
MAIN_FIGS=['ScienceFig1_V99_Conditional_Economics_and_LCA.tif',
           'ScienceFig2_V99_Crop_Economic_Selection.tif',
           'ScienceFig3_V99_Plant_Available_NPK_and_Carbon.tif',
           'ScienceFig4_V98_HTL_Return_Flow_With_Arrows.tif',
           'ScienceFig5_V99_Uncertainty_and_Reactor_Limits.tif']
KEEP_STATIC=['AEO2026_2050_TRANSPORT_DATA.zip','V911_DOCUMENT_MASTERS.zip',
 'BT23_REGIONAL_DATA_NEXT_STEPS_V910.md','BT23_AND_USDA_DOWNLOAD_INSTRUCTIONS_V9.9.md',
 'README_V9.12.md','V912_REFEREE_CHANGELOG.md','AUTHOR_SIGNOFF_REQUIRED_V912.md',
 'requirements-v912.txt','RUN_V912_VALIDATION.bat','RUN_V912_VALIDATION.sh','run_all.sh',
 'RUN_DOWNLOAD_OFFICIAL_BT23_DATA.bat','RUN_USDA_COUNTY_DATA.bat','RUN_V910_CHECK_BT23_EXPORT.bat']

def supplement_source_files():
    old2new={int(x['legacy_figure_id'][1:]):int(x['active_figure_id'][1:]) for x in csv.DictReader((R/'US912_FIGURE_CROSSWALK.csv').open())}
    mapping={}
    for old,new in old2new.items():
        if old==49:
            filenames=[R/'ScienceFigS49_V912_Terrestrial_HTL_Yield_BreakEven.tif']
        else:
            filenames=list(R.glob('FigS'+str(old)+'_*.tif'))+list(R.glob('ScienceFigS'+str(old)+'_*.tif'))
        assert len(filenames)==1,(old,new,[p.name for p in filenames])
        assert new not in mapping,new
        mapping[new]=filenames[0]
    assert sorted(mapping)==list(range(1,30)),sorted(mapping)
    return mapping

def build():
    if STAGE.exists():shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)
    mapping=supplement_source_files()
    files=set()
    # All active and historical TIFFs remain for code-backed reproducibility.
    for pattern in ('*.py','*.csv','*.json','*.tif'):
        for f in R.glob(pattern):
            if f.name.startswith('MANIFEST_V'):continue
            if f.name.endswith('_qa.png'):continue
            files.add(f.name)
    files.update(DOCS)
    files.update(KEEP_STATIC)
    for fn in sorted(files):
        assert (R/fn).is_file(),fn
        shutil.copy2(R/fn,STAGE/fn)
    # Clearly identify only the four current Word manuscripts; do not mix source masters into editorial upload.
    contents=[]
    with zipfile.ZipFile(STAGE/EDITOR,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
        for fn in DOCS:
            z.write(STAGE/fn,fn);contents.append(fn)
        for i,src in enumerate(MAIN_FIGS,1):
            assert (R/src).is_file(),src
            normalized=f'Figure_{i}.tif';z.write(R/src,normalized);contents.append(normalized)
        for i,src in sorted(mapping.items()):
            normalized=f'Figure_S{i}.tif';z.write(src,normalized);contents.append(normalized)
    assert len(contents)==38,(len(contents),contents)
    (STAGE/'EDITORIAL_UPLOAD_FILES_V912.txt').write_text(
       'For flagship Science submission, EXTRACT SCIENCE_EDITORIAL_UPLOAD_ONLY_V9.12.zip and upload its files individually as requested by the portal.\n'
       'Current documents: '+', '.join(DOCS)+'\nFive current main figures: Figure_1.tif to Figure_5.tif.\n'
       '29 sequential supplementary figure TIFFs: Figure_S1.tif through Figure_S29.tif.\n'
       'S1 is the Grid Harvester side/plan view; S22 is the Grid Harvester harvesting-energy efficiency chart.\n'
       'Do not upload source code or the outer complete ZIP as the single manuscript file; confirm journal-specific upload policy.\n'
       'Author approvals, journal policy, data availability and experimental calibration remain outstanding.\n',encoding='utf-8')
    # Auditable current-to-source file map, not just numerical old tag mapping.
    with (STAGE/'US912_EDITORIAL_FIGURE_PROVENANCE.csv').open('w',newline='',encoding='utf-8') as file:
        w=csv.writer(file);w.writerow(['editorial_name','original_600dpi_tiff'])
        for i,src in enumerate(MAIN_FIGS,1):w.writerow([f'Figure_{i}.tif',src])
        for i,src in sorted(mapping.items()):w.writerow([f'Figure_S{i}.tif',src.name])
    # Source checksum manifest excludes itself, avoids circular digest.
    manifest=STAGE/'MANIFEST_V9.12_SHA256.csv'
    with manifest.open('w',newline='',encoding='utf-8') as file:
        w=csv.writer(file);w.writerow(['filename','sha256','bytes'])
        for f in sorted(STAGE.iterdir()):
            if f.name==manifest.name:continue
            w.writerow([f.name,hashlib.sha256(f.read_bytes()).hexdigest(),f.stat().st_size])
    out=DEST/NAME
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
        for f in sorted(STAGE.iterdir()):z.write(f,f.name)
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None
        assert all('/' not in n for n in z.namelist())
        assert all(not n.lower().endswith(('.pdf','.png','.jpg','.jpeg')) for n in z.namelist())
        with zipfile.ZipFile(io.BytesIO(z.read(EDITOR))) as inner:
            assert inner.testzip() is None and len(inner.namelist())==38
            assert len([n for n in inner.namelist() if n.endswith('.tif')])==34
        print('ZIP',out,'BYTES',out.stat().st_size,'FILES',len(z.namelist()))
    return out
if __name__=='__main__':build()
