#!/usr/bin/env python3
"""Paired terrestrial-HTL liquid-energy-yield sensitivity, V9.12.

Changes the common terrestrial HTL output assumed by the inherited LP
(MWh finished liquid per dry metric tonne) in BOTH the crop-enabled and
matched no-crop alternatives. All crop prices, NPK/soil constraints, freight
and electricity costs remain common. This does not validate feedstock-
specific yields; the underlying solver does not assign distinct HTL product
yields to all 13 crop candidates, so no claim of crop-specific validation.
"""
import csv,json,math
from pathlib import Path
import us911_robustness as B
import us97_circular_feedstocks as C
import us95_aeo_reference_bridge as A
R=Path(__file__).resolve().parent
YIELDS=[1.2,1.6,2.0,2.3,2.6,3.0]

def run():
    _,a=A.read_source()
    z=json.loads((R/'US97_AEO_Boundary.json').read_text())
    bev=float(z['results'][1]['net_bev_differential_usd_yr'])
    out=[]
    for yield_t in YIELDS:
        common={}
        for enabled,cap in ((False,0),(True,166)):
            p=B.setup(a,bev,cap_mt=cap)
            p['ROUTES']['htl']['mwh_t']=yield_t
            c=C.one('matched crop' if enabled else 'matched no crop',p)
            common['crop' if enabled else 'no_crop']=c
        crop=common['crop'];no=common['no_crop']
        out.append(dict(htl_liquid_mwh_per_dry_metric_t=yield_t,
            crop_annual_bn=crop['annual_cost_bn'],no_crop_annual_bn=no['annual_cost_bn'],
            crop_saving_bn=no['annual_cost_bn']-crop['annual_cost_bn'],
            crop_selected_mt=crop['crop_htl_mt'],crop_liquid_twh=crop['crop_htl_liquid_twh'],
            crop_n_external_kt=crop['n_imports_kt'],crop_p_external_kt=crop['p_imports_kt'],
            crop_k_external_kt=crop['k_imports_kt'],
            boundary='system-wide common terrestrial HTL yield [A]; NOT measured feedstock-specific performance'))
        print('HTL yield',yield_t,'crop',round(crop['annual_cost_bn'],3),'no crop',round(no['annual_cost_bn'],3),'crop Mt',round(crop['crop_htl_mt'],2),flush=True)
    assert len(out)==len(YIELDS)
    baseline=next(q for q in out if q['htl_liquid_mwh_per_dry_metric_t']==2.6)
    assert math.isclose(baseline['crop_annual_bn'],654.7633815744,abs_tol=1e-4)
    assert math.isclose(baseline['no_crop_annual_bn'],661.5452670834,abs_tol=1e-4)
    with (R/'us912_terrestrial_htl_yield_sensitivity.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,list(out[0]));w.writeheader();w.writerows(out)
    (R/'US912_HTL_Yield_Sensitivity.json').write_text(json.dumps(dict(version='9.12',results=out,limitations=[
        'The inherited LP assigns a single common terrestrial HTL yield; distinct corn/wheat/rice/food-waste biocrude chemistry is NOT modelled or claimed',
        'Physical conversion and hydrogen requirements are screening assumptions; energy balance reoptimised for each yield',
        'The baseline 2.6 MWh per dry metric tonne is not supported by universal crop-specific HTL trials']),indent=2)+'\n')
    return out
if __name__=='__main__':run()
