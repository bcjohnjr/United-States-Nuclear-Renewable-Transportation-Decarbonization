#!/usr/bin/env python3
"""V9.11 editorial build from exactly source-controlled V9.10 Word masters.

Only V9.11 documents belong in the editorial upload. Source masters stay in
research reproducibility material. Do not silently regenerate any missing data.
"""
from pathlib import Path
from docx import Document
from docx.shared import Inches,Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph
from PIL import Image
import csv,io,json,math
R=Path(__file__).resolve().parent
ROOTS={'main':'Research_Article','supp':'Supplementary_Materials','letter':'Cover_Letter','title':'Title_Page'}
SOURCE={
 'main':'SOURCE_V910_Research_Article_V9.10_Science.docx',
 'supp':'SOURCE_V910_Supplementary_Materials_V9.10_Science.docx',
 'letter':'SOURCE_V910_Cover_Letter_Science_V9.10.docx',
 'title':'SOURCE_V910_Title_Page_V9.10_Science.docx'
}
TARGET={
 'main':'Research_Article_V9.11_Science.docx',
 'supp':'Supplementary_Materials_V9.11_Science.docx',
 'letter':'Cover_Letter_Science_V9.11.docx',
 'title':'Title_Page_V9.11_Science.docx'
}
FIGS=[
 ('S46','ScienceFigS46_V911_Delivered_Cost_Resource_Robustness.tif','Annual cost reduction from crop residues relative to matched no-crop system over 25 independently reoptimised availability and delivered-cost screens. Crop availability and delivered costs are assumed, not measured BT23 county supply curves.'),
 ('S47','ScienceFigS47_V911_Cover_Crop_Land_Economic_Robustness.tif','Cover-crop land constraint, economically selected residues, and avoided expenditure. A 0.5 t C/ha/year accumulation rate is imposed, not observed, and soil carbon is subject to saturation and agronomic limits.'),
 ('S48','ScienceFigS48_V911_Field_Counterfactual_LCA_Bounds.tif','Partial lifecycle emissions difference of crop-enabled and matched no-crop alternatives under assumed field-residue counterfactual values of −0.05 to +0.05 t CO₂e/dry tonne. Not a measured national field-carbon effect.')
]

def after(p,text):
 el=OxmlElement('w:p');p._p.addnext(el);out=Paragraph(el,p._parent);out.style=p.style;out.add_run(text);return out

def source_doc(name):
 p=R/SOURCE[name]
 if not p.exists():raise FileNotFoundError(f'Missing source Word master: {p.name}')
 return Document(p)

def add_table(d,headers,rows,title):
 p=d.add_paragraph(title);p.style='Normal';p.paragraph_format.keep_with_next=True
 for run in p.runs:run.bold=True
 t=d.add_table(rows=1,cols=len(headers));t.style='Light Shading Accent 1'
 for j,h in enumerate(headers):t.rows[0].cells[j].text=str(h)
 for row in rows:
  c=t.add_row().cells
  for j,x in enumerate(row):c[j].text=str(x)
 for row in t.rows:
  for cell in row.cells:
   for pp in cell.paragraphs:
    for rr in pp.runs:rr.font.size=Pt(7.5)
 return t

def figure(d,tag,filename,caption):
 with Image.open(R/filename) as image:
  img=image.convert('RGB');img.thumbnail((1850,1350));bytes_=io.BytesIO();img.save(bytes_,'PNG',optimize=True)
 bytes_.seek(0);p=d.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
 p.add_run().add_picture(bytes_,width=Inches(5.8))
 cap=d.add_paragraph(f'Fig. {tag}. {caption}');cap.paragraph_format.keep_together=True

def build_main(data):
 d=source_doc('main')
 a=d.paragraphs
 assert a[5].text=='Abstract'
 original=a[6].text
 marker=' Under unverified national subcategory capacities,'
 assert marker in original
 a[6].text=original.replace(' Modelled fertilizer replacement is',
  ' A $40/t delivery surcharge cuts this benefit to $0.69 billion. Modelled fertilizer replacement is')
 n=len(a[6].text.split())
 assert 105<=n<=125,f'Unexpected abstract {n}'
 for p in list(d.paragraphs):
  if p.text.startswith('The transport-system cost benefit from selected residues persists'):
   after(p,'In a paired 5 × 5 stress grid, the conditional crop value falls from $6.78 billion to $0.69 billion/year with a +$40/dry-metric-tonne delivered charge under the full assumed 166-Mt ceiling. At +$120/t, none of the modelled crop candidates is selected. At only 41.5 Mt availability and no delivery surcharge the benefit is $2.34 billion/year (Figs. S46 and S47). These tests show that the national benefit is not established by physical residue availability alone; county-level actual supply costs remain the key empirical prerequisite.')
  elif p.text.startswith('Our explicit agricultural process inventory is'):
   after(p,'Paired partial lifecycle accounting against the no-crop alternative gives −38.36 Mt CO₂e/year under the zero-field-counterfactual process-substitution screen; an assumed net field counterfactual of ±0.05 t CO₂e per dry tonne changes this comparison by ±8.30 Mt. The values are methodological bounds, not calibrated soil-carbon or N₂O effects (Fig. S48).')
  elif p.text.startswith('Supplementary materials:'):
   p.text='Supplementary materials: Text S1–S29, Tables S1–S15, supplementary TIFF figures including Figs. S1 and S22 (mandatory Grid Harvester views and harvesting-cycle energy efficiency), and resource-delivery, cover-crop and field-counterfactual sensitivities S46–S48.'
  elif p.text.startswith('Data and materials availability:'):
   p.text=('Data and materials availability: Source code, EIA AEO2026 workbooks, modelled scenario CSVs and figures are provided in this reproducibility archive. The national residue ceiling and category costs are analyst assumptions; a complete authenticated ORNL BT23 county price-supply export and independent USDA concordance remain unavailable. No version-matched public GitHub release, accession or archival DOI is asserted.')
 # Number-verified figures and abstract.
 assert len(d.inline_shapes)==5
 d.save(R/TARGET['main']);print('V9.11 article abstract words',n)

def build_supp(data):
 d=source_doc('supp')
 d.paragraphs[0].text='Supplementary Materials — V9.11: delivered biomass sensitivity, crop-land feasibility, field counterfactuals, nutrient restoration and Grid Harvester'
 for p in d.paragraphs:
  if p.text.startswith('Use RUN_V910_VALIDATION.bat'):
   p.text='Use RUN_V911_VALIDATION.bat on Windows or RUN_V911_VALIDATION.sh on Linux. The complete V9.11 robustness workflow and the mandatory Fig. S1 and Fig. S22 source/embedded-image regression tests form part of this release. Older numeric files are labelled archived diagnostics and are not a substitute for V9.11 stress screens.'
 d.add_page_break()
 d.add_heading('S27. Joint delivered-biomass cost and resource-capacity sensitivity',level=2)
 d.add_paragraph('A paired national optimisation holds the 2050 AEO2026 activity, vehicle-price screen, N/P/K plant availability, cover-crop land ceiling, reactor learning and all non-crop pathways unchanged. It varies the maximum allowed crop input between 0 and 166 million dry metric tonnes/year and adds 0–120 US$/dry metric tonne only to the 13 crop residue delivered cost tiers. This deliberately measures the model’s dependence on analyst category assumptions; none of these cells represents an observed DOE county-level resource price. The no-crop alternative is recalculated under identical environmental parameters, with no hidden free soil-carbon credit.')
 by={(float(x['analyst_cap_mt']),float(x['delivery_surcharge_usd_dry_metric_t'])):float(x['crop_saving_bn']) for x in data['grid']}
 limits=[0,41.5,83,124.5,166];costs=[0,20,40,80,120]
 rows=[[f'{q:g}']+[f'{by[(q,c)]:.2f}' for c in costs] for q in limits]
 add_table(d,['Analyst cap (Mt/y)']+[f'+${x}/t' for x in costs],rows,'Table S13. Modelled annual saving (US$ billion/year) versus matched no-crop alternative; assumed resource and cost bounds only.')
 d.add_paragraph('Under the full 166-Mt capacity bound, adding $40/t reduces annual crop value from $6.78 billion to $0.69 billion. At $80/t the programme selects only a tiny low-cost subset and is nearly indifferent to no collection; at $120/t it selects zero crop feedstock. These findings warn against asserting a national monetary benefit from an aggregate DOE national ceiling before regional delivered prices have been verified.')
 figure(d,*FIGS[0])
 d.add_heading('S28. Cover-crop restoration land, saturation and opportunity constraints',level=2)
 d.add_paragraph('The explicit joint-conservative biological soil-carbon model is limited by an assumed seasonal-cover land area and a hypothetical net additional 0.5 t stable-equivalent C/ha/year. Neither the cropland constraint nor annual accumulation is measured here. Cover area below 17.17 million hectares limits collection within the model; water demand, cover crop establishment, soils, rotation timing and long-run saturation remain untested.')
 rows=[[f"{float(x['assumed_cover_crop_land_mha']):g}",f"{float(x['maximum_additional_C_mt']):.2f}",
   f"{float(x['selected_crop_mt']):.1f}" if x['selected_crop_mt']!='' else 'Infeasible',
   f"{float(x['crop_saving_bn']):.2f}" if x['crop_saving_bn']!='' else '—'] for x in data['land']]
 add_table(d,['Cover area (Mha)','Maximum stable C (Mt/y)','Selected residues (Mt/y)','Annual saving (US$ bn)'],rows,
           'Table S14. Cover-land reoptimisation at assumed additional annual sequestration of 0.5 t C/ha.')
 figure(d,*FIGS[1])
 d.add_heading('S29. Agricultural counterfactual emissions: gross is not incremental',level=2)
 d.add_paragraph('The present partial process-LCA screen replaces the inherited generic crop-derived fuel coefficient with named agricultural process emissions. This substitution is intended to avoid adding identical processes twice, but no experimental process mapping or full cradle-to-grave system ledger is available. Crop collection additionally changes how residue would otherwise decay, enter the soil, influence soil N₂O and affect soil carbon. To expose this unresolved counterfactual, the model assigns a hypothetical net field offset between −0.05 and +0.05 t CO₂e per dry tonne of collected biomass. The sign expresses the counterfactual and is not a measured soil emissions factor.')
 rows=[[f"{float(x['field_residue_counterfactual_tco2e_per_dryt']):+.3f}",
        f"{float(x['assumed_field_counterfactual_mt']):+.2f}",
        f"{float(x['incremental_crop_emissions_mt']):+.2f}"] for x in data['field_lca']]
 add_table(d,['Assumed net field factor (t/t)','Annual field offset (Mt CO₂e)','Crop – no-crop partial emissions (Mt CO₂e)'],rows,
           'Table S15. Conditional incremental agricultural emissions, not observed LCA results.')
 figure(d,*FIGS[2])
 d.add_paragraph('The base-case −38.36 Mt CO₂e/year crop/no-crop difference is not a measured abatement benefit. Even under the small ±0.05 t/t assumed range the outcome spans −30.06 to −46.66 Mt/year. Feedstock-specific energy inputs, process heat source, biogenic carbon, fertilizer manufacturing, agricultural N₂O and field soil change must all be reconciled before the results can be interpreted as net lifecycle mitigation.')
 assert len(d.inline_shapes)>=28,len(d.inline_shapes)
 d.save(R/TARGET['supp']);print('V9.11 supplement images',len(d.inline_shapes),'tables',len(d.tables))

def build_letter():
 d=source_doc('letter')
 for p in d.paragraphs:
  if p.text.startswith('The research archive provides'):
   p.text=('The complete research archive includes AEO2026 provenance, the current joint-conservative crop and soil model, source-labelled 600-dpi figures, a fail-closed ORNL data importer, and new paired analyses testing the crop value against delivery-cost, resource-ceiling and cover-crop-land constraints. Grid Harvester Figs. S1/S22 and its source calculations are mandatory. Regional DOE county price/supply data remain unavailable, and we do not claim validated national implementation.')
 # author approval not presumed; don't contact editor on author's behalf
 for p in d.paragraphs:
  if p.text.startswith('The agricultural') and '$' in p.text:
   p.text+=(' A further $40/dry tonne delivered cost surcharge reduces the modelled crop saving to about $0.69 billion/year; this indicates strong sensitivity to unverified local supply costs.')
 d.save(R/TARGET['letter'])

def build_title():
 d=source_doc('title');d.save(R/TARGET['title'])

def run():
 data=json.loads((R/'US911_Robustness_Results.json').read_text())
 build_main(data);build_supp(data);build_letter();build_title()
if __name__=='__main__':run()
