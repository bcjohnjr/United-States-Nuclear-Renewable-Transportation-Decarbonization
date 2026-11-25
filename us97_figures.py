#!/usr/bin/env python3
"""V9.7 figures for *Science*: five main TIFFs + four technical SI TIFFs.
Every value comes from V9.7 reproducible JSON/CSV results; no generated data.
600 dpi RGB, <=7 in nominal width, restrained journal typography.
"""
import json,csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch,Rectangle
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent
boundary=json.loads((P/'US97_AEO_Boundary.json').read_text())
integ=json.loads((P/'US97_Integrated_Circular_EIA.json').read_text())
mc=json.loads((P/'US97_Paired_Uncertainty_Summary.json').read_text())
base=integ['scenario']['soil_costed_economic_crop']
marine=integ['scenario']['crop_seaweed_220gw_imposed']
ref=integ['source_weighted_reference_partial_bn']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8.1,'axes.labelsize':8.2,'xtick.labelsize':7.5,'ytick.labelsize':7.5,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.7,'figure.facecolor':'white','savefig.facecolor':'white'})
NAVY='#1c3c52';TEAL='#2b7880';SLATE='#6d7c8a';OCHRE='#aa7c3f';GREEN='#527b65';RED='#a7534e'

def save(fig,name):
 f=P/name;fig.savefig(f,dpi=600,format='tiff',bbox_inches='tight',pad_inches=.13,facecolor='white')
 plt.close(fig)
 with Image.open(f) as im:
  if im.mode!='RGB':im.convert('RGB').save(f,format='TIFF',dpi=(600,600),compression='tiff_lzw')
  else:
   # ensure reasonable compressed science delivery and accurate metadata
   im.copy().save(f,format='TIFF',dpi=(600,600),compression='tiff_lzw')
 print('FIG',f.name,round(f.stat().st_size/1e6,2),'MB')

def styl(ax,axis='y'):
 ax.grid(axis=axis,color='#e4e9ec',lw=.55);ax.set_axisbelow(True)

# Main 1: comparable source-weighted 2050 ownership and emissions cost screen.
sc=boundary['results'];idx=[1,2]
fig,(a,b)=plt.subplots(1,2,figsize=(6.9,3.35),gridspec_kw={'width_ratios':[1.2,1]})
labels=['Stock-weighted\nstraight-line','Stock-weighted\n7% financed','Crop + nutrient\nconstraints']
refr=[sc[1]['reference_screen_bn'],sc[2]['reference_screen_bn'],ref]
alts=[sc[1]['alternative_cost_bn'],sc[2]['alternative_cost_bn'],base['annual_cost_bn']]
x=np.arange(3);w=.35
br=a.bar(x-w/2,refr,w,color=SLATE,label='2050 reference screen')
ba=a.bar(x+w/2,alts,w,color=TEAL,label='Petroleum-free alternative')
for cont in (br,ba):
 for bar in cont:a.text(bar.get_x()+bar.get_width()/2,bar.get_height()+9,str(round(bar.get_height())),ha='center',fontsize=7)
a.set_ylim(0,875);a.set_ylabel('Annual US$ bn (model price basis)');a.set_xticks(x,labels,fontsize=7);styl(a)
a.legend(ncol=1,loc='upper left',frameon=False,fontsize=7)
a.text(-.08,1.04,'A',transform=a.transAxes,fontweight='bold',fontsize=10)
keys=['Source-weighted','7% financed','Crop / NPK']
vals=[sc[1]['abatement_usd_t'],sc[2]['abatement_usd_t'],1000*(base['annual_cost_bn']-ref)/(sc[1]['reference_partial_wtw_mt']-base['emissions_wtw_mt'])]
b.bar(np.arange(3),vals,width=.6,color=[OCHRE,'#bc976e',GREEN]);styl(b)
for i,v in enumerate(vals):b.text(i,v+5,f'{v:.0f}',ha='center',fontsize=8)
b.set_ylabel('Partial-screening US$/t CO₂e avoided');b.set_ylim(0,210);b.set_xticks(np.arange(3),keys,rotation=14,ha='right',fontsize=7)
b.text(-.12,1.04,'B',transform=b.transAxes,fontweight='bold',fontsize=10)
fig.subplots_adjust(left=.09,right=.985,bottom=.26,top=.9,wspace=.38)
save(fig,'ScienceFig1_V97_2050_Cost_Abatement.tif')

# Main 2: selection in distinct feedstock categories.
selected=base['selected']; names=[v['name'].replace(' (excluding cobs/husks)','').replace(' (separate field/process stream)','').replace(' (mill residue)','') for v in selected]
used=np.array([v['selected_mt'] for v in selected]);caps=np.array([v['max_mt'] for v in selected]);idx=np.arange(len(names))
fig,a=plt.subplots(figsize=(6.8,4.25))
a.barh(idx,caps,color='#e9eef0',height=.65,label='Assumed class ceiling [A]')
a.barh(idx,used,color=GREEN,height=.65,label='Selected by optimiser')
for i,val in enumerate(used):
 if val>.1:a.text(val+.9,i,f'{val:.0f}',va='center',fontsize=7)
a.set_yticks(idx,names,fontsize=7);a.invert_yaxis();a.set_xlim(0,100)
a.set_xlabel('Selected and available dry biomass (Mt/year)')
a.legend(loc='lower right',frameon=False,ncol=1,fontsize=7)
for t in (20,40,60,80):a.axvline(t,lw=.45,color='#e5e9ed',zorder=0)
a.text(.98,1.02,f'National cap = 166 Mt/year  |  Selected = {used.sum():.0f} Mt/year',ha='right',va='bottom',fontsize=7.5,transform=a.transAxes,color=NAVY)
fig.subplots_adjust(left=.40,right=.97,bottom=.14,top=.93)
save(fig,'ScienceFig2_V97_All_Crop_Waste_Economic_Dispatch.tif')

# Main 3: NPK closed mass accounting and soil stable-equivalent C.
fig,(a,b)=plt.subplots(1,2,figsize=(6.9,3.6),gridspec_kw={'width_ratios':[1.12,.88]})
x=np.arange(3);water=np.array([base[e+'_water_kt'] for e in ('n','p','k')]);char=np.array([base[e+'_char_kt'] for e in ('n','p','k')]);imp=np.array([base[e+'_imports_kt'] for e in ('n','p','k')])
a.bar(x,water,.58,color=TEAL,label='Recovered: treated water')
a.bar(x,char,.58,bottom=water,color=GREEN,label='Recovered: HTL solid')
a.bar(x,imp,.58,bottom=water+char,color=OCHRE,label='External replacement')
for i,total in enumerate(water+char+imp):a.text(i,total+30,f'{total:.0f}',ha='center',fontsize=7)
a.set_xticks(x,['N','P','K']);a.set_ylabel('Elemental nutrient balance (kt/year)');a.set_ylim(0,1850);styl(a)
a.legend(frameon=False,fontsize=6.6,loc='upper left',bbox_to_anchor=(-.01,1.02))
a.text(-.08,1.05,'A',transform=a.transAxes,fontweight='bold',fontsize=10)
c=[base['stable_hydrochar_c_mt'],base['stable_pyrolysis_c_mt'],base['cover_crop_stable_c_mt']]
b.bar([0],[c[0]],width=.56,color=GREEN,label='HTL hydrochar')
b.bar([0],[c[1]],bottom=[c[0]],width=.56,color=SLATE,label='Methane pyrolysis C')
if c[2]>0:b.bar([0],[c[2]],bottom=[c[0]+c[1]],width=.56,color=OCHRE,label='Cover crop C')
b.bar([1],[base['stable_soil_c_need_mt']],color='#d1d6d9',width=.56,label='Required stable-equivalent C')
b.set_ylim(0,12);b.set_xlim(-.7,1.7)
b.set_xticks([0,1],['Modelled\nreturns','Soil carbon\nrequirement'],fontsize=7)
b.set_ylabel('Stable-equivalent carbon (Mt/year)');styl(b)
b.text(0,sum(c)+.3,f'{sum(c):.2f}',ha='center',fontsize=7)
b.text(1,base['stable_soil_c_need_mt']+.3,f'{base["stable_soil_c_need_mt"]:.2f}',ha='center',fontsize=7)
b.legend(loc='upper left',frameon=False,fontsize=6.5)
b.text(-.1,1.05,'B',transform=b.transAxes,fontweight='bold',fontsize=10)
fig.subplots_adjust(left=.10,right=.985,bottom=.19,top=.89,wspace=.4)
save(fig,'ScienceFig3_V97_NPK_Carbon_Soil_Closure.tif')

# Main 4: clean author-drawn technical process schematic. Orthogonal connectors
# occupy corridors between cards, never cross caption or textbox interiors.
fig,a=plt.subplots(figsize=(6.95,4.35));a.set_xlim(0,14);a.set_ylim(0,10);a.axis('off')
def card(x,y,w,h,text,face='#f4f7f8',edge='#b9c7cf',fs=8):
 p=FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.09,rounding_size=.13',linewidth=.85,facecolor=face,edgecolor=edge)
 a.add_patch(p);a.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=fs,linespacing=1.3,color=NAVY)
def arrow(x0,y0,x1,y1,colour=NAVY,lw=1.2):
 a.add_patch(FancyArrowPatch((x0,y0),(x1,y1),arrowstyle='-|>',mutation_scale=11,color=colour,linewidth=lw,shrinkA=2,shrinkB=2))
card(.2,7.5,3.1,1.3,'Field-screened crop\nresidues: straw, cobs,\nhusks, bagasse',face='#eef5ef')
card(.2,5.45,3.1,1.3,'Coastal macroalgae\n(optional): desalting\nand separation',face='#eaf1f4')
card(5.1,6.25,3.3,1.75,'Hydrothermal liquefaction\nand fuel upgrading\n(additive co-feed screen)',face='#e4eef2',fs=8)
card(10.5,8.0,3.25,1.1,'Liquid transport fuels',face='#eaf1f4')
card(10.5,6.3,3.25,1.05,'Hydrochar / solid residue',face='#eef5ef')
card(10.5,4.5,3.25,1.25,'Aqueous-phase recovery\nN / P / K concentrate',face='#eef5ef')
card(.2,2.2,3.1,1.25,'Methane pyrolysis\nsolid carbon (qualified)',face='#f8f3e9')
card(5.1,1.4,4.0,1.65,'Field return after testing\nchar + treated nutrient product\n+ permitted pyro-carbon',face='#f4f7f5')
card(10.5,1.4,3.25,1.65,'Soil monitoring / imports\nSOC, N, P, K and metals\nexternal fertilizer if needed',face='#f8f3e9',fs=7.7)
arrow(3.42,8.15,5,7.35);arrow(3.42,6.1,5,6.85)
arrow(8.53,7.75,10.38,8.45);arrow(8.53,7.12,10.38,6.85);arrow(8.53,6.55,10.38,5.1)
# returns down side lanes and into the soil box, with branches outside cards
for yy in (6.82,5.1):
 a.plot([13.78,13.95],[yy,yy],color=GREEN,lw=1.0)
a.plot([13.95,13.95],[5.1,3.60],color=GREEN,lw=1.0)
a.plot([13.95,8.5],[3.60,3.60],color=GREEN,lw=1.0)
arrow(8.5,3.6,7.1,3.1,GREEN)
arrow(3.42,2.82,5,2.6,OCHRE)
arrow(9.2,2.2,10.38,2.2,GREEN)
a.text(7.0,.45,'Only certified, treated products are eligible for land application. Seaweed nutrient sales cannot also be credited as on-farm fertilizer.',
       ha='center',fontsize=7,color='#394b56')
fig.subplots_adjust(left=.02,right=.98,bottom=.05,top=.97)
save(fig,'ScienceFig4_V97_Terrestrial_Marine_HTL_Soil_Flow.tif')

# Main 5: paired 500-draw abatement-cost distribution, with deterministic soil case.
vals=np.array([float(r['abatement_usd_t']) for r in csv.DictReader(open(P/'us97_paired_uncertainty.csv'))])
fig,(a,b)=plt.subplots(1,2,figsize=(6.9,3.3),gridspec_kw={'width_ratios':[1.1,.9]})
a.hist(vals,bins=np.linspace(-100,330,28),color=SLATE,edgecolor='white',lw=.5)
a.axvline(float(np.median(vals)),color=TEAL,lw=1.6,label=f'Median ${np.median(vals):.0f}/t')
a.axvline(0,color=RED,lw=1,ls='--');a.set_xlabel('Partial-screening US$/t CO₂e avoided');a.set_ylabel('Monte Carlo draws (500)');a.legend(frameon=False,fontsize=7,loc='upper right');styl(a)
a.text(-.1,1.04,'A',transform=a.transAxes,fontweight='bold',fontsize=10)
rows=list(csv.DictReader(open(P/'us97_integrated_results.csv',encoding='utf-8-sig')))
case_names=['No crop','Costed crop','Lower nutrient\nrecovery','No pyro soil\ncredit','Imposed seaweed']
case_keys=['soil_costed_no_crop','soil_costed_economic_crop','crop_low_nutrient_recovery','crop_no_pyro_soil_credit','crop_seaweed_220gw_imposed']
rs={r['case']:r for r in rows};y=[float(rs[k]['system_cost_bn']) for k in case_keys]
b.barh(np.arange(len(y)),y,color=[SLATE,GREEN,OCHRE,SLATE,TEAL],height=.6)
b.set_xlim(0,830);b.invert_yaxis();b.set_yticks(np.arange(len(y)),case_names,fontsize=7)
b.set_xlabel('Annual alternative cost (US$ bn)');styl(b,'x')
for i,val in enumerate(y):b.text(val+8,i,f'{val:.0f}',va='center',fontsize=7)
b.text(-.2,1.04,'B',transform=b.transAxes,fontweight='bold',fontsize=10)
fig.subplots_adjust(left=.11,right=.985,bottom=.22,top=.90,wspace=.51)
save(fig,'ScienceFig5_V97_Uncertainty_Resource_Constraints.tif')

# SI: treated seaweed nutrient product and fields. No DOUBLE CREDIT.
fig,(a,b)=plt.subplots(1,2,figsize=(6.9,3.1))
land=integ['marine_to_land_optional'];xs=np.arange(3)
coastal=marine['marine']['recovered_treated_product_kt'];eligible=land['eligible_treated_marine_npk_to_cropland_kt'];remaining=land['residual_elemental_imports_kt']
a.bar(xs,[coastal[e] for e in ('n','p','k')],color=TEAL,width=.6,label='Treated marine coproduct')
a.bar(xs,[eligible[e] for e in ('n','p','k')],color=GREEN,width=.32,label='Illustrative transfer to fields')
a.set_xticks(xs,['N','P','K']);a.set_ylabel('Elemental nutrient (kt/year)');a.legend(frameon=False,fontsize=7);styl(a)
a.text(-.09,1.05,'A',fontweight='bold',transform=a.transAxes)
b.bar(xs,[remaining[e] for e in ('n','p','k')],color=OCHRE,width=.55)
b.set_xticks(xs,['N','P','K']);b.set_ylabel('Remaining cropland fertilizer import (kt)');styl(b)
b.text(-.1,1.05,'B',fontweight='bold',transform=b.transAxes)
fig.subplots_adjust(left=.09,right=.985,top=.89,bottom=.16,wspace=.4)
save(fig,'ScienceFigS34_V97_Seaweed_Treated_Nutrient_Transfer.tif')

# SI: separate marine and terrestrial hydrochar carbon and explicit uncertainty.
fig,a=plt.subplots(figsize=(6.7,3.25))
feed=['Terrestrial HTL\n166 Mt (dry)','Marine HTL\n19.9 Mt (dry)']
char=[base['crop_hydrochar_mt'],marine['seaweed_hydrochar_screen_mt']]
a.bar(np.arange(2),char,color=[GREEN,TEAL],width=.55)
for i,v in enumerate(char):a.text(i,v+.45,f'{v:.2f} Mt',ha='center',fontsize=8)
a.set_xticks([0,1],feed);a.set_ylim(0,25);a.set_ylabel('Modeled solid hydrochar coproduct (Mt/year)');styl(a)
a.text(.5,23,'Marine hydrochar receives NO default cropland carbon credit;\nsoil use requires desalting, contaminant tests and stability evidence.',ha='center',fontsize=7,color=NAVY)
fig.subplots_adjust(left=.13,right=.985,top=.93,bottom=.20)
save(fig,'ScienceFigS35_V97_Separate_Hydrochar_Streams.tif')

# SI: fertilizer recovery stress & soil return as separate paths.
fig,a=plt.subplots(figsize=(6.75,3.4))
labels=['Central recovery','Half recovery','No pyro-carbon\nsoil equivalence','No hydrochar\nstability credit']
keys=['soil_costed_economic_crop','crop_low_nutrient_recovery','crop_no_pyro_soil_credit','crop_no_stable_hydrochar']
data=[integ['scenario'][k] for k in keys]
x=np.arange(len(labels));w=.2
for i,e in enumerate(('n','p','k')):
 a.bar(x+(i-1)*w,[z[e+'_imports_kt'] for z in data],width=w,label=e,color=[TEAL,GREEN,OCHRE][i])
a.set_xticks(x,labels,fontsize=7);a.set_ylabel('Imported replacement (kt element/year)');a.legend(frameon=False,ncol=3,loc='upper left',fontsize=7);a.set_ylim(0,1200);styl(a)
fig.subplots_adjust(left=.12,right=.975,bottom=.25,top=.93)
save(fig,'ScienceFigS36_V97_NPK_Recovery_Stress.tif')

# SI: reference H2 emissions and year-2050 stock-pricing choices.
fig,(a,b)=plt.subplots(1,2,figsize=(6.9,3.2))
import us97_aeo_boundary as _eia_h2
eme=[_eia_h2.emission_inventory(10,50,v) for v in (0,7.5,15)]
a.plot([r['reference_h2_production_kgco2_kg'] for r in eme],[r['screening_wtw_mt'] for r in eme],marker='o',color=TEAL)
a.set_xlabel('Assumed reference H₂ production (kg CO₂e/kg H₂)');a.set_ylabel('Partial reference WTW (Mt CO₂e/year)');styl(a)
a.text(-.09,1.05,'A',fontweight='bold',transform=a.transAxes)
cs=boundary['results'][:3]
b.bar(np.arange(3),[r['abatement_usd_t'] for r in cs],color=[SLATE,GREEN,OCHRE]);b.set_xticks(np.arange(3),['Old 80%\n300-mile','EIA stock\nweighted','Financed\n7%'],fontsize=7)
b.set_ylabel('Partial-screening cost (US$/t CO₂e)');styl(b)
b.text(-.1,1.05,'B',fontweight='bold',transform=b.transAxes)
fig.subplots_adjust(left=.1,right=.985,top=.91,bottom=.25,wspace=.43)
save(fig,'ScienceFigS37_V97_Reference_H2_and_BEV_Price.tif')
print('FINISHED')
