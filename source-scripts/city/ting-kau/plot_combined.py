"""CPU-only plan proof: one terrain grid and two unchanged mapped-water regions."""
import json,pathlib,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import PathPatch
from matplotlib.path import Path
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def polygon(rings,**style):
 vertices=[];codes=[]
 for ring in rings:
  vertices.extend(ring);codes.extend([Path.MOVETO]+[Path.LINETO]*(len(ring)-2)+[Path.CLOSEPOLY])
 return PathPatch(Path(vertices,codes),**style)
def plot():
 d=json.loads((HERE/'combined/terrain-tsing-ma-ting-kau.json').read_text());hydro=json.loads((HERE/'combined/hydro-tsing-ma-ting-kau.json').read_text());g=d['meta']['georef'];x0=g['bE']-834500;z0=816500-g['bN'];x1=x0+5*(d['w']-1);z1=z0+5*(d['h']-1)
 fig,ax=plt.subplots(figsize=(10,8),dpi=240);fig.patch.set_facecolor('#f8f7f1');ax.set_facecolor('#ebe8db')
 image=np.array(d['elev']).reshape(d['h'],d['w']);ax.imshow(image,extent=[x0,x1,z1,z0],origin='upper',cmap='Greys',vmin=0,vmax=450,alpha=.45)
 for p in hydro['water']:ax.add_patch(polygon(p['rings'],facecolor='#99d9e7',edgecolor='#4f97a9',lw=.65))
 for region in hydro['regions']:
  a,b,c,e=region['bounds'];ax.plot([a,c,c,a,a],[b,b,e,e,b],color='#407c90',ls=':',lw=.8)
 for region in ['tsing-ma','ting-kau']:
  payload=json.loads((HERE.parent/region/f'bridges-{region}.json').read_text())
  for m in payload['models']:
   triangles=np.array(m['modelGeometry']['position']).reshape(-1,3,3)[:,:,[0,2]];ax.add_collection(PolyCollection(triangles,facecolor='#504b47',edgecolor='none'))
 for N in [824027.5,824167.5]:ax.plot([-8847.5,-7517.5],[816500-N]*2,color='#c47830',lw=1,ls='--')
 for x,z in [(-9500,-6860),(-8427.765,-8887.478),(-8229.83,-8485.528),(-8019.633,-8059.256)]:ax.scatter([x],[z],s=32,facecolor='#fff7d2',edgecolor='#2f615e',lw=.9,zorder=5)
 ax.text(-10050,-7320,'TSING MA',fontsize=13,weight='bold',color='#232c30');ax.text(-8060,-8670,'TING KAU',fontsize=13,weight='bold',rotation=65,color='#232c30')
 ax.annotate('Preserved tower island',xy=(-9500,-6860),xytext=(-10340,-6540),fontsize=8,color='#274b50',arrowprops={'arrowstyle':'-','color':'#274b50','lw':.7})
 ax.annotate('Preserved central foundation',xy=(-8229.83,-8485.528),xytext=(-10070,-8490),fontsize=8,color='#274b50',arrowprops={'arrowstyle':'-','color':'#274b50','lw':.7})
 ax.text(-8775,-7540,'Former overlapping patch edges\nnow inside one source mosaic',fontsize=8,color='#a15f23')
 ax.plot([x0,x1,x1,x0,x0],[z0,z0,z1,z1,z0],color='#334b54',lw=1.1)
 ax.set_xlim(x0-40,x1+40);ax.set_ylim(z1+40,z0-40);ax.set_aspect('equal');ax.set_xlabel('City east coordinate (m)');ax.set_ylabel('City south coordinate (m)')
 ax.set_title('Tsing Ma + Ting Kau · source geometry and bounded water repair',loc='left',fontsize=13,pad=12)
 fig.text(.115,.028,'Blue: original mapped-water polygons   •   Dark: original bridge mesh footprints   •   Circles: retained foundations\nOne 603 × 575 terrain grid; 5 m spacing. Cable illustrations omitted. No surveyed bathymetry or public access inferred.',fontsize=8,color='#42535b')
 fig.subplots_adjust(left=.115,right=.97,top=.93,bottom=.13);fig.savefig(ROOT/'docs/astra-city/ting-kau/combined/source-plan-2400x1920.png',dpi=240);plt.close(fig)
if __name__=='__main__':plot()
