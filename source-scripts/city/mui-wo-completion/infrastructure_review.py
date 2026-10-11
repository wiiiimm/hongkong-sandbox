"""Inspect exact source infrastructure surfaces; colour by height, number deck candidates."""
import gzip,json,pathlib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/mui-wo-completion'
data=json.loads(gzip.decompress((HERE/'infrastructure-models.json.gz').read_bytes()))
fig,axes=plt.subplots(5,2,figsize=(14,21))
for ax,m in zip(axes.flat,data['models']):
 tri=np.array(m['modelGeometry']['position']).reshape(-1,3,3);cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);up=np.where(cross[:,1]>1e-8)[0];p=tri[up][:,:,[0,2]];heights=tri[up][:,:,1].mean(axis=1)
 pc=PolyCollection(p,array=heights,cmap='viridis',edgecolor='black',linewidth=.35);ax.add_collection(pc);ax.autoscale();ax.invert_yaxis();ax.set_aspect('equal');ax.set_title(m['id'].split('/')[-1]+' · '+m['sheet']);fig.colorbar(pc,ax=ax,label='Source surface y / HKPD m',shrink=.7)
 if len(up)<100:
  for i,t in zip(up,tri[up]):
   if cross[i,1]>.5:ax.text(t[:,0].mean(),t[:,2].mean(),str(i),fontsize=5,color='darkred')
fig.suptitle('Mui Wo original source infrastructure – upward faces, untouched coordinates',y=.998);fig.tight_layout(rect=[0,0,1,.985]);fig.savefig(DOC/'source-infrastructure-plan.png',dpi=120)
