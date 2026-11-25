# BT23 V9.10: official export instructions and evidence gate

## Uploaded evidence status

`BT23_EXPORTS.zip` (SHA-256 `b8c1673ea90403e9e1f4ec76d75c6dae48e721aec1145b4ead1ac580b16f2246`) contains only the directory entry `BT23_EXPORTS/`. It has **0 data files and 0 county records**. No BT23 regional supply is incorporated in V9.10. The numerical national residue ceilings continue to be **analyst assumptions**, not observed USDA/DOE county volumes.

## Once ORNL approves your account

Official portal: https://bioenergykdf.ornl.gov/bt23-agricultural-download

1. Sign in and open the agricultural download page. Select agricultural **residues** (not energy crops). Export the **mature-market medium** scenario for the **entire United States, all applicable counties, all residue resources and all offered farmgate price levels**. Export CSV, not a screenshot, HTML page, directory name or empty ZIP. The server may create multiple CSV exports by price/resource.
2. Save all actual downloaded `.csv` files together in `BT23_EXPORTS` alongside the provided scripts. Retain the original raw files and units (`dt` = U.S. dry short tons); do not reformat them in Excel.
3. Double-click `RUN_V910_CHECK_BT23_EXPORT.bat` to inventory the files. It will tell you if you still have an empty ZIP.
4. From Command Prompt in the extracted folder, run `py -3 us910_bt23_evidence_gate.py --validate BT23_EXPORTS --attest-all-states-prices` **only after you verified** that your downloads include all states, counties and offered-price levels. Without this explicit attestation the tool will not label the export a national candidate.
5. To integrate the actual official tiers into the national model, run `py -3 us910_bt23_evidence_gate.py --model BT23_EXPORTS --attest-all-states-prices`. This replaces the analyst feedstock capacities with source-labelled marginal supply tiers. It does **not** automatically validate delivery distances, soil chemistry or field-level removal rates.
6. The tool automatically creates `BT23_OFFICIAL_COUNTY_EXPORT_FOR_V910.zip` (original CSV bytes plus audit/status). Attach that ONE ZIP here. If national coverage or required columns fail, send the diagnostic status file instead; no invented replacements are required.

USDA NASS Quick Stats also supports county-area cross-checks using a **free, separate API key**: https://quickstats.nass.usda.gov/api/. The included `RUN_USDA_COUNTY_DATA.bat` performs that query if a key is supplied. Harvested acres are not themselves sustainable residue volumes.

## Important scientific restrictions

The ORNL download portal identifies offered *farmgate* prices in dry U.S. short tons. These differ from delivered metric-ton costs; logistics, moisture, storage, plant siting and competing uses remain required assumptions. The importer differences cumulative county prices into **marginal increments**, detects duplicate county/feedstock/scenario/price keys, requires explicit units, rejects a partial archive as national evidence, and explicitly excludes unstated food-processing residue quantities and double-counted corn-husk fractions.

The batch files never bypass authentication. This package remains a conditional model until actual, national source data are loaded and verified.

**Permanent Grid Harvester inclusion:** Fig. S1 schematic, Fig. S22 efficiency chart, `grid_harvester.py`, and `us91_grid_harvester_efficiency.csv` are mandatory and image-matched by validation. The faired-hose/10%-solids scenario reduces calculated *harvesting-cycle energy* from 90.9 to 33.9 MJ (62.7%) per reference 1.44-ha cycle; no HTL conversion efficiency claim is made.
