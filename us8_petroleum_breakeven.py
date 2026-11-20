"""v8.3 petroleum-price break-even analysis.

The Monte Carlo compares each draw with one fixed petroleum price snapshot (late-2025 pre-tax prices).
This script asks the inverse question: at what uniform multiple of late-2025 pre-tax petroleum fuel
prices would petroleum cost the same as the modelled system?  It reads the archived scenario and
Monte Carlo outputs only; it does not rerun the transport model.

For a system cost C and the draw's own petroleum comparator R (late-2025 pre-tax fuel plus pipeline gas,
as stored in the Monte Carlo files), the break-even multiple is m* = C / R; for the deterministic cases,
m* = C / (P + G).  The multiple applies uniformly to all petroleum fuels and pipeline gas.
Petroleum is cheaper than the system when its price multiple is below m*.

Outputs: petroleum_breakeven_v8.json, petroleum_breakeven_v8.csv (share of draws cheaper than petroleum
at each price multiple).  Usage: python3 us8_petroleum_breakeven.py
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from us2_inputs import PRICES, TAX

MC_FILES = {"least_cost": "monte_carlo_least_cost.csv",
            "sweet_spot_220gw": "monte_carlo_sweet_spot.csv",
            "design_515gw": "monte_carlo_design.csv"}
DET_CASES = ["least_cost", "design_sweet_spot", "design", "least_cost_vhtr", "post_gas_least_cost", "post_gas_sweet_spot",
             "post_gas_reactor_high",
             "post_gas_design", "sustainable_fission", "sustainable_fission_nuclear_only",
             "sustainable_fission_nuclear_only_premium"]
GRID = [round(0.50 + 0.05 * i, 2) for i in range(31)]          # 0.50 ... 2.00 x late-2025 pre-tax prices
PRICE_SCENARIOS = {"low_0.7x": 0.70, "late_2025_1.0x": 1.00, "high_1.5x": 1.50}


def pct(xs, q):
    s = sorted(xs); k = (len(s) - 1) * q; f = int(k); c = min(f + 1, len(s) - 1)
    return s[f] + (s[c] - s[f]) * (k - f)


def main():
    sc = json.loads((ROOT / "scenarios.json").read_text())
    pet = sc["least_cost"]["petroleum"]
    P = pet["prices"]["late_2025"]["pretax_bn"]; G = pet["pipeline_gas_bn"]
    nov_mult = (pet["prices"]["nov_2026"]["pretax_bn"] + G) / (P + G)
    pretax_late = {k: PRICES["late_2025"][k] - TAX[k] for k in PRICES["late_2025"]}

    out = dict(basis=dict(petroleum_pretax_late_2025_bn=P, pipeline_gas_bn=G,
                          nov_2026_multiple_of_late_2025=nov_mult,
                          late_2025_pretax_usd_per_gal=pretax_late,
                          note="uniform multiple of late-2025 pre-tax petroleum fuel and pipeline-gas prices"),
               deterministic={}, monte_carlo={})
    for k in DET_CASES:
        c = sc[k]["transport_cost_bn"]; m = c / (P + G)
        out["deterministic"][k] = dict(cost_bn=c, breakeven_multiple=m,
                                       breakeven_gasoline_pretax_usd_gal=m * pretax_late["gasoline"],
                                       breakeven_diesel_pretax_usd_gal=m * pretax_late["diesel"],
                                       breakeven_jet_pretax_usd_gal=m * pretax_late["jet"])
    rows = []
    for name, fn in MC_FILES.items():
        with open(ROOT / fn) as f:
            draws = list(csv.DictReader(f))
        ms = []
        for d in draws:
            ms.append(float(d["transport_cost_bn"]) / float(d["petro_2025"]))
        n = len(ms)
        share = {m: sum(1 for x in ms if x < m) / n for m in GRID}
        out["monte_carlo"][name] = dict(n=n, breakeven_multiple_p5=pct(ms, 0.05), breakeven_multiple_p50=pct(ms, 0.5),
                                        breakeven_multiple_p95=pct(ms, 0.95),
                                        share_cheaper_than_petroleum={s: sum(1 for x in ms if x < v) / n for s, v in PRICE_SCENARIOS.items()},
                                        share_cheaper_nov_2026_prices=sum(1 for x in ms if x < nov_mult) / n)
        for m in GRID:
            rows.append(dict(case=name, petroleum_price_multiple=m, share_of_draws_cheaper_than_petroleum=round(share[m], 4)))
    (ROOT / "petroleum_breakeven_v8.json").write_text(json.dumps(out, indent=1))
    with open(ROOT / "petroleum_breakeven_v8.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

    # checks
    mcs = json.loads((ROOT / "monte_carlo_summary.json").read_text())
    for name, key in (("least_cost", "least_cost"), ("sweet_spot_220gw", "sweet_spot"), ("design_515gw", "design")):
        a = out["monte_carlo"][name]["share_cheaper_than_petroleum"]["late_2025_1.0x"]
        assert abs(a - mcs[key]["p_cheaper_2025"]) < 1e-9, (name, a, mcs[key]["p_cheaper_2025"])
    for name in MC_FILES:
        s = out["monte_carlo"][name]["share_cheaper_than_petroleum"]
        assert s["low_0.7x"] <= s["late_2025_1.0x"] <= s["high_1.5x"], name
    print("PASS: v8.3 petroleum break-even;",
          ", ".join(f"{k}: median break-even {v['breakeven_multiple_p50']:.2f}x" for k, v in out["monte_carlo"].items()))


if __name__ == "__main__":
    main()
