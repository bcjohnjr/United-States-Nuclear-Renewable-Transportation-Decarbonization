"""U.S. transport-energy system, v2: HTGR heat cascade + methane pyrolysis + large offshore wind with region-specific
seaweeds + electric highways + bamboo, hemp, residues and ethanol-to-jet + food from the cascade.  USD 2026.

    python3 us2_model.py [n_monte_carlo]      -> *.json, *.csv in this folder

Annual least-cost linear programme (HiGHS via SciPy) for 2050 plus accounting modules.  Screening model, not a forecast.
"""
from __future__ import annotations
import copy, json, math, csv
from pathlib import Path
import numpy as np
from scipy.optimize import linprog

import us2_inputs as I
from grid_harvester import fleet_sizing, energy as gh_energy, turning as gh_turning

OUT = Path(__file__).resolve().parent  # flat layout: results are written next to the scripts
crf = lambda r, n: r / (1 - (1 + r) ** -n)
DGE_TWH = lambda bgal: bgal * 1e9 * I.GAL_DIESEL_BTU / I.BTU_KWH / 1e9


def default_params():
    names = ["BASE", "ENDUSE", "ELEC", "HTGR", "PYRO", "GAS", "ELECTROLYSIS", "H2_DELIVERY", "BIOMASS", "BAMBOO", "HEMP",
             "ROUTES", "SEAWEED_PROCESS", "LOGISTICS", "VEH", "FOOD", "NUCLEAR_H2", "CROP_RESIDUE"]
    p = {n: copy.deepcopy(getattr(I, n)) for n in names}
    p["CARBON"] = [list(m) for m in I.CARBON_MARKETS]
    p["yield_level"] = 1; p["reactor_case"] = "central"; p["osw_scale"] = 1.0
    return p


# ============================================================================================= reactor cost (learning)
def reactor_cost(case="central", n_units=500, mwe_per_unit=80.0):
    """Wright's-law learning from a FOAK unit: cost(n) = FOAK * n^b, b = log2(1 - learning rate)."""
    c = I.REACTOR_COST[case]
    foak = c["boak_kwe"] * c["foak_mult"]
    b = math.log2(1 - c["learning"])
    n = max(n_units, 1)
    avg = foak * (n ** (b + 1)) / ((b + 1) * n)        # continuous average of n^b over 1..n
    unit = lambda k: foak * k ** b
    kwe_to_kwt = I.HTGR["kwe_per_kwt"]
    return dict(case=case, n_units=n, foak_kwe=foak, unit10_kwe=unit(10), unit100_kwe=unit(100), last_kwe=unit(n),
                fleet_avg_kwe=avg, fleet_avg_kwe_with_idc=avg * (1 + c["idc"]),
                fleet_avg_kwt_with_idc=avg * (1 + c["idc"]) * kwe_to_kwt, learning=c["learning"],
                fleet_capex_bn=avg * (1 + c["idc"]) * n * mwe_per_unit * 1000 / 1e9)


# ============================================================================================= demand
def base_demand(p):
    B = p["BASE"]; g = p["ENDUSE"]["service_growth_2050"]
    d = dict(ldv=B["gasoline_mbd"] * 42e6 * 365 * I.GAL_GASOLINE_BTU / I.BTU_KWH / 1e9,
             hdv=DGE_TWH(B["onroad_diesel_bgal"]), rail=DGE_TWH(B["rail_diesel_bgal"]),
             air=B["jet_mbd"] * 42e6 * 365 * I.GAL_JET_BTU / I.BTU_KWH / 1e9,
             marine=(B["marine_distillate_bgal"] * 1e9 * I.GAL_DIESEL_BTU + B["marine_resid_mbd"] * 42e6 * 365 * I.GAL_RESID_BTU) / I.BTU_KWH / 1e9,
             pipeline=B["pipeline_ng_quad"] * I.QUAD_TWH, farm=DGE_TWH(B["farm_diesel_bgal"]),
             construction=DGE_TWH(B["construction_mining_diesel_bgal"]), industrial=DGE_TWH(B["industrial_trucks_bgal_dge"]))
    return {k: v * g for k, v in d.items()}, d


def enduse_2050(p):
    d, base = base_demand(p); E = p["ENDUSE"]; rf = E["re_fuel_share"]
    VC = I.VEHICLE_CARBON; lw = p.get("lightweight", True)
    f_car = 1 - VC["mass_saving_car"] * VC["energy_per_mass"] if lw else 1.0
    f_trk = 1 - VC["mass_saving_truck"] * VC["energy_per_mass"] if lw else 1.0
    el, h2, liq = {}, {}, {}
    el["ldv"] = d["ldv"] * E["ldv"]["bev"] * E["r_ldv_bev"] * f_car; h2["ldv"] = d["ldv"] * E["ldv"]["fcev"] * E["r_ldv_fcev"] * f_car
    liq["ldv"] = d["ldv"] * E["ldv"]["liquid"]
    H = E["hdv"]; re_ = E["r_hdv_elec"] * f_trk
    el["hdv_ers_wire"] = d["hdv"] * H["ers"] * E["ers_on_wire"] * re_
    el["hdv_ers_battery"] = d["hdv"] * H["ers"] * (1 - E["ers_on_wire"]) * re_
    el["hdv_bev"] = d["hdv"] * H["bev"] * re_
    el["hdv_re"] = d["hdv"] * H["re"] * (1 - rf) * re_
    h2["hdv"] = d["hdv"] * H["fcev"] * E["r_hdv_fcev"]
    liq["hdv"] = d["hdv"] * (H["liquid"] + H["re"] * rf)
    for seg in ("farm", "construction"):
        S = E[seg]
        el[seg] = d[seg] * (S["bev"] + S["re"] * (1 - rf)) * E["r_offroad_elec"]
        liq[seg] = d[seg] * (S["liquid"] + S["re"] * rf)
    el["industrial"] = d["industrial"] * E["industrial"]["bev"] * E["r_fork_elec"]
    h2["industrial"] = d["industrial"] * E["industrial"]["fcev"] * 0.55
    R = E["rail"]
    el["rail"] = d["rail"] * (R["elec"] + R["re"] * (1 - rf)) * E["r_rail_elec"]
    liq["rail"] = d["rail"] * (R["liquid"] + R["re"] * rf)
    h2["air"] = d["air"] * E["air"]["h2"]; liq["air"] = d["air"] * E["air"]["saf"]
    el["marine"] = d["marine"] * E["marine"]["elec"] * 0.40; h2["marine"] = d["marine"] * E["marine"]["h2"]
    liq["marine"] = d["marine"] * E["marine"]["liquid"]
    el["pipeline"] = d["pipeline"] * E["pipeline"]["elec"] * E["r_pipe_elec"]
    return dict(demand=d, base=base, el=el, h2_twh=h2, liq=liq, gas_resid_twh=d["pipeline"] * E["pipeline"]["gas"],
                el_total=sum(el.values()), h2_mt_direct=sum(h2.values()) / I.H2_LHV_KWH_KG, liq_total=sum(liq.values()),
                jet=liq["air"])


def blend_h2(vol_frac):
    if vol_frac <= 0:
        return dict(h2_mt=0.0, gas_displaced_tcf=0.0, energy_share=0.0, co2_avoided_burner_mt=0.0)
    share = vol_frac * 10.8 / (vol_frac * 10.8 + (1 - vol_frac) * 35.8)
    h2_twh = share * I.NG["resch_comm_tcf"] * I.TCF_TWH * 0.90
    disp = h2_twh / (I.TCF_TWH * 0.90)
    return dict(h2_mt=h2_twh / I.H2_LHV_KWH_KG, gas_displaced_tcf=disp, energy_share=share, co2_avoided_burner_mt=disp * I.TCF_MT_CH4 * 44 / 16)


# ============================================================================================= hub
def hub(p, capex_kwt):
    H = p["HTGR"]; hrs = 8760 * H["cf"]
    q_pyro, q_mid, q_dry = H["mwt"] * H["f_pyro"], H["mwt"] * H["f_mid"], H["mwt"] * H["f_dry"]
    steam = H["mwt"] - q_pyro
    mwe = H["eta_cond"] * steam - H["z_mid"] * q_mid - H["z_dry"] * q_dry
    reject = steam - mwe - q_mid - q_dry
    cost = (H["mwt"] * 1000 * capex_kwt * crf(H["wacc"], H["life"]) + H["mwt"] * 1000 * H["fom_kwt_yr"] + H["mwt"] * hrs * H["fuel_mwhth"]) / 1e9
    return dict(mwt=H["mwt"], q_pyro_mw=q_pyro, q_mid_mw=q_mid, q_dry_mw=q_dry, mwe=mwe, reject_mw=reject,
                low_used_mw=reject * H["f_low_use"], pyro_twh=q_pyro * hrs / 1e6, mid_twh=q_mid * hrs / 1e6,
                dry_twh=q_dry * hrs / 1e6, el_twh=mwe * hrs / 1e6, low_twh=reject * H["f_low_use"] * hrs / 1e6,
                cost_bn=cost, capex_kwt=capex_kwt)


def vhtr_params(p):
    """Sensitivity: a 950 C very-high-temperature reactor at the same cost supplies all pyrolysis heat (and S-I heat)."""
    p = copy.deepcopy(p); p["HTGR"]["outlet_c"] = 950; p["PYRO"]["config"] = "vhtr"; return p


def breeder_params(p, capex_mult=1.25, fuel_mwhth=15.0):
    """Sensitivity: hubs built as fast/thorium breeders in a closed fuel cycle (capital-cost multiplier and fuel-cycle cost [A])."""
    p = copy.deepcopy(p); p["capex_mult"] = capex_mult; p["HTGR"]["fuel_mwhth"] = fuel_mwhth; return p


def sustainable_fission_params(p, nuclear_only=False, capex_mult=1.0, fuel_mwhth=12.0):
    """Theoretical future: mature breeder reactors in a closed fuel cycle (fast-spectrum uranium or thorium), running at
    950 C (gas-cooled fast reactor concept) at the HTGR hubs' cost.  No natural gas.  Hubs supply electricity, hydrogen
    (steam electrolysis or sulfur-iodine) and process heat for HTL with biocrude upgrading.  nuclear_only removes
    wind, solar and offshore wind, and light-water SMRs, so every MWh and kg of H2 comes from the breeder hubs."""
    p = vhtr_params(post_gas_params(p)); p = breeder_params(p, capex_mult, fuel_mwhth)
    p["ELEC"]["cap_lwr_twh"] = 0.0; p["HTGR"]["return_unused_steam"] = True
    if nuclear_only: p["ELEC"]["allow_vre"] = False
    return p


def pyro_reactor_heat(p):
    """kWh of reactor heat per kg H2 drawn from the hub's top tier (helium) by pyrolysis."""
    P = p["PYRO"]; return P["heat_kwh_kg"] if P.get("config") == "vhtr" else P["reactor_preheat_kwh_kg"]


def pyro_elec(p):
    """kWh of electricity per kg H2: process electricity plus, for 750 C reactors, electric boost heating."""
    P = p["PYRO"]; boost = 0.0 if P.get("config") == "vhtr" else (P["heat_kwh_kg"] - P["reactor_preheat_kwh_kg"]) / P["boost_eff"]
    return P["elec_kwh_kg"] + boost


def pyro_cost_per_kg(p):
    P = p["PYRO"]; kw = I.H2_LHV_KWH_KG / (8760 * 0.93)
    plant = kw * P["capex_kw_h2"] * (crf(0.07, P["life"]) + P["fom"]) + (0.0 if P.get("config") == "vhtr" else P.get("boost_heater_cost_kg", 0.0))
    gas = P["kg_ch4_per_kg_h2"] * 55.5 / 1055.06 * (p["GAS"]["price_mmbtu"] + p["GAS"]["delivery_mmbtu"])
    return plant, gas


def h2_ci(p, elec_ci=0.0):
    P = p["PYRO"]; ch4 = P["kg_ch4_per_kg_h2"]; L = P["leak_upstream"]
    return ch4 * L / (1 - L) * P["gwp_ch4"] + ch4 * P["upstream_co2_frac"] * 44 / 16 + (ch4 - 4.0) * 44 / 16 + P["h2_leak"] * P["gwp_h2"] + pyro_elec(p) * elec_ci


# ============================================================================================= seaweed logistics & cost
def seaweed_zone_economics(p, z):
    """Cost per dry tonne for one zone: farm (incl. drones), solar/wind Grid Harvesters, battery-sail haul vessels."""
    S, L = p["SEAWEED_PROCESS"], p["LOGISTICS"]
    y = z[5][p["yield_level"]]; dm = z[6]; km = z[10]
    farm = S["farm_cost_ref_t"] * (0.4 + 0.6 * S["ref_yield"] / y) * (1 - S["shared_mooring_saving"])
    # the Canadian reference farm cost already includes harvest and a 40 km haul: replace those with explicit logistics
    farm_ex = farm * 0.80
    ha_per_t = 1 / y
    # Grid Harvester: area duty with 2 passes/yr (perennial giant kelp 3); PV/wind on the unit covers its ~6.5 kWh/ha
    passes = 3.0 if "giant" in z[12] else (2.0 if "rotation" in z[12] or "red" in z[12] else 1.0)
    unit_ha_yr = 3.333 * L["gh_hours"]
    gh_cost_t = (L["gh_unit_capex"] * (crf(0.07, L["gh_life"]) + 0.05)) * ha_per_t * passes / unit_ha_yr
    gh_kwh_t = L["gh_kwh_per_ha_pass"] * passes * ha_per_t
    # press offshore to 30% DM, then haul by battery + wingsail vessel; charge at the wind farm substation
    wet_t = 1 / L["press_to_dm"]
    trip_h = 2 * km / (L["vessel_kn"] * 1.852) + L["load_hours"]
    trips_yr = L["vessel_days"] * 24 / trip_h
    t_dry_per_vessel_yr = trips_yr * L["vessel_t"] * L["press_to_dm"]
    vessel_cost_t = L["vessel_capex"] * (crf(0.07, L["vessel_life"]) + L["vessel_om"]) / t_dry_per_vessel_yr
    vessel_kwh_t = wet_t * 2 * km * L["vessel_kwh_tkm"] * (1 - L["vessel_sail_share"]) * 0.6   # empty return ~ 20% of laden
    battery_mwh = L["vessel_t"] * km * L["vessel_kwh_tkm"] * 1.3 / 1000
    drone_cost_t = ha_per_t / 100 / L["drone_km2"] * (L["drone_capex"] * crf(0.07, L["drone_life"]) + L["drone_om_yr"])
    fert = (z[7] * S["n_rec"] * I.FERT_PRICE["n"] + S["p"] * S["p_rec"] * I.FERT_PRICE["p"] + S["k"] * S["k_rec"] * I.FERT_PRICE["k"])
    total = farm_ex + gh_cost_t + vessel_cost_t + drone_cost_t
    return dict(yield_t_ha=y, farm_t=farm_ex, harvester_t=gh_cost_t, vessel_t=vessel_cost_t, drones_t=drone_cost_t,
                fert_credit_t=fert, biomass_cost_t=total, harvester_kwh_t=gh_kwh_t, vessel_kwh_t=vessel_kwh_t,
                vessel_battery_mwh=battery_mwh, t_dry_per_vessel_yr=t_dry_per_vessel_yr, passes=passes,
                ha_per_drone=L["drone_km2"] * 100)


def bamboo_cost_t(p):
    B = p["BAMBOO"]; y = B["yield_t_ha"][p["yield_level"]]
    return (B["establish_usd_ha"] * crf(0.07, B["establish_life"]) + B["land_rent_usd_ha"]) / y + B["harvest_usd_t"] + B["haul_usd_t"], y


# ============================================================================================= LP
HX_EFF, HX_COST = 0.95, 2.0   # flexible-heat sensitivity: heat-exchanger effectiveness and cost (USD/MWh_th) [A]


def solve(p, scenario="design", blend_vol=0.0, capex_kwt=2000.0, osw_scale=None, kelp_force=None, allow_ely=None, flex_heat=False, post_gas=False, allow_si=False, fixed_hubs=None):
    if osw_scale is None: osw_scale = p["osw_scale"] if scenario.startswith("design") else 0.0
    if kelp_force is None: kelp_force = scenario.startswith("design")
    if allow_ely is None: allow_ely = not scenario.startswith("design")
    eu = enduse_2050(p); E = p["ELEC"]; R = p["ROUTES"]; S = p["SEAWEED_PROCESS"]; hb = hub(p, capex_kwt); bl = blend_h2(blend_vol)
    pl, pg = pyro_cost_per_kg(p); bam_cost, bam_y = bamboo_cost_t(p); HM = p["HEMP"]
    Z = I.SEAWEED; zec = {z[0]: seaweed_zone_economics(p, z) for z in Z}
    names = ["onw", "pv", "lwr", "export", "hubs", "hp2e", "h_pyro", "h_ely", "bamboo", "hemp_mha",
             "htl", "pbtl", "cel", "corn_etoh", "atj", "etoh_ldv", "hefa", "hemp_oil_fuel", "e_heat", "e_dry", "heat_sold", "t2mid", "t2dry", "m2dry", "h_htse", "h_si", "m2e", "d2e"]
    # A biomass variable for every explicitly costed residue tier. The normal
    # unmodified model still has its three historic tiers.
    biomass_keys = [f"b{j+1}" for j in range(len(p["BIOMASS"]["tiers"]))]
    names += biomass_keys
    names += [f"osw_{z[0]}" for z in Z] + [f"kh_{z[0]}" for z in Z] + [f"kp_{z[0]}" for z in Z]
    names += [f"c{j}" for j in range(len(p["CARBON"]))] + ["cover_c"]
    ix = {n: i for i, n in enumerate(names)}; nv = len(names); c = np.zeros(nv)
    firm = E["vre_firming"]
    c[ix["onw"]] = (E["onshore_wind"] + firm) / 1e3; c[ix["pv"]] = (E["solar"] + 1.25 * firm) / 1e3; c[ix["lwr"]] = E["lwr_smr"] / 1e3
    c[ix["export"]] = -E["export_value"] / 1e3
    c[ix["hubs"]] = hb["cost_bn"]; c[ix["h_pyro"]] = pl + pg; c[ix["h_ely"]] = p["ELECTROLYSIS"]["capex_cost_kg"]
    for j, (nm, cap, pr) in enumerate(p["BIOMASS"]["tiers"]): c[ix[f"b{j+1}"]] = pr / 1e3
    c[ix["bamboo"]] = bam_cost / 1e3
    CR = p["CROP_RESIDUE"]
    c[ix["cover_c"]] = (CR["cover_crop_stable_carbon_cost_usd_t_c"] / 1e3) if CR["enabled"] else 0.0
    c[ix["hemp_mha"]] = (HM["cost_usd_ha"] - HM["seed_t_ha"] * (1 - HM["oil_frac"]) * HM["meal_value_usd_t"]) * 1e6 / 1e9
    c[ix["htl"]] = R["htl"]["cost_t"] / 1e3; c[ix["pbtl"]] = R["pbtl"]["cost_t"] / 1e3
    c[ix["cel"]] = R["ethanol"]["cellulosic_gal_per_t"] * R["ethanol"]["cellulosic_conv_per_gal"] / 1e3
    c[ix["corn_etoh"]] = R["ethanol"]["corn_cost_per_bgal"] / 1e9
    c[ix["atj"]] = R["atj"]["conv_per_bgal"] / 1e9
    c[ix["hefa"]] = R["hefa"]["cost_t"] / 1e3; c[ix["hemp_oil_fuel"]] = R["hefa_conv_only"] / 1e3
    c[ix["e_heat"]] = 2.0 / 1e3; c[ix["e_dry"]] = 8.0 / 1e3
    # v2.3: decision-dependent terms formerly added only after the solve are now in the objective
    c[ix["heat_sold"]] = -8.0 / 1e3
    # v2.4 flexible heat dispatch (sensitivity): top-tier helium heat may be stepped down to process steam or drying,
    # and process steam to drying, through heat exchangers (95% effective, USD 2/MWh)
    for k in ("t2mid", "t2dry", "m2dry"): c[ix[k]] = HX_COST / 1e3
    # v3.0 post-gas hydrogen routes from reactor hubs (only when post_gas=True)
    c[ix["h_htse"]] = p["NUCLEAR_H2"]["htse"]["capex_cost_kg"]; c[ix["h_si"]] = p["NUCLEAR_H2"]["sulfur_iodine"]["capex_cost_kg"]                                   # low-grade heat sold to food uses, USD 8/MWh
    onsite = p["H2_DELIVERY"]["onsite"]                               # on-site H2 delivery to refineries, USD bn/Mt
    for k, h in (("htl", R["htl"]["h2_kg_t"]), ("pbtl", R["pbtl"]["h2_kg_t"]), ("hefa", R["hefa"]["h2_kg_t"]), ("hemp_oil_fuel", R["hefa"]["h2_kg_t"])):
        c[ix[k]] += onsite * h / 1e3
    for z in Z:
        typ = z[1]; lcoe = E["osw_fixed"] if typ == "fixed" else E["osw_floating"]
        c[ix[f"osw_{z[0]}"]] = (lcoe + 0.5 * firm) / 1e3
        e = zec[z[0]]
        c[ix[f"kh_{z[0]}"]] = (e["biomass_cost_t"] - e["fert_credit_t"] + S["htl_cost_t"]) / 1e3
        c[ix[f"kp_{z[0]}"]] = (e["biomass_cost_t"] - e["fert_credit_t"] + S["pbtl_cost_t"]) / 1e3
        c[ix[f"kh_{z[0]}"]] += onsite * S["htl_h2_kg_t"] / 1e3; c[ix[f"kp_{z[0]}"]] += onsite * S["pbtl_h2_kg_t"] / 1e3
    for j, (nm, cap, val) in enumerate(p["CARBON"]): c[ix[f"c{j}"]] = -val / 1e3
    A, b, Aeq, beq = [], [], [], []
    def row(d):
        r = np.zeros(nv)
        for k, v in d.items(): r[ix[k]] += v
        return r
    le = lambda d, rhs: (A.append(row(d)), b.append(rhs))
    eq = lambda d, rhs: (Aeq.append(row(d)), beq.append(rhs))
    osw = [f"osw_{z[0]}" for z in Z]; kh = [f"kh_{z[0]}" for z in Z]; kp = [f"kp_{z[0]}" for z in Z]
    # electricity balance
    load = {"h_pyro": pyro_elec(p), "h_ely": p["ELECTROLYSIS"]["kwh_kg"], "h_htse": p["NUCLEAR_H2"]["htse"]["kwh_e_kg"],
            "h_si": p["NUCLEAR_H2"]["sulfur_iodine"]["kwh_e_kg"], "htl": R["htl"]["el_mwh_t"],
            "pbtl": R["pbtl"]["el_mwh_t"], "hefa": R["hefa"]["el_mwh_t"], "hemp_oil_fuel": R["hefa"]["el_mwh_t"], "e_heat": 1.0,
            "e_dry": 1.0, "export": 1.0, "cel": 0.25}
    for z in Z:
        e = zec[z[0]]
        load[f"kh_{z[0]}"] = S["htl_el_mwh_t"] + (e["harvester_kwh_t"] * 0 + e["vessel_kwh_t"]) / 1000
        load[f"kp_{z[0]}"] = S["pbtl_el_mwh_t"] + e["vessel_kwh_t"] / 1000
    r_ = dict(load)
    for s_ in ["onw", "pv", "lwr"] + osw: r_[s_] = r_.get(s_, 0) - 1
    r_["hubs"] = -hb["el_twh"]; r_["hp2e"] = -p["HTGR"]["eta_cond"]
    r_["m2e"] = -p["HTGR"]["z_mid"]; r_["d2e"] = -p["HTGR"]["z_dry"]      # unused extraction steam left in the turbine
    le(r_, -eu["el_total"])
    sup = ["onw", "pv", "lwr"] + osw
    r_ = {s_: -E["max_pv_share"] for s_ in sup}; r_["pv"] += 1; r_["hubs"] = -E["max_pv_share"] * hb["el_twh"]; le(r_, 0.0)
    le({"lwr": -1, "hubs": -hb["el_twh"], "hp2e": -p["HTGR"]["eta_cond"]}, -E["min_firm_share"] * eu["el_total"])
    # heat
    le({"h_pyro": pyro_reactor_heat(p), "hp2e": 1.0, "hubs": -hb["pyro_twh"], "t2mid": 1.0, "t2dry": 1.0,
        "h_si": p["NUCLEAR_H2"]["sulfur_iodine"]["kwh_th_kg"]}, 0.0)
    r_ = {"htl": R["htl"]["heat_mwh_t"], "hefa": R["hefa"]["heat_mwh_t"], "hemp_oil_fuel": R["hefa"]["heat_mwh_t"], "hubs": -hb["mid_twh"], "e_heat": -0.98,
          "t2mid": -HX_EFF, "m2dry": 1.0, "m2e": 1.0}
    for k in kh: r_[k] = S["htl_heat_mwh_t"]
    le(r_, 0.0)
    r_ = {k: S["pbtl_dry_mwh_t"] for k in kp}; r_["hubs"] = -hb["dry_twh"]; r_["e_dry"] = -2.5; r_["cel"] = 0.6; r_["t2dry"] = -HX_EFF; r_["m2dry"] = -HX_EFF
    r_["h_htse"] = p["NUCLEAR_H2"]["htse"]["kwh_th_kg"]; r_["d2e"] = 1.0; le(r_, 0.0)     # HTSE steam raised from the 130-180 C tier
    # hydrogen
    r_ = {"h_pyro": -1, "h_ely": -1, "h_htse": -1, "h_si": -1, "htl": R["htl"]["h2_kg_t"] / 1e3, "pbtl": R["pbtl"]["h2_kg_t"] / 1e3,
          "hefa": R["hefa"]["h2_kg_t"] / 1e3, "hemp_oil_fuel": R["hefa"]["h2_kg_t"] / 1e3}
    for k in kh: r_[k] = S["htl_h2_kg_t"] / 1e3
    for k in kp: r_[k] = S["pbtl_h2_kg_t"] / 1e3
    le(r_, -(eu["h2_mt_direct"] + bl["h2_mt"]))
    # liquids (TWh) and jet
    mw = {"htl": R["htl"]["mwh_t"], "pbtl": R["pbtl"]["mwh_t"], "hefa": R["hefa"]["mwh_t"], "hemp_oil_fuel": R["hefa"]["mwh_t"],
          "atj": R["atj"]["mwh_per_bgal"], "etoh_ldv": R["ethanol"]["mwh_per_bgal"]}
    jf = {"htl": R["htl"]["jet"], "pbtl": R["pbtl"]["jet"], "hefa": R["hefa"]["jet"], "hemp_oil_fuel": R["hefa"]["jet"], "atj": R["atj"]["jet"], "etoh_ldv": 0.0}
    for k in kh: mw[k] = S["htl_mwh_t"]; jf[k] = R["htl"]["jet"]
    for k in kp: mw[k] = S["pbtl_mwh_t"]; jf[k] = R["pbtl"]["jet"]
    le({k: -v for k, v in mw.items()}, -eu["liq_total"])
    le({k: -mw[k] * jf[k] for k in mw}, -eu["jet"])
    le({"etoh_ldv": mw["etoh_ldv"]}, eu["liq"]["ldv"])
    # ethanol balance: corn + cellulosic = atj + direct
    eq({"corn_etoh": 1, "cel": R["ethanol"]["cellulosic_gal_per_t"] / 1e3, "atj": -1, "etoh_ldv": -1}, 0.0)
    le({"corn_etoh": 1}, R["ethanol"]["corn_cap_bgal"])
    # land biomass pool (Mt): tiers + bamboo + hemp stalk -> htl, pbtl, cellulosic ethanol
    r_bio={"htl":1,"pbtl":1,"cel":1,"bamboo":-1,"hemp_mha":-HM["stalk_t_ha"]}
    for k in biomass_keys:r_bio[k]=-1
    eq(r_bio,0.0)
    for j,(nm,cap,pr) in enumerate(p["BIOMASS"]["tiers"]):le({f"b{j+1}":1},cap)
    if CR["enabled"]:
        crop_spec=CR.get("feedstocks") or [CR]
        crop_keys=biomass_keys[:len(crop_spec)]
        assert len(crop_spec)<=len(biomass_keys)
        le({**{k:1 for k in crop_keys},"htl":-1},0.0)
        le({k:-1 for k in crop_keys},-CR["collect_min_mt"])
        le({k:1 for k in crop_keys},CR["cap_mt"])
        for group,group_cap in CR.get("group_caps_mt",{}).items():
            group_keys=[crop_keys[i] for i,f in enumerate(crop_spec) if f.get("group")==group]
            if group_keys:le({k:1 for k in group_keys},group_cap)
        soil_market=next(j for j,(nm,cap,val) in enumerate(p["CARBON"]) if nm.startswith("Soil amendment"))
        char_stable=R["htl"]["char_t_t"]*CR["hydrochar_c_fraction"]*CR["hydrochar_stable_fraction"]
        # A plant-specific SOC replacement need, with hydrochar C credited
        # only at an assumed stable-equivalent fraction. The balance can
        # be met by a separately charged pyrolysis-carbon allocation or
        # biological cover crops; no raw HTL effluent is land-spread.
        soilrow={k:max(0.0,f.get("stable_soc_c_t_per_dry_t",CR["stable_soc_c_t_per_dry_t"])-char_stable) for k,f in zip(crop_keys,crop_spec)}
        soilrow[f"c{soil_market}"]=-CR["methane_carbon_stable_fraction"]
        soilrow["cover_c"]=-1.0
        le(soilrow,0.0)

    le({"bamboo": 1}, sum(r[1] for r in p["BAMBOO"]["regions"]) * bam_y)
    le({"hemp_mha": 1}, HM["max_mha"])
    le({"hemp_oil_fuel": 1, "hemp_mha": -HM["seed_t_ha"] * HM["oil_frac"]}, 0.0)
    le({"hefa": 1}, R["hefa"]["cap_mt"])
    # seaweed tied to wind area
    cfz = lambda z: E["cf_fixed"] if z[1] == "fixed" else E["cf_float"]
    for z in Z:
        km2_per_twh = 1000 / S["mw_per_km2"] / (8.76 * cfz(z)) * z[4]
        mt_per_twh = km2_per_twh * 100 * zec[z[0]]["yield_t_ha"] / 1e6
        (eq if kelp_force else le)({f"kh_{z[0]}": 1, f"kp_{z[0]}": 1, f"osw_{z[0]}": -mt_per_twh}, 0.0)
    # low-grade heat sold: no more than the hubs reject, and no more than the food markets can take
    le({"heat_sold": 1, "hubs": -hb["low_twh"]}, 0.0)
    le({"heat_sold": 1}, food_heat_market_twh(p))
    # carbon
    r_ = {f"c{j}": 1 for j in range(len(p["CARBON"]))}; r_["h_pyro"] = -p["PYRO"]["c_per_h2"]; eq(r_, 0.0)
    bounds = [(0, None)] * nv
    if not CR["enabled"]: bounds[ix["cover_c"]] = (0, 0)
    elif CR.get("cover_crop_max_stable_c_mt") is not None:
        lim=float(CR["cover_crop_max_stable_c_mt"])
        if lim<0:raise ValueError("Cover-crop annual C limit cannot be negative")
        bounds[ix["cover_c"]] = (0, lim)
    if fixed_hubs is not None:
        if fixed_hubs < 0: raise ValueError("fixed_hubs must be non-negative")
        bounds[ix["hubs"]] = (float(fixed_hubs), float(fixed_hubs))
    for j, (nm, cap, val) in enumerate(p["CARBON"]): bounds[ix[f"c{j}"]] = (0, cap)
    bounds[ix["onw"]] = (0, E["cap_onw_twh"]); bounds[ix["pv"]] = (0, E["cap_pv_twh"]); bounds[ix["lwr"]] = (0, E["cap_lwr_twh"])
    vre_ok = E.get("allow_vre", True)
    if not vre_ok: bounds[ix["onw"]] = (0, 0); bounds[ix["pv"]] = (0, 0)
    bounds[ix["export"]] = (0, E["export_cap_twh"])
    for z in Z:
        gw2twh = 8.76 * cfz(z)
        sc = osw_scale.get(z[0], 0.0) if isinstance(osw_scale, dict) else osw_scale
        lo = z[9] * sc * gw2twh
        bounds[ix[f"osw_{z[0]}"]] = (lo, max(lo, z[9] * 1.5 * gw2twh)) if vre_ok else (0, 0)
    if not allow_ely: bounds[ix["h_ely"]] = (0, 0)
    if not flex_heat:
        for k in ("t2mid", "t2dry", "m2dry"): bounds[ix[k]] = (0, 0)
    if post_gas: bounds[ix["h_pyro"]] = (0, 0)          # no natural gas: no pyrolysis, so no pyrolysis carbon either
    else: bounds[ix["h_htse"]] = (0, 0)
    if not p["HTGR"].get("return_unused_steam", False):
        for k in ("m2e", "d2e"): bounds[ix[k]] = (0, 0)
    if not (post_gas and allow_si and p["HTGR"].get("outlet_c", 750) >= 900): bounds[ix["h_si"]] = (0, 0)   # S-I needs ~900 C heat
    res = linprog(c, A_ub=np.array(A), b_ub=np.array(b), A_eq=np.array(Aeq), b_eq=np.array(beq), bounds=bounds, method="highs")
    if res.status != 0: raise RuntimeError(res.message)
    x = {n: float(res.x[i]) for n, i in ix.items()}
    out = post(p, x, float(res.fun), eu, bl, hb, zec, scenario, blend_vol, osw_scale, res); out["flex_heat"] = bool(flex_heat)
    out["post_gas"] = bool(post_gas)
    return out


def post(p, x, lp_cost, eu, bl, hb, zec, scenario, blend_vol, osw_scale, res):
    E = p["ELEC"]; R = p["ROUTES"]; S = p["SEAWEED_PROCESS"]; V = p["VEH"]; HM = p["HEMP"]; Z = I.SEAWEED
    biomass_keys=[f"b{j+1}" for j in range(len(p["BIOMASS"]["tiers"]))]
    out = dict(scenario=scenario, blend_vol=blend_vol, osw_scale=osw_scale, x=x, hub_spec=hb)
    cfz = lambda z: E["cf_fixed"] if z[1] == "fixed" else E["cf_float"]
    out["osw_gw"] = {z[0]: x[f"osw_{z[0]}"] / (8.76 * cfz(z)) for z in Z}
    out["gw"] = dict(onshore_wind=x["onw"] / (8.76 * E["cf_onw"]), solar=x["pv"] / (8.76 * E["cf_pv"]), lwr_smr=x["lwr"] / (8.76 * 0.92),
                     offshore_wind=sum(out["osw_gw"].values()))
    out["el_supply_twh"] = dict(onshore_wind=x["onw"], solar=x["pv"], lwr_smr=x["lwr"], offshore_wind=sum(x[f"osw_{z[0]}"] for z in Z),
                                htgr_hubs=x["hubs"] * hb["el_twh"] + x["hp2e"] * p["HTGR"]["eta_cond"]
                                + x["m2e"] * p["HTGR"]["z_mid"] + x["d2e"] * p["HTGR"]["z_dry"])
    out["el_export_twh"] = x["export"]
    out["hubs"] = x["hubs"]; out["reactors"] = 4 * x["hubs"]; out["htgr_gwt"] = x["hubs"] * hb["mwt"] / 1e3
    out["h2_mt"] = dict(pyrolysis=x["h_pyro"], electrolysis=x["h_ely"], steam_electrolysis=x["h_htse"], sulfur_iodine=x["h_si"], direct_vehicles=eu["h2_mt_direct"], blending=bl["h2_mt"],
                        htl=x["htl"] * R["htl"]["h2_kg_t"] / 1e3, pbtl=x["pbtl"] * R["pbtl"]["h2_kg_t"] / 1e3,
                        hefa=(x["hefa"] + x["hemp_oil_fuel"]) * R["hefa"]["h2_kg_t"] / 1e3,
                        seaweed=sum(x[f"kh_{z[0]}"] * S["htl_h2_kg_t"] + x[f"kp_{z[0]}"] * S["pbtl_h2_kg_t"] for z in Z) / 1e3)
    out["gas_for_pyrolysis_tcf"] = x["h_pyro"] * p["PYRO"]["kg_ch4_per_kg_h2"] / I.TCF_MT_CH4
    out["blend"] = bl
    carbon = x["h_pyro"] * p["PYRO"]["c_per_h2"]; out["carbon_mt"] = carbon
    out["carbon_alloc"] = [dict(market=m[0], mt=x[f"c{j}"], value_usd_t=m[2], cap_mt=m[1]) for j, m in enumerate(p["CARBON"])]
    out["carbon_revenue_bn"] = sum(a["mt"] * a["value_usd_t"] for a in out["carbon_alloc"]) / 1e3
    out["carbon_value_per_t"] = out["carbon_revenue_bn"] * 1e3 / carbon if carbon else 0.0
    sw_h = sum(x[f"kh_{z[0]}"] for z in Z); sw_p = sum(x[f"kp_{z[0]}"] for z in Z)
    stalk = x["hemp_mha"] * HM["stalk_t_ha"]
    residue_total=sum(x[k] for k in biomass_keys)
    pool = residue_total + x["bamboo"] + stalk
    share = lambda v: v / pool if pool else 0
    out["liquids_twh"] = dict(
        residues_and_grasses=(x["htl"] * R["htl"]["mwh_t"] + x["pbtl"] * R["pbtl"]["mwh_t"]) * share(residue_total),
        bamboo=(x["htl"] * R["htl"]["mwh_t"] + x["pbtl"] * R["pbtl"]["mwh_t"]) * share(x["bamboo"]) + x["cel"] * share(x["bamboo"]) * R["ethanol"]["cellulosic_gal_per_t"] / 1e3 * R["atj"]["mwh_per_bgal"],
        hemp=(x["htl"] * R["htl"]["mwh_t"] + x["pbtl"] * R["pbtl"]["mwh_t"]) * share(stalk) + x["hemp_oil_fuel"] * R["hefa"]["mwh_t"],
        seaweed=sw_h * S["htl_mwh_t"] + sw_p * S["pbtl_mwh_t"], oils_hefa=x["hefa"] * R["hefa"]["mwh_t"],
        corn_ethanol_atj=x["corn_etoh"] / max(x["corn_etoh"] + x["cel"] * R["ethanol"]["cellulosic_gal_per_t"] / 1e3, 1e-9) * (x["atj"] * R["atj"]["mwh_per_bgal"] + x["etoh_ldv"] * R["ethanol"]["mwh_per_bgal"]),
    )
    # cellulosic ethanol from non-bamboo pool counted with residues
    cel_twh_resid = x["cel"] * (1 - share(x["bamboo"])) * R["ethanol"]["cellulosic_gal_per_t"] / 1e3 * R["atj"]["mwh_per_bgal"]
    out["liquids_twh"]["residues_and_grasses"] += cel_twh_resid
    out["routes_mt"] = dict(htl=x["htl"], pbtl=x["pbtl"], cellulosic_ethanol_feed=x["cel"], seaweed_htl=sw_h, seaweed_pbtl=sw_p)
    out["biomass_mt"] = dict(residues_grasses=residue_total, bamboo=x["bamboo"], hemp_stalk=stalk,
                             hemp_seed=x["hemp_mha"] * HM["seed_t_ha"], seaweed=sw_h + sw_p, oils=x["hefa"],
                             corn_ethanol_bgal=x["corn_etoh"], cellulosic_ethanol_bgal=x["cel"] * R["ethanol"]["cellulosic_gal_per_t"] / 1e3,
                             atj_ethanol_bgal=x["atj"])
    bc, by = bamboo_cost_t(p)
    out["bamboo"] = dict(mt=x["bamboo"], mha=x["bamboo"] / by, yield_t_ha=by, cost_t=bc)
    out["hemp"] = dict(mha=x["hemp_mha"], seed_mt=x["hemp_mha"] * HM["seed_t_ha"], oil_mt=x["hemp_mha"] * HM["seed_t_ha"] * HM["oil_frac"],
                       meal_mt=x["hemp_mha"] * HM["seed_t_ha"] * (1 - HM["oil_frac"]), stalk_mt=stalk)
    out["biochar_mt"] = x["htl"] * R["htl"]["char_t_t"]
    CR=p["CROP_RESIDUE"]
    if CR["enabled"]:
        crop_spec=CR.get("feedstocks") or [CR]
        crop_keys=biomass_keys[:len(crop_spec)]
        crop=sum(x[k] for k in crop_keys)
        soil_market=next(j for j,(nm,cap,val) in enumerate(p["CARBON"]) if nm.startswith("Soil amendment"))
        nbal={}
        selected=[]
        for k,f in zip(crop_keys,crop_spec):
            flow=x[k]
            selected.append(dict(name=f.get("name",p["BIOMASS"]["tiers"][int(k[1:])-1][0]),group=f.get("group","crop"),
                                 selected_mt=flow,max_mt=f.get("cap_mt",CR["cap_mt"]),
                                 npk_kg_t=f.get("elemental_kg_t",CR["elemental_kg_t"]),
                                 source_status=f.get("source_status","assumed screening capacity"),
                                 delivered_and_soil_usd_t=p["BIOMASS"]["tiers"][int(k[1:])-1][2]))
        for nutrient in ("n","p","k"):
            removed=sum(x[k]*f.get("elemental_kg_t",CR["elemental_kg_t"])[nutrient] for k,f in zip(crop_keys,crop_spec))
            recovered=sum(x[k]*f.get("elemental_kg_t",CR["elemental_kg_t"])[nutrient]*f.get("recovered_fraction",CR["recovered_fraction"])[nutrient] for k,f in zip(crop_keys,crop_spec))
            aq=sum(x[k]*f.get("elemental_kg_t",CR["elemental_kg_t"])[nutrient]*f.get("recovered_fraction",CR["recovered_fraction"])[nutrient]*f.get("wastewater_recovered_share",CR["wastewater_recovered_share"])[nutrient] for k,f in zip(crop_keys,crop_spec))
            imports=removed-recovered
            nbal[nutrient]=dict(removed_kt=removed,wastewater_recovered_kt=aq,
                hydrochar_recovered_kt=recovered-aq,imported_kt=imports,
                recovered_returned_kt=recovered,returned_kt=recovered+imports,
                closed_residual_kt=removed-recovered-imports)
        char_c=crop*R["htl"]["char_t_t"]*CR["hydrochar_c_fraction"]*CR["hydrochar_stable_fraction"]
        pyro_c=x[f"c{soil_market}"]*CR["methane_carbon_stable_fraction"]
        cover_c=x["cover_c"]
        req=sum(x[k]*f.get("stable_soc_c_t_per_dry_t",CR["stable_soc_c_t_per_dry_t"]) for k,f in zip(crop_keys,crop_spec))
        out["crop_residue_soil"]=dict(feedstock_mt=crop,max_sustainable_screen_mt=CR["cap_mt"],selected_feedstocks=selected,
            htl_biocrude_fuel_twh=crop*R["htl"]["mwh_t"],hydrochar_return_mt=crop*R["htl"]["char_t_t"],
            treated_aqueous_stream='recovered nutrient concentrate only, after contaminant control, desalting if needed, and lawful field-specific application',
            nutrients=nbal,stable_soil_c_required_mt=req,hydrochar_stable_c_mt=char_c,
            methane_carbon_return_mt=x[f"c{soil_market}"],methane_carbon_stable_mt=pyro_c,
            cover_crop_extra_stable_c_mt=cover_c,carbon_balance_surplus_mt=char_c+pyro_c+cover_c-req,
            fertilizer_cost_bn=sum(nbal[k]["imported_kt"]*CR["nutrient_replacement_usd_per_kg"][k]/1e3 for k in nbal),
            assumption_warning='Feedstock type capacities, residue-specific NPK recovery, stable SOC equivalence and legal safe land application are sensitivity inputs, not field-verified.')

    # seaweed zones
    sz = []
    for z in Z:
        e = zec[z[0]]; gw = out["osw_gw"][z[0]]; km2 = gw * 1000 / S["mw_per_km2"]; mt = x[f"kh_{z[0]}"] + x[f"kp_{z[0]}"]
        sz.append(dict(zone=z[0], region=z[2], species=z[3], type=z[1], wind_gw=gw, wind_km2=km2,
                       seaweed_km2=km2 * z[4] if mt > 1e-9 else 0.0, yield_t_ha=e["yield_t_ha"], dry_mt=mt,
                       htl_mt=x[f"kh_{z[0]}"], pbtl_mt=x[f"kp_{z[0]}"], wet_mt=mt / z[6], n_kt=mt * z[7] * 1e3,
                       land_n_kt=mt * z[7] * 1e3 * z[8], fuel_twh=x[f"kh_{z[0]}"] * S["htl_mwh_t"] + x[f"kp_{z[0]}"] * S["pbtl_mwh_t"],
                       fert_n_kt=mt * z[7] * S["n_rec"] * 1e3, fert_p_kt=mt * S["p"] * S["p_rec"] * 1e3, fert_k_kt=mt * S["k"] * S["k_rec"] * 1e3,
                       vessels=mt * 1e6 / e["t_dry_per_vessel_yr"], drones=(km2 * z[4] if mt > 1e-9 else 0) / I.LOGISTICS["drone_km2"],
                       harvester_mwh=mt * e["harvester_kwh_t"] * 1e3, vessel_mwh=mt * e["vessel_kwh_t"] * 1e3, port_km=z[10],
                       **{f"cost_{k}": v for k, v in e.items() if k.endswith("_t")}, color=z[12], box=z[11]))
    out["seaweed"] = sz
    km2_by = {("pac_" if s["type"] == "float" and s["zone"] in ("wa", "or", "nca", "cca", "sca") else "") + s["zone"]: s["seaweed_km2"] for s in sz}
    tot_sw = sum(s["dry_mt"] for s in sz)
    out["grid_harvester"] = fleet_sizing(km2_by, tot_sw / 0.12, pacific_passes=3.0, other_passes=1.5) if tot_sw > 0 else {}
    out["fleet"] = dict(vessels=sum(s["vessels"] for s in sz), drones=sum(s["drones"] for s in sz),
                        vessel_energy_gwh=sum(s["vessel_mwh"] for s in sz) / 1e3, harvester_energy_gwh=sum(s["harvester_mwh"] for s in sz) / 1e3)
    # costs
    pl, pg = pyro_cost_per_kg(p)
    gen = (x["onw"] * (E["onshore_wind"] + E["vre_firming"]) + x["pv"] * (E["solar"] + 1.25 * E["vre_firming"]) + x["lwr"] * E["lwr_smr"]
           + sum(x[f"osw_{z[0]}"] * ((E["osw_fixed"] if z[1] == "fixed" else E["osw_floating"]) + 0.5 * E["vre_firming"]) for z in Z)) / 1e3
    ers = V["ers_km"] * V["ers_capex_m_per_km"] * 1e6 * (crf(0.07, V["ers_life"]) + V["ers_om"]) / 1e9
    Eu = p["ENDUSE"]
    veh = (V["ldv_stock_m"] * 1e6 * (Eu["ldv"]["bev"] * V["ldv_bev_net_usd_yr"] + Eu["ldv"]["fcev"] * V["ldv_fcev_net_usd_yr"])
           + V["ers_trucks_m"] * 1e6 * V["ers_truck_net_usd_yr"] + V["fcev_trucks_m"] * 1e6 * V["fcev_truck_net_usd_yr"]
           + V["bev_trucks_m"] * 1e6 * V["bev_truck_net_usd_yr"] + V["re_trucks_m"] * 1e6 * V["re_truck_net_usd_yr"]
           + V["tractors_m"] * 1e6 * 0.8 * V["tractor_net_usd_yr"] + V["constr_m"] * 1e6 * 0.8 * V["constr_net_usd_yr"]
           + V["forklifts_m"] * 1e6 * V["forklift_net_usd_yr"]) / 1e9
    el = eu["el"]
    sw_bio = sum(s["dry_mt"] * (s["cost_farm_t"] + s["cost_harvester_t"] + s["cost_vessel_t"] + s["cost_drones_t"]) for s in sz) / 1e3
    sw_ref = sum(s["htl_mt"] * S["htl_cost_t"] + s["pbtl_mt"] * S["pbtl_cost_t"] for s in sz) / 1e3
    costs = dict(
        electricity_generation=gen, transmission_distribution=eu["el_total"] * E["td_adder"] / 1e3,
        charging=(el["ldv"] * E["charge_ldv"] + (el["hdv_bev"] + el["hdv_ers_battery"] + el["hdv_re"] + el["farm"] + el["construction"] + el["industrial"]) * E["charge_hdv"]) / 1e3,
        electric_highways=ers, rail_electrification=V["rail_elec_capex_bn"] * crf(0.07, V["rail_life"]) * 1.02,
        htgr_hubs=x["hubs"] * hb["cost_bn"], pyrolysis_plants=x["h_pyro"] * pl, natural_gas=x["h_pyro"] * pg,
        electrolysis=x["h_ely"] * p["ELECTROLYSIS"]["capex_cost_kg"] + x["h_htse"] * p["NUCLEAR_H2"]["htse"]["capex_cost_kg"]
                    + x["h_si"] * p["NUCLEAR_H2"]["sulfur_iodine"]["capex_cost_kg"],
        h2_delivery=eu["h2_mt_direct"] * p["H2_DELIVERY"]["vehicle"] + bl["h2_mt"] * p["H2_DELIVERY"]["blend"]
                    + (out["h2_mt"]["htl"] + out["h2_mt"]["pbtl"] + out["h2_mt"]["hefa"] + out["h2_mt"]["seaweed"]) * p["H2_DELIVERY"]["onsite"],
        land_biomass=(sum(x[f"b{j+1}"] * t[2] for j, t in enumerate(p["BIOMASS"]["tiers"])) + x["bamboo"] * bc) / 1e3,
        hemp_net_of_meal=x["hemp_mha"] * 1e6 * (HM["cost_usd_ha"] - HM["seed_t_ha"] * (1 - HM["oil_frac"]) * HM["meal_value_usd_t"]) / 1e9,
        biorefineries=(x["htl"] * R["htl"]["cost_t"] + x["pbtl"] * R["pbtl"]["cost_t"] + x["cel"] * R["ethanol"]["cellulosic_gal_per_t"] * R["ethanol"]["cellulosic_conv_per_gal"]) / 1e3
                      + x["hemp_oil_fuel"] * R["hefa_conv_only"] / 1e3,
        seaweed_farms_harvest_haul=sw_bio, seaweed_refining=sw_ref, hefa_oils=x["hefa"] * R["hefa"]["cost_t"] / 1e3,
        ethanol=(x["corn_etoh"] * R["ethanol"]["corn_cost_per_bgal"] + x["atj"] * R["atj"]["conv_per_bgal"]) / 1e9,
        vehicles_and_machines_net=veh + V["farm_charging_bn_yr"],
        process_heat_equipment=(x["e_heat"] * 2.0 + x["e_dry"] * 8.0 + (x["t2mid"] + x["t2dry"] + x["m2dry"]) * HX_COST) / 1e3,
        soil_cover_crop_carbon=x["cover_c"] * p["CROP_RESIDUE"]["cover_crop_stable_carbon_cost_usd_t_c"] / 1e3,
        residual_pipeline_gas=eu["gas_resid_twh"] * 3.412e6 * (p["GAS"]["price_mmbtu"] + 0.5) / 1e9,
    )
    fd = food(p, out); heat_used_twh = fd["low_grade_twh"] - fd["unused_low_grade_twh"]   # v2.3: credit only heat actually used
    out["low_grade_heat_used_twh"] = heat_used_twh
    firm = x["hubs"] * hb["el_twh"] + x["hp2e"] * p["HTGR"]["eta_cond"] + x["m2e"] * p["HTGR"]["z_mid"] + x["d2e"] * p["HTGR"]["z_dry"] + x["lwr"]
    htse_el = x["h_htse"] * p["NUCLEAR_H2"]["htse"]["kwh_e_kg"]
    Rr = p["ROUTES"]; Ss = p["SEAWEED_PROCESS"]; Zs = I.SEAWEED; NH = p["NUCLEAR_H2"]
    mid_used = (x["htl"] * Rr["htl"]["heat_mwh_t"] + (x["hefa"] + x["hemp_oil_fuel"]) * Rr["hefa"]["heat_mwh_t"]
                + sum(x[f"kh_{z[0]}"] for z in Zs) * Ss["htl_heat_mwh_t"] - 0.98 * x["e_heat"] - HX_EFF * x["t2mid"])
    dry_used = (sum(x[f"kp_{z[0]}"] for z in Zs) * Ss["pbtl_dry_mwh_t"] + 0.6 * x["cel"] + x["h_htse"] * NH["htse"]["kwh_th_kg"]
                - 2.5 * x["e_dry"] - HX_EFF * (x["t2dry"] + x["m2dry"]))
    thermal = x["hubs"] * p["HTGR"]["mwt"] * p["HTGR"]["cf"] * 8.76 / 1e3
    out["hub_energy_twh"] = dict(thermal=thermal, electricity=firm - x["lwr"], refinery_process_steam=mid_used,
                                 htse_steam_and_drying=dry_used, food_heat=heat_used_twh,
                                 sulfur_iodine_heat=x["h_si"] * NH["sulfur_iodine"]["kwh_th_kg"])
    out["hub_energy_twh"]["conversion_losses_and_reject"] = thermal - sum(v for k, v in out["hub_energy_twh"].items() if k != "thermal")
    out["htse_firm_power"] = dict(firm_nuclear_twh=firm, htse_electricity_twh=htse_el, htse_share_of_firm=htse_el / firm if firm else 0.0)
    top = x["hubs"] * hb["pyro_twh"]; pyro_heat = x["h_pyro"] * pyro_reactor_heat(p)
    out["hub_heat_twh"] = dict(top_tier_available=top, to_pyrolysis=pyro_heat,
                               pyrolysis_electric_boost=x["h_pyro"] * (pyro_elec(p) - p["PYRO"]["elec_kwh_kg"]), to_turbine=x["hp2e"], to_process_steam=x["t2mid"],
                               to_drying=x["t2dry"], process_steam_to_drying=x["m2dry"],
                               top_tier_unused=top - pyro_heat - x["hp2e"] - x["t2mid"] - x["t2dry"],
                               pyrolysis_share_of_top_tier=pyro_heat / top if top else 0.0,
                               electricity_from_top_tier=x["hp2e"] * p["HTGR"]["eta_cond"],
                               electric_process_heat=x["e_heat"], electric_drying=x["e_dry"],
                               mid_available=x["hubs"] * hb["mid_twh"], dry_available=x["hubs"] * hb["dry_twh"])
    credits = dict(carbon_products=-out["carbon_revenue_bn"],
                   seaweed_fertiliser=-sum(s["dry_mt"] * s["cost_fert_credit_t"] for s in sz) / 1e3,
                   surplus_electricity_sold=-x["export"] * E["export_value"] / 1e3,
                   low_grade_heat_to_food=-heat_used_twh * 8.0 / 1e3)
    out["costs_bn"] = costs; out["credits_bn"] = credits
    out["total_cost_bn"] = sum(costs.values()) + sum(credits.values())
    sb = bl["h2_mt"] / max(x["h_pyro"] + x["h_ely"] + x["h_htse"] + x["h_si"], 1e-9); out["blend_share_of_h2"] = sb
    hub_blend = sb * (costs["htgr_hubs"] + costs["pyrolysis_plants"] + costs["natural_gas"] + credits["carbon_products"]) + bl["h2_mt"] * p["H2_DELIVERY"]["blend"]
    out["blending_cost_bn"] = hub_blend - bl["gas_displaced_tcf"] * 1.037 * (p["GAS"]["price_mmbtu"] + p["GAS"]["delivery_mmbtu"])
    out["transport_cost_bn"] = out["total_cost_bn"] - hub_blend
    out["lp_objective_bn"] = lp_cost
    # v2.3 reconciliation: reported cost = LP objective + terms fixed by exogenous demand (cannot change the LP solution)
    #   + (food()-based heat credit - LP heat credit) - LP-only electric heat/drying adders (already in generation cost)
    const = dict(transmission_distribution=costs["transmission_distribution"], charging=costs["charging"],
                 electric_highways=costs["electric_highways"], rail_electrification=costs["rail_electrification"],
                 vehicles_and_machines_net=costs["vehicles_and_machines_net"], residual_pipeline_gas=costs["residual_pipeline_gas"],
                 h2_delivery_vehicles_and_blend=eu["h2_mt_direct"] * p["H2_DELIVERY"]["vehicle"] + bl["h2_mt"] * p["H2_DELIVERY"]["blend"])
    heat_adj = credits["low_grade_heat_to_food"] - (-x["heat_sold"] * 8.0 / 1e3)
    resid = out["total_cost_bn"] - (lp_cost + sum(const.values()) + heat_adj)
    out["objective_reconciliation"] = dict(lp_objective_bn=lp_cost, fixed_terms_bn=const, fixed_terms_total_bn=sum(const.values()),
                                           heat_credit_adjustment_bn=heat_adj,
                                           reported_total_bn=out["total_cost_bn"], residual_bn=resid)
    # shadow price of liquid fuel (USD/MWh) from the LP: the liquids row is the 7th inequality (index 6)
    try:
        out["liquid_shadow_usd_mwh"] = -float(res.ineqlin.marginals[7]) * 1e3
        out["jet_shadow_usd_mwh"] = -float(res.ineqlin.marginals[8]) * 1e3
    except Exception:
        out["liquid_shadow_usd_mwh"] = None
    out["enduse"] = eu
    out["emissions"] = emissions_2050(p, out, eu, bl)
    out["petroleum"] = petroleum_baseline(p, eu)
    out["food"] = fd
    return out


# Single audited generic lifecycle coefficient for the mixed terrestrial HTL route.
CI_RESIDUES_GRASSES_G_MJ = 10.0

def emissions_2050(p, out, eu, bl, elec_ci=0.010):
    R, S = p["ROUTES"], p["SEAWEED_PROCESS"]; L = out["liquids_twh"]; H = out["h2_mt"]; P = p["PYRO"]
    made = H["pyrolysis"] + H["electrolysis"] + H["steam_electrolysis"] + H["sulfur_iodine"]
    water_ci = P["h2_leak"] * P["gwp_h2"]                       # water-splitting routes: H2 leakage + grid electricity only
    h2ci = ((H["pyrolysis"] * h2_ci(p, elec_ci) + H["electrolysis"] * (water_ci + p["ELECTROLYSIS"]["kwh_kg"] * elec_ci)
             + H["steam_electrolysis"] * (water_ci + p["NUCLEAR_H2"]["htse"]["kwh_e_kg"] * elec_ci)
             + H["sulfur_iodine"] * (water_ci + p["NUCLEAR_H2"]["sulfur_iodine"]["kwh_e_kg"] * elec_ci)) / made) if made > 1e-9 else h2_ci(p, elec_ci)
    ci = dict(residues_and_grasses=CI_RESIDUES_GRASSES_G_MJ, bamboo=12.0, hemp=20.0, seaweed=12.0, oils_hefa=R["hefa"]["ci_g_mj"], corn_ethanol_atj=R["atj"]["ci_g_mj"])
    h2_liq = (out["h2_mt"]["htl"] + out["h2_mt"]["pbtl"] + out["h2_mt"]["hefa"] + out["h2_mt"]["seaweed"]) * h2ci
    mt = dict(electricity_lifecycle=eu["el_total"] * elec_ci, h2_direct=eu["h2_mt_direct"] * h2ci,
              liquid_fuels=sum(L[k] * 3.6 * ci[k] for k in L) / 1e3 + h2_liq,
              pipeline_gas_residual=eu["gas_resid_twh"] * 3.6 * I.PETRO_CI["ng"] / 1e3)
    base = petroleum_baseline(p, eu)
    tot = sum(mt.values())
    return dict(by_source_mt=mt, total_mt=tot, baseline_wtw_mt=base["wtw_mt"], reduction_pct=100 * (1 - tot / base["wtw_mt"]),
                h2_ci_kg_per_kg=h2ci, biochar_removal_mt=out["biochar_mt"] * 0.6 * 44 / 12,
                solid_carbon_kept_out_mtco2=out["carbon_mt"] * 44 / 12, blending_co2_avoided_mt=bl["co2_avoided_burner_mt"] - bl["h2_mt"] * h2ci)


def petroleum_baseline(p, eu):
    B = p["BASE"]; d = eu["base"]
    gal = dict(gasoline=B["gasoline_mbd"] * 42e6 * 365, diesel=(B["onroad_diesel_bgal"] + B["rail_diesel_bgal"] + B["marine_distillate_bgal"]) * 1e9,
               jet=B["jet_mbd"] * 42e6 * 365, resid=B["marine_resid_mbd"] * 42e6 * 365)
    offroad_gal = (B["farm_diesel_bgal"] + B["construction_mining_diesel_bgal"] + B["industrial_trucks_bgal_dge"]) * 1e9
    res = {}
    for case, pr in I.PRICES.items():
        retail = sum(gal[f] * pr[f] for f in gal) / 1e9 + offroad_gal * I.OFFROAD_DIESEL_PRICE[case] / 1e9
        pretax = sum(gal[f] * (pr[f] - I.TAX[f]) for f in gal) / 1e9 + offroad_gal * I.OFFROAD_DIESEL_PRICE[case] / 1e9
        res[case] = dict(retail_bn=retail, pretax_bn=pretax)
    ng = d["pipeline"] * 3.412e6 * (p["GAS"]["price_mmbtu"] + 0.5) / 1e9
    wtw = (d["ldv"] * I.PETRO_CI["gasoline"] + (d["hdv"] + d["rail"] + d["farm"] + d["construction"] + d["industrial"]) * I.PETRO_CI["diesel"]
           + d["air"] * I.PETRO_CI["jet"] + d["marine"] * I.PETRO_CI["resid"] + d["pipeline"] * I.PETRO_CI["ng"]) * 3.6 / 1e3
    return dict(prices=res, pipeline_gas_bn=ng, wtw_mt=wtw, total_twh=sum(d.values()), total_quad=sum(d.values()) / I.QUAD_TWH,
                offroad_bgal=offroad_gal / 1e9)


# ============================================================================================= food from the cascade
def food_heat_market_twh(p):
    """Low-grade heat the food uses in food() can absorb: Asparagopsis tanks + greenhouses + RAS (TWh_th)."""
    F = p["FOOD"]; asp = asparagopsis()
    return (asp["seaweed_mt_dry"] * F["asparagopsis_heat_mwh_t"]
            + F["greenhouse_market_mt"] * 1e9 / F["greenhouse_yield_kg_m2"] * F["greenhouse_heat_kwh_m2"] / 1e9
            + F["ras_market_mt"] * 1e9 * F["ras_heat_kwh_kg"] / 1e9)


def food(p, out):
    F = p["FOOD"]; hb = out["hub_spec"]; n = out["hubs"]
    low = n * hb["low_twh"]                       # TWh_th of 35-70 C heat actually piped to neighbours
    dry_left = max(n * hb["dry_twh"] - sum(s["pbtl_mt"] for s in out["seaweed"]) * p["SEAWEED_PROCESS"]["pbtl_dry_mwh_t"], 0)
    asp = asparagopsis(); asp_heat = asp["seaweed_mt_dry"] * F["asparagopsis_heat_mwh_t"]
    left = max(low - asp_heat, 0)
    gh_cap_heat = F["greenhouse_market_mt"] * 1e9 / F["greenhouse_yield_kg_m2"] * F["greenhouse_heat_kwh_m2"] / 1e9   # TWh
    gh_heat = min(left * 0.85, gh_cap_heat); left -= gh_heat
    ras_heat = min(left, F["ras_market_mt"] * 1e9 * F["ras_heat_kwh_kg"] / 1e9); left -= ras_heat
    gh_m2 = gh_heat * 1e9 / F["greenhouse_heat_kwh_m2"]
    veg_mt = gh_m2 * F["greenhouse_yield_kg_m2"] / 1e9
    fish_mt = ras_heat * 1e9 / F["ras_heat_kwh_kg"] / 1e9
    grain_mt = min(dry_left / F["grain_dry_mwh_t"] * 1e-0, F["grain_near_hub_mt"])   # TWh / (MWh/t) = Mt
    hemp_seed = out["hemp"]["seed_mt"]
    # V7: Separate actual modelled primary food biomass from prospective hemp meal.
    # Energy-equivalents are NOT a complete human diet and do NOT imply delivery or consumption.
    veg_kcal = veg_mt * 1e9 * F["kcal_per_kg_veg"]
    fish_kcal = fish_mt * 1e9 * F["kcal_per_kg_fish"]
    hemp_kcal = out["hemp"]["meal_mt"] * 1e9 * 3500  # theoretical meal energy ONLY
    denominator = F["kcal_per_person_day"] * 365 * 1e6
    gross_primary_equiv_m = (veg_kcal + fish_kcal) / denominator
    edible_primary_equiv_m = (veg_kcal * F["vegetable_edible_fraction"] +
                              fish_kcal * F["fish_shrimp_edible_fraction"]) / denominator
    potential_hemp_equiv_m = hemp_kcal / denominator
    legacy_combined_equiv_m = gross_primary_equiv_m + potential_hemp_equiv_m
    return dict(low_grade_twh=low, asparagopsis=asp, greenhouse_ha=gh_m2 / 1e4, greenhouse_heat_twh=gh_heat, vegetables_mt=veg_mt,
                vegetables_value_bn=veg_mt * F["greenhouse_value_usd_t"] / 1e3, fish_shrimp_mt=fish_mt, fish_value_bn=fish_mt * F["ras_value_usd_t"] / 1e3,
                ras_heat_twh=ras_heat, grain_dried_mt=grain_mt, hemp_seed_mt=hemp_seed, hemp_meal_mt=out["hemp"]["meal_mt"],
                hemp_protein_mt=out["hemp"]["meal_mt"] * p["HEMP"]["protein_frac_meal"], unused_low_grade_twh=left,
                # Explicitly separate categories; do not interpret energy-equivalents as persons fed.
                greenhouse_seafood_gross_calorie_equiv_m=gross_primary_equiv_m,
                greenhouse_seafood_edible_calorie_equiv_m=edible_primary_equiv_m,
                edible_fraction_scenarios=dict(vegetables=F["vegetable_edible_fraction"], fish_shrimp=F["fish_shrimp_edible_fraction"]),
                hemp_meal_potential_calorie_equiv_m=potential_hemp_equiv_m,
                # Retained only for machine compatibility; deprecated misleading field:
                people_fed_calorie_equiv_m=legacy_combined_equiv_m,
                people_fed_calorie_equiv_deprecated=True)


def asparagopsis():
    A = I.AG; tot_s = tot_c = 0.0; g = {}
    for k, heads in dict(feedlot=A["head_feedlot_m"], dairy=A["head_dairy_m"], grazing=A["head_grazing_m"]).items():
        kg = heads * 1e6 * A["dmi_kg_d"][k] * 365 * A["dose_dm"] * A["adoption"][k]
        cut = A["enteric_mt"] * A["enteric_share"][k] * A["cut"][k] * A["adoption"][k]
        g[k] = dict(seaweed_kt=kg / 1e6, mtco2e_cut=cut); tot_s += kg / 1e9; tot_c += cut
    return dict(groups=g, seaweed_mt_dry=tot_s, mtco2e_cut=tot_c, share_of_enteric=tot_c / A["enteric_mt"],
                tank_ha=tot_s * 1e6 / A["tank_yield_t_ha"], cost_bn=tot_s * 1e6 * A["tank_cost_t"] / 1e9,
                usd_per_tco2e=tot_s * A["tank_cost_t"] / tot_c)


# ============================================================================================= v3.0 after natural gas
def post_gas_params(p):
    """Steady state after U.S. natural gas: no pyrolysis, no gas grid (so no blend), pipeline compressors fully electric
    (hydrogen and CO2 pipelines), and no methane-derived carbon for vehicle structures."""
    p = copy.deepcopy(p); p["ENDUSE"]["pipeline"] = dict(elec=1.0, gas=0.0); p["lightweight"] = False
    return p


def fuel_supply(r, p=None):
    """Heavy-metal demand of the reactor fleet and years of supply, once-through HALEU vs closed fast/thorium breeding."""
    F = I.FUEL; H = I.HTGR
    twh_th = r["hubs"] * H["mwt"] * H["cf"] * 8.76 / 1e3 + r["el_supply_twh"]["lwr_smr"] / 0.33      # hubs + any LWR SMRs
    feed = (F["haleu_enrich"] - F["tails"]) / (F["feed_assay"] - F["tails"])                        # kg natural U per kg HALEU
    once_t = twh_th * 1e6 / 24 / (F["haleu_burnup_gwd_t"] * 1e3) * feed                              # t natural U per year
    closed_t = twh_th * 1e6 / 24 / (F["fission_mwd_per_g"] * 1e6) / (1 - F["closed_cycle_loss"])     # t heavy metal per year
    yrs = lambda t, use: t / use
    gwe = twh_th / 8.76 / H["cf"] * F["gwe_per_gwt"]                                                   # electric-equivalent fleet size
    startup_pu = gwe * F["startup_pu_t_per_gwe"]; snf_pu = F["us_snf_thm"] * F["snf_pu_frac"]
    return dict(thermal_twh=twh_th, fleet_gwe_equivalent=gwe, startup_fissile_pu_t=startup_pu, us_spent_fuel_pu_t=snf_pu,
                startup_share_of_us_spent_fuel_pu=startup_pu / snf_pu, once_through_natural_u_t_yr=once_t, closed_cycle_heavy_metal_t_yr=closed_t,
                utilisation_gain=once_t / closed_t,
                years=dict(once_through_world_identified_u=yrs(F["world_identified_u_t"], once_t),
                           closed_us_depleted_u=yrs(F["us_depleted_u_t"], closed_t),
                           closed_us_thorium=yrs(F["us_thorium_t"], closed_t),
                           closed_world_identified_u=yrs(F["world_identified_u_t"], closed_t),
                           closed_world_thorium=yrs(F["world_thorium_t"], closed_t),
                           closed_seawater_u=yrs(F["seawater_u_t"], closed_t)))


# ============================================================================================= solve with reactor learning loop
def solve_learning(p, **kw):
    mult = p.get("capex_mult", 1.0); capex = p["HTGR"]["capex_kwt"] or 2000.0 * mult; r = None
    for _ in range(4):
        r = solve(p, capex_kwt=capex, **kw)
        rc = reactor_cost(p["reactor_case"], max(int(round(r["reactors"])), 1))
        new = rc["fleet_avg_kwt_with_idc"] * mult
        if p["HTGR"]["capex_kwt"] or abs(new - capex) < 20: break
        capex = new
    r["reactor_cost"] = reactor_cost(p["reactor_case"], max(int(round(r["reactors"])), 1)); r["capex_kwt_used"] = capex
    return r


# ============================================================================================= v5.0 bounded exhaustive reactor-learning audit
# The fleet-level learning curve gives a non-convex cost function in hub count.  For
# the hypothetical closed-fission cases, inspect every INTEGER hub count from zero
# through MAX_HUBS, and solve the conditional linear programme at its matching fleet
# cost. This is a bounded global comparison, NOT a proof about larger fleets or an
# engineering deployment forecast.
MAX_HUBS_V5 = 2000

def solve_bounded_learning(p, max_hubs=MAX_HUBS_V5, **kw):
    if max_hubs < 1 or int(max_hubs) != max_hubs:
        raise ValueError("max_hubs must be a positive integer")
    best, feasible, invalid, landscape = None, 0, 0, []
    mult = p.get("capex_mult", 1.0)
    if p["HTGR"].get("capex_kwt"):
        raise ValueError("bounded learning audit expects endogenous fleet capital cost")
    for n in range(max_hubs + 1):
        # The learning relation counts reactor modules (four per 800-MWt hub).
        rc = reactor_cost(p["reactor_case"], max(4*n, 1))
        capex = rc["fleet_avg_kwt_with_idc"] * mult
        try:
            r = solve(p, capex_kwt=capex, fixed_hubs=n, **kw)
        except RuntimeError as exc:
            if "infeasible" in str(exc).lower():
                invalid += 1
                continue
            raise
        feasible += 1
        if n % 10 == 0:
            landscape.append(dict(hubs=n, reported_transport_cost_bn=r["transport_cost_bn"], total_cost_bn=r["total_cost_bn"]))
        if best is None or r["total_cost_bn"] < best["total_cost_bn"]:
            r["reactor_cost"] = rc
            r["capex_kwt_used"] = capex
            best = r
    if best is None:
        raise RuntimeError("No feasible fleet was found within the bounded range")
    best["learning_search"] = dict(method="exhaustive_integer_hubs_bounded",
        max_hubs=max_hubs, feasible_count=feasible, infeasible_count=invalid,
        objective="total_cost_bn", explicitly_excludes_larger_fleets=True,
        assumption="four reactor modules per hub; continuous Wright average per module",
        samples_every_ten=landscape)
    return best


# ============================================================================================= gas depletion (unchanged from v1)
def gas_depletion(program_tcf_2050=0.0, displaced_tcf=0.0, lng_bcfd_2035=30.0, canada_extra_bcfd=0.0, canada_on=True, rec_frac=0.8,
                  domestic_growth=0.006, start=2026, end=2250, ramp=(2030, 2050)):
    N = I.NG; bcfd = 365 / 1000
    R_us = (N["us_proved_tcf"] + N["us_trr_tcf"]) * rec_frac; R_ca = N["canada_remaining_tcf"] * rec_frac
    rows, short = [], None
    for y in range(start, end + 1):
        f = min(max((y - ramp[0]) / (ramp[1] - ramp[0]), 0), 1)
        dom = N["us_consumption_bcfd_2025"] * (1 + domestic_growth) ** min(y - 2025, 15) * bcfd
        lng = (N["us_lng_bcfd_2025"] + (lng_bcfd_2035 - N["us_lng_bcfd_2025"]) * min(max((y - 2025) / 10, 0), 1)) * bcfd
        demand = dom + lng + N["mexico_pipe_bcfd"] * bcfd + f * (program_tcf_2050 - displaced_tcf)
        ca_dom = (N["canada_domestic_bcfd"] + N["canada_lng_bcfd_2035"] * min(max((y - 2025) / 10, 0), 1)) * bcfd
        ca_cap = R_ca / N["rp_floor_years"] if R_ca / max(ca_dom + 9 * bcfd, 1e-9) < N["rp_floor_years"] else 1e9
        to_us = 0.0
        if canada_on:
            want = (N["canada_imports_bcfd_2025"] + canada_extra_bcfd * min(max((y - 2028) / 7, 0), 1)) * bcfd
            to_us = max(min(want, ca_cap - ca_dom), 0.0)
        R_ca = max(R_ca - min(ca_dom + to_us, ca_cap), 0)
        need = max(demand - to_us, 0)
        cap = R_us / N["rp_floor_years"] if R_us / max(need, 1e-9) < N["rp_floor_years"] else 1e9
        prod = min(need, cap)
        if prod < need - 1e-6 and short is None: short = y
        R_us = max(R_us - prod, 0)
        rows.append(dict(year=y, demand_tcf=demand, us_prod_tcf=prod, canada_to_us_tcf=to_us, us_remaining_tcf=R_us, ca_remaining_tcf=R_ca))
        if R_us <= 1 and y > 2100: break
    return dict(first_shortfall_year=short, rows=rows)


# ============================================================================================= transition with E85 (from v1)
def logistic(t, mid, w): return 1 / (1 + math.exp(-(t - mid) / w))


def transition(p, design, e85=True, corn_cap_bgal=20.0, cellulosic_cap_bgal=8.0, conv_2035=0.40):
    eu = design["enduse"]; d = eu["base"]; tot_2050 = design["emissions"]["total_mt"]
    ci = dict(ldv=I.PETRO_CI["gasoline"], hdv=I.PETRO_CI["diesel"], rail=I.PETRO_CI["diesel"], farm=I.PETRO_CI["diesel"],
              construction=I.PETRO_CI["diesel"], industrial=I.PETRO_CI["diesel"], air=I.PETRO_CI["jet"], marine=I.PETRO_CI["resid"], pipeline=I.PETRO_CI["ng"])
    mids = dict(ldv=(2036, 3.2), hdv=(2039, 3.0), rail=(2040, 3.0), farm=(2041, 3.5), construction=(2040, 3.5), industrial=(2034, 3.0),
                air=(2042, 3.5), marine=(2042, 3.5), pipeline=(2038, 3.0))
    seg = {k: d[k] * ci[k] for k in ci}; segsum = sum(seg.values())
    rows, cb, cc, c0 = [], 0, 0, 0
    for y in range(2025, 2061):
        a = {}
        for k, (m, w) in mids.items():
            v = (logistic(y, m, w) - logistic(2025, m, w)) / (logistic(2050, m, w) - logistic(2025, m, w)); a[k] = min(max(v, 0), 1)
        eff = 0.995 ** (y - 2025)
        base = segsum * 3.6 / 1e3 * eff
        gas_left = d["ldv"] * (1 - 0.97 * a["ldv"]) * eff
        eci = I.ETHANOL_CI["today"] + (I.ETHANOL_CI["ccs"] - I.ETHANOL_CI["today"]) * min(max((y - 2026) / 9, 0), 1)
        supply = min(16.49 + (corn_cap_bgal - 16.49) * min(max((y - 2026) / 8, 0), 1), corn_cap_bgal) + cellulosic_cap_bgal * min(max((y - 2030) / 10, 0), 1)
        e10 = gas_left * 0.072
        conv = (min(conv_2035 * min(max((y - 2026) / 9, 0), 1) + 0.07, 0.6)) if e85 else 0.0
        used = min(e10 + gas_left * conv * 0.70 * 0.79, supply * 22.37)
        save = used * 3.6 * (I.PETRO_CI["gasoline"] - eci) / 1e3 - e10 * 3.6 * (I.PETRO_CI["gasoline"] - I.ETHANOL_CI["today"]) / 1e3
        petro = sum(seg[k] * (1 - a[k]) for k in seg) * 3.6 / 1e3 * eff
        new = tot_2050 * sum(seg[k] * a[k] for k in seg) / segsum
        case0 = petro + new; case = case0 - save
        cb += base; cc += case; c0 += case0
        rows.append(dict(year=y, baseline_mt=base, case_mt=case, case_no_e85_mt=case0, ethanol_supply_bgal=supply,
                         ethanol_used_bgal=used / 22.37, e85_bgal=max(used - e10, 0) / 22.37 / 0.79, **{f"adopt_{k}": v for k, v in a.items()}))
    s = lambda key, y0, y1: sum(r["baseline_mt"] - r[key] for r in rows if y0 <= r["year"] <= y1)
    return dict(rows=rows, cum_avoided_2026_2050=s("case_mt", 2026, 2050), cum_avoided_2026_2060=s("case_mt", 2026, 2060),
                e85_extra_avoided_2026_2045=sum(r["case_no_e85_mt"] - r["case_mt"] for r in rows if 2026 <= r["year"] <= 2045))


# ============================================================================================= sweet-spot sweeps
def sweep_offshore(scales=(0.0, 0.1, 0.25, 0.4, 0.5, 0.6, 0.75, 1.0, 1.25), yield_levels=(1, 2)):
    rows = []
    for yl in yield_levels:
        for s in scales:
            p = default_params(); p["yield_level"] = yl; p["osw_scale"] = s
            r = solve_learning(p, scenario="design", blend_vol=0.0)
            rows.append(dict(yield_level=yl, scale=s, osw_gw=r["gw"]["offshore_wind"], cost_bn=r["transport_cost_bn"],
                             seaweed_mt=r["biomass_mt"]["seaweed"], seaweed_twh=r["liquids_twh"]["seaweed"],
                             seaweed_share=r["liquids_twh"]["seaweed"] / r["enduse"]["liq_total"], export_twh=r["el_export_twh"],
                             liquid_shadow=r["liquid_shadow_usd_mwh"], hubs=r["hubs"]))
    return rows


def sweep_merit(yield_level=1):
    """Add whole offshore zones in merit order (cheapest seaweed fuel first) and re-optimise the system each time."""
    p0 = default_params(); p0["yield_level"] = yield_level
    order = [m["zone"] for m in zone_merit(p0)]
    rows = []
    for k in range(len(order) + 1):
        p = default_params(); p["yield_level"] = yield_level
        sc = {z: (1.0 if z in order[:k] else 0.0) for z in order}
        r = solve_learning(p, scenario="design", blend_vol=0.0, osw_scale=sc)
        rows.append(dict(yield_level=yield_level, n_zones=k, last_zone=order[k - 1] if k else "", osw_gw=r["gw"]["offshore_wind"],
                         cost_bn=r["transport_cost_bn"], seaweed_mt=r["biomass_mt"]["seaweed"], seaweed_twh=r["liquids_twh"]["seaweed"],
                         export_twh=r["el_export_twh"], land_n_kt=sum(s["land_n_kt"] for s in r["seaweed"]),
                         n_kt=sum(s["n_kt"] for s in r["seaweed"])))
    for i in range(1, len(rows)):
        dc = rows[i]["cost_bn"] - rows[i - 1]["cost_bn"]; dt = rows[i]["seaweed_twh"] - rows[i - 1]["seaweed_twh"]
        rows[i]["marginal_usd_per_mwh_seaweed"] = dc * 1e3 / dt if dt > 0 else None
    rows[0]["marginal_usd_per_mwh_seaweed"] = None
    return rows


def zone_merit(p):
    """Net cost of each zone's seaweed fuel (USD/MWh), counting its wind farm's electricity at system value."""
    out = []; S = p["SEAWEED_PROCESS"]
    for z in I.SEAWEED:
        e = seaweed_zone_economics(p, z)
        net_t = e["biomass_cost_t"] - e["fert_credit_t"]
        htl = (net_t + S["htl_cost_t"]) / S["htl_mwh_t"]
        pb = (net_t + S["pbtl_cost_t"] + S["pbtl_h2_kg_t"] * 1.9 + S["pbtl_el_mwh_t"] * 75) / S["pbtl_mwh_t"]
        out.append(dict(zone=z[0], region=z[2], species=z[3], yield_t_ha=e["yield_t_ha"], net_biomass_t=net_t,
                        htl_usd_mwh=htl, pbtl_usd_mwh=pb, best_usd_mwh=min(htl, pb), **{k: v for k, v in e.items() if k.endswith("_t")}))
    return sorted(out, key=lambda r: r["best_usd_mwh"])


# ============================================================================================= Monte Carlo
MC = [(("ELEC", "onshore_wind"), 40, 55, 85), (("ELEC", "solar"), 38, 48, 75), (("ELEC", "osw_fixed"), 75, 95, 150),
      (("ELEC", "osw_floating"), 85, 115, 175), (("ELEC", "lwr_smr"), 85, 115, 175), (("ELEC", "vre_firming"), 10, 20, 40),
      (("ELEC", "td_adder"), 20, 30, 45), (("ELEC", "charge_ldv"), 20, 35, 60), (("ELEC", "export_value"), 25, 40, 60),
      (("PYRO", "capex_kw_h2"), 700, 1000, 2200), (("GAS", "price_mmbtu"), 2.5, 3.5, 6.0), (("PYRO", "leak_upstream"), 0.005, 0.015, 0.03),
      (("ROUTES", "htl", "cost_t"), 130, 170, 260), (("ROUTES", "pbtl", "cost_t"), 220, 290, 420),
      (("SEAWEED_PROCESS", "farm_cost_ref_t"), 300, 380, 600), (("VEH", "ldv_bev_net_usd_yr"), -400, 100, 700),
      (("VEH", "ers_capex_m_per_km"), 2.5, 3.5, 6.0), (("H2_DELIVERY", "vehicle"), 1.5, 2.5, 4.0),
      (("ENDUSE", "service_growth_2050"), 0.95, 1.05, 1.25), (("HEMP", "cost_usd_ha"), 650, 850, 1200),
      (("BAMBOO", "establish_usd_ha"), 2500, 4000, 7000)]


def set_path(p, path, v):
    d = p
    for k in path[:-1]: d = d[k]
    d[path[-1]] = v


def monte_carlo(n=1000, seed=7, scenario="design", osw_scale=None):
    rng = np.random.default_rng(seed); rows = []
    for i in range(n):
        p = default_params(); dr = {}
        for path, lo, mo, hi in MC:
            v = float(rng.triangular(lo, mo, hi)); set_path(p, path, v); dr["/".join(path)] = v
        p["BIOMASS"]["tiers"] = [(nm, cap, pr * float(rng.triangular(0.8, 1.0, 1.4))) for nm, cap, pr in p["BIOMASS"]["tiers"]]
        p["yield_level"] = int(rng.choice([0, 1, 2], p=[0.3, 0.5, 0.2])); dr["yield_level"] = p["yield_level"]
        p["reactor_case"] = str(rng.choice(["low", "central", "high"], p=[0.25, 0.5, 0.25])); dr["reactor_case"] = {"low": 0, "central": 1, "high": 2}[p["reactor_case"]]
        cm, cv = float(rng.triangular(0.5, 1.0, 1.5)), float(rng.triangular(0.5, 1.0, 1.3))
        p["CARBON"] = [[m[0], m[1] * (cm if j < len(p["CARBON"]) - 1 else 1), m[2] * (cv if m[2] > 0 else 1)] for j, m in enumerate(p["CARBON"])]
        if osw_scale is not None: p["osw_scale"] = osw_scale
        dr["carbon_market_scale"] = cm; dr["carbon_value_scale"] = cv
        try:
            r = solve_learning(p, scenario=scenario, blend_vol=0.0)
        except RuntimeError:
            continue
        g = p["ENDUSE"]["service_growth_2050"]
        rows.append(dict(**dr, transport_cost_bn=r["transport_cost_bn"], hubs=r["hubs"], capex_kwt=r["capex_kwt_used"],
                         h2_mt=r["h2_mt"]["pyrolysis"], seaweed_mt=r["biomass_mt"]["seaweed"], bamboo_mt=r["biomass_mt"]["bamboo"],
                         hemp_mha=r["hemp"]["mha"], emissions_mt=r["emissions"]["total_mt"], reduction_pct=r["emissions"]["reduction_pct"],
                         petro_2025=(r["petroleum"]["prices"]["late_2025"]["pretax_bn"] + r["petroleum"]["pipeline_gas_bn"]) * g,
                         petro_2026=(r["petroleum"]["prices"]["nov_2026"]["pretax_bn"] + r["petroleum"]["pipeline_gas_bn"]) * g))
    return rows


def slim(r):
    keep = {k: v for k, v in r.items() if k not in ("x", "enduse")}
    eu = r["enduse"]; keep["enduse"] = {k: eu[k] for k in ("el", "el_total", "h2_twh", "h2_mt_direct", "liq", "liq_total", "jet", "demand", "base", "gas_resid_twh")}
    return keep


def main(n_mc=1000):
    res = {}
    cases = dict(design=dict(scenario="design", blend_vol=0.0), design_learning=dict(scenario="design", blend_vol=0.0),
                 design_demonstrated=dict(scenario="design", blend_vol=0.0), design_half_offshore=dict(scenario="design", blend_vol=0.0),
                 design_reactor_low=dict(scenario="design", blend_vol=0.0), design_reactor_high=dict(scenario="design", blend_vol=0.0),
                 design_no_vehicle_carbon=dict(scenario="design", blend_vol=0.0),
                 design_sweet_spot=dict(scenario="design", blend_vol=0.0, osw_scale={z: 1.0 for z in ("nca", "cca", "or", "wa", "gom", "la")}),
                 design_sweet_spot_no_fertiliser=dict(scenario="design", blend_vol=0.0, osw_scale={z: 1.0 for z in ("nca", "cca", "or", "wa", "gom", "la")}),
                 least_cost=dict(scenario="least_cost", blend_vol=0.0),          # same 20% blend basis as every other case (and the Monte Carlo)
                 least_cost_no_blend=dict(scenario="least_cost", blend_vol=0.0),
                 least_cost_blend20_sensitivity=dict(scenario="least_cost", blend_vol=0.20),
                 # v2.4 system-boundary check: with no blend the LP objective is the transport-only cost (no allocation)
                 design_sweet_spot_no_blend=dict(scenario="design", blend_vol=0.0, osw_scale={z: 1.0 for z in ("nca", "cca", "or", "wa", "gom", "la")}),
                 design_no_blend=dict(scenario="design", blend_vol=0.0),
                 design_blend20_sensitivity=dict(scenario="design", blend_vol=0.20),
                 # v2.4 flexible reactor-heat dispatch sensitivity
                 least_cost_flex_heat=dict(scenario="least_cost", blend_vol=0.0, flex_heat=True),
                 design_sweet_spot_flex_heat=dict(scenario="design", blend_vol=0.0, flex_heat=True, osw_scale={z: 1.0 for z in ("nca", "cca", "or", "wa", "gom", "la")}),
                 design_flex_heat=dict(scenario="design", blend_vol=0.0, flex_heat=True),
                 # v3.0 after natural gas: hydrogen from reactor hubs by steam electrolysis (and optionally sulfur-iodine)
                 post_gas_least_cost=dict(scenario="least_cost", blend_vol=0.0, post_gas=True),
                 post_gas_least_cost_si=dict(scenario="least_cost", blend_vol=0.0, post_gas=True, allow_si=True),
                 post_gas_sweet_spot=dict(scenario="design", blend_vol=0.0, post_gas=True, osw_scale={z: 1.0 for z in ("nca", "cca", "or", "wa", "gom", "la")}),
                 post_gas_design=dict(scenario="design", blend_vol=0.0, post_gas=True),
                 # v4.0 decomposition of the post-gas cost change, starting from the gas era without the blend
                 least_cost_no_blend_no_lightweight=dict(scenario="least_cost", blend_vol=0.0),
                 least_cost_no_blend_no_lightweight_pipe_elec=dict(scenario="least_cost", blend_vol=0.0),
                 # v4.0 950 C very-high-temperature reactor sensitivity (gas era: all pyrolysis heat from the reactor)
                 least_cost_vhtr=dict(scenario="least_cost", blend_vol=0.0),
                 design_sweet_spot_vhtr=dict(scenario="design", blend_vol=0.0, osw_scale={z: 1.0 for z in ("nca", "cca", "or", "wa", "gom", "la")}),
                 # v4.0 post-gas sensitivities: HTSE performance and cost, reactor learning, breeder reactors
                 post_gas_htse_42kwh=dict(scenario="least_cost", blend_vol=0.0, post_gas=True),
                 post_gas_htse_48kwh=dict(scenario="least_cost", blend_vol=0.0, post_gas=True),
                 post_gas_htse_cost150=dict(scenario="least_cost", blend_vol=0.0, post_gas=True),
                 post_gas_htse_48kwh_cost150=dict(scenario="least_cost", blend_vol=0.0, post_gas=True),
                 post_gas_reactor_low=dict(scenario="least_cost", blend_vol=0.0, post_gas=True),
                 post_gas_reactor_high=dict(scenario="least_cost", blend_vol=0.0, post_gas=True),
                 post_gas_breeder=dict(scenario="least_cost", blend_vol=0.0, post_gas=True),
                 post_gas_breeder_high=dict(scenario="least_cost", blend_vol=0.0, post_gas=True),
                 # v4.1 theoretical future: sustainable (breeding, closed-cycle, 950 C) fission
                 sustainable_fission=dict(scenario="least_cost", blend_vol=0.0, post_gas=True, allow_si=True),
                 sustainable_fission_nuclear_only=dict(scenario="least_cost", blend_vol=0.0, post_gas=True, allow_si=True),
                 sustainable_fission_nuclear_only_premium=dict(scenario="least_cost", blend_vol=0.0, post_gas=True, allow_si=True),
                 sustainable_fission_nuclear_only_si_cheap=dict(scenario="least_cost", blend_vol=0.0, post_gas=True, allow_si=True))
    for name, kw in cases.items():
        p = default_params()
        if name == "design_learning": p["yield_level"] = 2
        if name == "design_demonstrated": p["yield_level"] = 0
        if name == "design_half_offshore": p["osw_scale"] = 0.5
        if name == "design_reactor_low": p["reactor_case"] = "low"
        if name == "design_reactor_high": p["reactor_case"] = "high"
        if name == "design_no_vehicle_carbon": p["lightweight"] = False; p["CARBON"] = p["CARBON"][1:]
        if name.startswith("post_gas"): p = post_gas_params(p)
        if name.startswith("least_cost_no_blend_no_lightweight"): p["lightweight"] = False
        if name.endswith("_pipe_elec"): p["ENDUSE"]["pipeline"] = dict(elec=1.0, gas=0.0)
        if name.endswith("_vhtr") or name == "post_gas_least_cost_si": p = vhtr_params(p)
        if "htse_42kwh" in name: p["NUCLEAR_H2"]["htse"]["kwh_e_kg"] = 42.0
        if "htse_48kwh" in name: p["NUCLEAR_H2"]["htse"]["kwh_e_kg"] = 48.0
        if "cost150" in name: p["NUCLEAR_H2"]["htse"]["capex_cost_kg"] = 1.5
        if name == "post_gas_reactor_low": p["reactor_case"] = "low"
        if name == "post_gas_reactor_high": p["reactor_case"] = "high"
        if name == "post_gas_breeder": p = breeder_params(p, 1.25, 15.0)
        if name == "post_gas_breeder_high": p = breeder_params(p, 1.5, 20.0)
        if name == "sustainable_fission": p = sustainable_fission_params(p)
        if name == "sustainable_fission_nuclear_only": p = sustainable_fission_params(p, nuclear_only=True)
        if name == "sustainable_fission_nuclear_only_si_cheap":
            p = sustainable_fission_params(p, nuclear_only=True); p["NUCLEAR_H2"]["sulfur_iodine"]["capex_cost_kg"] = 0.8
        if name == "sustainable_fission_nuclear_only_premium": p = sustainable_fission_params(p, nuclear_only=True, capex_mult=1.25, fuel_mwhth=15.0)
        fert0 = dict(I.FERT_PRICE)
        if name == "design_sweet_spot_no_fertiliser":   # seaweed nutrient credit removed (no validated recovery balance)
            for k in I.FERT_PRICE: I.FERT_PRICE[k] = 0.0
        if name.startswith("sustainable_fission"):
            res[name] = solve_bounded_learning(p, **kw)
        else:
            res[name] = solve_learning(p, **kw)
        res[name]["fuel_supply"] = fuel_supply(res[name])
        I.FERT_PRICE.update(fert0)
    json.dump({k: slim(v) for k, v in res.items()}, open(OUT / "scenarios.json", "w"), indent=1, default=float)
    d = res["design"]; p = default_params()
    # reactor cost table
    n = int(round(d["reactors"]))
    json.dump({c: reactor_cost(c, n) for c in ("low", "central", "high")} | {"anchors": I.REACTOR_ANCHORS}, open(OUT / "reactor_costs.json", "w"), indent=1)
    # merit order & sweeps
    json.dump(dict(design=zone_merit(p), learning=zone_merit({**p, "yield_level": 2})), open(OUT / "seaweed_merit.json", "w"), indent=1)
    sm = sweep_merit(1) + sweep_merit(2)
    with open(OUT / "sweep_merit.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(sm[0].keys())); w.writeheader(); w.writerows(sm)
    sw = sweep_offshore()
    with open(OUT / "sweep_offshore.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(sw[0].keys())); w.writeheader(); w.writerows(sw)
    # gas
    disp = d["blend"]["gas_displaced_tcf"] + d["enduse"]["demand"]["pipeline"] * 0.6 / I.TCF_TWH
    gas = {}
    for lng in (20.0, 30.0, 40.0):
        for ca, on, extra in (("no_canada", False, 0.0), ("canada_current", True, 0.0), ("canada_plus4", True, 4.0), ("canada_plus8", True, 8.0)):
            for rf in (0.6, 0.8, 1.0):
                for pn, prog, ds in (("none", 0.0, 0.0), ("design", d["gas_for_pyrolysis_tcf"], disp)):
                    gas[f"lng{int(lng)}|{ca}|rf{rf}|{pn}"] = gas_depletion(prog, ds, lng, extra, on, rf)["first_shortfall_year"]
    json.dump(gas, open(OUT / "gas_depletion_grid.json", "w"), indent=1)
    central = {k: gas_depletion(d["gas_for_pyrolysis_tcf"] if k != "none" else 0.0, disp if k != "none" else 0.0, 30.0,
                                4.0 if k == "design_plus4" else 0.0, k != "design_no_canada", 0.8)
               for k in ("none", "design_no_canada", "design_current_canada", "design_plus4")}
    json.dump(central, open(OUT / "gas_depletion_central.json", "w"))
    tr, tr0 = transition(p, d, True), transition(p, d, False)
    json.dump(dict(with_e85=tr, without_e85={k: v for k, v in tr0.items() if k != "rows"}), open(OUT / "transition.json", "w"))
    json.dump(dict(turning=gh_turning(), energy=gh_energy(), fleet_design=d["grid_harvester"], fleet=d["fleet"]), open(OUT / "grid_harvester_us.json", "w"), indent=1)
    mc = monte_carlo(n_mc); mcl = monte_carlo(n_mc, seed=11, scenario="least_cost")
    mcs = monte_carlo(n_mc, seed=13, scenario="design", osw_scale={z: 1.0 for z in ("nca", "cca", "or", "wa", "gom", "la")})
    for nm, rows in (("monte_carlo_design.csv", mc), ("monte_carlo_least_cost.csv", mcl), ("monte_carlo_sweet_spot.csv", mcs)):
        with open(OUT / nm, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    q = lambda rows, k: {f"p{pp}": float(np.percentile([r[k] for r in rows], pp)) for pp in (5, 50, 95)}
    summ = {}
    for nm, rows in (("design", mc), ("least_cost", mcl), ("sweet_spot", mcs)):
        summ[nm] = {k: q(rows, k) for k in ("transport_cost_bn", "hubs", "capex_kwt", "h2_mt", "seaweed_mt", "bamboo_mt", "hemp_mha", "emissions_mt", "reduction_pct")}
        summ[nm]["p_cheaper_2025"] = float(np.mean([r["transport_cost_bn"] < r["petro_2025"] for r in rows]))
        summ[nm]["p_cheaper_2026"] = float(np.mean([r["transport_cost_bn"] < r["petro_2026"] for r in rows])); summ[nm]["n"] = len(rows)
    from scipy.stats import spearmanr
    keys = [k for k in mc[0] if "/" in k or k in ("yield_level", "reactor_case", "carbon_market_scale", "carbon_value_scale")]
    y = [r["transport_cost_bn"] for r in mc]
    summ["sensitivity_design"] = {k: float(spearmanr([r[k] for r in mc], y)[0]) for k in keys}
    json.dump(summ, open(OUT / "monte_carlo_summary.json", "w"), indent=1)
    print(json.dumps({k: dict(cost=round(v["transport_cost_bn"], 1), hubs=round(v["hubs"], 1), capex=round(v["capex_kwt_used"]),
                              osw=round(v["gw"]["offshore_wind"]), sw=round(v["biomass_mt"]["seaweed"], 1), bam=round(v["biomass_mt"]["bamboo"], 1),
                              hemp=round(v["hemp"]["mha"], 2), red=round(v["emissions"]["reduction_pct"], 1)) for k, v in res.items()}, indent=0))
    return res


if __name__ == "__main__":
    import sys
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 1000)
