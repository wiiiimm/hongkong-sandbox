"""Export exact original grade-contact context for visual source-role review."""
from pathlib import Path
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/'government-xl-orchards-grade-role-views-v1-20261017';CAP=BASE/'government-xl-orchards-assembly-four-world-v1-20261017';GRADE=BASE/'government-xl-orchards-grade-face-context-v1-20261017';PHYS=BASE/'government-xl-orchards-assembly-terrain-candidate-v1-20261017'
def main():
 assert not DOC.exists();DOC.mkdir();world=read(CAP/'world-triangles.json.gz')['literal'];rtpath=HERE/'local'/PHYS.name/'runtime-geometry.json.gz';rt={r['uid']:r for r in read(rtpath)['rows']};pins=[Path(__file__),CAP/'world-triangles.json.gz',rtpath,GRADE/'summary.json'];exports=[]
 for uid,label in [('landsd/233002:0','Original podium'),('landsd/256434:0','Original community complex')]:
  dpath=GRADE/(uid.split('/')[1]+'-literal.json.gz');d=read(dpath);pins.append(dpath);t=np.asarray(world[uid]);ground=np.asarray(rt[uid]['drawnGroundGeometry']).reshape(-1,3,3);ids=d['continuousNegativeFaceIds'];neg=t[ids];lo=t.min((0,1));hi=t.max((0,1));ground=ground[(ground[:,:,0].min(1)<=hi[0]+2)&(ground[:,:,0].max(1)>=lo[0]-2)&(ground[:,:,2].min(1)<=hi[2]+2)&(ground[:,:,2].max(1)>=lo[2]-2)]
  fig=plt.figure(figsize=(15,6),dpi=150)
  for n,az in enumerate([-55,125]):
   ax=fig.add_subplot(1,2,n+1,projection='3d');ax.add_collection3d(Poly3DCollection(ground[:,:,[0,2,1]],facecolors='#72a087',alpha=.32,edgecolors='none'));ax.add_collection3d(Poly3DCollection(t[:,:,[0,2,1]],facecolors='#b8c2cc',alpha=.20,edgecolors='none'));ax.add_collection3d(Poly3DCollection(neg[:,:,[0,2,1]],facecolors='#ed6a36',alpha=.9,edgecolors='#8d3326',linewidths=.15));ax.set_xlim(lo[0]-2,hi[0]+2);ax.set_ylim(lo[2]-2,hi[2]+2);ax.set_zlim(min(lo[1]-1,ground[:,:,1].min()),hi[1]+1);ax.set_box_aspect(np.maximum((hi-lo)[[0,2,1]],1));ax.view_init(elev=24,azim=az);ax.set_xlabel('World X');ax.set_ylabel('World Z');ax.set_zlabel('HKPD height');ax.set_title(label+' — exact flagged faces orange')
  fig.tight_layout();dest=DOC/(uid.split('/')[1]+'-grade-context.png');fig.savefig(dest);plt.close(fig);exports.append(dict(uid=uid,path=str(dest.relative_to(ROOT)),sha256=digest(dest.read_bytes()),faces=ids))
 save(DOC/'exports.json',dict(images=exports,inputHashes={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in pins},geometryChanges=0,reviewed=False))
if __name__=='__main__':main()
