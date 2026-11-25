"""V9.2 model-grounded visual + abatement sensitivity; schematic maps not siting studies.
Figures are directly plotted from archived v9.1 values, never image-predicted quantities.
"""
from pathlib import Path
import os,csv,json,math
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyArrowPatch, Rectangle, Circle
from matplotlib.lines import Line2D
import us2_basemap as B
import us2_figures as F
from PIL import Image
R=Path(__file__).resolve().parent
S=json.loads((R/'scenarios.json').read_text()); LC=S['least_cost']; P=592.77029536
NAV='#253e50';BLUE='#416c8a';GREEN='#36795f';ORANGE='#be7850';GRAY='#969d9e';RED='#a64e49';MUTE='#67727a';BG='#ffffff'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9.7,'axes.titlesize':10,'axes.labelsize':9.4,'xtick.labelsize':8.3,'ytick.labelsize':8.8,'figure.facecolor':'white','axes.spines.top':False,'axes.spines.right':False})

def save(fig,name):
    fig.savefig(R/(name+'.tif'),format='tiff',dpi=600,bbox_inches='tight',pad_inches=.08,pil_kwargs={'compression':'tiff_lzw','dpi':(600,600)})
    plt.close(fig)

def figure1():
    e=LC['enduse']; seg=[('Passenger cars','ldv'),('Heavy trucks','hdv'),('Aviation','air'),('Marine','marine'),('Rail','rail'),('Farm machines','farm'),('Construction','construction'),('Industrial vehicles','industrial')]
    el=e['el']; elmap={'ldv':el['ldv'],'hdv':sum(el.get(k,0) for k in ['hdv_ers_wire','hdv_ers_battery','hdv_bev','hdv_re']),'air':0,'marine':el['marine'],'rail':el['rail'],'farm':el['farm'],'construction':el['construction'],'industrial':el['industrial']}
    hmap={'ldv':e['h2_twh']['ldv'],'hdv':e['h2_twh']['hdv'],'air':e['h2_twh']['air'],'marine':e['h2_twh']['marine'],'rail':0,'farm':0,'construction':0,'industrial':e['h2_twh']['industrial']}
    lmap={'ldv':e['liq']['ldv'],'hdv':e['liq']['hdv'],'air':e['liq']['air'],'marine':e['liq']['marine'],'rail':e['liq']['rail'],'farm':e['liq']['farm'],'construction':e['liq']['construction'],'industrial':0}
    labels=[x[0] for x in seg];k=[x[1] for x in seg];orig=np.array([e['base'][x] for x in k]);E=np.array([elmap[x] for x in k]);H=np.array([hmap[x] for x in k]);L=np.array([lmap[x] for x in k]);new=E+H+L
    y=np.arange(len(k));fig,(a,b)=plt.subplots(1,2,figsize=(7.05,5.75),gridspec_kw={'width_ratios':[1.1,1]});fig.subplots_adjust(left=.195,right=.99,bottom=.10,top=.91,wspace=.33)
    a.barh(y-.16,orig,height=.28,color='#aeb4b9',label='Reference energy')
    a.barh(y+.16,new,height=.28,color=BLUE,label='Petroleum-free')
    a.invert_yaxis();a.set_yticks(y);a.set_yticklabels(labels,fontsize=8);a.set_xlim(0,5300);a.set_xlabel('End-use TWh/year');a.set_title('A  Total energy, by mode',loc='left');a.grid(axis='x',alpha=.16);a.set_axisbelow(True)
    a.legend(fontsize=7,frameon=False,loc='lower right')
    # Carrier mix is a true linear percentage stack, avoiding invalid stacked-log display.
    tot=np.maximum(new,1e-6); p1=100*E/tot;p2=100*H/tot;p3=100*L/tot
    b.barh(y,p1,height=.58,color=BLUE,label='Electricity');b.barh(y,p2,left=p1,height=.58,color=GREEN,label='Hydrogen');b.barh(y,p3,left=p1+p2,height=.58,color=ORANGE,label='Liquid fuel')
    b.invert_yaxis();b.set_yticks(y);b.set_yticklabels([]);b.set_xlim(0,100);b.set_xlabel('Carrier share of modelled energy (%)');b.set_title('B  2050 carrier composition',loc='left');b.grid(axis='x',alpha=.16);b.set_axisbelow(True)
    b.legend(fontsize=7.5,frameon=False,ncol=1,loc='lower right',bbox_to_anchor=(1.0,1.01))
    save(fig,'ScienceFig1_energy_and_liquids')

def figure2():
    fig=plt.figure(figsize=(7.05,4.75));ax=fig.add_axes([.05,.24,.90,.72]);ax.set_facecolor('#f5f8f9')
    ax.add_patch(Polygon(B.CONUS,closed=True,facecolor='#f7f3ed',edgecolor='#506977',linewidth=.8,zorder=0))
    # Only zero-offshore case; onshore and solar are model output, regional polygons are qualitative resource screens.
    for key,c in [('onshore_wind','#d9e9dc'),('solar','#f2e4c9')]:
        for verts in B.REGIONS.get(key,[]):ax.add_patch(Polygon(verts,closed=True,facecolor=c,edgecolor='none',alpha=.8,zorder=1))
    for vv in B.STATE_LINES:
        v=np.asarray(vv);ax.plot(v[:,0],v[:,1],color='#bdc6c7',lw=.28,zorder=2)
    for cities in B.CORRIDORS.values():
        xy=np.asarray([B.CITIES[c] for c in cities]);ax.plot(xy[:,0],xy[:,1],color=BLUE,lw=1.0,zorder=3,alpha=.8)
    hubs=F.allocate_hubs(LC['hubs']);assert abs(sum(hubs)-round(LC['hubs']))<1
    for (name,x,y,w,role),n in zip(B.HUB_SITES,hubs):
        if int(n)>0:ax.plot(x,y,'o',ms=3.5,color=RED,zorder=5,markeredgecolor='white',markeredgewidth=.3)
    for title,coords in [('PACIFIC',(-119,39)),('PLAINS',(-101,44)),('SOUTHEAST',(-86,33))]:ax.text(*coords,title,color='#70877a',fontsize=6.5,alpha=.65,weight='bold')
    ax.set_xlim(-128.8,-66.5);ax.set_ylim(24,50.5);ax.set_xticks([]);ax.set_yticks([])
    for s in ax.spines.values():s.set_visible(False)
    fig.text(.055,.16,'203 four-module hub equivalents   |   228 GW onshore wind   |   341 GW utility solar',fontsize=9.3,color=NAV,weight='bold')
    legend=[Line2D([0],[0],color=BLUE,lw=2,label='Electric road corridors'),Line2D([0],[0],marker='o',color='white',markerfacecolor=RED,markersize=6,label='Illustrative reactor-hub locations'),Rectangle((0,0),1,1,facecolor='#d9e9dc',label='Wind resource areas'),Rectangle((0,0),1,1,facecolor='#f2e4c9',label='Solar resource areas')]
    fig.legend(handles=legend,ncol=2,loc='lower left',bbox_to_anchor=(.047,.02),fontsize=7.8,frameon=False,columnspacing=1.7,handlelength=2)
    save(fig,'ScienceFig2_national_system')

def figure3():
    # readable at Science 7.2in print width; no point labels inside curves
    merit=list(csv.DictReader((R/'sweep_merit.csv').open()));fig,(a,b)=plt.subplots(2,1,figsize=(7.05,7.25),gridspec_kw={'height_ratios':[1,1.7]});fig.subplots_adjust(left=.31,right=.97,bottom=.08,top=.96,hspace=.48)
    for lev,c,lab in [(1,BLUE,'Central conversion yields'),(2,GREEN,'Learning sensitivity')]:
        v=sorted([r for r in merit if int(float(r['yield_level']))==lev],key=lambda r:float(r['osw_gw']))
        a.plot([float(q['osw_gw']) for q in v],[float(q['cost_bn']) for q in v],color=c,marker='.',lw=1.7,label=lab)
    a.axhline(P,color=GRAY,ls='--',lw=1);a.text(.985,.95,'Historical-price petroleum comparator',transform=a.transAxes,ha='right',va='top',fontsize=7.8,color=MUTE,bbox={'facecolor':'white','edgecolor':'none','pad':3})
    a.set_ylabel('Annual transport cost (US$bn)');a.set_xlabel('Imposed offshore capacity (GW)');a.grid(alpha=.17);a.legend(frameon=False,fontsize=8,loc='upper left',bbox_to_anchor=(0,1.0));a.set_title('A  Cost rises as offshore zones are added',loc='left',pad=9)
    m=json.loads((R/'seaweed_merit.json').read_text())['design'];k=np.arange(len(m));labs=[q['region'].split('(')[0].strip() for q in m];v=[q['best_usd_mwh'] for q in m]
    b.barh(k,v,height=.62,color=BLUE);b.invert_yaxis();b.set_yticks(k);b.set_yticklabels(labs,fontsize=7.3);b.set_xlabel('Lowest-cost modeled route (US$/MWh fuel)');b.set_xlim(0,360);b.grid(axis='x',alpha=.15);b.set_axisbelow(True);b.set_title('B  Offshore seaweed fuel-production costs',loc='left',pad=9)
    save(fig,'ScienceFig3_offshore_sensitivity')

def figure4():
    fig,(a,b)=plt.subplots(1,2,figsize=(7.05,4.40),gridspec_kw={'width_ratios':[.95,1.05]});fig.subplots_adjust(left=.115,right=.99,bottom=.32,top=.88,wspace=.40)
    cases=['Least-cost','220 GW imposed','515 GW imposed','Petroleum price\nsnapshot'];val=[LC['transport_cost_bn'],S['design_sweet_spot']['transport_cost_bn'],S['design']['transport_cost_bn'],P]
    xx=np.arange(4);a.bar(xx,val,color=[GREEN,BLUE,ORANGE,GRAY],width=.68);a.set_ylim(0,735);a.set_xticks(xx);a.set_xticklabels(['Least\ncost','220 GW','515 GW','Fuel-only\nreference'],fontsize=7.4)
    for i,v in enumerate(val):a.text(i,v+10,f'{v:.0f}',ha='center',fontsize=8,weight='bold')
    a.set_ylabel('Annual cost (US$bn)');a.set_title('A  Annual cost, historical-price benchmark',loc='left',pad=9);a.grid(axis='y',alpha=.15);a.set_axisbelow(True)
    for key,c,lab in [('least_cost',GREEN,'Least cost'),('sweet_spot',BLUE,'220 GW'),('design',ORANGE,'515 GW')]:
        rows=list(csv.DictReader((R/f'us91_paired_savings_{key}.csv').open()));v=np.asarray([float(q['paired_saving_pct']) for q in rows]);b.hist(v,bins=np.linspace(-45,55,30),histtype='step',lw=1.35,color=c,label=f'{lab}: {np.median(v):+.1f}% median')
    b.axvline(0,color=GRAY,ls='--',lw=1);b.set_xlim(-44,55);b.set_xlabel('Paired saving (%)');b.set_ylabel('Draws');b.grid(axis='y',alpha=.14);b.set_title('B  Conditional cost sensitivity',loc='left',pad=9);b.legend(frameon=False,fontsize=7.3,loc='upper center',bbox_to_anchor=(.5,-.27),ncol=1)
    save(fig,'ScienceFig4_cost_and_paired_uncertainty')

def figureS1():
    # Actual side and plan views; conceptual dimensional geometry, not fabricated performance traces.
    fig,(a,b)=plt.subplots(2,1,figsize=(7.05,6.0));fig.subplots_adjust(left=.055,right=.965,bottom=.08,top=.95,hspace=.36)
    for ax in (a,b):ax.set_xlim(0,100);ax.set_ylim(0,35);ax.set_aspect('equal');ax.axis('off')
    # side view water, vessel, hose, winch, cutting head, kelp vertical ropes
    a.fill_between([0,100],[15,15],[0,0],color='#e6f1f4');a.plot([0,100],[15,15],lw=1,color=BLUE)
    a.add_patch(Polygon([(69,18),(92,18),(87,14),(72,14)],color='#a8b4ba',ec=NAV));a.add_patch(Rectangle((75,18),9,5,facecolor='#e5e7e7',edgecolor=NAV,lw=.8))
    a.plot([60,73],[7,15],color=ORANGE,lw=2.8);a.add_patch(Rectangle((54,5),9,5,facecolor=GREEN,edgecolor=NAV,lw=.7))
    for x in [18,26,34,42]:
        a.plot([x,x],[14,4],color='#668d67',lw=1.8);a.plot([x-2,x,x+2],[8,3.5,8],color=GREEN,lw=1.8)
    a.add_patch(FancyArrowPatch((44,8),(54,8),arrowstyle='-|>',mutation_scale=10,color=ORANGE,lw=1.6))
    for txt,xy,target in [('Floating vessel',(72,30),(81,19)),('Slurry transfer hose',(43,26),(64,10)),('Cutting head',(44,1),(57,6)),('Kelp lines',(6,27),(26,9))]:a.annotate(txt,xy=target,xytext=xy,fontsize=8,arrowprops={'arrowstyle':'-','color':MUTE,'lw':.7},color=NAV)
    a.set_title('A  Side elevation (schematic)',loc='left',fontsize=10)
    # plan view rows, shuttle, hoses and vessel
    b.add_patch(Rectangle((7,6),48,22,facecolor='#eaf2ed',edgecolor='#8f9c96',lw=.8))
    for y in [9,13,17,21,25]:b.plot([10,52],[y,y],color=GREEN,lw=1.2)
    b.add_patch(Rectangle((47,8),8,18,facecolor='#c7d6d4',edgecolor=NAV,lw=.9));b.add_patch(Rectangle((76,13),18,8,facecolor='#d0d6db',edgecolor=NAV,lw=.9))
    b.plot([55,76],[17,17],color=ORANGE,lw=2);b.add_patch(FancyArrowPatch((32,3),(46,3),arrowstyle='-|>',mutation_scale=10,color=BLUE,lw=1))
    for txt,xy,target in [('Harvesting passes',(10,31),(25,25)),('Mobile cutting frame',(42,31),(49,22)),('Flexible hose',(56,5),(63,17)),('Vessel',(79,31),(85,20))]:b.annotate(txt,xy=target,xytext=xy,fontsize=8,arrowprops={'arrowstyle':'-','color':MUTE,'lw':.7},color=NAV)
    b.set_title('B  Plan view (schematic)',loc='left',fontsize=10)
    fig.text(.5,.012,'Concept sketch only; no field testing, certified power or scale-recovery performance is asserted.',ha='center',fontsize=8,color=MUTE)
    save(fig,'ScienceFigS1_grid_harvester')

def abatement_data():
    alt=LC['transport_cost_bn'];base=2873.;res=LC['emissions']['total_mt']; gas_tons=8.9e6*42*365*8.887/1e9 # million tonnes (8.887 kg/gal)
    rows=[]
    with (R/'us91_2050_reference_sensitivity.csv').open() as fh: rd=list(csv.DictReader(fh))
    for z in rd:
        pct=float(z['gasoline_fuel_efficiency_improvement_pct']);rc=float(z['petroleum_comparator_bn']); abate_fixed=base-res; emref=base-gas_tons*pct/100;abate_adj=emref-res
        rows.append({'gasoline_cut_pct':pct,'fuel_only_reference_bn':round(rc,3),'alternative_bn':round(alt,3),
           'reference_emissions_mt_adjusted_tailpipe_only':round(emref,3),'avoided_mt_fixed_denominator':round(abate_fixed,3),
           'abatement_usd_t_fixed_denominator':round((alt-rc)*1000/abate_fixed,2),
           'abatement_usd_t_adjusted_tailpipe':round((alt-rc)*1000/abate_adj,2),
           'full_2050_fleet_costs_included':False})
    with (R/'us92_abatement_sensitivity.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    (R/'us92_reference_framework.json').write_text(json.dumps({'EIA_AEO_2026_official_tables':'Tables 7, 12, 35-37, 39-45, 47-49, 51-52; use Counterfactual Baseline, 2050','status':'Official series source identified; 2050 table values not retrieved in this environment; no fully matched ownership-cost reference is claimed','AEO_narrative_verified':'2050 EV stock ~40%-46% in most cases with 2027+ policies; reference differs fundamentally from fixed historical-efficiency petroleum use','EPA_tailpipe_factor_kg_co2_per_gallon':8.887,'gasoline_tailpipe_2050_screen_mt':gas_tons,'cost_boundary':'2026 USD, transport only, zero building hydrogen blend','alternative_cost_bn':alt,'alternative_wtw_emissions_mt':res,'model_reference_2025_wtw_mt':base,'fuel_only_sensitivity_not_full_AEO':rows},indent=2))
    return rows

def figS23(rows):
    fig,(a,b)=plt.subplots(2,1,figsize=(7.05,6.0),gridspec_kw={'height_ratios':[1,1.2]});fig.subplots_adjust(left=.13,right=.95,top=.94,bottom=.13,hspace=.43)
    # Prior BEV curve is a re-optimised model set, not fuel-only.
    br=list(csv.DictReader((R/'us91_bev_premium.csv').open()));p=[float(z['bev_net_premium_usd_per_car_year']) for z in br];c=[float(z['system_cost_bn']) for z in br]
    a.plot(p,c,color=BLUE,marker='o',lw=1.6);a.axhline(P,color=GRAY,ls='--');a.axvline(343.4,color=ORANGE,ls=':',lw=1);a.set_xlabel('Net BEV ownership premium (US$/vehicle-year)');a.set_ylabel('System cost (US$bn/year)');a.set_title('A  Vehicle ownership-cost break-even under historical fuel prices',loc='left');a.grid(alpha=.18)
    xx=[z['gasoline_cut_pct'] for z in rows];yy=[z['abatement_usd_t_adjusted_tailpipe'] for z in rows];b.plot(xx,yy,color=ORANGE,marker='s',lw=1.7);b.axhline(0,color=GRAY,ls='--');b.set_xlabel('Fuel-only gasoline reduction in reference (%)');b.set_ylabel('Incremental cost (US$/t CO₂ avoided)');b.set_title('B  Illustrative abatement-cost screen (not a matched 2050 fleet)',loc='left');b.grid(alpha=.18)
    fig.text(.5,.025,'Tailpipe gasoline emissions adjusted using 8.887 kg CO₂/gallon; upstream and ICE ownership costs are NOT re-solved.',fontsize=7.6,ha='center',color=MUTE)
    save(fig,'ScienceFigS23_Reference_and_BEV_Breakeven')

if __name__=='__main__':
    rows=abatement_data()
    for fn in [figure1,figure2,figure3,figure4,figureS1]:fn();print('Rebuilt',fn.__name__,flush=True)
    figS23(rows); print('Rebuilt abatement sensitivity and figure',flush=True)

def figS19():
    dat=json.loads((R/'us9_crop_residue_results.json').read_text())['paired_crop_full_sustainable_cap_forced'];imp=np.array([dat['n_import_kt'],dat['p_import_kt'],dat['k_import_kt']]);rem=np.array([1162.,199.2,1494.]);rec=rem-imp
    fig,(a,b)=plt.subplots(1,2,figsize=(7.05,4.05),gridspec_kw={'width_ratios':[1.42,.72]});fig.subplots_adjust(left=.175,right=.985,bottom=.21,top=.88,wspace=.43)
    y=np.arange(3);labs=['Nitrogen','Phosphorus','Potassium']
    a.barh(y,rec,height=.52,color=GREEN,label='Recovered')
    a.barh(y,imp,left=rec,height=.52,color=ORANGE,label='Purchased')
    a.invert_yaxis();a.set_yticks(y);a.set_yticklabels(labs,fontsize=8.3);a.set_xlim(0,1850);a.set_xlabel('Elemental nutrient mass (kt/year)');a.set_title('A  Annual nutrient balance',loc='left');a.grid(axis='x',alpha=.17);a.set_axisbelow(True)
    for i,(tot,x) in enumerate(zip(rem,imp)):a.text(tot+20,i,f'{tot:.0f} kt',fontsize=7.8,va='center')
    a.legend(fontsize=7.7,loc='upper center',bbox_to_anchor=(.5,-.29),frameon=False,ncol=2)
    frac=100*imp/rem;b.bar(np.arange(3),frac,color=ORANGE,width=.55)
    b.set_xticks(np.arange(3));b.set_xticklabels(['N','P','K']);b.set_ylim(0,62);b.set_ylabel('Externally replaced (%)');b.set_title('B  Missing share',loc='left');b.grid(axis='y',alpha=.17);b.set_axisbelow(True)
    for i,v in enumerate(frac):b.text(i,v+1,f'{v:.0f}%',ha='center',fontsize=8)
    save(fig,'ScienceFigS19_Crop_NPK_Balance')

def figS20():
    c=json.loads((R/'us9_crop_residue_results.json').read_text());keys=['paired_without_crop','paired_crop_economic_optimum','paired_crop_full_sustainable_cap_forced','paired_crop_full_high_collection_cost'];labs=['No crop feedstock','Cost-selected crop','Force 166 Mt crop','High collection cost'];v=[c[x]['transport_cost_bn'] for x in keys]
    r=c['paired_crop_full_sustainable_cap_forced'];imp=[r['n_import_kt'],r['p_import_kt'],r['k_import_kt']]
    fig,(a,b)=plt.subplots(1,2,figsize=(7.05,4.2),gridspec_kw={'width_ratios':[1.2,.88]});fig.subplots_adjust(left=.26,right=.985,bottom=.19,top=.88,wspace=.44)
    y=np.arange(4);a.barh(y,v,height=.6,color=[GRAY,BLUE,GREEN,ORANGE]);a.set_xlim(0,610);a.set_yticks(y);a.set_yticklabels(labs,fontsize=8.4);a.invert_yaxis();a.set_xlabel('Annual cost (US$bn; zero origin)');a.set_title('A  Matched-resource comparison',loc='left');a.grid(axis='x',alpha=.16);a.set_axisbelow(True)
    for i,u in enumerate(v):a.text(u+8,i,f'{u:.1f}',fontsize=8,va='center')
    b.bar(np.arange(3),imp,width=.58,color=[ORANGE,BLUE,GREEN]);b.set_ylim(0,710);b.set_xticks(np.arange(3));b.set_xticklabels(['N','P','K']);b.set_xlabel('Externally supplied nutrient');b.set_ylabel('kt elemental/year');b.set_title('B  Residual nutrient demand',loc='left');b.grid(axis='y',alpha=.16);b.set_axisbelow(True)
    for i,u in enumerate(imp):b.text(i,u+12,f'{u:.1f}',ha='center',fontsize=8)
    save(fig,'ScienceFigS20_Crop_Economics_Carbon')

if __name__=='__main__':
    figS19();figS20();print('Rebuilt critical supplementary NPK and crop-cost figures',flush=True)
