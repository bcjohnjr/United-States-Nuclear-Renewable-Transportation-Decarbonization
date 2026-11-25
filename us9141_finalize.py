#!/usr/bin/env python3
"""Deterministic V9.14.1 editorial and author-clearance fixes applied AFTER us914_documents.py.

This script does not alter numerical calculations or source data. It updates
four DOCX outputs, figure provenance and the editorial upload ZIP. Run from
any current working directory. Avoids inventing author roles or image rights.
"""
from pathlib import Path
import csv
import zipfile
from docx import Document
from docx.shared import Pt

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
       ('Competing interests: The authors declare no competing interests. J. K. Bily’s association with Cloud Wash Laundry Corporation is disclosed for transparency.'),
       ('Author contributions: J. K. Bily conceptualization, computational investigation, original drafting and data curation; C. Pahl and P. Valdés Bacallao contributions and approval require confirmation from the individuals before journal submission.'):
       ('Author contributions: J. K. Bily: conceptualization, computational investigation, original drafting and data curation. All authors have reviewed and approved the final manuscript and its submission. Detailed CRediT contributions for C. Pahl and P. Valdés Bacallao must be supplied by the coauthors before submission metadata are finalized.'),
    })
    replace_where(DOCS[1], {
       'current V9.13 1,000-draw paired screen':'current V9.14 1,000-draw paired screen',
       'The complete V9.13 robustness workflow':'The V9.13-derived robustness workflow plus the V9.14 lifecycle audit',
       'current V9.13 stress screens':'current V9.14 stress screens',
       'Current V9.13 results':'Current V9.14 results',
    })
    replace_where(DOCS[2], {
       'Coauthor signoff, competing-interest/patent declarations and permission for any AI-generated figure remain pending author/editor verification.':
       'All named authors have read and approved the final manuscript and consent to its submission to Science. No external funding was received for this research. The authors declare no competing interests. J. K. Bily’s association with Cloud Wash Laundry Corporation is disclosed. The precise coauthor CRediT roles and any required AI-figure permissions must still be resolved before submission.'
    })
    replace_where(DOCS[3], {
       'Funding: None reported. Competing interests and author contributions: see manuscript; author and coauthor confirmation required before upload.':
       'Funding: No external funding was received for this research. Competing interests: The authors declare no competing interests; J. K. Bily’s association with Cloud Wash Laundry Corporation is disclosed in the manuscript. Author approval: All authors reviewed and approved the final manuscript and consent to submission. Detailed CRediT roles for C. Pahl and P. Valdés Bacallao remain to be supplied.'
    })
    # Keep the signature/contact together on one page; avoid a one-line second page.
    cover = Document(ROOT / DOCS[2])
    for para in cover.paragraphs:
        if para.style.name != 'Heading 1':
            para.paragraph_format.space_after = Pt(2)
            para.paragraph_format.line_spacing = 1.1
    cover.save(ROOT / DOCS[2])

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
    print('V9.14.1: editorial corrections, confirmed author approval and funding applied')

if __name__=='__main__':
    apply()
