"""Invariant tests for V9.1 no-blend transport boundary and crop NPK / soil carbon integration."""
import copy,math
import us2_inputs as I
import us2_model as M
import us9_crop_residue as C

def close(x,y,tol=1e-8):
    assert math.isclose(x,y,rel_tol=tol,abs_tol=tol),(x,y)

close(I.ENDUSE['r_hdv_elec'],2.4*3.6/21.1)
close(I.ENDUSE['r_hdv_fcev'],4.44*3.6/21.1)
base=M.solve_learning(M.default_params(),scenario='least_cost',blend_vol=0.0)
close(base['enduse']['el_total'],1836.7235486634781)
close(base['transport_cost_bn'],526.865733103)
assert base['objective_reconciliation']['residual_bn']<1e-7
cases=C.run(write=False)
result={x['scenario']:x for x in cases}
for name in result:
    r=result[name]
    assert abs(r['model_reconciliation_residual_bn'])<1e-7,name
    assert r['soil_c_gap_mt']<1e-7,name
    if name.startswith('paired_crop'):
        for k in ('n','p','k'):
            D=C.with_crop(supply_mt=166)['CROP_RESIDUE']
            if r['crop_htl_mt']:
                close(r[k+'_returned_kt'],r['crop_htl_mt']*D['elemental_kg_t'][k])
    if 'full' in name:close(r['crop_htl_mt'],166.0)
close(result['paired_without_crop']['crop_htl_mt'],0)
assert result['paired_crop_economic_optimum']['crop_htl_mt'] <= 166.0+1e-8
assert result['paired_crop_full_zero_nutrient_recovery']['fertilizer_replacement_bn']>result['paired_crop_full_sustainable_cap_forced']['fertilizer_replacement_bn']
assert result['paired_crop_full_cover_crops_only']['methane_carbon_to_soil_mt']<1e-7
assert result['paired_crop_full_cover_crops_only']['cover_crop_stable_carbon_mt']>0
assert result['paired_crop_full_sustainable_cap_forced']['k_import_kt']>0
print('PASS V9.1: truck conversion, objective reconciliation, field N/P/K closure, carbon alternatives, crop caps, no double counting')
