"""V7 uncluttered journal schematic. Original detailed maps and poster retained.
Hand-digitised location geometry, no siting implications.
"""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Rectangle
from matplotlib.lines import Line2D
import us2_basemap as M
ROOT=Path(__file__).resolve().parent
S=json.loads((ROOT/'scenarios.json').read_text())

def main():
    fig,ax=plt.subplots(figsize=(10.8,5.2))
    ax.add_patch(Polygon(M.CONUS, closed=True,fc='#f6f4ee',ec='#788892',linewidth=0.8,zorder=1))
    for nm in ('bamboo','hemp','corn_ethanol','residues'):
        colors={'bamboo':'#8fbf94','hemp':'#b7bc82','corn_ethanol':'#e3ba8b','residues':'#c9b39d'}
        for coords in M.REGIONS.get(nm,[]):ax.add_patch(Polygon(coords,closed=True,fc=colors[nm],ec='none',alpha=.47,zorder=2))
    for line in M.CORRIDORS.values():
        pts=np.array([M.CITIES[k] for k in line]);ax.plot(pts[:,0],pts[:,1],color='#3789c0',lw=1.25,alpha=.67,zorder=4)
    # Selection illustrates representative hubs only, not every actual proposed facility.
    hubs=[h for h in M.HUBS if len(h)>3][0:12]
    ax.scatter([h[1] for h in hubs],[h[2] for h in hubs],s=45,c='#b74b52',edgecolors='white',linewidths=.7,zorder=7,marker='h')
    selected={z['zone'] for z in S['design_sweet_spot']['seaweed'] if z['dry_mt']>0}
    for z in S['design']['seaweed']:
        if z['zone'] not in selected:continue
        x,y,w,h=z['box']; ax.add_patch(Rectangle((x,y),w,h,fc='#48ab9b',ec='white',lw=.6,alpha=.92,zorder=5))
    ax.set_xlim(-129,-64);ax.set_ylim(23,50.5);ax.set_aspect(1.45)
    ax.set_xticks([]);ax.set_yticks([])
    for k in ax.spines:ax.spines[k].set_visible(False)
    ax.set_title('Illustrative geographic components of U.S. transport-energy scenarios',fontsize=13,fontweight='bold',pad=12)
    labels=[Line2D([],[],color='#3789c0',lw=2,label='Electric-road corridors (schematic)'),
            Line2D([],[],marker='h',linestyle='',markersize=10,markerfacecolor='#b74b52',markeredgecolor='white',label='Representative reactor/heat hubs'),
            Rectangle((0,0),1,1,fc='#48ab9b',label='Selected offshore wind + fuel-seaweed zones'),
            Rectangle((0,0),1,1,fc='#e3ba8b',label='Corn/biomass and other terrestrial feedstocks')]
    ax.legend(handles=labels,ncol=2,loc='lower center',bbox_to_anchor=(0.5,-0.20),frameon=False,fontsize=9)
    fig.subplots_adjust(bottom=.23)
    fig.text(.5,.04,'Boundaries, offshore locations and routes are schematic. Not a licensed project siting map.',ha='center',fontsize=8.2,color='#56616b')
    for ext in ('png','pdf'):fig.savefig(ROOT/f'ScienceFig2_national_system.{ext}',dpi=300,bbox_inches='tight')
    plt.close(fig)
    print('Created simplified publication map; retained detailed Map1/Poster source')
if __name__=='__main__':main()
