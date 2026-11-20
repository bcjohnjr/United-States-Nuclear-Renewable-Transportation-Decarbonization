"""Inputs, U.S. transport-energy model v2 (USD 2026).  Tags: [S] sourced, [A] modeller assumption (varied in Monte
Carlo where it matters), [C] carried over from the Canadian two-coast model.  Not forecasts.

v2 scope: all aviation, all on-road, all rail and marine, all farm machinery, all construction & mining machinery and
all industrial trucks; large offshore wind with region-specific seaweed species; solar/wind-powered Grid Harvesters,
battery-sail transport vessels and utility drones; bamboo and hemp; ethanol-to-jet; food from the heat cascade;
reactor costs from a FOAK-to-NOAK learning model; a cost sweep for the offshore-wind 'sweet spot'.
"""
QUAD_TWH = 293.07; TCF_TWH = 302.0; TCF_MT_CH4 = 19.3; H2_LHV_KWH_KG = 33.33
GAL_GASOLINE_BTU = 120_238; GAL_DIESEL_BTU = 137_381; GAL_JET_BTU = 135_000; GAL_RESID_BTU = 149_690
GAL_PROPANE_BTU = 91_452; BTU_KWH = 3412.14

# ------------------------------------------------------------------------------------------------ 1. demand base
BASE = dict(
    gasoline_mbd=8.9,                 # [S] EIA 2025
    onroad_diesel_bgal=46.0,          # [A] EIA-consistent on-highway distillate
    rail_diesel_bgal=3.5, marine_distillate_bgal=2.0, marine_resid_mbd=0.18,   # [A]
    jet_mbd=1.70,                     # [A]
    pipeline_ng_quad=1.0,             # [A]
    farm_diesel_bgal=3.5,             # [S-order] EIA adjusted farm distillate sales ~3.4-3.8 bn gal (2004-07)
    construction_mining_diesel_bgal=2.8,   # [S-order] EIA off-highway construction ~2.3 bn gal + mining [A]
    industrial_trucks_bgal_dge=1.5,   # [A] forklifts, yard tractors, airport GSE (diesel+propane, diesel-gallon equiv.)
    eia_transport_quad_2024=28.1, transport_ghg_mt=1800.0,
    ethanol_prod_bgal_2025=16.49, ethanol_domestic_bgal_2025=14.34, ethanol_export_bgal_2025=2.18,   # [S]
)
# ------------------------------------------------------------------------------------------------ 2. 2050 end-use mix
# 're' = battery-electric with a biofuel range-extender generator ('backup generator'); re_fuel_share = share of that
# vehicle's energy delivered by the generator (the rest from the battery / charger).
ENDUSE = dict(
    ldv=dict(bev=0.95, fcev=0.02, liquid=0.03),
    hdv=dict(ers=0.45, bev=0.30, re=0.15, fcev=0.07, liquid=0.03), ers_on_wire=0.80,
    farm=dict(bev=0.30, re=0.50, liquid=0.20),
    construction=dict(bev=0.40, re=0.40, liquid=0.20),
    industrial=dict(bev=0.90, fcev=0.10),
    rail=dict(elec=0.60, re=0.20, liquid=0.20),
    air=dict(saf=0.97, h2=0.03),
    marine=dict(liquid=0.85, elec=0.05, h2=0.10),
    pipeline=dict(elec=0.60, gas=0.40),
    re_fuel_share=0.25,               # [A] 25% of range-extended vehicles' energy from the biofuel generator
    r_ldv_bev=0.33 / 1.41, r_ldv_fcev=0.55 / 1.41, r_hdv_elec=2.40 / 21.1, r_hdv_fcev=4.44 / 21.1,
    r_offroad_elec=0.36,              # [A] electric drive vs diesel in tractors/excavators (energy at meter)
    r_rail_elec=0.33, r_pipe_elec=0.35, r_fork_elec=0.30,
    service_growth_2050=1.00,
)
# ------------------------------------------------------------------------------------------------ 3. electricity
ELEC = dict(onshore_wind=55.0, solar=48.0, osw_fixed=95.0, osw_floating=115.0, lwr_smr=115.0,
            cf_onw=0.40, cf_pv=0.25, cf_fixed=0.45, cf_float=0.47,
            td_adder=30.0, vre_firming=20.0, charge_ldv=35.0, charge_hdv=25.0,
            cap_onw_twh=1800.0, cap_pv_twh=2400.0, cap_lwr_twh=1500.0,
            max_pv_share=0.40, min_firm_share=0.15,
            export_value=40.0, export_cap_twh=2500.0)   # [A] surplus sold to the rest of the U.S. grid at $40/MWh
# ------------------------------------------------------------------------------------------------ 4. reactors
HTGR = dict(outlet_c=750, mwt=800.0, cf=0.93, f_pyro=0.30, f_mid=0.075, f_dry=0.10, eta_cond=0.40, z_mid=0.30, z_dry=0.15,
            f_low_use=0.35, fom_kwt_yr=40.0, fuel_mwhth=9.0, life=60, wacc=0.07, kwe_per_kwt=0.40,
            capex_kwt=None)   # None -> fleet-average cost from the learning model below
REACTOR_COST = {   # INL literature review (BOAK OCC, FOAK multiplier, learning rate) [S]; IDC + owner's cost [A]
    "low":     dict(boak_kwe=4000.0, foak_mult=1.3, learning=0.15, idc=0.12),
    "central": dict(boak_kwe=6000.0, foak_mult=1.6, learning=0.10, idc=0.15),
    "high":    dict(boak_kwe=7000.0, foak_mult=2.1, learning=0.05, idc=0.20),
}
REACTOR_ANCHORS = {   # [S] public reference points used to sanity-check the learning model
    "Darlington BWRX-300, 4 x 300 MWe, all-in incl. interest": dict(total_bn_usd=15.1, mwe=1200),
    "Darlington BWRX-300 unit 1 (C$6.1 bn, ~C$20 M/MW)": dict(total_bn_usd=4.4, mwe=300),
    "DOE Liftoff advanced nuclear FOAK / NOAK overnight": dict(foak_kwe=9000, noak_kwe=3600),
}
PYRO = dict(kg_ch4_per_kg_h2=4.0 / 0.98, heat_kwh_kg=8.3, elec_kwh_kg=3.0, capex_kw_h2=1000.0, fom=0.04, life=25,
            c_per_h2=3.0, leak_upstream=0.015, upstream_co2_frac=0.05, h2_leak=0.02, gwp_h2=11.6, gwp_ch4=29.8,
            # v4.0 heat supply.  An Xe-100-class HTGR delivers helium at 750 C [S: X-energy], so it cannot supply the
            # reaction heat at 900-1,000 C.  "xe100": helium preheats the methane feed to ~700 C (sensible heat of CH4,
            # ~2.5 kWh per kg H2 [A: cp ~3.3 kJ/kg-K x 675 K x 4.08 kg CH4]); the remaining 5.8 kWh/kg (reaction enthalpy at
            # temperature, ~75-89 kJ/mol CH4, plus losses) comes from electric resistive/induction heaters at 95% [A],
            # costing USD 0.02/kg H2 extra capital [A].  "vhtr": a 950 C very-high-temperature reactor supplies all 8.3 kWh/kg.
            config="xe100", reactor_preheat_kwh_kg=2.5, boost_eff=0.95, boost_heater_cost_kg=0.02)
GAS = dict(price_mmbtu=3.5, delivery_mmbtu=0.5)
ELECTROLYSIS = dict(kwh_kg=52.0, capex_cost_kg=0.9)
# v3.0 post-gas hydrogen from reactor hubs.  HTSE (solid-oxide steam electrolysis): INL NOAK reference plant, 36.8 kWh_e and
# 6.4 kWh_th per kg [S: Wendt et al., INL/RPT-22-66117]; capital + O&M ~USD 0.8/kg from TCI ~USD 1,285/kW-dc [S: INL LWRS 2025], 7%/20 yr [A].
# Sulfur-iodine thermochemical cycle: ~45% heat-to-H2 (HHV) at 900-950 C [S: GA/Sandia; SRNL HyS flowsheets 44-48%];
# capital cost USD 1.5/kg is an assumption (no plant built) [A]; small pumping/separation electricity [A].
NUCLEAR_H2 = dict(htse=dict(kwh_e_kg=36.8, kwh_th_kg=6.4, capex_cost_kg=0.8),
                  sulfur_iodine=dict(kwh_e_kg=2.0, kwh_th_kg=39.4 / 0.45, capex_cost_kg=1.5))
# v3.0 nuclear fuel supply.  Once-through HTGR: 15.5% HALEU at ~160 GWd/tHM [A, Xe-100 class], 0.25% tails.
# Fast reactors in a closed cycle fission ~0.95 MWd/g of heavy metal; 2% reprocessing/fabrication loss [A].
# Resources: DOE depleted-uranium inventory ~470,000 tU [S: ANL/DOE]; world identified recoverable resources ~8.1 MtU
# [S: NEA/IAEA Uranium 2026]; seawater ~4.5e9 tU [S: Guidez & Gabriel 2016, EPJ N]. Thorium-232 breeds U-233 and is
# treated like U-238 in a closed breeding cycle (same fission energy per tonne) [A].
FUEL = dict(haleu_enrich=0.155, feed_assay=0.00711, tails=0.0025, haleu_burnup_gwd_t=160.0,
            fission_mwd_per_g=0.95, closed_cycle_loss=0.02,
            us_depleted_u_t=470_000.0, world_identified_u_t=8.1e6, seawater_u_t=4.5e9,
            us_thorium_t=600_000.0, world_thorium_t=6.4e6,
            # breeder start-up: ~10 t of fissile plutonium per GWe including out-of-core inventory [A]; U.S. commercial spent fuel
            # ~95,000 tHM [S: INL 2025 inventory] at ~1% plutonium [A]
            gwe_per_gwt=0.40, startup_pu_t_per_gwe=10.0, us_snf_thm=95_000.0, snf_pu_frac=0.01)   # thorium: identified resources [S: USGS Mineral Commodity Summaries 2026]
H2_DELIVERY = dict(vehicle=2.5, onsite=0.2, blend=0.3)
# ------------------------------------------------------------------------------------------------ 5. land biomass
# Terrestrial tiers: (name, cap Mt dry/yr, delivered USD/t). BT23: ~350 Mt unused now; >400 Mt more from crops [S]
BIOMASS = dict(tiers=[("Crop & forest residues, tier 1", 200.0, 65.0), ("Crop & forest residues, tier 2", 150.0, 85.0),
                      ("Perennial grasses / energy cane", 200.0, 100.0)], hhv_gj_t=18.5)
BAMBOO = dict(  # clumping species only (Dendrocalamus asper, Bambusa oldhamii, Guadua): lower invasion risk [S]
    yield_t_ha=(10.0, 15.0, 22.0),   # [A] dry t/ha/yr demonstrated / design / learning (25 t/ha reported in Brazil [S])
    establish_usd_ha=4000.0, establish_life=20, land_rent_usd_ha=250.0, harvest_usd_t=22.0, haul_usd_t=12.0,
    regions=[  # (region, max Mha suitable & available, note)
        ("Florida peninsula (former citrus, improved pasture)", 0.8, "frost-free; clumping species"),
        ("Gulf Coast plain: TX coastal bend to Mobile", 1.0, "USDA zone 9; wet marginal pasture"),
        ("Lower Rio Grande Valley TX", 0.3, "irrigation needed"),
        ("Coastal GA / SC lowlands", 0.4, "cold-hardy clumpers (Bambusa multiplex/ oldhamii) only"),
    ])
HEMP = dict(  # dual-purpose grain + stalk hemp in rotation, Northern Plains / Upper Midwest / KY
    seed_t_ha=0.9, oil_frac=0.30, stalk_t_ha=7.0, protein_frac_meal=0.33,  # [S-range] seed 0.5-1.6 t/ha; oil ~30%; stalk 4-12 t/ha
    cost_usd_ha=850.0, meal_value_usd_t=650.0, max_mha=4.0,               # [A]
    regions=[("North Dakota / Montana / South Dakota", 2.0), ("Minnesota / Wisconsin", 0.8), ("Kentucky / Tennessee", 0.6),
             ("Colorado / Nebraska", 0.6)])
ROUTES = dict(
    htl=dict(mwh_t=2.6, h2_kg_t=13.5, el_mwh_t=0.15, heat_mwh_t=0.35, cost_t=170.0, jet=0.45, ci_g_mj=12.0, char_t_t=0.12),
    pbtl=dict(mwh_t=4.44, h2_kg_t=110.0, el_mwh_t=0.60, heat_mwh_t=0.0, cost_t=290.0, jet=0.65, ci_g_mj=6.0, char_t_t=0.0),
    hefa=dict(mwh_t=10.1, h2_kg_t=35.0, el_mwh_t=0.10, heat_mwh_t=0.30, cost_t=1100.0 + 120.0, jet=0.55, ci_g_mj=35.0, cap_mt=12.0),
    hefa_conv_only=120.0,   # conversion cost for hemp oil (feedstock grown in-model)
    atj=dict(mwh_per_bgal=19.8, conv_per_bgal=0.5 * 1.1e9, jet=0.85, ci_g_mj=40.0, cap_bgal=25.0),
    ethanol=dict(mwh_per_bgal=22.37, corn_cost_per_bgal=1.9e9, corn_cap_bgal=20.0,
                 cellulosic_gal_per_t=85.0, cellulosic_conv_per_gal=1.25),   # [A] cellulosic ethanol from bamboo/residues
)
# ------------------------------------------------------------------------------------------------ 6. seaweed by region
# (key, wind field type, region, species, usable share, yields dem/design/learning t dry/ha/yr, DM, N%, land-N share,
#  GW in the large build, port distance km, map box lon0,lat0,w,h, colour key)
SEAWEED = [
    ("wa", "float", "Washington coast (Grays Harbor offshore)", "Sugar kelp Saccharina latissima, ribbon kelp Alaria marginata, bull kelp Nereocystis",
     0.40, (4.0, 8.0, 12.0), 0.12, 0.022, 0.06, 25.0, 60.0, (-125.9, 46.3, 0.8, 1.6), "cold_kelp"),
    ("or", "float", "Oregon (Coos Bay, Brookings)", "Giant kelp Macrocystis pyrifera + bull kelp Nereocystis",
     0.40, (4.0, 9.0, 13.0), 0.11, 0.020, 0.06, 35.0, 50.0, (-125.7, 42.1, 0.8, 2.1), "giant_kelp"),
    ("nca", "float", "Northern California (Humboldt, Mendocino)", "Giant kelp Macrocystis pyrifera",
     0.40, (5.0, 10.0, 14.0), 0.11, 0.020, 0.06, 35.0, 50.0, (-125.4, 39.0, 0.8, 2.0), "giant_kelp"),
    ("cca", "float", "Central California (Morro Bay)", "Giant kelp Macrocystis pyrifera",
     0.40, (5.0, 10.0, 14.0), 0.11, 0.020, 0.08, 25.0, 50.0, (-122.6, 34.9, 0.8, 1.4), "giant_kelp"),
    ("sca", "float", "Southern California Bight", "Giant kelp Macrocystis pyrifera, warm-tolerant strains, depth-cycled",
     0.35, (3.0, 7.0, 11.0), 0.11, 0.020, 0.15, 20.0, 60.0, (-120.3, 32.4, 1.6, 0.9), "giant_kelp_warm"),
    ("gom", "float", "Gulf of Maine", "Sugar kelp Saccharina latissima + winged kelp Alaria esculenta",
     0.50, (3.0, 7.0, 10.0), 0.12, 0.020, 0.15, 60.0, 60.0, (-70.3, 42.4, 2.2, 1.0), "cold_kelp"),
    ("sne", "fixed", "Southern New England", "Sugar kelp Saccharina latissima",
     0.55, (3.0, 6.0, 10.0), 0.12, 0.020, 0.20, 50.0, 50.0, (-71.6, 40.4, 1.8, 0.65), "cold_kelp"),
    ("nyb", "fixed", "New York Bight / New Jersey", "Winter sugar kelp + summer red Gracilaria tikvahiae (two crops)",
     0.55, (2.5, 6.0, 9.0), 0.12, 0.022, 0.35, 50.0, 45.0, (-73.4, 38.7, 1.4, 1.2), "kelp_red_rotation"),
    ("delmarva", "fixed", "Delmarva / Chesapeake mouth", "Winter sugar kelp + summer Gracilaria tikvahiae",
     0.55, (2.0, 5.0, 8.0), 0.12, 0.022, 0.40, 45.0, 45.0, (-74.9, 36.9, 1.1, 1.3), "kelp_red_rotation"),
    ("nc", "fixed", "Virginia Beach to Cape Hatteras", "Red Gracilaria tikvahiae + green Ulva lactuca (warm water)",
     0.55, (2.0, 5.0, 8.0), 0.14, 0.025, 0.30, 50.0, 45.0, (-75.6, 34.6, 1.0, 1.7), "red_green"),
    ("sab", "fixed", "South Atlantic Bight (SC, GA)", "Gracilaria + Ulva; capture of drifting Sargassum",
     0.55, (2.0, 5.0, 8.0), 0.14, 0.025, 0.25, 40.0, 60.0, (-80.5, 31.0, 1.4, 1.4), "red_green"),
    ("tx", "fixed", "Texas shelf (Galveston to Corpus Christi)", "Gracilaria + Ulva",
     0.50, (2.0, 5.0, 8.0), 0.14, 0.025, 0.35, 40.0, 50.0, (-96.6, 27.0, 2.2, 0.8), "red_green"),
    ("la", "fixed", "Louisiana / Mississippi plume", "Gracilaria + Ulva + Sargassum (nutrient-rich plume)",
     0.50, (3.0, 7.0, 10.0), 0.14, 0.025, 0.65, 40.0, 50.0, (-92.5, 27.9, 4.2, 0.75), "red_green"),
]
SEAWEED_PROCESS = dict(   # [C] whole-kelp HTL and kelp composition; dried gasification+FT with H2 is new [A]
    htl_mwh_t=1.9, htl_h2_kg_t=6.8, htl_el_mwh_t=0.12, htl_heat_mwh_t=0.30, htl_cost_t=260.0, htl_ci=15.0,
    pbtl_mwh_t=3.5, pbtl_h2_kg_t=90.0, pbtl_el_mwh_t=0.5, pbtl_dry_mwh_t=1.4, pbtl_cost_t=330.0, pbtl_ci=10.0,
    farm_cost_ref_t=380.0, ref_yield=15.0, shared_mooring_saving=0.15, mw_per_km2=4.0,
    p=0.003, k=0.045, n_rec=0.60, p_rec=0.80, k_rec=0.80, meal_share=0.05)
FERT_PRICE = dict(n=1000.0, p=1500.0, k=700.0)
LOGISTICS = dict(   # solar/wind-powered harvest and haul [A]
    gh_kwh_per_ha_pass=6.5,                 # Grid Harvester faired, 10% slurry: 33.9 MJ per 1.44-ha cycle [C]
    gh_unit_capex=6.0e6, gh_life=20, gh_pv_kw=150.0, gh_hours=4000.0,
    press_to_dm=0.30,                       # offshore screw-pressing before haul (press water returned to sea)
    vessel_t=2500.0, vessel_kn=10.0, vessel_kwh_tkm=0.06, vessel_capex=28.0e6, vessel_life=25, vessel_days=300,
    vessel_sail_share=0.25,                 # wingsail + deck PV share of propulsion energy
    vessel_om=0.04, load_hours=5.0,
    drone_km2=15.0, drone_capex=60_000.0, drone_life=5, drone_om_yr=8000.0,
)
# ------------------------------------------------------------------------------------------------ 7. carbon markets
CARBON_MARKETS = [
    ("Vehicle structures: methane-derived carbon nanotube/fibre in hybrid metal-composite bodies, H2 tanks", 0.76, 4000.0),
    ("Battery anode graphite (after graphitisation)", 1.5, 3000.0), ("Carbon black: tires & rubber (export incl.)", 3.0, 900.0),
    ("Specialty carbon (conductive additive, fibre precursors)", 0.4, 1500.0), ("Metallurgical: electrodes, recarburiser, Al anodes", 1.5, 400.0),
    ("Construction: asphalt & concrete additive", 8.0, 60.0), ("Soil amendment (methane-derived carbon; agronomic benefit unproven)", 10.0, 40.0),
    ("Permanent storage (mine voids, monofill)", 1e4, -25.0)]
CARBON_MARKET_SCALE = 1.0
# Vehicle-structure carbon: U.S. builds ~16 M cars and ~0.6 M trucks/buses a year [A]; hybrid steel/aluminium + CFRP/CNT
# bodies at ~40 kg carbon per car and ~150 kg per truck, plus Type IV hydrogen tanks (~60 kg per FCEV car, ~400 kg per
# FCEV truck) -> ~0.76 Mt/yr, 3-4x the 2025 world carbon-fibre market (224.5 kt [S]).  Net value after spinning,
# sizing and moulding: $4,000/t central [A] (virgin fibre sells ~$24-35/kg today [S]).
VEHICLE_CARBON = dict(cars_m=16.0, trucks_m=0.6, kg_car=40.0, kg_truck=150.0, fcev_car_tank_kg=60.0, fcev_truck_tank_kg=400.0,
                      mass_saving_car=0.10, mass_saving_truck=0.06, energy_per_mass=0.45)   # energy falls ~0.45% per 1% mass [A]
# ------------------------------------------------------------------------------------------------ 8. vehicles
VEH = dict(ldv_stock_m=285.0, ldv_bev_net_usd_yr=100.0, ldv_fcev_net_usd_yr=900.0,
           ers_trucks_m=1.4, fcev_trucks_m=0.25, bev_trucks_m=2.8, re_trucks_m=0.6,
           ers_truck_net_usd_yr=5000.0, fcev_truck_net_usd_yr=10000.0, bev_truck_net_usd_yr=2500.0, re_truck_net_usd_yr=4000.0,
           tractors_m=2.0, tractor_net_usd_yr=1500.0, constr_m=0.9, constr_net_usd_yr=3000.0, forklifts_m=1.0, forklift_net_usd_yr=-300.0,
           ers_km=40000.0, ers_capex_m_per_km=3.5, ers_om=0.025, ers_life=40,
           rail_elec_capex_bn=80.0, rail_life=40, farm_charging_bn_yr=3.0, e85_kit_usd=900.0)
PRICES = {"late_2025": dict(gasoline=3.05, diesel=3.82, jet=2.14, resid=1.90),
          "nov_2026": dict(gasoline=3.90, diesel=6.05, jet=3.62, resid=2.80)}
OFFROAD_DIESEL_PRICE = {"late_2025": 3.30, "nov_2026": 5.40}   # [A] dyed/untaxed off-road diesel ~ retail minus road taxes
TAX = dict(gasoline=0.57, diesel=0.62, jet=0.044, resid=0.0)
PETRO_CI = dict(gasoline=93.0, diesel=95.0, jet=89.0, resid=96.0, ng=70.0)
ETHANOL_CI = dict(today=55.0, ccs=30.0)
# ------------------------------------------------------------------------------------------------ 9. gas resource
NG = dict(us_proved_tcf=583.9, us_trr_tcf=3870.0, us_dry_prod_tcf_2025=39.0, us_consumption_bcfd_2025=91.8,
          us_lng_bcfd_2025=15.0, mexico_pipe_bcfd=7.5, canada_imports_bcfd_2025=8.6, canada_remaining_tcf=1105.0,
          canada_prod_bcfd_2025=19.1, canada_domestic_bcfd=12.5, canada_lng_bcfd_2035=4.0, resch_comm_tcf=9.0,
          rp_floor_years=15.0)
# ------------------------------------------------------------------------------------------------ 10. food from the cascade
FOOD = dict(
    greenhouse_heat_kwh_m2=250.0,        # [S-range] 46-357 kWh/m2/yr heated tomato houses; U.S. northern sites ~250 [A]
    greenhouse_yield_kg_m2=45.0,         # [S] Dutch glasshouse tomatoes ~50 kg/m2 (2004) -> 45 mixed crops [A]
    greenhouse_market_mt=8.0,            # [A] U.S. tomatoes, cucumbers, peppers, leafy greens that could shift to greenhouses
    greenhouse_value_usd_t=1800.0, kcal_per_kg_veg=200.0,
    ras_heat_kwh_kg=4.0, ras_market_mt=1.0, ras_value_usd_t=7000.0, kcal_per_kg_fish=1200.0,   # warm-water fish & shrimp RAS
    asparagopsis_heat_mwh_t=25.0,
    grain_dry_mwh_t=0.08, grain_near_hub_mt=60.0, grain_value_saved_usd_mwh=35.0,   # [A] corn/soy drying near hubs
    kcal_per_person_day=2200.0, hemp_kcal_per_kg_seed=5500.0,
    vegetable_edible_fraction=0.85, fish_shrimp_edible_fraction=0.60,  # [A] scenario factors, not measured national edible yields
)
AG = dict(head_feedlot_m=14.0, head_dairy_m=9.3, head_grazing_m=55.0, dmi_kg_d=dict(feedlot=10.0, dairy=24.0, grazing=11.0),
          dose_dm=0.0025, cut=dict(feedlot=0.60, dairy=0.60, grazing=0.35), adoption=dict(feedlot=0.8, dairy=0.8, grazing=0.3),
          enteric_mt=187.1, enteric_share=dict(feedlot=0.12, dairy=0.25, grazing=0.60),
          tank_yield_t_ha=30.0, tank_cost_t=4000.0)
