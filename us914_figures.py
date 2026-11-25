#!/usr/bin/env python3
"""V9.14 readable at 7.2-in publication width, 600-dpi RGB TIFFs.
Never modify FigS1 / FigS22 Grid Harvester source artwork or numbers.
"""
import csv,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
R=Path(__file__).resolve().parent
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8.2,'axes.labelsize':8.5,
                     'axes.titlesize':9.0,'xtick.labelsize':7.5,'ytick.labelsize':7.5})
def save(fig,name):
    p=R/name
    fig.savefig(p,dpi=600,format='tiff',pil_kwargs={'compression':'tiff_lzw'},facecolor='white')
    plt.close(fig)
    with Image.open(p) as im:
        if im.mode!='RGB':im.convert('RGB').save(p,format='TIFF',compression='tiff_lzw',dpi=(600,600))
    with Image.open(p) as im:assert im.mode=='RGB' and all(abs(q-600)<1 for q in im.info['dpi'])
    print('600-DPI FIG',name)
def fig1():
    a=json.loads((R/'US99_Scenario_Analysis.json').read_text());c=a['scenarios'][0];no=a['scenarios'][-1];l=a['lca_accounting'][0]
    fig,(ax,bx)=plt.subplots(1,2,figsize=(7.12,3.85))
    fig.subplots_adjust(left=.092,right=.975,top=.81,bottom=.32,wspace=.33)
    labs=['AEO2026\npartial reference','No-crop\nalternative','Crop-enabled\nalternative']
    vals=[477.15,no['annual_cost_bn'],c['annual_cost_bn']]
    ax.bar(range(3),vals,color=['#626e78','#c37a59','#266d5a'],width=.64)
    ax.set_xticks(range(3),labs);ax.tick_params(axis='x',pad=5)
    ax.set_ylabel('Annual expenditure (US$ bn)');ax.set_ylim(0,760)
    ax.set_title('A  Conditional cost comparison',loc='left',fontweight='bold',pad=11)
    for j,v in enumerate(vals):ax.text(j,v+14,f'{v:.1f}',ha='center',fontsize=8)
    emissions=[a['reference_partial_mt'],no['emissions_wtw_mt'],l['replaced_route_screen_mt']]
    bx.bar(range(3),emissions,color=['#626e78','#c37a59','#266d5a'],width=.64)
    bx.set_xticks(range(3),['AEO partial\nreference','No-crop\nalternative','Crop process\nsubstitution'])
    bx.set_ylabel('Screened emissions (Mt CO₂e/yr)');bx.set_ylim(0,1810)
    bx.set_title('B  Partial lifecycle comparison',loc='left',fontweight='bold',pad=11)
    for j,v in enumerate(emissions):bx.text(j,v+32,f'{v:,.0f}',ha='center',fontsize=8)
    # Place footnote below axes, not intersecting tick labels.
    fig.text(.5,.11,'EIA reference is a partial reconstruction; crop fuel replaces the audited 10-g/MJ route term.',
             ha='center',va='center',fontsize=7.1)
    fig.text(.5,.065,'Annual modelled comparisons; NOT an empirically validated national deployment forecast.',
             ha='center',va='center',fontsize=7.1)
    save(fig,'ScienceFig1_V914_Conditional_Cost_and_LCA.tif')
def fig5():
    with (R/'us914_paired_uncertainty.csv').open() as f:mc=list(csv.DictReader(f))
    with (R/'us99_joint_conservative_reactors.csv').open() as f:hubs=list(csv.DictReader(f))
    ab=np.array([float(z['abatement_usd_t']) for z in mc]);x=np.array([float(z['hubs']) for z in hubs]);y=np.array([float(z['annual_cost_bn']) for z in hubs])
    fig,(ax,bx)=plt.subplots(1,2,figsize=(7.12,3.65))
    fig.subplots_adjust(left=.097,right=.975,top=.83,bottom=.235,wspace=.34)
    ax.hist(ab,bins=26,color='#257e64',edgecolor='white')
    ax.axvline(np.median(ab),ls='--',color='#8d442e',lw=1.3)
    ax.set_xlabel('Conditional abatement cost (US$/t CO₂e)');ax.set_ylabel('Simulation draws')
    ax.set_title('A  1,000-draw uncertainty screen',loc='left',fontweight='bold',pad=10)
    ax.text(.04,.95,f'Median ${np.median(ab):.1f}/t\n5th–95th: ${np.percentile(ab,5):.0f}–${np.percentile(ab,95):.0f}/t',
            transform=ax.transAxes,va='top',fontsize=7.7)
    bx.plot(x,y,'o-',lw=1.8,color='#275f83',ms=4)
    bx.set_xlabel('Fixed four-module reactor hubs');bx.set_ylabel('Annual system cost (US$ bn)')
    bx.set_title('B  Joint-conservative reactor screen',loc='left',fontweight='bold',pad=10)
    bx.set_xlim(-12,266);bx.set_ylim(min(y)-7,max(y)+7)
    fig.text(.5,.075,'HTL yield and incremental crop-delivery cost are assumed; no calibrated probabilities.',ha='center',fontsize=7.1)
    save(fig,'ScienceFig5_V914_Uncertainty_and_Reactor.tif')
def joint():
    with (R/'us913_combined_yield_delivery.csv').open() as f:rows=list(csv.DictReader(f))
    ys=sorted({float(q['htl_liquid_yield_mwh_dry_t']) for q in rows});ds=sorted({float(q['extra_crop_delivery_usd_dry_t']) for q in rows})
    dat={(float(q['htl_liquid_yield_mwh_dry_t']),float(q['extra_crop_delivery_usd_dry_t'])):q for q in rows}
    z=np.array([[float(dat[y,d]['crop_saving_bn']) for d in ds] for y in ys])
    fig,ax=plt.subplots(figsize=(7.12,3.65))
    fig.subplots_adjust(left=.14,right=.87,top=.85,bottom=.18)
    im=ax.imshow(z,cmap='YlGn',vmin=0,vmax=13,origin='lower',aspect='auto')
    ax.set_xticks(range(len(ds)),[f'+${q:g}' for q in ds]);ax.set_yticks(range(len(ys)),[f'{q:.1f}' for q in ys])
    ax.set_xlabel('Additional biomass delivery charge (US$/dry metric tonne)')
    ax.set_ylabel('Common terrestrial HTL yield\n(MWh/dry metric tonne)')
    ax.set_title('Joint yield × delivery-cost sensitivity — matched paired optimisations',loc='left',fontweight='bold',pad=12)
    for i in range(len(ys)):
        for j in range(len(ds)):
            v=z[i,j];ax.text(j,i,f'${v:.2f}bn',ha='center',va='center',color='white' if v>7 else '#15372e',fontsize=8.4)
    cb=fig.colorbar(im,ax=ax,fraction=.045,pad=.025);cb.set_label('Annual saving (US$ bn)')
    fig.text(.51,.045,'All 16 cells use the same 166-Mt analyst ceiling; values are not county-supply estimates.',ha='center',fontsize=7.0)
    save(fig,'ScienceFigS50_V914_Joint_HTL_Yield_Delivery.tif')
if __name__=='__main__':
    fig1();fig5();joint()
