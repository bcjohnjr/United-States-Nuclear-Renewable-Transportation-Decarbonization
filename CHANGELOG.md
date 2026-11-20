# v8.2 — 20 November 2026 (submission package)

- Authors and contact: Jonathan Karl Bily (corresponding; jonathan@cloudwashlaundry.com), Cloud Wash Laundry Corporation, Teruel, Spain; Dr. Christoph Pahl, Technical University of Munich, Munich, Germany; Patricia Valdes Bacallao, University of Málaga, Málaga, Spain.
- Data availability now gives the public repository (https://github.com/bcjohnjr/United-States-Nuclear-Renewable-Transportation-Decarbonization, release v8.2) instead of the v8.0 ZIP name.
- Manuscript reframed around the transport result (new title and abstract). Restored content dropped in v8.1: Monte Carlo shares cheaper than petroleum (96.2/83.5/33.3%), Spearman sensitivities, natural-gas depletion and supply extensions, post-gas steam electrolysis and its decomposition, fuel supply (once-through vs closed cycle, thorium, start-up plutonium) and sustainable-fission results. Table 1 expanded to ten cases. Food and nutrient results kept as a shorter section.
- Supplementary materials rebuilt: S1–S18, Tables S1–S7, Figs. S1–S17 (every figure now explained in the text).
- References: authors and full details added for refs. 18, 35–37, 47–49; ref. 23 authors corrected (D. S. Wendt, L. T. Knighton, R. D. Boardman); ref. 47 verified (Vlaicu et al., Appl. Sci. 16, 11139); refs. 51–55 added (Potential Gas Committee, Canada Energy Regulator, EIA RECS, NREL biogas, NEA/IAEA Uranium 2024).
- Word files rebuilt with a clean single-column layout; stray Markdown markup removed.
- Removed superseded documents: v8.1 Word files and Markdown, the v5–v8 audit notes, the v6 manuscript insert and v5–v7 supplement fragments (their content is in the v8.2 supplementary materials).
- No change to the model code, inputs or numerical results. Verified by a clean end-to-end rerun (1,000 draws per case): all tests pass and all outputs match to floating-point rounding.

# V8.1 — Science text, displays and bibliography expansion

- Expanded main manuscript scientific substance to nearly the 3,000-word standard Research Article allowance; exactly 4 figures + 1 table, 50 references.
- All 17 supplemental figures remain in the consolidated supplement; Grid Harvester is Figure S1.
- No changes to the numerical model, results, or parameter assumptions; figure-rendering scripts only remove obsolete version labels.
- Preserved corresponding author, ORCID, AI and competing-interests details from the latest user instructions.

# V8 documentation and journal integrity revision (20 November 2026)

- Correct corresponding author to Mr. Jonathan Bily, Cloud Wash Laundry Corporation, Teruel, Spain; correspondence from Zaragoza, Spain; telephone +34 674 98 52 17; ORCID 0009-0004-3526-7271.
- Correct spelling to Dr. Christoph Pahl, Munich, Germany; retain Patricia Valdes Bacallao, University of Málaga, Málaga, Spain.
- AI disclosure: Artificial Inventor/Synthetic Scientist V63. No competing interests declared.
- Remove draft labels, instructions and working footers from the journal documents.
- Provide consolidated transport model methods, explicit constraints and parameters, 25 source references and the corrected Eason–Fennessy review citation.
- Assemble all 17 supplementary figures in a single Word file, with Grid Harvester S1 embedded and referenced from article.
- Maintain all underlying V7 model inputs, outputs and figures; no new claimed transport model rerun.
- Explicit pre-submission audit identifies remaining email, author approval and DOI confirmations.

# V7.0 — 20 Nov 2026 (referee revisions)

- Corrected the human-food calorie-equivalent interpretation in `food()` and kept the legacy value only with an explicit deprecation flag. Greenhouse/seafood gross 3.487m and assumption-adjusted edible 2.590m equivalents; hemp meal 10.984m separately prospective; no complete-diet claim.
- Added `us7_community_screen.py`: high-level RAS solids/dissolved capture, sanitation, salinity conditioning and separated side-stream treatment, with separate illustrative community capex and operating cost; no transport LP adjustment.
- Added adoption, efficacy and active-compound livestock sensitivities; product residue and regulatory safeguards are out of scope and not assumed satisfied.
- Figure S14 corrected to specify *no added seaweed nutrients* (aquafeed remains an external nutrient source) and N/P retained in seafood; Figure 05 food title corrected. Added process Figure S16 and food/livestock Figure S17. Replaced journal Figure 2 with simplified schematic; detailed Map 1/Poster kept unchanged.
- Added working Word manuscript, compiled supplementary material, revised methodology, and cover-letter draft. Missing author confirmation, source validation and permanent data DOI explicitly flagged.
- V7 saved baseline transport outputs and original transport Monte Carlo unchanged; V6 and V7 mass-balance/sensitivity tests pass. A full fresh 1000-draw transport rerun remains for signoff.

# V6.0 — Seafood-to-Asparagopsis elemental nutrient recovery (2026-11-20)

- Preserves the full V5 transport, nuclear, offshore seaweed, greenhouse, aquaculture, grain-drying and cattle-feed assumptions and model outputs.
- Adds `us6_nutrient_balance.py` with independent elemental feed-N/feed-P conservation from fish/shrimp RAS through harvested seafood, dissolved waste, sludge, treatment, delivery, co-location, Asparagopsis uptake, and residual potentially recoverable fertilizer.
- Distinguishes zero purchased *Asparagopsis* nutrients from supplemented 431 kt/y planned output. At central assumptions, RAS recovered nutrients support 267 kt/y dry Asparagopsis without supplemental N/P, versus 431 kt/y with 5.89 kt/y supplemental elemental N. Original 45 MtCO2e methane reduction remains conditional; nutrient-only case 27.9 MtCO2e/y.
- Regenerates `Fig05_cascade_food.png/.pdf` with an explicit nitrogen-supplement caveat on the existing cattle-feed result; the underlying food-energy outputs are unchanged.
- Adds manuscript-ready insertion text (`MANUSCRIPT_INSERT_V6.md`) and 1,000 seeded draws (nutrient uncertainty separated from unchanged existing 1,000-draw transport Monte Carlo), new S14/S15 PDF/PNG figures, nutrient output CSV/JSON, independent test suite and detailed supplementary methods.
- Does **not** add unverified fertilizer revenue, claim national fertilizer sufficiency, silently alter the original 2050 transport optimisation, or treat freshwater effluent as immediately suitable for marine seaweed culture.
- `run_all.sh` now includes V6 nutrient model and tests. Standalone V6 model and V5 regression tests pass; full original high-compute V5 optimisation was not rerun in this V6 build.

# Changelog

Versions of the U.S. transport decarbonisation model and manuscript. The version number is the same in the ZIP file name, the README and the manuscript documents.

## v5.0 — 20 Nov 2026 (authorised civilian fuel services and bounded breeder learning)

- Retains all V4.1 transport, seaweed, electric-highway, Grid Harvester, gas-era, post-gas and theoretical fission scenarios.
- Fixes the V4.1 inversion between unrestricted and nuclear-only sustainable-fission costs: exhaustive integer hub enumeration across **0–2,000 hubs** applies consistent fleet-learning capital costs to the LP. Result: unrestricted $498.862bn/year at 728 hubs; nuclear only $498.920bn/year at 729 hubs. Bound explicitly limits global-optimality claim.
- Adds a standalone 2026–2100 authorisation and capacity screen (`us5_fuel_transition.py`) distinguishing **public government-surplus material (~19.7 t hypothetical authorisable source)**, **eligible civilian spent-fuel resource**, and **exogenously assumed future licensed fuel services**. Existing conventional reactors are not credited as net breeders. No nuclear-material production, reactor-fuel design or reprocessing details are modelled.
- Five source/capacity scenarios, explicit construction limits, and new Figure S13; independent source conservation and no-double-counting tests (`us5_test.py`).
- Adds methods, source references and submission-readiness audit with caveats. V4.1's previous figures, data and modules remain available.
- The full new 1,000-draw Monte Carlo clean rerun exceeded the execution environment's time limit. Established-case outputs were unchanged by code and are retained from V4.1; final fresh-clone validation is still required.

## v4.1 — 20 Nov 2026 (theoretical sustainable-fission future)

- New `sustainable_fission_params`: post-gas system with mature breeder hubs at 950 °C (sulfur–iodine allowed), at the HTGR hubs' cost with a $12/MWh_th closed fuel cycle; no LWR SMRs. Option `nuclear_only` removes wind, solar and offshore wind.
- New cases:
  - `sustainable_fission`: $500.5 bn.
  - `sustainable_fission_nuclear_only`: $498.9 bn, 728 hubs.
  - `..._si_cheap`: sulfur–iodine at $0.8/kg, $498.5 bn.
  - `..._premium`: capital ×1.25 and a $15/MWh_th fuel cycle, $529.2 bn.
- Unused extraction steam can return to the turbine (`HTGR["return_unused_steam"]`, variables `m2e`, `d2e`). It is enabled only in the sustainable-fission cases, so earlier results are unchanged.
- New per-case output `hub_energy_twh` (where hub heat goes); new fig. S12 (`ScienceFigS12_sustainable_fission`).
- All earlier results are unchanged (only `scenarios.json` gains the new cases and fields).

## v4.0 — 20 Nov 2026 (referee revision 5: reactor temperature, post-gas comparison, breeder qualification)

- **Pyrolysis heat supply corrected (substantive model change).** Xe-100-class reactors deliver 750 °C helium, which cannot supply 900–1,000 °C reaction heat. The default configuration (`PYRO["config"] = "xe100"`) now takes 2.5 kWh/kg H2 of methane preheat from the reactor and supplies the remaining 5.8 kWh/kg with electric heaters at 95% efficiency, adding 6.1 kWh of electricity and $0.02/kg of heater capital. Its electricity is in the balance and in the hydrogen carbon intensity (now 3.0 kg CO2e/kg).
  - New VHTR sensitivity (`vhtr_params`; cases `least_cost_vhtr`, `design_sweet_spot_vhtr`) reproduces the earlier all-reactor-heat design.
  - Headline costs: least cost $455.2 bn (was 451.4); 220 GW $506.1 bn (504.1); 515 GW $590.3 bn (588.2).
  - The 220 GW case now makes 38 TWh of seaweed fuel (was 64), because extra hydrogen now costs electricity.
  - Monte Carlo: 96% / 84% / 33% of draws below late-2025 petroleum.
- Sulfur–iodine cycle offered only when the reactor outlet is at least 900 °C (`HTGR["outlet_c"]`).
- Post-gas like-for-like decomposition: new cases `least_cost_no_blend_no_lightweight` and `..._pipe_elec`.
- Post-gas sensitivities: HTSE at 42 and 48 kWh/kg and at $1.5/kg; reactor cost low and high; breeder fleets (`breeder_params`: capital ×1.25 with a $15/MWh_th fuel cycle, and ×1.5 with $20/MWh_th).
- `fuel_supply` now reports fleet GWe, breeder start-up plutonium (10 t/GWe) and the plutonium in U.S. commercial spent fuel (95,000 tHM at 1%); its lifetimes are labelled theoretical upper bounds.
- `htse_firm_power` compares steam-electrolysis electricity with firm nuclear output.
- HTSE parameters moved into the parameter set (`p["NUCLEAR_H2"]`).
- Fig. S10 relabelled for 750 °C helium. Fig. S11 now compares with the gas era without the blend, and labels fuel lifetimes as upper bounds.

## v3.0 — 20 Nov 2026 (model extension: after natural gas)

- New post-gas mode (`post_gas=True`, `post_gas_params`). Pyrolysis is unavailable, there is no gas grid (no blend; pipeline compressors fully electric), and there is no methane-derived carbon for vehicle structures.
- New hydrogen routes from the reactor hubs (`I.NUCLEAR_H2`):
  - high-temperature steam electrolysis (INL NOAK reference: 36.8 kWh_e + 6.4 kWh_th per kg, $0.8/kg capital and O&M);
  - an optional sulfur–iodine thermochemical cycle (45% heat-to-H2 at 900–950 °C; $1.5/kg assumed).
  Both are offered only after gas; HTSE is not chosen even when offered alongside pyrolysis.
- Hydrogen carbon intensity is now production-weighted across routes.
- New `fuel_supply()`: thermal output of the fleet; natural uranium for once-through HALEU versus heavy metal for closed fast or thorium breeding; years of supply from the U.S. depleted-uranium stockpile, U.S. and world thorium, world identified uranium and seawater uranium (`I.FUEL`).
- New cases `post_gas_least_cost`, `post_gas_least_cost_si`, `post_gas_sweet_spot`, `post_gas_design`. Least cost after gas: $495.6 bn/yr, all hydrogen from HTSE.
- New fig. S11 (`ScienceFigS11_post_gas`).
- Gas-era results unchanged. The added (inactive) variables change the Monte Carlo and sweep files only at floating-point level (< 1e-9).

## v2.4 — 20 Nov 2026 (referee revision 4)

- Reactor heat: each hub's breakdown of top-tier heat (pyrolysis, turbine, step-down) is now written to `scenarios.json` (`hub_heat_twh`). Heat not used for pyrolysis was already sent to the turbine, so none is left unused.
- New flexible-heat-dispatch sensitivity (`flex_heat=True`; cases `least_cost_flex_heat`, `design_sweet_spot_flex_heat`, `design_flex_heat`). Top-tier heat can step down to process steam or drying, and process steam to drying, through heat exchangers (95% effective, $2/MWh). Transport cost: least cost $453.7 bn, 220 GW $504.7 bn, 515 GW $586.8 bn; whole-system cost changes by less than 0.5%.
- System boundary: new no-blend cases for the 220 GW and 515 GW builds (`*_no_blend`). With no blend, the LP objective equals the transport cost exactly: $460.1, 511.2 and 589.9 bn.
- The electric process-heat and drying adders ($2 and $8/MWh) are now in the reported cost as `process_heat_equipment` (515 GW: +$0.27 bn, to $588.2 bn), so reported cost = LP objective + fixed terms exactly.
- New fig. S10 (`ScienceFigS10_heat_and_boundaries`).

## v2.3 — 20 Nov 2026 (referee revision 3)

- Monte Carlo: all three cases now use 1,000 draws (the least-cost and 220 GW cases previously used 500). Least cost: median $501 bn (375–637), cheaper than late-2025 petroleum in 97% of draws; 220 GW: $570 bn (456–696), 84%; 515 GW unchanged at $670 bn (555–792), 35%.
- Gas extension: the gas displaced by the programme is split into the hydrogen-blend part and pipeline-compressor electrification. Only the blend part now shrinks as heat pumps remove building gas. Least-cost system: 2086 → 2096 with clean heat pumps (was 2095); 2103 with a decarbonised Canada (was 2102); 2108 with Canadian output raised to 25 Bcf/d.
- Heat credit: only the low-grade heat the food uses actually absorb is credited (was all heat rejected by the hubs).
- LP objective aligned with reported cost: the heat credit (new `heat_sold` variable, capped by hub output and by the food markets) and on-site hydrogen delivery to refineries are now in the objective. A reconciliation of LP objective to reported cost is written for every case (residual zero). Least cost $451.4 bn (was 450.9); 220 GW $504.1 bn (was 505.4); 515 GW $588.0 bn (was 590.5). In the 515 GW build the optimiser now uses less pyrolysis hydrogen (14.1 instead of 25.7 Mt/yr), so its gas draw, solid carbon and emissions fall.

## v2.2 — 20 Nov 2026 (referee revision)

- Least-cost case now uses the same 20% hydrogen blend as every other case and as the Monte Carlo ($451 bn/yr); the offshore sweep uses the same basis.
- 220 GW offshore case relabelled as a selected diversification case, not a cost optimum. Its $55 bn/yr premium over the least-cost system is reported with what it buys.
- Manuscript retitled and led by the least-cost system.
- Gas model: the Potential Gas Committee resource convention is stated explicitly, with a sensitivity on potential resources only, recovery factors of 60–100%, and the 15-year reserves floor defined as a modelling threshold.
- Gas results added for the least-cost system.
- Screening costs added for heat pumps (clean electricity) and biogas, plus avoided building CO2.
- Fertiliser credit flagged as an assumption, with a sensitivity case without it.
- New `--no-figures` option in `run_all.sh`.
- Supplementary Materials drafted; references 19, 20, 22 and 28 completed.

## v2.1 — 20 Nov 2026

- Building heat pumps on clean power, farm and sewage biogas, and a decarbonised Canada exporting all its gas (`us2_gas_extension.py`, fig. S9).
- Full-size system map (`us2_poster_map.py`, Data S1).
- Grid Harvester figure (fig. S1).
- Flat repository layout; *Science* main-text figures (`us2_science_figs.py`).

## v2.0 — 19–20 Nov 2026

- Large offshore wind with region-specific seaweed and an offshore cost sweep.
- Grid Harvesters, battery–sail vessels and drones.
- Bamboo, hemp and ethanol-to-jet.
- All aviation, farm, construction and industrial machinery.
- Reactor learning-curve costs, food from the heat cascade, and carbon for vehicle structures.

## v1 — 19 Nov 2026

- First U.S. model: HTGR heat cascade, kelp, electric highways, hydrogen blending, gas depletion with Canada, and the E85 transition.
