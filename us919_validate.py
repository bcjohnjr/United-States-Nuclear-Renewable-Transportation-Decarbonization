"""V9.19 release and numerical regression checks (flat repository)."""
from pathlib import Path
import csv,hashlib,json,math
P=Path(__file__).resolve().parent
read=lambda n:list(csv.DictReader((P/n).open(encoding='utf-8',newline='')))
sha=lambda n:hashlib.sha256((P/n).read_bytes()).hexdigest()
d=json.loads((P/'US919_Results.json').read_text()); t=d['target']; b=d['baseline']; near=lambda a,b:math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-7)
assert near(b['combined_cost_bn'],667.1194115953747) and near(t['combined_cost_bn'],445.4477251781116)
assert near(t['crop_mt'],102.64425895935472) and near(t['biomethane_twh'],24.657252936357064)
assert near(t['combined_cost_bn'],t['transport_cost_bn']+t['agri_net_cost_bn'])
assert near(t['biomethane_twh'],t['internal_twh']+t['external_twh'])
refs=d['references']; pet=[r for r in refs if 'petroleum' in r['reference'].lower()]; assert len(pet)==4 and all(t['combined_cost_bn']<r['ref_cost_bn'] for r in pet)
assert near(t['combined_avoided_mt'],pet[0]['ref_emissions_mt']-t['transport_emissions_mt']+t['agri_avoided_mt']+t['gas_credit_mt'])
assert t['aeo_bev_matched_saving_bn']<0
assert len(read('us919_cases.csv'))==12 and len(read('us919_frontier.csv'))==21 and len(read('us919_joint_draws.csv'))==512
assert len(read('us919_transition.csv'))==300 and len(read('us919_gated_transition.csv'))==600
rows=[r for r in read('us919_gated_transition.csv') if r['profile']=='strong' and r['readiness_year']=='2040' and r['reserve_peak_bn']=='25']; assert len(rows)==25
prev=0
for r in rows:
 a=float(r['adoption_fraction']); assert -1e-8<=a-prev<=.10000001 and float(r['lowest_petroleum_saving_bn'])>=-1e-8;prev=a
assert near(prev,1)
for r in read('V919_OUTPUT_SHA256.csv'):assert sha(r['file'])==r['sha256'],r['file']
for r in read('V919_FIGURE_CROSSWALK.csv'):assert sha(r['repository_source_file'])==r['sha256'],r['file']
assert len(read('V919_FIGURE_CROSSWALK.csv'))==26
print('PASS: 12 cases, 21 frontier points, 512 draws, 900 transition rows, 26 visuals; exact output checksums.')
