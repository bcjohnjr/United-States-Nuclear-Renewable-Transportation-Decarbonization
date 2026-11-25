#!/usr/bin/env python3
"""V9.11 conditional robustness figures. Publication TIFFs; source-preserving."""
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from PIL import Image
R=Path(__file__).resolve().parent
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.labelsize':9.5,'xtick.labelsize':8,'ytick.labelsize':8.5})
def rows(name):return list(csv.DictReader((R/name).open(encoding='utf-8')))
def save(fig,stem):
 fn=R/stem
 fig.savefig(fn,dpi=600,format='tiff',pil_kwargs={'compression':'tiff_lzw'},facecolor='white',bbox_inches='tight',pad_inches=.13)
 plt.close(fig)
 with Image.open(fn) as im:
  if im.mode!='RGB':im.convert('RGB').save(fn,format='TIFF',compression='tiff_lzw',dpi=(600,600))
 with Image.open(fn) as im:
  assert im.mode=='RGB' and tuple(round(x) for x in im.info.get('dpi',(0,0)))==(600,600)
 print('FIGURE',stem)

def main():
 data=rows('us911_resource_delivery_grid.csv')
 aval=[0,0.25,0.5,0.75,1.0];prem=[0,20,40,80,120]
 z=np.array([[float(next(q['crop_saving_bn'] for q in data if float(q['resource_ceiling_fraction'])==a and float(q['delivery_surcharge_usd_dry_metric_t'])==p)) for p in prem] for a in aval])
 fig,ax=plt.subplots(figsize=(7.1,3.8),layout='constrained')
 ims=ax.imshow(z,cmap='YlGn',vmin=0,vmax=6.9,origin='lower',aspect='auto')
 ax.set_xticks(range(5),[f'+${p}/t' for p in prem]);ax.set_yticks(range(5),['0','41.5','83','124.5','166'])
 ax.set_xlabel('Additional delivered-biomass charge (2026 US$/dry metric tonne)')
 ax.set_ylabel('Assumed maximum crop availability (Mt/year)')
 ax.set_title('Marginal cost and resource capacity jointly govern crop value',loc='left',fontweight='bold')
 for i in range(5):
  for j in range(5):ax.text(j,i,f'{z[i,j]:.2f}',ha='center',va='center',color='white' if z[i,j]>=4 else '#1f332e',fontsize=9)
 fig.colorbar(ims,ax=ax,label='Annual crop saving (US$ bn)',shrink=.82)
 save(fig,'ScienceFigS46_V911_Delivered_Cost_Resource_Robustness.tif')
 data=rows('us911_cover_land_stress.csv')
 area=np.array([float(x['assumed_cover_crop_land_mha']) for x in data])
 saving=np.array([float(x['crop_saving_bn']) if x['crop_saving_bn'] else np.nan for x in data])
 biomass=np.array([float(x['selected_crop_mt']) if x['selected_crop_mt'] else np.nan for x in data])
 fig,ax=plt.subplots(figsize=(7.1,3.65));fig.subplots_adjust(left=.12,right=.87,top=.83,bottom=.27)
 ax.plot(area,saving,'o-',lw=2,color='#256b54',label='Annual avoided expenditure')
 ax.set_xlabel('Assumed eligible seasonal cover-crop area (million ha)')
 ax.set_ylabel('Annual crop saving (US$ bn)',color='#256b54')
 ax.tick_params(axis='y',labelcolor='#256b54');ax.set_ylim(0,8)
 bx=ax.twinx();bx.plot(area,biomass,'s--',color='#986237',label='Crop residues economically collected')
 bx.set_ylabel('Residues selected (Mt/year)',color='#986237');bx.tick_params(axis='y',labelcolor='#986237');bx.set_ylim(0,190)
 ax.axvline(8.585/.5,color='#717780',ls=':',lw=1,label='17.17 Mha required for 166 Mt')
 ax.set_title('Cropland limitation reduces feasible residue harvest',loc='left',fontweight='bold')
 fig.text(.5,.055,'Assumed accumulation: 0.5 t C/ha/year; county crop-area and soil trajectories unverified.',ha='center',fontsize=7.1)
 save(fig,'ScienceFigS47_V911_Cover_Crop_Land_Economic_Robustness.tif')
 d=rows('us911_field_counterfactual_lca.csv')
 xs=np.array([float(x['field_residue_counterfactual_tco2e_per_dryt']) for x in d])
 y=np.array([float(x['incremental_crop_emissions_mt']) for x in d])
 fig,ax=plt.subplots(figsize=(7.1,3.5));fig.subplots_adjust(left=.15,right=.95,top=.82,bottom=.28)
 ax.plot(xs,y,'o-',lw=2,color='#226b7c')
 ax.axhline(0,ls='--',lw=1,color='#888')
 for x,z in zip(xs,y):ax.annotate(f'{z:.1f}',(x,z),xytext=(0,8),textcoords='offset points',ha='center',fontsize=8)
 ax.set_xlabel('Assumed net field counterfactual (t CO₂e per dry tonne of residues)')
 ax.set_ylabel('Crop minus no-crop emissions (Mt CO₂e/yr)')
 ax.set_title('Unobserved field counterfactual changes apparent crop abatement',loc='left',fontweight='bold')
 fig.text(.5,.06,'Hypothetical boundary tests only (not field SOC/N₂O observations).',ha='center',fontsize=7.3)
 save(fig,'ScienceFigS48_V911_Field_Counterfactual_LCA_Bounds.tif')
if __name__=='__main__':main()
