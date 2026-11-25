#!/usr/bin/env python3
"""Publication-width 600-dpi RGB TIFF figures from deterministic V9.6 CSVs."""
import csv,json,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from pathlib import Path
HERE=Path(__file__).resolve().parent
DATA=json.loads((HERE/'US96_Shared_2050_Screen.json').read_text())['results']
LABELS=['Lower BEV cost','Central','Higher BEV cost']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.labelsize':9,'axes.titlesize':10,'xtick.labelsize':8.5,'ytick.labelsize':8.5,'legend.fontsize':8,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white','savefig.facecolor':'white','axes.linewidth':0.7})

def save(fig,name):
 path=HERE/name
 fig.savefig(path,dpi=600,facecolor='white',bbox_inches='tight',pad_inches=.15,format='tiff')
 plt.close(fig)
 with Image.open(path) as im:
  if im.mode!='RGB':im.convert('RGB').save(path,format='TIFF',dpi=(600,600),compression='tiff_lzw')
 print(name,path.stat().st_size)

fig,ax=plt.subplots(1,2,figsize=(7.25,3.5),gridspec_kw={'width_ratios':[1.3,1]})
x=np.arange(3)
a=[d['reference_screen_bn'] for d in DATA]; b=[d['alt_screen_bn'] for d in DATA]
w=.36
ax[0].bar(x-w/2,a,w,color='#53677a',label='AEO-based reference')
ax[0].bar(x+w/2,b,w,color='#167c83',label='Petroleum-free screen')
for i,v in enumerate(a):ax[0].text(i-w/2,v+9,f'{v:.0f}',ha='center',fontsize=8)
for i,v in enumerate(b):ax[0].text(i+w/2,v+9,f'{v:.0f}',ha='center',fontsize=8)
ax[0].set_xticks(x,LABELS,rotation=0)
ax[0].set_ylim(0,850)
ax[0].set_ylabel('Annual expenditure (US$ bn, 2026 basis)')
ax[0].legend(loc='upper left',frameon=False,ncol=1)
ax[0].grid(axis='y',color='#dde3e7',linewidth=.6)
ax[0].set_axisbelow(True)
ax[0].text(-.38,825,'(a)',weight='bold',fontsize=10)
vals=[d['cost_per_tonne_avoided_usd'] for d in DATA]
ax[1].bar(x,vals,width=.55,color='#927a51')
for i,v in enumerate(vals):ax[1].text(i,v+6,f'${v:.0f}',ha='center',fontsize=9,weight='bold')
ax[1].set_ylim(0,225)
ax[1].set_xticks(x,LABELS)
ax[1].set_ylabel('Screening cost (US$/t CO₂e avoided)')
ax[1].grid(axis='y',color='#dde3e7',linewidth=.6)
ax[1].set_axisbelow(True)
ax[1].text(-.35,218,'(b)',weight='bold',fontsize=10)
fig.subplots_adjust(left=.09,right=.985,top=.89,bottom=.16,wspace=.4)
save(fig,'Fig7_AEO2026_Shared_2050_Cost_Abatement.tif')

rows=list(csv.DictReader(open(HERE/'us96_deployment_stress.csv')))
h=np.array([float(r['hubs']) for r in rows]); y=np.array([float(r['annual_cost_bn']) for r in rows]);
fig,ax=plt.subplots(figsize=(7.1,3.6))
ax.plot(h,y,color='#176e7b',marker='o',ms=4,lw=1.6)
ax.axvspan(0,250,color='#e8f2ee',alpha=.65,zorder=0)
ax.axvline(250,ls='--',color='#777',lw=1)
ax.scatter([184,945],[y[np.where(h==184)[0][0]],y[np.where(h==945)[0][0]]],color='#a05a31',s=24,zorder=3)
ax.annotate('Iterative solution\n184 hubs',xy=(184,y[list(h).index(184)]),xytext=(350,688),fontsize=8,arrowprops={'arrowstyle':'-','lw':.8,'color':'#5c5c5c'})
ax.annotate('945 hubs\n3,780 modules',xy=(945,y[list(h).index(945)]),xytext=(975,680),fontsize=8,arrowprops={'arrowstyle':'-','lw':.8,'color':'#5c5c5c'})
ax.text(22,712,'Illustrative restricted fleet\n0–250 hubs',size=8,color='#376956')
ax.set_xlim(-25,1150);ax.set_ylim(635,730)
ax.set_xlabel('Four-module reactor hubs (fixed count)');ax.set_ylabel('Alternative annual cost (US$ bn)')
ax.grid(axis='y',color='#e0e4e6',lw=.65)
ax.set_axisbelow(True)
fig.subplots_adjust(left=.12,right=.97,top=.96,bottom=.17)
save(fig,'FigS32_Reactor_Deployment_Cost_Constraint.tif')

fig,ax=plt.subplots(figsize=(7.1,3.2))
keys=['reference_energy_2026usd_bn','tax_removed_bn','reference_ldv_net_premium_bn','reference_truck_net_premium_bn','reference_charging_bn','reference_coverage_add_bn']
names=['Energy expenditure','Tax transfer removed','LDV net premium','Truck net premium','Charging','Scope allowance']
cent=DATA[1];values=[cent[k] for k in keys];values[1]*=-1
colors=['#53677a','#bf6f57','#549a8f','#9d817a','#7194b0','#bca16a']
xx=np.arange(len(values))
ax.bar(xx,values,color=colors,width=.62)
for i,v in enumerate(values):
 ax.text(i,v+(5 if v>=0 else -7),f'{v:+.1f}' if i else f'{v:.1f}',fontsize=8,ha='center',va='bottom' if v>=0 else 'top')
ax.axhline(0,color='#333',lw=.8)
ax.set_xticks(xx,names,rotation=22,ha='right')
ax.set_ylim(-60,480);ax.set_ylabel('Annual contribution (US$ bn)')
ax.grid(axis='y',color='#e4e6e8',lw=.6);ax.set_axisbelow(True)
fig.subplots_adjust(left=.12,right=.98,top=.95,bottom=.28)
save(fig,'FigS33_AEO_Reference_Boundary_Components.tif')

# RSC TOC: 8cm x 4cm at 600 dpi, original programmatic art
fig,ax=plt.subplots(figsize=(3.15,1.57))
ax.bar([0,1],[cent['reference_screen_bn'],cent['alt_screen_bn']],color=['#53677a','#167c83'],width=.55)
for i,v in enumerate([cent['reference_screen_bn'],cent['alt_screen_bn']]):ax.text(i,v+20,f'${v:.0f}bn',ha='center',fontsize=8)
ax.set_xticks([0,1],['AEO reference','Petroleum-free'],fontsize=7)
ax.set_ylim(0,850);ax.set_yticks([0,400,800]);ax.tick_params(axis='y',labelsize=6)
ax.grid(axis='y',color='#dedede',lw=.4);ax.set_axisbelow(True)
fig.subplots_adjust(left=.17,right=.98,top=.96,bottom=.23)
save(fig,'TOC_2050_Transport_Cost_Screen.tif')
