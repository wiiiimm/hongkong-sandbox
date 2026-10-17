import sys,numpy as np
sys.path.insert(0,'source-scripts/city/government-import')
from run import ROOT,read,save,digest
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
b=ROOT/'docs/astra-city/government-import';d=b/'government-xl-orchards-grade-role-views-v1-20261017';p=b/'government-xl-orchards-assembly-four-world-v1-20261017/world-triangles.json.gz';w=read(p)['literal'];centre=np.array([5628.5205078125,29.174999237060547,472.33203125]);fig=plt.figure(figsize=(12,6),dpi=160)
for n,az in enumerate([-45,135]):
 ax=fig.add_subplot(1,2,n+1,projection='3d')
 for uid,color in [('landsd/233002:0','#83a895'),('landsd/254629:0','#6d94b5')]:
  t=np.asarray(w[uid]);mask=(t[:,:,0].min(1)<=centre[0]+2)&(t[:,:,0].max(1)>=centre[0]-2)&(t[:,:,2].min(1)<=centre[2]+2)&(t[:,:,2].max(1)>=centre[2]-2)&(t[:,:,1].min(1)<=35);shown=t[mask];ax.add_collection3d(Poly3DCollection(shown[:,:,[0,2,1]],facecolors=color,alpha=.45,edgecolors=color,linewidths=.3))
 t=np.asarray(w['landsd/254629:0'])
 for i in [1032,1035]:ax.add_collection3d(Poly3DCollection(t[[i]][:,:,[0,2,1]],facecolors='#ed6a36',alpha=.8,edgecolors='#8d3326',linewidths=.6))
 ax.scatter([centre[0]],[centre[2]],[centre[1]],color='black',s=20);ax.set_xlim(centre[0]-1.2,centre[0]+1.2);ax.set_ylim(centre[2]-1.2,centre[2]+1.2);ax.set_zlim(28.8,35);ax.set_box_aspect([2.4,2.4,6.2]);ax.view_init(elev=28,azim=az);ax.set_title('Original Tower 2 corner / green original podium');ax.set_xlabel('World X');ax.set_ylabel('World Z');ax.set_zlabel('HKPD height')
fig.tight_layout();out=d/'tower2-corner-original.png';fig.savefig(out);plt.close(fig);save(d/'corner-view-inputs.json',dict(inputPath=str(p.relative_to(ROOT)),inputSHA256=digest(p.read_bytes()),outputPath=str(out.relative_to(ROOT)),outputSHA256=digest(out.read_bytes()),sourceFaces=[1032,1035],geometryChanges=0));(d/'corner-view.py').write_bytes(__import__('pathlib').Path(__file__).read_bytes())
