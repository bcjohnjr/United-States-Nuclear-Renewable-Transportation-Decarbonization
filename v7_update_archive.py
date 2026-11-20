"""One-time state migration: annotate preserved V6 transport scenario food fields without changing LP outputs."""
import json
from pathlib import Path
from us2_inputs import FOOD
ROOT=Path(__file__).resolve().parent
path=ROOT/'scenarios.json';s=json.loads(path.read_text())
den=FOOD['kcal_per_person_day']*365*1e6
for k,v in s.items():
    if not isinstance(v,dict) or 'food' not in v:continue
    f=v['food']
    veg_kcal=f['vegetables_mt']*1e9*FOOD['kcal_per_kg_veg']
    fish_kcal=f['fish_shrimp_mt']*1e9*FOOD['kcal_per_kg_fish']
    gross=(veg_kcal+fish_kcal)/den
    adjusted=(veg_kcal*FOOD['vegetable_edible_fraction']+fish_kcal*FOOD['fish_shrimp_edible_fraction'])/den
    hemp=f['hemp_meal_mt']*1e9*3500/den
    assert abs((gross+hemp)-f['people_fed_calorie_equiv_m'])<1e-10, k
    f.update(greenhouse_seafood_gross_calorie_equiv_m=gross,
             greenhouse_seafood_edible_calorie_equiv_m=adjusted,
             edible_fraction_scenarios={'vegetables':FOOD['vegetable_edible_fraction'],'fish_shrimp':FOOD['fish_shrimp_edible_fraction']},
             hemp_meal_potential_calorie_equiv_m=hemp,
             people_fed_calorie_equiv_deprecated=True)
path.write_text(json.dumps(s,indent=2)+'\n')
print('V7 migrated',sum(isinstance(v,dict) and 'food' in v for v in s.values()),'transport food records; no costs or optimised decisions changed')
