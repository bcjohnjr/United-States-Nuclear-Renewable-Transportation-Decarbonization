#!/usr/bin/env python3
"""Deterministic V9.14.1 editorial fixes applied AFTER us914_documents.py.

This script does not alter numerical calculations or source data. It updates
four DOCX outputs, figure provenance and the editorial upload ZIP. Run from
any current working directory. Avoids inventing author roles or image rights.
"""
from pathlib import Path
import csv
import zipfile
from docx import Document

ROOT = Path(__file__).resolve().parent
DOCS = ('Research_Article_V9.14_Science.docx',
        'Supplementary_Materials_V9.14_Science.docx',
        'Cover_Letter_Science_V9.14.docx',
        'Title_Page_V9.14_Science.docx')

def replace_where(path, replacements):
    doc = Document(ROOT / path)
    hits = {old: 0 for old in replacements}
    for p in doc.paragraphs:
        s = p.text
        for old, new in replacements.items():
            if old in s:
                s = s.replace(old, new)
                hits[old] += 1
        if s != p.text:
            p.text = s
    for old, count in hits.items():
        if count == 0:
            raise AssertionError(f'Expected source text not found in {path}: {old}')
    doc.save(ROOT / path)
    print('UPDATED DOCX:', path, hits, flush=True)

def documents():
    replace_where(DOCS[0], {
       ('Competing interests: The corresponding author is associated with Cloud Wash Laundry Corporation. Financial interests, company involvement, related patents or applications, and all coauthor disclosures must be confirmed and completed by the authors before submission; no absence of conflicts or patents is certified by this package.'):
       ('Competing interests: The authors declare no competing interests, as confirmed by the corresponding author. J. K. Bily’s association with Cloud Wash Laundry Corporation is disclosed for transparency. This statement does not certify any third-party conflict-of-interest audit; relevant financial relationships or intellectual property must still be reported if applicable.'),
       ('Author contributions: J. K. Bily conceptualization, computational investigation, original drafting and data curation; C. Pahl and P. Valdés Bacallao contributions and approval require confirmation from the individuals before journal submission.'):
       ('Author contributions: J. K. Bily: conceptualization, computational investigation, original drafting and data curation. The corresponding author reports that all named human authors have approved submission. The precise CRediT roles of C. Pahl and P. Valdés Bacallao must be entered from verified author records; no roles have been inferred or invented.'),
    })
    replace_where(DOCS[1], {
       'current V9.13 1,000-draw paired screen':'current V9.14 1,000-draw paired screen',
       'The complete V9.13 robustness workflow':'The V9.13-derived robustness workflow plus the V9.14 lifecycle audit',
       'current V9.13 stress screens':'current V9.14 stress screens',
       'Current V9.13 results':'Current V9.14 results',
    })
    replace_where(DOCS[2], {
       'Coauthor signoff, competing-interest/patent declarations and permission for any AI-generated figure remain pending author/editor verification.':
       'The corresponding author reports that every named human author approved submission and that the authors declare no competing interests. The corresponding author’s Cloud Wash Laundry Corporation association is disclosed. Author contribution records and any AI-figure permissions still need independent editorial verification.'
    })
    replace_where(DOCS[3], {
       'Funding: None reported. Competing interests and author contributions: see manuscript; author and coauthor confirmation required before upload.':
       'Funding: None reported. Competing interests: The authors declare no competing interests, as confirmed by the corresponding author; Cloud Wash Laundry Corporation association disclosed in the manuscript. Author approval: confirmed by the corresponding author. Specific coauthor CRediT roles remain to be documented.'
    })

def provenance():
    path = ROOT / 'US914_EDITORIAL_FIGURE_PROVENANCE.csv'
    with path.open(newline='',encoding='utf-8') as f:
        original = list(csv.DictReader(f))
    assert len(original) == 35
    # A textual reference to a TIFF is an investigative lead, not proof of
    # generation or ownership. Distinguish it from directly verified creators.
    sources = {}
    for p in ROOT.glob('*.py'):
        if p.name.startswith(('us9141_','us914_validate','us912_validate','us911_validate')):
            continue
        try: content = p.read_text(encoding='utf-8')
        except UnicodeDecodeError: continue
        for r in original:
            if r['original_600dpi_tiff'] in content:
                sources.setdefault(r['original_600dpi_tiff'], []).append(p.name)
    headers = list(original[0]) + ['code_filename_references','source_verified_status']
    for r in original:
        k = r['editorial_name']
        if k in ('Figure_1.tif','Figure_5.tif','Figure_S30.tif'):
            r['source_class'] = 'Programmatic Matplotlib data plot, V9.14 generation script and numeric inputs verified'
            r['code_filename_references'] = 'us914_figures.py'
            r['source_verified_status'] = 'Verified code-derived plot; human rights and journal AI review still required'
        elif k in ('Figure_S1.tif','Figure_S22.tif'):
            r['code_filename_references'] = 'us99_figures.py; us91_journal_figures.py'
            r['source_verified_status'] = 'Engineering source/embedded pixels tested; external image rights not independently certified'
        else:
            r['code_filename_references'] = '; '.join(sorted(set(sources.get(r['original_600dpi_tiff'], []))))
            r['source_verified_status'] = 'Inherited; code filenames are leads only, origin/AI/permission review outstanding'
    with path.open('w',newline='',encoding='utf-8') as f:
        w = csv.DictWriter(f,fieldnames=headers); w.writeheader();w.writerows(original)

def editorial():
    with (ROOT/'US914_EDITORIAL_FIGURE_PROVENANCE.csv').open(newline='',encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    with zipfile.ZipFile(ROOT/'SCIENCE_EDITORIAL_UPLOAD_ONLY_V9.14.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for d in DOCS: z.write(ROOT/d,d)
        for r in rows: z.write(ROOT/r['original_600dpi_tiff'],r['editorial_name'])
    with zipfile.ZipFile(ROOT/'SCIENCE_EDITORIAL_UPLOAD_ONLY_V9.14.zip') as z:
        assert len(z.namelist())==39

def apply():
    documents();provenance();editorial()
    print('V9.14.1: editorial corrections and provenance register applied')

if __name__=='__main__':
    apply()
