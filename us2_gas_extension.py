"""How much longer can U.S. + Canadian natural gas sustain the programme?

Two levers are tested on top of the gas-depletion model in us2_model.py (same reserves, LNG, Mexico,
Canada and 15-year reserves-to-production floor):

  1. Biogas: anaerobic digesters on livestock farms and at municipal wastewater treatment plants.
     The upgraded biomethane replaces fossil methane fed to the pyrolysis hubs.
  2. Heat pumps: residential and commercial space and water heating move from gas to electric
     heat pumps. The extra electricity is supplied either by clean generation or partly by gas plants
     (the "grid-gas feedback"). Because there is less building gas, the 20% hydrogen blend into
     building gas also shrinks, so the hubs need less methane for blend hydrogen.

Flat layout: reads scenarios.json in this folder and writes gas_extension.json and
ScienceFigS9_gas_extension (.png/.pdf).  Run after us2_model.py.
"""
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import us2_inputs as I

HERE = Path(__file__).resolve().parent
S = json.load(open(HERE / "scenarios.json"))
BCFD = 365 / 1000                      # Bcf/d -> Tcf/yr
MT_PER_TCF = I.TCF_MT_CH4              # 19.3 Mt CH4 per Tcf (model constant)

# ------------------------------------------------------------------ data (sources in the manuscript, refs 34-40)
BIOGAS_MT = dict(                      # methane potential, Mt CH4/yr
    manure_nrel=1.905, wastewater_nrel=2.339,          # NREL (2013) Biogas Potential in the United States
    iic_food_waste_nrel=1.158, landfill_nrel=2.455,    # same source (not farm or sewage; sensitivity only)
)
# AgSTAR (2018): 8,113 candidate swine and dairy farms, 171.6 million MMBtu/yr of biogas energy
BIOGAS_MT["manure_agstar_swine_dairy"] = 171.608e6 / 1.037e6 / 1000 * MT_PER_TCF   # MMBtu -> Bcf -> Tcf -> Mt CH4
BIOGAS_CASES = {                       # (Mt CH4/yr at full build-out, label)
    "low":     (0.5 * (BIOGAS_MT["manure_nrel"] + BIOGAS_MT["wastewater_nrel"]), "Half of NREL manure + wastewater potential"),
    "central": (BIOGAS_MT["manure_nrel"] + BIOGAS_MT["wastewater_nrel"], "NREL manure + wastewater potential"),
    "high":    (BIOGAS_MT["manure_agstar_swine_dairy"] + BIOGAS_MT["wastewater_nrel"] + BIOGAS_MT["iic_food_waste_nrel"],
                "AgSTAR swine and dairy + NREL wastewater + food-waste co-digestion"),
    "all_organics": (BIOGAS_MT["manure_agstar_swine_dairy"] + BIOGAS_MT["wastewater_nrel"] + BIOGAS_MT["iic_food_waste_nrel"]
                     + BIOGAS_MT["landfill_nrel"], "High case + landfill gas"),
}
BIOGAS_RAMP = (2028, 2045)

BUILD = dict(                          # building gas, weather-normalised 2024-2025 average (EIA)
    res_tcf=12.65 * BCFD, com_tcf=9.45 * BCFD,
    res_share=dict(space=0.68, water=0.25),            # RECS 2020: 68% space heating, 25% water heating
    com_share=dict(space=1520 / 2216, water=221 / 2216),  # CBECS 2018 Table E8
    eff_gas=dict(space=0.85, water=0.62),              # stock furnace/boiler and gas water-heater efficiencies [A]
)
HP_COP = dict(low=dict(space=2.2, water=2.5), central=dict(space=2.8, water=3.0), high=dict(space=3.2, water=3.5))
HP_ADOPTION_2050 = 0.90                # share of space+water heating converted by 2050 [A]
HP_RAMP = (2028, 2050)
CANADA_EXPANDED_BCFD = 25.0           # upper case: Canadian output raised ~30% above 2025 (19.1 Bcf/d), all exported [A]
CANADA_DECARB = (2030, 2050)           # Canada's domestic gas use and LNG exports fall to zero over this period [A]
GAS_HEAT_RATE_MMBTU_MWH = 7.0          # gas fleet heat rate for any gas-fired share of the new load [A]
CLEAN_POWER_USD_MWH = dict(wind_solar=I.ELEC["onshore_wind"] * 0.5 + I.ELEC["solar"] * 0.5 + I.ELEC["vre_firming"] + I.ELEC["td_adder"],
                          nuclear=I.ELEC["lwr_smr"] + I.ELEC["td_adder"])   # delivered cost of the added clean electricity
GAS_DELIVERED_USD_MMBTU = I.GAS["price_mmbtu"] + I.GAS["delivery_mmbtu"]
MMBTU_PER_TCF = 1.037e9
CO2_KG_PER_MMBTU = 53.06               # EPA emission factor for natural gas combustion
RNG_COST_USD_MMBTU = (28.0, 35.0)      # dairy-manure RNG production cost, MJ Bradley & Associates (2019)
GRID_GAS_SHARE = dict(clean=0.0, today=0.41, all_gas=1.0)   # 41% = gas share of 2025 U.S. generation (EIA)


def ramp(y, a, b): return min(max((y - a) / (b - a), 0.0), 1.0)


def heat_pumps(cop="central", adoption=HP_ADOPTION_2050):
    """Gas saved, electricity added (TWh) and fraction of building gas removed at full adoption."""
    gas = elec = 0.0
    for sect, share in (("res", BUILD["res_share"]), ("com", BUILD["com_share"])):
        tot = BUILD[f"{sect}_tcf"]
        for use in ("space", "water"):
            g = tot * share[use] * adoption
            gas += g
            elec += g * I.TCF_TWH * BUILD["eff_gas"][use] / HP_COP[cop][use]
    return dict(gas_saved_tcf=gas, electricity_twh=elec, building_gas_removed_frac=gas / (BUILD["res_tcf"] + BUILD["com_tcf"]))


def depletion(prog_tcf, disp_tcf, blend_share, biogas_mt=0.0, hp=None, grid_gas=0.0,
              lng_bcfd_2035=30.0, canada_on=True, canada_extra_bcfd=0.0, rec_frac=0.8, domestic_growth=0.006,
              canada_all=None, resource="pgc", start=2026, end=2250, prog_ramp=(2030, 2050)):
    """resource: "pgc" = Potential Gas Committee convention, proved reserves + potential (technically recoverable,
    undiscovered + probable) resources, the default; "potential_only" = potential resources without proved reserves
    (smaller-base sensitivity requested in review).  rec_frac is a haircut applied to that whole stock."""
    """Same accounting as us2_model.gas_depletion, plus biogas and heat-pump terms."""
    N = I.NG
    R_us = ((N["us_proved_tcf"] if resource == "pgc" else 0.0) + N["us_trr_tcf"]) * rec_frac; R_ca = N["canada_remaining_tcf"] * rec_frac
    bg_tcf = biogas_mt / MT_PER_TCF
    hp_save = hp_gas_power = 0.0; blend_cut = 0.0
    if hp:
        hp_save = hp["gas_saved_tcf"]
        hp_gas_power = hp["electricity_twh"] * 1e6 * grid_gas * GAS_HEAT_RATE_MMBTU_MWH / 1.037e6 / 1000   # TWh -> Tcf
        blend_cut = hp["building_gas_removed_frac"]
    short = None; rows = []
    for y in range(start, end + 1):
        f, fh, fb = ramp(y, *prog_ramp), ramp(y, *HP_RAMP), ramp(y, *BIOGAS_RAMP)
        dom = N["us_consumption_bcfd_2025"] * (1 + domestic_growth) ** min(y - 2025, 15) * BCFD
        lng = (N["us_lng_bcfd_2025"] + (lng_bcfd_2035 - N["us_lng_bcfd_2025"]) * ramp(y, 2025, 2035)) * BCFD
        # pyrolysis methane for blend hydrogen shrinks with the building gas it was blended into
        prog = prog_tcf * (1 - blend_share * blend_cut * fh)
        # v2.3: only the blend part of the displacement shrinks with building gas; pipeline-compressor
        # electrification is independent of heat pumps.  disp_tcf may be (blend, pipeline) or a scalar (all blend).
        d_bl, d_pipe = disp_tcf if isinstance(disp_tcf, tuple) else (disp_tcf, 0.0)
        disp = d_bl * (1 - blend_cut * fh) + d_pipe
        fossil_prog = max(prog - fb * bg_tcf, 0.0)
        demand = dom + lng + N["mexico_pipe_bcfd"] * BCFD + f * (fossil_prog - disp) - fh * (hp_save - hp_gas_power)
        fc = ramp(y, *CANADA_DECARB) if canada_all else 0.0     # Canada's own gas use (and LNG) phases out
        ca_dom = (N["canada_domestic_bcfd"] + N["canada_lng_bcfd_2035"] * ramp(y, 2025, 2035)) * BCFD * (1 - fc)
        to_us = 0.0; want = 0.0
        if canada_on:
            want = (N["canada_imports_bcfd_2025"] + canada_extra_bcfd * ramp(y, 2028, 2035)) * BCFD
            if canada_all == "current_production":   # all of today's Canadian output, freed as Canada decarbonises
                want = max(want, N["canada_prod_bcfd_2025"] * BCFD - ca_dom)
            elif canada_all == "expanded":            # Canadian output raised to CANADA_EXPANDED_BCFD by 2040, all to the U.S.
                prod_ca = N["canada_prod_bcfd_2025"] + (CANADA_EXPANDED_BCFD - N["canada_prod_bcfd_2025"]) * ramp(y, 2030, 2040)
                want = max(want, prod_ca * BCFD - ca_dom)
        # reserves floor: Canada cannot produce more than R/15 once its R/P would fall below 15 years
        target = ca_dom + (want if canada_all else 9 * BCFD)
        ca_cap = R_ca / N["rp_floor_years"] if R_ca / max(target, 1e-9) < N["rp_floor_years"] else 1e9
        if canada_on:
            to_us = max(min(want, ca_cap - ca_dom), 0.0)
        R_ca = max(R_ca - min(ca_dom + to_us, ca_cap), 0)
        need = max(demand - to_us, 0)
        cap = R_us / N["rp_floor_years"] if R_us / max(need, 1e-9) < N["rp_floor_years"] else 1e9
        prod = min(need, cap)
        if prod < need - 1e-6 and short is None: short = y
        R_us = max(R_us - prod, 0)
        rows.append(dict(year=y, demand_tcf=demand, us_remaining_tcf=R_us))
        if R_us <= 1 and y > 2100: break
    return dict(first_shortfall_year=short, rows=rows)


def programme(case):
    d = S[case]
    disp = (d["blend"]["gas_displaced_tcf"], d["enduse"]["demand"]["pipeline"] * 0.6 / I.TCF_TWH)   # (blend, pipeline)
    return d["gas_for_pyrolysis_tcf"], disp, d["blend_share_of_h2"]


def main():
    out = dict(inputs=dict(biogas_mt=BIOGAS_MT, biogas_cases={k: v[0] for k, v in BIOGAS_CASES.items()},
                           biogas_tcf={k: v[0] / MT_PER_TCF for k, v in BIOGAS_CASES.items()},
                           building=BUILD, hp_cop=HP_COP, hp_adoption_2050=HP_ADOPTION_2050,
                           heat_pumps={k: heat_pumps(k) for k in HP_COP}, grid_gas_share=GRID_GAS_SHARE),
               cases={})
    hpc = heat_pumps("central")
    # screening economics (outside the transport LP; building equipment costs excluded)
    econ = {}
    for cop in HP_COP:
        h = heat_pumps(cop); gas_val = h["gas_saved_tcf"] * MMBTU_PER_TCF * GAS_DELIVERED_USD_MMBTU / 1e9
        co2 = h["gas_saved_tcf"] * MMBTU_PER_TCF * CO2_KG_PER_MMBTU / 1e9   # Mt
        econ[f"heatpumps_{cop}"] = dict(gas_saved_tcf=h["gas_saved_tcf"], electricity_twh=h["electricity_twh"], gas_saved_value_bn=gas_val,
                                        co2_avoided_combustion_mt=co2,
                                        **{f"electricity_cost_bn_{k}": h["electricity_twh"] * v / 1e3 for k, v in CLEAN_POWER_USD_MWH.items()},
                                        **{f"net_energy_cost_bn_{k}": h["electricity_twh"] * v / 1e3 - gas_val for k, v in CLEAN_POWER_USD_MWH.items()},
                                        **{f"usd_per_t_co2_{k}": (h["electricity_twh"] * v / 1e3 - gas_val) * 1e3 / co2 for k, v in CLEAN_POWER_USD_MWH.items()})
    for k, (mt, _) in BIOGAS_CASES.items():
        mmbtu = mt / MT_PER_TCF * MMBTU_PER_TCF
        econ[f"biogas_{k}"] = dict(tcf=mt / MT_PER_TCF, premium_bn=[mmbtu * (c - GAS_DELIVERED_USD_MMBTU) / 1e9 for c in RNG_COST_USD_MMBTU])
    out["economics"] = econ; out["inputs"]["clean_power_usd_mwh"] = CLEAN_POWER_USD_MWH
    for case, label in (("least_cost", "least-cost system"), ("design_sweet_spot", "220 GW diversification case"), ("design", "515 GW large build")):
        prog, disp, bs = programme(case)
        r = {}
        r["no_programme"] = depletion(0.0, 0.0, 0.0)["first_shortfall_year"]
        r["programme"] = depletion(prog, disp, bs)["first_shortfall_year"]
        for k, (mt, _) in BIOGAS_CASES.items():
            r[f"biogas_{k}"] = depletion(prog, disp, bs, biogas_mt=mt)["first_shortfall_year"]
        for cop in HP_COP:
            for g, gs in GRID_GAS_SHARE.items():
                r[f"heatpumps_{cop}_{g}"] = depletion(prog, disp, bs, hp=heat_pumps(cop), grid_gas=gs)["first_shortfall_year"]
        for g, gs in GRID_GAS_SHARE.items():
            r[f"both_central_{g}"] = depletion(prog, disp, bs, biogas_mt=BIOGAS_CASES["central"][0], hp=hpc, grid_gas=gs)["first_shortfall_year"]
            r[f"both_high_{g}"] = depletion(prog, disp, bs, biogas_mt=BIOGAS_CASES["high"][0], hp=heat_pumps("high"), grid_gas=gs)["first_shortfall_year"]
        r["no_canada_programme"] = depletion(prog, disp, bs, canada_on=False)["first_shortfall_year"]
        for mode in ("current_production", "expanded"):
            r[f"canada_all_{mode}"] = depletion(prog, disp, bs, canada_all=mode)["first_shortfall_year"]
            r[f"canada_all_{mode}_hp_clean"] = depletion(prog, disp, bs, hp=hpc, grid_gas=0.0, canada_all=mode)["first_shortfall_year"]
            r[f"canada_all_{mode}_both_clean"] = depletion(prog, disp, bs, biogas_mt=BIOGAS_CASES["central"][0], hp=hpc, grid_gas=0.0,
                                                           canada_all=mode)["first_shortfall_year"]
            r[f"canada_all_{mode}_no_programme"] = depletion(0.0, 0.0, 0.0, canada_all=mode)["first_shortfall_year"]
        r["no_canada_both_central_clean"] = depletion(prog, disp, bs, biogas_mt=BIOGAS_CASES["central"][0], hp=hpc, grid_gas=0.0,
                                                      canada_on=False)["first_shortfall_year"]
        res_sens = {}
        for res_basis in ("pgc", "potential_only"):
            for rf in (0.6, 0.8, 1.0):
                res_sens[f"{res_basis}|rf{rf}"] = dict(
                    programme=depletion(prog, disp, bs, resource=res_basis, rec_frac=rf)["first_shortfall_year"],
                    heatpumps_clean=depletion(prog, disp, bs, hp=hpc, resource=res_basis, rec_frac=rf)["first_shortfall_year"],
                    canada_all_hp_clean=depletion(prog, disp, bs, hp=hpc, canada_all="current_production", resource=res_basis, rec_frac=rf)["first_shortfall_year"],
                    no_programme=depletion(0.0, 0.0, 0.0, resource=res_basis, rec_frac=rf)["first_shortfall_year"])
        r["resource_sensitivity"] = res_sens
        r["share_of_pyrolysis_gas_from_biogas"] = {k: v[0] / MT_PER_TCF / prog for k, v in BIOGAS_CASES.items()}
        # trajectories for the figure
        bgc = BIOGAS_CASES["central"][0]
        r["traj"] = {nm: [(x["year"], x["us_remaining_tcf"]) for x in res["rows"] if x["year"] <= 2140] for nm, res in (
            ("programme", depletion(prog, disp, bs)),
            ("heatpumps_central_clean", depletion(prog, disp, bs, hp=hpc, grid_gas=0.0)),
            ("both_central_clean", depletion(prog, disp, bs, biogas_mt=bgc, hp=hpc, grid_gas=0.0)),
            ("canada_all_current_production_both_clean", depletion(prog, disp, bs, biogas_mt=bgc, hp=hpc, grid_gas=0.0, canada_all="current_production")),
            ("canada_all_expanded_both_clean", depletion(prog, disp, bs, biogas_mt=bgc, hp=hpc, grid_gas=0.0, canada_all="expanded")))}
        r["label"] = label; r["pyrolysis_gas_tcf"] = prog
        out["cases"][case] = r
    json.dump(out, open(HERE / "gas_extension.json", "w"), indent=1)
    figure(out)
    return out


def figure(out):
    import us2_figures as F
    from us2_figures import C, INK, INK2, GRID, save
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.4), gridspec_kw=dict(width_ratios=[1.15, 1], wspace=0.42))
    r = out["cases"]["least_cost"]
    ladder = [("programme", "#7a776f", "-", "Programme (least-cost system)"),
              ("heatpumps_central_clean", C["blue"], "-", "+ heat pumps on clean power"),
              ("both_central_clean", C["orange"], "--", "+ farm and sewage biogas"),
              ("canada_all_current_production_both_clean", C["violet"], "-", "+ Canada decarbonised, all output to U.S."),
              ("canada_all_expanded_both_clean", C["green"], "-", "+ Canadian output raised to 25 Bcf/d")]
    for k, col, ls, lab in ladder:
        t = np.array(r["traj"][k]); a.plot(t[:, 0], t[:, 1], lw=2, ls=ls, color=col, label=f"{lab}: {r[k]}")
    a.set_xlabel("Year"); a.set_ylabel("U.S. recoverable gas remaining, Tcf"); a.set_xlim(2026, 2140); a.set_ylim(0, 3700)
    a.grid(color=GRID, lw=0.5); a.legend(fontsize=6.4, loc="upper right", title="each step adds to the one above; first shortfall year", title_fontsize=6.4)
    a.set_title("A  Remaining U.S. gas, least-cost system", fontsize=8)
    cases = [("No Canadian imports", "no_canada_programme"), ("Programme (today's Canadian imports)", "programme"),
             ("+ heat pumps, clean power", "heatpumps_central_clean"), ("+ farm and sewage biogas", "both_central_clean"),
             ("+ Canada: all of today's output", "canada_all_current_production_both_clean"),
             ("+ Canada: output raised to 25 Bcf/d", "canada_all_expanded_both_clean")]
    y = np.arange(len(cases))[::-1]
    for (lab, k), yi in zip(cases, y):
        for case, off, col in (("least_cost", 0.18, C["aqua"]), ("design_sweet_spot", -0.18, C["orange"])):
            v = out["cases"][case][k]; base = out["cases"][case]["programme"]
            b.barh(yi + off, v - 2070, left=2070, height=0.34, color=col, label=out["cases"][case]["label"] if yi == y[0] else None)
            d = v - base
            b.text(2108.6, yi + off, f"{v}" if k == "programme" else f"{v} ({d:+d})", va="center", fontsize=6.4, color=INK2)
    npy = out["cases"]["design"]["no_programme"]
    b.plot([npy, npy], [y[-1] - 0.6, y[0] + 0.6], color=INK, lw=0.8, ls="--")
    b.text(npy, y[0] + 0.75, f"no programme: {npy}", fontsize=6.2, color=INK2, ha="center")
    b.set_yticks(y); b.set_yticklabels([c[0] for c in cases], fontsize=7); b.set_xlim(2070, 2117); b.set_ylim(y[-1] - 1.5, y[0] + 1.2)
    b.set_xticks(range(2070, 2111, 10))
    b.set_xlabel("First year supply cannot hold 15 years of reserves"); b.grid(axis="x", color=GRID, lw=0.5); b.set_axisbelow(True)
    b.legend(fontsize=6.6, loc="lower left", ncol=2); b.set_title("B  First shortfall year (change vs programme)", fontsize=8)
    save(fig, "ScienceFigS9_gas_extension")


if __name__ == "__main__":
    o = main()
    for case, r in o["cases"].items():
        print(case, {k: v for k, v in r.items() if k not in ("traj",)})
    print(json.dumps(o["inputs"]["heat_pumps"], indent=1)); print(o["inputs"]["biogas_tcf"])
