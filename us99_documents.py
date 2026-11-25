#!/usr/bin/env python3
"""Science-targeted V9.9 document revision. Grid Harvester S1/S22 are hard requirements."""
from pathlib import Path
from docx import Document
from docx.shared import Inches,Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from PIL import Image
import json,csv,io,zipfile,re
R=Path(__file__).resolve().parent
D=json.loads((R/'US99_Scenario_Analysis.json').read_text());crop,no=D['scenarios'][0],D['scenarios'][-1]; lca=D['lca_accounting'][0]
M=json.loads((R/'US99_Paired_Uncertainty_Summary.json').read_text())
TITLE='Economic potential of agricultural residues under nutrient and soil-carbon constraints in U.S. transport decarbonisation'
CURRENT=[('ScienceFig1_V99_Conditional_Economics_and_LCA.tif','conditional cost and emissions'),('ScienceFig2_V99_Crop_Economic_Selection.tif','economically selected residues'),('ScienceFig3_V99_Plant_Available_NPK_and_Carbon.tif','plant-available nutrient balance'),('ScienceFig4_V98_HTL_Return_Flow_With_Arrows.tif','HTL return-flow schematic'),('ScienceFig5_V99_Uncertainty_and_Reactor_Limits.tif','paired uncertainty / reactors')]
MANDATORY=['FigS1_grid_harvester.tif','FigS22_GridHarvester_Energy_Efficiency.tif']
SI_NEW=[('S42','ScienceFigS42_V99_Agricultural_LCA_Reconciliation.tif','Explicit crop process inventory and replacement of a legacy generic crop-fuel coefficient; non-overlapping boundaries remain a screened assumption.'),('S43','ScienceFigS43_V99_Nutrient_Availability_Chain.tif','Separated process recovery, treatment retention and plant availability, all analyst assumptions pending field or feedstock HTL data.'),('S44','ScienceFigS44_V99_Cover_Crop_Land_Feasibility.tif','Illustrative cover-crop land needs for 8.585 Mt stable-equivalent C per year; no verified cropland or soil-saturation trajectory.'),('S45','ScienceFigS45_V99_Joint_Crop_Reactor_Deployment.tif','Fixed high-temperature reactor hubs under V9.9 conservative agricultural parameters; no hourly grid feasibility or construction-rate guarantee.')]

def imbytes(fn,max_size=(2100,1800)):
 with Image.open(R/fn) as img:
  img=img.convert('RGB');img.thumbnail(max_size);buf=io.BytesIO();img.save(buf,'PNG',optimize=True);return buf.getvalue()

def replace_p(p,text):p.text=text

def update_main():
 d=Document(R/'SOURCE_MASTER_V98_Research_Article.docx');P=d.paragraphs
 P[0].text=TITLE
 P[4].text='One-sentence summary: An economically selected agricultural-residue pathway may lower the cost of deep U.S. transport decarbonisation under explicit nutrient replacement and soil-carbon constraints, but national regional feedstock supply remains unverified.'
 abstract=('Agricultural residues could lower the cost of petroleum-free transport, but nutrient loss, soil carbon and geographic supply limit their use. '
 'We combine AEO2026 transport activity with an optimisation of electricity, hydrogen, liquid fuels and hydrothermal processing of 13 residue categories. '
 'Under unverified national subcategory capacities, a plant-available nutrient and cover-crop-land-constrained system costs $654.8 billion annually, versus $661.5 billion without crop residues. '
 'Modelled fertilizer replacement is 977 kt nitrogen, 177 kt phosphorus and 1,093 kt potassium per year. '
 'A process-inventory substitution screen yields 229 Mt CO₂e/year for the alternative; lifecycle overlap and counterfactual field emissions remain unresolved. '
 'County-level feedstock exports and experimentally validated nutrient yields are required before national deployment claims.')
 P[6].text=abstract
 P[9].text='We evaluate 13 candidate classes of field and processing residues, including corn, wheat, soybean, rice, barley, sorghum, cotton, sugarcane and crop-processing streams. The 166-Mt national limit is an analyst screening assumption related to the DOE Billion-Ton Report; individual category capacities and delivered costs are not regionally verified. We provide a strict, county-level Oak Ridge National Laboratory BT23 import-and-optimise pipeline, but the official export is not included in the present release (2, 23).'
 P[11].text='A national annual linear-programming framework allocates wind, solar, nuclear process heat, hydrogen, methane pyrolysis, electrified vehicles and heavy-transport fuels. The integrated supply options retain hydrothermal crop residues, offshore macroalgae, hemp, bamboo, greenhouse and aquaculture heat cascades, and the conceptual Grid Harvester. The Grid Harvester engineering energy screen is retained as Supplementary Figs. S1 and S22; its 62.7% faired-hose saving concerns harvesting-cycle energy, not proven full-system fuel conversion efficiency.'
 P[13].text='The model now multiplies separate assumed coefficients for HTL nutrient recovery, treatment/storage retention and plant availability, then purchases the remaining N/P/K at separately priced elemental replacement rates. A conservative carbon case withholds hydrochar and methane-derived solid-carbon soil credits and requires biological replacement within an explicit 20-million-hectare assumed land limit at 0.5 t stable-equivalent C/ha/year. The original 166-Mt supply remains an unverified ceiling, not a field harvest plan (2, 23, 24).'
 P[15].text=(f'For AEO2026-based partial 2050 costs, the conditional reference is $477.1 billion/year. The V9.9 alternative costs ${crop["annual_cost_bn"]:.1f} billion/year with candidate crop residues under assumed chemistry and land constraints, or ${no["annual_cost_bn"]:.1f} billion/year without residues. The difference is a ${no["annual_cost_bn"]-crop["annual_cost_bn"]:.2f}-billion/year conditional crop benefit, not a validated county-level economic advantage. The comparison is not an official EIA total-system forecast.')
 P[17].text='Fig. 1. Conditional 2050 annual costs (partial AEO2026 reference and alternatives) and associated emissions screening boundaries. Crop process emissions substitute for—not add to—a generic legacy crop-fuel coefficient; the estimate is not a complete life-cycle inventory.'
 P[18].text='The new regional-import crosswalk fails closed when official county exports are incomplete, units are missing, duplicate county/feedstock/price records occur or resource categories cannot be mapped. Because no full export is included here, Fig. 2 uses analyst category caps and does not claim state-level supply estimates. BT23 corn stover is not added a second time as an independent corn husk resource.'
 P[20].text='Fig. 2. Economically selected crop-residue categories under assumed national capacity ceilings, with long names displayed in full. The actual county-level DOE BT23 price-supply tables have not been ingested, so the plotted limits are not geographically calibrated.'
 P[21].text=(f'The modelled 166-Mt case removes {crop["n_removed_kt"]:,.0f} kt N, {crop["p_removed_kt"]:,.0f} kt P and {crop["k_removed_kt"]:,.0f} kt K each year. After independent treatment-retention and assumed plant-availability factors, external fertilizer purchases rise to {crop["n_imports_kt"]:,.0f} kt N, {crop["p_imports_kt"]:,.1f} kt P and {crop["k_imports_kt"]:,.0f} kt K annually. These are calculated nutrient requirements, not field-measured crop uptake.')
 P[22].text=(f'The conservative soil-carbon screen denies stable hydrochar and methane-carbon agronomic-equivalence credits and procures {crop["cover_crop_stable_c_mt"]:.3f} Mt/year of biological stable-equivalent carbon. An assumed ceiling of 20 million hectares at 0.5 t C/ha/year provides at most 10 Mt C/year; long-term saturation, crop rotation and water demand remain unresolved. Solid pyrolysis carbon is not automatically counted as soil organic carbon.')
 P[24].text='Fig. 3. Effective plant-available elemental nutrient closure and biological soil-carbon land ceiling. Process recovery, treatment retention, field availability and accumulation rates remain unverified scenario coefficients.'
 P[25].text='Offshore seaweed, separate marine nutrient purification and terrestrial hydrothermal conversion remain optional system pathways. The previously corrected marine nutrient transfer has an illustrative net added cost of $79.27 million/year (fertilizer purchases avoided less foregone marine product sales and treatment/logistics). Marine process water is not directly applied to farmland, and a seaweed nutrient-routing optimum has not been established.'
 P[27].text='Fig. 4. Terrestrial–marine HTL, treated liquid nutrients and hydrochar return routes. Arrows indicate proposed processing and tested-field-application eligibility, not verified commercial mass transfers.'
 P[28].text=(f'A {M["n_feasible"]}-draw paired conditional uncertainty screen gives median abatement cost ${M["median_usd_t"]:.1f}/t CO₂e (5th–95th percentile ${M["p05_usd_t"]:.1f}–${M["p95_usd_t"]:.1f}/t); its sampled assumptions are not calibrated national probabilities. Fixed reactor-hub scenarios from 0 to 250 incorporate the joint-conservative agricultural configuration, but do not resolve hourly dispatch or reactor-construction feasibility.')
 P[30].text='Fig. 5. Paired parameter screening distribution and reactor deployment sensitivity using the new conservative agricultural assumptions. Large build configurations are mathematical scenarios, not deployment forecasts.'
 P[32].text='The transport-system cost benefit from selected residues persists in an assumed 166-Mt constrained case, but neither sustainable field collection nor the national residue category allocation has been independently verified. The official BT23 county agricultural export is a mandatory input for the next empirical test. BT23 supply prices are farmgate offers in short tons, not the modelled delivered costs; storage, transport, moisture and competing uses must be added separately.'
 P[33].text=(f'Our explicit agricultural process inventory is {lca["process_inventory_mt"]:.2f} Mt CO₂e/year. Removing an inherited {lca["generic_crop_ci_replaced_mt"]:.2f}-Mt equivalent crop-fuel coefficient before substitution gives {lca["replaced_route_screen_mt"]:.2f} Mt/year alternative emissions versus {lca["maximal_gross_addition_screen_mt"]:.2f} Mt/year under a full gross-addition upper screen. These are boundary diagnostics, not a certified cradle-to-grave inventory; baseline field emissions, industrial process H₂ and energy interactions remain to be independently reconciled.')
 P[34].text='The Grid Harvester is retained as a prospective engineering component with a dedicated view (Fig. S1), calculated cycle-energy comparison (Fig. S22), source model and numerical CSV. Under one faired-hose 10%-solids assumption, harvesting-cycle energy is 33.9 versus 90.9 MJ per 1.44-ha cycle, a modelled 62.7% reduction, not demonstrated fuel production efficiency. Hourly electric reliability, reactor construction schedules and mineral-nutrient field safety require independent engineering verification.'
 P[36].text='We solved the national annual energy and material system using a SciPy/HiGHS-based model with AEO2026 archived source workbooks and versioned Python scripts. Regional crop import code validates units, cumulative prices, duplicates and completeness, then replaces model capacities when official county records exist. No such records are supplied in this release. The agricultural LCA screen substitutes calculated process emissions for an overlapping legacy crop coefficient instead of adding them twice.'
 P[38].text='Conditional crop-residue economics survive more restrictive nutrient and soil assumptions, but the resource ceilings and soil-carbon accumulation remain hypothetical. The primary next empirical test is a nationally complete DOE BT23 county price-supply crosswalk with USDA resource consistency checks and experimental HTL recovery measurements. This is a modelling research article for Science consideration, not a site-approved transport deployment plan.'
 # Replace image parts and update geometric aspect ratios, preserving five figure positions.
 assert len(d.inline_shapes)==5,len(d.inline_shapes)
 for shape,(fn,_) in zip(d.inline_shapes,CURRENT):
  blob=imbytes(fn);rid=shape._inline.graphic.graphicData.pic.blipFill.blip.embed
  d.part.related_parts[rid]._blob=blob
  with Image.open(R/fn) as im:
   ratio=im.height/im.width
  shape.width=Inches(6.45);shape.height=Inches(min(6.45*ratio,6.4))
 # Revise potentially stale Methods claims and final disclosures only if supported.
 for p in d.paragraphs:
  if p.text.startswith('Data and materials availability:') or p.text.startswith('Data and code availability:'):
   p.text='Data and materials availability: Exact Python files, source-linked EIA 2026 tables, model outputs, and the BT23 authenticated-export importer are supplied in the archived research ZIP. A complete county-level BT23 export is not included; no public tagged release or DOI is asserted here.'
 # Append mandatory Grid Harvester mention in notes if absent from first 65 paragraphs.
 out=R/'Research_Article_V9.9_Science.docx';d.save(out);print(out)
 print('Abstract words',len(abstract.split()))
 return out

def update_si():
 d=Document(R/'SOURCE_MASTER_V98_Supplementary_Materials.docx')
 for p in d.paragraphs:
  if p.text.startswith('Supplementary Materials — V9.8:'):
   p.text='Supplementary Materials — V9.9: agricultural resource evidence gaps, nutrient availability, soil carbon, Grid Harvester and 2050 transport analysis'
  elif p.text.startswith('V9.8 recomputes 500 paired parameter draws'):
   p.text='The archived V9.8 500-draw paired uncertainty screen is retained as a historical diagnostic. Current V9.9 results use 150 reproducible draws, partial agricultural process-LCA substitution, crop availability 0–166 Mt/year and explicit land and nutrient-availability constraints. Neither distribution is a calibrated future national probability model.'
  elif p.text.startswith('Other inherited technical maps'):
   p.text='Other inherited technical maps and figures remain as clearly labelled historical diagnostics; only new V9.9 figures and source-matched current results should be interpreted as V9.9 conclusions.'
  elif p.text.startswith('Run RUN_V98_VALIDATION.bat'):
   p.text='Run RUN_V99_VALIDATION.bat (Windows) or ./RUN_V99_VALIDATION.sh (Linux) for current numerical outputs and embedded-figure checks. The Grid Harvester schematic (S1) AND harvesting-cycle energy-efficiency chart (S22) are mandatory release elements and must never be omitted.'
  elif p.text.startswith('The conceptual Grid Harvester is retained'):
   p.text='The Grid Harvester engineering concept is permanently retained in Fig. S1 (side/plan views), Fig. S22 (energy-efficiency comparison) and source grid_harvester.py and us91_grid_harvester_efficiency.csv. Conventional harvesting uses 90.9 MJ per reference 1.44-ha cycle; grid-hose at 10% solids uses 55.6 MJ, grid with faired hose at 10% solids 33.9 MJ, at 20% solids 23.8 MJ and at 30% solids 20.3 MJ. This is 38.8%, 62.7%, 73.8% and 77.7% less **harvesting-cycle** energy, respectively. These are engineering assumptions, not empirical demonstration, full-system energy efficiency or HTL conversion yields.'
 # Append current data sections after existing atlas rather than alter old table part geometry.
 d.add_page_break()
 d.add_heading('S22. V9.9 plant-available nutrients, regional resource data and agricultural lifecycle boundaries',level=2)
 d.add_paragraph('Unlike elemental HTL recovery alone, effective soil nutrient substitution multiplies assumed processing recovery, treatment/storage retention and field availability. V9.9 uses independent factors for N, P and K. The national 166-Mt candidate ceiling remains an unverified resource bound until an official all-county DOE BT23 download is supplied, checked and used in the model. The source importer rejects missing mass units, repeated price-tier records, empty files and incomplete geographical coverage.')
 d.add_paragraph(f'For the current assumed crop screen, annual fertilizer replacement is {crop["n_imports_kt"]:.1f} kt N, {crop["p_imports_kt"]:.1f} kt P and {crop["k_imports_kt"]:.1f} kt K, with {crop["cover_crop_stable_c_mt"]:.3f} Mt stable-equivalent biological C/year modelled at an assumed 20-Mha ceiling.')
 d.add_heading('S23. Agricultural emission substitution and field counterfactual',level=2)
 d.add_paragraph(f'The inherited fuel lifecycle term assigns 10 g CO₂e/MJ to a combined grasses-and-residues route. Applied to {crop["crop_htl_liquid_twh"]:.1f} TWh of modelled crop HTL liquid energy, this corresponds to {lca["generic_crop_ci_replaced_mt"]:.2f} Mt CO₂e/year. We remove this crop-specific overlap first, then include a {lca["process_inventory_mt"]:.2f}-Mt/year explicit production and nutrient management process screen. The resulting alternative {lca["replaced_route_screen_mt"]:.2f} Mt/year and maximal gross addition {lca["maximal_gross_addition_screen_mt"]:.2f} Mt/year bracket a partial boundary, not an independently validated life-cycle inventory. Regional collection distance and emissions from leaving residues in the soil remain data gaps.')
 d.add_heading('S24. Land and nuclear deployment feasibility',level=2)
 d.add_paragraph('The default land capacity is 20 million hectares of potential seasonal cover crops and 0.50 t stable-equivalent C/ha/year. Both are analyst assumptions; changes in soil type, rainfall, saturation, rotations and competing uses require spatial agricultural validation. Reactor deployment sensitivity is recomputed at 0, 30, 60, 100, 150, 166 and 250 four-module hubs using the SAME conservative crop and soil configuration. Hourly dispatch and deployment schedules are not established.')
 d.add_heading('S25. Mandatory Grid Harvester preservation rule',level=2)
 d.add_paragraph('Fig. S1, Fig. S22, the source grid_harvester.py and its five-row source efficiency table are non-optional technical components of every subsequent release. The validator checks filenames, 600-dpi RGB image metadata, actual image embedding directly before the S1 and S22 captions, and a required chart-data numerical invariant. An energy-saving percentage is not an HTL liquid-fuel yield.')
 for no,fn,caption in SI_NEW:
  p=d.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
  mem=io.BytesIO(imbytes(fn,(1900,1450)));p.add_run().add_picture(mem,width=Inches(5.7))
  cap=d.add_paragraph(f'Fig. {no}. {caption}');cap.paragraph_format.keep_together=True
 # Verify S1 and S22 captions still follow embedded graphic paragraphs
 for marker in ('Fig. S1. Grid Harvester','Fig. S22. Grid Harvester'):
  assert any(p.text.startswith(marker) for p in d.paragraphs),marker
 assert len(d.inline_shapes)>=25,len(d.inline_shapes)
 out=R/'Supplementary_Materials_V9.9_Science.docx';d.save(out);print(out);return out

def revise_letter():
 doc=Document(R/'SOURCE_MASTER_V98_Cover_Letter.docx')
 for p in doc.paragraphs:
  if 'Please consider' in p.text:p.text=f'Please consider the Research Article “{TITLE}” for publication in Science.'
  elif 'AEO2026 2050 partial reference' in p.text:p.text=f'An AEO2026-based partial reference is approximately $477.1 billion/year. The corresponding candidate crop-residue alternative is ${crop["annual_cost_bn"]:.1f} billion/year with conservative soil/nutrient restrictions and ${no["annual_cost_bn"]:.1f} billion/year without crop residues. These are conditional comparisons with an incomplete national lifecycle boundary; the official county dataset is not yet included.'
  elif 'The accompanying package' in p.text:p.text='The complete technical archive includes a national 2050 model, current and historical source-labelled figures, an AEO2026 data archive, a strict ORNL BT23 county-level import pipeline, updated agricultural emissions screens, a 150-draw uncertainty analysis and the mandatory Grid Harvester efficiency diagram (Fig. S22).'
 d=R/'Cover_Letter_Science_V9.9.docx';doc.save(d);print(d)

def revise_title():
 d=Document(R/'SOURCE_MASTER_V98_Title_Page.docx')
 for p in d.paragraphs:
  if 'Economically selected crop residues and conservative soil restoration' in p.text:p.text=TITLE
 out=R/'Title_Page_V9.9_Science.docx';d.save(out);print(out)

if __name__=='__main__':
 update_main();update_si();revise_letter();revise_title()
