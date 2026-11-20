---
title: "Supplementary Materials for: Reactor heat, electrification and renewable fuels could replace U.S. transport petroleum at lower annual cost"
---

Jonathan Karl Bily\*, Christoph Pahl, Patricia Valdes Bacallao

\*Corresponding author. Email: jonathan@cloudwashlaundry.com

**This PDF file includes:** Supplementary Text S1 to S18; Figs. S1 to S17; Tables S1 to S7; References (*1*–*55*).

Model code, inputs, outputs and tests: https://github.com/bcjohnjr/United-States-Nuclear-Renewable-Transportation-Decarbonization (release v8.2).

# Supplementary Text

## S1. Scope and system boundary

The model is an annual 2050 balance of U.S. transport energy services. It allocates electricity, hydrogen, land biomass, offshore resources and reactor heat across the transport system at least annual cost. It is a feasibility screen, not a spatially or hourly resolved construction plan. The reported transport cost covers generation, grid and charging infrastructure, electric roads and rail, reactor hubs, hydrogen production and delivery, biomass, fuel conversion, seaweed farms where built, and the net premium of vehicles and machines, minus credits for carbon products, fertiliser, useful heat and surplus power. Optional hydrogen blending into building gas, food production, nutrient recovery and livestock outcomes are reported in separate accounts and are not added to or subtracted from the transport cost. Costs are in 2026 U.S. dollars.

## S2. Baseline transport demand and 2050 technology shares

Table S1 lists the reference consumption that defines transport services, and Table S2 the fixed 2050 technology shares. The conversion routines are base_demand() and enduse_2050() in us2_model.py. The shares are scenario assumptions, not adoption forecasts; the central demand-growth multiplier is 1.00. Before scenario-specific allocation, 2050 transport needs about 1,377 TWh of electricity, 118 TWh of hydrogen and 1,556 TWh of liquid fuels, including about 1,000 TWh of jet fuel.

**Table S1. Reference transport fuel consumption.**

| Segment | Input magnitude | Status |
|:--|:--|:--|
| Gasoline | 8.9 million barrels/day | EIA-anchored baseline |
| On-road diesel | 46 billion gallons/year | assumption, EIA-consistent |
| Rail diesel | 3.5 billion gallons/year | assumption |
| Marine distillate | 2.0 billion gallons/year | assumption |
| Marine residual oil | 0.18 million barrels/day | assumption |
| Jet fuel | 1.70 million barrels/day | assumption |
| Natural gas for pipelines | 1.0 quadrillion Btu/year | assumption |
| Farm diesel | 3.5 billion gallons/year | order-of-magnitude baseline |
| Construction and mining diesel | 2.8 billion gallons/year | assumption |
| Industrial trucks | 1.5 billion diesel-gallon equivalents/year | assumption |

**Table S2. Modelled 2050 technology shares.**

| Segment | Technology allocation |
|:--|:--|
| Light-duty vehicles | 95% battery-electric; 2% hydrogen fuel cell; 3% liquid |
| Heavy-duty vehicles | 45% electric road; 30% battery-electric; 15% range-extended electric; 7% fuel cell; 3% liquid |
| Aviation | 97% drop-in sustainable jet fuel; 3% hydrogen |
| Marine | 85% liquid; 5% electric; 10% hydrogen |
| Rail | 60% electric; 20% range-extended; 20% liquid |
| Farm machinery | 30% battery-electric; 50% range-extended; 20% liquid |
| Construction equipment | 40% battery-electric; 40% range-extended; 20% liquid |
| Industrial vehicles | 90% electric; 10% fuel cell |
| Pipelines | 60% electrified; 40% gas (gas era) |

## S3. Decision variables, objective and constraints

The linear programme is solved with SciPy and the HiGHS solver (*21*, *22*). Its decision variables are onshore wind, solar, light-water reactors, surplus electricity exports, HTGR hubs, four hydrogen routes (pyrolysis, conventional electrolysis, high-temperature steam electrolysis and sulfur–iodine), land-feedstock tiers, bamboo, hemp, fuel-conversion routes, thirteen offshore wind zones, seaweed harvesting routes, flexible heat dispatch and carbon-product markets.

Objective (schematic): minimise C = Σ(generation and reactor costs) + Σ(feedstock and conversion costs) + Σ(hydrogen production and delivery costs) + Σ(heat boosting and process-heat equipment costs) − export revenue − useful-heat revenue − bounded carbon-product revenue.

Electricity balance: E~onshore~ + E~solar~ + E~LWR~ + E~HTGR~ + E~offshore~ ≥ E~transport~ + E~H2~ + E~fuels~ + E~process~ + E~export~. Hydrogen balance: H~pyrolysis~ + H~electrolysis~ + H~HTSE~ + H~SI~ ≥ H~vehicles~ + H~refining~ + H~blend~. Liquid balance: Σ~i~ y~i~x~i~ ≥ L~total~, with a jet sub-balance Σ~i~ j~i~y~i~x~i~ ≥ L~jet~. Feedstock equalities conserve mass from source to conversion route. Upper bounds apply to feedstock tiers, land, renewable capacity, carbon markets, offshore zones and heat sinks. Adequacy surrogates are a maximum 40% solar share and at least 15% firm electricity; these do not prove hourly operability.

The objective is linear at a fixed fleet-average reactor capital cost. Reactor learning is solved by iterating fleet size and unit cost to convergence (solve_learning). For the sustainable-fission cases the fleet cost curve is not convex, so the hub count is fixed and searched exhaustively over every integer from 0 to 2,000 (solve_bounded_learning). For each case the LP objective plus fixed terms is reconciled with the reported total (objective_reconciliation; residual below 10^−12^ billion dollars).

## S4. Power technology parameters and reactor learning

**Table S3. Electricity supply parameters.** Annualised supply cost and central capacity factor; transmission, distribution and firming adders are applied separately.

| Technology | Cost (US\$/MWh) | Capacity factor |
|:--|--:|--:|
| Onshore wind | 55 | 0.40 |
| Solar PV | 48 | 0.25 |
| Fixed-bottom offshore wind | 95 | 0.45 |
| Floating offshore wind | 115 | 0.47 |
| Light-water small modular reactor | 115 | scenario-constrained |
| Transmission and distribution adder | 30 | demand-linked |
| Variable renewable firming adder | 20 | assumption |

Each HTGR hub has four Xe-100-class modules (800 MWt total), a 93% capacity factor and a 750°C helium outlet (*7*). Capital is annualised at a 7% cost of capital over 60 years. Fleet cost follows Wright's law, cost(n) = FOAK × n^log2(1−LR)^, with low, central and high first-of-a-kind and learning-rate cases informed by the literature (*8*–*10*) (fig. S5).

## S5. Fuel pathways and conversion assumptions

**Table S4. Fuel conversion routes.** Screening yields, not guaranteed commercial performance.

| Route | Useful output | H~2~ demand | Direct electricity and heat | Jet fraction |
|:--|:--|:--|:--|--:|
| Hydrothermal liquefaction (HTL) | 2.60 MWh/dry t | 13.5 kg/t | 0.15 MWh~e~ + 0.35 MWh~th~ per t | 0.45 |
| Hydrogen-assisted gasification and Fischer–Tropsch (PBTL) | 4.44 MWh/dry t | 110 kg/t | 0.60 MWh~e~ per t | 0.65 |
| Hydroprocessed esters and fatty acids (HEFA) | 10.1 MWh/t oil | 35 kg/t | 0.10 MWh~e~ + 0.30 MWh~th~ per t | 0.55 |
| Alcohol-to-jet (ATJ) | 19.8 TWh per billion gallons of ethanol | route-dependent | priced separately | 0.85 |

Land tiers are 200 million dry tonnes of low-cost residues at US\$65/t, 150 million at US\$85/t and up to 200 million of perennial grasses and energy cane at US\$100/t (*2*). Clumping bamboo is capped at 2.5 million ha at a central 15 t/ha/year (10 to 22 in sensitivities). Hemp is capped at 4.0 million ha with 0.9 t seed and 7.0 t stalk per hectare per year.

## S6. Methane pyrolysis, electrolysis and reactor temperature

A 750°C reactor outlet cannot drive methane pyrolysis, which needs about 900 to 1,000°C (*6*). In the gas-era configuration, reactor helium preheats the methane (about 2.5 kWh of heat per kilogram of hydrogen) and electric heaters supply the remaining 5.8 kWh/kg at 95% efficiency, costing 6.1 kWh of electricity and US\$0.02/kg in heater capital. Pyrolysis uses about 4.08 kg CH~4~ per kilogram of hydrogen and yields about 3 kg of solid carbon. A 950°C very-high-temperature reactor sensitivity supplies all pyrolysis heat from the reactor (US\$451.4 billion per year, against US\$455.2 billion).

High-temperature steam electrolysis uses 36.8 kWh~e~ plus 6.4 kWh~th~ per kilogram at US\$0.8/kg non-energy cost (*23*). The sulfur–iodine cycle uses 87.6 kWh~th~/kg at US\$1.5/kg and is only allowed when the reactor outlet is at least 900°C. Conventional electrolysis remains available as a fallback.

## S7. Offshore seaweed and the Grid Harvester

Thirteen coastal zones each have a regional seaweed species, cultivation yield, nutrient limit and offshore wind cost (fig. S3). Seaweed biomass goes to HTL or PBTL, and zone output is tied to offshore capacity. Zones are added in cost-merit order (Fig. 3). These are engineering-screen assumptions, not observed yields at 220 GW scale (*12*, *13*, *35*–*37*).

The proposed Grid Harvester (fig. S1) is a vessel that follows the cultivation lines while a buoyancy-controlled head cuts seaweed from the netting. A hose returns the slurry to battery–sail transfer vessels. With a faired hose, the modelled energy is about 20 to 34 MJ per 1.44-ha harvest cycle, against 90.9 MJ for a conventional configuration. These are design calculations (grid_harvester.py), not field measurements.

## S8. Carbon markets, emissions and petroleum comparators

Pyrolysis carbon is sold only up to capped market channels (fig. S7); unsold carbon carries a storage cost. Carbon nanotube use in vehicle structures is a possible market, not demonstrated supply. Emissions use route-specific well-to-wheel factors, 1.5% upstream methane leakage (*45*), hydrogen leakage and a lifecycle electricity factor of 10 g CO~2~e/kWh. Biochar removal (71.7 Mt CO~2~ per year in the least-cost case) is reported but not netted against emissions.

The petroleum comparator prices the same modelled services at historical pre-tax prices: US\$588.8 billion for liquid fuels plus US\$4.0 billion for pipeline gas at late-2025 prices (US\$592.8 billion in total), and US\$881.0 billion at November 2026 prices. These are reference points, not 2050 price forecasts.

## S9. Natural-gas depletion and supply extensions

us2_gas_extension.py tracks U.S. and Canadian gas year by year from 2026. U.S. demand starts at 42.5 Tcf per year, of which about 3.1 Tcf comes from Canada. Remaining resources follow the Potential Gas Committee convention (*51*) and Canada Energy Regulator data (*52*), with 80% recovery, a production floor of 15 years of reserves and liquefied natural gas exports of 30 billion cubic feet per day. The shortfall year is the first year in which U.S. demand cannot be met. Heat pumps replace 90% of building space and water heating by 2050 (coefficient of performance 2.2 to 3.5) and save about 6.3 Tcf per year (*53*). Biogas from manure, wastewater, food waste and landfills supplies 0.11 to 0.47 Tcf per year (*54*). Table S6 and figs. S8 and S9 give the results for the least-cost case.

**Table S6. First year in which U.S. gas demand exceeds supply (least-cost transport system).**

| Case | Shortfall year |
|:--|--:|
| No transport pyrolysis programme | 2088 |
| With pyrolysis programme (central) | 2086 |
| Plus biogas (central to all organics) | 2086–2087 |
| Plus heat pumps on clean electricity | 2096 |
| Plus heat pumps on today's grid mix | 2093 |
| No Canadian imports | 2082 |
| All current Canadian production available | 2091 |
| All expanded Canadian production plus heat pumps (clean) | 2107 |
| Recovery factor 60% / 100% (with programme) | 2068 / 2104 |

## S10. Hydrogen after natural gas

The post-gas cases (post_gas_params) remove pyrolysis and building-gas blending and allow HTSE, conventional electrolysis and, where the reactor outlet is at least 900°C, sulfur–iodine hydrogen. Table S7 lists the results; fig. S11 shows the cost composition. On a common transport-only, no-blend boundary, the gas-era system costs US\$462.4 billion and the post-gas system US\$495.6 billion (+US\$33.3 billion, +7.2%). The increase comprises US\$7.5 billion from losing pyrolysis carbon for vehicle structures, US\$2.7 billion from fully electric pipeline compressors and US\$23.0 billion from replacing pyrolysis hydrogen. Against the headline gas-era result with blending (US\$455.2 billion), the difference is US\$40.5 billion (+8.9%). Hydrogen production falls from 12.8 to 7.7 Mt per year, and hub count rises from 203 to 251. When reactor capital is high, the optimiser builds no hubs and powers hydrogen production from wind and solar instead, at US\$513.5 billion.

**Table S7. Post-gas and sustainable-fission cases.** Transport-only cost in billions of 2026 U.S. dollars per year.

| Case | Cost | Hubs | Notes |
|:--|--:|--:|:--|
| Post-gas, least cost (HTSE) | 495.6 | 251 | 7.70 Mt H~2~ from HTSE; 131.5 Mt CO~2~e |
| Post-gas, sulfur–iodine allowed | 495.6 | 251 | sulfur–iodine not chosen at 750°C outlet |
| HTSE at 42 / 48 kWh/kg | 498.6 / 502.0 | 251 | |
| HTSE capital +50% | 501.0 | 251 | |
| HTSE 48 kWh/kg and capital +50% | 505.1 | 203 | |
| Reactor capital low / high | 445.5 / 513.5 | 785 / 0 | |
| Breeder fuel cycle, central / high | 508.4 / 513.5 | 93 / 0 | |
| Post-gas, 220 GW / 515 GW offshore | 547.2 / 614.8 | 204 / 93 | |
| Sustainable fission, with wind and solar | 498.9 | 728 | 1,844 TWh electricity from hubs |
| Sustainable fission, nuclear only | 498.9 | 729 | 130.1 Mt CO~2~e |
| Sustainable fission, cheap sulfur–iodine | 498.5 | 726 | 7.69 Mt H~2~ from sulfur–iodine |
| Sustainable fission, breeder premium | 529.3 | 728 | capital ×1.25; fuel cycle US\$15/MWh~th~ |

## S11. Sustainable fission and fuel supply

The sustainable-fission cases (sustainable_fission_params) assume that 950°C breeder reactors with full fuel recycling become commercial at HTGR-hub cost (*24*). They combine the post-gas configuration with a breeder fuel-cycle cost of US\$12 per MWh of heat, exclude light-water reactors and, in the nuclear-only variants, exclude wind and solar. Unused extraction steam returns to the turbine. The hubs supply electricity, HTSE or sulfur–iodine hydrogen, steam for HTL and upgrading, drying heat and low-grade heat (fig. S12B).

fuel_supply() compares once-through and closed fuel cycles for the nuclear-only fleet (4,751 TWh of heat per year; 233 GW electric-equivalent). Once-through operation would need about 40,930 t of natural uranium per year; a closed cycle needs about 213 t of heavy metal, a 192-fold gain in utilisation. At these rates, world identified uranium lasts about 198 years once-through; in a closed cycle, U.S. depleted uranium lasts about 2,210 years, U.S. thorium about 2,820 years, world identified uranium about 38,000 years and world thorium about 30,000 years (*20*, *55*). Start-up needs about 10 t of fissile material per GWe, or about 2,333 t for the fleet, 2.5 times the roughly 950 t of plutonium in U.S. spent fuel. That inventory is not qualified reactor fuel. us5_fuel_transition.py adds a staged deployment screen that separates authorised surplus material, licensed civilian recycling and conditional closed cycles (fig. S13); it is not a forecast of licensing or construction. The model contains no fuel-processing instructions.

## S12. Heat cascade and food accounting

Each hub sends high-temperature heat to pyrolysis preheating and electricity, medium-temperature heat to process steam, drying heat to agriculture and residual low-grade heat (35 to 70°C) to greenhouses, recirculating aquaculture and *Asparagopsis* tanks, within assumed market caps (fig. S6). Central output is 8.0 Mt of vegetables on about 17,778 ha, 1.0 Mt of fish and shrimp, 60 Mt of grain dried, 3.6 Mt of hemp seed and 2.52 Mt of hemp press meal. Grain drying preserves existing harvest.

Food energy equivalents = (vegetables × kcal/kg × edible fraction + seafood × kcal/kg × edible fraction) / (2,200 kcal × 365). Gross vegetables and seafood equal 3.49 million daily-energy equivalents; with edible fractions of 0.85 and 0.60, 2.59 million. These are not complete diets or people actually fed. Hemp meal (about 10.98 million equivalents) is reported separately because it needs food-grade processing (*47*).

## S13. Aquaculture-to-*Asparagopsis* nutrient balance

us6_nutrient_balance.py conserves nitrogen and phosphorus at each stage. One million tonnes of seafood at a feed-conversion ratio of 1.5 needs 1.5 Mt of aquafeed containing 5.6% N and 1.2% P (84 kt N, 18 kt P). Seafood retains 35% of N and 28% of P (29.4 kt N, 5.04 kt P). Solids and dissolved nutrients are captured at separate rates and reduced for treatment and delivery losses, leaving 27.47 kt N and 7.57 kt P. Only 35% of recovered flow is assumed eligible for seaweed tanks; this is not a measured national value.

Under these assumptions, nitrogen limits dry *Asparagopsis* to about 267 kt per year without added nutrients, 62% of the 431 kt target. The full target needs 5.89 kt N per year more; phosphorus is sufficient. After the full-target allocation, 17.86 kt N and 6.41 kt P remain in residual streams, about 0.16% of U.S. commercial nitrogen-fertiliser use (*41*). These streams are not certified fertiliser, and "no supplemental nutrients" still means aquafeed is an external input (fig. S14). Uncertainty uses 1,000 seeded triangular draws over feed conversion, composition, capture, delivery and seaweed demand (fig. S15).

## S14. Nutrient recovery process and community costs

The conceptual process (fig. S16) separates fish-farm sludge from bleed water, concentrates dissolved and solid nutrients, stabilises and disinfects them, tests for contaminants, conditions pH and salinity, feeds isolated seaweed tanks and removes rejected residues (*42*–*44*). The central screen treats 10 m^3^ of side stream per tonne of seafood at 2.5 kWh/m^3^, or 25 GWh per year. Treatment costs about US\$21.9 million per year (US\$6.9 to 130.4 million in sensitivities). Including greenhouses, fish farms, aquafeed, seaweed cultivation and supplemental nitrogen, the community account totals US\$15.44 billion per year against US\$21.4 billion in assumed produce sales. Permitting, labour detail, liabilities and distribution are not fully costed, so the difference is not a profit forecast. None of these amounts enter the transport cost.

## S15. Cattle methane response

The methane benefit depends on seaweed supply, participating cattle and assumed efficacy (*15*, *18*, *19*). Nutrient-limited seaweed corresponds to a potential 27.9 Mt CO~2~e per year and the full target to 45.0 Mt. Halving active-compound potency gives about 14.0 Mt; lower participation and efficacy give about 13.2 Mt (fig. S17). Bromoform content varies with species, cultivation and processing, and the Eason–Fennessy dose–response analysis has a published correction (*16*, *17*), so these values are scenario multipliers, not dose–response predictions. Residues, iodine, feed approval and delivery on pasture need validation.

## S16. Monte Carlo uncertainty and sensitivity

Each of the three gas-era cases has 1,000 seeded draws (seed 11 for least cost, 13 for 220 GW and 7 for 515 GW) from triangular distributions over technology costs, reactor capital and learning, biomass and seaweed yields, demand growth, fuel prices and carbon-market values. Table S5 summarises the results. These distributions are screening ranges, not calibrated probabilities.

**Table S5. Monte Carlo results (1,000 draws per case).** Median (5th to 95th percentile).

| Quantity | Least cost (0 GW) | 220 GW offshore | 515 GW offshore |
|:--|:--:|:--:|:--:|
| Transport cost (US\$ billion/year) | 504 (377–641) | 574 (457–700) | 673 (558–794) |
| Reactor hubs | 248 (17–829) | 230 (17–435) | 100 (17–230) |
| Hub capital (US\$/kWt) | 1,827 (456–5,576) | 1,846 (535–5,582) | 2,093 (615–5,589) |
| Hydrogen (Mt/year) | 13.4 (11.7–22.2) | 13.4 (12.4–25.0) | 13.6 (12.3–32.1) |
| Emissions (Mt CO~2~e/year) | 189 (172–219) | 190 (174–229) | 192 (174–254) |
| Emission reduction | 93.4% (92.4–94.0) | 93.4% (92.0–93.9) | 93.3% (91.2–93.9) |
| Cheaper than late-2025 petroleum | 96.2% | 83.5% | 33.3% |
| Cheaper than November 2026 petroleum | 100% | 100% | 100% |

Spearman rank correlations between inputs and cost in the 515 GW case are 0.82 for the net annual cost of battery-electric light vehicles, 0.36 for service-demand growth, 0.26 for fixed-bottom offshore wind cost, 0.21 for floating offshore wind cost and 0.12 for the reactor cost case. Correlations rank sensitivities; they are not causal estimates.

## S17. Reproducibility

The repository is a flat folder: every script, input, output and figure sits at the top level, with no subdirectories. It needs Python 3 with NumPy (1.24 or later), SciPy (1.9 or later) and Matplotlib (3.7 or later), as listed in requirements.txt. `bash run_all.sh 1000` runs the transport model, the 3,000 Monte Carlo draws, the gas, fuel-transition, nutrient and community modules and all regression tests, and regenerates the figures. On a clean copy the run took 53 s without figures. Every output CSV and JSON matched the archived files byte for byte, except scenarios.json and nutrient_balance_v6.json, whose largest differences were floating-point rounding (relative difference below 10^−15^ apart from a reconciliation residual of 10^−13^ billion dollars). Tests check energy and mass balances, objective reconciliation, the bounded hub search, calorie separation and nutrient conservation.

## S18. Limitations

The model balances energy annually and cannot demonstrate hourly adequacy, storage, ramping, winter peaks or transmission siting. Liquid-fuel yields, jet-fuel certification, refinery construction and offshore seaweed yields at national scale are assumed. Reactor costs, learning rates, very-high-temperature operation, breeding, recycling and start-up fuel availability are uncertain or speculative. The petroleum comparison uses fixed historical prices. The food, nutrient and cattle results need site-level engineering, contaminant control, sanitary approval and field trials. All results are conditional screening estimates.

# Supplementary Figures

![](ScienceFigS1_grid_harvester.png){width="6.5in"}

**Fig. S1. Grid Harvester concept.** (**A**) Side view with vessel and buoyancy-controlled head. (**B**) Plan-view path over the cultivation netting. (**C**) Modelled harvest energy per 1.44 ha with bare and faired slurry hoses. (**D**) Manoeuvring and unharvested area. Design calculations, not field results.

![](Map2_ehighways.png){width="6.5in"}

**Fig. S2. Illustrative U.S. electric-road corridors.** Schematic routes and lengths, not surveyed alignments.

![](Map3_seaweed_species.png){width="6.5in"}

**Fig. S3. Thirteen offshore cultivation zones and candidate seaweed species.** Indicative zones, not a siting assessment.

![](Map4_land_biomass.png){width="6.5in"}

**Fig. S4. Terrestrial biomass regions.** Candidate resource zones, including clumping bamboo and hemp.

![](Fig03_reactor_costs.png){width="6.5in"}

**Fig. S5. Reactor fleet cost learning.** Fleet-average capital cost under alternative first-of-a-kind cost and learning-rate assumptions.

![](Fig05_cascade_food.png){width="6.5in"}

**Fig. S6. Reactor heat cascade and food production.** Vegetables, seafood, grain-drying service and nutrient-limited *Asparagopsis*.

![](Fig06_carbon_markets.png){width="6.5in"}

**Fig. S7. Markets for pyrolysis carbon.** Capped market channels, storage and possible vehicle-structure applications.

![](Fig07_gas_and_transition.png){width="6.5in"}

**Fig. S8. Natural-gas depletion and transport transition.** (**A**) Remaining U.S. recoverable gas with and without the pyrolysis programme and Canadian imports. (**B**) Transport emissions during a phased transition from 2026, avoiding about 33 Gt CO~2~e by 2050 and 56 Gt by 2060.

![](ScienceFigS9_gas_extension.png){width="6.5in"}

**Fig. S9. Extending gas supply.** Shortfall year with biogas, building heat pumps and Canadian imports, and its sensitivity to the recovery factor (Table S6).

![](ScienceFigS10_heat_and_boundaries.png){width="6.5in"}

**Fig. S10. Flexible reactor heat use and cost boundaries.** Heat dispatch across uses, and transport-only cost compared with the combined cost including building-gas hydrogen blending.

![](ScienceFigS11_post_gas.png){width="6.5in"}

**Fig. S11. Hydrogen after natural gas.** Transport cost and emissions with steam electrolysis, sulfur–iodine and electrolysis sensitivities (Table S7).

![](ScienceFigS12_sustainable_fission.png){width="6.5in"}

**Fig. S12. Theoretical sustainable-fission fleet.** (**A**) Transport cost in the gas era, after gas and with breeder reactors. (**B**) Use of breeder-fleet heat. Costs are not reactor quotations.

![](ScienceFigS13_fuel_transition.png){width="6.5in"}

**Fig. S13. Fuel service and deployment screen.** Staged availability of start-up fuel and licensed reactors; not a forecast.

![](ScienceFigS14_nutrient_balance.png){width="6.5in"}

**Fig. S14. Nitrogen and phosphorus balance from aquafeed to seaweed.** Retention in seafood, losses, seaweed uptake and residual streams. "No supplemental seaweed nutrients" does not mean no external aquafeed.

![](ScienceFigS15_nutrient_sensitivity.png){width="6.5in"}

**Fig. S15. Nutrient capture and delivery sensitivity.** 1,000 seeded draws; distributions are assumptions, not empirical confidence intervals.

![](ScienceFigS16_RAS_process.png){width="6.5in"}

**Fig. S16. Conceptual nutrient recovery process.** Treatment, concentration, disinfection, salinity conditioning and isolated seaweed tanks. Not validated at full scale.

![](ScienceFigS17_food_methane.png){width="6.5in"}

**Fig. S17. Food energy and cattle methane sensitivity.** Edible-fraction correction and methane response under lower potency and participation.

# References

The supplementary materials cite the same numbered references (*1*–*55*) as the main text.
