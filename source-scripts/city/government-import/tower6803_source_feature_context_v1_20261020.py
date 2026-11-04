"""Render unchanged source context around six flagged tower facets; no acceptance."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tower6803-source-feature-context-v1-20261020';DOC=BASE/BATCH
CAP=BASE/'government-xl-tower6803-private-terrain-capture-v1-20261020';FACES=BASE/'government-xl-tower6803-buried-faces-v1-20261020'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [CAP,FACES]:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for e in r['evidenceRefs']:
    # Shared mutable manifest is not used from historical receipt.
    if e['path'].endswith(('runtime-geometry.json.gz','/6803:0.json')):pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 rt=read(HERE/'local'/CAP.name/'runtime-geometry.json.gz');world={r['uid']:np.asarray(r['position'],dtype='<f8').reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)] for r in rt['rows']}
 faces=read(FACES/'6803:0.json');ids=[r['faceId'] for r in faces['rows']];tower=world['landsd/6803:0'];pod=world['landsd/15047:0'];assert digest(tower.tobytes())==faces['sourceWorldSHA256'];flagged=tower[ids];origin=flagged.reshape(-1,3).mean(0);summary=[];DOC.mkdir()
 for radius in [2,6]:
  chosen={}
  for u,t in world.items():
   mask=((t[:,:,0].max(1)>=origin[0]-radius)&(t[:,:,0].min(1)<=origin[0]+radius)&(t[:,:,2].max(1)>=origin[2]-radius)&(t[:,:,2].min(1)<=origin[2]+radius)&(t[:,:,1].min(1)<=origin[1]+radius)&(t[:,:,1].max(1)>=origin[1]-radius))
   chosen[u]=np.flatnonzero(mask)
  fig=plt.figure(figsize=(14,7))
  for j,azim in enumerate([35,215]):
   ax=fig.add_subplot(1,2,j+1,projection='3d')
   for u,color,alpha in [('landsd/6803:0','#277da8',.45),('landsd/15047:0','#e5b35b',.23)]:
    triangles=world[u][chosen[u]]-origin
    ax.add_collection3d(Poly3DCollection(triangles[:,:,[0,2,1]],facecolors=color,edgecolors=color,linewidths=.3,alpha=alpha))
   ax.add_collection3d(Poly3DCollection((flagged-origin)[:,:,[0,2,1]],facecolors='#d62728',edgecolors='#710000',linewidths=1,alpha=1))
   ax.set(xlim=(-radius,radius),ylim=(-radius,radius),zlim=(-radius,radius),xlabel='East offset (m)',ylabel='South offset (m)',zlabel='Height offset (m)');ax.set_box_aspect([1,1,1]);ax.view_init(elev=20,azim=azim)
  fig.suptitle('Original Tower 1 (blue), podium (gold), six flagged facets (red)\nTransparent cropped context only; no visibility or structural proof')
  fig.tight_layout();fig.savefig(DOC/f'context-{radius}m.png',dpi=150);plt.close(fig)
  summary.append(dict(radiusM=radius,selectedFaceIds={u:v.tolist() for u,v in chosen.items()}))
 save(DOC/'context.json',dict(origin=origin.tolist(),flaggedFaces=ids,flaggedBounds=[flagged.min((0,1)).tolist(),flagged.max((0,1)).tolist()],views=summary,installationApproved=False,qualification='Cropped transparent original-source context; no hiddenness, structural or whole-face support proof.'))
 module('tower6803_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unchanged-tower-podium-flagged-feature-context',refs,dict(uids=list(world),flaggedFaces=ids,installationApproved=False))
if __name__=='__main__':main()
