#!/usr/bin/env python3
"""Minimal V9.13 edits to authoritative V9.12 Science documents.

Preserves user-mandated Grid Harvester S1/S22 embedded bitmaps and supplement order;
replaces only the two corrected main figures; adds one two-factor supplementary figure.
"""
from pathlib import Path
import csv,io,json,re,zipfile
from PIL import Image
from docx import Document
from docx.shared import Inches,Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph
R=Path(__file__).resolve().parent
BASE='V9.12'
NEW='V9.13'
SOURCE='V912_DOCUMENT_MASTERS.zip'
def source_doc(name):
    with zipfile.ZipFile(R/SOURCE) as z:return Document(io.BytesIO(z.read(name)))
MAIN='Research_Article_V9.13_Science.docx';SUP='Supplementary_Materials_V9.13_Science.docx'
LETTER='Cover_Letter_Science_V9.13.docx';TITLE='Title_Page_V9.13_Science.docx'
AI_DISCLOSURE=(
  'Artificial intelligence: Artificial Inventor / Synthetic Scientist V63 and ChatGPT (OpenAI, GPT-6) assisted with model code, data analysis, manuscript drafting/editing and reproducible numerical graphics. '
  'Human authors are responsible for the methods, source verification, interpretation and figure provenance. '
  'The complete historical prompt record is not certified as available, and any permission required for AI-assisted artwork must be resolved with the journal. '
  'AI systems are not authors; this statement and the associated provenance inventory require human-author confirmation.')

def add_after(p,text):
    el=OxmlElement('w:p');p._p.addnext(el);q=Paragraph(el,p._parent);q.style='Normal';q.add_run(text);return q

def picture_blob(path,dimensions=(1800,1350)):
    with Image.open(path) as im:
        rgb=im.convert('RGB');rgb.thumbnail(dimensions)
        data=io.BytesIO();rgb.save(data,format='PNG',optimize=True);return data.getvalue(),rgb.size

def replace_inline(d,index,src):
    sh=d.inline_shapes[index]
    el=sh._inline
    blip=el.xpath('.//*[local-name()="blip"]')
    assert len(blip)==1
    rid=blip[0].get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
    part=d.part.related_parts[rid]
    blob,size=picture_blob(R/src)
    part._blob=blob
    sh.width=Inches(6.55)
    sh.height=Inches(6.55*size[1]/size[0])
    print('Replaced main image',index,src,size)

def main():
    d=source_doc('Research_Article_V9.12_Science.docx')
    summary=json.loads((R/'US913_Paired_Uncertainty_Summary.json').read_text())
    # Rewrite only known blocks, preserving the five figure anchor paragraphs.
    for p in d.paragraphs:
        s=p.text
        if 'A 150-draw paired conditional uncertainty screen' in s:
            p.text=(f"A {summary['n_requested']:,}-draw paired parameter screen samples terrestrial HTL yield, "
                f"crop-delivery charges separately from wastewater and nutrient expenses, and bounded agricultural field-emissions assumptions. "
                f"Conditional abatement cost has a median ${summary['median_usd_t']:.1f}/t CO₂e "
                f"(5th–95th percentile ${summary['p05_usd_t']:.1f}–${summary['p95_usd_t']:.1f}/t). "
                f"In {100*summary['zero_crop_fraction']:.1f}% of draws, the optimizer selects no crop residues. "
                'These assumed distributions are diagnostic, not empirical national probabilities; nuclear hub-count screens still omit 8,760-hour dispatch feasibility.')
        elif s.startswith('Fig. 5.'):
            p.text=('Fig. 5. Paired 1,000-draw conditional uncertainty screen, now varying HTL liquid yield, biomass-delivery costs and agricultural lifecycle assumptions; fixed-reactor deployment comparison retains joint-conservative soil constraints. Ranges are analyst-specified, not calibrated probabilities.')
        elif 'The V9.9 alternative costs' in s:
            p.text=s.replace('The V9.9 alternative costs','The crop-enabled alternative costs')
        elif s.startswith('Fig. 1.'):
            p.text=('Fig. 1. AEO2026-based conditional expenditure comparison and partial lifecycle-emissions boundary. Agricultural process emissions substitute for a legacy crop-fuel term; this is neither an EIA total-system cost forecast nor a complete cradle-to-grave life-cycle assessment.')
        elif s.startswith('The new regional-import crosswalk fails closed'):
            p.text=(s.replace('fails closed when official county exports are incomplete, units are missing, duplicate county/feedstock/price records occur or resource categories cannot be mapped', 'rejects detectable defects such as missing units, duplicate county/feedstock/price records or unmapped resource categories, but cannot independently certify that a portal export covers all counties and offered prices'))
        elif 'Figs. S26 and S47' in s:
            p.text=s.replace('Figs. S26 and S47','Figs. S26 and S27')
        elif s.startswith('Supplementary materials:'):
            p.text=('Supplementary materials: Text S1–S31; Tables S1–S17; the consecutively captioned Figs. S1–S30, including mandatory Grid Harvester schematic S1 and cycle-energy chart S22. All main and supplementary figures are 600-dpi TIFFs. Regional biomass and HTL yield assumptions remain unvalidated.')
        elif s.startswith('Artificial intelligence:'):
            p.text=AI_DISCLOSURE
        elif s.startswith('Data and materials availability:'):
            p.text=('Data and materials availability: The version-matched V9.13 research package contains the full code, AEO2026 workbooks, numerical results, 1,000-draw uncertainty outputs, provenance records and validation tests. County-level BT23 resource data, feedstock-specific laboratory HTL yields and field SOC measurements are not included; the analysis remains conditional. A public repository release or DOI must not be represented as available until actually deposited.')
    target=next(p for p in d.paragraphs if p.text=='Conclusions')
    # Add durable two-factor result adjacent to the one-factor yield discussion.
    q=next(p for p in d.paragraphs if p.text.startswith('The common terrestrial HTL liquid yield'))
    add_after(q,('Jointly lowering the assumed common terrestrial HTL yield to 2.3 MWh/dry tonne and adding $40 per dry tonne to crop delivery costs reduces modelled annual crop-related savings to $0.062 billion with only 8 Mt selected, versus $6.78 billion and 166 Mt under the 2.6-MWh/t, zero-surcharge case. The two-factor screen (Fig. S30) and 1,000-draw uncertainty calculation indicate that crop selection is not robust across all economically and physically plausible-but-unverified combinations.'))
    replace_inline(d,0,'ScienceFig1_V913_Conditional_Cost_and_LCA.tif')
    replace_inline(d,4,'ScienceFig5_V913_Uncertainty_and_Reactor.tif')
    assert len(d.inline_shapes)==5
    d.save(R/MAIN)
    print('Main V9.13',len(d.paragraphs),'paragraphs',len(d.inline_shapes),'figures')

def supplement():
    d=source_doc('Supplementary_Materials_V9.12_Science.docx')
    for p in d.paragraphs:
        s=p.text
        if s.startswith('Fig. S13.'):
            p.text=s.replace('see corrected S40','see corrected Fig. S19')
        elif 'RUN_V911_VALIDATION.bat' in s or 'RUN_V911_VALIDATION.sh' in s:
            p.text=s.replace('RUN_V911_VALIDATION.bat','RUN_V913_VALIDATION.bat').replace('RUN_V911_VALIDATION.sh','RUN_V913_VALIDATION.sh').replace('V9.11 robustness workflow','V9.13 robustness workflow').replace('V9.11 stress screens','current V9.13 stress screens')
        elif s.startswith('S9. Paired uncertainty:'):
            p.text='S9. Paired uncertainty: current 1,000 draws, historical 500- and 150-draw diagnostics'
        elif s.startswith('The historical V9.8 500-draw Monte Carlo'):
            p.text=('The V9.8 500-draw and V9.9/V9.10 150-draw Monte Carlo outputs are historical diagnostics. The current V9.13 1,000-draw paired screen independently varies common HTL liquid yield, crop-only delivery costs, crop availability, selected process-emissions factors and the underlying vehicle/energy price parameters. Its ranges remain analyst assumptions, not calibrated future probabilities.')
        elif s.startswith('The archived V9.8 500-draw paired uncertainty screen'):
            p.text=('Historical V9.8 (500 draws) and V9.9 (150 draws) uncertainty files are retained only as annotated diagnostics. Current V9.13 results use 1,000 reproducible draws, explicit crop process-LCA substitution, assumed crop availability 0–166 Mt/year and plant-availability/soil-land constraints. Neither historical nor current distributions are calibrated national forecasts.')
        elif '150-draw' in s:
            p.text=s.replace('150-draw','1,000-draw')
        elif s.startswith('Supplementary figure atlas — Figs. S1–S29'):
            p.text='Supplementary figure atlas — Figs. S1–S30'
        elif s.startswith('Artificial intelligence:'):
            p.text=AI_DISCLOSURE
    # Append new methods to supplement without renumbering or removing Grid Harvester.
    d.add_heading('S31. Joint HTL-yield and delivery-cost test with 1,000-draw uncertainty',level=2)
    d.add_paragraph(('The two-factor screen reoptimises the same alternative with and without terrestrial crop residues at each combination of four assumed common terrestrial HTL liquid yields (2.0, 2.3, 2.6, 3.0 MWh/dry tonne) and four incremental crop-only delivered-cost charges (0, 20, 40, 80 US$/dry metric tonne). Unlike the inherited multiplicative crop-cost uncertainty, these additional delivery charges are not applied to wastewater treatment, hydrochar logistics or elemental N/P/K replacement. The agricultural cap is an unvalidated 166 Mt/year analytical ceiling. This study does not resolve feedstock-specific biocrude yields, operating-temperature dependence, or county transport costs.'))
    d.add_paragraph(('A reproducible 1,000-draw paired-screen (`us913_paired_uncertainty.py`, seed 913) also varies the modelled common HTL yield over 1.2–3.0 MWh/dry tonne, crop-only delivery charges, crop supply limits, plant-available nutrient recovery, reactor and electricity costs, and bounded field-emissions assumptions. The identical reference calculation is paired with each modelled alternative. These analyst-selected uniform ranges are not validated probability distributions; process heat, water and hydrogen inputs remain fixed per tonne when yield is varied. The HTL yield/carbon interaction thus requires experimental calibration before national resource or net-emissions claims.'))
    rows=list(csv.DictReader((R/'us913_combined_yield_delivery.csv').open()))
    pp=d.add_paragraph('Table S17. Matched crop-saving under simultaneous HTL-yield and crop delivery-price variation. All cells use the same unverified national resource screen.')
    pp.paragraph_format.keep_with_next=True
    t=d.add_table(rows=1,cols=4);t.style='Light Shading Accent 1'
    for k,v in enumerate(['Liquid yield (MWh/t)','Extra delivery (US$/t)','Residues selected (Mt)','Annual crop saving (US$ bn)']):t.rows[0].cells[k].text=v
    for q in rows:
        cells=t.add_row().cells
        for k,x in enumerate((f"{float(q['htl_liquid_yield_mwh_dry_t']):.1f}",
            f"{float(q['extra_crop_delivery_usd_dry_t']):.0f}",
            f"{float(q['crop_selected_mt']):.2f}",f"{float(q['crop_saving_bn']):.3f}")):
            cells[k].text=x
    for row in t.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                for rr in p.runs:rr.font.size=Pt(7.5)
    d.add_page_break()
    data,_=picture_blob(R/'ScienceFigS50_V913_Joint_HTL_Yield_Delivery.tif',dimensions=(1850,1350))
    p=d.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(io.BytesIO(data),width=Inches(5.9))
    cap=d.add_paragraph('Fig. S30. Paired optimization of 2050 crop-feedstock savings as common terrestrial HTL yield and crop-only delivery surcharge vary together; unvalidated national resource ceiling. No feedstock-specific laboratory performance or county delivery cost is implied.')
    cap.paragraph_format.keep_together=True
    assert len(d.inline_shapes)==30,len(d.inline_shapes)
    d.save(R/SUP)
    print('Supplement V9.13',len(d.inline_shapes),'figures',len(d.tables),'tables')

def letter():
    d=source_doc('Cover_Letter_Science_V9.12.docx')
    paras=[p for p in d.paragraphs if 'Artificial Inventor / Synthetic Scientist V63 assisted' in p.text]
    assert len(paras)==1
    paras[0].text=AI_DISCLOSURE
    anchor=next(p for p in d.paragraphs if p.text.startswith('An additional matched sensitivity now varies'))
    add_after(anchor,'The final paired uncertainty assessment uses 1,000 screening draws with sampled HTL yield and separate delivered-crop charges, and the supplementary analysis includes 16 matched yield–delivery combinations. The revised paper reports the unfavourable threshold results and does not claim field-calibrated national savings.')
    d.save(R/LETTER)

def title():
    source_doc('Title_Page_V9.12_Science.docx').save(R/TITLE)

if __name__=='__main__':main();supplement();letter();title()
