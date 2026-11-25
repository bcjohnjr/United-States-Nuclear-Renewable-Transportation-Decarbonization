#!/usr/bin/env python3
"""V9.10 evidence-gate editorial update, preserving V9.9 numerical baseline and embedded Grid Harvester figures.

DO NOT regenerate or rename a V9.9 numeric result as empirical BT23 validation.
"""
from pathlib import Path
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
R=Path(__file__).resolve().parent
STEMS=['Research_Article','Supplementary_Materials','Cover_Letter','Title_Page']
FILES={
 'article':('Research_Article_V9.9_Science.docx','Research_Article_V9.10_Science.docx'),
 'supp':('Supplementary_Materials_V9.9_Science.docx','Supplementary_Materials_V9.10_Science.docx'),
 'letter':('Cover_Letter_Science_V9.9.docx','Cover_Letter_Science_V9.10.docx'),
 'title':('Title_Page_V9.9_Science.docx','Title_Page_V9.10_Science.docx'),
}


def run():
 a=Document(R/FILES['article'][0]);
 for p in a.paragraphs:
  if p.text.startswith('We solved the national annual energy and material system using a SciPy/HiGHS-based model'):
   p.text=('We solved an annual national energy and material optimisation with the archived AEO2026 reference workbooks, SciPy/HiGHS and published code. The candidate crop category caps and regional transport costs remain analyst assumptions. A fail-closed county importer can replace these caps only upon receipt and verification of the official ORNL BT23 resource/price data, an explicit all-states/all-prices export attestation and a source-coverage audit. The only user-provided BT23 archive contained no data records and was not imported. The agricultural lifecycle boundary is a conditional explicit-process substitution screen, not a completed national lifecycle assessment.')
  elif p.text.startswith('Data and materials availability:'):
   p.text=('Data and materials availability: Versioned Python files, source-linked AEO2026 workbooks, archived outputs and a fail-closed ORNL BT23 county resource importer are supplied with the research package. No validated national county BT23 export was available; the resource distribution and national crop totals are therefore unverified assumptions. A version-matched public repository release and DOI have not been confirmed.')
  elif p.text.startswith('Conditional crop-residue economics survive more restrictive nutrient and soil assumptions'):
   p.text=('Conditional crop-residue economics remain favourable against the matched no-crop alternative within the specified assumptions. The geographic distribution and collection eligibility of residual biomass, nutrient plant availability, long-run soil-carbon persistence and a fully comparable national lifecycle emissions boundary have not been established. These are limitations on interpreting the model, not proof of national implementation readiness.')
 a.save(R/FILES['article'][1])

 s=Document(R/FILES['supp'][0]);
 title=a.paragraphs[0].text
 for p in s.paragraphs:
  if p.text.startswith('Supplementary Materials — V9.9:'):
   p.text='Supplementary Materials — V9.10: agricultural evidence gate, plant-available nutrient balances, soil carbon and Grid Harvester'
  elif p.text.startswith('Companion to:'):
   p.text='Companion to: '+title
  elif p.text.startswith('S9. 500-draw joint uncertainty'):
   p.text='S9. Paired uncertainty: current 150 draws versus historical 500-draw diagnostics'
  elif p.text.startswith('A 500-draw paired simulation samples'):
   p.text=('The historical V9.8 500-draw Monte Carlo is retained as a labelled archive diagnostic. The V9.9 and V9.10 current central analyses use 150 paired screening draws with per-draw plant-available nutrient balances, soil-restoration land constraints and agricultural emissions substitution. These are analyst-selected parameter ranges, not calibrated future probability distributions. Earlier numerical results must not be pooled with the revised boundary.')
  elif p.text.startswith('Run RUN_V99_VALIDATION.bat'):
   p.text=('Use RUN_V910_VALIDATION.bat on Windows or RUN_V910_VALIDATION.sh on Linux for current evidence-gate, document and mandatory Grid Harvester checks. For a complete recalculation use the --full option. Historic V9.8/V9.9 files remain source references only, and their conclusions are not substituted for present model outputs.')
 # Add an explicit country-data and source-provenance section. No fictitious data or numeric result.
 s.add_heading('S26. ORNL BT23 county-source completeness and transfer to the optimisation',level=2)
 s.add_paragraph('The user-supplied BT23_EXPORTS.zip contained a single directory entry and no CSV records. The V9.10 evidence gate therefore rejects this source and does not replace the analyst crop capacities. A Python/BAT intake tool records the original archive SHA-256, counts rows, validates explicit dry mass units and county FIPS, rejects duplicate county–resource–scenario–offered-price keys, and checks cumulative supply monotonicity and multi-price coverage. Country-wide completeness cannot be inferred from a county-count threshold alone; the portal filters must also be attested by the person downloading the data.')
 s.add_paragraph('When full source exports are provided, the existing model crosswalk differences successive cumulative offered-price records to create marginal state/resource/price tiers and charges separately for farmgate biomass, transport/storage, treatment, nutrients and soil services. Processing residues outside the agricultural BT23 field taxonomy are not automatically added to its national crop total. County-level supply does not itself establish project siting, soil erosivity, field accessibility or delivered transport logistics.')
 s.add_paragraph('The ORNL source is https://bioenergykdf.ornl.gov/bt23-agricultural-download ; the USDA NASS Quick Stats county acreage cross-check is https://quickstats.nass.usda.gov/api/. Both are distinct from the EIA AEO2026 transport-service dataset. The current model conclusions and Grid Harvester calculations do not depend on an invented county file.')
 s.save(R/FILES['supp'][1])

 l=Document(R/FILES['letter'][0]);
 for p in l.paragraphs:
  if p.text.startswith('The complete technical archive'):
   p.text=('The research archive provides the original AEO2026 data, model and validation source code, the full technical supplement, and mandatory Grid Harvester engineering figures S1 and S22. County-level BT23 data have not been certified for national modelling; the associated importer and source-acquisition procedure are provided so the key empirical resource test can be completed when official access becomes available.')
  elif p.text.startswith('Artificial Inventor / Synthetic Scientist V63'):
   p.text=('Artificial Inventor / Synthetic Scientist V63 assisted with drafting and computational code preparation. Authors remain responsible for verification, artwork provenance, and accurate AI-use disclosure and supporting records required by the journal. No unavailable prompt history is represented here as complete.')
 l.save(R/FILES['letter'][1])
 t=Document(R/FILES['title'][0]);t.save(R/FILES['title'][1])
 for label,(_,dest) in FILES.items():
  d=Document(R/dest)
  print(label, dest,'paragraphs',len(d.paragraphs),'figures',len(d.inline_shapes))
if __name__=='__main__':run()
