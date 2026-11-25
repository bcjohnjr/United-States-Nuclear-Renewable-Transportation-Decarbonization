#!/usr/bin/env python3
"""V9.12 yield-robustness figure, 600-dpi RGB TIFF; no experimental claim."""
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
R=Path(__file__).resolve().parent
F='ScienceFigS49_V912_Terrestrial_HTL_Yield_BreakEven.tif'
def run():
    d=list(csv.DictReader((R/'us912_terrestrial_htl_yield_sensitivity.csv').open()))
    x=np.array([float(q['htl_liquid_mwh_per_dry_metric_t']) for q in d])
    saving=np.array([float(q['crop_saving_bn']) for q in d]);mass=np.array([float(q['crop_selected_mt']) for q in d])
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.titlesize':11,'axes.labelsize':9.5})
    fig,axes=plt.subplots(1,2,figsize=(7.15,3.15),layout='constrained')
    ax=axes[0];ax.plot(x,saving,'o-',color='#235d85',lw=2.2)
    ax.axvline(2.6,ls='--',color='#8f7c68',lw=1.1)
    ax.axhline(0,ls=':',color='#777',lw=1)
    ax.set_ylim(bottom=-0.5);ax.set_xlim(1.05,3.14)
    ax.set_title('A  Crop-related annual saving',loc='left',fontweight='bold')
    ax.set_xlabel('Assumed terrestrial HTL liquid yield (MWh/dry t)')
    ax.set_ylabel('Saving versus matched no-crop case (US$ bn/yr)')
    ax=axes[1];ax.plot(x,mass,'s-',color='#268c65',lw=2.2)
    ax.axvline(2.6,ls='--',color='#8f7c68',lw=1.1)
    ax.set_xlim(1.05,3.14);ax.set_ylim(bottom=-6,top=185)
    ax.set_title('B  Crop residues economically selected',loc='left',fontweight='bold')
    ax.set_xlabel('Assumed terrestrial HTL liquid yield (MWh/dry t)')
    ax.set_ylabel('Model-selected crop biomass (Mt dry/yr)')
    fig.text(.5,-.015,'Shared system-wide HTL yield assumption, NOT feedstock-specific empirical yield; all cost and land constraints matched.',ha='center',fontsize=7.3)
    dest=R/F
    fig.savefig(dest,format='tiff',dpi=600,pil_kwargs={'compression':'tiff_lzw'},bbox_inches='tight',pad_inches=.18,facecolor='white')
    plt.close(fig)
    with Image.open(dest) as im:
      if im.mode!='RGB':im.convert('RGB').save(dest,format='TIFF',compression='tiff_lzw',dpi=(600,600))
    with Image.open(dest) as im: assert im.mode=='RGB' and tuple(round(k) for k in im.info['dpi'])==(600,600)
    print('Figure',F)
if __name__=='__main__':run()
