"""Figures and maps for the v2 U.S. model.  Run after us2_model.py.  Writes Map*/Fig*.png (300 dpi) and .pdf into this folder."""
import json, csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Circle
from matplotlib.lines import Line2D
import us2_basemap as M
import us2_inputs as I
from us2_model import reactor_cost

HERE = Path(__file__).resolve().parent; OUT = HERE; FIG = HERE  # flat layout
C = {"blue": "#2a78d6", "orange": "#eb6834", "aqua": "#1baf7a", "yellow": "#eda100", "magenta": "#e87ba4",
     "green": "#008300", "violet": "#6250d6", "red": "#e34948"}
INK, INK2, MUTED, GRID, LAND, SEA = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1", "#f4f2ec", "#e3eef7"
plt.rcParams.update({"font.size": 8, "font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.titlesize": 9, "axes.titleweight": "bold", "axes.titlelocation": "left", "legend.frameon": False,
                     "savefig.dpi": 300, "pdf.fonttype": 42})
S = json.load(open(OUT / "scenarios.json")); D = S["design"]; LC = S["least_cost"]; SS = S["design_sweet_spot"]
MCS = json.load(open(OUT / "monte_carlo_summary.json")); TR = json.load(open(OUT / "transition.json"))
GC = json.load(open(OUT / "gas_depletion_central.json")); GG = json.load(open(OUT / "gas_depletion_grid.json"))
RC = json.load(open(OUT / "reactor_costs.json")); SM = list(csv.DictReader(open(OUT / "sweep_merit.csv")))
MERIT = json.load(open(OUT / "seaweed_merit.json"))
SPECIES_COL = {"cold_kelp": C["blue"], "giant_kelp": C["green"], "giant_kelp_warm": C["aqua"], "kelp_red_rotation": C["violet"], "red_green": C["magenta"]}
SPECIES_LAB = {"cold_kelp": "Cold-water kelps: sugar, winged, ribbon & bull kelp", "giant_kelp": "Giant kelp (Macrocystis), upwelling coast",
               "giant_kelp_warm": "Giant kelp, warm-tolerant southern strains", "kelp_red_rotation": "Winter sugar kelp + summer red Gracilaria",
               "red_green": "Warm-water red & green seaweeds (Gracilaria, Ulva, Sargassum)"}
REG_STYLE = {"onshore_wind": ("#9fd8c4", "Onshore wind belt"), "solar": ("#f6d58a", "Utility solar regions"),
             "bamboo": ("#3f9d3f", "Clumping bamboo (frost-free / zone 9)"), "hemp": ("#b8a24a", "Grain-and-stalk hemp rotation"),
             "corn_ethanol": ("#f2a571", "Corn Belt ethanol -> jet (ATJ)"), "residues": ("#b58a65", "Forest & crop residues")}


def save(fig, name):
    fig.savefig(FIG / f"{name}.png", dpi=300, bbox_inches="tight"); fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight"); plt.close(fig)


def basemap(ax, xlim=(-127.0, -65.0), ylim=(23.8, 50.2), labels=True):
    ax.set_facecolor(SEA)
    ax.add_patch(Polygon(M.CONUS, closed=True, fc=LAND, ec=MUTED, lw=0.6, zorder=1))
    for ln in M.STATE_LINES:
        xy = np.array(ln); ax.plot(xy[:, 0], xy[:, 1], color="#bdbab2", lw=0.45, zorder=1.5)
    for pts in M.LAKES.values():
        ax.add_patch(Polygon(pts, closed=True, fc=SEA, ec=MUTED, lw=0.4, zorder=2))
    if labels:
        for s_, (x, y) in M.STATE_LABELS.items():
            if xlim[0] < x < xlim[1] and ylim[0] < y < ylim[1]:
                ax.text(x, y, s_, fontsize=5.2, color="#a3a09a", ha="center", va="center", zorder=1.6)
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect(1.25); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)


def allocate_hubs(n):
    w = np.array([h[3] for h in M.HUB_SITES], float); raw = n * w / w.sum(); base = np.floor(raw).astype(int)
    for i in np.argsort(-(raw - base))[: int(round(n)) - base.sum()]: base[i] += 1
    return base


def draw_regions(ax, keys, alpha=0.55):
    for k in keys:
        col, _ = REG_STYLE[k]
        for poly in M.REGIONS[k]:
            ax.add_patch(Polygon(poly, closed=True, fc=col, ec="none", alpha=alpha, zorder=1.8))


def draw_corridors(ax, lw=1.5, col=None, label=False):
    for name, cities in M.CORRIDORS.items():
        xy = np.array([M.CITIES[c] for c in cities]); ax.plot(xy[:, 0], xy[:, 1], color=col or C["blue"], lw=lw, zorder=3, solid_capstyle="round")
        if label:
            m = len(xy) // 2; ax.text(xy[m, 0], xy[m, 1] + 0.35, f"{name}\n{M.CORRIDOR_KM[name]:,} km", fontsize=5.6, color=C["blue"],
                                      ha="center", zorder=7, bbox=dict(fc="white", ec="none", alpha=0.7, pad=0.4))


def draw_seaweed(ax, label=True, fs=5.6):
    xl, yl = ax.get_xlim(), ax.get_ylim()
    for z in D["seaweed"]:
        x0, y0, w, h = z["box"]; col = SPECIES_COL[z["color"]]
        if not (xl[0] < x0 + w / 2 < xl[1] and yl[0] < y0 + h / 2 < yl[1]): continue
        ax.add_patch(Rectangle((x0, y0), w, h, fc=col, ec="white", lw=0.8, alpha=0.88, zorder=5))
        if label:
            right = z["zone"] not in ("wa", "or", "nca", "cca", "sca")
            tx = x0 + w + 0.2 if right else x0 - 0.2
            ax.text(tx, y0 + h / 2, f"{z['wind_gw']:.0f} GW · {z['dry_mt']:.1f} Mt", fontsize=fs, va="center", ha="left" if right else "right", color=INK, zorder=7)


# ---------------------------------------------------------------------------------------------- Map 1: everything
def map_master():
    fig, ax = plt.subplots(figsize=(12, 7.4)); basemap(ax)
    draw_regions(ax, ["onshore_wind", "solar", "corn_ethanol", "residues", "hemp", "bamboo"])
    draw_corridors(ax, lw=1.3)
    built = {z["zone"]: z for z in SS["seaweed"] if z["dry_mt"] > 0}
    for z in D["seaweed"]:
        x0, y0, w, h = z["box"]; col = SPECIES_COL[z["color"]]; b = z["zone"] in built
        ax.add_patch(Rectangle((x0, y0), w, h, fc=col if b else "none", ec=col if not b else "white", lw=0.9, alpha=0.9, hatch=None if b else "////", zorder=5))
        right = z["zone"] not in ("wa", "or", "nca", "cca", "sca")
        t = f"{built[z['zone']]['wind_gw']:.0f} GW · {built[z['zone']]['dry_mt']:.1f} Mt" if b else f"expansion: {z['wind_gw']:.0f} GW"
        ax.text(x0 + w + 0.2 if right else x0 - 0.2, y0 + h / 2, t, fontsize=5.6, va="center", ha="left" if right else "right", color=INK if b else INK2, zorder=7)
    n = allocate_hubs(SS["hubs"])
    for (nm, x, y, w, role), k in zip(M.HUB_SITES, n):
        if k <= 0: continue
        ax.scatter(x, y, s=25 + 9 * k, marker="h", c=C["red"], edgecolors="white", linewidths=0.7, zorder=8)
        ax.text(x, y, str(k), fontsize=5.2, color="white", ha="center", va="center", zorder=9, weight="bold")
    for nm, (x, y) in M.CANADA_ENTRY.items():
        ax.plot(x, y, marker="v", color=C["violet"], ms=6, zorder=6)
    for pts in M.NEW_PIPES:
        xy = np.array(pts); ax.plot(xy[:, 0], xy[:, 1], color=C["violet"], lw=1.2, ls=(0, (4, 2)), zorder=4)
    h = [Line2D([], [], marker="h", ls="", mfc=C["red"], mec="white", ms=9, label=f"HTGR cascade hubs: number = four-reactor hubs at the site ({SS['hubs']:.0f} hubs, {SS['reactors']:.0f} reactors)"),
         Line2D([], [], color=C["blue"], lw=1.5, label="Electrified Interstate corridors (catenary eHighways)"),
         Line2D([], [], color=C["violet"], marker="v", lw=0, label="Canada->U.S. gas entry points;  dashed = new pipeline corridors")]
    h += [Rectangle((0, 0), 1, 1, fc=REG_STYLE[k][0], alpha=0.7, label=REG_STYLE[k][1]) for k in ("onshore_wind", "solar", "bamboo", "hemp", "corn_ethanol", "residues")]
    h += [Rectangle((0, 0), 1, 1, fc=v, label=f"Offshore wind + {SPECIES_LAB[k][0].lower() + SPECIES_LAB[k][1:]}") for k, v in SPECIES_COL.items()]
    h += [Rectangle((0, 0), 1, 1, fc="none", ec=INK2, hatch="////", label="Further offshore zones in the 515 GW large build (beyond the 220 GW diversification case)")]
    ax.legend(handles=h, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=2, fontsize=6.6)
    ax.set_title(f"Map 1. 220 GW diversification case, 2050: {SS['gw']['offshore_wind']:.0f} GW offshore wind with seaweed, {SS['gw']['solar']:.0f} GW solar, "
                 f"{SS['hubs']:.0f} reactor hubs ({SS['reactors']:.0f} reactors), eHighways, bamboo, hemp, ethanol (schematic)")
    save(fig, "Map1_national_system")


# ---------------------------------------------------------------------------------------------- Map 2: eHighways
def map_ehighways():
    fig, ax = plt.subplots(figsize=(12, 7.0)); basemap(ax)
    draw_regions(ax, ["onshore_wind", "solar"], alpha=0.35)
    draw_corridors(ax, lw=2.6, label=True)
    n = allocate_hubs(D["hubs"])
    for (nm, x, y, w, role), k in zip(M.HUB_SITES, n):
        if "eHighway" in role or k >= 5:
            ax.scatter(x, y, s=60, marker="h", c=C["red"], edgecolors="white", linewidths=0.7, zorder=8)
    for c_ in ("Seattle", "Los Angeles", "Phoenix", "Denver", "Dallas", "Houston", "Chicago", "Atlanta", "New York", "Miami", "Minneapolis", "Kansas City"):
        x, y = M.CITIES[c_]; ax.plot(x, y, "o", ms=2.6, color=INK, zorder=9); ax.text(x + 0.25, y - 0.45, c_, fontsize=6, zorder=9)
    tot = sum(M.CORRIDOR_KM.values())
    h = [Line2D([], [], color=C["blue"], lw=2.6, label=f"Catenary on 11 trunk Interstates ({tot:,} km) + ~4,500 km of connectors (I-25, I-65, I-81, I-85) = 40,000 km"),
         Line2D([], [], marker="h", ls="", mfc=C["red"], mec="white", ms=9, label="Firm nuclear supply points (HTGR hubs feeding the corridor substations)"),
         Rectangle((0, 0), 1, 1, fc=REG_STYLE["onshore_wind"][0], alpha=0.5, label="Onshore wind belt"),
         Rectangle((0, 0), 1, 1, fc=REG_STYLE["solar"][0], alpha=0.5, label="Utility solar regions")]
    ax.legend(handles=h, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=2, fontsize=6.8)
    e = D["enduse"]["el"]
    ax.set_title(f"Map 2. Electric highways: {e['hdv_ers_wire']:.0f} TWh/yr from the wire to 1.4 million catenary-hybrid trucks; "
                 f"~$140 bn to build (schematic routes)")
    save(fig, "Map2_ehighways")


# ---------------------------------------------------------------------------------------------- Map 3: seaweed species
def map_seaweed():
    fig = plt.figure(figsize=(12, 7.2))
    axP = fig.add_axes([0.0, 0.08, 0.30, 0.86]); axA = fig.add_axes([0.33, 0.30, 0.40, 0.64]); axG = fig.add_axes([0.33, 0.0, 0.40, 0.27])
    axT = fig.add_axes([0.75, 0.05, 0.25, 0.9]); axT.axis("off")
    basemap(axP, (-128.5, -116.0), (31.5, 49.3)); basemap(axA, (-82.5, -66.0), (29.5, 45.5)); basemap(axG, (-98.5, -86.5), (25.5, 31.2), labels=False)
    for a in (axP, axA, axG):
        draw_seaweed(a, fs=6.2)
    ports = {"Grays Harbor": (-124.0, 46.95), "Coos Bay": (-124.2, 43.4), "Humboldt Bay": (-124.15, 40.8), "Morro Bay": (-120.85, 35.37),
             "Long Beach": (-118.2, 33.75), "Portland ME": (-70.25, 43.65), "New Bedford": (-70.93, 41.63), "NY/NJ Harbor": (-74.05, 40.65),
             "Hampton Roads": (-76.3, 36.95), "Morehead City": (-76.7, 34.72), "Savannah": (-81.1, 32.08), "Galveston": (-94.8, 29.3),
             "Port Fourchon": (-90.2, 29.1)}
    for nm, (x, y) in ports.items():
        for a in (axP, axA, axG):
            xl, yl = a.get_xlim(), a.get_ylim()
            if xl[0] < x < xl[1] and yl[0] < y < yl[1]:
                a.plot(x, y, "s", ms=3.5, color=INK, zorder=9); a.text(x + 0.15, y + 0.15, nm, fontsize=5.6, zorder=9)
    axP.set_title("Pacific (floating wind)"); axA.set_title("Atlantic (fixed + Gulf of Maine floating)"); axG.set_title("Gulf of Mexico (fixed)")
    rows = sorted(D["seaweed"], key=lambda z: ["wa", "or", "nca", "cca", "sca", "gom", "sne", "nyb", "delmarva", "nc", "sab", "tx", "la"].index(z["zone"]))
    y = 0.99
    axT.text(0, y, "Species by zone (design case)", fontsize=8.5, weight="bold", va="top"); y -= 0.035
    for z in rows:
        axT.add_patch(Rectangle((0, y - 0.022), 0.04, 0.022, fc=SPECIES_COL[z["color"]], transform=axT.transAxes))
        star = "  (220 GW case)" if z["zone"] in ("wa", "or", "nca", "cca", "gom", "la") else ""
        axT.text(0.06, y, z["region"] + star, fontsize=6.6, weight="bold", va="top", transform=axT.transAxes)
        axT.text(0.06, y - 0.024, z["species"], fontsize=5.8, va="top", wrap=True, transform=axT.transAxes, color=INK2)
        axT.text(0.06, y - 0.048, f"{z['yield_t_ha']:.0f} t dry/ha/yr design · {z['seaweed_km2']:,.0f} km² · {z['vessels']:.0f} haul vessels", fontsize=5.8,
                 va="top", transform=axT.transAxes, color=INK2)
        y -= 0.073
    fl = D["fleet"]; gh = D["grid_harvester"]
    axT.text(0, y - 0.01, f"Fleet: {gh.get('engineering_units', 0):.0f} solar/wind Grid Harvesters, {fl['vessels']:.0f} battery-wingsail\nhaul vessels "
                          f"(charged at the wind-farm substations), {fl['drones']:,.0f} utility drones.", fontsize=6.6, va="top", transform=axT.transAxes)
    fig.suptitle(f"Map 3. Seaweed between turbines: {D['biomass_mt']['seaweed']:.0f} Mt dry/yr on {sum(z['seaweed_km2'] for z in D['seaweed']):,.0f} km² "
                 f"in {D['gw']['offshore_wind']:.0f} GW of offshore wind (boxes schematic)", x=0.0, ha="left", fontsize=9.5, weight="bold", y=1.0)
    save(fig, "Map3_seaweed_species")


# ---------------------------------------------------------------------------------------------- Map 4: land biomass & biorefineries
def map_biomass():
    fig, ax = plt.subplots(figsize=(12, 7.0)); basemap(ax)
    draw_regions(ax, ["corn_ethanol", "residues", "hemp", "bamboo"], alpha=0.75)
    L = D["liquids_twh"]
    notes = {"bamboo": (-76.5, 26.6, f"Bamboo (clumping): {D['bamboo']['mha']:.1f} Mha, {D['bamboo']['mt']:.0f} Mt/yr\n-> {L['bamboo']:.0f} TWh fuel at ${D['bamboo']['cost_t']:.0f}/t"),
             "hemp": (-112.5, 48.4, f"Hemp: {D['hemp']['mha']:.1f} Mha, {D['hemp']['seed_mt']:.1f} Mt seed\n({D['hemp']['oil_mt']:.1f} Mt oil -> fuel, {D['hemp']['meal_mt']:.1f} Mt protein meal -> food)\n+ {D['hemp']['stalk_mt']:.0f} Mt stalks -> HTL: {L['hemp']:.0f} TWh fuel"),
             "corn": (-87.0, 47.6, f"Corn Belt: {D['biomass_mt']['corn_ethanol_bgal']:.0f} bn gal ethanol -> {D['biomass_mt']['atj_ethanol_bgal']:.0f} bn gal to jet\n= {L['corn_ethanol_atj']:.0f} TWh"),
             "res": (-76.5, 30.0, f"Residues & perennial grasses: {D['biomass_mt']['residues_grasses']:.0f} Mt -> {L['residues_and_grasses']:.0f} TWh")}
    for k, (x, y, t) in notes.items():
        ax.text(x, y, t, fontsize=6.6, ha="center", va="center", bbox=dict(fc="white", ec=GRID, alpha=0.9, pad=2), zorder=9)
    n = allocate_hubs(D["hubs"])
    for (nm, x, y, w, role), k in zip(M.HUB_SITES, n):
        if any(s in role for s in ("bamboo", "hemp", "ethanol", "residue", "refiner")):
            ax.scatter(x, y, s=55, marker="h", c=C["red"], edgecolors="white", linewidths=0.7, zorder=8)
    h = [Rectangle((0, 0), 1, 1, fc=REG_STYLE[k][0], alpha=0.8, label=REG_STYLE[k][1]) for k in ("bamboo", "hemp", "corn_ethanol", "residues")]
    h += [Line2D([], [], marker="h", ls="", mfc=C["red"], mec="white", ms=9, label="Cascade hubs upgrading biocrude, FT liquids and ethanol to jet and diesel")]
    ax.legend(handles=h, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=3, fontsize=6.8)
    ax.set_title("Map 4. Where the land-based liquid-fuel feedstocks would grow (schematic regions)")
    save(fig, "Map4_land_biomass")


# ---------------------------------------------------------------------------------------------- Fig: liquid fuels & energy
def fig_liquids():
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.2), gridspec_kw=dict(width_ratios=[1.1, 1]))
    L = D["liquids_twh"]; eu = D["enduse"]
    items = [("Crop & forest residues,\nperennial grasses", L["residues_and_grasses"], "#b58a65"), ("Corn ethanol -> jet", L["corn_ethanol_atj"], C["orange"]),
             ("Seaweed (dried, FT + H2)", L["seaweed"], C["blue"]), ("Bamboo", L["bamboo"], C["green"]), ("Hemp oil + stalks", L["hemp"], C["yellow"]),
             ("Oils & fats (HEFA)", L["oils_hefa"], C["violet"])]
    items = [i for i in items if i[1] > 0.5]
    y = np.arange(len(items))[::-1]
    a.barh(y, [i[1] for i in items], color=[i[2] for i in items], height=0.62)
    for yi, (lab, v, col) in zip(y, items): a.text(v + 10, yi, f"{v:,.0f} TWh ({100 * v / sum(i[1] for i in items):.0f}%)", va="center", fontsize=7.5)
    a.set_yticks(y); a.set_yticklabels([i[0] for i in items], fontsize=7.5); a.set_xlabel("TWh/yr of liquid fuel (2050, design)")
    a.set_xlim(0, max(i[1] for i in items) * 1.35); a.grid(axis="x", color=GRID, lw=0.5); a.set_axisbelow(True)
    a.set_title(f"(a) {eu['liq_total']:,.0f} TWh/yr of liquids; {eu['jet']:,.0f} TWh is jet fuel")
    segs = [("Aviation", "air"), ("Trucks", "hdv"), ("Marine", "marine"), ("Farm machines", "farm"), ("Construction\n& mining", "construction"), ("Rail", "rail"), ("Light-duty", "ldv")]
    x = np.arange(len(segs)); base = eu["base"]
    el = eu["el"]; e_seg = dict(air=0, hdv=el["hdv_ers_wire"] + el["hdv_ers_battery"] + el["hdv_bev"] + el["hdv_re"], marine=el["marine"], farm=el["farm"],
                                construction=el["construction"], rail=el["rail"], ldv=el["ldv"])
    b.bar(x - 0.2, [base[k] for _, k in segs], 0.38, color="#bdbab2", label="2024 fuel")
    b.bar(x + 0.2, [e_seg[k] for _, k in segs], 0.38, color=C["blue"], label="2050 electricity")
    b.bar(x + 0.2, [eu["h2_twh"].get(k, 0) for _, k in segs], 0.38, bottom=[e_seg[k] for _, k in segs], color=C["aqua"], label="2050 hydrogen")
    b.bar(x + 0.2, [eu["liq"].get(k, 0) for _, k in segs], 0.38, bottom=[e_seg[k] + eu["h2_twh"].get(k, 0) for _, k in segs], color=C["orange"], label="2050 liquid fuel")
    b.set_xticks(x); b.set_xticklabels([s for s, _ in segs], fontsize=6.6); b.set_yscale("log"); b.set_ylim(10, 8000)
    b.set_ylabel("TWh/yr (log scale)"); b.legend(fontsize=6.6, ncol=2); b.grid(axis="y", color=GRID, lw=0.5); b.set_axisbelow(True)
    b.set_title("(b) Energy by segment, 2024 vs 2050")
    save(fig, "Fig01_liquid_fuels_and_segments")


# ---------------------------------------------------------------------------------------------- Fig: sweet spot
def fig_sweetspot():
    fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.3), gridspec_kw=dict(width_ratios=[1.2, 1], wspace=0.55))
    for yl, col, lab in (("1", C["blue"], "design yields"), ("2", C["green"], "learning yields")):
        rows = [r for r in SM if str(int(float(r["yield_level"]))) == yl]
        gw = [float(r["osw_gw"]) for r in rows]; cost = [float(r["cost_bn"]) for r in rows]
        a.plot(gw, cost, "-o", color=col, ms=3.5, lw=1.8, label=f"System cost, {lab}")
        if yl == "1":
            for r in rows[1:]:
                a.text(float(r["osw_gw"]), float(r["cost_bn"]) - 9, r["last_zone"], fontsize=5.6, ha="center", color=INK2)
    rows = [r for r in SM if str(int(float(r["yield_level"]))) == "1"]
    ex = [float(r["export_twh"]) for r in rows]; gw = [float(r["osw_gw"]) for r in rows]
    first_exp = next((g for g, e in zip(gw, ex) if e > 1), max(gw))
    a.axvspan(175, 225, color=C["yellow"], alpha=0.18); a.text(258, 575, "220 GW diversification case:\nPacific kelp coast (WA-central CA),\nGulf of Maine, Mississippi plume", ha="center", fontsize=6.4)
    a.axvline(first_exp, color=C["red"], lw=1, ls="--"); a.text(first_exp + 5, 470, "beyond here, surplus\npower is sold at a loss", fontsize=6.4, color=C["red"])
    pet = D["petroleum"]["prices"]["late_2025"]["pretax_bn"] + D["petroleum"]["pipeline_gas_bn"]
    a.axhline(pet, color=INK, lw=0.8); a.text(250, pet + 3, f"petroleum at late-2025 prices (pre-tax): ${pet:.0f} bn", fontsize=6.6)
    a.set_xlabel("Offshore wind built (GW), zones added cheapest-seaweed-first"); a.set_ylabel("Transport system cost, $ bn/yr"); a.legend(fontsize=6.8, loc="lower right")
    a.grid(color=GRID, lw=0.5); a.set_axisbelow(True); a.set_title("(a) Cost rises with every offshore zone added")
    c0 = float(rows[0]["cost_bn"]); a.annotate(f"least-cost system:\n0 GW, ${c0:.0f} bn", xy=(0, c0), xytext=(40, c0 + 30), fontsize=6.6,
                                                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.7))
    m = MERIT["design"]; ml = {r["zone"]: r for r in MERIT["learning"]}
    y = np.arange(len(m))[::-1]
    b.barh(y, [r["best_usd_mwh"] for r in m], color=C["blue"], height=0.6, label="design yields")
    b.scatter([ml[r["zone"]]["best_usd_mwh"] for r in m], y, color=C["green"], zorder=5, s=18, label="learning yields")
    jet_marg = (D["liquid_shadow_usd_mwh"] or 0) + (D["jet_shadow_usd_mwh"] or 0)
    b.axvline(jet_marg, color=C["red"], lw=1, ls="--"); b.text(jet_marg + 4, len(m) - 0.6, f"marginal jet fuel\nfrom land: ${jet_marg:.0f}/MWh", fontsize=6.4, color=C["red"])
    b.set_yticks(y); b.set_yticklabels([r["region"].split("(")[0].strip() for r in m], fontsize=6.4)
    b.set_xlabel("Seaweed fuel cost, $/MWh (biomass + haul + refining − fertiliser)"); b.legend(fontsize=6.6, loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=2)
    b.grid(axis="x", color=GRID, lw=0.5); b.set_axisbelow(True); b.set_title("(b) Merit order of seaweed zones")
    save(fig, "Fig02_offshore_sweet_spot")


# ---------------------------------------------------------------------------------------------- Fig: reactor costs
def fig_reactors():
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.0))
    n = np.arange(1, 801)
    for case, col in (("low", C["green"]), ("central", C["blue"]), ("high", C["red"])):
        c = I.REACTOR_COST[case]; foak = c["boak_kwe"] * c["foak_mult"]; bb = np.log2(1 - c["learning"])
        a.plot(n, foak * n ** bb, color=col, lw=1.8, label=f"{case}: FOAK ${foak:,.0f}/kWe, learning {100 * c['learning']:.0f}%/doubling")
    a.axhline(15.1e9 / 1.2e6, color=INK2, lw=0.8, ls=":"); a.text(300, 15.1e9 / 1.2e6 + 300, "Darlington BWRX-300 (4 units, all-in incl. interest)", fontsize=6.4)
    a.axhline(9000, color=MUTED, lw=0.8, ls="--"); a.text(300, 9200, "DOE Liftoff FOAK", fontsize=6.4, color=INK2)
    a.axhline(3600, color=MUTED, lw=0.8, ls="--"); a.text(300, 3750, "DOE Liftoff NOAK", fontsize=6.4, color=INK2)
    a.axvline(D["reactors"], color=INK, lw=0.8); a.text(D["reactors"] + 8, 14000, f"design fleet\n{D['reactors']:.0f} reactors", fontsize=6.4)
    a.set_xscale("log"); a.set_xlabel("Reactor number in the fleet (80 MWe HTGR modules)"); a.set_ylabel("Overnight cost, $/kWe")
    a.legend(fontsize=6.4); a.grid(color=GRID, lw=0.5); a.set_axisbelow(True); a.set_title("(a) Learning curve: cost of the nth reactor")
    cases = ["low", "central", "high"]; vals = [RC[c]["fleet_avg_kwe_with_idc"] for c in cases]
    b.bar(cases, vals, color=[C["green"], C["blue"], C["red"]], width=0.55)
    for i, c in enumerate(cases):
        b.text(i, vals[i] + 200, f"${vals[i]:,.0f}/kWe\n(${RC[c]['fleet_avg_kwt_with_idc']:,.0f}/kWt)\nfleet ${RC[c]['fleet_capex_bn']:,.0f} bn", ha="center", fontsize=7)
    b.set_ylabel("Fleet-average cost incl. interest during construction, $/kWe"); b.set_ylim(0, max(vals) * 1.4)
    b.grid(axis="y", color=GRID, lw=0.5); b.set_axisbelow(True); b.set_title(f"(b) Fleet average for {RC['central']['n_units']} reactors")
    save(fig, "Fig03_reactor_costs")


# ---------------------------------------------------------------------------------------------- Fig: costs
def fig_costs():
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.6), gridspec_kw=dict(width_ratios=[1.35, 1]))
    groups = [("Electricity generation", ["electricity_generation", "process_heat_equipment"], C["blue"]),
              ("Grid, chargers, eHighways, rail", ["transmission_distribution", "charging", "electric_highways", "rail_electrification"], C["violet"]),
              ("Reactor hubs, pyrolysis, gas, H2 delivery", ["htgr_hubs", "pyrolysis_plants", "natural_gas", "electrolysis", "h2_delivery"], C["red"]),
              ("Land biomass, hemp, ethanol, refineries", ["land_biomass", "hemp_net_of_meal", "biorefineries", "hefa_oils", "ethanol", "residual_pipeline_gas"], C["orange"]),
              ("Seaweed farms, harvest, haul, refining", ["seaweed_farms_harvest_haul", "seaweed_refining"], C["aqua"]),
              ("Vehicles & machines (net premium)", ["vehicles_and_machines_net"], C["yellow"])]
    cases = [("Design\n(515 GW offshore)", S["design"]), (f"Diversification\n({S['design_sweet_spot']['gw']['offshore_wind']:.0f} GW offshore)", S["design_sweet_spot"]), ("Least-cost", S["least_cost"])]
    for i, (lab, r) in enumerate(cases):
        btm = 0; sb = r["blend_share_of_h2"]
        for g, keys, col in groups:
            v = sum(r["costs_bn"][k] for k in keys) * ((1 - sb) if g.startswith("Reactor") else 1)
            a.bar(i, v, bottom=btm, color=col, edgecolor="white", lw=0.8, width=0.6, label=g if i == 0 else None); btm += v
        cr = sum(r["credits_bn"].values())
        a.bar(i, cr, color=C["green"], width=0.6, label="Credits: surplus power, carbon, fertiliser, heat" if i == 0 else None)
        a.text(i, btm + 15, f"${r['transport_cost_bn']:.0f} bn", ha="center", fontsize=8, weight="bold")
    pet = D["petroleum"]["prices"]; pg = D["petroleum"]["pipeline_gas_bn"]
    for j, key in enumerate(("late_2025", "nov_2026")):
        v = pet[key]["pretax_bn"] + pg; a.bar(3 + j, v, color="#bdbab2", width=0.6); a.text(3 + j, v + 15, f"${v:.0f} bn", ha="center", fontsize=8)
    q = MCS["design"]["transport_cost_bn"]; a.errorbar(0.36, q["p50"], yerr=[[q["p50"] - q["p5"]], [q["p95"] - q["p50"]]], fmt="o", color=INK, ms=3.5, capsize=3)
    q = MCS["least_cost"]["transport_cost_bn"]; a.errorbar(2.36, q["p50"], yerr=[[q["p50"] - q["p5"]], [q["p95"] - q["p50"]]], fmt="o", color=INK, ms=3.5, capsize=3)
    a.set_xticks(range(5)); a.set_xticklabels([c[0] for c in cases] + ["Petroleum,\nlate-2025\n(pre-tax)", "Petroleum,\nNov-2026\n(pre-tax)"], fontsize=6.4)
    a.set_ylabel("$ bn/yr (2026 dollars)"); a.set_ylim(-80, 1050); a.legend(fontsize=6.0, loc="upper left")
    a.grid(axis="y", color=GRID, lw=0.5); a.set_axisbelow(True); a.set_title("(a) 2050 cost vs today's fuel bill (incl. farm & construction diesel)")
    mc = list(csv.DictReader(open(OUT / "monte_carlo_design.csv"))); ml = list(csv.DictReader(open(OUT / "monte_carlo_least_cost.csv")))
    bins = np.linspace(0.4, 1.5, 45)
    for rows, col, lab in ((mc, C["blue"], "design"), (ml, C["green"], "least-cost")):
        r25 = np.array([float(r["transport_cost_bn"]) / float(r["petro_2025"]) for r in rows])
        b.hist(r25, bins=bins, color=col, alpha=0.65, density=True, label=f"{lab}: cheaper than late-2025 fuel in {100 * np.mean(r25 < 1):.0f}% of draws")
    b.axvline(1, color=INK, lw=1); b.set_xlabel("System cost ÷ petroleum at late-2025 prices"); b.set_yticks([])
    b.legend(fontsize=6.6, loc="upper left"); b.set_ylim(0, b.get_ylim()[1] * 1.3); b.set_title("(b) Monte Carlo (1,000 + 500 draws)")
    save(fig, "Fig04_costs")


# ---------------------------------------------------------------------------------------------- Fig: heat cascade + food
def fig_cascade_food():
    hb = SS["hub_spec"]; F = SS["food"]
    # V6: distinguish full-dose cattle-feed target from nutrient-only RAS output.
    nb = json.load(open(OUT / "nutrient_balance_v6.json"))["scenarios"]["design_sweet_spot"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.2), gridspec_kw=dict(width_ratios=[1.0, 1], wspace=0.75))
    st = [("750 °C helium: methane preheat + turbine", hb["q_pyro_mw"], C["red"]), ("565 °C steam: electricity (net)", hb["mwe"], C["blue"]),
          ("350–400 °C: HTL reactors, hydrotreating", hb["q_mid_mw"], C["orange"]), ("130–180 °C: seaweed drying, distillation, grain drying", hb["q_dry_mw"], C["yellow"]),
          ("35–70 °C used: greenhouses, fish & shrimp, seaweed tanks", hb["low_used_mw"], C["aqua"]), ("Unused reject heat", hb["reject_mw"] - hb["low_used_mw"], "#cfcdc6")]
    y = np.arange(len(st))[::-1]
    for yi, (lab, mw, col) in zip(y, st): a.barh(yi, mw, color=col, height=0.6); a.text(mw + 5, yi, f"{mw:.0f} MW", va="center", fontsize=7.5)
    a.set_yticks(y); a.set_yticklabels([s[0] for s in st], fontsize=7); a.set_xlim(0, 300); a.set_xlabel("MW per 800 MWt hub (4 reactors)")
    a.grid(axis="x", color=GRID, lw=0.5); a.set_axisbelow(True); a.set_title("(a) Heat cascade of one hub")
    items = [("Greenhouse vegetables", F["vegetables_mt"], f"{F['greenhouse_ha']:,.0f} ha"), ("Warm-water fish & shrimp", F["fish_shrimp_mt"], "RAS farms"),
             ("Grain dried with hub heat", F["grain_dried_mt"], "near hubs"), ("Hemp seed (food + oil)", F["hemp_seed_mt"], f"{SS['hemp']['mha']:.0f} Mha"),
             ("Red seaweed feed for cattle", F["asparagopsis"]["seaweed_mt_dry"], f"{F['asparagopsis']['mtco2e_cut']:.0f} Mt CO2e conditional; +{nb['external_target_n_kt']:.1f} kt N")]
    y = np.arange(len(items))[::-1]
    b.barh(y, [i[1] for i in items], color=[C["green"], C["blue"], C["yellow"], "#b8a24a", C["magenta"]], height=0.6)
    for yi, (lab, v, note) in zip(y, items): b.text(v * 1.15, yi, f"{v:,.1f} Mt  ({note})", va="center", fontsize=7.2)
    b.set_xscale("log"); b.set_xlim(0.1, 600); b.set_yticks(y); b.set_yticklabels([i[0] for i in items], fontsize=7.2)
    b.set_xlabel("Mt/yr (log scale)"); b.grid(axis="x", color=GRID, lw=0.5); b.set_axisbelow(True)
    b.set_title(f"(b) Gross output and grain drying, 220 GW diversification\n({SS['hubs']:.0f} hubs; grain drying is not new food; seaweed benefit conditional)")
    save(fig, "Fig05_cascade_food")


# ---------------------------------------------------------------------------------------------- Fig: carbon incl. vehicles
def fig_carbon():
    fig, ax = plt.subplots(figsize=(9, 3.8))
    al = D["carbon_alloc"]; y = np.arange(len(al))[::-1]
    cols = [C["red"], C["violet"], INK2, C["blue"], C["orange"], C["yellow"], C["green"], "#bdbab2"]
    ax.barh(y, [x["mt"] for x in al], color=cols[: len(al)], height=0.62)
    for yi, x in zip(y, al): ax.text(x["mt"] + 0.6, yi, f"{x['mt']:.2f} Mt @ ${x['value_usd_t']:,.0f}/t", va="center", fontsize=7)
    ax.set_yticks(y); ax.set_yticklabels([x["market"].split(":")[0].split("(")[0].strip()[:48] for x in al], fontsize=7)
    ax.set_xlim(0, max(x["mt"] for x in al) * 1.3); ax.set_xlabel("Mt solid carbon per year"); ax.grid(axis="x", color=GRID, lw=0.5); ax.set_axisbelow(True)
    ax.set_title(f"Figure 6. {D['carbon_mt']:.0f} Mt/yr of pyrolysis carbon: average value ${D['carbon_value_per_t']:.0f}/t; vehicle structures take 0.76 Mt")
    save(fig, "Fig06_carbon_markets")


# ---------------------------------------------------------------------------------------------- Fig: gas and transition
def fig_gas_transition():
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.0))
    for k, (l, col, ls) in {"none": ("No programme", MUTED, "-"), "design_no_canada": ("Programme, no Canada", C["red"], "-"),
                            "design_current_canada": ("Programme, Canada today", C["blue"], "-"), "design_plus4": ("Programme, Canada +4 Bcf/d", C["violet"], "--")}.items():
        rows = [r for r in GC[k]["rows"] if r["year"] <= 2140]
        a.plot([r["year"] for r in rows], [r["us_remaining_tcf"] for r in rows], color=col, ls=ls, lw=1.8, label=f"{l}: shortfall {GC[k]['first_shortfall_year']}")
    a.set_ylabel("U.S. recoverable gas remaining, Tcf"); a.legend(fontsize=6.6); a.grid(color=GRID, lw=0.5); a.set_axisbelow(True)
    a.set_title("(a) Natural gas (80% recoverable, LNG 30 Bcf/d)")
    rows = TR["with_e85"]["rows"]; yr = [r["year"] for r in rows]
    b.plot(yr, [r["baseline_mt"] for r in rows], color=MUTED, lw=1.8, label="Petroleum baseline")
    b.plot(yr, [r["case_no_e85_mt"] for r in rows], color=C["blue"], ls="--", lw=1.6, label="Transition without E85")
    b.plot(yr, [r["case_mt"] for r in rows], color=C["green"], lw=2.2, label="Transition with E85 bridge")
    b.fill_between(yr, [r["case_mt"] for r in rows], [r["baseline_mt"] for r in rows], color=C["green"], alpha=0.12)
    b.set_ylabel("Well-to-wheel Mt CO2e/yr"); b.legend(fontsize=6.6); b.grid(color=GRID, lw=0.5); b.set_axisbelow(True)
    b.set_title(f"(b) {TR['with_e85']['cum_avoided_2026_2050'] / 1e3:.0f} Gt avoided 2026–2050; {TR['with_e85']['cum_avoided_2026_2060'] / 1e3:.0f} Gt to 2060")
    save(fig, "Fig07_gas_and_transition")


if __name__ == "__main__":
    for f in (map_master, map_ehighways, map_seaweed, map_biomass, fig_liquids, fig_sweetspot, fig_reactors, fig_costs, fig_cascade_food, fig_carbon, fig_gas_transition):
        f(); print("ok", f.__name__)
