from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
P=Path(__file__).resolve().parent
def run():
 d=json.loads((P/'US916_Coupled_Results.json').read_text()); rows=[r for r in d['rows'] if r['scenario']=='central' and r['carbon_shadow_usd_t']==100]; a,b,c=rows[:3]
 fig,axs=plt.subplots(2,1,figsize=(10,8),layout='constrained'); plt.rcParams.update({'font.size':12}); fig.suptitle('2050 same-service reference and biomethane routing screens',fontsize=16,fontweight='bold')
 labels=['AEO2026 partial\nreference','Continued petroleum\nlate-2025 prices','Continued petroleum\nNov-2026 price case','Integrated alternative\n$100/t routing weight']
 vals=[a['ref_cost_bn'],b['ref_cost_bn'],c['ref_cost_bn'],a['combined_cost_bn']]; colors=['#777777','#b98a58','#b98a58','#286e83']; ax=axs[0]; bars=ax.barh(labels[::-1],vals[::-1],color=colors[::-1]);ax.bar_label(bars,fmt='%.1f',padding=4,fontsize=11);ax.set_xlim(0,1160);ax.set_xlabel('Annual conditional expenditure (billion USD)');ax.set_title('A. Cost depends on reference and inherited liquid prices',loc='left',fontsize=13);ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True)
 ax=axs[1]; lab=['AEO2026 reference','Continued petroleum reference','Alternative after gas routing']; vv=[a['ref_emissions_mt'],b['ref_emissions_mt'],a['transport_emissions_before_ad_mt']-a['gas_direct_credit_mt']];bars=ax.barh(lab[::-1],vv[::-1],color=['#777777','#b98a58','#286e83'][::-1]);ax.bar_label(bars,fmt='%.1f',padding=4,fontsize=11);ax.set_xlim(0,3800);ax.set_xlabel('Partial transport emissions (Mt CO₂e/year)');ax.set_title('B. Transport emissions (agricultural savings reported separately)',loc='left',fontsize=13);ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True)
 for ax in axs:ax.spines[['top','right']].set_visible(False);ax.tick_params(labelsize=11)
 fig.savefig(P/'_us916_plot.png',dpi=600,facecolor='white');plt.close(fig)
 with Image.open(P/'_us916_plot.png') as im:im.convert('RGB').save(P/'ScienceFigS52_V916_Reference_and_Gas_Routing.tif',compression='tiff_lzw',dpi=(600,600));im.thumbnail((1600,1600));im.convert('RGB').save(P/'_us916_embed.png',dpi=(160,160))
 (P/'_us916_plot.png').unlink()
if __name__=='__main__':run()
