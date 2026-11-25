#!/usr/bin/env python3
"""Create V9.12 Science-targeted Word artifacts from version-controlled V9.11 masters.

No invented author consents, repository DOI or experimental validation. The full
supplementary figure atlas receives contiguous S1..S29 captions, preserving
Grid Harvester S1 and S22 permanently.
"""
from __future__ import annotations
import csv,io,re,zipfile
from pathlib import Path
from PIL import Image
from docx import Document
from docx.shared import Inches,Pt
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph
from docx.enum.text import WD_ALIGN_PARAGRAPH
R=Path(__file__).resolve().parent
SOURCE='V911_DOCUMENT_MASTERS.zip'
FILEBASE={'main':'Research_Article','supp':'Supplementary_Materials','title':'Title_Page','letter':'Cover_Letter'}
FILE={
 'main':('Research_Article_V9.11_Science.docx','Research_Article_V9.12_Science.docx'),
 'supp':('Supplementary_Materials_V9.11_Science.docx','Supplementary_Materials_V9.12_Science.docx'),
 'title':('Title_Page_V9.11_Science.docx','Title_Page_V9.12_Science.docx'),
 'letter':('Cover_Letter_Science_V9.11.docx','Cover_Letter_Science_V9.12.docx'),
}
FIG='ScienceFigS49_V912_Terrestrial_HTL_Yield_BreakEven.tif'
ABSTRACT=(
 'Agricultural residues may lower the cost of petroleum-free U.S. transportation, but collection, conversion, nutrient replacement and soil-carbon restoration constrain their value. '
 'We integrate AEO2026 transport activity with a national optimisation of electricity, hydrogen and liquid fuels, incorporating 13 candidate residue classes and a screened nutrient-availability chain. '
 'With an assumed 166-Mt annual ceiling and 2.6 MWh/dry-tonne terrestrial HTL yield, the alternative costs $654.8 billion/year, compared with $661.5 billion/year without crop residues. '
 'An added $40/dry-tonne delivery charge lowers the saving to $0.69 billion/year. '
 'At assumed common HTL yields of 2.0 MWh/dry-tonne or less, residues are not selected. '
 'Regional supplies, feedstock-specific yields and long-term agricultural emissions remain unvalidated; these estimates are conditional screening results, not a national deployment forecast.'
)

def src(name):
 with zipfile.ZipFile(R/SOURCE) as z:
  b=z.read(FILE[name][0])
 return Document(io.BytesIO(b))

def add_after(p,text):
 el=OxmlElement('w:p');p._p.addnext(el);new=Paragraph(el,p._parent);new.style='Normal';new.add_run(text);return new

def replace_figure_mentions(text,mapping):
 # Figure citations in prose, including comma-separated and en-dash ranges.
 pattern=re.compile(r'(?<!\w)(Figs?\.?\s*)((?:S\d+[\s,;–—-]*)+)',re.I)
 def f(m):
  part=re.sub(r'S(\d+)',lambda a:'S'+str(mapping.get(int(a.group(1)),int(a.group(1)))),m.group(2))
  return m.group(1)+part
 return pattern.sub(f,text)

def patch_main(mapping):
 d=src('main')
 assert d.paragraphs[5].text=='Abstract'
 d.paragraphs[6].text=ABSTRACT
 wc=len(ABSTRACT.split());assert wc<=125,(wc,ABSTRACT)
 for p in d.paragraphs:
  if p.text.startswith('Supplementary materials:'):
   p.text=('Supplementary materials: Text S1–S30, Tables S1–S16, a contiguous atlas of Figs. S1–S29, including mandatory Grid Harvester Fig. S1 and harvesting-cycle efficiency Fig. S22. All figures are supplied as 600-dpi TIFFs. HTL yield and delivered biomass sensitivities are analyst assumptions.')
  elif p.text.startswith('Data and materials availability:'):
   p.text=('Data and materials availability: The accompanying reproducibility archive contains model code, AEO2026 source workbooks, analysis scripts, checksums, and conditional scenario data. The official authenticated BT23 all-county resource export, validated HTL yield data by feedstock, and field soil-carbon observations are unavailable. No public version-matched repository or DOI is represented as deposited.')
  elif p.text.startswith('21. U.S. Nuclear Regulatory Commission, Long Mott Generating Station construction permit'):
   p.text=p.text.replace('construction permit (9 November 2026)','construction-permit application and review (2026)')
  elif p.text.startswith('Artificial intelligence:'):
   p.text=('Artificial intelligence: Artificial Inventor / Synthetic Scientist V63 and ChatGPT (OpenAI; model GPT-6) assisted with code, analysis, editing and vector-based scientific figures. Numerical and bibliographic verification is the responsibility of the human authors. Complete historical prompts are not represented as available. No AI system is listed as an author; all machine assistance and figure provenance require final author review and compliance with journal policy.')
 # Explicit limitations + yield finding before conclusions.
 target=next(p for p in d.paragraphs if p.text=='Conclusions')
 el=OxmlElement('w:p');target._p.addprevious(el)
 pp=Paragraph(el,target._parent);pp.add_run('The common terrestrial HTL liquid yield is a critical model parameter (26, 27). Under matched annual transport and soil constraints, lowering this assumed yield from 2.6 to 2.3 MWh/dry tonne reduces crop-related savings from $6.78 billion to $1.57 billion/year; at 2.0 MWh/dry tonne or below, none of the candidate residues is selected. The solver shares one terrestrial HTL yield between crops and noncrop biomass and does not resolve crop-specific chemistry. These sensitivities constrain the claims more strongly than the prior delivered-cost screen alone (Fig. S29).')
 # Add technical citation paragraph in framework rather than claim unconnected sources.
 p=next(p for p in d.paragraphs if p.text.startswith('A national annual linear-programming'))
 add_after(p,'Model assumptions draw on reactor and hydrogen process literature (7, 10–12, 21), offshore algal productivity and logistics studies (6, 13–17), energy-system and learning analyses (18, 19), and numerical optimisation methods (8, 9). EIA price and fleet conventions are provided in (1, 20, 25); agricultural sources and constraints in (2, 22, 23). These citations motivate screened technology ranges, not empirical proof of the integrated system.')
 ack=next(p for p in d.paragraphs if p.text=='Acknowledgments')
 for t in [
  '26. P. M. Guirguis, M. S. Seshasayee, B. Motavaf, and P. E. Savage, Review and assessment of models for predicting biocrude yields from hydrothermal liquefaction of biomass, RSC Sustainability 2, 736–756 (2024), doi:10.1039/D3SU00458A.',
  '27. I. Umeda et al., Element-Based Predictive Modeling of Hydrothermal Liquefaction Bioproducts Derived from Corn Stover, ACS Sustain. Chem. Eng. 14, 332–346 (2026), doi:10.1021/acssuschemeng.5c09967.'
 ]:
  el=OxmlElement('w:p');ack._p.addprevious(el);p=Paragraph(el,ack._parent);p.add_run(t)
 # Update mapped external refs (leave S1,S22 unchanged)
 for p in d.paragraphs:
  text=replace_figure_mentions(p.text,mapping)
  if text!=p.text:p.text=text
 d.save(R/FILE['main'][1])
 print('V9.12 main abstract words',wc,'images',len(d.inline_shapes),'refs 27')

def source_images(doc):
 pairs=[]
 for i,p in enumerate(doc.paragraphs):
  mt=re.match(r'^Fig\. S(\d+)\.',p.text)
  if not mt or i==0:continue
  prior=doc.paragraphs[i-1]
  if not prior._p.xpath('.//*[local-name()="blip"]'):continue
  pairs.append((int(mt.group(1)),prior,p))
 assert len(pairs)==28,len(pairs)
 assert len(set(tag for tag,*_ in pairs))==28
 return pairs

def add_picture_tiff(d,fn):
 with Image.open(R/fn) as im:
  rgb=im.convert('RGB');rgb.thumbnail((1850,1350));data=io.BytesIO();rgb.save(data,format='PNG',optimize=True)
 p=d.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
 p.add_run().add_picture(io.BytesIO(data.getvalue()),width=Inches(5.8))
 return p

def add_table(d,title,rows):
 p=d.add_paragraph(title);p.paragraph_format.keep_with_next=True
 for rr in p.runs:rr.bold=True
 cols=['HTL yield (MWh/dry t)','Crop intake (Mt/y)','Crop saving (US$ bn/y)']
 t=d.add_table(rows=1,cols=3);t.style='Light Shading Accent 1'
 for i,c in enumerate(cols):t.rows[0].cells[i].text=c
 for q in rows:
  cells=t.add_row().cells
  for i,val in enumerate((f"{float(q['htl_liquid_mwh_per_dry_metric_t']):.1f}",f"{float(q['crop_selected_mt']):.1f}",f"{float(q['crop_saving_bn']):.2f}")):
   cells[i].text=val
 for row in t.rows:
  for cell in row.cells:
   for p in cell.paragraphs:
    for rr in p.runs:rr.font.size=Pt(8)

def patch_supp(mapping,ordered):
 d=src('supp')
 d.paragraphs[0].text='Supplementary Materials — methods, resource and lifecycle boundaries, sensitivity analyses, and engineering figure atlas'
 for p in list(d.paragraphs):
  if re.match(r'^Fig\. S(3[4-7])\. ScienceFigS',p.text):
   p.text='Historical TIFF source filename for reproducibility (not an active figure caption): '+p.text[8:]
  if p.text.startswith('Supplementary figure atlas — selected technical figures'):
   p.text='Source-figure provenance and current method classifications'
 # Extract and temporarily detach all figure/image pairs, retaining their source image rels.
 figures={tag:(pic._p,cap._p,cap.text) for tag,pic,cap in source_images(d)}
 assert len(figures)==28
 for tag,(im,cap,_) in figures.items():
  im.getparent().remove(im)
  cap.getparent().remove(cap)
 # Change real cross-references (cannot change original archival TIFF filenames)
 for p in d.paragraphs:
  text=replace_figure_mentions(p.text,mapping)
  if text!=p.text:p.text=text
 # New methods section and table before figure atlas.
 d.add_page_break()
 d.add_heading('S30. HTL liquid-energy yield as an independently varied constraint',level=2)
 d.add_paragraph(('The inherited annual linear programme assigns one common liquid-energy output per dry metric tonne of terrestrial HTL feedstock. This model parameter applies to all terrestrial biomass in the current LP, not a calibrated corn-stover, wheat-straw, rice-husk or bagasse yield. Laboratory and kinetic literature demonstrates that biochemical composition, loading and reaction conditions can change biocrude product distribution (26, 27). We therefore reoptimise the crop-enabled and no-crop alternatives under identical nutrient, vehicle, delivery-cost, restoration-area and energy-supply assumptions, varying only the common terrestrial HTL liquid-energy yield. All reported values are finished-liquid-energy-equivalent model assumptions, not directly measured biocrude mass yields or verified upgrading efficiencies. The analysis does not infer fuel yields by feedstock class.'))
 rows=list(csv.DictReader((R/'us912_terrestrial_htl_yield_sensitivity.csv').open(encoding='utf-8')))
 add_table(d,'Table S16. Matched terrestrial HTL liquid-yield sensitivity; both alternatives are reoptimised using the same assumed yield.',rows)
 d.add_paragraph('Yields of 1.2, 1.6 and 2.0 MWh/dry tonne produce zero economic crop collection; at 2.3 MWh/dry tonne the optimiser selects 98.6 Mt and the incremental saving is $1.57 billion/year; at the inherited 2.6 MWh/dry tonne central assumption, 166 Mt is selected and the saving is $6.78 billion/year. The model also contains an uncalibrated raw-residue resource ceiling and its carbon/nutrient replacement assumptions remain uncertain. This sensitivity is not permission to treat any lower-yield residue as processed economically at the central 2.6 MWh/t assumption.')
 d.add_page_break()
 d.add_heading('Supplementary figure atlas — Figs. S1–S29',level=1)
 # Retain chronological sequence of the first 21 other figures, put mandatory Grid Harvester
 # efficiency panel at position S22, then remaining material, plus the new S29.
 body=d.element.body
 for i,old_tag in enumerate(ordered,1):
  im_el,cap_el,text=figures[old_tag]
  # Remap title once; source captions cannot disappear.
  newtxt=re.sub(r'^Fig\. S\d+\.',f'Fig. S{i}.',text)
  for r in cap_el.xpath('.//*[local-name()="t"]'):
   if r.text:
    r.text=newtxt
    # caption may have multiple runs, but all active captions use one text run
    break
  sect=next(el for el in body if el.tag.endswith("}sectPr"))
  body.insert(body.index(sect),im_el)
  body.insert(body.index(sect),cap_el)
 assert len(ordered)==28
 assert ordered[0]==1 and ordered[21]==22,(ordered[0],ordered[21])
 add_picture_tiff(d,FIG)
 cap=d.add_paragraph('Fig. S29. Identical-terrestrial-HTL-yield screening across paired crop and no-crop optimisations: annual savings and residue selection. Varying 1.2–3.0 MWh/dry tonne shows the result depends strongly on liquid-fuel yield; this is not crop-specific laboratory calibration.')
 cap.paragraph_format.keep_together=True
 assert len(d.inline_shapes)==29,len(d.inline_shapes)
 # Text substitutions after moving elements, but never renumber the new atlas again.
 assert 'Fig. S1.' in '\n'.join(p.text for p in d.paragraphs)
 d.save(R/FILE['supp'][1]);print('V9.12 supplement figures',len(d.inline_shapes),'tables',len(d.tables))

def patch_letter():
 d=src('letter')
 p=next((p for p in d.paragraphs if p.text.startswith('The complete research archive')),None)
 assert p
 add_after(p,'An additional matched sensitivity now varies terrestrial HTL liquid energy from 1.2 to 3.0 MWh per dry tonne and finds no economically selected crop residues at 2.0 MWh/t or below, versus $6.78 billion/year modelled savings at 2.6 MWh/t. The manuscript explicitly treats this as a critical conditional assumption, not an experimentally validated national conclusion.')
 d.save(R/FILE['letter'][1])

def patch_title():
 d=src('title');d.save(R/FILE['title'][1])

def run():
 doc=src('supp');pairs=source_images(doc);oldtags=[t for t,*_ in pairs];without=[x for x in oldtags if x!=22]
 # Place the user-required chart at S22.
 order=without[:21]+[22]+without[21:]
 assert len(order)==28 and order[0]==1 and order[21]==22
 mapping={old:i for i,old in enumerate(order,1)}
 patch_main(mapping);patch_supp(mapping,order);patch_letter();patch_title()
 (R/'US912_FIGURE_CROSSWALK.csv').write_text('legacy_figure_id,active_figure_id\n'+''.join(f'S{old},S{new}\n' for old,new in mapping.items())+'S49,S29\n')
 print('V9.12 figure crosswalk',mapping)
if __name__=='__main__':run()
