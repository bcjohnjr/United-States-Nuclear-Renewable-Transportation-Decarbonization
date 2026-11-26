"""Reproduce and validate V9.18; historical V9.17 remains independently reproducible."""
import csv,json,hashlib,sys
from pathlib import Path
import us917_validate as legacy
P=Path(__file__).resolve().parent

def close(a,b,tol=1e-6): assert abs(a-b)<=tol,(a,b)
def validate():
 legacy.validate(); d=json.loads((P/'US918_Evidence_Results.json').read_text()); b=json.loads((P/'US97_AEO_Boundary.json').read_text())['results'][1]; rows=d['results']; assert len(rows)==30 and len(d['details'])==6
 for r in rows:
  if r['reference'].startswith('AEO'):
   close(r['ref_emissions_mt'],b['reference_partial_wtw_mt']);close(r['ref_cost_bn'],b['reference_screen_bn'])
  close(r['internal_twh']+r['external_twh'],r['biomethane_twh']);close(r['gas_credit_mt'],r['internal_twh']*.202);close(r['combined_avoided_mt'],r['ref_emissions_mt']-r['transport_emissions_mt']+r['agri_net_mt']+r['gas_credit_mt']);close(r['combined_savings_bn'],r['ref_cost_bn']-r['combined_cost_bn']);close(r['combined_cost_bn'],r['transport_cost_bn']+r['agri_net_cost_bn'])
  assert r['crop_selected_mt']<=r['crop_cap_mt']+1e-8
 for x in d['details']:
  q=x['transport'];close(x['matched_no_crop']['crop_htl_mt'],0)
  for e in 'npk':close(q[e+'_removed_kt'],q[e+'_water_kt']+q[e+'_char_kt']+q[e+'_imports_kt'])
  for k,cap in x['group_caps_mt'].items(): assert sum(i['selected_mt'] for i in q['selected'] if i['group']==k)<=cap+1e-6
  if x['scenario'].startswith('mapped_'):
   allowed={'corn','wheat','small_grain','sorghum'}|({'processing','other'} if x['scenario']=='mapped_plus_wet' else set())
   for i in q['selected']:
    if i['group'] not in allowed or (x['scenario']=='mapped_exact' and (i['name'].startswith('Corn cobs') or i['group']=='small_grain')):close(i['selected_mt'],0)
  for s in x['agricultural']['streams']:
   close(s['gross_ch4_mt'],sum(s[k] for k in ['leaked_ch4_mt','flared_ch4_mt','parasitic_ch4_mt','delivered_ch4_mt']))
   assert s['gross_ch4_mt']<=s['potential_ch4_mt']+1e-8
 c=next(r for r in rows if r['scenario']=='central' and 'late_2025' in r['reference']);close(c['combined_cost_bn'],667.1194115953747);close(c['combined_avoided_mt'],3063.772088977009)
 print('PASS V9.18: unrounded HHV reference, 30 comparisons, 3 crop exclusions, matched no-crop, NPK, methane and cost balances')
if __name__=='__main__':validate()
