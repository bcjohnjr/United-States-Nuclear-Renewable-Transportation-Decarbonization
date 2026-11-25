"""V5: transparent *civilian capacity* deployment sensitivity, not a fuel-fabrication model.

Each input is an assumed, regulator-authorised stream of civilian startup-fuel
service (GWe-equivalent), NOT an instruction or prediction for producing,
separating or converting fissile materials. Existing light-water reactors are
NOT credited as net breeders. Earlier commercial spent fuel and separately
released government surplus are disjoint public planning pools. Hypothetical
future closed-cycle fuel-service capacity is an EXOGENOUS scenario; this script
contains no reactor physics, material production calculation, or reprocessing
parameters. All approvals, licensing, construction and fuel qualification must
be satisfied independently.
"""
from __future__ import annotations
import json, csv, math
from pathlib import Path
from dataclasses import dataclass, asdict

OUT=Path(__file__).resolve().parent
START_YEAR=2026
END_YEAR=2100
PUBLIC_SURPLUS_T=19.7              # DOE, FY2027 budget / June 2026 request; NOT approved release
BASELINE_US_SPENT_FUEL_PU_T=950.0  # V4.1 hypothetical SNF gross inventory, NOT separated / recoverable
STARTUP_T_PER_GWE=10.0             # V4.1 screening assumption; NOT a reactor-design value
YEARLY_CONSTRUCTION_LIMIT_IS_ASSUMED=True
SOURCE_LINKS={
 "public_surplus":"https://www.energy.gov/ne/articles/department-energy-seeks-transform-surplus-plutonium-nuclear-fuel",
 "civilian_inventory":"https://www.everycrsreport.com/files/2026-08-05_R42853_0cf1e5fdf24a10a808dbb585722c55b877a988ba.html",
 "fuel_cycle_overview":"https://infcis.iaea.org/nfcss/modeling",
 "safeguards":"https://www.iaea.org/topics/safeguards"
}

@dataclass(frozen=True)
class Assumptions:
    name:str
    description:str
    government_release_fraction:float
    government_ready_year:int
    government_certified_gwe_per_year:float
    civilian_spentfuel_access_fraction:float
    civilian_ready_year:int
    civilian_certified_gwe_per_year:float
    future_closed_cycle_ready_year:int
    hypothetical_future_certified_gwe_per_year:float
    reactor_commissioning_start_year:int
    maximum_hubs_commissioned_per_year:int

CASES=(
 Assumptions("not_authorized", "No government material released; no recycling or advanced-cycle service commissioned",0,2060,0,0,2070,0,2070,0,2050,20),
 Assumptions("surplus_only_upper", "All currently discussed public surplus exceptionally authorized; no spent-fuel recovery",1,2045,0.50,0,2060,0,2070,0,2045,15),
 Assumptions("regulated_civilian_limited", "Half of discussed surplus and 20% of gross spent-fuel inventory eligible",0.50,2050,0.25,0.20,2060,2,2070,0,2050,15),
 Assumptions("conditional_closed_cycle", "Scenario: government release, licensed civilian recovery and external future fuel services",1,2050,0.80,0.50,2060,5,2075,3,2050,25),
 Assumptions("illustrative_technology_upper", "Stress test only: entire stocks eligible, high authorization and construction throughput",1,2045,2,1,2050,12,2065,7,2045,40),
)


def simulate(case:Assumptions, fleet_target_hubs:int, startup_gwe_per_hub:float):
    assert fleet_target_hubs>0 and startup_gwe_per_hub>0
    assert 0 <= case.government_release_fraction<=1
    assert 0 <= case.civilian_spentfuel_access_fraction<=1
    government_remaining=PUBLIC_SURPLUS_T*case.government_release_fraction/STARTUP_T_PER_GWE
    civilian_remaining=BASELINE_US_SPENT_FUEL_PU_T*case.civilian_spentfuel_access_fraction/STARTUP_T_PER_GWE
    accumulated_uncommitted_gwe=0.0
    hubs=0
    rows=[]
    source_total={"government_public_surplus":0.,"licensed_civilian_spent_fuel":0.,"hypothetical_future_fuel_services":0.}
    for year in range(START_YEAR,END_YEAR+1):
        gov = min(government_remaining, case.government_certified_gwe_per_year) if year>=case.government_ready_year else 0.
        civil = min(civilian_remaining,case.civilian_certified_gwe_per_year) if year>=case.civilian_ready_year else 0.
        # EXOGENOUS: civilian-certified capacity added by a future approved
        # closed-fuel-cycle industry. Does not simulate breeding, separation,
        # irradiation, isotopes, or fabrication, and confers no availability claim.
        future = case.hypothetical_future_certified_gwe_per_year if year>=case.future_closed_cycle_ready_year else 0.
        government_remaining-=gov
        civilian_remaining-=civil
        source_total["government_public_surplus"]+=gov
        source_total["licensed_civilian_spent_fuel"]+=civil
        source_total["hypothetical_future_fuel_services"]+=future
        accumulated_uncommitted_gwe += gov+civil+future
        if year >= case.reactor_commissioning_start_year:
            possible = int(math.floor((accumulated_uncommitted_gwe+1e-10)/startup_gwe_per_hub))
            add = min(possible, case.maximum_hubs_commissioned_per_year, fleet_target_hubs-hubs)
            hubs += add
            accumulated_uncommitted_gwe -= add*startup_gwe_per_hub
        else:
            add = 0
        rows.append(dict(year=year, scenario=case.name, commissioned_hubs=hubs,
          fraction_of_static_target=hubs/fleet_target_hubs,
          fleet_capacity_gwe_equivalent=hubs*startup_gwe_per_hub,
          gov_certified_addition_gwe=gov, civilian_certified_addition_gwe=civil,
          hypothetical_future_certified_addition_gwe=future,
          uncommitted_authorized_capacity_gwe=max(accumulated_uncommitted_gwe,0.),
          newly_commissioned_hubs=add))
    first = next((r["year"] for r in rows if r["commissioned_hubs"]>=fleet_target_hubs),None)
    check_year = lambda yr: next((r for r in rows if r["year"]==yr),None)
    summ=dict(name=case.name,description=case.description,first_year_reaching_full_static_target=first,
       target_hubs=fleet_target_hubs,target_gwe_equivalent=fleet_target_hubs*startup_gwe_per_hub,
       year2050=check_year(2050),year2075=check_year(2075),year2100=check_year(2100),
       end_year=check_year(END_YEAR),cumulative_certified_capacity_gwe_by_source=source_total,
       public_surplus_fraction_of_target_if_all_approved=(PUBLIC_SURPLUS_T/STARTUP_T_PER_GWE)/(fleet_target_hubs*startup_gwe_per_hub),
       baseline_spent_fuel_fraction_of_target_if_all_approved=(BASELINE_US_SPENT_FUEL_PU_T/STARTUP_T_PER_GWE)/(fleet_target_hubs*startup_gwe_per_hub))
    return summ,rows


def run(render_figure=True):
    scenarios=json.loads((OUT/"scenarios.json").read_text())
    baseline=scenarios["sustainable_fission_nuclear_only"]
    # Preserve fuel-accounting methodology in original model; use reference
    # inventory as a capacity-scale screen, not as an actual reactor fuel loading.
    target_hubs=int(round(baseline["hubs"]))
    target_gwe=baseline["fuel_supply"]["fleet_gwe_equivalent"]
    per_hub=target_gwe/target_hubs
    all_summ, all_rows={},[]
    for c in CASES:
        result,rows=simulate(c,target_hubs,per_hub)
        all_summ[c.name]=result
        all_rows.extend(rows)
    metadata=dict(version="5.0",source_scenario="sustainable_fission_nuclear_only",time_resolution="annual",
       years=[START_YEAR,END_YEAR],target_hubs=target_hubs,target_fleet_gwe_equivalent=target_gwe,
       target_gwe_per_hub=per_hub,public_surplus_t=PUBLIC_SURPLUS_T,
       baseline_us_spent_fuel_pu_t=BASELINE_US_SPENT_FUEL_PU_T,
       assumed_startup_t_per_gwe=STARTUP_T_PER_GWE,source_links=SOURCE_LINKS,
       physical_status="scenario-screening only: hypothetical future plant is not a licensed design",
       disclaimer="Material stock != separated, approved or qualified fuel. Proposed U.S. surplus is not automatically released. Fuel-service flows and licensing dates are illustrative exogenous inputs, not validated capacity forecasts. Normal LWRs are not credited with net breeding. Does not calculate isotope production or material processing. No hour-by-hour electricity dispatch, financing, fuel fabrication or regulatory review is modelled. Horizon ends by 2100, before 60-year retirement of units commissioned from 2045 onward; later operation requires a replacement-fleet model.",
       comparison="Source envelopes are disjoint; neither the 19.7-t public surplus nor the 950-t gross spent-fuel estimate is double-counted.")
    (OUT/"fuel_transition_v5.json").write_text(json.dumps(dict(metadata=metadata,assumptions=[asdict(c) for c in CASES],scenarios=all_summ),indent=2))
    with (OUT/"fuel_transition_v5.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(all_rows[0]));w.writeheader();w.writerows(all_rows)
    if render_figure:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        f,ax=plt.subplots(figsize=(10.2,5.8))
        for c in CASES:
            rr=[r for r in all_rows if r["scenario"]==c.name]
            ax.plot([r["year"] for r in rr],[r["fraction_of_static_target"]*100 for r in rr],lw=2.1,label=c.name.replace("_"," "))
        ax.axhline(100,ls="--",lw=1,label="Corrected V8.5 theoretical steady-state target (100%)")
        ax.axvline(2050,ls=":",lw=1)
        ax.text(2051,4,"2050 steady-state comparison",fontsize=9)
        ax.set(xlim=(2035,2100),ylim=(0,105),xlabel="Calendar year",ylabel="Illustrative fraction of static reactor fleet commissioned (%)",
               title="V8.5: conditional authorised civilian fuel-service and deployment scenarios")
        ax.grid(alpha=.20)
        ax.legend(loc="upper left",fontsize=8,ncol=2)
        f.text(0.1,.02,"Not a forecast: inputs are assumed approval/qualification rates; no plutonium production or fuel-processing model.",fontsize=8)
        f.tight_layout(rect=[0,.045,1,1])
        for ext in ("png","pdf"):
            f.savefig(OUT/f"ScienceFigS13_fuel_transition.{ext}",dpi=250,bbox_inches="tight")
        plt.close(f)
    return metadata, all_summ

if __name__=="__main__":
    import sys
    meta,summary=run(render_figure=(len(sys.argv)<2 or sys.argv[1]!="0"))
    print("V5 civilian-fuel sensitivity: target hubs",meta["target_hubs"])
    for name,row in summary.items():
        print(name, "2050",row["year2050"]["commissioned_hubs"], "2100",row["year2100"]["commissioned_hubs"],"full year",row["first_year_reaching_full_static_target"])
