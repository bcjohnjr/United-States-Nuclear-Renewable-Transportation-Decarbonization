#!/usr/bin/env python3
"""V9.8 *Science* revision, no fictitious field validation, 5 main 600dpi RGB TIFFs.
Separate technical SI expands experimental assumptions and inserts numbered figures.
"""
from pathlib import Path
from docx import Document
from docx.shared import Inches,Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from PIL import Image
import json,io,zipfile,re
P=Path(__file__).resolve().parent
I=json.loads((P/'US97_Integrated_Circular_EIA.json').read_text())
B=json.loads((P/'US97_AEO_Boundary.json').read_text())
S=json.loads((P/'US98_Strict_Crop_and_Reactor_Sensitivity.json').read_text())
L=json.loads((P/'US98_Agriculture_Explicit_LCA.json').read_text())
U=json.loads((P/'US98_Paired_Uncertainty_Summary.json').read_text())
base=I['scenario']['soil_costed_economic_crop']; ref=I['source_weighted_reference_partial_bn']; refe=I['source_weighted_reference_emissions_partial_mt']; stric=S['cases'][1]
main_figs=['ScienceFig1_V98_Cost_LCA_Boundaries.tif','ScienceFig2_V98_Crop_Dispatch_and_Unverified_Caps.tif','ScienceFig3_V98_NPK_C_and_Conservative_Restoration.tif','ScienceFig4_V98_HTL_Return_Flow_With_Arrows.tif','ScienceFig5_V98_Uncertainty_and_Reactor_Screen.tif']
new_si=[('S38','ScienceFigS38_V98_Explicit_Agri_Emissions.tif','Explicit agricultural production and nutrient-recovery emissions, reported as gross candidate additions with coefficient overlap unknown.'),('S39','ScienceFigS39_V98_Regional_Data_Gap_Stress.tif','Economics under progressively reduced, unverified biomass supplies and excluded processing streams; not geographically calibrated.'),('S40','ScienceFigS40_V98_Marine_Market_Opportunity_Cost.tif','Marine-to-land nutrient reallocation using distinct offshore product sales and agricultural replacement values.'),('S41','ScienceFigS41_V98_Reference_Hydrogen_HHV_LHV.tif','Reference hydrogen conversion using provisional U.S. gross HHV convention versus LHV sensitivity.')]
SOURCE_NOTE='DOE BT23 county resource tool https://bioenergykdf.ornl.gov/bt23-agricultural-download; HTL nutrient partition review https://pubs.rsc.org/en/content/articlehtml/2026/ew/d5ew00569h; EIA gross fuel thermal factors https://www.eia.gov/totalenergy/conversion/factors/'

def replace_images(doc,filenames):
 assert len(doc.inline_shapes)==len(filenames),(len(doc.inline_shapes),len(filenames))
 for shape,name in zip(doc.inline_shapes,filenames):
  rid=shape._inline.graphic.graphicData.pic.blipFill.blip.embed
  part=doc.part.related_parts[rid]
  with Image.open(P/name) as im:
   im=im.convert('RGB');im.thumbnail((2800,1800));out=io.BytesIO();im.save(out,format='PNG',optimize=True)
  part._blob=out.getvalue()

def ptxt(doc,i,text):
 doc.paragraphs[i].text=text

def main_doc():
 doc=Document(P/'SOURCE_BASE_V97_Research_Article.docx')
 paras=doc.paragraphs
 title='Economically selected crop residues and conservative soil restoration in U.S. transport decarbonisation'
 ptxt(doc,0,title)
 ptxt(doc,4,'One-sentence summary: Economically selected residues may reduce costs of prospective U.S. petroleum-free transportation, but field-level supply, nutrient-recovery and soil-carbon validity remain unresolved.')
 abst=(
 'The costs of petroleum-free U.S. transportation depend on a 2050 baseline that already includes electric vehicles and on the sustainability of biomass supply. '
 'Using AEO2026 fleet and service data, we optimise electricity, hydrogen, liquid-fuel routes and agricultural residues while tracking nitrogen, phosphorus, potassium and soil-carbon restoration. '
 'The partial reference costs $477 billion annually; an illustrative crop-integrated system costs $651 billion. '
 'Removing optimistic char and methane-carbon soil credits and halving nutrient recovery raises alternative cost to $654 billion. '
 'Agricultural emissions screening identifies 13.7 Mt CO₂e/year of candidate additional processes, but overlapping existing lifecycle factors must be reconciled. '
 'Source-category yields remain uncalibrated against county data. '
 'We find potential savings from selected residues, not verified farm-level sustainability or a completed nationwide lifecycle forecast.' )
 ptxt(doc,6,abst)
 ptxt(doc,9,'We evaluate 13 classes of candidate crop residues, including corn stover, wheat straw, rice material, cotton, sorghum, pruning and processing wastes. The 166-Mt ceiling is a national economic screen derived from DOE BT23, not a geographic supply assignment. Primary field residues must be distinguished from processing wastes and disaggregated field components to prevent double counting. Regional BT23 records and farm-specific soil-conservation restrictions have not yet been assimilated (2,23).')
 ptxt(doc,13,'The linear programme imposes priced crop collection, treatment, elemental N/P/K nutrient closure, and hypothetical stable-equivalent soil-carbon obligations. HTL solids and treated water have separate return pathways; neither is assumed safe for direct land application. Conservative cases halve capture efficiency, deny hydrochar stability and methane-derived carbon soil-equivalence credits, and purchase biological cover-crop soil-carbon services. The combined test changes central annual system costs but does not validate assumed field-specific residue yields (2,24).')
 ptxt(doc,15,f'A 2050 AEO2026 source-stock-weighted partial reference costs ${ref:.1f} billion annually. The V9.7 crop-enabled alternative costs ${base["annual_cost_bn"]:.1f} billion; a joint conservative NPK/carbon case costs ${stric["annual_cost_bn"]:.1f} billion, while a primary-field-type, half-availability stress costs ${S["cases"][2]["annual_cost_bn"]:.1f} billion. These are matched *scenario* costs, not an official EIA national total-system forecast. The conventional historical-price petroleum comparator is not the current decision baseline (1–4).')
 ptxt(doc,17,'Fig. 1. Annual expenditure under a partially matched 2050 AEO2026 counterfactual and the proposed system, plus a separate gross agricultural emissions sensitivity. The candidate emissions could overlap existing fuel lifecycle coefficients; they are not an unconditional addition to reported WTW totals.')
 ptxt(doc,18,'The V9.7 crop optimiser selects 166 Mt/year across six positive residue classes using unvalidated national subcategory caps. A matched no-crop case costs $661.5 billion annually. The combined no-char-credit, half-nutrient-recovery test retains the economic benefit at $654.4 billion, but a quarter-availability stress raises it to $659.9 billion. These are deliberately conservative numerical screens; regional sustainable supply and the independence of corn field components and milling residues remain unverified.')
 ptxt(doc,20,'Fig. 2. Economically selected dry biomass among 13 candidate feedstock classes, alongside analyst-assumed maximum capacities. These bars are not USDA county resources or soil-specific removal permissions.')
 ptxt(doc,21,'The original 166-Mt screen removes 1,136, 214 and 1,575 kt/year of elemental N, P and K. Under assumed capture efficiencies, external replacement amounts to 568 kt N, 53.6 kt P and 315 kt K. These are conservation identities, not measured plant-available nutrient recovery. The joint conservative scenario halves recovered fractions, assigning additional fertilizer replacement and cover-crop restoration rather than relying on unverified carbon permanence.')
 ptxt(doc,22,'The original stable-equivalent carbon requirement is 8.58 Mt/year, met arithmetically by putative hydrochar and methane-derived carbon credits. Methane pyrolysis carbon is chemically distinct from agronomic biochar and may not reproduce soil organic matter functions. The revised primary sensitivity denies both carbon credits and procures a separately costed biological return pathway; it does not assume net soil-carbon sequestration without field evidence.')
 ptxt(doc,24,'Fig. 3. Elemental N/P/K conservation, treatment routes and external fertilizer replacement, with distinct biological and stable-carbon assumptions. Char permanence and plant nutrient availability are sensitivity parameters, not demonstrated field outcomes.')
 m=I['marine_to_land_optional']
 ptxt(doc,25,f'The imposed 220-GW offshore macroalgae case costs about $700.8 billion/year. A separate hypothetical marine-to-cropland nutrient transfer can displace purchases valued at ${m["avoided_fertilizer_purchase_value_bn"]*1000:.0f} million annually but foregoes ${m["foregone_existing_offshore_fertilizer_sale_credit_bn"]*1000:.0f} million in offshore product sales and incurs $200 million in additional treatment and transport. The net incremental cost is therefore ${m["extra_cost_after_opportunity_cost_bn"]*1000:.0f} million, conditional on contaminant removal and licensing; raw process liquor is never applied to fields.')
 ptxt(doc,27,'Fig. 4. Terrestrial and marine hydrothermal conversion pathways with explicit hydrochar and recovered aqueous nutrient routes to field-receiving soil. Product testing, agronomic eligibility and separate methane-carbon allocation are required; arrows indicate possible rather than measured transfers.')
 ptxt(doc,28,f'A revised 500-draw paired parameter screen, allowing crop-resource availability from zero to 166 Mt/year and independently disabling soil-carbon credits, gives a median partial abatement cost of ${U["abt_usd_t_median"]:.0f}/t CO₂e (5th–95th percentile ${U["abt_usd_t_p05"]:.0f}–${U["abt_usd_t_p95"]:.0f}/t). Oil-price assumptions dominate the sampled economic variation. These are conditional sensitivity results and not calibrated probabilities.')
 ptxt(doc,30,'Fig. 5. Paired economic sensitivity draws and conditional fixed-reactor-count search. Hub counts do not constitute an achievable licensing or construction schedule.')
 ptxt(doc,32,'The model identifies potential crop-residue cost reductions even when its most optimistic soil credits are removed. These bounds are not independent verification of 166 Mt annual sustainable removal: DOE BT23 distinguishes field crop residues from processing wastes, and subcategory allocations currently lack geographically resolved documentation. An importer for official county FIPS records is included, but the required full regional dataset is not present in the submission snapshot (2,23).')
 ptxt(doc,33,f'HTL process-water treatment, nutrient separation, fertilizer production, soil N₂O and amendment logistics add a gross candidate emissions burden of {L["central"]["gross_candidate_addon_mt"]:.2f} Mt CO₂e/year under one assumption set. Because the alternative emissions model already assigns aggregate lifecycle coefficients to fuel pathways, their potential overlap must be audited before the burden can be reported as a net additional national footprint. Soil carbon, indirect land use, contaminant pathways and reactor embodied materials remain incomplete (3,4,24).')
 ptxt(doc,34,'Reactor fleet sizes, hourly power reliability, regional transmission and fuel throughput remain prospective. A fixed-hub search produces lower mathematical costs for large hypothetical builds, but 945 hubs would require 3,780 modules. Reduced 30–150-hub screens carry higher yet comparable costs under the assumed technology-learning curve. Marine HTL, aquaculture, hemp, bamboo and Grid Harvester results remain engineering sensitivities; field-verified soil fertility and pilot nutrient-recovery evidence are still needed (10–18).')
 ptxt(doc,36,'We solved annual energy/material balances in Python using SciPy HiGHS and validated the archived AEO2026 workbook rows. Direct transport hydrogen and refining hydrogen are distinguished. Reference hydrogen is converted provisionally using 39.4 kWh/kg (HHV) consistent with EIA’s generally gross fuel-energy convention, with 33.33 kWh/kg (LHV) as a labelled sensitivity; the AEO table-specific convention requires confirmation. Five primary figures present the current model; supplementary figures report nutrient, agricultural lifecycle, marine pricing, nuclear and supply-bound screens. Source-specific HTL nutrient partition and long-run carbon stability remain unmeasured (1,8,9,24,25).')
 ptxt(doc,64,'Artificial intelligence: Artificial Inventor / Synthetic Scientist V63 assisted with computational source-code preparation, writing and reproducible data plots. All numerical values and conclusions require author verification; AI software is not an author. AI-assisted contributions are disclosed in the accompanying cover letter. No AI-generated painted artwork is submitted as evidence.')
 ptxt(doc,65,'Data and code availability: The complete V9.8 supporting snapshot includes AEO2026 source spreadsheets, numerical outputs, source code, checks and 600-dpi TIFF charts. The version-matched public GitHub release and archival DOI have NOT been confirmed. Full county-level BT23 resource data and feedstock-specific HTL experimental partition data are not included; claims requiring them are explicitly conditional.')
 ptxt(doc,66,'Supplementary materials: Text S1–S21; mathematical assumptions, emissions-ledger uncertainties and source crosswalks; supplementary tables and labelled TIFF figures, including Grid Harvester, seaweed, reactor and crop-soil diagnostics.')
 # Replace duplicate/reference-22 entry with actual independent source.
 ptxt(doc,59,'22. U.S. Department of Energy, Billion-Ton Report data portal, national feedstock resource categories and datasets (2024), https://bioenergykdf.ornl.gov/bt23-data-portal.')
 # add new literature sources before Acknowledgments
 ack=next(p for p in doc.paragraphs if p.text.strip()=='Acknowledgments')
 for t in [
 '23. Oak Ridge National Laboratory, BT23 Agricultural Download Tool (county and resource scenario data), https://bioenergykdf.ornl.gov/bt23-agricultural-download (accessed November 2026).',
 '24. Thermal treatment options for biosolids management: A critical review, Environmental Science: Water Research & Technology (2026), https://pubs.rsc.org/en/content/articlehtml/2026/ew/d5ew00569h.',
 '25. U.S. Energy Information Administration, British Thermal Unit and Other Conversion Factors, gross fuel heat-content methodology, https://www.eia.gov/totalenergy/conversion/factors/.'
 ]:ack.insert_paragraph_before(t)
 # Add a clear conclusions heading before references (main Science structure) with no unsupported field claims.
 before=next(p for p in doc.paragraphs if p.text.strip()=='References and Notes')
 pp=before.insert_paragraph_before('Conclusions');pp.style='Heading 1'
 before.insert_paragraph_before('The economically selected crop-residue pathway offers a conditional transport-cost reduction after priced nutrient replacement and conservative biological soil-carbon services. However, county-level supplies, HTL treatment recoveries, permanent soil carbon, agricultural lifecycle boundaries and buildable reactor deployment remain unverified. The contribution is a reproducible screening framework and a prioritized set of experiments rather than a validated national implementation forecast.')
 replace_images(doc,main_figs)
 path=P/'Research_Article_V9.8_Science.docx';doc.save(path)
 # document text tests
 chk=Document(path);assert len(chk.inline_shapes)==5
 return path

def supplemental_doc():
 doc=Document(P/'SOURCE_BASE_V97_Supplementary_Materials.docx')
 doc.paragraphs[0].text='Supplementary Materials — V9.8: crop-residue, soil-carbon and 2050 transport model'
 doc.paragraphs[1].text='Companion to: Economically selected crop residues and conservative soil restoration in U.S. transport decarbonisation'
 # correct marine opportunity price paragraph
 for p in doc.paragraphs:
  if 'potential avoided fertilizer purchases are' in p.text:
   m=I['marine_to_land_optional'];p.text=f'Under a hypothetical 50% treatment-eligible marine nutrient stream, potential avoided farm fertilizer spending is ${m["avoided_fertilizer_purchase_value_bn"]:.3f}bn/year, foregone offshore fertilizer-product revenue is ${m["foregone_existing_offshore_fertilizer_sale_credit_bn"]:.3f}bn/year, and assumed desalting, purification, transport and application cost is $0.200bn/year. Net additional cost after opportunity valuation is ${m["extra_cost_after_opportunity_cost_bn"]:.3f}bn/year. No marine nutrient is simultaneously sold and applied, and marine-char carbon is not credited to soils without testing.'
  if 'S14. Reproducibility' in p.text:p.text='S14. Reproducibility, heritage figures and limits of interpretation'
  if 'Code: run RUN_V97' in p.text:p.text='Run RUN_V98_VALIDATION.bat or ./RUN_V98_VALIDATION.sh to regenerate V9.8 research tables, economic sensitivity, agricultural emissions inventory, technical figures and Word documents. Dependency versions are pinned in requirements-v98.txt. Do not confuse preserved V9.7 technical charts with the active five main V9.8 figures; several earlier figures represent different historical parameterizations.'
 def h(t):doc.add_heading(t,level=1)
 def para(t):doc.add_paragraph(t)
 def table(title,headers,rows):
  para(title);t=doc.add_table(rows=1,cols=len(headers));t.style='Light Shading Accent 1'
  for j,c in enumerate(headers):t.rows[0].cells[j].text=str(c)
  for r in rows:
   cc=t.add_row().cells
   for j,c in enumerate(r):cc[j].text=str(c)
 h('S15. County-level agricultural residue data: present scope and importer')
 para('Official Oak Ridge National Laboratory BT23 agricultural exports provide rows by county FIPS, feedstock, scenario, price and dry short-ton production. These data are available from https://bioenergykdf.ornl.gov/bt23-agricultural-download, but the complete export was not available in this release. A shipped source-to-model parser, us98_resource_crosswalk.py, accepts a downloaded BT23 CSV and checks county FIPS, price, scenario, resource taxonomy and short-ton conversion. The absence of a county CSV is explicitly marked as NOT GEOGRAPHICALLY VALIDATED. The aggregate 166-Mt dry/year screen is not a field permit; processing and harvest residues cannot be silently added within the same category.')
 para('The additional regional-data-gap test limits primary crop streams to one-half or one-quarter of analyst capacities and excludes unverified food-processing, bagasse, corn-cob and milling coproduct substreams. This is NOT a county sum or a calculated sustainable removal rate; it tests economic resilience pending the actual ORNL/USDA regional import. Farm-level constraints include competing uses, erosion, nutrient return, moisture and soil organic carbon.')
 table('Table S9. Geographic-data-gap and soil-carbon stress screens.', ['Case','Crop Mt/yr','Annual cost $bn','Cover-crop C Mt/yr'], [(x['case'][:48],f"{x['crop_mt']:.1f}",f"{x['annual_cost_bn']:.2f}",f"{x['cover_crop_c_mt']:.2f}") for x in S['cases']])
 h('S16. Separately itemised agricultural lifecycle greenhouse gases')
 para('Candidate increments are fertilizer manufacture, field N2O from applied recovered and mineral N, HTL aqueous-phase treatment, hydrochar delivery and application, pyrocarbon transport and cover-crop establishment. For each category, model activity is multiplied by an explicitly disclosed engineering factor. The representative nitrogen fertilizer intensity is 4.0 kg CO2e/kg N, with phosphorus 2.0 and potassium 0.8 kg CO2e/kg element; direct N2O-N is 1.0% of applied N, multiplied by 44/28 and GWP100 273. Process water adds 0.035 t CO2e per tonne of dry feedstock and solid amendment transport adds 0.020 t/t. All are [A] factors, not universal literature constants.')
 para('The original alternative fuels already have aggregate lifecycle coefficients. We therefore report the entire new agricultural inventory as a GROSS candidate burden and do not treat it as additive without a process-level overlap audit. Indirect land-use change, persistent soil-stock trajectories, marine contaminant controls and infrastructure embodied carbon remain unknown, not assumed zero in a claimed comprehensive LCA.')
 table('Table S10. Candidate annual agricultural emissions inventory.', ['Component','Gross candidate Mt CO2e/year'],[(k.replace('_',' '),f'{v:.3f}') for k,v in L['central']['lines'].items()]+[('Total',f"{L['central']['gross_candidate_addon_mt']:.3f}")])
 h('S17. Carbon and NPK recovery stress: independent of theoretical permanence')
 para('The original V9.7 NPK mass ledger is elemental: removed = treated aqueous return + solids return + external replacement. Effective plant-available fractions, seasonal volatilisation and application losses are NOT empirically identified. We therefore test 50% of baseline nutrient recovery simultaneously with zero stable-hydrochar credit and zero methane-carbon soil-equivalence credit, forcing charged biological cover-crop C. Those scenarios preserve physical mass closure in the solver, but do not establish that soil productivity or soil aggregation is restored.')
 para('HTL should not be conflated with hydrothermal carbonization; solid and aqueous products can differ substantially by feedstock, temperature, and residence time. Nitrogen commonly enters the aqueous stream and phosphorus can partition into solids; plant availability must be measured. Experimental generalizations from sewage-sludge hydrothermal conversion are not automatically transferable to straw, husks and seaweed (https://pubs.rsc.org/en/content/articlehtml/2026/ew/d5ew00569h).')
 h('S18. Marine nutrient allocation and downstream opportunity cost')
 m=I['marine_to_land_optional']
 para('Treated marine nutrients diverted to agricultural fields displace fertilizer purchases but also forgo the offshore sale revenues already credited in the base solution. Agricultural replacement values (N $1.25/kg, P $2.60/kg, K $0.90/kg) differ from the offshore sale assumptions ($1.00, $1.50 and $0.70/kg). Thus net incremental cost = cleaning + foregone sales - avoided purchases. The original expression incorrectly used agricultural prices for both market streams.')
 table('Table S11. Marine-to-land transfer price reconciliation (US$bn/year).',['Term','Value'],[('Avoided replacement',f"{m['avoided_fertilizer_purchase_value_bn']:.6f}"),('Foregone offshore sales',f"{m['foregone_existing_offshore_fertilizer_sale_credit_bn']:.6f}"),('Extra treatment and logistics','0.200000'),('Net additional cost',f"{m['extra_cost_after_opportunity_cost_bn']:.6f}")])
 h('S19. Reference H2 energy convention and single-variable sensitivity')
 hh=B['h2_energy_basis_bracket'];para(f'AEO reports Btu-based fuel energies, and EIA conversion factors generally represent gross (HHV) contents. We therefore provisionally convert Table 36 freight H2 using 39.4 kWh/kg, giving {hh["HHV"]["hydrogen_mass_mt"]:.3f} Mt/year. The corresponding 33.33-kWh/kg LHV assumption gives {hh["LHV"]["hydrogen_mass_mt"]:.3f} Mt/year. The table-specific AEO hydrogen fuel convention should be confirmed rather than assumed certain. The V9.8 Figure S37 varies only hydrogen-production intensity while holding upstream fossil 10 g/MJ and electricity 50 g/kWh fixed; it no longer confounds three parameters.')
 h('S20. Reactor learning and buildability')
 para('The original learning solver is an iterative approximation to a non-convex problem. Fixed-hub sensitivity is evaluated at 0, 30, 60, 100, 150, 166, 250 and 945 hubs. These are mathematical screens, not planned annual construction schedules. No scenario has demonstrated the needed licensing rates, component supply chains, staffing, plant siting or hourly firm-power adequacy.')
 table('Table S12. Fixed-hub V9.8 learning sensitivities.', ['Hubs','Modules','Cost US$bn/year'],[(str(int(q['hubs'])),str(int(q['reactor_modules'])),f"{q['annual_cost_bn']:.2f}") for q in S['fixed_hub_cases']])
 h('S21. Conditional Monte Carlo, model provenance and supplementary figure guide')
 para(f'V9.8 recomputes 500 paired parameter draws with sustainable crop availability sampled from zero up to the assumed national ceiling, reactor capital, oil and electricity prices, BEV premium, fertilizer recovery, and hydrochar/pyrocarbon soil credit switches. Median abatement is ${U["abt_usd_t_median"]:.1f}/t (5th–95th: ${U["abt_usd_t_p05"]:.1f}–${U["abt_usd_t_p95"]:.1f}). The values are conditional responses to user-selected distributions, not statistical probabilities that a policy will succeed.')
 para('Literature and data sources supplement the main bibliography: DOE BT23 county download https://bioenergykdf.ornl.gov/bt23-agricultural-download ; 2026 RSC hydrothermal nutrient review https://pubs.rsc.org/en/content/articlehtml/2026/ew/d5ew00569h ; EIA Btu factors https://www.eia.gov/totalenergy/conversion/factors/ ; DOE Hydrogen Properties https://www.energy.gov/documents/fcm01r0pdf . County resources were not included; this is an explicit data gap.')
 # Embed comprehensive science-relevant appendix figures. Use resized in-doc PNGs only (not distributed separately), 600dpi TIFFs are separately archived.
 appendix=[
   ('S1','FigS1_grid_harvester.tif','Grid Harvester conceptual mechanism; unvalidated scale-up and operating dynamics.'),
   ('S9','FigS9_gas_extension.tif','Gas-use transition and model bounds.'),
   ('S10','FigS10_heat_and_boundaries.tif','Reactor thermal energy cascades and integrated boundaries.'),
   ('S11','FigS11_post_gas.tif','Non-pyrolysis hydrogen pathway sensitivity.'),
   ('S12','FigS12_sustainable_fission.tif','Advanced reactor deployment scenario engineering.'),
   ('S13','FigS13_fuel_transition.tif','Transport fuel transition, residual demand and carriers.'),
   ('S14','FigS14_nutrient_balance.tif','Historical nutrient balance model source comparison.'),
   ('S16','FigS16_RAS_process.tif','Recirculating aquaculture heat and water process design.'),
   ('S18','FigS18_Crop_HTL_Soil_Cycle.tif','HTL crop-solids and soil-recovery legacy engineering diagram.'),
   ('S19','FigS19_Crop_NPK_Balance.tif','Elemental N/P/K material closure.'),
   ('S22','FigS22_GridHarvester_Energy_Efficiency.tif','Grid Harvester calculated harvest-energy sensitivity, not fuel conversion efficiency.'),
   ('S26','FigS26_AEO_Freight_Stock_Reconciliation.tif','Freight-fleet size, classes and model cost adjustment.'),
   ('S31','FigS31_Reactor_Learning_Bounded_Search.tif','Reactor-learning objective sensitivity; construction infeasibility is not resolved.'),
   ('S34','ScienceFigS34_V97_Seaweed_Treated_Nutrient_Transfer.tif','Marine nutrient recovery eligibility and opportunity costs (V9.7 legacy pricing; see corrected S40).'),
   ('S35','ScienceFigS35_V97_Separate_Hydrochar_Streams.tif','Terrestrial and marine hydrochar streams not inherently interchangeable.'),
   ('S36','ScienceFigS36_V97_NPK_Recovery_Stress.tif','Agricultural nutrient capture fractions and external purchases.'),
   ('S37','ScienceFigS37_V97_Reference_H2_and_BEV_Price.tif','Unconfounded reference hydrogen-intensity and EV ownership price sensitivities, fixed V9.8.'),
 ]+new_si
 doc.add_page_break();h('Supplementary figure atlas — selected technical figures')
 for num,fn,cap in appendix:
  if not (P/fn).exists():continue
  d=doc.add_paragraph();d.alignment=WD_ALIGN_PARAGRAPH.CENTER
  with Image.open(P/fn) as im:
   img=im.convert('RGB');img.thumbnail((1650,1120));mem=io.BytesIO();img.save(mem,format='PNG',optimize=True);mem.seek(0)
   d.add_run().add_picture(mem,width=Inches(5.65))
  p=doc.add_paragraph(f'Fig. {num}. {cap}');p.paragraph_format.keep_together=True
 # Track preservation of other archival figures separately, without implying they belong to this manuscript's current dataset.
 para('Other inherited technical maps and figures remain in the reproducibility ZIP and are explicitly labelled historical model diagnostics. Their numerical content must not be treated as a V9.8 main result without checking the associated source and run configuration.')
 path=P/'Supplementary_Materials_V9.8_Science.docx';doc.save(path)
 return path

def cover():
 doc=Document(P/'SOURCE_BASE_V97_Cover_Letter.docx')
 title='Economically selected crop residues and conservative soil restoration in U.S. transport decarbonisation'
 for p in doc.paragraphs:
  if 'Please consider' in p.text:p.text=f'Please consider the Research Article “{title}” for publication in Science.'
  if 'selected 166-Mt crop-residue ceiling' in p.text:p.text='The study optimises candidate transport fuel, hydrogen and circular agricultural pathways with explicit N/P/K mass closure, while distinguishing the national residue screening ceiling from geographically verified sustainable harvest. We stress-test zero agricultural soil-carbon credits and lower nutrient recovery, report unquantified HTL and soil emissions separately, and preserve a reproducible county-level resource importer for future data verification.'
  if 'Under one source-stock-weighted' in p.text:p.text=f'An AEO2026 2050 partial reference costs approximately ${ref:.1f}bn/year versus ${stric["annual_cost_bn"]:.1f}bn/year for the joint conservative alternative, before any unverified net adjustment for gross agricultural process emissions. We do not claim a comprehensive national lifecycle comparison or an observed field-level removal rate.'
  if 'The attached submission set' in p.text:p.text='The accompanying package provides five current main 600-dpi TIFF figures, the substantially expanded illustrated supplement, reproducible source code, 38 original EIA workbooks, explicit agricultural process-lifecycle sensitivity, conservative biomass and nuclear tests, validation scripts and source hashes.'
  if 'Artificial Inventor' in p.text:p.text='Artificial Inventor / Synthetic Scientist V63 supported computational research, source editing and code-rendered data figures; the authors take responsibility for scientific verification and shall supply full AI-use records if requested. No generative painting is represented as a scientific data figure.'
 path=P/'Cover_Letter_Science_V9.8.docx';doc.save(path);return path

def titlepage():
 doc=Document(P/'SOURCE_BASE_V97_Title_Page.docx')
 for p in doc.paragraphs:
  if p.text.startswith('National crop residues'):p.text='Economically selected crop residues and conservative soil restoration in U.S. transport decarbonisation'
 path=P/'Title_Page_V9.8_Science.docx';doc.save(path);return path
if __name__=='__main__':
 print(main_doc());print(supplemental_doc());print(cover());print(titlepage())
