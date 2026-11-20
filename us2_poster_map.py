"""Full-size (poster) map of the whole U.S. transport decarbonisation system, 220 GW diversification case.

Layers: HTGR cascade hubs, offshore wind + seaweed zones (built and expansion) with species, seaweed haul routes
and landing ports, onshore wind, solar, bamboo, hemp, corn ethanol, residues, electric highways, farm digesters,
wastewater-plant digesters, gas basins, Canada entry points and new pipelines, LNG export terminals, and a side
panel with the main numbers.  Locations are schematic (hand-digitised, no GIS layers), not a siting study.

Flat layout: reads scenarios.json and gas_extension.json; writes Poster_US_system_map (.pdf vector, .png 200 dpi).
"""
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
from matplotlib.lines import Line2D
import us2_basemap as M
import us2_figures as F
from us2_figures import C, INK, INK2, SPECIES_COL, SPECIES_LAB, REG_STYLE, basemap, draw_regions, allocate_hubs

SS, D = F.SS, F.D
GX = json.load(open(F.HERE / "gas_extension.json"))

PORTS = {"wa": ("Grays Harbor", -124.0, 46.95), "or": ("Coos Bay", -124.2, 43.4), "nca": ("Humboldt Bay", -124.15, 40.8),
         "cca": ("Morro Bay", -120.85, 35.37), "sca": ("Long Beach", -118.2, 33.75), "gom": ("Portland ME", -70.25, 43.65),
         "sne": ("New Bedford", -70.93, 41.63), "nyb": ("NY/NJ Harbor", -74.05, 40.65), "delmarva": ("Hampton Roads", -76.3, 36.95),
         "nc": ("Morehead City", -76.7, 34.72), "sab": ("Savannah", -81.1, 32.08), "tx": ("Galveston", -94.8, 29.3),
         "la": ("Port Fourchon", -90.2, 29.1)}
# Schematic clusters of candidate livestock digesters (leading dairy and swine states in EPA AgSTAR) - not farm locations
DIGESTERS = {"dairy": [("Central Valley CA", -119.3, 36.3), ("Magic Valley ID", -114.6, 42.6), ("Wisconsin", -88.9, 44.4),
                       ("New York", -76.0, 42.8), ("Texas High Plains", -102.2, 34.4), ("Yakima WA", -120.4, 46.5),
                       ("Michigan", -84.9, 43.2), ("Pennsylvania", -76.4, 40.1), ("New Mexico", -104.3, 33.2),
                       ("N. Colorado", -104.6, 40.4), ("Central Arizona", -112.5, 33.1), ("Minnesota", -94.6, 45.6)],
             "swine": [("Iowa", -94.8, 42.6), ("E. North Carolina", -78.0, 35.0), ("S. Minnesota", -94.6, 44.0),
                       ("Illinois", -89.6, 40.9), ("Indiana", -86.6, 40.5), ("Oklahoma Panhandle", -101.4, 36.7),
                       ("N. Missouri", -93.0, 39.9), ("E. Nebraska", -97.4, 41.6)]}
WWTP = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "Washington", "Boston", "Detroit",
        "Atlanta", "Dallas", "San Francisco", "Seattle", "Miami", "Minneapolis", "Denver", "St. Louis", "Baltimore",
        "San Diego", "Kansas City", "Columbus", "Charlotte", "Tampa", "Las Vegas", "Salt Lake City", "Portland", "New Orleans", "San Antonio"]
HUB_LABEL_OFFSET = {"Seadrift / Coastal Bend TX": (-0.7, -0.15, "right"), "Florida (Tampa)": (-0.6, -0.1, "right"),
                    "Savannah / Brunswick GA": (-0.6, -0.1, "right")}
HUB_LABEL_LEADER = {"Houston Ship Channel": (-96.6, 26.2), "Port Arthur / Lake Charles": (-93.6, 25.6),
                    "Baton Rouge / St. James LA": (-90.6, 26.3), "Mobile / Pascagoula": (-87.4, 27.3)}
LNG = {"Sabine Pass / Cameron": (-93.6, 29.75), "Freeport": (-95.35, 28.95), "Corpus Christi": (-97.3, 27.85),
       "Plaquemines": (-89.7, 29.5), "Cove Point": (-76.4, 38.4)}


def main():
    plt.rcParams.update({"font.size": 11})
    fig = plt.figure(figsize=(36, 15.5))
    ax = fig.add_axes([0.005, 0.03, 0.74, 0.92]); side = fig.add_axes([0.755, 0.03, 0.24, 0.92]); side.axis("off")
    basemap(ax)
    draw_regions(ax, ["onshore_wind", "solar", "corn_ethanol", "residues", "hemp", "bamboo"], alpha=0.5)
    # regional labels
    for txt, x, y in (("Great Plains\nonshore wind", -100.6, 44.0), ("Desert Southwest\nsolar", -113.5, 34.6), ("Corn Belt ethanol\n-> jet fuel", -93.4, 41.4),
                      ("Southeastern pine\nresidues", -86.5, 33.3), ("Northern Plains hemp", -100.2, 47.6), ("Gulf Coast\nclumping bamboo", -96.3, 31.0),
                      ("Florida\nbamboo", -80.7, 27.0), ("Pacific NW\nforest residues", -122.6, 44.1)):
        ax.text(x, y, txt, fontsize=12, color=INK2, ha="center", va="center", style="italic", zorder=2.5)
    # electric highways
    for name, cities in M.CORRIDORS.items():
        xy = np.array([M.CITIES[c] for c in cities])
        ax.plot(xy[:, 0], xy[:, 1], color="white", lw=6.5, zorder=3, solid_capstyle="round")
        ax.plot(xy[:, 0], xy[:, 1], color=C["blue"], lw=3.6, zorder=3.1, solid_capstyle="round")
        m = len(xy) // 2; mx, my = (xy[m - 1] + xy[m]) / 2 if len(xy) > 2 else xy.mean(0)
        ax.text(mx, my, name, fontsize=11, color="white", weight="bold", ha="center", va="center", zorder=3.3,
                bbox=dict(boxstyle="round,pad=0.2", fc=C["blue"], ec="none"))
    # gas: basins, Canada entry, new pipes, LNG export
    for pts in M.NEW_PIPES:
        xy = np.array(pts); ax.plot(xy[:, 0], xy[:, 1], color=C["violet"], lw=2.4, ls=(0, (5, 3)), zorder=3.4)
    for nm, (x, y) in M.CANADA_ENTRY.items():
        ax.plot(x, y, marker="v", color=C["violet"], ms=15, mec="white", zorder=6); ax.text(x, y + 0.45, nm, fontsize=9.5, color=C["violet"], ha="center", zorder=6)
    for nm, (x, y) in M.GAS_BASINS.items():
        ax.plot(x, y, marker="D", color="#7a5c2e", ms=12, mec="white", zorder=6); ax.text(x + 0.35, y - 0.55, nm, fontsize=9.5, color="#7a5c2e", zorder=6)
    for nm, (x, y) in LNG.items():
        ax.plot(x, y, marker="P", color="#444444", ms=13, mec="white", zorder=6.5)
    # digesters
    for kind, mk, col in (("dairy", "o", "#8c564b"), ("swine", "s", "#d17b88")):
        for nm, x, y in DIGESTERS[kind]:
            ax.scatter(x, y, s=300, marker=mk, c=col, edgecolors="white", linewidths=1.2, zorder=7, alpha=0.95)
    for c_ in WWTP:
        x, y = M.CITIES[c_]; ax.scatter(x, y, s=170, marker="^", c="#2a9df4", edgecolors="#0b3d66", linewidths=1.0, zorder=7.2)
        ax.text(x + 0.3, y + 0.32, c_, fontsize=9.5, color=INK, zorder=7.3)
    # offshore wind + seaweed, haul routes, ports
    built = {z["zone"]: z for z in SS["seaweed"] if z["dry_mt"] > 0}
    for z in D["seaweed"]:
        x0, y0, w, h = z["box"]; col = SPECIES_COL[z["color"]]; b = z["zone"] in built
        ax.add_patch(Rectangle((x0, y0), w, h, fc=col if b else "none", ec="white" if b else col, lw=1.6, hatch=None if b else "////", alpha=0.92, zorder=5))
        nx, ny = x0 + w / 2, y0 + h / 2; pn, px, py = PORTS[z["zone"]]
        ax.annotate("", xy=(px, py), xytext=(nx, ny), arrowprops=dict(arrowstyle="-|>", color=INK2 if b else "#9a968c", lw=1.4,
                                                                    ls="-" if b else ":", mutation_scale=16), zorder=5.5)
        ax.plot(px, py, "s", ms=10, color=INK, mec="white", zorder=8); ax.text(px + 0.2, py - 0.45, pn, fontsize=9.5, zorder=8)
        right = z["zone"] not in ("wa", "or", "nca", "cca", "sca")
        t = (f"{z['region']}\n{built[z['zone']]['wind_gw']:.0f} GW, {built[z['zone']]['dry_mt']:.1f} Mt dry/yr" if b
             else f"{z['region']}\nexpansion: {z['wind_gw']:.0f} GW")
        ax.text(x0 + w + 0.25 if right else x0 - 0.25, y0 + h / 2, t, fontsize=10, va="center", ha="left" if right else "right",
                color=INK if b else INK2, zorder=9, bbox=dict(fc="white", ec="none", alpha=0.75, pad=1.0))
    # HTGR hubs
    n = allocate_hubs(SS["hubs"])
    for (nm, x, y, w, role), k in zip(M.HUB_SITES, n):
        if k <= 0: continue
        ax.scatter(x, y, s=260 + 60 * k, marker="h", c=C["red"], edgecolors="white", linewidths=1.5, zorder=10)
        ax.text(x, y, str(k), fontsize=11, color="white", ha="center", va="center", zorder=11, weight="bold")
        if nm in HUB_LABEL_LEADER:
            tx, ty = HUB_LABEL_LEADER[nm]
            ax.annotate(nm, xy=(x, y), xytext=(tx, ty), fontsize=8.8, color=C["red"], ha="center", va="top", zorder=11,
                        arrowprops=dict(arrowstyle="-", color=C["red"], lw=0.9), bbox=dict(fc="white", ec="none", alpha=0.85, pad=0.5))
            continue
        dx, dy, ha = HUB_LABEL_OFFSET.get(nm, (0.0, -0.62 - 0.02 * k, "center"))
        ax.text(x + dx, y + dy, nm, fontsize=8.8, color=C["red"], ha=ha, va="top", zorder=11,
                bbox=dict(fc="white", ec="none", alpha=0.75, pad=0.5))
    for s_, (x, y) in M.STATE_LABELS.items():
        ax.text(x, y, s_, fontsize=10, color="#9a968c", ha="center", va="center", zorder=2.2)
    ax.set_xlim(-132.5, -61.0); ax.set_ylim(24.0, 50.5); ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_visible(False)
    fig.text(0.008, 0.975, f"U.S. transport decarbonisation system, 2050: diversification case ({SS['gw']['offshore_wind']:.0f} GW offshore wind with seaweed)",
             fontsize=26, weight="bold", color=INK)
    fig.text(0.008, 0.955, "Reactor heat cascade, offshore wind-seaweed farms, electric highways, land biomass, farm and sewage biogas, "
             "and natural-gas supply.  Schematic locations, not a siting study.", fontsize=15, color=INK2)
    # legend (side panel, top)
    h = [Line2D([], [], marker="h", ls="", mfc=C["red"], mec="white", ms=20, label=f"HTGR heat-cascade hub site; number = four-reactor hubs\n({SS['hubs']:.0f} hubs, {SS['reactors']:.0f} reactors): pyrolysis H2 + carbon, fuel\nupgrading, drying, greenhouses and fish farms"),
         Line2D([], [], color=C["blue"], lw=4, label="Electric highways: 40,000 km of catenary"),
         Rectangle((0, 0), 1, 1, fc=SPECIES_COL["cold_kelp"], label="Offshore wind + seaweed (built, filled by species)"),
         Rectangle((0, 0), 1, 1, fc="none", ec=INK2, hatch="////", label="Further zones of the 515 GW large build"),
         Line2D([], [], color=INK2, lw=1.4, marker=">", label="Battery-wingsail haul route"),
         Line2D([], [], marker="s", ls="", mfc=INK, mec="white", ms=11, label="Seaweed landing port"),
         Line2D([], [], marker="o", ls="", mfc="#8c564b", mec="white", ms=15, label="Dairy digester cluster (AgSTAR leading states)"),
         Line2D([], [], marker="s", ls="", mfc="#d17b88", mec="white", ms=14, label="Swine digester cluster (AgSTAR leading states)"),
         Line2D([], [], marker="^", ls="", mfc="#2a9df4", mec="#0b3d66", ms=13, label="Major wastewater plant digesters (large metros)"),
         Line2D([], [], marker="D", ls="", mfc="#7a5c2e", mec="white", ms=11, label="Natural-gas basin"),
         Line2D([], [], marker="v", ls="", mfc=C["violet"], mec="white", ms=13, label="Canada -> U.S. gas entry point"),
         Line2D([], [], color=C["violet"], lw=2.4, ls=(0, (5, 3)), label="New Canadian pipeline corridor"),
         Line2D([], [], marker="P", ls="", mfc="#444444", mec="white", ms=13, label="LNG export terminal")]
    h += [Rectangle((0, 0), 1, 1, fc=REG_STYLE[k][0], alpha=0.7, label=REG_STYLE[k][1]) for k in ("onshore_wind", "solar", "bamboo", "hemp", "corn_ethanol", "residues")]
    h += [Rectangle((0, 0), 1, 1, fc=v, label=SPECIES_LAB[k]) for k, v in SPECIES_COL.items()]
    side.legend(handles=h, loc="upper left", fontsize=11.5, frameon=False, labelspacing=0.85, handlelength=2.6, borderaxespad=0)
    # key numbers
    r = GX["cases"]["design_sweet_spot"]; e = SS["enduse"]
    lines = [("Key numbers, 2050 (220 GW diversification case)", True),
             (f"Annual cost ${SS['transport_cost_bn']:.0f} bn (least-cost system with no offshore wind: ${F.LC['transport_cost_bn']:.0f} bn)", False),
             ("Petroleum for the same service: $593 bn (late-2025) / $881 bn (Nov-2026)", False),
             (f"Emissions {SS['emissions']['total_mt']:.0f} Mt CO2e/yr (-{SS['emissions']['reduction_pct']:.1f}% vs 2,873)", False),
             (f"Electricity {e['el_total']:,.0f} TWh, hydrogen {SS['h2_mt']['pyrolysis']:.1f} Mt, liquid fuel {e['liq_total']:,.0f} TWh", False),
             (f"Seaweed {sum(z['dry_mt'] for z in SS['seaweed']):.1f} Mt dry/yr; solar {SS['gw']['solar']:.0f} GW", False),
             (f"Pyrolysis gas {SS['gas_for_pyrolysis_tcf']:.1f} Tcf/yr; carbon {SS['carbon_mt']:.0f} Mt/yr", False),
             ("", False), ("Natural gas: first shortfall year", True),
             (f"Programme alone {r['programme']}  (no programme {r['no_programme']})", False),
             (f"+ heat pumps on clean power {r['heatpumps_central_clean']}", False),
             (f"+ farm and sewage biogas {r['both_central_clean']}  ({100 * r['share_of_pyrolysis_gas_from_biogas']['central']:.0f}% of pyrolysis gas)", False),
             (f"+ decarbonised Canada sends all its gas to the U.S. {r['canada_all_current_production_both_clean']}", False),
             (f"+ Canadian output raised to 25 Bcf/d {r['canada_all_expanded_both_clean']}", False)]
    y = 0.36
    for t, bold in lines:
        side.text(0.0, y, t, fontsize=12.5 if bold else 11.5, weight="bold" if bold else "normal", color=INK, transform=side.transAxes, va="top"); y -= 0.021
    fig.savefig(F.HERE / "Poster_US_system_map.pdf", bbox_inches="tight")
    fig.savefig(F.HERE / "Poster_US_system_map.png", dpi=200, bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__":
    main(); print("ok Poster_US_system_map")
