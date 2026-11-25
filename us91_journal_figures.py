"""Rebuild critical journal plots from V9.1 numerical CSV/JSON and reference screening physics.
Editorial charts are generated with Matplotlib, not generative illustration. TIFF 600 dpi.
"""
from pathlib import Path
import json,csv,math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
from PIL import Image
R=Path(__file__).resolve().parent
S=json.loads((R/'scenarios.json').read_text());A=json.loads((R/'us91_scientific_sensitivities.json').read_text())
C=json.loads((R/'us9_crop_residue_results.json').read_text())
P=A['petroleum_2025_bn'];COL={'navy':'#203a51','blue':'#316d96','green':'#28785a','orange':'#cc7952','gray':'#888f92','light':'#e2e6e9','dark':'#27323b','red':'#c75448'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'figure.facecolor':'white','axes.titlesize':11,'axes.titleweight':'bold','axes.labelcolor':COL['dark'],'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
def save(fig,name):
    # 600dpi actual rasterization and TIFF native 600x600 resolution tags.
    fig.savefig(R/f'{name}.tif',dpi=600,bbox_inches='tight',pad_inches=.16,format='tiff',pil_kwargs={'compression':'tiff_lzw','dpi':(600,600)})
    plt.close(fig)

def csvrows(name):return list(csv.DictReader((R/name).open()))

def offshore():
    merit=csvrows('sweep_merit.csv')
    fig,(ax,bx)=plt.subplots(1,2,figsize=(14.4,6.0),gridspec_kw={'width_ratios':[1.1,1.15]})
    fig.subplots_adjust(left=.085,right=.97,top=.83,bottom=.19,wspace=.42)
    for y,col,name in [(1,COL['blue'],'Central yields'),(2,COL['green'],'Learning yields')]:
        r=sorted((r for r in merit if int(float(r['yield_level']))==y),key=lambda r:float(r['osw_gw']))
        ax.plot([float(x['osw_gw']) for x in r],[float(x['cost_bn']) for x in r],lw=2,marker='o',markersize=3,color=col,label=name)
    ax.axhline(P,lw=1.15,ls='--',color=COL['gray']);ax.text(0.01,.94,f'Late-2025 petroleum benchmark  ${P:.1f}bn',transform=ax.transAxes,color=COL['dark'],fontsize=9,va='top',bbox=dict(facecolor='white',edgecolor='none',pad=2))
    ax.set_xlabel('Imposed offshore wind capacity (GW)');ax.set_ylabel('Modelled transport cost (US$bn/year)');ax.grid(alpha=.2);ax.legend(ncol=1,loc='upper left',bbox_to_anchor=(.018,.88),fontsize=8,frameon=False)
    ax.set_title('A  Additional offshore capacity raises total cost',loc='left',pad=12)
    m=json.loads((R/'seaweed_merit.json').read_text())
    rec=m['design'];lab=[x['region'].split('(')[0].strip() for x in rec];y=np.arange(len(rec))
    bx.barh(y,[r['best_usd_mwh'] for r in rec],color=COL['blue'],height=.66)
    bx.set_yticks(y);bx.set_yticklabels(lab,fontsize=8);bx.invert_yaxis();bx.set_xlim(0,max(x['best_usd_mwh'] for x in rec)*1.16)
    bx.grid(axis='x',alpha=.2);bx.set_axisbelow(True)
    bx.set_xlabel('Indicative fuel production cost (US$/MWh)');bx.set_title('B  Seaweed-zone cost comparison',loc='left',pad=12)
    fig.suptitle('Offshore wind and seaweed: imposed deployment sensitivity',fontsize=15,color=COL['navy'],y=.98)
    fig.text(.5,.035,'The 220 GW case is a diversification sensitivity, not an endogenous optimum. Marginal land-fuel prices vary by scenario.',ha='center',fontsize=9,color=COL['gray'])
    save(fig,'ScienceFig3_offshore_sensitivity')

def costs():
    fig,(a,b)=plt.subplots(1,2,figsize=(13.9,5.8),gridspec_kw={'width_ratios':[1.18,1]})
    fig.subplots_adjust(left=.075,right=.97,top=.84,bottom=.19,wspace=.28)
    cases=[('Least cost\n0 GW',S['least_cost']['transport_cost_bn']),('220 GW\nimposed',S['design_sweet_spot']['transport_cost_bn']),('515 GW\nimposed',S['design']['transport_cost_bn']),('Historical\npetroleum',P)]
    x=np.arange(len(cases));vals=[v for _,v in cases];col=[COL['green'],COL['blue'],COL['orange'],'#aab0b3']
    a.bar(x,vals,color=col,width=.65)
    for xx,v in zip(x,vals): a.text(xx,v+7,f'${v:.1f}bn',ha='center',fontsize=9,color=COL['dark'],weight='bold')
    a.set_xticks(x);a.set_xticklabels([q[0] for q in cases]);a.set_ylim(0,max(vals)*1.2);a.set_ylabel('Transport expenditure (US$bn/year)');a.grid(axis='y',alpha=.18);a.set_axisbelow(True)
    a.set_title('A  Exact net cost, including all modelled credits',loc='left',pad=16)
    # No stacked components: avoids misleading sum-to-total with negative credits.
    for key,col,name in [('least_cost',COL['green'],'Least cost'),('sweet_spot',COL['blue'],'220 GW'),('design',COL['orange'],'515 GW')]:
        z=csvrows(f'us91_paired_savings_{key}.csv');v=[float(q['paired_saving_pct']) for q in z]
        b.hist(v,bins=np.linspace(-45,55,53),histtype='step',linewidth=2,color=col,label=f'{name}: median {np.median(v):+.1f}%')
    b.axvline(0,color=COL['dark'],lw=1,ls='--');b.set_xlabel('Paired saving vs sampled-demand petroleum reference (%)');b.set_ylabel('Draw count');b.set_title('B  Conditional savings in 1,000 draws',loc='left',pad=16)
    b.legend(fontsize=8,frameon=False,loc='upper left');b.grid(axis='y',alpha=.2)
    fig.suptitle('2050 transport cost and conditional uncertainty',fontsize=15,color=COL['navy'],y=.98)
    fig.text(.5,.035,'Historical petroleum prices held fixed; demand growth is sampled. Oil prices and 2050 combustion technology are not sampled.',ha='center',fontsize=9,color=COL['gray'])
    save(fig,'ScienceFig4_cost_and_paired_uncertainty')

def harvester_schematic():
    fig,ax=plt.subplots(figsize=(13.5,6.2));fig.subplots_adjust(left=.03,right=.97,bottom=.10,top=.89)
    ax.set_xlim(0,100);ax.set_ylim(0,60);ax.axis('off')
    def box(x,y,w,h,title,body,col):
        ax.add_patch(Rectangle((x,y),w,h,facecolor='#f9fafb',edgecolor=col,lw=1.6))
        ax.text(x+2,y+h-5,title,weight='bold',color=col,fontsize=12,va='center')
        ax.text(x+2,y+h-11,body,fontsize=10,color=COL['dark'],linespacing=1.6,va='top')
    box(2,24,24,24,'Cultivation rows','Kelp growing on lines\nOne or multiple partial passes\nper growing season',COL['green'])
    box(38,24,26,24,'Grid Harvester','Buoyancy-controlled cutting head\nElectric drive + pumping\nSlurry hose, with optional fairing',COL['blue'])
    box(76,24,22,24,'Transfer vessel','Battery / sail assisted\nreceives seaweed slurry\nfor port-side handling',COL['orange'])
    for x1,x2 in [(26,38),(64,76)]:ax.add_patch(FancyArrowPatch((x1,36),(x2,36),arrowstyle='-|>',mutation_scale=15,linewidth=1.8,color=COL['gray']))
    ax.add_patch(FancyArrowPatch((51,24),(51,12),arrowstyle='-|>',mutation_scale=15,linewidth=1.8,color=COL['gray']))
    ax.text(53,15,'Reference energy per 1.44 ha cycle: 33.9 MJ at 10% solids, faired hose',fontsize=10,color=COL['dark'])
    ax.text(2,5,'Conceptual engineering configuration; not a surveyed sea trial, validated crop yield, or verified vessel manufacturing design.',fontsize=10,color=COL['gray'])
    fig.suptitle('Grid Harvester — conceptual harvesting and transfer pathway',color=COL['navy'],fontsize=16,weight='bold')
    save(fig,'ScienceFigS21_GridHarvester_Technical_Schematic')

def harvester_energy():
    d=csvrows('us91_grid_harvester_efficiency.csv')
    fig,(a,b)=plt.subplots(1,2,figsize=(13.9,5.7));fig.subplots_adjust(left=.08,right=.97,top=.81,bottom=.30,wspace=.3)
    labs=['Conventional','Grid / bare hose\n10% solids','Grid / faired hose\n10% solids','Grid / faired hose\n20% solids','Grid / faired hose\n30% solids']
    vals=[float(x['energy_mj_per_1_44ha_cycle']) for x in d];savepct=[float(x['modelled_energy_reduction_pct']) for x in d]
    colors=[COL['gray'],COL['blue'],COL['green'],COL['green'],COL['green']]
    x=np.arange(5)
    a.bar(x,vals,color=colors,width=.65);b.bar(x[1:],savepct[1:],color=colors[1:],width=.65)
    for xx,v in enumerate(vals):a.text(xx,v+2,f'{v:.1f}',ha='center',fontsize=10)
    for xx,v in zip(x[1:],savepct[1:]):b.text(xx,v+2,f'{v:.1f}%',ha='center',fontsize=10)
    for ax in [a,b]:ax.set_xticks(x);ax.set_xticklabels(labs,fontsize=8);ax.tick_params(axis='x',labelrotation=0);ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
    a.set_ylim(0,108);b.set_ylim(0,98)
    a.set_ylabel('Energy (MJ per 1.44 ha cycle)');b.set_ylabel('Reduced harvest-cycle energy vs conventional (%)')
    a.set_title('A  Engineering-screen energy balance',pad=15,loc='left');b.set_title('B  Relative energy saving',pad=15,loc='left')
    fig.suptitle('Grid Harvester: modelled harvesting-energy advantage',fontsize=16,color=COL['navy'],y=.98)
    fig.text(.5,.06,'Assumptions calibrated to a reference engineering design; energy does not measure downstream HTL yield or whole-system conversion efficiency.',fontsize=9,ha='center',color=COL['gray'])
    save(fig,'ScienceFigS22_GridHarvester_Energy_Efficiency')

def bev_comparator():
    v=csvrows('us91_bev_premium.csv');q=csvrows('us91_2050_reference_sensitivity.csv');be=A['bev_premium_break_even_usd_per_car_year']
    fig,(a,b)=plt.subplots(1,2,figsize=(13.4,5.4));fig.subplots_adjust(left=.08,right=.97,top=.83,bottom=.22,wspace=.29)
    a.plot([float(r['bev_net_premium_usd_per_car_year']) for r in v],[float(r['system_cost_bn']) for r in v],color=COL['blue'],marker='o')
    a.axhline(P,color=COL['gray'],ls='--');a.axvline(be,color=COL['orange'],ls=':');a.text(.05,.92,f'Break-even premium ≈ ${be:.0f}/car/year',transform=a.transAxes,fontsize=9,va='top')
    a.set_xlabel('Net BEV ownership premium (US$/vehicle/year)');a.set_ylabel('National transport cost (US$bn/year)');a.grid(alpha=.20);a.set_title('A  BEV ownership-cost sensitivity',loc='left',pad=15)
    b.plot([float(r['gasoline_fuel_efficiency_improvement_pct']) for r in q],[float(r['petroleum_comparator_bn']) for r in q],color=COL['orange'],marker='o',label='Fuel-only petroleum benchmark')
    b.axhline(S['least_cost']['transport_cost_bn'],color=COL['green'],ls='--',label='Modelled transport cost')
    b.set_xlabel('2050 gasoline efficiency improvement vs input fleet (%)');b.set_ylabel('Reference cost (US$bn/year)');b.grid(alpha=.20);b.legend(frameon=False,fontsize=9,loc='best');b.set_title('B  Illustrative combustion-fleet efficiency',loc='left',pad=15)
    fig.suptitle('Break-even assumptions: vehicles and petroleum reference',fontsize=15,color=COL['navy'],y=.98)
    fig.text(.5,.045,'Petroleum prices fixed at late-2025 values; fleet-efficiency sensitivity excludes changes in ICE purchase, maintenance and fuel mix.',ha='center',fontsize=8.7,color=COL['gray'])
    save(fig,'ScienceFigS23_Reference_and_BEV_Breakeven')

def crop():
    base=C['paired_without_crop']['transport_cost_bn'];cap=C['paired_crop_full_sustainable_cap_forced'];full=cap['transport_cost_bn'];xkeys=['paired_without_crop','paired_crop_economic_optimum','paired_crop_full_sustainable_cap_forced','paired_crop_full_high_collection_cost']
    fig,(a,b)=plt.subplots(1,2,figsize=(13.4,5.5));fig.subplots_adjust(left=.08,right=.97,top=.83,bottom=.24,wspace=.35)
    y=np.arange(len(xkeys));names=['No food crop\nresidues','Crop collection\ncost-optimal','Force 166 Mt/year\nfull collection','Force 166 Mt/year\nhigh collection cost']
    vals=[C[k]['transport_cost_bn'] for k in xkeys]
    a.barh(y,vals,color=[COL['gray'],COL['blue'],COL['green'],COL['orange']],height=.62);a.set_yticks(y);a.set_yticklabels(names,fontsize=9);a.invert_yaxis();a.set_xlim(0,max(vals)*1.17)
    for yi,v in enumerate(vals):a.text(v+2,yi,f'${v:.1f}bn',va='center',fontsize=9)
    a.set_xlabel('Full annual system cost (US$bn/year; zero-based)');a.set_title('A  Matched-resource comparison',loc='left',pad=12);a.grid(axis='x',alpha=.2);a.set_axisbelow(True)
    n=cap['n_import_kt'];ph=cap['p_import_kt'];k=cap['k_import_kt'];bb=[n,ph,k];lab=['Nitrogen','Phosphorus','Potassium'];bx=np.arange(3)
    b.bar(bx,bb,color=[COL['orange'],COL['blue'],COL['green']],width=.55)
    for xi,val in enumerate(bb):b.text(xi,val+10,f'{val:.1f} kt',ha='center',fontsize=10)
    b.set_xticks(bx);b.set_xticklabels(lab);b.set_ylabel('External nutrient replacement (kt element/year)');b.set_ylim(0,max(bb)*1.26);b.grid(axis='y',alpha=.2);b.set_axisbelow(True)
    b.set_title('B  Nutrients still imported at 166 Mt',loc='left',pad=12)
    fig.suptitle('Crop-residue HTL with soil-return and purchased nutrient constraints',fontsize=15,color=COL['navy'],y=.98)
    fig.text(.5,.043,f'Matched saving at forced collection: ${base-full:.2f}bn/year. Forest/non-crop resource ceiling is assumed; no agronomic certification implied.',ha='center',fontsize=9,color=COL['gray'])
    save(fig,'ScienceFigS20_Crop_Economics_Carbon')


def energy_and_liquids():
    r=S['least_cost'];eu=r['enduse'];L=r['liquids_twh']
    fig,(a,b)=plt.subplots(1,2,figsize=(14.2,5.8),gridspec_kw={'width_ratios':[1,1.15]})
    fig.subplots_adjust(left=.16,right=.98,top=.82,bottom=.22,wspace=.40)
    keys=[('Residues and grasses','residues_and_grasses'),('Corn ethanol to jet','corn_ethanol_atj'),('Bamboo','bamboo'),('Hemp','hemp'),('Oils / HEFA','oils_hefa'),('Seaweed','seaweed')]
    items=[(name,float(L.get(k,0))) for name,k in keys if float(L.get(k,0))>0.1]
    yy=np.arange(len(items));a.barh(yy,[x[1] for x in items],height=.65,color=COL['blue'])
    a.set_yticks(yy);a.set_yticklabels([x[0] for x in items],fontsize=9);a.invert_yaxis()
    a.set_xlim(0,max(x[1] for x in items)*1.28)
    for i,(name,v) in enumerate(items):a.text(v+10,i,f'{v:,.0f} TWh',va='center',fontsize=9)
    a.grid(axis='x',alpha=.18);a.set_axisbelow(True);a.set_xlabel('Liquid-fuel energy (TWh/year)');a.set_title('A  Fuel pathways, least-cost case',loc='left',pad=15)
    seg=[('Aviation','air'),('Heavy\ntrucks','hdv'),('Marine','marine'),('Farm\nmachinery','farm'),('Construction\n& mining','construction'),('Rail','rail'),('Passenger\ncars','ldv')]
    xx=np.arange(len(seg));E=eu['el'];electric={'air':0,'hdv':E['hdv_ers_wire']+E['hdv_ers_battery']+E['hdv_bev']+E['hdv_re'],'marine':E['marine'],'farm':E['farm'],'construction':E['construction'],'rail':E['rail'],'ldv':E['ldv']}
    base=[eu['base'][k] for _,k in seg];el=[electric[k] for _,k in seg];h=[eu['h2_twh'].get(k,0) for _,k in seg];li=[eu['liq'].get(k,0) for _,k in seg]
    b.bar(xx-.18,base,width=.35,color=COL['gray'],label='Reference fuel')
    b.bar(xx+.18,el,width=.35,color=COL['blue'],label='Electricity')
    b.bar(xx+.18,h,bottom=el,width=.35,color=COL['green'],label='Hydrogen')
    b.bar(xx+.18,li,bottom=np.array(el)+h,width=.35,color=COL['orange'],label='Liquid fuel')
    b.set_xticks(xx);b.set_xticklabels([x[0] for x in seg],fontsize=7.8);b.set_yscale('log');b.set_ylim(10,8000)
    b.grid(axis='y',alpha=.18);b.set_axisbelow(True);b.set_ylabel('End-use energy (TWh/year; log scale)');b.set_title('B  Energy by mode and carrier',loc='left',pad=15)
    b.legend(ncol=4,loc='upper center',bbox_to_anchor=(.5,1.16),frameon=False,fontsize=8)
    fig.suptitle('Transport energy and fuel pathways in the least-cost configuration',fontsize=15,color=COL['navy'],y=.98)
    save(fig,'ScienceFig1_energy_and_liquids')

def reactor_costs():
    import us2_inputs as I
    from us2_model import reactor_cost
    fig,(a,b)=plt.subplots(1,2,figsize=(13.7,5.6),gridspec_kw={'width_ratios':[1.1,.8]})
    fig.subplots_adjust(left=.08,right=.97,top=.80,bottom=.20,wspace=.35)
    n=np.logspace(0,3,200)
    for name,col in [('low',COL['green']),('central',COL['blue']),('high',COL['orange'])]:
        inp=I.REACTOR_COST[name];foak=inp['boak_kwe']*inp['foak_mult'];slope=math.log2(1-inp['learning'])
        a.plot(n,foak*n**slope,label=f'{name.title()}: FOAK ${foak:,.0f}/kWe',lw=2,color=col)
    a.set_xscale('log');a.set_xlabel('Cumulative modules built (log scale)');a.set_ylabel('Overnight reactor cost (US$/kWe)');a.grid(alpha=.20)
    a.legend(loc='upper center',bbox_to_anchor=(.5,1.20),ncol=2,fontsize=8,frameon=False)
    a.set_title('A  Conditional reactor learning',loc='left',pad=14)
    fleet=int(round(S['design']['reactors']))
    vals=[reactor_cost(name,fleet)['fleet_avg_kwe_with_idc'] for name in ['low','central','high']]
    b.bar(np.arange(3),vals,color=[COL['green'],COL['blue'],COL['orange']],width=.58)
    for i,v in enumerate(vals):b.text(i,v+300,f'${v:,.0f}',ha='center',fontsize=10)
    b.set_xticks(range(3));b.set_xticklabels(['Low','Central','High']);b.set_ylim(0,max(vals)*1.24)
    b.set_ylabel('Fleet average incl. construction finance (US$/kWe)');b.grid(axis='y',alpha=.2);b.set_axisbelow(True)
    b.set_title(f'B  Imposed 515 GW case ({fleet} modules)',loc='left',pad=14)
    fig.suptitle('Reactor costs are prospective assumptions, not delivered quotations',fontsize=15,color=COL['navy'],y=.98)
    save(fig,'Fig03_reactor_costs')

def npk():
    r=C['paired_crop_full_sustainable_cap_forced'];src=C['paired_crop_full_sustainable_cap_forced']['soil']['nutrients'] if 'soil' in C['paired_crop_full_sustainable_cap_forced'] else None
    fig,(a,b)=plt.subplots(1,2,figsize=(12.5,5.6));fig.subplots_adjust(left=.12,right=.97,top=.79,bottom=.27,wspace=.33)
    el=['Nitrogen','Phosphorus','Potassium'];keys=['n','p','k'];rem=[1162,199.2,1494.0];imp=[r[f'{k}_import_kt'] for k in keys];rec=[v-w for v,w in zip(rem,imp)]
    y=np.arange(3);a.barh(y,rec,color=COL['green'],height=.58,label='Modelled return')
    a.barh(y,imp,left=rec,color=COL['orange'],height=.58,label='External replacement')
    a.set_yticks(y);a.set_yticklabels(el);a.invert_yaxis();a.set_xlim(0,max(rem)*1.24)
    for j,(tot,ex) in enumerate(zip(rem,imp)):a.text(tot+16,j,f'{tot:.0f} kt total  ·  {ex:.1f} kt external',va='center',fontsize=8)
    a.set_xlabel('Elemental N, P or K (kt/year)');a.legend(ncol=2,frameon=False,loc='upper center',bbox_to_anchor=(.5,-.19),fontsize=8);a.grid(axis='x',alpha=.18);a.set_axisbelow(True);a.set_title('A  Elemental annual nutrient mass',loc='left',pad=14)
    frac=[100*e/t for e,t in zip(imp,rem)];b.bar(range(3),frac,color=COL['orange'],width=.60)
    for i,v in enumerate(frac):b.text(i,v+1,f'{v:.0f}% external',ha='center',fontsize=10)
    b.set_xticks(range(3));b.set_xticklabels(el);b.set_ylim(0,65);b.set_ylabel('External replacement share (%)');b.grid(axis='y',alpha=.18);b.set_axisbelow(True);b.set_title('B  Fertilizer not recovered internally',loc='left',pad=14)
    fig.suptitle('Crop-residue HTL: recovery does not fully replace N, P and K',fontsize=15,color=COL['navy'],y=.98)
    fig.text(.5,.04,'166 Mt/year crop collection; recoveries and wastewater-concentrate use are assumptions, not field-measured returns.',ha='center',fontsize=9,color=COL['gray'])
    save(fig,'ScienceFigS19_Crop_NPK_Balance')
if __name__=='__main__':
    for fn in (energy_and_liquids,reactor_costs,npk,offshore,costs,harvester_schematic,harvester_energy,bev_comparator,crop):
        fn();print('Created',fn.__name__,flush=True)
