#!/usr/bin/env python3
"""V9.12 substantive quick/full checks. Never conflate software PASS with scientific clearance.

Quick mode runs real scientific invariant, resource provenance, image and
publication-content tests. Full mode regenerates all current numerical outputs,
charts and Word files, and verifies pre-run release hashes.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,re,subprocess,sys,zipfile
from pathlib import Path
from PIL import Image
from docx import Document
import numpy as np
import us911_validate as prior
ROOT=Path(__file__).resolve().parent
OUT={'main':'Research_Article_V9.12_Science.docx','supp':'Supplementary_Materials_V9.12_Science.docx','title':'Title_Page_V9.12_Science.docx','letter':'Cover_Letter_Science_V9.12.docx'}

def sha_manifest():
    path=ROOT/'MANIFEST_V9.12_SHA256.csv'
    if not path.exists():
        print('MANIFEST V9.12 not present during pre-package; skipping hash check')
        return
    rows=list(csv.DictReader(path.open(encoding='utf-8')))
    assert rows,'manifest must not be empty'
    for r in rows:
        p=ROOT/r['filename'];assert p.is_file(),p
        assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'],p.name
    print('PASS: SHA-256 manifest',len(rows),'files')

def source_evidence():
    assert (ROOT/'V911_DOCUMENT_MASTERS.zip').is_file()
    with zipfile.ZipFile(ROOT/'V911_DOCUMENT_MASTERS.zip') as z:
        assert len([n for n in z.namelist() if n.endswith('.docx')])==4
    a=json.loads((ROOT/'BT23_UPLOADED_ARCHIVE_AUDIT_V910.json').read_text())
    assert a['csv_members']==0 and a['regional_data_present'] is False
    x=json.loads((ROOT/'US911_Robustness_Results.json').read_text())
    assert x['bt23_county_evidence'] is False
    with zipfile.ZipFile(ROOT/'AEO2026_2050_TRANSPORT_DATA.zip') as z:
        n=[x for x in z.namelist() if x.lower().endswith('.xlsx')]
        assert len(n)>=38,f'EIA archive has only {len(n)} workbooks'
    print('PASS: provenance: EIA workbooks present; county-level BT23 supply unavailable (not silently invented)')

def outputs():
    d=list(csv.DictReader((ROOT/'us912_terrestrial_htl_yield_sensitivity.csv').open(encoding='utf-8')))
    assert len(d)==6
    y=[float(a['htl_liquid_mwh_per_dry_metric_t']) for a in d]
    assert y==[1.2,1.6,2.0,2.3,2.6,3.0]
    for x in d:
        crop=float(x['crop_annual_bn']);no=float(x['no_crop_annual_bn']);saving=float(x['crop_saving_bn'])
        assert math.isclose(no-crop,saving,abs_tol=5e-6)
        assert crop>=0 and no>=0 and float(x['crop_selected_mt'])>=0
        if float(x['htl_liquid_mwh_per_dry_metric_t'])<=2.0:assert abs(saving)<1e-5
    baseline=d[4]
    assert abs(float(baseline['crop_saving_bn'])-6.7818855)<.005
    assert abs(float(d[3]['crop_saving_bn'])-1.574)<.01
    prior.numerics()  # 25 paired grid screens + land + field emissions, objective, NPK and original unit tests
    print('PASS: six matched HTL-yield sensitivities, mass balance, 25 delivered-price/capacity screens')

def compare_caption_image(doc,tag,filename):
    matches=[i for i,p in enumerate(doc.paragraphs) if p.text.startswith('Fig. '+tag+'.')]
    assert len(matches)==1,(tag,matches)
    p=doc.paragraphs[matches[0]-1]
    blips=p._p.xpath('.//*[local-name()="blip"]')
    assert len(blips)==1,tag
    rid=blips[0].get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
    with Image.open(io.BytesIO(doc.part.related_parts[rid].blob)) as im:
        got=im.convert('RGB')
    with Image.open(ROOT/filename) as im:
        want=im.convert('RGB')
        want.thumbnail((1850,1350) if tag=='S29' else (1650,1120))
    assert got.size==want.size,(tag,got.size,want.size)
    mse=np.mean((np.asarray(got,dtype=np.float32)-np.asarray(want,dtype=np.float32))**2)
    assert mse<6,(tag,mse)
    return float(mse)

def docs_figures():
    for p in ROOT.glob('*.tif'):
        with Image.open(p) as im:
            im.verify()
        with Image.open(p) as im:
            assert im.mode=='RGB' and all(abs(v-600)<1 for v in im.info.get('dpi',(0,0))),p.name
    for f in OUT.values():assert (ROOT/f).is_file()
    main=Document(ROOT/OUT['main']);si=Document(ROOT/OUT['supp'])
    assert len(main.inline_shapes)==5,len(main.inline_shapes)
    assert len(si.inline_shapes)==29,len(si.inline_shapes)
    assert len(si.tables)==16,len(si.tables)
    intro='\n'.join(p.text for p in main.paragraphs)
    n=next(i for i,p in enumerate(main.paragraphs) if p.text.strip()=='Abstract')
    count=len(main.paragraphs[n+1].text.split());assert 90<=count<=125,count
    assert '2.0 MWh' in intro and '2.6 MWh' in intro
    assert 'unavailable' in intro.lower() and 'author contributions' in intro.lower()
    assert '26.' in intro and '27.' in intro
    valid=[]
    for i,p in enumerate(si.paragraphs):
        m=re.match(r'^Fig\. S(\d+)\.',p.text)
        if m and i>0 and si.paragraphs[i-1]._p.xpath('.//*[local-name()="blip"]'):
            valid.append(int(m.group(1)))
    assert valid==list(range(1,30)),valid
    print('PASS: sequential embedded Figure atlas S1–S29, Word content and 16 tables')
    for tag,f in [('S1','FigS1_grid_harvester.tif'),('S22','FigS22_GridHarvester_Energy_Efficiency.tif'),('S29','ScienceFigS49_V912_Terrestrial_HTL_Yield_BreakEven.tif')]:
        mse=compare_caption_image(si,tag,f)
        print('PASS: actually embedded',tag,'image matches 600-dpi source',f,'MSE',round(mse,2))
    with (ROOT/'us91_grid_harvester_efficiency.csv').open(encoding='utf-8') as file:
        rows=list(csv.DictReader(file))
    assert len(rows)==5
    values=[float(x['energy_mj_per_1_44ha_cycle']) for x in rows]
    for got,expected in zip(values,(90.9,55.6,33.9,23.8,20.3)):
        assert math.isclose(got,expected,abs_tol=1e-8),(got,expected)
    assert abs(100*(1-33.9/90.9)-62.7)<.2
    print('PASS: Grid Harvester all five cycle energies and 62.7% metric')

def quick():
    source_evidence();outputs();docs_figures()
    print('V9.12 PASS: substantive code, figures and editorial tests. NOT empirically validated or author-cleared.')

def full(draws):
    sha_manifest()  # Must check the distributed archive BEFORE rewriting any outputs.
    steps=[['us9_test.py'],['us99_agricultural_accounts.py','--fixed-hubs'],['us99_paired_uncertainty.py',str(draws)],
           ['us99_figures.py'],['us911_robustness.py'],['us911_figures.py'],
           ['us912_yield_sensitivity.py'],['us912_figures.py'],['us912_documents.py']]
    for args in steps:
        print('REGENERATE:', ' '.join(args),flush=True)
        subprocess.run([sys.executable,*args],cwd=ROOT,check=True)
    quick()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--full',action='store_true')
    ap.add_argument('--draws',type=int,default=150)
    args=ap.parse_args()
    if args.full:full(args.draws)
    else:
        sha_manifest();quick()
if __name__=='__main__':main()
