"""Render source-backed identity and local wall context, without asset edits."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from shapely.geometry import Polygon,box
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-heya-aqua-source-context-v1-20261020';DOC=BASE/BATCH;SUP=BASE/'government-xl-heya-aqua-current-support-v3-20261020';IDENT=BASE/'government-xl-heya-aqua-identity-v1-20261020'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [SUP,IDENT]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256'] for e in r['evidenceRefs']}
 def take(folder,p):
  assert digest(p.read_bytes())==pins[folder][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 inp=take(SUP,SUP/'support-inputs.json');ident=take(IDENT,IDENT/'identity.json');sources={r['uid']:r for r in inp['sources']};tri={}
 for uid,r in sources.items():
  p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==r['sourceSHA256'];refs.append(p);tri[uid]=decode_original_world_triangles(p.read_bytes())
 tower=tri['landsd/184287:0'];podium=tri['landsd/184285:0'];DOC.mkdir(parents=True)
 cell=box(*ident['geographicCell']['worldXZBounds']);target=Polygon(sources['landsd/184287:0']['source']['building']['rings'][0]);supportform=Polygon(sources['landsd/184285:0']['source']['building']['rings'][0]);fig,axes=plt.subplots(1,2,figsize=(14,7))
 for ax,zoom in zip(axes,[False,True]):
  ax.add_collection(PolyCollection(tower[:,:,[0,2]],facecolors='#79b3cf',edgecolors='none',alpha=.4))
  for poly,color,label in [(supportform,'#bd7b25','Recorded installed podium'),(target,'#172c48','Recorded Tower 2'),(cell,'#c32d36','Encoded 1 m GeoRef cell')]:
   xy=np.asarray(poly.exterior.coords);ax.plot(xy[:,0],xy[:,1],color=color,lw=1.5,label=label)
  if zoom:ax.set_xlim(-563,-554);ax.set_ylim(-5690,-5681)
  else:ax.set_xlim(tower[:,:,0].min()-4,tower[:,:,0].max()+4);ax.set_ylim(tower[:,:,2].min()-4,tower[:,:,2].max()+4)
  ax.set_aspect('equal');ax.set_xlabel('World X (m)');ax.set_ylabel('World Z (m)');ax.legend(fontsize=7)
 axes[0].set_title('Complete original tower projection');axes[1].set_title('GeoRef cell and recorded footprint');fig.tight_layout();fig.savefig(DOC/'identity-context.png',dpi=160);plt.close(fig)
 witness=np.array([-552.03125,27.641000747680664,-5687.6796875]);selected=[]
 for data in [tower,podium]:
  lo,hi=data.min(1),data.max(1);mask=(lo[:,0]>=witness[0]-8)&(hi[:,0]<=witness[0]+8)&(lo[:,2]>=witness[2]-8)&(hi[:,2]<=witness[2]+8)&(lo[:,1]>=19)&(hi[:,1]<=38);selected.append(data[mask])
 for az in [-55,125]:
  fig=plt.figure(figsize=(9,8));ax=fig.add_subplot(projection='3d')
  for data,color in zip(selected,['#599ac2','#c99050']):ax.add_collection3d(Poly3DCollection(data[:,:,[0,2,1]],facecolors=color,edgecolors='#444444',linewidths=.1,alpha=.85))
  ax.scatter(*witness[[0,2,1]],c='red',s=35);ax.set_xlim(witness[0]-8,witness[0]+8);ax.set_ylim(witness[2]-8,witness[2]+8);ax.set_zlim(19,38);ax.view_init(24,az);ax.set_title('Local original faces: tower blue, podium orange\nDisplay subset only: fully inside 16 m box and height 19–38 m');fig.tight_layout();fig.savefig(DOC/f'wall-context-{az}.png',dpi=160);plt.close(fig)
 result=dict(uids=list(sources),sourceGeometryChanges=0,installationApproved=False,visualReviewComplete=False,cellAreaM2=cell.area,cellCoveredByTargetM2=cell.intersection(target).area,cellCoveredByPodiumM2=cell.intersection(supportform).area,localDisplaySourceFaces=[len(t) for t in selected],qualification='Complete projection identity diagram and explicitly cropped local source-face displays; not physical or visual approval.')
 save(DOC/'summary.json',result);refs.append(HERE/'exact_packed_world_geometry_20261009.py');module('heya_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-source-identity-cell-and-local-wall-visual-context',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
