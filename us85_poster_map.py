"""Rebuild the corrected U.S. V9.1 schematic poster from current model outputs.
Contains distinct panels for the 220-GW design and the OPTIONAL paired crop-HTL
experiment; no invented site-specific agronomic claims or route capacities.
"""
import csv,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Rectangle,FancyBboxPatch
from matplotlib.lines import Line2D
import us2_basemap as B
import us2_figures as F
P=Path(__file__).resolve().parent
S=json.load(open(P/'scenarios.json')); SS=S['design_sweet_spot']; D=S['design']; LC=S['least_cost']
rows={r['scenario']:r for r in csv.DictReader(open(P/'us9_crop_residue_scenarios.csv'))}
C={'navy':'#10283d','blue':'#2785bf','teal':'#118f84','brown':'#ab7d4c','red':'#b94152','muted':'#5c6c7a','bg':'#f8fafc','line':'#d5e0e9','green':'#417f5c','yellow':'#d4a146','sky':'#e6f3f9'}
plt.rcParams.update({'font.family':'DejaVu Sans','pdf.fonttype':42})

def panel(ax,xywh,fill='#ffffff'):
 x,y,w,h=xywh; ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.012,rounding_size=0.02',fc=fill,ec=C['line'],lw=1,transform=ax.transAxes))

def save(fig,name):
 fig.savefig(P/(name+'.tif'),dpi=600,bbox_inches='tight',facecolor='white',format='tiff',pil_kwargs={'compression':'tiff_lzw','dpi':(600,600)})
 plt.close(fig)

def main():
 fig=plt.figure(figsize=(22,14),facecolor='white')
 fig.text(.028,.970,'UNITED STATES  |  TRANSPORT DECARBONISATION',fontsize=31,color=C['navy'],weight='bold',ha='left',va='top')
 fig.text(.028,.936,'Corrected V9.1 model · 2050 energy system · schematic national network',fontsize=18,color=C['muted'],ha='left',va='top')
 fig.lines.append(Line2D([.025,.975],[.913,.913],color=C['line'],lw=1.5,transform=fig.transFigure))
 # map field
 ax=fig.add_axes([.025,.350,.662,.542]);
 ax.set_facecolor(C['sky']);ax.add_patch(Polygon(B.CONUS,fc='#f2f0e8',ec='#778b97',lw=1.5,zorder=1))
 for line in B.STATE_LINES:
  xy=np.asarray(line);ax.plot(xy[:,0],xy[:,1],lw=.48,color='#abb4b9',zorder=2)
 for cat,col in [('onshore_wind','#a5d9c2'),('solar','#f0d7a2'),('corn_ethanol','#e5af86'),('residues','#d5b28a'),('hemp','#c7cb87'),('bamboo','#95bd95')]:
  for v in B.REGIONS.get(cat,[]): ax.add_patch(Polygon(v,fc=col,alpha=.57,ec='none',zorder=1.7))
 for name,cities in B.CORRIDORS.items():
  xy=np.asarray([B.CITIES[c] for c in cities]);ax.plot(xy[:,0],xy[:,1],color='white',lw=4.5,zorder=3,solid_capstyle='round');ax.plot(xy[:,0],xy[:,1],color=C['blue'],lw=2.5,zorder=4,solid_capstyle='round')
 for k in ('I-90','I-70','I-40','I-10','I-95'):
  if k in B.CORRIDORS:
   xy=np.asarray([B.CITIES[c] for c in B.CORRIDORS[k]]);ii=len(xy)//2;x,y=xy[ii];ax.text(x,y+.4,k,fontsize=9,weight='bold',color=C['blue'],ha='center',bbox={'facecolor':'white','alpha':.8,'edgecolor':'none','pad':1},zorder=5)
 for i,z in enumerate(D['seaweed'],1):
  x,y,w,h=z['box'];sel=any(q['zone']==z['zone'] and q.get('dry_mt',0)>0 for q in SS['seaweed'])
  ax.add_patch(Rectangle((x,y),w,h,fc=F.SPECIES_COL[z['color']] if sel else 'none',ec=F.SPECIES_COL[z['color']],lw=1.2,hatch=None if sel else '///',alpha=.82,zorder=5))
  cx,cy=x+w/2,y+h/2;ax.text(cx,cy,f'Z{i:02d}',fontsize=9,weight='bold',color='white' if sel else C['navy'],ha='center',va='center',zorder=7,bbox=dict(facecolor=F.SPECIES_COL[z['color']] if sel else 'white',edgecolor='none',alpha=.85,pad=1.2))
 nums=F.allocate_hubs(SS['hubs']);assert int(nums.sum())==round(SS['hubs'])
 for i,((site,x,y,weight,role),count) in enumerate(zip(B.HUB_SITES,nums),1):
  ax.plot(x,y,marker='o',markersize=12,markerfacecolor=C['red'],markeredgecolor='white',markeredgewidth=1.3,zorder=9)
  ax.text(x,y,f'{i:02d}',fontsize=6.2,color='white',weight='bold',ha='center',va='center',zorder=10)
 for _,(x,y) in B.GAS_BASINS.items():ax.plot(x,y,'D',ms=5,color='#9c7043',markeredgecolor='white',zorder=6)
 for pts in B.NEW_PIPES:
  xy=np.array(pts);ax.plot(xy[:,0],xy[:,1],color='#8c65af',ls='--',lw=1.6,zorder=5)
 for nm,(x,y) in B.CANADA_ENTRY.items():ax.scatter(x,y,s=90,marker='v',c='#7256a5',edgecolors='white',zorder=7)
 ax.text(-118,46,'PACIFIC\nNORTHWEST',color=C['muted'],ha='center',fontsize=11,alpha=.85)
 ax.text(-100,43,'GREAT PLAINS',color=C['muted'],ha='center',fontsize=11,alpha=.75)
 ax.text(-85,37,'SOUTHEAST',color=C['muted'],ha='center',fontsize=11,alpha=.75)
 ax.set_xlim(-133,-62);ax.set_ylim(23.4,50.5);ax.set_aspect(1.28);ax.set_xticks([]);ax.set_yticks([])
 for sp in ax.spines.values():sp.set_visible(False)
 fig.text(.032,.339,'Hubs, energy zones and transport corridors are schematic. No site, pipeline or farm is represented as licensed or committed.',fontsize=10,color=C['muted'])
 # hub site key bottom left
 left=fig.add_axes([.025,.055,.41,.246]);left.axis('off')
 left.text(.0,.99,'REACTOR HEAT-CASCADE HUB SITE KEY',fontsize=15,weight='bold',color=C['navy'],va='top')
 left.text(.0,.91,f'Each red map marker is a site; allocations sum to ~{round(SS["hubs"]):,} four-reactor hubs in the 220 GW case.',fontsize=10.5,color=C['muted'])
 for j,(item,ct) in enumerate(zip(B.HUB_SITES,nums)):
  col=j//10;row=j%10
  n=item[0];n=n.replace('Seadrift / Coastal Bend TX','Coastal Bend TX').replace('Port Arthur / Lake Charles','Port Arthur / Lake Charles').replace('Baton Rouge / St. James LA','Baton Rouge / St James')
  if len(n)>24:n=n[:23]+'…'
  x=col*.34;y=.80-row*.072
  left.text(x,y,f'H{j+1:02d}',color=C['red'],weight='bold',fontsize=9.2,va='center')
  left.text(x+.053,y,f'{n} ({int(ct)})',fontsize=8.9,color=C['navy'],va='center')
 # offshore key bottom center
 zones=fig.add_axes([.445,.055,.235,.246]);zones.axis('off')
 zones.text(.0,.99,'OFFSHORE WIND + SEAWEED',fontsize=15,weight='bold',color=C['navy'],va='top')
 zones.text(.0,.91,'Filled = in 220 GW scenario; hatched = 515 GW expansion.',fontsize=10.2,color=C['muted'])
 selected={z['zone']:z for z in SS['seaweed'] if z.get('dry_mt',0)>0}
 for j,z in enumerate(D['seaweed']):
  x=(j//7)*.51;y=.82-(j%7)*.112
  flag='●' if z['zone'] in selected else '○'
  q=selected.get(z['zone'],z)
  label=z['region'];label=label if len(label)<24 else label[:22]+'…'
  zones.text(x,y,f'Z{j+1:02d}',fontsize=10,weight='bold',color=F.SPECIES_COL[z['color']],va='top')
  zones.text(x+.092,y,f'{label}',fontsize=8.8,color=C['navy'],va='top')
  zones.text(x+.092,y-.037,f'{flag} {q["wind_gw"]:.0f} GW',fontsize=8.8,color=C['muted'],va='top')
 # side panel
 side=fig.add_axes([.707,.055,.274,.840]);side.axis('off')
 side.add_patch(Rectangle((0,0),1,1,fc='#fbfdff',ec=C['line'],lw=1.2,transform=side.transAxes))
 def t(x,y,s,sz=10,weight='normal',color=None):side.text(x,y,s,fontsize=sz,weight=weight,color=color or C['navy'],va='top',transform=side.transAxes)
 t(.055,.968,'2050 TRANSPORT COST',18,'bold');t(.055,.924,'220 GW diversification configuration',11,color=C['muted'])
 t(.055,.892,f'${SS["transport_cost_bn"]:.1f} bn / year',24,'bold',C['navy'])
 t(.055,.830,f'Least cost, 0 GW: ${LC["transport_cost_bn"]:.1f} bn/yr',12)
 t(.055,.795,f'515 GW offshore case: ${D["transport_cost_bn"]:.1f} bn/yr',12)
 t(.055,.760,'Petroleum (late-2025): $592.8 bn/yr',12)
 side.plot([.05,.95],[.731,.731],transform=side.transAxes,c=C['line'],lw=1)
 t(.055,.707,'MODELLED 220 GW SYSTEM',15,'bold')
 vals=[(f'{SS["enduse"]["el_total"]:,.0f} TWh/yr','Transport electricity demand'),
       (f'{SS["emissions"]["total_mt"]:.0f} Mt/yr','Well-to-wheel CO₂e (−93.4%)'),
       (f'{SS["hubs"]:.0f} hubs','Four-reactor HTGR heat hubs (LP)'),
       (f'{SS["gw"]["solar"]:.0f} GW','Modelled utility solar capacity'),
       (f'{sum(x["dry_mt"] for x in SS["seaweed"]):.1f} Mt dry/yr','Seaweed crop, illustrative')]
 for j,(v,caption) in enumerate(vals):
  yy=.669-j*.069
  t(.058,yy,v,14,'bold',C['blue']);t(.41,yy-.001,caption,10,color=C['muted'])
 side.plot([.05,.95],[.318,.318],transform=side.transAxes,c=C['line'],lw=1)
 t(.055,.302,'OPTIONAL CROP-HTL / SOIL SCENARIO',14,'bold',C['green'])
 r=rows['paired_crop_full_sustainable_cap_forced'];zero=rows['paired_without_crop']
 t(.055,.264,f'{float(r["crop_htl_mt"]):.0f} Mt/yr crop residues → {float(r["crop_htl_liquids_twh"]):.0f} TWh liquid fuel',11)
 t(.055,.232,f'${float(zero["transport_cost_bn"])-float(r["transport_cost_bn"]):.2f} bn/yr saving vs paired no-crop case',10.5,weight='bold')
 t(.055,.199,'N 581 kt   ·   P 49.8 kt   ·   K 298.8 kt',11,weight='bold')
 t(.055,.172,'External elemental nutrient replacements (not zero)',9.6,color=C['muted'])
 t(.055,.145,'K ≈ 570 kt KCl/yr; Saskatchewan supply hypothetical',9.4)
 t(.055,.114,'19.9 Mt hydrochar and 3.34 Mt methane carbon to soil',9.4)
 t(.055,.085,'Not included in the 220 GW cost above.',10,weight='bold',color=C['red'])
 t(.055,.055,'No field-scale SOC/erosion or nutrient-treatment validation.',9.0,color=C['muted'])
 fig.text(.028,.021,'SOURCE: U.S. transport code V9.1 | Corrected MJ↔kWh truck ratios | Paired crop restoration assumptions [A] | 2026 USD, pre-tax | Schematics are not feasibility/siting studies.',fontsize=10,color=C['muted'])
 save(fig,'Poster_US_Map');print('wrote poster',round(SS['hubs']),round(SS['transport_cost_bn'],2))

if __name__=='__main__':main()
