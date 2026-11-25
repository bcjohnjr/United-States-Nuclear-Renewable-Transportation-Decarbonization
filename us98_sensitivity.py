#!/usr/bin/env python3
"""V9.8 reproducible *conservative screening* cases, not source-calibrated county model."""
from pathlib import Path
import json,csv,copy
import us97_circular_feedstocks as C
import us97_integrated as J
import us97_aeo_boundary as B
import us95_aeo_reference_bridge as A
import us2_model as M
R=Path(__file__).resolve().parent
PRIMARY={'Corn stalks and leaves (excluding cobs/husks)','Wheat straw and chaff','Rice straw','Barley, oat and rye straw','Grain sorghum stalks and leaves','Cotton stalks'}
def params(central,**kwargs):
 _,a=A.read_source();p=C.build_params(a,bevpremium=central,**kwargs)
 return p
def region_proxy(p,share=.5):
 # Exclude all independent processing/bagasse/cob/other tiers until a BT23
 # county resource table establishes disjoint supplies. The remaining crop
 # caps are also analyst screens reduced by share, NOT a regionally verified cap.
 for i,f in enumerate(p['CROP_RESIDUE']['feedstocks']):
  name,cap,cost=p['BIOMASS']['tiers'][i]
  cap2=cap*share if name in PRIMARY else 0.0
  p['BIOMASS']['tiers'][i]=(name,cap2,cost)
  f['cap_mt']=cap2
 p['CROP_RESIDUE']['cap_mt']=min(p['CROP_RESIDUE']['cap_mt'],166*share)
 return p

def row(name,r):
 c=r.get('crop_residue_soil',{})
 return {'case':name,'annual_cost_bn':r['transport_cost_bn'],'emissions_legacy_mt':r['emissions']['total_mt'],
         'hubs':r['hubs'],'reactor_modules':r['hubs']*4,'crop_mt':c.get('feedstock_mt',0),
         'n_import_kt':c.get('nutrients',{}).get('n',{}).get('imported_kt',0),
         'p_import_kt':c.get('nutrients',{}).get('p',{}).get('imported_kt',0),
         'k_import_kt':c.get('nutrients',{}).get('k',{}).get('imported_kt',0),
         'cover_crop_c_mt':c.get('cover_crop_extra_stable_c_mt',0),
         'residual_bn':r['objective_reconciliation']['residual_bn']}
def main():
 source=json.loads((R/'US97_AEO_Boundary.json').read_text())
 premium=source['results'][1]['net_bev_differential_usd_yr']
 cases=[]
 opts=[('V9.7 166Mt analyst reference',lambda p:p),
       ('Joint conservative: half NPK, no char/pyro soil C',lambda p:p),
       ('Joint + primary BT23-type only, half availability',lambda p:region_proxy(p,.5)),
       ('Joint + primary BT23-type only, quarter availability',lambda p:region_proxy(p,.25))]
 for i,(name,xf) in enumerate(opts):
  kw={} if i==0 else {'release_fraction':.5,'apply_pyro_to_soil':False,'allow_stable_hydrochar':False}
  p=params(premium,**kw);p=xf(p)
  r=M.solve_learning(p,scenario='least_cost',blend_vol=0)
  item=row(name,r);cases.append(item)
  print('CASE',name,round(item['annual_cost_bn'],3),'crop',round(item['crop_mt'],3),'cover C',round(item['cover_crop_c_mt'],3),flush=True)
 # identical conservative central p for realistic fleet ceilings, *fixed hub counts*
 p=params(premium)
 hrows=[]
 for n in (0,30,60,100,150,166,250,945):
  r=M.solve_learning(p,scenario='least_cost',blend_vol=0,fixed_hubs=n)
  q=row(f'{n} hubs fixed',r);hrows.append(q)
  print('HUB',n,round(q['annual_cost_bn'],2),flush=True)
 R.joinpath('US98_Strict_Crop_and_Reactor_Sensitivity.json').write_text(json.dumps({'version':'9.8','input_status':'UNVERIFIED REGION: all field/processing stream caps remain analyst assumptions', 'cases':cases,'fixed_hub_cases':hrows,'primary_types':sorted(PRIMARY),'regional_input':'NOT DOWNLOADED / NOT COUNTRY-LEVEL VALIDATED','notes':['Model learning is non-convex: fixed-hub screens are not certified global optimum','Alternative total emissions omit explicit new crop-cycle LCA; see us98_agri_lca.py','No directly placed raw wastewater in soil']},indent=2))
 for name,arr in [('us98_conservative_crop_scenarios.csv',cases),('us98_fixed_reactor_deployment.csv',hrows)]:
  with R.joinpath(name).open('w',newline='') as f:
   w=csv.DictWriter(f,list(arr[0]));w.writeheader();w.writerows(arr)
 return cases,hrows
if __name__=='__main__':main()
