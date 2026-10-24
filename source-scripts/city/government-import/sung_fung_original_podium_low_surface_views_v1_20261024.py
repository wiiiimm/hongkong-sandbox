"""Source/terrain close-ups covering every flagged upward face; display only."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-next-repairs-sung-fung-original-podium-low-surface-views-v1-20261024';DOC=BASE/BATCH
SRC=BASE/'government-xl-next-repairs-sung-fung-original-pair-current-runtime-v1-20261024';GROUND=BASE/'government-xl-next-repairs-sung-fung-original-pair-current-runtime-v1-20261024';CTX=BASE/'government-xl-next-repairs-sung-fung-original-pair-buried-context-v1-20261024'
def clipped(mesh,lo,hi):
 keep=(mesh.max(1)>=lo).all(1)&(mesh.min(1)<=hi).all(1);out=[]
 for triangle in mesh[keep]:
  poly=list(triangle)
  for axis in range(3):
   for value,sign in [(lo[axis],1),(hi[axis],-1)]:
    result=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
     da,db=sign*(a[axis]-value),sign*(b[axis]-value)
     if da>=0:result.append(a)
     if (da>=0)!=(db>=0):result.append(a+(b-a)*(da/(da-db)))
    poly=result
  if len(poly)>=3:out.append((np.asarray(poly)-lo)[:,[0,2,1]])
 return out

def main():
 assert not DOC.exists();refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py'];pins={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [SRC,GROUND,CTX]:
   r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(folder,path):
  assert digest(path.read_bytes())==pins[folder][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 rows=[r for r in take(SRC,SRC/'selection.json.gz')['rows']if r['uid']in ['landsd/45779:0']];records=[];DOC.mkdir(parents=True)
 for row in rows:
  uid=row['uid'];short=uid.split('/')[1];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset);tri=decode_original_world_triangles(asset.read_bytes())
  ground=np.asarray(next(g for g in take(GROUND,HERE/'local'/GROUND.name/'runtime-geometry.json.gz')['rows']if g['uid']==uid)['drawnGroundGeometry']).reshape(-1,3,3)
  detail=take(CTX,CTX/(short+'.json'));ids=[f['faceIndex']for f in detail['buriedFaces']if f['upward']];centres=tri.mean(1);remaining=set(ids);groups=[]
  while remaining:
   group={min(remaining)};remaining-=group
   while True:
    more={j for j in remaining if any(np.linalg.norm(centres[j,[0,2]]-centres[i,[0,2]])<8 for i in group)}
    if not more:break
    group|=more;remaining-=more
   groups.append(sorted(group))
  assert sorted(i for g in groups for i in g)==sorted(ids)
  for n,ids in enumerate(groups):
   bad=tri[ids];lo=bad.min((0,1))-np.array([3,1,3]);hi=bad.max((0,1))+np.array([3,4,3]);size=(hi-lo)[[0,2,1]]
   fig=plt.figure(figsize=(14,6))
   for k,angle in enumerate([35,215]):
    ax=fig.add_subplot(1,2,k+1,projection='3d')
    for mesh,color,alpha in [(ground,'#60a56b',.35),(tri,'#64748b',.28),(bad,'#b91c1c',1)]:
     polys=clipped(mesh,lo,hi)
     if polys:ax.add_collection3d(Poly3DCollection(polys,facecolors=color,edgecolors=color,alpha=alpha,linewidth=.2))
    ax.set_xlim(0,size[0]);ax.set_ylim(0,size[1]);ax.set_zlim(0,size[2]);ax.set_box_aspect(size.copy());ax.view_init(25,angle);ax.set_xlabel('X offset m');ax.set_ylabel('Z offset m');ax.set_zlabel('Y offset m')
   fig.suptitle(f'{uid} region {n+1} | source grey, current viewer ground green, flagged upward faces red\nDisplay crops only; original assets unchanged.');fig.tight_layout();file=DOC/f'{short}-region-{n+1}.png';fig.savefig(file,dpi=140);plt.close(fig)
   records.append(dict(uid=uid,sourceSHA256=row['sourceSHA256'],upwardFaceIds=ids,bounds=[lo.tolist(),hi.tolist()],image=str(file.relative_to(ROOT))));print(uid,n+1,len(ids),flush=True)
 result=dict(uids=[r['uid']for r in rows],regions=records,installationApproved=False,sourceGeometryChanges=0,visualAcceptance=False);save(DOC/'summary.json',result)
 module('two_local_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-originals-local-upward-surface-context',refs,result)
if __name__=='__main__':main()
