"""Verify immutable inputs and reproducible numerical constraints (no network)."""
from pathlib import Path
import csv,json,hashlib,sys,math,zipfile
P=Path(__file__).resolve().parent

def checksums():
 for name in ('V917_INPUT_SHA256.csv','V915_PRESERVED_ARTWORK_SHA256.csv'):
  rows=list(csv.DictReader((P/name).open(encoding='utf-8-sig')))
  for r in rows:
   assert hashlib.sha256((P/r['filename']).read_bytes()).hexdigest()==r['sha256'],r['filename']
 print('PASS: immutable source data and 72 original artwork hashes')

def close(a,b,tol=1e-6):assert abs(a-b)<=tol,(a,b)

def validate():
 checksums();d=json.loads((P/'US917_Evidence_Results.json').read_text());rr=d['results'];assert len(rr)==15 and len(d['details'])==3
 v=json.loads((P/'US916_Coupled_Results.json').read_text());close(v['baseline_rerun_cost_bn'],654.7633815744267);close(v['baseline_rerun_lca_mt'],229.38444669755273);assert len(v['rows'])==45
 for r in rr:
  close(r['internal_twh']+r['external_twh'],r['biomethane_twh']);assert r['internal_twh']<=v['gas_pipeline_lhv_twh']+1e-8
  close(r['gas_credit_mt'],r['internal_twh']*.202);close(r['combined_avoided_mt'],r['ref_emissions_mt']-r['transport_emissions_mt']+r['agri_net_mt']+r['gas_credit_mt']);close(r['combined_savings_bn'],r['ref_cost_bn']-r['combined_cost_bn']);close(r['combined_cost_bn'],r['transport_cost_bn']+r['agri_net_cost_bn']);assert r['crop_selected_mt']<=r['crop_cap_mt']+1e-8
 for r in d['details']:
  q=r['transport'];no=r['matched_no_crop'];assert no['crop_htl_mt']<1e-7
  for e in 'npk':close(q[e+'_removed_kt'],q[e+'_water_kt']+q[e+'_char_kt']+q[e+'_imports_kt'])
  for k,cap in r['group_caps_mt'].items():assert sum(x['selected_mt'] for x in q['selected'] if x['group']==k)<=cap+1e-6
  for s in r['agricultural']['streams']:
   close(s['gross_ch4_mt'],sum(s[k] for k in ['leaked_ch4_mt','flared_ch4_mt','parasitic_ch4_mt','delivered_ch4_mt']));assert s['gross_ch4_mt']<=s['potential_ch4_mt']+1e-8
  assert sum(s['baseline_avoided_mt'] for s in r['agricultural']['streams'])<=d['evidence']['historical_mt']['manure']*28+1e-8
 x=next(r for r in rr if r['scenario']=='central' and 'late_2025' in r['reference']);close(x['combined_cost_bn'],667.1194115953747);close(x['combined_avoided_mt'],3063.772088977009);close(x['crop_selected_mt'],102.64425895935472)
 assert d['evidence']['county_numeric']==3137;assert sum(d['evidence']['nwwi_counts'].values())==56111
 print('PASS: 15 evidence comparisons, matched crop/NPK/CH4 constraints, legacy central result, 45 legacy cases and central regression')
if __name__=='__main__':checksums() if '--inputs-only' in sys.argv else validate()
