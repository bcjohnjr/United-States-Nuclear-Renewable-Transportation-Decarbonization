"""Main-text figures for the Science manuscript (Figures 1-4).  Run after us2_model.py.

Flat layout: reads the result files in this folder and writes ScienceFig1..4 (.png at 300 dpi and .pdf) here.
  Fig. 1  2050 energy by segment and carrier; liquid-fuel supply by feedstock (220 GW vs 515 GW)
  Fig. 2  220 GW diversification-case system map            (same drawing as Map1_national_system)
  Fig. 3  Offshore build sweep and seaweed merit order  (same drawing as Fig02_offshore_sweet_spot)
  Fig. 4  Annual cost vs petroleum; Monte Carlo for all three cases
  Fig. S1 Grid Harvester: side and plan views (illustrations) with harvest energy and turning losses
  Fig. S10 Reactor top-tier heat use (fixed vs flexible dispatch) and cost under three system boundaries
  Fig. S11 After natural gas: cost with hydrogen from steam electrolysis, and years of nuclear fuel supply
  Fig. S12 Theoretical sustainable-fission future: cost by case, and where the breeder fleet's heat goes
"""
import csv
import numpy as np
import matplotlib.pyplot as plt
import us2_figures as F
from us2_figures import C, INK, INK2, MUTED, GRID, S, MCS, OUT, save

SS, D, LC = S["design_sweet_spot"], S["design"], S["least_cost"]


def fig1():
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.4), gridspec_kw=dict(width_ratios=[1.15, 1], wspace=0.55))
    e = SS["enduse"]; el, h2, lq, base = e["el"], e["h2_twh"], e["liq"], e["base"]
    seg = [("Light-duty vehicles", "ldv"), ("Trucks and buses", "hdv"), ("Aviation", "air"), ("Marine", "marine"),
           ("Pipeline compressors", "pipeline"), ("Rail", "rail"), ("Farm machinery", "farm"),
           ("Construction and mining", "construction"), ("Industrial trucks", "industrial")]
    y = np.arange(len(seg))[::-1]
    for yi, (lab, k) in zip(y, seg):
        ev = sum(v for kk, v in el.items() if kk == k or kk.startswith(k + "_"))
        hv, lv = h2.get(k, 0.0), lq.get(k, 0.0)
        a.barh(yi + 0.2, base[k], height=0.36, color="#bdbab2", label="2024 fuel use" if yi == y[0] else None)
        x0 = 0
        for v, col, nm in ((ev, C["blue"], "2050 electricity"), (hv, C["aqua"], "2050 hydrogen"), (lv, C["orange"], "2050 liquid fuel")):
            a.barh(yi - 0.2, v, left=x0, height=0.36, color=col, edgecolor="white", lw=0.6, label=nm if yi == y[0] else None); x0 += v
    a.set_yticks(y); a.set_yticklabels([s[0] for s in seg]); a.set_xlabel("Final energy, TWh/yr")
    a.grid(axis="x", color=GRID, lw=0.5); a.set_axisbelow(True); a.legend(fontsize=7, loc="lower right")
    a.set_title("A  Final energy by segment, 2024 and 2050", fontsize=8)
    order = [("Residues and grasses", "residues_and_grasses"), ("Corn ethanol to jet", "corn_ethanol_atj"), ("Waste oils (HEFA)", "oils_hefa"),
             ("Bamboo", "bamboo"), ("Hemp oil and stalks", "hemp"), ("Seaweed", "seaweed")]
    y = np.arange(len(order))[::-1]
    for r, off, col, nm in ((LC, 0.2, C["aqua"], "Least-cost system, 0 GW offshore"), (SS, -0.2, C["orange"], "Diversification case, 220 GW offshore")):
        v = [r["liquids_twh"].get(k, 0.0) for _, k in order]
        b.barh(y + off, v, height=0.36, color=col, label=nm)
        for yi, vi in zip(y, v): b.text(vi + 12, yi + off, f"{vi:.0f}", va="center", fontsize=6.5, color=INK2)
    b.set_yticks(y); b.set_yticklabels([o[0] for o in order]); b.set_xlabel("Liquid fuel, TWh/yr (2050)")
    b.set_xlim(0, 980); b.grid(axis="x", color=GRID, lw=0.5); b.set_axisbelow(True); b.legend(fontsize=7, loc="lower right")
    b.set_title("B  2050 liquid-fuel supply by feedstock", fontsize=8)
    save(fig, "ScienceFig1_energy_and_liquids")


def fig4():
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.6), gridspec_kw=dict(width_ratios=[1.35, 1], wspace=0.25))
    groups = [("Electricity generation", ["electricity_generation", "process_heat_equipment"], C["blue"]),
              ("Grid, chargers, electric highways, rail", ["transmission_distribution", "charging", "electric_highways", "rail_electrification"], C["violet"]),
              ("Reactor hubs, pyrolysis, gas, H2 delivery", ["htgr_hubs", "pyrolysis_plants", "natural_gas", "electrolysis", "h2_delivery"], C["red"]),
              ("Land biomass, ethanol, refineries", ["land_biomass", "hemp_net_of_meal", "biorefineries", "hefa_oils", "ethanol", "residual_pipeline_gas"], C["orange"]),
              ("Seaweed farms, harvest, haul, refining", ["seaweed_farms_harvest_haul", "seaweed_refining"], C["aqua"]),
              ("Vehicles and machines (net premium)", ["vehicles_and_machines_net"], C["yellow"])]
    cases = [("Least cost\n(0 GW offshore)", LC, "least_cost"), ("Diversification\n(220 GW offshore)", SS, "sweet_spot"), ("Large build\n(515 GW offshore)", D, "design")]
    for i, (lab, r, mk) in enumerate(cases):
        btm = 0; sb = r["blend_share_of_h2"]
        for g, keys, col in groups:
            v = sum(r["costs_bn"][k] for k in keys) * ((1 - sb) if g.startswith("Reactor") else 1)
            a.bar(i, v, bottom=btm, color=col, edgecolor="white", lw=0.8, width=0.6, label=g if i == 0 else None); btm += v
        a.bar(i, sum(r["credits_bn"].values()), color=C["green"], width=0.6, label="Credits: carbon, fertiliser, heat, surplus power" if i == 0 else None)
        a.text(i, btm + 14, f"${r['transport_cost_bn']:.0f} bn", ha="center", fontsize=8, weight="bold", color=INK)
        q = MCS[mk]["transport_cost_bn"]
        a.errorbar(i + 0.38, q["p50"], yerr=[[q["p50"] - q["p5"]], [q["p95"] - q["p50"]]], fmt="o", color=INK, ms=3.5, capsize=3)
    pet = D["petroleum"]["prices"]; pg = D["petroleum"]["pipeline_gas_bn"]
    for j, key in enumerate(("late_2025", "nov_2026")):
        v = pet[key]["pretax_bn"] + pg; a.bar(3 + j, v, color="#bdbab2", width=0.6); a.text(3 + j, v + 14, f"${v:.0f} bn", ha="center", fontsize=8, color=INK)
    a.set_xticks(range(5)); a.set_xticklabels([c[0] for c in cases] + ["Petroleum,\nlate-2025", "Petroleum,\nNov-2026"], fontsize=6.6)
    a.set_ylabel("US$ bn/yr (2026), pre-tax"); a.set_ylim(-60, 1000); a.legend(fontsize=6.0, loc="upper left")
    a.grid(axis="y", color=GRID, lw=0.5); a.set_axisbelow(True)
    a.set_title("A  Annual cost in 2050; whiskers: Monte Carlo median and 5-95%", fontsize=8)
    bins = np.linspace(0.4, 1.5, 45)
    for f, col, lab in (("monte_carlo_least_cost.csv", C["aqua"], "Least cost"), ("monte_carlo_sweet_spot.csv", C["orange"], "Diversification (220 GW)"),
                        ("monte_carlo_design.csv", C["blue"], "Large build")):
        rows = list(csv.DictReader(open(OUT / f)))
        r = np.array([float(x["transport_cost_bn"]) / float(x["petro_2025"]) for x in rows])
        b.hist(r, bins=bins, histtype="step", lw=2, color=col, density=True, label=f"{lab}: cheaper in {100 * np.mean(r < 1):.0f}% of draws")
    top = b.get_ylim()[1]; b.set_ylim(0, top * 1.45)
    b.plot([1, 1], [0, top * 1.08], color=INK, lw=1); b.text(1.015, top * 1.06, "petroleum at\nlate-2025 prices", fontsize=6.5, color=INK2, va="top")
    b.set_xlabel("System cost / petroleum cost at late-2025 prices"); b.set_yticks([]); b.set_ylabel("Density")
    b.legend(fontsize=6.6, loc="upper left")
    b.set_title("B  Monte Carlo, n = 1,000 draws per case", fontsize=8)
    save(fig, "ScienceFig4_cost_vs_petroleum")


def fig_s1_grid_harvester():
    import matplotlib.image as mpimg
    import grid_harvester as G
    fig = plt.figure(figsize=(11, 6.4))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 0.8], hspace=0.12, wspace=0.18)
    for k, (f, t) in enumerate((("grid_harvester_side.jpg", "A  Side view"), ("grid_harvester_top.jpg", "B  Plan view and path of the harvesting head"))):
        ax = fig.add_subplot(gs[0, k]); ax.imshow(mpimg.imread(F.HERE / f)); ax.axis("off"); ax.set_title(t, fontsize=8)
    e = G.energy(); rows = e["rows"]
    bars = [("Conventional\nharvester", e["conventional_mj"], "#bdbab2"), ("Grid Harvester,\nbare hose,\n10% solids", e["bare_hose_10pct_mj"], C["blue"])]
    bars += [(f"Grid Harvester,\nfaired hose,\n{r['dry_solids_fraction'] * 100:.0f}% solids", r["grid_total_mj"], C["aqua"]) for r in rows]
    c = fig.add_subplot(gs[1, 0])
    for i, (lab, v, col) in enumerate(bars):
        c.bar(i, v, color=col, width=0.62); c.text(i, v + 1.5, f"{v:.1f}", ha="center", fontsize=7, color=INK)
    c.set_xticks(range(len(bars))); c.set_xticklabels([b[0] for b in bars], fontsize=6.3)
    c.set_ylabel("Energy per 1.44 ha harvest cycle, MJ"); c.set_ylim(0, 105); c.grid(axis="y", color=GRID, lw=0.5); c.set_axisbelow(True)
    c.set_title("C  Harvest energy per cycle (screening model)", fontsize=8)
    t = G.turning(); d = fig.add_subplot(gs[1, 1])
    tl = [("Conventional\n(10 m turning radius)", t["conventional_missed_pct"], "#bdbab2"),
          ("Grid Harvester,\nforward turns", t["grid_forward_missed_pct"], C["blue"]),
          ("Grid Harvester,\nturns in place", t["grid_inplace_missed_pct"], C["aqua"])]
    for i, (lab, v, col) in enumerate(tl):
        d.bar(i, v, color=col, width=0.55); d.text(i, v + 0.05, f"{v:.2f}%", ha="center", fontsize=7, color=INK)
    d.set_xticks(range(3)); d.set_xticklabels([x[0] for x in tl], fontsize=6.5); d.set_ylim(0, 3.0)
    d.set_ylabel("Area missed at turns, % of 1.44 ha"); d.grid(axis="y", color=GRID, lw=0.5); d.set_axisbelow(True)
    d.set_title("D  Area left unharvested at row ends", fontsize=8)
    save(fig, "ScienceFigS1_grid_harvester")


def fig2_fig3():
    import shutil
    F.map_master(); F.fig_sweetspot()
    for src, dst in (("Map1_national_system", "ScienceFig2_national_system"), ("Fig02_offshore_sweet_spot", "ScienceFig3_offshore_sweet_spot")):
        for ext in (".png", ".pdf"): shutil.copyfile(F.FIG / (src + ext), F.FIG / (dst + ext))


def fig_s10_heat_and_boundaries():
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.4), gridspec_kw=dict(width_ratios=[1.2, 1], wspace=0.45))
    rows = [("Least cost, fixed", "least_cost"), ("Least cost, flexible", "least_cost_flex_heat"),
            ("220 GW, fixed", "design_sweet_spot"), ("220 GW, flexible", "design_sweet_spot_flex_heat"),
            ("515 GW, fixed", "design"), ("515 GW, flexible", "design_flex_heat")]
    parts = [("Methane preheat for pyrolysis", "to_pyrolysis", C["red"]), ("Turbine (40% to electricity)", "to_turbine", C["blue"]),
             ("Stepped down to process steam", "to_process_steam", C["orange"]), ("Stepped down to drying", "to_drying", C["yellow"])]
    parts = [pt for pt in parts if any(S[k]["hub_heat_twh"][pt[1]] > 0.05 for _, k in rows)]
    y = np.arange(len(rows))[::-1]
    for yi, (lab, k) in zip(y, rows):
        h = S[k]["hub_heat_twh"]; x0 = 0
        for nm, kk, col in parts:
            v = h[kk]
            a.barh(yi, v, left=x0, height=0.62, color=col, edgecolor="white", lw=0.8, label=nm if yi == y[0] else None); x0 += v
        a.text(x0 + 6, yi, f"{h['pyrolysis_share_of_top_tier']:.0%} to pyrolysis preheat", va="center", fontsize=6.5, color=INK2)
    a.set_yticks(y); a.set_yticklabels([r[0] for r in rows]); a.set_xlabel("Top-tier reactor heat (750 C helium), TWh/yr")
    a.set_xlim(0, 520); a.grid(axis="x", color=GRID, lw=0.5); a.set_axisbelow(True)
    a.legend(fontsize=6.5, loc="upper center", bbox_to_anchor=(0.45, -0.13), ncol=3, frameon=False)
    a.set_title("A  Top-tier reactor heat: none is left unused", fontsize=8)
    cases = [("Least cost", "least_cost"), ("220 GW", "design_sweet_spot"), ("515 GW", "design")]
    bases = [("Whole system incl. building-gas blend", lambda k: S[k]["total_cost_bn"], C["violet"]),
             ("Transport share (headline)", lambda k: S[k]["transport_cost_bn"], C["blue"]),
             ("No blend: LP objective = transport cost", lambda k: S[k.replace("least_cost", "least_cost_no_blend") if k == "least_cost" else k + "_no_blend"]["transport_cost_bn"], C["aqua"])]
    xx = np.arange(len(cases)); w = 0.26
    for j, (nm, f, col) in enumerate(bases):
        v = [f(k) for _, k in cases]
        b.bar(xx + (j - 1) * w, v, width=w, color=col, edgecolor="white", lw=0.8, label=nm)
        for xi, vi in zip(xx, v): b.text(xi + (j - 1) * w, vi + 8, f"{vi:.0f}", ha="center", fontsize=6, color=INK2)
    pv = D["petroleum"]["prices"]["late_2025"]["pretax_bn"] + D["petroleum"]["pipeline_gas_bn"]
    b.axhline(pv, color=INK, lw=1); b.text(0.5, pv - 12, f"petroleum, late-2025: {pv:.0f}", ha="center", va="top", fontsize=6.5, color=INK)
    b.set_xticks(xx); b.set_xticklabels([c[0] for c in cases]); b.set_ylabel("US$ bn/yr (2026), pre-tax"); b.set_ylim(0, 760)
    b.grid(axis="y", color=GRID, lw=0.5); b.set_axisbelow(True); b.legend(fontsize=6.5, loc="upper left")
    b.set_title("B  Cost under three system boundaries; ranking unchanged", fontsize=8)
    save(fig, "ScienceFigS10_heat_and_boundaries")


def fig_s11_post_gas():
    fig, (a, b) = plt.subplots(1, 2, figsize=(11.5, 4.6), gridspec_kw=dict(width_ratios=[1, 1], wspace=0.75))
    groups = [("Electricity generation", ["electricity_generation", "process_heat_equipment"], C["blue"]),
              ("Grid, chargers, electric highways, rail", ["transmission_distribution", "charging", "electric_highways", "rail_electrification"], C["violet"]),
              ("Reactor hubs, H2 production and delivery, gas", ["htgr_hubs", "pyrolysis_plants", "natural_gas", "electrolysis", "h2_delivery"], C["red"]),
              ("Land biomass, ethanol, refineries", ["land_biomass", "hemp_net_of_meal", "biorefineries", "hefa_oils", "ethanol", "residual_pipeline_gas"], C["orange"]),
              ("Seaweed farms, harvest, haul, refining", ["seaweed_farms_harvest_haul", "seaweed_refining"], C["aqua"]),
              ("Vehicles and machines (net premium)", ["vehicles_and_machines_net"], C["yellow"])]
    cases = [("Least cost,\nwith gas", "least_cost_no_blend"), ("Least cost,\nafter gas", "post_gas_least_cost"),
             ("220 GW,\nwith gas", "design_sweet_spot_no_blend"), ("220 GW,\nafter gas", "post_gas_sweet_spot")]
    for i, (lab, k) in enumerate(cases):
        r = S[k]; btm = 0; sb = r["blend_share_of_h2"]
        for g, keys, col in groups:
            v = sum(r["costs_bn"].get(kk, 0.0) for kk in keys) * ((1 - sb) if g.startswith("Reactor") else 1)
            a.bar(i, v, bottom=btm, color=col, edgecolor="white", lw=0.8, width=0.62, label=g if i == 0 else None); btm += v
        a.bar(i, sum(r["credits_bn"].values()), color=C["green"], width=0.62, label="Credits" if i == 0 else None)
        a.text(i, btm + 12, f"${r['transport_cost_bn']:.0f} bn", ha="center", fontsize=7.5, weight="bold", color=INK)
    a.set_xticks(range(len(cases))); a.set_xticklabels([c[0] for c in cases], fontsize=7)
    a.set_ylabel("US$ bn/yr (2026), pre-tax"); a.set_ylim(-40, 780); a.grid(axis="y", color=GRID, lw=0.5); a.set_axisbelow(True)
    a.legend(fontsize=6, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2, frameon=False)
    a.set_ylim(-40, 640)
    a.set_title("A  Transport cost with gas (no building blend) and after gas", fontsize=8)
    f = S["post_gas_least_cost"]["fuel_supply"]; y_ = f["years"]
    def sig(v):
        return f"{v / 1e6:.0f} million yr" if v >= 1e6 else f"{float(f'{v:.2g}'):,.0f} yr"
    rows = [("HTGR fleet, once-through HALEU,\nall identified world U", y_["once_through_world_identified_u"], C["red"]),
            ("Breeder fleet (fast),\nU.S. depleted-U stockpile", y_["closed_us_depleted_u"], C["blue"]),
            ("Breeder fleet (thorium),\nU.S. thorium resources", y_["closed_us_thorium"], C["violet"]),
            ("Breeder fleet (thorium),\nworld thorium resources", y_["closed_world_thorium"], C["violet"]),
            ("Breeder fleet (fast),\nworld identified uranium", y_["closed_world_identified_u"], C["blue"]),
            ("Breeder fleet (fast), seawater U\n(not a practical forecast)", y_["closed_seawater_u"], "#bdbab2")]
    yy = np.arange(len(rows))[::-1]
    for yi, (lab, v, col) in zip(yy, rows):
        b.barh(yi, v, height=0.6, color=col); b.text(v * 1.3, yi, sig(v), va="center", fontsize=6.5, color=INK2)
    b.set_xscale("log"); b.set_xlim(100, 1e11); b.set_yticks(yy); b.set_yticklabels([r[0] for r in rows], fontsize=6.8)
    b.set_xlabel("Resource / annual use, years (log scale): theoretical upper bounds,\nnot fleet lifetimes"); b.grid(axis="x", color=GRID, lw=0.5); b.set_axisbelow(True)
    b.set_title(f"B  Fuel for {f['thermal_twh']:,.0f} TWh of reactor heat a year (post-gas least cost)", fontsize=8)
    save(fig, "ScienceFigS11_post_gas")


def fig_s12_sustainable_fission():
    fig, (a, b) = plt.subplots(1, 2, figsize=(11.5, 4.6), gridspec_kw=dict(width_ratios=[1, 1.1], wspace=0.75))
    cases = [("Gas era\n(headline)", "least_cost", C["blue"]), ("After gas,\nHTGR fleet", "post_gas_least_cost", C["blue"]),
             ("Sustainable fission,\nwith wind + solar", "sustainable_fission", C["violet"]),
             ("Sustainable fission,\nnuclear only", "sustainable_fission_nuclear_only", C["violet"]),
             ("Nuclear only,\ncheap S-I hydrogen", "sustainable_fission_nuclear_only_si_cheap", C["violet"]),
             ("Nuclear only,\nbreeder premium", "sustainable_fission_nuclear_only_premium", C["red"])]
    y = np.arange(len(cases))[::-1]
    for yi, (lab, k, col) in zip(y, cases):
        v = S[k]["transport_cost_bn"]; a.barh(yi, v, height=0.6, color=col)
        a.text(v - 8, yi, f"${v:.0f} bn  ({S[k]['hubs']:.0f} hubs)", va="center", ha="right", fontsize=6.8, color="white", weight="bold")
    pv = D["petroleum"]["prices"]["late_2025"]["pretax_bn"] + D["petroleum"]["pipeline_gas_bn"]
    a.axvline(pv, color=INK, lw=1); a.text(pv + 8, y[-1], f"petroleum,\nlate-2025:\n{pv:.0f}", ha="left", va="center", fontsize=6.3, color=INK)
    a.set_yticks(y); a.set_yticklabels([c[0] for c in cases], fontsize=7); a.set_xlim(0, 700)
    a.set_xlabel("Transport cost, US$ bn/yr (2026), pre-tax"); a.grid(axis="x", color=GRID, lw=0.5); a.set_axisbelow(True)
    a.set_title("A  Transport cost: gas era, after gas, sustainable fission", fontsize=8)
    parts = [("Electricity", "electricity", C["blue"]), ("Refinery steam (HTL, upgrading)", "refinery_process_steam", C["orange"]),
             ("Steam electrolysis and drying", "htse_steam_and_drying", C["aqua"]), ("Sulfur-iodine heat", "sulfur_iodine_heat", C["red"]),
             ("Greenhouses and fish farms", "food_heat", C["green"]), ("Conversion losses and reject heat", "conversion_losses_and_reject", "#bdbab2")]
    rows = [("With wind + solar", "sustainable_fission"), ("Nuclear only", "sustainable_fission_nuclear_only"),
            ("Nuclear only,\ncheap S-I", "sustainable_fission_nuclear_only_si_cheap")]
    yy = np.arange(len(rows))[::-1]
    for yi, (lab, k) in zip(yy, rows):
        e = S[k]["hub_energy_twh"]; x0 = 0
        for nm, kk, col in parts:
            v = max(e[kk], 0.0)
            b.barh(yi, v, left=x0, height=0.6, color=col, edgecolor="white", lw=0.8, label=nm if yi == yy[0] else None); x0 += v
        b.text(x0 + 40, yi, f"{e['thermal']:,.0f} TWh(th)", va="center", fontsize=6.8, color=INK2)
    b.set_yticks(yy); b.set_yticklabels([r[0] for r in rows], fontsize=7); b.set_xlim(0, 6200)
    b.set_xlabel("Breeder-fleet heat by use, TWh/yr"); b.grid(axis="x", color=GRID, lw=0.5); b.set_axisbelow(True)
    b.legend(fontsize=6, loc="upper center", bbox_to_anchor=(0.45, -0.14), ncol=2, frameon=False)
    b.set_title("B  Where the breeder fleet's heat goes", fontsize=8)
    save(fig, "ScienceFigS12_sustainable_fission")


if __name__ == "__main__":
    fig1(); print("ok ScienceFig1"); fig2_fig3(); print("ok ScienceFig2, ScienceFig3"); fig4(); print("ok ScienceFig4"); fig_s1_grid_harvester(); print("ok ScienceFigS1"); fig_s10_heat_and_boundaries(); print("ok ScienceFigS10"); fig_s11_post_gas(); print("ok ScienceFigS11"); fig_s12_sustainable_fission(); print("ok ScienceFigS12")
