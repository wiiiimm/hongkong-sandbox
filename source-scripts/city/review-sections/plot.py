#!/usr/bin/env python3
"""CPU source-plan rendering, 3000 x 1900 pixels; does not use a browser/GPU."""
import json,pathlib,sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from matplotlib import patheffects
import numpy as np
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent));import build
COLORS=['#3f87a8','#d39743','#73935a','#b57381','#807fab','#559c96','#c17d55','#99a14e','#aa769c','#6c9b9e','#bca35d','#659297','#8f9c68','#7498b6','#b27d67','#8795b3','#a59575','#809b78']
def path_patch(poly,**kwargs):
 vs=[];codes=[]
 for r in poly['rings']:
  vs.extend([(x/1000,z/1000) for x,z in r]);codes.extend([Path.MOVETO]+[Path.LINETO]*(len(r)-2)+[Path.CLOSEPOLY])
 return PathPatch(Path(vs,codes),**kwargs)
def main():
 j=json.loads(build.OUT.read_text());districts=build.load_districts();rules,_,elements=build.load_islands()
 fig=plt.figure(figsize=(15,9.5),dpi=200,facecolor='#f5f4ef');gs=fig.add_gridspec(2,2,width_ratios=[1.32,1],height_ratios=[1,1],left=.035,right=.985,bottom=.10,top=.89,wspace=.035,hspace=.18)
 ax0=fig.add_subplot(gs[:,0]);ax1=fig.add_subplot(gs[0,1]);ax2=fig.add_subplot(gs[1,1]);panels=[(ax0,(-36,36,-32,18),'Official district spine · all 132 project areas',lambda s:int(s['district'])>=10),(ax1,(-9,10,-7,11),'Urban review areas · harbour and Hong Kong Island',lambda s:int(s['district'])<10),(ax2,(-36,-10,-1,18),'Lantau and adjoining island groups',lambda s:s['district'] in ('10','11'))]
 for ax,extent,title,labelled in panels:
  ax.set_facecolor('#e9eef0')
  for s in j['sections']:
   rgb=np.array(matplotlib.colors.to_rgb(COLORS[int(s['district'])-1]));shade=.77+.04*(int(s['id'].split('.')[1])%5);colour=rgb*shade+np.ones(3)*(1-shade)
   for p in s['polygons']:ax.add_patch(path_patch(p,facecolor=colour,alpha=.65,edgecolor='#ffffff',linewidth=.45,zorder=2))
  for d,record in districts.items():
   for p in build.poly_parts(record['geometry']):
    x,z=p.exterior.xy;ax.plot(np.array(x)/1000,np.array(z)/1000,color='#304d5b',lw=.6,zorder=4)
  for key,e in elements.items():
   if e.get('tags',{}).get('place') not in ('island','islet'):continue
   g=build.geometry(e)
   if g is None:continue
   for p in build.poly_parts(g):
    x,z=p.exterior.xy;ax.plot(np.array(x)/1000,np.array(z)/1000,color='#253d38',alpha=.8,lw=.35,zorder=5)
  labels=[]
  for s in j['sections']:
   x,z=np.array(s['label'])/1000
   if labelled(s) and extent[0]<x<extent[1] and extent[2]<z<extent[3]:
    labels.append((ax.text(x,z,s['id'],fontsize=5.5 if ax==ax0 else 6.2,ha='center',va='center',color='#123b4b',zorder=7,path_effects=[patheffects.withStroke(linewidth=2.3,foreground='white',alpha=.95)]),(x,z)))
  for p in j['provenance']['anchorExceptions']:
   x,z=np.array(p['sourcePoint'])/1000
   if extent[0]<x<extent[1] and extent[2]<z<extent[3]:ax.plot(x,z,'x',color='#ae3333',ms=5,mew=1.2,zorder=10)
  ax.set_xlim(extent[:2]);ax.set_ylim(extent[3],extent[2]);ax.set_aspect('equal');ax.set_title(title,fontsize=10,loc='left',color='#123b4b',pad=8);ax.set_xlabel('World X · kilometres',fontsize=7,color='#52656a');ax.tick_params(labelsize=6,colors='#52656a');ax.grid(alpha=.12,zorder=0)
  for spine in ax.spines.values():spine.set_color('#ccd6d7')
  fig.canvas.draw();renderer=fig.canvas.get_renderer()
  # Separate close urban labels in screen coordinates; fine leader lines retain their true locations.
  for iteration in range(65):
   changed=False
   for i,(text,origin) in enumerate(labels):
    a=text.get_window_extent(renderer).expanded(1.05,1.2)
    for other,_ in labels[i+1:]:
     b=other.get_window_extent(renderer).expanded(1.05,1.2)
     if not a.overlaps(b):continue
     pa=ax.transData.transform(text.get_position());pb=ax.transData.transform(other.get_position());shift=np.array([0,2.5 if pa[1]>=pb[1] else -2.5])
     text.set_position(ax.transData.inverted().transform(pa+shift));other.set_position(ax.transData.inverted().transform(pb-shift));changed=True
   if not changed:break
  for text,origin in labels:
   target=text.get_position()
   if np.linalg.norm(ax.transData.transform(target)-ax.transData.transform(origin))>4:ax.plot([origin[0],target[0]],[origin[1],target[1]],color='#294952',alpha=.6,lw=.35,zorder=6)

 fig.text(.035,.958,'HONG KONG / SECTION REVIEW GEOGRAPHY',fontsize=20,weight='bold',color='#123b4b')
 fig.text(.035,.927,'132 deterministic project areas inside 18 official HAD districts · version '+j['boundaryVersion'],fontsize=10,color='#4c646d')
 fig.text(.035,.064,'Coloured areas include district marine waters. White lines are inferred review divisions; dark lines show official district outlines and retained island coastlines.',fontsize=8,color='#4c646d')
 fig.text(.035,.045,'Red crosses: four existing destinations assigned to neighbouring districts in the checklist. Source coordinates and official borders remain unchanged.',fontsize=8,color='#4c646d')
 fig.text(.035,.025,'Sources: HAD / CSDI district response retrieved 7 Sep 2026 (source lifespan 2016); retained OpenStreetMap island geometry and 153 regional place anchors. These are not official neighbourhood boundaries.',fontsize=7.4,color='#4c646d')
 dest=build.DOC/'geography-source-plan-3000x1900.png';fig.savefig(dest,dpi=200,facecolor=fig.get_facecolor());plt.close(fig);print(dest)
if __name__=='__main__':main()
