"""Publication-quality supplementary charts and schematic crop HTL/soil cycle for U.S. V9.1.
Reads only generated scenario CSV/JSON. Assumed field-scale logistics are NOT represented.
"""
from pathlib import Path
import csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,FancyBboxPatch,FancyArrowPatch,Polygon
from matplotlib.lines import Line2D
import us2_basemap as B
P=Path(__file__).resolve().parent
R=json.load(open(P/'us9_crop_residue_results.json'))
T=R['paired_crop_full_sustainable_cap_forced'];S=T['soil'];N=S['nutrients']
rows={r['scenario']:r for r in csv.DictReader(open(P/'us9_crop_residue_scenarios.csv'))}
COL={'navy':'#10283d','green':'#17876d','tan':'#bf9b70','yellow':'#e5b258','blue':'#3a88b7','red':'#c75d57','gray':'#647887','pale':'#f5f8f7','line':'#d9e2e5','violet':'#7859a2'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})

def save(f,n):
 f.savefig(P/(n+'.tif'),dpi=600,bbox_inches='tight',facecolor='white',format='tiff',pil_kwargs={'compression':'tiff_lzw','dpi':(600,600)});plt.close(f)

def box(ax,x,y,w,h,head,body,fc='#ffffff',ec='#b0c1c8',hs=12,bs=9):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.018,rounding_size=0.018',fc=fc,ec=ec,lw=1.4))
 ax.text(x+.025,y+h-.043,head,color=COL['navy'],weight='bold',fontsize=hs,va='top')
 ax.text(x+.025,y+h-.126,body,color=COL['gray'],fontsize=bs,va='top',linespacing=1.45)

def arr(ax,a,b,col='#677b86',style='-|>',rad=0):
 ax.add_patch(FancyArrowPatch(a,b,arrowstyle=style,mutation_scale=19,lw=2,color=col,connectionstyle=f'arc3,rad={rad}'))

def cycle():
 fig=plt.figure(figsize=(17,10));ax=fig.add_axes([.035,.12,.93,.78]);ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis('off')
 fig.text(.045,.96,'Crop residues → HTL fuels → treated nutrient recovery → soils',fontsize=20,weight='bold',color=COL['navy'],va='top')
 fig.text(.045,.917,'U.S. V9.1 paired 166 Mt/yr residue scenario | indicative national mass balance, not a field application permit',fontsize=11,color=COL['gray'])
 box(ax,.01,.63,.26,.24,'CROP STRAW / STOVER / HUSKS',f'{S["feedstock_mt"]:.0f} Mt dry residues annually\nSustainable local retention comes first\nCollect, transport, preprocess',fc='#f8f3e7',hs=11)
 box(ax,.365,.63,.26,.24,'HYDROTHERMAL LIQUEFACTION',f'{S["htl_biocrude_fuel_twh"]:.0f} TWh/yr liquid-fuel energy\nAssumed upstream yield & upgrading\nAqueous, char and gas coproducts',fc='#e8f2f8',hs=11)
 box(ax,.735,.64,.25,.22,'TRANSPORT FUELS',f'{S["htl_biocrude_fuel_twh"]:.0f} TWh of upgraded liquid fuels\nFuel-value contribution included\nin modelled system cost',fc='#eaf4ed',hs=11)
 box(ax,.355,.23,.275,.22,'HYDROCHAR RECOVERY',f'{S["hydrochar_return_mt"]:.2f} Mt solids returned\n{S["hydrochar_stable_c_mt"]:.2f} Mt stable C assumed\nTest contaminants & agronomy',fc='#f4eee5',hs=11)
 box(ax,.012,.225,.265,.225,'WASTEWATER TREATMENT',f'Recovered concentrates only\nN {N["n"]["wastewater_recovered_kt"]:.1f} kt  ·  P {N["p"]["wastewater_recovered_kt"]:.1f} kt\nK {N["k"]["wastewater_recovered_kt"]:.1f} kt\nNo untreated field application',fc='#eff8fc',hs=11)
 box(ax,.735,.22,.25,.24,'RESTORED FIELD INPUTS',f'Return recovered N / P / K\n+ external N {N["n"]["imported_kt"]:.0f} kt, P {N["p"]["imported_kt"]:.1f} kt\n+ external K {N["k"]["imported_kt"]:.1f} kt\nSite-specific soil checks required',fc='#f2f6e9',hs=11)
 box(ax,.355,.005,.275,.15,'METHANE PYROLYSIS CARBON',f'{S["methane_carbon_return_mt"]:.2f} Mt C applied → {S["methane_carbon_stable_mt"]:.2f} Mt\nassumed stable C; agronomy unproven',fc='#f6f0f1',hs=11,bs=8.5)
 arr(ax,(.282,.75),(.35,.75),COL['tan'])
 arr(ax,(.646,.75),(.718,.75),COL['green'])
 arr(ax,(.46,.62),(.465,.47),COL['tan'])
 arr(ax,(.37,.6),(.2,.47),COL['blue'])
 arr(ax,(.645,.32),(.719,.32),COL['green'])
 ax.plot([.245,.245,.70],[.23,.19,.19],color=COL['blue'],lw=2.0)
 arr(ax,(.70,.19),(.725,.225),COL['blue'])
 arr(ax,(.65,.082),(.81,.2),COL['red'])
 fig.text(.045,.064,f'Soil stable-carbon target {S["stable_soil_c_required_mt"]:.2f} Mt C/yr = {S["hydrochar_stable_c_mt"]:.2f} hydrochar-C + {S["methane_carbon_stable_mt"]:.2f} methane-C under assumed stability factors.',fontsize=11,color=COL['navy'],weight='bold')
 fig.text(.045,.032,'Field residue retention, erosion, SOC dynamics, pyrocarbon safety and wastewater treatment require site-specific testing; these balances do not establish restoration.',fontsize=9,color=COL['gray'])
 save(fig,'ScienceFigS18_Crop_HTL_Soil_Cycle')

def npk():
 fig,(a,b)=plt.subplots(1,2,figsize=(15.5,6.6),gridspec_kw={'width_ratios':[1.6,1]},layout='constrained')
 els=['n','p','k'];lab=['Nitrogen (N)','Phosphorus (P)','Potassium (K)'];y=np.arange(3)
 hydro=np.array([N[k]['hydrochar_recovered_kt'] for k in els]);wet=np.array([N[k]['wastewater_recovered_kt'] for k in els]);imp=np.array([N[k]['imported_kt'] for k in els]);tot=hydro+wet+imp
 for z,col,offset,label in [(hydro,COL['tan'],np.zeros(3),'From hydrochar'),(wet,COL['blue'],hydro,'From treated water'),(imp,COL['red'],hydro+wet,'External replacements')]:
  a.barh(y,z,left=offset,color=col,label=label,height=.57,edgecolor='white');
  for yy,v,x in zip(y,z,offset):
   if v>42:a.text(x+v/2,yy,f'{v:,.0f}',va='center',ha='center',fontsize=10,color='white',weight='bold')
 for yy,v in zip(y,tot):a.text(v+25,yy,f'{v:,.0f} kt removed/returned',va='center',fontsize=9.4,color=COL['navy'])
 a.set_yticks(y,lab);a.invert_yaxis();a.set_xlim(0,max(tot)*1.34);a.set_xlabel('Elemental nutrient mass, thousand tonnes/year (kt)');a.set_title('A  Full N/P/K accounting, 166 Mt dry crop residues',loc='left',weight='bold');a.legend(loc='lower right',fontsize=10);a.grid(axis='x',alpha=.18);a.set_axisbelow(True)
 names=['N','P','K'];den=tot;perc=100*imp/den
 b.bar(names,perc,color=[COL['red'],COL['tan'],COL['yellow']],width=.58)
 for i,(v,t) in enumerate(zip(perc,imp)):b.text(i,v+1,f'{v:.0f}%\n{t:,.1f} kt',ha='center',va='bottom',color=COL['navy'],fontsize=11,weight='bold')
 b.set_ylim(0,65);b.set_ylabel('Share requiring external replacement (%)');b.set_title('B  Fraction not recovered internally',loc='left',weight='bold');b.grid(axis='y',alpha=.16);b.set_axisbelow(True)
 fig.suptitle('V9.1 | Explicit elemental nutrient closure: recovery alone does NOT close the cycle',fontsize=17,weight='bold',color=COL['navy'])
 fig.text(.50,.006,'Assumed recovery: N 50%, P 75%, K 80%. Treated nutrient concentrate only; illustrative external KCl equivalence: 569.7 kt/year.',ha='center',fontsize=10,color=COL['gray'])
 save(fig,'ScienceFigS19_Crop_NPK_Balance')

def costs():
 fig,(a,b)=plt.subplots(1,2,figsize=(15.5,6.2),gridspec_kw={'width_ratios':[1.05,1.05]},layout='constrained')
 opts=[('No crop residues', 'paired_without_crop'),('166 Mt crop input','paired_crop_full_sustainable_cap_forced'),('50% of recovery','paired_crop_full_low_nutrient_recovery'),('Zero nutrient recovery','paired_crop_full_zero_nutrient_recovery'),('No pyrocarbon to soil','paired_crop_full_cover_crops_only'),('Very high collection cost','paired_crop_full_very_high_collection_cost')]
 yl=np.arange(len(opts));v=[float(rows[k]['transport_cost_bn']) for _,k in opts]
 a.barh(yl,v,color=[COL['gray'],COL['green'],COL['blue'],COL['tan'],COL['violet'],COL['red']],height=.62)
 for y,val in zip(yl,v):a.text(val+1.1,y,f'${val:,.1f} bn',va='center',fontsize=11,color=COL['navy'])
 a.set_yticks(yl,[x for x,_ in opts]);a.invert_yaxis();a.set_xlim(490,max(v)+70);a.set_xlabel('Annual system cost (2026 US$ bn)');a.set_title('A  Consistent resource-pool comparison',loc='left',weight='bold');a.grid(axis='x',alpha=.15);a.set_axisbelow(True)
 x=['Recovered\nhydrochar C','Methane-derived\nstable C','Total target\nstable C'];y=[S['hydrochar_stable_c_mt'],S['methane_carbon_stable_mt'],S['stable_soil_c_required_mt']]
 b.bar(x,y,color=[COL['tan'],COL['red'],COL['green']],width=.6)
 for j,k in enumerate(y):b.text(j,k+.18,f'{k:.2f} Mt',ha='center',fontsize=12,weight='bold',color=COL['navy'])
 b.set_ylim(0,12.0);b.set_ylabel('Assumed stable elemental soil carbon, Mt C/yr');b.set_title('B  Carbon service assumed (not field validation)',loc='left',weight='bold');b.grid(axis='y',alpha=.15);b.set_axisbelow(True)
 fig.suptitle('V9.1 | Residue-HTL economics and soil-carbon assumptions',fontsize=17,color=COL['navy'],weight='bold')
 fig.text(.50,.006,'Paired crop benefit is scenario-specific; recompute cost from results: is vs revised no-crop supply pools, NOT vs the $526.9bn original-tier transport-only case.',ha='center',fontsize=10,color=COL['gray'])
 save(fig,'ScienceFigS20_Crop_Economics_Carbon')

def geomap():
 fig=plt.figure(figsize=(15.8,8.4));a=fig.add_axes([.03,.18,.72,.7]);
 a.add_patch(Polygon(B.CONUS,fc='#f6f4ea',ec='#83969f',lw=1.2))
 for ls in B.STATE_LINES:
  xy=np.array(ls);a.plot(xy[:,0],xy[:,1],color='#cad2d4',lw=.45)
 for k,col in [('corn_ethanol','#d5b277'),('residues','#c3b29a'),('hemp','#b2bc87')]:
  for coords in B.REGIONS.get(k,[]):a.add_patch(Polygon(coords,fc=col,alpha=.48,ec='none'))
 source=[('Wheat straw / stover',-100,44),('Corn stover / husks',-92,41),('Rice straw / husks',-92,33)]
 for lab,x,y in source:
  a.scatter(x,y,s=260,c=COL['yellow'],edgecolors='white',linewidth=1.8,marker='s',zorder=5)
  a.text(x+1.1,y+.6,lab,fontsize=11,color=COL['navy'],weight='bold',zorder=6,bbox=dict(fc='white',alpha=.83,ec='none',pad=1.2))
  a.annotate('',xy=(-91,39),xytext=(x,y),arrowprops=dict(arrowstyle='-|>',lw=1.3,color=COL['green'],ls='--'))
 a.scatter(-91,39,marker='h',s=700,c=COL['green'],edgecolors='white',linewidths=2,zorder=7)
 a.text(-90,38.1,'Illustrative HTL network\n+ soil return',fontsize=12,ha='left',weight='bold',color=COL['green'],bbox=dict(fc='white',alpha=.92,ec='none'),zorder=8)
 a.scatter(-105.4,50.7,marker='D',s=220,c=COL['violet'],zorder=6)
 a.annotate('',xy=(-98,44),xytext=(-105.4,50.7),arrowprops=dict(arrowstyle='-|>',lw=2.2,color=COL['violet'],ls='--',connectionstyle='arc3,rad=.15'))
 a.text(-126.8,53.1,'SASKATCHEWAN (CANADA)\nillustrative potash source',fontsize=10,color=COL['violet'],weight='bold',va='top')
 a.set_xlim(-127.5,-64.5);a.set_ylim(23,54);a.set_aspect(1.15);a.set_xticks([]);a.set_yticks([])
 for sp in a.spines.values():sp.set_visible(False)
 side=fig.add_axes([.77,.20,.20,.65]);side.axis('off')
 side.text(0,1,'CROP-RESIDUE SCREEN',fontsize=14,weight='bold',color=COL['navy'],va='top')
 q=[('166 Mt/yr','National collection ceiling'),('432 TWh/yr','Modelled crop liquid fuel'),('19.9 Mt/yr','Modelled hydrochar return'),('581 kt N','Additional elemental N'),('49.8 kt P','Additional elemental P'),('299 kt K','Additional elemental K'),('570 kt KCl','Illustrative KCl-equivalent demand')]
 for i,(v,k) in enumerate(q):
  yy=.91-i*.115;side.text(0,yy,v,fontsize=14,weight='bold',color=COL['green'],va='top');side.text(0,yy-.042,k,fontsize=9.2,color=COL['gray'],va='top')
 fig.suptitle('U.S. crop-residue HTL and soil inputs · illustrative regional resource map',x=.034,y=.96,ha='left',fontsize=19,color=COL['navy'],weight='bold')
 fig.text(.035,.07,'Arrows indicate conceptual supply/return functions, NOT verified shipment corridors, agricultural removability, state quantities or processor sites.',fontsize=10,color=COL['gray'])
 fig.text(.035,.04,'Field-scale erosion/SOC and biochar efficacy data are mandatory before assigning residue collection volumes to specific farms.',fontsize=10,color=COL['red'])
 save(fig,'Map5_Crop_Residue_HTL_Soil_Return')

if __name__=='__main__':
 for fn in (cycle,npk,costs,geomap):fn();print('Created',fn.__name__)
