from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
P=Path(__file__).resolve().parent

def run():
 d=json.loads((P/'US918_Evidence_Results.json').read_text());a,b,c=[x for x in d['results'] if x['scenario']=='central'][:3];
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12})
 fig,ax=plt.subplots(2,1,figsize=(11,8.5),layout='constrained');fig.suptitle('Evidence-constrained 2050 national screening results',fontsize=18,fontweight='bold')
 labels=['AEO2026 partial reference','Continued petroleum: late-2025 prices','Continued petroleum: higher-price case','Integrated alternative']
 v=[a['ref_cost_bn'],b['ref_cost_bn'],c['ref_cost_bn'],b['combined_cost_bn']];col=['#77818b','#a87842','#a87842','#237a78']
 bars=ax[0].barh(labels[::-1],v[::-1],color=col[::-1]);ax[0].bar_label(bars,fmt='%.1f',padding=6,fontsize=12);ax[0].set_xlim(0,1160);ax[0].set_title('A. Annual expenditure depends on the reference',loc='left',fontsize=14,fontweight='bold');ax[0].set_xlabel('Billion USD/year (conditional price cases)')
 labels=['AEO2026 partial reference','Continued petroleum reference','Alternative after gas substitution']
 v=[a['ref_emissions_mt'],b['ref_emissions_mt'],b['transport_emissions_mt']-b['gas_credit_mt']];bars=ax[1].barh(labels[::-1],v[::-1],color=['#77818b','#a87842','#237a78'][::-1]);ax[1].bar_label(bars,fmt='%.1f',padding=6,fontsize=12);ax[1].set_xlim(0,3800);ax[1].set_title('B. Partial transport emissions, excluding agricultural abatement',loc='left',fontsize=14,fontweight='bold');ax[1].set_xlabel('Million tonnes CO₂e/year')
 for a0 in ax:
  a0.spines[['top','right']].set_visible(False);a0.set_axisbelow(True);a0.grid(axis='x',alpha=.2);a0.tick_params(labelsize=11)
 png=P/'_v918_tmp.png';fig.savefig(png,dpi=600,facecolor='white');plt.close(fig)
 with Image.open(png) as im:
  im.convert('RGB').save(P/'ScienceFigS53_V918_Evidence_Constrained.tif',compression='tiff_lzw',dpi=(600,600));im.thumbnail((2200,2200));im.convert('RGB').save(P/'_us918_embed.png')
 png.unlink()
if __name__=='__main__':run()
