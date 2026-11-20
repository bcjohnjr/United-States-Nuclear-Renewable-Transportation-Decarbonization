# U.S. transport decarbonisation model — v8.2

Code and data for J. K. Bily, C. Pahl and P. Valdes Bacallao, *Reactor heat, electrification and renewable fuels could replace U.S. transport petroleum at lower annual cost* (submitted to *Science*).

Repository: https://github.com/bcjohnjr/United-States-Nuclear-Renewable-Transportation-Decarbonization
Contact: Jonathan Karl Bily, jonathan@cloudwashlaundry.com

The model asks whether all U.S. transport energy could be supplied without petroleum in 2050, at what annual cost, and what happens once natural gas is no longer available for hydrogen. It covers road, aviation, marine and rail transport, farm, construction and mining machinery, industrial trucks and pipelines. The system has five parts:

- **Reactor hubs.** Four-module high-temperature gas-cooled reactor (HTGR) hubs run a heat cascade: hydrogen (methane pyrolysis, or steam electrolysis after the gas), electricity, biocrude upgrading, drying, then greenhouses and fish farms.
- **Land biomass.** Residues, energy grasses, bamboo, hemp and ethanol converted to jet fuel.
- **Electric highways.** Overhead catenary on the Interstates, plus battery-electric vehicles.
- **Optional offshore wind with seaweed.** Regional seaweed species grown between the turbines.
- **Pyrolysis carbon.** Capped markets for the solid carbon, including vehicle structures.

## Main results (2050, 2026 US$ per year, pre-tax, transport-only)

| Case | Cost ($ bn) | Monte Carlo median (5–95%) | Cheaper than late-2025 petroleum |
| --- | --- | --- | --- |
| Petroleum, late-2025 prices | 592.8 | — | — |
| Petroleum, Nov-2026 prices | 881.0 | — | — |
| **Gas era, least cost (no offshore wind)** | **455.2** | 504 (377–641) | 96.2% of draws |
| Gas era, 220 GW offshore wind and seaweed | 506.1 | 574 (457–700) | 83.5% |
| Gas era, 515 GW offshore wind and seaweed | 590.3 | 673 (558–794) | 33.3% |
| After gas, steam electrolysis | 495.6 | — | — |
| Sustainable fission (hypothetical breeders), 728 hubs | 498.9 | — | — |
| Sustainable fission, nuclear only, 729 hubs | 498.9 | — | — |
| Sustainable fission, breeder cost premium | 529.3 | — | — |

- Emissions fall from 2,872.5 to 178.2 Mt CO2e/yr (−93.8%) in the gas era and to 131.5 Mt (−95.4%) after the gas.
- First U.S. gas shortfall: 2086 with the pyrolysis programme (2088 without); 2096 with building heat pumps on clean power; 2082 without Canadian imports; 2107 with all expanded Canadian production plus heat pumps.
- The hypothetical breeder fleet needs about 213 t/yr of heavy metal (U.S. depleted uranium ~2,200 yr, U.S. thorium ~2,800 yr) but about 2,333 t of start-up plutonium, 2.5 times the plutonium in U.S. spent fuel.
- Reactor waste heat could support 8.0 Mt/yr of vegetables and 1.0 Mt/yr of seafood; these food and nutrient accounts are kept separate from transport cost.

## Reproduce

Every file sits in the repository root; there are no sub-folders. The scripts read and write in the folder they are in.

```
pip install -r requirements.txt
bash run_all.sh                     # full model, tests and figures (1,000 Monte Carlo draws per case)
bash run_all.sh 1000 --no-figures   # numerical results only (about 1 minute)
```

A clean run reproduces every output CSV and JSON byte for byte, except `scenarios.json` and `nutrient_balance_v6.json`, which differ only by floating-point rounding (relative differences below 1e-15). Monte Carlo seeds: 11 (least cost), 13 (220 GW), 7 (515 GW), 23 (nutrients).

## Files

| File | Contents |
| --- | --- |
| `us2_inputs.py` | All assumptions, with sources in comments |
| `us2_model.py` | Transport linear programme, reactor learning, bounded 0–2,000-hub search, post-gas and sustainable-fission cases, fuel supply, Monte Carlo, gas depletion, transition |
| `us2_gas_extension.py` | Gas supply with heat pumps, biogas and Canadian imports (`gas_extension.json`, fig. S9) |
| `us5_fuel_transition.py`, `us5_test.py` | Staged start-up fuel and deployment screen (fig. S13) and its tests |
| `us6_nutrient_balance.py`, `us6_test.py` | Nitrogen and phosphorus balance from aquafeed to *Asparagopsis* (figs. S14, S15) and its tests |
| `us7_community_screen.py`, `us7_test.py` | Nutrient-recovery process, community costs, food and methane sensitivities (figs. S16, S17) and tests |
| `grid_harvester.py`, `grid_harvester_*.jpg` | Grid Harvester sizing and illustrations (fig. S1) |
| `us2_figures.py`, `us2_science_figs.py`, `us2_basemap.py`, `us2_poster_map.py`, `us7_publication_map.py` | Figures and maps |
| `v7_update_archive.py` | One-time migration that annotated food fields in `scenarios.json` (kept for provenance; not part of `run_all.sh`) |
| `run_all.sh` | Runs everything |
| `*.json`, `*.csv`, `*run_log.txt` | Results of the published run |
| `Fig*`, `ScienceFig*`, `Map*`, `Poster*` | Figures (PNG and PDF) |
| `Science_Research_Article_V8.2.docx`, `MANUSCRIPT_V8.2.md` | Manuscript |
| `Supplementary_Materials_V8.2.docx`, `SUPPLEMENTARY_MATERIALS_V8.2.md` | Supplementary materials |
| `Cover_Letter_Science_V8.2.docx` | Cover letter |
| `V7_BASELINE_INTEGRITY.json` | Hashes of the v7 baseline outputs |
| `CHANGELOG.md`, `requirements.txt` | Version history and Python packages |

## Limits

The model balances energy over a year and has no hourly dispatch, storage or transmission. Seaweed farming, pyrolysis carbon markets, HTGR costs and liquid-fuel yields have not been shown at national scale. Very-high-temperature breeder reactors with full recycling are hypothetical. The maps are schematic, not a siting study.
