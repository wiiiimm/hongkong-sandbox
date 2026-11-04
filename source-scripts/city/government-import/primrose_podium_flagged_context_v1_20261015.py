"""Inspect all current podium clearance failures without editing geometry."""
from pathlib import Path
from fractions import Fraction
import numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v1_20261015 import BASE,SOURCE,GROUND,PODIUM,module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BATCH='government-xl-primrose-podium-flagged-context-v1-20261015';DOC=BASE/BATCH;OLD=BASE/'government-xl-primrose-podium-current-finite-v1-20261015'
def main():
 assert not DOC.exists();receipt=read(OLD/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for q in receipt['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 source=next(r for r in read(SOURCE/'selection.json.gz')['rows']if r['uid']==PODIUM);asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256']
 t=decode_original_world_triangles(asset.read_bytes());proof=read(OLD/'original.json.gz');bad=[r for r in proof['faces']if not r['proof']['existingOrdinaryClearanceBoundProved']];indices=[r['sourceFace']for r in bad];assert len(indices)==25
 normals=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);up=[i for i in indices if normals[i,1]>0];assert up==[1845,1846]
 centre=t[up].mean(axis=(0,1));ground=np.asarray(read(GROUND/'after-ground.json.gz')['completeRelevantDrawnTriplets']).reshape(-1,3,3)
 near=np.all(t.max(axis=1)>=centre-[18,20,18],axis=1)&np.all(t.min(axis=1)<=centre+[18,15,18],axis=1)
 ng=(ground[:,:,0].max(axis=1)>=centre[0]-18)&(ground[:,:,0].min(axis=1)<=centre[0]+18)&(ground[:,:,2].max(axis=1)>=centre[2]-18)&(ground[:,:,2].min(axis=1)<=centre[2]+18)
 rows=[]
 for r in bad:
  i=r['sourceFace'];edges={tuple(sorted((tuple(t[i,a]),tuple(t[i,(a+1)%3]))))for a in range(3)};adj=[]
  for j,face in enumerate(t):
   if j==i:continue
   common=edges&{tuple(sorted((tuple(face[a]),tuple(face[(a+1)%3]))))for a in range(3)}
   if common:adj.append(dict(sourceFace=j,sharedWholeEdges=len(common),normal=normals[j].tolist(),vertices=face.tolist()))
  rows.append(dict(sourceFace=i,vertices=t[i].tolist(),normal=normals[i].tolist(),exactMinimumGapM=r['proof']['exactCertifiedLowerClearanceM'],minimumGapM=float(Fraction(r['proof']['exactCertifiedLowerClearanceM'])),exactSharedEdgeNeighbours=adj))
 DOC.mkdir();save(DOC/'context.json',dict(uid=PODIUM,sourceSHA256=source['sourceSHA256'],rows=rows,upwardFailures=up,sourceGeometryChanges=0,fullAcceptance=False))
 for label,with_ground in [('source',False),('terrain',True)]:
  fig=plt.figure(figsize=(14,6))
  for j,azim in enumerate([-55,125]):
   ax=fig.add_subplot(1,2,j+1,projection='3d');ax.add_collection3d(Poly3DCollection((t[near]-centre)[:,:,[0,2,1]],facecolor='#bac5d1',edgecolor='#6a7d90',alpha=.25,linewidths=.3))
   ax.add_collection3d(Poly3DCollection((t[indices]-centre)[:,:,[0,2,1]],facecolor='#e45d59',edgecolor='#8a2121',alpha=.65,linewidths=.6))
   ax.add_collection3d(Poly3DCollection((t[up]-centre)[:,:,[0,2,1]],facecolor='#f4d13b',edgecolor='black',alpha=1,linewidths=1))
   if with_ground:ax.add_collection3d(Poly3DCollection((ground[ng]-centre)[:,:,[0,2,1]],facecolor='#74a65c',edgecolor='#3d7238',alpha=.3,linewidths=.3))
   for i in up:
    c=t[i].mean(axis=0)-centre;ax.text(c[0],c[2],c[1]+.3,str(i),fontsize=10)
   ax.set(xlim=(-18,18),ylim=(-18,18),zlim=(-20,15),xlabel='X offset',ylabel='Z offset',zlabel='Height offset');ax.view_init(elev=28,azim=azim)
  fig.suptitle('Primrose original podium: red flagged faces; yellow upward faces1845/1846'+(' with corrected terrain'if with_ground else''));fig.tight_layout();fig.savefig(DOC/(label+'.png'),dpi=140);plt.close(fig)
 paths=[ROOT/q['path']for q in receipt['evidenceRefs']]+[OLD/'result.json',asset,Path(__file__),HERE/'primrose_compound_foundation_v1_20261015.py']
 module('context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'all-flagged-original-podium-source-context-v1',paths,dict(uids=[PODIUM],flaggedFaces=indices,upwardFailures=up,fullAcceptance=False))
if __name__=='__main__':main()
