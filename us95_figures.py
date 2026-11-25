#!/usr/bin/env python3
"""Generate V9.5 model-grounded TIFFs at actual 600-dpi metadata, RGB, journal width."""
import csv,json,pathlib,math
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from PIL import Image
import us2_model as M
import us95_aeo_reference_bridge as B
ROOT=pathlib.Path(__file__).resolve().parent
J=json.loads((ROOT/'US95_AEO2026_Cost_Emissions_Results.json').read_text())
U=json.loads((ROOT/'us95_paired_aeo_uncertainty_summary.json').read_text())
FONT=9
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':FONT,'axes.labelsize':FONT,'xtick.labelsize':8,'ytick.labelsize':8,'legend.fontsize':8,'savefig.facecolor':'white'})

def save(fig,name):
    f=ROOT/name
    fig.savefig(f,dpi=600,format='tiff',pil_kwargs={'compression':'tiff_lzw'},bbox_inches='tight',pad_inches=.14)
    plt.close(fig)
    with Image.open(f) as im:
        rgb=Image.new('RGB', im.size, 'white')
        if im.mode == 'RGBA': rgb.paste(im, mask=im.getchannel('A'))
        else: rgb.paste(im.convert('RGB'))
        rgb.save(f, format='TIFF', compression='tiff_lzw', dpi=(600,600))
    with Image.open(f) as im:
        assert im.info.get('dpi')==(600.0,600.0) and im.mode=='RGB', (f,im.info.get('dpi'),im.mode)
    print('Figure:',f.name,flush=True)

def fig6():
    rows=J['reference_cost_screens'];sc=J['scenarios'];old=sc['v94_jet_existing_truck_stock']['alternative_cost_bn_2026usd'];truck=sc['v95_jet_eia_medium_heavy_fleet']['alternative_cost_bn_2026usd'];bound=J['reactor_bounded_search']['best_cost_bn']
    fig,ax=plt.subplots(figsize=(7.2,4.1)); fig.subplots_adjust(bottom=.17,top=.97,left=.38,right=.94)
    cats=['EIA energy expenditures¹','EIA + low allowance²','EIA + central allowance²','EIA + high allowance²','Alternative: V9.4 fleet','Alternative: EIA truck fleet','Alternative: bounded hubs³']
    vals=[J['eia_source_values']['eia_energy_exp_2050_bn_2025_usd']]+[x['reference_screen_total_bn_2026usd'] for x in rows]+[old,truck,bound]
    ax.barh(range(len(vals)),vals,height=.68)
    for i,v in enumerate(vals):ax.text(v+7,i,f'{v:.0f}',ha='left',va='center',fontsize=8)
    ax.invert_yaxis();ax.set_xlim(0,725);ax.set_xlabel('US$bn per year — screening boundaries differ')
    ax.set_yticks(range(len(vals)),cats); ax.xaxis.grid(True,alpha=.15); ax.set_axisbelow(True)
    fig.text(.03,.015,'¹ EIA: 2025 dollars, energy incl. taxes.   ² Assumed allowances, 2026 dollars.   ³ 945 hubs; deployment unverified.',fontsize=7.1)
    save(fig,'Fig6_AEO2026_Partial_Cost_Bridge.tif')

def fleet():
    a=J['eia_source_values'];fig,ax=plt.subplots(figsize=(7.2,3.2));fig.subplots_adjust(left=.28,right=.96,top=.91,bottom=.18)
    items=[('V9.4 net-costed truck fleet',5.05),('AEO 2050 medium + heavy',a['freight_medium_heavy_m']),('AEO 2050 all classes',a['freight_2050_fleet_m'])]
    vals=[v for _,v in items]
    y=list(range(3));ax.barh(y,vals,height=.53)
    ax.set_yticks(y,[x[0] for x in items]);ax.invert_yaxis();ax.set_xlim(0,27)
    ax.set_xlabel('Million vehicles (different EIA size-class coverage)');ax.xaxis.grid(True,alpha=.15);ax.set_axisbelow(True)
    for i,v in enumerate(vals):ax.text(v+.3,i,f'{v:.2f} M',va='center',fontsize=8)
    save(fig,'FigS26_AEO_Freight_Stock_Reconciliation.tif')

def boundary():
    rs=J['reference_emissions_screens'];fig,ax=plt.subplots(figsize=(7.2,3.7));fig.subplots_adjust(bottom=.23,top=.9,left=.12,right=.98)
    cats=['EIA direct\nCO₂','Partial WTW\nlow','Partial WTW\ncentral','Partial WTW\nhigh','Alternative\nmodel WTW']
    vals=[rs[0]['eia_direct_mt']]+[r['partial_reference_wtw_mt'] for r in rs]+[rs[0]['alternative_model_wtw_mt']]
    ax.bar(range(5),vals,width=.62);ax.set_ylim(0,1900);ax.set_ylabel('Mt CO₂e/year (scope-dependent)');ax.set_xticks(range(5),cats);ax.yaxis.grid(True,alpha=.15);ax.set_axisbelow(True)
    for i,v in enumerate(vals):ax.text(i,v+25,f'{v:,.0f}',ha='center',fontsize=8)
    fig.text(.02,.015,'Reference WTW uses assumed 5–15 g/MJ upstream and 10–100 g/kWh electricity intensities; not a complete matched LCA.',fontsize=7.3)
    save(fig,'FigS27_AEO_2050_Emissions_Scope_Bridge.tif')

def paired():
    rows=list(csv.DictReader((ROOT/'us95_paired_aeo_cost_screen.csv').open(encoding='utf-8-sig')))
    vals=[float(r['delta_alt_minus_reference_bn']) for r in rows]
    fig,ax=plt.subplots(figsize=(7.2,3.3));fig.subplots_adjust(bottom=.24,top=.89,left=.11,right=.96)
    ax.hist(vals,bins=40,edgecolor='white',linewidth=.4)
    ax.axvline(0,color='black',linestyle='--',linewidth=1,label='Cost parity')
    ax.axvline(U['median_alt_minus_reference_bn'],linestyle='-',linewidth=1.5,label=f'Screen median +${U["median_alt_minus_reference_bn"]:.0f}bn')
    ax.set_xlabel('Alternative minus partial reference cost screen (US$bn/year)');ax.set_ylabel('Draws');ax.legend(frameon=False,loc='upper right');ax.yaxis.grid(True,alpha=.12);ax.set_axisbelow(True)
    fig.text(.02,.02,'Analyst-defined distributions; incomplete cost boundary. Draw frequencies are not probabilities of real-world outcomes.',fontsize=7.2)
    save(fig,'FigS28_Joint_Uncertainty_Partial_Reference.tif')

def crop():
    base=J['scenarios']['v95_jet_eia_medium_heavy_fleet'];c=J['scenarios']['v95_conservative_biomass_forced_full_crop']
    fig,axes=plt.subplots(1,2,figsize=(7.2,3.45),gridspec_kw={'width_ratios':[1,1.3]});fig.subplots_adjust(left=.11,right=.98,top=.90,bottom=.25,wspace=.44)
    ax=axes[0]; vals=[base['alternative_cost_bn_2026usd'],c['alternative_cost_bn_2026usd']];bars=ax.bar([0,1],vals);ax.set_ylim(0,760);ax.set_ylabel('US$bn/year');ax.set_xticks([0,1],['Unrestricted\nresidue pools','Conservative\nresource / NPK']);
    for i,v in enumerate(vals):ax.text(i,v+10,f'{v:.1f}',ha='center',fontsize=8)
    ax=axes[1]; n=[c['nitrogen_import_kt'],c['phosphorus_import_kt'],c['potassium_import_kt']]
    ax.bar(['N','P','K'],n);ax.set_ylabel('External replacement (kt element/year)');ax.set_ylim(0,720)
    for i,v in enumerate(n):ax.text(i,v+12,f'{v:.1f}',ha='center',fontsize=8)
    fig.text(.02,.02,'Forced 166 Mt annual crop-residue case, with 150 Mt independently assumed non-crop pool; soil restoration remains unvalidated.',fontsize=7.2)
    save(fig,'FigS29_Crop_Resource_NPK_Constraints.tif')

def prices():
    dat=J['eia_source_values']['new_2050_vehicle_price_thousand_2025usd_selected_classes'];cats=['Compact','Midsize','Small crossover','Large pickup'];names=['compact','midsize','small_crossover','large_pickup']
    gaps=[dat['bev_300mi'][k]-dat['gasoline'][k] for k in names]
    fig,ax=plt.subplots(figsize=(7.2,3.2));fig.subplots_adjust(left=.13,right=.97,bottom=.2,top=.92)
    ax.barh(range(4),gaps);ax.set_yticks(range(4),cats);ax.invert_yaxis();ax.set_xlabel('2050 BEV (300-mile) price minus gasoline price (thousand 2025 USD)');ax.axvline(0,color='black',linewidth=.7);ax.xaxis.grid(True,alpha=.16);ax.set_axisbelow(True)
    ax.set_xlim(min(-2,min(gaps)-2),max(gaps)+5)
    for i,v in enumerate(gaps):ax.text(v+.35 if v>=0 else v-.4,i,f'{v:+.1f}',va='center',fontsize=8)
    save(fig,'FigS30_AEO_New_Vehicle_Price_Differences.tif')

def reactor():
    _,a=B.read_source();p,_=B.config(a)
    rows=[]
    for n in range(0,1501,10):
        cap=M.reactor_cost(p['reactor_case'],max(4*n,1))['fleet_avg_kwt_with_idc']
        r=M.solve(p,scenario='least_cost',blend_vol=0.0,capex_kwt=cap,fixed_hubs=n)
        rows.append({'hubs':n,'annual_cost_bn':r['transport_cost_bn'],'reactor_modules':4*n,'learning_capex_kwt':cap})
    with (ROOT/'us95_reactor_cost_curve.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,rows[0].keys());w.writeheader();w.writerows(rows)
    fig,ax=plt.subplots(figsize=(7.2,3.3));fig.subplots_adjust(left=.12,right=.96,bottom=.23,top=.91)
    ax.plot([r['hubs'] for r in rows],[r['annual_cost_bn'] for r in rows],linewidth=1.6)
    it=J['scenarios']['v95_jet_eia_medium_heavy_fleet'];bound=J['reactor_bounded_search']
    ax.scatter([it['hubs'],bound['best_hubs']],[it['alternative_cost_bn_2026usd'],bound['best_cost_bn']],s=40,zorder=3)
    ax.annotate(f'Iterative: {it["hubs"]:.0f} hubs, ${it["alternative_cost_bn_2026usd"]:.1f}bn',(it['hubs'],it['alternative_cost_bn_2026usd']),xytext=(it['hubs']+125,it['alternative_cost_bn_2026usd']+35),arrowprops={'arrowstyle':'-','linewidth':.6},fontsize=8)
    ax.annotate(f'Bounded: {bound["best_hubs"]} hubs, ${bound["best_cost_bn"]:.1f}bn',(bound['best_hubs'],bound['best_cost_bn']),xytext=(bound['best_hubs']-220,bound['best_cost_bn']+30),arrowprops={'arrowstyle':'-','linewidth':.6},fontsize=8)
    ax.set_ylim(600,750);ax.set_xlim(0,1500);ax.set_ylabel('Annual alternative transport cost (US$bn)');ax.set_xlabel('Reactor hubs (four modules each)');ax.yaxis.grid(True,alpha=.12);ax.set_axisbelow(True)
    fig.text(.02,.02,'Capital learning is assumed endogenous; the high-hub minimum is not a demonstrated 2050 deployment plan.',fontsize=7.4)
    save(fig,'FigS31_Reactor_Learning_Bounded_Search.tif')

if __name__=='__main__':
    fig6();fleet();boundary();paired();crop();prices();reactor()
