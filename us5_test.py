"""Regression and conservation tests for high-level V5 capacity screen."""
from dataclasses import replace
from math import isclose
import json
from pathlib import Path
from us5_fuel_transition import CASES,simulate,PUBLIC_SURPLUS_T,BASELINE_US_SPENT_FUEL_PU_T,STARTUP_T_PER_GWE


def run_tests():
    sample_hubs=728
    gwe_per_hub=.32
    assert len({c.name for c in CASES}) == len(CASES)
    for c in CASES:
        summary,rows=simulate(c,sample_hubs,gwe_per_hub)
        assert len(rows) == 75
        assert all(r['commissioned_hubs']<=sample_hubs for r in rows)
        assert all(r['commissioned_hubs']>=0 for r in rows)
        assert all(r['newly_commissioned_hubs']<=c.maximum_hubs_commissioned_per_year for r in rows)
        assert all(a['commissioned_hubs']<=b['commissioned_hubs'] for a,b in zip(rows[:-1],rows[1:]))
        assert all(r['uncommitted_authorized_capacity_gwe']>=-1e-8 for r in rows)
        assert summary['cumulative_certified_capacity_gwe_by_source']['government_public_surplus'] <= PUBLIC_SURPLUS_T*c.government_release_fraction/STARTUP_T_PER_GWE + 1e-6
        assert summary['cumulative_certified_capacity_gwe_by_source']['licensed_civilian_spent_fuel']<=BASELINE_US_SPENT_FUEL_PU_T*c.civilian_spentfuel_access_fraction/STARTUP_T_PER_GWE + 1e-6
        assert rows[-1]['fleet_capacity_gwe_equivalent'] <= sum(summary['cumulative_certified_capacity_gwe_by_source'].values()) + 1e-6
    no,rows=simulate(CASES[0],sample_hubs,gwe_per_hub)
    assert all(r['commissioned_hubs']==0 for r in rows)
    # Surplus-only cannot create more eligible capacity than its finite public source.
    only,rows=simulate(CASES[1],sample_hubs,gwe_per_hub)
    assert rows[-1]['fleet_capacity_gwe_equivalent'] <= PUBLIC_SURPLUS_T/STARTUP_T_PER_GWE+1e-8
    # Hypothetical external future fuel services are never implicitly generated in a scenario with zero such flow.
    for c in CASES[:3]:
        assert c.hypothetical_future_certified_gwe_per_year==0
    # Strictly test that later authorisation cannot produce earlier licensed capacity.
    delayed=replace(CASES[1],government_ready_year=2080)
    _, delayed_rows=simulate(delayed,sample_hubs,gwe_per_hub)
    assert all(r['commissioned_hubs']==0 for r in delayed_rows if r['year']<2080)
    fp=Path(__file__).with_name('scenarios.json')
    if fp.exists():
        data=json.loads(fp.read_text())
        u=data['sustainable_fission']
        n=data['sustainable_fission_nuclear_only']
        assert u['total_cost_bn'] <= n['total_cost_bn'] + 1e-5
        for key in ('sustainable_fission','sustainable_fission_nuclear_only','sustainable_fission_nuclear_only_premium','sustainable_fission_nuclear_only_si_cheap'):
            z=data[key]; meta=z['learning_search']
            assert meta['max_hubs']==2000
            assert abs(z['hubs']-round(z['hubs'])) < 1e-8
            assert meta['feasible_count']>0
            assert abs(z['objective_reconciliation']['residual_bn']) < 1e-5
    print('PASS: V5 source/stock/deployment and bounded optimisation consistency checks')

if __name__=='__main__':run_tests()
