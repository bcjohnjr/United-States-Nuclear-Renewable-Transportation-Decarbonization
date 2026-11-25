#!/usr/bin/env python3
"""Science V9.8 reproducible 600 dpi RGB TIFF figures; no raster AI redraws."""
from pathlib import Path
import json,csv,math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
P=Path(__file__).resolve().parent
I=json.loads((P/'US97_Integrated_Circular_EIA.json').read_text())
B=json.loads((P/'US97_AEO_Boundary.json').read_text())
S=json.loads((P/'US98_Strict_Crop_and_Reactor_Sensitivity.json').read_text())
L=json.loads((P/'US98_Agriculture_Explicit_LCA.json').read_text())
U=json.loads((P/'US98_Paired_Uncertainty_Summary.json').read_text())
sc=I['scenario'];crop=sc['soil_costed_economic_crop'];ref=I['source_weighted_reference_partial_bn'];refe=I['source_weighted_reference_emissions_partial_mt']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8.2,'axes.labelsize':8.2,'axes.titlesize':9,'legend.fontsize':7,'xtick.labelsize':7.5,'ytick.labelsize':7.5,'figure.facecolor':'white','axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':0.7})
navy='#28445c'; teal='#39858a'; lime='#6e9275'; ochre='#bc9252'; grey='#8a959e'; red='#b46661'
def save(fig,name):
 f=P/name;fig.savefig(f,format='tiff',dpi=600,bbox_inches='tight',pad_inches=.16,facecolor='white');plt.close(fig)
 with Image.open(f) as img:img.convert('RGB').save(f,format='TIFF',dpi=(600,600),compression='tiff_lzw')
 print('FIG',name,round(f.stat().st_size/1e6,2),flush=True)
def grid(ax,axis='y'):ax.grid(axis=axis,color='#e5ebef',lw=.65,zorder=0);ax.set_axisbelow(True)
def ptitle(ax,ch,name):ax.set_title(f'{ch}  {name}',loc='left',fontweight='bold',pad=10)
# 1: matched reference economics and conditional gross LCA add-on: do not equate.
cases=S['cases']
fig,(a,b)=plt.subplots(1,2,figsize=(7.0,3.45),gridspec_kw={'width_ratios':[1.1,.9]})
labels=['AEO-based\npartial ref.','Crops / soil\nV9.7','No char or\npyro credit','Half field\navailability','No crops\nV9.7']
vals=[ref,crop['annual_cost_bn'],cases[1]['annual_cost_bn'],cases[2]['annual_cost_bn'],sc['soil_costed_no_crop']['annual_cost_bn']]
a.bar(np.arange(len(vals)),vals,color=[grey,teal,lime,ochre,navy],width=.64,zorder=3)
for j,v in enumerate(vals):a.text(j,v+7,f'{v:,.0f}',ha='center',fontsize=7.5)
a.set_ylim(0,770);a.set_xticks(range(len(vals)),labels,fontsize=7);a.set_ylabel('Annual expenditure (US$ bn)');grid(a);ptitle(a,'A','Alternative-system cost screens')
# Emissions compared on common provisional boundary with explicit agricultural add-on.
alt=crop['emissions_wtw_mt'];add=L['central']['gross_candidate_addon_mt'];avoid=refe-alt
x=np.arange(3);b.bar(x,[refe,alt,alt+add],color=[grey,teal,ochre],width=.6,zorder=3)
for j,v in enumerate([refe,alt,alt+add]):b.text(j,v+35,f'{v:,.0f}',ha='center',fontsize=7.3)
b.set_ylim(0,1860);b.set_xticks(x,['Reference\npartial WTW','Alternative\nlegacy factors','Alternative\n+ gross crop screen'],fontsize=7)
b.set_ylabel('Annual Mt CO₂e');grid(b);ptitle(b,'B','Emissions-boundary sensitivity')
fig.subplots_adjust(left=.075,right=.99,bottom=.25,top=.86,wspace=.33)
save(fig,'ScienceFig1_V98_Cost_LCA_Boundaries.tif')
# 2 13 feedstocks with assumptions explicit + strict resource ceilings.
selected=crop['selected'];ss=sorted(selected,key=lambda x:x['selected_mt'],reverse=True);short=[x['name'].split(' (')[0].replace('Corn stalks and leaves','Corn stalks/leaves').replace('Corn cobs and husks','Corn cobs/husks').replace('Fruit and vegetable processing waste','Food-processing waste').replace('Sugarcane bagasse and field trash','Sugarcane bagasse/trash')[:38] for x in ss]
fig,a=plt.subplots(figsize=(6.7,4.9));yy=np.arange(len(ss));a.barh(yy,[x['max_mt'] for x in ss],color='#edf0f2',height=.68,label='Assumed category cap [A]');a.barh(yy,[x['selected_mt'] for x in ss],color=teal,height=.68,label='Optimiser selected');a.set_yticks(yy,short,fontsize=7.2);a.invert_yaxis();a.set_xlim(0,90);a.set_xlabel('Million dry tonnes/year — category caps are NOT county-validated');grid(a,'x');a.legend(loc='lower right',frameon=False);fig.subplots_adjust(left=.34,right=.98,bottom=.10,top=.95)
save(fig,'ScienceFig2_V98_Crop_Dispatch_and_Unverified_Caps.tif')
# 3 elemental recovery stack and stable-equivalent C service assumptions
fig,(a,b)=plt.subplots(1,2,figsize=(6.9,3.38),gridspec_kw={'width_ratios':[1.04,.96]})
x=np.arange(3);water=np.array([crop[e+'_water_kt'] for e in 'npk']);char=np.array([crop[e+'_char_kt'] for e in 'npk']);imports=np.array([crop[e+'_imports_kt'] for e in 'npk']);a.bar(x,water,color=teal,label='Treated aqueous recovery');a.bar(x,char,bottom=water,color=lime,label='HTL solids');a.bar(x,imports,bottom=water+char,color=ochre,label='Purchased replacement')
a.set_xticks(x,['N','P','K']);a.set_ylabel('Elemental nutrients (kt/year)');ptitle(a,'A','Nutrient mass conservation');grid(a)
bars=[crop['stable_hydrochar_c_mt'],crop['stable_pyrolysis_c_mt'],crop['stable_soil_c_need_mt'],cases[1]['cover_crop_c_mt']];lb=['HTL char\ncredit [A]','Pyro C\ncredit [A]','Soil C\nrequired','Cover-crop C\nif credits 0'];b.bar(np.arange(4),bars,color=[teal,grey,red,lime]);b.set_xticks(range(4),lb,fontsize=6.5);b.set_ylabel('Million tonnes C/year');ptitle(b,'B','Stable-equivalent C screens');grid(b)
fig.legend(*a.get_legend_handles_labels(),loc='lower center',ncol=3,frameon=False,bbox_to_anchor=(.5,-.01),fontsize=7);fig.subplots_adjust(left=.1,right=.99,bottom=.30,top=.85,wspace=.34)
save(fig,'ScienceFig3_V98_NPK_C_and_Conservative_Restoration.tif')
# 4 explicit directed HTL and soil return diagram, labels never touch arrows.
fig,a=plt.subplots(figsize=(6.9,4.25));a.set_xlim(0,12);a.set_ylim(0,7.6);a.axis('off')
def rect(x,y,w,h,txt,c='#f2f6f6'):
 p=FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.14',lw=.9,ec=navy,fc=c);a.add_patch(p);a.text(x+w/2,y+h/2,txt,ha='center',va='center',fontsize=8.3,linespacing=1.3)
def arr(x1,y1,x2,y2,label='',dy=.28):
 a.annotate('',xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(arrowstyle='-|>',lw=1.4,color=navy,shrinkA=3,shrinkB=3))
 if label:a.text((x1+x2)/2,(y1+y2)/2+dy,label,ha='center',va='bottom',fontsize=7,color=navy)
rect(.25,4.9,2.45,1.05,'Crop residues\nsoil-constrained', '#e8f0e9')
rect(.25,2.2,2.45,1.05,'Seaweed HTL\nseparate marine route','#e8f0f6')
rect(4.15,3.9,3.2,1.5,'HTL + upgrading\nheat • H₂ • separation','#e8eef2')
rect(9.15,5.8,2.4,1.0,'Transport\nliquid fuel','#f6eddc')
rect(9.15,3.4,2.4,1.0,'Treated nutrient\nconcentrate','#e8f0e9')
rect(9.15,.85,2.4,1.05,'Separated hydrochar\ncharacterisation','#f1e9dd')
rect(4.15,.3,3.2,1.1,'Field receiving soil\npermitted rate + tests','#ebf4e8')
arr(2.75,5.35,4.1,4.95);arr(2.75,2.75,4.1,4.25)
arr(7.42,5.20,9.12,6.05)
arr(7.42,4.54,9.12,3.9)
arr(6.4,3.86,9.15,1.65)
# arrows to field BELOW boxes, not across or through any text
arr(9.5,3.33,6.8,1.53)
arr(9.2,1.26,7.38,1.07)
a.text(.2,7.35,'Nutrients, hydrochar and process-water return require treatment and verification',fontsize=9.2,fontweight='bold',color=navy)

fig.subplots_adjust(left=.02,right=.99,bottom=.025,top=.97)
save(fig,'ScienceFig4_V98_HTL_Return_Flow_With_Arrows.tif')
# 5 MC and reactor counts
arrs=[]
with (P/'us98_paired_uncertainty.csv').open(encoding='utf-8-sig') as f:
 for row in csv.DictReader(f):arrs.append(float(row['abatement_usd_t']))
fig,(a,b)=plt.subplots(1,2,figsize=(6.95,3.4))
a.hist(arrs,bins=28,color=teal,edgecolor='white',linewidth=.5);a.axvline(U['abt_usd_t_median'],color=red,lw=1.5,label=f"Median ${U['abt_usd_t_median']:.0f}/t")
a.set_xlabel('Conditional partial abatement cost (US$/t CO₂e)');a.set_ylabel('Draws (500 total)');ptitle(a,'A','Paired parameter screens');a.legend(frameon=False,loc='upper right');grid(a)
qs=S['fixed_hub_cases'];a2=b;b.plot([x['hubs'] for x in qs],[x['annual_cost_bn'] for x in qs],'-o',color=navy,ms=4);b.axvline(166,color=ochre,linestyle='--',label='Iterative ~166 hubs');b.set_xlabel('Reactor hubs (4 modules per hub)');b.set_ylabel('Annual cost (US$ bn)');ptitle(b,'B','Nonconvex learning screen');b.legend(frameon=False,fontsize=7);grid(b)
fig.subplots_adjust(left=.09,right=.98,bottom=.20,top=.85,wspace=.35)
save(fig,'ScienceFig5_V98_Uncertainty_and_Reactor_Screen.tif')
# Supplementary 4 figures
fig,(a,b)=plt.subplots(1,2,figsize=(6.8,3.2)); names=['Fertilizer\nmanufacture','Applied-N\nN₂O screen','HTL aqueous\ntreatment','Char logistics','Pyro C logistics']
ll=L['central']['lines'];v=[ll['fertilizer_manufacture_mt'],ll['soil_n2o_sensitivity_mt'],ll['aqueous_treatment_mt'],ll['hydrochar_transport_application_mt'],ll['pyrocarbon_delivery_mt']];a.bar(np.arange(5),v,color=[teal,lime,ochre,grey,red]);a.set_xticks(range(5),names,fontsize=6.9);a.set_ylabel('Gross candidate Mt CO₂e/year');ptitle(a,'A','Agricultural process inventory');grid(a)
b.bar([0,1,2],[z['gross_candidate_addon_mt'] for z in L['cases'][:3]],color=[lime,teal,ochre]);b.set_xticks(range(3),['Low','Central','High']);b.set_ylabel('Gross candidate Mt CO₂e/year');ptitle(b,'B','Unverified coefficient ranges');grid(b);fig.subplots_adjust(left=.1,right=.98,bottom=.26,top=.85,wspace=.34)
save(fig,'ScienceFigS38_V98_Explicit_Agri_Emissions.tif')
fig,a=plt.subplots(figsize=(6.7,3.3));r=S['cases'];a.bar(range(len(r)),[x['annual_cost_bn'] for x in r],color=[teal,lime,ochre,grey]);a.set_ylim(0,730);a.set_xticks(range(len(r)),['166 Mt /\ncredit screen','166 Mt / no\ncarbon credits','83 Mt /\nprimary only','41.5 Mt /\nprimary only'],fontsize=7);a.set_ylabel('Annual alternative-system cost (US$ bn)');grid(a);fig.subplots_adjust(left=.1,right=.98,bottom=.24,top=.93)
save(fig,'ScienceFigS39_V98_Regional_Data_Gap_Stress.tif')
fig,(a,b)=plt.subplots(1,2,figsize=(6.8,3.1));m=I['marine_to_land_optional'];els=['N','P','K'];idx=np.arange(3);allow=[m['eligible_treated_marine_npk_to_cropland_kt'][e] for e in 'npk'];a.bar(idx,allow,color=[teal,lime,ochre]);a.set_xticks(idx,els);a.set_ylabel('Hypothetical cropland offset (kt/year)');ptitle(a,'A','Permitted marine recovery [A]');grid(a)
v=[m['avoided_fertilizer_purchase_value_bn'],m['foregone_existing_offshore_fertilizer_sale_credit_bn'],m['purification_desalting_and_field_logistics_extra_bn'],m['extra_cost_after_opportunity_cost_bn']];b.bar(range(4),[x*1000 for x in v],color=[lime,red,ochre,teal]);b.set_xticks(range(4),['Avoided\nimports','Lost sale\nrevenue','Cleaning +\nlogistics','Net extra\ncost'],fontsize=7);b.set_ylabel('US$ million/year');ptitle(b,'B','Non-identical sale vs farm prices');grid(b);fig.subplots_adjust(left=.1,right=.98,bottom=.24,top=.84,wspace=.34)
save(fig,'ScienceFigS40_V98_Marine_Market_Opportunity_Cost.tif')
fig,a=plt.subplots(figsize=(6.5,3.25));z=B['h2_energy_basis_bracket'];v=[z[k]['hydrogen_mass_mt'] for k in ['HHV','LHV']];a.bar([0,1],v,color=[teal,ochre],width=.55);a.set_xticks([0,1],['Provisional EIA HHV\n39.4 kWh/kg','LHV comparison\n33.33 kWh/kg']);a.set_ylabel('Physical reference H₂ (million tonnes/yr)');a.set_ylim(0,7);grid(a);fig.subplots_adjust(left=.15,right=.96,bottom=.26,top=.9)
save(fig,'ScienceFigS41_V98_Reference_Hydrogen_HHV_LHV.tif')
