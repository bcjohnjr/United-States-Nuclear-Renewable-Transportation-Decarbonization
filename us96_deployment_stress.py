#!/usr/bin/env python3
"""Reactor build-out constraint sensitivity. Values are mathematical costs, not executable deployment plans."""
import csv, json
import us2_model as M
import us95_aeo_reference_bridge as B
from us96_aeo_shared_assumptions import run, vehicle_prices
r=json.load(open('US96_Shared_2050_Screen.json'))
central=r['results'][1]
_,a=B.read_source()
p,_=B.config(a)
p['VEH']['ldv_bev_net_usd_yr']=central['bev_cost_net_usd_yr_2026usd']
rows=[]
for n in [0,30,60,100,150,184,200,250,300,500,800,945]:
 cap=M.reactor_cost(p['reactor_case'],max(4*n,1))['fleet_avg_kwt_with_idc']*p.get('capex_mult',1)
 x=M.solve(p,scenario='least_cost',blend_vol=0.0,capex_kwt=cap,fixed_hubs=n)
 rows.append(dict(hubs=n,modules=4*n,annual_cost_bn=x['transport_cost_bn'],alternative_emissions_mt=x['emissions']['total_mt'],onshore_gw=x['gw']['onshore_wind'],solar_gw=x['gw']['solar'],capex_kwt=cap))
 print(n,round(x['transport_cost_bn'],3),round(x['emissions']['total_mt'],3),flush=True)
with open('us96_deployment_stress.csv','w',newline='') as f:
 w=csv.DictWriter(f,rows[0].keys());w.writeheader();w.writerows(rows)
