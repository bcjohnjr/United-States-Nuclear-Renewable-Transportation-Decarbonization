#!/usr/bin/env python3
"""Build V9.6 journal-targeted submission drafts from V9.5, preserving citations/figures."""
import re,json
from pathlib import Path
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
HERE=Path(__file__).resolve().parent
R=json.loads((HERE/'US96_Shared_2050_Screen.json').read_text())['results']
low,cen,high=R
TITLE='Prospective petroleum-free U.S. transport in 2050: an AEO2026-grounded cost, carbon and resource screen'
ABSTRACT=(
'National petroleum-free transport pathways are evaluated against a partially electrified 2050 reference from the U.S. Energy Information Administration’s Annual Energy Outlook 2026 (AEO2026). '
'A linear energy-system optimisation combines vehicle electrification, hydrogen, reactor heat, renewable liquids, and constrained agricultural residues. '
'Using AEO2026 travel and fleet stocks, the proposed system costs US$'+f"{cen['alt_screen_bn']:.0f}"+' billion per year under central shared vehicle-price assumptions, compared with a reconstructed reference of US$'+f"{cen['reference_screen_bn']:.0f}"+' billion. '
'Across three explicitly conditional cost and lifecycle screens, the additional cost is US$'+f"{low['cost_per_tonne_avoided_usd']:.0f}"+'–'+f"{high['cost_per_tonne_avoided_usd']:.0f}"+' per tonne CO₂e avoided, with approximately 1.2–1.5 Gt CO₂e of annual mitigation under partial well-to-wheel boundaries. '
'The reference includes AEO energy expenditure and modelled differential vehicle costs; tax treatment, maintenance, missing modes, lifecycle coefficients, biomass sustainability and reactor deployment remain uncertain. '
'A bounded reactor-cost search and nitrogen–phosphorus–potassium balance identify constraints that annual least-cost results alone cannot establish. '
'The calculations are conditional technology screens rather than forecasts of national implementation.'
)

def assign(par,text):
 par.text=text
 return par

def match(d,txt):
 for p in d.paragraphs:
  if txt.lower() in p.text.lower():return p
 raise KeyError(txt)

def keep_table(table):
 table.autofit=True
 table.alignment=WD_TABLE_ALIGNMENT.CENTER
 for row in table.rows:
  for c in row.cells:
   c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
   for p in c.paragraphs:
    p.paragraph_format.space_after=Pt(2)
    for run in p.runs:run.font.size=Pt(8.5)
   tcPr=c._tc.get_or_add_tcPr()
   shade=OxmlElement('w:shd')
   if row==table.rows[0]:shade.set(qn('w:fill'),'EAF0F2');tcPr.append(shade)

def add_para_before(target,text,style='Body Text'):
 p=target.insert_paragraph_before(text,style=style.replace(' ','') if style.startswith('Heading ') else style)
 p.paragraph_format.space_after=Pt(5)
 return p

m=Document(HERE/'SOURCE_MASTER_Research_Article_V9.5.docx')
assign(m.paragraphs[0],TITLE)
assign(match(m,'One-sentence summary:'),'One-sentence summary: Accounting for AEO2026’s already-electrified fleet, shared vehicle purchase costs and energy-boundary choices turns the earlier historical-price saving into a conditional positive decarbonisation cost.')
assign(match(m,'We investigate a petroleum-free'),ABSTRACT)
assign(match(m,'The U.S. Energy Information Administration’s Annual Energy Outlook 2026'),
'AEO2026 projects a partially electrified 2050 vehicle fleet, and therefore provides a different economic counterfactual from a petroleum-only fleet at historical prices (13). We use its original tables for activity, vehicle stock, new-vehicle prices, energy expenditure and direct transport CO₂; the remaining gaps are explicitly represented as modelling choices.')
assign(match(m,'EIA Table 3 reports US$411.5 billion'),
'EIA Table 3 reports US$411.5 billion in 2050 transportation energy expenditures (2025 dollars); Table 70 reports 1,334.3 Mt of direct energy-related transport CO₂. These quantities are not equivalent to annualised alternative infrastructure costs and partial well-to-wheel emissions. In addition to the original assumption screens (Fig. 6), we construct a more consistent BEV vehicle-price comparison using AEO2026 Table 52, accounting for differential purchase costs on both sides (Fig. 7; Table 2).')
assign(match(m,'Anchoring energy expenditure to EIA’s US$411.5 billion'),
'A simple fuel-only counterfactual understates the importance of powertrain stock, taxes and capital. The earlier partial EIA cost bridge ranged from US$432.9 billion to US$572.6 billion per year using separately assumed addenda (Fig. 6). The new V9.6 shared-assumption calculation supersedes those ranges as the principal conditional comparison: EIA Table 52 new-car prices inform BEV annual ownership premiums on both sides, and the 2050 fleet stocks are from Tables 39 and 49. Its three bounded cases and exclusions are in Table 2 and Supplementary Text S33.')
assign(match(m,'AEO reports 1334.2 Mt/year of direct transport CO₂'),
'AEO2026 reports 1,334.25 Mt/year of direct transportation CO₂. With assumed 5–15 g CO₂e/MJ upstream fossil emissions and 10–100 g CO₂e/kWh electricity lifecycle intensities, the partial reference spans 1,436–1,699 Mt CO₂e/year. The AEO-service petroleum-free model reports about 216.3 Mt CO₂e/year under its pathway assumptions. The resulting 1.22–1.48 Gt/year avoided is conditional, not a harmonised complete lifecycle assessment; indirect land-use change and embodied vehicle, reactor and network emissions remain incomplete.')
assign(match(m,'In 1,000 joint draws using analyst-defined'),
'The earlier 1,000-draw screen has a median US$179 billion alternative-minus-reference annual gap under separately specified addenda (5th–95th percentile US$59–315 billion). The new shared BEV-price comparison supplies three independently reproducible deterministic cases; neither the earlier draws nor the new cases are predictive probabilities. Oil prices, fleet mix and physical technology availability remain material sources of uncertainty (Fig. 7; fig. S33).')
# Retain discussion but introduce principal conclusion.
assign(match(m,'The least-cost configuration is conditional'),
'The AEO2026-counterfactual analysis no longer supports a claim of universally cheaper transport. Across the three explicit source-derived vehicle-price and analyst-defined tax, lifetime, maintenance and lifecycle screens, the petroleum-free alternative is US$78.8–265.3 billion/year more expensive. The central case is US$175.0 billion/year, or about US$130 per tonne of partially modelled CO₂e avoided. These are not official EIA whole-system forecasts; the quantities must be treated as decision-screening ranges. The system retains substantial emissions-reduction potential but requires technology, logistics and capital assumptions that are not validated at national deployment scale.')
assign(match(m,'AEO2026 service growth, vehicle capital'),
'AEO2026 service, vehicle size and powertrain-cost choices materially affect the result. Charging the same EIA-derived annual BEV purchase-price premium to both the already-electrified reference and the proposed 95%-BEV alternative avoids treating the reference as though it had no electric vehicles. However, class weights, maintenance, tax incidence, construction limits and financing remain model inputs. The integrated nuclear/biofuel system therefore offers an assessment of trade-offs and conditions for economic competitiveness, rather than a validated national minimum.')
assign(match(m,'For the AEO2026 bridge, official Counterfactual Baseline'),
'We ingest AEO2026 Counterfactual Baseline Tables 3, 7, 12, 36, 39, 49, 52 and 70 from checksum-verified spreadsheets. Activity is translated into 2050 service factors; vehicle purchase-price differences are calculated across four illustrative classes (compact, midsize, small crossover, large pickup), using explicitly assumed class weights of 25%, 25%, 30%, and 20%. In three cases, BEV capital-premium annualisation uses 12–18-year vehicle life and US$100–350/year maintenance savings. The identical resulting BEV premium is applied to the reference stock and the alternative fleet. Fuel tax transfer removal, charging and missing-mode adjustments are quantified separately; these do not constitute a complete NEMS-equivalent cost simulation (Supplementary Text S33).')
assign(match(m,'Independent reruns use the model source'),
'All numerical results in this submission use the accompanying version-matched Python source, a checksum-verified archive of 38 AEO2026 source workbooks and generated CSV/JSON outputs. The code includes tests for the heavy-truck MJ/kWh conversion, cost accounting, AEO fleet stock, three reference-cost screens, emitted greenhouse gases, crop balances and TIFF metadata. The public repository is given below; until it is updated to this version, the accompanying research package—not the older public files—is the reproducibility record.')
assign(match(m,'Model code, parameter files, the 38 EIA source workbooks'),
'Data and materials availability: The accompanying V9.6 reproducibility archive contains the complete model source, source-data workbooks, SHA-256 manifest, assumptions, scenario outputs, all comparison scripts and figure sources. The public project repository is https://github.com/bcjohnjr/United-States-Nuclear-Renewable-Transportation-Decarbonization. The public branch and DOI must match the exact V9.6 archive before submission; an unverified DOI is not asserted.')
assign(match(m,'Supplementary Text S1–S32'),
'Supplementary Text S1–S34, Figs. S1–S33, and Tables S1–S21. Seven main figures, 33 supplementary figures and the original additional technical maps are provided as 600-dpi RGB TIFF files, with complete software and archived EIA data.')
# insert new Results section before 'Hydrogen supply' heading
anchor=match(m,'Hydrogen supply after natural-gas constraints')
add_para_before(anchor,'AEO2026 shared-assumption incremental cost and carbon screen','Heading 3')
add_para_before(anchor,
  f'The shared vehicle-price screen uses AEO2026 Table 52 new-vehicle prices and Table 39 stocks, with the same BEV net annual cost applied to the AEO reference and 95%-BEV alternative. The lower, central and higher cases give reference costs of US${low["reference_screen_bn"]:.1f}, US${cen["reference_screen_bn"]:.1f} and US${high["reference_screen_bn"]:.1f} billion/year. Corresponding alternative costs are US${low["alt_screen_bn"]:.1f}, US${cen["alt_screen_bn"]:.1f} and US${high["alt_screen_bn"]:.1f} billion/year, respectively. The incremental costs are positive in all three screened cases. All prices are placed on an assumed 2026-dollar basis; EIA Table 3 alone is not a full ownership-cost forecast (Fig. 7; Table 2).',
  'First Paragraph')
add_para_before(anchor,
  f'Using the partial reference well-to-wheel emissions boundary, these scenarios yield US${low["cost_per_tonne_avoided_usd"]:.0f}–{high["cost_per_tonne_avoided_usd"]:.0f}/t CO₂e avoided, with a central value of US${cen["cost_per_tonne_avoided_usd"]:.0f}/t. The 0–250-hub build restriction, when treated as a mathematical fleet cap, provides a check on the low-cost assumption; 945 hubs or 3,780 reactor modules is a far more speculative unconstrained learning case (fig. S32). These results cannot establish hourly reliability or complete lifecycle performance. The source rows, formulae, taxes and assumed adjustments are provided in Supplementary Text S33–S34 and Table S20–S21.',
  'Body Text')

# add Table 2 by moving generated table and caption before Hydrogen heading
caption=m.add_paragraph('Table 2. AEO2026 shared-parameter annual 2050 screening scenarios. Expenditures are US$ billion/year; tax, vehicle turnover, maintenance, infrastructure and emissions boundaries remain conditional.',style='Body Text')
t=m.add_table(rows=1,cols=6)
for i,x in enumerate(['Case','Reference','Alternative','Difference','Avoided Mt CO₂e','US$/t CO₂e']):t.rows[0].cells[i].text=x
for r in R:
 row=t.add_row().cells
 data=[r['case'].replace('_',' '),f"{r['reference_screen_bn']:.1f}",f"{r['alt_screen_bn']:.1f}",f"+{r['incremental_alt_minus_reference_bn']:.1f}",f"{r['avoided_mt']:.0f}",f"+{r['cost_per_tonne_avoided_usd']:.0f}"]
 for i,x in enumerate(data):row[i].text=x
keep_table(t)
anchor._p.addprevious(caption._p);anchor._p.addprevious(t._tbl)
# figures section append Fig7 with a compact inline render
fpar=m.add_paragraph('Fig. 7. Shared-parameter AEO2026 2050 screening costs (A) and conditional avoided-emissions costs (B). EIA vehicle prices inform both fleets; class mix, maintenance, taxes, reference scope and emissions intensities are assumptions. The bars are not official EIA national total-cost forecasts. File: Fig7_AEO2026_Shared_2050_Cost_Abatement.tif.',style='Body Text')
fig=p= m.add_paragraph()
fig.alignment=WD_ALIGN_PARAGRAPH.CENTER
fig.add_run().add_picture(str(HERE/'Fig7_AEO2026_Shared_2050_Cost_Abatement.tif'),width=Inches(6.5))
# ensure end figure after other labels (appends there)
m.save(HERE/'Research_Article_V9.6.docx')

s=Document(HERE/'SOURCE_MASTER_Supplementary_Materials_V9.5.docx')
assign(s.paragraphs[0],'Supplementary Materials — AEO2026-grounded U.S. transport cost, carbon, reactor-learning and soil-nutrient screens (V9.6)')
# section S6 was absent in V9.5; restore explanatory text before S7
before=match(s,'S7. Offshore seaweed')
add_para_before(before,'S6. Land-biomass supply, conversion and field-removal constraints','Heading 2')
add_para_before(before,'The base model contains two combined crop-and-forest residue tiers (200 and 150 Mt dry/year) and 200 Mt of perennial grass/energy-cane potential; these are assumed available quantities, not verified field-specific resource entitlements. The separate constrained experiment uses at most 166 Mt of recoverable food-crop residues, an independently assumed 150-Mt non-crop tier, HTL treatment costs, elemental nitrogen, phosphorus and potassium replacement and stable-carbon return. Model comparisons must keep these feedstock boundaries separate to avoid double counting (SR26; U.S. DOE 2023 Billion-Ton Report).','Body Text')
anchor=match(s,'Supplementary Tables (S1–S19)')
add_para_before(anchor,'S33. Shared powertrain-premium and 2050 reference-cost construction','Heading 2')
add_para_before(anchor,
 f'AEO2026 Table 52 provides 2050 new-price values by powertrain and size class. A deliberately illustrative 4-class sample uses class weights 25% compact, 25% midsize, 30% small-crossover and 20% large pickup; these are analyst weights, NOT the EIA sales-weighted mix. The price vector and all 38 source-workbook SHA-256s are archived. The selected representative 2050 new gasoline vehicle averages US${json.loads((HERE/"US96_Shared_2050_Screen.json").read_text())["vehicle_prices_2025usd_thousands"]["ice"]:.1f} thousand in 2025 dollars. The BEV 200-mile/300-mile share, purchase-price annualisation (12, 15 or 18 years) and maintenance allowance (US$100–350/year) are explicitly varied. Applying each resulting common BEV net premium to the 154.44-million AEO2026 BEVs and to the alternative 95%-BEV fleet prevents an erroneous zero-BEV reference. Hybrid and plug-in-hybrid premiums use the same class sample. Reference charging, historical-style gasoline and diesel excise transfers, non-energy offroad scope and price-year assumptions remain independently stated. Modelled alternative supply, net vehicle premiums, electric roads and conversion plants are included only once. The V9.6 CSV and source code show every equation (fig. S33 and table S20).','Body Text')
add_para_before(anchor,
 'This calculation does not claim that Table 52 new-vehicle prices are observed annual ownership costs or that EIA Table 3 transportation energy spending contains all national vehicle or infrastructure expenditure. Common conventional-vehicle base purchase and maintenance costs are excluded from both sides; net powertrain differences are annualised. Vehicles and services outside the selected classes, embodied energy, vehicle financing and class-specific deployment remain limitations. The three bounded cases are not calibrated real-world probabilities.','Body Text')
add_para_before(anchor,'S34. Reactor deployment limits and lifecycle-emissions denominators','Heading 2')
add_para_before(anchor,
 'The source model’s endogenous fleet learning is non-convex. We solve selected fixed hub counts of 0, 30, 60, 100, 150, 184, 200, 250, 300, 500, 800 and 945 with a fleet-average capital curve conditional on that count. This is a deployment constraint sensitivity rather than an hourly-feasible network or construction schedule. Four modules are assumed per hub. The primary iterative configuration is about 184 hubs in the AEO-service case; 945 hubs would require 3,780 modules, an implausibly high deployment burden absent evidence of manufacturing, licensing and siting capability.','Body Text')
add_para_before(anchor,
 'The emissions reference starts from AEO Table 70 direct transportation CO₂ of 1,334.25 Mt/year. Upstream fuel extraction and processing and electricity emissions are approximated with 5–15 g CO₂e/MJ and 10–100 g CO₂e/kWh on disaggregated Table 36 fuels. The calculated reference range is 1,436–1,699 Mt CO₂e/year; the corresponding alternative’s reported partial WTW emissions are 216.3 Mt/year. The model does not fully harmonise indirect land-use change, fertilizer production, vehicle/construction embodiment, international transport and refinery emissions. Hence divided incremental costs are labelled partial-screening US$/t CO₂e, not an audited lifecycle mitigation cost.','Body Text')
assign(anchor,'Supplementary Tables (S1–S21)')
# Append two additional tables at the end with self-contained captions. Tables 1-19 remain untouched.
s.add_paragraph('Table S20. Shared-parameter 2050 AEO cost and emissions screen. Dollar values are annual 2026-basis model screens, not EIA total-cost forecasts.',style='Body Text')
t=s.add_table(rows=1,cols=8)
for i,v in enumerate(['Case','BEV premium $/yr','Ref $bn','Alt $bn','Delta $bn','Ref WTW Mt','Alt WTW Mt','$/t']):t.rows[0].cells[i].text=v
for r in R:
 row=t.add_row().cells
 values=[r['case'],f"{r['bev_cost_net_usd_yr_2026usd']:.0f}",f"{r['reference_screen_bn']:.1f}",f"{r['alt_screen_bn']:.1f}",f"{r['incremental_alt_minus_reference_bn']:.1f}",f"{r['reference_partial_wtw_mt']:.0f}",f"{r['alt_model_wtw_mt']:.1f}",f"{r['cost_per_tonne_avoided_usd']:.0f}"]
 for i,v in enumerate(values):row[i].text=v
keep_table(t)
s.add_paragraph('Table S21. Selected reactor-deployment limits for central price assumptions, without hourly feasibility or construction-rate verification.',style='Body Text')
import csv
rows=[r for r in csv.DictReader(open(HERE/'us96_deployment_stress.csv')) if int(r['hubs']) in (0,60,184,250,945)]
t=s.add_table(rows=1,cols=4)
for i,v in enumerate(['Hubs','Modules','Cost $bn/year','WTW Mt CO₂e/year']):t.rows[0].cells[i].text=v
for r in rows:
 cells=t.add_row().cells
 for i,v in enumerate([r['hubs'],r['modules'],f"{float(r['annual_cost_bn']):.1f}",f"{float(r['alternative_emissions_mt']):.1f}"]):cells[i].text=v
keep_table(t)
s.add_paragraph('Fig. S32. Alternative cost sensitivity to selected fixed reactor-hub counts, under the V9.6 central 2050 vehicle-price screen. Green area denotes an illustrative cap of 250 hubs, not an approved build schedule. File: FigS32_Reactor_Deployment_Cost_Constraint.tif.',style='Body Text')
s.add_paragraph('Fig. S33. Reference-cost components and assumptions for the V9.6 central case. Tax transfer removal is negative; technology and missing-scope additions are positive. The components are not a complete national TCO. File: FigS33_AEO_Reference_Boundary_Components.tif.',style='Body Text')
s.save(HERE/'Supplementary_Materials_V9.6.docx')

# RSC-specific cover letter (not falsely claiming public release or coauthor approval).
c=Document(); sec=c.sections[0];sec.top_margin=Inches(.8);sec.bottom_margin=Inches(.8)
c.add_heading('Submission cover letter — Sustainable Energy & Fuels',0)
c.add_paragraph('Dear Editor,')
c.add_paragraph('Please consider the Full Paper “'+TITLE+'” for publication in Sustainable Energy & Fuels.')
c.add_paragraph('Using original AEO2026 transport-fleet, fuel and vehicle-price tables, this study evaluates an integrated United States petroleum-free transport pathway, including electrification, hydrogen, high-temperature reactor heat, sustainable liquids and treatment of crop residues with soil nutrient replacement. The central conditional 2050 economic screen reports approximately US$660 billion/year for the alternative versus US$485 billion/year for a reconstructed reference, with a partial-lifecycle abatement cost near US$130 per tonne CO₂e avoided. Three explicit shared-vehicle-cost cases span approximately US$65–179 per tonne. We do not present these as official EIA total-system forecasts or as a fully harmonised life-cycle result.')
c.add_paragraph('The new contribution is a reproducible, whole-system resource and cost comparison with common 2050 BEV purchase-cost assumptions on both sides, and explicit constraints for crop residue collection, nitrogen–phosphorus–potassium replacement, reactor fleet learning and high-energy offshore harvesting. Engineering designs and agricultural returns are screening concepts, not commercial operating records.')
c.add_paragraph('A research archive accompanies this manuscript with the original 38 AEO2026 workbooks, verification hashes, source code, reported numerical outputs, sensitivity calculations and independent 600-dpi TIFF figures. All figures provided are programmatically rendered from the model and source series. The corresponding public project repository will be matched to the final submitted revision; a public DOI is not asserted in advance of deposit.')
c.add_paragraph('Artificial Inventor / Synthetic Scientist V63 assisted with code development, manuscript writing and figure plotting. The authors take responsibility for the numerical assumptions and statements. The manuscript includes a funding, potential competing-interests and AI-use disclosure for final author approval in accordance with journal policies.')
c.add_paragraph('This research has not been published previously. The authors intend to select the traditional subscription publication route.')
c.add_paragraph('Sincerely,')
c.add_paragraph('Jonathan Karl Bily\nCorresponding author\njonathan@cloudwashlaundry.com')
c.save(HERE/'Cover_Letter_Sustainable_Energy_Fuels_V9.6.docx')

toc=Document();toc.add_heading('Table-of-contents entry',0)
toc.add_paragraph('Reconstructing the partly electrified 2050 U.S. reference shows that petroleum-free transport has substantial mitigation potential but positive conditional abatement costs, with biomass and reactor deployment limits essential to the result.')
toc.add_picture(str(HERE/'TOC_2050_Transport_Cost_Screen.tif'),width=Inches(3.14))
toc.save(HERE/'TOC_Entry_V9.6.docx')
print('Abstract words',len(ABSTRACT.split()))
print('Created manuscript and supplement')
