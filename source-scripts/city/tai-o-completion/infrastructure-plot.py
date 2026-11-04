"""Static inspection of exact official infrastructure triangles and OSM paths."""
import gzip,json,pathlib
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[3];DOC=ROOT/'docs/astra-city/tai-o-completion'
r=json.loads(gzip.decompress((ROOT/'source-scripts/city/tai-o-completion/infrastructure-models.json.gz').read_bytes()))
bridges=json.loads((ROOT/'3d-viewer/city/data/bridges.json').read_text())['bridges']
fig=plt.figure(figsize=(18,14),layout='constrained')
for i,m in enumerate(r['models']):
 p=np.array(m['modelGeometry']['position']).reshape(-1,3);t=p.reshape(-1,3,3);c=p.mean(axis=0);c[1]=0
 ax=fig.add_subplot(3,4,2*i+1,projection='3d');tt=(t-c)[:,:,[0,2,1]]
 col=Poly3DCollection(tt,facecolors='#9eaeb4',edgecolors='#304c59',linewidths=.22,alpha=.22);ax.add_collection3d(col);ax.add_collection3d(Poly3DCollection(tt[m['walkTriangleIndices']],facecolors='#328956',edgecolors='#145835',linewidths=.3,alpha=.8))
 ax.set_xlim(tt[:,:,0].min(),tt[:,:,0].max());ax.set_ylim(tt[:,:,1].min(),tt[:,:,1].max());ax.set_zlim(tt[:,:,2].min(),tt[:,:,2].max());ax.set_box_aspect((max(np.ptp(p[:,0]),5),max(np.ptp(p[:,2]),5),max(np.ptp(p[:,1]),5)))
 ax.view_init(25,-55);ax.set_title(m['id'].split('/')[-1]+'\n'+str(len(t))+' source triangles');ax.set_xlabel('E / m');ax.set_ylabel('South / m');ax.set_zlabel('HKPD / m')
 ax=fig.add_subplot(3,4,2*i+2)
 for tri in t:ax.fill(tri[:,0],tri[:,2],color='#8cb6bc',alpha=.2,edgecolor='#496778',linewidth=.3)
 for index in m['walkTriangleIndices']:
  tri=t[index];ax.fill(tri[:,0],tri[:,2],color='#328956',alpha=.8,edgecolor='#145835',linewidth=.3)
 for b in bridges:
  path=np.array(b['path'])
  if b['role']=='bridge' and np.any((path[:,0]>=p[:,0].min()-10)&(path[:,0]<=p[:,0].max()+10)&(path[:,1]>=p[:,2].min()-10)&(path[:,1]<=p[:,2].max()+10)):
   ax.plot(path[:,0],path[:,1],'-r',linewidth=1);ax.text(*path.mean(axis=0),b['id'],fontsize=6)
 ax.set_aspect('equal');ax.invert_yaxis();ax.set_title('Green = selected floor / red = mapped route');ax.ticklabel_format(useOffset=False)
fig.suptitle('Tai O retained official infrastructure — exact source geometry, no inferred supports',fontsize=17)
fig.savefig(DOC/'infrastructure-model-contact-sheet-2700x2100.png',dpi=150)
