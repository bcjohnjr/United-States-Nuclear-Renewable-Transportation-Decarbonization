#!/usr/bin/env python3
"""V9.7 AAAS *Science* Research Article + technical SI, reproducibly typeset.
Five main plots are reported as individual 600-dpi TIFFs, with source code;
only internal temporary PNG representations are used for Word layout.
"""
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from PIL import Image
from pathlib import Path
import json,csv,os,math,io,datetime
R=Path(__file__).resolve().parent
A=json.loads((R/'US97_AEO_Boundary.json').read_text())
J=json.loads((R/'US97_Integrated_Circular_EIA.json').read_text())
U=json.loads((R/'US97_Paired_Uncertainty_Summary.json').read_text())
C=J['scenario']['soil_costed_economic_crop'];NC=J['scenario']['soil_costed_no_crop'];SW=J['scenario']['crop_seaweed_220gw_imposed'];REF=J['source_weighted_reference_partial_bn'];EMO=J['source_weighted_reference_emissions_partial_mt'];AVOID=EMO-C['emissions_wtw_mt'];DELTA=C['annual_cost_bn']-REF;CPT=1000*DELTA/AVOID
T='National crop residues, nutrient recycling and the cost of petroleum-free U.S. transport in 2050'
MAIN=[
' ScienceFig1_V97_2050_Cost_Abatement.tif'.strip(),
' ScienceFig2_V97_All_Crop_Waste_Economic_Dispatch.tif'.strip(),
' ScienceFig3_V97_NPK_Carbon_Soil_Closure.tif'.strip(),
' ScienceFig4_V97_Terrestrial_Marine_HTL_Soil_Flow.tif'.strip(),
' ScienceFig5_V97_Uncertainty_Resource_Constraints.tif'.strip(),]
SFIG=[
'ScienceFigS34_V97_Seaweed_Treated_Nutrient_Transfer.tif',
'ScienceFigS35_V97_Separate_Hydrochar_Streams.tif',
'ScienceFigS36_V97_NPK_Recovery_Stress.tif',
'ScienceFigS37_V97_Reference_H2_and_BEV_Price.tif',]
CIT=[
'U.S. Energy Information Administration (EIA), Annual Energy Outlook 2026, Counterfactual Baseline, Tables 3, 7, 12, 36, 39, 49, 52 and 70 (2026), https://www.eia.gov/outlooks/aeo/.',
'U.S. Department of Energy and Oak Ridge National Laboratory, 2023 Billion-Ton Report: An Assessment of U.S. Renewable Carbon Resources, ORNL/SPR-2024/3103 (2024), doi:10.23720/BT2023/2316165.',
'P. Jaramillo et al., “Transport,” in Climate Change 2022: Mitigation of Climate Change, IPCC Working Group III, chap. 10 (Cambridge Univ. Press, 2022).',
'U.S. Environmental Protection Agency (EPA), Inventory of U.S. Greenhouse Gas Emissions and Sinks: 1990–2023, EPA 430-R-25-001 (2025).',
'S. J. Davis et al., Net-zero emissions energy systems, Science 360, eaas9793 (2018).',
'Pacific Northwest National Laboratory, 2024 Whole Algae Hydrothermal Liquefaction and Upgrading, PNNL-37209 (2024), https://www.pnnl.gov/main/publications/external/technical_reports/PNNL-37209.pdf.',
'N. Sánchez-Bastardo, R. Schlögl and H. Ruland, Methane pyrolysis for zero-emission hydrogen production: A potential bridge technology, Ind. Eng. Chem. Res. 60, 11855–11881 (2021).',
'P. Virtanen et al., SciPy 1.0: Fundamental algorithms for scientific computing in Python, Nat. Methods 17, 261–272 (2020).',
'Q. Huangfu and J. A. J. Hall, Parallelizing the dual revised simplex method, Math. Program. Comput. 10, 119–142 (2018).',
'A. Abou-Jaoude et al., Literature Review of Advanced Reactor Cost Estimates, INL/RPT-23-72972 (Idaho National Laboratory, 2024).',
'U.S. Department of Energy, Pathways to Commercial Liftoff: Advanced Nuclear (2024 update).',
'D. S. Wendt, L. T. Knighton and R. D. Boardman, High-Temperature Steam Electrolysis Process Performance and Cost Estimates, INL/RPT-22-66117 (Idaho National Laboratory, 2022).',
'F. W. R. Ross, M. E. Malerba and P. I. Macreadie, Global potential for seaweed aquaculture on existing offshore infrastructure, Heliyon 11, e41248 (2025).',
'M. Stekoll et al., Development of scalable coastal and offshore kelp farming for marine biomass production, J. World Aquac. Soc. (2025), doi:10.1111/jwas.70017.',
'M. A. Waqas et al., Environmental performance of seaweed cultivation and use in different industries: A systematic review, Sustain. Prod. Consum. 48, 123–142 (2024).',
'H. E. Froehlich, J. C. Afflerbach, M. Frazier and B. S. Halpern, Blue growth potential to mitigate climate change through seaweed offsetting, Curr. Biol. 29, 3087–3093 (2019).',
'U.S. Department of Energy, ARPA-E MARINER: Macroalgae Research Inspiring Novel Energy Resources, programme description, https://arpa-e.energy.gov/.',
'L. Clarke et al., “Energy systems,” in Climate Change 2022: Mitigation of Climate Change, IPCC Working Group III, chap. 6 (2022).',
'T. P. Wright, Factors affecting the cost of airplanes, J. Aeronaut. Sci. 3, 122–128 (1936).',
'U.S. Energy Information Administration, Monthly Energy Review, October 2026, Table 2.5, https://www.eia.gov/totalenergy/data/monthly/.',
'U.S. Nuclear Regulatory Commission, Long Mott Generating Station construction permit (9 November 2026), https://www.nrc.gov/.',
'U.S. Department of Energy, U.S. energy and agricultural residue assessments, DOE 2023 Billion-Ton Report, op. cit. (2024).',
]

def docsetup(doc):
 sec=doc.sections[0];sec.page_width=Inches(8.5);sec.page_height=Inches(11)
 sec.top_margin=Inches(.74);sec.bottom_margin=Inches(.70)
 sec.left_margin=Inches(.78);sec.right_margin=Inches(.78)
 styles=doc.styles
 s=styles['Normal'];s.font.name='Aptos';s.font.size=Pt(9.4);s.paragraph_format.space_after=Pt(5)
 s.paragraph_format.line_spacing=1.16
 for k,pt in [('Title',15),('Heading 1',11),('Heading 2',10)]:
  st=styles[k];st.font.name='Aptos Display';st.font.size=Pt(pt);st.font.color.rgb=RGBColor(32,57,72)
 return doc

def para(doc,text='',bold=False,style=None):
 p=doc.add_paragraph(style=style)
 if bold:p.add_run(text).bold=True
 else:p.add_run(text)
 return p

def heading(doc,text,level=1):return doc.add_heading(text,level)

def addtable(doc,heads,rows,widths=None):
 t=doc.add_table(rows=1,cols=len(heads));t.style='Light Shading Accent 1';t.alignment=WD_TABLE_ALIGNMENT.CENTER
 for i,h in enumerate(heads):t.rows[0].cells[i].text=str(h)
 for row in rows:
  cs=t.add_row().cells
  for i,v in enumerate(row):cs[i].text=str(v)
 for row in t.rows:
  for cell in row.cells:cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
 return t

def addfig(doc,filename,cap,scale=6.55):
 # Source TIFF remains the only externally distributed figure representation;
 # a temporary PNG inserted into DOCX is strictly a Word compatibility layer.
 from PIL import Image
 f=R/filename;out=R/('_WORD_TEMP_'+f.stem+'.png')
 with Image.open(f) as im: im.convert('RGB').save(out,format='PNG',optimize=True)
 pi=doc.add_paragraph();pi.paragraph_format.keep_with_next=True
 pi.alignment=WD_ALIGN_PARAGRAPH.CENTER
 pi.add_run().add_picture(str(out),width=Inches(scale))
 p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.LEFT
 p.paragraph_format.keep_together=True
 r=p.add_run(cap);r.italic=True;r.font.size=Pt(8)

abs_text=(
'National petroleum-free transport in 2050 requires a reference fleet that already includes electric vehicles. '
'Using AEO2026 activity and vehicle prices, we jointly screen electrification, hydrogen, nuclear process heat, renewable liquids, and 13 types of food-crop residues. '
'Under illustrative national supply and soil constraints, the model selects 166 million tonnes of residues and returns treated nutrients and hydrochar, while requiring imported nitrogen, phosphorus, and potassium. '
'A stock-weighted, soil-costed alternative costs about $651 billion annually versus a $477 billion partial reference screen, or about $123 per tonne of CO₂e avoided. '
'A 500-draw uncertainty screen yields a median near $121 per tonne. '
'These estimates are conditional: local biomass removal, nutrient recovery, reactor deployment, and full lifecycle boundaries remain unverified.'
)
assert len(abs_text.split())<=125,len(abs_text.split())

def main_document():
 d=docsetup(Document());p=d.add_paragraph(style='Title');p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.add_run(T)
 p=d.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.add_run('Jonathan Karl Bily¹*  ·  Christoph Pahl²  ·  Patricia Valdés Bacallao³')
 p=d.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.add_run('¹ Independent Researcher, Spain   ² Technical University of Munich, Germany   ³ University of Málaga, Spain')
 p=d.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.add_run('* Correspondence: jonathan@cloudwashlaundry.com  |  ORCID: 0009-0004-3526-7271')
 para(d,'One-sentence summary: At a 2050 activity and vehicle-price baseline, field-screened crop residues and recovered nutrients help constrain—not eliminate—the cost of a prospective petroleum-free U.S. transportation system.')
 heading(d,'Abstract');para(d,abs_text)
 heading(d,'Introduction')
 para(d,'The U.S. transportation sector spans light-duty mobility, freight trucks, rail, shipping, aircraft, farming and construction. An oil-free energy system must replace liquid fuels where electrification is difficult while respecting electricity supply, resource availability and soil constraints (1–5). The Annual Energy Outlook 2026 (AEO2026) Counterfactual Baseline already contains an extensively electrified 2050 vehicle fleet. A petroleum-only comparison at historical prices would therefore misstate the counterfactual (1).')
 para(d,'We evaluate whether economically useful crop residues—including corn stalks, cobs and husks; wheat straw; rice residues; sorghum; soybean stems; cotton; bagasse; orchard prunings; and food-processing solids—can support transport fuels while returning recovered nutrients and carbon to the originating agricultural system. The DOE 2023 Billion-Ton Report provides a national screening ceiling, but field-level eligibility is distinct from national availability (2). We also test separately the conversion of marine macroalgae to hydrothermal-liquefaction (HTL) fuels and recovered nutrient coproducts (6).')
 heading(d,'Modelling framework')
 para(d,'A national annual optimisation allocates wind, solar, high-temperature reactor heat, hydrogen, methane pyrolysis, hydrothermal liquefaction, alternative aviation fuels and vehicle technologies. The electricity and hydrogen balances use the corrected heavy-truck energy conversion. Construction and capital costs, a four-module reactor-hub topology, and lifecycle-intensity ranges remain engineering assumptions, not forecasts (7–12). The model does not simulate hourly network reliability or demonstrate a licensing and construction schedule.')
 para(d,'AEO2026 Tables 3, 36, 39, 49, 52 and 70 provide 2050 fleet stock, activity, energy expenditure, new-vehicle purchase prices and direct transport CO₂. We apply the same illustrative BEV net purchase-cost differential to the already-electrified reference and proposed fleets. The primary source-weighted case uses 60.8% 300-mile and 38.9% 200-mile BEVs in the EIA stock, with the remaining approximately 0.3% proxied using the 200-mile price. A 7% capital-recovery sensitivity replaces straight-line annualisation; these are not verified vehicle-sales-weighted lifetime costs (1).')
 para(d,'Thirteen crop-residue classes enter the same linear programme as alternative fuels, each with a separately costed delivery, HTL treatment, elemental N/P/K content, nutrient-recovery fraction and field carbon replacement requirement. Their total is capped at 166 Mt dry/year, with overlapping corn/rice material excluded through additional source-group ceilings. Individual class capacities are explicitly assumed screening values, not measured state-by-state supplies. The model may reject uneconomic categories, and no material is removed from a field unless erosion, soil carbon and regulatory limits permit it (2).')
 heading(d,'Results')
 para(d,f'The stock-weighted 2050 reference costs ${REF:.1f} billion/year under the stated partial purchase-price, tax and infrastructure boundary; the corresponding alternative without new soil constraints costs ${A["results"][1]["alternative_cost_bn"]:.1f} billion/year. Incorporating the separately costed land-residue and soil loop gives ${C["annual_cost_bn"]:.1f} billion/year, ${DELTA:.1f} billion above the reference, with a conditional partial emissions saving of {AVOID:.0f} Mt CO₂e/year (${CPT:.0f}/t). A 7%-financed BEV comparison raises the cost per tonne relative to straight-line ownership accounting. These are screening numbers, not a fully harmonised national total-cost or lifecycle assessment (fig. 1).')
 addfig(d,MAIN[0],'Fig. 1. AEO2026-grounded reference and petroleum-free alternative. (A) Common vehicle-cost assumptions and the soil-costed crop variant. (B) Partial-emissions abatement-cost screens; these are not predictive forecasts.',6.45)
 para(d,f'Of the candidate crop types, the optimiser selects {C["crop_htl_mt"]:.0f} Mt dry/year, the national assumed ceiling, equivalent to {C["crop_htl_liquid_twh"]:.1f} TWh of upgraded liquid fuel. Corn stems/leaves, cobs/husks, wheat straw, mill rice husks and sugarcane bagasse are selected in this parameterisation (fig. 2). Other candidate streams are explicitly represented but not selected at the assumed delivered cost and nutrient-restoration penalty. The chosen mix is not evidence that all of these supplies can be harvested sustainably in practice.')
 addfig(d,MAIN[1],'Fig. 2. Economic dispatch across 13 candidate crop-residue streams. Category capacities and costs are sensitivity assumptions [A], not estimated state-level USDA inventories; the aggregate 166-Mt ceiling is separately constrained.',6.45)
 para(d,f'The {C["crop_htl_mt"]:.0f}-Mt case removes {C["n_removed_kt"]:.0f}, {C["p_removed_kt"]:.0f} and {C["k_removed_kt"]:.0f} kt/year of elemental N, P and K. Treated process-water and solid coproducts recover part of these amounts, leaving external purchases of {C["n_imports_kt"]:.0f} kt N, {C["p_imports_kt"]:.1f} kt P and {C["k_imports_kt"]:.0f} kt K annually. These are elemental quantities, not fertilizer-oxide equivalents. Returning solid material and nutrient concentrates is conditioned on contaminant removal and field-soil testing. Nutrient balance is achieved arithmetically with external fertilizer; it is not a self-contained nutrient cycle (fig. 3A).')
 para(d,f'The modeled field carbon requirement is {C["stable_soil_c_need_mt"]:.2f} Mt/year stable-equivalent C. Assumed durable hydrochar supplies {C["stable_hydrochar_c_mt"]:.2f} Mt and allocated methane-pyrolysis carbon {C["stable_pyrolysis_c_mt"]:.2f} Mt, with separately charged cover crops filling any gap. The hydrochar corresponds to {C["crop_hydrochar_mt"]:.1f} Mt of solid coproduct. The use of pyrolysis carbon as agronomically equivalent to protected soil organic carbon is unvalidated; excluding that credit remains a required sensitivity (fig. 3B).')
 addfig(d,MAIN[2],'Fig. 3. Crop N/P/K mass closure and stable-equivalent carbon screening. (A) Treated-water and solid recovery plus external replacement. (B) Hypothetical soil-carbon-return services, which are not a demonstrated recovery of soil function.',6.45)
 para(d,f'Imposing six offshore seaweed zones raises the combined annual alternative to ${SW["annual_cost_bn"]:.1f} billion, compared with ${C["annual_cost_bn"]:.1f} billion for the zero-offshore crop case. It yields {SW["seaweed_htl_mt"]:.1f} Mt dry macroalgal HTL feedstock and an illustrative {SW["seaweed_hydrochar_screen_mt"]:.2f} Mt solid hydrochar. Its estimated marine treated nutrient coproducts are tracked separately, avoiding double-counting the pre-existing fertilizer-sale credit. A conditional 50% redirection to farmland would still require treatment, desalting, toxic-metal screening and nutrient application permits; seaweed-char stability is not credited to cropland by default (fig. 4).')
 addfig(d,MAIN[3],'Fig. 4. Additive terrestrial/marine HTL material flow, solid-carbon coproducts and conditional treated nutrient return. The schematic does not assert demonstrated blended-feedstock yields or direct application of raw HTL liquor.',6.45)
 para(d,f'Across {U["n"]} paired simulations with explicit analyst-defined ranges for BEV costs, oil and electricity prices, reactor learning, crop supply and nutrient recovery, the median partial abatement cost is ${U["abt_usd_t_median"]:.0f}/t CO₂e (5th–95th percentile ${U["abt_usd_t_p05"]:.0f}–${U["abt_usd_t_p95"]:.0f}/t). The median selected crop volume is {U["crop_selected_mt_median"]:.1f} Mt/year. The distributions are neither calibrated to empirical likelihoods nor a probability of actual national cost advantage (fig. 5).')
 addfig(d,MAIN[4],'Fig. 5. Paired 500-draw parameter sensitivity (A) and deterministic resource/environmental variants (B). Uncertainty ranges are assumed, not statistical forecasts; the 220-GW seaweed case is an imposed sensitivity.',6.45)
 heading(d,'Discussion')
 para(d,f'Under the explicit national residue cap, the soil-costed mixed-crop optimisation saves ${NC["annual_cost_bn"]-C["annual_cost_bn"]:.1f} billion/year relative to a matched zero-crop case in which the other non-crop feedstock assumptions remain unchanged. This is an incremental resource benefit, not a claim that the full transport system is cheaper than the AEO2026 partially electrified reference. The 166-Mt result saturates the assumed national ceiling and therefore needs local soil safeguards, alternative disposal baselines and subnational collection-cost validation.')
 para(d,'Macroalgae can potentially supply wet HTL inputs and recoverable N, P and K, but the treated marine output cannot automatically be returned to farmland: salts, trace metals and biologically inhibitory organics must be managed. Likewise, HTL solid hydrochar is not interchangeable with certified agricultural biochar, and durable methane-derived black carbon cannot be assumed to restore soil aggregation, microbial substrates or fertility solely by persistence (6,13–17). The model credits no unverified synergistic increase in liquid-fuel yield from mixing marine and terrestrial feedstocks.')
 para(d,'The reactor component remains constrained by high initial capital costs, fleet-learning uncertainty, manufacturing throughput and limited hourly-feasibility analysis (10–12,18–19). Transportation aviation growth, 2050 petroleum price assumptions and omitted vehicle or infrastructure embodied emissions materially change the cost per tonne. A field-validated, geographically resolved farm-to-refinery and refinery-to-field model is the next necessary test.')
 heading(d,'Materials and Methods')
 para(d,'The full model is implemented in Python/SciPy HiGHS (8,9). We reproduced the archived AEO2026 baseline workbooks by SHA-256, corrected the diesel excise reference to Table 36 row 24, and explicitly identified inclusion/exclusion of pipeline energy, recreational boats and LNG-export liquefaction. Reference freight hydrogen is assigned an independent 0–15 kg CO₂e/kg hydrogen upstream-production sensitivity because EIA fuel consumption does not specify its complete production lifecycle. We use a 500-draw paired parameter screen and provide deterministic soil and nutrient recovery stress tests. Full equations, feedstock assumptions, emissions scope and code are supplied in the supplementary materials and reproducibility files.')
 heading(d,'References and Notes')
 for i,ref in enumerate(CIT,1):para(d,f'{i}. {ref}')
 heading(d,'Acknowledgments')
 para(d,'Funding: No external funding was received for this analysis.')
 para(d,'Competing interests: The corresponding author is associated with Cloud Wash Laundry Corporation and has reported intellectual-property filings concerning related infrastructure. The commercial applicability of the concepts is disclosed; the calculations do not represent commissioned commercial validation.')
 para(d,'Author contributions: J. K. Bily conceptualization, computational investigation, original drafting and data curation; C. Pahl and P. Valdés Bacallao contributions and approval require confirmation from the individuals before journal submission.')
 para(d,'Artificial intelligence: Artificial Inventor / Synthetic Scientist V63 assisted with source-code development, text editing and reproducible scientific plots. All modeled values are generated by the identified analysis scripts. The authors take responsibility for evaluation, accuracy and submission policies.')
 para(d,'Data and materials availability: A complete version-matched archive of Python code, archived AEO2026 workbooks, checksums, numerical outputs and TIFF figure source is supplied with this manuscript. The public repository is https://github.com/bcjohnjr/United-States-Nuclear-Renewable-Transportation-Decarbonization; no unpublished DOI is claimed.')
 para(d,'Supplementary materials: Supplementary Text S1–S14; Tables S1–S8; additional source figures, Grid Harvester technical diagrams, reaction-route and deployment checks; executable code and original EIA workbooks.')
 out=R/'Research_Article_V9.7_Science.docx';d.save(out)
 print('main saved',out,'abstract',len(abs_text.split()),'paras',len(d.paragraphs))
 return out

def supplemental():
 d=docsetup(Document());heading(d,'Supplementary Materials: national petroleum-free transport and circular crop/seaweed nutrient pathways',1)
 para(d,'Companion to: '+T+' | Technical details, source flags, equations, uncertainty, figs. S1–S37 and original modelling scripts.')
 heading(d,'S1. AEO2026 sources and comparable service boundary',2)
 para(d,'AEO2026 source workbook archive contains 38 Table spreadsheets plus CSV extracts and SHA-256 manifest. Tables 3, 7, 12, 36, 39, 49, 52 and 70 govern 2050 stock, travel, mode fuel and costs. The partially electrified reference includes 154.44 million BEV light-duty vehicles among 334.77 million light-duty stock; medium-plus-heavy trucks total approximately 12.56 million. EIA reference energy expenditure is not a full national vehicle/infrastructure TCO. The comparison uses identical illustrative purchase-price differentials, vehicle activity and explicit tax/scope adjustments (1).')
 heading(d,'S2. Reference vehicle purchase-price and financing sensitivities',2)
 para(d,'AEO2026 Table 52 new-vehicle prices are sampled from four model classes: compact, midsize, small crossover and large pickup, with assumed class weights .25,.25,.30,.20. BEV installed stock is approximately 60.8% 300-mile, 38.9% 200-mile and 0.3% 100-mile; the smallest class is proxied at 200-mile price. Purchased BEV cost differences versus gasoline are annualised for 15 years under both straight-line and 7% capital recovery and offset by an assumed $250/year maintenance saving. These are sensitivity inputs, not measured fleet sales or complete finance cost.')
 rows=[]
 for r in A['results'][:3]:rows.append((r['label'][:38],f"{r['net_bev_differential_usd_yr']:.0f}",f"{r['reference_screen_bn']:.1f}",f"{r['alternative_cost_bn']:.1f}",f"{r['abatement_usd_t']:.0f}"))
 para(d,'Table S1. AEO vehicle-stock and capital-recovery sensitivity (annual US$bn; BEV premium US$/vehicle/year; abatement US$/t CO₂e).')
 addtable(d,['Illustrative case','Net BEV','Reference','Alternative','Abatement'],rows)
 heading(d,'S3. Corrected 2050 fuel, fossil and hydrogen scope',2)
 para(d,f'Table 36 on-road commercial light-truck diesel is Excel row 24 (not row 23 E85). On-road diesel tax uses the exact row list {A["tax_36"]["table36_source_rows"]["diesel_onroad"]}. Fuel-use totals exclude heading subtotals to prevent duplication. Pipeline natural gas, international shipping, military fuels and recreational boats are identified individually; LNG-export liquefaction (row 106) is excluded from direct transport. Table 70 direct emissions are included ONCE; add-ons only cover assumed upstream emissions and electricity supply. Freight H₂ is {A["reference_emissions"]["hydrogen_energy_tbtu"]:.1f} trillion Btu ({A["reference_emissions"]["hydrogen_mass_mt"]:.2f} Mt on LHV). Production carbon intensity remains a 0–15 kg CO₂e/kg H₂ sensitivity because the AEO row does not specify its total production route.')
 para(d,'Table S2. Reference emissions boundary. Annual Mt CO₂e; assumed 0, 10 or 15 kg CO₂e per kg hydrogen co-produced in the national reference.')
 addtable(d,['H₂ intensity','Direct','Fossil upstream','Electricity','H₂ production','Partial WTW'],[(str(z['reference_h2_production_kgco2_kg']),f"{z['direct_mt']:.1f}",f"{z['added_upstream_mt']:.1f}",f"{z['added_electricity_mt']:.1f}",f"{z['added_hydrogen_mt']:.1f}",f"{z['screening_wtw_mt']:.1f}") for z in A['corrected_lifecycle_ranges']])
 heading(d,'S4. Physical crop availability, types and double-counting controls',2)
 para(d,'Feedstock class caps below are independent analyst assumptions [A]. The *national* 166-Mt dry crop-residue ceiling is a high-level DOE BT23 mature-market screening constraint, not a statement that each listed class is independently collectible or each field can sustain it. Corn stalks/leaves EXCLUDE cobs/husks; rice straw excludes milled husks; group caps prevent those physical streams from being counted twice. The baseline ambiguous 350-Mt mixed crop/forest feedstock tiers are removed in all V9.7 crop cases and replaced by the named crop pools plus separate, explicitly assumed non-crop tiers (2).')
 para(d,'Table S3. Feedstocks by type. Mt/year dry biomass; unit collection and treatment costs include NPK replacement [A], and no agronomic concentrations are presented as measurements.')
 rows=[]
 for v in C['selected']:
  rows.append((v['name'][:48],f"{v['max_mt']:.0f}",f"{v['selected_mt']:.1f}",f"{v['delivered_and_soil_usd_t']:.0f}",'/'.join(f"{v['npk_kg_t'][e]:.1f}" for e in ('n','p','k'))))
 addtable(d,['Crop residue','[A] cap Mt','Selected Mt','All-in $/t','N/P/K kg/t [A]'],rows)
 heading(d,'S5. Nutrient conservation and fertilizer sourcing',2)
 para(d,'Elemental balance for e in {N, P, K}: Removed_e = Σ_i (dry feedstock_i × e_kg_per_t_i); Recovered_e = water_e + solid_e; External replacement_e = Removed_e − Recovered_e. Recovered-water nutrients are counted only after a permitted treatment and concentration process. A closed arithmetic balance can be achieved with purchased imports; physical soil function remains unverified. No P₂O₅ or K₂O values are silently treated as elemental quantities. Saskatchewan potash is an identified candidate supply source, not a logistics contract.')
 para(d,'Table S4. Modelled crop N, P, K balance, kilotonnes element per year. Mineral imports are explicitly paid for.')
 rows=[(e.upper(),f"{C[e+'_removed_kt']:.1f}",f"{C[e+'_water_kt']:.1f}",f"{C[e+'_char_kt']:.1f}",f"{C[e+'_imports_kt']:.1f}") for e in ('n','p','k')]
 addtable(d,['Element','Removed','Treated water','Solid char','Imports'],rows)
 para(d,f'K deficit {C["k_imports_kt"]:.1f} kt elemental K corresponds to approximately {C["k_imports_kt"]/(39.0983/(39.0983+35.45)):.0f} kt/year potassium chloride (KCl) at theoretical pure-product composition; a commercial potash grade would require purity and delivery adjustments. Legume cover crops, digestate and manure could substitute for some purchased nitrogen only with farm-specific nutrient plans.')
 heading(d,'S6. Soil-carbon return and pyrolysis-carbon constraints',2)
 para(d,'HTL land-crop feedstock is assigned 0.12 t solid char/t feedstock, 65% carbon fraction and 55% stable-equivalent carbon fraction [A]. Pyrolysis solid carbon is charged $60/t for field application and receives 85% durability equivalence [A] only in one sensitivity. Soil organic-carbon function (structure, microbial food, water retention) is not established by carbon durability alone; a no-pyrolysis-soil-credit and no-hydrochar-stability-credit scenario is reported. The model also permits cover-crop-derived stable carbon at $250/t of stable C [A].')
 para(d,'Table S5. Annual hypothetical stable-equivalent carbon fluxes, Mt of carbon/year; these are not directly measured soil-carbon changes.')
 addtable(d,['Component','Mt stable-equivalent C'],[
  ('Required residue-origin carbon replacement',f"{C['stable_soil_c_need_mt']:.3f}"),
  ('Land HTL hydrochar',f"{C['stable_hydrochar_c_mt']:.3f}"),
  ('Methane-derived solid carbon allocated to fields',f"{C['stable_pyrolysis_c_mt']:.3f}"),
  ('Extra cover crop carbon',f"{C['cover_crop_stable_c_mt']:.3f}"),
 ])
 heading(d,'S7. Combined macroalgal and terrestrial HTL',2)
 para(d,f'The imposed six-zone offshore design converts {SW["seaweed_htl_mt"]:.1f} Mt dry seaweed by HTL and {SW["seaweed_pbtl_mt"]:.1f} Mt through PBTL. The mass-equivalent seaweed solid byproduct is {SW["seaweed_hydrochar_screen_mt"]:.2f} Mt under an assumed 0.12 t/t char yield. The source model already credits fertilizer coproduct market values. The marine nutrient recovery is therefore first counted as marketable treated nutrient product, not simultaneously credited against crop NPK imports; nutrient return to a field is an explicit market-reallocation stress case. Marine feedstock contains salts and may contain trace metals, requiring separate treatment, bioassays and legal applications (6,13–17).')
 mar=SW['marine']; land=J['marine_to_land_optional']
 para(d,'Table S6. Optional marine nutrient recovery, all elemental kt/year; a 50% hypothetical eligible fraction gives *possible* cropland redirection but no unpriced sale and field credits together.')
 addtable(d,['Element','Marine treated product','Potential farm allocation','Remaining external import'],[(e.upper(),f"{mar['recovered_treated_product_kt'][e]:.1f}",f"{land['eligible_treated_marine_npk_to_cropland_kt'][e]:.1f}",f"{land['residual_elemental_imports_kt'][e]:.1f}") for e in ('n','p','k')])
 para(d,f'Under [A] 50% treatment eligibility, potential avoided fertilizer purchases are ${land["avoided_fertilizer_purchase_value_bn"]:.2f}bn/year, offset by the same foregone coproduct sale value, plus an assumed ${land["purification_desalting_and_field_logistics_extra_bn"]:.2f}bn/year of transfer and cleaning. No field credit is assigned to marine char pending agronomic testing. Mixed terrestrial/marine HTL uses additive yields, not experimental evidence of enhanced yields or co-conversion chemistry.')
 heading(d,'S8. Economic counterfactual with crop routes',2)
 para(d,'Table S7. The AEO2026 source-weighted BEV ownership model is held identical across these alternatives. The reference cost includes explicit fuel taxes, vehicle premiums and assumed missing-scope allowances and is not an official EIA total ownership forecast.')
 rows=[(k.replace('_',' '),f"{z['annual_cost_bn']:.1f}",f"{z['crop_htl_mt']:.0f}",f"{z['seaweed_htl_mt']:.1f}") for k,z in J['scenario'].items()]
 addtable(d,['Alternative scenario','Annual US$bn','Crop Mt','Marine HTL Mt'],rows)
 heading(d,'S9. 500-draw joint uncertainty',2)
 para(d,f'A 500-draw paired simulation samples analyst-defined BEV cost adjustments, oil prices, onshore/solar/LWR costs, reactor capital cost, crop delivered prices, national sustainable collection ceiling (50–100% of 166 Mt), nutrient capture, methane solid-carbon soil eligibility and reference H₂ intensity. The median partial abatement cost is ${U["abt_usd_t_median"]:.1f}/t, with fifth and ninety-fifth percentiles ${U["abt_usd_t_p05"]:.1f} and ${U["abt_usd_t_p95"]:.1f}/t. These are parameter-screen results, not calibrated probabilities of climate-policy outcomes.')
 para(d,'Table S8. Primary Spearman rank sensitivities of screening abatement cost.')
 addtable(d,['Parameter','Spearman rho'],[(k.replace('_',' '),str(v)) for k,v in U['parameter_spearman_against_abatement'].items()])
 heading(d,'S10. Hydrogen, methane pyrolysis and reactor process heat',2)
 para(d,'Direct transportation demand is 188.44 TWh/year H₂, distinct from total hydrogen produced for direct use and refining. Reactors and electrolysis options are prospective engineering screens. High-temperature gas and fuel-stream heat matching must respect actual temperature levels and equipment. Methane pyrolysis carbon allocated to durable products may not simultaneously be counted as soil restoration or permanent storage. Hydraulic and thermal input values should be treated as model assumptions until validated (7,10–12).')
 heading(d,'S11. Grid Harvester and marine logistics',2)
 para(d,'The conceptual Grid Harvester is retained in Fig. S1 side/plan diagrams and the Grid Harvester energy chart. At 10% slurry solids with a faired hose, a source energy screen reports 33.9 MJ per 1.44-ha harvest cycle against a 90.9 MJ conventional comparison, an illustrative 62.7% decrease in harvesting energy. This is NOT an HTL biocrude conversion-efficiency gain nor a demonstrated commercial field test. Seaweed farming yield, moorings, nautical safety and environmental permits remain external validation requirements (13–17).')
 heading(d,'S12. Community heat reuse, aquaculture, algae and farming',2)
 para(d,'Greenhouse crops, recirculating aquaculture systems, optional Asparagopsis feed supplements, biomass drying and recovered low-grade heat are retained as separately accounted community resources. Their scale and revenue assumptions were developed in the earlier model and are available in us2_inputs.py, us6_nutrient_balance.py and us7_community_screen.py. They are not credited against the primary U.S. transport system without specified supply and demand boundaries.')
 heading(d,'S13. Reactor learning and deployment constraints',2)
 para(d,'The inherited iterative reactor-learning approximation can select around 184 hubs in the AEO service central case. A bounded search shows a mathematical cost minimum at much higher unit counts conditional on fleet learning. The model does not demonstrate delivery of thousands of modules within the stated calendar, nor hourly balancing or completed siting and permitting. Fixed 0, 30, 60, 100, 184, 250 and 945-hub screens are retained for interpretation.')
 heading(d,'S14. Reproducibility, figure catalog and uncertainty in interpretation',2)
 para(d,'Code: run RUN_V97_VALIDATION.bat on Windows or python us97_validate.py --full on any compatible Python environment. Required packages: scipy, numpy, matplotlib, python-docx and pillow. The script verifies SHA-256 of source AEO files; the v9.7 source row mapping; the multi-feedstock NPK and carbon conservation; paired uncertainty input and outputs; and 600-dpi TIFF encoding. Supplementary figures include all legacy technical map and reactor-network diagnostics as separate TIFFs and the four V9.7 circular-system analyses. Historical intermediate scenario outputs are retained but not to be confused with the version 9.7 central results.')
 para(d,'Technical supplemental figure files (individual TIFFs in the flat archive):')
 for i,x in enumerate(SFIG,34):para(d,f'Fig. S{i}. {x.replace("_", " ").replace(".tif", "")}.')
 para(d,'Additional archived technical figures retained include Grid Harvester views and cycle-energy chart; offshore and seaweed species maps; fuel transition; reactor cost and learning; transport map; crop nutrient and soil-return diagrams; RAS and farming emissions. Each has a separate, source-identified TIFF file. Their previous labels are not the five main Science display items.')
 out=R/'Supplementary_Materials_V9.7_Science.docx';d.save(out); print('supp saved',len(d.paragraphs),'paras',len(d.tables),'tables');return out

def cover():
 d=docsetup(Document());heading(d,'Cover letter — Science (AAAS)',1)
 para(d,'Dear Science Editors,')
 para(d,f'Please consider the Research Article “{T}” for publication in Science.')
 para(d,'This national screening study integrates a 2050 transport-fleet counterfactual already incorporating electric vehicles with a constrained fuel-production optimization. It compares petroleum-free energy pathways against AEO2026 vehicle stocks and purchase prices, and explicitly tests land-biomass residue removal, hydrothermal liquefaction, treated nitrogen–phosphorus–potassium returns and stable-carbon amendments. The selected 166-Mt crop-residue ceiling, its category-specific dispatch, and quantified fertilizer imports provide a falsifiable environmental and economic result rather than assuming that crop waste or fertilizer coproducts are free.')
 para(d,f'Under one source-stock-weighted vehicle-cost screen, the conditional 2050 alternative with crop and soil constraints costs ${C["annual_cost_bn"]:.1f} billion/year versus a ${REF:.1f} billion/year partial reference, or about ${CPT:.0f} per tonne of CO₂e avoided under the defined scope. The conclusions neither claim lower costs across all 2050 scenarios nor imply verified national life-cycle greenhouse gas accounting. Independent reference hydrogen-production emissions, BEV financing and restricted reactor deployment are explicit sensitivities.')
 para(d,'The attached submission set consists of five main TIFF figures at 600 dpi, manuscript and technical supplement, with a version-matched supporting research archive including model source, AEO2026 workbooks, hashes, 500-draw sensitivity outputs, and field-nutrient accounting tables. All new scientific charts are generated reproducibly with Python, not synthetic or illustrative estimates of measurements.')
 para(d,'Artificial Inventor / Synthetic Scientist V63 assisted with code, manuscript and figure preparation. The authors take responsibility for the analysis and will provide additional AI-use records as required by editorial policy. The corresponding author reports commercial and intellectual-property interests in related infrastructure; those disclosures appear in the manuscript.')
 para(d,'The manuscript is offered for consideration as original research and is not under concurrent consideration at another journal.')
 para(d,'Sincerely,\nJonathan Karl Bily\nCorresponding author\njonathan@cloudwashlaundry.com')
 f=R/'Cover_Letter_Science_V9.7.docx';d.save(f);return f

def titlepage():
 d=docsetup(Document());heading(d,'Author and affiliation information',1)
 para(d,T,bold=True)
 para(d,'Jonathan Karl Bily¹*, Christoph Pahl², Patricia Valdés Bacallao³')
 para(d,'¹ Independent Researcher, Spain\n² Technical University of Munich, Munich, Germany\n³ University of Málaga, Málaga, Spain')
 para(d,'* Corresponding author: jonathan@cloudwashlaundry.com\nORCID: 0009-0004-3526-7271')
 para(d,'Funding: None reported. Competing interests and author contributions: see manuscript; author and coauthor confirmation required before upload.')
 f=R/'Title_Page_V9.7_Science.docx';d.save(f);return f
if __name__=='__main__':
 main_document();supplemental();cover();titlepage()
 print('Main abstract words:',len(abs_text.split()))
