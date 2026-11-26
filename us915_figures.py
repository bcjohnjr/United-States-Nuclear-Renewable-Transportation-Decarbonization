from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
P=Path(__file__).resolve().parent
s=json.loads((P/'US915_Methane_Results.json').read_text())['scenarios']
keys=['conservative','central','optimistic']; names=['Conservative','Central','Optimistic']; rows=[s[k] for k in keys]
plt.rcParams.update({'font.size':12,'axes.titlesize':14,'axes.labelsize':12,'font.family':'DejaVu Sans'})
fig,ax=plt.subplots(2,2,figsize=(11,8.2),layout='constrained')
x=np.arange(3); c=['#2B6576','#659A59']; a=ax[0,0]; b=np.array([r['biogas_net_avoided_mt'] for r in rows]); e=np.array([r['asp_net_avoided_mt'] for r in rows]); a.bar(x,b,label='Biogas, net',color=c[0]); a.bar(x,e,bottom=b,label='Cattle feed, net',color=c[1]); a.set_xticks(x,names); a.set_ylabel('Mt CO₂e/year'); a.set_title('A  Additional net abatement',loc='left',weight='bold'); a.legend(loc='upper left',fontsize=10); a.set_ylim(0,85)
for i,t in enumerate(b+e): a.text(i,t+2,f'{t:.1f}',ha='center',weight='bold')
a=ax[0,1]; vals=[r['biomethane_twh'] for r in rows]; a.bar(x,vals,color=c[0]); a.set_xticks(x,names); a.set_ylabel('TWh LHV/year'); a.set_title('B  Delivered biomethane',loc='left',weight='bold'); a.set_ylim(0,60)
for i,t in enumerate(vals): a.text(i,t+1.5,f'{t:.1f}',ha='center',weight='bold')
a=ax[1,0]; vals=[r['incremental_net_cost_bn'] for r in rows]; a.bar(x,vals,color='#B37939'); a.set_xticks(x,names); a.set_ylabel('US$ billion/year'); a.set_title('C  Added programme cost*',loc='left',weight='bold'); a.set_ylim(0,4.5)
for i,t in enumerate(vals): a.text(i,t+.10,f'{t:.2f}',ha='center',weight='bold')
a=ax[1,1]; l=[s['central_5pct_leak'],s['central']]; v=[r['leaked_ch4_mt']*1000 for r in l]; a.bar([0,1],v,color=['#B37939',c[0]]); a.set_xticks([0,1],['5% leak\n(no monitoring cost)','1% target\n(with monitoring)']); a.set_ylabel('kt methane/year'); a.set_title('D  Leakage control sensitivity',loc='left',weight='bold'); a.set_ylim(0,140)
for i,t in enumerate(v): a.text(i,t+4,f'{t:.1f}',ha='center',weight='bold')
for a in ax.flat:a.spines[['top','right']].set_visible(False);a.grid(axis='y',alpha=.15);a.set_axisbelow(True)
fig.suptitle('Additional agricultural and waste methane mitigation',fontsize=18,weight='bold')
fig.supxlabel('*Conditional annual costs net of biomethane sales; no fertilizer, fossil displacement, or carbon credit in central case.\nAnalyst screening assumptions; not national deployment forecasts.',fontsize=10)
fig.savefig(P/'ScienceFigS51_V915_Methane_Abatement.tif',dpi=600,pil_kwargs={'compression':'tiff_lzw'});fig.savefig(P/'_us915_embed.png',dpi=300)
plt.close(fig)
