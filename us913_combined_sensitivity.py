#!/usr/bin/env python3
"""Matched two-factor terrestrial HTL yield x incremental delivery-price optimisation."""
import csv,json
from pathlib import Path
import us911_robustness as B
import us97_circular_feedstocks as C
import us95_aeo_reference_bridge as A
R=Path(__file__).resolve().parent
YIELDS=(2.0,2.3,2.6,3.0)
EXTRA=(0,20,40,80)
def run():
    _,a=A.read_source()
    bev=json.loads((R/'US97_AEO_Boundary.json').read_text())['results'][1]['net_bev_differential_usd_yr']
    rows=[]
    for h in YIELDS:
        p0=B.setup(a,bev,cap_mt=0);p0['ROUTES']['htl']['mwh_t']=h
        base=C.one('paired no-crop',p0)
        for charge in EXTRA:
            p=B.setup(a,bev,cap_mt=166,delivery_usd_t=charge);p['ROUTES']['htl']['mwh_t']=h
            crop=C.one('paired crop',p)
            rows.append(dict(htl_liquid_yield_mwh_dry_t=h,extra_crop_delivery_usd_dry_t=charge,
                crop_selected_mt=crop['crop_htl_mt'],crop_annual_bn=crop['annual_cost_bn'],
                no_crop_annual_bn=base['annual_cost_bn'],crop_saving_bn=base['annual_cost_bn']-crop['annual_cost_bn'],
                status='Assumed common HTL yield, delivery surcharge and national crop-capacity ceiling'))
            print('PAIR',h,charge,round(rows[-1]['crop_saving_bn'],4),round(rows[-1]['crop_selected_mt'],2),flush=True)
    with (R/'us913_combined_yield_delivery.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
    (R/'US913_Combined_Yield_Delivery.json').write_text(json.dumps({'version':'9.13','results':rows,
        'note':'16 reoptimised two-factor analyst screens; no county resource or feedstock-specific conversion evidence.'},indent=2)+'\n')
    return rows
if __name__=='__main__':run()
