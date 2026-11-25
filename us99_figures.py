#!/usr/bin/env python3
"""V9.9 current 600-dpi publication TIFFs; preserve Grid Harvester S1 and S22 unchanged."""
import csv, json, textwrap
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
R=Path(__file__).resolve().parent
A=json.loads((R/'US99_Scenario_Analysis.json').read_text());c=A['scenarios'][0];no=A['scenarios'][-1];l=A['lca_accounting'][0]
with (R/'us99_paired_uncertainty.csv').open() as f:mc=list(csv.DictReader(f))
with (R/'us99_joint_conservative_reactors.csv').open() as f:hubs=list(csv.DictReader(f))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9.0,'axes.labelsize':9,'axes.titlesize':10,
  'xtick.labelsize':8.3,'ytick.labelsize':8.3,'savefig.pad_inches':.08})

def save(fig,stem):
 fig.savefig(R/stem,dpi=600,format='tiff',pil_kwargs={'compression':'tiff_lzw'},facecolor='white')
 plt.close(fig)
 with Image.open(R/stem) as im:
  if im.mode!='RGB':
   im.convert('RGB').save(R/stem,format='TIFF',compression='tiff_lzw',dpi=(600,600))
 with Image.open(R/stem) as im:
  assert im.mode=='RGB' and tuple(round(x) for x in im.info.get('dpi',(0,0)))==(600,600),(stem,im.mode,im.info.get('dpi'))
 print('FIG',stem,flush=True)

def main_cost():
 fig,(ax,bx)=plt.subplots(1,2,figsize=(7.10,3.5),gridspec_kw={'width_ratios':[1.05,1]},layout='constrained')
 labels=['AEO2026\npartial reference','No-crop\nalternative','Crop-enabled\nalternative']
 vals=[477.15,no['annual_cost_bn'],c['annual_cost_bn']]
 ax.bar(range(3),vals,color=['#666e77','#d49370','#236a57'],width=.66)
 ax.set_xticks(range(3),labels);ax.set_ylabel('Annual expenditure (US$ bn, conditional)')
 ax.set_ylim(0,745);ax.set_title('A  Shared-service expenditure screens',loc='left',fontweight='bold')
 for i,v in enumerate(vals):ax.text(i,v+16,f'{v:.1f}',ha='center',fontweight='bold',fontsize=9)
 bx.bar(range(3),[A['reference_partial_mt'],no['emissions_wtw_mt'],l['replaced_route_screen_mt']],color=['#666e77','#d49370','#236a57'],width=.66)
 bx.set_xticks(range(3),['Reference\npartial LCA','No-crop\nalternative','Crop-enabled\nsubstitution'])
 bx.set_ylim(0,1800);bx.set_ylabel('Screened emissions (Mt CO₂e/yr)')
 bx.set_title('B  Partial lifecycle comparison',loc='left',fontweight='bold')
 for i,v in enumerate([A['reference_partial_mt'],no['emissions_wtw_mt'],l['replaced_route_screen_mt']]):bx.text(i,v+31,f'{v:,.0f}',ha='center',fontweight='bold',fontsize=9)
 fig.text(.51,-.01,'The reference is not an official full-system cost forecast; agricultural process emissions replace a generic route coefficient.',ha='center',fontsize=7.1)
 save(fig,'ScienceFig1_V99_Conditional_Economics_and_LCA.tif')

def crop():
 rows=c['selected'];names=[textwrap.fill(t['name'].replace(' (excluding cobs/husks)',''),width=31) for t in rows]
 sel=np.array([r['selected_mt'] for r in rows]);cap=np.array([r['max_mt'] for r in rows]);y=np.arange(len(rows))
 fig,ax=plt.subplots(figsize=(7.10,6.80));fig.subplots_adjust(left=.40,right=.95,top=.94,bottom=.11)
 ax.barh(y,cap,color='#c7cdd0',height=.76,label='Analyst upper limit')
 ax.barh(y,sel,color='#2b8168',height=.49,label='Economically selected')
 ax.set_yticks(y,names);ax.invert_yaxis();ax.set_xlim(0,max(cap)*1.15);ax.set_xlabel('Dry agricultural residues (million metric tonnes per year)')
 ax.set_title('National crop categories under unverified subcategory capacities',pad=10,fontsize=10)
 ax.legend(loc='lower right',fontsize=8,frameon=False)
 for yy,v in enumerate(sel):
  if v>0.1:ax.text(v+.9,yy,f'{v:g}',va='center',fontsize=7.9)
 ax.text(0,-.105,'National total ceiling: 166 Mt/year. Source allocation not geographically validated.',transform=ax.transAxes,fontsize=7.5)
 save(fig,'ScienceFig2_V99_Crop_Economic_Selection.tif')

def npk():
 fig,(ax,bx)=plt.subplots(1,2,figsize=(7.10,3.35),layout='constrained')
 labels=['Nitrogen','Phosphorus','Potassium'];x=np.arange(3)
 ext=np.array([c[e+'_imports_kt'] for e in 'npk']);rem=np.array([c[e+'_removed_kt'] for e in 'npk']);rec=rem-ext
 ax.bar(x,ext,color='#bb7648',label='External fertilizer')
 ax.bar(x,rec,bottom=ext,color='#397f6c',label='Plant-available recovered')
 ax.set_xticks(x,labels);ax.set_ylim(0,1750);ax.set_ylabel('Elemental nutrient (kt/yr)')
 ax.set_title('A  N/P/K closure after field availability',loc='left',fontweight='bold')
 ax.legend(loc='upper left',fontsize=7,frameon=False)
 for i,(e,r) in enumerate(zip(ext,rem)):
  ax.text(i,r+30,f'{r:,.0f}',ha='center',fontsize=8)
 requirement=c['stable_soil_c_need_mt'];achieved=c['cover_crop_stable_c_mt'];capacity=A['cover_crop_land_constraint']['max_stable_c_mt']
 bx.bar([0,1,2],[requirement,achieved,capacity],color=['#777','#3a7c5b','#a3bb9b'])
 bx.set_xticks([0,1,2],['Required\nrestoration','Cover-crop\nmodelled','Assumed land\ncapacity'])
 bx.set_ylim(0,11.5);bx.set_ylabel('Stable-equivalent C (Mt/yr)')
 bx.set_title('B  Biological soil-carbon constraint',loc='left',fontweight='bold')
 for i,v in enumerate([requirement,achieved,capacity]):bx.text(i,v+.2,f'{v:.2f}',ha='center',fontsize=8)
 save(fig,'ScienceFig3_V99_Plant_Available_NPK_and_Carbon.tif')

def uncertainty():
 ab=np.array([float(z['abatement_usd_t']) for z in mc]);x=np.array([int(z['hubs']) for z in hubs]);y=np.array([float(z['annual_cost_bn']) for z in hubs])
 fig,(ax,bx)=plt.subplots(1,2,figsize=(7.10,3.35),layout='constrained')
 ax.hist(ab,bins=18,color='#287d62',edgecolor='white')
 ax.axvline(np.median(ab),ls='--',color='#9d5033',lw=1.3)
 ax.set_xlabel('Conditional abatement cost (US$/t CO₂e)');ax.set_ylabel('Simulation draws')
 ax.set_title('A  150-draw paired screening distribution',loc='left',fontweight='bold')
 ax.text(.04,.95,f'Median {np.median(ab):.1f}; 5–95% {np.percentile(ab,5):.0f}–{np.percentile(ab,95):.0f}',transform=ax.transAxes,va='top',fontsize=7.7)
 bx.plot(x,y,'o-',lw=1.5,color='#296181');bx.set_xlabel('Fixed 4-module reactor hubs')
 bx.set_ylabel('Alternative annual cost (US$ bn)')
 bx.set_title('B  Joint-conservative deployment screen',loc='left',fontweight='bold')
 bx.set_xlim(-10,265)
 save(fig,'ScienceFig5_V99_Uncertainty_and_Reactor_Limits.tif')

def supplement():
 fig,ax=plt.subplots(figsize=(7.1,3.45),layout='constrained')
 keys=['Legacy alternative','Generic crop route removed','Explicit processes','Substituted crop LCA','Gross-addition upper screen']
 vals=[l['legacy_mt'],-l['generic_crop_ci_replaced_mt'],l['process_inventory_mt'],l['replaced_route_screen_mt'],l['maximal_gross_addition_screen_mt']]
 ax.barh(np.arange(5),vals,color=['#6e7a85','#c17b59','#9b7647','#317863','#a65c51'])
 ax.set_yticks(np.arange(5),keys);ax.invert_yaxis();ax.set_xlim(-40,285)
 ax.set_xlabel('Alternative emissions (Mt CO₂e/year; labelled scenarios)')
 for j,v in enumerate(vals):ax.text(v+(3 if v>0 else -3),j,f'{v:+.1f}' if j in (1,2) else f'{v:.1f}',ha='left' if v>=0 else 'right',va='center',fontsize=8)
 ax.set_title('Agricultural process inventory: substitute, do not double count',loc='left',fontweight='bold')
 save(fig,'ScienceFigS42_V99_Agricultural_LCA_Reconciliation.tif')
 fig,ax=plt.subplots(figsize=(7.1,3.4),layout='constrained')
 e=['N','P','K'];removed=np.array([c[f'{z}_removed_kt'] for z in 'npk']);imports=np.array([c[f'{z}_imports_kt'] for z in 'npk'])
 ax.barh(e,removed,color='#d3d8db',label='Removed');ax.barh(e,imports,color='#b57948',height=.46,label='Mineral replacement')
 for i,(r,q) in enumerate(zip(removed,imports)):
  ax.text(r+25,i,f'{q:,.0f} / {r:,.0f} kt',va='center',fontsize=8)
 ax.invert_yaxis();ax.set_xlim(0,max(removed)*1.27);ax.legend(frameon=False,fontsize=8)
 ax.set_xlabel('Elemental nutrient (kt/year)');ax.set_title('Joint recovery × storage × crop availability, not just HTL recovery',loc='left',fontweight='bold')
 save(fig,'ScienceFigS43_V99_Nutrient_Availability_Chain.tif')
 fig,ax=plt.subplots(figsize=(7.1,3.4),layout='constrained')
 # Derived coverage from land scale, illustrative only, not GIS evidence
 rates=np.array([.10,.25,.50,.75,1.0,1.5]);hectares=8.585e6/rates/1e6
 ax.plot(rates,hectares,'o-',color='#287d62');ax.axhline(20,color='#ae6b36',linestyle='--',label='Assumed maximum: 20 Mha')
 ax.set_xlabel('Additional stable-equivalent soil-C accumulation (t C/ha/year)')
 ax.set_ylabel('Required cover-crop area (million hectares)')
 ax.legend(frameon=False,fontsize=8);ax.set_title('Land needed for 8.585 Mt C/year restoration: illustrative limits',loc='left',fontweight='bold')
 save(fig,'ScienceFigS44_V99_Cover_Crop_Land_Feasibility.tif')
 fig,ax=plt.subplots(figsize=(7.1,3.4),layout='constrained')
 ax.plot(x:=np.array([int(z['hubs']) for z in hubs]),y:=np.array([float(z['annual_cost_bn']) for z in hubs]),'o-',color='#317863')
 ax.set_xlabel('Four-module high-temperature reactor hubs');ax.set_ylabel('Annual system cost (US$ bn)')
 ax.set_xlim(-8,265);ax.set_title('Fixed-hub optimisation with joint-conservative agricultural settings',loc='left',fontweight='bold')
 for xx,yy in zip(x,y):ax.text(xx,yy+2,f'{yy:.1f}',ha='center',fontsize=7.5)
 save(fig,'ScienceFigS45_V99_Joint_Crop_Reactor_Deployment.tif')

def verify_grid_preserved():
 for fn in ('FigS1_grid_harvester.tif','FigS22_GridHarvester_Energy_Efficiency.tif'):
  im=Image.open(R/fn);assert im.mode=='RGB';assert tuple(int(round(k)) for k in im.info.get('dpi',(0,0)))==(600,600)
  print('MANDATORY GRID HARVESTER PRESERVED:',fn)

if __name__=='__main__':
 main_cost();crop();npk();uncertainty();supplement();verify_grid_preserved()
