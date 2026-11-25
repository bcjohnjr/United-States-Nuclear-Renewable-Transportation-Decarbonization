#!/usr/bin/env python3
"""Build V9.14 Science docs from immutable V9.13 masters at same directory level.
Preserves all 35 figure positions including the two mandatory Grid Harvester plates.
"""
from pathlib import Path
import csv,json,zipfile,io
from docx import Document
from docx.shared import Inches
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph
from us913_documents import replace_inline
R=Path(__file__).resolve().parent
MASTER='V913_DOCUMENT_MASTERS.zip'
DOCS={
 'Research_Article_V9.13_Science.docx':'Research_Article_V9.14_Science.docx',
 'Supplementary_Materials_V9.13_Science.docx':'Supplementary_Materials_V9.14_Science.docx',
 'Cover_Letter_Science_V9.13.docx':'Cover_Letter_Science_V9.14.docx',
 'Title_Page_V9.13_Science.docx':'Title_Page_V9.14_Science.docx',
}
ABSTRACT=('Agricultural residues may lower the cost of petroleum-free U.S. transportation, but collection, conversion, nutrient replacement and soil-carbon restoration constrain their value. '
 'We combine AEO2026 transport activity with a national electricity, hydrogen and liquid-fuel optimisation screening 13 residue classes. '
 'With an unverified 166-Mt/year ceiling and assumed terrestrial HTL yield of 2.6 MWh/dry tonne, the alternative costs $654.8 billion/year versus $661.5 billion/year without crop residues. '
 'Adding $40 per dry tonne above baseline screened crop-delivery charges reduces savings to $0.69 billion/year; yields of 2.0 MWh/t or less select none. '
 'In 59.8% of 1,000 uncalibrated uncertainty draws, no residues are selected. '
 'Actual county supplies, feedstock-specific yields and full lifecycle emissions remain unverified.')

def src(name):
 with zipfile.ZipFile(R/MASTER) as z:return Document(io.BytesIO(z.read(name)))
def after(p,t):
 el=OxmlElement('w:p');p._p.addnext(el);q=Paragraph(el,p._parent);q.style='Normal';q.add_run(t);return q

def main():
 d=src('Research_Article_V9.13_Science.docx')
 stats=json.loads((R/'US914_Paired_Uncertainty_Summary.json').read_text())
 assert stats['zero_crop_fraction']==.598
 x=next(i for i,p in enumerate(d.paragraphs) if p.text.strip()=='Abstract');assert 85<=len(ABSTRACT.split())<=125
 d.paragraphs[x+1].text=ABSTRACT
 for p in d.paragraphs:
  s=p.text
  if s.startswith('A 1,000-draw paired parameter screen'):
   p.text=(f"A 1,000-draw paired parameter screen samples terrestrial HTL yield, incremental crop-only delivery charges separately from wastewater and nutrient expenses, and bounded agricultural field-emissions assumptions. Conditional abatement cost has a median ${stats['median_usd_t']:.1f}/t CO₂e (5th–95th percentile ${stats['p05_usd_t']:.1f}–${stats['p95_usd_t']:.1f}/t). In {100*stats['zero_crop_fraction']:.1f}% of draws, the optimizer selects no crop residues. The 7–13 g/MJ hypothetical crop-route coefficient is first applied to the existing 10 g/MJ source inventory and then removed consistently, so merely sampling that bookkeeping parameter cannot create an emissions reduction. These assumed distributions are diagnostic, not empirical national probabilities; reactor screens still omit 8,760-hour feasibility.")
  elif s.startswith('Our explicit agricultural process inventory'):
   p.text=('The conditional agricultural process inventory is 19.97 Mt CO₂e/year. The underlying transport code applies 10 g CO₂e/MJ to the combined terrestrial residue-and-grass liquid route. Of 1,173.88 TWh in this route, 431.6 TWh is attributed to the modelled crop HTL stream, so only 15.5376 Mt (=431.6 × 0.0036 × 10) of the inherited generic term is replaced, not the coefficient for noncrop liquid fuel or emissions from electricity and process hydrogen. Substituting the crop-specific 19.97-Mt process screen gives 229.38 Mt/year, versus 244.92 Mt/year for the deliberately conservative gross-addition boundary. These are partial-boundary diagnostics, not a validated cradle-to-grave inventory.')
  elif s.startswith('In a paired 5 × 5 stress grid'):
   p.text=s.replace('a +$40/dry-metric-tonne delivered charge','a +$40/dry-metric-tonne incremental crop-only charge above screened baseline delivered-tier costs').replace('At +$120/t','At an added +$120/t')
  elif s.startswith('Jointly lowering the assumed common terrestrial HTL yield'):
   p.text=s.replace('adding $40 per dry tonne to crop delivery costs','adding an incremental $40 per dry tonne above screened crop-tier delivered costs')
  elif s.startswith('Fig. 1.'):
   p.text='Fig. 1. Conditional AEO2026-based annual expenditure and partial lifecycle-emissions comparison. Only the 10-g/MJ generic coefficient for crop liquid within the mixed terrestrial residue/grass route is substituted; noncrop liquid, process hydrogen and electricity remain accounted for. The comparison is neither an EIA total-system cost forecast nor a complete national life-cycle assessment.'
  elif s.startswith('Fig. 5.'):
   p.text='Fig. 5. Paired 1,000-draw conditional uncertainty screen with screened HTL yield, incremental crop-only delivery costs and agricultural process/field terms, compared with a fixed-reactor deployment sensitivity. The ranges are analyst assumptions, not empirically calibrated probabilities.'
  elif s.startswith('Competing interests:'):
   p.text='Competing interests: The corresponding author is associated with Cloud Wash Laundry Corporation. Financial interests, company involvement, related patents or applications, and all coauthor disclosures must be confirmed and completed by the authors before submission; no absence of conflicts or patents is certified by this package.'
  elif s.startswith('Data and materials availability:'):
   p.text=s.replace('V9.13','V9.14')+' The reproduction scripts operate from a single extracted flat directory, with repository tag and DOI awaiting verification.'
  elif s.startswith('Supplementary materials:'):
   p.text=s.replace('Text S1–S31','Text S1–S32')
 replace_inline(d,0,'ScienceFig1_V914_Conditional_Cost_and_LCA.tif')
 replace_inline(d,4,'ScienceFig5_V914_Uncertainty_and_Reactor.tif')
 assert len(d.inline_shapes)==5
 d.save(R/DOCS['Research_Article_V9.13_Science.docx'])

def supplement():
 d=src('Supplementary_Materials_V9.13_Science.docx')
 for p in d.paragraphs:
  s=p.text
  if s.startswith('A reproducible 1,000-draw paired-screen'):
   p.text=s.replace('(`us913_paired_uncertainty.py`, seed 913)', '(`us914_paired_uncertainty.py`, seed 913)').replace('identical reference calculation','identical reference calculation')+' The source-route CI is adjusted before any hypothetical coefficient is removed; the bookkept partial emissions total is invariant to a purely notional route-CI redraw.'
  elif s.startswith('The two-factor screen reoptimises'):
   p.text=s.replace('incremental crop-only delivered-cost charges','incremental crop-only delivered-cost charges above the assumed baseline tier prices')
  elif 'RUN_V913_VALIDATION' in s:
   p.text=s.replace('RUN_V913_VALIDATION','RUN_V914_REPRODUCE')
  elif s.startswith('Fig. S30.'):
   p.text=s.replace('crop-only delivery surcharge','crop-only delivery surcharge above screened baseline tiers')
 replace_inline(d,29,'ScienceFigS50_V914_Joint_HTL_Yield_Delivery.tif')
 d.add_heading('S32. Audited crop-route coefficient substitution and unit check',level=2)
 d.add_paragraph(('The transport solver uses a single generic 10 g CO₂e/MJ factor for the combined terrestrial residues-and-grasses liquid route; its central crop-enabled output is 1,173.878 TWh of mixed-route liquid energy, including 431.600 TWh of agricultural-residue HTL liquid. Substituting process emissions may remove only the crop share: 431.600 TWh × 3.6 PJ/TWh × 10 g/MJ ÷ 1,000 = 15.5376 Mt CO₂e/year. The generic coefficient continues to apply to 742.278 TWh of noncrop mixed-route liquid output. Existing hydrogen process and electricity lifecycle totals remain in the underlying emissions ledger.'))
 d.add_paragraph(('In the uncertainty code, a hypothetical 7–13 g/MJ alternative coefficient is first reflected in the legacy inventory by adding crop_liquid_TWh × 0.0036 × (hypothetical coefficient − 10) Mt; only then is crop_liquid_TWh × 0.0036 × hypothetical coefficient subtracted. These exactly cancel, leaving the same 10-g/MJ crop-only removal for every draw. Sampling a subtraction without adjusting the baseline would spuriously change emissions, and is prohibited by the new lifecycle unit tests. Agricultural process intensities, field counterfactuals, feedstock-specific yields, and spatial fuel transport remain independent unresolved scientific uncertainties.'))
 d.add_paragraph(('The extra +$20/+40/+80 per dry metric tonne in the two-factor screen is an addition to the already assumed model crop-tier delivered price and is NOT the complete farmgate, transport, storage, and nutrient replacement cost. Farmgate offers in official BT23 releases are a different boundary. This experiment does not validate regional supply or produce an empirical per-county delivered-cost schedule.'))
 assert len(d.inline_shapes)==30 and len(d.tables)==17
 d.save(R/DOCS['Supplementary_Materials_V9.13_Science.docx'])

def cover():
 d=src('Cover_Letter_Science_V9.13.docx')
 for p in d.paragraphs:
  s=p.text
  if '1,000 screening draws' in s:
   p.text=s.replace('separate delivered-crop charges','incremental crop-only charges above baseline screened delivered-tier costs')
  if '15.54' in s or 'lifecycle' in s.lower():
   if 'lifecycle' in s.lower() and 'V9.13' in s:p.text=s.replace('V9.13','V9.14')
 sig=next(p for p in d.paragraphs if p.text.startswith('Sincerely,'))
 el=OxmlElement('w:p');sig._p.addprevious(el);inserted=Paragraph(el,sig._parent);inserted.add_run('An additional lifecycle bookkeeping audit ties the 10-g/MJ generic mixed-route coefficient to the crop liquid-energy ledger and demonstrates that hypothetical coefficient sensitivity is baseline-adjusted before substitution; it does not invent marginal emissions savings. The 1,000-draw stress test selects no residues in 59.8% of draws. Coauthor signoff, competing-interest/patent declarations and permission for any AI-generated figure remain pending author/editor verification.')
 d.save(R/DOCS['Cover_Letter_Science_V9.13.docx'])

def title():
 d=src('Title_Page_V9.13_Science.docx')
 for p in d.paragraphs:
  if 'V9.13' in p.text:p.text=p.text.replace('V9.13','V9.14')
 d.save(R/DOCS['Title_Page_V9.13_Science.docx'])

def editorial():
 entries=list(csv.DictReader((R/'US913_EDITORIAL_FIGURE_PROVENANCE.csv').open()))
 changes={'Figure_1.tif':'ScienceFig1_V914_Conditional_Cost_and_LCA.tif',
          'Figure_5.tif':'ScienceFig5_V914_Uncertainty_and_Reactor.tif',
          'Figure_S30.tif':'ScienceFigS50_V914_Joint_HTL_Yield_Delivery.tif'}
 for e in entries:
  if e['editorial_name'] in changes:e['original_600dpi_tiff']=changes[e['editorial_name']]
 with (R/'US914_EDITORIAL_FIGURE_PROVENANCE.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(entries[0]));w.writeheader();w.writerows(entries)
 assert len(entries)==35
 with zipfile.ZipFile(R/'SCIENCE_EDITORIAL_UPLOAD_ONLY_V9.14.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for name in DOCS.values():z.write(R/name,name)
  for e in entries:z.write(R/e['original_600dpi_tiff'],e['editorial_name'])
 with zipfile.ZipFile(R/'SCIENCE_EDITORIAL_UPLOAD_ONLY_V9.14.zip') as z:assert len(z.namelist())==39

if __name__=='__main__':
 main();supplement();cover();title();editorial()
 from us9141_finalize import apply as apply_referee_patch
 apply_referee_patch()
 print('Built V9.14.1 editorial revision: 4 documents, 35 figures, 1 editor-only sub-archive')
