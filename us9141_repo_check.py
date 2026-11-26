#!/usr/bin/env python3
"""GitHub/workspace-independent static, editorial and release preflight.

Invoked from any CWD; requires only source files at the checkout root.
All Python scripts are syntax-checked without importing legacy entrypoints.
"""
import ast
import csv
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path
from docx import Document
from PIL import Image

ROOT=Path(__file__).resolve().parent

def run():
    pyfiles=sorted(ROOT.glob('*.py'))
    assert len(pyfiles)>=40, 'missing source scripts; did the flat ZIP unpack in a repository subfolder?'
    bad=[]
    for file in pyfiles:
        try: compile(file.read_bytes(),str(file),'exec')
        except Exception as e: bad.append((file.name,str(e)))
    assert not bad, f'Python syntax failures: {bad}'
    manifest=list(csv.DictReader((ROOT/'MANIFEST_V9.14_SHA256.csv').open(encoding='utf-8-sig')))
    named={r['filename'] for r in manifest}
    actual={p.name for p in ROOT.iterdir() if p.is_file() and p.name != 'MANIFEST_V9.14_SHA256.csv'}
    assert named==actual, f'Untracked/absent flat root files: missing={sorted(named-actual)}, untracked={sorted(actual-named)}'
    assert all('/' not in x and '\\' not in x for x in named)
    for r in manifest:
        assert hashlib.sha256((ROOT/r['filename']).read_bytes()).hexdigest()==r['sha256'],r['filename']
    for f in ('US913_Paired_Uncertainty_Summary.json','us913_paired_uncertainty.csv'):
        assert (ROOT/('V913_ORIGINAL__'+f)).is_file(), f
    audit=list(csv.DictReader((ROOT/'V913_V914_CORRECTED_LEGACY_AUDIT.csv').open()))
    assert len(audit)>=7
    for row in audit:
        fn=row['filename']
        if fn in ('US913_Paired_Uncertainty_Summary.json','us913_paired_uncertainty.csv'):
            assert hashlib.sha256((ROOT/('V913_ORIGINAL__'+fn)).read_bytes()).hexdigest()==row['v913_sha256']
    m=Document(ROOT/'Research_Article_V9.14_Science.docx')
    si=Document(ROOT/'Supplementary_Materials_V9.14_Science.docx')
    cover=Document(ROOT/'Cover_Letter_Science_V9.14.docx')
    title=Document(ROOT/'Title_Page_V9.14_Science.docx')
    t='\n'.join(p.text for p in m.paragraphs)
    s='\n'.join(p.text for p in si.paragraphs)
    assert 'The authors declare no competing interests' in t
    assert 'Cloud Wash Laundry Corporation' in t
    assert 'all named human authors have approved submission' in t
    assert 'precise CRediT roles' in t
    assert 'current V9.13' not in s and 'Current V9.13 results' not in s
    assert 'current V9.14 1,000-draw paired screen' in s
    assert 'The corresponding author reports that every named human author approved' in '\n'.join(p.text for p in cover.paragraphs)
    assert 'Specific coauthor CRediT roles' in '\n'.join(p.text for p in title.paragraphs)
    with (ROOT/'US914_EDITORIAL_FIGURE_PROVENANCE.csv').open(newline='') as f:prov=list(csv.DictReader(f))
    assert len(prov)==35 and all('source_verified_status' in p for p in prov)
    for p in prov:
        if p['editorial_name'] in ('Figure_1.tif','Figure_5.tif','Figure_S30.tif'):
            assert 'V9.14 generation' in p['source_class']
        assert (ROOT/p['original_600dpi_tiff']).is_file()
    with zipfile.ZipFile(ROOT/'SCIENCE_EDITORIAL_UPLOAD_ONLY_V9.14.zip') as z:
        assert len(z.namelist())==39
        for doc in ('Research_Article_V9.14_Science.docx','Supplementary_Materials_V9.14_Science.docx','Cover_Letter_Science_V9.14.docx','Title_Page_V9.14_Science.docx'):
            assert z.read(doc)==(ROOT/doc).read_bytes()
        for p in prov:assert z.read(p['editorial_name'])==(ROOT/p['original_600dpi_tiff']).read_bytes()
    assert all(p.stat().st_size<100_000_000 for p in ROOT.iterdir() if p.is_file()), 'GitHub 100MB file cap exceeded'
    assert (ROOT/'GITHUB_ACTIONS_US_TRANSPORT_V9141.yml').is_file()
    print(f'PASS: {len(pyfiles)} flat-root Python files parse; {len(manifest)} rooted hashes; current manuscript/declarations; all 35 editorial images; GitHub single-file limit',flush=True)

if __name__=='__main__':run()
